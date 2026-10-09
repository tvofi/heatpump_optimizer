#!/bin/bash
# Does main's CURRENT copy (d8a4bd36f, after #2059 landed a bot-subject carry on
# the same seam) already carry the pin commits PR #2075 exists to fix?
# Read-only. Runs from /private/tmp/r9-main.
set -uo pipefail
MAINCOPY=/Users/timmalmstrom/hpo-seats/review-2075/mainnow/tools/pr/app_approve.sh
FIXCOPY=/Users/timmalmstrom/hpo-seats/review-2075/wt/tools/pr/app_approve.sh
BASECOPY=/private/tmp/r9-main/tools/pr/app_approve.sh
cd /private/tmp/r9-main || exit 9

one() { # label script v h
  local label=$1 script=$2 v=$3 h=$4 out rc verdict
  out=$(bash "$script" --carry "$v" "$h" origin/main 2>&1); rc=$?
  [ "$rc" = 0 ] && verdict=CARRY || verdict=REFUSE
  printf '    %-26s rc=%s %s\n' "$label" "$rc" "$verdict"
  printf '%s\n' "$out" | sed 's/^/      /'
  echo "RESULT $label $v->$h $verdict"
}

for spec in \
  "2071 6aaba97fef582f7381fda9b270c1cfd25e64324d 7843b799255741fcfee41c6d719d3de1bef84c50" \
  "2070 3ecb86adaf247f182679a175bd619fd363a5e35c a9ba0b8874092db8780f93fa290b282b5ce200b5" \
  "2066 b511f9dc5b9ee076d3113aaad4b9e296222bbd7c d1538a73bbd89e806f01af6c01fc72090304e4f6" ; do
  set -- $spec
  echo "########## PR #$1  $2 -> $3   (main ref = origin/main = $(git rev-parse origin/main))"
  one "base-copy-b2b6acd64"  "$BASECOPY" "$2" "$3"
  one "main-copy-d8a4bd36f"  "$MAINCOPY" "$2" "$3"
  one "head-copy-094f2c0d2"  "$FIXCOPY"  "$2" "$3"
done

echo
echo "=== main's CURRENT copy: does its own self-test still pass, and how many checks? ==="
( cd /Users/timmalmstrom/hpo-seats/review-2075/mainnow && bash tools/pr/app_approve.sh --self-test > /Users/timmalmstrom/hpo-seats/review-2075/evidence/selftest-mainnow.txt 2>&1 )
echo "  rc=$?  $(tail -1 /Users/timmalmstrom/hpo-seats/review-2075/evidence/selftest-mainnow.txt)"
echo "  its own pin-commit arms:"
grep -n "pin killed mutants\|bot_paths\|its subject" /Users/timmalmstrom/hpo-seats/review-2075/evidence/selftest-mainnow.txt | head -12 | sed 's/^/    /'

echo
echo "=== main's CURRENT layout.py guard on the HEAD's line (is the red still the head's?) ==="
echo "  (answered by tests/layout.py at both ends; see layout-head4.txt / layout-base4.txt)"
