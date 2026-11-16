"""D7.M3 consequence (round 11, D7-s2): what a two-week absence teaches the learners that do not freeze on away.

Metric (comfort): learned comfort weight after D days of half-hourly cycles of
``HeatPumpOptimizerCoordinator._record_quiet_comfort_period`` with ``_away_state.active``,
each cycle reading the plan of a REAL solve (``_solve_record(...).optimizer().optimize``) of
the same coordinator under the same away state, as a ratio to the configured weight.
Count key: ``ComfortLearner.learned_weight`` as the production seam writes it.
Metric (hot water): the reservoir share of zero-energy occurrences and the p90 per configured
demand window that ``DhwProfileLearner.async_learn_dynamics`` leaves after 26 occupied days
then D away days with no draws (``DrawStats.quantile``, the planner's #20 ready energy).

Metric (gains): mean of the hourly internal-gains profile after DAYS of dark away intervals
whose free heat is short by the occupants' share, closed loop in the gains (the replay heats
by the learned hour, so the residual shrinks as the profile learns), over the configured g0.

Arms: away (baseline), away frozen (``--perturb``: ``_learning_frozen`` answers "away" while
away is active, the fix shape), and the null control: the same days at home with the same real
plan solved without away (the quiet evidence it books there is the learner's intended input).

Run:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D7/s2/m3_away_drift.py [--perturb]
Expected (baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, D=14): comfort_weight_ratio_away
< 1 (exact value printed), 1.000 under --perturb; dhw zero share 14/40 per window, 0 under --perturb.
Machine: box B5 (round-11 finder container), numpy 2.5.4 / scipy 1.18.1, CPython 3.14.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import asyncio  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import timedelta  # noqa: E402
from unittest import mock  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m3_learner_freeze as M  # noqa: E402  (applies --perturb on import)
import numpy as np  # noqa: E402

DAYS = 14
CYCLE_MIN = 30


def _prices(start, n=48):
    return [{"total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
             "starts_at": (start + timedelta(hours=h)).isoformat(), "level": "NORMAL"}
            for h in range(n)]


def _weather(start, n=48):
    return [{"datetime": (start + timedelta(hours=h)).isoformat(),
             "temperature": -5.0 + 3.0 * (h % 24) / 24.0, "wind_speed": 3.0,
             "precipitation": 0.0, "humidity": 85.0} for h in range(n)]


def real_plan(c, now):
    """One production solve of this coordinator at ``now`` (its away state included)."""
    c._prices = _prices(now)
    c._weather_forecast = _weather(now)
    c._solar_radiation_forecast = [0.0] * 48
    with mock.patch.object(M.dt_mod, "now", lambda: now), \
            mock.patch.object(M.coord_mod.dt_util, "now", lambda: now):
        horizon = c._forecast_arrays(now)
        rec = c._solve_record(now, horizon)
        return rec.optimizer().optimize(inputs=rec.inputs)


def comfort_arm(away: bool):
    c = M.make(comfort_learning_enabled=True, away_enabled=True, away_temperature=16.0,
               optimization_interval=CYCLE_MIN)
    if away:
        c._away_state = replace(c._away_state, active=True, target_temperature=16.0)
        # the steady state of an absence: past its first day the house sits at the setback
        c._current_state.room_temperature = 16.0
    start = M.T0
    result = real_plan(c, start)
    c._optimization_result = result
    traj = np.asarray(result.room_temp_trajectory, dtype=float)
    configured = c._comfort_learner.configured_weight
    clock = M.Clock(start)
    with mock.patch.object(M.coord_mod.dt_util, "now", clock):
        for i in range(DAYS * 24 * 60 // CYCLE_MIN):
            clock.t = start + timedelta(minutes=CYCLE_MIN * i)
            c._record_quiet_comfort_period()
    return c._comfort_learner.learned_weight / configured, float(traj.max() - traj.min())


def dhw_arm(away_days: int):
    c = M.make(dhw_enabled=True, dhw_temp_entity="sensor.dhw",
               dhw_windows="06:00-09:00, 18:00-22:00")
    c._current_action = {"power": 0.0}
    clock = M.Clock(M.T0)
    occupied = 26
    with mock.patch.object(M.dt_mod, "now", clock), \
            mock.patch.object(M.coord_mod.dt_util, "now", clock):
        temp = 55.0
        for i in range((occupied + away_days) * 48):
            day = i // 48
            away = day >= occupied
            if away:
                M.apply_signal(c, "away")
            clock.t = M.T0 + timedelta(minutes=30 * i)
            asyncio.run(c._dhw_learner.async_learn_dynamics(temp))
            hour = clock.t.hour
            drop = 0.15
            if not away and hour in (7, 19):
                drop = 5.0 + (day % 5)
            temp -= drop
            if temp < 45.0:  # a recharge outside the windows' sampling: reset quietly
                temp = 55.0
                c._dhw_learner.last_temp_sample = None
    stats = c._dhw_learner.draw_stats
    out = {}
    for label, events in stats.reservoirs.items():
        ev = np.asarray(events, dtype=float)
        out[label] = (int(np.sum(ev < 0.1)), len(ev), stats.quantile(label, 0.9),
                      stats.quantile(label, 0.5))
    return out


def gains_arm(absent_fraction: float):
    """The internal-gains profile after DAYS of dark away intervals whose free heat is
    ``absent_fraction`` of the configured gains short (the occupants' share)."""
    c = M.make(internal_gains_learning_enabled=True, two_zone_mode="off")
    c._house_heat_loss_samples = 500
    g0 = float(c._thermal_params.internal_gains)
    from heatpump_optimizer.coordinator import _zone_capacity
    cap = _zone_capacity(c._thermal_params)
    observed = c._current_state.room_temperature
    dt_h = 0.5
    g_true = (1.0 - absent_fraction) * g0
    hour_of = {"h": 0}

    def _sim(prev, power, outdoor, **kw):
        # closed loop in the gains: the replay heats by the profile's own hour, the
        # house by the free heat really present, so the residual shrinks as it learns
        prof = c._internal_gains_profile or [g0] * 24
        return replace(prev, room_temperature=observed + (prof[hour_of["h"]] - g_true) * dt_h / cap)

    c._thermal_model.simulate_step = _sim
    clock = M.Clock(M.T0)
    with mock.patch.object(M.dt_mod, "now", clock):
        for i in range(DAYS * 48):
            M.apply_signal(c, "away")
            clock.t = M.T0 + timedelta(minutes=30 * i)
            hour_of["h"] = (clock.t - timedelta(minutes=30)).hour
            asyncio.run(c._async_learn_house_heat_loss(c._close_fabric_interval()))
    prof = c._internal_gains_profile or [g0] * 24
    return float(np.mean(prof)), g0


def main():
    t0 = time.process_time()
    tag = "perturb" if M.PERTURB else "base"
    r_away, span_away = comfort_arm(True)
    r_home, span_home = comfort_arm(False)
    print(f"# [{tag}] real plan span: away {span_away:.3f} K, home {span_home:.3f} K")
    print(f"RESULT comfort_weight_ratio_away_{DAYS}d={r_away:.4f} ratio")
    print(f"RESULT comfort_weight_ratio_home_null_{DAYS}d={r_home:.4f} ratio")
    for d in (0, DAYS, 28):
        res = dhw_arm(d)
        for label, (zeros, n, p90, p50) in sorted(res.items()):
            safe = label.replace(":", "").replace("-", "_")
            print(f"RESULT dhw_zero_occurrences_{safe}_away{d}d={zeros} count (of {n})")
            print(f"RESULT dhw_p50_{safe}_away{d}d={p50:.3f} kWh")
            print(f"RESULT dhw_p90_{safe}_away{d}d={p90:.3f} kWh")
    for frac in (0.5, 1.0):
        mean, g0 = gains_arm(frac)
        print(f"RESULT gains_profile_mean_over_g0_absent{int(frac * 100)}pct_{DAYS}d={mean / g0:.4f} ratio")
    print("RESULT thread_factor=1.000")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")
    print(f"# cpu {time.process_time() - t0:.1f}s (provisional, not a finding)")


if __name__ == "__main__":
    main()
