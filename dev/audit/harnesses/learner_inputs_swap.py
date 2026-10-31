#!/usr/bin/env python3
"""R10-HOTFIX-LEARNER-INPUTS: the heat-loss learners' inputs, through the production coordinator.

(1) What decides the heat-loss basis: ``heat_loss_basis`` over a config with no
power entity, a meter, and an estimate. (2) A zone-sensor move through
``_async_load_thermal_learning``: a store the coordinator wrote with
indoor=``sensor.t6``, lower=``sensor.floor_old`` and the owner's learned
scale 1.2356 / ratio 1.943 (400 samples each), reloaded under each arm, plus
both ends of the input range (zero evidence; both learners on the 3.0 clamp).
UA is ``(upper + lower * ratio) * scale`` on the stock two-zone house
(``tests/profiles.house``), kW/K.

    python3 -I dev/audit/harnesses/learner_inputs_swap.py [TREE]

TREE defaults to this checkout; pass a ``git archive`` export of another
commit (custom_components and tests) to measure it.
"""
import asyncio
import os
import sys

T = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path[:0] = [f"{T}/tests/hastub", f"{T}/custom_components", f"{T}/tests"]
from harness import FakeEntry, FakeHass  # noqa: E402
from profiles import house  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord  # noqa: E402
from heatpump_optimizer.thermal_model import heat_loss_basis  # noqa: E402


class Store:
    def __init__(self):
        self.saved = None

    async def async_save(self, data):
        self.saved = data

    async def async_load(self):
        return self.saved

    async def async_wait_for_read(self):
        return None


BASE = dict(house(two_zone=True, dhw=False), indoor_temp_entity="sensor.t6",
            lower_floor_temp_entity="sensor.floor_old")
MOVE = dict(BASE, indoor_temp_entity="sensor.bthome", lower_floor_temp_entity="sensor.t6")


def coord(cfg, store):
    c = Coord(FakeHass({}), FakeEntry(data=cfg))
    c._thermal_learning_store = store
    return c


def learned(scale=1.2356, ratio=1.943, n=400):
    c = coord(BASE, Store())
    c._apply_house_heat_loss_scale(scale)
    c._apply_lower_floor_loss_ratio(ratio)
    c._house_heat_loss_samples, c._lower_floor_loss_samples = n, n
    asyncio.run(c._async_save_thermal_learning())
    return c._thermal_learning_store


def reload(cfg, **kw):
    c = coord(cfg, learned(**kw))
    asyncio.run(c._async_load_thermal_learning())
    p = c._thermal_params
    ua = (p.upper_floor_heat_loss + p.lower_floor_heat_loss * c._lower_floor_loss_ratio) * c._house_heat_loss_scale
    return (round(c._house_heat_loss_scale, 4), round(c._lower_floor_loss_ratio, 4),
            c._house_heat_loss_samples, c._lower_floor_loss_samples, round(ua, 4))


if __name__ == "__main__":
    for name, cfg in (
        ("no power entity (null)", {}),
        ("power = a revenue meter", {"heat_pump_power_entity": "sensor.shelly_em_power"}),
        ("power = the pump's own estimate", {"heat_pump_power_entity": "sensor.pump_estimated_power"}),
    ):
        print(f"basis  {name:<38} {heat_loss_basis(cfg)}")
    for name, cfg, kw in (
        ("unchanged sensors", BASE, {}),
        ("move: indoor=bthome, lower=t6", MOVE, {}),
        ("lower only: lower=t6", dict(BASE, lower_floor_temp_entity="sensor.t6"), {}),
        ("null: outdoor + comfort_weight edit", dict(BASE, outdoor_temp_entity="sensor.out2", comfort_weight=3.0), {}),
        ("zero evidence (1.0, 1.0, n=0), move", MOVE, {"scale": 1.0, "ratio": 1.0, "n": 0}),
        ("on the clamp (3.0, 3.0, n=400), move", MOVE, {"scale": 3.0, "ratio": 3.0}),
    ):
        print(f"swap   {name:<38} (scale, ratio, n_scale, n_ratio, UA kW/K) = {reload(cfg, **kw)}")
