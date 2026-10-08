#!/bin/bash
export GIT_BIN=/Users/timmalmstrom/hpo-seats/review-2051/git255/bin
R=/Users/timmalmstrom/hpo-seats/review-2054/wt; M=/Users/timmalmstrom/hpo-seats/review-2054/mut
echo "### head $(git -C $R rev-parse HEAD) $(date -u +%FT%TZ)"
echo "## hostile 1 all"; bash $R/dev/audit/harnesses/throwaway_git_sites.sh 1 hostile
echo "## hostile 5 stamp"; bash $R/dev/audit/harnesses/throwaway_git_sites.sh 5 hostile stamp
echo "## plain 1 all"; bash $R/dev/audit/harnesses/throwaway_git_sites.sh 1 plain
echo "## mutant: roster_edit without throwaway_git_environ, hostile 1"
python3 - <<'PY'
p='/Users/timmalmstrom/hpo-seats/review-2054/mut/tools/audit/seat/roster_edit.py';s=open(p).read()
a="        with throwaway_git_environ():\n            return _self_test()"
assert a in s; open(p,'w').write(s.replace(a,"        return _self_test()",1))
PY
bash $M/dev/audit/harnesses/throwaway_git_sites.sh 1 hostile roster_edit
git -C $M checkout -q -- tools/audit/seat/roster_edit.py
echo DONE
