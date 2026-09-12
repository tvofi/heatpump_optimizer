"""D9 round 4 / H3 -- published payload bytes, and what the recorder keeps.

METRIC (D9.md, verbatim): "Payload bytes = JSON bytes of
``_build_data_dict`` and of every entity's attributes, split by what
``_unrecorded_attributes`` excludes, per cycle and per day."

Every entity is instantiated through the platform's own
``async_setup_entry`` (the ``tests/entities.py:collect`` idiom, re-written
here because ``entities.py`` runs its checks at import and ``sys.exit``s).
Each entity's ``extra_state_attributes`` is serialised with
``json.dumps(..., default=str, separators=(",", ":"))`` -- the compact
form, so the number is a floor on what the recorder writes, never an
inflation of it. Bytes are split into the keys the class lists in
``_unrecorded_attributes`` (dropped before the recorder sees them) and the
rest (written to ``state_attributes`` on every state change whose
attribute blob hashes differently).

Per-day scaling: ``const.DEFAULT_OPTIMIZATION_INTERVAL`` = 30 minutes, so
48 coordinator cycles per day, each publishing one state write per entity.

COMMAND (from the repository root):

    PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
      MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
      python3 tools/audit/round4/D9/h3_payload.py

EXPECTED (baseline 7dd68dd, Apple M1, python 3.11): entity count 200-400,
recorded_attr_bytes_per_cycle 40 000 - 200 000, excluded_attr_bytes_per_cycle
> 100 000. Tolerance +/- 2 % (a byte count is deterministic for a fixed
payload; the spread comes only from float repr).

PERTURBATION: ``H3_PERTURB=exclude_all`` sets
``_unrecorded_attributes = frozenset(all attribute keys)`` on every entity
class; ``recorded_attr_bytes_per_cycle`` must fall to 0.
``H3_PERTURB=exclude_none`` clears every ``_unrecorded_attributes``;
``recorded_attr_bytes_per_cycle`` must rise to the total.

BYTES ARE CONTENTION-IMMUNE and final.
"""
from __future__ import annotations

import os

for _t in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_t, "1")

import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round4", "D9"))

import d9common as C  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    HeatPumpOptimizerCoordinator,
)

PERTURB = os.environ.get("H3_PERTURB", "")
CYCLES_PER_DAY = 24 * 60 // const.DEFAULT_OPTIMIZATION_INTERVAL

PLATFORMS = ("sensor", "binary_sensor", "button", "climate", "switch", "datetime")


def jbytes(obj):
    try:
        return len(json.dumps(obj, default=str, separators=(",", ":")).encode())
    except Exception:
        return len(repr(obj).encode())


def build_coordinator():
    hass = FakeHass()
    hass.states.set("sensor.indoor", FakeState("21.4"))
    hass.states.set("sensor.outdoor", FakeState("-3.0"))
    cfg = {
        const.CONF_INDOOR_TEMP_ENTITY: "sensor.indoor",
        const.CONF_OUTDOOR_TEMP_ENTITY: "sensor.outdoor",
        const.CONF_DHW_TANK_VOLUME: 200.0,
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
        "peak_tariff_enabled": True,
        "peak_tariff_price_per_kw": 45.0,
        "pv_enabled": True,
        "pv_peak_kw": 8.0,
        "pv_export_price": 0.3,
        "away_enabled": True,
        "external_heat_detection_enabled": True,
        "comfort_learning_enabled": True,
        "system_identification_enabled": True,
    }
    entry = FakeEntry(data=cfg)
    coord = HeatPumpOptimizerCoordinator(hass, entry)
    start = C.START
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (start + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (start + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    async def _noop(*a, **kw):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._skip_solve_once = False
    return hass, coord, entry


def collect(module, entry, coord):
    added = []

    def add_entities(entities, *a, **kw):
        added.extend(entities)

    hass = FakeHass()
    entry.runtime_data = coord
    asyncio.run(module.async_setup_entry(hass, entry, add_entities))
    return added


def main():
    print(f"# baseline=7dd68dd  perturb={PERTURB or 'none'}")
    dt_util.freeze(C.START)
    try:
        hass, coord, entry = build_coordinator()
        # One REAL cycle first: without a plan the schedule-bearing
        # attributes are empty and the payload measured is not the one a
        # running install publishes.
        data = asyncio.run(coord._async_update_data())
        C.result("plan_present", bool(coord._optimization_result is not None))
        coord.data = data
        coord.last_update_success = True

        data_bytes = jbytes(data)
        C.result("data_dict_keys", len(data), "keys")
        C.result("data_dict_json_bytes", data_bytes, "bytes")
        by_key = sorted(
            ((jbytes(v), k) for k, v in data.items()), reverse=True
        )
        for size, key in by_key[:10]:
            C.result(f"data_dict.top.{key}", size, "bytes")

        entities = []
        for name in PLATFORMS:
            mod = __import__(f"heatpump_optimizer.{name}", fromlist=["x"])
            try:
                entities.extend(collect(mod, entry, coord))
            except Exception as err:  # noqa: BLE001
                print(f"# platform {name} failed: {type(err).__name__}: {err}")

        if PERTURB == "exclude_none":
            for ent in entities:
                type(ent)._unrecorded_attributes = frozenset()
        elif PERTURB == "exclude_all":
            for ent in entities:
                attrs = getattr(ent, "extra_state_attributes", None) or {}
                type(ent)._unrecorded_attributes = frozenset(attrs.keys())

        n_ok = 0
        rec_total = 0
        exc_total = 0
        state_total = 0
        rows = []
        for ent in entities:
            try:
                attrs = getattr(ent, "extra_state_attributes", None) or {}
            except Exception:  # noqa: BLE001
                attrs = {}
            try:
                val = getattr(ent, "native_value", None)
            except Exception:  # noqa: BLE001
                val = None
            excluded_keys = set(getattr(ent, "_unrecorded_attributes", frozenset()))
            rec = sum(jbytes({k: v}) for k, v in attrs.items()
                      if k not in excluded_keys)
            exc = sum(jbytes({k: v}) for k, v in attrs.items()
                      if k in excluded_keys)
            rec_total += rec
            exc_total += exc
            state_total += jbytes(val)
            n_ok += 1
            rows.append((rec, exc, type(ent).__name__,
                         getattr(ent, "_attr_unique_id", None) or
                         getattr(ent, "unique_id", None)))

        C.result("entities_instantiated", n_ok, "entities")
        C.result("entities_with_exclusions",
                 sum(1 for e in entities
                     if getattr(e, "_unrecorded_attributes", frozenset())),
                 "entities")
        C.result("recorded_attr_bytes_per_cycle", rec_total, "bytes")
        C.result("excluded_attr_bytes_per_cycle", exc_total, "bytes")
        C.result("state_value_bytes_per_cycle", state_total, "bytes")
        C.result("attr_bytes_total_per_cycle", rec_total + exc_total, "bytes")
        C.result(
            "excluded_share_pct",
            float(100.0 * exc_total / (rec_total + exc_total))
            if (rec_total + exc_total) else float("nan"),
            "pct",
        )
        C.result("cycles_per_day", CYCLES_PER_DAY, "cycles")
        C.result("recorded_attr_bytes_per_day",
                 rec_total * CYCLES_PER_DAY, "bytes")
        C.result("recorded_attr_mb_per_day",
                 float(rec_total * CYCLES_PER_DAY / 1048576.0), "MiB")
        C.result("recorded_attr_mb_per_10day_purge",
                 float(rec_total * CYCLES_PER_DAY * 10 / 1048576.0), "MiB")
        rows.sort(reverse=True)
        for rec, exc, cls, uid in rows[:12]:
            C.result(f"entity.top.{cls}", f"recorded={rec} excluded={exc} uid={uid}")
    finally:
        dt_util.freeze(None)
    C.telemetry()


if __name__ == "__main__":
    main()
