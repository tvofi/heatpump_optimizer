"""D14 class N-period-rollover: enumerate every period-boundary reset seam.

A seam is an ``if`` whose test compares a freshly derived period key against a
stored one (``key != self.<attr>`` / ``self.<attr>[i] != key``, key or attr
named month/day/date/period/window/week/key). Inside the branch the seam is
UNSAFE when it resets accumulator state (assigns ``[]``, ``{}``, ``0``,
``0.0``, ``""``, ``None`` or calls ``.clear()``) to a self attribute BEFORE any
call that folds/closes the open period (any call whose name is not a plain
builtin/logging), i.e. the open window is wiped without being closed.

Command: python3 dev/audit/rounds/round10/D14/period_rollover_seams.py [ROOT] [--fixture]
  ROOT defaults to custom_components/heatpump_optimizer.
  --fixture runs the built-in null control (a close-then-reset class) and must print unsafe=0.
Prints one SEAM line per seam, then RESULT seams=N unsafe=M.
"""
import ast, pathlib, sys

NAMES = ("month", "day", "date", "period", "window", "week", "key")
INERT_CALLS = {"len", "int", "float", "str", "max", "min", "debug", "info",
               "warning", "_note", "isoformat", "strftime", "get"}
RESET_VALUES = (list, dict)

FIXTURE = '''
class Clean:
    def observe(self, when, kw):
        month = when.strftime("%Y-%m")
        if month != self.month:
            self._close_window()
            self.month = month
            self.peaks = []
'''


def _named(node):
    s = ast.unparse(node).lower()
    return any(n in s for n in NAMES)


def _self_attr(node):
    while isinstance(node, ast.Subscript):
        node = node.value
    return isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self"


def _is_reset(stmt):
    if isinstance(stmt, ast.Assign) and any(_self_attr(t) for t in stmt.targets):
        v = stmt.value
        if isinstance(v, (ast.List, ast.Dict)) and not getattr(v, "elts", None) and not getattr(v, "keys", None):
            return True
        if isinstance(v, ast.Constant) and v.value in (0, 0.0, "", None):
            return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        f = stmt.value.func
        return isinstance(f, ast.Attribute) and f.attr == "clear" and _self_attr(f.value)
    return False


def _folding_call(stmt):
    for n in ast.walk(stmt):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if name not in INERT_CALLS:
                return True
    return False


def scan(src, label):
    out = []
    tree = ast.parse(src)
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if not isinstance(node, ast.If):
                continue
            tests = [node.test] + ([v for v in node.test.values] if isinstance(node.test, ast.BoolOp) else [])
            hit = None
            for t in tests:
                if isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], ast.NotEq):
                    l, r = t.left, t.comparators[0]
                    if (_self_attr(l) or _self_attr(r)) and (_named(l) or _named(r)):
                        hit = t
            if hit is None:
                continue
            verdict = "safe"
            for stmt in node.body:
                if _folding_call(stmt) and not _is_reset(stmt):
                    break
                if _is_reset(stmt):
                    verdict = "unsafe"
                    break
            out.append((label, node.lineno, fn.name, ast.unparse(hit), verdict))
    return out


def main():
    if "--fixture" in sys.argv:
        rows = scan(FIXTURE, "<fixture>")
    else:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        root = pathlib.Path(args[0] if args else "custom_components/heatpump_optimizer")
        rows = []
        for p in sorted(root.rglob("*.py")):
            rows += scan(p.read_text(), str(p))
    for r in rows:
        print("SEAM %s:%d %s [%s] %s" % r)
    print(f"RESULT seams={len(rows)} unsafe={sum(r[4] == 'unsafe' for r in rows)}")


if __name__ == "__main__":
    main()
