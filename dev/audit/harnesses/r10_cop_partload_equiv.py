#!/usr/bin/env python3
"""R10-COP-PARTLOAD: is the `0.0 <= derate` CMP_BOUND twin an equivalent mutant?

    PYTHONPATH=tests/hastub:. python3 \
        dev/audit/harnesses/r10_cop_partload_equiv.py [--identity]

Metric: the number of probe inputs on which the operator's own rewrite of
`thermal_model._partload_derate`'s lower bound -- `0.0 <= derate` written
`0.0 < derate` -- makes the helper, and `ThermalParameters.from_config`
through it, answer a different value than the tree's. The grid holds both
bounds and their just-outside floats, +0.0 and -0.0, the non-finite floats,
numeric strings, non-float types and numpy scalars; the anchor's other twin
(`<= MAX` written `< MAX`) rides along as the differential's positive control.
0 differing cells over that grid is an equivalent mutant on the probed domain:
no check can kill it, so the ledger's `survivor_triage` mark for it is
`equivalent` and never a gap.
Expected on this tree (chain R10-COP-PARTLOAD, the part-load derate):
    RESULT equiv_cells=40 count
    RESULT equiv_differs=0 count             (lower-bound twin, direct)
    RESULT equiv_config_differs=0 count      (the same grid through from_config)
    RESULT equiv_ties=7 count                (the cells that are 0.0 -- +0.0,
                                              -0.0, their two strings, False, 0,
                                              np.int64(0): every input the two
                                              arms decide differently)
    RESULT equiv_sign_only=2 count           (-0.0 and "-0.0": the arms answer
                                              -0.0 and 0.0, numerically equal and
                                              equal in every caller's product)
    RESULT equiv_control_differs=7 count     (tie-only control: a deliberate
                                              change at the ties, differing on
                                              every tied cell)
    RESULT equiv_control_untied=0 count
    RESULT equiv_positive_differs=4 count    (the other twin: differs on the
                                              four cells that are 0.5 -- 0.5,
                                              "0.5", Fraction(1, 2),
                                              np.float64(0.5) -- and nowhere else)
    RESULT load1=...                         (reported, not asserted)
Baseline 3890f2825: the operator text is
`if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:` at thermal_model.py
line 1738; mutation is applied in memory, nothing on disk changes.
Perturbation: --identity applies each mutant's *old* line as the "mutant";
every RESULT count above must read 0, so a difference the normal run reports is
the operator's and not the comparison's -- and the normal run's tie-only
control, which differs on all seven tied cells and nowhere else, is what shows
the comparison sees a difference there when one exists.
"""
from __future__ import annotations

import inspect
import math
import os
import sys
from fractions import Fraction

import numpy as np

from custom_components.heatpump_optimizer import thermal_model as tm
from custom_components.heatpump_optimizer.const import (
    CONF_HEAT_PUMP_COP_PARTLOAD_DERATE as KEY,
)

IDENT = "--identity" in sys.argv

LOWER_OLD = "    if 0.0 <= derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:"
LOWER_NEW = "    if 0.0 < derate <= MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:"
UPPER_OLD = LOWER_OLD
UPPER_NEW = "    if 0.0 <= derate < MAX_HEAT_PUMP_COP_PARTLOAD_DERATE:"
ACCEPT_OLD = "        return derate"
ACCEPT_CTRL = "        return 1.0 if derate == 0.0 else derate"

GRID = [
    0.0, -0.0, 1e-12, -1e-12, 1e-9, 0.01, 0.1, 0.25, 0.49,
    0.4999999999, 0.5, 0.5000000001, 0.51, 0.9, 1.0, 2.0, 1e9, -1e9,
    float("nan"), float("inf"), float("-inf"),
    "0.0", "-0.0", "0.1", "0.5", "0.51", "-0.1", "x", "", None,
    True, False, 0, 1, -1, Fraction(1, 2), 0.5 + 0j,
    np.float64(0.5), np.float32(0.1), np.int64(0),
]


def mutate(old: str, new: str):
    """The tree's `_partload_derate` with one of its lines rewritten.

    In memory: the function's own source is re-exec'd against the module's
    globals, so `MAX_HEAT_PUMP_COP_PARTLOAD_DERATE` and the default resolve
    exactly as they do in the tree.
    """
    src = inspect.getsource(tm._partload_derate)
    assert src.count(old) == 1, (old, src.count(old))
    ns: dict = {}
    exec(compile(src.replace(old, old if IDENT else new), "<mut>", "exec"),
         dict(vars(tm)), ns)
    return ns["_partload_derate"]


def same(a, b) -> bool:
    """Value equality that treats two NaNs as the same answer."""
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def call(fn, value):
    """One probe cell, a raise included as an answer rather than a crash."""
    try:
        return fn(value)
    except Exception as exc:  # noqa: BLE001 - the answer is the exception
        return ("raised", type(exc).__name__)


def tie(value) -> bool:
    """True where the two lower bounds decide differently: derate == 0.0."""
    try:
        d = float(value)
    except (TypeError, ValueError):
        return False
    return (0.0 <= d) != (0.0 < d)


def config_cells(fn) -> list:
    """`cop_partload_derate` through the public constructor, with `fn` in place."""
    had = tm._partload_derate
    tm._partload_derate = fn
    try:
        return [tm.ThermalParameters.from_config({KEY: v}).cop_partload_derate
                for v in GRID]
    finally:
        tm._partload_derate = had


def main() -> int:
    head = tm._partload_derate
    lower = mutate(LOWER_OLD, LOWER_NEW)
    upper = mutate(UPPER_OLD, UPPER_NEW)
    ctrl = mutate(ACCEPT_OLD, ACCEPT_CTRL)

    cells = [call(head, v) for v in GRID]
    differs = [v for v, a in zip(GRID, cells)
               if not same(a, call(lower, v))]
    config_differs = sum(
        1 for a, b in zip(config_cells(head), config_cells(lower))
        if not same(a, b))
    ties = [v for v in GRID if tie(v)]
    sign_only = sum(
        1 for a, v in zip(cells, GRID)
        if isinstance(a, float) and a == 0.0
        and isinstance(call(lower, v), float) and call(lower, v) == 0.0
        and math.copysign(1.0, a) != math.copysign(1.0, call(lower, v)))
    ctrl_differs = [v for v, a in zip(GRID, cells)
                    if not same(a, call(ctrl, v))]
    ctrl_untied = [v for v in ctrl_differs if not tie(v)]
    positive = [v for v, a in zip(GRID, cells)
                if not same(a, call(upper, v))]

    print(f"RESULT equiv_cells={len(GRID)} count")
    print(f"RESULT equiv_differs={len(differs)} count")
    print(f"RESULT equiv_config_differs={config_differs} count")
    print(f"RESULT equiv_ties={len(ties)} count")
    print(f"RESULT equiv_sign_only={sign_only} count")
    print(f"RESULT equiv_control_differs={len(ctrl_differs)} count")
    print(f"RESULT equiv_control_untied={len(ctrl_untied)} count")
    print(f"RESULT equiv_positive_differs={len(positive)} count")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    if differs or config_differs:
        print(f"  lower twin differs at {differs!r}")
        return 1
    if not IDENT and not positive:
        print("  the positive control saw no difference: the probe is blind")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
