#!/usr/bin/env python3
"""Print every a3 architecture metric's headline value as JSON.

    python3 run_all.py [ROOT] [--details] [--timing]

ROOT is a repository checkout (default: the current directory); the package
measured is ROOT/custom_components/heatpump_optimizer. Pure static, stdlib
only, deterministic. The package is parsed once and shared across metrics.
Each metric module is also runnable on its own: ``python3 metrics/<m>.py ROOT``.

P10 (loop kernel count) is deliberately absent: it is a runtime measurement
(a solve has to run), not a property the AST can see.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "metrics"))

METRICS = (
    "hub_solve_writes",
    "shared_inplace_writes",
    "private_reach",
    "untyped_payload_keys",
    "xmodule_duplication",
    "import_cycles",
    "public_surface",
    "dead_by_reachability",
    "family_splits",
)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else ".").resolve()
    t0 = time.perf_counter()
    out: dict = {}
    full: dict = {}
    timing: dict = {}
    for name in METRICS:
        mod = __import__(name)
        t = time.perf_counter()
        res = mod.measure(root)
        timing[name] = round(time.perf_counter() - t, 3)
        out[name] = res["value"]
        full[name] = res
    if "--details" in argv:
        print(json.dumps(full, indent=1, ensure_ascii=False))
    else:
        print(json.dumps(out, indent=1))
    if "--timing" in argv:
        timing["total"] = round(time.perf_counter() - t0, 3)
        print(json.dumps({"timing_s": timing}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
