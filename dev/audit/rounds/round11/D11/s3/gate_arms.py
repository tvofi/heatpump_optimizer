#!/usr/bin/env python3
"""D11-s3 (round 11, D11.M4): drop each required context from the `gate` umbrella and ask its self-test.

Metric: per gate-required name (tools/policy/fixtures/required-contexts.json `gate_required`),
  whether tools/ci/gate.py:self_test returns non-zero when tools/ci/gate.py:REQUIRED is
  rebound in memory with that one name removed from every event class; RESULT
  dropped_refused = arms whose self-test failed, of dropped_arms. Count key: the
  self-test's own return value, never the harness's edit.
Null: REQUIRED unchanged -> self_test() returns 0.
Expected: null 0; 21 of 21 arms refused, exact.
Command: PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s3/gate_arms.py [--perturb]
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B7 (4 vCPU container).
Perturbation (production, one line): `--perturb` rebinds gate.gate_required to return the
  fixture's own list (the equality check then compares the record with itself):
  dropped_refused falls 21 -> 8 (the arms a dedicated pin or a replay case still holds;
  measured 2026-11-16).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import time

ROOT = pathlib.Path.cwd()


def load():
    spec = importlib.util.spec_from_file_location("gate_d11s3", ROOT / "tools/ci/gate.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_self_test(g):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = g.self_test()
        except Exception as e:  # a crash is a refusal too, but say so
            print("CRASH %r" % e)
            rc = 99
    return rc, buf.getvalue()


def main():
    t0p, t0t = time.process_time(), time.thread_time()
    g = load()
    fixture = json.loads((ROOT / "tools/policy/fixtures/required-contexts.json").read_text())
    if "--perturb" in sys.argv:
        g.gate_required = lambda: list(fixture["gate_required"])
        print("PERTURBED: gate_required() returns the fixture's own list")
    orig = dict(g.REQUIRED)
    rc0, out0 = run_self_test(g)
    print("null: self_test rc=%d" % rc0)
    names = sorted({n for v in orig.values() for n in v})
    refused, crashed = [], 0
    for n in names:
        g.REQUIRED.clear()
        g.REQUIRED.update({k: tuple(x for x in v if x != n) for k, v in orig.items()})
        rc, out = run_self_test(g)
        crashed += "CRASH" in out
        fails = [l for l in out.splitlines() if l.startswith("FAIL")]
        print("arm drop %-42s rc=%d %s" % (n, rc, (fails[0][:90] if fails else "")))
        if rc != 0:
            refused.append(n)
    g.REQUIRED.clear()
    g.REQUIRED.update(orig)
    print("RESULT null_rc=%d" % rc0)
    print("RESULT fixture_gate_required=%d count" % len(fixture["gate_required"]))
    print("RESULT dropped_arms=%d count" % len(names))
    print("RESULT dropped_refused=%d count" % len(refused))
    print("RESULT arms_crashed=%d count" % crashed)
    tp, tt = time.process_time() - t0p, time.thread_time() - t0t
    print("RESULT thread_factor=%.3f ratio" % (tp / tt if tt else 1.0))
    print("RESULT load1=%.2f" % os.getloadavg()[0])
    sw = 0
    try:
        for l in open("/proc/vmstat"):
            if l.startswith("pswpin "):
                sw = int(l.split()[1])
    except OSError:
        pass
    print("RESULT swapins=%d count" % sw)


if __name__ == "__main__":
    sys.exit(main())
