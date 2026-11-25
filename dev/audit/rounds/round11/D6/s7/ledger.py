#!/usr/bin/env python3
"""D6-s7, step M3: join the two per-file ledgers and run text_ledger.py check (with --plant) over D6-s7's cells.

Metric (one line): text_ledger.py check's counts over LEDGER.tsv for docs/CONTRIBUTING.md and
dev/programme/plan-2026-09-open-issues.md: units, rows, claims, each verdict, unrowed, orphan,
malformed; `--plant` is the null control that an omitted unit is refused.

Run (from the export root), after contributing.py and plan_claims.py have written their TSVs:
    PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D6/s7/ledger.py
Perturbation: --drop N removes the first N data rows from the joined ledger before the check:
`unrowed` must go UP by N and check must exit 1.
Expected at 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (counts, exact): units=2668, rows=2668,
unrowed=0, orphan=0, malformed=0, false=5, stale=8 + 29 [D2 path] = 37; plant refused.
Machine: box B13 (light seat), linux x86_64. Writes LEDGER.tsv beside itself.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ["docs/CONTRIBUTING.md", "dev/programme/plan-2026-09-open-issues.md"]
t0, th0 = time.process_time(), time.thread_time()
ap = argparse.ArgumentParser()
ap.add_argument("--drop", type=int, default=0)
a = ap.parse_args()
lines = []
for part in ("ledger_contributing.tsv", "ledger_plan.tsv"):
    rows = (HERE / part).read_text(encoding="utf-8").splitlines()
    lines += rows if not lines else rows[1:]
lines = lines[:1] + lines[1 + a.drop:]
(HERE / "LEDGER.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
rel = os.path.relpath(HERE / "LEDGER.tsv")
for extra in ([], ["--plant"]):
    r = subprocess.run([sys.executable, "tools/audit/text_ledger.py", "check", rel, *FILES, "--dim", "D6", "--root", ".", *extra],
                       capture_output=True, text=True)
    tag = "plant" if extra else "check"
    for l in (r.stdout + r.stderr).splitlines():
        if l.startswith("RESULT"):
            print(l.replace("RESULT ", f"RESULT {tag}_", 1))
        elif extra or len(l) < 300:
            print(f"  {tag}: {l[:200]}")
    print(f"RESULT {tag}_exit={r.returncode}")
d2 = sum(1 for l in lines[1:] if "\t[D2 path]" in l)
print(f"RESULT d2_path_stale_rows={d2}")
tp, tt = time.process_time() - t0, time.thread_time() - th0
print(f"RESULT thread_factor={tp / tt if tt else 1.0:.3f}")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
print(f"RESULT swapins={resource.getrusage(resource.RUSAGE_SELF).ru_majflt}")
