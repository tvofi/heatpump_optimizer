#!/usr/bin/env python3
"""F10.6: the two CMP_BOUND mutants the #1861 review proved equivalent, driven.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/F10/f10_6/equiv_probe.py

Needs numpy. For each site the operator's own mutant is taken from
`candidates()`, the enclosing production function is compiled from the
mutated module text into that module's globals, and head and mutant are
called on the same input grid.

A `<` against `<=` mutant can differ only where the two sides are EQUAL, so
both the tie count and the control are about that arm:
- ties are counted INSIDE the compiled production function, by an append in
  the comparison itself (`_T.append(a == b) or True`), not by recomputation;
- the control is a TIE-ONLY edit of the same line, one that changes the
  result only when the two sides are equal; it must differ on the tied cases,
  or the grid cannot see a tie. `control_differs_untied` must stay 0.
The tie counter and both tie-only controls are the #1861 fix review's
(~/hpo-seats/1861-review/own/rv_equiv_probe.py, round 2, sha1 6f7aee1d).
"""
import ast
import sys
import types
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path[:0] = ["tests", "."]
import mutation_table as mt  # noqa: E402
from custom_components.heatpump_optimizer import away, dhw_planner  # noqa: E402


def compiled(mod, text: str, name: str, cls: str | None = None, ties=None):
    body = ast.parse(text).body
    if cls:
        body = next(n for n in body if isinstance(n, ast.ClassDef)
                    and n.name == cls).body
    fn = next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(vars(mod), _T=ties if ties is not None else [])
    exec(compile(ast.Module([fn], []), mod.__file__, "exec"), ns)
    return ns[name]


def edited(mod, old: str, new: str | None = None) -> tuple[str, str, int]:
    """(module text, text with line `old` replaced, line number); `new=None`
    takes CMP_BOUND's own mutant of that line from candidates()."""
    path = mt.Path(mod.__file__)
    src = path.read_text()
    lines = src.splitlines(True)
    if new is None:
        m = [m for m in mt.candidates(path) if m["kind"] == "CMP_BOUND"
             and m["old"].strip() == old]
        assert len(m) == 1, (old, len(m))
        ln, line = m[0]["line"], m[0]["new"]
    else:
        ln = next(i for i, t in enumerate(lines, 1) if t.strip() == old)
        t = lines[ln - 1]
        line = t[: len(t) - len(t.lstrip())] + new
    lines[ln - 1] = line + "\n"
    return src, "".join(lines), ln


def same(a, b) -> bool:
    if isinstance(a, np.ndarray):
        return np.array_equal(a, b)
    return a == b


def run(name, mod, old, tie_line, ctl_line, grid, cls=None):
    src, mtext, ln = edited(mod, old)
    _, ttext, _ = edited(mod, old, tie_line)
    _, ctext, _ = edited(mod, old, ctl_line)
    head = compiled(mod, src, name, cls)
    mut = compiled(mod, mtext, name, cls)
    ctl = compiled(mod, ctext, name, cls)
    cases = ties = diff = ctl_tied = ctl_untied = 0
    for args in grid():
        t: list[bool] = []
        compiled(mod, ttext, name, cls, ties=t)(*args)
        tied = any(t)
        a = head(*args)
        cases += 1
        ties += tied
        diff += not same(a, mut(*args))
        moved = not same(a, ctl(*args))
        ctl_tied += moved and tied
        ctl_untied += moved and not tied
    print(f"SITE {mod.__name__.rsplit('.', 1)[-1]}.py:{ln} CMP_BOUND")
    print(f"RESULT {name} cases={cases} ties={ties} mutant_differs={diff} "
          f"control_differs_at_tie={ctl_tied} control_differs_untied={ctl_untied}")


def away_grid():
    now = datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc)
    stamps = [None, "2026-03-29T00:00:00+00:00", "2026-03-29T08:00:00+00:00",
              "2026-03-30T00:00:00+00:00", "2026-03-28T23:00:00+00:00",
              "2026-03-31T17:30:00+00:00", "2026-03-27T00:00:00+00:00"]
    for s in stamps:
        for e in stamps:
            yield {"start_time": s or "", "end_time": e or ""}, now


ME = types.SimpleNamespace(model=types.SimpleNamespace(params=types.SimpleNamespace(
    dhw_setpoint=55.0, dhw_inlet_reference=10.0)))


def draws_grid():
    rng = np.random.default_rng(20261002)
    for n in (1, 3, 8, 24):
        for m in (1, 2, n, n + 3):
            yield ME, rng.uniform(0.0, 0.3, n), rng.uniform(20.0, 80.0, m)


run("_holiday_span", away, "if last < first:",
    "if (_T.append(last == first) or True) and last < first:",
    "if last < first or last == first and (first := first - timedelta(days=1)):",
    away_grid)
run("_dhw_planner_draws", dhw_planner, "idx = i if i <= last else last",
    "idx = i if (_T.append(i == last) or True) and i <= last else last",
    "idx = i if i < last else (last - 1 if i == last and last > 0 else last)",
    draws_grid, cls="DhwPlanner")
lone = sum(1 for _, r, w in draws_grid() if len(w) == 1)
print(f"RESULT _dhw_planner_draws tied_cases_with_last_0={lone} "
      f"(the control's `last > 0` cannot move them)")
