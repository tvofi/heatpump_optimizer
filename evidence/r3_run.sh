#!/bin/bash
# review-2373 round 3: finder harness, calibration subset, targeted mutants M13/M15 (root passed as $1)
export PATH=$HOME/.local/state/hpo/bin:$PATH
R=$1; E=$R/evidence
IDS=a3_card_clone_copies_control,a3_card_clone_copies_fix,a3_card_clone_copies_null,a3_card_dead_definitions_control,a3_card_dead_definitions_fix,a3_card_dead_definitions_null,a3_literal_clone_copies_control,a3_literal_clone_copies_fix,a3_literal_clone_copies_null,rt_42_literal_respelled,rt_42b_literal_module_constant,rt_42c_literal_keyword_args,rt_42d_literal_module_attr,rt_43_literal_local_hop,rt_44_card_rename_locals,rt_44b_card_noop_split,rt_44c_card_empty_statement
cd $R/head3; H=dev/audit/rounds/round10/D7/arch2-s5; P=$H/patches
(nice -n 10 env PYTHONPATH=tests/hastub python3 $H/arch_delta.py --base 9061fbd3d $P/F1_wizard_widgets_from_registry.patch; echo "exit=$? head=$(git rev-parse HEAD)") > $E/r3_finder_F1.txt 2>&1
(nice -n 10 env PYTHONPATH=tests/hastub python3 $H/arch_delta.py --base 9061fbd3d $P/C1_textwidth_owner.patch $P/C2_setup_slot_deep_link.patch $P/C3_reading_rules.patch $P/C4_empty_state_and_finite_owner.patch; echo "exit=$? head=$(git rev-parse HEAD)") > $E/r3_finder_C.txt 2>&1
(echo "head=$(git rev-parse HEAD)"; nice -n 10 env PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only $IDS --jobs 2; echo "exit=$?") > $E/r3_calib_M0.txt 2>&1
cd $R/mut3
python3 - <<'P'
p='tools/audit/archscore/metrics/literal_clones.py'; s=open(p).read()
old="        v = self.attr(n) if self.attr is not None else None\n"
assert old in s; open(p,'w').write(s.replace(old,"        v = None\n",1))
P
(echo "M13 head=$(git rev-parse HEAD)"; git diff --stat; nice -n 10 env PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only rt_42d_literal_module_attr,rt_42b_literal_module_constant,a3_literal_clone_copies_fix --jobs 2; echo "exit=$?") > $E/r3_mut_M13.txt 2>&1
git checkout -- .
python3 - <<'P'
p='tools/audit/archscore/metrics/card.py'; s=open(p).read()
old='(run or out[-1:] != ["}"])'
assert old in s; open(p,'w').write(s.replace(old,'run',1))
P
(echo "M15 head=$(git rev-parse HEAD)"; git diff --stat; nice -n 10 env PYTHONPATH=tests/hastub python3 tools/audit/archscore/calibrate.py --only rt_44c_card_empty_statement,rt_44b_card_noop_split,a3_card_clone_copies_fix --jobs 2; echo "exit=$?") > $E/r3_mut_M15.txt 2>&1
git checkout -- .; git status --porcelain
echo R3DONE
