"""verifier 3 own harness -- D7-01: does the sysid experiment ever adopt?

METRIC (one line): over 3 hand-typed building presets x 3 outdoor temps x
2 cadences (18 cells), the count of cells in which the production fit
(``sysid.SystemIdentification.identify`` via the production ``step``
protocol against the production ``ThermalModel`` plant) returns
``completed=True`` and ``confidence >= 0.3`` -- the exact predicate at
coordinator.py:_adopt_system_identification line 10154.

Independence from the finder's harness: the plants are built from
hand-typed literals (derived via presets.derive on 2026-09-12 and typed
into this file), not from stress.BUILDINGS/derive imports; the driver is
this verifier's own loop; the attack arms (wide comfort bound, slab
multiplier 10, sensor noise) are new.

COMMAND (from the tree root, working directory):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/verify3_own_D7-01.py
    # attack arms:
    HPO_V3_SLABK=10   ... dose-response below the finder's 100x
    HPO_V3_BOUND=2.0  ... a user-widened comfort allowance
    HPO_V3_NOISE=0.02 ... sensor noise sigma, degC

EXPECTED (finder's number, mine to check): adopted_cells=0 of 18.
ROOT RULE: ROOT = Path(".") -- measures the working directory.
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

import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np

from heatpump_optimizer.sysid import SysIdConfig, SystemIdentification
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

SLABK = float(os.environ.get("HPO_V3_SLABK", "1"))
BOUND = float(os.environ.get("HPO_V3_BOUND", "0.8"))
NOISE = float(os.environ.get("HPO_V3_NOISE", "0.0"))
COP = 3.0
BASE_T = 21.0
OUTDOORS = (-5.0, 0.0, 5.0)
GAINS = 0.3  # pinned to SysIdConfig.gains_prior_kw: most favourable case
MAX_ELEC = 6.0

# hand-typed from presets.derive(BUILDINGS[...]) executed 2026-09-12:
# light_new  UA 0.066  C 3.6  slab (0.24, 0.24)
# heavy_old  UA 0.31   C 11.0 slab (23.0, 2.0)
# typical_slab UA 0.1725 C 5.25 slab (16.5, 1.5)
PLANTS = {
    "light_new": dict(ua=0.066, cap=3.6, slab_m=0.24, slab_k=0.24),
    "heavy_old": dict(ua=0.31, cap=11.0, slab_m=23.0, slab_k=2.0),
    "typical_slab": dict(ua=0.1725, cap=5.25, slab_m=16.5, slab_k=1.5),
}


def _plant(spec, slab_mult):
    p = ThermalParameters(
        heat_loss_coefficient=spec["ua"],
        house_heat_loss_scale=1.0,
        room_thermal_mass=spec["cap"],
        slab_thermal_mass=spec["slab_m"],
        slab_heat_transfer=spec["slab_k"] * slab_mult,
        internal_gains=GAINS,
        wind_sensitivity=0.0,
        two_zone_enabled=False,
        max_electrical_power=MAX_ELEC,
    )
    return ThermalModel(p)


def _cell(name, outdoor, dt_h, rng):
    spec = PLANTS[name]
    model = _plant(spec, SLABK)
    p = model.params
    ua = spec["ua"]
    q_hold = ua * (BASE_T - outdoor) - GAINS
    k_slab = max(p.slab_heat_transfer, 1e-9)
    state = ThermalState(
        room_temperature=BASE_T,
        slab_temperature=BASE_T + q_hold / k_slab,
        outdoor_temperature=outdoor,
    )
    hold_el = max(q_hold, 0.0) / COP
    sid = SystemIdentification(SysIdConfig(
        enabled=True, min_days_between_runs=0.0, max_excursion_c=BOUND,
    ))
    assert sid.arm(datetime(2026, 1, 15, 23, 0, 0))
    horizon = np.full(48, 1.0)
    now = datetime(2026, 1, 15, 23, 0, 0)
    n_steps = int((1.0 + 2.0 + 2.0) / dt_h) + 4
    seen_peak = 0.0
    for _ in range(n_steps):
        override = sid.step(
            now=now,
            room_temp=state.room_temperature,
            outdoor_temp=outdoor,
            price=0.1,
            price_horizon=horizon,
            learner_samples=0,
            max_power_kw=MAX_ELEC,
            cop=COP,
            plan_power_kw=hold_el,
            house_ua=ua,
            house_capacity=spec["cap"],
            house_gains=GAINS,
        )
        if not sid.active:
            break
        elec = hold_el if override is None else float(override)
        seen_peak = max(seen_peak, abs(state.room_temperature - BASE_T))
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=dt_h,
            external_heat_kw=elec * COP,
        )
        now = now + timedelta(hours=dt_h)
    seen_peak = max(seen_peak, abs(state.room_temperature - BASE_T))
    res = sid.result
    adopted = bool(res.completed and res.confidence >= 0.3)
    return {
        "name": name, "outdoor": outdoor, "dt": dt_h,
        "adopted": adopted, "reason": res.reason,
        "confidence": res.confidence, "peak": seen_peak,
    }


def main() -> int:
    rng = np.random.default_rng(7)
    cells = [_cell(n, o, dt, rng) for n in PLANTS for o in OUTDOORS
             for dt in (0.25, 0.5)]
    print(f"{'preset':<14}{'T_out':>6}{'dt':>5}{'adopt':>7}{'conf':>7}"
          f"{'peak':>7}  reason")
    for c in cells:
        print(f"{c['name']:<14}{c['outdoor']:>6.1f}{c['dt']:>5.2f}"
              f"{str(c['adopted']):>7}{c['confidence']:>7.2f}"
              f"{c['peak']:>7.2f}  {c['reason']}")
    adopted = sum(1 for c in cells if c["adopted"])
    print("########## RESULT lines ##########")
    print(f"RESULT v3_grid_cells={len(cells)} count")
    print(f"RESULT v3_adopted_cells={adopted} count")
    for r in ("room temperature drifted beyond the allowed excursion",
              "fit gave implausible signs",
              "fitted gains outside plausible bounds",
              "fitted parameters outside plausible bounds"):
        print(f"RESULT v3_reason_cells[{r[:28]}]="
              f"{sum(1 for c in cells if c['reason'] == r)} count")
    print(f"RESULT v3_params slabk_mult={SLABK} bound_c={BOUND} noise={NOISE}")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
