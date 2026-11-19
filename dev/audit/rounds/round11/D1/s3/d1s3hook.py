"""D1-s3 injection hook: an import-time AST rewrite of the integration's own modules.

Not a harness on its own. Every try statement owning a handler `enumerate.py d1-excepts`
lists gets, at the top of its body (same line number as the body's first statement):

    if __import__("d1s3hook").armed("<id>"):
        raise __import__("d1s3hook").make("<id>", lambda: (<the handler's own except expression>))

and, at the top of the handler body, `__import__("d1s3hook").entered("<id>")`. Nothing else in
the module changes, so a fault-free run is the production code path (control arm: no id armed).
A settrace raise was the first design and is unusable: CPython unsets the tracer after a trace
function raises, so only the first injection of a run ever fired.

Modes: `persistent` (every pass of an armed id raises) and `oneshot` (each armed id raises on its
first pass only). `install(ids)` must run before the package is first imported.
"""
import ast
import collections
import importlib.abc
import importlib.util
import os
import sys

MARK = "D1S3-INJECTED"
PKG_DIR = os.path.abspath("custom_components/heatpump_optimizer")


class Injected(RuntimeError):
    pass


ARMED = set()
EDITS = []  # (rel path, old text, new text), applied in memory at import
MODE = "persistent"
FIRED = collections.Counter()
ENTERED = collections.Counter()
PASSED = collections.Counter()
FIRST_FIRE = {}
ON_FIRE = None  # callback(id) for the one-shot observer


RAISED_OUT = collections.Counter()
WINDOW_LOGS = {}      # id -> [records between its handler entry and the next hook event]
RECORDS = None        # list the observer appends log records to (level, template)
_OPEN = None          # (id, start index) of the handler window being observed


def _close():
    global _OPEN
    if _OPEN is not None and RECORDS is not None:
        hid, i0 = _OPEN
        WINDOW_LOGS.setdefault(hid, []).extend(RECORDS[i0:])
    _OPEN = None


def left(hid, raised):
    _close()
    if raised:
        RAISED_OUT[hid] += 1


def armed(hid):
    _close()
    PASSED[hid] += 1
    if hid not in ARMED:
        return False
    if MODE == "oneshot" and FIRED[hid]:
        return False
    return True


def make(hid, caught):
    FIRED[hid] += 1
    if ON_FIRE is not None:
        ON_FIRE(hid)
    try:
        typ = caught()
    except Exception:
        typ = Exception
    if isinstance(typ, tuple):
        typ = typ[0] if typ else Exception
    if typ in (Exception, BaseException) or not isinstance(typ, type):
        return Injected(MARK)
    for args in ((MARK,), (), (MARK, 2, 1), (MARK, MARK)):
        try:
            return typ(*args)
        except Exception:
            pass
    return Injected(MARK)


def entered(hid):
    global _OPEN
    _close()
    ENTERED[hid] += 1
    if RECORDS is not None and FIRED[hid] and ENTERED[hid] <= FIRED[hid]:
        _OPEN = (hid, len(RECORDS))


class _Rewrite(ast.NodeTransformer):
    def __init__(self, rel, lines):
        self.rel, self.lines = rel, lines

    def _visit_try(self, node):
        self.generic_visit(node)
        mine = [h for h in node.handlers if h.lineno in self.lines]
        if not mine:
            return node
        # One guard per listed handler of this try (a try with several handlers, e.g.
        # `except UpdateFailed: raise` then `except Exception`, arms each one separately;
        # the raised type is the armed handler's own, so an earlier sibling handler that
        # catches it too is what production does with it).
        first = node.body[0]
        for h0 in reversed(mine):
            hid = f"{self.rel}:{h0.lineno}"
            caught = ast.unparse(h0.type) if h0.type is not None else "BaseException"
            guard = ast.parse(
                f'if __import__("d1s3hook").armed("{hid}"):\n'
                f'    raise __import__("d1s3hook").make("{hid}", lambda: ({caught}))\n').body[0]
            for n in ast.walk(guard):
                ast.copy_location(n, first)
                n.end_lineno, n.end_col_offset = first.lineno, first.col_offset
            node.body.insert(0, guard)
        for h in mine:
            hid_h = f"{self.rel}:{h.lineno}"
            note = ast.parse(f'__import__("d1s3hook").entered("{hid_h}")').body[0]
            tgt = h.body[0]
            for n in ast.walk(note):
                ast.copy_location(n, tgt)
                n.end_lineno, n.end_col_offset = tgt.lineno, tgt.col_offset
            wrap = ast.parse(
                "try:\n    pass\n"
                "except BaseException:\n"
                f'    __import__("d1s3hook").left("{hid_h}", True)\n'
                "    raise\n"
                f'__import__("d1s3hook").left("{hid_h}", False)\n').body
            wrap[0].body = h.body
            for n in [wrap[0], *wrap[0].handlers, *ast.walk(wrap[0].handlers[0]), *ast.walk(wrap[1])]:
                if hasattr(n, "lineno"):
                    ast.copy_location(n, tgt)
                    n.end_lineno, n.end_col_offset = tgt.lineno, tgt.col_offset
            h.body = [note, *wrap]
        return node

    visit_Try = _visit_try
    visit_TryStar = _visit_try


class _Loader(importlib.abc.SourceLoader):
    def __init__(self, path, lines, rel):
        self.path, self.lines, self.rel = path, lines, rel

    def get_filename(self, fullname):
        return self.path

    def get_data(self, path):
        with open(path, "rb") as fh:
            return fh.read()

    def source_to_code(self, data, path, *, _optimize=-1):
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        for rel, old, new in EDITS:  # a finding's perturbation: a one-line production edit
            if rel == self.rel:
                assert data.count(old) == 1, f"perturbation text not unique in {rel}: {old!r}"
                data = data.replace(old, new)
        tree = ast.parse(data, path)
        tree = _Rewrite(self.rel, self.lines).visit(tree)
        ast.fix_missing_locations(tree)
        return compile(tree, path, "exec", dont_inherit=True)

    # never write or read a bytecode cache: the rewrite must not leak into the tree
    def get_code(self, fullname):
        return self.source_to_code(self.get_data(self.path), self.path)


class _Finder(importlib.abc.MetaPathFinder):
    def __init__(self, by_file):
        self.by_file = by_file

    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith("heatpump_optimizer") and \
                not fullname.startswith("custom_components.heatpump_optimizer"):
            return None
        tail = fullname.split("heatpump_optimizer", 1)[1].lstrip(".")
        if tail:
            fp = os.path.join(PKG_DIR, *tail.split(".")) + ".py"
            is_pkg = False
        else:
            fp = os.path.join(PKG_DIR, "__init__.py")
            is_pkg = True
        if not os.path.exists(fp):
            return None
        rel = os.path.relpath(fp).replace(os.sep, "/")
        loader = _Loader(fp, self.by_file.get(rel, set()), rel)
        return importlib.util.spec_from_file_location(
            fullname, fp, loader=loader,
            submodule_search_locations=[PKG_DIR] if is_pkg else None)


def handlers():
    """One row per `enumerate.py d1-excepts` line, with the handler's AST facts."""
    import subprocess
    out = subprocess.run([sys.executable, "tools/audit/enumerate.py", "d1-excepts"],
                         capture_output=True, text=True, check=True).stdout.splitlines()
    trees, rows = {}, []
    for line in out:
        loc, kind, func = line.split(" ", 2)
        rel, ln = loc.rsplit(":", 1)
        ln = int(ln)
        path = os.path.abspath(rel)
        if path not in trees:
            trees[path] = ast.parse(open(path).read())
        hit = None
        for node in ast.walk(trees[path]):
            if isinstance(node, (ast.Try, getattr(ast, "TryStar", ast.Try))):
                for h in node.handlers:
                    if h.lineno == ln:
                        hit = (node, h)
        node, h = hit
        body = ast.Module(body=h.body, type_ignores=[])
        names = {type(n).__name__ for n in ast.walk(body)}
        calls = [ast.unparse(c.func) for c in ast.walk(body) if isinstance(c, ast.Call)]
        logs = any(c.split(".")[-1] in {"debug", "info", "warning", "error", "exception", "critical"}
                   or "log" in c.lower() for c in calls)
        rows.append({
            "id": f"{rel}:{ln}", "file": path, "line": ln, "kind": kind, "func": func,
            "first": node.body[0].lineno, "caught": ast.unparse(h.type) if h.type else "",
            "reraises": "Raise" in names, "static_logs": logs,
            "body": ast.unparse(body)[:240],
        })
    return rows


def install(rows):
    """rows: dicts with 'id' = '<rel>:<except line>'. Call before importing the package."""
    sys.modules["d1s3hook"] = sys.modules[__name__]
    by_file = collections.defaultdict(set)
    for r in rows:
        rel, ln = r["id"].rsplit(":", 1)
        by_file[rel].add(int(ln))
    sys.meta_path.insert(0, _Finder(by_file))
    # a test that loads a module file directly (tests/open_meteo.py) gets the same rewrite
    real = importlib.util.spec_from_file_location

    def spec_from_file_location(name, location=None, *a, **k):
        if location is not None and os.path.abspath(str(location)).startswith(PKG_DIR + os.sep) \
                and "loader" not in k:
            fp = os.path.abspath(str(location))
            rel = os.path.relpath(fp).replace(os.sep, "/")
            k["loader"] = _Loader(fp, by_file.get(rel, set()), rel)
        return real(name, location, *a, **k)

    importlib.util.spec_from_file_location = spec_from_file_location
