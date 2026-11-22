#!/bin/bash
# Delta-review driver at 8800ed7c: the P2 and 3B feature blocks, tests/manual_plan.py, under two mutants of the moved helpers.
EV=$(dirname "$0"); cd /home/user/rev3838; export PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1
R=custom_components/heatpump_optimizer/rooms.py
blk(){ # $1 label
  timeout 900 python3 tools/audit/seat/features_block.py --prelude "exec(open('$EV/P2.py').read())" 'R.section("#3616 R11-OUTSIDE-ROOMS-P2' 'R.section("R10-DRAW-MAP-EVIDENCE part A' > $EV/out.P2.$1 2>&1; echo "$1 P2 rc=$? $(tail -1 $EV/out.P2.$1)"
  timeout 900 python3 tools/audit/seat/features_block.py --prelude "exec(open('$EV/P3B.py').read())" 'R.section("#3616 R11-OUTSIDE-ROOMS-3B' > $EV/out.3B.$1 2>&1; echo "$1 3B rc=$? $(tail -1 $EV/out.3B.$1)"
  grep -E '^ *FAIL' $EV/out.P2.$1 $EV/out.3B.$1 | cut -c1-220
}
mp(){ timeout 900 python3 tests/manual_plan.py > $EV/out.mp.$1 2>&1; echo "$1 manual_plan rc=$? $(tail -1 $EV/out.mp.$1)"; }
blk unmutated; mp unmutated
cp $R $EV/rooms.bak
python3 - "$R" <<'PY'
import sys;p=sys.argv[1];s=open(p).read();o="    return np.minimum(low, high - 0.5), comfort, mold";assert s.count(o)==1;open(p,"w").write(s.replace(o,"    return (low), comfort, mold"))
PY
blk M1_raised_floor_CLAMP_DROP; cp $EV/rooms.bak $R
python3 - "$R" <<'PY'
import sys;p=sys.argv[1];s=open(p).read();o="    if room_lifts is None:\n        return reasons";assert s.count(o)==1;open(p,"w").write(s.replace(o,"    if False:\n        return reasons"))
PY
mp M2_mark_room_floor_GUARD_OFF; blk M2_mark_room_floor_GUARD_OFF; cp $EV/rooms.bak $R
git status --short custom_components; echo DONE
