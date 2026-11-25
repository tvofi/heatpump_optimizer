#!/usr/bin/env python3
# Metric: the learned solar-aperture scale (_solar_aperture["scale"]) after exactly SOLAR_APERTURE_MIN_SAMPLES (30)
#   sunny-step folds with varying irradiance (200..780 W/m2) and a residual implying 1.5x the modelled solar gain.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_d3cad40ffce9b765.py
# EXPECTED RESULT scale_baseline_at_min=2.000000 ratio  (the first correction is taken at sample 30; cov/var step clipped to SOLAR_APERTURE_MAX)
# EXPECTED RESULT scale_mutant_at_min=1.000000 ratio  (no correction until sample 31)
# EXPECTED RESULT scale_baseline_at_min_plus_1 and scale_mutant_at_min_plus_1: both moved off 1.0
# EXPECTED RESULT null_baseline=1.000000 ratio, null_mutant=1.000000 ratio  (29 folds: below the minimum in both arms)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_solar_aperture, line 9402.
# Perturbation: key d3cad40ffce9b765 (CMP_BOUND), line 9402 `if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:` ->
#   `if m["n"] > SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:`, applied in memory. Direction: scale at sample 30 back to 1.0.
# Null control: 29 folds (below the minimum in both arms).
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
from heatpump_optimizer import coordinator as co  # noqa: E402

BASE = L.baseline("_fold_solar_aperture")
MUT = L.mutant("_fold_solar_aperture", 'if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:',
               'if m["n"] > SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:')
N = co.SOLAR_APERTURE_MIN_SAMPLES
print(f"RESULT min_samples={N} count")


def scale_after(fn, folds, dt_h=0.25):
    c = L.coord(solar_aperture_learning_enabled=True)
    cap = co._zone_capacity(c._thermal_params)
    for i in range(folds):
        irr = 200.0 + 20.0 * i
        st = dataclasses.replace(c._current_state, solar_radiation=irr)
        y = 1.5 * c._thermal_model.compute_solar_gain(irr)  # true aperture 1.5x the modelled one
        fn(c, st, y * dt_h / cap, dt_h)
    return float(c._solar_aperture["scale"])


print(f"RESULT scale_baseline_at_min={scale_after(BASE, N):.6f} ratio")
print(f"RESULT scale_mutant_at_min={scale_after(MUT, N):.6f} ratio")
print(f"RESULT scale_baseline_at_min_plus_1={scale_after(BASE, N + 1):.6f} ratio")
print(f"RESULT scale_mutant_at_min_plus_1={scale_after(MUT, N + 1):.6f} ratio")
print(f"RESULT null_baseline={scale_after(BASE, N - 1):.6f} ratio")
print(f"RESULT null_mutant={scale_after(MUT, N - 1):.6f} ratio")
L.footer()
