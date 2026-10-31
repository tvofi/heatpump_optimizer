"""R10 identifiability study, Q3: an honest "days until converged" per learner,
scored against the true convergence day on synthetic plants.

Metric (one line): eta_err_days = (checkpoint day + the estimator's ETA at that
checkpoint) - (the true settle day: first day after which the learner stays
within 10 % of its own fixed point, i.e. its value at day 42 +/- 10 % of the
distance it travelled), over 6 plants x checkpoints {1,2,3,5,7,10,14} d, for
the house scale, the lower-floor ratio, the solar aperture and the internal
gains, each with two estimators: COUNT (the learner's own EWMA law and its
sample rate) and STEP (remaining distance inferred from the mean recent step).
A second column scores the same ETAs against the TRUTH (plant value +/- 10 %).

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-ident/eta_rolling.py [--plants E1,E2] [--days 42]
Expected (measured, see REPORT.md): both ETAs UNDER-predict the settle day by
a median of ~3 weeks (p10..p90 about -37..-10 d) on an autumn trajectory --
the learners' targets move (season + coupling), which no count law sees.
Also printed: the SETTLED flag's false rate (flag up, value later leaves 2x tol).
Baseline SHA: a77faf30d. Machine: macOS arm64.

Instrumented symbols: the same learners ident_rolling.py drives
    (coordinator._async_learn_house_heat_loss / _async_learn_lower_floor_loss /
    _fold_solar_aperture / _fold_internal_gains / _refresh_model_corrections),
    plus coordinator:house_loss_confidence (the COUNT law's own constant).
Perturbation: --alpha-scale 2 (patches coordinator.HOUSE_LOSS_ALPHA x2): the
    COUNT law's n90 halves (114 -> 56) and its ETA with it, while the measured
    house settle day does NOT move earlier (noise doubles with the gain) --
    direction: the COUNT error grows more negative. --rel-tol 0.05 widens the
    settle band: settle days move earlier, errors shrink toward 0.
Null control: plant E0 (prior = truth everywhere): every learner's settle day
    is ~0 and every ETA must say ~0 ("nothing to learn"), not a count deficit.
Count key: values read from the coordinator attributes the learners write.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import timedelta  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ident_rolling as ir  # noqa: E402  (inserts tests/ and custom_components/)

import numpy as np  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer import const as const_mod  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

DT = ir.DT
#: name -> (UA truth/prior, lower ratio truth, aperture truth/model, mass factor, evening gains kW)
PLANTS = {
    "E0": (1.00, 1.00, 1.00, 1.0, 0.30),
    "E1": (1.50, 1.00, 1.50, 1.0, 0.60),
    "E2": (0.70, 1.40, 0.60, 1.0, 0.30),
    "E3": (1.20, 0.80, 2.00, 1.0, 0.60),
    "E4": (1.00, 1.50, 1.00, 1.0, 0.30),
    "E5": (1.40, 1.20, 1.30, 1.3, 0.50),
    "E6": (0.80, 1.00, 1.50, 0.8, 0.30),
}
CHECKPOINTS = (1, 2, 3, 5, 7, 10, 14)


def gains_profile(evening):
    return [evening if 17 <= h < 23 else 0.3 for h in range(24)]


def run(plant, days, seed, sigma=0.1):
    ua_err, lo_err, ap_err, mass, evening = PLANTS[plant]
    cfg = ir.base_cfg(mass)
    cfg["internal_gains"] = 0.3
    truth = ThermalParameters.from_config(dict(cfg, window_area=cfg["window_area"] * ap_err))
    truth.dhw_enabled = False
    truth.upper_floor_heat_loss *= ua_err
    truth.lower_floor_heat_loss *= ua_err * lo_err
    truth.internal_gains_profile = gains_profile(evening)
    plant_m = ThermalModel(truth)
    prior = ThermalParameters.from_config(cfg)
    prior_m = ThermalModel(prior)
    arm = ir.make_arm(cfg, 1.0, True, True)
    c = arm["coord"]
    t_out, irr = ir.make_weather("autumn", days, seed)
    rng = np.random.default_rng(seed + 1)
    total = int(days * 24 / DT)
    t_set = cfg["target_temperature"]
    state = ThermalState(room_temperature=t_set, slab_temperature=t_set + 1.0,
                         outdoor_temperature=float(t_out[0]), upper_floor_temperature=t_set,
                         lower_floor_temperature=t_set, buffer_tank_temperature=30.0)
    integ = 0.0
    rec = {k: [] for k in ("s", "r", "ap", "ap_n", "n", "n_lo", "g")}
    loop = asyncio.new_event_loop()
    for step in range(total):
        now = ir.START + timedelta(hours=step * DT)
        sensed_up = state.upper_floor_temperature + rng.normal(0.0, sigma)
        sensed_lo = state.lower_floor_temperature + rng.normal(0.0, sigma)
        e = t_set - sensed_up
        integ = float(np.clip(integ + 0.3 * e * DT, -2.0, 4.0))
        cop = prior_m.compute_cop(float(t_out[step]))
        ff = (prior.upper_floor_heat_loss + prior.lower_floor_heat_loss) * max(t_set - t_out[step], 0.0) / max(cop, 1.0)
        power = float(np.clip(ff + 1.5 * e + integ, 0.0, 5.5))
        seen = replace(state, room_temperature=sensed_up, upper_floor_temperature=sensed_up,
                       lower_floor_temperature=sensed_lo, outdoor_temperature=float(t_out[step]),
                       solar_radiation=float(irr[step]))
        dt_util.freeze(now)
        c._current_state = seen
        c._weather_forecast = [{"wind_speed": 0.0, "precipitation": 0.0}]
        loop.run_until_complete(c._async_learn_lower_floor_loss())
        loop.run_until_complete(c._async_learn_house_heat_loss())
        c._refresh_model_corrections()
        c._current_action = {"power": power, "dhw_power": 0.0}
        rec["s"].append(c._house_heat_loss_scale)
        rec["r"].append(c._lower_floor_loss_ratio)
        rec["ap"].append(c._solar_aperture["scale"])
        rec["ap_n"].append(c._solar_aperture["n"])
        rec["n"].append(c._house_heat_loss_samples)
        rec["n_lo"].append(c._lower_floor_loss_samples)
        prof = c._internal_gains_profile
        rec["g"].append(float(np.mean(prof[17:23])) if prof is not None else 0.3)
        state = plant_m.simulate_step(replace(state, solar_radiation=float(irr[step])), power,
                                      float(t_out[step]), wind_speed=0.0, precipitation=0.0,
                                      solar_radiation=float(irr[step]), dt_hours=DT,
                                      hour_of_day=now.hour + now.minute / 60.0)
    dt_util.freeze(None)
    loop.close()
    truth_vals = {"s": ua_err, "r": lo_err, "ap": ap_err, "g": evening}
    return {k: np.asarray(v, dtype=float) for k, v in rec.items()}, truth_vals, total


SPD = int(24 / DT)  # steps per day


def daily(series):
    n = len(series) // SPD
    return np.asarray(series[: n * SPD]).reshape(n, SPD).mean(axis=1)


def settle_day(series, target, start, rel_tol=0.03, abs_tol=0.0):
    """First day after which the DAILY MEAN stays within tol of `target`,
    tol = max(10 % of the travel |target - start|, rel_tol*|target|, abs_tol):
    the 3 % floor is the learners' own day-to-day noise at sigma = 0.1 K."""
    dm = daily(series)
    tol = max(0.10 * abs(target - start), rel_tol * abs(target), abs_tol)
    bad = np.where(np.abs(dm - target) > tol)[0]
    if len(bad) == 0:
        return 0.0
    if bad[-1] == len(dm) - 1:
        return float("nan")
    return float(bad[-1] + 1)


def count_eta(n_now, rate, n_needed):
    if n_now >= n_needed:
        return 0.0
    if rate <= 0:
        return float("inf")
    return (n_needed - n_now) / rate


def drift_eta(series, n, cday, gain, rel_tol=0.03, abs_tol=0.0):
    """DRIFT estimator: an EWMA closing on a target moves at v = dist/tau with
    tau = 1/(gain*rate) days, so the remaining distance is v*tau and the time
    to bring it inside tol is tau*ln(|v*tau|/tol). v is the slope of the last
    three daily means; tol = max(rel_tol*|value|, abs_tol). Needs no truth,
    no travel and no count: only what the learner has published."""
    dm = daily(series[: cday * SPD])
    if len(dm) < 3:
        return float("nan")
    v = float(np.polyfit(np.arange(3), dm[-3:], 1)[0])
    rate = (n[cday * SPD - 1] - n[max(0, (cday - 3) * SPD - 1)]) / 3.0
    if rate <= 0:
        return float("inf")
    tau = 1.0 / (gain * rate)
    remaining = abs(v) * tau
    tol = max(rel_tol * abs(dm[-1]), abs_tol)
    return 0.0 if remaining <= tol else tau * math.log(remaining / tol)


def score(rec, truth, total, days, rel_tol=0.03):
    out = {}
    end = total - 1
    a_h = coord_mod.HOUSE_LOSS_ALPHA          # already patched by --alpha-scale
    n90 = math.log(0.1) / math.log(1.0 - a_h)
    f_up = const_mod.DEFAULT_SOLAR_UPPER_FRACTION
    a_s = const_mod.SOLAR_APERTURE_ALPHA * f_up
    n90_s = const_mod.SOLAR_APERTURE_MIN_SAMPLES + math.log(0.1) / math.log(1.0 - a_s)
    # gains: g += a*y - ridge*(g - g0), y re-centred ~ upper-area share of the error
    a_g = const_mod.INTERNAL_GAINS_ALPHA * 0.5 + const_mod.INTERNAL_GAINS_RIDGE
    n90_g = math.log(0.1) / math.log(1.0 - a_g)
    gn = np.cumsum(np.ones(len(rec["g"]))) / 24.0   # folds per hour bucket (4/day at 15 min)
    learners = {
        "house": ("s", rec["n"], n90, a_h, 0.0),
        "lower": ("r", rec["n_lo"], n90, a_h, 0.0),
        "solar": ("ap", rec["ap_n"], n90_s, a_s, 0.0),
        "gains": ("g", gn, n90_g, a_g, 0.02),
    }
    for name, (xk, n, need, gain, abs_tol) in learners.items():
        x = rec[xk]
        fixed = float(np.mean(daily(x)[-3:]))          # its own end point (last 3 days)
        t_settle = settle_day(x, fixed, x[0], rel_tol=rel_tol, abs_tol=abs_tol)
        t_truth = settle_day(x, truth[xk], x[0], rel_tol=rel_tol, abs_tol=abs_tol)
        errs_c, errs_d, errs_ct, errs_dt, flags = [], [], [], [], []
        for cday in CHECKPOINTS:
            i = cday * SPD - 1
            if i >= end:
                continue
            rate = n[i] / cday
            eta_c = count_eta(n[i], rate, need)
            eta_d = drift_eta(x, n, cday, gain, rel_tol=rel_tol, abs_tol=abs_tol)
            if name == "solar" and n[i] < const_mod.SOLAR_APERTURE_MIN_SAMPLES:
                eta_d = eta_c
            # the SETTLED flag a card would show (drift ETA == 0 and the count
            # law traversed): false when the daily mean later leaves 2 x tol
            if eta_d == 0.0 and eta_c == 0.0:
                dm = daily(x)
                tol = max(rel_tol * abs(dm[cday - 1]), abs_tol)
                later = np.abs(dm[cday:] - dm[cday - 1]).max() if cday < len(dm) else 0.0
                flags.append(bool(later > 2 * tol))
            for t_ref, ec, ed in ((t_settle, errs_c, errs_d), (t_truth, errs_ct, errs_dt)):
                if not math.isnan(t_ref) and cday < t_ref:
                    ec.append(cday + eta_c - t_ref)
                    if np.isfinite(eta_d):
                        ed.append(cday + eta_d - t_ref)
        out[name] = {"settle_day": t_settle, "truth_day": t_truth, "fixed": fixed, "truth": truth[xk],
                     "samples_per_day": float(n[end] / days), "n90": need,
                     "err_count": errs_c, "err_drift": errs_d,
                     "err_count_vs_truth": errs_ct, "err_drift_vs_truth": errs_dt,
                     "settled_flags": len(flags), "false_settled": int(sum(flags))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plants", default=",".join(PLANTS))
    ap.add_argument("--days", type=float, default=42.0)
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--alpha-scale", type=float, default=1.0)
    ap.add_argument("--rel-tol", type=float, default=0.03)
    a = ap.parse_args()
    if a.alpha_scale != 1.0:
        coord_mod.HOUSE_LOSS_ALPHA = coord_mod.HOUSE_LOSS_ALPHA * a.alpha_scale
    c0, t0, w0 = time.process_time(), time.thread_time(), time.time()
    metrics = ("err_count", "err_drift", "err_count_vs_truth", "err_drift_vs_truth")
    pooled = {k: {m: [] for m in metrics} for k in ("house", "lower", "solar", "gains")}
    flag_tot = {k: [0, 0] for k in pooled}
    for p in a.plants.split(","):
        rec, truth, total = run(p, a.days, a.seed)
        sc = score(rec, truth, total, a.days, a.rel_tol)
        for k, v in sc.items():
            print(f"RESULT {p}.{k}.settle_day={v['settle_day']:.1f} truth_day={v['truth_day']:.1f} "
                  f"fixed={v['fixed']:.3f} truth={v['truth']:.3f} "
                  f"samples_per_day={v['samples_per_day']:.1f} n90={v['n90']:.0f} "
                  f"settled_flags={v['settled_flags']} false_settled={v['false_settled']}")
            flag_tot[k][0] += v["settled_flags"]
            flag_tot[k][1] += v["false_settled"]
            for m in metrics:
                if v[m]:
                    pooled[k][m].append((p, v[m]))
                    print(f"RESULT {p}.{k}.{m}=" + ",".join(f"{e:+.1f}" for e in v[m]))
    for k, d in pooled.items():
        for m, lst in d.items():
            allv = [e for _, v in lst for e in v if np.isfinite(e)]
            if len(allv) < 3:
                continue
            p10, p50, p90 = np.percentile(allv, (10, 50, 90))
            # leave-one-plant-out: the band with the single most favourable plant dropped
            per = {p: float(np.mean(np.abs([e for e in v if np.isfinite(e)]))) for p, v in lst if any(np.isfinite(v))}
            best = min(per, key=per.get) if per else None
            rest = [e for p, v in lst if p != best for e in v if np.isfinite(e)]
            loo = np.percentile(rest, (10, 50, 90)) if len(rest) >= 3 else (float("nan"),) * 3
            print(f"RESULT pooled.{k}.{m}.p10={p10:+.1f} p50={p50:+.1f} p90={p90:+.1f} n={len(allv)} "
                  f"plants={len(lst)} loo_drop={best} loo_p10={loo[0]:+.1f} loo_p50={loo[1]:+.1f} loo_p90={loo[2]:+.1f}")
    for k, (nf, bad) in flag_tot.items():
        print(f"RESULT pooled.{k}.settled_flags={nf} false_settled={bad} "
              f"false_rate={(bad / nf) if nf else float('nan'):.2f}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT wall_s={time.time() - w0:.1f}")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a(macOS)")


if __name__ == "__main__":
    main()
