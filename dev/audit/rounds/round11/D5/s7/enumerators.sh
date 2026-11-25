#!/usr/bin/env bash
# The step enumerators of seat D5-s7 (D5.md steps 1-4), run from the export root:
#   bash dev/audit/rounds/round11/D5/s7/enumerators.sh M1|M2|M3|M4
# Each prints its step's universe one item per line (text_ledger.py over check_scopes.py's cells).
# M1: reader path x outline 'document' row; M2: outline 'heading' and 'link' rows;
# M3: units --dim D6 of those documents (Markdown/HTML); M4: units --dim D5.
set -euo pipefail
PY=${PY:-$HOME/venv-ci/bin/python3}
R=${REPO:-/home/user/heatpump_optimizer}; S=${REF:-92d38ecb640bd462f2e19c0814d0f0b7df1ee692}
TL="tools/audit/text_ledger.py"
case "$1" in
  M1) PYTHONPATH=tests/hastub "$PY" $TL outline --seat D5-s7 --repo "$R" --ref "$S" | awk -F'\t' '$3=="document"' |
        while IFS=$'\t' read -r f _ _ _; do for p in new-user-hacs feature-config developer-tests; do printf '%s\t%s\n' "$p" "$f"; done; done ;;
  M2) PYTHONPATH=tests/hastub "$PY" $TL outline --seat D5-s7 --repo "$R" --ref "$S" | awk -F'\t' '$3=="heading"||$3=="link"' ;;
  M3) PYTHONPATH=tests/hastub "$PY" $TL units --dim D6 --seat D5-s7 --repo "$R" --ref "$S" | grep -E '^[^#]*\.(md|mdc|html?)#' || true ;;
  M4) PYTHONPATH=tests/hastub "$PY" $TL units --dim D5 --seat D5-s7 --repo "$R" --ref "$S" ;;
  *) echo "usage: $0 M1|M2|M3|M4" >&2; exit 2 ;;
esac
