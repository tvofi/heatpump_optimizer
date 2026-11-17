"""Reviewer's instrument (not the finder's): does either half of runs.commit's
tie break alone change a mask? Loads runs.py from the tree in argv[1] three
times (as it stands, the not-asked half off, the asked half off) and compares
the masks on generated plans, realizable and not, priced and not."""
import sys, importlib, types
import numpy as np
sys.path.insert(0, sys.argv[1] + "/tests/hastub"); sys.path.insert(0, sys.argv[1] + "/custom_components")
import heatpump_optimizer.runs as runs
src = open(runs.__file__).read()
A = "price[k] * level[k] * dt + _TIE_BREAK * (not asked)),\n"
B = "            (-q[k] * dt, _TIE_BREAK * asked),\n"
assert src.count(A) == 1 and src.count(B) == 1
def variant(s):
    m = types.ModuleType("heatpump_optimizer.runs_variant"); m.__package__ = "heatpump_optimizer"; m.__file__ = runs.__file__
    exec(compile(s, runs.__file__, "exec"), m.__dict__); return m
arms = {"not-asked half off": variant(src.replace(A, A.replace("_TIE_BREAK", "0.0"))),
        "asked half off": variant(src.replace(B, B.replace("_TIE_BREAK", "0.0"))),
        "both off": variant(src.replace("_TIE_BREAK = 1e-9\n", "_TIE_BREAK = 0.0\n"))}
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
diff = {k: {} for k in arms}; total = {}
for i in range(int(sys.argv[3]) if len(sys.argv) > 3 else 1500):
    n = int(rng.integers(6, 97)); f = float(rng.choice([0.53, 1.1])); dt = float(rng.choice([0.25, 1 / 12]))
    real = bool(i % 2)
    q = np.where(rng.random(n) < 0.5, 0.0, rng.uniform(f if real else 0.05, 3.0, n))
    lengths = (1, 1) if i % 3 else (int(rng.integers(1, 4)), int(rng.integers(1, 4)))
    for name, p, start in (("nothing priced", 0.0, 0.0), ("flat price", 0.2, 0.0), ("start priced", 0.0, 0.25),
                           ("varying price", rng.uniform(0.05, 0.4, n), 0.1)):
        key = ("realizable" if real else "not realizable", name, "one-step lengths" if lengths == (1, 1) else "longer lengths")
        for band in runs.BANDS:
            total[key] = total.get(key, 0) + 1
            kw = dict(dt=dt, running=bool(i % 4 < 2), lengths=lengths)
            want = runs.commit(q, p, f, 3.0, start, band, **kw)[0]
            for arm, mod in arms.items():
                diff[arm][key] = diff[arm].get(key, 0) + (not np.array_equal(mod.commit(q, p, f, 3.0, start, band, **kw)[0], want))
for arm in arms:
    print("RESULT", arm, {" / ".join(k): f"{v} of {total[k]}" for k, v in sorted(diff[arm].items())})
