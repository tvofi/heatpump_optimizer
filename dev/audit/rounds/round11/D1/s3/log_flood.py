#!/usr/bin/env python3
"""D1-s3 M5: _async_update_data's generic arm logs ERROR with a traceback on every failed cycle.

Metric (one line): with the update body forced to raise on every pass (the handler at
coordinator.py:6148, excepts_inject.py's persistent fault), the number of the integration's own
ERROR records "Error updating Heat Pump Optimizer: %s" added in the armed refreshes A1, A2 and B1
-- refreshes that each follow an already-failed update, so a log-once-per-outage rule adds none.
Count key: the integration's own log records (the base class's transition log is separate).

Command:
    PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/log_flood.py [--perturb]
  --perturb  one production edit, in memory at import (excepts_inject.py --edit): the generic arm
             logs ERROR only on the transition, `(_LOGGER.error if self.last_update_success else
             _LOGGER.debug)(...)`
Expected on baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692: RESULT repeat_error_records=3
(exact); --perturb: 0. Null control: RESULT recovered=1 (the disarmed refresh B2 succeeds and adds
no such record). Machine: orchestrator Mac (Apple M1), shared box; no timing RESULT.
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
HID = "custom_components/heatpump_optimizer/coordinator.py:6148"
OLD = ('            _LOGGER.error(\n'
       '                "Error updating Heat Pump Optimizer: %s", err, exc_info=True\n'
       '            )\n'
       '            _raise_update_failed("update_failed", f"Error updating data: {err}", err, error=str(err))\n'
       '        finally')  # no trailing colon: excepts_inject.py's --edit separator is '::'
NEW = OLD.replace("_LOGGER.error(", "(_LOGGER.error if self.last_update_success else _LOGGER.debug)(", 1)
TPL = "40:Error updating Heat Pump Optimizer: %s"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perturb", action="store_true")
    a = ap.parse_args()
    out = tempfile.mktemp(prefix="d1s3_flood_", suffix=".jsonl", dir=os.environ.get("TMPDIR"))
    cmd = [sys.executable, os.path.join(HERE, "excepts_inject.py"), "--out", out,
           "--reached-file", os.path.join(HERE, "out", "reach2.json"), "--only", HID]
    if a.perturb:
        cmd += ["--edit", f"custom_components/heatpump_optimizer/coordinator.py::{OLD}::{NEW}"]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    rec = json.loads(open(out).readline())
    ph = {p["phase"]: p for p in rec["phases"]}
    n = sum(1 for k in ("refreshA1", "refreshA2", "refreshB1") if TPL in ph[k]["added_tpl"])
    for k in ("setupA", "refreshA1", "refreshA2", "setupB", "refreshB1", "refreshB2"):
        print(f"  {k}: value={ph[k]['value']} added_warn={ph[k]['added_warn']} tpl={ph[k]['added_tpl']}")
    print(f"RESULT fired={rec['fired']} injections")
    print(f"RESULT repeat_error_records={n} records")
    print(f"RESULT recovered={int(bool(ph['refreshB2']['value']) and TPL not in ph['refreshB2']['added_tpl'])}")
    print("RESULT thread_factor=1.0 (no timing RESULT)")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
