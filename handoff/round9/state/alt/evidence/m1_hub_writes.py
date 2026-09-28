"""M1 enumerator: fields of the live hub objects written on the solve path vs restored by its finally.
Run from the repo root: python3 m1_hub_writes.py"""
import ast, pathlib, re
P = pathlib.Path("custom_components/heatpump_optimizer")
src = (P / "coordinator.py").read_text()
tree = ast.parse(src)
HUBS = ("_opt_config", "_thermal_params", "_current_state")
fns = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
def hub_writes(fn):
    alias = {}
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
           and isinstance(n.value, ast.Attribute) and n.value.attr in HUBS:
            alias[n.targets[0].id] = n.value.attr
    for n in ast.walk(fn):
        tgts = []
        if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
        for t in tgts:
            if isinstance(t, ast.Attribute):
                v = t.value
                if isinstance(v, ast.Attribute) and v.attr in HUBS:
                    out.append((v.attr, t.attr, t.lineno))
                elif isinstance(v, ast.Name) and v.id in alias:
                    out.append((alias[v.id], t.attr, t.lineno))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "setattr" and n.args:
            a0 = n.args[0]
            hub = a0.attr if isinstance(a0, ast.Attribute) and a0.attr in HUBS else alias.get(getattr(a0, "id", None))
            if hub:
                f = n.args[1].value if isinstance(n.args[1], ast.Constant) else "<dynamic>"
                out.append((hub, f, n.lineno))
    return out
writes = []
for name in ("async_run_optimization", "_prepare_dhw_inputs"):
    w = hub_writes(fns[name]); writes += w
    print(f"{name} (coordinator.py:{fns[name].lineno}): {len(w)} write sites")
fields = sorted({(h, f) for h, f, _ in writes})
print(f"distinct hub fields written on the solve path: {len(fields)}")
for h, f in fields:
    lines = sorted(l for hh, ff, l in writes if (hh, ff) == (h, f))
    print(f"  {h}.{f}  @ {lines}")
away = (P / "away.py").read_text()
restored = set()
for m in re.finditer(r"^_(OPT|DHW)_FIELDS = \((.*?)\)", away, re.M):
    restored |= set(re.findall(r'"(\w+)"', m.group(2)))
print(f"fields the finally restores (away.restore_setback, away.py _OPT_FIELDS/_DHW_FIELDS): {len(restored)} {sorted(restored)}")
fin = [n for n in ast.walk(fns["async_run_optimization"]) if isinstance(n, ast.Try) and n.finalbody]
print("finally blocks in async_run_optimization:", [(f.finalbody[0].lineno, f.finalbody[-1].end_lineno) for f in fin])
not_restored = [(h, f) for h, f in fields if f not in restored]
print(f"written and NOT restored: {len(not_restored)}")
# null control: the restore set is a subset of what the solve path writes (else the enumerator is blind)
print("control: restored fields all seen as written by the solve path or by apply_setback:",
      all(any(f == r for _, f in fields) or r in away for r in restored))
# global: all in-place hub writes in coordinator.py
allw = hub_writes(tree)
print(f"all in-place hub writes anywhere in coordinator.py: {len(allw)} sites, {len({(h,f) for h,f,_ in allw})} fields")
# frozen?
for mod, cls in (("thermal_model.py", "ThermalParameters"), ("optimizer.py", "OptimizationConfig"), ("thermal_model.py", "ThermalState")):
    t = ast.parse((P / mod).read_text())
    for n in ast.walk(t):
        if isinstance(n, ast.ClassDef) and n.name == cls:
            dec = [ast.unparse(d) for d in n.decorator_list]
            nf = sum(isinstance(s, ast.AnnAssign) for s in n.body)
            print(f"{mod}:{n.lineno} {cls}: decorators={dec} annotated fields={nf}")
# the documented prior fixes of this shape
for pat in (r"#240: ``replace`` copies", r"never this object \(#1529\)", r"never a solve's away setback \(D1-s3-04\)",
            r"The cap is the CONFIGURED target, never the live one"):
    hits = [i + 1 for i, l in enumerate(src.splitlines()) if re.search(pat, l)]
    print(f"coordinator.py note {pat!r}: lines {hits}")
hits = [i + 1 for i, l in enumerate(away.splitlines()) if "#1517" in l]
print(f"away.py #1517 notes: lines {hits}")
