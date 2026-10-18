"""Reviewer's probe (PR #2411 round 2), not the finder's: the transient arm of
r10_sav_baseline.py at two-zone and DHW houses, and the shoulder/summer weather."""
import sys
sys.path.insert(0, "dev/audit/harnesses")
import r10_sav_baseline as h
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
from profiles import house, prices, solve_inputs, weather

def opt_for(two_zone, dhw):
    cfg = house(two_zone=two_zone, dhw=dhw)
    p = ThermalParameters.from_config(cfg); p.dhw_enabled = dhw
    m = ThermalModel(p)
    return HeatPumpOptimizer(m, OptimizationConfig(horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"], min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"]))

for two_zone, dhw in ((False, False), (True, False), (False, True), (True, True)):
    for wx in ("winter_cold", "shoulder"):
        for pr in ("flat", "winter_narrow") if wx == "winter_cold" else ("flat",):
            try:
                opt = opt_for(two_zone, dhw)
                out, wind, rain, sol = weather(wx, h.START)
                firsts = []
                for room, slab in h.STARTS:
                    plan = opt.optimize(inputs=solve_inputs(initial_state=h._state(room, slab, float(out[0])),
                        prices=prices(pr, h.START), outdoor_temps=out, wind_speeds=wind, precipitation=rain,
                        solar_radiation=sol, start_time=h.START))
                    firsts.append(float(plan.baseline_power_schedule[0]))
                spread = max(firsts) - min(firsts)
                print(f"RESULT probe transient two_zone={two_zone} dhw={dhw} weather={wx} prices={pr} "
                      f"firsts={[round(x,2) for x in firsts]} spread={spread:.2f} {'SOUND' if spread < 0.05 else 'DEFECT'}")
            except Exception as e:
                print(f"RESULT probe transient two_zone={two_zone} dhw={dhw} weather={wx} prices={pr} ERROR {type(e).__name__}: {e}")
