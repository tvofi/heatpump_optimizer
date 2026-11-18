"""Verifier D1#1, V2 for D1-s2-06: boost._restore_settle against timedelta's range, called directly.

Metric: over stored boosted_h in {1.5, 1e9, 1e10, 2.39e10, 2.41e10, 3e10, 1e12, 9.9e14}, the count
that (a) pass store._sanitize (below store.ABSURD) and (b) make boost._restore_settle raise.
Also whether space_since is left unrestored after the raise (the half-applied restore).
timedelta.max in hours = 999999999*24 + 23.99 = ~2.4e10.
Null: 1.5 and 1e9 must not raise.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s2_06_settle_unit.py
"""
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")
from heatpump_optimizer import boost, store  # noqa: E402

now = datetime(2026, 2, 1, 6, 0, tzinfo=timezone.utc)
since = (now - timedelta(hours=2)).isoformat()
raised = passed = unrestored = nulls = 0
for h in (1.5, 1e9, 1e10, 2.39e10, 2.41e10, 3e10, 1e12, 9.9e14):
    raw = {"space_settle": {"until": (now + timedelta(hours=1)).isoformat(), "boosted_h": h},
           boost.CHANNEL_SPACE: {"since": since, "until": (now + timedelta(hours=3)).isoformat()}}
    clean = store._sanitize(raw)
    ok_boundary = clean["space_settle"]["boosted_h"] == h
    passed += ok_boundary
    held = boost.BoostState()
    held.until[boost.CHANNEL_SPACE] = now + timedelta(hours=3)
    try:
        boost._restore_settle(held, clean, now)
        err = None
    except Exception as e:  # noqa: BLE001
        err = type(e).__name__
    print(f"boosted_h={h:g} passes_boundary={ok_boundary} raise={err} space_since={held.space_since} space_boosted={held.space_boosted}")
    if err:
        raised += 1
        unrestored += held.space_since is None
    elif h < 1e10:
        nulls += 0
print(f"RESULT pass_boundary={passed} of 8")
print(f"RESULT raise={raised} of 8")
print(f"RESULT raise_and_since_unrestored={unrestored}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
