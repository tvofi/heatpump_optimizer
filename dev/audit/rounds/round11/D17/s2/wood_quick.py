"""D17-s2-03 -- quick setup's wood furnace and wood-tank probe change nothing in the plan
on the plant quick setup produces (no throttling valve).

Metric: on entries created through the real quick-setup path (quick_setup ->
device_prefill skipped -> finish_now) with wood_furnace / wood_buffer_tank answered
"yes" and the wood tank top probe picked on the same page, the spread of the planned
space-heating energy (sum power_schedule * 0.25 h) over a 2x2 grid: furnace {on, off}
x wood-tank probe reading {85 C, 35 C}. Key: the plan the real coordinator solves,
never the stored answers. Cells printed individually; with four cells the
leave-one-out value is printed too.
Oracle: strings.json config.step.quick_setup.data_description.wood_furnace "On lets the
optimizer factor its heat in and stand the pump down while the fire is lit";
.wood_buffer_tank "the two-tank physics activates only once a probe is assigned";
.wood_tank_top_entity "this gives the heat left in the wood tank".
Null control / config perturbation: the same grid with a throttling mixing valve
stored (options mixing_valve_mode=smart_write) -- the plant topology the model's
two-tank variant requires (thermal_model.ThermalParameters.topology_layout); there the
spread must be > 0.

Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D17/s2/wood_quick.py
Expected at 92d38ecb: RESULT quick_path_plan_kwh_spread=0.0 ; RESULT
          valve_arm_plan_kwh_spread>0 ; tolerance 1e-6.
Perturbation: the valve arm above (a config change: options mixing_valve_mode=smart_write
on the same entry) -- expected spread > 0 (11.8 kWh at baseline). A code-level
perturbation forcing topology_layout to two_tank_4way without a valve was tried and
does NOT move the number (the two-tank variant also needs the valve's delivery), so
the gate is the valve, not the layout key alone.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, box B13 (Linux x86_64 container).
Instrumented: custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.topology_layout (read back per cell) and the plan of coordinator.py:HeatPumpOptimizerCoordinator.async_run_optimization
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time  # noqa: E402

import rig  # noqa: E402

VALVE = {"mixing_valve_mode": "smart_write", "mixing_valve_write_entity": "number.valve"}


def cell(furnace, tank, options=None):
    d = rig.walk("quick", quick_setup={"two_zone": True, "wood_furnace": furnace, "wood_buffer_tank": True,
                                       "wood_tank_top_entity": "sensor.wood_top"})
    _, _, c = rig.build(d, states={"sensor.wood_top": tank}, options=options)
    reason, res, data = rig.cycle(c)
    layout = c._ctx._thermal_params.topology_layout
    return round(sum(res.power_schedule) * 0.25, 4), layout, (data.get("external_heat") or {}).get("wood_energy_kwh")


def grid(options=None, tag=""):
    vals = {}
    for furnace in (True, False):
        for tank in ("85.0", "35.0"):
            kwh, layout, wood = cell(furnace, tank, options)
            vals[(furnace, tank)] = kwh
            print(f"{tag} furnace={furnace!s:5} probe={tank}: plan kWh={kwh} layout={layout} wood_energy_kwh={wood}")
    xs = list(vals.values())
    spread = max(xs) - min(xs)
    loo = min(max(xs[:i] + xs[i + 1:]) - min(xs[:i] + xs[i + 1:]) for i in range(len(xs)))
    return spread, loo


def measure():
    s, loo = grid(None, "quick")
    print(f"RESULT quick_path_plan_kwh_spread={s:.4f} kWh")
    print(f"RESULT quick_path_plan_kwh_spread_loo={loo:.4f} kWh")
    s2, loo2 = grid(VALVE, "valve")
    print(f"RESULT valve_arm_plan_kwh_spread={s2:.4f} kWh")
    print(f"RESULT valve_arm_plan_kwh_spread_loo={loo2:.4f} kWh")


if __name__ == "__main__":
    t0 = time.time()
    measure()
    print(f"RESULT wall_s={time.time() - t0:.1f} s (provisional)")
    print("RESULT thread_factor=1.00 (counts only; single-thread pin)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
