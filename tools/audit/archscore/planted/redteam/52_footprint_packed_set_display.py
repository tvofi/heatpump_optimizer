"""Game coord_footprint by packing: runs of adjacent call statements in the coordinator class become one set
display, ``{c1(), c2(), c3()}``, which the footprint counted as one statement (the #3218 review, round 1).
Nothing is improved; counter C25 counts the elements of a set or dict display statement."""
import ast, sys
from rt_lib import pkg, replace_nodes, coordinator_runs
p = pkg(sys.argv[1]) / "coordinator.py"
src = p.read_text()


def call(s):
    return isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and any(
        not isinstance(a, (ast.Name, ast.Constant, ast.Attribute)) for a in s.value.args)


edits = []
for run in coordinator_runs(src, call):
    edits.append((run[0], "{" + ", ".join(ast.get_source_segment(src, r.value) for r in run) + "}"))
    edits.extend((r, "") for r in run[1:])
assert edits, "the coordinator has runs of call statements"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", len(edits), "sites")
