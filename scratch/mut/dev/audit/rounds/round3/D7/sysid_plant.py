#!/usr/bin/env python3
"""D7-01 harness: the first-order sysid experiment against the second-order plant.

METRIC (one line): excursion_ratio = (max |room_temp - baseline| observed during
one SystemIdentification experiment driven over the production
ThermalModel.simulate_step) / SysIdConfig.max_excursion_c -- i.e. the fraction
of the comfort allowance the experiment actually spends on excitation; with
completed_cells = how many grid cells reach SysIdResult.completed is True.

RUN (from the repository root, nothing else):
    PYTHONPATH=tests/hastub python3 tools/audit/round3/D7/sysid_plant.py

EXPECTED (baseline ae36eff19d8e542bc351b1ab31ad4167ec8e4ea1, 8-core Apple M1,
python3 3.11.5 / numpy 2.4.6 / scipy 1.17.1). Every number is a count or a
ratio, so contention cannot move any of them:
    excursion_ratio_worst          = 0.092 +/- 0.01
    excursion_ratio_best           = 0.729 +/- 0.01
    excursion_ratio_loo_worst      = 0.092 +/- 0.01  (single best cell dropped)
    excursion_ratio_loo_best       = 0.671 +/- 0.01
    excursion_c_worst              = 0.0733 +/- 0.005 degC
    cells_below_stated_noise_0.10  = 6     exactly   (of 9)
    grid_cells                     = 9     exactly
    completed_cells                = 1     exactly   (of 9, noise-free)
    admitted_cells                 = 0     exactly   (of 9)
    completed_cells_noise0.02      = 1 ;  admitted_cells_noise0.02 = 1
    completed_cells_noise0.10      = 3 ;  admitted_cells_noise0.10 = 2
    null_excursion_ratio_worst     = 0.996 +/- 0.01   NULL CONTROL
    null_completed_cells           = 9     exactly    NULL CONTROL
    null_admitted_cells            = 9     exactly    NULL CONTROL
    null_ua_bias_pct_worst         = 0.00  +/- 0.5    NULL CONTROL
    secondorder_ua_bias_pct_worst  = 0.000 +/- 0.5
    perturb_massless_slab_ratio_worst = 0.816 +/- 0.02 (must exceed 0.092)
    perturb_massless_slab_completed   = 9 exactly      (must exceed 1)
    perturb_massless_slab_admitted    = 9 exactly      (must exceed 0)

WHAT IT SHOWS
    ThermalModel._simulate_step_single is a two-state plant: the pump's thermal
    output enters the SLAB (dT_slab = (thermal_power - q_slab_to_room)/
    slab_thermal_mass) and reaches the room only through
    params.slab_heat_transfer. Both halves of sysid.py assume ONE state with the
    heat in the room:
      * SystemIdentification._size_step_power sizes the step through
        sysid._predict_step_excursion, a single exponential on
        (house_ua, house_capacity=room_thermal_mass, house_gains). The
        coordinator passes exactly those (coordinator.py
        _run_system_identification), so the step is sized to spend the whole
        0.8 degC comfort allowance -- and the slab eats it.
      * SystemIdentification.identify regresses the room's rate on the pump's
        own thermal output, which the room never sees directly.

    Consequence measured below: the experiment spends a five-hour night, two
    hours of it with the pump commanded off, and moves the room by a tenth of
    what the comfort constraint would have allowed -- on two of the three
    presets by less than the 0.10 degC sensor noise sysid.py's own SysIdConfig
    docstring names as the case the fit must survive.

ARMS
    null (the control the claim must vanish in): the SAME protocol on the plant
        the identifier assumes -- one state, heat straight into the room,
        integrated by the exact exponential sysid._predict_step_excursion is
        derived from. If the effect is a protocol or arithmetic artefact rather
        than a plant-order one, it must show up here too. It does not.
    secondorder: the SAME rows fitted with the correct second-order regression
        (linear in the parameters after eliminating the slab state), showing the
        rows do carry UA and that it is the first-order structure that loses it.
    perturb_massless_slab (the judge's PERTURBATION): one production parameter,
        params.slab_thermal_mass, multiplied by 0.01. That is the well-mixed
        massless-slab limit in which the two-state plant collapses to the
        one-state model sysid assumes. DIRECTION: excursion_ratio must RISE and
        completed_cells must RISE.
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

import resource  # noqa: E402
import sys  # noqa: E402
import threading  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from heatpump_optimizer.presets import (  # noqa: E402
    BuildingPreset,
    EMITTER_FLOOR,
    EMITTER_RADIATORS,
    ERA_1960_1980,
    ERA_POST_2005,
    ERA_PRE_1960,
    STRUCTURE_CONCRETE_SLAB,
    STRUCTURE_MASONRY,
    STRUCTURE_TIMBER_CRAWLSPACE,
    derive,
)
from heatpump_optimizer.sysid import (  # noqa: E402
    PHASE_RELAX,
    PHASE_SETTLING,
    PHASE_STEP,
    SysIdConfig,
    SystemIdentification,
)
from heatpump_optimizer.thermal_model import (  # noqa: E402
    ThermalModel,
    ThermalParameters,
    ThermalState,
)
from profiles import house  # noqa: E402

UTC = timezone.utc
# 23:30 is inside the night window sysid.conditions_met requires (23 -> 5).
START = datetime(2026, 1, 15, 23, 30, tzinfo=UTC)
CADENCE_H = 0.5  # const.DEFAULT_OPTIMIZATION_INTERVAL = 30 minutes
SUBSTEPS = 30  # one production simulate_step per minute between sysid samples
BASELINE = 21.0  # profiles.house()["target_temperature"]
# Inside SysIdConfig's [min_outdoor_temp, max_outdoor_temp] = [-5, 10].
OUTDOORS = (-4.0, 0.0, 8.0)
#: The noise level sysid.SysIdConfig's own docstring names as the case the fit
#: must survive ("a 0.10 degC-noise night at the 30-minute cadence").
STATED_NOISE_C = 0.10

# The three presets tests/stress.py:BUILDINGS sweeps.
PRESETS = {
    "light_new": BuildingPreset(
        structure=STRUCTURE_TIMBER_CRAWLSPACE,
        era=ERA_POST_2005,
        heated_area_m2=120,
        lower_emitter=EMITTER_RADIATORS,
    ),
    "heavy_old": BuildingPreset(
        structure=STRUCTURE_MASONRY,
        era=ERA_PRE_1960,
        heated_area_m2=200,
        lower_emitter=EMITTER_FLOOR,
    ),
    "typical_slab": BuildingPreset(
        structure=STRUCTURE_CONCRETE_SLAB,
        era=ERA_1960_1980,
        heated_area_m2=150,
        lower_emitter=EMITTER_FLOOR,
    ),
}
USABLE = (PHASE_SETTLING, PHASE_STEP, PHASE_RELAX)


def build_params(name: str, slab_mass_scale: float = 1.0) -> ThermalParameters:
    cfg = house(two_zone=False, dhw=False)
    derived = derive(PRESETS[name])
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    if slab_mass_scale != 1.0:
        params.slab_thermal_mass = float(params.slab_thermal_mass) * slab_mass_scale
        params.clamp()
    return params


def run_experiment(
    params: ThermalParameters,
    outdoor: float,
    first_order: bool = False,
    noise_c: float = 0.0,
    seed: int = 7,
):
    """Drive the real state machine over a plant. Returns (sysid, peak, cfg)."""
    model = ThermalModel(params)
    cop = model.compute_cop(outdoor)
    ua = float(params.heat_loss_coefficient)
    gains = float(params.internal_gains)
    rng = np.random.default_rng(seed)

    # Start on the plan's own steady state: the room sits at target, the slab
    # delivers exactly the net loss, the pump delivers exactly what the slab
    # loses. Nothing is drifting when the experiment arms.
    q_room_needed = ua * (BASELINE - outdoor) - gains
    plan_electrical = max(q_room_needed, 0.0) / max(cop, 0.1)
    room = BASELINE
    state = ThermalState(
        room_temperature=BASELINE,
        slab_temperature=BASELINE + q_room_needed / max(params.slab_heat_transfer, 1e-9),
        outdoor_temperature=outdoor,
    )

    cfg = SysIdConfig(
        enabled=True,
        gains_prior_kw=gains,
        thermal_mass_prior=float(params.room_thermal_mass),
    )
    sysid = SystemIdentification(cfg)
    assert sysid.arm(START)
    prices = np.full(48, 1.0)

    now = START
    peak = 0.0
    for _ in range(400):
        reported = room + (rng.normal(0.0, noise_c) if noise_c > 0.0 else 0.0)
        override = sysid.step(
            now=now,
            room_temp=float(reported),
            outdoor_temp=outdoor,
            price=0.1,
            price_horizon=prices,
            learner_samples=0,
            max_power_kw=float(params.max_electrical_power),
            cop=cop,
            plan_power_kw=plan_electrical,
            house_ua=ua,
            house_capacity=float(params.room_thermal_mass),
            house_gains=gains,
        )
        if not sysid.active:
            break
        electrical = plan_electrical if override is None else float(override)
        if first_order:
            # The plant sysid ASSUMES: one state, heat in the room, integrated
            # by the exact exponential sysid._predict_step_excursion uses.
            q = cop * electrical + gains
            t_ss = outdoor + q / ua
            room = float(t_ss + (room - t_ss) * np.exp(-CADENCE_H * ua / params.room_thermal_mass))
        else:
            for _s in range(SUBSTEPS):
                state = model.simulate_step(
                    state,
                    electrical_power=electrical,
                    outdoor_temp=outdoor,
                    dt_hours=CADENCE_H / SUBSTEPS,
                )
            room = float(state.room_temperature)
        peak = max(peak, abs(room - BASELINE))
        now += timedelta(hours=CADENCE_H)
    return sysid, peak, cfg


def second_order_ua(sysid: SystemIdentification) -> float | None:
    """Two-exponential (second-order) fit of the SAME samples, for UA.

    Eliminating the slab state from the production plant's two equations gives,
    at constant outdoor temperature,
        a*T'' + b*T' + UA*(T - T_out) - G = Q,   a = Cr*Cs/k, b = Cs*(k+UA)/k + Cr
    which is linear in (a, b, UA, G): regress Q on [T'', T', (T - T_out), 1].
    Only interior points whose three-sample window lies inside ONE phase are
    used -- power is discontinuous at a phase boundary, so a difference across
    one estimates nothing.
    """
    s = [x for x in sysid.samples if x.phase in USABLE]
    if len(s) < 8:
        return None
    temp = np.array([x.room_temp for x in s])
    out = np.array([x.outdoor_temp for x in s])
    q = np.array([x.power_kw for x in s])
    h = CADENCE_H
    keep = [
        i
        for i in range(1, len(s) - 1)
        if s[i - 1].phase == s[i].phase == s[i + 1].phase
    ]
    if len(keep) < 5:
        return None
    idx = np.array(keep)
    d1 = (temp[idx + 1] - temp[idx - 1]) / (2.0 * h)
    d2 = (temp[idx + 1] - 2.0 * temp[idx] + temp[idx - 1]) / (h * h)
    delta = temp[idx] - out[idx]
    a = np.column_stack([d2, d1, delta, np.ones_like(delta)])
    sol, _r, rank, _sv = np.linalg.lstsq(a, q[idx], rcond=None)
    if rank < 4:
        return None
    return float(sol[2])


def cell(
    name: str,
    outdoor: float,
    first_order: bool = False,
    noise_c: float = 0.0,
    slab_mass_scale: float = 1.0,
) -> dict:
    params = build_params(name, slab_mass_scale=slab_mass_scale)
    sysid, peak, cfg = run_experiment(
        params, outdoor, first_order=first_order, noise_c=noise_c
    )
    res = sysid.result
    true_ua = float(params.heat_loss_coefficient)
    ident = res.heat_loss_kw_per_c
    so = second_order_ua(sysid)
    return {
        "cell": f"{name}@{outdoor:+.0f}C",
        "name": name,
        "outdoor": outdoor,
        "true_ua": true_ua,
        "peak_c": peak,
        "ratio": peak / cfg.max_excursion_c,
        "completed": bool(res.completed),
        # coordinator._adopt_system_identification: completed and conf >= 0.3.
        "admitted": bool(res.completed and res.confidence >= 0.3),
        "confidence": float(res.confidence),
        "reason": res.reason,
        "ua_bias": None if ident is None else 100.0 * (ident / true_ua - 1.0),
        "so_bias": None if so is None else 100.0 * (so / true_ua - 1.0),
    }


def grid(**kw) -> list[dict]:
    return [cell(n, o, **kw) for n in PRESETS for o in OUTDOORS]


def _fmt(v, spec="%+.2f"):
    return (spec % v) if v is not None else "    -   "


def thread_factor() -> float:
    """process CPU / single-thread CPU over one identical numpy workload."""
    m = np.random.default_rng(0).standard_normal((300, 300))
    t0, w0 = time.process_time(), time.thread_time()
    for _ in range(6):
        m @ m
    t1, w1 = time.process_time(), time.thread_time()
    dt, dw = t1 - t0, w1 - w0
    return float(dt / dw) if dw > 1e-9 else 1.0


def main() -> int:
    base = grid()
    print(
        "\nBASE (production ThermalModel, noise-free)\n"
        "cell                 peak_degC  ratio  completed  conf    UA_bias%   2nd-order%  reason"
    )
    for r in base:
        print(
            f"  {r['cell']:<18} {r['peak_c']:8.4f}  {r['ratio']:5.3f}  "
            f"{str(r['completed']):>9}  {r['confidence']:.3f}  "
            f"{_fmt(r['ua_bias']):>9}  {_fmt(r['so_bias'], '%+.3f'):>10}  {r['reason']}"
        )

    nulls = grid(first_order=True)
    print("\nNULL CONTROL (the one-state plant sysid assumes, same protocol)")
    for r in nulls:
        print(
            f"  {r['cell']:<18} {r['peak_c']:8.4f}  {r['ratio']:5.3f}  "
            f"{str(r['completed']):>9}  {r['confidence']:.3f}  "
            f"{_fmt(r['ua_bias']):>9}  {r['reason']}"
        )

    noisy = {n: grid(noise_c=n) for n in (0.02, 0.10)}
    pert = grid(slab_mass_scale=0.01)
    print("\nPERTURBATION (params.slab_thermal_mass x 0.01, massless-slab limit)")
    for r in pert:
        print(
            f"  {r['cell']:<18} {r['peak_c']:8.4f}  {r['ratio']:5.3f}  "
            f"{str(r['completed']):>9}  {r['confidence']:.3f}  "
            f"{_fmt(r['ua_bias']):>9}  {r['reason']}"
        )

    ratios = [r["ratio"] for r in base]
    worst, best = min(ratios), max(ratios)
    loo = sorted(ratios)[:-1]  # drop the single most favourable cell
    print()
    print(f"RESULT excursion_ratio_worst={worst:.3f} ratio")
    print(f"RESULT excursion_ratio_best={best:.3f} ratio")
    print(f"RESULT excursion_ratio_range={best - worst:.3f} ratio")
    print(f"RESULT excursion_ratio_loo_worst={min(loo):.3f} ratio")
    print(f"RESULT excursion_ratio_loo_best={max(loo):.3f} ratio")
    print(f"RESULT excursion_c_worst={min(r['peak_c'] for r in base):.4f} degC")
    print(
        f"RESULT cells_below_stated_noise_{STATED_NOISE_C:.2f}="
        f"{sum(1 for r in base if r['peak_c'] < STATED_NOISE_C)} count"
    )
    print(f"RESULT grid_cells={len(base)} count")
    print(f"RESULT completed_cells={sum(1 for r in base if r['completed'])} count")
    print(f"RESULT admitted_cells={sum(1 for r in base if r['admitted'])} count")
    for lvl, rs in noisy.items():
        print(
            f"RESULT completed_cells_noise{lvl:.2f}="
            f"{sum(1 for r in rs if r['completed'])} count"
        )
        print(
            f"RESULT admitted_cells_noise{lvl:.2f}="
            f"{sum(1 for r in rs if r['admitted'])} count"
        )
    print(f"RESULT null_excursion_ratio_worst={min(r['ratio'] for r in nulls):.3f} ratio")
    print(f"RESULT null_completed_cells={sum(1 for r in nulls if r['completed'])} count")
    print(f"RESULT null_admitted_cells={sum(1 for r in nulls if r['admitted'])} count")
    nb = [abs(r["ua_bias"]) for r in nulls if r["ua_bias"] is not None]
    print(f"RESULT null_ua_bias_pct_worst={(max(nb) if nb else float('nan')):.2f} percent")
    sb = [abs(r["so_bias"]) for r in base if r["so_bias"] is not None]
    print(
        f"RESULT secondorder_ua_bias_pct_worst="
        f"{(max(sb) if sb else float('nan')):.3f} percent"
    )
    print(
        f"RESULT perturb_massless_slab_ratio_worst={min(r['ratio'] for r in pert):.3f} ratio"
    )
    print(
        f"RESULT perturb_massless_slab_completed="
        f"{sum(1 for r in pert if r['completed'])} count"
    )
    print(
        f"RESULT perturb_massless_slab_admitted="
        f"{sum(1 for r in pert if r['admitted'])} count"
    )

    print(f"RESULT thread_factor={thread_factor():.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
    print(f"RESULT threads_alive={threading.active_count()} count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
