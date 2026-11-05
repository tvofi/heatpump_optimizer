"""Game coord_footprint by nesting the chain in the body arm: each ``if p: x = A / elif q: x = B / else: x = C`` in the
coordinator class becomes ``x = ((A) if (p) else (B)) if (p) or (q) else (C)``, the same semantics with the tests read
again. The chain followed only ``orelse``, so this read as one statement against the five of the if/elif/else (the
#3218 review, round 2). Counter C25 reads every ``IfExp`` reachable through ``body`` and ``orelse``."""
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
    if isinstance(n, ast.If) and len(n.orelse) == 1 and isinstance(n.orelse[0], ast.If) and n.orelse[0].orelse:
        e = n.orelse[0]
        if one(n.body) and one(e.body) and one(e.orelse) \
                and n.body[0].targets[0].id == e.body[0].targets[0].id == e.orelse[0].targets[0].id:
            edits.append((n, f"{n.body[0].targets[0].id} = (({seg(n.body[0].value)}) if ({seg(n.test)}) else ({seg(e.body[0].value)})) if ({seg(n.test)}) or ({seg(e.test)}) else ({seg(e.orelse[0].value)})"))
assert edits, "the coordinator has an if/elif/else binding one name"
replace_nodes(p, edits)
ast.parse(p.read_text())
print("packed", len(edits), "sites")
