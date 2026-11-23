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
from homeassistant.util import dt as dt_util
strings = json.loads((ROOT / "strings.json").read_text())
_CRED_DATA = {
    "tibber_token": "secret-token-do-not-ship",
    "name": "HP", "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
}

from heatpump_optimizer.config_flow import HeatPumpOptimizerConfigFlow as _ReauthFlow  # noqa: E402
from heatpump_optimizer.const import CONF_TIBBER_TOKEN as _CONF_TOKEN  # noqa: E402
# --- D10-12: the diagnostics payload ---------------------------------------
R.section("Diagnostics (D10-12)")

from heatpump_optimizer import diagnostics as _diag_mod  # noqa: E402
import json as _json

# #509: what a household looks like in a diagnostics file. The coordinate is
# full precision and its 1-decimal rounding is a different string, so the
# redaction check also catches a rounded leftover, not only the exact value;
# ``_DIAG_DEEP`` sits two levels down and inside a list, because the property
# that stops the NEXT nested location from leaking is depth-independence, not a
# rule about ``solar_location``; and the option-level coordinate differs from
# the data-level one so a payload that ever starts emitting option values is
# measured too.
_DIAG_LAT, _DIAG_LON = 59.331234, 18.071234
_DIAG_OPT_LAT, _DIAG_OPT_LON = 59.385555, 18.175555
_DIAG_NAME = "Villa Solbacken Storgatan 5"
_DIAG_TOPIC = "home/storgatan5/ecl110/state"
_DIAG_DEEP = {
    "sites": [{"station": {"latitude": _DIAG_LAT, "longitude": _DIAG_LON}}],
    # A coordinate that is not a number: free text under a coordinate key can
    # be an address, so it must not survive the way a number does.
    "typed": {"latitude": "Storgatan 5, Solna", "longitude": None},
}
_DIAG_DATA = {
    **_CRED_DATA,
    "name": _DIAG_NAME,
    const.CONF_SOLAR_LOCATION: {
        "latitude": _DIAG_LAT,
        "longitude": _DIAG_LON,
        "elevation": "not-a-number",
    },
    const.CONF_ECL110_STATE_TOPIC: _DIAG_TOPIC,
    "_deep": _DIAG_DEEP,
    # The setup-time value the options below override: the live v6.7.17
    # dump showed this one instead of the value the install was running on.
    const.CONF_TARGET_TEMP: 20.0,
}
_DIAG_OPTIONS = {
    const.CONF_SOLAR_LOCATION: {
        "latitude": _DIAG_OPT_LAT,
        "longitude": _DIAG_OPT_LON,
    },
    const.CONF_TARGET_TEMP: 21.0,
    # Saved by the options flow unchanged: an option equal to its setup value
    # overrides nothing, so it is not named as one (review of #2071).
    const.CONF_ECL110_STATE_TOPIC: _DIAG_TOPIC,
}

_diag_hass = FakeHass()
_diag_entry = FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
_diag_entry.runtime_data = integration.HeatPumpOptimizerCoordinator(
    _diag_hass, FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
)
_diag = asyncio.run(
    _diag_mod.async_get_config_entry_diagnostics(_diag_hass, _diag_entry)
)
_blob = _json.dumps(_diag, default=str)
_HA_REDACTED = "**REDACTED**"


def _diag_at(node, *path):
    """Walk ``path`` through dicts and lists, returning None at any mismatch.

    Over-redaction replaces a dict with a string, so a check written as
    ``payload["config"]["solar_location"].get(...)`` raises instead of
    failing -- which aborts the section before the over-redaction control
    below can run. This keeps every outcome a named check.
    """
    for step in path:
        if isinstance(step, int):
            if not isinstance(node, list) or len(node) <= step:
                return None
            node = node[step]
        elif isinstance(node, dict):
            node = node.get(step)
        else:
            return None
    return node


R.check(
    "the Tibber token never leaves the instance",
    _diag["config"].get(_CONF_TOKEN) == _HA_REDACTED
    and "stub-token" not in _blob
    and _CRED_DATA[_CONF_TOKEN] not in _blob,
    "a credential (or a fragment of it) appeared in the payload",
)

# --- #509: no precise coordinate, and no household label, in the payload ----
R.check(
    "no precise coordinate leaves the instance, from data or from options",
    not any(
        repr(_c) in _blob
        for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
    ),
    "a full-precision coordinate appeared in the diagnostics payload: "
    + ", ".join(
        repr(_c)
        for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
        if repr(_c) in _blob
    ),
)
def _diag_payload_at(when):
    """The diagnostics payload with the clock pinned to ``when``."""
    dt_util.freeze(when)
    try:
        _hass = FakeHass()
        _entry = FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
        _entry.runtime_data = integration.HeatPumpOptimizerCoordinator(
            _hass, FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
        )
        return asyncio.run(_diag_mod.async_get_config_entry_diagnostics(_hass, _entry))
    finally:
        dt_util.freeze(None)


def _clockless(a, b):
    """``a`` with every value differing from ``b`` replaced by None, at any depth.

    ``a`` and ``b`` are one payload taken at two pinned clocks, so what differs
    is what the clock wrote (``exported_at``, the draw-range timestamp, any
    later one) and no field is named here. A rounded coordinate such as "18.1"
    is searched only in what is left, because a clock reading holds one by
    chance (the check failed 1 of 2711 on main at 50373173).
    """
    if isinstance(a, dict) and isinstance(b, dict):
        return {k: _clockless(v, b.get(k)) for k, v in a.items()}
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [_clockless(x, y) for x, y in zip(a, b)]
    return a if a == b else None


_CLOCK_A = datetime(2026, 1, 5, 3, 4, 5, tzinfo=UTC)
_CLOCK_B = datetime(2026, 7, 9, 10, 11, 12, tzinfo=UTC)
_ROUNDED = tuple(
    str(round(_c, 1)) for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
)


def _rounded_hits(first, second):
    """Each rounded coordinate found in the clock-free payload, with its context."""
    blob = _json.dumps(_clockless(first, second), default=str)
    return [
        f"{r!r} in ...{blob[max(0, i - 40) : i + 20]}..."
        for r in _ROUNDED
        for i in [blob.find(r)]
        if i >= 0
    ]


_diag_a = _diag_payload_at(_CLOCK_A)
_diag_b = _diag_payload_at(_CLOCK_B)
R.check(
    "the location is redacted whole, from data and from options, not coarsened",
    _diag_at(_diag, "config_setup", const.CONF_SOLAR_LOCATION) == _HA_REDACTED
    and _diag_at(_diag, "config", const.CONF_SOLAR_LOCATION) == _HA_REDACTED
    and not _rounded_hits(_diag_a, _diag_b),
    repr(_diag_at(_diag, "config", const.CONF_SOLAR_LOCATION))
    + " / rounded matches: "
    + "; ".join(_rounded_hits(_diag_a, _diag_b)),
)
# The flake, deterministically: a clock reading that holds a rounded coordinate
# fails the whole-blob search and passes the clock-free one.
_diag_p = _diag_payload_at(datetime(2026, 1, 5, 3, 4, 18, 100000, tzinfo=UTC))
R.check(
    "the rounded-coordinate search ignores a clock reading that contains one",
    any(r in _json.dumps(_diag_p, default=str) for r in _ROUNDED)
    and not _rounded_hits(_diag_p, _diag_a),
    "poisoned clock: whole-blob hit expected, clock-free hit not",
)
# Null control: a genuinely coarsened coordinate still fails the new search.
_coarse = {**_diag_a, "config": {**_diag_a["config"], "coarse_probe": _ROUNDED[0]}}
_coarse_b = {**_diag_b, "config": {**_diag_b["config"], "coarse_probe": _ROUNDED[0]}}
R.check(
    "a genuinely coarsened coordinate in the payload still fails the clock-free search",
    bool(_rounded_hits(_coarse, _coarse_b)),
)
R.check(
    "a coordinate nested below the top level, inside a list, is redacted",
    _diag_at(_diag, "config", "_deep", "sites", 0, "station")
    == {"latitude": _HA_REDACTED, "longitude": _HA_REDACTED},
    repr(_diag_at(_diag, "config", "_deep", "sites", 0, "station")),
)
R.check(
    "a coordinate that is not a number is redacted too (None stays None, as in Home Assistant)",
    _diag_at(_diag, "config", "_deep", "typed")
    == {"latitude": _HA_REDACTED, "longitude": None}
    and "Storgatan 5, Solna" not in _blob,
    f"a non-numeric coordinate came back as {_diag_at(_diag, 'config', '_deep', 'typed')!r}",
)
R.check(
    "the installation name the user typed never leaves the instance",
    _diag["config"].get("name") == _HA_REDACTED and _DIAG_NAME not in _blob,
    "the user's chosen entry name appeared in the diagnostics payload",
)
# The over-redaction control. Diagnostics exist for support; a fix that
# redacts the whole config would pass every check above and make the file
# useless, so the two things a bug report is actually read for are pinned.
R.check(
    "the entity ids and the MQTT topic survive redaction",
    _diag_at(_diag, "config", "weather_entity") == _CRED_DATA["weather_entity"]
    and _diag_at(_diag, "config", "indoor_temp_entity")
    == _CRED_DATA["indoor_temp_entity"]
    and _diag_at(_diag, "config", const.CONF_ECL110_STATE_TOPIC) == _DIAG_TOPIC,
    "redaction removed what a diagnostics file is read for: weather_entity is "
    f"{_diag_at(_diag, 'config', 'weather_entity')!r}",
)
# Live v6.7.17 install: ``config`` was ``entry.data`` alone, so a dump showed
# the setup-time values while the coordinator ran on the options laid over
# them. The live merge is what the coordinator reads; the setup data stays
# beside it, with the keys options override named.
_diag_live = {**_DIAG_DATA, **_DIAG_OPTIONS}
R.check(
    "the diagnostics config is the live config, with options laid over setup data",
    _diag_at(_diag, "config", const.CONF_TARGET_TEMP)
    == _diag_live[const.CONF_TARGET_TEMP]
    == _diag_entry.runtime_data._ctx._config[const.CONF_TARGET_TEMP]
    and _diag_at(_diag, "config", "indoor_temp_entity")
    == _CRED_DATA["indoor_temp_entity"],
    f"config target is {_diag_at(_diag, 'config', const.CONF_TARGET_TEMP)!r}, "
    f"the coordinator runs on {_diag_live[const.CONF_TARGET_TEMP]!r}",
)
R.check(
    "the setup data is kept beside it, with the keys options override named",
    _diag_at(_diag, "config_setup", const.CONF_TARGET_TEMP) == 20.0
    and _diag.get("config_overridden_by_options")
    == sorted([const.CONF_SOLAR_LOCATION, const.CONF_TARGET_TEMP])
    and _diag_at(_diag, "entry", "options_keys") == sorted(_DIAG_OPTIONS),
    repr((_diag_at(_diag, "config_setup", const.CONF_TARGET_TEMP),
          _diag.get("config_overridden_by_options"))),
)
R.check(
    "an option equal to its setup value is not named as overriding it",
    const.CONF_ECL110_STATE_TOPIC in (_diag_at(_diag, "entry", "options_keys") or [])
    and const.CONF_ECL110_STATE_TOPIC
    not in (_diag.get("config_overridden_by_options") or []),
    repr(_diag.get("config_overridden_by_options")),
)
R.check(
    "the setup data is redacted like the live config",
    _diag_at(_diag, "config_setup", "name") == _HA_REDACTED
    and _diag_at(_diag, "config_setup", _CONF_TOKEN) == _HA_REDACTED,
    repr(_diag_at(_diag, "config_setup", "name")),
)
R.check(
    "the payload is plain JSON and names the coordinator's state",
    isinstance(_diag.get("coordinator"), dict)
    and "tibber_outage_cycles" in _diag["coordinator"]
    and "mode" in _diag["coordinator"],
    f"coordinator keys: {sorted((_diag.get('coordinator') or {}).keys())[:8]}",
)
R.check(
    "the learner summaries are present",
    any(
        k in (_diag.get("coordinator") or {})
        for k in ("accuracy", "comfort_learner", "curve_learner", "price_model")
    ),
    "none of the four learner summaries appeared",
)

# The snapshot's wiring, at the values (not just the keys): a delegate that
# stopped calling the view, or a view that stopped reading its members,
# leaves the keys in place with None behind them (R9-EG-B6, #1739).
R.check(
    "the coordinator snapshot carries the live counter values, not None placeholders",
    _diag["coordinator"].get("solve_failures") == 0
    and _diag["coordinator"].get("tibber_outage_cycles") == 0
    and _diag["coordinator"].get("tibber_reauth_started") is False
    and _diag["coordinator"].get("cop_samples") is not None,
    f"counters: " + repr({
        k: _diag["coordinator"].get(k)
        for k in ("solve_failures", "tibber_outage_cycles",
                  "tibber_reauth_started", "cop_samples")
    }),
)
# The mode is handed to the view by the coordinator (ADR-005), so a
# coordinator that stopped handing it would report None behind a present key.
# A real coordinator is told two modes through ``async_set_mode`` in turn: the
# second is the null control, so a constant or stale value fails one of them.
_diag_coord = _diag_entry.runtime_data
_diag_modes = {}
for _m in (const.MODE_BOOST, const.MODE_COMFORT):
    asyncio.run(_diag_coord.async_set_mode(_m, refresh=False))
    _diag_modes[_m] = (
        _diag_coord.diagnostics_state().mode,
        asyncio.run(_diag_mod.async_get_config_entry_diagnostics(
            _diag_hass, _diag_entry))["coordinator"]["mode"],
    )
asyncio.run(_diag_coord.async_set_mode(const.MODE_AUTO, refresh=False))
R.check(
    "the diagnostics view and the download report the mode a real coordinator was "
    "set to, for each of two modes",
    all(got == (m, m) for m, got in _diag_modes.items()),
    repr(_diag_modes),
)
sys.exit(R.close("ENTITY CHECKS"))
