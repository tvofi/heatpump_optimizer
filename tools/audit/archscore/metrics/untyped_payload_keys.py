"""untyped_payload_keys: top-level keys the coordinator publishes in
``coordinator.data`` that no TypedDict contract declares.

Definition. The PRODUCER is ``_async_update_data`` of the
DataUpdateCoordinator subclass: what it returns is ``coordinator.data``. Its
key set is derived statically by following the returned dict:

  * dict literals (constant keys; ``**x`` spreads followed into ``x``),
  * ``d["k"] = ..`` (tuple targets too), ``d.update({..})`` / ``d.update(k=..)``,
    ``d.setdefault("k", ..)``, ``d |= {..}``,
  * ``d.update(f())`` / ``return f()`` / ``return await f()`` into the callee's
    returned dict, through methods (role engine) and module functions,
  * ``g(.., d, ..)`` into ``g``'s writes on that parameter.

Keys whose name is not a literal (``{k: .. for k in ..}``, ``d[var] = ..``)
are counted separately as DYNAMIC emission sites; they cannot be typed by
name and are a blind spot of the key count.

A key is TYPED when some dict on its path to ``coordinator.data`` is
annotated with a package ``TypedDict`` (class or functional form) that
declares it: the tracked variable's annotation, the parameter's annotation,
or the emitting function's return annotation. A TypedDict declared anywhere
else does not count -- a contract has to be attached to the producer.

Headline: produced keys that are not typed. Details: produced total, typed,
dynamic sites, the surfaces' top-level reads (the m2 enumerator's scope,
generalised to the role engine), keys read but never produced (dangling),
keys produced but read by no surface module.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path

from . import common as C

SURFACE_MODULES = ("sensor", "binary_sensor", "climate", "switch", "entity", "button", "datetime", "diagnostics")


def is_any(ann: ast.AST) -> bool:
    """``Any`` or ``object`` (also under Required / NotRequired / ReadOnly) states no type.

    A key declared this way is not a contract: a ``total=False`` TypedDict of every
    key as ``Any`` read 164 -> 0 with no consumer checked (red-team attempt 01).
    """
    text = ast.unparse(ann)
    while text.split("[", 1)[0].split(".")[-1] in ("Required", "NotRequired", "ReadOnly") and text.endswith("]"):
        text = text.split("[", 1)[1][:-1]
    return text.split(".")[-1] in ("Any", "object")


def typed_dicts(pkg: C.Pkg) -> dict[tuple[str, str], set[str]]:
    out: dict[tuple[str, str], set[str]] = {}
    todo = list(pkg.classes.values())
    for _ in range(4):
        for c in todo:
            if c.key in out:
                continue
            if any(b.split(".")[-1] == "TypedDict" for b in c.ext_bases) or any(b in out for b in c.base_keys):
                keys = {s.target.id for s in c.node.body if isinstance(s, ast.AnnAssign)
                        and isinstance(s.target, ast.Name) and not is_any(s.annotation)}
                for b in c.base_keys:
                    keys |= out.get(b, set())
                out[c.key] = keys
    for m in pkg.mods.values():  # functional form: X = TypedDict("X", {"k": T})
        for s in m.tree.body:
            if isinstance(s, ast.Assign) and isinstance(s.value, ast.Call) and isinstance(s.value.func, (ast.Name, ast.Attribute)) \
                    and ast.unparse(s.value.func).split(".")[-1] == "TypedDict" and len(s.value.args) >= 2 \
                    and isinstance(s.value.args[1], ast.Dict) and isinstance(s.targets[0], ast.Name):
                out[(m.name, s.targets[0].id)] = {
                    k.value for k, v in zip(s.value.args[1].keys, s.value.args[1].values)
                    if isinstance(k, ast.Constant) and not is_any(v)}
    return out


class Flow:
    def __init__(self, pkg: C.Pkg, eng: C.Engine):
        self.pkg, self.eng = pkg, eng
        self.td = typed_dicts(pkg)
        self.memo: dict[tuple, tuple[dict, set]] = {}
        self.envs: dict[str, dict] = {}

    def env(self, fn: C.Fn) -> dict:
        if fn.qual not in self.envs:
            self.envs[fn.qual] = self.eng._local_env(fn.node, self.eng.seed_env(fn), fn.cls, fn.mod)
        return self.envs[fn.qual]

    def contract(self, fn: C.Fn, ann: ast.AST | None) -> set[str]:
        if ann is None:
            return set()
        r = self.pkg.resolve_expr_static(fn.mod, ann)
        if r and r[0] == "class" and r[1] in self.td:
            return self.td[r[1]]
        if isinstance(ann, ast.Constant) and isinstance(ann.value, str):
            r = self.pkg.resolve_name(fn.mod, ann.value)
            if r and r[0] == "class" and r[1] in self.td:
                return self.td[r[1]]
        return set()

    def loop_bindings(self, fn: C.Fn) -> dict[str, list]:
        out: dict[str, list] = {}
        for n in C.walk(fn.node):
            if isinstance(n, (ast.For, ast.AsyncFor)) and isinstance(n.target, ast.Name) \
                    and isinstance(n.iter, (ast.Tuple, ast.List)):
                out.setdefault(n.target.id, []).extend(n.iter.elts)
        return out

    @staticmethod
    def body_nodes(fn: C.Fn):
        """Nodes of fn excluding nested function / lambda bodies."""
        out, todo = [], list(ast.iter_child_nodes(fn.node))
        while todo:
            n = todo.pop()
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                continue
            out.append(n)
            todo.extend(ast.iter_child_nodes(n))
        return out

    def merge(self, acc: dict, keys: dict, typed: set[str], origin: str) -> None:
        for k, (t, o) in keys.items():
            t = t or k in typed
            if k not in acc:
                acc[k] = (t, o)
            else:
                acc[k] = (acc[k][0] or t, acc[k][1])

    def expr_keys(self, fn: C.Fn, e: ast.AST, stack: frozenset) -> tuple[dict, set]:
        """(key -> (typed, origin), dynamic sites) for a dict-valued expr."""
        keys: dict = {}
        dyn: set = set()
        where = f"{self.pkg.mods[fn.mod].rel.rsplit('/', 1)[-1]}:{getattr(e, 'lineno', 0)}"
        if isinstance(e, ast.Await):
            return self.expr_keys(fn, e.value, stack)
        if isinstance(e, ast.IfExp):
            a, da = self.expr_keys(fn, e.body, stack)
            b, db = self.expr_keys(fn, e.orelse, stack)
            self.merge(a, b, set(), where)
            return a, da | db
        if isinstance(e, ast.Dict):
            for k, v in zip(e.keys, e.values):
                if k is None:
                    sk, sd = self.expr_keys(fn, v, stack)
                    self.merge(keys, sk, set(), where)
                    dyn |= sd
                elif isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.setdefault(k.value, (False, where))
                else:
                    dyn.add(where)
            return keys, dyn
        if isinstance(e, ast.DictComp):
            dyn.add(where)
            return keys, dyn
        if isinstance(e, ast.Name):
            return self.var_keys(fn, e.id, stack)
        if isinstance(e, ast.Call):
            f = e.func
            if isinstance(f, ast.Name) and f.id == "dict":
                for a in e.args:
                    sk, sd = self.expr_keys(fn, a, stack)
                    self.merge(keys, sk, set(), where)
                    dyn |= sd
                for kw in e.keywords:
                    if kw.arg:
                        keys.setdefault(kw.arg, (False, where))
                    else:
                        sk, sd = self.expr_keys(fn, kw.value, stack)
                        self.merge(keys, sk, set(), where)
                        dyn |= sd
                return keys, dyn
            quals = [q for q, _s, _o in self.eng.callees(fn, e, self.env(fn))]
            if isinstance(f, ast.Name):
                # ``for view in (self._a_view, self._b_view): data.update(view())``
                for elt in self.loop_bindings(fn).get(f.id, []):
                    quals += [q for q, _s in self.eng.references(fn, elt, self.env(fn))]
            for q in quals:
                sk, sd = self.returned_keys(q, stack)
                self.merge(keys, sk, set(), where)
                dyn |= sd
            return keys, dyn
        return keys, dyn

    def returned_keys(self, qual: str, stack: frozenset = frozenset()) -> tuple[dict, set]:
        key = ("ret", qual)
        if key in self.memo:
            return self.memo[key]
        if key in stack or len(stack) > 12:
            return {}, set()
        stack = stack | {key}
        fn = self.pkg.funcs[qual]
        typed = self.contract(fn, fn.node.returns)
        keys: dict = {}
        dyn: set = set()
        for n in self.body_nodes(fn):
            if isinstance(n, ast.Return) and n.value is not None:
                sk, sd = self.expr_keys(fn, n.value, stack)
                self.merge(keys, sk, typed, "")
                dyn |= sd
        keys = {k: (t or k in typed, o) for k, (t, o) in keys.items()}
        self.memo[key] = (keys, dyn)
        return keys, dyn

    def var_keys(self, fn: C.Fn, var: str, stack: frozenset) -> tuple[dict, set]:
        key = ("var", fn.qual, var)
        if key in self.memo:
            return self.memo[key]
        if key in stack or len(stack) > 12:
            return {}, set()
        stack = stack | {key}
        keys: dict = {}
        dyn: set = set()
        typed: set[str] = set()
        a = fn.node.args
        for p in a.posonlyargs + a.args + a.kwonlyargs:
            if p.arg == var:
                typed |= self.contract(fn, p.annotation)
        fname = self.pkg.mods[fn.mod].rel.rsplit("/", 1)[-1]

        def is_var(x):
            return isinstance(x, ast.Name) and x.id == var

        def store(t, line):
            if isinstance(t, (ast.Tuple, ast.List)):
                for x in t.elts:
                    store(x, line)
            elif isinstance(t, ast.Subscript) and is_var(t.value):
                s = t.slice
                if isinstance(s, ast.Constant) and isinstance(s.value, str):
                    keys.setdefault(s.value, (False, f"{fname}:{line}"))
                else:
                    dyn.add(f"{fname}:{line}")

        for n in self.body_nodes(fn):
            if isinstance(n, ast.AnnAssign) and is_var(n.target):
                typed |= self.contract(fn, n.annotation)
                if n.value is not None:
                    sk, sd = self.expr_keys(fn, n.value, stack)
                    self.merge(keys, sk, set(), "")
                    dyn |= sd
            elif isinstance(n, ast.Assign):
                for t in n.targets:
                    if is_var(t):
                        sk, sd = self.expr_keys(fn, n.value, stack)
                        self.merge(keys, sk, set(), "")
                        dyn |= sd
                    else:
                        store(t, n.lineno)
            elif isinstance(n, ast.AugAssign) and is_var(n.target) and isinstance(n.op, ast.BitOr):
                sk, sd = self.expr_keys(fn, n.value, stack)
                self.merge(keys, sk, set(), "")
                dyn |= sd
            elif isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Attribute) and is_var(f.value) and f.attr in ("update", "setdefault"):
                    if f.attr == "setdefault":
                        if n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                            keys.setdefault(n.args[0].value, (False, f"{fname}:{n.lineno}"))
                        else:
                            dyn.add(f"{fname}:{n.lineno}")
                        continue
                    for arg in n.args:
                        sk, sd = self.expr_keys(fn, arg, stack)
                        self.merge(keys, sk, set(), "")
                        dyn |= sd
                    for kw in n.keywords:
                        if kw.arg:
                            keys.setdefault(kw.arg, (False, f"{fname}:{n.lineno}"))
                    continue
                # the variable passed into a package function that writes it
                argpos = [i for i, x in enumerate(n.args) if is_var(x)]
                kwpos = [kw.arg for kw in n.keywords if kw.arg and is_var(kw.value)]
                if not argpos and not kwpos:
                    continue
                for q, _s, off in self.eng.callees(fn, n, self.env(fn)):
                    callee = self.pkg.funcs[q]
                    for i in argpos:
                        if i + off < len(callee.params):
                            sk, sd = self.var_keys(callee, callee.params[i + off], stack)
                            self.merge(keys, sk, set(), "")
                            dyn |= sd
                    for k in kwpos:
                        if k in callee.params:
                            sk, sd = self.var_keys(callee, k, stack)
                            self.merge(keys, sk, set(), "")
                            dyn |= sd
        keys = {k: (t or k in typed, o) for k, (t, o) in keys.items()}
        self.memo[key] = (keys, dyn)
        return keys, dyn


def surface_reads(pkg: C.Pkg, eng: C.Engine) -> dict[str, list[str]]:
    """Top-level ``coordinator.data`` reads in the surface modules."""
    reads: dict[str, list[str]] = {}
    for q, fn in pkg.funcs.items():
        if fn.mod not in SURFACE_MODULES:
            continue
        env = eng._local_env(fn.node, eng.seed_env(fn), fn.cls, fn.mod)

        def is_data(e):
            if isinstance(e, ast.BoolOp):
                return any(is_data(v) for v in e.values)
            if isinstance(e, ast.Attribute) and e.attr == "data":
                return C.COORD in eng.ev(e.value, env, fn.mod, fn.cls)
            if isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute) and e.func.attr == "_data" \
                    and isinstance(e.func.value, ast.Name) and e.func.value.id == "self":
                return True
            return False

        bound = set()
        for n in C.walk(fn.node):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and is_data(n.value):
                bound.add(n.targets[0].id)

        def top(e):
            return is_data(e) or (isinstance(e, ast.Name) and e.id in bound)

        for n in C.walk(fn.node):
            k = None
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args \
                    and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str) and top(n.func.value):
                k = n.args[0].value
            elif isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str) \
                    and top(n.value):
                k = n.slice.value
            if k:
                reads.setdefault(k, []).append(f"{fn.mod}.py:{n.lineno}")
    return reads


def measure(root: Path) -> dict:
    t0 = time.perf_counter()
    pkg = C.load(str(root))
    eng = C.engine(pkg)
    flow = Flow(pkg, eng)
    producer = f"{C.COORD_MODULE}:{C.COORD_CLASS}._async_update_data"
    keys, dyn = flow.returned_keys(producer) if producer in pkg.funcs else ({}, set())
    untyped = sorted(k for k, (t, _o) in keys.items() if not t)
    reads = surface_reads(pkg, eng)
    dangling = sorted(k for k in reads if k not in keys)
    return {
        "metric": "untyped_payload_keys",
        "value": len(untyped),
        "details": {
            "produced_keys": len(keys),
            "typed_keys": len(keys) - len(untyped),
            "typeddict_classes": len(flow.td),
            "dynamic_key_sites": sorted(dyn),
            "surface_keys_read": len(reads),
            "read_but_not_produced": {k: reads[k] for k in dangling},
            "produced_but_unread_by_surfaces": len([k for k in keys if k not in reads]),
            "untyped": untyped,
        },
        "runtime_s": round(time.perf_counter() - t0, 3),
    }

