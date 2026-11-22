#!/usr/bin/env python3
# Metric: the largest run-up floor DhwPlanner._dhw_legionella_ceilings writes, and the number of steps whose folded
#   requirement min(max(floor, run-up), ceiling) is at the boost top, when the pump cannot carry the ramp
#   (a heavy draw before the cycle), baseline vs mutant.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_f1549576a94b99be.py
# EXPECTED RESULT runup_max_baseline=0.0000 C (walk cut at once)  runup_max_mutant=139.1276 C (20 steps above the 60 C top)
# EXPECTED RESULT req_at_boost_steps_baseline=0  req_at_boost_steps_mutant=20 count; ceilings at 60 C: 1 vs 21 steps
# EXPECTED RESULT null_moved=0 count  (no draw: the ramp is carried, the guard never fires, arms identical)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 784
#   `if need > boost_top:` (its `break`); the folded requirement is dhw_planner.py:1174 then _within_ceiling.
# Perturbation: key f1549576a94b99be (GUARD_OFF) -> `if False:`, in memory (method recompiled, mock.patch.object).
#   Direction: the walk no longer stops where the pump cannot carry the ramp: run-up floors above the boost top
#   and boost-top ceilings are written all the way back to step 0.
# Null control: zero draws (need stays below the boost top), identical arrays.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "if need > boost_top:", "if False:")
p = c.params()
n, step = 96, 40
h = c.horizon(n=n)
floor = np.full(n, 20.0)
draw = np.zeros(n)
draw[36:41] = 20.0  # a 20 kW-equivalent tap draw for the hour before the cycle, more than a 4 kW pump delivers
b, m = c.ceilings(p, h, step=step, draw=draw), c.ceilings(p, h, step=step, draw=draw, fn=fn)
B = min(70.0, float(p.dhw_store.rating_max_temp))
rb, rm = c.requirement(b, floor), c.requirement(m, floor)
print(f"RESULT boost_top={B} C")
print(f"RESULT runup_max_baseline={max(b[2]):.4f} C")
print(f"RESULT runup_max_mutant={max(m[2]):.4f} C")
print(f"RESULT runup_steps_above_boost_mutant={sum(1 for x in m[2] if x > B)} count")
print(f"RESULT req_at_boost_steps_baseline={sum(1 for x in rb if x >= B)} count")
print(f"RESULT req_at_boost_steps_mutant={sum(1 for x in rm if x >= B)} count")
print(f"RESULT ceiling_at_boost_steps_baseline={sum(1 for x in b[0] if x >= B)} count  mutant={sum(1 for x in m[0] if x >= B)} count")
print(f"RESULT null_moved={c.differs(c.ceilings(p, h, step=step), c.ceilings(p, h, step=step, fn=fn))} count")
c.footer()
