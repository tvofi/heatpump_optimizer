"""Reviewer's own instrument: every call of the shared closures in each solve path, as
source text in order, so base and head call sites can be diffed (the 'pass
dhw_plan_power on the space path' perturbation lives here, not in the builder)."""
import ast, sys
p = sys.argv[1]; src = open(p).read(); t = ast.parse(src)
NAMES = {"objective", "objective_batch", "_space_traj", "energy_cost_of"}
for c in t.body:
    if isinstance(c, ast.ClassDef) and c.name == "HeatPumpOptimizer":
        for f in c.body:
            if isinstance(f, ast.FunctionDef) and f.name in ("_optimize_space_only", "_optimize_with_dhw"):
                nested = {id(n) for d in ast.walk(f) if isinstance(d, ast.FunctionDef) and d is not f for n in ast.walk(d)}
                calls = [n for n in ast.walk(f) if id(n) not in nested and isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in NAMES]
                refs = [n for n in ast.walk(f) if id(n) not in nested and isinstance(n, ast.Name) and n.id in NAMES and isinstance(n.ctx, ast.Load)]
                calls.sort(key=lambda n: (n.lineno, n.col_offset))
                for n in calls: print(f.name, "CALL", " ".join(ast.get_source_segment(src, n).split()))
                print(f.name, "LOADS", sorted(n.id for n in refs))
