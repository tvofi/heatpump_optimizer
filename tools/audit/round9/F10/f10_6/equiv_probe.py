#!/usr/bin/env python3
"""F10.6: the two CMP_BOUND mutants the #1861 review proved equivalent, driven.

    PYTHONPATH=tests/hastub python3 tools/audit/round9/F10/f10_6/equiv_probe.py

Needs numpy (optimizer.py). For each site the operator's own mutant is taken
from `candidates()`, the enclosing production function is compiled from the
mutated module text into that module's globals, and head and mutant are called
on the same input grid. `ties` counts inputs that reach the comparison with
its two sides EQUAL -- the only place `<` and `<=` can differ -- so a probe
whose grid never ties would be vacuous. The control is a non-equivalent edit
of the same line (GUARD_OFF's `if False:` for away.py; `idx = last` for
optimizer.py), which must differ on the same grid.
"""
import ast
import sys
import types
from datetime import datetime, timedelta, timezone

import numpy as np

sys.path[:0] = ["tests", "."]
import mutation_table as mt  # noqa: E402
from custom_components.heatpump_optimizer import away, optimizer  # noqa: E402


def compiled(mod, text: str, name: str, cls: str | None = None):
    tree = ast.parse(text)
    body = tree.body
    if cls:
        body = next(n for n in body if isinstance(n, ast.ClassDef)
                    and n.name == cls).body
    fn = next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(vars(mod))
    exec(compile(ast.Module([fn], []), mod.__file__, "exec"), ns)
    return ns[name]


def mutant_text(mod, old: str, kind: str, new: str | None = None):
    path = mt.Path(mod.__file__)
    src = path.read_text()
    lines = src.splitlines(True)
    if new is None:
        m = [m for m in mt.candidates(path) if m["kind"] == kind
             and m["old"].strip() == old]
        assert len(m) == 1, (old, kind, len(m))
        ln, new = m[0]["line"], m[0]["new"]
    else:
        ln = next(i for i, t in enumerate(lines, 1) if t.strip() == old)
        new = lines[ln - 1][: len(lines[ln - 1]) - len(lines[ln - 1].lstrip())] + new
    lines[ln - 1] = new + "\n"
    return src, "".join(lines), ln


def away_grid():
    now = datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc)
    stamps = [None, "2026-03-29T00:00:00+00:00", "2026-03-29T08:00:00+00:00",
              "2026-03-30T00:00:00+00:00", "2026-03-28T23:00:00+00:00",
              "2026-03-31T17:30:00+00:00", "2026-03-27T00:00:00+00:00"]
    for s in stamps:
        for e in stamps:
            yield {"start_time": s or "", "end_time": e or ""}, now


def run(name, head, mut, ctl, grid, tie):
    diff = ctl_diff = ties = n = 0
    for args in grid():
        n += 1
        a, b, c = head(*args), mut(*args), ctl(*args)
        same = (np.array_equal(a, b) if isinstance(a, np.ndarray) else a == b)
        diff += not same
        ctl_diff += not (np.array_equal(a, c) if isinstance(a, np.ndarray) else a == c)
        ties += tie(args)
    print(f"RESULT {name} cases={n} ties={ties} mutant_differs={diff} "
          f"control_differs={ctl_diff}")


src, mtext, ln = mutant_text(away, "if last < first:", "CMP_BOUND")
_, ctext, _ = mutant_text(away, "if last < first:", "GUARD_OFF")
print(f"SITE away.py:{ln} CMP_BOUND")
h = compiled(away, src, "_holiday_span")


def away_tie(args):
    first, last = h(*args)
    attrs, now = args
    end = away._parse_return_time(attrs["end_time"]) or now
    start = away._parse_return_time(attrs["start_time"]) or now
    raw = end.date() - (timedelta(days=1) if end.time() == datetime.min.time()
                        and end > start else timedelta(0))
    return int(raw == start.date())


run("away._holiday_span", h, compiled(away, mtext, "_holiday_span"),
    compiled(away, ctext, "_holiday_span"), away_grid, away_tie)

OLD = "idx = i if i <= last else last"
src, mtext, ln = mutant_text(optimizer, OLD, "CMP_BOUND")
_, ctext, _ = mutant_text(optimizer, OLD, None, new="idx = last")
print(f"SITE optimizer.py:{ln} CMP_BOUND")
kw = dict(cls="HeatPumpOptimizer")
heads = [compiled(optimizer, t, "_dhw_planner_draws", **kw)
         for t in (src, mtext, ctext)]
me = types.SimpleNamespace(model=types.SimpleNamespace(params=types.SimpleNamespace(
    dhw_setpoint=55.0, dhw_inlet_reference=10.0)))


def opt_grid():
    rng = np.random.default_rng(20261002)
    for n in (1, 3, 8, 24):
        for m in (1, 2, n, n + 3):
            yield me, rng.uniform(0.0, 0.3, n), rng.uniform(20.0, 80.0, m)


run("optimizer._dhw_planner_draws", *[(lambda f: (lambda *a: f(*a)))(f) for f in heads],
    opt_grid, lambda a: int(len(a[2]) - 1 < len(a[1])))
