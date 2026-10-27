#!/usr/bin/env python3
"""R2 fix-review control (REVIEWER-BUILT): every value the store admits is
unchanged by 4522d46b0/6d526cfdc.

CLAIM UNDER TEST (fix1 body): "Every value the store admits is unchanged --
_clean_month already drops a bool, a non-finite or a past-double leaf on load."

`_clean_month` admits a meta entry only as {"sum": finite float, "count":
int >= 1}. This prints coverage_factor for a grid over exactly that admitted
domain; run it at both ends and diff the outputs. An empty diff is the
control; any differing cell is a value the fix moved.

    python3 -I admitted_grid.py <TREE_ROOT> <LABEL>
"""
import sys
from datetime import datetime

root, label = sys.argv[1], sys.argv[2]
sys.path.insert(0, root + "/tests/hastub")
sys.path.insert(0, root + "/tests")
sys.path.insert(0, root + "/custom_components")

from heatpump_optimizer.ledger import (  # noqa: E402
    SPOT_PRICE_META, SETTLED_HOURS_META, coverage_factor,
)

NOW = datetime(2026, 2, 10, 15, 0)
SUMS = (0.0, 0.001, 0.1, 1.0, 23.9, 24.0, 100.0, 671.9, 672.0, 10000.0)
COUNTS = (1, 2, 24, 100)
SPOT_COUNTS = (0, 1, 24, 100, 240)
for s in SUMS:
    for c in COUNTS:
        for sc in SPOT_COUNTS:
            meta = {SETTLED_HOURS_META: {"sum": s, "count": c},
                    SPOT_PRICE_META: {"sum": float(sc), "count": sc}}
            got = coverage_factor(meta, NOW)
            print(f"RESULT {label} sum={s!r} count={c} spot_count={sc} -> {got!r}")
print(f"RESULT {label} cells={len(SUMS)*len(COUNTS)*len(SPOT_COUNTS)} count")
