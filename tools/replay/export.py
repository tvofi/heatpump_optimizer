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

WHAT IT KEEPS is an allowlist, because the file goes into a public
repository: the entry's keys that are this integration's own ``CONF_*`` names
(read from the installed ``const.py``), the state attributes the replay reads
(``ATTRIBUTE_KEYS``), and string values that are an entity id, a number, an
ISO time or a short word-like label. Everything else is dropped or nulled --
friendly names, addresses, URLs, e-mails, serials, MACs. On top of that, every
key naming a credential is dropped wherever it occurs (``tibber_token``
included), and every coordinate key (``latitude``, ``lat``, ``lon``, any
case) is cut to two decimals, the rule ``tests/nightly_ha.py``'s A10 checks
apply to diagnostics. The export then searches its own output for every
unsafe value it removed, and refuses to write if one survives.

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
    r"entity_picture|pin$|pin_|passcode|access_code|psk|private_key|email|"
    r"serial|mac_?address|^mac$)",
    re.I,
)
#: Keys whose number is a coordinate, in any capitalisation.
COORDINATE_KEYS = frozenset({"latitude", "longitude", "lat", "lon", "lng"})
MAX_COORDINATE_DECIMALS = 2
#: A string that carries a credential whatever key it sits under.
SECRET_TEXT = (
    re.compile(r"eyJ[\w-]{8,}\.[\w-]{8,}\."),  # a JWT
    re.compile(r"[?&](token|access_token|api_?key)=", re.I),
    re.compile(r"\bbearer\s+\S{12,}", re.I),
)

# THE ALLOWLIST. The export goes into a public repository, so what leaves the
# install is what the replay reads and nothing else; a denylist of secret
# names let eleven constructed leaks through (review of #1508). Three parts:
#
# * entry keys: the integration's own ``CONF_*`` names, parsed from the
#   installed ``const.py`` -- so the list cannot drift from the release;
# * attribute keys: the ones the integration reads off an input's state
#   (unit, device class, options, the weather and price series, the away
#   calendar's span) plus the few published ones the replay compares;
# * every string value, at any depth, must be an entity id, a number, an ISO
#   time, or a short word-like label (letters first; no ``@ : , ?``; no run
#   of four digits). Anything else -- an address, a URL, an e-mail, a MAC, a
#   serial, a "lat,lon" pair -- is redacted to null.
ATTRIBUTE_KEYS = frozenset({
    "unit_of_measurement", "device_class", "state_class", "options",
    "temperature", "temperature_unit", "wind_speed", "wind_speed_unit",
    "precipitation", "precipitation_unit",
    "raw_today", "raw_tomorrow", "today", "tomorrow", "currency",
    "min", "max", "start_time", "end_time",
    "hvac_action", "current_temperature", "heat_pump_on", "power_kw",
})
KEY = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)?$")  # a key, or an entity id
LABEL = re.compile(r"^[A-Za-z\u00b0][A-Za-z0-9 _+\-./()\u00b0%\u00b2\u00b3]{0,39}$")
ISO_TIME = re.compile(r"^\d{4}-\d\d-\d\d([T ][\d:.]+([+-]\d\d:\d\d|Z)?)?$")
CONST_PATTERN = re.compile(r'^CONF_\w+: Final = "([a-z0-9_]+)"', re.M)


def entry_keys(*candidates: Path) -> frozenset[str]:
    """The ``CONF_*`` values of the first ``const.py`` that exists; refuses if none."""
    for path in candidates:
        if path.is_file():
            keys = frozenset(CONST_PATTERN.findall(path.read_text()))
            if keys:
                return keys
    raise SystemExit(
        "no heatpump_optimizer const.py found to take the entry allowlist from; "
        "pass --const PATH"
    )


def default_const_paths(config_dir: Path | None = None) -> list[Path]:
    here = Path(__file__).resolve().parent
    rel = Path("custom_components") / DOMAIN / "const.py"
    out = [config_dir / rel] if config_dir else []
    return out + [here / rel, here.parent.parent / rel]


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


def text_ok(value: str) -> bool:
    """Whether a string may leave the install."""
    if value == "" or ENTITY_ID.match(value) or ISO_TIME.match(value):
        return True
    if any(p.search(value) for p in SECRET_TEXT):
        return False
    try:
        float(value)
        return "," not in value
    except ValueError:
        pass
    return bool(LABEL.match(value)) and not re.search(r"\d{4}", value)


def _is_coordinate(key: str) -> bool:
    return str(key).lower() in COORDINATE_KEYS


def clean_value(node: object, dropped: list[str]) -> object:
    """``node`` with every unsafe string nulled, every unsafe key gone."""
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if SECRET_KEY.search(str(key)) or not KEY.match(str(key)):
                _collect_strings(value, dropped, bool(SECRET_KEY.search(str(key))))
                continue
            if _is_coordinate(key) and isinstance(value, (int, float, str)) \
                    and not isinstance(value, bool):
                try:
                    out[key] = round(float(value), MAX_COORDINATE_DECIMALS)
                except ValueError:
                    dropped.append(str(value))
                    out[key] = None
                continue
            out[key] = clean_value(value, dropped)
        return out
    if isinstance(node, list):
        return [clean_value(v, dropped) for v in node]
    if isinstance(node, str) and not text_ok(node):
        dropped.append(node)
        return None
    return node


def _keep_keys(section: object, allowed: frozenset[str], dropped: list[str]) -> dict:
    out = {}
    for key, value in (section if isinstance(section, dict) else {}).items():
        if key in allowed and not SECRET_KEY.search(str(key)):
            out[key] = value
        else:
            _collect_strings(value, dropped, bool(SECRET_KEY.search(str(key))))
    return clean_value(out, dropped)


def sanitise(raw: dict, conf: frozenset[str], dropped: list[str]) -> dict:
    """The export payload cut down to the allowlist.

    ``dropped`` collects every string removed, so the caller can prove none
    of them survived anywhere else in the payload.
    """
    out = dict(raw)
    entry = dict(raw["entry"])
    entry["data"] = _keep_keys(entry.get("data"), conf, dropped)
    entry["options"] = _keep_keys(entry.get("options"), conf, dropped)
    out["entry"] = entry
    states = {}
    for entity_id, rows in raw["states"].items():
        clean_rows = []
        for updated, state, attrs, reported in rows:
            if attrs is not None:
                attrs = _keep_keys(attrs, ATTRIBUTE_KEYS, dropped)
            if isinstance(state, str) and not text_ok(state):
                dropped.append(state)
                state = None
            clean_rows.append([updated, state, attrs, reported])
        states[entity_id] = clean_rows
    out["states"] = states
    return clean_value(out, dropped)


def _collect_strings(node: object, into: list[str], secret: bool = False) -> None:
    """Collect what the leak check must not find again: every value under a
    credential-named key, and every string that fails ``text_ok`` elsewhere.
    A plain label dropped only for sitting under an unlisted key ("Hot water",
    a friendly name) may legitimately appear elsewhere, so it is not collected."""
    if isinstance(node, bool) or node is None:
        return
    if isinstance(node, (str, int, float)):
        text = str(node)
        if text and (secret or (isinstance(node, str) and not text_ok(node))):
            into.append(text)
    elif isinstance(node, dict):
        for key, value in node.items():
            _collect_strings(value, into, secret or bool(SECRET_KEY.search(str(key))))
    elif isinstance(node, list):
        for value in node:
            _collect_strings(value, into, secret)


def _walk(node: object, path: str, found: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            if SECRET_KEY.search(str(key)) and value not in (None, "", [], {}):
                found.append(f"{here}: a credential-named key carries a value")
            if _is_coordinate(key):
                places = json_decimal_places(value)
                if places is not None and places > MAX_COORDINATE_DECIMALS:
                    found.append(f"{here}={value!r}: {places} decimals")
            _walk(value, here, found)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            _walk(value, f"{path}[{i}]", found)
    elif isinstance(node, str) and not text_ok(node):
        found.append(f"{path}: text outside the allowlist")


def violations(payload: object, conf: frozenset[str] | None = None) -> list[str]:
    """Every place ``payload`` breaks a rule. Empty means committable.

    Without ``conf`` the entry's keys are judged by shape only; ``check_file``
    always passes the installed allowlist.
    """
    found: list[str] = []
    _walk(payload, "", found)
    if not isinstance(payload, dict):
        return found
    for section in ("data", "options"):
        block = (payload.get("entry") or {}).get(section) or {}
        for key in block:
            if (conf is not None and key not in conf) or not KEY.match(str(key)):
                found.append(f"entry.{section}.{key}: not an entry key of this integration")
    for entity_id, rows in (payload.get("states") or {}).items():
        if not ENTITY_ID.match(str(entity_id)):
            found.append(f"states.{entity_id}: not an entity id")
        for i, row in enumerate(rows if isinstance(rows, list) else []):
            attrs = row[2] if isinstance(row, list) and len(row) > 2 else None
            for key in (attrs or {}):
                if key not in ATTRIBUTE_KEYS:
                    found.append(f"states.{entity_id}[{i}].{key}: attribute outside the allowlist")
    return found


def check_file(path: Path, conf: frozenset[str] | None = None) -> list[str]:
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError) as err:
        return [f"{path}: unreadable ({err})"]
    found = violations(payload, conf if conf is not None else entry_keys(*default_const_paths()))
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
    const: Path | None = None,
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
    conf = entry_keys(*([const] if const else default_const_paths(config_dir)))
    dropped: list[str] = []
    clean = sanitise(raw, conf, dropped)
    blob = json.dumps(clean, sort_keys=True)
    leaked = sorted({s for s in dropped if len(s) >= 6 and s in blob})
    if leaked:
        raise SystemExit(
            f"refusing to write: {len(leaked)} dropped credential value(s) "
            "survive elsewhere in the payload"
        )
    left = violations(clean, conf)
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
    ap.add_argument("--const", type=Path, help="the integration's const.py "
                    "(default: <config-dir>/custom_components/heatpump_optimizer/const.py)")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", type=Path, metavar="FILE",
                    help="refuse FILE if it breaks a sanitising rule")
    args = ap.parse_args(argv)

    if args.check:
        found = check_file(args.check, entry_keys(
            *([args.const] if args.const else default_const_paths(args.config_dir))))
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
        args.const,
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
