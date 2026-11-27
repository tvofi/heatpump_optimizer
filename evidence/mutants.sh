#!/bin/bash
cd /tmp/hpo-rev-3933/wt
S='# --- R10-DRAW-MAP-EVIDENCE part B (design'; E='R.section("Room history and the identifiability report")'
C=custom_components/heatpump_optimizer
run() { # name file line old new
  name=$1 f=$2 ln=$3 old=$4 new=$5
  cp "$f" /tmp/hpo-rev-3933/orig.bak
  python3 - "$f" "$ln" "$old" "$new" <<'PY'
import sys
f,ln,old,new=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
L=open(f).read().split("\n"); assert old in L[ln-1], L[ln-1]; L[ln-1]=L[ln-1].replace(old,new,1); open(f,"w").write("\n".join(L))
PY
  PYTHONPATH=tests/hastub timeout 900 python3 tools/audit/seat/features_block.py --prelude 'exec(open("/tmp/hpo-rev-3933/prelude.py").read())' "$S" "$E" > /tmp/hpo-rev-3933/ev/mut-$name.log 2>&1
  rc=$?
  cp /tmp/hpo-rev-3933/orig.bak "$f"
  echo "MUTANT $name rc=$rc fails=$(grep -c 'FAIL' /tmp/hpo-rev-3933/ev/mut-$name.log)"
}
run M1-fold-sweep-excl $C/draw_range.py 1070 'elif not sweep:' 'else:'
run M2-floor-release $C/pump_arbiter.py 1380 'held.sweep_floor_c = None' 'pass'
run M3-tank-cold $C/pump_arbiter.py 1491 'if _sweep_tank_cold(inp):' 'if False:'
run M4-dear-hour-end $C/sysid.py 1621 'if index and (price is None' 'if False and (price is None'
git status --porcelain
