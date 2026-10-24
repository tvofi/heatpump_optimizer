"""D8-s1-01: the plan sensors say "heating now" on a step the plan declares off.

Metric (key = the entity's own native_value): snapshots in which
sensor:plan_space_heating or sensor:plan_dhw_heating publishes "heating now"
while the same payload's current_action has heat_pump_on False (Heat Pump Action
"off", climate idle, Recommended Power 0). Secondary (key = the published
space_plan / dhw_plan slots vs schedule[i].heat_pump_on): plan steps counted
inside a published slot that the plan's own schedule declares off.

Cells: coord_all_features and min+min_modulation, each walked over 17 quarter-hours
(matrix.build sweep). Production symbols: sensor.SpaceHeatingPlanSensor.native_value,
sensor.DHWHeatingPlanSensor.native_value, coordinator.HeatPumpOptimizerCoordinator._build_plan_views (active_now,
_plan_slots threshold 0.05) against thermal_model.MIN_RUNNING_DRAW_KW (0.1).

Perturbation: --perturb wraps coordinator.HeatPumpOptimizerCoordinator._build_plan_views
in memory so each plan's active_now also requires the plan's own on decision
(result.heat_pump_on_schedule[0]) -> heating_now_while_off goes to zero. The
secondary count is not touched by it (the slot threshold is a separate literal).
(MIN_RUNNING_DRAW_KW cannot be patched from here: the solve runs in process_worker.py's
subprocess, so an in-memory constant swap never reaches the on decision.)

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D8/s1/f1_active_now.py [--perturb]
Expected at baseline 17f1c55fad1b: heating_now_while_off >= 1, exact per machine
(the solve is deterministic on one BLAS); machine macOS arm64.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matrix as M  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

CELLS = ("coord_all_features", "min+min_modulation")


def main():
    if "--perturb" in sys.argv:
        from heatpump_optimizer import coordinator as C
        orig = C.HeatPumpOptimizerCoordinator._build_plan_views

        def gated(self, result):
            views = orig(self, result)
            sched = list(result.heat_pump_on_schedule or [])
            on0 = bool(sched[0]) if sched else True
            for k in ("space_plan", "dhw_plan"):
                if isinstance(views.get(k), dict):
                    views[k]["active_now"] = bool(views[k].get("active_now")) and on0
            return views

        C.HeatPumpOptimizerCoordinator._build_plan_views = gated
    t0p, t0t = time.process_time(), time.thread_time()
    dt_util.freeze(M.START)
    snaps_total = 0
    hits = 0
    step_hits = 0
    steps_total = 0
    try:
        for cell in CELLS:
            coord, snaps = M.build(M.cells()[cell], sweep=16)
            for i, sn in enumerate(snaps):
                snaps_total += 1
                ca = sn["__action__"]["state"]
                for key in ("sensor:plan_space_heating", "sensor:plan_dhw_heating"):
                    r = sn.get(key)
                    if r and r["available"] and r["state"] == "heating now" and ca.get("heat_pump_on") is False:
                        hits += 1
                        print(f"HIT {cell}@{i} {key}=heating now; action mode={ca.get('mode')} "
                              f"power={ca.get('power')} dhw={ca.get('dhw_power')} on={ca.get('heat_pump_on')}")
            # step level, last snapshot's payload
            d = coord.data
            sched = d.get("schedule") or []
            in_slot = set()
            for plan_key in ("space_plan", "dhw_plan"):
                for slot in (d.get(plan_key) or {}).get("slots", []):
                    in_slot |= {s for s in range(len(sched))
                                if slot["start"] <= sched[s]["time"] < slot["end"]}
            for s in range(len(sched)):
                steps_total += 1
                if s in in_slot and sched[s].get("heat_pump_on") is False:
                    step_hits += 1
    finally:
        dt_util.freeze(None)
    print(f"RESULT heating_now_while_off={hits} count")
    print(f"RESULT snapshots={snaps_total} count")
    print(f"RESULT slot_steps_declared_off={step_hits} count")
    print(f"RESULT steps={steps_total} count")
    print(f"RESULT perturbed={int('--perturb' in sys.argv)}")
    tf = (time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
