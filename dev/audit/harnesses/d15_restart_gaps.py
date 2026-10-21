"""R10-D15-GRADER harness (#2268 arm b): D15.md M1's restart-gap rule over a bundle.

A restart gap is two consecutive ``cycle_rows[].t`` at least three
``optimization_interval`` apart, read from the download's ``config``, else
``const.DEFAULT_OPTIMIZATION_INTERVAL``. Accepts the whole download (HA's
``data`` wrapper and the ``debug`` key are unwrapped) or a bare bundle, such
as ``tools/replay/dbg_bundle_gen.py``'s.

    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/d15_restart_gaps.py --bundle B [--plant SECONDS]

``--plant`` delays every row after the middle one, so the middle spacing
becomes SECONDS: the perturbation. On the synthetic week (30 min cadence)
restart_gaps reads 0 unplanted, 0 at 3600 (one skipped cycle), 1 at 5400 and
1 at 12054 (the owner's upgrade gap). Prints each gap's start, so a finder
dates releases against it with ``git for-each-ref refs/tags``.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta

from heatpump_optimizer import const

GAP_INTERVALS = 3


def unwrap(doc: dict) -> tuple[dict, dict]:
    """(bundle, config): the download's own ``config`` sits beside ``debug``."""
    doc = doc.get("data", doc) if isinstance(doc.get("data"), dict) else doc
    config = doc.get("config") if isinstance(doc.get("config"), dict) else {}
    return (doc["debug"] if isinstance(doc.get("debug"), dict) else doc), config


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--plant", type=float, default=0.0)
    a = ap.parse_args()
    with open(a.bundle, encoding="utf-8") as fh:
        bundle, config = unwrap(json.load(fh))
    named = config.get(const.CONF_OPTIMIZATION_INTERVAL)
    interval_s = float(named if named is not None else const.DEFAULT_OPTIMIZATION_INTERVAL) * 60.0
    stamps = [datetime.fromisoformat(r["t"]) for r in bundle.get("cycle_rows", ())]
    if len(stamps) < 2:
        print(f"RESULT rows={len(stamps)} unit=count")
        print("REFUSED fewer than two cycle rows: no spacing to read", file=sys.stderr)
        return 2
    if a.plant:
        mid = len(stamps) // 2
        shift = timedelta(seconds=a.plant) - (stamps[mid + 1] - stamps[mid])
        stamps = stamps[:mid + 1] + [t + shift for t in stamps[mid + 1:]]
    spacing = [(b - c).total_seconds() for c, b in zip(stamps, stamps[1:])]
    gaps = [(stamps[i], s) for i, s in enumerate(spacing) if s >= GAP_INTERVALS * interval_s]
    print(f"RESULT rows={len(stamps)} unit=count")
    print(f"RESULT interval_s={interval_s:g} unit=s source={'config' if named is not None else 'default'}")
    print(f"RESULT max_spacing_s={max(spacing):g} unit=s")
    print(f"RESULT planted_s={a.plant:g} unit=s")
    print(f"RESULT restart_gaps={len(gaps)} unit=count")
    for start, s in gaps:
        print(f"GAP from={start.isoformat()} seconds={s:g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
