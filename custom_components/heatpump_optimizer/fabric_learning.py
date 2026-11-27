"""The fabric learners' folds: interval values in, the new parameter out.

The buffer cooling rate, the hourly internal gains, the house heat-loss scale
and the re-anchor of that scale against an edited nameplate. Every function
here is a function of the values it is handed: it reads no coordinator, no
clock and no store, and it writes nothing it was given. The coordinator asks
the freeze question, keeps the baselines and the sample counters, and applies
and saves what a fold returns.
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

# The buffer tank is learned with the same lower-envelope estimator as the DHW
# tank, but it is a much smaller vessel that is charged frequently, so quiet
# intervals are shorter and rarer. The window is therefore tighter and the
# minimum useful ΔT lower.
BUFFER_COOLING_ALPHA_DOWN = 0.25
BUFFER_COOLING_ALPHA_UP = 0.02
BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.15
BUFFER_COOLING_MAX_SAMPLE_HOURS = 3.0
BUFFER_COOLING_MIN_DELTA = 4.0
BUFFER_AMBIENT_TEMP = 20.0

# House heat loss learning.
#
# The estimator is a one-step model correction: simulate the interval that just
# elapsed with the power that was actually applied, compare the predicted
# indoor temperature to the measured one, and attribute the residual to the
# heat loss coefficient. The sensitivity of the predicted change to UA is
#
#     d(ΔT_room)/dUA = -(T_room - T_out) * Δt / C_room
#
# so a Newton step gives the correction directly. Unlike the tank, the bias
# here is two-sided (unmodelled solar and occupancy gains push it down, an open
# window or a draughty day pushes it up), so a symmetric EWMA is correct and
# the lower-envelope trick from the DHW learner deliberately does *not* apply.
HOUSE_LOSS_ALPHA = 0.02
# The re-anchor threshold gate: a nameplate edit within this fraction keeps
# the learned scale verbatim (``reanchor_learned``). It is no per-interval
# limit: one sample moves the estimate by at most
# ``HOUSE_LOSS_ALPHA * LEARNER_TRUST_REGION`` of it (``learner_newton_step``).
HOUSE_LOSS_MAX_STEP = 0.05
# Symmetric bound on how far one sample's Newton target may sit from the
# *current* estimate before it is clipped, as a fraction of that estimate.
# Centred on the current value, zero-mean noise has zero-mean effect after
# clipping; rejecting or clamping against fixed global bounds does not have
# that property, because the midpoint of a fixed range is not the current
# estimate. A fraction rather than a multiplier offset (#2252), so the bound
# in UA is the same whether the learned value sits in the settings or in
# the multiplier.
LEARNER_TRUST_REGION = 0.5


def house_loss_confidence(samples: int) -> float:
    """The fraction of an EWMA walk from 1.0 the learner has traversed.

    The learner moves ``scale`` toward its target by ``HOUSE_LOSS_ALPHA``
    per sample, so after ``n`` samples the distance still to travel is
    ``(1 - alpha) ** n`` and the traversed fraction is one minus that.
    This is the phi of the re-anchor law: how much of the stored scale
    is measurement rather than starting prior. It is derived from the
    learner's own constant and nothing else, and it lives at module
    level so tests import it rather than re-implement it (issue #91).
    """
    return 1.0 - (1.0 - HOUSE_LOSS_ALPHA) ** max(0, int(samples))


def house_loss_terms(params: ThermalParameters) -> tuple[float, float]:
    """``(base_u, capacity)`` the house heat-loss scale is fitted about.

    Two-zone fits from the upper zone alone, matching the indoor sensor the
    residual is read from. The scale still multiplies both zones -- it owns
    the overall *level* -- while ``lower_floor_loss_ratio`` owns the split
    and is fitted separately from the lower zone. Splitting the jobs this
    way is what keeps the two identifiable: the ratio does not touch the
    upper zone, so this fit is unaffected by it.
    """
    if params.two_zone_enabled:
        return params.upper_floor_heat_loss, params.upper_floor_thermal_mass
    return params.heat_loss_coefficient, params.room_thermal_mass


def learned_zone_temperature(
    state: ThermalState, params: ThermalParameters
) -> float:
    """The zone a heat-loss fold's residual is read on: upper floor, else room."""
    if params.two_zone_enabled:
        return state.upper_floor_temperature
    return state.room_temperature


def zone_capacity(params: ThermalParameters) -> float:
    """The thermal mass the #36 and #53 folds scale a residual by (same zone)."""
    return house_loss_terms(params)[1]


def fold_buffer_cooling(
    rate: float, previous_temp: float, buffer_temp: float, dt_h: float, bounds: tuple[float, float]
) -> tuple[float, float] | None:
    """``(observed, new rate)`` of one quiet decay interval, or ``None`` when a gate refuses it.

    ``rate`` is the standing cooling rate, ``bounds`` its ``(low, high)``
    plausibility range; an observation outside it is refused, not clipped.
    The envelope is one-sided: an observation below the standing rate is
    adopted fast, one above it slowly.
    """
    if dt_h < BUFFER_COOLING_MIN_SAMPLE_HOURS:
        return None
    if dt_h > BUFFER_COOLING_MAX_SAMPLE_HOURS:
        return None
    if buffer_temp > previous_temp:
        return None

    start_delta = previous_temp - BUFFER_AMBIENT_TEMP
    end_delta = buffer_temp - BUFFER_AMBIENT_TEMP
    # The tank did not warm, so the start is at least as far above ambient.
    if end_delta < BUFFER_COOLING_MIN_DELTA:
        return None

    observed = float(
        -np.log(end_delta / start_delta) / dt_h * DHW_COOLING_REFERENCE_DELTA
    )
    if not np.isfinite(observed):
        return None
    low, high = bounds
    if observed < low or observed > high:
        return None

    alpha = (
        BUFFER_COOLING_ALPHA_DOWN
        if observed < rate
        else BUFFER_COOLING_ALPHA_UP
    )
    return observed, (1.0 - alpha) * rate + alpha * observed


def fold_internal_gains(
    profile: list[float] | None,
    params: ThermalParameters,
    previous_time: datetime | None,
    residual: float,
    dt_h: float,
) -> list[float] | None:
    """#53: the hourly gains profile after one dark interval pulls its hour toward the residual.

    Each hour starts at the configured constant and is tethered by the clip
    below and the caller's convergence gate, not by a pull back toward it
    (D2-s3-11). Returns ``profile`` itself where a gate refuses before the
    profile is seeded, and otherwise a new list: the list handed in is never
    written.
    """
    if previous_time is None or dt_h <= 1e-6:
        return profile
    capacity = zone_capacity(params)
    if capacity <= 1e-6:
        return profile
    g0 = float(params.internal_gains)
    folded = [g0] * 24 if profile is None else list(profile)
    hour = int(previous_time.hour) % 24
    y = residual * capacity / dt_h
    if not np.isfinite(y):
        return folded
    # D2-s3-11: no pull toward g0. A ridge's fixed point is
    # alpha/(alpha+ridge) of the true gain; the step's expectation is zero
    # only at a zero residual. The clip and the convergence gate tether it.
    g = folded[hour] + INTERNAL_GAINS_ALPHA * y
    folded[hour] = float(
        np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05))
    )
    return folded


def fold_house_heat_loss(
    scale: float, params: ThermalParameters, residual: float, delta_t: float, dt_h: float
) -> tuple[float, float] | None:
    """``(target scale, new scale)`` of one accepted residual, or ``None``.

    The Newton step is taken about the fitted zone's terms at the current
    effective coefficient, i.e. what actually produced the prediction.
    """
    base_u, capacity = house_loss_terms(params)
    return learner_newton_step(
        scale,
        base_u, capacity, residual, delta_t, dt_h,
        trust_region=LEARNER_TRUST_REGION,
        alpha=HOUSE_LOSS_ALPHA,
    )


def house_heat_loss_anchor(params: ThermalParameters, ratio: float) -> float:
    """The total base UA the learned scale currently multiplies.

    In two-zone mode the scale owns the *level* of both zones -- the
    ratio owns the split -- so the quantity it multiplies is the zone
    total with the learned ratio applied, not the upper zone the fit
    reads (taking the upper zone went sign-negative on single-zone edits).
    """
    if params.two_zone_enabled:
        return float(
            params.upper_floor_heat_loss
            + params.lower_floor_heat_loss * ratio
        )
    return float(params.heat_loss_coefficient)


def heat_loss_anchors(params: ThermalParameters, config: Any, earned: bool, ratio: float) -> dict[str, Any]:
    """The stored anchor keys as the configuration in force writes them."""
    return {
        "house_heat_loss_anchor": round(house_heat_loss_anchor(params, ratio), 6),
        "lower_floor_loss_anchor": params.lower_floor_heat_loss
        if params.two_zone_enabled else None,
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

    ``then`` is the stored ``(total, lower floor)`` nameplate pair, the total
    already re-expressed at a voided ratio by the caller; ``live`` is
    ``heat_loss_anchors`` of the configuration in force. ``None`` is also a
    store with no anchor to re-express, which the caller adopts on its next
    save. A basis that voids the evidence zeroes both sample counts, and a
    value the law cannot express against the new nameplate is reset with its
    count.
    """
    scale, scale_samples, ratio, ratio_samples = learned
    void = heat_loss_basis_voids(stored_basis, live["house_heat_loss_basis"])
    pair = heat_loss_anchor_pair(
        then,
        (live["house_heat_loss_anchor"], live["lower_floor_loss_anchor"]),
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
        scale, new_scale, ratio, new_ratio,
        then[0], live["house_heat_loss_anchor"], *phi, void,
    )
    return HeatLossLearned(new_scale, scale_samples, new_ratio, ratio_samples)
