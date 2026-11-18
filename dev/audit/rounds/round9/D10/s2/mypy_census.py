#!/usr/bin/env python3
"""D10.M3 strict-typing: mypy --strict over the integration, counted by error code.

Metric: number of `error:` lines mypy --strict reports under
custom_components/heatpump_optimizer, by error code, in two arms:
  stub  -- the brief's literal instruction: tests/hastub on MYPYPATH
  real  -- the pinned toolchain of tests/typing_budgets.json (homeassistant-stubs
           + homeassistant installed --no-deps into a temp target, scipy-stubs),
           which is what tests/typing_ruler.py measures in CI.
Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s2/mypy_census.py [--arm stub|real|both] [--target DIR]
--target reuses an existing install dir (must hold homeassistant, homeassistant-stubs, scipy-stubs).
Expected at baseline: stub arm package_errors=358 (+-0, mypy 2.3.1), real arm package_errors=0.
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: 4-CPU Linux cloud container, Python 3.14.0rc2
(the real arm installs with --ignore-requires-python: homeassistant 2026.9.3 declares >=3.14.2).
Instrumented symbol: every module of custom_components/heatpump_optimizer (mypy's input).
Perturbation (real arm): --inject writes one mis-annotated function into a temp copy of the package -> package_errors up by >=1.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, collections, json, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--arm", default="both", choices=("stub", "real", "both"))
ap.add_argument("--target", default="")
ap.add_argument("--inject", action="store_true")
args = ap.parse_args()
ROOT = Path.cwd(); PKG = "custom_components/heatpump_optimizer"
work = Path(tempfile.mkdtemp(prefix="d10s2mypy-"))
budget = json.loads((ROOT / "tests/typing_budgets.json").read_text())["ruler"]

def ensure(mod, spec, dest):
    try:
        m = __import__(mod); return str(Path(m.__file__).resolve().parent.parent)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--target", str(dest), spec], check=True)
        return str(dest)

extra = [p for p in (ensure("mypy", f"mypy=={budget['mypy']}", work / "tool"),) if p]
# the package under test: the tree itself, or a temp copy carrying the injected error
pkg_root = ROOT
if args.inject:
    pkg_root = work / "copy"
    shutil.copytree(ROOT / PKG, pkg_root / PKG)
    (pkg_root / PKG / "zz_injected.py").write_text("def f(x):\n    return x\n\nY: int = 'str'\n")

def run(arm):
    env = {k: v for k, v in os.environ.items() if k not in ("MYPYPATH", "PYTHONPATH")}
    path = list(extra)
    if arm == "stub":
        env["MYPYPATH"] = str(ROOT / "tests/hastub")
    else:
        tgt = Path(args.target.split(os.pathsep)[0]) if args.target else work / "ha"
        if not args.target:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--ignore-requires-python", "--no-deps",
                            "--target", str(tgt), f"homeassistant-stubs=={budget['homeassistant_stubs']}",
                            f"homeassistant=={budget['homeassistant_stubs']}", "scipy-stubs"], check=True)
        path.extend(args.target.split(os.pathsep) if args.target else [str(tgt)])
    env["PYTHONPATH"] = os.pathsep.join(path)
    p = subprocess.run([sys.executable, "-m", "mypy", "--strict", "--warn-unused-ignores", "--show-error-codes",
                        "--no-error-summary", "--no-incremental", "--cache-dir", str(work / f"cache-{arm}"),
                        "--python-version", budget["python_version_flag"], PKG],
                       cwd=pkg_root, env=env, capture_output=True, text=True)
    lines = (p.stdout + p.stderr).splitlines()
    errs = [l for l in lines if ": error:" in l]
    pkg = [l for l in errs if l.startswith(PKG)]
    codes = collections.Counter((re.search(r"\[([a-z-]+)\]$", l) or [None, "no-code"])[1] for l in pkg)
    print(f"arm={arm} rc={p.returncode} by_code={dict(codes.most_common())}")
    if p.returncode not in (0, 1) or (p.returncode == 1 and not errs):
        print("\n".join(lines[:20])); raise SystemExit(f"mypy did not run cleanly in arm {arm}")
    print(f"RESULT {arm}.package_errors={len(pkg)} count")
    print(f"RESULT {arm}.outside_package_errors={len(errs) - len(pkg)} count")
    print(f"RESULT {arm}.files_with_errors={len({l.split(':')[0] for l in pkg})} count")

for arm in (("stub", "real") if args.arm == "both" else (args.arm,)):
    run(arm)
print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={[l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]}")
