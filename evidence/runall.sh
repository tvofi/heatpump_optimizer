M=/root/ev/mut.sh
$M base
$M M1-planner96-GUARD_OFF custom_components/heatpump_optimizer/dhw_planner.py 96 'if not len(hours_mod):' 'if False:'
$M M2-planner99-CMP_BOUND custom_components/heatpump_optimizer/dhw_planner.py 99 'np.diff(hours_mod) < 0.0' 'np.diff(hours_mod) <= 0.0'
$M M3-sysid2504-GUARD_OFF custom_components/heatpump_optimizer/sysid.py 2504 'if ident.active:' 'if False:'
$M M4-sensor545-RETURN_DEL custom_components/heatpump_optimizer/sensor.py 545 'return None' 'pass'
$M M5-schedule566-CMP_BOUND custom_components/heatpump_optimizer/dhw_schedule.py 566 'if start > h]' 'if start >= h]'
$M M0-null-comment custom_components/heatpump_optimizer/dhw_planner.py 96 'if not len(hours_mod):' 'if not len(hours_mod):  # null'
echo ALLDONE
