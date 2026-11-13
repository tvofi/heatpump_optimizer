#!/bin/bash
# reviewer's harness re-runs; $1 = worktree, $2 = label
cd "$1"; L=$2; O=$HOME/W/ev/harness; export PYTHONPATH=tests/hastub:tests:custom_components
run(){ n=$1; shift; "$@" > $O/${L}_$n.log 2>&1; echo "rc=$? ${L}_$n"; }
run residue_whatif python3 dev/audit/harnesses/r10_advisor_residue.py whatif
if [ "$L" = head ]; then
run residue_steadysign python3 dev/audit/harnesses/r10_advisor_residue.py steadysign
run bracket_peaks env PRICES=peaks python3 dev/audit/harnesses/r10_advisor_steady_bracket.py
run bracket_flat env PRICES=flat python3 dev/audit/harnesses/r10_advisor_steady_bracket.py
run bracket_spread2 env PRICES=spread2 python3 dev/audit/harnesses/r10_advisor_steady_bracket.py
run carrier_2_4 env AGE=2 STEP=4 python3 dev/audit/harnesses/r10_advisor_steady_carrier.py
run carrier_0_0 env AGE=0 STEP=0 python3 dev/audit/harnesses/r10_advisor_steady_carrier.py
run carrier_1_4 env AGE=1 STEP=4 python3 dev/audit/harnesses/r10_advisor_steady_carrier.py
for a in weekday fields pair pv; do run seams_$a python3 dev/audit/harnesses/r10_advisor_steady_seams.py $a; done
fi
echo ALLDONE $L
