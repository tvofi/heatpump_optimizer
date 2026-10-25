"""Reviewer's own driver (not the finder's): apply HEAD's tests/finite_boundary.py::_finite_float_coercers
to each tree's custom_components/heatpump_optimizer/*.py. Usage: python3 ff_census_mine.py HEAD_TREE TREE"""
import ast, sys, pathlib
head, tree = sys.argv[1], sys.argv[2]
src = pathlib.Path(head, "tests/finite_boundary.py").read_text()
fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "_finite_float_coercers")
ns = {"ast": ast}; exec(compile(ast.Module(body=[fn], type_ignores=[]), "fb", "exec"), ns)
pkg = pathlib.Path(tree, "custom_components/heatpump_optimizer")
sources = {p.name: p.read_text() for p in sorted(pkg.glob("*.py"))}
found = sorted(ns["_finite_float_coercers"](sources))
print(f"RESULT finite_float_coercers={len(found)} count")
for f in found: print("  ", f)
