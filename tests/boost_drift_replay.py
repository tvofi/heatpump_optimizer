#!/usr/bin/env python3
"""#1935: two days of repeated space-boost use against the real learners.

The R9-DIAG-1 pre-study measured the defect this pins: the interval
learners replay the elapsed interval through a plant state propagated
open-loop from the PLAN's trajectory, so heat a boost overlay added -- real
in the house's slab, absent from the model's -- leaves every replay
residual warm-side, and two boost days walked a converged, persisted
``house_heat_loss_scale`` from 1.04 to the 0.5 trust-region floor, with a
~4-day recovery walk at the learner's designed pace. The harness moved
in-tree with the fix (the pre-study ran it from a branch); this is the
same scenario, shortened to what the assertions need.

Per 30-minute cycle, in ``_async_update_data``'s production order minus
the network fetches: frozen clock -> fake-bus sensor states reading what
the true house did -> ``_update_current_state`` (every interval learner
runs here) -> a real ``HeatPumpOptimizer.optimize`` solve on the
coordinator's own live model, adopted through ``boost.adopt_plan`` -> the
boost channel driven through the switch's own ``set_channel``/``apply``
path -> the true house (a second ``ThermalModel`` with the true heat loss)
advancing one step under the actuated action with a thermostat cap ->
``_record_accuracy`` -> once per calendar day ``_async_watch_learning_drift``.

Arms (argv selects; default runs all three):

``null_no_boost``   no boost at all -- the machinery control: the scale
                    converges on plan-power intervals alone and stays
                    flat across the days the other arms boost.
``channel_boost``   two boost days through the space-channel switch.
``mode_boost``      the same windows through the global mode select,
                    driven through ``async_set_mode`` so the mode
                    surface's settling tail is the real one.

The true house and the configured model share a parameter set (the
learner has converged, not work left to do -- the corruption scenario is
the damaging one). The true house's weather is the same analytic weather
the solve forecasts and the sensors read, so the only plant/model
differences are the ones under test.
"""
from __future__ import annotations

import sys
from datetime import timedelta, timezone

import numpy as np

import homeassistant.util.dt as dt_mod
from harness import FakeEntry, FakeHass, FakeState, Results
from profiles import solve_inputs

from heatpump_optimizer import boost as boost_mod
from heatpump_optimizer.accuracy import AccuracySample
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

R = Results("#1935 boost drift replay")

UTC = timezone.utc
DT_MIN = 30.0          # the production default optimization interval
STEP_MIN = 30.0        # solver time step, minutes
DAYS = 9               # 5 to converge, 2 boost days, 2 recovery
START = dt_mod.parse_datetime("2026-01-05T00:00:00+00:00")
BOOST_DAYS = (5, 6)    # tvofi's report: "a few times over two days"
BOOST_STARTS = (7.0, 12.0, 18.0)   # local hours
#: The settling tail, read from production (under a name of this script's
#: own, so closure.py's no-copies sees a reference, not a re-implementation:
#: a test symbol named like production's is refused however it gets its
#: value). The window length and the freeze reason are used as
#: ``boost_mod.BOOST_HOURS`` / ``boost_mod.FREEZE_REASON`` at their sites
#: for the same reason, with no fallbacks: a fallback the check itself
#: supplies would pass silently if production renamed one. The
#: failing-first run at the merge base used fallback forms (that run
#: predates the fix's symbols); it is recorded in the PR body's
#: ## Mutation proof / ## Figures.
SETTLE_TAIL = boost_mod.SPACE_SETTLE_TAIL
#: The band the frozen scale must stay inside across the boost days and
#: the two days after. Unfixed, the scale leaves it by an order of
#: magnitude (-50 %, the trust-region floor); the fix holds it exactly.
BAND = 0.05
#: Window plus settling tail, in local hours from each window start: the
#: cycles whose folds the freeze reason must suppress.
FROZEN_SPAN = (boost_mod.BOOST_HOURS
               + SETTLE_TAIL.total_seconds() / 3600.0)


def day_arrays(day_index: int):
    """Prices (SEK/kWh) and weather for one day, at the solver's step."""
    n = int(24 * 60 / STEP_MIN)
    h = np.arange(n) * (STEP_MIN / 60.0)
    p = np.full(n, 1.05)
    p[(h >= 0) & (h < 5)] = 0.62
    p[(h >= 7) & (h < 10)] = 2.35
    p[(h >= 16) & (h < 20)] = 2.85
    p[h >= 23] = 0.78
    # A cold but not extreme January day, repeating with a slow multi-day
    # swing so the learner never sees an identical day twice.
    base = -6.0 + 3.0 * np.sin((day_index / 4.0) * np.pi / 2.0)
    t_out = base + 4.0 * np.sin((h - 14.0) / 24.0 * 2 * np.pi)
    solar = np.clip(45.0 * np.sin((h - 8.5) / 7.0 * np.pi), 0.0, None)
    return p, t_out, solar, np.full(n, 2.0), np.zeros(n)


def build_house() -> ThermalModel:
    cfg = {
        "target_temperature": 21.0, "min_temperature": 20.0,
        "max_temperature": 23.0, "heat_pump_max_power": 6.0,
        "heat_pump_min_power": 1.0,
    }
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    return ThermalModel(params)


def weather_now(day_index: int, hour: float):
    """The TRUE outdoor temperature and solar at an instant.

    Same formulas as ``day_arrays``, evaluated continuously, so the sensor
    readings, the house's experience and the solve's perfect forecast are
    one weather."""
    base = -6.0 + 3.0 * np.sin((day_index / 4.0) * np.pi / 2.0)
    t_out = base + 4.0 * np.sin((hour - 14.0) / 24.0 * 2 * np.pi)
    solar = float(np.clip(45.0 * np.sin((hour - 8.5) / 7.0 * np.pi), 0.0, None))
    return float(t_out), solar


def build_coord():
    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor",
        "outdoor_temp_entity": "sensor.outdoor",
        "heat_pump_power_entity": "sensor.hp_power",
        "solar_radiation_entity": "sensor.solar",
        "optimization_interval": DT_MIN,
    }
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    coord._snapshots_loaded = True
    return coord


def window_frozen(day_index: int, hour: float) -> bool:
    """Whether the freeze reason must be suppressing folds at this cycle.

    From the first cycle after a window opens (the learners of the opening
    cycle itself replay a pre-boost interval and rightly fold) through the
    settling tail behind it, tail end exclusive. This is the harness's own
    expectation, computed from the schedule it drives -- not a read of the
    production predicate, which is what the checks judge.
    """
    if day_index not in BOOST_DAYS:
        return False
    return any(s < hour < s + FROZEN_SPAN for s in BOOST_STARTS)


def fork_cycle() -> int:
    """The first cycle any boost surface acts on: day ``BOOST_DAYS[0]`` at
    the earliest window start.

    Before it the three surfaces run one code path -- the channel switch is
    entered only on a boosting cycle, the mode select is driven only when
    its wanted mode differs from auto, which only a boosting cycle makes it
    -- so every arm's state there is one state, solved once and copied
    (``replay``). Each cycle's solve is a full production multi-start and
    the solves are the script's cost, so the pre-boost days are paid once
    rather than once per arm. ``check_fork`` asserts the precondition."""
    per_day = int(24 * 60 / DT_MIN)
    return BOOST_DAYS[0] * per_day + int(min(BOOST_STARTS) * 60 / DT_MIN)


def boosting_at(day_index: int, h_now: float) -> bool:
    """Whether a boost window is open at this cycle, on any surface."""
    return (
        day_index in BOOST_DAYS
        and any(s <= h_now < s + boost_mod.BOOST_HOURS for s in BOOST_STARTS)
    )


def start_state(two_zone: bool = False) -> dict:
    """Everything one arm's replay carries from cycle to cycle."""
    coord = build_coord()
    ctx = getattr(coord, "_ctx", coord)
    house = build_house()
    if two_zone:
        # The named follow-up measurement (R9-DIAG-1 F5): a two-zone house,
        # upper-floor sensor, the learner's own comments describe a 1.5 K
        # zone split injecting +0.53 K of systematic residual -- the leading
        # candidate amplifier behind tvofi's alarm.
        ctx._thermal_params.two_zone_enabled = True
        house.params.two_zone_enabled = True
    opt_cfg = OptimizationConfig(
        horizon_hours=24.0,
        time_step_minutes=STEP_MIN,
        target_temp=21.0, min_temp=20.0, max_temp=23.0,
    )
    return {
        "coord": coord, "ctx": ctx, "house": house, "two_zone": two_zone,
        "optimizer": HeatPumpOptimizer(coord._thermal_model, opt_cfg),
        "house_state": ThermalState(
            room_temperature=20.5, outdoor_temperature=-6.0,
            upper_floor_temperature=20.75, lower_floor_temperature=20.25,
        ),
        "draw": 0.0, "daily": {}, "daily_bias": {}, "alarmed": False,
        "folds_frozen": 0,      # folds on cycles the freeze must suppress
        "folds_outside": 0,     # folds on cycles outside every frozen span
        "folds_after": 0,       # folds after the boost days (resumption)
        "mode_is_boost": False, "day_index": -1,
    }


def cycle(st: dict, i: int, surface: str) -> None:
    """One 30-minute cycle of the replay, in production order."""
    import asyncio

    coord, ctx, house = st["coord"], st["ctx"], st["house"]
    two_zone = st["two_zone"]
    house_state = st["house_state"]
    t = START + timedelta(minutes=i * DT_MIN)
    if t.date() != (t - timedelta(minutes=DT_MIN)).date():
        st["day_index"] += 1
    day_index = st["day_index"]
    dt_mod.freeze(t)
    h_now = t.hour + t.minute / 60.0
    outdoor_now, solar_now = weather_now(day_index, h_now)
    indoor_reading = (
        house_state.upper_floor_temperature
        if two_zone else house_state.room_temperature
    )
    coord.hass.states.set(
        "sensor.indoor",
        FakeState(f"{indoor_reading:.3f}", last_updated=t, unit="°C"),
    )
    coord.hass.states.set(
        "sensor.outdoor",
        FakeState(f"{outdoor_now:.3f}", last_updated=t, unit="°C"),
    )
    coord.hass.states.set(
        "sensor.hp_power",
        FakeState(f"{st['draw']:.3f}", last_updated=t, unit="kW"),
    )
    coord.hass.states.set(
        "sensor.solar",
        FakeState(f"{solar_now:.2f}", last_updated=t, unit="W/m²"),
    )
    # -- learners replay the elapsed interval ------------------------------
    n0 = coord._house_heat_loss_samples
    asyncio.run(coord._update_current_state())
    if coord._house_heat_loss_samples > n0:
        if window_frozen(day_index, h_now):
            st["folds_frozen"] += 1
        else:
            st["folds_outside"] += 1
            if day_index > max(BOOST_DAYS):
                st["folds_after"] += 1
    # -- the plan (a real solve on the live model) --------------------------
    step_idx = int(round(h_now * 60.0 / STEP_MIN))
    p, t_out, solar, wind, rain = day_arrays(day_index)
    p2, t_out2, solar2, wind2, rain2 = day_arrays(day_index + 1)
    result = st["optimizer"].optimize(inputs=solve_inputs(
        initial_state=ctx._current_state,
        prices=np.concatenate([p, p2])[step_idx:],
        outdoor_temps=np.concatenate([t_out, t_out2])[step_idx:],
        wind_speeds=np.concatenate([wind, wind2])[step_idx:],
        precipitation=np.concatenate([rain, rain2])[step_idx:],
        solar_radiation=np.concatenate([solar, solar2])[step_idx:],
        start_time=t,
    ))
    coord._optimization_result = result
    # -- the boost surface, as its own switch leaves it ---------------------
    boosting = boosting_at(day_index, h_now)
    if surface == "mode" and boosting:
        # What ``_async_update_data``'s MODE_BOOST branch adopts:
        # nameplate power at the comfort ceiling. The mode select is
        # driven through ``async_set_mode`` below, so the mode surface's
        # own settling tail is the real one.
        boost_mod.adopt_plan(coord, {
            "power": float(coord._thermal_model.params.max_electrical_power),
            "setpoint": 23.0,
            "mode": "boost",
            "power_normalized": 1.0,
            "heat_pump_on": True,
            "displace_value": 0.0,
            "space_reason": "plan",
        })
    else:
        boost_mod.adopt_plan(coord, {
            "power": float(result.power_schedule[0]),
            "setpoint": 23.0,
            "mode": "auto",
            "power_normalized": float(result.power_schedule[0]) / 6.0,
            "heat_pump_on": result.power_schedule[0] > 0.05,
            "displace_value": 0.0,
            "space_reason": "plan",
        })
    if surface == "channel":
        # Enter through the real switch path at each window start; the
        # normal end is the expiry ``apply`` observes, not a cancel.
        if boosting and h_now in BOOST_STARTS:
            asyncio.run(boost_mod.set_channel(
                coord, boost_mod.CHANNEL_SPACE, True, refresh=False))
    elif surface == "mode":
        want = "boost" if boosting else "auto"
        if want != ("boost" if st["mode_is_boost"] else "auto"):
            asyncio.run(coord.async_set_mode(want, refresh=False))
            st["mode_is_boost"] = boosting
    boost_mod.apply(coord, boost_mod.BoostOverlay(
        max_power=float(coord._thermal_model.params.max_electrical_power),
        max_temp=float(ctx._opt_config.max_temp),
        ecl_max=float(coord._ecl110_displace_max),
    ))
    # -- actuate: the true house answers the overlaid action ---------------
    act = coord._current_action
    want = float(act.get("power", 0.0))
    setpoint = float(act.get("setpoint", 23.0))
    # thermostat cap: the pump stops at its setpoint
    applied = want if house_state.room_temperature < setpoint - 0.1 else 0.0
    if boosting and house_state.room_temperature >= setpoint - 0.1:
        # modulating near the ceiling rather than fully off
        applied = want * 0.35
    house_state = house.simulate_step(
        house_state, applied, outdoor_now,
        wind_speed=2.0, precipitation=0.0,
        solar_radiation=solar_now, dt_hours=DT_MIN / 60.0,
        hour_of_day=h_now,
    )
    house_state.outdoor_temperature = outdoor_now
    st["house_state"] = house_state
    st["draw"] = applied
    # -- close the loop on the prediction ----------------------------------
    coord._record_accuracy()
    # -- the daily heartbeat, once per calendar day ------------------------
    if t.hour == 3 and t.minute == 0:
        asyncio.run(coord._async_watch_learning_drift())
        st["daily"][day_index] = round(coord._house_heat_loss_scale, 4)
        bias = coord._accuracy.temperature_bias()
        st["daily_bias"][day_index] = (
            round(bias, 4) if bias is not None else None)
        st["alarmed"] = st["alarmed"] or coord._snapshot_ring.alarmed


def arm_summary(arm: str, st: dict) -> dict:
    coord = st["coord"]
    samples = coord._accuracy.samples
    return {
        "arm": arm,
        "daily": st["daily"],
        "folds_frozen": st["folds_frozen"],
        "folds_outside": st["folds_outside"],
        "folds_after": st["folds_after"],
        "tagged": [s for s in samples if getattr(s, "boost_space", False)],
        "untagged": [s for s in samples
                     if not getattr(s, "boost_space", False)],
        "hh_final": round(coord._house_heat_loss_scale, 4),
        "daily_bias": st["daily_bias"],
        "alarmed": st["alarmed"],
    }


def replay(arms: dict, two_zone: bool = False,
           fork: int | None = None) -> dict:
    """Each arm's replay summary, ``arms`` mapping its name to its surface.

    The cycles before ``fork`` (default ``fork_cycle()``) are surface-free,
    so they run once and every arm continues from a deep copy of that one
    state; ``fork=0`` replays every arm from its own fresh start, which is
    the unshared replay the shared one must equal
    (``tools/audit/harnesses/boost_replay_fork_parity.py``)."""
    import copy

    n_cycles = int(DAYS * 24 * 60 / DT_MIN)
    fork = fork_cycle() if fork is None else fork
    shared = start_state(two_zone)
    for i in range(fork):
        cycle(shared, i, "none")
    outs = {}
    for arm, surface in arms.items():
        st = copy.deepcopy(shared)
        for i in range(fork, n_cycles):
            cycle(st, i, surface)
        outs[arm] = arm_summary(arm, st)
    return outs


class _OneSolve:
    """The solve ``check_fork`` drives every arm with: one real production
    plan, returned for every cycle. The guard asks whether a SURFACE acts
    before the fork, not what the solver says, so one plan stands for all
    and the guard costs one solve instead of three prefixes'."""

    def __init__(self, result) -> None:
        self.result = result

    def optimize(self, *, inputs):
        return self.result


def prefix_trace(st: dict, i: int) -> tuple:
    """What one cycle left behind that any arm-specific act would move: the
    action and mode the surfaces write, the overlay's held state, the freeze
    reason, the learners' fold and the true house's answer."""
    coord = st["coord"]
    held = boost_mod.held_for(coord)
    samples = coord._accuracy.samples
    return (
        i, repr(sorted(coord._current_action.items())), coord._mode,
        repr(sorted(held.until.items())), repr(held.space_settle_until),
        coord._learning_frozen("sensor.indoor"),
        coord._house_heat_loss_samples, coord._house_heat_loss_scale,
        st["house_state"].room_temperature, st["draw"],
        st["folds_frozen"], st["folds_outside"], st["mode_is_boost"],
        len(samples), repr(samples[-1].as_dict()) if samples else None,
    )


def check_fork() -> None:
    """The shared prefix's precondition, asserted rather than assumed.

    Two halves. The arithmetic: ``fork_cycle`` is exactly the first cycle
    ``boosting_at`` opens. The behaviour: every surface's arm, driven
    through ``cycle`` itself over the cycles before the fork, leaves the
    same trace as the surface-free arm -- so an action or input planted on
    one surface ahead of its window (which the arithmetic cannot see, and
    which the shared prefix would silently erase) fails here."""
    R.section("shared pre-boost prefix")
    fork = fork_cycle()
    first = None
    day_index = -1
    for i in range(int(DAYS * 24 * 60 / DT_MIN)):
        t = START + timedelta(minutes=i * DT_MIN)
        if t.date() != (t - timedelta(minutes=DT_MIN)).date():
            day_index += 1
        if boosting_at(day_index, t.hour + t.minute / 60.0):
            first = i
            break
    R.check(
        "the fork is the first boosting cycle of the schedule",
        first == fork,
        f"fork={fork} first boosting cycle={first}",
    )
    solved = None
    traces = {}
    for surface in ("none", "channel", "mode"):
        st = start_state()
        if solved is None:
            cycle(st, 0, surface)
            solved = _OneSolve(st["coord"]._optimization_result)
            st = start_state()
        st["optimizer"] = solved
        trace = []
        for i in range(fork):
            cycle(st, i, surface)
            trace.append(prefix_trace(st, i))
        traces[surface] = trace
    for surface in ("channel", "mode"):
        diverged = next((a[0] for a, b in zip(traces["none"], traces[surface])
                         if a != b), None)
        R.check(
            f"the {surface} surface acts on nothing before the fork (its "
            f"pre-fork trace equals the surface-free arm's, so one prefix "
            f"stands for it)",
            diverged is None and len(traces[surface]) == fork,
            f"first differing cycle {diverged} of {fork}",
        )


def check_arm(
    out: dict, *, boosted: bool, converged_near: float | None = 1.0424,
    band: float | None = BAND,
) -> None:
    arm = out["arm"]
    daily = out["daily"]
    pre = daily[BOOST_DAYS[0] - 1]  # the 03:00 row before the first window
    R.section(f"arm {arm}")
    if converged_near is None:
        # The two-zone learner identifies a different level (the upper
        # zone's own loss) and walks it faster: what the corruption
        # scenario needs is that it had SETTLED, not where.
        R.check(
            f"{arm}: the scale had settled before the boost days (the "
            f"corruption scenario needs a settled learner to corrupt)",
            abs(daily[BOOST_DAYS[0]] / daily[BOOST_DAYS[0] - 2] - 1.0) < 0.025,
            f"{daily[BOOST_DAYS[0]]} vs {daily[BOOST_DAYS[0] - 2]}",
        )
    else:
        R.check(
            f"{arm}: the scale converged before the boost days (the corruption "
            f"scenario needs a converged learner to corrupt)",
            abs(pre - converged_near) < 0.01,
            f"pre-boost hh_scale={pre}",
        )
    if band is not None:
        for day in range(BOOST_DAYS[0], DAYS - 1):
            value = daily[day]
            R.check(
                f"{arm}: day {day} hh_scale {value} stays within "
                f"{band:.0%} of the pre-boost {pre} (#1935)",
                abs(value / pre - 1.0) <= band,
                f"{value} vs {pre}",
            )
        R.check(
            f"{arm}: final hh_scale {out['hh_final']} still within the band "
            f"after the recovery days",
            abs(out["hh_final"] / pre - 1.0) <= band,
            f"{out['hh_final']} vs {pre}",
        )
    if boosted:
        R.check(
            f"{arm}: no heat-loss fold on any boost window or settling-tail "
            f"cycle (the freeze reason suppresses them; unfixed it does not)",
            out["folds_frozen"] == 0,
            f"{out['folds_frozen']} folds inside frozen spans",
        )
        R.check(
            f"{arm}: the freeze is scoped to the overlay spans and their "
            f"tails, not the whole boost usage -- most cycles outside them "
            f"still fold",
            out["folds_outside"] >= 100,
            f"{out['folds_outside']} folds outside spans",
        )
        R.check(
            f"{arm}: learning resumes once the last tail has passed "
            f"(the freeze ends with the tail)",
            out["folds_after"] >= 20,
            f"{out['folds_after']} folds after the boost days",
        )


def check_record(out: dict) -> None:
    """The accuracy record through the channel surface (#1935)."""
    R.section("accuracy record")
    tagged, untagged = out["tagged"], out["untagged"]
    R.check(
        "boost intervals are tagged on the sample (3 windows x 2 h x 2 days "
        "settled one cycle later)",
        len(tagged) >= 20,
        f"{len(tagged)} tagged",
    )
    R.check(
        "the plan-based prediction is suppressed on every tagged interval "
        "-- the channel surface now matches the global-mode gate",
        all(s.predicted_temp is None for s in tagged),
    )
    R.check(
        "untagged intervals still carry their prediction (the record "
        "itself is not switched off)",
        sum(1 for s in untagged if s.predicted_temp is not None) >= 100,
        f"{len(untagged)} untagged",
    )
    R.check(
        "the tag survives the store round trip, both ways",
        AccuracySample.from_dict(tagged[0].as_dict()).boost_space is True
        and AccuracySample.from_dict(untagged[0].as_dict()).boost_space is False
        if tagged and untagged else False,
    )


def check_freeze_units() -> None:
    """The freeze predicate's shape, without a replay around it."""
    import asyncio

    R.section("freeze reason units")
    coord = build_coord()
    now = dt_mod.now()
    dt_mod.freeze(now)
    R.check(
        "a clean coordinator reports no freeze reason",
        coord._learning_frozen("sensor.indoor") is None,
    )
    asyncio.run(boost_mod.set_channel(
        coord, boost_mod.CHANNEL_SPACE, True, refresh=False))
    R.check(
        "a live space overlay freezes learning (#1935)",
        coord._learning_frozen("sensor.indoor") == boost_mod.FREEZE_REASON,
    )
    R.check(
        "the prediction is suppressed while the overlay is live, with the "
        "mode still auto (the channel surface matches the mode gate)",
        coord._mode == "auto"
        and coord._predicted_next_room_temp() is None,
    )
    coord._vent_cusum.tripped = True
    R.check(
        "ventilation still outranks the boost reason, so the heat-loss "
        "learner's pass-through keeps feeding the window CUSUM",
        coord._learning_frozen("sensor.indoor") == "ventilation",
    )
    coord._vent_cusum.tripped = False
    asyncio.run(boost_mod.set_channel(
        coord, boost_mod.CHANNEL_DHW, True, refresh=False))
    held = boost_mod.held_for(coord)
    held.until.pop(boost_mod.CHANNEL_SPACE, None)
    held.space_settle_until = now + timedelta(hours=1)
    R.check(
        "the settling tail freezes learning after the overlay ends, and a "
        "DHW-only overlay does not (the freeze is scoped to space heat)",
        coord._learning_frozen("sensor.indoor") == boost_mod.FREEZE_REASON,
    )
    dt_mod.freeze(now + timedelta(hours=3))
    R.check(
        "past the tail, learning resumes",
        coord._learning_frozen("sensor.indoor") is None,
    )
    # The cancel path owes the same tail an expiry does, and only the
    # space channel's cancel does.
    coord3 = build_coord()
    asyncio.run(boost_mod.set_channel(
        coord3, boost_mod.CHANNEL_SPACE, True, refresh=False))
    asyncio.run(boost_mod.set_channel(
        coord3, boost_mod.CHANNEL_SPACE, False, refresh=False))
    R.check(
        "cancelling a live space overlay starts the settling tail",
        coord3._learning_frozen("sensor.indoor") == boost_mod.FREEZE_REASON,
    )
    coord4 = build_coord()
    asyncio.run(boost_mod.set_channel(
        coord4, boost_mod.CHANNEL_DHW, True, refresh=False))
    asyncio.run(boost_mod.set_channel(
        coord4, boost_mod.CHANNEL_DHW, False, refresh=False))
    R.check(
        "cancelling a DHW overlay starts none (the freeze is scoped to "
        "space heat)",
        coord4._learning_frozen("sensor.indoor") is None,
    )
    # The tag's exact boundaries: an overlay that ends this instant, or
    # began this instant, did not govern the interval that is closing.
    coord5 = build_coord()
    now5 = dt_mod.now()
    held5 = boost_mod.held_for(coord5)
    held5.until[boost_mod.CHANNEL_SPACE] = now5
    R.check(
        "an overlay ending exactly now did not govern the closing "
        "interval (no tag)",
        not boost_mod.interval_boosted({}, coord5),
    )
    held5.until[boost_mod.CHANNEL_SPACE] = now5 + timedelta(hours=2)
    R.check(
        "an overlay beginning exactly now governs only the NEXT interval "
        "(no tag on the closing one)",
        not boost_mod.interval_boosted({}, coord5),
    )
    held5.until[boost_mod.CHANNEL_SPACE] = now5 + timedelta(hours=1)
    R.check(
        "an overlay that began mid-interval tags the closing interval",
        boost_mod.interval_boosted({}, coord5),
    )
    # The diagnosis record's apportionment: a plan that drew nothing
    # splits the meter's whole draw to space.
    coord6 = build_coord()
    sample6 = AccuracySample(
        when=now5, predicted_power_kw=None, actual_power_kw=2.0,
        predicted_temp=None, actual_temp=20.0,
    )
    from heatpump_optimizer.coordinator import _settle_interval_diag
    _settle_interval_diag(coord6, sample6, {
        "diag": {"state": {}, "planned": {}},
        "space_power": 5e-7, "dhw_power": 5e-7,   # planned_total == 1e-6
    }, 0.5, now5)
    R.check(
        "a plan whose total draw sits exactly at the apportionment floor "
        "books the whole metered draw to space (share 1.0)",
        coord6._last_interval_record is not None
        and coord6._last_interval_record["realised"]["electrical_power"] == 2.0,
    )
    asyncio.run(coord.async_set_mode("boost", refresh=False))
    R.check(
        "the global boost mode freezes learning through the same reason",
        coord._learning_frozen("sensor.indoor") == boost_mod.FREEZE_REASON,
    )
    _tail_before = boost_mod.held_for(coord).space_settle_until
    asyncio.run(coord.async_set_mode("boost", refresh=False))
    R.check(
        "re-selecting boost while already in it starts no second tail "
        "(the tail is owed to LEAVING boost, not to being in it)",
        boost_mod.held_for(coord).space_settle_until == _tail_before,
    )
    asyncio.run(coord.async_set_mode("auto", refresh=False))
    R.check(
        "leaving boost mode starts the settling tail (same mechanism, "
        "same owed tail)",
        coord._learning_frozen("sensor.indoor") == boost_mod.FREEZE_REASON,
    )
    coord2 = build_coord()
    asyncio.run(coord2.async_set_mode("comfort", refresh=False))
    asyncio.run(coord2.async_set_mode("auto", refresh=False))
    R.check(
        "leaving a non-boost mode starts no tail (comfort->auto never "
        "freezes learning)",
        coord2._learning_frozen("sensor.indoor") is None,
    )


def check_vent_feed() -> None:
    """The ventilation pass-through still feeds its detector under boost.

    The one behavioural consequence of ranking boost below ventilation:
    with the window detector tripped AND an overlay live, the heat-loss
    learner must still replay the interval and feed the CUSUM (so the
    detector can see the window close), while folding nothing.
    """
    import asyncio

    R.section("ventilation pass-through")
    coord = build_coord()
    now = dt_mod.now()
    dt_mod.freeze(now)
    asyncio.run(boost_mod.set_channel(
        coord, boost_mod.CHANNEL_SPACE, True, refresh=False))
    coord._vent_cusum.tripped = True
    coord._current_action = {"power": 3.0, "mode": "auto"}
    coord._measured_power = 3.0
    previous = ThermalState(room_temperature=20.0, outdoor_temperature=-6.0)
    coord._last_house_sample = previous
    coord._last_house_sample_time = now - timedelta(minutes=30)
    getattr(coord, "_ctx", coord)._current_state.room_temperature = 20.0
    fed0 = coord._vent_cusum.last_fed
    stat0 = coord._vent_cusum.stat
    scale0 = coord._house_heat_loss_scale
    asyncio.run(coord._async_learn_house_heat_loss())
    R.check(
        "vent tripped + overlay live: the learner reports the ventilation "
        "reason and stays folded (no scale move)",
        coord._learner_freeze_reason == "ventilation"
        and coord._house_heat_loss_scale == scale0,
        f"reason={coord._learner_freeze_reason} "
        f"scale={coord._house_heat_loss_scale}",
    )
    R.check(
        "the CUSUM was fed on that pass-through interval (the detector "
        "keeps its feed through a boost window)",
        coord._vent_cusum.last_fed is not None
        and coord._vent_cusum.last_fed != fed0,
        f"last_fed {fed0} -> {coord._vent_cusum.last_fed}, stat {stat0} -> "
        f"{coord._vent_cusum.stat}",
    )


def main() -> int:
    argv = sys.argv[1:]
    arms = {
        "null_no_boost": "none",
        "channel_boost": "channel",
        "mode_boost": "mode",
    }
    # argv-only: measurements, not the gate
    followups = {"two_zone_boost": "channel", "two_zone_null": "none"}
    todo = argv or list(arms)
    check_fork()
    outs = replay({a: arms[a] for a in todo if a in arms})
    outs.update(replay({a: followups[a] for a in todo if a in followups},
                       two_zone=True))
    channel_out = None
    for arm in todo:
        out = outs[arm]
        if arm in followups:
            worst = max(
                (abs(v) for v in out["daily_bias"].values() if v is not None),
                default=0.0,
            )
            R.section(f"follow-up arm {arm}")
            if arm == "two_zone_null":
                R.check(
                    "two-zone null (no boost): the alarm never fires either "
                    f"(worst daily bias {worst:.3f} C against the 0.5 C "
                    "band) -- the boost arms' bias is the zone split's, not "
                    "boost's",
                    not out["alarmed"],
                    f"worst={worst}",
                )
                check_arm(out, boosted=False, converged_near=None, band=None)
                continue
            R.check(
                "two-zone: the alarm never fires (worst daily bias "
                f"{worst:.3f} C against the 0.5 C band, #42)",
                not out["alarmed"],
                f"worst={worst}",
            )
            # No band here: the two-zone learner's own walk between
            # spans is +/-5 % a night (the zone split the pre-study
            # named), so a band would measure that walk, not the freeze.
            # The freeze's own properties -- no fold inside a span,
            # resumption after -- are checked below.
            check_arm(out, boosted=True, converged_near=None, band=None)
            continue
        check_arm(out, boosted=arms[arm] != "none")
        if arms[arm] == "channel":
            channel_out = out
    if channel_out is not None:
        check_record(channel_out)
    check_freeze_units()
    check_vent_feed()
    return R.close("BOOST DRIFT CHECKS")


if __name__ == "__main__":
    sys.exit(main())
