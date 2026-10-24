"""R10 identifiability study, Q1: can falling solar gain be separated from the
house heat loss while both learners run, or must solar converge first?

Metric (one line): ua_bias = (effective house UA the real coordinator learners
publish, mean over the last 7 days) / (the plant's true house UA) - 1, per arm,
where the arms differ only in the model's solar aperture (fixed at a ratio of
the truth, or learned by #36) on ONE shared closed-loop autumn trajectory; plus
an offline joint OLS of the replay residual on [dT, Q_solar_model, 1] (its
condition number and its UA / aperture separation errors).

Command (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/study-ident/ident_rolling.py \
        [--plant P1] [--scenario autumn|flat|indep] [--delivery 1.0] [--days 42]
Expected (+-0.02 unless noted): autumn P1 arm fix1.00 ua_bias ~0 (within the
learner's own noise, |x|<0.03); arm fix0.50 (model sees half the sun) ua_bias
> 0; flat scenario: every fixed arm equal to fix1.00 within 0.005 (no sun, no
aperture effect); delivery 0.4: fix1.00 ua_bias ~ +1.5 (UA/g).
Baseline SHA: a77faf30d (origin/main at study start). Machine: macOS arm64.

Template: dev/audit/... tools/audit/round10/study-reseed/reseed_rolling.py
(study/r10-reseed @ 2c42ba4a0): several learner coordinators observe one
closed-loop trajectory (paired arms, common random numbers). Deviation: the
loop is closed by a PI controller on the sensed upper zone, not by the
optimizer -- the learners never see who chose the power, only the power, and
a PI loop makes a 42-day multi-arm run take seconds (the optimizer is not under
study). The trajectory is independent of the arms, so arms are exactly paired.

Instrumented symbols (all driven, none re-implemented):
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_lower_floor_loss
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._fold_solar_aperture (via the house learner)
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._refresh_model_corrections
    heatpump_optimizer.thermal_model:ThermalModel.simulate_step (plant, replay, joint estimator)
Perturbation: --scenario flat (irradiance identically 0): every fixed-aperture
    arm's ua_bias must collapse onto fix1.00's (the aperture multiplies zero).
    Direction: spread across fixed arms -> ~0. Second: --delivery 0.4 moves
    fix1.00's ua_bias from ~0 to ~+1.5 (commanded-power replay, see REPORT).
Null control: the fix1.00 arm (model aperture = truth): no solar error, so its
    ua_bias is the learner's own noise floor on the same trajectory.
Count key: ua is read from the coordinator attributes the learners write
    (_house_heat_loss_scale, _lower_floor_loss_ratio) times the arm's own
    ThermalParameters zone bases -- the value the production seam delivers.
`_learning_frozen` is patched to None for every arm alike (no HA states).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402

from heatpump_optimizer import coordinator as coord_mod  # noqa: E402
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

DT = 0.25
LAT = 60.1
START = datetime(2026, 9, 1, 0, 0)

#: name -> (UA truth / prior, aperture truth / model, mass factor)
PLANTS = {
    "P1": (1.00, 1.50, 1.0),
    "P2": (1.00, 0.50, 1.0),
    "P3": (1.50, 2.00, 1.0),
    "P4": (0.80, 0.70, 1.3),
    "P5": (1.20, 1.30, 0.8),
    "P0": (1.00, 1.00, 1.0),
}
FIXED_RATIOS = (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)


def base_cfg(mass):
    """Owner-shaped two-zone house (timber, crawlspace, radiators up, slab down)."""
    return {
        "target_temperature": 20.5, "min_temperature": 18.0, "max_temperature": 22.0,
        "heat_pump_max_power": 5.5, "heat_pump_min_power": 0.0,
        "heat_pump_cop_nominal": 4.0, "dhw_enabled": False,
        "two_zone_mode": "on",
        "upper_floor_heat_loss": 0.0627, "lower_floor_heat_loss": 0.0627,
        "upper_floor_thermal_mass": 1.26 * mass, "lower_floor_thermal_mass": 1.26 * mass,
        "slab_thermal_mass": 4.41 * mass, "slab_heat_transfer": 0.7,
        "inter_zone_heat_transfer": 0.5, "radiator_power_fraction": 0.5,
        "house_heat_loss_coefficient": 0.1254,
        "window_area": 14.5, "solar_heat_gain_coefficient": 0.6, "solar_orientation_factor": 0.7,
        "lower_floor_temp_entity": "sensor.lower_floor",
        "buffer_tank_volume": 0.0,
    }


def clear_sky_ghi(doy, hour, lat=LAT):
    """Haurwitz clear-sky GHI, W/m2, local solar time."""
    decl = math.radians(23.45) * math.sin(2 * math.pi * (284 + doy) / 365.0)
    ha = math.radians(15.0 * (hour - 12.0))
    phi = math.radians(lat)
    sin_el = math.sin(phi) * math.sin(decl) + math.cos(phi) * math.cos(decl) * math.cos(ha)
    if sin_el <= 0.01:
        return 0.0
    return 1098.0 * sin_el * math.exp(-0.057 / sin_el)


def make_weather(scenario, days, seed):
    """outdoor T, irradiance (W/m2), per DT step, plus the day's clearness."""
    rng = np.random.default_rng(seed)
    n = int(days * 24 / DT) + 8
    clear = rng.beta(0.6, 0.6, size=int(days) + 2)
    t_out = np.zeros(n)
    irr = np.zeros(n)
    ar = 0.0
    for i in range(n):
        d = i * DT / 24.0
        day = int(d)
        hour = (i * DT) % 24.0
        doy = START.timetuple().tm_yday + day
        ar = 0.95 * ar + rng.normal(0.0, 0.15)
        if scenario == "indep":
            # no trend, no diurnal cycle: dT moves only by AR noise, so the
            # sun is independent of dT (apart from the house's own response)
            t_out[i] = 5.0 + 4.0 * ar
        else:
            mean = 13.0 - 10.0 * d / days          # 13 -> 3 degC over the run
            amp = 1.5 + 4.0 * clear[day]           # clear days swing harder
            t_out[i] = mean + amp * math.cos(2 * math.pi * (hour - 15.0) / 24.0) + ar
        if scenario == "flat":
            irr[i] = 0.0
        else:
            irr[i] = clear_sky_ghi(doy, hour) * (0.2 + 0.8 * clear[day])
    return t_out, irr


def effective(arm):
    p, c = arm["params"], arm["coord"]
    s, r = c._house_heat_loss_scale, c._lower_floor_loss_ratio
    return (p.upper_floor_heat_loss + p.lower_floor_heat_loss * r) * s


#: sensor quantization the owner's install shows (lower T6: 1 K steps; T4: integer)
QUANT_LOWER = float(os.environ.get("IDENT_QUANT_LOWER", "0"))
QUANT_OUT = os.environ.get("IDENT_QUANT_OUT", "0") == "1"
DARK_W_M2 = float(os.environ.get("IDENT_DARK_W_M2", "1.0"))  # night only; 50 = the gains learner's "dark"


def _dark_only(c):
    """Design candidate (not production): the UA step is taken only on dark
    intervals. A sunny interval takes the house learner's own early-return
    path -- the snapshot advances, nothing folds -- exactly what a rejected
    sample does in production."""
    orig = c._async_learn_house_heat_loss

    async def learn():
        prev = c._last_house_sample
        if prev is not None and float(prev.solar_radiation or 0.0) >= DARK_W_M2:
            c._last_house_sample = replace(c._current_state)
            c._last_house_sample_time = dt_util.now()
            return
        await orig()
    c._async_learn_house_heat_loss = learn
    # the lower-floor ratio reads the same snapshot and folds the lower zone,
    # which takes 1 - solar_upper_fraction (60 %) of the sun: same rule
    orig_lo = c._async_learn_lower_floor_loss

    async def learn_lo():
        prev = c._last_house_sample
        if prev is not None and float(prev.solar_radiation or 0.0) >= DARK_W_M2:
            return
        await orig_lo()
    c._async_learn_lower_floor_loss = learn_lo


def make_arm(cfg, aperture_ratio, learn_solar, learn_gains, dark_only=False):
    cfg = dict(cfg)
    cfg["solar_aperture_learning_enabled"] = bool(learn_solar)
    cfg["internal_gains_learning_enabled"] = bool(learn_gains)
    cfg["window_area"] = cfg["window_area"] * aperture_ratio
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    m = ThermalModel(p)
    c._thermal_params = p
    c._thermal_model = m
    c._learning_frozen = lambda *keys: None
    if dark_only:
        _dark_only(c)
    return {"coord": c, "params": p, "model": m}


def run(plant, scenario, days, delivery, sigma, seed, arms_spec):
    ua_err, ap_err, mass = PLANTS[plant]
    cfg = base_cfg(mass)
    truth = ThermalParameters.from_config(dict(cfg, window_area=cfg["window_area"] * ap_err))
    truth.dhw_enabled = False
    truth.upper_floor_heat_loss *= ua_err
    truth.lower_floor_heat_loss *= ua_err
    truth.heat_loss_coefficient *= ua_err
    plant_m = ThermalModel(truth)
    true_house = truth.upper_floor_heat_loss + truth.lower_floor_heat_loss
    prior = ThermalParameters.from_config(cfg)
    prior_m = ThermalModel(prior)

    arms = {k: make_arm(cfg, *spec) for k, spec in arms_spec.items()}
    t_out, irr = make_weather(scenario, days, seed)
    rng = np.random.default_rng(seed + 1)
    total = int(days * 24 / DT)
    t_set = cfg["target_temperature"]
    state = ThermalState(room_temperature=t_set, slab_temperature=t_set + 1.0,
                         outdoor_temperature=float(t_out[0]), upper_floor_temperature=t_set,
                         lower_floor_temperature=t_set, buffer_tank_temperature=30.0)
    integ = 0.0
    hist = {k: [] for k in arms}
    solar_hist = {k: [] for k in arms}
    vent = {k: 0 for k in arms}
    obs = []          # (prev seen state, power, t_out, irr, seen next) for the joint OLS
    seen_prev = None
    loop = asyncio.new_event_loop()
    for step in range(total):
        now = START + timedelta(hours=step * DT)
        # PI on the sensed upper zone; feed-forward from the PRIOR (fixed) model
        sensed_up = state.upper_floor_temperature + rng.normal(0.0, sigma)
        sensed_lo = state.lower_floor_temperature + rng.normal(0.0, sigma)
        if QUANT_LOWER > 0:   # the owner's lower sensor reads only 18.3 / 19.3
            sensed_lo = math.floor((sensed_lo - 0.3) / QUANT_LOWER + 0.5) * QUANT_LOWER + 0.3
        e = t_set - sensed_up
        integ = float(np.clip(integ + 0.3 * e * DT, -2.0, 4.0))
        cop = prior_m.compute_cop(float(t_out[step]))
        ff = (prior.upper_floor_heat_loss + prior.lower_floor_heat_loss) * max(t_set - t_out[step], 0.0) / max(cop, 1.0)
        power = float(np.clip(ff + 1.5 * e + integ, 0.0, 5.5))
        seen = replace(state, room_temperature=sensed_up, upper_floor_temperature=sensed_up,
                       lower_floor_temperature=sensed_lo,
                       outdoor_temperature=(float(round(t_out[step])) if QUANT_OUT else float(t_out[step])),
                       solar_radiation=float(irr[step]))
        if seen_prev is not None:
            obs.append((seen_prev[0], seen_prev[1], seen))
        dt_util.freeze(now)
        for k, arm in arms.items():
            c = arm["coord"]
            c._current_state = seen
            c._weather_forecast = [{"wind_speed": 0.0, "precipitation": 0.0}]
            # the learners run BEFORE this cycle's action replaces the last one
            loop.run_until_complete(c._async_learn_lower_floor_loss())
            loop.run_until_complete(c._async_learn_house_heat_loss())
            c._refresh_model_corrections()
            c._current_action = {"power": power, "dhw_power": 0.0}
            hist[k].append(effective(arm))
            solar_hist[k].append((c._solar_aperture["scale"], c._solar_aperture["n"]))
            vent[k] += int(bool(c._vent_cusum.tripped))
        seen_prev = (seen, power)
        # the plant receives `delivery` x the commanded electrical power
        state = plant_m.simulate_step(replace(state, solar_radiation=float(irr[step])), power * delivery,
                                      float(t_out[step]), wind_speed=0.0, precipitation=0.0,
                                      solar_radiation=float(irr[step]), dt_hours=DT,
                                      hour_of_day=now.hour + now.minute / 60.0)
    dt_util.freeze(None)
    loop.close()
    return {"hist": hist, "solar": solar_hist, "vent": vent, "true_house": true_house, "obs": obs,
            "truth": truth, "prior": prior, "prior_m": prior_m, "cfg": cfg,
            "t_out": t_out, "irr": irr, "total": total, "ap_err": ap_err, "ua_err": ua_err}


def joint_ols(res):
    """Offline joint estimator: replay each interval through the FIXED prior model
    (real simulate_step) and regress the implied upper-zone surplus power on
    [dT_upper, Q_solar_model, 1], with the house learner's own sample gates.

    Two-stage least squares, dT instrumented by the PREVIOUS interval's dT: the
    sensed start temperature sits in both dT and (with the opposite sign) in the
    replay residual, so plain OLS is biased by sigma^2*C/dt/var(dT) (+9 % on
    P1 at sigma=0.1 K); the lag shares the signal but not the noise. Plain OLS is
    reported beside it. Without sun (flat) the solar column is dropped."""
    prior, m = res["prior"], res["prior_m"]
    rows, ys, irrs, zs = [], [], [], []
    prev_dT = None
    for prev, power, nxt in res["obs"]:
        dT = prev.upper_floor_temperature - prev.outdoor_temperature
        lag, prev_dT = prev_dT, dT
        if dT < coord_mod.HOUSE_LOSS_MIN_DELTA or lag is None:
            continue
        pred = m.simulate_step(prev, power, prev.outdoor_temperature, wind_speed=0.0,
                               precipitation=0.0, solar_radiation=prev.solar_radiation, dt_hours=DT)
        resid = nxt.upper_floor_temperature - pred.upper_floor_temperature
        if abs(resid) > coord_mod.HOUSE_LOSS_MAX_RESIDUAL:
            continue
        q = m.compute_solar_gain(prev.solar_radiation)
        rows.append((dT, q, 1.0))
        zs.append((lag, q, 1.0))
        ys.append(resid * prior.upper_floor_thermal_mass / DT)
        irrs.append(prev.solar_radiation)
    X, Z, y = np.asarray(rows), np.asarray(zs), np.asarray(ys)
    sunny = np.std(X[:, 1]) > 0
    cols = [0, 1, 2] if sunny else [0, 2]
    X, Z = X[:, cols], Z[:, cols]
    Xs = X / np.linalg.norm(X, axis=0)
    b_ols, *_ = np.linalg.lstsq(X, y, rcond=None)
    b_iv = np.linalg.solve(Z.T @ X, Z.T @ y)
    r = y - X @ b_iv
    s2 = float(r @ r) / max(len(y) - X.shape[1], 1)
    zx_inv = np.linalg.inv(Z.T @ X)
    cov = s2 * zx_inv @ (Z.T @ Z) @ zx_inv.T
    f_up = prior.solar_upper_fraction
    scale_hat = 1.0 - b_iv[0] / prior.upper_floor_heat_loss
    out = {
        "n": len(y), "n_sunny": int(np.sum(np.asarray(irrs) >= coord_mod.SOLAR_APERTURE_MIN_IRRADIANCE)),
        "cond": float(np.linalg.cond(Xs)),
        "corr_dT_qsol": float(np.corrcoef(X[:, 0], X[:, 1])[0, 1]) if sunny else float("nan"),
        "scale_hat": float(scale_hat),
        "scale_se": float(math.sqrt(cov[0, 0]) / prior.upper_floor_heat_loss),
        "ua_sep_err": float(scale_hat / res["ua_err"] - 1.0),
        "ua_sep_err_ols": float((1.0 - b_ols[0] / prior.upper_floor_heat_loss) / res["ua_err"] - 1.0),
    }
    if sunny:
        ap_hat = 1.0 + b_iv[1] / f_up
        out.update({"ap_hat": float(ap_hat), "ap_se": float(math.sqrt(cov[1, 1]) / f_up),
                    "ap_sep_err": float(ap_hat / res["ap_err"] - 1.0)})
        # how many sunny samples the joint fit needs for a 10 % aperture SE:
        # SE scales as 1/sqrt(n_sunny), so n_needed = n_sunny * (se/0.10)^2
        out["n_sunny_for_10pct"] = float(out["n_sunny"] * (out["ap_se"] / 0.10) ** 2)
    return out


def arms_for(ap_err):
    spec = {f"fix{r:.2f}": (r * ap_err, False, False) for r in FIXED_RATIOS}
    spec["learn"] = (1.0, True, False)           # starts at the configured aperture
    spec["learn+gains"] = (1.0, True, True)       # the owner's flags
    spec["none"] = (1.0, False, False)            # configured aperture, no learning
    # design candidate: UA folds only in the dark, aperture fixed wrong/right
    for r in (0.5, 1.0, 2.0):
        spec[f"dark{r:.2f}"] = (r * ap_err, False, False, True)
    return spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", default="P1", choices=sorted(PLANTS))
    ap.add_argument("--scenario", default="autumn", choices=("autumn", "flat", "indep"))
    ap.add_argument("--delivery", type=float, default=1.0)
    ap.add_argument("--days", type=float, default=42.0)
    ap.add_argument("--sigma", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    c0, t0, w0 = time.process_time(), time.thread_time(), time.time()
    res = run(a.plant, a.scenario, a.days, a.delivery, a.sigma, a.seed, arms_for(PLANTS[a.plant][1]))
    tag = f"{a.plant}.{a.scenario}.g{a.delivery:.2f}"
    last = slice(res["total"] - int(7 * 24 / DT), res["total"])
    out = {}
    for k, h in res["hist"].items():
        h = np.asarray(h)
        bias = float(np.mean(h[last]) / res["true_house"] - 1.0)
        out[k] = bias
        print(f"RESULT {tag}.ua_bias.{k}={bias:+.4f}")
    for k in ("learn", "learn+gains"):
        sc, n = res["solar"][k][-1]
        print(f"RESULT {tag}.solar_scale.{k}={sc:.3f} (truth {res['ap_err']:.2f}) n={n:.0f}")
        # first day the learned aperture is within 10 % of the truth and stays there
        ser = np.asarray([s for s, _ in res["solar"][k]])
        ok = np.abs(ser / res["ap_err"] - 1.0) <= 0.10
        idx = next((i for i in range(len(ok)) if ok[i:].all()), None)
        print(f"RESULT {tag}.solar_conv_day.{k}={(idx * DT / 24.0) if idx is not None else float('nan'):.1f}")
        n_ser = np.asarray([nn for _, nn in res["solar"][k]])
        i30 = int(np.argmax(n_ser >= 30)) if (n_ser >= 30).any() else None
        print(f"RESULT {tag}.solar_n30_day.{k}={(i30 * DT / 24.0) if i30 is not None else float('nan'):.1f}")
        print(f"RESULT {tag}.solar_samples_per_day.{k}={n_ser[-1] / a.days:.2f}")
    fixed = [out[f"fix{r:.2f}"] for r in FIXED_RATIOS]
    print(f"RESULT {tag}.fixed_arm_spread={max(fixed) - min(fixed):.4f}")
    # the open-window CUSUM is fed by the same residual; `_learning_frozen` is
    # patched, so a trip here freezes nothing -- it only counts how often a
    # model bias alone would have frozen every learner in production
    for k, v in res["vent"].items():
        print(f"RESULT {tag}.vent_tripped_share.{k}={v / res['total']:.3f}")
    j = joint_ols(res)
    for m, v in j.items():
        print(f"RESULT {tag}.joint.{m}={v:.4f}" if isinstance(v, float) else f"RESULT {tag}.joint.{m}={v}")
    print(f"RESULT {tag}.truth_house_w_per_k={res['true_house'] * 1000:.1f}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT wall_s={time.time() - w0:.1f}")
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=n/a(macOS)")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"args": vars(a), "ua_bias": out, "joint": j,
                       "series": {k: list(np.asarray(v)[::4] * 1000) for k, v in res["hist"].items()},
                       "solar": {k: [s for s, _ in v][::4] for k, v in res["solar"].items()}}, fh)


if __name__ == "__main__":
    main()
