# Review packet #3737
head: 212e79760d8427b1a16ce33f3074b71a94886824
base: 9fe63d00b59f100aea67267ddddc95522e164aa1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=135087753689 queued
arm id=135079058988 skipped
budget-raise-gate / budget-raise-gate id=135087753703 queued
cancel-superseded id=135082391125 queued
codeql / Analyze (actions) id=135087753551 queued
codeql / Analyze (javascript-typescript) id=135087753564 queued
codeql / Analyze (python) id=135087753469 queued
governance / env-matrix id=135087753799 queued
governance / instrument-self-tests id=135087753618 queued
governance / policy-docs id=135087753595 queued
governance / record id=135087756933 skipped
governance / wave-script id=135087753628 queued
hassfest / hassfest id=135087753546 success
kernel-points id=135087756457 skipped
prelude id=135082391540 queued
refresh id=135082391611 queued
tests / briefs id=135087753544 queued
tests / closure-scope id=135087753683 queued
tests / mutation id=135087753389 queued
tests / nightly-status id=135087753533 queued
validate / validate-hacs id=135087753449 in_progress

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 135087753618: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item a1204677: R11-CARRY-DRAWMAP: R11-CARRY-DRAWMAP resolved on origin/handoff/audit-r10-roster
NOTE body item a6fca9b9: R11-CARRY-DRAWMAP: R11-CARRY-DRAWMAP resolved on origin/handoff/audit-r10-roster
NOTE body item d3edeb82: R11-CARRY-DRAWMAP: R11-CARRY-DRAWMAP resolved on origin/handoff/audit-r10-roster
NOTE body item 1da85573: R11-CARRY-DRAWMAP: R11-CARRY-DRAWMAP resolved on origin/handoff/audit-r10-roster
NOTE body item ae43e858: R11-CARRY-DRAWMAP: R11-CARRY-DRAWMAP resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 28 script(s) run, 5 scoped out.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude "exec(open('<prelude>').read())" 'R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")'
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         dev/audit/harnesses/draw_map_rows.py
             `dev/audit/harnesses/draw_map_rows.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/draw_map_rows.py --synthetic
             `dev/audit/harnesses/draw_map_rows.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D
             `tests/closure.py` is in the tree at this head
  unverified git grep -n "judge_floor(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "owed_scale(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 5 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
new file mode 100644
index 0000000000..bd324872f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF ac9b3721",
+  "killed_by": "tests/features.py",
+  "old": "        if experiment:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.BOOLOP.b9424216.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.BOOLOP.b9424216.json
new file mode 100644
index 0000000000..de0c0a7d9e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.BOOLOP.b9424216.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.owed_scale BOOLOP b9424216",
+  "killed_by": "tests/features.py",
+  "old": "            configured, now, read and self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`configured, now, read or self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json
deleted file mode 100644
index c691d8a05a..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.owed_scale RETURN_DEL a64e3c97",
-  "killed_by": "tests/features.py",
-  "old": "        return self.probe.owed_scale(configured, now, self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.2d59d2fc.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.2d59d2fc.json
new file mode 100644
index 0000000000..6cdf6cbba9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.2d59d2fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 2d59d2fc",
+  "killed_by": "tests/structure.py",
+  "old": "        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now(), not experiment)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
index d2589c55da..7e0808e417 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF f61826c8",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c294c9b7",
   "killed_by": "tests/features.py",
-  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json
deleted file mode 100644
index 0a826b8c36..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c41a3ead",
-  "killed_by": "tests/features.py",
-  "old": "        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now())) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_dhw_current_hour.RETURN_DEL.a2025997.json b/tests/mutation_ledger/killed_by/coordinator.py/_dhw_current_hour.RETURN_DEL.a2025997.json
new file mode 100644
index 0000000000..7e614f40e7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_dhw_current_hour.RETURN_DEL.a2025997.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_dhw_current_hour RETURN_DEL a2025997",
+  "killed_by": "tests/features.py",
+  "old": "    return now.hour + now.minute / 60.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.0a236124.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.0a236124.json
new file mode 100644
index 0000000000..3ea724c73f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.0a236124.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 0a236124",
+  "killed_by": "tests/features.py",
+  "old": "SEGMENT_SETTLE_MIN = 3",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SEGMENT_SETTLE_MIN = 6`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.849fc597.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.849fc597.json
new file mode 100644
index 0000000000..392fae90ab
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.849fc597.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 849fc597",
+  "killed_by": "tests/features.py",
+  "old": "SEGMENT_MAX_MIN = 30",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SEGMENT_MAX_MIN = 60`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.cdb85f1f.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.cdb85f1f.json
new file mode 100644
index 0000000000..7b5329cc12
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.cdb85f1f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST cdb85f1f",
+  "killed_by": "tests/features.py",
+  "old": "MAP_ROWS = 672",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`MAP_ROWS = 1344`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.d55ebb0a.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.d55ebb0a.json
new file mode 100644
index 0000000000..1a1f168e3d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.d55ebb0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST d55ebb0a",
+  "killed_by": "tests/features.py",
+  "old": "SEGMENT_STEADY_MIN = 2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SEGMENT_STEADY_MIN = 4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows._close.GUARD_OFF.57f875bd.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows._close.GUARD_OFF.57f875bd.json
new file mode 100644
index 0000000000..8b530c0136
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows._close.GUARD_OFF.57f875bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows._close GUARD_OFF 57f875bd",
+  "killed_by": "tests/features.py",
+  "old": "        if row is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.commit_runs.GUARD_OFF.5f94b1f4.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.commit_runs.GUARD_OFF.5f94b1f4.json
new file mode 100644
index 0000000000..2fe71c3432
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.commit_runs.GUARD_OFF.5f94b1f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.commit_runs GUARD_OFF 5f94b1f4",
+  "killed_by": "tests/features.py",
+  "old": "        if keep:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.BOOLOP.5370a6a2.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.BOOLOP.5370a6a2.json
new file mode 100644
index 0000000000..517641c1df
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.BOOLOP.5370a6a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass BOOLOP 5370a6a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.open and int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.open or int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.3603e23a.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.3603e23a.json
new file mode 100644
index 0000000000..ac89a0128b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.3603e23a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass CMP_BOUND 3603e23a",
+  "killed_by": "tests/features.py",
+  "old": "        stopped = rec.defrost or rec.drawn_kw is None or rec.drawn_kw <= RUNNING_FLOOR_KW",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`stopped = rec.defrost or rec.drawn_kw is None or rec.drawn_kw < RUNNING_FLOOR_KW`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.a2c87e94.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.a2c87e94.json
new file mode 100644
index 0000000000..89f918b0f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.a2c87e94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass CMP_BOUND a2c87e94",
+  "killed_by": "tests/features.py",
+  "old": "                (rec.at - first.at).total_seconds() >= SEGMENT_MAX_MIN * 60.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`(rec.at - first.at).total_seconds() > SEGMENT_MAX_MIN * 60.0):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.5370a6a2.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.5370a6a2.json
new file mode 100644
index 0000000000..c82c5a33d8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.5370a6a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass GUARD_OFF 5370a6a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.open and int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.603e3086.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.603e3086.json
new file mode 100644
index 0000000000..971b66d52e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.603e3086.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass GUARD_OFF 603e3086",
+  "killed_by": "tests/features.py",
+  "old": "        if rec is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.ed8f0eb2.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.ed8f0eb2.json
new file mode 100644
index 0000000000..2719e4bdf3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.ed8f0eb2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass GUARD_OFF ed8f0eb2",
+  "killed_by": "tests/features.py",
+  "old": "        if stopped:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/PassRecord.run_key.RETURN_DEL.832052c6.json b/tests/mutation_ledger/killed_by/draw_range.py/PassRecord.run_key.RETURN_DEL.832052c6.json
new file mode 100644
index 0000000000..cd631f51c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/PassRecord.run_key.RETURN_DEL.832052c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:PassRecord.run_key RETURN_DEL 832052c6",
+  "killed_by": "tests/features.py",
+  "old": "        return (self.written_c, self.level_kw, self.duty, self.origin)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.4e439b74.json b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.4e439b74.json
new file mode 100644
index 0000000000..7ce39d5035
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.4e439b74.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_cell GUARD_OFF 4e439b74",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(value, str):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.5cd1f888.json b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.5cd1f888.json
new file mode 100644
index 0000000000..6e38481602
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.5cd1f888.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_cell GUARD_OFF 5cd1f888",
+  "killed_by": "tests/features.py",
+  "old": "    if value is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_cell.RETURN_DEL.9b1bb4f6.json b/tests/mutation_ledger/killed_by/draw_range.py/_cell.RETURN_DEL.9b1bb4f6.json
new file mode 100644
index 0000000000..6d732bb5ae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_cell.RETURN_DEL.9b1bb4f6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_cell RETURN_DEL 9b1bb4f6",
+  "killed_by": "tests/features.py",
+  "old": "    return str(int(value)) if isinstance(value, int) else repr(round(float(value), 3))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.BOOLOP.c470afed.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.BOOLOP.c470afed.json
new file mode 100644
index 0000000000..a90a6b39c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.BOOLOP.c470afed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell BOOLOP c470afed",
+  "killed_by": "tests/features.py",
+  "old": "    if cell == \"\" and name not in MAP_COLUMNS[:2]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if cell == \"\" or name not in MAP_COLUMNS[:2]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.345675b8.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.345675b8.json
new file mode 100644
index 0000000000..5cca0b8258
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.345675b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell GUARD_OFF 345675b8",
+  "killed_by": "tests/structure.py",
+  "old": "    if name in _MAP_TEXT:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.b061f526.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.b061f526.json
new file mode 100644
index 0000000000..6152108342
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.b061f526.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell GUARD_OFF b061f526",
+  "killed_by": "tests/features.py",
+  "old": "    if not np.isfinite(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.c470afed.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.c470afed.json
new file mode 100644
index 0000000000..7404101e18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.c470afed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell GUARD_OFF c470afed",
+  "killed_by": "tests/features.py",
+  "old": "    if cell == \"\" and name not in MAP_COLUMNS[:2]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.RETURN_DEL.d4c9e2a6.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.RETURN_DEL.d4c9e2a6.json
new file mode 100644
index 0000000000..f35dd2e8c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.RETURN_DEL.d4c9e2a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell RETURN_DEL d4c9e2a6",
+  "killed_by": "tests/features.py",
+  "old": "    return value",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.1179dcea.json b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.1179dcea.json
new file mode 100644
index 0000000000..0a2ad550e9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.1179dcea.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_segment_row CMP_BOUND 1179dcea",
+  "killed_by": "tests/features.py",
+  "old": "    steady = [p for p in passes if (p.at - first.at).total_seconds() >= SEGMENT_SETTLE_MIN * 60.0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`steady = [p for p in passes if (p.at - first.at).total_seconds() > SEGMENT_SETTLE_MIN * 60.0]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.bec45cb3.json b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.bec45cb3.json
new file mode 100644
index 0000000000..c141adb4da
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.bec45cb3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_segment_row CMP_BOUND bec45cb3",
+  "killed_by": "tests/features.py",
+  "old": "    if len(steady) < SEGMENT_STEADY_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(steady) <= SEGMENT_STEADY_MIN:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.GUARD_OFF.bec45cb3.json b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.GUARD_OFF.bec45cb3.json
new file mode 100644
index 0000000000..e88f365015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.GUARD_OFF.bec45cb3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_segment_row GUARD_OFF bec45cb3",
+  "killed_by": "tests/structure.py",
+  "old": "    if len(steady) < SEGMENT_STEADY_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.5edbe6c2.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.5edbe6c2.json
new file mode 100644
index 0000000000..e4d73eab95
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.5edbe6c2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_map GUARD_OFF 5edbe6c2",
+  "killed_by": "tests/features.py",
+  "old": "    if len(split) != len(MAP_COLUMNS):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.76b546cb.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.76b546cb.json
new file mode 100644
index 0000000000..f1328adc24
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.76b546cb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_map GUARD_OFF 76b546cb",
+  "killed_by": "tests/features.py",
+  "old": "    if len({len(c) for c in split}) != 1:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.RETURN_DEL.a8227ccf.json
new file mode 100644
index 0000000000..edeadcda14
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.RETURN_DEL.a8227ccf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_map RETURN_DEL a8227ccf",
+  "killed_by": "tests/features.py",
+  "old": "    return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/note_pass.GUARD_OFF.b2310c56.json b/tests/mutation_ledger/killed_by/draw_range.py/note_pass.GUARD_OFF.b2310c56.json
new file mode 100644
index 0000000000..5dc93fa25c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/note_pass.GUARD_OFF.b2310c56.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:note_pass GUARD_OFF b2310c56",
+  "killed_by": "tests/features.py",
+  "old": "    if draw is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_map_inputs.RETURN_DEL.86bbdd73.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_map_inputs.RETURN_DEL.86bbdd73.json
new file mode 100644
index 0000000000..ce42f5a25c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_map_inputs.RETURN_DEL.86bbdd73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_map_inputs RETURN_DEL 86bbdd73",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return MapInputs(_level_kw(inp, now, boost_c is not None), p_min, p_max, heat_c, floor_c, boost_c is not None)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_pass_record.GUARD_OFF.c93be904.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_pass_record.GUARD_OFF.c93be904.json
new file mode 100644
index 0000000000..ddcdc43432
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_pass_record.GUARD_OFF.c93be904.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_pass_record GUARD_OFF c93be904",
+  "killed_by": "tests/features.py",
+  "old": "    if command is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.CMP_BOUND.ebe1fc1b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.CMP_BOUND.ebe1fc1b.json
new file mode 100644
index 0000000000..63c1c6295b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.CMP_BOUND.ebe1fc1b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin CMP_BOUND ebe1fc1b",
+  "killed_by": "tests/features.py",
+  "old": "    held_start = utc_elapsed_seconds(now, run.start) < FEEDBACK_START_HOLD.total_seconds()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`held_start = utc_elapsed_seconds(now, run.start) <= FEEDBACK_START_HOLD.total_seconds()`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.50cd56b2.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.50cd56b2.json
new file mode 100644
index 0000000000..63e75161fc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.50cd56b2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF 50cd56b2",
+  "killed_by": "tests/features.py",
+  "old": "    if run is None or not run.running:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.531d53db.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.531d53db.json
new file mode 100644
index 0000000000..23eadd1541
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.531d53db.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF 531d53db",
+  "killed_by": "tests/features.py",
+  "old": "    if duty not in (\"space\", \"both\"):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.60aea822.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.60aea822.json
new file mode 100644
index 0000000000..c7783c9bc3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.60aea822.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF 60aea822",
+  "killed_by": "tests/features.py",
+  "old": "    if action.get(\"mode\") == \"system_identification\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.bd37d9be.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.bd37d9be.json
new file mode 100644
index 0000000000..f30022d24b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.bd37d9be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF bd37d9be",
+  "killed_by": "tests/features.py",
+  "old": "    if boost_on:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.RETURN_DEL.f3bc64b6.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.RETURN_DEL.f3bc64b6.json
new file mode 100644
index 0000000000..5990a4f0b4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.RETURN_DEL.f3bc64b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin RETURN_DEL f3bc64b6",
+  "killed_by": "tests/structure.py",
+  "old": "    return ORIGIN_FEEDBACK_START if held_start else ORIGIN_FEEDBACK",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json
deleted file mode 100644
index b4b7d7250a..0000000000
--- a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_flow_target CLAMP_DROP 38a077e7",
-  "old": "            lo=min(floor_c, heat_c),",
-  "reason": "CLAMP_DROP prints `lo=(floor_c)` for `lo=min(floor_c, heat_c)` in _flow_target's _bounded call. The argument reaches nothing but that call's `lo`, which quantise_setpoint_c applies as `max(out, _on_step(lo, \"up\"))` and then bounds by the same call's `hi=heat_c`. If floor_c <= heat_c both texts pass the same number. If floor_c > heat_c the original passes heat_c and the mutant floor_c: the mutant's `max(out, ceil-step(floor_c))` is at least floor_c > heat_c, so the following `min(..., floor-step(heat_c))` returns floor-step(heat_c) -- the value the original's `max(out, ceil-step(heat_c))` also returns, since ceil-step(heat_c) >= floor-step(heat_c). Equal on both branches, and the unit conversion is monotone, so the Fahrenheit path is equal too. Measured at this head: 7680 _flow_target cells (entity ranges with and without a min/max, steps 1.0/0.5/0.1, degC and degF; configured heating ceiling absent and 30-60 degC; inlets 5-65 degC and an unmeasured one; levels at p_min/mid/p_max; the heating and idle duties) differ on 0 cells between the head and the mutant, while the probe's null control -- the same line's other mutant, `lo=None` -- differs on 21 cells (a 25.3 degC tank at the floor writes 31.0 at the head, 30.0 under lo=None). The probe is scratch ($SCRATCH/mut/eqprobe.py sha1 c035d11b3a900642cc478a1a3ef1ab28c4016cfb, $SCRATCH/mut/grid.py sha1 c10409a553f148215f700bc542d345a9f40a0c6c); the in-tree re-verification is `python3 tests/mutation_table.py --anchor '<this anchor>'`, which drives the site with the drivers in play.",
-  "verdict": "equivalent"
-}


## Review scope: full (no verdict on verdict/<pr> names the reviewed head dbc6569df207a9e9c39ec9134074182888f6b9b9, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/accuracy.py b/custom_components/heatpump_optimizer/accuracy.py
index fb60587220..8b60ba5f88 100644
--- a/custom_components/heatpump_optimizer/accuracy.py
+++ b/custom_components/heatpump_optimizer/accuracy.py
@@ -1218,10 +1218,28 @@ class MeasuredCop:
         return self.probe.response
 
     @staticmethod
-    def judge_floor(asked_kw: float, drawn_kw: float | None, params: Any, draw: DrawRange | None = None) -> str | None:
-        """``COP_REFUSED_DUTY_FLOOR`` when the ask or the draw is under the duty
-        floor (``draw_range.power_floor_kw`` on the window ``draw``), else None;
-        None with no draw (a heat counter's install, judged at its span close)."""
+    def judge_floor(
+        asked_kw: float, drawn_kw: float | None, params: Any, draw: DrawRange | None = None,
+        experiment: bool = False,
+    ) -> str | None:
+        """The first judgement every interval meets, or None.
+
+        ``COP_REFUSED_OFF_ASK`` for an ``experiment`` interval (the fit, the
+        ceiling probe; the action that governed it was the
+        system-identification override, the action ``asked_kw`` is read from):
+        an experiment's ask is not the plan's, so drawn over asked is no
+        efficiency reading. Where heat is metered the COP is heat over the
+        draw, and the reason is the scale's: it is one scalar on a law of lift
+        alone, learned where the plan runs the compressor, and an experiment
+        drives it to its band ends, where an inverter's efficiency departs from
+        that law (a part-load point would bias it). Then
+        ``COP_REFUSED_DUTY_FLOOR`` when the ask or the draw is under the duty
+        floor (``draw_range.power_floor_kw`` on the window ``draw``).
+        ``drawn_kw`` ``None``: no per-cycle draw (a heat counter's install),
+        judged on the experiment alone, so its span fails the cycle's gate.
+        """
+        if experiment:
+            return COP_REFUSED_OFF_ASK
         if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw(draw, params):
             return COP_REFUSED_DUTY_FLOOR
         return None
@@ -1251,10 +1269,13 @@ class MeasuredCop:
         install measures no heat (``probe_install(...).measured_heat``)."""
         return state == ASK_UNOBTAINABLE and draw is not None and not measured_heat
 
-    def owed_scale(self, configured: Callable[[], float], now: datetime) -> float | None:
+    def owed_scale(self, configured: Callable[[], float], now: datetime, read: bool = True) -> float | None:
         """The COP scale ``probe`` owes this cycle, or None (``ScaleProbe.owed_scale``).
-        A frozen or unread cycle since the last one (``refusal``) read no interval."""
-        return self.probe.owed_scale(configured, now, self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))
+        A frozen or unread cycle since the last one (``refusal``) read no interval,
+        nor does this one where not ``read`` (an experiment's: the step the last
+        row earned is not taken inside it)."""
+        return self.probe.owed_scale(
+            configured, now, read and self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))
 
     def judge_ratio(
         self, ewma: float, row: CopInterval, params: Any, draw: DrawRange | None, measured_heat: bool = False
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 1f44ffc639..b013e79038 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -904,6 +904,12 @@ def _outage_reading(
     return f"Update gap of {gap_minutes:.0f} minutes"
 
 
+def _dhw_current_hour() -> float:
+    """The local hour now, fractional, as the hot-water windows read it."""
+    now = dt_util.now()
+    return now.hour + now.minute / 60.0
+
+
 def _cop_fold_blocked(coord: Any) -> bool:
     """#1067: whether this interval's meter reading describes the compressor.
 
@@ -4147,6 +4153,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             action=self._current_action,
             measured_power_kw=pump_arbiter.live_power_kw(self.hass, ctx._config),
             defrosting=self._pump_signals.defrosting,
+            draw=self._accuracy.draw,
             disinfecting=getattr(
                 getattr(self._legionella, "disinfect", None), "memo", None
             )
@@ -5337,12 +5344,14 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         commanded = self._commanded_power()
         params, measured_heat, priced = ctx._thermal_params, probe_install(ctx._config).measured_heat, self._cop_scale
         # Past the freeze gate (a frozen cycle moves no scale): the held intervals ``MeasuredCop.release``
-        # lets out, then the scale its heat-ask probe owes this cycle (``owed_scale``; owner ruling D4).
+        # lets out, then the scale its heat-ask probe owes this cycle (``owed_scale``; owner ruling D4),
+        # which an experiment's cycle reads as no interval: its row is never admitted.
+        experiment = self._current_action.get("mode") == "system_identification"
         for row in self._measured_cop.release(draw, params, dt_util.now(), measured_heat):
             self._fold_cop_evidence(row.asked_kw, row.drawn_kw, None, row.reference, row.cop_scale)
-        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now())) is not None:
+        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now(), not experiment)) is not None:
             self._apply_cop_scale(owed)
-        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw):
+        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):
             return refusal
 
         # In the frosting band the shortfall belongs to the defrost derate,
@@ -6024,10 +6033,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             },
         )
 
-    def _dhw_current_hour(self) -> float:
-        now = dt_util.now()
-        return now.hour + now.minute / 60.0
-
     def _dhw_effective_windows(self) -> list[Any]:
         """Demand windows the optimizer is actually planning against."""
         result = self._optimization_result
@@ -6043,13 +6048,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     def _dhw_in_demand_window(self) -> bool:
         """Whether hot water is required right now."""
         return hour_in_windows(
-            self._dhw_current_hour(), self._dhw_effective_windows()
+            _dhw_current_hour(), self._dhw_effective_windows()
         )
 
     def _dhw_next_window_in_hours(self) -> float | None:
         """Hours until the next DHW demand window opens (0 if inside one)."""
         hours = hours_until_next_window(
-            self._dhw_current_hour(), self._dhw_effective_windows()
+            _dhw_current_hour(), self._dhw_effective_windows()
         )
         return round(hours, 2) if hours is not None else None
 
@@ -11098,6 +11103,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             ),
             "heat_pump_on": planned_draw_runs(float(override)),
             "mode": "system_identification",
+            "kind": self._sysid.kind,
             # T6: the experiment's draw is not the plan's -- booking it under
             # the overridden plan's reason would say "cheapest hours" or
             # whatever the plan claimed for this step; the experiment is the
diff --git a/custom_components/heatpump_optimizer/draw_range.py b/custom_components/heatpump_optimizer/draw_range.py
index 409de8e85b..31f668c4a3 100644
--- a/custom_components/heatpump_optimizer/draw_range.py
+++ b/custom_components/heatpump_optimizer/draw_range.py
@@ -112,6 +112,185 @@ CEILING_LAPSE_DAYS = 45.0
 #: AGREE_TOLERANCE above the learned top is an overdraw; this many since the
 #: store's newest sample drop the store: the pump has shown it draws more.
 CEILING_OVERDRAWS = 2
+#: The steady-run map rows (``MapRows``): one per steady run of arbiter
+#: passes holding one written set-point, level, duty and origin. Kept apart
+#: from the window: the latch and the draw-floor judgement read the window's
+#: interval pairs, never a row. Two weeks of half-hour rows, a design
+#: constant not keyed to the configured range.
+MAP_ROWS = 672
+#: A run closes after this long, minutes, and the next pass opens another ...
+SEGMENT_MAX_MIN = 30
+#: ... its first minutes are the response settling, and dropped ...
+SEGMENT_SETTLE_MIN = 3
+#: ... and it is a row only with at least this many steady minutes left.
+SEGMENT_STEADY_MIN = 2
+#: A row's fields, each stored as one comma-separated column string.
+MAP_COLUMNS = (
+    "start_min", "steady_min", "written_c", "gate_c", "ceiling_c", "floor_c",
+    "level_kw", "band_low_kw", "band_high_kw", "heat_ceiling_c", "inlet_mean_c",
+    "inlet_change_k", "outdoor_c", "drawn_mean_kw", "drawn_spread_kw", "origin", "duty",
+)
+#: The two text columns; every other cell is a number or empty (unread).
+_MAP_TEXT = ("origin", "duty")
+
+
+@dataclass(frozen=True)
+class PassRecord:
+    """One arbitration pass under Control on a flow set-point install.
+
+    Built by ``pump_arbiter`` (its ``ArbiterState.last_pass``), which alone
+    decides ``origin``; read here, where it becomes map rows. The map's
+    inputs are the ones ``pump_arbiter._flow_target`` mapped the level on:
+    the level and band, kW, the heat ceiling and the modulation floor, °C.
+    ``None`` is a value not read.
+    """
+
+    at: Any
+    written_c: float
+    gate_c: float
+    ceiling_c: float
+    floor_c: float | None
+    level_kw: float | None
+    band_low_kw: float | None
+    band_high_kw: float | None
+    heat_ceiling_c: float | None
+    inlet_c: float | None
+    drawn_kw: float | None
+    outdoor_c: float | None
+    duty: str | None
+    mode: str | None
+    defrost: bool
+    origin: str
+
+    def run_key(self) -> tuple[Any, ...]:
+        """What one run holds fixed: a change in any of it closes the run."""
+        return (self.written_c, self.level_kw, self.duty, self.origin)
+
+
+def _mean(values: list[float]) -> float | None:
+    return float(np.mean(values)) if values else None
+
+
+def _segment_row(passes: list[PassRecord]) -> tuple[Any, ...] | None:
+    """The map row of one closed run, or ``None`` with too few steady minutes.
+
+    The map's inputs are the first pass's, the one whose write the run held;
+    inlet, draw and outdoor are over the steady passes, those at least
+    ``SEGMENT_SETTLE_MIN`` after the run opened.
+    """
+    first = passes[0]
+    steady = [p for p in passes if (p.at - first.at).total_seconds() >= SEGMENT_SETTLE_MIN * 60.0]
+    if len(steady) < SEGMENT_STEADY_MIN:
+        return None
+    inlets = [p.inlet_c for p in steady if p.inlet_c is not None]
+    drawn = [p.drawn_kw for p in steady if p.drawn_kw is not None]
+    return (
+        int(first.at.timestamp() // 60), len(steady), first.written_c, first.gate_c,
+        first.ceiling_c, first.floor_c, first.level_kw, first.band_low_kw, first.band_high_kw,
+        first.heat_ceiling_c, _mean(inlets), inlets[-1] - inlets[0] if inlets else None,
+        _mean([p.outdoor_c for p in steady if p.outdoor_c is not None]), _mean(drawn),
+        max(drawn) - min(drawn) if drawn else None, first.origin, first.duty,
+    )
+
+
+def _cell(value: Any) -> str:
+    if value is None:
+        return ""
+    if isinstance(value, str):
+        return value
+    return str(int(value)) if isinstance(value, int) else repr(round(float(value), 3))
+
+
+@dataclass
+class MapRows:
+    """The set-point-to-draw map's evidence: closed steady runs as rows.
+
+    ``take_pass`` takes each pass and closes runs on a change of ``PassRecord.run_key``,
+    a defrost pass, a compressor stop (a draw at or under ``RUNNING_FLOOR_KW``,
+    or none read) and ``SEGMENT_MAX_MIN``. A closed run waits in ``closed``
+    for the next ``fold``, which keeps the space-only ones as ``rows`` unless
+    its interval was frozen or distorted. The open run and ``closed`` are not
+    persisted: a reload drops them.
+    """
+
+    rows: Deque[tuple[Any, ...]] = field(default_factory=lambda: deque(maxlen=MAP_ROWS))
+    open: list[PassRecord] = field(default_factory=list)
+    closed: Deque[tuple[Any, ...]] = field(default_factory=lambda: deque(maxlen=MAP_ROWS))
+
+    def _close(self) -> None:
+        row = _segment_row(self.open) if self.open else None
+        if row is not None:
+            self.closed.append(row)
+        self.open = []
+
+    def take_pass(self, rec: PassRecord | None) -> None:
+        """Fold one pass (``None``: no Control pass on a set-point) into the open run."""
+        if rec is None:
+            self._close()
+            return
+        stopped = rec.defrost or rec.drawn_kw is None or rec.drawn_kw <= RUNNING_FLOOR_KW
+        first = self.open[0] if self.open else None
+        if stopped or first is None or first.run_key() != rec.run_key() or (
+                (rec.at - first.at).total_seconds() >= SEGMENT_MAX_MIN * 60.0):
+            self._close()
+        if stopped:
+            return
+        if self.open and int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):
+            return  # one pass a minute: a listener's extra pass weighs nothing
+        self.open.append(rec)
+
+    def commit_runs(self, keep: bool) -> None:
+        """The next fold's commit: the closed space-only runs become rows,
+        unless ``keep`` is False (the interval was frozen or distorted)."""
+        if keep:
+            self.rows.extend(r for r in self.closed if r[-1] == "space")
+        self.closed.clear()
+
+    def as_columns(self) -> dict[str, str]:
+        return {name: ",".join(_cell(r[i]) for r in self.rows) for i, name in enumerate(MAP_COLUMNS)}
+
+
+def _stored_map(data: Any) -> MapRows:
+    """A stored record's map rows; a record without them reads empty.
+
+    Every column is split, an empty string being one unread cell (the record
+    is written only with rows). Columns of unequal length cannot be aligned
+    and are all dropped; a row with an unreadable number is dropped alone.
+    """
+    out = MapRows()
+    raw = data.get("map_rows") if isinstance(data, dict) else None
+    cols = [raw.get(name) if isinstance(raw, dict) else None for name in MAP_COLUMNS]
+    split = [c.split(",") for c in cols if isinstance(c, str)]
+    if len(split) != len(MAP_COLUMNS):
+        return out
+    if len({len(c) for c in split}) != 1:
+        return out
+    for cells in zip(*split):
+        try:
+            out.rows.append(tuple(_map_cell(name, cell) for name, cell in zip(MAP_COLUMNS, cells)))
+        except (ValueError, OverflowError):
+            continue
+    return out
+
+
+def _map_cell(name: str, cell: str) -> Any:
+    """One stored cell: text kept, empty unread, else a finite number (the
+    first two columns whole minutes, never unread); anything else raises
+    ``ValueError``."""
+    if name in _MAP_TEXT:
+        return cell
+    if cell == "" and name not in MAP_COLUMNS[:2]:
+        return None
+    value = int(cell) if name in MAP_COLUMNS[:2] else float(cell)
+    if not np.isfinite(value):
+        raise ValueError(cell)
+    return value
+
+
+def note_pass(draw: "DrawRange | None", rec: PassRecord | None) -> None:
+    """Hand one arbitration pass to ``draw``'s map rows (none: nothing kept)."""
+    if draw is not None:
+        draw.map.take_pass(rec)
 
 
 @dataclass
@@ -159,6 +338,8 @@ class DrawRange:
     floor_kw: float | None = None
     #: Samples appended since ``floor_kw`` last moved, at most ``WINDOW``.
     floor_since: int = 0
+    #: The steady-run map rows: never read by the window or the latch.
+    map: MapRows = field(default_factory=MapRows)
 
     def idle_kw(self) -> float | None:
         """The learned idle draw, or ``None`` while too few readings."""
@@ -370,6 +551,8 @@ class DrawRange:
             "overdraws": self.overdraws,
             "floor_since": self.floor_since,
             **({} if self.floor_kw is None else {"floor_kw": self.floor_kw}),
+            # Absent with no rows: a store that never kept one is unchanged.
+            **({"map_rows": self.map.as_columns()} if self.map.rows else {}),
         }
 
     @classmethod
@@ -385,6 +568,7 @@ class DrawRange:
         out = cls()
         out.ceiling.extend(_stored_ceiling(data))
         out.overdraws = _stored_overdraws(data)
+        out.map = _stored_map(data)
         try:
             lo, hi = (float(v) for v in data["config"])
         except (TypeError, ValueError, OverflowError, KeyError, IndexError):
@@ -690,8 +874,13 @@ def fold(
     ``takes_ceiling`` goes to the ceiling store and NOT to the window, so no
     experiment's draw can trip the window's latch; every other interval
     folds into the window as before.
+
+    First, whatever this interval: the map runs closed since the last fold
+    become rows (``MapRows.commit_runs``) unless ``frozen`` or ``distorted``;
+    they never reach the window.
     """
     space, dhw = split
+    draw.map.commit_runs(keep=not (frozen or distorted))
     if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c <= command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):
         draw.observe_idle(drawn_kw)
     if drawn_kw is None or not is_running_space(
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index 105830d542..4fb47943ca 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -195,6 +195,9 @@ class CurrentAction(TypedDict, total=False):
     boost_space: bool
     boost_dhw: bool
     why_now: WhyNow
+    # The system-identification override's experiment (``sysid.KIND_*``);
+    # absent on every other action.
+    kind: str
 
 
 class DisinfectionSwitch(TypedDict, total=False):
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index d5cfa8a975..930e745350 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -154,7 +154,7 @@ from collections import Counter, deque
 from collections.abc import Awaitable, Callable, Mapping
 from dataclasses import dataclass, field, replace
 from datetime import datetime, timedelta, timezone
-from typing import Any, TypeGuard, cast
+from typing import Any, NamedTuple, TypeGuard, cast
 from weakref import WeakKeyDictionary
 
 from homeassistant.core import callback
@@ -165,7 +165,7 @@ from homeassistant.helpers.event import (
 )
 from homeassistant.util import dt as dt_util
 
-from . import boost, duty_switch, issues, off_restore, pump_mode, quiet_windows
+from . import boost, draw_range, duty_switch, issues, off_restore, pump_mode, quiet_windows
 from .const import (
     CONF_BUFFER_TANK_TEMP_ENTITY,
     CONF_FLOOR_RETURN_TEMP_ENTITY,
@@ -203,6 +203,7 @@ from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_start
 from .drift import utc_elapsed_seconds, utc_shift
 from .drift import stored_instant
 from .store import QuarantiningStore, load_mapping
+from .sysid import KIND_PROBE
 from .thermal_model import (
     configured_flow_heat_c,
     dhw_start_below_c,
@@ -306,6 +307,19 @@ FEEDBACK_STOP_MARGIN_K = 0.2
 #: Past the gate by any amount the entity's step rounding does not absorb,
 #: so the loop's lowest write is the gate plus one entity step (I2).
 FEEDBACK_GATE_CLEAR_K = 0.01
+#: Where a pass's space write came from (:func:`pass_origin`, the one place
+#: it is decided), the origin column of ``draw_range``'s map rows: the plan's
+#: level mapped open-loop; the feedback loop's start-hold (today's target)
+#: and its moved target; a boost's ceiling; the gate of a step that does not
+#: heat; the baseline's hold; the experiment's fit or ceiling probe.
+ORIGIN_PLAN = "plan"
+ORIGIN_FEEDBACK_START = "feedback_start"
+ORIGIN_FEEDBACK = "feedback"
+ORIGIN_BOOST = "boost"
+ORIGIN_GATE = "gate"
+ORIGIN_HOLD = "hold"
+ORIGIN_FIT = "fit"
+ORIGIN_PROBE = "probe"
 
 
 @dataclass(frozen=True)
@@ -383,6 +397,8 @@ class ArbiterState:
     supply_held: bool = False
     #: Until when (UTC) the learners freeze after ``supply_hold`` held a write.
     held_until: datetime | None = None
+    #: The last Control pass on a flow set-point (:func:`_pass_record`); never persisted.
+    last_pass: draw_range.PassRecord | None = None
 
 
 @dataclass(frozen=True)
@@ -412,6 +428,9 @@ class ArbiterInputs:
     #: means is ``freq_control.defrost_interval``'s, and ``None`` is no flag
     #: or no evidence.
     defrosting: bool | None = None
+    #: The running-draw window each pass record is handed to
+    #: (``draw_range.note_pass``); ``None`` keeps none.
+    draw: Any = None
 
 
 _STATES: WeakKeyDictionary[Any, ArbiterState] = WeakKeyDictionary()
@@ -944,20 +963,14 @@ def _flow_target(
     where that is higher.
     """
     if duty in ("space", "both"):
-        p_min, p_max = _band_kw(inp)
-        boost_c = _boost_ceiling_c(inp) if boosted else None
-        heat_c = _heat_ceiling_c(inp.config) if boost_c is None else boost_c
-        floor_c = _or_hold(modulation_floor_flow_c(
-            _flow_inlet_c(inp), _gate_c(inp),
-            start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),
-        ), inp.config)
+        m = _map_inputs(inp, now, boosted)
         return _bounded(
             inp,
             "space_setpoint",
-            flow_setpoint_for_level(_level_kw(inp, now, boost_c is not None), p_min, p_max, heat_c, floor_c),
+            flow_setpoint_for_level(m.level_kw, m.low_kw, m.high_kw, m.heat_c, m.floor_c),
             _gate_floor_c(inp.config),
-            lo=min(floor_c, heat_c),
-            hi=heat_c,
+            lo=min(m.floor_c, m.heat_c),
+            hi=m.heat_c,
         )
     if duty is not None:
         return _gate_c(inp)
@@ -974,6 +987,31 @@ def _flow_target(
     return _bounded(inp, "space_setpoint", hold, _gate_floor_c(inp.config))
 
 
+class MapInputs(NamedTuple):
+    """What a heating step's level is mapped on (:func:`_flow_target`)."""
+
+    level_kw: float | None
+    low_kw: Any
+    high_kw: Any
+    heat_c: float
+    floor_c: float
+    #: The heat ceiling is a live boost's (:func:`_boost_ceiling_c`).
+    boost: bool
+
+
+def _map_inputs(inp: ArbiterInputs, now: datetime, boosted: bool) -> MapInputs:
+    """The level, band, heat ceiling and floor a heating step maps, read once
+    for the write (:func:`_flow_target`) and the pass record (:func:`_pass_record`)."""
+    p_min, p_max = _band_kw(inp)
+    boost_c = _boost_ceiling_c(inp) if boosted else None
+    heat_c = _heat_ceiling_c(inp.config) if boost_c is None else boost_c
+    floor_c = _or_hold(modulation_floor_flow_c(
+        _flow_inlet_c(inp), _gate_c(inp),
+        start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),
+    ), inp.config)
+    return MapInputs(_level_kw(inp, now, boost_c is not None), p_min, p_max, heat_c, floor_c, boost_c is not None)
+
+
 def _feedback_on(inp: ArbiterInputs, duty: str | None, now: datetime, boosts: Any) -> bool:
     """Whether this pass's water target (the caller's water unit) is the loop's.
 
@@ -1300,10 +1338,7 @@ def desired(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) ->
     silent = _silent_target(coord, inp, now)
     duty = _disinfecting(inp, duty)
     mode = _mode_for(inp, duty)
-    # The boost fact is read for a water set-point only: an indoor one maps no
-    # level, and a caller may hand no coordinator for it.
-    space = _space_target(inp, result, now, duty, boosted=_flow_unit(inp.config) and (
-        inp.mode == MODE_BOOST or boost.held_for(coord).active(boost.CHANNEL_SPACE, now)))
+    space = _space_target(inp, result, now, duty, boosted=_boosted(coord, inp, now))
     if _flow_unit(inp.config):
         space = _feedback(state_for(coord), inp, now, space, _feedback_on(inp, duty, now, boost.held_for(coord)))
     if duty == "space" and mode != pump_mode.MODE_HEAT:
@@ -1313,6 +1348,59 @@ def desired(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) ->
     return PumpCommand(mode, dhw, space, silent)
 
 
+def _boosted(coord: Any, inp: ArbiterInputs, now: datetime) -> bool:
+    """A space boost or the global boost mode is live on a water set-point.
+
+    Read for a water set-point only: an indoor one maps no level, and a
+    caller may hand no coordinator for it.
+    """
+    return _flow_unit(inp.config) and (
+        inp.mode == MODE_BOOST or boost.held_for(coord).active(boost.CHANNEL_SPACE, now))
+
+
+def pass_origin(inp: ArbiterInputs, duty: str | None, boost_on: bool, run: FeedbackRun | None, now: datetime) -> str:
+    """Where this pass's space write came from: one of the ``ORIGIN_*``.
+
+    ``duty`` is the duty served, ``boost_on`` whether a boost's ceiling was
+    mapped (:attr:`MapInputs.boost`), ``run`` the feedback loop's run after
+    this pass's :func:`_feedback`. The experiment's action names its kind.
+    """
+    action = inp.action or {}
+    if action.get("mode") == "system_identification":
+        return ORIGIN_PROBE if action.get("kind") == KIND_PROBE else ORIGIN_FIT
+    if duty not in ("space", "both"):
+        return ORIGIN_HOLD if duty is None else ORIGIN_GATE
+    if boost_on:
+        return ORIGIN_BOOST
+    if run is None or not run.running:
+        return ORIGIN_PLAN
+    held_start = utc_elapsed_seconds(now, run.start) < FEEDBACK_START_HOLD.total_seconds()
+    return ORIGIN_FEEDBACK_START if held_start else ORIGIN_FEEDBACK
+
+
+def _note_pass(held: ArbiterState, inp: ArbiterInputs, duty: str | None, boosted: bool, now: datetime) -> None:
+    """Record this Control pass on ``held`` and hand it to the window ``inp.draw``."""
+    held.last_pass = _pass_record(held, inp, duty, boosted, now)
+    draw_range.note_pass(inp.draw, held.last_pass)
+
+
+def _pass_record(held: ArbiterState, inp: ArbiterInputs, duty: str | None, boosted: bool, now: datetime) -> draw_range.PassRecord | None:
+    """This Control pass as ``draw_range`` keeps it, or ``None`` where no
+    flow set-point is held (:func:`_flow_command`). ``boosted``: :func:`_boosted`."""
+    command = _flow_command(inp, held)
+    if command is None:
+        return None
+    m = _map_inputs(inp, now, boosted)
+    return draw_range.PassRecord(
+        now, command.written_c, command.gate_c, command.ceiling_c, m.floor_c,
+        m.level_kw, finite_float(m.low_kw), finite_float(m.high_kw), m.heat_c,
+        _flow_inlet_c(inp), finite_float(inp.measured_power_kw),
+        finite_float(getattr(inp.state, "outdoor_temperature", None)), duty,
+        getattr(_slot_state(inp, "mode"), "state", None), defrost_interval(inp.defrosting),
+        pass_origin(inp, duty, m.boost, held.feedback, now),
+    )
+
+
 def _disinfecting(inp: ArbiterInputs, duty: str | None) -> str | None:
     """A space-only step under a held disinfection is Heating + DHW (module table)."""
     return "both" if duty == "space" and inp.disinfecting else duty
@@ -1887,7 +1975,10 @@ async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: s
         return
     await _adopt(inp, coord.entry, held, now)
     hold(coord, now)
-    await _command(coord, inp, desired(coord, inp, _served(coord, inp, duty, now), now), now)
+    served = _served(coord, inp, duty, now)
+    await _command(coord, inp, desired(coord, inp, served, now), now)
+    boosted = _boosted(coord, inp, now)
+    _note_pass(held, inp, served, boosted, now)
     await _write_night_schedule(coord, inp, now)
 
 
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 1da5d7a64b..523affadf4 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -44,7 +44,7 @@ from .accuracy import HISTORY_LENGTH, LEAD_BUCKETS
 from .comfort_learning import COMFORT_WEIGHT_MAX, COMFORT_WEIGHT_MIN
 from .curve_learning import BIAS_MAX, BIAS_MIN
 from .defrost import DERATE_MAX, DERATE_MIN, STORE_VERSION
-from .draw_range import ASK_FOLLOWS, ASK_IGNORED, ASK_PENDING, RUNNING_FLOOR_KW
+from .draw_range import ASK_FOLLOWS, ASK_IGNORED, ASK_PENDING, MAP_COLUMNS, RUNNING_FLOOR_KW
 from .price_tiles import TILE_NAMES
 from .drift import REFERENCE_PRIOR_COV, STAT_CAP_FACTOR
 from .flow_lift import FLOW_BIAS_CLAMP_K, FLOW_SUPPLY_MAX_C
@@ -328,6 +328,10 @@ _ACCURACY: dict[str, Domain | str] = {
     # An unreadable latch reads disengaged (``from_dict``: ``is True``) and
     # costs only itself; the samples stay.
     "draw/engaged": _FLAG,
+    # R10-DRAW-MAP-EVIDENCE: the steady-run map rows, one comma-separated
+    # string per column, empty where one row's only cell is unread; a record
+    # without them reads empty (draw_range._stored_map).
+    **{f"draw/map_rows/{name}": Domain("text", null=True) for name in MAP_COLUMNS},
     "draw/config/#": Domain("real", whole=_DRAW_KEY),
     # R11-OUTSIDE-HONEST-METERED-FLOOR: the learned floor (absent while
     # unset) and the samples appended since it last moved; a bad cell reads
diff --git a/dev/audit/harnesses/draw_map_rows.py b/dev/audit/harnesses/draw_map_rows.py
new file mode 100644
index 0000000000..7b24c1266a
--- /dev/null
+++ b/dev/audit/harnesses/draw_map_rows.py
@@ -0,0 +1,144 @@
+#!/usr/bin/env python3
+"""R10-DRAW-MAP-EVIDENCE part A: the set-point-to-draw map fitted from the steady-run map rows.
+
+The rows are ``draw_range.MapRows``'s, built here the way production builds
+them: one ``draw_range.PassRecord`` a minute through ``MapRows.take_pass``,
+committed by ``MapRows.commit_runs``, stored by ``DrawRange.as_dict`` and read
+back by ``DrawRange.from_dict`` before the fit. The fit is least squares of a
+row's drawn mean on its lift, written set-point less inlet mean:
+``drawn = offset_kw + gain_kw_per_k * lift``.
+
+    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_map_rows.py --synthetic
+    PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/draw_map_rows.py --bundle BUNDLE.json
+
+``--synthetic`` prints four ``RESULT`` lines on a planted plant (gain 0.3
+kW/K, offset 0.4 kW, inlets 30 to 40 °C, five held set-points each):
+
+* ``open_loop``: the rows of held set-points recover the planted gain and
+  offset;
+* ``shuffled`` (null): the same rows with their set-points permuted fall to a
+  flat fit -- the recovery is the rows' pairing, not the fit;
+* ``closed_loop`` (null): rows whose set-point a loop moved while the draw sat
+  on the plan's level give a slope far from the planted one -- why the origin
+  column must separate them;
+* ``store``: the stored bytes of the rows at ``MAP_ROWS`` (compact JSON, as
+  Home Assistant's store writes), and those bytes times the 48 saves a day
+  of the default cycle (the accuracy store saves every cycle).
+
+``--bundle`` reads a diagnostics download (``data.debug.stores``, the
+accuracy store's ``draw`` record) and prints its rows by origin, the fit on
+the open-loop ones (``fit=none`` under three distinct set-points), and the
+accuracy store's own compact bytes. A bundle from before the rows reads
+``rows=0``. Counts only: no row is printed.
+"""
+from __future__ import annotations
+
+import json
+import random
+import sys
+from datetime import datetime, timedelta, timezone
+
+from heatpump_optimizer import draw_range as dr
+
+#: Origins whose write no loop moved against the draw: the map's evidence.
+OPEN_LOOP = ("plan", "fit", "probe", "boost")
+GAIN, OFFSET = 0.3, 0.4
+T0 = datetime(2026, 1, 12, 0, 0, tzinfo=timezone.utc)
+SAVES_PER_DAY = 48
+
+
+def fit(rows: list[tuple]) -> tuple[float, float, int] | None:
+    """``(gain, offset, distinct set-points)`` or ``None`` under three."""
+    pts = [(r[2] - r[10], r[13]) for r in rows if r[10] is not None and r[13] is not None]
+    if len({r[2] for r in rows}) < 3 or len(pts) < 3:
+        return None
+    n = len(pts)
+    mx, my = sum(x for x, _ in pts) / n, sum(y for _, y in pts) / n
+    sxx = sum((x - mx) ** 2 for x, _ in pts)
+    if sxx <= 0.0:
+        return None
+    gain = sum((x - mx) * (y - my) for x, y in pts) / sxx
+    return gain, my - gain * mx, len({r[2] for r in rows})
+
+
+def _runs(closed_loop: bool, seed: int = 3) -> dr.DrawRange:
+    rng = random.Random(seed)
+    draw = dr.DrawRange()
+    minute = 0
+    for inlet0 in (30.0, 32.5, 35.0, 37.5, 40.0):
+        for lift in (1.0, 2.0, 3.0, 4.5, 6.0):
+            level = OFFSET + GAIN * lift
+            # A closed loop holds the plan's draw and walks the set-point,
+            # held for 6-minute stretches the run rule can keep.
+            walk = [round(inlet0 + 3.0 + rng.uniform(-2.0, 2.0), 1) for _ in range(4)]
+            for m in range(24 if closed_loop else 20):
+                inlet = inlet0 + 0.02 * m
+                if closed_loop:
+                    written, origin = walk[m // 6], "feedback"
+                    drawn = 1.3 + rng.uniform(-0.03, 0.03)
+                else:
+                    written, origin = inlet0 + lift, "plan"
+                    drawn = OFFSET + GAIN * (written - inlet) + rng.uniform(-0.03, 0.03)
+                draw.map.take_pass(dr.PassRecord(
+                    T0 + timedelta(minutes=minute), written, 25.0, 45.0, inlet0 + 0.5, level,
+                    0.5, 4.0, 45.0, inlet, drawn, 4.0, "space", "heat", False, origin))
+                minute += 1
+            draw.map.take_pass(None)
+            minute += 5
+    draw.map.commit_runs(True)
+    return dr.DrawRange.from_dict(json.loads(json.dumps(draw.as_dict())))
+
+
+def _line(label: str, rows: list[tuple]) -> str:
+    got = fit(rows)
+    if got is None:
+        return f"RESULT {label} rows={len(rows)} fit=none"
+    gain, offset, distinct = got
+    return f"RESULT {label} rows={len(rows)} distinct_c={distinct} gain_kw_per_k={gain:.3f} offset_kw={offset:.3f}"
+
+
+def synthetic() -> None:
+    rows = list(_runs(False).map.rows)
+    print(_line("open_loop", rows) + f" planted_gain={GAIN} planted_offset={OFFSET}")
+    written = [r[2] for r in rows]
+    random.Random(5).shuffle(written)
+    print(_line("shuffled", [(r[0], r[1], w) + r[3:] for r, w in zip(rows, written)]))
+    print(_line("closed_loop", list(_runs(True).map.rows)))
+    full = dr.DrawRange()
+    template = rows[0]
+    full.map.rows.extend((template[0] + 30 * i,) + template[1:] for i in range(dr.MAP_ROWS))
+    empty = json.dumps(dr.DrawRange().as_dict(), separators=(",", ":"))
+    capped = json.dumps(full.as_dict(), separators=(",", ":"))
+    added = len(capped) - len(empty)
+    print(f"RESULT store rows={len(full.map.rows)} draw_record_bytes_empty={len(empty)} "
+          f"draw_record_bytes_capped={len(capped)} added_bytes={added} added_bytes_per_day={added * SAVES_PER_DAY}")
+
+
+def bundle(path: str) -> None:
+    with open(path, encoding="utf-8") as fh:
+        data = json.load(fh)
+    stores = (((data.get("data") or {}).get("debug") or {}).get("stores")) or {}
+    acc = next((v for k, v in stores.items() if k.endswith("_accuracy") and isinstance(v, dict)), None)
+    if acc is None:
+        print("RESULT bundle accuracy_store=absent")
+        return
+    draw = dr.DrawRange.from_dict((acc.get("accuracy") or {}).get("draw") or {})
+    rows = list(draw.map.rows)
+    origins: dict[str, int] = {}
+    for r in rows:
+        origins[r[15]] = origins.get(r[15], 0) + 1
+    size = len(json.dumps(acc, separators=(",", ":")))
+    print(f"RESULT bundle accuracy_store_bytes={size} bytes_per_day={size * SAVES_PER_DAY} "
+          f"origins={dict(sorted(origins.items()))}")
+    print(_line("bundle_open_loop", [r for r in rows if r[15] in OPEN_LOOP]))
+
+
+if __name__ == "__main__":
+    args = sys.argv[1:]
+    if args[:1] == ["--synthetic"]:
+        synthetic()
+    elif args[:1] == ["--bundle"] and len(args) == 2:
+        bundle(args[1])
+    else:
+        print(__doc__)
+        sys.exit(2)
diff --git a/dev/programme/delivery/3737.md b/dev/programme/delivery/3737.md
new file mode 100644
index 0000000000..ad60a38cb7
--- /dev/null
+++ b/dev/programme/delivery/3737.md
@@ -0,0 +1 @@
+- [#3737](https://github.com/tvofi/heatpump_optimizer/pull/3737) — **open**, R11-CARRY-DRAWMAP: r11 carry drawmap (R11-CARRY-DRAWMAP)
diff --git a/tests/closures.json b/tests/closures.json
index ec631afefa..629b17ac90 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4319,6 +4319,7 @@
    "dev/audit/harnesses/dependabot_stale_hash.py",
    "dev/audit/harnesses/drain_admission_probe.py",
    "dev/audit/harnesses/draw_map_linearity.py",
+   "dev/audit/harnesses/draw_map_rows.py",
    "dev/audit/harnesses/draw_range_evidence.py",
    "dev/audit/harnesses/dual_path.py",
    "dev/audit/harnesses/early_cutoff_closed_loop.py",
diff --git a/tests/features.py b/tests/features.py
index 0868f72811..a70fbe0906 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -96912,4 +96912,578 @@ R.check(
 )
 
 
+# --- R10-DRAW-MAP-EVIDENCE part A (design/R10-DRAW-MAP-EVIDENCE at 9aa450f5,
+# approved at design-verdict f10dd418). Each Control pass on a flow set-point
+# is recorded with where its write came from (``pump_arbiter.pass_origin``,
+# the one place that decides it); steady runs of passes become map rows kept
+# beside the running-draw window and never in it, stored as one string per
+# column; and an experiment's interval is no efficiency reading for the COP
+# learner (``MeasuredCop.judge_floor``). Synthetic fixtures throughout.
+R.section("R10-DRAW-MAP-EVIDENCE part A: map rows and the learner exclusion")
+import asyncio as _mr_aio  # noqa: E402
+from heatpump_optimizer import draw_range as _mr_dr  # noqa: E402
+from heatpump_optimizer import heat_energy as _mr_he  # noqa: E402
+from heatpump_optimizer import coordinator as _mr_cm  # noqa: E402
+from heatpump_optimizer import pump_arbiter as _mr_pa  # noqa: E402
+from heatpump_optimizer import store as _mr_store  # noqa: E402
+from heatpump_optimizer.accuracy import (  # noqa: E402
+    COP_REFUSED_OFF_ASK as _MR_OFF,
+    COP_REFUSED_SPAN_OPEN as _MR_OPEN,
+    MeasuredCop as _MR_MC,
+)
+from dataclasses import replace as _mr_dc_replace  # noqa: E402
+from heatpump_optimizer.sysid import KIND_FIT as _MR_FIT, KIND_PROBE as _MR_PROBE  # noqa: E402
+
+_MR_T0 = datetime(2026, 1, 12, 8, 0, tzinfo=timezone.utc)
+_MR_MIN0 = int(_MR_T0.timestamp() // 60)
+
+
+def _mr_pass(minute, written=35.0, drawn=2.0, *, level=2.0, duty="space", origin="plan",
+             inlet=30.0, defrost=False):
+    return _mr_dr.PassRecord(
+        _MR_T0 + timedelta(minutes=minute), written, 25.0, 45.0, 31.0, level, 0.5, 4.0, 45.0,
+        inlet, drawn, 4.0, duty, "heat", defrost, origin)
+
+
+def _mr_rows(passes, keep=True):
+    rows = _mr_dr.MapRows()
+    for p in passes:
+        rows.take_pass(p)
+    rows.take_pass(None)
+    rows.commit_runs(keep)
+    return list(rows.rows)
+
+
+# Segments: the first SEGMENT_SETTLE_MIN minutes dropped, at least
+# SEGMENT_STEADY_MIN steady minutes, closed at SEGMENT_MAX_MIN.
+_mr_ten = _mr_rows([_mr_pass(m, inlet=30.0 + 0.1 * m, drawn=2.0 + 0.1 * (m % 2)) for m in range(10)])
+R.check(
+    "a ten-minute run at one set-point is one row: started at its first pass, 7 "
+    "steady minutes (3 to 9), its map inputs the first pass's, inlet mean and "
+    "change and draw mean and spread over the steady minutes",
+    len(_mr_ten) == 1 and _mr_ten[0][:2] == (_MR_MIN0, 7)
+    and _mr_ten[0][2:10] == (35.0, 25.0, 45.0, 31.0, 2.0, 0.5, 4.0, 45.0)
+    and abs(_mr_ten[0][10] - 30.6) < 1e-9 and abs(_mr_ten[0][11] - 0.6) < 1e-9
+    and _mr_ten[0][12] == 4.0 and abs(_mr_ten[0][13] - (2.0 + 0.1 * 4 / 7)) < 1e-9
+    and abs(_mr_ten[0][14] - 0.1) < 1e-9 and _mr_ten[0][15:] == ("plan", "space"),
+    f"{_mr_ten}",
+)
+R.check(
+    "a run of five passes keeps two steady minutes and is a row; one of four "
+    "keeps one and is none",
+    [len(_mr_rows([_mr_pass(m) for m in range(n)])) for n in (4, 5)] == [0, 1]
+    and _mr_rows([_mr_pass(m) for m in range(5)])[0][1] == 2,
+)
+R.check(
+    "a forty-minute run closes at thirty minutes and the next pass opens a new "
+    "run: steady minutes 27 and 7",
+    [r[1] for r in _mr_rows([_mr_pass(m) for m in range(40)])] == [27, 7],
+)
+_mr_cut = {
+    "written": [_mr_pass(m, written=35.0 if m < 10 else 36.0) for m in range(20)],
+    "level": [_mr_pass(m, level=2.0 if m < 10 else 2.5) for m in range(20)],
+    "origin": [_mr_pass(m, origin="plan" if m < 10 else "feedback") for m in range(20)],
+    "duty": [_mr_pass(m, duty="space" if m < 10 else "both") for m in range(20)],
+}
+R.check(
+    "a change of written set-point, level, origin or duty closes the run (the "
+    "duty case keeps only its space-only run)",
+    {k: [r[1] for r in _mr_rows(v)] for k, v in _mr_cut.items()}
+    == {"written": [7, 7], "level": [7, 7], "origin": [7, 7], "duty": [7]},
+    f"{ {k: [r[:2] for r in _mr_rows(v)] for k, v in _mr_cut.items()} }",
+)
+_mr_stops = {
+    "defrost": [_mr_pass(m, defrost=m == 10) for m in range(20)],
+    "stop": [_mr_pass(m, drawn=0.25 if m == 10 else 2.0) for m in range(20)],
+    "unread": [_mr_pass(m, drawn=None if m == 10 else 2.0) for m in range(20)],
+}
+R.check(
+    "a defrost pass, a draw at RUNNING_FLOOR_KW and an unread draw each close the "
+    "run and join none: steady minutes 7 and 6 (minutes 0-9, 11-19)",
+    all([r[1] for r in _mr_rows(v)] == [7, 6] for v in _mr_stops.values()),
+    f"{ {k: [r[1] for r in _mr_rows(v)] for k, v in _mr_stops.items()} }",
+)
+_mr_dup = [_mr_pass(m) for m in range(10)]
+_mr_dup.insert(6, _mr_dc_replace(_mr_dup[5], at=_mr_dup[5].at + timedelta(seconds=30), drawn_kw=9.0))
+R.check(
+    "a second pass inside a minute (a listener's) weighs nothing",
+    _mr_rows(_mr_dup) == _mr_rows([_mr_pass(m) for m in range(10)]),
+)
+_mr_mixed = _mr_dr.MapRows()
+for _mr_p in _mr_cut["duty"]:
+    _mr_mixed.take_pass(_mr_p)
+_mr_mixed.take_pass(None)
+_mr_mixed_closed = len(_mr_mixed.closed)
+_mr_mixed.commit_runs(True)
+_mr_frozen = _mr_dr.MapRows()
+for _mr_p in _mr_cut["duty"]:
+    _mr_frozen.take_pass(_mr_p)
+_mr_frozen.take_pass(None)
+_mr_frozen.commit_runs(False)
+R.check(
+    "the fold commits the closed space-only runs and clears the rest; a frozen "
+    "or distorted interval commits none",
+    _mr_mixed_closed == 2 and [r[-1] for r in _mr_mixed.rows] == ["space"] and not _mr_mixed.closed
+    and not _mr_frozen.rows and not _mr_frozen.closed,
+    f"{list(_mr_mixed.rows)} / {list(_mr_frozen.rows)}",
+)
+_mr_cap = _mr_dr.MapRows()
+_mr_cap.closed.extend((_MR_MIN0 + i, 2) + (None,) * 13 + ("plan", "space") for i in range(700))
+_mr_cap.commit_runs(True)
+R.check(
+    "the rows are capped at MAP_ROWS (672), oldest dropped",
+    _mr_dr.MAP_ROWS == 672 and len(_mr_cap.rows) == 672 and _mr_cap.rows[0][0] == _MR_MIN0 + 28,
+    f"{len(_mr_cap.rows)}",
+)
+
+# Storage: one string per column, read back without a migration.
+_mr_win = _mr_dr.DrawRange()
+_mr_win.map.rows.append((_MR_MIN0, 2) + (None,) * 13 + ("hold", "space"))
+_mr_win.map.rows.extend(_mr_rows([_mr_pass(m, inlet=30.0 + 0.25 * m) for m in range(25)])
+                        + _mr_rows([_mr_pass(m, written=40.5, origin="probe") for m in range(8)]))
+_mr_doc = _mr_win.as_dict()
+_mr_back = _mr_dr.DrawRange.from_dict(_mr_doc)
+R.check(
+    "the rows are stored as one comma-separated string per column, every column, "
+    "and read back as the same rows",
+    tuple(_mr_doc["map_rows"]) == _mr_dr.MAP_COLUMNS
+    and all(isinstance(v, str) for v in _mr_doc["map_rows"].values())
+    and _mr_doc["map_rows"]["origin"] == "hold,plan,probe"
+    and list(_mr_back.map.rows) == list(_mr_win.map.rows),
+    f"{_mr_doc['map_rows']} / {list(_mr_back.map.rows)}",
+)
+_mr_plain = _mr_dr.DrawRange()
+_mr_plain.observe(2.0, 2.0, 0.5, 4.0, (35.0, 45.0))
+R.check(
+    "with no rows the record keeps no map key, so a store that never held one is "
+    "unchanged; a record stored before the rows reads empty, its window intact",
+    "map_rows" not in _mr_plain.as_dict()
+    and not _mr_dr.DrawRange.from_dict(_mr_plain.as_dict()).map.rows
+    and list(_mr_dr.DrawRange.from_dict(_mr_plain.as_dict()).samples) == [(2.0, 2.0)],
+)
+_mr_bad = {k: v for k, v in _mr_doc["map_rows"].items()}
+_mr_bad["written_c"] = "x," + _mr_bad["written_c"].split(",", 1)[1]
+_mr_nan = dict(_mr_doc["map_rows"], drawn_mean_kw="nan," + _mr_doc["map_rows"]["drawn_mean_kw"].split(",", 1)[1])
+_mr_short = dict(_mr_doc["map_rows"], gate_c="25.0")
+R.check(
+    "an unreadable or non-finite cell drops its row alone; columns of unequal "
+    "length cannot be aligned and drop every row; a column that is not a string "
+    "drops every row",
+    [r[15] for r in _mr_dr.DrawRange.from_dict({"map_rows": _mr_bad}).map.rows] == ["plan", "probe"]
+    and [r[15] for r in _mr_dr.DrawRange.from_dict({"map_rows": _mr_nan}).map.rows] == ["plan", "probe"]
+    and not _mr_dr.DrawRange.from_dict({"map_rows": _mr_short}).map.rows
+    and not _mr_dr.DrawRange.from_dict({"map_rows": dict(_mr_doc["map_rows"], duty=None)}).map.rows
+    and not _mr_dr.DrawRange.from_dict({"map_rows": "x"}).map.rows
+    and not _mr_dr.DrawRange.from_dict({"map_rows": dict(_mr_doc["map_rows"], duty=["space"] * 3)}).map.rows,
+)
+_mr_round = _mr_dr.MapRows()
+_mr_round.rows.append((_MR_MIN0, 2, 31.6875) + (None,) * 12 + ("plan", "space"))
+R.check(
+    "a number is stored to three decimals",
+    _mr_round.as_columns()["written_c"] == "31.688",
+    f"{_mr_round.as_columns()['written_c']}",
+)
+R.check(
+    "store.DOMAINS declares every column leaf, an empty one included (null: an "
+    "undeclared column is reported, as its key and its value)",
+    _mr_store.off_domain("hpo_accuracy", {"accuracy": {"draw": _mr_doc}}) == []
+    and _mr_store.off_domain("hpo_accuracy", {"accuracy": {"draw": {
+        **_mr_doc, "map_rows": dict(_mr_doc["map_rows"], bogus="1")}}}) == ["accuracy/draw/map_rows/bogus"] * 2,
+    f"{_mr_store.off_domain('hpo_accuracy', {'accuracy': {'draw': _mr_doc}})}",
+)
+_mr_one_row = _mr_dr.DrawRange()
+_mr_one_row.map.rows.append((_MR_MIN0, 2) + (None,) * 13 + ("hold", "space"))
+R.check(
+    "a single row with unread cells stores empty column strings, which the "
+    "domain admits",
+    _mr_one_row.as_dict()["map_rows"]["written_c"] == ""
+    and _mr_store.off_domain("hpo_accuracy", {"accuracy": {"draw": _mr_one_row.as_dict()}}) == [],
+)
+_mr_a = [_mr_pass(m, inlet=None) for m in range(6)]
+_mr_b = [_mr_pass(m, written=40.0, inlet=inl) for m, inl in ((6, None), (7, None), (8, 31.0), (9, 31.0), (10, 31.0))]
+_mr_no_inlet = [_mr_rows(_mr_a), _mr_rows(_mr_a + [_mr_dc_replace(p, inlet_c=None) for p in _mr_b]), _mr_rows(_mr_a + _mr_b)]
+
+
+def _mr_reload(rows):
+    held = _mr_dr.DrawRange()
+    held.map.rows.extend(rows)
+    return list(_mr_dr.DrawRange.from_dict(held.as_dict()).map.rows)
+
+
+R.check(
+    "an unread cell is a stored value: a single row with unread cells, a column "
+    "unread in every row (no inlet sensor) and one row unread among read ones "
+    "each read back as the same rows",
+    _mr_reload(_mr_one_row.map.rows) == list(_mr_one_row.map.rows)
+    and [len(r) for r in _mr_no_inlet] == [1, 2, 2]
+    and [r[-1][10] is None for r in _mr_no_inlet] == [True, True, False]
+    and all(r[0][10] is None for r in _mr_no_inlet)
+    and all(_mr_reload(r) == r for r in _mr_no_inlet),
+    f"{[_mr_reload(r) for r in _mr_no_inlet]} / {_mr_reload(_mr_one_row.map.rows)}",
+)
+R.check(
+    "an unread start or steady minute is a bad cell and drops its row alone; a "
+    "record of empty columns holds no row",
+    [r[15] for r in _mr_dr.DrawRange.from_dict({"map_rows": dict(
+        _mr_doc["map_rows"], start_min="," + _mr_doc["map_rows"]["start_min"].split(",", 1)[1])}).map.rows]
+    == ["plan", "probe"]
+    and [r[15] for r in _mr_dr.DrawRange.from_dict({"map_rows": dict(
+        _mr_doc["map_rows"], steady_min="," + _mr_doc["map_rows"]["steady_min"].split(",", 1)[1])}).map.rows]
+    == ["plan", "probe"]
+    and not _mr_dr.DrawRange.from_dict({"map_rows": dict.fromkeys(_mr_dr.MAP_COLUMNS, "")}).map.rows,
+)
+
+
+# The window is untouched: the same intervals folded with and without map
+# rows leave every reader of the window identical.
+class _MrParams:
+    min_electrical_power, max_electrical_power, flow_lift_power_floor_kw = 0.5, 4.0, 0.4
+
+
+# The fold's own wiring of the exclusion: each flag alone, through draw_range.fold.
+def _mr_fold_flags(frozen, distorted):
+    draw = _mr_dr.DrawRange()
+    for m in range(10):
+        _mr_dr.note_pass(draw, _mr_pass(m))
+    _mr_dr.note_pass(draw, None)
+    _mr_dr.fold(draw, 2.0, (2.0, 0.0), _MrParams(), frozen=frozen, distorted=distorted,
+                defrost=False, command=_mr_pa.FlowCommand(35.0, 25.0, 45.0))
+    return len(draw.map.rows), len(draw.map.closed)
+
+
+_mr_flag_rows = {f: _mr_fold_flags(*f) for f in ((False, False), (True, False), (False, True), (True, True))}
+R.check(
+    "fold commits a closed space run as a row only when the interval is neither "
+    "frozen nor distorted: frozen alone, distorted alone and both commit none and "
+    "clear the closed runs (control: neither flag commits one)",
+    _mr_flag_rows == {(False, False): (1, 0), (True, False): (0, 0), (False, True): (0, 0), (True, True): (0, 0)},
+    f"{_mr_flag_rows}",
+)
+
+
+def _mr_fold_run(with_rows):
+    draw = _mr_dr.DrawRange()
+    for i in range(240):
+        ask = (0.5, 1.6, 2.4, 3.2)[i % 4]  # asks at the configured minimum draw 0.8: the floor moves
+        drawn = 0.8 if i % 4 == 0 else ask * 1.1
+        cmd = _mr_pa.FlowCommand(30.0 + 2 * (i % 4), 25.0, 45.0)
+        if with_rows:
+            for m in range(30):
+                _mr_dr.note_pass(draw, _mr_pass(30 * i + m, written=cmd.written_c, level=ask, drawn=drawn))
+        _mr_dr.fold(draw, drawn if i % 9 else 0.1, (ask, 0.0), _MrParams(), frozen=False,
+                    distorted=False, defrost=False, command=cmd)
+    return draw
+
+
+_mr_with, _mr_without = _mr_fold_run(True), _mr_fold_run(False)
+_MR_CAP = __import__("heatpump_optimizer.thermal_model", fromlist=["InstallCapability"]).InstallCapability(
+    frozenset({"power"}), True, False)
+_mr_band = lambda d: _mr_dr.solve_band(d, _MrParams(), _MR_CAP, 0.0, applies_floor=True)  # noqa: E731
+_mr_readers = lambda d: (list(d.samples), list(d.commands), d.engaged, list(d.idle), list(d.ceiling),  # noqa: E731
+                         _mr_dr.ask_evidence(d), _mr_dr.power_floor_kw(d, _MrParams()), d.observed(),
+                         d.floor_kw, d.floor_since, _mr_band(d),
+                         {k: v for k, v in d.as_dict().items() if k != "map_rows"})
+R.check(
+    "null: DrawRange.samples, engaged, ask_evidence, the floor, the learned floor and its "
+    "count, the solve band's bottom and the stored window are identical with and without map "
+    "rows, and the rows were kept",
+    _mr_readers(_mr_with) == _mr_readers(_mr_without) and len(_mr_with.map.rows) > 0
+    and not _mr_without.map.rows and _mr_without.floor_kw is not None
+    and _mr_band(_mr_without).min_source != "configured",
+    f"rows {len(_mr_with.map.rows)} floor {_mr_with.floor_kw} since {_mr_with.floor_since} "
+    f"band min {_mr_band(_mr_with).min_kw} {_mr_band(_mr_with).min_source}",
+)
+
+# Origin: decided once, in pump_arbiter.pass_origin.
+_mr_in = _FbCoord().arbiter_inputs()
+_mr_exp = lambda kind: _mr_dc_replace(_mr_in, action={"mode": "system_identification", "power": 2.0, **kind})  # noqa: E731
+_mr_now = _MR_T0 + timedelta(hours=1)
+_mr_run_at = lambda s, running=True: _mr_dc_setrun(  # noqa: E731
+    _mr_pa.FeedbackRun(_mr_now - timedelta(seconds=s), 30.0, _mr_now), running)
+
+
+def _mr_dc_setrun(run, running):
+    run.running = running
+    return run
+
+
+_MR_HOLD_S = _mr_pa.FEEDBACK_START_HOLD.total_seconds()
+_mr_origins = [
+    _mr_pa.pass_origin(_mr_exp({"kind": _MR_PROBE}), "space", False, None, _mr_now),
+    _mr_pa.pass_origin(_mr_exp({"kind": _MR_FIT}), "space", True, _mr_run_at(600), _mr_now),
+    _mr_pa.pass_origin(_mr_exp({}), "idle", False, None, _mr_now),
+    _mr_pa.pass_origin(_mr_in, None, False, None, _mr_now),
+    _mr_pa.pass_origin(_mr_in, "dhw", True, None, _mr_now),
+    _mr_pa.pass_origin(_mr_in, "idle", False, None, _mr_now),
+    _mr_pa.pass_origin(_mr_in, "space", True, _mr_run_at(600), _mr_now),
+    _mr_pa.pass_origin(_mr_in, "both", False, None, _mr_now),
+    _mr_pa.pass_origin(_mr_in, "space", False, _mr_run_at(600, False), _mr_now),
+    _mr_pa.pass_origin(_mr_in, "space", False, _mr_run_at(_MR_HOLD_S - 1), _mr_now),
+    _mr_pa.pass_origin(_mr_in, "space", False, _mr_run_at(_MR_HOLD_S), _mr_now),
+]
+R.check(
+    "pass_origin: the experiment's kind first (probe, fit, and fit with no "
+    "kind); the baseline holds; a step that does not heat writes the gate; a "
+    "boost's ceiling; the plan open-loop with no running loop; the loop's start "
+    "hold until FEEDBACK_START_HOLD, then its moved target",
+    _mr_origins == ["probe", "fit", "fit", "hold", "gate", "gate", "boost", "plan", "plan",
+                    "feedback_start", "feedback"],
+    f"{_mr_origins}",
+)
+
+
+# Through the production _arbitrate: the feedback option on gives the loop's
+# origins, off gives none (the design's origin null).
+def _mr_sim(**kw):
+    seen = []
+    note, inputs = _mr_dr.note_pass, _FbCoord.arbiter_inputs
+
+    def _note(draw, rec):
+        seen.append(rec)
+        note(draw, rec)
+
+    def _inputs(self):
+        if self.__dict__.get("draw") is None:
+            self.draw = _mr_dr.DrawRange()
+        return _mr_dc_replace(inputs(self), draw=self.draw)
+
+    _mr_dr.note_pass, _FbCoord.arbiter_inputs = _note, _inputs
+    try:
+        sim = _fb_sim(minutes=90, **kw)
+    finally:
+        _mr_dr.note_pass, _FbCoord.arbiter_inputs = note, inputs
+    return sim, seen
+
+
+_mr_on, _mr_on_seen = _mr_sim()
+_mr_off, _mr_off_seen = _mr_sim(feedback=False)
+_mr_on_o = {r.origin for r in _mr_on_seen if r is not None}
+_mr_off_o = {r.origin for r in _mr_off_seen if r is not None}
+_mr_last = _mr_pa.state_for(_mr_on["coord"]).last_pass
+R.check(
+    "with the feedback option on the passes carry the loop's start hold and "
+    "moved target; off, none does and the plan's open-loop write is the origin; "
+    "the last pass is on the arbiter state, its written set-point the held one, "
+    "and closed runs reached the coordinator's window",
+    {"feedback_start", "feedback"} <= _mr_on_o and not _mr_off_o & {"feedback_start", "feedback"}
+    and "plan" in _mr_off_o
+    and _mr_last is _mr_on_seen[-1]
+    and _mr_last.written_c == _mr_pa.state_for(_mr_on["coord"]).written["space_setpoint"][0]
+    and len(_mr_off["coord"].draw.map.closed) > 0,
+    f"on {_mr_on_o} off {_mr_off_o} closed {len(_mr_off['coord'].draw.map.closed)}",
+)
+_mr_boost_in = _mr_dc_replace(_mr_in, mode=_mr_pa.MODE_BOOST)
+_mr_indoor = _FbCoord()
+_mr_indoor._config = EntryConfig.from_mapping({**_mr_indoor._config.raw, "space_setpoint_unit": "indoor"})
+R.check(
+    "the boost fact (_boosted): the global boost mode on a water set-point is "
+    "live, outside it with no boost set it is not, and an indoor set-point is "
+    "never boosted",
+    _mr_pa._boosted(_FbCoord(), _mr_boost_in, _mr_now) is True
+    and _mr_pa._boosted(_FbCoord(), _mr_in, _mr_now) is False
+    and _mr_pa._boosted(_mr_indoor, _mr_dc_replace(_mr_indoor.arbiter_inputs(), mode=_mr_pa.MODE_BOOST), _mr_now)
+    is False,
+)
+_mr_fresh = _FbCoord()
+R.check(
+    "a fresh arbiter state holds no pass record",
+    _mr_pa.ArbiterState().last_pass is None,
+)
+R.check(
+    "no pass record where no flow set-point is held (nothing written yet)",
+    _mr_pa._pass_record(_mr_pa.state_for(_mr_fresh), _mr_fresh.arbiter_inputs(), "space", False,
+                        _MR_T0) is None,
+)
+
+# The learner exclusion [R3]: the first judgement refuses an experiment's
+# interval with the existing literal, before any ratio is walked.
+_mr_p = _cf_coord()._thermal_params
+R.check(
+    "judge_floor: an experiment interval is draw_off_ask whatever its figures, "
+    "with or without a per-cycle draw; a plan interval with no draw is judged on "
+    "nothing and passes",
+    _MR_MC.judge_floor(2.0, 2.0, _mr_p, None, True) == _MR_OFF
+    and _MR_MC.judge_floor(2.0, None, _mr_p, None, True) == _MR_OFF
+    and _MR_MC.judge_floor(2.0, 2.0, _mr_p, None, False) is None
+    and _MR_MC.judge_floor(2.0, None, _mr_p, None) is None,
+)
+_mr_floor = _mr_dr.power_floor_kw(None, _mr_p)
+R.check(
+    "judge_floor: a plan interval drawing under the duty floor still reads "
+    "duty_floor, and one drawing exactly the floor passes",
+    _MR_MC.judge_floor(2.0, 0.5 * _mr_floor, _mr_p, None) == "duty_floor"
+    and _MR_MC.judge_floor(_mr_floor, _mr_floor, _mr_p, None) is None,
+    f"floor {_mr_floor}",
+)
+_mr_live = _cf_coord()
+R.check(
+    "the coordinator hands its own running-draw window to the arbiter on every "
+    "pass (ArbiterInputs.draw)",
+    _mr_live.arbiter_inputs().draw is _mr_live._accuracy.draw,
+)
+# The sysid override names its kind on the action (moved from part B: the
+# arbiter's origin reads it and cannot reach the coordinator's _sysid).
+_mr_si = _SysIdHost(PumpSignals())
+_mr_si._sysid.phase = _SysIdModule.PHASE_STEP
+_sysid_cycle(_mr_si, np.full(48, 0.2))
+R.check(
+    "the experiment's override action carries its kind",
+    _mr_si._current_action.get("mode") == "system_identification"
+    and _mr_si._current_action.get("kind") == _mr_si._sysid.kind == _MR_FIT,
+    f"{_mr_si._current_action}",
+)
+# The hot-water window clock moved to module level unchanged: 13:30 local is
+# 13.5, inside a 13:00-14:00 window, and 30 minutes before a 14:00 one.
+_mr_hw = _cf_coord()
+_mr_clock = _mr_cm.dt_util.now
+_mr_cm.dt_util.now = lambda: datetime(2026, 1, 12, 13, 30, tzinfo=timezone.utc)
+try:
+    _mr_hw._optimization_result = __import__("types").SimpleNamespace(predictive_info={"dhw_windows": "13:00-14:00"})
+    _mr_hw_in = (_mr_cm._dhw_current_hour(), _mr_hw._dhw_in_demand_window())
+    _mr_hw._optimization_result.predictive_info = {"dhw_windows": "14:00-15:00"}
+    _mr_hw_next = (_mr_hw._dhw_in_demand_window(), _mr_hw._dhw_next_window_in_hours())
+finally:
+    _mr_cm.dt_util.now = _mr_clock
+R.check(
+    "the hot-water windows read the local hour: 13:30 is 13.5, inside "
+    "13:00-14:00, outside 14:00-15:00 and 0.5 h before it",
+    _mr_hw_in == (13.5, True) and _mr_hw_next == (False, 0.5),
+    f"{_mr_hw_in} {_mr_hw_next}",
+)
+_MR_SYSID = {"mode": "system_identification", "kind": _MR_PROBE}
+
+
+def _mr_cop(coord, cycles, freeze=()):
+    """``cycles`` of (action extra, asked kW, drawn kW) on ``coord``; the
+    learner state the exclusion must leave as a frozen cycle would."""
+    _cf_learn(coord, 2.0, 0)  # the window's follow evidence, as _cf_learn builds it
+    for i, (extra, asked, drawn) in enumerate(cycles):
+        coord._current_action = {"power": asked, "dhw_power": 0.0, **extra}
+        coord._measured_power = drawn
+        if i in freeze:
+            coord._learning_frozen = lambda *a, **k: "frozen"
+        coord._learn_measured_cop(coord._accuracy.draw)
+        coord.__dict__.pop("_learning_frozen", None)
+    m = coord._measured_cop
+    return (coord._cop_samples, repr(coord._cop_scale), m.ratio_ewma, list(m.held),
+            dict(coord._capacity_envelope), dict(coord._cop_baseline), m.cop)
+
+
+_mr_seq = [({}, 2.0, 2.0), (_MR_SYSID, 4.0, 5.2), ({}, 2.4, 2.4), ({}, 2.0, 2.1)]
+_mr_excl = _mr_cop(_cf_coord(), _mr_seq)
+_mr_froz = _mr_cop(_cf_coord(), _mr_seq, freeze={1})
+_mr_noexp = _mr_cop(_cf_coord(), [c for c in _mr_seq if not c[0]])
+R.check(
+    "null: a run with an experiment interval leaves the sample count, the COP "
+    "scale, the walking ratio, the hold, the envelope and the health baseline "
+    "byte-identical to the same run with that interval frozen, and to the run "
+    "without it; the first plan interval after it folds none of its draw",
+    _mr_excl == _mr_froz == _mr_noexp and _mr_excl[0] == 3,
+    f"{_mr_excl} / {_mr_froz} / {_mr_noexp}",
+)
+
+
+# The dither's first experiment cycle (design R11-CARRY-DRAWMAP, item 1 and
+# the verdict's dither-first-cycle note): owed_scale reads the cycle before's
+# admission, so a plan row admitted just ahead of an experiment would step the
+# scale inside it. An experiment cycle moves no scale, as a frozen one does not.
+def _mr_dither(k, arm, n=70):
+    """``n`` heat-led cycles on ``_ss_coord``; cycle ``k`` is ``arm`` ("plan",
+    "experiment" or "frozen"). Per cycle: the scale in force, the probe's level,
+    the dither's state and the verdict; and whether the row before ``k`` was admitted."""
+    coord, trace, admitted_before = _ss_coord(), [], None
+    for i, (asked, _) in enumerate(_ss_flat(n, seed=11)):
+        if i == k:
+            admitted_before = coord._measured_cop.probe.dither.admitted
+        drawn = asked * coord._cop_scale / 1.1
+        coord._current_action = {"power": asked, "dhw_power": 0.0,
+                                 **(_MR_SYSID if i == k and arm == "experiment" else {})}
+        coord._measured_power = drawn
+        coord._current_state.outdoor_temperature = 8.0
+        _cf_drm.fold(coord._accuracy.draw, drawn, coord._commanded_split(), coord._thermal_params,
+                     frozen=False, distorted=False, defrost=False)
+        if i == k and arm == "frozen":
+            coord._learning_frozen = lambda *a, **kw: "frozen"
+        coord._learn_measured_cop(coord._accuracy.draw)
+        coord.__dict__.pop("_learning_frozen", None)
+        d, p = coord._measured_cop.probe.dither, coord._measured_cop.probe
+        trace.append((repr(coord._cop_scale), p.level, p.base, d.rows, list(d.contrasts), d.reading,
+                      d.ahead, d.admitted, coord._measured_cop.scale_response))
+    return trace, admitted_before
+
+
+_mr_dk = 55  # past the probe arming (cycle 47 on this run), the row before admitted
+_mr_d_exp, _mr_d_froz, _mr_d_plan = (_mr_dither(_mr_dk, a) for a in ("experiment", "frozen", "plan"))
+R.check(
+    "the dither's first experiment cycle: a run whose cycle 55 is an experiment, entered with the "
+    "row before it admitted, takes no dither step inside it -- the scale in force is the probe's "
+    "base and the dither holds no reading -- and from the next cycle to the run's end is "
+    "byte-identical to the same run with that cycle frozen; null control, the same cycle under "
+    "the plan steps the dither off its base",
+    _mr_d_exp[1] is True and _mr_d_exp[0][_mr_dk][2] is not None
+    and float(_mr_d_exp[0][_mr_dk][0]) == _mr_d_exp[0][_mr_dk][2]
+    and _mr_d_exp[0][_mr_dk][5:7] == (None, None)
+    and _mr_d_exp[0][_mr_dk + 1:] == _mr_d_froz[0][_mr_dk + 1:]
+    and float(_mr_d_plan[0][_mr_dk][0]) != _mr_d_plan[0][_mr_dk][2],
+    f"admitted before {_mr_d_exp[1]}; cycle {_mr_dk}: experiment {_mr_d_exp[0][_mr_dk][:3]} "
+    f"plan {_mr_d_plan[0][_mr_dk][:3]}; first diverging cycle after it "
+    f"{next((i for i, (a, b) in enumerate(zip(_mr_d_exp[0], _mr_d_froz[0])) if a != b and i > _mr_dk), None)}",
+)
+_mr_one = _cf_coord()
+_mr_cop(_mr_one, [(_MR_SYSID, 2.0, 2.0)])
+_mr_plan_one = _cf_coord()
+_mr_cop(_mr_plan_one, [({}, 2.0, 2.0)])
+R.check(
+    "an experiment interval drawing exactly its ask reads draw_off_ask and "
+    "folds nothing; the same interval under the plan folds",
+    (_mr_one._cop_samples, _mr_one._measured_cop.refusal) == (0, _MR_OFF)
+    and (_mr_plan_one._cop_samples, _mr_plan_one._measured_cop.refusal) == (1, None),
+)
+# r13: on a heat-metered install the COP is heat over the draw; the refusal
+# stands there for the scale's reason (judge_floor's docstring), tested.
+_mr_met, _mr_met_plan = _cf_metered(), _cf_metered()
+for _mr_c, _mr_a in ((_mr_met, _MR_SYSID), (_mr_met_plan, {})):
+    _mr_c._current_action = {"power": 2.0, "dhw_power": 0.0, **_mr_a}
+    _mr_c._measured_power = 2.0
+    _mr_c._current_state.outdoor_temperature = 8.0
+    _mr_c._learn_measured_cop(_mr_c._accuracy.draw)
+R.check(
+    "r13: on a heat-metered install an experiment interval is refused too, and "
+    "the same interval under the plan folds its measured COP",
+    (_mr_met._cop_samples, _mr_met._measured_cop.refusal, _mr_met._measured_cop.cop) == (0, _MR_OFF, None)
+    and _mr_met_plan._cop_samples == 1 and _mr_met_plan._measured_cop.cop is not None,
+    f"{_mr_met._cop_samples} {_mr_met._measured_cop.refusal} / {_mr_met_plan._cop_samples}",
+)
+
+
+# A heat counter with no power entity: a span holding an experiment cycle
+# fails the cycle's gate, so its COP never folds (null: the same span with no
+# experiment folds, as #2854's test does).
+def _mr_span(experiment_cycle=None, cycles=3, elec_kw=2.0):
+    c = _t2_coord(**{"heat_pump_energy_entity": "sensor.e"}, **{_HE_KEY: "sensor.he"})
+    c._current_state.outdoor_temperature = 8.0
+    c._measured_power = None
+    m = _mr_he.meter_of(c)
+    refusals = []
+    for i in range(cycles):
+        c._current_action = {"power": elec_kw, **(_MR_SYSID if i == experiment_cycle else {})}
+        at = NOW + timedelta(hours=0.5 * i)
+        m.observe_counters(at, 100.0 + 3.7 * elec_kw * 0.5 * i, 50.0 + elec_kw * 0.5 * i,
+                           configured=True, cadence_h=0.5, bounds_h=_HE_BOUNDS, max_heat_kw=30.0)
+        c._last_house_sample, c._last_house_sample_time = _mr_dc_replace(c._current_state), at
+        c._learn_measured_cop()
+        refusals.append(c._measured_cop.refusal)
+        _mr_aio.run(_mr_cm._async_learn_heat_span(c, {"cop": c._measured_cop.refusal == _MR_OPEN}))
+    return c._cop_samples, refusals
+
+
+_mr_span_exp, _mr_span_plan = _mr_span(1), _mr_span()
+R.check(
+    "a heat counter span holding an experiment cycle folds no COP, that cycle "
+    "reading draw_off_ask; the same span with none folds one",
+    _mr_span_exp[0] == 0 and _mr_span_exp[1][1] == _MR_OFF and _mr_span_plan[0] == 1,
+    f"{_mr_span_exp} / {_mr_span_plan}",
+)
+
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
new file mode 100644
index 0000000000..bd324872f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF ac9b3721",
+  "killed_by": "tests/features.py",
+  "old": "        if experiment:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.BOOLOP.b9424216.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.BOOLOP.b9424216.json
new file mode 100644
index 0000000000..de0c0a7d9e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.BOOLOP.b9424216.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.owed_scale BOOLOP b9424216",
+  "killed_by": "tests/features.py",
+  "old": "            configured, now, read and self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`configured, now, read or self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json
deleted file mode 100644
index c691d8a05a..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.owed_scale RETURN_DEL a64e3c97",
-  "killed_by": "tests/features.py",
-  "old": "        return self.probe.owed_scale(configured, now, self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.2d59d2fc.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.2d59d2fc.json
new file mode 100644
index 0000000000..6cdf6cbba9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.2d59d2fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 2d59d2fc",
+  "killed_by": "tests/structure.py",
+  "old": "        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now(), not experiment)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
index d2589c55da..7e0808e417 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF f61826c8",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c294c9b7",
   "killed_by": "tests/features.py",
-  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json
deleted file mode 100644
index 0a826b8c36..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c41a3ead",
-  "killed_by": "tests/features.py",
-  "old": "        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now())) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_dhw_current_hour.RETURN_DEL.a2025997.json b/tests/mutation_ledger/killed_by/coordinator.py/_dhw_current_hour.RETURN_DEL.a2025997.json
new file mode 100644
index 0000000000..7e614f40e7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_dhw_current_hour.RETURN_DEL.a2025997.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_dhw_current_hour RETURN_DEL a2025997",
+  "killed_by": "tests/features.py",
+  "old": "    return now.hour + now.minute / 60.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.0a236124.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.0a236124.json
new file mode 100644
index 0000000000..3ea724c73f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.0a236124.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 0a236124",
+  "killed_by": "tests/features.py",
+  "old": "SEGMENT_SETTLE_MIN = 3",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SEGMENT_SETTLE_MIN = 6`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.849fc597.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.849fc597.json
new file mode 100644
index 0000000000..392fae90ab
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.849fc597.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 849fc597",
+  "killed_by": "tests/features.py",
+  "old": "SEGMENT_MAX_MIN = 30",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SEGMENT_MAX_MIN = 60`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.cdb85f1f.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.cdb85f1f.json
new file mode 100644
index 0000000000..7b5329cc12
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.cdb85f1f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST cdb85f1f",
+  "killed_by": "tests/features.py",
+  "old": "MAP_ROWS = 672",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`MAP_ROWS = 1344`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.d55ebb0a.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.d55ebb0a.json
new file mode 100644
index 0000000000..1a1f168e3d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.d55ebb0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST d55ebb0a",
+  "killed_by": "tests/features.py",
+  "old": "SEGMENT_STEADY_MIN = 2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SEGMENT_STEADY_MIN = 4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows._close.GUARD_OFF.57f875bd.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows._close.GUARD_OFF.57f875bd.json
new file mode 100644
index 0000000000..8b530c0136
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows._close.GUARD_OFF.57f875bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows._close GUARD_OFF 57f875bd",
+  "killed_by": "tests/features.py",
+  "old": "        if row is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.commit_runs.GUARD_OFF.5f94b1f4.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.commit_runs.GUARD_OFF.5f94b1f4.json
new file mode 100644
index 0000000000..2fe71c3432
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.commit_runs.GUARD_OFF.5f94b1f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.commit_runs GUARD_OFF 5f94b1f4",
+  "killed_by": "tests/features.py",
+  "old": "        if keep:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.BOOLOP.5370a6a2.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.BOOLOP.5370a6a2.json
new file mode 100644
index 0000000000..517641c1df
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.BOOLOP.5370a6a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass BOOLOP 5370a6a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.open and int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.open or int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.3603e23a.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.3603e23a.json
new file mode 100644
index 0000000000..ac89a0128b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.3603e23a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass CMP_BOUND 3603e23a",
+  "killed_by": "tests/features.py",
+  "old": "        stopped = rec.defrost or rec.drawn_kw is None or rec.drawn_kw <= RUNNING_FLOOR_KW",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`stopped = rec.defrost or rec.drawn_kw is None or rec.drawn_kw < RUNNING_FLOOR_KW`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.a2c87e94.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.a2c87e94.json
new file mode 100644
index 0000000000..89f918b0f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.CMP_BOUND.a2c87e94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass CMP_BOUND a2c87e94",
+  "killed_by": "tests/features.py",
+  "old": "                (rec.at - first.at).total_seconds() >= SEGMENT_MAX_MIN * 60.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`(rec.at - first.at).total_seconds() > SEGMENT_MAX_MIN * 60.0):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.5370a6a2.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.5370a6a2.json
new file mode 100644
index 0000000000..c82c5a33d8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.5370a6a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass GUARD_OFF 5370a6a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.open and int(rec.at.timestamp() // 60) == int(self.open[-1].at.timestamp() // 60):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.603e3086.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.603e3086.json
new file mode 100644
index 0000000000..971b66d52e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.603e3086.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass GUARD_OFF 603e3086",
+  "killed_by": "tests/features.py",
+  "old": "        if rec is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.ed8f0eb2.json b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.ed8f0eb2.json
new file mode 100644
index 0000000000..2719e4bdf3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/MapRows.take_pass.GUARD_OFF.ed8f0eb2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:MapRows.take_pass GUARD_OFF ed8f0eb2",
+  "killed_by": "tests/features.py",
+  "old": "        if stopped:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/PassRecord.run_key.RETURN_DEL.832052c6.json b/tests/mutation_ledger/killed_by/draw_range.py/PassRecord.run_key.RETURN_DEL.832052c6.json
new file mode 100644
index 0000000000..cd631f51c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/PassRecord.run_key.RETURN_DEL.832052c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:PassRecord.run_key RETURN_DEL 832052c6",
+  "killed_by": "tests/features.py",
+  "old": "        return (self.written_c, self.level_kw, self.duty, self.origin)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.4e439b74.json b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.4e439b74.json
new file mode 100644
index 0000000000..7ce39d5035
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.4e439b74.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_cell GUARD_OFF 4e439b74",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(value, str):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.5cd1f888.json b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.5cd1f888.json
new file mode 100644
index 0000000000..6e38481602
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_cell.GUARD_OFF.5cd1f888.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_cell GUARD_OFF 5cd1f888",
+  "killed_by": "tests/features.py",
+  "old": "    if value is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_cell.RETURN_DEL.9b1bb4f6.json b/tests/mutation_ledger/killed_by/draw_range.py/_cell.RETURN_DEL.9b1bb4f6.json
new file mode 100644
index 0000000000..6d732bb5ae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_cell.RETURN_DEL.9b1bb4f6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_cell RETURN_DEL 9b1bb4f6",
+  "killed_by": "tests/features.py",
+  "old": "    return str(int(value)) if isinstance(value, int) else repr(round(float(value), 3))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.BOOLOP.c470afed.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.BOOLOP.c470afed.json
new file mode 100644
index 0000000000..a90a6b39c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.BOOLOP.c470afed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell BOOLOP c470afed",
+  "killed_by": "tests/features.py",
+  "old": "    if cell == \"\" and name not in MAP_COLUMNS[:2]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if cell == \"\" or name not in MAP_COLUMNS[:2]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.345675b8.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.345675b8.json
new file mode 100644
index 0000000000..5cca0b8258
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.345675b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell GUARD_OFF 345675b8",
+  "killed_by": "tests/structure.py",
+  "old": "    if name in _MAP_TEXT:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.b061f526.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.b061f526.json
new file mode 100644
index 0000000000..6152108342
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.b061f526.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell GUARD_OFF b061f526",
+  "killed_by": "tests/features.py",
+  "old": "    if not np.isfinite(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.c470afed.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.c470afed.json
new file mode 100644
index 0000000000..7404101e18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.GUARD_OFF.c470afed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell GUARD_OFF c470afed",
+  "killed_by": "tests/features.py",
+  "old": "    if cell == \"\" and name not in MAP_COLUMNS[:2]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.RETURN_DEL.d4c9e2a6.json b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.RETURN_DEL.d4c9e2a6.json
new file mode 100644
index 0000000000..f35dd2e8c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_map_cell.RETURN_DEL.d4c9e2a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_map_cell RETURN_DEL d4c9e2a6",
+  "killed_by": "tests/features.py",
+  "old": "    return value",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.1179dcea.json b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.1179dcea.json
new file mode 100644
index 0000000000..0a2ad550e9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.1179dcea.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_segment_row CMP_BOUND 1179dcea",
+  "killed_by": "tests/features.py",
+  "old": "    steady = [p for p in passes if (p.at - first.at).total_seconds() >= SEGMENT_SETTLE_MIN * 60.0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`steady = [p for p in passes if (p.at - first.at).total_seconds() > SEGMENT_SETTLE_MIN * 60.0]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.bec45cb3.json b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.bec45cb3.json
new file mode 100644
index 0000000000..c141adb4da
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.CMP_BOUND.bec45cb3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_segment_row CMP_BOUND bec45cb3",
+  "killed_by": "tests/features.py",
+  "old": "    if len(steady) < SEGMENT_STEADY_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(steady) <= SEGMENT_STEADY_MIN:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.GUARD_OFF.bec45cb3.json b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.GUARD_OFF.bec45cb3.json
new file mode 100644
index 0000000000..e88f365015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_segment_row.GUARD_OFF.bec45cb3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_segment_row GUARD_OFF bec45cb3",
+  "killed_by": "tests/structure.py",
+  "old": "    if len(steady) < SEGMENT_STEADY_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.5edbe6c2.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.5edbe6c2.json
new file mode 100644
index 0000000000..e4d73eab95
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.5edbe6c2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_map GUARD_OFF 5edbe6c2",
+  "killed_by": "tests/features.py",
+  "old": "    if len(split) != len(MAP_COLUMNS):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.76b546cb.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.76b546cb.json
new file mode 100644
index 0000000000..f1328adc24
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.GUARD_OFF.76b546cb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_map GUARD_OFF 76b546cb",
+  "killed_by": "tests/features.py",
+  "old": "    if len({len(c) for c in split}) != 1:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.RETURN_DEL.a8227ccf.json
new file mode 100644
index 0000000000..edeadcda14
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_map.RETURN_DEL.a8227ccf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_map RETURN_DEL a8227ccf",
+  "killed_by": "tests/features.py",
+  "old": "    return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/note_pass.GUARD_OFF.b2310c56.json b/tests/mutation_ledger/killed_by/draw_range.py/note_pass.GUARD_OFF.b2310c56.json
new file mode 100644
index 0000000000..5dc93fa25c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/note_pass.GUARD_OFF.b2310c56.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:note_pass GUARD_OFF b2310c56",
+  "killed_by": "tests/features.py",
+  "old": "    if draw is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_map_inputs.RETURN_DEL.86bbdd73.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_map_inputs.RETURN_DEL.86bbdd73.json
new file mode 100644
index 0000000000..ce42f5a25c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_map_inputs.RETURN_DEL.86bbdd73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_map_inputs RETURN_DEL 86bbdd73",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return MapInputs(_level_kw(inp, now, boost_c is not None), p_min, p_max, heat_c, floor_c, boost_c is not None)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_pass_record.GUARD_OFF.c93be904.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_pass_record.GUARD_OFF.c93be904.json
new file mode 100644
index 0000000000..ddcdc43432
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_pass_record.GUARD_OFF.c93be904.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_pass_record GUARD_OFF c93be904",
+  "killed_by": "tests/features.py",
+  "old": "    if command is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.CMP_BOUND.ebe1fc1b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.CMP_BOUND.ebe1fc1b.json
new file mode 100644
index 0000000000..63c1c6295b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.CMP_BOUND.ebe1fc1b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin CMP_BOUND ebe1fc1b",
+  "killed_by": "tests/features.py",
+  "old": "    held_start = utc_elapsed_seconds(now, run.start) < FEEDBACK_START_HOLD.total_seconds()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`held_start = utc_elapsed_seconds(now, run.start) <= FEEDBACK_START_HOLD.total_seconds()`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.50cd56b2.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.50cd56b2.json
new file mode 100644
index 0000000000..63e75161fc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.50cd56b2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF 50cd56b2",
+  "killed_by": "tests/features.py",
+  "old": "    if run is None or not run.running:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.531d53db.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.531d53db.json
new file mode 100644
index 0000000000..23eadd1541
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.531d53db.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF 531d53db",
+  "killed_by": "tests/features.py",
+  "old": "    if duty not in (\"space\", \"both\"):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.60aea822.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.60aea822.json
new file mode 100644
index 0000000000..c7783c9bc3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.60aea822.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF 60aea822",
+  "killed_by": "tests/features.py",
+  "old": "    if action.get(\"mode\") == \"system_identification\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.bd37d9be.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.bd37d9be.json
new file mode 100644
index 0000000000..f30022d24b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.GUARD_OFF.bd37d9be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin GUARD_OFF bd37d9be",
+  "killed_by": "tests/features.py",
+  "old": "    if boost_on:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.RETURN_DEL.f3bc64b6.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.RETURN_DEL.f3bc64b6.json
new file mode 100644
index 0000000000..5990a4f0b4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/pass_origin.RETURN_DEL.f3bc64b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:pass_origin RETURN_DEL f3bc64b6",
+  "killed_by": "tests/structure.py",
+  "old": "    return ORIGIN_FEEDBACK_START if held_start else ORIGIN_FEEDBACK",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json
deleted file mode 100644
index b4b7d7250a..0000000000
--- a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_flow_target.CLAMP_DROP.38a077e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_flow_target CLAMP_DROP 38a077e7",
-  "old": "            lo=min(floor_c, heat_c),",
-  "reason": "CLAMP_DROP prints `lo=(floor_c)` for `lo=min(floor_c, heat_c)` in _flow_target's _bounded call. The argument reaches nothing but that call's `lo`, which quantise_setpoint_c applies as `max(out, _on_step(lo, \"up\"))` and then bounds by the same call's `hi=heat_c`. If floor_c <= heat_c both texts pass the same number. If floor_c > heat_c the original passes heat_c and the mutant floor_c: the mutant's `max(out, ceil-step(floor_c))` is at least floor_c > heat_c, so the following `min(..., floor-step(heat_c))` returns floor-step(heat_c) -- the value the original's `max(out, ceil-step(heat_c))` also returns, since ceil-step(heat_c) >= floor-step(heat_c). Equal on both branches, and the unit conversion is monotone, so the Fahrenheit path is equal too. Measured at this head: 7680 _flow_target cells (entity ranges with and without a min/max, steps 1.0/0.5/0.1, degC and degF; configured heating ceiling absent and 30-60 degC; inlets 5-65 degC and an unmeasured one; levels at p_min/mid/p_max; the heating and idle duties) differ on 0 cells between the head and the mutant, while the probe's null control -- the same line's other mutant, `lo=None` -- differs on 21 cells (a 25.3 degC tank at the floor writes 31.0 at the head, 30.0 under lo=None). The probe is scratch ($SCRATCH/mut/eqprobe.py sha1 c035d11b3a900642cc478a1a3ef1ab28c4016cfb, $SCRATCH/mut/grid.py sha1 c10409a553f148215f700bc542d345a9f40a0c6c); the in-tree re-verification is `python3 tests/mutation_table.py --anchor '<this anchor>'`, which drives the site with the drivers in play.",
-  "verdict": "equivalent"
-}
diff --git a/tests/seam_map.json b/tests/seam_map.json
index 00c8668eb9..3f77543780 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -73,7 +73,6 @@
   "_detect_immersion": "core",
   "_detect_outage": "grid",
   "_dhw_confidence_band": "dhw",
-  "_dhw_current_hour": "dhw",
   "_dhw_effective_windows": "dhw",
   "_dhw_in_demand_window": "dhw",
   "_dhw_mixed_water": "dhw",
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 8f925f20e3..28edeca684 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -16,6 +16,6 @@
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "e352724335c136b65562cd3e71f728549ad04a82",
- "seam_cut_total": 415
+ "recorded_at": "ae0ed64af898d8923ac35afe6e9c031ac1e6b111",
+ "seam_cut_total": 413
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
