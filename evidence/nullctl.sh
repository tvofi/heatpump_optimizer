#!/bin/bash
# Reviewer's own null-control harness for PR #2075. Read-only: runs `git` reads
# in /private/tmp/r9-main and `--carry` from both main's and the head's copy of
# tools/pr/app_approve.sh. Prints RESULT lines the verdict quotes.
set -uo pipefail
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence
MAINCOPY=/private/tmp/r9-main/tools/pr/app_approve.sh
FIXCOPY=/Users/timmalmstrom/hpo-seats/review-2075/wt/tools/pr/app_approve.sh
BASE=b2b6acd64cde652676a568e93c05f021571ebe5e
cd /private/tmp/r9-main || exit 9

run() { # label script v h mainref
  local label=$1 script=$2 v=$3 h=$4 m=$5 out rc
  out=$(bash "$script" --carry "$v" "$h" "$m" 2>&1); rc=$?
  printf '%s\n' "  [$label main=$m] rc=$rc"
  printf '%s\n' "$out" | sed 's/^/    /'
  if [ "$rc" = 0 ]; then echo "RESULT $label $m CARRY"; else echo "RESULT $label $m REFUSE"; fi
}

for spec in \
  "2071 6aaba97fef582f7381fda9b270c1cfd25e64324d 7843b799255741fcfee41c6d719d3de1bef84c50" \
  "2070 3ecb86adaf247f182679a175bd619fd363a5e35c a9ba0b8874092db8780f93fa290b282b5ce200b5" \
  "2066 b511f9dc5b9ee076d3113aaad4b9e296222bbd7c d1538a73bbd89e806f01af6c01fc72090304e4f6" ; do
  set -- $spec
  pr=$1; v=$2; h=$3
  echo "########## PR #$pr  $v -> $h"
  echo "--- commits between (first-parent, %H %an <%ae> %s) ---"
  git log --first-parent --format='  %H  %an <%ae>  %s' "$v..$h"
  echo "--- head commit's own diff (name-status vs its parent) ---"
  git diff --no-renames --name-status "$h^" "$h" | sed 's/^/  /'
  run "main-copy-#$pr" "$MAINCOPY" "$v" "$h" "$BASE"
  run "main-copy-#$pr" "$MAINCOPY" "$v" "$h" origin/main
  run "fixed-copy-#$pr" "$FIXCOPY" "$v" "$h" "$BASE"
  run "fixed-copy-#$pr" "$FIXCOPY" "$v" "$h" origin/main
done

echo "########## #2065 74-commit range 3c9fe53fa -> 90b9e87f"
git log --first-parent --format='  %H  %an <%ae>  %s' 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530..90b9e87f7dece277cfbf46cbc64b2b3f816d841c | wc -l | sed 's/^/  first-parent commits: /'
run "main-copy-#2065" "$MAINCOPY" 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530 90b9e87f7dece277cfbf46cbc64b2b3f816d841c "$BASE"
run "fixed-copy-#2065" "$FIXCOPY" 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530 90b9e87f7dece277cfbf46cbc64b2b3f816d841c "$BASE"
run "main-copy-#2065" "$MAINCOPY" 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530 90b9e87f7dece277cfbf46cbc64b2b3f816d841c origin/main
run "fixed-copy-#2065" "$FIXCOPY" 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530 90b9e87f7dece277cfbf46cbc64b2b3f816d841c origin/main

echo "########## #2010 context shift d67d8a44 -> 87849cd2 (must STILL refuse at the fixed copy)"
git log --first-parent --format='  %H  %an <%ae>  %s' d67d8a44..87849cd277485bd28bc85d64bc104293c5c7e6de | sed -n '1,10p'
run "main-copy-#2010" "$MAINCOPY" "$(git rev-parse d67d8a44)" 87849cd277485bd28bc85d64bc104293c5c7e6de "$BASE"
run "fixed-copy-#2010" "$FIXCOPY" "$(git rev-parse d67d8a44)" 87849cd277485bd28bc85d64bc104293c5c7e6de "$BASE"
run "fixed-copy-#2010" "$FIXCOPY" "$(git rev-parse d67d8a44)" 87849cd277485bd28bc85d64bc104293c5c7e6de origin/main
