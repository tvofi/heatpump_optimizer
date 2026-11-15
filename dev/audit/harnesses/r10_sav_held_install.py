"""R10-SAV-VALUATION-RESIDUE Carry 9: the reference's held room beside the plant's own ceiling.

    PYTHONPATH=tests/hastub:tests:custom_components \\
        python3 dev/audit/harnesses/r10_sav_held_install.py

Two houses behind a throttling valve, target 21 C, at +5, -5 and -15 C
outdoor (wind 3 m/s, no rain or sun):

  install   the owner replay's own configuration (``profiles.replay_install``:
            two zones, valve ``manual`` at 21 C, 4 kW pump, 500 l buffer).
  one-tank  the synthetic fixture pull request 3481's ``fields`` arm builds
            (``profiles.house()``, single zone, the first throttling mode, a
            500 l wood tank, valve target unset).

Per row: ``held`` is ``_thermostat_held_state``'s room, upper and lower floor;
``end`` the same three where ``_compute_baseline_power``'s 96-step day ends;
``plant`` where ``simulate_step`` at ``max_electrical_power`` for 288 steps
from the held state leaves them -- the plant's own ceiling, its tank at the
cap. ``gap`` is the largest of the six held-to-end and held-to-plant moves, K.
The control is ``valve off``: the install with ``mixing_valve_mode`` none,
whose held floors read 21.000 (no plant column: an unvalved pump at its
maximum has no ceiling below the target).

Precondition, asserted (exit 1): every held room lies in [outdoor, 21].
"""

import sys

import numpy as np

from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig, _thermostat_held_state
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
from profiles import house, replay_install

STEPS, DT_H, WIND = 96, 0.25, 3.0


def one_tank():
    cfg = house(dhw=False)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    params.mixing_valve_mode = "manual"
    params.wood_tank_configured, params.wood_tank_volume = True, 500.0
    return params


def zones(s):
    return (s.room_temperature, s.upper_floor_temperature, s.lower_floor_temperature)


def row(label, params, outdoor, ceiling=True):
    model = ThermalModel(params)
    opt = HeatPumpOptimizer(model, OptimizationConfig(horizon_hours=24, time_step_minutes=15, target_temp=21.0))
    w = WeatherSeries(outdoor_temps=np.full(STEPS, outdoor), wind_speeds=np.full(STEPS, WIND),
                      precipitation=np.zeros(STEPS), solar_radiation=np.zeros(STEPS))
    start = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=outdoor,
                         upper_floor_temperature=21.0, lower_floor_temperature=21.0,
                         buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
    held = _thermostat_held_state(model, start, w, 21.0)
    end = opt._compute_baseline_power(w, start, DT_H, np.full(STEPS, 21.0))[1]
    fmt = lambda s: "/".join(f"{v:.3f}" for v in zones(s))  # noqa: E731
    line = f"{label} {outdoor:+.0f} C: held {fmt(held)} end {fmt(end)}"
    if ceiling:
        plant = held
        for _ in range(3 * STEPS):
            plant = model.simulate_step(plant, params.max_electrical_power, outdoor, WIND, 0.0, 0.0, DT_H)
        gap = max(abs(a - b) for other in (end, plant) for a, b in zip(zones(held), zones(other)))
        line += f" plant {fmt(plant)} gap {gap:.3f}"
    print(line)
    return min(outdoor, 21.0) <= held.room_temperature <= 21.0


def main():
    ok = True
    for outdoor in (5.0, -5.0, -15.0):
        ok &= row("install", ThermalParameters.from_config(replay_install()), outdoor)
        ok &= row("valve off", ThermalParameters.from_config(replay_install(mixing_valve_mode="none")), outdoor, False)
        ok &= row("one-tank", one_tank(), outdoor)
    if not ok:
        print("PRECONDITION FAILED: a held room outside [outdoor, 21]")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
