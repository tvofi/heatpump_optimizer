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


def build_case(two_zone: bool, dhw: bool):
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


def always_on(optimizer, state, outdoor, wind, rain, solar, comfort_targets):
    """A thermostat following the user's schedule: the integration's baseline.

    ``comfort_targets`` is not optional. Since v3.8.0 the optimizer reports its
    savings against a thermostat that follows the configured day/night
    schedule, so replaying a *flat* one here compares two different references
    and the reconciliation check below fails for a reason that has nothing to
    do with the plan.
    """
    power, _ = optimizer._compute_baseline_power(
        state, outdoor, wind, rain, solar, DT, comfort_targets
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
    model, opt_cfg, optimizer = build_case(two_zone, dhw=False)
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

    comfort_targets = np.array(
        [opt_cfg.get_comfort_temp((i * DT) % 24) for i in range(len(price_series))]
    )
    base = always_on(
        optimizer, state, outdoor, wind, rain, solar, comfort_targets
    )
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
    # A 24-hour bill is not the whole cost of a 24-hour plan: a strategy can
    # look cheap by ending the day colder and leaving the heat to be bought
    # back tomorrow. The integration already prices that as its deferred
    # energy settlement, so the comparison uses it too -- otherwise the
    # cheapest "strategy" is always the one that simply stops heating.
    #
    # Measured on the shoulder scenario, this is not a hypothetical: greedy
    # spends 3.35 against the optimizer's 4.02 but ends 4.3 kWh colder, which
    # settles at 1.01 SEK. Its true cost is 4.36.
    caps = optimizer._settlement_caps(outdoor)
    opt_end = optimizer._replay_end_state(
        state, optimized, outdoor, wind, rain, solar, DT
    )
    greedy_end = optimizer._replay_end_state(
        state, candidates["greedy cheapest"], outdoor, wind, rain, solar, DT
    )
    greedy_settled = greedy["cost"] + optimizer._deferred_energy_cost(
        opt_end, greedy_end, price_series, outdoor, caps=caps
    )
    if greedy_settled < opt["cost"]:
        # Still a competitor after settling: only excused if it is colder.
        R.check(
            f"{label}: nothing cheaper is also comfortable",
            greedy["violation"] > opt["violation"] + 0.5,
            f"greedy settled {greedy_settled:.2f} at {greedy['violation']:.2f} "
            f"violation vs optimizer {opt['cost']:.2f} at {opt['violation']:.2f}",
        )
    else:
        R.check(
            f"{label}: the optimizer beats price-only greed outright",
            True,
            f"greedy {greedy['cost']:.2f} + {greedy_settled - greedy['cost']:.2f} "
            f"left unstored = {greedy_settled:.2f} vs {opt['cost']:.2f}",
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


# ===========================================================================
# Storage sizing (item 29): what is a real buffer tank worth?
# ===========================================================================
#
# The empirical check the item deferred to "after implementation". Two arms
# under identical valve physics -- a 750 L accumulator against a tank just
# below the store threshold -- each planned AND scored under its own model,
# with the end state valued symmetrically against the start at the refill
# reference.
#
# Measurement design, learned the hard way (three failed designs are recorded
# in the item, and two more fell in this session):
#
# * Planning one arm against the other's model measures model mismatch, not
#   storage (20 % "gain" at flat prices).
# * Valve-vs-no-valve compares two different comfort trajectories -- the
#   valve arm rides cooler, which is a comfort-for-money trade, not storage.
# * Big-tank-vs-tiny-tank still differs in pass-through dynamics: a small
#   tank's temperature spikes when the pump runs, and the Carnot flow term
#   prices those spikes. Both residual asymmetries are *price-independent*,
#   which is the fix: difference the gain against the flat-price null
#   control, and what survives is the part only a price spread can produce
#   -- storage.
_STORE_START = 25.0  # C: too cold to coast for free, so charging is a choice


def _storage_arm(volume: float, price_profile: str):
    cfg = house(
        two_zone=True, dhw=False,
        buffer_tank_volume=volume,
        buffer_max_temperature=70.0,
        mixing_valve_mode="manual",
    )
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    model = ThermalModel(params)
    opt_cfg = OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    optimizer = HeatPumpOptimizer(model, opt_cfg)
    price_series = prices(price_profile, START)
    outdoor, wind, rain, solar = weather("winter_cold", START)
    state = ThermalState(
        room_temperature=20.0, upper_floor_temperature=20.0,
        lower_floor_temperature=20.0, slab_temperature=21.0,
        buffer_tank_temperature=_STORE_START,
        outdoor_temperature=float(outdoor[0]),
    )
    result = optimizer.optimize(
        state, price_series, outdoor, wind, rain, solar, START
    )
    power = np.asarray(result.power_schedule)
    s = score(model, opt_cfg, power, price_series, outdoor, wind, rain,
              solar, state)
    # Symmetric end-state settlement against the start, at the same refill
    # reference the integration's own settlement uses. Symmetric because the
    # arms are peers, not a plan against a thermostat: a surplus carried into
    # tomorrow is worth exactly what a deficit costs.
    room, slab, upper, lower = model.simulate_trajectory(
        state, power, outdoor, wind, rain, solar, DT
    )
    buf = model.last_buffer_trajectory
    p = model.params
    e_delta = (
        p.upper_floor_thermal_mass * (upper[-1] - 20.0)
        + p.lower_floor_thermal_mass * (lower[-1] - 20.0)
        + p.slab_thermal_mass * (slab[-1] - 21.0)
        + p.buffer_tank_thermal_mass * (min(buf[-1], 70.0) - _STORE_START)
    )
    refill = float(np.percentile(price_series, 25))
    cop_end = model.compute_cop(float(np.mean(outdoor)))
    return s["cost"] - e_delta * refill / cop_end, s["violation"]


_store_gain = {}
for _profile in ("winter_typical", "winter_extreme", "flat"):
    _small, _v_small = _storage_arm(99.0, _profile)
    _large, _v_large = _storage_arm(750.0, _profile)
    _store_gain[_profile] = _small - _large
    R.check(
        f"storage {_profile}: both arms hold comfort",
        _v_small < 0.5 and _v_large < 0.5,
        f"violations {_v_small:.2f} / {_v_large:.2f} degree-hours -- a cheaper "
        "arm that is colder is not cheaper",
    )

R.check(
    "storage pays where the spread is wide, beyond any arm asymmetry",
    _store_gain["winter_typical"] - _store_gain["flat"] > 1.0,
    f"typical {_store_gain['winter_typical']:+.2f} vs flat null "
    f"{_store_gain['flat']:+.2f} SEK/day at 750 L",
)
R.check(
    "and an extreme spread is worth more than a typical one",
    _store_gain["winter_extreme"] > _store_gain["winter_typical"],
    f"extreme {_store_gain['winter_extreme']:+.2f} vs typical "
    f"{_store_gain['winter_typical']:+.2f} SEK/day",
)


# ===========================================================================
# Wood furnace sizing (item 28): what is knowing about a burn worth?
# ===========================================================================
#
# The check the item asks for before the estimator is built: "how much does
# the optimizer save if it *knows* the furnace covers part of the load,
# versus ignoring it". A value-of-information measurement: both arms live in
# the same physics (the fire burns either way -- lighting it is human
# behaviour the plan never controls), but only one arm's plan gets the
# forecast. The blind arm's model mismatch is not a confound here; it is
# precisely the cost of ignorance being measured. Null control: with no burn
# the two arms are the same plan, asserted byte-for-byte in features.py.


def _furnace_arm(informed: bool, burn: np.ndarray):
    cfg = house(two_zone=True, dhw=False)
    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = False
    model = ThermalModel(params)
    opt_cfg = OptimizationConfig(
        horizon_hours=24, time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    optimizer = HeatPumpOptimizer(model, opt_cfg)
    price_series = prices("winter_typical", START)
    outdoor, wind, rain, solar = weather("winter_cold", START)
    state = ThermalState(
        room_temperature=20.5, upper_floor_temperature=20.5,
        lower_floor_temperature=20.5, slab_temperature=22.0,
        buffer_tank_temperature=30.0,
        outdoor_temperature=float(outdoor[0]),
    )
    result = optimizer.optimize(
        state, price_series, outdoor, wind, rain, solar, START,
        external_heat_kw=burn if informed else None,
    )
    power = np.asarray(result.power_schedule)
    # Score under the real physics: the fire burns whether or not the plan
    # knew about it.
    room, slab, upper, lower = model.simulate_trajectory(
        state, power, outdoor, wind, rain, solar, DT, external_heat_kw=burn
    )
    indoor = np.minimum(upper[1:], lower[1:])
    floor = np.array(
        [opt_cfg.get_temp_bounds((i * DT) % 24)[0] for i in range(len(indoor))]
    )
    violation = float(np.sum(np.maximum(0.0, floor - indoor)) * DT)
    cost = float(np.sum(price_series * power * DT))
    p = model.params
    e_delta = (
        p.upper_floor_thermal_mass * (upper[-1] - 20.5)
        + p.lower_floor_thermal_mass * (lower[-1] - 20.5)
        + p.slab_thermal_mass * (slab[-1] - 22.0)
    )
    refill = float(np.percentile(price_series, 25))
    cop_end = model.compute_cop(float(np.mean(outdoor)))
    return cost - e_delta * refill / cop_end, violation


# An evening fire: lit at 17:00, 8 kW fading through 23:00 -- covering the
# whole house load straight through the evening price peak.
_burn = np.zeros(96)
_burn[68:80] = 8.0   # 17:00-20:00
_burn[80:92] = 4.0   # 20:00-23:00, dying down
_aware_cost, _aware_viol = _furnace_arm(True, _burn)
_blind_cost, _blind_viol = _furnace_arm(False, _burn)
R.check(
    "knowing about an evening burn is worth real money",
    _blind_cost - _aware_cost > 1.0,
    f"blind {_blind_cost:.2f} vs informed {_aware_cost:.2f} SEK "
    f"({_blind_cost - _aware_cost:+.2f}/day for an evening fire)",
)
R.check(
    "and the informed plan still holds comfort",
    _aware_viol < 0.5,
    f"violation {_aware_viol:.2f} degree-hours",
)

sys.exit(R.close("BACKTEST CHECKS"))
