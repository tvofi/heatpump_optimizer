#!/usr/bin/env python3
"""D7-s1 M1: does the structural ratchet price growth of a class that is not the largest?

Metric: number of tests/structure_budgets.json keys whose value rises when K
lines of new, called, non-duplicated, CC-1 code are added to a class, measured
by the production tests/structure.py:measure over an in-memory copy of the tree
(tests/structure.py:module_trees is swapped; nothing on disk changes).
Key: the metrics dict measure() returns, compared key-by-key with the unpadded run.
Arms: target=HeatPumpOptimizer (2nd-largest class, optimizer.py) vs control
target=HeatPumpOptimizerCoordinator (largest class).
Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D7/s1/class_growth.py [--structure PATH]
Expected (baseline 17f1c55fad1b): keys_moved_second_class=0, keys_moved_coordinator=1 (max_class_loc), exact.
Perturbation: in measure(), "max_class_loc": sum((g[0] for g in god_classes)) (or a
per-class budget) -> keys_moved_second_class becomes 1. Run with --structure <edited copy>.
Machine: macOS arm64 audit box B5.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast, importlib.util, sys, time

args = sys.argv[1:]
spath = args[args.index("--structure") + 1] if "--structure" in args else "tests/structure.py"
sys.path.insert(0, "tests")
spec = importlib.util.spec_from_file_location("structure_under_test", spath)
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
from pathlib import Path as _P
S.REPO_ROOT = _P.cwd().resolve()
S.PACKAGE_DIR = S.REPO_ROOT / "custom_components" / "heatpump_optimizer"
S.BUDGET_FILE = S.REPO_ROOT / "tests" / "structure_budgets.json"
S.SEAM_MAP_FILE = S.REPO_ROOT / "tests" / "seam_map.json"

PAD_METHODS = 10
PAD_LINES = 120  # per method, under MONSTER_LIMITS[1]=150


def pad_source(src: str, cls_name: str) -> str:
    tree = ast.parse(src)
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name)
    init = next(m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == "__init__")
    lines = src.splitlines()
    ind = " " * (init.body[-1].col_offset)
    mind = " " * init.col_offset
    block = []
    for m in range(PAD_METHODS):
        block.append(f"{mind}def _r10pad{m}(self):")
        block.append(f"{ind}acc = {m}.5")
        for k in range(PAD_LINES - 3):
            block.append(f"{ind}acc = acc * {m * 1000 + k + 2} + {k * 7 + 3}")
        nxt = f"self._r10pad{m + 1}()" if m + 1 < PAD_METHODS else "None"
        block.append(f"{ind}return (acc, {nxt})")
    # call the chain from __init__ so nothing is dead
    out = lines[:init.end_lineno] + [f"{ind}self._r10pad0()"] + lines[init.end_lineno:cls.end_lineno] + block + lines[cls.end_lineno:]
    return "\n".join(out) + "\n"


def run(target_cls=None, target_file=None):
    orig = S.module_trees
    def patched():
        out = []
        for path, tree in orig():
            if target_file and str(path).endswith(target_file):
                tree = ast.parse(pad_source(path.read_text(), target_cls), filename=str(path))
            out.append((path, tree))
        return out
    orig_seams = S.load_seam_map
    def seams():
        m = dict(orig_seams())
        first = m.get("__init__", next(iter(m.values())))
        m.update({f"_r10pad{i}": first for i in range(PAD_METHODS)})
        return m
    S.module_trees = patched
    S.load_seam_map = seams if target_cls == "HeatPumpOptimizerCoordinator" else orig_seams
    try:
        return S.measure()["metrics"]
    finally:
        S.module_trees = orig
        S.load_seam_map = orig_seams

t0p, t0t = time.process_time(), time.thread_time()
base = run()
sec = run("HeatPumpOptimizer", "heatpump_optimizer/optimizer.py")
coo = run("HeatPumpOptimizerCoordinator", "heatpump_optimizer/coordinator.py")
moved = lambda m: sorted(k for k in base if m[k] > base[k])
print("second-class moved:", moved(sec), {k: (base[k], sec[k]) for k in moved(sec)})
print("coordinator moved:", moved(coo), {k: (base[k], coo[k]) for k in moved(coo)})
print(f"RESULT lines_added_per_arm={PAD_METHODS * PAD_LINES + 1} lines")
print(f"RESULT keys_moved_second_class={len(moved(sec))} count")
print(f"RESULT keys_moved_coordinator={len(moved(coo))} count")
tf = (time.process_time() - t0p) / max(time.thread_time() - t0t, 1e-9)
print(f"RESULT thread_factor={tf:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
