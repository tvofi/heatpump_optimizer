#!/usr/bin/env python3
"""D3.M5: solves per script against assertions per script, for every recorded
gate script in seat D3-s3's cells (enumerator: enumerate_m5.py).

Metric (one line): per script, S = calls of
custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize in
the script's process tree (every process that inherits PYTHONPATH), A = the
checks the green run reports (its `ALL N ... PASSED` count, else its `ok` lines),
and A/S = assertions per solve. Count key: the optimize() call the production
seam takes, never a script-side attribute. Also logs wall + child CPU
(provisional) for comparison with tests/closures.json `recorded.seconds`.

Hook: a sitecustomize on a private PYTHONPATH head wraps
HeatPumpOptimizer.optimize after the optimizer module executes (meta-path
loader wrapper); every process appends `pid argv0 count` at exit.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/solves.py [script ...] \
          [--out dev/audit/rounds/round11/D3/s3/solves.json]
Perturbation: --perturb-double makes the wrapper call the original optimize
twice per call; every script with S>0 must report S doubled (direction up),
scripts with S=0 stay 0 (null control).
Expected: S and A exact per script (deterministic suite); wall/CPU provisional.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: box B3, 4 vCPU.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import re
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
TARGET = "custom_components.heatpump_optimizer.optimizer"

SITE = r'''
import os, sys, atexit, importlib.abc, importlib.machinery
_LOG = os.environ["D3S3_SOLVE_LOG"]
_DOUBLE = os.environ.get("D3S3_DOUBLE") == "1"
_N = [0]
def _patch(mod):
    cls = getattr(mod, "HeatPumpOptimizer", None)
    if cls is None or getattr(cls.optimize, "_d3s3", False):
        return
    raw = cls.optimize
    def orig(self, *a, **k):
        _N[0] += 1          # counts executions of the production solve
        return raw(self, *a, **k)
    def optimize(self, *a, **k):
        if _DOUBLE:
            orig(self, *a, **k)
        return orig(self, *a, **k)
    optimize._d3s3 = True
    cls.optimize = optimize
class _Loader(importlib.abc.Loader):
    def __init__(self, inner): self.inner = inner
    def create_module(self, spec): return self.inner.create_module(spec)
    def exec_module(self, module):
        self.inner.exec_module(module); _patch(module)
class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if not (name == "%(t)s" or name.endswith(".optimizer") or name == "optimizer"):
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec is None or spec.loader is None or not str(spec.origin).replace(os.sep, "/").endswith("heatpump_optimizer/optimizer.py"):
            return None
        spec.loader = _Loader(spec.loader)
        return spec
sys.meta_path.insert(0, _Finder())
def _dump():
    with open(_LOG, "a") as f:
        f.write("%%d\t%%s\t%%d\n" %% (os.getpid(), (sys.argv or ["?"])[0], _N[0]))
atexit.register(_dump)
_ox = os._exit
def _exit(code):
    _dump(); _ox(code)
os._exit = _exit
''' % {"t": TARGET}

ALL_RE = re.compile(r"^ALL (\d+) .*PASSED", re.M | re.I)
OK_RE = re.compile(r"^\s*ok\b", re.M)
OKEND_RE = re.compile(r"\bOK\s*$", re.M)


def run(script: str, hookdir: Path, tmp: Path, double: bool) -> dict:
    argv = script.split()
    log = tmp / (Path(argv[0]).stem + (".dbl" if double else "") + ".log")
    log.unlink(missing_ok=True)
    env = {**os.environ, "PYTHONPATH": f"{hookdir}:tests/hastub",
           "D3S3_SOLVE_LOG": str(log), "D3S3_DOUBLE": "1" if double else "0",
           "HPO_PLANDATA": str(tmp / "plandata")}
    exe = "node" if argv[0].endswith(".mjs") else sys.executable
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t = time.monotonic()
    p = subprocess.run([exe, *argv], cwd=ROOT, env=env, capture_output=True,
                       text=True, timeout=7200)
    wall = time.monotonic() - t
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    solves = 0
    procs = 0
    if log.exists():
        for ln in log.read_text().splitlines():
            procs += 1
            solves += int(ln.split("\t")[2])
    m = ALL_RE.findall(p.stdout)
    oks = len(OK_RE.findall(p.stdout))
    okend = len(OKEND_RE.findall(p.stdout))
    asserts = int(m[-1]) if m else (oks or okend)
    return {"script": script, "rc": p.returncode, "solves": solves,
            "hooked_processes": procs, "asserts": asserts,
            "asserts_source": "ALL-N" if m else ("ok-lines" if oks else "OK-suffix-lines"),
            "asserts_per_solve": round(asserts / solves, 3) if solves else None,
            "wall_s": round(wall, 1), "cpu_s": round(cpu, 1),
            "tail": p.stdout.strip().splitlines()[-1:] if p.stdout else []}


def main() -> int:
    args = [a for a in sys.argv[1:]]
    out = None
    if "--out" in args:
        i = args.index("--out"); out = args[i + 1]; del args[i:i + 2]
    double = "--perturb-double" in args
    args = [a for a in args if a != "--perturb-double"]
    scripts = args
    tmp = Path(tempfile.mkdtemp(prefix="d3s3-solves-"))
    hookdir = tmp / "hook"; hookdir.mkdir()
    (hookdir / "sitecustomize.py").write_text(SITE)
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()
    rows = []
    for s in scripts:
        r = run(s, hookdir, tmp, double)
        rows.append(r)
        print(f"RESULT {s}:solves={r['solves']} count")
        print(f"RESULT {s}:asserts={r['asserts']} count ({r['asserts_source']}, rc={r['rc']})")
        print(f"RESULT {s}:asserts_per_solve={r['asserts_per_solve']} ratio")
        print(f"RESULT {s}:wall={r['wall_s']} s (provisional)")
        print(f"RESULT {s}:cpu={r['cpu_s']} s (provisional)", flush=True)
        if out:
            Path(out).write_text(json.dumps(rows, indent=1))
    pc, tc = time.process_time() - t_cpu0, time.thread_time() - t_thr0
    print(f"RESULT thread_factor={pc / tc if tc else 0:.3f}")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    try:
        sw = sum(int(ln.split()[1]) for ln in open("/proc/vmstat")
                 if ln.startswith("pswpin"))
    except OSError:
        sw = -1
    print(f"RESULT swapins={sw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
