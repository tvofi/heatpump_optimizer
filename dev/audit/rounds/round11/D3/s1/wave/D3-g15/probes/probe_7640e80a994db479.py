#!/usr/bin/env python3
# Metric: whether the anti-legionella cycle is planned (DhwPlanner._dhw_legionella_due's `due`, and the production
#   optimize()'s published predictive_info["dhw_legionella_due"] plus its hot-water kWh) when the hard deadline falls
#   EXACTLY on the horizon's end (deadline_step == n_steps), baseline vs mutant.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_7640e80a994db479.py
# EXPECTED RESULT edge_due_baseline=False  edge_due_mutant=True (step = the cheapest reachable step)
# EXPECTED RESULT edge_solve_due_baseline=False  edge_solve_due_mutant=True; dhw kWh moves
# EXPECTED RESULT null_moved=0 count  (deadline one step later, n+1: elastic window, both arms no cycle; one step
#   earlier, n-1: hard deadline in both arms, same step)
# Inputs: 200 L tank, 55/60 C, interval 7 d = 168 h, 96 x 15 min steps; hours_since 144 h -> 24 h remaining ->
#   deadline_step floor(24/0.25) = 96 = n_steps. hours_since 143.75 / 144.25 are the nulls. Every input is a
#   value the cycle clock passes through in production once per interval.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_due, line 628
#   `if deadline_step < n_steps:`; published as predictive_info["dhw_legionella_due"] (optimizer.py:5952).
# Perturbation: key 7640e80a994db479 (CMP_BOUND) -> `if deadline_step <= n_steps:`, in memory (method recompiled,
#   mock.patch.object onto DhwPlanner, which optimize() builds per solve). Direction: at deadline == n_steps the
#   baseline leaves the cycle to the next solves (deadline outside this horizon), the mutant buys it now.
# Null control: hours_since 143.75 and 144.25 (deadline n+1 and n-1), identical arms.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_due", "if deadline_step < n_steps:", "if deadline_step <= n_steps:")
p = c.params()
n = 96
h = c.horizon(n=n, hours_since=144.0)
dl = int(np.floor((168.0 - 144.0) / h.dt))
print(f"RESULT deadline_step={dl} n_steps={n}")
b, m = c.due(p, h), c.due(p, h, fn=fn)
print(f"RESULT edge_due_baseline={b[0]} step={b[2]}")
print(f"RESULT edge_due_mutant={m[0]} step={m[2]}")
nm = 0
for hs in (143.75, 144.25):
    hh = c.horizon(n=n, hours_since=hs)
    nm += c.differs(c.due(p, hh), c.due(p, hh, fn=fn))
print(f"RESULT null_moved={nm} count")


def run(f, hs):
    with c.arm("_dhw_legionella_due", f):
        r = c.solve(hours_since=hs)
    return bool(r.predictive_info.get("dhw_legionella_due")), float(np.sum(r.dhw_power_schedule)) * 0.25


sb, sm = run(None, 144.0), run(fn, 144.0)
print(f"RESULT edge_solve_due_baseline={sb[0]} dhw_kwh={sb[1]:.4f}")
print(f"RESULT edge_solve_due_mutant={sm[0]} dhw_kwh={sm[1]:.4f}")
print(f"RESULT edge_solve_dhw_kwh_delta={sm[1] - sb[1]:.4f} kWh")
nb, nmu = run(None, 143.75), run(fn, 143.75)
print(f"RESULT null_solve_moved={int(nb != nmu)} count  (hours_since 143.75)")
c.footer()
