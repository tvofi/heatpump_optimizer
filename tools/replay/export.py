#!/usr/bin/env python3
"""Export recorded days from a Home Assistant install for the replay lane.

Run on the owner's own Home Assistant box. It reads, and only reads:

* ``<config>/home-assistant_v2.db`` -- the recorder's SQLite database, opened
  with ``mode=ro`` (the ``states``, ``states_meta``, ``state_attributes`` and
  ``schema_changes`` tables of the current schema; ``states_meta`` arrived in
  schema 41, so an older database is refused by name);
* ``<config>/.storage/core.config_entries`` -- this integration's entry;
* ``<config>/.storage/core.entity_registry`` -- the entities it publishes;
* ``<config>/.storage/core.config`` -- the instance's time zone.

It opens no socket. The standard library is all it imports, so it runs under
the interpreter inside the Home Assistant container as it is.

WHAT IT EXPORTS, for the window ``[end - days, end)`` in the instance's zone:
every entity id the config entry maps (any value in ``data`` or ``options``
spelled like an entity id -- thermometers, the price and weather entities, the
pump's mode, switch, power and valve entities), the entities this integration
publishes (from the registry; carried for comparison, never fed back), and any
``--extra-entity``. For each, the last state before the window and every state
inside it.

WHAT IT REMOVES, by the rules ``tests/nightly_ha.py``'s A10 checks enforce on
diagnostics (``a10:no_credential``, ``a10:no_precise_location``): every key
naming a credential is dropped wherever it occurs (``tibber_token`` included),
every ``latitude``/``longitude`` is rounded to two decimals, and ``entity_picture``
and any ``?token=`` URL are dropped because a camera or media picture carries an
access token there. The literal value of every dropped credential is then
searched for in the output, and the export refuses to write if one survives.

``--check FILE`` applies the same rules to a file already written and exits 1
on any violation; ``tests/replay.py`` runs it on every committed fixture.

    python3 export.py --config-dir /config --days 7 --out /config/hpo-replay.json
    python3 export.py --check /config/hpo-replay.json
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

FORMAT = "hpo-replay/1"
DOMAIN = "heatpump_optimizer"
#: ``states_meta`` is where current Home Assistant keeps entity ids (#41).
MIN_SCHEMA = 41

ENTITY_ID = re.compile(r"^[a-z_]+\.[a-z0-9_]+$")
#: A key naming a credential. Matched on the whole key, case-insensitively,
#: so ``tibber_token``, ``access_token``, ``api_key`` and ``password`` all hit.
SECRET_KEY = re.compile(
    r"(token|password|passwd|secret|api_?key|credential|auth|webhook|cookie|"
    r"entity_picture)",
    re.I,
)
COORDINATE_KEYS = frozenset({"latitude", "longitude"})
MAX_COORDINATE_DECIMALS = 2
#: A string that carries a credential whatever key it sits under.
SECRET_TEXT = (
    re.compile(r"eyJ[\w-]{8,}\.[\w-]{8,}\."),  # a JWT
    re.compile(r"[?&](token|access_token|api_key)=", re.I),
    re.compile(r"\bbearer\s+\S{12,}", re.I),
)


# --- the rules ---------------------------------------------------------------


def json_decimal_places(value: object) -> int | None:
    """Decimal places in the JSON spelling -- ``tests/nightly_ha.py``'s rule."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        dumped = json.dumps(value)
    elif isinstance(value, str):
        try:
            float(value)
        except ValueError:
            return None
        dumped = value if "." in value else json.dumps(float(value))
    else:
        return None
    if "." not in dumped:
        return 0
    return len(dumped.split(".", 1)[1])


def sanitise(node: object, dropped: list[str]) -> object:
    """A copy of ``node`` with the credential keys gone and coordinates coarse.

    ``dropped`` collects the string value of every dropped key, so the caller
    can prove none of them survived anywhere else in the payload.
    """
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if SECRET_KEY.search(str(key)):
                _collect_strings(value, dropped)
                continue
            if key in COORDINATE_KEYS and isinstance(value, (int, float, str)) \
                    and not isinstance(value, bool):
                try:
                    out[key] = round(float(value), MAX_COORDINATE_DECIMALS)
                except ValueError:
                    out[key] = value
                continue
            out[key] = sanitise(value, dropped)
        return out
    if isinstance(node, list):
        return [sanitise(v, dropped) for v in node]
    if isinstance(node, str) and any(p.search(node) for p in SECRET_TEXT):
        dropped.append(node)
        return None
    return node


def _collect_strings(node: object, into: list[str]) -> None:
    if isinstance(node, str) and node:
        into.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            _collect_strings(value, into)
    elif isinstance(node, list):
        for value in node:
            _collect_strings(value, into)


def violations(payload: object, path: str = "") -> list[str]:
    """Every place ``payload`` breaks a rule. Empty means committable."""
    found: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            here = f"{path}.{key}" if path else str(key)
            if SECRET_KEY.search(str(key)) and value not in (None, "", [], {}):
                found.append(f"{here}: a credential-named key carries a value")
            if key in COORDINATE_KEYS:
                places = json_decimal_places(value)
                if places is not None and places > MAX_COORDINATE_DECIMALS:
                    found.append(f"{here}={value!r}: {places} decimals")
            found.extend(violations(value, here))
    elif isinstance(payload, list):
        for i, value in enumerate(payload):
            found.extend(violations(value, f"{path}[{i}]"))
    elif isinstance(payload, str):
        for pattern in SECRET_TEXT:
            if pattern.search(payload):
                found.append(f"{path}: text matching {pattern.pattern!r}")
    return found


def check_file(path: Path) -> list[str]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError) as err:
        return [f"{path}: unreadable ({err})"]
    found = violations(payload)
    if not isinstance(payload, dict) or payload.get("format") != FORMAT:
        found.insert(0, f"format is not {FORMAT!r}")
    return found


# --- reading the install -----------------------------------------------------


def _storage(config_dir: Path, name: str) -> dict:
    return json.loads((config_dir / ".storage" / name).read_text())["data"]


def mapped_entities(node: object) -> set[str]:
    """Every value in the entry spelled like an entity id, at any depth."""
    found: set[str] = set()
    if isinstance(node, str) and ENTITY_ID.match(node):
        found.add(node)
    elif isinstance(node, dict):
        for value in node.values():
            found |= mapped_entities(value)
    elif isinstance(node, list):
        for value in node:
            found |= mapped_entities(value)
    return found


def _open_ro(db: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def _schema_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT MAX(schema_version) FROM schema_changes").fetchone()
    return int(row[0] or 0)


def _iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def read_states(
    conn: sqlite3.Connection, entity_id: str, start: float, end: float
) -> list[list]:
    """``[updated, state, attributes | None, reported | None]`` rows.

    Attributes are written only when they differ from the previous row's, so
    a thermometer's unchanged unit is not repeated a thousand times a day.
    """
    cols = {r[1] for r in conn.execute("PRAGMA table_info(states)")}
    reported = "s.last_reported_ts" if "last_reported_ts" in cols else "NULL"
    base = (
        f"SELECT s.last_updated_ts, {reported}, s.state, a.shared_attrs "
        "FROM states s JOIN states_meta m ON s.metadata_id = m.metadata_id "
        "LEFT JOIN state_attributes a ON s.attributes_id = a.attributes_id "
        "WHERE m.entity_id = ? "
    )
    before = conn.execute(
        base + "AND s.last_updated_ts < ? ORDER BY s.last_updated_ts DESC LIMIT 1",
        (entity_id, start),
    ).fetchall()
    inside = conn.execute(
        base + "AND s.last_updated_ts >= ? AND s.last_updated_ts < ? "
        "ORDER BY s.last_updated_ts",
        (entity_id, start, end),
    ).fetchall()
    rows: list[list] = []
    last_attrs: object = object()
    for updated, rep, state, shared in before + inside:
        try:
            attrs = json.loads(shared) if shared else {}
        except ValueError:
            attrs = {}
        row = [_iso(updated), state, None, _iso(rep) if rep and rep > updated else None]
        if attrs != last_attrs:
            row[2] = attrs
            last_attrs = attrs
        rows.append(row)
    return rows


def build_export(
    config_dir: Path,
    db: Path,
    days: int,
    end_date: str | None,
    entry_id: str | None,
    extra: list[str],
    price_entity: str | None,
) -> dict:
    entries = [
        e for e in _storage(config_dir, "core.config_entries")["entries"]
        if e.get("domain") == DOMAIN
        and (entry_id is None or e.get("entry_id") == entry_id)
    ]
    if len(entries) != 1:
        raise SystemExit(
            f"found {len(entries)} {DOMAIN} config entries; pass --entry-id"
            if entries else f"no {DOMAIN} config entry in {config_dir}"
        )
    entry = entries[0]
    tz_name = _storage(config_dir, "core.config").get("time_zone") or "UTC"
    tz = ZoneInfo(tz_name)
    if end_date:
        end_day = datetime.fromisoformat(end_date).date()
    else:
        end_day = datetime.now(tz).date()
    end = datetime.combine(end_day, time(0), tz)
    start = datetime.combine(end_day - timedelta(days=days), time(0), tz)

    inputs = mapped_entities(entry.get("data", {})) | mapped_entities(
        entry.get("options", {})
    )
    inputs |= set(extra)
    if price_entity:
        inputs.add(price_entity)
    published = sorted(
        e["entity_id"]
        for e in _storage(config_dir, "core.entity_registry")["entities"]
        if e.get("platform") == DOMAIN
        and e.get("config_entry_id") == entry.get("entry_id")
    )
    conn = _open_ro(db)
    try:
        version = _schema_version(conn)
        if version < MIN_SCHEMA:
            raise SystemExit(
                f"recorder schema {version} predates states_meta ({MIN_SCHEMA}); "
                "upgrade Home Assistant or export by the History API instead"
            )
        states = {
            eid: read_states(conn, eid, start.timestamp(), end.timestamp())
            for eid in sorted(inputs | set(published))
        }
    finally:
        conn.close()

    raw = {
        "format": FORMAT,
        "time_zone": tz_name,
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "recorder_schema": version,
        "entry": {
            "version": entry.get("version"),
            "minor_version": entry.get("minor_version"),
            "data": entry.get("data", {}),
            "options": entry.get("options", {}),
        },
        "inputs": sorted(inputs),
        "published": published,
        "price_series_entity": price_entity,
        "states": states,
    }
    dropped: list[str] = []
    clean = sanitise(raw, dropped)
    blob = json.dumps(clean, sort_keys=True)
    leaked = sorted({s for s in dropped if len(s) >= 6 and s in blob})
    if leaked:
        raise SystemExit(
            f"refusing to write: {len(leaked)} dropped credential value(s) "
            "survive elsewhere in the payload"
        )
    left = violations(clean)
    if left:
        raise SystemExit("refusing to write: " + "; ".join(left[:5]))
    return clean


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config-dir", type=Path, default=Path("/config"))
    ap.add_argument("--db", type=Path, help="default <config-dir>/home-assistant_v2.db")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--end", help="local date the window ends on (exclusive), YYYY-MM-DD")
    ap.add_argument("--entry-id", help="needed only with more than one entry")
    ap.add_argument("--extra-entity", action="append", default=[])
    ap.add_argument(
        "--price-entity",
        help="with the Tibber source: a recorded price sensor (its state is "
        "the price) the replay builds the day's series from",
    )
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", type=Path, metavar="FILE",
                    help="refuse FILE if it breaks a sanitising rule")
    args = ap.parse_args(argv)

    if args.check:
        found = check_file(args.check)
        for line in found:
            print(f"  VIOLATION {line}")
        print(f"{args.check}: {len(found)} violation(s)")
        return 1 if found else 0
    if not args.out:
        ap.error("--out is required unless --check is given")
    payload = build_export(
        args.config_dir,
        args.db or args.config_dir / "home-assistant_v2.db",
        args.days,
        args.end,
        args.entry_id,
        args.extra_entity,
        args.price_entity,
    )
    args.out.write_text(json.dumps(payload, sort_keys=True, indent=1) + "\n")
    rows = sum(len(v) for v in payload["states"].values())
    print(
        f"wrote {args.out}: {len(payload['states'])} entities, {rows} state rows, "
        f"{payload['window']['start']} .. {payload['window']['end']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
