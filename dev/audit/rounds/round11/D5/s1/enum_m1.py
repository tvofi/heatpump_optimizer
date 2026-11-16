"""D5-s1 enumerator for D5.M1: reader path x `document` row of text_ledger.py outline.

Command: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s1/enum_m1.py
Prints one line per item: <reader path>\t<document>.  Baseline 92d38ecb: 3 x 9 = 27 lines.
"""
import subprocess, sys
PATHS = ("new-user-hacs-to-first-plan", "feature-config(two-tank,ECL110,capacity-tariff)",
         "developer-running-tests")
out = subprocess.run([sys.executable, "tools/audit/text_ledger.py", "outline", "--seat", "D5-s1",
                      "--repo", "/Users/timmalmstrom/hpo-orch/r10s6/r11/find-wt",
                      "--ref", "92d38ecb640bd462f2e19c0814d0f0b7df1ee692"], capture_output=True, text=True).stdout
docs = [l.split("\t")[3] for l in out.splitlines() if l.count("\t") >= 3 and l.split("\t")[2] == "document"]
for p in PATHS:
    for d in docs:
        print(f"{p}\t{d}")
