#!/usr/bin/env python3
"""D3 round-4 verify-0-2 -- my own targeted mutant kill-check driver.

METRIC: per mutant, per named driver script, the exit status and the last
"N of M ... FAILED" count under the mutant, with the clean arm run by the
same driver for comparison. A mutant is KILLED by a script iff the script
fails with the mutant and passes without it.

RUN (from the repository root):
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/verify_mutants_v2.py \
        --mutant M06 --script tests/features.py,tests/entities.py
    PYTHONPATH=tests/hastub python3 tools/audit/round4/D3/verify_mutants_v2.py --clean-arm \
        --script tests/features.py

EXPECTED: one RESULT line per (mutant, script) with rc/failed/mutant-applied;
restoration is asserted by SHA-256 before and after.
BASELINE: pool drawn at 7dd68dd327fe3dbfb09f3bd0fe38910c58877697; this run's
tree is the branch head (production files identical to 7dd68dd for the four
mutants under test, verified by git diff).
MACHINE: 8-core Apple M1, 8 GB, macOS 25.6.0, python 3.11, OpenBLAS.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
POOL = HERE / "pool.json"
PY = sys.executable
_FAILED = re.compile(r"^\s*(\d+) of (\d+) .*FAILED\s*$", re.M)


def _sh(cmd, timeout=2400):
    started = time.monotonic()
    p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                       timeout=timeout)
    return p.returncode, p.stdout + p.stderr, time.monotonic() - started


def apply_mutant(mut: dict) -> tuple[str, str]:
    path = ROOT / mut["file"]
    original = path.read_text()
    lines = original.splitlines(True)
    idx = mut["line"] - 1
    assert lines[idx].rstrip("\n") == mut["old"], f"line mismatch at {mut['line']}"
    nl = "\n" if lines[idx].endswith("\n") else ""
    lines[idx] = mut["new"] + nl
    path.write_text("".join(lines))
    return original, hashlib.sha256(original.encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutant", default="")
    ap.add_argument("--script", required=True)
    ap.add_argument("--clean-arm", action="store_true")
    ap.add_argument("--env-drift-ref", default="")
    args = ap.parse_args()
    sys.stdout.reconfigure(line_buffering=True)

    scripts = args.script.split(",")
    if args.env_drift_ref:
        scripts.append(f"env_drift:{args.env_drift_ref}")

    env = dict(os.environ)
    env["PYTHONPATH"] = "tests/hastub"

    mut = None
    if not args.clean_arm:
        pool = json.loads(POOL.read_text())
        mut = next(m for m in pool["mutants"] if m["id"] == args.mutant)
        original, orig_hash = apply_mutant(mut)
        assert hashlib.sha256((ROOT / mut["file"]).read_text().encode()).hexdigest() != orig_hash

    try:
        for s in scripts:
            if s.startswith("env_drift:"):
                ref = s.split(":", 1)[1]
                cmd = [PY, "tests/env_drift.py", "--all", ref]
            else:
                cmd = [PY, s]
            rc, out, secs = _sh(cmd)
            hits = _FAILED.findall(out)
            failed = int(hits[-1][0]) if hits else 0
            tag = f"{args.mutant or 'CLEAN'} {s}"
            print(f"RESULT {tag} rc={rc} failed={failed} secs={secs:.1f} "
                  f"load1={os.getloadavg()[0]:.2f} mutant_applied={bool(mut)}")
            if rc != 0:
                tail = "\n".join(out.splitlines()[-25:])
                print(f"---- tail of {s} (rc={rc}) ----\n{tail}\n---- end tail ----")
    finally:
        if mut is not None:
            path = ROOT / mut["file"]
            path.write_text(original)
            back = hashlib.sha256(path.read_text().encode()).hexdigest()
            assert back == orig_hash, f"FAILED TO RESTORE {mut['file']}"
            print(f"RESULT restored={mut['id']} sha256_match=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
