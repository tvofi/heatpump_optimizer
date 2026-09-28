"""M2 enumerator (top-level payload reads only). Run from the repo root."""
import ast, json, pathlib, re
P = pathlib.Path("custom_components/heatpump_optimizer")
prod = set()
for g in sorted(pathlib.Path("tests/golden").glob("coord_*.json")):
    d = json.loads(g.read_text()); data = d.get("data", d)
    prod |= set(data) if isinstance(data, dict) else set()
print(f"producer keys, union of tests/golden/coord_*.json 'data': {len(prod)}")
TOP = {"self.coordinator.data", "self.coordinator.data or {}", "self._data()", "coordinator.data", "coordinator.data or {}"}
SURF = ["sensor.py", "binary_sensor.py", "climate.py", "switch.py", "entity.py", "button.py", "datetime.py"]
reads = {}
for f in SURF:
    t = ast.parse((P / f).read_text())
    for fn in [n for n in ast.walk(t) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        bound = {n.targets[0].id for n in ast.walk(fn) if isinstance(n, ast.Assign) and len(n.targets) == 1
                 and isinstance(n.targets[0], ast.Name) and ast.unparse(n.value) in TOP}
        def top(e):
            return ast.unparse(e) in TOP or (isinstance(e, ast.Name) and e.id in bound)
        for n in ast.walk(fn):
            k = None
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args \
               and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str) and top(n.func.value):
                k = n.args[0].value
            elif isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str) and top(n.value):
                k = n.slice.value
            if k:
                reads.setdefault(k, []).append(f"{f}:{n.lineno}")
print(f"distinct top-level keys read by the surfaces: {len(reads)}; read sites: {sum(map(len, reads.values()))}")
pkg = "\n".join(p.read_text() for p in P.glob("*.py") if p.name not in SURF)
miss = sorted(k for k in reads if k not in prod)
print(f"top-level keys read but absent from every golden: {len(miss)}")
for k in miss:
    pat = "[\"']" + re.escape(k) + "[\"']"
    print(f"  {k!r} read at {reads[k]}; literal occurrences in non-surface modules: {len(re.findall(pat, pkg))}")
print(f"golden keys no surface reads at top level: {len(prod - set(reads))} (card / nested / diagnostics may consume)")
print(f"TypedDict in package: {sum(p.read_text().count('TypedDict') for p in P.glob('*.py'))}")
print("coordinator class line:", next(l.strip() for l in (P / 'coordinator.py').read_text().splitlines() if l.startswith('class HeatPumpOptimizerCoordinator')))
