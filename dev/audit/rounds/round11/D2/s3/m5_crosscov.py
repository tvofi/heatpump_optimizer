"""D2.M5 cross-covariate: the house heat-loss scale and the internal-gains
profile driven together, each under error in the other's covariate, with the
gains fold gated on a converged heat-loss level. Cells: noise in {white,
quantised_0.1C, drifting} on the readings the residual is built from.

Drives the production arithmetic on a duck-typed holder, per accepted dark
interval, in the coordinator's order (_async_learn_house_heat_loss): first
HeatPumpOptimizerCoordinator._fold_internal_gains (gated by
coordinator.internal_gains_gate_open on the house sample count), then
thermal_model.learner_newton_step (trust region coordinator._LEARNER_TRUST_REGION,
alpha coordinator.HOUSE_LOSS_ALPHA) and
HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale. The residual is the
first-order single-zone one the replay produces against a model that carries
the current scale AND the current per-hour profile (the profile reaches the
live model through _model_corrections, as ThermalModel.internal_gains_at reads it):
  e = [(g_true(h) - g_model(h)) - (u_true*(Tin - Tout) - u_now*(Tin_read - Tout_read))] * dt / C
Plant: UA 0.2 kW/K x scale 1.0, C 10 kWh/K, dt 0.5 h, indoor 21 C, outdoor
-5 + 3 sin(diurnal) C, dark; prior gains g0 = 0.3 kW. Two truths: no genuine
gain (g_true = g0 every hour) and a genuine +0.6 kW evening gain 17-22 h.
Noise arms (on both readings): white N(0, 0.1 K); quantised to 0.1 K;
drifting: an outdoor sensor drift ramping 0 -> +1.5 K over the run.
120 days of 30-minute intervals per run, 5 seeds.

Metric definitions (one line each):
  gain_recovery = (g_learned - g0) / (g_true - g0) averaged over the gain hours,
                  genuine-gain truth (identity: 1; the ridge INTERNAL_GAINS_RIDGE
                  tethers it to a fixed point alpha/(alpha+ridge))
  gain_spurious = max over hours of |g_learned - g0| under the no-gain truth, kW (identity: ~0)
  scale_err     = |house_heat_loss_scale - 1| at the end (identity: ~0 under zero-mean noise)
  premature     = gains folds taken while internal_gains_gate_open was False (identity: 0)
Count key: the holder's _internal_gains_profile and _house_heat_loss_scale as the
production folds leave them.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m5_crosscov.py
Perturbation: --perturb-ridge0 sets coordinator.INTERNAL_GAINS_RIDGE = 0:
  gain_recovery must go up to 1 (the shortfall to_zero).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, np

import argparse
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace

sys.path.insert(0, "custom_components")
import harness  # noqa: F401,E402
import heatpump_optimizer.coordinator as cm  # noqa: E402
from heatpump_optimizer.thermal_model import learner_newton_step  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--perturb-ridge0", action="store_true")
ap.add_argument("--days", type=int, default=120)
ap.add_argument("--seeds", type=int, default=5)
A = ap.parse_args()

cm._publish_params = lambda coord, /, **f: None  # the seam's write, not its arithmetic
if A.perturb_ridge0:
    cm.INTERNAL_GAINS_RIDGE = 0.0

U, C, DT_H, TIN, G0 = 0.2, 10.0, 0.5, 21.0, 0.3
GAIN_HOURS = range(17, 22)


def g_true(hour, genuine):
    return G0 + (0.6 if genuine and hour in GAIN_HOURS else 0.0)


def run(noise, genuine, seed):
    rng = np.random.default_rng(seed)
    params = SimpleNamespace(two_zone_enabled=False, heat_loss_coefficient=U, room_thermal_mass=C,
                             internal_gains=G0)
    h = SimpleNamespace(_house_heat_loss_scale=1.0, _house_heat_loss_samples=0,
                        _internal_gains_profile=None,
                        _config=SimpleNamespace(internal_gains_learning_enabled=True),
                        _thermal_params=params)
    t0 = datetime(2026, 1, 1)
    n = int(A.days * 24 / DT_H)
    premature = 0
    folds = 0
    for i in range(n):
        when = t0 + timedelta(hours=i * DT_H)
        hr = when.hour
        tout = -5.0 + 3.0 * np.sin(2 * np.pi * (hr - 9) / 24.0)
        if noise == "white":
            tin_r = TIN + rng.normal(0, 0.1)
            tout_r = tout + rng.normal(0, 0.1)
        elif noise == "quantised_0.1C":
            tin_r = round(TIN + rng.uniform(-0.3, 0.3), 1) - 0.0  # the room wanders, the sensor rounds
            tin_true = tin_r  # quantised reading of a wandering room: truth unrounded below
            tout_r = round(tout, 1)
        else:  # drifting
            tin_r = TIN
            tout_r = tout + 1.5 * i / n
        tin_t = TIN
        if noise == "quantised_0.1C":
            tin_t = tin_true + rng.uniform(-0.05, 0.05)  # the true room within the rounding bin
        prof = h._internal_gains_profile
        g_model = G0 if prof is None else prof[hr]
        cur = h._house_heat_loss_scale
        e = ((g_true(hr, genuine) - g_model) - (U * 1.0 * (tin_t - tout) - U * cur * (tin_r - tout_r))) * DT_H / C
        if cm._loss_residual_rejected(e, "house heat loss"):
            continue
        state = SimpleNamespace(solar_radiation=0.0)
        before = None if h._internal_gains_profile is None else list(h._internal_gains_profile)
        gate = cm.internal_gains_gate_open(h._house_heat_loss_samples)
        cm.HeatPumpOptimizerCoordinator._fold_internal_gains(h, when, state, e, DT_H)
        moved = h._internal_gains_profile is not None and h._internal_gains_profile != before
        if moved:
            folds += 1
            if not gate:
                premature += 1
        step = learner_newton_step(cur, U, C, e, tin_r - tout_r, DT_H,
                                   trust_region=cm._LEARNER_TRUST_REGION, alpha=cm.HOUSE_LOSS_ALPHA)
        if step is not None:
            cm.HeatPumpOptimizerCoordinator._apply_house_heat_loss_scale(h, step[1])
            h._house_heat_loss_samples += 1
    prof = h._internal_gains_profile or [G0] * 24
    return prof, h._house_heat_loss_scale, premature, folds


rec_all, spur_all, scale_all, prem_all = [], [], [], []
sg_all, sn_all = [], []
for noise in ("white", "quantised_0.1C", "drifting"):
    recs, spurs, scales, prems = [], [], [], 0
    sg_l, sn_l = [], []
    for seed in range(A.seeds):
        prof_g, s_g, p1, f1 = run(noise, True, seed)
        prof_n, s_n, p2, f2 = run(noise, False, seed)
        recs.append(float(np.mean([(prof_g[hh] - G0) / 0.6 for hh in GAIN_HOURS])))
        spurs.append(float(max(abs(g - G0) for g in prof_n)))
        scales.append(max(abs(s_g - 1.0), abs(s_n - 1.0)))
        sg_l.append(s_g - 1.0); sn_l.append(s_n - 1.0)
        prems += p1 + p2
    sg_all += sg_l; sn_all += sn_l
    rec_all += recs; spur_all += spurs; scale_all += scales; prem_all.append(prems)
    print(f"CELL cross-covariate noise={noise} gain_recovery_mean={np.mean(recs):.4f} "
          f"gain_recovery_range=[{min(recs):.4f},{max(recs):.4f}] gain_spurious_max_kw={max(spurs):.4f} "
          f"scale_err_max={max(scales):.4f} scale_bias_genuine_mean={np.mean(sg_l):+.4f} "
          f"scale_bias_nogain_mean={np.mean(sn_l):+.4f} premature_folds={prems} gain_folds_last={f1}", flush=True)
print(f"RESULT gain_recovery_mean={np.mean(rec_all):.4f} ratio")
print(f"RESULT gain_shortfall_mean={1 - np.mean(rec_all):.4f} ratio")
print(f"RESULT gain_spurious_max={max(spur_all):.4f} kW")
print(f"RESULT scale_err_max={max(scale_all):.4f} ratio")
print(f"RESULT scale_bias_genuine_mean={np.mean(sg_all):+.4f} ratio")
print(f"RESULT scale_bias_nogain_mean={np.mean(sn_all):+.4f} ratio")
print(f"RESULT gain_recovery_min={min(rec_all):.4f} ratio")
print(f"RESULT gain_recovery_max={max(rec_all):.4f} ratio")
print(f"RESULT premature_folds={sum(prem_all)} count")
footer()
