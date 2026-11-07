"""Reviewer's own instrument (not the finder's; none named): does the why-now
net push agree with what the solver did at the step, and does the top driver
agree with the solver's own space_reason? Flat-price null control included."""
import sys, collections
from datetime import datetime, timezone
import numpy as np
sys.path[:0] = ["tests/hastub", "custom_components"]
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, SolveInputs, ForecastSeries, SolveLimits
from heatpump_optimizer import slot_drivers
t0 = datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc)
hours = np.arange(96) / 4
prof = {
  "flat_null": np.full(96, 1.0),
  "daily_curve": 1.0 + 0.8 * np.sin((hours - 6) / 24 * 2 * np.pi) ** 2 + 0.6 * ((hours >= 7) & (hours < 9) | (hours >= 17) & (hours < 20)),
  "cheap_night": np.where((hours < 5), 0.3, 1.5),
  "spiky": 1.0 + 1.5 * (np.arange(96) % 12 == 0),
}
for name, prices in prof.items():
  for room in (20.0, 21.0, 22.0):
    opt = HeatPumpOptimizer(ThermalModel(ThermalParameters()), OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0))
    out = -5.0 + 3 * np.sin(hours / 24 * 2 * np.pi)
    res = opt.optimize(inputs=SolveInputs(state=ThermalState(room_temperature=room, slab_temperature=25.0, outdoor_temperature=float(out[0])), start_time=t0, forecast=ForecastSeries(prices=prices, outdoor_temps=out), limits=SolveLimits()))
    p = np.asarray(res.power_schedule)
    agree = n = topagree = 0; top = collections.Counter(); neutral = 0
    for i in range(96):
      w = slot_drivers.why_now_at(res, i)
      if w is None: continue
      net = sum(d["weight"] for d in w["drivers"])
      run = p[i] > 0.05
      if all(d["direction"] == "neutral" for d in w["drivers"]): neutral += 1; continue
      n += 1; agree += (net > 0) == run; topagree += (w['drivers'][0]['direction'] == 'run') == run
      top[(w["drivers"][0]["code"], res.space_reasons[i])] += 1
    print(f"RESULT claim profile={name} room={room} steps_non_neutral={n} all_neutral={neutral} net_push_agrees_with_run={agree}/{n} top_dir_agrees_with_run={topagree}/{n} always_idle_baseline={96-(p>0.05).sum()}/96 run_steps={(p>0.05).sum()} top_driver_vs_space_reason={dict(top.most_common(4))}", flush=True)
