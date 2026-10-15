#!/usr/bin/env python3
"""Probe (N-shared-config sweep, seam C away.py:349-352): the spawned away
restore overwrites a user override written while its store load is in flight.

away.restore_override (spawned by boost.restore_session from the
coordinator's construction, not awaited by setup) awaits load_mapping, then
apply_override_payload writes the STORED payload into the live AwayState --
unconditionally. HeatPumpOptimizerCoordinator.async_set_away writes the same
AwayState fields on the loop. A set_away landing inside the load await is
lost, and its own persist then saves the restored (old) value.

Metric: lost = 1 when, after both finish, state.override_active is not the
user's True. Cells: midload (set_away inside the load await) and null (the
same set_away after the restore finished, expected 0).
Perturbation (--perturb, in memory): apply_override_payload skips when the
state was written since the restore started (compare by identity of a
generation counter) -> lost 0.
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-shared-config/probe_away_restore.py [--perturb]
Expected at 9355f107d: RESULT lost_midload=1, lost_null=0; --perturb lost_midload=0.
"""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


ROOT = repo_root(__file__)
sys.path[:0] = [str(ROOT / "tests" / "hastub"), str(ROOT / "custom_components")]

from heatpump_optimizer import away as away_mode  # noqa: E402
from heatpump_optimizer import coordinator as cm  # noqa: E402

PERTURB = "--perturb" in sys.argv
STORED = {"active": False, "return_time": None, "migrated_helpers": True}


async def cell(midload: bool) -> int:
    gate = asyncio.Event()
    entered = asyncio.Event()

    async def load_mapping(_store, _what):
        entered.set()
        await gate.wait()
        return dict(STORED)

    saved = []

    async def persist_override(_coord, st):
        saved.append(st.override_active)

    away_mode.load_mapping = load_mapping
    away_mode.persist_override = persist_override
    state = away_mode.AwayState()
    gen = {"n": 0}
    if PERTURB:
        orig_apply = away_mode.apply_override_payload
        start = {}

        def guarded(st, payload):
            if gen["n"] != start.get("n", 0):
                return
            orig_apply(st, payload)
        away_mode.apply_override_payload = guarded
        start["n"] = gen["n"]
    coord = SimpleNamespace(_away_state=state, hass=None, entry=SimpleNamespace(entry_id="e"))

    async def set_away():
        gen["n"] += 1
        await cm.HeatPumpOptimizerCoordinator.async_set_away(coord, active=True, refresh=False)

    restore = asyncio.ensure_future(away_mode.restore_override(coord, state, {}, lambda _e: (None, {})))
    await entered.wait()
    if midload:
        await set_away()
    gate.set()
    await restore
    if not midload:
        await set_away()
    if PERTURB:
        away_mode.apply_override_payload = orig_apply
    return int(state.override_active is not True)


async def main():
    mid = await cell(True)
    null = await cell(False)
    print(f"RESULT lost_midload={mid} count")
    print(f"RESULT lost_null={null} count")


asyncio.run(main())
