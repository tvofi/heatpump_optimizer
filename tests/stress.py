"""Stress the optimizer across realistic combinations, and check the economics.

    PYTHONPATH=tests/hastub python tests/stress.py

The other suites each answer a narrow question. `validate.py` checks a fixed
list of scenarios, `golden.py` checks that behaviour has not *changed*, and
`features.py` checks each module in isolation. None of them asks the question
that actually matters:

    across the whole space of houses, seasons, tariffs and feature
    combinations a real user might have, does this thing behave sensibly?

So this sweeps a combinatorial matrix and asserts the invariants that must hold
everywhere. Failures here are the interesting ones: they are conditions nobody
thought to write a scenario for.

Three families of check:

* **Physical.** Power within bounds, temperatures finite, tank never boiled,
  energy conserved between the schedule and the slot summaries. A violation is
  unambiguously a bug.
* **Economic.** Cheaper than a thermostat when there is price spread to exploit;
  never worse than one; costs reconcile with the schedule. These are the claims
  the integration makes, checked rather than assumed.
* **Comfort.** The floor is respected to within the tolerance the soft penalty
  allows, and hot water is available when it was promised. A cheaper plan that
  is colder is not a better plan.
"""
from __future__ import annotations

import itertools
import sys
from datetime import datetime, timedelta

from harness import Results

import numpy as np

from profiles import DT, house, prices, weather
from heatpump_optimizer import pv as pv_model
from heatpump_optimizer.dhw_schedule import hour_in_windows, parse_windows
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.presets import (
    BuildingPreset,
    EMITTER_FLOOR,
    EMITTER_RADIATORS,
    ERA_1960_1980,
    ERA_POST_2005,
    ERA_PRE_1960,
    STRUCTURE_CONCRETE_SLAB,
    STRUCTURE_MASONRY,
    STRUCTURE_TIMBER_CRAWLSPACE,
    derive,
)
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

R = Results("Stress and economics")

START = datetime(2026, 1, 15, 0, 0)

# Season -> (price profile, weather profile). Paired because a summer price
# curve with a January weather profile is not a case any user has.
SEASONS = {
    "winter": ("winter_typical", "winter_cold"),
    "winter_extreme": ("winter_extreme", "winter_cold"),
    "winter_mild": ("winter_typical", "winter_mild"),
    "shoulder": ("shoulder", "shoulder"),
    "summer": ("summer_typical", "summer_warm"),
    "summer_negative": ("summer_negative", "summer_warm"),
    "flat": ("flat", "winter_cold"),
}

# Building archetypes covering the light/heavy and leaky/tight corners.
BUILDINGS = {
    "light_new": BuildingPreset(
        structure=STRUCTURE_TIMBER_CRAWLSPACE,
        era=ERA_POST_2005,
        heated_area_m2=120,
        lower_emitter=EMITTER_RADIATORS,
    ),
    "heavy_old": BuildingPreset(
        structure=STRUCTURE_MASONRY,
        era=ERA_PRE_1960,
        heated_area_m2=200,
        lower_emitter=EMITTER_FLOOR,
    ),
    "typical_slab": BuildingPreset(
        structure=STRUCTURE_CONCRETE_SLAB,
        era=ERA_1960_1980,
        heated_area_m2=150,
        lower_emitter=EMITTER_FLOOR,
    ),
}


def build(
    *,
    season: str,
    building: str | None = None,
    two_zone: bool = False,
    dhw: bool = True,
    tariff: bool = False,
    pv: bool = False,
    cycling: float = 0.0,
    cop_scale: float = 1.0,
    hours: int = 24,
    state: dict | None = None,
    config: dict | None = None,
):
    """One fully specified run of the optimizer."""
    price_key, weather_key = SEASONS[season]
    cfg = house(two_zone=two_zone, dhw=dhw)
    if building:
        preset = BuildingPreset(**{**vars(BUILDINGS[building]), "two_zone": two_zone})
        derived = derive(preset)
        derived.pop("heating_response_hours", None)
        cfg.update(derived)
    cfg.update(config or {})

    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    params.cop_scale = cop_scale

    opt_cfg = OptimizationConfig(
        horizon_hours=hours,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
        cycling_cost=cycling,
    )
    if tariff:
        opt_cfg.peak_price_per_kw = 20.0
        opt_cfg.peak_threshold_kw = 3.0
        opt_cfg.baseline_load_kw = 1.5

    n = int(hours / DT)

    def fit(arr):
        arr = np.asarray(arr, dtype=float)
        if len(arr) >= n:
            return arr[:n]
        return np.tile(arr, int(np.ceil(n / len(arr))))[:n]

    price_series = fit(prices(price_key, START))
    outdoor, wind, rain, solar = (fit(a) for a in weather(weather_key, START))

    surplus = None
    if pv:
        production = np.clip(solar / 1000.0 * 8.0 * 0.8, 0, 8.0)
        surplus = np.clip(production - 1.0, 0.0, None)
        # Prices stay the raw import series. Since v3.8.0 the optimizer
        # prices the surplus-covered energy at the export compensation
        # itself, piecewise per step, exactly as the coordinator wires it —
        # substituting a cliff price into the series here would double-count
        # the discount.
        opt_cfg.pv_export_price = 0.25

    initial = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    for key, value in (state or {}).items():
        setattr(initial, key, value)

    model = ThermalModel(params)
    optimizer = HeatPumpOptimizer(model, opt_cfg)
    result = optimizer.optimize(
        initial, price_series, outdoor, wind, rain, solar, START, None, surplus
    )
    return {
        "result": result,
        "model": model,
        "params": params,
        "config": opt_cfg,
        "cfg": cfg,
        "prices": price_series,
        "outdoor": outdoor,
        "wind": wind,
        "rain": rain,
        "solar": solar,
        "initial": initial,
        "optimizer": optimizer,
        "surplus": surplus,
        "n": n,
    }


# ===========================================================================
# Invariants that must hold in every scenario
# ===========================================================================


def check_invariants(label: str, run: dict) -> list[str]:
    """Return a list of violations. Empty means the plan is sound."""
    problems = []
    result = run["result"]
    params = run["params"]
    cfg = run["config"]
    n = run["n"]

    space = np.asarray(result.power_schedule, dtype=float)
    dhw = np.asarray(result.dhw_power_schedule or np.zeros(n), dtype=float)
    p_max = params.max_electrical_power

    # --- physical ---------------------------------------------------------
    if not np.all(np.isfinite(space)):
        problems.append("space power is not finite")
    if not np.all(np.isfinite(dhw)):
        problems.append("DHW power is not finite")
    if space.min() < -1e-6:
        problems.append(f"negative space power {space.min():.3f}")
    if dhw.size and dhw.min() < -1e-6:
        problems.append(f"negative DHW power {dhw.min():.3f}")
    # The compressor serves one circuit at a time, so the *sum* is what the
    # hardware has to deliver.
    combined = space + (dhw if dhw.size == space.size else 0.0)
    if combined.max() > p_max + 1e-3:
        problems.append(
            f"combined power {combined.max():.3f} exceeds the {p_max:.1f} kW pump"
        )

    for name, trajectory in (
        ("room", result.room_temp_trajectory),
        ("slab", result.slab_temp_trajectory),
        ("upper", result.upper_temp_trajectory),
        ("lower", result.lower_temp_trajectory),
        ("dhw", result.dhw_temp_trajectory),
    ):
        if not trajectory:
            continue
        arr = np.asarray(trajectory, dtype=float)
        if not np.all(np.isfinite(arr)):
            problems.append(f"{name} trajectory is not finite")
        elif arr.min() < -50 or arr.max() > 120:
            problems.append(
                f"{name} trajectory left physical reality "
                f"({arr.min():.1f}..{arr.max():.1f} °C)"
            )

    if result.dhw_temp_trajectory:
        peak = float(np.max(result.dhw_temp_trajectory))
        # A tank that *starts* above its rating cannot be brought down by a
        # plan -- there is no way to un-heat water, only to stop adding heat
        # and let it coast. So the bound is the rating or the starting
        # temperature, whichever is higher.
        ceiling = max(params.dhw_max_temp, run["initial"].dhw_temperature)
        if peak > ceiling + 1.0:
            problems.append(
                f"tank reached {peak:.1f} °C, over its {ceiling:.0f} °C ceiling"
            )

    # --- accounting -------------------------------------------------------
    # With PV surplus the cost is piecewise — covered energy at the export
    # compensation, the rest at import — so the plain price-times-power sum
    # is only the right reference when there is no surplus.
    surplus = run.get("surplus")
    if surplus is not None:
        recomputed = pv_model.piecewise_cost(
            np.asarray(result.prices),
            np.asarray(surplus)[: combined.size],
            run["config"].pv_export_price,
            combined,
            DT,
        )
    else:
        recomputed = float(np.sum(np.asarray(result.prices) * combined * DT))
    if abs(recomputed - result.predicted_cost) > max(0.05, abs(recomputed) * 0.01):
        problems.append(
            f"predicted cost {result.predicted_cost:.2f} does not match the "
            f"schedule's {recomputed:.2f}"
        )
    if result.baseline_cost < -1e-6:
        problems.append(f"negative baseline cost {result.baseline_cost:.2f}")
    if not -100.0 <= result.savings_percentage <= 100.0:
        problems.append(f"savings {result.savings_percentage:.1f}% out of range")

    # --- provenance and reporting ----------------------------------------
    if len(result.price_known) != len(result.prices):
        problems.append("price provenance mask does not cover the horizon")
    if len(result.space_reasons) != n:
        problems.append("reason codes do not cover the horizon")
    else:
        unexplained = sum(
            1
            for i, p in enumerate(space)
            if p > 0.05 and result.space_reasons[i] == "idle"
        )
        if unexplained:
            problems.append(f"{unexplained} heating steps have no reason code")

    return problems


#: How far below the comfort floor a plan may sit before it counts as a
#: failure rather than as the soft constraint doing its job.
COMFORT_TOLERANCE_DEGREE_HOURS = 1.5


def best_possible_violation(run: dict) -> float:
    """Degree-hours below the floor with the pump running flat out.

    An undersized pump in a leaky house cannot hold the comfort floor at all,
    and calling that a planning bug would be blaming the optimizer for physics.
    """
    model = run["model"]
    room, _, upper, lower = model.simulate_trajectory(
        initial_state=run["initial"],
        power_schedule=np.full(run["n"], run["params"].max_electrical_power),
        outdoor_temps=run["outdoor"],
        wind_speeds=run["wind"],
        precipitation=run["rain"],
        solar_radiation=run["solar"],
        dt_hours=DT,
    )
    if run["params"].two_zone_enabled:
        indoor = np.minimum(upper[1:], lower[1:])
    else:
        indoor = room[1:]
    cfg = run["config"]
    floor = np.array(
        [cfg.get_temp_bounds((i * DT) % 24)[0] for i in range(len(indoor))]
    )
    return float(np.sum(np.maximum(0.0, floor - indoor)) * DT)


def comfort_violation(run: dict) -> float:
    """Degree-hours below the comfort floor, in the coldest zone."""
    result = run["result"]
    cfg = run["config"]
    if result.upper_temp_trajectory and result.lower_temp_trajectory:
        indoor = np.minimum(
            np.asarray(result.upper_temp_trajectory[1:]),
            np.asarray(result.lower_temp_trajectory[1:]),
        )
    else:
        indoor = np.asarray(result.room_temp_trajectory[1:])
    floor = np.array(
        [cfg.get_temp_bounds((i * DT) % 24)[0] for i in range(len(indoor))]
    )
    return float(np.sum(np.maximum(0.0, floor - indoor)) * DT)


def dhw_shortfall(run: dict) -> float:
    """Worst shortfall below the usable minimum inside a demand window, °C."""
    result = run["result"]
    if not result.dhw_temp_trajectory:
        return 0.0
    windows = parse_windows(run["cfg"].get("dhw_windows", "") or "")
    if not windows:
        return 0.0
    temps = np.asarray(result.dhw_temp_trajectory[1:])
    hours = [(START.hour + i * DT) % 24 for i in range(len(temps))]
    inside = np.array([hour_in_windows(h, windows) for h in hours])
    if not inside.any():
        return 0.0
    return float(max(0.0, run["params"].dhw_min_temp - temps[inside].min()))


# ===========================================================================
# The sweep
# ===========================================================================
R.section("Combination sweep")

combinations = []
for season, two_zone, dhw in itertools.product(
    SEASONS, (False, True), (False, True)
):
    combinations.append(
        dict(season=season, two_zone=two_zone, dhw=dhw, label=f"{season}/{'2z' if two_zone else '1z'}/{'dhw' if dhw else 'space'}")
    )

# Feature combinations, on the seasons where each actually bites.
for season in ("winter", "shoulder"):
    for tariff, pv, cycling in itertools.product(
        (False, True), (False, True), (0.0, 1.0)
    ):
        if not (tariff or pv or cycling):
            continue
        flags = "+".join(
            f for f, on in (("tariff", tariff), ("pv", pv), ("cycle", cycling)) if on
        )
        combinations.append(
            dict(
                season=season, two_zone=True, dhw=True, tariff=tariff, pv=pv,
                cycling=cycling, label=f"{season}/{flags}",
            )
        )

# Building archetypes.
for building, season in itertools.product(BUILDINGS, ("winter", "shoulder")):
    combinations.append(
        dict(season=season, building=building, dhw=True,
             label=f"{building}/{season}")
    )

failures = 0
comfort_failures: list[str] = []
worst_dhw = 0.0
slow = []

for combo in combinations:
    label = combo.pop("label")
    run = build(**combo)
    problems = check_invariants(label, run)
    violation = comfort_violation(run)
    shortfall = dhw_shortfall(run)
    worst_dhw = max(worst_dhw, shortfall)
    if violation > COMFORT_TOLERANCE_DEGREE_HOURS:
        achievable = best_possible_violation(run)
        if violation > achievable + COMFORT_TOLERANCE_DEGREE_HOURS:
            comfort_failures.append(
                f"{label}: {violation:.2f} vs {achievable:.2f} achievable"
            )

    # The comfort floor is a soft constraint, so a small breach is by design.
    # A large one means the penalty is not doing its job -- unless the pump
    # physically cannot hold the house, in which case no plan can, and the
    # honest comparison is against what running flat out would achieve.
    if violation > COMFORT_TOLERANCE_DEGREE_HOURS:
        achievable = best_possible_violation(run)
        if violation > achievable + COMFORT_TOLERANCE_DEGREE_HOURS:
            problems.append(
                f"{violation:.2f} degree-hours below the comfort floor, "
                f"against {achievable:.2f} achievable at full power"
            )
    if shortfall > 2.0:
        problems.append(f"hot water {shortfall:.1f} °C short inside a demand window")
    if run["result"].solve_time_ms > 30000:
        slow.append((label, run["result"].solve_time_ms))

    if problems:
        failures += 1
        print(f"  FAIL {label}")
        for p in problems:
            print(f"         {p}")

R.check(
    f"all {len(combinations)} combinations satisfy the invariants",
    failures == 0,
    f"{failures} failed",
)
R.check(
    "the comfort floor is never breached beyond what physics forces",
    not comfort_failures,
    "; ".join(comfort_failures),
)
R.check(
    "hot water is available when promised",
    worst_dhw <= 2.0,
    f"worst shortfall {worst_dhw:.1f} °C",
)
R.check(
    "every scenario solves in reasonable time",
    not slow,
    "; ".join(f"{n} took {t:.0f}ms" for n, t in slow),
)


# ===========================================================================
# Economics: the claims the integration makes
# ===========================================================================
R.section("Economics")


def thermostat_cost(run: dict) -> float:
    """What a plain setpoint-holding thermostat would spend."""
    power, _ = run["optimizer"]._compute_baseline_power(
        run["initial"], run["outdoor"], run["wind"], run["rain"], run["solar"], DT
    )
    return float(np.sum(run["prices"] * np.asarray(power) * DT))


for season in ("winter", "winter_extreme", "shoulder"):
    run = build(season=season, two_zone=False, dhw=False)
    result = run["result"]
    baseline = thermostat_cost(run)
    R.check(
        f"{season}: cheaper than holding the setpoint",
        result.predicted_cost < baseline,
        f"{result.predicted_cost:.2f} vs {baseline:.2f}",
    )

# With a flat price curve there is nothing to arbitrage, so the optimizer
# should not be *worse* than a thermostat -- but neither should it claim a
# large saving, which would mean it is simply running colder.
flat = build(season="flat", two_zone=False, dhw=False)
R.check(
    "a flat price curve produces no fictitious saving",
    flat["result"].savings_percentage < 35.0,
    f"claimed {flat['result'].savings_percentage:.1f}%",
)
R.check(
    "a flat price curve still respects comfort",
    comfort_violation(flat) <= COMFORT_TOLERANCE_DEGREE_HOURS,
    f"{comfort_violation(flat):.2f} degree-hours",
)

# More price spread must buy more saving. If it does not, the optimizer is not
# actually responding to price.
spread_savings = {}
for season in ("flat", "winter", "winter_extreme"):
    run = build(season=season, two_zone=False, dhw=False)
    prices_arr = np.asarray(run["result"].prices)
    spread = float(prices_arr.max() - prices_arr.min())
    spread_savings[season] = (spread, run["result"].savings_percentage)

R.check(
    "a wider price spread yields a larger saving",
    spread_savings["winter_extreme"][1] > spread_savings["winter"][1]
    > spread_savings["flat"][1],
    ", ".join(
        f"{k}: spread {v[0]:.2f} -> {v[1]:.0f}%" for k, v in spread_savings.items()
    ),
)

# Comfort weight is the money/degrees exchange rate, and the README publishes
# a table of what it buys. That table is the contract, so it is what gets
# checked -- over the documented range, where the signal is far larger than the
# solver noise discussed below.
comfort_curve = []
for weight in (5.0, 10.0, 20.0, 40.0):
    run = build(season="winter", two_zone=False, dhw=False)
    run["config"].comfort_weight = weight
    optimizer = HeatPumpOptimizer(run["model"], run["config"])
    result = optimizer.optimize(
        run["initial"], run["prices"], run["outdoor"], run["wind"],
        run["rain"], run["solar"], START,
    )
    comfort_curve.append(
        (weight, float(np.mean(result.room_temp_trajectory)),
         result.savings_percentage)
    )

temps = [t for _, t, _ in comfort_curve]
savings = [s for _, _, s in comfort_curve]
R.check(
    "a higher comfort weight is warmer, across the documented range",
    all(a < b for a, b in zip(temps, temps[1:])),
    ", ".join(f"w={w:.0f}: {t:.2f}°C" for w, t, _ in comfort_curve),
)
R.check(
    "a higher comfort weight saves less, across the documented range",
    all(a > b for a, b in zip(savings, savings[1:])),
    ", ".join(f"w={w:.0f}: {s:.0f}%" for w, _, s in comfort_curve),
)
# The README's own table, reproduced. If this drifts, either the optimizer
# changed or the documentation is now lying to users.
documented = {5.0: (19.8, 51), 10.0: (20.1, 49), 20.0: (20.4, 47), 40.0: (20.5, 46)}
drift = [
    f"w={w:.0f}: {t:.1f}°C/{s:.0f}% vs documented "
    f"{documented[w][0]}°C/{documented[w][1]}%"
    for w, t, s in comfort_curve
    if abs(t - documented[w][0]) > 0.15 or abs(s - documented[w][1]) > 2
]
R.check("the README's comfort-weight table still holds", not drift, "; ".join(drift))

# Adjacent comfort weights can invert on cost by around a percent. The
# objective is non-convex -- the comfort penalty is one-sided and the price
# signal creates several distinct "charge here, coast there" patterns that are
# each locally optimal -- so two nearby weights can land in different basins.
# Measured rather than assumed: neither a third multi-start solve nor a
# polishing pass closed the gap, and both cost 25-30% more time.
adjacent = []
for weight in (2.0, 5.0):
    run = build(season="winter", two_zone=False, dhw=False)
    run["config"].comfort_weight = weight
    optimizer = HeatPumpOptimizer(run["model"], run["config"])
    result = optimizer.optimize(
        run["initial"], run["prices"], run["outdoor"], run["wind"],
        run["rain"], run["solar"], START,
    )
    adjacent.append(result.predicted_cost)
R.check(
    "solver noise between adjacent comfort weights stays small",
    abs(adjacent[0] - adjacent[1]) / max(adjacent) < 0.02,
    f"{adjacent[0]:.2f} vs {adjacent[1]:.2f}",
)

# The capacity tariff must actually flatten the peak it is priced against.
plain = build(season="winter", two_zone=True, dhw=True)
tariffed = build(season="winter", two_zone=True, dhw=True, tariff=True)
plain_peak = plain["result"].projected_peak_kw
tariff_peak = tariffed["result"].projected_peak_kw
R.check(
    "a capacity tariff lowers the projected peak",
    tariff_peak <= plain_peak + 1e-6,
    f"{plain_peak:.2f} kW -> {tariff_peak:.2f} kW",
)
R.check(
    "and does not wreck comfort doing it",
    comfort_violation(tariffed) <= COMFORT_TOLERANCE_DEGREE_HOURS,
    f"{comfort_violation(tariffed):.2f} degree-hours",
)

# A cycling cost must reduce cycling.
smooth = build(season="winter", two_zone=False, dhw=True, cycling=3.0)
rough = build(season="winter", two_zone=False, dhw=True, cycling=0.0)
R.check(
    "a cycling cost reduces compressor starts",
    smooth["result"].compressor_starts <= rough["result"].compressor_starts,
    f"{rough['result'].compressor_starts} -> {smooth['result'].compressor_starts}",
)

# PV surplus must pull consumption into the surplus hours.
sunny = build(season="shoulder", two_zone=False, dhw=True, pv=True)
R.check(
    "PV surplus is self-consumed",
    sunny["result"].pv_self_consumed_kwh > 0.0,
    f"{sunny['result'].pv_self_consumed_kwh:.2f} kWh",
)

# A better heat pump must cost less to run for the same comfort.
efficient = build(season="winter", two_zone=False, dhw=False, cop_scale=1.4)
standard = build(season="winter", two_zone=False, dhw=False, cop_scale=1.0)
R.check(
    "a more efficient heat pump costs less",
    efficient["result"].predicted_cost < standard["result"].predicted_cost,
    f"{standard['result'].predicted_cost:.2f} -> "
    f"{efficient['result'].predicted_cost:.2f}",
)

# A leakier house must cost more than a tight one, all else equal.
tight = build(season="winter", building="light_new", dhw=False)
leaky = build(season="winter", building="heavy_old", dhw=False)
R.check(
    "a leakier, larger house costs more to heat",
    leaky["result"].predicted_cost > tight["result"].predicted_cost,
    f"{tight['result'].predicted_cost:.2f} vs {leaky['result'].predicted_cost:.2f}",
)


# ===========================================================================
# Edge conditions
# ===========================================================================
R.section("Edge conditions")

edges = {
    "very cold start": dict(
        season="winter", state={"room_temperature": 10.0,
                                "upper_floor_temperature": 10.0,
                                "lower_floor_temperature": 10.0,
                                "slab_temperature": 11.0}),
    "overheated start": dict(
        season="summer", state={"room_temperature": 30.0,
                                "upper_floor_temperature": 30.0,
                                "lower_floor_temperature": 30.0}),
    "empty tank": dict(season="winter", state={"dhw_temperature": 10.0}),
    "boiling tank": dict(season="winter", state={"dhw_temperature": 70.0}),
    "legionella overdue": dict(
        season="winter", state={"dhw_hours_since_legionella": 400.0}),
    "collapsed comfort band": dict(
        season="winter",
        config={"min_temperature": 21.0, "target_temperature": 21.0,
                "max_temperature": 21.0}),
    "enormous band": dict(
        season="winter",
        config={"min_temperature": 5.0, "max_temperature": 35.0}),
    "tiny pump": dict(season="winter", config={"heat_pump_max_power": 0.5}),
    "huge pump": dict(season="winter", config={"heat_pump_max_power": 40.0}),
    "tiny tank": dict(season="winter", config={"dhw_tank_volume": 20.0}),
    "enormous tank": dict(season="winter", config={"dhw_tank_volume": 2000.0}),
    "no demand windows": dict(season="winter", config={"dhw_windows": ""}),
    "all-day window": dict(season="winter", config={"dhw_windows": "00:00-24:00"}),
    "six hour horizon": dict(season="winter", hours=6),
    "48 hour horizon": dict(season="winter", hours=48),
    "negative prices": dict(season="summer_negative"),
    "external heat": dict(
        season="winter", state={"external_heat_active": True,
                                "dhw_temperature": 60.0}),
}

edge_failures = 0
for label, spec in edges.items():
    try:
        run = build(**spec)
    except Exception as err:  # noqa: BLE001 - a crash is the finding
        edge_failures += 1
        print(f"  FAIL {label}: raised {type(err).__name__}: {err}")
        continue
    problems = check_invariants(label, run)
    if problems:
        edge_failures += 1
        print(f"  FAIL {label}")
        for p in problems:
            print(f"         {p}")

R.check(
    f"all {len(edges)} edge conditions produce a sound plan",
    edge_failures == 0,
    f"{edge_failures} failed",
)

# A pump that physically cannot keep up must still produce its best effort
# rather than an infeasible or nonsensical plan.
tiny = build(season="winter", config={"heat_pump_max_power": 0.5}, dhw=False)
R.check(
    "an undersized pump runs flat out rather than giving up",
    float(np.mean(tiny["result"].power_schedule)) > 0.3,
    f"mean {float(np.mean(tiny['result'].power_schedule)):.3f} kW of 0.5 kW",
)

# Negative prices mean being paid to consume; the plan should take some.
negative = build(season="summer_negative", dhw=True)
cheapest = float(np.min(negative["result"].prices))
if cheapest < 0:
    total = np.asarray(negative["result"].power_schedule) + np.asarray(
        negative["result"].dhw_power_schedule or 0.0
    )
    negative_steps = np.asarray(negative["result"].prices) < 0
    R.check(
        "negative prices are exploited rather than ignored",
        float(np.sum(total[negative_steps])) > 0.0,
        "nothing was consumed while being paid to consume",
    )

# External heat must suppress discretionary electric hot water.
with_fire = build(
    season="winter", state={"external_heat_active": True, "dhw_temperature": 60.0}
)
without_fire = build(season="winter", state={"dhw_temperature": 60.0})
R.check(
    "an external heat source suppresses electric hot water",
    float(np.sum(with_fire["result"].dhw_power_schedule))
    <= float(np.sum(without_fire["result"].dhw_power_schedule)) + 1e-6,
    f"{float(np.sum(without_fire['result'].dhw_power_schedule)):.2f} -> "
    f"{float(np.sum(with_fire['result'].dhw_power_schedule)):.2f}",
)


sys.exit(R.close("STRESS CHECKS"))
