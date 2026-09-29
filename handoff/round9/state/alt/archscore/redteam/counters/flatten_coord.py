#!/usr/bin/env python3
"""C4 normaliser: the coordinator is its MRO, not one class node.

    python3 flatten_coord.py SRC_ROOT DST_ROOT

Copies SRC_ROOT's package to DST_ROOT and, in coordinator.py, inlines every package-local base
class of HeatPumpOptimizerCoordinator (defined in coordinator.py, recursively) into the coordinator
class body -- members the coordinator itself defines win, as the MRO would -- and replaces the
coordinator's bases with the bases' external bases. Every metric keyed on the coordinator class
(footprint, hub roots, the payload producer, async-method rules, writers) is then measured on
the class the runtime actually builds. Identity on a tree whose coordinator has no local base.
"""
import ast, shutil, sys
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src / PKG, dst / PKG, ignore=shutil.ignore_patterns("__pycache__"))
if (src / "tests").exists():
    shutil.copytree(src / "tests", dst / "tests", ignore=shutil.ignore_patterns("__pycache__", "fixtures", "golden", "replay", "mutation_ledger"))
p = dst / PKG / "coordinator.py"
text = p.read_text()
tree = ast.parse(text)
classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
coord = classes["HeatPumpOptimizerCoordinator"]
lines = text.splitlines(keepends=True)


def names(c):
    out = set()
    for s in c.body:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(s.name)
        elif isinstance(s, ast.Assign):
            out |= {t.id for t in s.targets if isinstance(t, ast.Name)}
        elif isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name):
            out.add(s.target.id)
    return out


def src_of(s):
    a = min([s.lineno] + [d.lineno for d in getattr(s, "decorator_list", [])])
    return "".join(lines[a - 1:s.end_lineno])


have = names(coord)
extra, ext_bases, drop = [], [], []
todo = [ast.unparse(b) for b in coord.bases]
while todo:
    b = todo.pop(0)
    if b in classes and b != coord.name:
        base = classes[b]
        drop.append(base)
        for s in base.body:
            if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant):
                continue
            nm = names(type("X", (), {"body": [s]}))
            if nm and nm <= have:
                continue
            have |= nm
            extra.append(src_of(s))
        todo += [ast.unparse(x) for x in base.bases]
    elif b not in ext_bases:
        ext_bases.append(b)
if drop:
    header = f"class HeatPumpOptimizerCoordinator({', '.join(ext_bases)}):\n"
    body_start = coord.body[0].lineno
    new = header + "".join(lines[body_start - 1:coord.end_lineno]) + "\n" + "".join(extra)
    cut = {(min([c.lineno] + [d.lineno for d in c.decorator_list]), c.end_lineno) for c in drop}
    out, i = [], 1
    spans = sorted(cut | {(min([coord.lineno] + [d.lineno for d in coord.decorator_list]), coord.end_lineno)})
    for a, b in spans:
        out.append("".join(lines[i - 1:a - 1]))
        if (a, b) not in cut:
            out.append(new)
        i = b + 1
    out.append("".join(lines[i - 1:]))
    p.write_text("".join(out))
print(f"inlined {len(drop)} local base(s), {len(extra)} member(s)")
