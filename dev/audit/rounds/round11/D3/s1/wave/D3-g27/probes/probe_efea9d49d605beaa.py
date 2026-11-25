#!/usr/bin/env python3
# Metric: whether optimizer._mark_manual_reasons's relabelled reasons differ between baseline and mutant over a reason x pin grid (with length mismatches) and its production-domain subset (equal lengths, pins 1.0/0.0/NaN), and over four production solves the published space/DHW reasons equal to REASON_MANUAL and the reason labels that change.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g27/probes/probe_efea9d49d605beaa.py
#   (from the repository root; $HOME/venv-ci on this box is /opt/hpo/venv-ci)
# EXPECTED RESULT example_input=reasons=['idle_coasting'],pins=[0.5]
# EXPECTED RESULT output_baseline=('ok',('manual_plan',))
# EXPECTED RESULT output_mutant=('ok',('idle_coasting',))
# EXPECTED RESULT grid_inputs_tried=54 count
# EXPECTED RESULT grid_inputs_moved=2 count
# EXPECTED RESULT domain_inputs_tried=18 count
# EXPECTED RESULT domain_inputs_moved=0 count
# EXPECTED RESULT production_calls=8 count
# EXPECTED RESULT production_calls_len_mismatch=0 count
# EXPECTED RESULT production_calls_moved=0 count
# EXPECTED RESULT production_manual_labels_baseline=3 count
# EXPECTED RESULT production_manual_labels_mutant=3 count
# EXPECTED RESULT production_reason_labels_changed=0 count
# EXPECTED RESULT null_inputs_moved=0 count
# EXPECTED RESULT null_reason_labels_changed=0 count
#   (counts are exact and deterministic, the random grid seeded; kW and objective deltas are solver floats, re-taken to 1e-3 relative on another BLAS build; thread_factor, load1, swapins quoted, not expected)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g27 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, Linux, venv-ci CPython 3.14).
# Instrumented symbol: heatpump_optimizer.optimizer:_mark_manual_reasons, custom_components/heatpump_optimizer/optimizer.py:2494 `if _pin_is_free(pin) or pin < 0.5:`.
# Perturbation: key efea9d49d605beaa (CMP_BOUND), `if _pin_is_free(pin) or pin < 0.5:` -> `if _pin_is_free(pin) or pin <= 0.5:`, applied in memory: the function is
#   re-compiled from its own source with the one line replaced, in a copy of the module namespace; the production solves
#   see it through mock.patch.object on the module the suite imports (heatpump_optimizer.optimizer). Direction: moved inputs and changed labels rise from 0 under the mutant.
# Null control: the same function re-compiled with the line unchanged (the null_* RESULT lines), expected 0 moved.
# Count key: the reason list _mark_manual_reasons returns, and the published space_reasons/dhw_reasons, never an input attribute.
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

OLD = '        if _pin_is_free(pin) or pin < 0.5:'
NEW = '        if _pin_is_free(pin) or pin <= 0.5:'

# ---- _mark_manual_reasons: a grid plus the published reasons of the production solves ----
F = "_mark_manual_reasons"
base = opt._mark_manual_reasons
mut = mutant(F, OLD, NEW)
MANUAL = opt.REASON_MANUAL
REASONS = [opt.REASON_IDLE, opt.REASON_COMFORT_FLOOR, opt.REASON_LEGIONELLA, "idle_coasting", "cheap_price", MANUAL]
PIN_VALUES = [0.0, 1.0, float("nan"), 0.5, 0.49999999999999994, 0.5000000000000001]


def call(fn, reasons, pins):
    try:
        return ("ok", tuple(fn(list(reasons), pins)))
    except Exception as exc:
        return ("raised", type(exc).__name__)


tried = moved = dom_tried = dom_moved = 0
example = dom_example = None
cases = []
for r in REASONS:
    for p in PIN_VALUES:
        cases.append(([r], np.array([p])))
# length mismatches (pins shorter / longer than the reasons)
for r in REASONS:
    cases.append(([r, r, r], np.array([1.0])))
    cases.append(([r], np.array([1.0, 0.0, 1.0])))
    cases.append(([r, r], np.array([], dtype=float)))
for reasons, pins in cases:
    tried += 1
    # the production domain: equal lengths (both are the horizon's n_steps) and pins in {1.0, 0.0, NaN}
    dom = len(reasons) == len(pins) and all(p in (0.0, 1.0) or p != p for p in pins)
    dom_tried += dom
    ob, om = call(base, reasons, pins), call(mut, reasons, pins)
    if ob != om:
        moved += 1
        ex = (list(reasons), [float(p) for p in pins], ob, om)
        example = example or ex
        if dom:
            dom_moved += 1
            dom_example = dom_example or ex

calls = diff_calls = len_mismatch = 0


def _rec(reasons, pins):
    global calls, diff_calls, len_mismatch
    calls += 1
    if pins is not None and len(pins) != len(reasons):
        len_mismatch += 1
    ob_ = base(list(reasons), pins)
    if call(mut, reasons, pins) != ("ok", tuple(ob_)):
        diff_calls += 1
    return ob_


mp = load_mp()
run_arms(mp, (F, _rec))
plans_b = production_solves(mp)[0]
plans_m = run_arms(mp, (F, mut))[0]


def manual_labels(plans):
    return sum(list(plans[k].space_reasons).count(MANUAL) + list(plans[k].dhw_reasons).count(MANUAL) for k in plans)


def label_diff(pb, pm):
    return sum(sum(a != b for a, b in zip(pb[k].space_reasons, pm[k].space_reasons))
               + sum(a != b for a, b in zip(pb[k].dhw_reasons, pm[k].dhw_reasons)) for k in pb)


if dom_example is not None:
    example = dom_example
if example is not None:
    r, p, ob, om = example
    result("example_input", f"reasons={r!r},pins={p!r}")
    result("output_baseline", repr(ob).replace(" ", ""))
    result("output_mutant", repr(om).replace(" ", ""))
result("grid_inputs_tried", tried, "count")
result("grid_inputs_moved", moved, "count")
result("domain_inputs_tried", dom_tried, "count")
result("domain_inputs_moved", dom_moved, "count")
result("production_calls", calls, "count")
result("production_calls_len_mismatch", len_mismatch, "count")
result("production_calls_moved", diff_calls, "count")
result("production_manual_labels_baseline", manual_labels(plans_b), "count")
result("production_manual_labels_mutant", manual_labels(plans_m), "count")
result("production_reason_labels_changed", label_diff(plans_b, plans_m), "count")

# null arm: the same function re-compiled with the line unchanged moves nothing, on the grid or the plans
nul = mutant(F, OLD, OLD)
null_moved = sum(call(base, r, p) != call(nul, r, p) for r, p in cases)
plans_n = run_arms(mp, (F, nul))[0]
result("null_inputs_moved", null_moved, "count")
result("null_reason_labels_changed", label_diff(plans_b, plans_n), "count")

tail()
