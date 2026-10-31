#!/usr/bin/env python3
"""R9-SW-1: `_forced_off_with`'s CMP_BOUND mutant, driven for equivalence.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/SW1/forced_off_equiv.py

The method is tools/audit/round9/F10/f10_6/equiv_probe.py's: the operator's
own mutant is taken from `candidates()`, the function is compiled from the
mutated module text into `dhw_planner`'s globals, and head and mutant are
called on one grid. `<` against `<=` can differ only at `mask.size ==
n_steps`, so ties are counted by an append inside the compiled comparison,
and the control is a tie-only edit that inverts the mask only at a tie; it
must move on the tied cases, and `control_differs_untied` must stay 0.

Every caller only reads the returned mask (`forced_off[j]`, a slice under
`~`, `np.where`), so the view head returns at a tie and the copy the mutant
returns are compared by value.
"""
import ast
import sys

import numpy as np

sys.path[:0] = ["tests", "."]
import mutation_table as mt  # noqa: E402
from custom_components.heatpump_optimizer import dhw_planner  # noqa: E402

NAME = "_forced_off_with"
OLD = "if mask.size < n_steps:"
TIE = "if (_T.append(mask.size == n_steps) or True) and mask.size < n_steps:"
CONTROL = ("if mask.size < n_steps or mask.size == n_steps"
           " and (mask := ~mask) is not None:")


def build(text: str, ties: list | None = None):
    fn = next(n for n in ast.parse(text).body
              if isinstance(n, ast.FunctionDef) and n.name == NAME)
    ns = dict(vars(dhw_planner), _T=ties if ties is not None else [])
    exec(compile(ast.Module([fn], []), dhw_planner.__file__, "exec"), ns)
    return ns[NAME]


def replaced(src: str, ln: int, new: str) -> str:
    lines = src.splitlines(True)
    t = lines[ln - 1]
    lines[ln - 1] = t[: len(t) - len(t.lstrip())] + new + "\n"
    return "".join(lines)


def grid():
    rng = np.random.default_rng(20261006)
    for n in (0, 1, 4, 8, 96):
        for m in sorted({0, 1, max(n - 1, 0), n, n + 3}):
            off = rng.random(m) < 0.4
            for prior in (None, rng.random(n) < 0.3):
                yield prior, off, n
                yield prior, list(off), n


path = mt.Path(dhw_planner.__file__)
src = path.read_text()
site = [m for m in mt.candidates(path)
        if m["kind"] == "CMP_BOUND" and m["old"].strip() == OLD]
assert len(site) == 1, len(site)
ln = site[0]["line"]
head = build(src)
mutant = build(replaced(src, ln, site[0]["new"].strip()))
control = build(replaced(src, ln, CONTROL))
cases = ties = diff = ctl_tied = ctl_untied = immovable = 0
for args in grid():
    t: list[bool] = []
    build(replaced(src, ln, TIE), ties=t)(*args)
    tied = any(t)
    a = head(*args)
    cases += 1
    ties += tied
    diff += not np.array_equal(a, mutant(*args))
    moved = not np.array_equal(a, control(*args))
    ctl_tied += moved and tied
    ctl_untied += moved and not tied
    prior, _, n = args
    immovable += tied and (n == 0 or (prior is not None and bool(prior.all())))
print(f"SITE dhw_planner.py:{ln} CMP_BOUND {site[0]['new'].strip()}")
print(f"RESULT {NAME} cases={cases} ties={ties} mutant_differs={diff} "
      f"control_differs_at_tie={ctl_tied} control_differs_untied={ctl_untied}")
print(f"RESULT {NAME} tied_cases_the_control_cannot_move={immovable} "
      f"(n_steps 0, or a prior mask already all True)")
