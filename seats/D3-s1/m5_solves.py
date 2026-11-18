#!/usr/bin/env python3
"""D3-s1 M5: checks per solve, per gate script whose closure reaches the cells.

Metric (one line): solves = calls of
`custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize`
summed over every Python process the script starts (a sitecustomize hook
wraps the method when the module finishes executing, counts persist per pid);
checks = the script's own closing tally (`N of M` / `ALL N ... PASSED`);
ratio = checks / solves. Also `_multi_start_minimize` calls (inner L-BFGS-B
multi-starts) and process CPU seconds of the run (provisional).

Instrumented symbol: optimizer:HeatPumpOptimizer.optimize (and
optimizer:_multi_start_minimize).
Perturbation: `--double-solve` makes the hook call the original optimize twice
per call (same result returned) -> solves for every script doubles (direction
up) and checks stay flat, so checks_per_solve halves; identity run = null.

Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/m5_solves.py [--scripts a,b] [--double-solve]
Box D3-m5 (C4): for tests/env_drift.py the --capture --all child is also run
directly under the hook (the parent drops it) and its solves added.
Writes only under a mkdtemp root and its own worker tree under $TMPDIR.
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: owner macOS arm64, shared box.
Expected: exact counts (contention-immune); CPU seconds provisional.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import json
import re
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, "tests")
import mutation_table as mt  # noqa: E402

HOOK = r'''
import os, sys, atexit, importlib.abc, importlib.machinery
_OUT = os.environ.get("D3S1_SOLVE_OUT")
_DOUBLE = os.environ.get("D3S1_DOUBLE") == "1"
_C = {"optimize": 0, "multi_start": 0}
def _dump():
    if _OUT:
        with open(os.path.join(_OUT, f"{os.getpid()}.json"), "w") as f:
            import json; json.dump(_C, f)
atexit.register(_dump)
def _patch(mod):
    cls = getattr(mod, "HeatPumpOptimizer", None)
    if cls is not None and not getattr(cls.optimize, "_d3s1", False):
        orig = cls.optimize
        def optimize(self, *a, **k):
            _C["optimize"] += 1
            if _DOUBLE:
                _C["optimize"] += 1
                orig(self, *a, **k)
            return orig(self, *a, **k)
        optimize._d3s1 = True
        cls.optimize = optimize
    ms = getattr(mod, "_multi_start_minimize", None)
    if ms is not None and not getattr(ms, "_d3s1", False):
        def _ms(*a, **k):
            _C["multi_start"] += 1
            return ms(*a, **k)
        _ms._d3s1 = True
        mod._multi_start_minimize = _ms
class _L(importlib.abc.Loader):
    def __init__(self, inner): self.inner = inner
    def create_module(self, spec): return self.inner.create_module(spec)
    def exec_module(self, module):
        self.inner.exec_module(module); _patch(module)
class _F(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if not name.endswith("optimizer") or name.endswith("_optimizer"):
            return None
        for f in sys.meta_path:
            if f is self: continue
            fs = getattr(f, "find_spec", None)
            if fs is None: continue
            spec = fs(name, path, target)
            if spec is not None:
                if spec.origin and spec.origin.endswith(os.path.join("heatpump_optimizer", "optimizer.py")):
                    spec.loader = _L(spec.loader)
                return spec
        return None
sys.meta_path.insert(0, _F())
'''

TALLY = [re.compile(r"(\d+) of (\d+) .*FAILED"),
         re.compile(r"ALL (\d+) .*PASSED"),
         re.compile(r"(\d+)/(\d+) .*(?:passed|ok)", re.I)]


def tally(out: str):
    m = None
    for m in TALLY[0].finditer(out):
        pass
    if m:
        return int(m.group(2))
    for m in TALLY[1].finditer(out):
        pass
    if m:
        return int(m.group(1))
    n = len(re.findall(r"^\s*(?:ok|FAIL)\s", out, re.M))
    return n or None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts")
    ap.add_argument("--double-solve", action="store_true")
    ap.add_argument("--tree", default=str(Path(tempfile.gettempdir()) / "d3s1-workers" / "w5"))
    ap.add_argument("--out", help="append JSON lines here")
    a = ap.parse_args()
    here = Path(__file__).resolve().parent
    if a.scripts:
        scripts = a.scripts.split(",")
    else:
        base = json.loads((here / "state" / "baselines.json").read_text())
        scripts = sorted(base)
    t = Path(a.tree)
    if not (t / ".git").exists():
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(t), "HEAD"],
                       cwd=mt.ROOT, check=True)
    root = Path(tempfile.mkdtemp(prefix="d3s1-solves-"))
    hook = root / "_hook"
    hook.mkdir()
    (hook / "sitecustomize.py").write_text(HOOK)
    for s in scripts:
        out = root / s.replace("/", "_")
        out.mkdir()
        args, env = mt.drive_spec(s, "HEAD^1")
        env = {**os.environ, **env, "PYTHONPATH": f"{hook}{os.pathsep}tests/hastub",
               "D3S1_SOLVE_OUT": str(out), "D3S1_DOUBLE": "1" if a.double_solve else "0"}
        r0 = resource.getrusage(resource.RUSAGE_CHILDREN)
        t0 = time.monotonic()
        p = subprocess.run([sys.executable, s, *args], cwd=t, env=env,
                           capture_output=True, text=True, timeout=7200)
        wall = time.monotonic() - t0
        r1 = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = (r1.ru_utime + r1.ru_stime) - (r0.ru_utime + r0.ru_stime)
        opt = ms = procs = 0
        for f in out.glob("*.json"):
            d = json.loads(f.read_text())
            opt += d["optimize"]
            ms += d["multi_start"]
            procs += 1
        checks = tally(p.stdout)
        cap_opt = cap_ms = cap_procs = None
        if s == "tests/env_drift.py":
            # Box D3-m5 (C4): env_drift.py starts its --capture child with
            # PYTHONPATH reset to <tree>/tests/hastub, which drops this hook
            # (D3-s1-01's mechanism), so the parent run counts no solve. Run
            # that child directly under the hook, exactly as the parent
            # launches it (--capture <tree> <out> --all), and count its solves.
            cout = root / "capture"
            cout.mkdir()
            cenv = {**env, "D3S1_SOLVE_OUT": str(cout),
                    "PYTHONPATH": f"{hook}{os.pathsep}{t / 'tests' / 'hastub'}"}
            r2 = resource.getrusage(resource.RUSAGE_CHILDREN)
            subprocess.run([sys.executable, "tests/env_drift.py", "--capture", str(t),
                            str(root / "capture.json"), "--all"], cwd=t, env=cenv,
                           capture_output=True, text=True, timeout=7200)
            r3 = resource.getrusage(resource.RUSAGE_CHILDREN)
            cap_opt = cap_ms = cap_procs = 0
            for f in cout.glob("*.json"):
                d = json.loads(f.read_text())
                cap_opt += d["optimize"]
                cap_ms += d["multi_start"]
                cap_procs += 1
            print(f"RESULT env_drift_capture_cpu_s={(r3.ru_utime + r3.ru_stime) - (r2.ru_utime + r2.ru_stime):.1f} s (provisional)")
        if cap_opt is not None:
            row_extra = {"solves_parent_traced": opt, "capture_solves": cap_opt,
                         "capture_multi_starts": cap_ms, "capture_procs": cap_procs}
            opt, ms = opt + cap_opt, ms + cap_ms
        else:
            row_extra = {}
        row = {"script": s, "rc": p.returncode, "checks": checks, "solves": opt, **row_extra,
               "multi_starts": ms, "procs_recorded": procs,
               "cpu_s": round(cpu, 1), "wall_s": round(wall, 1),
               "checks_per_solve": (round(checks / opt, 3) if checks and opt else None)}
        print(json.dumps(row), flush=True)
        if a.out:
            with open(a.out, "a") as f:
                f.write(json.dumps(row) + "\n")
        key = s.rsplit("/", 1)[-1].replace(".py", "")
        print(f"RESULT {key}_solves={opt}")
        print(f"RESULT {key}_checks={checks}")
        print(f"RESULT {key}_cpu_s={cpu:.1f} s (provisional)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
