"""Behavioural tests for the manual plan override (pinning when the pump runs).

These drive three layers directly, because the whole point of the feature is a
set of interactions no outcome assertion elsewhere would catch:

* ``manual_plan`` — parsing, the omitted-vs-empty distinction, expiry, and the
  serialisation a restart depends on. Home Assistant-free, so exercised bare.
* ``optimizer`` — that pins actually move the solved schedule, and that the
  safety release fires exactly when forcing a channel off would breach a hard
  floor (comfort, tank minimum, legionella) and stays quiet when it would not.
* ``coordinator`` — the persistence round-trip, discarding an expired plan on
  restore, dropping one that expires mid-flight, and that a rejected apply
  leaves an override already in force untouched.

Deliberately plain scripts, matching the rest of the suite. Run directly:

    PYTHONPATH=tests/hastub python tests/manual_plan.py
"""
from __future__ import annotations

import asyncio
import math
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

from harness import (
    FakeEntry,
    FakeHass,
    FakeState,
    Results,
    ha_setup_entry,
)
from profiles import solve_inputs  # noqa: E402

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

from profiles import house, prices, weather

import heatpump_optimizer as integ
import homeassistant.util.dt as dt_util
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.storage import _reset_store_disk
from homeassistant.util import dt as _dt_stub

from heatpump_optimizer.const import (
    CAPACITY_FLOOR_FRACTION,
    CONF_COMPRESSOR_FREQ_ENTITY,
    CONF_COMPRESSOR_FREQ_MAX_HZ,
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
    CONF_POWER_ENTITY,
    CONF_QUIET_OFF_WINDOWS,
    CONF_QUIET_SILENT_WINDOWS,
    CONF_SILENT_MODE_FRACTION,
    DEFAULT_SILENT_MODE_FRACTION,
    MANUAL_PLAN_WINDOW_HOURS,
)
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.dhw_planner import (
    _forced_off_with,
    _legionella_charge,
    _place_legionella_step,
)
from heatpump_optimizer import quiet_windows as _qw
from heatpump_optimizer.entry_config import EntryConfig
from heatpump_optimizer.sensor import MonthlyPeakSensor, _quiet_windows_attributes
from heatpump_optimizer.services import (
    _canonical_quiet_spec,
    _canonical_quiet_updates,
    _refuse_quiet,
)
from heatpump_optimizer.manual_plan import (
    CHANNEL_DHW,
    CHANNEL_SPACE,
    PIN_ON,
    ManualOverride,
    ManualPlanError,
    build_override,
    parse_channel,
)
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer,
    OptimizationConfig,
    REASON_LEGIONELLA,
    REASON_MANUAL,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

START = datetime(2026, 1, 15, 0, 0)
N = 96


def _slot(start_h: float, end_h: float, base: datetime = START) -> dict:
    return {
        "start": (base + timedelta(hours=start_h)).isoformat(),
        "end": (base + timedelta(hours=end_h)).isoformat(),
    }


def _build_optimizer(price_profile, weather_profile, dhw=True, **state_over):
    cfg = house()
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    opt = OptimizationConfig(
        horizon_hours=24,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    p = prices(price_profile, START)
    outdoor, wind, rain, solar = weather(weather_profile, START)
    base = dict(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    base.update(state_over)
    state = ThermalState(**base)
    opt_obj = HeatPumpOptimizer(ThermalModel(params), opt)
    return opt_obj, state, p, outdoor, wind, rain, solar


def _solve(bundle, **kwargs):
    opt_obj, state, p, outdoor, wind, rain, solar = bundle
    return opt_obj.optimize(inputs=solve_inputs(
        initial_state=state, prices=p, outdoor_temps=outdoor, wind_speeds=wind,
        precipitation=rain, solar_radiation=solar, start_time=START, **kwargs
    ))


def _last_planned_dhw(plan):
    """The last planned DHW run, and how many runs the plan has.

    The step this names is the one nothing downstream can be counting on, so
    forcing it off is the case the safety release must NOT fire for. Named
    rather than searched: a helper that tries every run until one happens to
    need no release proves only that some step somewhere was dispensable —
    which is nearly always true and says nothing about which — and it costs a
    full solve per rejected candidate. Naming it means a plan where even the
    last run has become load-bearing fails the check loudly instead of
    quietly moving on to another step.

    Hard-coding an index instead is what this replaces: v5.1.5's `active[0]`
    stopped being dispensable once the charge limit, rather than the
    disinfection temperature, set how much slack a summer plan carries.
    """
    powers = np.asarray(plan.dhw_power_schedule)
    runs = [j for j, v in enumerate(powers) if v > 0.01]
    return (runs[-1] if runs else None), len(runs)


def _last_safe_dhw_off(bundle, plan):
    """Force the last planned DHW run off, and solve once."""
    k, _n = _last_planned_dhw(plan)
    if k is None:
        return None, None
    off = np.full(N, np.nan)
    off[k] = 0.0
    return k, _solve(bundle, dhw_pins=off)


def _mk_coordinator() -> HeatPumpOptimizerCoordinator:
    return HeatPumpOptimizerCoordinator(
        FakeHass(),
        FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"}),
    )


# ---------------------------------------------------------------------------


def test_parsing(R: Results) -> None:
    R.section("Slot parsing and validation")
    ref = START

    R.check(
        "omitted channel stays None (fully automatic)",
        parse_channel(None, ref) is None,
    )
    R.check(
        "explicit empty list stays [] (off for the whole period)",
        parse_channel([], ref) == [],
    )

    parsed = parse_channel([_slot(6, 8), _slot(2, 3)], ref)
    R.check(
        "slots are sorted by start time",
        parsed is not None and parsed[0][0] < parsed[1][0],
    )

    def rejects(name, raw, **kw):
        try:
            if "expires_at" in kw:
                build_override(
                    dhw_slots=None,
                    space_slots=raw,
                    expires_at=kw["expires_at"],
                    now=ref,
                )
            else:
                parse_channel(raw, ref)
        except ManualPlanError:
            R.check(name, True)
        else:
            R.check(name, False, "no ManualPlanError raised")

    rejects("rejects end == start", [_slot(3, 3)])
    rejects("rejects end < start", [_slot(4, 3)])
    rejects("rejects overlapping slots", [_slot(2, 5), _slot(4, 6)])
    rejects("rejects unparseable datetime", [{"start": "not-a-date", "end": "x"}])
    rejects("rejects a non-object slot", ["06:00-08:00"])
    rejects(
        "rejects expires_at in the past",
        None,
        expires_at=ref - timedelta(hours=1),
    )

    R.check("ManualPlanError is a ValueError", issubclass(ManualPlanError, ValueError))


def test_channel_semantics(R: Results) -> None:
    R.section("Channel pin semantics")
    now = START
    expires = START + timedelta(hours=6)
    step_starts = [START + timedelta(hours=i * 0.25) for i in range(N)]

    # Space omitted, DHW pinned to 02:00-03:00.
    ov = build_override(
        dhw_slots=[_slot(2, 3)],
        space_slots=None,
        expires_at=expires,
        now=now,
    )
    space_pins = ov.channel_pins(CHANNEL_SPACE, step_starts)
    dhw_pins = ov.channel_pins(CHANNEL_DHW, step_starts)
    R.check("omitted channel yields no pins", space_pins is None)
    R.check("supplied channel yields a pin array", dhw_pins is not None)
    on = [i for i, v in enumerate(dhw_pins) if v == 1.0]
    R.check("pins on inside the slot", on == [8, 9, 10, 11])
    R.check(
        "pins off outside the slot but before expiry",
        dhw_pins[0] == 0.0 and dhw_pins[7] == 0.0,
    )
    R.check(
        "free at and beyond expiry",
        all(v != v for v in dhw_pins[24:]),  # NaN past 6h
    )
    R.check("pinned_step_count counts the on steps", ov.pinned_step_count(CHANNEL_DHW, step_starts) == 4)

    # Empty list means off for the whole period, never free before expiry.
    off = build_override(
        dhw_slots=[], space_slots=None, expires_at=expires, now=now
    )
    off_pins = off.channel_pins(CHANNEL_DHW, step_starts)
    R.check(
        "empty list forces off up to expiry",
        all(off_pins[i] == 0.0 for i in range(24)),
    )
    R.check(
        "empty list still frees steps past expiry",
        all(v != v for v in off_pins[24:]),
    )

    # Overlap, not start-containment: the solve anchor snaps to the quarter
    # grid, so a service call's "from now" slot starts mid-step. Judging
    # only the step's start turned that command into a force-OFF of the
    # very step it landed in — a boost that switched the channel off.
    mid = build_override(
        dhw_slots=[_slot(7.5 / 60.0, 1.0 + 7.5 / 60.0)],
        space_slots=None,
        expires_at=expires,
        now=now,
    )
    mid_pins = mid.channel_pins(CHANNEL_DHW, step_starts)
    R.check(
        "a slot starting mid-step pins the step it lands in ON",
        mid_pins[0] == 1.0,
        f"step 0 pin = {mid_pins[0]}",
    )
    R.check(
        "and the partially covered trailing step stays ON too",
        [i for i, v in enumerate(mid_pins) if v == 1.0] == [0, 1, 2, 3, 4],
        f"on steps = {[i for i, v in enumerate(mid_pins) if v == 1.0]}",
    )
    # Grid-aligned slots — everything the card produces — are untouched:
    # overlap and containment agree exactly there (asserted above by the
    # 02:00-03:00 slot's [8, 9, 10, 11]).


def test_serialization(R: Results) -> None:
    R.section("Serialisation round-trip")
    now = START
    expires = START + timedelta(hours=8)
    ov = build_override(
        dhw_slots=[_slot(2, 3)],
        space_slots=[],
        expires_at=expires,
        now=now,
    )
    restored = ManualOverride.from_dict(ov.to_dict())
    R.check(
        "space channel empty-list survives the round-trip",
        restored.space_slots == [],
    )
    R.check(
        "dhw channel slots survive the round-trip",
        restored.dhw_slots is not None and len(restored.dhw_slots) == 1,
    )
    R.check("expiry survives the round-trip", restored.expires_at == expires)

    try:
        ManualOverride.from_dict({"space_slots": None})
    except ManualPlanError:
        R.check("from_dict rejects a missing expiry", True)
    else:
        R.check("from_dict rejects a missing expiry", False)


def test_pins_change_schedule(R: Results) -> None:
    R.section("Pins change the solved schedule")

    # Forcing space heating ON at an expensive morning step the optimizer would
    # otherwise skip must add a real run there and label it manual.
    winter = _build_optimizer("winter_typical", "winter_cold")
    base = _solve(winter)
    sp = np.full(N, np.nan)
    sp[36] = 1.0
    pinned = _solve(winter, space_pins=sp)
    R.check(
        "forcing space on adds a run the optimizer skipped",
        base.power_schedule[36] < 0.05 and pinned.power_schedule[36] > 0.5,
        f"base={base.power_schedule[36]:.3f} pinned={pinned.power_schedule[36]:.3f}",
    )
    R.check(
        "a manual-on step is labelled manual_plan",
        pinned.space_reasons[36] == REASON_MANUAL,
    )
    R.check("the override is flagged active", pinned.manual_pins_active)

    # Forcing hot water ON in a step the plan skipped adds DHW power there.
    # The step is picked from the plan, not hard-coded: a pin can only add a
    # run where the tank has room for one, and since v5.1.10 "room" is measured
    # against the user's charge limit rather than the disinfection
    # temperature, so an evening tank runs out of headroom sooner.
    _base_dhw = np.asarray(base.dhw_power_schedule)
    _base_tank = np.asarray(base.dhw_temp_trajectory)
    _ceiling = winter[0].model.params.dhw_max_temp
    _on_idx = next(
        i
        for i in range(N)
        if _base_dhw[i] < 0.05 and _base_tank[i] < _ceiling - 2.0
    )
    dp = np.full(N, np.nan)
    dp[_on_idx] = 1.0
    pinned_dhw = _solve(winter, dhw_pins=dp)
    R.check(
        "forcing hot water on adds a DHW run",
        base.dhw_power_schedule[_on_idx] < 0.05
        and pinned_dhw.dhw_power_schedule[_on_idx] > 0.3,
        f"step {_on_idx}: {base.dhw_power_schedule[_on_idx]:.3f} -> "
        f"{pinned_dhw.dhw_power_schedule[_on_idx]:.3f}",
    )
    R.check(
        "a manual DHW step is labelled manual_plan",
        pinned_dhw.dhw_reasons[_on_idx] == REASON_MANUAL,
    )

    # Forcing hot water OFF when it is safe (hot tank in summer) removes a run.
    summer = _build_optimizer(
        "summer_typical", "summer_warm", dhw_temperature=54.0
    )
    sbase = _solve(summer)
    k, pinned_off = _last_safe_dhw_off(summer, sbase)
    _, nruns = _last_planned_dhw(sbase)
    R.check(
        "the summer plan has several runs, so the last one is a real choice",
        nruns >= 2,
        f"{nruns} planned DHW runs",
    )
    R.check(
        "forcing hot water off removes a run when safe",
        k is not None
        and sbase.dhw_power_schedule[k] > 0.1
        and pinned_off.dhw_power_schedule[k] < 0.01,
        f"step {k}",
    )
    R.check(
        "a safe forced-off step is not released",
        k is not None and not pinned_off.manual_released_dhw,
        f"step {k} released {getattr(pinned_off, 'manual_released_dhw', None)}",
    )


def test_off_window_over_pins(R: Results) -> None:
    R.section("A quiet Off window outranks a force-on pin (#1910)")

    # The one place the Off mask is fitted to the horizon: a short mask is
    # padded False and, with nothing else forced off, is the whole result.
    try:
        fitted = _forced_off_with(None, [True, False], 4)
    except TypeError as err:
        fitted = err
    R.check(
        "an Off mask shorter than the horizon is padded off-free to its length",
        isinstance(fitted, np.ndarray)
        and fitted.tolist() == [True, False, False, False],
        f"got {fitted!r}",
    )
    merged = _forced_off_with(np.array([False, True, False, False]), [True], 4)
    R.check(
        "an Off mask is OR'd into the steps pins already forced off",
        isinstance(merged, np.ndarray)
        and merged.tolist() == [True, True, False, False],
        f"got {merged!r}",
    )

    # A force-on pin inside the window must not reopen it: the overlay runs
    # after the planners, so only the restated invariant keeps the steps
    # empty. The pinned step is one the pin alone does fill (the null
    # control), so the zeros are the window's.
    winter = _build_optimizer("winter_typical", "winter_cold")
    base = _solve(winter)
    _base_dhw = np.asarray(base.dhw_power_schedule)
    _base_tank = np.asarray(base.dhw_temp_trajectory)
    _ceiling = winter[0].model.params.dhw_max_temp
    _on_idx = next(
        i
        for i in range(2, N - 2)
        if _base_dhw[i] < 0.05 and _base_tank[i] < _ceiling - 2.0
    )
    dp = np.full(N, np.nan)
    dp[_on_idx] = 1.0
    off = np.zeros(N, dtype=bool)
    off[_on_idx - 2 : _on_idx + 2] = True
    free = _solve(winter, dhw_pins=dp.copy())
    held = _solve(winter, dhw_pins=dp.copy(), off_steps=off)
    in_window = np.asarray(held.dhw_power_schedule)[off]
    R.check(
        "a force-on hot-water pin inside an Off window plans nothing in its steps",
        free.dhw_power_schedule[_on_idx] > 0.3 and float(np.max(in_window)) == 0.0,
        f"step {_on_idx}: pin alone {free.dhw_power_schedule[_on_idx]:.3f}, "
        f"inside the window {float(np.max(in_window)):.3f}",
    )


def _legionella_steps(plan) -> list[int]:
    """Steps whose reason is the anti-legionella cycle itself."""
    return [i for i, reason in enumerate(plan.dhw_reasons) if reason == REASON_LEGIONELLA]


def test_legionella_outside_off_window(R: Results) -> None:
    """An Off window must not delete an anti-legionella cycle placed in it (#1910).

    The cycle is due (200 h since the last one, interval 7 days) on a 50 °C
    tank whose disinfection target is 60 °C. With no window the plan puts the
    cycle at step 1. A window over that step used to zero the slot and leave
    the tank at the everyday ceiling; the cycle has to be bought on a step
    the window leaves free. A window that does not cover step 1 leaves the
    cycle there, and still buys no hot water inside itself.
    """
    R.section("An Off window plans the anti-legionella cycle outside itself (#1910)")
    winter = _build_optimizer(
        "winter_typical", "winter_cold", dhw_hours_since_legionella=200.0,
    )
    params = winter[0].model.params
    bare = _solve(winter)
    bare_steps = _legionella_steps(bare)
    bare_max = float(np.max(bare.dhw_temp_trajectory))
    R.check(
        "with no Off window the overdue cycle is at step 1 and the tank reaches 60 C",
        params.dhw_legionella_temp == 60.0
        and params.dhw_legionella_interval_days == 7.0
        and winter[1].dhw_temperature == 50.0
        and bare_steps == [1]
        and bare_max == 60.0,
        f"steps {bare_steps} max {bare_max} "
        f"target {params.dhw_legionella_temp} interval {params.dhw_legionella_interval_days}",
    )

    cover = np.zeros(N, dtype=bool)
    cover[0:3] = True
    covered = _solve(winter, off_steps=cover)
    covered_steps = _legionella_steps(covered)
    covered_max = float(np.max(covered.dhw_temp_trajectory))
    covered_in = float(np.max(np.asarray(covered.dhw_power_schedule)[cover]))
    R.check(
        "an Off window covering the placed step plans the cycle outside it",
        bool(covered_steps)
        and all(not cover[i] for i in covered_steps)
        and covered_in == 0.0
        and covered_max == params.dhw_legionella_temp,
        f"steps {covered_steps} in-window DHW {covered_in} max {covered_max}",
    )

    elsewhere = np.zeros(N, dtype=bool)
    elsewhere[40:52] = True
    left = _solve(winter, off_steps=elsewhere)
    left_steps = _legionella_steps(left)
    left_max = float(np.max(left.dhw_temp_trajectory))
    left_in = float(np.max(np.asarray(left.dhw_power_schedule)[elsewhere]))
    R.check(
        "an Off window elsewhere leaves the cycle at step 1 and buys no hot water inside it",
        left_steps == [1] and left_max == 60.0 and left_in == 0.0,
        f"steps {left_steps} in-window DHW {left_in} max {left_max}",
    )

    # The overdue cycle's window is one step, so the reach simulation is what
    # moves it. A deadline that still has hours left shops the cheapest step
    # in that span, and an elastic cycle shops the horizon: both can land on
    # an Off step the reach never needed. Step 10 is made strictly cheapest
    # so the placement is that step and not the tied night price.
    def cheap(hours: float):
        bundle = _build_optimizer(
            "winter_typical", "winter_cold", dhw_hours_since_legionella=hours,
        )
        opt, state, priced, outdoor, wind, rain, solar = bundle
        priced = np.array(priced, dtype=float)
        priced[10] = 0.01
        return (opt, state, priced, outdoor, wind, rain, solar)

    def outside(bundle, index: int, name: str) -> None:
        bare_at = _legionella_steps(_solve(bundle))
        mask = np.zeros(N, dtype=bool)
        mask[index] = True
        moved = _solve(bundle, off_steps=mask)
        moved_at = _legionella_steps(moved)
        moved_in = float(np.max(np.asarray(moved.dhw_power_schedule)[mask]))
        R.check(
            name,
            bare_at == [index]
            and moved_at == [1]
            and moved_in == 0.0
            and float(np.max(moved.dhw_temp_trajectory)) == 60.0,
            f"bare {bare_at} moved {moved_at} in-window DHW {moved_in} "
            f"max {float(np.max(moved.dhw_temp_trajectory))}",
        )

    outside(
        cheap(158.0), 10,
        "an Off window on the deadline's cheap hour plans the cycle elsewhere",
    )
    elastic = cheap(140.0)
    elastic[0].model.params.dhw_elastic_legionella_enabled = True
    elastic[0].model.params.dhw_legionella_price_ceiling = float(
        np.max(elastic[2])
    )
    outside(
        elastic, 10,
        "an elastic cycle shops the hour outside an Off window",
    )


def test_legionella_arms_a_solve_horizon_never_builds(R: Results) -> None:
    """The Off-window arms a solve's horizon does not build (#1910).

    A placement slice that is entirely off still has a later free step, or
    it does not. A charge with no window is the other arm: every step runs.
    """
    R.section("Legionella placement when the slice is entirely off (#1910)")
    prices = np.array([9.0, 8.0, 7.0, 0.2, 3.0])
    covered = np.array([True, True, True, False, True])
    placed = _place_legionella_step(prices, 0, 3, covered)
    R.check(
        "a slice the Off window covers entirely is bought at the next free step",
        placed == 3,
        f"got {placed}",
    )
    blocked = np.ones(5, dtype=bool)
    blocked[0] = False
    nowhere = _place_legionella_step(prices, 1, 4, blocked)
    R.check(
        "no free step left places no anti-legionella cycle",
        nowhere is None,
        f"got {nowhere}",
    )
    open_charge = _legionella_charge(4, 1.5, None)
    R.check(
        "no Off window charges every step of the reach",
        isinstance(open_charge, np.ndarray) and bool(np.allclose(open_charge, 1.5)),
        f"got {open_charge!r}",
    )
    masked = _legionella_charge(4, 1.5, np.array([True, False, True, False]))
    R.check(
        "an Off step contributes nothing to the reach",
        isinstance(masked, np.ndarray)
        and bool(np.allclose(masked, [0.0, 1.5, 0.0, 1.5])),
        f"got {masked!r}",
    )


class _QuietCoord:
    def __init__(self, specs: dict) -> None:
        self._specs = specs

    def configured_quiet_windows(self) -> dict:
        return self._specs

    @property
    def effective_config(self) -> EntryConfig:
        return EntryConfig()


class _PowerState:
    def __init__(self, state: str, unit: str | None = "W") -> None:
        self.state = state
        self.attributes = {} if unit is None else {"unit_of_measurement": unit}


def _quiet_get(mapping: dict):
    def get_state(entity_id):
        if not isinstance(entity_id, str):
            raise TypeError(entity_id)
        return mapping.get(entity_id)
    return get_state


def test_quiet_window_arms(R: Results) -> None:
    """The quiet-window arms a full solve never reaches (#1910).

    Each check is the value the production function returns on a degenerate
    or boundary input. A guard deleted, a bound widened, or a return
    removed changes that value or raises; the count drive's survivors are
    the arms these inputs are the first to name.
    """
    R.section("Quiet-window arms the solve does not reach (#1910)")
    start = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)

    def call(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (TypeError, ValueError, ZeroDivisionError, AttributeError) as err:
            return err

    neg = call(_qw.step_actions, start, -1, 0.25, "01:00-02:00", "")
    R.check(
        "a negative horizon is no actions, not an error",
        neg is None,
        f"got {neg!r}",
    )
    R.check(
        "a zero horizon is no actions",
        _qw.step_actions(start, 0, 0.25, "01:00-02:00", "") is None,
    )
    bad = call(_qw.step_actions, start, 4, 0.25, "not-a-window", "")
    R.check(
        "an unreadable spec is no actions",
        bad is None,
        f"got {bad!r}",
    )
    R.check(
        "a non-string control and a switch control are domain verdicts",
        _qw.silent_control_usable(None) is False
        and _qw.silent_control_usable("not-an-entity") is False
        and _qw.silent_control_usable("switch.night") is True,
    )
    missing = call(_qw._power_entity_kw, "sensor.hp", lambda _e: None)
    R.check(
        "a power entity with no state is no reading",
        missing is None,
        f"got {missing!r}",
    )
    zero_kw = call(
        _qw._power_entity_kw, "sensor.hp",
        _quiet_get({"sensor.hp": _PowerState("0", "W")}),
    )
    R.check(
        "a zero power reading is no reading",
        zero_kw is None,
        f"got {zero_kw!r}",
    )
    bad_unit = call(
        _qw._power_entity_kw, "sensor.hp",
        _quiet_get({"sensor.hp": _PowerState("3500", "furlong")}),
    )
    R.check(
        "an unrecognised power unit is no reading",
        bad_unit is None,
        f"got {bad_unit!r}",
    )
    R.check(
        "no state callable and a non-positive nameplate measure nothing",
        _qw.measured_ceiling_kw({CONF_POWER_ENTITY: "sensor.hp"}, None, 5.0) is None
        and call(
            _qw.measured_ceiling_kw,
            {CONF_POWER_ENTITY: "sensor.hp"},
            _quiet_get({"sensor.hp": _PowerState("3500", "W")}),
            0.0,
        ) is None,
    )
    odd_id = call(
        _qw.measured_ceiling_kw,
        {CONF_POWER_ENTITY: 12},
        _quiet_get({}),
        5.0,
    )
    R.check(
        "a non-string power entity id is not read",
        odd_id is None,
        f"got {odd_id!r}",
    )
    hz_zero = call(
        _qw.measured_ceiling_kw,
        {
            CONF_COMPRESSOR_FREQ_SENSOR: "sensor.hz",
            CONF_COMPRESSOR_FREQ_MAX_HZ: 120.0,
        },
        _quiet_get({"sensor.hz": _PowerState("0", None)}),
        5.0,
    )
    R.check(
        "a zero hertz reading measures nothing",
        hz_zero is None,
        f"got {hz_zero!r}",
    )
    _hz_number = _PowerState("40", None)
    _hz_number.attributes = {"min": 0.0, "max": 0.0}
    hz_ceiling = call(
        _qw.measured_ceiling_kw,
        {CONF_COMPRESSOR_FREQ_ENTITY: "number.hz"},
        _quiet_get({"number.hz": _hz_number}),
        5.0,
    )
    R.check(
        "a frequency entity whose range max is zero measures nothing",
        hz_ceiling is None,
        f"got {hz_ceiling!r}",
    )
    R.check(
        "a non-positive nameplate has no silent cap, and fraction 1.0 caps nothing",
        _qw.silent_cap_kw({CONF_SILENT_MODE_FRACTION: 0.7}, None, 0.0) is None
        and _qw.silent_cap_kw({CONF_SILENT_MODE_FRACTION: 0.7}, None, -1.0) is None
        and _qw.silent_cap_kw({CONF_SILENT_MODE_FRACTION: 1.0}, None, 5.0) is None,
    )
    floored = _qw.silent_cap_kw(
        {CONF_POWER_ENTITY: "sensor.hp", CONF_SILENT_MODE_FRACTION: 0.3},
        _quiet_get({"sensor.hp": _PowerState("1000", "W")}),
        5.0,
    )
    R.check(
        "a measured figure below the floor is raised to the floor",
        floored is not None
        and abs(floored - CAPACITY_FLOOR_FRACTION * 5.0) < 1e-9,
        f"got {floored!r}",
    )
    fraction_cap = _qw.silent_cap_kw({CONF_SILENT_MODE_FRACTION: 0.7}, None, 5.0)
    R.check(
        "the configured fraction is the cap when nothing is measured",
        fraction_cap is not None and abs(fraction_cap - 3.5) < 1e-9,
        f"got {fraction_cap!r}",
    )
    at_nameplate = _qw.compose(
        None,
        {
            CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.n",
            CONF_QUIET_SILENT_WINDOWS: "00:00-01:00",
            CONF_POWER_ENTITY: "sensor.hp",
        },
        _quiet_get({"sensor.hp": _PowerState("5000", "W")}),
        start, 4, 0.25, 5.0,
    )
    R.check(
        "a measured ceiling equal to nameplate does not install a cap array",
        at_nameplate.caps is None,
        f"caps {at_nameplate.caps!r}",
    )
    dropped = call(
        _qw.compose,
        None,
        {
            CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.n",
            CONF_QUIET_SILENT_WINDOWS: "00:00-01:00",
            CONF_SILENT_MODE_FRACTION: 1.0,
        },
        _quiet_get({}),
        start, 4, 0.25, 5.0,
    )
    R.check(
        "fraction 1.0 resolves the rows and installs no cap",
        not isinstance(dropped, Exception)
        and dropped.caps is None
        and dropped.actions is not None,
        f"got {dropped!r}",
    )
    unreachable = call(
        _qw.compose,
        None,
        {
            CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.n",
            CONF_QUIET_SILENT_WINDOWS: "03:00-04:00",
        },
        _quiet_get({}),
        start, 4, 0.25, 5.0,
    )
    R.check(
        "a window the horizon never reaches leaves the caller's cap alone",
        not isinstance(unreachable, Exception) and unreachable.caps is None,
        f"got {unreachable!r}",
    )
    extra = np.full(4, 4.0)
    folded = _qw.compose(
        extra,
        {
            CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "switch.n",
            CONF_QUIET_SILENT_WINDOWS: "00:00-01:00",
            CONF_SILENT_MODE_FRACTION: 0.5,
        },
        _quiet_get({}),
        start, 4, 0.25, 5.0,
    )
    R.check(
        "a silent cap is the elementwise minimum with the caller's extra cap",
        folded.caps is not None
        and abs(float(folded.caps[0]) - CAPACITY_FLOOR_FRACTION * 5.0) < 1e-9
        and float(folded.caps[0]) < float(extra[0]),
        f"caps {None if folded.caps is None else folded.caps.tolist()}",
    )
    folded_frac = _qw.overridden_config(
        {"a": 1}, {CONF_SILENT_MODE_FRACTION: 0.4},
    )
    R.check(
        "a what-if fraction off the default is folded into the config",
        folded_frac.get(CONF_SILENT_MODE_FRACTION) == 0.4
        and folded_frac.get("a") == 1,
        f"got {folded_frac!r}",
    )
    folded_key = _qw.overridden_config(
        {"a": 1}, {CONF_QUIET_SILENT_WINDOWS: "01:00-02:00"},
    )
    R.check(
        "a what-if spec key is folded and an absent one is not",
        folded_key.get(CONF_QUIET_SILENT_WINDOWS) == "01:00-02:00"
        and "a" in folded_key
        and _qw.overridden_config({"a": 1}, {}) == {"a": 1},
        f"got {folded_key!r}",
    )
    empty_pair = _qw._parse_spec_pair("", "")
    one_pair = _qw._parse_spec_pair("", "08:00-09:00")
    R.check(
        "two empty specs parse as nothing; one empty spec does not drop the other",
        empty_pair is None and one_pair is not None and one_pair[1][0],
        f"empty {empty_pair!r}, one {one_pair!r}",
    )
    R.check(
        "windows that only touch at an endpoint do not overlap, from either side",
        _qw._overlaps((1.0, 2.0), (2.0, 3.0)) is False
        and _qw._overlaps((2.0, 3.0), (1.0, 2.0)) is False,
    )
    R.check(
        "an off window overlapping a silent window is refused even with no hot water",
        _qw.overlap_problem("06:00-07:30", "05:00-07:00", "") is not None,
    )
    R.check(
        "an off window overlapping hot water is refused",
        _qw.overlap_problem("", "05:00-07:00", "06:00-08:30") is not None,
    )
    weekly = _canonical_quiet_spec("weekdays 08:00-09:00")
    R.check(
        "a weekly quiet spec keeps its day selector through canonicalisation",
        "weekdays" in weekly and "08:00" in weekly,
        f"got {weekly!r}",
    )
    updates = call(_canonical_quiet_updates, {})
    one_update = call(
        _canonical_quiet_updates, {CONF_QUIET_OFF_WINDOWS: "08:00-09:00"},
    )
    R.check(
        "absent quiet specs canonicalise to nothing, and a present one round-trips",
        updates == {}
        and isinstance(one_update, dict)
        and "08:00" in one_update.get(CONF_QUIET_OFF_WINDOWS, ""),
        f"empty {updates!r}, one {one_update!r}",
    )
    try:
        _refuse_quiet(
            {CONF_QUIET_OFF_WINDOWS: "05:00-07:00"},
            "apply_schedule_invalid_quiet_windows",
            "", "", "06:00-08:30",
        )
        refused = False
    except ServiceValidationError:
        refused = True
    R.check(
        "a service call whose off window overlaps hot water is refused",
        refused,
    )

    opt = _build_optimizer("winter_typical", "winter_cold")[0]
    off = np.zeros(8, dtype=bool)
    off[1:3] = True
    _throttling, caps, _extra = opt._build_space_power_caps(8, None, False, off)
    R.check(
        "an Off mask with no other cap still zeroes exactly its own space steps",
        caps is not None and np.array_equal(caps[off] == 0.0, np.ones(2))
        and float(np.min(caps[~off])) > 0.0,
        f"caps {None if caps is None else np.asarray(caps).tolist()}",
    )

    specs = {
        "quiet_silent_windows_spec": "22:00-06:00",
        "quiet_off_windows_spec": "",
        "quiet_silent_not_enforced": "true",
    }
    published = _quiet_windows_attributes(
        _QuietCoord(specs),
        {"predictive_info": {"quiet_actions": [0, 2, 2]}},
    )
    R.check(
        "the plan sensor publishes the not-enforced marker and the resolved actions",
        published.get("quiet_silent_not_enforced") is True
        and published.get("quiet_actions") == [0, 2, 2],
        f"got {published!r}",
    )
    # The sensor check above feeds a stub, so it never executes
    # configured_specs. This one calls that function: deleting its return
    # makes the check fail.
    produced = _qw.configured_specs({
        CONF_QUIET_SILENT_WINDOWS: "22:00-06:00",
        CONF_QUIET_OFF_WINDOWS: "09:00-09:30",
        CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: "binary_sensor.gchv_night",
    })
    R.check(
        "configured_specs returns the stored rows and the not-enforced marker",
        produced == {
            "quiet_silent_windows_spec": "22:00-06:00",
            "quiet_off_windows_spec": "09:00-09:30",
            "quiet_silent_not_enforced": "true",
        },
        f"got {produced!r}",
    )
    peak_coord = _mk_coordinator()
    peak_coord.data = {
        "peak_month": "2026-01",
        "peak_threshold_kw": 3.0,
        "projected_peak_kw": 2.0,
        "projected_peak_cost": 10.0,
        "billed_peak_kw": 4.0,
        "fuse_advisor": {"ok": 1},
    }
    peak_attrs = MonthlyPeakSensor(peak_coord, FakeEntry(data={})).extra_state_attributes
    R.check(
        "the monthly peak sensor publishes the tariff fields it was given",
        isinstance(peak_attrs, dict)
        and peak_attrs.get("month") == "2026-01"
        and peak_attrs.get("fuse_advisor") == {"ok": 1},
        f"got {peak_attrs!r}",
    )
    # The default fraction is the one the fold must treat as unset.
    R.check(
        "the default silent fraction is the unset value the fold compares against",
        DEFAULT_SILENT_MODE_FRACTION == 1.0,
    )


def test_safety_release(R: Results) -> None:
    R.section("Safety release fires only when a hard floor binds")

    # Space: a cold winter house forced fully off must be rescued — the comfort
    # floor is a soft penalty, so only the release actually protects it.
    winter = _build_optimizer("winter_typical", "winter_cold")
    pinned = _solve(winter, space_pins=np.zeros(N))
    R.check(
        "forcing space off in the cold releases pins for the comfort floor",
        len(pinned.manual_released_space) > 0,
    )
    R.check(
        "released space steps actually run again",
        sum(pinned.power_schedule) > 1.0,
    )

    # Space: a warm summer house needs no space heating, so forcing it off must
    # NOT trigger a release.
    summer = _build_optimizer(
        "summer_typical", "summer_warm", room_temperature=23.0, dhw_temperature=54.0
    )
    quiet = _solve(summer, space_pins=np.zeros(N))
    R.check(
        "forcing space off when it is not needed releases nothing",
        len(quiet.manual_released_space) == 0,
    )

    # DHW: a low tank forced off must be released to protect the tank minimum.
    low_tank = _build_optimizer(
        "winter_typical", "winter_cold", dhw_temperature=40.0
    )
    tank = _solve(low_tank, dhw_pins=np.zeros(N))
    R.check(
        "forcing hot water off with a low tank releases pins",
        len(tank.manual_released_dhw) > 0 and sum(tank.dhw_power_schedule) > 0.1,
    )

    # DHW: a due legionella cycle must survive being forced off even when the
    # tank is otherwise warm enough for daily use.
    legio = _build_optimizer(
        "winter_typical",
        "winter_cold",
        dhw_temperature=50.0,
        dhw_hours_since_legionella=200.0,
    )
    base = _solve(legio)
    legio_steps = [i for i, r in enumerate(base.dhw_reasons) if r == REASON_LEGIONELLA]
    forced = _solve(legio, dhw_pins=np.zeros(N))
    R.check(
        "a due legionella cycle is released when forced off",
        len(legio_steps) > 0
        and any(s in forced.manual_released_dhw for s in legio_steps),
    )

    # DHW: a hot summer tank forced off for a single step needs no release.
    summer_dhw = _build_optimizer(
        "summer_typical", "summer_warm", dhw_temperature=54.0
    )
    sbase = _solve(summer_dhw)
    _k, quiet_dhw = _last_safe_dhw_off(summer_dhw, sbase)
    R.check(
        "forcing hot water off when the tank is hot releases nothing",
        quiet_dhw is not None and len(quiet_dhw.manual_released_dhw) == 0,
        f"step {_k}",
    )


def test_naive_expiry(R: Results) -> None:
    R.section("A timezone-less expiry is handled, not crashed on")

    # The service UI's expires_at field is free text, so a user typing
    # "2026-08-23T06:00:00" produces a naive datetime while `now` is aware.
    # Coercing each operand towards the other gives them opposite awareness and
    # the comparison raises TypeError -- which is not a ManualPlanError, so it
    # escapes the service handler as an opaque crash instead of a clear message.
    # An explicitly aware `now`: real Home Assistant hands out aware local
    # times, while the test stub's clock is naive, and it is precisely the
    # aware-now/naive-expiry pairing that raises.
    now = dt_util.now().replace(tzinfo=timezone(timedelta(hours=2)))
    naive_expiry = (now + timedelta(hours=9)).replace(tzinfo=None)
    slot_start = now + timedelta(hours=1)
    slot_end = now + timedelta(hours=2)

    try:
        override = build_override(
            dhw_slots=[{
                "start": slot_start.isoformat(),
                "end": slot_end.isoformat(),
            }],
            space_slots=None,
            expires_at=naive_expiry,
            now=now,
        )
        built = True
        error = ""
    except TypeError as err:  # pragma: no cover - the bug being guarded
        override = None
        built = False
        error = f"raised TypeError: {err}"

    R.check("a naive expiry does not raise TypeError", built, error)

    if override is not None:
        # The stored expiry has to be comparable with the slots, which were
        # parsed against an aware `now` -- otherwise every later refresh raises
        # inside channel_pins instead, which is worse than failing up front.
        try:
            override.expires_at > override.dhw_slots[0][0]
            comparable = True
            detail = ""
        except TypeError as err:  # pragma: no cover - the bug being guarded
            comparable = False
            detail = f"raised TypeError: {err}"
        R.check(
            "the stored expiry is comparable with the parsed slots",
            comparable,
            detail,
        )
        try:
            pins = override.channel_pins(
                CHANNEL_DHW,
                [now + timedelta(minutes=15 * i) for i in range(8)],
            )
            usable = pins is not None and any(p == PIN_ON for p in pins)
            detail = ""
        except TypeError as err:  # pragma: no cover - the bug being guarded
            usable = False
            detail = f"raised TypeError: {err}"
        R.check("and the override can still be applied to the horizon", usable, detail)

    # A naive expiry in the past must still be rejected cleanly.
    stale = (now - timedelta(hours=1)).replace(tzinfo=None)
    try:
        build_override(
            dhw_slots=None, space_slots=None, expires_at=stale, now=now
        )
        rejected = False
    except ManualPlanError:
        rejected = True
    except TypeError:  # pragma: no cover - the bug being guarded
        rejected = False
    R.check("a naive expiry in the past is rejected as a plan error", rejected)


def test_give_up_is_per_channel(R: Results) -> None:
    R.section("Abandoning an unsafe plan does not discard the safe channel")

    # When one channel cannot be made safe, only that channel's pins may be
    # abandoned. Discarding the other one would free the optimizer to heat in
    # exactly the expensive hours the user excluded, and would then report those
    # slots as released for safety -- which would not be true.
    winter = _build_optimizer("winter_typical", "winter_cold")
    original = HeatPumpOptimizer._safety_release_steps

    def dhw_never_satisfied(self, result, temp_min_bounds, space_pins, dhw_pins):
        """Insist hot water is always breaching, and space never is."""
        if dhw_pins is None:
            return [], []
        free = [
            i
            for i in range(len(dhw_pins))
            if not math.isnan(float(dhw_pins[i])) and float(dhw_pins[i]) < 0.5
        ]
        return ([], free[:1])

    space_pins = np.zeros(N)
    HeatPumpOptimizer._safety_release_steps = dhw_never_satisfied
    try:
        out = _solve(winter, space_pins=space_pins, dhw_pins=np.zeros(N))
    finally:
        HeatPumpOptimizer._safety_release_steps = original

    R.check(
        "the breaching channel is abandoned",
        len(out.manual_released_dhw) == N,
        f"released {len(out.manual_released_dhw)} of {N}",
    )
    R.check(
        "the channel that was never unsafe keeps its pins",
        len(out.manual_released_space) == 0,
        f"released {len(out.manual_released_space)} space steps",
    )
    R.check(
        "so the space plan the user asked for still holds",
        sum(out.power_schedule) < 1e-6,
        f"total space power {sum(out.power_schedule):.3f}",
    )


def test_release_always_resolves(R: Results) -> None:
    R.section("A released pin is never reported without being planned around")

    # The repair loop is bounded, so the interesting case is what happens when
    # it runs out of rounds. Releasing a pin and then handing back the plan that
    # was solved *with* it would be the worst possible outcome: a schedule known
    # to be unsafe, reported as if the unsafe part had been dropped.
    winter = _build_optimizer("winter_typical", "winter_cold")

    original = HeatPumpOptimizer._safety_release_steps
    calls: list[int] = []

    def never_satisfied(self, result, temp_min_bounds, space_pins, dhw_pins):
        """Insist on one more release every round, so the cap is always hit."""
        calls.append(1)
        if space_pins is None:
            return [], []
        free = [
            i
            for i in range(len(space_pins))
            if not math.isnan(float(space_pins[i])) and float(space_pins[i]) < 0.5
        ]
        return (free[:1], [])

    HeatPumpOptimizer._safety_release_steps = never_satisfied
    try:
        stubborn = _solve(winter, space_pins=np.zeros(N))
    finally:
        HeatPumpOptimizer._safety_release_steps = original

    R.check("a plan that never converges still terminates", len(calls) > 0)
    # Having given up, every forced-off step must have been abandoned, not just
    # the handful the rounds got through.
    R.check(
        "giving up releases every forced-off slot",
        len(stubborn.manual_released_space) == N,
        f"released {len(stubborn.manual_released_space)} of {N}",
    )
    # And the returned plan must be the one solved *after* that release. The
    # property that matters is not that some power was scheduled, but that the
    # house ends up as warm as it would have been with no override at all --
    # returning the plan solved before the release would leave it colder.
    auto = _solve(winter)
    R.check(
        "the abandoned plan is as warm as planning freely",
        min(stubborn.room_temp_trajectory) >= min(auto.room_temp_trajectory) - 0.05,
        f"pinned {min(stubborn.room_temp_trajectory):.2f} vs "
        f"auto {min(auto.room_temp_trajectory):.2f}",
    )
    R.check(
        "and it heats about as much as planning freely",
        abs(sum(stubborn.power_schedule) - sum(auto.power_schedule))
        <= 0.05 * max(sum(auto.power_schedule), 1e-6),
        f"pinned {sum(stubborn.power_schedule):.3f} vs "
        f"auto {sum(auto.power_schedule):.3f}",
    )


def test_no_override_identical(R: Results) -> None:
    R.section("No override leaves behaviour unchanged")
    for name, (pp, wp, dhw) in {
        "winter_dhw": ("winter_typical", "winter_cold", True),
        "summer": ("summer_typical", "summer_warm", True),
        "no_dhw": ("winter_typical", "winter_cold", False),
    }.items():
        bundle = _build_optimizer(pp, wp, dhw=dhw)
        a = _solve(bundle)
        b = _solve(bundle, space_pins=None, dhw_pins=None)
        same = (
            a.power_schedule == b.power_schedule
            and a.dhw_power_schedule == b.dhw_power_schedule
            and a.space_reasons == b.space_reasons
            and a.dhw_reasons == b.dhw_reasons
        )
        R.check(f"{name}: passing no pins is byte-for-byte identical", same)
        R.check(
            f"{name}: no pins means the override is inactive",
            not b.manual_pins_active
            and b.manual_released_space == []
            and b.manual_released_dhw == [],
        )


def test_coordinator(R: Results) -> None:
    R.section("Coordinator wiring, persistence and expiry")
    now = dt_util.now()
    expires = now + timedelta(hours=MANUAL_PLAN_WINDOW_HOURS)

    _reset_store_disk()
    coord = _mk_coordinator()
    ov = build_override(
        dhw_slots=[_slot(0, 2, base=now)],
        space_slots=None,
        expires_at=expires,
        now=now,
    )
    result = asyncio.run(coord.async_apply_manual_plan(ov))
    R.check("apply reports the pinned DHW step count", result["pinned_dhw_steps"] == 8)

    # The step count has to be measured over the whole optimisation horizon.
    # Measuring it in price entries instead -- which are hourly, not per step --
    # covers only a quarter of the day, so a late slot is reported as pinning
    # nothing at all and the user is told their plan did not take.
    #
    # "Late" now means late *within the manual-plan window*. This used to sit at
    # 20-22 h against a 26 h expiry, which the 20 h window would free -- so the
    # check would have gone on passing for entirely the wrong reason.
    late = asyncio.run(
        coord.async_apply_manual_plan(
            build_override(
                dhw_slots=[_slot(17, 19, base=now)],
                space_slots=None,
                expires_at=now + timedelta(hours=MANUAL_PLAN_WINDOW_HOURS),
                now=now,
            )
        )
    )
    R.check(
        "a slot late in the horizon is still counted",
        late["pinned_dhw_steps"] == 8,
        f"reported {late['pinned_dhw_steps']} steps",
    )

    # And the other side of that boundary: past the window nothing is pinned,
    # because `channel_pins` frees every step at or after the expiry. The card's
    # edit ceiling exists to stop a user arranging slots there and being shown
    # them as pinned while they quietly do nothing.
    beyond = asyncio.run(
        coord.async_apply_manual_plan(
            build_override(
                dhw_slots=[
                    _slot(
                        MANUAL_PLAN_WINDOW_HOURS,
                        MANUAL_PLAN_WINDOW_HOURS + 2,
                        base=now,
                    )
                ],
                space_slots=None,
                expires_at=now + timedelta(hours=MANUAL_PLAN_WINDOW_HOURS),
                now=now,
            )
        )
    )
    R.check(
        "a slot past the window pins nothing, rather than pretending to",
        beyond["pinned_dhw_steps"] == 0,
        f"reported {beyond['pinned_dhw_steps']} steps",
    )

    # The window has to stay shorter than the horizon, or an override re-applied
    # each day would cover every step at every moment and leave the optimizer
    # nothing to decide -- switching it off while appearing to leave it on.
    R.check(
        "the manual-plan window is shorter than the optimisation horizon",
        MANUAL_PLAN_WINDOW_HOURS < 24,
        f"window {MANUAL_PLAN_WINDOW_HOURS} h",
    )
    asyncio.run(coord.async_apply_manual_plan(ov))

    space_pins, dhw_pins = coord._manual_pins(now, N)
    R.check("an omitted channel produces no pins", space_pins is None)
    R.check(
        "a supplied channel produces aligned pins",
        dhw_pins is not None and int((dhw_pins == 1.0).sum()) == 8,
    )

    state = coord._manual_plan_state()
    R.check(
        "the coordinator exposes the active override to the sensors",
        state is not None and state["active"] and state["dhw_slots"] is not None,
    )

    # A restart: a fresh coordinator restores the same plan from the Store.
    coord2 = _mk_coordinator()
    asyncio.run(coord2._async_load_manual_plan())
    R.check(
        "an override survives a restart within the day",
        coord2._manual_override is not None
        and coord2._manual_override.expires_at == expires,
    )

    # Discard-if-expired on restore.
    _reset_store_disk()
    stale = {
        "space_slots": None,
        "dhw_slots": [],
        "expires_at": (now - timedelta(hours=1)).isoformat(),
        "created_at": (now - timedelta(hours=3)).isoformat(),
    }
    asyncio.run(coord2._manual_plan_store.async_save(stale))
    coord3 = _mk_coordinator()
    asyncio.run(coord3._async_load_manual_plan())
    R.check(
        "an already-expired override is discarded on restore",
        coord3._manual_override is None,
    )

    # An override that expires mid-flight is inert and dropped by the pin build.
    _reset_store_disk()
    coord4 = _mk_coordinator()
    soon = now + timedelta(minutes=5)
    ov_soon = build_override(
        dhw_slots=[_slot(0, 1, base=now)],
        space_slots=None,
        expires_at=soon,
        now=now,
    )
    asyncio.run(coord4.async_apply_manual_plan(ov_soon))
    later = now + timedelta(minutes=10)
    sp, dp = coord4._manual_pins(later, N)
    R.check(
        "an expired override yields no pins",
        sp is None and dp is None,
    )
    R.check(
        "an expired override is dropped from the coordinator",
        coord4._manual_override is None,
    )

    # A rejected apply must leave an override already in force untouched. This
    # mirrors the service handler, which validates via build_override before it
    # ever calls the coordinator.
    _reset_store_disk()
    coord5 = _mk_coordinator()
    good = build_override(
        dhw_slots=[_slot(0, 2, base=now)],
        space_slots=None,
        expires_at=expires,
        now=now,
    )
    asyncio.run(coord5.async_apply_manual_plan(good))
    before = coord5._manual_override
    try:
        build_override(
            dhw_slots=[_slot(2, 1, base=now)],  # end before start
            space_slots=None,
            expires_at=expires,
            now=now,
        )
    except ManualPlanError:
        pass
    R.check(
        "a rejected apply leaves the existing override intact",
        coord5._manual_override is before and before is not None,
    )

    # A .storage file that is not a mapping at all -- corrupted, or hand-edited
    # by someone poking at their config -- must cost the user their override and
    # nothing more. Letting it raise would abort the whole integration's setup.
    for junk in ([], "nonsense", 7):
        _reset_store_disk()
        coord6 = _mk_coordinator()
        asyncio.run(coord6._manual_plan_store.async_save(junk))
        try:
            asyncio.run(coord6._async_load_manual_plan())
            survived = True
            detail = ""
        except Exception as err:  # noqa: BLE001 - the bug being guarded
            survived = False
            detail = f"{type(err).__name__}: {err}"
        R.check(
            f"a stored {type(junk).__name__} payload is discarded, not raised",
            survived and coord6._manual_override is None,
            detail,
        )

    # The data dict only carries the manual_plan key while one is active.
    R.check(
        "the data dict omits manual_plan when none is active",
        _mk_coordinator()._manual_plan_state() is None,
    )


def test_reload_handover_expiry(R: Results) -> None:
    """#774: a reload handover older than one update interval is dropped.

    The published payload object stays the stash so the existing identity
    pin in features.py still holds; the stamp lives beside it. Ages on a
    fresh handover are recomputed in ``_async_first_refresh_light``.
    """
    R.section("#774 — reload handover expiry")
    payload = {"mode": "auto", "sentinel": "the pre-reload plan"}
    interval = 30.0

    class _StashCoord:
        def __init__(self) -> None:
            self.data = payload

        async def async_shutdown(self) -> None:
            return None

    hass = FakeHass()
    entry = FakeEntry(
        data={"tibber_token": "x", "weather_entity": "weather.home"},
        entry_id="ho_expire",
    )
    entry.runtime_data = _StashCoord()
    asyncio.run(integ.async_unload_entry(hass, entry))
    R.check(
        "unload keeps the published payload object identity",
        integ._plan_handovers(hass).get(entry.entry_id) is payload,
    )
    R.check(
        "unload stamps the handover",
        entry.entry_id in integ._handover_stamps(hass),
    )

    fresh = integ._take_fresh_handover(hass, entry.entry_id, interval)
    R.check("a stamp inside one interval is handed over", fresh is payload)
    R.check(
        "take always pops the handover",
        entry.entry_id not in integ._plan_handovers(hass)
        and entry.entry_id not in integ._handover_stamps(hass),
    )

    integ._plan_handovers(hass)[entry.entry_id] = payload
    integ._handover_stamps(hass)[entry.entry_id] = dt_util.now() - timedelta(days=7)
    R.check(
        "a seven-day stamp is dropped",
        integ._take_fresh_handover(hass, entry.entry_id, interval) is None,
    )

    integ._plan_handovers(hass)[entry.entry_id] = payload
    integ._handover_stamps(hass)[entry.entry_id] = dt_util.now() - timedelta(minutes=1)
    R.check(
        "a one-minute stamp is still handed over",
        integ._take_fresh_handover(hass, entry.entry_id, interval) is payload,
    )

    integ._plan_handovers(hass)[entry.entry_id] = payload
    R.check(
        "an unstamped leftover is dropped",
        integ._take_fresh_handover(hass, entry.entry_id, interval) is None,
    )

    integ._plan_handovers(hass)[entry.entry_id] = payload
    integ._handover_stamps(hass)[entry.entry_id] = dt_util.now()
    asyncio.run(integ.async_remove_entry(hass, entry))
    R.check(
        "async_remove_entry clears the leftover handover",
        entry.entry_id not in integ._plan_handovers(hass)
        and entry.entry_id not in integ._handover_stamps(hass),
    )

    expired_hass = FakeHass()
    _seed_prices(expired_hass)  # #924: no handover means the first
    # refresh runs the fetch path, which needs a working offline source
    expired_entry = FakeEntry(
        data={**_OFFLINE_PRICES, "weather_entity": "weather.home"},
        entry_id="ho_setup_expired",
    )
    integ._plan_handovers(expired_hass)[expired_entry.entry_id] = payload
    integ._handover_stamps(expired_hass)[expired_entry.entry_id] = (
        dt_util.now() - timedelta(days=7)
    )
    asyncio.run(ha_setup_entry(integ, expired_hass, expired_entry))
    R.check(
        "setup does not hand an expired plan to the first refresh",
        expired_entry.runtime_data._reload_handover is None,
    )

    fresh_hass = FakeHass()
    _seed_prices(fresh_hass)  # #924
    fresh_entry = FakeEntry(
        data={**_OFFLINE_PRICES, "weather_entity": "weather.home"},
        entry_id="ho_setup_fresh",
    )
    integ._plan_handovers(fresh_hass)[fresh_entry.entry_id] = payload
    integ._handover_stamps(fresh_hass)[fresh_entry.entry_id] = (
        dt_util.now() - timedelta(minutes=1)
    )
    asyncio.run(ha_setup_entry(integ, fresh_hass, fresh_entry))
    # #924 re-cut: the first refresh now RUNS through the base class, so it
    # does not leave the handover latched -- it publishes it. The payload
    # dict is handed through by identity, which is the stronger form of the
    # property this check always pinned: the fresh plan reached the entities.
    R.check(
        "setup's first refresh publishes the one-minute plan, by identity",
        fresh_entry.runtime_data.data is payload
        and fresh_entry.runtime_data._reload_handover is None,
        f"data is payload: {fresh_entry.runtime_data.data is payload}, "
        f"handover consumed: "
        f"{fresh_entry.runtime_data._reload_handover is None}",
    )


def test_reload_handover_republish_ages(R: Results) -> None:
    """#774 residual: a still-fresh handover must not republish frozen ages.

    #880 expires a stash older than one update interval. A stamp inside that
    window still handed the pre-unload payload back verbatim, so
    ``plan_age_minutes`` / ``plan_stale`` stayed at the values frozen at
    unload. The light refresh must recompute both from ``last_optimization``.
    """
    R.section("#774 — handover republish ages")
    last = dt_util.now() - timedelta(minutes=120)
    payload = {
        "mode": "auto",
        "sentinel": "frozen-age",
        "last_optimization": last,
        "plan_age_minutes": 0.0,
        "plan_stale": False,
    }
    coord = _mk_coordinator()
    coord._reload_handover = payload
    out = asyncio.run(coord._async_first_refresh_light())
    R.check(
        "republish keeps the payload object so the features.py identity pin holds",
        out is payload,
    )
    R.check(
        "republish recomputes plan_age_minutes from last_optimization",
        out.get("plan_age_minutes") == 120.0,
        f"published {out.get('plan_age_minutes')}",
    )
    R.check(
        "republish recomputes plan_stale from the live age",
        out.get("plan_stale") is True,
        f"published {out.get('plan_stale')}",
    )

    just_now = dt_util.now()
    fresh_payload = {
        "mode": "auto",
        "last_optimization": just_now,
        "plan_age_minutes": 0.0,
        "plan_stale": False,
    }
    fresh = _mk_coordinator()
    fresh._reload_handover = fresh_payload
    fresh_out = asyncio.run(fresh._async_first_refresh_light())
    R.check(
        "a just-solved handover still publishes age 0.0 (null control)",
        fresh_out.get("plan_age_minutes") == 0.0
        and fresh_out.get("plan_stale") is False,
        f"published age={fresh_out.get('plan_age_minutes')} "
        f"stale={fresh_out.get('plan_stale')}",
    )


#: Overrides now expire a fixed number of hours from the moment they are
#: applied, so the old reason for freezing the clock -- a midnight cap that
#: silently truncated "two hours from now" when the suite ran at 22:30 -- no
#: longer applies. The clock stays frozen anyway: several checks below assert on
#: hour-of-day arithmetic, and a frozen clock keeps a failure meaning the code
#: changed rather than that the suite ran at an awkward time.
_TEST_CLOCK = datetime(2026, 1, 15, 9, 0, 0)


def main() -> int:
    _dt_stub.freeze(_TEST_CLOCK)
    try:
        return _run()
    finally:
        _dt_stub.freeze(None)


def _run() -> int:
    R = Results("Manual plan override")
    test_parsing(R)
    test_channel_semantics(R)
    test_serialization(R)
    test_pins_change_schedule(R)
    test_off_window_over_pins(R)
    test_legionella_outside_off_window(R)
    test_legionella_arms_a_solve_horizon_never_builds(R)
    test_quiet_window_arms(R)
    test_safety_release(R)
    test_naive_expiry(R)
    test_give_up_is_per_channel(R)
    test_release_always_resolves(R)
    test_no_override_identical(R)
    test_coordinator(R)
    test_reload_handover_expiry(R)
    test_reload_handover_republish_ages(R)
    return R.close("manual plan checks")


if __name__ == "__main__":
    sys.exit(main())
