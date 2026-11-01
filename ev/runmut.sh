W=$(cat /tmp/claude-0/W); R=/home/user/heatpump_optimizer
for m in "$@"; do
  wt=$(mktemp -d)/wt; git -C $R worktree add -q --detach $wt 32d880b3dee4e525d16ec270af83d867f7006431
  ( cd $wt && python3 /tmp/claude-0/scripts/mut.py $m tools/pr/app_approve.sh && git diff --stat && env -u BASH_ENV bash tools/pr/app_approve.sh --self-test; echo "rc=$?"; git checkout -q -- tools/pr/app_approve.sh; git diff --quiet -- tools/pr/app_approve.sh && echo restored ) > $W/ev/mut-$m.log 2>&1
  git -C $R worktree remove --force $wt
done
