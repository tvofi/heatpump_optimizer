"""Class search: stub class members missing vs upstream, not declared in `absent`.
Run twice: emit (stub) then diff (real)."""
import importlib, inspect, json, sys
sys.path.insert(0, "tests")
import ha_contract as hc
mode, path = sys.argv[1], sys.argv[2]
def members(key):
    mod, name = key.rsplit(".", 1)
    try:
        obj = getattr(importlib.import_module(mod), name)
    except Exception as err:
        return None
    if not inspect.isclass(obj):
        return None
    return sorted(n for n in dir(obj) if not n.startswith("_"))
if mode == "emit":
    json.dump({k: members(k) for k in hc.INVENTORY}, open(path, "w"))
else:
    stub = json.load(open(path)); tot = 0
    for k, e in hc.INVENTORY.items():
        s = stub.get(k); r = members(k)
        if s is None or r is None or e.disposition not in (hc.FAITHFUL, hc.SIMPLIFIED):
            continue
        und = sorted(set(r) - set(s) - set(e.absent))
        if und:
            tot += len(und); print(f"{e.disposition:10} {k}: {und}")
    print("undeclared_missing_members", tot)
if mode == "reach":
    import ast, pathlib
    used = set()
    for p in pathlib.Path("custom_components").rglob("*.py"):
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n, ast.Attribute): used.add(n.attr)
            elif isinstance(n, ast.keyword) and n.arg: used.add(n.arg)
    stub = json.load(open(path)); tot = 0
    for k, e in hc.INVENTORY.items():
        s = stub.get(k); r = members(k)
        if s is None or r is None or e.disposition not in (hc.FAITHFUL, hc.SIMPLIFIED):
            continue
        und = sorted((set(r) - set(s) - set(e.absent)) & used)
        if und:
            tot += len(und); print(f"REACH {e.disposition:10} {k}: {und}")
    print("reachable_undeclared_missing_members", tot)
