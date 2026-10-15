"""P10 sweep enumerator: model-kernel seams reachable from an ``async def`` by direct calls.

Static call graph over the package resolved by receiver (module.f -> that module, self.f / f -> same file).  An edge is a direct ``ast.Call``;
a function handed to ``_await_process``/``_await_off_loop``/``async_add_executor_job``
is an argument, not a call, so every off-loop hop cuts the edge by construction.
Kernel seams are the same set as ``D14/s1/p10_seams.py`` (simulate_*, linalg, scipy.optimize).
Prints one ``LOOP`` line per seam reachable from the loop, then ``RESULT loop_reachable_seams=N``.
Usage: python3 p10_loop_reach.py [--pkg DIR] [--seam FILE:FUNC]   (run from the repo root)
"""
import argparse, ast
from collections import defaultdict, deque
from pathlib import Path

LINALG = ("lstsq", "solve", "inv", "pinv", "eig", "eigh", "svd", "cholesky")
OPT = ("minimize", "linprog", "least_squares", "curve_fit", "nnls", "minimize_scalar")


def is_kernel(name):
    return bool(name) and (name in LINALG + OPT or name.startswith("simulate_"))


def cname(c):
    f = c.func
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)


def target_file(c, here, stems):
    """The file a call resolves into: ``mod.f`` -> mod.py, ``self.f``/``f`` -> here,
    any other receiver -> None (unresolved; the dynamic harness covers it)."""
    f = c.func
    if isinstance(f, ast.Name):
        return here
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        r = f.value.id
        if r in ("self", "cls", "coord", "coordinator", "ctx"):
            return here
        if r in stems:
            return stems[r] + ".py"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pkg", default="custom_components/heatpump_optimizer")
    ap.add_argument("--seam", default=None,
                    help="probe mode: exit 1 iff a listed seam starts with this file:function")
    a = ap.parse_args()
    stems = {p.stem: p.stem for p in Path(a.pkg).glob("*.py")}
    for f in Path(a.pkg).glob("*.py"):  # ``from . import away as away_mode``
        for n in ast.walk(ast.parse(f.read_text())):
            if isinstance(n, ast.ImportFrom) and n.level == 1 and not n.module:
                for al in n.names:
                    if al.asname and al.name in stems:
                        stems[al.asname] = al.name
    defs, edges, roots, seams = {}, defaultdict(set), set(), defaultdict(set)
    for f in sorted(Path(a.pkg).glob("*.py")):
        tree = ast.parse(f.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            key = f"{f.name}:{fn.name}"
            defs.setdefault(fn.name, set()).add(key)
            if isinstance(fn, ast.AsyncFunctionDef):
                roots.add(key)
            for n in ast.walk(fn):
                if isinstance(n, ast.Call):
                    nm = cname(n)
                    if is_kernel(nm):
                        seams[key].add(nm)
                    elif nm:
                        edges[key].add((target_file(n, f.name, stems), nm))
    seen, q, via = set(roots), deque(roots), {r: [r] for r in roots}
    while q:
        k = q.popleft()
        for tf, nm in edges[k]:
            for t in defs.get(nm, ()):
                if tf is None or not t.startswith(tf + ":"):
                    continue
                if t not in seen:
                    seen.add(t); via[t] = via[k] + [f"{nm}->{t}"]; q.append(t)
    hits = sorted((k, s) for k in seen for s in seams.get(k, ()))
    for k, s in hits:
        print(f"LOOP {k}:{s}  via {' / '.join(via[k])}")
    print(f"RESULT loop_reachable_seams={len(hits)}")
    if a.seam is not None:
        bad = [k for k, _ in hits if k.startswith(a.seam)]
        print(f"PROBE {a.seam}: {'FAIL on the loop' if bad else 'pass'}")
        raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
