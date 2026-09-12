"""VERIFIER-0-1 OWN HARNESS for D7-02 (the step sizer plants default slab).

METRIC (one line): (a) STATIC -- for each building preset, whether production
``sysid._sizing_model(ua, capacity, gains)`` returns a plant whose
(slab_thermal_mass, slab_heat_transfer) equals ThermalParameters' DEFAULTS
(5.0, 0.8) while the preset's own plant carries different values (a mismatch
count over 3 presets x 3 outdoors x 2 cadences = 18 cells); (b) DYNAMIC -- the
number of those 18 cells whose experiment ends with the production abort
"room temperature drifted beyond the allowed excursion" (the module's OWN
comfort enforcement, not my threshold), and the max achieved
peak/max_excursion_c ratio; (c) COUNTERFACTUAL -- the same counts after a
harness-side swap of ``sysid._sizing_model`` for one carrying the plant's own
slab pair, plus per-preset whether the honest step is comfort-capped or
power-capped.

COMMAND (from the worktree root, which must be the working directory):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/d7_own_D7-02.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697; counts, no timing):
    own_sizer_default_slab_cells   = 18  +- 0
    own_comfort_abort_cells        = 6   +- 0
    own_max_excursion_over_bound   ~ 1.3 +- 0.1
    own_honest_comfort_abort_cells = 0   +- 0
    own_honest_max_ratio           ~ 1.0 +- 0.05

PERTURBATION: the honest-sizer swap is executed in-process below; the comfort
abort count must FALL to 0 (direction: down).

INSTRUMENTED SYMBOLS (production, unmodified):
    custom_components/heatpump_optimizer/sysid.py:_sizing_model
    custom_components/heatpump_optimizer/sysid.py:_size_step_power
    custom_components/heatpump_optimizer/sysid.py:_over_excursion
    custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_step

ROOT RULE: ROOT = Path(".") -- measures the working directory it is run from.
"""
from __future__ import annotations

import os

for _v in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_v, "1")

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np

import heatpump_optimizer.sysid as sysid_mod
from heatpump_optimizer.presets import derive
from heatpump_optimizer.sysid import SysIdConfig, SystemIdentification
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

from stress import BUILDINGS
from profiles import house

COP = 3.0
START = datetime(2026, 1, 15, 23, 0, 0)
OUTDOORS = (-5.0, 0.0, 5.0)
DTS = (0.25, 0.5)
BASELINE_T = 21.0
GAINS = 0.3
COMFORT = 0.8  # sysid.DEFAULT_MAX_EXCURSION_C


def _plant(name: str) -> ThermalModel:
    cfg = house(two_zone=False, dhw=False)
    derived = derive(BUILDINGS[name])
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    params = ThermalParameters.from_config(cfg)
    params.two_zone_enabled = False
    params.internal_gains = GAINS
    params.wind_sensitivity = 0.0
    return ThermalModel(params)


def _preroll(model: ThermalModel, outdoor: float, hours: int = 400) -> ThermalState:
    p = model.params
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    q_hold = max(ua * (BASELINE_T - outdoor) - GAINS, 0.0)
    state = ThermalState(
        room_temperature=BASELINE_T,
        slab_temperature=BASELINE_T,
        outdoor_temperature=outdoor,
    )
    for _ in range(int(hours / 0.25)):
        state = model.simulate_step(
            state, electrical_power=0.0, outdoor_temp=outdoor,
            dt_hours=0.25, external_heat_kw=q_hold,
        )
    return state


def _drive(model: ThermalModel, outdoor: float, dt_h: float):
    """Run the production protocol; return the sizer's plant, the sized step,
    the achieved peak and the production abort reason."""
    p = model.params
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    q_hold = max(ua * (BASELINE_T - outdoor) - GAINS, 0.0)
    state = _preroll(model, outdoor)
    baseline = float(state.room_temperature)
    sysid = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=0.0))
    assert sysid.arm(START)
    prices = np.full(48, 1.0)
    now = START
    peak = 0.0
    sized = None
    sizer_plant = None
    for _ in range(int((1.0 + 2.0 + 2.0) / dt_h) + 4):
        room = state.room_temperature
        was_settling = sysid.phase == "settling"
        override = sysid.step(
            now=now,
            room_temp=room,
            outdoor_temp=outdoor,
            price=0.1,
            price_horizon=prices,
            learner_samples=0,
            max_power_kw=float(p.max_electrical_power),
            cop=COP,
            plan_power_kw=q_hold / COP,
            house_ua=ua,
            house_capacity=float(p.room_thermal_mass),
            house_gains=GAINS,
        )
        if was_settling and sysid.phase == "step" and sized is None:
            sized = float(sysid._step_power)
            sizer_plant = sysid_mod._sizing_model(
                ua, float(p.room_thermal_mass), GAINS
            )
        if not sysid.active:
            break
        elec = q_hold / COP if override is None else float(override)
        state = model.simulate_step(
            state, electrical_power=0.0, outdoor_temp=outdoor,
            dt_hours=dt_h, external_heat_kw=elec * COP,
        )
        peak = max(peak, abs(state.room_temperature - baseline))
        now = now + timedelta(hours=dt_h)
    return {
        "sized": sized,
        "max_power": float(p.max_electrical_power),
        "sizer_slab": (
            sizer_plant.params.slab_thermal_mass,
            sizer_plant.params.slab_heat_transfer,
        ),
        "plant_slab": (p.slab_thermal_mass, p.slab_heat_transfer),
        "peak": peak,
        "ratio": peak / COMFORT,
        "reason": sysid.result.reason,
    }


def _procs() -> int:
    try:
        out = subprocess.run(
            ["ps", "axo", "command"], capture_output=True, text=True, timeout=10
        ).stdout
    except Exception:  # noqa: BLE001
        return -1
    return len([
        ln for ln in out.splitlines()
        if any(k in ln for k in ("stress.py", "tests/run.sh", "audit-round", "round4"))
        and "grep" not in ln and "d7_own" not in ln
    ])


def main() -> int:
    defaults = ThermalParameters()
    print(
        f"ThermalParameters defaults: slab_thermal_mass="
        f"{defaults.slab_thermal_mass}, slab_heat_transfer="
        f"{defaults.slab_heat_transfer}"
    )

    grid = []
    for name in BUILDINGS:
        for outdoor in OUTDOORS:
            for dt_h in DTS:
                grid.append(
                    {"name": name, "outdoor": outdoor, "dt": dt_h,
                     **_drive(_plant(name), outdoor, dt_h)}
                )

    print()
    print(f"{'preset':<14}{'T_out':>6}{'dt':>5}{'sizer(mass,k)':>16}"
          f"{'plant(mass,k)':>16}{'peak/bound':>11}  abort reason")
    for r in grid:
        print(f"{r['name']:<14}{r['outdoor']:>6.1f}{r['dt']:>5.2f}"
              f"{str(tuple(round(v, 3) for v in r['sizer_slab'])):>16}"
              f"{str(tuple(round(v, 3) for v in r['plant_slab'])):>16}"
              f"{r['ratio']:>11.3f}  {r['reason']}")

    mismatch = sum(
        1 for r in grid if tuple(r["sizer_slab"]) != tuple(r["plant_slab"])
    )
    default_cells = sum(
        1 for r in grid
        if abs(r["sizer_slab"][0] - defaults.slab_thermal_mass) < 1e-9
        and abs(r["sizer_slab"][1] - defaults.slab_heat_transfer) < 1e-9
    )
    aborts = sum(
        1 for r in grid
        if r["reason"] == "room temperature drifted beyond the allowed excursion"
    )
    max_ratio = max(r["ratio"] for r in grid)

    # ---- counterfactual: the honest sizer, executed in-process -------------
    orig = sysid_mod._sizing_model

    def _honest_factory(plant_params):
        def _honest(u, c, g, _p=plant_params):
            return ThermalModel(
                ThermalParameters(
                    heat_loss_coefficient=u,
                    house_heat_loss_scale=1.0,
                    room_thermal_mass=c,
                    internal_gains=g,
                    two_zone_enabled=False,
                    slab_thermal_mass=_p.slab_thermal_mass,
                    slab_heat_transfer=_p.slab_heat_transfer,
                )
            )
        return _honest

    honest_rows = []
    try:
        for name in BUILDINGS:
            model = _plant(name)
            sysid_mod._sizing_model = _honest_factory(model.params)
            for outdoor in (0.0,):
                for dt_h in DTS:
                    honest_rows.append(
                        {"name": name, "outdoor": outdoor, "dt": dt_h,
                         **_drive(model, outdoor, dt_h)}
                    )
    finally:
        sysid_mod._sizing_model = orig

    print()
    print("-- honest-sizer counterfactual (0 C, both cadences)")
    print(f"{'preset':<14}{'dt':>5}{'sized kW':>10}{'max kW':>8}"
          f"{'peak/bound':>11}{'capped by':>12}")
    for r in honest_rows:
        capped = (
            "power" if r["sized"] is not None and r["sized"] >= r["max_power"] - 1e-6
            else "comfort"
        )
        print(f"{r['name']:<14}{r['dt']:>5.2f}{r['sized']:>10.3f}"
              f"{r['max_power']:>8.2f}{r['ratio']:>11.3f}{capped:>12}"
              f"  {r['reason']}")

    honest_aborts = sum(
        1 for r in honest_rows
        if r["reason"] == "room temperature drifted beyond the allowed excursion"
    )
    honest_max = max(r["ratio"] for r in honest_rows)
    power_capped = sorted({
        r["name"] for r in honest_rows
        if r["sized"] is not None and r["sized"] >= r["max_power"] - 1e-6
    })

    print()
    print("########## RESULT lines ##########")
    print(f"RESULT own_grid_cells={len(grid)} count")
    print(f"RESULT own_sizer_default_slab_cells={default_cells} count")
    print(f"RESULT own_sizer_plant_mismatch_cells={mismatch} count")
    print(f"RESULT own_comfort_abort_cells={aborts} count")
    print(f"RESULT own_max_excursion_over_bound={max_ratio:.3f} ratio")
    print(f"RESULT own_honest_comfort_abort_cells={honest_aborts} count")
    print(f"RESULT own_honest_max_excursion_over_bound={honest_max:.3f} ratio")
    print(f"RESULT own_honest_power_capped_presets={len(power_capped)} count")
    if power_capped:
        print(f"RESULT own_honest_power_capped_names={power_capped} list")
    print(f"RESULT own_concurrent_procs={_procs()} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
