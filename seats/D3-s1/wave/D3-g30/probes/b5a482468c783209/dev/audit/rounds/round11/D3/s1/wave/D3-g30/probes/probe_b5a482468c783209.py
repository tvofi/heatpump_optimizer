#!/usr/bin/env python3
# Metric: days[weekday] after one hourly day folded through PriceShapeLearner.fold (1 = the day was learned); printed per input for the baseline and the mutant arm.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g30/probes/probe_b5a482468c783209.py
# EXPECTED RESULT mean_is_exact=1 count
# EXPECTED RESULT days_learned_mean_exactly_1e-6_baseline=0
# EXPECTED RESULT days_learned_mean_exactly_1e-6_mutant=1
# EXPECTED RESULT null_days_learned_mean_zero_baseline=0
# EXPECTED RESULT null_days_learned_mean_zero_mutant=0
# EXPECTED RESULT null_days_learned_winter_day_baseline=1
# EXPECTED RESULT null_days_learned_winter_day_mutant=1
# EXPECTED RESULT null_days_learned_mean_2e-6_baseline=1
# EXPECTED RESULT null_days_learned_mean_2e-6_mutant=1
# EXPECTED RESULT days_learned_inputs_moved=1 count
# EXPECTED RESULT null_delta=0 count
# EXPECTED RESULT inputs_tried=mean_exactly_1e-6,mean_zero,winter_day,mean_2e-6
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g30 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB, CPython 3.14 venv-ci).
# Instrumented symbol: custom_components.heatpump_optimizer.price_model:PriceShapeModel.observe_day (mean guard; caller PriceShapeLearner.fold), price_model.py line 207.
# Perturbation: key b5a482468c783209 (CMP_BOUND), line 207 `if mean <= 1e-6:` -> `if mean < 1e-6:`, applied in memory: the
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


OLD = '        if mean <= 1e-6:'
NEW = '        if mean < 1e-6:'
LINE = 207

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
edge = [0.0] * 12 + [2e-6] * 12
print(f"RESULT mean_is_exact={int(float(np.mean(np.asarray(edge))) == 1e-6)} count")
def days(mod, day):
    return fold(mod, [(WEEKDAYS[0], day)]).model.days[0]
compare("days_learned", days, {"mean_exactly_1e-6": edge}, nulls={"mean_zero": [0.0] * 24, "winter_day": DAY, "mean_2e-6": [2e-6] * 24})

footer()
