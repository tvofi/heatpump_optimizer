"""One cycle's reading of the four heat-pump signals, resolved to decisions.

The four optional slots added in v5.2.0 — operating mode, defrosting, online
status and fault alarm — are read here, together, once per update cycle, and
turned into the three answers the rest of the integration actually asks:

* what the pump can deliver right now (:attr:`PumpSignals.mode`),
* whether the learners must stand down (:attr:`PumpSignals.freeze_reason`),
* whether this interval contains a defrost (:attr:`PumpSignals.defrosting`).

Keeping the resolution in one module rather than spread across the coordinator
is what makes the rules below checkable at a glance, because they are subtle
and their failure modes are silent.

The two rules
-------------

**A value acts. Its absence never does.** Every one of the four slots is
optional and most installs will have none of them. So an unconfigured slot,
an unavailable entity, a word the mode table does not recognise and a reading
past its horizon all resolve to *no evidence*, and no evidence is exactly the
pre-v5.2.0 behaviour: full capability, no freeze, no defrost. Only a reading
that is present, fresh and legible changes anything.

**Staleness demotes a signal to silence — it never promotes it to bad news.**
This is the rule that is easy to get wrong, and getting it wrong would break
the very installs this release is for. The reference integration runs in three
modes: LAN polling, cloud polling every three minutes, and MQTT push. Under
MQTT push it sets ``update_interval = None`` and writes entity state *only
when a datapoint changes* — so a healthy pump idling overnight can leave every
one of these four entities untouched for hours. Reading "the online flag has
not been written for 40 minutes" as "the pump is gone" would freeze the
learners of every MQTT user, every night. It is not evidence of anything.

That leaves the horizons in :data:`const.INPUT_MAX_AGE_MINUTES` doing the job
they are actually for: bounding how long a *value* may keep acting. A "cooling"
mode read six hours ago must not still be freezing the learners, and a defrost
flag that latched on yesterday must not still be excluding COP samples. The
horizon expires the evidence; it never manufactures any.

What closes the cloud gap
-------------------------

The hazard this release exists for is specific. In cloud mode, when Tuya
answers 200/success but the device's property timestamps are stale, that
coordinator sets ``is_online = False`` and **returns the stale data anyway** —
it does not raise ``UpdateFailed`` on that branch, unlike the HTTP-error
branches either side of it. Its online binary sensor hardcodes ``available``
to ``True``. So every pump entity stays available, Home Assistant bumps
``last_reported`` on each write, and a pump that has physically dropped off the
network looks perfectly fresh to :class:`~.inputs.InputReader` — which prefers
``last_reported``, deliberately. Neither ``unavailable`` nor ``stale`` fires.

Nothing about *freshness* can see that. What closes it is the online signal's
**value**: the same poll that returns stale data writes ``off``. In LAN mode
the offline paths do raise ``UpdateFailed``, entities go unavailable, and
v5.1.3's rule already freezes the learners — so the value-based freeze here is
additive there, not a second mechanism fighting the first.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from . import pump_mode
from .const import (
    CONF_HEAT_PUMP_DEFROST_ENTITY,
    CONF_HEAT_PUMP_FAULT_ENTITY,
    CONF_HEAT_PUMP_MODE_ENTITY,
    CONF_HEAT_PUMP_ONLINE_ENTITY,
)
from .pump_mode import FULL_CAPABILITY, ModeCapability

_LOGGER = logging.getLogger(__name__)

#: Freeze reasons this module can return, in the order they are tested.
#: Reported through ``_learning_frozen`` and published in the diagnostics, so
#: a starved learner names its cause instead of just going quiet.
FREEZE_OFFLINE = "pump_offline"
FREEZE_FAULT = "pump_fault"
FREEZE_COOLING = "pump_cooling"

#: Where :attr:`PumpSignals.mode` came from. ``absent`` covers both "no entity
#: configured" and "configured but never yet readable, with no last good
#: value"; the two are indistinguishable in their effect and reporting them
#: separately would suggest a difference that does not exist.
MODE_SOURCE_LIVE = "live"
MODE_SOURCE_LAST_GOOD = "last_good"
MODE_SOURCE_ABSENT = "absent"
#: The entity is readable and fresh, and reported a word the table does not
#: recognise. Distinct from ``absent`` so the diagnostics can say "your mode
#: entity works, we just do not know what it is telling us" — the one case a
#: user can actually act on, by picking a different entity.
MODE_SOURCE_UNKNOWN = "unrecognised"

#: Read problems that mean "the sensor stopped telling us", as opposed to
#: "the sensor told us something we do not understand". Only these fall back
#: to the last good mode: the pump did not change mode because its sensor
#: went quiet, so continuing to believe the last reading is right.
#:
#: ``unknown_value`` is deliberately NOT here, and that is the whole point.
#: An unrecognised word is a *live* reading, and ``pump_mode``'s contract for
#: it is explicit — "Unknown means full capability, never suppress
#: everything" — because wrongly believing the pump is incapable suppresses a
#: channel on the strength of a word nobody recognised. Routing it to
#: ``last_good`` instead latched that suppression permanently and offered no
#: recovery path: a generic status sensor that says ``Heating`` once and then
#: ``idle`` forever would hold hot water blocked for the life of the install.
_UNREADABLE_PROBLEMS = frozenset(
    {"unavailable", "missing_entity", "stale", "not_configured"}
)


@dataclass(frozen=True)
class PumpSignals:
    """What the four slots say this cycle, already resolved to decisions."""

    #: What the pump can deliver. Never ``None``: an absent or unusable mode
    #: resolves to :data:`pump_mode.FULL_CAPABILITY`, which fails safe toward
    #: "plan normally".
    mode: ModeCapability = FULL_CAPABILITY
    #: Whether :attr:`mode` rests on evidence at all — a mode entity that is
    #: configured, fresh and reporting a word the table recognises, or the
    #: last such reading. False means "we are assuming, not observing", and
    #: every correction in the coordinator that *changes* a measurement is
    #: gated on this rather than on the capability flags, so an install
    #: without a mode entity is bit-identical to v5.1.5.
    mode_observed: bool = False
    #: :data:`MODE_SOURCE_LIVE`, :data:`MODE_SOURCE_LAST_GOOD` or
    #: :data:`MODE_SOURCE_ABSENT`, for the diagnostics.
    mode_source: str = MODE_SOURCE_ABSENT
    #: The raw state string the mode came from, for the diagnostics. The
    #: reference integration publishes the select's *label* ("Heating + DHW"),
    #: not the device enum, so seeing the literal word matters when a mode is
    #: not being recognised.
    mode_text: str | None = None
    #: ``True``/``False`` when the flag was readable this cycle, ``None`` when
    #: there is no evidence either way.
    defrosting: bool | None = None
    online: bool | None = None
    fault: bool | None = None
    #: Why the learners must stand down, or ``None``. Plant-wide: it does not
    #: name a configuration key, because it is not about one sensor being
    #: unreadable — it is about the machine being in a state where every
    #: thermal measurement it produces is misleading.
    freeze_reason: str | None = None

    @property
    def space_heat(self) -> bool:
        """Whether space heating may be planned."""
        return self.mode.space_heat

    @property
    def dhw(self) -> bool:
        """Whether hot water may be planned."""
        return self.mode.dhw

    @property
    def space_blocked(self) -> bool:
        """Whether the plan must not promise space heat.

        Gated on ``mode_observed`` as well as on the capability so that the
        unknown-mode fallback can never suppress: ``FULL_CAPABILITY`` already
        says the pump can do everything, and this is the belt to that braces.
        """
        return self.mode_observed and not self.mode.space_heat

    @property
    def dhw_blocked(self) -> bool:
        """Whether the plan must not promise hot water."""
        return self.mode_observed and not self.mode.dhw

    def as_dict(self) -> dict[str, Any]:
        """The diagnostics view."""
        return {
            "mode": self.mode.label,
            "mode_key": self.mode.key,
            "mode_state": self.mode_text,
            "mode_source": self.mode_source,
            "space_heat_available": self.mode.space_heat,
            "dhw_available": self.mode.dhw,
            "cooling": self.mode.cooling,
            "concurrent_duties": self.mode.concurrent,
            "space_blocked": self.space_blocked,
            "dhw_blocked": self.dhw_blocked,
            "defrosting": self.defrosting,
            "online": self.online,
            "fault": self.fault,
            "freeze_reason": self.freeze_reason,
        }


def read(reader: Any, *, last_good: ModeCapability | None = None) -> PumpSignals:
    """Read all four slots through ``reader`` and resolve them.

    ``reader`` is the cycle's :class:`~.inputs.InputReader`, so every one of
    the four lands in that cycle's :class:`~.inputs.InputHealth` and shows up
    in the diagnostics with its entity id and problem — a mode entity nobody
    can read is *visible*, it just does not act.

    ``last_good`` is the last recognised mode, if one has ever been seen. A
    configured mode entity that goes unreadable falls back to it rather than
    to full capability: the pump did not change mode because its sensor
    stopped reporting, and quietly re-enabling a channel the pump cannot
    serve is precisely the promise this feature exists to stop making. Only
    when nothing was ever seen does it fall back to full capability.
    """
    mode_reading = reader.read_state(
        CONF_HEAT_PUMP_MODE_ENTITY, valid=pump_mode.is_known
    )
    if mode_reading.ok and mode_reading.text:
        capability = pump_mode.capability(mode_reading.text)
        source = MODE_SOURCE_LIVE
        observed = True
    elif mode_reading.problem == "unknown_value":
        # Live, fresh and unrecognised. Full capability, never last_good:
        # see ``_UNREADABLE_PROBLEMS``.
        capability = FULL_CAPABILITY
        source = MODE_SOURCE_UNKNOWN
        observed = False
        _LOGGER.debug(
            "Heat pump mode entity %s reports %r, which names no mode this "
            "release recognises; assuming full capability",
            mode_reading.entity_id,
            mode_reading.text,
        )
    elif (
        last_good is not None
        and mode_reading.entity_id
        and mode_reading.problem in _UNREADABLE_PROBLEMS
    ):
        capability = last_good
        source = MODE_SOURCE_LAST_GOOD
        observed = True
    else:
        capability = FULL_CAPABILITY
        source = MODE_SOURCE_ABSENT
        observed = False

    defrost_reading = reader.read_bool(CONF_HEAT_PUMP_DEFROST_ENTITY)
    online_reading = reader.read_bool(CONF_HEAT_PUMP_ONLINE_ENTITY)
    fault_reading = reader.read_bool(CONF_HEAT_PUMP_FAULT_ENTITY)

    defrosting = defrost_reading.flag if defrost_reading.ok else None
    online = online_reading.flag if online_reading.ok else None
    fault = fault_reading.flag if fault_reading.ok else None

    # Ordered by what explains the most. A pump that is not reachable makes
    # every other reading about it doubtful, so it is named first; a fault
    # likewise explains an odd mode. Only one reason is reported because
    # ``_learning_frozen`` returns one, and the first is the root cause.
    freeze: str | None = None
    if online is False:
        freeze = FREEZE_OFFLINE
    elif fault is True:
        freeze = FREEZE_FAULT
    elif observed and capability.cooling:
        # The whole thermal model assumes heating. An interval that drew power
        # while the house got *colder* is not a noisy heating sample, it is a
        # sign-inverted one: the house heat-loss learner reads the fall as an
        # enormous heat loss, and the COP learner reads electricity spent for
        # negative modelled output. Both persist what they conclude.
        freeze = FREEZE_COOLING

    signals = PumpSignals(
        mode=capability,
        mode_observed=observed,
        mode_source=source,
        mode_text=mode_reading.text,
        defrosting=defrosting,
        online=online,
        fault=fault,
        freeze_reason=freeze,
    )
    if freeze is not None:
        _LOGGER.debug(
            "Heat pump signals freeze learning: %s (mode %s from %s, "
            "online=%s, fault=%s)",
            freeze,
            capability.label,
            source,
            online,
            fault,
        )
    return signals
