#!/usr/bin/env python3
"""D1-s3 M5: broad handlers that swallow any exception with no record at any level.

Metric (one line): of the `except Exception`/bare handlers whose body neither logs nor re-raises
(--seams lists them all) and which the lifecycle workload reaches, the number whose try body,
forced to raise on every pass (excepts_inject.py's persistent fault), added zero log records at
any level (DEBUG included) over the fault-free control run.
Count key: the integration's own log records.

Command:
    PYTHONPATH=tests/hastub /Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/silent_broad.py [--seams] [--perturb]
  --seams    print the static seam list (every such handler in the package) and exit
  --perturb  one production line, in memory at import: _record_accuracy's COP-residual handler
             emits a DEBUG record (`sample.cop_residual = _LOGGER.debug(...)`, still None)
Expected on baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT silent_broad_no_record=7
of RESULT silent_broad_reached=11 (exact); --perturb: 6. Machine: orchestrator Mac (Apple M1), shared box; no timing RESULT.
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
sys.path.insert(0, HERE)
import d1s3hook as hook  # noqa: E402

EDIT = ("custom_components/heatpump_optimizer/coordinator.py::"
        "                    sample.cop_residual = None\n                # D7-03::"
        "                    sample.cop_residual = _LOGGER.debug(\"COP residual tag skipped\")\n"
        "                # D7-03")


def seams():
    return [r for r in hook.handlers()
            if r["kind"] == "broad" and not r["static_logs"] and not r["reraises"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seams", action="store_true")
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    rows = seams()
    if a.seams:
        for r in rows:
            print(f"{r['id']} {r['func']} | {r['body'][:80]!r}")
        print(f"RESULT silent_broad_seams={len(rows)} handlers")
        return
    reach = json.load(open(os.path.join(HERE, "out", "reach.json")))["reach"]
    ids = [r["id"] for r in rows if reach["proc"].get(r["id"]) or reach["inproc"].get(r["id"])]
    out = tempfile.mktemp(prefix="d1s3_silent_", suffix=".jsonl", dir=os.environ.get("TMPDIR"))
    cmd = [sys.executable, os.path.join(HERE, "excepts_inject.py"), "--out", out, "--only", *ids]
    if a.perturb:
        cmd += ["--edit", EDIT]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    silent = 0
    for line in open(out):
        r = json.loads(line)
        armed = [p for p in r["phases"] if p["phase"] != "refreshB2"]
        added = sum(p["added"] for p in armed) + sum(p["mark_logged"] for p in armed)
        print(f"  {r['id']} fired={r['fired']} added_records={added}")
        if r["fired"] and added == 0:
            silent += 1
    print(f"RESULT silent_broad_reached={len(ids)} handlers")
    print(f"RESULT silent_broad_no_record={silent} handlers")
    print("RESULT thread_factor=1.0 (no timing RESULT)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
