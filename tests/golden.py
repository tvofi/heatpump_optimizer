"""Characterization harness: pin current optimizer behaviour as golden fixtures.

    PYTHONPATH=tests/hastub python tests/golden.py            # check
    PYTHONPATH=tests/hastub python tests/golden.py --record   # re-record

The rest of the suite asserts on *outcomes* — savings percentages, comfort
bounds, solver status. That catches a change that makes the optimizer obviously
worse. It does not catch one that quietly shifts a plan by one interval, drops a
constraint in a rare branch, or changes a learned parameter's convergence. Those
are exactly the failures a refactor produces, and they are invisible to every
other test here.

So this records the *entire* output of a broad scenario matrix — every power
schedule, setpoint, trajectory, cost, reason code and diagnostic figure — and
diffs against it byte for byte. A refactor that changes any of it is either a
bug or a deliberate change that has to be justified and re-recorded on purpose.

The optimizer is deterministic (verified: two runs of the same scenario are
bitwise identical), which is what makes this possible at all.

**When a diff appears, read it before re-recording.** The whole value of this
file is that `--record` is an explicit decision rather than a reflex.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

import numpy as np

from profiles import DT, house, prices, weather
from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
from heatpump_optimizer.presets import BuildingPreset, derive
from heatpump_optimizer.thermal_model import (
    ThermalModel,
    ThermalParameters,
    ThermalState,
)

GOLDEN_DIR = Path("tests/golden")
START = datetime(2026, 1, 15, 0, 0)

# Values are rounded before storage and compared exactly against that rounding.
# Six decimals is far finer than any behavioural change worth making — a
# one-interval shift or a dropped constraint moves things by whole kilowatts —
# while tolerating last-bit floating point noise that carries no meaning.
PRECISION = 6


def _walk_finite(node, path, problems) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            _walk_finite(v, f"{path}.{k}", problems)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            _walk_finite(v, f"{path}[{i}]", problems)
    elif isinstance(node, float) and not math.isfinite(node):
        problems.append(f"{path}: non-finite value {node!r}")


def _walk_nan(node, path, problems) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            _walk_nan(v, f"{path}.{k}", problems)
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            _walk_nan(v, f"{path}[{i}]", problems)
    elif isinstance(node, float) and math.isnan(node):
        problems.append(f"{path}: NaN")


def assert_invariants(name: str, payload: dict, params) -> None:
    """Hard physical facts every captured plan must satisfy.

    The exact comparison pins behaviour; this layer pins *possibility*.
    Without it, ``--record`` would happily bake a NaN, a negative power or
    a diverged trajectory into a fixture, and from then on the suite would
    defend the bug. Runs on both record and check, in every mode.
    """
    problems: list[str] = []
    _walk_finite(payload, name, problems)

    n = len(payload.get("prices") or [])
    p_max = float(params.max_electrical_power)
    space = payload.get("power_schedule") or []
    dhw = payload.get("dhw_power_schedule") or []
    for label, series in (("power_schedule", space), ("dhw_power_schedule", dhw)):
        if series and len(series) != n:
            problems.append(f"{label}: {len(series)} values for {n} steps")
        for i, v in enumerate(series):
            if v < -1e-9:
                problems.append(f"{label}[{i}]: negative power {v}")
                break
    if space:
        combined = (
            [a + b for a, b in zip(space, dhw)] if len(dhw) == len(space) else space
        )
        worst = max(combined)
        if worst > p_max + 1e-6:
            problems.append(
                f"electrical draw peaks at {worst:.3f} kW, above the "
                f"{p_max:.3f} kW compressor maximum"
            )

    for key in (
        "room_temp_trajectory",
        "slab_temp_trajectory",
        "buffer_temp_trajectory",
        "wood_temp_trajectory",
        "upper_temp_trajectory",
        "lower_temp_trajectory",
        "dhw_temp_trajectory",
    ):
        series = payload.get(key) or []
        if series and len(series) != n + 1:
            problems.append(f"{key}: {len(series)} values for {n}-step horizon")
        for i, v in enumerate(series):
            if not -40.0 <= v <= 120.0:
                problems.append(f"{key}[{i}]: {v} °C is outside -40..120 °C")
                break

    savings = payload.get("savings_percentage")
    if isinstance(savings, (int, float)) and savings > 100.0 + 1e-6:
        problems.append(f"savings_percentage {savings} claims more than 100%")

    if problems:
        for line in problems[:10]:
            print(f"  INVARIANT {line}", file=sys.stderr)
        raise SystemExit(
            f"golden scenario {name!r} violates {len(problems)} physical "
            "invariant(s); refusing to record or compare it"
        )


def r(value):
    """Round anything array-like to the stored precision, as plain Python."""
    if value is None:
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return round(float(value), PRECISION)
    if isinstance(value, (list, tuple, np.ndarray)):
        return [r(v) for v in value]
    if isinstance(value, dict):
        return {k: r(v) for k, v in value.items()}
    return value


# ---------------------------------------------------------------------------
# Scenario construction
# ---------------------------------------------------------------------------


def make(
    *,
    two_zone=False,
    dhw=True,
    price_profile="winter_typical",
    weather_profile="winter_cold",
    hours=24,
    state_overrides=None,
    config_overrides=None,
    opt_overrides=None,
    param_overrides=None,
):
    """Build one fully specified scenario."""
    cfg = house(two_zone=two_zone, dhw=dhw)
    cfg.update(config_overrides or {})

    params = ThermalParameters.from_config(cfg)
    params.dhw_enabled = dhw
    for key, value in (param_overrides or {}).items():
        setattr(params, key, value)

    opt_cfg = OptimizationConfig(
        horizon_hours=hours,
        time_step_minutes=15,
        target_temp=cfg["target_temperature"],
        min_temp=cfg["min_temperature"],
        max_temp=cfg["max_temperature"],
    )
    for key, value in (opt_overrides or {}).items():
        setattr(opt_cfg, key, value)

    price_series = prices(price_profile, START)
    outdoor, wind, rain, solar = weather(weather_profile, START)

    # A horizon longer than the profiles cover is tiled, which is what the
    # coordinator effectively does when the weather forecast runs out.
    need = int(hours / DT)
    def fit(arr):
        arr = np.asarray(arr, dtype=float)
        if len(arr) >= need:
            return arr[:need]
        reps = int(np.ceil(need / len(arr)))
        return np.tile(arr, reps)[:need]

    state = ThermalState(
        room_temperature=21.0,
        slab_temperature=22.0,
        outdoor_temperature=float(outdoor[0]),
        upper_floor_temperature=21.0,
        lower_floor_temperature=21.0,
        dhw_temperature=50.0,
        dhw_hours_since_legionella=20.0,
        buffer_tank_temperature=40.0,
    )
    for key, value in (state_overrides or {}).items():
        setattr(state, key, value)

    return {
        "optimizer": HeatPumpOptimizer(ThermalModel(params), opt_cfg),
        "state": state,
        "prices": fit(price_series),
        "outdoor": fit(outdoor),
        "wind": fit(wind),
        "rain": fit(rain),
        "solar": fit(solar),
    }


def known_mask(n, known_steps):
    mask = np.zeros(n, dtype=bool)
    mask[: min(known_steps, n)] = True
    return mask


# ---------------------------------------------------------------------------
# The scenario matrix
# ---------------------------------------------------------------------------
#
# Chosen to reach every branch a refactor could plausibly damage, not to be
# representative. Each entry names what it is there to protect.

SCENARIOS: dict[str, dict] = {
    # --- the core paths ---------------------------------------------------
    "winter_single_dhw": dict(),
    "winter_two_zone_dhw": dict(two_zone=True),
    "winter_single_no_dhw": dict(dhw=False),
    "winter_two_zone_no_dhw": dict(two_zone=True, dhw=False),
    # --- seasons ----------------------------------------------------------
    "summer_dhw_only": dict(
        price_profile="summer_typical", weather_profile="summer_warm"
    ),
    "shoulder": dict(price_profile="shoulder", weather_profile="shoulder"),
    "shoulder_two_zone": dict(
        two_zone=True, price_profile="shoulder", weather_profile="shoulder"
    ),
    # --- price shapes -----------------------------------------------------
    "extreme_prices": dict(price_profile="winter_extreme"),
    "negative_prices": dict(
        price_profile="summer_negative", weather_profile="summer_warm"
    ),
    "flat_prices": dict(price_profile="flat"),
    # --- weather ----------------------------------------------------------
    "mild_windy_rain": dict(weather_profile="winter_mild"),
    "cool_rainy_summer": dict(
        price_profile="summer_typical", weather_profile="summer_cool"
    ),
    # --- DHW branches -----------------------------------------------------
    "legionella_due": dict(
        state_overrides={"dhw_hours_since_legionella": 170.0},
    ),
    "dhw_schedule_off": dict(
        config_overrides={"dhw_schedule_enabled": False},
    ),
    "dhw_learned_windows": dict(
        config_overrides={"dhw_windows": ""},
    ),
    "dhw_cold_tank": dict(state_overrides={"dhw_temperature": 30.0}),
    "dhw_large_tank": dict(config_overrides={"dhw_tank_volume": 1500.0}),
    # --- comfort band edges ------------------------------------------------
    "start_below_band": dict(
        state_overrides={
            "room_temperature": 15.0,
            "upper_floor_temperature": 15.0,
            "lower_floor_temperature": 15.0,
            "slab_temperature": 16.0,
        }
    ),
    "start_above_band": dict(
        state_overrides={
            "room_temperature": 25.0,
            "upper_floor_temperature": 25.0,
            "lower_floor_temperature": 25.0,
        }
    ),
    "narrow_band": dict(
        config_overrides={"min_temperature": 20.9, "target_temperature": 21.0},
    ),
    "wide_band": dict(
        config_overrides={"min_temperature": 12.0, "max_temperature": 28.0},
    ),
    # --- horizons ----------------------------------------------------------
    "horizon_48h": dict(hours=48),
    "horizon_6h": dict(hours=6),
    # --- v2.8.0 features ---------------------------------------------------
    "capacity_tariff": dict(
        opt_overrides={
            "peak_price_per_kw": 20.0,
            # Near what this house actually draws, which is where a real peak
            # tracker puts it. A threshold far below the house's demand asks
            # the plan to avoid an unavoidable peak, which is not a case any
            # user has and tells us nothing useful.
            "peak_threshold_kw": 6.5,
            "peak_window_minutes": 60,
            "baseline_load_kw": 1.5,
        }
    ),
    "capacity_tariff_15min": dict(
        opt_overrides={
            "peak_price_per_kw": 20.0,
            "peak_threshold_kw": 6.0,
            "peak_window_minutes": 15,
            "baseline_load_kw": 1.0,
        }
    ),
    "cycling_cost": dict(opt_overrides={"cycling_cost": 1.5}),
    "external_heat_active": dict(
        state_overrides={"external_heat_active": True, "dhw_temperature": 58.0},
    ),
    "cop_scale_learned": dict(param_overrides={"cop_scale": 1.3}),
    "away_setback": dict(
        config_overrides={
            "min_temperature": 16.0,
            "target_temperature": 16.0,
            "comfort_temp_day": 16.0,
            "comfort_temp_night": 16.0,
        },
        opt_overrides={
            "min_temp": 16.0,
            "comfort_temp_day": 16.0,
            "comfort_temp_night": 16.0,
        },
    ),
    "building_preset": dict(
        config_overrides=derive(BuildingPreset(heated_area_m2=180)),
    ),
    # --- the buffer tank as a store (items 27/29) -------------------------
    #
    # Not one scenario in this matrix exercised a mixing valve before these,
    # across four releases of work on the feature: the discharge law, the
    # weather-curve cap, the hard power constraint and the store threshold all
    # landed without a single recorded scenario able to see them. Every fixture
    # here pins a valve on.
    "valve_storage": dict(
        two_zone=True,
        dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual",
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    ),
    # The valve pinned at the comfort target rather than left at its ceiling
    # default. This is the setting that works the tank hardest, so a storage
    # regression shows here first.
    "valve_storage_low_target": dict(
        two_zone=True,
        dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual",
            "mixing_valve_target": 21.0,
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    ),
    # Flat prices are the null control: with nothing to arbitrage the store
    # should barely move. A fixture that cycles as hard here as on a peaky day
    # is a bug no cost assertion would catch.
    "valve_storage_flat_prices": dict(
        two_zone=True,
        dhw=False,
        price_profile="flat",
        config_overrides={
            "mixing_valve_mode": "manual",
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    ),
    # Below `BUFFER_STORE_MIN_VOLUME`, so the planner stops treating the tank as
    # a store while the physics stay modelled -- the branch where the discharge
    # bound is the only thing keeping the trajectory physical.
    "valve_storage_small_tank": dict(
        two_zone=True,
        dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual",
            "buffer_tank_volume": 35.0,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    ),
    # A commanded valve, which is the only mode that can hold its charge for
    # the peak. Pinned because the hold schedule is a *derived* candidate:
    # a change to the derivation, the adoption rule or the per-step target in
    # the model all show up here as a moved schedule, and nowhere else.
    "valve_storage_smart_write": dict(
        two_zone=True,
        dhw=False,
        config_overrides={
            "mixing_valve_mode": "smart_write",
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    ),
    # --- the two-tank topology (issue #40) ---------------------------------
    #
    # A hot wood tank beside the heat-pump tank, the 4-way valve drawing
    # wood-while-usable, and an active burn charging the wood side. The burn
    # must land in the WOOD tank: the HP's modelled COP and its cap headroom
    # stay its own, which is the entire fix these fixtures pin.
    "wood_two_tank": dict(
        two_zone=True,
        dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual",
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_volume": 500.0,
        },
        state_overrides={
            "buffer_tank_temperature": 32.0,
            "wood_tank_temperature": 55.0,
        },
    ),
    # The commanded valve on the same plumbing: hold-schedule derivation and
    # the two-tank draw law interact nowhere else.
    "wood_two_tank_smart_write": dict(
        two_zone=True,
        dhw=False,
        config_overrides={
            "mixing_valve_mode": "smart_write",
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_volume": 500.0,
        },
        state_overrides={
            "buffer_tank_temperature": 32.0,
            "wood_tank_temperature": 55.0,
        },
    ),
    # The DHW refill coil (v3.15.1): hot water joins the two-tank plumbing,
    # so refill water is preheated by the wood side and the electric DHW
    # demand falls exactly by what the coil pulls from that tank.
    "wood_coil": dict(
        two_zone=True,
        config_overrides={
            "mixing_valve_mode": "manual",
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "wood_tank_top_entity": "sensor.wood_top",
            "wood_tank_volume": 500.0,
            "dhw_wood_coil_enabled": True,
        },
        state_overrides={
            "buffer_tank_temperature": 32.0,
            "wood_tank_temperature": 55.0,
        },
    ),
    # The stored-layout override (v3.16.0): the slab drinks raw tank water,
    # so a hot tank drains into the floor with no curve cap — the layout
    # the pre-v3.14.1 drawing showed, now honestly modelled.
    "valve_upper_direct_slab": dict(
        two_zone=True,
        dhw=False,
        config_overrides={
            "mixing_valve_mode": "manual",
            "buffer_tank_volume": 750.0,
            "buffer_max_temperature": 70.0,
            "topology_layout": "valve_upper_direct_slab",
        },
        state_overrides={"buffer_tank_temperature": 32.0},
    ),
    # --- combinations, because features interact --------------------------
    "tariff_plus_two_zone": dict(
        two_zone=True,
        opt_overrides={
            "peak_price_per_kw": 25.0,
            "peak_threshold_kw": 7.0,
            "baseline_load_kw": 2.0,
        },
    ),
    "everything_on": dict(
        two_zone=True,
        opt_overrides={
            "peak_price_per_kw": 15.0,
            "peak_threshold_kw": 7.0,
            "baseline_load_kw": 1.2,
            "cycling_cost": 0.5,
        },
        param_overrides={"cop_scale": 1.15},
        state_overrides={"dhw_hours_since_legionella": 160.0},
    ),
    # --- v4.0.0 T1: the bill beyond spot -----------------------------------
    # The #13 masks ON: a Nov-Mar weekday-daytime tariff with half-rate
    # off-peak hours, on a January Thursday. Pins the per-window factor
    # composition through the whole solve.
    "peak_masked": dict(
        opt_overrides={
            "peak_price_per_kw": 20.0,
            "peak_threshold_kw": 6.5,
            "peak_window_minutes": 60,
            "baseline_load_kw": 1.5,
            "peak_months": frozenset({11, 12, 1, 2, 3}),
            "peak_hours": ((7.0, 19.0),),
            "peak_weekdays_only": True,
            "peak_offpeak_factor": 0.5,
        }
    ),
    # #34 ON: a risk premium on the prior-guessed 45% of the horizon. The
    # sigma vector is synthetic (the capture harness has no learned prior)
    # but rides the exact production path through the objective.
    "price_risk": dict(opt_overrides={"price_risk_lambda": 1.0}),
    # --- v4.0.0 T2: peak & power --------------------------------------------
    # #3/#7 ON: an external total-power cap at 60% of nameplate on the DHW
    # winter day. Pins every piece of the cap composition through one solve:
    # the DHW block's bounded run power, space headroom under a DHW block,
    # and the ``power_cap_breach_c`` report.
    "fuse_guard": dict(),
    # --- T4b (#17 #30) ----------------------------------------------------
    # The learned capacity envelope arrives through the same caps_extra
    # channel as the fuse guard, but VARYING per step — the fuse fixture
    # only ever exercised a constant cap, so a per-step regression in the
    # cap handling was invisible until this one.
    "capacity_curve": dict(),
    # The rain multiplier weighted by liquid fraction (#30): the first
    # half of the wet, mild day falls as snow (fraction 0), the second as
    # rain (fraction 1). The pre-weighted array is exactly what the
    # coordinator hands the optimizer with the flag on.
    "precip_snow": dict(weather_profile="winter_mild"),
    # --- T5 (#16 #54) -------------------------------------------------------
    # Both comfort-floor adjustments riding one solve: a lead-shaped margin
    # ramp on the min bounds and a flat mold floor, the shapes the
    # coordinator actually produces with the flags on.
    "confidence_margins": dict(),
}

# Scenarios where prices past a point are the learned prior rather than
# published, exercising the provenance mask through the whole result.
PARTIAL_PRICE_SCENARIOS = {"winter_single_dhw", "horizon_48h", "price_risk"}

# Scenarios given a synthetic per-step sigma on the guessed steps (#34).
RISK_SCENARIOS = {"price_risk"}

# Scenarios solved under an external total-power cap (T2, items 3/7). The
# cap is derived from the scenario's own nameplate so the fixture cannot
# silently go slack if the harness house ever changes size.
CAP_SCENARIOS = {"fuse_guard"}

# T4b #17: a per-step VARYING electrical cap, shaped like a cold snap
# tightening the learned envelope toward its 0.6 × nameplate floor.
ENVELOPE_CAP_SCENARIOS = {"capacity_curve"}

# T4b #30: precipitation pre-weighted by liquid fraction, the transform
# the coordinator applies with precip_type_enabled on.
SNOW_SCENARIOS = {"precip_snow"}

# T5: per-step comfort-floor adjustments (#16 margins, #54 mold floor).
MARGIN_SCENARIOS = {"confidence_margins"}

# Scenarios given a PV surplus profile, which changes the marginal price.
PV_SCENARIOS = {"shoulder", "summer_dhw_only"}

# Scenarios with an active wood burn: the shape forecast_free_heat produces,
# a rate fading linearly over the detector's two-hour horizon.
EXTERNAL_HEAT_SCENARIOS = {
    "wood_two_tank", "wood_two_tank_smart_write", "wood_coil",
}


def external_heat_for(n):
    steps = min(n, int(2.0 / DT))
    arr = np.zeros(n)
    for i in range(steps):
        arr[i] = 8.0 * (1.0 - i / max(steps, 1))
    return arr


def pv_surplus_for(n, solar):
    """A plausible surplus profile derived from the scenario's own irradiance."""
    production = np.clip(np.asarray(solar, dtype=float) / 1000.0 * 8.0 * 0.8, 0, 8.0)
    return np.clip(production - 1.0, 0.0, None)[:n]


# ---------------------------------------------------------------------------
# Recording
# ---------------------------------------------------------------------------


def capture(name: str, spec: dict) -> dict:
    """Run one scenario and record everything the optimizer produced."""
    built = make(**spec)
    opt = built["optimizer"]
    n = len(built["prices"])

    price_known = None
    if name in PARTIAL_PRICE_SCENARIOS:
        price_known = known_mask(n, int(n * 0.55))
    price_sigma = None
    if name in RISK_SCENARIOS and price_known is not None:
        price_sigma = np.where(price_known, 0.0, 0.5)
    surplus = None
    if name in PV_SCENARIOS:
        surplus = pv_surplus_for(n, built["solar"])
    ext = None
    if name in EXTERNAL_HEAT_SCENARIOS:
        ext = external_heat_for(n)
    caps = None
    if name in CAP_SCENARIOS:
        caps = np.full(n, opt.model.params.max_electrical_power * 0.6)
    if name in ENVELOPE_CAP_SCENARIOS:
        p_max = opt.model.params.max_electrical_power
        caps = np.clip(
            p_max * np.linspace(1.0, 0.6, n), 0.6 * p_max, p_max
        )
    if name in SNOW_SCENARIOS:
        liquid = np.where(np.arange(n) < n // 2, 0.0, 1.0)
        built["rain"] = np.asarray(built["rain"], dtype=float) * liquid
    margins = None
    floors = None
    if name in MARGIN_SCENARIOS:
        # #16's real shape: expected error grows with lead, capped at 0.8.
        margins = np.minimum(0.1 + np.arange(n) * (0.7 / max(n - 1, 1)), 0.8)
        # #54's: a modest flat floor between the config's min and target.
        floors = np.full(n, 18.5)

    result = opt.optimize(
        built["state"],
        built["prices"],
        built["outdoor"],
        built["wind"],
        built["rain"],
        built["solar"],
        START,
        price_known,
        surplus,
        external_heat_kw=ext,
        price_sigma=price_sigma,
        power_caps_extra=caps,
        min_temp_margins=margins,
        min_temp_floors=floors,
    )

    # Everything that describes the plan. Trajectories included: a constraint
    # dropped in a rare branch shows up there before it shows up in the cost.
    payload = {
        "power_schedule": r(result.power_schedule),
        "dhw_power_schedule": r(result.dhw_power_schedule),
        "optimal_setpoints": r(result.optimal_setpoints),
        "upper_setpoints": r(result.upper_setpoints),
        "lower_setpoints": r(result.lower_setpoints),
        "displace_schedule": r(result.displace_schedule),
        "heat_pump_on_schedule": r(result.heat_pump_on_schedule),
        "room_temp_trajectory": r(result.room_temp_trajectory),
        "slab_temp_trajectory": r(result.slab_temp_trajectory),
        "buffer_temp_trajectory": r(result.buffer_temp_trajectory),
        "wood_temp_trajectory": r(result.wood_temp_trajectory),
        "valve_target_schedule": r(result.valve_target_schedule),
        "upper_temp_trajectory": r(result.upper_temp_trajectory),
        "lower_temp_trajectory": r(result.lower_temp_trajectory),
        "dhw_temp_trajectory": r(result.dhw_temp_trajectory),
        "solar_gain_trajectory": r(result.solar_gain_trajectory),
        "prices": r(result.prices),
        "outdoor_temps": r(result.outdoor_temps),
        "predicted_cost": r(result.predicted_cost),
        "baseline_cost": r(result.baseline_cost),
        "predicted_savings": r(result.predicted_savings),
        "savings_percentage": r(result.savings_percentage),
        "deferred_energy_cost": r(result.deferred_energy_cost),
        "dhw_heating_cost": r(result.dhw_heating_cost),
        "status": result.status,
        "space_reasons": result.space_reasons,
        "dhw_reasons": result.dhw_reasons,
        "price_known": r(result.price_known),
        "projected_peak_kw": r(result.projected_peak_kw),
        "peak_cost": r(result.peak_cost),
        "compressor_starts": r(result.compressor_starts),
        "pv_surplus": r(result.pv_surplus),
        "pv_self_consumed_kwh": r(result.pv_self_consumed_kwh),
        # ``solve_time_ms`` is deliberately excluded: it is the one field that
        # legitimately varies run to run, and including it would make every
        # diff noise.
        "predictive_info": r(
            {
                k: v
                for k, v in (result.predictive_info or {}).items()
                if k != "solve_time_ms"
            }
        ),
    }
    assert_invariants(name, payload, opt.model.params)
    return payload


# ---------------------------------------------------------------------------
# Coordinator-level captures
# ---------------------------------------------------------------------------
#
# The optimizer captures above protect the plan. They say nothing about the
# layer that assembles the optimizer's inputs and publishes its outputs — which
# is where the config plumbing, the learners and the entity payloads live, and
# which is just as easy to break silently. So the forecast assembly and the
# published data dictionary get pinned too.


def coordinator_scenarios() -> dict[str, dict]:
    """Configurations exercising the coordinator's own branches."""
    base = {
        "tibber_token": "x",
        "weather_entity": "weather.home",
        "target_temperature": 21.0,
        "min_temperature": 17.0,
        "max_temperature": 23.0,
    }
    return {
        "coord_minimal": base,
        "coord_dhw": {
            **base,
            "dhw_tank_volume": 200.0,
            "dhw_setpoint": 55.0,
            "dhw_min_temperature": 45.0,
            "dhw_windows": "06:00-08:30, 17:00-22:00",
        },
        "coord_two_zone": {
            **base,
            "upper_floor_thermal_mass": 3.0,
            "lower_floor_thermal_mass": 8.0,
            "upper_floor_heat_loss": 0.08,
            "lower_floor_heat_loss": 0.07,
        },
        "coord_grid_fee": {
            **base,
            "grid_fee_mode": "rules",
            "grid_fee_rules": "Mon-Fri 06:00-22:00 = 0.25",
            "grid_fee_fixed": 0.05,
            "contract_fixed_price": 1.2,
        },
        "coord_all_features": {
            **base,
            "dhw_tank_volume": 200.0,
            "peak_tariff_enabled": True,
            "peak_tariff_price_per_kw": 45.0,
            "pv_enabled": True,
            "pv_peak_kw": 8.0,
            "pv_export_price": 0.3,
            "away_enabled": True,
            "external_heat_detection_enabled": True,
            "comfort_learning_enabled": True,
            "system_identification_enabled": True,
            "compressor_cycling_cost": 0.5,
        },
    }


def capture_coordinator(config: dict) -> dict:
    """Everything the coordinator assembles and publishes, for one config.

    The clock is frozen for the duration: the coordinator publishes
    time-derived values such as "hours until the next hot water window", so
    without this every replay would differ from the recording by however long
    the two runs were apart, and the fixture would be pure noise.
    """
    from harness import FakeEntry, FakeHass
    from homeassistant.util import dt as dt_util
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    dt_util.freeze(START)
    try:
        payload = _capture_coordinator(config)
    finally:
        dt_util.freeze(None)
    # Coordinator payloads mix strings, nulls and numbers, so the only
    # invariant cheap enough to hold everywhere is "no NaN". Infinity is
    # deliberately allowed: `peak_threshold_kw` publishes +inf as "no
    # capacity tariff configured", and the committed fixtures carry it.
    problems: list[str] = []
    _walk_nan(payload, "coordinator", problems)
    if problems:
        for line in problems[:10]:
            print(f"  INVARIANT {line}", file=sys.stderr)
        raise SystemExit(
            f"coordinator capture violates {len(problems)} invariant(s)"
        )
    return payload


def _capture_coordinator(config: dict) -> dict:
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    hass = FakeHass()
    entry = FakeEntry(data=config)
    coord = HeatPumpOptimizerCoordinator(hass, entry)

    # Deterministic inputs: real Tibber-shaped prices for a fixed day, so the
    # published dict does not depend on when the test runs.
    coord._prices = [
        {
            "total": round(0.6 + 0.5 * (h % 12) / 12.0, 4),
            "starts_at": (START + timedelta(hours=h)).isoformat(),
            "level": "NORMAL",
        }
        for h in range(48)
    ]
    coord._weather_forecast = [
        {
            "datetime": (START + timedelta(hours=h)).isoformat(),
            "temperature": -5.0 + 3.0 * (h % 24) / 24.0,
            "wind_speed": 3.0,
            "precipitation": 0.0,
            "humidity": 85.0,
        }
        for h in range(48)
    ]
    coord._solar_radiation_forecast = [
        max(0.0, 200.0 * (1 - abs(12 - (h % 24)) / 12.0)) for h in range(48)
    ]

    arrays = coord._forecast_arrays()
    data = coord._build_data_dict()

    # ``last_optimization``/``next_optimization`` are wall-clock and would make
    # every diff noise; the rest of the dictionary is a pure function of state.
    volatile = {"last_optimization", "next_optimization", "solve_time_ms"}
    return {
        "forecast_prices": r(arrays[0]),
        "forecast_outdoor": r(arrays[1]),
        "forecast_wind": r(arrays[2]),
        "forecast_rain": r(arrays[3]),
        "forecast_solar": r(arrays[4]),
        "forecast_price_known": r(arrays[5]),
        "forecast_pv_surplus": r(arrays[6]),
        "data": r({k: v for k, v in data.items() if k not in volatile}),
    }


def capture_config_flow() -> dict:
    """Every option page's schema, field by field.

    The config flow has no runtime behaviour to pin — it is a declaration —
    but that makes it *more* worth fingerprinting, not less: a selector whose
    bounds or default silently change produces a form that still works and
    quietly means something different.
    """
    import asyncio

    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.config_flow import (
        HeatPumpOptimizerConfigFlow as InitialFlow,
        HeatPumpOptimizerOptionsFlow as Flow,
    )

    flow = Flow(
        FakeEntry(data={"tibber_token": "x", "weather_entity": "weather.home"})
    )
    flow.hass = FakeHass()

    def fingerprint(schema) -> dict:
        fields = {}
        for key, value in (schema.schema.items() if schema else []):
            config = getattr(value, "config", None)
            try:
                default = repr(key.default())
            except Exception:
                default = None
            fields[str(key)] = {
                "selector": type(value).__name__,
                "config": (
                    {k: repr(v) for k, v in sorted(dict(config).items())}
                    if config
                    else None
                ),
                "default": default,
                "required": type(key).__name__,
            }
        return fields

    pages = {}
    for step in Flow._MENU_LABELS:
        result = asyncio.run(getattr(flow, f"async_step_{step}")())
        pages[step] = fingerprint(result.get("data_schema"))

    # The initial flow (v4.1.0): fingerprinted since its restructure, because
    # a first-run form that silently gains or loses a field is exactly the
    # kind of change this fixture exists to make deliberate. Menu steps are
    # recorded as their ordered option list.
    initial = InitialFlow()
    initial.hass = FakeHass()
    initial_pages = {}
    for step in (
        "user",
        "temperature",
        "building",
        "building_describe",
        "building_extras",
        "thermal",
        "zones",
        "dhw",
        "weather_sensitivity",
    ):
        result = asyncio.run(getattr(initial, f"async_step_{step}")())
        if result.get("type") == "menu":
            initial_pages[step] = {
                "menu": [[k, v] for k, v in result["menu_options"].items()]
            }
        else:
            initial_pages[step] = fingerprint(result.get("data_schema"))
    pages["_initial"] = initial_pages

    # The two-level menu (v4.0.0) is structure the schemas cannot see: which
    # page sits on which menu, and in what order. Recorded as ordered pairs,
    # because ``sort_keys`` would alphabetise a dict and silently drop the
    # order users actually see.
    menus = {}
    for step in ("init", "advanced"):
        result = asyncio.run(getattr(flow, f"async_step_{step}")())
        menus[step] = [[k, v] for k, v in result["menu_options"].items()]
    pages["_menu"] = menus
    return pages


def record_all(only: str | None = None) -> None:
    """Record fixtures; ``only`` filters by substring, exactly like checking.

    The filter is honoured here for a reason with a scar attached: five
    fixtures are machine-sensitive (scipy finds a different local optimum
    per environment) and must NEVER be re-recorded casually. A --record
    that silently ignored --only rewrote all of them in one keystroke.
    """
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    recorded = 0
    for name, spec in SCENARIOS.items():
        if only and only not in name:
            continue
        payload = capture(name, spec)
        path = GOLDEN_DIR / f"{name}.json"
        path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        print(f"  recorded {name} ({path.stat().st_size // 1024} KB)")
        recorded += 1
    for name, config in coordinator_scenarios().items():
        if only and only not in name:
            continue
        payload = capture_coordinator(config)
        path = GOLDEN_DIR / f"{name}.json"
        path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        print(f"  recorded {name} ({path.stat().st_size // 1024} KB)")
        recorded += 1
    if not only or only in "config_flow":
        path = GOLDEN_DIR / "config_flow.json"
        path.write_text(
            json.dumps(capture_config_flow(), indent=1, sort_keys=True) + "\n"
        )
        print(f"  recorded config_flow ({path.stat().st_size // 1024} KB)")
        recorded += 1
    print(f"\nRecorded {recorded} golden fixture(s) in {GOLDEN_DIR}/")


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------


def describe_diff(name: str, key: str, expected, actual) -> str:
    """A diff a human can act on, not a wall of numbers."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        # Recurse to the leaf that actually changed. Printing two whole
        # dictionaries names nothing and buries the one field that moved.
        sub = []
        for k in sorted(set(expected) | set(actual)):
            if k not in expected:
                sub.append(f"{key}.{k}: new")
            elif k not in actual:
                sub.append(f"{key}.{k}: removed")
            elif expected[k] != actual[k]:
                sub.append(describe_diff(name, f"{key}.{k}", expected[k], actual[k]))
        if not sub:
            return f"{key}: differs but no leaf found"
        head = "; ".join(sub[:3])
        return head + (f"; (+{len(sub) - 3} more)" if len(sub) > 3 else "")
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return f"{key}: length {len(expected)} -> {len(actual)}"
        bad = [
            i
            for i, (e, a) in enumerate(zip(expected, actual))
            if e != a
        ]
        first = bad[0]
        e, a = expected[first], actual[first]
        # A refactor bug very often shifts a series by one step; say so
        # explicitly, because it is otherwise easy to misread as noise.
        shifted = (
            len(expected) > 2
            and expected[:-1] == actual[1:]
            or expected[1:] == actual[:-1]
        )
        hint = "  (looks like a one-step shift)" if shifted else ""
        return (
            f"{key}: {len(bad)}/{len(expected)} values differ, "
            f"first at index {first}: {e} -> {a}{hint}"
        )
    return f"{key}: {expected!r} -> {actual!r}"


def check_all(only: str | None = None) -> int:
    if not GOLDEN_DIR.exists():
        print(
            f"No fixtures in {GOLDEN_DIR}/. Run with --record first.",
            file=sys.stderr,
        )
        return 1

    failures = 0
    checked = 0
    missing = []

    cases = [(name, ("plan", spec)) for name, spec in SCENARIOS.items()]
    cases += [
        (name, ("coordinator", config))
        for name, config in coordinator_scenarios().items()
    ]
    cases.append(("config_flow", ("config_flow", None)))

    for name, (kind, spec) in cases:
        if only and only not in name:
            continue
        path = GOLDEN_DIR / f"{name}.json"
        if not path.exists():
            missing.append(name)
            continue

        expected = json.loads(path.read_text())
        if kind == "plan":
            actual = capture(name, spec)
        elif kind == "coordinator":
            actual = capture_coordinator(spec)
        else:
            actual = capture_config_flow()
        checked += 1

        diffs = []
        for key in sorted(set(expected) | set(actual)):
            if key not in expected:
                diffs.append(f"{key}: new field")
            elif key not in actual:
                diffs.append(f"{key}: field removed")
            elif expected[key] != actual[key]:
                diffs.append(describe_diff(name, key, expected[key], actual[key]))

        if diffs:
            failures += 1
            print(f"  DIFF {name}")
            for d in diffs[:6]:
                print(f"         {d}")
            if len(diffs) > 6:
                print(f"         ... and {len(diffs) - 6} more fields")
        else:
            print(f"  ok   {name}")

    if missing:
        print(f"\n{len(missing)} scenario(s) have no fixture: {', '.join(missing)}")
        print("Run with --record to add them.")
        failures += len(missing)

    print()
    if failures:
        print(f"{failures} of {checked} GOLDEN SCENARIOS CHANGED")
        print(
            "\nRead the diffs before re-recording. A change here is either a bug\n"
            "or a deliberate behaviour change that should be justified in the\n"
            "commit message; `--record` is meant to be a decision, not a reflex."
        )
        return 1
    print(f"ALL {checked} GOLDEN SCENARIOS UNCHANGED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--record",
        action="store_true",
        help="re-record the fixtures from current behaviour",
    )
    parser.add_argument(
        "--only", help="only run scenarios whose name contains this substring"
    )
    args = parser.parse_args()

    print("=== Golden characterization ===\n")
    if args.record:
        record_all(args.only)
        return 0
    return check_all(args.only)


if __name__ == "__main__":
    sys.exit(main())
