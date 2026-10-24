"""Reseed study (R10, owner question 2026-10-14): does resetting the settings'
estimate (the prior) to the learned value make the heat-loss learners steadier?

Metric (one line): over the window after a reseed, the std (W/K) and the RMSE
against the plant's truth (W/K) of the effective house UA and lower-zone UA the
real coordinator learners publish, and the 12-h open-loop forecast MAE (degC) of
each arm's model on the shared closed-loop trajectory; arms compared pairwise
on common random numbers.

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-reseed/reseed_rolling.py \
        [--plant NAME] [--sigma 0.1] [--trust-region X] [--days 10]
Expected: see REPORT.md in the study scratch; arm B (reseed) vs A (none) std
ratio ~1.0 on the null plant, != 1 where the prior was wrong.
Baseline SHA: 17f1c55fa (origin/main, v7.0.0). Machine: macOS arm64, Python 3.11.

Template: tests/rolling.py:run_rolling(learn=True) -- the same plant/optimizer
loop, re-written here (rolling.py runs its checks at import and sys.exits)
with three changes: a reseed hook, several learner coordinators observing the
ONE closed-loop trajectory (paired arms, common random numbers), and Gaussian
sensor noise on what the learners read.

Instrumented symbols:
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_lower_floor_loss
    heatpump_optimizer.thermal_model:learner_newton_step (via both)
    heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize (closed loop)
Perturbation: --trust-region 1e9 (patches coordinator._LEARNER_TRUST_REGION):
    the only factorisation-dependent term of the step vanishes, so the B/A std
    and RMSE ratios must collapse to 1.000 (the reseed becomes an exact
    re-parameterisation). Direction: |ratio-1| decreases to ~0.
Null control: plant 'sz_null' / 'tz_null' -- the prior is already right, so a
    reseed moves nothing (ratios ~1.000).
Count key: values are read from the coordinator attributes the learners write
    (_house_heat_loss_scale, _lower_floor_loss_ratio) times the arm's own
    ThermalParameters bases -- the value the production seam delivers.
The arms' `_learning_frozen` is patched to None for every arm alike: the
    harness has no Home Assistant states, and the lower-floor learner needs a
    configured sensor key; the freeze logic is not under study.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from profiles import DT, house, prices, solve_inputs, weather  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

START = datetime(2026, 1, 15, 0, 0)

#: name -> (two_zone, house error truth/prior, extra lower-zone error, weather)
PLANTS = {
    "sz_157": (False, 1.57, 1.0, "winter_cold"),
    "sz_060": (False, 0.60, 1.0, "winter_cold"),
    "sz_250": (False, 2.50, 1.0, "winter_cold"),
    "sz_157_mild": (False, 1.57, 1.0, "winter_mild"),
    "tz_157_192": (True, 1.57, 1.92, "winter_cold"),
    "tz_120_150": (True, 1.20, 1.50, "winter_cold"),
    "sz_null": (False, 1.00, 1.0, "winter_cold"),
    "tz_null": (True, 1.00, 1.0, "winter_cold"),
}


def tile(series, steps):
    a = np.asarray(series, dtype=float)
    return a[:steps] if len(a) >= steps else np.tile(a, int(np.ceil(steps / len(a))))[:steps]


def base_terms(p):
    """(house-total base, lower base) the arm's learned multipliers apply to."""
    if p.two_zone_enabled:
        return p.upper_floor_heat_loss, p.lower_floor_heat_loss
    return p.heat_loss_coefficient, 0.0


def effective(arm):
    """Effective (house-total UA, lower-zone UA), kW/K, as the model applies them."""
    p, c = arm["params"], arm["coord"]
    s = c._house_heat_loss_scale
    if p.two_zone_enabled:
        r = c._lower_floor_loss_ratio
        return (p.upper_floor_heat_loss + p.lower_floor_heat_loss * r) * s, p.lower_floor_heat_loss * r * s
    return p.heat_loss_coefficient * s, 0.0


def make_arm(cfg):
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    m = ThermalModel(p)
    c._thermal_params = p
    c._thermal_model = m
    c._learning_frozen = lambda *keys: None  # same for every arm; see header
    return {"coord": c, "params": p, "model": m}


def reseed(arm, keep_samples=True):
    """prior := learned. The effective UA is unchanged by construction."""
    p, c = arm["params"], arm["coord"]
    s = c._house_heat_loss_scale
    r = c._lower_floor_loss_ratio
    p.heat_loss_coefficient *= s
    if p.two_zone_enabled:
        p.upper_floor_heat_loss *= s
        p.lower_floor_heat_loss *= s * r
    c._apply_house_heat_loss_scale(1.0)
    c._apply_lower_floor_loss_ratio(1.0)
    if not keep_samples:
        c._house_heat_loss_samples = 0
        c._lower_floor_loss_samples = 0


def reset_to_prior(arm):
    """A learner state lost (store gone, re-created entry): back to the prior."""
    c = arm["coord"]
    c._apply_house_heat_loss_scale(1.0)
    c._apply_lower_floor_loss_ratio(1.0)
    c._house_heat_loss_samples = 0
    c._lower_floor_loss_samples = 0


def run(plant, sigma, days, reseed_day, reset_day, replan_hours, seed):
    two_zone, err, err_lower, wprof = PLANTS[plant]
    cfg = house(two_zone=two_zone, dhw=False)
    if two_zone:
        cfg["lower_floor_temp_entity"] = "sensor.lower_floor"
    truth_p = ThermalParameters.from_config(cfg)
    truth_p.dhw_enabled = False
    truth_p.heat_loss_coefficient *= err
    truth_p.upper_floor_heat_loss *= err
    truth_p.lower_floor_heat_loss *= err * err_lower
    plant_m = ThermalModel(truth_p)
    if two_zone:
        true_house = truth_p.upper_floor_heat_loss + truth_p.lower_floor_heat_loss
        true_lower = truth_p.lower_floor_heat_loss
    else:
        true_house, true_lower = truth_p.heat_loss_coefficient, 0.0

    # Arms: A none | B reseed (samples kept) | C reseed + samples reset
    #       E none, then a reset to the prior | F reseed, then the same reset
    arms = {k: make_arm(cfg) for k in "ABCEF"}
    opt_cfg = OptimizationConfig(horizon_hours=24, time_step_minutes=15,
                                 target_temp=cfg["target_temperature"],
                                 min_temp=cfg["min_temperature"], max_temp=cfg["max_temperature"])
    optimizer = HeatPumpOptimizer(arms["A"]["model"], opt_cfg)  # run_rolling: the learner's own model plans

    total = int(days * 24 / DT)
    span = total + int(24 / DT) + 4
    price = tile(prices("winter_typical", START), span)
    outdoor, wind, rain, solar = (tile(a, span) for a in weather(wprof, START))
    rng = np.random.default_rng(seed)
    t0 = cfg["target_temperature"]
    state = ThermalState(room_temperature=t0, slab_temperature=t0 + 1.0,
                         outdoor_temperature=float(outdoor[0]), upper_floor_temperature=t0,
                         lower_floor_temperature=t0)
    replan = max(1, int(replan_hours / DT))
    reseed_step, reset_step = int(reseed_day * 24 / DT), int(reset_day * 24 / DT)
    hist = {k: {"house": [], "lower": [], "s": [], "r": [], "base": []} for k in arms}
    traj = {"state": [], "power": []}
    plan = None
    for step in range(total):
        now = START + timedelta(hours=step * DT)
        if step == reseed_step:
            for k in "BCF":
                reseed(arms[k], keep_samples=(k != "C"))
        if step == reset_step:
            for k in "EF":
                reset_to_prior(arms[k])
        if step % replan == 0:
            plan = optimizer.optimize(inputs=solve_inputs(
                initial_state=state, prices=price[step:step + 96], outdoor_temps=outdoor[step:step + 96],
                wind_speeds=wind[step:step + 96], precipitation=rain[step:step + 96],
                solar_radiation=solar[step:step + 96], start_time=now))
        power = float(plan.power_schedule[step % replan])
        traj["state"].append(replace(state, solar_radiation=float(solar[step])))
        traj["power"].append(power)
        state = plant_m.simulate_step(replace(state, solar_radiation=float(solar[step])), power,
                                      float(outdoor[step]), wind_speed=float(wind[step]),
                                      precipitation=float(rain[step]),
                                      solar_radiation=float(solar[step]), dt_hours=DT)
        state = replace(state, outdoor_temperature=float(outdoor[step + 1]),
                        solar_radiation=float(solar[step + 1]))
        n_up, n_lo = rng.normal(0.0, sigma, 2)
        sensed_up = (state.upper_floor_temperature if two_zone else state.room_temperature) + n_up
        seen = replace(state, room_temperature=sensed_up,
                       upper_floor_temperature=(sensed_up if two_zone else state.upper_floor_temperature),
                       lower_floor_temperature=state.lower_floor_temperature + n_lo)
        dt_util.freeze(now + timedelta(hours=DT))
        for k, arm in arms.items():
            c = arm["coord"]
            c._current_state = seen
            c._current_action = {"power": power, "dhw_power": 0.0}
            c._weather_forecast = [{"wind_speed": float(wind[step]), "precipitation": float(rain[step])}]
            # lower first: both read the same _last_house_sample, which the
            # house learner overwrites -- the production order (coordinator.py, the learn step)
            asyncio.run(c._async_learn_lower_floor_loss())
            asyncio.run(c._async_learn_house_heat_loss())
            h, lo = effective(arm)
            hist[k]["house"].append(h)
            hist[k]["lower"].append(lo)
            hist[k]["s"].append(c._house_heat_loss_scale)
            hist[k]["r"].append(c._lower_floor_loss_ratio)
            hist[k]["base"].append(base_terms(arm["params"]) + (arm["params"].heat_loss_coefficient,))
        if two_zone is False and state.room_temperature < 5:
            break
    dt_util.freeze(None)
    traj["state"].append(state)
    return {"hist": hist, "traj": traj, "true_house": true_house, "true_lower": true_lower,
            "outdoor": outdoor, "wind": wind, "rain": rain, "solar": solar, "cfg": cfg,
            "reseed_step": reseed_step, "reset_step": reset_step, "total": total, "two_zone": two_zone}


def forecast_mae(res, arm_key, start, stop, lead_h=12.0, every_h=3.0):
    """12-h open-loop forecast MAE of the arm's model, at its params of that step."""
    cfg, two_zone = res["cfg"], res["two_zone"]
    lead, every = int(lead_h / DT), int(every_h / DT)
    errs = []
    for i in range(start, min(stop, res["total"] - lead), every):
        p = ThermalParameters.from_config(cfg)
        p.dhw_enabled = False
        u, lo, hlc = res["hist"][arm_key]["base"][max(i - 1, 0)]
        s = res["hist"][arm_key]["s"][max(i - 1, 0)]
        r = res["hist"][arm_key]["r"][max(i - 1, 0)]
        p.heat_loss_coefficient = hlc
        if two_zone:
            p.upper_floor_heat_loss, p.lower_floor_heat_loss = u, lo
        p.house_heat_loss_scale, p.lower_floor_loss_ratio = s, r
        m = ThermalModel(p)
        st = res["traj"]["state"][i]
        for j in range(lead):
            st = m.simulate_step(replace(st, solar_radiation=float(res["solar"][i + j])),
                                 res["traj"]["power"][i + j], float(res["outdoor"][i + j]),
                                 wind_speed=float(res["wind"][i + j]), precipitation=float(res["rain"][i + j]),
                                 solar_radiation=float(res["solar"][i + j]), dt_hours=DT)
        true = res["traj"]["state"][i + lead]
        key = "upper_floor_temperature" if two_zone else "room_temperature"
        errs.append(abs(getattr(st, key) - getattr(true, key)))
    return float(np.mean(errs)) if errs else float("nan")


def summarise(res):
    rs, rr, tot = res["reseed_step"], res["reset_step"], res["total"]
    out = {}
    for k, h in res["hist"].items():
        house = np.asarray(h["house"]) * 1000.0
        lower = np.asarray(h["lower"]) * 1000.0
        th, tl = res["true_house"] * 1000.0, res["true_lower"] * 1000.0
        w_post = slice(rs, rr)            # after the reseed, before the reset
        w_reset = slice(rr, tot)          # after the reset
        d_house = np.diff(house[w_post])
        out[k] = {
            "house_std_post": float(np.std(house[w_post])),
            "house_step_rms_post": float(np.sqrt(np.mean(d_house ** 2))),
            "house_rmse_post": float(np.sqrt(np.mean((house[w_post] - th) ** 2))),
            "house_at_reseed": float(house[rs - 1]),
            "house_rmse_after_reset": float(np.sqrt(np.mean((house[w_reset] - th) ** 2))),
            "lower_std_post": float(np.std(lower[w_post])) if res["two_zone"] else None,
            "lower_rmse_post": float(np.sqrt(np.mean((lower[w_post] - tl) ** 2))) if res["two_zone"] else None,
            "lower_rmse_after_reset": float(np.sqrt(np.mean((lower[w_reset] - tl) ** 2))) if res["two_zone"] else None,
            "fc_mae_post": forecast_mae(res, k, rs, rr),
            "fc_mae_after_reset": forecast_mae(res, k, rr, tot),
        }
    out["_truth"] = {"house_w_per_k": res["true_house"] * 1000.0, "lower_w_per_k": res["true_lower"] * 1000.0}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", default="sz_157", choices=sorted(PLANTS))
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--days", type=float, default=10.0)
    ap.add_argument("--reseed-day", type=float, default=4.0)
    ap.add_argument("--reset-day", type=float, default=7.0)
    ap.add_argument("--replan-hours", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--trust-region", type=float, default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    if a.trust_region is not None:
        coord_mod._LEARNER_TRUST_REGION = a.trust_region
    print(f"plant={a.plant} sigma={a.sigma} trust_region={coord_mod._LEARNER_TRUST_REGION} "
          f"days={a.days} reseed_day={a.reseed_day} reset_day={a.reset_day}")
    c0, t0, w0 = time.process_time(), time.thread_time(), time.time()
    res = run(a.plant, a.sigma, a.days, a.reseed_day, a.reset_day, a.replan_hours, a.seed)
    s = summarise(res)
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    for k in "ABCEF":
        for m, v in s[k].items():
            if v is not None:
                print(f"RESULT {a.plant}.{k}.{m}={v:.5f}")
    for m in ("house_std_post", "house_step_rms_post", "house_rmse_post", "fc_mae_post", "lower_std_post", "lower_rmse_post"):
        if s["A"][m] is not None and s["A"][m] > 0:
            print(f"RESULT {a.plant}.ratio_B_over_A.{m}={s['B'][m] / s['A'][m]:.4f}")
            print(f"RESULT {a.plant}.ratio_C_over_B.{m}={s['C'][m] / max(s['B'][m], 1e-12):.4f}")
    for m in ("house_rmse_after_reset", "fc_mae_after_reset", "lower_rmse_after_reset"):
        if s["E"][m] is not None and s["E"][m] > 0:
            print(f"RESULT {a.plant}.ratio_F_over_E.{m}={s['F'][m] / s['E'][m]:.4f}")
    print(f"RESULT {a.plant}.truth_house_w_per_k={s['_truth']['house_w_per_k']:.2f}")
    print(f"RESULT wall_s={time.time() - w0:.1f}")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a(macOS)")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"args": vars(a), "summary": s,
                       "series": {k: {"house": res["hist"][k]["house"], "lower": res["hist"][k]["lower"]}
                                  for k in res["hist"]}}, fh)


if __name__ == "__main__":
    main()
