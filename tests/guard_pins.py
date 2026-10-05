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
from harness import FakeHass, Results
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
    return R.close("GUARD PIN CHECKS")


if __name__ == "__main__":
    raise SystemExit(main())
