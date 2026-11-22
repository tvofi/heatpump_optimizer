"""Differential check, PR #3838 delta c03b640cd6: the old _build_comfort_bounds floor
arithmetic (reviewed head 6ef32c22f3, _raised_floor padding inside) against the head's
(raised_floor in rooms.py, padding at the caller), on inputs shaped as
rooms.floor_limits hands them (margins = _margins(base) + lift, room_lifts = lift).
Run from the head checkout with PYTHONPATH=tests/hastub."""
import sys
import numpy as np

sys.path.insert(0, ".")
from custom_components.heatpump_optimizer.optimizer import _padded_nonneg  # noqa: E402
from custom_components.heatpump_optimizer.rooms import raised_floor, _margins  # noqa: E402


def old_raised(low, high, margins, floors, n):  # verbatim from 6ef32c22f3 optimizer._raised_floor
    comfort, mold = low, None
    if margins is None and floors is None:
        return low, comfort, mold
    if margins is not None:
        low = comfort = low + _padded_nonneg(margins, n)
    if floors is not None:
        f = np.asarray(floors, dtype=float)[:n]
        mold = np.full(n, -np.inf)
        mold[:f.size] = f
        low = np.maximum(low, mold)
    return np.minimum(low, high - 0.5), comfort, mold


def old_build(low, high, mtm, floors, lifts_in, n):  # 6ef32c22f3 call site
    tmin, cf, mf = old_raised(low, high, mtm, floors, n)
    lifts = None
    if lifts_in is not None:
        margins = _padded_nonneg(np.zeros(n) if mtm is None else mtm, n)
        unl = old_raised(low, high, margins - _padded_nonneg(lifts_in, n), floors, n)[0]
        lifts = np.maximum(tmin - unl, 0.0)
    return tmin, cf, mf, lifts


def new_build(low, high, mtm, floors, lifts_in, n):  # 9516fcc5 call site
    margins = None if mtm is None else _padded_nonneg(mtm, n)
    tmin, cf, mf = raised_floor(low, high, margins, floors, n)
    lifts = None
    if lifts_in is not None:
        unl = raised_floor(low, high, (0.0 if margins is None else margins)
                           - _padded_nonneg(lifts_in, n), floors, n)[0]
        lifts = np.maximum(tmin - unl, 0.0)
    return tmin, cf, mf, lifts


def same(a, b):
    for x, y in zip(a, b):
        if (x is None) != (y is None):
            return False
        if x is not None and not np.array_equal(x, y):
            return False
    return True


rng = np.random.default_rng(3838)
cases = diffs = 0
for _ in range(20000):
    n = int(rng.integers(1, 49))
    low = rng.uniform(15, 22, n)
    high = low + rng.uniform(0.0, 6.0, n)
    base = None if rng.random() < 0.2 else rng.normal(0.3, 0.6, int(rng.integers(0, n + 3)))
    floors = None if rng.random() < 0.4 else rng.uniform(10, 24, int(rng.integers(0, n + 3)))
    lift = None if rng.random() < 0.3 else np.clip(rng.uniform(-0.5, 2.0, n), 0.0, None)
    if lift is not None and rng.random() < 0.3:
        lift[:] = np.where(rng.random(n) < 0.5, 0.0, lift)
    # floor_limits' shape: lift present -> margins = _margins(base, n) + lift
    if lift is None or not lift.any():
        mtm, rl = base, None
    else:
        mtm, rl = _margins(base, n) + lift, lift
    cases += 1
    if not same(old_build(low, high, mtm, floors, rl, n), new_build(low, high, mtm, floors, rl, n)):
        diffs += 1
print(f"EQUIV floor_limits-shaped inputs: {cases} cases, {diffs} differ")

# Null control: inputs floor_limits never produces (room_lifts with margins None, or a
# lift longer than the margins) must make the two differ, or the check above reads nothing.
n = 4
low, high = np.full(n, 19.0), np.full(n, 23.0)
lift = np.full(n, 1.0)
a = old_build(low, high, None, None, lift, n)[3]
b = new_build(low, high, None, None, lift, n)[3]
print(f"NULL CONTROL margins None + lift 1.0: old lifts {a.tolist()} new lifts {b.tolist()} differ={not np.array_equal(a, b)}")
a = old_build(low, high, np.array([1.0, 1.0]), None, lift, n)[3]
b = new_build(low, high, np.array([1.0, 1.0]), None, lift, n)[3]
print(f"NULL CONTROL margins shorter than lift: old {a.tolist()} new {b.tolist()} differ={not np.array_equal(a, b)}")
