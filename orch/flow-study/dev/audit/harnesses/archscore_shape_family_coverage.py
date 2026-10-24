#!/usr/bin/env python3
"""ARCH-s2's payload-guard seam rule, and how many of its implementations archscore's shape census joins.

WHY IT EXISTS. R10-ARCHSCORE-COVERAGE item 6 (#2259) asks for a census of N implementations of one rule.
Part 5's `shape_copies` (`tools/audit/archscore/metrics/shapes.py`, counter C23) is that census, and this
is its companion: it applies the finder's own rule -- `shape_payload_guard.py`'s `family()` from ARCH-s2,
copied verbatim below -- to `sensor.py` at a ref, and reports how many of the rule's implementations fall
in a shape class of two or more. An instrument with no `metrics/shapes.py` has no census, so `joined`
reads 0 there: that is the base end of the figure. It also pins part 5's mutant M3 (strings kept, not
abstracted), which joins none.

    python3 dev/audit/harnesses/archscore_shape_family_coverage.py <worktree> <ref>

`<worktree>` supplies the instrument (`<worktree>/tools/audit/archscore`); `<ref>` is the tree measured,
read by `git archive` from `<worktree>`'s repository. RESULT lines: `implementations` (functions the
finder's rule names), `joined` (those in a shape class of 2+), `classes_spanned` (the classes they fall in).

Measured (R10-ARCHSCORE-COVERAGE part 5, #2401, 2026-10-18), ref `554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef`
(ARCH-s2's baseline): with the part-5 instrument, implementations=35, joined=26, classes_spanned=3; with an
instrument that has no shape census, joined=0. The 9 not joined are spelled differently, which a census on
spellings cannot see.
"""
import ast, subprocess, sys, tempfile
from pathlib import Path
WT, REF = Path(sys.argv[1]), sys.argv[2]
sys.path.insert(0, str(WT / "tools" / "audit"))

def family(fn):
    ret = [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None
           and not (isinstance(n.value, ast.Constant) and n.value.value is None)]
    if not ret:
        return None
    src = ast.unparse(ret[0].value)
    body = ast.unparse(fn)
    if "self.coordinator.data" not in body and "self._data()" not in body:
        return None
    if src.startswith("round(") and "is not None" in src:
        return "round_if_not_none"
    if src.startswith("round(") and "isinstance" in src:
        return "round_if_number"
    if " if isinstance(" in src and "bool" not in src:
        return "isinstance_number"
    if src.startswith("_as_float("):
        return "_as_float"
    return None

with tempfile.TemporaryDirectory() as t:
    arch = subprocess.run(["git", "-C", str(WT), "archive", REF, "custom_components"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", t], input=arch, check=True)
    sensor = Path(t) / "custom_components/heatpump_optimizer/sensor.py"
    impl = set()
    for cls in ast.parse(sensor.read_text()).body:
        if isinstance(cls, ast.ClassDef):
            for f in cls.body:
                if isinstance(f, ast.FunctionDef) and f.name == "native_value" and family(f):
                    impl.add(f"sensor:{cls.name}.native_value")
    try:
        from archscore.metrics import shapes
        groups = shapes.classes(Path(t))
    except ImportError:
        groups = []
    joined = {m for g in groups for m in g} & impl
    spanned = sum(1 for g in groups if impl & set(g))
    print(f"RESULT implementations={len(impl)} count")
    print(f"RESULT joined={len(joined)} count")
    print(f"RESULT classes_spanned={spanned} count")
