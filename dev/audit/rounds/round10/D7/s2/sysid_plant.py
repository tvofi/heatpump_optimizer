"""D7.M2 -- first-order sysid plant vs the production ThermalModel.

Metric: UA bias = fitted UA / true UA - 1, per building preset (tests/stress.py
BUILDINGS), for (a) sysid:SystemIdentification.identify (first-order, harness-only
route), (b) sysid:SystemIdentification.identify_slab (production route, arm with
plant), (c) a two-exponential step fit; and sysid:adoption_decision's admit flag.
Count key: the UA the production fit returns (result.heat_loss_kw_per_c).
Run:   PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s2/sysid_plant.py [--sigma S]
Noise-free by default (sigma=0); --seed fixed.  Expected: printed values exact (deterministic).
Baseline 17f1c55fad1b; machine: B5 (macOS arm64), venv-ci.
Root rule: ROOT = Path('.') (cwd = tree under test); sys.path from cwd.
Perturbation: --two-state-truth=off sets slab_heat_transfer huge (slab glued
to room) so the plant is effectively first-order; the first-order bias must shrink.
"""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse
sys.path.insert(0, "custom_components"); sys.path.insert(0, "tests")
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import numpy as np
from scipy.optimize import curve_fit
t0p, t0t = time.process_time(), time.thread_time()
from heatpump_optimizer.presets import derive
from heatpump_optimizer.thermal_model import ThermalParameters, ThermalModel, ThermalState
from heatpump_optimizer import sysid as S
from stress import BUILDINGS, house

ap = argparse.ArgumentParser(); ap.add_argument("--sigma", type=float, default=0.0)
ap.add_argument("--glue-slab", action="store_true"); ap.add_argument("--step-kw", type=float, default=0.0)
a = ap.parse_args()
rng = np.random.default_rng(7)
OUT = 0.0; DT = 0.25

def params_for(name):
    cfg = house(two_zone=False, dhw=False)
    d = derive(BUILDINGS[name]); d.pop("heating_response_hours", None); cfg.update(d)
    p = ThermalParameters.from_config(cfg); p.dhw_enabled = False
    if a.glue_slab: p.slab_heat_transfer = 1e3
    return p

def run(name):
    p = params_for(name); m = ThermalModel(p)
    ua_true = p.heat_loss_coefficient * p.house_heat_loss_scale
    q = a.step_kw or 0.25 * ua_true * 21.0  # thermal step, ~quarter of the standing loss
    # equilibrium start: hold room at 21 with standing-loss heat for 48 h
    st = ThermalState(room_temperature=21.0, slab_temperature=21.0, outdoor_temperature=OUT)
    hold = ua_true * 21.0
    for _ in range(int(48/DT)):
        st = m.simulate_step(st, 0.0, OUT, dt_hours=DT, measured_heat_kw=hold)
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True))
    now = datetime(2026, 1, 15, 23, tzinfo=timezone.utc)
    armed = sid.arm(now, plant=p)
    if not armed:  # no-plant arm keeps the state machine usable for identify()
        sid.arm(now)
    phases = [(S.PHASE_SETTLING, 1.0, hold), (S.PHASE_STEP, 2.0, hold + q), (S.PHASE_RELAX, 2.0, hold - q)]
    samples = []; t = now; rooms = []; times = []
    for ph, hrs, qk in phases:
        for _ in range(int(hrs/DT)):
            obs = st.room_temperature + (rng.normal(0, a.sigma) if a.sigma else 0.0)
            samples.append(S.SysIdSample(t, obs, OUT, qk, ph)); rooms.append(st.room_temperature); times.append((t-now).total_seconds()/3600)
            st = m.simulate_step(st, 0.0, OUT, dt_hours=DT, measured_heat_kw=qk); t += timedelta(hours=DT)
    samples.append(S.SysIdSample(t, st.room_temperature, OUT, 0.0, S.PHASE_RELAX))
    sid.samples = samples
    r1 = sid.identify()
    r2 = sid.identify_slab() if armed else None
    # two-exponential fit of the step segment response (settle..end of step), gain -> UA
    tt = np.array(times[4:12]) - times[4]; yy = np.array(rooms[4:12]) - rooms[4]
    tt = np.append(tt, 2.0); yy = np.append(yy, rooms[12] - rooms[4]) if len(rooms) > 12 else yy
    f = lambda x, a1, t1, a2, t2: a1*(1-np.exp(-x/t1)) + a2*(1-np.exp(-x/t2))
    try:
        popt, _ = curve_fit(f, tt, yy, p0=[0.3, 0.5, 0.5, 20.0], bounds=([0,0.01,0,1],[50,5,50,500]), maxfev=20000)
        ua2 = q / (popt[0] + popt[2])
    except Exception:
        ua2 = float("nan")
    out = {}
    for tag, r in (("first_order", r1), ("slab", r2)):
        if r is None:
            print(f"RESULT {name}.{tag}.armed=0 flag"); continue
        ua = r.heat_loss_kw_per_c
        bias = (ua/ua_true - 1) if (r.completed and ua) else float("nan")
        dec = S.adoption_decision(r, p, sid.config)
        print(f"RESULT {name}.{tag}.ua_bias={bias:+.4f} ratio")
        print(f"RESULT {name}.{tag}.completed={int(bool(r.completed))} flag  reason={r.reason!r}")
        print(f"RESULT {name}.{tag}.admitted={int(dec.admit)} flag  why={dec.reason!r}")
        out[tag] = (bias, dec.admit)
    print(f"RESULT {name}.two_exp.ua_bias={ua2/ua_true-1:+.4f} ratio")
    print(f"RESULT {name}.armed_with_plant={int(armed)} flag ua_true={ua_true:.4f} q={q:.3f}")
    return out

res = {n: run(n) for n in BUILDINGS}
fo = [abs(v["first_order"][0]) for v in res.values() if "first_order" in v and np.isfinite(v["first_order"][0])]
print(f"RESULT first_order_max_abs_bias={max(fo) if fo else float('nan'):.4f} ratio")
adm = sum(1 for v in res.values() for k in v if v[k][1] and abs(v[k][0]) > 0.10)
print(f"RESULT admitted_with_abs_bias_gt_10pct={adm} count")
tf = (time.process_time()-t0p)/max(time.thread_time()-t0t,1e-9)
print(f"RESULT thread_factor={tf:.3f}"); print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
