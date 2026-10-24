"""L4 lead (raised by D14-s3) for D2-s4 / D2.M5 -- the sysid gate refuses an exact, noise-free fit.

Metric (one line): null_refused = building cells whose production step experiment, run on a plant
  EXACTLY equal to the declared one with a noise-free room reading, completes and is then refused by
  sysid.adoption_decision; "never_adoptable" = the same cells, since zero bias is the best case.
  Count key: the admit bit adoption_decision returns for the fit the production experiment delivers.
Grid: every BuildingPreset structure (4) x era (5) x lower emitter (2) at 120 m2, derived through
  presets.derive onto tests/profiles.house (single zone, no DHW), x pump max power {3.5, 6.0} kW
  = 80 cells. Drive (arm -> step at 0.25 h -> _finish) transcribed from D14-s3's
  tools/audit/round9/D14/s3/p5_gate.py:drive, zero-bias arm only.
Run:  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D2/leads/l4_sysid_null_refusal.py [--perturb]
Perturbation (--perturb): sysid.UA_ADOPTION_HALFWIDTH_BAR ln(1.10) -> ln(1.20) in memory.
  Expected: null_refused down.
Null control: the same drive's admitted cells (a zero-bias fit the gate does admit), printed.
Expected: null_refused=19, null_admitted=37, null_aborted=24 of 80; --perturb null_refused=2. Exact.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box: 4-vCPU Linux container.
Instrumented: sysid:SystemIdentification.arm/step/_finish, sysid:adoption_decision,
  sysid:slab_ua_adoption_halfwidth.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
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
STRUCTS = [P.STRUCTURE_TIMBER_CRAWLSPACE, P.STRUCTURE_TIMBER_SLAB, P.STRUCTURE_CONCRETE_SLAB,
           P.STRUCTURE_MASONRY]
ERAS = [P.ERA_PRE_1960, P.ERA_1960_1980, P.ERA_1980_2005, P.ERA_POST_2005, P.ERA_LOW_ENERGY]
EMITTERS = [P.EMITTER_FLOOR, P.EMITTER_RADIATORS]


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
        out.update(admit=bool(dec.admit), why=dec.reason,
                   hw=S.slab_ua_adoption_halfwidth(res.ua_profile_halfwidth, res.ua_prior_halfwidth),
                   err=float(np.log(res.heat_loss_kw_per_c / ua_true)))
    return out


def main():
    t0, th0 = time.process_time(), time.thread_time()
    refused = admitted = aborted = unarmed = 0
    per_struct = {}
    for st in STRUCTS:
        for era in ERAS:
            for em in EMITTERS:
                for kw in (3.5, 6.0):
                    r = drive(plant(st, era, em), kw)
                    tag = f"{st}|{era}|{em}|{kw}kW"
                    if not r["armed"]:
                        unarmed += 1
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
                        per_struct[st] = per_struct.get(st, 0) + 1
                    hw = r.get("hw")
                    print(f"CELL {tag:48s} {kind:8s} hw={'%.4f' % hw if hw is not None else 'na'} "
                          f"err={'%+.4f' % r['err'] if 'err' in r else 'na'} why={r['why']}", flush=True)
    counts = [per_struct.get(s, 0) for s in STRUCTS]
    print(f"RESULT cells={4 * 5 * 2 * 2} count")
    print(f"RESULT null_refused={refused} count")
    print(f"RESULT null_admitted={admitted} count")
    print(f"RESULT null_aborted={aborted} count")
    print(f"RESULT unarmed={unarmed} count")
    print(f"RESULT null_refused_by_structure={dict(zip(STRUCTS, counts))}")
    print(f"RESULT null_refused_drop_worst_structure={refused - max(counts) if counts else 0} count")
    print(f"RESULT bar={S.UA_ADOPTION_HALFWIDTH_BAR:.4f} log-units perturbed={int(PERTURB)}")
    print(f"RESULT thread_factor={(time.process_time()-t0)/max(time.thread_time()-th0,1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except Exception:
        sw = "n/a"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
