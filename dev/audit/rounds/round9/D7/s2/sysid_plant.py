"""D7.M2 -- the sysid plant: UA bias of the production fit on the presets.

Metric: UA bias = fitted UA / true UA - 1 of the production sysid fit
(sysid:SystemIdentification driven end to end through arm/step/_finish ->
identify_slab, then sysid:adoption_decision), for step responses generated
by the production thermal_model:ThermalModel on the three stress presets
(light_new, heavy_old, typical_slab; single zone, 0 C outdoor, 21 C room,
30-min coordinator cadence, noise 0). The TRUTH plant has exactly the
declared parameters; the only thing varied is how finely the truth is
integrated (TRUTH_SUBSTEPS per 30-min sample: 1 = the fit's own Euler step,
2 = the optimizer's 15-min step, 6 and 30 = a continuous-time house).
Count key: the value the production seam delivers -- result.heat_loss_kw_per_c
and AdoptionDecision.admit -- never an input attribute.

Also, per preset on the 30-substep truth: the one-state regression
(sysid:SystemIdentification.identify, harness-only #1395) and a free
two-state (two-exponential) fit with UA, C_r, C_s, k_s free.

Command (repo root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/s2/sysid_plant.py
Perturbation (in memory): --substep-rollout replaces sysid:_valve_drive with
the same call split into 6 equal sub-steps (a one-line production edit).
Expected: continuous_presets_bias_gt5pct 3 -> 0 (down);
continuous_presets_adopted 0 -> >=2 (up).
Expected values at baseline: slab_bias_light_new_sub30 ~ -0.15, heavy_old
~ -0.21, typical_slab refused; continuous_presets_adopted=0 (exact, noise 0).
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1, machine: cloud container B7.
Root rule: sys.path from the working directory (run from the tree under test).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time
sys.path.insert(0, ".")
sys.path.insert(0, "tests")
from datetime import datetime, timedelta
import numpy as np

from custom_components.heatpump_optimizer import sysid as S
from custom_components.heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
from custom_components.heatpump_optimizer.presets import BuildingPreset, derive
from profiles import house
from stress import BUILDINGS

OUTDOOR = 0.0
ROOM0 = 21.0
CADENCE_H = 0.5
PRESETS = ("light_new", "heavy_old", "typical_slab")
TRUTH_SUBSTEPS = (1, 2, 6, 30)

if "--substep-rollout" in sys.argv:
    _orig_drive = S._valve_drive

    def _substepped(model, state, q, outdoor, dt, _n=6):
        for _ in range(_n):
            state = _orig_drive(model, state, q, outdoor, dt / _n)
        return state
    S._valve_drive = _substepped


def declared_params(building):
    cfg = house(two_zone=False, dhw=False)
    preset = BuildingPreset(**{**vars(BUILDINGS[building]), "two_zone": False})
    d = derive(preset)
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    return p


def drive(dec, substeps):
    """The production state machine on a truth plant == the declared one."""
    model = ThermalModel(dec)
    state = S._held_state(model, ROOM0, OUTDOOR)
    ua_t = dec.heat_loss_coefficient * dec.house_heat_loss_scale
    cop = model.compute_cop(OUTDOOR)
    hold = max(ua_t * (ROOM0 - OUTDOOR) - dec.internal_gains, 0.0) / cop
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True))
    now = datetime(2026, 1, 10, 23, 0)
    assert sid.arm(now, plant=dec), sid.result.reason
    for _ in range(40):
        out = sid.step(
            now=now, room_temp=state.room_temperature, outdoor_temp=OUTDOOR,
            price=0.0, price_horizon=np.array([]), learner_samples=0,
            max_power_kw=dec.max_electrical_power, cop=cop, plan_power_kw=hold,
            house_ua=ua_t, house_capacity=dec.room_thermal_mass,
            house_gains=dec.internal_gains, house_slab_mass=dec.slab_thermal_mass,
            house_slab_transfer=dec.slab_heat_transfer,
        )
        if sid.phase in (S.PHASE_DONE, S.PHASE_ABORTED, S.PHASE_IDLE):
            break
        elec = hold if out is None else float(out)
        for _k in range(substeps):
            state = model.simulate_step(state, elec, OUTDOOR, dt_hours=CADENCE_H / substeps)
        now += timedelta(hours=CADENCE_H)
    return sid, ua_t


def twoexp_fit(sid, dec):
    """Free two-state fit (UA, C_r, C_s, k_s free; G at the prior), fine rollout."""
    from scipy.optimize import least_squares
    usable = [s for s in sid.samples if s.phase in (S.PHASE_SETTLING, S.PHASE_STEP, S.PHASE_RELAX)]
    rooms, outs, pw, dts = S._slab_series(usable)
    g = sid.config.gains_prior_kw
    n = 30
    fine = lambda a: np.repeat(a, n)

    def res(x):
        ua, cr, cs, ks = np.exp(x)
        pred = S._simulate_slab_path(ua, cr, g, cs, ks, rooms[0], fine(outs[:-1]),
                                     fine(pw[:-1]), fine(dts) / n)
        return pred[n::n] - rooms[1:]
    x0 = np.log([dec.heat_loss_coefficient * 1.3, dec.room_thermal_mass,
                 dec.slab_thermal_mass, dec.slab_heat_transfer])
    r = least_squares(res, x0, bounds=(x0 - 3, x0 + 3), max_nfev=300)
    return float(np.exp(r.x[0]))


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    biased = adopted = adopted_biased = 0
    for b in PRESETS:
        dec = declared_params(b)
        for sub in TRUTH_SUBSTEPS:
            sid, ua_t = drive(dec, sub)
            r = sid.result
            d = S.adoption_decision(r, dec, sid.config)
            bias = (r.heat_loss_kw_per_c / ua_t - 1) if r.heat_loss_kw_per_c else float("nan")
            print(f"RESULT slab_bias_{b}_sub{sub}={bias:+.5f} ratio  # completed={r.completed} "
                  f"fit_reason={r.reason!r} admit={d.admit} weight={d.weight:.3f} gate={d.reason!r}")
            if sub == 30:
                if not (np.isfinite(bias) and abs(bias) <= 0.05):
                    biased += 1
                if d.admit:
                    adopted += 1
                    if not abs(bias) <= 0.05:
                        adopted_biased += 1
                one = sid.identify()
                ob = (one.heat_loss_kw_per_c / ua_t - 1) if one.heat_loss_kw_per_c else float("nan")
                od = S.adoption_decision(one, dec, sid.config)
                print(f"RESULT one_state_bias_{b}={ob:+.5f} ratio  # completed={one.completed} "
                      f"reason={one.reason!r} admit={od.admit}")
                print(f"RESULT twoexp_bias_{b}={twoexp_fit(sid, dec) / ua_t - 1:+.5f} ratio")
    print(f"RESULT continuous_presets_bias_gt5pct={biased} count  # of 3; bias nan (refused) counts")
    print(f"RESULT continuous_presets_adopted={adopted} count  # of 3")
    print(f"RESULT continuous_presets_adopted_biased={adopted_biased} count")
    p, t = time.process_time() - t0p, time.thread_time() - t0t
    print(f"RESULT thread_factor={p / max(t, 1e-9):.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
    except Exception:
        sw = "na"
    print(f"RESULT swapins={sw}")


if __name__ == "__main__":
    main()
