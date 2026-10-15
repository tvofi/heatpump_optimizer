"""I1 sweep probe hook: rewrites every LEN seam's `<i> < len(<s>)` operand in
custom_components/heatpump_optimizer at import so each evaluation records
(file:line, outcome) to $I1_TRACE. Only the False outcome matters: a seam
whose guard is never False under a gate script is never exercised by it, so
no check in that script can pin the guard. Installed by PYTHONPATH."""
import ast, os, sys, importlib.abc, importlib.util, atexit

_OUT = os.environ.get("I1_TRACE")
_SEEN = set()
if _OUT:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
    from enumerate_i1 import _is_len_cmp  # noqa

    def _rec(key, v):
        _SEEN.add((key, bool(v)))
        return v
    import builtins
    builtins.i1rec_ = _rec

    @atexit.register
    def _dump():
        with open(_OUT, "a") as f:
            for k, v in _SEEN:
                f.write(f"{k} {int(v)}\n")

    class _T(ast.NodeTransformer):
        def __init__(self, rel): self.rel = rel
        def visit_BoolOp(self, node):
            self.generic_visit(node)
            if isinstance(node.op, ast.And):
                node.values = [ast.copy_location(ast.Call(
                    func=ast.Name("i1rec_", ast.Load()),
                    args=[ast.Constant(f"{self.rel}:{node.lineno}"), v], keywords=[]), v)
                    if _is_len_cmp(v) else v for v in node.values]
            return node

    class _F(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if not name.startswith("heatpump_optimizer") and ".heatpump_optimizer" not in name:
                return None
            for f in sys.meta_path:
                if f is self: continue
                spec = getattr(f, "find_spec", lambda *a: None)(name, path, target)
                if spec: break
            else:
                return None
            o = spec.origin or ""
            if not o.endswith(".py") or "heatpump_optimizer" not in o: return spec
            rel = "custom_components/heatpump_optimizer/" + o.split("heatpump_optimizer/", 1)[1]
            ld = spec.loader
            class L(importlib.abc.Loader):
                def create_module(self, s): return None
                def exec_module(self, m):
                    src = open(o).read()
                    t = ast.fix_missing_locations(_T(rel).visit(ast.parse(src, o)))
                    exec(compile(t, o, "exec"), m.__dict__)
            spec.loader = L()
            return spec
    sys.meta_path.insert(0, _F())
