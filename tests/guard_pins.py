#!/usr/bin/env python3
"""Pins #805 survivors that do not live in coordinator.py.

The judge-corrected sample left ten consequential mutants. #806 and #807
already kill the two sensor None-returns and the NaN price-shape admission.
#877 pinned the four that need neither coordinator.py nor optimizer.py.
These two are the optimizer residuals: the legionella run-up break (M04)
and the pinned-guess lower clamp (M11). The coordinator residual stays.

    PYTHONPATH=tests/hastub python3 tests/guard_pins.py
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest import mock

import asyncio
import logging
import math
import sys
import warnings
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import heatpump_optimizer.legionella as legionella_mod
from harness import FakeEntry, FakeHass, FakeState, Results, UTC
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.optimizer import _Horizon
from heatpump_optimizer.thermal_model import ThermalState
from heatpump_optimizer.disinfection import DisinfectionSwitch
from heatpump_optimizer.legionella import LegionellaGuard
from heatpump_optimizer.dhw_planner import DhwPlanner
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.price_model import PriceShapeModel
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
from heatpump_optimizer import arbiter_record, topology
from heatpump_optimizer import grid_fee as grid_fee_mod
from heatpump_optimizer import price_model as price_model_mod
from heatpump_optimizer import tariff as tariff_mod
from heatpump_optimizer.wood_fuel import wood_slots_to_kw
from homeassistant.util import dt as dt_util


def _owned_params(params):
    """A test owner of ``params``, as the coordinator's ``_publish_params`` owns
    its own: the learner reads through ``params`` and publishes a new snapshot."""
    from dataclasses import replace as _replace
    box = [params]

    def publish(**fields):
        box[0] = _replace(box[0], **fields)

    return {"params": lambda: box[0], "publish": publish}


class _Learner(DhwProfileLearner):
    """The learner, with persistence stubbed so a cooling fold is visible."""

    def __init__(self) -> None:
        super().__init__(
            FakeHass(),
            "guard-pins",
            **_owned_params(ThermalParameters()),
            frozen=lambda *_, **_kw: None,
            heating_active=lambda: False,
            external_heat_active=lambda: False,
        )

    async def async_save_profile(self) -> None:
        return None


def _idle_cooling_learned() -> bool:
    # Aware, as the dt_util.now() production stores as the previous sample
    # time: a naive one is read as UTC against a clock in the configured
    # zone, and under Asia/Tokyo the interval came out negative.
    now = datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
    dt_util.freeze(now)
    try:
        learner = _Learner()
        learner.last_temp_sample = 55.0
        learner.last_sample_time = now - timedelta(hours=1)
        learner.heating_since_sample = False
        before = learner.cooling_samples
        asyncio.run(learner.async_learn_dynamics(53.0))
        return learner.cooling_samples > before
    finally:
        dt_util.freeze(None)


def _coil_caption_present() -> bool:
    setup = topology.describe_setup(
        {
            "upper_floor_thermal_mass": 2.0,
            "mixing_valve_mode": "manual",
            "wood_tank_top_entity": "sensor.wood_top",
            "dhw_tank_volume": 200.0,
            "dhw_wood_coil_enabled": True,
        }
    )
    return "refilled through a coil in the wood tank" in topology.render_text_summary(
        setup
    )


def _aware_slot_on_naive_stamps() -> bool:
    stamps = [datetime(2026, 1, 1, hour) for hour in range(4)]
    start = datetime(2026, 1, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 3, tzinfo=timezone.utc)
    try:
        kw = wood_slots_to_kw(
            [{"start": start.isoformat(), "end": end.isoformat(), "liters": 50.0}],
            stamps,
            1.0,
            "birch",
            "packed",
            75.0,
        )
    except TypeError:
        return False
    return kw[0] == 0.0 and kw[1] > 0.0 and kw[2] > 0.0 and kw[3] == 0.0


def _spike_rail_holds() -> bool:
    """A 10-to-1 day is a data-error spike; the rail must flatten it.

    After the profile is re-normalised to mean 1, a rail of 3 leaves the
    peak/floor near 4; doubling the rail leaves it near 8. Five sits
    between those and does not name the constant.
    """
    model = PriceShapeModel()
    if not model.observe_day(datetime(2026, 1, 5), [1.0] * 23 + [10.0]):
        return False
    peak, floor = max(model.shapes[0]), min(model.shapes[0])
    return floor > 0.0 and peak / floor < 5.0


def _runup_stops_at_the_ordinary_floor() -> bool:
    """M04: ``if need <= floor_temps[m]: break`` must fire.

    A high ordinary floor is already the heat the plan owes. Continuing
    the walk writes earlier run-up floors below that, including negatives.
    """
    params = ThermalParameters()
    opt = HeatPumpOptimizer(
        ThermalModel(params),
        OptimizationConfig(
            horizon_hours=6,
            time_step_minutes=60,
            target_temp=21.0,
            min_temp=18.0,
            max_temp=24.0,
        ),
    )
    n_steps = 12
    floor_temps = np.full(n_steps, 50.0)
    plan = DhwPlanner(opt.model, opt.config)._dhw_legionella_ceilings(
        _Horizon(
            initial_state=ThermalState(room_temperature=21.0),
            prices=np.zeros(n_steps), outdoor_temps=np.zeros(n_steps),
            wind_speeds=np.zeros(n_steps), precipitation=np.zeros(n_steps),
            solar_radiation=np.zeros(n_steps), start_time=None,
            n_steps=n_steps, dt=1.0, comfort_targets=np.full(n_steps, 21.0),
            temp_min_bounds=np.full(n_steps, 17.0),
            temp_max_bounds=np.full(n_steps, 23.0),
            step_hours=np.arange(n_steps) * 1.0,
            solar_gains=np.zeros(n_steps),
            heat_loss_factors=np.ones(n_steps), forecast={}, t_start=0.0,
        ),
        params=params,
        draw_rates=np.zeros(n_steps),
        floor_temps=floor_temps,
        p_dhw_run=3.0,
        legionella_due=True,
        legionella_hour=11.0,
        legionella_step=10,
    )
    at_or_below = [
        i
        for i, value in enumerate(plan.runup_temps)
        if value != 0.0 and value <= float(floor_temps[i])
    ]
    return len(at_or_below) == 1


def _space_scope_caps_pins() -> dict[str, bool]:
    """R11-OUTSIDE-HONEST-STARTS-RUNS: ``_space_scope`` bounds space heating by
    the horizon's space caps, and by a total cap less the hot water beside it.

    Each guard is driven with its cap set and the other unset; the uncapped
    scope is the null control, the plain ``p_max - dhw`` headroom.
    """
    from heatpump_optimizer.optimizer import _space_scope

    n = 4
    opt = HeatPumpOptimizer(
        ThermalModel(ThermalParameters()),
        OptimizationConfig(
            horizon_hours=n, time_step_minutes=60, target_temp=21.0,
            min_temp=18.0, max_temp=24.0,
        ),
    )
    p_max = opt.model.params.max_electrical_power
    dhw = np.array([0.0, 1.0, 0.0, 0.0])
    cap = np.array([p_max, 2.0, 0.5, p_max + 4.0])
    zero = np.zeros(n)

    def headroom(caps, extra) -> list[float]:
        h = _Horizon(
            initial_state=ThermalState(room_temperature=21.0),
            prices=zero, outdoor_temps=zero, wind_speeds=zero,
            precipitation=zero, solar_radiation=zero, start_time=None,
            n_steps=n, dt=1.0, comfort_targets=np.full(n, 21.0),
            temp_min_bounds=np.full(n, 17.0), temp_max_bounds=np.full(n, 23.0),
            step_hours=np.arange(n) * 1.0, solar_gains=zero,
            heat_loss_factors=np.ones(n), forecast={}, t_start=0.0,
            power_caps=caps, power_caps_extra=extra,
        )
        got, scope = _space_scope(
            opt, h, None, dhw, p_max, lambda *a, **k: 0.0, lambda *a, **k: zero)
        return got.tolist() if [b[1] for b in scope[0]] == got.tolist() else []

    plain = (p_max - dhw).tolist()
    return {
        "uncapped headroom is p_max less the hot water (null control)":
            headroom(None, None) == plain,
        "a space cap bounds the scope's headroom":
            headroom(cap, None) == np.minimum(plain, cap).tolist(),
        "a total cap bounds it less the hot water beside it":
            headroom(None, cap) == np.minimum(plain, cap - dhw).tolist(),
    }


def _pinned_guess_respects_the_lower_bound() -> bool:
    """M11: ``min(max(out[i], low), high)`` must keep a warm start above low."""
    out = HeatPumpOptimizer._seed_pinned_guess(
        np.array([0.0, 10.0]),
        [(1.5, 4.0), (1.5, 4.0)],
    )
    return bool(out[0] == 1.5 and out[1] == 4.0)


def _draw_folded_only_without_external_heat() -> bool:
    """D3-s3-04: a positive draw is folded, except while external heat runs.

    ``async_fold_draw_stats`` skips an interval outright while external heat
    (a wood burn) drives the tank, and otherwise folds the energy beyond
    standby into the open occurrence. Both arms are pinned: forcing the
    ``_external_heat_active()`` guard off folds the wood-driven drop, and
    forcing it on folds nothing ever -- and no gate check saw either.
    """
    folded = []
    for external in (True, False):
        params = ThermalParameters()
        params.dhw_enabled = True
        learner = DhwProfileLearner(
            FakeHass(),
            "guard-pins-draws",
            **_owned_params(params),
            frozen=lambda *_, **_kw: None,
            heating_active=lambda: False,
            external_heat_active=lambda external=external: external,
        )

        async def _no_save() -> None:
            return None

        learner.async_save_draws = _no_save
        learner.cooling_rate = 0.3
        # 07:00 lies in the stock morning window; a 2 °C drop in 15 min at
        # 55 °C is well beyond standby.
        now = datetime(2026, 1, 15, 7, 0, tzinfo=timezone.utc)
        asyncio.run(learner.async_fold_draw_stats(now, 55.0, 2.0, 0.25))
        folded.append(learner.draw_stats._open_kwh)
    return bool(folded[0] == 0.0 and folded[1] > 0.0)


def _ceiling_notice_is_deduplicated() -> bool:
    """D3-01: an unchanged ceiling signature must not re-raise the notice.

    ``check_ceiling`` raises ``dhw_legionella_above_setpoint`` only when the
    (legionella, setpoint, interval) signature changes. Without the
    ``if signature == self.ceiling_notice`` guard, ``create_issue`` runs on
    every coordinator tick and a notice the user dismissed comes straight
    back.
    """
    params = ThermalParameters()
    params.dhw_enabled = True
    params.dhw_legionella_enabled = True
    params.dhw_setpoint = 52.0  # non-stock, so legionella 60 > setpoint is active
    guard = LegionellaGuard(
        FakeHass(),
        "guard-pins-ceiling",
        lambda: params,
        {},
        action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    calls: list[int] = []
    ir = legionella_mod.ir  # the registry ``issues.set_issue`` writes
    original = ir.async_create_issue
    ir.async_create_issue = lambda *a, **k: calls.append(1)
    try:
        guard.check_ceiling()
        guard.check_ceiling()
    finally:
        ir.async_create_issue = original
    return len(calls) == 1


def _write_failed_notice_is_memoised() -> bool:
    """D3-s3-05: the write-failed notice is raised once and cleared once.

    ``_drive_switch`` compares ``switch.failed`` with its memo
    (``write_failed_notice``) and returns while they agree, so a healthy
    cycle issues no Repairs call at all. Without the guard every healthy
    cycle deletes the issue and every failing one re-creates it -- a notice
    the user dismissed comes straight back; forcing it on never raises it.
    """
    guard = LegionellaGuard(
        FakeHass(),
        "guard-pins-write-failed",
        lambda _p=ThermalParameters(): _p,
        {},
        action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )

    async def _no_save() -> None:
        return None

    guard.async_save = _no_save
    calls: list[str] = []
    ir = legionella_mod.ir  # the registry ``issues.set_issue`` writes
    original = ir.async_create_issue, ir.async_delete_issue
    ir.async_create_issue = lambda *a, **k: calls.append(f"create {a[2]}")
    ir.async_delete_issue = lambda hass, dom, iid: calls.append(f"delete {iid}")
    try:
        # Observe mode, nothing owned: release writes nothing, so the
        # switch's sticky ``failed`` flag is what each cycle reports.
        for failed in (False, False, True, True, True, False, False):
            guard.disinfect.failed = failed
            guard.disinfect.failed_entity = "switch.disinfect" if failed else None
            asyncio.run(guard._drive_switch(False))
    finally:
        ir.async_create_issue, ir.async_delete_issue = original
    return calls == [
        "create dhw_disinfection_write_failed",
        "delete dhw_disinfection_write_failed",
    ]


def _gchv_night_mode_pins() -> dict[str, bool]:
    """#1913: kill the GCHV night-mode sites ``--pin-killed`` skip-budgeted.

    ``tests/features.py`` already holds these checks; this copy is the cheap
    driver the pin lane can finish. CI's measure step killed one site with
    features.py and left 53 as SKIP-BUDGET; mutation-autofix then printed
    skip-no-measurement.
    """
    from types import SimpleNamespace as NS
    from itertools import count

    from heatpump_optimizer import const, modbus_prefill, pump_arbiter, quiet_windows

    flag = "binary_sensor.hp_night_mode_frequency_reduction_active"
    start_h = "number.hp_night_mode_start_hour"
    start_m = "number.hp_night_mode_start_minute"
    end_h = "number.hp_night_mode_end_hour"
    end_m = "number.hp_night_mode_end_minute"
    numbers = (start_h, start_m, end_h, end_m)
    limited = const.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY
    silent = const.CONF_QUIET_SILENT_WINDOWS
    off = const.CONF_QUIET_OFF_WINDOWS
    frac = const.CONF_SILENT_MODE_FRACTION
    states = {
        flag: FakeState("off"),
        start_h: FakeState("21", attributes={"min": 0, "max": 23}),
        start_m: FakeState("0", attributes={"min": 0, "max": 59}),
        end_h: FakeState("5", attributes={"min": 0, "max": 23}),
        end_m: FakeState("0", attributes={"min": 0, "max": 59}),
    }
    cfg = {limited: flag, silent: "22:00-06:00", frac: 0.7}
    get = lambda mapping: (lambda eid: mapping.get(eid))
    eve = datetime(2026, 1, 15, 20, 0, tzinfo=timezone.utc)
    at_start = datetime(2026, 1, 15, 22, 0, tzinfo=timezone.utc)
    at_end = datetime(2026, 1, 16, 6, 0, tzinfo=timezone.utc)
    ids = count()

    def capped(arr, p_max=5.0):
        if arr is None:
            return []
        return [i for i, v in enumerate(arr) if float(v) < p_max - 1e-9]

    class Coord:
        def __init__(self, silent_spec="22:00-06:00", off_spec="", duty="control"):
            self.hass = FakeHass({
                "select.pump_mode": FakeState(
                    "Heat + DHW",
                    attributes={"options": ["Off", "Cool + DHW", "Heat + DHW"]},
                ),
                "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
                "number.water_set": FakeState("53", attributes={"min": 25, "max": 63}),
            })
            self._config = {
                "pump_duty_mode": duty,
                "heat_pump_mode_entity": "select.pump_mode",
                "dhw_setpoint_entity": "number.dhw_set",
                "space_setpoint_entity": "number.water_set",
                "space_setpoint_unit": "flow",
                limited: flag,
                silent: silent_spec,
                off: off_spec,
            }
            self._mode = const.MODE_AUTO
            self.stale = False
            # The real coordinator carries its entry; duty_switch keys its store on it.
            self.entry = SimpleNamespace(entry_id="guard_pins")
            self._current_action = {"mode": "eco"}
            t0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
            self._optimization_result = NS(
                timestamps=[t0 + timedelta(minutes=15 * i) for i in range(4)],
                power_schedule=[0.0, 0.0, 0.0, 0.0],
                dhw_power_schedule=[0.0, 0.0, 0.0, 0.0],
                optimal_setpoints=[21.0, 21.0, 21.0, 21.0],
            )
            self._thermal_model = NS(
                params=NS(min_electrical_power=0.4),
                curve_flow_temp=lambda _o: 34.2,
            )
            self._thermal_params = NS(dhw_setpoint=48.0, dhw_max_temp=48.0)
            self._current_state = NS(outdoor_temperature=2.0)
            self.entry = FakeEntry(entry_id=f"gp{next(ids)}")
            self.hass.states.set(flag, FakeState("off"))
            for eid, st in states.items():
                if eid != flag:
                    self.hass.states.set(
                        eid, FakeState(st.state, attributes=dict(st.attributes)),
                    )

        @property
        def effective_config(self):
            return self._config

        @property
        def thermal_params(self):
            return self._thermal_params

        def arbiter_inputs(self):
            return pump_arbiter.ArbiterInputs(
                hass=self.hass,
                config=self._config,
                mode=self._mode,
                plan=self._optimization_result,
                plan_stale=self.stale,
                entry_released=False,
                state=self._current_state,
                thermal=self._thermal_model,
                params=self._thermal_params,
                action=self._current_action,
                measured_power_kw=None,
                disinfecting=False,
            )

        async def async_set_mode(self, mode):
            self._mode = mode

        def device(self, entity, value):
            self.hass.states.get(entity).state = value

        def night_writes(self):
            out = []
            for domain, service, data in self.hass.services.calls:
                entity = (data or {}).get("entity_id") or ""
                if entity in numbers:
                    out.append((entity, (data or {}).get("value")))
            return out

    def run(coord, minutes=0, *, t0=None):
        when = t0 or datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
        asyncio.run(pump_arbiter.apply(coord, when + timedelta(minutes=minutes)))

    one = quiet_windows.compose(
        None, cfg, get(states), eve, 96, 0.25, 5.0,
    )
    two = quiet_windows.compose(
        None, {**cfg, silent: "12:00-13:00,22:00-06:00"}, get(states),
        eve, 96, 0.25, 5.0,
    )
    two_caps = capped(two.caps)
    on = Coord()
    run(on, 0)
    first = on.night_writes()
    for eid, val in first:
        on.device(eid, str(val))
    on.hass.services.calls.clear()
    run(on, 1)
    off_only = Coord(silent_spec="", off_spec="09:00-09:30")
    run(off_only, 0)
    mode_off = Coord()
    mode_off._mode = const.MODE_OFF
    run(mode_off, 0)
    unset = Coord(silent_spec="", off_spec="")
    run(unset, 0)
    day = Coord()
    t0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
    asyncio.run(pump_arbiter.apply(day, t0 + timedelta(hours=4)))
    day_writes = day.night_writes()
    hold = Coord()
    run(hold, 0)
    for eid, val in hold.night_writes():
        hold.device(eid, str(val))
    hold.device(start_h, "21")
    hold.hass.services.calls.clear()
    asyncio.run(pump_arbiter.apply(hold, t0 + timedelta(seconds=5)))
    inside_grace = hold.night_writes()
    asyncio.run(pump_arbiter.apply(hold, t0 + timedelta(seconds=60)))
    past_grace = hold.night_writes()
    gone = Coord()
    gone.hass.states._states.pop(start_h, None)
    restored_bool = arbiter_record.writable("night_start_hour", True)
    restored_int = arbiter_record.writable("night_start_hour", 22)
    wrap = quiet_windows.next_gchv_window(at_start, "22:00-06:00")
    after = quiet_windows.next_gchv_window(at_end, "22:00-06:00")
    ids_hp = modbus_prefill.night_mode_write_ids("hp")
    zero = Coord(silent_spec="10:00-10:00")
    run(zero, 0)
    garbage = Coord(silent_spec="not-a-window")
    run(garbage, 0)
    frac_obs = Coord()
    frac_obs.device(start_h, "22.4")
    return {
        "prefix": (
            modbus_prefill.package_prefix(flag) == "hp"
            and modbus_prefill.package_prefix("binary_sensor.gchv_night") is None
            and modbus_prefill.package_prefix("switch.hp_night_mode") is None
            and modbus_prefill.package_prefix(None) is None
            and modbus_prefill.package_prefix("binary_sensor._night_mode_frequency_reduction_active") is None
        ),
        "ids": ids_hp == {
            "start_hour": start_h, "start_minute": start_m,
            "end_hour": end_h, "end_minute": end_m,
        },
        "ready": (
            quiet_windows.gchv_schedule_ready(cfg, get(states)) is True
            and quiet_windows.gchv_schedule_ready(cfg, get({flag: FakeState("off")})) is False
            and quiet_windows.gchv_schedule_ready(
                {limited: "binary_sensor.gchv_night", silent: "22:00-06:00"},
                get(states),
            ) is False
            and quiet_windows.gchv_schedule_ready(cfg, None) is False
        ),
        "fits": (
            quiet_windows.gchv_fits_pump("22:00-06:00") is True
            and quiet_windows.gchv_fits_pump("12:00-13:00,22:00-06:00") is False
            and quiet_windows.gchv_fits_pump("weekdays 22:00-06:00") is False
        ),
        "next": (
            wrap == (22.0, 6.0)
            and after == (22.0, 6.0)
            and quiet_windows.next_gchv_window(eve, None) is None
        ),
        "one_window": (
            one.caps is not None
            and capped(one.caps) == list(range(8, 40))
            and one.silent_dropped is False
        ),
        "two_windows": (
            two.silent_dropped is True
            and two_caps == list(range(8, 40))
            and 64 not in two_caps
        ),
        "writes": (
            (start_h, 22) in first
            and (start_m, 0) in first
            and (end_h, 6) in first
            and (end_m, 0) in first
            and len(first) == 4
            and on.night_writes() == []
        ),
        "off_d1": off_only.night_writes() == [],
        "optimizer_off": mode_off.night_writes() == [],
        "unset": unset.night_writes() == [],
        "daytime": (
            (start_h, 10) not in day_writes
            and not any(v == 10 for _, v in day_writes)
            and (start_h, 22) in day_writes
            and (end_h, 6) in day_writes
        ),
        "hold": inside_grace == [] and (start_h, 22) in past_grace,
        "observed_none": pump_arbiter._observed(
            gone.arbiter_inputs(), "night_start_hour",
        ) is None,
        "writable": restored_int is True and restored_bool is False,
        "unenforceable": (
            quiet_windows.silent_unenforceable(cfg, get(states)) is False
            and quiet_windows.silent_unenforceable(
                {**cfg, silent: "12:00-13:00,22:00-06:00"}, get(states),
            ) is True
            and quiet_windows.silent_unenforceable({silent: ""}, get(states)) is False
            and quiet_windows.silent_unenforceable(
                {limited: "switch.pump_night_mode", silent: "22:00-06:00"},
                get(states),
            ) is False
        ),
        "domain": modbus_prefill.package_prefix(
            "switch.hp_night_mode_frequency_reduction_active",
        ) is None,
        "suffix": modbus_prefill.package_prefix(
            "binary_sensor.hp_" + ("x" * 50) + "_nope",
        ) is None,
        "mode_slot": pump_arbiter._slot_entity(on._config, "mode") == "select.pump_mode",
        "differs_none": pump_arbiter._differs("night_start_hour", None, 22) is False,
        "differs_frac": pump_arbiter._differs("night_start_hour", 21.8, 22) is True,
        "observed_int": isinstance(
            pump_arbiter._observed(on.arbiter_inputs(), "night_start_hour"), int,
        ),
        "write_ints": bool(first) and all(type(v) is int for _, v in first),
        "zero_window": zero.night_writes() == [],
        "garbage_write": garbage.night_writes() == [],
        "observed_frac": pump_arbiter._observed(
            frac_obs.arbiter_inputs(), "night_start_hour",
        ) == 22,
        "listeners": any(
            start_h in ids
            for ids, _action in getattr(on.hass, "state_listeners", [])
        ),
        "switch_compose": (
            quiet_windows.compose(
                None,
                {limited: "switch.pump_night_mode", silent: "22:00-06:00", frac: 0.7},
                get({}),
                eve, 96, 0.25, 5.0,
            ).silent_dropped is False
        ),
        "unread_compose": (
            quiet_windows.compose(
                None, cfg, get({flag: FakeState("off")}), eve, 96, 0.25, 5.0,
            ).silent_dropped is True
        ),
        "off_only_dropped": (
            quiet_windows.compose(
                None,
                {limited: flag, off: "09:00-09:30", frac: 0.7},
                get(states),
                eve, 96, 0.25, 5.0,
            ).silent_dropped is False
        ),
        "at_noon_end": (
            quiet_windows.next_gchv_window(
                datetime(2026, 1, 15, 13, 0, tzinfo=timezone.utc),
                "12:00-13:00,22:00-06:00",
            ) == (22.0, 6.0)
        ),
        "at_wrap_end": (
            quiet_windows.next_gchv_window(
                datetime(2026, 1, 16, 6, 0, tzinfo=timezone.utc),
                "22:00-06:00,12:00-13:00",
            ) == (12.0, 13.0)
        ),
        "inside_wrap_two": (
            quiet_windows.next_gchv_window(
                datetime(2026, 1, 16, 2, 0, tzinfo=timezone.utc),
                "22:00-06:00,12:00-13:00",
            ) == (22.0, 6.0)
        ),
        "weekday_sat": (
            quiet_windows.next_gchv_window(
                datetime(2026, 1, 17, 10, 0, tzinfo=timezone.utc),
                "weekdays 12:00-13:00, weekend 22:00-06:00",
            ) == (22.0, 6.0)
        ),
        "yesterday_day": (
            quiet_windows.next_gchv_window(eve, "12:00-13:00,22:00-06:00")
            == (22.0, 6.0)
        ),
        "same_day_finish": (
            quiet_windows.next_gchv_window(
                datetime(2026, 1, 15, 12, 30, tzinfo=timezone.utc),
                "12:00-13:00",
            ) == (12.0, 13.0)
        ),
        "empty_merge": quiet_windows._gchv_merge([]) == [],
        "garbage_spec": quiet_windows.compose(
            None, {**cfg, silent: "garbage"}, get(states), eve, 96, 0.25, 5.0,
        ).silent_dropped is True,
    }


def _service_dispatch_pins() -> dict[str, bool]:
    """R9-SW-2: kill ``pump_arbiter._service``'s sites ``--pin-killed`` timed out.

    Each slot's one write through ``_write``: the mode an option select, the
    silent switch turn_on/turn_off, a set-point ``inputs.write_setpoint_c``'s
    set_value. ``tests/features.py`` holds the behaviour; this is the cheap
    driver the pin lane can finish.
    """
    from heatpump_optimizer import pump_arbiter

    class Coord:
        # The real coordinator carries its entry; duty_switch keys its store on it.
        entry = SimpleNamespace(entry_id="guard_pins_slots")

    states = {
        "select.pump_mode": FakeState(
            "Heat + DHW", attributes={"options": ["Heat", "Heat + DHW"]},
        ),
        "switch.night": FakeState("off"),
        "number.dhw_set": FakeState("50", attributes={"min": 40, "max": 63}),
    }
    config = {
        "heat_pump_mode_entity": "select.pump_mode",
        "dhw_setpoint_entity": "number.dhw_set",
        "heat_pump_capacity_limited_entity": "switch.night",
    }
    now = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)

    def one(slot, value):
        coord = Coord()
        coord.hass = FakeHass(dict(states))
        coord.entry = FakeEntry(entry_id=f"gp-write-{slot}")  # _write hands it to off_restore's arm
        inp = pump_arbiter.ArbiterInputs(
            hass=coord.hass, config=config, mode="auto", plan=None,
            plan_stale=False, entry_released=False, state=None, thermal=None,
            params=None, action=None, measured_power_kw=None, disinfecting=False,
        )
        asyncio.run(pump_arbiter._write(coord, inp, slot, value, now))
        calls = [(d, s, dict(data or {})) for d, s, data in coord.hass.services.calls]
        return calls, pump_arbiter.state_for(coord).written.get(slot)

    mode_calls, mode_held = one("mode", "heat")
    on_calls, on_held = one("silent", True)
    off_calls, _ = one("silent", False)
    dhw_calls, dhw_held = one("dhw_setpoint", 52.0)
    return {
        "mode writes its option": mode_calls == [
            ("select", "select_option", {"entity_id": "select.pump_mode", "option": "Heat"}),
        ] and mode_held is not None and mode_held[0] == "heat",
        "silent writes turn_on and turn_off": on_calls == [
            ("switch", "turn_on", {"entity_id": "switch.night"}),
        ] and off_calls == [
            ("switch", "turn_off", {"entity_id": "switch.night"}),
        ] and on_held is not None and on_held[0] is True,
        "a set-point writes set_value": dhw_calls == [
            ("number", "set_value", {"entity_id": "number.dhw_set", "value": 52.0}),
        ] and dhw_held is not None and dhw_held[0] == 52.0,
    }


def _r10_arch_shapes_pins() -> dict[str, bool]:
    """R10-ARCH-SHAPES: the bounds the shared coercions re-spelled (#2819).

    The move put each reader on ``finite_float``, so every guard and bound on
    the re-spelled lines is a new mutation site. One input per site sits on
    the bound itself, where the operator's one-step move changes the answer.
    """
    from heatpump_optimizer import sensor
    from heatpump_optimizer.accuracy import AccuracySample
    from heatpump_optimizer.const import (
        DHW_MIN_TEMP_SETPOINT_MARGIN,
        buffer_tank_surface_area,
    )
    from heatpump_optimizer.coordinator import _at_least
    from heatpump_optimizer.dhw_schedule import _format_day_selector, format_clock
    from heatpump_optimizer.optimizer import CHANNEL_ACTIVE_KW, channel_heating_steps
    from heatpump_optimizer.quiet_windows import _within_nameplate
    from heatpump_optimizer.wood_fuel import _scan_wood_night, cheaper_hour_count

    def sample_kw(raw: object) -> float | None:
        got = AccuracySample.from_dict(
            {"t": "2026-01-05T00:00:00+00:00", "predicted_power_kw": raw}
        )
        return None if got is None else got.predicted_power_kw

    def tank_area(raw: object) -> float | None:
        try:
            return buffer_tank_surface_area(raw)  # type: ignore[arg-type]
        except TypeError:
            return None

    def wood_scan_short_cops() -> bool:
        now = datetime(2026, 1, 5, 20, 0, tzinfo=timezone.utc)
        stamps = [now + timedelta(hours=h) for h in range(3)]
        try:
            _scan_wood_night(now, [3.0, 3.0, 3.0], stamps, [2.0], 0.1, 3)
        except IndexError:
            return False
        return True

    return {
        "an accuracy sample's zero planned draw is kept (bound lo inclusive)":
            sample_kw(0.0) == 0.0 and sample_kw(-0.1) is None,
        "an unreadable tank volume has no surface, not a raise":
            tank_area("x") == 0.0 and (tank_area(200.0) or 0.0) > 0.0,
        "a stored aperture sum at its floor is kept, below it defaulted":
            _at_least(0.0, 0.0, 7.0) == 0.0 and _at_least(-1.0, 0.0, 7.0) == 7.0,
        "three contiguous days render as a range, two as a list":
            _format_day_selector([0, 1, 2]) == "Mo-We"
            and _format_day_selector([0, 1]) == "Mo,Tu",
        "a window ending at midnight keeps 24:00, a later hour folds":
            format_clock(24.0) == "24:00" and format_clock(25.0) == "01:00",
        "a channel drawing exactly the active line is not heating":
            channel_heating_steps([CHANNEL_ACTIVE_KW], [1.0]) == [False]
            and channel_heating_steps([CHANNEL_ACTIVE_KW + 0.01], [1.0]) == [True],
        "a measured ceiling of zero is no measurement":
            _within_nameplate(0.0, 5.0) is None,
        "a measured ceiling exactly at the nameplate is admitted":
            _within_nameplate(5.0, 5.0) == 5.0 and _within_nameplate(5.01, 5.0) is None,
        "the DHW minimum ceiling is the setpoint less the margin":
            sensor._dhw_min_ceiling(55) == round(55 - DHW_MIN_TEMP_SETPOINT_MARGIN, 1)
            and sensor._dhw_min_ceiling("x") is None,
        "a pump hour costing exactly wood's price is not cheaper wood":
            cheaper_hour_count(1.0, [2.0], [2.0], [True]) == 0
            and cheaper_hour_count(1.0, [3.0], [2.0], [True]) == 1,
        "a COP series shorter than the horizon reads as no COP, not a raise":
            wood_scan_short_cops(),
    }


_STEP_ISSUE = "dhw_legionella_off_step"
#: The config flow's integer sliders (``config_flow.py``'s everyday and
#: disinfection selectors) on a 30-80 degC number of each step: every row
#: whose disinfection temperature is above the everyday set-point.
_SLIDER_STEPS = (0.1, 0.5, 1, 2, 5)


def _slider_rows():
    for step in _SLIDER_STEPS:
        for disinfection in range(55, 71):
            for everyday in range(40, min(65, disinfection - 1) + 1):
                yield step, float(everyday), float(disinfection)


#: ``dev/audit/harnesses/r10_disinfection_setpoint.py``'s ``--grid``
#: temperatures, its cycle rows: disinfection above everyday, at most 70.
_GRID_TEMPS = (50.0, 55.0, 57.0, 58.0, 60.0, 60.2, 60.3, 60.4, 60.7, 62.0, 69.6, 70.0, 72.0)


def _grid_rows():
    for step in _SLIDER_STEPS:
        for everyday in _GRID_TEMPS[:-1]:
            for disinfection in _GRID_TEMPS:
                if everyday < disinfection <= 70.0:
                    yield step, everyday, disinfection


def _disinfection_on_step(value, step):
    return abs(value / step - round(value / step)) < 1e-9


def _step_notice(everyday, disinfection, step, *, hold=False, cycle=True, dhw=True,
                 entity="number.dhw", duty="control", attrs=None):
    """The off-step notice's placeholders after one observe pass, or None."""
    params = ThermalParameters(
        dhw_setpoint=everyday, dhw_legionella_temp=disinfection,
        dhw_legionella_enabled=cycle, dhw_enabled=dhw,
    )
    states = {} if entity is None else {
        entity: FakeState("50", attributes=attrs or {"min": 30, "max": 80, "step": step}),
    }
    config = {"pump_duty_mode": duty, "dhw_setpoint_entity": entity,
              "dhw_free_disinfection_enabled": hold}
    hass = FakeHass(states)
    guard = LegionellaGuard(
        hass, "guard-pins-step", lambda: params, config, action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    asyncio.run(guard.async_observe(None, None))
    raised = [i for i in getattr(hass, "issues", []) if i[1] == _STEP_ISSUE]
    return raised[-1][2].get("translation_placeholders") if raised else None


def _slider_count(*, hold=False, on_step=None, steps=_SLIDER_STEPS, rows=_slider_rows):
    """(rows driven, notices raised) over ``rows`` filtered by step and on-step."""
    driven = raised = 0
    for step, everyday, disinfection in rows():
        if step not in steps or on_step not in (None, _disinfection_on_step(disinfection, step)):
            continue
        driven += 1
        raised += _step_notice(everyday, disinfection, step, hold=hold) is not None
    return driven, raised


def _standing(hass):
    """The issue ids standing on the stub registry (``hass.issues``)."""
    return {i[1] for i in getattr(hass, "issues", [])}


def _unreachable_yields_to_the_step_notice() -> bool:
    """While the off-step notice stands, a short cycle raises no hardware advice, and raising it clears that."""
    params = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=62.0,
                               dhw_legionella_enabled=True, dhw_enabled=True)
    hass = FakeHass({"number.dhw": FakeState("50", attributes={"min": 30, "max": 80, "step": 5})})
    guard = LegionellaGuard(
        hass, "guard-pins-step", lambda: params,
        {"pump_duty_mode": "control", "dhw_setpoint_entity": "number.dhw"}, action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    unreachable = "dhw_legionella_unreachable"
    guard.raise_unreachable_issue(58.0, 62.0)
    raised_before = unreachable in _standing(hass)
    asyncio.run(guard.async_observe(None, None))
    cleared = unreachable not in _standing(hass)
    guard.raise_unreachable_issue(58.0, 62.0)
    return raised_before and cleared and unreachable not in _standing(hass) and _STEP_ISSUE in _standing(hass)


def _credit_edges() -> dict[str, bool]:
    """The two credit rules at their edges, through ``async_track``: target less 1.0 credits at once, less 0.5 starts a hold."""
    out: dict[str, bool] = {}
    for free, margin, attr in ((False, 1.0, "last_cycle"), (True, 0.5, "hold_last")):
        seen = []
        for reading in (60.0 - margin, 60.0 - margin - 0.01):
            params = ThermalParameters(dhw_legionella_temp=60.0, dhw_legionella_enabled=True, dhw_enabled=True)
            guard = LegionellaGuard(
                FakeHass(), "guard-pins-edge", lambda p=params: p, {"dhw_free_disinfection_enabled": free},
                action=lambda: {}, disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
                dhw_blocked=lambda: False,
            )
            asyncio.run(guard.async_track(reading))
            seen.append(getattr(guard, attr) is not None)
        out[f"{'hold' if free else 'instant'} credit counts target less {margin} and not 0.01 under"] = seen == [True, False]
    return out


def _off_step_notice_is_deduplicated() -> bool:
    """An unchanged off-step signature does not re-raise the notice (as ``check_ceiling``'s)."""
    params = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=62.0,
                               dhw_legionella_enabled=True, dhw_enabled=True)
    hass = FakeHass({"number.dhw": FakeState("50", attributes={"min": 30, "max": 80, "step": 5})})
    guard = LegionellaGuard(
        hass, "guard-pins-step", lambda: params,
        {"pump_duty_mode": "control", "dhw_setpoint_entity": "number.dhw"}, action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    calls: list[int] = []
    ir = legionella_mod.ir
    original = ir.async_create_issue
    ir.async_create_issue = lambda *a, **k: calls.append(a[2])
    try:
        asyncio.run(guard.async_observe(None, None))
        asyncio.run(guard.async_observe(None, None))
    finally:
        ir.async_create_issue = original
    return calls.count(_STEP_ISSUE) == 1


def _off_step_notice_clears() -> bool:
    """Raised at 62 on step 5, then gone after one pass at 65 (and only then)."""
    params = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=62.0,
                               dhw_legionella_enabled=True, dhw_enabled=True)
    hass = FakeHass({"number.dhw": FakeState("50", attributes={"min": 30, "max": 80, "step": 5})})
    guard = LegionellaGuard(
        hass, "guard-pins-step", lambda: params,
        {"pump_duty_mode": "control", "dhw_setpoint_entity": "number.dhw"}, action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    asyncio.run(guard.async_observe(None, None))
    raised = _STEP_ISSUE in _standing(hass)
    params.dhw_legionella_temp = 65.0
    asyncio.run(guard.async_observe(None, None))
    return raised and _STEP_ISSUE not in _standing(hass)


def _off_step_notice_pins() -> dict[str, bool]:
    """R10-DISINFECTION-STEP-NOTICE: a cycle write the entity's step leaves short of credit is named before it runs.

    The arbiter writes a cycle on the step at or below ``dhw_hard_max_temp``
    (``pump_arbiter.cycle_write``); where that write is under the credit
    threshold in force (target less 1.0, or less 0.5 under free
    disinfection) the guard raises ``dhw_legionella_off_step`` with the
    configured, written and on-step temperatures, in place of the
    after-the-fact ``dhw_legionella_unreachable``. Counts are over the
    slider grid of ``_slider_rows``: the product ruling's 201 (instant, all
    at step 5) and 436 (hold) of 1750; the 1314 on-step rows raise none.
    """
    out: dict[str, bool] = {}
    case = _step_notice(55.0, 62.0, 5)
    out["55/62 on step 5 is named: 62 configured, 60 written, 60 and 65 on the step"] = case == {
        "legionella_temp": "62", "written": "60", "step": "5", "below": "60", "above": "65",
    }
    out["the slider grid raises 201 of 1750 under the instant rule"] = _slider_count() == (1750, 201)
    out["the slider grid raises 436 of 1750 under the hold rule"] = _slider_count(hold=True) == (1750, 436)
    out["the instant rule's 201 are all at step 5"] = _slider_count(steps=(5,))[1] == 201
    out["null: the 1314 on-step slider rows raise none, either rule"] = (
        _slider_count(on_step=True) == (1314, 0) == _slider_count(on_step=True, hold=True)
    )
    out["null: steps 0.1 and 0.5 raise none, either rule"] = (
        _slider_count(steps=(0.1, 0.5))[1] == 0 == _slider_count(steps=(0.1, 0.5), hold=True)[1]
    )
    grid = dict(rows=_grid_rows)
    out["the harness grid raises 34 / 71 of 330 (instant / hold)"] = (
        _slider_count(**grid) == (330, 34) and _slider_count(hold=True, **grid) == (330, 71)
    )
    out["null: the 169 on-step harness grid rows raise none, either rule"] = (
        _slider_count(on_step=True, **grid) == (169, 0) == _slider_count(on_step=True, hold=True, **grid)
    )
    out["the off-step notice shows, not the unreachable notice's hardware advice"] = (
        _unreachable_yields_to_the_step_notice()
    )
    out["an unchanged off-step signature does not re-raise the notice"] = _off_step_notice_is_deduplicated()
    out["the notice clears once the disinfection temperature is on the step"] = _off_step_notice_clears()
    out.update(_credit_edges())
    out["null: the cycle disabled raises none"] = _step_notice(55.0, 62.0, 5, cycle=False) is None
    out["null: hot water disabled raises none"] = _step_notice(55.0, 62.0, 5, dhw=False) is None
    out["null: no set-point entity raises none"] = _step_notice(55.0, 62.0, 5, entity=None) is None
    out["null: an arbiter that writes nothing (observe) raises none"] = (
        _step_notice(55.0, 62.0, 5, duty="observe") is None
    )
    out["null: the stock 55/60 raises none on any step"] = all(
        _step_notice(55.0, 60.0, s, hold=h) is None for s in _SLIDER_STEPS for h in (False, True)
    )
    out["63 on step 5 is named below 60 and above 65, the step down and up, not the nearest"] = (
        _step_notice(55.0, 63.0, 5) == {
            "legionella_temp": "63", "written": "60", "step": "5", "below": "60", "above": "65",
        }
    )
    capped = {"min": 30, "max": 60, "step": 1}
    out["a range-capped write (max 60 under 65, step 1) raises no off-step notice, either rule"] = all(
        _step_notice(55.0, 65.0, 1, hold=h, attrs=capped) is None for h in (False, True)
    )
    out["a range-capped write leaves the unreachable notice's hardware advice standing"] = (
        _shortfall_standing(capped, 65.0) == {"dhw_legionella_above_setpoint", "dhw_legionella_unreachable"}
    )
    for step in (5, 1):
        out[f"a hard-cap shortfall (75 over the 70 C hard maximum, step {step}) raises no off-step notice, either rule"] = all(
            _step_notice(55.0, 75.0, step, hold=h) is None for h in (False, True)
        )
    out["a hard-cap shortfall leaves the unreachable notice's hardware advice standing"] = (
        _shortfall_standing({"min": 30, "max": 80, "step": 5}, 75.0)
        == {"dhw_legionella_above_setpoint", "dhw_legionella_unreachable"}
    )
    out["68 on step 5 is named: the step above, 70, is the hard maximum and writable"] = (
        _step_notice(55.0, 68.0, 5) == {
            "legionella_temp": "68", "written": "65", "step": "5", "below": "65", "above": "70",
        }
    )
    out["null: the same 65 on a max-80 step-5 entity off the step (62) still raises"] = (
        _step_notice(55.0, 62.0, 5, attrs={"min": 30, "max": 80, "step": 5}) is not None
        and _shortfall_standing({"min": 30, "max": 80, "step": 5}, 62.0)
        == {"dhw_legionella_above_setpoint", _STEP_ISSUE}
    )
    rows, raised, bad = _range_census()
    out[f"entity-range census: {raised} of {rows} rows raise, each with below < target <= above <= max"] = (
        (rows, raised) == _RANGE_CENSUS and not bad
    )
    return out


#: (rows, notices) of `_range_census`: min 30 or 60, max 55-80, steps 0.5/1/3/5,
#: disinfection 55-75 (the service's range until it stopped at the 70 °C cap;
#: an earlier release's stored 71-75 still reaches the guard), everyday 55,
#: both credit rules.
_RANGE_CENSUS = (2856, 277)


def _shortfall_standing(attrs, disinfection) -> set:
    """The issues standing after one observe pass and a short cycle (58 reached)."""
    params = ThermalParameters(dhw_setpoint=55.0, dhw_legionella_temp=disinfection,
                               dhw_legionella_enabled=True, dhw_enabled=True)
    hass = FakeHass({"number.dhw": FakeState("50", attributes=attrs)})
    guard = LegionellaGuard(
        hass, "guard-pins-step", lambda: params,
        {"pump_duty_mode": "control", "dhw_setpoint_entity": "number.dhw"}, action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    asyncio.run(guard.async_observe(None, None))
    guard.raise_unreachable_issue(58.0, disinfection)
    return _standing(hass)


def _range_census():
    """Every entity range against every disinfection target: (rows, raised, bad rows).

    The notice is owed exactly where the step below the target is short of
    credit and the step above it is writable (inside min and max, and at or
    under the 70 C hard maximum a cycle never exceeds): a range cap or the
    hard cap is the unreachable notice's. A raised notice must name a writable
    step above the target and one below it (below < target <= above <= max,
    above - below == step).
    """
    rows = raised = 0
    bad = []
    for lo in (30, 60):
        for hi in (55, 58, 60, 62, 64, 65, 66, 68, 70, 80):
            if hi <= lo:
                continue
            for step in (0.5, 1, 3, 5):
                for d in range(55, 76):
                    for hold in (False, True):
                        rows += 1
                        got = _step_notice(55.0, float(d), step, hold=hold,
                                           attrs={"min": lo, "max": hi, "step": step})
                        down, up = math.floor(d / step) * step, math.ceil(d / step) * step
                        owed = lo <= down < d - (0.5 if hold else 1.0) and up <= min(hi, 70)
                        if (got is not None) != owed:
                            bad.append((lo, hi, step, d, hold, got))
                        if got is None:
                            continue
                        raised += 1
                        below, above = float(got["below"]), float(got["above"])
                        if not (below < d <= above <= hi and abs(above - below - step) < 1e-9
                                and hi >= d and lo <= d):
                            bad.append((lo, hi, step, d, hold, got))
    return rows, raised, bad


# R11-D3-PINS-plant pins (#3755)
def _plant_pins() -> dict[str, bool]:
    """COP path, weather, ECL110 displacement and DHW coast-hours pins."""
    import heatpump_optimizer.defrost as dfr
    from heatpump_optimizer.thermal_model import ThermalModel as TM

    tanks = np.array([25.0, 35.0, 40.0, 50.0, 60.0])

    def model(**kw):
        return TM(ThermalParameters(two_zone_enabled=True, **kw))

    def derate(grid):
        d = dfr.DefrostDerate(factors=dfr._grid(1.0), counts=dfr._grid(100))
        for i in range(len(d.factors)):
            for j in range(len(d.factors[i])):
                d.factors[i][j] = grid(i, j)
        return d

    def is_(got, want):
        return bool(np.allclose(np.asarray(got, dtype=float), want, rtol=0, atol=1e-6))

    out: dict[str, bool] = {}
    # COP path: _batch_cop and the scalar law.
    ref = model()
    out["_batch_cop caps the nominal-COP factor at 1.5x above 27 C (D3-wave-43b54266f12bfb21)"] = (
        is_(ref._batch_cop(30.0, None, tanks, False), 5.25)
        and is_(ref._batch_cop(40.0, None, tanks, False), 5.25))
    out["compute_cop caps the nominal-COP factor at 1.5x above 27 C (D3-wave-a6cebb125b72f083)"] = (
        is_(ref.compute_cop(30.0), 5.25) and is_(ref.compute_cop(40.0), 5.25))
    flat = model(defrost_derate=derate(lambda i, j: 0.7))
    out["_batch_cop applies a learned defrost derate (D3-wave-dfe094233a9164e0)"] = (
        is_(flat._batch_cop(-2.0, 90.0, tanks, False), 1.89875)
        and is_(flat.compute_cop(-2.0, 90.0), 1.89875))
    wet = derate(lambda i, j: (0.9, 0.6)[min(j, 1)])
    m_none = model(defrost_derate=wet)
    m_80 = model(defrost_derate=wet, ambient_humidity=80.0)
    m_90 = model(defrost_derate=wet, ambient_humidity=90.0)
    nan = float("nan")
    out["_batch_cop treats a NaN humidity step as no humidity (D3-wave-e3a350a3272762f1)"] = (
        is_(m_none._batch_cop(-2.0, nan, tanks, False), 2.44125)
        and is_(m_80._batch_cop(-2.0, nan, tanks, False), 1.7161262376237623)
        and is_(m_80._batch_cop(-2.0, None, tanks, False), 1.7161262376237623))
    out["_batch_cop falls back to the live ambient humidity for a step without one (D3-wave-94ce174acf85b6f2)"] = (
        is_(m_90._batch_cop(-2.0, None, tanks, False), 1.6275)
        and is_(m_90.compute_cop(-2.0, humidity=None), 1.6275)
        and is_(m_none._batch_cop(-2.0, None, tanks, False), 2.44125))
    carnot = model(cop_flow_carnot=True)
    unthrottled = carnot._batch_cop(0.0, None, tanks, False)
    out["_batch_cop applies the Carnot lift cost only on a throttled step (D3-wave-898d741cf6142efb)"] = (
        is_(unthrottled, 2.8875)
        and is_(carnot.compute_cop(0.0, flow_temp=None), 2.8875)
        and float(carnot._batch_cop(0.0, None, tanks, True)[-1]) < 2.0
        and is_(model(cop_flow_carnot=False)._batch_cop(0.0, None, tanks, True), 2.8875))
    # Weather: rain and solar.
    u = lambda precip: ref.effective_heat_loss_coefficient(0.1, 0.0, precip)  # noqa: E731
    out["precipitation of exactly 0.1 mm/h is dry (D3-wave-9df41596c4fa89c6)"] = (
        is_(u(0.1), 0.1) and is_(u(0.2), 0.10075 + 0.00075))
    out["heavy rain saturates the heat-loss multiplier at 2 mm/h (D3-wave-029c040224dc4e38)"] = (
        is_(u(2.0), 0.115) and is_(u(10.0), 0.115) and is_(u(50.0), 0.115))
    out["negative irradiance yields no solar gain (D3-wave-f7e051cc469b465f)"] = (
        ref.compute_solar_gain(-10.0) == 0.0 and is_(ref.compute_solar_gain(500.0), 2.45))
    # ECL110 displacement lag.
    def ecl(eff, cmd, dt):
        s = ThermalState()
        s.ecl110_effective_displace = eff
        s = ref.update_ecl110_displace_state(s, cmd, dt)
        return s.ecl110_displace_command, s.ecl110_effective_displace
    out["the ECL110 command is clipped to the displace range (D3-wave-f66c6e9cf9d1f84a)"] = (
        is_(ecl(0.0, 40.0, 0.25), (20.0, 3.3333333333))
        and is_(ecl(0.0, -40.0, 0.25), (-20.0, -3.3333333333)))
    out["the ECL110 lag gain never overshoots the command (D3-wave-9362d5efbe6808c2)"] = (
        ecl(0.0, 10.0, 24.0) == (10.0, 10.0) and ecl(0.0, 10.0, 1.5) == (10.0, 10.0))
    out["the ECL110 effective displace is held inside the range (D3-wave-36117bb3a189672b)"] = (
        ecl(-25.0, -29.0, 0.0) == (-20.0, -20.0) and ecl(25.0, 29.0, 0.0) == (20.0, 20.0))
    # DHW hours of storage.
    out["a tank at exactly ambient coasts 0 h (D3-wave-402ffd06ddbd856a)"] = (
        ref.dhw_coast_hours(20.0, 10.0, 20.0) == 0.0
        and ref.dhw_coast_hours(30.0, 10.0, 30.0) == 0.0)
    out["a tank below ambient coasts 0 h (D3-wave-d90533f4d17cfa14)"] = (
        ref.dhw_coast_hours(10.0, 5.0, 20.0) == 0.0
        and ref.dhw_coast_hours(15.0, 10.0, 20.0) == 0.0)
    slow = TM(ThermalParameters(dhw_cooling_rate=0.0))
    out["dhw_coast_hours is capped at 168 h for a near-lossless tank (D3-wave-011b9e2e975b5e98)"] = (
        slow.dhw_coast_hours(60.0, 40.0) == 168.0
        and abs(ref.dhw_coast_hours(60.0, 40.0) - 57.762265046662115) < 1e-9)
    return out


# R11-D3-PINS-plant pins (#3755) -- valve delivery, batch wood/tank, params
def _valve_batch_params_pins() -> dict[str, bool]:
    """Two-zone valve delivery, batch two-tank trajectory and parameter pins."""
    import heatpump_optimizer.thermal_model as tmod
    from heatpump_optimizer import const, dhw_schedule, mixing_valve
    from heatpump_optimizer.thermal_model import ThermalState

    def near(got, want, tol=1e-6):
        return bool(np.allclose(np.asarray(got, dtype=float), want, rtol=0, atol=tol))

    def valve(two, loss, dt, T_buf=25.0):
        p = ThermalParameters()
        p.wood_tank_configured = True
        s = ThermalState(upper_floor_temperature=18.0, slab_temperature=15.0,
                         buffer_tank_temperature=T_buf, wood_tank_temperature=30.0)
        try:
            return tmod._valve_two_zone_delivery(
                p, s, 0.0, 0.0, loss, None, 5.0, (0.2, 0.2), dt, two)
        except ZeroDivisionError:
            return (float("nan"),) * 5

    out: dict[str, bool] = {}
    # _valve_two_zone_delivery
    r = valve(False, 0.0, 0.25)
    out["a valved single tank's delivery is bounded by the coldest zone it feeds (D3-wave-19404e3632806509)"] = (
        near(r[:2], [0.5167272727272727, 1.1072727272727272]))
    r = valve(True, 0.0, 0.0)
    out["a zero-length two-tank step delivers finite heat, the wood-tank bound keeps its dt floor (D3-wave-beeb068352333132)"] = (
        near(r[:3], [5.578333333333334, 10.4675, 16.045833333333334]))
    out["a zero-length two-tank step delivers finite heat, the heat-pump-tank bound keeps its dt floor (D3-wave-ea9c4705de428b28)"] = (
        near(r[:3], [5.578333333333334, 10.4675, 16.045833333333334]))
    r = valve(True, 3.0, 0.25)
    out["a heat-pump tank losing more than it holds supplies zero, not negative heat (D3-wave-98853a541b6b5d6a)"] = (
        near(r[:3], [5.578333333333334, 10.4675, 16.045833333333334]))
    r = valve(True, 0.0, 1.0)
    out["a partly starved two-tank step scales both emitters down in proportion (D3-wave-39041ccf21eedba6)"] = (
        near(r[:3], [3.1525414441895445, 5.915606973478468, 8.662148417668012]))
    # _simulate_step_two_zone: a throttled single tank charging at a zero-length step
    def charge(dt):
        q = ThermalParameters(two_zone_enabled=True, mixing_valve_mode="manual")
        st = ThermalState(upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                          slab_temperature=22.0, buffer_tank_temperature=69.9999999)
        try:
            return ThermalModel(q)._simulate_step_two_zone(st, 5.0, 0.0, dt_hours=dt).buffer_tank_temperature
        except ZeroDivisionError:
            return float("nan")

    out["a zero or sub-microsecond step keeps the buffer-ceiling cap finite and below the ceiling (D3-wave-c5e678a5d1812e40)"] = (
        near(charge(0.0), 69.9999999, 1e-12) and near(charge(1e-7), 69.99999991, 1e-12)
        and near(charge(0.25), 70.0, 1e-12))
    # apply_dhw_coil: a wood tank colder than the mains is left alone
    pm = ThermalParameters()
    cold = pm.dhw_inlet_reference - 0.5
    st = ThermalState(wood_tank_temperature=cold)
    ThermalModel(pm).apply_dhw_coil(st, 3.0, 50.0, 0.25)
    out["a wood tank colder than the DHW inlet is not lifted to it by the coil (D3-wave-5b8e7044ee7974f8)"] = (
        st.wood_tank_temperature == cold)
    # ThermalParameters
    def loss(volume, rate):
        q = ThermalParameters(buffer_tank_volume=volume, buffer_cooling_rate=rate,
                              mixing_valve_mode=mixing_valve.MODE_MANUAL)
        return q.buffer_tank_heat_loss_coefficient

    lo, hi = const.buffer_cooling_rate_bounds(750.0)
    out["a near-zero buffer cooling rate is lifted to the tank's lower bound (D3-wave-b2faf84904db389e)"] = (
        loss(750.0, 1e-9) > 0.0 and loss(750.0, 1e-9) == loss(750.0, lo)
        and loss(750.0, 1e-9) < loss(750.0, hi))
    out["an absurd buffer cooling rate is capped at the tank's upper bound (D3-wave-05b5a15efaaf70de)"] = (
        loss(750.0, 50.0) == loss(750.0, hi) and loss(750.0, hi) > loss(750.0, lo))
    pat = [0.0] * 24
    pat[3] = 1e-6
    pw = ThermalParameters(dhw_schedule_enabled=True, dhw_windows=[dhw_schedule.FULL_DAY],
                           dhw_hourly_draw_pattern=pat)
    out["a windowed draw pattern whose masked total is exactly 1e-6 keeps its base shape (D3-wave-3d4899a05eb126c3)"] = (
        pw.effective_dhw_draw_pattern()[3] == 1e-6)
    return out


# R11-D3-PINS-money: the money seam's surviving mutants (#3755, class I1),
# judged at a826f55f8c; ADR-011 fixes the shape. Each pin drives the
# production entry point with the judge's moving input and asserts the
# outcome the probe measured at the unpatched tree; the key in each name is
# the mutant's, and tests/mutation_ledger/killed_by/ holds its row.
def _money_safe(fn):
    try:
        return bool(fn())
    except Exception:  # noqa: BLE001
        return False


class _MoneyCount(logging.Handler):
    def __init__(self):
        super().__init__(logging.WARNING)
        self.n = 0

    def emit(self, record):
        self.n += 1


def _money_restore(factor, wsum=2.0, samples=1):
    return tariff_mod.PeakTracker.from_dict({
        "month": "2026-01", "peaks": [1.0], "peak_days": ["2026-01-05"],
        "window_key": "2026-01-10T07:00:00|60", "window_sum": wsum,
        "window_samples": samples, "window_factor": factor})


def _money_tar(n=3):
    return tariff_mod.CapacityTariff(enabled=True, price_per_kw=50.0, peaks_averaged=n)


def _money_tiny_warns(fn):
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        out = fn()
    return out, sum(1 for w in rec if issubclass(w.category, RuntimeWarning))


def _pin_de935c38():
    """D3-wave-de935c38786265e7: a non-finite persisted window_factor keeps the window (peak 2.0 survives its close)."""
    for f in ("nan", "inf", float("nan"), float("inf")):
        t = _money_restore(f)
        t.observe(datetime(2026, 1, 10, 9, 0), 0.5, _money_tar())
        if tuple(round(p, 6) for p in t.peaks) != (2.0, 1.0):
            return False
    return True


def _pin_7fcaf91c():
    """D3-wave-7fcaf91cced5ce41: non-finite/negative samples are dropped; the window peak stays 2.0."""
    for bad in (float("nan"), float("inf"), -1.0):
        t = tariff_mod.PeakTracker()
        tar = _money_tar()
        for i, kw in enumerate([2.0, bad]):
            t.observe(datetime(2026, 1, 10, 7, 10 * i), kw, tar)
        t.observe(datetime(2026, 1, 10, 9, 0), 0.5, tar)
        if [round(p, 6) for p in t.peaks] != [2.0]:
            return False
    return True


def _pin_3e9a439b():
    """D3-wave-3e9a439baa86a074: stored 0.0 peaks survive an as_dict/from_dict restart (3 reloaded, billed 1.3333)."""
    t = tariff_mod.PeakTracker(month="2026-11", peaks=[4.0, 0.0004, 0.0003],
                      peak_days=["2026-11-03", "2026-11-04", "2026-11-05"],
                      closed_month="2026-10", closed_peaks=[4.0, 0.0004, 0.0003])
    t2 = tariff_mod.PeakTracker.from_dict(t.as_dict())
    tar = _money_tar()
    return (len(t2.peaks) == 3 and abs(t2.billed_peak_kw(tar) - 1.3333333) < 1e-3
            and abs(t2.threshold_kw(tar)) < 1e-6)


def _pin_9297f123():
    """D3-wave-9297f123a6265555: apply_catalog(none/''/None) returns None with no warning logged."""
    h = _MoneyCount()
    log = logging.getLogger(grid_fee_mod.__name__)
    log.addHandler(h)
    try:
        outs = [grid_fee_mod.apply_catalog(p) for p in (grid_fee_mod.DSO_PRODUCT_NONE, "", None)]
    finally:
        log.removeHandler(h)
    return outs == [None, None, None] and h.n == 0


def _pin_911f3cf5():
    """D3-wave-911f3cf5172ffc44: apply_catalog on a catalog row with unparsable rules returns None."""
    tmpl = dict(next(iter(grid_fee_mod.SWEDEN_CATALOG.values())))
    for bad in ("garbage", "Mon = abc"):
        with mock.patch.dict(grid_fee_mod.SWEDEN_CATALOG, {"stale_row": dict(tmpl, grid_fee_rules=bad)}):
            if grid_fee_mod.apply_catalog("stale_row") is not None:
                return False
    return True


def _pin_b5f0a732():
    """D3-wave-b5f0a73275608684: max_abs_component on a tie with the fixed fee is labelled 'fixed'."""
    s = grid_fee_mod.GridFeeSchedule(mode=grid_fee_mod.MODE_ENTITY, fixed=0.30)
    z = grid_fee_mod.GridFeeSchedule(mode=grid_fee_mod.MODE_ENTITY, fixed=0.0)
    return (grid_fee_mod.max_abs_component(s, 0.30)[1] == "fixed" and grid_fee_mod.max_abs_component(s, -0.30)[1] == "fixed"
            and grid_fee_mod.max_abs_component(z, 0.0)[1] == "fixed")


def _pin_68cc141b():
    """D3-wave-68cc141bf2c3493a: min_component on a tie with the fixed fee is labelled 'fixed'."""
    s = grid_fee_mod.GridFeeSchedule(mode=grid_fee_mod.MODE_ENTITY, fixed=-0.20)
    z = grid_fee_mod.GridFeeSchedule(mode=grid_fee_mod.MODE_ENTITY, fixed=0.0)
    return grid_fee_mod.min_component(s, -0.20)[1] == "fixed" and grid_fee_mod.min_component(z, 0.0)[1] == "fixed"


def _pin_2043855e():
    """D3-wave-2043855ef5cf151d: parse_rules(None) and parse_rules('') are [], spec_problem(None) is None."""
    return grid_fee_mod.parse_rules(None) == [] and grid_fee_mod.parse_rules("") == [] and grid_fee_mod.spec_problem(None) is None


def _pin_24604339():
    """D3-wave-246043395831f540: peaks_averaged 0 gives marginal_price_per_kw 0.0 (no ZeroDivisionError)."""
    return (_money_tar(0).marginal_price_per_kw == 0.0 and _money_tar(-1).marginal_price_per_kw == 0.0
            and abs(_money_tar(3).marginal_price_per_kw - 16.6666667) < 1e-4)


def _pin_4ad3dc13():
    """D3-wave-4ad3dc13bfdb70a8: a persisted window_factor of exactly 0.0 is kept (window restored, factor 0.0)."""
    t = _money_restore(0.0)
    d = t.as_dict()
    return d["window_factor"] == 0.0 and d["window_sum"] == 2.0 and d["window_samples"] == 1


def _pin_37b3c9a0():
    """D3-wave-37b3c9a03326d207: _one_per_day keeps every undated peak."""
    return (tariff_mod._one_per_day([(3.0, ""), (2.0, "")]) == [(3.0, ""), (2.0, "")]
            and tariff_mod._one_per_day([(3.0, ""), (2.0, ""), (1.0, "2026-01-05")])
            == [(3.0, ""), (2.0, ""), (1.0, "2026-01-05")])


def _pin_6536ff6b():
    """D3-wave-6536ff6b094f971d: _smooth_topk_sum with k<=0 or empty input is 0.0."""
    x = np.array([3.0, 1.0, 2.0])
    return (tariff_mod._smooth_topk_sum(x, 0, 0.05) == 0.0 and tariff_mod._smooth_topk_sum(x, -1, 0.05) == 0.0
            and tariff_mod._smooth_topk_sum(np.array([]), 3, 0.05) == 0.0)


def _pin_5371ee2b():
    """D3-wave-5371ee2b5e897750: _smooth_topk_sum with no positive entry is 0.0 (negative / nan-only too)."""
    f = tariff_mod._smooth_topk_sum
    return (f(np.array([-1.0, -2.0]), 1, 0.05) == 0.0 and f(np.array([0.0, 0.0, 0.0]), 2, 0.05) == 0.0
            and f(np.array([float("nan")]), 1, 0.05) == 0.0)


def _pin_2d037a10():
    """D3-wave-2d037a10caa62e28: realised_peak of empty series is 0.0."""
    e = np.array([])
    return tariff_mod.realised_peak(e, e, 60, 0.25) == 0.0 and tariff_mod.realised_peak(e, e, 15, 0.25, 2) == 0.0


def _pin_5f094dbc():
    """D3-wave-5f094dbca9a593e9: _smooth_topk_sum on a 1e-8 kW plateau (recorded 9.97887e-09 / 1.99579e-08 for k=1/2)."""
    x1 = np.array([1e-8] * 3 + [5e-9, 0.0, 1e-8 / 3])
    x2 = np.array([1e-8] * 4 + [5e-9, 0.0, 1e-8 / 3])
    return (abs(tariff_mod._smooth_topk_sum(x1, 1, 0.05) - 9.978865e-09) < 2e-12
            and abs(tariff_mod._smooth_topk_sum(x2, 2, 0.05) - 1.995794e-08) < 4e-12)


def _pin_996dce51():
    """D3-wave-996dce5148e02763: _smooth_topk_sum_batch on 1e-8 kW rows (recorded 9.97887e-09 / 1.99579e-08 for k=1/2)."""
    x1 = np.array([[1e-8] * 3 + [5e-9, 0.0, 1e-8 / 3]] * 2)
    x2 = np.array([[1e-8] * 4 + [5e-9, 0.0, 1e-8 / 3]] * 2)
    return (bool(np.all(np.abs(tariff_mod._smooth_topk_sum_batch(x1, 1, 0.05) - 9.978865e-09) < 2e-12))
            and bool(np.all(np.abs(tariff_mod._smooth_topk_sum_batch(x2, 2, 0.05) - 1.995794e-08) < 4e-12)))


def _pin_1894e6dc():
    """D3-wave-1894e6dcd2251a30: metering_windows of an empty series is empty (not a one-element nan), no warning."""
    e = np.array([])
    out, n = _money_tiny_warns(lambda: [tariff_mod.metering_windows(e, w, 0.25, o) for w, o in ((60, 0), (60, 2), (15, 0))])
    return n == 0 and all(r.size == 0 for r in out)


_MONEY_DAY = [0.30, 0.25, 0.20, 0.20, 0.22, 0.35, 0.80, 1.20, 1.10, 0.90, 0.70, 0.60,
       0.55, 0.50, 0.60, 0.80, 1.10, 1.50, 1.40, 1.00, 0.80, 0.60, 0.45, 0.35]
_MONEY_DAY2 = _MONEY_DAY[::-1]
_MONEY_WEEKDAYS = [datetime(2026, 1, 5 + i, 12) for i in range(5)]  # Mon..Fri
_MONEY_WEEKEND = [datetime(2026, 1, 10, 12), datetime(2026, 1, 11, 12),
           datetime(2026, 1, 17, 12), datetime(2026, 1, 18, 12)]  # Sat Sun Sat Sun
_MONEY_WED = datetime(2026, 1, 7, 12)


def _money_close(a, b, tol=1e-3):
    return abs(float(a) - float(b)) <= tol


def _money_model(days, whens=_MONEY_WEEKDAYS):
    m = PriceShapeModel()
    for when, d in zip(whens, days):
        m.observe_day(when, d)
    return m


def _money_quarters(hourly, ramp=(0.9, 0.97, 1.03, 1.1)):
    return [p * r for p in hourly for r in ramp]


def _money_trained5():
    return _money_model([_MONEY_DAY, _MONEY_DAY2, _MONEY_DAY, _MONEY_DAY2, _MONEY_DAY])


def _pin_0ea7620c():
    """SHAPE_ALPHA: learned hour-17 weekday shape after two different days (0ea7620c)."""
    return _money_close(_money_model([_MONEY_DAY, _MONEY_DAY2]).summary()["weekday_shape"][17], 2.063)


def _pin_213a122a():
    """SHAPE_CONFIDENCE_DAYS: damped shape after two days (213a122a)."""
    m = _money_model([_MONEY_DAY, _MONEY_DAY2])
    return _money_close(m.shape_for(_MONEY_WED)[17], 1.42535, 1e-4)


def _pin_b10967dd():
    """SHAPE_MIN: a near-zero hour is clipped before learning (b10967dd)."""
    m = _money_model([[0.01] + [1.0] * 23])
    return _money_close(m.summary()["weekday_shape"][0], 0.198)


def _pin_7e5493bc():
    """QUARTER_ALPHA: quarter factor after a second, different quarter day (7e5493bc)."""
    m = PriceShapeModel()
    m.observe_day_quarters(_MONEY_WEEKDAYS[0], _money_quarters(_MONEY_DAY))
    m.observe_day_quarters(_MONEY_WEEKDAYS[1], _money_quarters(_MONEY_DAY2, (1.5, 0.5, 1.5, 0.5)))
    return _money_close(m.quarter_factor(datetime(2026, 1, 7, 5, 45)), 1.0112, 1e-3)


def _pin_66686e3b():
    """QUARTER_CONFIDENCE_DAYS: damped quarter factor after one quarter day (66686e3b)."""
    m = PriceShapeModel()
    m.observe_day_quarters(_MONEY_WEEKDAYS[0], _money_quarters(_MONEY_DAY))
    return _money_close(m.quarter_factor(datetime(2026, 1, 7, 5, 45)), 1.02, 1e-4)


def _pin_5bf50f5d():
    """QUARTER_FACTOR_MIN: a tiny quarter is clipped up before learning (5bf50f5d)."""
    m = PriceShapeModel()
    m.observe_day_quarters(_MONEY_WEEKDAYS[0], _money_quarters(_MONEY_DAY, (0.01, 0.5, 0.5, 3.0)))
    return _money_close(m.quarter_factors[0][4 * 5], 0.23585, 1e-4)


def _money_spike_day():
    v = []
    for i, p in enumerate(_MONEY_DAY):
        v += [-p, -p, -p, 5 * p] if i == 5 else [p] * 4
    return v


def _pin_cc96ce9e():
    """QUARTER_FACTOR_MAX: a huge quarter is clipped down before learning (cc96ce9e)."""
    m = PriceShapeModel()
    m.observe_day_quarters(_MONEY_WEEKDAYS[0], _money_spike_day())
    return _money_close(m.quarter_factors[0][4 * 5 + 3], 3.36842, 1e-4)


def _pin_b5aef007():
    """VAR_ALPHA: hour-17 sigma after four alternating days (b5aef007)."""
    m = _money_model([_MONEY_DAY, _MONEY_DAY2, _MONEY_DAY, _MONEY_DAY2])
    return _money_close(m.summary()["weekday_sigma"][17], 0.9862, 1e-3)


def _pin_b9b6cf1d():
    """expected_daily_min: no day types or a non-finite / non-positive level gives None (b9b6cf1d)."""
    m = _money_trained5()
    return (
        m.expected_daily_min([], 0.8) is None
        and m.expected_daily_min([0], float("nan")) is None
        and m.expected_daily_min([0], 0.0) is None
        and m.expected_daily_min([0, 1], -0.4) is None
        and m.expected_daily_min([0], float("inf")) is None
    )


def _pin_a5c9796d():
    """expected_daily_min: exactly 5 observed days is trusted, 4 is not (a5c9796d)."""
    five = _money_trained5().expected_daily_min([0], 1.0)
    four = _money_model([_MONEY_DAY, _MONEY_DAY2, _MONEY_DAY, _MONEY_DAY2]).expected_daily_min([0], 1.0)
    return five is not None and four is None


def _pin_13cadf1a():
    """from_dict: residual variance exactly at the learner's maximum is kept (13cadf1a)."""
    top = price_model_mod.RESIDUAL_VAR_MAX
    row = [top] + [0.5] * 23
    m = PriceShapeModel.from_dict({"residual_var": [row, list(row)]})
    return m.residual_var[0][0] == top and m.residual_var[1][1] == 0.5


def _pin_0b10a7c7():
    """observe_day: first day seeds residual variance outright; sigma[17] 1.1858 (0b10a7c7)."""
    s = _money_model([_MONEY_DAY]).summary()["weekday_sigma"]
    return _money_close(s[17], 1.1858, 1e-3) and _money_close(s[3], 0.7086, 1e-3)


def _pin_c4697335():
    """observe_day: first day seeds the shape outright; weekday_shape[17] 2.186 (c4697335)."""
    return _money_close(_money_model([_MONEY_DAY]).summary()["weekday_shape"][17], 2.186)


def _pin_4e79ba6e():
    """observe_day_quarters: an hour averaging exactly 1e-6 keeps factors 1.0 (4e79ba6e)."""
    hour = [0.5e-6, 1.5e-6, 0.5e-6, 1.5e-6]
    day = hour + [1.0] * 92
    if float(np.mean(hour)) != 1e-6:
        return False
    m = PriceShapeModel()
    for when in _MONEY_WEEKDAYS:
        m.observe_day_quarters(when, day)
    return (m.quarter_factor(datetime(2026, 1, 7, 0, 0)) == 1.0
            and m.quarter_factor(datetime(2026, 1, 7, 0, 15)) == 1.0)


def _pin_12cd6ddd():
    """observe_day_quarters: first quarter day seeds factors outright (12cd6ddd)."""
    m = PriceShapeModel()
    m.observe_day_quarters(_MONEY_WEEKDAYS[0], _money_quarters(_MONEY_DAY, (0.5, 0.5, 0.5, 2.5)))
    return _money_close(m.quarter_factors[0][4 * 5 + 3], 2.5, 1e-4)


def _pin_3a064c11():
    """summary: weekday_sigma reports the learned dispersion, not zero (3a064c11)."""
    s = _money_model([_MONEY_DAY, _MONEY_DAY2, _MONEY_DAY, _MONEY_DAY2]).summary()["weekday_sigma"]
    return _money_close(s[17], 0.9862, 1e-3) and max(s) > 0.9


def _pin_efa02472():
    """summary: weekend_sigma reports the learned dispersion, not zero (efa02472)."""
    s = _money_model([_MONEY_DAY, _MONEY_DAY2, _MONEY_DAY, _MONEY_DAY2], _MONEY_WEEKEND).summary()["weekend_sigma"]
    return _money_close(s[17], 0.9862, 1e-3) and max(s) > 0.9


def _pin_a38612ad():
    """from_dict: an all-zero stored shape is clipped and renormalised to ones (a38612ad)."""
    m = PriceShapeModel.from_dict({"shapes": [[0.0] * 24, [1.0] * 24]})
    return all(_money_close(v, 1.0, 1e-9) for v in m.shapes[0])


def _pin_28de20de():
    """observe_day: Saturday folds into the weekend profile (28de20de)."""
    m = PriceShapeModel()
    m.observe_day(datetime(2026, 1, 10, 12), _MONEY_DAY)
    s = m.summary()
    return s["weekend_days"] == 1 and s["weekday_days"] == 0


class _MoneyResp:
    def __init__(self, status):
        self.status = status

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def json(self):
        raise RuntimeError("non-JSON body")


class _MoneySession:
    def __init__(self, status):
        self.status = status

    def post(self, *a, **k):
        return _MoneyResp(self.status)


def _money_pull(status):
    cfg = {price_model_mod.CONF_TIBBER_TOKEN: "tok"}
    return asyncio.run(price_model_mod.pull_prices(_MoneySession(status), cfg))


def _pin_e5eea05f():
    """pull_prices via _tibber_post: non-200 with an unreadable body gives reauth/fail (e5eea05f)."""
    return (_money_pull(401)[0] == "reauth" and _money_pull(403)[0] == "reauth"
            and _money_pull(502) == ("fail", "Tibber API error: 502"))


def _pin_0d159d7d():
    """extend_price_series: a model with no confidence repeats the last known price (0d159d7d)."""
    times = [datetime(2026, 1, 14, 12 + i) for i in range(6)]
    prices, mask, sigma = price_model_mod.extend_price_series(
        [1.0, 2.0, 3.0], 6, times, PriceShapeModel())
    return [float(x) for x in prices[3:]] == [3.0, 3.0, 3.0]


def _pin_b539d450():
    """prices_from_entity_state: unknown state with empty attributes is 'Price entity is empty' (b539d450)."""
    return all(
        price_model_mod.prices_from_entity_state(SimpleNamespace(state=s, attributes=a))
        == "Price entity is empty"
        for s in ("unknown", "unavailable", "")
        for a in ({}, (1,))
    )


def _money_pins() -> dict[str, bool]:
    return {
        "de935c38 non-finite window_factor keeps window": _money_safe(_pin_de935c38),
        "7fcaf91c non-finite/negative sample dropped": _money_safe(_pin_7fcaf91c),
        "3e9a439b zero stored peaks survive restart": _money_safe(_pin_3e9a439b),
        "9297f123 none/empty product no warning": _money_safe(_pin_9297f123),
        "911f3cf5 stale catalog row returns None": _money_safe(_pin_911f3cf5),
        "b5f0a732 max_abs tie labelled fixed": _money_safe(_pin_b5f0a732),
        "68cc141b min_component tie labelled fixed": _money_safe(_pin_68cc141b),
        "2043855e parse_rules None is empty": _money_safe(_pin_2043855e),
        "24604339 zero peaks_averaged marginal 0": _money_safe(_pin_24604339),
        "4ad3dc13 window_factor 0.0 kept": _money_safe(_pin_4ad3dc13),
        "37b3c9a0 undated peaks all kept": _money_safe(_pin_37b3c9a0),
        "6536ff6b smooth topk k<=0 is 0": _money_safe(_pin_6536ff6b),
        "5371ee2b smooth topk no positive is 0": _money_safe(_pin_5371ee2b),
        "2d037a10 realised_peak empty is 0": _money_safe(_pin_2d037a10),
        "5f094dbc smooth topk tiny plateau value": _money_safe(_pin_5f094dbc),
        "996dce51 smooth topk batch tiny plateau value": _money_safe(_pin_996dce51),
        "1894e6dc metering_windows empty stays empty": _money_safe(_pin_1894e6dc),
    
        "b9b6cf1d expected_daily_min guard": _money_safe(_pin_b9b6cf1d),
        "c4697335 shape seed on first day": _money_safe(_pin_c4697335),
        "3a064c11 summary weekday sigma": _money_safe(_pin_3a064c11),
        "efa02472 summary weekend sigma": _money_safe(_pin_efa02472),
        "28de20de saturday is weekend": _money_safe(_pin_28de20de),
        "e5eea05f tibber non-200 no json": _money_safe(_pin_e5eea05f),
        "0d159d7d zero-confidence flat tail": _money_safe(_pin_0d159d7d),
        "0ea7620c SHAPE_ALPHA": _money_safe(_pin_0ea7620c),
        "213a122a SHAPE_CONFIDENCE_DAYS": _money_safe(_pin_213a122a),
        "b10967dd SHAPE_MIN": _money_safe(_pin_b10967dd),
        "7e5493bc QUARTER_ALPHA": _money_safe(_pin_7e5493bc),
        "66686e3b QUARTER_CONFIDENCE_DAYS": _money_safe(_pin_66686e3b),
        "5bf50f5d QUARTER_FACTOR_MIN": _money_safe(_pin_5bf50f5d),
        "cc96ce9e QUARTER_FACTOR_MAX": _money_safe(_pin_cc96ce9e),
        "b5aef007 VAR_ALPHA": _money_safe(_pin_b5aef007),
        "a5c9796d five days trusted": _money_safe(_pin_a5c9796d),
        "13cadf1a residual var max kept": _money_safe(_pin_13cadf1a),
        "0b10a7c7 residual var seed": _money_safe(_pin_0b10a7c7),
        "4e79ba6e hour mean 1e-6 unusable": _money_safe(_pin_4e79ba6e),
        "12cd6ddd quarter seed": _money_safe(_pin_12cd6ddd),
        "a38612ad zero shape renormalised": _money_safe(_pin_a38612ad),
        "b539d450 empty attrs reason": _money_safe(_pin_b539d450),
    
    }


def main() -> int:
    R = Results("Guard pins (#805 non-coordinator)")
    R.check(
        "an idle interval teaches the tank cooling rate",
        _idle_cooling_learned(),
        "async_learn_cooling must run when the tank was not heated",
    )
    R.check(
        "a wood-coil install captions the hot-water tank",
        _coil_caption_present(),
    )
    R.check(
        "a tz-aware wood slot against naive stamps still places energy",
        _aware_slot_on_naive_stamps(),
        "aware-vs-naive comparison raises unless the stamp is stripped",
    )
    R.check(
        "a tenfold hour does not remain tenfold in the learned shape",
        _spike_rail_holds(),
        "the rail must flatten a data-error spike",
    )
    R.check(
        "a legionella run-up stops once the ordinary floor already covers it",
        _runup_stops_at_the_ordinary_floor(),
        "need <= floor_temps[m] must break the backward walk",
    )
    R.check(
        "a starting guess below a pinned bound is lifted to the bound",
        _pinned_guess_respects_the_lower_bound(),
        "the lower clamp of _seed_pinned_guess must bind",
    )
    R.check(
        "an unchanged ceiling signature does not re-raise the notice",
        _ceiling_notice_is_deduplicated(),
        "the signature guard in check_ceiling must stop the Repairs issue "
        "being re-created on every tick",
    )
    R.check(
        "a draw is folded, and skipped while external heat drives the tank",
        _draw_folded_only_without_external_heat(),
        "the _external_heat_active() guard in async_fold_draw_stats must "
        "skip exactly the wood-driven intervals",
    )
    R.check(
        "the disinfection write-failed notice is raised once and cleared once",
        _write_failed_notice_is_memoised(),
        "the write_failed_notice memo in _drive_switch must stop a Repairs "
        "call on every cycle whose state did not change",
    )
    for name, ok in _gchv_night_mode_pins().items():
        R.check(f"#1913 GCHV {name}", ok)
    for name, ok in _service_dispatch_pins().items():
        R.check(f"R9-SW-2 {name}", ok)
    for name, ok in _r10_arch_shapes_pins().items():
        R.check(f"R10-ARCH-SHAPES {name}", ok)
    for name, ok in _off_step_notice_pins().items():
        R.check(f"R10-DISINFECTION-STEP-NOTICE {name}", ok)
    for name, ok in _space_scope_caps_pins().items():
        R.check(f"R11-OUTSIDE-HONEST-STARTS-RUNS {name}", ok)
    # R11-D3-PINS-plant pins (#3755)
    for name, ok in _plant_pins().items():
        R.check(name, ok)
    for name, ok in _valve_batch_params_pins().items():
        R.check(name, ok)
    for name, ok in _money_pins().items():
        R.check(f"R11-D3-PINS-money {name}", ok)
    return R.close("GUARD PIN CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
