"""D14 class sweep, P3 (round 10): every seam where a learned multiplier on a
configured thermal quantity is applied in one sibling formula and not another.

Class P3 (dev/audit/config/bugclasses.json): "a capacity floor or divisor
applied inconsistently across sibling formulas". The round-10 findings in the
class are a learned *multiplier* (the lower-floor ratio, the house scale) that
some readers of the configured nameplate apply and others do not, a learned
multiplier with no anchor against an options edit of its nameplate, and a
coercion rule implemented nine times. The barrier on record (R9-P3 arm (a))
covers max(E, c) floors only; this enumerator covers the multiplier shapes.

Arms (each an AST walk of the package; nothing is listed by hand):

  R  raw-ratio read: every Load of ``.lower_floor_heat_loss`` whose enclosing
     statement does not also name ``lower_floor_loss_ratio`` (attribute or
     ``_lower_floor_loss_ratio``). The property that owns the product is a seam
     too, reported as the owner.
  S  scale-free zone sum: every function that reads ``.upper_floor_heat_loss``
     (the two-zone total's first term) and nowhere in its body names
     ``house_heat_loss_scale`` / ``_house_heat_loss_scale`` / ``loss_scale``, does
     not call ``effective_heat_loss_coefficient`` (which applies the scale) and
     takes no ``scale`` argument.
  A  unanchored learned multiplier: every key of store.DOMAINS["thermal_learning"]
     whose last path part ends ``scale`` or ``ratio`` (a learned multiplier on a
     configured product) and has no sibling ``*_anchor`` key sharing its stem.
  F  finite-float coercion implementations: D7 ARCH-s2's SEAM_RE rule
     (shape_finite_float.py), on the tree measured, not on its pinned base.

Run (repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P3/enumerate.py [--tree DIR] [--perturb]
--tree DIR    measure another checkout's package (default: this tree).
--null        measure the clean fixture under fixture_clean/ (expected R=0 S=0 A=0 F<=1).
--perturb     copy the package to a temp dir, drop ``* self._lower_floor_loss_ratio``
              from coordinator._house_heat_loss_anchor and the
              ``house_heat_loss_anchor`` DOMAINS key (two one-line edits), and
              measure: R and A must each rise by exactly 1.
Expected at handoff/audit-r10-register 9355f107d: R=4 S=4 A=3 F=9, seams_total=33.
Machine: counts only, any box.
"""
from __future__ import annotations

import argparse
import ast
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
SEAM_RE = re.compile(r"^_?(as_float|as_num|optional_float|finite|finite_or_none|finite_float|number|at_least)$")
RATIO_NAMES = {"lower_floor_loss_ratio", "_lower_floor_loss_ratio"}
SCALE_NAMES = {"house_heat_loss_scale", "_house_heat_loss_scale", "loss_scale"}


def _names(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.Name):
            out.add(n.id)
    return out


def _parents(tree):
    par = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            par[c] = p
    return par


def _enclosing(node, par, kinds):
    while node in par:
        node = par[node]
        if isinstance(node, kinds):
            return node
    return None


def arm_r(pkg):
    rows = []
    for p in sorted(pkg.glob("*.py")):
        tree = ast.parse(p.read_text())
        par = _parents(tree)
        for n in ast.walk(tree):
            if isinstance(n, ast.Attribute) and n.attr == "lower_floor_heat_loss" and isinstance(n.ctx, ast.Load):
                stmt = _enclosing(n, par, ast.stmt)
                fn = _enclosing(n, par, (ast.FunctionDef, ast.AsyncFunctionDef))
                cls = _enclosing(fn, par, ast.ClassDef) if fn else None
                sym = ".".join(x.name for x in (cls, fn) if x) or "<module>"
                applied = bool(_names(stmt) & RATIO_NAMES)
                rows.append((f"{p.stem}.py", sym, n.lineno, "owner" if fn and fn.name == "lower_floor_heat_loss_learned"
                             else ("ratio-applied" if applied else "RAW")))
    return rows


def arm_s(pkg):
    rows = []
    for p in sorted(pkg.glob("*.py")):
        tree = ast.parse(p.read_text())
        par = _parents(tree)
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            reads = [n for n in ast.walk(fn) if isinstance(n, ast.Attribute)
                     and n.attr == "upper_floor_heat_loss" and isinstance(n.ctx, ast.Load)]
            if not reads:
                continue
            inner = [f for f in ast.walk(fn) if f is not fn and isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if any(r in set(ast.walk(f)) for f in inner for r in reads):
                continue  # attributed to the innermost function
            cls = _enclosing(fn, par, ast.ClassDef)
            sym = ".".join(x.name for x in (cls, fn) if x)
            rows.append((f"{p.stem}.py", sym, reads[0].lineno,
                         "scale-in-body" if (_names(fn) & SCALE_NAMES
                                             or "effective_heat_loss_coefficient" in _names(fn)
                                             or "scale" in {x.arg for x in fn.args.args})
                         else "NO-SCALE"))
    return rows


def arm_a(pkg):
    src = (pkg / "store.py").read_text()
    tree = ast.parse(src)
    keys = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Dict):
            for k in n.keys:
                if isinstance(k, ast.Constant) and k.value == "thermal_learning":
                    pass
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DOMAINS" for t in n.targets) \
                or isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == "DOMAINS":
            outer = n.value
            for k, v in zip(outer.keys, outer.values):
                if isinstance(k, ast.Constant) and k.value == "thermal_learning" and isinstance(v, ast.Dict):
                    for kk in v.keys:
                        if isinstance(kk, ast.Constant) and isinstance(kk.value, str):
                            keys.append(kk.value)
                        elif isinstance(kk, ast.Attribute):  # c.CONF_COP_SCALE
                            keys.append(kk.attr.lower().removeprefix("conf_"))
    anchors = {k[: -len("_anchor")] for k in keys if k.endswith("_anchor")}
    rows = []
    for k in keys:
        last = k.split("/")[-1]
        if not (last.endswith("scale") or last.endswith("ratio")):
            continue
        stem = re.sub(r"_?(scale|ratio)$", "", k.replace("/", "_"))
        rows.append(("store.py", f"DOMAINS.thermal_learning[{k!r}]", 0, "anchored" if stem in anchors else "NO-ANCHOR"))
    return rows


def arm_f(pkg):
    out, seen = [], set()
    for p in sorted(pkg.glob("*.py")):
        for fn in ast.parse(p.read_text()).body:
            if not isinstance(fn, ast.FunctionDef) or not SEAM_RE.match(fn.name):
                continue
            if fn.returns is None or "float" not in ast.unparse(fn.returns):
                continue
            first = fn.args.args[0].annotation if fn.args.args else None
            if first is not None and "Mapping" in ast.unparse(first):
                continue
            if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "float"
                       for n in ast.walk(fn)):
                continue
            if (p.stem, fn.name) in seen:
                continue
            seen.add((p.stem, fn.name))
            out.append((f"{p.stem}.py", fn.name, fn.lineno, "IMPL"))
    return out


def measure(pkg, label):
    arms = {"R": arm_r(pkg), "S": arm_s(pkg), "A": arm_a(pkg), "F": arm_f(pkg)}
    for arm, rows in arms.items():
        for r in rows:
            print(f"SEAM {arm} {r[0]}:{r[2]} {r[1]} {r[3]}")
    flagged = {
        "R": sum(r[3] == "RAW" for r in arms["R"]),
        "S": sum(r[3] == "NO-SCALE" for r in arms["S"]),
        "A": sum(r[3] == "NO-ANCHOR" for r in arms["A"]),
        "F": len(arms["F"]),
    }
    print(f"RESULT {label} " + " ".join(f"{k}={v}" for k, v in flagged.items())
          + f" seams_total={sum(len(v) for v in arms.values())}")
    return flagged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", type=Path, default=REPO)
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    if a.null:
        measure(HERE / "fixture_clean", "null")
        return 0
    pkg = a.tree / "custom_components" / "heatpump_optimizer"
    base = measure(pkg, "tree")
    if a.perturb:
        tmp = Path(tempfile.mkdtemp(prefix="sweep-p3-"))
        shutil.copytree(pkg, tmp / "pkg")
        co = tmp / "pkg" / "coordinator.py"
        t = co.read_text()
        t2 = t.replace("+ p.lower_floor_heat_loss * self._lower_floor_loss_ratio", "+ p.lower_floor_heat_loss", 1)
        st = tmp / "pkg" / "store.py"
        s = st.read_text()
        s2 = re.sub(r'\n\s*"house_heat_loss_anchor": Domain\("real", _POS, unread=\(\n[^\n]*\n', "\n", s, count=1)
        assert t2 != t and s2 != s, "perturbation site moved"
        co.write_text(t2)
        st.write_text(s2)
        pert = measure(tmp / "pkg", "perturbed")
        print(f"RESULT perturb_delta R={pert['R'] - base['R']} A={pert['A'] - base['A']} (expected 1 and 1)")
        shutil.rmtree(tmp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
