"""R10 identifiability study: the owner's live bundle, read by path, never copied.

Metric (one line, four numbers): (a) the joint OLS of the accuracy residual
(actual - predicted indoor, degC) on [clear-sky irradiance proxy, dT, power gap
(asked - metered kW), 1] -- coefficients, t-values, condition number;
(b) the energy-balance house UA = mean(metered kW x model COP(outdoor) - DHW
share + internal gains) / mean(indoor - outdoor), W/K, against the learned one;
(c) the share of metered intervals the house learner's tracking gate
(coordinator._interval_space_power) and the COP learner's gates
(accuracy.MeasuredCop.judge_floor / judge_ratio) let through, per 3-degC bin
and per day; (d) the learners' trajectory from the snapshot ring.

Command (repository root; the bundle is PRIVATE -- pass its path, never commit it):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-ident/owner_rows.py PATH/TO/diag.json
Expected: see the study REPORT.md (values are the owner's, so the expected
value is the bundle's own, re-derivable by anyone holding it).
Baseline SHA: a77faf30d. Machine: macOS arm64.

Instrumented symbols:
    heatpump_optimizer.thermal_model:ThermalParameters.from_config (the owner's own config)
    heatpump_optimizer.thermal_model:ThermalModel.compute_cop
    heatpump_optimizer.accuracy:MeasuredCop.judge_floor, MeasuredCop.judge_ratio
    heatpump_optimizer.defrost:in_frost_band
    heatpump_optimizer.coordinator:COP_TRACKING_ERROR_GATE (the house learner's tracking gate)
Perturbation: --min-power 0.3 (the owner's configured heat_pump_min_power set to
    the metered running floor) must raise the COP duty-floor pass share from
    ~0 (direction: up), because judge_floor reads flow_lift_power_floor_kw =
    0.8 x min power. --cop-scale 0.5 halves model COP and must halve UA_eb.
Null control: the clear-sky proxy is regressed on night-time samples only
    (irradiance identically 0 there): its column vanishes and the dT/power
    coefficients must not depend on it.
Count key: the accuracy store's own samples (`actual_power_kw` is the metered
    figure the coordinator held at the sample, `predicted_power_kw` the plan's
    ask for that interval) -- the values the production seams delivered.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import collections  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from heatpump_optimizer.accuracy import MeasuredCop  # noqa: E402
from heatpump_optimizer.coordinator import COP_TRACKING_ERROR_GATE, HOUSE_LOSS_MIN_DELTA  # noqa: E402
from heatpump_optimizer.const import COP_BASELINE_MIN_SAMPLES  # noqa: E402
from heatpump_optimizer.defrost import in_frost_band  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters  # noqa: E402

LAT, LON = 60.1, 17.0


def clear_sky(ts):
    """Haurwitz clear-sky GHI at the owner's site, W/m2 (solar time from UTC + lon)."""
    t = ts.astimezone(timezone.utc)
    doy = t.timetuple().tm_yday
    hour = t.hour + t.minute / 60.0 + LON / 15.0
    decl = math.radians(23.45) * math.sin(2 * math.pi * (284 + doy) / 365.0)
    ha = math.radians(15.0 * (hour - 12.0))
    phi = math.radians(LAT)
    s = math.sin(phi) * math.sin(decl) + math.cos(phi) * math.cos(decl) * math.cos(ha)
    return 0.0 if s <= 0.01 else 1098.0 * s * math.exp(-0.057 / s)


def ols(X, y, names):
    X, y = np.asarray(X, float), np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    s2 = float(r @ r) / max(len(y) - X.shape[1], 1)
    cov = s2 * np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    Xs = X / np.maximum(np.linalg.norm(X, axis=0), 1e-12)
    return {n: (float(b), float(b / s) if s > 0 else float("nan")) for n, b, s in zip(names, beta, se)}, float(np.linalg.cond(Xs)), len(y)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--min-power", type=float, default=None)
    ap.add_argument("--cop-scale", type=float, default=1.0)
    ap.add_argument("--t-mean", type=float, default=6.0, help="outdoor daily mean at the bundle's end, degC")
    ap.add_argument("--t-slope", type=float, default=-0.12, help="degC/day, the season's fall (climatology ~60N Oct->Dec)")
    ap.add_argument("--t-spread", type=float, default=3.0, help="sd of interval outdoor T about the daily mean")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    d = json.load(open(a.bundle))["data"]
    cfg = dict(d["config"])
    if a.min_power is not None:
        cfg["heat_pump_min_power"] = a.min_power
    p = ThermalParameters.from_config(cfg)
    p.cop_scale = a.cop_scale
    m = ThermalModel(p)
    stores = d["debug"]["stores"]
    key = next(k for k in stores if k.endswith("_thermal_learning"))
    tl = stores[key]
    acc = stores[next(k for k in stores if k.endswith("_accuracy"))]["accuracy"]["samples"]
    snaps = stores[next(k for k in stores if k.endswith("_snapshots"))]["snapshots"]

    # (d) trajectory
    u_up, u_lo = p.upper_floor_heat_loss, p.lower_floor_heat_loss
    for s in snaps + [{"taken_at": tl["updated_at"], "learners": {"thermal_learning": tl}}]:
        t = s["learners"]["thermal_learning"]
        sc, r = t["house_heat_loss_scale"], t["lower_floor_loss_ratio"]
        two = r != 1.0 or t["lower_floor_loss_samples"] > 0
        eff = (u_up + u_lo * r) * sc if two else (u_up + u_lo) * sc
        print(f"RESULT traj.{s['taken_at'][:10]}.ua_eff_w_per_k={eff * 1000:.1f} scale={sc:.3f} "
              f"n={t['house_heat_loss_samples']} ratio={r:.3f} n_lo={t['lower_floor_loss_samples']} "
              f"solar_n={t['solar_aperture']['n']:.0f}")
    ap_m = tl["solar_aperture"]
    slope = ap_m["cov"] / ap_m["var"] if ap_m["var"] > 1e-9 else float("nan")
    print(f"RESULT solar.n={ap_m['n']:.0f} pending_slope={slope:.3f} my_kw={ap_m['my']:.3f}")

    # the open-window detector's trips: every learner (the solar fold included,
    # which sits after the vent-only return) is frozen while tripped
    ev = tl.get("vent_cusum", {}).get("evidence", [])
    trips, frozen_h, t_on = [], 0.0, None
    for line in ev:
        ts = datetime.fromisoformat(line.split(": ", 1)[0])
        if "tripped" in line:
            t_on = ts
        elif "released" in line and t_on is not None:
            frozen_h += (ts - t_on).total_seconds() / 3600.0
            trips.append((t_on, ts))
            t_on = None
    if ev:
        span_h = (datetime.fromisoformat(tl["updated_at"]) - datetime.fromisoformat(ev[0].split(": ", 1)[0])).total_seconds() / 3600.0
        print(f"RESULT vent.trips={len(trips) + (t_on is not None)} frozen_h={frozen_h:.1f} of {span_h:.1f} h "
              f"share={frozen_h / span_h:.2f} still_tripped={t_on is not None or tl['vent_cusum'].get('tripped')}")

    rows = []
    for s in acc:
        ts = datetime.fromisoformat(s["t"])
        rows.append({
            "ts": ts, "day": ts.date().isoformat(),
            "res": None if s["predicted_temp"] is None or s["actual_temp"] is None else s["actual_temp"] - s["predicted_temp"],
            "dT": None if s["actual_temp"] is None else s["actual_temp"] - s["outdoor_temp"],
            "out": float(s["outdoor_temp"]), "hum": s.get("humidity"),
            "ask": s["predicted_power_kw"], "drawn": s["actual_power_kw"],
            "irr": clear_sky(ts),
        })
    print(f"RESULT acc.samples={len(rows)} first={rows[0]['ts'].isoformat()} last={rows[-1]['ts'].isoformat()}")
    metered = [r for r in rows if r["drawn"] is not None and r["ask"] is not None]
    print(f"RESULT acc.metered={len(metered)}")

    # (a) joint regression of the residual
    full = [r for r in metered if r["res"] is not None and r["dT"] is not None]
    X = [(r["irr"] / 100.0, r["dT"], r["ask"] - r["drawn"], 1.0) for r in full]
    y = [r["res"] for r in full]
    co, cond, n = ols(X, y, ("irr_per_100Wm2", "dT", "power_gap_kw", "const"))
    for k, (b, tv) in co.items():
        print(f"RESULT joint.{k}={b:+.4f} t={tv:+.2f}")
    print(f"RESULT joint.cond={cond:.2f} n={n}")
    night = [r for r in full if r["irr"] == 0.0]
    co_n, cond_n, n_n = ols([(r["dT"], r["ask"] - r["drawn"], 1.0) for r in night], [r["res"] for r in night],
                            ("dT", "power_gap_kw", "const"))
    for k, (b, tv) in co_n.items():
        print(f"RESULT joint_night.{k}={b:+.4f} t={tv:+.2f}")
    print(f"RESULT joint_night.n={n_n} sunny_proxy_samples={sum(1 for r in full if r['irr'] >= 150.0)}")
    allres = [r["res"] for r in rows if r["res"] is not None]
    print(f"RESULT acc.mean_residual_c={np.mean(allres):+.3f} n={len(allres)}")

    # (b) energy balance UA (metered period; steady over days, storage term ~0)
    heat = [r["drawn"] * m.compute_cop(r["out"], humidity=r["hum"]) for r in metered]
    dts = [r["dT"] for r in metered if r["dT"] is not None]
    dhw_kw = (cfg["dhw_daily_consumption"] * (cfg["dhw_setpoint"] - cfg["dhw_inlet_temp"]) * 1.163e-3
              + tl.get("dhw_cooling_rate", 0.62) * 0) / 24.0
    gains = p.internal_gains
    q_mean = float(np.mean(heat))
    ua_raw = q_mean / float(np.mean(dts))
    ua_net = (q_mean - dhw_kw + gains) / float(np.mean(dts))
    learned = (u_up + u_lo * tl["lower_floor_loss_ratio"]) * tl["house_heat_loss_scale"]
    print(f"RESULT eb.mean_metered_kw={np.mean([r['drawn'] for r in metered]):.3f} mean_ask_kw={np.mean([r['ask'] for r in metered]):.3f}")
    print(f"RESULT eb.power_ratio={np.mean([r['drawn'] for r in metered]) / max(np.mean([r['ask'] for r in metered]), 1e-9):.3f}")
    print(f"RESULT eb.mean_heat_kw={q_mean:.3f} mean_dT={np.mean(dts):.2f} dhw_heat_kw={dhw_kw:.3f} gains_kw={gains:.3f}")
    print(f"RESULT eb.ua_raw_w_per_k={ua_raw * 1000:.1f}")
    print(f"RESULT eb.ua_net_w_per_k={ua_net * 1000:.1f}")
    print(f"RESULT eb.ua_learned_w_per_k={learned * 1000:.1f} ua_configured_w_per_k={(u_up + u_lo) * 1000:.1f}")
    print(f"RESULT eb.learned_over_eb={learned / ua_net:.3f}")

    # (c) gates per interval
    hl_pass = sum(1 for r in metered if abs(r["drawn"] - r["ask"]) / max(r["ask"], 0.5) <= COP_TRACKING_ERROR_GATE)
    print(f"RESULT gate.house_tracking_pass={hl_pass}/{len(metered)}")
    reasons = collections.Counter()
    per_bin_day = collections.defaultdict(collections.Counter)
    ewma = 1.0
    for r in metered:
        if r["ask"] <= 0.0 and r["drawn"] <= 0.25:
            reasons["off"] += 1
            continue
        why = MeasuredCop.judge_floor(r["ask"], r["drawn"], p)
        if why is None:
            if in_frost_band(r["out"]):
                why = "frost_band(if_defrost)"
        if why is None:
            ratio = r["drawn"] / max(r["ask"], 1e-6)
            prev, ewma = ewma, 0.9 * ewma + 0.1 * ratio
            why = MeasuredCop.judge_ratio(ratio, prev, r["ask"], p, None)
        reasons[why or "FOLDS"] += 1
        if why is None and abs(r["drawn"] / max(r["ask"], 1e-6) - 1.0) <= 0.15:
            reasons["FOLDS_within_ask_tolerance"] += 1
        if why is None:
            per_bin_day[int(math.floor(r["out"] / 3.0))][r["day"]] += 1
    print(f"RESULT cop.power_floor_kw={p.flow_lift_power_floor_kw:.2f} nameplate_floor_kw={p.nameplate_power_floor_kw:.2f}")
    for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"RESULT cop.refusal.{k}={v}")
    days = sorted({r["day"] for r in metered})
    span_days = (metered[-1]["ts"] - metered[0]["ts"]).total_seconds() / 86400.0
    print(f"RESULT cop.metered_span_days={span_days:.2f} metered_days={len(days)}")
    stored = tl.get("cop_baseline", {})
    print(f"RESULT cop.stored_baseline={json.dumps(stored)} cop_samples={tl.get('cop_samples')}")
    for b, cnt in sorted(per_bin_day.items()):
        tot = sum(cnt.values())
        rate = tot / max(span_days, 1e-9)
        eta = (COP_BASELINE_MIN_SAMPLES - tot) / rate if rate > 0 else float("inf")
        print(f"RESULT cop.bin[{b * 3},{b * 3 + 3}).folds={tot} per_day={rate:.2f} eta_days_to_{COP_BASELINE_MIN_SAMPLES}={eta:.1f}")
    # ETA to COP_BASELINE_MIN_SAMPLES per 3-degC bin under a falling season:
    # the fold rate R/day (production's stored count over the metered span, and
    # this replay's count) is spread over bins by N(T(d), spread); T(d) = mean + slope*d
    from math import erf
    def share(b, mu, sd):
        cdf = lambda x: 0.5 * (1 + erf((x - mu) / (sd * math.sqrt(2))))
        return cdf(3 * b + 3) - cdf(3 * b)
    n_replay = sum(sum(c.values()) for c in per_bin_day.values())
    for label, rate in (("production", (tl.get("cop_samples") or 0) / max(span_days, 1e-9)),
                        ("replay", n_replay / max(span_days, 1e-9))):
        counts = collections.Counter({int(k): int(v[1]) for k, v in stored.items()})
        first, reached = None, {}
        for day in range(1, 366):
            mu = a.t_mean + a.t_slope * day
            for b in range(-10, 6):
                counts[b] += rate * share(b, mu, a.t_spread)
                if counts[b] >= COP_BASELINE_MIN_SAMPLES and b not in reached:
                    reached[b] = day
                    first = first or day
            if day == 120:
                break
        print(f"RESULT cop.eta.{label}.rate_per_day={rate:.2f} first_bin_day={first} "
              f"bins_reached_by_day120={sorted((b * 3, d) for b, d in reached.items())}")
    # does the draw follow the ask at all? draw_range's own evidence, fed the
    # metered running pairs (accuracy rows, ask > 0, drawn above standby)
    from heatpump_optimizer import draw_range as dr
    rng_ = dr.DrawRange()
    for r in metered:
        if dr.is_running_space(r["drawn"], r["ask"], 0.0, frozen=False, distorted=False, defrost=False):
            rng_.observe(r["drawn"], r["ask"], p.min_electrical_power, p.max_electrical_power)
    pairs = np.asarray([(dd, aa) for dd, aa in rng_.samples if aa > 0], float).reshape(-1, 2)
    slope = float("nan")
    if len(pairs) >= 3 and np.std(np.log(pairs[:, 1])) > 0:
        la = np.log(pairs[:, 1]) - np.log(pairs[:, 1]).mean()
        slope = float(la @ (np.log(pairs[:, 0]) - np.log(pairs[:, 0]).mean()) / (la @ la))
    asks = pairs[:, 1] if len(pairs) else np.asarray([0.0])
    print(f"RESULT follow.running_pairs={len(pairs)} (MIN_SAMPLES {dr.MIN_SAMPLES}) follows_ask={dr.follows_ask(rng_)} "
          f"ask_span_p90_over_p10={np.percentile(asks, 90) / max(np.percentile(asks, 10), 1e-9):.2f} "
          f"(needs {dr.FOLLOW_ASK_SPAN}) loglog_slope={slope:.2f} (follows at >= {dr.FOLLOW_SLOPE_MIN})")
    # once draw_range HAS its evidence and it says the draw does not follow the
    # ask (the owner's slope is 0.37 < 0.5): how many of the same intervals
    # would still fold? Evidence built from the owner's own running pairs,
    # repeated to MIN_SAMPLES (their slope, not a synthetic one).
    ev_rng = dr.DrawRange()
    k = 0
    while dr.follows_ask(ev_rng) is None and len(pairs) and k < 20 * dr.MIN_SAMPLES:
        dd, aa = pairs[k % len(pairs)]
        ev_rng.observe(float(dd), float(aa), p.min_electrical_power, p.max_electrical_power)
        k += 1
    ev_follows = dr.follows_ask(ev_rng)
    folds_no_follow, in_band = 0, 0
    ewma = 1.0
    for r in metered:
        if r["ask"] <= 0.0 and r["drawn"] <= 0.25:
            continue
        if MeasuredCop.judge_floor(r["ask"], r["drawn"], p) is not None:
            continue
        ratio = r["drawn"] / max(r["ask"], 1e-6)
        prev, ewma = ewma, 0.9 * ewma + 0.1 * ratio
        if MeasuredCop.judge_ratio(ratio, prev, r["ask"], p, ev_rng) is None:
            folds_no_follow += 1
            in_band += int(abs(ratio - 1.0) <= 0.15)
    print(f"RESULT cop.with_evidence.follows_ask={ev_follows} folds={folds_no_follow} "
          f"of_which_within_ask_tolerance={in_band}")
    # the sample counts by draw level, for the floor question
    draws = np.asarray([r["drawn"] for r in metered if r["drawn"] > 0.25])
    if len(draws):
        print(f"RESULT draw.running_n={len(draws)} p10={np.percentile(draws, 10):.2f} p50={np.percentile(draws, 50):.2f} "
              f"p90={np.percentile(draws, 90):.2f} share_ge_floor={np.mean(draws >= p.flow_lift_power_floor_kw):.3f}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a(macOS)")


if __name__ == "__main__":
    main()
