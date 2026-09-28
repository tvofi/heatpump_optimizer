#!/usr/bin/env python3
"""Generate the device-pre-fill registry fixtures from upstream definitions.

W1067-G7b's source tables (``custom_components/heatpump_optimizer/
device_prefill.py``) say which of a heat-pump integration's entities fill
which option. What that integration actually publishes is not this
repository's to assert, so the fixtures those tables are tested against are
**generated from the upstream definitions at a pinned commit**, never typed.

One checkout per pinned source, named by its own ``origin`` URL so a fixture
cannot be built from the wrong clone:

    python3 tools/gen_device_fixtures.py --write \
        --repo ~/tuya_heat_pump --repo ~/tuya-local \
        --repo ~/hass-localtuya --repo ~/localtuya
    python3 tools/gen_device_fixtures.py --check <the same --repo arguments>

Each ``--repo`` may be given once per source; the source is found by matching
the checkout's ``remote.origin.url`` against the ``repo`` its spec names, and
every pinned *tag* is re-resolved to its recorded commit first, so a moved tag
fails in ``--check`` before a table is re-derived.

Honest scope: a fixture proves the mapping against one source's definitions
at one commit. It proves nothing about a live device, and nothing about a
model file this repository has not seen. Drift is noticed when the pin is
bumped: re-run with ``--check`` and a changed upstream fails here, before any
table is re-derived.

Per-source notes, each of which the fixture records rather than the reader
reconstructing:

* **tuya_heat_pump** executes the model file as upstream does and reads its
  per-platform tables; the device name is the model's product name, and the
  entity ids carry it because ``has_entity_name`` is true there.
* **tuya_local** parses ``devices/<config>.yaml`` and applies the config-id
  and unique-id rules of ``helpers/device_config.py`` at the pinned commit.
  The *config id* is the entity type plus the slugified entity name, then the
  translation key, then the device class, then the bare type; the *unique id*
  is the device uid, a hyphen, and that config id. The device name used for
  entity ids is the config's own top-level ``name``: a real install's is the
  name the user paired under, and the resolver keys on unique ids, so the
  difference lives inside those strings only. Units are mapped through the
  ascii spellings the same commit's device schema documents (``C`` for
  ``°C``), which is also where ``unit_from_ascii`` gets them.
* **localtuya** has no per-device definition file: the entity set is the
  user's own configuration. Its records are therefore **hand-shaped** from
  the ``entities`` list below on the unique-id rule read out of each
  maintained line's own source (``local_<device id>_<dp>``); the rule is
  extracted, not restated, and ``--check`` fails if either line stops reading
  as device plus DP.

``_slug`` reproduces Home Assistant's ``slugify`` for the names these
definitions carry: NFKD to ASCII, then runs of anything that is not a word
character, a hyphen or a space collapsed to one underscore.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import unicodedata

import yaml

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "tests" / "fixtures"

#: The model file each fixture is generated from, at the commit recorded in
#: it. ``slug`` is the device-name slug the coordinator builds from the
#: device name (``coordinator.py``: lowercased, spaces and hyphens to
#: underscores); the fixture uses the model's own product name so the
#: fixture's unique ids read as a real install's.
TUYA_HEAT_PUMP = {
    "fixture": "tuya_heat_pump_000004k4z6.json",
    "shape": "tuya_heat_pump",
    "repo": "tvofi/tuya_heat_pump",
    "tag": "v2.6.0-beta04",
    "commit": "fda9bed19395267898570d72fe5e9324f523d574",
    "path": "custom_components/tuya_heat_pump/models/000004k4z6.py",
    "platform": "tuya_heat_pump",
    "device_name": "Rotenso Windmi",
    #: ``models/__init__.py`` hands each platform its own table; the platform
    #: modules build ``f"{slug}_{key}"`` from that table's keys.
    "tables": {
        "SENSOR_TYPES": "sensor",
        "BINARY_SENSOR_TYPES": "binary_sensor",
        "SWITCH_TYPES": "switch",
        "NUMBER_TYPES": "number",
        "SELECT_TYPES": "select",
    },
}

#: The Fisher air-to-water config: the tuya-local device known to share this
#: firmware family (tvofi/tuya_heat_pump ``models/000004k4z6.py``:12-14,
#: make-all/tuya-local issue #1870). ``device_uid`` stands in for a real
#: install's Tuya device id, which is what that config's unique ids hang off.
TUYA_LOCAL = {
    "fixture": "tuya_local_fisher_water_heatpump.json",
    "shape": "tuya_local",
    "repo": "make-all/tuya-local",
    "tag": "2026.9.1",
    "commit": "4551357adb34b6cf3073af8deada6a9bf13c94f0",
    "path": "custom_components/tuya_local/devices/fisher_water_heatpump.yaml",
    #: The same commit's device schema, whose own description documents the
    #: ascii unit spellings (``C`` for ``°C``).
    "schema": "custom_components/tuya_local/devices/device_config_schema.json",
    "platform": "tuya_local",
    "device_uid": "bf1234567890abcdef12",
}

#: localtuya's two maintained lines. The records are hand-shaped (see the
#: module docstring); the rule is read out of each line's own source.
LOCALTUYA = {
    "fixture": "localtuya_local_dp.json",
    "shape": "localtuya",
    "platform": "localtuya",
    #: The shaped-on line's own repository, tag and commit, repeated at the
    #: fixture's top level; both lines are read into ``sources``.
    "repo": "xZetsubou/hass-localtuya",
    "tag": "2026.7.0",
    "commit": "3d0c0ec737b59ebfb1eea65df42f5d902eafaecc",
    "lines": [
        {
            "repo": "xZetsubou/hass-localtuya",
            "tag": "2026.7.0",
            "commit": "3d0c0ec737b59ebfb1eea65df42f5d902eafaecc",
            "path": "custom_components/localtuya/entity.py",
        },
        {
            "repo": "rospogrigio/localtuya",
            "tag": "v5.2.5",
            "commit": "59c95cd06c2696afc98f6bc52d5fa060f3c517da",
            "path": "custom_components/localtuya/common.py",
        },
    ],
    #: The line the records' entity ids are shaped on: the first, whose
    #: ``has_entity_name`` prefixes the device name. The other line leaves the
    #: entity id to the friendly name alone; both build the same unique id.
    "shaped_on": 0,
    "device_name": "Radiator heat pump",
    "device_id": "bf1234567890abcdef12",
    #: Hand-shaped, and the reason is the decision W1067-G7b-2 records: a
    #: localtuya device is whatever its user configured. This one is the
    #: owner's own pump by its DP numbers -- the case a DP-keyed table would
    #: be tempted by, and still cannot prove the firmware of.
    "entities": [
        {"domain": "switch", "dp": 1, "name": "Power"},
        {"domain": "sensor", "dp": 10, "name": "Outlet water temperature",
         "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
        {"domain": "sensor", "dp": 26, "name": "Tank temperature",
         "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
        {"domain": "sensor", "dp": 101, "name": "Inlet water temperature",
         "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
        {"domain": "sensor", "dp": 105, "name": "Outdoor temperature",
         "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
        {"domain": "sensor", "dp": 109, "name": "Water pump gear",
         "state_class": "measurement"},
    ],
}


# --------------------------------------------------------------------- corpus

#: The labelled corpus W1067-G7b-3's fuzzy fallback is measured on. A *label*
#: is the entity a role should resolve to on that device, or ``None`` when the
#: device carries no entity for it; a fallback that suggests something where
#: the label is ``None``, or an entity other than the label, is a WRONG
#: suggestion -- the one thing the corpus measurement refuses.
#:
#: Two shapes. A device read ``from_fixture`` takes another fixture's records
#: and re-platforms them, so its entity set is the pinned definitions' own and
#: its labels are entity ids. A ``hand_shaped`` device is the set a user
#: configured by hand, marked as such, and its labels are DP numbers.
#:
#: The three localtuya-shaped devices stand on the unique-id rule the
#: generated localtuya fixture records (``local_{device}_{dp}``), read out of
#: it rather than restated, so ``--write-corpus`` needs no upstream checkout.
CORPUS = {
    "fixture": "prefill_corpus.json",
    "devices": [
        {
            "name": "rotenso_windmi",
            "from_fixture": "tuya_heat_pump_000004k4z6.json",
            "platform": "tuya_heat_pump",
            "hand_shaped": False,
            "note": (
                "tvofi/tuya_heat_pump's own model at fda9bed. Its source table "
                "resolves six roles, so the fallback has nothing left to fill "
                "here: this device is the corpus's null control. Its dp 106 "
                "'Heat Exchanger Outlet Water Temperature (Tout)' is a second "
                "outlet-named temperature the fallback must not read as the "
                "supply (its own table already decided the supply is T1)."
            ),
            "labels": {
                "outdoor_temp_entity": "sensor.rotenso_windmi_outdoor_ambient_temperature_t4",
                "dhw_temp_entity": "sensor.rotenso_windmi_dhw_tank_temperature",
                "heat_pump_supply_temp_entity": (
                    "sensor.rotenso_windmi_outlet_water_temperature_t1"),
                "heat_pump_return_temp_entity": (
                    "sensor.rotenso_windmi_heat_exchanger_inlet_water_temperature_tin"),
                "compressor_freq_sensor": None,
                "r404": "number.rotenso_windmi_dhw_setpoint",
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
        {
            "name": "fisher_water_heatpump",
            "from_fixture": "tuya_local_fisher_water_heatpump.json",
            "platform": "tuya_local",
            "hand_shaped": False,
            "note": (
                "make-all/tuya-local at 2026.9.1. Its table resolves the "
                "outdoor and return sensors. Its third named sensor, 'Outlet "
                "temperature' (dp 106), is the plate outlet rather than the T1 "
                "supply, so the supply label is null and a suggestion there is "
                "wrong: the near-tie trap, on a device whose dp 10 supply "
                "reading is a climate attribute no entity slot can take."
            ),
            "labels": {
                "outdoor_temp_entity": "sensor.radiator_heat_pump_outdoor_temperature",
                "dhw_temp_entity": None,
                "heat_pump_supply_temp_entity": None,
                "heat_pump_return_temp_entity": "sensor.radiator_heat_pump_inlet_temperature",
                "compressor_freq_sensor": None,
                "r404": None,
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
        {
            "name": "localtuya_owner_pump",
            "hand_shaped": True,
            "platform": "localtuya",
            "unique_id": "local_{device}_{dp}",
            "device_name": "Radiator heat pump",
            "device_id": "bf1234567890abcdef12",
            "note": (
                "The same DP numbers as the generated localtuya fixture, under "
                "the names that fixture's user configured. No table reaches a "
                "localtuya device, so the fallback resolves all four."
            ),
            "entities": [
                {"domain": "switch", "dp": 1, "name": "Power"},
                {"domain": "sensor", "dp": 10, "name": "Outlet water temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 26, "name": "Tank temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 101, "name": "Inlet water temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 105, "name": "Outdoor temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 109, "name": "Water pump gear",
                 "state_class": "measurement"},
            ],
            "labels": {
                "outdoor_temp_entity": 105,
                "dhw_temp_entity": 26,
                "heat_pump_supply_temp_entity": 10,
                "heat_pump_return_temp_entity": 101,
                "compressor_freq_sensor": None,
                "r404": None,
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
        {
            "name": "localtuya_t1_tout",
            "hand_shaped": True,
            "platform": "localtuya",
            "unique_id": "local_{device}_{dp}",
            "device_name": "Garage pump",
            "device_id": "bf1234567890abcdef12",
            "note": (
                "The plan's own trap, in the form a fallback meets it: the "
                "machine's T1 (dp 10) and its plate outlet Tout (dp 106) on "
                "one device, named as the pinned source names them. T1 is the "
                "supply; Tout is nothing."
            ),
            "entities": [
                {"domain": "sensor", "dp": 10, "name": "Outlet Water Temperature (T1)",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 106,
                 "name": "Heat Exchanger Outlet Water Temperature (Tout)",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 101, "name": "Inlet water temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 105, "name": "Outdoor temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 26, "name": "Tank temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
            ],
            "labels": {
                "outdoor_temp_entity": 105,
                "dhw_temp_entity": 26,
                "heat_pump_supply_temp_entity": 10,
                "heat_pump_return_temp_entity": 101,
                "compressor_freq_sensor": None,
                "r404": None,
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
        {
            "name": "localtuya_wrong_unit",
            "hand_shaped": True,
            "platform": "localtuya",
            "unique_id": "local_{device}_{dp}",
            "device_name": "Holiday home pump",
            "device_id": "bf1234567890abcdef12",
            "note": (
                "A perfect supply name in the wrong unit: the slot expects "
                "degrees Celsius and this probe reads Fahrenheit, so the "
                "number would be a different temperature. The two correct "
                "neighbours must still resolve."
            ),
            "entities": [
                {"domain": "sensor", "dp": 10, "name": "Supply water temperature",
                 "device_class": "temperature", "unit": "°F", "state_class": "measurement"},
                {"domain": "sensor", "dp": 105, "name": "Outdoor temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 26, "name": "Hot water tank temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
            ],
            "labels": {
                "outdoor_temp_entity": 105,
                "dhw_temp_entity": 26,
                "heat_pump_supply_temp_entity": None,
                "heat_pump_return_temp_entity": None,
                "compressor_freq_sensor": None,
                "r404": None,
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
        {
            "name": "localtuya_energy",
            "hand_shaped": True,
            "platform": "localtuya",
            "unique_id": "local_{device}_{dp}",
            "device_name": "Workshop pump",
            "device_id": "bf1234567890abcdef12",
            "note": (
                "An energy total, an instantaneous power and a frequency "
                "sensor. The frequency is the compressor slot; neither the "
                "kWh total nor the kW reading is the unit's capacity, which "
                "is a rating rather than a measurement."
            ),
            "entities": [
                {"domain": "sensor", "dp": 1, "name": "Compressor frequency",
                 "device_class": "frequency", "unit": "Hz", "state_class": "measurement"},
                {"domain": "sensor", "dp": 2, "name": "Heat pump power",
                 "device_class": "power", "unit": "W", "state_class": "measurement"},
                {"domain": "sensor", "dp": 3, "name": "Energy today",
                 "device_class": "energy", "unit": "kWh", "state_class": "total_increasing"},
            ],
            "labels": {
                "outdoor_temp_entity": None,
                "dhw_temp_entity": None,
                "heat_pump_supply_temp_entity": None,
                "heat_pump_return_temp_entity": None,
                "compressor_freq_sensor": 1,
                "r404": None,
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
        {
            "name": "brand_flow_names",
            "hand_shaped": True,
            "platform": "some_brand_heatpump",
            "unique_id": "{slug}_{dp}",
            "device_name": "Brand Pump",
            "device_id": "brand-0001",
            "note": (
                "A brand-specific integration with no table: the fallback only. "
                "Its own words for the four water readings and the compressor."
            ),
            "entities": [
                {"domain": "sensor", "dp": 1, "name": "Flow temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 2, "name": "Return temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 3, "name": "Outside temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 4, "name": "Hot water tank temperature",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 5, "name": "Compressor frequency",
                 "device_class": "frequency", "unit": "Hz", "state_class": "measurement"},
            ],
            "labels": {
                "outdoor_temp_entity": 3,
                "dhw_temp_entity": 4,
                "heat_pump_supply_temp_entity": 1,
                "heat_pump_return_temp_entity": 2,
                "compressor_freq_sensor": 5,
                "r404": None,
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
        {
            "name": "brand_swedish",
            "hand_shaped": True,
            "platform": "some_brand_heatpump",
            "unique_id": "{slug}_{dp}",
            "device_name": "Varmepump",
            "device_id": "brand-0002",
            "note": (
                "The same device named in Swedish, which the synonym lists "
                "carry: a Swedish install's own words."
            ),
            "entities": [
                {"domain": "sensor", "dp": 1, "name": "Framledningstemperatur",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 2, "name": "Returtemperatur",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 3, "name": "Utomhustemperatur",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
                {"domain": "sensor", "dp": 4, "name": "Varmvattentemperatur",
                 "device_class": "temperature", "unit": "°C", "state_class": "measurement"},
            ],
            "labels": {
                "outdoor_temp_entity": 3,
                "dhw_temp_entity": 4,
                "heat_pump_supply_temp_entity": 1,
                "heat_pump_return_temp_entity": 2,
                "compressor_freq_sensor": None,
                "r404": None,
                "r405": None,
                "r406": None,
                "unit_capacity": None,
            },
        },
    ],
}


def _slug(text: str) -> str:
    """Home Assistant's entity-id slug, and the coordinator's device slug.

    ``homeassistant.util.slugify`` is ``python-slugify``'s ``slugify`` with
    the underscore separator, and its default is to NFKD-normalise to ASCII
    before collapsing anything that is not a word character, a hyphen or a
    space; that is the step reproduced here, so ``ΔT`` and ``ö`` become ``t``
    and ``o`` as upstream's own slugs do.
    """
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", ascii_text.lower())).strip("_")


def _device_slug(name: str) -> str:
    """The coordinator's own device slug (``coordinator.py``): lowercase,
    spaces and hyphens to underscores, and nothing else touched."""
    return name.lower().replace(" ", "_").replace("-", "_")


def _run(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=True,
    ).stdout


def _show(repo: pathlib.Path, commit: str, path: str) -> str:
    return _run(repo, "show", f"{commit}:{path}")


def _checkout(repos: list[pathlib.Path], spec: dict) -> pathlib.Path:
    """The checkout whose origin is the repository the spec names."""
    wanted = spec["repo"].lower()
    for repo in repos:
        origin = _run(repo, "config", "--get", "remote.origin.url").strip()
        if origin.startswith("git@"):
            origin = origin.replace(":", "/", 1)
        if origin.removesuffix(".git").lower().endswith(wanted):
            return repo
    raise SystemExit(
        f"no --repo checkout has origin {spec['repo']}; pass every pinned source"
    )


def _check_pin(spec: dict, repos: list[pathlib.Path]) -> None:
    """A pinned tag must still name the recorded commit."""
    resolved = _run(_checkout(repos, spec), "rev-parse",
                    f"{spec['tag']}^{{commit}}").strip()
    if resolved != spec["commit"]:
        raise SystemExit(
            f"{spec['repo']} tag {spec['tag']} is {resolved[:7]}, "
            f"not the recorded {spec['commit'][:7]}"
        )


def _record(*, platform: str, unique_id: str, entity_id: str,
            name: str | None, entity: dict) -> dict:
    """One registry record, in the field order the three fixtures share."""
    return {
        "platform": platform,
        "unique_id": unique_id,
        "entity_id": entity_id,
        "original_name": name,
        "translation_key": entity.get("translation_key"),
        "device_class": entity.get("device_class"),
        "unit": entity.get("unit"),
        "state_class": entity.get("state_class"),
    }


# -------------------------------------------------------------- tuya_heat_pump

def _tuya_heat_pump_records(spec: dict, source: str) -> tuple[list[dict], list[dict]]:
    """The entity-registry records the model file's tables describe.

    The model files are plain data: module-level dicts and no imports. They
    are executed rather than parsed so a value the upstream computes (a fault
    bitmap, a conversion string) is read as upstream reads it.
    """
    namespace: dict = {}
    exec(compile(source, spec["path"], "exec"), namespace)  # noqa: S102
    slug = _device_slug(spec["device_name"])
    records, readings = [], []
    for table, domain in spec["tables"].items():
        for key, config in (namespace.get(table) or {}).items():
            name = config.get("name", key)
            records.append(_record(
                platform=spec["platform"],
                unique_id=f"{slug}_{key}",
                # has_entity_name is true on every platform there, so Home
                # Assistant prefixes the device name.
                entity_id=f"{domain}.{slug}_{_slug(name)}",
                name=name,
                entity=config,
            ))
            if config.get("dp_id") is not None:
                readings.append({"dp": config["dp_id"], "key": key, "name": name})
    records.sort(key=lambda r: r["entity_id"])
    readings.sort(key=lambda r: (r["dp"], r["key"]))
    return records, readings


# ------------------------------------------------------------------ tuya_local

def _ascii_units(schema: str) -> dict[str, str]:
    """The ascii unit spellings the device schema's own text documents.

    ``unit_from_ascii`` (``entity.py`` at the same commit) maps a config's
    ``unit: C`` to the unit Home Assistant shows, through four entries the
    schema description spells out; reading it there is why this generator
    holds no unit table of its own.
    """
    description = json.loads(schema)["properties"]["entities"]["items"][
        "properties"]["dps"]["items"]["properties"]["unit"]["description"]
    pairs = dict(re.findall(r"\b(\w+) for ([^\s,]+)", description))
    if "C" not in pairs:
        raise SystemExit(
            f"the device schema no longer spells out the ascii units: {description!r}"
        )
    return pairs


def _tuya_local_config_id(entity: dict) -> str:
    """The config id, by ``helpers/device_config.py:323-338``'s own chain."""
    etype = entity["entity"]
    if entity.get("name"):
        return f"{etype}_{_slug(entity['name'])}"
    if entity.get("translation_key"):
        slug = f"{etype}_{entity['translation_key']}"
        for key, value in (entity.get("translation_placeholders") or {}).items():
            if key in slug:
                slug = slug.replace(key, _slug(value))
            else:
                slug = f"{slug}_{value}"
        return slug
    if entity.get("class"):
        return f"{etype}_{entity['class']}"
    return etype


def _tuya_local_records(spec: dict, source: str, schema: str) -> tuple[list[dict], list[dict], dict]:
    """The records the config's own entities become.

    ``unique_id`` is the device uid, a hyphen, and the slugified config id
    (``device_config.py:293-295``); ``entity_id`` follows Home Assistant's
    suggestion for a ``has_entity_name`` entity (``entity_platform.py:800-806``
    at 2025.2.0): the device name, then the entity's own name when it has one.
    An entity with no name of its own takes the device name alone.
    """
    config = yaml.safe_load(source)
    units = _ascii_units(schema)
    uid = spec["device_uid"]
    device_name = config["name"]
    records, readings = [], []
    for entity in config["entities"]:
        key = _tuya_local_config_id(entity)
        name = entity.get("name")
        dps = entity.get("dps") or []
        only = dps[0] if len(dps) == 1 else {}
        entity_id = f"{entity['entity']}.{_slug(device_name)}"
        if name:
            named = f"{device_name} {name}"
            entity_id = f"{entity['entity']}.{_slug(named)}"
        records.append(_record(
            platform=spec["platform"],
            unique_id=f"{uid}-{_slug(key)}",
            entity_id=entity_id,
            name=name,
            entity={
                "translation_key": entity.get("translation_key"),
                "device_class": entity.get("class"),
                "unit": units.get(only.get("unit"), only.get("unit")),
                "state_class": only.get("class"),
            },
        ))
        for dp in dps:
            readings.append({"dp": dp["id"], "key": key, "name": dp.get("name")})
    records.sort(key=lambda r: r["entity_id"])
    readings.sort(key=lambda r: (r["dp"], r["key"]))
    products = [
        {field: product.get(field) for field in ("id", "manufacturer", "model", "name")}
        for product in config.get("products") or []
    ]
    return records, readings, {
        "device_uid": uid,
        "config_name": device_name,
        "products": products,
    }


# ------------------------------------------------------------------- localtuya

def _localtuya_rule(line: dict, source: str) -> dict:
    """The unique-id rule, read out of that line's own source.

    The expression is extracted from the ``unique_id`` property and taken
    apart: its literal parts become the rule, and each placeholder is named by
    what it reads -- the expression ending in ``_dp_id`` is the DP, the other
    the device id. A line that stops reading that way stops the generator,
    which is the point: the rule is not restated here.
    """
    start = source.index("def unique_id")
    match = re.search(r'f"([^"]*)"', source[start:])
    if match is None:
        raise SystemExit(f"{line['repo']} {line['path']}: no f-string in unique_id")
    expression = match.group(1)
    order = [
        "dp" if placeholder.strip().endswith("_dp_id") else "device"
        for placeholder in re.findall(r"\{([^}]*)\}", expression)
    ]
    if sorted(order) != ["device", "dp"]:
        raise SystemExit(
            f"{line['repo']} {line['path']}: unique_id is no longer device plus DP: "
            f"{expression!r}"
        )
    rule = re.sub(r"\{[^}]*\}", "{}", expression)
    for role in order:
        rule = rule.replace("{}", "{" + role + "}", 1)
    return {
        "repo": line["repo"],
        "tag": line["tag"],
        "commit": line["commit"],
        "path": line["path"],
        "line": source.count("\n", 0, start) + 1,
        "expression": f'f"{expression}"',
        "rule": rule,
        # Whether the line prefixes the device name to the entity id:
        # xZetsubou sets it, rospogrigio leaves Home Assistant's default.
        "has_entity_name": "_attr_has_entity_name = True" in source,
    }


def _build_unique_id(rule: str, values: dict[str, str]) -> str:
    for role in re.findall(r"\{(\w+)\}", rule):
        rule = rule.replace("{" + role + "}", values[role], 1)
    return rule


def _localtuya_records(spec: dict, rules: list[dict]) -> tuple[list[dict], list[dict]]:
    """Hand-shaped records, on the first line's own rule and naming."""
    shaped = rules[spec["shaped_on"]]
    records, readings = [], []
    for entity in spec["entities"]:
        unique_id = _build_unique_id(
            shaped["rule"], {"device": spec["device_id"], "dp": str(entity["dp"])})
        entity_id = f"{entity['domain']}.{_slug(entity['name'])}"
        if shaped["has_entity_name"]:
            named = f"{spec['device_name']} {entity['name']}"
            entity_id = f"{entity['domain']}.{_slug(named)}"
        records.append(_record(
            platform=spec["platform"],
            unique_id=unique_id,
            entity_id=entity_id,
            name=entity["name"],
            entity=entity,
        ))
        readings.append({"dp": entity["dp"], "key": unique_id, "name": entity["name"]})
    records.sort(key=lambda r: r["entity_id"])
    readings.sort(key=lambda r: (r["dp"], r["key"]))
    return records, readings


# ---------------------------------------------------------------------- corpus

def _hand_records(spec: dict) -> list[dict]:
    """One hand-shaped device's records, on its own unique-id rule.

    The rule is the spec's own format string, joined the way that
    integration's source joins it (``local_{device}_{dp}`` for the
    localtuya-shaped sets, read out of the generated localtuya fixture's
    ``sources``); the entity id is the device name and the entity's own name,
    because every set below is one a ``has_entity_name`` platform publishes.
    """
    slug = _slug(spec["device_name"])
    records = []
    for entity in spec["entities"]:
        values = {"device": spec.get("device_id", ""), "dp": str(entity["dp"]),
                  "slug": slug}
        unique_id = spec["unique_id"]
        for role in re.findall(r"\{(\w+)\}", unique_id):
            unique_id = unique_id.replace("{" + role + "}", values[role], 1)
        named = spec["device_name"] + " " + entity["name"]
        records.append(_record(
            platform=spec["platform"],
            unique_id=unique_id,
            entity_id=f"{entity['domain']}.{_slug(named)}",
            name=entity["name"],
            entity=entity,
        ))
    records.sort(key=lambda r: r["entity_id"])
    return records


def _label_entity(records: list[dict], value) -> str | None:
    """One label as the entity id it names.

    A generated device's label is an entity id and a hand-shaped device's is a
    DP number; either way a label that names no record, or more than one, is a
    typo in this file and stops the build rather than quietly measuring
    nothing.
    """
    if value is None:
        return None
    found = [
        row["entity_id"] for row in records
        if row["entity_id"] == value or row["unique_id"].endswith(f"_{value}")
    ]
    if len(found) != 1:
        raise SystemExit(f"corpus label {value!r} names {found or 'no'} record(s)")
    return found[0]


def build_corpus(spec: dict) -> dict:
    """The labelled corpus, from the fixtures this script already wrote."""
    devices = []
    for device in spec["devices"]:
        if device.get("from_fixture"):
            source = load(device["from_fixture"])
            records = [
                {**row, "platform": device["platform"]}
                for row in source["records"]
            ]
            upstream = {
                "upstream_repo": source["upstream_repo"],
                "upstream_tag": source["upstream_tag"],
                "upstream_commit": source["upstream_commit"],
                "upstream_path": source["upstream_path"],
            }
        else:
            records = _hand_records(device)
            upstream = {
                "upstream_repo": None,
                "upstream_tag": None,
                "upstream_commit": None,
                "upstream_path": None,
            }
        devices.append({
            "name": device["name"],
            "platform": device["platform"],
            "hand_shaped": device["hand_shaped"],
            "note": device["note"],
            **upstream,
            "records": records,
            "labels": {
                role: _label_entity(records, value)
                for role, value in device["labels"].items()
            },
        })
    return {
        "_generated_by": "tools/gen_device_fixtures.py",
        "sources": [
            {
                "fixture": item["fixture"],
                "repo": item["repo"],
                "tag": item.get("tag"),
                "commit": item["commit"],
                "platform": item["platform"],
            }
            for item in (TUYA_HEAT_PUMP, TUYA_LOCAL, LOCALTUYA)
        ],
        "devices": devices,
    }


# ----------------------------------------------------------------------- build

def build(spec: dict, repos: list[pathlib.Path]) -> dict:
    """One fixture, read from the pinned sources in ``repos``.

    The top-level ``upstream_*`` fields name the definition the records were
    read from: the spec's own file, or -- for localtuya, which has none -- the
    line the records are shaped on, whose rule and naming are repeated in
    ``sources`` beside the other maintained line's.
    """
    if spec.get("tag"):
        _check_pin(spec, repos)
    path = spec.get("path") or spec["lines"][spec["shaped_on"]]["path"]
    fixture = {
        "_generated_by": "tools/gen_device_fixtures.py",
        "upstream_repo": spec["repo"],
        "upstream_tag": spec.get("tag"),
        "upstream_commit": spec["commit"],
        "upstream_path": path,
        "platform": spec["platform"],
    }
    if spec["shape"] == "tuya_heat_pump":
        records, readings = _tuya_heat_pump_records(
            spec, _show(_checkout(repos, spec), spec["commit"], path))
        fixture["device_name"] = spec["device_name"]
    elif spec["shape"] == "tuya_local":
        repo = _checkout(repos, spec)
        records, readings, extra = _tuya_local_records(
            spec, _show(repo, spec["commit"], path),
            _show(repo, spec["commit"], spec["schema"]))
        fixture["device_name"] = extra.pop("config_name")
        fixture.update(extra)
    else:
        for line in spec["lines"]:
            _check_pin(line, repos)
        rules = [
            _localtuya_rule(line, _show(_checkout(repos, line), line["commit"], line["path"]))
            for line in spec["lines"]
        ]
        records, readings = _localtuya_records(spec, rules)
        fixture["device_name"] = spec["device_name"]
        fixture["device_id"] = spec["device_id"]
        fixture["sources"] = rules
    fixture["records"] = records
    fixture["dp_readings"] = readings
    return fixture


def load(name: str) -> dict:
    """One written fixture. The only entry point the test suite uses."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _dump(fixture: dict) -> str:
    return json.dumps(fixture, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", type=pathlib.Path, default=[],
                        help="a pinned source's checkout; repeat once per source")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--write-corpus", action="store_true",
        help="write the labelled corpus, from the fixtures already on disk",
    )
    parser.add_argument("--check-corpus", action="store_true")
    args = parser.parse_args(argv)
    failures = 0
    if args.write_corpus or args.check_corpus:
        # No --repo: the corpus re-platforms the fixtures this script already
        # wrote and shapes its hand-set devices on a rule one of them records.
        # A label that names no record stops the build inside build_corpus.
        target = FIXTURES / CORPUS["fixture"]
        built = _dump(build_corpus(CORPUS))
        if args.write_corpus:
            target.write_text(built, encoding="utf-8")
            print(f"wrote {target}")
            return 0
        recorded = target.read_text(encoding="utf-8") if target.exists() else ""
        if recorded == built:
            print(f"{CORPUS['fixture']}: matches the recorded corpus")
            return 0
        return 1
    if args.write or args.check:
        if not args.repo:
            raise SystemExit("--write and --check need one --repo per pinned source")
    for spec in (TUYA_HEAT_PUMP, TUYA_LOCAL, LOCALTUYA):
        target = FIXTURES / spec["fixture"]
        built = _dump(build(spec, args.repo))
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(built, encoding="utf-8")
            print(f"wrote {target}")
            continue
        recorded = target.read_text(encoding="utf-8") if target.exists() else ""
        if recorded == built:
            print(f"{spec['fixture']}: matches {spec['repo']} {spec['commit'][:7]}")
        else:
            failures += 1
            print(f"{spec['fixture']}: DIFFERS from {spec['repo']} {spec['commit'][:7]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
