"""Game hub_solve_writes without any reflective write: inside the coordinator class every LOAD of
a live hub (ctx._opt_config / self._thermal_params / getattr(self, "_ctx", self)._current_state ...)
that is written through or handed to a callee is re-spelled self._live("<hub>"), a two-line accessor returning the same live object. Writes
through it (self._live("_opt_config").peak_count = n) are the same in-place writes into the same
hub; the role engine cannot evaluate a method's return value, so they vanish."""
import ast, sys
from rt_lib import pkg, replace_nodes
root = sys.argv[1]
HUBS = ("_opt_config", "_thermal_params", "_current_state")
p = pkg(root) / "coordinator.py"
src = p.read_text()
cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")


def hub_base(e) -> bool:
    s = ast.unparse(e)
    return s in ("ctx", "self", "self._ctx", "getattr(self, '_ctx', self)")


edits = []
for fn in cls.body:
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name == "__init__":
        continue
    wanted = set()
    for n in ast.walk(fn):  # only where a write happens through it, or it is handed to a callee
        if isinstance(n, (ast.Assign, ast.AugAssign)):
            for t in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                for x in (t.elts if isinstance(t, ast.Tuple) else [t]):
                    if isinstance(x, (ast.Attribute, ast.Subscript)):
                        wanted.add(id(x.value))
        elif isinstance(n, ast.Call):
            wanted |= {id(a) for a in n.args} | {id(k.value) for k in n.keywords}
    for n in ast.walk(fn):
        if isinstance(n, ast.Attribute) and n.attr in HUBS and isinstance(n.ctx, ast.Load) and hub_base(n.value) \
                and id(n) in wanted:
            edits.append((n, f'self._live("{n.attr}")'))
# drop nested duplicates (none expected: a hub load never contains another)
replace_nodes(p, edits)
src = p.read_text()
cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
lines = src.splitlines(keepends=True)
helper = ('\n    def _live(self, name: str) -> Any:\n        """The live hub ``name`` (through the context when there is one)."""\n'
          '        ctx = getattr(self, "_ctx", self)\n        return getattr(ctx, name)\n')
lines.insert(cls.end_lineno, helper)
p.write_text("".join(lines))
print("hub loads re-spelled", len(edits))
