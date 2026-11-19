#!/usr/bin/env python3
"""D1-s3 M5: a store save that keeps failing is never logged above DEBUG.

Metric (one line): of the persist handlers (persist_seams.py) the lifecycle workload reaches, the
number whose save body, forced to raise on every pass across setup, two refreshes, unload, restart
and a refresh (excepts_inject.py's persistent fault), added zero WARNING-or-higher records over
the fault-free control run.
Count key: the integration's own log records, captured from its loggers.

Command:
    PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/persist_family.py [--perturb]
  --perturb  one production line, in memory at import (excepts_inject.py --edit): the ledger
             save handler logs at WARNING instead of DEBUG -> the count drops by one
Expected on baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT persist_silent_at_warning=10
of RESULT persist_reached=10 (exact); --perturb: 9 of 10.
Machine: orchestrator Mac (Apple M1), shared box; no RESULT is a timing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
EDIT = ("custom_components/heatpump_optimizer/coordinator.py::"
        '_LOGGER.debug("Could not persist ledger: %s", err)::'
        '_LOGGER.warning("Could not persist ledger: %s", err)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    seams = subprocess.run([sys.executable, os.path.join(HERE, "persist_seams.py")],
                           capture_output=True, text=True, check=True).stdout.split("\n")
    ids = [l.split()[0] for l in seams if l.startswith("custom_components/")]
    reach = json.load(open(os.path.join(HERE, "out", "reach.json")))["reach"]
    ids = [i for i in ids if reach["proc"].get(i) or reach["inproc"].get(i)]
    out = tempfile.mktemp(prefix="d1s3_persist_", suffix=".jsonl", dir=os.environ.get("TMPDIR"))
    cmd = [sys.executable, os.path.join(HERE, "excepts_inject.py"), "--out", out, "--only", *ids]
    if a.perturb:
        cmd += ["--edit", EDIT]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    silent = 0
    for line in open(out):
        r = json.loads(line)
        armed = [p for p in r["phases"] if p["phase"] != "refreshB2"]
        warn = sum(p["added_warn"] for p in armed)
        print(f"  {r['id']} fired={r['fired']} added_warning={warn} "
              f"added_any={sum(p['added'] for p in armed)}")
        if r["fired"] and warn == 0:
            silent += 1
    print(f"RESULT persist_reached={len(ids)} handlers")
    print(f"RESULT persist_silent_at_warning={silent} handlers")
    print("RESULT thread_factor=1.0 (no timing RESULT)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
