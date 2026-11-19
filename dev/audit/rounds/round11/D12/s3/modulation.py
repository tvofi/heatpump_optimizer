"""D12.M3 -- a declared on/off compressor (compressor_modulation=on_off) is planned as a modulating one.

Metric (one line): per grid cell, the number of 15-min plan steps whose total
electrical level (space + DHW) lies strictly in (0, p_min) in the plan one real
coordinator cycle publishes for a plant that DECLARED compressor_modulation=on_off;
RESULT on_off_sub_min_total sums them over the grid, and RESULT on_off_cells_failing
counts cells with any. A declared on/off compressor cannot run such a step.

Count key: the plan the production cycle publishes
(``HeatPumpOptimizerCoordinator._optimization_result.power_schedule`` +
``dhw_power_schedule``), and ``_ctx._opt_config.clamp_planned_levels`` it solved
under -- never the harness's config dict.

Hooks / drives: heatpump_optimizer.thermal_model:declared_modulation (through
optimizer:OptimizationConfig.from_mapping -> levels_clamped -> duty_cycle_realizable),
the whole cycle heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_update_data.

Plant: switch + flow set-point + power meter + frequency SENSOR (fully metered, so the
install probe alone would not clamp), cycling cost 0 (the coordinator default), p_min 1.2 kW,
p_max 3.5 kW, DHW 180 L. Grid: 5 price shapes x 2 weather shapes from tests/profiles.py.

Arms printed per cell: on_off (the defect), modulating and absent (null controls: sub-min
steps are legitimate there), switch_setpoint_on_off (an unmetered switch+setpoint plant that
the probe clamps under auto/absent: declaring on_off there REMOVES the clamp).

Run (from the export root):
  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s3/modulation.py
  ... modulation.py --perturb doc-modulation   # declared_modulation as its docstring states (on_off -> False):
                                                # on_off_sub_min_total and on_off_cells_failing -> 0 (down / to_zero)
  ... modulation.py --flat                      # null control: flat prices only (the arms' difference must stay)
Expected at baseline 92d38ecb (export as handed over, box B6): on_off_clamped_cells=0 of 10 (exact;
-> 10 under --perturb doc-modulation); switch_setpoint_on_off_clamped_cells=0 against
switch_setpoint_absent_clamped_cells=10 (exact: the declaration removes the probe's clamp);
on_off_sub_min_total=132 (+-10, solver warm-start noise; modulating arm 129) and on_off_cells_failing=8 of 10
(the two summer_typical/winter_cold-like cells plan no sub-minimum step at all); both -> 0 under the perturbation.
--flat: on_off_sub_min_total=35, switch_setpoint_on_off 35 vs switch_setpoint_absent 0.
Machine: box B6, Linux x86_64, python 3.14, numpy 2.5.4 / scipy 1.18.1.
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import asyncio
import time
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import surfaces as S  # noqa: E402  (same directory: the plant builders and the documented map)
from profiles import prices as profile_prices, weather as profile_weather  # noqa: E402
from harness import FakeState  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import const as c  # noqa: E402
from heatpump_optimizer import thermal_model  # noqa: E402

PRICES = ("winter_typical", "winter_extreme", "shoulder", "winter_moderate", "summer_typical")
WEATHERS = ("winter_cold", "winter_mild")

UNMETERED = {c.CONF_HEAT_PUMP_SWITCH_ENTITY: "switch.hp", c.CONF_SPACE_SETPOINT_ENTITY: "number.flow_sp",
             c.CONF_SPACE_SETPOINT_UNIT: "flow"}
ARMS = {
    "on_off": ({**S.METERED_FREQ, c.CONF_COMPRESSOR_MODULATION: "on_off"}, S.METERED_STATES),
    "modulating": ({**S.METERED_FREQ, c.CONF_COMPRESSOR_MODULATION: "modulating"}, S.METERED_STATES),
    "absent": (dict(S.METERED_FREQ), S.METERED_STATES),
    "switch_setpoint_absent": (dict(UNMETERED), S.METERED_STATES),
    "switch_setpoint_on_off": ({**UNMETERED, c.CONF_COMPRESSOR_MODULATION: "on_off"}, S.METERED_STATES),
}


def cycle(arm, price, wx, idx):
    extra, states = ARMS[arm]
    cfg = {**S.GEN_BASE, **extra}
    st = {**S.GEN_STATES, **{k: FakeState(v.state, attributes=dict(v.attributes)) for k, v in states.items()}}
    hass, coord = S.build(cfg, st, entry_id=f"d12s3_mod_{arm}_{idx}")
    now = dt_util.now().replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(hours=1)
    p = profile_prices(price, start.replace(tzinfo=None))
    t, wind, rain, _sol = profile_weather(wx, start.replace(tzinfo=None))

    async def fetch_prices():
        coord._prices = [{"total": float(p[i * 4]), "starts_at": (start + timedelta(hours=i)).isoformat(),
                          "level": "NORMAL"} for i in range(24)] + [
            {"total": float(p[i * 4]), "starts_at": (start + timedelta(hours=24 + i)).isoformat(),
             "level": "NORMAL"} for i in range(24)]

    async def fetch_weather():
        coord._weather_forecast = [{"datetime": (start + timedelta(hours=i)).isoformat(),
                                    "temperature": float(t[(i * 4) % len(t)]), "wind_speed": float(wind[(i * 4) % len(t)]),
                                    "precipitation": float(rain[(i * 4) % len(t)]), "humidity": 85.0}
                                   for i in range(48)]

    coord._fetch_tibber_prices = fetch_prices
    coord._fetch_weather_forecast = fetch_weather
    hass.states.set("sensor.outdoor", S.T(float(t[4])))
    asyncio.run(coord._async_update_data())
    res = coord._optimization_result
    return S._planned_sub_min(res), bool(coord._ctx._opt_config.clamp_planned_levels)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", choices=["doc-modulation"])
    ap.add_argument("--flat", action="store_true")
    a = ap.parse_args()
    grid = [("flat", w) for w in WEATHERS] if a.flat else [(p, w) for p in PRICES for w in WEATHERS]
    patches = []
    if a.perturb == "doc-modulation":
        patches.append(mock.patch.object(thermal_model, "declared_modulation", S.documented_declared_modulation))
    t0, c0, th0 = time.time(), time.process_time(), time.thread_time()
    for p in patches:
        p.start()
    try:
        rows = {}
        for i, (price, wx) in enumerate(grid):
            for arm in ARMS:
                rows[(price, wx, arm)] = cycle(arm, price, wx, i)
            print("CELL", price, wx, " ".join(f"{arm}={rows[(price, wx, arm)][0]}(clamp={int(rows[(price, wx, arm)][1])})" for arm in ARMS), flush=True)
    finally:
        for p in patches:
            p.stop()
    per = {arm: [rows[(p, w, arm)][0] for p, w in grid] for arm in ARMS}
    on = per["on_off"]
    print(f"RESULT grid_cells={len(grid)} count")
    for arm in ARMS:
        print(f"RESULT {arm}_sub_min_total={sum(per[arm])} count")
        print(f"RESULT {arm}_clamped_cells={sum(rows[(p, w, arm)][1] for p, w in grid)} count")
    print(f"RESULT on_off_cells_failing={sum(1 for v in on if v > 0)} count")
    print(f"RESULT switch_setpoint_on_off_cells_failing={sum(1 for v in per['switch_setpoint_on_off'] if v > 0)} count")
    if len(on) >= 5:
        print(f"RESULT loo_min={min(on)} count")
        print(f"RESULT loo_max={max(on)} count")
        # most favourable to the claim = the cell with the most sub-min steps; drop it
        print(f"RESULT loo_drop_most_favourable_total={sum(on) - max(on)} count")
    pc, tc = time.process_time() - c0, time.thread_time() - th0
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    sw = 0
    try:
        for line in open("/proc/vmstat"):
            if line.startswith("pswpin"):
                sw = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
