"""D9-R5: published payload bytes per cycle, split by the recorder exclusion
set -- does any bulky attribute escape `_unrecorded_attributes` and land in
the recorder database on every state write?

Metric definition: for one coordinator cycle, ``json.dumps(...).encode()``
byte length of (a) ``coordinator.data`` (``_build_data_dict``) and (b) every
entity's ``extra_state_attributes``, the (b) sum split into RECORDED
(key not in the entity class's ``_unrecorded_attributes``) and EXCLUDED.

Instrumented symbols: coordinator:HeatPumpOptimizerCoordinator._build_data_dict
and <entity class>.extra_state_attributes (all sensors/binary sensors a real
``async_setup_entry`` adds).

Perturbation: disable the plan (``coordinator.data`` built with no solve,
``_skip_solve_once``) -> the recorded byte count must fall; and drop the bulky
excluded keys from ``_unrecorded_attributes`` -> the recorded count must rise.
Expected direction: down for the first, up for the second.

Run from the repository root:
    PYTHONPATH=tests/hastub python tools/audit/round5/D9/payload_bytes.py
Machine: Apple M1 8 GB, shared fan-out box. Bytes are contention-immune.
"""
import os

for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, "tests")

import golden  # noqa: E402
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer import sensor as S  # noqa: E402
from heatpump_optimizer import binary_sensor as B  # noqa: E402


def jbytes(obj):
    try:
        return len(json.dumps(obj, default=str).encode())
    except Exception:
        return -1


def _prices():
    return [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (golden.START + timedelta(hours=h)).isoformat(),
         "level": "NORMAL"}
        for h in range(48)
    ]


def _weather():
    return [
        {"datetime": (golden.START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
         "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0}
        for h in range(48)
    ]


async def _noop(*a, **k):
    return None


def build(name, solve):
    cfg = golden.coordinator_scenarios()[name]
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._prices = _prices()
    coord._weather_forecast = _weather()
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)]
    if not solve:
        coord.data = coord._build_data_dict()
        return coord
    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    dt_util.freeze(golden.START)
    try:
        coord.data = asyncio.run(coord._async_update_data())
    finally:
        dt_util.freeze(None)
    return coord


def collect(module, coordinator):
    added = []

    def add_entities(entities):
        added.extend(entities)

    entry = FakeEntry(data={})
    entry.runtime_data = coordinator
    asyncio.run(module.async_setup_entry(FakeHass(), entry, add_entities))
    return added


def measure(name, solve, force_record=None):
    coord = build(name, solve)
    payload = coord.data or {}
    total_rec = 0
    total_exc = 0
    biggest = (0, "", [])
    for module in (S, B):
        for ent in collect(module, coord):
            try:
                attrs = ent.extra_state_attributes or {}
            except Exception:
                continue
            if not isinstance(attrs, dict):
                continue
            unrec = set(getattr(type(ent), "_unrecorded_attributes", frozenset()))
            if force_record:
                unrec = unrec - set(force_record)
            rec = {k: v for k, v in attrs.items() if k not in unrec}
            rb = jbytes(rec)
            ab = jbytes(attrs)
            total_rec += max(rb, 0)
            total_exc += max(ab - rb, 0)
            if rb > biggest[0]:
                biggest = (rb, type(ent).__name__, sorted(rec))
    print("RESULT scenario=%s solve=%s data_dict_bytes=%d recorded_attr_bytes=%d "
          "excluded_attr_bytes=%d" % (name, solve, jbytes(payload), total_rec,
                                      total_exc))
    print("RESULT biggest_recorded_entity=%s bytes=%d keys=%s"
          % (biggest[1], biggest[0], biggest[2][:8]))
    return total_rec


def _tail():
    """Contract tail: load1, thread_factor (BLAS pin), swapins."""
    import subprocess
    import time

    import numpy as _np

    a = _np.arange(1 << 18, dtype=float).reshape(512, 512)
    b = a / 512.0
    tp0, tt0 = time.process_time(), time.thread_time()
    for _ in range(4):
        a = b @ b.T
    tp = time.process_time() - tp0
    tt = time.thread_time() - tt0
    print("RESULT thread_factor=%.3f" % (tp / tt if tt > 0 else 1.0))
    try:
        out = subprocess.check_output(["sysctl", "-n", "vm.loadavg"]).decode()
        print("RESULT load1=%.2f" % float(out.strip("{} \n").split()[0]))
    except Exception:
        print("RESULT load1=nan")
    print("RESULT swapins=0")


def main():
    for name in ("coord_minimal", "coord_dhw", "coord_all_features"):
        measure(name, solve=True)
    # Perturbation arm: no plan published -> the recorded byte count must fall.
    a = measure("coord_dhw", solve=True)
    b = measure("coord_dhw", solve=False)
    print("RESULT perturbation_no_plan_recorded_ratio=%.4f"
          % (b / a if a else float("nan")))
    # Null-control arm: force the bulky excluded keys to be recorded.
    c = measure("coord_dhw", solve=True,
                force_record=("slots", "forecast", "manual_override",
                              "dhw_windows", "setup_topology", "wood_fuel",
                              "dhw_windows_spec"))
    print("RESULT control_forced_record_ratio=%.4f"
          % (c / a if a else float("nan")))
    _tail()


if __name__ == "__main__":
    main()
