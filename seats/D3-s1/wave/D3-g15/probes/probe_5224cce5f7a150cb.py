#!/usr/bin/env python3
# Metric: count of inputs on which DhwPlanner._dhw_legionella_due's (due, hour, step, ready_temps) differ between
#   baseline and mutant, over a grid covering every branch of the hard-deadline placement, and how many grid
#   points take the branch the mutated line sits in (hard deadline, tank reachable).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_5224cce5f7a150cb.py
# EXPECTED RESULT inputs_tried=432 count  moved=0 count  branch_hard_reachable=124  branch_hard_overdue_reachable=156  branch_hard_unreachable=8
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_due, line 658
#   `first = min(max(reach_step, 0), n_steps - 1)`.
# Perturbation: key 5224cce5f7a150cb (CLAMP_DROP) -> `first = (max(reach_step, 0))`, in memory (method recompiled, mock.patch.object).
#   Direction: none expected. The dropped clamp is redundant by the branch's own invariant:
#   the outer min(..., n_steps - 1): in this branch reach_step < n_steps (the else of reach_step >= n_steps), so max(reach_step, 0) <= n_steps - 1 already.
# Inputs tried: n_steps 4/96/192 x hours_since 0/100/150/167/168/170/400/2000 h (interval 168 h: deadline inside,
#   at, past the horizon, and overdue) x initial tank 20/45/55/59.5/60/65 C x Off window none/step 0/a band,
#   seeded random prices (the tie for the min/max is reach_step == n_steps - 1 or deadline_step == n_steps - 1,
#   both inside the grid).
# Null control: the baseline on the same grid (identity of both arms is the claim).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402

fn = c.mutant("_dhw_legionella_due", "first = min(max(reach_step, 0), n_steps - 1)", "first = (max(reach_step, 0))")
tried, moved, br = c.due_grid(fn, seed=658)
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved={moved} count")
for k, v in br.items():
    print(f"RESULT branch_{k}={v} count")
c.footer()
