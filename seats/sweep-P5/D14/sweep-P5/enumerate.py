"""Round 11 class sweep P5: every told quantity of the sysid fit against the
adoption interval that gates it.

Class P5: "a sysid/adoption gate keyed on a quantity other than the bias it
gates". Seam rule (D2-s3-10's grep of the width chain and D7-s2-02's
told-quantity sweep, widened to the whole step() surface): every argument of
``SystemIdentification.step`` and every field of ``HousePlant`` is a quantity
the fit is TOLD. Each is a seam. The enumerator reads that surface by
``inspect`` (nothing listed by hand), injects one realistic misstatement per
seam (the true plant or reading differs from what step is told), runs the
production night (arm/step/_finish -> identify_slab) and the coordinator's one
gate ``adoption_decision``, and counts nights ADMITTED with |UA bias| above
the gate's own bar (log 1.10 -> 10 %), and admitted nights whose error lies
outside the half-width the gate admitted them on (the 95 % interval's misses,
D2-s3-10's miss_rate; flagged at >= 2 misses and a rate above 0.05).

A seam with an injector and biased_admitted > 0 is flagged; one with no
injector is printed as `unprobed` with the reason (it does not enter the heat
balance). Drive: D7-s2's m2_sysid_plant protocol (tests/stress.py BUILDINGS via
presets.derive, production ThermalModel, 15 substeps per tick), extended with
the injectors.

Usage: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/sweep-P5/enumerate.py [--null | --perturb] [--json PATH]
  --null     every injector at zero (the told plant is the true one): 0 flagged
  --perturb  one-line re-introduction: sysid.SLAB_INTERCEPT_PRIOR_SD_KW 0.1 -> 0.01
             (the free-heat width the interval prices all but removed, the
             pre-R9-P5 shape): biased_admitted_total and misses_total must rise.
             (Narrowing SLAB_PAIR_PRIOR_LOG_SD instead LOWERS admissions -- the
             same width also ridges the fit -- so it is not a clean perturbation.)
"""
from __future__ import annotations

import inspect
import json
import os
import sys
import time
from dataclasses import fields, replace
from datetime import timedelta
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
ROOT = Path(__file__).resolve().parents[6]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "dev/audit/rounds/round11/D7/s2")]
import numpy as np  # noqa: E402
import m2_sysid_plant as M  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalState  # noqa: E402

NULL = "--null" in sys.argv
if "--perturb" in sys.argv:
    S.SLAB_INTERCEPT_PRIOR_SD_KW = 0.01

BAR = float(np.expm1(S.UA_ADOPTION_HALFWIDTH_BAR))

# seam -> (injection dict, label). One realistic misstatement each.
INJECT = {
    "room_temp": [({"noise": 0.005}, "white 0.005 C (D2-s3-10)"), ({"noise": 0.01}, "white 0.01 C (D2-s3-10)"),
                  ({"noise": 0.02}, "white 0.02 C (D2-s3-10)"), ({"quant": 0.1}, "quantised 0.1 C (D2-s3-10)")],
    "outdoor_temp": [({"outdoor_bias": 1.5}, "sensor +1.5 K")],
    "cop": [({"cop_true": 1.15}, "true COP x1.15 of told")],
    "plan_power_kw": [({"deliver": 0.9}, "pump delivers 0.9 of the told hold")],
    "house.ua": [({"ua": 1.3}, "declared UA x1.3 of true")],
    "house.capacity": [({"capacity": 2.0}, "true room capacity x2")],
    "house.gains": [({"gains": 0.8}, "free heat +0.8 kW (D7-s2-02)")],
    "house.slab_mass": [({"slab_mass": 2.0}, "true slab mass x2")],
    "house.slab_transfer": [({"slab_transfer": 2.0}, "true slab transfer x2")],
}
NOT_PHYSICAL = {
    "self": "the instance", "now": "clock", "price": "scheduling only (when to run the test night)",
    "price_horizon": "scheduling only", "learner_samples": "arming precondition (sample count)",
    "max_power_kw": "bounds the test override; told equals the plant's own limit",
    "house": "expanded into its HousePlant fields",
}
SEEDS = tuple(range(1, 13))


def surface() -> list[str]:
    names = list(inspect.signature(S.SystemIdentification.step).parameters)
    return names + [f"house.{f.name}" for f in fields(S.HousePlant)]


def drive(declared, true, inj, seed):
    rng = np.random.default_rng(seed)
    model = ThermalModel(true)
    ua_true = true.heat_loss_coefficient * true.house_heat_loss_scale
    gains_true = float(true.internal_gains)
    ua_decl = declared.heat_loss_coefficient * declared.house_heat_loss_scale * inj.get("ua", 1.0)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0))
    if not sid.arm(M.NOW, plant=declared):
        return None, ua_true
    outdoor = 0.0
    ks = max(float(true.slab_heat_transfer), 1e-9)
    hold = max(ua_true * (21.0 - outdoor) - gains_true, 0.0)
    state = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / ks, outdoor_temperature=outdoor)
    prices = np.full(48, 1.0)
    when, dt_h, cop = M.NOW, 0.25, M.COP
    cop_true = cop * inj.get("cop_true", 1.0)
    for _ in range(int(5.0 / dt_h) + 4):
        reading = state.room_temperature + (rng.normal(0.0, inj["noise"]) if inj.get("noise") else 0.0)
        if inj.get("quant"):
            q = inj["quant"]
            reading = round(reading / q) * q
        override = sid.step(
            now=when, room_temp=reading, outdoor_temp=outdoor + inj.get("outdoor_bias", 0.0), price=0.1,
            price_horizon=prices, learner_samples=0, max_power_kw=M.MAX_KW, cop=cop,
            plan_power_kw=hold / cop_true,
            house=S.HousePlant(ua=ua_decl, capacity=float(declared.room_thermal_mass),
                               gains=float(declared.internal_gains),
                               slab_mass=float(declared.slab_thermal_mass),
                               slab_transfer=float(declared.slab_heat_transfer)),
        )
        if not sid.active:
            break
        elec = hold / cop_true if override is None else float(override)
        elec *= inj.get("deliver", 1.0) if override is None else 1.0
        for _ in range(15):
            state = model.simulate_step(state, electrical_power=0.0, outdoor_temp=outdoor,
                                        dt_hours=dt_h / 15, external_heat_kw=elec * cop_true)
        when += timedelta(hours=dt_h)
    return sid.result, ua_true


def run_cell(name, inj, seed):
    declared = M.plant(name)
    true = replace(declared)
    true.slab_thermal_mass = declared.slab_thermal_mass * inj.get("slab_mass", 1.0)
    true.slab_heat_transfer = declared.slab_heat_transfer * inj.get("slab_transfer", 1.0)
    true.room_thermal_mass = declared.room_thermal_mass * inj.get("capacity", 1.0)
    true.internal_gains = max(0.0, declared.internal_gains + inj.get("gains", 0.0))
    res, ua_true = drive(declared, true, inj, seed)
    if res is None or not res.completed or res.heat_loss_kw_per_c is None:
        return None, False, None
    d = S.adoption_decision(res, declared, S.SysIdConfig(enabled=True))
    # the half-width the gate admitted on: weight = 1 - hw / bar (adoption_decision)
    hw = (1.0 - d.weight) * S.UA_ADOPTION_HALFWIDTH_BAR if d.admit else None
    return res.heat_loss_kw_per_c / ua_true - 1.0, bool(d.admit), hw


def main() -> int:
    t0 = time.process_time()
    rows, flagged = {}, 0
    for seam in surface():
        if seam not in INJECT:
            print(f"--  {seam:20s} unprobed: {NOT_PHYSICAL.get(seam, 'NO INJECTOR')}")
            rows[seam] = {"probed": False, "reason": NOT_PHYSICAL.get(seam, "NO INJECTOR")}
            continue
        out = []
        for inj, label in INJECT[seam]:
            inj = {} if NULL else inj
            stochastic = any(k in inj for k in ("noise",))
            cells = adm = bad = miss = 0
            worst = 0.0
            for name in M.BUILDINGS:
                for seed in (SEEDS if stochastic else (0,)):
                    b, a, hw = run_cell(name, inj, seed)
                    cells += 1
                    adm += a
                    if a and b is not None and abs(np.log1p(b)) > hw:
                        miss += 1
                    if a and b is not None and abs(b) > BAR:
                        bad += 1
                        worst = max(worst, abs(b))
            # flagged: an admitted night past the bar, or the interval under-covering
            # its own 95 % claim (at least 2 misses and a miss rate above 0.05)
            under = miss >= 2 and miss > 0.05 * adm
            out.append({"inject": label, "cells": cells, "admitted": adm, "biased_admitted": bad,
                        "interval_misses": miss, "worst_admitted_bias": round(worst, 4),
                        "flagged": bool(bad or under)})
            print(f"{'P5' if (bad or under) else 'ok'}  {seam:20s} {label:40s} cells={cells} admitted={adm} "
                  f"biased_admitted={bad} misses={miss} worst={worst:.4f}", flush=True)
        hit = any(o["flagged"] for o in out)
        flagged += hit
        rows[seam] = {"probed": True, "flagged": hit, "arms": out}
    tot_bad = sum(o["biased_admitted"] for r in rows.values() if r["probed"] for o in r["arms"])
    tot_miss = sum(o["interval_misses"] for r in rows.values() if r["probed"] for o in r["arms"])
    tag = "null" if NULL else "perturb" if "--perturb" in sys.argv else "tree"
    print(f"RESULT {tag} seams={len(rows)} probed={sum(r['probed'] for r in rows.values())} flagged={flagged} "
          f"biased_admitted_total={tot_bad} misses_total={tot_miss} "
          f"cpu={time.process_time() - t0:.0f}s")
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(rows, indent=1) + "\n")
    return 1 if NULL and flagged else 0


if __name__ == "__main__":
    sys.exit(main())
