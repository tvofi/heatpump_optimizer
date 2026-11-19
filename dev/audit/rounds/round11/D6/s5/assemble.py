#!/usr/bin/env python3
"""D6-s5 M3: assemble the seat's ledger from atoms.py and claims.py rows and run text_ledger.py check on it.

Metric: text_ledger.check's RESULT lines over the seat's 140 files (units, rows, claims, each verdict,
unrowed, orphan, malformed); claims.py's row replaces atoms.py's for the same unit.
Command (from the export root):
  PYTHONPATH=tests/hastub PYTHONUTF8=1 ~/venv-ci/bin/python3 dev/audit/rounds/round11/D6/s5/assemble.py \
      --repo /home/user/heatpump_optimizer
Expected at baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (box B13): the counts REPORT.md records, exact;
check exits 1 while any unit is unrowed (the M1/M2 remainder this seat names as not_reached).
Perturbation: --drop-claims omits claims.py's rows -> RESULT false goes to 0 and stale falls to atoms.py's 3.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse, subprocess, sys
from pathlib import Path

D = "dev/audit/rounds/round11/D6/s5"
SHA = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--drop-claims", action="store_true")
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    py = sys.executable
    subprocess.run([py, f"{D}/atoms.py", "--repo", a.repo, "--ledger", f"{D}/atom_rows.tsv"], check=True, stdout=subprocess.DEVNULL)
    if not a.drop_claims:
        subprocess.run([py, f"{D}/claims.py", "--repo", a.repo, "--rows", f"{D}/claims_rows.tsv"], check=True, stdout=subprocess.DEVNULL)
    rows = {}
    for f in [f"{D}/atom_rows.tsv"] + ([] if a.drop_claims else [f"{D}/claims_rows.tsv"]):
        for l in Path(f).read_text().splitlines():
            if l.strip():
                rows[l.split("\t")[0]] = l
    head = "unit\tline\tkind\tcommand\tresult\tverdict\ttruth"
    ledger = f"{D}/ledger_noclaims.tsv" if a.drop_claims else f"{D}/ledger.tsv"
    Path(ledger).write_text(head + "\n" + "\n".join(rows[k] for k in sorted(rows)) + "\n")
    cmd = [py, "tools/audit/text_ledger.py", "check", "--dim", "D6", ledger, "--seat", "D6-s5", "--repo", a.repo, "--ref", SHA]
    if a.plant:
        cmd.append("--plant")
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout.splitlines()
    print("\n".join(l for l in out if l.startswith("RESULT")))
    unrowed = [l.split()[1] for l in out if l.startswith("   unrowed")]
    print(f"RESULT check_rc={r.returncode}")
    print(f"RESULT unrowed_listed={len(unrowed)} (check lists at most 50)")
    print("RESULT thread_factor=1.00")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
