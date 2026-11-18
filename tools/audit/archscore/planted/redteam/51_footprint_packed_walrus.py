"""Game coord_footprint by packing: runs of adjacent plain assignments in the coordinator class become one call
over walrus bindings, ``repr((a := e1, b := e2, c := e3))``, which the footprint counted as one statement (the
#3218 review, round 1). Nothing is improved; counter C25 charges each walrus a statement."""
import ast, sys
from rt_lib import pkg, replace_nodes, coordinator_runs
p = pkg(sys.argv[1]) / "coordinator.py"
src = p.read_text()


def plain(s):
    return (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name)
            and isinstance(s.value, (ast.BinOp, ast.Compare, ast.IfExp, ast.BoolOp)))


edits = []
for run in coordinator_runs(src, plain):
    inner = ", ".join(f"{r.targets[0].id} := ({ast.get_source_segment(src, r.value)})" for r in run)
    edits.append((run[0], f"repr(({inner}))"))
    edits.extend((r, "") for r in run[1:])
assert edits, "the coordinator has runs of plain assignments"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", len(edits), "sites")
