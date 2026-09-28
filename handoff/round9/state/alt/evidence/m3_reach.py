"""M3 enumerator: reads/writes of the coordinator's private members from other modules. Run from repo root."""
import ast, pathlib, collections
P = pathlib.Path("custom_components/heatpump_optimizer")
COORD_NAMES = {"coordinator", "coord", "self.coordinator", "self._coordinator", "self._coord"}
tot = collections.Counter(); names = collections.Counter(); writes = []
for p in sorted(P.glob("*.py")):
    if p.name == "coordinator.py":
        continue
    t = ast.parse(p.read_text())
    for n in ast.walk(t):
        hit = None
        if isinstance(n, ast.Attribute) and n.attr.startswith("_") and not n.attr.startswith("__") \
           and ast.unparse(n.value) in COORD_NAMES:
            hit = n.attr
            if isinstance(n.ctx, ast.Store):
                writes.append(f"{p.name}:{n.lineno} {ast.unparse(n.value)}.{n.attr} =")
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "setattr", "hasattr") \
             and len(n.args) >= 2 and ast.unparse(n.args[0]) in COORD_NAMES and isinstance(n.args[1], ast.Constant) \
             and isinstance(n.args[1].value, str) and n.args[1].value.startswith("_") and not n.args[1].value.startswith("__"):
            hit = n.args[1].value
            if n.func.id == "setattr":
                writes.append(f"{p.name}:{n.lineno} setattr(..., {hit!r})")
        if hit:
            tot[p.name] += 1; names[hit] += 1
print("private coordinator-member reaches outside coordinator.py, per file:")
for f, c in tot.most_common():
    print(f"  {f}: {c}")
print(f"total: {sum(tot.values())} across {len(tot)} files; distinct members: {len(names)}")
print("most reached:", names.most_common(10))
print("writes into coordinator state from other modules:")
for w in writes:
    print("  ", w)
