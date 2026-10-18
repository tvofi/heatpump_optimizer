#!/bin/bash
# review-2401 targeted mutants: M0 and M1 (shapes never forms a class), root passed as $1
export PATH=$HOME/.local/state/hpo/bin:$PATH
R=$1; E=$R/evidence; cd $R/mut
IDS=a3_shape_copies_control,a3_shape_copies_fix,a3_shape_copies_null,a3_shape_copies_respelled_control,rt_45_shape_private_copy,a3_hub_event_write_control,a3_hub_event_write_fix,rt_20b_hub_event_pkg_wrap
(echo "M0 head=$(git rev-parse HEAD)"; nice -n 10 env PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only $IDS --jobs 2; echo "exit=$?") > $E/mut_M0.txt 2>&1
python3 - <<'P'
p='tools/audit/archscore/metrics/shapes.py'; s=open(p).read()
old="if len(v) > 1), key="; assert old in s; open(p,'w').write(s.replace(old,"if len(v) > 999), key=",1))
P
(echo "M1 head=$(git rev-parse HEAD)"; git diff --stat; nice -n 10 env PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only a3_shape_copies_control,a3_shape_copies_fix,a3_shape_copies_null --jobs 2; echo "exit=$?") > $E/mut_M1.txt 2>&1
git checkout -- .; git status --porcelain; echo DONE
