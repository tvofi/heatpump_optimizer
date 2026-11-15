#!/bin/bash
# usage: ancestry_calls.sh <prepr.sh file>
# The calls one `ancestry_reds` read makes (tools/pr/prepr.sh) over a synthetic 520-commit all-green
# branch and a 2-commit one, cold (the kept reads off): a stub gh counts each check-runs url and real jq
# applies the filter. Run it at `git show origin/main:tools/pr/prepr.sh` and at the head to compare.
set -u
ROOT=$(cd "$(dirname "$0")/../../.." && pwd -P)
. "$ROOT/tests/throwaway_git.sh" || exit 2
SRC=$(realpath "${1:?usage: ancestry_calls.sh <prepr.sh>}"); W=$(mktemp -d); cd "$W"
throwaway_git_env
export GIT_AUTHOR_NAME=st GIT_AUTHOR_EMAIL=st@st GIT_COMMITTER_NAME=st GIT_COMMITTER_EMAIL=st@st GIT_AUTHOR_DATE='2005-04-07T22:13:13 +0000' GIT_COMMITTER_DATE='2005-04-07T22:13:13 +0000'
throwaway_git_init . -q -b main && git remote add origin https://github.com/tvofi/heatpump_optimizer.git
echo a > code; git add -A; git -c commit.gpgsign=false commit -qm base
tree=$(git write-tree); parent=$(git rev-parse HEAD); first=$parent
for i in $(seq 1 520); do parent=$(git commit-tree "$tree" -p "$parent" -m "c$i"); [ "$i" = 2 ] && two=$parent; done
git update-ref refs/remotes/origin/long "$parent"; git update-ref refs/remotes/origin/two "$two"; git update-ref refs/remotes/origin/main main
mkdir fix; for sha in $(git rev-list main..origin/long); do printf '{"total_count":1,"check_runs":[{"name":"fast (3.14)","status":"completed","conclusion":"success"}]}' >fix/$sha.json; done
cat > gh <<'EOS'
#!/bin/bash
f=""; u=""; p=""
for a in "$@"; do [ "$p" = "--jq" ] && f=$a; case "$a" in repos/*/commits/*/check-runs) u=$a ;; esac; p=$a; done
echo "$u" >>"$CALLS"; s=${u#*/commits/}; s=${s%/check-runs}; exec jq -r "$f" "$FIX/$s.json"
EOS
chmod +x gh
# the function text: from REDS_JQ= through the end of ancestry_reds, plus gh_credential
awk '/^REDS_JQ=/{p=1} /^reds_line\(\)/{p=0} /^# Step 7c/{p=0} p' "$SRC" > fn.sh
sed -i 's/^reds_line.*//' fn.sh
. ./fn.sh
export GITHUB_TOKEN=x PREPR_GH=$W/gh FIX=$W/fix PREPR_ANCESTRY_TTL_S=0 HPO_STATE_DIR=$W/state
for br in long two; do : >"$W/calls"; export CALLS=$W/calls
  out=$(ancestry_reds origin/$br); rc=$?
  echo "$br rc=$rc commits=$(git rev-list main..origin/$br | wc -l) calls=$(wc -l <"$W/calls") out=[$out]"
done
