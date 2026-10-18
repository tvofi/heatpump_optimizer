#!/bin/bash
export PATH=$HOME/.local/state/hpo/bin:$PATH
S=/Users/timmalmstrom/hpo-seats/r10s3/review-2373
side=$1
cd $S/head2
H=dev/audit/rounds/round10/D7/arch2-s5
P=$H/patches
PYTHONPATH=tests/hastub python3 $H/arch_delta.py --base 9061fbd3d $P/F1_wizard_widgets_from_registry.patch > $S/evidence/r2_finder_F1_head2.txt 2>&1; echo "exit=$?" >> $S/evidence/finder_F1_$side.txt
PYTHONPATH=tests/hastub python3 $H/arch_delta.py --base 9061fbd3d $P/C1_textwidth_owner.patch $P/C2_setup_slot_deep_link.patch $P/C3_reading_rules.patch $P/C4_empty_state_and_finite_owner.patch > $S/evidence/r2_finder_C_head2.txt 2>&1; echo "exit=$?" >> $S/evidence/finder_C_$side.txt
