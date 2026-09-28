"""C1: the worker-fallback streak (hass.data[_WORKER_FALLBACK_STREAK]) and
cause latch (module global _WORKER_FALLBACK_CAUSE) are shared by every config
entry on one hass. Does entry B's successful process solve reset entry A's
streak -- so A's #783 cap (WORKER_FALLBACK_CAP consecutive fallbacks ->
stop holding the GIL, keep the last plan) never engages -- and flap the
repair issue?

Drives the REAL coordinator._await_optimize (unpatched) with the process
transport and the in-process solver replaced by recorders:
  _await_process      raises ProcessWorkerUnavailable for entry A's job
                      (a job-specific transport failure, e.g. A's optimizer
                      does not pickle) and returns for entry B's;
  optimize_in_process returns a marker (the GIL-holding fallback solve).
One FakeHass, the tests/hastub issue registry (hass.issues).
Arms: probe = A and B interleaved (A,B,A,B...), null = A alone.
Extra arm: both entries failing (entry-agnostic failure) -> how many
intervals until the cap.
"""
import asyncio
import sys

sys.argv = [sys.argv[0]]
import logging
logging.disable(logging.CRITICAL)
from harness import FakeHass  # noqa: E402
from homeassistant.exceptions import HomeAssistantError  # noqa: E402
from heatpump_optimizer import coordinator as cmod  # noqa: E402

FAILING = set()
INPROC = []


async def fake_process(hass, fn, optimizer, state, positional, keywords):
    if optimizer in FAILING:
        raise cmod.ProcessWorkerUnavailable(f"cannot pickle job for entry {optimizer}")
    return f"process-solve[{optimizer}]"


def fake_inproc(optimizer, state, positional, keywords):
    INPROC.append(optimizer)
    return f"inprocess-solve[{optimizer}]"


cmod._await_process = fake_process
cmod.optimize_in_process = fake_inproc


def reset():
    cmod._WORKER_FALLBACK_CAUSE = None
    INPROC.clear()


async def solve(hass, entry):
    try:
        r = await cmod._await_optimize(hass, entry, None)
        outcome = "inproc(GIL)" if r.startswith("inprocess") else "process"
    except Exception as err:  # UpdateFailed at the cap
        outcome = f"CAP:{type(err).__name__}"
    issue = any(i[1] == "solve_worker_fallback" for i in getattr(hass, "issues", []))
    return outcome, cmod._worker_fallback_streak(hass), issue


async def run(order, failing):
    reset()
    FAILING.clear()
    FAILING.update(failing)
    hass = FakeHass()
    hass.issues = []
    rows = []
    created = deleted = 0
    was = False
    for i, e in enumerate(order):
        outcome, streak, issue = await solve(hass, e)
        if issue and not was:
            created += 1
        if was and not issue:
            deleted += 1
        was = issue
        rows.append(f"{e}:{outcome}/streak={streak}/issue={'Y' if issue else 'n'}")
    a_inproc = sum(1 for x in INPROC if x == "A")
    a_capped = sum(1 for r in rows if r.startswith("A:CAP"))
    return rows, a_inproc, a_capped, created, deleted


async def main():
    print(f"WORKER_FALLBACK_CAP = {cmod.WORKER_FALLBACK_CAP}\n")
    arms = [
        ("probe: A(fails) & B(ok) interleaved, 8 intervals", ["A", "B"] * 8, {"A"}),
        ("null:  A(fails) alone, 8 intervals", ["A"] * 8, {"A"}),
        ("extra: A & B both fail, interleaved, 4 intervals", ["A", "B"] * 4, {"A", "B"}),
        ("extra-null: A fails alone, 4 intervals", ["A"] * 4, {"A"}),
    ]
    for name, order, failing in arms:
        rows, a_inproc, a_capped, created, deleted = await run(order, failing)
        print(f"== {name}")
        for i in range(0, len(rows), 4):
            print("   " + "  ".join(r.ljust(34) for r in rows[i:i + 4]))
        print(f"   -> A in-process (GIL) solves: {a_inproc}; A cycles refused at cap: {a_capped}; "
              f"issue created {created}x, deleted {deleted}x\n")


asyncio.run(main())
