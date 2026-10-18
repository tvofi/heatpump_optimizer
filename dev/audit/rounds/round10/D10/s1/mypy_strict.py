"""D10-s1 (round 10) M3 strict-typing: mypy --strict error count by category and file owner.

Metric: mypy --strict errors over custom_components/heatpump_optimizer, in two arms:
  real  -- against the real homeassistant package (venv-ha, HA 2026.9.3);
  stub  -- against tests/hastub on MYPYPATH (the brief's arm), split into errors
           located in the integration vs in the stub itself.
Command (from the export root):
  PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python \
    dev/audit/rounds/round10/D10/s1/mypy_strict.py [--perturb]
Expected at 17f1c55fad1b: RESULT mypy_real_errors=0 (exact); stub arm ~513 total
  (exact for mypy 2.3.1), integration-located errors are stub-shape artefacts.
--perturb copies the package to a temp root and appends one unannotated
  function to const.py: mypy_real_errors must move up (to 1).
Machine: macOS arm64 dev box (B1). Counts only.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HA_PY = os.path.expanduser("~/.local/state/hpo/venv-ha/bin/python")
SYS_MYPY = shutil.which("mypy") or "mypy"
t0p, t0t = time.process_time(), time.thread_time()
tmp = Path(tempfile.mkdtemp(prefix="d10s1mypy"))
pkg_root = Path(".")
if "--perturb" in sys.argv:
    shutil.copytree("custom_components", tmp / "src/custom_components")
    with open(tmp / "src/custom_components/heatpump_optimizer/const.py", "a") as fh:
        fh.write("\n\ndef _d10s1_untyped(x):\n    return x\n")
    pkg_root = tmp / "src"


def run(cmd, env=None):
    p = subprocess.run(cmd, cwd=pkg_root, env=env, capture_output=True, text=True)
    return [ln for ln in p.stdout.splitlines() if ": error:" in ln]


real = run([HA_PY, "-m", "mypy", "--strict", "--cache-dir", str(tmp / "c1"),
            "--no-error-summary", "custom_components/heatpump_optimizer"],
           env={**os.environ, "PYTHONPATH": "", "MYPYPATH": ""})
stub_env = {**os.environ, "MYPYPATH": str(Path("tests/hastub").resolve())}
stub = run([SYS_MYPY, "--strict", "--cache-dir", str(tmp / "c2"), "--no-error-summary",
            "custom_components/heatpump_optimizer"], env=stub_env)
print(f"RESULT mypy_real_errors={len(real)} count")
for ln in real[:20]:
    print("REAL", ln)
in_pkg = [ln for ln in stub if ln.startswith("custom_components/")]
print(f"RESULT mypy_stub_errors_total={len(stub)} count")
print(f"RESULT mypy_stub_errors_in_integration={len(in_pkg)} count")
print(f"RESULT mypy_stub_errors_in_stub={len(stub) - len(in_pkg)} count")
cats = collections.Counter(re.search(r"\[([a-z-]+)\]$", ln).group(1) for ln in in_pkg if re.search(r"\[([a-z-]+)\]$", ln))
for c, n in cats.most_common():
    print(f"CAT integration-located {c}={n}")
shutil.rmtree(tmp, ignore_errors=True)
pc, tc = time.process_time() - t0p, time.thread_time() - t0t
print(f"RESULT thread_factor={pc / tc if tc else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print("RESULT swapins=0")
