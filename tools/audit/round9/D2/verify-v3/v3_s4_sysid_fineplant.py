#!/usr/bin/env python3
"""V3 (round 9, D2-s4-01 and D2-s4-02): sysid abort and coverage with a near-continuous plant and real-sensor noise.

Metric (one line): per (preset, noise) cell, over seeded runs of the production experiment
(sysid.SystemIdentification.arm/step at the coordinator's default 30-min cadence,
DEFAULT_OPTIMIZATION_INTERVAL), with the true plant integrated by ThermalModel.simulate_step in
1-minute substeps between readings (so the plant's own Euler step cannot overshoot the sizer's
prediction), (a) the count of runs ending with reason "room temperature drifted beyond the allowed
excursion" and (b) among fits sysid.adoption_decision admits, the count whose true UA lies outside
|log(UA_fit/UA_true)| <= slab_ua_adoption_halfwidth(profile, prior). Noise kinds: sigma0 (null),
white 0.02 C, q01 (0.1 C rounding + 0.005 white, the shape an HA temperature entity reports).
Command: PYTHONPATH=tests/hastub PYTHONDONTWRITEBYTECODE=1 /home/claude/venv/bin/python tools/audit/round9/D2/verify-v3/v3_s4_sysid_fineplant.py [--seeds 12] [--dt 0.5] [--sub N] [--perturb margin]
(--sub 1 integrates the plant at the reading step, the estimator's own discretisation: the finders' setting.)
Perturbation (--perturb margin): SystemIdentification._size_step_power's return x 0.85 in memory;
(a) must go down. Null control: sigma0 -> (a) = 0 and (b) = 0.
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; machine: G3-V3 cloud container, 4 cores, linux.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys, time, argparse, warnings
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "custom_components")
sys.path.insert(0, "tests")
import numpy as np
from unittest import mock
from heatpump_optimizer import presets, sysid as S
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
from profiles import house
from stress import BUILDINGS

warnings.simplefilter("ignore", RuntimeWarning)
ap = argparse.ArgumentParser(); ap.add_argument("--seeds", type=int, default=12); ap.add_argument("--perturb", default="none"); ap.add_argument("--dt", type=float, default=0.5); ap.add_argument("--sub", type=int, default=0)
A = ap.parse_args()
t0p, t0t = time.process_time(), time.thread_time()
ABORT = "room temperature drifted beyond the allowed excursion"
NOW = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
COP = 3.0
DT = A.dt
SUB = A.sub or int(round(DT * 60))  # 1-minute plant substeps; --sub 1 reproduces the finders' same-step plant

def plant(name):
    cfg = house(two_zone=False, dhw=False)
    d = presets.derive(BUILDINGS[name]); d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg); p.two_zone_enabled = False
    return p

def drive(params, seed, kind):
    rng = np.random.default_rng(seed)
    ua = params.heat_loss_coefficient * params.house_heat_loss_scale
    g = float(params.internal_gains)
    model = ThermalModel(ThermalParameters(**{**params.__dict__}))
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0,
        gains_prior_kw=g, thermal_mass_prior=float(params.room_thermal_mass)))
    assert sid.arm(NOW, plant=params)
    hold = max(ua * 21.0 - g, 0.0)
    ks = max(float(params.slab_heat_transfer), 1e-9)
    st = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / ks, outdoor_temperature=0.0)
    when = NOW
    for _ in range(int(5.0 / DT) + 4):
        x = st.room_temperature
        if kind == "white002": x += rng.normal(0.0, 0.02)
        elif kind == "q01": x = round((x + rng.normal(0.0, 0.005)) / 0.1) * 0.1
        ov = sid.step(now=when, room_temp=x, outdoor_temp=0.0, price=0.1, price_horizon=np.full(48, 1.0),
                      learner_samples=0, max_power_kw=float(params.max_electrical_power), cop=COP,
                      plan_power_kw=hold / COP, house_ua=ua, house_capacity=float(params.room_thermal_mass),
                      house_gains=g, house_slab_mass=float(params.slab_thermal_mass),
                      house_slab_transfer=float(params.slab_heat_transfer))
        if not sid.active: break
        elec = hold / COP if ov is None else float(ov)
        for _k in range(SUB):
            st = model.simulate_step(st, electrical_power=0.0, outdoor_temp=0.0, dt_hours=DT / SUB,
                                     external_heat_kw=elec * COP)
        when += timedelta(hours=DT)
    return sid, sid.result, ua

patch = []
if A.perturb == "margin":
    orig = S.SystemIdentification._size_step_power
    patch = [mock.patch.object(S.SystemIdentification, "_size_step_power",
             lambda self, *a, **k: (lambda q: None if q is None else 0.85 * q)(orig(self, *a, **k)))]
for pt in patch: pt.start()
tot = {"abort": 0, "runs": 0, "adm": 0, "miss": 0}
bias = []; aerr = []
for pname in ("light_new", "typical_slab", "heavy_old"):
    p = plant(pname)
    for kind in ("sigma0", "white002", "q01"):
        n = ab = adm = miss = 0
        for k in range(1 if kind == "sigma0" else A.seeds):
            sid, res, ua = drive(p, 20260926 + k, kind)
            n += 1
            if res is None: continue
            ab += res.reason == ABORT
            if res.completed:
                d = S.adoption_decision(res, p, sid.config)
                if d.admit:
                    adm += 1
                    hw = S.slab_ua_adoption_halfwidth(res.ua_profile_halfwidth, res.ua_prior_halfwidth)
                    miss += abs(float(np.log(res.heat_loss_kw_per_c / ua))) > hw
                    bias.append(res.heat_loss_kw_per_c / ua - 1.0)
                    aerr.append(d.weight * (d.scale - ua / float(p.heat_loss_coefficient)))
        tag = f"{pname}_{kind}"
        print(f"RESULT {tag}_runs={n} count"); print(f"RESULT {tag}_aborted={ab} count")
        print(f"RESULT {tag}_admitted={adm} count"); print(f"RESULT {tag}_admitted_missed={miss} count", flush=True)
        if kind != "sigma0":
            tot["abort"] += ab; tot["runs"] += n; tot["adm"] += adm; tot["miss"] += miss
for pt in patch: pt.stop()
print(f"RESULT noisy_aborted_total={tot['abort']} of {tot['runs']}")
print(f"RESULT noisy_admitted_missed_total={tot['miss']} of {tot['adm']}")
if bias:
    print(f"RESULT admitted_bias_mean={np.mean(bias)*100:+.2f} pct (positive {sum(b > 0 for b in bias)} of {len(bias)})")
    print(f"RESULT adopted_scale_err_mean={np.mean(aerr)*100:+.2f} pct max {np.max(aerr)*100:+.2f} pct")
print(f"RESULT perturbed={A.perturb} dt={DT} sub={SUB}")
dp, dtt = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={dp/max(dtt,1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
sw = 0
try:
    for line in open("/proc/vmstat"):
        if line.startswith("pswpin"): sw = int(line.split()[1])
except OSError: pass
print(f"RESULT swapins={sw}")
