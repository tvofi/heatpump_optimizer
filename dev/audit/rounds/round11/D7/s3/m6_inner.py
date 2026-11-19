#!/usr/bin/env python3
"""D7.M6 (round 11, seat D7-s3), second census: dead state inside live code.

Metric (one line): an instance attribute is `write_only` when the package stores `self.<a>`
(or `<obj>.<a>`) and no code of the package loads an attribute or names a string `<a>`; a
parameter is `unread` when its function's body never loads it; a local is `unread` when its
function stores it and never loads it; a dataclass field is `unread` when no code of the
package loads an attribute or names a string of its name; a module-level function is `masked`
when every naming of it in the package is an attribute read off a non-module receiver.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_inner.py --list   # the universe
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_inner.py          # the census
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m6_inner.py --perturb

Instrumented symbols: every `self.<attr>` store, parameter and local of
`custom_components/heatpump_optimizer/*.py` (static counts, no timing).
Count key: (file, owner, name) of the stored attribute, parameter or local; a fix deletes the
store or adds a production reader. Perturbation (`--perturb`): append a reader of every reported
attribute to an in-memory copy; `write_only` must fall to 0 (to_zero); a planted
`self._d7s3_planted = 1` must raise it by exactly 1.
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, Darwin arm64 / Python 3.14; exact.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import glob
import re
import sys
import time

PKG = os.path.join("custom_components", "heatpump_optimizer")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def load_sources(root):
    return {os.path.basename(f): open(f, encoding="utf-8").read()
            for f in sorted(glob.glob(os.path.join(root, PKG, "*.py")))}


def words_in(root, pats):
    out = set()
    for pat in pats:
        for f in glob.glob(os.path.join(root, pat), recursive=True):
            try:
                out.update(WORD.findall(open(f, encoding="utf-8").read()))
            except (OSError, UnicodeDecodeError):
                pass
    return out


def census(sources):
    attr_stores = {}   # name -> [(file, owner, line)]
    attr_loads = set()
    strings = set()
    params, locals_ = [], []
    fields = []
    module_funcs = {}  # name -> [(file, line)]
    name_refs = {}     # name -> count of Name loads / import aliases, by file
    modattr_refs = set()
    universe = []
    for rel, text in sources.items():
        tree = ast.parse(text)
        mod_bound = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names:
                    mod_bound.add(a.asname or a.name.split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                for a in n.names:
                    mod_bound.add(a.asname or a.name)  # may be a module; conservative
                    name_refs.setdefault(a.name, set()).add(rel)
        for st in tree.body:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                module_funcs.setdefault(st.name, []).append((rel, st.lineno))
        parents = {}
        for n in ast.walk(tree):
            for c in ast.iter_child_nodes(n):
                parents[c] = n

        def owner_of(n):
            names = []
            while n in parents:
                n = parents[n]
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    names.append(n.name)
            return ".".join(reversed(names)) or "<module>"

        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef) and any(
                    (getattr(d, "id", None) or getattr(getattr(d, "func", None), "id", None)) == "dataclass"
                    for d in n.decorator_list):
                for st in n.body:
                    if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                        ann = ast.unparse(st.annotation)
                        if "ClassVar" in ann or "InitVar" in ann:
                            continue
                        fields.append((rel, n.name, st.target.id, st.lineno))
                        universe.append("%s:%s.%s [dataclass-field]" % (rel, n.name, st.target.id))
            if isinstance(n, ast.Attribute):
                if isinstance(n.ctx, ast.Store):
                    # an augmented assignment loads what it stores; that read feeds only itself
                    attr_stores.setdefault(n.attr, []).append((rel, owner_of(n), n.lineno))
                    universe.append("%s:%s.%s [attribute-store]" % (rel, owner_of(n), n.attr))
                else:
                    attr_loads.add(n.attr)
                    if isinstance(n.value, ast.Name) and n.value.id in mod_bound:
                        modattr_refs.add(n.attr)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                name_refs.setdefault(n.id, set()).add(rel)
            elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                if IDENT.match(n.value):
                    strings.add(n.value)
                elif len(n.value) < 200:
                    strings.update(WORD.findall(n.value)) if re.match(r"^[\w.\[\]]+$", n.value) else None
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                loads, stores, declared = set(), {}, set()
                for m in ast.walk(n):
                    if isinstance(m, ast.Name):
                        if isinstance(m.ctx, ast.Load) or isinstance(m.ctx, ast.Del):
                            loads.add(m.id)
                        else:
                            stores.setdefault(m.id, m.lineno)
                    elif isinstance(m, (ast.Global, ast.Nonlocal)):
                        declared.update(m.names)
                    elif isinstance(m, ast.AugAssign) and isinstance(m.target, ast.Name):
                        pass
                    elif isinstance(m, ast.Call) and getattr(m.func, "id", "") in ("locals", "vars"):
                        loads.add("*")
                body = n.body
                if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
                    body = body[1:]
                trivial = (not body or all(isinstance(b, (ast.Pass, ast.Raise)) or
                                           (isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant)) or
                                           (isinstance(b, ast.Return) and (b.value is None or isinstance(b.value, ast.Constant)))
                                           for b in body))
                own = owner_of(n)
                qual = (own + "." if own != "<module>" else "") + n.name
                in_class = isinstance(parents.get(n), ast.ClassDef)
                allargs = n.args.posonlyargs + n.args.args + n.args.kwonlyargs
                for i, a in enumerate(allargs):
                    if i == 0 and in_class and a.arg in ("self", "cls", "mcs"):
                        continue
                    universe.append("%s:%s(%s) [parameter]" % (rel, qual, a.arg))
                    if a.arg in loads or "*" in loads or a.arg.startswith("_") or trivial:
                        continue
                    params.append((rel, qual, a.arg, n.lineno, n.name, in_class,
                                   bool(n.decorator_list)))
                argnames = {a.arg for a in allargs} | {x.arg for x in (n.args.vararg, n.args.kwarg) if x}
                for name, line in stores.items():
                    if name in argnames:
                        continue
                    universe.append("%s:%s:%s [local]" % (rel, qual, name))
                    if name in loads or "*" in loads or name in declared or name.startswith("_"):
                        continue
                    locals_.append((rel, qual, name, line))
    return {"attr_stores": attr_stores, "attr_loads": attr_loads, "strings": strings,
            "params": params, "locals": locals_, "module_funcs": module_funcs, "fields": fields,
            "name_refs": name_refs, "modattr_refs": modattr_refs, "universe": universe}


def write_only(c):
    out = []
    for name, sites in sorted(c["attr_stores"].items()):
        if name in c["attr_loads"] or name in c["strings"]:
            continue
        out.append((name, sites))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    sources = load_sources(a.root)
    c = census(sources)
    if a.list:
        for u in c["universe"]:
            print(u)
        for name, sites in sorted(c["module_funcs"].items()):
            for rel, line in sites:
                print("%s:%s [module-function-naming]" % (rel, name))
        return 0
    tw = words_in(a.root, ("tests/*.py", "tests/*.mjs"))
    hastub = words_in(a.root, ("tests/hastub/**/*.py",))
    wo = write_only(c)
    n_wo = n_wo_fw = n_wo_tests = 0
    for name, sites in wo:
        cls = "write_only"
        if name in hastub or name.startswith("_attr_"):
            cls = "framework_read"      # Home Assistant reads `_attr_*` and entity fields
            n_wo_fw += 1
        elif name in tw:
            cls = "test_read_only"
            n_wo_tests += 1
        else:
            n_wo += 1
        print("ROW %s attribute %s stores=%d first=%s:%d owner=%s" % (
            cls, name, len(sites), sites[0][0], sites[0][2], sites[0][1]))
    # parameters: a name another definition shares is a protocol's signature, not a dead input
    shared = {}
    for rel, text in sources.items():
        for n in ast.walk(ast.parse(text)):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                shared[n.name] = shared.get(n.name, 0) + 1
    n_par = n_par_proto = 0
    for rel, qual, arg, line, fname, in_class, decorated in c["params"]:
        proto = shared.get(fname, 0) > 1 or fname in hastub or fname.startswith("async_") or decorated
        cls = "protocol_param" if proto else "unread_param"
        n_par_proto += proto
        n_par += (not proto)
        if not proto:
            print("ROW %s parameter %s:%d %s(%s)" % (cls, rel, line, qual, arg))
    for rel, qual, name, line in c["locals"]:
        print("ROW unread_local local %s:%d %s:%s" % (rel, line, qual, name))
    n_fields = n_fields_tests = 0
    for rel, cls_name, name, line in c["fields"]:
        if name in c["attr_loads"] or name in c["strings"]:
            continue
        if name in tw:
            n_fields_tests += 1
            print("ROW test_read_only field %s:%d %s.%s" % (rel, line, cls_name, name))
        else:
            n_fields += 1
            print("ROW unread_field field %s:%d %s.%s" % (rel, line, cls_name, name))
    masked = []
    for name, sites in sorted(c["module_funcs"].items()):
        direct = c["name_refs"].get(name, set())
        if direct or name in c["modattr_refs"] or name in c["strings"]:
            continue
        if name in c["attr_loads"]:
            masked.append((name, sites))
    for name, sites in masked:
        for rel, line in sites:
            print("ROW masked function %s:%d %s named_in_tests=%s" % (rel, line, name, name in tw))
    print("RESULT universe=%d items" % (len(c["universe"]) + sum(len(s) for s in c["module_funcs"].values())))
    print("RESULT write_only_attributes=%d attributes" % n_wo)
    print("RESULT test_read_only_attributes=%d attributes" % n_wo_tests)
    print("RESULT framework_read_attributes=%d attributes" % n_wo_fw)
    print("RESULT unread_params=%d parameters" % n_par)
    print("RESULT protocol_params=%d parameters" % n_par_proto)
    print("RESULT unread_locals=%d locals" % len(c["locals"]))
    print("RESULT unread_fields=%d fields" % n_fields)
    print("RESULT test_read_only_fields=%d fields" % n_fields_tests)
    print("RESULT masked_functions=%d functions" % sum(len(s) for _n, s in masked))
    if a.perturb:
        planted = dict(sources)
        planted["wear.py"] += "\n\nclass _D7S3Planted:\n    def __init__(self):\n        self._d7s3_planted = 1\n"
        print("RESULT planted_delta=%d attributes" % (len(write_only(census(planted))) - len(wo)))
        fixed = dict(sources)
        fixed["wear.py"] += "\n\ndef _d7s3_readers(o):\n    return (" + ", ".join("o.%s" % n for n, _s in wo) + ",)\n"
        print("RESULT write_only_after_readers=%d attributes" % len(write_only(census(fixed))))
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
