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
            "peak_threshold_kw": 3.0,
            "peak_window_minutes": 60,
            "baseline_load_kw": 1.5,
        }
    ),
    "capacity_tariff_15min": dict(
        opt_overrides={
            "peak_price_per_kw": 20.0,
            "peak_threshold_kw": 2.0,
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
    # --- combinations, because features interact --------------------------
    "tariff_plus_two_zone": dict(
        two_zone=True,
        opt_overrides={
            "peak_price_per_kw": 25.0,
            "peak_threshold_kw": 4.0,
            "baseline_load_kw": 2.0,
        },
    ),
    "everything_on": dict(
        two_zone=True,
        opt_overrides={
            "peak_price_per_kw": 15.0,
            "peak_threshold_kw": 4.0,
            "baseline_load_kw": 1.2,
            "cycling_cost": 0.5,
        },
        param_overrides={"cop_scale": 1.15},
        state_overrides={"dhw_hours_since_legionella": 160.0},
    ),
}

# Scenarios where prices past a point are the learned prior rather than
# published, exercising the provenance mask through the whole result.
PARTIAL_PRICE_SCENARIOS = {"winter_single_dhw", "horizon_48h"}

# Scenarios given a PV surplus profile, which changes the marginal price.
PV_SCENARIOS = {"shoulder", "summer_dhw_only"}


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
    surplus = None
    if name in PV_SCENARIOS:
        surplus = pv_surplus_for(n, built["solar"])

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
    )

    # Everything that describes the plan. Trajectories included: a constraint
    # dropped in a rare branch shows up there before it shows up in the cost.
    return {
        "power_schedule": r(result.power_schedule),
        "dhw_power_schedule": r(result.dhw_power_schedule),
        "optimal_setpoints": r(result.optimal_setpoints),
        "upper_setpoints": r(result.upper_setpoints),
        "lower_setpoints": r(result.lower_setpoints),
        "displace_schedule": r(result.displace_schedule),
        "heat_pump_on_schedule": r(result.heat_pump_on_schedule),
        "room_temp_trajectory": r(result.room_temp_trajectory),
        "slab_temp_trajectory": r(result.slab_temp_trajectory),
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


def record_all() -> None:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    for name, spec in SCENARIOS.items():
        payload = capture(name, spec)
        path = GOLDEN_DIR / f"{name}.json"
        path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        print(f"  recorded {name} ({path.stat().st_size // 1024} KB)")
    print(f"\nRecorded {len(SCENARIOS)} golden fixtures in {GOLDEN_DIR}/")


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------


def describe_diff(name: str, key: str, expected, actual) -> str:
    """A diff a human can act on, not a wall of numbers."""
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

    for name, spec in SCENARIOS.items():
        if only and only not in name:
            continue
        path = GOLDEN_DIR / f"{name}.json"
        if not path.exists():
            missing.append(name)
            continue

        expected = json.loads(path.read_text())
        actual = capture(name, spec)
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
        record_all()
        return 0
    return check_all(args.only)


if __name__ == "__main__":
    sys.exit(main())
