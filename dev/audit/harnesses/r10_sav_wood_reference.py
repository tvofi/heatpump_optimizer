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
Its meter is a stated multiplier, not the plant's: it measures the floor's
arithmetic, not the size of the heat.

``wood-plant`` measures that size (R10-SAV-WOOD-HEAT). The fire is in the plant
only (``FIRE_KW`` x ``FIRE_START_H``, ``FIRE_HOURS`` long, never forecast); the
plant pump tracks the plan's own buffer trajectory over each ``REPLAN`` hold, so
it draws less once wood carries the draw, and the meter reads
``METER_OVER_MODEL`` m times what it drew (m: the model's own meter error,
which the calibration exists to correct). The figure is the applied
calibration's error against the true m, the fire's share being that error less
the no-fire run's: ``RESULT wood_plant_error_m<m>`` with its spread over the
grid. Controls: no fire, and flat prices (the row is volume only); the
perturbation is the largest fire with the pump blind to it (meter = plan),
whose error from the heat must read zero. What it cannot show: a real pump's
control loop, a fire's coupling on a real house, or the coordinator's
per-interval re-plan (the hold is ``REPLAN`` intervals, a wider window for the
meter to leave the plan than production's one).

R10-SAV-METER-FLOOR. Every wood loop passes the pending snapshot's
``wood_heated``, so a wood month calibrates from the intervals wood did not
heat. The harness has no detector: ``_wood_heated`` reads the plant's burn,
active or within the detector's fading tail (``ExternalHeatConfig.decay_minutes``),
and ignores its confirmation lag. ``--no-wood-flag`` books no flag, a month
booked before the pair existed: the null control that must read what the merge
base reads. ``meter-floor`` (asserted) runs the valve and wood closed loops and
the wood-plant rows and requires each to publish; zeroes the booked reference
(withheld) and drops the check (``METER_FLOOR`` 0: published); runs a month
under ``MIN_CALIBRATION_KWH`` metered (published); and measures a resistive-heavy
month, an immersion's kWh added to the meter at ``IMMERSION_SHARE`` of the pump's,
printing booked over metered and whether the row is withheld.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py [--quick] [--no-settlement] [--no-wood-flag] [arm ...]
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta

import numpy as np

from profiles import DT, house, prices, solve_inputs, weather
from heatpump_optimizer import ledger as ledger_mod
from heatpump_optimizer.external_heat import ExternalHeatConfig
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
#: The null control for the wood-free calibration: no ``wood_heated`` booked.
NO_WOOD_FLAG = "--no-wood-flag" in sys.argv
#: The detector's fading tail after a burn, hours.
FADE_H = ExternalHeatConfig().decay_minutes / 60.0


def _wood_heated(ext, k: int, wood: bool):
    """The pending snapshot's ``wood_heated`` at interval k: None with no wood."""
    if not wood or NO_WOOD_FLAG:
        return None
    return bool(np.max(ext[max(0, k - int(round(FADE_H / DT))):k + 1]) > 0.0)
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


def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", metered=None, foresee: bool = True,
                zero_reference: bool = False, added_kwh: float = 0.0):
    """A solve per ``REPLAN`` on a plant equal to the model; the row and the terms.

    ``zero_reference`` books a 0 kW thermostat (the collapsed reference the
    meter floor exists for); ``added_kwh`` adds that many kWh per interval to
    the meter and the spot line, the pump's plan unchanged (an immersion).
    """
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
        meter = power * DT * (1.0 if metered is None else metered(now)) + added_kwh
        # The production snapshot: the plan step's settlement readings (stored
        # heat, comfort, steady COP), the baseline re-read from THIS state.
        step = {} if NO_SETTLEMENT else dict(_settlement_at(plan, k % REPLAN))
        led.observe_spot_and_settle_savings(
            now, float(pr[k]), {**step, "baseline_kw": 0.0 if zero_reference else booked, "power": power,
                                "wood_heated": _wood_heated(ext, k, wood)}, meter, DT
        )
        led.add(now, "spot", kwh=meter, sek=meter * float(pr[k]))
        states.append((state, series))
        state = model.simulate_step(
            state, power, float(out[k]), float(wind[k]), float(rain[k]), float(sol[k]), DT,
            external_heat_kw=float(ext[k]),
        )
        rooms.append(state.room_temperature)
    row = led.savings_months(datetime(2026, 2, 1), wood_configured=wood)[0]
    booked_kwh, metered_kwh = led.line("2026-01", "savings_baseline")["kwh"], led.line("2026-01", "savings_actual")["kwh"]
    print(f"  row: baseline {row['baseline_sek']} actual {row['actual_sek']} saved {row['savings_sek']} pct {row['savings_pct']}")
    print(f"  floor: booked over metered {booked_kwh / metered_kwh if metered_kwh > 0 else float('nan'):.3f}"
          f" ({booked_kwh:.2f} / {metered_kwh:.2f} kWh); below_meter_floor {row.get('below_meter_floor')};"
          f" calibration_basis {row.get('calibration_basis')}")
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
    return {**row, "metered_kwh": metered_kwh}, residual


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


#: The plant arm's grid: fire size kW, start hour, a 4 h burn; and the plant
#: pump's metered kWh per kWh the model books (the model's own meter error).
FIRE_KW = (4.0, 8.0, 12.0)
FIRE_START_H = (6, 17, 22)
FIRE_HOURS = 4
METER_OVER_MODEL = (0.8, 1.0, 1.2)


def _pump_response(model, state, plan_kw, args, fire_kw, target):
    """The plant pump's kW: the plan's, cut so the buffer ends no warmer than ``target``.

    Actuation is a setpoint, not a power: the pump stops charging once the
    buffer reaches the plan's own trajectory at the step's end, which the
    plan solved without the fire. Bisection on the plant's own step.
    """
    def end(p):
        return model.simulate_step(state, p, *args, external_heat_kw=fire_kw).buffer_tank_temperature
    if plan_kw <= 0.0 or end(plan_kw) <= target + 1e-9:
        return plan_kw
    if end(0.0) >= target:
        return 0.0
    lo, hi = 0.0, plan_kw
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if end(mid) <= target else (lo, mid)
    return lo


def plant_loop(burn_kw, price: str, respond: bool = True, foresee: bool = False, wood0: float = 40.0):
    """wood-plant: the fire is in the plant and not the plan; the meter is the pump's response.

    Returns, per ``METER_OVER_MODEL`` m, the row the ledger books and the
    applied calibration, plus the plant's metered and planned kWh. The plan
    books ``power``; the plant pump draws ``_pump_response`` (``respond``
    False: the plan's power, the perturbation that leaves the meter blind to
    the fire); the meter reads m times what it drew.
    """
    opt, model = _install(True)
    total, hs = int(DAYS * 24 / DT), int(24 / DT)
    span = total + hs + 4

    def tile(a):
        a = np.asarray(a, dtype=float)
        return np.tile(a, int(np.ceil(span / len(a))))[:span]

    pr = tile(prices(price, START))
    out, wind, rain, sol = (tile(a) for a in weather("winter_cold", START))
    ext = np.array([burn_kw(START + timedelta(hours=k * DT)) for k in range(span)], float)
    state = ThermalState(
        room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=float(out[0]),
        upper_floor_temperature=20.5, lower_floor_temperature=20.5,
        buffer_tank_temperature=30.0, wood_tank_temperature=wood0,
    )
    leds = {m: MonthlyLedger() for m in METER_OVER_MODEL}
    plan_kwh = drawn_kwh = fire_kwh = 0.0
    plan = None
    for k in range(total):
        now = START + timedelta(hours=k * DT)
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
        args = (float(out[k]), float(wind[k]), float(rain[k]), float(sol[k]), DT)
        # The plan's buffer at this step's end, solved at its replan: a burn
        # since then is heat the target does not know of.
        target = float(plan.buffer_temp_trajectory[k % REPLAN + 1])
        drawn = _pump_response(model, state, power, args, float(ext[k]), target) if respond else power
        booked = float(opt._compute_baseline_power(series, state, DT)[0][0])
        step = {} if NO_SETTLEMENT else dict(_settlement_at(plan, k % REPLAN))
        heated = _wood_heated(ext, k, True)
        for m, led in leds.items():
            meter = drawn * DT * m
            led.observe_spot_and_settle_savings(
                now, float(pr[k]), {**step, "baseline_kw": booked, "power": power, "wood_heated": heated}, meter, DT
            )
            led.add(now, "spot", kwh=meter, sek=meter * float(pr[k]))
        plan_kwh += power * DT
        drawn_kwh += drawn * DT
        fire_kwh += float(ext[k]) * DT
        state = model.simulate_step(state, drawn, *args, external_heat_kw=float(ext[k]))
    rows = {m: led.savings_months(datetime(2026, 2, 1), wood_configured=True)[0] for m, led in leds.items()}
    return rows, plan_kwh, drawn_kwh, fire_kwh


def _booking_error_pct(row, m) -> float:
    """The booked baseline against the one calibrated by the model's true meter error m, percent.

    Every term of ``baseline_sek`` scales with the applied calibration, so the
    oracle baseline is ``baseline_sek * m / applied``.
    """
    return (row["meter_calibration"] / m - 1.0) * 100.0


def wood_plant() -> None:
    price = "winter_typical"
    base_rows, base_plan, base_drawn, _ = plant_loop(lambda t: 0.0, price)
    flat_rows, *_ = plant_loop(lambda t: 0.0, "flat")
    print(f"  no fire ({price}): plan {base_plan:.2f} kWh, drawn {base_drawn:.2f} kWh")
    for m in METER_OVER_MODEL:
        print(f"    m {m}: pct {base_rows[m]['savings_pct']} calibration {base_rows[m]['meter_calibration']}"
              f" ({base_rows[m].get('calibration_basis')})"
              f" error {_booking_error_pct(base_rows[m], m):+.2f} %; flat pct {flat_rows[m]['savings_pct']}")
    errs = {m: [] for m in METER_OVER_MODEL}
    for kw in FIRE_KW:
        for h0 in FIRE_START_H:
            burn = (lambda kw, h0: lambda t: kw if (t.hour - h0) % 24 < FIRE_HOURS else 0.0)(kw, h0)
            rows, plan_kwh, drawn_kwh, fire_kwh = plant_loop(burn, price)
            for m in METER_OVER_MODEL:
                # The heat's own share: the error with the fire less the error without it.
                e = _booking_error_pct(rows[m], m) - _booking_error_pct(base_rows[m], m)
                errs[m].append(e)
                print(f"  fire {kw:4.1f} kW from {h0:02d}:00 ({fire_kwh:.1f} kWh_th): plan {plan_kwh:.2f} drawn {drawn_kwh:.2f};"
                      f" m {m}: calibration {rows[m]['meter_calibration']} ({rows[m].get('calibration_basis')})"
                      f" pct {rows[m]['savings_pct']}"
                      f" (no fire {base_rows[m]['savings_pct']}); booking error from the heat {e:+.2f} %")
    for m, e in errs.items():
        a = np.asarray(e)
        print(f"RESULT wood_plant_error_m{m}: mean {a.mean():+.2f} % min {a.min():+.2f} max {a.max():+.2f} sd {a.std():.2f} over {a.size} fires")
    # The perturbation: the same largest fire with the pump blind to it, the
    # meter at the plan's power; the error from the heat must read zero.
    blind, *_ = plant_loop(lambda t: 12.0 if 17 <= t.hour < 17 + FIRE_HOURS else 0.0, price, respond=False)
    print("  perturbation (pump blind to the fire): "
          + ", ".join(f"m {m} error {_booking_error_pct(blind[m], m) - _booking_error_pct(base_rows[m], m):+.2f} %"
                      for m in METER_OVER_MODEL))


#: The resistive-heavy month: an immersion's kWh per interval, as a share of
#: the valve-flat plan's mean pump kWh per interval.
IMMERSION_SHARE = (0.5, 1.0, 1.5, 2.0)


def meter_floor() -> bool:
    """R10-SAV-METER-FLOOR's acceptance; rc 1 on any arm off its expectation."""
    ok = True

    def expect(name, row, withheld):
        nonlocal ok
        got = row.get("below_meter_floor") is True and row["savings_pct"] is None
        bad = got != withheld
        ok = ok and not bad
        print(f"  {name}: {'withheld' if got else 'published'} (expected {'withheld' if withheld else 'published'})"
              f" pct {row['savings_pct']}{' BAD' if bad else ''}")
    for name in ("valve-flat", "valve-vary"):
        expect(name, closed_loop(False, lambda t: 0.0, None, 30.0, "flat" if name == "valve-flat" else "winter_typical")[0], False)
    for name, run in OWED.items():
        if name != "wood-plant":
            expect(name, run()[0], False)
    for fire in (False, True):
        burn = (lambda t: 12.0 if 17 <= t.hour < 17 + FIRE_HOURS else 0.0) if fire else (lambda t: 0.0)
        rows, *_ = plant_loop(burn, "winter_typical")
        for m, row in rows.items():
            expect(f"wood-plant {'fire 12 kW 17:00' if fire else 'no fire'} m {m}", row, False)
    flat_row, _ = closed_loop(False, lambda t: 0.0, None, 30.0, "flat")
    expect("mutant: booked reference zeroed", closed_loop(False, lambda t: 0.0, None, 30.0, "flat", zero_reference=True)[0], True)
    floor, ledger_mod.METER_FLOOR = ledger_mod.METER_FLOOR, 0.0
    try:
        expect("mutant: booked reference zeroed, check dropped (METER_FLOOR 0)",
               closed_loop(False, lambda t: 0.0, None, 30.0, "flat", zero_reference=True)[0], False)
    finally:
        ledger_mod.METER_FLOOR = floor
    expect("booked reference zeroed, metered under MIN_CALIBRATION_KWH",
           closed_loop(False, lambda t: 0.0, None, 30.0, "flat", zero_reference=True,
                       metered=lambda t: 0.0, added_kwh=0.5 / (DAYS * 24 / DT))[0], False)
    # Measured, not asserted: the immersion's share at which the floor fires.
    pump_kwh = flat_row["metered_kwh"]
    for share in IMMERSION_SHARE:
        row, _ = closed_loop(False, lambda t: 0.0, None, 30.0, "flat", added_kwh=share * pump_kwh / (DAYS * 24 / DT))
        print(f"RESULT meter_floor_immersion_share{share}: below_meter_floor {row.get('below_meter_floor')} pct {row['savings_pct']}")
    return ok


ARMS = {
    "first": first_step,
    "meter-floor": meter_floor,
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
    "wood-plant": wood_plant,
}


def main(argv: list[str]) -> int:
    names = [a for a in argv if a not in ("--quick", "--no-settlement", "--no-wood-flag")] or list(ARMS)
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
