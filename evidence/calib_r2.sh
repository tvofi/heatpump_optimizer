#!/bin/bash
export PATH=$HOME/.local/state/hpo/bin:$PATH
S=/Users/timmalmstrom/hpo-seats/r10s3/review-2373
cd $S/head2
IDS=a3_card_clone_copies_control,a3_card_clone_copies_fix,a3_card_clone_copies_null,a3_card_dead_definitions_control,a3_card_dead_definitions_fix,a3_card_dead_definitions_null,a3_literal_clone_copies_control,a3_literal_clone_copies_fix,a3_literal_clone_copies_null,rt_42_literal_respelled,rt_42b_literal_module_constant,rt_42c_literal_keyword_args,rt_43_literal_local_hop,rt_44_card_rename_locals,rt_44b_card_noop_split
echo "head=$(git rev-parse HEAD)" > $S/evidence/r2_calib_full.txt
PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only $IDS --jobs 3 >> $S/evidence/r2_calib_full.txt 2>&1; echo "exit=$?" >> $S/evidence/r2_calib_full.txt
