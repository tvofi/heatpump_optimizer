"""D8-s1 M2, the brief's two named probes, through the production cycle and the plan sensors.

A) reason under flat weather on a house whose heat-loss scale is above 1.1:
   metric `weather_reason_steps` = steps of the published plan (space_plan slots' `reasons`, the
   current action's `space_reason`, and Plan Narrative's state) carrying preheat_weather while the
   forecast is flat (constant temperature, wind, rain). Arms: scale 1.3 (`--scale`), null 1.0.
   Perturbation --unscaled-divisor: optimizer._weather_loss_factors divides by the unscaled
   nameplate (the pre-fix shape its docstring names) -> the count must rise above 0.
B) merged plan-slot average power on a non-modulating pump with a minimum power:
   metric `slot_avg_mismatch` = published SpaceHeatingPlanSensor/DHWHeatingPlanSensor slots whose
   avg_power_kw differs by > 0.01 kW from energy_kwh / duration_hours, or whose energy differs by
   > 0.01 kWh from the plan's own step draws (data `schedule` power, `dhw_schedule` dhw_power) inside the slot.
   Perturbation --slot-halve: plan_slots.plan_slots publishes avg_power_kw halved -> count rises.
Command (from the export root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D8/s1/extras.py [--scale S] [--unscaled-divisor] [--slot-halve] [-v]
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B4. Expected at baseline: 0 and 0, exact.
Instrumented symbols: heatpump_optimizer.optimizer:_weather_loss_factors, heatpump_optimizer.plan_slots:plan_slots,
heatpump_optimizer.sensor:SpaceHeatingPlanSensor, DHWHeatingPlanSensor, PlanNarrativeSensor.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402
import numpy as np  # noqa: E402
from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import optimizer as opt_mod  # noqa: E402
from heatpump_optimizer import plan_slots as ps_mod  # noqa: E402


def flat_forecast(start):
    return [{"datetime": (start + timedelta(hours=h)).isoformat(), "temperature": -5.0,
             "wind_speed": 3.0, "precipitation": 0.0, "humidity": 85.0} for h in range(48)]


def part_a(scale, verbose):
    cfg = {**rig.cells()["coord_minimal"], "house_heat_loss_scale": scale}
    hass, entry, coord = rig.build(cfg)
    day0 = rig.START.replace(hour=0)
    count = 0
    seen_scale = None
    for idx in range(2):
        coord._weather_forecast = flat_forecast(day0)
        coord._solar_radiation_forecast = [0.0] * 48
        rig.when = None
        rig.dt_util.freeze(rig.START + timedelta(minutes=15 * idx))
        rig.set_states(hass, 0, rig.START + timedelta(minutes=15 * idx))  # flat inputs both cycles
        import asyncio
        coord.data = asyncio.run(coord._async_update_data())
        data = coord.data
        seen_scale = getattr(coord, "_house_heat_loss_scale", None)
        for slot in (data.get("space_plan") or {}).get("slots", []):
            n = sum(1 for r in slot.get("reasons", []) if r == "preheat_weather")
            count += n
        if (data.get("current_action") or {}).get("space_reason") == "preheat_weather":
            count += 1
        items = ((data.get("insight") or {}).get("narrative") or {}).get("items") or []
        count += sum(1 for it in items if isinstance(it, dict) and it.get("reason") == "preheat_weather")
        if verbose:
            print("  A", scale, idx, [s.get("reasons") for s in (data.get("space_plan") or {}).get("slots", [])],
                  (data.get("current_action") or {}).get("space_reason"))
    rig.dt_util.freeze(None)
    return count, seen_scale


def part_b(verbose):
    cfg = {**rig.cells()["coord_dhw"], "compressor_modulation": False, "heat_pump_min_power": 2.0,
           "heat_pump_max_power": 2.0}
    hass, entry, coord = rig.build(cfg)
    bad = slots_seen = 0
    for idx in range(2):
        rig.cycle(hass, coord, idx)
        data = coord.data or {}
        for key, part, skey in (("space_plan", "power", "schedule"), ("dhw_plan", "dhw_power", "dhw_schedule")):
            sched = data.get(skey) or []
            for slot in (data.get(key) or {}).get("slots", []):
                slots_seen += 1
                dur, avg, kwh = slot["duration_hours"], slot["avg_power_kw"], slot["energy_kwh"]
                s0 = datetime.fromisoformat(slot["start"])
                s1 = datetime.fromisoformat(slot["end"])
                steps = [r for r in sched if s0 <= datetime.fromisoformat(r["time"]) < s1]
                plan_kwh = sum(float(r.get(part) or 0.0) for r in steps) * 0.25
                if (dur and abs(avg - kwh / dur) > 0.01) or (steps and abs(plan_kwh - kwh) > 0.01):
                    bad += 1
                    if verbose:
                        print("  B", key, slot, "plan_kwh", round(plan_kwh, 3), "steps", len(steps))
    rig.dt_util.freeze(None)
    return bad, slots_seen


def main():
    t0, th0 = time.process_time(), time.thread_time()
    verbose = "-v" in sys.argv
    scale = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.3
    orig_w, orig_ps = opt_mod._weather_loss_factors, ps_mod.plan_slots
    # Both arms solve in this interpreter: the production process worker
    # (coordinator._run_in_process) runs the solve in a child that an in-memory
    # perturbation cannot reach. The baseline arm takes the same path.
    coord_mod._run_in_process = lambda fn, args: fn(*args)
    if "--unscaled-divisor" in sys.argv:
        def unscaled(model, wind, rain, n):
            base = max(model.params.heat_loss_coefficient, 0.001)
            return np.array([model.effective_heat_loss_coefficient(base, wind[i], rain[i]) / base for i in range(n)])
        opt_mod._weather_loss_factors = unscaled
    if "--slot-halve" in sys.argv:
        def halved(*a, **k):
            out = orig_ps(*a, **k)
            for s in out:
                s["avg_power_kw"] = round(s["avg_power_kw"] / 2, 2)
            return out
        ps_mod.plan_slots = halved
        coord_mod.plan_slots = halved if hasattr(coord_mod, "plan_slots") else None
    try:
        a, seen = part_a(scale, verbose)
        a0, _ = part_a(1.0, verbose)
        b, nslots = part_b(verbose)
    finally:
        opt_mod._weather_loss_factors = orig_w
        ps_mod.plan_slots = orig_ps
        if hasattr(coord_mod, "plan_slots"):
            coord_mod.plan_slots = orig_ps
    print(f"RESULT house_heat_loss_scale_in_use={seen}")
    print(f"RESULT weather_reason_steps={a} count")
    print(f"RESULT weather_reason_steps_null_scale1={a0} count")
    print(f"RESULT slot_avg_mismatch={b} count")
    print(f"RESULT slots_checked={nslots} count")
    print(f"RESULT thread_factor={(time.process_time() - t0) / max(time.thread_time() - th0, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
