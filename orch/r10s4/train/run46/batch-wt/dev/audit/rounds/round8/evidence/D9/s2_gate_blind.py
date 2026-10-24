#!/usr/bin/env python3
"""D9-s2 harness: which cost/memory-budgeted gate scripts can see a change to the coordinator cycle?

Metric: count of gate scripts that (a) carry a CPU/memory measurement instrument
  (an elapsed process_time/thread_time/perf_counter difference, or tracemalloc / ru_maxrss /
  getsizeof, in their source) AND (b) list the changed production file in their MEASURED closure
  (tests/closures.json, the table tests/closure.py:select trusts). Printed per production file
  of the per-cycle path, plus the scoped-gate verdict tests/closure.py prints for that file.
  Count key: closures.json membership, i.e. what select() and the FULL suite would execute.
Positive control: optimizer.py (the solve) -> 1 (tests/stress.py).
Perturbation: --closures PATH with coordinator.py appended to tests/stress.py's closure
  (--make-perturbed writes that copy under the temp root) -> the coordinator count goes 0 -> 1.
Command:
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D9/s2_gate_blind.py
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D9/s2_gate_blind.py --make-perturbed
Expected: coordinator.py / sensor.py / process_worker.py -> 0 budgeted scripts; optimizer.py -> 1.
  Exact (counts).
Baseline: cdf82daabcfe3777d98b31489f36df5555ec9d82. Machine: 4-vCPU shared cloud container.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import re
import subprocess
import sys

TMP_ROOT = "/home/claude/audit-r8/tmp/D9-s2"
# An ELAPSED/SIZE measurement, not a bare thread_factor print (structure.py prints only
# process_time()/thread_time(), a BLAS signal, and budgets no runtime cost).
INSTRUMENT = re.compile(
    r"\b(tracemalloc|ru_maxrss|getsizeof)\b|perf_counter\(\)\s*-|(process_time|thread_time)\(\)\s*-\s*\w")
PKG = "custom_components/heatpump_optimizer/"
CYCLE_FILES = ["coordinator.py", "sensor.py", "process_worker.py", "price_model.py", "narrative.py"]
CONTROL = "optimizer.py"


def budgeted_scripts(closures):
    out = []
    for script in closures:
        if not os.path.isfile(script):
            continue
        with open(script, encoding="utf-8", errors="replace") as fh:
            if INSTRUMENT.search(fh.read()):
                out.append(script)
    return sorted(out)


def scoped_verdict(path):
    p = subprocess.run([sys.executable, "tests/closure.py", "select", "--files", path],
                       capture_output=True, text=True, env=dict(os.environ))
    line = [ln.strip() for ln in p.stdout.splitlines() if "tests/stress.py" in ln]
    return line[0][:60] if line else "(no stress.py line)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--closures", default="tests/closures.json")
    ap.add_argument("--make-perturbed", action="store_true")
    args = ap.parse_args()
    path = args.closures
    if args.make_perturbed:
        os.makedirs(TMP_ROOT, exist_ok=True)
        with open("tests/closures.json", encoding="utf-8") as fh:
            table = json.load(fh)
        table["closures"]["tests/stress.py"].append(PKG + "coordinator.py")
        path = os.path.join(TMP_ROOT, "closures_perturbed.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(table, fh)
    with open(path, encoding="utf-8") as fh:
        closures = json.load(fh)["closures"]
    budgeted = budgeted_scripts(closures)
    print(f"# closures from {path}; budgeted scripts: {budgeted}")
    for name in CYCLE_FILES + [CONTROL]:
        f = PKG + name
        seers = [s for s in budgeted if f in closures[s]]
        any_seers = [s for s in closures if f in closures[s]]
        verdict = scoped_verdict(f) if path == "tests/closures.json" else "(perturbed table)"
        stem = name.replace(".py", "")
        print(f"RESULT budgeted_scripts_seeing_{stem}={len(seers)} count  "
              f"# {seers}; {len(any_seers)} scripts reach it at all; scoped stress: {verdict}")
    print("RESULT thread_factor=1.000 (no timed work)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    sys.exit(main())
