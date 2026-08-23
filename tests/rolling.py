"""Closed-loop simulation: many days of re-planning against a house that drifts.

    PYTHONPATH=tests/hastub python tests/rolling.py

Every other test solves once. That is not how the integration runs: it re-plans
every half hour against a house whose real behaviour never quite matches the
model, and it feeds the outcome back into learners that change the model.

Whole classes of failure only appear in that loop:

* **Drift.** A plan that is fine in isolation but, applied one step at a time
  and re-planned, walks the house somewhere it should not go.
* **Oscillation.** Consecutive plans that disagree, so the pump is told to heat
  hard and then not at all, and nothing settles.
* **Learner divergence.** A correction that chases its own tail, because the
  model it corrects is the one generating the residual it learns from.
* **Deadline failures.** Anti-legionella and demand windows that are always
  "later" until suddenly they are missed.

So this runs a real plant model, deliberately mismatched from the optimizer's
model, and drives the whole cycle for several simulated days.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta

from harness import Results

import numpy as np

from harness import FakeEntry, FakeHass
from homeassistant.util import dt as dt_util

from profiles import DT, house, prices, weather
from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

R = Results("Closed-loop rolling simulation")

START = datetime(2026, 1, 15, 0, 0)
#: How often the coordinator re-plans, in hours. The default is 30 minutes;
#: two hours keeps the test to a sensible runtime while still exercising the
#: loop many times over.
REPLAN_HOURS = 2.0
DAYS = 3


def tile(series, steps):
    series = np.asarray(series, dtype=float)
    if len(series) >= steps:
        return series[:steps]
    return np.tile(series, int(np.ceil(steps / len(series))))[:steps]


def run_rolling(
    *,
    days: int = DAYS,
    dhw: bool = True,
    two_zone: bool = False,
    plant_error: float = 1.25,
    price_profile: str = "winter_typical",
    weather_profile: str = "winter_cold",
    horizon_hours: int = 24,
    learn: bool = False,
    config: dict | None = None,
):
    """Drive the optimizer round its own loop for ``days`` simulated days.

    ``plant_error`` is the ratio of the *real* house's heat loss to the one the
    optimizer believes. A value of 1.0 would be a model that is exactly right,
    which is the one case that never happens in the field; 1.25 means the house
    leaks a quarter more than configured, which is the situation the
    self-learning correction exists for.
    """
    cfg = house(two_zone=two_zone, dhw=dhw)
    cfg.update(config or {})

    # The optimizer's model.
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    model = ThermalModel(params)

    # The real house: the same, but leakier. The optimizer never sees this.
    plant_params = ThermalParameters.from_config(cfg)
    plant_params.dhw_enabled = dhw
    plant_params.heat_loss_coefficient *= plant_error
    plant_params.upper_floor_heat_loss *= plant_error
    plant_params.lower_floor_heat_loss *= plant_error
    plant = ThermalModel(plant_params)

    opt_cfg = OptimizationConfig(
        horizon_hours=horizon_hours,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    optimizer = HeatPumpOptimizer(model, opt_cfg)

    # When learning, the *real* coordinator's estimator is driven rather than a
    # copy of its arithmetic. A test that reimplements the learner would only
    # prove the reimplementation works.
    learner = None
    if learn:
        learner = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=cfg))
        learner._thermal_params = params
        learner._thermal_model = model
        learner._opt_config = opt_cfg
        learner._optimizer = optimizer

    total_steps = int(days * 24 / DT)
    horizon_steps = int(horizon_hours / DT)
    span = total_steps + horizon_steps + 4

    price_series = tile(prices(price_profile, START), span)
    outdoor, wind, rain, solar = (tile(a, span) for a in weather(weather_profile, START))

    state = ThermalState(
        room_temperature=cfg["target_temperature"],
        slab_temperature=cfg["target_temperature"] + 1.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=cfg["target_temperature"],
        lower_floor_temperature=cfg["target_temperature"],
        dhw_temperature=52.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )

    replan_every = max(1, int(REPLAN_HOURS / DT))
    windows = parse_windows(cfg.get("dhw_windows", "") or "")

    history = {
        "room": [], "dhw": [], "space_power": [], "dhw_power": [],
        "price": [], "cost": [], "hours_since_legionella": [],
        "replan_first_step": [], "status": [],
        "heat_loss_scale": [], "heat_loss_samples": [],
    }
    plan = None

    for step in range(total_steps):
        now = START + timedelta(hours=step * DT)

        if step % replan_every == 0:
            plan = optimizer.optimize(
                state,
                price_series[step : step + horizon_steps],
                outdoor[step : step + horizon_steps],
                wind[step : step + horizon_steps],
                rain[step : step + horizon_steps],
                solar[step : step + horizon_steps],
                now,
            )
            history["status"].append(plan.status)
            history["replan_first_step"].append(float(plan.power_schedule[0]))

        offset = step % replan_every
        space_power = float(plan.power_schedule[offset])
        dhw_power = (
            float(plan.dhw_power_schedule[offset])
            if plan.dhw_power_schedule
            else 0.0
        )

        # Advance the *real* house by one step under that command.
        if dhw:
            room, slab, upper, lower, tank = plant.simulate_trajectory_with_dhw(
                initial_state=state,
                space_power_schedule=np.array([space_power]),
                dhw_power_schedule=np.array([dhw_power]),
                outdoor_temps=outdoor[step : step + 1],
                wind_speeds=wind[step : step + 1],
                precipitation=rain[step : step + 1],
                solar_radiation=solar[step : step + 1],
                start_hour=now.hour + now.minute / 60.0,
                dt_hours=DT,
            )
        else:
            room, slab, upper, lower = plant.simulate_trajectory(
                initial_state=state,
                power_schedule=np.array([space_power]),
                outdoor_temps=outdoor[step : step + 1],
                wind_speeds=wind[step : step + 1],
                precipitation=rain[step : step + 1],
                solar_radiation=solar[step : step + 1],
                dt_hours=DT,
            )
            tank = [state.dhw_temperature, state.dhw_temperature]

        state = ThermalState(
            room_temperature=float(room[-1]),
            slab_temperature=float(slab[-1]),
            outdoor_temperature=float(outdoor[step]),
            upper_floor_temperature=float(upper[-1]),
            lower_floor_temperature=float(lower[-1]),
            dhw_temperature=float(tank[-1]),
            buffer_tank_temperature=state.buffer_tank_temperature,
            dhw_hours_since_legionella=(
                0.0
                if float(tank[-1]) >= params.dhw_legionella_temp - 1.0
                else (state.dhw_hours_since_legionella or 0.0) + DT
            ),
        )

        if learner is not None:
            # The estimator keys off wall-clock time, so the clock is moved to
            # the simulated instant before each observation.
            dt_util.freeze(now + timedelta(hours=DT))
            learner._current_state = state
            learner._current_action = {"power": space_power, "dhw_power": dhw_power}
            learner._weather_forecast = [
                {
                    "wind_speed": float(wind[step]),
                    "precipitation": float(rain[step]),
                }
            ]
            asyncio.run(learner._async_learn_house_heat_loss())
            history["heat_loss_scale"].append(learner._house_heat_loss_scale)
            history["heat_loss_samples"].append(learner._house_heat_loss_samples)

        history["room"].append(
            min(float(upper[-1]), float(lower[-1])) if two_zone else float(room[-1])
        )
        history["dhw"].append(float(tank[-1]))
        history["space_power"].append(space_power)
        history["dhw_power"].append(dhw_power)
        history["price"].append(float(price_series[step]))
        history["cost"].append((space_power + dhw_power) * DT * float(price_series[step]))
        history["hours_since_legionella"].append(state.dhw_hours_since_legionella)

    if learner is not None:
        dt_util.freeze(None)

    return {
        "history": {k: np.asarray(v) for k, v in history.items()},
        "params": params,
        "config": opt_cfg,
        "windows": windows,
        "days": days,
        "total_steps": total_steps,
    }


def floor_for(config, steps):
    return np.array(
        [config.get_temp_bounds((i * DT) % 24)[0] for i in range(steps)]
    )


# ===========================================================================
# The loop must be stable
# ===========================================================================
R.section("Stability over three days")

base = run_rolling()
h = base["history"]
n = base["total_steps"]
floor = floor_for(base["config"], n)

R.check("every plan solved", all("fail" not in s for s in h["status"]), str(set(h["status"])))
R.check(
    "the house never runs away",
    float(h["room"].min()) > 5.0 and float(h["room"].max()) < 35.0,
    f"{h['room'].min():.1f}..{h['room'].max():.1f} °C",
)

violation = float(np.sum(np.maximum(0.0, floor - h["room"])) * DT)
R.check(
    "comfort holds across three days despite a 25% model error",
    violation < 3.0,
    f"{violation:.2f} degree-hours below the floor over {base['days']} days",
)

# The loop must settle rather than wander: compare each day to the next.
per_day = n // base["days"]
day_means = [
    float(np.mean(h["room"][d * per_day : (d + 1) * per_day]))
    for d in range(base["days"])
]
R.check(
    "the indoor temperature settles rather than drifting",
    max(day_means) - min(day_means) < 1.0,
    ", ".join(f"day {i + 1}: {m:.2f} °C" for i, m in enumerate(day_means)),
)

day_costs = [
    float(np.sum(h["cost"][d * per_day : (d + 1) * per_day]))
    for d in range(base["days"])
]
R.check(
    "daily cost is stable, not escalating",
    max(day_costs) / max(min(day_costs), 1e-6) < 1.6,
    ", ".join(f"day {i + 1}: {c:.1f}" for i, c in enumerate(day_costs)),
)

# Consecutive plans disagreeing wildly means the pump is told to heat hard and
# then not at all. Every re-plan sees slightly different state, so some change
# is expected; reversing between the extremes every time is not.
first_steps = h["replan_first_step"]
p_max = base["params"].max_electrical_power
swings = np.abs(np.diff(first_steps))
R.check(
    "consecutive plans do not contradict each other",
    float(np.mean(swings)) < p_max * 0.5,
    f"mean swing {float(np.mean(swings)):.2f} kW of {p_max:.1f} kW",
)

# The plan must respond to price, not just to temperature.
expensive = h["price"] >= np.percentile(h["price"], 75)
cheap = h["price"] <= np.percentile(h["price"], 25)
total_power = h["space_power"] + h["dhw_power"]
R.check(
    "cheap hours are used more than expensive ones, over three days",
    float(np.mean(total_power[cheap])) > float(np.mean(total_power[expensive])),
    f"cheap {float(np.mean(total_power[cheap])):.2f} kW vs "
    f"expensive {float(np.mean(total_power[expensive])):.2f} kW",
)


# ===========================================================================
# Hot water deadlines, over repeated days
# ===========================================================================
R.section("Hot water over three days")

hours = np.array([(START.hour + i * DT) % 24 for i in range(n)])
inside = np.array([hour_in_windows(float(x), base["windows"]) for x in hours])
if inside.any():
    worst = float(h["dhw"][inside].min())
    R.check(
        "hot water is available in every demand window, every day",
        worst >= base["params"].dhw_min_temp - 2.0,
        f"worst {worst:.1f} °C against a {base['params'].dhw_min_temp:.0f} °C minimum",
    )

R.check(
    "the tank never exceeds its rating during operation",
    float(h["dhw"].max()) <= base["params"].dhw_max_temp + 1.0,
    f"reached {float(h['dhw'].max()):.1f} °C",
)

# The legionella timer must not ratchet upward forever: over three days with a
# seven-day interval it may legitimately never fire, but it must not be
# *ignored* once due.
R.check(
    "the legionella clock advances sensibly",
    float(h["hours_since_legionella"].max()) <= 20.0 + base["days"] * 24 + 1.0,
    f"reached {float(h['hours_since_legionella'].max()):.0f} h",
)


# ===========================================================================
# The same loop under harder conditions
# ===========================================================================
R.section("Harder conditions")

variants = {
    "two zone": dict(two_zone=True),
    "no hot water": dict(dhw=False),
    "model 40% optimistic": dict(plant_error=1.4),
    "model 20% pessimistic": dict(plant_error=0.8),
    "mild and windy": dict(weather_profile="winter_mild"),
    "shoulder season": dict(price_profile="shoulder", weather_profile="shoulder"),
    "flat prices": dict(price_profile="flat"),
    "short horizon": dict(horizon_hours=12),
}

for label, spec in variants.items():
    try:
        run = run_rolling(days=2, **spec)
    except Exception as err:  # noqa: BLE001 - a crash is the finding
        R.check(f"{label}: the loop survives", False, f"{type(err).__name__}: {err}")
        continue

    hist = run["history"]
    steps = run["total_steps"]
    bound = floor_for(run["config"], steps)
    breach = float(np.sum(np.maximum(0.0, bound - hist["room"])) * DT)
    finite = bool(
        np.all(np.isfinite(hist["room"])) and np.all(np.isfinite(hist["space_power"]))
    )
    runaway = float(hist["room"].min()) < 5.0 or float(hist["room"].max()) > 35.0

    R.check(
        f"{label}: two days stay sound",
        finite and not runaway and breach < 8.0,
        f"breach {breach:.2f} degree-hours, room "
        f"{hist['room'].min():.1f}..{hist['room'].max():.1f} °C",
    )

# A pessimistic model -- the house is *tighter* than configured -- must not
# make the plan overheat, which is the failure mode symmetric to under-heating
# and much easier to miss because nobody complains about a warm house until
# the bill arrives.
tight = run_rolling(days=2, plant_error=0.8)
overshoot = float(
    np.sum(
        np.maximum(0.0, tight["history"]["room"] - tight["config"].max_temp)
    )
    * DT
)
R.check(
    "a tighter-than-configured house is not overheated",
    overshoot < 3.0,
    f"{overshoot:.2f} degree-hours above the maximum",
)


# ===========================================================================
# The self-learning correction, end to end
# ===========================================================================
R.section("Self-learning in the loop")

# Nothing else tests the heat-loss learner against a house that really is
# different from its model -- features.py tests the modules in isolation, and
# every other suite hands the optimizer a model that is true by construction.
# This is the only place the correction has to actually work.
#
# The comfort-breach comparison below only discriminates while the *real*
# house's worst-hour demand exceeds the pump: with headroom, the 2-hourly
# replanning alone holds the floor even on a wrong model, and both arms
# breach by exactly zero. That property used to hold by accident -- the old
# 0.15/m/s wind default inflated the loss until the 6 kW pump bound -- so it
# is now set explicitly: at 4.25 kW the mis-modelled house genuinely cannot
# coast through the cold nights (measured: 6.7 degree-hours of breach
# uncorrected, 0.0 with learning), and knowing the true loss — pre-heating
# the slab through the milder, cheaper hours — is worth real comfort.
TRUE_ERROR = 1.35
_BOUND_PUMP = {"heat_pump_max_power": 4.25}
learned = run_rolling(
    days=3, dhw=False, plant_error=TRUE_ERROR, learn=True, config=_BOUND_PUMP
)
uncorrected = run_rolling(
    days=3, dhw=False, plant_error=TRUE_ERROR, config=_BOUND_PUMP
)

scale = learned["history"]["heat_loss_scale"]
samples = learned["history"]["heat_loss_samples"]

R.check(
    "the learner takes samples",
    int(samples[-1]) > 10,
    f"{int(samples[-1])} samples over three days",
)
R.check(
    "the learned correction moves towards the real error",
    scale[-1] > scale[0] + 0.05,
    f"scale went {scale[0]:.3f} -> {scale[-1]:.3f}, truth {TRUE_ERROR}",
)
R.check(
    "and does not overshoot it",
    scale[-1] <= TRUE_ERROR + 0.15,
    f"{scale[-1]:.3f} against a true error of {TRUE_ERROR}",
)
R.check(
    "the correction converges rather than oscillating",
    float(np.std(scale[-len(scale) // 4 :])) < 0.05,
    f"last-quarter spread {float(np.std(scale[-len(scale) // 4:])):.4f}",
)

steps = learned["total_steps"]
bound = floor_for(learned["config"], steps)
breach_learned = float(np.sum(np.maximum(0.0, bound - learned["history"]["room"])) * DT)
breach_plain = float(
    np.sum(np.maximum(0.0, bound - uncorrected["history"]["room"])) * DT
)
R.check(
    "learning reduces the comfort breach it exists to fix",
    breach_learned < breach_plain,
    f"{breach_plain:.2f} -> {breach_learned:.2f} degree-hours",
)

# A model that is already right must be left alone: a learner that wanders on
# correct data is worse than no learner, because it breaks a working install.
correct = run_rolling(days=2, dhw=False, plant_error=1.0, learn=True)
drift = correct["history"]["heat_loss_scale"]
R.check(
    "a correct model is not corrupted by the learner",
    abs(float(drift[-1]) - 1.0) < 0.12,
    f"scale drifted to {float(drift[-1]):.3f} on a model that was already right",
)


sys.exit(R.close("ROLLING CHECKS"))
