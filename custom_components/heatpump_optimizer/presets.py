"""Building archetype presets: ask what the user knows, derive the physics.

The thermal step of the config flow asked for ``house_thermal_mass`` in kWh/°C
and ``slab_thermal_mass`` as raw numbers. No homeowner knows either value.
Worse, the shipped defaults quietly encoded one specific house — a two-zone
building with a concrete slab downstairs and radiators upstairs — so every
other house started from a wrong prior, and the learners then spent weeks
walking away from it, rate-limited by guard thresholds that exist precisely
because the prior might be bad.

This module replaces two unanswerable questions with three answerable ones:
what the building is made of, roughly when it was built, and what the heat is
emitted through. Those map onto physics that is well characterised, especially
for Swedish era bands, which track the insulation standards of their time
fairly closely.

**Presets set starting values only.** The learners remain authoritative and
converge to the real house. That has to be explicit in the UI too, or users
will read a preset as a claim about their building.

**Everything is scaled by heated area**, which users reliably know, rather than
shipped as absolute numbers per archetype.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

_LOGGER = logging.getLogger(__name__)

# --- Structure -------------------------------------------------------------
#
# Thermal mass is what is *inside* the insulation envelope and thermally
# coupled to the room air, per m² of heated floor area, in kWh/°C.
STRUCTURE_TIMBER_CRAWLSPACE = "timber_crawlspace"
STRUCTURE_TIMBER_SLAB = "timber_slab"
STRUCTURE_CONCRETE_SLAB = "concrete_slab"
STRUCTURE_MASONRY = "masonry"

STRUCTURES: tuple[str, ...] = (
    STRUCTURE_TIMBER_CRAWLSPACE,
    STRUCTURE_TIMBER_SLAB,
    STRUCTURE_CONCRETE_SLAB,
    STRUCTURE_MASONRY,
)

# kWh/°C per m² of heated area, split into the fast (air + furnishings + light
# fabric) and slow (slab / heavy masonry) stores.
_STRUCTURE_MASS = {
    # Regelstomme with krypgrund or torpargrund: very little heavy mass inside
    # the envelope, and the floor is a loss path rather than a store.
    STRUCTURE_TIMBER_CRAWLSPACE: {"fast": 0.020, "slow": 0.010},
    # Platta på mark: light walls, heavy floor.
    STRUCTURE_TIMBER_SLAB: {"fast": 0.020, "slow": 0.055},
    STRUCTURE_CONCRETE_SLAB: {"fast": 0.035, "slow": 0.065},
    # Older stone or masonry: very heavy, and usually leakier with it.
    STRUCTURE_MASONRY: {"fast": 0.055, "slow": 0.070},
}

# Extra loss area and mass from a heated basement.
FOUNDATION_NONE = "none"
FOUNDATION_CRAWLSPACE = "crawlspace"
FOUNDATION_BASEMENT = "heated_basement"
FOUNDATIONS: tuple[str, ...] = (
    FOUNDATION_NONE,
    FOUNDATION_CRAWLSPACE,
    FOUNDATION_BASEMENT,
)
_FOUNDATION_ADJUST = {
    FOUNDATION_NONE: {"mass": 1.0, "loss": 1.0},
    FOUNDATION_CRAWLSPACE: {"mass": 0.9, "loss": 1.12},
    # A heated basement adds both mass and loss area.
    FOUNDATION_BASEMENT: {"mass": 1.25, "loss": 1.18},
}

# --- Era -------------------------------------------------------------------
#
# Specific heat loss in W/(m²·K) of heated floor area, which is the figure
# Swedish energy declarations are effectively built from.
ERA_PRE_1960 = "pre_1960"
ERA_1960_1980 = "1960_1980"
ERA_1980_2005 = "1980_2005"
ERA_POST_2005 = "post_2005"
ERA_LOW_ENERGY = "low_energy"

ERAS: tuple[str, ...] = (
    ERA_PRE_1960,
    ERA_1960_1980,
    ERA_1980_2005,
    ERA_POST_2005,
    ERA_LOW_ENERGY,
)

_ERA_LOSS_W_PER_M2K = {
    ERA_PRE_1960: 1.55,
    ERA_1960_1980: 1.15,
    ERA_1980_2005: 0.80,
    ERA_POST_2005: 0.55,
    ERA_LOW_ENERGY: 0.35,
}

# --- Emitters --------------------------------------------------------------
EMITTER_FLOOR = "floor"
EMITTER_RADIATORS = "radiators"
EMITTERS: tuple[str, ...] = (EMITTER_FLOOR, EMITTER_RADIATORS)

# A heated screed or slab is a large thermal store that is *actively charged*,
# so floor heating raises effective thermal mass well beyond the same house
# with radiators. Kept separate from the structural mass above because the two
# are physically distinct: one is what the building is, the other is what the
# heating system couples into.
_EMITTER_SLAB_MASS_PER_M2 = 0.045  # kWh/°C per m² of floor-heated area
# Response time in hours, which bounds how far ahead load can usefully shift.
_EMITTER_RESPONSE_HOURS = {EMITTER_FLOOR: 4.0, EMITTER_RADIATORS: 0.3}
# Slab-to-room transfer, kW/°C per m² of floor-heated area.
_EMITTER_SLAB_TRANSFER_PER_M2 = 0.010


@dataclass
class BuildingPreset:
    """User-answerable description of a building."""

    structure: str = STRUCTURE_TIMBER_SLAB
    era: str = ERA_1980_2005
    foundation: str = FOUNDATION_NONE
    heated_area_m2: float = 140.0
    upper_emitter: str = EMITTER_RADIATORS
    lower_emitter: str = EMITTER_FLOOR
    #: Fraction of the heated area on the upper floor. Only meaningful in
    #: two-zone mode; a single-storey house leaves this at 0.
    upper_area_ratio: float = 0.5
    two_zone: bool = False

    def validate(self) -> "BuildingPreset":
        """Clamp to known values so a bad option cannot produce nonsense."""
        if self.structure not in STRUCTURES:
            self.structure = STRUCTURE_TIMBER_SLAB
        if self.era not in _ERA_LOSS_W_PER_M2K:
            self.era = ERA_1980_2005
        if self.foundation not in _FOUNDATION_ADJUST:
            self.foundation = FOUNDATION_NONE
        if self.upper_emitter not in EMITTERS:
            self.upper_emitter = EMITTER_RADIATORS
        if self.lower_emitter not in EMITTERS:
            self.lower_emitter = EMITTER_FLOOR
        self.heated_area_m2 = max(20.0, min(1000.0, float(self.heated_area_m2)))
        self.upper_area_ratio = max(0.0, min(1.0, float(self.upper_area_ratio)))
        return self


def _floor_heated_area(preset: BuildingPreset) -> float:
    """Heated area served by a floor-heating circuit, m²."""
    if not preset.two_zone:
        return (
            preset.heated_area_m2
            if preset.lower_emitter == EMITTER_FLOOR
            else 0.0
        )
    upper = preset.heated_area_m2 * preset.upper_area_ratio
    lower = preset.heated_area_m2 - upper
    area = 0.0
    if preset.upper_emitter == EMITTER_FLOOR:
        area += upper
    if preset.lower_emitter == EMITTER_FLOOR:
        area += lower
    return area


def derive(preset: BuildingPreset) -> dict[str, Any]:
    """Turn a preset into starting values for the thermal parameters.

    Returns a dict of configuration keys, so the caller can merge it into the
    config entry without this module needing to know about Home Assistant.
    """
    preset = preset.validate()
    area = preset.heated_area_m2
    mass = _STRUCTURE_MASS[preset.structure]
    adjust = _FOUNDATION_ADJUST[preset.foundation]

    fast_mass = mass["fast"] * area * adjust["mass"]
    slow_mass = mass["slow"] * area * adjust["mass"]

    # Floor heating adds an actively charged store on top of the structural
    # slab mass, proportional to the area actually served by it.
    slab_mass = slow_mass + _EMITTER_SLAB_MASS_PER_M2 * _floor_heated_area(preset)
    slab_transfer = max(
        0.05, _EMITTER_SLAB_TRANSFER_PER_M2 * max(_floor_heated_area(preset), 1.0)
    )

    # W/(m²·K) → kW/°C
    loss = _ERA_LOSS_W_PER_M2K[preset.era] * area * adjust["loss"] / 1000.0

    result: dict[str, Any] = {
        "house_thermal_mass": round(fast_mass, 2),
        "house_heat_loss_coefficient": round(loss, 4),
        "slab_thermal_mass": round(slab_mass, 2),
        "slab_heat_transfer": round(slab_transfer, 3),
    }

    if preset.two_zone:
        upper_ratio = preset.upper_area_ratio
        lower_ratio = 1.0 - upper_ratio
        # The upper floor carries the light mass; the slab mass belongs to
        # whichever zone the floor heating actually serves.
        upper_mass = fast_mass * upper_ratio
        lower_mass = fast_mass * lower_ratio
        if preset.upper_emitter == EMITTER_FLOOR:
            upper_mass += _EMITTER_SLAB_MASS_PER_M2 * area * upper_ratio
        if preset.lower_emitter == EMITTER_FLOOR:
            lower_mass += slow_mass * adjust["mass"]
        else:
            upper_mass += slow_mass * 0.5
            lower_mass += slow_mass * 0.5

        result.update(
            {
                "upper_floor_thermal_mass": round(max(0.5, upper_mass), 2),
                "lower_floor_thermal_mass": round(max(0.5, lower_mass), 2),
                "upper_floor_heat_loss": round(loss * upper_ratio, 4),
                "lower_floor_heat_loss": round(loss * lower_ratio, 4),
                "upper_floor_area_ratio": round(upper_ratio, 2),
                # Power split follows the emitters: a radiator zone takes its
                # heat directly, a floor zone takes it through the slab.
                "radiator_power_fraction": round(
                    _radiator_fraction(preset), 2
                ),
            }
        )

    result["heating_response_hours"] = round(response_hours(preset), 2)
    return result


def _radiator_fraction(preset: BuildingPreset) -> float:
    """Share of pump output that goes to radiators rather than the slab."""
    if not preset.two_zone:
        return 0.0 if preset.lower_emitter == EMITTER_FLOOR else 1.0
    upper_ratio = preset.upper_area_ratio
    fraction = 0.0
    if preset.upper_emitter == EMITTER_RADIATORS:
        fraction += upper_ratio
    if preset.lower_emitter == EMITTER_RADIATORS:
        fraction += 1.0 - upper_ratio
    return max(0.0, min(1.0, fraction))


def response_hours(preset: BuildingPreset) -> float:
    """How long the heating system takes to move the room temperature.

    This bounds how far ahead the optimizer can usefully shift load and how
    quickly it can recover from a setback. A slow emitter makes pre-heating
    both more valuable and more necessary, which is why it is derived and
    published rather than left implicit in the thermal masses.
    """
    preset = preset.validate()
    if not preset.two_zone:
        return _EMITTER_RESPONSE_HOURS[preset.lower_emitter]
    upper = _EMITTER_RESPONSE_HOURS[preset.upper_emitter]
    lower = _EMITTER_RESPONSE_HOURS[preset.lower_emitter]
    ratio = preset.upper_area_ratio
    return upper * ratio + lower * (1.0 - ratio)


def describe(preset: BuildingPreset) -> dict[str, Any]:
    """Preset plus derived values, for display and for the sensor attributes."""
    preset = preset.validate()
    derived = derive(preset)
    return {
        "structure": preset.structure,
        "era": preset.era,
        "foundation": preset.foundation,
        "heated_area_m2": preset.heated_area_m2,
        "upper_emitter": preset.upper_emitter,
        "lower_emitter": preset.lower_emitter,
        "derived": derived,
        # Stated explicitly so nobody reads the numbers above as a measurement
        # of their building.
        "note": (
            "Starting values only. The self-learning model refines these from "
            "how the house actually behaves."
        ),
    }
