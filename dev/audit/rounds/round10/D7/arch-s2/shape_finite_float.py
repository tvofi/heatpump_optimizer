"""Shape: 'coerce one value to a float, or a fallback' -- every implementation, and whether they agree.

Metric: implementations = module-level functions in the package whose name matches SEAM_RE, whose
return annotation names ``float``, and whose body calls the builtin ``float`` (the seam rule, an
AST walk; nothing is listed by hand). disagreeing_inputs = probe inputs on which the
implementations, each called with fallback None (or its own default sentinel), do not all return
the same value. Key: the value the production helper RETURNS for the probe.

Perturbation: --patch patches/06_finite_float_owner.patch measures the prototype tree: the five
finite-checking helpers and pump_arbiter's become one owner, so implementations falls 9 -> 4; the
residue (away, wood_fuel, sensor) is the bool/text policy REPORT.md leaves to the owner.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/shape_finite_float.py [--patch P]
Expected at baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef: implementations=9, disagreeing_inputs=10,
tolerance 0. The tree measured is the baseline extracted from git (plus any --patch), never the
working tree. Machine: the seat's macOS box; counts only.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import importlib  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
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
PKG: Path = Path()
SEAM_RE = re.compile(r"^_?(as_float|as_num|optional_float|finite|finite_or_none|finite_float|number|at_least)$")
SENTINEL = -12345.0


def seams():
    out, seen = [], set()
    for p in sorted(PKG.glob("*.py")):
        for fn in ast.parse(p.read_text()).body:
            if not isinstance(fn, ast.FunctionDef) or not SEAM_RE.match(fn.name):
                continue
            if fn.returns is None or "float" not in ast.unparse(fn.returns):
                continue
            first = fn.args.args[0].annotation if fn.args.args else None
            if first is not None and "Mapping" in ast.unparse(first):
                continue  # modbus_prefill._number(snap, label): a lookup, not a coercion
            if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "float"
                       for n in ast.walk(fn)):
                continue
            if (p.stem, fn.name) in seen:
                continue  # an @overload stub; the implementation is the last def
            seen.add((p.stem, fn.name))
            out.append((p.stem, fn.name, fn.lineno, [a.arg for a in fn.args.args]))
    return out


PROBES = [None, 0, 3, 2.5, True, False, "2.5", "", "warm", "nan", "inf", float("nan"), float("inf"),
          -float("inf"), 10 ** 400, [1], b"3"]


def call(fn, params, value):
    """The helper's answer, its fallback normalised: a default parameter gets SENTINEL and a
    returned SENTINEL or None reads as 'refused'; a raise reads as its exception name."""
    try:
        if len(params) == 1:
            got = fn(value)
        elif params[1] in ("default",):
            got = fn(value, SENTINEL)
        elif params[1] == "lo":
            got = fn(value, -math.inf, SENTINEL)
        else:
            return "n/a"
    except Exception as exc:  # noqa: BLE001 -- a raise is an answer
        return type(exc).__name__
    if got is None or got == SENTINEL:
        return "refused"
    if isinstance(got, float) and math.isnan(got):
        return "nan"
    return repr(float(got)) if isinstance(got, (int, float)) else repr(got)


def main() -> int:
    global PKG
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", action="append", default=[], type=Path)
    a = ap.parse_args()
    t0, c0 = time.time(), time.process_time()
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    from archscore.score import tree_of
    tmp = Path(tempfile.mkdtemp(prefix="arch-s2-ff-"))
    tree = tree_of(BASE, tmp / "t")
    for p in a.patch:
        subprocess.run(["patch", "-p1", "-s", "-d", str(tree), "-i", str(p.resolve())], check=True)
    PKG = tree / "custom_components" / "heatpump_optimizer"
    sys.path.insert(0, str(tree / "custom_components"))
    rows = seams()
    print(f"RESULT implementations={len(rows)} count")
    table = {}
    for mod, name, line, params in rows:
        m = importlib.import_module(f"heatpump_optimizer.{mod}")
        table[f"{mod}.{name}:{line}"] = [call(getattr(m, name), params, v) for v in PROBES]
    w = max(len(k) for k in table) if table else 10
    print("probe".ljust(w), *[repr(v)[:8].rjust(9) for v in PROBES])
    for k, vals in table.items():
        print(k.ljust(w), *[str(v)[:9].rjust(9) for v in vals])
    disagree = []
    for i, v in enumerate(PROBES):
        answers = {vals[i] for vals in table.values() if vals[i] != "n/a"}
        if len(answers) > 1:
            disagree.append(repr(v)[:12])
    print(f"RESULT disagreeing_inputs={len(disagree)} count")
    print(f"RESULT disagreeing_probes={','.join(disagree) or '-'}")
    shutil.rmtree(tmp, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=unmeasured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
