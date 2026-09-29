"""Candidate guard for the pass-through chain: functions with > 10 parameters (self excluded)."""
import ast, sys, pathlib
wt = pathlib.Path(sys.argv[1])
n = 0; worst = 0
for p in sorted((wt / "custom_components/heatpump_optimizer").rglob("*.py")):
    for fn in ast.walk(ast.parse(p.read_text())):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            k = len([a for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs if a.arg not in ("self", "cls")])
            n += k > 10; worst = max(worst, k)
print(n, worst)
