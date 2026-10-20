#!/usr/bin/env python3
"""Audit the fixer's in-file mutation harness independently.

Run: python3 -I mut-harness-audit.py <worktree>
Each case writes a copy of tools/plan/replan.py (and, where stated, its
durations.json) into a TemporaryDirectory and runs `--self-test` with
REPLAN_MUTATION_CHILD=1 and REPLAN_SEAT_DIR pointed at the real seat dir --
the environment the harness uses for its child.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

W = Path(sys.argv[1])
SRC = (W / "tools/plan/replan.py").read_text()
SEAT = str(W / "tools/audit/seat")
DUR = W / "tools/plan/durations.json"


def run(source, with_durations, label):
    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "replan.py"
        copy.write_text(source)
        if with_durations:
            shutil.copy(DUR, Path(td) / "durations.json")
        env = {**os.environ, "REPLAN_MUTATION_CHILD": "1", "REPLAN_SEAT_DIR": SEAT}
        r = subprocess.run([sys.executable, "-I", str(copy), "--self-test"],
                           capture_output=True, text=True, env=env)
        fails = [l for l in r.stdout.split("\n") if l.startswith("FAIL")]
        print(f"RESULT {label} rc={r.returncode} fails={fails[:1]}")
        return r.returncode


OLD = 'if prev is None or started < prev["started"]:'
NEW = 'if prev is None:'

# 1. The harness's own setup: a fresh temp dir holding only replan.py.
run(SRC, False, "harness_setup_unmutated_RC_MUST_BE_ZERO_FOR_A_NULL_CONTROL")

# 2. The null control the harness lacks: same copy, durations.json beside it.
run(SRC, True, "unmutated_with_durations")

# 3. The harness's replace(..., 1) as written: the FIRST occurrence of the
#    anchor is the mutation list's own literal, after selftest() and before
#    _ingest_check_runs(), so the production line is not changed.
first = SRC.replace(OLD, NEW, 1)
print(f"RESULT first_occurrence_is_production={SRC.find(OLD) > SRC.find('def _ingest_check_runs')}")
run(first, True, "earliest_attempt_as_the_harness_applies_it")

# 4. The production occurrence (the second) changed: the arm is sound.
i = SRC.rfind(OLD)
run(SRC[:i] + NEW + SRC[i + len(OLD):], True,
    "earliest_attempt_production_line_changed")

# 5. The other five as the harness applies them.
OTHER = [
    ("coordinator-cap", "if coord[n] and n not in inherited and cc >= coord_cap:", "if False:"),
    ("dispatch-order", "key = (-height[n], -dur_min[n], n)", "key = (n,)"),
    ("stamp-cadence", "if len(carry) >= every:", "if False:"),
    ("ci-formula", "ci = round((len(batch_rows) + len(stamps)) * gate_report, 1)",
     "ci = round(len(batch_rows) * gate_report, 1)"),
    ("gate-cancellation", "return fast + clo + ana * (1.0 + p_cancel)",
     "return fast + clo + ana"),
]
for name, old, new in OTHER:
    assert old in SRC, name
    run(SRC.replace(old, new, 1), True, name)
