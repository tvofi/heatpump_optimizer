#!/usr/bin/env python3
# Metric: the learned solar-aperture scale after one fold whose EWMA variance update lands EXACTLY on 1e-6 (the tie of
#   the `var > 1e-6` guard), from a moment state n=100, cov=2e-6, x == mx (so dx = 0 and var' = var - a*var).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g07/probes/probe_e163f6fbc359cd4c.py
# EXPECTED RESULT var_after=1e-06 (exact float equality, tie_found=1)
# EXPECTED RESULT scale_baseline_tie=1.000000 ratio  (var > 1e-6 is False at the tie: no step)
# EXPECTED RESULT scale_mutant_tie=2.000000 ratio  (step cov/var ~ 1.96, clipped to SOLAR_APERTURE_MAX 2.0)
# EXPECTED RESULT null_baseline=null_mutant  (var one float above the tie: both arms step alike)
# EXPECTED RESULT realistic_sequences_tried=36 count, realistic_sequences_differing=0 count  (fold sequences of
#   31/60/200 sunny steps, irradiance ramps from 150/300/600 W/m2 in 5/20 W/m2 steps, residual ratio 0.6/1.5: the EWMA
#   variance never lands exactly on 1e-6, so both arms publish the same scale)
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g07 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB RAM).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_solar_aperture, line 9402.
# Perturbation: key e163f6fbc359cd4c (CMP_BOUND), line 9402 `... and m["var"] > 1e-6:` -> `... and m["var"] >= 1e-6:`, in memory.
#   Direction: scale moves off 1.0 at the exact tie only.
# Null control: the variance one representable float above the tie.
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import dataclasses
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
from heatpump_optimizer import coordinator as co  # noqa: E402

BASE = L.baseline("_fold_solar_aperture")
MUT = L.mutant("_fold_solar_aperture", 'if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] > 1e-6:',
               'if m["n"] >= SOLAR_APERTURE_MIN_SAMPLES and m["var"] >= 1e-6:')
a = co.SOLAR_APERTURE_ALPHA
# a start variance whose one-step decay v - a*v lands exactly on 1e-6
v0 = 1e-6 / (1 - a)
tie = None
for k in range(-2000, 2000):
    v = v0
    for _ in range(abs(k)):
        v = math.nextafter(v, math.inf if k > 0 else -math.inf)
    if v + a * (0.0 * 0.0 - v) == 1e-6:
        tie = v
        break
print(f"RESULT tie_found={int(tie is not None)} bool")


def one_fold(fn, var0):
    c = L.coord(solar_aperture_learning_enabled=True)
    irr = 400.0
    x = c._thermal_model.compute_solar_gain(irr)
    c._solar_aperture.update({"n": 100.0, "mx": x, "my": 0.0, "cov": 2e-6, "var": var0, "scale": 1.0})
    st = dataclasses.replace(c._current_state, solar_radiation=irr)
    fn(c, st, 0.0, 0.25)
    return float(c._solar_aperture["scale"]), c._solar_aperture["var"]


sb, vb = one_fold(BASE, tie)
sm, _ = one_fold(MUT, tie)
print(f"RESULT var_after={vb!r}")
print(f"RESULT scale_baseline_tie={sb:.6f} ratio")
print(f"RESULT scale_mutant_tie={sm:.6f} ratio")
above = math.nextafter(math.nextafter(tie, math.inf), math.inf)
nb, _ = one_fold(BASE, above)
nm, _ = one_fold(MUT, above)
print(f"RESULT null_baseline={nb:.6f} ratio")
print(f"RESULT null_mutant={nm:.6f} ratio")


def seq(fn, folds, start, inc, ratio):
    c = L.coord(solar_aperture_learning_enabled=True)
    cap = co._zone_capacity(c._thermal_params)
    for i in range(folds):
        irr = start + inc * (i % 40)
        st = dataclasses.replace(c._current_state, solar_radiation=irr)
        fn(c, st, ratio * c._thermal_model.compute_solar_gain(irr) * 0.25 / cap, 0.25)
    return float(c._solar_aperture["scale"])


tried = differ = 0
for folds in (31, 60, 200):
    for start in (150.0, 300.0, 600.0):
        for inc in (5.0, 20.0):
            for ratio in (0.6, 1.5):
                tried += 1
                differ += int(seq(BASE, folds, start, inc, ratio) != seq(MUT, folds, start, inc, ratio))
print(f"RESULT realistic_sequences_tried={tried} count")
print(f"RESULT realistic_sequences_differing={differ} count")
L.footer()
