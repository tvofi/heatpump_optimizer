#!/usr/bin/env python3
"""D15-s1: the finder wall strips the evidence D15's universe enumerator requires.

Metric (one line): lines `enumerate.py d15-installs` prints in a planted tree
before and after `prepare_baseline.sh --strip <tree> <round>`; a refusal reads -1.
Count key: the enumerator's own stdout line count (exit 0), else -1 (exit 2, refused).

Command (export or checkout root):
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D15/s1/wall_enum.py [--cite-in-tests]
Expected: RESULT d15_installs_before_strip=1, RESULT d15_installs_after_strip=-1 (exact).
Perturbation: --cite-in-tests plants one tests/*.py that cites the evidence path,
    the strip's own keep rule -> d15_installs_after_strip=1 (up).
Null control: the same tree with no earlier round to strip (--round 10, the
    evidence's own round, is not stripped) -> after == before.
Baseline SHA: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Machine: macOS arm64, CI venv;
    no solve, no bundle (the planted tree holds no user data).
Instrumented symbols: tools/audit/enumerate.py:d15, tools/audit/prepare_baseline.sh:strip_earlier_rounds.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path.cwd()
EVIDENCE = "dev/audit/rounds/round10/D15/s1/intake.py"


def count(tree: Path) -> int:
    proc = subprocess.run([sys.executable, "-I", str(ROOT / "tools/audit/enumerate.py"), "d15-installs",
                           "--repo", str(tree)], capture_output=True, text=True)
    return len(proc.stdout.splitlines()) if proc.returncode == 0 else -1


def plant(tree: Path, cite: bool) -> None:
    (tree / "dev/audit/config").mkdir(parents=True)
    (tree / "tests").mkdir()
    bundles = {"bundles": [{"install": "install-1", "date": "2026-10-14", "round": 10,
                            "steps": ["M1"], "evidence": EVIDENCE}]}
    (tree / "dev/audit/config/bundles.json").write_text(json.dumps(bundles))
    ev = tree / EVIDENCE
    ev.parent.mkdir(parents=True)
    ev.write_text("# planted evidence\n")
    # The tree's own closures and tests, so the strip's keep rule reads what it reads in an export.
    shutil.copy(ROOT / "tests/closures.json", tree / "tests/closures.json")
    for g in ("*.py", "*.mjs", "*.sh"):
        for f in (ROOT / "tests").glob(g):
            shutil.copy(f, tree / "tests" / f.name)
    if cite:
        (tree / "tests/zz_cite_d15_evidence.py").write_text(f'# cites {EVIDENCE}\n')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cite-in-tests", action="store_true")
    ap.add_argument("--round", default="11")
    a = ap.parse_args()
    c0, t0 = time.process_time(), time.thread_time()
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp) / "tree"
        tree.mkdir()
        plant(tree, a.cite_in_tests)
        before = count(tree)
        env = dict(os.environ, PYTHON=sys.executable)
        strip = subprocess.run(["bash", str(ROOT / "tools/audit/prepare_baseline.sh"), "--strip", str(tree), a.round],
                               capture_output=True, text=True, env=env)
        after = count(tree)
        print(f"RESULT strip_exit={strip.returncode} unit=code")
        print(f"RESULT evidence_survives={int((tree / EVIDENCE).exists())} unit=bool")
    print(f"RESULT d15_installs_before_strip={before} unit=lines")
    print(f"RESULT d15_installs_after_strip={after} unit=lines")
    print(f"RESULT cite_in_tests={int(a.cite_in_tests)} unit=bool")
    tc = time.thread_time() - t0
    print(f"RESULT thread_factor={((time.process_time() - c0) / tc) if tc > 0 else 1.0:.3f} unit=ratio")
    print(f"RESULT load1={os.getloadavg()[0]:.2f} unit=load")
    print(f"RESULT swapins={_swapins()} unit=count")
    return 0


def _swapins() -> int:
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
        return int(next(l for l in out.splitlines() if l.startswith("Swapins")).split(":")[1].strip(" ."))
    except Exception:  # noqa: BLE001 - Linux has no vm_stat
        try:
            return int(next(l for l in open("/proc/vmstat") if l.startswith("pswpin")).split()[1])
        except Exception:  # noqa: BLE001
            return -1


if __name__ == "__main__":
    sys.exit(main())
