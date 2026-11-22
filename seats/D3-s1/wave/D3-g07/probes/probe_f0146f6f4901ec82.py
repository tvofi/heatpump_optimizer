#!/usr/bin/env python3
# Metric: mean of ForecastArrays.humidity (%) over the 96-step horizon from _forecast_arrays(), with the weather entity
#   forecasting 85 % and an available Open-Meteo client (production parser) forecasting 95 % for every hour.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_f0146f6f4901ec82.py
# EXPECTED RESULT humidity_mean_baseline=95.0 %  (Open-Meteo's hourly humidity overlays the entity's)
# EXPECTED RESULT humidity_mean_mutant=85.0 %  (Open-Meteo humidity never copied: the defrost derate reads the entity's)
# EXPECTED RESULT null_baseline=85.0 %, null_mutant=85.0 %  (Open-Meteo also forecasting 85 %)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._forecast_arrays, line 7491.
# Perturbation: key f0146f6f4901ec82 (GUARD_OFF), line 7491 `if rh is not None:` -> `if False:`, in memory.
#   Direction: humidity down from 95 to the entity's 85.
# Null control: Open-Meteo forecasting the entity's own 85 %.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import _probe_lib as L  # noqa: E402
import probe_fa_common as F  # noqa: E402

BASE = L.baseline("_forecast_arrays")
MUT = L.mutant("_forecast_arrays", "if rh is not None:", "if False:")
for tag, rh in (("humidity_mean", 95.0), ("null", 85.0)):
    b = F.arrays(BASE, F.build(open_meteo_rh=rh)).humidity
    m = F.arrays(MUT, F.build(open_meteo_rh=rh)).humidity
    sfx = ("_baseline", "_mutant")
    print(f"RESULT {tag}{sfx[0]}={float(np.mean(b)):.1f} %")
    print(f"RESULT {tag}{sfx[1]}={float(np.mean(m)):.1f} %")
L.footer()
