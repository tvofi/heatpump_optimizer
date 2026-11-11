#!/usr/bin/env python3
"""D10.M3 test-coverage: per-module statement coverage of the integration.

Metric: statement coverage (coverage.py, statement mode, raw percent) of every
module of custom_components/heatpump_optimizer, measured by running each
default-gate test script (the "fast" stage the CI coverage job runs, list
DERIVED from tests/run.sh exactly as tools/audit/w5-partition/coverage_tree.sh
derives it) under coverage, one process per script, then combining. Also
reports modules <= 95.0 (the rule says "above 95%"), and branch coverage as a
second, separately named number.

Command (from the export root):
  PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D10/s2/coverage_modules.py [--stage fast|all] [--drop script,...]
Perturbation: --drop config_flow_steps  -> config_flow.py percent must go DOWN.
Expected: see REPORT.md (package percent +-0.3, per-module +-0.5: the timing
checks inside features.py can take different branches under load).
Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: 4-CPU Linux cloud container, Python 3.14.0rc2.
Instrumented symbol: every module of custom_components/heatpump_optimizer (coverage.py source=).
Writes only under a mkdtemp root.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, json, re, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path.cwd()
assert (ROOT / "custom_components/heatpump_optimizer/manifest.json").exists(), "run from the export root"
ap = argparse.ArgumentParser()
ap.add_argument("--stage", default="fast", choices=("fast", "all"))
ap.add_argument("--drop", default="")
ap.add_argument("--branch", action="store_true", help="also record branch coverage")
args = ap.parse_args()

work = Path(tempfile.mkdtemp(prefix="d10s2cov-"))
pylib = work / "pylib"
try:
    import coverage  # noqa: F401
    extra = str(Path(coverage.__file__).resolve().parent.parent)
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--target", str(pylib), "coverage"], check=True)
    extra = str(pylib)

run_sh = (ROOT / "tests/run.sh").read_text()
derived = []
for m in re.finditer(r'run "\$PYTHON" tests/([a-z_]+)\.py', run_sh):
    if m.group(1) not in derived:
        derived.append(m.group(1))
excl = {"env_drift", "rolling"}
if args.stage == "fast":
    excl |= {"stress", "validate", "edge", "backtest", "optimality"}
drop = {d for d in args.drop.split(",") if d}
scripts = [s for s in derived if s not in excl and s not in drop]

site = work / "site"; site.mkdir()
(site / "sitecustomize.py").write_text("try:\n    import coverage\nexcept ImportError:\n    pass\nelse:\n    coverage.process_startup()\n")
(work / "data").mkdir()
rc = work / "coveragerc"
rc.write_text(f"[run]\nparallel = True\nrelative_files = True\nbranch = {bool(args.branch)}\n"
              f"data_file = {work}/data/.coverage\nsource = {ROOT}/custom_components/heatpump_optimizer\n")
env = dict(os.environ)
env["COVERAGE_PROCESS_START"] = str(rc)
env["PYTHONPATH"] = os.pathsep.join(p for p in (str(site), extra, str(ROOT / "tests/hastub")) if p)
env["HPO_PLANDATA"] = str(work / "plandata.json")
env["TMPDIR"] = str(work)
statuses = {}
for s in scripts:
    t = time.time()
    e = dict(env)
    if s == "golden":
        e["GOLDEN_MODE"] = "strict"
    with open(work / f"{s}.log", "w") as log:
        p = subprocess.run([sys.executable, f"tests/{s}.py"], cwd=ROOT, env=e, stdout=log, stderr=subprocess.STDOUT)
    statuses[s] = p.returncode
    print(f"ran tests/{s}.py exit={p.returncode} wall={time.time()-t:.0f}s", flush=True)

cenv = dict(env); cenv.pop("COVERAGE_PROCESS_START")
subprocess.run([sys.executable, "-m", "coverage", "combine", f"--rcfile={rc}", "--append", "--keep"], cwd=ROOT, env=cenv, capture_output=True)
subprocess.run([sys.executable, "-m", "coverage", "json", f"--rcfile={rc}", "-o", str(work / "coverage.json")], cwd=ROOT, env=cenv, capture_output=True)
data = json.loads((work / "coverage.json").read_text())
mods = {}
for fn, v in data["files"].items():
    s = v["summary"]
    mods[Path(fn).name] = (s["num_statements"], s["missing_lines"], 100.0 * s["covered_lines"] / s["num_statements"] if s["num_statements"] else 100.0,
                           (100.0 * (s.get("covered_branches", 0)) / s["num_branches"]) if s.get("num_branches") else None)
tot = data["totals"]
print("module\tstatements\tmissed\tstmt_percent\tbranch_percent")
for n, (st, mi, pc, bp) in sorted(mods.items(), key=lambda kv: kv[1][2]):
    print(f"{n}\t{st}\t{mi}\t{pc:.2f}\t{'' if bp is None else f'{bp:.2f}'}")
pkg = 100.0 * tot["covered_lines"] / tot["num_statements"]
below = [n for n, v in mods.items() if v[2] <= 95.0]
print(f"RESULT scripts_run={len(scripts)} count")
print(f"RESULT scripts_nonzero_exit={sum(1 for v in statuses.values() if v)} count  ({','.join(k for k,v in statuses.items() if v)})")
print(f"RESULT package_stmt_percent={pkg:.2f} percent")
print(f"RESULT min_module_stmt_percent={min(v[2] for v in mods.values()):.2f} percent ({min(mods, key=lambda k: mods[k][2])})")
print(f"RESULT modules_not_above_95={len(below)} count ({','.join(sorted(below))})")
print(f"RESULT config_flow_stmt_percent={mods.get('config_flow.py', (0,0,0.0))[2]:.2f} percent")
if args.branch:
    bps = {n: v[3] for n, v in mods.items() if v[3] is not None}
    print(f"RESULT package_branch_percent={100.0*tot['covered_branches']/tot['num_branches']:.2f} percent")
    bb = sorted(n for n, b in bps.items() if b <= 95.0)
    print(f"RESULT modules_branch_not_above_95={len(bb)} count ({','.join(bb)})")
print(f"RESULT thread_factor={time.process_time()/max(time.thread_time(),1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open('/proc/vmstat') if l.startswith('pswpin')][0].split()[1]
except Exception:
    sw = "na"
print(f"RESULT swapins={sw}")
print(f"workdir {work}")
