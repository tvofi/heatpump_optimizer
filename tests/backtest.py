"""Replay harness: score the optimizer against alternative strategies.

    PYTHONPATH=tests/hastub python tests/backtest.py

``PredictedSavingsSensor`` publishes a prediction with no realised counterpart,
so the savings figure has always been a simulation result rather than an
observed one. This turns it into something checkable: the same house, the same
prices and the same weather are driven through several strategies and scored on
what they actually cost and what comfort they actually delivered.

Three baselines, chosen because each fails differently:

* **always-on** — a thermostat holding the setpoint. The comparison the
  integration's savings claim is made against, so it has to be reproduced here.
* **night tariff** — heat hard between 22:00 and 06:00 and coast otherwise. The
  obvious cheap strategy a user might implement by hand, and the one the
  optimizer has to beat to be worth installing.
* **greedy cheapest hours** — buy the same energy as the baseline, but in the
  cheapest hours, ignoring the building entirely. This is the strategy that
  looks best on price alone and worst on comfort, which is exactly the trap the
  optimizer exists to avoid.

A strategy that is cheaper *and* comfortable is a genuine finding and should be
investigated, not explained away. A strategy that is cheaper while breaching the
comfort floor is not a competitor.
"""
from __future__ import annotations

import sys
from datetime import datetime

from harness import Results

import numpy as np

from profiles import DT, house, prices, weather
from heatpump_optimizer.optimizer import (
    HeatPumpOptimizer,
    OptimizationConfig,
    count_compressor_starts,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

R = Results("Replay backtest")

START = datetime(2026, 1, 15, 0, 0)


def build(two_zone: bool, dhw: bool):
    cfg = house(two_zone=two_zone, dhw=dhw)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    opt_cfg = OptimizationConfig(
        horizon_hours=24,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    model = ThermalModel(params)
    return model, opt_cfg, HeatPumpOptimizer(model, opt_cfg)


def score(model, opt_cfg, power, price_series, outdoor, wind, rain, solar, state):
    """Cost and realised comfort of an arbitrary power schedule."""
    room, slab, upper, lower = model.simulate_trajectory(
        initial_state=state,
        power_schedule=power,
        outdoor_temps=outdoor,
        wind_speeds=wind,
        precipitation=rain,
        solar_radiation=solar,
        dt_hours=DT,
    )
    if model.params.two_zone_enabled:
        indoor = np.minimum(upper[1:], lower[1:])
    else:
        indoor = room[1:]
    # The comfort floor is relaxed overnight, so comparing against the flat
    # ``min_temp`` would score every strategy as violating during the night
    # setback and hide any real breach among the noise.
    floor = np.array(
        [
            opt_cfg.get_temp_bounds((i * DT) % 24)[0]
            for i in range(len(indoor))
        ]
    )
    return {
        "cost": float(np.sum(price_series * power * DT)),
        "energy": float(np.sum(power) * DT),
        "min_room": float(np.min(indoor)),
        # Degree-hours below the comfort floor: the honest way to compare
        # strategies, since a plan can always be made cheaper by being colder.
        "violation": float(np.sum(np.maximum(0.0, floor - indoor)) * DT),
        "starts": count_compressor_starts(power),
        "peak": float(np.max(power)),
    }


def always_on(optimizer, state, outdoor, wind, rain, solar):
    """A thermostat holding the setpoint: the integration's own baseline."""
    power, _ = optimizer._compute_baseline_power(
        state, outdoor, wind, rain, solar, DT
    )
    return np.asarray(power, dtype=float)


def night_tariff(baseline, start_hour=22, end_hour=6):
    """Everything the baseline needs, bought between 22:00 and 06:00."""
    n = len(baseline)
    hours = (np.arange(n) * DT) % 24
    night = (hours >= start_hour) | (hours < end_hour)
    if not night.any():
        return baseline.copy()
    total = float(np.sum(baseline) * DT)
    plan = np.zeros(n)
    plan[night] = total / (night.sum() * DT)
    return plan


def greedy_cheapest(baseline, price_series, p_max):
    """The same energy, bought in the cheapest hours, ignoring the building."""
    plan = np.zeros(len(price_series))
    remaining = float(np.sum(baseline) * DT)
    for idx in np.argsort(price_series):
        if remaining <= 0:
            break
        take = min(p_max, remaining / DT)
        plan[idx] = take
        remaining -= take * DT
    return plan


SCENARIOS = [
    ("winter, single zone", False, "winter_typical", "winter_cold"),
    ("winter, two zone", True, "winter_typical", "winter_cold"),
    ("shoulder season", False, "shoulder", "shoulder"),
]

print(
    f"\n{'scenario':<22} {'strategy':<16} {'cost':>8} {'kWh':>7} "
    f"{'min °C':>7} {'viol':>6} {'starts':>7}"
)

for label, two_zone, price_key, weather_key in SCENARIOS:
    model, opt_cfg, optimizer = build(two_zone, dhw=False)
    price_series = prices(price_key, START)
    outdoor, wind, rain, solar = weather(weather_key, START)
    state = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
    )

    result = optimizer.optimize(state, price_series, outdoor, wind, rain, solar, START)
    optimized = np.asarray(result.power_schedule, dtype=float)

    base = always_on(optimizer, state, outdoor, wind, rain, solar)
    p_max = model.params.max_electrical_power
    candidates = {
        "optimizer": optimized,
        "always-on": base,
        "night tariff": night_tariff(base),
        "greedy cheapest": greedy_cheapest(base, price_series, p_max),
    }

    scores = {}
    for name, plan in candidates.items():
        scores[name] = score(
            model, opt_cfg, plan, price_series, outdoor, wind, rain, solar, state
        )
        s = scores[name]
        print(
            f"{label:<22} {name:<16} {s['cost']:8.2f} {s['energy']:7.2f} "
            f"{s['min_room']:7.2f} {s['violation']:6.2f} {s['starts']:7d}"
        )

    opt = scores["optimizer"]
    R.check(
        f"{label}: the optimizer beats an always-on thermostat",
        opt["cost"] < scores["always-on"]["cost"],
        f"{opt['cost']:.2f} vs {scores['always-on']['cost']:.2f}",
    )
    R.check(
        f"{label}: the optimizer beats a hand-written night schedule",
        opt["cost"] < scores["night tariff"]["cost"],
        f"{opt['cost']:.2f} vs {scores['night tariff']['cost']:.2f}",
    )
    R.check(
        f"{label}: the optimizer respects the comfort floor",
        opt["violation"] < 0.5,
        f"{opt['violation']:.2f} degree-hours below {opt_cfg.min_temp}",
    )

    greedy = scores["greedy cheapest"]
    if greedy["cost"] < opt["cost"]:
        # Only a competitor if it is also comfortable. A cheaper-and-colder
        # plan is not a better plan, it is a different set of preferences.
        R.check(
            f"{label}: nothing cheaper is also comfortable",
            greedy["violation"] > opt["violation"] + 0.5,
            f"greedy cost {greedy['cost']:.2f} at {greedy['violation']:.2f} "
            f"violation vs optimizer {opt['cost']:.2f} at {opt['violation']:.2f}",
        )
    else:
        R.check(
            f"{label}: the optimizer beats price-only greed outright", True
        )

    # Reported savings must reconcile with what the replay actually measures,
    # or the number on the dashboard is a different quantity from the one the
    # user would compute themselves.
    replayed_saving = scores["always-on"]["cost"] - opt["cost"]
    reported = result.predicted_savings + result.deferred_energy_cost
    R.check(
        f"{label}: reported savings match the replay",
        abs(replayed_saving - reported) < max(1.0, abs(reported) * 0.1),
        f"replay {replayed_saving:.2f} vs reported {reported:.2f}",
    )

    R.check(
        f"{label}: the plan does not chatter",
        opt["starts"] <= max(6, int(len(optimized) * DT / 3)),
        f"{opt['starts']} compressor starts in 24 h",
        # Measure before paying for a cycling penalty: if realistic plans do
        # not chatter, the penalty is not worth its cost in savings.
    )

sys.exit(R.close("BACKTEST CHECKS"))
