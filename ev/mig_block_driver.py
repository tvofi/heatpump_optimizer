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
    # 7.2 then places each surviving key: neither is DATA_ONLY, so both land in options
    and _mig_bad.data == {}
    and _mig_bad.options == {"dhw_tank_volume": 200.0, "silent_mode_power_fraction": "abc"},
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

# The keys the migration must repair, by the parse's own behaviour rather than
# by entry_config._DEFAULTED_NUMBERS: a field whose parse reads numeric text as
# its float and other text as the default. Text left under one such key is read
# raw by no parse at all once a release reads it outside EntryConfig.
from heatpump_optimizer.entry_config import number_repairs as _mig_repairs  # noqa: E402


def _mig_defaulted(f):
    _p = f.metadata["parse"]
    _twelve = _p("12", f.default)
    return _p("abc", f.default) == f.default and type(_twelve) is float and _twelve == 12.0


_mig_numeric = [f.name for f in _mig_fields(_MigEC) if f.metadata and _mig_defaulted(f)]
_mig_unrepaired = [k for k in _mig_numeric if _mig_repairs({k: "12"}) != {k: 12.0}]
R.check(
    "every option whose parse defaults text it cannot read is repaired by the migration",
    "optimization_interval" in _mig_numeric and "wood_lighting_lead_minutes" in _mig_numeric
    and not _mig_unrepaired,
    f"unrepaired: {_mig_unrepaired}",
)
R.check(
    "and a stored number under each is left alone (null control)",
    not [k for k in _mig_numeric if _mig_repairs({k: 12.0})],
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
sys.exit(R.close("MIGRATION BLOCK CHECKS"))
