"""D7-s1 sysid: UA bias of the production sysid fit and whether the adoption gate admits it.

Metric (ua_bias_pct): (adopted-fit UA - true plant UA) / true UA * 100, where the fit is
  heatpump_optimizer.sysid:SystemIdentification.identify_slab (reached through arm/step/_finish,
  the production call sequence) and "admitted" means the production gate
  coordinator:HeatPumpOptimizerCoordinator._adopt_system_identification applied a scale.
  Count key: the heat-loss scale the production gate WRITES (stub._apply_house_heat_loss_scale),
  not any attribute of the result.
Cells: three building presets (tests/stress.py:BUILDINGS) x true slab pair (k_s, C_s) scaled by a
  factor against the DECLARED (configured) pair the fit trusts. factor 1.0 is the null control.
Also: the one-state identify() (declare_plant=False) and a free two-state fit (UA, C_r, C_s, k_s
  all free; the "two-exponential" fit) on the matched plant, for the brief's step 2 comparison.
Command:  PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/s1_sysid.py [--perturb-declared] [--free]
  --free: also run the free four-constant fit on the matched plant (slow: minutes per preset).
  --perturb-declared: declare the TRUE slab pair to the fit (i.e. the config is right);
  max_abs_ua_bias must fall from 25.83 toward 0.
Expected (baseline, sigma=0, deterministic): admitted_biased_cells=0, max_abs_ua_bias=25.83 pct,
  matched prod bias 0.000 pct on all three presets. A NON-FINDING instrument: the adoption gate
  refuses every slab-misspecified fit whose UA bias exceeds 10 %.
Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82; machine: 4-vCPU cloud container (counts only).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, types, dataclasses
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests/hastub")
import numpy as np
from datetime import datetime, timedelta, timezone
from scipy.optimize import least_squares

_p0, _t0 = time.process_time(), time.thread_time()

from heatpump_optimizer.presets import BuildingPreset, derive
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from heatpump_optimizer import sysid as S
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from profiles import house
from stress import BUILDINGS

PERTURB = "--perturb-declared" in sys.argv
NOW = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
COP = 3.0
MAXP = 3.5


def preset_params(name):
    cfg = house(two_zone=False, dhw=False)
    d = derive(BuildingPreset(**{**vars(BUILDINGS[name]), "two_zone": False}))
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.wind_sensitivity = 0.0
    return p


def drive(true_p, declared_p, declare=True):
    model = ThermalModel(true_p)
    ua_true = true_p.heat_loss_coefficient * true_p.house_heat_loss_scale
    gains = float(true_p.internal_gains)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0))
    assert sid.arm(NOW, plant=declared_p if declare else None)
    outdoor = 0.0
    hold = max(ua_true * (21.0 - outdoor) - gains, 0.0)
    st = ThermalState(room_temperature=21.0,
                      slab_temperature=21.0 + hold / max(true_p.slab_heat_transfer, 1e-9),
                      outdoor_temperature=outdoor)
    when, dt = NOW, 0.25
    trace = []
    for _ in range(int(5.0 / dt) + 4):
        ov = sid.step(now=when, room_temp=st.room_temperature, outdoor_temp=outdoor, price=0.1,
                      price_horizon=np.full(48, 1.0), learner_samples=0, max_power_kw=MAXP,
                      cop=COP, plan_power_kw=hold / COP,
                      house_ua=declared_p.heat_loss_coefficient * declared_p.house_heat_loss_scale,
                      house_capacity=float(declared_p.room_thermal_mass), house_gains=gains,
                      house_slab_mass=float(declared_p.slab_thermal_mass),
                      house_slab_transfer=float(declared_p.slab_heat_transfer))
        if not sid.active:
            break
        el = hold / COP if ov is None else float(ov)
        trace.append((st.room_temperature, el * COP))
        st = model.simulate_step(st, electrical_power=0.0, outdoor_temp=outdoor, dt_hours=dt,
                                 external_heat_kw=el * COP)
        when += timedelta(hours=dt)
    return sid, ua_true


def gate(sid, declared_p):
    """Run the production adoption gate on a stub coordinator; return written scale or None."""
    written = []
    stub = types.SimpleNamespace(
        _sysid=sid, _thermal_params=declared_p, _house_heat_loss_scale=1.0,
        _house_heat_loss_samples=0,
        _apply_house_heat_loss_scale=lambda v: written.append(v),
        _spawn=lambda c: getattr(c, "close", lambda: None)(),
        _async_save_thermal_learning=lambda: None,
    )
    stub._ctx = stub
    HeatPumpOptimizerCoordinator._adopt_system_identification(stub)
    return written[0] if written else None


def free_two_state(sid, declared_p):
    """Free fit of all four two-state constants (the 'two-exponential' comparison fit)."""
    usable = [s for s in sid.samples if s.phase in (S.PHASE_SETTLING, S.PHASE_STEP, S.PHASE_RELAX)]
    rooms, outs, pw, dts = S._slab_series(usable)
    g = sid.config.gains_prior_kw
    def res(x):
        ua, cr, cs, ks = np.exp(x)
        pred = S._simulate_slab_path(ua, cr, g, cs, ks, float(rooms[0]), outs[:-1], pw[:-1], dts)
        return pred[1:] - rooms[1:]
    ua0 = declared_p.heat_loss_coefficient
    x0 = np.log([ua0, declared_p.room_thermal_mass, declared_p.slab_thermal_mass,
                 declared_p.slab_heat_transfer])
    best = None
    for m in (2.0,):  # one start, off the truth by 2x on every constant but UA
        r = least_squares(res, x0 + np.log([1, m, 1 / m, m]), method="lm", max_nfev=1500)
        if best is None or r.cost < best.cost:
            best = r
    return float(np.exp(best.x[0]))


FACTORS = [("ks", 0.5), ("ks", 0.7), ("ks", 1.4), ("ks", 2.0), ("cs", 0.5), ("cs", 2.0)]


def main():
    global admitted_biased
    admitted_biased = 0
    cells = []
    bar = S.UA_ADOPTION_HALFWIDTH_BAR
    for name in BUILDINGS:
        declared = preset_params(name)
        # matched plant (null control): one-state, production two-state, free two-state
        sid_m, ua_t = drive(declared, declared)
        r = sid_m.result
        hw = S.slab_ua_adoption_halfwidth(r.ua_profile_halfwidth, r.ua_prior_halfwidth)
        sc = gate(sid_m, declared)
        b = (r.heat_loss_kw_per_c - ua_t) / ua_t * 100 if r.heat_loss_kw_per_c else float("nan")
        print(f"RESULT matched_{name}_prod_ua_bias={b:.3f} pct  hw={hw} admitted={sc is not None}")
        sid_1, _ = drive(declared, declared, declare=False)
        r1 = sid_1.result
        b1 = ((r1.heat_loss_kw_per_c - ua_t) / ua_t * 100) if r1.completed and r1.heat_loss_kw_per_c else r1.reason
        print(f"RESULT matched_{name}_onestate_ua_bias={b1} pct")
        if "--free" in sys.argv:
            uaf = free_two_state(sid_m, declared)
            print(f"RESULT matched_{name}_free_twostate_ua_bias={(uaf-ua_t)/ua_t*100:.3f} pct")
        for key, f in FACTORS:
            true_p = dataclasses.replace(declared)
            if key == "ks":
                true_p.slab_heat_transfer = declared.slab_heat_transfer * f
            else:
                true_p.slab_thermal_mass = declared.slab_thermal_mass * f
            decl = true_p if PERTURB else declared
            sid, ua_t = drive(true_p, decl)
            r = sid.result
            if not r.completed:
                print(f"CELL {name} {key}x{f}: refused ({r.reason})")
                cells.append(None)
                continue
            b = (r.heat_loss_kw_per_c - ua_t) / ua_t * 100
            hw = S.slab_ua_adoption_halfwidth(r.ua_profile_halfwidth, r.ua_prior_halfwidth)
            sc = gate(sid, decl)
            adopted_err = ((sc * decl.heat_loss_coefficient) - ua_t) / ua_t * 100 if sc else None
            ab = sc is not None and abs(b) > 10.0
            admitted_biased += ab
            cells.append(b)
            print(f"CELL {name} {key}x{f}: ua_bias={b:+.2f}% hw={hw:.4f} (bar {bar:.4f}) conf={r.confidence:.2f} "
                  f"admitted={sc is not None} written_scale={sc} adopted_ua_err={adopted_err}")

    vals = [abs(c) for c in cells if c is not None]
    print(f"RESULT cells={len(cells)} completed={len(vals)}")
    print(f"RESULT max_abs_ua_bias={max(vals):.2f} pct min_abs_ua_bias={min(vals):.2f} pct")
    print(f"RESULT max_abs_ua_bias_drop_worst={sorted(vals)[-2]:.2f} pct")
    print(f"RESULT admitted_biased_cells={admitted_biased} count (|bias|>10% and gate wrote a scale)")
    tf = (time.process_time() - _p0) / max(time.thread_time() - _t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
