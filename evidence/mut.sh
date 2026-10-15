#!/bin/bash
set -u
R=$1; cd $R/wt; F=tools/policy/policy_lint.mjs
run(){ PYTHONPATH=tests/hastub python3 tests/entities.py > $R/evidence/mut_$1.out 2>&1; echo "$1 rc=$? $(grep -E 'ENTITY CHECKS' $R/evidence/mut_$1.out | tail -1)"; git checkout -q -- $F; }
# M1 restore the verdict-map bump
perl -0pi -e 's/(      rounds\[kind\]\.prs\.add\(pr\)\n)/$1      if (kind === "reverify" \&\& cur.word !== REWORK_CLASS) bump(verdicts, REWORK_CLASS, pr)\n/' $F; git diff --stat; run M1
# M2 drop canon in frictionKey
perl -pi -e 's/const bare = canon\(raw\.replace\(\/\^`\+\|`\+\$\/g, .....\)\.replace\(\/#\.\*\$\/, ..\)\)/const bare = raw.replace(\/^`+|`+\$\/g, "").replace(\/#.*\$\/, "")/' $F; git diff --stat; run M2
# M3 class constant
perl -pi -e "s/^  if \(!f\) return '\(unfetched\)'/  return '(untyped)'; if (!f) return '(unfetched)'/" $F; git diff --stat; run M3
# M4 rework row empty
perl -pi -e 's/rework: new Map\(rounds\.reverify\.entries \? \[\[REWORK_KEY, rounds\.reverify\]\] : \[\]\)/rework: new Map()/' $F; git diff --stat; run M4
git status --short
