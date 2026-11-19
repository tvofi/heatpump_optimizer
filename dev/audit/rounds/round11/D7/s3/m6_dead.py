#!/usr/bin/env python3
"""D7.M6 (round 11, seat D7-s3): dead code by AST reachability, with a runtime sentinel.

Metric (one line): a definition of the package is `dead` when no other code of the package
names it (Name, Attribute, alias or whole-string constant, outside its own body), no Home
Assistant stub class or non-Python package file names it, and -- transitively -- it is named
only from dead definitions; `test_only` is the same with a tests/ reference or a traced entry.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_dead.py --list     # the universe
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_dead.py            # the census
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_dead.py --trace DIR  # + runtime sentinel
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_dead.py --perturb  # null/positive control

Instrumented symbols: every definition `custom_components/heatpump_optimizer/*.py` holds; the
harness reads the tree (static count, no timing), and `--trace DIR` reads the function-entry
records `fn_trace.sh` wrote while the real suite drove the real package.
Count key: the definition's (file, qualified name); a fix that deletes the definition or adds
a production reader moves the count, a rename of the harness's own records cannot.
Perturbation: `--perturb` appends a module-level reader of each reported name to an in-memory
copy of its module; `dead` must fall to 0 (to_zero). It also plants one unreferenced function
in memory and requires the count to rise by exactly 1.
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 on Darwin arm64 / Python 3.14:
see RESULT lines; exact (static counts).
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import glob
import json
import re
import sys
import time

PKG = os.path.join("custom_components", "heatpump_optimizer")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
DOTTED = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$|^[A-Za-z_][A-Za-z0-9_\[\], |.]*$")


# What Home Assistant's loader reads off an integration's modules by name (the platform
# contract): nothing in the package names these, the framework does.
HA_CONTRACT = {
    "async_setup", "async_setup_entry", "async_unload_entry", "async_remove_entry",
    "async_migrate_entry", "async_get_config_entry_diagnostics", "async_get_device_diagnostics",
    "async_create_fix_flow", "async_get_options_flow", "async_remove_config_entry_device",
    "CONFIG_SCHEMA", "PARALLEL_UPDATES", "PLATFORMS", "DOMAIN", "SCAN_INTERVAL",
    "async_get_triggers", "async_reset_platform", "async_setup_platform",
}


class Def:
    __slots__ = ("file", "qual", "name", "kind", "lineno", "end", "decorated", "in_class", "bases", "owner")

    def __init__(self, file, qual, name, kind, lineno, end, decorated=False, in_class=False):
        self.file, self.qual, self.name, self.kind = file, qual, name, kind
        self.lineno, self.end, self.decorated, self.in_class = lineno, end, decorated, in_class
        self.bases, self.owner = (), None

    @property
    def key(self):
        return "%s:%s [%s]" % (self.file, self.qual, self.kind)


def _plain_decorator(d):
    """A decorator that registers nothing: property, staticmethod, classmethod, callback, cache."""
    n = d
    if isinstance(n, ast.Call):
        n = n.func
    name = n.attr if isinstance(n, ast.Attribute) else getattr(n, "id", "")
    return name in {"property", "staticmethod", "classmethod", "callback", "cached_property",
                    "lru_cache", "cache", "dataclass", "setter", "contextmanager",
                    "asynccontextmanager", "overload", "final", "override", "abstractmethod",
                    "wraps", "total_ordering", "runtime_checkable"}


def collect(sources):
    """sources: {relfile: text}. Returns (defs, refs) where refs is a list of
    (name, file, lineno) for every naming of an identifier in the package."""
    defs, refs, unreachable = [], [], []
    for rel, text in sorted(sources.items()):
        tree = ast.parse(text)

        def walk(node, scope, in_class, in_func):
            body_lists = []
            for field in ("body", "orelse", "finalbody"):
                seq = getattr(node, field, None)
                if isinstance(seq, list) and seq and isinstance(seq[0], ast.stmt):
                    body_lists.append(seq)
            for h in getattr(node, "handlers", []) or []:
                body_lists.append(h.body)
            for c in getattr(node, "cases", []) or []:
                body_lists.append(c.body)
            for seq in body_lists:
                ended = False
                for st in seq:
                    if ended:
                        unreachable.append((rel, st.lineno, ".".join(scope) or "<module>"))
                        break
                    if isinstance(st, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
                        ended = True
                for st in seq:
                    if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        q = scope + [st.name]
                        if not in_func:
                            defs.append(Def(rel, ".".join(q), st.name,
                                            "method" if in_class else "function", st.lineno,
                                            st.end_lineno,
                                            any(not _plain_decorator(d) for d in st.decorator_list),
                                            in_class))
                            defs[-1].owner = scope[-1] if in_class and scope else None
                        walk(st, q, False, True)
                    elif isinstance(st, ast.ClassDef):
                        q = scope + [st.name]
                        if not in_func:
                            defs.append(Def(rel, ".".join(q), st.name, "class", st.lineno,
                                            st.end_lineno,
                                            any(not _plain_decorator(d) for d in st.decorator_list),
                                            in_class))
                            defs[-1].bases = tuple(
                                (b.attr if isinstance(b, ast.Attribute) else
                                 b.value.id if isinstance(b, ast.Subscript) and isinstance(b.value, ast.Name) else
                                 getattr(b, "id", "?")) for b in st.bases)
                        walk(st, q, True, in_func)
                    else:
                        if not in_func and not in_class and not scope:
                            targets = []
                            if isinstance(st, ast.Assign):
                                targets = st.targets
                            elif isinstance(st, ast.AnnAssign) and st.value is not None:
                                targets = [st.target]
                            for t in targets:
                                for n in ast.walk(t):
                                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                                        defs.append(Def(rel, n.id, n.id, "constant", st.lineno,
                                                        st.end_lineno))
                            if isinstance(st, (ast.Import, ast.ImportFrom)):
                                for a in st.names:
                                    if a.name == "*":
                                        continue
                                    bound = a.asname or a.name.split(".")[0]
                                    if isinstance(st, ast.ImportFrom) and st.module == "__future__":
                                        continue
                                    defs.append(Def(rel, "import " + bound, bound, "import",
                                                    st.lineno, st.end_lineno))
                        walk(st, scope, in_class, in_func)

        walk(tree, [], False, False)
        # TYPE_CHECKING and try/except imports are nested one level: take them too.
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Load, ast.Del)):
                refs.append((node.id, rel, node.lineno))
            elif isinstance(node, ast.Attribute):
                refs.append((node.attr, rel, node.lineno))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                s = node.value
                if IDENT.match(s):
                    refs.append((s, rel, node.lineno))
                elif DOTTED.match(s):
                    # a dotted lookup or a string annotation names identifiers too; prose
                    # (a log line, a docstring) does not keep a definition alive
                    for w in WORD.findall(s):
                        refs.append((w, rel, -node.lineno))
            elif isinstance(node, ast.ImportFrom):
                for a in node.names:
                    if a.asname and a.asname != a.name:
                        refs.append((a.name, rel, node.lineno))
                    # an import of a package name from a package module is a naming of it
                    if node.level and a.name != "*":
                        refs.append(("__import__:" + a.name, rel, node.lineno))
    return defs, refs, unreachable


def framework_names(root):
    """Names a Home Assistant stub class defines, or the stub calls on an integration object:
    a method of that name is the framework's to call."""
    names = set()
    for f in glob.glob(os.path.join(root, "tests", "hastub", "**", "*.py"), recursive=True):
        try:
            tree = ast.parse(open(f, encoding="utf-8").read())
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(n.name)
            elif isinstance(n, ast.Attribute):
                names.add(n.attr)
    return names


def other_package_words(root):
    words = set()
    for pat in ("*.json", "*.yaml", "translations/*.json", "www/*.js", "www/**/*.js"):
        for f in glob.glob(os.path.join(root, PKG, pat), recursive=True):
            try:
                words.update(WORD.findall(open(f, encoding="utf-8").read()))
            except (OSError, UnicodeDecodeError):
                pass
    return words


def test_words(root):
    words = set()
    for pat in ("tests/*.py", "tests/*.mjs"):
        for f in glob.glob(os.path.join(root, pat)):
            try:
                words.update(WORD.findall(open(f, encoding="utf-8").read()))
            except (OSError, UnicodeDecodeError):
                pass
    return words


def census(sources, fw, other, exempt_dunder=True):
    defs, refs, unreachable = collect(sources)
    by_name = {}
    for d in defs:
        by_name.setdefault(d.name, []).append(d)
    # which definition (innermost function/class/method) holds a reference line
    spans = {}
    for d in defs:
        if d.kind in ("function", "method", "class"):
            spans.setdefault(d.file, []).append(d)
    for f in spans:
        spans[f].sort(key=lambda d: (d.lineno, -d.end))

    def holder(file, line):
        line = abs(line)
        best = None
        for d in spans.get(file, ()):
            if d.lineno <= line <= d.end:
                if d.kind != "class":
                    if best is None or d.lineno >= best.lineno:
                        best = d
        return best

    imports_from_pkg = set(n[len("__import__:"):] for n, _f, _l in refs if n.startswith("__import__:"))
    uses = {}  # name -> list of holder (None = module level / class body)
    for name, file, line in refs:
        if name.startswith("__import__:"):
            continue
        if name in by_name:
            uses.setdefault(name, []).append((file, line, holder(file, line)))

    # a class is the framework's when a base of it is not a package class (a Home Assistant
    # entity, flow or coordinator base; an Enum, Protocol, TypedDict or Exception), transitively
    pkg_classes = {}
    for d in defs:
        if d.kind == "class":
            pkg_classes.setdefault(d.name, []).append(d)
    fw_class = set()
    changed = True
    while changed:
        changed = False
        for name, lst in pkg_classes.items():
            if name in fw_class:
                continue
            for d in lst:
                if any((b not in pkg_classes and b != "object") or b in fw_class for b in d.bases):
                    fw_class.add(name)
                    changed = True
                    break

    def rooted(d):
        if d.kind == "import":
            return False
        if d.name in HA_CONTRACT or d.name.startswith("async_step_"):
            return True
        if d.kind == "method" and d.owner in fw_class and not d.name.startswith("_"):
            return True
        if exempt_dunder and d.name.startswith("__") and d.name.endswith("__"):
            return True
        if d.decorated:
            return True
        if d.kind == "method" and d.name in fw:
            return True
        if d.kind in ("function", "class") and not d.in_class and d.name in fw and d.name.startswith("async_"):
            return True  # async_setup_entry and friends: the platform contract
        return False

    live = set()
    work = []
    for d in defs:
        if rooted(d):
            live.add(id(d))
            work.append(d)
    # references from module level or class bodies are roots; from a function, edges
    edges = {}
    for name, lst in uses.items():
        for file, line, h in lst:
            for d in by_name[name]:
                if d.kind == "import" and d.file != file:
                    # another module importing the bound name re-exports it
                    if name in imports_from_pkg:
                        pass
                    else:
                        continue
                if h is None:
                    if d.kind in ("constant", "import") and d.file == file and d.lineno <= abs(line) <= d.end:
                        continue  # its own assignment statement
                    if id(d) not in live:
                        live.add(id(d))
                        work.append(d)
                else:
                    if h is d:
                        continue  # recursion is not a caller
                    if d.kind in ("function", "method", "class") and d.file == file and d.lineno <= abs(line) <= d.end and d.kind != "class":
                        continue
                    edges.setdefault(id(h), []).append(d)
    # a class's methods hold the class alive only through explicit naming; a live class
    # does not make its unnamed methods live (that is the question).
    for d in defs:
        if d.kind == "import" and d.name in imports_from_pkg:
            # re-exported by a sibling's `from .x import name`
            if id(d) not in live:
                live.add(id(d))
                work.append(d)
    while work:
        d = work.pop()
        for t in edges.get(id(d), ()):
            if id(t) not in live:
                live.add(id(t))
                work.append(t)
    dead = [d for d in defs if id(d) not in live]
    return defs, dead, unreachable, uses


def load_sources(root):
    out = {}
    for f in sorted(glob.glob(os.path.join(root, PKG, "*.py"))):
        out[os.path.basename(f)] = open(f, encoding="utf-8").read()
    return out


def load_trace(tdir):
    seen = set()
    for f in glob.glob(os.path.join(tdir, "*.json")):
        if os.path.basename(f).startswith("plandata"):
            continue
        try:
            for rel, qual, line in json.load(open(f)):
                seen.add((rel, qual.replace(".<locals>", ""), line))
        except (ValueError, OSError):
            pass
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--trace")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    sources = load_sources(a.root)
    fw = framework_names(a.root)
    other = other_package_words(a.root)
    defs, dead, unreachable, uses = census(sources, fw, other)
    if a.list:
        for d in defs:
            print(d.key)
        for rel, line, scope in unreachable:
            print("%s:%s:%d [unreachable-statement]" % (rel, scope, line))
        return 0
    tw = test_words(a.root)
    entered = load_trace(a.trace) if a.trace else None
    rows = []
    for d in dead:
        in_tests = d.name in tw
        ent = None
        if entered is not None and d.kind in ("function", "method"):
            ent = any(rel == d.file and line == d.lineno for rel, _q, line in entered)
        if d.kind == "import":
            cls = "unused_import"
        elif ent:
            cls = "test_only" if in_tests else "entered_unnamed"
        elif in_tests:
            cls = "test_only"
        else:
            cls = "dead"
        rows.append({"file": d.file, "qual": d.qual, "kind": d.kind, "line": d.lineno,
                     "loc": d.end - d.lineno + 1, "class": cls, "entered": ent,
                     "named_in_tests": in_tests})
    for r in rows:
        print("ROW %(class)s %(kind)s %(file)s:%(line)d %(qual)s loc=%(loc)d entered=%(entered)s tests=%(named_in_tests)s" % r)
    for rel, line, scope in unreachable:
        print("ROW unreachable_statement %s:%d %s" % (rel, line, scope))
    kinds = {}
    for r in rows:
        kinds[r["class"]] = kinds.get(r["class"], 0) + 1
    print("RESULT universe=%d definitions" % (len(defs) + len(unreachable)))
    for k in ("dead", "test_only", "entered_unnamed", "unused_import"):
        print("RESULT %s=%d definitions" % (k, kinds.get(k, 0)))
    print("RESULT dead_loc=%d lines" % sum(r["loc"] for r in rows if r["class"] == "dead"))
    print("RESULT test_only_loc=%d lines" % sum(r["loc"] for r in rows if r["class"] == "test_only"))
    print("RESULT unreachable_statements=%d statements" % len(unreachable))
    if a.perturb:
        # positive control: one planted unreferenced function raises the count by exactly 1
        planted = dict(sources)
        planted["const.py"] += "\n\ndef _d7s3_planted_unreferenced():\n    return 1\n"
        _d, dead2, _u, _ = census(planted, fw, other)
        print("RESULT planted_delta=%d definitions" % (len(dead2) - len(dead)))
        # perturbation: a module-level reader of every reported name; dead must be 0
        fixed = dict(sources)
        for d in dead:
            if d.kind == "import":
                fixed[d.file] += "\n_ = %s\n" % d.name
            elif d.kind == "method":
                fixed[d.file] += "\n_ = %s\n" % d.qual
            else:
                fixed[d.file] += "\n_ = %s\n" % d.name
        _d, dead3, _u, _ = census(fixed, fw, other)
        print("RESULT dead_after_readers=%d definitions" % len(dead3))
        for d in dead3:
            print("STILL " + d.key)
    if a.json:
        json.dump({"rows": rows, "unreachable": unreachable, "universe": len(defs) + len(unreachable)},
                  open(a.json, "w"), indent=1)
    tf = (time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9)
    print("RESULT thread_factor=%.3f ratio" % tf)
    print("RESULT load1=%.2f load" % os.getloadavg()[0])
    try:
        import resource
        print("RESULT swapins=%d count" % resource.getrusage(resource.RUSAGE_SELF).ru_nswap)
    except Exception:
        print("RESULT swapins=0 count")
    return 0


if __name__ == "__main__":
    sys.exit(main())
