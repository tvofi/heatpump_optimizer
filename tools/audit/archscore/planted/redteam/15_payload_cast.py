"""Game untyped_payload_keys with a cast: every value _async_update_data returns is wrapped in
typing.cast(dict[str, Any], ...). Nothing is typed and no producer changed; the census stopped
following the returned dict at the cast and read the produced keys as gone. The R9-EG-B3a
round-1 review's finding (#1852): with the producer behind a cast the metric read 166 -> 0 on
three produced keys."""
import ast, sys
from rt_lib import pkg, replace_nodes, seg
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
fn = next(n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "_async_update_data")
edits = [(n.value, f"cast(dict[str, Any], {seg(src, n.value)})")
         for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None]
assert edits, "the producer returns nothing to wrap"
imp = next(n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module == "typing")
names = sorted({a.name for a in imp.names} | {"cast"})
edits.append((imp, f"from typing import {', '.join(names)}"))
replace_nodes(p, edits)
ast.parse(p.read_text())
print("returns wrapped", len(edits) - 1)
