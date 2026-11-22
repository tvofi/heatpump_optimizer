#!/usr/bin/env python3
# Metric: learned quarter factor of hour 3 quarter 0 after one quarter day folded; and the stored factor after PriceShapeModel.from_dict; printed per input for the baseline and the mutant arm.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_cc96ce9e391ca6f2.py
# EXPECTED RESULT qf_h3q0_negative_quarters_q0_30x_baseline=3.368421
# EXPECTED RESULT qf_h3q0_negative_quarters_q0_30x_mutant=3.657143
# EXPECTED RESULT qf_h3q0_negative_quarters_q0_5x_baseline=3.368421
# EXPECTED RESULT qf_h3q0_negative_quarters_q0_5x_mutant=3.478261
# EXPECTED RESULT qf_h3q0_q0_exactly_4x_baseline=3.254237
# EXPECTED RESULT qf_h3q0_q0_exactly_4x_mutant=3.254237
# EXPECTED RESULT null_qf_h3q0_nonnegative_max_possible_4x_baseline=3.368421
# EXPECTED RESULT null_qf_h3q0_nonnegative_max_possible_4x_mutant=3.368421
# EXPECTED RESULT null_qf_h3q0_ramp_baseline=0.9
# EXPECTED RESULT null_qf_h3q0_ramp_mutant=0.9
# EXPECTED RESULT qf_h3q0_inputs_moved=2 count
# EXPECTED RESULT null_delta=0 count
# EXPECTED RESULT inputs_tried=negative_quarters_q0_30x,negative_quarters_q0_5x,q0_exactly_4x,nonnegative_max_possible_4x,ramp
# EXPECTED RESULT stored_q0_stored_ratio_20_baseline=3.129584
# EXPECTED RESULT stored_q0_stored_ratio_20_mutant=3.2
# EXPECTED RESULT null_stored_q0_stored_ratio_2_baseline=0.7
# EXPECTED RESULT null_stored_q0_stored_ratio_2_mutant=0.7
# EXPECTED RESULT stored_q0_inputs_moved=1 count
# EXPECTED RESULT null_delta=0 count
# EXPECTED RESULT inputs_tried=stored_ratio_20,stored_ratio_2
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g30 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:QUARTER_FACTOR_MAX (read by PriceShapeModel.observe_day_quarters' np.clip and _in_domain in from_dict), price_model.py line 85.
# Perturbation: key cc96ce9e391ca6f2 (CONST), line 85 `QUARTER_FACTOR_MAX = 4.0` -> `QUARTER_FACTOR_MAX = 8.0`, applied in memory: the
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


OLD = 'QUARTER_FACTOR_MAX = 4.0'
NEW = 'QUARTER_FACTOR_MAX = 8.0'
LINE = 85

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
def qf(mod, q):
    return round(fold(mod, [(WEEKDAYS[0], q)]).model.quarter_factors[0][12], 6)
spike = quarters(DAY); spike[12:16] = [3.0, -1.0, -1.0, -0.6]     # negative spot quarters: hour mean 0.1, q0 at 30x
mild = quarters(DAY); mild[12:16] = [1.2, -0.2, 0.1, 0.1]          # hour mean 0.3, q0 at 4x..8x (=4.0x)
mild2 = quarters(DAY); mild2[12:16] = [1.5, -0.3, 0.0, 0.0]        # hour mean 0.3, q0 at 5x
compare("qf_h3q0", qf, {"negative_quarters_q0_30x": spike, "negative_quarters_q0_5x": mild2, "q0_exactly_4x": mild},
        nulls={"nonnegative_max_possible_4x": quarters(DAY)[:12] + [0.0, 0.0, 0.0, 4.0][::-1] + quarters(DAY)[16:], "ramp": quarters(DAY)})
def stored(mod, row):
    data = {"quarter_factors": [row + [1.0] * 92, [1.0] * 96]}
    return round(mod.PriceShapeModel.from_dict(data).quarter_factors[0][0], 6)
compare("stored_q0", stored, {"stored_ratio_20": [3.2, 0.16, 0.32, 0.32]}, nulls={"stored_ratio_2": [0.7, 0.9, 1.0, 1.4]})

footer()
