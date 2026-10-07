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
#                                     (the instrumenting finders, D14, and D11 and D13, which
#                                      audit the process and read `main`'s history and
#                                      the API, so they need .git)
# and writes tools/audit/round<round>/BASELINE.md into each with the paths the
# finders need. Idempotent: refuses to overwrite an existing export.
set -euo pipefail
strip_earlier_rounds() {
  "$PYTHON" - "$1" "$ROUND" <<'PY'
import json, re, sys
from pathlib import Path
root, cur = Path(sys.argv[1]), f"round{sys.argv[2]}"
# R9-RO-8: rounds live at dev/audit/rounds/. An export of an older baseline
# still has them under tools/audit/, so both homes are stripped. A glob of
# only the old home removes nothing once the files have moved.
homes = [h for h in (root / "dev/audit/rounds", root / "tools/audit") if h.is_dir()]
rounds = sorted({d for h in homes for d in h.glob("round*") if d.is_dir() and d.name != cur})
keep = {f for fs in json.loads((root / "tests/closures.json").read_text())["closures"].values()
        for f in fs if f.startswith(("dev/audit/rounds/round", "tools/audit/round"))}
lit = re.compile(r"(?:dev/audit/rounds/|tools/audit/)round[A-Za-z0-9_.-]*(?:/[A-Za-z0-9_.-]+)*")
for t in sorted(p for g in ("*.py", "*.mjs", "*.sh") for p in (root / "tests").glob(g)):
    for m in lit.findall(t.read_text(errors="replace")):
        p = root / m.rstrip("/.")
        depth = 4 if m.startswith("dev/audit/rounds/") else 3
        if p.is_file():
            keep.add(p.relative_to(root).as_posix())
        elif p.is_dir() and len(p.relative_to(root).parts) > depth:
            keep.update(f.relative_to(root).as_posix() for f in p.rglob("*") if f.is_file())
removed = kept = 0
for d in rounds:
    for f in sorted(d.rglob("*")):
        if f.is_file() or f.is_symlink():
            if f.relative_to(root).as_posix() in keep:
                kept += 1
            else:
                f.unlink()
                removed += 1
    for sub in sorted((d, *(p for p in d.rglob("*") if p.is_dir())), key=lambda p: -len(p.parts)):
        if not any(sub.iterdir()):
            sub.rmdir()
print(f"RESULT stripped_earlier_rounds={len(rounds)} files_removed={removed} files_kept={kept} dir={root}")
PY
}
# `prepare_baseline.sh --strip <export-dir> <round>` runs ONLY the earlier-round
# strip, on an export or a worktree some other path made: audit-find.js's Prepare
# (and the leads seat's own export) run it, so the driver and this script cannot
# disagree on what the wall leaves in (R9 box B1's wall breach: the driver copied
# tools/audit/ whole and nothing stripped it).
# The finder wall. docs/audit-2026-09.md is still under docs/; the August
# register and the backlog moved to dev/archive/ (R9-RO-4). A glob that names
# only the old directory removes nothing once the file has moved, and the
# export then carries the register the wall exists to keep out.
finder_wall() {
  local root="$1"
  rm -f "$root"/docs/audit-*.md \
        "$root"/dev/archive/audits/audit-*.md \
        "$root"/dev/archive/backlog.md \
        "$root"/dev/programme/register/audit-*.md
}
if [ "${1:-}" = "--wall-self-test" ]; then
  plant() {
    local d="$1"
    mkdir -p "$d/docs" "$d/dev/archive/audits" "$d/dev/programme/register"
    printf s > "$d/docs/audit-2026-09.md"
    printf a > "$d/dev/archive/audits/audit-2026-08.md"
    printf b > "$d/dev/archive/backlog.md"
    printf r > "$d/dev/programme/register/audit-2026-09.md"
    printf k > "$d/docs/setup.md"
  }
  old_wall() { rm -f "$1"/docs/audit-*.md "$1"/docs/backlog.md; }
  d1=$(mktemp -d); plant "$d1"; old_wall "$d1"
  [ ! -e "$d1/docs/audit-2026-09.md" ] || { echo "FAIL old wall kept the live register"; exit 1; }
  [ -e "$d1/dev/archive/audits/audit-2026-08.md" ] || { echo "FAIL old wall removed the archived register; the control no longer shows the miss"; exit 1; }
  [ -e "$d1/dev/archive/backlog.md" ] || { echo "FAIL old wall removed the archived backlog; the control no longer shows the miss"; exit 1; }
  [ -e "$d1/dev/programme/register/audit-2026-09.md" ] || { echo "FAIL old wall removed the programme register; the control no longer shows the miss"; exit 1; }
  [ -e "$d1/docs/setup.md" ] || { echo "FAIL old wall removed a reader doc"; exit 1; }
  d2=$(mktemp -d); plant "$d2"; finder_wall "$d2"
  [ ! -e "$d2/docs/audit-2026-09.md" ] || { echo "FAIL wall kept the live register"; exit 1; }
  [ ! -e "$d2/dev/archive/audits/audit-2026-08.md" ] || { echo "FAIL wall kept the archived register"; exit 1; }
  [ ! -e "$d2/dev/archive/backlog.md" ] || { echo "FAIL wall kept the archived backlog"; exit 1; }
  [ ! -e "$d2/dev/programme/register/audit-2026-09.md" ] || { echo "FAIL wall kept the programme register"; exit 1; }
  [ -e "$d2/docs/setup.md" ] || { echo "FAIL wall removed a reader doc"; exit 1; }
  rm -rf "$d1" "$d2"
  echo "RESULT finder_wall=ok"
  exit 0
fi
if [ "${1:-}" = "--strip-self-test" ]; then
  PYTHON="${PYTHON:-python3}"
  d=$(mktemp -d)
  mkdir -p "$d/dev/audit/rounds/round3" "$d/tools/audit/round3" "$d/dev/audit/rounds/round4/D6" "$d/tests"
  printf leak > "$d/dev/audit/rounds/round3/LEAK.md"
  printf old > "$d/tools/audit/round3/OLD.md"
  printf keep > "$d/dev/audit/rounds/round4/D6/claims.json"
  printf '%s\n' '{"closures":{"tests/x.py":["dev/audit/rounds/round4/D6/claims.json"]}}' > "$d/tests/closures.json"
  # The pre-edit wall globbed only tools/audit/round*. The new-path file must survive that.
  "$PYTHON" - "$d" 9 <<'ENDPY'
import sys
from pathlib import Path
root = Path(sys.argv[1])
cur = f"round{sys.argv[2]}"
rounds = sorted(d for d in (root / "tools/audit").glob("round*") if d.is_dir() and d.name != cur)
for d in rounds:
    for f in list(d.rglob("*")):
        if f.is_file():
            f.unlink()
ENDPY
  [ -e "$d/dev/audit/rounds/round3/LEAK.md" ] || { echo "FAIL old wall removed the new-path leak; the control no longer shows the miss"; exit 1; }
  [ ! -e "$d/tools/audit/round3/OLD.md" ] || { echo "FAIL old wall kept the old-path evidence"; exit 1; }
  ROUND=9 strip_earlier_rounds "$d"
  [ ! -e "$d/dev/audit/rounds/round3/LEAK.md" ] || { echo "FAIL strip kept the new-path leak"; exit 1; }
  [ -e "$d/dev/audit/rounds/round4/D6/claims.json" ] || { echo "FAIL strip removed a closure read"; exit 1; }
  rm -rf "$d"
  echo "RESULT strip_earlier_rounds=ok"
  exit 0
fi
if [ "${1:-}" = "--strip" ]; then
  PYTHON="${PYTHON:-python3}"; ROUND="${3:?round}"
  strip_earlier_rounds "$(cd "${2:?export dir}" && pwd)"
  exit 0
fi
ROUND="${1:?round}"; SHA="${2:?baseline sha}"; SRC="${3:-$(git rev-parse --show-toplevel)}"
cd "$(git rev-parse --show-toplevel)"
PARENT="$(cd .. && pwd)"
EXPORT="$PARENT/audit-r${ROUND}-baseline"
[ -e "$EXPORT" ] && { echo "refusing: $EXPORT exists"; exit 2; }
git rev-parse --verify --quiet "${SHA}^{commit}" >/dev/null || { echo "refusing: $SHA is not a commit here"; exit 2; }
FULL=$(git rev-parse "${SHA}^{commit}")
PYTHON="${PYTHON:-$PARENT/tvofi-claude/.venv/bin/python}"
[ -x "$PYTHON" ] || { echo "refusing: no interpreter at $PYTHON (set PYTHON)"; exit 2; }
# orjson is Home Assistant's serializer and optional to the gate, so a box without
# it measured nothing about the real boundary and said nothing: round 8's
# s1_finite_boundary.py fell back to a stub on one box only (judge note 1). The
# pin is Home Assistant's own, read from the hash-pinned typing lock, not carried.
ORJSON_PIN=$(sed -n 's/^orjson==\([^ ]*\) .*/\1/p' tests/requirements-typing.txt)
ORJSON_HAVE=$("$PYTHON" -c 'import orjson; print(orjson.__version__)' 2>/dev/null || echo none)
if [ -z "$ORJSON_PIN" ] || [ "$ORJSON_HAVE" != "$ORJSON_PIN" ]; then
  REQ=$(mktemp -d "${TMPDIR:-/tmp}/hpo-orjson.XXXXXX")/orjson.txt
  sed -n '/^orjson==/,/[^\\]$/p' tests/requirements-typing.txt > "$REQ"
  echo "refusing: $PYTHON has orjson $ORJSON_HAVE, tests/requirements-typing.txt pins ${ORJSON_PIN:-nothing}"
  echo "  install it hash-pinned, outside the cwd: \"$PYTHON\" -m pip install --require-hashes -r $REQ"
  exit 2
fi

mkdir -p "$EXPORT"
git archive "$FULL" | tar -x -C "$EXPORT"
# RELEASE_NOTES.md IS NOT DELETED, and the reason is a defect this line used to
# carry: tests/entities.py:12140 reads it with Path(...).read_text() at import,
# outside any guard, so an export without it ran 0 of its 1360 entity checks and
# died with FileNotFoundError before a finder's first measurement. COMMON.md and
# audit-find.js both say to keep it. The `finders_can_start` refusal below is the
# general form of that lesson and fires on any other file a test opens this way.
finder_wall "$EXPORT"
mkdir -p "$EXPORT/tools/audit"
cp -R "$SRC/tools/audit/." "$EXPORT/tools/audit/"     # instruments that stayed
mkdir -p "$EXPORT/dev/audit/rounds"
if [ -d "$SRC/dev/audit/rounds" ]; then cp -R "$SRC/dev/audit/rounds/." "$EXPORT/dev/audit/rounds/"; fi
mkdir -p "$EXPORT/dev/audit/rounds/round${ROUND}"

# Earlier rounds must not steer a finder -- COMMON.md's wall, and the reason the
# export drops docs/audit-*.md at all. Deleting only those two documents left the
# wall open twice over: `git archive` carries any tools/audit/round<N>/ that is
# tracked at the baseline, and the cp above copies every round the SOURCE
# checkout holds. Round 4 was prepared with 116 round-3 files in every finder
# tree, ledger/verdicts.tsv among them -- 43 findings with their verdicts and
# headlines.
#
# BUT THE GATE READS SOME OF THEM, so the wall stops at what a test reads
# (round 8, F1). Stripping every earlier round made finders_can_start below
# refuse this script's own output (tests/entities.py opens
# round4/D11/governance_cost.py and round4/D6/claims.json unguarded), and past
# that, tests/entities.py failed checks in a stripped tree that pass in an
# unstripped one: d11lib.py, dora_keys.py, the round-5 D13 harness and
# fixtures, the round-6 D13 fixtures, and the PHANTOM check that every file a
# committed closure names exists. What survives is the union of two rules, each
# derived from the tree being stripped, never a carried list:
#   1. every tools/audit/round*/ path tests/closures.json names -- the MEASURED
#      read set, which includes tests/harness_headers.py's discovery corpus;
#   2. every file (or directory's files) a literal tools/audit/round... string in
#      tests/*.py, tests/*.mjs or tests/*.sh names -- because a committed
#      closure can miss a read: the round-6 D13 fixtures, opened by a `node -e`
#      child of tests/entities.py, are in none. A literal naming a whole round
#      directory is ignored.
# Everything else in an earlier round -- reports, verdicts, ledgers, logs -- is
# removed. The instruments that survive are the ones dev/audit/harnesses/
# README.md's rule would keep live anyway: evidence is archived, instruments
# are kept.
strip_earlier_rounds "$EXPORT"

# One list, read three times below. audit-find.js's ISOLATED must agree with it;
# they are separate files and a seat that edits one edits both. D13 joined it
# with R7-INSTR-01 (#1477): the round driver's DIMS/WAVES/ISOLATED stopped at
# D12, and D13 reads `main`'s history and the API just as D11 does, so it needs
# a worktree rather than the export. The check in
# .claude/workflows/check-wave-script.mjs derives both lists and refuses them
# drifting apart again. D14 joined because it mutates production to prove its
# detectors move and runs them at pre-fix commits (tools/audit/briefs/D14.md).
ISOLATED_DIMS="D0 D3 D9 D11 D13 D14"

for dim in $ISOLATED_DIMS; do
  wt="$PARENT/audit-r${ROUND}-${dim}"
  [ -e "$wt" ] && { echo "refusing: $wt exists"; exit 2; }
  git worktree add --detach "$wt" "$FULL" >/dev/null
  mkdir -p "$wt/tools/audit"; cp -R "$SRC/tools/audit/." "$wt/tools/audit/"
  mkdir -p "$wt/dev/audit/rounds"
  if [ -d "$SRC/dev/audit/rounds" ]; then cp -R "$SRC/dev/audit/rounds/." "$wt/dev/audit/rounds/"; fi
  mkdir -p "$wt/dev/audit/rounds/round${ROUND}/${dim}"
  # A worktree is a real checkout, so this leaves tracked deletions in its status
  # rather than an absent file. That is the honest state and it costs nothing the
  # gate can see; BASELINE.md below says so, and a finder restoring its tree
  # around a mutant restores these with it.
  strip_earlier_rounds "$wt"
done

# THE REFUSAL THAT WOULD HAVE CAUGHT BOTH DEFECTS ABOVE, in its general form.
# Every literal path a tests/*.py script hands to Path(...) or open() must still
# exist in the finder tree if it exists in the source checkout. That is what
# separates a deliberate wall (docs/audit-*.md, dev/archive/audits/audit-*.md,
# dev/archive/backlog.md -- which no test
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
CHROMIUM=$(ls -d "$HOME"/.cache/pw-browsers/chromium-* 2>/dev/null | tr '\n' ' ' || true)
ISOLATED_DIRS=""; for dim in $ISOLATED_DIMS; do ISOLATED_DIRS="$ISOLATED_DIRS $PARENT/audit-r${ROUND}-${dim}"; done
for dir in "$EXPORT" $ISOLATED_DIRS; do
  mkdir -p "$dir/dev/audit/rounds/round${ROUND}"
  cat > "$dir/dev/audit/rounds/round${ROUND}/BASELINE.md" <<MD
# Round ${ROUND} baseline

- baseline: ${FULL}
- export (read-only finders): ${EXPORT}
- worktrees (isolated finders): $(for d in $ISOLATED_DIMS; do printf '%s %s/audit-r%s-%s, ' "$d" "$PARENT" "$ROUND" "$d"; done | sed 's/, $//')
- python: ${PYTHON} (run from the directory root with PYTHONPATH=tests/hastub)
- orjson: ${ORJSON_HAVE} in that interpreter (the typing lock's pin). The stub's
  json_bytes takes orjson whenever it imports and CI's gate job has none, so a
  gate check on that path may read differently here than on CI.
- temp root: derive every scratch path from \$TMPDIR (mktemp -d, tempfile.mkdtemp),
  pip download -d / install --target included -- never a literal seat path, never
  the cwd (tools/audit/README.md, the harness contract).
- node: ${NODE:-not found}
- chromium: ${CHROMIUM:-not found} (PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/pw-browsers)
- playwright module: the browser lane's own lock, integrity-checked:
  P=\$(mktemp -d); cp tests/pwlane/package.json tests/pwlane/package-lock.json "\$P/";
  npm ci --prefix "\$P"; "\$P/node_modules/.bin/playwright" install chromium (under the
  PLAYWRIGHT_BROWSERS_PATH above); NODE_PATH=\$P/node_modules
- gate lease: .claude/rules/gate-scoping.md. tests/run.sh takes it around each
  tests/stress.py run itself; stress.py run directly takes nothing, so wrap it:
  python3 tests/gate_lock.py auto-lease --label <your-label> -- python3 tests/stress.py
- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
MD
done
echo "RESULT export=$EXPORT"
echo "RESULT baseline=$FULL"
