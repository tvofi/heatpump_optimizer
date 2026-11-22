"""Entity and platform tests for the new features.

    PYTHONPATH=tests/hastub python tests/entities.py

The entities are thin readers over ``coordinator.data``, so they are exercised
against a data dict rather than a live coordinator. That is deliberate: the
existing ``solar_alignment.py`` fixture has to know exactly which private
attributes a coordinator method touches, and it broke on every new attribute.
Testing the entities against their actual input — the published data — does not
have that problem.

What this catches that nothing else does:

* a platform added to ``PLATFORMS`` but not to ``PLATFORM_LIST``, or vice
  versa, which loads nothing and reports no error;
* an options menu entry with no handler behind it, which renders a menu row
  that does nothing;
* ``strings.json`` drifting from the translations, which had already happened
  twice by v2.7.0;
* an accumulating sensor declared ``MEASUREMENT``, which silently keeps it out
  of the Energy dashboard — the one place the integration's central claim
  should be visible.
"""
from __future__ import annotations

import subprocess
import ast
import asyncio
import json
import pathlib
import re
import os
import string
import sys
import tempfile
import threading
from datetime import UTC, datetime, timedelta
from pathlib import Path

from layout import canon as _layout_canon, locate as _layout_locate, repo_path as _layout_repo_path
from throwaway_git import throwaway_git_env, throwaway_git_environ, throwaway_git_init

# Dynamic import of a moved instrument. The string is the path while the file
# is still there, otherwise the path the move map records, so a module import
# follows the same file the `node <locate>` invocations already run.
_PL_IMPORT = "import('./" + _layout_locate(".claude/workflows/policy_lint.mjs") + "')"
_COUNTS_IMPORT = "import('./" + _layout_locate(".claude/workflows/counts.mjs") + "')"
from harness import (
    SHIPPED_LANGS,
    TRANSLATED_LANGS,
    EagerHass,
    FakeCoordinator,
    FakeEntry,
    FakeHass,
    FakeState,
    Results,
    ha_setup_component,
    ha_setup_entry,
    ha_unload_entry,
)

# #1495: the Mold Floor Breach sensor reads its floor from the coordinator's
# own _mold_floor_series. A FakeCoordinator stands for an install at the
# default (mold guard off), where that series is None; the arms that need a
# floor use a real coordinator after one input-read cycle. Set here rather
# than in harness.py for the reason the next comment gives.
FakeCoordinator._mold_floor_series = lambda self, outdoor, target_cap=None: None

# #924: the fixed first refresh fetches through the base class, and a token
# config has no HTTP under the stub. The entity feed is a real production
# source that works offline. Local rather than shared through harness.py:
# harness.py is a capture source, and a diff touching it makes every
# inherited claim list this branch's to rewrite -- the corner card_drift
# reports and the claims bot refuses to repair (#743/#747).
# The light first refresh CONSUMES ``_skip_solve_once`` at setup -- arm it
# after setup if a test wants it.
_OFFLINE_PRICES = {
    "price_source": "entity",
    "price_entity": "sensor.prices",
}


def _seed_prices(hass, entity_id="sensor.prices", hours=48, base=0.5):
    """A Nord-Pool-style sensor with ``hours`` fresh hourly rows."""
    from datetime import timedelta

    from homeassistant.util import dt as dt_util

    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    hass.states.set(
        entity_id,
        FakeState(
            str(base),
            attributes={
                "raw_today": [
                    {
                        "start": (now + timedelta(hours=h)).isoformat(),
                        "value": round(base + 0.1 * (h % 4), 3),
                    }
                    for h in range(hours)
                ]
            },
        ),
    )


from homeassistant.components.sensor import SensorStateClass

import heatpump_optimizer as integration
from homeassistant import const as ha_const
from heatpump_optimizer import (
    binary_sensor,
    button,
    config_flow,
    const,
    sensor,
    topology,
)
from golden import (  # noqa: E402
    _nested_schema,
    _presented_fields,
    empty_section_payload,
    nest_flat,
)

R = Results("Entities and platforms")

ROOT = Path("custom_components/heatpump_optimizer")
ENTRY = FakeEntry()

# v5.0.0: display names live in the translation files, not in ``_attr_name``.
# The tests keep addressing entities by their English display name — resolved
# through strings.json exactly the way Home Assistant's frontend would — so a
# missing translation entry fails loudly here rather than rendering as a raw
# key in the UI.
_ENTITY_STRINGS = json.loads((ROOT / "strings.json").read_text())["entity"]


def display_name(platform: str, entity) -> str:
    key = getattr(entity, "_attr_translation_key", None)
    return _ENTITY_STRINGS.get(platform, {}).get(key, {}).get(
        "name", f"<untranslated {platform}:{key}>"
    )


# ===========================================================================
# Platform registration
# ===========================================================================
R.section("Config entry migration")

_mig_hass = FakeHass()
_mig = FakeEntry()
_mig.version = const.CONFIG_ENTRY_VERSION
_mig.minor_version = const.CONFIG_ENTRY_MINOR_VERSION
R.check(
    "the current version is a no-op that reports success",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _mig)) is True
    and _mig.version == const.CONFIG_ENTRY_VERSION,
)
_old = FakeEntry()
_old.version = 1
_old_data = dict(_old.data)
R.check(
    "an old entry is stamped forward without touching its data",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _old)) is True
    and _old.version == const.CONFIG_ENTRY_VERSION
    and _old.data == _old_data,
    "every option is read with a default, so only the stamp moves",
)
# D1-s2-05: an earlier release's non-number under a numeric option raised in
# the thermal table or the comfort band at setup or on every cycle.
from heatpump_optimizer.entry_config import EntryConfig as _MigEC  # noqa: E402
from dataclasses import fields as _mig_fields  # noqa: E402

_mig_bad_data = {"min_temperature": [19.0], "max_temperature": "abc", "dhw_tank_volume": "200",
                 "mixing_valve_target": "abc"}
_mig_bad_options = {"target_temperature": None, "comfort_weight": {"v": 1.0}, "price_weight": "nan",
                    "cop_scale": True, "silent_mode_power_fraction": "abc"}
import logging as _mig_logging  # noqa: E402


class _MigLog(_mig_logging.Handler):
    def __init__(self):
        super().__init__(_mig_logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(record)


def _mig_warnings(entry):
    """Migrate ``entry``; return (result, the integration's WARNING records)."""
    handler, logger = _MigLog(), _mig_logging.getLogger(integration.__name__)
    logger.addHandler(handler)
    try:
        return asyncio.run(integration.async_migrate_entry(_mig_hass, entry)), handler.records
    finally:
        logger.removeHandler(handler)


_mig_quiet = FakeEntry(data={"min_temperature": 19.0, "dhw_tank_volume": 200.0})
_mig_quiet_ok, _mig_quiet_logs = _mig_warnings(_mig_quiet)
R.check(
    "a healthy old entry migrates with no repair warning (null control)",
    _mig_quiet_ok is True and not _mig_quiet_logs
    and {**_mig_quiet.data, **_mig_quiet.options} == {"min_temperature": 19.0, "dhw_tank_volume": 200.0},
    f"{[r.getMessage() for r in _mig_quiet_logs]} data={_mig_quiet.data} options={_mig_quiet.options}",
)
_mig_bad = FakeEntry(data=dict(_mig_bad_data), options=dict(_mig_bad_options))
_mig_before = _MigEC.from_mapping({**_mig_bad.data, **_mig_bad.options})
_mig_bad_ok, _mig_bad_logs = _mig_warnings(_mig_bad)
R.check(
    "an old entry's non-numbers under numeric options are repaired, with one warning naming them",
    _mig_bad_ok is True
    and len(_mig_bad_logs) == 1 and "min_temperature" in _mig_bad_logs[0].getMessage()
    and _mig_bad.version == const.CONFIG_ENTRY_VERSION
    # Numeric text is its number, None is dropped, anything else is its default;
    # 7.2 then places each key: none is DATA_ONLY, so every one lands in options.
    and _mig_bad.data == {}
    and _mig_bad.options == {
        "min_temperature": const.DEFAULT_MIN_TEMP, "max_temperature": const.DEFAULT_MAX_TEMP,
        "dhw_tank_volume": 200.0, "mixing_valve_target": const.DEFAULT_MIXING_VALVE_TARGET,
        "comfort_weight": const.DEFAULT_COMFORT_WEIGHT, "price_weight": const.DEFAULT_PRICE_WEIGHT,
        "cop_scale": const.DEFAULT_COP_SCALE, "silent_mode_power_fraction": "abc"},
    f"data={_mig_bad.data} options={_mig_bad.options}",
)
_mig_after = _MigEC.from_mapping({**_mig_bad.data, **_mig_bad.options})
_mig_moved = [
    f.name for f in _mig_fields(_MigEC)
    if f.metadata and getattr(_mig_before, f.name) != getattr(_mig_after, f.name)
]
R.check(
    "and the repair moves no parsed field (refused-number keys are left alone)",
    not _mig_moved,
    f"moved: {_mig_moved}",
)

# sweep-P1 (early_cutoff.arm): a re-solve interval outside (0, a day] is no
# interval; the parse reads it as the default.
_mig_iv = {v: _MigEC.from_mapping({"optimization_interval": v}).optimization_interval
           for v in (0, -5, 0.0, 1e12, 1440.5, "nan", 10, 120, 1440)}
R.check(
    "an optimization interval outside (0, a day] parses as the default",
    all(_mig_iv[v] == const.DEFAULT_OPTIMIZATION_INTERVAL for v in (0, -5, 0.0, 1e12, 1440.5, "nan")),
    f"{_mig_iv}",
)
R.check(
    "and one inside it, both ends' neighbours included, is read as stored (null control)",
    _mig_iv[10] == 10.0 and _mig_iv[120] == 120.0 and _mig_iv[1440] == 1440.0,
    f"{_mig_iv}",
)

# D1-s2-05, the whole class: every numeric option a release stores. The rule
# enumerates it from where the keys come from and where they are read, not
# from the repair's own key set. Those are the options flow's number rows (a
# money row builds its NumberSelector per currency) and the building
# questionnaire's number fields. They are also every key
# ThermalParameters.from_config or comfort_band.violations reads with a
# numeric default (recorded by a mapping that answers every read with its
# default), and every field EntryConfig parses as a number.
import inspect as _mig_inspect  # noqa: E402
from homeassistant.helpers import selector as _mig_selector  # noqa: E402
from heatpump_optimizer import comfort_band as _mig_band  # noqa: E402
from heatpump_optimizer import entry_config as _mig_entry  # noqa: E402
from heatpump_optimizer.entry_config import number_repairs as _mig_repairs  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters as _MigTP  # noqa: E402


class _MigReads(dict):
    """An empty mapping that records each key read with ``.get`` and its default."""

    def __init__(self):
        super().__init__()
        self.read = {}

    def get(self, key, default=None):
        self.read.setdefault(key, default)
        return default


def _mig_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _mig_raw_numbers(read):
    reads = _MigReads()
    read(reads)
    return {k for k, v in reads.read.items() if _mig_number(v)}


_MIG_NUMERIC_PARSES = {
    const.finite_float, _mig_entry._nonzero_number, _mig_entry._interval_minutes,
    _mig_entry._lead_minutes, _mig_entry._whole, _mig_entry._refused_number,
}
_mig_parse = {f.name: f.metadata["parse"] for f in _mig_fields(_MigEC) if f.metadata}
_mig_class = {
    "flow": {
        r.key for r in config_flow._OPTION_FIELDS
        if isinstance(r.widget, _mig_selector.NumberSelector)
        or (isinstance(r.widget, config_flow._ByHass)
            and re.search(r"\b_(money|number)\(", _mig_inspect.getsource(r.widget.of)))
    },
    "questionnaire": {
        m.schema for m, w in config_flow._questionnaire_fields({}).items()
        if isinstance(w, _mig_selector.NumberSelector)
    },
    "thermal": _mig_raw_numbers(_MigTP.from_config),
    "band": _mig_raw_numbers(lambda reads: _mig_band.violations({}, reads)),
    "parsed": {k for k, p in _mig_parse.items() if p in _MIG_NUMERIC_PARSES},
}
_mig_members = sorted(set().union(*_mig_class.values()))
R.check(
    "the numeric-option census reaches every source it enumerates (precondition)",
    all(_mig_class.values())
    and {"day_start_hour", "buffer_tank_volume", "heated_area_m2", "wood_price_sek_m3",
         "price_vat"} <= set(_mig_members),
    f"{ {s: len(k) for s, k in _mig_class.items()} }",
)
_mig_undeclared = [k for k in _mig_members if _mig_parse.get(k) not in _MIG_NUMERIC_PARSES]
R.check(
    "every numeric option a release stores is declared in EntryConfig with a numeric parse",
    not _mig_undeclared,
    f"undeclared: {_mig_undeclared}",
)
# The residue: a ``_refused_number`` field reads a refused value as None, which
# caps nothing, and dropping the key would make it the default instead.
_mig_repaired = [k for k in _mig_members if _mig_parse.get(k) is not _mig_entry._refused_number]
_mig_open = {}
for _k in _mig_repaired:
    if _k not in _mig_parse:
        _mig_open[_k] = ["undeclared"]
        continue
    for _bad in ("abc", None, [12], {"v": 12}, "12"):
        _rep = _mig_repairs({_k: _bad})
        _before = getattr(_MigEC.from_mapping({_k: _bad}), _k)
        _after = getattr(_MigEC.from_mapping(_mig_entry.repaired_numbers({_k: _bad}, _rep)), _k)
        _stored = _mig_entry.repaired_numbers({_k: _bad}, _rep).get(_k)
        if set(_rep) != {_k} or _before != _after or not (_stored is None or _mig_number(_stored)):
            _mig_open.setdefault(_k, []).append(repr(_bad))
R.check(
    "the migration repairs every member's non-number: numeric text is stored as its number, "
    "None is dropped, anything else is its default, and no parsed field moves",
    _mig_repaired and not _mig_open,
    f"open: {_mig_open}",
)
R.check(
    "and a stored number under each is left alone (null control)",
    not [k for k in _mig_members if _mig_repairs({k: 12.0}) or _mig_repairs({k: 12})],
)
_mig_whole = _mig_repairs({"day_start_hour": "9", "ecl110_mqtt_qos": " 1 ", "day_end_hour": "7.5"})
R.check(
    "an hour stored as text is stored as its whole number, and text no whole number reads as the default",
    _mig_whole == {"day_start_hour": 9, "ecl110_mqtt_qos": 1, "day_end_hour": const.DEFAULT_DAY_END_HOUR}
    and type(_mig_whole["day_start_hour"]) is int,
    f"{_mig_whole}",
)
_mig_raw = FakeEntry(data={"day_start_hour": "abc", "buffer_tank_volume": None, "ecl110_mqtt_qos": "1"})


def _mig_raw_reads(entry):
    """The two raw readers the finding names, over ``entry``'s mapping: None, or what raised."""
    merged = {**entry.data, **entry.options}
    try:
        _MigTP.from_config(merged)
        _mig_band.violations({}, merged)
    except (TypeError, ValueError) as err:
        return repr(err)
    return None


_mig_raw_before = _mig_raw_reads(_mig_raw)
_mig_raw_ok, _ = _mig_warnings(_mig_raw)
R.check(
    "an old entry's text hour and null tank volume no longer raise in the thermal table or the "
    "comfort band once migrated",
    _mig_raw_before is not None and _mig_raw_ok is True and _mig_raw_reads(_mig_raw) is None
    and {**_mig_raw.data, **_mig_raw.options}
    == {"day_start_hour": const.DEFAULT_DAY_START_HOUR, "ecl110_mqtt_qos": 1},
    f"before={_mig_raw_before} after={_mig_raw_reads(_mig_raw)} "
    f"stored={ {**_mig_raw.data, **_mig_raw.options} }",
)
# A reader that takes a key's presence (a zone, the hot-water tank, the buffer
# cooling prior) reads the repaired entry as it read the stored one.
from heatpump_optimizer import thermal_model as _mig_thermal  # noqa: E402

_mig_present = FakeEntry(data={"upper_floor_thermal_mass": "abc", "dhw_tank_volume": [200],
                               "buffer_cooling_rate": {"v": 1.0}})


def _mig_presence(entry):
    merged = {**entry.data, **entry.options}
    return (_mig_thermal.two_zone_from_config(merged), _mig_thermal.dhw_enabled_from_config(merged),
            "buffer_cooling_rate" in merged)


_mig_present_before = _mig_presence(_mig_present)
_mig_present_ok, _ = _mig_warnings(_mig_present)
R.check(
    "a repaired key stays present: an old two-zone, hot-water entry keeps both, and its buffer "
    "cooling rate stays configured",
    _mig_present_ok is True and _mig_present_before == (True, True, True)
    and _mig_presence(_mig_present) == _mig_present_before,
    f"before={_mig_present_before} after={_mig_presence(_mig_present)} "
    f"stored={ {**_mig_present.data, **_mig_present.options} }",
)
_mig_cleared = FakeEntry(data={"dhw_tank_volume": None})
_mig_cleared_before = _mig_presence(_mig_cleared)
_mig_cleared_ok, _ = _mig_warnings(_mig_cleared)
R.check(
    "and a stored None is no value: it is dropped, so a cleared tank volume enables no hot water",
    _mig_cleared_ok is True and _mig_cleared_before[1] is False
    and _mig_presence(_mig_cleared)[1] is False and not {**_mig_cleared.data, **_mig_cleared.options},
    f"before={_mig_cleared_before} after={_mig_presence(_mig_cleared)} "
    f"stored={ {**_mig_cleared.data, **_mig_cleared.options} }",
)

_new = FakeEntry()
_new.version = const.CONFIG_ENTRY_VERSION + 1
R.check(
    "a downgrade is refused rather than mangled",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _new)) is False,
)

# R11-SEAM-config: 7.2 stores each key in its one place (entry_config.placed).
from heatpump_optimizer import entry_config as _mig_ec  # noqa: E402

_m71 = FakeEntry(
    data={"name": "Annex", const.CONF_TIBBER_TOKEN: "t", const.CONF_TARGET_TEMP: 21.0},
    options={const.CONF_TARGET_TEMP: 22.0},
)
_m71.version = const.CONFIG_ENTRY_VERSION
_m71_effective = {**_m71.data, **_m71.options}
R.check(
    "a 7.1 entry migrates to 7.2: data holds DATA_ONLY alone, the effective mapping is "
    "unchanged and a key in both sides keeps the options value in force",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _m71)) is True
    and (_m71.version, _m71.minor_version)
    == (const.CONFIG_ENTRY_VERSION, const.CONFIG_ENTRY_MINOR_VERSION)
    and set(_m71.data) <= _mig_ec.DATA_ONLY
    and {**_m71.data, **_m71.options} == _m71_effective
    and _m71.options[const.CONF_TARGET_TEMP] == 22.0,
    f"data={_m71.data} options={_m71.options} minor={_m71.minor_version}",
)
# Null control: an entry already at the minor version is not rewritten, so a
# 7.2 written under a downgraded release's reconfigure is left as it stands.
_m72 = FakeEntry(data={"name": "Annex", const.CONF_TARGET_TEMP: 21.0})
_m72.version = const.CONFIG_ENTRY_VERSION
_m72.minor_version = const.CONFIG_ENTRY_MINOR_VERSION
_m72_updates = len(_mig_hass.config_entries.updated)
R.check(
    "an entry at the current minor version is not rewritten",
    asyncio.run(integration.async_migrate_entry(_mig_hass, _m72)) is True
    and len(_mig_hass.config_entries.updated) == _m72_updates
    and _m72.data == {"name": "Annex", const.CONF_TARGET_TEMP: 21.0},
    f"data={_m72.data} updates={_mig_hass.config_entries.updated[_m72_updates:]}",
)
# An undo record written before the migration holds its settings in data:
# undoing it stores each key where the entry now keeps it.
_undo_rec = _mig_ec.undo_point(
    const.FACTORY_RESET_SCOPES[0], {"name": "Annex", const.CONF_TARGET_TEMP: 21.0}, {})
_undone = _mig_ec.undone_settings({"name": "Annex"}, {}, _undo_rec)
R.check(
    "undoing a reset recorded before 7.2 places the restored settings in options",
    _undone is not None
    and set(_undone[0]) <= _mig_ec.DATA_ONLY
    and _undone[1].get(const.CONF_TARGET_TEMP) == 21.0,
    f"record={_undo_rec} undone={_undone}",
)


# ===========================================================================
# Service handlers, dispatched through the registry
# ===========================================================================


sys.exit(R.close("ENTITY CHECKS"))
