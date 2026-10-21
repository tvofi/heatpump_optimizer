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
the interpreter inside the Home Assistant container as it is -- and the rules
below, which it loads by path from the integration's own
``custom_components/heatpump_optimizer/replay_doc.py`` (the checkout's, else a
copy beside this file, else the one installed under ``/config``), because
Download diagnostics writes the same document through the same rules (#2271).

WHAT IT EXPORTS, for the window ``[end - days, end)`` in the instance's zone:
every entity id the config entry maps (any value in ``data`` or ``options``
spelled like an entity id -- thermometers, the price and weather entities, the
pump's mode, switch, power and valve entities), the entities this integration
publishes (from the registry; carried for comparison, never fed back), and any
``--extra-entity``. For each, the last state before the window and every state
inside it.

WITH THE TIBBER PRICE SOURCE the integration fetches prices itself, so the
replay builds the day's series from a recorded price sensor
(``price_series_entity``). ``--price-entity`` names it; without the flag the
export takes the Tibber integration's own price sensor from the entity
registry (``tibber_price_candidates``) that has a numeric state in the
window, says which on stderr, and refuses -- listing the candidates -- when
there is none or, with several homes, when the entry's ``price_entity`` does
not name one of them.

WHAT IT KEEPS is an allowlist, because the file goes into a public
repository:

* entry keys that are this integration's own ``CONF_*`` names (read from the
  installed ``const.py``); a key naming an entity (``*_entity``) must hold an
  entity id, and ``*_entities`` only entity ids;
* the state attributes the replay reads (``ATTRIBUTE_KEYS``), each cut to its
  shape (``ATTRIBUTE_SHAPES``): numbers where numbers belong, a three-letter
  currency, select options as short word labels with no digits, price series
  as rows of an ISO time and a number and nothing else;
* string values, at any depth, that are an entity id, a number, an ISO time or
  a short label -- letters first, none of ``@ : , ?``, no run of four digits,
  no host followed by a path (``nas.example.se/x``, scheme or not), no run of
  twelve hex digits (a MAC without separators).

Every key naming a credential is dropped wherever it occurs, and every
coordinate key (``latitude``, ``lat``, ``lon``, any case) is cut to two
decimals, the rule ``tests/nightly_ha.py``'s A10 checks apply to diagnostics.
The export then searches its own output for every unsafe string it removed,
and refuses to write if one survives.

WHAT IT CANNOT REMOVE, because the rules above judge a string's shape and
not its meaning, so a person reads the file before it is committed:

* any text state, and any entry value under a key not naming an entity, of
  up to 40 characters that starts with a letter and breaks none of the rules
  above -- several words and short numbers included: a full name, a street
  and house number ("Storgatan 12"), a bare hostname, a random-looking token;
* the same for units (up to 16 characters) and for ``device_class``,
  ``state_class`` and ``hvac_action`` (any ``[a-z_]`` word up to 32
  characters, a snake-case name included) -- and a select's option labels
  (no digits, otherwise the same);
* entity ids, which the user named and which may embed a name, a street or a
  device's MAC (``sensor.anna_storgatan_power``);
* numbers: a state, a numeric attribute or a price or forecast value is kept
  whatever it is, so a coordinate published as a sensor's state or a long
  number survives -- only keys named as coordinates are rounded.

``--check FILE`` applies the same rules to a file already written and exits 1
on any violation; ``tests/replay.py`` runs it on every committed fixture.

    python3 export.py --config-dir /config --days 7 --out /config/hpo-replay.json
    python3 export.py --config-dir /config --days 7 --out /config/hpo-replay.json \\
        --price-entity sensor.electricity_price_home   # only to override the pick
    python3 export.py --check /config/hpo-replay.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DOMAIN = "heatpump_optimizer"
#: ``states_meta`` is where current Home Assistant keeps entity ids (#41).
MIN_SCHEMA = 41
HERE = Path(__file__).resolve().parent
_RULES = Path("custom_components") / DOMAIN / "replay_doc.py"


def _load(path: Path, name: str):
    """A module of the integration, loaded by path: the package's ``__init__``
    imports Home Assistant, and this file runs without it."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_rules():
    for path in (HERE.parent.parent / _RULES, HERE / _RULES.name, Path("/config") / _RULES):
        if path.is_file():
            return _load(path, "hpo_replay_doc")
    raise SystemExit(f"no {_RULES} found; copy it beside {Path(__file__).name}")


_doc = _load_rules()
FORMAT = _doc.FORMAT
PRICE_SOURCE_ENTITY = _doc.PRICE_SOURCE_ENTITY
sanitise, violations, text_ok = _doc.sanitise, _doc.violations, _doc.text_ok
tibber_price_candidates, mapped_entities = _doc.tibber_price_candidates, _doc.mapped_entities


def choose_price_entity(config: dict, registry: list[dict], recorded) -> str:
    """``replay_doc.choose_price_entity``, its refusal this command's exit."""
    try:
        return _doc.choose_price_entity(config, registry, recorded)
    except _doc.Refused as err:
        raise SystemExit(str(err)) from None


def entry_keys(*candidates: Path) -> frozenset[str]:
    """``replay_doc.conf_keys`` of the first ``const.py`` that exists; refuses if none."""
    for path in candidates:
        if path.is_file():
            keys = _doc.conf_keys(vars(_load(path, "hpo_replay_const")))
            if keys:
                return keys
    raise SystemExit(
        "no heatpump_optimizer const.py found to take the entry allowlist from; "
        "pass --const PATH"
    )


def default_const_paths(config_dir: Path | None = None) -> list[Path]:
    rel = Path("custom_components") / DOMAIN / "const.py"
    out = [config_dir / rel] if config_dir else []
    return out + [HERE / rel, HERE.parent.parent / rel]


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
    """``replay_doc.state_rows`` of the entity's rows: the last before ``start``,
    then every one in ``[start, end)``."""
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
    return _doc.state_rows(
        (_iso(updated), state, _attributes(shared), _iso(rep) if rep and rep > updated else None)
        for updated, rep, state, shared in before + inside
    )


def _attributes(shared: str | None) -> dict:
    try:
        return json.loads(shared) if shared else {}
    except ValueError:
        return {}


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
    registry = _storage(config_dir, "core.entity_registry")["entities"]
    published = sorted(
        e["entity_id"]
        for e in registry
        if e.get("platform") == DOMAIN
        and e.get("config_entry_id") == entry.get("entry_id")
    )
    config = {**entry.get("data", {}), **entry.get("options", {})}
    conn = _open_ro(db)
    try:
        version = _schema_version(conn)
        if version < MIN_SCHEMA:
            raise SystemExit(
                f"recorder schema {version} predates states_meta ({MIN_SCHEMA}); "
                "upgrade Home Assistant or export by the History API instead"
            )
        if not price_entity and config.get("price_source") != PRICE_SOURCE_ENTITY:
            price_entity = choose_price_entity(
                config, registry,
                lambda eid: any(_doc.numeric(row[1]) for row in read_states(
                    conn, eid, start.timestamp(), end.timestamp())))
            print(f"price series from the Tibber price sensor {price_entity} "
                  "(--price-entity overrides)", file=sys.stderr)
        if price_entity:
            inputs.add(price_entity)
        states = {
            eid: read_states(conn, eid, start.timestamp(), end.timestamp())
            for eid in sorted(inputs | set(published))
        }
    finally:
        conn.close()

    raw = _doc.document(
        time_zone=tz_name, window=(start.isoformat(), end.isoformat()),
        recorder_schema=version, entry=entry, inputs=inputs, published=published,
        price_series_entity=price_entity, states=states,
    )
    try:
        return _doc.seal(raw, entry_keys(*([const] if const else default_const_paths(config_dir))))
    except _doc.Refused as err:
        raise SystemExit(str(err)) from None

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
        "the price) the replay builds the day's series from; default: the one "
        "Tibber price sensor the entity registry and the recorder hold",
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
