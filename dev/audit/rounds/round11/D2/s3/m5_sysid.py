"""D2.M5 sysid-bias: the production fit (SystemIdentification.identify_slab,
the fit every production experiment runs) and its adoption gate
(sysid.adoption_decision) under white, quantised and drifting sensor noise,
over a plant grid.

The true plant is the fit's own candidate class (sysid._candidate_model, rolled
by sysid._valve_drive at SYSID_ROLLOUT_STEP_HOURS), single-zone, so a
noise-free window must be recovered exactly (the null control). The declared
plant the experiment is armed with carries the CONFIGURED UA (scale 1); the
truth carries scale s_true in {0.8, 1.0, 1.25} and room capacity x{0.7, 1.4}.
Protocol: 1 h settle at the hold power, 2 h step at hold+3 kW thermal, 2 h relax
at 0, sampled every 10 min; outdoor 0 C; 40 seeds per cell.

Metric definitions (one line each):
  bias         = UA_fit / UA_true - 1 for a fit adoption_decision admits
  miss_rate    = share of admitted fits whose |log(UA_fit/UA_true)| exceeds the
                 half-width the gate admitted it on (slab_ua_adoption_halfwidth),
                 i.e. the 95 % interval's non-coverage; nominal 0.05
  over_bar     = share of admitted fits with |bias| > 10 % (the bar's claim)
  weighted_bias= decision.weight * bias, the error the coordinator's blend
                 ((1-w)*scale + w*fit) carries into house_heat_loss_scale from a learner at the truth
Count key: the result's heat_loss_kw_per_c and the decision's admit, both
delivered by production.

Run:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D2/s3/m5_sysid.py [--seeds N]
Perturbation: --perturb-bar5 sets sysid.UA_ADOPTION_HALFWIDTH_BAR to log(1.05):
  admitted counts must go down in every noisy cell.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, machine B6 (shared).
"""
import _common  # noqa: F401
from _common import footer, np

import argparse
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "custom_components")
import harness  # noqa: F401,E402
from heatpump_optimizer import sysid  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=40)
ap.add_argument("--perturb-bar5", action="store_true")
A = ap.parse_args()
if A.perturb_bar5:
    sysid.UA_ADOPTION_HALFWIDTH_BAR = float(np.log(1.05))

declared = ThermalParameters()
UA0 = declared.heat_loss_coefficient * declared.house_heat_loss_scale
CR0 = declared.room_thermal_mass
CS, KS = declared.slab_thermal_mass, declared.slab_heat_transfer
OUT = 0.0
CAD = 10.0 / 60.0
T0 = datetime(2026, 1, 20, 23, 0, tzinfo=timezone.utc)


def truth_series(s_true, cr_mult, gains):
    ua, cr = UA0 * s_true, CR0 * cr_mult
    model = sysid._candidate_model(ua, cr, gains, CS, KS, None)
    state = sysid._held_state(model, 21.0, OUT)
    hold = max(ua * (21.0 - OUT) - gains, 0.0)
    plan = [(sysid.PHASE_SETTLING, hold, 6), (sysid.PHASE_STEP, hold + 3.0, 12), (sysid.PHASE_RELAX, 0.0, 12)]
    rows, t = [], 0.0
    for phase, q, n in plan:
        for _ in range(n):
            rows.append((t, state.room_temperature, q, phase))
            sub = int(np.ceil(CAD / sysid.SYSID_ROLLOUT_STEP_HOURS - 1e-9))
            for _ in range(sub):
                state = sysid._valve_drive(model, state, q, OUT, CAD / sub)
            t += CAD
    rows.append((t, state.room_temperature, 0.0, sysid.PHASE_RELAX))
    return rows, ua


def noisy(rows, kind, rng):
    out = []
    for t, room, q, ph in rows:
        if kind.startswith("white"):
            r = room + rng.normal(0, float(kind.split("_")[1]))
        elif kind == "quantised_0.1C":
            r = np.round((room + rng.uniform(-0.05, 0.05)) * 10.0) / 10.0
        elif kind == "drifting":
            r = room + 0.05 * t + rng.normal(0, 0.005)
        else:
            r = room
        out.append(sysid.SysIdSample(T0 + timedelta(hours=t), float(r), OUT, q, ph))
    return out


def fit(samples):
    si = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
    si._slab_pair = (CS, KS)
    si._slab_prior = (UA0, CR0)
    si.config.gains_prior_kw = 0.3
    si.samples = samples
    res = si.identify_slab()
    dec = sysid.adoption_decision(res, declared, si.config)
    hw = sysid.slab_ua_adoption_halfwidth(res.ua_profile_halfwidth, res.ua_prior_halfwidth,
                                          res.ua_told_halfwidth) if res.completed else None
    return res, dec, hw


rng = np.random.default_rng(2611)
rows_out = []
grand = {"adm": 0, "miss": 0, "over": 0}
for kind in ("none", "white_0.005", "white_0.02", "white_0.05", "quantised_0.1C", "drifting"):
    for s_true in (0.8, 1.0, 1.25):
        for cr_mult in (0.7, 1.4):
            truth, ua_true = truth_series(s_true, cr_mult, 0.3)
            biases, misses, adm, completed, cb, hws, wbias = [], 0, 0, 0, [], [], []
            seeds = 1 if kind == "none" else A.seeds
            for _ in range(seeds):
                res, dec, hw = fit(noisy(truth, kind, rng))
                completed += res.completed
                if res.completed:
                    cb.append(res.heat_loss_kw_per_c / ua_true - 1.0)
                    hws.append(hw if hw is not None else np.nan)
                if dec.admit:
                    adm += 1
                    lb = float(np.log(res.heat_loss_kw_per_c / ua_true))
                    biases.append(res.heat_loss_kw_per_c / ua_true - 1.0)
                    misses += abs(lb) > hw
                    wbias.append(dec.weight * (res.heat_loss_kw_per_c / ua_true - 1.0))
            b = np.array(biases) if biases else np.array([np.nan])
            over = int(np.sum(np.abs(b) > 0.10)) if biases else 0
            if kind != "none":
                grand["adm"] += adm
                grand["miss"] += misses
                grand["over"] += over
            rows_out.append((kind, s_true, cr_mult, adm, seeds, misses, over, b, wbias))
            print(f"CELL sysid-bias noise={kind} s_true={s_true} cr_mult={cr_mult} completed={completed}/{seeds} "
                  f"admitted={adm}/{seeds} miss_rate={misses / adm if adm else float('nan'):.3f} "
                  f"over_bar={over}/{adm} bias_median={np.nanmedian(b):+.4f} bias_min={np.nanmin(b):+.4f} "
                  f"bias_max={np.nanmax(b):+.4f} completed_bias_median={np.median(cb) if cb else np.nan:+.4f} "
                  f"completed_absbias_max={np.max(np.abs(cb)) if cb else np.nan:.4f} hw_median={np.nanmedian(hws) if hws else np.nan:.4f} "
                  f"weighted_bias_max={max(wbias, key=abs) if wbias else float('nan'):+.4f}", flush=True)

for kind in ("white_0.005", "white_0.02", "white_0.05", "quantised_0.1C", "drifting"):
    sel = [r for r in rows_out if r[0] == kind]
    adm = sum(r[3] for r in sel)
    miss = sum(r[5] for r in sel)
    over = sum(r[6] for r in sel)
    allb = np.concatenate([r[7] for r in sel if r[3]]) if adm else np.array([np.nan])
    print(f"RESULT {kind}_admitted={adm} count")
    print(f"RESULT {kind}_miss_rate={miss / adm if adm else float('nan'):.3f} ratio")
    print(f"RESULT {kind}_over_bar={over} count")
    wb = [w for r in sel for w in r[8]]
    print(f"RESULT {kind}_misses={miss} count")
    print(f"RESULT {kind}_weighted_abs_bias_max={(max(abs(w) for w in wb) if wb else float('nan')):.4f} ratio")
    print(f"RESULT {kind}_abs_bias_max={(np.nanmax(np.abs(allb)) if adm else float('nan')):.4f} ratio")
null = [r for r in rows_out if r[0] == "none"]
print(f"RESULT null_abs_bias_max={max(float(np.nanmax(np.abs(r[7]))) for r in null):.2e} ratio")
footer()
