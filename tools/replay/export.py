#!/usr/bin/env python3
"""Export recorded days from a Home Assistant install for the replay lane.

Run on the owner's own Home Assistant box. It reads, and only reads:

* the recorder's database (the ``states``, ``states_meta``,
  ``state_attributes`` and ``schema_changes`` tables of the current schema;
  ``states_meta`` arrived in schema 41, so an older database is refused by
  name), SELECTs only. Which database: ``--db-url``, else ``--db``, else the
  ``db_url`` configuration.yaml's ``recorder:`` names (inline or by
  ``!include``, a ``!secret`` resolved through secrets.yaml), else
  ``<config>/home-assistant_v2.db``. SQLite is opened with ``mode=ro``;
  MySQL/MariaDB through the driver the Home Assistant container ships
  (``MySQLdb``, else ``pymysql``), found at run time, in a read-only session.
  The URL's credentials are never printed, logged or written: the recorder is
  named as ``scheme://host/database``;
* ``<config>/.storage/core.config_entries`` -- this integration's entry;
* ``<config>/.storage/core.entity_registry`` -- the entities it publishes;
* ``<config>/.storage/core.config`` -- the instance's time zone.

It opens no socket but the database's, for a ``db_url`` recorder. The
standard library is all it imports on the SQLite path, so it runs under the
interpreter inside the Home Assistant container as it is -- and the rules
below, which it loads by path from the integration's own
``custom_components/heatpump_optimizer/replay_doc.py`` (the checkout's, else a
copy beside this file, else the one installed under ``/config``), because
Download diagnostics writes the same document through the same rules (#2271).

WHAT IT EXPORTS, for the window ``[end - days, end)`` in the instance's zone:
every entity id the config entry maps under a key the installed integration
reads (any value in ``data`` or ``options`` spelled like an entity id, under a
``CONF_*`` key; a key a release retired is named on stderr and left out --
thermometers, the price and weather entities, the
pump's mode, switch, power and valve entities), the entities this integration
publishes (from the registry; carried for comparison, never fed back), and any
``--extra-entity``. For each, the last state before the window and every state
inside it. It refuses a window in which a mapped input has no state, updated
or reported -- naming the inputs by their masked role and the recorder it read
-- because a near-empty day passes every other rule.

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
  above -- several words and short numbers included: a full name, a bare
  hostname, a random-looking token;
* the same for units (up to 16 characters) and for ``device_class``,
  ``state_class`` and ``hvac_action`` (any ``[a-z_]`` word up to 32
  characters, a snake-case name included) -- and a select's option labels
  (no digits, otherwise the same);
* nothing of the entity ids, which the user named and which may embed a
  name, a street or a device's MAC: ``replay_doc.mask`` renames every one to
  a role (``sensor.price``) or a keyed hash, and a street and house number in
  any text is dropped (``replay_doc.ADDRESS``);
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
import importlib
import importlib.util
import json
import re
import sqlite3
import sys
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
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
    found = _doc.refusals(
        payload, conf if conf is not None else entry_keys(*default_const_paths()))
    if not isinstance(payload, dict) or payload.get("format") != FORMAT:
        found.insert(0, f"format is not {FORMAT!r}")
    return found


# --- reading the install -----------------------------------------------------


def _storage(config_dir: Path, name: str) -> dict:
    return json.loads((config_dir / ".storage" / name).read_text())["data"]


def _yaml_scalar(text: str) -> str:
    """A one-line YAML scalar: quoted, or plain with its trailing comment cut."""
    text = text.strip()
    if text[:1] in "\"'" and len(text) > 1 and text[-1] == text[0]:
        return text[1:-1]
    return re.split(r"\s+#", text, maxsplit=1)[0].strip()


def _top_key(text: str, key: str) -> tuple[str, list[str]] | None:
    """A top-level ``key:``'s inline value and its indented block's lines."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        found = re.match(rf"^{re.escape(key)}:(.*)$", line)
        if found:
            block = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt[:1].isspace():
                    break
                block.append(nxt)
            return found.group(1), block
    return None


def _secret(config_dir: Path, value: str) -> str:
    tag = re.match(r"^!secret\s+(\S+)$", value)
    if not tag:
        return value
    secrets = config_dir / "secrets.yaml"
    hit = _top_key(secrets.read_text(), tag.group(1)) if secrets.is_file() else None
    if hit is None:
        raise SystemExit(f"configuration.yaml's recorder db_url names !secret "
                         f"{tag.group(1)}, which {secrets} does not hold")
    return _yaml_scalar(hit[0])


def recorder_url(config_dir: Path) -> str | None:
    """The ``db_url`` of configuration.yaml's top-level ``recorder:``, written
    inline or in the file its ``!include`` names, a ``!secret`` resolved; None
    without one, which is the default SQLite file."""
    path = config_dir / "configuration.yaml"
    hit = _top_key(path.read_text(), "recorder") if path.is_file() else None
    if hit is None:
        return None
    inline, block = hit
    include = re.match(r"^\s*!include\s+(\S+)", inline)
    if include:
        included = config_dir / include.group(1)
        block = included.read_text().splitlines() if included.is_file() else []
    depth = min((len(b) - len(b.lstrip()) for b in block if b.strip()), default=0)
    for line in block:
        found = re.match(rf"^ {{{depth}}}db_url:(.*)$", line)
        if found:
            return _secret(config_dir, _yaml_scalar(found.group(1)))
    return None


def redacted(url: str) -> str:
    """``scheme://host[:port]/database``: the URL with no user, password or query."""
    parts = urlsplit(url)
    port = f":{parts.port}" if parts.port else ""
    return f"{parts.scheme}://{parts.hostname or ''}{port}{parts.path}"


class Recorder:
    """The recorder database through DB-API, its SQL written once with ``?``
    placeholders and rewritten to the driver's ``%s`` where it uses that."""

    def __init__(self, conn, label: str, qmark: bool) -> None:
        self.conn, self.label, self.qmark = conn, label, qmark

    def rows(self, sql: str, params: tuple = ()) -> list[tuple]:
        cur = self.conn.cursor()
        try:
            cur.execute(sql if self.qmark else sql.replace("?", "%s"), params)
            return [tuple(r) for r in cur.fetchall()]
        finally:
            cur.close()

    def columns(self, table: str) -> set[str]:
        cur = self.conn.cursor()
        try:
            cur.execute(f"SELECT * FROM {table} WHERE 1 = 0")
            return {d[0] for d in cur.description}
        finally:
            cur.close()

    def close(self) -> None:
        self.conn.close()


#: The MySQL/MariaDB DB-API drivers, in the order tried: what SQLAlchemy's
#: ``mysql://`` resolves to in the Home Assistant container, then the pure one.
MYSQL_DRIVERS = ("MySQLdb", "pymysql")


def _mysql(url: str) -> Recorder:
    parts, label = urlsplit(url), redacted(url)
    wanted = ("pymysql",) if parts.scheme.endswith("+pymysql") else MYSQL_DRIVERS
    module = None
    for name in wanted:
        try:
            module = importlib.import_module(name)
            break
        except ImportError:
            continue
    if module is None:
        raise SystemExit(
            f"the recorder {label} is MySQL/MariaDB, and reading it needs the "
            f"{' or '.join(wanted)} module, which the Home Assistant container ships: "
            "run this inside it (the SSH add-on's `docker exec -it homeassistant`)")
    query = {k: v[-1] for k, v in parse_qs(parts.query).items()}
    kwargs = {"host": parts.hostname or "localhost", "user": unquote(parts.username or ""),
              "password": unquote(parts.password or ""), "database": parts.path.lstrip("/"),
              "charset": query.get("charset", "utf8mb4")}
    if parts.port:
        kwargs["port"] = parts.port
    if "unix_socket" in query:
        kwargs["unix_socket"] = query["unix_socket"]
    try:
        conn = module.connect(**kwargs)
        cur = conn.cursor()
        cur.execute("SET SESSION TRANSACTION READ ONLY")
        cur.close()
    except Exception as err:  # noqa: BLE001 - its text can carry the user name
        raise SystemExit(f"cannot open the recorder {label} read-only: "
                         f"{type(err).__name__}") from None
    return Recorder(conn, label, qmark=False)


def open_recorder(config_dir: Path, db: Path | None, db_url: str | None) -> Recorder:
    """The recorder ``--db-url``, ``--db``, configuration.yaml or the default names."""
    url = db_url or (None if db else recorder_url(config_dir))
    if url and not url.startswith("sqlite"):
        if not url.split(":", 1)[0].split("+", 1)[0] in ("mysql", "mariadb"):
            raise SystemExit(f"the recorder {redacted(url)} is neither SQLite nor "
                             "MySQL/MariaDB, the two this export reads")
        return _mysql(url)
    if url:
        db = Path(urlsplit(url).path[1:] if url.startswith("sqlite:////") else
                  config_dir / urlsplit(url).path.lstrip("/"))
    db = db or config_dir / "home-assistant_v2.db"
    return Recorder(sqlite3.connect(f"file:{db}?mode=ro", uri=True), f"SQLite {db}", qmark=True)


def _schema_version(rec: Recorder) -> int:
    return int(rec.rows("SELECT MAX(schema_version) FROM schema_changes")[0][0] or 0)


def _iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, timezone.utc).isoformat()


def read_states(rec: Recorder, entity_id: str, start: float, end: float) -> list[list]:
    """``replay_doc.state_rows`` of the entity's rows: the last before ``start``,
    then every one in ``[start, end)``."""
    cols = rec.columns("states")
    reported = "s.last_reported_ts" if "last_reported_ts" in cols else "NULL"
    base = (
        f"SELECT s.last_updated_ts, {reported}, s.state, a.shared_attrs "
        "FROM states s JOIN states_meta m ON s.metadata_id = m.metadata_id "
        "LEFT JOIN state_attributes a ON s.attributes_id = a.attributes_id "
        "WHERE m.entity_id = ? "
    )
    before = rec.rows(
        base + "AND s.last_updated_ts < ? ORDER BY s.last_updated_ts DESC LIMIT 1",
        (entity_id, start))
    inside = rec.rows(
        base + "AND s.last_updated_ts >= ? AND s.last_updated_ts < ? "
        "ORDER BY s.last_updated_ts",
        (entity_id, start, end))
    return _doc.state_rows(
        (_iso(updated), _text(state), _attributes(shared),
         _iso(rep) if rep and rep > updated else None)
        for updated, rep, state, shared in before + inside
    )


def _text(value: object) -> object:
    """A MySQL driver can hand a text column back as bytes."""
    return value.decode() if isinstance(value, (bytes, bytearray)) else value


def _attributes(shared: object) -> dict:
    try:
        return json.loads(_text(shared)) if shared else {}
    except ValueError:
        return {}


def quiet_inputs(doc: dict) -> list[str]:
    """The (masked) inputs with no state updated or reported inside the window."""
    start = datetime.fromisoformat(doc["window"]["start"])
    return [eid for eid in doc["inputs"] if not any(
        any(t and datetime.fromisoformat(t) >= start for t in (row[0], row[3]))
        for row in doc["states"].get(eid, []))]


def build_export(
    config_dir: Path,
    db: Path | None,
    days: int,
    end_date: str | None,
    entry_id: str | None,
    extra: list[str],
    price_entity: str | None,
    const: Path | None = None,
    db_url: str | None = None,
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

    # An input is an id under a key the installed integration reads: an old
    # entry can keep a key a release retired (``heat_pump_entity``, v3.8.0),
    # whose entity nothing reads and the recorder may long have stopped writing.
    conf = entry_keys(*([const] if const else default_const_paths(config_dir)))
    sections = [entry.get("data", {}), entry.get("options", {})]
    retired = sorted({k for sec in sections for k, v in sec.items()
                      if k not in conf and mapped_entities(v)})
    if retired:
        print(f"left out: entity id(s) under {len(retired)} entry key(s) this integration "
              f"does not read ({', '.join(retired)})", file=sys.stderr)
    inputs = set().union(*(mapped_entities({k: v for k, v in sec.items() if k in conf})
                           for sec in sections))
    inputs |= set(extra)
    registry = _storage(config_dir, "core.entity_registry")["entities"]
    published = sorted(
        e["entity_id"]
        for e in registry
        if e.get("platform") == DOMAIN
        and e.get("config_entry_id") == entry.get("entry_id")
    )
    config = {**entry.get("data", {}), **entry.get("options", {})}
    rec = open_recorder(config_dir, db, db_url)
    print(f"reading the recorder {rec.label}", file=sys.stderr)
    try:
        version = _schema_version(rec)
        if version < MIN_SCHEMA:
            raise SystemExit(
                f"recorder schema {version} predates states_meta ({MIN_SCHEMA}); "
                "upgrade Home Assistant or export by the History API instead"
            )
        if not price_entity and config.get("price_source") != PRICE_SOURCE_ENTITY:
            price_entity = choose_price_entity(
                config, registry,
                lambda eid: any(_doc.numeric(row[1]) for row in read_states(
                    rec, eid, start.timestamp(), end.timestamp())))
            print("price series from the one Tibber price sensor the registry and the "
                  "recorder agree on, masked as sensor.price (--price-entity overrides)",
                  file=sys.stderr)
        if price_entity:
            inputs.add(price_entity)
        states = {
            eid: read_states(rec, eid, start.timestamp(), end.timestamp())
            for eid in sorted(inputs | set(published))
        }
    finally:
        rec.close()

    raw = _doc.document(
        time_zone=tz_name, window=(start.isoformat(), end.isoformat()),
        recorder_schema=version, entry=entry, inputs=inputs, published=published,
        price_series_entity=price_entity, states=states,
    )
    quiet = quiet_inputs(raw)
    if quiet:
        raise SystemExit(
            f"refusing to write: the recorder {rec.label} holds no state in "
            f"[{start.isoformat()}, {end.isoformat()}) for {len(quiet)} of "
            f"{len(raw['inputs'])} mapped input(s): {', '.join(quiet)} (masked ids; "
            "is this the recorder Home Assistant writes?)")
    try:
        return _doc.seal(raw, conf)
    except _doc.Refused as err:
        raise SystemExit(str(err)) from None

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--config-dir", type=Path, default=Path("/config"))
    ap.add_argument("--db", type=Path, help="a SQLite recorder file; default: the db_url "
                    "configuration.yaml's recorder names, else "
                    "<config-dir>/home-assistant_v2.db")
    ap.add_argument("--db-url", help="the recorder's URL, over --db and configuration.yaml; "
                    "prefer configuration.yaml's, which keeps the password off the "
                    "command line")
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
        args.db,
        args.days,
        args.end,
        args.entry_id,
        args.extra_entity,
        args.price_entity,
        args.const,
        args.db_url,
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
