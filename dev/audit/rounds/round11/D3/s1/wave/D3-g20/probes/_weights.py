"""Shared body of the three _anticipatory_weights probes (keys a0722b8c, d800d285, 176e4dd6)."""
import warnings
import numpy as np
from _mutant import HeatPumpOptimizer, build, mutated, outcome, tail

OPT = build()
DTS = (0.25, 0.5, 1.0, 8.0, 9.0, 24.0)
NS = (1, 4, 96)


def inputs():
    """(label, n, dt, solar, loss): boundaries, the exact ties, empty-ish and non-finite."""
    out = []
    for dt in DTS:
        for n in NS:
            for s in (0.0, 0.5, np.nextafter(0.5, 1), 2.0, np.nan):
                for f in (1.0, 1.1, np.nextafter(1.1, 2), 2.0, np.nan):
                    out.append((f"dt={dt} n={n} solar={s!r} loss={f!r}", n, dt,
                                np.full(n, s, dtype=float), np.full(n, f, dtype=float)))
    return out


def run(old, new, tie_label):
    moved, first, tie = 0, None, None
    cases = inputs()
    for label, n, dt, s, f in cases:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            b = outcome(lambda: OPT._anticipatory_weights(n, dt, s, f))
            with mutated("_anticipatory_weights", old, new):
                m = outcome(lambda: OPT._anticipatory_weights(n, dt, s, f))
        same = (isinstance(b, str) and b == m) or (
            not isinstance(b, str) and not isinstance(m, str) and np.array_equal(b, m, equal_nan=True))
        if not same:
            moved += 1
            first = first or (label, b if isinstance(b, str) else float(b[0]), m if isinstance(m, str) else float(m[0]))
        if label == tie_label:
            tie = (b if isinstance(b, str) else float(b[0]), m if isinstance(m, str) else float(m[0]))
    print(f"RESULT inputs_tried={len(cases)} count")
    print(f"RESULT inputs_moved={moved} count")
    if tie is not None:
        print(f"RESULT tie_baseline_weight0={tie[0]}")
        print(f"RESULT tie_mutant_weight0={tie[1]}")
    if first:
        print(f"RESULT first_moved_input={first[0]!r} baseline={first[1]} mutant={first[2]}")
    # null control: a comfortably interior input, where the mutated comparison has the same truth value
    s, f = np.full(96, 2.0), np.full(96, 2.0)
    b = OPT._anticipatory_weights(96, 0.25, s, f)
    with mutated("_anticipatory_weights", old, new):
        m = OPT._anticipatory_weights(96, 0.25, s, f)
    print(f"RESULT null_delta={float(np.max(np.abs(b - m))):.6g}")
    tail()
    return moved
