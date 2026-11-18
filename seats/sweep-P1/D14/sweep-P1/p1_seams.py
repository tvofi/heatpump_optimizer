#!/usr/bin/env python3
"""Round-11 class sweep P1 (D14 steps 3-4): every seam of the class's seven judged shapes.

Class P1: a non-finite, malformed or out-of-domain value crosses an input boundary
with no guard. Each judged finding of round 11 is one shape of that boundary; this
enumerator lists every function in the package that carries the shape (a SEAM),
and flags the seams where the guard the finding names is absent (FLAG).

Families (seam rule -> flag rule):
  num-flag       a flag computed from float(x) compared with 0 (parse_bool, D1-s3-01)
                 -> FLAG when the function never calls math.isfinite/isnan/isinf
  bool-number    isinstance(x, (int, float)) accepting a JSON/stored/payload value as a
                 number (_parse_ecl110_state, D1-s3-02)
                 -> FLAG when the same function never tests isinstance(<x>, bool)
  dyn-timedelta  timedelta(<unit>=<expr>) whose expr is read off a mapping in the same
                 function (boost._restore_settle, D1-s2-06)
                 -> FLAG when no finite upper bound (a compare with a finite literal or
                    an UPPER_CASE constant, or min()) touches that name
  opt-float      float(<cfg>.get(...)) on an options/config mapping (comfort_band.effective,
                 thermal_model, D1-s2-05)
                 -> FLAG when no enclosing try catches ValueError/TypeError/Exception
  window         a function reading a *PLAUSIBLE* window (inputs.plausible_c, D1-s2-51)
                 -> FLAG when it compares against one bound only
  feed-instant   datetime.fromisoformat / parse_datetime of a feed stamp inside a parser
                 (open_meteo._parse_block, D1-s3-03)
                 -> FLAG when the function never bounds the parsed instant (no .year,
                    no compare of the parsed name, no stored_instant/bounded helper)
  store-leaf     the store's leaf predicate _poisoned (D1-s2-01)
                 -> FLAG when its float branch never calls math.isfinite

  python3 p1_seams.py [--root DIR] [--null] [--perturb FAMILY] [--flagged]
--null runs on the clean fixture below (every family guarded): seams_flagged must be 0.
--perturb FAMILY re-introduces that family's shape with one line in the fixture: 1.
Prints `SEAM <family> <file>::<qualname> <FLAG|ok> <line>` then RESULT lines.
"""
from __future__ import annotations

import argparse
import ast
import sys
import tempfile
from pathlib import Path

PKG = "custom_components/heatpump_optimizer"
FAMILIES = ("num-flag", "bool-number", "dyn-timedelta", "opt-float", "window", "feed-instant", "store-leaf")
CFG_NAMES = ("config", "candidate", "options", "opts", "merged", "entry_options", "data_in")
TIME_PARSERS = ("fromisoformat", "parse_datetime")
BOUNDED_HELPERS = ("stored_instant", "bounded_instant", "_plausible_instant", "parse_feed_instant")


def _name(node):
    return node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else None


def _calls(fn, names):
    return any(isinstance(n, ast.Call) and _name(n.func) in names for n in ast.walk(fn))


def _const_like(e):
    if isinstance(e, ast.Constant):
        return True
    if isinstance(e, ast.Name):
        return e.id.isupper() or e.id.lstrip("_").isupper()
    if isinstance(e, ast.Attribute):
        return e.attr.lstrip("_").isupper()
    if isinstance(e, ast.UnaryOp):
        return _const_like(e.operand)
    if isinstance(e, ast.BinOp):
        return _const_like(e.left) and _const_like(e.right)
    return False


def _finite_bound(e):
    if isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) and not isinstance(e.value, bool):
        return e.value not in (float("inf"),)
    return _const_like(e) and not (isinstance(e, ast.Attribute) and e.attr == "inf")


def _functions(tree):
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = f"{prefix}{ch.name}"
                out.append((q, ch))
                walk(ch, q + ".")
            elif isinstance(ch, ast.ClassDef):
                walk(ch, f"{prefix}{ch.name}.")
            else:
                walk(ch, prefix)
    walk(tree, "")
    return out


def _own_nodes(fn):
    """Nodes of fn, not of functions nested in it."""
    stack, out = list(ast.iter_child_nodes(fn)), []
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        out.append(n)
        stack.extend(ast.iter_child_nodes(n))
    return out


def _mapping_read_names(nodes):
    names = set()
    for n in nodes:
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.Call, ast.Subscript)):
            v = n.value
            src = v.func if isinstance(v, ast.Call) else v
            if (isinstance(v, ast.Subscript) and isinstance(v.slice, ast.Constant) and isinstance(v.slice.value, str)) or \
               (isinstance(v, ast.Call) and isinstance(src, ast.Attribute) and src.attr == "get"):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
    return names


def _is_float_call(e):
    return isinstance(e, ast.Call) and _name(e.func) == "float"


def _try_guarded(parents, node):
    p = parents.get(node)
    while p is not None:
        if isinstance(p, ast.Try):
            for h in p.handlers:
                t = h.type
                names = [_name(x) for x in (t.elts if isinstance(t, ast.Tuple) else [t])] if t is not None else ["*"]
                if set(names) & {"ValueError", "TypeError", "Exception", "*"}:
                    return True
        if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        p = parents.get(p)
    return False


def scan_module(rel, src):
    tree = ast.parse(src)
    parents = {c: p for p in ast.walk(tree) for c in ast.iter_child_nodes(p)}
    seams = []
    for q, fn in _functions(tree):
        own = _own_nodes(fn)
        finite = _calls(fn, {"isfinite", "isnan", "isinf"})
        # num-flag
        floats = {t.id for n in own if isinstance(n, ast.Assign) and _is_float_call(n.value)
                  for t in n.targets if isinstance(t, ast.Name)}
        fl = lambda e: _is_float_call(e) or (isinstance(e, ast.Name) and e.id in floats)
        for n in own:
            if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], (ast.NotEq, ast.Eq)):
                l, r = n.left, n.comparators[0]
                if (fl(l) and isinstance(r, ast.Constant) and r.value == 0) or \
                   (fl(r) and isinstance(l, ast.Constant) and l.value == 0):
                    seams.append(("num-flag", q, not finite, n.lineno)); break
        # bool-number
        for n in own:
            if isinstance(n, ast.Call) and _name(n.func) == "isinstance" and len(n.args) == 2:
                t = n.args[1]
                kinds = {_name(x) for x in t.elts} if isinstance(t, ast.Tuple) else {_name(t)}
                if {"int", "float"} <= kinds and "bool" not in kinds:
                    subj = ast.dump(n.args[0])
                    excl = any(isinstance(m, ast.Call) and _name(m.func) == "isinstance" and len(m.args) == 2
                               and ast.dump(m.args[0]) == subj and _name(m.args[1]) == "bool" for m in own)
                    seams.append(("bool-number", q, not excl, n.lineno)); break
        # dyn-timedelta
        reads = _mapping_read_names(own)
        for n in own:
            if isinstance(n, ast.Call) and _name(n.func) == "timedelta":
                for kw in n.keywords:
                    v = kw.value
                    if isinstance(v, ast.Name) and v.id in reads:
                        bounded = False
                        for m in own:
                            if isinstance(m, ast.Compare):
                                parts = [m.left, *m.comparators]
                                for i, op in enumerate(m.ops):
                                    a, b = parts[i], parts[i + 1]
                                    if isinstance(op, (ast.Lt, ast.LtE)) and isinstance(a, ast.Name) and a.id == v.id and _finite_bound(b):
                                        bounded = True
                                    if isinstance(op, (ast.Gt, ast.GtE)) and isinstance(b, ast.Name) and b.id == v.id and _finite_bound(a):
                                        bounded = True
                            if isinstance(m, ast.Call) and _name(m.func) == "min" and any(isinstance(a, ast.Name) and a.id == v.id for a in m.args):
                                bounded = True
                        seams.append(("dyn-timedelta", q, not bounded, n.lineno))
                        break
        # opt-float
        for n in own:
            if _is_float_call(n) and n.args and isinstance(n.args[0], ast.Call):
                g = n.args[0]
                if isinstance(g.func, ast.Attribute) and g.func.attr == "get" and isinstance(g.func.value, ast.Name) \
                   and g.func.value.id in CFG_NAMES:
                    seams.append(("opt-float", q, not _try_guarded(parents, n), n.lineno)); break
        # window
        logged = {id(x) for c in own if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                  and isinstance(c.func.value, ast.Name) and c.func.value.id.lstrip("_").upper() in ("LOGGER", "LOG")
                  for x in ast.walk(c)}
        wnames = [n for n in own if isinstance(n, (ast.Name, ast.Attribute)) and "PLAUSIBLE" in (_name(n) or "")
                  and id(n) not in logged]
        if wnames:
            others = {}
            for m in own:
                if isinstance(m, ast.Compare) and all(isinstance(o, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for o in m.ops):
                    parts = [m.left, *m.comparators]
                    if len(m.ops) >= 2:
                        others.setdefault(ast.dump(parts[1]), set()).update({ast.dump(parts[0]), ast.dump(parts[2])})
                    for a_, b_ in ((parts[0], parts[1]), (parts[1], parts[0])):
                        if isinstance(a_, ast.Name):
                            others.setdefault(ast.dump(a_), set()).add(ast.dump(b_))
            two = any(len(v) >= 2 for v in others.values())
            seams.append(("window", q, not two, wnames[0].lineno))
        # feed-instant
        for n in own:
            if isinstance(n, ast.Call) and _name(n.func) in TIME_PARSERS:
                if True:
                    parsed = None
                    p = parents.get(n)
                    if isinstance(p, ast.Assign) and isinstance(p.targets[0], ast.Name):
                        parsed = p.targets[0].id
                    bounded = _calls(fn, set(BOUNDED_HELPERS)) or any(
                        isinstance(m, ast.Attribute) and m.attr == "year" for m in own) or (parsed is not None and any(
                        isinstance(m, ast.Compare) and not all(isinstance(o, (ast.Is, ast.IsNot)) for o in m.ops)
                        and any(isinstance(x, ast.Name) and x.id == parsed for x in ast.walk(m))
                        for m in own))
                    seams.append(("feed-instant", q, not bounded, n.lineno)); break
        # store-leaf
        if q == "_poisoned":
            seams.append(("store-leaf", q, not finite, fn.lineno))
    return [(f, rel, q, flag, ln) for f, q, flag, ln in seams]


CLEAN = '''
import math, json
from datetime import datetime, timedelta
CAP_H = 48.0
PLAUSIBLE = {"t": (-40.0, 60.0)}
def parse_bool(raw):
    try:
        v = float(raw)
    except ValueError:
        return None
    return v != 0.0 if math.isfinite(v) else None
def parse_payload(p):
    d = json.loads(p)
    if isinstance(d, bool) or not isinstance(d, (int, float)):
        return None
    return float(d)
def restore(raw):
    hours = raw.get("boosted_h")
    if isinstance(hours, (int, float)) and not isinstance(hours, bool) and 0.0 <= hours <= CAP_H:
        return timedelta(hours=hours)
    return None
def effective(candidate, key):
    try:
        return float(candidate.get(key))
    except (TypeError, ValueError):
        return None
def plausible(key, v):
    lo, hi = PLAUSIBLE[key]
    return lo <= v <= hi
def _parse_block(rows, now):
    out = []
    for r in rows:
        t = datetime.fromisoformat(r)
        if abs((t - now).days) > 30:
            continue
        out.append(t)
    return out
def _poisoned(value):
    if isinstance(value, float):
        return not math.isfinite(value) or abs(value) >= 1e15
    return False
'''

PERTURB = {
    "num-flag": ("    return v != 0.0 if math.isfinite(v) else None", "    return v != 0.0"),
    "bool-number": ("    if isinstance(d, bool) or not isinstance(d, (int, float)):", "    if not isinstance(d, (int, float)):"),
    "dyn-timedelta": ("0.0 <= hours <= CAP_H", "0.0 <= hours < math.inf"),
    "opt-float": ("    try:\n        return float(candidate.get(key))\n    except (TypeError, ValueError):\n        return None",
                  "    return float(candidate.get(key))"),
    "window": ("    return lo <= v <= hi", "    return lo <= v"),
    "feed-instant": ("        if abs((t - now).days) > 30:\n            continue\n", ""),
    "store-leaf": ("        return not math.isfinite(value) or abs(value) >= 1e15", "        return abs(value) >= 1e15"),
}


PLANT = (
    ("store.py", "return not math.isfinite(value) or abs(value) >= ABSURD", "return abs(value) >= ABSURD"),
    ("inputs.py", "return window is None or window[0] <= value_c <= window[1]", "return window is None or window[0] <= value_c"),
)
JUDGED = {  # finding id -> (family, file::qualname)
    "D1-s2-01": ("store-leaf", PKG + "/store.py::_poisoned"),
    "D1-s2-05": ("opt-float", PKG + "/thermal_model.py::ThermalParameters.from_config"),
    "D1-s2-06": ("dyn-timedelta", PKG + "/boost.py::_restore_settle"),
    "D1-s2-51": ("window", PKG + "/inputs.py::plausible_c"),
    "D1-s3-01": ("num-flag", PKG + "/inputs.py::parse_bool"),
    "D1-s3-02": ("bool-number", PKG + "/coordinator.py::_parse_ecl110_state"),
    "D1-s3-03": ("feed-instant", PKG + "/open_meteo.py::_parse_block"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--perturb", choices=FAMILIES)
    ap.add_argument("--flagged", action="store_true", help="print flagged seams only")
    ap.add_argument("--plant", action="store_true",
                    help="positive control: a copy of the package with the two judged sites the register "
                         "head already guards put back in their pre-fix shape (D1-s2-01, D1-s2-51)")
    a = ap.parse_args()
    if a.null or a.perturb:
        src = CLEAN
        if a.perturb:
            old, new = PERTURB[a.perturb]
            assert old in src, a.perturb
            src = src.replace(old, new)
        d = Path(tempfile.mkdtemp()) / PKG
        d.mkdir(parents=True)
        (d / "fixture.py").write_text(src)
        root = d.parents[1]
    else:
        root = Path(a.root)
    if a.plant:
        import shutil
        tmp = Path(tempfile.mkdtemp())
        shutil.copytree(root / PKG, tmp / PKG)
        for f, old, new in PLANT:
            t = (tmp / PKG / f).read_text()
            assert old in t, (f, old)
            (tmp / PKG / f).write_text(t.replace(old, new, 1))
        root = tmp
    seams = []
    for p in sorted((root / PKG).rglob("*.py")):
        rel = str(p.relative_to(root))
        seams += scan_module(rel, p.read_text())
    seams.sort(key=lambda s: (s[0], s[1], s[2]))
    for fam, rel, q, flag, ln in seams:
        if a.flagged and not flag:
            continue
        print(f"SEAM {fam} {rel}::{q} {'FLAG' if flag else 'ok'} {ln}")
    for fam in FAMILIES:
        fs = [s for s in seams if s[0] == fam]
        print(f"RESULT {fam} seams={len(fs)} flagged={sum(1 for s in fs if s[3])}")
    if not (a.null or a.perturb):
        flagged = {(f, f"{r}::{q}") for f, r, q, fl, _ in seams if fl}
        listed = {(f, f"{r}::{q}") for f, r, q, fl, _ in seams}
        print(f"RESULT judged_sites_listed={sum(1 for v in JUDGED.values() if v in listed)} of {len(JUDGED)}")
        print(f"RESULT judged_sites_flagged={sum(1 for v in JUDGED.values() if v in flagged)} of {len(JUDGED)} "
              f"({','.join(k for k, v in JUDGED.items() if v in flagged)})")
    print(f"RESULT seams_total={len(seams)}")
    print(f"RESULT seams_flagged={sum(1 for s in seams if s[3])}")


if __name__ == "__main__":
    sys.exit(main())
