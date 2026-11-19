#!/usr/bin/env bash
# D5-s10 step enumerators (COMMON.md "The denominator"): prints one universe item per line for the step named.
#   bash dev/audit/rounds/round11/D5/s10/enumerate.sh M1|M2|M3|M4 [REPO] [REF]
# M1: each reader path x each `document` row of text_ledger.py outline over the seat's cells.
# M2: the `heading` and `link` rows of that outline.
# M3: the D6 units (text_ledger.py units --dim D6) of those documents.
# M4: the D5 units (text_ledger.py units --dim D5) of the seat's cells.
# Expected at 92d38ecb (round 11): M1 0, M2 0, M3 0, M4 1794 lines -- the cells hold no Markdown or HTML.
set -euo pipefail
STEP=$1; REPO=${2:-/home/user/heatpump_optimizer}; REF=${3:-92d38ecb640bd462f2e19c0814d0f0b7df1ee692}
TL="python3 tools/audit/text_ledger.py"; S="--seat D5-s10 --repo $REPO --ref $REF"
docs() { $TL outline $S | awk -F'\t' '$3=="document"{print $1}'; }
case $STEP in
  M1) for r in hacs-install-to-first-plan configure-feature developer-runs-tests; do docs | sed "s|^|$r\t|"; done ;;
  M2) $TL outline $S | awk -F'\t' '$3=="heading"||$3=="link"' ;;
  M3) d=$(docs); [ -z "$d" ] || $TL units --dim D6 $d ;;
  M4) $TL units --dim D5 $S ;;
  *) echo "usage: enumerate.sh M1|M2|M3|M4" >&2; exit 2 ;;
esac
