"""private_reach: reads and writes of the coordinator's private members from
outside coordinator.py, writes weighted x3.

Definition. In every function of every module except coordinator.py, an
access ``<c>._x`` (single leading underscore, not a dunder) where ``<c>``
evaluates to the coordinator under the role engine: a ``coord`` /
``coordinator`` parameter or one annotated with a coordinator type or
``*Coord`` protocol, ``entry.runtime_data``, ``self.coordinator`` on a
CoordinatorEntity, any ``self.X`` a class stores a coordinator parameter
into, any local alias of those, and any parameter a coordinator was passed
into from ANY module (``wood_fuel_from_coordinator(self, ..)``). Also
``getattr/hasattr/setattr/delattr(<c>, "_x", ..)`` with a literal name.
The context hop is transparent: ``getattr(coord, "_ctx", coord)._config``
and ``coord._ctx._config`` reach ``_config``; ``_ctx`` itself is not counted.

WRITE = a store / del / setattr / delattr on ``<c>._x`` (rebinding the
coordinator's slot) OR an in-place mutation whose base is ``<c>._x``
(``coord._x[k] = v``, ``coord._x.f = v``, ``coord._x.append(..)``); every
other access is a READ. Headline = reads + 3 * writes, over distinct
(file, line, member, kind) sites.

Why x3: a foreign read couples a module to a name; a foreign write couples
it to the coordinator's invariants (who else writes, when, under which
await), and is the shape behind #1752 (boost overlay) and the __init__.py
reload handover.
"""
from __future__ import annotations

import ast
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402

WRITE_WEIGHT = 3


def _private(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__") and name != C.CTX_ATTR


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    eng = C.engine(pkg)
    penv, reached = eng.propagate(None)
    sites: set[tuple] = set()
    for q in sorted(reached):
        fn = pkg.funcs[q]
        if fn.mod == C.COORD_MODULE:
            continue
        fname = pkg.mods[fn.mod].rel.rsplit("/", 1)[-1]
        env = eng._local_env(fn.node, penv[q], fn.cls, fn.mod)

        def is_coord(e):
            return C.COORD in eng.ev(e, env, fn.mod, fn.cls)

        mutated_bases: set[int] = set()
        for n in C.walk(fn.node):
            tgts = []
            if isinstance(n, (ast.Assign, ast.Delete)):
                tgts = n.targets
            elif isinstance(n, (ast.AugAssign, ast.AnnAssign)):
                tgts = [n.target]
            for t in tgts:
                for x in (t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]):
                    if isinstance(x, (ast.Attribute, ast.Subscript)):
                        mutated_bases.add(id(x.value))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in C.MUTATORS:
                mutated_bases.add(id(n.func.value))
        for n in C.walk(fn.node):
            if isinstance(n, ast.Attribute) and _private(n.attr) and is_coord(n.value):
                if isinstance(n.ctx, (ast.Store, ast.Del)):
                    kind = "write"
                elif id(n) in mutated_bases:
                    kind = "write"
                else:
                    kind = "read"
                sites.add((fname, n.lineno, n.col_offset, n.attr, kind, fn.qual))
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id in ("getattr", "hasattr", "setattr", "delattr") and len(n.args) >= 2 \
                    and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str) \
                    and _private(n.args[1].value) and is_coord(n.args[0]):
                kind = "write" if n.func.id in ("setattr", "delattr") or id(n) in mutated_bases else "read"
                sites.add((fname, n.lineno, n.col_offset, n.args[1].value, kind, fn.qual))
    reads = [s for s in sites if s[4] == "read"]
    writes = [s for s in sites if s[4] == "write"]
    per_file: dict[str, int] = {}
    per_member: dict[str, int] = {}
    for s in sites:
        w = WRITE_WEIGHT if s[4] == "write" else 1
        per_file[s[0]] = per_file.get(s[0], 0) + w
        per_member[s[3]] = per_member.get(s[3], 0) + w
    return {
        "metric": "private_reach",
        "value": len(reads) + WRITE_WEIGHT * len(writes),
        "details": {
            "reads": len(reads),
            "writes": len(writes),
            "files": len(per_file),
            "distinct_members": len(per_member),
            "per_file_weighted": dict(sorted(per_file.items(), key=lambda kv: (-kv[1], kv[0]))),
            "top_members_weighted": dict(sorted(per_member.items(), key=lambda kv: (-kv[1], kv[0]))[:15]),
            "write_sites": sorted(f"{f}:{ln} {m} ({q})" for f, ln, _c, m, _k, q in writes),
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(measure(Path(sys.argv[1] if len(sys.argv) > 1 else ".")), indent=1))
