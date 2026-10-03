"""hub_solve_writes: in-place writes to the coordinator's three live hubs
(``_opt_config``, ``_thermal_params``, ``_current_state``) reachable from the
solve path.

Definition. Roots: ``HeatPumpOptimizerCoordinator.async_run_optimization``
(the scheduled solve) and ``async_simulate`` (the what-if solve), ``self``
bound to the coordinator. Everything reachable from them through calls and
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

Headline: distinct write sites (file:line, hub, field). Details: distinct
fields, per-root split, sites inside a ``finally``-reached restore helper.
"""
from __future__ import annotations

import time
from pathlib import Path

from . import common as C

ROOTS = ("async_run_optimization", "async_simulate")


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
    for r in ROOTS:
        q = f"{C.COORD_MODULE}:{C.COORD_CLASS}.{r}"
        if q not in pkg.funcs:
            continue
        s = _sites(eng, q)
        per_root[r] = len({x[:4] for x in s})
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

