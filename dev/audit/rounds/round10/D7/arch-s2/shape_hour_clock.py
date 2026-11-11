"""Shape: 'an hour-of-day float as a clock' -- every implementation, and whether they agree.

Metric: implementations = functions (nested ones included) in the package whose body rounds
``<hour> * 60`` to whole minutes and reduces it by a day (``24 * 60``): the seam rule, an AST walk.
disagreeing_hours = probe hours on which the driven implementations, each read back as "HH:MM",
do not all agree. Key: the string or clock each production function returns.

Perturbation: --patch patches/05_hour_clock.patch; the seam rule then finds the two owners
(dhw_schedule.format_clock, quiet_windows.wall_clock), and the remaining disagreement is exactly
the one the two names declare (24:00 kept by the label, folded by the clock).

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/shape_hour_clock.py [--patch P]
Expected at baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef: implementations=5, disagreeing_hours=2,
tolerance 0. Machine: the seat's macOS box; counts only.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import datetime as _dt  # noqa: E402
import importlib  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

def repo_root(start):
    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
    from pathlib import Path
    here = Path(start).resolve()
    if here.is_file():
        here = here.parent
    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
    for cand in (here, *here.parents):
        if (cand / marker).is_file():
            return cand
    raise RuntimeError(f"no repository root above {start}")


REPO = repo_root(__file__)
BASE = "554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef"
HOURS = [0.0, 6.5, 7.9999, 23.999, 24.0, 12.25]


def is_seam(fn) -> bool:
    has_round = has_day = False
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "round" and n.args:
            a = n.args[0]
            if isinstance(a, ast.BinOp) and isinstance(a.op, ast.Mult) and any(
                    isinstance(x, ast.Constant) and x.value in (60, 60.0) for x in (a.left, a.right)):
                has_round = True
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult) and ast.unparse(n) == "24 * 60":
            has_day = True
    return has_round and has_day


def seams(pkg: Path):
    out = []
    for p in sorted(pkg.glob("*.py")):
        tree = ast.parse(p.read_text())
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_seam(fn):
                # the innermost function that holds the arithmetic
                inner = [g for g in ast.walk(fn) if g is not fn and isinstance(g, ast.FunctionDef) and is_seam(g)]
                if not inner:
                    out.append((p.stem, fn.name, fn.lineno))
    return out


def driver(mod, name):
    f = getattr(mod, name, None)
    if name == "fmt":  # dhw_schedule.format_windows's nested formatter
        return lambda h: mod.format_windows([(h, h)]).split("-")[0]
    if name == "_gchv_at":
        return lambda h: f(_dt.date(2026, 1, 5), h, _dt.timezone.utc).strftime("%H:%M")
    if f is None:
        return None
    def call(h):
        r = f(h)
        return f"{r[0]:02d}:{r[1]:02d}" if isinstance(r, tuple) else r
    return call


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", action="append", default=[], type=Path)
    a = ap.parse_args()
    t0, c0 = time.time(), time.process_time()
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    from archscore.score import tree_of
    tmp = Path(tempfile.mkdtemp(prefix="arch-s2-clock-"))
    try:
        tree = tree_of(BASE, tmp / "t")
        for p in a.patch:
            subprocess.run(["patch", "-p1", "-s", "-d", str(tree), "-i", str(p.resolve())], check=True)
        sys.path.insert(0, str(tree / "custom_components"))
        rows = seams(tree / "custom_components" / "heatpump_optimizer")
        print(f"RESULT implementations={len(rows)} count")
        table = {}
        for mod_name, name, line in rows:
            mod = importlib.import_module(f"heatpump_optimizer.{mod_name}")
            d = driver(mod, name)
            if d is None:
                print(f"  undriven: {mod_name}.{name}:{line}")
                continue
            table[f"{mod_name}.{name}:{line}"] = [d(h) for h in HOURS]
        w = max(map(len, table)) if table else 5
        print("hour".ljust(w), *[f"{h:>8}" for h in HOURS])
        for k, v in table.items():
            print(k.ljust(w), *[f"{x:>8}" for x in v])
        dis = [h for i, h in enumerate(HOURS) if len({v[i] for v in table.values()}) > 1]
        print(f"RESULT disagreeing_hours={len(dis)} count")
        print(f"RESULT disagreeing_hour_values={','.join(map(str, dis)) or '-'}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=unmeasured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
