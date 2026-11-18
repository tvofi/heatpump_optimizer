#!/usr/bin/env python3
"""D7-s1 / D7.M1: the structural ratchet cannot see coordinator state reached
through a module-level ``_helper(self, ...)`` -- the shape docs/HANDOVER.md
records as refused -- so it rewards that move and refuses its reversal.

Metric (one line): rows of tests/structure.py:measure() whose value RISES when
one module-level helper that the coordinator calls as ``f(self, ...)`` is
inlined byte-for-byte back into the class as a method (coordinator_loc and
coordinator_methods excluded: an inlined method legitimately costs those).

Count key: the values ``structure.measure()`` returns for the transformed copy,
minus its values for the untransformed copy -- the production seam is the
ratchet itself; the harness only moves source text between two shapes that
execute identically.

Also printed: the seam rule -- every module-level function in the package the
coordinator class calls with ``self`` as an argument, and the coordinator-state
attribute references and coordinator-method calls those bodies make through
that parameter (plus ``getattr(coord, "_ctx", coord)`` aliases), none of which
any structure.py metric counts.

Run (repository root):
    PYTHONPATH=tests/hastub /home/claude/venv/bin/python tools/audit/round9/D7/s1/helper_escape.py
    ... --helper _warm_seeded   # perturbation arm: a helper whose refs cross no seam
    ... --all                   # leave-one-out grid over the 10 coordinator.py helpers

Headline number: inline__fold_flow_lift_cut_delta (sum of cut_* and
cross_seam_edges movement when _fold_flow_lift is inlined).
Expected at 1936d5ca (exact, counts): helpers=11, helper_state_refs=30,
helper_coord_method_calls=8, inline__fold_flow_lift_cut_delta=8 (rows_up=4);
--helper _warm_seeded: cut_delta=0; --all: cells=10, sum=36, min=0, max=12,
sum_drop_max=24, nonzero=8.
Machine: cloud container (linux), baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1.
Writes only under a tempfile.mkdtemp() root.
"""
from __future__ import annotations

import os

for _pin in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_pin, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "tests"))
import structure  # noqa: E402

PKG_REL = Path("custom_components/heatpump_optimizer")
CLS = structure.COORDINATOR_CLASS_NAME
EXEMPT = {"coordinator_loc", "coordinator_methods", "max_class_loc"}


def helpers_called_with_self(root: Path) -> dict[str, tuple[str, int, int, int]]:
    """name -> (module, param index, state refs, coord-method calls)."""
    out = {}
    coord_src = (root / PKG_REL / "coordinator.py").read_text()
    tree = ast.parse(coord_src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == CLS)
    methods = {m.name for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
    tops = {}
    for path in sorted((root / PKG_REL).glob("*.py")):
        t = ast.parse(path.read_text())
        for n in t.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                tops.setdefault(n.name, (path.name, n))
    for node in ast.walk(cls):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in tops:
            for i, a in enumerate(node.args):
                if isinstance(a, ast.Name) and a.id == "self":
                    mod, fn = tops[node.func.id]
                    p = fn.args.args[i].arg
                    roots = {p}
                    for m in ast.walk(fn):  # ctx = getattr(coord, "_ctx", coord)
                        if (isinstance(m, ast.Assign) and isinstance(m.value, ast.Call)
                                and isinstance(m.value.func, ast.Name) and m.value.func.id == "getattr"
                                and any(isinstance(x, ast.Name) and x.id == p for x in m.value.args)):
                            roots.update(t.id for t in m.targets if isinstance(t, ast.Name))
                    refs = calls = 0
                    for m in ast.walk(fn):
                        if isinstance(m, ast.Attribute) and isinstance(m.value, ast.Name) and m.value.id in roots:
                            if m.attr in methods:
                                calls += 1
                            elif m.attr != "_ctx":
                                refs += 1
                    out[node.func.id] = (mod, i, refs, calls)
    return out


def inline(root: Path, name: str) -> None:
    """Move coordinator.py's top-level ``name(coord, ...)`` into the class as a method."""
    path = root / PKG_REL / "coordinator.py"
    src = path.read_text()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    fn = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == CLS)
    param = fn.args.args[0].arg
    start = min([d.lineno for d in fn.decorator_list] + [fn.lineno])
    body = lines[start - 1:fn.end_lineno]
    body = [re.sub(rf"\b{param}\b", "self", ln) for ln in body]
    body = [("    " + ln) if ln.strip() else ln for ln in body]
    cls_end = cls.end_lineno
    new = lines[:start - 1] + lines[fn.end_lineno:cls_end] + ["\n"] + body + lines[cls_end:]
    text = "".join(new)
    text = re.sub(rf"(?<![\w.]){name}\(self,\s*", f"self.{name}(", text)
    text = re.sub(rf"(?<![\w.]){name}\(self\)", f"self.{name}()", text)
    path.write_text(text)
    ast.parse(text)
    seam_file = root / "tests" / "seam_map.json"
    doc = json.loads(seam_file.read_text())
    doc["seams"][name] = structure.regex_seam(name)
    seam_file.write_text(json.dumps(doc))


def copy_tree(dst: Path) -> None:
    shutil.copytree(ROOT / PKG_REL, dst / PKG_REL)
    (dst / "tests").mkdir()
    shutil.copy(ROOT / "tests" / "seam_map.json", dst / "tests" / "seam_map.json")


def measure_at(root: Path) -> dict:
    structure.REPO_ROOT = root
    structure.PACKAGE_DIR = root / PKG_REL
    structure.SEAM_MAP_FILE = root / "tests" / "seam_map.json"
    return structure.measure()["metrics"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--helper", default="_fold_flow_lift")
    ap.add_argument("--all", action="store_true",
                    help="leave-one-out grid: inline each coordinator.py helper in turn")
    args = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    tmp = Path(tempfile.mkdtemp(prefix="d7s1_helper_"))
    try:
        base, arm = tmp / "base", tmp / "arm"
        copy_tree(base)
        copy_tree(arm)
        helpers = helpers_called_with_self(base)
        for n, (mod, i, refs, calls) in sorted(helpers.items()):
            print(f"  seam  {mod}:{n}  self-arg#{i}  state_refs={refs}  coord_method_calls={calls}")
        print(f"RESULT helpers={len(helpers)} count")
        print(f"RESULT helper_state_refs={sum(v[2] for v in helpers.values())} count")
        print(f"RESULT helper_coord_method_calls={sum(v[3] for v in helpers.values())} count")
        m0 = measure_at(base)
        if args.all:
            cells = {}
            for n, (mod, *_r) in sorted(helpers.items()):
                if mod != "coordinator.py":
                    continue
                cell = tmp / f"cell{n}"
                copy_tree(cell)
                inline(cell, n)
                m = measure_at(cell)
                cells[n] = sum(m[k] - m0[k] for k in m0 if k.startswith("cut_") or k == "cross_seam_edges")
                print(f"  cell {n}: cut_delta={cells[n]}")
            vals = sorted(cells.values())
            print(f"RESULT grid_cells={len(vals)} count")
            print(f"RESULT grid_cut_delta_sum={sum(vals)} count")
            print(f"RESULT grid_cut_delta_min={vals[0]} count")
            print(f"RESULT grid_cut_delta_max={vals[-1]} count")
            print(f"RESULT grid_cut_delta_sum_drop_max={sum(vals) - vals[-1]} count")
            print(f"RESULT grid_cells_nonzero={sum(1 for v in vals if v > 0)} count")
        inline(arm, args.helper)
        m1 = measure_at(arm)
        up = []
        for k in sorted(m0):
            d = m1[k] - m0[k]
            if d:
                print(f"  {k:36s} {m0[k]} -> {m1[k]}  ({d:+d})")
            if d > 0 and k not in EXEMPT:
                up.append(k)
        print(f"  rows rising (ratchet would exit 1 on each): {up}")
        print(f"RESULT inline_{args.helper}_rows_up={len(up)} count")
        print(f"RESULT inline_{args.helper}_cut_delta="
              f"{sum(m1[k]-m0[k] for k in m0 if k.startswith('cut_') or k == 'cross_seam_edges')} count")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    c1, t1 = time.process_time(), time.thread_time()
    print(f"RESULT thread_factor={(c1-c0)/max(t1-t0,1e-9):.3f} ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = [ln for ln in open("/proc/vmstat") if ln.startswith("pswpin")][0].split()[1]
    except OSError:
        sw = "n/a"
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
