"""The fabric learners' folds: interval values in, the new parameter out.

SPIKE for design/R11-ARCH-fabric-learner, never merged: it exists so arm.py can read the
architecture score of the cut. The fixer writes the module from the note, after R11-SEAM-learners.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime
from typing import Any, NamedTuple

import numpy as np

from .const import (
    DHW_COOLING_REFERENCE_DELTA,
    HOUSE_HEAT_LOSS_SCALE_MAX,
    HOUSE_HEAT_LOSS_SCALE_MIN,
    INTERNAL_GAINS_ALPHA,
    INTERNAL_GAINS_MAX_FACTOR,
    INTERNAL_GAINS_RIDGE,
    LOWER_FLOOR_LOSS_RATIO_MAX,
    LOWER_FLOOR_LOSS_RATIO_MIN,
)
from .thermal_model import (
    ThermalParameters,
    ThermalState,
    heat_loss_anchor_pair,
    heat_loss_basis,
    heat_loss_basis_voids,
    heat_loss_zone_entities,
    learner_newton_step,
    reanchor_heat_loss,
)

_LOGGER = logging.getLogger(__name__)

BUFFER_COOLING_ALPHA_DOWN = 0.25
BUFFER_COOLING_ALPHA_UP = 0.02
BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.15
BUFFER_COOLING_MAX_SAMPLE_HOURS = 3.0
BUFFER_COOLING_MIN_DELTA = 4.0
BUFFER_AMBIENT_TEMP = 20.0
HOUSE_LOSS_ALPHA = 0.02
HOUSE_LOSS_MAX_STEP = 0.05
LEARNER_TRUST_REGION = 0.5


def house_loss_confidence(samples: int) -> float:
    return 1.0 - (1.0 - HOUSE_LOSS_ALPHA) ** max(0, int(samples))


def house_loss_terms(params: ThermalParameters) -> tuple[float, float]:
    if params.two_zone_enabled:
        return params.upper_floor_heat_loss, params.upper_floor_thermal_mass
    return params.heat_loss_coefficient, params.room_thermal_mass


def learned_zone_temperature(state: ThermalState, params: ThermalParameters) -> float:
    if params.two_zone_enabled:
        return state.upper_floor_temperature
    return state.room_temperature


def zone_capacity(params: ThermalParameters) -> float:
    return house_loss_terms(params)[1]


def fold_buffer_cooling(
    rate: float, previous_temp: float, buffer_temp: float, dt_h: float, bounds: tuple[float, float]
) -> tuple[float, float] | None:
    """``(observed, new rate)`` of one quiet decay interval, or ``None`` when a gate refuses it."""
    if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:
        return None
    if dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS:
        return None
    if buffer_temp > previous_temp:
        return None
    start_delta = previous_temp - BUFFER_AMBIENT_TEMP
    end_delta = buffer_temp - BUFFER_AMBIENT_TEMP
    if start_delta < BUFFER_COOLING_MIN_DELTA:
        return None
    if end_delta < BUFFER_COOLING_MIN_DELTA:
        return None
    observed = float(-np.log(end_delta / start_delta) / dt_h * DHW_COOLING_REFERENCE_DELTA)
    if not np.isfinite(observed):
        return None
    low, high = bounds
    if observed < low or observed > high:
        return None
    alpha = BUFFER_COOLING_ALPHA_DOWN if observed < rate else BUFFER_COOLING_ALPHA_UP
    return observed, (1.0 - alpha) * rate + alpha * observed


def fold_internal_gains(
    profile: list[float] | None, params: ThermalParameters, previous_time: datetime | None,
    residual: float, dt_h: float,
) -> list[float] | None:
    """The hourly gains profile after one dark interval; the profile handed in when a gate refuses."""
    if previous_time is None or dt_h <= 1e-6:
        return profile
    capacity = zone_capacity(params)
    if capacity <= 1e-6:
        return profile
    g0 = float(params.internal_gains)
    out = [g0] * 24 if profile is None else list(profile)
    hour = int(previous_time.hour) % 24
    y = residual * capacity / dt_h
    if not np.isfinite(y):
        return out
    g = out[hour]
    g += INTERNAL_GAINS_ALPHA * y - INTERNAL_GAINS_RIDGE * (g - g0)
    out[hour] = float(np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05)))
    return out


def fold_house_heat_loss(
    scale: float, params: ThermalParameters, residual: float, delta_t: float, dt_h: float
) -> tuple[float, float] | None:
    """``(target scale, new scale)`` of one accepted residual: the Newton step about the fitted zone."""
    base_u, capacity = house_loss_terms(params)
    return learner_newton_step(
        scale, base_u, capacity, residual, delta_t, dt_h,
        trust_region=LEARNER_TRUST_REGION, alpha=HOUSE_LOSS_ALPHA,
    )


def house_heat_loss_anchor(params: ThermalParameters, ratio: float) -> float:
    """The total base UA the learned scale multiplies, the learned ratio applied in two-zone mode."""
    if params.two_zone_enabled:
        return float(params.upper_floor_heat_loss + params.lower_floor_heat_loss * ratio)
    return float(params.heat_loss_coefficient)


def heat_loss_anchors(params: ThermalParameters, config: Any, earned: bool, ratio: float) -> dict[str, Any]:
    """The stored anchor keys as the configuration in force writes them."""
    return {
        "house_heat_loss_anchor": round(house_heat_loss_anchor(params, ratio), 6),
        "lower_floor_loss_anchor": params.lower_floor_heat_loss if params.two_zone_enabled else None,
        "house_heat_loss_basis": heat_loss_basis(config, earned),
        "heat_loss_zone_entities": heat_loss_zone_entities(config),
    }


class HeatLossLearned(NamedTuple):
    """The two heat-loss learners' values and evidence, as the store carries them."""

    scale: float
    scale_samples: int
    ratio: float
    ratio_samples: int


def reanchor_learned(
    learned: HeatLossLearned, then: tuple[float, float], stored_basis: Any, live: Mapping[str, Any]
) -> HeatLossLearned | None:
    """``learned`` re-expressed against the UA now configured; ``None`` below the gate.

    ``then`` is the stored ``(total, lower floor)`` nameplate pair, the total already re-expressed
    at a voided ratio by the caller.
    """
    scale, scale_samples, ratio, ratio_samples = learned
    void = heat_loss_basis_voids(stored_basis, live["house_heat_loss_basis"])
    pair = heat_loss_anchor_pair(
        then, (live["house_heat_loss_anchor"], live["lower_floor_loss_anchor"]),
        ratio, void=void, step=HOUSE_LOSS_MAX_STEP,
    )
    if pair is None:
        return None
    if void:
        scale_samples = ratio_samples = 0
    phi = (house_loss_confidence(scale_samples), house_loss_confidence(ratio_samples))
    new_scale, new_ratio, scale_reset, ratio_reset = reanchor_heat_loss(
        *pair, scale, ratio, phi,
        scale_bounds=(HOUSE_HEAT_LOSS_SCALE_MIN, HOUSE_HEAT_LOSS_SCALE_MAX),
        ratio_bounds=(LOWER_FLOOR_LOSS_RATIO_MIN, LOWER_FLOOR_LOSS_RATIO_MAX),
    )
    if ratio_reset:
        _LOGGER.warning(
            "Learned lower floor loss ratio %.3f (%d samples) cannot be expressed against "
            "the newly configured lower floor loss: resetting to the configuration",
            ratio, ratio_samples,
        )
        ratio_samples, phi = 0, (phi[0], 0.0)
    if scale_reset:
        _LOGGER.warning(
            "Learned house heat loss scale %.3f (fitted against %.4f kW/°C, %d samples) cannot be "
            "expressed against the newly configured %.4f kW/°C: resetting to the configuration",
            scale, then[0], scale_samples, live["house_heat_loss_anchor"],
        )
        scale_samples, phi = 0, (0.0, phi[1])
    _LOGGER.info(
        "Re-anchored learned house heat loss scale %.3f -> %.3f and ratio %.3f -> %.3f "
        "against the configured UA %.4f -> %.4f kW/°C (confidence %.2f, %.2f; "
        "evidence voided by a later basis: %s)",
        scale, new_scale, ratio, new_ratio, then[0], live["house_heat_loss_anchor"], *phi, void,
    )
    return HeatLossLearned(new_scale, scale_samples, new_ratio, ratio_samples)
