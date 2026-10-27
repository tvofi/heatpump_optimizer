#!/usr/bin/env python3
"""R2 fix-review harness (REVIEWER-BUILT, not the finder's): coverage_factor's
totality over a hostile month meta.

WHY IT EXISTS. #2745's two round-2 commits (4522d46b0, 6d526cfdc) claim
``coverage_factor`` falls back to ``pro_rata_factor`` for a meta entry that is
not a dict or whose ``sum``/``count`` is missing or not finite, where the old
head raised (KeyError), read a bool as 1.0, or scaled by a nan/inf. There is no
committed harness that drives these inputs, so this one is the reviewer's own
and is named as such (fix-review.md step 9).

METRIC. For each input row: (result, verdict) where verdict is
  fallback  = result == pro_rata_factor(NOW) exactly          (coverage read as lost)
  scaled    = result == max(1.0, month_hours(NOW)/settled)    (a settled figure used)
  raise:<T> = the call raised T                               (the old defect)
The key is the VALUE coverage_factor returns, not any input attribute.

RUN (per tree root, a worktree):
    python3 -I bad_inputs.py <TREE_ROOT> <LABEL>

Null controls: (a) a genuinely covered month must be ``scaled`` at BOTH ends and
equal at both ends; (b) ``meta={}`` (no coverage) must be ``fallback`` at both.
"""
import sys
from datetime import datetime

root = sys.argv[1]
label = sys.argv[2]
sys.path.insert(0, root + "/tests/hastub")
sys.path.insert(0, root + "/tests")
sys.path.insert(0, root + "/custom_components")

from heatpump_optimizer.ledger import (  # noqa: E402
    SPOT_PRICE_META, SETTLED_HOURS_META, coverage_factor, month_hours, pro_rata_factor,
)

NOW = datetime(2026, 2, 10, 15, 0)  # day 10 of a 28-day month -> pro_rata 2.8
PR = pro_rata_factor(NOW)
MH = month_hours(NOW)
GOOD = {SETTLED_HOURS_META: {"sum": 24.0, "count": 24},
        SPOT_PRICE_META: {"sum": 24.0, "count": 24}}


def run(meta):
    try:
        return coverage_factor(meta, NOW), None
    except Exception as exc:  # noqa: BLE001 -- the raise is the defect
        return None, type(exc).__name__


def verdict(got, settled=0.0):
    if settled > 0:
        return "scaled" if got == max(1.0, MH / settled) else "OTHER"
    return "fallback" if got == PR else "OTHER"


E = SETTLED_HOURS_META
S = SPOT_PRICE_META
ROWS = [
    ("control: genuinely covered (24 h settled, 24 spot folds)", GOOD, 24.0),
    ("control: no coverage (meta={})", {}, 0.0),
    ("settled entry None", {E: None}, 0.0),
    ("settled entry not a dict (list)", {E: [1, 2]}, 0.0),
    ("settled entry not a dict (str)", {E: "24"}, 0.0),
    ("settled dict missing 'sum'", {E: {"count": 24}}, 0.0),
    ("settled sum non-numeric 'warm'", {E: {"sum": "warm", "count": 24}}, 0.0),
    ("settled sum 'nan'", {E: {"sum": "nan", "count": 24}}, 0.0),
    ("settled sum 'inf'", {E: {"sum": "inf", "count": 24}}, 0.0),
    ("settled sum float('nan')", {E: {"sum": float("nan"), "count": 24}}, 0.0),
    ("settled sum float('inf')", {E: {"sum": float("inf"), "count": 24}}, 0.0),
    ("settled sum bool True", {E: {"sum": True, "count": 24}}, 0.0),
    ("settled dict missing 'count'", {E: {"sum": 24.0}}, 0.0),
    ("settled count 'nan'", {E: {"sum": 24.0, "count": "nan"}}, 0.0),
    ("settled count 'inf'", {E: {"sum": 24.0, "count": "inf"}}, 0.0),
    ("settled count bool True", {E: {"sum": 24.0, "count": True}}, 24.0),
    ("spot entry None (covered settled)", {E: {"sum": 24.0, "count": 24}, S: None}, 24.0),
    ("spot entry not a dict", {E: {"sum": 24.0, "count": 24}, S: 7}, 24.0),
    ("spot dict missing 'count'", {E: {"sum": 24.0, "count": 24}, S: {"sum": 1.0}}, 24.0),
    ("spot count 'nan'", {E: {"sum": 24.0, "count": 24}, S: {"count": "nan"}}, 24.0),
    ("spot count 'inf'", {E: {"sum": 24.0, "count": 24}, S: {"count": "inf"}}, 24.0),
    ("whole meta is None (out of stated scope)", None, 0.0),
]

print(f"# {label}  pro_rata={PR!r} month_hours={MH!r}")
bad = 0
for name, meta, settled in ROWS:
    got, exc = run(meta)
    v = ("raise:" + exc) if exc else verdict(got, settled)
    if v not in ("fallback", "scaled") and not name.startswith("whole meta"):
        bad += 1
    print(f"RESULT {label:10s} | {name:52s} | got={got!r:28s} | {v}")

print(f"RESULT {label} unexpected={bad} count")
