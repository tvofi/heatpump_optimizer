"""hub_solve_writes: in-place writes to the coordinator's three live hubs
(``_opt_config``, ``_thermal_params``, ``_current_state``) reachable from the
scheduled cycle or a solve.

Definition. Roots: ``HeatPumpOptimizerCoordinator._async_update_data`` (the
scheduled cycle, which runs the solve), ``async_run_optimization`` (the solve,
also reached from a service call) and ``async_simulate`` (the what-if solve),
``self`` bound to the coordinator. The cycle is a root so that a write moved
out of the solve into a step before it is the same site, not a removed one
(R9-EG-A4: the #1887 round-1 review's probe, red-team attempt 14); the name
stays, because the frozen weights key on it. Everything reachable from them through calls and
callback references, in any module, with roles propagated through arguments
(see _common). A site is an assignment / augmented assignment / ``del`` /
``setattr`` / item store / container mutation whose base evaluates to a hub
or to anything under one -- however spelled: ``self.X``, ``ctx.X`` with
``ctx = getattr(self, "_ctx", self)``, ``self._ctx.X``, a local alias, a
parameter a hub was passed into (``away.apply_setback(.., ctx._opt_config,
..)``), or an owned object's field the constructor bound to the hub
(``self._thermal_model.params``, ``self._legionella._params`` -- derived, see
Engine._derive_aliases). Rebinding the hub itself (``ctx._opt_config =
replace(..)``) is NOT a site: that is the copy-on-write the CoordinatorContext
facade exists for.

C16 (round 10, ARCH2-s2 P4's instrument half): a coordinator method the package hands to code
outside it -- a Home Assistant event, MQTT or timer subscription -- is called back at runtime with
the live hubs, so it is a root too (``event_roots``); before, an in-place hub write in the ECL110
state message or the peak-guard meter event was counted by no score metric. A callback handed to
a package function is reached from wherever that function is, so it is not a root of its own --
unless that function passes it ON without calling it: hands it to code outside the package, at any
depth of package calls, or returns it (``def wrap(cb): return cb``, or a closure over it) into a call
that hands the result on -- ``subscribe(wrap(self._cb))`` (``_passes_on``, ``_consumed``, counter C16b;
#2311 round-1 review F1, attempt 20b). A returned reference whose result is discarded, or bound to a
name and handed on later, is not a root: the first because nothing subscribes it (the null control in
``tests/arch_score.py``), the second because the census does not follow a local.

Precision, stated: a method reference handed to ANY non-package call is a root, including one that
never calls it (``_LOGGER.debug("%r", self.method)``): the census over-counts such a method's writes
(#2311 review F2) rather than miss a subscription it cannot tell from it.

Headline: distinct write sites (file:line, hub, field). Details: distinct
fields, per-root split, sites inside a ``finally``-reached restore helper.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path

from . import common as C

ROOTS = ("_async_update_data", "async_run_optimization", "async_simulate")
#: Counter C16: the event callbacks are roots. ``vector.py`` switches it off.
EVENT_ROOTS = True
#: Counter C16b: a callback a package function passes on uncalled is a root. ``vector.py`` switches it off.
PASS_ON = True


def _carriers(fn_node: ast.AST, param: str) -> set[str]:
    """``param`` and the nested functions of ``fn_node`` that read it: what carries the argument out."""
    out = {param}
    for n in C.walk(fn_node):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n is not fn_node \
                and any(isinstance(y, ast.Name) and y.id == param for y in C.walk(n)):
            out.add(n.name)
    return out


def _passes_on(pkg: C.Pkg, qual: str, param: str, _seen: frozenset = frozenset()) -> str | None:
    """How package function ``qual`` lets its parameter ``param`` out uncalled: ``"out"`` when it hands
    it to a call that does not resolve to a package function or class (directly, or through a package
    callee that does), ``"returned"`` when a ``return`` reads it (or a nested function or lambda over it),
    else None. A returned reference is a root only where its caller hands the result on (``_consumed``)."""
    fn = pkg.funcs.get(qual)
    if fn is None or (qual, param) in _seen:
        return None
    seen = _seen | {(qual, param)}
    carry = _carriers(fn.node, param)

    def reads(e: ast.AST | None) -> bool:
        """``e`` reads a carrier other than as the function it calls (``cb(x)`` calls it, not passes it)."""
        if e is None:
            return False
        called = {id(y.func) for y in C.walk(e) if isinstance(y, ast.Call)}
        return any(isinstance(y, ast.Name) and y.id in carry and id(y) not in called for y in C.walk(e))

    returned = False
    for n in C.walk(fn.node):
        if isinstance(n, ast.Return) and reads(n.value):
            returned = True
        if not isinstance(n, ast.Call):
            continue
        handed = [(i, a) for i, a in enumerate(n.args) if reads(a)] + \
                 [(k.arg, k.value) for k in n.keywords if reads(k.value)]
        if not handed:
            continue
        callee = pkg.resolve_expr_static(fn.mod, n.func)
        if not callee or callee[0] not in ("func", "class"):
            return "out"
        target = pkg.funcs.get(callee[1]) if callee[0] == "func" else None
        for pos, _a in handed:
            if target is None:
                continue
            name = pos if isinstance(pos, str) else (target.params[pos] if pos < len(target.params) else None)
            if name and _passes_on(pkg, target.qual, name, seen) == "out":
                return "out"
    return "returned" if returned else None


def _param_at(target, pos) -> str | None:
    return pos if isinstance(pos, str) else (target.params[pos] if pos < len(target.params) else None)


def _consumed(pkg: C.Pkg, mod: str, call: ast.Call, parent: dict[int, ast.AST], _depth: int = 0) -> bool:
    """Whether the value ``call`` returns is handed on: an argument of a call outside the package, or of a
    package function that passes that argument on in turn (C16b's returned arm)."""
    up = parent.get(id(call))
    if not isinstance(up, ast.Call) or _depth > 8:
        return False
    pos = next((i for i, a in enumerate(up.args) if a is call), None)
    if pos is None:
        pos = next((k.arg for k in up.keywords if k.value is call), None)
    if pos is None:
        return False
    callee = pkg.resolve_expr_static(mod, up.func)
    if not callee or callee[0] not in ("func", "class"):
        return True
    target = pkg.funcs.get(callee[1]) if callee[0] == "func" else None
    name = _param_at(target, pos) if target else None
    how = _passes_on(pkg, target.qual, name) if name else None
    return how == "out" or (how == "returned" and _consumed(pkg, mod, up, parent, _depth + 1))


def event_roots(pkg: C.Pkg) -> list[str]:
    """Coordinator methods referenced, not called, as an argument of a call that does not resolve to a
    package function: what the package hands to Home Assistant to call back."""
    if not EVENT_ROOTS or pkg.coord_key not in pkg.classes:
        return []
    methods = pkg.classes[pkg.coord_key].methods
    out: set[str] = set()
    for fn in pkg.funcs.values():
        if fn.cls != pkg.coord_key:
            continue
        parent = {id(c): n for n in C.walk(fn.node) for c in ast.iter_child_nodes(n)}
        for n in C.walk(fn.node):
            if not isinstance(n, ast.Call):
                continue
            callee = pkg.resolve_expr_static(fn.mod, n.func)
            target = pkg.funcs.get(callee[1]) if callee and callee[0] == "func" else None
            if callee and callee[0] in ("func", "class") and (target is None or not PASS_ON):
                continue
            for pos, a in [*enumerate(n.args), *((k.arg, k.value) for k in n.keywords)]:
                if not (isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) and a.value.id == fn.params[0]
                        and a.attr in methods and fn.kind == "method"):
                    continue
                if target is None:
                    out.add(methods[a.attr])
                    continue
                # a package function: a root only if it passes the reference on uncalled (C16b): hands it
                # out itself, or returns it into a call that does
                name = _param_at(target, pos)
                how = _passes_on(pkg, target.qual, name) if name else None
                if how == "out" or (how == "returned" and _consumed(pkg, fn.mod, n, parent)):
                    out.add(methods[a.attr])
    return sorted(out)


def roots(pkg: C.Pkg) -> list[str]:
    """Every root qual: the cycle and the solves, then the event callbacks."""
    fixed = [f"{C.COORD_MODULE}:{C.COORD_CLASS}.{r}" for r in ROOTS]
    return [q for q in dict.fromkeys(fixed + event_roots(pkg)) if q in pkg.funcs]


def _sites(eng: C.Engine, root_qual: str) -> set[tuple]:
    pkg = eng.pkg
    penv, reached = eng.propagate({root_qual: {}})
    out = set()
    for q in reached:
        fn = pkg.funcs[q]
        for s in eng.write_sites(fn, penv[q]):
            if s["kind"] == "rebind" or s["path"][0] not in C.HUBS:
                continue
            fld = s["path"][1] if len(s["path"]) > 1 else s["field"]
            out.add((pkg.mods[fn.mod].rel.rsplit("/", 1)[-1], s["line"], s["path"][0], fld, fn.qual, s["kind"]))
    return out


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    eng = C.engine(pkg)
    per_root = {}
    allsites: set[tuple] = set()
    for q in roots(pkg):
        s = _sites(eng, q)
        per_root[q.rsplit(".", 1)[-1]] = len({x[:4] for x in s})
        allsites |= s
    sites = sorted({x[:4] for x in allsites})
    fields = sorted({(h, f) for _, _, h, f in sites})
    by_fn: dict[str, int] = {}
    for x in allsites:
        by_fn[x[4]] = by_fn.get(x[4], 0) + 1
    return {
        "metric": "hub_solve_writes",
        "value": len(sites),
        "details": {
            "distinct_fields": len(fields),
            "per_root_sites": per_root,
            "per_hub_sites": {h: sum(1 for s in sites if s[2] == h) for h in C.HUBS},
            "sites_by_function": dict(sorted(by_fn.items(), key=lambda kv: (-kv[1], kv[0]))),
            "sites": [f"{f}:{ln} {h}.{fl}" for f, ln, h, fl in sites],
            "derived_aliases": {f"{a}.{b}": ".".join(p) for (a, b), p in sorted(eng.alias.items())
                                if p and p[0] in C.HUBS},
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }

