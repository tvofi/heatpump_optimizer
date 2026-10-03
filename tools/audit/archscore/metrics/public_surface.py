"""public_surface: the package's public API per module, and how much of it no
other module uses.

Census. PUBLIC = no leading underscore.
  * module-level names: top-level ``def`` / ``class`` / assignment targets,
    minus HA_CONVENTION_NAMES (HA reads them off the module) and ConfigFlow /
    OptionsFlow subclasses (HA finds them by manifest);
  * methods (properties included) of package classes whose whole MRO stays
    inside the package and that are not Protocol / TypedDict / NamedTuple
    declarations. A class with an external base (entity, flow, coordinator)
    exposes its public members to the framework, not to the package, so they
    are out of this census (dead_by_reachability prices them instead).

USE by another module:
  * module-level ``N`` of ``m``: another module imports it (``from .m import
    N``, through re-exports), or reads ``m.N`` through a module binding, or
    reads ``x.N`` on an untyped receiver (tests/structure.py's
    bound_references rule 4 -- the conservative arm);
  * method ``N``: another module reads ``.N`` on any receiver or
    ``getattr(x, "N")`` -- name-based, since receivers are untyped.

Headline: public names with NO cross-module use -- surface that is either
used only inside its own module (should be ``_``-private: internal_only) or
not used at all (dead public API: unused). Details: per module totals,
cross-module-used counts, and both lists.
"""
from __future__ import annotations

import ast
import time
from collections import defaultdict
from pathlib import Path

from . import common as C

DECL_BASES = ("Protocol", "TypedDict", "NamedTuple", "Enum", "StrEnum", "IntEnum")


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    # -- census
    tops: list[tuple[str, str]] = []
    for m in pkg.mods.values():
        for name, node in m.tops.items():
            if name.startswith("_") or name in C.HA_CONVENTION_NAMES:
                continue
            if isinstance(node, ast.ClassDef) and any(
                    "ConfigFlow" in b or "OptionsFlow" in b for b in pkg.classes[(m.name, name)].ext_bases):
                continue
            tops.append((m.name, name))
    methods: list[tuple[str, str, str]] = []
    for key, c in pkg.classes.items():
        mro = pkg.mro(key)
        if any(pkg.classes[k].ext_bases for k in mro):
            if not all(all(b.split(".")[-1] in ("object", "Generic") or b.startswith("Generic[")
                           for b in pkg.classes[k].ext_bases) for k in mro):
                continue
        seen = set()
        for s in c.node.body:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)) and not s.name.startswith("_") \
                    and s.name not in seen:
                seen.add(s.name)
                methods.append((key[0], key[1], s.name))
    # -- uses, per module
    used_top: dict[tuple[str, str], set[str]] = defaultdict(set)   # (mod, N) -> using modules
    attr_by_mod: dict[str, set[str]] = defaultdict(set)            # module -> attribute names it reads
    untyped_attr: dict[str, set[str]] = defaultdict(set)
    load_names: dict[str, set[str]] = defaultdict(set)
    for m in pkg.mods.values():
        mod_bind = {k: v[1] for k, v in m.imports.items() if v[0] == "mod"}
        for local, imp in m.imports.items():
            if imp[0] == "sym":
                r = pkg.resolve_name(imp[1], imp[2])
                target = None
                if r and r[0] == "func":
                    fn = pkg.funcs[r[1]]
                    target = (fn.mod, fn.name)
                elif r and r[0] in ("class", "var"):
                    target = r[1]
                if target:
                    used_top[target].add(m.name)
                    # a re-export chain credits every hop
                    src, nm = imp[1], imp[2]
                    for _ in range(4):
                        used_top[(src, nm)].add(m.name)
                        nxt = pkg.mods.get(src).imports.get(nm) if src in pkg.mods else None
                        if not nxt or nxt[0] != "sym":
                            break
                        src, nm = nxt[1], nxt[2]
        own_fn_spans = {n.name: (n.lineno, n.end_lineno) for n in m.tree.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}
        for n in C.walk(m.tree):
            if isinstance(n, ast.Attribute):
                attr_by_mod[m.name].add(n.attr)
                if isinstance(n.value, ast.Name) and n.value.id in mod_bind:
                    used_top[(mod_bind[n.value.id], n.attr)].add(m.name)
                elif not (isinstance(n.value, ast.Name) and n.value.id in ("self", "cls")):
                    untyped_attr[m.name].add(n.attr)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr") \
                    and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
                attr_by_mod[m.name].add(n.args[1].value)
                untyped_attr[m.name].add(n.args[1].value)
            elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                span = own_fn_spans.get(n.id)
                if not (span and span[0] <= n.lineno <= span[1]):
                    load_names[m.name].add(n.id)
    # runtime-assembled names (tests/structure.py DYNAMIC_REFERENCES, generalised):
    # getattr(x, f"PREFIX{..}") in a module plus a string literal S in that
    # module make PREFIX+S used by it.
    for m in pkg.mods.values():
        prefixes = set()
        literals = set()
        for n in C.walk(m.tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "getattr" \
                    and len(n.args) >= 2 and isinstance(n.args[1], ast.JoinedStr) and n.args[1].values \
                    and isinstance(n.args[1].values[0], ast.Constant):
                prefixes.add(n.args[1].values[0].value)
            elif isinstance(n, ast.Constant) and isinstance(n.value, str):
                literals.add(n.value)
        for pfx in prefixes:
            for lit in literals:
                untyped_attr[m.name].add(pfx + lit)
    internal_only, unused, external = [], [], 0
    per_mod: dict[str, dict] = defaultdict(lambda: {"public": 0, "cross_used": 0})
    for mod, name in tops:
        per_mod[mod]["public"] += 1
        users = used_top.get((mod, name), set()) - {mod}
        users |= {m for m, attrs in untyped_attr.items() if m != mod and name in attrs}
        if users:
            external += 1
            per_mod[mod]["cross_used"] += 1
        elif name in load_names[mod] or name in attr_by_mod[mod]:
            internal_only.append(f"{mod}.{name}")
        else:
            unused.append(f"{mod}.{name}")
    for mod, cls, name in methods:
        per_mod[mod]["public"] += 1
        if any(name in attrs for m, attrs in attr_by_mod.items() if m != mod):
            external += 1
            per_mod[mod]["cross_used"] += 1
        elif name in attr_by_mod[mod]:
            internal_only.append(f"{mod}.{cls}.{name}")
        else:
            unused.append(f"{mod}.{cls}.{name}")
    return {
        "metric": "public_surface",
        "value": len(internal_only) + len(unused),
        "details": {
            "public_module_level": len(tops),
            "public_methods": len(methods),
            "cross_module_used": external,
            "internal_only": len(internal_only),
            "unused": len(unused),
            "per_module": {k: v for k, v in sorted(per_mod.items())},
            "internal_only_names": sorted(internal_only),
            "unused_names": sorted(unused),
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }

