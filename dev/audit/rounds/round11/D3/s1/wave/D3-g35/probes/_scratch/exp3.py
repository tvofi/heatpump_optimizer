import sys, time, math; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
L2237 = "            and abs(drift_c_per_h) < self.config.sensor_drift_prior_c_per_h"
L2208 = "        if drift_c_per_h is not None and a.shape[1] >= 4 and excursion > 1e-9:"
L2223 = "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):"
m = c.load()
# a5b0 fixed point
for kw in [dict(drift=0.01, start_steady=False, t0=1.3), dict(drift=0.01), dict(drift=0.019, start_steady=False, t0=1.3)]:
    p = 0.02
    for it in range(60):
        r = c.run(m, c.plant_samples(m, **kw), m.SysIdConfig(enabled=True, sensor_drift_prior_c_per_h=p))
        d = r.sensor_drift_c_per_h
        if d is None: print("none", r.reason); break
        if abs(d) == p: print("FIXED", kw, it, p, c.fmt(r)); break
        p = abs(d)
    else:
        print("nofix", kw, p, d, c.fmt(r))
# excursion
tap = c.load_tap(L2208, "excursion")
for q in [1e-9, 2e-9, 5e-9]:
    v, r = c.tapped(tap, c.plant_samples(m, q=q))
    print("exc", q, v, c.fmt(r))
tap = c.load_tap(L2223, "tau")
for x in [3.0, 3.5, 4.0]:
    print("tau", x, c.tapped(tap, c.plant_samples(m, ua=x, cap=0.3, gains=0.0, cadence_min=1.0))[0])
