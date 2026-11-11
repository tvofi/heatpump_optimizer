#!/bin/bash
# for each named survivor: locate its line at the block head (stated line, or a fixed-string grep),
# then report whether diff mode lists a mutant on that line, and its rank (cap 40 = rank <= 40)
cd /root/wt
while IFS='|' read key file line pat; do
  pr=${key%-*}; h8=${key#*-}; head=$(awk -v p=$pr -v h=$h8 '$1==p && index($2,h)==1{print $2}' /tmp/claude-0/sp/bases.txt)
  L=/tmp/claude-0/sp/lists/$key.list
  if [ -z "$line" ]; then line=$(git show $head:$file 2>/dev/null | grep -nF -- "$pat" | cut -d: -f1 | tr '\n' ','); line=${line%,}; fi
  hit=""; for l in ${line//,/ }; do r=$(grep -n "^MUTANT $file:$l " $L | head -1 | cut -d: -f1); [ -n "$r" ] && hit="$hit $l@rank$r"; done
  echo "$key $file lines=[$line] listed:${hit:- none}"
done
