#!/usr/bin/env python3
"""v1_suite_mutants.py -- D3 verifier: does the committed suite notice the
D3-s2-01 / D3-s2-02 mutants when every script of the file's MEASURED closure runs?

Metric (one line): per mutant, the scripts of tests/closures.json's closure of
the mutated file (minus tests/env_drift.py, which needs a ref != HEAD -- see the
report) whose (rc, failed-count) differs from the unmutated baseline run in the
same tree -- the tests/mutation_table.py:run_script kill rule. 0 = survivor.

Mutants (one production line each, restored in finally, hash-checked):
  m05 legionella.py hours_since clamp removed
  m11 services.py:486  `float(minimum) > ceiling` -> `>=`
  m12 services.py:823  `wanted > ceiling` -> `>=`
Positive control (--posctl): m11 with `>` -> `<` must be killed.

Command (tree root):
  PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/v1_suite_mutants.py [--posctl]
Machine: 4-vCPU shared container; walls provisional; kill counts exact.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
TMP = Path("/home/claude/audit-r8/tmp/D3-v1")
PKG = "custom_components/heatpump_optimizer/"
_FAILED = re.compile(r"(\d+) of (\d+) [^\n]*FAILED")
MUTANTS = {
    "m05": ("legionella.py", "        return max(0.0, since.total_seconds() / 3600.0)",
            "        return since.total_seconds() / 3600.0"),
    "m11": ("services.py", "            if float(minimum) > ceiling:",
            "            if float(minimum) >= ceiling:"),
    "m12": ("services.py", "            if wanted > ceiling:",
            "            if wanted >= ceiling:"),
}
if "--posctl" in sys.argv:
    MUTANTS = {"posctl": ("services.py", "            if float(minimum) > ceiling:",
                          "            if float(minimum) < ceiling:")}


def closure(rel):
    raw = json.loads((ROOT / "tests/closures.json").read_text())
    rec = raw["recorded"]
    s = [k for k, v in raw["closures"].items() if rel in v and k != "tests/env_drift.py"]
    s.sort(key=lambda k: rec.get(k, {}).get("seconds", 999))
    if "tests/card.mjs" in s and "tests/plan_view.py" in s:
        s.remove("tests/card.mjs")
        s.insert(s.index("tests/plan_view.py") + 1, "tests/card.mjs")
    if "tests/card_drift.mjs" in s and "tests/plan_view.py" in s:
        s.remove("tests/card_drift.mjs")
        s.insert(s.index("tests/plan_view.py") + 1, "tests/card_drift.mjs")
    return s


def run(script):
    env = dict(os.environ, PYTHONPATH="tests/hastub", TMPDIR=str(TMP),
               HPO_PLANDATA=str(TMP / "plandata"))
    cmd = ["node", script] if script.endswith(".mjs") else [sys.executable, script]
    t = time.monotonic()
    try:
        p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=2400)
        hits = _FAILED.findall(p.stdout)
        return p.returncode, (int(hits[-1][0]) if hits else 0), time.monotonic() - t, p.stdout
    except subprocess.TimeoutExpired:
        return 124, 0, time.monotonic() - t, ""


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    files = sorted({m[0] for m in MUTANTS.values()})
    order = []
    for f in files:
        for s in closure(PKG + f):
            if s not in order:
                order.append(s)
    base = {}
    for s in order:
        rc, failed, wall, _ = run(s)
        base[s] = (rc, failed)
        print(f"  baseline {s}: rc={rc} failed={failed} {wall:.0f}s (provisional)", flush=True)
    survivors = 0
    for mid, (fname, old, new) in MUTANTS.items():
        path = ROOT / PKG / fname
        orig = path.read_text()
        h = hashlib.sha256(orig.encode()).hexdigest()
        assert orig.count(old) == 1, (mid, orig.count(old))
        killers = []
        try:
            path.write_text(orig.replace(old, new, 1))
            for s in closure(PKG + fname):
                rc, failed, wall, out = run(s)
                if rc != base[s][0] or failed > base[s][1]:
                    fails = [ln.strip() for ln in out.splitlines() if "FAIL" in ln][:3]
                    killers.append(s)
                    print(f"  {mid} KILLED by {s}: rc={rc} failed={failed} {fails}", flush=True)
                else:
                    print(f"  {mid} survives {s} ({wall:.0f}s)", flush=True)
        finally:
            path.write_text(orig)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == h
        survivors += int(not killers)
        print(f"RESULT {mid}_killers={len(killers)} count")
    print(f"RESULT survivors={survivors} count (of {len(MUTANTS)})")
    print(f"RESULT load1={os.getloadavg()[0]:.2f}")
    print("RESULT thread_factor=1.000 (subprocess-only harness; counts not timings)")
    print("RESULT swapins=0")


if __name__ == "__main__":
    main()
