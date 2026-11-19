"""D7.M3 enumerator (round 11, D7-s2): every learner with persisted state, one per line.

The universe is read from production: every key of a real coordinator's
``HeatPumpOptimizerCoordinator._learner_snapshot_payloads()`` is mapped to the learner that
writes it (KEY_TO_LEARNER); a key the map does not know fails the run, so a new learner
cannot drop out of the denominator silently. Bookkeeping keys map to ``None``.

Run: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D7/s2/enum_m3.py
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: 21 lines.
"""
from __future__ import annotations

import sys

KEY_TO_LEARNER = {
    "thermal_learning.house_heat_loss_scale": "house_heat_loss",
    "thermal_learning.house_heat_loss_samples": "house_heat_loss",
    "thermal_learning.house_heat_loss_anchor": "house_heat_loss",
    "thermal_learning.house_heat_loss_basis": "house_heat_loss",
    "thermal_learning.heat_loss_zone_entities": "house_heat_loss",
    "thermal_learning.lower_floor_loss_ratio": "lower_floor_loss",
    "thermal_learning.lower_floor_loss_samples": "lower_floor_loss",
    "thermal_learning.lower_floor_loss_anchor": "lower_floor_loss",
    "thermal_learning.buffer_cooling_rate": "buffer_cooling",
    "thermal_learning.buffer_cooling_samples": "buffer_cooling",
    "thermal_learning.cop_scale": "measured_cop",
    "thermal_learning.cop_samples": "measured_cop",
    "thermal_learning.measured_cop": "measured_cop",
    "thermal_learning.cop_baseline_measured": "cop_health",
    "thermal_learning.cop_health_cusum_measured": "cop_health",
    "thermal_learning.capacity_envelope": "capacity_envelope",
    "thermal_learning.curve_learner": "curve",
    "thermal_learning.flow_bias": "flow_bias",
    "thermal_learning.freq_map": "freq_map",
    "thermal_learning.freq_fallback": "freq_map",
    "thermal_learning.internal_gains_profile": "internal_gains",
    "thermal_learning.solar_aperture": "solar_aperture",
    "thermal_learning.vent_cusum": "vent_detector",
    "thermal_learning.immersion_events": "immersion_log",
    "thermal_learning.snow_accum_cm": "snow",
    "thermal_learning.snow_accum_last": "snow",
    "thermal_learning.last_heavy_snow": "snow",
    "thermal_learning.updated_at": None,
    "dhw_profile.hourly_profile": "dhw_profile",
    "dhw_profile.profile_weekday": "dhw_profile",
    "dhw_profile.profile_weekday_samples": "dhw_profile",
    "dhw_profile.profile_weekend": "dhw_profile",
    "dhw_profile.profile_weekend_samples": "dhw_profile",
    "dhw_profile.cooling_rate": "dhw_cooling",
    "dhw_profile.cooling_samples": "dhw_cooling",
    "dhw_draws.open_date": "dhw_draws",
    "dhw_draws.open_kwh": "dhw_draws",
    "dhw_draws.open_label": "dhw_draws",
    "dhw_draws.reservoirs": "dhw_draws",
    "price_model.days": "price_model",
    "price_model.quarter_days": "price_model",
    "price_model.quarter_factors": "price_model",
    "price_model.residual_var": "price_model",
    "price_model.shapes": "price_model",
    "accuracy.lead_counts": "accuracy",
    "accuracy.lead_pending": "accuracy",
    "accuracy.lead_sigma": "accuracy",
    "accuracy.promises": "accuracy",
    "accuracy.samples": "accuracy",
    "accuracy.draw": "accuracy",
    "comfort.configured_weight": "comfort",
    "comfort.evidence": "comfort",
    "comfort.history": "comfort",
    "comfort.last_update": "comfort",
    "comfort.learned_weight": "comfort",
    "comfort.overrides": "comfort",
    "defrost.counts": "defrost",
    "defrost.duty": "defrost",
    "defrost.duty_counts": "defrost",
    "defrost.duty_events": "defrost",
    "defrost.factors": "defrost",
    "defrost.version": None,
}


def learner_of(key: str) -> str | None:
    if key not in KEY_TO_LEARNER:
        raise KeyError(f"unmapped persisted learner key {key!r}: extend KEY_TO_LEARNER")
    return KEY_TO_LEARNER[key]


def keys_from_production() -> list[str]:
    sys.path[:0] = ["tests"]
    from harness import FakeEntry, FakeHass
    from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator

    c = HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data={
        "tibber_token": "x", "weather_entity": "weather.home",
        "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor"}))
    return [f"{s}.{k}" for s, body in c._learner_snapshot_payloads().items() for k in body]


if __name__ == "__main__":
    learners = sorted({learner_of(k) for k in keys_from_production()} - {None})
    print("\n".join(learners))
