#!/usr/bin/env python3
"""Assemble seat D3-s3's coverage rows from the committed records (no run).

Command: python3 dev/audit/rounds/round11/D3/s3/build_report.py > /tmp/cov.json
Reads enumerate.py's universe (via /root-independent re-run), the pre-screen
record prescreen_all.json and the M5 table (solves*.json). Source-only.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
env_pp = {"PYTHONPATH": "tests/hastub"}


def lines(cmd):
    import os
    out = subprocess.run(cmd, capture_output=True, text=True,
                         env={**os.environ, **env_pp}).stdout
    return [ln for ln in out.splitlines() if ln and not ln.startswith("#")]


def main():
    m1 = lines([PY, "dev/audit/rounds/round11/D3/s3/enumerate.py"])
    pre = json.load(open(HERE / "prescreen_all.json"))
    outc, verd = pre["outcomes"], pre["verdicts"]
    screened = {f"{m['file']}:{m['line']} {m['kind']}" for m in pre["pool"]
                if f"{m['file']}:{m['line']} {m['kind']}" in verd}
    # an enumerator line: anchor \t file:line \t old
    m1_keys = []
    for ln in m1:
        parts = ln.split("\t")
        m1_keys.append(parts[1])
    # M2 examined: unpinned sites whose (file:line) a driven mutant covered
    scr_fl = Counter(k.split()[0] for k in screened)
    examined2 = []
    left2 = Counter()
    seen = Counter()
    for fl in m1_keys:
        seen[fl] += 1
        if seen[fl] <= scr_fl.get(fl, 0):
            examined2.append(fl)
        else:
            left2[fl.split(":")[0].rsplit("/", 1)[-1]] += 1
    surv = lines([PY, "dev/audit/rounds/round11/D3/s3/survivors.py", "--survivors"])
    print(json.dumps({"m1": len(m1), "m2_examined": len(examined2),
                      "m2_not_reached_groups": [f"{f} ({n} sites)" for f, n in sorted(left2.items())],
                      "survivors": surv, "screened": len(screened),
                      "pool": len(pre["pool"])}, indent=1))


if __name__ == "__main__":
    main()
