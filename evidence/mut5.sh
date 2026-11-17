#!/bin/bash
# usage: mut5.sh  -- runs each of the five mutants against old and new tests/features.py rooms blocks
S=$HOME/mutwork/head; cd $S
IN=custom_components/heatpump_optimizer/inputs.py; RM=custom_components/heatpump_optimizer/rooms.py
cp $IN /tmp/in.orig 2>/dev/null; cp $IN $HOME/mutwork/in.orig; cp $RM $HOME/mutwork/rm.orig; cp tests/features.py $HOME/mutwork/new_features.py
MARK='R.section("#3616 R11-OUTSIDE-ROOMS-P1'
run() { # $1 features file label
  cp $HOME/mutwork/$1 tests/features.py
  PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --emit-prelude $HOME/mutwork/P "$MARK" >/dev/null 2>&1
  out=$(PYTHONPATH=tests/hastub OPENBLAS_NUM_THREADS=1 timeout 900 python3 tools/audit/seat/features_block.py --prelude "import asyncio as _asyncio" --prelude "exec(open(\"$HOME/mutwork/P\").read())" "$MARK" 2>&1); rc=$?
  echo "  [$1] rc=$rc $(echo "$out" | grep -E 'FEATURES BLOCK|^FAIL|Error' | head -4 | tr '\n' '|')"
}
mut() { # name file old new
  echo "== $1"
  python3 - "$2" "$3" "$4" <<'PY'
import sys; p,o,n=sys.argv[1:]; s=open(p).read(); assert s.count(o)==1,(p,o); open(p,'w').write(s.replace(o,n))
PY
  run old_features.py; run new_features.py
  cp $HOME/mutwork/in.orig $IN; cp $HOME/mutwork/rm.orig $RM
}
cp $HOME/mutwork/old/features.py $HOME/mutwork/old_features.py
echo "== unmutated"; run old_features.py; run new_features.py
mut scaled_min $IN 'min(max(float(scale), STALENESS_SCALE_MIN), STALENESS_SCALE_MAX)' 'max(float(scale), STALENESS_SCALE_MIN)'
mut scaled_max $IN 'min(max(float(scale), STALENESS_SCALE_MIN), STALENESS_SCALE_MAX)' 'min(float(scale), STALENESS_SCALE_MAX)'
mut margins_clip $RM 'np.clip(np.asarray(base, dtype=float)[:n_steps], 0.0, None)' 'np.asarray(base, dtype=float)[:n_steps]'
mut resolve_floor $RM 'min(max(worst[0] - (target_c - house_c), 0.0), ROOM_LIFT_CAP_C)' 'min(worst[0] - (target_c - house_c), ROOM_LIFT_CAP_C)'
mut resolve_cap $RM 'min(max(worst[0] - (target_c - house_c), 0.0), ROOM_LIFT_CAP_C)' 'max(worst[0] - (target_c - house_c), 0.0)'
cp $HOME/mutwork/new_features.py tests/features.py
cmp $IN <(cd /home/user/heatpump_optimizer && git show 815ebab2a5:$IN) && cmp $RM <(cd /home/user/heatpump_optimizer && git show 815ebab2a5:$RM) && echo RESTORED
echo MUT5_DONE
