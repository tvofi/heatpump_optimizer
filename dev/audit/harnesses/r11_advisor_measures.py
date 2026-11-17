#!/usr/bin/env python3
"""R11-ADVISOR-MEASURES (#2257): the what-if's steady figure on the asks and houses R10 left unmeasured.

WHY IT EXISTS. ``r10_advisor_steady_seams.py`` measured the hot-water pair and the
schedule estimate on single fixtures. Three seams stayed open (#3481 items
128b800e and c33b6f10); each arm reads one and its null control, through the
functions ``async_simulate``'s branch calls (``whatif.schedule_days``,
``price_tiles.schedule_figure``, ``price_tiles.monthly_deltas(steady=)``) on
tests/profiles.py houses, never through ``async_simulate``.

  asks   item pair-other-asks: the steady pair's figure for each ask the card
         prices by two plans -- the hot-water setpoint and minimum, the comfort
         weight, the lowest allowed temperature -- on a house with a hot-water
         tank, by hour and by the tank's measured temperature. Each row is
         split into what the pair spends on space heat and on hot water. A row
         is against its ask when its sign opposes the one physics gives it (a
         cooler setpoint or floor, a lighter weight: a saving or nothing).
         Nulls: the same ask on the house without a tank (column ``no tank``),
         and a hot-water setpoint moved half a degree, whose rows read the
         pair's own resolution.
  valve  item measured-fields x weekday-day: the schedule estimate on a
         throttling-valve two-tank house with weekend comfort temperatures, each
         ask asked at 09:00 on each day of a week and at every odd hour of a
         Friday. Null: the same house without weekend comfort.
  pv     item pv-price: a schedule ask on a house with a PV surplus forecast.
         The estimate's two ends (the mean price, the what-if plan's own average
         purchase price) beside the same reference-day thermostats priced at
         each step's own surplus-aware price (``_energy_cost_fn``), which is
         what the mean price stands in for. Null: the same house without a
         surplus.

  loop   the truth ``asks`` is read against: the tanked house's plan run closed-loop
         four days after a warm-up day, re-solved every four hours from where its
         own trajectory put the house, per ask against the live configuration,
         each loop's drift in stored heat over its measured days bought back. The
         null row (the half-degree setpoint) is the loop's own resolution: a truth
         inside it resolves no sign.
  pvloop the same loop for the ``pv`` arm's two schedule asks, with and without the
         surplus, beside the estimate's two ends asked at 09:00 of each loop day.

Run from the tree root:

  PYTHONPATH=tests/hastub:tests:custom_components \\
      python3 dev/audit/harnesses/r11_advisor_measures.py [asks|valve|pv|loop|pvloop ...]

No argument runs all five; ``asks`` is slow (about 180 solves), the loops slower
(30 solves an ask, one process each). Every figure is
a month's money in the fixture's price unit; re-run rather than carry a number.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r10_advisor_steady_seams as seams  # noqa: E402

from heatpump_optimizer import price_tiles, whatif  # noqa: E402

DT = seams.DT
HOURS = (1, 5, 9, 13, 17, 21)
#: (label, ask, the sign physics gives its steady money; 0 = none claimed).
PAIR_ASKS = (
    ("dhw_setpoint 55 to 50", {"dhw_setpoint": 50.0}, -1),
    ("dhw_setpoint 55 to 60", {"dhw_setpoint": 60.0}, 1),
    ("dhw_min_temperature 45 to 50", {"dhw_min_temperature": 50.0}, 1),
    ("comfort_weight 5 to 2.5", {"comfort_weight": 2.5}, -1),
    ("comfort_weight 5 to 10", {"comfort_weight": 10.0}, 1),
    ("min_temp 17 to 16", {"min_temp": 16.0}, -1),
    ("min_temp 17 to 18", {"min_temp": 18.0}, 1),
    ("null: dhw_setpoint 55 to 55.5", {"dhw_setpoint": 55.5}, 0),
)
TANKS = (("tank 52", 52.0), ("tank 44", 44.0), ("tank 58", 58.0))


def _split(live, sim):
    """The pair's spend difference split by channel: space heat and hot water at each step's price."""
    prices = np.asarray(live.prices, dtype=float)

    def channel(r, dhw):
        p = np.asarray((r.dhw_power_schedule or [0.0] * len(prices)) if dhw else r.power_schedule, dtype=float)
        return float(np.sum(p * prices[: len(p)]) * DT)

    return tuple(price_tiles.per_month(channel(sim, d) - channel(live, d), 24.0) for d in (False, True))


def _pair(opt, params, asked, given):
    assert whatif.schedule_days((seams.shadow(opt, params, {}), given), (seams.shadow(opt, params, asked), given)) is None
    live, sim = (seams.shadow(opt, params, a).optimize(inputs=given) for a in ({}, asked))
    return price_tiles.monthly_deltas(live, sim, 0.0, 24.0, steady=(live, sim))[whatif.STEADY_KEY], _split(live, sim)


def arm_asks():
    tanked, tanked_p = seams.build(dhw=True)
    bare, bare_p = seams.build()
    for name, asked, want in PAIR_ASKS:
        rows = against = 0
        figs, space_share = [], []
        for hour in HOURS:
            cells = []
            for _label, tank in TANKS:
                fig, (space, dhw) = _pair(tanked, tanked_p, asked, replace(seams.inputs(hour, seams.start(dhw=tank)), held_start=True))
                rows += 1
                against += want != 0 and fig * want < 0
                figs.append(fig)
                space_share.append(abs(space) / max(abs(space) + abs(dhw), 1e-9))
                cells.append(f"{fig:+7.1f} (space {space:+6.1f} hot water {dhw:+6.1f})")
            bare_cell = ""
            if not any(k.startswith("dhw_") for k in asked):
                bare_fig, _ = _pair(bare, bare_p, asked, replace(seams.inputs(hour, seams.start()), held_start=True))
                bare_cell = f" | no tank {bare_fig:+7.1f}"
            print(f"  asks {name} {hour:02d}:00 by tank: " + "  ".join(cells) + bare_cell)
        print(f"RESULT asks {name}: rows {rows} against the ask {against}, range {min(figs):+.1f}..{max(figs):+.1f}, "
              f"median share of the moved spend that is space heat {float(np.median(space_share)):.2f}")


def arm_valve():
    for label, config in (("weekend comfort set", seams.WEEKEND), ("null, no weekend comfort", {})):
        opt, params = seams.build(two_zone=True, valve=True, **config)
        moved = pairs = wrong = zero = 0
        for name, asked, want in seams.asks(opt, seams.WEEKEND_ASKS if config else ()):
            week = [seams.figure(opt, params, asked, seams.inputs(9, seams.start(), seams.MONDAY + timedelta(days=d)))
                    for d in range(7)]
            pairs += sum(f is None for f in week)
            moved += len({f for f in week if f is not None}) > 1
            wrong += sum(f is not None and f * want < 0 for f in week)
            zero += sum(f == 0 for f in week)
            print(f"  valve {label}: {name} asked 09:00 Mon..Sun: " + " ".join("pair" if f is None else f"{f:+.1f}" for f in week))
        print(f"RESULT valve {label}: asks whose figure moves with the weekday {moved}, days against the ask {wrong}, "
              f"days at 0.00 {zero}, days leaving the schedule branch {pairs}")
    opt, params = seams.build(two_zone=True, valve=True, **seams.WEEKEND)
    friday, rows, wrong, pairs, zero = seams.MONDAY + timedelta(days=4), 0, 0, 0, 0
    for hour in seams.HOURS:
        for _name, asked, want in seams.asks(opt, seams.WEEKEND_ASKS):
            f = seams.figure(opt, params, asked, seams.inputs(hour, seams.start(), friday))
            rows += 1
            pairs += f is None
            wrong += f is not None and f * want < 0
            zero += f == 0
    print(f"RESULT valve friday: rows {rows} against the ask {wrong} at 0.00 {zero} reading the pair {pairs}")
    weather = seams.optimizer._day_mean_weather(seams.optimizer._horizon_weather(seams.inputs(9, seams.start()).forecast, seams.N), seams.N)
    for set_to in (21.0, 22.0, 23.0):
        _, held = opt._compute_baseline_power(weather, seams.start(), DT, np.full(seams.N, set_to))
        _, held = opt._compute_baseline_power(weather, seams.start(), DT, np.full(seams.N, set_to), start=held)
        print(f"RESULT valve holds: a thermostat set to {set_to:.1f} all day ends its second pass with the rooms at "
              f"{held.upper_floor_temperature:.2f} and {held.lower_floor_temperature:.2f}")


def _thermostat_cost(side, given):
    """What the reference day's thermostat (its second pass, ``reference_day``'s) pays at each
    step's own surplus-aware price (``_energy_cost_fn``); ``side`` has solved ``given``."""
    weather = seams.optimizer._day_mean_weather(seams.optimizer._horizon_weather(given.forecast, seams.N), seams.N)
    when, hours = seams.optimizer._step_clock(given.start_time, seams.N, DT)
    comfort = side._build_comfort_bounds(hours, seams.N, None, None, when)[0]
    _, settled = side._compute_baseline_power(weather, given.state, DT, comfort)
    power, _ = side._compute_baseline_power(weather, given.state, DT, comfort, start=settled)
    return float(side._energy_cost_fn(np.asarray(given.forecast.prices[: seams.N], dtype=float), DT)(power))


def arm_pv():
    opt, params = seams.build()
    surplus = np.array([2.5 * max(0.0, np.sin((h % 24 - 8) * np.pi / 8)) if 8 <= h % 24 <= 16 else 0.0
                        for h in np.arange(len(seams.PRICES)) * DT])
    for name, asked, _want in seams.asks(opt)[:2]:
        for label, pv in (("null, no surplus", None), ("surplus to 2.5 kW, 08..16", surplus)):
            for hour in (1, 9):
                j = int(hour / DT)
                given = seams.inputs(hour, seams.start(), pv=None if pv is None else pv[j:j + seams.N])
                days = whatif.schedule_days((seams.shadow(opt, params, {}), given), (seams.shadow(opt, params, asked), given))
                sim_opt = seams.shadow(opt, params, asked)
                sim = sim_opt.optimize(inputs=given)
                out = price_tiles.schedule_figure(
                    *days, float(np.mean(given.forecast.prices)), 0.0, 24.0, price_tiles.realised_price(sim, DT))
                live = seams.shadow(opt, params, {})
                live.optimize(inputs=given)
                ref = price_tiles.per_month(_thermostat_cost(sim_opt, given) - _thermostat_cost(live, given), 24.0)
                lo, hi = sorted((out[whatif.STEADY_KEY], out[price_tiles.SHIFTED_KEY]))
                closer = "own-price" if abs(out[price_tiles.SHIFTED_KEY] - ref) < abs(out[whatif.STEADY_KEY] - ref) else "mean-price"
                print(f"RESULT pv {name} {hour:02d}:00 {label}: mean-price {out[whatif.STEADY_KEY]:+.1f} "
                      f"own-price {out[price_tiles.SHIFTED_KEY]:+.1f} thermostat at each step's surplus-aware price {ref:+.1f}; "
                      f"inside the range {lo <= ref <= hi}, closer end {closer}")


LOOP_DAYS, RESOLVE_STEPS = 4, 16


def _surplus(n):
    """A PV surplus forecast to 2.5 kW from 08 to 16 every day, ``n`` steps."""
    return np.array([2.5 * max(0.0, np.sin((h % 24 - 8) * np.pi / 8)) if 8 <= h % 24 <= 16 else 0.0
                     for h in np.arange(n) * DT])


def _loop(asked, dhw=True, pv=False):
    """(daily spend, stored-heat drift over the measured days: room, slab, tank) of the house's plan run closed-loop for ``LOOP_DAYS`` days after
    one warm-up day, re-solved every ``RESOLVE_STEPS`` steps from where the plan's own trajectory put the
    house (the model is the truth here), each solve from the measured state, never a held one."""
    base, params = seams.build(dhw=dhw)
    opt = seams.shadow(base, params, asked)
    prices, (o, w, r, sr) = deg_series(full=True)
    surplus = _surplus(len(prices)) if pv else None
    state, spend = seams.start(), 0.0
    for j in range(0, (LOOP_DAYS + 1) * seams.N, RESOLVE_STEPS):
        if j == seams.N:
            measured = state
        cut = slice(j, j + seams.N)
        plan = opt.optimize(inputs=seams.solve_inputs(
            initial_state=replace(state), prices=prices[cut], outdoor_temps=o[cut], wind_speeds=w[cut],
            precipitation=r[cut], solar_radiation=sr[cut], start_time=seams.MONDAY + timedelta(hours=j * DT),
            pv_surplus=None if surplus is None else surplus[cut]))
        k = RESOLVE_STEPS
        if j >= seams.N:
            drawn = np.asarray(plan.power_schedule[:k]) + np.asarray(plan.dhw_power_schedule[:k] or np.zeros(k))
            # What the grid charges: the plan's own surplus-aware pricing of the steps it ran.
            spend += float(opt._energy_cost_fn(np.asarray(prices[j:j + k]), DT)(drawn)) if surplus is not None else \
                float(np.sum(drawn * prices[j:j + k]) * DT)
        state = replace(state, room_temperature=plan.room_temp_trajectory[k], slab_temperature=plan.slab_temp_trajectory[k],
                        upper_floor_temperature=plan.upper_temp_trajectory[k], lower_floor_temperature=plan.lower_temp_trajectory[k],
                        dhw_temperature=plan.dhw_temp_trajectory[k] if plan.dhw_temp_trajectory else state.dhw_temperature,
                        outdoor_temperature=float(o[j + k]))
    return spend / LOOP_DAYS, tuple(getattr(state, f) - getattr(measured, f) for f in
                                    ("room_temperature", "slab_temperature", "dhw_temperature"))


def _loop_one(item):
    name, asked, kw = item
    daily, end = _loop(asked, **kw)
    return name, daily, end


def arm_loop():
    """The truth the pair is read against: each ask's closed loop against the live one's."""
    from concurrent.futures import ProcessPoolExecutor

    items = [("live", {}, {})] + [(n, a, {}) for n, a, _w in PAIR_ASKS]
    with ProcessPoolExecutor() as pool:
        done = dict((n, (d, e)) for n, d, e in pool.map(_loop_one, items))
    params = seams.build(dhw=True)[1]
    prices, o = deg_series()
    live_daily, live_end = done["live"]
    model = seams.ThermalModel(params)
    cop = model.compute_cop(float(np.mean(o)))
    for name, asked, want in PAIR_ASKS:
        daily, end = done[name]
        stored = (params.room_thermal_mass * (end[0] - live_end[0]) + params.slab_thermal_mass * (end[1] - live_end[1])
                  + params.dhw_store.capacity_kwh_per_c * (end[2] - live_end[2]))
        # Each loop's own change in stored heat over its measured days, beyond the live loop's, bought back
        # at the mean price and COP: a steady state's level is no debt, a drift over the window is.
        settled = daily - live_daily - stored / cop * float(np.mean(prices)) / LOOP_DAYS
        month = price_tiles.per_month(settled, 24.0)
        print(f"RESULT loop {name}: closed-loop steady money {month:+.1f} a month "
              f"(unsettled {price_tiles.per_month(daily - live_daily, 24.0):+.1f}), against the ask "
              f"{want != 0 and month * want < 0}")


def deg_series(full=False):
    """The loop's prices and weather: ``r10_advisor_degree``'s days, a warm-up and a horizon longer."""
    import r10_advisor_degree as deg

    prices, wx = deg._series(LOOP_DAYS + 2, False)
    return (prices, wx) if full else (prices, wx[0])


def _ends(opt, params, asked, j, pv):
    """The schedule estimate's two ends asked at step ``j`` of the loop's series."""
    prices, (o, w, r, sr) = deg_series(full=True)
    cut = slice(j, j + seams.N)
    given = seams.solve_inputs(
        initial_state=seams.start(), prices=prices[cut], outdoor_temps=o[cut], wind_speeds=w[cut],
        precipitation=r[cut], solar_radiation=sr[cut], start_time=seams.MONDAY + timedelta(hours=j * DT),
        pv_surplus=_surplus(len(prices))[cut] if pv else None)
    days = whatif.schedule_days((seams.shadow(opt, params, {}), given), (seams.shadow(opt, params, asked), given))
    sim = seams.shadow(opt, params, asked).optimize(inputs=given)
    out = price_tiles.schedule_figure(*days, float(np.mean(given.forecast.prices)), 0.0, 24.0, price_tiles.realised_price(sim, DT))
    return out[whatif.STEADY_KEY], out[price_tiles.SHIFTED_KEY]


def arm_pvloop():
    """The truth the pv arm's range is read against: a schedule ask's closed loop on the house with and
    without the surplus, beside the estimate's two ends at the loop's first solve."""
    from concurrent.futures import ProcessPoolExecutor

    opt, params = seams.build()
    named = seams.asks(opt)[:2]
    items = [(f"{label} {n}", a, {"dhw": False, "pv": pv}) for label, pv in (("null", False), ("pv", True))
             for n, a in (("live", {}),) + tuple((n, a) for n, a, _w in named)]
    with ProcessPoolExecutor() as pool:
        done = {n: (d, e) for n, d, e in pool.map(_loop_one, items)}
    prices, o = deg_series()
    cop = seams.ThermalModel(params).compute_cop(float(np.mean(o)))
    for label, pv in (("null", False), ("pv", True)):
        live_daily, live_end = done[f"{label} live"]
        for name, asked, _want in named:
            daily, end = done[f"{label} {name}"]
            stored = params.room_thermal_mass * (end[0] - live_end[0]) + params.slab_thermal_mass * (end[1] - live_end[1])
            truth = price_tiles.per_month(daily - live_daily - stored / cop * float(np.mean(prices)) / LOOP_DAYS, 24.0)
            ends = np.mean([_ends(opt, params, asked, d * seams.N + int(9 / DT), pv) for d in range(1, LOOP_DAYS + 1)], axis=0)
            print(f"RESULT pvloop {label} {name}: closed-loop steady money {truth:+.1f} a month; the estimate asked "
                  f"at 09:00 of each loop day, mean-price {ends[0]:+.1f} own-price {ends[1]:+.1f}")


ARMS = {"asks": arm_asks, "valve": arm_valve, "pv": arm_pv, "loop": arm_loop, "pvloop": arm_pvloop}

if __name__ == "__main__":
    for arm in sys.argv[1:] or list(ARMS):
        ARMS[arm]()
