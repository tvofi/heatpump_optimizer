"""Reviewer's re-derivation: SetpointGrid.bounded with and without the pre-clamp to the entity's maximum
that commit 497c8133f5 deleted as dead. Prints the count of differing results (reviewer's instrument)."""
import sys, os, itertools
TREE = sys.argv[1]; sys.path[:0] = [os.path.join(TREE, "tests", "hastub"), os.path.join(TREE, "custom_components")]
from heatpump_optimizer.inputs import SetpointGrid
n = d = 0; ex = None
units = ["°C", "°F", None]
for unit, step, low, high in itertools.product(units, (0.1, 0.5, 1.0, 5.0), (None, 5.0, 37.3), (None, 55.0, 61.7, 80.0)):
    g = SetpointGrid(unit, step, low, high)
    for v10, rounding, floor, lo, hi in itertools.product(range(-50, 950, 13), ("nearest", "up", "down"), (-1e9, 20.0, 58.0), (None, 41.2), (None, 30.0, 56.0, 90.0)):
        v = v10 / 10.0
        a = g.bounded(v, floor, rounding=rounding, lo=lo, hi=hi)
        # the deleted statement, applied where it stood: after the max() with floor and low
        low_, high_ = g.low_c, g.high_c
        vv = max(v, floor, low_ if low_ is not None else floor)
        vv = min(vv, high_) if high_ is not None else vv
        b = g.bounded(vv, -1e9 if True else floor, rounding=rounding, lo=lo, hi=hi) if False else None
        # re-state the old body exactly
        lows = [x for x in (lo, low_) if x is not None]; highs = [high_] if high_ is not None else []
        if hi is not None and (low_ is None or hi >= g.on_step(low_, rounding="up")): highs.append(hi)
        b = g.on_step(vv, rounding=rounding, lo_c=max(lows) if lows else None, hi_c=min(highs) if highs else None)
        n += 1
        if abs(a - b) > 1e-9:
            d += 1; ex = ex or (unit, step, low, high, v, rounding, floor, lo, hi, a, b)
print(f"RESULT preclamp cases={n} differing={d} example={ex}")
