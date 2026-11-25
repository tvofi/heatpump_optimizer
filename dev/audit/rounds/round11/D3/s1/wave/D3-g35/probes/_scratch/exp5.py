import sys, time; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
L2154 = "            if not (-0.5 <= gains_kw <= 2.0):"
L2223 = "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):"
L2246 = "                    if ua_ss > 0.0 and abs(ua_ss - ua) / ua > 0.10:"
m = c.load(); t = time.time()
def H(name, line, expr, mk, lo, hi, target, qs):
    tap = c.load_tap(line, expr); tot = 0
    for q in qs:
        f = lambda x: c.tapped(tap, mk(x, q))[0]
        hit, tried, best = c.hunt(f, lo, hi, target, scan=150); tot += tried
        if hit is not None:
            print(name, "HIT q", q, "x", repr(hit), "tried", tot, round(time.time()-t,1)); return
    print(name, "nohit tried", tot, round(time.time()-t,1))
qs = [3.0 + 0.05*i for i in range(30)]
H("g2", L2154, "gains_kw", lambda x, q: c.plant_samples(m, gains=x, q=q), 1.9, 2.1, 2.0, qs)
H("r.10", L2246, "abs(ua_ss - ua) / ua", lambda x, q: c.plant_samples(m, start_steady=False, t0=x, q=q), 1.30, 1.40, 0.10, qs)
H("ua.01", L2223, "ua", lambda x, q: c.plant_samples(m, ua=x, cap=1.0, gains=0.0, q=q), 0.009, 0.011, 0.01, qs)
