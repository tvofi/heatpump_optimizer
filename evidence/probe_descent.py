"""Reviewer's probe (built by the reviewer, not the finder's): over one owner
replay, count the plans _relaxed_plans returns and the CPU seconds spent in
_relaxed_plans and _commit_runs. Run from the worktree root with
PYTHONPATH=tests/hastub:tests."""
import collections, sys, time, json, atexit
import replay as R

stats = collections.Counter()
cpu = collections.Counter()

def wrap(O, name, count_plans=False):
    f = getattr(O, name)
    def g(*a, **k):
        t = time.process_time()
        out = f(*a, **k)
        cpu[name] += time.process_time() - t
        stats[name + ":calls"] += 1
        if count_plans:
            stats["plans=%d" % len(out[1])] += 1
        return out
    setattr(O, name, g)

import heatpump_optimizer.optimizer as O
wrap(O, "_relaxed_plans", True)
wrap(O, "_commit_runs")
atexit.register(lambda: print("PROBE", json.dumps({"counts": stats, "cpu_s": {k: round(v, 1) for k, v in cpu.items()}}), file=sys.stderr))
sys.exit(R.main(["--one", sys.argv[1]]))
