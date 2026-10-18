"""Game literal_clone_copies by hoisting a value into a local: in each function that spells
``_number(1, 24, 1, slider=True)`` the upper bound becomes a local, ``last_hour = 24``, set once at the top, and
the call reads ``_number(1, last_hour, 1, slider=True)``. A census that treated any local as runtime data read the
call as no declaration at all. Counter C21."""
import ast, sys
from rt_lib import pkg
root = sys.argv[1]
p = pkg(root) / "config_flow.py"
src = p.read_text()
tree = ast.parse(src)
spelled = "_number(1, 24, 1, slider=True)"
lines = src.splitlines(keepends=True)
hits = []
for f in ast.walk(tree):
    if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and spelled in ast.get_source_segment(src, f):
        if not any(isinstance(g, (ast.FunctionDef, ast.AsyncFunctionDef)) and g is not f and spelled in ast.get_source_segment(src, g) for g in ast.walk(f)):
            hits.append(f)
assert hits, "no function spells it"
for f in sorted(hits, key=lambda f: -f.lineno):
    a, b = f.body[0].lineno, f.end_lineno
    body = "".join(lines[a - 1:b]).replace(spelled, "_number(1, last_hour, 1, slider=True)")
    indent = " " * f.body[0].col_offset
    lines[a - 1:b] = [indent + "last_hour = 24\n", body]
p.write_text("".join(lines))
ast.parse(p.read_text())
print("hoisted in", len(hits))
