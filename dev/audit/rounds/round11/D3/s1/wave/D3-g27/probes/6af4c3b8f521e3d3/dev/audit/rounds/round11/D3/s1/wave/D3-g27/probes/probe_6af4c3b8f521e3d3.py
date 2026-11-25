#!/usr/bin/env python3
# Metric: which of two plans optimizer._better_objective keeps (left/right) over an objective-value grid and its finite subset, the kept objective for left=10 against right=5, and the production calls that move.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_6af4c3b8f521e3d3.py
#   (from the repository root; $HOME/venv-ci on this box is /opt/hpo/venv-ci)
# EXPECTED RESULT example_input=left=0.0,right=-1e-09
# EXPECTED RESULT kept_baseline=left
# EXPECTED RESULT kept_mutant=right
# EXPECTED RESULT kept_objective_baseline_left10_right5=5.0
# EXPECTED RESULT kept_objective_mutant_left10_right5=5.0
# EXPECTED RESULT grid_inputs_tried=196 count
# EXPECTED RESULT grid_inputs_moved=4 count
# EXPECTED RESULT domain_inputs_tried=121 count
# EXPECTED RESULT domain_inputs_moved=4 count
# EXPECTED RESULT production_calls=0 count
# EXPECTED RESULT production_calls_moved=0 count
# EXPECTED RESULT null_inputs_moved=0 count
#   (counts are exact and deterministic, the random grid seeded; kW and objective deltas are solver floats, re-taken to 1e-3 relative on another BLAS build; thread_factor, load1, swapins quoted, not expected)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g27 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython 3.14).
# Instrumented symbol: heatpump_optimizer.optimizer:_better_objective, custom_components/heatpump_optimizer/optimizer.py:2111 `if np.isfinite(ro) and (not np.isfinite(lo) or ro < lo - 1e-9):`.
# Perturbation: key 6af4c3b8f521e3d3 (CMP_BOUND), `if np.isfinite(ro) and (not np.isfinite(lo) or ro < lo - 1e-9):` -> `if np.isfinite(ro) and (not np.isfinite(lo) or ro <= lo - 1e-9):`, applied in memory: the function is
#   re-compiled from its own source with the one line replaced, in a copy of the module namespace; the production solves
#   see it through mock.patch.object on the module the suite imports (heatpump_optimizer.optimizer). Direction: moved inputs rise from 0 under the mutant.
# Null control: the same function re-compiled with the line unchanged (the null_* RESULT lines), expected 0 moved.
# Count key: the OptimizationResult _better_objective returns (by identity), never an input attribute.
# Out of the D3-g27 full-gate wave (round 11, seat D3-s1): the key's full gate is gates/<key>.json in this wave dir.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import inspect, math, sys, textwrap, time
from pathlib import Path
from unittest import mock


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents, Path.cwd()):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))
import numpy as np  # noqa: E402
import harness  # noqa: E402,F401  (the suite's stub wiring, as tests/manual_plan.py imports it)
# the package path the suite's solves import (heatpump_optimizer.*), so a patch reaches them
from heatpump_optimizer import optimizer as opt  # noqa: E402

_T0 = (time.process_time(), time.thread_time())


def mutant(fn_name, old, new):
    """``fn_name`` re-compiled from its own source with the one mutated line, in a copy of
    the module namespace (the module itself is untouched)."""
    fn = getattr(opt, fn_name)
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old.strip()) == 1, (fn_name, old)
    src = src.replace(old.strip(), new.strip())
    ns = dict(opt.__dict__)
    exec(compile(src, opt.__file__, "exec"), ns)
    return ns[fn_name]


def result(name, value, unit=""):
    print(f"RESULT {name}={value}{(' ' + unit) if unit else ''}")


def tail():
    cpu, thr = time.process_time() - _T0[0], time.thread_time() - _T0[1]
    result("thread_factor", f"{cpu / thr:.3f}" if thr > 0 else "1.000")
    result("load1", f"{os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "na"
    result("swapins", sw)


def load_mp():
    """tests/manual_plan.py's optimizer builder (the module has a __main__ guard)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_mp_probe", str(ROOT / "tests" / "manual_plan.py"))
    mp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mp)
    return mp


def production_solves(mp):
    """The production solves every reach count runs: HeatPumpOptimizer.optimize on
    tests/manual_plan.py's winter house (with DHW): unpinned; space-pinned (on at step 36, off
    at 40-43, on at every step whose headroom beside the unpinned plan's DHW is below the pin's
    on-power, free elsewhere); DHW-pinned (on at step 20, off at 60-63, free elsewhere); and
    space-pinned on at step 36 under a 0.05 kW total power cap there (power_caps_extra), a step
    whose upper bound is below the pin's on-power."""
    bundle = mp._build_optimizer("winter_typical", "winter_cold")
    out = {"plain": mp._solve(bundle)}
    n = mp.N
    p_max = bundle[0].model.params.max_electrical_power
    on_power = bundle[0]._pin_on_power(p_max)
    full = [i for i, v in enumerate(out["plain"].dhw_power_schedule) if p_max - v < on_power]
    sp = np.full(n, np.nan)
    sp[36] = 1.0
    sp[40:44] = 0.0
    sp[full] = 1.0
    out["space_pinned"] = mp._solve(bundle, space_pins=sp)
    dp = np.full(n, np.nan)
    dp[20] = 1.0
    dp[60:64] = 0.0
    out["dhw_pinned"] = mp._solve(bundle, dhw_pins=dp)
    cap = np.full(n, 100.0)
    cap[36] = 0.05
    sp2 = np.full(n, np.nan)
    sp2[36] = 1.0
    out["capped_pinned"] = mp._solve(bundle, space_pins=sp2, power_caps_extra=cap)
    return out, full, p_max


def run_arms(mp, patch_to=None):
    """production_solves with ``opt.<name>`` replaced by ``fn`` for ``patch_to=(name, fn)``."""
    if patch_to is None:
        return production_solves(mp)
    with mock.patch.object(opt, patch_to[0], patch_to[1]):
        return production_solves(mp)


def same(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return a.shape == b.shape and bool(np.all((a == b) | (np.isnan(a) & np.isnan(b))))

OLD = '    if np.isfinite(ro) and (not np.isfinite(lo) or ro < lo - 1e-9):'
NEW = '    if np.isfinite(ro) and (not np.isfinite(lo) or ro <= lo - 1e-9):'

# ---- _better_objective: a value grid plus a production reach count ----
from types import SimpleNamespace  # noqa: E402
F = "_better_objective"
base = opt._better_objective
mut = mutant(F, OLD, NEW)
VALUES = [0.0, 1.0, 1.0 - 1e-9, 1.0 - 2e-9, 1.0 + 1e-9, 0.0 - 1e-9, 5.0, 10.0, 69.47964532244127,
          69.47964532244127 - 1e-9, -3.0, float("inf"), float("-inf"), float("nan")]

tried = moved = dom_tried = dom_moved = 0
example = dom_example = None
for lo in VALUES:
    for ro in VALUES:
        left, right = SimpleNamespace(objective_value=lo, tag="left"), SimpleNamespace(objective_value=ro, tag="right")
        tried += 1
        # the production domain: an objective is any float a solve returns; finite on a sound solve
        dom = math.isfinite(lo) and math.isfinite(ro)
        dom_tried += dom
        cb, cm = base(left, right).tag, mut(left, right).tag
        if cb != cm:
            moved += 1
            ex = (lo, ro, cb, cm)
            example = example or ex
            if dom:
                dom_moved += 1
                dom_example = dom_example or ex
# the metric itself: the objective of the plan kept, left 10.0 against a better right 5.0
kept_b = base(SimpleNamespace(objective_value=10.0), SimpleNamespace(objective_value=5.0)).objective_value
kept_m = mut(SimpleNamespace(objective_value=10.0), SimpleNamespace(objective_value=5.0)).objective_value

calls = diff_calls = 0


def _rec(left, right):
    global calls, diff_calls
    calls += 1
    rb = base(left, right)
    if mut(left, right) is not rb:
        diff_calls += 1
    return rb


mp = load_mp()
run_arms(mp, (F, _rec))

if dom_example is not None:
    example = dom_example
if example is not None:
    lo, ro, cb, cm = example
    result("example_input", f"left={lo!r},right={ro!r}")
    result("kept_baseline", cb)
    result("kept_mutant", cm)
result("kept_objective_baseline_left10_right5", kept_b)
result("kept_objective_mutant_left10_right5", kept_m)
result("grid_inputs_tried", tried, "count")
result("grid_inputs_moved", moved, "count")
result("domain_inputs_tried", dom_tried, "count")
result("domain_inputs_moved", dom_moved, "count")
result("production_calls", calls, "count")
result("production_calls_moved", diff_calls, "count")

# null arm: the same function re-compiled with the line unchanged moves nothing on the grid
nul = mutant(F, OLD, OLD)
null_moved = 0
for lo in VALUES:
    for ro in VALUES:
        left, right = SimpleNamespace(objective_value=lo, tag="left"), SimpleNamespace(objective_value=ro, tag="right")
        null_moved += base(left, right).tag != nul(left, right).tag
result("null_inputs_moved", null_moved, "count")

tail()
