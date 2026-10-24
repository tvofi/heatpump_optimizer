"""Behaviour equivalence for patches 00+01+02: every sensor's published native_value before and after.

Metric: mismatches = (sensor class, probe) pairs whose published native_value -- through the real
property Home Assistant reads, finite scrub included -- differs between the baseline tree and the
patched tree. The probe is placed at the payload path the BASELINE property reads (inferred from its
AST); classes whose path cannot be inferred are counted as not driven. Key: the value the property
returns on the entity object.

Perturbation: run with patches 01+02 but WITHOUT 00 (the scrub that resolves through the MRO):
the NaN/inf probes must then mismatch (the mixin-supplied property escapes the scrub).

Run (from the repository root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/arch-s2/equiv_sensor_values.py \
        --patch dev/audit/rounds/round10/D7/arch-s2/patches/00_scrub_resolves_mro.patch \
        --patch dev/audit/rounds/round10/D7/arch-s2/patches/01_payload_value_mixin.patch \
        --patch dev/audit/rounds/round10/D7/arch-s2/patches/02_payload_path_mixin.patch
Expected: mismatches=0 (tolerance 0); without patch 00: mismatches > 0.
Baseline 554e2ecfa7ad5b1660a1256ebf6cf6ac3810d9ef. Machine: the seat's macOS box.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import ast  # noqa: E402
import json  # noqa: E402
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

CHILD = r'''
import importlib, json, math, sys, types
sys.path.insert(0, sys.argv[1])
paths = json.loads(sys.argv[2])
sensor = importlib.import_module("heatpump_optimizer.sensor")
PROBES = [21.456, 0, -3.25, True, "21.5", float("nan"), float("inf"), None, 7]
def nest(path, v):
    for k in reversed(path):
        v = {k: v}
    return v
def show(v):
    if isinstance(v, float) and math.isnan(v):
        return "nan"
    return repr(v)
out = {}
for cname, path in paths.items():
    cls = getattr(sensor, cname)
    row = []
    for v in PROBES:
        ent = object.__new__(cls)
        ent.coordinator = types.SimpleNamespace(data=nest(path, v), last_update_success=True)
        try:
            row.append(show(cls.native_value.fget(ent)))
        except Exception as exc:
            row.append(type(exc).__name__)
    out[cname] = row
print(json.dumps(out))
'''


def baseline_paths(src: str) -> dict:
    out = {}
    for cls in ast.parse(src).body:
        if not isinstance(cls, ast.ClassDef):
            continue
        for fn in cls.body:
            if isinstance(fn, ast.FunctionDef) and fn.name == "native_value":
                calls = sorted((n for n in ast.walk(fn) if isinstance(n, ast.Call)),
                               key=lambda n: (n.lineno, n.col_offset))
                keys = [n.args[0].value for n in calls if isinstance(n.func, ast.Attribute)
                        and n.func.attr == "get" and n.args and isinstance(n.args[0], ast.Constant)
                        and isinstance(n.args[0].value, str)]
                if keys:
                    out[cls.name] = keys
    return out


def answers(tree: Path, paths: dict) -> dict:
    env = dict(os.environ, PYTHONPATH=str(REPO / "tests" / "hastub"))
    r = subprocess.run([sys.executable, "-c", CHILD, str(tree / "custom_components"), json.dumps(paths)],
                       capture_output=True, text=True, env=env, check=True)
    return json.loads(r.stdout.strip().splitlines()[-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", action="append", default=[], type=Path)
    a = ap.parse_args()
    t0, c0 = time.time(), time.process_time()
    sys.path.insert(0, str(REPO / "tools" / "audit"))
    from archscore.score import tree_of
    root = Path(tempfile.mkdtemp(prefix="arch-s2-sv-"))
    try:
        base = tree_of(BASE, root / "base")
        head = root / "head"
        shutil.copytree(base, head)
        for p in a.patch:
            subprocess.run(["patch", "-p1", "-s", "-d", str(head), "-i", str(p.resolve())], check=True)
        paths = baseline_paths((base / "custom_components/heatpump_optimizer/sensor.py").read_text())
        b, h = answers(base, paths), answers(head, paths)
        bad = [(c, i, b[c][i], h[c][i]) for c in b for i in range(len(b[c])) if b[c][i] != h[c][i]]
        print(f"RESULT sensors_driven={len(paths)} count")
        print(f"RESULT probes={sum(len(v) for v in b.values())} count")
        print(f"RESULT mismatches={len(bad)} count")
        for row in bad[:12]:
            print("  ", row)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    wall, cpu = time.time() - t0, time.process_time() - c0
    print(f"RESULT thread_factor={cpu / wall if wall else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=unmeasured")
    return 0


if __name__ == "__main__":
    sys.exit(main())
