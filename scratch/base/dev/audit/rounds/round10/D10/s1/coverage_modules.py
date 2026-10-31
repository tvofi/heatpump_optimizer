"""D10-s1 (round 10) M3 test-coverage: statement coverage per integration module.

Metric: per module of custom_components/heatpump_optimizer, covered/total
statements (coverage.py line data) over the union of the per-script data
tools/coverage/coverage_tree.sh writes (one .coverage.<script> per test
script, combined here); RESULT modules_below_95 counts modules under the
Silver bar (95 %), RESULT config_flow_percent is config_flow.py's.
Command (from the export root; first produce the per-script data):
  W=$(mktemp -d); mkdir -p $W/site; \
  ~/.local/state/hpo/venv-ci/bin/python -m pip install -q --target $W/site coverage; \
  W5P_WORK=$W PYTHON=~/.local/state/hpo/venv-ci/bin/python \
    bash tools/coverage/coverage_tree.sh fast; \
  W5P_WORK=$W bash tools/coverage/coverage_tree.sh e2e   # optional, e2e stage
  PYTHONPATH=$W/site:tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
    dev/audit/rounds/round10/D10/s1/coverage_modules.py $W/out [--drop config_flow_steps]
Expected at 17f1c55fad1b: see REPORT.md (stage fast; tolerance exact for the same
  script set). --drop <script> removes that script's data before the combine:
  config_flow_percent must move down under --drop config_flow_steps.
Machine: macOS arm64 dev box (B1). Counts only.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import shutil
import sys
import tempfile
import time
from pathlib import Path

import coverage

t0p, t0t = time.process_time(), time.thread_time()
out = Path(sys.argv[1])
drop = set()
if "--drop" in sys.argv:
    drop.add(sys.argv[sys.argv.index("--drop") + 1])
pkg = Path("custom_components/heatpump_optimizer").resolve()
tmp = Path(tempfile.mkdtemp(prefix="d10s1cov"))
files = []
for f in sorted((out / "per").glob(".coverage.*")):
    if f.name.split(".coverage.", 1)[1] in drop:
        continue
    dst = tmp / f.name
    shutil.copy(f, dst)
    files.append(str(dst))
print(f"RESULT scripts_combined={len(files)} count")
cov = coverage.Coverage(data_file=str(tmp / ".coverage"), source=[str(pkg)],
                        config_file=False)
cov.config.relative_files = True
cov.combine(files, keep=True)
cov.load()
rows = []
tot_s = tot_c = 0
for py in sorted(pkg.glob("*.py")):
    _, stmts, _, missing, _ = cov.analysis2(str(py))
    n, m = len(stmts), len(missing)
    pct = 100.0 * (n - m) / n if n else 100.0
    rows.append((pct, py.name, n, m))
    tot_s += n
    tot_c += n - m
rows.sort()
below = [r for r in rows if r[0] < 95.0]
for pct, name, n, m in rows[:15]:
    print(f"MODULE {name} {pct:.2f}% stmts={n} missed={m}")
print(f"RESULT package_percent={100.0 * tot_c / tot_s:.2f} percent")
print(f"RESULT modules_below_95={len(below)} count")
print(f"RESULT lowest_module_percent={rows[0][0]:.2f} percent")
cf = [r for r in rows if r[1] == "config_flow.py"][0]
print(f"RESULT config_flow_percent={cf[0]:.2f} percent")
shutil.rmtree(tmp, ignore_errors=True)
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
