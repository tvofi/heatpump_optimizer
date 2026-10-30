#!/usr/bin/env python3
"""R10-STORE-RACES (#2248, #2674): the setup-refresh store-read census, on any tree.

Runs the census block of a features.py (default: this tree's) against the
production code of the tree at the cwd, so the census that landed can measure
a tree from before it (a merge base, a mutant) without a second copy of it.

Metric:   per store read the constructor spawns, held alone across the setup
          refresh: the load-assigned state that differs from the serial order
          (read first). census_lost_total = stores with any such state.
Count key: one arm per held store key; the state compared is every coordinator
          attribute or per-coordinator side table a load assigns (diffed, not
          listed), less ``*_cache``/``*_memo`` memo fields.
Command:  PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_store_races_census.py \\
              [--features PATH]
          from the root of the tree under test.
Null control: the serial arm itself (the reads land before the refresh); and
          census_unfenced_differs, every read held at once with every store's
          async_wait_for_read removed, which must read non-empty, or the window
          reaches no writer and a 0 above is blind.
Perturbation: the tree under test -- delete one writer's fence and the store
          it reads must appear in census_lost.
Expected at 88c6ad5bb (origin/main): census_lost_total=0, unfenced non-empty.
At c78df2b86 (before #2817): census_lost names the price-model and the
legionella reads.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "custom_components"))

import numpy as np  # noqa: E402,F401  (the block's namespace)
from harness import FakeEntry, FakeHass, FakeState  # noqa: E402,F401
from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402,F401

START = "# #2248's class (N-restore-race) over the setup refresh"
END = 'f"unfenced differs in {_src_differ[\'unfenced\']}",\n)\n'


class _Checks:
    def check(self, name, ok, detail=""):
        print(f"CHECK {'ok' if ok else 'FAIL'} {name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default=str(ROOT / "tests" / "features.py"))
    src = Path(ap.parse_args().features).read_text(encoding="utf-8")
    block = src[src.index(START):src.index(END) + len(END)]
    ns = {**globals(), "R": _Checks(), "asyncio": asyncio, "datetime": datetime,
          "timedelta": timedelta, "timezone": timezone}
    exec(compile(block, "census", "exec"), ns)
    lost = ns["_src_differ"]["fenced"]
    print(f"RESULT census_stores_held={len(ns['_src_held'])} count")
    print(f"RESULT census_assigned={','.join(ns['_src_assigned'])}")
    print(f"RESULT census_lost_total={len(lost)} of {len(ns['_src_held'])}")
    for key, state in sorted(lost.items()):
        print(f"RESULT census_lost {key} -> {','.join(state)}")
    print(f"RESULT census_unfenced_differs={','.join(ns['_src_differ']['unfenced']) or 'none'}")


main()
