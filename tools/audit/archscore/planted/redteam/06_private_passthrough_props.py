"""Game coordinator_private_reach: for every coordinator private a foreign module READS, add a public
passthrough property ``raw_<name>`` (``return self._<name>``) to the coordinator and re-spell
the foreign read as ``coord.raw_<name>``. Same object handed out, same coupling, the
coordinator's surface grows by one accessor per private. Writes are left alone (a setter
would be a counted logic statement), and so are reads through the ``_ctx`` hop (the context
object has no passthrough)."""
import ast, sys
from collections import defaultdict
from rt_lib import pkg, replace_nodes, seg
from archscore.metrics import common as C


class PR:
    @staticmethod
    def _private(name):
        return name.startswith("_") and not name.startswith("__") and name != C.CTX_ATTR


root = sys.argv[1]
P = C.load(str(root))
eng = C.engine(P)
penv, reached = eng.propagate(None)
edits = defaultdict(list)
members = set()
seen = set()
for q in sorted(reached):
    fn = P.funcs[q]
    if fn.mod == C.COORD_MODULE:
        continue
    env = eng._local_env(fn.node, penv[q], fn.cls, fn.mod)
    mutated = set()
    for n in C.walk(fn.node):
        tg = n.targets if isinstance(n, (ast.Assign, ast.Delete)) else [n.target] if isinstance(n, (ast.AugAssign, ast.AnnAssign)) else []
        for t in tg:
            for x in (t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]):
                if isinstance(x, (ast.Attribute, ast.Subscript)):
                    mutated.add(id(x.value))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in C.MUTATORS:
            mutated.add(id(n.func.value))
    ctx_alias = {t.id for x in C.walk(fn.node)
                 if isinstance(x, (ast.Assign, ast.AnnAssign)) and x.value is not None and "_ctx" in ast.unparse(x.value)
                 for t in (x.targets if isinstance(x, ast.Assign) else [x.target]) if isinstance(t, ast.Name)}

    def via_ctx(e):
        return "_ctx" in ast.unparse(e) or any(isinstance(x, ast.Name) and x.id in ctx_alias for x in ast.walk(e))
    for n in C.walk(fn.node):
        if isinstance(n, ast.Attribute) and PR._private(n.attr) and isinstance(n.ctx, ast.Load) \
                and id(n) not in mutated and C.COORD in eng.ev(n.value, env, fn.mod, fn.cls) \
                and not via_ctx(n.value):  # a read through the context hop stays
            k = (fn.mod, n.lineno, n.col_offset)
            if k not in seen:
                seen.add(k)
                edits[fn.mod].append((n, n.attr))
                members.add(n.attr)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr") \
                and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str) \
                and PR._private(n.args[1].value) and id(n) not in mutated \
                and C.COORD in eng.ev(n.args[0], env, fn.mod, fn.cls) and not via_ctx(n.args[0]):
            k = (fn.mod, n.args[1].lineno, n.args[1].col_offset)
            if k not in seen:
                seen.add(k)
                edits[fn.mod].append((n.args[1], None))
                members.add(n.args[1].value)
tot = 0
for mod, es in edits.items():
    p = pkg(root) / f"{mod}.py"
    src = p.read_text()
    out = []
    for n, attr in es:
        if attr is not None:
            out.append((n, f"{seg(src, n.value)}.raw{attr}"))
        else:
            out.append((n, repr("raw" + n.value)))
    tot += replace_nodes(p, out)
# the passthroughs, appended to the coordinator class
p = pkg(root) / "coordinator.py"
src = p.read_text()
cls = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "HeatPumpOptimizerCoordinator")
props = "".join(f"\n    @property\n    def raw{m}(self) -> Any:\n        return self.{m}\n" for m in sorted(members))
lines = src.splitlines(keepends=True)
lines.insert(cls.end_lineno, props)
p.write_text("".join(lines))
print("reads rewritten", tot, "members", len(members))
