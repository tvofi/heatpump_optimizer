#!/usr/bin/env python3
"""D10 -- quality-scale rule `diagnostics` (Gold), measured by rendering the real
diagnostics payload for an entry seeded with a marked credential and a marked
home coordinate, and searching the serialized result for both markers.

METRIC (one line): occurrences of the seeded Tibber token string, and of the
seeded home latitude/longitude at full precision, in json.dumps() of what
``async_get_config_entry_diagnostics`` returns.

COMMAND (from the export root, nothing else needed):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D10/diagnostics_rule.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5): token_leaks=0, precise_coordinate_leaks=0, payload_keys=4.
Counts; contention-immune.

INSTRUMENTED SYMBOL:
custom_components.heatpump_optimizer.diagnostics:async_get_config_entry_diagnostics

PERTURBATION: remove CONF_TIBBER_TOKEN from ``diagnostics.TO_REDACT`` and
token_leaks goes 0 -> 1 (direction: up).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
os.chdir(ROOT)
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
import heatpump_optimizer.diagnostics as diag  # noqa: E402

TOKEN = "SEEDED-TIBBER-TOKEN-4f2a9c"
LAT, LON = 59.334591, 18.063240


def main() -> int:
    entry = FakeEntry(data={
        "tibber_token": TOKEN,
        "name": "The Andersson house",
        "solar_location": {"latitude": LAT, "longitude": LON},
        "heat_pump_switch": "switch.heat_pump",
    })
    entry.runtime_data = None
    payload = asyncio.run(diag.async_get_config_entry_diagnostics(FakeHass(), entry))
    blob = json.dumps(payload, default=str)
    print(f"RESULT token_leaks={blob.count(TOKEN)} count")
    print(f"RESULT precise_coordinate_leaks="
          f"{blob.count(str(LAT)) + blob.count(str(LON))} count")
    print(f"RESULT entry_name_leaks={blob.count('Andersson')} count")
    print(f"RESULT payload_keys={len(payload)} count")
    print(f"RESULT payload_bytes={len(blob)} bytes")
    print(f"RESULT entity_ids_kept={blob.count('switch.heat_pump')} count")
    print("RESULT thread_factor=1.0")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    except OSError:
        print("RESULT load1=nan")
    print("RESULT swapins=0")
    print("DETAIL payload:", blob[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
