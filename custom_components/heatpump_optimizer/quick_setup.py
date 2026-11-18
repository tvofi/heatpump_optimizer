"""The quick-setup path's answer-to-config mapping.

The full initial wizard is eleven pages. Only two answers are genuinely
required — a price source (a Tibber token, or a price entity) and a weather
entity — so a new user who stops
after the first two screens already has a working entry with shipped defaults
(``finish_setup``'s "finish now"). What that minimal path cannot know is what
the house *is*: how many zones, whether there is a buffer store, a DHW tank,
a wood furnace with its own tank, and what the building is made of. Those are
the answers that change the thermal model from "a plausible prior" into "this
house", and they are exactly the answers ``presets.py`` already derives physics
from.

This module turns the quick-setup page's handful of yes/no answers plus the
building questionnaire into the config keys the coordinator reads. It writes
only existing keys (no new option keys), it is the *only* place that maps a
question to a key, and it stays free of Home Assistant imports like
``presets``, ``modbus_prefill`` and ``device_prefill`` so ``tests/features.py``
can drive it directly.

Two of the questions have no boolean flag in the model, and the mapping states
the convention rather than hiding it:

* "Buffer tank" — the integration always models a buffer; what the question
  means is *is it a store*. That is derived, not configured: a buffer is a
  store only when its volume reaches ``BUFFER_STORE_MIN_VOLUME``. "yes" writes a
  store-sized volume, "no" leaves the shipped small default (not a store).
* "Wood buffer tank" — a second tank only enters the two-tank physics when
  its top/bottom probe entities are present (that is the model's own gate,
  ``wood_furnace_on`` and a probe), which is why the page asks for the probes
  beside the question. "yes" records the tank volume; the probe entities the
  user picks on the page are what activate the two-tank physics.

The zone answer is written as the explicit override (``two_zone_mode``), never
by adding or removing the two-zone presence keys, because the latter is exactly
the trap the options flow defends against (a fresh entry's voluptuous defaults
silently flipping a 1-zone house to 2-zone).
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from . import presets
from .const import (
    BUFFER_STORE_MIN_VOLUME,
    CONF_BUFFER_TANK_VOLUME,
    CONF_BUILDING_ERA,
    CONF_BUILDING_FOUNDATION,
    CONF_BUILDING_PRESET_ENABLED,
    CONF_BUILDING_STRUCTURE,
    CONF_DHW_ENABLED,
    CONF_HEATED_AREA,
    CONF_LOWER_EMITTER,
    CONF_TWO_ZONE_MODE,
    CONF_UPPER_EMITTER,
    CONF_WOOD_FURNACE_ENABLED,
    CONF_WOOD_TANK_BOTTOM_ENTITY,
    CONF_WOOD_TANK_TOP_ENTITY,
    CONF_WOOD_TANK_VOLUME,
    DEFAULT_HEATED_AREA,
    DEFAULT_UPPER_FLOOR_AREA_RATIO,
    DEFAULT_WOOD_TANK_VOLUME,
    TWO_ZONE_MODE_AUTO,
    TWO_ZONE_MODE_OFF,
    TWO_ZONE_MODE_ON,
)

#: The quick-setup form's transient fields. These are *questions*, not option
#: keys — the keys below would collide with real option names if spelled as
#: such, so they are named for what the user is asked.
FIELD_TWO_ZONE: Final = "two_zone"
FIELD_BUFFER_TANK: Final = "buffer_tank"
FIELD_DHW_TANK: Final = "dhw_tank"
FIELD_WOOD_FURNACE: Final = "wood_furnace"
FIELD_WOOD_BUFFER_TANK: Final = "wood_buffer_tank"

#: The volume "buffer tank: yes" writes, in litres. Store-sized — above
#: ``BUFFER_STORE_MIN_VOLUME`` (100 L) — but not an assumption about a specific
#: house; the user refines it on the building page. Kept here rather than in
#: ``const.py`` so the quick-setup mapping is self-contained, like ``presets``
#: own tables.
QUICK_SETUP_BUFFER_VOLUME: Final = 500.0

#: The five questions, in the order the page asks them.
FIELD_QUESTIONS: Final = (
    FIELD_TWO_ZONE,
    FIELD_BUFFER_TANK,
    FIELD_DHW_TANK,
    FIELD_WOOD_FURNACE,
    FIELD_WOOD_BUFFER_TANK,
)

#: The questions' shipped answers — ONE source, read by the fresh form's
#: defaults, by the Configure form's suggestions for never-answered questions,
#: and by :func:`derive`'s own fallbacks, so the three can never disagree.
#: v6.6.5 carried the same values inline in each place; #1273 is what happened
#: the one time a caller (the Configure page) fed them back without knowing
#: they were answers.
SHIPPED_ANSWERS: Final[dict[str, bool]] = {
    FIELD_TWO_ZONE: False,
    FIELD_BUFFER_TANK: False,
    FIELD_DHW_TANK: True,
    FIELD_WOOD_FURNACE: False,
    FIELD_WOOD_BUFFER_TANK: False,
}


def stored_answers(current: Mapping[str, Any]) -> dict[str, bool]:
    """The five questions' answers as an existing entry records them (#1258).

    The REVERSE of ``derive``, question by question, and honest about what
    the config actually says: an answer the entry carries comes back as that
    answer, and a question the entry has never answered is ABSENT — never a
    guessed False — so the Configure page can leave it at its shipped default
    for the user to answer and an untouched submit cannot turn "never
    answered" into "answered no" underneath them. That absence is what
    #1273's nightly-ha red hinged on: re-deriving an existing entry with the
    shipped answers flipped its two-zone mode off.

    What each question leaves behind, read back:

    * two zones — the explicit ``two_zone_mode`` override, when it is the
      on/off value ``derive`` writes (``auto`` is not an answer; the page
      shows the shipped "no" for it);
    * buffer tank — a stored ``buffer_tank_volume``: a store-sized volume is
      the "yes" the question writes, anything smaller is a recorded "no";
    * DHW tank / wood furnace — the flags ``derive`` always writes;
    * wood buffer tank — the two probes or a stored tank volume say "yes";
      "no" writes nothing, so an entry without any of them is unrecorded.
    """
    answers: dict[str, bool] = {}
    # The default names the absent value exactly (``auto``), which the
    # absent-fallback proof reads: absent and default are the same state, an
    # entry that never chose is not recorded as having chosen either way.
    mode = current.get(CONF_TWO_ZONE_MODE, TWO_ZONE_MODE_AUTO)
    if mode in (TWO_ZONE_MODE_ON, TWO_ZONE_MODE_OFF):
        answers[FIELD_TWO_ZONE] = mode == TWO_ZONE_MODE_ON
    volume = current.get(CONF_BUFFER_TANK_VOLUME)
    if volume is not None:
        answers[FIELD_BUFFER_TANK] = float(volume) >= BUFFER_STORE_MIN_VOLUME
    if current.get(CONF_DHW_ENABLED) is not None:
        answers[FIELD_DHW_TANK] = bool(current.get(CONF_DHW_ENABLED))
    if current.get(CONF_WOOD_FURNACE_ENABLED) is not None:
        answers[FIELD_WOOD_FURNACE] = bool(current.get(CONF_WOOD_FURNACE_ENABLED))
    if (
        current.get(CONF_WOOD_TANK_TOP_ENTITY)
        or current.get(CONF_WOOD_TANK_BOTTOM_ENTITY)
        or current.get(CONF_WOOD_TANK_VOLUME) is not None
    ):
        answers[FIELD_WOOD_BUFFER_TANK] = True
    return answers


def suggested_answers(current: Mapping[str, Any]) -> dict[str, bool]:
    """What the Configure page suggests: stored answers, shipped elsewhere.

    The Configure form's suggested value for each question — the entry's own
    answer where it has one, the shipped default where it does not — and the
    baseline its handler compares a submission against, so a submit that
    answers nothing the page did not already say writes nothing.
    """
    return {**SHIPPED_ANSWERS, **stored_answers(current)}


def derive(answers: dict[str, Any]) -> dict[str, Any]:
    """Turn the quick-setup answers into config keys.

    ``answers`` is the page's flattened ``user_input``: the transient
    :data:`FIELD_*` booleans plus the building-questionnaire keys
    (``building_structure``, ``building_era``, ``building_foundation``,
    ``heated_area_m2``, ``upper_floor_emitter``, ``lower_floor_emitter``).

    Returns the config-key dict to merge into the entry's setup data. A "no"
    answer writes nothing for its key, so the shipped default applies; a "yes"
    writes the explicit override or value.
    """
    two_zone = bool(answers.get(FIELD_TWO_ZONE, SHIPPED_ANSWERS[FIELD_TWO_ZONE]))
    structure = answers.get(CONF_BUILDING_STRUCTURE, presets.STRUCTURE_TIMBER_SLAB)
    era = answers.get(CONF_BUILDING_ERA, presets.ERA_1980_2005)
    foundation = answers.get(CONF_BUILDING_FOUNDATION, presets.FOUNDATION_NONE)
    heated_area = float(answers.get(CONF_HEATED_AREA, DEFAULT_HEATED_AREA))
    upper_emitter = answers.get(CONF_UPPER_EMITTER, presets.EMITTER_RADIATORS)
    lower_emitter = answers.get(CONF_LOWER_EMITTER, presets.EMITTER_FLOOR)
    wood_top = answers.get(CONF_WOOD_TANK_TOP_ENTITY)
    wood_bottom = answers.get(CONF_WOOD_TANK_BOTTOM_ENTITY)

    preset = presets.BuildingPreset(
        structure=structure,
        era=era,
        foundation=foundation,
        heated_area_m2=heated_area,
        upper_emitter=upper_emitter,
        lower_emitter=lower_emitter,
        upper_area_ratio=DEFAULT_UPPER_FLOOR_AREA_RATIO,
        two_zone=two_zone,
    )
    derived = presets.derive(preset)
    # Informational only; not a thermal parameter and rejected by the model.
    derived.pop("heating_response_hours", None)

    return {
        # The explicit override, never zone-key presence: a fresh entry has no
        # zone keys, and adding them is what silently flips a house to 2-zone.
        CONF_TWO_ZONE_MODE: TWO_ZONE_MODE_ON if two_zone else TWO_ZONE_MODE_OFF,
        CONF_DHW_ENABLED: bool(
            answers.get(FIELD_DHW_TANK, SHIPPED_ANSWERS[FIELD_DHW_TANK])
        ),
        CONF_WOOD_FURNACE_ENABLED: bool(
            answers.get(FIELD_WOOD_FURNACE, SHIPPED_ANSWERS[FIELD_WOOD_FURNACE])
        ),
        CONF_BUILDING_PRESET_ENABLED: True,
        CONF_BUILDING_STRUCTURE: structure,
        CONF_BUILDING_ERA: era,
        CONF_BUILDING_FOUNDATION: foundation,
        CONF_HEATED_AREA: heated_area,
        CONF_UPPER_EMITTER: upper_emitter,
        CONF_LOWER_EMITTER: lower_emitter,
        **({
            CONF_BUFFER_TANK_VOLUME: QUICK_SETUP_BUFFER_VOLUME
        } if answers.get(
            FIELD_BUFFER_TANK, SHIPPED_ANSWERS[FIELD_BUFFER_TANK]
        ) else {}),
        **({
            CONF_WOOD_TANK_VOLUME: DEFAULT_WOOD_TANK_VOLUME
        } if answers.get(
            FIELD_WOOD_BUFFER_TANK, SHIPPED_ANSWERS[FIELD_WOOD_BUFFER_TANK]
        ) else {}),
        # The probes are the two-tank model's own gate, so they are written
        # whenever the user picked them; the volume alone changes nothing.
        **({CONF_WOOD_TANK_TOP_ENTITY: wood_top} if wood_top else {}),
        **({CONF_WOOD_TANK_BOTTOM_ENTITY: wood_bottom} if wood_bottom else {}),
        **derived,
    }
