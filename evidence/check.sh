#!/bin/bash
# usage: check.sh <dir with docs/delivery> ; compares to base blob, validates with gh + reachability
D=$1; B=$2; fail=0
for n in 1838 1842 1843 1844 1849; do
  new=$(cat $D/docs/delivery/$n.md); old=$(git show $B:docs/delivery/$n.md)
  sha=$(echo "$new" | grep -o '\*\*merged\*\* [0-9a-f]\{8\}' | head -1 | awk '{print $2}')
  js=$(gh pr view $n --json state,mergeCommit -q '.state+" "+.mergeCommit.oid')
  st=${js% *}; full=${js#* }
  reach=no; git merge-base --is-ancestor "$sha" origin/main 2>/dev/null && reach=yes
  rest=$([ "${new/\*\*merged\*\* $sha/**open**}" == "$old" ] && echo same || echo DIFF)
  pre=$([ "${full:0:8}" == "$sha" ] && echo match || echo MISMATCH)
  echo "#$n state=$st sha=$sha full=${full:0:12} prefix=$pre reach=$reach rest=$rest"
  [ "$st" == MERGED -a $pre == match -a $reach == yes -a $rest == same ] || fail=1
done; echo "FAIL=$fail"
