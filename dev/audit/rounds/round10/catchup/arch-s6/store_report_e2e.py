#!/usr/bin/env python3
"""arch-s6 catch-up verifier, V2 for ARCH3-s6-P3: debugger.store_report end to end, two trees.

Different entry point from the finder's store_report_equiv.py (which re-states the old expressions
inside the new tree): here the PUBLIC debugger.store_report runs unmodified in the origin/main tree
and in the P3 tree, each in its own interpreter, over one seeded corpus (store keys for every
DOMAINS entry plus foreign keys; JSON-shaped docs with poisoned leaves/keys, bools, ints, tuples,
in-memory NaN keys), and the two reports are compared key by key.
Metric:   report_mismatches = number of (key, doc) pairs whose report dict differs between trees.
Command:  python3 store_report_e2e.py MAIN_TREE PROTO_TREE [--n N] [--perturb]
          --perturb: in the PROTO interpreter, store.quarantines ignores poisoned map keys (the
          finder's perturbation) -> mismatches must rise above 0.
Null:     MAIN_TREE vs MAIN_TREE -> 0.
Expected (baseline d749c986d, macOS arm64): main vs P3 -> 0; --perturb -> > 0.
"""
import json, os, subprocess, sys, time

CHILD = r'''
import json, math, random, sys
sys.path[:0] = ["tests/hastub", "custom_components"]
from heatpump_optimizer import store, debugger
n, perturb = int(sys.argv[1]), sys.argv[2] == "1"
if perturb:
    def q(payload):
        def s(v):
            if isinstance(v, dict): return {k: s(x) for k, x in v.items()}
            if isinstance(v, list): return [s(x) for x in v]
            if isinstance(v, tuple): return tuple(s(x) for x in v)
            return None if store._poisoned(v) else v
        return s(payload) != payload
    debugger.quarantines = q
r = random.Random(4711)
POI = [float("nan"), float("inf"), -float("inf"), 1e300, 2**64, "NaN", "1e300", "-Infinity"]
PL = [0, 1, -2, 0.25, 19.5, True, False, None, "x", "2026-02-01T00:00:00+00:00", 1e14]
KEYS = ["a", "rate", "value", "last", "0", "nan", "1e300", "Infinity", "samples"]
def val(d=0):
    x = r.random()
    if d < 3 and x < .22: return {r.choice(KEYS): val(d+1) for _ in range(r.randint(0, 4))}
    if d < 3 and x < .34: return [val(d+1) for _ in range(r.randint(0, 3))]
    if d < 3 and x < .40: return tuple(val(d+1) for _ in range(r.randint(0, 3)))
    return r.choice(POI) if x < .55 else r.choice(PL)
keys = [f"heatpump_optimizer_e_9_{nm}" for nm in store.DOMAINS] + ["heatpump_optimizer_x_nope", "other"]
docs = [{k: 1.0 for k in store.DOMAINS[nm] if isinstance(k, str) and "*" not in k} for nm in store.DOMAINS]
docs += [{r.choice(KEYS): val() for _ in range(r.randint(1, 6))} for _ in range(n)]
docs += [{float("nan"): 1.0}, {1e300: 2}, {"a": (1, float("nan"))}]
out = []
for k in keys:
    for i, doc in enumerate(docs):
        try:
            rep = debugger.store_report({k: (1, doc)})[k]
            out.append(repr(rep))
        except Exception as e:
            out.append("EXC " + type(e).__name__)
print(json.dumps(out))
'''


def run(tree, n, perturb):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-c", CHILD, str(n), "1" if perturb else "0"], cwd=tree,
                       env=env, check=True, capture_output=True, text=True)
    return json.loads(p.stdout)


if __name__ == "__main__":
    t0p, t0t = time.process_time(), time.thread_time()
    a, b = sys.argv[1], sys.argv[2]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 600
    ra, rb = run(a, n, False), run(b, n, "--perturb" in sys.argv)
    mm = sum(x != y for x, y in zip(ra, rb)) + abs(len(ra) - len(rb))
    exc = sum(x.startswith("EXC") for x in ra), sum(x.startswith("EXC") for x in rb)
    print(f"RESULT pairs={len(ra)} report_mismatches={mm} exceptions_main={exc[0]} exceptions_proto={exc[1]}")
    print(f"RESULT thread_factor={(time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
