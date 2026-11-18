#!/usr/bin/env python3
"""Enumerator for class N-uncleared-issue (round 11, D14 steps 3-4).

Lists every repair issue the package raises and, per issue id, its clear
sites. A seam is an issue id that is
  - persistent (is_persistent=True / persistent=True): it survives a restart,
    so its clear must be reachable from a fresh process (the seam_rule of
    D1-s1-01), or
  - raised with no clear site at all, or
  - cleared only behind an early return that tests module-level state
    (``restart_gated``: empty in a fresh process, as _clear_worker_fallback).
Usage: enum_uncleared_issue.py [PKG_DIR] [--json]
"""
from __future__ import annotations
import ast, json, sys
from pathlib import Path

RAISE = {"async_create_issue", "create_issue", "_create_issue"}
CLEAR = {"async_delete_issue", "clear_issue"}


def _name(f):
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)


def _const_map(trees):
    m = {}
    for t in trees.values():
        for n in t.body:
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str):
                for tg in n.targets:
                    if isinstance(tg, ast.Name):
                        m[tg.id] = n.value.value
    return m


def _iid(node, consts):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return consts.get(node.id, "$" + node.id)
    if isinstance(node, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in node.values)
    return "?" + ast.unparse(node)


def _module_globals(tree):
    g = set()
    for n in tree.body:
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            for tg in (n.targets if isinstance(n, ast.Assign) else [n.target]):
                if isinstance(tg, ast.Name):
                    g.add(tg.id)
    return g


def _fresh_attrs(trees):
    """Attributes an ``__init__`` or ``_init*`` initialiser sets to a literal 0/None/False/empty: in-memory state a restart resets."""
    out = set()
    for t in trees.values():
        for f in ast.walk(t):
            if isinstance(f, ast.FunctionDef) and (f.name == "__init__" or f.name.startswith("_init")):
                for a in ast.walk(f):
                    tg = a.targets[0] if isinstance(a, ast.Assign) else (a.target if isinstance(a, ast.AnnAssign) else None)
                    v = getattr(a, "value", None)
                    if isinstance(tg, ast.Attribute) and (
                        (isinstance(v, ast.Constant) and not v.value)
                        or (isinstance(v, (ast.Dict, ast.List, ast.Set)) and not getattr(v, "keys", getattr(v, "elts", [1])))
                    ):
                        out.add(tg.attr)
    return out


FRESH: set = set()


def _enclosing_ifs(func, call):
    hits = []
    for st in ast.walk(func):
        if isinstance(st, ast.If) and any(n is call for b in st.body for n in ast.walk(b)):
            hits.append(st)
    return hits


def _restart_gated(func, call, globs):
    """The clear sits behind a test of state a fresh process starts empty:
    an `if <module global>: return` before it, or an enclosing `if` on an
    attribute ``__init__`` sets to 0/None/False/empty."""
    if func is None:
        return False
    for st in _enclosing_ifs(func, call):
        if {x.attr for x in ast.walk(st.test) if isinstance(x, ast.Attribute)} & FRESH:
            return True
    for st in ast.walk(func):
        if isinstance(st, ast.If) and st.lineno < call.lineno and any(isinstance(b, ast.Return) for b in st.body):
            names = {x.id for x in ast.walk(st.test) if isinstance(x, ast.Name)}
            # a local bound from a module global counts too (cause = G.pop(..))
            for a in ast.walk(func):
                if isinstance(a, ast.Assign) and a.lineno < st.lineno:
                    src = {x.id for x in ast.walk(a.value) if isinstance(x, ast.Name)}
                    if src & globs:
                        names |= {t.id for t in a.targets if isinstance(t, ast.Name)}
            if names & globs:
                return True
    return False


def enumerate_pkg(pkg: Path):
    trees = {p: ast.parse(p.read_text(), str(p)) for p in sorted(pkg.rglob("*.py"))}
    consts = _const_map(trees)
    FRESH.clear(); FRESH.update(_fresh_attrs(trees))
    issues: dict[str, dict] = {}
    for p, t in trees.items():
        if p.name == "issues.py":
            # the writer itself; its one literal raise is note_price_outage
            pass
        globs = _module_globals(t)
        parents = {}
        for f in ast.walk(t):
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for c in ast.walk(f):
                    parents.setdefault(id(c), f) if False else None
                    if isinstance(c, ast.Call):
                        parents[id(c)] = f  # innermost wins (walk is outer-first)
        for c in ast.walk(t):
            if not isinstance(c, ast.Call):
                continue
            nm = _name(c.func)
            func = parents.get(id(c))
            fname = func.name if func else "<module>"
            if nm in RAISE or nm in CLEAR:
                # (hass, domain, id) or (hass, id)
                args = c.args
                if nm in ("clear_issue",):
                    idn = args[1] if len(args) > 1 else None
                else:
                    idn = args[2] if len(args) > 2 else None
                if idn is None or (p.name == "issues.py" and fname in ("create_issue", "clear_issue")):
                    continue
                iid = _iid(idn, consts)
                e = issues.setdefault(iid, {"raises": [], "clears": [], "persistent": False})
                site = f"{p.name}:{c.lineno}:{fname}"
                if nm in RAISE:
                    e["raises"].append(site)
                    if any(k.arg == "is_persistent" and isinstance(k.value, ast.Constant) and k.value.value for k in c.keywords):
                        e["persistent"] = True
                else:
                    e["clears"].append({"site": site, "restart_gated": _restart_gated(func, c, globs)})
            elif nm == "set_issue" and len(c.args) >= 3:
                iid = _iid(c.args[1], consts)
                e = issues.setdefault(iid, {"raises": [], "clears": [], "persistent": False})
                site = f"{p.name}:{c.lineno}:{fname}"
                rv = c.args[2]
                if not (isinstance(rv, ast.Constant) and not rv.value):
                    e["raises"].append(site)
                if not (isinstance(rv, ast.Constant) and rv.value):
                    e["clears"].append({"site": site, "restart_gated": _restart_gated(func, c, globs)})
                if any(k.arg == "persistent" and not (isinstance(k.value, ast.Constant) and not k.value.value) for k in c.keywords):
                    e["persistent"] = True
            elif nm == "note_price_outage":
                e = issues.setdefault("price_feed_stale", {"raises": [], "clears": [], "persistent": False})
                e["raises"].append(f"{p.name}:{c.lineno}:{fname}")
    seams = []
    for iid, e in sorted(issues.items()):
        if not e["raises"]:
            continue
        reasons = []
        if e["persistent"]:
            reasons.append("persistent")
        if not e["clears"]:
            reasons.append("no_clear")
        elif e["persistent"] and all(x["restart_gated"] for x in e["clears"]):
            reasons.append("restart_gated")
        if reasons:
            seams.append({"issue_id": iid, "reasons": reasons, **e})
    return issues, seams


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    pkg = Path(a[0] if a else "custom_components/heatpump_optimizer")
    issues, seams = enumerate_pkg(pkg)
    if "--json" in sys.argv:
        print(json.dumps({"issues": issues, "seams": seams}, indent=1))
    else:
        for s in seams:
            print(f"SEAM {s['issue_id']} {','.join(s['reasons'])} raises={s['raises']} clears={[c['site']+('!gated' if c['restart_gated'] else '') for c in s['clears']]}")
        print(f"issues_raised={sum(1 for e in issues.values() if e['raises'])} seams={len(seams)} restart_gated={sum('restart_gated' in s['reasons'] for s in seams)}")
