#!/usr/bin/env python3
"""R10-SAV-BASELINE (#2255): the savings month table, measured through the production symbols.

WHY IT EXISTS. The owner's screenshot (2026-10-14) showed three defects in the
Savings tab: September saved 81 % against a plain thermostat, October's
estimate was negative with a baseline below the actual, and the closed month's
receipt total disagreed with the table's Actual for the same month. The
screenshot is the finding's only evidence; this harness is the instrument that
reproduces each arm on the tree it runs against, so a later seat can re-take
it at its own merge base.

Arms (each prints one line per figure, then its verdict):

  transient  The settlement books ``baseline_power_schedule[i]`` of the plan
             covering the interval, i.e. the thermostat's FIRST step from the
             plan's actual start state. One flat-price plan per start state:
             a counterfactual that is a thermostat running all along does not
             depend on where the optimiser left the house, so the spread of
             step 0 across start states is the defect's size (0 when sound).
  cost       A closed month with every billed line plus one interval no plan
             covered: the row's ``actual_sek`` against the receipt's
             ``total_sek`` (equal when sound).
  coverage   An install that settled 24 hours of a 672-hour month: the open
             row's scale against month hours over settled hours.
  null       The flat-price null control (owner-required): a closed loop on a
             plant that matches the model, every interval booked through
             ``MonthlyLedger.observe_spot_and_settle_savings`` exactly as the
             coordinator books it; the published savings percentage should
             read about 0 at a flat price.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline.py [arm ...]

With no arm named, all four run. ``null`` is the slow one (one solve per
re-plan over the loop).
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

import numpy as np

from profiles import DT, house, prices, solve_inputs, weather
from heatpump_optimizer.ledger import MonthlyLedger, freeze_month_report
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
)

START = datetime(2026, 1, 15, 0, 0)
#: Start states (room, slab) for the transient arm: at target, below it by
#: one and two kelvin (the optimiser coasting), above it (pre-heated).
STARTS = ((21.0, 22.0), (20.0, 21.0), (19.0, 20.0), (22.0, 23.5))


def _optimizer(dhw: bool = False) -> tuple[HeatPumpOptimizer, ThermalModel, dict]:
    cfg = house(two_zone=False, dhw=dhw)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    model = ThermalModel(params)
    opt = HeatPumpOptimizer(model, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    ))
    return opt, model, cfg


def _state(room: float, slab: float, outdoor: float) -> ThermalState:
    return ThermalState(
        room_temperature=room, slab_temperature=slab, outdoor_temperature=outdoor,
        upper_floor_temperature=room, lower_floor_temperature=room,
        dhw_temperature=52.0, dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )


def arm_transient() -> bool:
    opt, _, _ = _optimizer()
    out, wind, rain, sol = weather("winter_cold", START)
    firsts = []
    for room, slab in STARTS:
        plan = opt.optimize(inputs=solve_inputs(
            initial_state=_state(room, slab, float(out[0])),
            prices=prices("flat", START), outdoor_temps=out, wind_speeds=wind,
            precipitation=rain, solar_radiation=sol, start_time=START,
        ))
        first = float(plan.baseline_power_schedule[0])
        firsts.append(first)
        print(f"transient: start room {room} slab {slab}: booked baseline step 0 = {first:.2f} kW")
    spread = max(firsts) - min(firsts)
    print(f"transient: spread of the booked step across start states = {spread:.2f} kW")
    return spread < 0.05


def arm_cost() -> bool:
    led = MonthlyLedger()
    base = datetime(2026, 9, 12, 3, 0)
    for i, baseline_kw in enumerate((2.0, 2.0, None)):
        t = base.replace(hour=3 + i)
        led.observe_spot_and_settle_savings(
            t, 1.0, {"baseline_kw": baseline_kw, "grid_fee": 0.4}, 1.5, 1.0
        )
        led.add(t, "spot", kwh=1.25, sek=1.25)
        led.add(t, "immersion", kwh=0.25, sek=0.25)
        led.add(t, "grid_fee", kwh=1.5, sek=0.6)
    led.book_capacity("2026-09", 3.0, 2.5)
    led.add(base, "wear", kwh=0.0, sek=1.2)
    receipt = freeze_month_report(led, "2026-09", compressor_starts=1, contract_comparison={})
    row = led.savings_months(datetime(2026, 10, 3, 12, 0))[0]
    print(f"cost: receipt total_sek = {receipt['total_sek']}; row actual_sek = {row['actual_sek']}")
    return row["actual_sek"] == receipt["total_sek"]


def arm_coverage() -> bool:
    led = MonthlyLedger()
    t0 = datetime(2026, 2, 9, 15, 0)
    for h in range(24):
        t = t0 + timedelta(hours=h)
        led.observe_spot_and_settle_savings(t, 1.0, {"baseline_kw": 2.0}, 1.0, 1.0)
        led.add(t, "spot", kwh=1.0, sek=1.0)
    row = led.savings_months(datetime(2026, 2, 10, 15, 0))[0]
    scale = row["actual_sek"] / 24.0
    print(f"coverage: 24 settled hours of 672; open-row scale = {scale:.2f} (month hours / settled = 28.00)")
    return abs(scale - 28.0) < 1e-6


def arm_null(days: int = 2, replan: int = 4) -> bool:
    """Flat price, plant == model: the booked saving is the baseline's own bias."""
    opt, model, _ = _optimizer()
    total = int(days * 24 / DT)
    span = total + int(24 / DT) + 4

    def tile(a):
        a = np.asarray(a, dtype=float)
        return np.tile(a, int(np.ceil(span / len(a))))[:span]

    pr = tile(prices("flat", START))
    out, wind, rain, sol = (tile(a) for a in weather("winter_cold", START))
    hs = int(24 / DT)
    state = _state(21.0, 22.0, float(out[0]))
    led = MonthlyLedger()
    plan = None
    for k in range(total):
        now = START + timedelta(hours=k * DT)
        if k % replan == 0:
            plan = opt.optimize(inputs=solve_inputs(
                initial_state=state, prices=pr[k:k + hs], outdoor_temps=out[k:k + hs],
                wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
                solar_radiation=sol[k:k + hs], start_time=now,
            ))
        o = k % replan
        power = float(plan.power_schedule[o])
        pending = {"baseline_kw": float(plan.baseline_power_schedule[o])}
        led.observe_spot_and_settle_savings(now, float(pr[k]), pending, power * DT, DT)
        led.add(now, "spot", kwh=power * DT, sek=power * DT * float(pr[k]))
        room, slab, up, lo, _, _, _ = model.simulate_trajectory(
            initial_state=state, power_schedule=np.array([power]),
            weather=WeatherSeries(outdoor_temps=out[k:k + 1], wind_speeds=wind[k:k + 1],
                                  precipitation=rain[k:k + 1], solar_radiation=sol[k:k + 1]),
            dt_hours=DT,
        )
        state = _state(float(room[-1]), float(slab[-1]), float(out[k]))
        state.upper_floor_temperature = float(up[-1])
        state.lower_floor_temperature = float(lo[-1])
    row = led.savings_months(datetime(2026, 2, 1, 0, 0))[0]
    print(
        f"null: flat price, {days} days, re-plan every {replan * DT:.2f} h: "
        f"baseline {row['baseline_sek']} actual {row['actual_sek']} saved {row['savings_sek']} "
        f"({row['savings_pct']} %)"
    )
    return row["savings_pct"] is not None and abs(row["savings_pct"]) < 3.0


ARMS = {"transient": arm_transient, "cost": arm_cost, "coverage": arm_coverage, "null": arm_null}


def main(argv: list[str]) -> int:
    names = argv or list(ARMS)
    failed = []
    for name in names:
        ok = ARMS[name]()
        print(f"{name}: {'SOUND' if ok else 'DEFECT'}")
        if not ok:
            failed.append(name)
    print(f"arms run {len(names)}, defect {len(failed)}: {' '.join(failed) or '-'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
