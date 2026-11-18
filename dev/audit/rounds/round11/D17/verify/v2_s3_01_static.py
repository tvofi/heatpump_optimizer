"""V2 for D17-s3-01: does async_run_optimization's body publish coordinator.data?

Counts, by AST, the publish calls (async_set_updated_data, async_update_listeners,
async_request_refresh, async_refresh, _build_data_dict) and `.data =` assignments
in the function body, and lists the methods it awaits (to follow one level down).
Run from the export root: python3 dev/audit/rounds/round11/D17/verify/v2_s3_01_static.py
"""
import ast
import json

src = open("custom_components/heatpump_optimizer/coordinator.py").read()
tree = ast.parse(src)
PUB = {"async_set_updated_data", "async_update_listeners", "async_request_refresh",
       "async_refresh", "_build_data_dict"}
funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef))}


def scan(name, depth=0, seen=None):
    seen = seen or set()
    if name in seen or name not in funcs or depth > 2:
        return 0, 0
    seen.add(name)
    node = funcs[name]
    calls = [n.func.attr for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
    pub = sum(c in PUB for c in calls)
    assigns = sum(1 for n in ast.walk(node) if isinstance(n, ast.Assign)
                  for t in n.targets if ast.unparse(t).endswith("self.data"))
    for c in set(calls):
        if c.startswith("_async") or c.startswith("async_"):
            p, a = scan(c, depth + 1, seen)
            pub += p
            assigns += a
    return pub, assigns


pub, assigns = scan("async_run_optimization")
print(f"RESULT s3_01_publish_calls_reachable_depth2={pub}")
print(f"RESULT s3_01_self_data_assignments_depth2={assigns}")
s = json.load(open("custom_components/heatpump_optimizer/strings.json"))
print("RESULT s3_01_strings_description=" + json.dumps(s["services"]["run_optimization"].get("description")))
