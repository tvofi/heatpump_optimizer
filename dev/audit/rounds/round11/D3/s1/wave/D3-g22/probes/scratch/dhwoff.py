import sys; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g22/probes")
import g22_rig as rig
from g22_rig import np
opt, run = rig.january()
opt.model.params.dhw_enabled = False
r = run(dhw_blocked=True)
print("dhw off: req", None if opt._dhw_requirement is None else len(opt._dhw_requirement), "traj", type(r.dhw_temp_trajectory), len(r.dhw_temp_trajectory or []), {k:v for k,v in r.predictive_info.items() if 'breach' in k})
opt.model.params.dhw_enabled = True
from g22_rig import ThermalState
for t0 in (55.0, 60.0, 65.0):
    import profiles
    opt2, run2 = rig.january()
    # hot tank
    import types
    r = None
    from profiles import solve_inputs
    st = ThermalState(room_temperature=21.0, outdoor_temperature=-12.0, dhw_temperature=t0)
    n = opt2.config.n_steps
    from datetime import datetime
    start = datetime(2026,1,15,0,0)
    prices = np.asarray(profiles.prices("winter_typical", start))[:n]
    t, w, rn, s = profiles.weather("winter_cold", start)
    r = opt2.optimize(inputs=solve_inputs(initial_state=st, prices=prices, outdoor_temps=t[:n], wind_speeds=w[:n], precipitation=rn[:n], solar_radiation=s[:n], start_time=start, dhw_blocked=True))
    req = np.asarray(opt2._dhw_requirement, float); tr = np.asarray(r.dhw_temp_trajectory, float)[1:]
    print(t0, r.predictive_info.get("dhw_floor_breach_c"), "max(req-planned)", float(np.max(req-tr)), "req range", req.min(), req.max())
