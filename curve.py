import sys, copy
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests/hastub")
import numpy as np
import stress
from profiles import solve_inputs
from heatpump_optimizer.optimizer import HeatPumpOptimizer

base = stress.case(season="winter", two_zone=False, dhw=False)
for w in (5.0, 10.0, 20.0, 40.0):
    cfg = copy.copy(base["config"]); cfg.comfort_weight = w
    r = HeatPumpOptimizer(base["model"], cfg).optimize(inputs=solve_inputs(
        initial_state=base["initial"], prices=base["prices"], outdoor_temps=base["outdoor"],
        wind_speeds=base["wind"], precipitation=base["rain"], solar_radiation=base["solar"],
        start_time=stress.START))
    print(f"w={w:.0f}: room {float(np.mean(r.room_temp_trajectory)):.2f} C  savings {r.savings_percentage:.1f}%")
