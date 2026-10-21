#!/usr/bin/env python3
"""R10-ADVISOR (#2257): the price of a degree, at the merge base's tile and at the head's.

WHY IT EXISTS. The owner's Advisor screenshot (2026-10-14) read "a degree
cooler is cheaper, about 140 SEK/month" over "a degree warmer costs -266
SEK/month more", and the figures swung day to day. This harness is the
instrument for both, so a later seat can re-take it at its own merge base.

Arms (each prints RESULT lines, then the arm's verdict):

  days   A 40-day sequence of day-ahead prices (the suite's SE3 profiles in
         rotation) and outdoor temperatures (a mild January shifted by a
         9-day swing), the live house starting each day where a plan may
         have left it. Per day, both degree tiles, two ways:
           base  the merge base's tile: ``target_temp`` alone moved one
                 kelvin, the plan's single-solve spend difference scaled to
                 a month (``async_simulate``'s ``monthly_cost_delta``);
           head  ``price_tiles.specs`` (the whole comfort schedule moved),
                 ``price_tiles.monthly_figure`` reading the held figure the head's
                 ``async_simulate`` publishes (the thermostat baselines'
                 difference, ``price_tiles.per_month``), and the published
                 figure ``price_tiles.published`` averages over the horizon.
         Counted per arm: days whose pair is not monotone (a cooler degree
         that does not save, or a warmer one that does not cost), and the
         day-to-day spread; for the head, the spread of the published mean.
  null   Closed loops, three days each, at the comfort schedule moved -1, 0
         and +1 K: a flat price and a constant outdoor temperature, so the
         plan has no timing to exploit. Its realised cost per degree it
         delivers (cost difference over room-mean difference) is the truth
         the held figure must read; beside it, the plan's spend difference of
         each loop's first solve (from that loop's own state, per degree). ``timing`` is the same loop with
         the outdoor temperature's daily swing, where buying in warmer hours
         is a real saving the held figure does not claim.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_degree.py [days] [null] [timing]

The null's 15 % is the loop's own error: the stored heat each loop drew is
bought back at the window's mean price and COP, not at what refilling it
would cost. With no arm named, ``days`` runs. ``null`` and ``timing`` are slow (about
300 solves each).
"""
from __future__ import annotations

import copy
import math
import sys
from datetime import datetime, timedelta

import numpy as np

from profiles import DT, house, prices, solve_inputs, weather
from heatpump_optimizer import price_tiles
from heatpump_optimizer.coordinator import _SIM_OVERRIDE_CONFIG_CASTS
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
)

START = datetime(2026, 1, 5, 0, 0)
N = int(24 / DT)
PRICE_DAYS = ("winter_typical", "winter_moderate", "winter_narrow", "shoulder",
              "winter_extreme", "winter_typical", "flat")
#: Where the live plan may have left the house when a tile solves: at the
#: target, coasted below it, pre-heated above it.
STARTS = ((21.0, 22.0), (20.4, 21.3), (21.7, 23.0))


def _optimizer() -> tuple[HeatPumpOptimizer, ThermalModel]:
    cfg = house(two_zone=False, dhw=False)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    model = ThermalModel(params)
    return HeatPumpOptimizer(model, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
        comfort_temp_day=cfg["target_temperature"], comfort_temp_night=19.5,
    )), model


def _shadow(opt: HeatPumpOptimizer, model: ThermalModel, overrides: dict) -> HeatPumpOptimizer:
    """The scratch optimizer ``async_simulate`` builds: its override loop, verbatim."""
    config = copy.deepcopy(opt.config)
    for key, cast in _SIM_OVERRIDE_CONFIG_CASTS:
        if key in overrides:
            setattr(config, key, cast(overrides[key]))
    return HeatPumpOptimizer(ThermalModel(copy.deepcopy(model.params)), config)


def _state(room: float, slab: float, outdoor: float) -> ThermalState:
    return ThermalState(
        room_temperature=room, slab_temperature=slab, outdoor_temperature=outdoor,
        upper_floor_temperature=room, lower_floor_temperature=room,
        dhw_temperature=52.0, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )


def _day(k: int) -> tuple[np.ndarray, tuple[np.ndarray, ...], str]:
    profile = PRICE_DAYS[k % len(PRICE_DAYS)]
    o, w, r, s = weather("winter_mild", START)
    shift = 6.0 * math.sin(2.0 * math.pi * k / 9.0)
    return prices(profile, START), (o + shift, w, r, s), profile


def _spread(xs: list[float]) -> str:
    a = np.asarray(xs, float)
    return f"std {a.std():.1f} range {a.min():+.1f}..{a.max():+.1f}"


def arm_days() -> bool:
    opt, model = _optimizer()
    hours = opt.config.horizon_hours
    base_rows: list[tuple[float, float]] = []
    head_rows: list[tuple[float, float]] = []
    book: dict = {}
    published: list[tuple[float, float]] = []
    for k in range(40):
        pr, (o, w, r, s), profile = _day(k)
        room, slab = STARTS[k % len(STARTS)]
        st = _state(room, slab, float(o[0]))
        kw = dict(prices=pr, outdoor_temps=o, wind_speeds=w, precipitation=r,
                  solar_radiation=s, start_time=START + timedelta(days=k))
        live = opt.optimize(inputs=solve_inputs(initial_state=copy.deepcopy(st), **kw))
        target = float(opt.config.target_temp)
        base_pair = []
        for step in (-1.0, 1.0):
            sim = _shadow(opt, model, {"target_temp": round(target + step, 1)}).optimize(
                inputs=solve_inputs(initial_state=copy.deepcopy(st), **kw))
            base_pair.append(price_tiles.per_month(sim.predicted_cost - live.predicted_cost, hours))
        head_pair = []
        for name, overrides in price_tiles.specs(opt.config, 6.0)[:2]:
            sim = _shadow(opt, model, overrides).optimize(
                inputs=solve_inputs(initial_state=copy.deepcopy(st), **kw))
            answer = {
                "monthly_cost_delta": price_tiles.per_month(sim.predicted_cost - live.predicted_cost, hours),
                "monthly_held_cost_delta": price_tiles.per_month(sim.baseline_cost - live.baseline_cost, hours),
            }
            head_pair.append(price_tiles.monthly_figure(overrides, answer))
            price_tiles.record(book, name, overrides, answer, kw["start_time"])
        view = price_tiles.published(book, kw["start_time"].date())
        published.append((view["target_minus_1"]["monthly_cost_delta"],
                          view["target_plus_1"]["monthly_cost_delta"]))
        base_rows.append(tuple(base_pair))
        head_rows.append(tuple(head_pair))
        print(f"RESULT day {k:2d} {profile:15s} outdoor {float(np.mean(o)):+5.1f} start {room:4.1f} "
              f"base {base_pair[0]:+7.1f} {base_pair[1]:+7.1f} | head {head_pair[0]:+7.1f} {head_pair[1]:+7.1f} "
              f"| published {published[-1][0]:+7.1f} {published[-1][1]:+7.1f}", flush=True)

    def bad(rows: list[tuple[float, float]]) -> int:
        return sum(1 for down, up in rows if not (down < 0.0 < up))

    settled = published[price_tiles.HORIZON_DAYS - 1:]
    print(f"RESULT days base non_monotone {bad(base_rows)}/40 warmer_not_costing "
          f"{sum(1 for _d, up in base_rows if up <= 0.0)}/40 "
          f"cooler {_spread([d for d, _u in base_rows])} warmer {_spread([u for _d, u in base_rows])}")
    print(f"RESULT days head non_monotone {bad(head_rows)}/40 "
          f"cooler {_spread([d for d, _u in head_rows])} warmer {_spread([u for _d, u in head_rows])}")
    print(f"RESULT days head published over days {price_tiles.HORIZON_DAYS}-40 non_monotone {bad(settled)}/{len(settled)} "
          f"cooler {_spread([d for d, _u in settled])} warmer {_spread([u for _d, u in settled])}")
    ok = bad(head_rows) == 0 and bad(settled) == 0
    print(f"VERDICT days {'head monotone every day' if ok else 'head NOT monotone'}; base non-monotone on "
          f"{bad(base_rows)} of 40 days")
    return ok


def _loop(offset: float, pr: np.ndarray, wx: tuple[np.ndarray, ...], days: int) -> tuple[float, float, object]:
    """(settled cost, mean room, first solve) of the plan run ``days`` at the schedule moved ``offset``."""
    base, model = _optimizer()
    opt = _shadow(base, model, dict(price_tiles.specs(base.config, 6.0))["target_plus_1"]) if offset > 0 else (
        _shadow(base, model, dict(price_tiles.specs(base.config, 6.0))["target_minus_1"]) if offset < 0 else base)
    o, w, r, s = wx
    state = _state(21.0 + offset, 22.0 + offset, float(o[0]))
    total = days * N
    cost = room_sum = 0.0
    first = plan = None
    # One warm-up day first, so the measured loop starts at the policy's own steady state.
    for k in range(-N, total):
        kk = k % N if k < 0 else k
        if k % 4 == 0:
            sl = slice(kk, kk + N)
            plan = opt.optimize(inputs=solve_inputs(
                initial_state=copy.deepcopy(state), prices=pr[sl], outdoor_temps=o[sl], wind_speeds=w[sl],
                precipitation=r[sl], solar_radiation=s[sl], start_time=START + timedelta(hours=k * DT)))
            if k == 0:
                first = plan
        p = float(plan.power_schedule[k % 4])
        if k == 0:
            s0 = (state.room_temperature, state.slab_temperature)
        if k >= 0:
            cost += p * pr[kk] * DT
            room_sum += state.room_temperature
        room, slab, up, lo, *_ = model.simulate_trajectory(
            initial_state=state, power_schedule=np.array([p]), dt_hours=DT,
            weather=WeatherSeries(outdoor_temps=o[kk:kk + 1], wind_speeds=w[kk:kk + 1],
                                  precipitation=r[kk:kk + 1], solar_radiation=s[kk:kk + 1]))
        state = _state(float(room[-1]), float(slab[-1]), float(o[kk]))
        state.upper_floor_temperature, state.lower_floor_temperature = float(up[-1]), float(lo[-1])
    pm = model.params
    drawn = pm.room_thermal_mass * (s0[0] - state.room_temperature) + pm.slab_thermal_mass * (s0[1] - state.slab_temperature)
    # The stored heat the loop drew from (or added to) the house, bought back at the mean price.
    settled = cost + drawn / model.compute_cop(float(np.mean(o[:total]))) * float(np.mean(pr[:total]))
    return settled, room_sum / total, first


def arm_loop(name: str, flat_outdoor: bool) -> bool:
    days = 3
    pr = np.full((days + 1) * N, 1.20)
    o, w, r, s = (np.tile(a, days + 1) for a in weather("winter_mild", START))
    if flat_outdoor:
        o = np.full_like(o, float(np.mean(o[:days * N])))
    runs = {off: _loop(off, pr, (o, w, r, s), days) for off in (-1.0, 0.0, 1.0)}
    month = 30.4 / days
    base = runs[0.0]
    ok = True
    for off in (-1.0, 1.0):
        cost, room, first = runs[off]
        truth = (cost - base[0]) * month / (room - base[1])
        held = price_tiles.per_month(first.baseline_cost - base[2].baseline_cost, 24.0) * off
        plan = price_tiles.per_month(first.predicted_cost - base[2].predicted_cost, 24.0) * off
        gap = (held - truth) / abs(truth) * 100.0
        print(f"RESULT {name} offset {off:+.0f} delivered {room - base[1]:+.3f} K truth_per_delivered_degree "
              f"{truth:+.1f} held {held:+.1f} ({gap:+.1f} %) first_solve_plan {plan:+.1f}")
        ok = ok and abs(gap) < 15.0
    kind = "" if flat_outdoor else " (informational: the plan's timing gain is real here)"
    print(f"VERDICT {name}{kind} held figure {'within' if ok else 'NOT within'} 15 % of the plan's "
          "realised price per delivered degree")
    # Only the null is a pass/fail: with the outdoor swing the plan's timing
    # gain is real, and the gap it opens is the measurement, not a defect.
    return ok or not flat_outdoor


if __name__ == "__main__":
    arms = sys.argv[1:] or ["days"]
    results = []
    for arm in arms:
        if arm == "days":
            results.append(arm_days())
        elif arm == "null":
            results.append(arm_loop("null", flat_outdoor=True))
        elif arm == "timing":
            results.append(arm_loop("timing", flat_outdoor=False))
        else:
            raise SystemExit(f"unknown arm {arm}")
    sys.exit(0 if all(results) else 1)
