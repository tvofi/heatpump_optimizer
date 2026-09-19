"""Whether a heat-pump device is worth offering the pre-fill for (#1067).

W1067-G7b built the pre-fill page: a device picked on ``modbus_prefill`` has
its entity-registry records resolved into the role map ``modbus_prefill.infer``
reads, through a source table where one proves the model and through
``name_match`` for the roles a table left empty. That page lives in the
options flow, so a user only meets it by going looking. W1067-POST1 offers it
while the integration is being set up instead: the device has just been added,
which is when the suggestion is worth making.

What decides whether a device is worth offering: a device qualifies only when
one of the sources G7b can map resolves it, which is
:func:`device_prefill.resolve_with_fallback`'s own answer -- a source table
that proves the model, or, for a device no table knows, the fuzzy fallback
filling at least :data:`QUALIFYING_MINIMUM` roles. A device nothing resolves
gets no offer, because a prompt that opens an empty page is noise.

**The minimum is measured, not chosen.** It is read off the corpus table
W1067-G7b-3 built and keeps:

    PYTHONPATH=tests/hastub python3 tools/measure_prefill_corpus.py

prints "roles the fallback fills per corpus device (W1067-POST1's table)",
one row per labelled device with the roles its source table resolved and the
roles the fallback then filled. The minimum is the smallest count in that
table's ``fallback`` column *among its hand-shaped rows* -- the devices no
source table reads, whose resolvability is the names' doing alone. The two
generated rows print six and two tabled roles and zero fallback roles while
being fully resolvable, so a zero there is the source table's doing and not
the device being unreadable: that is why this number is never read off the
whole column, and why the rule is stated rather than the count alone.

A device with a source table that resolves it is qualified by that table, not
by this number, which is the other half of the same measurement.

Kept free of Home Assistant imports, like ``device_prefill`` and
``modbus_prefill``: ``config_flow.py`` reads the registries and hands this
module plain records. Nothing here re-derives the matcher -- the resolution
is ``device_prefill``'s own, so the offer and the options page can never
disagree about what a device resolves to.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Final

from . import device_prefill, name_match
from .device_prefill import EntityRecord, Resolution

#: How many roles the fallback must fill on a device no source table proves.
#: Read off ``tools/measure_prefill_corpus.py``'s roles-per-device table as
#: the smallest ``fallback`` count among its hand-shaped rows; the module
#: docstring states the rule and the command. ``tests/features.py`` re-derives
#: it from the corpus on every run, so a corpus that moves takes this with it.
QUALIFYING_MINIMUM: Final = 1


def fallback_roles(resolution: Resolution) -> int:
    """How many of a device's roles came from a name rather than from a table.

    Read off the resolution's own ``source`` labels, so it is the matcher's
    answer and not a second count of the same thing: every role
    :func:`device_prefill.resolve` decided is attributed to a platform, and
    everything else to :data:`name_match.SOURCE`.
    """
    return sum(
        1 for label in resolution.source.values() if label == name_match.SOURCE
    )


def qualifies(
    resolution: Resolution, minimum: int = QUALIFYING_MINIMUM
) -> bool:
    """Whether one device is worth offering the pre-fill page for.

    A source table that resolved any role qualifies the device outright: the
    table is derived from that integration's own published definitions, so
    what it read is proven rather than guessed. A device no table proves is
    read by name alone, and qualifies only when the names fill at least
    ``minimum`` roles -- the measured floor below which a page would offer
    less than the corpus's own smallest hand-shaped device.
    """
    tabled = len(resolution.roles) - fallback_roles(resolution)
    return tabled > 0 or fallback_roles(resolution) >= minimum


def offered(
    devices: Mapping[str, Iterable[EntityRecord]],
    minimum: int = QUALIFYING_MINIMUM,
) -> dict[str, Resolution]:
    """``device_id -> resolution`` for the devices worth offering, id order.

    The whole input of the offer: one device's records per registry device, as
    ``config_flow.py`` reads them. Sorted by device id, so the same registry
    offers the same set in the same order rather than in dict-iteration order,
    and each device is resolved once, through the options page's own resolver.
    """
    found: dict[str, Resolution] = {}
    for device_id in sorted(devices):
        resolution = device_prefill.resolve_with_fallback(devices[device_id])
        if qualifies(resolution, minimum):
            found[device_id] = resolution
    return found
