#!/usr/bin/env python3
"""D15-s2 enumerator, D15.M5: the timeline replay's universe, one line per cycle.

Prints ``cycle <UTC instant>`` for every cycle ``tests/replay.py:run_fixture``
steps through the bundle's replay half (window start to end, the entry's
``optimization_interval``, walked in UTC as run_fixture walks it), then one
``seeding <store name>`` line per store document ``debug_replay.seed_stores``
would seed. Prints nothing but the header line when the replay half is empty.

    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/rounds/round11/D15/s2/m5_enumerate.py --bundle B

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Privacy: instants and store
names only.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path.cwd()
for _p in (ROOT / "tests" / "hastub", ROOT / "custom_components", ROOT / "tools" / "replay"):
    sys.path.insert(0, str(_p))

import debug_ingest  # noqa: E402
from heatpump_optimizer import const  # noqa: E402
from heatpump_optimizer import store as store_mod  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True, type=Path)
    a = ap.parse_args(argv)
    bundle = debug_ingest.load_bundle(a.bundle)
    doc = bundle.get("replay") or {}
    if not doc.get("window"):
        return 0
    config = {**(doc["entry"].get("data") or {}), **(doc["entry"].get("options") or {})}
    step = timedelta(minutes=int(config.get(const.CONF_OPTIMIZATION_INTERVAL,
                                            const.DEFAULT_OPTIMIZATION_INTERVAL)))
    t = datetime.fromisoformat(doc["window"]["start"]).astimezone(timezone.utc)
    end = datetime.fromisoformat(doc["window"]["end"])
    while t < end:
        print(f"cycle {t.isoformat()}")
        t += step
    for key in sorted(bundle.get("stores") or {}):
        name = store_mod.store_name(key)
        if name is not None:
            print(f"seeding {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
