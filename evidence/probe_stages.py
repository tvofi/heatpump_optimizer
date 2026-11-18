"""Reviewer's probe: CPU seconds in HeatPumpOptimizer.optimize and in
_multi_start_minimize (the relaxed descent) over one owner replay, at
whatever tree it runs from. Run from that tree's root with
PYTHONPATH=tests/hastub:tests:."""
import collections, sys, time, json, atexit
import replay as R
import heatpump_optimizer.optimizer as O
cpu = collections.Counter(); n = collections.Counter()
def timed(owner, name):
    f = getattr(owner, name)
    def g(*a, **k):
        t = time.process_time()
        try:
            return f(*a, **k)
        finally:
            cpu[name] += time.process_time() - t; n[name] += 1
    setattr(owner, name, g)
timed(O, "_multi_start_minimize")
timed(O.HeatPumpOptimizer, "optimize")
for extra in ("_commit_runs", "_relaxed_plans", "_relaxed_starts"):
    if hasattr(O, extra):
        timed(O, extra)
atexit.register(lambda: print("PROBE", json.dumps({"calls": n, "cpu_s": {k: round(v, 1) for k, v in cpu.items()}}), file=sys.stderr))
sys.exit(R.main(["--one", sys.argv[1]]))
