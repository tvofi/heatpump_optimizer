# Review packet #3841
head: b0ee904f74393f05b4a2195bdef1c305f9b1dcc5
base: baa9a467ac518bc3f8733d2603ea8ae406b235af

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=137337171654 success
arch-score / arch-score id=137338894102 success
arm id=137330607488 skipped
budget-raise-gate / budget-raise-gate id=137338894085 success
cancel-superseded id=137333215725 success
codeql id=137338895437 skipped
codeql / Analyze (actions) id=137336599120 success
codeql / Analyze (javascript-typescript) id=137336599150 success
codeql / Analyze (python) id=137336599197 success
gate id=137342358631 failure
governance id=137338895545 skipped
governance / env-matrix id=137336599188 success
governance / instrument-self-tests id=137336599185 success
governance / policy-docs id=137336599157 success
governance / record id=137336600986 skipped
governance / wave-script id=137336599248 success
hassfest id=137338895170 skipped
hassfest / hassfest id=137336599149 success
kernel-points id=137338895659 skipped
pr-contract id=137342359367 skipped
prelude id=137333215683 success
refresh id=137333215415 success
sweep-self id=137343896794 skipped
tests id=137338895531 skipped
tests / arch-instrument id=137338983748 success
tests / briefs id=137336599138 success
tests / browser id=137338983551 success
tests / ci-ratchet id=137357230884 skipped
tests / claims-autofix id=137357228344 success
tests / closure-scope id=137336599152 success
tests / closures id=137338983604 success
tests / closures-autofix id=137354617589 skipped
tests / coverage id=137338983532 success
tests / coverage-ratchet id=137352204036 success
tests / fast (3.14) id=137338983550 failure
tests / graders-head-copy id=137352204099 success
tests / lane-proofs id=137357228604 success
tests / mutation id=137336599092 failure
tests / mutation-pins (1) id=137340583942 success
tests / mutation-pins (2) id=137340584094 success
tests / mutation-pins (3) id=137340583905 success
tests / mutation-pins (4) id=137340583982 success
tests / mutation-pins (5) id=137340583999 in_progress
tests / nightly-ha (2025.2.0) id=137338983594 failure
tests / nightly-ha (stable) id=137338983580 failure
tests / nightly-status id=137336599070 success
tests / replay id=137338983508 success
tests / typing id=137338983514 success
validate id=137338895101 skipped
validate / validate-hacs id=137336599059 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at b0ee904f74393f05b4a2195bdef1c305f9b1dcc5 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE stale tree: b0ee904f74393f05b4a2195bdef1c305f9b1dcc5 lacks origin/main 2f4e32c2a3b959142e29966e001292d42ff1affd; roster read at origin/main
NOTE body item a41d3d0f: R11-CLOSEOUT-CLEANUP
NOTE body item 252ca3f2: R11-CLOSEOUT-CLEANUP
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified PYTHONPATH=tests/hastub python3 <path>
             the path `<path>` is a template or an expansion, not a literal
  unverified git archive dbdc1d95fef3 dev/audit/rounds/round11
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         dev/audit/rounds/round11/D10/s2/entity_census.py
             `dev/audit/rounds/round11/D10/s2/entity_census.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D8/s1/monthly.py -v
             `dev/audit/rounds/round11/D8/s1/monthly.py` is in the tree at this head
  unverified git archive 92d38ecb custom_components tests
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D8/s2/m3_naming.py
             `dev/audit/rounds/round11/D8/s2/m3_naming.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D8/s3/m5_matrix.py
             `dev/audit/rounds/round11/D8/s3/m5_matrix.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D14/s1/step_grid.py
             `dev/audit/rounds/round11/D14/s1/step_grid.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D17/leads/dhw_window_weekday.py
             `dev/audit/rounds/round11/D17/leads/dhw_window_weekday.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests python3 tools/replay/dbg_bundle_gen.py --days 2
             `tools/replay/dbg_bundle_gen.py` is in the tree at this head
  unverified git grep -n solve_time_ms -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff a8efe1d1c2a8
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GATE_JOBS=3 bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tools/policy/field_coverage.mjs
             `tools/policy/field_coverage.mjs` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff a8efe1d1c2a8
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         tools/audit/seat/features_block.py
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff baa9a467ac51
             `tests/closure.py` is in the tree at this head

FIGURES: 22 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/binary_sensor.py/WoodCheaperBinarySensor.available.BOOLOP.fdaf4ca2.json b/tests/mutation_ledger/killed_by/binary_sensor.py/WoodCheaperBinarySensor.available.BOOLOP.fdaf4ca2.json
deleted file mode 100644
index 5aaf57781a..0000000000
--- a/tests/mutation_ledger/killed_by/binary_sensor.py/WoodCheaperBinarySensor.available.BOOLOP.fdaf4ca2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/binary_sensor.py:WoodCheaperBinarySensor.available BOOLOP fdaf4ca2",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and fuel.get(\"ready\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or fuel.get(\"ready\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.2d0b59e7.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.2d0b59e7.json
deleted file mode 100644
index 361db9eeef..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.2d0b59e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open GUARD_OFF 2d0b59e7",
-  "killed_by": "tests/block_duty.py",
-  "old": "    if not windows:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 62f604eb062bf88d3dc4b0f4ec85ca17359af229: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.6492d240.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.6492d240.json
deleted file mode 100644
index 35d5e8ca38..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.6492d240.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open GUARD_OFF 6492d240",
-  "killed_by": "tests/block_duty.py",
-  "old": "    if planned:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 62f604eb062bf88d3dc4b0f4ec85ca17359af229: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.015b285e.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.015b285e.json
deleted file mode 100644
index a41a57a675..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.015b285e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open RETURN_DEL 015b285e",
-  "killed_by": "tests/block_duty.py",
-  "old": "    return hour_in_windows(hour, windows)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 62f604eb062bf88d3dc4b0f4ec85ca17359af229: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.571abbe7.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.571abbe7.json
new file mode 100644
index 0000000000..e7c06bef39
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.571abbe7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open RETURN_DEL 571abbe7",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return hour_in_windows(now.hour + now.minute / 60.0, windows)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.4a4aab1a.json b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.4a4aab1a.json
new file mode 100644
index 0000000000..5c6f861628
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.4a4aab1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/button.py:SystemIdentificationButton.async_press GUARD_OFF 4a4aab1a",
+  "killed_by": "tests/features.py",
+  "old": "        if refused == sysid.ARM_REFUSED_DISABLED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.83253676.json b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.83253676.json
new file mode 100644
index 0000000000..05ae7d3e19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.83253676.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/button.py:SystemIdentificationButton.async_press GUARD_OFF 83253676",
+  "killed_by": "tests/features.py",
+  "old": "        if refused is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.BOOLOP.320af692.json b/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.BOOLOP.320af692.json
deleted file mode 100644
index 779372da85..0000000000
--- a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.BOOLOP.320af692.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/climate.py:HeatPumpOptimizerClimate.available BOOLOP 320af692",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and flags.get(\"upper_floor_temperature\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or flags.get(\"upper_floor_temperature\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.RETURN_DEL.320af692.json b/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.RETURN_DEL.320af692.json
deleted file mode 100644
index 33bc4b0038..0000000000
--- a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.RETURN_DEL.320af692.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/climate.py:HeatPumpOptimizerClimate.available RETURN_DEL 320af692",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and flags.get(\"upper_floor_temperature\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_on_grid.GUARD_OFF.390fac7a.json b/tests/mutation_ledger/killed_by/config_flow.py/_on_grid.GUARD_OFF.390fac7a.json
new file mode 100644
index 0000000000..efea1bbfe1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_on_grid.GUARD_OFF.390fac7a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_on_grid GUARD_OFF 390fac7a",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if value == declared or base is None or not isinstance(step, (int, float)) or step <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.0fe17c48.json b/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.0fe17c48.json
new file mode 100644
index 0000000000..0091be4b72
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.0fe17c48.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_widen_to_fit GUARD_OFF 0fe17c48",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not math.isfinite(number_value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.7a72fcf1.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.7a72fcf1.json
deleted file mode 100644
index a72004e967..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.7a72fcf1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_drive_pumps BOOLOP 7a72fcf1",
-  "killed_by": "tests/features.py",
-  "old": "                if params.dhw_enabled and params.dhw_windows_active",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if params.dhw_enabled or params.dhw_windows_active`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.a550a1f3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.a550a1f3.json
new file mode 100644
index 0000000000..e5fb60d71f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.a550a1f3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_drive_pumps BOOLOP a550a1f3",
+  "killed_by": "tests/features.py",
+  "old": "            scheduled = params.dhw_enabled and params.dhw_windows_active",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`scheduled = params.dhw_enabled or params.dhw_windows_active`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.GUARD_OFF.077aa3ea.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.GUARD_OFF.077aa3ea.json
deleted file mode 100644
index dcff060351..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.GUARD_OFF.077aa3ea.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_effective_windows GUARD_OFF 077aa3ea",
-  "killed_by": "tests/features.py",
-  "old": "        if planned:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.99a2b558.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.99a2b558.json
deleted file mode 100644
index 97f21378f3..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.99a2b558.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_effective_windows RETURN_DEL 99a2b558",
-  "killed_by": "tests/features.py",
-  "old": "        return windows",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.ba9098c8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.ba9098c8.json
new file mode 100644
index 0000000000..68f7fbb3f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.ba9098c8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_effective_windows RETURN_DEL ba9098c8",
+  "killed_by": "tests/structure.py",
+  "old": "        return windows_in_force(ctx._thermal_params, self._optimization_result, now, holidays, days)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.BOOLOP.e8eac339.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.BOOLOP.e8eac339.json
new file mode 100644
index 0000000000..fea6537c19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.BOOLOP.e8eac339.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window BOOLOP e8eac339",
+  "killed_by": "tests/features.py",
+  "old": "    if windows and hour_in_windows(hour, windows):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if windows or hour_in_windows(hour, windows):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.e8eac339.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.e8eac339.json
new file mode 100644
index 0000000000..6549aeeb2b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.e8eac339.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window GUARD_OFF e8eac339",
+  "killed_by": "tests/features.py",
+  "old": "    if windows and hour_in_windows(hour, windows):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.f92e3c65.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.f92e3c65.json
deleted file mode 100644
index ef9cd75ceb..0000000000
--- a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.f92e3c65.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window GUARD_OFF f92e3c65",
-  "killed_by": "tests/features.py",
-  "old": "        if best is None or delta < best:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.RETURN_DEL.9a247f7f.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.RETURN_DEL.9a247f7f.json
deleted file mode 100644
index 3549e5fe02..0000000000
--- a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.RETURN_DEL.9a247f7f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window RETURN_DEL 9a247f7f",
-  "killed_by": "tests/features.py",
-  "old": "    return best",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/windows_in_force.GUARD_OFF.2891c313.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/windows_in_force.GUARD_OFF.2891c313.json
new file mode 100644
index 0000000000..4194b8f349
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/windows_in_force.GUARD_OFF.2891c313.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:windows_in_force GUARD_OFF 2891c313",
+  "killed_by": "tests/features.py",
+  "old": "    if info.get(\"dhw_windows\"):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_schedule.py/vvc_should_run.GUARD_OFF.2d0b59e7.json b/tests/mutation_ledger/killed_by/pump_schedule.py/vvc_should_run.GUARD_OFF.2d0b59e7.json
deleted file mode 100644
index dd9510104f..0000000000
--- a/tests/mutation_ledger/killed_by/pump_schedule.py/vvc_should_run.GUARD_OFF.2d0b59e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_schedule.py:vvc_should_run GUARD_OFF 2d0b59e7",
-  "killed_by": "tests/features.py",
-  "old": "    if not windows:",
-  "reason": "Recorded by `mutation_table.py --drain` against 15f0b5924f3c2a75befe984d156cb3e602effd2e: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/CompressorStartsSensor.available.RETURN_DEL.950e6d25.json b/tests/mutation_ledger/killed_by/sensor.py/CompressorStartsSensor.available.RETURN_DEL.950e6d25.json
deleted file mode 100644
index b949de5809..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/CompressorStartsSensor.available.RETURN_DEL.950e6d25.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:CompressorStartsSensor.available RETURN_DEL 950e6d25",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data)",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.BOOLOP.33e22e1d.json b/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.BOOLOP.33e22e1d.json
deleted file mode 100644
index 459e39f6d9..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.BOOLOP.33e22e1d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MeasuredPowerSensor.available BOOLOP 33e22e1d",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data.get(\"measured_power_available\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or data.get(\"measured_power_available\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.RETURN_DEL.33e22e1d.json b/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.RETURN_DEL.33e22e1d.json
deleted file mode 100644
index dcb953583b..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.RETURN_DEL.33e22e1d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MeasuredPowerSensor.available RETURN_DEL 33e22e1d",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data.get(\"measured_power_available\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MixedHotWaterSensor.available.BOOLOP.0bd743fb.json b/tests/mutation_ledger/killed_by/sensor.py/MixedHotWaterSensor.available.BOOLOP.0bd743fb.json
deleted file mode 100644
index b156d31821..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MixedHotWaterSensor.available.BOOLOP.0bd743fb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MixedHotWaterSensor.available BOOLOP 0bd743fb",
-  "killed_by": "tests/entities.py",
-  "old": "            super().available and (self._data()).get(\"dhw_mixed\")",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 777c23180a08b0d6c7abd41d6dd5fe7b1abf19b3: BOOLOP (`super().available or (self._data()).get(\"dhw_mixed\")`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.BOOLOP.1ba360a6.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.BOOLOP.1ba360a6.json
deleted file mode 100644
index 8fe0553541..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.BOOLOP.1ba360a6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for BOOLOP 1ba360a6",
-  "killed_by": "tests/features.py",
-  "old": "        if any(isinstance(row, dict) and row.get(\"estimated\") for row in rows):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if any(isinstance(row, dict) or row.get(\"estimated\") for row in rows):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.1ba360a6.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.1ba360a6.json
deleted file mode 100644
index 50a869ceae..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.1ba360a6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for GUARD_OFF 1ba360a6",
-  "killed_by": "tests/entities.py",
-  "old": "        if any(isinstance(row, dict) and row.get(\"estimated\") for row in rows):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.e9869136.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.e9869136.json
deleted file mode 100644
index 9cfc248976..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.e9869136.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for GUARD_OFF e9869136",
-  "killed_by": "tests/entities.py",
-  "old": "        if not rows:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.2c97a7fe.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.2c97a7fe.json
deleted file mode 100644
index 0aa7b432e3..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.2c97a7fe.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for RETURN_DEL 2c97a7fe",
-  "killed_by": "tests/features.py",
-  "old": "        return \"open_month_coverage\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.fd57f30a.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.fd57f30a.json
new file mode 100644
index 0000000000..e5f003620a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.fd57f30a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for RETURN_DEL fd57f30a",
+  "killed_by": "tests/harness_headers.py",
+  "old": "        return \"open_month_coverage\" if self._rows() else \"settled_savings_month\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/harness_headers.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.GUARD_OFF.9fb40798.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.GUARD_OFF.9fb40798.json
deleted file mode 100644
index 9bd13d54f9..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.GUARD_OFF.9fb40798.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor.native_value GUARD_OFF 9fb40798",
-  "killed_by": "tests/entities.py",
-  "old": "            if isinstance(row, dict) and row.get(\"estimated\"):",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.RETURN_DEL.f0d4f327.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.RETURN_DEL.f0d4f327.json
deleted file mode 100644
index 2d22430fa9..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.RETURN_DEL.f0d4f327.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor.native_value RETURN_DEL f0d4f327",
-  "killed_by": "tests/entities.py",
-  "old": "                return None if val is None else round(val, 2)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 99cf51c1a73a5a1a44577021399b7f1cfcab898d: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/PVSurplusSensor.available.BOOLOP.b6a68906.json b/tests/mutation_ledger/killed_by/sensor.py/PVSurplusSensor.available.BOOLOP.b6a68906.json
deleted file mode 100644
index d22eed8a41..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/PVSurplusSensor.available.BOOLOP.b6a68906.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:PVSurplusSensor.available BOOLOP b6a68906",
-  "killed_by": "tests/entities.py",
-  "old": "            super().available and (self._data()).get(\"pv_enabled\")",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 777c23180a08b0d6c7abd41d6dd5fe7b1abf19b3: BOOLOP (`super().available or (self._data()).get(\"pv_enabled\")`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/PowerHeadroomSensor.available.BOOLOP.7455907d.json b/tests/mutation_ledger/killed_by/sensor.py/PowerHeadroomSensor.available.BOOLOP.7455907d.json
deleted file mode 100644
index f286cec7c4..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/PowerHeadroomSensor.available.BOOLOP.7455907d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:PowerHeadroomSensor.available BOOLOP 7455907d",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data.get(\"available\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or data.get(\"available\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/survivor_triage/boost.py/_window_open.GUARD_OFF.2d0b59e7~2.json b/tests/mutation_ledger/survivor_triage/boost.py/_window_open.GUARD_OFF.2d0b59e7~2.json
deleted file mode 100644
index faf59b7bf7..0000000000
--- a/tests/mutation_ledger/survivor_triage/boost.py/_window_open.GUARD_OFF.2d0b59e7~2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open GUARD_OFF 2d0b59e7#2",
-  "old": "    if not windows:",
-  "reason": "Equivalent (GUARD_OFF) on the second `if not windows`. Skipping return False falls through to hour_in_windows(hour, windows). hour_in_windows(12.0, []) is False, measured by PYTHONPATH=tests/hastub:custom_components python3 -c 'from heatpump_optimizer.dhw_schedule import hour_in_windows; print(hour_in_windows(12.0, []))'.",
-  "verdict": "equivalent"
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/binary_sensor.py b/custom_components/heatpump_optimizer/binary_sensor.py
index eea76f87ab..3b38cfa76d 100644
--- a/custom_components/heatpump_optimizer/binary_sensor.py
+++ b/custom_components/heatpump_optimizer/binary_sensor.py
@@ -30,7 +30,7 @@ from homeassistant.helpers.entity_platform import AddEntitiesCallback
 from homeassistant.util import dt as dt_util
 
 from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
-from .entity import HeatPumpOptimizerEntity
+from .entity import HeatPumpOptimizerEntity, PayloadFlagMixin
 from .payload import Payload
 from .const import finite_float
 
@@ -305,7 +305,7 @@ class AwayModeBinarySensor(_OptimizerBinarySensorBase):
         }
 
 
-class WoodCheaperBinarySensor(_OptimizerBinarySensorBase):
+class WoodCheaperBinarySensor(PayloadFlagMixin, _OptimizerBinarySensorBase):
     # The wood furnace is an options-page opt-in most installs never turn
     # on; the comparison is unavailable without it, so disabled rather than
     # shipped dead (#1335), with the advisor twin on the same gate.
@@ -317,10 +317,7 @@ class WoodCheaperBinarySensor(_OptimizerBinarySensorBase):
     ) -> None:
         super().__init__(coordinator, entry, "wood_cheaper", "wood_cheaper")
 
-    @property
-    def available(self) -> bool:
-        fuel = self._data().get("wood_fuel") or {}
-        return bool(super().available and fuel.get("ready"))
+    _available_flag = ("wood_fuel", "ready")
 
     @property
     def is_on(self) -> bool:
diff --git a/custom_components/heatpump_optimizer/boost.py b/custom_components/heatpump_optimizer/boost.py
index 7a54506a89..924852f697 100644
--- a/custom_components/heatpump_optimizer/boost.py
+++ b/custom_components/heatpump_optimizer/boost.py
@@ -38,7 +38,7 @@ from .const import (
     MODE_BOOST,
     SPACE_PUMP_FLOOR_MARGIN_C,
 )
-from .dhw_schedule import DHWWindowError, hour_in_windows, parse_windows
+from .dhw_schedule import hour_in_windows, windows_in_force
 from .drift import stored_instant
 from .entity import has_hot_water
 from .payload import CurrentAction, REASON_BOOST, REASON_LEGIONELLA
@@ -736,20 +736,10 @@ def _due_inside_horizon(coord: Any) -> bool:
 
 
 def _window_open(snap: Any, now: datetime) -> bool:
-    info = getattr(snap.plan, "predictive_info", None) or {}
-    planned = info.get("dhw_windows") if snap.plan is not None else None
-    windows = None
-    if planned:
-        try:
-            windows = parse_windows(planned)
-        except DHWWindowError:
-            windows = None
-    if not windows:
-        windows = list(getattr(snap.params, "dhw_demand_windows", None) or [])
-    if not windows:
-        return False
-    hour = now.hour + now.minute / 60.0
-    return hour_in_windows(hour, windows)
+    holidays = away_mode.holiday_dates(
+        getattr(snap, "hass", None), getattr(getattr(snap, "config", None), "holiday_calendar_entity", None), now)
+    windows = windows_in_force(snap.params, snap.plan, now, holidays)
+    return hour_in_windows(now.hour + now.minute / 60.0, windows)
 
 
 def _dhw_floor(coord: Any, snap: Any, now: datetime) -> str | None:
diff --git a/custom_components/heatpump_optimizer/button.py b/custom_components/heatpump_optimizer/button.py
index 6f94c7ebd8..447fdddf04 100644
--- a/custom_components/heatpump_optimizer/button.py
+++ b/custom_components/heatpump_optimizer/button.py
@@ -26,12 +26,16 @@ import logging
 
 from homeassistant.components.button import ButtonEntity
 from homeassistant.core import HomeAssistant
-from homeassistant.exceptions import HomeAssistantError
+from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
 from homeassistant.helpers.entity_platform import AddEntitiesCallback
 
-from . import debugger
+from . import debugger, sysid
 from .const import DOMAIN
-from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
+from .coordinator import (
+    HeatPumpOptimizerConfigEntry,
+    HeatPumpOptimizerCoordinator,
+    ProcessWorkerUnavailable,
+)
 from .entity import HeatPumpOptimizerEntity, off_the_action
 
 _LOGGER = logging.getLogger(__name__)
@@ -153,7 +157,28 @@ class SystemIdentificationButton(_OptimizerButtonBase):
         )
 
     async def async_press(self) -> None:
-        off_the_action(self, self.coordinator.async_arm_system_identification())
+        """Arm the experiment, raising when nothing was armed (D10-s1-02).
+
+        The arm is a synchronous decision, so the refusal reaches the press;
+        the refresh that publishes the armed phase runs off the action, as
+        the optimize-now press's does.
+        """
+        refused = self.coordinator.arm_system_identification()
+        off_the_action(self, self.coordinator.async_request_refresh())
+        if refused == sysid.ARM_REFUSED_DISABLED:
+            raise ServiceValidationError(
+                f"System identification is turned off for {self._entry.entry_id}",
+                translation_domain=DOMAIN,
+                translation_key="system_identification_disabled",
+                translation_placeholders={"entry_ids": self._entry.entry_id},
+            )
+        if refused is not None:
+            raise ServiceValidationError(
+                f"System identification was not armed for {self._entry.entry_id}: {refused}",
+                translation_domain=DOMAIN,
+                translation_key="system_identification_not_armed",
+                translation_placeholders={"entry_ids": self._entry.entry_id, "reason": refused},
+            )
 
 
 class ResetComfortWeightButton(_OptimizerButtonBase):
@@ -214,7 +239,18 @@ class DiagnoseIntervalButton(_OptimizerButtonBase):
         )
 
     async def async_press(self) -> None:
-        off_the_action(self, self.coordinator.async_diagnose_interval())
+        """Run the diagnosis, raising as the ``diagnose_interval`` action does
+        when the worker cannot run it (D10-s1-02)."""
+        try:
+            await self.coordinator.async_diagnose_interval()
+        except ProcessWorkerUnavailable as err:
+            raise HomeAssistantError(
+                f"The interval diagnosis could not run for {self._entry.entry_id}: {err}",
+                translation_domain=DOMAIN,
+                translation_key="diagnose_interval_failed",
+                translation_placeholders={"entry_ids": self._entry.entry_id, "error": str(err)},
+            ) from err
+        off_the_action(self, self.coordinator.async_request_refresh())
 
 
 class DebugFinalizeButton(_OptimizerButtonBase):
diff --git a/custom_components/heatpump_optimizer/climate.py b/custom_components/heatpump_optimizer/climate.py
index 65980abe97..eb423db1ac 100644
--- a/custom_components/heatpump_optimizer/climate.py
+++ b/custom_components/heatpump_optimizer/climate.py
@@ -33,7 +33,7 @@ from .const import (
 from .coordinator import HeatPumpOptimizerConfigEntry, HeatPumpOptimizerCoordinator
 from .entity import HeatPumpOptimizerEntity, commanded_power_kw, publish_then_refresh
 from .entity import effective_outdoor, payload_number, zone_setpoint_attributes
-from .entity import dhw_split_attributes
+from .entity import PayloadFlagMixin, dhw_split_attributes
 from .entry_config import EntryConfig
 
 _LOGGER = logging.getLogger(__name__)
@@ -70,7 +70,7 @@ async def async_setup_entry(
     async_add_entities([HeatPumpOptimizerClimate(coordinator, entry)])
 
 
-class HeatPumpOptimizerClimate(HeatPumpOptimizerEntity, ClimateEntity):
+class HeatPumpOptimizerClimate(PayloadFlagMixin, HeatPumpOptimizerEntity, ClimateEntity):
     """Climate entity for the Heat Pump Optimizer."""
 
     # The device's main feature: a device-named entity (name None) takes the
@@ -123,17 +123,12 @@ class HeatPumpOptimizerClimate(HeatPumpOptimizerEntity, ClimateEntity):
         self._attr_min_temp = config.min_temperature
         self._attr_max_temp = config.max_temperature
 
-    @property
-    def available(self) -> bool:
-        """Unavailable while the indoor thermometer has not read.
-
-        ``native_current_temperature`` used to return ``ThermalState.room_temperature``
-        (21.0 °C) on a default install with no indoor entity, and the climate
-        entity stayed available, so the thermostat card published that
-        constructor default as a measurement (A3(e)).
-        """
-        flags = (self._data()).get("reading_ok") or {}
-        return bool(super().available and flags.get("upper_floor_temperature"))
+    # Unavailable while the indoor thermometer has not read.
+    # ``native_current_temperature`` used to return ``ThermalState.room_temperature``
+    # (21.0 °C) on a default install with no indoor entity, and the climate
+    # entity stayed available, so the thermostat card published that
+    # constructor default as a measurement (A3(e)).
+    _available_flag = ("reading_ok", "upper_floor_temperature")
 
     @property
     def native_current_temperature(self) -> float | None:
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 24858c41b9..1340ed8394 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -3,6 +3,7 @@ from __future__ import annotations
 
 import hashlib
 import logging
+import math
 from collections.abc import Awaitable, Callable, Iterable, Mapping
 from functools import partial
 from typing import TYPE_CHECKING, Any, Final, NamedTuple, Protocol, cast
@@ -53,7 +54,6 @@ from .const import (
     DEFAULT_PRICE_VAT,
     DEFAULT_PRICE_SURCHARGE,
     PRICE_SOURCE_ENTITY,
-    PRICE_SOURCE_TIBBER,
     PRICE_SOURCES,
     CONF_WEATHER_ENTITY,
     CONF_INDOOR_TEMP_ENTITY,
@@ -437,7 +437,6 @@ from .const import (
     DEFAULT_PV_EFFICIENCY,
     DEFAULT_PV_EXPORT_PRICE,
     CONF_AWAY_PRESENCE_ENTITY,
-    CONF_AWAY_RETURN_ENTITY,
     CONF_AWAY_TEMPERATURE,
     CONF_AWAY_DHW_MIN_TEMP,
     DEFAULT_AWAY_TEMPERATURE,
@@ -815,10 +814,7 @@ def _widen_to_fit(
             number_value = float(value)
         except (TypeError, ValueError):
             continue
-        if number_value != number_value or number_value in (
-            float("inf"),
-            float("-inf"),
-        ):
+        if not math.isfinite(number_value):
             continue
         if fitted_low is not None and number_value < fitted_low:
             fitted_low = number_value
@@ -827,13 +823,32 @@ def _widen_to_fit(
     if fitted_low == low and fitted_high == high:
         return None
     config: selector.NumberSelectorConfig = {**number.config}
+    step = config.get("step")
     if fitted_low is not None:
-        config["min"] = fitted_low
+        config["min"] = _on_grid(low, fitted_low, low, step, math.floor)
     if fitted_high is not None:
-        config["max"] = fitted_high
+        config["max"] = _on_grid(low, fitted_high, high, step, math.ceil)
     return selector.NumberSelector(selector.NumberSelectorConfig(**config))
 
 
+def _on_grid(
+    base: Any, value: float, declared: Any, step: Any, rounding: Callable[[float], int]
+) -> float:
+    """A widened bound ``value`` moved outward onto the field's own ``base + k * step`` grid (D14-s1-01).
+
+    A slider's and a number box's grid starts at ``min``: a min widened to a
+    stored 14.7 on a 0.5 grid put every nominal value of the field, its
+    default included, off the reachable set. ``rounding`` is ``math.floor``
+    for a lower bound and ``math.ceil`` for an upper one. A bound left at its
+    ``declared`` value, a step of ``"any"`` and a field with no ``min`` keep
+    ``value``: only what the widening moved is snapped.
+    """
+    if value == declared or base is None or not isinstance(step, (int, float)) or step <= 0:
+        return value
+    low, grain = float(base), float(step)
+    return round(low + rounding(round((value - low) / grain, 9)) * grain, 9)
+
+
 def _fit_stored_values(schema: Any) -> tuple[Any, list[str]]:
     """Schema with every numeric field widened to admit what it displays.
 
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 233a4eff49..5cce8b55d7 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -1932,8 +1932,9 @@ INPUT_PLAUSIBLE_RANGE_C: Final = {
 # --- Entity families (N-name-sort barrier, #1760) ---------------------------
 #
 # A family is a translation key's lead token -- the token the suggested
-# object id is already built from -- plus the explicit overrides below for
-# members homed elsewhere. tests/entities.py holds the one check this
+# object id is built from -- plus the explicit overrides below for members
+# homed elsewhere, whose suggested object id leads with the family
+# (entity._pin_identity). tests/entities.py holds the check this
 # declaration feeds: every family of two or more members must form one
 # contiguous run in the English and Swedish name sorts. Before this table
 # existed, family membership was declared nowhere, and eight fixes (#174,
@@ -1944,9 +1945,10 @@ ENTITY_FAMILY_OVERRIDES: Final[dict[str, str]] = {
     # The accuracy readout sorts with its prediction sensor (#1668), not
     # among the diagnose buttons' other neighbours.
     "diagnose_last_interval": "prediction",
-    # The four lifetime meters left the Cost family: their names lead with
-    # the meters' own token so the name sort keeps them in one run (#1668);
-    # entity ids and translation keys are untouched.
+    # The four lifetime meters left the Cost family. Their names lead with
+    # the meters' own token, so the name sort keeps them in one run (#1668).
+    # Their suggested object ids lead with it too (entity._pin_identity,
+    # D8-s2-02). Translation keys and unique ids are untouched.
     "cost_total_heating": "lifetime",
     "space_heating_cost": "lifetime",
     "space_heating_energy": "lifetime",
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 4dbd33b29a..a8616c6102 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -189,7 +189,6 @@ from .const import (
     INTERNAL_GAINS_MIN_UA_CONFIDENCE,
     CONFIDENCE_MARGIN_CAP_C,
     MOLD_SURFACE_RH_LIMIT,
-    SCORE_ALPHA,
     SCORE_FREE_SPAN_RESET,
     TEMPERATURE_UNIT_TO_C,
     OUTDOOR_AIR_RANGE_C,
@@ -275,7 +274,6 @@ from .manual_plan import (
 from .price_model import (
     PriceShapeLearner,
     PriceShapeModel,
-    TIBBER_API_URL,
     _raw_value,
     entity_priced,
     extend_price_series,
@@ -340,7 +338,6 @@ from .wood_fuel import (
 )
 from .thermal_model import (
     TANK_ROOM_AMBIENT_TEMP,
-    WATER_SPECIFIC_HEAT,
     ThermalModel,
     ThermalParameters,
     ThermalState,
@@ -375,6 +372,7 @@ from .dhw_schedule import (
     overlap_fraction,
     parse_weekly_windows,
     parse_windows,
+    windows_in_force,
 )
 from .optimizer import (
     ForecastSeries,
@@ -3755,6 +3753,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # The live detector, never a solve's copy of it: no solve runs
             # in comfort, boost or off to refresh one (#1736 H4).
             external_heat_active=lambda: bool(self._external_heat_active),
+            holidays=lambda now: away_mode.holiday_dates(self.hass, _ctx_of(self)._config.holiday_calendar_entity, now),
         )
         # #193's W5-G10: the disinfection cycle, its ceilings and its three
         # repair notices are their own subsystem. It reads the published
@@ -4475,15 +4474,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # With hot water disabled (or no schedule) there is no frame to
             # exploit and the loop is simply left on — never abandoned in
             # whatever state the last schedule-driven command left it.
-            windows = (
-                list(params.dhw_windows)
-                if params.dhw_enabled and params.dhw_windows_active
-                else []
-            )
-            on, reason = pump_schedule.vvc_should_run(
-                now.hour + now.minute / 60.0,
-                windows,
-                ctx._config.vvc_lead_minutes,
+            scheduled = params.dhw_enabled and params.dhw_windows_active
+            on, reason = pump_schedule.vvc_should_run_at(
+                now, params if scheduled else None, ctx._config.vvc_lead_minutes,
+                away_mode.holiday_dates(self.hass, ctx._config.holiday_calendar_entity, now),
             )
             await self._async_set_pump(vvc_entity, on, reason)
 
@@ -5990,17 +5984,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             },
         )
 
-    def _dhw_effective_windows(self) -> list[Any]:
-        """Demand windows the optimizer is actually planning against."""
-        result = self._optimization_result
-        planned = (result.predictive_info or {}).get("dhw_windows") if result else None
-        if planned:
-            try:
-                return parse_windows(planned)
-            except DHWWindowError:
-                pass
-        windows: list[Any] = getattr(self, "_ctx", self)._thermal_params.dhw_demand_windows
-        return windows
+    def _dhw_effective_windows(self, days: int = 0) -> list[Any]:
+        """Demand windows the optimizer plans against, today or ``days`` on (``windows_in_force``)."""
+        ctx, now = getattr(self, "_ctx", self), dt_util.now()
+        holidays = away_mode.holiday_dates(self.hass, ctx._config.holiday_calendar_entity, now)
+        return windows_in_force(ctx._thermal_params, self._optimization_result, now, holidays, days)
 
     def _dhw_in_demand_window(self) -> bool:
         """Whether hot water is required right now."""
@@ -6011,7 +5999,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     def _dhw_next_window_in_hours(self) -> float | None:
         """Hours until the next DHW demand window opens (0 if inside one)."""
         hours = hours_until_next_window(
-            _dhw_current_hour(), self._dhw_effective_windows()
+            _dhw_current_hour(), self._dhw_effective_windows(), self._dhw_effective_windows(1)
         )
         return round(hours, 2) if hours is not None else None
 
@@ -10630,7 +10618,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         """Service/button entry for #52; publishes on the insight view.
 
         The last SETTLED interval, from a snapshot on the loop: the worker
-        gets copies, never this object (#1529).
+        gets copies, never this object (#1529). The caller asks for the
+        refresh that publishes it: the press off its action (D10-s1-02).
         """
         report: DiagnosisReport | None = await _await_process(
             self.hass,
@@ -10643,7 +10632,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 "No settled interval to diagnose yet — one full "
                 "optimization interval must pass first"
             )
-        await self.async_request_refresh()
         return report
 
     async def _maybe_refresh_price_tile(self, record: SolveRecord) -> None:
@@ -10999,14 +10987,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     def system_identification_active(self) -> bool:
         return self._sysid.active
 
-    async def async_arm_system_identification(self) -> None:
-        """Arm a step-response experiment for the next suitable moment."""
+    def arm_system_identification(self) -> str | None:
+        """Arm a step-response experiment for the next suitable moment; why not, else ``None``."""
         ctx = getattr(self, "_ctx", self)
-        sysid.arm_from_config(
+        return sysid.arm_refusal(
             self._sysid, dt_util.now(), ctx._config, ctx._thermal_params,
             self._house_heat_loss_samples, self._accuracy.draw,
         )
-        await self.async_request_refresh()
 
     async def _run_system_identification(self, prices: np.ndarray) -> None:
         """Advance sysid and override the plan when the experiment commands heat.
diff --git a/custom_components/heatpump_optimizer/debugger.py b/custom_components/heatpump_optimizer/debugger.py
index b09a76a66e..38394d1e3e 100644
--- a/custom_components/heatpump_optimizer/debugger.py
+++ b/custom_components/heatpump_optimizer/debugger.py
@@ -320,7 +320,13 @@ def collection_window(rows: list[dict[str, Any]], now: datetime) -> dict[str, An
 
 
 async def _solver_smoke(coordinator: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
-    """One what-if solve with no override, which the live plan should equal."""
+    """One what-if solve with no override, which the live plan should equal.
+
+    ``week_solve_ms`` spreads the rows where a solve ran: the not-run publish
+    after a restart (``_apply_unsolved_payload``) carries ``solve_time_ms`` 0,
+    an inert value and never a duration (D15-s3-01), so a row whose recorded
+    time is not positive is left out.
+    """
     began = time.monotonic()
     result = await coordinator.async_simulate({}, limited=False)
     return {
@@ -328,7 +334,7 @@ async def _solver_smoke(coordinator: Any, rows: list[dict[str, Any]]) -> dict[st
         "error": result.get("error"),
         "cost_delta": result.get("cost_delta"),
         "week_solve_ms": spread(
-            [row["payload_solve_time_ms"] for row in rows if "payload_solve_time_ms" in row]),
+            [ms for row in rows if (ms := row.get("payload_solve_time_ms") or 0) > 0]),
     }
 
 
diff --git a/custom_components/heatpump_optimizer/dhw_learning.py b/custom_components/heatpump_optimizer/dhw_learning.py
index c912d13db2..f4c313e792 100644
--- a/custom_components/heatpump_optimizer/dhw_learning.py
+++ b/custom_components/heatpump_optimizer/dhw_learning.py
@@ -18,9 +18,9 @@ from __future__ import annotations
 
 import logging
 import math
-from collections.abc import Callable
+from collections.abc import Callable, Collection
 from dataclasses import dataclass, field
-from datetime import datetime
+from datetime import date, datetime
 from typing import Any
 
 import numpy as np
@@ -38,6 +38,7 @@ from .const import (
     DHW_DAYTYPE_BLEND_K,
     DOMAIN,
 )
+from .dhw_schedule import hour_in_windows, windows_in_force
 from .dhw_draws import DrawStats, labels_for, window_label as draw_window_label
 from .inputs import plausible_c
 from .thermal_model import TANK_ROOM_AMBIENT_TEMP, ThermalParameters
@@ -153,7 +154,8 @@ class DhwProfileLearner:
     no snapshot is ever edited in place (D7-s1-82). ``frozen`` answers why learning should be skipped this
     interval, ``heating_active`` whether the plan is heating the tank now, and
     ``external_heat_active`` whether a wood burn is driving the tank — the
-    three coordinator facts the learner observes and never owns.
+    three coordinator facts the learner observes and never owns. ``holidays``
+    names the holiday dates around an instant, for the window in force.
     """
 
     def __init__(
@@ -166,8 +168,10 @@ class DhwProfileLearner:
         frozen: Callable[[str], str | None],
         heating_active: Callable[[], bool],
         external_heat_active: Callable[[], bool],
+        holidays: Callable[[datetime], Collection[date]] = lambda _now: (),
     ) -> None:
         self._params = params
+        self._holidays = holidays
         self._publish = publish
         self._frozen = frozen
         self._heating_active = heating_active
@@ -499,10 +503,13 @@ class DhwProfileLearner:
         cap = params.dhw_store.capacity_kwh_per_c
         intensity = max(0.0, temp_drop / dt_h - self._standby_rate(previous_temp))
         energy_kwh = intensity * dt_h * cap  # beyond standby
+        # The stats table is keyed by the flat windows, as the planner reads
+        # it; whether the draw fell in a window is the day's own answer
+        # (dhw_schedule.windows_in_force, D17-s3-51).
         windows = params.dhw_demand_windows
-        label = draw_window_label(
-            now.hour + now.minute / 60.0, windows
-        )
+        hour = now.hour + now.minute / 60.0
+        in_force = hour_in_windows(hour, windows_in_force(params, None, now, self._holidays(now)))
+        label = draw_window_label(hour, windows) if in_force else ""
         self.draw_stats.prune(labels_for(windows))
         before = {k: len(v) for k, v in self.draw_stats.reservoirs.items()}
         taken_kwh = self.draw_stats.take_back(recovered_k * cap)
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index cd0e495d1c..5a8aa8adf9 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -32,6 +32,7 @@ from .dhw_draws import window_label as draw_window_label
 from .dhw_schedule import (
     FULL_DAY,
     Window,
+    cyclic_span,
     format_windows,
     hour_in_windows,
     hours_until_next_window,
@@ -62,28 +63,48 @@ _LOGGER = logging.getLogger(__name__)
 
 
 def _dhw_windows_at(
-    weekly: list[list[Window]] | None,
-    step_weekdays: np.ndarray | None,
+    params: ThermalParameters,
+    step_weekdays: np.ndarray | list[int] | None,
     index: int,
     windows: list[Window],
-    holiday_windows: list[Window] | None,
     holiday_flags: np.ndarray | None,
-    day_overrides: list[list[Window] | None] | None = None,
 ) -> list[Window]:
+    """The windows in force at entry ``index`` of the step arrays: ``params``' day tiers."""
     weekday = None if step_weekdays is None else int(step_weekdays[index])
     holiday = False
     if holiday_flags is not None and index < len(holiday_flags):
         holiday = bool(holiday_flags[index])
     return windows_for_day(
-        weekly,
+        params.dhw_weekly_windows,
         weekday,
         windows,
-        holiday_windows=holiday_windows,
+        holiday_windows=getattr(params, "dhw_holiday_windows", None),
         holiday=holiday,
-        day_overrides=day_overrides,
+        day_overrides=getattr(params, "dhw_day_windows", None),
     )
 
 
+def _dhw_next_window_hours(
+    hours_mod: np.ndarray, weekdays: np.ndarray | None, windows: list[Window],
+    params: ThermalParameters, holiday_flags: np.ndarray | None,
+) -> float | None:
+    """Hours to the next demand window in the day's windows (D17-s3-51), never the flat union.
+
+    Today's are the ones ``in_window[0]`` tests (entry 1); tomorrow's the first step past
+    midnight's, else, on a horizon ending first, the next weekday's with no holiday tier.
+    """
+    if not len(hours_mod):
+        return None  # no step to read a day from
+    today = _dhw_windows_at(params, weekdays, 1, windows, holiday_flags)
+    wraps = np.nonzero(np.diff(hours_mod) < 0.0)[0]
+    if len(wraps):
+        tomorrow = _dhw_windows_at(params, weekdays, int(wraps[0]) + 2, windows, holiday_flags)
+    else:
+        nxt = None if weekdays is None else [cyclic_span(int(d), int(d) + 1, 7)[-1] for d in weekdays[1:2]]
+        tomorrow = _dhw_windows_at(params, nxt, 0, windows, None)
+    return hours_until_next_window(float(hours_mod[0]), today, tomorrow)
+
+
 # How far either side of a contended step space heating may look for spare
 # compressor capacity when its energy is displaced by hot water. Beyond a few
 # hours the building has already lost the heat, so a cheap slot that far away
@@ -960,44 +981,14 @@ class DhwPlanner:
         # overrides (#1260) ride the same array: a flat spec with overrides
         # set computes weekdays too, and `windows_for_day` applies the
         # whole precedence chain (override > holiday > default) per step.
-        weekly = params.dhw_weekly_windows
-        holiday_windows = getattr(params, "dhw_holiday_windows", None)
-        day_overrides = getattr(params, "dhw_day_windows", None)
+        def day(index: int) -> list[Window]:
+            return _dhw_windows_at(params, step_weekdays, index, windows, holiday_flags)
+
         in_window = np.array(
-            [
-                hour_in_windows(
-                    float(h),
-                    _dhw_windows_at(
-                        weekly,
-                        step_weekdays,
-                        i + 1,
-                        windows,
-                        holiday_windows,
-                        holiday_flags,
-                        day_overrides,
-                    ),
-                )
-                for i, h in enumerate(hours_mod)
-            ],
-            dtype=bool,
+            [hour_in_windows(float(h), day(i + 1)) for i, h in enumerate(hours_mod)], dtype=bool
         )
         prev_in_window = np.array(
-            [
-                hour_in_windows(
-                    float(h) - dt,
-                    _dhw_windows_at(
-                        weekly,
-                        step_weekdays,
-                        i,
-                        windows,
-                        holiday_windows,
-                        holiday_flags,
-                        day_overrides,
-                    ),
-                )
-                for i, h in enumerate(hours_mod)
-            ],
-            dtype=bool,
+            [hour_in_windows(float(h) - dt, day(i)) for i, h in enumerate(hours_mod)], dtype=bool
         )
         window_starts = np.where(in_window & ~prev_in_window)[0].tolist()
 
@@ -1348,9 +1339,7 @@ class DhwPlanner:
             suppress_steps = int(np.sum(mask & (schedule > 1e-6)))
             schedule = np.where(mask, 0.0, schedule)
 
-        next_window = hours_until_next_window(
-            float(hours_mod[0]) if n_steps else 0.0, windows
-        )
+        next_window = _dhw_next_window_hours(hours_mod, step_weekdays, windows, params, holiday_flags)
 
         # A manual plan overrides *timing* last, after the economics and the
         # external-heat suppression, because it expresses the user's explicit
diff --git a/custom_components/heatpump_optimizer/dhw_schedule.py b/custom_components/heatpump_optimizer/dhw_schedule.py
index e188ce8021..c1552d5dc9 100644
--- a/custom_components/heatpump_optimizer/dhw_schedule.py
+++ b/custom_components/heatpump_optimizer/dhw_schedule.py
@@ -55,7 +55,8 @@ from __future__ import annotations
 
 import logging
 import re
-from collections.abc import Mapping
+from collections.abc import Collection, Mapping
+from datetime import date, datetime, timedelta
 from typing import Any, Final
 
 from . import const
@@ -417,6 +418,43 @@ def windows_for_day(
     return weekly[max(0, min(6, int(weekday)))]
 
 
+def windows_in_force(
+    params: Any,
+    plan: Any,
+    when: datetime,
+    holiday_dates: Collection[date] = (),
+    days: int = 0,
+) -> list[Window]:
+    """The hot-water demand windows in force at ``when`` (D17-s3-51).
+
+    ``windows_for_day``'s chain over ``params``' day-aware fields -- the
+    resolution the planner applies to every step (``dhw_planner._dhw_windows_at``)
+    -- for a reader holding a clock instead of a step array. A clock tested
+    against the flat every-day union instead reads a weekend window open on a
+    weekday morning. The chain ends in the planned windows ``plan`` (the last
+    optimization result, or ``None``) published, learned ones included, where
+    they parse, else ``params.dhw_demand_windows``. ``days`` moves to a later
+    calendar day of ``when``'s date: date arithmetic, never wall-clock.
+    """
+    info = getattr(plan, "predictive_info", None) or {}
+    fallback = list(params.dhw_demand_windows)
+    if info.get("dhw_windows"):
+        try:
+            fallback = parse_windows(info["dhw_windows"])
+        except DHWWindowError:
+            pass
+    # The day-aware fields read as the planner reads them (None: no tier).
+    day = when.date() + timedelta(days=days)
+    return windows_for_day(
+        getattr(params, "dhw_weekly_windows", None),
+        day.weekday(),
+        fallback,
+        holiday_windows=getattr(params, "dhw_holiday_windows", None),
+        holiday=day in holiday_dates,
+        day_overrides=getattr(params, "dhw_day_windows", None),
+    )
+
+
 def _split_wrapping(windows: list[Window]) -> list[Window]:
     """Split midnight-wrapping windows into non-wrapping segments."""
     flat: list[Window] = []
@@ -512,22 +550,23 @@ def overlap_fraction(
     return max(0.0, min(1.0, covered / length))
 
 
-def hours_until_next_window(hour: float, windows: list[Window]) -> float | None:
+def hours_until_next_window(
+    hour: float, windows: list[Window], tomorrow: list[Window] | None = None
+) -> float | None:
     """Hours from ``hour`` until the next window starts (0.0 when inside one).
 
-    Returns None when no windows are configured.
+    ``windows`` are today's; a start already passed reads in ``tomorrow``'s,
+    the next day's windows in force (``windows_in_force``), or today's again
+    when ``None`` -- the every-day schedule. Returns None when neither day
+    has a window.
     """
-    if not windows:
-        return None
-    if hour_in_windows(hour, windows):
+    if windows and hour_in_windows(hour, windows):
         return 0.0
     h = hour % 24.0
-    best: float | None = None
-    for start, _ in windows:
-        delta = (start - h) % 24.0
-        if best is None or delta < best:
-            best = delta
-    return best
+    starts = [start - h for start, _ in windows if start > h] + [
+        start + 24.0 - h for start, _ in (windows if tomorrow is None else tomorrow)
+    ]
+    return min(starts, default=None)
 
 
 def is_valid_spec(spec: str) -> bool:
diff --git a/custom_components/heatpump_optimizer/entity.py b/custom_components/heatpump_optimizer/entity.py
index 2062082c4f..24c0d37880 100644
--- a/custom_components/heatpump_optimizer/entity.py
+++ b/custom_components/heatpump_optimizer/entity.py
@@ -25,6 +25,7 @@ import numpy as np
 from homeassistant.helpers.entity import DeviceInfo
 from homeassistant.helpers.update_coordinator import CoordinatorEntity
 
+from .const import ENTITY_FAMILY_OVERRIDES
 from .payload import Payload
 
 if TYPE_CHECKING:  # coordinator imports this module
@@ -310,15 +311,22 @@ class HeatPumpOptimizerEntity(CoordinatorEntity["HeatPumpOptimizerCoordinator"])
         is one) would derive *translated* object ids from the translation-keyed
         name, breaking the dashboard card's id-suffix contract on fresh
         installs. The object id is ``heat_pump_optimizer_`` plus the
-        translation key; ``object_id`` replaces it only for the climate entity,
-        whose id predates the scheme.
+        translation key. Where ``const.ENTITY_FAMILY_OVERRIDES`` homes a key
+        outside its own lead token, the declared family leads, so the id sort
+        keeps the family in one run as the name sort does (D8-s2-02). New
+        installs only: the registry keeps an existing entity's id by
+        ``unique_id``. ``object_id`` replaces the rule only for the climate
+        entity, whose id predates the scheme.
         """
         self._entry = entry
         self._attr_unique_id = f"{entry.entry_id}_{key}"
         if translation_key is not None:
             self._attr_translation_key = translation_key
         if object_id is None:
-            object_id = f"heat_pump_optimizer_{self._attr_translation_key}"
+            translation_key = self._attr_translation_key or ""
+            family = ENTITY_FAMILY_OVERRIDES.get(translation_key)
+            lead = f"{family}_" if family and not translation_key.startswith(f"{family}_") else ""
+            object_id = f"heat_pump_optimizer_{lead}{translation_key}"
         self.entity_id = f"{self._platform_domain}.{object_id}"
 
     def _data(self) -> Payload:
@@ -428,6 +436,28 @@ class ConfiguredInputMixin(HeatPumpOptimizerEntity):
         return bool(super().available and self.entity_registry_enabled_default)
 
 
+class PayloadFlagMixin(HeatPumpOptimizerEntity):
+    """An entity that answers only while one flag of the payload is set.
+
+    The flag is the coordinator's own statement that the feature has an answer:
+    a top-level key (``pv_enabled``) or one flag of one block
+    (``wood_fuel.ready``, ``power_headroom.available``, ``reading_ok.<input>``);
+    a missing block or flag is unavailable, never a default.
+    """
+
+    #: Key path from the payload to the flag that must be truthy for the entity
+    #: to be available: ``(key,)`` or ``(block, flag)``. No default: a subclass
+    #: that forgets it raises on ``available``, never stays unavailable silently.
+    _available_flag: tuple[str, ...]
+
+    @property
+    def available(self) -> bool:
+        gate: Any = self._data()
+        for key in self._available_flag:
+            gate = (gate or {}).get(key)
+        return bool(super().available and gate)
+
+
 class DHWEntityMixin(HeatPumpOptimizerEntity):
     """A hot-water entity, gated on the install actually having hot water.
 
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 8fc1cc6845..6d9b93ac11 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -176,7 +176,6 @@ from .const import (
     CONF_POWER_ENTITY,
     CONF_SPACE_SETPOINT_HIGH_LIMIT_ENTITY,
     CONF_SPACE_SETPOINT_LOW_LIMIT_ENTITY,
-    CONF_SPACE_SETPOINT_POWER_FEEDBACK,
     CONF_VALVE_OUTLET_TEMP_ENTITY,
     DEFAULT_FLOW_HEAT_C,
     DOMAIN,
diff --git a/custom_components/heatpump_optimizer/pump_schedule.py b/custom_components/heatpump_optimizer/pump_schedule.py
index f824d32323..03e4884f53 100644
--- a/custom_components/heatpump_optimizer/pump_schedule.py
+++ b/custom_components/heatpump_optimizer/pump_schedule.py
@@ -22,22 +22,49 @@ transitions, and only for entities the user explicitly configured.
 """
 from __future__ import annotations
 
-from collections.abc import Sequence
+from collections.abc import Collection, Sequence
+from datetime import date, datetime
+from typing import Any
 
 from .const import SPACE_PUMP_FLOOR_MARGIN_C
-from .dhw_schedule import Window, hour_in_windows, hours_until_next_window
+from .dhw_schedule import Window, hour_in_windows, hours_until_next_window, windows_in_force
+
+def vvc_should_run_at(
+    now: datetime, params: Any | None, lead_minutes: float, holidays: Collection[date] = (),
+) -> tuple[bool, str]:
+    """``vvc_should_run`` at ``now`` on the windows in force (D17-s3-51).
+
+    Today's windows (``dhw_schedule.windows_in_force``) decide the window,
+    and tomorrow's the lead across midnight. ``params`` ``None`` is no
+    schedule: hot water is always required.
+    """
+    hour = now.hour + now.minute / 60.0
+    if params is None:
+        return vvc_should_run(hour, None, lead_minutes)
+    return vvc_should_run(
+        hour,
+        windows_in_force(params, None, now, holidays),
+        lead_minutes,
+        windows_in_force(params, None, now, holidays, days=1),
+    )
+
 
 def vvc_should_run(
-    hour_of_day: float, windows: list[Window], lead_minutes: float
+    hour_of_day: float, windows: list[Window] | None, lead_minutes: float,
+    tomorrow: list[Window] | None = None,
 ) -> tuple[bool, str]:
     """Whether the hot-water circulation loop should run right now.
 
     Inside a demand window, or within the lead time before one opens, the
     loop must be hot; anywhere else it is pure standby loss. With no
-    windows configured hot water is "always required" and the pump is
-    simply left on — the schedule can only save where a schedule exists.
+    schedule (``None``) hot water is "always required" and the pump is
+    simply left on — the schedule can only save where a schedule exists. An
+    empty list is a schedule with no window today (a day-aware spec's day
+    with no segment, ``dhw_schedule.windows_in_force``): nothing to keep hot.
+    ``tomorrow`` is the next day's windows, which a lead crossing midnight
+    reads; ``None`` reads today's again, the every-day schedule.
     """
-    if not windows:
+    if windows is None:
         return True, "no demand windows; hot water always required"
     hour = float(hour_of_day) % 24.0
     if hour_in_windows(hour, windows):
@@ -47,7 +74,7 @@ def vvc_should_run(
     # inside one". Probing the single instant left a hole in the final
     # approach to any window shorter than the lead — off during exactly
     # the minutes the pre-heat exists for.
-    until = hours_until_next_window(hour, list(windows))
+    until = hours_until_next_window(hour, list(windows), tomorrow)
     if lead_h > 0.0 and until is not None and 0.0 < until <= lead_h:
         return True, f"window opens within {int(lead_minutes)} min; pre-heating the loop"
     return False, "outside every demand window"
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index ed05156011..ab1324a768 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -51,7 +51,7 @@ from .entity import ConfiguredInputMixin as _ConfiguredInputMixin
 from .entity import DHWEntityMixin as _DHWEntityMixin
 from .entity import HeatPumpOptimizerEntity, commanded_power_kw
 from .entity import effective_outdoor, payload_number, zone_setpoint_attributes
-from .entity import dhw_split_attributes
+from .entity import PayloadFlagMixin, dhw_split_attributes
 from .entry_config import EntryConfig
 from .payload import Payload
 from .mixing_valve import is_throttling
@@ -72,6 +72,11 @@ ECL110_TOPIC_SLOTS = (
     CONF_HEAT_CURVE_DISPLACE_ENTITY,
 )
 
+#: A temperature DIFFERENCE in K/degC (D10-s2-04): TEMPERATURE would convert it
+#: as an absolute for a Fahrenheit user. Home Assistant 2025.11.0 added this class,
+#: above hacs.json's floor, where it reads None and the readout stays classless.
+_TEMPERATURE_DELTA = getattr(SensorDeviceClass, "TEMPERATURE_DELTA", None)
+
 # Coordinator-fed and read-only: the coordinator serialises the one inbound
 # refresh, and no entity here calls out, so there is nothing to throttle
 # (parallel-updates, Silver).
@@ -530,24 +535,27 @@ class MonthlySavingsSensor(_WaitsForEvidenceMixin, HeatPumpOptimizerSensorBase):
         rows = (self._data()).get("savings_months")
         return rows if isinstance(rows, list) else []
 
+    def _open_saving(self) -> float | None:
+        """The open month's estimated saving: the one number both the state and
+        the availability read (D8-s1-03), ``None`` while the ledger has no open
+        row or withholds its saving (``old_basis``, ``below_meter_floor``)."""
+        for row in self._rows():
+            if isinstance(row, dict) and row.get("estimated"):
+                return payload_number(row.get("savings_sek"))
+        return None
+
     @property
     def _waiting_for(self) -> str | None:
-        # Closed months and no open row: the ledger holds the open month back
-        # until it has covered ``ledger.MIN_COVERAGE_HOURS``.
-        rows = self._rows()
-        if not rows:
-            return "settled_savings_month"
-        if any(isinstance(row, dict) and row.get("estimated") for row in rows):
+        # Closed months and no open saving: the ledger holds the open month
+        # back until it has covered ``ledger.MIN_COVERAGE_HOURS``.
+        if self._open_saving() is not None:
             return None
-        return "open_month_coverage"
+        return "open_month_coverage" if self._rows() else "settled_savings_month"
 
     @property
     def native_value(self) -> float | None:
-        for row in self._rows():
-            if isinstance(row, dict) and row.get("estimated"):
-                val = payload_number(row.get("savings_sek"))
-                return None if val is None else round(val, 2)
-        return None
+        val = self._open_saving()
+        return None if val is None else round(val, 2)
 
     @property
     def extra_state_attributes(self) -> dict[str, Any]:
@@ -1441,6 +1449,7 @@ class ECL110DisplaceSensor(_PayloadNumberMixin, _ConfiguredInputMixin, HeatPumpO
     """Current ECL110 displace command value."""
 
     _attr_state_class = SensorStateClass.MEASUREMENT
+    _attr_device_class = _TEMPERATURE_DELTA
     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
     _attr_suggested_display_precision = 1
     # ECL110 hardware is a per-install opt-in (its MQTT topics live on the
@@ -1463,6 +1472,7 @@ class ECL110EffectiveDisplaceSensor(_PayloadNumberMixin, _ConfiguredInputMixin,
     """Modeled effective displace after ECL110 PI/PID dynamics."""
 
     _attr_state_class = SensorStateClass.MEASUREMENT
+    _attr_device_class = _TEMPERATURE_DELTA
     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
     _attr_suggested_display_precision = 1
     # Same opt-in hardware as ECL110 Displace above, same gate and category.
@@ -1746,7 +1756,7 @@ class DHWHeatingPlanSensor(_DHWEntityMixin, _PlanSensorBase):
 # ---------------------------------------------------------------------------
 
 
-class MeasuredPowerSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
+class MeasuredPowerSensor(PayloadFlagMixin, _PayloadNumberMixin, HeatPumpOptimizerSensorBase):
     """The heat pump's actual electrical draw.
 
     Deliberately named to contrast with "Recommended Power", which is what the
@@ -1770,10 +1780,7 @@ class MeasuredPowerSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
     def __init__(self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry) -> None:
         super().__init__(coordinator, entry, "measured_power", "measured_power")
 
-    @property
-    def available(self) -> bool:
-        data = self._data()
-        return bool(super().available and data.get("measured_power_available"))
+    _available_flag = ("measured_power_available",)
 
     @property
     def extra_state_attributes(self) -> dict[str, Any]:
@@ -2018,6 +2025,7 @@ class PredictionAccuracySensor(_WaitsForEvidenceMixin, HeatPumpOptimizerSensorBa
     """
 
     _attr_state_class = SensorStateClass.MEASUREMENT
+    _attr_device_class = _TEMPERATURE_DELTA
     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
     _attr_entity_category = EntityCategory.DIAGNOSTIC
     _attr_suggested_display_precision = 2
@@ -2231,7 +2239,7 @@ def _sysid_outcome(view: Any) -> dict[str, Any] | None:
 # ---------------------------------------------------------------------------
 
 
-class MonthlyPeakSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
+class MonthlyPeakSensor(PayloadFlagMixin, _PayloadNumberMixin, HeatPumpOptimizerSensorBase):
     """The peak level this month's capacity tariff is currently based on."""
 
     _attr_state_class = SensorStateClass.MEASUREMENT
@@ -2248,12 +2256,7 @@ class MonthlyPeakSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
     def __init__(self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry) -> None:
         super().__init__(coordinator, entry, "monthly_peak", "cost_monthly_peak_power")
 
-    @property
-    def available(self) -> bool:
-        return bool(
-            super().available
-            and (self._data()).get("peak_tariff_enabled")
-        )
+    _available_flag = ("peak_tariff_enabled",)
 
     @property
     def extra_state_attributes(self) -> dict[str, Any]:
@@ -2282,7 +2285,7 @@ class MonthlyPeakSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
 # ---------------------------------------------------------------------------
 
 
-class PVSurplusSensor(HeatPumpOptimizerSensorBase):
+class PVSurplusSensor(PayloadFlagMixin, HeatPumpOptimizerSensorBase):
     """Forecast solar surplus available to the heat pump."""
 
     _attr_state_class = SensorStateClass.MEASUREMENT
@@ -2306,11 +2309,7 @@ class PVSurplusSensor(HeatPumpOptimizerSensorBase):
     def __init__(self, coordinator: HeatPumpOptimizerCoordinator, entry: HeatPumpOptimizerConfigEntry) -> None:
         super().__init__(coordinator, entry, "pv_surplus", "solar_surplus_forecast")
 
-    @property
-    def available(self) -> bool:
-        return bool(
-            super().available and (self._data()).get("pv_enabled")
-        )
+    _available_flag = ("pv_enabled",)
 
     @property
     def native_value(self) -> float | None:
@@ -2560,7 +2559,7 @@ class ContractComparisonSensor(
         return self._evidence_attributes("contract_comparison", "monthly_report")
 
 
-class PowerHeadroomSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
+class PowerHeadroomSensor(PayloadFlagMixin, _PayloadNumberMixin, HeatPumpOptimizerSensorBase):
     """How many kW the house can draw right now without new cost (#5).
 
     ``min(main fuse, capacity threshold) − current house draw``, clamped at
@@ -2588,10 +2587,7 @@ class PowerHeadroomSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
             coordinator, entry, "power_headroom", "cost_power_headroom"
         )
 
-    @property
-    def available(self) -> bool:
-        data = (self._data()).get("power_headroom") or {}
-        return bool(super().available and data.get("available"))
+    _available_flag = ("power_headroom", "available")
 
     @property
     def extra_state_attributes(self) -> dict[str, Any]:
@@ -2649,7 +2645,7 @@ class DHWSetpointAdvisorSensor(_PayloadNumberMixin, _DHWEntityMixin, HeatPumpOpt
 
 
 class MixedHotWaterSensor(
-    _PayloadNumberMixin, _DHWEntityMixin, _MeasuredTemperatureMixin, HeatPumpOptimizerSensorBase
+    PayloadFlagMixin, _PayloadNumberMixin, _DHWEntityMixin, _MeasuredTemperatureMixin, HeatPumpOptimizerSensorBase
 ):
     """The tank translated into shower terms (#28).
 
@@ -2689,11 +2685,7 @@ class MixedHotWaterSensor(
             coordinator, entry, "dhw_mixed_water", "dhw_mixed_water"
         )
 
-    @property
-    def available(self) -> bool:
-        return bool(
-            super().available and (self._data()).get("dhw_mixed")
-        )
+    _available_flag = ("dhw_mixed",)
 
     @property
     def extra_state_attributes(self) -> dict[str, Any]:
@@ -2860,7 +2852,7 @@ class OptimizationScoreSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
         return attrs
 
 
-class CompressorStartsSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
+class CompressorStartsSensor(PayloadFlagMixin, _PayloadNumberMixin, HeatPumpOptimizerSensorBase):
     """Realised compressor starts, counted from the meter (#55).
 
     State: lifetime starts. TOTAL_INCREASING, so long-term statistics and
@@ -2885,10 +2877,7 @@ class CompressorStartsSensor(_PayloadNumberMixin, HeatPumpOptimizerSensorBase):
             coordinator, entry, "compressor_starts", "compressor_starts"
         )
 
-    @property
-    def available(self) -> bool:
-        data = (self._data()).get("measured_power_available")
-        return bool(super().available and data)
+    _available_flag = ("measured_power_available",)
 
     @property
     def extra_state_attributes(self) -> dict[str, Any]:
diff --git a/custom_components/heatpump_optimizer/services.py b/custom_components/heatpump_optimizer/services.py
index 22ec38828a..cd40d5bd63 100644
--- a/custom_components/heatpump_optimizer/services.py
+++ b/custom_components/heatpump_optimizer/services.py
@@ -1302,6 +1302,7 @@ async def handle_diagnose_interval(hass: HomeAssistant, call: ServiceCall) -> di
         # live coordinator state off the loop (#1529).
         try:
             reports[entry_id] = await coord.async_diagnose_interval()
+            await coord.async_request_refresh()
         except ProcessWorkerUnavailable as err:
             # A worker that timed out or could not run the job: the service
             # call failed, so it says so in the shape the other services use,
diff --git a/custom_components/heatpump_optimizer/services.yaml b/custom_components/heatpump_optimizer/services.yaml
index 6c14153c27..e986d781b6 100644
--- a/custom_components/heatpump_optimizer/services.yaml
+++ b/custom_components/heatpump_optimizer/services.yaml
@@ -57,8 +57,9 @@ set_thermal_parameters:
         number:
           min: 0.1
           max: 60
-          step: 0.5
+          step: any
           unit_of_measurement: kWh/°C
+          mode: box
     slab_heat_transfer:
       required: false
       example: 0.8
@@ -66,8 +67,9 @@ set_thermal_parameters:
         number:
           min: 0.02
           max: 5.0
-          step: 0.1
+          step: any
           unit_of_measurement: kW/°C
+          mode: box
     heat_pump_cop_nominal:
       required: false
       example: 3.5
@@ -83,8 +85,9 @@ set_thermal_parameters:
         number:
           min: 0.25
           max: 60
-          step: 0.5
+          step: any
           unit_of_measurement: kWh/°C
+          mode: box
     lower_floor_thermal_mass:
       required: false
       example: 8.0
@@ -92,8 +95,9 @@ set_thermal_parameters:
         number:
           min: 0.25
           max: 60
-          step: 0.5
+          step: any
           unit_of_measurement: kWh/°C
+          mode: box
     inter_zone_heat_transfer:
       required: false
       example: 0.5
@@ -101,8 +105,9 @@ set_thermal_parameters:
         number:
           min: 0.01
           max: 3.0
-          step: 0.1
+          step: any
           unit_of_measurement: kW/°C
+          mode: box
     radiator_power_fraction:
       required: false
       example: 0.4
@@ -118,8 +123,9 @@ set_thermal_parameters:
         number:
           min: 0.01
           max: 50
-          step: 0.5
+          step: any
           unit_of_measurement: m²
+          mode: box
     solar_heat_gain_coefficient:
       required: false
       example: 0.7
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 64e36d0449..560e21a429 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -465,6 +465,12 @@
     "diagnose_interval_failed": {
       "message": "The interval diagnosis could not run for {entry_ids}: {error}"
     },
+    "system_identification_disabled": {
+      "message": "System identification is turned off for {entry_ids}: turn on \"Allow a one-off measurement experiment\" in the options to arm it"
+    },
+    "system_identification_not_armed": {
+      "message": "System identification was not armed for {entry_ids}: {reason}"
+    },
     "simulate_plan_failed": {
       "message": "The what-if simulation could not run for {entry_ids}: {error}"
     },
diff --git a/custom_components/heatpump_optimizer/sysid.py b/custom_components/heatpump_optimizer/sysid.py
index d73375a0a0..443bca4821 100644
--- a/custom_components/heatpump_optimizer/sysid.py
+++ b/custom_components/heatpump_optimizer/sysid.py
@@ -1827,7 +1827,7 @@ class SystemIdentification:
         #
         # The one-state branch is HARNESS-ONLY (#1395): production always arms
         # with a declared plant (``HeatPumpOptimizerCoordinator.
-        # async_arm_system_identification`` passes ``_thermal_params``), and a
+        # arm_system_identification`` passes ``_thermal_params``), and a
         # plant that fails the arm-time gate never finishes an experiment — so
         # ``_slab_pair`` is set on every ``_finish`` production reaches, and
         # ``identify()`` is entered zero times by the production call sequence.
@@ -1864,7 +1864,7 @@ class SystemIdentification:
 
     # HARNESS-ONLY (#1395). The production call sequence never enters
     # ``identify`` below: the coordinator always arms with a declared plant
-    # (``async_arm_system_identification`` passes ``_thermal_params``), so
+    # (``arm_system_identification`` passes ``_thermal_params``), so
     # ``_finish`` routes every experiment production can finish to
     # ``identify_slab``, and ``identify`` is entered zero times by that
     # sequence. #1330 removed this method's last production route by refusing
@@ -2481,3 +2481,26 @@ def arm_from_config(
             ident.kind,
         )
     return armed
+
+
+#: ``arm_refusal``'s answer when the options page has the experiment off.
+ARM_REFUSED_DISABLED = "disabled"
+
+
+def arm_refusal(
+    ident: SystemIdentification, now: datetime, config: Any, plant: ThermalParameters,
+    learner_samples: int, draw: DrawRange,
+) -> str | None:
+    """``arm_from_config``, answering why nothing was armed (``None``: armed).
+
+    The press that asked must hear a refusal (D10-s1-02): ``ARM_REFUSED_DISABLED``
+    with the option off, else the reason ``arm`` published in ``result``, else
+    the experiment already running.
+    """
+    if arm_from_config(ident, now, config, plant, learner_samples, draw):
+        return None
+    if not ident.config.enabled:
+        return ARM_REFUSED_DISABLED
+    if ident.active:
+        return "an experiment is already armed or running"
+    return ident.result.reason or "the experiment cannot be armed now"
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 0a14a852e1..6eeeb3ac7a 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -66,9 +66,6 @@ from .const import (
     DEFAULT_RADIATOR_POWER_FRACTION,
     DEFAULT_UPPER_FLOOR_AREA_RATIO,
     DEFAULT_BUFFER_TANK_VOLUME,
-    BUFFER_COOLING_RATE_MAX,
-    BUFFER_COOLING_RATE_MIN,
-    DEFAULT_BUFFER_COOLING_RATE,
     buffer_cooling_rate_bounds,
     default_buffer_cooling_rate,
     DEFAULT_BUFFER_TANK_LOSS,
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index d024d3c067..cd5c45d1b6 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -465,6 +465,12 @@
     "diagnose_interval_failed": {
       "message": "Die Intervalldiagnose konnte für {entry_ids} nicht ausgeführt werden: {error}"
     },
+    "system_identification_disabled": {
+      "message": "Die Systemidentifikation ist für {entry_ids} ausgeschaltet: \"Einmaliges Messexperiment zulassen\" in den Optionen einschalten, um sie vorzubereiten"
+    },
+    "system_identification_not_armed": {
+      "message": "Die Systemidentifikation wurde für {entry_ids} nicht vorbereitet: {reason}"
+    },
     "simulate_plan_failed": {
       "message": "Die Was-wäre-wenn-Simulation konnte für {entry_ids} nicht ausgeführt werden: {error}"
     },
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 64e36d0449..560e21a429 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -465,6 +465,12 @@
     "diagnose_interval_failed": {
       "message": "The interval diagnosis could not run for {entry_ids}: {error}"
     },
+    "system_identification_disabled": {
+      "message": "System identification is turned off for {entry_ids}: turn on \"Allow a one-off measurement experiment\" in the options to arm it"
+    },
+    "system_identification_not_armed": {
+      "message": "System identification was not armed for {entry_ids}: {reason}"
+    },
     "simulate_plan_failed": {
       "message": "The what-if simulation could not run for {entry_ids}: {error}"
     },
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 42c981d30b..1455d408ba 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -465,6 +465,12 @@
     "diagnose_interval_failed": {
       "message": "Intervalldiagnosen kunde inte köras för {entry_ids}: {error}"
     },
+    "system_identification_disabled": {
+      "message": "Systemidentifiering är avstängd för {entry_ids}: slå på \"Tillåt ett engångsförsök för att mäta huset\" i alternativen för att aktivera den"
+    },
+    "system_identification_not_armed": {
+      "message": "Systemidentifiering aktiverades inte för {entry_ids}: {reason}"
+    },
     "simulate_plan_failed": {
       "message": "Simuleringen kunde inte köras för {entry_ids}: {error}"
     },
diff --git a/dev/programme/delivery/3841.md b/dev/programme/delivery/3841.md
new file mode 100644
index 0000000000..33b4978ff9
--- /dev/null
+++ b/dev/programme/delivery/3841.md
@@ -0,0 +1 @@
+- [#3841](https://github.com/tvofi/heatpump_optimizer/pull/3841) — **open**, R11-SEAM-entity-service: published metadata and outcomes (R11-SEAM-entity-service)
diff --git a/tests/ci_budgets.json b/tests/ci_budgets.json
index 82c10dd687..3af80e2a47 100644
--- a/tests/ci_budgets.json
+++ b/tests/ci_budgets.json
@@ -7,7 +7,7 @@
  "archscore.coord_footprint": 2592,
  "archscore.coordinator_multiassigned_attrs": 120,
  "archscore.coordinator_private_reach": 2,
- "archscore.dead_members": 1,
+ "archscore.dead_members": 0,
  "archscore.duplication_copies": 68,
  "archscore.family_orphan_overrides": 0,
  "archscore.family_splits": 0,
@@ -17,7 +17,7 @@
  "archscore.literal_clone_copies": 123,
  "archscore.params_over_10": 12,
  "archscore.private_cross_module": 17,
- "archscore.public_unused": 1,
+ "archscore.public_unused": 0,
  "archscore.reflective_writes": 17,
  "archscore.shape_copies": 66,
  "archscore.shared_inplace_writes": 3,
@@ -25,8 +25,8 @@
  "archscore.untyped_payload_keys": 0,
  "archscore.unused_boundary_imports": 0,
  "critical_path_minutes": 23.574,
- "reason": "critical_path_minutes made report-only and critical_path_minutes_band deleted (R10-CI-SLIM card C2, owner ruling 2026-11-05): the ratchet prints it against this reference and never grades it; no value re-recorded. Previous reason: critical_path_minutes re-recorded 21.983 -> 23.574, the value CI printed at 8bf45e5dc (run 42038071453; also 23.351 at 788e8ceed, 23.43 at 7af0c2a79, 23.574 at b707d8932). No job's work grew in the diff: the 0ae75bf31 window already read at the band edge (23.287 against 21.983+1.3=23.283 when replayed from its job timings), and the chain prelude -> tests / closures -> tests / ci-ratchet is priced on `closures` at a 1318 s probed median (1191..1455 over the window) with ci-ratchet at 77 s. The same change runs the ratchet job's two independent fetches concurrently (a real cut of the chain's tail). Band 1.3 unchanged. Previous reason: critical_path_minutes re-recorded at 21.983 under a new statistic (R10-HOTFIX-CI-CRITPATH-3): main went red from 8f286293b, a diff of seven delivery-row .md files, at GREW 40.817 on 34.267+1.3. No job's work grew and no runner queue moved it: each heavy tests lane draws hosted runners of different speed on the same work (per-script ratios 1.6-2.9, one reference solve 45.0 ms against 18.8 ms), so the median of per-run critical paths read the host draw. The metric is now window_work_minutes over the newest 16 push runs: every job priced at its fastest success run in the window (a run under a third of the job's window median did other work and never prices it), summed along each run's own critical chain, the longest kept. 21.983 is critical_path_minutes(stat=record) over the 40 completed ci.yml push runs 41363452534..41577822624 (dev/audit/harnesses/r10_hotfix_ci_critpath_3/runs.json), the largest of its 25 sixteen-run windows (19.967..21.983). critical_path_minutes_band stays 1.3: the most any window read past the record of every window before it is 0.55 (replay.py beside that runs.json); every other row is unchanged and at zero tolerance (previous reason: band added at 1.3, R10-HOTFIX-CI-CRITPATH-2, owner ruling 2026-10-31 under mandate 6329234399).",
- "recorded_at": "8bf45e5dcedd3fbeb6842c5bfc7545ba5c8176fc",
+ "reason": "Two rows lowered (R11-SEAM-entity-service), each at the value tools/audit/archscore's vector.measure derives at 96d8a05b2159 (score.py --diff a8efe1d1c2a8 reads dead_members 1 -> 0 and public_unused 1 -> 0): the D7-s1-05 avail arm and the window-in-force owner leave no dead member and no unused public symbol, so a planted one is refused (field_coverage's census rows). No other row moves. Previous reason: critical_path_minutes made report-only and critical_path_minutes_band deleted (R10-CI-SLIM card C2, owner ruling 2026-11-05): the ratchet prints it against this reference and never grades it; no value re-recorded. Previous reason: critical_path_minutes re-recorded 21.983 -> 23.574, the value CI printed at 8bf45e5dc (run 42038071453; also 23.351 at 788e8ceed, 23.43 at 7af0c2a79, 23.574 at b707d8932). No job's work grew in the diff: the 0ae75bf31 window already read at the band edge (23.287 against 21.983+1.3=23.283 when replayed from its job timings), and the chain prelude -> tests / closures -> tests / ci-ratchet is priced on `closures` at a 1318 s probed median (1191..1455 over the window) with ci-ratchet at 77 s. The same change runs the ratchet job's two independent fetches concurrently (a real cut of the chain's tail). Band 1.3 unchanged. Previous reason: critical_path_minutes re-recorded at 21.983 under a new statistic (R10-HOTFIX-CI-CRITPATH-3): main went red from 8f286293b, a diff of seven delivery-row .md files, at GREW 40.817 on 34.267+1.3. No job's work grew and no runner queue moved it: each heavy tests lane draws hosted runners of different speed on the same work (per-script ratios 1.6-2.9, one reference solve 45.0 ms against 18.8 ms), so the median of per-run critical paths read the host draw. The metric is now window_work_minutes over the newest 16 push runs: every job priced at its fastest success run in the window (a run under a third of the job's window median did other work and never prices it), summed along each run's own critical chain, the longest kept. 21.983 is critical_path_minutes(stat=record) over the 40 completed ci.yml push runs 41363452534..41577822624 (dev/audit/harnesses/r10_hotfix_ci_critpath_3/runs.json), the largest of its 25 sixteen-run windows (19.967..21.983). critical_path_minutes_band stays 1.3: the most any window read past the record of every window before it is 0.55 (replay.py beside that runs.json); every other row is unchanged and at zero tolerance (previous reason: band added at 1.3, R10-HOTFIX-CI-CRITPATH-2, owner ruling 2026-10-31 under mandate 6329234399).",
+ "recorded_at": "96d8a05b21594b9df107588a80b46a9d245c0e17",
  "script_runs_full_case_pr": 68,
  "script_runs_per_push": 54
 }
diff --git a/tests/closures.json b/tests/closures.json
index 65f5750a3c..688bce594a 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -922,6 +922,7 @@
    "custom_components/heatpump_optimizer/runs.py",
    "custom_components/heatpump_optimizer/sensor.py",
    "custom_components/heatpump_optimizer/services.py",
+   "custom_components/heatpump_optimizer/services.yaml",
    "custom_components/heatpump_optimizer/setpoint_check.py",
    "custom_components/heatpump_optimizer/silent_mode.py",
    "custom_components/heatpump_optimizer/slab_seed.py",
@@ -6065,11 +6066,11 @@
   },
   "tests/features.py": {
    "rc": 0,
-   "seconds": 422.7
+   "seconds": 1031.5
   },
   "tests/finite_boundary.py": {
    "rc": 0,
-   "seconds": 193.8
+   "seconds": 96.8
   },
   "tests/frontend.py": {
    "rc": 0,
@@ -6077,7 +6078,7 @@
   },
   "tests/golden.py": {
    "rc": 0,
-   "seconds": 1.2
+   "seconds": 0.5
   },
   "tests/guard_pins.py": {
    "rc": 0,
@@ -6085,7 +6086,7 @@
   },
   "tests/ha_contract.py": {
    "rc": 0,
-   "seconds": 0.5
+   "seconds": 0.2
   },
   "tests/harness_headers.py": {
    "rc": 0,
@@ -6113,7 +6114,7 @@
   },
   "tests/plan_view.py": {
    "rc": 0,
-   "seconds": 1.8
+   "seconds": 0.8
   },
   "tests/solar_alignment.py": {
    "rc": 0,
@@ -6121,7 +6122,7 @@
   },
   "tests/stress.py": {
    "rc": 0,
-   "seconds": 928.7
+   "seconds": 434.9
   },
   "tests/structure.py": {
    "rc": 0,
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 1ce16fb27b..4157a73bbd 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -4809,6 +4809,77 @@ async def widening_refusals():
         repr(None if widened is None else dict(widened.config)),
     )
 
+    # D14-s1-01: a slider's grid starts at its min. A min widened to a stored
+    # 14.7 on a 0.5 grid put the field's default 21.0 off the reachable set.
+    # The widened bound now moves outward onto the grid. A step "any" field
+    # has no grid and widens to exactly the value.
+    def _on_grid(cfg, value):
+        steps = (value - cfg["min"]) / cfg["step"]
+        return abs(steps - round(steps)) < 1e-9
+
+    slider = selector.NumberSelector(selector.NumberSelectorConfig(
+        min=15.0, max=25.0, step=0.5, mode=selector.NumberSelectorMode.SLIDER))
+    low_w = config_flow._widen_to_fit(slider, [14.7])
+    high_w = config_flow._widen_to_fit(slider, [25.3])
+    any_w = config_flow._widen_to_fit(selector.NumberSelector(selector.NumberSelectorConfig(
+        min=15.0, max=25.0, step="any", mode=selector.NumberSelectorMode.BOX)), [14.7])
+    check(
+        "schema_widening",
+        "happy",
+        "a widened slider keeps its grid: the default and the far bound stay reachable (D14-s1-01)",
+        low_w is not None and low_w.config["min"] == 14.5 and low_w.config["max"] == 25.0
+        and _on_grid(low_w.config, 21.0) and _on_grid(low_w.config, 25.0)
+        and high_w is not None and high_w.config["max"] == 25.5 and high_w.config["min"] == 15.0
+        and any_w is not None and any_w.config["min"] == 14.7,
+        f"low {None if low_w is None else dict(low_w.config)} high "
+        f"{None if high_w is None else dict(high_w.config)} any "
+        f"{None if any_w is None else dict(any_w.config)}",
+    )
+    # The grid's two edges. A step of 0 is no grid: the bound is the value, never
+    # a division by it. A stored value within float noise of a grid point
+    # (14.4999999998, a round-trip's residue) widens to that point, not one step past.
+    try:
+        zero_w = config_flow._widen_to_fit(selector.NumberSelector(selector.NumberSelectorConfig(
+            min=15.0, max=25.0, step=0, mode=selector.NumberSelectorMode.BOX)), [14.7])
+        zero_min = None if zero_w is None else zero_w.config["min"]
+    except ZeroDivisionError as err:
+        zero_min = repr(err)
+    noise_w = config_flow._widen_to_fit(slider, [14.4999999998])
+    check(
+        "schema_widening",
+        "happy",
+        "a step-0 field widens to exactly the value; float noise below a grid point widens to that point (D14-s1-01)",
+        zero_min == 14.7 and noise_w is not None and noise_w.config["min"] == 14.5,
+        f"step 0 -> min {zero_min!r}; 14.4999999998 on 15/0.5 -> "
+        f"{None if noise_w is None else noise_w.config['min']!r}",
+    )
+    # The service surface (D14-s1-01's twelve seams): every number selector
+    # services.yaml declares reaches its own max and example, or has no grid.
+    import yaml as _svc_yaml
+    from pathlib import Path
+    _svc = _svc_yaml.safe_load(
+        (Path(config_flow.__file__).parent / "services.yaml").read_text(encoding="utf-8"))
+    _svc_fields, _svc_off = 0, []
+    for _svc_name, _svc_def in (_svc or {}).items():
+        for _f_name, _f in ((_svc_def or {}).get("fields") or {}).items():
+            _num = ((_f or {}).get("selector") or {}).get("number")
+            if not isinstance(_num, dict):
+                continue
+            _svc_fields += 1
+            if not isinstance(_num.get("step", 1), (int, float)) or _num.get("min") is None:
+                continue
+            _grid = {"min": float(_num["min"]), "step": float(_num.get("step", 1))}
+            for _what, _v in (("max", _num.get("max")), ("example", _f.get("example"))):
+                if isinstance(_v, (int, float)) and not _on_grid(_grid, float(_v)):
+                    _svc_off.append(f"{_svc_name}.{_f_name} {_what} {_v}")
+    check(
+        "schema_widening",
+        "error",
+        "every services.yaml number selector reaches its own max and example (D14-s1-01)",
+        _svc_fields > 20 and not _svc_off,
+        f"{_svc_fields} number fields; off grid: {_svc_off}",
+    )
+
     # The whole-schema entry point: nothing to walk is not an error. The
     # mixin applies it to every form result, including the menus and aborts
     # that carry no schema at all.
diff --git a/tests/debug_collect.py b/tests/debug_collect.py
index fed82dca7b..fe54759967 100644
--- a/tests/debug_collect.py
+++ b/tests/debug_collect.py
@@ -2211,4 +2211,16 @@ R.check(
     all(row["null"] for row in _bounded_rows),
     str([row["row"] for row in _bounded_rows if not row["null"]]),
 )
+# D15-s3-01: the not-run publish after a restart carries solve_time_ms 0, an
+# inert value, never a duration; the solver self-test's week spread is over
+# the rows where a solve ran. The real bundle read min 0 ms and n 662 where
+# 652 solves ran. The control row with no recorded time is left out alike.
+_smoke_rows = [{"payload_solve_time_ms": 9806.0}, {"payload_solve_time_ms": 0},
+               {"payload_solve_time_ms": 12000.0}, {"mode": "auto"}]
+_smoke = asyncio.run(debugger._solver_smoke(_SimCoord(data={}), _smoke_rows))["week_solve_ms"]
+R.check(
+    "the solver self-test spreads only rows where a solve ran: a not-run 0 is no duration (D15-s3-01)",
+    _smoke is not None and _smoke["n"] == 2 and _smoke["min"] == 9806.0,
+    str(_smoke),
+)
 sys.exit(R.close("DEBUG COLLECT CHECKS"))
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 35be7f2db5..afb5316e81 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -57,13 +57,15 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 167 of the 528 script pairs (33 choose 2) sharing 0.80 or more
-of their production-module closure (164 on each side before the merge joining
+recording finds 165 of the 528 script pairs (33 choose 2) sharing 0.80 or more
+of their production-module closure (167 before R11-SEAM-entity-service's
+services.yaml joined config_flow_steps.py's closure, taking its pairs with
+debug_collect.py and wood_advisor.py under 0.80; 164 on each side before the merge joining
 R11-OUTSIDE-ROOMS-P1's rooms.py, read by every closure that imports the
 coordinator, the input reader, the config flow or the sensor platform, and
 R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which joined
 config_flow_steps.py/debug_collect.py at 0.80; 162 before #3616 re-recorded the
-closures that import the coordinator), all 167 among the 406 pairs whose two
+closures that import the coordinator), all 165 among the 406 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 062b8ee5b5..cf93d97909 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -136,14 +136,15 @@ def entity_id_prefix_literals() -> dict[str, str]:
     Returns ``{module_name: prefix_token}`` for every module that assigns
     ``entity_id = f"<domain>.<prefix>_{translation_key}"``, or the entity
     base's one rule (``object_id = f"<prefix>_{self._attr_translation_key}"``,
-    R9-EG-B2) that every platform now pins through. A prefix that followed
+    R9-EG-B2) that every platform now pins through, with the declared
+    family's ``{lead}`` between them (D8-s2-02). A prefix that followed
     the entry name would be written as an expression (``{slug(entry title)}``)
     or omit the assignment; the shipped form is a hard-coded literal, which
     is the fact #1393's prose contradicts.
     """
     pattern = re.compile(
         r'(?:entity_id|object_id)\s*=\s*f"(?:[a-z_]+\.)?([a-z0-9_]+)_'
-        r'\{(?:self\._attr_)?translation_key\}"'
+        r'(?:\{lead\})?\{(?:self\._attr_)?translation_key\}"'
     )
     found: dict[str, str] = {}
     for path in sorted(PKG.glob("*.py")):
diff --git a/tests/entities.py b/tests/entities.py
index 66a6295560..1bc4745ded 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -104,7 +104,7 @@ def _seed_prices(hass, entity_id="sensor.prices", hours=48, base=0.5):
     )
 
 
-from homeassistant.components.sensor import SensorStateClass
+from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
 
 import heatpump_optimizer as integration
 from homeassistant import const as ha_const
@@ -4286,6 +4286,48 @@ def _p2_registry(sources):
                  ast.IfExp, r"if \w+ is None else \w+\.astimezone\(timezone\.utc\)$",
                  lambda n: isinstance(n.test, ast.Compare)),
              owners=["tariff.py::_window_starts"], dispositions={}),
+        # D17-s3-51 and the P2 sweep's F14 seams (R11-SEAM-entity-service):
+        # the hot-water window in force at an instant is windows_in_force's,
+        # the planner's per-step day chain for a reader holding a clock. A
+        # read of the flat every-day set elsewhere tests no instant.
+        dict(fact="dhw_window_in_force", finding="D17-s3-51",
+             match=_p2_match_node(
+                 ast.Attribute, r"\.dhw_(demand_)?windows$",
+                 lambda n: n.attr in ("dhw_windows", "dhw_demand_windows")),
+             owners=["dhw_schedule.py::windows_in_force"], dispositions={
+                 # The flat set itself, and whether a schedule is in force.
+                 "thermal_model.py::ThermalParameters.dhw_demand_windows":
+                     "defines the flat every-day set windows_in_force's chain ends in",
+                 "thermal_model.py::ThermalParameters.dhw_windows_active":
+                     "whether a schedule is configured at all; no instant",
+                 # The 24-hour draw profile, a day-agnostic mask.
+                 "thermal_model.py::ThermalParameters.effective_dhw_draw_pattern":
+                     "the draw mask's cache key; no instant",
+                 "thermal_model.py::ThermalParameters._windowed_draw_pattern":
+                     "masks the 24-hour draw profile by each hour's window coverage, "
+                     "the day-agnostic profile the weekday pattern multiplies; no instant",
+                 # The planner's own fallback, which its per-step chain resolves.
+                 "dhw_planner.py::DhwPlanner._effective_dhw_windows":
+                     "the fallback set the planner's per-step windows_for_day chain "
+                     "(_dhw_windows_at) resolves; windows_in_force is that chain for a clock; "
+                     "every consumer of its return is the flat-consumers census's",
+                 # Stats tables keyed by the flat windows' labels.
+                 "dhw_learning.py::DhwProfileLearner.async_fold_draw_stats":
+                     "labels a draw with the flat window, the key the planner reads "
+                     "the stats by; whether it fell in a window is windows_in_force's",
+                 "coordinator.py::HeatPumpOptimizerCoordinator._dhw_plan_fields":
+                     "keys the stats table by the flat labels; the clock picks the "
+                     "weekday pattern, and no instant is tested (sweep-P2.md F14)",
+                 "coordinator.py::HeatPumpOptimizerCoordinator._dhw_setpoint_sweep":
+                     "the heaviest window's ready energy over the flat labels' stats; no instant",
+                 # Published text.
+                 "coordinator.py::HeatPumpOptimizerCoordinator._dhw_view":
+                     "publishes the spec text and the per-window stats; no instant",
+                 "coordinator.py::HeatPumpOptimizerCoordinator.configured_dhw_windows":
+                     "formats the configured spec for display; no instant",
+                 "optimizer.py::_dhw_resolved_publish":
+                     "formats the resolved day spec for the card; no instant",
+             }),
         # D7-s3-04 (R11-SEAM-kernel-step): the heat that warms a litre of
         # water by one kelvin is const.WATER_SPECIFIC_HEAT, and the per-kg
         # form is derived from it there (const.py is not scanned). Any
@@ -4347,6 +4389,19 @@ _P2_CENSUSES = {
     # D7-s2-52/53, D7-s2-60 (#2242): a published state's number is
     # payload_number's -- every number state driven with a bool and a text
     # payload publishes neither, nor reads either as a number.
+    # D8-s1-03 and the sweep's F18 family (R11-SEAM-entity-service): a
+    # waits-for-evidence sensor is available exactly when it has a value.
+    "waits_for_evidence_value": (
+        "tests/entities.py",
+        "waits_for_evidence census: every waits-for-evidence sensor is available only with a value"),
+    # D17-s3-51's other half: the flat set's consumers past the attribute
+    # load, and the planner's published countdown against windows_in_force.
+    "dhw_window_flat_consumers": (
+        "tests/entities.py",
+        "D17-s3-51: every consumer of the flat every-day hot-water windows, "),
+    "dhw_planner_next_window_day": (
+        "tests/features.py",
+        "the planner's published next window reads the day's windows, today's and "),
     "payload_number_published": (
         "tests/finite_boundary.py",
         "every number state publishes None, never the bool or the text, from a "),
@@ -4524,6 +4579,10 @@ _P2_PLANTS["power_state_kw"] = (
 _P2_PLANTS["channel_active_kw"] = (
     "\n\ndef _p2_plant(dhw_power):\n    return dhw_power > CHANNEL_ACTIVE_KW\n"
 )
+_P2_PLANTS["dhw_window_in_force"] = (
+    "\n\ndef _p2_plant(params, hour):\n"
+    "    return hour_in_windows(hour, params.dhw_demand_windows)\n"
+)
 _P2_PLANTS["defrost_standoff"] = (
     "\n\ndef _p2_plant(signals):\n"
     "    if signals.defrosting:\n"
@@ -4595,6 +4654,179 @@ R.check(
     f"planted={_p2_planted} unfenced={_p2_unfenced} renamed={_p2_renamed}",
 )
 
+# D17-s3-51's consumers census (R11-SEAM-entity-service). dhw_window_in_force's
+# rule matches the flat set's attribute loads, function by function. So a
+# value that leaves a dispositioned site -- a return (`_effective_dhw_windows`),
+# a local, a same-module parameter -- reached an instant test unread: the
+# planner's next window read the flat union on a weekend. This follows every
+# flat value from those loads to the call that consumes it. A resolver
+# (`_FW_RESOLVERS`, the windows_for_day chain) ends the walk; a same-module
+# function is entered at the parameter it binds; a function returning the
+# value becomes a source. Every other consumer is keyed
+# "file::site -> callee" against a disposition. Design choice: the key is the
+# callee, not the line, so a second read through a dispositioned callee in the
+# same site rides its disposition.
+_FW_ATTRS = ("dhw_windows", "dhw_demand_windows")
+_FW_WRAPS = ("list", "tuple", "sorted")
+_FW_RESOLVERS = ("windows_for_day", "_dhw_windows_at", "windows_in_force")
+_FW_DISPOSITIONS = {
+    "thermal_model.py::ThermalParameters.dhw_demand_windows -> <Return>":
+        "the flat set itself (a source)",
+    "thermal_model.py::ThermalParameters.dhw_windows_active -> <BoolOp>":
+        "whether a schedule is configured; no instant",
+    "thermal_model.py::ThermalParameters.effective_dhw_draw_pattern -> <BoolOp>":
+        "the draw mask's cache key; no instant",
+    "thermal_model.py::ThermalParameters._windowed_draw_pattern -> overlap_fraction":
+        "each hour's coverage of the day-agnostic 24-hour profile; no instant",
+    "dhw_planner.py::DhwPlanner._effective_dhw_windows -> <Return>":
+        "the planner's fallback set (a source)",
+    "dhw_planner.py::DhwPlanner._build_dhw_requirements -> _dhw_window_floors":
+        "entered: its per-step chain resolves the set",
+    "dhw_planner.py::DhwPlanner._build_dhw_requirements -> _dhw_next_window_hours":
+        "entered: today's and the next day's windows, resolved",
+    "dhw_planner.py::DhwPlanner._build_dhw_requirements -> format_windows":
+        "publishes the spec text windows_in_force's chain ends in; no instant",
+    "dhw_planner.py::DhwPlanner._dhw_window_floors -> draw_window_label":
+        "keys the stats table by the flat labels the learner writes; the step "
+        "is a resolved window start already",
+    "dhw_learning.py::DhwProfileLearner.async_fold_draw_stats -> draw_window_label":
+        "the flat label the stats table is keyed by, taken only when the "
+        "day's windows (windows_in_force) hold the instant",
+    "dhw_learning.py::DhwProfileLearner.async_fold_draw_stats -> labels_for":
+        "prunes the stats table to the flat labels; no instant",
+    "coordinator.py::HeatPumpOptimizerCoordinator._dhw_plan_fields -> labels_for":
+        "the stats table's flat labels; no instant",
+    "coordinator.py::HeatPumpOptimizerCoordinator._dhw_setpoint_sweep -> labels_for":
+        "the heaviest window's stats over the flat labels; no instant",
+    "coordinator.py::HeatPumpOptimizerCoordinator._dhw_setpoint_sweep -> zip":
+        "pairs each flat window with its label for the profile overlap; no instant",
+    "coordinator.py::HeatPumpOptimizerCoordinator._dhw_view -> format_windows":
+        "publishes the spec text; no instant",
+    "coordinator.py::HeatPumpOptimizerCoordinator._dhw_view -> labels_for":
+        "publishes the per-window stats; no instant",
+    "coordinator.py::HeatPumpOptimizerCoordinator.configured_dhw_windows -> format_windows":
+        "formats the configured spec for display; no instant",
+    "optimizer.py::_dhw_resolved_publish -> format_resolved_day_spec":
+        "formats the resolved day spec for the card; no instant",
+}
+
+
+def _fw_consumers(sources):
+    """({"file::site -> callee": [line, ...]}, flat source function names)."""
+    idx, funcs = {}, {}
+    for name, text in sources.items():
+        if name == "const.py":
+            continue
+        tree = ast.parse(text)
+        parents, qual = _p2_index(tree)
+        idx[name] = parents
+        for n in ast.walk(tree):
+            if (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
+                    and not isinstance(parents.get(n), (ast.FunctionDef, ast.AsyncFunctionDef))):
+                funcs.setdefault((name, n.name), (qual[n], n))
+
+    def callee(c):
+        return c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", "?")
+
+    def flat(n, names, srcs):
+        return (isinstance(n, ast.Attribute) and n.attr in _FW_ATTRS and isinstance(n.ctx, ast.Load)
+                or isinstance(n, ast.Name) and n.id in names and isinstance(n.ctx, ast.Load)
+                or isinstance(n, ast.Call) and callee(n) in srcs)
+
+    def scan(file, site, fn, names, srcs, out, depth):
+        parents, names = idx[file], set(names)
+        grew = True
+        while grew:
+            grew = False
+            for n in ast.walk(fn):
+                if isinstance(n, ast.Assign) and len(n.targets) == 1:
+                    v, t = n.value, n.targets[0]
+                    while isinstance(v, ast.Call) and callee(v) in _FW_WRAPS and v.args:
+                        v = v.args[0]
+                    t = t.elts[0] if isinstance(t, ast.Tuple) and t.elts else t
+                    if flat(v, names, srcs) and isinstance(t, ast.Name) and t.id not in names:
+                        names.add(t.id)
+                        grew = True
+        for n in ast.walk(fn):
+            if not flat(n, names, srcs):
+                continue
+            node, up = n, parents.get(n)
+            while isinstance(up, ast.Call) and callee(up) in _FW_WRAPS and node in up.args:
+                node, up = up, parents.get(up)
+            if isinstance(up, ast.Assign):
+                continue
+            if isinstance(up, ast.Tuple) and isinstance(parents.get(up), ast.Return):
+                up = parents[up]
+            if isinstance(up, ast.Call) and (node in up.args or any(k.value is node for k in up.keywords)):
+                c = callee(up)
+                if c in _FW_RESOLVERS:
+                    continue
+                out.setdefault(f"{file}::{site} -> {c}", []).append(n.lineno)
+                if (file, c) in funcs and depth < 4:
+                    cq, cfn = funcs[(file, c)]
+                    params = [a.arg for a in cfn.args.args if a.arg != "self"]
+                    i = up.args.index(node) if node in up.args else None
+                    p = (params[i] if i is not None and i < len(params)
+                         else next((k.arg for k in up.keywords if k.value is node), None))
+                    if p:
+                        scan(file, cq, cfn, [p], srcs, out, depth + 1)
+                continue
+            out.setdefault(f"{file}::{site} -> <{type(up).__name__}>", []).append(n.lineno)
+
+    srcs = set()
+    while True:
+        out = {}
+        for (file, _), (site, fn) in sorted(funcs.items()):
+            if site.rsplit(".", 1)[-1] not in _FW_RESOLVERS:
+                scan(file, site, fn, (), srcs, out, 0)
+        grown = srcs | {k.split(" -> ")[0].rsplit(".", 1)[-1].split("::")[-1]
+                        for k in out if k.endswith("<Return>")}
+        if grown == srcs:
+            return out, srcs
+        srcs = grown
+
+
+_fw_out, _fw_srcs = _fw_consumers(_P2_SOURCES)
+_fw_stray = sorted(k for k in _fw_out if k not in _FW_DISPOSITIONS)
+_fw_stale = sorted(k for k in _FW_DISPOSITIONS if k not in _fw_out)
+R.check(
+    "D17-s3-51: every consumer of the flat every-day hot-water windows, "
+    "followed from each attribute load through locals, returns and same-module "
+    "parameters, is a resolver or a dispositioned no-instant read; none stale, "
+    "and the walk found its two sources (its own precondition)",
+    not _fw_stray and not _fw_stale
+    and {"_effective_dhw_windows", "dhw_demand_windows"} <= _fw_srcs,
+    f"SEAM {[(k, _fw_out[k]) for k in _fw_stray]} STALE {_fw_stale} sources={sorted(_fw_srcs)}",
+)
+# Null controls: the pre-fix countdown, a flat set returned and tested by a
+# caller, and a parameter carrying it into an instant test each fail alone.
+_FW_FIXED = "next_window = _dhw_next_window_hours(hours_mod, step_weekdays, windows, params, holiday_flags)"
+_fw_plants = {
+    "pre-fix countdown": _P2_SOURCES["dhw_planner.py"].replace(
+        _FW_FIXED, "next_window = hours_until_next_window(\n"
+        "            float(hours_mod[0]) if n_steps else 0.0, windows\n        )"),
+    "returned then tested": _P2_SOURCES["dhw_planner.py"]
+    + "\n\ndef _fw_src(p):\n    return list(p.dhw_windows)\n"
+      "\n\ndef _fw_use(p, h):\n    return hour_in_windows(h, _fw_src(p))\n",
+    "parameter then tested": _P2_SOURCES["dhw_planner.py"]
+    + "\n\ndef _fw_inner(ws, h):\n    return hour_in_windows(h, ws)\n"
+      "\n\ndef _fw_outer(p, h):\n    ws = p.dhw_demand_windows\n    return _fw_inner(ws, h)\n",
+}
+_fw_planted = {
+    k: sorted(set(_fw_consumers({**_P2_SOURCES, "dhw_planner.py": v})[0]) - set(_FW_DISPOSITIONS))
+    for k, v in _fw_plants.items()
+}
+R.check(
+    "and the consumers census fails on each planted flat read: the pre-fix "
+    "countdown, a returned set, a parameter (null controls)",
+    _P2_SOURCES["dhw_planner.py"].count(_FW_FIXED) == 1
+    and _fw_planted["pre-fix countdown"]
+    == ["dhw_planner.py::DhwPlanner._build_dhw_requirements -> hours_until_next_window"]
+    and "dhw_planner.py::_fw_use -> hour_in_windows" in _fw_planted["returned then tested"]
+    and "dhw_planner.py::_fw_inner -> hour_in_windows" in _fw_planted["parameter then tested"],
+    f"{_fw_planted}",
+)
+
 
 # ===========================================================================
 # #1745: the entry's configuration is parsed once
@@ -5027,6 +5259,8 @@ P6_UPSTREAM_PROBES = {
     "async_start_reauth", "last_update_success", "async_items",
     "register_static_path", "async_update_item", "last_updated", "last_changed",
     "last_reported", "isoformat", "temperature_unit",
+    # SensorDeviceClass member since 2025.11.0, read above the hacs.json floor (D10-s2-04).
+    "TEMPERATURE_DELTA",
 }
 #: Home Assistant's own climate presets (climate/const.py PRESET_*), which the
 #: climate component translates and icons itself.
@@ -6777,18 +7011,31 @@ R.check(
     "; ".join(_impossible),
 )
 
-# Two the audit brief flagged and this PR deliberately leaves alone, pinned so
-# a future "consistency" pass does not add a device class to either.
-R.check(
-    "Heat-Curve Displace stays bare: it is a parallel shift, not a temperature",
-    getattr(by_name["Heat-Curve Displace"], "_attr_device_class", None) is None
-    and by_name["Heat-Curve Displace"]._attr_native_unit_of_measurement == "°C",
-    "a TEMPERATURE device class would have HA convert a delta as an absolute",
+# A temperature DIFFERENCE never takes TEMPERATURE, which converts a delta as
+# an absolute for a Fahrenheit user; it takes TEMPERATURE_DELTA where the
+# running core has it (2025.11.0, above the hacs.json floor: None there).
+# D10-s2-04 found these readouts left bare after the class existed.
+_DELTA_DC = getattr(SensorDeviceClass, "TEMPERATURE_DELTA", None)
+for _delta_name in ("Heat-Curve Displace", "Heat-Curve Effective Displace", "Prediction Accuracy"):
+    R.check(
+        f"{_delta_name} is a temperature difference: TEMPERATURE_DELTA, never TEMPERATURE (D10-s2-04)",
+        _DELTA_DC is not None
+        and getattr(by_name[_delta_name], "_attr_device_class", None) == _DELTA_DC
+        and by_name[_delta_name]._attr_native_unit_of_measurement == "°C",
+        f"{getattr(by_name[_delta_name], '_attr_device_class', None)!r} -- TEMPERATURE "
+        "would have HA convert a delta as an absolute",
+    )
+# The census the rule needs (D10-s2-04's metric): no sensor publishing in °C
+# or K is left classless where the class exists.
+_delta_bare = sorted(
+    type(_e).__name__ for _e in by_name.values()
+    if getattr(_e, "_attr_native_unit_of_measurement", None) in ("°C", "K")
+    and getattr(_e, "_attr_device_class", None) is None
 )
 R.check(
-    "Prediction Accuracy stays bare for the same reason: it is a mean error",
-    getattr(by_name["Prediction Accuracy"], "_attr_device_class", None) is None
-    and by_name["Prediction Accuracy"]._attr_native_unit_of_measurement == "°C",
+    "no sensor in degC or K is published without a device class (D10-s2-04 census)",
+    len(by_name) > 40 and not _delta_bare,
+    f"bare: {_delta_bare} of {len(by_name)} sensors",
 )
 R.check(
     "a device class with no state class is legal, so the valve target is fine",
@@ -13061,6 +13308,49 @@ R.check(
     == _ATTR_RICH["savings_months"],
     repr(_ready_sav.native_value),
 )
+# D8-s1-03: availability and state read the same row. At a month rollover
+# (only the settled month booked) and on an open row whose saving the ledger
+# withholds (old_basis, below_meter_floor: savings_sek None) the sensor was
+# available with state unknown.
+for _sav_label, _sav_rows in (
+    ("rollover: only the settled month", [{"month": "2026-01", "estimated": False, "savings_sek": 80.0}]),
+    ("open row withheld", [{"month": "2026-01", "estimated": False, "savings_sek": 80.0},
+                           {"month": "2026-02", "estimated": True, "savings_sek": None}]),
+):
+    _sav_w = sensor.MonthlySavingsSensor(FakeCoordinator({**DATA, "savings_months": _sav_rows}), ENTRY)
+    R.check(
+        f"MonthlySavingsSensor is unavailable, never unknown, with no open saving ({_sav_label}; D8-s1-03)",
+        not _sav_w.available and _sav_w.native_value is None
+        and _sav_w.extra_state_attributes.get("waiting_for") == "open_month_coverage",
+        f"available {_sav_w.available} value {_sav_w.native_value!r} "
+        f"waiting_for {_sav_w.extra_state_attributes.get('waiting_for')!r}",
+    )
+
+# The census the fact needs (sweep-P2 F18). Every waits-for-evidence sensor
+# the platform builds is available exactly when it has a value, on the empty,
+# the default and the rich payload. That is the mixin's contract: "not
+# measured yet" is unavailable, never unknown. The census asserts its reach:
+# every subclass the module defines is built here.
+_wfe_classes = {
+    _c for _c in vars(sensor).values()
+    if isinstance(_c, type) and issubclass(_c, sensor._WaitsForEvidenceMixin)
+    and _c is not sensor._WaitsForEvidenceMixin
+}
+_wfe_seen, _wfe_bad = set(), []
+_wfe_runtime = getattr(ENTRY, "runtime_data", None)
+for _wfe_data in ({}, DATA, _ATTR_RICH):
+    for _wfe in collect(sensor, _wfe_data):
+        if isinstance(_wfe, sensor._WaitsForEvidenceMixin):
+            _wfe_seen.add(type(_wfe))
+            if _wfe.available and _wfe.native_value is None:
+                _wfe_bad.append(f"{type(_wfe).__name__}@{len(_wfe_data)} keys")
+ENTRY.runtime_data = _wfe_runtime
+R.check(
+    "waits_for_evidence census: every waits-for-evidence sensor is available only with a value",
+    _wfe_classes and _wfe_seen == _wfe_classes and not _wfe_bad,
+    f"available and unknown: {_wfe_bad}; not built: "
+    f"{sorted(c.__name__ for c in _wfe_classes - _wfe_seen)}",
+)
 # R10-SAV-WOOD-HEAT (owner ruling, 2026-11-04): the reference has no wood, so on
 # a house with wood configured the entity's saving says it includes wood's heat
 # and not firewood's cost, by the receipt event's one definition. The null
@@ -13961,14 +14251,44 @@ _bad_ids = sorted(
     e._attr_unique_id
     for _platform, e in _named_entities
     if _platform != "climate"
-    and getattr(e, "entity_id", None)
-    != f"{_platform}.heat_pump_optimizer_{e._attr_translation_key}"
+    and not (
+        str(getattr(e, "entity_id", "")).startswith(f"{_platform}.heat_pump_optimizer_")
+        and str(getattr(e, "entity_id", "")).endswith(f"_{e._attr_translation_key}")
+    )
 )
 R.check(
     "every entity pre-assigns its suggested object id",
     not _bad_ids,
     ", ".join(_bad_ids),
 )
+
+
+# D8-s2-02: a declared family (_fam_token: override, else lead token) is ONE
+# run in each platform's suggested entity-id sort, as it is in each language's
+# name sort above. The four lifetime meters sorted as three id runs while
+# their names led with "Lifetime". The null control sorts the same entities
+# by the bare translation-key id the scheme used before, which must split.
+def _fam_id_splits(_id_of):
+    _out = []
+    for _plat in sorted({_p for _p, _ in _named_entities}):
+        _order = [_fam_token(_e._attr_translation_key) for _, _e in sorted(
+            ((_id_of(_p, _e), _e) for _p, _e in _named_entities if _p == _plat),
+            key=lambda _r: _r[0])]
+        for _fam in sorted(set(_order)):
+            _runs = sum(1 for _i, _f in enumerate(_order) if _f == _fam and (_i == 0 or _order[_i - 1] != _fam))
+            if _runs > 1:
+                _out.append(f"{_plat}:{_fam}:{_runs} runs")
+    return _out
+
+
+_fam_id_split = _fam_id_splits(lambda _p, _e: str(_e.entity_id))
+_fam_id_split_bare = _fam_id_splits(
+    lambda _p, _e: f"{_p}.heat_pump_optimizer_{_e._attr_translation_key}")
+R.check(
+    "every declared family is one run in each platform's entity-id sort (D8-s2-02)",
+    not _fam_id_split and bool(_fam_id_split_bare),
+    f"split: {_fam_id_split}; null control (bare translation-key ids) split: {_fam_id_split_bare}",
+)
 # Spot-pins against the pre-v5.0.0 slugs, written out literally so a renamed
 # translation key cannot silently move the goalposts of the check above.
 for _display, _expected_id in (
@@ -14067,7 +14387,8 @@ for _display, _new_id, _uid in (
     ("Cost Monthly Peak Power", "sensor.heat_pump_optimizer_cost_monthly_peak_power", "monthly_peak"),
     ("Cost Power Headroom", "sensor.heat_pump_optimizer_cost_power_headroom", "power_headroom"),
     ("Cost Predicted", "sensor.heat_pump_optimizer_cost_predicted", "predicted_cost"),
-    ("Lifetime Total Heating Cost", "sensor.heat_pump_optimizer_cost_total_heating", "total_cost"),
+    # D8-s2-02 then led the lifetime meters' ids with their declared family.
+    ("Lifetime Total Heating Cost", "sensor.heat_pump_optimizer_lifetime_cost_total_heating", "total_cost"),
     ("Learning Comfort Weight", "sensor.heat_pump_optimizer_learning_comfort_weight", "comfort_weight"),
     ("Learning Estimated COP", "sensor.heat_pump_optimizer_learning_estimated_cop", "current_cop"),
     ("Learning Observed COP", "sensor.heat_pump_optimizer_learning_observed_cop", "observed_cop"),
diff --git a/tests/features.py b/tests/features.py
index 658969c8a4..0a527d1e6b 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -5989,6 +5989,99 @@ R.check(
     not (set(_mon_req) & set(_sat_req)),
     f"mon {_mon_req} vs sat {_sat_req}",
 )
+# D17-s3-51, the planner's reader: `DhwPlan.next_window_in_hours`
+# (published as dhw_next_window_in_hours) is read in the day's windows,
+# today's and the next day's, exactly as `windows_in_force` answers for a
+# clock. It read the flat every-day union, so a Saturday 07:00 read 0.0
+# (inside the weekday window) where the weekend window opens in 1.0 h.
+# The census drives every weekday at hours before, inside, between and
+# after the windows, plus a holiday and a per-day override, and compares
+# each cell with the owner's answer. It asserts its own precondition: the
+# grid holds cells where the flat set disagrees with the day's.
+import dataclasses as _nw_dc
+import datetime as _nw_dt
+from heatpump_optimizer.dhw_schedule import (
+    hours_until_next_window as _nw_hunw, windows_in_force as _nw_wif,
+    parse_windows as _nw_parse,
+)
+
+_NW_SPEC = "weekdays 06:00-08:30, weekend 08:00-09:30"
+
+
+def _nw_cell(params, t0, holidays=frozenset()):
+    _o = _PvOpt(ThermalModel(params), _PvOptCfg(
+        horizon_hours=24, time_step_minutes=15,
+        target_temp=21.0, min_temp=17.0, max_temp=23.0))
+    _n = 96
+    _ts = [t0 + _nw_dt.timedelta(hours=i * 0.25) for i in range(_n)]
+    _plan, _ = _dhw_planner(_o)._build_dhw_requirements(
+        _dhw_horizon(
+            prices=np.full(_n, 1.0), outdoor=np.full(_n, -5.0), n=_n, dt=0.25,
+            step_hours=np.array([t.hour + t.minute / 60.0 for t in _ts]),
+            step_weekdays=np.array(
+                [(t0 + _nw_dt.timedelta(hours=(i - 1) * 0.25)).weekday()
+                 for i in range(_n + 1)]),
+            holiday_flags=(np.array(
+                [False] + [t.date() in holidays for t in _ts])
+                if holidays else None),
+        ),
+        p_max=4.0,
+    )
+    _h = t0.hour + t0.minute / 60.0
+    _owner = _nw_hunw(_h, _nw_wif(params, None, t0, holidays),
+                      _nw_wif(params, None, t0, holidays, days=1))
+    _flat = _nw_hunw(_h, list(params.dhw_demand_windows))
+    return _plan.next_window_in_hours, _owner, _flat
+
+
+_nw_cfg = _grad_house(two_zone=False, dhw=True)
+_nw_cfg["dhw_windows"] = _NW_SPEC
+_nw_p = ThermalParameters.from_config(_nw_cfg)
+_nw_grid = {}
+for _nw_day in range(12, 19):  # Mon 2026-01-12 .. Sun 2026-01-18
+    for _nw_h in (0.0, 5.0, 7.0, 8.75, 9.0, 12.0, 23.5):
+        _nw_t = _WDT(2026, 1, _nw_day) + _nw_dt.timedelta(hours=_nw_h)
+        _nw_grid[("weekly", _nw_t.isoformat())] = _nw_cell(_nw_p, _nw_t)
+# A holiday Wednesday reads the holiday set; a Thursday override reads its own.
+_nw_hp = _nw_dc.replace(_nw_p, dhw_holiday_windows=_nw_parse("10:00-11:00"))
+for _nw_h in (7.0, 23.5):
+    _nw_t = _WDT(2026, 1, 13) + _nw_dt.timedelta(hours=_nw_h)
+    _nw_grid[("holiday", _nw_t.isoformat())] = _nw_cell(
+        _nw_hp, _nw_t, frozenset({_nw_dt.date(2026, 1, 14)}))
+    _nw_t = _WDT(2026, 1, 14) + _nw_dt.timedelta(hours=_nw_h)
+    _nw_grid[("holiday", _nw_t.isoformat())] = _nw_cell(
+        _nw_hp, _nw_t, frozenset({_nw_dt.date(2026, 1, 14)}))
+_nw_op = _nw_dc.replace(
+    _nw_p, dhw_day_windows=[None, None, None, _nw_parse("13:00-14:00"),
+                            None, None, None])
+for _nw_h in (7.0, 23.5):
+    for _nw_day in (14, 15):
+        _nw_t = _WDT(2026, 1, _nw_day) + _nw_dt.timedelta(hours=_nw_h)
+        _nw_grid[("override", _nw_t.isoformat())] = _nw_cell(_nw_op, _nw_t)
+# A horizon from midnight never wraps, so the next day is the weekday after;
+# a Saturday with no window reads Sunday's.
+_nw_ec = dict(_nw_cfg, dhw_windows="weekdays 06:00-08:30, Su 09:00-10:00")
+_nw_grid[("no-wrap", "2026-01-17T00:00:00")] = _nw_cell(
+    ThermalParameters.from_config(_nw_ec), _WDT(2026, 1, 17))
+_nw_wrong ={k: v for k, v in _nw_grid.items()
+             if v[0] is None or v[1] is None or abs(v[0] - v[1]) > 1e-9}
+_nw_separating = [k for k, v in _nw_grid.items()
+                  if v[2] is None or v[1] is None or abs(v[2] - v[1]) > 1e-9]
+R.check(
+    "the census grid holds cells where the flat every-day set and the day's "
+    "windows disagree on the next window (its own precondition)",
+    len(_nw_separating) >= 10 and any(k[0] == "holiday" for k in _nw_separating)
+    and any(k[0] == "override" for k in _nw_separating)
+    and _nw_grid[("no-wrap", "2026-01-17T00:00:00")][1] == 33.0,
+    f"{len(_nw_separating)} separating of {len(_nw_grid)}: {_nw_separating[:6]}",
+)
+R.check(
+    "the planner's published next window reads the day's windows, today's and "
+    "the next day's, in every census cell (D17-s3-51, windows_in_force's answer)",
+    not _nw_wrong,
+    f"{len(_nw_wrong)} of {len(_nw_grid)} wrong (planner, owner, flat): "
+    f"{list(_nw_wrong.items())[:4]}",
+)
 # The flat spec is byte-identical to before: the weekly path is entirely
 # gated on dhw_weekly_windows, which is None here. (The drift gate holds
 # this across every captured scenario; this is the local statement.)
@@ -20337,8 +20430,109 @@ R.check(
     "exact minutes the pre-heat exists for",
 )
 R.check(
-    "with no windows the loop is simply left on",
-    _ps.vvc_should_run(3.0, [], 20)[0],
+    "with no schedule the loop is simply left on",
+    _ps.vvc_should_run(3.0, None, 20)[0],
+)
+R.check(
+    "a schedule with no window today keeps the loop off (D17-s3-51)",
+    not _ps.vvc_should_run(3.0, [], 20)[0] and not _ps.vvc_should_run(7.0, [], 20)[0],
+    f"{_ps.vvc_should_run(3.0, [], 20)!r} -- an empty day of a day-aware spec "
+    "read as 'no schedule' ran the loop all day",
+)
+
+# D17-s3-51 and the P2 sweep's F14 seams: every reader asking "is a hot-water
+# window open now" resolves the day's windows (dhw_schedule.windows_in_force),
+# as the planner does per step. On "weekdays 06:00-08:30, weekend
+# 08:00-09:30" Saturday 07:00 is outside every window in force; the flat
+# union 06:00-09:30 read it open at the published flag, boost's release and
+# the draw learner. Monday 07:00 is the control: inside, at every reader.
+from unittest import mock as _d17_mock  # noqa: E402
+from harness import FakeEntry as _d17_entry  # noqa: E402
+from heatpump_optimizer import boost as _d17_boost, dhw_schedule as _d17_sched  # noqa: E402
+from homeassistant.util import dt as _d17_dt_util  # noqa: E402
+
+_D17_MON = datetime(2026, 1, 12, 7, 0, tzinfo=UTC)
+_D17_SAT = _D17_MON + timedelta(days=5)
+_d17_c = Coord(FakeHass({}), _d17_entry(data={
+    "tibber_token": "x", "weather_entity": "weather.home",
+    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
+    "dhw_enabled": True, "dhw_schedule_enabled": True,
+    "dhw_windows": "weekdays 06:00-08:30, weekend 08:00-09:30"}))
+_d17_seen = {}
+for _d17_label, _d17_t in (("mon", _D17_MON), ("sat", _D17_SAT), ("mon_0845", _D17_MON.replace(hour=8, minute=45))):
+    _d17_labels = []
+    with _d17_mock.patch.object(_d17_dt_util, "now", lambda _t=_d17_t: _t), \
+            _d17_mock.patch.object(_d17_c._dhw_learner.draw_stats, "fold",
+                                   lambda now, lab, e, charge=False, _l=_d17_labels: _l.append(lab)):
+        _asyncio.run(_d17_c._dhw_learner.async_fold_draw_stats(_d17_t, 50.0, 3.0, 0.25))
+        _d17_seen[_d17_label] = (
+            _d17_c._dhw_in_demand_window(),
+            _d17_boost._window_open(_d17_c.arbiter_inputs(), _d17_t),
+            _d17_labels,
+        )
+R.check(
+    "the hot-water window in force is the day's at every reader: flag, boost, draw learner (D17-s3-51)",
+    _d17_seen["sat"] == (False, False, [""])
+    and _d17_seen["mon"] == (True, True, ["06:00-09:30"]),
+    f"{_d17_seen} -- Saturday 07:00 lies in the flat union 06:00-09:30 and in "
+    "no window that day",
+)
+R.check(
+    "boost and the draw learner read the clock to the minute: Monday 08:45 is past the 08:30 close (D17-s3-51)",
+    _d17_seen["mon_0845"] == (False, False, [""]),
+    f"{_d17_seen['mon_0845']} -- an hour read at half the minutes (8.375) lands back inside 06:00-08:30",
+)
+_d17_params = _d17_c._thermal_params
+_d17_params.dhw_holiday_windows = [(10.0, 11.0)]
+R.check(
+    "windows_in_force takes the holiday tier on a holiday date and the day's own windows otherwise",
+    _d17_sched.windows_in_force(_d17_params, None, _D17_SAT, {_D17_SAT.date()}) == [(10.0, 11.0)]
+    and _d17_sched.windows_in_force(_d17_params, None, _D17_SAT) == [(8.0, 9.5)]
+    and _d17_sched.windows_in_force(_d17_params, None, _D17_MON) == [(6.0, 8.5)],
+    f"{_d17_sched.windows_in_force(_d17_params, None, _D17_SAT, {_D17_SAT.date()})!r}",
+)
+_d17_params.dhw_holiday_windows = None
+# The learner reads the holiday tier through the coordinator's calendar,
+# its ``holidays`` callback. On a holiday whose windows cover Saturday 07:00,
+# the draw falls in a window. It takes the flat label the planner keys its
+# stats by. The same instant on an ordinary Saturday is out of window.
+_d17_params.dhw_holiday_windows = [(6.5, 7.5)]
+_d17_hol = {}
+for _d17_label, _d17_days in (("holiday", lambda now: {now.date()}), ("ordinary", lambda now: ())):
+    _d17_labels = []
+    _d17_c._dhw_learner._holidays = _d17_days
+    with _d17_mock.patch.object(_d17_c._dhw_learner.draw_stats, "fold",
+                                lambda now, lab, e, charge=False, _l=_d17_labels: _l.append(lab)):
+        _asyncio.run(_d17_c._dhw_learner.async_fold_draw_stats(_D17_SAT, 50.0, 3.0, 0.25))
+    _d17_hol[_d17_label] = _d17_labels
+R.check(
+    "the draw learner takes the holiday tier from the coordinator's calendar (D17-s3-51)",
+    _d17_hol == {"holiday": ["06:00-09:30"], "ordinary": [""]},
+    str(_d17_hol),
+)
+_d17_params.dhw_holiday_windows = None
+
+# The lead across midnight reads TOMORROW's windows: the VVC pre-heat and the
+# published hours to the next window. "Tu 00:10-00:40": Monday 23:55 is 15
+# minutes before Tuesday's window; Tuesday 23:55 is before no window at all
+# (Wednesday has none), where the flat every-day union pre-heated.
+_d17_mid = Coord(FakeHass({}), _d17_entry(data={
+    "tibber_token": "x", "weather_entity": "weather.home",
+    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
+    "dhw_enabled": True, "dhw_schedule_enabled": True, "dhw_windows": "Tu 00:10-00:40"}))
+_D17_MON2355 = datetime(2026, 1, 12, 23, 55, tzinfo=UTC)
+_D17_TUE2355 = _D17_MON2355 + timedelta(days=1)
+_d17_vvc = {
+    _l: _ps.vvc_should_run_at(_t, _d17_mid._thermal_params, 20)[0]
+    for _l, _t in (("mon", _D17_MON2355), ("tue", _D17_TUE2355))
+}
+with _d17_mock.patch.object(_d17_dt_util, "now", lambda: _D17_MON2355):
+    _d17_next = _d17_mid._dhw_next_window_in_hours()
+R.check(
+    "the VVC lead and the next-window hours read tomorrow's windows across midnight (D17-s3-51)",
+    _d17_vvc == {"mon": True, "tue": False} and _d17_next == 0.25
+    and _ps.vvc_should_run_at(_D17_MON2355, None, 20)[0],
+    f"vvc {_d17_vvc} next window {_d17_next!r} h at Monday 23:55",
 )
 
 _SAFE = dict(
@@ -41859,6 +42053,9 @@ _ET_KEYS = {
     "manual_plan_invalid_expires_at": {"expires_at"},
     "manual_plan_invalid_slots": {"error"},
     "run_optimization_no_prices": {"entry_ids"},
+    # D10-s1-02: the system-identification press's two refusals.
+    "system_identification_disabled": {"entry_ids"},
+    "system_identification_not_armed": {"entry_ids", "reason"},
     "run_optimization_solve_failed": {"entry_ids"},
     "simulate_plan_no_plan": {"entry_ids"},
     "simulate_plan_no_prices": {"entry_ids"},
@@ -47625,16 +47822,23 @@ R.check(
     and _r11m_feb_rows == _r11m_jan_rows and not _r11m_jan_rows[0]["estimated"],
     repr(_r11m_feb_rows),
 )
-_r11m_sensor = _r11m_NS(_rows=lambda: _r11m_feb_rows)
+def _r11m_stand_in(rows):
+    """The sensor's two row readers on a stand-in: ``_rows`` and the one open saving."""
+    ns = _r11m_NS(_rows=rows)
+    ns._open_saving = lambda: _r11m_Sensor._open_saving(ns)
+    return ns
+
+
+_r11m_sensor = _r11m_stand_in(lambda: _r11m_feb_rows)
 _r11m_two_day = _SavLedger.from_dict(_r11m_two.as_dict())
 for _h in range(24):
     _r11m_two_day.observe_spot_and_settle_savings(
         datetime(2026, 2, 1, 0, 15) + timedelta(hours=_h), 1.0, {"baseline_kw": 2.0}, 1.0, 1.0)
-_r11m_ready = _r11m_NS(_rows=lambda: _r11m_two_day.savings_months(datetime(2026, 2, 2, 0, 30)))
+_r11m_ready = _r11m_stand_in(lambda: _r11m_two_day.savings_months(datetime(2026, 2, 2, 0, 30)))
 R.check(
     "R11-SEAM-money: MonthlySavingsSensor waits for open_month_coverage while only closed months have rows",
     _r11m_Sensor._waiting_for.fget(_r11m_sensor) == "open_month_coverage"
-    and _r11m_Sensor._waiting_for.fget(_r11m_NS(_rows=lambda: [])) == "settled_savings_month"
+    and _r11m_Sensor._waiting_for.fget(_r11m_stand_in(lambda: [])) == "settled_savings_month"
     and _r11m_Sensor._waiting_for.fget(_r11m_ready) is None,
     f"{_r11m_Sensor._waiting_for.fget(_r11m_sensor)!r} / {_r11m_Sensor._waiting_for.fget(_r11m_ready)!r}",
 )
@@ -51138,7 +51342,6 @@ _RC2_SETTERS = {
     "async_reset_comfort_weight": "row: the reset button",
     "async_reset_heat_loss_learners": "row: the heat-loss reset button",
     "async_restore_learned_snapshot": "restores from the store it reads",
-    "async_arm_system_identification": "in memory by design: arms tonight's run",
     "async_update_thermal_params": "the call's fields persist into entry "
         "options and reload the entry (D1-s2-53, F1.4); the learner anchors "
         "also persist through the thermal-learning store (#86)",
@@ -51266,6 +51469,99 @@ R.check(
 )
 
 
+# D10-s1-02: a refused or failed press raises to the caller, as the action
+# and the optimize-now press do (action-exceptions, Silver). The sysid press
+# with the option off (the default) armed nothing and returned; the diagnose
+# press with the worker down returned while its background task raised.
+from homeassistant.exceptions import ServiceValidationError as _rc2_sve  # noqa: E402
+from heatpump_optimizer.coordinator import ProcessWorkerUnavailable as _rc2_pwu  # noqa: E402
+
+
+async def _rc2_press(cls, setup):
+    entry = FakeEntry(data=dict(_T1_DATA), entry_id=f"rc2_refuse_{cls.__name__}")
+    coord = await _rc2_boot(entry)
+
+    async def _refresh():
+        return None
+
+    coord.async_request_refresh = _refresh
+    setup(coord)
+    ent = cls(coord, entry)
+    ent.hass = _RC2Hass()
+    try:
+        await ent.async_press()
+    except Exception as err:  # noqa: BLE001 - an untranslated escape is the defect's shape
+        return type(err).__name__, getattr(err, "translation_key", None), coord
+    return None, None, coord
+
+
+def _rc2_sysid_off(coord):
+    with_config(coord, {"system_identification_enabled": False})
+
+
+def _rc2_sysid_on(coord):
+    with_config(coord, {"system_identification_enabled": True})
+    coord._thermal_params.slab_heat_transfer *= 100.0  # the #942 gate's fast slab
+
+
+def _rc2_sysid_recent(coord):
+    _rc2_sysid_on(coord)
+    coord._sysid.last_run = _rc2_dt_util.now()  # armable's minimum days between runs
+
+
+def _rc2_worker_down(coord):
+    async def _down():
+        raise _rc2_pwu("the process worker timed out")
+
+    coord.async_diagnose_interval = _down
+
+
+_rc2_off = _asyncio.run(_rc2_press(_rc2_button.SystemIdentificationButton, _rc2_sysid_off))
+_rc2_on = _asyncio.run(_rc2_press(_rc2_button.SystemIdentificationButton, _rc2_sysid_on))
+_rc2_recent = _asyncio.run(_rc2_press(_rc2_button.SystemIdentificationButton, _rc2_sysid_recent))
+_rc2_down = _asyncio.run(_rc2_press(_rc2_button.DiagnoseIntervalButton, _rc2_worker_down))
+R.check(
+    "a refused system-identification press raises a translated refusal; an armed one returns (D10-s1-02)",
+    _rc2_off[:2] == (_rc2_sve.__name__, "system_identification_disabled")
+    and _rc2_off[2]._sysid.phase == "idle"
+    and _rc2_on[:2] == (None, None) and _rc2_on[2]._sysid.phase == "armed"
+    and _rc2_recent[:2] == (_rc2_sve.__name__, "system_identification_not_armed")
+    and _rc2_recent[2]._sysid.phase == "idle",
+    f"option off -> {_rc2_off[:2]} phase {_rc2_off[2]._sysid.phase!r}; "
+    f"ran just now -> {_rc2_recent[:2]}; "
+    f"option on -> {_rc2_on[:2]} phase {_rc2_on[2]._sysid.phase!r}",
+)
+R.check(
+    "a diagnose press whose worker is down raises the action's diagnose_interval_failed (D10-s1-02)",
+    _rc2_down[:2] == ("HomeAssistantError", "diagnose_interval_failed"),
+    f"{_rc2_down[:2]} -- the press returned while its background task raised",
+)
+
+
+_rc2_refreshes: list[str] = []
+
+
+def _rc2_diagnosed(coord):
+    async def _ran():
+        return None
+
+    def _refresh():  # counted when asked for: the press hands the coroutine off the action
+        _rc2_refreshes.append("refresh")
+        return _ran()
+
+    coord.async_diagnose_interval = _ran
+    coord.async_request_refresh = _refresh
+
+
+_rc2_ran = _asyncio.run(_rc2_press(_rc2_button.DiagnoseIntervalButton, _rc2_diagnosed))
+R.check(
+    "a diagnose press whose diagnosis ran returns and asks for the refresh that publishes it (D10-s1-02)",
+    _rc2_ran[:2] == (None, None) and _rc2_refreshes == ["refresh"],
+    f"{_rc2_ran[:2]}, refreshes asked {len(_rc2_refreshes)} -- without the refresh the "
+    "diagnosis lands in the payload only at the next cycle",
+)
+
+
 async def _rc2_manual_plan():
     """The service setters with no entity: apply, then clear, each followed by
     a restart that cancels the refresh it asked for."""
@@ -54678,17 +54974,15 @@ R.check(
 
 # The user-facing route: the item-18 button on a DEFAULT install (no k_s bump).
 _arm1329 = _t4_coord()
-_t4_count_refresh(_arm1329)
 with_config(_arm1329, {"system_identification_enabled": True})
-_t4_drive(_arm1329, "async_arm_system_identification")
+_arm1329_refused = _arm1329.arm_system_identification()
 R.check(
     "#1329: the item-18 button arms on a default install (was inert)",
     _arm1329._sysid.phase == "armed"
     and _arm1329._sysid.active
-    and _arm1329._t4_refreshes == 1
-    and _arm1329._t4_escaped is None,
+    and _arm1329_refused is None,
     f"phase {_arm1329._sysid.phase!r} active {_arm1329._sysid.active} "
-    f"refreshes {_arm1329._t4_refreshes} "
+    f"refused {_arm1329_refused!r} "
     f"reason {_arm1329._sysid.result.reason!r} -- before the fix every "
     "answers-based install refused here with 'slab mode too slow for the "
     "excitation window', so the button reported nothing at any plant the "
@@ -55449,11 +55743,11 @@ _t4_arm_on._thermal_params.slab_heat_transfer *= 100.0
 _t4_count_refresh(_t4_arm_on)
 _t4_arm_on_built = _t4_arm_on._sysid.config.enabled
 with_config(_t4_arm_on, {"system_identification_enabled": True})
-_t4_drive(_t4_arm_on, "async_arm_system_identification")
+_t4_arm_on.arm_system_identification()
 _t4_arm_off = _t4_coord(system_identification_enabled=True)
 _t4_count_refresh(_t4_arm_off)
 with_config(_t4_arm_off, {"system_identification_enabled": False})
-_t4_drive(_t4_arm_off, "async_arm_system_identification")
+_t4_arm_off.arm_system_identification()
 R.check(
     "arming re-reads the option at call time, so an edit needs no reload",
     _t4_arm_on_built is False
@@ -55468,15 +55762,35 @@ R.check(
     f"{_t4_arm_off._sysid.phase!r} -- both directions, because the push is "
     "invisible whenever the constructed value already agrees",
 )
+# The arm is a synchronous decision since D10-s1-02, so the press, not the
+# arm, schedules the refresh that publishes it: armed or refused alike.
+from heatpump_optimizer import button as _t4_button  # noqa: E402
+from unittest import mock as _t4_mock  # noqa: E402
+
+_t4_scheduled = []
+
+
+def _t4_off_action(entity, work):
+    _t4_scheduled.append(entity.coordinator)
+    work.close()
+
+
+_t4_press = {}
+for _t4_label, _t4_on in (("armed", True), ("refused", False)):
+    _t4_c = _t4_coord(system_identification_enabled=_t4_on)
+    _t4_c._thermal_params.slab_heat_transfer *= 100.0
+    _t4_ent = _t4_button.SystemIdentificationButton(_t4_c, _t4_c.entry)
+    with _t4_mock.patch.object(_t4_button, "off_the_action", _t4_off_action):
+        try:
+            _asyncio.run(_t4_ent.async_press())
+            _t4_press[_t4_label] = (None, _t4_scheduled.count(_t4_c))
+        except Exception as err:  # noqa: BLE001
+            _t4_press[_t4_label] = (type(err).__name__, _t4_scheduled.count(_t4_c))
 R.check(
-    "a refused arm still refreshes, which is what publishes the refusal",
-    _t4_arm_on._t4_refreshes == 1
-    and _t4_arm_off._t4_refreshes == 1
-    and _t4_arm_on._t4_escaped is None
-    and _t4_arm_off._t4_escaped is None,
-    f"armed -> {_t4_arm_on._t4_refreshes} refresh, refused -> "
-    f"{_t4_arm_off._t4_refreshes} -- returning early on a refusal leaves the "
-    "user's own button reporting nothing at all",
+    "a refused press still schedules the refresh, which is what publishes the refusal",
+    _t4_press == {"armed": (None, 1), "refused": ("ServiceValidationError", 1)},
+    f"{_t4_press} -- returning early on a refusal leaves the user's own "
+    "button reporting nothing at all",
 )
 
 _t4_reset = _t4_coord(comfort_learning_enabled=True)
@@ -89321,11 +89635,7 @@ def _cp_coord(samples=482, **config):
     c._house_heat_loss_samples = samples
     with_config(c, {"system_identification_enabled": True})
 
-    async def _no_refresh():
-        return None
-
-    c.async_request_refresh = _no_refresh
-    _cp_aio.run(c.async_arm_system_identification())
+    c.arm_system_identification()
     return c
 
 
diff --git a/tests/harness.py b/tests/harness.py
index 56347324cd..ac3caf1e7e 100644
--- a/tests/harness.py
+++ b/tests/harness.py
@@ -481,8 +481,9 @@ class FakeCoordinator:
         self.pressed.append("force_optimization")
         return None
 
-    async def async_arm_system_identification(self):
+    def arm_system_identification(self):
         self.pressed.append("system_identification")
+        return None
 
     async def async_reset_comfort_weight(self):
         self.pressed.append("reset_comfort_weight")
diff --git a/tests/hastub/homeassistant/components/sensor.py b/tests/hastub/homeassistant/components/sensor.py
index e141bb779d..0358c998ca 100644
--- a/tests/hastub/homeassistant/components/sensor.py
+++ b/tests/hastub/homeassistant/components/sensor.py
@@ -5,6 +5,9 @@ from homeassistant.helpers.entity import Entity
 
 class SensorDeviceClass(str):
     TEMPERATURE = "temperature"
+    # Upstream since 2025.11.0, above the hacs.json floor: production reads it
+    # through getattr (sensor._TEMPERATURE_DELTA), so the floor still loads.
+    TEMPERATURE_DELTA = "temperature_delta"
     POWER = "power"
     ENERGY = "energy"
     MONETARY = "monetary"
@@ -33,6 +36,7 @@ class SensorStateClass(str):
 #: class is never a violation.
 DEVICE_CLASS_STATE_CLASSES = {
     SensorDeviceClass.TEMPERATURE: {SensorStateClass.MEASUREMENT},
+    SensorDeviceClass.TEMPERATURE_DELTA: {SensorStateClass.MEASUREMENT},
     SensorDeviceClass.POWER: {SensorStateClass.MEASUREMENT},
     SensorDeviceClass.ENERGY: {
         SensorStateClass.TOTAL,
diff --git a/tests/mutation_ledger/killed_by/binary_sensor.py/WoodCheaperBinarySensor.available.BOOLOP.fdaf4ca2.json b/tests/mutation_ledger/killed_by/binary_sensor.py/WoodCheaperBinarySensor.available.BOOLOP.fdaf4ca2.json
deleted file mode 100644
index 5aaf57781a..0000000000
--- a/tests/mutation_ledger/killed_by/binary_sensor.py/WoodCheaperBinarySensor.available.BOOLOP.fdaf4ca2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/binary_sensor.py:WoodCheaperBinarySensor.available BOOLOP fdaf4ca2",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and fuel.get(\"ready\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or fuel.get(\"ready\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.2d0b59e7.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.2d0b59e7.json
deleted file mode 100644
index 361db9eeef..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.2d0b59e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open GUARD_OFF 2d0b59e7",
-  "killed_by": "tests/block_duty.py",
-  "old": "    if not windows:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 62f604eb062bf88d3dc4b0f4ec85ca17359af229: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.6492d240.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.6492d240.json
deleted file mode 100644
index 35d5e8ca38..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_window_open.GUARD_OFF.6492d240.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open GUARD_OFF 6492d240",
-  "killed_by": "tests/block_duty.py",
-  "old": "    if planned:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 62f604eb062bf88d3dc4b0f4ec85ca17359af229: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.015b285e.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.015b285e.json
deleted file mode 100644
index a41a57a675..0000000000
--- a/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.015b285e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open RETURN_DEL 015b285e",
-  "killed_by": "tests/block_duty.py",
-  "old": "    return hour_in_windows(hour, windows)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 62f604eb062bf88d3dc4b0f4ec85ca17359af229: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.571abbe7.json b/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.571abbe7.json
new file mode 100644
index 0000000000..e7c06bef39
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/boost.py/_window_open.RETURN_DEL.571abbe7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open RETURN_DEL 571abbe7",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return hour_in_windows(now.hour + now.minute / 60.0, windows)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.4a4aab1a.json b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.4a4aab1a.json
new file mode 100644
index 0000000000..5c6f861628
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.4a4aab1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/button.py:SystemIdentificationButton.async_press GUARD_OFF 4a4aab1a",
+  "killed_by": "tests/features.py",
+  "old": "        if refused == sysid.ARM_REFUSED_DISABLED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.83253676.json b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.83253676.json
new file mode 100644
index 0000000000..05ae7d3e19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/button.py/SystemIdentificationButton.async_press.GUARD_OFF.83253676.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/button.py:SystemIdentificationButton.async_press GUARD_OFF 83253676",
+  "killed_by": "tests/features.py",
+  "old": "        if refused is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.BOOLOP.320af692.json b/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.BOOLOP.320af692.json
deleted file mode 100644
index 779372da85..0000000000
--- a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.BOOLOP.320af692.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/climate.py:HeatPumpOptimizerClimate.available BOOLOP 320af692",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and flags.get(\"upper_floor_temperature\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or flags.get(\"upper_floor_temperature\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.RETURN_DEL.320af692.json b/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.RETURN_DEL.320af692.json
deleted file mode 100644
index 33bc4b0038..0000000000
--- a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.available.RETURN_DEL.320af692.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/climate.py:HeatPumpOptimizerClimate.available RETURN_DEL 320af692",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and flags.get(\"upper_floor_temperature\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_on_grid.GUARD_OFF.390fac7a.json b/tests/mutation_ledger/killed_by/config_flow.py/_on_grid.GUARD_OFF.390fac7a.json
new file mode 100644
index 0000000000..efea1bbfe1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_on_grid.GUARD_OFF.390fac7a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_on_grid GUARD_OFF 390fac7a",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if value == declared or base is None or not isinstance(step, (int, float)) or step <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.0fe17c48.json b/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.0fe17c48.json
new file mode 100644
index 0000000000..0091be4b72
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.0fe17c48.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_widen_to_fit GUARD_OFF 0fe17c48",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not math.isfinite(number_value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.7a72fcf1.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.7a72fcf1.json
deleted file mode 100644
index a72004e967..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.7a72fcf1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_drive_pumps BOOLOP 7a72fcf1",
-  "killed_by": "tests/features.py",
-  "old": "                if params.dhw_enabled and params.dhw_windows_active",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if params.dhw_enabled or params.dhw_windows_active`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.a550a1f3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.a550a1f3.json
new file mode 100644
index 0000000000..e5fb60d71f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.a550a1f3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_drive_pumps BOOLOP a550a1f3",
+  "killed_by": "tests/features.py",
+  "old": "            scheduled = params.dhw_enabled and params.dhw_windows_active",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`scheduled = params.dhw_enabled or params.dhw_windows_active`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.GUARD_OFF.077aa3ea.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.GUARD_OFF.077aa3ea.json
deleted file mode 100644
index dcff060351..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.GUARD_OFF.077aa3ea.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_effective_windows GUARD_OFF 077aa3ea",
-  "killed_by": "tests/features.py",
-  "old": "        if planned:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.99a2b558.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.99a2b558.json
deleted file mode 100644
index 97f21378f3..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.99a2b558.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_effective_windows RETURN_DEL 99a2b558",
-  "killed_by": "tests/features.py",
-  "old": "        return windows",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.ba9098c8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.ba9098c8.json
new file mode 100644
index 0000000000..68f7fbb3f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_effective_windows.RETURN_DEL.ba9098c8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_effective_windows RETURN_DEL ba9098c8",
+  "killed_by": "tests/structure.py",
+  "old": "        return windows_in_force(ctx._thermal_params, self._optimization_result, now, holidays, days)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.BOOLOP.e8eac339.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.BOOLOP.e8eac339.json
new file mode 100644
index 0000000000..fea6537c19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.BOOLOP.e8eac339.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window BOOLOP e8eac339",
+  "killed_by": "tests/features.py",
+  "old": "    if windows and hour_in_windows(hour, windows):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if windows or hour_in_windows(hour, windows):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.e8eac339.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.e8eac339.json
new file mode 100644
index 0000000000..6549aeeb2b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.e8eac339.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window GUARD_OFF e8eac339",
+  "killed_by": "tests/features.py",
+  "old": "    if windows and hour_in_windows(hour, windows):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.f92e3c65.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.f92e3c65.json
deleted file mode 100644
index ef9cd75ceb..0000000000
--- a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.GUARD_OFF.f92e3c65.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window GUARD_OFF f92e3c65",
-  "killed_by": "tests/features.py",
-  "old": "        if best is None or delta < best:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.RETURN_DEL.9a247f7f.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.RETURN_DEL.9a247f7f.json
deleted file mode 100644
index 3549e5fe02..0000000000
--- a/tests/mutation_ledger/killed_by/dhw_schedule.py/hours_until_next_window.RETURN_DEL.9a247f7f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hours_until_next_window RETURN_DEL 9a247f7f",
-  "killed_by": "tests/features.py",
-  "old": "    return best",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/windows_in_force.GUARD_OFF.2891c313.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/windows_in_force.GUARD_OFF.2891c313.json
new file mode 100644
index 0000000000..4194b8f349
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/windows_in_force.GUARD_OFF.2891c313.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:windows_in_force GUARD_OFF 2891c313",
+  "killed_by": "tests/features.py",
+  "old": "    if info.get(\"dhw_windows\"):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_schedule.py/vvc_should_run.GUARD_OFF.2d0b59e7.json b/tests/mutation_ledger/killed_by/pump_schedule.py/vvc_should_run.GUARD_OFF.2d0b59e7.json
deleted file mode 100644
index dd9510104f..0000000000
--- a/tests/mutation_ledger/killed_by/pump_schedule.py/vvc_should_run.GUARD_OFF.2d0b59e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_schedule.py:vvc_should_run GUARD_OFF 2d0b59e7",
-  "killed_by": "tests/features.py",
-  "old": "    if not windows:",
-  "reason": "Recorded by `mutation_table.py --drain` against 15f0b5924f3c2a75befe984d156cb3e602effd2e: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/CompressorStartsSensor.available.RETURN_DEL.950e6d25.json b/tests/mutation_ledger/killed_by/sensor.py/CompressorStartsSensor.available.RETURN_DEL.950e6d25.json
deleted file mode 100644
index b949de5809..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/CompressorStartsSensor.available.RETURN_DEL.950e6d25.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:CompressorStartsSensor.available RETURN_DEL 950e6d25",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data)",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.BOOLOP.33e22e1d.json b/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.BOOLOP.33e22e1d.json
deleted file mode 100644
index 459e39f6d9..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.BOOLOP.33e22e1d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MeasuredPowerSensor.available BOOLOP 33e22e1d",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data.get(\"measured_power_available\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or data.get(\"measured_power_available\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.RETURN_DEL.33e22e1d.json b/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.RETURN_DEL.33e22e1d.json
deleted file mode 100644
index dcb953583b..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MeasuredPowerSensor.available.RETURN_DEL.33e22e1d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MeasuredPowerSensor.available RETURN_DEL 33e22e1d",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data.get(\"measured_power_available\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MixedHotWaterSensor.available.BOOLOP.0bd743fb.json b/tests/mutation_ledger/killed_by/sensor.py/MixedHotWaterSensor.available.BOOLOP.0bd743fb.json
deleted file mode 100644
index b156d31821..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MixedHotWaterSensor.available.BOOLOP.0bd743fb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MixedHotWaterSensor.available BOOLOP 0bd743fb",
-  "killed_by": "tests/entities.py",
-  "old": "            super().available and (self._data()).get(\"dhw_mixed\")",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 777c23180a08b0d6c7abd41d6dd5fe7b1abf19b3: BOOLOP (`super().available or (self._data()).get(\"dhw_mixed\")`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.BOOLOP.1ba360a6.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.BOOLOP.1ba360a6.json
deleted file mode 100644
index 8fe0553541..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.BOOLOP.1ba360a6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for BOOLOP 1ba360a6",
-  "killed_by": "tests/features.py",
-  "old": "        if any(isinstance(row, dict) and row.get(\"estimated\") for row in rows):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if any(isinstance(row, dict) or row.get(\"estimated\") for row in rows):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.1ba360a6.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.1ba360a6.json
deleted file mode 100644
index 50a869ceae..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.1ba360a6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for GUARD_OFF 1ba360a6",
-  "killed_by": "tests/entities.py",
-  "old": "        if any(isinstance(row, dict) and row.get(\"estimated\") for row in rows):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.e9869136.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.e9869136.json
deleted file mode 100644
index 9cfc248976..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.GUARD_OFF.e9869136.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for GUARD_OFF e9869136",
-  "killed_by": "tests/entities.py",
-  "old": "        if not rows:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.2c97a7fe.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.2c97a7fe.json
deleted file mode 100644
index 0aa7b432e3..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.2c97a7fe.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for RETURN_DEL 2c97a7fe",
-  "killed_by": "tests/features.py",
-  "old": "        return \"open_month_coverage\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.fd57f30a.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.fd57f30a.json
new file mode 100644
index 0000000000..e5f003620a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor._waiting_for.RETURN_DEL.fd57f30a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for RETURN_DEL fd57f30a",
+  "killed_by": "tests/harness_headers.py",
+  "old": "        return \"open_month_coverage\" if self._rows() else \"settled_savings_month\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/harness_headers.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.GUARD_OFF.9fb40798.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.GUARD_OFF.9fb40798.json
deleted file mode 100644
index 9bd13d54f9..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.GUARD_OFF.9fb40798.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor.native_value GUARD_OFF 9fb40798",
-  "killed_by": "tests/entities.py",
-  "old": "            if isinstance(row, dict) and row.get(\"estimated\"):",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.RETURN_DEL.f0d4f327.json b/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.RETURN_DEL.f0d4f327.json
deleted file mode 100644
index 2d22430fa9..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/MonthlySavingsSensor.native_value.RETURN_DEL.f0d4f327.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor.native_value RETURN_DEL f0d4f327",
-  "killed_by": "tests/entities.py",
-  "old": "                return None if val is None else round(val, 2)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 99cf51c1a73a5a1a44577021399b7f1cfcab898d: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/PVSurplusSensor.available.BOOLOP.b6a68906.json b/tests/mutation_ledger/killed_by/sensor.py/PVSurplusSensor.available.BOOLOP.b6a68906.json
deleted file mode 100644
index d22eed8a41..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/PVSurplusSensor.available.BOOLOP.b6a68906.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:PVSurplusSensor.available BOOLOP b6a68906",
-  "killed_by": "tests/entities.py",
-  "old": "            super().available and (self._data()).get(\"pv_enabled\")",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 777c23180a08b0d6c7abd41d6dd5fe7b1abf19b3: BOOLOP (`super().available or (self._data()).get(\"pv_enabled\")`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/PowerHeadroomSensor.available.BOOLOP.7455907d.json b/tests/mutation_ledger/killed_by/sensor.py/PowerHeadroomSensor.available.BOOLOP.7455907d.json
deleted file mode 100644
index f286cec7c4..0000000000
--- a/tests/mutation_ledger/killed_by/sensor.py/PowerHeadroomSensor.available.BOOLOP.7455907d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sensor.py:PowerHeadroomSensor.available BOOLOP 7455907d",
-  "killed_by": "tests/entities.py",
-  "old": "        return bool(super().available and data.get(\"available\"))",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`return bool(super().available or data.get(\"available\"))`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/survivor_triage/boost.py/_window_open.GUARD_OFF.2d0b59e7~2.json b/tests/mutation_ledger/survivor_triage/boost.py/_window_open.GUARD_OFF.2d0b59e7~2.json
deleted file mode 100644
index faf59b7bf7..0000000000
--- a/tests/mutation_ledger/survivor_triage/boost.py/_window_open.GUARD_OFF.2d0b59e7~2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/boost.py:_window_open GUARD_OFF 2d0b59e7#2",
-  "old": "    if not windows:",
-  "reason": "Equivalent (GUARD_OFF) on the second `if not windows`. Skipping return False falls through to hour_in_windows(hour, windows). hour_in_windows(12.0, []) is False, measured by PYTHONPATH=tests/hastub:custom_components python3 -c 'from heatpump_optimizer.dhw_schedule import hour_in_windows; print(hour_in_windows(12.0, []))'.",
-  "verdict": "equivalent"
-}
diff --git a/tests/seam_map.json b/tests/seam_map.json
index 3f77543780..5d133142c5 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -207,8 +207,8 @@
   "_whatif_solve": "core",
   "adopt_action": "core",
   "arbiter_inputs": "views",
+  "arm_system_identification": "core",
   "async_apply_manual_plan": "core",
-  "async_arm_system_identification": "core",
   "async_clear_manual_plan": "core",
   "async_diagnose_interval": "core",
   "async_publish_current_action": "views",
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 87b424eaa0..cda05f2a75 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,24 +1,24 @@
 {
- "class_excess_loc": 17317,
+ "class_excess_loc": 17280,
  "const_modules_over_50": 4,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
  "coordinator_private_reach": 0,
  "dead_methods": 0,
- "dead_top_level_symbols": 1,
- "duplication_copies": 5,
+ "dead_top_level_symbols": 0,
+ "duplication_copies": 3,
  "functions_cc_over_15": 26,
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
  "in_function_copies": 11,
  "max_cc": 44,
- "max_class_loc": 7868,
+ "max_class_loc": 7857,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
- "module_excess_loc": 21779,
+ "module_excess_loc": 21778,
  "name_kept_members": 38,
- "recorded_at": "4ebd430fbff9a7b19582ca530a817f34abbafa16",
+ "recorded_at": "baa9a467ac518bc3f8733d2603ea8ae406b235af",
  "seam_cut_total": 413,
- "unloaded_package_imports": 14
+ "unloaded_package_imports": 5
 }
diff --git a/tests/worker_deadlines.py b/tests/worker_deadlines.py
index d4576b8770..a7dfd84707 100644
--- a/tests/worker_deadlines.py
+++ b/tests/worker_deadlines.py
@@ -530,6 +530,10 @@ def run(R, _parent: int) -> None:
                 raise self.outcome
             return self.outcome
 
+        async def async_request_refresh(self):
+            """The service publishes each diagnosis it ran (D10-s1-02)."""
+            return None
+
 
     def _wt_diagnose(outcome):
         saved = _wt_svc._manual_targets

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
