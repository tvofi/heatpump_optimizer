"""F2.2 production-call count (the N-solve-recompute RCA's carry-in metric).

Drives the RCA prototype's own capture (tests/stress.py:capture_calls and
calls_drift at handoff/r9-rca-avoidable-interpreter-bound-recomputation
ab04e39b) on two trees side by side, in fresh interpreters, exactly as the
RCA's demo_calls.py does, but on worktrees named on the command line.
Usage: python calls_demo.py HERE_TREE BASE_TREE [LABEL ...]   (cwd: RCA export root)
Null arm: the same tree twice.
"""
import json, os, sys, tempfile, time
sys.path[:0] = ["tests", "custom_components"]
import stress

here_wt, base_wt = sys.argv[1], sys.argv[2]
labels = sys.argv[3:] or None
tmp = tempfile.mkdtemp(prefix="f22_calls_")
t0 = time.perf_counter()
procs = [stress.capture_calls(wt, os.path.join(tmp, f"t{i}.json"), labels)
         for i, wt in enumerate((here_wt, base_wt))]
rows = []
for i, p in enumerate(procs):
    out, err = p.communicate()
    assert p.returncode == 0, err[-800:]
    rows.append(json.load(open(os.path.join(tmp, f"t{i}.json"))))
here, base = rows
covered, replanned, over, unmetered = stress.calls_drift(here, base)
for label in sorted(here):
    h, b = here[label], base[label]
    hc, bc = sum(h["calls"].values()), sum(b["calls"].values())
    print(f"  {label:30s} calls {hc}/{bc} = {hc / bc:.4f}x  evals {h['evals']}/{b['evals']}  "
          f"simulate {h['simulate']}/{b['simulate']}  "
          f"objective_identical={h['objective'] == b['objective']}")
for o in over:
    print("  OVER", o)
print(f"RESULT objective_identical={sum(here[k]['objective'] == base[k]['objective'] for k in here)} of {len(here)}")
print(f"RESULT scenarios={len(here)} covered={len(covered)} replanned={len(replanned)} "
      f"calls_over={len(over)} wall_s={time.perf_counter() - t0:.1f}")
