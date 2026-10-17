"""Game layer_bound with a lazy import: silent_mode's module-level ``from .optimizer import _utc_step_starts``
moves into the one function that calls it. The module still needs the solver's module, and with it scipy, the
first time it plans; only the moment it is paid moved. A census of import-time edges read silent_mode as freed of
scipy (ARCH2-s4, round 10: the persistence layer's closure dragged the solver in this way). Counter C17."""
import ast, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "silent_mode.py"
src = p.read_text()
line = "from .optimizer import _utc_step_starts\n"
assert src.count(line) == 1
src = src.replace(line, "")
tree = ast.parse(src)
users = [f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)
         and any(isinstance(n, ast.Name) and n.id == "_utc_step_starts" for n in ast.walk(f))]
assert users
lines = src.splitlines(keepends=True)
for f in sorted(users, key=lambda f: -f.body[0].lineno):
    first = f.body[0]
    at = (f.body[1] if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and len(f.body) > 1 else first)
    indent = " " * at.col_offset
    lines.insert(at.lineno - 1, f"{indent}from .optimizer import _utc_step_starts\n")
p.write_text("".join(lines))
ast.parse(p.read_text())
print("lazy in", [f.name for f in users])
