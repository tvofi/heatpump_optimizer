#!/usr/bin/env python3
"""R10-HOTFIX-SAV-ESTIMATE: the valved house's month row, closed loop.

WHY IT EXISTS. The owner's November row read baseline/actual 0.14 because the
settlement books the thermostat's FIRST step of a plan re-made every interval,
and behind a valve that step read the stores' transient: a tank above the curve
zeroed it through ``valve_charge_demand``, a wood side above it through
``wood_share``, and a tank below it overshot. The reference now has no wood. No bundle data: every figure is
this synthetic install's.

Asserted arms (rc 1 on DEFECT):

  first   step 0 over the horizon mean at one outdoor, across installs and tank
          starts, and the null control: a wood house reads the plain valved
          house's kW exactly. A steady demand makes a sound first step the mean, so any ratio
          off 1 is transient. Spread across starts is no acceptance: all-zero
          first steps have spread 0 (#2411's metric read SOUND on this defect).
  valve   a valved house with no wood tank, plant equal to the model, booked
          through ``MonthlyLedger.observe_spot_and_settle_savings``: the row at a
          flat and a varying price, with its gap split into terms. Only the flat
          row is asserted, inside ``FLAT_BAND_PCT``.

Measured, not asserted: ``wood-*`` drive the same loop on a modelled wood tank.
The reference has no wood (owner ruling, 2026-11-04) and the actual stays metered,
so a positive row on these arms is wood's heat, expected, and the card says so:
firewood's cost is not counted. ``wood-unforeseen`` meters under the plan: with
wood configured the row's calibration only raises the reference (floor 1.0), and
the arm prints what the uncalibrated row reads beside it.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py [--quick] [--no-settlement] [arm ...]
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

import numpy as np

from profiles import DT, house, prices, solve_inputs, weather
from heatpump_optimizer.ledger import MonthlyLedger
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer, OptimizationConfig, _floor_demand_at_target, _reference_cop,
    _settlement_at, _thermostat_held_state,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel, ThermalParameters, ThermalState, WeatherSeries,
)

START = datetime(2026, 1, 15, 0, 0)
#: Intervals between solves; the reference is booked per interval regardless.
REPLAN = 4
DAYS = 1.0 if "--quick" in sys.argv else 2.0
#: The null control for R10-SAV-COMFORT's stored-heat settlement: book the
#: baseline and power alone, as before the plan step carried its readings.
NO_SETTLEMENT = "--no-settlement" in sys.argv
VALVE_CFG = {
    "mixing_valve_mode": "manual", "mixing_valve_target": 21.0, "buffer_tank_volume": 750.0,
    "buffer_max_temperature": 56.0, "heat_pump_max_power": 4.0,
}
WOOD_CFG = {
    **VALVE_CFG, "wood_furnace_enabled": True, "wood_tank_volume": 750.0,
    "wood_tank_top_entity": "sensor.wood_top",
}
#: Flat row's acceptance, percent: main reads tens of points past it; the terms
#: printed beside the row say what the remainder is.
FLAT_BAND_PCT = 10.0


def _install(wood: bool, two_zone: bool = True):
    cfg = dict(WOOD_CFG if wood else VALVE_CFG, two_zone_mode="on" if two_zone else "off")
    params = ThermalParameters.from_config(house(two_zone=two_zone, dhw=False, **cfg))
    assert params.two_tank_modelled is wood, "the arm's install is not the one it names"
    model = ThermalModel(params)
    return HeatPumpOptimizer(model, OptimizationConfig(
        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=17.0, max_temp=23.0,
    )), model


def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", metered=None, foresee: bool = True):
    """A solve per ``REPLAN`` on a plant equal to the model; the row and the terms."""
    opt, model = _install(wood)
    total, hs = int(DAYS * 24 / DT), int(24 / DT)
    span = total + hs + 4

    def tile(a):
        a = np.asarray(a, dtype=float)
        return np.tile(a, int(np.ceil(span / len(a))))[:span]

    pr = tile(prices(price, START))
    out, wind, rain, sol = (tile(a) for a in weather("winter_cold", START))
    ext = np.array([burn_kw(START + timedelta(hours=k * DT)) for k in range(span)], float)
    state = first = ThermalState(
        room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=float(out[0]),
        upper_floor_temperature=20.5, lower_floor_temperature=20.5,
        buffer_tank_temperature=buf0, wood_tank_temperature=wood0,
    )
    led = MonthlyLedger()
    plan_kwh = ref_kwh = plan_heat = 0.0
    rooms, states, booked_series, plan = [], [], [], None
    for k in range(total):
        now = START + timedelta(hours=k * DT)
        # The detector's bound: a fire is forecast two hours ahead, never more.
        forecast = ext[k:k + hs].copy()
        forecast[int(2.0 / DT):] = 0.0
        if not foresee:
            forecast[:] = 0.0
        series = WeatherSeries(
            outdoor_temps=out[k:k + hs], wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
            solar_radiation=sol[k:k + hs], external_heat_kw=forecast,
        )
        if k % REPLAN == 0:
            plan = opt.optimize(inputs=solve_inputs(
                initial_state=state, prices=pr[k:k + hs], outdoor_temps=out[k:k + hs],
                wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
                solar_radiation=sol[k:k + hs], start_time=now, external_heat_kw=forecast,
            ))
        power = float(plan.power_schedule[k % REPLAN])
        # The coordinator re-plans every interval, so it books step 0 of a plan
        # from THIS state; the solve is hourly for cost, the booked reference is
        # the production call a fresh solve makes.
        booked = float(opt._compute_baseline_power(series, state, DT)[0][0])
        booked_series.append(booked)
        plan_kwh += power * DT
        ref_kwh += booked * DT
        plan_heat += power * DT * model.compute_cop(
            float(out[k]), flow_temp=state.buffer_tank_temperature
        )
        meter = power * DT * (1.0 if metered is None else metered(now))
        # The production snapshot: the plan step's settlement readings (stored
        # heat, comfort, steady COP), the baseline re-read from THIS state.
        step = {} if NO_SETTLEMENT else dict(_settlement_at(plan, k % REPLAN))
        led.observe_spot_and_settle_savings(
            now, float(pr[k]), {**step, "baseline_kw": booked, "power": power}, meter, DT
        )
        led.add(now, "spot", kwh=meter, sek=meter * float(pr[k]))
        states.append((state, series))
        state = model.simulate_step(
            state, power, float(out[k]), float(wind[k]), float(rain[k]), float(sol[k]), DT,
            external_heat_kw=float(ext[k]),
        )
        rooms.append(state.room_temperature)
    row = led.savings_months(datetime(2026, 2, 1), wood_configured=wood)[0]
    print(f"  row: baseline {row['baseline_sek']} actual {row['actual_sek']} saved {row['savings_sek']} pct {row['savings_pct']}")
    print(f"  row: stored_heat_sek {row['stored_heat_sek']} comfort_sek {row['comfort_sek']}"
          f"{' (--no-settlement)' if NO_SETTLEMENT else ''}")
    # The month row's meter calibration, read off: what it does to the percent.
    raw = led.line("2026-01", "savings_baseline")["sek"]
    print(f"  calibration {row['meter_calibration']}; uncalibrated baseline {raw:.2f}, pct {(raw - row['actual_sek']) / raw * 100.0 if raw > 0 else float('nan'):.2f}")
    # The row's gap in kWh, split. Every term re-reads the same states; none is
    # fitted. Comfort is R10-SAV-COMFORT's rule: the steady thermostat at the
    # comfort target less at the room the plan delivered.
    room = float(np.mean(rooms))
    comfort = ref_heat = 0.0
    for (s, series), booked_kw, delivered in zip(states, booked_series, rooms):
        held = _thermostat_held_state(model, s, series, 21.0)
        o, w, r, g = (float(a[0]) for a in (
            series.outdoor_temps, series.wind_speeds, series.precipitation, series.solar_radiation))
        cop_ref = _reference_cop(model, held, o, None)
        ref_heat += booked_kw * DT * cop_ref
        comfort += (
            _floor_demand_at_target(model, 21.0, o, w, r, g)
            - _floor_demand_at_target(model, delivered, o, w, r, g)
        ) / cop_ref * DT
    cop = plan_heat / plan_kwh if plan_kwh > 0 else 0.0
    cop_ref_mean = ref_heat / ref_kwh if ref_kwh > 0 else 0.0
    stored = (opt._stored_thermal_energy(state) - opt._stored_thermal_energy(first)) / max(cop, 1e-9)
    settled = ref_kwh - comfort + stored
    residual = (settled - plan_kwh) / settled * 100.0 if settled > 0 else float("nan")
    print(f"  plan kWh {plan_kwh:.2f} at COP {cop:.3f}; booked reference {ref_kwh:.2f} at COP {cop_ref_mean:.3f}; gap {ref_kwh - plan_kwh:+.2f}; mean room {room:.2f} C against 21.00")
    print(f"  comfort term {comfort:+.2f} kWh_e (the reference's warmer house); stored term {stored:+.2f} kWh_e (the plan's store change)")
    print(f"  residual: reference less comfort, plus stored, {settled:.2f} kWh against plan {plan_kwh:.2f}: {residual:+.2f} %")
    return row, residual


INSTALLS = {
    "wood-valve": (True, True), "valve-only 2z": (True, False), "valve-only 1z": (False, False),
}


def first_step() -> bool:
    ok = True
    plain = None
    for name, (two_zone, wood) in reversed(list(INSTALLS.items())):
        opt, _ = _install(wood, two_zone)
        out, zero = np.full(96, -5.0), np.zeros(96)
        series = WeatherSeries(outdoor_temps=out, wind_speeds=zero, precipitation=zero, solar_radiation=zero)
        for buf in (20.0, 27.3, 40.0):
            for w0 in ((5.0, 28.0) if wood else (None,)):
                state = ThermalState(
                    room_temperature=20.0, slab_temperature=22.0, outdoor_temperature=-5.0,
                    upper_floor_temperature=20.0, lower_floor_temperature=20.0,
                    buffer_tank_temperature=buf, wood_tank_temperature=w0,
                )
                ref = opt._compute_baseline_power(series, state, DT)[0]
                ratio = float(ref[0]) / max(float(np.mean(ref)), 1e-9)
                bad = abs(ratio - 1.0) > 0.01
                if name == "valve-only 2z":
                    plain = ref
                if wood:
                    gap = float(np.abs(ref - plain).max())
                    bad = bad or gap > 1e-9
                    print(f"    null: gap to the plain valved house {gap:.2e} kW")
                ok = ok and not bad
                print(f"  {name:14s} buf {buf:5.1f} wood {w0}: step0 {ref[0]:.3f} mean {np.mean(ref):.3f} step0/mean {ratio:.3f} zero {int((ref < 1e-6).sum())}{' BAD' if bad else ''}")
    return ok


def valve_arm(price: str) -> bool:
    row, residual = closed_loop(False, lambda t: 0.0, None, 30.0, price)
    print(f"  {price}: pct {row['savings_pct']}, residual {residual:+.2f} % (rule: flat |pct| < {FLAT_BAND_PCT}; vary pct above flat by the timing saving, printed)")
    return price != "flat" or abs(row["savings_pct"]) < FLAT_BAND_PCT


ARMS = {
    "first": first_step,
    "valve-flat": lambda: valve_arm("flat"),
    "valve-vary": lambda: valve_arm("winter_typical"),
}
OWED = {
    # A fire the plan did not foresee: the pump draws half the plan while it
    # burns and the tank coasts after. The meter's fall is wood's; the row's
    # meter calibration scales the reference down by it (triage P387).
    "wood-unforeseen": lambda: closed_loop(
        True, lambda t: 12.0 if 17 <= t.hour < 21 else 0.0, 40.0, 30.0, foresee=False,
        metered=lambda t: 0.5 if 17 <= t.hour < 24 else 1.0,
    ),
    "wood-cold": lambda: closed_loop(True, lambda t: 0.0, 15.0, 30.0),
    "wood-full": lambda: closed_loop(True, lambda t: 6.0, 60.0, 30.0),
    "wood-fire": lambda: closed_loop(True, lambda t: 12.0 if 17 <= t.hour < 21 else 0.0, 40.0, 30.0),
    "wood-stale": lambda: closed_loop(True, lambda t: 0.0, 28.0, 27.3),
    "wood-coast": lambda: closed_loop(True, lambda t: 0.0, 75.0, 30.0),
}


def main(argv: list[str]) -> int:
    names = [a for a in argv if a not in ("--quick", "--no-settlement")] or list(ARMS)
    failed = []
    for name in names:
        print(name)
        if name in OWED:
            OWED[name]()
            print(f"{name}: measured, not asserted (the saving includes wood's heat; firewood not counted)")
            continue
        ok = ARMS[name]()
        print(f"{name}: {'SOUND' if ok else 'DEFECT'}")
        if not ok:
            failed.append(name)
    print(f"arms run {len(names)}, defect {len(failed)}: {' '.join(failed) or '-'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
