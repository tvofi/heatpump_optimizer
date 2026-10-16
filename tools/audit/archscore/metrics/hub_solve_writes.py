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
a package function is reached from wherever that function is, so it is not a root of its own.

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
        for n in C.walk(fn.node):
            if not isinstance(n, ast.Call):
                continue
            callee = pkg.resolve_expr_static(fn.mod, n.func)
            if callee and callee[0] in ("func", "class"):
                continue
            for a in [*n.args, *(k.value for k in n.keywords)]:
                if isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) and a.value.id == fn.params[0] \
                        and a.attr in methods and fn.kind == "method":
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

