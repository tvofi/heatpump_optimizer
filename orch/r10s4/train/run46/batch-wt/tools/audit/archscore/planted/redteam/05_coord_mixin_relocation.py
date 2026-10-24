"""Game coord_footprint_v1 (and everything keyed on the coordinator class): move every method
of HeatPumpOptimizerCoordinator except __init__ -- and the two plain class constants -- verbatim
into a base class _CoordinatorBody in the same module, which the coordinator now inherits
first. The runtime object, its MRO lookups and every line of logic are unchanged.
Variants: argv[2] == "private" moves only the _private methods; argv[2] == "all" moves the
whole body (incl. __init__ and the hub descriptors) into _CoordinatorBody(DataUpdateCoordinator)
and leaves HeatPumpOptimizerCoordinator(_CoordinatorBody) with just its docstring."""
import ast, sys
from rt_lib import pkg
root = sys.argv[1]
only_private = len(sys.argv) > 2 and sys.argv[2] == "private"
everything = len(sys.argv) > 2 and sys.argv[2] == "all"
p = pkg(root) / "coordinator.py"
src = p.read_text()
lines = src.splitlines(keepends=True)
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")


def span(s):
    start = min([s.lineno] + [d.lineno for d in getattr(s, "decorator_list", [])])
    return start, s.end_lineno


moved = []
for s in cls.body:
    if everything and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)):
        moved.append(span(s))
        continue
    if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)) and s.name != "__init__":
        if only_private and not s.name.startswith("_"):
            continue
        moved.append(span(s))
    elif isinstance(s, ast.Assign) and isinstance(s.value, ast.Constant | ast.Dict) and not only_private:
        moved.append(span(s))
# include comment lines immediately above each moved member
def grow(a):
    while a > 1 and lines[a - 2].strip().startswith("#"):
        a -= 1
    return a
moved = [(grow(a), b) for a, b in moved]
body = []
keep = set()
for a, b in moved:
    body.append("".join(lines[a - 1:b]) + "\n")
    keep.update(range(a, b + 1))
new_cls_lines = [ln for i, ln in enumerate(lines[cls.lineno - 1:cls.end_lineno], cls.lineno) if i not in keep]
header = cls.lineno
new_cls = "".join(new_cls_lines).replace(
    "class HeatPumpOptimizerCoordinator(DataUpdateCoordinator):",
    "class HeatPumpOptimizerCoordinator(_CoordinatorBody):" if everything else
    "class HeatPumpOptimizerCoordinator(_CoordinatorBody, DataUpdateCoordinator):", 1)
mixin = (("class _CoordinatorBody(DataUpdateCoordinator):\n" if everything else 'class _CoordinatorBody:\n')
         + '    """The coordinator\'s behaviour (mixed into HeatPumpOptimizerCoordinator)."""\n\n'
         + "".join(body) + "\n\n")
cstart = grow(min([cls.lineno] + [d.lineno for d in cls.decorator_list]))
out = "".join(lines[:cstart - 1]) + mixin + "".join(lines[cstart - 1:cls.lineno - 1]) + new_cls + "".join(lines[cls.end_lineno:])
p.write_text(out)
print("moved members", len(moved))
