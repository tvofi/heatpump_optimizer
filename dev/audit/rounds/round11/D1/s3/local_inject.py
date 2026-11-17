#!/usr/bin/env python3
"""D1-s3 M5, second arm: one-shot injection into every d1-excepts handler a test script reaches.

Metric (one line): per handler, the first time a test script's own call passes its try body, the
body raises (the handler's own caught type for a narrow handler, RuntimeError for a broad one,
d1s3hook.py) and the harness records whether the handler caught it, whether the handler body
raised out again, and the log records (by level) the integration emitted inside the handler.
Count key: the production handler's own entry/exit (compiled into its body by the hook), so a
fix that changes the handler changes the count; the test script only supplies the call.

Command:
    PYTHONPATH=tests/hastub <HOME>/.local/state/hpo/venv-ci/bin/python3 \
        dev/audit/rounds/round11/D1/s3/local_inject.py --script tests/entities.py --out OUT.jsonl
  The script runs once with every handler armed one-shot; a handler is recorded when it fired.
  (--exclude-from FILE skips handlers already recorded in an earlier script's JSONL.)
Expected: deterministic per handler (exact) on baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692;
machine: orchestrator Mac (darwin arm64), shared box. No RESULT here is a timing.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse
import json
import logging
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d1s3hook as hook  # noqa: E402


class Cap(logging.Handler):
    def __init__(self, sink):
        super().__init__(logging.DEBUG)
        self.sink = sink

    def emit(self, r):
        if os.path.abspath(r.pathname).startswith(hook.PKG_DIR + os.sep):
            self.sink.append((r.levelno, str(r.msg)[:80], hook.MARK in r.getMessage()
                              or bool(r.exc_info and hook.MARK in str(r.exc_info[1]))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--exclude-from", nargs="*", default=[])
    a = ap.parse_args()
    rows = hook.handlers()
    skip = set()
    for f in a.exclude_from:
        if os.path.exists(f):
            skip |= {json.loads(l)["id"] for l in open(f) if l.strip()}
    hook.install(rows)
    hook.MODE = "oneshot"
    hook.ARMED.update(r["id"] for r in rows if r["id"] not in skip)
    hook.RECORDS = []
    cap = Cap(hook.RECORDS)
    root = logging.getLogger()
    root.addHandler(cap)
    root.setLevel(logging.DEBUG)
    for name in ("heatpump_optimizer", "custom_components.heatpump_optimizer"):
        logging.getLogger(name).setLevel(logging.DEBUG)
    sys.argv = [a.script]
    sys.path.insert(0, os.path.dirname(os.path.abspath(a.script)))  # as `python3 tests/x.py` does
    status = "finished"
    try:
        runpy.run_path(a.script, run_name="__main__")
    except SystemExit:
        pass
    except BaseException as err:  # noqa: BLE001 - an escaped injection ends the script
        status = f"aborted: {type(err).__name__}: {str(err)[:120]}"
    hook._close()
    n = 0
    with open(a.out, "a") as fh:
        for r in rows:
            hid = r["id"]
            if not hook.FIRED[hid]:
                continue
            n += 1
            logs = hook.WINDOW_LOGS.get(hid, [])
            fh.write(json.dumps({
                "id": hid, "kind": r["kind"], "func": r["func"], "script": a.script,
                "caught_expr": r["caught"], "entered": hook.ENTERED[hid] > 0,
                "raised_out": hook.RAISED_OUT[hid] > 0, "static_reraises": r["reraises"],
                "logs": len(logs), "logs_warn": sum(1 for l, _, _ in logs if l >= 30),
                "levels": sorted({l for l, _, _ in logs}), "mark_logged": any(m for *_, m in logs),
                "tpl": [m for _, m, _ in logs][:3], "body": r["body"][:160],
            }) + "\n")
    print(f"STATUS {status}")
    print(f"RESULT fired={n} handlers")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.0 (no timing RESULT; not measured)")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
