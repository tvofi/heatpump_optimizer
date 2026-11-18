"""Game coord_footprint by packing: runs of adjacent plain assignments in the coordinator class become a for
loop over a one-element literal, ``for a, b, c in [(e1, e2, e3,)]: "_"``, which the footprint counted as one
statement whatever the loop unpacked (the #3218 review, round 1). Nothing is improved; counter C25 reads a loop
over a literal display as the pairs of target and element it spells."""
import ast, sys
from rt_lib import pkg, replace_nodes, coordinator_runs
p = pkg(sys.argv[1]) / "coordinator.py"
src = p.read_text()


def plain(s):
    return (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name)
            and isinstance(s.value, (ast.BinOp, ast.Compare, ast.IfExp, ast.BoolOp)))


edits = []
for run in coordinator_runs(src, plain):
    lhs = ", ".join(r.targets[0].id for r in run)
    rhs = ", ".join(ast.get_source_segment(src, r.value) for r in run)
    edits.append((run[0], f'for {lhs} in [({rhs},)]: "_"'))
    edits.extend((r, "") for r in run[1:])
assert edits, "the coordinator has runs of plain assignments"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", len(edits), "sites")
