"""Verifier D1#1, V2 for D1-s1-01: is a persisted solve_worker_fallback repair withdrawable from a fresh process?

Metric: count of ('heatpump_optimizer','solve_worker_fallback') issues left on the
registry after a FRESH interpreter, holding only the persistent issues the first
interpreter left (the restore model of a real HA issue registry: persistent issues
are restored, module globals start empty), runs the production success-path call
coordinator._clear_worker_fallback(hass, entry_id) K=3 times.
Cause used: the EOF text a stop's reap produces. Null: clear in the SAME interpreter -> 0.
Run: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D1/verify-1/v2_s1_01_fallback_clear.py
"""
import json
import os
import subprocess
import sys

CHILD_A = r'''
import json, sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeHass
from heatpump_optimizer import coordinator as c
h = FakeHass()
c._note_worker_fallback(h, c.ProcessWorkerUnavailable("process worker exited rc=None: Ran out of input"), "e1")
issues = [(d, i, {"is_persistent": k.get("is_persistent")}) for d, i, k in getattr(h, "issues", [])]
same = FakeHass(); c._WORKER_FALLBACK_CAUSES.clear()
c._note_worker_fallback(same, c.ProcessWorkerUnavailable("x"), "e1")
for _ in range(3):
    c._clear_worker_fallback(same, "e1")
left = len([i for i in getattr(same, "issues", []) if i[1] == "solve_worker_fallback"])
print(json.dumps({"issues": issues, "same_process_left": left}))
'''
CHILD_B = r'''
import json, sys
sys.path.insert(0, "tests"); sys.path.insert(0, "custom_components")
from harness import FakeHass
from heatpump_optimizer import coordinator as c
h = FakeHass()
h.issues = [tuple(x) for x in json.loads(sys.argv[1]) if x[2].get("is_persistent")]
for _ in range(3):
    c._clear_worker_fallback(h, "e1")
print(len([i for i in h.issues if i[1] == "solve_worker_fallback"]))
'''


def run(code, *args):
    out = subprocess.run([sys.executable, "-c", code, *args], capture_output=True, text=True, check=True)
    return out.stdout.strip().splitlines()[-1]


a = json.loads(run(CHILD_A))
persist = sum(1 for d, i, k in a["issues"] if i == "solve_worker_fallback" and k["is_persistent"])
b = run(CHILD_B, json.dumps(a["issues"]))
print(f"RESULT created_persistent={persist} count")
print(f"RESULT left_after_fresh_process_clears={b} count")
print(f"RESULT null_same_process_left={a['same_process_left']} count")
print(f"RESULT load1={os.getloadavg()[0]:.2f}")
