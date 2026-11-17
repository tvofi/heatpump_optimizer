#!/bin/bash
# usage: zero_cache.sh <prepr.sh> : a 2-commit branch; the head has NO check run yet (total_count 0,
# just pushed); first read; then a red lands on the head; second read within the TTL.
set -u
ROOT=$HOME/wt
. "$ROOT/tests/throwaway_git.sh" || exit 2
SRC=$(realpath "$1"); W=$(mktemp -d); cd "$W"
throwaway_git_env
export GIT_AUTHOR_NAME=st GIT_AUTHOR_EMAIL=st@st GIT_COMMITTER_NAME=st GIT_COMMITTER_EMAIL=st@st GIT_AUTHOR_DATE='2005-04-07T22:13:13 +0000' GIT_COMMITTER_DATE='2005-04-07T22:13:13 +0000'
throwaway_git_init . -q -b main && git remote add origin https://github.com/tvofi/heatpump_optimizer.git
echo a > code; git add -A; git -c commit.gpgsign=false commit -qm base
tree=$(git write-tree); c1=$(git commit-tree "$tree" -p HEAD -m c1); c2=$(git commit-tree "$tree" -p "$c1" -m c2)
git update-ref refs/remotes/origin/br "$c2"; git update-ref refs/remotes/origin/main main
mkdir fix
printf '{"total_count":1,"check_runs":[{"name":"fast","status":"completed","conclusion":"success"}]}' >fix/$c1.json
printf '{"total_count":0,"check_runs":[]}' >fix/$c2.json
cat > gh <<'EOS'
#!/bin/bash
f=""; u=""; p=""
for a in "$@"; do [ "$p" = "--jq" ] && f=$a; case "$a" in repos/*/commits/*/check-runs) u=$a ;; esac; p=$a; done
echo "$u" >>"$CALLS"; s=${u#*/commits/}; s=${s%/check-runs}; exec jq -r "$f" "$FIX/$s.json"
EOS
chmod +x gh
awk '/^REDS_JQ=/{p=1} /^reds_line\(\)/{p=0} /^# Step 7c/{p=0} p' "$SRC" > fn.sh
sed -i 's/^reds_line.*//' fn.sh
. ./fn.sh
export GITHUB_TOKEN=x PREPR_GH=$W/gh FIX=$W/fix PREPR_ANCESTRY_TTL_S=3600 HPO_STATE_DIR=$W/state CALLS=$W/calls
: >$W/calls; out=$(ancestry_reds origin/br); echo "read1 (head has no run yet) rc=$? calls=$(wc -l <$W/calls) out=[$out]"
printf '{"total_count":1,"check_runs":[{"name":"closures","status":"completed","conclusion":"failure"}]}' >fix/$c2.json
: >$W/calls; out=$(ancestry_reds origin/br); echo "read2 (a red landed on the head) rc=$? calls=$(wc -l <$W/calls) out=[$out]"
