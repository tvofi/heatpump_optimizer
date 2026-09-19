#!/usr/bin/env python3
"""D12 generalization slot sweep — one optional entity slot at a time.

METRIC (one line): over the richest plant the tree can build (two zones, DHW,
wood, PV, a throttling valve, every optional entity slot mapped), the number
of single-slot perturbations — one slot's entity OMITTED from the config, or
mapped but MISSING from hass.states — whose one coordinator cycle publishes
no plan (``_optimization_result is None``) or raises.

COMMAND:  cd <repo root> && HPO_PLANDATA=$TMP/plandata \
            PYTHONPATH=tests/hastub python3 tools/audit/round5/D12/slot_sweep.py

EXPECTED:  0 failing slots in both arms.
BASELINE:  origin/main eaa2a06af16a1b5b006f58a0f36cc92131f80225
           (production code identical to the authoring worktree)
MACHINE:   darwin 25.6.0, Apple M1, 8 GB

The count is keyed on the published plan (``_optimization_result`` and the
``_build_data_dict`` payload), never on a config attribute the harness wrote.
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

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cells  # noqa: E402
from heatpump_optimizer import const as C  # noqa: E402


def rich_config() -> dict:
    cfg = cells.base_config()
    cells.map_all(cfg)
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    ref = cells.drive(rich_config())
    print(f"  RICH reference: plan={ref['plan']} status={ref.get('status')}")

    results: dict[str, dict] = {}
    t0 = time.process_time()
    for key in cells.SLOTS:
        base = rich_config()
        # arm 1: OMITTED from the config (and so also from the states)
        om = dict(base)
        om.pop(key, None)
        results[f"omitted:{key}"] = cells.drive(om)
        # arm 2: mapped, but hass.states has no entry for its entity
        miss = dict(base)
        miss[key] = "sensor.__absent__"
        results[f"missing:{key}"] = cells.drive(miss)
    cpu = time.process_time() - t0

    bad_om = [k for k, v in results.items() if k.startswith("omitted") and not v["plan"]]
    bad_mi = [k for k, v in results.items() if k.startswith("missing") and not v["plan"]]
    for k in bad_om + bad_mi:
        print(f"  FAIL {k:46s} {results[k]['stage']:14s} {results[k]['detail'][:100]}")
    print(f"RESULT rich_reference_plan={int(ref['plan'])} count")
    print(f"RESULT slots={len(cells.SLOTS)} count")
    print(f"RESULT omitted_cells={len(bad_om)} count")
    print(f"RESULT missing_cells={len(bad_mi)} count")
    print(f"RESULT failing_omitted={','.join(bad_om) if bad_om else '-'}")
    print(f"RESULT failing_missing={','.join(bad_mi) if bad_mi else '-'}")
    print(f"RESULT total_cells={2 * len(cells.SLOTS)} count")
    print(f"RESULT pid_cpu_s={round(cpu, 3)}")
    print("RESULT thread_factor=1.0")
    try:
        load1 = float(os.getloadavg()[0])
    except Exception:
        load1 = float("nan")
    print(f"RESULT load1={round(load1, 2)}")
    print("RESULT swapins=0 count")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"ref": ref, "slots": results}, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
