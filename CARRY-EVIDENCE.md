# R11-SEAM-kernel-step carry 0: m6_restore.py re-run

Carry (roster): pump_arbiter.py is shared with R11-SEAM-actuation-release with no edge; the second of the two to merge re-runs the finder's restore harness (design/R11-SEAM-actuation-release section 6: dev/audit/rounds/round11/D16/s3/m6_restore.py).

The partner is R11-SEAM-actuation-release (#3812, open), not R11-CARRY-DRAWMAP (#3737). R11-SEAM-kernel-step (#3728, merge 4ebd430fbf) merged first, so the closing re-run falls to #3812 at its merge.

Command, from the tree root of each commit:
    PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D16/s3/m6_restore.py
(local overlay: venv-ci lives at ~/.local/state/hpo/venv-ci on this host, not $HOME/venv-ci or /opt/hpo/venv-ci.)

Runs:
- origin/main 49cb3207a997b4f38c11cb2f1adf4b8d613e06ea (after #3728 and #3737)
- 6fdc15354f0f6f4613370fdabe4bd82adbadc087 (first parent of #3728's merge, before kernel-step)

The two outputs are byte-identical (205 lines, diff empty), and each matches the docstring's expected baseline exactly:
unrestored_off=5, unload=4, remove=4, duty_change=7, off_modbus=4, off_disinfecting=6, unload_disinfecting=5,
remove_disinfecting=5, duty_change_disinfecting=8; restored_more_than_once_*=0; every null_unrestored_*=0.

Summary lines at origin/main:
RESULT unrestored_off=5 entities
RESULT unrestored_off_arbiter_slots=1 entities
RESULT unrestored_off_unregistered=4 entities
RESULT written_off=10 entities
RESULT restored_more_than_once_off=0 entities
RESULT unrestored_unload=4 entities
RESULT unrestored_unload_arbiter_slots=0 entities
RESULT unrestored_unload_unregistered=4 entities
RESULT written_unload=10 entities
RESULT restored_more_than_once_unload=0 entities
RESULT unrestored_remove=4 entities
RESULT unrestored_remove_arbiter_slots=0 entities
RESULT unrestored_remove_unregistered=4 entities
RESULT written_remove=10 entities
RESULT restored_more_than_once_remove=0 entities
RESULT unrestored_duty_change=7 entities
RESULT unrestored_duty_change_arbiter_slots=0 entities
RESULT unrestored_duty_change_unregistered=7 entities
RESULT written_duty_change=10 entities
RESULT restored_more_than_once_duty_change=0 entities
RESULT unrestored_off_modbus=4 entities
RESULT unrestored_off_modbus_arbiter_slots=1 entities
RESULT unrestored_off_modbus_unregistered=3 entities
RESULT written_off_modbus=10 entities
RESULT restored_more_than_once_off_modbus=0 entities
RESULT unrestored_off_disinfecting=6 entities
RESULT unrestored_off_disinfecting_arbiter_slots=2 entities
RESULT unrestored_off_disinfecting_unregistered=4 entities
RESULT written_off_disinfecting=11 entities
RESULT restored_more_than_once_off_disinfecting=0 entities
RESULT unrestored_unload_disinfecting=5 entities
RESULT unrestored_unload_disinfecting_arbiter_slots=1 entities
RESULT unrestored_unload_disinfecting_unregistered=4 entities
RESULT written_unload_disinfecting=11 entities
RESULT restored_more_than_once_unload_disinfecting=0 entities
RESULT unrestored_remove_disinfecting=5 entities
RESULT unrestored_remove_disinfecting_arbiter_slots=1 entities
RESULT unrestored_remove_disinfecting_unregistered=4 entities
RESULT written_remove_disinfecting=11 entities
RESULT restored_more_than_once_remove_disinfecting=0 entities
RESULT unrestored_duty_change_disinfecting=8 entities
RESULT unrestored_duty_change_disinfecting_arbiter_slots=1 entities
RESULT unrestored_duty_change_disinfecting_unregistered=7 entities
RESULT written_duty_change_disinfecting=11 entities
RESULT restored_more_than_once_duty_change_disinfecting=0 entities
RESULT null_unrestored_off=0 entities
RESULT null_written_off=9 entities
RESULT null_unrestored_unload=0 entities
RESULT null_written_unload=9 entities
RESULT null_unrestored_remove=0 entities
RESULT null_written_remove=9 entities
RESULT null_unrestored_duty_change=0 entities
RESULT null_written_duty_change=9 entities
RESULT null_unrestored_off_modbus=0 entities
RESULT null_written_off_modbus=9 entities
RESULT null_unrestored_off_disinfecting=0 entities
RESULT null_written_off_disinfecting=9 entities
RESULT null_unrestored_unload_disinfecting=0 entities
RESULT null_written_unload_disinfecting=9 entities
RESULT null_unrestored_remove_disinfecting=0 entities
RESULT null_written_remove_disinfecting=9 entities
RESULT null_unrestored_duty_change_disinfecting=0 entities
RESULT null_written_duty_change_disinfecting=9 entities
