import sys, time; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
L2154 = "            if not (-0.5 <= gains_kw <= 2.0):"
L2223 = "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):"
L2208 = "        if drift_c_per_h is not None and a.shape[1] >= 4 and excursion > 1e-9:"
L2244 = "                if abs(den) > 1e-6:"
L2246 = "                    if ua_ss > 0.0 and abs(ua_ss - ua) / ua > 0.10:"
m = c.load()
t=time.time()
def H(name, line, expr, mk, lo, hi, target):
    tap = c.load_tap(line, expr)
    f = lambda x: c.tapped(tap, mk(x))[0]
    print(name, "lo", f(lo), "hi", f(hi))
    hit, tried, best = c.hunt(f, lo, hi, target, scan=500)
    print(name, "hit", hit, "tried", tried, "best", best, round(time.time()-t,1)); sys.stdout.flush()
H("g2", L2154, "gains_kw", lambda x: c.plant_samples(m, gains=x), 1.9, 2.1, 2.0)
H("g-.5", L2154, "gains_kw", lambda x: c.plant_samples(m, gains=x), -0.6, -0.4, -0.5)
H("tau200", L2223, "tau", lambda x: c.plant_samples(m, ua=x, cap=3.0, gains=0.0), 0.0145, 0.0155, 200.0)
H("ua.01", L2223, "ua", lambda x: c.plant_samples(m, ua=x, cap=1.0, gains=0.0), 0.009, 0.011, 0.01)
H("ua5", L2223, "ua", lambda x: c.plant_samples(m, ua=x, cap=10.0, gains=0.0, q=40.0), 4.9, 5.1, 5.0)
H("tau.1", L2223, "tau", lambda x: c.plant_samples(m, ua=x, cap=0.3, gains=0.0, cadence_min=1.0), 2.9, 3.1, 0.1)
H("r.10", L2246, "abs(ua_ss - ua) / ua", lambda x: c.plant_samples(m, start_steady=False, t0=x), 1.30, 1.40, 0.10)
for x in [1e-6]:
    print("den", c.tapped(c.load_tap(L2244, "den"), c.plant_samples(m, last_settle_room=x)))
for q in [4.0, 0.1, 1e-3, 1e-5, 1e-7]:
    print("exc", q, c.tapped(c.load_tap(L2208, "excursion"), c.plant_samples(m, q=q))[0], c.fmt(c.run(m, c.plant_samples(m, q=q))))
