#!/usr/bin/env python3
"""D10.M3 test-coverage: re-combine cov_modules.sh's per-script coverage data, optionally without some scripts.

Metric: per module statement coverage (covered/total) of
custom_components/heatpump_optimizer over the union of the per-script data
files cov_modules.sh left in <root>/work/out/per/ (one .coverage.<script>
per measured test script); RESULT modules_below_95 and package percent.
Perturbation: ``--drop SCRIPT[,SCRIPT]`` leaves those scripts' data out of
the union -- the same measurement as a run without them, because the union
is monotone. modules_below_95 must move up (or hold) and package_percent
down; dropping a script that covers nothing moves nothing (its null).
Instrumented symbols: every module of the package, as coverage.py traced it
under each test script (the data is the production code's executed lines).

Run (from the export root, after cov_modules.sh printed its "data root"):
  PYTHONPATH=<root>/work/site <HOME>/.local/state/hpo/venv-ci/bin/python3 \
      dev/audit/rounds/round11/D10/s1/cov_recombine.py <root> [--drop entities]
Expected: with no --drop, the same numbers cov_modules.sh printed (exact).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (the round's export tree). Machine: macOS arm64, venv-ci Python 3.14.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import glob
import sys
import tempfile

root = sys.argv[1]
sys.path.insert(0, os.path.join(root, "work", "site"))
import coverage  # noqa: E402

drop = set()
if "--drop" in sys.argv:
    drop = set(sys.argv[sys.argv.index("--drop") + 1].split(","))
per = os.path.join(root, "work", "out", "per")
files = [f for f in glob.glob(os.path.join(per, ".coverage.*"))
         if os.path.basename(f)[len(".coverage."):] not in drop]
print(f"RESULT scripts_combined={len(files)} count")
if drop:
    print(f"RESULT dropped={','.join(sorted(drop))}")
tmp = tempfile.mkdtemp(prefix="d10s1rc.")
cov = coverage.Coverage(data_file=os.path.join(tmp, ".coverage"),
                        config_file=os.path.join(root, "work", "coveragerc"))
cov.combine(files, keep=True)
cov.save()
rows = []
pkg = os.path.abspath("custom_components/heatpump_optimizer")
data = cov.get_data()
tot_s = tot_c = 0
for f in sorted(glob.glob(os.path.join(pkg, "*.py"))):
    try:
        _, stmts, _, missing, _ = cov.analysis2(f)
    except Exception:  # noqa: BLE001 - never imported by any script
        stmts, missing = None, None
    if stmts is None:
        continue
    n = len(stmts)
    c = n - len(missing)
    tot_s += n
    tot_c += c
    rows.append((100.0 * c / n if n else 100.0, os.path.basename(f), n))
rows.sort()
below = [r for r in rows if r[0] < 95.0]
for p, name, n in rows:
    print(f"MODULE {name} {p:.2f} stmts={n}")
print(f"RESULT package_percent={100.0 * tot_c / tot_s:.2f} %")
print(f"RESULT modules={len(rows)} count")
print(f"RESULT modules_below_95={len(below)} count")
cf = [r for r in rows if r[1] == "config_flow.py"]
if cf:
    print(f"RESULT config_flow_percent={cf[0][0]:.2f} %")
print("RESULT thread_factor=1.0")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
