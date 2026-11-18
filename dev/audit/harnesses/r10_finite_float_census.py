"""R10-ARCH-SHAPES census (D7-s2-58): one tree's finite-float coercers, by another tree's rule.

Applies ``tests/finite_boundary.py::_finite_float_coercers`` as written at
RULE_TREE to the package under TARGET_TREE, so the head's seam rule can be
run against the base (where the rule does not yet exist) and against the head.

    python3 dev/audit/harnesses/r10_finite_float_census.py RULE_TREE TARGET_TREE

Both arguments are checkout roots (a worktree or a ``git archive`` export).
Null control: the rule asserts its own reach in ``tests/finite_boundary.py``
("the census reaches the owner and a planted sibling").
"""
import ast
import pathlib
import sys

rule_tree, target = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
mod = ast.parse((rule_tree / "tests/finite_boundary.py").read_text())
fn = next(n for n in mod.body
          if isinstance(n, ast.FunctionDef) and n.name == "_finite_float_coercers")
ns = {"ast": ast}
exec(compile(ast.Module(body=[fn], type_ignores=[]), "rule", "exec"), ns)
pkg = target / "custom_components/heatpump_optimizer"
found = sorted(ns["_finite_float_coercers"]({p.name: p.read_text() for p in sorted(pkg.glob("*.py"))}))
print(f"RESULT coercers={len(found)}")
for f in found:
    print("  ", f)
