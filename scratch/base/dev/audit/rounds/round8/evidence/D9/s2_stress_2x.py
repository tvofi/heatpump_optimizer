#!/usr/bin/env python3
"""D9-s2 harness: does tests/stress.py, as shipped, fail on a synthetic 2x solve regression?

Metric: count of stress.py checks reported FAILED (and the process exit code) when
  heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize is made to run its whole
  solve twice (--inject 2), against the same run with no injection (--inject 1, the
  null control). Count key: the "FAIL"/"FAILED" lines stress.py itself prints, and its rc.
Command (take the lease first; stress.py always needs it):
  python3 tests/gate_lock.py take --label D9-s2
  PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 GOLDEN_REF=HEAD^1 \
    python3 tools/audit/round8/D9/s2_stress_2x.py --inject 2
  python3 tests/gate_lock.py release --label D9-s2
Expected: --inject 2 -> rc != 0 with >= 1 failing check (the gate detects it);
  --inject 1 -> the shipped state on this box (see REPORT-s2.md). Tolerance: exact on
  the pass/fail verdict; ratios printed are provisional (shared box).
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU cloud container
  shared with up to 13 seats (NOT the M1 audit box).
Mechanism: a sitecustomize on a private PYTHONPATH entry wraps optimize() only in
  processes importing THIS tree's optimizer.py; stress.py's baseline capture resets
  PYTHONPATH, so the GOLDEN_REF side is never injected. No production file is edited.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.getcwd()
TMP_ROOT = "/home/claude/audit-r8/tmp/D9-s2"

SITE = r'''
import importlib.abc, importlib.machinery, os, sys
_N = int(os.environ.get("D9S2_INJECT", "1"))
_TREE = os.environ.get("D9S2_TREE", "")
class _Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name != "heatpump_optimizer.optimizer" or _N <= 1:
            return None
        spec = importlib.machinery.PathFinder.find_spec(name, path)
        if spec is None or not (spec.origin or "").startswith(_TREE):
            return spec
        orig = spec.loader.exec_module
        def exec_module(module, _orig=orig):
            _orig(module)
            cls = module.HeatPumpOptimizer
            base = cls.optimize
            def optimize(self, *a, **k):
                for _ in range(_N - 1):
                    base(self, *a, **k)
                return base(self, *a, **k)
            cls.optimize = optimize
            sys.stderr.write("D9S2: optimize() wrapped x%d in %s\n" % (_N, spec.origin))
        spec.loader.exec_module = exec_module
        return spec
sys.meta_path.insert(0, _Finder())
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inject", type=int, default=2)
    ap.add_argument("--log", default=None)
    args = ap.parse_args()
    os.makedirs(TMP_ROOT, exist_ok=True)
    site_dir = tempfile.mkdtemp(prefix="site_", dir=TMP_ROOT)
    with open(os.path.join(site_dir, "sitecustomize.py"), "w") as fh:
        fh.write(SITE)
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(["tests/hastub", site_dir])
    env["D9S2_INJECT"] = str(args.inject)
    env["D9S2_TREE"] = os.path.join(ROOT, "custom_components")
    env["TMPDIR"] = TMP_ROOT
    env.setdefault("GOLDEN_REF", "HEAD^1")
    env.setdefault("HPO_GATE_LOCK_LABEL", "D9-s2")
    log = args.log or os.path.join(TMP_ROOT, f"stress_inject{args.inject}.log")
    t0 = time.time()
    with open(log, "w") as fh:
        rc = subprocess.run([sys.executable, "tests/stress.py"], env=env,
                            stdout=fh, stderr=subprocess.STDOUT).returncode
    text = open(log, encoding="utf-8", errors="replace").read()
    wrapped = text.count("D9S2: optimize() wrapped")
    fails = [ln for ln in text.splitlines() if re.search(r"\bFAIL(ED)?\b", ln)]
    print(f"log: {log}")
    for ln in fails[:40]:
        print("  ", ln.strip()[:220])
    print(f"RESULT inject_factor={args.inject}")
    print(f"RESULT injected_processes={wrapped} count")
    print(f"RESULT stress_rc={rc}")
    print(f"RESULT stress_fail_lines={len(fails)} count")
    print(f"RESULT wall_s={time.time() - t0:.0f} s (provisional)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    # stress.py prints its own thread-factor check; this driver does no timed work.
    print("RESULT thread_factor=1.00 (driver does no timed work; see stress.py's own line)")
    print("RESULT swapins=0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
