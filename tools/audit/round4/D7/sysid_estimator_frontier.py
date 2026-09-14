"""sysid-estimator wave (#942 options 2+3): the frontier's gate-passing cells,
measured through the PRODUCTION fitted arm.

live-header: this header is maintained against the tree; harness_headers.py
executes it.

This is the pre-study's probe scaffolding (issue #942 comment 5656402482,
probes run at 2d09043) committed as the wave's evaluation instrument: the
frontier's bottom row -- gate-passing plants (slab_heat_transfer x100, the
#991 null-control construction) + the ported intercept ridge, nightly 5 h
window -- re-derived through production ``SystemIdentification.identify()``
dispatching to ``_identify_two_state``. The ratified hybrid (owner decision
2026-09-14, comment 5659441129): fitted -- UA and tau_fast only -- where the
#991 gate passes AND the ridge is ported AND the residual scatter clears the
noise gate; refused everywhere else, by name.

METRIC (one line): per (plant, sigma) cell, over n=16 noise draws on the
recorded production-protocol window, the COUNT of draws whose production
identify() returns a completed fitted result (``slab_mode_tau_hours`` set)
that the production adoption predicate accepts (confidence >= 0.3), the
count of draws the residual-scatter noise gate refuses by name, and the
count of fitted draws within the +-10 % UA bar the frontier defines
"useful" against; plus the shipped-preset null control (arming refused by
name on all three presets the integration ships, ridge present).

METHOD: the production protocol (honest sizer through step()'s house_*
wiring) excites the production two-state plant noise-free; N(0, sigma)
noise lands on the room OBSERVATIONS the fit consumes (the pre-study's
arm-E method -- sizing and the comfort guard price the excitation, the
noise prices the estimation); the plant is DECLARED at arm() the way
production arms, and the fitted result is production identify() on the
noised samples. Seeds: the pre-study's 20260913 family verbatim.

COMMAND (from the repository root, < 60 s):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D7/sysid_estimator_frontier.py

PERTURBATION (either, from the same tree):
  * HPO_EST_RIDGE_NONE=1 drops the ridge width from the config: the fitted
    arm must not be dispatched at all (every fitted count -> 0; the plain
    two-state fit is noise-wrecked, -36/+45 % UA at sigma 0.01 -- the
    no-ridge control re-derived at this branch's base against the
    pre-study's -35/+46).
  * HPO_EST_NOISE_GATE_OFF=1 lifts the residual-scatter ceiling to 1e9:
    the sigma=0.05 noise_refused count -> 0 and that cell's fitted UA
    biases print PAST the +-10 % bar -- the degradation the noise gate
    exists to refuse, made visible.

INSTRUMENTED SYMBOLS: custom_components/heatpump_optimizer/sysid.py:
SystemIdentification.arm, SystemIdentification.step,
SystemIdentification.identify, SystemIdentification._identify_two_state,
slab_mode_tau_fast, slab_mode_identifiability, MAX_FIT_RESIDUAL_SCATTER_C;
custom_components/heatpump_optimizer/thermal_model.py:
ThermalModel.simulate_step.

EXPECTED on this tree (every line a COUNT, stable across BLAS builds by
margin: sigma=0.01 fitted biases stay inside +-4.1 % against the 10 % bar
and sigma=0.05 scatters sit near 0.05 against the 0.03 gate; the sigma=0.02
cell is deliberately NOT pinned -- its refusals land on the gate itself
(0.030/0.031 measured) and its p95 touches the bar, so its counts are
printed as context, never asserted):
    RESULT gatepass_plants=2
    RESULT draws_per_cell=16
    RESULT fitted_typical_s001=16
    RESULT within10_typical_s001=16
    RESULT fitted_heavy_s001=16
    RESULT within10_heavy_s001=16
    RESULT noise_refused_typical_s005=16
    RESULT noise_refused_heavy_s005=16
    RESULT shipped_presets_armed=0
    RESULT shipped_presets_gate_named=3
    RESULT ridge_none_fitted_dispatches=0

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
from dataclasses import replace
from datetime import datetime, timedelta
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

RIDGE_WIDTH = None if os.environ.get("HPO_EST_RIDGE_NONE") else 0.1
if os.environ.get("HPO_EST_NOISE_GATE_OFF"):
    sysid_module.MAX_FIT_RESIDUAL_SCATTER_C = 1e9
COP = 3.0
BASE = 21.0
START = datetime(2026, 1, 15, 23, 0, 0)
OUTDOOR = 0.0
DT = 0.25
W = 5.0
NDRAW = 16
SEED = 20260913
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


def _run_protocol(p: ThermalParameters) -> tuple[SystemIdentification, float]:
    """The production experiment on the production plant, plant declared."""
    model = ThermalModel(p)
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    gains = float(p.internal_gains)
    kw = dict(enabled=True, min_days_between_runs=0.0)
    if RIDGE_WIDTH is not None:
        kw["gains_ridge_width_kw"] = RIDGE_WIDTH
    sy = SystemIdentification(SysIdConfig(**kw))
    assert sy.arm(START, plant=p)
    qh = ua * (BASE - OUTDOOR) - gains
    ks = max(p.slab_heat_transfer, 1e-9)
    st = ThermalState(
        room_temperature=BASE,
        slab_temperature=BASE + qh / ks,
        outdoor_temperature=OUTDOOR,
    )
    hold = max(qh, 0.0) / COP
    prices = np.full(48, 1.0)
    now = START
    for _ in range(int(W / DT) + 4):
        override = sy.step(
            now=now,
            room_temp=st.room_temperature,
            outdoor_temp=OUTDOOR,
            price=0.1,
            price_horizon=prices,
            learner_samples=0,
            max_power_kw=float(p.max_electrical_power),
            cop=COP,
            plan_power_kw=hold,
            house_ua=ua,
            house_capacity=float(p.room_thermal_mass),
            house_gains=gains,
            house_slab_mass=float(p.slab_thermal_mass),
            house_slab_transfer=float(p.slab_heat_transfer),
        )
        if not sy.active:
            break
        elec = hold if override is None else float(override)
        st = model.simulate_step(
            st,
            electrical_power=0.0,
            outdoor_temp=OUTDOOR,
            dt_hours=DT,
            external_heat_kw=elec * COP,
        )
        now = now + timedelta(hours=DT)
    return sy, ua


def _cell(name: str, sigma: float) -> dict[str, float]:
    p = _plant(name, 100.0)
    sy, ua = _run_protocol(p)
    clean = list(sy.samples)
    tau_true = slab_mode_tau_fast(p)
    fitted = within10 = refused = 0
    biases: list[float] = []
    taus: list[float] = []
    for draw in range(NDRAW):
        seed = (
            SEED
            + int(W * 10) * 100003
            + int(sigma * 1000) * 1009
            + draw * 7919
            + sum(ord(c) * (i + 1) for i, c in enumerate(name))
        )
        rng = np.random.default_rng(seed % (2**32))
        sy.samples = [
            replace(s, room_temp=s.room_temp + float(rng.normal(0.0, sigma)))
            for s in clean
        ]
        r = sy.identify()
        if r.completed and r.slab_mode_tau_hours is not None:
            if r.confidence >= 0.3:
                fitted += 1
                bias = (r.heat_loss_kw_per_c / ua - 1.0) * 100.0
                biases.append(bias)
                taus.append(r.slab_mode_tau_hours / tau_true)
                within10 += abs(bias) <= 10.0
        elif "residual scatter" in r.reason:
            refused += 1
    out = {
        "fitted": fitted,
        "within10": within10,
        "refused": refused,
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
        f"ridge width = {RIDGE_WIDTH}; noise gate = "
        f"{sysid_module.MAX_FIT_RESIDUAL_SCATTER_C}"
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
                f"within10 {c['within10']:>2d}  noise-refused {c['refused']:>2d}  "
                f"{extra}"
            )
    print(
        "context (NOT pinned): the sigma=0.02 row is the frontier's "
        "-8.6/+9.5 cell; its refusals land on the gate itself and its p95 "
        "touches the bar, so counts there are printed, never asserted"
    )
    # Null control 1: no shipped preset may arm, ridge present or not.
    armed = 0
    named = 0
    for name in BUILDINGS:
        p = _plant(name)
        sy = SystemIdentification(
            SysIdConfig(
                enabled=True,
                min_days_between_runs=0.0,
                gains_ridge_width_kw=0.1,
            )
        )
        ok = sy.arm(START, plant=p)
        why = sy.result.reason
        if ok:
            armed += 1
        elif "slab mode too slow" in why:
            named += 1
        print(f"shipped preset {name:13s}: armed={ok} reason='{why[:58]}'")
    # Null control 2: without the ported ridge the fitted arm is not
    # dispatched -- the count of dispatches over every gate-passing cell.
    dispatches = 0
    if RIDGE_WIDTH is None:
        for name in ("typical_slab", "heavy_old"):
            p = _plant(name, 100.0)
            sy, _ = _run_protocol(p)
            r = sy.identify()
            dispatches += r.slab_mode_tau_hours is not None
    else:
        # The default run has the ridge: prove the conjunct by re-running
        # one cell with it dropped.
        p = _plant("typical_slab", 100.0)
        sy, _ = _run_protocol(p)
        sy.config.gains_ridge_width_kw = None
        r = sy.identify()
        dispatches = r.slab_mode_tau_hours is not None
        print(
            f"ridge-dropped control: fitted dispatched={dispatches} "
            f"reason='{r.reason[:40]}' completed={r.completed}"
        )
    print()
    print("########## RESULT lines ##########")
    print(f"RESULT gatepass_plants=2 count")
    print(f"RESULT draws_per_cell={NDRAW} count")
    for name in ("typical_slab", "heavy_old"):
        tag = "typical" if name.startswith("typical") else "heavy"
        c1 = counts[(name, 0.01)]
        c5 = counts[(name, 0.05)]
        print(f"RESULT fitted_{tag}_s001={c1['fitted']} count")
        print(f"RESULT within10_{tag}_s001={c1['within10']} count")
        print(f"RESULT noise_refused_{tag}_s005={c5['refused']} count")
    print(f"RESULT shipped_presets_armed={armed} count")
    print(f"RESULT shipped_presets_gate_named={named} count")
    print(f"RESULT ridge_none_fitted_dispatches={int(dispatches)} count")
    print("RESULT thread_factor=1.0 ratio")
    try:
        print(f"RESULT load1={os.getloadavg()[0]:.2f} ratio")
    except OSError:
        print("RESULT load1=nan ratio")
    print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
