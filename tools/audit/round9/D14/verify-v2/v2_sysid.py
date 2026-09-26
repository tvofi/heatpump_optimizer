"""D14 round 9, verifier V2 (independent) for D14-s3-03: sysid admits a UA fit biased by unmodelled free heat.

Metric (one line): v2_admitted_over_bar = sweep cells in which sysid:adoption_decision admits the
production experiment's fit while |ln(UA_fit / UA_true)| > sysid.UA_ADOPTION_HALFWIDTH_BAR;
also reported: the gated half-width at the smallest and the largest injected bias.
This verifier's own plant and bias route: houses from tests/golden.py:coordinator_scenarios
(coord_minimal, coord_dhw thermal params via ThermalParameters.from_config) at outdoor -5 C; the
unmodelled free heat enters the rolled plant as external_heat_kw on top of the heat pump's heat
(the declared internal_gains are untouched), magnitudes 0, 0.15, 0.3, 0.5, 0.8 kW.
Key: result.heat_loss_kw_per_c the production fit returns and the admit bit adoption_decision returns.

Null control: magnitude 0 -> 0 over the bar.
Perturbation (--bar-tight): UA_ADOPTION_HALFWIDTH_BAR / 10 in memory -> admitted over bar to 0.

Run: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D14/verify-v2/v2_sysid.py [--bar-tight]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; 4-core cloud container, CPython 3.14.0rc2.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, copy, logging
from datetime import UTC, datetime, timedelta
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
logging.disable(logging.CRITICAL)
t_proc0, t_thr0 = time.process_time(), time.thread_time()
import numpy as np  # noqa: E402
import golden  # noqa: E402
from heatpump_optimizer import sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

if "--bar-tight" in sys.argv:
    S.UA_ADOPTION_HALFWIDTH_BAR = S.UA_ADOPTION_HALFWIDTH_BAR / 10
NOW = datetime(2026, 2, 10, 22, 0, tzinfo=UTC)
COP, MAX_KW, OUT = 3.2, 4.0, -5.0


def run(p, extra):
    decl = copy.deepcopy(p)
    plant = copy.deepcopy(p)
    model = ThermalModel(plant)
    ua = float(plant.heat_loss_coefficient * plant.house_heat_loss_scale)
    g = float(plant.internal_gains)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0,
                                               gains_prior_kw=float(decl.internal_gains)))
    if not sid.arm(NOW, plant=decl):
        return None
    ks = max(float(plant.slab_heat_transfer), 1e-9)
    hold = max(ua * (21.0 - OUT) - g - extra, 0.0)
    st = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / ks, outdoor_temperature=OUT)
    when = NOW
    for _ in range(48):
        ov = sid.step(now=when, room_temp=st.room_temperature, outdoor_temp=OUT, price=0.1,
                      price_horizon=np.full(48, 1.0), learner_samples=0, max_power_kw=MAX_KW, cop=COP,
                      plan_power_kw=hold / COP, house_ua=ua, house_capacity=float(decl.room_thermal_mass),
                      house_gains=float(decl.internal_gains), house_slab_mass=float(decl.slab_thermal_mass),
                      house_slab_transfer=float(decl.slab_heat_transfer))
        if not sid.active:
            break
        elec = hold / COP if ov is None else float(ov)
        st = model.simulate_step(st, electrical_power=0.0, outdoor_temp=OUT, dt_hours=0.25,
                                 external_heat_kw=elec * COP + extra)
        when += timedelta(hours=0.25)
    r = sid.result
    if not (r.completed and r.heat_loss_kw_per_c is not None):
        return {"completed": False, "reason": r.reason}
    d = S.adoption_decision(r, decl, sid.config)
    hw = S.slab_ua_adoption_halfwidth(r.ua_profile_halfwidth, r.ua_prior_halfwidth)
    return {"completed": True, "admit": bool(d.admit), "err": float(np.log(r.heat_loss_kw_per_c / ua)), "hw": hw}


sc = golden.coordinator_scenarios()
over = null_over = cells = done = 0
worst = 0.0
for hname in ("coord_minimal", "coord_dhw"):
    p = ThermalParameters.from_config(dict(sc[hname]))
    p.two_zone_enabled = False
    for extra in (0.0, 0.15, 0.3, 0.5, 0.8):
        o = run(p, extra)
        cells += 1
        if not o or not o["completed"]:
            print(f"CELL {hname} extra={extra}: not completed {o and o.get('reason')}")
            continue
        done += 1
        bad = o["admit"] and abs(o["err"]) > S.UA_ADOPTION_HALFWIDTH_BAR
        over += bad
        if extra == 0.0:
            null_over += bad
        if o["admit"]:
            worst = max(worst, abs(o["err"]))
        print(f"CELL {hname} extra={extra}: admit={o['admit']} ua_err={np.expm1(o['err']) * 100:+.2f}% hw={o['hw']}")
print(f"RESULT v2_cells={cells} count")
print(f"RESULT v2_completed={done} count")
print(f"RESULT v2_admitted_over_bar={over} count")
print(f"RESULT v2_null_over_bar={null_over} count")
print(f"RESULT v2_worst_admitted_abs_err={np.expm1(worst) * 100:.2f} %")
pc, tc = time.process_time() - t_proc0, time.thread_time() - t_thr0
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
