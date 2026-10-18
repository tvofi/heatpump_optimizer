"""The ``hpo-replay/1`` document: its allowlist, its sanitiser and ``violations``.

One copy, read by both writers of the document (#2271): ``tools/replay/export.py``,
which builds it from the recorder's SQLite file on the owner's box, and the
debug bundle's replay half (``debugger.py``), which builds it at download time
from Home Assistant's recorder history API. A rule changed here changes both,
and ``tests/replay.py`` checks each against the same ``violations``.

The export loads this file BY PATH, outside the package, under the interpreter
inside the Home Assistant container as it is: so it imports the standard
library and nothing else -- no ``homeassistant``, no sibling module.

WHAT IT KEEPS is an allowlist, because the file goes into a public
repository; ``tools/replay/export.py``'s docstring states it, with what it
cannot remove.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable, Iterable

FORMAT = "hpo-replay/1"

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
#: A host followed by a path, with or without a scheme ("nas.example.se/cam").
HOST_PATH = re.compile(r"[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+/")
#: Twelve hex digits in a row: a MAC written without separators.
HEX12 = re.compile(r"[0-9A-Fa-f]{12}")
SNAKE = re.compile(r"^[a-z_]{1,32}$")
CURRENCY = re.compile(r"^[A-Z]{3}$")
_DROP = object()
SERIES_TIME_KEYS = frozenset({"start", "end", "starts_at"})
SERIES_VALUE_KEYS = frozenset({"value", "price", "total"})
LABEL = re.compile(r"^[A-Za-z\u00b0][A-Za-z0-9 _+\-./()\u00b0%\u00b2\u00b3]{0,39}$")
ISO_TIME = re.compile(r"^\d{4}-\d\d-\d\d([T ][\d:.]+([+-]\d\d:\d\d|Z)?)?$")
CONST_PATTERN = re.compile(r'^CONF_\w+: Final = "([a-z0-9_]+)"', re.M)

# THE TIBBER PRICE SENSOR. With the Tibber source the integration fetches
# prices itself, so the replay needs a recorded sensor whose state is the
# price. Home Assistant core's Tibber integration publishes one per home with
# an active subscription (homeassistant/components/tibber/sensor.py,
# ``TibberSensorElPrice``, at core commit a108a5c3d7f6f9d27b5b4e8f3e3818084dfc3726):
# its unique id is the bare Tibber home id and its translation key
# "electricity_price"; every other Tibber sensor's unique id is
# ``<home id>_<key>``, ``<home id>_rt_<key>`` or ``<device id>_<key>``, so an
# underscore rules it out. A registry too old to store translation keys holds
# None there, which the unique-id rule alone then decides.
TIBBER_PLATFORM = "tibber"
TIBBER_PRICE_KEY = "electricity_price"
#: ``const.PRICE_SOURCE_ENTITY``; every other source is Tibber's, as
#: ``coordinator._entity_price_source`` decides it.
PRICE_SOURCE_ENTITY = "entity"


class Refused(ValueError):
    """A document that may not be written, and why."""


def conf_keys(const_text: str) -> frozenset[str]:
    """The ``CONF_*`` values a ``const.py`` source declares: the entry allowlist."""
    return frozenset(CONST_PATTERN.findall(const_text))


def tibber_price_candidates(registry: list[dict]) -> list[str]:
    """The enabled Tibber price sensors in the entity registry, sorted."""
    return sorted(
        e["entity_id"] for e in registry
        if e.get("platform") == TIBBER_PLATFORM
        and str(e.get("entity_id", "")).startswith("sensor.")
        and not e.get("disabled_by")
        and "_" not in str(e.get("unique_id") or "_")
        and e.get("translation_key") in (None, TIBBER_PRICE_KEY)
    )


def choose_price_entity(
    config: dict, registry: list[dict], recorded: Callable[[str], bool]
) -> str:
    """The Tibber price sensor to build the replay's price series from.

    A candidate must also have a numeric state in force during the window
    (``recorded(entity_id)``). The entry's own ``price_entity``, when it names
    one of them, decides between homes; otherwise exactly one must remain,
    and anything else is refused with the candidates listed.
    """
    candidates = tibber_price_candidates(registry)
    live = [c for c in candidates if recorded(c)]
    if config.get("price_entity") in live:
        return config["price_entity"]
    if len(live) == 1:
        return live[0]
    listed = ", ".join(
        f"{c}{'' if c in live else ' (no numeric state in the window)'}"
        for c in candidates) or "none"
    raise Refused(
        f"the Tibber price source needs a recorded price sensor; found "
        f"{len(live)} usable of {len(candidates)} Tibber price sensor(s) in the "
        f"registry: {listed}. Pass --price-entity SENSOR"
    )


def numeric(state: object) -> bool:
    try:
        float(state)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    return True
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
    if HOST_PATH.search(value) or HEX12.search(value):
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


# THE SHAPE EACH ALLOWLISTED ATTRIBUTE MUST HAVE. A key on the allowlist is
# not a licence for any value under it: a name in ``currency``, a dict of
# strings in ``options`` or a token in ``today`` has the right key and the
# wrong shape. Each function returns the value cut to its shape, or _DROP.


def _number(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return _DROP


def _unit(value: object) -> object:
    if value is None or (isinstance(value, str) and len(value) <= 16 and text_ok(value)):
        return value
    return _DROP


def _snake(value: object) -> object:
    return value if value is None or (isinstance(value, str) and SNAKE.match(value)) else _DROP


def _options(value: object) -> object:
    """A select's option labels: short, word-like, no digits at all."""
    if value is None:
        return None
    if not isinstance(value, list):
        return _DROP
    return [v for v in value if isinstance(v, str) and text_ok(v) and LABEL.match(v)
            and not re.search(r"\d", v)]


def _series(value: object) -> object:
    """A price series: rows of a time and a number, nothing else."""
    if value is None:
        return None
    if not isinstance(value, list):
        return _DROP
    rows = []
    for item in value:
        if not isinstance(item, dict):
            continue
        row = {k: v for k, v in item.items()
               if (k in SERIES_TIME_KEYS and isinstance(v, str) and ISO_TIME.match(v))
               or (k in SERIES_VALUE_KEYS and _number(v) is not _DROP)}
        if set(row) & SERIES_TIME_KEYS and set(row) & SERIES_VALUE_KEYS:
            rows.append(row)
    return rows


def _time(value: object) -> object:
    return value if value is None or (isinstance(value, str) and ISO_TIME.match(value)) else _DROP


ATTRIBUTE_SHAPES = {
    **{k: _unit for k in ("unit_of_measurement", "temperature_unit",
                          "wind_speed_unit", "precipitation_unit")},
    **{k: _snake for k in ("device_class", "state_class", "hvac_action")},
    **{k: _number for k in ("temperature", "wind_speed", "precipitation", "min",
                            "max", "current_temperature", "power_kw")},
    **{k: _series for k in ("raw_today", "raw_tomorrow", "today", "tomorrow")},
    "options": _options,
    "currency": lambda v: v if v is None or (isinstance(v, str) and CURRENCY.match(v)) else _DROP,
    "start_time": _time,
    "end_time": _time,
    "heat_pump_on": lambda v: v if v is None or isinstance(v, bool) else _DROP,
}
assert set(ATTRIBUTE_SHAPES) == ATTRIBUTE_KEYS


def _entry_shape(key: str, value: object) -> object:
    """An entry key naming an entity holds entity ids and nothing else."""
    if key.endswith("_entity"):
        if value in (None, "") or (isinstance(value, str) and ENTITY_ID.match(value)):
            return value
        return _DROP
    if key.endswith("_entities"):
        if isinstance(value, list):
            return [v for v in value if isinstance(v, str) and ENTITY_ID.match(v)]
        return _DROP
    return value


def _keep_keys(section: object, allowed: frozenset[str], dropped: list[str],
               shape=None) -> dict:
    out = {}
    for key, value in (section if isinstance(section, dict) else {}).items():
        secret = bool(SECRET_KEY.search(str(key)))
        shaped = _DROP if secret or key not in allowed else (
            shape(key, value) if shape else value)
        if shaped is _DROP:
            _collect_strings(value, dropped, secret)
            continue
        if shaped != value:
            _collect_strings(value, dropped)
        out[key] = shaped
    return clean_value(out, dropped)


def _attr_shape(key: str, value: object) -> object:
    return ATTRIBUTE_SHAPES[key](value)


def sanitise(raw: dict, conf: frozenset[str], dropped: list[str]) -> dict:
    """The export payload cut down to the allowlist.

    ``dropped`` collects every string removed, so the caller can prove none
    of them survived anywhere else in the payload.
    """
    out = dict(raw)
    entry = dict(raw["entry"])
    entry["data"] = _keep_keys(entry.get("data"), conf, dropped, _entry_shape)
    entry["options"] = _keep_keys(entry.get("options"), conf, dropped, _entry_shape)
    out["entry"] = entry
    states = {}
    for entity_id, rows in raw["states"].items():
        clean_rows = []
        for updated, state, attrs, reported in rows:
            if attrs is not None:
                attrs = _keep_keys(attrs, ATTRIBUTE_KEYS, dropped, _attr_shape)
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
    return found + _entry_violations(payload.get("entry") or {}, conf) + _state_violations(
        payload.get("states") or {})


def _entry_violations(entry: dict, conf: frozenset[str] | None) -> list[str]:
    found = []
    for section in ("data", "options"):
        block = entry.get(section) or {}
        for key in block:
            if (conf is not None and key not in conf) or not KEY.match(str(key)):
                found.append(f"entry.{section}.{key}: not an entry key of this integration")
            elif _entry_shape(key, block[key]) != block[key]:
                found.append(f"entry.{section}.{key}: must hold entity ids only")
    return found


def _state_violations(states: dict) -> list[str]:
    found = []
    for entity_id, rows in states.items():
        if not ENTITY_ID.match(str(entity_id)):
            found.append(f"states.{entity_id}: not an entity id")
        for i, row in enumerate(rows if isinstance(rows, list) else []):
            attrs = row[2] if isinstance(row, list) and len(row) > 2 else None
            for key in (attrs or {}):
                if key not in ATTRIBUTE_KEYS:
                    found.append(f"states.{entity_id}[{i}].{key}: attribute outside the allowlist")
                elif _attr_shape(key, attrs[key]) != attrs[key]:
                    found.append(f"states.{entity_id}[{i}].{key}: not the shape this attribute has")
    return found


# --- building the document ----------------------------------------------------


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


def state_rows(records: Iterable[tuple]) -> list[list]:
    """``[updated, state, attributes | None, reported | None]`` rows of
    ``(updated, state, attributes, reported)`` records, oldest first.

    Attributes are written only when they differ from the previous row's, so
    a thermometer's unchanged unit is not repeated a thousand times a day.
    """
    rows: list[list] = []
    last_attrs: object = object()
    for updated, state, attrs, reported in records:
        row = [updated, state, None, reported]
        if attrs != last_attrs:
            row[2] = attrs
            last_attrs = attrs
        rows.append(row)
    return rows


def document(
    *, time_zone: str, window: tuple[str, str], recorder_schema: int | None,
    entry: dict, inputs: Iterable[str], published: Iterable[str],
    price_series_entity: str | None, states: dict[str, list[list]],
) -> dict:
    """The unsanitised ``hpo-replay/1`` document; ``seal`` makes it writable."""
    return {
        "format": FORMAT,
        "time_zone": time_zone,
        "window": {"start": window[0], "end": window[1]},
        "recorder_schema": recorder_schema,
        "entry": {
            "version": entry.get("version"),
            "minor_version": entry.get("minor_version"),
            "data": entry.get("data", {}),
            "options": entry.get("options", {}),
        },
        "inputs": sorted(inputs),
        "published": sorted(published),
        "price_series_entity": price_series_entity,
        "states": states,
    }


def seal(raw: dict, conf: frozenset[str]) -> dict:
    """``raw`` sanitised, or ``Refused`` when a dropped value survives elsewhere in
    it or the result still breaks a rule."""
    dropped: list[str] = []
    clean = sanitise(raw, conf, dropped)
    blob = json.dumps(clean, sort_keys=True)
    leaked = sorted({s for s in dropped if len(s) >= 6 and s in blob})
    if leaked:
        raise Refused(
            f"refusing to write: {len(leaked)} dropped credential value(s) "
            "survive elsewhere in the payload"
        )
    left = violations(clean, conf)
    if left:
        raise Refused("refusing to write: " + "; ".join(left[:5]))
    return clean
