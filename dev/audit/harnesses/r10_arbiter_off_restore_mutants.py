#!/usr/bin/env python3
"""R10-ARBITER-OFF-RESTORE's mutation proof: each named mutant of pump_arbiter.py, alone.

Every line this group adds to ``pump_arbiter.py`` that carries behaviour has a
mutant below; each is applied to a ``git archive`` copy of the tree by
``tools/audit/seat/mutant_run.py`` (whose NULL run, unmutated, must pass
first) and the pump-duty arbiter block of ``tests/features.py`` is run
through ``tools/audit/seat/features_block.py``. Run from the repository root:

    python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py

It prints mutant_run's lines, ``SURVIVED NULL`` then ``KILLED <name>`` per
mutant at the fix head, once for M01-M20 on the arbiter block and once for the
seam mutants (M21 to M38; M33 retired) on the water-setpoint feedback block, and exits with
mutant_run's status. A mutant whose ``old`` text no longer occurs exactly once
is refused before anything runs.
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
  "old": "    if await off_restore.async_rebaseline(inp.hass, entry, CONSUMER, entity, baseline):\n",
  "new": "    if False:\n"
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
  "old": "if held.written or held.retry or held.dropped or held.space_before is not None:",
  "new": "if held.written or held.retry or held.dropped:"
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
  "old": "held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None",
  "new": "held.written, held.misses, held.retry, held.dropped = {}, {}, {}, {}"
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
 },
 {
  "name": "M17_adoption_unbounded",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    baseline = cast(float, _bounded(inp, \"space_setpoint\", edit))\n",
  "new": "    baseline = edit\n"
 },
 {
  "name": "M18_send_before_arm",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if await _held_back(inp, coord.entry, held, slot, entity, now):\n        return\n    domain = entity.split(\".\", 1)[0]\n    service = _service(slot, state, value)\n    try:\n        if service is None:\n            await write_setpoint_c(coord.hass, entity, value)\n",
  "new": "    domain = entity.split(\".\", 1)[0]\n    service = _service(slot, state, value)\n    try:\n        if service is None:\n            await write_setpoint_c(coord.hass, entity, value)\n            if await _held_back(inp, coord.entry, held, slot, entity, now):\n                return\n"
 },
 {
  "name": "M19_grace_strict",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "utc_elapsed_seconds(now, record[1]) >= ECHO_GRACE_S",
  "new": "utc_elapsed_seconds(now, record[1]) > ECHO_GRACE_S"
 },
 {
  "name": "M20_restorer_unguarded",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if not entity:\n        return None\n    return off_restore.Restorer(",
  "new": "    return off_restore.Restorer("
 }
]
""")
#: The seam with R10-WATER-SETPOINT-FEEDBACK (the merge of #3405): the off
#: restore's edit adoption reads the space slot before ``hold``, so a loop
#: write's controller cut is ``_clamp_cut``'s, never a person's baseline; and
#: the record a loop move drops (``_note_sent``) still refuses the optimizer's
#: own write as the restore's baseline (roster Carry 8). Their checks sit in
#: the feedback block, which needs the arbiter block's imports.
SEAM_BLOCK = (
    'env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py '
    '--prelude "from harness import FakeEntry as _pa_entry" '
    '--prelude "from types import SimpleNamespace as _PaNS" '
    '--prelude "from heatpump_optimizer.const import MODE_AUTO as _PA_AUTO, MODE_OFF as _PA_OFF" '
    '"# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380" "_fb_floor = _fb_sim("'
)
SEAM_MUTANTS = json.loads(r"""
[
 {
  "name": "M21_edit_adopts_cut",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        and _differs(\"space_setpoint\", observed, before) \\\n        and not _cut_of(held.feedback, record[0], observed)\n",
  "new": "        and _differs(\"space_setpoint\", observed, before)\n"
 },
 {
  "name": "M22_cut_bracket_open",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "low - SETPOINT_TOLERANCE <= observed <= high + SETPOINT_TOLERANCE",
  "new": "low - SETPOINT_TOLERANCE < observed < high + SETPOINT_TOLERANCE"
 },
 {
  "name": "M23_arm_ignores_dropped_record",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    last = record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
  "new": "    last = record[0] if record is not None else None\n"
 },
 {
  "name": "M24_prev_not_kept",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if recorded is not None:\n        rec.prev_c = held.dropped[\"space_setpoint\"] = recorded[0]\n",
  "new": "    rec.prev_c = None\n    if recorded is not None:\n        rec.prev_c = held.dropped[\"space_setpoint\"] = recorded[0]\n"
 },
 {
  "name": "M25_restored_keeps_run",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        held.feedback = None  # its prev_c is that record too (_note_sent)\n",
  "new": "        pass\n"
 },
 {
  "name": "M26_dropped_not_kept",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    if recorded is not None:\n        rec.prev_c = held.dropped[\"space_setpoint\"] = recorded[0]\n",
  "new": "    held.dropped.pop(\"space_setpoint\", None)\n    if recorded is not None:\n        rec.prev_c = held.dropped[\"space_setpoint\"] = recorded[0]\n"
 },
 {
  "name": "M27_off_pass_ends_fact",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        held.feedback = None\n        return base\n",
  "new": "        held.feedback = None\n        held.dropped.clear()\n        return base\n"
 },
 {
  "name": "M28_stale_run_ends_fact",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        rec = None  # passes that skipped the loop",
  "new": "        rec = None; held.dropped.clear()  # passes that skipped the loop"
 },
 {
  "name": "M29_stop_ends_fact",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        held.feedback = FeedbackRun(now, base, now)\n        return base\n",
  "new": "        held.feedback = FeedbackRun(now, base, now)\n        held.dropped.clear()\n        return base\n"
 },
 {
  "name": "M30_new_run_ends_fact",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        rec = held.feedback = FeedbackRun(now, base, now)\n",
  "new": "        rec = held.feedback = FeedbackRun(now, base, now)\n        held.dropped.clear()\n"
 },
 {
  "name": "M31_restart_drops_fact",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "        \"dropped\": dict(held.dropped),\n",
  "new": ""
 },
 {
  "name": "M32_load_ignores_fact",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    held.dropped = {k: v for k, v in dropped.items() if _writable(k, v)} if isinstance(dropped, dict) else {}\n",
  "new": "    held.dropped = {}\n"
 },
 {
  "name": "M34_restore_keeps_fact",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "(held.written, held.misses, held.retry, held.dropped)",
  "new": "(held.written, held.misses, held.retry)"
 },
 {
  "name": "M35_forget_keeps_dropped",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None",
  "new": "held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None"
 },
 {
  "name": "M36_off_ignores_dropped",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "if held.written or held.retry or held.dropped or held.space_before is not None:",
  "new": "if held.written or held.retry or held.space_before is not None:"
 },
 {
  "name": "M37_arm_reads_run",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": "    last = record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
  "new": "    last = record[0] if record is not None else None if held.feedback is None else held.feedback.prev_c\n"
 },
 {
  "name": "M38_load_unfiltered",
  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
  "old": " if _writable(k, v)} if isinstance(dropped, dict)",
  "new": "} if isinstance(dropped, dict)"
 }
]
""")


def _run(mutants: list[dict[str, str]], cmd: str) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as spec:
        json.dump(mutants, spec)
    return subprocess.call(
        [sys.executable, "tools/audit/seat/mutant_run.py", "--spec", spec.name, "--cmd", cmd])


def main() -> int:
    return max(_run(MUTANTS, BLOCK), _run(SEAM_MUTANTS, SEAM_BLOCK))


if __name__ == "__main__":
    sys.exit(main())
