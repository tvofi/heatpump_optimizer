"""shared_inplace_writes: in-place writes into long-lived objects the
coordinator holds, made where another task can observe them half-done.

Definition. A LONG-LIVED object is anything reached from the coordinator by
at least one attribute hop -- ``coord.A`` (a dict, list, dataclass, owned
collaborator) or deeper (``coord.A.B``, ``coord.A[k]``) -- excluding the
three hubs, which hub_solve_writes prices. An IN-PLACE write mutates that
object instead of rebinding the coordinator's slot: attribute store,
augmented assignment, ``del``, ``setattr``, item store, or a container
mutator (``update``/``append``/``pop``/``setdefault``/...), through any
spelling or alias the role engine resolves, including a parameter the object
was passed into (``overlay(coord._current_action, ...)``).

It counts when it runs where the object is SHARED:
  (a) in an ``async def`` method of the coordinator (the body may suspend at
      an ``await`` with the object half-written, and ``coordinator.data``
      hands the same objects to every entity), or
  (b) in any function of a collaborator module (not coordinator.py) --
      a mutation of coordinator-held state from outside its owner;
and not in the construction phase: ``__init__``, ``_init_*`` and every
method ``__init__`` references directly (the spawned loaders, the boost
session restore), which run before the first refresh publishes anything. A
collaborator mutating ITS OWN fields through its own ``self`` is ordinary
encapsulation and does not count.

Plus the S2 shape, BORROW/RESTORE: in an ``async`` function, a coordinator
slot ``A`` saved into a local (``snap = (self.A, self.B)``) and written back
from that local (``self.A, self.B = snap``) with an ``await`` in the body --
one site per (function, slot). It is a rebinding, not an in-place write, but
it is the same hazard: the slot is borrowed state for the width of an await.

Headline: in-place sites + borrow/restore sites.
"""
from __future__ import annotations

import ast
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402


def construction_phase(eng: C.Engine) -> set[str]:
    pkg = eng.pkg
    out = set()
    ck = pkg.coord_key
    if ck not in pkg.classes:
        return out
    for name, q in pkg.classes[ck].methods.items():
        if name == "__init__" or name.startswith("_init_"):
            out.add(q)
    init = pkg.funcs.get(pkg.classes[ck].methods.get("__init__"))
    if init is not None:
        env = eng._local_env(init.node, eng.seed_env(init), init.cls, init.mod)
        for n in ast.walk(init.node):
            if isinstance(n, ast.Call):
                out.update(q for q, _s, _o in eng.callees(init, n, env))
            if isinstance(n, (ast.Attribute, ast.Name)):
                out.update(q for q, _s in eng.references(init, n, env))
    return out


def borrow_restore(eng: C.Engine, fn: C.Fn, env: dict) -> list[tuple[int, str]]:
    if not fn.is_async or not any(isinstance(n, ast.Await) for n in ast.walk(fn.node)):
        return []
    full = eng._local_env(fn.node, env, fn.cls, fn.mod)

    def coord_attrs(e) -> set[str]:
        out = set()
        elts = e.elts if isinstance(e, (ast.Tuple, ast.List)) else [e]
        for x in elts:
            if isinstance(x, ast.Attribute) and C.COORD in eng.ev(x.value, full, fn.mod, fn.cls):
                out.add(x.attr)
        return out

    saved: dict[str, set[str]] = {}
    for n in ast.walk(fn.node):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            a = coord_attrs(n.value)
            if a:
                saved.setdefault(n.targets[0].id, set()).update(a)
    out = []
    for n in ast.walk(fn.node):
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            v = n.value
            src = v.value if isinstance(v, ast.Subscript) else v
            if not (isinstance(src, ast.Name) and src.id in saved):
                continue
            for a in coord_attrs(n.targets[0]) & saved[src.id]:
                out.append((n.lineno, a))
    return out


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    eng = C.engine(pkg)
    penv, reached = eng.propagate(None)
    ctor = construction_phase(eng)
    sites = set()
    borrow = set()
    for q in sorted(reached):
        fn = pkg.funcs[q]
        if q in ctor:
            continue
        in_coord_async = fn.cls == pkg.coord_key and fn.is_async
        collab = fn.mod != C.COORD_MODULE
        fname = pkg.mods[fn.mod].rel.rsplit("/", 1)[-1]
        if in_coord_async or collab:
            for s in eng.write_sites(fn, penv[q]):
                if s["kind"] == "rebind" or s["own"] or s["path"][0] in C.HUBS:
                    continue
                where = "coord-async" if in_coord_async else "collaborator"
                obj = ".".join(s["path"])
                sites.add((fname, s["line"], obj, s["field"], s["kind"], where, fn.qual))
        for line, a in borrow_restore(eng, fn, penv[q]):
            borrow.add((fname, line, a, fn.qual))
    uniq = sorted({x[:4] for x in sites})
    borrow_keys = sorted({(x[3], x[2]) for x in borrow})
    per_obj: dict[str, int] = {}
    for x in uniq:
        root_attr = x[2].split(".")[0]
        per_obj[root_attr] = per_obj.get(root_attr, 0) + 1
    return {
        "metric": "shared_inplace_writes",
        "value": len(uniq) + len(borrow_keys),
        "details": {
            "inplace_sites": len(uniq),
            "borrow_restore_sites": len(borrow_keys),
            "coord_async_sites": len({x[:4] for x in sites if x[5] == "coord-async"}),
            "collaborator_sites": len({x[:4] for x in sites if x[5] == "collaborator"}),
            "per_object": dict(sorted(per_obj.items(), key=lambda kv: (-kv[1], kv[0]))),
            "sites": [f"{f}:{ln} {o} .{fl}" for f, ln, o, fl in uniq],
            "borrow_restore": [f"{q} restores {a}" for q, a in borrow_keys],
            "construction_phase_excluded": len(ctor),
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(measure(Path(sys.argv[1] if len(sys.argv) > 1 else ".")), indent=1))
