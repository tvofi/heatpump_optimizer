#!/usr/bin/env python3
# Metric: (a) unit: the solver's (x, cost) when the step size is exactly 1e-10, baseline vs mutant;
#   (b) reach: over the production sweep in _drive.sweep() -- 120 two-state/one-state runs of SystemIdentification
#   arm/step/identify on the production ThermalModel (presets heavy_old, typical_slab, light_new x declared plant x
#   true house {as configured, gains 2.5 / -1.5 kW, heat-loss scale x3, room mass x0.25} x (noise, seed, cadence)
#   {(0,0,0.5h), (0.02C,0,0.5h), (0.05C,1,0.5h), (0.02C,2,0.25h)}) plus 48 one-state runs on the first-order plant of
#   tests/features.py:_drift_drive (seeds 1000..1011 x {sigma 0.02, 0, 0.02 with 0.10 C/h drift, 0.05 at 15 min}) --
#   the count of runs whose published outcome differs (every SysIdResult field, the override sequence, every sysid
#   log line), and the count of calls of the mutated symbol whose arguments separate the two arms.
#   Count key: the outcome the production seam delivers (SystemIdentification.result, step()'s return, the log).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g37/probes/probe_99866c2ffc704413.py
# Expected: see the RESULT lines recorded in dev/audit/rounds/round11/D3/s1/wave/D3-g37/results/99866c2ffc704413.json (exact; no timing).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g37 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.sysid:_lm_solve (sysid.py:852); production callers sysid.py:1027/1120/1149 (slab UA profile/prior half-widths) and sysid.py:2380 (identify_slab multi-start).
# Perturbation: sysid.py:852 `if not accepted or float(np.max(np.abs(delta))) < 1e-10:` -> `if not accepted or float(np.max(np.abs(delta))) <= 1e-10:` (key 99866c2ffc704413), applied in memory (the function recompiled
#   from its own source with the one line replaced; production reaches it through a module-attribute swap).
#   Direction: the solver stops one iteration earlier only when max|delta| is exactly 1e-10
# Null control: the linear residual null_linear
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _mut  # noqa: E402  thread pin first
import _drive  # noqa: E402
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import sysid  # noqa: E402

KEY = "99866c2ffc704413"
mut, name, rec = _mut.mutant_for(sysid, KEY)
assert name == "_lm_solve", name
base = getattr(sysid, name)

def _same(u, v):
    if isinstance(u, tuple) and isinstance(v, tuple):
        return len(u) == len(v) and all(_same(p, q) for p, q in zip(u, v))
    a, b = np.asarray(u, dtype=float), np.asarray(v, dtype=float)
    return a.shape == b.shape and bool(np.all((a == b) | (np.isnan(a) & np.isnan(b))))


def _call(fn, *a, **kw):
    try:
        return fn(*a, **kw)
    except Exception as exc:  # an exception is an outcome too
        return type(exc).__name__


def separates(a, kw):
    u, v = _call(base, *a, **kw), _call(mut, *a, **kw)
    if isinstance(u, str) or isinstance(v, str):
        return u != v
    return not _same(u, v)


def arm(label, *a, **kw):
    u, v = _call(base, *a, **kw), _call(mut, *a, **kw)
    print(f"RESULT {label}_baseline={u}")
    print(f"RESULT {label}_mutant={v}")
    moved = (u != v) if (isinstance(u, str) or isinstance(v, str)) else (not _same(u, v))
    print(f"RESULT {label}_moved={int(moved)} count")
    return int(moved)


step_res = lambda x: np.array([1.0 if x[0] < 1.0 + 5e-7 else 2.0])          # a plateau: equal cost off the jump
rosen = lambda x: np.array([10.0 * (x[1] - x[0] ** 2), 1.0 - x[0]])          # 20+ accepted steps from (-1.2, 1)
lin = lambda x: np.array([x[0] - 3.0, 2.0 * (x[1] + 1.0)])                   # null: one exact Gauss-Newton step
bound = lambda x: np.array([x[0] - 20.0, x[1]])                              # optimum past the clip bound 10
flat2 = lambda x: np.array([x[0] + x[1] - 1.0])                              # rank-deficient Jacobian
moved = 0
moved += arm("unit_plateau", step_res, np.array([1.0]), clip=None)
moved += arm("unit_rosenbrock", rosen, np.array([-1.2, 1.0]), max_iter=200, clip=None)
moved += arm("unit_bound", bound, np.array([10.0, 0.5]), clip=(0, -5.0, 10.0))
moved += arm("unit_rankdef", flat2, np.array([0.3, 0.1]), max_iter=200, clip=None)
rng = np.random.default_rng(7)
rmoved = 0
for t in range(200):
    A = rng.normal(size=(3, 3)); c = rng.normal(size=3)
    q = lambda x, A=A, c=c: np.concatenate([A @ x - c, 0.1 * np.sin(3.0 * x)])
    rmoved += separates((q, rng.normal(size=3)), {"max_iter": 100, "clip": None})
print(f"RESULT unit_random_moved={rmoved} count (over 200 random nonlinear least-squares problems)")
print(f"RESULT unit_moved={moved} count")
nm = arm("null_linear", lin, np.array([0.0, 0.0]), clip=None)
print(f"RESULT null_moved={nm} count")


calls = []


def spy(*a, **kw):
    calls.append((a, kw))
    return base(*a, **kw)


runs, differ = _drive.reach(sysid, name, mut, spy)
print(f"RESULT reach_runs={runs} count")
print(f"RESULT reach_calls={len(calls)} count")
print(f"RESULT reach_calls_separating={sum(1 for a, kw in calls if separates(a, kw))} count")
print(f"RESULT reach_outcomes_differ={len(differ)} count")
for lab, b, m in differ[:10]:
    print(f"RESULT reach_differ_case={lab}: baseline[{b}] mutant[{m}]")
_mut.tail()
