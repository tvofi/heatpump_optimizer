#!/usr/bin/env bash
# Prepare a round's audit baseline: a git-archive export the finders work in
# (no .git, no earlier audit records), one worktree per finder that mutates
# production, and the current briefs copied into each.
#
#   tools/audit/prepare_baseline.sh <round> <baseline-sha> [<briefs-source-checkout>]
#
# Run from any checkout of the repository. Creates, beside the repository's
# worktrees directory:
#   ../audit-r<round>-baseline        the export (D1, D2, D4, D5, D6, D7, D8, D10, D12)
#   ../audit-r<round>-<dim>           a worktree per dimension in ISOLATED_DIMS below
#                                     (the instrumenting finders, and D11, which audits
#                                      the process and so needs .git and the API)
# and writes tools/audit/round<round>/BASELINE.md into each with the paths the
# finders need. Idempotent: refuses to overwrite an existing export.
set -euo pipefail
ROUND="${1:?round}"; SHA="${2:?baseline sha}"; SRC="${3:-$(git rev-parse --show-toplevel)}"
cd "$(git rev-parse --show-toplevel)"
PARENT="$(cd .. && pwd)"
EXPORT="$PARENT/audit-r${ROUND}-baseline"
[ -e "$EXPORT" ] && { echo "refusing: $EXPORT exists"; exit 2; }
git rev-parse --verify --quiet "${SHA}^{commit}" >/dev/null || { echo "refusing: $SHA is not a commit here"; exit 2; }
FULL=$(git rev-parse "${SHA}^{commit}")
PYTHON="${PYTHON:-$PARENT/tvofi-claude/.venv/bin/python}"
[ -x "$PYTHON" ] || { echo "refusing: no interpreter at $PYTHON (set PYTHON)"; exit 2; }

mkdir -p "$EXPORT"
git archive "$FULL" | tar -x -C "$EXPORT"
# RELEASE_NOTES.md IS NOT DELETED, and the reason is a defect this line used to
# carry: tests/entities.py:12140 reads it with Path(...).read_text() at import,
# outside any guard, so an export without it ran 0 of its 1360 entity checks and
# died with FileNotFoundError before a finder's first measurement. COMMON.md and
# audit-find.js both say to keep it. The `finders_can_start` refusal below is the
# general form of that lesson and fires on any other file a test opens this way.
rm -f "$EXPORT"/docs/audit-*.md "$EXPORT"/docs/backlog.md
mkdir -p "$EXPORT/tools/audit"
cp -R "$SRC/tools/audit/." "$EXPORT/tools/audit/"     # current briefs, README, schema
mkdir -p "$EXPORT/tools/audit/round${ROUND}"

# Earlier rounds must not steer a finder -- COMMON.md's wall, and the reason the
# export drops docs/audit-*.md at all. Deleting only those two documents left the
# wall open twice over: `git archive` carries any tools/audit/round<N>/ that is
# tracked at the baseline, and the cp above copies every round the SOURCE
# checkout holds. Round 4 was prepared with 116 round-3 files in every finder
# tree, ledger/verdicts.tsv among them -- 43 findings with their verdicts and
# headlines. tools/audit/ is INERT in tests/closure.py, so removing them selects
# no script and leaves the gate untouched (measured: tests/entities.py passes
# 1360 of 1360 in a worktree with the directory removed).
strip_earlier_rounds() {
  local dir="$1" n
  n=$(find "$dir/tools/audit" -maxdepth 1 -type d -name 'round*' ! -name "round${ROUND}" 2>/dev/null | wc -l | tr -d ' ')
  find "$dir/tools/audit" -maxdepth 1 -type d -name 'round*' ! -name "round${ROUND}" -exec rm -rf {} +
  echo "RESULT stripped_earlier_rounds=$n dir=$dir"
}
strip_earlier_rounds "$EXPORT"

# One list, read three times below. audit-find.js's ISOLATED must agree with it;
# they are separate files and a seat that edits one edits both.
ISOLATED_DIMS="D0 D3 D9 D11"

for dim in $ISOLATED_DIMS; do
  wt="$PARENT/audit-r${ROUND}-${dim}"
  [ -e "$wt" ] && { echo "refusing: $wt exists"; exit 2; }
  git worktree add --detach "$wt" "$FULL" >/dev/null
  mkdir -p "$wt/tools/audit"; cp -R "$SRC/tools/audit/." "$wt/tools/audit/"
  mkdir -p "$wt/tools/audit/round${ROUND}/${dim}"
  # A worktree is a real checkout, so this leaves tracked deletions in its status
  # rather than an absent file. That is the honest state and it costs nothing the
  # gate can see; BASELINE.md below says so, and a finder restoring its tree
  # around a mutant restores these with it.
  strip_earlier_rounds "$wt"
done

# THE REFUSAL THAT WOULD HAVE CAUGHT BOTH DEFECTS ABOVE, in its general form.
# Every literal path a tests/*.py script hands to Path(...) or open() must still
# exist in the finder tree if it exists in the source checkout. That is what
# separates a deliberate wall (docs/audit-*.md, docs/backlog.md -- which no test
# opens, checked) from a file the preparation dropped by accident.
#
# WHAT IT CANNOT SEE, stated rather than left to be discovered: a path built at
# runtime, a path under a directory literal, and any reader that is not a
# tests/*.py script. It is a refusal on the shapes that have actually broken an
# export, not a proof that one starts.
finders_can_start() {
  local dir="$1" missing="" f
  for f in $(grep -rhoE '(Path\(|open\()"[A-Za-z0-9_./-]+"' "$SRC"/tests/*.py 2>/dev/null \
             | sed -E 's/^[^"]*"//; s/"$//' | sort -u); do
    case "$f" in /*) continue ;; esac          # absolute: not ours to carry
    [ -e "$SRC/$f" ] || continue               # not in the baseline either
    [ -e "$dir/$f" ] || missing="$missing $f"
  done
  if [ -n "$missing" ]; then
    echo "refusing: the preparation dropped file(s) a tests/*.py script opens unguarded:$missing"
    echo "  (an export missing one of these dies at import, before a finder's first measurement)"
    return 1
  fi
  echo "RESULT finders_can_start=ok dir=$dir"
}
for dir in "$EXPORT" $(for dim in $ISOLATED_DIMS; do echo "$PARENT/audit-r${ROUND}-${dim}"; done); do
  finders_can_start "$dir" || exit 2
done

NODE=$(command -v node || true)
CHROMIUM=$(ls -d "$HOME"/.cache/pw-browsers/chromium-* 2>/dev/null | head -1 || true)
ISOLATED_DIRS=""; for dim in $ISOLATED_DIMS; do ISOLATED_DIRS="$ISOLATED_DIRS $PARENT/audit-r${ROUND}-${dim}"; done
for dir in "$EXPORT" $ISOLATED_DIRS; do
  cat > "$dir/tools/audit/round${ROUND}/BASELINE.md" <<MD
# Round ${ROUND} baseline

- baseline: ${FULL}
- export (read-only finders): ${EXPORT}
- worktrees (isolated finders): $(for d in $ISOLATED_DIMS; do printf '%s %s/audit-r%s-%s, ' "$d" "$PARENT" "$ROUND" "$d"; done | sed 's/, $//')
- python: ${PYTHON} (run from the directory root with PYTHONPATH=tests/hastub)
- node: ${NODE:-not found}
- chromium: ${CHROMIUM:-not found} (PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/pw-browsers)
- playwright module: install into a scratch prefix, e.g. \`npm i --prefix /tmp/pw playwright@1.49.0\`, then NODE_PATH=/tmp/pw/node_modules
- gate lock: take it only when tests/closure.py select reports MODE: FULL or names
  tests/stress.py -- that one script is what the lock exists for. Use
  tests/gate_lock.py, never mkdir and a shell pid (#404 replaced that: no lease, so
  tests/run.sh cannot renew it, and no flock, so a crashed holder holds it forever).

      python3 tests/gate_lock.py take --label <your-label>
      HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \\
        GOLDEN_REF=<a ref that is not HEAD> ./tests/run.sh
      python3 tests/gate_lock.py renew --label <your-label>   # between commands
      python3 tests/gate_lock.py release --label <your-label>

- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
MD
done
echo "RESULT export=$EXPORT"
echo "RESULT baseline=$FULL"
