#!/usr/bin/env python3
"""V2 (independent) re-measure of D2-s4-01: sysid adoption interval coverage.

Metric (one line): among fits sysid.adoption_decision admits, the share whose
normalised error z = |log(UA_fit/UA_true)| / slab_ua_adoption_halfwidth(profile, prior)
exceeds 1 (a calibrated 95 % interval: ~0.05), plus the median z and the admitted
fits' mean signed UA error; own driver (not the finder's gate_bias.drive): plant
integrated with 6 sub-steps per reading on production ThermalModel.simulate_step, seeds
disjoint from the finder's (base 777000), presets typical_slab and heavy_old, step
capped at 3.5 kW (the finder's MAX_KW, so the sizer is not the abort-limited D2-s4-02
regime), outdoor --out (default 2 degC), white sigma --sigmas, cadence {0.5, 0.25} h.
Count key: SysIdResult.heat_loss_kw_per_c and its published half-widths vs the plant's UA.
Hooks: sysid:SystemIdentification.arm/step/_finish/identify_slab, sysid:adoption_decision,
sysid:slab_ua_adoption_halfwidth.
Perturbation / null: --sigma0 (noise 0): admitted misses must be 0.
Command: PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D2/verify-v2/v2_coverage.py [--seeds 30] [--sigma0]
Baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1; box G3-V2 (4-core linux, py3.14.0rc2). Seeded, exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import sys
import time
import warnings
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np  # noqa: E402
from profiles import house  # noqa: E402
from stress import BUILDINGS  # noqa: E402
from heatpump_optimizer import presets, sysid as S  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

warnings.simplefilter("ignore", RuntimeWarning)
ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=30)
ap.add_argument("--sigma0", action="store_true")
ap.add_argument("--out", type=float, default=2.0)
ap.add_argument("--sigmas", default="0.02,0.05")
A = ap.parse_args()
t0p, t0t = time.process_time(), time.thread_time()
T0 = datetime(2026, 2, 10, 23, 0, tzinfo=timezone.utc)
COP, OUT, MAXKW = 3.0, A.out, 3.5


def params(name):
    cfg = house(two_zone=False, dhw=False)
    d = presets.derive(BUILDINGS[name])
    d.pop("heating_response_hours", None)
    cfg.update(d)
    p = ThermalParameters.from_config(cfg)
    p.two_zone_enabled = False
    return p


def experiment(p, seed, sigma, cad):
    rng = np.random.default_rng(seed)
    ua = p.heat_loss_coefficient * p.house_heat_loss_scale
    g = float(p.internal_gains)
    plant = ThermalModel(ThermalParameters(**{**p.__dict__}))
    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0,
                                               gains_prior_kw=g, thermal_mass_prior=float(p.room_thermal_mass)))
    if not sid.arm(T0, plant=p):
        return None
    hold = max(ua * (21.0 - OUT) - g, 0.0)
    st = ThermalState(room_temperature=21.0, slab_temperature=21.0 + hold / max(p.slab_heat_transfer, 1e-9),
                      outdoor_temperature=OUT)
    now = T0
    for _ in range(int(6.0 / cad)):
        rd = st.room_temperature + (rng.normal(0.0, sigma) if sigma else 0.0)
        ov = sid.step(now=now, room_temp=rd, outdoor_temp=OUT, price=0.05, price_horizon=np.full(48, 1.0),
                      learner_samples=0, max_power_kw=MAXKW, cop=COP, plan_power_kw=hold / COP,
                      house_ua=ua, house_capacity=float(p.room_thermal_mass), house_gains=g,
                      house_slab_mass=float(p.slab_thermal_mass), house_slab_transfer=float(p.slab_heat_transfer))
        if not sid.active:
            break
        q = hold if ov is None else float(ov) * COP
        for _ in range(6):
            st = plant.simulate_step(st, 0.0, OUT, dt_hours=cad / 6, external_heat_kw=q)
        now += timedelta(hours=cad)
    return sid, sid.result, ua


adm = miss = 0
zs, bias = [], []
cells = []
for name in ("typical_slab", "heavy_old"):
    p = params(name)
    for sg in [float(x) for x in A.sigmas.split(",")]:
        for cad in (0.5, 0.25):
            sigma = 0.0 if A.sigma0 else sg
            ca = cm = 0
            for k in range(A.seeds if sigma else 1):
                out = experiment(p, 777000 + k, sigma, cad)
                if out is None:
                    continue
                sid, res, ua = out
                if not res.completed:
                    continue
                dec = S.adoption_decision(res, p, sid.config)
                if not dec.admit:
                    continue
                hw = S.slab_ua_adoption_halfwidth(res.ua_profile_halfwidth, res.ua_prior_halfwidth)
                z = abs(np.log(res.heat_loss_kw_per_c / ua)) / hw
                ca += 1
                cm += z > 1.0
                zs.append(z)
                bias.append(res.heat_loss_kw_per_c / ua - 1.0)
            adm += ca
            miss += cm
            cells.append((ca, cm))
            print(f"RESULT {name}_s{sg}_cad{cad}_admitted={ca} missed={cm}", flush=True)
print(f"RESULT admitted_total={adm} count")
print(f"RESULT admitted_miss_share={miss / max(adm, 1):.3f} ratio (miss {miss})")
if zs:
    print(f"RESULT admitted_z_median={np.median(zs):.3f}")
    print(f"RESULT admitted_bias_mean={np.mean(bias) * 100:+.2f} %")
    print(f"RESULT admitted_bias_positive={sum(b > 0 for b in bias)} of {len(bias)}")
rated = [(m, a) for a, m in cells if a]
if len(rated) >= 2:
    wm, wa = max(rated)
    print(f"RESULT miss_share_drop_worst_cell={(miss - wm) / max(adm - wa, 1):.3f} ratio")
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / max(tc, 1e-9):.4f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = next(int(ln.split()[1]) for ln in open("/proc/vmstat") if ln.startswith("pswpin"))
except Exception:
    sw = -1
print(f"RESULT swapins={sw}")
