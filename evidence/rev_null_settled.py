"""Reviewer's own probe (disclosed): the finder's r10_sav_baseline.arm_null loop, verbatim,
but the pending snapshot carries every SETTLEMENT_KEYS reading of the plan step, as the
coordinator's snapshot does. Arms: vary|const outdoor; FLATCOP=1 replaces compute_cop with
a constant (null control: the COP-timing term must vanish)."""
import os, sys
sys.path.insert(0, "dev/audit/harnesses")
from datetime import datetime, timedelta
import numpy as np
import r10_sav_baseline as h
from heatpump_optimizer.ledger import MonthlyLedger, SETTLEMENT_KEYS
from heatpump_optimizer.optimizer import _settlement_at
from heatpump_optimizer.thermal_model import WeatherSeries
from profiles import DT, prices, solve_inputs, weather
arm = sys.argv[1]; FLAT = os.environ.get("FLATCOP") == "1"; ONLY_BASE = os.environ.get("ONLY_BASE") == "1"
opt, model, _ = h._optimizer()
if FLAT:
    from heatpump_optimizer import thermal_model as tm
    tm.ThermalModel.compute_cop = lambda self, *a, **k: 3.0
days, replan = 2, 4
total = int(days * 24 / DT); span = total + int(24 / DT) + 4
tile = lambda a: np.tile(np.asarray(a, float), int(np.ceil(span / len(a))))[:span]
pr = tile(prices("flat", h.START)); out, wind, rain, sol = (tile(a) for a in weather("winter_cold", h.START))
if arm == "const":
    out = np.full_like(out, float(np.mean(out[:total])))
hs = int(24 / DT); state = h._state(21.0, 22.0, float(out[0])); led = MonthlyLedger(); plan = None
for k in range(total):
    now = h.START + timedelta(hours=k * DT)
    if k % replan == 0:
        plan = opt.optimize(inputs=solve_inputs(initial_state=state, prices=pr[k:k+hs], outdoor_temps=out[k:k+hs],
            wind_speeds=wind[k:k+hs], precipitation=rain[k:k+hs], solar_radiation=sol[k:k+hs], start_time=now))
    o = k % replan; power = float(plan.power_schedule[o])
    act = _settlement_at(plan, o)
    pending = {key: act.get(key) for key in SETTLEMENT_KEYS}
    if ONLY_BASE: pending = {"baseline_kw": pending["baseline_kw"]}
    led.observe_spot_and_settle_savings(now, float(pr[k]), pending, power * DT, DT)
    led.add(now, "spot", kwh=power * DT, sek=power * DT * float(pr[k]))
    room, slab, up, lo, *_ = model.simulate_trajectory(initial_state=state, power_schedule=np.array([power]),
        weather=WeatherSeries(outdoor_temps=out[k:k+1], wind_speeds=wind[k:k+1], precipitation=rain[k:k+1],
        solar_radiation=sol[k:k+1]), dt_hours=DT)
    state = h._state(float(room[-1]), float(slab[-1]), float(out[k]))
    state.upper_floor_temperature = float(up[-1]); state.lower_floor_temperature = float(lo[-1])
row = led.savings_months(datetime(2026, 2, 1, 0, 0))[0]
b, s, c = row["baseline_sek"], row["savings_sek"], row.get("comfort_sek", 0.0)
print(f"RESULT rev arm={arm} flatcop={FLAT} only_base={ONLY_BASE} baseline {b} actual {row['actual_sek']} saved {s} ({row['savings_pct']:.2f} %) "
      f"stored_heat_sek {row.get('stored_heat_sek')} comfort_sek {c} comfort_matched {s - c:.2f} ({(s - c) / b * 100:+.2f} %)")
