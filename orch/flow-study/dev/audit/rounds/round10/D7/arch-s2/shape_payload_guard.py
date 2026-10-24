"""Shape: 'a sensor publishes one payload value as its number' -- every guard spelling, and their answers.

Metric: implementations = native_value properties in sensor.py whose body reads one payload key
and publishes it through a guard (seam rule: an AST walk over every class; the guard family is the
returned expression's shape: ``round(v, n) if v is not None``, ``v if isinstance(v, <types>)``,
``_as_float(...)``, ``round(v, n) if isinstance(...)``). owners = distinct guard functions/properties
the package uses for it. disagreeing_probes = probe values that, placed at the property's own
payload key, do not publish the same state through every family. Key: the value the production
property RETURNS (the entity object's native_value), driven on a real sensor class with a stub
coordinator.

Perturbation: --tree PROTO measures a tree with patches 01+02 applied; the 24 per-sensor
properties collapse into the two mixins, implementations drops to the residue.

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/shape_payload_guard.py [--patch P ...]
Expected at baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef: see REPORT.md, tolerance 0.
Machine: the seat's macOS box; counts only. Writes only under a tempfile.mkdtemp root.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import importlib  # noqa: E402
import math  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
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
PROBES = [21.456, 0, True, "21.5", float("nan"), None]


def family(fn: ast.FunctionDef) -> str | None:
    ret = [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None
           and not (isinstance(n.value, ast.Constant) and n.value.value is None)]
    if not ret:
        return None
    src = ast.unparse(ret[0].value)
    body = ast.unparse(fn)
    if "self.coordinator.data" not in body and "self._data()" not in body:
        return None
    if src.startswith("round(") and "is not None" in src:
        return "round_if_not_none"
    if src.startswith("round(") and "isinstance" in src:
        return "round_if_number"
    if " if isinstance(" in src and "bool" not in src:
        return "isinstance_number"
    if src.startswith("_as_float("):
        return "_as_float"
    return None


def payload_path(fn: ast.FunctionDef) -> list[str] | None:
    calls = sorted((n for n in ast.walk(fn) if isinstance(n, ast.Call)), key=lambda n: (n.lineno, n.col_offset))
    keys = [n.args[0].value for n in calls if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and n.func.attr == "get" and n.args
            and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)]
    return keys or None


def nest(path, value):
    out = value
    for k in reversed(path):
        out = {k: out}
    return out


def show(v):
    if isinstance(v, float) and math.isnan(v):
        return "nan"
    return repr(v)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", action="append", default=[], type=Path)
    a = ap.parse_args()
    t0, c0 = time.time(), time.process_time()
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    from archscore.score import tree_of
    root = Path(tempfile.mkdtemp(prefix="arch-s2-guard-"))
    try:
        tree = tree_of(BASE, root / "t")
        for p in a.patch:
            subprocess.run(["patch", "-p1", "-s", "-d", str(tree), "-i", str(p.resolve())], check=True)
        sys.path.insert(0, str(tree / "custom_components"))
        sensor = importlib.import_module("heatpump_optimizer.sensor")
        src = (tree / "custom_components" / "heatpump_optimizer" / "sensor.py").read_text()
        fams = Counter()
        sites = defaultdict(list)
        for cls in ast.parse(src).body:
            if not isinstance(cls, ast.ClassDef):
                continue
            for fn in cls.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == "native_value":
                    f = family(fn)
                    if f:
                        fams[f] += 1
                        sites[f].append((cls.name, payload_path(fn)))
        print(f"RESULT implementations={sum(fams.values())} count")
        for f, n in sorted(fams.items()):
            print(f"RESULT family_{f}={n} count")
        print(f"RESULT guard_families={len(fams)} count")
        # drive EVERY site: each probe placed at the property's own payload path
        vectors = {}
        for f, rows in sorted(sites.items()):
            for cname, path in rows:
                if not path:
                    continue
                cls = getattr(sensor, cname)
                got = []
                for v in PROBES:
                    ent = object.__new__(cls)
                    ent.coordinator = types.SimpleNamespace(data=nest(path, v), last_update_success=True)
                    try:
                        got.append(show(cls.native_value.fget(ent)))
                    except Exception as exc:  # noqa: BLE001 -- a raise is the answer
                        got.append(type(exc).__name__)
                # driven: the plain float comes back, so the inferred path was the property's own
                if got[0] == "None":
                    continue
                vectors[f"{f}:{cname}"] = tuple(got)
        print(f"RESULT driven_sites={len(vectors)} count")
        distinct = defaultdict(list)
        for k, vec in vectors.items():
            # the rounding precision is a declared per-sensor choice, not a guard
            distinct[("21.x",) + vec[1:]].append(k)
        print(f"RESULT distinct_answer_vectors={len(distinct)} count")
        print("probe".ljust(26), *[show(p).rjust(10) for p in PROBES[1:]], "  sites")
        for vec, ks in sorted(distinct.items(), key=lambda kv: -len(kv[1])):
            fam = sorted({k.split(':')[0] for k in ks})
            print(f"{len(ks):>3} x {','.join(fam)[:20]:<20}", *[v[:10].rjust(10) for v in vec[1:]],
                  "  e.g.", ks[0].split(':')[1])
        dis = [show(p) for i, p in enumerate(PROBES) if i and len({vec[i] for vec in distinct}) > 1]
        print(f"RESULT disagreeing_probes={len(dis)} count")
        print(f"RESULT disagreeing_probe_values={','.join(dis) or '-'}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=unmeasured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
