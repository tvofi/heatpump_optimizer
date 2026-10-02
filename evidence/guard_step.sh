set -euo pipefail
if ! git cat-file -e "$PINNED:.claude/workflows/agreement.mjs"; then
  echo "agreement lane: the base does not carry it, so its readers were restored from a base that predates it; skipped"
else
  python3 -I .claude/workflows/agreement_py.py --out "$RUNNER_TEMP/agreement.json"
  node .claude/workflows/agreement.mjs --py-json "$RUNNER_TEMP/agreement.json"
fi

