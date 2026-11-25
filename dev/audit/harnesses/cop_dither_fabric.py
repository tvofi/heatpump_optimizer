#!/usr/bin/env python3
"""The fabric replays under the COP-scale dither (carry 7 of R11-OUTSIDE-SELF-SETTING-PUMP).

#3662 item 26742487: on an admitted install the fabric replays
(``thermal_model.simulate_step`` through ``_async_learn_house_heat_loss`` and
``_async_learn_lower_floor_loss``) price pump heat at the COP scale in force
over the interval they replay, which while the heat-ask probe runs is a dither
level. This is the full-cycle instrument that item lacked: a real plant
(``ThermalModel`` with its own heat loss and the pump's true COP scale) advanced
by what a heat-led pump draws, and the real coordinator driven once per
interval through ``_async_learn_interval`` -- both fabric learners on the
closed interval, then the COP learner and its probe, in the cycle's order.

The plan's ask is pinned (flat 1.5 kW electrical), the case in which the
probe runs (``cop_duty_floor.py``'s ``flat`` rows); a heat-led pump of true
scale ``t`` delivers the heat that ask prices, ``asked x scale``, so it draws
``asked x scale / t`` and the plant is advanced by that draw at its true COP.
Outdoor follows a 6 K daily swing around 2 °C (inside the frost band, where
most COP intervals are refused ``frost_band``: read cycles that admit no row,
so the probe holds its slot) or 9 °C (outside it), so the house learner has
load to fit; the plant leaks ``PLANT_ERROR`` times the configured loss.

Each row is one run of ``CYCLES`` intervals and prints the stored fabric
values (``house_heat_loss_scale``, ``lower_floor_loss_ratio`` and their
sample counts), the COP scale and
the probe's verdict, and the furthest the house scale's trajectory sat from
its null twin's. ``null`` is null control 1 of the round-3 design note
(``ScaleDither.levels`` returning the base twice): the same run with no
dither, so the difference between the two rows is the dither's effect on the
fabric fit and nothing else. ``no_probe`` is the second control: the scale
held at 1.0 with the probe never admitted (a measured-heat-free install whose
window evidence never turns unobtainable is not reachable here, so the probe
is removed by making ``MeasuredCop._admits`` false).

Not reached: the lower-floor learner. It needs a lower-floor sensor and a
two-zone house; ``run(two_zone=True)`` on ``profiles.house(two_zone=True)``
learns no lower-floor sample and pins the house scale at its 0.3 clamp at
every arm, so that row measures the driver, not the dither, and is not printed.

    PYTHONPATH=tests/hastub:custom_components:tests \\
        python3 dev/audit/harnesses/cop_dither_fabric.py
"""
from __future__ import annotations

import asyncio
import math
import sys
from datetime import datetime, timedelta

import numpy as np

sys.path.insert(0, "tests")
from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from profiles import house  # noqa: E402

from heatpump_optimizer import accuracy, draw_range  # noqa: E402
from heatpump_optimizer.const import CONF_INDOOR_TEMP_ENTITY  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)
DT_H = 0.5
CYCLES = 672
PLANT_ERROR = 1.1
ASKED_KW = 1.5


def run(true: float, cycles: int = CYCLES, outdoor_c: float = 2.0, two_zone: bool = False) -> tuple[dict, list[float]]:
    cfg = dict(house(two_zone=two_zone, dhw=False), heat_pump_power_entity="sensor.pump_power")
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={**cfg, CONF_INDOOR_TEMP_ENTITY: "sensor.indoor"}))
    plant_params = ThermalParameters.from_config(cfg)
    plant_params.dhw_enabled = False
    plant_params.heat_loss_coefficient *= PLANT_ERROR
    plant_params.upper_floor_heat_loss *= PLANT_ERROR
    plant_params.lower_floor_heat_loss *= PLANT_ERROR
    plant_params.cop_scale = true
    plant = ThermalModel(plant_params)
    t = cfg["target_temperature"]
    state = ThermalState(room_temperature=t, slab_temperature=t + 1.0, outdoor_temperature=outdoor_c,
                         upper_floor_temperature=t, lower_floor_temperature=t, dhw_temperature=45.0,
                         dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
    coord._current_state = state
    trace = []
    try:
        for step in range(cycles):
            now = START + timedelta(hours=step * DT_H)
            outdoor = outdoor_c + 3.0 * math.sin(2 * math.pi * (step * DT_H) / 24.0)
            drawn = ASKED_KW * coord._cop_scale / true
            room, slab, upper, lower, _, _, _ = plant.simulate_trajectory(
                initial_state=state, power_schedule=np.array([drawn]),
                weather=WeatherSeries(outdoor_temps=np.array([outdoor]), wind_speeds=np.array([0.0]),
                                      precipitation=np.array([0.0]), solar_radiation=np.array([0.0])),
                dt_hours=DT_H)
            prior = state
            state = ThermalState(room_temperature=float(room[-1]), slab_temperature=float(slab[-1]),
                                 outdoor_temperature=outdoor, upper_floor_temperature=float(upper[-1]),
                                 lower_floor_temperature=float(lower[-1]), dhw_temperature=45.0,
                                 dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
            dt_util.freeze(now + timedelta(hours=DT_H))
            coord._current_state = state
            coord._current_action = {"power": ASKED_KW, "dhw_power": 0.0}
            coord._measured_power = drawn
            coord._weather_forecast = [{"wind_speed": 0.0, "precipitation": 0.0}]
            draw_range.fold(coord._accuracy.draw, drawn, coord._commanded_split(), coord._thermal_params,
                            frozen=False, distorted=False, defrost=False)
            asyncio.run(coord._async_learn_interval(prior, slab_unsensed=False))
            trace.append(coord._house_heat_loss_scale)
    finally:
        dt_util.freeze(None)
    return {
        "house_scale": coord._house_heat_loss_scale,
        "house_samples": coord._house_heat_loss_samples,
        "lower_ratio": coord._lower_floor_loss_ratio,
        "lower_samples": coord._lower_floor_loss_samples,
        "cop_scale": coord._cop_scale,
        "verdict": coord._measured_cop.scale_response,
    }, trace


def row(name: str, out: dict, gap: float | None = None) -> None:
    extra = "" if gap is None else f" max_gap_vs_null={gap:.4f}"
    print(f"RESULT {name}=house_scale={out['house_scale']:.4f} house_samples={out['house_samples']} "
          f"lower_ratio={out['lower_ratio']:.4f} lower_samples={out['lower_samples']} cop_scale={out['cop_scale']:.3f} verdict={out['verdict']}{extra}")


def main() -> None:
    sd = accuracy.ScaleDither
    for outdoor, two_zone in ((2.0, False), (9.0, False)):
        for true in (1.0, 0.8):
            tag = f"true{true:g}_{outdoor:g}C" + ("_two_zone" if two_zone else "")
            kw = {"outdoor_c": outdoor, "two_zone": two_zone}
            live, live_trace = run(true, **kw)
            levels, sd.levels = sd.levels, staticmethod(lambda base: (base, base))
            try:
                null, null_trace = run(true, **kw)
            finally:
                sd.levels = staticmethod(levels)
            admits, accuracy.MeasuredCop._admits = accuracy.MeasuredCop._admits, staticmethod(lambda *a: False)
            try:
                off, _ = run(true, **kw)
            finally:
                accuracy.MeasuredCop._admits = staticmethod(admits)
            gap = max(abs(a - b) for a, b in zip(live_trace, null_trace))
            row(f"dither_{tag}", live, gap)
            row(f"null_dither0_{tag}", null)
            row(f"no_probe_{tag}", off)


if __name__ == "__main__":
    main()
