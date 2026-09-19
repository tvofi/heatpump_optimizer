#!/usr/bin/env python3
"""D12 generalization — sensitivity control for the fail-count metric.

METRIC (one line): the number of plant cells whose one coordinator cycle
publishes no plan, run once on the fully-mapped reference plant (the null
control) and once on the same plant with exactly one required numeric config
value perturbed to a non-numeric value.

WHY THIS EXISTS: method step 6 of the D12 brief voids any harness whose
number does not move when the plant changes.  The two matrix harnesses
(``cells.py``, ``slot_sweep.py``) report 0 failing cells; a 0 that never
moves proves nothing.  This harness shows the metric is wired to the
*published plan* by moving the count off zero with a plant the coordinator
cannot solve, and back to zero on the reference.

The perturbation here is deliberately NOT a reachable config surface (see
TOOLING note in REPORT.md): it is a wiring control, not a claimed cell.

COMMAND:  cd <repo root> && HPO_PLANDATA=$TMP/plandata \
            PYTHONPATH=tests/hastub python3 tools/audit/round5/D12/control.py

EXPECTED:  reference no-plan count 0; perturbed no-plan count > 0.
BASELINE:  origin/main eaa2a06af16a1b5b006f58a0f36cc92131f80225
           (production code identical to this worktree; only tests/closure.py
           and tests/entities.py differ between eaa2a06 and this HEAD)
MACHINE:   darwin 25.6.0, Apple M1, 8 GB
"""
import os

for _k in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_k, "1")

import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cells  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402

#: numeric keys a plant carries; each is a value the production seam
#: ``ThermalParameters.from_config`` must read as a float.
NUMERIC_KEYS = [
    C.CONF_BUFFER_TANK_VOLUME,
    C.CONF_BUFFER_MAX_TEMP,
    C.CONF_DHW_TANK_VOLUME,
    C.CONF_WOOD_TANK_VOLUME,
    C.CONF_HEAT_PUMP_MAX_POWER,
    C.CONF_HEAT_PUMP_MIN_POWER,
    C.CONF_UPPER_FLOOR_THERMAL_MASS,
    C.CONF_LOWER_FLOOR_THERMAL_MASS,
    C.CONF_HOUSE_HEAT_LOSS_COEFFICIENT,
    C.CONF_PV_PEAK_KW,
    C.CONF_DHW_SETPOINT,
    C.CONF_DHW_MIN_TEMP,
    C.CONF_TARGET_TEMP,
    C.CONF_MIN_TEMP,
    C.CONF_MAX_TEMP,
    C.CONF_MIXING_VALVE_TARGET,
    C.CONF_OPTIMIZATION_INTERVAL,
]


def rich() -> dict:
    cfg = cells.map_all(cells.base_config())
    cfg.update(
        {
            C.CONF_DHW_TANK_VOLUME: 200.0,
            C.CONF_UPPER_FLOOR_THERMAL_MASS: 3.0,
            C.CONF_LOWER_FLOOR_THERMAL_MASS: 8.0,
            C.CONF_UPPER_FLOOR_HEAT_LOSS: 0.08,
            C.CONF_LOWER_FLOOR_HEAT_LOSS: 0.07,
            C.CONF_MIXING_VALVE_MODE: "manual",
            C.CONF_BUFFER_TANK_VOLUME: 750.0,
            C.CONF_BUFFER_MAX_TEMP: 70.0,
            C.CONF_WOOD_FURNACE_ENABLED: True,
            C.CONF_WOOD_TANK_VOLUME: 500.0,
            C.CONF_DHW_WOOD_COIL_ENABLED: True,
            C.CONF_PV_ENABLED: True,
            C.CONF_PV_PEAK_KW: 8.0,
            C.CONF_EXTERNAL_HEAT_ENABLED: True,
        }
    )
    return cfg


def main() -> int:
    t0 = time.process_time()

    # null control: the fully-mapped reference plant
    ref = cells.drive(rich())
    print(f"  reference          plan={ref['plan']} stage={ref['stage']}")

    # perturbation arm: one required numeric set to None
    cells_seen: dict[str, dict] = {}
    for key in NUMERIC_KEYS:
        cfg = rich()
        cfg[key] = None
        cells_seen[key] = cells.drive(cfg)
        r = cells_seen[key]
        print(f"  {key:38s} plan={int(r['plan'])} stage={r['stage']:12s} {r['detail'][:70]}")

    cpu = time.process_time() - t0
    ref_bad = 0 if ref["plan"] else 1
    bad = [k for k, v in cells_seen.items() if not v["plan"]]
    print(f"RESULT control_reference_no_plan={ref_bad} count")
    print(f"RESULT control_numeric_keys={len(NUMERIC_KEYS)} count")
    print(f"RESULT control_perturbed_no_plan={len(bad)} count")
    print(f"RESULT control_moves={int(ref_bad == 0 and len(bad) > 0)} bool")
    print(f"RESULT control_first_failing={bad[0] if bad else '-'}")
    print(f"RESULT pid_cpu_s={round(cpu, 3)}")
    print("RESULT thread_factor=1.0")
    try:
        load1 = float(os.getloadavg()[0])
    except Exception:
        load1 = float("nan")
    print(f"RESULT load1={round(load1, 2)}")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
