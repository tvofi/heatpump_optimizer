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

import asyncio
import sys
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import heatpump_optimizer.legionella as legionella_mod
from harness import FakeHass, FakeState, Results, UTC
from heatpump_optimizer.dhw_learning import DhwProfileLearner
from heatpump_optimizer.optimizer import _Horizon
from heatpump_optimizer.thermal_model import ThermalState
from heatpump_optimizer.disinfection import DisinfectionSwitch
from heatpump_optimizer.legionella import LegionellaGuard
from heatpump_optimizer.dhw_planner import DhwPlanner
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.price_model import PriceShapeModel
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
from heatpump_optimizer import topology
from heatpump_optimizer.wood_fuel import wood_slots_to_kw
from homeassistant.util import dt as dt_util


class _Learner(DhwProfileLearner):
    """The learner, with persistence stubbed so a cooling fold is visible."""

    def __init__(self) -> None:
        super().__init__(
            FakeHass(),
            "guard-pins",
            ThermalParameters(),
            frozen=lambda *_: None,
            heating_active=lambda: False,
            external_heat_active=lambda: False,
        )

    async def async_save_profile(self) -> None:
        return None


def _idle_cooling_learned() -> bool:
    now = datetime(2026, 1, 5, 12, 0, 0)
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
        c_dhw=max(params.dhw_tank_thermal_mass, 0.05),
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
            params,
            frozen=lambda *_: None,
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
        params,
        {},
        action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )
    calls: list[int] = []
    original = legionella_mod.create_issue
    legionella_mod.create_issue = lambda *a, **k: calls.append(1)
    try:
        guard.check_ceiling()
        guard.check_ceiling()
    finally:
        legionella_mod.create_issue = original
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
        ThermalParameters(),
        {},
        action=lambda: {},
        disinfect=DisinfectionSwitch({}, lambda *a, **k: None, lambda e: None),
        dhw_blocked=lambda: False,
    )

    async def _no_save() -> None:
        return None

    guard.async_save = _no_save
    calls: list[str] = []
    ir = legionella_mod.ir
    original = legionella_mod.create_issue, ir.async_delete_issue
    legionella_mod.create_issue = lambda *a, **k: calls.append(f"create {a[2]}")
    ir.async_delete_issue = lambda hass, dom, iid: calls.append(f"delete {iid}")
    try:
        # Observe mode, nothing owned: release writes nothing, so the
        # switch's sticky ``failed`` flag is what each cycle reports.
        for failed in (False, False, True, True, True, False, False):
            guard.disinfect.failed = failed
            guard.disinfect.failed_entity = "switch.disinfect" if failed else None
            asyncio.run(guard._drive_switch(False))
    finally:
        legionella_mod.create_issue, ir.async_delete_issue = original
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
            self._thermal_params = NS(dhw_setpoint=48.0)
            self._current_state = NS(outdoor_temperature=2.0)
            self.entry = NS(entry_id=f"gp{next(ids)}")
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
    restored_bool = pump_arbiter._writable("night_start_hour", True)
    restored_int = pump_arbiter._writable("night_start_hour", 22)
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
    silent switch turn_on/turn_off, a set-point ``_write_setpoint``'s
    set_value. ``tests/features.py`` holds the behaviour; this is the cheap
    driver the pin lane can finish.
    """
    from heatpump_optimizer import pump_arbiter

    class Coord:
        pass

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
    return R.close("GUARD PIN CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
