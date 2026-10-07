"""Game untyped_payload_keys with a cast: the payload builder's ``return data`` becomes
``return cast(dict, data)``, the spelling R9-EG-B3a used (``return cast(Payload, data)``). Nothing is
typed and no producer changed; the census stopped following the returned dict at the cast and read
its keys as gone, and the footprint reads the cast as delegation. The R9-EG-B3a round-1 review's
finding (#1852): behind the cast the metric read 166 -> 0 on three produced keys."""
import ast, sys
from rt_lib import pkg, replace_nodes
root = sys.argv[1]
p = pkg(root) / "coordinator.py"
src = p.read_text()
tree = ast.parse(src)
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_build_data_dict")
edits = [(n.value, f"cast(dict, {n.value.id})") for n in ast.walk(fn)
         if isinstance(n, ast.Return) and isinstance(n.value, ast.Name)]
assert len(edits) == 1, "the builder returns its dict once"
imp = next(n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module == "typing")
names = sorted({a.name for a in imp.names} | {"cast"})
edits.append((imp, f"from typing import {', '.join(names)}"))
replace_nodes(p, edits)
ast.parse(p.read_text())
print("builder return cast")
