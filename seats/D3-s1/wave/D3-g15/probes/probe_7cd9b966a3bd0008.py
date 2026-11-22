#!/usr/bin/env python3
# Metric: the run-up floors DhwPlanner._dhw_legionella_ceilings writes, and the folded requirement
#   min(max(floor, run-up), ceiling) summed over the steps before the cycle, when the availability floor at one
#   step of the walk equals the walk's `need` there EXACTLY (the `need <= floor_temps[m]` boundary), baseline vs mutant.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_7cd9b966a3bd0008.py
# EXPECTED RESULT tie_runup_steps_baseline=2  tie_runup_steps_mutant=5 count  (tie at step 38: the mutant walks on to 35)
# EXPECTED RESULT tie_req_sum_delta_c=14.0886 C  (the extra run-up floors raise the requirement where they beat 20 C)
# EXPECTED RESULT ties_moved=5/5 count (floor tie at each walk step m = 39..35)  null_moved=0 count (floor 1e-9 off the tie)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 793
#   `if need <= floor_temps[m]:` (its `break`); the requirement fold is dhw_planner.py:1174.
# Perturbation: key 7cd9b966a3bd0008 (CMP_BOUND) -> `if need < floor_temps[m]:`, in memory (method recompiled,
#   mock.patch.object). Direction: at the tie the baseline stops the walk, the mutant writes run-up floors below it.
# Null control: the same floor raised by 1e-9 C (need < floor in both arms: both stop, identical).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "if need <= floor_temps[m]:", "if need < floor_temps[m]:")
p = c.params()
n, step = 96, 40
h = c.horizon(n=n)
base_floor = np.full(n, 20.0)
ref = c.ceilings(p, h, step=step, floor=base_floor)
walk = [m for m in range(step - 1, -1, -1) if ref[2][m]]
print(f"RESULT reference_runup_steps={len(walk)} count  (floor 20 C: steps {walk[-1]}..{walk[0]})")
moved = 0
for m in walk:
    fl = base_floor.copy()
    fl[m] = ref[2][m]
    moved += c.differs(c.ceilings(p, h, step=step, floor=fl), c.ceilings(p, h, step=step, floor=fl, fn=fn))
print(f"RESULT ties_moved={moved}/{len(walk)} count")
m = walk[1]
fl = base_floor.copy()
fl[m] = ref[2][m]
b, mu = c.ceilings(p, h, step=step, floor=fl), c.ceilings(p, h, step=step, floor=fl, fn=fn)
rb, rm = c.requirement(b, fl), c.requirement(mu, fl)
print(f"RESULT tie_step={m} floor={fl[m]!r} C")
print(f"RESULT tie_runup_steps_baseline={sum(1 for x in b[2] if x)} count")
print(f"RESULT tie_runup_steps_mutant={sum(1 for x in mu[2] if x)} count")
print(f"RESULT tie_req_sum_baseline={sum(rb[:step]):.4f} C  tie_req_sum_mutant={sum(rm[:step]):.4f} C")
print(f"RESULT tie_req_sum_delta_c={sum(rm[:step]) - sum(rb[:step]):.4f} C")
fl2 = fl.copy()
fl2[m] = fl[m] + 1e-9
print(f"RESULT null_moved={c.differs(c.ceilings(p, h, step=step, floor=fl2), c.ceilings(p, h, step=step, floor=fl2, fn=fn))} count")
c.footer()
