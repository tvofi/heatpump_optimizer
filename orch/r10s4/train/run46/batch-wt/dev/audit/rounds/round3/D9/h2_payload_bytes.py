"""D9 round 3 / H2 -- published payload bytes against the recorder exclusion set.

METRIC (from tools/audit/briefs/D9.md, verbatim):
  payload_bytes = JSON bytes of coordinator._build_data_dict() and of every
  entity's extra_state_attributes, split by what each entity class's
  ``_unrecorded_attributes`` excludes, per cycle and per day.

  recorded_attr_bytes  = sum over every entity a platform adds, of
                         len(json.dumps(attrs_without_unrecorded_keys)).
  excluded_attr_bytes  = the same for the keys _unrecorded_attributes names.
  A state write also carries the state value itself; only attributes are
  counted here, so every figure is a LOWER bound on what the recorder writes.

COMMAND (from the repository root):
  PYTHONPATH=tests/hastub python3 tools/audit/round3/D9/h2_payload_bytes.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, Apple M1,
python 3.11.5). Bytes are exact and contention-immune: +-0 on a re-run of the
same tree with the same inputs.
  all_features.entities                  = 74     +-0
  all_features.recorded_attr_bytes       = 12699  +-0
  all_features.excluded_attr_bytes       = 85246  +-0
  all_features.excluded_fraction         = 0.8703 +-0.001
  all_features.recorded_attr_kib_per_day = 595.3  +-0.1
  all_features.data_dict_bytes           = 84751  +-0
  all_features.churn_entities_changed    = 20     +-0
  all_features.churn_recorded_bytes_per_cycle = 8236 +-0
  all_features.churn_recorded_kib_per_day     = 386.1 +-0.1
  null_control_ratio_recorded            = 1.006  +-0.02  (flat vs priced: the
      payload is structural, so a price signal must not decide its size)

PERTURBATION: HPO_D9_UNRECORDED=all treats every attribute as unrecorded;
recorded_attr_bytes must collapse to the sum of the per-entity empty-dict
JSON ("{}") and excluded_attr_bytes must rise by exactly the difference.
HPO_D9_UNRECORDED=none empties every _unrecorded_attributes set; recorded
must rise to recorded+excluded.

INSTRUMENTED SYMBOLS: heatpump_optimizer.coordinator.
HeatPumpOptimizerCoordinator._build_data_dict, every platform's
async_setup_entry, and each entity class's ``_unrecorded_attributes``.
"""
from __future__ import annotations

import asyncio
import importlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "tools", "audit", "round3", "D9"))
import d9lib  # noqa: E402
from d9lib import result, telemetry  # noqa: E402

from heatpump_optimizer import const  # noqa: E402

UNRECORDED_MODE = os.environ.get("HPO_D9_UNRECORDED", "as-shipped")
CYCLES_PER_DAY = 24 * 60 / const.DEFAULT_OPTIMIZATION_INTERVAL  # 48

ALL_FEATURES = {
    "dhw_tank_volume": 200.0,
    "dhw_setpoint": 55.0,
    "dhw_min_temperature": 45.0,
    "dhw_windows": "06:00-08:30, 17:00-22:00",
    "peak_tariff_enabled": True,
    "peak_tariff_price_per_kw": 45.0,
    "pv_enabled": True,
    "pv_peak_kw": 8.0,
    "pv_export_price": 0.3,
    "away_enabled": True,
    "external_heat_detection_enabled": True,
    "comfort_learning_enabled": True,
    "system_identification_enabled": True,
    "compressor_cycling_cost": 0.5,
}


def jbytes(obj) -> int:
    return len(json.dumps(obj, default=str).encode("utf-8"))


def collect(module_name, coord):
    """Drive the platform's real async_setup_entry, as tests/entities.py does."""
    from harness import FakeEntry, FakeHass

    module = importlib.import_module(f"heatpump_optimizer.{module_name}")
    added = []
    entry = FakeEntry(data=dict(coord._config))
    entry.runtime_data = coord
    hass = FakeHass()
    asyncio.run(module.async_setup_entry(hass, entry, added.extend))
    return added


def unrecorded_of(entity) -> frozenset:
    if UNRECORDED_MODE == "none":
        return frozenset()
    keys = frozenset(getattr(entity, "_unrecorded_attributes", frozenset()))
    if UNRECORDED_MODE == "all":
        try:
            return frozenset(entity.extra_state_attributes or {})
        except Exception:  # noqa: BLE001
            return keys
    return keys


def snapshot_attrs(coord) -> dict:
    """{(class, entity index): {recorded attrs}} for every entity added."""
    out = {}
    for platform in const.PLATFORMS:
        for i, ent in enumerate(collect(platform, coord)):
            try:
                attrs = dict(ent.extra_state_attributes or {})
            except Exception:  # noqa: BLE001
                attrs = {}
            skip = unrecorded_of(ent)
            out[(platform, i, type(ent).__name__)] = {
                k: v for k, v in attrs.items() if k not in skip
            }
    return out


def churn(name: str, coord) -> None:
    """Bytes of RECORDED attributes that actually CHANGE cycle to cycle.

    Home Assistant's recorder stores one row per distinct attribute set and
    reuses it, so bytes that never change are written once, not once per
    cycle. This is the honest per-cycle recorder cost: the JSON bytes of the
    entities whose recorded attributes differ from the previous cycle.
    """
    from homeassistant.util import dt as dt_util
    from datetime import timedelta

    async def _noop(*a, **k):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    restore = d9lib.inline_solves()
    try:
        coord.data = asyncio.run(coord._async_update_data())
        first = snapshot_attrs(coord)
        dt_util.freeze(d9lib.START + timedelta(minutes=const.DEFAULT_OPTIMIZATION_INTERVAL))
        coord.data = asyncio.run(coord._async_update_data())
        second = snapshot_attrs(coord)
        dt_util.freeze(d9lib.START)
    finally:
        restore()
    changed_bytes = 0
    changed_entities = 0
    for key, attrs in second.items():
        if first.get(key) != attrs:
            changed_entities += 1
            changed_bytes += jbytes(attrs)
    result(f"{name}.churn_entities_changed", changed_entities, "count")
    result(f"{name}.churn_entities_total", len(second), "count")
    result(f"{name}.churn_recorded_bytes_per_cycle", changed_bytes, "bytes")
    result(
        f"{name}.churn_recorded_kib_per_day",
        changed_bytes * CYCLES_PER_DAY / 1024.0, "KiB",
    )


def measure(name: str, profile: str, extra) -> dict:
    hass, coord = d9lib.build_coordinator(extra, profile=profile)
    restore = d9lib.inline_solves()

    async def _noop(*a, **k):
        return None

    coord._fetch_tibber_prices = _noop
    coord._fetch_weather_forecast = _noop
    coord._fetch_solar_forecast = _noop
    coord._async_learn_price_shape = _noop
    try:
        data = asyncio.run(coord._async_update_data())
    finally:
        restore()
    coord.data = data

    rec = exc = 0
    n_ent = 0
    biggest: list[tuple[int, str, str]] = []
    for platform in const.PLATFORMS:
        for ent in collect(platform, coord):
            n_ent += 1
            try:
                attrs = dict(ent.extra_state_attributes or {})
            except Exception:  # noqa: BLE001 - an entity with no attributes
                attrs = {}
            skip = unrecorded_of(ent)
            kept = {k: v for k, v in attrs.items() if k not in skip}
            dropped = {k: v for k, v in attrs.items() if k in skip}
            rec += jbytes(kept)
            exc += jbytes(dropped)
            for k, v in kept.items():
                biggest.append((jbytes({k: v}), type(ent).__name__, k))
    biggest.sort(reverse=True)

    result(f"{name}.data_dict_keys", len(data), "count")
    result(f"{name}.data_dict_bytes", jbytes(data), "bytes")
    result(f"{name}.entities", n_ent, "count")
    result(f"{name}.recorded_attr_bytes", rec, "bytes")
    result(f"{name}.excluded_attr_bytes", exc, "bytes")
    result(
        f"{name}.excluded_fraction",
        (exc / (rec + exc)) if (rec + exc) else 0.0,
        "1",
    )
    result(
        f"{name}.recorded_attr_kib_per_day",
        rec * CYCLES_PER_DAY / 1024.0,
        "KiB",
    )
    for i, (b, cls, key) in enumerate(biggest[:8]):
        result(f"{name}.top{i}_recorded", f"{cls}.{key}={b}", "bytes")
    return {"rec": rec, "exc": exc, "ent": n_ent}


def main() -> None:
    result("baseline_sha", "ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1", "sha")
    result("unrecorded_mode", UNRECORDED_MODE, "enum")
    result("cycles_per_day", CYCLES_PER_DAY, "count")

    print("-- all_features (the payload a fully configured install writes)")
    a = measure("all_features", "tibber_like", ALL_FEATURES)
    print("-- NULL CONTROL: the same install at a flat price profile")
    f = measure("flat", "flat", ALL_FEATURES)
    print("-- minimal install (no DHW, no optional features)")
    measure("minimal", "tibber_like", None)

    print("-- churn: recorded attribute bytes that CHANGE per cycle")
    _, coord = d9lib.build_coordinator(ALL_FEATURES, profile="tibber_like")
    churn("all_features", coord)

    result(
        "null_control_ratio_recorded",
        (f["rec"] / a["rec"]) if a["rec"] else float("nan"),
        "1",
    )
    telemetry()


if __name__ == "__main__":
    main()
