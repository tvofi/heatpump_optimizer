#!/usr/bin/env python3
"""D3.M5 enumerator for seat D3-s3: every gate script tests/closures.json
records (`recorded`) that lies in this seat's cells, one per line with its
recorded seconds. Source-only. Expected 34 lines at
92d38ecb640bd462f2e19c0814d0f0b7df1ee692 (exact).
Command: python3 dev/audit/rounds/round11/D3/s3/enumerate_m5.py
"""
import json
import subprocess
import sys
from pathlib import Path

BASELINE = "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"
out = subprocess.run([sys.executable, "tools/audit/check_scopes.py", "--repo",
                      str(Path.cwd()), "--ref", BASELINE, "--seat", "D3-s3"],
                     capture_output=True, text=True, check=True).stdout
cells = {ln.split("\t")[2] for ln in out.splitlines() if ln.count("\t") >= 2}
rec = json.load(open("tests/closures.json"))["recorded"]
for s in sorted(rec):
    if s in cells:
        print(f"{s}\t{rec[s]['seconds']}")
