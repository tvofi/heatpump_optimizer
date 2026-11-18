"""N-restore-race enumerator (round 11, D14 steps 3-4).

Lists every seam of the class in the package: an async function that awaits a
persisted-state read (async_load / load_mapping / async_get_last_*) and, after that
await, writes the loaded value onto a shared object (an attribute or subscript of
``self``, a parameter, or a record fetched before the await). A writer that runs
on another loop task during the read is overwritten by the stale snapshot.

Each seam is tagged:
  flag_before_await  a ``*loaded* = True`` written before the read (D1-s2-04's shape)
  locked             the read sits inside ``async with <...lock...>``
  lock_covered       every call site of the function (transitively) is under such a lock
The printed metric ``unlocked`` counts seams neither locked nor lock_covered: the
ones whose safety rests on something other than a lock and needs a disposition.

  python3 restore_race.py [--root PKG]          enumerate the package
  python3 restore_race.py --clean               null control: a clean fixture -> unlocked=0
  python3 restore_race.py --plant               perturbation: pump_arbiter.apply's
                                                ``async with held.lock:`` -> ``if True:`` on a
                                                copy (one line) -> unlocked rises by 1
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import shutil
import sys
import tempfile

LOADS = {"async_load", "load_mapping", "async_get_last_state", "async_get_last_extra_data"}
MUTATORS = {"restore", "load", "update", "setdefault", "clear", "append", "extend", "add"}
HERE = pathlib.Path(__file__).resolve()
REPO = HERE.parents[6]
PKG = REPO / "custom_components" / "heatpump_optimizer"


def _callee(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        f = node.func
        if isinstance(f, ast.Attribute):
            return f.attr
        if isinstance(f, ast.Name):
            return f.id
    return None


def _root(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def _is_lock(item: ast.withitem) -> bool:
    return "lock" in ast.unparse(item.context_expr).lower()


class _Fn(ast.NodeVisitor):
    """Walk one async function, tracking enclosing async-with-lock."""

    def __init__(self, fn: ast.AsyncFunctionDef):
        self.fn = fn
        self.params = {a.arg for a in fn.args.args + fn.args.kwonlyargs}
        self.lock_depth = 0
        self.loads: list[tuple[int, bool, set[str]]] = []  # (line, locked, bound names)
        self.flag_lines: list[int] = []
        self.writes: list[tuple[int, str]] = []
        self.local_from: dict[str, int] = {}  # local name -> line bound
        self.calls: list[tuple[str, bool]] = []

    def visit_AsyncWith(self, node):
        lk = any(_is_lock(i) for i in node.items)
        self.lock_depth += lk
        self.generic_visit(node)
        self.lock_depth -= lk

    def visit_FunctionDef(self, node):  # nested defs are their own scope
        return

    visit_AsyncFunctionDef = visit_FunctionDef
    visit_Lambda = visit_FunctionDef

    def visit_Await(self, node):
        name = _callee(node.value)
        if name in LOADS:
            self.loads.append((node.lineno, self.lock_depth > 0, set()))
        self.generic_visit(node)

    def visit_Call(self, node):
        name = _callee(node)
        if name:
            f0 = node.func
            recv = None if not isinstance(f0, ast.Attribute) else (f0.value.id if isinstance(f0.value, ast.Name) else "?")
            self.calls.append(((recv, name), self.lock_depth > 0))
        f = node.func
        if isinstance(f, ast.Attribute) and f.attr in MUTATORS and isinstance(f.value, (ast.Attribute, ast.Subscript)):
            self._write(f.value, node.lineno, f"{ast.unparse(f.value)}.{f.attr}()")
        self.generic_visit(node)

    def _write(self, target, line, text=None):
        root = _root(target)
        if root is None:
            return
        shared = root == "self" or root in self.params or (root in self.local_from and self.local_from[root] < line)
        if shared and isinstance(target, (ast.Attribute, ast.Subscript)):
            self.writes.append((line, text or ast.unparse(target)))

    def visit_Assign(self, node):
        self._assign(node.targets, node.value, node.lineno)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self._assign([node.target], node.value, node.lineno)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if node.value is not None:
            self._assign([node.target], node.value, node.lineno)
        self.generic_visit(node)

    def _assign(self, targets, value, line):
        flat = []
        for t in targets:
            flat.extend(t.elts if isinstance(t, ast.Tuple) else [t])
        for t in flat:
            if isinstance(t, ast.Name):
                # a local bound from a non-load expression before the read can alias shared state
                if not (isinstance(value, ast.Await) and _callee(value.value) in LOADS):
                    self.local_from.setdefault(t.id, line)
            else:
                if isinstance(t, ast.Attribute) and "loaded" in t.attr and isinstance(value, ast.Constant) and value.value is True:
                    self.flag_lines.append(line)
                self._write(t, line)


def _aliases(tree: ast.Module) -> dict[str, str]:
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                out[a.asname or a.name] = a.name
        elif isinstance(n, ast.Import):
            for a in n.names:
                out[a.asname or a.name.split(".")[-1]] = a.name.split(".")[-1]
    return out


def scan(pkg: pathlib.Path) -> list[dict]:
    # call_sites[(module, name)] -> [((caller module, caller name), locked)]; module "*" = unresolved
    call_sites: dict[tuple[str, str], list[tuple[tuple[str, str], bool]]] = {}
    modules = {p.stem for p in pkg.rglob("*.py")}
    seams = []
    for path in sorted(pkg.rglob("*.py")):
        tree = ast.parse(path.read_text(), str(path))
        mod = path.stem
        alias = _aliases(tree)

        def key(recv, name):
            if recv is None:
                return (mod, name)
            target = alias.get(recv, recv)
            return (target, name) if target in modules else ("*", name)

        def walk(node, owner=""):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.ClassDef):
                    walk(child, child.name)
                elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    sym = f"{owner}.{child.name}" if owner else child.name
                    if isinstance(child, ast.AsyncFunctionDef):
                        v = _Fn(child)
                        for stmt in child.body:
                            v.visit(stmt)
                        for (recv, name), locked in v.calls:
                            call_sites.setdefault(key(recv, name), []).append(((mod, child.name), locked))
                        if v.loads:
                            first = min(l for l, _, _ in v.loads)
                            after = [(l, w) for l, w in v.writes if l > first]
                            if after:
                                seams.append({
                                    "file": str(path.relative_to(pkg.parents[1])),
                                    "symbol": sym, "name": (mod, child.name), "line": first,
                                    "writes": sorted({w for _, w in after})[:8],
                                    "flag_before_await": any(fl < first for fl in v.flag_lines),
                                    "locked": all(lk for _, lk, _ in v.loads),
                                })
                    else:
                        v = _Fn(child)  # sync callers count for lock coverage too
                        for stmt in child.body:
                            v.visit(stmt)
                        for (recv, name), locked in v.calls:
                            call_sites.setdefault(key(recv, name), []).append(((mod, child.name), locked))
                    walk(child, owner)
        walk(tree)
    # transitive lock coverage: every call site is locked, or inside a covered function
    methods = {(pathlib.Path(s["file"]).stem, s["symbol"].split(".")[-1]) for s in seams if "." in s["symbol"]}

    def sites_of(fn):
        # a module-level function is reached by its bare name or module.name; a method by any receiver
        return call_sites.get(fn, []) + (call_sites.get(("*", fn[1]), []) if fn in methods else [])

    fns = {c for sites in call_sites.values() for c, _ in sites} | {s["name"] for s in seams}
    covered: set[tuple[str, str]] = set()
    changed = True
    while changed:
        changed = False
        for fn in fns:
            sites = sites_of(fn)
            if fn not in covered and sites and all(lk or caller in covered for caller, lk in sites):
                covered.add(fn); changed = True
    for s in seams:
        s["lock_covered"] = s["name"] in covered
        s["unlocked"] = not (s["locked"] or s["lock_covered"])
    return seams


CLEAN = '''
import asyncio
class Rec:
    def __init__(self): self.lock = asyncio.Lock(); self.data = {}; self.loaded = False
async def load(rec, store):
    async with rec.lock:
        if not rec.loaded:
            raw = await store.async_load()
            rec.data = raw; rec.loaded = True
async def peek(store):
    raw = await store.async_load()
    out = dict(raw or {})
    return out
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=pathlib.Path, default=PKG)
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--plant", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        root = a.root
        if a.clean:
            root = pathlib.Path(tmp) / "custom_components" / "clean"
            root.mkdir(parents=True)
            (root / "fixture.py").write_text(CLEAN)
        elif a.plant:
            root = pathlib.Path(tmp) / "custom_components" / "heatpump_optimizer"
            shutil.copytree(a.root, root)
            pa = root / "pump_arbiter.py"
            src = pa.read_text()
            needle = "    async with held.lock:\n        await _load(coord)\n        inp = coord.arbiter_inputs()\n"
            at = src.find(needle)  # the first is apply's; _lead_mode keeps its lock
            assert at > src.find("async def apply(") > 0 and at < src.find("async def _arbitrate("), "plant site moved"
            pa.write_text(src[:at] + "    if True:\n" + src[at + len("    async with held.lock:\n"):])
        seams = scan(root)
    if a.json:
        print(json.dumps(seams, indent=1))
    for s in seams:
        tag = "UNLOCKED" if s["unlocked"] else ("locked" if s["locked"] else "lock_covered")
        print(f"SEAM {tag:12s} flag_before_await={int(s['flag_before_await'])} {s['file']}:{s['line']} {s['symbol']} writes={s['writes']}")
    print(f"RESULT seams={len(seams)} unlocked={sum(s['unlocked'] for s in seams)} "
          f"flag_before_await_unlocked={sum(s['unlocked'] and s['flag_before_await'] for s in seams)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
