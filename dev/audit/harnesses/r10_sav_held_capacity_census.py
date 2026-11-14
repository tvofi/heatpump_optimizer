"""R10-SAV-VALUATION-RESIDUE: the held state's census over every bound on the reference's heat.

    PYTHONPATH=tests/hastub:tests:custom_components \\
        python3 dev/audit/harnesses/r10_sav_held_capacity_census.py

Drives ``_thermostat_held_state`` over a grid of installs -- no valve and the
three throttling valve modes, both zonings, the derived and the
``two_tank_4way`` layout, pumps of 4, 6 and 9 kW, valve targets 21 to 40 C,
outdoor -25 to 18 C -- and books one reference step from each held state at
``_compute_baseline_power``'s power on a one-step horizon (nothing to
apportion). The property is the phenomenon's, not an instance's: a held state
the reference step can keep draws no stored heat on its first booked step.
Prints the case count, the worst first-step store change in kWh_th and the
count over 0.02 kWh_th, then the capacity control: at -25 C a 9 kW pump holds
21 C (valved and not), a 4 kW pump does not.

Preconditions, asserted (exit 1): every grid case ran without an exception,
every held room lies in [min(outdoor, 21), 21], and the case count is the
grid's product.
"""

import itertools
import sys

import numpy as np

from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer,
    OptimizationConfig,
    _thermostat_held_state,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
    WeatherSeries,
)
from profiles import house

TARGET_C = 21.0
MODES = ("none", "manual", "smart_read", "smart_write")
ZONINGS = (True, False)
LAYOUTS = (None, "two_tank_4way")
PUMPS_KW = (4.0, 6.0, 9.0)
VALVE_TARGETS_C = (21.0, 25.0, 30.0, 40.0)
OUTDOORS_C = (-25.0, -15.0, -5.0, 0.0, 5.0, 10.0, 14.0, 16.0, 18.0)


def first_step(mode, two_zone, layout, pump_kw, valve_target, outdoor):
    """The held state and its first booked reference step's store change, kWh_th."""
    cfg = {"buffer_tank_volume": 750.0, "buffer_max_temperature": 56.0,
           "heat_pump_max_power": pump_kw}
    if mode != "none":
        cfg.update(mixing_valve_mode=mode, mixing_valve_target=valve_target)
    if layout:
        cfg["topology_layout"] = layout
    model = ThermalModel(ThermalParameters.from_config(house(two_zone=two_zone, dhw=False, **cfg)))
    opt = HeatPumpOptimizer(model, OptimizationConfig(
        horizon_hours=1, time_step_minutes=15, target_temp=TARGET_C))
    weather = WeatherSeries(outdoor_temps=np.array([outdoor]), wind_speeds=np.zeros(1),
                            precipitation=np.zeros(1), solar_radiation=np.zeros(1))
    start = ThermalState(room_temperature=20.5, slab_temperature=22.0,
                         outdoor_temperature=outdoor, upper_floor_temperature=20.5,
                         lower_floor_temperature=20.5, buffer_tank_temperature=30.0)
    held = _thermostat_held_state(model, start, weather, TARGET_C)
    power = float(opt._compute_baseline_power(weather, start, 0.25)[0][0])
    nxt = model.simulate_step(held, power, outdoor, 0.0, 0.0, 0.0, 0.25)
    return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), power


def main() -> int:
    grid = list(itertools.product(MODES, ZONINGS, LAYOUTS, PUMPS_KW, VALVE_TARGETS_C, OUTDOORS_C))
    ran, worst, worst_case, over, refused = 0, 0.0, None, 0, []
    for case in grid:
        try:
            held, ds, power = first_step(*case)
        except Exception as exc:  # a refusal is a precondition failure, reported
            refused.append((case, repr(exc)[:120]))
            continue
        ran += 1
        outdoor = case[-1]
        if not min(outdoor, TARGET_C) - 1e-9 <= held.room_temperature <= TARGET_C:
            refused.append((case, f"held room {held.room_temperature:.3f} out of range"))
        if abs(ds) > abs(worst):
            worst, worst_case = ds, (*case, round(held.room_temperature, 3), round(power, 3))
        over += abs(ds) > 0.02
    print(f"RESULT census: cases {ran} of {len(grid)}, worst first-step dS {worst:+.4f} kWh_th "
          f"at {worst_case}, over 0.02 kWh_th {over}")
    for mode in ("none", "manual"):
        for pump_kw in (4.0, 9.0):
            held, ds, power = first_step(mode, True, None, pump_kw, 40.0, -25.0)
            print(f"RESULT control two-zone -25 C mode={mode} pump {pump_kw} kW: held room "
                  f"{held.room_temperature:.3f} power {power:.3f} first-step dS {ds:+.4f} kWh_th")
    for case, why in refused[:10]:
        print("REFUSED", case, why)
    return 1 if refused or ran != len(grid) else 0


if __name__ == "__main__":
    sys.exit(main())
