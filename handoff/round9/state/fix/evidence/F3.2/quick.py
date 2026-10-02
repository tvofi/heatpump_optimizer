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

from harness import FakeHass, FakeState, Results, UTC, minutes_ago

import numpy as np

from heatpump_optimizer import away as away_mode
from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer import battery as battery_view
from heatpump_optimizer import presets, pv
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
from heatpump_optimizer.defrost import (
    DEFROST_LOSS_MULTIPLIER,
    DERATE_CONFIDENCE_SAMPLES,
    DERATE_MAX,
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
    PHASE_ARMED,
    PHASE_DONE,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.tariff import (
    CapacityTariff,
    PeakTracker,
    _smooth_topk_sum,
    peak_cost,
    peak_cost_smooth,
    realised_peak,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState

R = Results("Feature modules")

import asyncio as _asyncio

from harness import FakeEntry as _FakeEntry, FakeHass as _FakeHass
from heatpump_optimizer.coordinator import (
    HeatPumpOptimizerCoordinator as _Coord,
)
from homeassistant.util import dt as dt_util
_METER = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("-5.0", unit="°C"),
    "sensor.house_power": FakeState("6500", unit="W"),
    "sensor.hp_power": FakeState("2000", unit="W"),
}


def _t2_coord(states=None, **extra):
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        **extra,
    }
    return _Coord(_FakeHass(dict(_METER, **(states or {}))), _FakeEntry(data=cfg))

R.section("pump-duty arbiter — mode and set-points per plan step, held while the optimizer is active")

import asyncio as _pa_aio  # noqa: E402
from types import SimpleNamespace as _PaNS  # noqa: E402

from heatpump_optimizer import pump_arbiter as _pa  # noqa: E402
from heatpump_optimizer.const import MODE_AUTO as _PA_AUTO, MODE_OFF as _PA_OFF  # noqa: E402

_PA_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
_PA_TUYA = ("Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW")
_PA_MODBUS = ("Off", "Cool + DHW", "Heat + DHW")


def _pa_result(duties):
    """A plan of 15-min steps from ``duties`` ('s', 'd', 'b', '-')."""
    return _PaNS(
        timestamps=[_PA_T0 + timedelta(minutes=15 * i) for i in range(len(duties))],
        power_schedule=[1.5 if c in "sb" else 0.15 if c == "x" else 0.0 for c in duties],
        dhw_power_schedule=[2.0 if c in "dbx" else 0.0 for c in duties],
        optimal_setpoints=[21.0 for _ in duties],
    )


_PA_IDS = __import__("itertools").count()


class _PaCoord:
    def __init__(self, options, duties="dds-", flow=True, duty="control"):
        self.hass = FakeHass({
            "select.pump_mode": FakeState("Heating + DHW", attributes={"options": list(options)}),
            "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
            "number.water_set": FakeState("53", attributes={"min": 25, "max": 63}),
        })
        self._config = {
            "pump_duty_mode": duty,
            "heat_pump_mode_entity": "select.pump_mode",
            "dhw_setpoint_entity": "number.dhw_set",
            "space_setpoint_entity": "number.water_set",
            "space_setpoint_unit": "flow" if flow else "indoor",
        }
        self._mode = _PA_AUTO
        self.stale = False
        self._current_action = {"mode": "eco"}
        self._optimization_result = _pa_result(duties)
        self._thermal_model = _PaNS(
            params=_PaNS(min_electrical_power=0.4), curve_flow_temp=lambda _o: 34.2
        )
        self._thermal_params = _PaNS(dhw_setpoint=48.0)
        self._current_state = _PaNS(outdoor_temperature=2.0)
        # One store key per coordinator: the storage stub outlives FakeHass.
        self.entry = _PaNS(entry_id=f"pa{next(_PA_IDS)}")
        self.set_modes = []

    def _plan_is_stale(self):
        return self.stale

    async def async_set_mode(self, mode):
        self.set_modes.append(mode)
        self._mode = mode

    def device(self, entity, value):
        self.hass.states.get(entity).state = value

    def writes(self):
        return [(d, sv, (data or {}).get("option", (data or {}).get("value")))
                for d, sv, data in self.hass.services.calls]


def _pa_run(coord, minutes):
    _pa_aio.run(_pa.apply(coord, _PA_T0 + timedelta(minutes=minutes)))


def _pa_own(coord, signals):
    held = _pa.own(coord, signals)
    return _pa_aio.run(held) if _pa_aio.iscoroutine(held) else held


# The lock-in (P2): the arbiter's own DHW-only write must not reach the next
R.section("P1/P2 — a stored instant loads aware, or not at all (D1-s1-01, D1-s3-01, D1-s1-02, D1-s3-05)")
# Round 9 (#1644 P2, #1647 P1, #1660 N-future-instant). Every loader below
# parsed a persisted instant with fromisoformat and handed a naive one to a
# consumer that diffs it against Home Assistant's always-aware now, which
# raised on every cycle until something rewrote the leaf. One rule now loads
# it: drift.stored_instant. The future bound is the store boundary's, pinned
# by tests/finite_boundary.py's instant arm, not here.
import asyncio as _si_aio  # noqa: E402
import json as _si_json  # noqa: E402
from zoneinfo import ZoneInfo as _SiZone  # noqa: E402

from heatpump_optimizer import drift as _si_drift  # noqa: E402
from heatpump_optimizer import pump_arbiter as _si_pa  # noqa: E402
from heatpump_optimizer.curve_learning import CurveLearner as _SiCurve  # noqa: E402
from heatpump_optimizer.snapshots import SnapshotRing as _SiRing  # noqa: E402
from homeassistant.helpers import storage as _si_storage  # noqa: E402

_SI_NOW = datetime(2026, 6, 20, 12, 0, tzinfo=UTC)
_SI_NAIVE = "2026-06-01T12:00:00"


def _si_raises(fn) -> str | None:
    try:
        fn()
    except Exception as err:  # noqa: BLE001
        return type(err).__name__
    return None

R.section("P1/P2 — the pump-duty arbiter's record, unload and mode route, and the frequency map (D1-s3-02, D1-s3-03, D12-s2-02, D1-s3-06)")
# Round 9 F3.2 (#1644 P2, #1647 P1, #1660 N-future-instant). What the arbiter
# restores is a record it could have written; an apply queued before an
# unload arms and writes nothing; the mode is written through the target's
# own domain; the frequency map loads only the domain its update path folds;
# and the store bounds a naive stamp in the zone its loader reads it in.
from heatpump_optimizer import freq_control as _f32_fc  # noqa: E402
from heatpump_optimizer.store import QuarantiningStore as _F32Store  # noqa: E402

_F32_T0 = datetime(2026, 6, 1, 12, 0, tzinfo=UTC)


def _f32_load(coord, written):
    """``written`` stored as the arbiter's record, then its real loader."""
    _si_storage._DISK[f"heatpump_optimizer_{coord.entry.entry_id}_pump_duty"] = (
        _si_json.dumps({"written": written}))
    _si_pa.state_for(coord).loaded = False
    try:
        _si_aio.run(_si_pa._load(coord))
    finally:
        _si_storage._DISK.clear()
    return _si_pa.state_for(coord).written


# D1-s3-02: an apply queued by a state change before the unload runs after
# it. It must neither re-arm the tick and the state listener nor write.
# Under an aware clock, as Home Assistant's: release() stamps its baseline
# write with the clock, and the stub's default one is naive (D1-s1-52).
_f32_live = {}
dt_util.freeze(_PA_T0 + timedelta(minutes=10))
try:
    for _f32_arm in ("released", "null"):
        _f32_c = _PaCoord(_PA_TUYA)
        _f32_c._entry_released = False
        _pa_run(_f32_c, 1)
        _f32_c._entry_released = _f32_arm == "released"
        _pa_aio.run(_pa.release(_f32_c))
        _f32_c.hass.services.calls.clear()
        _pa_run(_f32_c, 16)
        _f32_live[_f32_arm] = (len(_pa.state_for(_f32_c).unsubs), len(_f32_c.writes()))
finally:
    dt_util.freeze(None)
R.check(
    "an apply queued before the unload arms no listener and writes nothing "
    "after it (D1-s3-02); a live coordinator re-arms both (null control)",
    _f32_live["released"] == (0, 0) and _f32_live["null"][0] == 2,
    f"{_f32_live}",
)

# D1-s3-03: a record of any other shape is not restored, and the next pass
# neither raises nor keeps it; an honest record still loads.
_f32_iso = "2026-06-01T11:59:00+00:00"
_f32_bad = {
    "written-list": [["heat", _f32_iso]],
    "setpoint-str": {"dhw_setpoint": ["53", _f32_iso]},
    "setpoint-list": {"space_setpoint": [[34.0], _f32_iso]},
    "setpoint-bool": {"dhw_setpoint": [True, _f32_iso]},
    "mode-dict": {"mode": [{"v": "heat"}, _f32_iso]},
    "mode-list": {"mode": [["heat"], _f32_iso]},
    "slot-unknown": {"boiler": [48.0, _f32_iso]},
    "pair-dict": {"mode": {"0": "heat", "1": _f32_iso}},
}
_f32_raised = {}
dt_util.freeze(_F32_T0)
try:
    for _f32_name, _f32_rec in _f32_bad.items():
        _f32_c = _PaCoord(_PA_TUYA)
        try:
            _f32_kept = dict(_f32_load(_f32_c, _f32_rec))
            _pa_run(_f32_c, 1)
            _pa_run(_f32_c, 2)
            _f32_raised[_f32_name] = _f32_kept or None
        except Exception as _f32_err:  # noqa: BLE001
            _f32_raised[_f32_name] = type(_f32_err).__name__
    _f32_ok = dict(_f32_load(_PaCoord(_PA_TUYA), {
        "mode": ["heat", _f32_iso], "dhw_setpoint": [48.0, _f32_iso],
        "space_setpoint": [34, _f32_iso]}))
finally:
    dt_util.freeze(None)
R.check(
    "the arbiter restores only a record it could have written: no malformed "
    "record loads or raises on the next pass (D1-s3-03)",
    not any(_f32_raised.values()),
    f"{_f32_raised}",
)
R.check(
    "an honest arbiter record still loads, every slot (null control)",
    sorted(_f32_ok) == ["dhw_setpoint", "mode", "space_setpoint"]
    and _f32_ok["dhw_setpoint"][0] == 48.0,
    f"{_f32_ok}",
)

# FI-sw5: a write instant stored ahead of the clock (N-future-instant) is
# bounded by the store at load, so hold()'s write-echo grace is not held
# open by it: a differing reading past the grace is rewritten.
_f32_grace = {}
dt_util.freeze(_F32_T0)
try:
    for _f32_arm, _f32_at in (("ahead", _F32_T0 + timedelta(days=400)),
                              ("null", _F32_T0)):
        _f32_c = _PaCoord(_PA_TUYA)
        _f32_load(_f32_c, {"dhw_setpoint": [48.0, _f32_at.isoformat()]})
        _pa.hold(_f32_c, _F32_T0 + timedelta(seconds=30 if _f32_arm == "ahead" else 10))
        _f32_grace[_f32_arm] = "dhw_setpoint" in _pa.state_for(_f32_c).written
finally:
    dt_util.freeze(None)
R.check(
    "a write instant stored ahead of the clock is bounded, so the echo grace "
    "closes on time (FI-sw5); an honest one inside the grace still holds (null control)",
    _f32_grace == {"ahead": False, "null": True},
    f"record kept after a differing reading: {_f32_grace}",
)

# D12-s2-02: the mode slot accepts select, input_select and sensor. The
# write goes through the target's own domain; a sensor is read, never written.
_f32_route = {}
for _f32_dom in ("select", "input_select", "sensor"):
    _f32_c = _PaCoord(_PA_TUYA)
    _f32_ent = f"{_f32_dom}.pump_mode"
    _f32_c._config["heat_pump_mode_entity"] = _f32_ent
    _f32_c.hass.states._states[_f32_ent] = FakeState(
        "Heating + DHW", attributes={"options": list(_PA_TUYA)})
    _pa_run(_f32_c, 1)
    _f32_route[_f32_dom] = sorted(
        {(d, s) for d, s, data in _f32_c.hass.services.calls
         if (data or {}).get("entity_id") == _f32_ent})
R.check(
    "the arbiter writes the mode through the target's own domain, and never "
    "writes a read-only sensor slot (D12-s2-02)",
    _f32_route == {"select": [("select", "select_option")],
                   "input_select": [("input_select", "select_option")],
                   "sensor": []},
    f"{_f32_route}",
)

# The store bounds a naive instant in the zone its loader reads it in: Home
# Assistant's, for the arbiter, legionella and boost. Read as UTC, a zone
# west of Greenwich let a naive future stamp through by its offset, and one
# east of it pulled an honest stamp back by its offset (a boost with an hour
# left came back ended).
_f32_zone = {}
_f32_zone0 = dt_util.DEFAULT_TIME_ZONE
for _f32_tz in ("Europe/Stockholm", "America/Los_Angeles"):
    _f32_z = _SiZone(_f32_tz)
    _f32_now = datetime(2026, 6, 1, 12, 0, tzinfo=_f32_z)
    dt_util.DEFAULT_TIME_ZONE = _f32_z
    dt_util.freeze(_f32_now)
    try:
        _f32_c = _t2_coord()
        _f32_w = _f32_load(_f32_c, {
            "mode": ["heat", "2026-06-01T11:00:00"],
            "dhw_setpoint": [48.0, "2026-06-01T18:00:00"]})
        _si_storage._DISK[_f32_c._legionella.store._key] = _si_json.dumps(
            {"last_cycle": "2026-06-01T11:00:00", "last_attempt": "2026-06-01T18:00:00"})
        _si_aio.run(_f32_c._legionella.async_load())
        _si_storage._DISK[f"heatpump_optimizer_{_f32_c.entry.entry_id}_boost"] = (
            _si_json.dumps({"space": {"until": "2026-06-01T13:00:00"},
                            "dhw": {"until": "2026-06-01T18:00:00"}}))
        _si_aio.run(boost_mod.restore(_f32_c))
        _f32_b = boost_mod.held_for(_f32_c).until
        _f32_zone[_f32_tz] = (
            _f32_w["mode"][1] == _f32_now - timedelta(hours=1)
            and _f32_w["dhw_setpoint"][1] == _f32_now
            and _f32_c._legionella.last_cycle == _f32_now - timedelta(hours=1)
            and _f32_c._legionella.attempt == _f32_now
            and _f32_b.get("space") == _f32_now + timedelta(hours=1)
            and _f32_b.get("dhw") == _f32_now + timedelta(hours=boost_mod.BOOST_HOURS),
            _f32_w["mode"][1].isoformat(), _f32_w["dhw_setpoint"][1].isoformat(),
            {k: v.isoformat() for k, v in _f32_b.items()})
    finally:
        dt_util.DEFAULT_TIME_ZONE = _f32_zone0
        dt_util.freeze(None)
        _si_storage._DISK.clear()
R.check(
    "the store bounds a naive stored instant in its loader's zone: an honest "
    "one is kept and one beyond the lead lands on it, in Stockholm and Los Angeles",
    all(v[0] for v in _f32_zone.values()) and len(_f32_zone) == 2,
    f"{_f32_zone}",
)

# The bound's target is now plus the store's lead, exactly: an instant
# beyond it lands on it, not merely somewhere at or before it.
_f32_lead = timedelta(hours=2)
_F32Key = "heatpump_optimizer_f32_lead"
_si_storage._DISK[_F32Key] = _si_json.dumps({
    "aware": (_F32_T0 + timedelta(days=400)).astimezone(_SiZone("Europe/Stockholm")).isoformat(),
    "naive": (_F32_T0 + timedelta(days=400)).replace(tzinfo=None).isoformat(),
    "inside": (_F32_T0 + _f32_lead - timedelta(minutes=1)).isoformat()})
dt_util.freeze(_F32_T0)
try:
    _f32_got = _si_aio.run(_F32Store(FakeHass({}), 1, _F32Key, lead=_f32_lead).async_load())
finally:
    dt_util.freeze(None)
    _si_storage._DISK.clear()
R.check(
    "an instant beyond the store's lead is bounded to exactly now plus the "
    "lead, aware or naive, and one inside it is kept",
    datetime.fromisoformat(_f32_got["aware"]) == _F32_T0 + _f32_lead
    and datetime.fromisoformat(_f32_got["aware"]).utcoffset() == timedelta(hours=2)
    and _f32_got["naive"] == (_F32_T0 + _f32_lead).replace(tzinfo=None).isoformat()
    and _f32_got["inside"] == (_F32_T0 + _f32_lead - timedelta(minutes=1)).isoformat(),
    f"{_f32_got}",
)

# D1-s3-06: a stored bucket outside the domain observe() can fold -- a decile
# index outside [0, FREQ_DECILES), a ratio above FREQ_MAX_KW_PER_HZ -- does
# not load, so no phantom bucket pins recommend() at the range's floor.
_f32_map = _f32_fc.FrequencyMap.from_dict({
    "-1": [5.0, 50], "10": [0.04, 50], "3": [1e6, 50], "2": [50.0, 50],
    "4": [0.04, 50], "5": [_f32_fc.FREQ_MAX_KW_PER_HZ, 50],
})
_f32_obs = _f32_fc.FrequencyMap()
_f32_obs.observe(2.0, 6.0, 1.0, 120.0)
_f32_obs.observe(60.0, 2.4, 20.0, 120.0)
R.check(
    "the frequency map loads only a decile in [0, FREQ_DECILES) and a ratio "
    "up to FREQ_MAX_KW_PER_HZ, the domain observe() folds (D1-s3-06)",
    sorted(_f32_map.buckets) == [4, 5]
    and _f32_map.recommend(3.0, 20.0, 120.0) == 75.0
    and list(_f32_obs.buckets) == [4],
    f"loaded={_f32_map.buckets} observed={_f32_obs.buckets}",
)

sys.exit(R.close("QUICK"))
