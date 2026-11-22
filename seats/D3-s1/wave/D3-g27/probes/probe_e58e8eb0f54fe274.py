#!/usr/bin/env python3
# Metric: whether optimizer._apply_pins_to_bounds's (lower, upper) box differs between baseline and mutant over a pin x upper-bound x on-power grid and its production-domain subset (pins 1.0/0.0/NaN), the inverted boxes (lower > upper) each arm builds for on-pins, and over four production solves the calls that move, the plan power delta (kW) and the objective delta.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_e58e8eb0f54fe274.py
#   (from the repository root; $HOME/venv-ci on this box is /opt/hpo/venv-ci)
# EXPECTED RESULT example_input=pin=0.5,bounds=(0.0,0.3),min_on_power=0.0
# EXPECTED RESULT bounds_baseline=(0.0,0.3)
# EXPECTED RESULT bounds_mutant=(0.0,0.0)
# EXPECTED RESULT grid_inputs_tried=180 count
# EXPECTED RESULT grid_inputs_moved=16 count
# EXPECTED RESULT domain_inputs_tried=60 count
# EXPECTED RESULT domain_inputs_moved=0 count
# EXPECTED RESULT inverted_boxes_on_pins_baseline=0 count
# EXPECTED RESULT inverted_boxes_on_pins_mutant=0 count
# EXPECTED RESULT production_calls=4 count
# EXPECTED RESULT production_calls_moved=0 count
# EXPECTED RESULT production_calls_inverted_under_mutant=0 count
# EXPECTED RESULT production_pins_not_0_1_nan=0 count
# EXPECTED RESULT production_low_headroom_dhw_steps_pinned_on=0 count
# EXPECTED RESULT production_mutant_solve_error=none
# EXPECTED RESULT production_plan_max_abs_delta_kw=0 kW
# EXPECTED RESULT production_objective_max_abs_delta=0
# EXPECTED RESULT capped_step36_total_kw_baseline=0.1 kW
# EXPECTED RESULT capped_step36_total_kw_mutant=0.1 kW
# EXPECTED RESULT capped_step36_cap_kw=0.05 kW
# EXPECTED RESULT null_inputs_moved=0 count
# EXPECTED RESULT null_plan_max_abs_delta_kw=0 kW
#   (counts are exact and deterministic, the random grid seeded; kW and objective deltas are solver floats, re-taken to 1e-3 relative on another BLAS build; thread_factor, load1, swapins quoted, not expected)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g27 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython 3.14).
# Instrumented symbol: heatpump_optimizer.optimizer:_apply_pins_to_bounds, custom_components/heatpump_optimizer/optimizer.py:2417 `if pin >= 0.5:`.
# Perturbation: key e58e8eb0f54fe274 (CMP_BOUND), `if pin >= 0.5:` -> `if pin > 0.5:`, applied in memory: the function is
#   re-compiled from its own source with the one line replaced, in a copy of the module namespace; the production solves
#   see it through mock.patch.object on the module the suite imports (heatpump_optimizer.optimizer). Direction: moved inputs and inverted boxes rise from 0 under the mutant.
# Null control: the same function re-compiled with the line unchanged (the null_* RESULT lines), expected 0 moved.
# Count key: the bounds list _apply_pins_to_bounds returns, and the optimize() result built from it, never an input attribute.
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

OLD = '        if pin >= 0.5:'
NEW = '        if pin > 0.5:'

# ---- _apply_pins_to_bounds: a boundary grid plus a production reach count ----
F = "_apply_pins_to_bounds"
base = opt._apply_pins_to_bounds
mut = mutant(F, OLD, NEW)
PIN_VALUES = [0.0, 1.0, float("nan"), 0.5, 0.49999999999999994, 0.5000000000000001, -1.0, 2.0, float("inf")]
HIGHS = [0.0, 0.3, 0.8, 1.0, 3.0]
MIN_ON = [0.0, 0.8, 1.0, 5.0]


def inverted(bounds):
    return sum(1 for lo, hi in bounds if lo > hi)


tried = moved = dom_tried = dom_moved = 0
example = dom_example = None
for pin in PIN_VALUES:
    for hi in HIGHS:
        for mo in MIN_ON:
            b_in = [(0.0, hi)]
            ob, om = base(list(b_in), np.array([pin]), mo), mut(list(b_in), np.array([pin]), mo)
            tried += 1
            # the production domain: pins are PIN_ON 1.0 / PIN_OFF 0.0 / PIN_FREE NaN
            # (manual_plan.channel_pins, optimizer.py:565's np.where); bounds and floor >= 0
            dom = pin in (0.0, 1.0) or pin != pin
            dom_tried += dom
            if ob != om:
                moved += 1
                ex = (pin, hi, mo, ob[0], om[0])
                example = example or ex
                if dom:
                    dom_moved += 1
                    dom_example = dom_example or ex
direct_inv_base = direct_inv_mut = 0
for hi in HIGHS:
    for mo in MIN_ON:
        direct_inv_base += inverted(base([(0.0, hi)], np.array([1.0]), mo))
        direct_inv_mut += inverted(mut([(0.0, hi)], np.array([1.0]), mo))

# production reach: every call of the production solves, both arms on the same input
calls = diff_calls = inv_calls = 0
odd_pins = 0


def _rec(bounds, pins, min_on):
    global calls, diff_calls, inv_calls, odd_pins
    calls += 1
    ob_ = base(list(bounds), pins, min_on)
    om_ = mut(list(bounds), pins, min_on)
    if pins is not None:
        odd_pins += sum(1 for p in np.asarray(pins, dtype=float) if not (p in (0.0, 1.0) or p != p))
    if ob_ != om_:
        diff_calls += 1
    if inverted(om_):
        inv_calls += 1
    return ob_


mp = load_mp()
run_arms(mp, (F, _rec))
plans_b, full, p_max = production_solves(mp)
err = "none"
try:
    plans_m = run_arms(mp, (F, mut))[0]
    plan_delta = max(float(np.max(np.abs(np.asarray(plans_b[k].power_schedule) - np.asarray(plans_m[k].power_schedule))))
                     for k in plans_b)
    obj_delta = max(abs(float(plans_b[k].objective_value) - float(plans_m[k].objective_value)) for k in plans_b)

    def total36(plans):
        r = plans["capped_pinned"]
        return float(r.power_schedule[36]) + float(np.asarray(r.dhw_power_schedule)[36] if len(r.dhw_power_schedule) else 0.0)
    cap36_b, cap36_m = total36(plans_b), total36(plans_m)
except Exception as exc:  # the mutant arm's solve raising is itself the number
    plan_delta = obj_delta = cap36_b = cap36_m = float("nan")
    err = type(exc).__name__

if dom_example is not None:
    example = dom_example
if example is not None:
    pin, hi, mo, b0, m0 = example
    result("example_input", f"pin={pin!r},bounds=(0.0,{hi!r}),min_on_power={mo!r}")
    result("bounds_baseline", f"({b0[0]!r},{b0[1]!r})")
    result("bounds_mutant", f"({m0[0]!r},{m0[1]!r})")
result("grid_inputs_tried", tried, "count")
result("grid_inputs_moved", moved, "count")
result("domain_inputs_tried", dom_tried, "count")
result("domain_inputs_moved", dom_moved, "count")
result("inverted_boxes_on_pins_baseline", direct_inv_base, "count")
result("inverted_boxes_on_pins_mutant", direct_inv_mut, "count")
result("production_calls", calls, "count")
result("production_calls_moved", diff_calls, "count")
result("production_calls_inverted_under_mutant", inv_calls, "count")
result("production_pins_not_0_1_nan", odd_pins, "count")
result("production_low_headroom_dhw_steps_pinned_on", len(full), "count")
result("production_mutant_solve_error", err)
result("production_plan_max_abs_delta_kw", f"{plan_delta:.6g}", "kW")
result("production_objective_max_abs_delta", f"{obj_delta:.6g}")
result("capped_step36_total_kw_baseline", f"{cap36_b:.6g}", "kW")
result("capped_step36_total_kw_mutant", f"{cap36_m:.6g}", "kW")
result("capped_step36_cap_kw", "0.05", "kW")

# null arm: the same function re-compiled with the line unchanged moves nothing, on the grid or the plans
nul = mutant(F, OLD, OLD)
null_moved = sum(base([(0.0, hi)], np.array([pin]), mo) != nul([(0.0, hi)], np.array([pin]), mo)
                 for pin in PIN_VALUES for hi in HIGHS for mo in MIN_ON)
plans_n = run_arms(mp, (F, nul))[0]
null_plan = max(float(np.max(np.abs(np.asarray(plans_b[k].power_schedule) - np.asarray(plans_n[k].power_schedule))))
                for k in plans_b)
result("null_inputs_moved", null_moved, "count")
result("null_plan_max_abs_delta_kw", f"{null_plan:.6g}", "kW")

tail()
