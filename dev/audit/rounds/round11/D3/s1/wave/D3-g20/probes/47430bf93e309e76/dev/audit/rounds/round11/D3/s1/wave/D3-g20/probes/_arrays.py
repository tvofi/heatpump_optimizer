"""Shared body of the _build_comfort_bounds / _build_space_power_caps probes."""
import numpy as np
from _mutant import build, mutated, outcome, tail

OPT = build()


def same(a, b):
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    if isinstance(a, (tuple, list)):
        return isinstance(b, (tuple, list)) and len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if a is None or b is None or isinstance(a, (bool, np.bool_)):
        return a is b or a == b
    a, b = np.asarray(a), np.asarray(b)
    return a.shape == b.shape and np.array_equal(a, b, equal_nan=True)


def show(v):
    if isinstance(v, str):
        return v
    if isinstance(v, (tuple, list)):
        return "(" + ", ".join(show(x) for x in v) + ")"
    if v is None or isinstance(v, (bool, np.bool_)):
        return repr(v)
    v = np.asarray(v)
    return f"shape{v.shape} first={v.ravel()[:3].tolist()}"


def run(method, old, new, cases, null):
    """cases: [(label, args)], null: (label, args) where the mutated condition has one truth value."""
    moved, rows = 0, []
    for label, args in cases:
        b = outcome(lambda: getattr(OPT, method)(*args))
        with mutated(method, old, new):
            m = outcome(lambda: getattr(OPT, method)(*args))
        if not same(b, m):
            moved += 1
            rows.append((label, b, m))
    print(f"RESULT inputs_tried={len(cases)} count")
    print(f"RESULT inputs_moved={moved} count")
    both_raise = sum(1 for _, b, m in rows if isinstance(b, str) and isinstance(m, str))
    print(f"RESULT inputs_moved_beyond_exception_type={moved - both_raise} count "
          f"(rows where both arms raise, differing only in the exception type: {both_raise})")
    for label, b, m in rows[:5]:
        print(f"RESULT moved {label}: baseline={show(b)} mutant={show(m)}")
    label, args = null
    b = outcome(lambda: getattr(OPT, method)(*args))
    with mutated(method, old, new):
        m = outcome(lambda: getattr(OPT, method)(*args))
    print(f"RESULT null_delta={0 if same(b, m) else 1} count ({label})")
    tail()
    return moved
