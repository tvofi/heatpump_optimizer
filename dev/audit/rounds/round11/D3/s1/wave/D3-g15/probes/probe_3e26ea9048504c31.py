#!/usr/bin/env python3
# Metric: whether DhwPlanner._dhw_legionella_ceilings' outputs differ between baseline and mutant (count of inputs),
#   and, at n_steps == 0 (the only separating value), what each arm does when driven through the production
#   path: _dhw_legionella_due's own `n_steps > 0` guard returns step None there, and optimize() on a 0-step
#   horizon, in both arms.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_3e26ea9048504c31.py
# EXPECTED RESULT moved_in_range=0 count  (n_steps 1, 2, 96 with the cycle step None / 0 / middle / last)
# EXPECTED RESULT direct_n0_step0_baseline=unchanged  direct_n0_step0_mutant=raises IndexError (a direct call with a
#   step on an empty horizon: the separating input, which no caller hands over)
# EXPECTED RESULT reach_n0_due_step=None  (the due stage never names a step at n_steps 0)
# EXPECTED RESULT reach_n0_plan_moved=0 count  (_dhw_legionella_plan at n_steps 0: identical both arms)
# EXPECTED RESULT reach_n0_optimize_baseline=raises IndexError  reach_n0_optimize_mutant=raises IndexError
# Reach note: coordinator.py:6379 returns "no_prices" before any solve when fewer than 4 price steps exist, so the
#   integration never calls optimize() with n_steps 0; the optimize() arms above are a direct call.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings, line 743
#   `if c_dhw > 0.0 and legionella_step is not None and n_steps > 0 and (`; caller _dhw_legionella_plan (line 819).
# Perturbation: key 3e26ea9048504c31 (CMP_BOUND) `n_steps > 0` -> `n_steps >= 0`, in memory (method recompiled, attached
#   with mock.patch.object). Direction: only n_steps == 0 with a non-None step separates (no-op -> IndexError).
# Null control: n_steps >= 1, where the guard is identical in both arms.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402
import numpy as np  # noqa: E402

OLD = "if c_dhw > 0.0 and legionella_step is not None and n_steps > 0 and ("
NEW = "if c_dhw > 0.0 and legionella_step is not None and n_steps >= 0 and ("
fn = c.mutant("_dhw_legionella_ceilings", OLD, NEW)
p = c.params()
moved = tried = 0
for n in (1, 2, 96):
    h = c.horizon(n=n)
    for step in (None, 0, n // 2, n - 1):
        tried += 1
        moved += c.differs(c.ceilings(p, h, step=step), c.ceilings(p, h, step=step, fn=fn))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_in_range={moved} count")
h0 = c.horizon(n=0)
b, m = c.ceilings(p, h0, step=0), c.ceilings(p, h0, step=0, fn=fn)
print(f"RESULT direct_n0_step0_baseline={'unchanged' if isinstance(b, tuple) else b}")
print(f"RESULT direct_n0_step0_mutant={m if isinstance(m, str) else 'unchanged'}")
# Through the production caller at n_steps 0: the due stage decides the step.
for hs in (20.0, 150.0, 400.0):
    d = c.due(p, c.horizon(n=0, hours_since=hs))
    print(f"RESULT reach_n0_due_step_hours_since_{int(hs)}={d[2] if isinstance(d, tuple) else d}")


def plan(fn_):
    pl = c.planner(p)
    with c.arm("_dhw_legionella_ceilings", fn_):
        try:
            r = pl._dhw_legionella_plan(c.horizon(n=0, hours_since=400.0), params=p, hours_mod=np.zeros(0),
                                        draw_rates=np.zeros(0), ready_temps=np.zeros(0), floor_temps=np.zeros(0),
                                        p_dhw_run=4.0, dhw_prices=np.zeros(0))
            return (r.due, r.step, r.max_temp.tolist(), r.lp_max_temp.tolist(), r.runup_temps.tolist())
        except Exception as exc:
            return f"raises {type(exc).__name__}"


print(f"RESULT reach_n0_plan_moved={c.differs(plan(None), plan(fn))} count")
for name, f in (("baseline", None), ("mutant", fn)):
    with c.arm("_dhw_legionella_ceilings", f):
        r = c.solve_reach("_dhw_legionella_due", lambda kw, h: h.n_steps, n=0, hours_since=400.0)
    print(f"RESULT reach_n0_optimize_{name}={[x for x in r if isinstance(x, str)] or 'ok'}")
c.footer()
