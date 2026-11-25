#!/usr/bin/env python3
# Metric: whether DhwPlanner._dhw_legionella_ceilings' three output arrays differ between the baseline and the
#   mutant on a horizon of n_steps (count of inputs that differ), and the smallest n_steps a production
#   optimize() hands the planner.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g15/probes/probe_0e752f692873e876.py
# EXPECTED RESULT moved_in_range=0 count  (n_steps in {0, 1, 2, 96, 192}, cycle step None / first / middle / last)
# EXPECTED RESULT neg_n_baseline=ok-empty  neg_n_mutant=raises ValueError  (n_steps=-1, the only separating input)
# EXPECTED RESULT reach_min_n_steps=96 count  (optimize: n_steps = min(len(prices), len(outdoor), config.n_steps) >= 0)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g15 (4 vCPU Intel Xeon @ 2.10GHz, Linux).
# Instrumented symbol: custom_components.heatpump_optimizer.dhw_planner:DhwPlanner._dhw_legionella_ceilings,
#   line 740 `runup_temps = np.zeros(max(n_steps, 0))`.
# Perturbation: key 0e752f692873e876 (CLAMP_DROP) -> `runup_temps = np.zeros((n_steps))`, applied in memory (method
#   recompiled from its own source, attached with mock.patch.object for the mutant arm). Direction: only a
#   negative n_steps separates (empty array -> ValueError); n_steps is a min of lengths, never negative.
# Null control: every n_steps >= 0, where max(n, 0) == n and both arms return identical arrays.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lg_common as c  # noqa: E402

fn = c.mutant("_dhw_legionella_ceilings", "runup_temps = np.zeros(max(n_steps, 0))", "runup_temps = np.zeros((n_steps))")
p = c.params()
moved = tried = 0
for n in (0, 1, 2, 96, 192):
    h = c.horizon(n=n)
    for step in sorted({None, 0, n // 2, n - 1} - ({0, n // 2, n - 1} if n == 0 else set()), key=str):
        tried += 1
        moved += c.differs(c.ceilings(p, h, step=step), c.ceilings(p, h, step=step, fn=fn))
print(f"RESULT inputs_tried={tried} count")
print(f"RESULT moved_in_range={moved} count")
h = c.horizon(n=-1)
b, m = c.ceilings(p, h, step=None), c.ceilings(p, h, step=None, fn=fn)
print(f"RESULT neg_n_baseline={'ok-empty' if isinstance(b, tuple) and b[2] == [] else b}")
print(f"RESULT neg_n_mutant={m if isinstance(m, str) else 'ok'}")
seen = c.solve_reach("_dhw_legionella_ceilings", lambda kw, h: h.n_steps)
ns = [s for s in seen if isinstance(s, int)]
print(f"RESULT reach_calls={len(ns)} count")
print(f"RESULT reach_min_n_steps={min(ns) if ns else 'none'} count")
c.footer()
