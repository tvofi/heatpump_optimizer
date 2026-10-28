#!/bin/bash
# repro_causes.sh <first-pass relay> <first-pass args> <head relay>: relay with the first, then one head `pass --confirm`
HD=$(cd "$(dirname "$0")" && pwd)
R1=$(readlink -f "$1"); A1=$2; R=$(readlink -f "$3"); t=$(mktemp -d); export RELAY_T=$t
git init -q --bare "$t/o.git"; git init -q "$t/w"; cd "$t/w"; git remote add origin "$t/o.git"
export GIT_AUTHOR_NAME=x GIT_AUTHOR_EMAIL=x@x GIT_COMMITTER_NAME=x GIT_COMMITTER_EMAIL=x@x
git commit -q --allow-empty -m init; git push -q origin HEAD:refs/heads/main 2>/dev/null
h=0123456789abcdef0123456789abcdef01234567; n=0123456789abcdef0123456789abcdef
export HPO_STATE_DIR=$t/state HPO_BUS_STATE=$t/bus; mkdir -p $t/bus $t/state
printf '#!/bin/sh\n' > $t/none.sh; chmod +x $t/none.sh; export HPO_RELAY_PRS=$t/none.sh
sed -n '/^cat > \$t\/push.sh/,/^EOF/p' "$HD/repro_po.sh" | sed '1d;$d' > $t/push.sh
sed -n '/^cat > \$t\/confirm.sh/,/^EOF/p' "$HD/repro_po.sh" | sed '1d;$d' > $t/confirm.sh
chmod +x $t/push.sh $t/confirm.sh; export HPO_RELAY_PUSH=$t/push.sh HPO_RELAY_CONFIRM=$t/confirm.sh
rm -rf $t/pr; git init -q $t/pr; mkdir $t/pr/ev; echo 1 > $t/pr/ev/e
printf 'Fix review: merge %s\n\nbus-nonce: %s\n' $h $n > $t/pr/verdict.md
git -C $t/pr add -A; git -C $t/pr commit -qm "verdict 70 $h"; git -C $t/o.git fetch -qf $t/pr "HEAD:refs/heads/probe/rev-70-${n:0:8}"
echo "70 $h cloud $n" >> $t/bus/dispatched
bash "$R1" pass $A1 --log $t/log >/dev/null 2>&1
c1=$(grep -c "^70 " $t/calls 2>/dev/null); bash "$R" pass --confirm --log $t/log > $t/o 2>&1
echo "RESULT first_pass_calls=${c1:-0} after_head_confirm_pass_calls=$(grep -c '^70 ' $t/calls) posted=$(grep -c '^POSTED .* 70 ' $t/log)"; rm -rf $t
