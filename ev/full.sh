#!/bin/sh
# $1 = mutant id; full tests/features.py on its own copy with that mutant applied
S=/tmp/claude-0/-home-user-heatpump-optimizer/a47c5907-eede-5a2a-adfb-38c93e72e427/scratchpad
D=$S/full_$1; rm -rf $D; mkdir $D; (cd $S/head && git archive HEAD | tar -x -C $D)
python3 - "$D" "$1" <<'PY'
import sys, runpy, pathlib
sys.argv=[ "x", sys.argv[1] ]
PY
python3 -c "
import sys,importlib.util
spec=importlib.util.spec_from_file_location('m','$S/probes/mut.py')
" 
cd $D && python3 $S/probes/apply.py $D $1 && PYTHONPATH=tests/hastub:custom_components:tests timeout 5400 python3 tests/features.py > $S/ev/full_$1.txt 2>&1; echo "exit $?" >> $S/ev/full_$1.txt
