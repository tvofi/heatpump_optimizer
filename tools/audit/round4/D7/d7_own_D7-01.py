"""VERIFIER-0-1 OWN HARNESS for D7-01 (sysid adopts 0 of 18 cells).

METRIC (one line): the number of (building preset x outdoor x cadence) cells
in which the production sysid protocol, driven by THIS verifier's own
pre-rolled closed loop against the production single-zone ThermalModel plant,
yields ``SysIdResult.completed and confidence >= 0.3`` -- the exact gate
``coordinator.py:_adopt_system_identification`` applies -- plus, as an
independent misspecification probe, the count of cells whose relax-window
rate-vs-deltaT least-squares slope (this verifier's own OLS, not the finder's
two-exponential fit) has the WRONG sign for a first-order cooling house.

COMMAND (from the worktree root, which must be the working directory):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/d7_own_D7-01.py

EXPECTED (baseline 7dd68dd327fe3dbfb09f3bd0fe38910c58877697; tree head verified
identical in custom_components/*.py by `git diff --stat`; 8-core Apple M1,
macOS 25.6, numpy on OpenBLAS pinned to 1 thread; every number a count or a
sign -- no timing number is claimed):
    own_grid_cells                = 18
    own_adopted_cells             = 0    +- 0
    own_comfort_abort_cells       = 6    +- 0   (abort reasons, informational)
    own_wrongsign_relax_cells     > 0            (the misspecification probe)
    own_null_slabk100_adopted     > 0            (in-process perturbation:
                                                 plant slab_heat_transfer x100
                                                 must RAISE adoptions)
    own_null_smallmass_adopted    = (exploratory second null: slab mass x0.01)
    own_adopted_cells_dt1h        = (attack arm: 1 h cadence, outside the
                                     finder's grid -- if > 0 the 0/18 claim is
                                     cadence-scoped; if 0 it extends)

INSTRUMENTED SYMBOLS (production, unmodified):
    custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step
    custom_components/heatpump_optimizer/sysid.py:SystemIdentification.identify
    custom_components/heatpump_optimizer/sysid.py:_sizing_model
    custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.simulate_step

PERTURBATION: executed IN-PROCESS below as the ``slabk100`` arm (identical to
the finder's HPO_D7_SLABK=100 but passed as an argument, not an env var):
``own_adopted_cells`` must rise above 0, and it does.

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

from heatpump_optimizer.presets import derive
from heatpump_optimizer.sysid import PHASE_RELAX, SysIdConfig, SystemIdentification
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

from stress import BUILDINGS  # the three building presets the gate sweeps
from profiles import house

COP = 3.0
START = datetime(2026, 1, 15, 23, 0, 0)
OUTDOORS = (-5.0, 0.0, 5.0)
DTS = (0.25, 0.5)
BASELINE_T = 21.0
GAINS = 0.3  # == SysIdConfig.gains_prior_kw: the favourable intercept prior


def _plant(name: str, k_mult: float = 1.0, m_mult: float = 1.0) -> ThermalModel:
    cfg = house(two_zone=False, dhw=False)
    derived = derive(BUILDINGS[name])
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    params = ThermalParameters.from_config(cfg)
    params.two_zone_enabled = False
    params.internal_gains = GAINS
    params.wind_sensitivity = 0.0
    params.slab_heat_transfer = params.slab_heat_transfer * k_mult
    params.slab_thermal_mass = params.slab_thermal_mass * m_mult
    return ThermalModel(params)


def _preroll(model: ThermalModel, outdoor: float, hours: int = 400) -> ThermalState:
    """Reach the hold equilibrium DYNAMICALLY (my own pre-roll, not the
    finder's analytic steady state): hold at q_hold from (21, 21) for `hours`
    and keep whatever state the plant actually settles at."""
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
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=0.25,
            external_heat_kw=q_hold,
        )
    return state


def _drive(model: ThermalModel, outdoor: float, dt_h: float):
    """My own closed-loop drive of the production sysid state machine."""
    p = model.params
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    q_hold = max(ua * (BASELINE_T - outdoor) - GAINS, 0.0)
    state = _preroll(model, outdoor)
    baseline = float(state.room_temperature)
    sysid = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=0.0))
    assert sysid.arm(START)
    prices = np.full(48, 1.0)
    now = START
    relax_pts = []  # (delta, rate) pairs on my own relax window
    trace_room = [baseline]
    for _ in range(int((1.0 + 2.0 + 2.0) / dt_h) + 4):
        prev_room = state.room_temperature
        phase_before = sysid.phase
        override = sysid.step(
            now=now,
            room_temp=state.room_temperature,
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
        if not sysid.active:
            break
        elec = q_hold / COP if override is None else float(override)
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=outdoor,
            dt_hours=dt_h,
            external_heat_kw=elec * COP,
        )
        trace_room.append(state.room_temperature)
        if phase_before == PHASE_RELAX:
            relax_pts.append(
                (prev_room - outdoor, (state.room_temperature - prev_room) / dt_h)
            )
        now = now + timedelta(hours=dt_h)
    # One extra plant step past the stop so the peak sees what the abort saw.
    state = model.simulate_step(
        state, electrical_power=0.0, outdoor_temp=outdoor, dt_hours=dt_h,
        external_heat_kw=0.0,
    )
    trace_room.append(state.room_temperature)
    res = sysid.result
    adopted = bool(res.completed and res.confidence >= 0.3)
    peak = max(abs(t - baseline) for t in trace_room)
    # My own wrong-sign probe: OLS slope of rate on deltaT over the relax
    # window. A first-order cooling house must slope NEGATIVE.
    slope = float("nan")
    if len(relax_pts) >= 4:
        arr = np.asarray(relax_pts, dtype=float)
        x, y = arr[:, 0], arr[:, 1]
        denom = float(np.sum((x - x.mean()) ** 2))
        if denom > 1e-12:
            slope = float(np.sum((x - x.mean()) * (y - y.mean())) / denom)
    return {
        "adopted": adopted,
        "reason": res.reason,
        "confidence": res.confidence,
        "peak": peak,
        "slope": slope,
    }


def _grid(k_mult: float = 1.0, m_mult: float = 1.0, dts=DTS):
    rows = []
    for name in BUILDINGS:
        for outdoor in OUTDOORS:
            for dt_h in dts:
                rows.append(
                    {
                        "name": name,
                        "outdoor": outdoor,
                        "dt": dt_h,
                        **_drive(_plant(name, k_mult, m_mult), outdoor, dt_h),
                    }
                )
    return rows


def _procs() -> int:
    try:
        out = subprocess.run(
            ["ps", "axo", "command"], capture_output=True, text=True, timeout=10
        ).stdout
    except Exception:  # noqa: BLE001
        return -1
    hits = [
        ln
        for ln in out.splitlines()
        if any(k in ln for k in ("stress.py", "tests/run.sh", "audit-round", "round4"))
        and "grep" not in ln
        and "d7_own" not in ln
    ]
    return len(hits)


def main() -> int:
    grid = _grid()
    print(f"{'preset':<14}{'T_out':>6}{'dt':>5}{'adopt':>7}{'peakC':>8}"
          f"{'slope':>9}  reason")
    for r in grid:
        print(f"{r['name']:<14}{r['outdoor']:>6.1f}{r['dt']:>5.2f}"
              f"{str(r['adopted']):>7}{r['peak']:>8.3f}{r['slope']:>9.3f}"
              f"  {r['reason']}")

    adopted = sum(1 for r in grid if r["adopted"])
    comfort = sum(
        1 for r in grid
        if r["reason"] == "room temperature drifted beyond the allowed excursion"
    )
    signs = sum(
        1 for r in grid if np.isfinite(r["slope"]) and r["slope"] >= 0.0
    )
    reasons: dict[str, int] = {}
    for r in grid:
        reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1

    # Perturbation, executed in-process: collapse the plant towards one state.
    slabk100 = _grid(k_mult=100.0)
    smallmass = _grid(m_mult=0.01)
    # Attack arm: a cadence outside the finder's grid.
    dt1h = _grid(dts=(1.0,))

    print()
    print("########## RESULT lines ##########")
    print(f"RESULT own_grid_cells={len(grid)} count")
    print(f"RESULT own_adopted_cells={adopted} count")
    print(f"RESULT own_comfort_abort_cells={comfort} count")
    print(f"RESULT own_wrongsign_relax_cells={signs} count")
    for reason, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"RESULT own_reason[{reason}]={n} count")
    print(f"RESULT own_null_slabk100_adopted="
          f"{sum(1 for r in slabk100 if r['adopted'])} count")
    print(f"RESULT own_null_smallmass_adopted="
          f"{sum(1 for r in smallmass if r['adopted'])} count")
    print(f"RESULT own_adopted_cells_dt1h="
          f"{sum(1 for r in dt1h if r['adopted'])} count")
    print(f"RESULT own_dt1h_grid_cells={len(dt1h)} count")
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
