#!/usr/bin/env python3
# Metric: observe_duty calls (0/1) from one HeatPumpOptimizerCoordinator._settle_defrost(sample, window) on a
#   measured-duty window (window.observed True, duty 0.12, 2 events, outdoor -2 C) whose length is exactly
#   0.25 x the optimization interval (the tie), one second inside and one second outside, at intervals 10, 30, 120 min.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_df697cc04154fbdd.py
# EXPECTED RESULT calls_tie_baseline=1, calls_tie_mutant=0 at every interval; null control: the inside and outside
#   cells agree (1/1 and 0/0).
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._settle_defrost
#   (coordinator.py:9980 `if 0.25 * interval_s <= window.seconds <= 3.0 * interval_s:`).
# Perturbation: mutant df697cc04154fbdd, the lower bound made strict (`0.25 * interval_s < window.seconds <= 3.0 * interval_s`), in memory.
#   Direction: a window exactly a quarter interval long (450 s at the 30-min interval) is no longer observed.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402
import _defrost_common as D  # noqa: E402

OLD = "if 0.25 * interval_s <= window.seconds <= 3.0 * interval_s:"
NEW = "if 0.25 * interval_s < window.seconds <= 3.0 * interval_s:"
MUT = L.mutant(D.C, "_settle_defrost", OLD, NEW)
INSIDE = -1.0 if "lower" == "upper" else 1.0
for interval in (10, 30, 120):
    edge = 0.25 * interval * 60.0
    for label, secs in (("tie", edge), ("inside", edge + INSIDE), ("outside", edge - INSIDE)):
        b, _ = D.observed(secs, None, interval)
        m, _ = D.observed(secs, MUT, interval)
        print(f"RESULT calls_{label}_i{interval}_baseline={b} calls_{label}_i{interval}_mutant={m} seconds={secs}")
L.trailer()
