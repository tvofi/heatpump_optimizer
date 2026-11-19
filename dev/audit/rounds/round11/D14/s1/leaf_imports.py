"""D14-s1 detector for class N-leaf-imports-solver: a leaf module whose import
loads the solver (heatpump_optimizer.optimizer) or scipy.

Metric: count of package modules that (i) are not the solver side -- not
optimizer.py, not a module that itself imports scipy (the solver kernels), not
coordinator.py and not a module that reaches the optimizer only through
coordinator.py (HA platforms that type their coordinator) -- and (ii) whose
import in a fresh interpreter puts heatpump_optimizer.optimizer or scipy in
sys.modules. Key = sys.modules after the real import, never the import text.

Command:   PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/leaf_imports.py [--tree DIR] [--perturb]
Expected:  at 92d38ecb RESULT leaf_seams=0 (exact) over 105 modules; at an export of
           234087a510^1 (pre-#2371) leaf_seams>=4 (store, silent_mode, quiet_windows, legionella).
Baseline:  92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (x86_64, 4 vCPU).
Hooked:    the real import of every custom_components.heatpump_optimizer.<module>;
           sys.modules after it.
Perturbation (--perturb): in the child, a meta-path hook makes the import of
           heatpump_optimizer.store also import heatpump_optimizer.optimizer (a one-line
           misplaced `from .optimizer import ...` in store.py) -> leaf_seams 0 -> 1 (up).
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import ast
import json
import subprocess
import sys
import time

argv = sys.argv[1:]
TREE = os.path.abspath(argv[argv.index("--tree") + 1]) if "--tree" in argv else os.getcwd()
PERTURB = "--perturb" in argv
PKG = os.path.join(TREE, "custom_components", "heatpump_optimizer")

CHILD = r"""
import sys, json, importlib, importlib.abc
mod, perturb = sys.argv[1], sys.argv[2] == "1"
if perturb:
    class Hook(importlib.abc.MetaPathFinder):
        def find_spec(self, name, path, target=None):
            if name == "custom_components.heatpump_optimizer.store" and not getattr(self, "busy", False):
                self.busy = True
                importlib.import_module("custom_components.heatpump_optimizer.optimizer")
            return None
    sys.meta_path.insert(0, Hook())
importlib.import_module("custom_components.heatpump_optimizer." + mod)
print(json.dumps({"optimizer": "custom_components.heatpump_optimizer.optimizer" in sys.modules,
                  "scipy": "scipy" in sys.modules,
                  "coordinator": "custom_components.heatpump_optimizer.coordinator" in sys.modules}))
"""


def imports_scipy_directly(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "scipy" for a in n.names):
            return True
        if isinstance(n, ast.ImportFrom) and n.level == 0 and (n.module or "").split(".")[0] == "scipy":
            return True
    return False


def main():
    t0 = time.process_time(); th0 = time.thread_time()
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([os.path.join(TREE, "tests", "hastub"), TREE])}
    mods = sorted(f[:-3] for f in os.listdir(PKG) if f.endswith(".py"))
    seams = []; solver_side = []; via_coord = []; clean = 0; errors = []
    for m in mods:
        r = subprocess.run([sys.executable, "-c", CHILD, m, "1" if PERTURB else "0"],
                           capture_output=True, text=True, env=env, cwd=TREE, timeout=300)
        if r.returncode != 0:
            errors.append(m)
            continue
        got = json.loads(r.stdout.strip().splitlines()[-1])
        loads = got["optimizer"] or got["scipy"]
        if not loads:
            clean += 1
        elif m in ("optimizer", "coordinator") or imports_scipy_directly(os.path.join(PKG, m + ".py")):
            solver_side.append(m)
        elif got["coordinator"]:
            via_coord.append(m)
        else:
            seams.append(m)
    for m in seams:
        print("SEAM", f"custom_components/heatpump_optimizer/{m}.py loads", "the solver")
    print("SOLVER_SIDE", " ".join(solver_side))
    print("VIA_COORDINATOR", " ".join(via_coord))
    print(f"RESULT modules={len(mods)} modules")
    print(f"RESULT clean={clean} modules")
    print(f"RESULT solver_side={len(solver_side)} modules")
    print(f"RESULT via_coordinator={len(via_coord)} modules")
    print(f"RESULT import_errors={len(errors)} modules {' '.join(errors)}")
    print(f"RESULT leaf_seams={len(seams)} modules")
    pc = time.process_time() - t0; tc = time.thread_time() - th0
    print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
