#!/usr/bin/env python3
"""Price R9-DBG-2's shipped self-tests on the pre-study's synthetic week (#1940).

The R9-DBG-0 pre-study (section 4) priced each self-test from its prototype
and put the whole set inside a 15-minute budget. This drives the shipped path
-- ``DebugCollector.finalize`` and the self-tests it starts -- over that
study's week bundle (``runs/week/bundle.json.gz`` on ``handoff/r9-dbg-0``):
its cycle rows become the collector's ring, its store documents are written
where the collector reads them, and its accuracy store seeds the live
tracker. It prints each self-test's wall time, then the bundle's size against
``INLINE_CAP_BYTES``.

What it does not price: the solver smoke's solve. ``async_simulate`` needs a
coordinator with a live plan, which this harness does not build, so the
stand-in answers at once and the row reads as the orchestration's own cost.
The pre-study priced the solve itself (``reference_solve``, 20.2 ms).

    git show origin/handoff/r9-dbg-0:tools/audit/round9/prestudy/runs/week/bundle.json.gz > week.json.gz
    PYTHONPATH=tests/hastub python3 tools/audit/harnesses/r9_dbg2_selftest_price.py --bundle week.json.gz

RESULT lines: ``selftest_<name>_ms``, ``selftest_total_ms``, ``bundle_bytes``,
``bundle_inline`` (1 or 0). Perturbation: ``--repeat N`` repeats the week's
rows N times, a ring N weeks long; ``--repeat 60`` passes the inline cap.
Null control: at the merge base ``8d7903e6`` the collector has no self-tests,
and the harness prints ``RESULT selftests=absent``.
"""
from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for _p in (ROOT / "tests" / "hastub", ROOT / "tests", ROOT / "custom_components"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from harness import FakeHass  # noqa: E402
from heatpump_optimizer import debugger  # noqa: E402
from heatpump_optimizer.accuracy import AccuracyTracker  # noqa: E402
from heatpump_optimizer.store import _store_name  # noqa: E402

ENTRY = "price"


class _Coordinator:
    """What the self-tests read from a coordinator, seeded from the bundle."""

    def __init__(self, bundle: dict) -> None:
        accuracy = next((doc for key, doc in bundle["stores"].items()
                         if _store_name(key) == "accuracy"), {})
        self.accuracy = AccuracyTracker.from_dict(accuracy.get("accuracy"))
        snapshots = bundle.get("payload_snapshots") or []
        self.data = snapshots[-1]["data"] if snapshots else None
        self.integration_version = "price"

    async def async_simulate(self, overrides, *, limited=True, base=None):
        return {"error": "not priced by this harness", "rate_limited": False}


async def _price(bundle: dict, folder: Path, repeat: int) -> int:
    storage = folder / ".storage"
    storage.mkdir()
    for key, doc in bundle["stores"].items():
        name = _store_name(key)
        if name:
            (storage / f"heatpump_optimizer_{ENTRY}_{name}").write_text(
                json.dumps({"version": 1, "data": doc}), encoding="utf-8")
    hass = FakeHass()
    hass.config.path = lambda *parts: str(Path(folder, *parts))
    pending: list = []
    collector = debugger.DebugCollector(hass, ENTRY, pending.append)
    # A stored row carries no null field: ``cycle_row`` omits them.
    rows = [{k: v for k, v in row.items() if v is not None} for row in bundle["cycle_rows"]]
    collector.rows = rows * repeat
    collector.started_at = datetime.fromisoformat(rows[0]["t"])
    coordinator = _Coordinator(bundle)
    if not hasattr(debugger, "run_self_tests"):
        print("RESULT selftests=absent")
        return 0
    collector.finalize(coordinator)
    for coro in pending:
        await coro
    tests = collector.self_tests or {}
    total = 0.0
    for name, outcome in tests.items():
        total += outcome.get("ms", 0.0)
        state = "error=" + outcome["error"] if "error" in outcome else "ok"
        print(f"RESULT selftest_{name}_ms={outcome.get('ms')} ms  # {state}")
    print(f"RESULT selftest_total_ms={round(total, 1)} ms  # budget "
          f"{debugger.SELF_TEST_BUDGET.total_seconds() * 1000:.0f} ms")
    whole = await collector.async_bundle(coordinator)
    size = len(debugger._dumps(whole).encode())
    shown = debugger.capped(whole, f"heatpump_optimizer_{ENTRY}_debug")
    print(f"RESULT bundle_bytes={size} B  # cap {debugger.INLINE_CAP_BYTES} B")
    print(f"RESULT bundle_inline={0 if shown.get('inline') is False else 1} flag")
    return 0 if len(tests) == 5 and not any("error" in t for k, t in tests.items()
                                            if k != "solver") else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args(argv)
    opener = gzip.open if args.bundle.suffix == ".gz" else open
    with opener(args.bundle, "rt", encoding="utf-8") as handle:
        bundle = json.load(handle)
    with tempfile.TemporaryDirectory() as tmp:
        return asyncio.run(_price(bundle, Path(tmp), args.repeat))


if __name__ == "__main__":
    sys.exit(main())
