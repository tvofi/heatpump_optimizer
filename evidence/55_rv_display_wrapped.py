"""Reviewer plant (#3218 round 2): the bare-display rule (attempt 52) re-spelled through a call. Runs of adjacent
expression statements in the coordinator class become ``list((c1, c2, ...))``: a display that is an argument, not
the statement, so C25's bare-display rule does not see it. Nothing is improved."""
import ast, sys
from rt_lib import pkg, replace_nodes, coordinator_runs
p = pkg(sys.argv[1]) / "coordinator.py"
src = p.read_text()


def plain(s):
    return isinstance(s, ast.Expr) and isinstance(s.value, (ast.Call, ast.Await)) and not isinstance(s.value, ast.Await)


edits = []
for run in coordinator_runs(src, plain, independent=False):
    edits.append((run[0], "list((" + ", ".join(ast.get_source_segment(src, r.value) for r in run) + ",))"))
    edits.extend((r, "") for r in run[1:])
assert edits, "the coordinator has runs of call statements"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", len(edits), "sites")
