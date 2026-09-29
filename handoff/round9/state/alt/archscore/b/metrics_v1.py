#!/usr/bin/env python3
"""v1 definitions of the four metrics v0 calibration showed faulty (PRE-STUDY.md section 5.2).

    python3 metrics_v1.py ROOT   -> JSON on stdout

Each fault was predicted before calibration (A1's caveats, A3's own null) and confirmed by a
planted case; none was changed because of a historical-corpus case (the corpus is the holdout).

coord_footprint_v1   logic statements in the coordinator class plus every module-level function
                     a parameter of which carries the coordinator, by ROLE (a3's engine: call
                     sites, not the parameter's name). Plumbing is not logic and is not counted:
                     an alias (x = self.a.b), a bare delegation (self.f(a, b) / coord.f(...) as an
                     expression, return or single assignment whose arguments are names,
                     attributes or constants), and a trivial accessor (return self._x).
                     Fixes: a rename escaping the count (private_reach null: -232), Extract
                     Method / dedupe / accessor reading as growth (G1, G2, G4b +1).
dup_pairs_v1         a1's dup_pairs with two normalisations: a function's own names (parameters
                     and locals) are alpha-renamed in order of first use within the window, and
                     ``mod.X`` for an imported module ``mod`` is read as ``X``. Fixes: the rename
                     null (-1) and the const-namespace null N4 (+1).
import_cycle_modules_v1
                     modules in a non-trivial SCC of the package import graph; function-scope
                     imports included (a1), imports under ``if TYPE_CHECKING:`` excluded (a3).
                     Fixes: a3's fix arm (a TYPE_CHECKING import) still counted by a1; B6b
                     (a function-scope cycle) missed by a3.
params_over_10       unchanged from a1; enters the score as the guard A1 proposed against
                     meaningless fragment chains (B3a +3, B3c +6, G1 0).
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "a3" / "metrics"))
import _common as C  # noqa: E402

DUP_W, DUP_NODES = 2, 30


def _is_doc(s):
    return isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str)


def _simple(e) -> bool:
    return isinstance(e, (ast.Name, ast.Constant)) or (
        isinstance(e, ast.Attribute) and _simple(e.value)) or (
        isinstance(e, ast.Starred) and _simple(e.value))


def _delegation(call) -> bool:
    return isinstance(call, ast.Call) and isinstance(call.func, (ast.Attribute, ast.Name)) \
        and _simple(call.func if isinstance(call.func, ast.Name) else call.func.value) \
        and all(_simple(a) for a in call.args) and all(_simple(k.value) for k in call.keywords)


def _plumbing(s) -> bool:
    if isinstance(s, ast.Expr):
        v = s.value.value if isinstance(s.value, ast.Await) else s.value
        return _delegation(v)
    if isinstance(s, ast.Return) and s.value is not None:
        v = s.value.value if isinstance(s.value, ast.Await) else s.value
        return _delegation(v) or (isinstance(v, ast.Attribute) and _simple(v))
    if isinstance(s, ast.Assign) and len(s.targets) == 1 and isinstance(s.targets[0], ast.Name):
        v = s.value.value if isinstance(s.value, ast.Await) else s.value
        return (isinstance(v, ast.Attribute) and _simple(v)) or _delegation(v)
    return False


def logic_stmts(node) -> int:
    return sum(1 for n in ast.walk(node) if isinstance(n, ast.stmt) and not _is_doc(n)
               and not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
               and not _plumbing(n))


def coord_footprint_v1(pkg, eng) -> tuple[int, list]:
    key = pkg.coord_key
    cls = pkg.classes[key].node
    total = logic_stmts(cls)
    penv, _ = eng.propagate(None)
    charged = []
    for q, fn in sorted(pkg.funcs.items()):
        if fn.cls is not None or fn.node not in pkg.mods[fn.mod].tree.body:
            continue
        env = penv.get(q, {})
        if any(C.COORD in env.get(p, frozenset()) for p in fn.params):
            n = logic_stmts(fn.node)
            total += n
            charged.append(f"{fn.mod}.{fn.name}:{n}")
    return total, charged


def _module_aliases(tree) -> set[str]:
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module is None:
            out |= {a.asname or a.name for a in n.names}
    return out


def _local_names(fn) -> set[str]:
    a = fn.args
    names = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
    names |= {x.arg for x in (a.vararg, a.kwarg) if x}
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            names.add(n.id)
    return names


def _norm_window(w, local, modalias) -> str:
    mapping: dict[str, str] = {}
    out = []
    for s in w:
        s = ast.parse(ast.unparse(s)).body[0]

        class T(ast.NodeTransformer):
            def visit_Attribute(self, n):
                self.generic_visit(n)
                if isinstance(n.value, ast.Name) and n.value.id in modalias and n.value.id not in local:
                    return ast.copy_location(ast.Name(id=n.attr, ctx=n.ctx), n)
                return n

            def visit_Name(self, n):
                if n.id in local:
                    n.id = mapping.setdefault(n.id, f"v{len(mapping)}")
                return n

            def visit_Constant(self, n):
                if isinstance(n.value, str):
                    n.value = "S"
                return n
        out.append(ast.dump(T().visit(s)))
    return "".join(out)


def dup_pairs_v1(pkg) -> int:
    win = defaultdict(set)
    for mname, m in sorted(pkg.mods.items()):
        modalias = _module_aliases(m.tree)
        for fn in ast.walk(m.tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            local = _local_names(fn)
            for node in ast.walk(fn):
                if node is not fn and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                    continue
                blocks = [getattr(node, f) for f in ("body", "orelse", "finalbody")
                          if isinstance(getattr(node, f, None), list) and getattr(node, f)
                          and isinstance(getattr(node, f)[0], ast.stmt)]
                blocks += [h.body for h in getattr(node, "handlers", []) or []]
                for b in blocks:
                    b = [s for s in b if not _is_doc(s)]
                    for i in range(len(b) - DUP_W + 1):
                        w = b[i:i + DUP_W]
                        if any(isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for s in w):
                            continue
                        if sum(1 for s in w for _ in ast.walk(s)) < DUP_NODES:
                            continue
                        key = hashlib.sha1(_norm_window(w, local, modalias).encode()).hexdigest()
                        win[key].add((mname, fn.name, fn.lineno))
    pairs = set()
    for owners in win.values():
        o = sorted(owners)
        for i in range(len(o)):
            for j in range(i + 1, len(o)):
                pairs.add((o[i], o[j]))
    return len(pairs)


def import_cycle_modules_v1(pkg) -> int:
    g = defaultdict(set)
    names = set(pkg.mods)
    for mname, m in pkg.mods.items():
        tc = C._in_type_checking(m.tree)
        for n in ast.walk(m.tree):
            if id(n) in tc or not isinstance(n, ast.ImportFrom) or n.level != 1:
                continue
            if n.module:
                g[mname].add(n.module.split(".")[0])
            else:
                g[mname] |= {a.name for a in n.names}
    idx, low, st, on, cnt, c = {}, {}, [], set(), [0], [0]
    sys.setrecursionlimit(10000)

    def sc(v):
        idx[v] = low[v] = c[0]
        c[0] += 1
        st.append(v)
        on.add(v)
        for w in sorted(g[v]):
            if w not in names:
                continue
            if w not in idx:
                sc(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                cnt[0] += len(comp)
    for v in sorted(names):
        if v not in idx:
            sc(v)
    return cnt[0]


def measure(root: Path) -> dict:
    pkg = C.load(str(root))
    eng = C.engine(pkg)
    fp, charged = coord_footprint_v1(pkg, eng)
    return {"coord_footprint_v1": fp, "dup_pairs_v1": dup_pairs_v1(pkg),
            "import_cycle_modules_v1": import_cycle_modules_v1(pkg), "_footprint_charged": len(charged)}


if __name__ == "__main__":
    print(json.dumps(measure(Path(sys.argv[1]).resolve()), sort_keys=True))
