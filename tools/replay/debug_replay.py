#!/usr/bin/env python3
"""Replay a debugger bundle through ``tests/replay.py:run_fixture``.

``run_fixture`` constructs the coordinator against ``FakeEntry``'s default
id ``test_entry`` and ``FakeHass.async_create_task`` closes spawned store
loads without running them. This driver remaps the bundle's store documents
onto that id, writes them into the HA-stub ``Store._DISK``, and runs those
loads so the tick starts from learned state. It does not edit
``tests/replay.py``.

    PYTHONPATH=tests/hastub:tests python3 tools/replay/debug_replay.py --bundle B.json
    PYTHONPATH=tests/hastub:tests python3 tools/replay/debug_replay.py --fixture F.json --start ISO --end ISO
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components", HERE):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

import debug_ingest  # noqa: E402

DOMAIN = "heatpump_optimizer"
REPLAY_ENTRY_ID = "test_entry"  # tests/harness.py FakeEntry default
LOAD_NAMES = frozenset({
    "async_load_profile", "async_load_draws", "async_load",
    "_async_load_thermal_learning", "_async_load_price_model",
    "_async_load_accuracy", "_async_load_energy_totals",
    "_async_load_ledger", "_async_load_snapshots",
    "_async_load_manual_plan", "restore_session",
})
# The pre-study's single agreement offender: first-day 23:00 UTC on the
# synthetic week (debugger-prestudy.md section 5).
OFFENDER_INSTANT = "2026-01-15T23:00:00+00:00"


def seed_stores(stores: dict, *, entry_id: str = REPLAY_ENTRY_ID) -> list[str]:
    """Write bundle stores onto ``Store._DISK`` under ``entry_id``'s keys."""
    from heatpump_optimizer import store as store_mod
    from homeassistant.helpers import storage as stub
    written: list[str] = []
    for key, document in stores.items():
        suffix = debug_ingest.domain_suffix(key, store_mod.DOMAINS)
        if suffix is None:
            continue
        dest = f"{DOMAIN}_{entry_id}_{suffix}"
        stub._DISK[dest] = json.dumps(document)
        written.append(dest)
    return written


def enable_store_loads() -> object:
    """Run spawned store-load coroutines that ``FakeHass`` would close."""
    import harness
    original = harness.FakeHass.async_create_task

    def async_create_task(self, coro):
        name = getattr(getattr(coro, "cr_code", None), "co_name", "")
        if name in LOAD_NAMES:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(coro)
                return None
            return asyncio.create_task(coro)
        return original(self, coro)

    harness.FakeHass.async_create_task = async_create_task
    return original


def restore_store_loads(original) -> None:
    import harness
    harness.FakeHass.async_create_task = original


def trim_replay(replay_doc: dict, start: datetime, end: datetime,
                pad: timedelta = timedelta(hours=6)) -> dict:
    """A windowed copy of an ``hpo-replay/1`` document (the smoke's tail-day)."""
    out = copy.deepcopy(replay_doc)
    out["window"] = {"start": start.isoformat(), "end": end.isoformat()}
    keep_from = start - pad
    for entity_id, rows in list((out.get("states") or {}).items()):
        kept = [r for r in rows if datetime.fromisoformat(r[0]) >= keep_from]
        if kept:
            out["states"][entity_id] = kept
        else:
            del out["states"][entity_id]
    return out


def run_seeded(replay_doc: dict, stores: dict | None = None,
               step_minutes: int | None = None) -> dict:
    import replay as replay_mod
    original = enable_store_loads() if stores else None
    try:
        if stores:
            seed_stores(stores)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(json.dumps(replay_doc))
            return replay_mod.run_fixture(path, step_minutes, None)
    finally:
        if original is not None:
            restore_store_loads(original)


def offender_window(replay_doc: dict, instant: str = OFFENDER_INSTANT,
                    hours: float = 2.0) -> dict:
    at = datetime.fromisoformat(instant)
    half = timedelta(hours=hours / 2)
    return trim_replay(replay_doc, at - half, at + half)


def gate_checks() -> list[tuple[str, bool, str]]:
    from heatpump_optimizer import store as store_mod
    from homeassistant.helpers import storage as stub
    before = dict(stub._DISK)
    stores = {
        "heatpump_optimizer_foreign_accuracy": {"accuracy": {"samples": []}},
        "heatpump_optimizer_foreign_energy": {"total_energy_kwh": 7.5},
        "not_a_store": {"x": 1},
        "heatpump_optimizer_foreign_nope": {"x": 1},
    }
    written = seed_stores(stores)
    dest_acc = f"{DOMAIN}_{REPLAY_ENTRY_ID}_accuracy"
    dest_en = f"{DOMAIN}_{REPLAY_ENTRY_ID}_energy"
    loaded = json.loads(stub._DISK.get(dest_en, "{}"))
    undeclared = debug_ingest.domain_suffix(
        "heatpump_optimizer_foreign_nope", store_mod.DOMAINS)
    replay = json.loads(
        (ROOT / "tests" / "replay" / "synthetic-dhw-only.json").read_text())
    start = datetime.fromisoformat(replay["window"]["start"])
    trimmed = trim_replay(replay, start, start + timedelta(hours=2))
    stub._DISK.clear()
    stub._DISK.update(before)
    return [
        ("debug replay: store keys remap onto FakeEntry's test_entry",
         dest_acc in written and dest_en in written and "not_a_store" not in written,
         f"written={written}"),
        ("debug replay: seeded energy document is on the stub disk",
         loaded.get("total_energy_kwh") == 7.5, f"loaded={loaded}"),
        ("debug replay: a key outside DOMAINS is not seeded",
         undeclared is None, f"suffix={undeclared!r}"),
        ("debug replay: trim_replay shortens the window and keeps states",
         trimmed["window"]["end"] != replay["window"]["end"]
         and bool(trimmed.get("states")),
         f"end={trimmed['window']['end']} n={len(trimmed.get('states') or {})}"),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--start", help="inclusive window start (ISO)")
    parser.add_argument("--end", help="exclusive window end (ISO)")
    parser.add_argument("--offender", action="store_true",
                        help="trim around the synthetic-week agreement instant")
    parser.add_argument("--step-minutes", type=int)
    args = parser.parse_args(argv)
    stores: dict = {}
    if args.bundle:
        bundle = debug_ingest.load_bundle(args.bundle)
        replay_doc = bundle.get("replay") or {}
        stores = bundle.get("stores") or {}
    elif args.fixture:
        replay_doc = json.loads(args.fixture.read_text())
    else:
        parser.error("pass --bundle or --fixture")
    if args.offender:
        replay_doc = offender_window(replay_doc)
    elif args.start or args.end:
        start = datetime.fromisoformat(args.start or replay_doc["window"]["start"])
        end = datetime.fromisoformat(args.end or replay_doc["window"]["end"])
        replay_doc = trim_replay(replay_doc, start, end)
    verdict = run_seeded(replay_doc, stores or None, args.step_minutes)
    counts = verdict.get("counts") or {}
    print(f"RESULT cycles={verdict.get('cycles')} unit=count")
    for name in ("finite", "unit", "no_default", "agreement", "cycle"):
        print(f"RESULT {name}={counts.get(name, 0)} unit=count")
    offenders = (verdict.get("results") or {}).get("agreement") or []
    for line in offenders[:8]:
        print(f"RESULT agreement_line={line}")
    print(f"RESULT smoke_verdict={'pass' if not any(counts.get(k) for k in ('finite', 'unit', 'no_default', 'cycle')) else 'fail'} unit=verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
