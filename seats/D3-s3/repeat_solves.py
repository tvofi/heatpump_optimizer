#!/usr/bin/env python3
"""D3.M5: identical solves a gate script repeats inside one process, with the
call site of each repeat and the CPU it costs. Seat D3-s3, round 11.

Metric (one line): per script, R = calls of
custom_components.heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize whose
whole input -- the optimizer's pickled __dict__, the call's arguments AND the
identity of every function/class bound in every loaded heatpump_optimizer
module and in HeatPumpOptimizer's class dict (so a mock.patch.object or a
class-attribute swap between two solves makes them different) -- equals one
the same process already solved; R_cpu = thread CPU spent inside those calls.
Count key: the input the production seam receives at optimize() entry, never a
script-side attribute. A call whose input does not pickle is never a repeat
(R is a lower bound).

Hook: a sitecustomize on a private PYTHONPATH head wraps
HeatPumpOptimizer.optimize after the optimizer module executes (the meta-path
loader of solves.py); every process appends one JSON line at exit.
Command:  PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 \
          dev/audit/rounds/round11/D3/s3/repeat_solves.py SCRIPT [...] \
          [--out dev/audit/rounds/round11/D3/s3/repeat_solves.json]
Perturbation: --perturb-double calls the original optimize twice per call,
the second time on the restored pre-call state; every hashed solve then gains
one repeat (R moves up by the hashed-call count). Null control: a script with
no solve reports R=0 in both arms.
Expected: R exact per script (deterministic suite); R_cpu, wall, CPU are
provisional (shared box). Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692.
Machine: box B3, 4 vCPU linux.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import resource
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()

SITE = r'''
import os, sys, json, time, atexit, copy, importlib.abc, importlib.machinery
_LOG = os.environ["D3S3_REPEAT_LOG"]
_DOUBLE = os.environ.get("D3S3_DOUBLE") == "1"
_SEEN = {}
_REC = {"calls": 0, "hashed": 0, "repeats": [], "cpu_all": 0.0}
def _site():
    f = sys._getframe(2)
    while f is not None:
        fn = f.f_code.co_filename.replace(os.sep, "/")
        if "/tests/" in fn and "/hastub/" not in fn and "sitecustomize" not in fn:
            return "%s:%d:%s" % (fn.split("/tests/", 1)[1], f.f_lineno, f.f_code.co_name)
        f = f.f_back
    return "?"
def _codeprint(cls):
    out = []
    for name, mod in sorted(sys.modules.items()):
        if mod is None or "heatpump_optimizer" not in name:
            continue
        for k, v in sorted(vars(mod).items()):
            if callable(v):
                out.append((name, k, id(v)))
    for k, v in sorted(vars(cls).items()):
        out.append(("cls", k, id(v)))
    return tuple(out)
def _patch(mod):
    cls = getattr(mod, "HeatPumpOptimizer", None)
    if cls is None or getattr(cls.optimize, "_d3s3", False):
        return
    raw = cls.optimize
    def one(self, key, site, a, k):
        _REC["calls"] += 1
        t = time.thread_time()
        try:
            return raw(self, *a, **k)
        finally:
            dt = time.thread_time() - t
            _REC["cpu_all"] += dt
            if key is not None:
                _REC["hashed"] += 1
                if key in _SEEN:
                    _REC["repeats"].append({"site": site, "first": _SEEN[key], "cpu": dt})
                else:
                    _SEEN[key] = site
    def optimize(self, *a, **k):
        import hashlib, pickle
        site = _site()
        try:
            key = hashlib.sha1(pickle.dumps(
                (self.__dict__, a, sorted(k.items()), _codeprint(type(self))),
                protocol=4)).hexdigest()
        except Exception:
            key = None
        if _DOUBLE and key is not None:
            saved = copy.deepcopy(self.__dict__)
            one(self, key, site, a, k)
            self.__dict__.clear(); self.__dict__.update(saved)
        return one(self, key, site, a, k)
    optimize._d3s3 = True
    cls.optimize = optimize
class _Loader(importlib.abc.Loader):
    def __init__(self, inner): self.inner = inner
    def create_module(self, spec): return self.inner.create_module(spec)
    def exec_module(self, module):
        self.inner.exec_module(module); _patch(module)
class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if not (name.endswith(".optimizer") or name == "optimizer"):
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec is None or spec.loader is None or not str(spec.origin).replace(os.sep, "/").endswith("heatpump_optimizer/optimizer.py"):
            return None
        spec.loader = _Loader(spec.loader)
        return spec
sys.meta_path.insert(0, _Finder())
import subprocess as _sp
_HOOK = os.path.dirname(os.path.abspath(__file__))
_pinit = _sp.Popen.__init__
def _init(self, *a, **k):
    env = k.get("env")
    if env is not None and "D3S3_REPEAT_LOG" in env:
        pp = env.get("PYTHONPATH", "")
        if _HOOK not in pp.split(os.pathsep):
            env = dict(env)
            env["PYTHONPATH"] = _HOOK + (os.pathsep + pp if pp else "")
            k["env"] = env
    _pinit(self, *a, **k)
_sp.Popen.__init__ = _init
_done = [False]
def _dump():
    if _done[0] or not _REC["calls"]:
        return
    _done[0] = True
    with open(_LOG, "a") as f:
        f.write(json.dumps({"pid": os.getpid(), "argv0": (sys.argv or ["?"])[0], **_REC}) + "\n")
atexit.register(_dump)
_ox = os._exit
def _exit(code):
    _dump(); _ox(code)
os._exit = _exit
'''


def run(script: str, hookdir: Path, tmp: Path, double: bool) -> dict:
    argv = script.split()
    log = tmp / (Path(argv[0]).stem + (".dbl" if double else "") + ".jsonl")
    log.unlink(missing_ok=True)
    env = {**os.environ, "PYTHONPATH": f"{hookdir}:tests/hastub",
           "D3S3_REPEAT_LOG": str(log), "D3S3_DOUBLE": "1" if double else "0",
           "HPO_PLANDATA": str(tmp / "plandata")}
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t = time.monotonic()
    p = subprocess.run([sys.executable, *argv], cwd=ROOT, env=env,
                       capture_output=True, text=True, timeout=7200)
    wall = time.monotonic() - t
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
    calls = hashed = 0
    cpu_all = 0.0
    reps: list[dict] = []
    if log.exists():
        for ln in log.read_text().splitlines():
            r = json.loads(ln)
            calls += r["calls"]; hashed += r["hashed"]; cpu_all += r["cpu_all"]
            reps.extend(r["repeats"])
    by_site = Counter((r["site"], r["first"]) for r in reps)
    cpu_site: dict = {}
    for r in reps:
        k = (r["site"], r["first"])
        cpu_site[k] = cpu_site.get(k, 0.0) + r["cpu"]
    return {"script": script, "rc": p.returncode, "calls": calls,
            "hashed": hashed, "repeats": len(reps),
            "repeat_cpu_s": round(sum(r["cpu"] for r in reps), 2),
            "solve_cpu_s": round(cpu_all, 2),
            "wall_s": round(wall, 1), "cpu_s": round(cpu, 1),
            "sites": [{"site": s, "first": f, "n": n,
                       "cpu_s": round(cpu_site[(s, f)], 2)}
                      for (s, f), n in by_site.most_common()],
            "tail": p.stdout.strip().splitlines()[-1:] if p.stdout else []}


def main() -> int:
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out"); out = args[i + 1]; del args[i:i + 2]
    double = "--perturb-double" in args
    scripts = [a for a in args if a != "--perturb-double"]
    tmp = Path(tempfile.mkdtemp(prefix="d3s3-repeat-"))
    hookdir = tmp / "hook"; hookdir.mkdir()
    (hookdir / "sitecustomize.py").write_text(SITE)
    t_cpu0, t_thr0 = time.process_time(), time.thread_time()
    rows = []
    for s in scripts:
        r = run(s, hookdir, tmp, double)
        rows.append(r)
        print(f"RESULT {s}:calls={r['calls']} count (rc={r['rc']})")
        print(f"RESULT {s}:hashed={r['hashed']} count")
        print(f"RESULT {s}:repeats={r['repeats']} count")
        print(f"RESULT {s}:repeat_cpu={r['repeat_cpu_s']} s (provisional)")
        print(f"RESULT {s}:solve_cpu={r['solve_cpu_s']} s (provisional)")
        print(f"RESULT {s}:wall={r['wall_s']} s (provisional)")
        print(f"RESULT {s}:cpu={r['cpu_s']} s (provisional)")
        for x in r["sites"][:12]:
            print(f"  repeat {x['n']}x at {x['site']} (first solved at "
                  f"{x['first']}) cpu={x['cpu_s']} s")
        sys.stdout.flush()
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
