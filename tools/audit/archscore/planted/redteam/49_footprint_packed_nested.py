"""Game coord_footprint by packing: runs of adjacent plain assignments in the coordinator class become one
nested tuple pair, ``a, (b, c) = (e1), ((e2), (e3))``, which the footprint's top-level pairing counted as two
statements for three (the #3218 review, round 1). Nothing is improved; counter C25 pairs a nested target with
its nested value, so the plain statements are counted."""
import ast, sys
from rt_lib import pkg, replace_nodes, coordinator_runs
p = pkg(sys.argv[1]) / "coordinator.py"
src = p.read_text()


def plain(s):
    return (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name)
            and isinstance(s.value, (ast.BinOp, ast.Compare, ast.IfExp, ast.BoolOp)))


def nest(xs):
    return xs[0] if len(xs) == 1 else f"({xs[0]}, {nest(xs[1:])})"


edits = []
for run in coordinator_runs(src, plain):
    lhs = nest([r.targets[0].id for r in run])
    rhs = nest(["(" + ast.get_source_segment(src, r.value) + ")" for r in run])
    edits.append((run[0], f"{lhs[1:-1]} = {rhs[1:-1]}"))
    edits.extend((r, "") for r in run[1:])
assert edits, "the coordinator has runs of plain assignments"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", len(edits), "sites")
