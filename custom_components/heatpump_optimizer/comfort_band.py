"""The comfort band's cross-field rules, in one place.

A comfort band is four numbers that only mean anything together: a minimum, a
target, a maximum and a day/night pair. No single selector can catch a minimum
above the target or a night temperature above the day one, and the optimizer
will not catch them either — the bounds are priced, not fenced, so a
contradictory band produces a plan that simply sits in permanent violation.
That is close to undiagnosable from the outside, which is why the config flow
has always refused to store one.

The config flow was the only path that checked. Two others write the same
fields and skipped it entirely:

* the ``apply_schedule`` service writes ``comfort_temp_day`` straight into the
  entry options behind a range check alone;
* the climate entity's temperature slider writes ``target_temperature`` through
  the coordinator, with the slider's own maximum sitting one degree *above* the
  configured ceiling.

So the rules live here, and all three call the same function. ``errors`` keeps
the config flow's shape — field to error key, landing on the field a user would
naturally correct — and ``violations`` carries the same findings as sentences,
for the service and entity paths that raise rather than re-render a form.

Deliberately free of Home Assistant imports so it stays unit-testable and can
be imported from anywhere in the integration without dragging the config flow
(and its selectors and HTTP session) into a runtime path.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import (
    COMFORT_TEMP_NIGHT_SELECTOR_MAX,
    CONF_COMFORT_TEMP_DAY,
    CONF_COMFORT_TEMP_NIGHT,
    CONF_DAY_END_HOUR,
    CONF_DAY_START_HOUR,
    CONF_MAX_TEMP,
    CONF_MIN_TEMP,
    CONF_TARGET_TEMP,
    DEFAULT_COMFORT_TEMP_DAY,
    DEFAULT_COMFORT_TEMP_NIGHT,
    DEFAULT_DAY_END_HOUR,
    DEFAULT_DAY_START_HOUR,
    DEFAULT_MAX_TEMP,
    DEFAULT_MIN_TEMP,
    DEFAULT_TARGET_TEMP,
)


@dataclass(frozen=True)
class BandViolation:
    """One contradiction, addressed to the field that should change."""

    #: The config key a user would naturally correct.
    field: str
    #: The config flow's error key, translated in ``strings.json``.
    code: str
    #: The same finding as a sentence, for callers that raise.
    message: str


def effective(
    candidate: dict[str, Any], current: dict[str, Any], key: str, default: Any
) -> float:
    """The value a save would leave in force for one field.

    Cross-field rules must judge the *pair that would be stored*, not just the
    submitted values: every write path here is partial — an options page saves
    one page over existing data, a service call carries one field, the climate
    slider carries one number — so a write that only touches one half of a pair
    can still create a contradiction with the stored other half.
    """
    return float(candidate.get(key, current.get(key, default)))


def violations(
    candidate: dict[str, Any], current: dict[str, Any]
) -> list[BandViolation]:
    """Every comfort-band contradiction the stored result would carry."""
    found: list[BandViolation] = []

    def eff(key: str, default: Any) -> float:
        return effective(candidate, current, key, default)

    target = eff(CONF_TARGET_TEMP, DEFAULT_TARGET_TEMP)
    minimum = eff(CONF_MIN_TEMP, DEFAULT_MIN_TEMP)
    maximum = eff(CONF_MAX_TEMP, DEFAULT_MAX_TEMP)
    day = eff(CONF_COMFORT_TEMP_DAY, DEFAULT_COMFORT_TEMP_DAY)
    night = eff(CONF_COMFORT_TEMP_NIGHT, DEFAULT_COMFORT_TEMP_NIGHT)
    start = int(eff(CONF_DAY_START_HOUR, DEFAULT_DAY_START_HOUR))
    end = int(eff(CONF_DAY_END_HOUR, DEFAULT_DAY_END_HOUR))

    if minimum > target:
        found.append(
            BandViolation(
                CONF_MIN_TEMP,
                "min_above_target",
                f"A coldest acceptable temperature of {minimum:g} °C is above "
                f"the {target:g} °C target",
            )
        )
    if target > maximum:
        found.append(
            BandViolation(
                CONF_MAX_TEMP,
                "max_below_target",
                f"A warmest acceptable temperature of {maximum:g} °C is below "
                f"the {target:g} °C target",
            )
        )
    if night > day:
        found.append(
            BandViolation(
                CONF_COMFORT_TEMP_NIGHT,
                "night_above_day",
                f"A night-time comfort temperature of {night:g} °C is above "
                f"the {day:g} °C daytime one",
            )
        )
    # get_comfort_temp only returns the day value for start <= hour < end, so
    # start >= end leaves the house on the night temperature around the clock.
    if start >= end:
        found.append(
            BandViolation(
                CONF_DAY_END_HOUR,
                "day_window_empty",
                f"The heating day would start at {start}:00 and end at "
                f"{end}:00, leaving no daytime period at all",
            )
        )
    # Day and night comfort must sit inside the band itself: the reported
    # savings are computed against the comfort reference in force, so an
    # out-of-band day or night leaves the plan essentially unchanged while
    # the savings figure is measured against a comfort the user cannot
    # actually experience (issue #92). The night lower edge is demanded
    # only while the night selector can express it: `minimum` reaches 25
    # on its own slider while night stops at 24, and demanding the
    # impossible would dead-end every form that pair reaches -- the trap
    # the first attempt at this rule fell into. The joint satisfiability
    # sweep in tests/entities.py pins the whole rule set against exactly
    # that, at every slider extreme.
    if day < minimum or day > maximum:
        found.append(
            BandViolation(
                CONF_COMFORT_TEMP_DAY,
                "comfort_outside_band",
                f"A daytime comfort temperature of {day:g} °C is outside "
                f"the {minimum:g}-{maximum:g} °C comfort band",
            )
        )
    night_below_band = night < minimum and minimum <= COMFORT_TEMP_NIGHT_SELECTOR_MAX
    if night_below_band or night > maximum:
        found.append(
            BandViolation(
                CONF_COMFORT_TEMP_NIGHT,
                "comfort_outside_band",
                f"A night-time comfort temperature of {night:g} °C is "
                f"outside the {minimum:g}-{maximum:g} °C comfort band",
            )
        )
    return found


def errors(candidate: dict[str, Any], current: dict[str, Any]) -> dict[str, str]:
    """The config flow's view: field to error key."""
    return {v.field: v.code for v in violations(candidate, current)}


def describe(found: list[BandViolation]) -> str:
    """The findings as one sentence, for a caller that raises."""
    return "; ".join(v.message for v in found)
