#!/usr/bin/env python3
# Metric: HeatPumpOptimizerCoordinator._power_headroom()["available"] (0/1) for a capacity tariff with no
#   main fuse and no reference peak, at a moment its sample_factor is 0.0 (a month outside
#   peak_tariff_months "Nov-Mar": 2026-07-15 12:00 UTC).
# Command: PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s1/wave/D3-g09/probes/probe_d8101520588009d9.py
# EXPECTED RESULT available_offseason_baseline=0, available_offseason_mutant=1 (limit 0.0 kW, "capacity tariff
#   with no peak reference yet"); null control: in season (2026-01-15) both arms 1 with the same limit.
# Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box D3-g09 (4 vCPU Intel Xeon @ 2.10GHz, 16 GB).
# Instrumented symbol: custom_components.heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._power_headroom
#   (coordinator.py:8900 `elif tariff.enabled and tariff.sample_factor(dt_util.now()) > 0.0:`).
# Perturbation: mutant d8101520588009d9, `> 0.0` -> `>= 0.0`, in memory (recompiled method, mock.patch.object,
#   mutant arm only). sample_factor is clamped to [0, 1], so the mutant's test is always true.
#   Direction: off-season "available" 0 -> 1 with limit_kw 0.0 (a published "0 kW headroom" where the
#   tariff bills nothing).
# Count key: the dict the method returns (what the power-headroom sensor publishes).
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _probe_lib as L  # noqa: E402

C = L.HeatPumpOptimizerCoordinator
OLD = "elif tariff.enabled and tariff.sample_factor(dt_util.now()) > 0.0:"
NEW = "elif tariff.enabled and tariff.sample_factor(dt_util.now()) >= 0.0:"
MUT = L.mutant(C, "_power_headroom", OLD, NEW)
c = L.coord(peak_tariff_enabled=True, peak_tariff_price_per_kw=50.0, peak_tariff_months="Nov-Mar")


def arm(when, m):
    with mock.patch.object(L.coord_mod.dt_util, "now", lambda *a, **k: when):
        if m:
            with mock.patch.object(C, "_power_headroom", MUT):
                return c._power_headroom()
        return c._power_headroom()


print(f"RESULT fuse_kw={c._fuse_kw()}")
for label, when in (("offseason", datetime(2026, 7, 15, 12, tzinfo=timezone.utc)),
                    ("inseason", datetime(2026, 1, 15, 12, tzinfo=timezone.utc))):
    print(f"RESULT sample_factor_{label}={c._capacity_tariff().sample_factor(when)}")
    for name, m in (("baseline", False), ("mutant", True)):
        out = arm(when, m)
        print(f"RESULT available_{label}_{name}={int(bool(out.get('available')))}"
              f" limit_kw={out.get('limit_kw')} limit_source={out.get('limit_source')!r}")
L.trailer()
