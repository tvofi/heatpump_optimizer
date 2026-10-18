#!/bin/sh
# reviewer's own runner: M0 then M10 (drop_noops not called), restored with git checkout
cd /tmp/seat/rev2373/head
export PYTHONPATH=tests/hastub
python3 tools/audit/archscore/calibrate.py --only a3_card_clone_copies_control,a3_card_clone_copies_fix,a3_card_clone_copies_null,a3_card_dead_definitions_control,a3_card_dead_definitions_fix,a3_card_dead_definitions_null,a3_literal_clone_copies_control,a3_literal_clone_copies_fix,a3_literal_clone_copies_null,rt_42_literal_respelled,rt_42b_literal_module_constant,rt_42c_literal_keyword_args,rt_42d_literal_module_attr,rt_43_literal_local_hop,rt_44_card_rename_locals,rt_44b_card_noop_split,rt_44c_card_empty_statement > ../ev/r4_calib_M0.txt 2>&1
sed -i 's/^        body = drop_noops(body)$/        body = body  # M10/' tools/audit/archscore/metrics/card.py
git diff --stat > ../ev/r4_mut_M10.diffstat
python3 tools/audit/archscore/calibrate.py --only a3_card_clone_copies_control,a3_card_clone_copies_fix,a3_card_clone_copies_null,a3_card_dead_definitions_control,a3_card_dead_definitions_fix,a3_card_dead_definitions_null,a3_literal_clone_copies_control,a3_literal_clone_copies_fix,a3_literal_clone_copies_null,rt_42_literal_respelled,rt_42b_literal_module_constant,rt_42c_literal_keyword_args,rt_42d_literal_module_attr,rt_43_literal_local_hop,rt_44_card_rename_locals,rt_44b_card_noop_split,rt_44c_card_empty_statement > ../ev/r4_mut_M10.txt 2>&1
git checkout -- tools/audit/archscore/metrics/card.py
git status --short tools > ../ev/r4_restored_status.txt
