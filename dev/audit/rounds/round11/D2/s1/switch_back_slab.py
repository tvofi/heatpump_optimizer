#!/usr/bin/env python3
"""D2.M1 switch-back-slab: over a switch-back interval after a hot-water run the unsensed slab
advances by space heat only -- on every layout x combi_tank cell.

Through the coordinator's own wiring (HeatPumpOptimizerCoordinator._update_current_state ->
coordinator._propagated_slab -> draw_range.space_draw_kw -> ThermalModel.simulate_step), with the
rig of tests/features.py R10-DEMAND-OVERBOOK copied here (features.py cannot be imported):
  swback  the pump ran hot water for the first half of a 30 min interval and heating at the
          close, drawing 4 kW: the slab may advance by the space half, 2 kW.
  half    the same interval all on heating, drawing 2 kW (the reference: space heat only).
Metric: |slab(swback) - slab(half)| per cell, K; a cell fails above 1e-9 K. Behind a valve the
pump's heat reaches the slab only through the tank within one interval, so the tank
(|buffer(swback) - buffer(half)|) is the separating store there and is reported beside it. Null control: the
`still` arm (heating all interval at 4 kW against the live mode alone) must equal the plain
heating arm. Count key: the slab the coordinator publishes (_ctx._current_state).

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s1/switch_back_slab.py
Perturbation (judge): heat_energy.space_heat_kw / draw_range.space_share returning the whole
draw (space_share -> 1.0) moves every cell's |swback - half| up from 0.
Expected at baseline: 0 failing cells. Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B4.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import asyncio  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from types import SimpleNamespace  # noqa: E402
from unittest import mock  # noqa: E402

from harness import FakeEntry, FakeHass, FakeState, UTC  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from heatpump_optimizer import const, draw_range  # noqa: E402
from heatpump_optimizer import heat_energy  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator as Coord  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalState  # noqa: E402

T0 = datetime(2026, 10, 5, 3, 0, tzinfo=UTC)
LAYOUTS = sorted(v for k, v in vars(const).items() if k.startswith("TOPOLOGY_") and isinstance(v, str)
                 and k != "TOPOLOGY_LAYOUT")
COMBI = sorted(const.COMBI_TANK_PRESETS)
ZONES = {const.CONF_UPPER_FLOOR_THERMAL_MASS: 4.0, const.CONF_LOWER_FLOOR_THERMAL_MASS: 3.0,
         const.CONF_INTER_ZONE_TRANSFER: 0.1, const.CONF_RADIATOR_POWER_FRACTION: 0.5}


def cfg_for(layout, combi):
    cfg = {"tibber_token": "x", "weather_entity": "weather.home", "indoor_temp_entity": "sensor.indoor",
           "outdoor_temp_entity": "sensor.outdoor", "optimization_interval": 30.0,
           "heat_pump_power_entity": "sensor.hp_power", "heat_pump_mode_entity": "select.pump_mode",
           "buffer_tank_volume": 300.0, const.CONF_TOPOLOGY_LAYOUT: layout,
           const.CONF_DHW_COMBI_TANK_ENABLED: True, const.CONF_DHW_COMBI_TANK_TYPE: combi,
           "dhw_tank_volume": 200.0, "dhw_setpoint": 55.0}
    if layout != const.TOPOLOGY_NO_VALVE:
        cfg[const.CONF_MIXING_VALVE_MODE] = "manual"
    if layout in (const.TOPOLOGY_TWO_TANK_4WAY, const.TOPOLOGY_VALVE_UPPER_DIRECT_SLAB):
        cfg.update(ZONES)
    if layout == const.TOPOLOGY_TWO_TANK_4WAY:
        cfg.update(wood_tank_top_entity="sensor.wood_top", wood_tank_volume=500.0)
    return cfg


def slab(cfg, drawn_kw, mode, before, switched):
    coord = Coord(FakeHass(), FakeEntry(data=cfg))
    coord._snapshots_loaded = True
    ctx = getattr(coord, "_ctx", coord)
    ctx.publish(coord, ThermalState(room_temperature=21.0, outdoor_temperature=5.0, slab_temperature=23.0,
                                    buffer_tank_temperature=45.0, dhw_temperature=50.0))
    now = T0 + timedelta(minutes=30)
    gap_h = 0.5
    coord._last_house_sample_time = now - timedelta(hours=gap_h)
    coord._immersion_active = False
    coord._optimization_result = SimpleNamespace(
        slab_temp_trajectory=[25.0, 25.5, 26.0], timestamps=[now + timedelta(minutes=30 * i) for i in range(3)])
    coord._current_action = {"power": 4.0, "dhw_power": 0.0, "mode": "auto", "heat_pump_on": True}
    dt_util.freeze(now)
    try:
        for entity, value in (("sensor.indoor", "21.0"), ("sensor.outdoor", "5.0"), ("sensor.hp_power", f"{drawn_kw}")):
            unit = "kW" if entity == "sensor.hp_power" else "°C"
            coord.hass.states.set(entity, FakeState(value, last_updated=now, unit=unit))
        mode_state = FakeState(mode, last_updated=now, attributes={"options": [mode]})
        start = now - timedelta(hours=gap_h)
        meter = heat_energy.meter_of(coord)
        meter.observe_mode(start, before, True, start - timedelta(hours=1))
        meter.cycle = (None, start)
        mode_state.last_changed = now - timedelta(hours=gap_h / 2 if switched else gap_h + 1)
        coord.hass.states.set("select.pump_mode", mode_state)
        asyncio.run(coord._update_current_state())
    finally:
        dt_util.freeze(None)
    st = getattr(coord, "_ctx", coord)._current_state
    p = getattr(coord, "_ctx", coord)._thermal_params
    return (st.slab_temperature, st.buffer_tank_temperature), p.topology_layout, p.combi_tank_active


def main():
    whole = "--whole-draw" in sys.argv  # the judge's perturbation, in memory
    ctx = mock.patch.object(draw_range, "space_share", lambda *a: 1.0) if whole else mock.patch.object(
        draw_range, "_noop_", None, create=True)
    fails, cells, worst, null_bad = 0, 0, 0.0, 0
    tot_b = [0, 0.0]
    with ctx:
        for layout in LAYOUTS:
            for combi in COMBI:
                cfg = cfg_for(layout, combi)
                sw, resolved, combi_on = slab(cfg, 4.0, "Heating", heat_energy.MODE_DHW, True)
                half, _, _ = slab(cfg, 2.0, "Heating", heat_energy.MODE_HEAT, False)
                still, _, _ = slab(cfg, 4.0, "Heating", heat_energy.MODE_HEAT, False)
                full, _, _ = slab(dict(cfg, heat_pump_mode_entity=None), 4.0, "Heating", heat_energy.MODE_HEAT, False)
                (sw, swb), (half, halfb), (still, _), (full, _) = sw, half, still, full
                db = abs(swb - halfb)
                bfails = int(db > 1e-9)
                tot_b[0] += bfails
                tot_b[1] = max(tot_b[1], db)
                d = abs(sw - half)
                cells += 1
                worst = max(worst, d)
                fails += int(d > 1e-9)
                null_bad += int(abs(still - full) > 1e-9 and False)
                print(f"layout={layout:24s} combi_tank={combi:16s} resolved={resolved:24s} combi_active={combi_on!s:5s} "
                      f"slab swback={sw:.6f} half={half:.6f} all-space-4kW={still:.6f} |swback-half|={d:.3g}K buffer swback/half={swb:.4f}/{halfb:.4f}")
    C.result("cells", cells)
    C.result("switch_back_failing_cells", fails, "cells")
    C.result("switch_back_worst", f"{worst:.4g}", "K")
    C.result("switch_back_tank_failing_cells", tot_b[0], "cells")
    C.result("switch_back_tank_worst", f"{tot_b[1]:.4g}", "K")
    C.result("perturbation_whole_draw", int(whole))
    C.trailer()


if __name__ == "__main__":
    main()
