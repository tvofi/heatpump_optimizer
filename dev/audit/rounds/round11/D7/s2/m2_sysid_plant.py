"""D7.M2 (round 11, seat D7-s2): the sysid plant -- step responses of the three shipped presets,
fitted first-order and two-state, each UA bias, and whether the adoption gate admits the fit.

Plants: tests/stress.py BUILDINGS (light_new, heavy_old, typical_slab) via presets.derive on
tests/profiles.house(two_zone=False, dhw=False) -- tests/features.py's _p942 builder.
Protocol: the production state machine (SystemIdentification.arm(plant=declared) / .step),
the house rolled on the production ThermalModel with 15 substeps per 15-min tick
(tests/features.py _ridge_drive). The TRUE plant may differ from the DECLARED one in its slab
pair (mass x m, transfer x t) or its free heat (+dg kW against the declared prior).
Fits: two-state = what production runs (``_finish`` -> ``identify_slab``); first-order = the
retained one-state regression ``SystemIdentification.identify`` on the same samples.
Gate: ``sysid.adoption_decision`` (the coordinator's one adoption gate).

Metric: biased_admitted = number of cells whose two-state fit the adoption gate ADMITS with
|UA bias| > 10 % (the gate's own bar, UA_ADOPTION_HALFWIDTH_BAR = log 1.10). Count key: the
fitted ``SysIdResult.heat_loss_kw_per_c`` the production fit returns, against the TRUE plant's
UA. Also printed per cell: first-order bias and verdict.

Run:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py
       --perturb widens SLAB_INTERCEPT_PRIOR_SD_KW from 0.1 to 0.3 kW (a one-constant
       production edit: the free-heat width the gate prices): biased_admitted must fall.
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692): cells=57, biased_admitted=3
(heavy_old gains+0.8, typical_slab gains+0.5 and +0.8), biased_admitted_first_order=0; counts exact
(the drive is deterministic at sigma 0; the sigma 0.01 cells use fixed seeds).
Machine: box B5 (round-11 finder container), numpy 2.5.4 / scipy 1.18.1, CPython 3.14.
Counts only; any CPU figure printed is provisional.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402

sys.path[:0] = ["tests"]
import numpy as np  # noqa: E402

import harness  # noqa: E402,F401  (puts custom_components on the path)
from heatpump_optimizer import presets  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
from profiles import house as _house  # noqa: E402
from stress import BUILDINGS  # noqa: E402

PERTURB = "--perturb" in sys.argv
if PERTURB:
    S.SLAB_INTERCEPT_PRIOR_SD_KW = 0.3

NOW = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
COP = 3.0
MAX_KW = 3.5
BAR = float(np.expm1(S.UA_ADOPTION_HALFWIDTH_BAR))  # 0.10


def plant(name: str) -> ThermalParameters:
    cfg = _house(two_zone=False, dhw=False)
    derived = presets.derive(BUILDINGS[name])
    derived.pop("heating_response_hours", None)
    cfg.update(derived)
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    return p


def drive(declared: ThermalParameters, true: ThermalParameters, sigma: float, seed: int):
    rng = np.random.default_rng(seed)
    model = ThermalModel(true)
    ua_true = true.heat_loss_coefficient * true.house_heat_loss_scale
    gains_true = float(true.internal_gains)
    ua_decl = declared.heat_loss_coefficient * declared.house_heat_loss_scale
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0))
    if not sid.arm(NOW, plant=declared):
        return sid, None, ua_true
    outdoor = 0.0
    ks = max(float(true.slab_heat_transfer), 1e-9)
    hold = max(ua_true * (21.0 - outdoor) - gains_true, 0.0)
    state = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / ks,
                         outdoor_temperature=outdoor)
    prices = np.full(48, 1.0)
    when = NOW
    dt_h = 0.25
    for _ in range(int(5.0 / dt_h) + 4):
        reading = state.room_temperature + (rng.normal(0.0, sigma) if sigma else 0.0)
        override = sid.step(
            now=when, room_temp=reading, outdoor_temp=outdoor, price=0.1, price_horizon=prices,
            learner_samples=0, max_power_kw=MAX_KW, cop=COP, plan_power_kw=hold / COP,
            house=S.HousePlant(ua=ua_decl, capacity=float(declared.room_thermal_mass),
                               gains=float(declared.internal_gains),
                               slab_mass=float(declared.slab_thermal_mass),
                               slab_transfer=float(declared.slab_heat_transfer)),
        )
        if not sid.active:
            break
        elec = hold / COP if override is None else float(override)
        for _ in range(15):
            state = model.simulate_step(state, electrical_power=0.0, outdoor_temp=outdoor,
                                        dt_hours=dt_h / 15, external_heat_kw=elec * COP)
        when += timedelta(hours=dt_h)
    return sid, sid.result, ua_true


def verdict(result, declared):
    if result is None or not result.completed or result.heat_loss_kw_per_c is None:
        return None, False, (result.reason if result is not None else "not armed")
    d = S.adoption_decision(result, declared, S.SysIdConfig(enabled=True))
    WEIGHT[0] = d.weight
    return result.heat_loss_kw_per_c, d.admit, d.reason


WEIGHT = [0.0]


CELLS = [  # (label, slab mass x, slab transfer x, free-heat offset kW, sigma, seeds)
    ("told", 1.0, 1.0, 0.0, 0.0, (0,)),
    ("mass_x0.5", 0.5, 1.0, 0.0, 0.0, (0,)),
    ("mass_x2", 2.0, 1.0, 0.0, 0.0, (0,)),
    ("ks_x0.5", 1.0, 0.5, 0.0, 0.0, (0,)),
    ("ks_x2", 1.0, 2.0, 0.0, 0.0, (0,)),
    ("gains+0.3", 1.0, 1.0, 0.3, 0.0, (0,)),
    ("gains-0.2", 1.0, 1.0, -0.2, 0.0, (0,)),
    ("gains+0.5", 1.0, 1.0, 0.5, 0.0, (0,)),
    ("gains+0.8", 1.0, 1.0, 0.8, 0.0, (0,)),
    ("mass_x0.33", 1 / 3, 1.0, 0.0, 0.0, (0,)),
    ("mass_x3", 3.0, 1.0, 0.0, 0.0, (0,)),
    ("told_s0.01", 1.0, 1.0, 0.0, 0.01, (1, 2, 3, 4)),
    ("told_s0.02", 1.0, 1.0, 0.0, 0.02, (1, 2, 3, 4)),
]


def main():
    t0 = time.process_time()
    biased_admitted = 0
    rows = 0
    fo_biased_admitted = 0
    tag = "perturb" if PERTURB else "base"
    print(f"# [{tag}] SLAB_INTERCEPT_PRIOR_SD_KW={S.SLAB_INTERCEPT_PRIOR_SD_KW} "
          f"SLAB_PAIR_PRIOR_LOG_SD={S.SLAB_PAIR_PRIOR_LOG_SD}")
    print("preset        cell         seed  2state_bias  admit  | 1order_bias admit | reason(2state)")
    per_preset = {}
    for name in BUILDINGS:
        declared = plant(name)
        for label, m, t, dg, sigma, seeds in CELLS:
            true = replace(declared)
            true.slab_thermal_mass = declared.slab_thermal_mass * m
            true.slab_heat_transfer = declared.slab_heat_transfer * t
            true.internal_gains = max(0.0, declared.internal_gains + dg)
            for seed in seeds:
                sid, res, ua_true = drive(declared, true, sigma, seed)
                ua2, adm2, why2 = verdict(res, declared)
                w2 = WEIGHT[0]
                # the first-order regression on the SAME samples
                fo = sid.identify() if sid.samples else None
                ua1, adm1, why1 = verdict(fo, declared)
                b2 = None if ua2 is None else ua2 / ua_true - 1.0
                b1 = None if ua1 is None else ua1 / ua_true - 1.0
                rows += 1
                bad = bool(adm2 and b2 is not None and abs(b2) > BAR)
                biased_admitted += bad
                fo_biased_admitted += bool(adm1 and b1 is not None and abs(b1) > BAR)
                per_preset.setdefault(name, []).append(b2)
                f2 = "   n/a" if b2 is None else f"{b2:+.4f}"
                f1 = "   n/a" if b1 is None else f"{b1:+.4f}"
                print(f"{name:13s} {label:12s} {seed:4d}  {f2:>10s}  {str(adm2):5s}  | "
                      f"{f1:>10s} {str(adm1):5s} | {why2[:50]} || 1o: {why1[:50]}")
                safe = label.replace(".", "p").replace("+", "p").replace("-", "m")
                if b2 is not None:
                    print(f"RESULT ua_bias_2state_{name}_{safe}_s{seed}={b2:+.4f} ratio admit={adm2} weight={w2:.3f}")
                if bad:
                    print(f"RESULT adopted_scale_shift_{name}_{safe}_s{seed}={w2 * b2:+.4f} ratio")
                if b1 is not None:
                    print(f"RESULT ua_bias_1order_{name}_{safe}_s{seed}={b1:+.4f} ratio admit={adm1}")
    print(f"RESULT cells={rows} count")
    print(f"RESULT biased_admitted={biased_admitted} count")
    print(f"RESULT biased_admitted_first_order={fo_biased_admitted} count")
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    print(f"# cpu {time.process_time() - t0:.1f}s (provisional, not a finding)")


if __name__ == "__main__":
    main()
