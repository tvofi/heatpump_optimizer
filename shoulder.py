import sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components"); sys.path.insert(0, "tests/hastub")
import numpy as np
import stress
from heatpump_optimizer.thermal_model import WeatherSeries
from profiles import DT

def thermostat_cost(run):
    power, _ = run["optimizer"]._compute_baseline_power(
        WeatherSeries(outdoor_temps=run["outdoor"], wind_speeds=run["wind"],
                      precipitation=run["rain"], solar_radiation=run["solar"]),
        run["initial"], DT)
    return float(np.sum(run["prices"] * np.asarray(power) * DT))

for season in ("winter", "winter_extreme", "shoulder"):
    run = stress.case(season=season, two_zone=False, dhw=False)
    print(f"{season}: plan {run['result'].predicted_cost:.2f} thermostat {thermostat_cost(run):.2f}")
