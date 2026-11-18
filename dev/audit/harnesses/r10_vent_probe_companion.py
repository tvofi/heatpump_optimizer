"""Companion to the round-10 P5 sweep instruments for #2241 (D2-s3-72).

Both finder instruments read flat across the fix, because each is keyed to
the instance rather than the property:
  dev/audit/rounds/round10/D14/sweep-P5/probe_vent_bias.py builds a bare
      ``drift.Cusum(threshold, drift, side=-1)`` -- the primitive's default,
      which the fix leaves alone (the COP-health watch uses it);
  dev/audit/rounds/round10/D14/sweep-P5/enumerate.py marks a Cusum an
      instance when its ``.update()`` argument names "residual" -- a name the
      fix rightly keeps, since the residual stays the detector's signal.
This applies the tree's own rule to the probe's inputs.

Part 1 (the probe's series, through the coordinator's OWN detector): a fresh
real coordinator per arm, its ``_vent_cusum`` fed 96 x 15-min samples of a
constant cold bias (-0.00, -0.05, -0.10, -0.40 K), then the same arm with a
window planted on top (the bias plus a further -0.50 K for 4 samples).
Property: no bias arm trips; every planted window does.
Null control: bias 0.00 -> no trip at both ends. Perturbation: the planted
window -> trips at both ends.

Part 2 (the class rule): every ``Cusum(...)`` construction in the package,
with whether it is read in ``_learning_frozen`` and whether it sets
``reference_hours`` -- a learning gate whose zero is not the signal's
normal needs one.

Command (tree root):
    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_vent_probe_companion.py
"""
import ast
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "tests")
sys.path.insert(0, "custom_components")

from harness import FakeEntry, FakeHass  # noqa: E402
from profiles import house  # noqa: E402

from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402

T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
PKG = Path("custom_components/heatpump_optimizer")


def detector():
    return HeatPumpOptimizerCoordinator(FakeHass(), FakeEntry(data=house(dhw=False)))._vent_cusum


def feed(c, series):
    tripped_at = None
    for i, r in enumerate(series):
        c.update(T0 + timedelta(minutes=15 * i), r)
        if c.tripped and tripped_at is None:
            tripped_at = i
    return tripped_at


def part1():
    bad = 0
    for bias in (0.0, 0.05, 0.10, 0.40):
        quiet = feed(detector(), [-bias] * 96)
        window = feed(detector(), [-bias] * 96 + [-bias - 0.5] * 4)
        ok = quiet is None and window is not None and window >= 96
        bad += not ok
        print(f"RESULT bias={bias:.2f} bias_only_trips_at={quiet} window_trips_at={window} "
              f"{'ok' if ok else 'FAIL'}")
    print(f"RESULT part1_failures={bad}")
    return bad


def part2():
    gated = set()
    rows = []
    for f in sorted(PKG.rglob("*.py")):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_learning_frozen":
                for a in ast.walk(node):
                    if isinstance(a, ast.Attribute) and a.attr == "tripped" and isinstance(a.value, ast.Attribute):
                        gated.add(a.value.attr)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                    and getattr(node.value.func, "id", None) == "Cusum":
                kw = {k.arg for k in node.value.keywords}
                for t in node.targets:
                    if isinstance(t, ast.Attribute):
                        rows.append((f.relative_to(PKG).as_posix(), t.attr, "reference_hours" in kw))
    open_seams = 0
    for rel, name, ref in rows:
        g = name in gated
        flag = "OPEN" if (g and not ref) else "ok"
        open_seams += flag == "OPEN"
        print(f"RESULT cusum {rel}:{name} gates_learning={g} referenced={ref} {flag}")
    print(f"RESULT cusums={len(rows)} open_learning_gates={open_seams}")
    return open_seams


if __name__ == "__main__":
    sys.exit(1 if (part1() + part2()) else 0)
