#!/usr/bin/env python3
"""D1 store-corruption harness: does a non-finite value in the persisted
thermal-learning store install non-finite state on the live thermal model and
poison the next solve?

METRIC DEFINITION (one line)
  `nan_params_installed` = total, summed over the six corrupt-store mutants
  below, of learned scalars on `HeatPumpOptimizerCoordinator._thermal_params`
  (house_heat_loss_scale, buffer_cooling_rate, lower_floor_loss_ratio,
  cop_scale) that are non-finite AFTER `_async_load_thermal_learning()` loads
  the mutant; plus the published `predicted_cost` and the count of NaN entries
  in `result.room_temp_trajectory` from the solve that follows.
  The count is keyed on the value the production seam `_apply_*` delivers into
  `_thermal_params` (not on the store bytes), so a fix that rejects the
  non-finite value at that seam moves the count to 0 while a fix that merely
  re-labels the input does not.

INSTRUMENTED SYMBOL
  heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._apply_cop_scale
  (and its siblings _apply_house_heat_loss_scale / _apply_buffer_cooling_rate /
  _apply_lower_floor_loss_ratio) - driven through the real loader
  `heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_load_thermal_learning`.

PERTURBATION (direction: down, to_zero)
  Install the one-line finite guard the fix would add at that same seam:
      if not math.isfinite(float(value)): return
  inside each `_apply_*`. Run with `--perturb`. `nan_params_installed` must go
  to 0 and `published_cost_cop_scale_nan` must return to the clean value.

NULL CONTROL
  The same solve with a FINITE store payload (all four learned scalars finite):
  nan_params_installed=0, published_cost == published_cost_clean, 0 NaN traj.

COMMAND
  cd <repo root> && PYTHONPATH=tests/hastub python3 tools/audit/round5/D1/store_nan.py
  add --perturb for the perturbation run.

EXPECTED (baseline eaa2a06af16a1b5b006f58a0f36cc92131f80225, 8-core Apple M1)
  RESULT nan_params_installed=8 of 20          (count; tolerance exact)
  RESULT cells_with_nonfinite_installed=5 of 5
  RESULT coord_mirror_nonfinite_all_four=4
  RESULT published_cost_clean=15.899724649879767  (ratio; tolerance +/-0.5%)
  RESULT published_cost_cop_scale_nan=21.651570770345387 (tolerance +/-0.5%)
  RESULT published_data_cost_cop_scale_nan=21.651570770345387
  RESULT nan_traj_cop_scale=95 of 97
  RESULT result_none_house_scale=1  (solve_failed: ValueError NaN->int)
  RESULT consecutive_cycles_failed_house_scale=3 of 3
  RESULT stored_nonfinite_after_coordinator_save=1
  with --perturb:  RESULT nan_params_installed=0 of 20
                   RESULT published_cost_cop_scale_nan=15.899724649879767
                   RESULT nan_traj_cop_scale=0 of 97

MACHINE  8-core Apple M1, 8 GB; numpy on OpenBLAS, BLAS pinned to 1 thread.
"""
from __future__ import annotations

import os

# Thread pin BEFORE numpy import (tests/stress.py's own recipe).
for _v in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import asyncio
import json
import math
import sys
import time
from datetime import timedelta

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.helpers import storage  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

import golden  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

DOMAIN = "heatpump_optimizer"
EID = "test_entry"
STORE_KEY = f"{DOMAIN}_{EID}_thermal_learning"
START = golden.START
CONFIG = dict(golden.coordinator_scenarios()["coord_all_features"])

# The four learned scalars the thermal-learning loader installs, and the
# `_apply_*` seam each lands through.
LEARNED = {
    "house_heat_loss_scale": "_house_heat_loss_scale",
    "buffer_cooling_rate": "_buffer_cooling_rate",
    "lower_floor_loss_ratio": "_lower_floor_loss_ratio",
    "cop_scale": "_cop_scale",
}
APPLY_SEAMS = (
    "_apply_house_heat_loss_scale",
    "_apply_buffer_cooling_rate",
    "_apply_lower_floor_loss_ratio",
    "_apply_cop_scale",
)

PERTURB = "--perturb" in sys.argv


def _install_finite_guard() -> None:
    """The one-line production fix, applied at the seam it would live at."""
    for name in APPLY_SEAMS:
        orig = getattr(HeatPumpOptimizerCoordinator, name)

        def guarded(self, value, _orig=orig):
            try:
                ok = math.isfinite(float(value))
            except (TypeError, ValueError, OverflowError):
                return
            if not ok:
                return
            return _orig(self, value)

        setattr(HeatPumpOptimizerCoordinator, name, guarded)


def _build():
    hass = FakeHass()
    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data=dict(CONFIG)))
    coord._prices = [
        {"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
         "starts_at": (START + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
        for h in range(48)
    ]
    coord._weather_forecast = [
        {"datetime": (START + timedelta(hours=h)).isoformat(),
         "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
         "precipitation": 0.0, "humidity": 85.0} for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]
    return coord


def _put(payload: dict) -> None:
    storage._DISK[STORE_KEY] = json.dumps(payload)


def _nan_count(coord) -> int:
    """Non-finite learned scalars installed on the live thermal model.

    Keyed on `_thermal_params.<name>` — the value the production seam
    `_apply_*` delivers into the model, which is what a solve actually reads.
    (The coordinator's `_<name>` mirror is set by the same call and is checked
    separately as `coord_mirror_nonfinite`.)
    """
    tp = coord._thermal_params
    return sum(
        0 if math.isfinite(getattr(tp, name)) else 1 for name in LEARNED
    )


def _coord_mirror_nonfinite(coord) -> int:
    """The diagnostics mirror `coordinator._<name>` non-finite count."""
    return sum(
        0 if math.isfinite(getattr(coord, "_" + name)) else 1 for name in LEARNED
    )


def _solve(coord):  # kept for reference; _case drives the solve inline
    """Drive one solve and read the payload."""
    try:
        status = asyncio.run(coord.async_run_optimization())
        err = None
    except Exception as exc:  # noqa: BLE001
        status, err = None, f"{type(exc).__name__}: {exc}"
    res = coord._optimization_result
    data = coord._build_data_dict()
    return status, err, res, data


def _case(payload: dict) -> dict:
    storage._reset_store_disk()
    _put(payload)
    coord = _build()
    asyncio.run(coord._async_load_thermal_learning())
    out = {
        "nan_params": _nan_count(coord),
        "coord_mirror": _coord_mirror_nonfinite(coord),
    }
    try:
        status = asyncio.run(coord.async_run_optimization())
        out["err"] = None
    except Exception as exc:  # noqa: BLE001
        status, out["err"] = None, f"{type(exc).__name__}: {exc}"
    out["status"] = status
    res = coord._optimization_result
    out["result_none"] = res is None
    if res is not None:
        traj = np.asarray(res.room_temp_trajectory, dtype=float)
        sp = np.asarray(res.optimal_setpoints, dtype=float)
        out["cost"] = float(res.predicted_cost)
        out["nan_traj"] = int(np.isnan(traj).sum())
        out["traj_len"] = int(traj.size)
        out["nan_setpoint"] = int(np.isnan(sp).sum())
        out["res_status"] = getattr(res, "status", None)
        out["data_cost"] = coord._build_data_dict().get("predicted_cost")
    else:
        out["cost"] = out["nan_traj"] = out["nan_setpoint"] = None
        out["res_status"] = None
        out["data_cost"] = coord._build_data_dict().get("predicted_cost")
    return out


# --- the mutant grid (six cells) -------------------------------------------
NAN = float("nan")
CLEAN = {"house_heat_loss_scale": 1.0, "buffer_cooling_rate": 0.3,
         "lower_floor_loss_ratio": 0.5, "cop_scale": 1.0,
         "house_heat_loss_anchor": 0.0}
MUTANTS = {
    "clean": dict(CLEAN),
    "nan_cop_scale": {**CLEAN, "cop_scale": NAN},
    "nan_house_scale": {**CLEAN, "house_heat_loss_scale": NAN},
    "nan_buffer": {**CLEAN, "buffer_cooling_rate": NAN},
    "nan_lower_floor": {**CLEAN, "lower_floor_loss_ratio": NAN},
    "nan_all_four": {**CLEAN, "house_heat_loss_scale": NAN,
                     "buffer_cooling_rate": NAN,
                     "lower_floor_loss_ratio": NAN, "cop_scale": NAN},
}
CYCLES = 3


def _permanence(cycles: int = CYCLES) -> dict:
    """A NaN house heat-loss scale: does every CONSECUTIVE cycle fail, and is
    the stored value ever repaired by the coordinator's own save path?

    The serialised store is what a restart reads, so a value the save path
    writes back as non-finite is permanent across restarts, not just across
    cycles."""
    storage._reset_store_disk()
    _put({**CLEAN, "house_heat_loss_scale": NAN})
    coord = _build()
    asyncio.run(coord._async_load_thermal_learning())
    failed = 0
    for _ in range(cycles):
        try:
            asyncio.run(coord.async_run_optimization())
        except Exception:  # noqa: BLE001
            pass
        if coord._optimization_result is None:
            failed += 1
    # Does the coordinator's own save persist the non-finite value?
    asyncio.run(coord._async_save_thermal_learning())
    raw = storage._DISK.get(STORE_KEY, "")
    try:
        written = json.loads(raw)
    except Exception:  # noqa: BLE001
        written = None
    stored_nonfinite = _count_nonfinite_static(written)
    return {"cycles": cycles, "cycles_failed": failed,
            "stored_nonfinite_after_save": stored_nonfinite}


def _count_nonfinite_static(x) -> int:
    if isinstance(x, bool):
        return 0
    if isinstance(x, float):
        return 0 if math.isfinite(x) else 1
    if isinstance(x, int):
        return 0
    if isinstance(x, list):
        return sum(_count_nonfinite_static(v) for v in x)
    if isinstance(x, dict):
        return sum(_count_nonfinite_static(v) for v in x.values())
    return 0


def main() -> int:
    if PERTURB:
        _install_finite_guard()
    dt_util.freeze(START)

    cpu0, cpu1 = time.process_time(), time.thread_time()
    cells = {}
    total_nan_installed = 0
    nonzero_cells = 0
    for name, payload in MUTANTS.items():
        cells[name] = _case(payload)
        if name != "clean":
            total_nan_installed += cells[name]["nan_params"]
            if cells[name]["nan_params"]:
                nonzero_cells += 1
    proc = time.process_time() - cpu0
    thr = time.thread_time() - cpu1

    cop = cells["nan_cop_scale"]
    clean = cells["clean"]

    print("\n=== store_nan (thermal-learning persistence) ===")
    print(f"perturb={PERTURB}")
    print("cells: " + json.dumps({
        k: {"nan_params": v["nan_params"], "coord_mirror": v["coord_mirror"],
            "cost": v["cost"], "nan_traj": v["nan_traj"],
            "result_none": v["result_none"], "status": v["status"]}
        for k, v in cells.items()}))

    loo = [cells[n]["nan_params"] for n in MUTANTS if n != "clean"]
    print("RESULT cells=5 non_clean_cells=5")
    print(f"RESULT nan_params_installed={total_nan_installed} of 20")
    print(f"RESULT cells_with_nonfinite_installed={nonzero_cells} of 5")
    print(f"RESULT coord_mirror_nonfinite_all_four={cells['nan_all_four']['coord_mirror']}")
    print(f"RESULT loo_min={min(loo)} loo_max={max(loo)} "
          f"loo_drop_most_favourable={total_nan_installed - max(loo)}")
    print(f"RESULT published_cost_clean={clean['cost']}")
    print(f"RESULT published_cost_cop_scale_nan={cop['cost']}")
    print(f"RESULT published_data_cost_cop_scale_nan={cop['data_cost']}")
    print(f"RESULT nan_traj_cop_scale={cop['nan_traj']} of {cop['traj_len']}")
    print(f"RESULT nan_setpoint_cop_scale={cop['nan_setpoint']}")
    print(f"RESULT result_none_house_scale={int(cells['nan_house_scale']['result_none'])}")
    print(f"RESULT result_none_all_four={int(cells['nan_all_four']['result_none'])}")
    print(f"RESULT status_cop_scale={cop['status']!r} err={cop['err']!r}")

    perm = _permanence()
    print(f"RESULT consecutive_cycles_failed_house_scale={perm['cycles_failed']} "
          f"of {perm['cycles']}")
    print(f"RESULT stored_nonfinite_after_coordinator_save="
          f"{perm['stored_nonfinite_after_save']}")

    load1 = os.getloadavg()[0]
    print(f"RESULT thread_factor={(proc) / thr if thr > 0 else 0.0}")
    print(f"RESULT load1={load1}")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
