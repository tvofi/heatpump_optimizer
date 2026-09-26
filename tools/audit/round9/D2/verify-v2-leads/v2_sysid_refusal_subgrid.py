"""Verifier V2 (independent) check on D2-s4-81.

Metric (own): same admit-bit definition as the finder (production sysid.adoption_decision on an
exact, noise-free zero-bias fit), but on an independently chosen 8-cell subgrid (2 structures x
2 eras x 2 emitters, fixed pump 4.0 kW -- a value the finder did not test) rather than the full
80-cell grid, to check the phenomenon is not an artefact of the finder's own grid choice.

Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python \
  tools/audit/round9/D2/verify-v2-leads/v2_sysid_refusal_subgrid.py [--perturb]
Instrumented symbol: heatpump_optimizer.sysid:SystemIdentification.arm/step/_finish,
  sysid:adoption_decision, sysid:slab_ua_adoption_halfwidth.
Perturbation (--perturb): sysid.UA_ADOPTION_HALFWIDTH_BAR ln(1.10) -> ln(1.20) in memory.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import copy
import sys
import time
from datetime import UTC, datetime, timedelta
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from profiles import house  # noqa: E402
from heatpump_optimizer import presets as P  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

NOW = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
COP = 3.0
PERTURB = "--perturb" in sys.argv
if PERTURB:
    S.UA_ADOPTION_HALFWIDTH_BAR = float(np.log(1.20))

STRUCTS = [P.STRUCTURE_TIMBER_SLAB, P.STRUCTURE_MASONRY]
ERAS = [P.ERA_1960_1980, P.ERA_LOW_ENERGY]
EMITTERS = [P.EMITTER_FLOOR, P.EMITTER_RADIATORS]
KW = 4.0


def plant(structure, era, emitter):
    cfg = house(two_zone=False, dhw=False)
    d = P.derive(P.BuildingPreset(structure=structure, era=era, heated_area_m2=120,
                                  lower_emitter=emitter))
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    return p


def drive(true_p, max_kw):
    decl = copy.deepcopy(true_p)
    plant_p = copy.deepcopy(true_p)
    model = ThermalModel(plant_p)
    ua_true = float(plant_p.heat_loss_coefficient * plant_p.house_heat_loss_scale)
    g_true = float(plant_p.internal_gains)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0,
                                               gains_prior_kw=float(decl.internal_gains)))
    if not sid.arm(NOW, plant=decl):
        return {"armed": False, "why": sid.result.reason}
    outdoor = 0.0
    ks = max(float(plant_p.slab_heat_transfer), 1e-9)
    hold = max(ua_true * (21.0 - outdoor) - g_true, 0.0)
    state = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / ks,
                         outdoor_temperature=outdoor)
    prices = np.full(48, 1.0)
    when, dt_h = NOW, 0.25
    for _ in range(int(8.0 / dt_h)):
        override = sid.step(
            now=when, room_temp=state.room_temperature, outdoor_temp=outdoor, price=0.1,
            price_horizon=prices, learner_samples=0, max_power_kw=max_kw, cop=COP,
            plan_power_kw=hold / COP, house_ua=ua_true,
            house_capacity=float(decl.room_thermal_mass), house_gains=float(decl.internal_gains),
            house_slab_mass=float(decl.slab_thermal_mass),
            house_slab_transfer=float(decl.slab_heat_transfer),
        )
        if not sid.active:
            break
        elec = hold / COP if override is None else float(override)
        state = model.simulate_step(state, electrical_power=0.0, outdoor_temp=outdoor,
                                    dt_hours=dt_h, external_heat_kw=elec * COP)
        when += timedelta(hours=dt_h)
    res = sid.result
    out = {"armed": True, "completed": bool(res.completed), "why": res.reason, "admit": False}
    if res.completed and res.heat_loss_kw_per_c is not None:
        dec = S.adoption_decision(res, decl, sid.config)
        out.update(admit=bool(dec.admit), why=dec.reason)
    return out


t0, th0 = time.process_time(), time.thread_time()
refused = admitted = aborted = 0
for st in STRUCTS:
    for era in ERAS:
        for em in EMITTERS:
            r = drive(plant(st, era, em), KW)
            if not r["armed"]:
                kind = "unarmed"
            elif not r["completed"]:
                aborted += 1
                kind = "aborted"
            elif r["admit"]:
                admitted += 1
                kind = "admitted"
            else:
                refused += 1
                kind = "REFUSED"
            print(f"CELL {st}|{era}|{em}|{KW}kW {kind} why={r['why']}")

print(f"RESULT cells={len(STRUCTS)*len(ERAS)*len(EMITTERS)} count")
print(f"RESULT refused={refused} count")
print(f"RESULT admitted={admitted} count")
print(f"RESULT aborted={aborted} count")
print(f"RESULT perturbed={int(PERTURB)}")
print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
