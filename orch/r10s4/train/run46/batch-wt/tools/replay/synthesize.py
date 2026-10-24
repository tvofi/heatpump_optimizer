#!/usr/bin/env python3
"""Build the synthetic replay fixture THROUGH the exporter, not beside it.

The replay lane needs a recorded day before the owner's first export exists,
and a fixture written straight to JSON would prove nothing about
``export.py``. So this writes what a Home Assistant install holds -- a
recorder database in the current schema (``states``, ``states_meta``,
``state_attributes``, ``schema_changes``) and the three ``.storage`` files --
into a temporary config directory, and runs ``export.build_export`` over it.

The day is the one #1499 was reported on: the pump in its hot-water-only mode
all day (space heating blocked), the tank drawn down morning and evening and
reheated, on a January day with a Nord Pool price entity. The config entry
carries a leftover token and an exact coordinate, and the weather entity a
tokenised picture URL, so the committed file also shows the sanitiser working.

    python3 tools/replay/synthesize.py            # rewrite the fixture
    python3 tools/replay/synthesize.py --out X    # write elsewhere
"""
from __future__ import annotations

import argparse
import json
import math
import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import export  # noqa: E402

ROOT = HERE.parent.parent
FIXTURE = ROOT / "tests" / "replay" / "synthetic-dhw-only.json"
TZ_NAME = "Europe/Stockholm"
DAY = datetime(2026, 1, 15, tzinfo=ZoneInfo(TZ_NAME))
ENTRY_ID = "01JSYNTHETICREPLAY0000000001"
SCHEMA = 48

ENTRY_DATA = {
    "price_source": "entity",
    "price_entity": "sensor.nordpool_kwh_se3_sek",
    "weather_entity": "weather.forecast_home",
    "indoor_temp_entity": "sensor.living_room_temperature",
    "outdoor_temp_entity": "sensor.outdoor_temperature",
    "dhw_temp_entity": "sensor.hot_water_tank_temperature",
    "dhw_tank_volume": 180.0,
    "heat_pump_mode_entity": "select.heat_pump_operating_mode",
    "heat_pump_power_entity": "sensor.heat_pump_power",
    # A token left behind from an earlier Tibber setup, and a map pin to the
    # metre: both must be gone from the committed file.
    "tibber_token": "synthetic-leftover-token-5b1f0c9e",
    "solar_location": {"latitude": 59.334591, "longitude": 18.063240},
}
ENTRY_OPTIONS = {"optimization_interval": 30}
PUBLISHED = (
    "sensor.heat_pump_optimizer_heat_pump_action",
    "climate.heat_pump_optimizer",
)
MODES = ["Heating + hot water", "Heating", "Hot water"]


def _prices(day: datetime) -> list[dict]:
    """A January Nord Pool day: two peaks, a cheap night."""
    rows = []
    for h in range(24):
        peak = math.exp(-((h - 8) ** 2) / 4.0) + 1.2 * math.exp(-((h - 18) ** 2) / 5.0)
        value = round(0.42 + 0.9 * peak + 0.03 * math.sin(h), 4)
        start = day + timedelta(hours=h)
        rows.append({"start": start.isoformat(),
                     "end": (start + timedelta(hours=1)).isoformat(),
                     "value": value})
    return rows


def _series() -> dict[str, list[tuple[datetime, str, dict]]]:
    """Every recorded row, as (last_updated, state, attributes)."""
    out: dict[str, list[tuple[datetime, str, dict]]] = {}
    start = DAY - timedelta(hours=1)
    temp_attrs = {"unit_of_measurement": "°C", "device_class": "temperature",
                  "state_class": "measurement"}

    def minutes(step: int, span_h: float = 26.0):
        t = start
        while t < start + timedelta(hours=span_h):
            yield t
            t += timedelta(minutes=step)

    out["sensor.outdoor_temperature"] = [
        (t, f"{-5.3 + 2.7 * math.sin((t.hour + t.minute / 60 - 9) / 24 * 2 * math.pi):.1f}",
         {**temp_attrs, "friendly_name": "Outdoor"})
        for t in minutes(10)
    ]
    out["sensor.living_room_temperature"] = [
        (t, f"{20.6 + 0.35 * math.sin((t.hour + t.minute / 60 - 15) / 24 * 2 * math.pi):.2f}",
         {**temp_attrs, "friendly_name": "Living room"})
        for t in minutes(10)
    ]
    tank, power, t = 48.3, [], start
    tank_rows = []
    while t < start + timedelta(hours=26):
        local_h = t.hour + t.minute / 60
        heating = 4.0 <= local_h < 5.5 or 15.5 <= local_h < 17.0
        if 6.5 <= local_h < 7.25 or 18.5 <= local_h < 19.5:
            tank -= 1.1  # a shower's draw, per five minutes
        tank += 0.55 if heating else -0.02
        tank_rows.append((t, f"{tank:.1f}", {**temp_attrs, "friendly_name": "Tank"}))
        power.append((t, "1.83" if heating else "0.0",
                      {"unit_of_measurement": "kW", "device_class": "power",
                       "state_class": "measurement", "friendly_name": "Heat pump power"}))
        t += timedelta(minutes=5)
    out["sensor.hot_water_tank_temperature"] = tank_rows
    out["sensor.heat_pump_power"] = power
    out["select.heat_pump_operating_mode"] = [
        (start, "Hot water", {"options": MODES, "friendly_name": "Operating mode"})
    ]
    today, tomorrow = _prices(DAY), _prices(DAY + timedelta(days=1))
    yesterday = _prices(DAY - timedelta(days=1))
    nord = []
    for h in range(-1, 25):
        at = DAY + timedelta(hours=h)
        day_rows = yesterday if h < 0 else today if h < 24 else tomorrow
        idx = h % 24
        published_tomorrow = (h % 24) >= 13 if h < 24 else False
        attrs = {
            "unit_of_measurement": "SEK/kWh",
            "currency": "SEK",
            "raw_today": day_rows,
            "raw_tomorrow": (tomorrow if h < 24 else _prices(DAY + timedelta(days=2)))
            if published_tomorrow else [],
            "friendly_name": "Nord Pool SE3",
        }
        nord.append((at, f"{day_rows[idx]['value']:.4f}", attrs))
    out["sensor.nordpool_kwh_se3_sek"] = nord
    out["weather.forecast_home"] = [
        (t, "cloudy", {
            "temperature": round(-5.0 + 2.5 * math.sin((t.hour - 9) / 24 * 2 * math.pi), 1),
            "wind_speed": 11.2, "humidity": 86, "temperature_unit": "°C",
            "wind_speed_unit": "km/h", "friendly_name": "Forecast Home",
            "entity_picture": "/api/weather_proxy/home?token=synthetic5b1f0c9e",
        })
        for t in minutes(60)
    ]
    # What the owner saw: the action pinned at "off" through a hot-water day.
    out["sensor.heat_pump_optimizer_heat_pump_action"] = [
        (t, "off", {"heat_pump_on": 2 <= t.hour < 6, "friendly_name": "Heat pump action"})
        for t in minutes(30)
    ]
    out["climate.heat_pump_optimizer"] = [
        (t, "auto", {"hvac_action": "idle", "current_temperature": 20.6})
        for t in minutes(30)
    ]
    return out


def write_install(config_dir: Path) -> Path:
    """The recorder database and the three ``.storage`` files."""
    storage = config_dir / ".storage"
    storage.mkdir(parents=True)
    (storage / "core.config").write_text(json.dumps(
        {"version": 1, "key": "core.config",
         "data": {"time_zone": TZ_NAME, "latitude": 59.334591, "longitude": 18.06324}}))
    (storage / "core.config_entries").write_text(json.dumps(
        {"version": 1, "key": "core.config_entries", "data": {"entries": [
            {"entry_id": ENTRY_ID, "domain": export.DOMAIN, "title": "Heat Pump Optimizer",
             "version": 1, "minor_version": 1, "data": ENTRY_DATA,
             "options": ENTRY_OPTIONS},
            {"entry_id": "01JOTHER", "domain": "met", "title": "Home",
             "data": {"latitude": 59.334591, "longitude": 18.06324}, "options": {}},
        ]}}))
    (storage / "core.entity_registry").write_text(json.dumps(
        {"version": 1, "key": "core.entity_registry", "data": {"entities": [
            {"entity_id": eid, "platform": export.DOMAIN, "config_entry_id": ENTRY_ID}
            for eid in PUBLISHED
        ] + [{"entity_id": "weather.forecast_home", "platform": "met",
              "config_entry_id": "01JOTHER"}]}}))

    db = config_dir / "home-assistant_v2.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE schema_changes (change_id INTEGER PRIMARY KEY,
            schema_version INTEGER, changed DATETIME);
        CREATE TABLE states_meta (metadata_id INTEGER PRIMARY KEY,
            entity_id VARCHAR(255));
        CREATE TABLE state_attributes (attributes_id INTEGER PRIMARY KEY,
            hash BIGINT, shared_attrs TEXT);
        CREATE TABLE states (state_id INTEGER PRIMARY KEY, entity_id CHAR(0),
            state VARCHAR(255), attributes CHAR(0), event_id SMALLINT,
            last_changed CHAR(0), last_changed_ts FLOAT, last_reported_ts FLOAT,
            last_updated CHAR(0), last_updated_ts FLOAT, old_state_id INTEGER,
            attributes_id INTEGER, context_id CHAR(0), context_user_id CHAR(0),
            context_parent_id CHAR(0), origin_idx SMALLINT, context_id_bin BLOB,
            context_user_id_bin BLOB, context_parent_id_bin BLOB,
            metadata_id INTEGER);
        CREATE INDEX ix_states_metadata_id_last_updated_ts
            ON states (metadata_id, last_updated_ts);
        """
    )
    conn.execute("INSERT INTO schema_changes VALUES (1, ?, '2026-01-01')", (SCHEMA,))
    # A row for an entity nobody maps, so the exporter's selection is tested.
    series = {**_series(), "device_tracker.phone": [
        (DAY, "home", {"latitude": 59.334591, "longitude": 18.06324})]}
    attrs_ids: dict[str, int] = {}
    for meta_id, (entity_id, rows) in enumerate(sorted(series.items()), start=1):
        conn.execute("INSERT INTO states_meta VALUES (?, ?)", (meta_id, entity_id))
        previous = None
        # A polled source re-reports an unchanged value, and the recorder keeps
        # the newest report on the row: one minute before the next change, or
        # past the window for the last row.
        reported = [r[0] for r in rows[1:]] + [DAY + timedelta(days=1, hours=1)]
        for (when, state, attrs), until in zip(rows, reported):
            shared = json.dumps(attrs, sort_keys=True)
            if shared not in attrs_ids:
                attrs_ids[shared] = len(attrs_ids) + 1
                conn.execute("INSERT INTO state_attributes VALUES (?, ?, ?)",
                             (attrs_ids[shared], hash(shared) & 0xFFFF, shared))
            ts = when.astimezone(timezone.utc).timestamp()
            cur = conn.execute(
                "INSERT INTO states (state, last_updated_ts, last_changed_ts, "
                "last_reported_ts, old_state_id, attributes_id, metadata_id) "
                "VALUES (?, ?, NULL, ?, ?, ?, ?)",
                (state, ts, (until - timedelta(minutes=1)).astimezone(timezone.utc).timestamp(),
                 previous, attrs_ids[shared], meta_id),
            )
            previous = cur.lastrowid
    conn.commit()
    conn.close()
    return db


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=FIXTURE)
    args = ap.parse_args(argv)
    with tempfile.TemporaryDirectory() as tmp:
        config_dir = Path(tmp)
        db = write_install(config_dir)
        payload = export.build_export(
            config_dir, db, days=1, end_date=(DAY + timedelta(days=1)).date().isoformat(),
            entry_id=None, extra=[], price_entity=None,
        )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, sort_keys=True, indent=1) + "\n")
    rows = sum(len(v) for v in payload["states"].values())
    print(f"wrote {args.out}: {len(payload['states'])} entities, {rows} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
