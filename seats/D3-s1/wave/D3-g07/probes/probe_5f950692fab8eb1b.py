#!/usr/bin/env python3
# Metric: max of ForecastArrays.humidity (%) from _forecast_arrays() with an available Open-Meteo client, per input arm.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_5f950692fab8eb1b.py
# EXPECTED RESULT reach_calls=96 count  (line 7492 executes once per step when Open-Meteo has humidity: the probe reaches it)
# EXPECTED RESULT parsed150_baseline=85.0 %, parsed150_mutant=85.0 %  (the production parser drops 150 > max_value
#   100, so humidity_for is None and the entity's 85 % stands in both arms)
# EXPECTED RESULT parsed95_baseline=95.0 %, parsed95_mutant=95.0 %  (an in-range value: the clip is the identity)
# EXPECTED RESULT parsedneg_baseline=85.0 %, parsedneg_mutant=85.0 %  (-5 dropped by the parser)
# EXPECTED RESULT parsednan_baseline=85.0 %, parsednan_mutant=85.0 %  (NaN dropped by the parser)
# EXPECTED RESULT production_inputs_differing=0 count
# EXPECTED RESULT bypass_baseline=100.0 %, bypass_mutant=150.0 %  (positive arm: a 150 % series injected PAST the
#   parser, an input no production path builds, shows the probe would see the clamp act)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._forecast_arrays, line 7492
#   (fed by open_meteo:OpenMeteoSolar.humidity_for over the series open_meteo:_parse_block builds with max_value=100).
# Perturbation: key 5f950692fab8eb1b (CLAMP_DROP), line 7492 `humidity[i] = float(np.clip(rh, 0.0, 100.0))` ->
#   `humidity[i] = float((rh))`, in memory. Direction: humidity up past 100 only for an out-of-range rh.
# Null control: the in-range 95 % arm.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import _probe_lib as L  # noqa: E402
import probe_fa_common as F  # noqa: E402
from heatpump_optimizer import open_meteo as om  # noqa: E402

BASE = L.baseline("_forecast_arrays")
MUT = L.mutant("_forecast_arrays", "humidity[i] = float(np.clip(rh, 0.0, 100.0))", "humidity[i] = float((rh))")
CLIP = L.mutant("_forecast_arrays", "humidity[i] = float(np.clip(rh, 0.0, 100.0))",
                "humidity[i] = float(_reach(np.clip(rh, 0.0, 100.0)))")
calls = []
CLIP.__globals__["_reach"] = lambda v: (calls.append(v), v)[1]
F.arrays(CLIP, F.build(open_meteo_rh=95.0))
print(f"RESULT reach_calls={len(calls)} count")
differ = 0
for tag, rh in (("parsed150", 150.0), ("parsed95", 95.0), ("parsedneg", -5.0), ("parsednan", float("nan"))):
    b = float(np.max(F.arrays(BASE, F.build(open_meteo_rh=rh)).humidity))
    m = float(np.max(F.arrays(MUT, F.build(open_meteo_rh=rh)).humidity))
    differ += int(b != m)
    print(f"RESULT {tag}_baseline={b:.1f} %")
    print(f"RESULT {tag}_mutant={m:.1f} %")
print(f"RESULT production_inputs_differing={differ} count")


def bypass(fn):
    c = F.build(open_meteo_rh=95.0)
    block = {"time": [t.strftime("%Y-%m-%dT%H:%M") for t in c._open_meteo._humidity.times],
             om._VARIABLE_HUMIDITY: [150.0] * len(c._open_meteo._humidity.times)}
    c._open_meteo._humidity = om._parse_block(block, om._VARIABLE_HUMIDITY, max_value=1000.0)
    return float(np.max(F.arrays(fn, c).humidity))


print(f"RESULT bypass_baseline={bypass(BASE):.1f} %")
print(f"RESULT bypass_mutant={bypass(MUT):.1f} %")
L.footer()
