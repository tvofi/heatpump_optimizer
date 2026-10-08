#!/usr/bin/env python3
"""The COP learner's duty floor against an overstated nameplate maximum.

Drives the real coordinator's ``_learn_measured_cop`` with synthetic
intervals (the pump draws what the plan commanded) on a 14 kW-nameplate
install whose pump really runs at 1.9-2.55 kW, with a 1.0 kW modulation
floor and with an overstated 3.0 kW one, outside the frost band. The 3.0 kW
rows are the remaining gap this fix does not close: the floor is 2.4 kW
there, and capping it at the observed running draw is the power-clamp
seat's ``draw_range`` consumer (live-fix design note, S4). Run it from a worktree root, at the base and
at the head:

    PYTHONPATH=tests/hastub:custom_components:tests \
        python3 tools/audit/harnesses/cop_duty_floor.py

Rows: the floor in kW, then, per draw class, how many of its intervals
folded into ``cop_samples``. ``running`` is the defect (0 at the base);
``idle`` and ``standby`` are what the floor exists to refuse, and the
``liveness`` row is the null control: a 4 kW nameplate whose old floor
(1.2 kW) already admitted 2.2 kW, so a zero at the base is the floor and
not a learner that cannot fold. The sweep prints, for floors k x p_min, how
many standby and running draws each would admit (the constant's choice).
"""
from __future__ import annotations

import sys

sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import on_threshold_kw  # noqa: E402

CFG = {
    "tibber_token": "x",
    "weather_entity": "weather.home",
    "indoor_temp_entity": "sensor.indoor",
    "outdoor_temp_entity": "sensor.outdoor",
    "heat_pump_power_entity": "sensor.pump_power",
}
STATES = {
    "sensor.indoor": FakeState("21.0", unit="°C"),
    "sensor.outdoor": FakeState("8.0", unit="°C"),
    "sensor.pump_power": FakeState("2200", unit="W"),
}
#: Synthetic draw classes, kW. Idle: controller and crankcase heater.
#: Standby: circulation pump, at or under ``on_threshold_kw`` (0.5 kW here).
#: Duty-cycled: the pump at its 1.0 kW floor for 50 % / 70 % of the interval
#: over a 0.05 kW idle. Running: the live install's band, and the floor itself.
CLASSES = {
    "idle": (0.02, 0.05, 0.1),
    "standby": (0.2, 0.3, 0.5),
    "duty_cycled": (0.525, 0.715),
    "running": (1.0, 1.2, 1.9, 2.2, 2.55),
}


def folds(p_max: float, p_min: float, kw: float, cycles: int = 3) -> int:
    """How many of ``cycles`` intervals drawing ``kw`` fold into ``cop_samples``."""
    coord = HeatPumpOptimizerCoordinator(
        FakeHass(dict(STATES)),
        FakeEntry(data=dict(CFG, heat_pump_max_power=p_max, heat_pump_min_power=p_min)),
    )
    coord._current_action = {"power": kw, "dhw_power": 0.0}
    coord._measured_power = kw
    coord._current_state.outdoor_temperature = 8.0
    for _ in range(cycles):
        coord._learn_measured_cop()
    return int(coord._cop_samples)


def main() -> None:
    probe = HeatPumpOptimizerCoordinator(
        FakeHass(dict(STATES)),
        FakeEntry(data=dict(CFG, heat_pump_max_power=14.0, heat_pump_min_power=1.0)),
    )
    params = probe._thermal_params
    print(f"RESULT duty_floor_kw={params.flow_lift_power_floor_kw:.3f}")
    print(f"RESULT on_threshold_kw={on_threshold_kw(params):.3f}")
    for p_min in (1.0, 3.0):
        tag = f"min{p_min:g}"
        for name, draws in CLASSES.items():
            got = [folds(14.0, p_min, kw) for kw in draws]
            print(f"  {tag} {name:12s} " + " ".join(f"{kw:g}kW:{n}" for kw, n in zip(draws, got)))
            print(f"RESULT {tag}_{name}_folded={sum(got)}/{3 * len(draws)}")
    print(f"RESULT liveness_folded={folds(4.0, 1.0, 2.2)}/3")
    print("  sweep: floor k x p_min (p_min 1.0) -> admitted standby+duty / running")
    below = CLASSES["standby"] + CLASSES["duty_cycled"]
    for k in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        floor = max(k * 1.0, 0.2)
        print(f"  k={k:.1f} floor={floor:.2f}  low admitted {sum(d >= floor for d in below)}"
              f"/{len(below)}  running admitted {sum(d >= floor for d in CLASSES['running'])}"
              f"/{len(CLASSES['running'])}  min-power margin {1.0 - floor:+.2f} kW")


if __name__ == "__main__":
    main()
