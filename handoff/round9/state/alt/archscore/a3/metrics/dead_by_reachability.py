"""dead_by_reachability: functions, methods and properties no PRODUCTION root
reaches. Tests are not roots.

Roots (Home Assistant's own entry points, all derived from the tree):
  * every module's import-time code (module-level statements, class bodies,
    decorators, default values): HA imports the package, its platforms,
    config_flow, diagnostics and repairs, and they import the rest;
  * the convention names HA looks up on a module (tests/structure.py's
    HA_CONVENTION_NAMES: async_setup_entry, async_setup, async_unload_entry,
    async_migrate_entry, async_get_config_entry_diagnostics,
    async_create_fix_flow, ...), which covers every platform's setup;
  * ``manifest.json`` ``config_flow: true`` -> every class whose external base
    names ConfigFlow/OptionsFlow is instantiated by HA;
  * framework dispatch: in any LIVE class with a base outside the package
    (an entity, a flow, the DataUpdateCoordinator), every public member and
    every HA_CONVENTION_METHODS / ``async_step_*`` member, plus dunders of
    every live class.

Reachability (a rapid-type-analysis sweep): from a reached body, a bare name
reaches the function/class it resolves to through imports and re-exports; a
module attribute reaches that module's symbol; ``Class.m`` reaches ``m``
through the MRO; ``self.m``/``cls.m`` reaches ``m`` in the method's class and
in every live subclass that overrides it; ``super().m`` the base's ``m``;
``self.A.m`` with ``A``'s class known from ``self.A = K(..)`` reaches
``K.m``; any other ``x.m`` (receiver untyped) reaches every member named
``m`` of every live class, now or later -- conservative, so the count
under-reports rather than calling a live member dead. A class is LIVE when a
reached body names it. Nested defs and lambdas belong to their enclosing
body.

Headline: members (module-level functions + class-body functions, property
accessors included) never reached. Details: per module; the subset whose NAME
is referenced somewhere in the package (the ones tests/structure.py's
name-based dead_methods / dead_top_level_symbols cannot see: called only by
other dead code); the subset whose name appears in tests/ (kept alive only
by the suite).
"""
from __future__ import annotations

import ast
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as C  # noqa: E402


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    eng = C.engine(pkg, seed_params=False)
    by_cls_name: dict[tuple, list[str]] = defaultdict(list)
    for q, fn in pkg.funcs.items():
        if fn.cls:
            by_cls_name[(fn.cls, fn.name)].append(q)

    top_funcs: dict[str, list[str]] = defaultdict(list)
    for q, fn in pkg.funcs.items():
        if fn.cls is None:
            top_funcs[fn.name].append(q)
    top_classes: dict[str, list[tuple]] = defaultdict(list)
    for key in pkg.classes:
        top_classes[key[1]].append(key)
    # Protocol bodies declare a shape; nothing ever calls their members
    protocol = {key for key, c in pkg.classes.items() if any(b.split(".")[-1] == "Protocol" for b in c.ext_bases)}
    census = [q for q, fn in pkg.funcs.items() if fn.cls not in protocol]

    reached: set[str] = set()
    alive: set[tuple] = set()
    pending_names: set[str] = set()
    pending_self: dict[tuple, set[str]] = defaultdict(set)  # class -> names dispatched on self
    work: list = []  # ("fn", qual) | ("body", mod, cls, node-list)

    def reach_fn(q):
        if q not in reached:
            reached.add(q)
            work.append(("fn", q))

    def reach_member(key, name, dispatch=True):
        """name looked up on an instance of ``key``: MRO hit, plus overrides."""
        found = False
        for k in pkg.mro(key):
            if (k, name) in by_cls_name:
                for q in by_cls_name[(k, name)]:
                    reach_fn(q)
                found = True
                break
        if dispatch:
            pending_self[key].add(name)
            for s in pkg.subclasses(key):
                if s in alive:
                    for q in by_cls_name.get((s, name), []):
                        reach_fn(q)
        return found

    def make_alive(key):
        if key in alive or key not in pkg.classes:
            return
        alive.add(key)
        c = pkg.classes[key]
        work.append(("body", key[0], key, [s for s in c.node.body
                                           if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))]
                     + c.node.bases + c.node.keywords + c.node.decorator_list))
        external = any(pkg.classes[k].ext_bases for k in pkg.mro(key))
        for s in c.node.body:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                n = s.name
                if (n.startswith("__") and n.endswith("__")) or n in pending_names \
                        or (external and (not n.startswith("_") or C.is_ha_method(n))):
                    for q in by_cls_name[(key, n)]:
                        reach_fn(q)
        for k in pkg.mro(key)[1:]:
            for n in pending_self.get(k, ()):
                for q in by_cls_name.get((key, n), []):
                    reach_fn(q)
        for b in c.base_keys:
            make_alive(b)

    def hit(mod, r):
        if not r:
            return
        if r[0] == "func":
            reach_fn(r[1])
        elif r[0] == "class":
            make_alive(r[1])

    def scan(mod, cls, nodes, self_name=None):
        typed = pkg.attr_types(cls) if cls else {}
        for top in nodes:
            for n in C.walk(top):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    hit(mod, pkg.resolve_name(mod, n.id))
                elif isinstance(n, ast.Attribute):
                    v = n.value
                    st = pkg.resolve_expr_static(mod, v)
                    if st and st[0] == "mod":
                        hit(mod, pkg.resolve_name(st[1], n.attr))
                        continue
                    if st and st[0] == "class":
                        reach_member(st[1], n.attr)
                        continue
                    if cls and isinstance(v, ast.Name) and v.id in ("self", "cls", self_name):
                        if reach_member(cls, n.attr):
                            continue
                    if cls and isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "super":
                        for b in pkg.classes[cls].base_keys:
                            if reach_member(b, n.attr, dispatch=False):
                                break
                        continue
                    if cls and isinstance(v, ast.Attribute) and isinstance(v.value, ast.Name) \
                            and v.value.id == "self" and v.attr in typed:
                        make_alive(typed[v.attr])
                        if reach_member(typed[v.attr], n.attr):
                            continue
                    name_based(n.attr)
                elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("getattr", "hasattr") \
                        and len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
                    name_based(n.args[1].value)

    def name_based(name):
        if name in pending_names:
            return
        pending_names.add(name)
        for k in list(alive):
            for q in by_cls_name.get((k, name), []):
                reach_fn(q)
        # an untyped receiver may be a module (``mod = await _async_lazy(..)``)
        for q in top_funcs.get(name, []):
            reach_fn(q)
        for key in top_classes.get(name, []):
            make_alive(key)

    # roots
    for m in pkg.mods.values():
        work.append(("body", m.name, None, [s for s in m.tree.body
                                            if not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]))
        for s in m.tree.body:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                work.append(("body", m.name, None, s.decorator_list + s.args.defaults + [d for d in s.args.kw_defaults if d is not None]))
                if s.name in C.HA_CONVENTION_NAMES or (s.name.startswith("__") and s.name.endswith("__")):
                    reach_fn(f"{m.name}:{s.name}")
            elif isinstance(s, ast.ClassDef):
                # the class statement runs at import: bases, decorators, body
                work.append(("body", m.name, None, s.bases + s.keywords + s.decorator_list))
    manifest = pkg.dir / "manifest.json"
    flows = '"config_flow": true' in manifest.read_text() if manifest.exists() else False
    for key, c in pkg.classes.items():
        if flows and any("ConfigFlow" in b or "OptionsFlow" in b for b in c.ext_bases):
            make_alive(key)

    while work:
        item = work.pop()
        if item[0] == "fn":
            fn = pkg.funcs[item[1]]
            node = fn.node
            scan(fn.mod, fn.cls, list(node.body) + node.decorator_list + node.args.defaults
                 + [d for d in node.args.kw_defaults if d is not None],
                 self_name=fn.params[0] if fn.params and fn.kind != "staticmethod" else None)
            if fn.cls:
                make_alive(fn.cls)  # a reached method implies an instance or class access
        else:
            _, mod, cls, nodes = item
            scan(mod, cls, nodes)

    dead = sorted(q for q in census if q not in reached)
    all_names = set()
    for m in pkg.mods.values():
        for n in C.walk(m.tree):
            if isinstance(n, ast.Attribute):
                all_names.add(n.attr)
            elif isinstance(n, ast.Name):
                all_names.add(n.id)
    tests_dir = pkg.root / "tests"
    test_text = ""
    if tests_dir.is_dir():
        test_text = "\n".join(p.read_text(errors="replace") for p in sorted(tests_dir.glob("*.py")))
    dead_names = {pkg.funcs[q].name for q in dead}
    test_words = {n for n in dead_names if re.search(r"\b" + re.escape(n) + r"\b", test_text)}
    per_mod: dict[str, int] = defaultdict(int)
    hidden, test_only = [], []
    for q in dead:
        fn = pkg.funcs[q]
        per_mod[fn.mod] += 1
        # the name is still spoken somewhere else in the package
        own = {id(x) for x in C.walk(fn.node)}
        if fn.name in all_names:
            hidden.append(q)
        if fn.name in test_words:
            test_only.append(q)
        del own
    return {
        "metric": "dead_by_reachability",
        "value": len(dead),
        "details": {
            "members": len(census),
            "protocol_members_excluded": len(pkg.funcs) - len(census),
            "reached": len(reached),
            "live_classes": len(alive),
            "classes": len(pkg.classes),
            "dead_whose_name_is_referenced_in_package": len(hidden),
            "dead_whose_name_appears_in_tests": len(test_only),
            "per_module": dict(sorted(per_mod.items(), key=lambda kv: (-kv[1], kv[0]))),
            "dead": dead,
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(measure(Path(sys.argv[1] if len(sys.argv) > 1 else ".")), indent=1))
