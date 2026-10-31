"""EG-B5 (#1743): per-class logical statements (ast.stmt nodes below the class), methods and lines.
    python3 tools/audit/round9/EG-B5/class_stmts.py BASE HEAD
"""
import ast, subprocess, sys
def cls_stats(ref, path, name):
    src = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=True).stdout
    for n in ast.parse(src).body:
        if isinstance(n, ast.ClassDef) and n.name == name:
            stmts = sum(1 for x in ast.walk(n) if isinstance(x, ast.stmt)) - 1
            meths = sum(1 for x in n.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)))
            return f"{name} @ {ref[:9]}: {stmts} logical statements (ast.stmt nodes below the class), {meths} methods, {n.end_lineno - n.lineno + 1} lines"
    return f"{name} @ {ref[:9]}: absent"
base, head = sys.argv[1:3]
P = "custom_components/heatpump_optimizer/"
print(cls_stats(base, P + "optimizer.py", "HeatPumpOptimizer"))
print(cls_stats(head, P + "optimizer.py", "HeatPumpOptimizer"))
try: print(cls_stats(base, P + "dhw_planner.py", "DhwPlanner"))
except subprocess.CalledProcessError: print("DhwPlanner @ base: no dhw_planner.py")
print(cls_stats(head, P + "dhw_planner.py", "DhwPlanner"))
