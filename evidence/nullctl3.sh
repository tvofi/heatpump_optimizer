#!/bin/bash
# Three-copy live-pair null control for PR #2075 round 2. The COPY of the
# instrument is the variable, not only the main ref: base-copy is main before
# #2059 (no `bot_paths` at all), main-copy is current main (d0f085ffb, #2059's
# coarse subtree exclusion), head-copy is the re-cut (cfa0f3d00).
# Read-only: git reads run in /private/tmp/r9-main.
set -uo pipefail
EV=/Users/timmalmstrom/hpo-seats/review-2075/evidence2
BASECOPY=$EV/copies/app_approve.base-b2b6acd64.sh
MAINCOPY=$EV/copies/app_approve.main-d0f085ffb.sh
HEADCOPY=$EV/copies/app_approve.head-cfa0f3d00.sh
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
  git log --first-parent --format='  %H  %an <%ae>  %s' "$v..$h"
  git diff --no-renames --name-status "$h^" "$h" | sed 's/^/  commit-diff /'
  run "base-copy-#$pr" "$BASECOPY" "$v" "$h" origin/main
  run "main-copy-#$pr" "$MAINCOPY" "$v" "$h" origin/main
  run "head-copy-#$pr" "$HEADCOPY" "$v" "$h" origin/main
done

echo "########## #2065 74-commit range 3c9fe53fa -> 90b9e87f (must REFUSE at all three)"
git log --first-parent --format='  %H' 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530..90b9e87f7dece277cfbf46cbc64b2b3f816d841c | wc -l | sed 's/^/  first-parent commits: /'
git log --format='  %H' 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530..90b9e87f7dece277cfbf46cbc64b2b3f816d841c | wc -l | sed 's/^/  all commits: /'
run "base-copy-#2065" "$BASECOPY" 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530 90b9e87f7dece277cfbf46cbc64b2b3f816d841c origin/main
run "main-copy-#2065" "$MAINCOPY" 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530 90b9e87f7dece277cfbf46cbc64b2b3f816d841c origin/main
run "head-copy-#2065" "$HEADCOPY" 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530 90b9e87f7dece277cfbf46cbc64b2b3f816d841c origin/main

echo "########## #2010 context shift d67d8a44 -> 87849cd2 (must STILL refuse at the head)"
run "base-copy-#2010" "$BASECOPY" "$(git rev-parse d67d8a44)" 87849cd277485bd28bc85d64bc104293c5c7e6de origin/main
run "head-copy-#2010" "$HEADCOPY" "$(git rev-parse d67d8a44)" 87849cd277485bd28bc85d64bc104293c5c7e6de origin/main
