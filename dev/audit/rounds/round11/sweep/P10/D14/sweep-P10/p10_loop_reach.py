#!/usr/bin/env python3
"""Round-11 P10 sweep enumerator: model-kernel seams reachable from an ``async def`` by direct calls.

Round 10's enumerator (dev/audit/rounds/round10/D14/sweep-P10/p10_loop_reach.py) left a call on
any receiver other than ``self``/a module unresolved; D9-s1-04 sits exactly there
(``whatif.schedule_days`` calls ``o.reference_day(i)`` on an optimizer it was handed). This one
keeps its rules and closes that blind spot:

* Edges: every ``ast.Call`` in a function (nested defs are their own functions). ``mod.f`` -> that
  module (relative-import aliases included); ``self.f``/``cls.f``/bare ``f`` -> the same file, or the
  module a ``from .mod import f`` names (a bare name defined nowhere is a callable parameter and
  stays unresolved); ANY OTHER RECEIVER (``o.f``, ``self.model.f``; a logger excluded) -> every
  package function named ``f`` when the package defines it at most ``--fanout`` times (default 3;
  a name defined more often is too generic to resolve and stays unresolved, printed on stderr).
* Off-loop cut: a function handed to ``_await_process`` / ``_await_off_loop`` /
  ``async_add_executor_job`` is an argument, not a call, so no edge is made.
* Kernels: ``*.simulate_*`` on any receiver; the linalg/optimize names (solve, lstsq, minimize,
  linprog, ...) only when the receiver is ``linalg``/``np.linalg``/``numpy.linalg``/``optimize``/
  ``scipy.optimize`` or the bare name was imported from numpy/scipy (round 10 counted a callable
  parameter named ``solve`` as a kernel).
* Roots: every ``async def``.

  python3 p10_loop_reach.py [--pkg DIR] [--fanout N] [--seam FILE:FUNC] [--null] [--perturb]
Prints ``LOOP <file>:<func>:<kernel>  via <chain>`` per loop-reachable seam, ``SEAM`` lines for every
kernel seam (reachable or not), then RESULT lines. ``--seam`` exits 1 iff that seam is loop-reachable.
``--null``: a clean two-file fixture (kernel reached only through _await_off_loop) -> 0.
``--perturb``: the same fixture with one line changed (the hop removed) -> 1.
"""
from __future__ import annotations

import argparse
import ast
import sys
import tempfile
from collections import defaultdict, deque
from pathlib import Path

LINALG = ("lstsq", "solve", "inv", "pinv", "eig", "eigh", "svd", "cholesky")
OPT = ("minimize", "linprog", "least_squares", "curve_fit", "nnls", "minimize_scalar")
NUM_RECV = ("linalg", "optimize")
HOPS = ("_await_process", "_await_off_loop", "async_add_executor_job")


def recv_text(f):
    parts = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
    return ".".join(reversed(parts))


def kernel_of(call, numeric_names):
    f = call.func
    name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
    if not name:
        return None
    if name.startswith("simulate_"):
        return name
    if name in LINALG + OPT:
        if isinstance(f, ast.Attribute):
            r = recv_text(f.value)
            if r.split(".")[-1] in NUM_RECV:
                return name
        elif name in numeric_names:
            return name
    return None


def functions(tree):
    out = []

    def walk(node, prefix):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((prefix + ch.name, ch))
                walk(ch, prefix + ch.name + ".")
            elif isinstance(ch, ast.ClassDef):
                walk(ch, prefix)
            else:
                walk(ch, prefix)
    walk(tree, "")
    return out


def own_calls(fn):
    stack, out = list(ast.iter_child_nodes(fn)), []
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if isinstance(n, ast.Call):
            out.append(n)
        stack.extend(ast.iter_child_nodes(n))
    return out


def analyse(pkg: Path, fanout: int, through_hops: bool = False):
    files = sorted(pkg.glob("*.py"))
    stems = {p.stem: p.stem for p in files}
    trees = {p.name: ast.parse(p.read_text()) for p in files}
    from_imports = defaultdict(dict)   # file -> {local name: module stem}
    numeric = defaultdict(set)         # file -> bare names imported from numpy/scipy
    for fname, tree in trees.items():
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom):
                if n.level == 1 and not n.module:
                    for al in n.names:
                        if al.name in stems:
                            stems[al.asname or al.name] = al.name
                elif n.level == 1 and n.module in stems:
                    for al in n.names:
                        from_imports[fname][al.asname or al.name] = n.module
                elif n.module and n.module.split(".")[0] in ("numpy", "scipy"):
                    for al in n.names:
                        numeric[fname].add(al.asname or al.name)
    defs = defaultdict(list)  # bare name -> [(file, qualname)]
    fns = {}
    for fname, tree in trees.items():
        for q, fn in functions(tree):
            fns[(fname, q)] = fn
            defs[q.split(".")[-1]].append((fname, q))
    by_file_name = defaultdict(list)
    for (fname, q) in fns:
        by_file_name[(fname, q.split(".")[-1])].append(q)

    edges, roots, seams, unresolved = defaultdict(set), set(), defaultdict(set), defaultdict(int)
    hop_edge = set()
    for (fname, q), fn in fns.items():
        key = (fname, q)
        if isinstance(fn, ast.AsyncFunctionDef):
            roots.add(key)
        for c in own_calls(fn):
            k = kernel_of(c, numeric[fname])
            if k:
                seams[key].add(k)
                continue
            f = c.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name in HOPS and through_hops:
                # --through-hops: follow the function a hop is handed, marking the edge, so the
                # report can name the hop that guards each seam the default run does not reach.
                for arg in c.args:
                    an = arg.attr if isinstance(arg, ast.Attribute) else getattr(arg, "id", None)
                    if not an:
                        continue
                    if isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name) and arg.value.id in stems:
                        tg = [(stems[arg.value.id] + ".py", q2) for q2 in by_file_name[(stems[arg.value.id] + ".py", an)]]
                    elif an in from_imports[fname]:
                        tg = [(from_imports[fname][an] + ".py", q2) for q2 in by_file_name[(from_imports[fname][an] + ".py", an)]]
                    else:
                        tg = [(fname, q2) for q2 in by_file_name[(fname, an)]] or (
                            list(defs[an]) if len(defs.get(an, ())) <= fanout else [])
                    for t in tg:
                        edges[key].add(t)
                        hop_edge.add((key, t, name))
                continue
            if not name or name in HOPS:
                continue
            targets = []
            if isinstance(f, ast.Name):
                if name in from_imports[fname]:
                    targets = [(from_imports[fname][name] + ".py", q2)
                               for q2 in by_file_name[(from_imports[fname][name] + ".py", name)]]
                else:
                    targets = [(fname, q2) for q2 in by_file_name[(fname, name)]]
            elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in ("self", "cls"):
                targets = [(fname, q2) for q2 in by_file_name[(fname, name)]]
            elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in stems:
                mod = stems[f.value.id] + ".py"
                targets = [(mod, q2) for q2 in by_file_name[(mod, name)]]
            other_receiver = (isinstance(f, ast.Attribute) and not targets
                              and "log" not in recv_text(f.value).lower())
            if other_receiver and name in defs:
                if len(defs[name]) <= fanout:
                    targets = list(defs[name])
                else:
                    unresolved[name] += 1
            for t in targets:
                edges[key].add(t)

    via = {r: [f"{r[0]}:{r[1]}"] for r in roots}
    dq = deque(roots)
    while dq:
        k = dq.popleft()
        for t in edges[k]:
            if t in fns and t not in via:
                hop = next((h for kk, tt, h in hop_edge if kk == k and tt == t), None)
                via[t] = via[k] + [(f"[{hop}] " if hop else "") + f"{t[0]}:{t[1]}"]
                dq.append(t)
    all_seams = sorted((f"{k[0]}:{k[1]}", s) for k, ss in seams.items() for s in ss)
    hits = sorted((f"{k[0]}:{k[1]}", s, via[k]) for k, ss in seams.items() for s in ss if k in via)
    return all_seams, hits, unresolved


FIXTURE = {
    "coordinator.py": '''
from . import model
async def _await_off_loop(hass, fn, *args):
    return fn(*args)
class Coordinator:
    async def async_simulate(self, opt):
        return await _await_off_loop(None, model.reference_day, opt)
''',
    "model.py": '''
class Model:
    def simulate_step(self, s):
        return s
def reference_day(opt):
    return opt.model.simulate_step(1)
''',
}
PERTURB = ("        return await _await_off_loop(None, model.reference_day, opt)",
           "        return model.reference_day(opt)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default="custom_components/heatpump_optimizer")
    ap.add_argument("--fanout", type=int, default=3)
    ap.add_argument("--seam")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    ap.add_argument("--through-hops", action="store_true",
                    help="follow hops too; each seam's chain then names the hop ([...]) that guards it")
    a = ap.parse_args()
    pkg = Path(a.pkg)
    if a.null or a.perturb:
        pkg = Path(tempfile.mkdtemp())
        for name, src in FIXTURE.items():
            if a.perturb and name == "coordinator.py":
                src = src.replace(*PERTURB)
            (pkg / name).write_text(src)
    all_seams, hits, unresolved = analyse(pkg, a.fanout, a.through_hops)
    for s, k in all_seams:
        print(f"SEAM {s}:{k}")
    for s, k, v in hits:
        print(f"LOOP {s}:{k}  via {' / '.join(v)}")
    print(f"RESULT kernel_seams={len(all_seams)}")
    print(f"RESULT loop_reachable_seams={len(hits)}")
    print(f"unresolved generic names (> fanout): {len(unresolved)}", file=sys.stderr)
    if a.seam:
        bad = [s for s, _, _ in hits if s.startswith(a.seam)]
        print(f"PROBE {a.seam}: {'FAIL on the loop' if bad else 'pass'}")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
