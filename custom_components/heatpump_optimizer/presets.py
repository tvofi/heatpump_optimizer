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

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .const import (
    CONF_BUILDING_ERA,
    CONF_BUILDING_FOUNDATION,
    CONF_BUILDING_STRUCTURE,
    CONF_HEATED_AREA,
    CONF_LOWER_EMITTER,
    CONF_UPPER_EMITTER,
    CONF_UPPER_FLOOR_AREA_RATIO,
    DEFAULT_HEATED_AREA,
    DEFAULT_UPPER_FLOOR_AREA_RATIO,
)
from .thermal_model import ThermalParameters

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

# A radiator circuit modelled in the same slot: the thermal model pushes every
# watt of space heat through the "slab" store, so for a radiator house that
# store has to *be* the radiators — a few litres of water and some steel, with
# the good coupling radiators are sized for (0.002 kW/°C·m² is ~50 W/m² at a
# 25 K flow-to-room difference). Giving it the building's slow mass instead,
# behind the 0.05 kW/°C floor transfer, modelled a house where delivering 3 kW
# needs the emitter 60 °C above the room — effectively unheatable.
_EMITTER_RADIATOR_LOOP_MASS_PER_M2 = 0.002  # kWh/°C per m² served
_EMITTER_RADIATOR_TRANSFER_PER_M2 = 0.002  # kW/°C per m² served


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
    slow_per_m2 = mass["slow"]
    if preset.foundation == FOUNDATION_CRAWLSPACE and preset.structure in (
        STRUCTURE_TIMBER_SLAB,
        STRUCTURE_CONCRETE_SLAB,
    ):
        # A slab-bearing structure paired with a crawl-space foundation
        # counted the floor twice: once as the structure table's heavy
        # slow store and once as the foundation's loss path. Subtract the
        # slab exactly once -- the delta between the timber table's own
        # slab-on-grade and crawl-space rows, so it moves with a future
        # table edit -- floored at the crawl-space row, which is what is
        # actually under that house (issue #93). Scoped to slab-bearing
        # structures: "stone or masonry" makes no claim about what is
        # under the floor, so masonry + crawl space is two honest
        # answers with nothing to remove, and the timber crawl-space row
        # is already floorless. Timber-on-slab over a crawl space now
        # derives identically to the crawl-space structure, which the
        # features suite pins as this rule's mutation anchor.
        slow_per_m2 = max(
            slow_per_m2
            - (
                _STRUCTURE_MASS[STRUCTURE_TIMBER_SLAB]["slow"]
                - _STRUCTURE_MASS[STRUCTURE_TIMBER_CRAWLSPACE]["slow"]
            ),
            _STRUCTURE_MASS[STRUCTURE_TIMBER_CRAWLSPACE]["slow"],
        )
    slow_mass = slow_per_m2 * area * adjust["mass"]

    # The model pushes every watt of space heat through the "slab" store, so
    # these two keys describe the *emitter loop* — the slab circuit of the
    # zone it serves, or the radiator circuit where there is no floor heating.
    # In two-zone mode that store feeds the lower zone; in single-zone, the
    # room. The structural slow mass goes to exactly one store, below.
    if preset.two_zone:
        emitter_area = area * (1.0 - preset.upper_area_ratio)
        loop_emitter = preset.lower_emitter
    else:
        emitter_area = area
        loop_emitter = preset.lower_emitter
    if loop_emitter == EMITTER_FLOOR:
        # An actively charged screed on top of the structural slow mass,
        # which lives here: a heated slab *is* the building's heavy floor.
        slab_mass = slow_mass + _EMITTER_SLAB_MASS_PER_M2 * emitter_area
        slab_transfer = max(
            0.05, _EMITTER_SLAB_TRANSFER_PER_M2 * emitter_area
        )
    else:
        slab_mass = max(0.1, _EMITTER_RADIATOR_LOOP_MASS_PER_M2 * emitter_area)
        slab_transfer = max(
            0.05, _EMITTER_RADIATOR_TRANSFER_PER_M2 * emitter_area
        )

    # W/(m²·K) → kW/°C
    loss = _ERA_LOSS_W_PER_M2K[preset.era] * area * adjust["loss"] / 1000.0

    house_mass = fast_mass
    if not preset.two_zone and preset.lower_emitter != EMITTER_FLOOR:
        # With radiators the heavy floor is not the emitter, but it is still
        # inside the envelope and coupled to the room air — it is what lets a
        # radiator house coast at all, so it belongs to the room store.
        house_mass += slow_mass

    result: dict[str, Any] = {
        "house_thermal_mass": round(house_mass, 2),
        "house_heat_loss_coefficient": round(loss, 4),
        "slab_thermal_mass": round(slab_mass, 2),
        "slab_heat_transfer": round(slab_transfer, 3),
    }

    if preset.two_zone:
        upper_ratio = preset.upper_area_ratio
        lower_ratio = 1.0 - upper_ratio
        # The upper floor carries the light mass; the slab mass belongs to
        # whichever store the floor heating actually charges.
        upper_mass = fast_mass * upper_ratio
        lower_mass = fast_mass * lower_ratio
        if preset.upper_emitter == EMITTER_FLOOR:
            upper_mass += _EMITTER_SLAB_MASS_PER_M2 * area * upper_ratio
        if preset.lower_emitter == EMITTER_FLOOR:
            # The slow mass is already in ``slab_thermal_mass`` above — the
            # heated slab is the heavy floor. Counting it in the lower zone
            # as well doubled the downstairs store and let plans coast on
            # heat the building does not have.
            pass
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


def preset_from_config(
    answers: Mapping[str, Any], current: Mapping[str, Any]
) -> BuildingPreset:
    """The questionnaire's preset for ``answers`` on the configuration ``current``.

    ``two_zone`` is the canonical predicate's verdict on the configuration in
    force (R9 D14-s2-01) -- the rule ``ThermalParameters.from_config``
    applies -- never a proxy read of one zone key. An unanswered question
    falls to ``BuildingPreset.validate``'s default.
    """
    return BuildingPreset(
        structure=answers.get(CONF_BUILDING_STRUCTURE) or "",
        era=answers.get(CONF_BUILDING_ERA) or "",
        foundation=answers.get(CONF_BUILDING_FOUNDATION) or "",
        heated_area_m2=float(answers.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA)),
        upper_emitter=answers.get(CONF_UPPER_EMITTER) or "",
        lower_emitter=answers.get(CONF_LOWER_EMITTER) or "",
        upper_area_ratio=float(
            current.get(CONF_UPPER_FLOOR_AREA_RATIO, DEFAULT_UPPER_FLOOR_AREA_RATIO)
        ),
        two_zone=ThermalParameters.from_config(dict(current)).two_zone_enabled,
    ).validate()


#: The house grade's slope in log loss ratio: the owner's ~100-year-old house
#: at 1.5x the typical pre-1960 loss grades 35, inside #2816's asked 30-40.
_GRADE_SLOPE = 1.5
#: 0 is reserved for no data (#2816), so a measured house never rounds onto it.
_GRADE_FLOOR = 1.0


def house_grade(
    params: ThermalParameters, scale: float, config: Mapping[str, Any]
) -> tuple[float, list[dict[str, Any]]]:
    """The house grade (#65, #2816) and the drivers that account for it.

    The loss ratio is the model's envelope loss (W/K) against the loss
    ``derive`` gives the configured type, era, foundation and area,
    corrected for thermal mass: the learner identifies the time constant
    ``mass / loss``, so a loss read off a mass unlike the typical one is
    rescaled by ``typical_mass / mass``. The ratio is therefore
    ``typical_tau / tau``, and its log is the sum of three drivers: the
    configured loss against typical, the learned correction (``scale``),
    and the mass correction. The grade is ``100 / (1 + ratio ** slope)``:
    50 at typical, above for tighter, below for leakier, never 0. Each
    driver's ``points`` is its log share of the distance from 50, so the
    points sum to ``grade - 50``.
    """
    typical = ThermalParameters.from_config(derive(preset_from_config(config, config)))
    logs = {
        "loss_vs_typical": math.log(params.house_heat_loss_base / typical.house_heat_loss_base),
        "learned_heat_loss": math.log(scale),
        "thermal_mass": math.log(
            typical.envelope_thermal_mass / params.envelope_thermal_mass
        ),
    }
    total = sum(logs.values())
    grade = max(100.0 / (1.0 + math.exp(_GRADE_SLOPE * total)), _GRADE_FLOOR)
    drivers = [
        {"code": code, "points": (grade - 50.0) * value / total if total else 0.0}
        for code, value in logs.items()
    ]
    if not config.get(CONF_BUILDING_ERA):
        drivers.append({"code": "era_assumed", "points": 0.0})
    return grade, drivers


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

    This bounds how far the optimizer can usefully shift load and how
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
