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

from harness import FakeEntry, FakeHass, Results
from profiles import house, prices, weather

import homeassistant.util.dt as dt_util
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.storage import _reset_store_disk
from homeassistant.util import dt as _dt_stub

from heatpump_optimizer.const import MANUAL_PLAN_WINDOW_HOURS
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
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
    return opt_obj.optimize(state, p, outdoor, wind, rain, solar, START, **kwargs)


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

    # Forcing hot water ON in an expensive evening step adds DHW power there.
    dp = np.full(N, np.nan)
    dp[68] = 1.0
    pinned_dhw = _solve(winter, dhw_pins=dp)
    R.check(
        "forcing hot water on adds a DHW run",
        base.dhw_power_schedule[68] < 0.05 and pinned_dhw.dhw_power_schedule[68] > 0.3,
    )
    R.check(
        "a manual DHW step is labelled manual_plan",
        pinned_dhw.dhw_reasons[68] == REASON_MANUAL,
    )

    # Forcing hot water OFF when it is safe (hot tank in summer) removes a run.
    summer = _build_optimizer(
        "summer_typical", "summer_warm", dhw_temperature=54.0
    )
    sbase = _solve(summer)
    active = [i for i, v in enumerate(sbase.dhw_power_schedule) if v > 0.01]
    k = active[0]
    off = np.full(N, np.nan)
    off[k] = 0.0
    pinned_off = _solve(summer, dhw_pins=off)
    R.check(
        "forcing hot water off removes a run when safe",
        sbase.dhw_power_schedule[k] > 0.1
        and pinned_off.dhw_power_schedule[k] < 0.01,
    )
    R.check(
        "a safe forced-off step is not released",
        k not in pinned_off.manual_released_dhw,
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
    active = [i for i, v in enumerate(sbase.dhw_power_schedule) if v > 0.01]
    off = np.full(N, np.nan)
    off[active[0]] = 0.0
    quiet_dhw = _solve(summer_dhw, dhw_pins=off)
    R.check(
        "forcing hot water off when the tank is hot releases nothing",
        len(quiet_dhw.manual_released_dhw) == 0,
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
    test_safety_release(R)
    test_naive_expiry(R)
    test_give_up_is_per_channel(R)
    test_release_always_resolves(R)
    test_no_override_identical(R)
    test_coordinator(R)
    return R.close("manual plan checks")


if __name__ == "__main__":
    sys.exit(main())
