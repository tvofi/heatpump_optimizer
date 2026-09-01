#!/usr/bin/env bash
# Prepare a round's audit baseline: a git-archive export the finders work in
# (no .git, no earlier audit records), one worktree per finder that mutates
# production, and the current briefs copied into each.
#
#   tools/audit/prepare_baseline.sh <round> <baseline-sha> [<briefs-source-checkout>]
#
# Run from any checkout of the repository. Creates, beside the repository's
# worktrees directory:
#   ../audit-r<round>-baseline        the export (D1, D2, D4, D5, D6, D7, D8, D10)
#   ../audit-r<round>-D0 / -D3 / -D9  worktrees at the baseline (instrumenting finders)
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
rm -f "$EXPORT"/docs/audit-*.md "$EXPORT"/docs/backlog.md "$EXPORT"/RELEASE_NOTES.md
mkdir -p "$EXPORT/tools/audit"
cp -R "$SRC/tools/audit/." "$EXPORT/tools/audit/"     # current briefs, README, schema
mkdir -p "$EXPORT/tools/audit/round${ROUND}"

for dim in D0 D3 D9; do
  wt="$PARENT/audit-r${ROUND}-${dim}"
  [ -e "$wt" ] && { echo "refusing: $wt exists"; exit 2; }
  git worktree add --detach "$wt" "$FULL" >/dev/null
  mkdir -p "$wt/tools/audit"; cp -R "$SRC/tools/audit/." "$wt/tools/audit/"
  mkdir -p "$wt/tools/audit/round${ROUND}/${dim}"
done

NODE=$(command -v node || true)
CHROMIUM=$(ls -d "$HOME"/.cache/pw-browsers/chromium-* 2>/dev/null | head -1 || true)
for dir in "$EXPORT" "$PARENT/audit-r${ROUND}-D0" "$PARENT/audit-r${ROUND}-D3" "$PARENT/audit-r${ROUND}-D9"; do
  cat > "$dir/tools/audit/round${ROUND}/BASELINE.md" <<MD
# Round ${ROUND} baseline

- baseline: ${FULL}
- export (read-only finders): ${EXPORT}
- worktrees (instrumenting finders): D0 ${PARENT}/audit-r${ROUND}-D0, D3 ${PARENT}/audit-r${ROUND}-D3, D9 ${PARENT}/audit-r${ROUND}-D9
- python: ${PYTHON} (run from the directory root with PYTHONPATH=tests/hastub)
- node: ${NODE:-not found}
- chromium: ${CHROMIUM:-not found} (PLAYWRIGHT_BROWSERS_PATH=\$HOME/.cache/pw-browsers)
- playwright module: install into a scratch prefix, e.g. \`npm i --prefix /tmp/pw playwright@1.49.0\`, then NODE_PATH=/tmp/pw/node_modules
- gate lock: mkdir /tmp/hpo-gate.lock before any tests/run.sh; rmdir after
- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
MD
done
echo "RESULT export=$EXPORT"
echo "RESULT baseline=$FULL"
