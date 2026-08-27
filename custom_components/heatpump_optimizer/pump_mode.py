"""What the heat pump's operating mode says it can currently deliver.

One table, five modes, two questions: can this unit heat the house right now,
and can it make hot water right now. Everything downstream — slot suppression
in the planner, the comfort floors the plan is allowed to promise, and a
future path that *writes* the mode — reads its answer from here, so there is
exactly one place where "DHW means no space heating" is written down.

**Read only, in this release.** The optimizer never writes the mode. The
table nevertheless carries what a writer would need (``key``, the device's
own enum value, and ``options``, the strings a Home Assistant ``select``
actually offers) because the alternative is to encode the vocabulary twice
and have the two halves disagree the first time a mode is renamed.

**The state is the label, not the enum.** This matters and is easy to get
wrong. The reference integration builds its ``select`` from a mapping of
device enum value to human label — ``{"HEATDHW": "Heating + DHW", ...}`` —
sets ``_attr_options`` to the *labels*, and returns a label from
``current_option``. So the Home Assistant state of the mode entity reads
``Heating + DHW``, never ``HEATDHW``. A vocabulary that matched only the
device enum would recognise nothing at all on a real install, and — because
an unrecognised mode falls back to full capability — would silently do
nothing forever rather than fail loudly. Both spellings are accepted, plus
the obvious near-misses, and matching is on an alphanumeric-only fold so
punctuation, case and spacing cannot break it.

**Two duties at once.** ``HEATDHW`` and ``COOLDHW`` are not "either/or"
modes: the unit runs both duties concurrently. That contradicts the comment
in ``_commanded_power`` that "the compressor serves them one at a time",
which is true of the single-duty modes and of most single-circuit units, and
false for this hardware in these two modes. It is recorded here as
``concurrent`` so that a future mode-writing path, or any capacity reasoning
that needs it, inherits the correct premise rather than the convenient one.

**Unknown means full capability, never "suppress everything".** An
unrecognised word, a pump from a different vendor, a mode this table has not
learned yet: all of them fall back to "this pump can do everything". The
asymmetry is deliberate. Wrongly believing the pump is capable costs a plan
that over-promises for one interval; wrongly believing it is incapable
suppresses heating on the strength of a word nobody recognised, which in
January is a cold house.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

#: The device's own enum values (Tuya DP 2 on the reference unit).
MODE_COOL = "cool"
MODE_HEAT = "heat"
MODE_DHW = "DHW"
MODE_COOL_DHW = "COOLDHW"
MODE_HEAT_DHW = "HEATDHW"


def _fold(raw: object) -> str:
    """Lowercase, alphanumerics only — the form aliases are matched in."""
    return re.sub(r"[^a-z0-9]+", "", str(raw).strip().lower())


@dataclass(frozen=True)
class ModeCapability:
    """What one operating mode allows the pump to do."""

    #: The device's enum value, or ``None`` for the unknown fallback. What a
    #: future writer would put on the wire.
    key: str | None
    #: Human name, for logs and explanations.
    label: str
    #: Whether space heating can be delivered in this mode.
    space_heat: bool
    #: Whether hot water can be made in this mode.
    dhw: bool
    #: Whether the mode is actively cooling. Not the negation of
    #: ``space_heat``: a hot-water-only mode heats nothing and cools nothing.
    cooling: bool = False
    #: Whether the unit serves both of its duties at the same time in this
    #: mode, rather than one after the other.
    concurrent: bool = False
    #: Whether this is a mode the table actually recognises.
    known: bool = True
    #: The Home Assistant ``select`` options that mean this mode. The first
    #: entry is what the reference integration displays, which is also what
    #: ``select.select_option`` would have to be given to write it.
    options: tuple[str, ...] = field(default_factory=tuple)


#: What an absent, unusable or unrecognised mode reading resolves to: a pump
#: that can do everything. Fails safe toward "plan normally".
FULL_CAPABILITY = ModeCapability(
    key=None,
    label="Unknown",
    space_heat=True,
    dhw=True,
    cooling=False,
    # The pre-v5.2.0 assumption, kept for anything unrecognised: without
    # evidence that this unit runs two duties at once, do not assume it can.
    concurrent=False,
    known=False,
)


#: Every mode the reference unit exposes, keyed by its device enum value.
MODES: dict[str, ModeCapability] = {
    mode.key: mode
    for mode in (
        ModeCapability(
            key=MODE_COOL,
            label="Cooling",
            space_heat=False,
            dhw=False,
            cooling=True,
            options=("Cooling",),
        ),
        ModeCapability(
            key=MODE_HEAT,
            label="Heating",
            space_heat=True,
            dhw=False,
            options=("Heating",),
        ),
        ModeCapability(
            key=MODE_DHW,
            label="Hot water only",
            space_heat=False,
            dhw=True,
            options=("DHW (Hot Water)",),
        ),
        ModeCapability(
            key=MODE_COOL_DHW,
            label="Cooling and hot water",
            space_heat=False,
            dhw=True,
            cooling=True,
            concurrent=True,
            options=("Cooling + DHW",),
        ),
        ModeCapability(
            key=MODE_HEAT_DHW,
            label="Heating and hot water",
            space_heat=True,
            dhw=True,
            concurrent=True,
            options=("Heating + DHW",),
        ),
    )
}

#: Device enum values in the order the device lists them.
MODE_KEYS: tuple[str, ...] = tuple(MODES)


def _build_aliases() -> dict[str, str]:
    """Folded spelling -> device enum value.

    Seeded from the enum values and the select's own option labels — the two
    spellings that actually occur — and then widened with the near-misses a
    differently-configured integration might publish.
    """
    aliases: dict[str, str] = {}
    for key, mode in MODES.items():
        aliases[_fold(key)] = key
        aliases[_fold(mode.label)] = key
        for option in mode.options:
            aliases[_fold(option)] = key
    aliases.update(
        {
            _fold(spelling): key
            for spelling, key in (
                ("cooling", MODE_COOL),
                ("cool only", MODE_COOL),
                ("heating", MODE_HEAT),
                ("heat only", MODE_HEAT),
                ("space heating", MODE_HEAT),
                ("hot water", MODE_DHW),
                ("hotwater", MODE_DHW),
                ("dhw only", MODE_DHW),
                ("water heating", MODE_DHW),
                ("cool dhw", MODE_COOL_DHW),
                ("cool + dhw", MODE_COOL_DHW),
                ("cooling and dhw", MODE_COOL_DHW),
                ("cooling + hot water", MODE_COOL_DHW),
                ("heat dhw", MODE_HEAT_DHW),
                ("heat + dhw", MODE_HEAT_DHW),
                ("heating and dhw", MODE_HEAT_DHW),
                ("heating + hot water", MODE_HEAT_DHW),
            )
        }
    )
    return aliases


_ALIASES: dict[str, str] = _build_aliases()


def resolve(raw: object) -> str | None:
    """The device enum value a reported state means, or ``None``."""
    if raw is None:
        return None
    return _ALIASES.get(_fold(raw))


def capability(raw: object) -> ModeCapability:
    """What the pump can do in the mode this state describes.

    Tolerant by design: unknown in, full capability out. ``known`` on the
    result is how a caller tells "the pump told us it can do everything" from
    "we have no idea, so we are assuming it can".
    """
    key = resolve(raw)
    if key is None:
        return FULL_CAPABILITY
    return MODES[key]


def is_known(raw: object) -> bool:
    """Whether this state names a mode the table recognises.

    Written to be passed straight to ``InputReader.read_state(valid=...)``,
    for a caller that would rather see an unrecognised mode reported as a
    problem — visible in the diagnostics, with the entity named — than folded
    silently into full capability. Both are safe; only one is legible.
    """
    return resolve(raw) is not None
