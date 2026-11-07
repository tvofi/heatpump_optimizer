# usage: drive_pp.sh <tree-with-plan_public.py>
set -u; T=$1; S=$(mktemp -d); cd $S; git init -q r; cd r
mkdir -p handoff/round10/state; printf '<!doctype html><html><body>plan r10</body></html>\n' > handoff/round10/state/PLAN.html
git add -A; git -c user.name=t -c user.email=t@t commit -qm s; git update-ref refs/remotes/origin/handoff/audit-r10-plan HEAD
python3 -I $T/tools/audit/seat/plan_public.py stage --out $S/out --repo $S/r; echo "clean page: rc=$?  staged=$(test -f $S/out/plan/index.html && echo yes || echo no)"
printf '<!doctype html><html><body>see /ho''me/someone/wt</body></html>\n' > handoff/round10/state/PLAN.html; git commit -qam leak; git update-ref refs/remotes/origin/handoff/audit-r10-plan HEAD
rm -rf $S/out; python3 -I $T/tools/audit/seat/plan_public.py stage --out $S/out --repo $S/r; echo "leaky page: rc=$?  staged=$(test -f $S/out/plan/index.html && echo yes || echo no)"
