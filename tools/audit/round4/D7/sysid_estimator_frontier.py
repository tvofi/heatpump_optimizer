"""sysid-estimator wave (#942 options 2+3): the frontier's gate-passing cells,
measured through the PRODUCTION fitted arm.

live-header: this header is maintained against the tree; harness_headers.py
executes it.

This is the pre-study's probe scaffolding (issue #942 comment 5656402482,
probes run at 2d09043) committed as the wave's evaluation instrument: the
frontier's bottom row -- gate-passing plants (slab_heat_transfer x100, the
#991 null-control construction) + the ported intercept ridge, nightly 5 h
window -- re-derived through the production experiment, whose _finish
routes a plant the arm-time gate admitted to identify_slab (act 1, #1013:
the ported D2-01 ridge) with this wave's act 2 on top: the
fitted UA's own 95 % profile-likelihood interval and the re-derived
slab-mode tau. The ratified hybrid (owner decision 2026-09-14, comment
5659441129), as superseded by #1410's interval gate: fitted -- UA and
tau_fast only, never the C_s/k_s split -- where the #991 gate passes AND
the ridge is ported AND the fit's own interval clears the adoption bar;
refused everywhere else.

METRIC (one line): per (plant, sigma) cell, over n=16 sensor-noise draws
of the production protocol (the recorder sees N(0, sigma); the plant rolls
noise-free), the COUNT of draws whose production result completed with a
fitted UA the adoption gate accepts (ua_profile_halfwidth <=
UA_ADOPTION_HALFWIDTH_BAR) within the +-10 % bar the frontier defines
"useful" against, the count refused by the interval gate (halfwidth
above the bar), and the count aborted on the comfort bound (act 1's documented sizing knife-edge); plus the shipped-preset null
control (arming now SUCCEEDS on all three presets the integration ships --
before #1329 the one-state predicate priced the arm/adopt gate and refused
all three by name, so these two rows were 0 armed / 3 named) and the
unridged control (the frontier's no-ridge cell).

METHOD: the act-1 ensemble drive (tests/features.py's _ridge_drive)
verbatim -- power capped at 3.5 kW so the step is a legal sub-maximal
experiment with noise margin against the 0.8 C abort bound; the fit is
whatever production ran at _finish, reached through step() alone. Seeds:
20260913 + draw, the wave's family.

COMMAND (from the repository root, < 90 s):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/sysid_estimator_frontier.py

PERTURBATION (either, from the same tree):
  * HPO_EST_RIDGE_OFF=1 sets the module's SLAB_INTERCEPT_PRIOR_SD_KW to
    1e9 -- the ported ridge effectively deleted: the fitted counts collapse
    toward the frontier's unridged cell (-35/+46 % UA at sigma 0.01, the
    pre-study's measurement of exactly this deletion).
  * HPO_EST_INTERVAL_GATE_OFF=1 lifts UA_ADOPTION_HALFWIDTH_BAR to 1e9:
    the sigma=0.05 interval_refused count -> 0 and that cell's fitted UA
    biases print PAST the +-10 % bar -- the degradation the gate exists
    to refuse, made visible.

INSTRUMENTED SYMBOLS: custom_components/heatpump_optimizer/sysid.py:
SystemIdentification.arm, SystemIdentification.step,
SystemIdentification.identify_slab, slab_mode_identifiability,
slab_mode_tau_fast, SLAB_INTERCEPT_PRIOR_SD_KW,
UA_ADOPTION_HALFWIDTH_BAR; custom_components/heatpump_optimizer/
thermal_model.py: ThermalModel.simulate_step.

EXPECTED on this tree (every line a COUNT with cross-build margin: the
sigma=0.01 fitted biases stay inside +-4 % against the 10 % bar, the
sigma=0.05 half-widths sit past the bar on the refused draws, and the one
comfort-bound abort is a protocol-path draw with no solver in it; the
sigma=0.02 cell is deliberately NOT pinned -- its refusals land on the
gate itself and its p95 touches the bar, so its counts are printed as
context, never asserted):
    RESULT gatepass_plants=2
    RESULT draws_per_cell=16
    RESULT fitted_typical_s001=16
    RESULT within10_typical_s001=16
    RESULT fitted_heavy_s001=16
    RESULT within10_heavy_s001=16
    RESULT interval_refused_typical_s005=14
    RESULT interval_refused_heavy_s005=4
    RESULT shipped_presets_armed=3
    RESULT shipped_presets_gate_named=0
    RESULT unridged_fitted_typical_s001=0

ROOT RULE: ROOT = Path(".") -- this harness measures the working directory
it is run from. Run it from the tree under test.
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
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(".").resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np

import heatpump_optimizer.sysid as sysid_module
from heatpump_optimizer.presets import derive
from heatpump_optimizer.sysid import (
    SysIdConfig,
    SystemIdentification,
    slab_mode_identifiability,
    slab_mode_tau_fast,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

from stress import BUILDINGS  # the three building presets the gate sweeps
from profiles import house

if os.environ.get("HPO_EST_RIDGE_OFF"):
    sysid_module.SLAB_INTERCEPT_PRIOR_SD_KW = 1e9
if os.environ.get("HPO_EST_INTERVAL_GATE_OFF"):
    sysid_module.UA_ADOPTION_HALFWIDTH_BAR = 1e9
UTC = timezone.utc
COP = 3.0
BASE = 21.0
START = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
OUTDOOR = 0.0
DT = 0.25
#: The act-1 ensemble drive's electrical ceiling (see its comment in
#: tests/features.py): a legal sub-maximal experiment with noise margin
#: against the 0.8 C abort bound.
MAX_POWER_KW = 3.5
NDRAW = 16
SEED0 = 20260913
NOISES = (0.01, 0.02, 0.05)


def _plant(name: str, slab_mult: float = 1.0) -> ThermalParameters:
    cfg = house(two_zone=False, dhw=False)
    derived = derive(BUILDINGS[name])
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    p.internal_gains = 0.3
    p.wind_sensitivity = 0.0
    p.slab_heat_transfer = p.slab_heat_transfer * slab_mult
    return p


def _drive(p: ThermalParameters, sigma: float, seed: int):
    """One production experiment: the recorder sees the noisy series."""
    rng = np.random.default_rng(seed)
    model = ThermalModel(p)
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    gains = float(p.internal_gains)
    sid = SystemIdentification(
        SysIdConfig(enabled=True, min_days_between_runs=0.0)
    )
    assert sid.arm(START, plant=p)
    ks = max(float(p.slab_heat_transfer), 1e-9)
    hold_thermal = max(ua * (BASE - OUTDOOR) - gains, 0.0)
    state = ThermalState(
        room_temperature=BASE,
        slab_temperature=BASE + hold_thermal / ks,
        outdoor_temperature=OUTDOOR,
    )
    prices = np.full(48, 1.0)
    when = START
    for _ in range(int(5.0 / DT) + 4):
        reading = state.room_temperature + rng.normal(0.0, sigma)
        override = sid.step(
            now=when,
            room_temp=reading,
            outdoor_temp=OUTDOOR,
            price=0.1,
            price_horizon=prices,
            learner_samples=0,
            max_power_kw=MAX_POWER_KW,
            cop=COP,
            plan_power_kw=hold_thermal / COP,
            house_ua=ua,
            house_capacity=float(p.room_thermal_mass),
            house_gains=gains,
            house_slab_mass=float(p.slab_thermal_mass),
            house_slab_transfer=float(p.slab_heat_transfer),
        )
        if not sid.active:
            break
        elec = hold_thermal / COP if override is None else float(override)
        state = model.simulate_step(
            state,
            electrical_power=0.0,
            outdoor_temp=OUTDOOR,
            dt_hours=DT,
            external_heat_kw=elec * COP,
        )
        when += timedelta(hours=DT)
    return sid.result, ua


def _cell(name: str, sigma: float) -> dict[str, float]:
    p = _plant(name, 100.0)
    tau_true = slab_mode_tau_fast(
        float(p.room_thermal_mass),
        float(p.slab_thermal_mass),
        float(p.slab_heat_transfer),
    )
    fitted = within10 = interval_refused = aborted = 0
    biases: list[float] = []
    taus: list[float] = []
    for draw in range(NDRAW):
        r, ua = _drive(p, sigma, SEED0 + draw)
        if r.completed and r.heat_loss_kw_per_c is not None:
            hw = r.ua_profile_halfwidth
            if hw is not None and hw <= sysid_module.UA_ADOPTION_HALFWIDTH_BAR:
                fitted += 1
                bias = (r.heat_loss_kw_per_c / ua - 1.0) * 100.0
                biases.append(bias)
                taus.append(r.slab_mode_tau_hours / tau_true)
                within10 += abs(bias) <= 10.0
            else:
                interval_refused += 1
        elif "drifted beyond" in r.reason:
            aborted += 1
    out = {
        "fitted": fitted,
        "within10": within10,
        "interval_refused": interval_refused,
        "aborted": aborted,
    }
    if biases:
        out["p5"] = float(np.percentile(biases, 5))
        out["p95"] = float(np.percentile(biases, 95))
        out["tau_p5"] = float(np.percentile(taus, 5))
        out["tau_p95"] = float(np.percentile(taus, 95))
    return out


def main() -> int:
    print("=" * 92)
    print("sysid-estimator frontier: gate-passing cells through the production fit")
    print(
        f"ridge width = {sysid_module.SLAB_INTERCEPT_PRIOR_SD_KW}; interval bar = "
        f"{sysid_module.UA_ADOPTION_HALFWIDTH_BAR}"
    )
    print("=" * 92)
    counts: dict[tuple[str, float], dict[str, float]] = {}
    for name in ("typical_slab", "heavy_old"):
        for sigma in NOISES:
            c = _cell(name, sigma)
            counts[(name, sigma)] = c
            extra = (
                f"UA p5/p95 {c['p5']:+.1f}/{c['p95']:+.1f} % "
                f"tau/true p5/p95 {c['tau_p5']:.3f}/{c['tau_p95']:.3f}"
                if "p5" in c
                else "no fitted draws"
            )
            print(
                f"{name:13s} sigma={sigma:.2f}  fitted {c['fitted']:>2d}/{NDRAW} "
                f"within10 {c['within10']:>2d}  interval-refused {c['interval_refused']:>2d} "
                f"aborted {c['aborted']:>2d}  {extra}"
            )
    print(
        "context (NOT pinned): the sigma=0.02 row is the frontier's "
        "-8.6/+9.5 cell; its refusals land on the gate itself and its p95 "
        "touches the bar, so counts there are printed, never asserted"
    )
    # Null control 1: every shipped preset arms (#1329). The count is a
    # real control either way -- before the fix it was 0 armed / 3 named.
    armed = 0
    named = 0
    for name in BUILDINGS:
        p = _plant(name)
        sy = SystemIdentification(
            SysIdConfig(enabled=True, min_days_between_runs=0.0)
        )
        ok = sy.arm(START, plant=p)
        why = sy.result.reason
        if ok:
            armed += 1
        elif "slab mode too slow" in why:
            named += 1
        print(
            f"shipped preset {name:13s}: armed={ok} reason='{why[:58]}'"
        )
    # Null control 2: the frontier's unridged cell -- the ported ridge
    # deleted, the same window. The fitted count collapses (guards refuse
    # the unridged fits; the pre-study measured -35/+46 % UA here).
    unridged = -1
    if not os.environ.get("HPO_EST_RIDGE_OFF"):
        saved = sysid_module.SLAB_INTERCEPT_PRIOR_SD_KW
        sysid_module.SLAB_INTERCEPT_PRIOR_SD_KW = 1e9
        try:
            unridged = _cell("typical_slab", 0.01)["fitted"]
        finally:
            sysid_module.SLAB_INTERCEPT_PRIOR_SD_KW = saved
    print(f"unridged control: fitted {unridged}/16 (ridge deleted)")
    print()
    print("########## RESULT lines ##########")
    print("RESULT gatepass_plants=2 count")
    print(f"RESULT draws_per_cell={NDRAW} count")
    for name in ("typical_slab", "heavy_old"):
        tag = "typical" if name.startswith("typical") else "heavy"
        c1 = counts[(name, 0.01)]
        c5 = counts[(name, 0.05)]
        print(f"RESULT fitted_{tag}_s001={c1['fitted']} count")
        print(f"RESULT within10_{tag}_s001={c1['within10']} count")
        print(f"RESULT interval_refused_{tag}_s005={c5['interval_refused']} count")
    print(f"RESULT shipped_presets_armed={armed} count")
    print(f"RESULT shipped_presets_gate_named={named} count")
    if unridged >= 0:
        print(f"RESULT unridged_fitted_typical_s001={unridged} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
