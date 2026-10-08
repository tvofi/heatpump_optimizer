#!/usr/bin/env python3
"""The COP learner's duty floor and ratio gates (#2066's fixer's instrument).

Written by the #2066 fixer, not by the finder: the live-install finding
committed no harness. The ``selfmod`` rows reproduce the #2066 round-1
reviewer's probe 3 (hpo-seats/review-2066/ev/reviewer_probe3.py) as a control.

Drives the real coordinator's ``_learn_measured_cop`` with synthetic intervals
on a 14 kW-nameplate install with a 1.0 kW modulation floor (and an overstated
3.0 kW one), outside the frost band. Run it from a worktree root, at the base
and at the head:

    PYTHONPATH=tests/hastub:custom_components:tests \
        python3 dev/audit/harnesses/cop_duty_floor.py

Rows, each "folded/intervals scale":
  * ``duty_floor_kw`` -- the floor both folds read.
  * ``min1_*``/``min3_*`` -- the pump draws what the plan asked (3 intervals
    per draw). ``running`` is the defect (0 at the base); ``idle``,
    ``standby`` and ``duty_cycled`` are what the floor exists to refuse. The
    3.0 kW rows are the gap this PR leaves for the observed-draw cap
    (dev/programme/carries/carry-2065.json).
  * ``selfmod_independent`` -- the reviewer's probe: the plan asks 1.0-2.0 kW,
    the pump draws 1.9-2.55 kW regardless; true COP equals the model's, so the
    right scale is 1.000. ``selfmod_matched`` is its control: draw == ask.
  * ``true_<s>`` -- a heat-led pump whose true COP scale is ``s``: the meter
    reads ask x current scale / s, with +-5 % meter noise (seeded). The right
    scale is ``s``; a gate on the ask level alone would never fold these.
  * ``true_0.7_4kw`` -- the same on a correctly sized 4 kW nameplate, which
    the base could already learn: the head must not lose it.
  * ``fixed3_duty<d>`` -- a fixed-speed pump (min == max == 3 kW) at duty
    ``d``, plan and meter both averaging: the behaviour change on such pumps.
  * ``liveness`` -- a 4 kW nameplate whose old floor (1.2 kW) already
    admitted 2.2 kW: a zero at the base is the floor, not a dead learner.
"""
from __future__ import annotations

import itertools
import random
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
ASKED = (1.0, 1.25, 1.5, 1.75, 2.0)
DRAWN = (1.9, 2.2, 2.55)


def coord(p_max: float = 14.0, p_min: float = 1.0) -> HeatPumpOptimizerCoordinator:
    c = HeatPumpOptimizerCoordinator(
        FakeHass(dict(STATES)),
        FakeEntry(data=dict(CFG, heat_pump_max_power=p_max, heat_pump_min_power=p_min)),
    )
    c._current_state.outdoor_temperature = 8.0
    return c


def run(pairs, p_max=14.0, p_min=1.0, true=None, noise=0.0) -> str:
    """Feed (asked, drawn) intervals; ``true`` replaces drawn by a heat-led pump's."""
    rnd = random.Random(1)
    c = coord(p_max, p_min)
    for asked, drawn in pairs:
        if true is not None:
            drawn = asked * c._cop_scale / true
        c._current_action = {"power": asked, "dhw_power": 0.0}
        c._measured_power = drawn * (1.0 + rnd.uniform(-noise, noise))
        c._learn_measured_cop()
    return f"{c._cop_samples}/{len(pairs)} {c._cop_scale:.3f}"


def main() -> None:
    params = coord()._thermal_params
    print(f"RESULT duty_floor_kw={params.flow_lift_power_floor_kw:.3f}")
    print(f"RESULT on_threshold_kw={on_threshold_kw(params):.3f}")
    for p_min in (1.0, 3.0):
        for name, draws in CLASSES.items():
            got = [run([(kw, kw)] * 3, p_min=p_min).split()[0] for kw in draws]
            folded = sum(int(g.split("/")[0]) for g in got)
            print(f"RESULT min{p_min:g}_{name}_folded={folded}/{3 * len(draws)}")
    cyc = lambda xs, n: list(itertools.islice(itertools.cycle(xs), n))  # noqa: E731
    independent = list(zip(cyc(ASKED, 96), cyc(DRAWN, 96)))
    matched = [(d, d) for d in cyc(DRAWN, 96)]
    print(f"RESULT selfmod_independent={run(independent).replace(' ', '_scale=')}")
    print(f"RESULT selfmod_independent_4kw={run(independent, p_max=4.0).replace(' ', '_scale=')}")
    print(f"RESULT selfmod_matched={run(matched).replace(' ', '_scale=')}")
    for true in (0.6, 0.7, 0.8, 1.3):
        print(f"RESULT true_{true:g}={run(matched * 3, true=true, noise=0.05).replace(' ', '_scale=')}")
    print(f"RESULT true_0.7_4kw={run(matched * 3, p_max=4.0, true=0.7, noise=0.05).replace(' ', '_scale=')}")
    # A fixed-speed pump (min == max == 3 kW) whose plan prices part duty as an
    # average and whose meter averages too: the floor is 2.4 kW at the head.
    for duty in (0.5, 0.7, 0.85):
        kw = 3.0 * duty + 0.05 * (1.0 - duty)
        print(f"RESULT fixed3_duty{int(duty * 100)}={run([(kw, kw)] * 5, p_max=3.0, p_min=3.0).replace(' ', '_scale=')}")
    print(f"RESULT liveness_folded={run([(2.2, 2.2)] * 3, p_max=4.0).split()[0]}")


if __name__ == "__main__":
    main()
