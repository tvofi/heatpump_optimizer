#!/usr/bin/env python3
# Metric: HeatPumpOptimizerCoordinator._outage_recovery_active(now) as 0/1, at now == _outage_recovery_until
#   (the tie), one second before it and one second after it.
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_9cdf54d2309cfcc8.py
# EXPECTED RESULT active_at_tie_baseline=0, active_at_tie_mutant=1 (exact; booleans)
# EXPECTED RESULT before/after: baseline == mutant (1 before the end, 0 after it): the null control
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._outage_recovery_active
#   (coordinator.py:9038 `and utc_elapsed_seconds(self._outage_recovery_until, now) > 0`).
# Perturbation: mutant 9cdf54d2309cfcc8, `> 0` -> `>= 0`, in memory (method recompiled from its source,
#   mock.patch.object on the mutant arm only). Direction: active at the tie goes 0 -> 1.
# Count key: the method's return value, the value the production seam delivers.
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402

C = L.HeatPumpOptimizerCoordinator
OLD = "and utc_elapsed_seconds(self._outage_recovery_until, now) > 0"
NEW = "and utc_elapsed_seconds(self._outage_recovery_until, now) >= 0"
MUT = L.mutant(C, "_outage_recovery_active", OLD, NEW)
c = L.coord()
until = datetime(2026, 2, 1, 3, 0, 0, tzinfo=timezone.utc)
c._outage_recovery_until = until


def arm(now, m):
    if m:
        with mock.patch.object(C, "_outage_recovery_active", MUT):
            return int(c._outage_recovery_active(now))
    return int(c._outage_recovery_active(now))


for label, now in (("tie", until), ("before_end", until - timedelta(seconds=1)),
                   ("after_end", until + timedelta(seconds=1))):
    print(f"RESULT active_at_{label}_baseline={arm(now, False)}")
    print(f"RESULT active_at_{label}_mutant={arm(now, True)}")
L.trailer()
