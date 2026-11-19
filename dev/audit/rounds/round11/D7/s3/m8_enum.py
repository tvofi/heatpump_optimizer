#!/usr/bin/env python3
"""D7.M8 (round 11, seat D7-s3): the enumerator of rules written twice.

Metric (one line): a `family` is a set of two or more package functions that state one rule --
(A) bodies whose normalised token streams match at ratio >= --ratio (default 0.72, at least 14 tokens, names
numbered, attribute and callee names kept), (B) one function name defined at module level in
two or more modules, (C) a non-trivial numeric literal within --tol (2 %) of another
literal of a different value in the package (one physical constant spelled twice), or (D) the
sites one of SEAMS's regular expressions finds in two or more places (a rule too small or too
differently spelled for A to join; each seam is code, and --list prints its site count), or
(E) a function and its twin by suffix (`_batch`, `_vec`, `_single`): one rule written for one
plan and for a batch of plans.

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --dispositions
        # every family against m8_families.tsv: a family with no row is NOT examined

    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --list   # one family per line
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s3/m8_enum.py --show A017

Instrumented symbols: every function of `custom_components/heatpump_optimizer/*.py`.
Static, exact; a seam rule written as code, not the census of `shape_copies` (which is the
floor below the clone window). Perturbation: `--plant` appends a renamed copy of
`inputs.py:temperature_c` to an in-memory copy; the A-family member count must rise by 1 (up).
Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692, Darwin arm64 / Python 3.14.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_k, "1")

import argparse
import ast
import collections
import difflib
import glob
import sys
import time

PKG = os.path.join("custom_components", "heatpump_optimizer")


def load_sources(root):
    return {os.path.basename(f): open(f, encoding="utf-8").read()
            for f in sorted(glob.glob(os.path.join(root, PKG, "*.py")))}


def tokens(fn):
    """The body as a token stream: node types, attribute and callee names, constants by value
    for numbers and by type for strings; local names numbered in order of first use."""
    names = {}
    out = []
    body = fn.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]

    def visit(n):
        if isinstance(n, ast.Name):
            out.append("n%d" % names.setdefault(n.id, len(names)))
            return
        if isinstance(n, ast.arg):
            out.append("n%d" % names.setdefault(n.arg, len(names)))
            return
        if isinstance(n, ast.Constant):
            v = n.value
            out.append("s" if isinstance(v, str) else repr(v))
            return
        if isinstance(n, ast.Attribute):
            visit(n.value)
            out.append("." + n.attr)
            return
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            out.append("call:" + n.func.id)
            for c in n.args:
                visit(c)
            for k in n.keywords:
                visit(k.value)
            return
        out.append(type(n).__name__)
        for c in ast.iter_child_nodes(n):
            if isinstance(c, (ast.expr_context, ast.operator, ast.cmpop, ast.boolop, ast.unaryop)):
                if not isinstance(c, ast.expr_context):
                    out.append(type(c).__name__)
                continue
            visit(c)

    for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs:
        names.setdefault(a.arg, len(names))
    for st in body:
        visit(st)
    return out


def functions(sources):
    out = []
    for rel, text in sources.items():
        tree = ast.parse(text)

        def walk(node, scope, in_class):
            for n in ast.iter_child_nodes(node):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.append({"file": rel, "qual": ".".join(scope + [n.name]), "name": n.name,
                                "line": n.lineno, "end": n.end_lineno, "node": n,
                                "top": not scope, "method": in_class})
                    walk(n, scope + [n.name], False)
                elif isinstance(n, ast.ClassDef):
                    walk(n, scope + [n.name], True)
                else:
                    walk(n, scope, in_class)

        walk(tree, [], False)
    return out


def families_a(funcs, ratio, min_tokens):
    items = []
    for f in funcs:
        t = tokens(f["node"])
        if len(t) >= min_tokens:
            items.append((f, t, collections.Counter(t)))
    items.sort(key=lambda x: len(x[1]))
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    pair_ratio = {}
    for i in range(len(items)):
        fi, ti, ci = items[i]
        li = len(ti)
        for j in range(i + 1, len(items)):
            fj, tj, cj = items[j]
            lj = len(tj)
            if lj * ratio > li * (2 - ratio) + 1e-9:  # 2*li/(li+lj) < ratio
                break
            common = sum((ci & cj).values())
            if 2.0 * common / (li + lj) < ratio:
                continue
            r = difflib.SequenceMatcher(None, ti, tj, autojunk=False).ratio()
            if r >= ratio:
                pair_ratio[(i, j)] = r
                a, b = find(i), find(j)
                if a != b:
                    parent[a] = b
    groups = collections.defaultdict(list)
    for i in range(len(items)):
        groups[find(i)].append(i)
    fams = []
    for g in groups.values():
        if len(g) < 2:
            continue
        members = [items[i][0] for i in g]
        rs = [r for (i, j), r in pair_ratio.items() if i in g and j in g]
        fams.append({"members": sorted(members, key=lambda f: (f["file"], f["line"])),
                     "min_ratio": min(rs), "max_ratio": max(rs),
                     "tokens": len(items[g[0]][1])})
    fams.sort(key=lambda f: (f["members"][0]["file"], f["members"][0]["line"]))
    return fams


def families_b(funcs):
    by = collections.defaultdict(list)
    for f in funcs:
        if f["top"]:
            by[f["name"]].append(f)
    return [{"members": v} for k, v in sorted(by.items()) if len({m["file"] for m in v}) > 1]


TRIVIAL = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 24, 25, 30, 45, 50, 60, 90, 100, 120, 180,
           360, 365, 1000, 1440, 3600, 0.5, 0.1, 0.25, 0.01, 0.05, 0.2, 0.75, 1.5, 2.5, 0.001, 1e-6,
           1e-9, 1e-3, 0.9, 0.95, 0.8, 0.3, 0.4, 0.6, 0.7, 0.15, 0.02, 1e-12, 0.99, 1.1, 1.2, 1.25,
           0.35, 0.85, 0.65, 0.45, 0.55, 3.5, 4.5, 5.5, 6.5, 7.5, 0.03, 0.04, 0.06, 0.08, 1.05}


def families_c(sources, tol):
    lits = collections.defaultdict(list)
    for rel, text in sources.items():
        for n in ast.walk(ast.parse(text)):
            if isinstance(n, ast.Constant) and isinstance(n.value, float) and not isinstance(n.value, bool):
                v = abs(n.value)
                if v in TRIVIAL or v == 0 or v != v or v in (float("inf"),):
                    continue
                # a literal with three or more significant digits is a measured constant
                s = repr(v).replace(".", "").strip("0").split("e")[0]
                if len(s) < 3:
                    continue
                lits[v].append((rel, n.lineno))
    vals = sorted(lits)
    fams = []
    used = set()
    for i, v in enumerate(vals):
        near = [w for w in vals[i + 1:] if w <= v * (1 + tol)]
        if near and v not in used:
            group = [v] + near
            used.update(group)
            fams.append({"values": group, "sites": {g: lits[g] for g in group}})
    return fams


# (D) seam rules written as code: a name and the expression whose matches are the rule's sites.
SEAMS = (
    ("D001", "a state holding no value", r"""["']unknown["'],\s*["']unavailable["']|["']unavailable["'],\s*["']unknown["']"""),
    ("D002", "the zone of a naive instant", r"tzinfo is None|\.replace\(tzinfo=|\.astimezone\(|as_utc\("),
    ("D003", "a finite number or nothing", r"def (finite_float|payload_number|_as_float|numeric|_number|_stored_number)\("),
    ("D004", "the value a save would leave", r"def _?effective\("),
    ("D005", "the plan step covering now", r"bisect_right\("),
    ("D006", "the mean of a metering window", r"project_window_mean\(|def window_snapshot\(|window_minutes"),
    ("D007", "the switch weight of a plan", r"def switch_weights?(_batch)?\("),
    # (F) a rule and its inverse: a writer and the reader of what it wrote
    ("F001", "a spec's parser and its formatter (dhw_schedule)", r"^def _?(parse|format)_(day_selector|time|clock|windows|weekly_windows)\("),
    ("F002", "a record's as_dict and its from_dict", r"^    def (as_dict|from_dict)\("),
    ("F003", "a unit table's forward and backward conversion", r"TEMPERATURE_UNIT_TO_C\.get\("),
    ("F004", "a store temperature and the tap temperature it delivers", r"def (store_temp_for_tap|tap_temp_for_store)\("),
)


def families_d(sources):
    import re
    out = []
    for fid, name, pattern in SEAMS:
        rx = re.compile(pattern)
        sites = []
        for rel, text in sources.items():
            for i, ln in enumerate(text.splitlines(), 1):
                if rx.search(ln) and not ln.lstrip().startswith("#"):
                    sites.append("%s:%d" % (rel, i))
        if len(sites) >= 2:
            out.append({"id": fid, "name": name, "pattern": pattern, "sites": sites})
    return out


TWIN_SUFFIXES = ("_batch", "_vec", "_single")


def families_e(funcs):
    by = collections.defaultdict(list)
    for f in funcs:
        by[f["name"]].append(f)
    out = []
    for name in sorted(by):
        for suf in TWIN_SUFFIXES:
            if name.endswith(suf):
                base = name[:-len(suf)]
                twin = by.get(base) or by.get(base.lstrip("_"))
                if twin:
                    out.append({"members": twin[:1] + by[name][:1]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dispositions", action="store_true")
    ap.add_argument("--root", default=".")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--show")
    ap.add_argument("--ratio", type=float, default=0.72)
    ap.add_argument("--min-tokens", type=int, default=14)
    ap.add_argument("--tol", type=float, default=0.02)
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    t0p, t0t = time.process_time(), time.thread_time()
    sources = load_sources(a.root)
    funcs = functions(sources)
    fa = families_a(funcs, a.ratio, a.min_tokens)
    fb = families_b(funcs)
    fc = families_c(sources, a.tol)
    lines = []
    for i, f in enumerate(fa, 1):
        lines.append(("A%03d" % i, "ratio=%.2f-%.2f tokens~%d " % (f["min_ratio"], f["max_ratio"], f["tokens"]) +
                      " | ".join("%s:%s:%d" % (m["file"], m["qual"], m["line"]) for m in f["members"]), f))
    for i, f in enumerate(fb, 1):
        lines.append(("B%03d" % i, " | ".join("%s:%s:%d" % (m["file"], m["qual"], m["line"]) for m in f["members"]), f))
    for i, f in enumerate(fc, 1):
        lines.append(("C%03d" % i, " ~ ".join("%r@%s" % (v, ",".join("%s:%d" % s for s in f["sites"][v][:3]))
                                               for v in f["values"]), f))
    for i, f in enumerate(families_e(funcs), 1):
        lines.append(("E%03d" % i, " | ".join("%s:%s:%d" % (m["file"], m["qual"], m["line"]) for m in f["members"]), f))
    for f in families_d(sources):
        lines.append((f["id"], "%s: %d sites of /%s/ (%s ...)" % (f["name"], len(f["sites"]), f["pattern"],
                                                                 ", ".join(f["sites"][:4])), f))
    if a.dispositions:
        here = os.path.dirname(os.path.abspath(__file__))
        rows = {}
        for ln in open(os.path.join(here, "m8_families.tsv"), encoding="utf-8"):
            if ln.strip() and not ln.startswith("#"):
                parts = ln.rstrip("\n").split("\t")
                rows[parts[0]] = parts[1]
        missing = [fid for fid, _t, _f in lines if fid not in rows]
        extra = sorted(set(rows) - {fid for fid, _t, _f in lines})
        counts = collections.Counter(rows[fid] for fid, _t, _f in lines if fid in rows)
        for fid in missing:
            print("NOT_EXAMINED", fid)
        for fid in extra:
            print("STALE_ROW", fid)
        print("RESULT universe=%d families" % len(lines))
        print("RESULT examined=%d families" % (len(lines) - len(missing)))
        for k in ("probed", "construction", "siblings", "unrelated"):
            print("RESULT %s=%d families" % (k, counts.get(k, 0)))
        return 0
    if a.show:
        for fid, text, f in lines:
            if fid == a.show:
                print(fid, text)
                for m in f.get("members", []):
                    src = sources[m["file"]].splitlines()[m["line"] - 1:m["end"]]
                    print("---- %s:%s:%d" % (m["file"], m["qual"], m["line"]))
                    print("\n".join(src))
        return 0
    if a.list:
        for fid, text, _f in lines:
            print(fid, text)
        return 0
    for fid, text, _f in lines:
        print("ROW", fid, text)
    print("RESULT families_A=%d families" % len(fa))
    print("RESULT families_B=%d families" % len(fb))
    print("RESULT families_C=%d families" % len(fc))
    print("RESULT families_D=%d families" % len(families_d(sources)))
    print("RESULT families_E=%d families" % len(families_e(funcs)))
    print("RESULT universe=%d families" % len(lines))
    if a.plant:
        planted = dict(sources)
        src = sources["inputs.py"]
        node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "temperature_c")
        seg = "\n".join(src.splitlines()[node.lineno - 1:node.end_lineno]).replace("def temperature_c", "def _d7s3_planted_copy")
        planted["wear.py"] += "\n\n" + seg + "\n"
        fa2 = families_a(functions(planted), a.ratio, a.min_tokens)
        print("RESULT planted_member_delta=%d functions" % (
            sum(len(f["members"]) for f in fa2) - sum(len(f["members"]) for f in fa)))
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
