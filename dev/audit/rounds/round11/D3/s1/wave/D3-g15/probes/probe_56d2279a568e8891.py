#!/usr/bin/env python3
# Metric: DhwPlanner._dhw_legionella_due's result at n_steps == 0 (the one separating value), baseline vs mutant,
#   directly and through the production optimize() on a 0-step horizon (horizon_hours 0, or empty price and
#   outdoor series), and the count of in-range inputs (n_steps >= 1) whose arms differ.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_56d2279a568e8891.py
# EXPECTED RESULT moved_in_range=0 count
# EXPECTED RESULT n0_baseline=(False, None, None)  n0_mutant: per hours_since (overdue: raises; due later: unchanged)
# EXPECTED RESULT reach_n0_optimize_baseline=raises IndexError  reach_n0_optimize_mutant=raises (optimize fails at
#   n_steps 0 in both arms, so no published plan separates them)
# Reach note: coordinator.py:6379 returns "no_prices" before any solve when fewer than 4 price steps exist, so the
#   integration never calls optimize() with n_steps 0; the optimize() arms above are a direct call.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_due, line 598
#   `and n_steps > 0`.
# Perturbation: key 56d2279a568e8891 (CMP_BOUND) -> `and n_steps >= 0`, in memory (method recompiled,
#   mock.patch.object). Direction: only n_steps == 0 separates.
# Null control: n_steps 1, 2, 96 at several hours_since, identical.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402

fn = c.mutant("_dhw_legionella_due", "and n_steps > 0", "and n_steps >= 0")
p = c.params()
moved = 0
for n in (1, 2, 96):
    for hs in (0.0, 20.0, 150.0, 167.9, 400.0):
        h = c.horizon(n=n, hours_since=hs)
        moved += c.differs(c.due(p, h), c.due(p, h, fn=fn))
print(f"RESULT moved_in_range={moved} count")
for hs in (20.0, 168.0, 400.0):
    h = c.horizon(n=0, hours_since=hs)
    b, m = c.due(p, h), c.due(p, h, fn=fn)
    print(f"RESULT n0_hours_since_{int(hs)}_baseline={b[:3] if isinstance(b, tuple) else b}")
    print(f"RESULT n0_hours_since_{int(hs)}_mutant={m[:3] if isinstance(m, tuple) else m}")
for name, f in (("baseline", None), ("mutant", fn)):
    with c.arm("_dhw_legionella_due", f):
        r = c.solve_reach("_dhw_legionella_ceilings", lambda kw, h: h.n_steps, n=0, hours_since=400.0)
    print(f"RESULT reach_n0_optimize_{name}={[x for x in r if isinstance(x, str)] or 'ok'}")
c.footer()
