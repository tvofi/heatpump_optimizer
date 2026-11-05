"""Game coord_footprint by packing: runs of adjacent plain assignments in the coordinator class become
one tuple-unpack of a generator, ``a, b, c = (x for x in (e1, e2, e3))``, which the footprint counted as
one statement (the #3185 review, a2e21972: 6 of the 7 statements behind its score movement). Nothing is
improved and the logic is the same; counter C25 reads a packed statement as the plain ones it spells."""
import ast, sys
from rt_lib import pkg, replace_nodes
p = pkg(sys.argv[1]) / "coordinator.py"
src = p.read_text()
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")


def plain(s):
    return (isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name)
            and isinstance(s.value, (ast.BinOp, ast.Compare, ast.IfExp, ast.BoolOp)))


def names(e):
    return {n.id for n in ast.walk(e) if isinstance(n, ast.Name)}


edits = []
for fn in ast.walk(cls):
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    for body in [fn.body] + [b for n in ast.walk(fn) for b in (getattr(n, "body", None), getattr(n, "orelse", None)) if isinstance(b, list)]:
        run = []
        for s in body + [None]:
            # a run extends while the statement reads no name an earlier statement of the run binds
            if s is not None and plain(s) and not (names(s.value) & {r.targets[0].id for r in run}) \
                    and s.targets[0].id not in {n for r in run for n in names(r.value)}:
                run.append(s)
                continue
            if len(run) >= 2:
                lhs = ", ".join(r.targets[0].id for r in run)
                rhs = ", ".join(ast.get_source_segment(src, r.value) for r in run)
                edits.append((run[0], f"for {lhs} in [({rhs},)]: \"_\""))
                edits.extend((r, "") for r in run[1:])
            run = [s] if s is not None and plain(s) else []
edits = [e for i, e in enumerate(edits) if all(e[0] is not f[0] for f in edits[:i])]
assert edits, "the coordinator has runs of plain assignments"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", sum(1 for _, t in edits if t), "runs")
