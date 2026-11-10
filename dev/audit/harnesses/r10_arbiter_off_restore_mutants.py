#!/usr/bin/env python3
"""R10-ARBITER-OFF-RESTORE's mutation proof: each named mutant of pump_arbiter.py, alone.

Every line this group adds to ``pump_arbiter.py`` that carries behaviour has a
mutant below; each is applied to a ``git archive`` copy of the tree by
``tools/audit/seat/mutant_run.py`` (whose NULL run, unmutated, must pass
first) and the pump-duty arbiter block of ``tests/features.py`` is run
through ``tools/audit/seat/features_block.py``. Run from the repository root:

    python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py

It prints mutant_run's lines, ``SURVIVED NULL`` then ``KILLED <name>`` per
mutant at the fix head, and exits with mutant_run's status. A mutant whose
``old`` text no longer occurs exactly once is refused before anything runs.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile

BLOCK = (
    'env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py '
    '"R.section(\\"pump-duty arbiter — mode and set-points per plan step" "_pa_subs = _PaCoord("'
)
MUTANTS = json.loads(r"""
[
 {
  "name": "M01_no_consumer",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "off_restore.register_consumer(CONSUMER, _restorer, write=write_setpoint_c)",
  "new": "pass"
 },
 {
  "name": "M02_no_arm",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
  "new": "    return False"
 },
 {
  "name": "M03_no_own_refusal",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "f\"space_baseline_own:{entity}\", own,",
  "new": "f\"space_baseline_own:{entity}\", False,"
 },
 {
  "name": "M04_before_ignored",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        and _differs(\"space_setpoint\", observed, before)",
  "new": "        and True"
 },
 {
  "name": "M05_misses_ignored",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        and not held.misses.get(\"space_setpoint\") \\\n",
  "new": "        and True \\\n"
 },
 {
  "name": "M06_power_off_kept",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    held.space_before = None if off else held.space_before",
  "new": "    pass"
 },
 {
  "name": "M07_no_rebaseline",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if edit is not None and _edited(held, edit, now) and await",
  "new": "    if False and _edited(held, edit, now) and await"
 },
 {
  "name": "M08_release_writes_space",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "replace(desired(coord, inp, None, dt_util.now()), space_setpoint=None)",
  "new": "desired(coord, inp, None, dt_util.now())"
 },
 {
  "name": "M09_restored_keeps_record",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "            record.pop(\"space_setpoint\", None)",
  "new": "            pass"
 },
 {
  "name": "M10_release_no_persist",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if held.loaded:\n        await _persist(coord)",
  "new": "    if False:\n        await _persist(coord)"
 },
 {
  "name": "M11_off_no_persist",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "if held.written or held.retry or held.space_before is not None:",
  "new": "if held.written or held.retry:"
 },
 {
  "name": "M12_no_grace",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        and utc_elapsed_seconds(now, record[1]) >= ECHO_GRACE_S \\\n",
  "new": "        and True \\\n"
 },
 {
  "name": "M13_forget_keeps_before",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None",
  "new": "held.written, held.misses, held.retry = {}, {}, {}"
 },
 {
  "name": "M14_factory_none",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if not entity:\n        return None\n    return off_restore.Restorer(",
  "new": "    if True:\n        return None\n    return off_restore.Restorer("
 },
 {
  "name": "M15_adopt_skipped",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    await _adopt(inp, coord.entry, held, now)\n",
  "new": "    pass\n"
 },
 {
  "name": "M16_written_differs_ignored",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        and _differs(\"space_setpoint\", observed, record[0]) \\\n",
  "new": "        and True \\\n"
 }
]
""")


def main() -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as spec:
        json.dump(MUTANTS, spec)
    return subprocess.call(
        [sys.executable, "tools/audit/seat/mutant_run.py", "--spec", spec.name, "--cmd", BLOCK])


if __name__ == "__main__":
    sys.exit(main())
