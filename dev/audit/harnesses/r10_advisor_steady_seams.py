#!/usr/bin/env python3
"""R10-ADVISOR-STEADY-START (#2257): the steady figure on the fixtures its other harnesses do not read.

WHY IT EXISTS. The design note (55f90c7c6) left four items to measure, and the
fix review at 7c7f06081 measured two of them open. Each arm reads one item and
its null control, through the functions ``async_simulate``'s branch calls
(``whatif.schedule_days``, ``price_tiles.schedule_figure``,
``price_tiles.monthly_deltas(steady=)``) on tests/profiles.py houses; it does
not go through ``async_simulate``.

  weekday  item weekday-day: one schedule ask, asked at 09:00 on each day of a
           week, same prices and weather every day, with weekend comfort
           temperatures configured. The figure must be one figure across the
           seven days and never leave the schedule branch. Null: no weekend
           comfort. Then every ask at hours 01..23 step 2 of a Friday: rows
           against the ask, rows rounding to 0.00 (a weekend night a mild day
           barely binds), rows reading the pair.
  fields   item measured-fields: the schedule figure's spread over measured
           starts, one field moved at a time (rooms, slab, hot-water tank,
           buffer, wood tank), on a single-zone house, a two-zone house, a
           throttling valve on one tank and a throttling-valve two-tank house.
           The one-tank valve fixture's thermostat never reaches its setpoint
           (the ``holds`` line prints the room it settles at), so its day
           setpoints tie and two passes do not settle it: that row reads the
           thermostat reference on such a house, not the schedule arithmetic. Null: the same start twice.
  pair     item pair-other-asks: the steady pair's figure for a hot-water ask
           alone on a tanked house, by measured start and by hour. Null: the
           room and slab start (columns 1 and 2), which the held start holds.
  pv       item pv-price: a schedule ask on a house with a PV surplus forecast
           against the same house without one: the mean-price figure, which
           reads no surplus, beside the same energy at each what-if plan's own
           average purchase price.
  wall     what the week costs: ``reference_day``'s wall a call, and how many
           distinct days a week holds (each is one pair of thermostat passes),
           with and without weekend comfort. Two calls a what-if, on the loop.

Run from the tree root:

  PYTHONPATH=tests/hastub:tests:custom_components \
      python3 dev/audit/harnesses/r10_advisor_steady_seams.py [weekday|fields|pair|pv|wall ...]

No argument runs all five. Every figure is a month's money in the fixture's
price unit; re-run rather than carry a number.
"""
from __future__ import annotations

import statistics
import sys
import time
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r10_advisor_degree as deg  # noqa: E402
from profiles import DT, house, solve_inputs  # noqa: E402

from heatpump_optimizer import mixing_valve, optimizer, price_tiles, whatif  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

N = deg.N
PRICES, WEATHER = deg._series(3, False)
MONDAY = datetime(2026, 1, 5)
HOURS = range(1, 24, 2)
SCHEDULE_ASKS = (
    ("day-1", {"comfort_temp_day": 20.0}, -1), ("day+1", {"comfort_temp_day": 22.0}, 1),
    ("night-1", {"comfort_temp_night": 18.5}, -1), ("night+1", {"comfort_temp_night": 20.5}, 1),
    ("daystart-1h", {"day_start_hour": -1}, 1), ("dayend-1h", {"day_end_hour": -1}, -1),
)
WEEKEND = {"comfort_temp_day_weekend": 22.0, "comfort_temp_night_weekend": 20.0}
WEEKEND_ASKS = (("wkday+1", {"comfort_temp_day_weekend": 23.0}, 1), ("wknight-1", {"comfort_temp_night_weekend": 19.0}, -1))


def build(two_zone=False, dhw=False, valve=False, **config):
    params = ThermalParameters.from_config(house(two_zone=two_zone, dhw=dhw))
    if not dhw:
        params.dhw_enabled = False
    if valve:
        params.mixing_valve_mode = sorted(mixing_valve.THROTTLING_MODES)[0]
        params.wood_tank_configured, params.wood_tank_volume = True, 500.0
        assert mixing_valve.is_throttling(params.mixing_valve_mode) and params.two_tank_modelled == two_zone
    kw = dict(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0,
              comfort_temp_day=21.0, comfort_temp_night=19.5)
    kw.update(config)
    return HeatPumpOptimizer(ThermalModel(params), OptimizationConfig(**kw)), params


def start(room=21.0, slab=22.0, dhw=52.0, buffer=40.0, wood=50.0):
    return ThermalState(
        room_temperature=room, slab_temperature=slab, outdoor_temperature=0.0, upper_floor_temperature=room,
        lower_floor_temperature=room, dhw_temperature=dhw, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=buffer, wood_tank_temperature=wood)


def inputs(hour, state, day=MONDAY, pv=None):
    j = int(hour / DT)
    cut = slice(j, j + N)
    return solve_inputs(
        initial_state=state, prices=PRICES[cut], outdoor_temps=WEATHER[0][cut], wind_speeds=WEATHER[1][cut],
        precipitation=WEATHER[2][cut], solar_radiation=WEATHER[3][cut],
        start_time=day + timedelta(hours=j * DT), pv_surplus=pv)


def shadow(opt, params, asked):
    config, scratch = whatif.scratch_copies(opt.config, params, asked)
    return HeatPumpOptimizer(ThermalModel(scratch), config)


def asks(opt, extra=()):
    out = []
    for name, asked, want in SCHEDULE_ASKS + tuple(extra):
        asked = {k: getattr(opt.config, k) + v if k.endswith("_hour") else v for k, v in asked.items()}
        out.append((name, asked, want))
    return out


def figure(opt, params, asked, given):
    """The schedule figure of one ask, or None when the ask leaves the schedule branch."""
    days = whatif.schedule_days((shadow(opt, params, {}), given), (shadow(opt, params, asked), given))
    if days is None:
        return None
    return price_tiles.schedule_figure(*days, float(np.mean(given.forecast.prices)), 0.0, 24.0)[whatif.STEADY_KEY]


def arm_weekday():
    for label, config in (("weekend comfort set", WEEKEND), ("null, no weekend comfort", {})):
        opt, params = build(**config)
        moved = pairs = 0
        for name, asked, _want in asks(opt, WEEKEND_ASKS if config else ()):
            week = [figure(opt, params, asked, inputs(9, start(), MONDAY + timedelta(days=d))) for d in range(7)]
            pairs += sum(f is None for f in week)
            moved += len({f for f in week if f is not None}) > 1
            print(f"  weekday {label}: {name} asked 09:00 Mon..Sun: "
                  + " ".join("pair" if f is None else f"{f:+.1f}" for f in week))
        print(f"RESULT weekday {label}: asks whose figure moves with the weekday {moved}, "
              f"asks leaving the schedule branch on some day {pairs}")
    opt, params = build(**WEEKEND)
    friday, rows, wrong, pairs, zero = MONDAY + timedelta(days=4), 0, 0, 0, 0
    for hour in HOURS:
        for _name, asked, want in asks(opt, WEEKEND_ASKS):
            f = figure(opt, params, asked, inputs(hour, start(), friday))
            rows += 1
            pairs += f is None
            wrong += f is not None and f * want < 0
            zero += f == 0
    print(f"RESULT weekday friday: rows {rows} against the ask {wrong} rounding to 0.00 {zero} reading the pair {pairs}")


def arm_fields():
    moves = (("null (same start)", {}), ("rooms 20.4", {"room": 20.4}), ("slab 19.0", {"slab": 19.0}),
             ("hot water 42", {"dhw": 42.0}), ("buffer 30", {"buffer": 30.0}), ("buffer 55", {"buffer": 55.0}),
             ("wood tank 75", {"wood": 75.0}))
    for label, kw in (("single-zone", {}), ("two-zone", {"two_zone": True}),
                      ("valve, one tank", {"valve": True}), ("two-zone valve two-tank", {"two_zone": True, "valve": True})):
        opt, params = build(**kw)
        worst = dict.fromkeys((m[0] for m in moves), 0.0)
        rows = wrong = 0
        for hour in HOURS:
            for _name, asked, want in asks(opt):
                base = figure(opt, params, asked, inputs(hour, start()))
                rows += 1
                wrong += base is None or base * want <= 0
                for move, change in moves:
                    other = figure(opt, params, asked, inputs(hour, start(**change)))
                    worst[move] = max(worst[move], abs(other - base))
        weather = optimizer._day_mean_weather(optimizer._horizon_weather(inputs(9, start()).forecast, N), N)
        _, held = opt._compute_baseline_power(weather, start(), DT, np.full(N, 21.0))
        _, held = opt._compute_baseline_power(weather, start(), DT, np.full(N, 21.0), start=held)
        print(f"  fields {label} holds: a thermostat set to 21.0 all day ends its second pass with the room at "
              f"{held.room_temperature:.2f}")
        print(f"RESULT fields {label}: rows {rows} at 0 or against the ask {wrong}; largest move of the figure by start: "
              + ", ".join(f"{m} {v:.2f}" for m, v in worst.items()))


def arm_pair():
    opt, params = build(dhw=True)
    starts = (start(), start(20.4, 21.3), start(dhw=44.0), start(dhw=58.0))
    for name, asked in (("dhw_setpoint 55 to 60", {"dhw_setpoint": 60.0}), ("dhw_setpoint 55 to 50", {"dhw_setpoint": 50.0}),
                        ("dhw_min_temperature 45 to 50", {"dhw_min_temperature": 50.0})):
        signs, widest, rooms = set(), 0.0, 0.0
        for hour in (1, 9, 17):
            figs = []
            for state in starts:
                given = replace(inputs(hour, state), held_start=True)
                assert whatif.schedule_days((shadow(opt, params, {}), given), (shadow(opt, params, asked), given)) is None
                live, sim = (shadow(opt, params, a).optimize(inputs=given) for a in ({}, asked))
                figs.append(price_tiles.monthly_deltas(live, sim, 0.0, 24.0, steady=(live, sim))[whatif.STEADY_KEY])
            signs |= {f > 0 for f in figs}
            widest, rooms = max(widest, max(figs) - min(figs)), max(rooms, abs(figs[1] - figs[0]))
            print(f"  pair {name} {hour:02d}:00 by start (base, rooms coasted, tank 44, tank 58): "
                  + " ".join(f"{f:+.1f}" for f in figs))
        print(f"RESULT pair {name}: both signs {len(signs) == 2}, widest spread by start {widest:.1f}, "
              f"moved by the room and slab start (null) {rooms:.1f}")


def arm_pv():
    opt, params = build()
    surplus = np.array([2.5 * max(0.0, np.sin((h % 24 - 8) * np.pi / 8)) if 8 <= h % 24 <= 16 else 0.0
                        for h in np.arange(len(PRICES)) * DT])
    for name, asked, _want in asks(opt)[:2]:
        for label, pv in (("null, no surplus", None), ("surplus to 2.5 kW, 08..16", surplus)):
            for hour in (1, 9):
                given = inputs(hour, start(), pv=None if pv is None else pv[int(hour / DT):int(hour / DT) + N])
                days = whatif.schedule_days((shadow(opt, params, {}), given), (shadow(opt, params, asked), given))
                sim = shadow(opt, params, asked).optimize(inputs=given)
                out = price_tiles.schedule_figure(
                    *days, float(np.mean(given.forecast.prices)), 0.0, 24.0, price_tiles.realised_price(sim, DT))
                print(f"RESULT pv {name} {hour:02d}:00 {label}: mean-price figure {out[whatif.STEADY_KEY]:+.1f} "
                      f"own-price figure {out[price_tiles.SHIFTED_KEY]:+.1f} "
                      f"plan's average purchase price {price_tiles.realised_price(sim, DT):.3f} "
                      f"mean price {float(np.mean(given.forecast.prices)):.3f}")


def arm_wall():
    for label, config in (("no weekend comfort", {}), ("weekend comfort set", WEEKEND)):
        opt, _params = build(**config)
        walls, distinct = [], set()
        for hour in HOURS:
            for d in range(7):
                given = inputs(hour, start(), MONDAY + timedelta(days=d))
                began = time.perf_counter()
                week, _kwh = opt.reference_day(given)
                walls.append((time.perf_counter() - began) * 1e3)
                distinct.add(len({tuple(week[k:k + N]) for k in range(0, 7 * N, N)}))
        print(f"RESULT wall {label}: reference_day calls {len(walls)} median {statistics.median(walls):.1f} ms "
              f"max {max(walls):.1f} ms on this host, distinct days in a week {min(distinct)}..{max(distinct)}")


ARMS = {"weekday": arm_weekday, "fields": arm_fields, "pair": arm_pair, "pv": arm_pv, "wall": arm_wall}

if __name__ == "__main__":
    for arm in sys.argv[1:] or list(ARMS):
        ARMS[arm]()
