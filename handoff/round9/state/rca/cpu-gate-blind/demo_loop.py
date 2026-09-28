"""RCA demo: the loop-thread figure prototyped in tests/replay.py on
handoff/r9-rca-cpu-gate-blind (cost_figures' loop_cpu_ratio, judged by the
shipped cost_offenders).
Metric: offenders tests/replay.py:cost_offenders returns for each arm, judged
twice -- against the SHIPPED budget keys only (cpu_ratio, peak_kib: D9-s2-02's
blindness) and against the prototype's keys (plus loop_cpu_ratio).
Arms (each a fresh interpreter, `tests/replay.py --one ... --inject-cost`):
  none x3   clean (null control; its spread sizes nothing, the 2x band does)
  loop      the loop thread's own work run exactly twice (D9-s2-02's injection)
  cpu       the whole cycle doubled (replay's own shipped perturbation; positive control)
Budget: sqrt(2) x the largest clean figure of the three none runs, per replay.py's
own recording rule. Command (prototype worktree root):
  PYTHONPATH=tests/hastub python3 <this>
"""
import json, math, subprocess, sys, os
sys.path[:0] = ["tests"]
import replay
FIX = "tests/replay/synthetic-dhw-only.json"
def arm(kind):
    cmd = [sys.executable, "tests/replay.py", "--one", FIX] + (["--inject-cost", kind] if kind else [])
    out = subprocess.run(cmd, capture_output=True, text=True, env=dict(os.environ)).stdout
    line = next(l for l in out.splitlines() if l.startswith(replay.MARK))
    return json.loads(line[len(replay.MARK):])["cost"]
clean = [arm(None) for _ in range(3)]
keys = ("cpu_ratio", "peak_kib", "loop_cpu_ratio")
budget = {k: round(math.sqrt(2) * max(c[k] for c in clean), 4) for k in keys}
shipped_budget = dict(replay.COST_BUDGETS["synthetic-dhw-only.json"]); shipped_budget.pop("loop_cpu_ratio", None)
print("budget(prototype, this box)", budget, "shipped", shipped_budget)
runs = [("none", c) for c in clean] + [("loop", arm("loop")), ("cpu", arm("cpu"))]
for name, c in runs:
    fig = {k: c[k] for k in keys}
    shipped = replay.cost_offenders({k: fig[k] for k in ("cpu_ratio", "peak_kib")}, shipped_budget)
    proto = replay.cost_offenders(fig, budget)
    over = lambda offs: [o for o in offs if "over its budget" in o]
    print(f"RESULT arm={name} cpu_ratio={fig['cpu_ratio']} loop_cpu_ratio={fig['loop_cpu_ratio']} "
          f"shipped_over={len(over(shipped))} prototype_over={len(over(proto))} prototype_offenders={proto}")
