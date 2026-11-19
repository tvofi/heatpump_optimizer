#!/usr/bin/env python3
"""D11-s1 round 11: the claim-file merge driver's mutation control cannot fire.

Metric (one line): RESULT baseline_pass of dev/audit/harnesses/claim_merge_mutants.py
(1 = its unmutated null control passes, so its kills mean something; 0 = every
row after it is unreachable), and the kills it reaches.
Count key: the production control's own null-control return code.

Run (from the export root):
    PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D11/s1/claim_control.py
    ... --perturb   # the one-line edit: its temp copy also takes custom_components/,
                    # which tests/harness.py has read at import since aa631f7c5d
Expected: baseline_pass=0, mutants_reached=0 (exact); under --perturb
baseline_pass=1 and mutants_reached=<its MUTANTS count> (up).
Null control: tests/entities.py's CM section, run in the real tree by the gate,
is unaffected (the harness's copy is what lacks the integration).
Baseline: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692; machine: box B6 (linux, 4 cpu).
Instrumented symbol: dev/audit/harnesses/claim_merge_mutants.py:main (run_section),
driving tests/entities.py's claim-file merge-driver section over tests/env_drift.py:merge_claim_file.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import contextlib
import importlib.util
import io
import shutil
import sys
import time

c0, t0 = time.process_time(), time.thread_time()
spec = importlib.util.spec_from_file_location("cmm", "dev/audit/harnesses/claim_merge_mutants.py")
cmm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cmm)

if "--perturb" in sys.argv:
    real_copytree = shutil.copytree

    def copytree(src, dst, *a, **k):
        r = real_copytree(src, dst, *a, **k)
        if str(src).endswith("/tests"):
            real_copytree(cmm.ROOT / "custom_components", os.path.join(os.path.dirname(dst), "custom_components"),
                          ignore=shutil.ignore_patterns("__pycache__"))
        return r
    cmm.shutil.copytree = copytree

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    rc = cmm.main()
out = buf.getvalue()
print(out)
res = dict(l.split(" ", 1)[1].split("=", 1) for l in out.splitlines() if l.startswith("RESULT "))
reached = int(res.get("killed", 0)) + int(res.get("survived", 0))
print(f"RESULT baseline_pass={res.get('baseline_pass')} bool")
print(f"RESULT mutants_reached={reached} mutants")
print(f"RESULT mutants_defined={len(cmm.MUTANTS)} mutants")
c1, t1 = time.process_time(), time.thread_time()
print(f"RESULT thread_factor={(c1 - c0) / max(t1 - t0, 1e-9):.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
try:
    sw = [l for l in open("/proc/vmstat") if l.startswith("pswpin")][0].split()[1]
except Exception:
    sw = "n/a"
print(f"RESULT swapins={sw}")
