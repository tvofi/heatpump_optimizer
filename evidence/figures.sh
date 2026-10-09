#!/bin/bash
# Reviewer's re-derivation of the two figures PR #2075's body quotes:
#   (a) #2065's "74-commit range" 3c9fe53fa -> 90b9e87f
#   (b) #2010's "one line out of 16,965 ... pure context" d67d8a44 -> 87849cd2
# Read-only. Runs in /private/tmp/r9-main.
set -uo pipefail
cd /private/tmp/r9-main || exit 9
BASE=b2b6acd64cde652676a568e93c05f021571ebe5e

echo "=== (a) #2065 range size ==="
printf 'RESULT 2065 rev-list --count (all)          = %s\n' \
  "$(git rev-list --count 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530..90b9e87f7dece277cfbf46cbc64b2b3f816d841c)"
printf 'RESULT 2065 rev-list --count --first-parent = %s\n' \
  "$(git rev-list --count --first-parent 3c9fe53fafcd3e9336ecc3574fedc713f3c3d530..90b9e87f7dece277cfbf46cbc64b2b3f816d841c)"
echo "--- the first-parent commits carry() actually walks ---"
git log --first-parent --format='  %h  %an  %s' \
  3c9fe53fafcd3e9336ecc3574fedc713f3c3d530..90b9e87f7dece277cfbf46cbc64b2b3f816d841c

echo
echo "=== (b) #2010 context-shift figure, with carry's own norm() pipeline ==="
d=(git -c core.quotepath=off diff --binary --no-renames --no-color --no-ext-diff --no-textconv
   --diff-algorithm=myers -U3)
t=$(git show "$BASE:.gitattributes" | awk '!/^#/ && / merge=/ {print ":(exclude)" $1}')
x=()
while IFS= read -r p; do [ -z "$p" ] || x[${#x[@]}]=$p; done <<<"$t"
mv=$(git merge-base "$BASE" d67d8a44ec6e6a2c93e2cedf126ba10ea00b2470)
mh=$(git merge-base "$BASE" 87849cd277485bd28bc85d64bc104293c5c7e6de)
echo "  mv = $mv"
echo "  mh = $mh"
"${d[@]}" "$mv" d67d8a44ec6e6a2c93e2cedf126ba10ea00b2470 -- . ${x[@]+"${x[@]}"} \
  | sed -e '/^index /d' -e 's/^@@ .*/@@/' > /tmp/r9-2010-v.txt
"${d[@]}" "$mh" 87849cd277485bd28bc85d64bc104293c5c7e6de -- . ${x[@]+"${x[@]}"} \
  | sed -e '/^index /d' -e 's/^@@ .*/@@/' > /tmp/r9-2010-h.txt
printf 'RESULT 2010 wc -l of mv..v side = %s\n' "$(wc -l < /tmp/r9-2010-v.txt)"
printf 'RESULT 2010 wc -l of mh..h side = %s\n' "$(wc -l < /tmp/r9-2010-h.txt)"
echo "  diff of the two sides, verbatim:"
diff /tmp/r9-2010-v.txt /tmp/r9-2010-h.txt | sed 's/^/    /'
printf 'RESULT 2010 diff output lines   = %s\n' "$(diff /tmp/r9-2010-v.txt /tmp/r9-2010-h.txt | wc -l)"
printf 'RESULT 2010 of those, lines whose payload starts with a single space (pure context) = %s\n' \
  "$(diff /tmp/r9-2010-v.txt /tmp/r9-2010-h.txt | grep -c '^[<>] ')"
printf 'RESULT 2010 of those, lines whose payload starts with + or - (branch own text)     = %s\n' \
  "$(diff /tmp/r9-2010-v.txt /tmp/r9-2010-h.txt | grep -c '^[<>] [++-]')"
