import sys, time, random, math; sys.path.insert(0, "dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes")
import sysid_probe_common as c
L2223 = "        if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0):"
m = c.load(); tap = c.load_tap(L2223, "tau"); t=time.time()
rng = random.Random(1); n=0; near=[]
while time.time()-t < 100:
    cap = rng.uniform(2.0, 4.0); q = rng.uniform(2.0, 6.0)
    mk = lambda ua: c.plant_samples(m, ua=ua, cap=cap, gains=0.0, q=q)
    ua = cap/200.0
    for _ in range(6):
        v,_r = c.tapped(tap, mk(ua)); n+=1
        if v is None: break
        ua = ua * v/200.0
    if v is None: continue
    near.append(abs(v-200))
    for k in range(300):
        x = ua*(1+rng.uniform(-1e-12,1e-12)); v, r = c.tapped(tap, mk(x)); n+=1
        if v == 200.0:
            print("HIT", repr(x), repr(cap), repr(q), n, r.reason, round(time.time()-t)); sys.exit()
print("nohit", n, sorted(near)[:5])
