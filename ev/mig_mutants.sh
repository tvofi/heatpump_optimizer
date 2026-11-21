# usage: mig_mutants.sh W ; runs the migration block of tests/entities.py at the head and under each mutant
W=$1; cd $W/wt; export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests/hastub:tests
F=custom_components/heatpump_optimizer/__init__.py
L='        data, options = placed(repaired_numbers(effective, repairs))'
run(){ echo "=== $1"; grep -cF "$2" $F; timeout 600 python3 $W/ev/mig_block_driver.py 2>&1 | grep -E 'FAIL|PASSED|FAILED|Error'; echo rc=${PIPESTATUS[0]}; git checkout -q $F; }
run head "$L"
python3 - "$F" <<'P'
import sys;p=sys.argv[1];s=open(p).read();s=s.replace("placed(repaired_numbers(effective, repairs))","placed(effective)",1);open(p,'w').write(s)
P
run "mR: repair dropped from the resolution, placed(effective)" "placed(effective)"
python3 - "$F" <<'P'
import sys;p=sys.argv[1];s=open(p).read();s=s.replace("data, options = placed(repaired_numbers(effective, repairs))","data, options = repaired_numbers(entry.data, repairs), repaired_numbers(entry.options, repairs)",1);open(p,'w').write(s)
P
run "mP: placement dropped, old per-side repair" "repaired_numbers(entry.data"
python3 - "$F" <<'P'
import sys;p=sys.argv[1];s=open(p).read();s=s.replace("effective = {**entry.data, **entry.options}","effective = {**entry.options, **entry.data}",1);open(p,'w').write(s)
P
run "mO: data over options in the effective mapping" "{**entry.options, **entry.data}"
git status --porcelain
