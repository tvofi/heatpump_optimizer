#!/usr/bin/env python3
# Metric: record_quiet_period calls (0/1) and the comfort learner's evidence change from one
#   HeatPumpOptimizerCoordinator._record_quiet_comfort_period() on a flat plan, at a price vector whose
#   float64 (max-min)/mean is exactly 0.15 (the tie), with 1.5 kWh of planned heating.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_8daaf4fcaf8cd897.py
# EXPECTED RESULT calls_tie_baseline=1, calls_tie_mutant=0; null control: spreads 0.10 and 0.30 equal arms.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._record_quiet_comfort_period
#   (coordinator.py:11002 `if float(np.max(prices) - np.min(prices)) / mean_price < 0.15:`).
# Perturbation: mutant 8daaf4fcaf8cd897, `< 0.15` -> `<= 0.15`, in memory. Direction: at a spread of exactly 15 %
#   the quiet period is no longer recorded (evidence unchanged instead of down).
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _quiet_common as Q  # noqa: E402

OLD = "if float(np.max(prices) - np.min(prices)) / mean_price < 0.15:"
NEW = "if float(np.max(prices) - np.min(prices)) / mean_price <= 0.15:"
MUT = L.mutant(Q.C, "_record_quiet_comfort_period", OLD, NEW)
tie = Q.tie_search(0.15, lambda v: float(np.max(v) - np.min(v)) / float(np.mean(v)),
                   [(0.925, 1.0, 1.075)] + [(a, a * 1.075 / 0.925) for a in np.linspace(0.5, 2.0, 61)])
print(f"RESULT tie_prices={tie.tolist()} ratio={float(np.max(tie)-np.min(tie))/float(np.mean(tie))!r}")
for label, prices in (("tie", tie), ("spread010", np.array([1.0, 1.10526])), ("spread030", np.array([0.85, 1.0, 1.15]))):
    for name, fn in (("baseline", None), ("mutant", MUT)):
        d, n, dt = Q.evidence_delta(prices, [6.0], fn=fn)
        print(f"RESULT calls_{label}_{name}={n} evidence_delta={d}")
L.trailer()
