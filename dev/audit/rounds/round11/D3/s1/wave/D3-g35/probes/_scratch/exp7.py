import sys, time, random; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
L2223 = "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):"
m = c.load(); tap = c.load_tap(L2223, "tau"); t=time.time()
rng = random.Random(0); n=0; vals=set()
while time.time()-t < 120:
    cap = rng.uniform(2.0, 4.0); q = rng.uniform(2.0, 6.0); cad = rng.choice([5.0, 10.0, 15.0])
    ua = cap/200.0 * (1 + rng.uniform(-3e-9, 3e-9))
    v, r = c.tapped(tap, c.plant_samples(m, ua=ua, cap=cap, gains=0.0, q=q, cadence_min=cad)); n+=1
    if v is not None: vals.add(round((v-200)/2.8e-14))
    if v == 200.0: print("HIT", repr(ua), repr(cap), repr(q), cad, n, r.reason); break
else: print("nohit", n)
print(sorted(vals)[:10], sorted(vals)[-10:], len(vals))
