# mutrun.sh <worktree> <outdir>: apply each mutant, run three blocks, restore
WT=$1; OUT=$2; mkdir -p $OUT; cd $WT; export PYTHONPATH=tests/hastub
python3 - <<PY > $OUT/ids
import sys; sys.path.insert(0, "$HOME"); from mutants import MUTANTS
for i,m in enumerate(MUTANTS): print(i)
PY
for i in $(cat $OUT/ids); do
  git checkout -q -- custom_components
  python3 - <<PY || { echo "M$i APPLY-FAILED" >> $OUT/summary; continue; }
import sys; sys.path.insert(0, "$HOME"); from mutants import MUTANTS
mid,f,o,n = MUTANTS[$i]; s=open(f).read(); c=s.count(o)
assert c==1, (mid, c); open(f,"w").write(s.replace(o,n)); print(mid, file=open("$OUT/name$i","w"))
PY
  name=$(cat $OUT/name$i)
  timeout 900 python3 tools/audit/seat/features_block.py "# R11-SEAM-actuation-release (ADR-004" "# R10-HOTFIX-FLOW-SETPOINT-STUCK (tvofi, 2026-11-13" > $OUT/m$i.section 2>&1
  timeout 600 python3 tools/audit/seat/features_block.py --prelude 'exec(open("/root/preA.py").read())' 'R.section("°F set-points' '# R10-PUMP-MODEL -- one hot-water lift law' > $OUT/m$i.blockA 2>&1
  timeout 600 python3 tools/audit/seat/features_block.py --prelude 'exec(open("/root/preB.py").read())' 'R.section("supply switch: minimum run and pause' 'R.section("duty-switch restart learning, part A' > $OUT/m$i.blockB 2>&1
  r=""; for b in section blockA blockB; do r="$r $b:$(grep -hoE 'ALL [0-9]+ FEATURES BLOCK PASSED|[0-9]+ of [0-9]+ FEATURES BLOCK FAILED|[A-Za-z]+Error' $OUT/m$i.$b | tail -1 | tr ' ' '_')"; done
  case "$r" in *FAILED*|*Error*) v=KILLED;; *) v=SURVIVED;; esac
  echo "$name $v $r" >> $OUT/summary
done
git checkout -q -- custom_components
echo MUTRUN-DONE; cat $OUT/summary
