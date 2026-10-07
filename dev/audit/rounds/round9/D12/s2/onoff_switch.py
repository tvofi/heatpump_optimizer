"""D12-s2 (round 9, D12.M3): an on/off heat pump on the switch path is switched
OFF in steps whose planned heat the plan counts as delivered.

Metric (one line): withheld_frac = sum over plan steps whose production
``OptimizationResult.heat_pump_on_schedule`` is False of the planned space+DHW
electrical energy, divided by the plan's total planned energy (kWh/kWh), per
cell; a cell FAILS when withheld_frac > 0.10.

Count key: the value the production seam delivers -- ``heat_pump_on_schedule``
from ``HeatPumpOptimizer._power_to_heat_pump_schedule`` and the plan's own
``power_schedule``/``dhw_power_schedule`` -- never a config attribute. The
end-to-end arm keys on the ``switch.turn_off`` calls ``_apply_action``
actually issues (``HeatPumpOptimizerCoordinator._apply_action`` via
``HeatPumpOptimizer.get_current_action``).

Arms:
  modulating  profiles.house() as shipped: min 1.0 kW, max 6.0 kW (null control)
  onoff       min == max == 6.0 kW: a fixed-speed pump, whose "lowest input it
              can run at without cycling on and off" (strings.json) IS its rating;
              config_flow._power_errors accepts min == max.
Grid: 9 golden SCENARIOS cells (single/two-zone, DHW/no DHW, four price
profiles, four weather profiles). Leave-one-out printed.

Consequence arm: the shoulder cell's plan re-simulated through
``ThermalModel.simulate_step`` twice, once with the planned space power and
once with space power zeroed where the switch is commanded off; reports the
min room temperature of each and the degree-hours below min_temperature.

Perturbation (--perturb): ``HeatPumpOptimizer._power_to_heat_pump_schedule``
patched in memory to a 0.1 kW on-threshold (the function's own floor) instead
of min_electrical_power*0.5. Expected: onoff failing_cells 4 -> 0, and the
end-to-end turn_off-with-planned-heat count 30 -> 0 (direction: DOWN).
Second perturbation (--min 1.0) sets the onoff arm's min back to 1.0: the
count collapses to the modulating arm's (DOWN).

Run:   PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D12/s2/onoff_switch.py
       ... --perturb
Expected (baseline): RESULT onoff_failing_cells=4 cells (+-1; loo 3), modulating_failing_cells=0,
       e2e_turn_off_with_planned_heat=30 steps (+-3), shoulder onoff withheld_frac ~0.67 (+-0.05)
Baseline SHA: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1
Machine: box B7 cloud container, Linux 6.18, 4 vCPU, numpy/OpenBLAS; counts are
contention-immune (no timing RESULT here besides the required tail).
Root rule: run from the repository root; tests/ and custom_components/ are
inserted relatively (golden.py's own rule), so it measures the cwd tree.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import asyncio
import sys
import time
from datetime import timedelta
from unittest import mock

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

import golden
from golden import START, make
from heatpump_optimizer.optimizer import HeatPumpOptimizer

CELLS = (
    "winter_single_dhw",
    "winter_single_no_dhw",
    "winter_two_zone_dhw",
    "winter_two_zone_no_dhw",
    "shoulder",
    "shoulder_two_zone",
    "summer_dhw_only",
    "flat_prices",
    "mild_windy_rain",
)
FAIL_FRAC = 0.10
DT = 0.25


def _perturbed_schedule(self, space_power_schedule, dhw_power_schedule=None):
    space = np.asarray(space_power_schedule, dtype=float)
    dhw = (
        np.zeros_like(space)
        if dhw_power_schedule is None
        else np.asarray(dhw_power_schedule, dtype=float)
    )
    return (np.maximum(space, dhw) >= 0.1).tolist()


def solve(name, p_min):
    spec = dict(golden.SCENARIOS[name])
    po = dict(spec.pop("param_overrides", None) or {})
    po["min_electrical_power"] = p_min
    built = make(param_overrides=po, **spec)
    opt = built["optimizer"]
    res = opt.optimize(
        built["state"], built["prices"], built["outdoor"], built["wind"],
        built["rain"], built["solar"], START,
    )
    return built, opt, res


def withheld(res):
    sp = np.asarray(res.power_schedule, dtype=float)
    dh = np.asarray(res.dhw_power_schedule or np.zeros_like(sp), dtype=float)
    dh = dh[: len(sp)] if len(dh) >= len(sp) else np.pad(dh, (0, len(sp) - len(dh)))
    on = np.asarray(res.heat_pump_on_schedule, dtype=bool)
    tot = float((sp + dh).sum() * DT)
    off_kwh = float(((sp + dh) * (~on)).sum() * DT)
    off_steps_with_heat = int(((~on) & ((sp + dh) > 0.1)).sum())
    return tot, off_kwh, (off_kwh / tot if tot > 1e-9 else 0.0), off_steps_with_heat


def consequence(built, opt, res):
    """Re-simulate the plan with and without the switched-off space power."""
    model = opt.model
    on = np.asarray(res.heat_pump_on_schedule, dtype=bool)
    sp = np.asarray(res.power_schedule, dtype=float)
    floor = float(opt.config.min_temp)
    out = {}
    for arm, power in (("planned", sp), ("actuated", sp * on)):
        state = built["state"]
        rooms = []
        for i in range(len(power)):
            state = model.simulate_step(
                state, float(power[i]), float(built["outdoor"][i]),
                float(built["wind"][i]), float(built["rain"][i]),
                float(built["solar"][i]), DT,
            )
            rooms.append(float(state.room_temperature))
        rooms = np.asarray(rooms)
        out[arm] = (float(rooms.min()), float(np.clip(floor - rooms, 0, None).sum() * DT), rooms)
    shortfall = float(np.clip(out["planned"][2] - out["actuated"][2], 0, None).sum() * DT)
    return out, shortfall


def end_to_end(res, p_min, p_max):
    """Drive each plan step through get_current_action -> _apply_action."""
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    cfg = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "heat_pump_switch_entity": "switch.heat_pump",
        "heat_pump_max_power": p_max,
        "heat_pump_min_power": p_min,
    }
    coord = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))

    async def _no_publish(**_kw):
        return None

    coord.async_publish_current_action = _no_publish
    coord._mode = "auto"
    sp = np.asarray(res.power_schedule, dtype=float)
    dh = np.asarray(res.dhw_power_schedule or np.zeros_like(sp), dtype=float)
    bad = 0
    offs = 0
    for i, ts in enumerate(res.timestamps):
        coord._current_action = coord._optimizer.get_current_action(
            res, ts + timedelta(minutes=1)
        )
        before = len(coord.hass.services.calls)
        asyncio.run(coord._apply_action())
        new = coord.hass.services.calls[before:]
        off = any(c[1] == "turn_off" and c[2].get("entity_id") == "switch.heat_pump" for c in new)
        offs += off
        if off and (sp[i] + (dh[i] if i < len(dh) else 0.0)) > 0.1:
            bad += 1
    return bad, offs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--min", type=float, default=6.0, help="onoff arm's min kW")
    args = ap.parse_args()
    p_max = 6.0
    t0p, t0t = time.process_time(), time.thread_time()
    patcher = (
        mock.patch.object(HeatPumpOptimizer, "_power_to_heat_pump_schedule", _perturbed_schedule)
        if args.perturb
        else None
    )
    if patcher:
        patcher.start()
    try:
        summary = {}
        keep = {}
        for arm, p_min in (("modulating", 1.0), ("onoff", args.min)):
            fracs = {}
            for name in CELLS:
                built, opt, res = solve(name, p_min)
                tot, off_kwh, frac, n_off = withheld(res)
                fracs[name] = frac
                print(f"CELL arm={arm} cell={name} planned_kwh={tot:.2f} "
                      f"withheld_kwh={off_kwh:.2f} withheld_frac={frac:.3f} "
                      f"off_steps_with_heat={n_off}")
                if name == "shoulder":
                    keep[arm] = (built, opt, res, p_min)
            fails = sum(1 for f in fracs.values() if f > FAIL_FRAC)
            vals = sorted(fracs.values())
            summary[arm] = fracs
            print(f"RESULT {arm}_failing_cells={fails} cells")
            print(f"RESULT {arm}_cells={len(fracs)} cells")
            print(f"RESULT {arm}_withheld_frac_mean={np.mean(vals):.3f} ratio")
            print(f"RESULT {arm}_withheld_frac_range={vals[0]:.3f}..{vals[-1]:.3f} ratio")
            # leave-one-out: drop the single most-failing (largest) cell
            loo = vals[:-1]
            print(f"RESULT {arm}_withheld_frac_mean_loo={np.mean(loo):.3f} ratio")
            print(f"RESULT {arm}_failing_cells_loo={sum(1 for f in loo if f > FAIL_FRAC)} cells")
        for arm in ("modulating", "onoff"):
            built, opt, res, p_min = keep[arm]
            c, shortfall = consequence(built, opt, res)
            print(f"RESULT {arm}_shoulder_min_room_planned={c['planned'][0]:.2f} degC")
            print(f"RESULT {arm}_shoulder_min_room_actuated={c['actuated'][0]:.2f} degC")
            print(f"RESULT {arm}_shoulder_Kh_below_min_actuated={c['actuated'][1]:.2f} Kh")
            print(f"RESULT {arm}_shoulder_Kh_below_plan_actuated={shortfall:.2f} Kh")
            bad, offs = end_to_end(res, p_min, p_max)
            print(f"RESULT {arm}_e2e_turn_off_with_planned_heat={bad} steps")
            print(f"RESULT {arm}_e2e_turn_off_calls={offs} calls")
    finally:
        if patcher:
            patcher.stop()
    proc, thr = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    swap = 0
    try:
        with open("/proc/vmstat") as fh:
            for line in fh:
                if line.startswith("pswpin "):
                    swap = int(line.split()[1])
    except OSError:
        pass
    print(f"RESULT swapins={swap}")


if __name__ == "__main__":
    main()
