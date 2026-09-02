#!/usr/bin/env python
"""D2 harness -- bias of sysid.SystemIdentification.identify under sensor noise.

Metric: median relative error (estimate/truth - 1) of the identified UA (kW/K), C (kWh/K)
and tau (h) over 300 Monte-Carlo step experiments on an exact first-order room
(C=8 kWh/K, UA=0.20 kW/K, G=0.30 kW, T_out=2 C; 2 h step at 6 kW thermal then 2 h
relax at 0 kW, sampled every 15 min -- the shape SystemIdentification.step records),
under white noise (sigma 0, 0.02, 0.05, 0.10 K), 0.1 K and 0.5 K quantisation, and a
0.15 K/h linear drift; the completion rate; the mean confidence; and, for the
experiments the coordinator's gate (confidence >= 0.3) would adopt, the median |UA error|.
Command: PYTHONPATH=tests/hastub python tools/audit/round2/D2/sysid_bias.py
Expected (c398fc84): sigma=0 -> |bias| < 1e-6 (exact recovery); quantised 0.1 K ->
  adopted-UA median |error| reported; confidence does not separate biased fits.
Perturbation: noise sigma -> 0 (the sigma=0 row IS the perturbation): bias -> 0 (to_zero).
Instrumented: sysid:SystemIdentification.identify (through SysIdSample records),
  coordinator:_adopt_system_identification gate (confidence < 0.3) replicated as a filter.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import resource
import sys
import time
from datetime import datetime, timedelta
sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
import numpy as np
_T_PROC0 = time.process_time()
_T_THR0 = time.thread_time()

from heatpump_optimizer.sysid import (
    PHASE_RELAX, PHASE_STEP, SysIdConfig, SysIdSample, SystemIdentification,
)

C_TRUE, UA_TRUE, G_TRUE, T_OUT = 8.0, 0.20, 0.30, 2.0
TAU_TRUE = C_TRUE / UA_TRUE
DT_H = 0.25
Q_STEP = 6.0
T0 = datetime(2026, 1, 15, 23, 0)


def truth(t_start: float, q: float, hours: float) -> float:
    """Exact first-order response over one interval."""
    t_inf = T_OUT + (q + G_TRUE) / UA_TRUE
    return t_inf + (t_start - t_inf) * np.exp(-hours / TAU_TRUE)


def experiment(noise, seed, dt_h=DT_H):
    rng = np.random.default_rng(seed)
    samples = []
    t = 21.0
    when = T0
    k = 0
    for phase, q, hours in ((PHASE_STEP, Q_STEP, 2.0), (PHASE_RELAX, 0.0, 2.0)):
        for _ in range(int(hours / dt_h)):
            meas = t
            if noise["kind"] == "white":
                meas = t + rng.normal(0.0, noise["sigma"]) if noise["sigma"] > 0 else t
            elif noise["kind"] == "quant":
                meas = np.round(t / noise["q"]) * noise["q"]
            elif noise["kind"] == "drift":
                meas = t + noise["rate"] * k * DT_H
            samples.append(SysIdSample(when, float(meas), T_OUT, q, phase))
            t = truth(t, q, dt_h)
            when += timedelta(hours=dt_h)
            k += 1
    sid = SystemIdentification(SysIdConfig(enabled=True, gains_prior_kw=0.3, thermal_mass_prior=10.0))
    sid.samples = samples
    return sid.identify()


noises = [
    ("white_0", {"kind": "white", "sigma": 0.0}),
    ("white_0.02", {"kind": "white", "sigma": 0.02}),
    ("white_0.05", {"kind": "white", "sigma": 0.05}),
    ("white_0.10", {"kind": "white", "sigma": 0.10}),
    ("quant_0.1", {"kind": "quant", "q": 0.1}),
    ("quant_0.5", {"kind": "quant", "q": 0.5}),
    ("drift_0.05Kph", {"kind": "drift", "rate": 0.05}),
    ("drift_0.10Kph", {"kind": "drift", "rate": 0.10}),
    ("drift_0.15Kph", {"kind": "drift", "rate": 0.15}),
]

# ---- the confidence ceiling, decomposed (sysid.py:453-459) -------------------
# confidence = r2 * min(1, rows/20) * clip(excursion/2, 0.3, 1). The comfort abort
# (max_excursion_c = 0.8 K either side of the baseline) bounds the excursion range
# at 1.6 K, so with r2 = 1 the ceiling is 0.8 * min(1, rows/20); rows come from the
# coordinator's sampling interval over the 4 h step + relax.
for dt_h in (0.25, 0.5):
    res = experiment({"kind": "white", "sigma": 0.0}, 0, dt_h=dt_h)
    rows = int(4.0 / dt_h) - 1
    sid = SystemIdentification(SysIdConfig(enabled=True))
    print(f"CELL clean data sampled every {int(dt_h * 60)} min: rows={rows} completed={res.completed} "
          f"confidence={res.confidence:.3f} UA={res.heat_loss_kw_per_c} C={res.thermal_mass_kwh_per_c}")
    print(f"RESULT sysid_clean_confidence_{int(dt_h * 60)}min={res.confidence:.3f} ratio")
    print(f"RESULT sysid_confidence_ceiling_{int(dt_h * 60)}min={0.8 * min(1.0, rows / 20.0):.3f} ratio (r2=1, 1.6 K range)")
print("RESULT sysid_adoption_gate=0.300 ratio (coordinator._adopt_system_identification)")

N = 300
summary = {}
for label, noise in noises:
    ua, c, tau, conf, done = [], [], [], [], 0
    reasons = {}
    for seed in range(N):
        res = experiment(noise, seed)
        if not res.completed:
            reasons[res.reason] = reasons.get(res.reason, 0) + 1
            continue
        done += 1
        ua.append(res.heat_loss_kw_per_c / UA_TRUE - 1.0)
        c.append(res.thermal_mass_kwh_per_c / C_TRUE - 1.0)
        tau.append(res.time_constant_hours / TAU_TRUE - 1.0)
        conf.append(res.confidence)
        if noise["kind"] in ("quant", "drift") or noise.get("sigma", 0) == 0:
            if seed >= 1 and noise["kind"] != "white":
                break  # deterministic: one run says it all
    ua, c, tau, conf = map(np.asarray, (ua, c, tau, conf))
    runs = done + sum(reasons.values())
    adopted = conf >= 0.3 if conf.size else np.zeros(0, dtype=bool)
    med_ua = float(np.median(ua)) if ua.size else float("nan")
    med_c = float(np.median(c)) if c.size else float("nan")
    med_tau = float(np.median(tau)) if tau.size else float("nan")
    mean_conf = float(np.mean(conf)) if conf.size else float("nan")
    adopt_frac = float(np.mean(adopted)) if conf.size else 0.0
    adopted_abs_ua = float(np.median(np.abs(ua[adopted]))) if np.any(adopted) else float("nan")
    corr = float(np.corrcoef(conf, np.abs(ua))[0, 1]) if ua.size > 2 and np.std(conf) > 0 else float("nan")
    print(f"CELL {label}: runs={runs} completed={done} reasons={reasons} median_rel_err UA={med_ua:+.4f} "
          f"C={med_c:+.4f} tau={med_tau:+.4f} mean_conf={mean_conf:.3f} adopted={adopt_frac:.2f} "
          f"adopted_median_abs_UA_err={adopted_abs_ua:.4f} corr(conf,|UAerr|)={corr:+.3f}")
    print(f"RESULT sysid_{label}_completion={done / max(runs, 1):.3f} ratio")
    print(f"RESULT sysid_{label}_median_rel_err_UA={med_ua:+.4f} ratio")
    print(f"RESULT sysid_{label}_median_rel_err_C={med_c:+.4f} ratio")
    print(f"RESULT sysid_{label}_median_rel_err_tau={med_tau:+.4f} ratio")
    print(f"RESULT sysid_{label}_mean_confidence={mean_conf:.3f} ratio")
    print(f"RESULT sysid_{label}_adopted_fraction={adopt_frac:.3f} ratio")
    print(f"RESULT sysid_{label}_adopted_median_abs_UA_err={adopted_abs_ua:.4f} ratio")
    summary[label] = (med_ua, adopted_abs_ua, adopt_frac)

proc = time.process_time() - _T_PROC0
thr = time.thread_time() - _T_THR0
print(f"RESULT thread_factor={proc / max(thr, 1e-9):.3f} ratio")
print(f"RESULT load1={os.getloadavg()[0]:.2f} load")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_nswap} count")
