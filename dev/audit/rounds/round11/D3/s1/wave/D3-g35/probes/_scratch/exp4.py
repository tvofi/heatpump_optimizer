import sys; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
L2237 = "            and abs(drift_c_per_h) < self.config.sensor_drift_prior_c_per_h"
NEW = "            and abs(drift_c_per_h) <= self.config.sensor_drift_prior_c_per_h"
m = c.load(); mm = c.load(L2237, NEW); tap = c.load_tap("        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):", "drift_c_per_h")
for kw in [dict(drift=0.01, start_steady=False, t0=1.3), dict(drift=0.01, start_steady=False, t0=1.0), dict(drift=0.005, start_steady=False, t0=1.3)]:
    p = 0.02
    for it in range(80):
        cfg = c.load and m.SysIdConfig(enabled=True, sensor_drift_prior_c_per_h=p)
        d, r = c.tapped(tap, c.plant_samples(m, **kw), tap.SysIdConfig(enabled=True, sensor_drift_prior_c_per_h=p))
        if d is None: print("none", r.reason); break
        if abs(d) == p:
            s = c.plant_samples(m, **kw)
            print("FIXED", kw, it, p)
            print(" base", c.fmt(c.run(m, s, m.SysIdConfig(enabled=True, sensor_drift_prior_c_per_h=p))))
            print(" mut ", c.fmt(c.run(mm, s, mm.SysIdConfig(enabled=True, sensor_drift_prior_c_per_h=p))))
            break
        p = abs(d)
    else: print("nofix", kw, p, d)
