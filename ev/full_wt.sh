set -u
k=$1; S=$2; d=/root/wtm_$k
cd /home/user/heatpump_optimizer && git worktree add -q --detach $d d6a54399a63b76d43c4f3a84e1d2ac518da28ed0
cd $d && python3 - "$(cat $S/m/$k.f)" "$S/m/$k.old" "$S/m/$k.new" <<'PY'
import sys; f="custom_components/heatpump_optimizer/"+sys.argv[1]; old=open(sys.argv[2]).read(); new=open(sys.argv[3]).read()
s=open(f).read(); assert s.count(old)==1, "stale"; open(f,"w").write(s.replace(old,new))
PY
git diff --stat | tail -1
PYTHONPATH=tests/hastub timeout 3000 python3 tests/features.py > $S/full_$k.out 2>&1; echo "features rc=$?"; grep -E '^ *FAIL ' $S/full_$k.out | head -5; tail -1 $S/full_$k.out
