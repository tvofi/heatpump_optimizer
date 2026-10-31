"""The stress suite's `shoulder` economics check, both ends, same code path.

`tests/stress.py`'s Economics section does exactly this:

    run = case(season=season, two_zone=False, dhw=False)
    baseline = thermostat_cost(run)          # _compute_baseline_power
    R.check(..., result.predicted_cost < baseline, ...)

This driver calls the same `stress.case` and the same two expressions, so the
two numbers it prints are the two the check compares. Nothing is re-implemented.

usage: shoulder.py <tree-root>
"""
import sys

import numpy as np

ROOT = sys.argv[1]
sys.path[:0] = [ROOT + "/tests", ROOT + "/tests/hastub", ROOT + "/custom_components"]

import stress  # noqa: E402
from profiles import DT  # noqa: E402
from heatpump_optimizer.thermal_model import WeatherSeries  # noqa: E402


def thermostat_cost(run: dict) -> float:
    power, _ = run["optimizer"]._compute_baseline_power(
        WeatherSeries(outdoor_temps=run["outdoor"], wind_speeds=run["wind"],
                      precipitation=run["rain"], solar_radiation=run["solar"]),
        run["initial"], DT,
    )
    return float(np.sum(run["prices"] * np.asarray(power) * DT))


for season in ("winter", "winter_extreme", "shoulder"):
    run = stress.case(season=season, two_zone=False, dhw=False)
    res = run["result"]
    base = thermostat_cost(run)
    p = run["optimizer"].model.params
    print(
        f"{season:15s} predicted {res.predicted_cost:.4f}  thermostat {base:.4f}  "
        f"cheaper {res.predicted_cost < base}  "
        f"| buffer {p.buffer_tank_volume:.0f} L  valve {p.mixing_valve_mode!r} "
        f"target {p.mixing_valve_target}"
    )
