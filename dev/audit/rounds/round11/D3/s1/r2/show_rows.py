"""Compact view of m5_gate_table.py JSON rows (stdin)."""
import json
import sys

for line in sys.stdin:
    if line.startswith("{"):
        d = json.loads(line)
        print(d["script"], d["rc"], d["cpu_s"], d["wall_s"], d.get("reach_problems"),
              d.get("processes"), d.get("over_approx"),
              d["tail"][-200:].replace("\n", " | "))
    else:
        print(line.rstrip())
