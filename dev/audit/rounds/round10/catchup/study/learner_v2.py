"""Catch-up verifier V2 for R10-ID-01 and R10-ID-02 (house learner vs solar
error; open-window CUSUM tripping on model bias).

Independent of the finder's ident_rolling.py: a SYNTHETIC SINGLE-ZONE house
(tests/profiles.py:house(), no two-zone ratio path), a half-sine sun, a fixed
feed-forward + P loop, 14 days, and -- unlike the finder -- the PRODUCTION
``_learning_frozen`` left in place (it returns None on a fresh FakeHass
coordinator, so the only freeze that can fire here is the vent CUSUM's
"ventilation"). One closed-loop trajectory per (delivery, UA truth, sun)
scenario; the learner arms observe it (paired arms).

Metrics (one line each):
  ID-01  ua_bias(k) = mean over the last 3 days of the learned effective UA /
         true UA - 1, at model aperture k x truth; slope = (bias(2) -
         bias(0.5)) / 1.5. Null: sun 0 -> every k equal.
  ID-02  vent_share = share of intervals after which production
         _learning_frozen(indoor, outdoor) == "ventilation"; and the same
         arm's ua_bias. Null: delivery 1.0, aperture exact, UA prior exact.
         Patched arm (finder's method): _learning_frozen -> None, count
         _vent_cusum.tripped.

Command (tree root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/catchup/study/learner_v2.py [--days 14] [--seeds 2] [--two-zone]
Caveat (both this harness and the finder's): the hidden states (slab, lower
zone) handed to the learners are the PLANT's true ones, which re-anchors the
replay every interval; in the single-zone house the heat enters through the
slab, so a delivery shortfall barely reaches the room residual there
(measured: ID-02 single-zone shares are 0 at every delivery). The two-zone
arm (--two-zone, radiators feed the sensed upper zone directly) is the one
that exercises ID-02.
Expected: ID-01 slope > 0, null spread ~0; ID-02 null 0, delivery 0.4 > 0,
    production-freeze share >= patched share (frozen learners cannot remove
    the bias that keeps the CUSUM tripped).
Baseline SHA: d749c986d (production byte-identical to a77faf30d).
Machine: macOS arm64, venv Python 3.14. No timing figure.
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
from datetime import datetime, timedelta  # noqa: E402

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np  # noqa: E402

from harness import FakeEntry, FakeHass  # noqa: E402
from homeassistant.util import dt as dt_util  # noqa: E402
from profiles import house  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402

DT = 0.25
START = datetime(2026, 10, 1, 0, 0)
KEYS = ("indoor_temp_entity", "outdoor_temp_entity")


TWO_ZONE = False


def cfg_base():
    c = house(two_zone=TWO_ZONE, dhw=False, buffer_tank_volume=0.0, house_heat_loss_coefficient=0.18,
              window_area=15.0, heat_pump_max_power=6.0, heat_pump_min_power=0.0,
              target_temperature=21.0)
    if TWO_ZONE:
        c["lower_floor_temp_entity"] = "sensor.synthetic_lower"
    return c


def ua_of(p, c):
    if p.two_zone_enabled:
        return (p.upper_floor_heat_loss + p.lower_floor_heat_loss * c._lower_floor_loss_ratio) * c._house_heat_loss_scale
    return p.heat_loss_coefficient * c._house_heat_loss_scale


def arm(cfg, aperture_k, patched):
    cfg = dict(cfg, window_area=cfg["window_area"] * aperture_k)
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    c._thermal_params = p
    c._thermal_model = ThermalModel(p)
    if patched:
        c._learning_frozen = lambda *keys: None
    return {"c": c, "p": p, "patched": patched, "ua": [], "vent": 0}


def run(days, seed, delivery=1.0, ua_true=1.0, sun=True, arms_spec=None):
    cfg = cfg_base()
    truth = ThermalParameters.from_config(cfg)
    truth.dhw_enabled = False
    truth.heat_loss_coefficient *= ua_true
    truth.upper_floor_heat_loss *= ua_true
    truth.lower_floor_heat_loss *= ua_true
    plant = ThermalModel(truth)
    prior = ThermalParameters.from_config(cfg)
    prior_m = ThermalModel(prior)
    arms = {k: arm(cfg, *v) for k, v in arms_spec.items()}
    rng = np.random.default_rng(seed)
    n = int(days * 24 / DT)
    clear = rng.uniform(0.2, 1.0, size=days + 2)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=5.0)
    ar = 0.0
    loop = asyncio.new_event_loop()
    for i in range(n):
        now = START + timedelta(hours=i * DT)
        h = (i * DT) % 24.0
        ar = 0.9 * ar + rng.normal(0, 0.2)
        t_out = 5.0 + 4.0 * math.cos(2 * math.pi * (h - 15) / 24) + ar
        irr = (450.0 * max(0.0, math.sin(math.pi * (h - 7) / 10)) * clear[int(i * DT / 24)]) if sun else 0.0
        sensed = (st.upper_floor_temperature if TWO_ZONE else st.room_temperature) + rng.normal(0, 0.05)
        cop = prior_m.compute_cop(t_out)
        ua_prior = (prior.upper_floor_heat_loss + prior.lower_floor_heat_loss) if TWO_ZONE else prior.heat_loss_coefficient
        ff = ua_prior * max(21.0 - t_out, 0.0) / max(cop, 1.0)
        power = float(np.clip(ff + 2.0 * (21.0 - sensed), 0.0, 6.0))
        seen = replace(st, room_temperature=sensed, outdoor_temperature=t_out, solar_radiation=irr)
        if TWO_ZONE:
            seen = replace(seen, upper_floor_temperature=sensed,
                           lower_floor_temperature=st.lower_floor_temperature + rng.normal(0, 0.05))
        dt_util.freeze(now)
        for a in arms.values():
            c = a["c"]
            c._current_state = seen
            c._weather_forecast = [{"wind_speed": 0.0, "precipitation": 0.0}]
            if TWO_ZONE:
                loop.run_until_complete(c._async_learn_lower_floor_loss())
            loop.run_until_complete(c._async_learn_house_heat_loss())
            c._refresh_model_corrections()
            c._current_action = {"power": power, "dhw_power": 0.0}
            a["ua"].append(ua_of(a["p"], c))
            if a["patched"]:
                a["vent"] += int(bool(c._vent_cusum.tripped))
            else:
                a["vent"] += int(type(c)._learning_frozen(c, *KEYS) == "ventilation")
        st = plant.simulate_step(replace(st, solar_radiation=irr), power * delivery, t_out,
                                 solar_radiation=irr, dt_hours=DT, hour_of_day=h)
    dt_util.freeze(None)
    loop.close()
    ua_t = (truth.upper_floor_heat_loss + truth.lower_floor_heat_loss) if TWO_ZONE else truth.heat_loss_coefficient
    last = int(3 * 24 / DT)
    return {k: (float(np.mean(a["ua"][-last:]) / ua_t - 1.0), a["vent"] / n) for k, a in arms.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--two-zone", action="store_true")
    a = ap.parse_args()
    global TWO_ZONE
    TWO_ZONE = a.two_zone
    print(f"RESULT two_zone={TWO_ZONE}")
    c0, t0 = time.process_time(), time.thread_time()
    ks = (0.5, 1.0, 2.0)
    for seed in range(1, a.seeds + 1):
        for sun in (True, False):
            r = run(a.days, seed, sun=sun, arms_spec={f"k{k}": (k, False) for k in ks})
            b = {k: r[f"k{k}"][0] for k in ks}
            print(f"RESULT ID01.seed{seed}.sun{int(sun)}.ua_bias " + " ".join(f"k{k}={b[k]:+.4f}" for k in ks)
                  + f"  slope={(b[2.0] - b[0.5]) / 1.5:+.4f} spread={max(b.values()) - min(b.values()):.4f}"
                  + f"  vent_prod_k1={r['k1.0'][1]:.3f}")
    for seed in range(1, a.seeds + 1):
        for g, ua in ((1.0, 1.0), (0.9, 1.0), (0.8, 1.0), (0.6, 1.0), (0.4, 1.0), (1.0, 1.3), (1.0, 1.6)):
            r = run(a.days, seed, delivery=g, ua_true=ua, sun=False,
                    arms_spec={"prod": (1.0, False), "patched": (1.0, True)})
            print(f"RESULT ID02.seed{seed}.g{g}.ua{ua} prod: vent_share={r['prod'][1]:.3f} ua_bias={r['prod'][0]:+.4f}"
                  f" | patched: vent_share={r['patched'][1]:.3f} ua_bias={r['patched'][0]:+.4f}")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
