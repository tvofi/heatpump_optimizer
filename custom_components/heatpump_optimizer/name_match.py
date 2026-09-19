"""The fallback that reads a device's entity NAMES when no table proves it (#1067).

``device_prefill`` resolves a device from the definitions of the integration
that publishes it, and refuses what those definitions do not prove: a device
from an integration with no table, or one whose own table cannot establish its
model, resolves nothing. That refusal is right and it leaves the pre-fill page
empty for the owner's own case -- a locally-configured pump, or a brand whose
definitions this repository has never seen (#1067 owner decision 7).

This module is the fallback, and it guesses, so it is built to be boring:

* **The hard filter runs first, and it is not a name test.** A candidate must
  already be the role's domain, its device class where the role names one, and
  its unit *family* (degrees Celsius with kelvin, watts with kilowatts) before
  any name is read. Nothing here matches on a name alone, which is why a role
  with no physical unit is out of reach: the hot water and silent-mode
  windows, the legionella interval and the flag slots are not in
  :data:`ROLE_FILTERS` at all. A set-point role is in reach because a Home
  Assistant state carrying a unit already reads in engineering units, so the
  role's scale is 1.0.
* **A name is evidence, not identity.** ``entity_id``, ``original_name`` and
  ``translation_key`` are lowercased, split on case, underscore and digit
  boundaries, and stripped of the words every one of the device's entity ids
  starts with -- the device's own name, which the integration prefixes to
  each. Each is scored against the role's synonym phrases as the mean of the
  phrase's token coverage and a :mod:`difflib` ratio, so a phrase whose words
  are all present scores high and a name carrying a phrase's words *plus*
  others scores lower.
* **A suggestion needs a winner, not a candidate.** A role is suggested only
  when its best score clears :data:`THRESHOLD` and beats the runner-up by
  :data:`MARGIN`; a tie or a near-tie gives nothing, and one entity is
  suggested for at most one role. The trap this exists for is real: on the
  pinned sources, dp 10 is named ``Outlet Water Temperature (T1)`` and dp 106
  ``Heat Exchanger Outlet Water Temperature (Tout)``, and only one of them is
  the supply.

The two constants are **measured, not chosen**: ``tools/measure_prefill_corpus.py``
sweeps them over the labelled corpus and prints the grid the shipped pair
comes from, and ``tests/features.py`` asserts the corpus has no wrong
suggestion at that pair. Raising the threshold buys precision and spends
recall, which is the right direction to spend it in: a role this misses is one
the user fills by hand, and a role it fills wrongly is one the plan reads from
the wrong probe.

Kept free of Home Assistant imports, like ``modbus_prefill`` and
``device_prefill`` which it serves.
"""
from __future__ import annotations

import difflib
import re
from collections.abc import Callable, Iterable
from typing import NamedTuple, Protocol

from .const import (
    CONF_COMPRESSOR_FREQ_SENSOR,
    CONF_DHW_TEMP_ENTITY,
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
    CONF_OUTDOOR_TEMP_ENTITY,
)

#: How a name-matched role is named on the page, where the source tables are
#: named by their own platform.
SOURCE = "name match"

#: The decision rule. Both are read off the corpus sweep in
#: ``tools/measure_prefill_corpus.py``; the pair below is the widest-recall
#: cell of the grid that reports **no** wrong suggestion.
THRESHOLD = 0.60
MARGIN = 0.08


class Named(Protocol):
    """One entity-registry record, as much of it as a name is read from.

    A structural type rather than an import of ``device_prefill.EntityRecord``:
    that module is this one's caller, and the fields below are all the matcher
    needs to see. Declared as read-only properties rather than as plain
    attributes, because the record that satisfies this is a ``NamedTuple``
    whose fields are read-only, and a settable attribute in the protocol would
    demand a settable one in the implementation.
    """

    @property
    def entity_id(self) -> str:
        """The entity id, domain included -- ``sensor.hp_t4``."""

    @property
    def original_name(self) -> str | None:
        """The name the registry holds, or None where the entity has none."""

    @property
    def translation_key(self) -> str | None:
        """The translation key the integration gave it, if any."""

    @property
    def device_class(self) -> str | None:
        """The device class Home Assistant published for it, if any."""

    @property
    def unit(self) -> str | None:
        """The unit of measurement its state carries, if any."""

    @property
    def domain(self) -> str:
        """The entity id's domain -- ``sensor`` for ``sensor.hp_t4``."""


class Role(NamedTuple):
    """What a candidate must be before its name is read at all."""

    #: The entity domains the role is configured with.
    domains: tuple[str, ...]
    #: The device classes the role names; empty where it names none, which is
    #: where Home Assistant publishes no device class at all (the ``number``
    #: entities a set-point role reads).
    device_classes: tuple[str, ...]
    #: The unit family the role reads in.
    unit_family: str


#: The unit spellings each family accepts. Deliberately narrow: an energy
#: total is not a power reading and a Fahrenheit probe is not a Celsius one,
#: so ``kWh`` and ``°F`` belong to no family a role here reads in, and a
#: perfect name in the wrong unit suggests nothing.
_FAMILIES: dict[str, frozenset[str]] = {
    "temperature": frozenset({"c", "k", "degc", "celsius", "kelvin"}),
    "frequency": frozenset({"hz"}),
    "power": frozenset({"w", "kw"}),
}

def family(unit: str | None) -> str | None:
    """The family a unit string belongs to, or None when it belongs to none.

    ``°C`` normalises to ``c`` and ``°F`` to ``f``, and neither is the other.
    """
    if not unit:
        return None
    text = unit.strip().lower().replace("°", "").replace(" ", "")
    for name, spellings in _FAMILIES.items():
        if text in spellings:
            return name
    return None


#: The roles the fallback can reach: a role is here only when its option reads
#: a physical quantity, and every one of these is also the unit a Home
#: Assistant state already carries, so the resolved scale is 1.0.
#:
#: Absent, and deliberately: the hot water and silent-mode windows (a
#: ``-``-joined clock string), the legionella interval (days), the control
#: mode and the flag slots (no unit), and the capacity-limited switch. A name
#: is no evidence for any of them.
ROLE_FILTERS: dict[str, Role] = {
    CONF_OUTDOOR_TEMP_ENTITY: Role(("sensor",), ("temperature",), "temperature"),
    CONF_DHW_TEMP_ENTITY: Role(("sensor",), ("temperature",), "temperature"),
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: Role(
        ("sensor",), ("temperature",), "temperature"),
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: Role(
        ("sensor",), ("temperature",), "temperature"),
    CONF_COMPRESSOR_FREQ_SENSOR: Role(("sensor",), ("frequency",), "frequency"),
    # The GCHV package's own roles, which a device may carry as a set-point
    # entity instead: register 404 is the hot water set-point, 405 the
    # anti-legionella set-point and 406 the hot water minimum.
    "r404": Role(("number",), (), "temperature"),
    "r405": Role(("number",), (), "temperature"),
    "r406": Role(("number",), (), "temperature"),
    # The package's unit-capacity reading, which the plan's power figure is
    # derived from. A rating, so a measured power or an energy total is not it.
    "unit_capacity": Role(("sensor",), (), "power"),
}

#: Each role's phrases: English and Swedish, plus the words the pinned source
#: definitions themselves use. The last part is not typed from memory --
#: ``tests/features.py`` derives the distinctive words of the entities the
#: source tables map out of the generated fixtures and asserts every one of
#: them is in the role's own vocabulary here, so a definition's word this list
#: omits fails the suite rather than silently missing the role.
#:
#: A phrase is as long as the role's evidence is: ``outlet water`` rather than
#: ``outlet water temperature``, because "temperature" is in every temperature
#: entity's name and a phrase carrying it would match ``Outlet temperature``
#: -- which on the pinned tuya-local config is the plate outlet (dp 106), not
#: the supply. That near-tie is the reason the rule has a margin at all.
SYNONYMS: dict[str, tuple[str, ...]] = {
    CONF_OUTDOOR_TEMP_ENTITY: (
        "outdoor temperature",
        "outdoor air",
        "ambient temperature",
        "outside temperature",
        "utomhustemperatur",
        "utomhus",
        "t4",
    ),
    CONF_DHW_TEMP_ENTITY: (
        "dhw tank",
        "tank temperature",
        "hot water tank",
        "dhw temperature",
        "varmvattentemperatur",
        "varmvattenberedare",
    ),
    CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: (
        "supply water",
        "leaving water",
        "flow water",
        "flow temperature",
        "supply temperature",
        "outlet water",
        "framledningstemperatur",
        "t1",
    ),
    CONF_HEAT_PUMP_RETURN_TEMP_ENTITY: (
        "return water",
        "return temperature",
        "entering water",
        "inlet water",
        "inlet temperature",
        "returtemperatur",
        "returvatten",
        "tw in",
        "tin",
    ),
    CONF_COMPRESSOR_FREQ_SENSOR: (
        "compressor frequency",
        "compressor speed",
        "compressor hz",
        "frequenz",
        "frekvens",
    ),
    "r404": (
        "dhw setpoint",
        "dhw set point",
        "hot water setpoint",
        "dhw target",
        "varmvattenbörvärde",
    ),
    "r405": (
        "legionella temperature",
        "legionella setpoint",
        "anti legionella",
        "legionella",
        "desinfection temperature",
    ),
    "r406": (
        "dhw minimum temperature",
        "minimum temperature",
        "min temperature",
        "lowest temperature",
        "dhw economic temperature",
        "lägsta temperatur",
    ),
    "unit_capacity": (
        "unit capacity",
        "nominal capacity",
        "capacity",
        "kapacitet",
    ),
}

#: ``tests/features.py`` derives the words each pinned definition names its
#: own mapped entities with and asserts they are all above; the words that
#: identify no reading ("temperature", "water") are excluded there, because a
#: definition's name is only evidence for the part of it that is distinctive.

class Match(NamedTuple):
    """One role a name filled, and how safely."""

    role: str
    entity_id: str
    #: The best score among the role's candidates.
    score: float
    #: The next best, so the reader can see the margin that was cleared.
    runner_up: float


def tokens(text: str) -> tuple[str, ...]:
    """A text's words: split on punctuation, case changes and digit runs.

    ``temp_current_f``, ``compressorFrequency`` and ``T1`` become their own
    words, so ``temp_current_f`` is not read as ``temp_current``.
    """
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)
    spaced = re.sub(r"(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])", " ", spaced)
    return tuple(word for word in re.split(r"[^a-z0-9]+", spaced.lower()) if word)


def score_name(name: str, phrase: str) -> float:
    """How well one phrase describes one name.

    Half the phrase's words being present, half a :mod:`difflib` ratio over
    the two strings. The first term is what makes a short, exact phrase win
    over a long name that merely contains one of its words; the second is what
    forgives a spelling the lists did not anticipate (``framledning`` for
    ``framledningstemperatur``).
    """
    wanted = set(tokens(phrase))
    if not wanted or not name:
        return 0.0
    covered = len(wanted & set(tokens(name))) / len(wanted)
    return 0.5 * covered + 0.5 * difflib.SequenceMatcher(None, name, phrase).ratio()


def _device_words(records: list[Named]) -> tuple[str, ...]:
    """The words every one of the device's entity ids starts with.

    A ``has_entity_name`` integration prefixes the device's own name to each
    entity id (``sensor.rotenso_windmi_outlet_water_temperature_t1``), and the
    device is the one thing in those strings that names nothing about the
    reading. Read off the records rather than passed in, so the matcher needs
    no device lookup: with fewer than two records there is no prefix to find,
    and with two it is their shared leading run.
    """
    if len(records) < 2:
        return ()
    runs = [tokens(record.entity_id.split(".", 1)[-1]) for record in records]
    common = list(runs[0])
    for run in runs[1:]:
        keep = 0
        while keep < min(len(common), len(run)) and common[keep] == run[keep]:
            keep += 1
        common = common[:keep]
    return tuple(common)


def _names(record: Named, device: tuple[str, ...]) -> tuple[str, ...]:
    """The texts one record is named by, device name stripped."""
    texts: list[str | None] = [
        record.entity_id.split(".", 1)[-1],
        record.original_name,
        record.translation_key,
    ]
    names = []
    for text in texts:
        if not text:
            continue
        words = tokens(text)
        if device and words[: len(device)] == device:
            words = words[len(device):]
        names.append(" ".join(words))
    return tuple(names)


def _passes(record: Named, role: Role) -> bool:
    """The hard filter: domain, device class and unit, before any name."""
    if record.domain not in role.domains:
        return False
    if role.device_classes and (record.device_class or "").lower() not in role.device_classes:
        return False
    return family(record.unit) == role.unit_family


def _candidates(
    records: list[Named],
    device: tuple[str, ...],
    role: str,
    scalar: Callable[[str, str], float],
) -> list[tuple[float, str]]:
    """The role's candidates, best first, ties broken on the entity id."""
    phrases = SYNONYMS[role]
    return sorted(
        (
            (
                max(
                    (
                        scalar(name, phrase)
                        for name in _names(record, device)
                        for phrase in phrases
                    ),
                    default=0.0,
                ),
                record.entity_id,
            )
            for record in records
            if _passes(record, ROLE_FILTERS[role])
        ),
        key=lambda pair: (-pair[0], pair[1]),
    )


def matches(
    records: Iterable[Named],
    taken: Iterable[str] = (),
    *,
    threshold: float = THRESHOLD,
    margin: float = MARGIN,
    name_score: Callable[[str, str], float] | None = None,
) -> list[Match]:
    """The roles these records' names fill, strongest claim first.

    ``taken`` is the roles already decided -- by a source table, or by the
    options in force -- and is never reopened. ``name_score`` replaces the
    module's own :func:`score_name`, which is how the corpus null control runs
    the whole decision with no name evidence at all.
    """
    pool = list(records)
    device = _device_words(pool)
    scalar = score_name if name_score is None else name_score
    candidates: list[Match] = []
    for role in ROLE_FILTERS:
        if role in taken:
            continue
        ranked = _candidates(pool, device, role, scalar)
        if not ranked:
            continue
        best, entity_id = ranked[0]
        runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
        if best >= threshold and best - runner_up >= margin:
            candidates.append(Match(role, entity_id, best, runner_up))
    chosen: list[Match] = []
    roles: set[str] = set()
    entities: set[str] = set()
    for match in sorted(candidates, key=lambda m: (-m.score, m.role, m.entity_id)):
        if match.role in roles or match.entity_id in entities:
            continue
        roles.add(match.role)
        entities.add(match.entity_id)
        chosen.append(match)
    return chosen
