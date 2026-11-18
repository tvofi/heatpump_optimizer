"""When a solve runs: the cycle's one in-flight guard and its budgets.

The coordinator keeps the solve paths; this module owns the questions every
one of them asks before it starts, in a per-coordinator side table
(``boost.py``'s and ``whatif.py``'s discipline), so the coordinator class
holds no state it never computes with.

THE MAIN SOLVE. One in flight. A request that lands while it runs is recorded
as ONE re-run the in-flight solve's ``finally`` honours (#1754), so an input
changed mid-solve is actuated in the cycle that is running, not dropped until
the next. A request that lands while a refresh is fetching or actuating but
not solving is recorded as ONE trailing refresh, scheduled when that refresh
ends: Home Assistant's debouncer drops a call made while it executes, which
left a write made then unplanned until the next interval (D1-s1-03).

THE BACKGROUND BUDGET. One background what-if (the fuse advisor, a price
tile) per main solve, so a cycle never stacks them (D9-s1-02). The debug
collection's finalize self-test is exempt: it runs once per finalize, never
per cycle, and exists to answer.

THE USER'S SLOT. One user what-if solving and the newest one waiting: an ask
overtaken by a newer one while it waits is answered from the held answer,
unsolved (D9-s1-03), so a burst of K asks solves at most two.

THE RUN-NOW PATH. The Optimize Now button and the ``run_optimization``
action are one refresh, fetch to publish (D17-s3-01): ``async_optimize_now``.
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any
from weakref import WeakKeyDictionary

from .const import MODE_AUTO, MODE_ECONOMY


@dataclass
class SolveGate:
    """One coordinator's answer to "may this solve start now"."""

    #: A main solve is in flight.
    solving: bool = False
    #: A request landed during that solve; it re-runs once (#1754).
    rerun: bool = False
    #: A request landed during a refresh that was not solving; one refresh follows it.
    trailing: bool = False
    #: The current main solve's one background what-if has been spent.
    background_taken: bool = False
    #: The last refresh's solve answer: None ran, else its reason code.
    reason: str | None = None
    #: A user what-if is solving.
    user_running: bool = False
    #: The newest waiting user ask's ticket; a waiter holding an older one is superseded.
    user_waiting: int = 0
    #: Set when the user what-if in flight ends.
    user_freed: asyncio.Event = field(default_factory=asyncio.Event, repr=False)


_GATES: WeakKeyDictionary[Any, SolveGate] = WeakKeyDictionary()


def gate_for(owner: Any) -> SolveGate:
    """``owner``'s gate, created on first use."""
    return _GATES.setdefault(owner, SolveGate())


def absorb_request(gate: SolveGate, refreshing: bool) -> bool:
    """Whether a refresh request is absorbed by work already running.

    Solving: the in-flight solve re-runs once. Refreshing without a solve:
    one refresh trails it. Otherwise False, and the caller requests as usual.
    """
    if gate.solving:
        gate.rerun = True
        return True
    if refreshing:
        gate.trailing = True
        return True
    return False


def begin_solve(gate: SolveGate) -> bool:
    """Start a main solve; False, with a re-run recorded, when one is in flight.

    A started solve opens a fresh background budget.
    """
    if absorb_request(gate, False):
        return False
    gate.solving = True
    gate.background_taken = False
    return True


def end_solve(gate: SolveGate) -> bool:
    """End the main solve; whether a re-run was recorded during it (taken)."""
    gate.solving = False
    rerun, gate.rerun = gate.rerun, False
    return rerun


def take_trailing(gate: SolveGate) -> bool:
    """Whether a refresh was requested during the one ending (taken)."""
    trailing, gate.trailing = gate.trailing, False
    return trailing


def admit_background(gate: SolveGate) -> bool:
    """Whether a background what-if may run: once per main solve.

    Asked before the caller chooses its work, so a denied price tile moves no rotation.
    """
    if gate.background_taken:
        return False
    gate.background_taken = True
    return True


@asynccontextmanager
async def user_slot(gate: SolveGate, user: bool = True) -> AsyncIterator[bool]:
    """Wait for the user what-if in flight; yield whether this ask may solve.

    False when a newer ask arrived while this one waited: the newest supersedes.
    The slot is held while the body runs and freed on any exit. A background
    caller (``user`` False) neither waits nor holds it (#1753): yields True.
    """
    if not user:
        yield True
        return
    freed = gate.user_freed
    gate.user_waiting += 1
    ticket = gate.user_waiting
    while gate.user_running:
        freed.clear()
        await freed.wait()
    if ticket != gate.user_waiting:
        yield False
        return
    gate.user_running = True
    try:
        yield True
    finally:
        gate.user_running = False
        freed.set()


async def async_optimize_now(coord: Any) -> str | None:
    """Optimize Now and ``run_optimization``: one fetch-solve-actuate-publish refresh (D17-s3-01).

    A fixed mode's refresh solves nothing, so its private plan is solved first.
    None when the solve ran, else why not: the solve's reason, or a failed
    refresh's (``"no_prices"`` when no published price covers now).
    """
    gate = gate_for(coord)
    gate.reason = None
    if coord.mode not in (MODE_AUTO, MODE_ECONOMY):
        gate.reason = await coord.async_run_optimization()
    await coord.async_refresh()
    if coord.last_update_success:
        return gate.reason
    key = getattr(coord.last_exception, "translation_key", None)
    return "no_prices" if key == "tibber_fetch_failed" else "solve_failed"
