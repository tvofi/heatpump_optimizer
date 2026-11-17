"""N-no-expiry seam census (D14-s2, round 11): covering-now reads the class barrier's AST shape cannot see.

Metric: number of sites in custom_components/heatpump_optimizer/*.py that read
a time-indexed container by a constant position -- ``X[0]`` or ``X[-1]`` where
X's source text names a timed series (forecast, series, prices, timestamps,
samples, history, readings) -- printed one per line as
``SEAM file:line function expr``, next to the barrier's own count:
tests/entities.py's ``_r10_covering_lookups`` (its source extracted by AST and
exec'd, never copied), which counts only ``bisect_right(...) - 1``.

This lists candidate seams. Each needs a per-site disposition: an index-0 read
of a series the caller has already matched to now is guarded. The one
demonstrated instance is current_weather.py's ``_current_weather``.

Perturbation (``--plant``): add one ``return self._weather_forecast[-1]`` method to the
coordinator source in memory -> census count +1, barrier count unchanged (the
barrier's blindness, measured on its own function).

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D14/s2/covering_census.py [--plant]
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT barrier_bisect_sites=6 (exact),
RESULT census_constant_index_sites=N (exact, printed); --plant: census N+1, barrier 6.
"""
import os

for _threads in (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
):
    os.environ.setdefault(_threads, "1")

import argparse
import ast
import re
import sys
import time
from collections import Counter
from pathlib import Path

TIMED = re.compile(r"(forecast|series|prices|timestamps|samples|history|readings)", re.I)
PLANT = "\n\nclass _Planted:\n    def _planted_now(self):\n        return self._weather_forecast[-1]\n"


def _barrier_fn():
    """tests/entities.py's own _r10_functions/_r10_covering_lookups, extracted by AST."""
    src = Path("tests/entities.py").read_text()
    tree = ast.parse(src)
    keep = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ("_r10_functions", "_r10_covering_lookups")]
    assert len(keep) == 2, "barrier functions not found"
    ns = {"ast": ast, "Counter": Counter}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "tests/entities.py", "exec"), ns)
    return ns["_r10_covering_lookups"]


def census(sources):
    out = []
    for name, source in sorted(sources.items()):
        tree = ast.parse(source)

        def walk(node, fn):
            for ch in ast.iter_child_nodes(node):
                inner = ch if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn
                if (isinstance(ch, ast.Subscript) and isinstance(ch.slice, (ast.Constant, ast.UnaryOp))
                        and not isinstance(ch.ctx, ast.Store)):
                    idx = ast.unparse(ch.slice)
                    base = ast.unparse(ch.value)
                    if idx in ("0", "-1") and TIMED.search(base):
                        out.append((name, ch.lineno, fn.name if fn else "<module>", ast.unparse(ch)))
                walk(ch, inner)

        walk(tree, None)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    t0, c0 = time.thread_time(), time.process_time()
    pkg = Path("custom_components/heatpump_optimizer")
    sources = {p.name: p.read_text() for p in sorted(pkg.glob("*.py"))}
    if a.plant:
        sources["coordinator.py"] += PLANT
    rows = census(sources)
    for r in rows:
        print("SEAM {}:{} {} {}".format(*r))
    barrier = _barrier_fn()(sources)
    print(f"RESULT census_constant_index_sites={len(rows)} sites")
    print(f"RESULT census_functions={len({(r[0], r[2]) for r in rows})} functions")
    print(f"RESULT barrier_bisect_sites={sum(barrier.values())} sites")
    tf = (time.process_time() - c0) / max(time.thread_time() - t0, 1e-9)
    print(f"RESULT thread_factor={tf:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        with open("/proc/vmstat") as f:
            print("RESULT swapins=" + next(l.split()[1] for l in f if l.startswith("pswpin")))
    except OSError:
        print("RESULT swapins=unknown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
