#!/bin/bash
# usage: drive.sh <hook> ; prints rc per probe. Reviewer's own driver.
HOOK=$1
T=$(mktemp -d); git init -q $T/orch; git -C $T/orch commit -q --allow-empty -m x; git init -q $T/other; git -C $T/other commit -q --allow-empty -m x
mkdir -p $T/state; echo $T/orch > $T/state/orch-checkout
export HPO_STATE_DIR=$T/state
O=$T/orch
p() { # cwd-name, command
  local cwd=$T/$1
  local pl; pl=$(python3 -c 'import json,sys; print(json.dumps({"tool_name":"Bash","cwd":sys.argv[2],"tool_input":{"command":sys.argv[1]}}))' "$2" "$cwd")
  echo "$pl" | bash $HOOK >/dev/null 2>&1; echo "rc=$? cwd=$1 :: ${2//$T/<T>}"
}
echo "# controls"
p orch 'git pull'
p orch 'git status'
p other 'git pull'
p orch 'git fetch'
p other "git -C $O show origin/main:x"
echo "# prior block's five probes"
p orch "bash -c 'git pull'"
p orch 'eval git pull'
p other "(cd $O && git pull)"
p other "echo x \$(git -C $O checkout main)"
p other "sh -c 'cd $O; git reset --hard'"
echo "# design acceptance rows (cwd and -C)"
for s in checkout switch reset pull merge rebase stash clean restore; do p orch "git $s"; p other "git -C $O $s"; done
echo "# false positives"
p orch "echo 'git pull' > notes.txt"
p orch "grep 'git reset' file"
p orch "cat <<EOF2
git pull
EOF2"
echo "# repository-selection seams outside the census"
p other "pushd $O && git pull"
p other "git --git-dir=$O/.git --work-tree=$O reset --hard"
p other "git --git-dir $O/.git --work-tree $O reset --hard"
p other "GIT_DIR=$O/.git GIT_WORK_TREE=$O git reset --hard"
p other "env GIT_DIR=$O/.git git -C $T/other reset --hard"
p other "timeout 5 git -C $O pull"
p other "cd $O; eval 'git pull'"
p other "eval \"cd $O && git pull\""
p other "cd $O
git pull"
p other "if true; then git -C $O pull; fi"
p other "{ git -C $O pull; }"
p other "for x in 1; do git -C $O pull; done"
p other "true && (git -C $O pull)"
p other "xargs git -C $O pull < /dev/null"
p other "git -C$O pull"
p other "D=$O; git -C \$D pull"
p orch "git -c core.x=1 pull"
p orch "git --no-pager pull"
p orch "git worktree add ../wt"
rm -rf $T
