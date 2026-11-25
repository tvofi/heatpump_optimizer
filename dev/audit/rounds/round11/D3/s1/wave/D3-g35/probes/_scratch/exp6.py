import sys, time; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
L2208 = "        if drift_c_per_h is not None and a.shape[1] >= 4 and excursion > 1e-9:"
L2223 = "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):"
m = c.load(); t=time.time()
tap = c.load_tap(L2208, "excursion")
for q in [0.0, 1e-12, 1e-10, 1e-9, 3e-9, 1e-8]:
    v, r = c.tapped(tap, c.plant_samples(m, q=q)); print("q", q, v, r.reason)
for g in [0.0, 1e-9]:
    v, r = c.tapped(tap, c.plant_samples(m, q=0.0, gains=g)); print("g", g, v, r.reason)
x, s, tried = c.multi_hunt(L2223, "tau", lambda x, s: c.plant_samples(m, ua=x, cap=s[1], gains=0.0, q=s[0]), 0.0145*1, 0.0155, 200.0, [(3.0+0.1*i, 3.0) for i in range(20)])
print("tau200 cap3", x, s, tried, time.time()-t)
for cap in [2.0, 4.0]:
    x, s, tried = c.multi_hunt(L2223, "tau", lambda x, s: c.plant_samples(m, ua=x, cap=s[1], gains=0.0, q=s[0]), cap/206, cap/194, 200.0, [(3.0+0.1*i, cap) for i in range(30)])
    print("tau200 cap", cap, x, s, tried, time.time()-t)
