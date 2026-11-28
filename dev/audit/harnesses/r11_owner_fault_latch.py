#!/usr/bin/env python3
"""R11-OWNER-FAULT-HOLD (#3856): a fault-alarm timeline replayed through the production latch.

Drives ``fault_hold.holding`` minute by minute over a fault-alarm timeline and
prints counts only: no entity id, state word or time of a bundle is printed. A
bundle is a user's private data and is never committed.

Arms (each prints RESULT lines):

  synthetic  24 hours of one-minute control passes with one multi-hour latch
             (03:00-07:30), four sub-minute faults and two few-minute faults
             (3 and 6 minutes). A pass that is not held would actuate (mode,
             set-points, an OFF), so it counts one actuating pass. Printed:
             ``latched_actuating`` (actuating passes past FAULT_HOLD_AFTER of
             the latch, expected 0), ``short_held`` (held passes inside the
             short faults, expected 0) and ``repairs`` (rising edges).
             ``--opt-out`` runs the same timeline with ``fault_hold`` off, the
             null control: it reproduces today's counts, every pass actuating.
  bundle     ``--timeline T``: a JSON list of ``[iso time, state]`` pairs, the
             fault entity's history extracted from a diagnostics bundle or the
             recorder. Printed: ``latches`` (holds that started), ``short_faults``
             (on-spells shorter than FAULT_HOLD_AFTER) and ``short_held``.

Command (repository root):
    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_owner_fault_latch.py synthetic [--opt-out]
    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_owner_fault_latch.py bundle --timeline T
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta, timezone

from harness import FakeEntry, FakeHass, FakeState

from heatpump_optimizer import fault_hold

ENTITY = "binary_sensor.pump_fault"
T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)


def _synthetic() -> list[tuple[datetime, str]]:
    """The 24-hour timeline: (when, state) changes."""
    out = [(T0, "off")]
    spells = [(180, 450)]  # the latch, minutes from 00:00
    spells += [(m, m + 0.5) for m in (60, 600, 900, 1200)]  # sub-minute
    spells += [(720, 723), (1300, 1306)]  # few-minute
    for on, off in sorted(spells):
        out += [(T0 + timedelta(minutes=on), "on"), (T0 + timedelta(minutes=off), "off")]
    return out


def replay(changes: list[tuple[datetime, str]], *, hold: bool = True, step=timedelta(minutes=1)):
    """Per pass: (when, alarm on, held), the latch driven at every ``step``."""
    hass = FakeHass({})
    entry = FakeEntry(entry_id="replay")
    config = {"heat_pump_fault_entity": ENTITY, "fault_hold": hold}
    changes = sorted(changes)
    now, end, i, state, passes = changes[0][0], changes[-1][0] + timedelta(hours=1), 0, None, []
    while now <= end:
        while i < len(changes) and changes[i][0] <= now:
            state = changes[i][1]
            hass.states.set(ENTITY, FakeState(state, last_updated=changes[i][0]))
            i += 1
        passes.append((now, state == "on", fault_hold.holding(entry, hass, config, off=False, now=now)))
        now += step
    return passes, getattr(hass, "issues", [])


def _spells(changes):
    """(on, off) of each on-spell."""
    out, start = [], None
    for when, state in sorted(changes):
        if state == "on" and start is None:
            start = when
        elif state != "on" and start is not None:
            out.append((start, when))
            start = None
    return out


def _counts(changes, passes):
    after = fault_hold.FAULT_HOLD_AFTER
    spells = _spells(changes)
    short = [(a, b) for a, b in spells if b - a < after]
    long_ = [(a, b) for a, b in spells if b - a >= after]
    inside = lambda t, ss, lead=timedelta(0): any(a + lead <= t < b for a, b in ss)  # noqa: E731
    return {
        "latched_actuating": sum(1 for t, _on, held in passes if inside(t, long_, after) and not held),
        "short_held": sum(1 for t, _on, held in passes if inside(t, short) and held),
        "short_faults": len(short),
        "latches": sum(1 for (_t, _o, h), (_t2, _o2, h2) in zip(passes, passes[1:]) if h2 and not h),
    }


def main(argv: list[str]) -> int:
    logging.disable(logging.CRITICAL)  # the latch's warning names the entity
    if argv[:1] == ["synthetic"]:
        changes = _synthetic()
        passes, issues = replay(changes, hold="--opt-out" not in argv)
        counts = _counts(changes, passes)
        print(f"RESULT latched_actuating={counts['latched_actuating']}")
        print(f"RESULT short_held={counts['short_held']}")
        print(f"RESULT short_faults={counts['short_faults']}")
        print(f"RESULT repairs={counts['latches']}")
        print(f"RESULT actuating_passes={sum(1 for _t, _o, h in passes if not h)}")
        return 0
    if argv[:1] == ["bundle"] and "--timeline" in argv:
        raw = json.loads(open(argv[argv.index("--timeline") + 1], encoding="utf-8").read())
        changes = [(datetime.fromisoformat(t).astimezone(timezone.utc), str(s)) for t, s in raw]
        passes, _issues = replay(changes)
        counts = _counts(changes, passes)
        for key in ("latches", "short_faults", "short_held"):
            print(f"RESULT {key}={counts[key]}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
