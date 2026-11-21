"""Which interval a learner may ingest: the one freeze predicate (ADR-008).

Pure: the coordinator builds :class:`Facts` once per ask from the cycle's
own state, the module owning each piece of local evidence computes it into
:class:`Evidence`, and :func:`reason` answers. No learner holds a facts
value; a learner states only which kind of sample it folds (:class:`Sample`).

Fail closed. A learner that pauses for an hour loses an hour of
convergence; a learner that trains on a flatline or on heat it did not
supply corrupts a parameter that is persisted to disk.

The order is the root-cause order: a reason earlier in :func:`reason`
outranks every later one, so the reason reported is the one a user should
look at first. Reason strings are displayed (``learner_progress.pauses``,
the freeze notes) and are kept verbatim.
"""

from __future__ import annotations

import enum
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

REASON_EXTERNAL_HEAT = "external_heat_source"
REASON_DEFROSTING = "defrosting"
REASON_VENTILATION = "ventilation"
REASON_AWAY = "away"
REASON_AWAY_RECOVERY = "away_recovery"
REASON_UNPLANNED_CHARGE = "unplanned_charge"
REASON_AT_RUNNING_FLOOR = "at_running_floor"
REASON_CHARGE_OPEN = "charge_open"
REASON_ASK_IGNORED = "ask_ignored"


class Sample(enum.Enum):
    """The kind of sample a learner folds; it decides which reasons refuse it."""

    #: a plant reading with no room air in it (tank standby, buffer, COP)
    PLANT = "plant"
    #: a room-air reading (the fabric learners)
    ROOM_AIR = "room_air"
    #: a property of the occupied house (internal gains, the quiet-comfort evidence)
    OCCUPANCY = "occupancy"
    #: the comfort a resident reads (the curve learner)
    COMFORT = "comfort"
    #: heat the plan put into space heating, attributed by its split
    SPACE_HEAT = "space_heat"
    #: the same, on metered heat: no room air in the sample (R10-COP-GATE item E)
    METERED_SPACE_HEAT = "metered_space_heat"
    #: a running-draw ceiling sample of a draw-range experiment
    CEILING = "ceiling"
    #: the tank's draws and usage hours (no room air; occupied)
    TANK_DRAW = "tank_draw"
    #: the defrost derate's delivered-over-asked ratio
    DELIVERED_RATIO = "delivered_ratio"


#: Kinds the open-window detector refuses: every one with room air in it.
_ROOM_AIR_KINDS = frozenset(
    {Sample.ROOM_AIR, Sample.OCCUPANCY, Sample.COMFORT, Sample.SPACE_HEAT, Sample.CEILING}
)
#: Kinds an away period falsifies: the occupancy-borne ones.
_AWAY_KINDS = frozenset({Sample.OCCUPANCY, Sample.COMFORT, Sample.TANK_DRAW})


@dataclass(frozen=True)
class Facts:
    """The cycle's plant-wide facts, built by the coordinator per ask."""

    external_heat: bool = False
    #: ``PumpSignals.freeze_reason``: online, fault, cooling mode
    signals: str | None = None
    defrosting: bool = False
    #: configured readings that are unusable: key -> problem
    unusable: Mapping[str, str] = field(default_factory=dict)
    ventilation: bool = False
    #: the boost freeze's reason while it holds, else None
    boost: str | None = None
    #: the early cut, the supply hold or the unmetered power (``_tail_freeze``)
    tail: str | None = None
    away: bool = False
    away_recovery: bool = False


@dataclass(frozen=True)
class Evidence:
    """The interval's local evidence, each field computed by the module holding its inputs."""

    #: ``heat_energy``: an unobserved interval the plan put no hot water in, over which the tank rose
    unplanned_charge: bool = False
    #: ``draw_range``: the experiment's draw sat at the running floor in force
    at_running_floor: bool = False
    #: ``dhw_learning``: the interval starts or ends on a heated sample of an open charge
    charge_open: bool = False
    #: ``accuracy``: ``MeasuredCop.scale_response`` reads the ask ignored
    ask_ignored: bool = False


NO_EVIDENCE = Evidence()


def space_heat(metered: bool) -> Sample:
    """The space-heat kind of a sample whose heat is ``metered``, or inferred from the room."""
    return Sample.METERED_SPACE_HEAT if metered else Sample.SPACE_HEAT


#: The additive reasons, after the shared ones and in this order: each with
#: the kinds it refuses and the fact or evidence that raises it. An away
#: setback sits below the floor the curve tracker reads and the recovery
#: climbs back through it, so the recovery refuses the comfort kind alone.
_ADDITIVE: tuple[tuple[str, frozenset[Sample], Callable[[Facts, Evidence], bool]], ...] = (
    (REASON_AWAY, _AWAY_KINDS, lambda f, e: f.away),
    (REASON_AWAY_RECOVERY, frozenset({Sample.COMFORT}), lambda f, e: f.away_recovery),
    (REASON_UNPLANNED_CHARGE, frozenset({Sample.SPACE_HEAT, Sample.METERED_SPACE_HEAT}),
     lambda f, e: e.unplanned_charge),
    (REASON_AT_RUNNING_FLOOR, frozenset({Sample.CEILING}), lambda f, e: e.at_running_floor),
    (REASON_CHARGE_OPEN, frozenset({Sample.TANK_DRAW}), lambda f, e: e.charge_open),
    (REASON_ASK_IGNORED, frozenset({Sample.DELIVERED_RATIO}), lambda f, e: e.ask_ignored),
)


def reason(
    facts: Facts, keys: tuple[str, ...], sample: Sample, evidence: Evidence = NO_EVIDENCE
) -> str | None:
    """Why a ``sample`` over ``keys`` must not be folded this interval, or ``None``.

    The delivered ratio answers its own reason alone (#944): the caller's
    power gate owns the shared reasons and exempts ``defrosting``, the
    derate's own input.
    """
    if sample is not Sample.DELIVERED_RATIO:
        shared = _shared(facts, keys, sample)
        if shared is not None:
            return shared
    return next(
        (why for why, kinds, raised in _ADDITIVE if sample in kinds and raised(facts, evidence)),
        None,
    )


def _shared(facts: Facts, keys: tuple[str, ...], sample: Sample) -> str | None:
    """The nine reasons every kind but the delivered ratio answers, in today's order."""
    if facts.external_heat:
        return REASON_EXTERNAL_HEAT
    # v5.3.0: the plant-wide freezes, from the heat pump's own signals.
    # They have a shape the key loop below cannot express: that loop asks
    # "is the reading the caller named unusable" and freezes on the
    # *absence* of a measurement, while these freeze on the *presence*
    # of one -- the online flag says False, the fault flag says True,
    # the mode says cooling. Each is a healthy, fresh reading that
    # happens to be bad news and makes the whole interval misleading
    # rather than one sensor unreadable, so they are not scoped to the
    # caller's keys either, and they sit ahead of the key loop as the
    # root cause when both fire: reporting the symptom would send a
    # user looking at the wrong thing. See ``pump_signals.py`` for why
    # the absence of these signals never freezes anything.
    if facts.signals is not None:
        return facts.signals
    # #944 (round-4 D7-03): a fourth presence condition, kept out of
    # ``freeze_reason`` because the derate still folds these intervals
    # (the settlement exempts the reason it causes). A defrost reverses
    # the cycle -- the interval's heat is negative while the learners
    # replay the commanded power as if it had flowed -- and happens
    # below the frost band too, where the COP learner's guard ends.
    if facts.defrosting:
        return REASON_DEFROSTING
    # An unusable input outranks ventilation deliberately: the heat-loss
    # learner treats "ventilation" as a pass-through to keep feeding
    # the detector, and a flatline fed through that pass would
    # drive the very detector that froze everything. With the input
    # check first, the latch simply holds until real data returns.
    #
    # v5.1.3: freeze on ANY unusable reading, not only ``stale``.
    # ``_update_current_state`` deliberately PINS the last good value when
    # a read fails: right for the *input*, fatal for a *learner*, which
    # then reads a frozen number as thermal behaviour and persists it (a
    # dropped Zigbee sensor walked the house heat-loss scale from 1.0 to
    # ~0.37 inside 48 h). The coordinator lists a reading here only when it
    # has an entity: a slot the user never configured reads
    # ``not_configured`` with none and must NOT freeze learning.
    for key in keys:
        problem = facts.unusable.get(key)
        if problem is not None:
            return f"{problem}:{key}"
    # #26: training on an open window teaches a phantom heat loss the
    # house does not have -- measured in degC-scale residuals, far above
    # any learning signal. A sample with no room air in it is untouched.
    if sample in _ROOM_AIR_KINDS and facts.ventilation:
        return REASON_VENTILATION
    # #1935: boost space heating -- either surface -- actuates heat the
    # plan's trajectory never assumed, so every residual is warm-side
    # garbage. Ranked below "ventilation" deliberately: that is the one
    # reason the heat-loss learner looks past (its pass-through feeds the
    # window CUSUM), and a boost window must not starve the detector.
    if facts.boost is not None:
        return facts.boost
    # The early cut, then the held supply write, then the unmetered power
    # (``coordinator._tail_freeze``): each an interval that did not run the
    # commanded power.
    return facts.tail
