"""Game untyped_payload_keys: a TypedDict declaring every produced key as Any (total=False),
attached only to _async_update_data's return annotation. The coordinator stays
DataUpdateCoordinator (unparameterised), so no consumer read is checked against it."""
import ast, sys
from rt_lib import pkg, metric, replace_nodes
root = sys.argv[1]
keys = metric("untyped_payload_keys", root)["details"]["untyped"]
p = pkg(root) / "coordinator.py"
src = p.read_text()
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
fn = next(n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "_async_update_data")
replace_nodes(p, [(fn.returns, "CoordinatorPayload")])
assert all(k.isidentifier() for k in keys)
body = "".join(f"    {k}: Any\n" for k in keys)
decl = ("\n\nfrom typing import TypedDict  # noqa: E402\n\n\nclass CoordinatorPayload(TypedDict, total=False):\n"
        '    """Every key coordinator.data carries."""\n\n' + body + "\n")
src = p.read_text()
i = src.index("\nclass HeatPumpOptimizerCoordinator(")
# put the declaration right before the class
j = src.rfind("\n\n", 0, i)
p.write_text(src[:j] + decl + src[j:])
print("keys", len(keys))
