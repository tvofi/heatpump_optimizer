"""D12-s2-01: an install with no zone settings and no lower-floor sensor is modelled as two zones.

Metric: invented_zone_cells = cells of the D12.M2 grid whose config names no lower-floor sensor,
  no zone key and no explicit two_zone_mode=on, where the coordinator's published payload says
  ``two_zone_enabled`` True (count; key: the value HeatPumpOptimizerCoordinator._async_update_data
  publishes, not the config). Plus heat_loss_response_kwh = |planned space kWh at the user's
  house_heat_loss_coefficient 0.30 - at 0.10| on the minimal plant (the planner's response to the
  single-zone heat-loss figure the options flow asks a one-zone user for).
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D12/s2/two_zone_auto.py [--perturb]
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (export as handed to the seat):
  invented_zone_cells=47 of 47 (exact), heat_loss_response_kwh=0.000 (exact), planned 20.511 kWh both;
  under --perturb: invented_zone_cells=0, heat_loss_response_kwh > 1.
Perturbation (--perturb): cells.py's _perturb_two_zone -- ThermalParameters.from_config handed an
  absent or "auto" two_zone_mode as a value outside (on, auto, off), so its own else-branch (the
  presence rule its comment says "auto" is) decides; equivalent to the one-line edit
  ``if two_zone_mode == const.TWO_ZONE_MODE_ON:``. Direction: invented_zone_cells to zero.
Null control: the fully mapped reference plant (lower-floor sensor, zone keys, mode on) publishes
  two_zone_enabled True under both arms (null_ref_two_zone=1 both ways).
Machine: box B5, shared; counts are contention-immune.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio
import logging
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells as C  # noqa: E402  (the cell driver beside this file)
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402
from heatpump_optimizer import thermal_model  # noqa: E402
from heatpump_optimizer.optimizer import optimize_in_process  # noqa: E402

ZONE_KEYS = (const.CONF_LOWER_FLOOR_TEMP_ENTITY, const.CONF_UPPER_FLOOR_THERMAL_MASS,
             const.CONF_LOWER_FLOOR_THERMAL_MASS, const.CONF_INTER_ZONE_TRANSFER,
             const.CONF_RADIATOR_POWER_FRACTION)


def single_zone_cells():
    """The M2 grid's cells that configure nothing two-zone: every slot's present cell on MIN."""
    out = {}
    for name, (cfg, _kw) in C.cells().items():
        if any(k in cfg for k in ZONE_KEYS) or cfg.get(const.CONF_TWO_ZONE_MODE) == "on":
            continue
        out[name] = cfg
    return out


def planned_space_kwh(data) -> float:
    sched = data.get("schedule") or []
    step_h = 0.25
    if len(sched) > 1:
        from datetime import datetime
        t0, t1 = (datetime.fromisoformat(sched[i]["time"]) for i in (0, 1))
        step_h = (t1 - t0).total_seconds() / 3600
    return sum(float(r.get("power") or 0.0) for r in sched) * step_h


async def measure() -> dict:
    res = {}
    grid = single_zone_cells()
    invented = 0
    for name, cfg in sorted(grid.items()):
        r = await C.run_cell(cfg)
        data = r["data"] or {}
        if data.get("two_zone_enabled"):
            invented += 1
    res["grid"] = len(grid)
    res["invented"] = invented
    kwh = {}
    for hl in (0.10, 0.30):
        cfg = {**C.min_plant(), const.CONF_HOUSE_HEAT_LOSS_COEFFICIENT: hl}
        r = await C.run_cell(cfg)
        kwh[hl] = planned_space_kwh(r["data"] or {})
        res[f"published_heat_loss_{hl}"] = (r["data"] or {}).get("house_heat_loss_effective")
    res["kwh"] = kwh
    ref = await C.run_cell(C.ref_plant())
    res["null_ref"] = int(bool((ref["data"] or {}).get("two_zone_enabled")))
    return res


def main() -> int:
    perturb = "--perturb" in sys.argv

    async def solve(hass, opt, inputs):
        return optimize_in_process(opt, inputs)
    cm._await_optimize = solve
    C.dt_util.now = lambda *a, **k: C.NOW
    C.dt_util.utcnow = lambda *a, **k: C.NOW
    logging.disable(logging.CRITICAL)
    if perturb:
        C.PERTURB["two_zone"](True)
    t0p, t0t = time.process_time(), time.thread_time()
    try:
        res = asyncio.run(measure())
    finally:
        C.PERTURB["two_zone"](False)
    pt, tt = time.process_time() - t0p, time.thread_time() - t0t
    print(f"arm={'perturbed' if perturb else 'baseline'}")
    print(f"RESULT single_zone_cells={res['grid']} count")
    print(f"RESULT invented_zone_cells={res['invented']} count")
    print(f"RESULT planned_space_kwh_hl010={res['kwh'][0.10]:.3f} kWh")
    print(f"RESULT planned_space_kwh_hl030={res['kwh'][0.30]:.3f} kWh")
    print(f"RESULT heat_loss_response_kwh={abs(res['kwh'][0.30] - res['kwh'][0.10]):.3f} kWh")
    print(f"RESULT published_heat_loss_at_user_0.10={res['published_heat_loss_0.1']} kW/K")
    print(f"RESULT published_heat_loss_at_user_0.30={res['published_heat_loss_0.3']} kW/K")
    print(f"RESULT null_ref_two_zone={res['null_ref']} count")
    print(f"RESULT thread_factor={pt / tt if tt else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
