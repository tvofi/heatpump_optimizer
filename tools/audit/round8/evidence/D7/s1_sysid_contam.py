"""D7-s1 sysid contamination consequence: what a contaminated experiment night does to the adopted UA.

Companion to s1_learner_freeze.py (which shows the coordinator feeds the experiment through every
contamination the passive learners freeze on). Here the production experiment
(sysid:SystemIdentification.step -> _finish -> identify_slab) runs on the production ThermalModel
plant with ONE contamination the recorder cannot see, and the production adoption gate
(coordinator:HeatPumpOptimizerCoordinator._adopt_system_identification, stubbed coordinator) decides.
Metric (adopted_ua_err_pct): (UA the gate would write - true UA)/true UA*100; "admitted" = the gate
  wrote a heat-loss scale. Count key: the scale the production gate writes.
Contaminations (plant-side only; the recorder sees the room reading and the commanded power):
  clean (null control), wood (1.0 kW unrecorded external heat through the relax phase),
  defrost (one 15-min step tick where the commanded heat was not delivered), window (1 h of extra
  loss during step: plant outdoor -15 C for 4 ticks while recorded 0 C), stale (room reading
  pinned for the whole relax phase).
Command:  PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/s1_sysid_contam.py [--perturb]
  --perturb: the sysid recorder is handed the freeze (the fix): a contaminated tick aborts the
  experiment, as _learning_frozen would; admitted_contaminated must go to 0.
Expected: admitted_contaminated=4 of 12 (exact, deterministic); clean_max_abs_fit_err=0.000 pct.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, logging
sys.path.insert(0, "tools/audit/round8/D7")
logging.disable(logging.CRITICAL)
_p0, _t0 = time.process_time(), time.thread_time()
import numpy as np
from datetime import timedelta
import s1_sysid as H  # preset_params, gate, NOW, COP, MAXP, S, BUILDINGS
S = H.S
from heatpump_optimizer.thermal_model import ThermalModel, ThermalState

PERTURB = "--perturb" in sys.argv


def drive_c(p, contam):
    model = ThermalModel(p)
    ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
    gains = float(p.internal_gains)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0))
    assert sid.arm(H.NOW, plant=p)
    outdoor = 0.0
    hold = max(ua_true * (21.0 - outdoor) - gains, 0.0)
    st = ThermalState(room_temperature=21.0,
                      slab_temperature=21.0 + hold / max(p.slab_heat_transfer, 1e-9),
                      outdoor_temperature=outdoor)
    when, dt = H.NOW, 0.25
    step_ticks = relax_ticks = 0
    pinned = None
    for _ in range(int(5.0 / dt) + 4):
        phase = sid.phase
        reading = st.room_temperature
        if contam == "stale" and phase == S.PHASE_RELAX:
            pinned = reading if pinned is None else pinned
            reading = pinned
        dirty = ((contam == "wood" and phase == S.PHASE_RELAX)
                 or (contam == "defrost" and phase == S.PHASE_STEP and step_ticks == 2)
                 or (contam == "window" and phase == S.PHASE_STEP and 1 <= step_ticks <= 4)
                 or (contam == "stale" and phase == S.PHASE_RELAX and relax_ticks >= 1))
        if PERTURB and dirty:
            sid.abort("learning frozen")  # what a _learning_frozen consult would do
        ov = sid.step(now=when, room_temp=reading, outdoor_temp=outdoor, price=0.1,
                      price_horizon=np.full(48, 1.0), learner_samples=0, max_power_kw=H.MAXP,
                      cop=H.COP, plan_power_kw=hold / H.COP, house_ua=ua_true,
                      house_capacity=float(p.room_thermal_mass), house_gains=gains,
                      house_slab_mass=float(p.slab_thermal_mass),
                      house_slab_transfer=float(p.slab_heat_transfer))
        if not sid.active:
            break
        el = hold / H.COP if ov is None else float(ov)
        heat = el * H.COP
        plant_out = outdoor
        if sid.phase == S.PHASE_STEP:
            if contam == "defrost" and step_ticks == 2:
                heat = 0.0
            if contam == "window" and 1 <= step_ticks <= 4:
                plant_out = -15.0
            step_ticks += 1
        if sid.phase == S.PHASE_RELAX:
            if contam == "wood":
                heat += 1.0
            relax_ticks += 1
        st = model.simulate_step(st, electrical_power=0.0, outdoor_temp=plant_out, dt_hours=dt,
                                 external_heat_kw=heat)
        when += timedelta(hours=dt)
    return sid, ua_true


def main():
    admitted = 0
    clean_err = []
    for name in H.BUILDINGS:
        p = H.preset_params(name)
        for contam in ("clean", "wood", "defrost", "window", "stale"):
            sid, ua_t = drive_c(p, contam)
            r = sid.result
            if not r.completed:
                print(f"CELL {name} {contam}: not completed ({r.reason})", flush=True)
                continue
            hw = S.slab_ua_adoption_halfwidth(r.ua_profile_halfwidth, r.ua_prior_halfwidth)
            sc = H.gate(sid, p)
            fit_err = (r.heat_loss_kw_per_c - ua_t) / ua_t * 100
            ad_err = (sc * p.heat_loss_coefficient - ua_t) / ua_t * 100 if sc else None
            print(f"CELL {name} {contam}: fit_ua_err={fit_err:+.2f}% hw={hw:.4f} bar={S.UA_ADOPTION_HALFWIDTH_BAR:.4f} "
                  f"admitted={sc is not None} adopted_ua_err={ad_err}", flush=True)
            if contam == "clean":
                clean_err.append(abs(fit_err))
            elif sc is not None:
                admitted += 1
    print(f"RESULT clean_max_abs_fit_err={max(clean_err) if clean_err else float('nan'):.3f} pct")
    print(f"RESULT admitted_contaminated={admitted} count (of 12 contaminated cells)")
    tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
