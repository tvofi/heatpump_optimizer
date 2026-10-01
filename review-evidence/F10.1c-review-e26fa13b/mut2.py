"""Reviewer's own mutants of the round-2 _instant (F10.1c review)."""

import pathlib
import sys

root = pathlib.Path(sys.argv[1])
m = sys.argv[2]
p = root / "custom_components/heatpump_optimizer/manual_plan.py"
s = p.read_text()
M = {
    "INSTANT-guard-off": (
        "    if when.tzinfo is not None:\n        return when.timestamp()\n",
        "    if False:\n        return when.timestamp()\n",
    ),
    "INSTANT-naive-local": (
        "    return when.replace(tzinfo=timezone.utc).timestamp()",
        "    return when.timestamp()",
    ),
}
o, n = M[m]
assert s.count(o) == 1
p.write_text(s.replace(o, n))
print("applied", m)
