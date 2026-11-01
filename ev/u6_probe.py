"""Unit tests for the v2.8.0 feature modules.

    PYTHONPATH=tests/hastub python tests/features.py

Each module is driven directly rather than through a full optimization run.
The end-to-end scripts already cover "does the plan come out sensible"; what
they cannot cover is a detector that never fires, a watchdog that lets a
flatline through, or a tariff term that charges a month's fee once per hour.
Those failures produce a *plausible* plan, which is exactly why they need
tests that look at the mechanism rather than at the outcome.
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone

from harness import FakeHass, FakeState, Results, UTC, minutes_ago, with_config
from profiles import solve_inputs  # noqa: E402

import numpy as np

from heatpump_optimizer import away as away_mode
from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer import battery as battery_view
from heatpump_optimizer import presets, price_tiles, pv
from heatpump_optimizer.accuracy import (
    AccuracySample,
    AccuracyTracker,
    delivered_ratio,
)
from heatpump_optimizer.comfort_learning import (
    COMFORT_WEIGHT_MAX,
    COMFORT_WEIGHT_MIN,
    ComfortLearner,
    OverrideEvent,
)
from heatpump_optimizer.const import COP_SCALE_MAX, COP_SCALE_MIN
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer.defrost import (
    DEFROST_LOSS_MULTIPLIER,
    DERATE_CONFIDENCE_SAMPLES,
    DERATE_MAX,
    HUMIDITY_CENTERS,
    DefrostDerate,
    DefrostWindow,
    derate_from_duty,
)
from heatpump_optimizer.external_heat import (
    ExternalHeatConfig,
    ExternalHeatDetector,
    ExternalHeatObservation,
)
from heatpump_optimizer import inputs as inputs_mod
from heatpump_optimizer import flow_lift, pump_mode, pump_signals
from heatpump_optimizer.pump_signals import PumpSignals
from heatpump_optimizer.inputs import (
    InputReader,
    InputReading,
    normalize_power_kw,
    parse_bool,
    stale_summary,
)
from heatpump_optimizer.price_model import (
    PriceShapeModel,
    extend_price_series,
    hourly_from_entries,
)
from heatpump_optimizer.sysid import (
    HousePlant,
    PHASE_ARMED,
    PHASE_DONE,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakBilling,
    PeakTracker,
    _smooth_topk_sum,
    peak_cost,
    peak_cost_smooth,
    realised_peak,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
from heatpump_optimizer.plan_slots import plan_slots
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries)
from heatpump_optimizer.dhw_planner import DhwPlanner, _DhwPlanContext
from heatpump_optimizer.optimizer import _Horizon


def _owned_params(params):
    """A test owner of ``params``, as the coordinator's ``_publish_params`` owns
    its own: the learner reads through ``params`` and publishes a new snapshot."""
    from dataclasses import replace as _replace
    box = [params]

    def publish(**fields):
        box[0] = _replace(box[0], **fields)

    return {"params": lambda: box[0], "publish": publish}


R = Results("Feature modules")
import asyncio as _aio
import json as _fi_json
from profiles import house as _ra_house
from homeassistant.config_entries import ConfigEntryState as _li_state  # noqa: E402
from harness import FakeServiceCall as _li_call  # noqa: E402
def _li_state_of(c):
    return (c._house_heat_loss_scale, c._lower_floor_loss_ratio,
            c._house_heat_loss_samples, c._lower_floor_loss_samples)

# --- R10-FACTORY-RESET: settings, learners or both back to their defaults -----
#
# The owner's request (tvofi, 2026-10-30). Real coordinators over a two-zone
# house with its wiring assigned, set up again the way the reset sets them up
# (every learned store's loader), each expectation a property: kept keys
# unchanged, every other setting reading its declared default, every learner
# reading what a coordinator that never learned reads, and the undo point
# putting both back.
import ast as _fr_ast  # noqa: E402
import dataclasses as _fr_dc  # noqa: E402
from pathlib import Path as _FrPath  # noqa: E402

from homeassistant.helpers import storage as _fr_storage  # noqa: E402
from homeassistant.util import dt as _fr_dt  # noqa: E402
from harness import FakeEntry as _fr_entry_cls, FakeServiceCall as _fr_call  # noqa: E402
from heatpump_optimizer import config_flow as _fr_flow  # noqa: E402
from heatpump_optimizer import const as _fr_const  # noqa: E402
from heatpump_optimizer import entry_config as _fr_ec  # noqa: E402
from heatpump_optimizer import services as _fr_services  # noqa: E402
from heatpump_optimizer.coordinator import (  # noqa: E402
    _FACTORY_VOID as _FR_VOID,
    async_factory_reset as _fr_reset,
)
from heatpump_optimizer.wood_fuel import wood_furnace_on as _fr_wood  # noqa: E402

R.section("A factory reset returns settings, learners or both to their defaults")

_FR_THERMAL_KEYS, _FR_ACC_KEYS = dict(_FR_VOID)["thermal_learning"], dict(_FR_VOID)["accuracy"]

_FR_DATA = dict(_ra_house(two_zone=True), name="My pump", indoor_temp_entity="sensor.indoor",
                lower_floor_temp_entity="sensor.lower", outdoor_temp_entity="sensor.outdoor",
                dhw_temp_entity="sensor.dhw", price_source="entity", price_entity="sensor.price",
                main_fuse_amperes=20, upper_floor_emitter="radiator")
_FR_OPTS = {"comfort_weight": 3.0, "target_temperature": 22.5, "price_weight": 2.0,
            "heat_pump_cop_nominal": 3.9, "dhw_setpoint": 58.0, "freq_control_mode": "observe"}
#: The wiring the body lists, key by key: the reset keeps exactly these.
_FR_LISTED = {
    "name", "compressor_freq_sensor", "price_source", "tibber_token", "solar_forecast_source",
    "two_zone_mode", "upper_floor_emitter", "lower_floor_emitter", "dhw_enabled",
    "wood_furnace_enabled", "dhw_wood_coil_enabled", "mixing_valve_mode",
    "mixing_valve_write_target_kind", "space_setpoint_unit", "topology_layout",
    "topology_positions", "ecl110_command_topic", "ecl110_displace_set_topic",
    "ecl110_state_topic", "ecl110_mqtt_qos", "ecl110_mqtt_retain", "modbus_prefill_prefix",
    "main_fuse_amperes", "main_fuse_phases",
}
#: Every key a ``CONF_`` constant names (a tuple names several: the weekday
#: hot-water windows), and Home Assistant's own ``name``.
_FR_OPTION_KEYS = {key for name, v in vars(_fr_const).items() if name.startswith("CONF_")
                   for key in ((v,) if isinstance(v, str) else v if isinstance(v, tuple) else ())} | {"name"}
_FR_ENTITY_KEYS = {k for k in _FR_OPTION_KEYS if k.endswith("_entity")}


async def _fr_boot(hass, entry):
    """What the reset's ``async_setup`` builds: a coordinator over every learned store."""
    c = Coord(hass, entry)
    for load in (c._dhw_learner.async_load_profile, c._dhw_learner.async_load_draws,
                 c._async_load_thermal_learning, c._async_load_price_model,
                 c._async_load_accuracy, c._async_load_snapshots):
        await load()
    entry.runtime_data, entry.state = c, _li_state.LOADED
    return c


def _fr_learn(c):
    """Every learner the owner names moved off its initial state, saved by its own saver."""
    c._apply_house_heat_loss_scale(1.4)
    c._apply_lower_floor_loss_ratio(1.3)
    c._house_heat_loss_samples, c._lower_floor_loss_samples = 60, 40
    c._apply_cop_scale(1.13)
    c._cop_samples = 20
    c._apply_buffer_cooling_rate(c._buffer_cooling_rate * 1.5)
    c._buffer_cooling_samples = 9
    c._comfort_learner.evidence = -1.4
    c._dhw_learner.apply_cooling_rate(c._dhw_learner.cooling_rate * 1.4)
    c._dhw_learner.cooling_samples = 7
    c._dhw_learner.hourly_profile = c._dhw_learner.normalize_profile([1.0] * 12 + [3.0] * 12)
    c._defrost.factors[0][0] = 0.8
    c._curve_learner.bias = -0.6
    c._freq_fallback = True  # a fact the reset keeps: the watchdog's latch
    c._accuracy.lead_sigma[1.0], c._accuracy.lead_counts[1.0] = 0.3, 12
    c._price_learner.model.shapes[0][3] = 1.2
    c._dhw_learner.draw_stats.fold(_fr_dt.now(), "06:00-09:00", 2.5)
    _aio.run(c._async_save_thermal_learning())
    _aio.run(c._dhw_learner.async_save_profile())
    _aio.run(c._dhw_learner.async_save_draws())
    _aio.run(c._async_save_accuracy())
    _aio.run(c._async_save_price_model())


def _fr_disk(entry_id):
    """Every stored document of the entry, as the stub writes it."""
    prefix = f"{_fr_const.DOMAIN}_{entry_id}_"
    return {k[len(prefix):]: _fi_json.loads(v) for k, v in _fr_storage._DISK.items() if k.startswith(prefix)}


def _fr_learned(c):
    """The learners' persisted shapes without the save stamp and the watchdog's
    latch, a fact the reset keeps (pinned on its own below)."""
    out = c._learner_snapshot_payloads()
    out["thermal_learning"] = {k: v for k, v in out["thermal_learning"].items()
                               if k not in ("updated_at", "freq_fallback")}
    return out


def _fr_case(scope, entry_id, *, learn=True):
    """Reset a learned entry under ``scope``; (before, after, entry, hass, old coordinator)."""
    hass = FakeHass({})
    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id=entry_id)
    hass.config_entries.entries.append(entry)
    c = _aio.run(_fr_boot(hass, entry))
    if learn:
        _fr_learn(c)
    before = {"learned": _fr_learned(c), "disk": _fr_disk(entry_id), "config": {**entry.data, **entry.options}}

    async def _setup(eid):
        hass.config_entries.set_up.append(eid)
        before.setdefault("at_setup", _fr_disk(entry_id))
        await _fr_boot(hass, entry)
        return True

    hass.config_entries.async_setup = _setup
    _aio.run(_fr_reset(c, scope))
    return before, entry, hass, c


def _fr_fresh(entry, entry_id):
    """A coordinator that never learned, over the configuration the reset left."""
    return _aio.run(_fr_boot(FakeHass({}), _fr_entry_cls(data=dict(entry.data), options=dict(entry.options),
                                                       entry_id=entry_id)))


# The enumeration: every option key the integration names, by its constants.
R.check(
    "the kept keys are the listed wiring and every entity assignment, each an option key",
    set(_fr_ec.FACTORY_KEPT) == _FR_LISTED | _FR_ENTITY_KEYS
    and set(_fr_ec.FACTORY_KEPT) <= _FR_OPTION_KEYS and len(_FR_ENTITY_KEYS) > 30,
    f"kept-not-listed {sorted(set(_fr_ec.FACTORY_KEPT) - _FR_LISTED - _FR_ENTITY_KEYS)}, "
    f"listed-not-kept {sorted((_FR_LISTED | _FR_ENTITY_KEYS) - set(_fr_ec.FACTORY_KEPT))}",
)

_fr_s_before, _fr_s_entry, _fr_s_hass, _fr_s_old = _fr_case("settings", "fr_settings")
_fr_s_after = {**_fr_s_entry.data, **_fr_s_entry.options}
_fr_s_new = _fr_s_entry.runtime_data
_fr_parsed = _fr_ec.EntryConfig.from_mapping(_fr_s_after)
_fr_not_default = sorted(
    f.name for f in _fr_dc.fields(_fr_ec.EntryConfig)
    if f.metadata and f.name not in _fr_ec.FACTORY_KEPT and getattr(_fr_parsed, f.name) != f.default
)
R.check(
    "after a settings reset every tunable option reads its default",
    not _fr_not_default and set(_fr_s_after) <= set(_fr_ec.FACTORY_KEPT),
    f"not default {_fr_not_default}, stored beyond the wiring {sorted(set(_fr_s_after) - set(_fr_ec.FACTORY_KEPT))}",
)
_fr_kept_moved = sorted(k for k in _fr_s_before["config"] if k in _fr_ec.FACTORY_KEPT
                        and _fr_s_after.get(k) != _fr_s_before["config"][k])
R.check(
    "after a settings reset every kept key is unchanged, and the topology it implied with it",
    not _fr_kept_moved
    and _fr_s_new._thermal_params.two_zone_enabled is _fr_s_old._thermal_params.two_zone_enabled is True
    and _fr_s_new._thermal_params.dhw_enabled is _fr_s_old._thermal_params.dhw_enabled is True
    and _fr_wood(_fr_s_after) == _fr_wood(_fr_s_before["config"]),
    f"moved {_fr_kept_moved}, two-zone {_fr_s_new._thermal_params.two_zone_enabled}",
)
_fr_s_disk = _fr_disk("fr_settings")


def _fr_unstamped(doc):
    return {k: v for k, v in (doc or {}).items() if k != "updated_at"}


# The reload is an options change, and a learner answers it as it answers any
# options edit (a changed nameplate re-anchors or voids its own learner); what
# the reset itself owes is to write no learned store.
_fr_s_setup = _fr_s_before["at_setup"]
R.check(
    "a settings reset writes no learned store: each is as it was when the entry is set up again",
    all(_fr_unstamped(_fr_s_setup.get(k)) == _fr_unstamped(_fr_s_before["disk"].get(k))
        for k in ("thermal_learning", "dhw_profile", "price_model", "accuracy"))
    and _fr_s_hass.config_entries.unloaded == _fr_s_hass.config_entries.set_up == ["fr_settings"],
    str([k for k in ("thermal_learning", "dhw_profile", "price_model", "accuracy")
         if _fr_unstamped(_fr_s_setup.get(k)) != _fr_unstamped(_fr_s_before["disk"].get(k))]),
)

_fr_l_before, _fr_l_entry, _fr_l_hass, _ = _fr_case("learners", "fr_learners")
_fr_l_fresh = _fr_fresh(_fr_l_entry, "fr_learners_fresh")
_fr_l_got, _fr_l_want = _fr_learned(_fr_l_entry.runtime_data), _fr_learned(_fr_l_fresh)
_fr_named = ("thermal_learning", "dhw_profile", "comfort", "defrost", "accuracy", "price_model")
R.check(
    "the learned state before the reset is not the initial one, learner by learner (the control)",
    all(_fr_l_before["learned"][k] != _fr_l_want[k] for k in _fr_named),
    str([k for k in _fr_named if _fr_l_before["learned"][k] == _fr_l_want[k]]),
)
R.check(
    "after a learners reset every learner reads what one that never learned reads",
    _fr_l_got == _fr_l_want
    and _fr_l_entry.runtime_data._dhw_accuracy.as_dict() == _fr_l_fresh._dhw_accuracy.as_dict()
    and _li_state_of(_fr_l_entry.runtime_data) == (1.0, 1.0, 0, 0),
    str({k: sorted(f for f in set(v) | set(_fr_l_want[k]) if v.get(f) != _fr_l_want[k].get(f))
         for k, v in _fr_l_got.items() if v != _fr_l_want[k]}),
)
# The void list, key by key, against a list this test owns rather than
# ``_FACTORY_VOID`` itself (an enumeration read from the list it checks pins
# nothing): every key a learned store holds is a learner the reset drops, or
# one of these facts it keeps. The heat-loss pair stays, voided by its own
# path; the rest is the anchors, the meter's last COP, snow memory, the
# frequency watchdog's latch, the billed peaks, the mode and the save stamp.
_FR_FACTS = {
    "thermal_learning": {
        "house_heat_loss_scale", "house_heat_loss_samples", "lower_floor_loss_ratio",
        "lower_floor_loss_samples", "house_heat_loss_anchor", "house_heat_loss_basis",
        "lower_floor_loss_anchor", "heat_loss_zone_entities", "measured_cop", "snow_accum_cm",
        "snow_accum_last", "last_heavy_snow", "freq_fallback", "updated_at",
    },
    "accuracy": {"peaks", "mode"},
    "dhw_profile": set(), "dhw_draws": set(), "price_model": set(),
}
_fr_l_setup = _fr_l_before["at_setup"]
_fr_learned_keys = sorted((n, k) for n, facts in _FR_FACTS.items()
                          for k in (_fr_l_before["disk"].get(n) or {}) if k not in facts)
R.check(
    "before a learners reset every learned store is on disk and holds learned keys beyond its facts (the control)",
    all(_fr_l_before["disk"].get(n) for n in _FR_FACTS)
    and {n for n, _ in _fr_learned_keys} == set(_FR_FACTS) and len(_fr_learned_keys) >= 25,
    f"stores absent {sorted(n for n in _FR_FACTS if not _fr_l_before['disk'].get(n))}, "
    f"{len(_fr_learned_keys)} learned key(s)",
)
_fr_left = [(n, k) for n, k in _fr_learned_keys if k in (_fr_l_setup.get(n) or {})]
_fr_facts_lost = sorted((n, k) for n, facts in _FR_FACTS.items() for k in facts
                        if k in (_fr_l_before["disk"].get(n) or {}) and k not in (_fr_l_setup.get(n) or {}))
R.check(
    "a learners reset drops every learned key, key by key, and keeps every fact, before the entry is set up again",
    not _fr_left and not _fr_facts_lost
    and not any(n in _fr_l_setup for n, facts in _FR_FACTS.items() if not facts),
    f"learned left {_fr_left}, facts lost {_fr_facts_lost}, "
    f"whole stores left {sorted(n for n, f in _FR_FACTS.items() if not f and n in _fr_l_setup)}",
)
_fr_l_disk = _fr_disk("fr_learners")
R.check(
    "a learners reset keeps the settings and the stores' facts: the watchdog latch, peaks, mode",
    {**_fr_l_entry.data, **_fr_l_entry.options} == _fr_l_before["config"]
    and _fr_l_entry.runtime_data._freq_fallback is True
    and _fr_l_disk["accuracy"].get("peaks") == _fr_l_before["disk"]["accuracy"].get("peaks")
    and _fr_l_disk["accuracy"].get("mode") == _fr_l_before["disk"]["accuracy"].get("mode"),
    f"freq_fallback {_fr_l_entry.runtime_data._freq_fallback}",
)

_fr_b_before, _fr_b_entry, _fr_b_hass, _ = _fr_case("both", "fr_both")
_fr_b_new = _fr_b_entry.runtime_data
_fr_b_fresh = _fr_fresh(_fr_b_entry, "fr_both_fresh")
R.check(
    "a reset of both leaves the wiring alone and every learner at its initial state",
    _fr_learned(_fr_b_new) == _fr_learned(_fr_b_fresh)
    and set({**_fr_b_entry.data, **_fr_b_entry.options}) <= set(_fr_ec.FACTORY_KEPT)
    and _fr_b_entry.data["indoor_temp_entity"] == "sensor.indoor",
    f"stored {sorted({**_fr_b_entry.data, **_fr_b_entry.options})}",
)
_fr_undo = _fr_b_new._snapshot_ring.snapshots[-1]
R.check(
    "the drift rollback never takes the reset's undo point; the restore does, while it is newest",
    "before_reset" in _fr_undo and _fr_b_new._snapshot_ring.best_restore() is not _fr_undo
    and _fr_b_new._snapshot_ring.undo_target() is _fr_undo,
    f"undo {sorted(_fr_undo)}",
)


def _fr_counting_refresh(c):
    """Record every refresh asked of ``c``: an undo asks the coordinator it unloaded for none."""
    asked = []

    async def _refresh(*_a, **_k):
        asked.append(c)

    c.async_request_refresh = _refresh
    return asked


_fr_b_reset_cfg = {**_fr_b_entry.data, **_fr_b_entry.options}
R.check(
    "the house is auto-mode before the reset and pinned two-zone by it (the undo's control)",
    "two_zone_mode" not in _fr_b_before["config"] and _fr_b_reset_cfg.get("two_zone_mode") == "on",
    f"before {_fr_b_before['config'].get('two_zone_mode')!r}, reset {_fr_b_reset_cfg.get('two_zone_mode')!r}",
)
_fr_b_asked = _fr_counting_refresh(_fr_b_new)
_fr_restored = _aio.run(_fr_b_new.async_restore_learned_snapshot())
_fr_undone = _fr_b_entry.runtime_data
R.check(
    "restore_learned_snapshot undoes the reset: every learner, the accuracy history and the settings exactly as before it",
    _fr_restored is True and _fr_undone is not _fr_b_new and _fr_learned(_fr_undone) == _fr_b_before["learned"]
    and _li_state_of(_fr_undone) == (1.4, 1.3, 60, 40)
    and {**_fr_b_entry.data, **_fr_b_entry.options} == _fr_b_before["config"],
    str({k: sorted(f for f in set(v) | set(_fr_b_before["learned"][k]) if v.get(f) != _fr_b_before["learned"][k].get(f))
         for k, v in _fr_learned(_fr_undone).items() if v != _fr_b_before["learned"][k]})
    + f" config moved {sorted(k for k in set(_fr_b_before['config']) | set({**_fr_b_entry.data, **_fr_b_entry.options}) if _fr_b_before['config'].get(k) != {**_fr_b_entry.data, **_fr_b_entry.options}.get(k))}",
)
R.check(
    "the undo asks the coordinator it unloaded for nothing more: no refresh, no learner applied after it",
    _fr_b_asked == [] and _fr_b_entry.runtime_data is _fr_undone,
    f"refreshes asked {len(_fr_b_asked)}",
)
# The undo's pins, as stored: an explicit value, and one stored on the other
# side (data versus options), each come back where and as they were.
_FR_PIN_DATA = {"name": "x", "two_zone_mode": "auto", "comfort_weight": 3.0, "indoor_temp_entity": "sensor.in"}
_FR_PIN_OPTS = {"dhw_enabled": False, "target_temperature": 22.0}
_fr_pin_reset = _fr_ec.factory_settings(_FR_PIN_DATA, _FR_PIN_OPTS, two_zone=True, dhw=True, wood=False)
_fr_pin_record = _fi_json.loads(_fi_json.dumps(_fr_ec.undo_point("both", _FR_PIN_DATA, _FR_PIN_OPTS)))
R.check(
    "an undo puts each pinned key back where and as it was stored, over the pins the reset wrote",
    _fr_pin_reset != (_FR_PIN_DATA, _FR_PIN_OPTS)
    and _fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record) == (_FR_PIN_DATA, _FR_PIN_OPTS),
    f"reset {_fr_pin_reset}, undone {_fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record)}",
)
# A record missing either half, or holding a half that is not a (data,
# options) pair, undoes no settings: the reset that wrote it kept them, or the
# record is not one an undo point writes.
_fr_pin_malformed = {
    name: _fr_ec.undone_settings(*_fr_pin_reset, record)
    for name, record in (
        ("no pins", {k: v for k, v in _fr_pin_record.items() if k != "pinned"}),
        ("no settings", {k: v for k, v in _fr_pin_record.items() if k != "settings"}),
        ("one side", {**_fr_pin_record, "pinned": [{}]}),
        ("not dicts", {**_fr_pin_record, "settings": [[], []]}),
    )
}
R.check(
    "an undo record missing either half, or holding a malformed one, undoes no settings",
    all(v is None for v in _fr_pin_malformed.values())
    and _fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record) is not None,
    str({k: v is None for k, v in _fr_pin_malformed.items()}),
)
R.check(
    "the spent undo point stays as an ordinary snapshot, so a second restore is the ordinary one",
    not any("before_reset" in snap for snap in _fr_undone._snapshot_ring.snapshots)
    and len(_fr_undone._snapshot_ring.snapshots) == 1,
)


# The undo of a learners reset: its record carries no settings, and the
# settings are left exactly as they are.
_fr_lu_before, _fr_lu_entry, _, _ = _fr_case("learners", "fr_undo_learners")
_fr_lu_new = _fr_lu_entry.runtime_data
_fr_lu_record = _fr_lu_new._snapshot_ring.snapshots[-1].get("before_reset", {})
_fr_counting_refresh(_fr_lu_new)
_fr_lu_ok = _aio.run(_fr_lu_new.async_restore_learned_snapshot())
R.check(
    "restore_learned_snapshot undoes a learners reset: every learner back, the settings untouched",
    _fr_lu_ok is True and "settings" not in _fr_lu_record and _fr_lu_record.get("scope") == "learners"
    and _fr_learned(_fr_lu_entry.runtime_data) == _fr_lu_before["learned"]
    and _li_state_of(_fr_lu_entry.runtime_data) == (1.4, 1.3, 60, 40)
    and {**_fr_lu_entry.data, **_fr_lu_entry.options} == _fr_lu_before["config"],
    f"record {sorted(_fr_lu_record)}, restored {_fr_lu_ok}",
)


async def _fr_failed_unload(scope="both"):
    """An unload Home Assistant refuses: the reset changes nothing but the undo point."""
    hass = FakeHass({})
    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id="fr_no_unload")
    hass.config_entries.entries.append(entry)
    c = await _fr_boot(hass, entry)
    c._apply_house_heat_loss_scale(1.4)
    c._apply_lower_floor_loss_ratio(1.3)
    c._house_heat_loss_samples, c._lower_floor_loss_samples = 60, 40
    await c._async_save_thermal_learning()
    disk = _fr_disk("fr_no_unload")

    async def _refuse(eid):
        hass.config_entries.unloaded.append(eid)
        return False

    hass.config_entries.async_unload = _refuse
    import logging as _fr_logging
    from heatpump_optimizer import coordinator as _fr_coord_mod

    said = []
    handler = _fr_logging.Handler()
    handler.emit = lambda record: said.append(record.getMessage())
    _fr_coord_mod._LOGGER.addHandler(handler)
    try:
        done = await _fr_reset(c, scope)
    finally:
        _fr_coord_mod._LOGGER.removeHandler(handler)
    after = {k: v for k, v in _fr_disk("fr_no_unload").items() if k != "snapshots"}
    return entry, hass.config_entries, (disk, after), c, (done, said)


_fr_nu_entry, _fr_nu_mgr, _fr_nu_disk, _fr_nu_c, (_fr_nu_done, _fr_nu_said) = _aio.run(_fr_failed_unload())
R.check(
    "a refused unload changes nothing but the undo point: settings, every store and the heat-loss pair as before",
    _fr_nu_done is False
    and {**_fr_nu_entry.data, **_fr_nu_entry.options} == {**_FR_DATA, **_FR_OPTS}
    and _fr_nu_mgr.set_up == []
    and all(_fr_unstamped(_fr_nu_disk[1].get(k)) == _fr_unstamped(v) for k, v in _fr_nu_disk[0].items() if k != "snapshots")
    and _li_state_of(_fr_nu_c) == (1.4, 1.3, 60, 40)
    and "before_reset" in _fr_nu_c._snapshot_ring.snapshots[-1]
    and any("not applied" in m for m in _fr_nu_said) and not any(" applied;" in m for m in _fr_nu_said),
    f"done {_fr_nu_done}, said {_fr_nu_said}, set up {_fr_nu_mgr.set_up}, heat loss {_li_state_of(_fr_nu_c)}, "
    f"stores moved {sorted(k for k, v in _fr_nu_disk[0].items() if k != 'snapshots' and _fr_unstamped(_fr_nu_disk[1].get(k)) != _fr_unstamped(v))}",
)
_fr_nu_c.hass.config_entries.async_unload = _fr_nu_mgr.async_unload
_fr_nu_undo = _aio.run(_fr_nu_c.async_restore_learned_snapshot())
R.check(
    "a refused unload refuses the undo too, and the undo point stays the undo point",
    _fr_nu_undo is False and "before_reset" in _fr_nu_c._snapshot_ring.snapshots[-1]
    and _fr_nu_mgr.set_up == [],
    f"undo {_fr_nu_undo}",
)
# Once a weekly snapshot is newer, the restore is the ordinary one again.
_fr_w_before, _fr_w_entry, _, _ = _fr_case("learners", "fr_weekly")
_fr_w_ring = _fr_w_entry.runtime_data._snapshot_ring
_fr_w_ring.take(_fr_dt.now(), _fr_w_entry.runtime_data._learner_snapshot_payloads(), {}, True)
R.check(
    "a weekly snapshot newer than the undo point takes the restore back from it",
    _fr_w_ring.undo_target() is _fr_w_ring.snapshots[-1] and "before_reset" not in _fr_w_ring.snapshots[-1]
    and "before_reset" in _fr_w_ring.snapshots[-2],
)


async def _fr_flow_case(user_input, entry_id, *, loaded=True):
    hass = FakeHass({})
    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id=entry_id)
    hass.config_entries.entries.append(entry)
    if loaded:
        await _fr_boot(hass, entry)
    flow = _fr_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = hass
    disk = _fr_disk(entry_id)
    config = ({**entry.data}, {**entry.options})
    first = await flow.async_step_factory_reset()
    second = await flow.async_step_factory_reset(user_input) if user_input is not None else None
    changed = (_fr_disk(entry_id) != disk, ({**entry.data}, {**entry.options}) != config)
    return first, second, changed, hass.config_entries


_fr_cancel = _aio.run(_fr_flow_case({"scope": "both", "confirm": False}, "fr_flow_cancel"))
R.check(
    "the options step shows the scope and the confirmation; unconfirmed, nothing changes (null control)",
    _fr_cancel[0]["type"] == "form" and _fr_cancel[0]["step_id"] == "factory_reset"
    and set(map(str, _fr_cancel[0]["data_schema"].schema)) == {"scope", "confirm"}
    and _fr_cancel[1]["type"] == "menu" and _fr_cancel[1]["step_id"] == "advanced"
    and _fr_cancel[2] == (False, False) and _fr_cancel[3].unloaded == [] and _fr_cancel[3].set_up == [],
    f"{_fr_cancel[1]}, changed {_fr_cancel[2]}",
)
_fr_go = _aio.run(_fr_flow_case({"scope": "both", "confirm": True}, "fr_flow_go"))
R.check(
    "confirmed, the options step resets, sets the entry up again and closes",
    _fr_go[1]["type"] == "abort" and _fr_go[1]["reason"] == "factory_reset_done"
    and _fr_go[2] == (True, True) and _fr_go[3].unloaded == ["fr_flow_go"] == _fr_go[3].set_up,
    f"{_fr_go[1]}, changed {_fr_go[2]}",
)


async def _fr_flow_refused():
    hass = FakeHass({})
    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id="fr_flow_refused")
    hass.config_entries.entries.append(entry)
    await _fr_boot(hass, entry)

    async def _refuse(eid):
        return False

    hass.config_entries.async_unload = _refuse
    flow = _fr_flow.HeatPumpOptimizerOptionsFlow(entry)
    flow.hass = hass
    await flow.async_step_factory_reset()
    shown = await flow.async_step_factory_reset({"scope": "both", "confirm": True})
    try:
        await _fr_services.handle_factory_reset(hass, _fr_call(
            "heatpump_optimizer", "factory_reset",
            _fr_services.SERVICE_SCHEMA_FACTORY_RESET({"entry_id": "fr_flow_refused", "scope": "learners"})))
        raised = None
    except Exception as err:  # HomeAssistantError
        raised = err
    return shown, raised


_fr_refused = _aio.run(_fr_flow_refused())
R.check(
    "a refused unload is said as not applied, by the options step and by the service, never as done",
    _fr_refused[0]["type"] == "abort" and _fr_refused[0]["reason"] == "factory_reset_not_applied"
    and getattr(_fr_refused[1], "translation_key", None) == "factory_reset_not_applied"
    and all(_fi_json.loads(_FrPath(p).read_text())["options"]["abort"].get("factory_reset_not_applied")
            and _fi_json.loads(_FrPath(p).read_text())["exceptions"]["factory_reset_not_applied"]["message"]
            for p in ("custom_components/heatpump_optimizer/strings.json",
                      "custom_components/heatpump_optimizer/translations/en.json",
                      "custom_components/heatpump_optimizer/translations/sv.json")),
    f"{_fr_refused[0]}, raised {_fr_refused[1]!r}",
)
_fr_off = _aio.run(_fr_flow_case({"scope": "both", "confirm": True}, "fr_flow_off", loaded=False))
R.check(
    "an entry that is not running is not reset, confirmed or not",
    _fr_off[1]["type"] == "abort" and _fr_off[1]["reason"] == "factory_reset_not_loaded"
    and _fr_off[2] == (False, False) and _fr_off[3].unloaded == [],
    f"{_fr_off[1]}, changed {_fr_off[2]}",
)
R.check(
    "the advanced menu offers the reset, labelled by the translations",
    "factory_reset" in _fr_flow.HeatPumpOptimizerOptionsFlow._ADVANCED_MENU
    and all(_fi_json.loads(_FrPath(p).read_text())["options"]["step"]["advanced"]["menu_options"].get("factory_reset")
            for p in ("custom_components/heatpump_optimizer/strings.json",
                      "custom_components/heatpump_optimizer/translations/en.json",
                      "custom_components/heatpump_optimizer/translations/sv.json")),
)

_fr_svc_refused = []
for _fr_bad in ({"scope": "both"}, {"entry_id": "x", "scope": "everything"}, {"entry_id": "x"}):
    try:
        _fr_services.SERVICE_SCHEMA_FACTORY_RESET(_fr_bad)
    except Exception:  # vol.Invalid
        _fr_svc_refused.append(sorted(_fr_bad))


async def _fr_service():
    hass = FakeHass({})
    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id="fr_svc")
    hass.config_entries.entries.append(entry)
    await _fr_boot(hass, entry)
    answer = await _fr_services.handle_factory_reset(hass, _fr_call(
        "heatpump_optimizer", "factory_reset",
        _fr_services.SERVICE_SCHEMA_FACTORY_RESET({"entry_id": "fr_svc", "scope": "settings"})))
    return answer, hass.config_entries, {**entry.data, **entry.options}


_fr_svc = _aio.run(_fr_service())
R.check(
    "the service needs an entry and a known scope, and resets that entry",
    len(_fr_svc_refused) == 3 and _fr_svc[0] == {"reset": "fr_svc", "scope": "settings"}
    and _fr_svc[1].unloaded == ["fr_svc"] and set(_fr_svc[2]) <= set(_fr_ec.FACTORY_KEPT),
    f"refused {_fr_svc_refused}, answer {_fr_svc[0]}",
)

# The store enumeration: every store the integration persists, by the AST walk
# finite_boundary.py's arm 1 uses, each with its disposition.
_FR_STORES = {
    "thermal_learning": "voided: learned keys dropped, the heat-loss pair by its void path",
    "accuracy": "voided: accuracy, dhw_accuracy, defrost, comfort; peaks and mode are facts",
    "price_model": "voided",
    "dhw_profile": "voided",
    "dhw_draws": "voided",
    "snapshots": "kept: the undo point lives here",
    "ledger": "kept: billed energy",
    "energy": "kept: metered totals",
    "manual_plan": "kept: the user's own override",
    "away": "kept: the user's own override",
    "boost": "kept: the user's own override",
    "dhw_legionella": "kept: the last disinfection, a safety fact",
    "notifier": "kept: which notices were sent",
    "pump_duty": "kept: what was last written to the pump",
    "debug": "kept: a diagnostics collection",
}
_fr_found = set()
for _fr_p in sorted(_FrPath("custom_components/heatpump_optimizer").glob("*.py")):
    for _fr_n in _fr_ast.walk(_fr_ast.parse(_fr_p.read_text())):
        if (isinstance(_fr_n, _fr_ast.Call) and isinstance(_fr_n.func, _fr_ast.Name)
                and _fr_n.func.id == "QuarantiningStore"):
            for _fr_arg in _fr_n.args:
                if isinstance(_fr_arg, _fr_ast.JoinedStr):
                    _fr_found.add(_fr_arg.values[-1].value.lstrip("_"))
R.check(
    "every store the integration persists has a factory-reset disposition",
    _fr_found == set(_FR_STORES) and len(_fr_found) >= 15,
    f"undispositioned {sorted(_fr_found - set(_FR_STORES))}, stale {sorted(set(_FR_STORES) - _fr_found)}",
)



# --- reviewer probe (not the PR's): state learned in memory after the last save ---
R.section("U6 probe: unsaved in-memory state at the moment of the reset")
def _u6_case(scope, eid):
    hass = FakeHass({})
    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id=eid)
    hass.config_entries.entries.append(entry)
    c = _aio.run(_fr_boot(hass, entry))
    _fr_learn(c)
    c._apply_cop_scale(1.21)          # learned after the last save
    c._freq_fallback = True           # already True and saved by _fr_learn; flip a fact instead:
    c._snow_accum_cm = 7.5            # a fact the reset keeps, changed since the last save
    before = _fr_learned(c)
    async def _setup(eid2):
        hass.config_entries.set_up.append(eid2); await _fr_boot(hass, entry); return True
    hass.config_entries.async_setup = _setup
    _aio.run(_fr_reset(c, scope))
    return before, entry
_u6_b, _u6_e = _u6_case("learners", "u6_l")
R.check("a learners reset keeps a fact changed since the last save (snow memory)",
        _u6_e.runtime_data._snow_accum_cm == 7.5, f"snow {_u6_e.runtime_data._snow_accum_cm}")
_u6_b2, _u6_e2 = _u6_case("both", "u6_b")
_u6_new = _u6_e2.runtime_data; _fr_counting_refresh(_u6_new)
_aio.run(_u6_new.async_restore_learned_snapshot())
R.check("the undo brings back a learner learned since the last save (COP scale 1.21)",
        abs(_u6_e2.runtime_data._cop_scale - 1.21) < 1e-9, f"cop {_u6_e2.runtime_data._cop_scale}")
sys.exit(R.close("FR CHECKS"))
