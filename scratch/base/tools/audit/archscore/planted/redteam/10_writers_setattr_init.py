"""Game a1_coord_writers_multi: every plain ``self.X = v`` (and ``self.X: T = v``) in the
coordinator's __init__ and _init_* methods is re-spelled ``setattr(self, "X", v)``. Same
writes, same descriptors; the attribute declarations disappear from view (mypy loses the
declared types), and the construction phase stops being a 'writer'."""
import ast, sys
from rt_lib import pkg, replace_nodes, seg
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
edits = []
for fn in cls.body:
    if not (isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and (fn.name == "__init__" or fn.name.startswith("_init_"))):
        continue
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            t = n.targets[0]
        elif isinstance(n, ast.AnnAssign) and n.value is not None:
            t = n.target
        else:
            continue
        if isinstance(n.value, ast.Call):
            continue  # constructions stay (the variant that also re-spelled them tripped the gate)
        if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self":
            edits.append((n, f'setattr(self, "{t.attr}", {seg(src, n.value)})'))
print("rewritten", replace_nodes(p, edits))
