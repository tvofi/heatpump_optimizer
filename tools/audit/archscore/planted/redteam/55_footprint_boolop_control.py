"""Game coord_footprint by respelling control flow as a BoolOp: each ``if p: x = A / else: x = B`` in the coordinator
class becomes ``x = (p) and (A) or (B)`` (the #3218 review, round 2: the conditional chain's sibling). Behaviour differs
when A is falsy, which only the suite would see; the attempt asks what the footprint reads."""
import ast, sys
from rt_lib import pkg, replace_nodes
p = pkg(sys.argv[1]) / "coordinator.py"
src = p.read_text()
cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")


def one(b):
    return len(b) == 1 and isinstance(b[0], ast.Assign) and len(b[0].targets) == 1 and isinstance(b[0].targets[0], ast.Name)


def seg(n):
    return ast.get_source_segment(src, n)


edits = []
for n in ast.walk(cls):
    if isinstance(n, ast.If) and one(n.body) and one(n.orelse) \
            and n.body[0].targets[0].id == n.orelse[0].targets[0].id:
        edits.append((n, f"{n.body[0].targets[0].id} = ({seg(n.test)}) and ({seg(n.body[0].value)}) or ({seg(n.orelse[0].value)})"))
assert edits, "the coordinator has an if/else binding one name"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", len(edits), "sites")
