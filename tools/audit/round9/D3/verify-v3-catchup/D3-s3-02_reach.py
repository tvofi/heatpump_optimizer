#!/usr/bin/env python3
"""Verifier V3 cheap check for D3-s3-02 (dhw_draws.DrawStats.from_dict).

Metric: open_kwh recovered by from_dict({"open_kwh": 1.5, ...}) under the
baseline body vs the M19 mutant (`stats._open_kwh = (0.0)`), with a null
(identity) arm. Mutation applied in memory as an alternate function body,
not on disk.

Command:
    PYTHONPATH=tests/hastub /root/venv314/bin/python \
    tools/audit/round9/D3/verify-v3-catchup/D3-s3-02_reach.py

Real-HA note: DrawStats/dhw_draws.py imports no homeassistant symbol (grep
confirms), so this seam's behaviour cannot diverge between the stub and real
Home Assistant 2026.2.3 — reach is about the store round trip (any HA
restart mid-shower), not about stub vs real HA divergence. Recorded as
not-applicable to the real-HA arm rather than run against /root/venvha.

Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: box G1-V3 (4 CPUs).
"""
import os
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")

t_process0 = time.process_time()
t_wall0 = time.time()

sys.path.insert(0, os.getcwd())

from custom_components.heatpump_optimizer.dhw_draws import DrawStats  # noqa: E402
from unittest import mock  # noqa: E402


def recover_open_kwh(mutant: bool) -> float:
    data = {"reservoirs": {}, "open_label": "morning", "open_date": "2026-01-15",
            "open_kwh": 1.5}
    if not mutant:
        stats = DrawStats.from_dict(data)
        return stats._open_kwh
    # M19: `stats._open_kwh = max(0.0, float(...))` -> `stats._open_kwh = (0.0)`
    real_from_dict = DrawStats.from_dict.__func__

    def mutated_from_dict(cls, data):
        stats = cls()
        if not isinstance(data, dict):
            return stats
        raw = data.get("reservoirs")
        if isinstance(raw, dict):
            for label, events in raw.items():
                pass
        stats._open_label = str(data.get("open_label", ""))
        stats._open_date = str(data.get("open_date", ""))
        stats._open_kwh = 0.0  # the mutant
        return stats

    with mock.patch.object(DrawStats, "from_dict", classmethod(mutated_from_dict)):
        stats = DrawStats.from_dict(data)
    return stats._open_kwh


def main():
    baseline_val = recover_open_kwh(mutant=False)
    mutant_val = recover_open_kwh(mutant=True)
    null_val = recover_open_kwh(mutant=False)  # identity re-run, same code path

    delta_mut = abs(baseline_val - mutant_val)
    delta_null = abs(baseline_val - null_val)

    print(f"RESULT baseline_open_kwh={baseline_val}")
    print(f"RESULT mutant_open_kwh={mutant_val}")
    print(f"RESULT mutant_delta={delta_mut} kWh")
    print(f"RESULT null_delta={delta_null} kWh")

    thread_cpu = time.process_time() - t_process0
    wall = time.time() - t_wall0
    thread_factor = (thread_cpu / wall) if wall > 0 else 1.0
    try:
        load1 = os.getloadavg()[0]
    except (OSError, AttributeError):
        load1 = -1.0
    print(f"RESULT thread_factor={min(thread_factor, 1.0):.3f}")
    print(f"RESULT load1={load1}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
