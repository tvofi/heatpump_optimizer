"""Reviewer's own attack rows for #3662 (fix review, cloud seat): self-setting
pumps whose draw is independent of the asks but NOT a stationary sinusoid --
random walk, heavy tails, step change, burst duty -- plus one heat-led row with
a slowly drifting true scale. Uses the head harness's run(); argv[1] = NPROC."""
import math, random, sys
from multiprocessing import Pool
sys.path.insert(0, "dev/audit/harnesses")
import cop_duty_floor as h

N = 672

def walk(seed, kw=2.2, sd=0.04):
    r = random.Random(seed); x = 0.0; out = []
    for t in range(N):
        x = max(-0.5, min(0.5, x + r.gauss(0, sd)))
        out.append((1.5 * r.uniform(0.98, 1.02), kw * math.exp(x)))
    return out

def heavy(seed, kw=2.2, sd=0.35):
    r = random.Random(seed)
    return [(1.5 * r.uniform(0.98, 1.02), max(1.2, min(3.9, kw * math.exp(r.gauss(0, sd))))) for _ in range(N)]

def stepchg(seed, kw=2.2):
    r = random.Random(seed); at = r.randrange(100, 500)
    return [(1.5 * r.uniform(0.98, 1.02), kw * (1.4 if t >= at else 1.0) * r.uniform(0.97, 1.03)) for t in range(N)]

def burst(seed, kw=2.2):
    r = random.Random(seed); out = []; hi = False
    for t in range(N):
        if r.random() < 0.2: hi = not hi
        out.append((1.5 * r.uniform(0.98, 1.02), kw * (1.35 if hi else 0.8) * r.uniform(0.97, 1.03)))
    return out

def job(a):
    kind, seed = a
    st = {}
    if kind == "heatled_drift":
        r = random.Random(seed)
        pairs = h.flat(N, seed=seed)
        tr = [0.8]
        for _ in range(N): tr.append(max(0.55, min(1.2, tr[-1] * math.exp(r.gauss(0, 0.01)))))
        got = h.run(pairs, p_max=4.0, true=lambda t: tr[t], noise=0.05, stats=st, noise_seed=seed)
    else:
        got = h.run({"walk": walk, "heavy": heavy, "step": stepchg, "burst": burst}[kind](seed), p_max=4.0, stats=st)
    return f"ATTACK {kind} s{seed} {got} verdict={st.get('verdict')} lo={st.get('lowest')} hi={st.get('highest')} probes={st.get('probes')} band={st.get('band')}"

if __name__ == "__main__":
    jobs = [(k, s) for k in ("walk", "heavy", "step", "burst", "heatled_drift") for s in range(1, 21)]
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 2) as p:
        for line in p.imap(job, jobs):
            print(line, flush=True)
