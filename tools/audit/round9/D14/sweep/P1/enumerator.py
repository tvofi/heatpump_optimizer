#!/usr/bin/env python3
# Round 9, Phase D, sweep thread S3, class P1 ("A non-finite or malformed
# value crosses a persisted-store boundary with no guard").
#
# METRIC: for every persisted-store loader in custom_components/heatpump_optimizer
#   (every from_dict/_load*/async_load*/apply_payload/_stored_peaks/
#   _load_switch_record, per the class's own findings' seam_rules, widened to
#   every such def in the package), and for every numeric leaf it reads with
#   data.get(...)/dict subscript/iteration-unpacked item feeding a float()/int()
#   conversion: whether that leaf's value is checked with isfinite/isnan/isinf
#   (or an equivalent domain check named in --domain-checks) anywhere in the
#   same function before being stored or used. Separately, for every
#   datetime.fromisoformat(...) call: whether the *lifetime* of its result
#   (same function, until return) is ever combined with another datetime via
#   -, <, <=, >, >= while the enclosing except clause does not also catch
#   TypeError (the offset-naive/aware subtraction crash) and the value is not
#   dropped when naive.
# INSTRUMENTED SYMBOLS: every classmethod/function this scan names below,
#   e.g. custom_components.heatpump_optimizer.price_model:PriceShapeModel.from_dict.
# COMMAND (repo root):
#   PYTHONPATH=tests/hastub python3 tools/audit/round9/D14/sweep/P1/enumerator.py
#     [--list] [--fixture] [--history]
# EXPECTED: see SWEEP.md. Deterministic AST scan (no I/O beyond reading the tree).
import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
PKG = ROOT / "custom_components" / "heatpump_optimizer"

LOADER_NAME_PREFIXES = ("from_dict", "_load", "async_load", "apply_payload",
                         "_stored_peaks", "_load_switch_record")
FINITE_CHECK_NAMES = {"isfinite", "isnan", "isinf", "_finite"}


def is_loader_name(name: str) -> bool:
    return any(name == p or name.startswith(p) for p in LOADER_NAME_PREFIXES)


def _name_of(node) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


class FuncScan(ast.NodeVisitor):
    """Walks one loader function body once, collecting NUMFIELD and
    DTNAIVE seams keyed by the local variable each assigns to."""

    def __init__(self, qualname: str, filename: str):
        self.qualname = qualname
        self.filename = filename
        self.numfield: list[dict] = []   # {var, key, line, guarded}
        self.dtnaive: list[dict] = []     # {var, line, guarded, reason}
        self._finite_checked_vars: set[str] = set()
        self._typeerror_caught_vars: set[str] = set()

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        types = []
        if node.type is None:
            types = ["*"]
        elif isinstance(node.type, ast.Tuple):
            types = [_name_of(e) for e in node.type.elts]
        else:
            types = [_name_of(node.type)]
        if "TypeError" in types or "*" in types:
            for n in ast.walk(node):
                self.generic_visit(n) if False else None
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        if name in FINITE_CHECK_NAMES:
            for a in node.args:
                v = _name_of(a)
                if v:
                    self._finite_checked_vars.add(v)
        if name == "fromisoformat":
            self.dtnaive.append({"line": node.lineno, "kind": "parse"})
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # var = data.get("key") / data.get("key", default) / entry[i] / data["key"]
        for target in node.targets:
            tname = _name_of(target)
            if tname is None:
                continue
            key = None
            src = node.value
            if isinstance(src, ast.Call) and _name_of(src.func) == "get" and src.args:
                a0 = src.args[0]
                if isinstance(a0, ast.Constant):
                    key = a0.value
            elif isinstance(src, ast.Subscript):
                sl = src.slice
                if isinstance(sl, ast.Constant):
                    key = sl.value
            looks_numeric = isinstance(src, ast.Call) and _name_of(src.func) in ("float", "int")
            # also catch var = float(np.clip(data.get(...), lo, hi)) and
            # var = max(0.0, float(data.get(...))) -- float()/int() nested
            # one call deep inside the RHS, still a direct numeric cast of a
            # store leaf (not a container variable read for later processing).
            if not looks_numeric and isinstance(src, ast.Call):
                for arg in ast.walk(src):
                    if (isinstance(arg, ast.Call) and _name_of(arg.func) in ("float", "int")
                            and any(_name_of(a2) in ("get",) or isinstance(a2, ast.Subscript)
                                    for c in ast.walk(arg) if isinstance(c, ast.Call)
                                    for a2 in [c.func])):
                        looks_numeric = True
                        break
            if looks_numeric:
                self.numfield.append({"var": tname, "key": key, "line": node.lineno})
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # tracker.foo = float(...)-style attribute assigns are handled via
        # visit_Assign's target walk too (Attribute is a valid target), so
        # nothing extra needed here; kept for completeness / future shapes.
        self.generic_visit(node)


def scan_function(fn: ast.AST, qualname: str, filename: str, src_lines: list[str]) -> FuncScan:
    fs = FuncScan(qualname, filename)
    fs.visit(fn)
    # Determine finiteness coverage per numeric field: guarded if the var
    # (or its final attribute alias) appears as an argument to an isfinite-
    # shaped call anywhere later in the same function, OR if the RHS line
    # itself is wrapped by max(0.0/... , float(...)) AND ALSO isfinite-checked
    # (max/min alone is not a finiteness guard: max(0.0, nan) == 0.0 only
    # when the literal is the FIRST argument, and max(nan, 0.0) == nan; both
    # shapes are observed in this codebase (price_model.py residual_var vs.
    # dhw_draws.py open_kwh), so we key strictly on an isfinite-shaped call,
    # never on clamp order).
    src = "\n".join(src_lines)
    finite_call_lines = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            name = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
            if name in FINITE_CHECK_NAMES:
                finite_call_lines.add(n.lineno)
    # A field counts as isfinite-guarded if ANY isfinite-shaped call exists
    # anywhere in the function body that could plausibly test it: we require
    # the guarded variable's name (or the attribute it is ultimately stored
    # under) to appear as a Name inside that call's own line, or the function
    # to raise/continue immediately after a bare isfinite(...) test whose only
    # candidate is this field (single-numeric-field loaders).
    body_names_per_line: dict[int, set[str]] = {}
    for n in ast.walk(fn):
        line = getattr(n, "lineno", None)
        if line is None:
            continue
        nm = _name_of(n)
        if nm:
            body_names_per_line.setdefault(line, set()).add(nm)
    guarded_vars = set(fs._finite_checked_vars)
    for line in finite_call_lines:
        guarded_vars |= body_names_per_line.get(line, set())
    for item in fs.numfield:
        item["guarded"] = item["var"] in guarded_vars
        item["qualname"] = qualname
        item["file"] = filename
    # dtnaive: guarded if a TypeError-catching except wraps the parse+use, OR
    # the result is never combined with another datetime in this function
    # (stored as an opaque string/attr and compared to `now` only elsewhere,
    # which this local scan cannot see -- conservatively "not applicable"
    # here rather than a false instance) OR tzinfo is normalised
    # (.replace(tzinfo=...) / .astimezone( / a bare naive `now` on both sides,
    # which this repo's coordinator.py already does at some of these seams).
    handlers_by_line_range: list[tuple[int, int, set[str]]] = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Try):
            types_all: set[str] = set()
            for h in n.handlers:
                if h.type is None:
                    types_all.add("*")
                elif isinstance(h.type, ast.Tuple):
                    types_all |= {_name_of(e) for e in h.type.elts if _name_of(e)}
                else:
                    nm = _name_of(h.type)
                    if nm:
                        types_all.add(nm)
            handlers_by_line_range.append((n.lineno, n.end_lineno or n.lineno, types_all))
    combined_lines = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Sub):
            combined_lines.add(n.lineno)
        if isinstance(n, ast.Compare):
            combined_lines.add(n.lineno)
    for item in fs.dtnaive:
        line = item["line"]
        guard = "no_combine_seen"
        for lo, hi, types in handlers_by_line_range:
            if lo <= line <= hi:
                if "TypeError" in types or "*" in types:
                    guard = "typeerror_caught"
                break
        combined_nearby = any(lo_line >= line for lo_line in combined_lines
                               if lo_line - line < 15)
        naive_normalised = "replace(tzinfo" in src or ".astimezone(" in src
        item["guard"] = guard
        item["combined_nearby"] = combined_nearby
        item["naive_normalised"] = naive_normalised
        item["qualname"] = qualname
        item["file"] = filename
    fs._scan_extra = {"finite_call_lines": finite_call_lines}
    return fs


def iter_functions(path: Path):
    src = path.read_text()
    tree = ast.parse(src)
    lines = src.splitlines()

    def visit(node, where):
        for ch in ast.iter_child_nodes(node):
            w = where
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                w = f"{where}.{ch.name}" if where else ch.name
                if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_loader_name(ch.name):
                    yield ch, w, lines
            yield from visit(ch, w)
    yield from visit(tree, "")


def measure(files):
    numfield, dtnaive = [], []
    for p in files:
        for fn, qualname, lines in iter_functions(p):
            rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
            fs = scan_function(fn, qualname, rel, lines)
            numfield += fs.numfield
            dtnaive += fs.dtnaive
    return numfield, dtnaive


FIXTURE_CLEAN = '''
import math

class Stored:
    @classmethod
    def from_dict(cls, data):
        obj = cls()
        v = float(data.get("bias", 0.0))
        if not math.isfinite(v):
            v = 0.0
        obj.bias = v
        return obj
'''
FIXTURE_REINTRO = FIXTURE_CLEAN.replace(
    "        if not math.isfinite(v):\n            v = 0.0\n", "")


def fixture() -> tuple[int, int]:
    import tempfile
    d = Path(tempfile.mkdtemp(prefix="p1-sweep-"))
    out = []
    for name, src in (("clean.py", FIXTURE_CLEAN), ("reintro.py", FIXTURE_REINTRO)):
        p = d / name
        p.write_text(src)
        nf, _ = measure([p])
        out.append(sum(1 for r in nf if not r["guarded"]))
    return out[0], out[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--fixture", action="store_true")
    a = ap.parse_args()
    clean, reintro = fixture()
    print(f"RESULT fixture_clean_unguarded={clean} count")
    print(f"RESULT fixture_reintro_unguarded={reintro} count")
    if a.fixture:
        return 0
    files = sorted(PKG.glob("*.py"))
    numfield, dtnaive = measure(files)
    unguarded_num = [r for r in numfield if not r["guarded"]]
    print(f"RESULT numfield_seams={len(numfield)} count")
    print(f"RESULT numfield_unguarded={len(unguarded_num)} count")
    dt_instance = [r for r in dtnaive
                   if r["guard"] != "typeerror_caught" and r["combined_nearby"]
                   and not r["naive_normalised"]]
    print(f"RESULT dtnaive_seams={len(dtnaive)} count")
    print(f"RESULT dtnaive_instance={len(dt_instance)} count")
    if a.list:
        for r in unguarded_num:
            print(f"  SEAM NUMFIELD {r['file']}:{r['line']} {r['qualname']} key={r['key']!r} var={r['var']}")
        for r in dt_instance:
            print(f"  SEAM DTNAIVE {r['file']}:{r['line']} {r['qualname']} guard={r['guard']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
