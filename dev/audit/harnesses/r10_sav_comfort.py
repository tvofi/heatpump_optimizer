#!/usr/bin/env python3
"""R10-SAV-COMFORT (#2492): the flat-price null, split into comfort, COP timing and stored heat.

WHY IT EXISTS. ``r10_sav_baseline.py null`` booked 10.83 % saved on a flat
price with the plant equal to the model, and the carry from R10-SAV-BASELINE
asked for the residual to be separated, not driven to 0: (a) comfort -- the
plan holds the house below the comfort schedule; (b) COP timing -- the plan
heats in the warmer hours, a real saving that must survive; (c) stored heat
the window leaves unsettled. This harness books the same closed loop through
``MonthlyLedger.observe_spot_and_settle_savings`` as the coordinator books it,
and prints each term beside the booked figure:

  comfort  the plan's mean room against the mean comfort target, and the
           booked thermostat's kWh against a steady thermostat at the comfort
           target and at the room the plan delivered (``_floor_demand_at_target``
           over ``compute_cop``, step by step).
  stored   the plan's house heat at the end of the booked window less at its
           start, kWh_th, settled at the window's steady COP (thermal loss
           at the delivered room over the steady thermostat's kWh).
  timing   the plan's power-weighted COP against the booked thermostat's.

The loop runs ``warmup`` unbooked days first, so booking starts from the
plan's own operating state and not from the harness's start state.

Arms:

  const  outdoor held at the window mean: no timing to buy, so the booked
         saving with stored heat settled reads about 0 (SOUND below 1.5 %).
  vary   the ``winter_cold`` profile: the settled saving reads the timing
         term -- the energy a thermostat at the plan's COP would have saved,
         1 - cop_thermostat / cop_plan -- not 0 (SOUND within 2 points of it,
         and above 3 %).

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_comfort.py [const|vary ...]
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r10_sav_baseline as h  # noqa: E402
from heatpump_optimizer.ledger import MonthlyLedger  # noqa: E402
from heatpump_optimizer.optimizer import _floor_demand_at_target  # noqa: E402
from heatpump_optimizer.thermal_model import WeatherSeries  # noqa: E402
from profiles import DT, prices, solve_inputs, weather  # noqa: E402


def run(arm: str, warmup: int = 1, days: int = 2, replan: int = 4) -> bool:
    opt, model, _ = h._optimizer()
    pm = model.params
    skip = int(warmup * 24 / DT)
    total = skip + int(days * 24 / DT)
    hs = int(24 / DT)
    span = total + hs + 4

    def tile(a):
        a = np.asarray(a, dtype=float)
        return np.tile(a, int(np.ceil(span / len(a))))[:span]

    pr = tile(prices("flat", h.START))
    out, wind, rain, sol = (tile(a) for a in weather("winter_cold", h.START))
    if arm == "const":
        out = np.full_like(out, float(np.mean(out[skip:total])))
    state = h._state(21.0, 22.0, float(out[0]))
    led = MonthlyLedger()
    plan = None
    rooms, targets = [], []
    kwh_plan = kwh_base = at_target = at_room = loss_th = copw_plan = copw_base = 0.0
    heat0 = None
    for k in range(total):
        now = h.START + timedelta(hours=k * DT)
        if k % replan == 0:
            plan = opt.optimize(inputs=solve_inputs(
                initial_state=state, prices=pr[k:k + hs], outdoor_temps=out[k:k + hs],
                wind_speeds=wind[k:k + hs], precipitation=rain[k:k + hs],
                solar_radiation=sol[k:k + hs], start_time=now,
            ))
        o = k % replan
        power = float(plan.power_schedule[o])
        base = float(plan.baseline_power_schedule[o])
        room0 = state.room_temperature
        room, slab, up, lo, *_ = model.simulate_trajectory(
            initial_state=state, power_schedule=np.array([power]),
            weather=WeatherSeries(outdoor_temps=out[k:k + 1], wind_speeds=wind[k:k + 1],
                                  precipitation=rain[k:k + 1], solar_radiation=sol[k:k + 1]),
            dt_hours=DT,
        )
        if k >= skip:
            if heat0 is None:
                heat0 = pm.room_thermal_mass * room0 + pm.slab_thermal_mass * state.slab_temperature
            tgt = opt.config.get_comfort_temp(now.hour + now.minute / 60.0, when=now)
            cop = model.compute_cop(float(out[k]))
            args = (float(out[k]), float(wind[k]), float(rain[k]), float(sol[k]))
            mid = 0.5 * (room0 + float(room[-1]))
            q_room = max(0.0, _floor_demand_at_target(model, mid, *args))
            at_target += max(0.0, _floor_demand_at_target(model, tgt, *args)) / cop * DT
            at_room += q_room / cop * DT
            loss_th += q_room * DT
            kwh_plan += power * DT
            kwh_base += base * DT
            copw_plan += power * cop * DT
            copw_base += base * cop * DT
            targets.append(tgt)
            rooms.append(float(room[-1]))
            led.observe_spot_and_settle_savings(now, float(pr[k]), {"baseline_kw": base}, power * DT, DT)
            led.add(now, "spot", kwh=power * DT, sek=power * DT * float(pr[k]))
        state = h._state(float(room[-1]), float(slab[-1]), float(out[k]))
        state.upper_floor_temperature = float(up[-1])
        state.lower_floor_temperature = float(lo[-1])
    heat1 = pm.room_thermal_mass * state.room_temperature + pm.slab_thermal_mass * state.slab_temperature
    row = led.savings_months(h.START + timedelta(days=60))[0]
    steady_cop = loss_th / at_room
    drawn_e = (heat0 - heat1) / steady_cop
    settled = (kwh_base - kwh_plan - drawn_e) / kwh_base * 100.0
    cop_plan, cop_base = copw_plan / kwh_plan, copw_base / kwh_base
    timing = (1.0 - cop_base / cop_plan) * 100.0
    print(f"{arm}: booked row (production ledger): baseline {row['baseline_sek']} actual "
          f"{row['actual_sek']} saved {row['savings_pct']:.2f} %")
    print(f"{arm}: comfort: plan mean room {np.mean(rooms):.2f} C vs mean target {np.mean(targets):.2f} C; "
          f"booked thermostat {kwh_base:.1f} kWh vs steady at target {at_target:.1f}, "
          f"steady at the delivered room {at_room:.1f}")
    print(f"{arm}: stored: plan house heat drawn {heat0 - heat1:+.1f} kWh_th = {drawn_e:+.1f} kWh_e "
          f"at the steady COP {steady_cop:.3f}")
    print(f"{arm}: timing: power-weighted COP plan {cop_plan:.3f} thermostat {cop_base:.3f}; "
          f"timing saving {timing:+.2f} %")
    print(f"{arm}: booked kWh: thermostat {kwh_base:.1f} plan {kwh_plan:.1f}; "
          f"saving with stored heat settled {settled:+.2f} % against timing {timing:+.2f} %")
    if arm == "const":
        return abs(settled) < 1.5
    return settled > 3.0 and abs(settled - timing) < 2.0


def main(argv: list[str]) -> int:
    names = argv or ["const", "vary"]
    failed = []
    for name in names:
        ok = run(name)
        print(f"{name}: {'SOUND' if ok else 'DEFECT'}")
        if not ok:
            failed.append(name)
    print(f"arms run {len(names)}, defect {len(failed)}: {' '.join(failed) or '-'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
