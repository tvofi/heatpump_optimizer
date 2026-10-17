"""R10-VENT-DETECTOR (#2241, D2-s3-72): does the open-window detector separate
a persistent model bias from a planted open window?

Metric (one line each, per scenario):
  false_share = share of 15-min intervals OUTSIDE any planted window after
      which the PRODUCTION ``_learning_frozen(indoor, outdoor)`` returns
      "ventilation" (the freeze the finder counted, with the real freeze in
      place, so a self-latch shows);
  detect_h    = hours from a planted window opening to the first interval
      frozen "ventilation" (nan: never inside the window);
  release_h   = hours from the window closing to the first interval not
      frozen (nan: still frozen at the end);
  ua_bias     = learned effective UA over the last 3 days / true UA - 1.

Command (tree root):
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_vent_bias_window.py [--days 14] [--seeds 2]

Scenarios: delivery g in {1.0, 0.6, 0.4} (the plant receives g x the commanded
power the model replays: a meter or COP off by 1/g), UA truth 1.0 or 1.6 x the
prior, power by a smooth feed-forward + P loop ("pi") or a hysteresis on/off
thermostat ("onoff", full power in blocks: the hardest shape for a bias that is
proportional to power), with no window or a planted one (an extra ``vent_w_k``
W/K on the sensed upper zone, opened on day 10 at 18:00 for ``hours``; the
sizes are ``WINDOWS``). false_onsets_h lists the hours (from the start) at
which a freeze outside the window began.

Plant: the catch-up verifier's two-zone house (tests/profiles.py:house(two_zone=True),
radiators on the sensed upper zone), same weather and loop as
dev/audit/rounds/round10/catchup/study/learner_v2.py --two-zone.
Instrumented symbols (driven, none re-implemented):
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._async_learn_lower_floor_loss
    heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator._learning_frozen
    heatpump_optimizer.thermal_model:ThermalModel.simulate_step (plant)
Null control: g 1.0, UA 1.0, no window -> false_share 0.
Perturbation: the planted window -> detect_h finite on every arm at g 1.0; and
    g 1.0 -> 0.4 is the finding's own perturbation of false_share.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import asyncio  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
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
WINDOW_DAY, WINDOW_HOUR = 10, 18.0
#: (extra W/K on the upper zone, hours open). The upper zone's own UA is
#: 100 W/K here, so 300 W/K is a window opened wide for airing and 150 W/K a
#: tilted one; 100 W/K moves the residual (~0.13 K per 15 min at dT 16 K)
#: barely past the CUSUM's per-sample drift allowance, below its reach.
WINDOWS = ((0.0, 0.0), (300.0, 2.0), (300.0, 8.0), (150.0, 4.0), (100.0, 8.0))


def cfg_base():
    c = house(two_zone=True, dhw=False, buffer_tank_volume=0.0, house_heat_loss_coefficient=0.18,
              window_area=15.0, heat_pump_max_power=6.0, heat_pump_min_power=0.0,
              target_temperature=21.0)
    c["lower_floor_temp_entity"] = "sensor.synthetic_lower"
    return c


def ua_of(p, c):
    return (p.upper_floor_heat_loss + p.lower_floor_heat_loss * c._lower_floor_loss_ratio) * c._house_heat_loss_scale


def run(days, seed, delivery, ua_true, control, vent_w_k, hours):
    cfg = cfg_base()
    truth = ThermalParameters.from_config(cfg)
    truth.dhw_enabled = False
    truth.heat_loss_coefficient *= ua_true
    truth.upper_floor_heat_loss *= ua_true
    truth.lower_floor_heat_loss *= ua_true
    plant = ThermalModel(truth)
    vented = ThermalModel(replace(truth, upper_floor_heat_loss=truth.upper_floor_heat_loss + vent_w_k / 1000.0))
    prior = ThermalParameters.from_config(cfg)
    prior_m = ThermalModel(prior)
    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
    p = ThermalParameters.from_config(cfg)
    p.dhw_enabled = False
    c._thermal_params = p
    c._thermal_model = ThermalModel(p)
    rng = np.random.default_rng(seed)
    n = int(days * 24 / DT)
    w0 = int((WINDOW_DAY * 24 + WINDOW_HOUR) / DT)
    w1 = w0 + int(hours / DT) if vent_w_k > 0 else w0
    clear = rng.uniform(0.2, 1.0, size=days + 2)
    st = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=5.0)
    ar = 0.0
    on = False
    frozen = []
    ua = []
    loop = asyncio.new_event_loop()
    for i in range(n):
        now = START + timedelta(hours=i * DT)
        h = (i * DT) % 24.0
        ar = 0.9 * ar + rng.normal(0, 0.2)
        t_out = 5.0 + 4.0 * math.cos(2 * math.pi * (h - 15) / 24) + ar
        irr = 450.0 * max(0.0, math.sin(math.pi * (h - 7) / 10)) * clear[int(i * DT / 24)]
        sensed = st.upper_floor_temperature + rng.normal(0, 0.05)
        if control == "onoff":
            on = sensed < 20.7 if not on else sensed < 21.3
            power = 6.0 if on else 0.0
        else:
            cop = prior_m.compute_cop(t_out)
            ff = (prior.upper_floor_heat_loss + prior.lower_floor_heat_loss) * max(21.0 - t_out, 0.0) / max(cop, 1.0)
            power = float(np.clip(ff + 2.0 * (21.0 - sensed), 0.0, 6.0))
        seen = replace(st, room_temperature=sensed, upper_floor_temperature=sensed,
                       lower_floor_temperature=st.lower_floor_temperature + rng.normal(0, 0.05),
                       outdoor_temperature=t_out, solar_radiation=irr)
        dt_util.freeze(now)
        c._current_state = seen
        c._weather_forecast = [{"wind_speed": 0.0, "precipitation": 0.0}]
        loop.run_until_complete(c._async_learn_lower_floor_loss())
        loop.run_until_complete(c._async_learn_house_heat_loss())
        c._refresh_model_corrections()
        c._current_action = {"power": power, "dhw_power": 0.0}
        ua.append(ua_of(p, c))
        frozen.append(type(c)._learning_frozen(c, *KEYS) == "ventilation")
        m = vented if w0 <= i < w1 else plant
        st = m.simulate_step(replace(st, solar_radiation=irr), power * delivery, t_out,
                             solar_radiation=irr, dt_hours=DT, hour_of_day=h)
    dt_util.freeze(None)
    loop.close()
    ua_t = truth.upper_floor_heat_loss + truth.lower_floor_heat_loss
    last = int(3 * 24 / DT)
    # The learners see interval i's state at step i, so the window's first
    # effect is read at step w0 + 1; a release is read at w1 + 1 onwards.
    in_window = (lambda j: w0 < j <= w1 + int(24 / DT)) if vent_w_k > 0 else (lambda j: False)
    outside = [f for j, f in enumerate(frozen) if not in_window(j)]
    onsets = [j for j in range(1, n) if frozen[j] and not frozen[j - 1] and not in_window(j)]
    detect = next((j for j in range(w0 + 1, w1 + 1) if frozen[j]), None) if vent_w_k > 0 else None
    release = next((j for j in range(w1 + 1, n) if not frozen[j]), None) if vent_w_k > 0 else None
    return {
        "false_share": sum(outside) / len(outside),
        "detect_h": (detect - w0) * DT if detect is not None else float("nan"),
        "release_h": (release - w1) * DT if release is not None else float("nan"),
        "ua_bias": float(np.mean(ua[-last:]) / ua_t - 1.0),
        "false_onsets_h": [round(j * DT, 2) for j in onsets],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--seeds", type=int, default=2)
    a = ap.parse_args()
    for seed in range(1, a.seeds + 1):
        for control in ("pi", "onoff"):
            for g, ua_t in ((1.0, 1.0), (0.6, 1.0), (0.4, 1.0), (1.0, 1.6)):
                for vent, hours in WINDOWS:
                    r = run(a.days, seed, g, ua_t, control, vent, hours)
                    tag = f"seed{seed}.{control}.g{g}.ua{ua_t}.vent{vent:.0f}x{hours:.0f}h"
                    print(f"RESULT {tag} false_share={r['false_share']:.3f} detect_h={r['detect_h']:.2f} "
                          f"release_h={r['release_h']:.2f} ua_bias={r['ua_bias']:+.4f} "
                          f"false_onsets_h={r['false_onsets_h'][:6]}", flush=True)
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")


if __name__ == "__main__":
    main()
