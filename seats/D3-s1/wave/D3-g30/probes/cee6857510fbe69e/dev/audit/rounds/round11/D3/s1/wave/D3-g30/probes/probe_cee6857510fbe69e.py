#!/usr/bin/env python3
# Metric: quarter_factors[weekday][12] after observe_day_quarters: through production (fold, from_dict-restored) and on a hand-built model whose stored factors are negative; printed per input for the baseline and the mutant arm.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_cee6857510fbe69e.py
# EXPECTED RESULT qf12_production_zero_price_hour_baseline=1.0
# EXPECTED RESULT qf12_production_zero_price_hour_mutant=1.0
# EXPECTED RESULT qf12_production_negative_hour_two_days_baseline=0.912
# EXPECTED RESULT qf12_production_negative_hour_two_days_mutant=0.912
# EXPECTED RESULT qf12_production_spike_then_zero_baseline=3.1238193282717797
# EXPECTED RESULT qf12_production_spike_then_zero_mutant=3.1238193282717797
# EXPECTED RESULT qf12_production_inputs_moved=0 count
# EXPECTED RESULT null_delta=0 count
# EXPECTED RESULT inputs_tried=zero_price_hour,negative_hour_two_days,spike_then_zero
# EXPECTED RESULT qf12_from_dict_stored_negative_baseline=1.0
# EXPECTED RESULT qf12_from_dict_stored_negative_mutant=1.0
# EXPECTED RESULT qf12_from_dict_stored_zero_baseline=1.0
# EXPECTED RESULT qf12_from_dict_stored_zero_mutant=1.0
# EXPECTED RESULT qf12_from_dict_inputs_moved=0 count
# EXPECTED RESULT null_delta=0 count
# EXPECTED RESULT inputs_tried=stored_negative,stored_zero
# EXPECTED RESULT qf12_handbuilt_negative_bypassing_from_dict_baseline=-760000.0
# EXPECTED RESULT qf12_handbuilt_negative_bypassing_from_dict_mutant=1.0
# EXPECTED RESULT qf12_handbuilt_inputs_moved=1 count
# EXPECTED RESULT null_delta=0 count
# EXPECTED RESULT inputs_tried=negative_bypassing_from_dict
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g30 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:PriceShapeModel.observe_day_quarters (per-hour renormalisation floor; caller PriceShapeLearner.fold), price_model.py line 275.
# Perturbation: key cee6857510fbe69e (CLAMP_DROP), line 275 `updated = updated / np.maximum(updated.mean(axis=1, keepdims=True), 1e-6)` -> `updated = updated / (updated.mean(axis=1, keepdims=True))`, applied in memory: the
#   module is re-executed from its own source with that one line replaced (never on disk); the mutant arm uses that copy.
#   Direction: see the EXPECTED lines (baseline value -> mutant value); `<metric>_inputs_moved` counts inputs that separate the arms.
# Null control: the null_* inputs, where the mutated line is inert or takes the same branch, must give null_delta=0.
# Count key: the value the production symbol returns or stores (never an input attribute).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import math, sys, time, types
from datetime import datetime, timedelta
from pathlib import Path

_T0P, _T0T = time.process_time(), time.thread_time()


def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


OLD = '        updated = updated / np.maximum(updated.mean(axis=1, keepdims=True), 1e-6)'
NEW = '        updated = updated / (updated.mean(axis=1, keepdims=True))'
LINE = 275

ROOT = repo_root(__file__)
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
from custom_components.heatpump_optimizer import price_model as B  # noqa: E402


def mutant_module():
    """price_model re-executed from its own source with line LINE replaced (the one-line mutant), in memory."""
    src = Path(B.__file__).read_text().splitlines(keepends=True)
    assert src[LINE - 1].rstrip("\n") == OLD, f"anchor moved: line {LINE} is {src[LINE - 1]!r}"
    src[LINE - 1] = NEW + "\n"
    name = "custom_components.heatpump_optimizer._price_model_mutant"
    mod = types.ModuleType(name)
    mod.__package__ = "custom_components.heatpump_optimizer"
    mod.__file__ = B.__file__
    sys.modules[name] = mod
    exec(compile("".join(src), B.__file__, "exec"), mod.__dict__)
    return mod


M = mutant_module()
ARMS = (("baseline", B), ("mutant", M))
# Weekdays (2026-11-16 Mon .. 2026-11-20 Fri, 2026-11-23 Mon ..) and a weekday noon for queries.
WEEKDAYS = ["2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19", "2026-11-20",
            "2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26", "2026-11-27", "2026-11-30"]
WED = datetime(2026, 11, 18, 12, 0)
# A realistic Nordic winter weekday, SEK/kWh by hour.
DAY = [0.30, 0.25, 0.20, 0.20, 0.22, 0.35, 0.80, 1.20, 1.10, 0.90, 0.70, 0.60,
       0.55, 0.50, 0.60, 0.80, 1.10, 1.50, 1.40, 1.00, 0.80, 0.60, 0.45, 0.35]
DAY2 = list(reversed(DAY))
FLAT = [1.0] * 24


def quarters(hourly, ramp=(0.9, 0.97, 1.03, 1.1)):
    return [p * r for p in hourly for r in ramp]


def entries(day, values):
    """Tibber-style price entries for one local day: 24 hourly or 96 quarter values."""
    step = 60 if len(values) == 24 else 15
    t0 = datetime.fromisoformat(f"{day}T00:00:00")
    return [{"starts_at": (t0 + timedelta(minutes=step * i)).isoformat(), "total": v} for i, v in enumerate(values)]


def fold(mod, days):
    """A fresh production PriceShapeLearner with each (day, values) folded through PriceShapeLearner.fold."""
    learner = mod.PriceShapeLearner()
    for d, v in days:
        learner.fold(entries(d, v))
    return learner


def same(a, b):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def compare(metric, fn, inputs, nulls=()):
    """fn(mod, inp) -> value per arm; RESULT lines, moved count over inputs, null_delta over nulls."""
    moved, tried = 0, []
    for name, inp in inputs.items():
        vals = {}
        for arm, mod in ARMS:
            try:
                vals[arm] = fn(mod, inp)
            except Exception as exc:  # the exception is the outcome
                vals[arm] = f"raises {type(exc).__name__}"
            print(f"RESULT {metric}_{name}_{arm}={vals[arm]!r}")
        moved += not same(vals["baseline"], vals["mutant"])
        tried.append(name)
    nd = 0
    for name, inp in (nulls or {}).items():
        vals = {}
        for arm, mod in ARMS:
            try:
                vals[arm] = fn(mod, inp)
            except Exception as exc:
                vals[arm] = f"raises {type(exc).__name__}"
            print(f"RESULT null_{metric}_{name}_{arm}={vals[arm]!r}")
        nd += not same(vals["baseline"], vals["mutant"])
        tried.append(name)
    print(f"RESULT {metric}_inputs_moved={moved} count")
    print(f"RESULT null_delta={nd} count")
    print(f"RESULT inputs_tried={','.join(tried)}")
    return moved, nd


def footer():
    tt = time.thread_time() - _T0T
    pc = time.process_time() - _T0P
    try:
        load1 = os.getloadavg()[0]
    except OSError:
        load1 = float("nan")
    swapins = 0
    try:
        for line in Path("/proc/vmstat").read_text().splitlines():
            if line.startswith("pswpin "):
                swapins = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT thread_factor={pc / tt if tt > 0 else 1.0:.3f}")
    print(f"RESULT load1={load1:.2f}")
    print(f"RESULT swapins={swapins}")

# ---- the measurement ----
zero_hour = quarters(DAY); zero_hour[12:16] = [0.0, 0.0, 0.0, 0.0]
negh = quarters(DAY); negh[12:16] = [-0.5, -0.5, -0.5, -0.5]
spike = quarters(DAY); spike[12:16] = [3.0, -1.0, -1.0, -0.6]
def prod(mod, days):
    return fold(mod, list(zip(WEEKDAYS, days))).model.quarter_factors[0][12]
compare("qf12_production", prod, {"zero_price_hour": [zero_hour], "negative_hour_two_days": [quarters(DAY), negh],
                                  "spike_then_zero": [spike, zero_hour, spike]})
def restored(mod, row):
    m = mod.PriceShapeModel.from_dict({"quarter_factors": [[1.0] * 12 + row + [1.0] * 80, [1.0] * 96], "quarter_days": [2, 0]})
    m.observe_day_quarters(WED, zero_hour)
    return m.quarter_factors[0][12]
compare("qf12_from_dict", restored, {"stored_negative": [-1.0] * 4, "stored_zero": [0.0] * 4})
def handbuilt(mod, row):
    m = mod.PriceShapeModel(quarter_factors=[[1.0] * 12 + row + [1.0] * 80, [1.0] * 96], quarter_days=[2, 0])
    m.observe_day_quarters(WED, zero_hour)
    return m.quarter_factors[0][12]
compare("qf12_handbuilt", handbuilt, {"negative_bypassing_from_dict": [-1.0] * 4})

footer()
