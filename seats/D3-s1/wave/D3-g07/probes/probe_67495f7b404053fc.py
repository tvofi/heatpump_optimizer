#!/usr/bin/env python3
# Metric: count of ForecastArrays fields (10 per call) that differ (array_equal, NaN-aware) between the baseline and
#   the mutant padding loop `while len(series) <= n_steps`, over a grid of forecast lengths, Open-Meteo on/off and
#   two consecutive calls on one coordinator (to catch a padded list persisting into the next cycle).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_67495f7b404053fc.py
# EXPECTED RESULT cases_tried=16 count  (weather forecast 0/1/10/48 h x solar series 0/48 h x Open-Meteo off/on,
#   each compared on a first and a second call of the same coordinator)
# EXPECTED RESULT fields_differing=0 count  (every series is sliced [:n_steps] before it becomes an array, and the
#   series are fresh lists per call, so the extra padded element never leaves the function)
# EXPECTED RESULT padded_len_baseline=96, padded_len_mutant=97  (positive arm: the outdoor list's length right after the
#   padding loop, read through a hook on the loop's list: the mutant does run and does pad one more)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._forecast_arrays, line 7477.
# Perturbation: key 67495f7b404053fc (CMP_BOUND), line 7477 `while len(series) < n_steps:` -> `while len(series) <= n_steps:`,
#   in memory. Direction: one more padded element per series (internal only).
# Null control: the positive arm above.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import _probe_lib as L  # noqa: E402
import probe_fa_common as F  # noqa: E402
import inspect  # noqa: E402
import textwrap  # noqa: E402

BASE = L.baseline("_forecast_arrays")
MUT = L.mutant("_forecast_arrays", "while len(series) < n_steps:", "while len(series) <= n_steps:")
FIELDS = ("prices", "outdoor_temps", "wind_speeds", "precipitation", "solar_radiation", "price_known", "pv_surplus",
          "price_sigma", "humidity", "snowfall")


def eq(a, b):
    if a is None or b is None:
        return a is b
    a, b = np.asarray(a), np.asarray(b)
    return a.shape == b.shape and bool(np.array_equal(a, b, equal_nan=a.dtype.kind == "f"))


def build(hours_w, hours_s, om_on):
    c = F.build(open_meteo_rh=90.0 if om_on else None)
    c._weather_forecast = c._weather_forecast[:hours_w]
    c._solar_radiation_forecast = c._solar_radiation_forecast[:hours_s]
    return c


cases = differ = 0
for hw in (0, 1, 10, 48):
    for hs in (0, 48):
        for om_on in (False, True):
            cb, cm = build(hw, hs, om_on), build(hw, hs, om_on)
            for _call in range(2):
                cases += 1 if _call == 0 else 0
                ab, am = F.arrays(BASE, cb), F.arrays(MUT, cm)
                for f in FIELDS:
                    if not eq(getattr(ab, f), getattr(am, f)):
                        differ += 1
                        print(f"DIFF hw={hw} hs={hs} om={om_on} call={_call} field={f}")
print(f"RESULT cases_tried={cases} count")
print(f"RESULT fields_differing={differ} count")
seen = {}
for tag in ("baseline", "mutant"):
    src = "while len(series) <= n_steps:" if tag == "mutant" else "while len(series) < n_steps:"
    # the arm's loop condition plus a hook recording len(outdoor) right after the padding loop
    lines = inspect.getsource(L.baseline("_forecast_arrays")).splitlines(keepends=True)
    out = []
    for ln in lines:
        s = ln.strip()
        ind = ln[: len(ln) - len(ln.lstrip())]
        if s == "while len(series) < n_steps:":
            ln = ind + src + "\n"
        elif s == "snowfall = [0.0] * n_steps":
            ln = ind + "snowfall = [0.0] * n_steps; _seen(len(outdoor))\n"
        out.append(ln)
    ns = dict(L.co.__dict__)
    ns["_seen"] = lambda n, t=tag: seen.__setitem__(t, n)
    exec(compile(textwrap.dedent("".join(out)), L.co.__file__, "exec"), ns)
    F.arrays(ns["_forecast_arrays"], build(10, 48, False))
print(f"RESULT padded_len_baseline={seen['baseline']} count")
print(f"RESULT padded_len_mutant={seen['mutant']} count")
L.footer()
