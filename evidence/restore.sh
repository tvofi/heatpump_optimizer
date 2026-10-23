#!/bin/bash
# restore.sh <worktree> <pinned sha> <yml> <job>: extract the job's pathspec list from the workflow and checkout from PINNED, as governance.yml does
set -euo pipefail
wt=$1 P=$2 yml=$3 job=$4
specs=$(python3 - "$yml" "$job" <<'P'
import sys,re
t=open(sys.argv[1]).read().split('\n')
job=sys.argv[2]; i=t.index(f'  {job}:')
j=next(k for k in range(i,len(t)) if 'Restore the check source from the base commit' in t[k])
k=next(k for k in range(j,len(t)) if 'git diff --name-only -z' in t[k])
out=[]
for l in t[k+1:]:
    out+=re.findall(r"'([^']+)'",l)
    if 'pinned.list' in l: break
print('\n'.join(out))
P
)
cd "$wt"; rm -rf .claude/workflows/vendor
mapfile -t arr <<<"$specs"
git diff --name-only -z "$(git hash-object -t tree /dev/null)" "$P" -- "${arr[@]}" > /tmp/claude-0/pinned.$job
git checkout "$P" --pathspec-from-file=/tmp/claude-0/pinned.$job --pathspec-file-nul
echo "restored from $P: $(git diff --cached --name-only | wc -l) file(s) differ ($job)"
git diff --cached --name-only
