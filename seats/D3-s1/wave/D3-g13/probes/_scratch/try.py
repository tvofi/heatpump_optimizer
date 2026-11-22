exec(open('/tmp/claude-0/-home-user-heatpump-optimizer/25370d85-7c12-5d31-9bdf-080232e3fc11/scratchpad/preamble.py').read().replace('ROOT = repo_root(__file__)','ROOT = Path.cwd()'))
exec(open('/tmp/claude-0/-home-user-heatpump-optimizer/25370d85-7c12-5d31-9bdf-080232e3fc11/scratchpad/dhw_common.py').read())
F = DhwPlanner._apply_dhw_min_run
muts = {
 '597d': ("weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]", "weak = np.where((plan > 1e-6) & (plan <= min_run_power))[0]"),
 'df4d': ("weak = np.where((plan > 1e-6) & (plan < min_run_power))[0]", "weak = np.where((plan >= 1e-6) & (plan < min_run_power))[0]"),
 '7224': ("unchanged: np.ndarray = np.clip(plan, 0.0, p_dhw_max)", "unchanged: np.ndarray = (plan)"),
 '49dc': ("run_power = min(min_run_power, p_dhw_max)", "run_power = (min_run_power)"),
 '1117': ("if bool(np.all(joint_temps <= joint_limit + 1e-9)):", "if False:"),
 'af8d': ("if bool(np.all(joint_temps <= joint_limit + 1e-9)):", "if bool(np.all(joint_temps < joint_limit + 1e-9)):"),
}
import time as _t
for k,(o,n) in muts.items():
    t=_t.time(); M = mutated(dhw_planner, F, o, n)
    mv, tot = sweep(M)
    print(k, len(mv), tot, mv[:3], round(_t.time()-t,1))
