"""Stand-in for ``homeassistant.components.recorder.history``'s one call here.

``get_significant_states`` over states a test records with ``record(hass,
entity_id, states)``: each a ``State``-shaped object (``state``,
``attributes``, ``last_updated``, ``last_reported``), oldest first. Upstream
reads the database; what is kept is its window rule, read at the 2025.2.0
floor (``history/modern.py``): every state updated after ``start_time`` and
before ``end_time``, and, with ``include_start_time_state``, the last one
updated before ``start_time``, which upstream returns stamped AT
``start_time`` -- its start-state query selects ``literal(0)`` as
``last_updated_ts`` and ``LazyState`` falls back to ``start_time_ts``, as
``last_reported`` then falls back to that. ``significant_changes_only`` is
ignored: every recorded state is a change.
"""
from __future__ import annotations

import copy
from datetime import datetime
from typing import Any

_RECORDED = "_stub_recorder_history"


def record(hass: Any, entity_id: str, states: list[Any]) -> None:
    hass.data.setdefault(_RECORDED, {})[entity_id] = list(states)


def get_significant_states(
    hass: Any,
    start_time: datetime,
    end_time: datetime | None = None,
    entity_ids: list[str] | None = None,
    filters: Any = None,
    include_start_time_state: bool = True,
    significant_changes_only: bool = True,
    minimal_response: bool = False,
    no_attributes: bool = False,
    compressed_state_format: bool = False,
) -> dict[str, list[Any]]:
    out: dict[str, list[Any]] = {}
    for entity_id in entity_ids or ():
        states = hass.data.get(_RECORDED, {}).get(entity_id, [])
        rows = [s for s in states if s.last_updated > start_time
                and (end_time is None or s.last_updated < end_time)]
        before = [s for s in states if s.last_updated < start_time]
        if include_start_time_state and before:
            first = copy.copy(before[-1])
            first.last_updated = first.last_reported = start_time
            rows.insert(0, first)
        if rows:
            out[entity_id] = rows
    return out
