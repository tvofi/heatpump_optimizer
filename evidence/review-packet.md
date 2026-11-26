# Review packet #3907
head: 46cdd1f9191180fc1f420a0d5eedd0f758b947ad
base: 8f22a3b2842987bf6da13dedb08c4b99b7447f1f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139744780639 success
arch-score / arch-score id=139743769458 success
arm id=139741915373 skipped
budget-raise-gate / budget-raise-gate id=139743769287 success
cancel-superseded id=139742452406 success
codeql id=139742578889 skipped
codeql / Analyze (actions) id=139743769448 success
codeql / Analyze (javascript-typescript) id=139743769477 success
codeql / Analyze (python) id=139743769444 success
gate id=139743440900 failure
governance id=139742578216 skipped
governance / env-matrix id=139743769604 in_progress
governance / instrument-self-tests id=139743769465 in_progress
governance / policy-docs id=139743769455 in_progress
governance / record id=139743771150 skipped
governance / wave-script id=139743769379 success
hassfest id=139742577888 skipped
hassfest / hassfest id=139743769399 success
kernel-points id=139743771357 skipped
pr-contract id=139743442234 skipped
prelude id=139742452584 success
refresh id=139742452529 success
sweep-self id=139744083753 skipped
tests id=139742577892 skipped
tests / arch-instrument id=139744834442 queued
tests / briefs id=139743769384 success
tests / browser id=139744834398 queued
tests / closure-scope id=139743769436 success
tests / closures id=139744834371 queued
tests / coverage id=139744834422 queued
tests / fast (3.14) id=139744834382 queued
tests / mutation id=139743769371 failure
tests / mutation-pins (1) id=139744386308 queued
tests / mutation-pins (10) id=139744386271 queued
tests / mutation-pins (11) id=139744386211 queued
tests / mutation-pins (12) id=139744386256 queued
tests / mutation-pins (2) id=139744386222 queued
tests / mutation-pins (3) id=139744386278 in_progress
tests / mutation-pins (4) id=139744386257 in_progress
tests / mutation-pins (5) id=139744386306 queued
tests / mutation-pins (6) id=139744386214 queued
tests / mutation-pins (7) id=139744386284 queued
tests / mutation-pins (8) id=139744386327 queued
tests / mutation-pins (9) id=139744386277 queued
tests / nightly-ha id=139744836533 skipped
tests / nightly-status id=139743769356 failure
tests / replay id=139744834412 queued
tests / typing id=139744834474 queued
validate id=139742578897 skipped
validate / validate-hacs id=139743769277 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 139743769465: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at 46cdd1f9191180fc1f420a0d5eedd0f758b947ad in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --prelude 'exec(open("P").read())' "R11-OUTSIDE-START-APPROACH: a run's"
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py --emit-prelude P "R11-OUTSIDE-START-APPROACH: a run's"
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_honest_starts_runs.py approach
             `dev/audit/harnesses/r11_honest_starts_runs.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/audit/archscore/score.py --diff d972dae309
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         GOLDEN_MODE=drift GOLDEN_REF=d972dae309 PYTHONPATH=tests/hastub python3 tests/golden.py
             `tests/golden.py` is in the tree at this head
  unverified git diff --quiet d972dae309 HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt && echo IDENTICAL
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         ./tests/derive_closures.sh --scripts-from F --record-only --out-dir D
             `tests/derive_closures.sh` is in the tree at this head
  ok         python3 tests/closure.py merge --in-dir D --partial --allow-failures
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified PYTHONPATH=tests/hastub:tests python3 -c "import comment_ratchet; [print(p, n) for n, p, d in comment_ratchet.gate('origin/main')]"
             python3 runs an inline script rather than a file
  unverified git grep -n "_commanded_power()\|_commanded_split()"
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n 'predicted_power_kw\|pending\["split"\]\|pending.get("power")'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n "plan_promise(\|power_schedule"
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n 'action.get("power"\|get("dhw_power"'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --name-only d972dae309 HEAD -- custom_components | wc -l
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 10 resolved, 7 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.32289174.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.32289174.json
index 52b2a109c9..c5ddcc60b4 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.32289174.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature BOOLOP 25dfd051",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature BOOLOP 32289174",
   "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if value is not None or self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if value is not None or self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.32289174.json
similarity index 68%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.32289174.json
index 4c2a483d6d..f174a69bd6 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.32289174.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF 25dfd051",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF 32289174",
   "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
+  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.955886dd.json
similarity index 52%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.955886dd.json
index 63ac676bff..dae47ab630 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.955886dd.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF cd19f403",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_internal_gains GUARD_OFF 955886dd",
   "killed_by": "tests/features.py",
-  "old": "        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.OCCUPANCY) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.d3d77cdd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.d3d77cdd.json
deleted file mode 100644
index 8627fe3928..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.d3d77cdd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop BOOLOP d3d77cdd",
-  "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None or not heat_energy.meter_of(self).counter):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.07efdbdf.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.07efdbdf.json
index 84f259b026..40d98a1a0e 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.07efdbdf.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF d3d77cdd",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 07efdbdf",
   "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, sample=learning_freeze.space_heat(heat_kw is not None or heat_energy.meter_of(self).counter), evidence=_space_evidence(self, self._commanded_split())):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.5a195a77.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.5a195a77.json
new file mode 100644
index 0000000000..87ff434cc0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.5a195a77.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF 5a195a77",
+  "killed_by": "tests/features.py",
+  "old": "        if heat_energy.ran_hot_water((m := heat_energy.meter_of(self)).attribution(split := (commanded_space, dhw_share))) or m.unplanned_charge(split):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.BOOLOP.a70a3ddd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.BOOLOP.a70a3ddd.json
deleted file mode 100644
index 1cef75bb3f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.BOOLOP.a70a3ddd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen BOOLOP a70a3ddd",
-  "killed_by": "tests/features.py",
-  "old": "        if room_air and self._vent_cusum.tripped:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if room_air or self._vent_cusum.tripped:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=31."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.4aa09690.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.4aa09690.json
deleted file mode 100644
index b5772501af..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.4aa09690.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF 4aa09690",
-  "killed_by": "tests/features.py",
-  "old": "        if health is not None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=29."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.cd0382df.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.cd0382df.json
deleted file mode 100644
index c99d0349c4..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.cd0382df.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF cd0382df",
-  "killed_by": "tests/features.py",
-  "old": "        if self._external_heat_active:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json
deleted file mode 100644
index c42b539e06..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF f728b131",
-  "killed_by": "tests/features.py",
-  "old": "        if signals.defrosting:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.fe0eb2bc.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.fe0eb2bc.json
deleted file mode 100644
index b00c678925..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.fe0eb2bc.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF fe0eb2bc",
-  "killed_by": "tests/structure.py",
-  "old": "        if boost.space_learning_frozen(self):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 82d1f47f20c0557f6898f843960eaa64bb20cbfd: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.2050bdf3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.2050bdf3.json
deleted file mode 100644
index b40cdb30c8..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.2050bdf3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen RETURN_DEL 2050bdf3",
-  "killed_by": "tests/features.py",
-  "old": "        return _tail_freeze(self)",
-  "reason": "Recorded by applying the mutant on this branch: RETURN_DEL (`pass`) makes HeatPumpOptimizerCoordinator._learning_frozen return None on an unmetered switch-plus-setpoint install, and tests/features.py's check that the house learner freezes there expects unmetered_power. `mutation_table.py --pin-killed` records no verdict on this machine because tests/features.py's baseline is red on R9-F2.1 P3, the same pair origin/main fails."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.937e866c.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.937e866c.json
new file mode 100644
index 0000000000..6cbe18fb68
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.937e866c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen RETURN_DEL 937e866c",
+  "killed_by": "tests/features.py",
+  "old": "        return learning_freeze.reason(_freeze_facts(self), keys, sample, evidence)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=77."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
deleted file mode 100644
index 55ee71d138..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF fe5030a3",
-  "killed_by": "tests/features.py",
-  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending[\"split\"])):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_quiet_comfort_period.GUARD_OFF.955886dd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_quiet_comfort_period.GUARD_OFF.955886dd.json
new file mode 100644
index 0000000000..645e213a8c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_quiet_comfort_period.GUARD_OFF.955886dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_quiet_comfort_period GUARD_OFF 955886dd",
+  "killed_by": "tests/features.py",
+  "old": "        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.OCCUPANCY) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._settle_defrost.GUARD_OFF.b00f0008.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._settle_defrost.GUARD_OFF.b00f0008.json
deleted file mode 100644
index 680723786f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._settle_defrost.GUARD_OFF.b00f0008.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._settle_defrost GUARD_OFF b00f0008",
-  "killed_by": "tests/features.py",
-  "old": "        if ratio is not None and in_frost_band(outdoor) and not _cop_fold_blocked(self):",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.2de48876.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.2de48876.json
deleted file mode 100644
index e51e155a19..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.2de48876.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._track_curve_comfort GUARD_OFF 2de48876",
-  "killed_by": "tests/features.py",
-  "old": "        if (self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) or learner_room_unread(ctx._config)) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.442286fa.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.442286fa.json
deleted file mode 100644
index f56ab545b2..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.442286fa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._track_curve_comfort GUARD_OFF 442286fa",
-  "killed_by": "tests/features.py",
-  "old": "        if self._away_state.active or self._away_state.recovery_active:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.23b8d2ba.json
similarity index 61%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
rename to tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.23b8d2ba.json
index d4aaf40705..c7830f4293 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.23b8d2ba.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF a70a3ddd",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_learn_heat_span GUARD_OFF 23b8d2ba",
   "killed_by": "tests/features.py",
-  "old": "        if room_air and self._vent_cusum.tripped:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+  "old": "        if close.house or close.lower:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.cee88ab2.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
rename to tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.cee88ab2.json
index 7e0808e417..a3f2cbf897 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.cee88ab2.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c294c9b7",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_learn_heat_span GUARD_OFF cee88ab2",
   "killed_by": "tests/features.py",
-  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
+  "old": "        if close.cop:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.06010c5d.json b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.06010c5d.json
deleted file mode 100644
index 8f7c08f96e..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.06010c5d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_fold_flow_lift GUARD_OFF 06010c5d",
-  "killed_by": "tests/features.py",
-  "old": "    if coord._learning_frozen(CONF_OUTDOOR_TEMP_ENTITY) is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_space_evidence.RETURN_DEL.051d6794.json b/tests/mutation_ledger/killed_by/coordinator.py/_space_evidence.RETURN_DEL.051d6794.json
new file mode 100644
index 0000000000..c17416afad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_space_evidence.RETURN_DEL.051d6794.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_space_evidence RETURN_DEL 051d6794",
+  "killed_by": "tests/features.py",
+  "old": "    return learning_freeze.Evidence(unplanned_charge=heat_energy.meter_of(coord).unplanned_charge(split))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.805aff0a.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.805aff0a.json
new file mode 100644
index 0000000000..4e1fcd591b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.805aff0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST 805aff0a",
+  "killed_by": "tests/features.py",
+  "old": "_STORE_MARGIN_K = 0.02",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_STORE_MARGIN_K = 0.04`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.819025de.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.819025de.json
new file mode 100644
index 0000000000..8f100f698d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.819025de.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST 819025de",
+  "killed_by": "tests/features.py",
+  "old": "_COP_KNOT_K = 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_COP_KNOT_K = 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.c95e30be.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.c95e30be.json
index 6778cf2e61..9b96ba4842 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.c95e30be.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:<module> CONST c95e30be",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST c95e30be",
   "killed_by": "tests/block_duty.py",
   "old": "STARTABLE_ROUNDS = 8",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`STARTABLE_ROUNDS = 16`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.ccd84963.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.ccd84963.json
new file mode 100644
index 0000000000..07357b167d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.ccd84963.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST ccd84963",
+  "killed_by": "tests/features.py",
+  "old": "SHORTFALL_K = 0.05",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SHORTFALL_K = 0.1`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.dce4c8cc.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.dce4c8cc.json
new file mode 100644
index 0000000000..5741e3d53f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.dce4c8cc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST dce4c8cc",
+  "killed_by": "tests/features.py",
+  "old": "_STORE_GRID_K = 0.25",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_STORE_GRID_K = 0.5`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.GUARD_OFF.e1433e05.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.GUARD_OFF.e1433e05.json
new file mode 100644
index 0000000000..3e816db2b9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.GUARD_OFF.e1433e05.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> GUARD_OFF e1433e05",
+  "killed_by": "tests/structure.py",
+  "old": "if TYPE_CHECKING:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.073c5b69.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.073c5b69.json
new file mode 100644
index 0000000000..59dfea130e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.073c5b69.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.__init__ CLAMP_DROP 073c5b69",
+  "killed_by": "tests/features.py",
+  "old": "            self.lo, float(np.ceil(max(self.initial, float(np.max(self.ceilings))))) + 2.0 * _COP_KNOT_K, _COP_KNOT_K)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`self.lo, float(np.ceil((self.initial))) + 2.0 * _COP_KNOT_K, _COP_KNOT_K)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.e3d37ae9.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.e3d37ae9.json
new file mode 100644
index 0000000000..1bb9441766
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.e3d37ae9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.__init__ CLAMP_DROP e3d37ae9",
+  "killed_by": "tests/features.py",
+  "old": "        self.lo = float(np.floor(min(self.initial, float(np.min(self.floors))))) - _COP_KNOT_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`self.lo = float(np.floor((self.initial))) - _COP_KNOT_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.CMP_BOUND.64eeed1c.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.CMP_BOUND.64eeed1c.json
new file mode 100644
index 0000000000..17874f309e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.CMP_BOUND.64eeed1c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions CMP_BOUND 64eeed1c",
+  "killed_by": "tests/features.py",
+  "old": "        ran, paused = runs.tie_break(bool(self.asked[k] > 0.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ran, paused = runs.tie_break(bool(self.asked[k] >= 0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.RETURN_DEL.43f64127.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.RETURN_DEL.43f64127.json
new file mode 100644
index 0000000000..7e46c9e62b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.RETURN_DEL.43f64127.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions RETURN_DEL 43f64127",
+  "killed_by": "tests/features.py",
+  "old": "        return [*(at(level) for level in self.levels), fill], pauses",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._rise.RETURN_DEL.ad4cb87b.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._rise.RETURN_DEL.ad4cb87b.json
new file mode 100644
index 0000000000..bb38f95872
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._rise.RETURN_DEL.ad4cb87b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._rise RETURN_DEL ad4cb87b",
+  "killed_by": "tests/features.py",
+  "old": "        return heat * self.ctx.dt / self.ctx.c_dhw",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.268a674c.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.268a674c.json
new file mode 100644
index 0000000000..50c58a16d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.268a674c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.accepted GUARD_OFF 268a674c",
+  "killed_by": "tests/features.py",
+  "old": "            if fitted is None or isinstance(fitted, np.ndarray):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.497d643e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.497d643e.json
new file mode 100644
index 0000000000..d9be76b3be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.497d643e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.accepted GUARD_OFF 497d643e",
+  "killed_by": "tests/features.py",
+  "old": "            if fitted[0] != \"start\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.RETURN_DEL.d7923b87.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.RETURN_DEL.d7923b87.json
new file mode 100644
index 0000000000..2c777d9a35
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.RETURN_DEL.d7923b87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.accepted RETURN_DEL d7923b87",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "        return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.BOOLOP.b30ce7fa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.BOOLOP.b30ce7fa.json
new file mode 100644
index 0000000000..9cb8acdc0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.BOOLOP.b30ce7fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan BOOLOP b30ce7fa",
+  "killed_by": "tests/features.py",
+  "old": "                out[k] = self.levels[action[k]] if mask[k] and action[k] < len(self.levels) else float(",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`out[k] = self.levels[action[k]] if mask[k] or action[k] < len(self.levels) else float(`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.CMP_BOUND.b30ce7fa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.CMP_BOUND.b30ce7fa.json
new file mode 100644
index 0000000000..1c7dde9ba5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.CMP_BOUND.b30ce7fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan CMP_BOUND b30ce7fa",
+  "killed_by": "tests/features.py",
+  "old": "                out[k] = self.levels[action[k]] if mask[k] and action[k] < len(self.levels) else float(",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`out[k] = self.levels[action[k]] if mask[k] and action[k] <= len(self.levels) else float(`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.2f0256bb.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.2f0256bb.json
new file mode 100644
index 0000000000..3ae8298cc0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.2f0256bb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan GUARD_OFF 2f0256bb",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.isfinite(cost).any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.6a1d1d58.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.6a1d1d58.json
new file mode 100644
index 0000000000..28dd6926f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.6a1d1d58.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan GUARD_OFF 6a1d1d58",
+  "killed_by": "tests/features.py",
+  "old": "            if mask[k] or action[k]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.RETURN_DEL.7edb83fa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.RETURN_DEL.7edb83fa.json
new file mode 100644
index 0000000000..967df2b040
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.RETURN_DEL.7edb83fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan RETURN_DEL 7edb83fa",
+  "killed_by": "tests/features.py",
+  "old": "        return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.3a89afa4.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.3a89afa4.json
new file mode 100644
index 0000000000..50db5344b1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.3a89afa4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place CMP_BOUND 3a89afa4",
+  "killed_by": "tests/features.py",
+  "old": "                    inside &= t <= self.ceilings[k] - _STORE_MARGIN_K + 1e-9",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`inside &= t < self.ceilings[k] - _STORE_MARGIN_K + 1e-9`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.GUARD_OFF.11ab4ed8.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.GUARD_OFF.11ab4ed8.json
new file mode 100644
index 0000000000..0bc1ea8e53
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.GUARD_OFF.11ab4ed8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place GUARD_OFF 11ab4ed8",
+  "killed_by": "tests/features.py",
+  "old": "                if charged:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.RETURN_DEL.ea9b6ec1.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.RETURN_DEL.ea9b6ec1.json
new file mode 100644
index 0000000000..05b17b52ae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.RETURN_DEL.ea9b6ec1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place RETURN_DEL ea9b6ec1",
+  "killed_by": "tests/features.py",
+  "old": "                return np.clip(j, 0, width - 1), np.where(inside, 0.0, np.inf)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.CMP_BOUND.767963ce.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.CMP_BOUND.767963ce.json
new file mode 100644
index 0000000000..06b51864d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.CMP_BOUND.767963ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal CMP_BOUND 767963ce",
+  "killed_by": "tests/features.py",
+  "old": "    short = np.flatnonzero(temps_of(candidate)[1 : candidate.size + 1] < held - SHORTFALL_K)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`short = np.flatnonzero(temps_of(candidate)[1 : candidate.size + 1] <= held - SHORTFALL_K)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
new file mode 100644
index 0000000000..d942d4aade
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal GUARD_OFF 4763baed",
+  "killed_by": "tests/features.py",
+  "old": "    if start_below is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.c9743976.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.c9743976.json
new file mode 100644
index 0000000000..da0bce1db4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.c9743976.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal GUARD_OFF c9743976",
+  "killed_by": "tests/features.py",
+  "old": "        if lost.size:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.RETURN_DEL.6f93183b.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.RETURN_DEL.6f93183b.json
new file mode 100644
index 0000000000..fa2c65331f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.RETURN_DEL.6f93183b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal RETURN_DEL 6f93183b",
+  "killed_by": "tests/features.py",
+  "old": "    return (\"floor\", int(short[0])) if short.size else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.CMP_BOUND.bbc78afe.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.CMP_BOUND.bbc78afe.json
new file mode 100644
index 0000000000..53382068cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.CMP_BOUND.bbc78afe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charges_run CMP_BOUND bbc78afe",
+  "killed_by": "tests/features.py",
+  "old": "    on, low = plan > 0.0, (plan > 0.0) & (plan < floor - 1e-9)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on, low = plan >= 0.0, (plan > 0.0) & (plan < floor - 1e-9)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.RETURN_DEL.70fe77b1.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.RETURN_DEL.70fe77b1.json
new file mode 100644
index 0000000000..1b16e77bcf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.RETURN_DEL.70fe77b1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charges_run RETURN_DEL 70fe77b1",
+  "killed_by": "tests/features.py",
+  "old": "    return not bool(np.any(low & ~(ends & tails)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.BOOLOP.a48fe321.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.BOOLOP.a48fe321.json
new file mode 100644
index 0000000000..30e60ef683
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.BOOLOP.a48fe321.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges BOOLOP a48fe321",
+  "killed_by": "tests/features.py",
+  "old": "    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not charge.start_cost > 0 or charges_run(plan, floor, not charge.clamped):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.0f54c97d.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.0f54c97d.json
new file mode 100644
index 0000000000..5ab6a6c153
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.0f54c97d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CLAMP_DROP 0f54c97d",
+  "killed_by": "tests/features.py",
+  "old": "    held = np.minimum(limits[0], walk[1:])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`held = (limits[0])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.1e8af2ea.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.1e8af2ea.json
new file mode 100644
index 0000000000..b3710d3bdd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.1e8af2ea.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CLAMP_DROP 1e8af2ea",
+  "killed_by": "tests/features.py",
+  "old": "    program = _StoreProgram(planner, ctx, plan, tank, (held, np.maximum(limits[1], walk[1:])), forced_off, space)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`program = _StoreProgram(planner, ctx, plan, tank, (held, (limits[1])), forced_off, space)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.92461313.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.92461313.json
new file mode 100644
index 0000000000..d0f380f174
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.92461313.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CLAMP_DROP 92461313",
+  "killed_by": "tests/features.py",
+  "old": "    space = np.zeros(ctx.n_steps) if space_demand is None else np.clip(space_demand, 0.0, None)",
+  "reason": "Killed by the check \"a space plan under zero commits as no space plan: ...\" in tests/features.py's R11-OUTSIDE-HONEST-DHW-RUNS block: CLAMP_DROP (`(space_demand)`) lets a space step of -10 kW under the program's dear early charge hide that charge's start, so the early charge ships; features_block.py over the block went from 1 failed (the block-mode baseline) to 2 failed with the mutant, the added failure being that check."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.a48fe321.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.a48fe321.json
new file mode 100644
index 0000000000..8393bcc816
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.a48fe321.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CMP_BOUND a48fe321",
+  "killed_by": "tests/features.py",
+  "old": "    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not charge.start_cost >= 0 and charges_run(plan, floor, not charge.clamped):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.e2cc9d77.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.e2cc9d77.json
new file mode 100644
index 0000000000..8e9e34a0c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.e2cc9d77.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CMP_BOUND e2cc9d77",
+  "killed_by": "tests/features.py",
+  "old": "    if charge is None or ctx.p_dhw_max < floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if charge is None or ctx.p_dhw_max <= floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.a48fe321.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.a48fe321.json
new file mode 100644
index 0000000000..d160762a4f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.a48fe321.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges GUARD_OFF a48fe321",
+  "killed_by": "tests/features.py",
+  "old": "    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.e2cc9d77.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.e2cc9d77.json
new file mode 100644
index 0000000000..c02bd55dec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.e2cc9d77.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges GUARD_OFF e2cc9d77",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if charge is None or ctx.p_dhw_max < floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.RETURN_DEL.6881576e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.RETURN_DEL.6881576e.json
new file mode 100644
index 0000000000..4c6cc3d5b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.RETURN_DEL.6881576e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges RETURN_DEL 6881576e",
+  "killed_by": "tests/features.py",
+  "old": "    return min((c for c in proposed if isinstance(c, np.ndarray)), key=cost, default=plan)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.cost.RETURN_DEL.066c6846.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.cost.RETURN_DEL.066c6846.json
new file mode 100644
index 0000000000..fc5dfc528b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.cost.RETURN_DEL.066c6846.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.cost RETURN_DEL 066c6846",
+  "killed_by": "tests/features.py",
+  "old": "        return float(np.sum(ctx.prices * candidate) * ctx.dt) + charge.start_cost * starts",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.3b32803b.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.3b32803b.json
new file mode 100644
index 0000000000..7272457fc3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.3b32803b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits GUARD_OFF 3b32803b",
+  "killed_by": "tests/features.py",
+  "old": "        if not charges_run(candidate, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.e8d52e79.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.e8d52e79.json
new file mode 100644
index 0000000000..00b0b5d737
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.e8d52e79.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits GUARD_OFF e8d52e79",
+  "killed_by": "tests/features.py",
+  "old": "        if candidate is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.387565ce.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.387565ce.json
new file mode 100644
index 0000000000..bec19e26de
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.387565ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits RETURN_DEL 387565ce",
+  "killed_by": "tests/features.py",
+  "old": "        return charge_refusal(candidate, start_below, temps_of, held) or candidate",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.BOOLOP.6c096d09.json
similarity index 84%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.BOOLOP.6c096d09.json
index ab09d83fe4..3211a8a7a0 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.BOOLOP.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps BOOLOP 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps BOOLOP 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if cycle_step is not None or 0 <= cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.CMP_BOUND.6c096d09.json
similarity index 86%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.CMP_BOUND.6c096d09.json
index d702531e8c..4ffa0b64f0 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.CMP_BOUND.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps CMP_BOUND 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps CMP_BOUND 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if cycle_step is not None and 0 < cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.6c096d09.json
similarity index 82%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.6c096d09.json
index 3a532a0795..dd20b43472 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps GUARD_OFF 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
index a26a52429d..28bd8101ab 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF cccafcc1",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps GUARD_OFF cccafcc1",
   "killed_by": "tests/manual_plan.py",
   "old": "    if everyday is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.RETURN_DEL.87df096e.json
similarity index 79%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.RETURN_DEL.87df096e.json
index 5ed862def7..3edce0523d 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.RETURN_DEL.87df096e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps RETURN_DEL 87df096e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps RETURN_DEL 87df096e",
   "killed_by": "tests/block_duty.py",
   "old": "    return start",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.064a19f6.json
similarity index 83%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.064a19f6.json
index a4e8b3a54d..5b4f6f6c40 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable CMP_BOUND 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if temps_of(plan)[i] > start_below[i]:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.b56fd264.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.b56fd264.json
index 3d43b90b16..a9eeae612b 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.b56fd264.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND b56fd264",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable CMP_BOUND b56fd264",
   "killed_by": "tests/block_duty.py",
   "old": "    on = plan > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = plan >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=8."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.GUARD_OFF.064a19f6.json
similarity index 81%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.GUARD_OFF.064a19f6.json
index f68b057eb8..68a1bf5ab1 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.GUARD_OFF.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable GUARD_OFF 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable GUARD_OFF 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.RETURN_DEL.c913c48e.json
similarity index 79%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.RETURN_DEL.c913c48e.json
index bba12cc624..718843a931 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.RETURN_DEL.c913c48e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable RETURN_DEL c913c48e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable RETURN_DEL c913c48e",
   "killed_by": "tests/block_duty.py",
   "old": "    return plan",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=9."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.99a579b8.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.99a579b8.json
index a9e44056f4..8973d5a037 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:place_startable GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.e4a2bfaa.json
similarity index 81%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.e4a2bfaa.json
index 0c4ceb6b59..43d58de22e 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.e4a2bfaa.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF e4a2bfaa",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:place_startable GUARD_OFF e4a2bfaa",
   "killed_by": "tests/block_duty.py",
   "old": "        if np.array_equal(fixed, plan):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.RETURN_DEL.68208daf.json
similarity index 82%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.RETURN_DEL.68208daf.json
index 9e7ca6a749..a5089f7349 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.RETURN_DEL.68208daf.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable RETURN_DEL 68208daf",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:place_startable RETURN_DEL 68208daf",
   "killed_by": "tests/block_duty.py",
   "old": "    return drop_unstartable(plan, start_below, temps_of)",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=5."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.BOOLOP.3d3ec5bc.json
similarity index 82%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.BOOLOP.3d3ec5bc.json
index 6443097405..e4836e1976 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.BOOLOP.3d3ec5bc.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps BOOLOP 3d3ec5bc",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps BOOLOP 3d3ec5bc",
   "killed_by": "tests/block_duty.py",
   "old": "        under_way = bool(on[i] and ok[i])",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`under_way = bool(on[i] or ok[i])`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.1edfe326.json
similarity index 83%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.1edfe326.json
index f11e540a53..f83ef0622d 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.1edfe326.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 1edfe326",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps CMP_BOUND 1edfe326",
   "killed_by": "tests/block_duty.py",
   "old": "    on = np.asarray(plan, dtype=float) > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = np.asarray(plan, dtype=float) >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.6e3a088f.json
similarity index 86%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.6e3a088f.json
index 94c3474d95..13bd54cc1e 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.6e3a088f.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 6e3a088f",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps CMP_BOUND 6e3a088f",
   "killed_by": "tests/block_duty.py",
   "old": "    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] <= start_below[: on.size]`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.GUARD_OFF.99a579b8.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.GUARD_OFF.99a579b8.json
index 26c5b81261..d4d39effe3 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.RETURN_DEL.82bc35de.json
similarity index 79%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.RETURN_DEL.82bc35de.json
index 1fc93528fd..737d23018a 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.RETURN_DEL.82bc35de.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps RETURN_DEL 82bc35de",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps RETURN_DEL 82bc35de",
   "killed_by": "tests/block_duty.py",
   "old": "    return ok",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=4."
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.CMP_BOUND.2515841c.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.CMP_BOUND.2515841c.json
new file mode 100644
index 0000000000..da25c5c06f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.CMP_BOUND.2515841c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges CMP_BOUND 2515841c",
+  "killed_by": "tests/features.py",
+  "old": "    on, kept = np.r_[False, plan > 0.0, False], mask.copy()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on, kept = np.r_[False, plan >= 0.0, False], mask.copy()`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/arm_refusal.GUARD_OFF.2569c66f.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
similarity index 56%
rename from tests/mutation_ledger/killed_by/sysid.py/arm_refusal.GUARD_OFF.2569c66f.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
index 2b716d8e37..82d3290dba 100644
--- a/tests/mutation_ledger/killed_by/sysid.py/arm_refusal.GUARD_OFF.2569c66f.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:arm_refusal GUARD_OFF 2569c66f",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges GUARD_OFF cbabd675",
   "killed_by": "tests/features.py",
-  "old": "    if not ident.config.enabled:",
+  "old": "    if charge_runs is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.RETURN_DEL.d78a0d21.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.RETURN_DEL.d78a0d21.json
index 2cd18bdda4..1596ff6123 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.RETURN_DEL.d78a0d21.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance RETURN_DEL e82fb19a",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges RETURN_DEL d78a0d21",
   "killed_by": "tests/features.py",
-  "old": "    return new_cost, new_bal, back",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "old": "    return kept",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/dhw_learning.py/DhwProfileLearner.async_learn_dynamics.GUARD_OFF.efe52220.json b/tests/mutation_ledger/killed_by/dhw_learning.py/DhwProfileLearner.async_learn_dynamics.GUARD_OFF.efe52220.json
new file mode 100644
index 0000000000..3c0404c5d6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_learning.py/DhwProfileLearner.async_learn_dynamics.GUARD_OFF.efe52220.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_learning.py:DhwProfileLearner.async_learn_dynamics GUARD_OFF efe52220",
+  "killed_by": "tests/features.py",
+  "old": "        if occupied:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.cedbad00.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.cedbad00.json
deleted file mode 100644
index 6fff52f6b9..0000000000
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.cedbad00.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_shortfall CMP_BOUND cedbad00",
-  "killed_by": "tests/features.py",
-  "old": "        for i in np.where(gaps > 0.05)[0]:",
-  "reason": "Recorded by hand for R9-EG-A2 (#1874) on an export of the branch, 2026-10-03, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS): a kill is a red run naming a FAIL line or traceback the unmutated baseline does not. CMP_BOUND (`for i in np.where(gaps >= 0.05)[0]:`) took tests/features.py from rc=1 failed=2 to rc=1 failed=3, newly failing ['EG-A2 a DHW breach is a shortfall of MORE than 0.05 K: exactly 0.05 is met, 0.06 is the first breach']."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.f38f29c7.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.f38f29c7.json
new file mode 100644
index 0000000000..eec23a8832
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.f38f29c7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_shortfall CMP_BOUND f38f29c7",
+  "killed_by": "tests/features.py",
+  "old": "        for i in np.where(gaps > SHORTFALL_K)[0]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`for i in np.where(gaps >= SHORTFALL_K)[0]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.coast.RETURN_DEL.32c6aaf4.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.coast.RETURN_DEL.32c6aaf4.json
new file mode 100644
index 0000000000..204d8abc3f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.coast.RETURN_DEL.32c6aaf4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_DhwPlanContext.coast RETURN_DEL 32c6aaf4",
+  "killed_by": "tests/block_duty.py",
+  "old": "        return decay * temp - (float(draw_rates[i]) - _exo_at(self.tank_exo_kw, i)) * self.dt / self.c_dhw + gain",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.BOOLOP.58d599ba.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.BOOLOP.58d599ba.json
deleted file mode 100644
index 3d4225c7d7..0000000000
--- a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.BOOLOP.58d599ba.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.from_dict BOOLOP 58d599ba",
-  "killed_by": "tests/features.py",
-  "old": "        if not (np.isfinite(lo) and np.isfinite(hi)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: BOOLOP (`if not (np.isfinite(lo) or np.isfinite(hi)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.GUARD_OFF.58d599ba.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.GUARD_OFF.58d599ba.json
deleted file mode 100644
index 8302dfb391..0000000000
--- a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.GUARD_OFF.58d599ba.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.from_dict GUARD_OFF 58d599ba",
-  "killed_by": "tests/features.py",
-  "old": "        if not (np.isfinite(lo) and np.isfinite(hi)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against b2b6acd64cde652676a568e93c05f021571ebe5e: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.BOOLOP.dc29709b.json
similarity index 92%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.BOOLOP.dc29709b.json
index 704b09b3cd..f05a55d7e0 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.BOOLOP.dc29709b.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold BOOLOP dc29709b",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window BOOLOP dc29709b",
   "killed_by": "tests/features.py",
   "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if experiment_s is not None or draw.takes_ceiling(drawn_kw, command):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.8c264f30.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.8c264f30.json
similarity index 93%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.8c264f30.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.8c264f30.json
index d58eecf874..9b40a866dc 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.8c264f30.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.8c264f30.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF 8c264f30",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF 8c264f30",
   "killed_by": "tests/structure.py",
   "old": "    if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c <= command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):",
   "reason": "Recorded by `mutation_table.py --pin-killed` against d5cd003111277faa3f2abd7fbe6c9157d2e48ed7: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
new file mode 100644
index 0000000000..8271995631
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF d042d302",
+  "killed_by": "tests/features.py",
+  "old": "        if not ceiling_frozen:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.dc29709b.json
similarity index 90%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.dc29709b.json
index 33b15211f0..cb3dc2da4f 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.dc29709b.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF dc29709b",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF dc29709b",
   "killed_by": "tests/structure.py",
   "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.CMP_BOUND.9058b534.json b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.CMP_BOUND.9058b534.json
new file mode 100644
index 0000000000..dfae4b6695
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.CMP_BOUND.9058b534.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:at_running_floor CMP_BOUND 9058b534",
+  "killed_by": "tests/features.py",
+  "old": "    return drawn_kw is not None and floor > 0.0 and drawn_kw <= (1.0 + AGREE_TOLERANCE) * floor",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return drawn_kw is not None and floor >= 0.0 and drawn_kw <= (1.0 + AGREE_TOLERANCE) * floor`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.RETURN_DEL.9058b534.json b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.RETURN_DEL.9058b534.json
new file mode 100644
index 0000000000..e80087f479
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.RETURN_DEL.9058b534.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:at_running_floor RETURN_DEL 9058b534",
+  "killed_by": "tests/features.py",
+  "old": "    return drawn_kw is not None and floor > 0.0 and drawn_kw <= (1.0 + AGREE_TOLERANCE) * floor",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/@module.CONST.ba3007dd.json b/tests/mutation_ledger/killed_by/heat_energy.py/@module.CONST.ba3007dd.json
new file mode 100644
index 0000000000..0ae9bb0b27
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/@module.CONST.ba3007dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:<module> CONST ba3007dd",
+  "killed_by": "tests/features.py",
+  "old": "UNPLANNED_CHARGE_RISE_K = 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`UNPLANNED_CHARGE_RISE_K = 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.GUARD_OFF.c6189501.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.GUARD_OFF.c6189501.json
new file mode 100644
index 0000000000..ef5a2dd80c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.GUARD_OFF.c6189501.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.booked_dhw_share GUARD_OFF c6189501",
+  "killed_by": "tests/features.py",
+  "old": "        if self.unplanned_charge(plan_split):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.RETURN_DEL.c46109ce.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.RETURN_DEL.c46109ce.json
new file mode 100644
index 0000000000..38cd14370c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.RETURN_DEL.c46109ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.booked_dhw_share RETURN_DEL c46109ce",
+  "killed_by": "tests/features.py",
+  "old": "        return dhw_share(self.attribution(plan_split))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.BOOLOP.c90a604e.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.BOOLOP.c90a604e.json
new file mode 100644
index 0000000000..1a8d9bd550
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.BOOLOP.c90a604e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone BOOLOP c90a604e",
+  "killed_by": "tests/features.py",
+  "old": "        return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return a.dhw <= 0.0 < a.space or not self.unplanned_charge(plan_split)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.CMP_BOUND.c90a604e.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.CMP_BOUND.c90a604e.json
new file mode 100644
index 0000000000..efe36edb46
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.CMP_BOUND.c90a604e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone CMP_BOUND c90a604e",
+  "killed_by": "tests/features.py",
+  "old": "        return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return a.dhw < 0.0 < a.space and not self.unplanned_charge(plan_split)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.GUARD_OFF.0f67a887.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.GUARD_OFF.0f67a887.json
new file mode 100644
index 0000000000..a0761738fb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.GUARD_OFF.0f67a887.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone GUARD_OFF 0f67a887",
+  "killed_by": "tests/features.py",
+  "old": "        if plan_split is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.RETURN_DEL.c90a604e.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.RETURN_DEL.c90a604e.json
new file mode 100644
index 0000000000..30c30b8156
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.RETURN_DEL.c90a604e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone RETURN_DEL c90a604e",
+  "killed_by": "tests/features.py",
+  "old": "        return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.settle.GUARD_OFF.ded6790b.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.settle.GUARD_OFF.ded6790b.json
new file mode 100644
index 0000000000..7893ab01df
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.settle.GUARD_OFF.ded6790b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.settle GUARD_OFF ded6790b",
+  "killed_by": "tests/features.py",
+  "old": "        if self._opened:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.unplanned_charge.RETURN_DEL.5fd3d065.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.unplanned_charge.RETURN_DEL.5fd3d065.json
new file mode 100644
index 0000000000..c7171a8e8a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.unplanned_charge.RETURN_DEL.5fd3d065.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.unplanned_charge RETURN_DEL 5fd3d065",
+  "killed_by": "tests/features.py",
+  "old": "        return unplanned_charge(self.attribution(plan_split), rise)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.6ceb3cee.json b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.6ceb3cee.json
new file mode 100644
index 0000000000..24b321b1af
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.6ceb3cee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:unplanned_charge CMP_BOUND 6ceb3cee",
+  "killed_by": "tests/features.py",
+  "old": "        not a.observed and a.dhw <= 0.0 < a.space",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`not a.observed and a.dhw < 0.0 < a.space`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.8c76c4b6.json b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.8c76c4b6.json
new file mode 100644
index 0000000000..92e703c13a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.8c76c4b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:unplanned_charge CMP_BOUND 8c76c4b6",
+  "killed_by": "tests/features.py",
+  "old": "        and tank_rise_k is not None and tank_rise_k > UNPLANNED_CHARGE_RISE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and tank_rise_k is not None and tank_rise_k >= UNPLANNED_CHARGE_RISE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.BOOLOP.5944a80c.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.BOOLOP.5944a80c.json
new file mode 100644
index 0000000000..f8c38b2557
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.BOOLOP.5944a80c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared BOOLOP 5944a80c",
+  "killed_by": "tests/features.py",
+  "old": "    if sample in _ROOM_AIR_KINDS and facts.ventilation:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if sample in _ROOM_AIR_KINDS or facts.ventilation:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=22."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.093742d2.json
similarity index 51%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
rename to tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.093742d2.json
index bd324872f3..5f6b906736 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.093742d2.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF ac9b3721",
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 093742d2",
   "killed_by": "tests/features.py",
-  "old": "        if experiment:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "old": "        if problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=32."
 }
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.131f698a.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.131f698a.json
new file mode 100644
index 0000000000..111b69b737
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.131f698a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 131f698a",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.defrosting:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.20cd6c12.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.20cd6c12.json
new file mode 100644
index 0000000000..0a67368ddd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.20cd6c12.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 20cd6c12",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.boost is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.5944a80c.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.5944a80c.json
new file mode 100644
index 0000000000..1a4ed9554c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.5944a80c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 5944a80c",
+  "killed_by": "tests/structure.py",
+  "old": "    if sample in _ROOM_AIR_KINDS and facts.ventilation:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.8566cb75.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.8566cb75.json
new file mode 100644
index 0000000000..c6bea2d1ef
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.8566cb75.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 8566cb75",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.signals is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.d88e9b76.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.d88e9b76.json
new file mode 100644
index 0000000000..55c438864d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.d88e9b76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF d88e9b76",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.external_heat:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.RETURN_DEL.e3a2add1.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.RETURN_DEL.e3a2add1.json
new file mode 100644
index 0000000000..9e5cf8a325
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.RETURN_DEL.e3a2add1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared RETURN_DEL e3a2add1",
+  "killed_by": "tests/features.py",
+  "old": "    return facts.tail",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/reason.BOOLOP.fe66f904.json b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.BOOLOP.fe66f904.json
new file mode 100644
index 0000000000..ef86a4196c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.BOOLOP.fe66f904.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:reason BOOLOP fe66f904",
+  "killed_by": "tests/features.py",
+  "old": "        (why for why, kinds, raised in _ADDITIVE if sample in kinds and raised(facts, evidence)),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`(why for why, kinds, raised in _ADDITIVE if sample in kinds or raised(facts, evidence)),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.5f2c2f63.json b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.5f2c2f63.json
new file mode 100644
index 0000000000..36092af534
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.5f2c2f63.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:reason GUARD_OFF 5f2c2f63",
+  "killed_by": "tests/features.py",
+  "old": "        if shared is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=66."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.c4d5f7cd.json b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.c4d5f7cd.json
new file mode 100644
index 0000000000..c0d596cbb8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.c4d5f7cd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:reason GUARD_OFF c4d5f7cd",
+  "killed_by": "tests/features.py",
+  "old": "    if sample is not Sample.DELIVERED_RATIO:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=66."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/space_heat.RETURN_DEL.0f2b23c3.json b/tests/mutation_ledger/killed_by/learning_freeze.py/space_heat.RETURN_DEL.0f2b23c3.json
new file mode 100644
index 0000000000..59bd16cc33
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/space_heat.RETURN_DEL.0f2b23c3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:space_heat RETURN_DEL 0f2b23c3",
+  "killed_by": "tests/features.py",
+  "old": "    return Sample.METERED_SPACE_HEAT if metered else Sample.SPACE_HEAT",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.b866fab8.json b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.b866fab8.json
new file mode 100644
index 0000000000..a02b202e72
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.b866fab8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST b866fab8",
+  "killed_by": "tests/features.py",
+  "old": "_COMBI_COMMIT_SLACK_K = 0.05",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_COMBI_COMMIT_SLACK_K = 0.1`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.GUARD_OFF.32c4a23e.json b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.GUARD_OFF.32c4a23e.json
new file mode 100644
index 0000000000..fe0f84b9ef
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.GUARD_OFF.32c4a23e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_charge_runs GUARD_OFF 32c4a23e",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if not _engaged(opt):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.RETURN_DEL.616b7fba.json b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.RETURN_DEL.616b7fba.json
new file mode 100644
index 0000000000..099827091d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.RETURN_DEL.616b7fba.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_charge_runs RETURN_DEL 616b7fba",
+  "killed_by": "tests/features.py",
+  "old": "    return ChargeRuns(opt.config.start_price, running, opt.config.clamp_planned_levels)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.CMP_BOUND.a94c3e31.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.CMP_BOUND.a94c3e31.json
new file mode 100644
index 0000000000..e361bb405f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.CMP_BOUND.a94c3e31.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange CMP_BOUND a94c3e31",
+  "killed_by": "tests/features.py",
+  "old": "    kept = short(committed, net_under(committed, space_net)) <= short(dhw_power, space_net) + _COMBI_COMMIT_SLACK_K",
+  "reason": "Killed by the check \"combi: the committed build ships where its store falls exactly the slack further under the requirement ...\" in tests/features.py's R11-OUTSIDE-HONEST-DHW-RUNS block, which sets the slack to the float that makes the two sides equal: CMP_BOUND (`<`) ships the last round's plan there; features_block.py over the block went from 1 failed (the block-mode baseline) to 2 failed with the mutant, the added failure being that check."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.5afe5330.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.5afe5330.json
index a532a51c97..a4c946d049 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.5afe5330.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF ba727eb5",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF 5afe5330",
   "killed_by": "tests/features.py",
-  "old": "        if np.allclose(plan.schedule, dhw_power, atol=1e-4):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "        if np.allclose(plan, dhw_power, atol=1e-4):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.aab41faf.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.aab41faf.json
new file mode 100644
index 0000000000..f5430f3414
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.aab41faf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF aab41faf",
+  "killed_by": "tests/features.py",
+  "old": "    if planner.charge_runs is None or space_net is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.e8792dae.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.e8792dae.json
index f1bc862fd8..316ba86b88 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.e8792dae.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received RETURN_DEL d631f182",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange RETURN_DEL e8792dae",
   "killed_by": "tests/features.py",
-  "old": "    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))",
+  "old": "    return committed if kept else dhw_power",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.build.RETURN_DEL.ea9b6925.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.build.RETURN_DEL.ea9b6925.json
new file mode 100644
index 0000000000..70a284bfe3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.build.RETURN_DEL.ea9b6925.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange.build RETURN_DEL ea9b6925",
+  "killed_by": "tests/features.py",
+  "old": "        return np.asarray(plan.schedule)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.net_under.RETURN_DEL.17cf83f0.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.net_under.RETURN_DEL.17cf83f0.json
new file mode 100644
index 0000000000..d574577d9c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.net_under.RETURN_DEL.17cf83f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange.net_under RETURN_DEL 17cf83f0",
+  "killed_by": "tests/structure.py",
+  "old": "        return combi_space_net_kw(store, buffer_temps, dhw_exo, h.dt)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.short.RETURN_DEL.0581556e.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.short.RETURN_DEL.0581556e.json
index b2cba62747..0fab3edeaf 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.short.RETURN_DEL.0581556e.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange RETURN_DEL d235e41f",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange.short RETURN_DEL 0581556e",
   "killed_by": "tests/features.py",
-  "old": "    return dhw_power",
+  "old": "        return float(np.max(gaps))",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.BOOLOP.78de307e.json b/tests/mutation_ledger/killed_by/room_history.py/_accumulate.BOOLOP.78de307e.json
deleted file mode 100644
index 5ee0e8a4ee..0000000000
--- a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.BOOLOP.78de307e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/room_history.py:_accumulate BOOLOP 78de307e",
-  "killed_by": "tests/features.py",
-  "old": "    period.space += house.space_kw > 0.0 and house.dhw_kw <= 0.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`period.space += house.space_kw > 0.0 or house.dhw_kw <= 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.CMP_BOUND.78de307e.json b/tests/mutation_ledger/killed_by/room_history.py/_accumulate.CMP_BOUND.78de307e.json
deleted file mode 100644
index ee712e0cae..0000000000
--- a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.CMP_BOUND.78de307e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/room_history.py:_accumulate CMP_BOUND 78de307e",
-  "killed_by": "tests/features.py",
-  "old": "    period.space += house.space_kw > 0.0 and house.dhw_kw <= 0.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`period.space += house.space_kw >= 0.0 and house.dhw_kw <= 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
deleted file mode 100644
index a0591e68f6..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP faf454fb",
-  "killed_by": "tests/features.py",
-  "old": "        j = np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`j = (np.rint(b / quantum).astype(np.int64) + half)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
deleted file mode 100644
index 4c13f622b6..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CMP_BOUND a2abb9b6",
-  "killed_by": "tests/features.py",
-  "old": "        change, paid = step[0] if dest < min_on else step[1]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`change, paid = step[0] if dest <= min_on else step[1]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_shift.RETURN_DEL.f8e0538e.json b/tests/mutation_ledger/killed_by/runs.py/_shift.RETURN_DEL.f8e0538e.json
new file mode 100644
index 0000000000..d7f5bf2912
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_shift.RETURN_DEL.f8e0538e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_shift RETURN_DEL f8e0538e",
+  "killed_by": "tests/features.py",
+  "old": "    return lambda bal, _ran: (bal + change, paid)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.25623db3.json b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.25623db3.json
new file mode 100644
index 0000000000..5075a44941
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.25623db3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance CMP_BOUND 25623db3",
+  "killed_by": "tests/features.py",
+  "old": "            for a, act in enumerate(actions[0] if dest < min_on else actions[1])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`for a, act in enumerate(actions[0] if dest <= min_on else actions[1])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=29."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.3909ec94.json b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.3909ec94.json
new file mode 100644
index 0000000000..597b9dd615
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.3909ec94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance CMP_BOUND 3909ec94",
+  "killed_by": "tests/features.py",
+  "old": "        j, extra = place(b, dest < min_on)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`j, extra = place(b, dest <= min_on)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.f2948235.json b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.f2948235.json
new file mode 100644
index 0000000000..3181b63d30
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.f2948235.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance CMP_BOUND f2948235",
+  "killed_by": "tests/features.py",
+  "old": "            (s, starts, a, *act(val[s], s < min_on))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`(s, starts, a, *act(val[s], s <= min_on))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json b/tests/mutation_ledger/killed_by/runs.py/advance.GUARD_OFF.329931dd.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
rename to tests/mutation_ledger/killed_by/runs.py/advance.GUARD_OFF.329931dd.json
index c82853e3a0..22d6e7bca2 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.GUARD_OFF.329931dd.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance GUARD_OFF 329931dd",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance GUARD_OFF 329931dd",
   "killed_by": "tests/features.py",
   "old": "        if not ok.any():",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.RETURN_DEL.a247a21c.json b/tests/mutation_ledger/killed_by/runs.py/advance.RETURN_DEL.a247a21c.json
new file mode 100644
index 0000000000..7bff27325f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.RETURN_DEL.a247a21c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance RETURN_DEL a247a21c",
+  "killed_by": "tests/features.py",
+  "old": "    return new_cost, new_val, back",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
deleted file mode 100644
index 556f4a03bc..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 056c259e",
-  "killed_by": "tests/features.py",
-  "old": "        asked = bool(q[k] > 0.0)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`asked = bool(q[k] >= 0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.b415c985.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.b415c985.json
new file mode 100644
index 0000000000..54ef30a5a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.b415c985.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND b415c985",
+  "killed_by": "tests/features.py",
+  "old": "        ran, paused = tie_break(bool(q[k] > 0.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ran, paused = tie_break(bool(q[k] >= 0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
deleted file mode 100644
index 4bc0e47f2f..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND d914b133",
-  "killed_by": "tests/features.py",
-  "old": "        mask[k] = u < min_on",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`mask[k] = u <= min_on`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.3103be9a.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
rename to tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.3103be9a.json
index 82e9874454..e672ff4105 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.3103be9a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP 3103be9a",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit.cells CLAMP_DROP 3103be9a",
   "killed_by": "tests/features.py",
   "old": "        outside = np.maximum(np.abs(b) - half * quantum, 0.0)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`outside = (np.abs(b) - half * quantum)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`outside = (np.abs(b) - half * quantum)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.c77a9bdd.json b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.c77a9bdd.json
new file mode 100644
index 0000000000..c3ee0b1fd7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.c77a9bdd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit.cells CLAMP_DROP c77a9bdd",
+  "killed_by": "tests/features.py",
+  "old": "        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), fine * outside",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (np.rint(b / quantum).astype(np.int64) + half), fine * outside`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.cells.RETURN_DEL.c77a9bdd.json b/tests/mutation_ledger/killed_by/runs.py/commit.cells.RETURN_DEL.c77a9bdd.json
new file mode 100644
index 0000000000..f2395cde90
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.cells.RETURN_DEL.c77a9bdd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit.cells RETURN_DEL c77a9bdd",
+  "killed_by": "tests/features.py",
+  "old": "        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), fine * outside",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/read_back.CMP_BOUND.50ea6816.json b/tests/mutation_ledger/killed_by/runs.py/read_back.CMP_BOUND.50ea6816.json
new file mode 100644
index 0000000000..40ad80db11
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/read_back.CMP_BOUND.50ea6816.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:read_back CMP_BOUND 50ea6816",
+  "killed_by": "tests/features.py",
+  "old": "        mask[k], action[k] = u < min_on, trail[k][2, u, j]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`mask[k], action[k] = u <= min_on, trail[k][2, u, j]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=30."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/read_back.RETURN_DEL.3f4a837c.json b/tests/mutation_ledger/killed_by/runs.py/read_back.RETURN_DEL.3f4a837c.json
new file mode 100644
index 0000000000..d686774334
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/read_back.RETURN_DEL.3f4a837c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:read_back RETURN_DEL 3f4a837c",
+  "killed_by": "tests/features.py",
+  "old": "    return mask, action",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.89e6a09b.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.89e6a09b.json
index 65d574631c..8a1ace9abd 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.89e6a09b.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP 89e6a09b",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves CLAMP_DROP 89e6a09b",
   "killed_by": "tests/features.py",
   "old": "        out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on, states)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on, states)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.b33258f0.json
similarity index 62%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.b33258f0.json
index 84a00e6ada..056c5dabf1 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.b33258f0.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP b33258f0",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves CLAMP_DROP b33258f0",
   "killed_by": "tests/features.py",
   "old": "        out += [(i, min(i + 1, last_on), False) for i in range(min_on)]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=22."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.853776b6.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.853776b6.json
index 520a00450d..68f8418bc0 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.853776b6.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF 853776b6",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves GUARD_OFF 853776b6",
   "killed_by": "tests/features.py",
   "old": "    if not want == 0.0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=39."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.8742274c.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.8742274c.json
new file mode 100644
index 0000000000..c5ecc37c61
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.8742274c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves GUARD_OFF 8742274c",
+  "killed_by": "tests/features.py",
+  "old": "        if may_start or not free:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=37."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.edbdf8a8.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.edbdf8a8.json
index 83e3505d83..0a02059388 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.edbdf8a8.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF edbdf8a8",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves GUARD_OFF edbdf8a8",
   "killed_by": "tests/features.py",
   "old": "    if not want == 1.0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=32."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.RETURN_DEL.a8227ccf.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.RETURN_DEL.a8227ccf.json
index 7fec4cdf5a..46c67baa2a 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.RETURN_DEL.a8227ccf.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves RETURN_DEL a8227ccf",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves RETURN_DEL a8227ccf",
   "killed_by": "tests/features.py",
   "old": "    return out",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/tie_break.RETURN_DEL.1cc6ddc1.json b/tests/mutation_ledger/killed_by/runs.py/tie_break.RETURN_DEL.1cc6ddc1.json
new file mode 100644
index 0000000000..d2cd574c1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/tie_break.RETURN_DEL.1cc6ddc1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:tie_break RETURN_DEL 1cc6ddc1",
+  "killed_by": "tests/features.py",
+  "old": "    return _TIE_BREAK * (not asked), _TIE_BREAK * asked",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.1be5d9b5.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.1be5d9b5.json
deleted file mode 100644
index 7a36937c2f..0000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.1be5d9b5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF 1be5d9b5",
-  "killed_by": "tests/features.py",
-  "old": "        if not self.config.enabled:",
-  "reason": "Recorded by `mutation_table.py --drain` against 1005e27a6fe2b60ded9fa530e03513c5c35c4ead: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.9912aac4.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.9912aac4.json
new file mode 100644
index 0000000000..3780744aec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.9912aac4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF 9912aac4",
+  "killed_by": "tests/features.py",
+  "old": "        if not enabled:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_fdjac.CLAMP_DROP.bcd1af89.json b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.CLAMP_DROP.bcd1af89.json
new file mode 100644
index 0000000000..0d8c1c6a3f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.CLAMP_DROP.bcd1af89.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:_fdjac CLAMP_DROP bcd1af89",
+  "killed_by": "tests/features.py",
+  "old": "        step = 1e-6 * max(abs(float(x[i])), 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`step = 1e-6 * (abs(float(x[i])))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_fdjac.RETURN_DEL.fb4c1dd0.json b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.RETURN_DEL.fb4c1dd0.json
new file mode 100644
index 0000000000..a7f1e9dca5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.RETURN_DEL.fb4c1dd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:_fdjac RETURN_DEL fb4c1dd0",
+  "killed_by": "tests/features.py",
+  "old": "    return jac",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_lm_solve.CLAMP_DROP.6f2a10e7.json b/tests/mutation_ledger/killed_by/sysid.py/_lm_solve.CLAMP_DROP.6f2a10e7.json
deleted file mode 100644
index 16afff8992..0000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/_lm_solve.CLAMP_DROP.6f2a10e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:_lm_solve CLAMP_DROP 6f2a10e7",
-  "killed_by": "tests/features.py",
-  "old": "            step = 1e-6 * max(abs(float(x[i])), 1.0)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`step = 1e-6 * (abs(float(x[i])))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.be0146fa.json b/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.be0146fa.json
new file mode 100644
index 0000000000..296f89d389
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.be0146fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:_ridged.residual RETURN_DEL be0146fa",
+  "killed_by": "tests/features.py",
+  "old": "        return np.append(e, (float(x[2]) - prior_g) / width_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.bec8ba9e.json b/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.bec8ba9e.json
deleted file mode 100644
index b234efb8fd..0000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.bec8ba9e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:_ridged.residual RETURN_DEL bec8ba9e",
-  "killed_by": "tests/features.py",
-  "old": "        return np.append(e, (float(x[2]) - prior_g) / SLAB_INTERCEPT_PRIOR_SD_KW)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5003d56f9d9f7617d5e4dc1372e49dbdbacd39bd: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.d335b51b.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.d335b51b.json
new file mode 100644
index 0000000000..dfdbd135d3
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.d335b51b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions.fill CMP_BOUND d335b51b",
+  "old": "            fills = fills & (under & (level >= ctx.min_run_power) & ran_before if tail else ~under)",
+  "reason": "Equivalent on every float input (CMP_BOUND, the tail's `level >= ctx.min_run_power` -> `>`): the two differ only where the fill's level equals the minimum run power exactly, and no input reaches that float. Measured on the block's rig (`_hdr_rig(t0=50.0, draws=0.5)`, min_run_power 0.6 kW): bisecting step 0's ceiling to two adjacent floats (50.894160773134445 and the next) gives levels 0.5999999999999979 and 0.6000000000000008, either side of 0.6 and some 26 ulps of it apart, so the level steps over the bound and the tie is never computed. Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.f5054d73.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.f5054d73.json
new file mode 100644
index 0000000000..c380450e78
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.f5054d73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions.fill CMP_BOUND f5054d73",
+  "old": "            under = level < floor - 1e-9",
+  "reason": "Equivalent on every float input (CMP_BOUND, `level < floor - 1e-9` -> `<=`): the two differ only where the fill's level, `_StoreProgram._to_ceiling`'s `power_for_heat_per_cop_kw` of a share of the run power's heat, equals `floor - 1e-9` exactly, and no input reaches that float. Measured on the block's own rig (`_hdr_rig()`, a 50 degC tank, floor 1.0 kW): bisecting the step's ceiling to two adjacent floats (52.43492312513295 and the next) gives levels 0.9999999989999981 and 0.9999999990000011, either side of 0.999999999 and some 27 ulps apart, so the level steps over the bound and the tie is never computed; the 1e-9 itself is the tolerance that keeps a level a rounding under the floor from reading as a tail. Survived the pin drive's shard 1 (tests/mutation_table.py --pin-killed --scripts tests/features.py --shard 1/4) and features_block.py over the R11-OUTSIDE-HONEST-DHW-RUNS block with the mutant applied (no added failure).",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._to_ceiling.CMP_BOUND.83613a48.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._to_ceiling.CMP_BOUND.83613a48.json
new file mode 100644
index 0000000000..326ba6ff80
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._to_ceiling.CMP_BOUND.83613a48.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._to_ceiling CMP_BOUND 83613a48",
+  "old": "        fills = (share > 0.0) & (share < 1.0)",
+  "reason": "Both mutants of the line are equivalent. `share > 0.0` -> `>=` adds only share == 0.0, a tank whose coast lands exactly on the ceiling less the margin: the fill's level is then `power_for_heat_per_cop_kw` of no heat, 0.0 kW, which the run's fill refuses (`under`, 0.0 < floor - 1e-9) and the tail refuses (`level >= ctx.min_run_power`, every caller's minimum run power above 0), so the action is the idle coast either way. `share < 1.0` -> `<=` adds only share == 1.0, which no float input reaches: on the block's rig (`_hdr_rig(t0=50.0, draws=0.5)`, step 0, run power 4.8 kW) bisecting step 0's ceiling to two adjacent floats gives shares 0.9999999999999996 and 1.0000000000000002, so the quotient steps over 1.0, and where it would land the fill's level is the run power the `at(4.8)` action already takes to the same temperature. Measured with the share == 0 tie constructed exactly (room 0.0: level 0.0, fills False). Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CLAMP_DROP.ea9b6ec1.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CLAMP_DROP.ea9b6ec1.json
new file mode 100644
index 0000000000..a4367369ba
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CLAMP_DROP.ea9b6ec1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place CLAMP_DROP ea9b6ec1",
+  "old": "                return np.clip(j, 0, width - 1), np.where(inside, 0.0, np.inf)",
+  "reason": "Equivalent on every input (CLAMP_DROP, `np.clip(j, 0, width - 1)` -> `(j)`): a cell index the clip would move lies outside [0, width - 1], where `inside` (which requires `j >= 0` and `j < width`) is False, so the same arrival's extra cost is inf; runs.advance drops every arrival whose cost is not finite (`ok = np.isfinite(c)`, then `j = j[ok]`) before it indexes a cell with j, so no clipped index is ever read. Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.0637f071.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.0637f071.json
new file mode 100644
index 0000000000..f247193949
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.0637f071.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place CMP_BOUND 0637f071",
+  "old": "                inside = (t >= self.floors[k] - SHORTFALL_K + _STORE_MARGIN_K) & (j >= 0) & (j < width)",
+  "reason": "The line carries three CMP_BOUND mutants under one anchor, and the ledger pins an anchor killed only when every mutant is. Two are killed by tests/features.py's R11-OUTSIDE-HONEST-DHW-RUNS block: `t > ...` by the check \"the store program keeps a store that coasts exactly onto its floor bound ...\", and `j <= width` by \"the store program's grid ends at its top knot ...\" (features_block.py over the block: 1 failed at the block-mode baseline, 2 with each mutant). The third, `j >= 0` -> `j > 0`, is equivalent: `_StoreProgram.__init__` sets `lo = floor(min(initial, min(floors))) - _COP_KNOT_K`, so wherever the first conjunct holds, t >= floors[k] - 0.05 + 0.02 >= lo + 0.97 and j = rint((t - lo) / 0.25) >= 4; j == 0 arrives only where the first conjunct is already false, and `np.clip(j, 0, width - 1)` is untouched by the mutant. That mutant ran the block with no added failure.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/commit_charges.CMP_BOUND.a8e7dc9b.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/commit_charges.CMP_BOUND.a8e7dc9b.json
new file mode 100644
index 0000000000..40cdbed8b6
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/commit_charges.CMP_BOUND.a8e7dc9b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CMP_BOUND a8e7dc9b",
+  "old": "        fits(np.where((plan > 0.0) & (plan < floor), floor, plan)),",
+  "reason": "The line carries two CMP_BOUND mutants under one anchor. `plan > 0.0` -> `>=` is killed by tests/features.py (it lifts every idle step to the floor). `plan < floor` -> `<=` is equivalent on every input: it adds only steps where plan == floor, and `np.where(mask, floor, plan)` writes floor there, the value the step already holds, so the lifted plan is the same array. Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/draw_range.py/fold.CMP_BOUND.8c264f30.json b/tests/mutation_ledger/survivor_triage/draw_range.py/_fold_window.CMP_BOUND.8c264f30.json
similarity index 97%
rename from tests/mutation_ledger/survivor_triage/draw_range.py/fold.CMP_BOUND.8c264f30.json
rename to tests/mutation_ledger/survivor_triage/draw_range.py/_fold_window.CMP_BOUND.8c264f30.json
index 9ef48a1684..cbe002a3b8 100644
--- a/tests/mutation_ledger/survivor_triage/draw_range.py/fold.CMP_BOUND.8c264f30.json
+++ b/tests/mutation_ledger/survivor_triage/draw_range.py/_fold_window.CMP_BOUND.8c264f30.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold CMP_BOUND 8c264f30",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window CMP_BOUND 8c264f30",
   "old": "    if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c <= command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):",
   "reason": "R10 mutation-anchor: the `killed_by: tests/entities.py` pin was vacuous. Re-driven at 0be5e2de5 by dev/audit/harnesses/r10_anchor_vacuous.py with the 2 ledger row(s) the mutant itself makes stale hidden from its tree, 0 of 1 site(s) were killed by tests/entities.py: the recorded kill was a check refusing a ledger row the mutant made stale (the --anchor self-test, or the survivor_triage staleness check), not one that saw the mutation. Was: Recorded by `mutation_table.py --pin-killed` against 52011c69ae04f8a725c82040669b7c158290f834: CMP_BOUND (`if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c < command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Not re-driven here against the other drivers in its closure, so a gap until one is shown to kill it.",
   "verdict": "gap"
diff --git a/tests/mutation_ledger/survivor_triage/sysid.py/_slab_ua_profile_halfwidth.CLAMP_DROP.dffcdea0.json b/tests/mutation_ledger/survivor_triage/sysid.py/_slab_ua_profile_halfwidth.CLAMP_DROP.dffcdea0.json
deleted file mode 100644
index 02f18b9a81..0000000000
--- a/tests/mutation_ledger/survivor_triage/sysid.py/_slab_ua_profile_halfwidth.CLAMP_DROP.dffcdea0.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:_slab_ua_profile_halfwidth CLAMP_DROP dffcdea0",
-  "old": "        step = 1e-6 * max(abs(float(x_hat[i])), 1.0)",
-  "reason": "arrived with origin/main, commit 96374e62 (\"gate sysid adoption on the fitted UA's profile-likelihood interval\", #1410/#1437); a real gap: dropping `max(..., 1.0)` shrinks the finite-difference step to `1e-6 * |x_hat[i]|` for any `|x_hat[i]| < 1` (a fitted G below 1), which moves the Jacobian and the published interval in its low digits -- inside the driver's margin to the bar, which reads a comparison and never the number. An assertion on the half-width's value would pin it. Survival measured UNMARKED at 467d3d9c on 2026-09-23: no driver in the recorded net (13 drivers) detects the mutant behaviourally. The one driver that reddens it is tests/entities.py's #1217 mark-staleness self-check, which fires solely because THIS entry exists -- a property of the record, not of the mutant, and one it shares with the instrument's own D3-07 `equivalent` marks (pump_mode.py:242, __init__.py:340), which redden identically. It is not a behavioural kill and is not recorded under `killed_by`: moving the mark there removes the mechanism (measured -- entities.py rc=0, ALL 1707 pass).",
-  "verdict": "gap"
-}


## Review scope: full (no verdict on verdict/<pr> names the reviewed head 46cdd1f9191180fc1f420a0d5eedd0f758b947ad, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/accuracy.py b/custom_components/heatpump_optimizer/accuracy.py
index 16aadfa116..36c0d00238 100644
--- a/custom_components/heatpump_optimizer/accuracy.py
+++ b/custom_components/heatpump_optimizer/accuracy.py
@@ -1282,7 +1282,7 @@ class MeasuredCop:
     @staticmethod
     def judge_floor(
         asked_kw: float, drawn_kw: float | None, params: Any, draw: DrawRange | None = None,
-        experiment: bool = False,
+        experiment: bool = False, approach: bool = False,
     ) -> str | None:
         """The first judgement every interval meets, or None.
 
@@ -1290,7 +1290,9 @@ class MeasuredCop:
         ceiling probe; the action that governed it was the
         system-identification override, the action ``asked_kw`` is read from):
         an experiment's ask is not the plan's, so drawn over asked is no
-        efficiency reading. Where heat is metered the COP is heat over the
+        efficiency reading. The same holds inside a run's learned ``approach``
+        (``draw_range.expect``): the pump draws above its ask by its own
+        wind-down. Where heat is metered the COP is heat over the
         draw, and the reason is the scale's. It is one scalar on a law of lift
         alone, learned where the plan runs the compressor. An experiment
         drives it to its band ends, where an inverter's efficiency departs from
@@ -1300,7 +1302,7 @@ class MeasuredCop:
         ``drawn_kw`` ``None``: no per-cycle draw (a heat counter's install),
         judged on the experiment alone, so its span fails the cycle's gate.
         """
-        if experiment:
+        if experiment or approach:
             return COP_REFUSED_OFF_ASK
         if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw(draw, params):
             return COP_REFUSED_DUTY_FLOOR
diff --git a/custom_components/heatpump_optimizer/approach.py b/custom_components/heatpump_optimizer/approach.py
new file mode 100644
index 0000000000..e53622a514
--- /dev/null
+++ b/custom_components/heatpump_optimizer/approach.py
@@ -0,0 +1,228 @@
+"""What the pump draws in a space run's first steps, and in a pause's first.
+
+The finding and its series are Bankaifan's (comment 6944433306 on pull
+request 3670). An on/off install holds its running floor, but a space run
+entered from a higher compressor state (off, or a hot-water charge) draws well
+above the floor for most of an hour before it settles there. Once the gate is
+written, the compressor winds down for minutes while the plan books the step
+as off. The plan booked the floor; the meter read more.
+
+:class:`ApproachProfile` keeps that evidence. Per age bin since a
+**space-run entry** (a step with a space level after one with none) it keeps
+the draw while the space ask sat at the floor in force. Per age bin since a
+space run's end it keeps the draw while nothing was asked. It keeps the live
+run's age too. :func:`entry_levels`
+and :func:`ramp_levels` read it as levels by bin, which ``runs.received``
+reads as the draw a plan's run takes. Nothing here books a fee: the heat the
+excess buys is delivered, so the plan reads it as received draw.
+
+A leaf: numpy and the plan's running rule, no Home Assistant.
+"""
+from __future__ import annotations
+
+from collections import deque
+from dataclasses import dataclass, field
+from typing import Any, Deque
+
+import numpy as np
+
+from .const import finite_float
+from .thermal_model import planned_draw_runs
+
+#: Age bin width, minutes. This, :data:`BINS`, :data:`RAMP_BINS`,
+#: :data:`DEPTH` and :data:`MIN_COUNT` are constants from one install's series
+#: (Bankaifan's series D and H), not measured thresholds.
+BIN_MIN = 5.0
+#: The longest age the entry profile keeps, in bins (2 h): series D settles
+#: at the floor after 50 to 60 minutes.
+BINS = 24
+#: The longest age the ramp-down profile keeps, in bins: series H's wind-down
+#: lasted 330 s.
+RAMP_BINS = 3
+#: Samples kept per bin; a bin's level is their median.
+DEPTH = 9
+#: Samples a bin needs before it reads as a level.
+MIN_COUNT = 3
+#: Float slack on an age read into a bin, in bins.
+_SLACK = 1e-9
+
+
+def _bins(n: int) -> list[Deque[float]]:
+    return [deque(maxlen=DEPTH) for _ in range(n)]
+
+
+@dataclass
+class ApproachProfile:
+    """Draw by age since a space-run entry and since a space run's end."""
+
+    #: Metered draw per :data:`BIN_MIN` bin after an entry, oldest first.
+    entry: list[Deque[float]] = field(default_factory=lambda: _bins(BINS))
+    #: Metered draw per bin after a space run's end while nothing was asked.
+    ramp: list[Deque[float]] = field(default_factory=lambda: _bins(RAMP_BINS))
+    #: Epoch seconds the live space run was entered, or ``None``: unknown, or
+    #: no space run live (``running`` says which).
+    entered_s: float | None = None
+    #: Epoch seconds the last space run ended, or ``None``.
+    ended_s: float | None = None
+    #: Whether the last folded interval asked a space level; ``None`` unknown.
+    running: bool | None = None
+    #: The configured ``(min, max)`` the evidence belongs to.
+    config: tuple[float, float] | None = None
+    #: Epoch seconds the last folded interval ended, or ``None``.
+    seen_s: float | None = None
+    #: The draw expected of the interval in hand where it sits inside the
+    #: profile, kW (``draw_range.expect``); not stored: a restart pairs none.
+    expected_kw: float | None = None
+
+    def observe(
+        self, drawn_kw: float | None, split: tuple[float, float], floor_kw: float,
+        start_s: float, end_s: float, *, sample: bool, standby_kw: float,
+        tolerance: float, config: tuple[float, float],
+    ) -> str | None:
+        """Fold one interval ``[start_s, end_s)`` and move the run's clock:
+        ``"ramp"`` for a wind-down sample, ``"inside"`` for an entry sample at
+        an age the profile still covers, else ``None``.
+
+        ``sample`` is ``draw_range.is_running_space`` for a space interval
+        and the learners' gates (not frozen, not distorted, no defrost) for
+        one asking nothing. An entry sample is a running space interval whose
+        ask sits at or under ``floor_kw`` by ``tolerance``: a higher ask draws
+        more by asking more. A ramp-down sample is the first interval after
+        a space run, asking nothing, metered above ``standby_kw``. A changed
+        ``config`` drops the evidence, as ``DrawRange.observe`` drops its own.
+        A gap since the last interval longer than this one (a restart, a
+        stall) leaves the run's state unknown: no entry is read across it.
+        """
+        if self.config != config:
+            self.entry, self.ramp, self.config = _bins(BINS), _bins(RAMP_BINS), config
+        runs, was = self._clock(split[0], start_s, end_s)
+        if drawn_kw is None or not sample:
+            return None
+        if runs and self.entered_s is not None and split[0] <= (1.0 + tolerance) * floor_kw:
+            age_min = (start_s - self.entered_s) / 60.0
+            _put(self.entry, age_min, drawn_kw)
+            return "inside" if age_min < _levels(self.entry, floor_kw, tolerance).size * BIN_MIN else None
+        quiet = not runs and not planned_draw_runs(split[1], modulation_floor=0.0)
+        if quiet and was and drawn_kw > standby_kw and self.ended_s is not None:
+            _put(self.ramp, (start_s - self.ended_s) / 60.0, drawn_kw)
+            return "ramp"
+        return None
+
+    def _clock(self, space_kw: float, start_s: float, end_s: float) -> tuple[bool, bool | None]:
+        """Move the run's clock by one interval: whether it asks a space
+        level, and whether the one before did (``None`` across a gap)."""
+        runs = planned_draw_runs(space_kw, modulation_floor=0.0)
+        gap = self.seen_s is None or start_s - self.seen_s > end_s - start_s
+        was = None if gap else self.running
+        self.seen_s, self.running = end_s, runs
+        if runs and was is False:
+            self.entered_s = start_s
+        elif not runs and was:
+            self.ended_s, self.entered_s = start_s, None
+        elif gap or not runs:
+            self.entered_s = None
+        return runs, was
+
+    def expect(self, total_kw: float, *, inside: bool) -> float:
+        """Keep the draw expected of the interval in hand where it sits
+        inside the profile (``expected_kw``); ``total_kw`` back."""
+        self.expected_kw = total_kw if inside else None
+        return total_kw
+
+    def age_h(self, now_s: float) -> float | None:
+        """The live space run's age, hours: ``0.0`` with none live (a step
+        that runs space next is an entry), ``None`` where unknown, which books
+        no entry and reads as no profile."""
+        if self.running is False:
+            return 0.0
+        if self.running is None or self.entered_s is None or now_s < self.entered_s:
+            return None
+        return (now_s - self.entered_s) / 3600.0
+
+    def as_dict(self) -> dict[str, Any]:
+        return {
+            "entry": [[round(v, 3) for v in b] for b in self.entry],
+            "ramp": [[round(v, 3) for v in b] for b in self.ramp],
+            **({} if self.config is None else {"config": list(self.config)}),
+            **({} if self.entered_s is None else {"entered_s": self.entered_s}),
+            **({} if self.ended_s is None else {"ended_s": self.ended_s}),
+            **({} if self.running is None else {"running": self.running}),
+            **({} if self.seen_s is None else {"seen_s": self.seen_s}),
+        }
+
+    @classmethod
+    def of_record(cls, draw: Any) -> "ApproachProfile":
+        """The profile a stored ``DrawRange`` record carries, if any."""
+        return cls.from_dict(draw.get("approach") if isinstance(draw, dict) else None)
+
+    @classmethod
+    def from_dict(cls, data: Any) -> "ApproachProfile":
+        """A stored profile; a bad cell costs that cell, a bad key its field."""
+        out = cls()
+        out.config = stored_config(data)
+        if out.config is None:
+            return out
+        out.entry = _stored_bins(data.get("entry"), BINS)
+        out.ramp = _stored_bins(data.get("ramp"), RAMP_BINS)
+        out.entered_s = finite_float(data.get("entered_s"))
+        out.ended_s = finite_float(data.get("ended_s"))
+        out.seen_s = finite_float(data.get("seen_s"))
+        running = data.get("running")
+        out.running = running if isinstance(running, bool) else None
+        if out.running and out.entered_s is None:
+            out.running = None
+        return out
+
+
+def stored_config(data: Any) -> tuple[float, float] | None:
+    """A stored record's configured ``(min, max)`` key, or ``None`` where
+    unreadable or not finite: the evidence it keys is dropped with it."""
+    try:
+        lo, hi = (finite_float(v) for v in data["config"])
+    except (TypeError, ValueError, KeyError, IndexError):
+        return None
+    return None if lo is None or hi is None else (lo, hi)
+
+
+def _put(bins: list[Deque[float]], age_min: float, drawn_kw: float) -> None:
+    j = int(np.floor(age_min / BIN_MIN + _SLACK))
+    if 0 <= j < len(bins):
+        bins[j].append(float(drawn_kw))
+
+
+def _stored_bins(raw: Any, n: int) -> list[Deque[float]]:
+    out = _bins(n)
+    for b, cells in zip(out, raw if isinstance(raw, list) else []):
+        b.extend(v for cell in (cells if isinstance(cells, list) else []) if (v := finite_float(cell)) is not None and v >= 0.0)
+    return out
+
+
+def _levels(bins: list[Deque[float]], floor_kw: float, tolerance: float) -> np.ndarray:
+    """Median per bin, at least ``floor_kw``, up to the first bin with too
+    few samples or within ``tolerance`` of the floor: the profile ends there."""
+    out: list[float] = []
+    for b in bins:
+        if len(b) < MIN_COUNT:
+            break
+        level = max(float(np.median(list(b))), floor_kw)
+        if level <= (1.0 + tolerance) * floor_kw:
+            break
+        out.append(level)
+    return np.array(out, dtype=np.float64)
+
+
+def entry_levels(profile: ApproachProfile | None, floor_kw: float, tolerance: float) -> np.ndarray:
+    """The space draw by :data:`BIN_MIN` bin after an entry, kW; empty with
+    no evidence above the floor."""
+    if profile is None or floor_kw <= 0.0:
+        return np.zeros(0)
+    return _levels(profile.entry, floor_kw, tolerance)
+
+
+def ramp_levels(profile: ApproachProfile | None, floor_kw: float, tolerance: float) -> np.ndarray:
+    """The draw by bin after a space run's end, kW; empty with no evidence.
+    Read against the floor, as the entry is: a wind-down at or under it is
+    noise beside the standby draw."""
+    if profile is None or floor_kw <= 0.0:
+        return np.zeros(0)
+    return _levels(profile.ramp, floor_kw, tolerance)
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index f30638dd17..f40bd9baee 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -1214,15 +1214,12 @@ SOLAR_APERTURE_MIN_SAMPLES: Final = 30
 #: capacity turns into 0.012 K, under 0.02 K of residual against the
 #: learner's 1.0 K rejection.
 HEAT_LOSS_MAX_SOLAR_W_M2: Final = 50.0
-#: #53 — per-hour internal gains, ridge-regularised toward the constant.
+#: #53 — per-hour internal gains, started at the constant (D2-s3-11: no ridge).
 CONF_INTERNAL_GAINS_LEARNING_ENABLED: Final = (
     "internal_gains_learning_enabled"
 )
 DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED: Final = False
 INTERNAL_GAINS_ALPHA: Final = 0.05
-#: Pull toward the configured constant per fold — the profile is a
-#: perturbation of the prior, not a replacement for it.
-INTERNAL_GAINS_RIDGE: Final = 0.02
 #: Per-hour ceiling as a multiple of the configured constant.
 INTERNAL_GAINS_MAX_FACTOR: Final = 3.0
 #: #2223: the share of the heat-loss walk the level must have traversed
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index ae92ea0460..444015bb8d 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -184,7 +184,6 @@ from .const import (
     SOLAR_APERTURE_ALPHA,
     SOLAR_APERTURE_MIN_SAMPLES,
     INTERNAL_GAINS_ALPHA,
-    INTERNAL_GAINS_RIDGE,
     INTERNAL_GAINS_MAX_FACTOR,
     INTERNAL_GAINS_MIN_UA_CONFIDENCE,
     CONFIDENCE_MARGIN_CAP_C,
@@ -226,6 +225,7 @@ from . import battery as battery_view
 from . import comfort_band
 from . import draw_range
 from . import heat_energy
+from . import learning_freeze
 from . import heat_curve
 from . import mixing_valve
 from . import off_restore
@@ -961,7 +961,9 @@ def _fold_flow_lift(coord: Any, now: datetime) -> None:
     commanded = coord._commanded_power()
     if commanded < draw_range.power_floor_kw(coord._accuracy.draw, params):
         return
-    if coord._learning_frozen(CONF_OUTDOOR_TEMP_ENTITY) is not None:
+    # An unplanned charge runs the supply at the tank's charge temperature (#3760).
+    if coord._learning_frozen(CONF_OUTDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.SPACE_HEAT,
+                              evidence=_space_evidence(coord, coord._commanded_split())) is not None:
         return
     if _cop_fold_blocked(coord):
         return
@@ -1114,13 +1116,25 @@ def _observe_heat_energy(coord: Any, reader: Any, at: datetime) -> None:
     """
     ctx = _ctx_of(coord)
     meter = heat_energy.meter_of(coord)
-    heat = reader.read(CONF_HEAT_ENERGY_ENTITY)
+    heat, tank = reader.read(CONF_HEAT_ENERGY_ENTITY), reader.read(CONF_DHW_TEMP_ENTITY)
     meter.observe_cycle(
         at, coord._pump_signals, heat, coord._measured_energy, ctx._config.optimization_interval,
-        HOUSE_LOSS_SAMPLE_BOUNDS_H, ctx._thermal_params,
+        HOUSE_LOSS_SAMPLE_BOUNDS_H, ctx._thermal_params, tank.value if tank.ok else None,
     )
 
 
+def _ceiling_frozen(coord: Any) -> bool:
+    """A draw-range ceiling sample's ask (D2-s3-09): refused at the running floor in force."""
+    at_floor = draw_range.at_running_floor(coord._accuracy.draw, coord._measured_power)
+    return coord._learning_frozen(CONF_POWER_ENTITY, sample=learning_freeze.Sample.CEILING,
+                                  evidence=learning_freeze.Evidence(at_running_floor=at_floor)) is not None
+
+
+def _space_evidence(coord: Any, split: tuple[float, float]) -> learning_freeze.Evidence:
+    """A space-heat ask's evidence for the interval ``split`` planned (#3760, D12-s3-03)."""
+    return learning_freeze.Evidence(unplanned_charge=heat_energy.meter_of(coord).unplanned_charge(split))
+
+
 def _replay_gate(
     coord: Any, interval: FabricInterval | None, span_heat_kw: float | None, raw: str | None
 ) -> tuple[float | None, bool, str | None, bool]:
@@ -1174,6 +1188,15 @@ async def _async_learn_heat_span(coord: Any, clean: dict[str, bool]) -> None:
     modelled_cop = coord._thermal_model.compute_cop(ctx._current_state.outdoor_temperature)
     close = heat_energy.close_span(meter, clean, split, coord._last_house_sample, coord._last_house_sample_time,
                                    modelled_cop, COP_REFUSED_UNALIGNED, FabricInterval)
+    # The span's own evidence; its cycles' facts are already ANDed into ``clean``.
+    if frozen := learning_freeze.reason(learning_freeze.Facts(), (), learning_freeze.Sample.SPACE_HEAT,
+                                        learning_freeze.Evidence(unplanned_charge=close.unplanned_charge)):
+        # One span, one note (it spoils every learner it would reach).
+        if close.house or close.lower:
+            coord._learner_freezes.note_freeze("house" if close.house else "lower", frozen)
+        if close.cop:
+            coord._measured_cop.refusal = COP_REFUSED_FROZEN
+        return
     if close.lower:
         await coord._async_learn_lower_floor_loss(close.interval, close.space_kw)
     if close.house:
@@ -3479,6 +3502,31 @@ def _tail_freeze(coord: Any) -> str | None:
     )
 
 
+def _freeze_facts(coord: Any) -> learning_freeze.Facts:
+    """The cycle's facts for :func:`learning_freeze.reason`, read off ``coord``.
+
+    A reading is unusable only with an entity: a slot never configured reads
+    ``not_configured`` with none and must not freeze learning.
+    """
+    health = coord._input_health
+    signals = coord._pump_signals
+    away = coord._away_state
+    return learning_freeze.Facts(
+        external_heat=bool(coord._external_heat_active),
+        signals=signals.freeze_reason,
+        defrosting=bool(signals.defrosting),
+        unusable={} if health is None else {
+            key: reading.problem for key, reading in health.readings.items()
+            if reading is not None and reading.entity_id and not reading.ok
+        },
+        ventilation=bool(coord._vent_cusum.tripped),
+        boost=boost.FREEZE_REASON if boost.space_learning_frozen(coord) else None,
+        tail=_tail_freeze(coord),
+        away=bool(away.active),
+        away_recovery=bool(away.recovery_active),
+    )
+
+
 class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     """Coordinator for Heat Pump Cost Optimizer."""
 
@@ -3757,7 +3805,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             entry.entry_id,
             lambda: _ctx_of(self)._thermal_params,
             publish=functools.partial(_publish_params, self),
-            frozen=functools.partial(self._learning_frozen, room_air=False),
+            frozen=self._learning_frozen,
             heating_active=lambda: bool(planned().get("dhw_heating_active", False)),
             # The live detector, never a solve's copy of it: no solve runs
             # in comfort, boost or off to refresh one (#1736 H4).
@@ -4023,7 +4071,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # --- Active system identification (item 18) ------------------------
         self._sysid = SystemIdentification(
             SysIdConfig(
-                enabled=ctx._config.system_identification_enabled,
                 # The fit's intercept ridge pulls toward these CONFIGURED priors;
                 # arm() re-seeds the gains from the learned profile (#1655).
                 gains_prior_kw=float(ctx._thermal_params.internal_gains),
@@ -4983,11 +5030,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         flow meter measures the interval's heat instead (#2016). The hot
         water subtracted is ``_commanded_split``'s, which zeroes a channel the
         observed mode cannot serve: a phantom allocation would bias every
-        sample low, in one direction (v5.3.0). A mode dwell that saw hot water
-        leaves neither the reading nor the ask a space figure (``ran_hot_water``).
+        sample low, in one direction (v5.3.0). A dwell that saw hot water, or an
+        unplanned charge (#3760), leaves the reading and the ask no space figure.
         """
         commanded_space, dhw_share = self._commanded_split()
-        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):
+        if heat_energy.ran_hot_water((m := heat_energy.meter_of(self)).attribution(split := (commanded_space, dhw_share))) or m.unplanned_charge(split):
             return None
         if not getattr(self, "_ctx", self)._config.heat_pump_power_entity:
             return commanded_space
@@ -5014,7 +5061,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # fabricates a confident 0 kW sample. Same gate, same reasoning as
         # the COP fold: a large total gap is tracking, not measurement, so
         # the interval carries no usable split (v4.0.5 review).
-        commanded_total = commanded_space + dhw_share
+        commanded_total = draw_range.inside_approach(self._accuracy.draw) or commanded_space + dhw_share  # inside a run's learned approach, the expected draw
         if (
             abs(float(self._measured_power) - commanded_total)
             / max(commanded_total, 0.5)
@@ -5281,7 +5328,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if self._measured_power is None and not heat_energy.meter_of(self).counter:
             return COP_REFUSED_NO_POWER
         heat_kw = self._flow_bias.heat_output_kw  # read first: an open window moves no measured heat
-        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):
+        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, sample=learning_freeze.space_heat(heat_kw is not None or heat_energy.meter_of(self).counter), evidence=_space_evidence(self, self._commanded_split())):
             self._measured_cop.frozen_refusals += 1  # machine_evidence's tally
             return COP_REFUSED_FROZEN
 
@@ -5295,7 +5342,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             self._fold_cop_evidence(row.asked_kw, row.drawn_kw, None, row.reference, row.cop_scale)
         if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now(), not experiment)) is not None:
             self._apply_cop_scale(owed)
-        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):
+        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment, draw_range.inside_approach(draw) is not None):
             return refusal
 
         # In the frosting band the shortfall belongs to the defrost derate,
@@ -5716,7 +5763,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # #2508: no room entity is the raw freeze, so it ranks before the
         # ventilation pass-through below and leaves no counter span clean.
         raw = learner_room_unread(ctx._config) or self._learning_frozen(
-            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY)
+            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY,
+            sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, self._commanded_split()))
         heat_kw, clean, frozen, fold = _replay_gate(self, interval, span_heat_kw, raw)
         # "ventilation" is the one reason to look past: the detector below
         # clears it and needs the residual to see the window close. Any other
@@ -5875,7 +5923,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if not params.two_zone_enabled or not ctx._config.lower_floor_temp_entity:
             return False
         heat_kw, clean, frozen, fold = _replay_gate(self, interval, span_heat_kw, self._learning_frozen(
-            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_LOWER_FLOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY
+            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_LOWER_FLOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY,
+            sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, self._commanded_split()),
         ))
         if frozen:
             self._learner_freezes.note_freeze("lower", frozen)
@@ -6056,14 +6105,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             await _best_effort_cycle_step(
                 self._async_drive_pumps, "Pump scheduling skipped: %s")
 
-            # Close the loop: pair the previous interval's prediction with
-            # what actually happened, accumulate energy, and train the
-            # derate. #1644 (D1-s2-91): each step owns its own failure.
-            await _best_effort_cycle_step(
-                self._record_accuracy, "Accuracy pairing skipped: %s"
-            )
-            await _best_effort_cycle_step(lambda: room_record.async_note_cycle(self, dt_util.now(), rooms.readings_of(self), room_record.House(  # #3616 phase 3a
-                _ctx_of(self)._current_state.outdoor_temperature, self._floor_return_temp, self._measured_power, float(self._current_action.get("power", 0.0)), float(self._current_action.get("dhw_power", 0.0)))), "Room history skipped: %s")
+            # #3616 phase 3a, before the pairing replaces the settled interval's split.
+            await _best_effort_cycle_step(lambda: room_record.async_note_cycle(self, dt_util.now(), rooms.readings_of(self), room_record.House(_ctx_of(self)._current_state.outdoor_temperature, self._floor_return_temp,
+                self._measured_power, heat_energy.meter_of(self).served_space_alone((self._pending_prediction or {}).get("split")))), "Room history skipped: %s")
+            # Close the loop: pair the previous interval's prediction with what
+            # actually happened, accumulate energy, and train the derate.
+            # #1644 (D1-s2-91): each step owns its own failure.
+            await _best_effort_cycle_step(self._record_accuracy, "Accuracy pairing skipped: %s")
             await _best_effort_cycle_step(
                 self._track_realised_peak, "Realised-peak tracking skipped: %s"
             )
@@ -6261,6 +6309,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             state=state,
             start_time=solve_now,
             compressor_running=duty_switch.running_now(duty_switch.record_for(self), self._current_action),
+            approach=draw_range.solve_approach(self._accuracy.draw, params, solve_now.timestamp()),
             forecast=ForecastSeries(
                 prices=horizon.prices,
                 outdoor_temps=horizon.outdoor_temps,
@@ -6816,86 +6865,18 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         """
         _publish_params(self, **self._model_corrections(dt_util.now()))
 
-    def _learning_frozen(self, *keys: str, room_air: bool = True) -> str | None:
-        """Why learning should be skipped this interval, or ``None``.
+    def _learning_frozen(
+        self,
+        *keys: str,
+        sample: learning_freeze.Sample = learning_freeze.Sample.ROOM_AIR,
+        evidence: learning_freeze.Evidence = learning_freeze.NO_EVIDENCE,
+    ) -> str | None:
+        """Why a ``sample`` over ``keys`` should be skipped this interval, or ``None``.
 
-        Fail closed. A learner that pauses for an hour loses an hour of
-        convergence; a learner that trains on a flatline or on heat it did not
-        supply corrupts a parameter that is persisted to disk.
+        The facts of this cycle, handed to the one predicate
+        (:func:`learning_freeze.reason`), which owns the reasons and their order.
         """
-        if self._external_heat_active:
-            return "external_heat_source"
-        # v5.3.0: the plant-wide freezes, from the heat pump's own signals.
-        # They have a shape the loop below cannot express: that loop asks
-        # "is the reading the caller named unusable" and freezes on the
-        # *absence* of a measurement, while these freeze on the *presence*
-        # of one — the online flag says False, the fault flag says True,
-        # the mode says cooling. Each is a healthy, fresh reading that
-        # happens to be bad news and makes the whole interval misleading
-        # rather than one sensor unreadable, so they are not scoped to the
-        # caller's keys either, and they sit ahead of the key loop as the
-        # root cause when both fire: reporting the symptom would send a
-        # user looking at the wrong thing. See ``pump_signals.py`` for why
-        # the absence of these signals never freezes anything.
-        signals = self._pump_signals
-        if signals.freeze_reason is not None:
-            return signals.freeze_reason
-        # #944 (round-4 D7-03): a fourth presence condition, kept out of
-        # ``freeze_reason`` because the derate still folds these intervals
-        # (the settlement exempts the reason it causes). A defrost reverses
-        # the cycle — the interval's heat is negative while the learners
-        # replay the commanded power as if it had flowed — and happens
-        # below the frost band too, where the COP learner's guard ends.
-        if signals.defrosting:
-            return "defrosting"
-        # An unusable input outranks ventilation deliberately: the heat-loss
-        # learner treats "ventilation" as a pass-through to keep feeding
-        # the detector, and a flatline fed through that pass would
-        # drive the very detector that froze everything. With the input
-        # check first, the latch simply holds until real data returns.
-        #
-        # v5.1.3: this used to freeze only on ``stale``. Every other
-        # unusable-input problem — ``unavailable``, ``missing_entity``,
-        # ``not_numeric``, ``unknown_unit`` — left the learners running.
-        # That mattered because ``_update_current_state`` deliberately PINS
-        # the last good value when a read fails (there is no ``else`` on
-        # those branches, by design: the planner is better off steering from
-        # the last known room temperature than from nothing). Pinning is
-        # right for the *input*; it is fatal for a *learner*, which then
-        # reads a frozen number as thermal behaviour and persists the
-        # result. A flat battery or a dropped Zigbee sensor walked the house
-        # heat-loss scale from 1.0 to ~0.37 inside 48 h, saved every 10
-        # samples, and the corruption outlived the sensor outage by weeks.
-        # So: freeze on ANY unusable reading. The pinning in
-        # ``_update_current_state`` is untouched and intentional — this
-        # bounds only what the learners may do with a pinned value.
-        #
-        # ``reading.entity_id`` is the load-bearing half of the predicate: a
-        # slot the user never configured reads as ``not_configured`` with no
-        # entity, and must NOT freeze learning — otherwise every install
-        # without an optional sensor would never learn anything.
-        health = self._input_health
-        if health is not None:
-            for key in keys:
-                reading = health.readings.get(key)
-                if reading is not None and reading.entity_id and not reading.ok:
-                    return f"{reading.problem}:{key}"
-        # #26: training on an open window teaches a phantom heat loss the
-        # house does not have — measured in °C-scale residuals, far above
-        # any learning signal. ``room_air=False``: a learner reading no room air.
-        if room_air and self._vent_cusum.tripped:
-            return "ventilation"
-        # #1935: boost space heating — either surface — actuates heat the
-        # plan's trajectory never assumed, so the plant state the interval
-        # replay integrates from diverges and every residual is warm-side
-        # garbage: two boost days walked a persisted ``house_heat_loss_scale``
-        # to the trust-region floor. Ranked below "ventilation" deliberately:
-        # that is the one reason the heat-loss learner looks past (its
-        # pass-through feeds the window CUSUM), and a boost window must not
-        # starve the detector of its feed.
-        if boost.space_learning_frozen(self):
-            return boost.FREEZE_REASON
-        return _tail_freeze(self)
+        return learning_freeze.reason(_freeze_facts(self), keys, sample, evidence)
 
     async def _fetch_tibber_prices(self) -> None:
         """Fetch electricity prices (Tibber or a price entity).
@@ -9170,13 +9151,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             return
         # An away setback sits deliberately below the normal floor this
         # tracker reads (the lowered floor lives only inside the solve's
-        # snapshot/unwind envelope), so every vacation would read as a
-        # comfort miss and wipe the learned bias. Same for a tripped window
-        # detector, a stale sensor or none (#2508: room and upper zone are
-        # 21.0 C defaults): not the curve's doing. No evidence on such days.
-        if self._away_state.active or self._away_state.recovery_active:
-            return
-        if (self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) or learner_room_unread(ctx._config)) is not None:
+        # snapshot/unwind envelope), so every vacation, and its recovery,
+        # would read as a comfort miss and wipe the learned bias: the
+        # comfort kind's own reasons. Same for a tripped window detector, a
+        # stale sensor or none (#2508: room and upper zone are 21.0 C
+        # defaults): not the curve's doing. No evidence on such days.
+        if (self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.COMFORT)
+                or learner_room_unread(ctx._config)) is not None:
             return
         hour = now.hour + now.minute / 60.0
         try:
@@ -9356,9 +9337,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         """#53: pull the interval's hour toward the residual it produced.
 
         Only dark intervals feed it — under real sun the same surplus is
-        the aperture learner's business (#36) — and the ridge term keeps
-        every hour tethered to the configured constant: the profile is a
-        perturbation of the prior, never a replacement for it.
+        the aperture learner's business (#36). Each hour starts at the
+        configured constant and is tethered by the clip below and the
+        convergence gate, not by a pull back toward it (D2-s3-11).
 
         #2223: folded only once the heat-loss level has converged -- the
         residual's ΔT-part is hour-correlated, so the shape would learn it.
@@ -9368,6 +9349,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             getattr(self, "_house_heat_loss_samples", 0)
         ):
             return
+        # D7-s2-01: the occupied house's gains; an away residual is the empty house's.
+        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.OCCUPANCY) is not None:
+            return
         if is_sunlit_interval(previous_state.solar_radiation):
             return
         if previous_time is None or dt_h <= 1e-6:
@@ -9382,8 +9366,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         y = residual * capacity / dt_h
         if not np.isfinite(y):
             return
-        g = self._internal_gains_profile[hour]
-        g += INTERNAL_GAINS_ALPHA * y - INTERNAL_GAINS_RIDGE * (g - g0)
+        # D2-s3-11: no pull toward g0. A ridge's fixed point is
+        # alpha/(alpha+ridge) of the true gain; the step's expectation is zero
+        # only at a zero residual. The clip and the convergence gate tether it.
+        g = self._internal_gains_profile[hour] + INTERNAL_GAINS_ALPHA * y
         self._internal_gains_profile[hour] = float(
             np.clip(g, 0.0, INTERNAL_GAINS_MAX_FACTOR * max(g0, 0.05))
         )
@@ -9922,7 +9908,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # D7-s2-02: the inference folds the same meter the COP learner
         # refuses (``_cop_fold_blocked``, #1067); the duty path above
         # reads the flag, not the meter, and stays open.
-        if ratio is not None and in_frost_band(outdoor) and not _cop_fold_blocked(self):
+        # Carries 0-1 (item 0116e1a6): a pump that sets its own power draws
+        # what it decides, so drawn over asked is no delivery ratio there.
+        ignored = self._measured_cop.scale_response == draw_range.ASK_IGNORED
+        if ratio is not None and in_frost_band(outdoor) and not _cop_fold_blocked(self) and self._learning_frozen(
+                sample=learning_freeze.Sample.DELIVERED_RATIO, evidence=learning_freeze.Evidence(ask_ignored=ignored)) is None:
             self._defrost.observe(outdoor, sample.humidity, ratio)
 
     def _record_accuracy(self) -> None:
@@ -9949,9 +9939,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # The meter read now closes the interval ``pending`` governed, so the
         # draw pairs with that interval's ask and set-point, not the next one's
         # (#2262), within the window the accuracy pairing below trusts; a
-        # prediction recording no split, or a dwell that saw hot water, is none.
-        if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending["split"])):
-            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=power_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"), experiment_s=pending["when"].timestamp() if pending.get("mode") == "system_identification" else None)
+        # prediction recording no split is none, and a dwell that saw hot water moves only the approach's run clock.
+        if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0):
+            # An unplanned charge is no running space sample (#3760): the pending split's own evidence.
+            space_frozen = self._learning_frozen(CONF_POWER_ENTITY, sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, pending["split"]))
+            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=space_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"), ceiling_frozen=_ceiling_frozen(self), span=draw_range.Span(pending["when"].timestamp(), now.timestamp(), heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending["split"])), pending.get("mode") == "system_identification"))
 
         # T5 #16: settle every matured lead-time promise against the same
         # measured temperature the one-step sample below uses. The window
@@ -10037,11 +10029,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
         self._pending_prediction = {
             "when": now,
-            # The meter sees the whole heat pump, so the prediction it is
-            # compared against has to be the whole plan. Recording space
-            # heating alone made every hot-water charge look like the unit
-            # under-delivering, which fed straight into the defrost derate.
-            "power": self._commanded_power(),
+            # The meter sees the whole heat pump, so the prediction it is compared against is the whole
+            # plan (space alone read every charge as a defrost loss), a run's learned approach included.
+            "power": draw_range.expect(self._accuracy.draw, self._commanded_split(), ctx._thermal_params, now.timestamp(), interval_h),
             "split": self._commanded_split(),
             "flow_command": pump_arbiter.flow_command(self),
             "mode": self._current_action.get("mode"),  # routes draw_range.fold
@@ -10103,7 +10093,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if not getattr(self, "_ctx", self)._config.dhw_temp_entity:
             return None
         value = finite_float(self._dhw_temperature)
-        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:
+        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:
             return value
         return None
 
@@ -10158,9 +10148,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         trajectory = result.sensor_trajectory(ctx._thermal_params.two_zone_enabled)
         if not trajectory:
             return
-        self._accuracy.note_promise(  # R9-UX-6: the day-ahead replay's promise
-            solve_time, dt_h, trajectory, result.power_schedule,
-            result.dhw_power_schedule, result.prices,
+        space = draw_range.received_schedule(self._accuracy.draw, ctx._thermal_params, result.power_schedule, result.dhw_power_schedule, solve_time, dt_h)
+        self._accuracy.note_promise(  # R9-UX-6: the day-ahead replay's promise, on the draw the pump takes
+            solve_time, dt_h, trajectory, space, result.dhw_power_schedule, result.prices,
         )
         for lead in LEAD_BUCKETS:
             idx = int(round(lead / dt_h))
@@ -10268,9 +10258,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             self._schedule_ledger_save()
             return
 
-        dhw_share = heat_energy.dhw_share(
-            heat_energy.meter_of(self).attribution((planned_space, planned_dhw))
-        )
+        # The interval ``pending`` governed, read at this cycle's close: an
+        # unplanned charge books as hot water (the whole-unit rule).
+        dhw_share = heat_energy.meter_of(self).booked_dhw_share((planned_space, planned_dhw))
         dhw_energy = energy * dhw_share
         space_energy = energy - dhw_energy
 
@@ -10910,8 +10900,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if not ctx._config.comfort_learning_enabled:
             return
         # The shared freeze discipline its sibling ``_track_curve_comfort``
-        # consults: a defrost or a dead indoor sensor fakes a flat plan (#1332).
-        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) is not None:
+        # consults: a defrost or a dead indoor sensor fakes a flat plan (#1332),
+        # and an empty house complains about nothing (D7-s2-01).
+        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.OCCUPANCY) is not None:
             return
         result = self._optimization_result
         if result is None or not result.room_temp_trajectory:
@@ -10985,9 +10976,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         ctx = getattr(self, "_ctx", self)
         if not self._sysid.active:
             return
-        why = sysid.hold_reason(
+        why = sysid.hold_reason(  # a space-heat ask: an unplanned charge's heat went to the tank
             self._pump_signals,
-            self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY),
+            self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.SPACE_HEAT,
+                                  evidence=_space_evidence(self, self._commanded_split())),
             getattr(ctx, "_config", None),
             dt_util.now(),
         )
@@ -11251,6 +11243,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             start_time=solve_at,
             held_start=held_start,
             compressor_running=duty_switch.record_for(self).solved_running,
+            approach=draw_range.solve_approach(self._accuracy.draw, scratch_params, solve_at.timestamp()),
             forecast=ForecastSeries(
                 prices=horizon.prices,
                 outdoor_temps=horizon.outdoor_temps,
diff --git a/custom_components/heatpump_optimizer/dhw_charges.py b/custom_components/heatpump_optimizer/dhw_charges.py
new file mode 100644
index 0000000000..0e97e272e2
--- /dev/null
+++ b/custom_components/heatpump_optimizer/dhw_charges.py
@@ -0,0 +1,400 @@
+"""Hot-water charges the pump would start and run, for the planner's plan.
+
+Two stages ``DhwPlanner._build_dhw_requirements`` calls after the planners
+have bought the floor. The start condition: the tank temperature below
+which the pump starts a charge (:func:`dhw_start_temps`), and the floor
+repair under it (:func:`place_startable`), which keeps no charge the pump
+would not start. The commit (:func:`commit_charges`), on a solve that plans
+runs (:class:`ChargeRuns`): the plan as charges that run at the pump's
+floor or above, chosen between the store program's plan
+(:class:`_StoreProgram`) and the lifted one.
+
+Pure computation over arrays and the planner's own tank walk; the planner
+is passed in, never imported at run time.
+"""
+from __future__ import annotations
+
+from functools import partial
+from typing import TYPE_CHECKING, Any, Callable, NamedTuple
+
+import numpy as np
+
+from . import runs
+from .thermal_model import (
+    ThermalParameters,
+    ThermalState,
+    dhw_start_below_c,
+    dhw_step_target_c,
+    heat_per_cop_kw,
+    power_for_heat_per_cop_kw,
+)
+
+if TYPE_CHECKING:
+    from .dhw_planner import DhwPlanner, _DhwPlanContext
+
+
+#: How many times :func:`place_startable` re-buys what the start condition
+#: barred before it settles for dropping. A round re-buys under the charges
+#: the round before kept, and the measured placements settle in two or three
+#: (``dev/audit/harnesses/r10_dhw_start_hysteresis.py``, repair_rounds_max),
+#: so eight is that with room to spare and still a bound.
+STARTABLE_ROUNDS = 8
+
+
+def dhw_start_temps(
+    params: ThermalParameters, state: ThermalState, n_steps: int, cycle_step: int | None
+) -> np.ndarray | None:
+    """Per step, the tank temperature below which the pump starts a charge, °C.
+
+    The target the arbiter writes on that step (``dhw_step_target_c`` on the
+    set-point entity's grid, ``state.dhw_setpoint_grid``: the cycle's on
+    ``cycle_step``, the everyday one elsewhere) less the pump's start
+    hysteresis (``state.dhw_start_hysteresis_k``), so a disinfection charge
+    is judged against its own target and a stepped entity's against the step
+    it lands on. ``None`` where no start condition is known
+    (``dhw_start_below_c``).
+    """
+    hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid
+    everyday = dhw_start_below_c(dhw_step_target_c(params, False, grid), hysteresis_k)
+    if everyday is None:
+        return None
+    start = np.full(n_steps, everyday)
+    if cycle_step is not None and 0 <= cycle_step < n_steps:
+        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)
+    return start
+
+
+def startable_steps(
+    plan: np.ndarray, temps: np.ndarray, start_below: np.ndarray | None
+) -> np.ndarray:
+    """The steps where charging is something the pump does.
+
+    A step that opens on a tank below its start temperature (``temps[i]``,
+    the simulated level at its start), and the step after one of a charge
+    under way, which runs on to its target. A charge is under way from the
+    step it opens below its start temperature, or from the first step, where
+    it is kept as one that may be (:func:`drop_unstartable`); a charge the
+    pump would not start carries nothing on, so the repair buys neither
+    inside it nor behind it. Every step where no start condition is known
+    (``start_below`` ``None``).
+    """
+    on = np.asarray(plan, dtype=float) > 0.0
+    if start_below is None:
+        return np.ones(on.size, dtype=bool)
+    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]
+    under_way = bool(on[:1].any())
+    for i in range(1, on.size):
+        ok[i] |= under_way
+        under_way = bool(on[i] and ok[i])
+    return ok
+
+
+def drop_unstartable(
+    plan: np.ndarray, start_below: np.ndarray, temps_of: Callable[[np.ndarray], np.ndarray]
+) -> np.ndarray:
+    """``plan`` without the charges the pump would never start.
+
+    Each run is judged in time order on the trajectory ``temps_of`` simulates
+    for the runs kept before it: one that begins on a tank at or above its
+    step's start temperature is removed whole. A run at the first step is
+    kept, as it may be a charge already under way (Bankaifan, #3440).
+    """
+    plan = np.array(plan, dtype=float)
+    on = plan > 0.0
+    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:
+        end = i + int(np.argmin(np.append(on[i:], False)))
+        if temps_of(plan)[i] >= start_below[i]:
+            plan[i:end] = 0.0
+    return plan
+
+
+def place_startable(
+    plan: np.ndarray,
+    start_below: np.ndarray | None,
+    temps_of: Callable[[np.ndarray], np.ndarray],
+    repair: Callable[..., np.ndarray],
+) -> np.ndarray:
+    """The floor repair of ``plan`` under the pump's start condition.
+
+    With no condition, ``repair(plan=plan)``, the call as it always was. With
+    one, the charges the pump would not start are dropped and ``repair``,
+    handed the condition so it places only on :func:`startable_steps`,
+    re-buys what the floor still needs; a top-up
+    warms the tank under every later charge, so the two repeat until the
+    plan stands, at most :data:`STARTABLE_ROUNDS` times. The plan that leaves
+    holds no charge the pump would not start, and is short of the floor only
+    where no startable step can hold it.
+    """
+    if start_below is None:
+        return repair(plan=plan)
+    for _ in range(STARTABLE_ROUNDS):
+        fixed = repair(plan=drop_unstartable(plan, start_below, temps_of), start_below=start_below)
+        if np.array_equal(fixed, plan):
+            break
+        plan = fixed
+    return drop_unstartable(plan, start_below, temps_of)
+
+
+#: How far under a floor a tank may read and still hold it, K: the planners'
+#: shortfall tolerance (``DhwPlanner._dhw_shortfall``) and the commit's.
+SHORTFALL_K = 0.05
+
+#: The store program's temperature cell, K, and the spacing of its COP table.
+#: Constants from the contributor's spike on one install, not measured
+#: thresholds: the grid decides how cheap a committed plan is, never whether
+#: it ships, which is :func:`charge_refusal`'s on the planner's own walk.
+_STORE_GRID_K = 0.25
+_COP_KNOT_K = 1.0
+#: How far inside its bounds the program keeps its store, K, so the rating
+#: clamp trims no committed step on the walk. The linear store and the walk
+#: differ by about a thousandth of a kelvin along the fixtures' plans
+#: (``dev/audit/harnesses/r11_honest_dhw_runs.py``, ``stores``).
+_STORE_MARGIN_K = 0.02
+
+
+def charge_refusal(
+    candidate: np.ndarray,
+    start_below: np.ndarray | None,
+    temps_of: Callable[[np.ndarray], np.ndarray],
+    held: np.ndarray,
+) -> tuple[str, int] | None:
+    """Why the commit may not ship ``candidate``, or ``None`` where it may.
+
+    ``("start", step)``: on the candidate's own walk the pump would not start
+    the charge that opens there (:func:`drop_unstartable` removes it).
+    ``("floor", step)``: the walk falls under ``held``, the floors the
+    uncommitted plan held, by more than the planners' tolerance. With no
+    start condition known every charge is taken to start.
+    """
+    if start_below is not None:
+        lost = np.flatnonzero(drop_unstartable(candidate, start_below, temps_of) != candidate)
+        if lost.size:
+            return "start", int(lost[0])
+    short = np.flatnonzero(temps_of(candidate)[1 : candidate.size + 1] < held - SHORTFALL_K)
+    return ("floor", int(short[0])) if short.size else None
+
+
+def charges_run(plan: np.ndarray, floor: float, tails: bool) -> bool:
+    """Every charging step of ``plan`` runs at ``floor`` or above; with
+    ``tails``, a charge's last step may end inside it, at any level."""
+    on, low = plan > 0.0, (plan > 0.0) & (plan < floor - 1e-9)
+    ends = np.r_[False, on[:-1] & ~low[:-1]] & ~np.r_[on[1:], False]
+    return not bool(np.any(low & ~(ends & tails)))
+
+
+def whole_charges(charge_runs: ChargeRuns | None, plan: np.ndarray, mask: np.ndarray) -> np.ndarray:
+    """``mask``, the steps a suppression would zero, without the steps of any
+    charge it does not cover whole, on a solve that plans runs. A committed
+    charge is suppressed whole or kept whole, so no fragment is left shorter
+    than a run or under the floor. ``mask`` itself on a solve that does not."""
+    if charge_runs is None:
+        return mask
+    on, kept = np.r_[False, plan > 0.0, False], mask.copy()
+    for a, b in zip(np.flatnonzero(on[1:] & ~on[:-1]), np.flatnonzero(~on[1:] & on[:-1])):
+        kept[a:b] &= bool(np.all(mask[a:b]))
+    return kept
+
+
+class ChargeRuns(NamedTuple):
+    """What a solve that plans runs hands the planner (``optimizer._engaged``):
+    a start's price, whether the compressor runs at solve time, and whether
+    the install can only run at its floor or above. ``None`` on a solve that
+    plans duty-cycle averages, whose hot-water plan is left as planned."""
+
+    start_cost: float
+    running: bool
+    clamped: bool
+
+
+class _StoreProgram:
+    """The cheapest charges that keep the planner's linear store in bounds:
+    ``runs``' program with the tank temperature as its scalar.
+
+    The state is the run or pause length and the tank on a
+    :data:`_STORE_GRID_K` grid. A step pauses (``_DhwPlanContext.coast``) or
+    charges at the pump's floor or at the run power, at the planning price
+    and the COP of the cell's temperature. A charge that would pass the
+    ceiling fills the tank to it instead, at the level that takes, where
+    that is the floor or above. Under the floor it does so only as a run's
+    last step, which ends inside it (the contributor's tail), and only on an
+    install that can end a run at any moment. The bounds are the caller's floors
+    and, on a charging step, ceilings; a forced-off step stays off, and a
+    start is made only where the caller says the pump would make one.
+
+    What a start pays inside the program is ``start_cost`` less the share of
+    it the space plan's step before already carries (``runs.running_share``):
+    an estimate that steers the search. The committed plan is priced by the
+    start count of the combined draw, in :func:`commit_charges`.
+    """
+
+    def __init__(
+        self,
+        planner: DhwPlanner,
+        ctx: _DhwPlanContext,
+        asked: np.ndarray,
+        tank: tuple[float, np.ndarray],
+        bounds: tuple[np.ndarray, np.ndarray],
+        forced_off: np.ndarray | None,
+        space: np.ndarray,
+    ) -> None:
+        charge, self.params = planner.charge_runs, planner.model.params
+        assert charge is not None
+        self.ctx, self.asked, (self.initial, self.draws), (self.floors, self.ceilings) = ctx, asked, tank, bounds
+        n, floor = ctx.n_steps, runs.floor_kw(self.params.min_electrical_power)
+        self.floor, self.levels = floor, sorted({floor, ctx.p_dhw_max})
+        self.tails, self.running = not charge.clamped, charge.running
+        self.lo = float(np.floor(min(self.initial, float(np.min(self.floors))))) - _COP_KNOT_K
+        self.knots = np.arange(
+            self.lo, float(np.ceil(max(self.initial, float(np.max(self.ceilings))))) + 2.0 * _COP_KNOT_K, _COP_KNOT_K)
+        self.cop = np.array(
+            [planner._dhw_cop_profile(ctx.outdoor_temps, np.full(n, t), ctx.humidity) for t in self.knots])
+        self.forced = np.where(np.zeros(n, dtype=bool) if forced_off is None else forced_off[:n], 0.0, np.nan)
+        before = np.r_[1.0 if charge.running else 0.0, runs.running_share(space, floor)[:-1]]
+        self.start_price = charge.start_cost * (1.0 - before)
+
+    def _rise(self, k: int, temp: Any, level: float) -> Any:
+        """K a whole step ``k`` at ``level`` kW adds to a tank at ``temp``."""
+        heat = np.interp(temp, self.knots, self.cop[:, k]) * heat_per_cop_kw(self.params, level)
+        return heat * self.ctx.dt / self.ctx.c_dhw
+
+    def _to_ceiling(self, k: int, temp: Any) -> tuple[Any, Any]:
+        """The level that takes a tank at ``temp`` to step ``k``'s ceiling
+        by the step's end, kW, and where there is one: a whole step at the
+        run power would pass the ceiling and a part of one reaches it."""
+        room = self.ceilings[k] - _STORE_MARGIN_K - self.ctx.coast(self.draws, k, temp)
+        share = room / self._rise(k, temp, self.levels[-1])
+        fills = (share > 0.0) & (share < 1.0)
+        return power_for_heat_per_cop_kw(
+            self.params, np.where(fills, share, 0.0) * heat_per_cop_kw(self.params, self.levels[-1])), fills
+
+    def _actions(self, k: int) -> tuple[list[runs.Action], list[runs.Action]]:
+        """What step ``k`` may do in a run and in a pause. In a run: each
+        level, and the fill to the ceiling where its level is the floor or
+        above. In a pause: idle, and the tail, a fill under the floor that
+        ends the run before it."""
+        ctx, price, floor = self.ctx, float(self.ctx.prices[k]) * self.ctx.dt, self.floor
+        ran, paused = runs.tie_break(bool(self.asked[k] > 0.0))
+
+        def at(level: float) -> runs.Action:
+            return lambda temp, _ran: (ctx.coast(self.draws, k, temp) + self._rise(k, temp, level), price * level + ran)
+
+        def idle(temp: np.ndarray, _ran: bool) -> tuple[np.ndarray, Any]:
+            return ctx.coast(self.draws, k, temp), paused
+
+        def fill(temp: np.ndarray, ran_before: bool, tail: bool = False) -> tuple[np.ndarray, Any]:
+            level, fills = self._to_ceiling(k, temp)
+            under = level < floor - 1e-9
+            fills = fills & (under & (level >= ctx.min_run_power) & ran_before if tail else ~under)
+            return (
+                np.where(fills, self.ceilings[k] - _STORE_MARGIN_K, ctx.coast(self.draws, k, temp)),
+                np.where(fills, price * level + ran, np.inf),
+            )
+
+        pauses: list[runs.Action] = [idle, partial(fill, tail=True)] if self.tails else [idle]
+        return [*(at(level) for level in self.levels), fill], pauses
+
+    def plan(self, may_start: np.ndarray) -> np.ndarray | None:
+        """The program's plan, kW per step, or ``None`` where no mask keeps
+        the store in bounds."""
+        n, dt = self.ctx.n_steps, self.ctx.dt
+        lengths = (runs.steps_at_least(runs.MIN_RUN, dt), runs.steps_at_least(runs.MIN_PAUSE, dt))
+        width = int(round((self.knots[-1] - self.lo) / _STORE_GRID_K)) + 1
+        cost = np.full((sum(lengths), width), np.inf)
+        temp = np.zeros_like(cost)
+        row = lengths[0] - 1 if self.running else sum(lengths) - 1
+        cell = int(round((self.initial - self.lo) / _STORE_GRID_K))
+        cost[row, cell], temp[row, cell] = 0.0, self.initial
+        trail = []
+        for k in range(n):
+            def place(t: np.ndarray, charged: bool, k: int = k) -> tuple[np.ndarray, np.ndarray]:
+                j = np.rint((t - self.lo) / _STORE_GRID_K).astype(np.int64)
+                inside = (t >= self.floors[k] - SHORTFALL_K + _STORE_MARGIN_K) & (j >= 0) & (j < width)
+                if charged:
+                    inside &= t <= self.ceilings[k] - _STORE_MARGIN_K + 1e-9
+                return np.clip(j, 0, width - 1), np.where(inside, 0.0, np.inf)
+
+            cost, temp, back = runs.advance(
+                cost, temp, runs.state_moves(*lengths, self.forced[k], bool(may_start[k])),
+                self._actions(k), float(self.start_price[k]), place, lengths[0])
+            trail.append(back)
+        if not np.isfinite(cost).any():
+            return None
+        mask, action = runs.read_back(trail, cost, lengths[0])
+        out, at = np.zeros(n), np.array([self.initial])
+        for k in range(n):
+            if mask[k] or action[k]:
+                out[k] = self.levels[action[k]] if mask[k] and action[k] < len(self.levels) else float(
+                    self._to_ceiling(k, at)[0][0])
+            at = self._actions(k)[0 if mask[k] else 1][action[k]](at, True)[0]
+        return out
+
+
+    def accepted(
+        self, may_start: np.ndarray, fits: Callable[[np.ndarray | None], Any]
+    ) -> np.ndarray | None:
+        """The program's plan as ``fits`` passes it, where the pump would
+        start it: a charge ``fits`` refuses for its start clears that step
+        and the program runs again, at most :data:`STARTABLE_ROUNDS` times."""
+        for _ in range(STARTABLE_ROUNDS):
+            fitted = fits(self.plan(may_start))
+            if fitted is None or isinstance(fitted, np.ndarray):
+                return fitted
+            if fitted[0] != "start":
+                break
+            may_start[fitted[1]] = False
+        return None
+
+
+def commit_charges(
+    planner: DhwPlanner,
+    plan: np.ndarray,
+    store: tuple[_DhwPlanContext, float, np.ndarray],
+    limits: tuple[np.ndarray, np.ndarray],
+    forced_off: np.ndarray | None,
+    start_below: np.ndarray | None,
+    space_demand: np.ndarray | None,
+) -> np.ndarray:
+    """The planner's finished, uncommitted ``plan`` as charges the pump can
+    run, on a solve that plans runs (``planner.charge_runs``). ``plan``
+    itself on one that does not, where its cap is under the floor, and where
+    it already runs and no start has a price. The finding and the program
+    are Bankaifan's (pull request 3529).
+
+    The candidates are the store program's plan and the lifted plan (each
+    step under the floor raised to it), each clamped to the rating and kept
+    only if every charge runs (:func:`charges_run`) and
+    :func:`charge_refusal` passes it on its own walk. The cheapest ships:
+    its energy at the planning prices plus the starts of the combined draw,
+    so a charge beside a space run is no start. With no candidate, ``plan``,
+    which ``place_startable`` already left startable.
+    """
+    charge, floor = planner.charge_runs, runs.floor_kw(planner.model.params.min_electrical_power)
+    ctx, tank = store[0], store[1:]
+    if charge is None or ctx.p_dhw_max < floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):
+        return plan
+    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):
+        return plan
+    temps_of = partial(planner._ctx_temps, ctx, *tank)
+    walk = temps_of(plan)
+    held = np.minimum(limits[0], walk[1:])
+    space = np.zeros(ctx.n_steps) if space_demand is None else np.clip(space_demand, 0.0, None)
+
+    def fits(candidate: np.ndarray | None) -> np.ndarray | tuple[str, int] | None:
+        """``candidate`` as the rating leaves it, or why it may not ship."""
+        if candidate is None:
+            return None
+        candidate = planner._ctx_clamp(ctx, tank[0], tank[1], limits[1], candidate)
+        if not charges_run(candidate, floor, not charge.clamped):
+            return "level", 0
+        return charge_refusal(candidate, start_below, temps_of, held) or candidate
+
+    def cost(candidate: np.ndarray) -> float:
+        starts = runs.start_count(space + candidate, floor, charge.running)
+        return float(np.sum(ctx.prices * candidate) * ctx.dt) + charge.start_cost * starts
+
+    program = _StoreProgram(planner, ctx, plan, tank, (held, np.maximum(limits[1], walk[1:])), forced_off, space)
+    proposed = (
+        program.accepted(startable_steps(plan, walk, start_below), fits),
+        fits(np.where((plan > 0.0) & (plan < floor), floor, plan)),
+    )
+    return min((c for c in proposed if isinstance(c, np.ndarray)), key=cost, default=plan)
diff --git a/custom_components/heatpump_optimizer/dhw_learning.py b/custom_components/heatpump_optimizer/dhw_learning.py
index f4c313e792..4731a4895a 100644
--- a/custom_components/heatpump_optimizer/dhw_learning.py
+++ b/custom_components/heatpump_optimizer/dhw_learning.py
@@ -42,6 +42,7 @@ from .dhw_schedule import hour_in_windows, windows_in_force
 from .dhw_draws import DrawStats, labels_for, window_label as draw_window_label
 from .inputs import plausible_c
 from .thermal_model import TANK_ROOM_AMBIENT_TEMP, ThermalParameters
+from .learning_freeze import Evidence, Sample
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -165,7 +166,7 @@ class DhwProfileLearner:
         params: Callable[[], ThermalParameters],
         *,
         publish: Callable[..., None],
-        frozen: Callable[[str], str | None],
+        frozen: Callable[..., str | None],
         heating_active: Callable[[], bool],
         external_heat_active: Callable[[], bool],
         holidays: Callable[[datetime], Collection[date]] = lambda _now: (),
@@ -442,35 +443,44 @@ class DhwProfileLearner:
         self.last_sample_time = now
         self.heating_since_sample = heating
 
-        frozen = self._frozen(CONF_DHW_TEMP_ENTITY)
+        frozen = self._frozen(CONF_DHW_TEMP_ENTITY, sample=Sample.PLANT)
         if frozen:
             return frozen
+        # The usage hours and the draws are the occupied house's: an away
+        # period holds them, never the tank's standby loss (D7-s2-01).
+        occupied = self._frozen(CONF_DHW_TEMP_ENTITY, sample=Sample.TANK_DRAW)
 
         if previous_temp is None or previous_time is None:
-            return None
+            return occupied
 
         dt_h = utc_elapsed_seconds(now, previous_time) / 3600.0
         if dt_h <= 0.02 or dt_h > DHW_COOLING_MAX_SAMPLE_HOURS:
-            return None
+            return occupied
 
         temp_drop = previous_temp - dhw_temp
         weekend = now.weekday() >= 5
         recovered_k, due = self.charge_settle.advance(
             heated_interval, settling, [previous_temp, temp_drop, dt_h, now.hour, weekend]
         )
-        for prev, drop, dt_p, hour, wkend in due:
-            await self.async_learn_usage(prev, drop, dt_p, hour, False, weekend=wkend)
-
         if not heated_interval:
             await self.async_learn_cooling(previous_temp, dhw_temp, dt_h)
+        if occupied:
+            return occupied
+        for prev, drop, dt_p, hour, wkend in due:
+            await self.async_learn_usage(prev, drop, dt_p, hour, False, weekend=wkend)
         if not settling:
             await self.async_learn_usage(
                 previous_temp, temp_drop, dt_h, now.hour, heated_interval, weekend=weekend
             )
-        await self.async_fold_draw_stats(
-            now, previous_temp, temp_drop, dt_h,
-            charge=started_heated or settling, recovered_k=recovered_k,
-        )
+        # D2-s3-08: an interval starting or ending on a heated sample holds
+        # the charge-start dip, which the reading climbs out of while still
+        # heated, so no unheated rise ever takes it back: it is no draw sample.
+        if self._frozen(CONF_DHW_TEMP_ENTITY, sample=Sample.TANK_DRAW,
+                        evidence=Evidence(charge_open=heated_interval)) is None:
+            await self.async_fold_draw_stats(
+                now, previous_temp, temp_drop, dt_h,
+                charge=started_heated or settling, recovered_k=recovered_k,
+            )
         return None
 
     def _standby_rate(self, previous_temp: float) -> float:
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index 5a8aa8adf9..bfe1805200 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -28,6 +28,15 @@ from scipy.optimize import linprog
 
 from . import pv
 from .const import DHW_QUANTILE_MIN_EVENTS
+from .dhw_charges import (
+    SHORTFALL_K,
+    ChargeRuns,
+    commit_charges,
+    dhw_start_temps,
+    place_startable,
+    startable_steps,
+    whole_charges,
+)
 from .dhw_draws import window_label as draw_window_label
 from .dhw_schedule import (
     FULL_DAY,
@@ -53,8 +62,6 @@ from .thermal_model import (
     dhw_draw_scale,
     added_power_for_heat_per_cop_kw,
     delivered_heat_kw,
-    dhw_start_below_c,
-    dhw_step_target_c,
     heat_per_cop_kw,
     power_for_heat_per_cop_kw,
 )
@@ -232,108 +239,6 @@ def _drop_off_steps(mask: np.ndarray, off: np.ndarray | None) -> np.ndarray:
     return kept
 
 
-#: How many times :func:`place_startable` re-buys what the start condition
-#: barred before it settles for dropping. A round re-buys under the charges
-#: the round before kept, and the measured placements settle in two or three
-#: (``dev/audit/harnesses/r10_dhw_start_hysteresis.py``, repair_rounds_max),
-#: so eight is that with room to spare and still a bound.
-STARTABLE_ROUNDS = 8
-
-
-def dhw_start_temps(
-    params: ThermalParameters, state: ThermalState, n_steps: int, cycle_step: int | None
-) -> np.ndarray | None:
-    """Per step, the tank temperature below which the pump starts a charge, °C.
-
-    The target the arbiter writes on that step (``dhw_step_target_c`` on the
-    set-point entity's grid, ``state.dhw_setpoint_grid``: the cycle's on
-    ``cycle_step``, the everyday one elsewhere) less the pump's start
-    hysteresis (``state.dhw_start_hysteresis_k``), so a disinfection charge
-    is judged against its own target and a stepped entity's against the step
-    it lands on. ``None`` where no start condition is known
-    (``dhw_start_below_c``).
-    """
-    hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid
-    everyday = dhw_start_below_c(dhw_step_target_c(params, False, grid), hysteresis_k)
-    if everyday is None:
-        return None
-    start = np.full(n_steps, everyday)
-    if cycle_step is not None and 0 <= cycle_step < n_steps:
-        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)
-    return start
-
-
-def startable_steps(
-    plan: np.ndarray, temps: np.ndarray, start_below: np.ndarray | None
-) -> np.ndarray:
-    """The steps where charging is something the pump does.
-
-    A step that opens on a tank below its start temperature (``temps[i]``,
-    the simulated level at its start), and the step after one of a charge
-    under way, which runs on to its target. A charge is under way from the
-    step it opens below its start temperature, or from the first step, where
-    it is kept as one that may be (:func:`drop_unstartable`); a charge the
-    pump would not start carries nothing on, so the repair buys neither
-    inside it nor behind it. Every step where no start condition is known
-    (``start_below`` ``None``).
-    """
-    on = np.asarray(plan, dtype=float) > 0.0
-    if start_below is None:
-        return np.ones(on.size, dtype=bool)
-    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]
-    under_way = bool(on[:1].any())
-    for i in range(1, on.size):
-        ok[i] |= under_way
-        under_way = bool(on[i] and ok[i])
-    return ok
-
-
-def drop_unstartable(
-    plan: np.ndarray, start_below: np.ndarray, temps_of: Callable[[np.ndarray], np.ndarray]
-) -> np.ndarray:
-    """``plan`` without the charges the pump would never start.
-
-    Each run is judged in time order on the trajectory ``temps_of`` simulates
-    for the runs kept before it: one that begins on a tank at or above its
-    step's start temperature is removed whole. A run at the first step is
-    kept, as it may be a charge already under way (Bankaifan, #3440).
-    """
-    plan = np.array(plan, dtype=float)
-    on = plan > 0.0
-    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:
-        end = i + int(np.argmin(np.append(on[i:], False)))
-        if temps_of(plan)[i] >= start_below[i]:
-            plan[i:end] = 0.0
-    return plan
-
-
-def place_startable(
-    plan: np.ndarray,
-    start_below: np.ndarray | None,
-    temps_of: Callable[[np.ndarray], np.ndarray],
-    repair: Callable[..., np.ndarray],
-) -> np.ndarray:
-    """The floor repair of ``plan`` under the pump's start condition.
-
-    With no condition, ``repair(plan=plan)``, the call as it always was. With
-    one, the charges the pump would not start are dropped and ``repair``,
-    handed the condition so it places only on :func:`startable_steps`,
-    re-buys what the floor still needs; a top-up
-    warms the tank under every later charge, so the two repeat until the
-    plan stands, at most :data:`STARTABLE_ROUNDS` times. The plan that leaves
-    holds no charge the pump would not start, and is short of the floor only
-    where no startable step can hold it.
-    """
-    if start_below is None:
-        return repair(plan=plan)
-    for _ in range(STARTABLE_ROUNDS):
-        fixed = repair(plan=drop_unstartable(plan, start_below, temps_of), start_below=start_below)
-        if np.array_equal(fixed, plan):
-            break
-        plan = fixed
-    return drop_unstartable(plan, start_below, temps_of)
-
-
 class _DhwLegionellaPlan(NamedTuple):
     """What the anti-legionella stage decides, and the ceilings it sets."""
 
@@ -406,6 +311,13 @@ class _DhwPlanContext:
         """The store's per-step ``_tank_decay`` (share kept, standby gain), for a positive capacity."""
         return _tank_decay(self.store.ua_kw_per_c, self.dt, self.c_dhw)
 
+    def coast(self, draw_rates: np.ndarray, i: int, temp: Any) -> Any:
+        """The linear store one step on from ``temp`` with no charge: what it
+        keeps, less step ``i``'s draw, plus the combi flux and the standby
+        gain. The one copy the linear program and the store program read."""
+        decay, gain = self.tank_decay
+        return decay * temp - (float(draw_rates[i]) - _exo_at(self.tank_exo_kw, i)) * self.dt / self.c_dhw + gain
+
 
 class _Horizon(Protocol):
     """The planner's read-only view of the optimizer's per-solve horizon.
@@ -459,7 +371,7 @@ class DhwPlanner:
 
     Every input is explicit and fixed at construction. ``pv_surplus`` and
     ``price_known`` default to None, which is what a fresh optimizer held
-    before its first solve.
+    before its first solve. ``charge_runs``: :class:`ChargeRuns`, or None.
     """
 
     def __init__(
@@ -468,11 +380,13 @@ class DhwPlanner:
         config: _PlannerConfig,
         pv_surplus: np.ndarray | None = None,
         price_known: np.ndarray | None = None,
+        charge_runs: ChargeRuns | None = None,
     ) -> None:
         self.model = model
         self.config = config
         self._pv_surplus = pv_surplus
         self._price_known = price_known
+        self.charge_runs = charge_runs
 
     def _dhw_planning_prices(
         self,
@@ -1298,6 +1212,7 @@ class DhwPlanner:
             max_temp=max_temp,
             forced_off=forced_off,
         ))
+        schedule = commit_charges(self, schedule, tank, (requirement, max_temp), forced_off, start_below, space_demand)
         # Not re-clamped here, because the repair now carries the clamp
         # inside its own loop: every top-up it places is followed by one,
         # so a plan leaves this stage already bounded by the per-step
@@ -1336,6 +1251,7 @@ class DhwPlanner:
             mask[:horizon] = covered[:horizon]
             if legionella_step is not None:
                 mask[legionella_step] = False
+            mask = whole_charges(self.charge_runs, schedule, mask)
             suppress_steps = int(np.sum(mask & (schedule > 1e-6)))
             schedule = np.where(mask, 0.0, schedule)
 
@@ -1482,16 +1398,13 @@ class DhwPlanner:
 
         requirement, max_temp = _within_ceiling(requirement, max_temp)
         params = self.model.params
-        decay, gain = ctx.tank_decay
+        decay, _gain = ctx.tank_decay
 
         # Free trajectory: the tank with no heating (in combi, under the space side's flux).
         free = np.zeros(n_steps + 1)
         free[0] = initial_temp
         for i in range(n_steps):
-            free[i + 1] = (
-                decay * free[i]
-                - (float(draw_rates[i]) - _exo_at(ctx.tank_exo_kw, i)) * dt / c_dhw + gain
-            )
+            free[i + 1] = ctx.coast(draw_rates, i, free[i])
 
         # Influence matrix: A[m, j] = degrees at step m+1 per thermal kWh at j.
         idx = np.arange(n_steps)
@@ -1664,7 +1577,7 @@ class DhwPlanner:
                 plan, initial_temp, outdoor_temps, draw_rates, dt, humidity, exo_kw
             )
         gaps = requirement - temps[1 : plan.size + 1]
-        for i in np.where(gaps > 0.05)[0]:
+        for i in np.where(gaps > SHORTFALL_K)[0]:
             if int(i) not in unreachable:
                 return temps, gaps, int(i)
         return temps, gaps, None
diff --git a/custom_components/heatpump_optimizer/draw_range.py b/custom_components/heatpump_optimizer/draw_range.py
index 31f668c4a3..ca8ec138bd 100644
--- a/custom_components/heatpump_optimizer/draw_range.py
+++ b/custom_components/heatpump_optimizer/draw_range.py
@@ -35,10 +35,12 @@ from __future__ import annotations
 
 from collections import deque
 from dataclasses import dataclass, field
-from typing import Any, Deque
+from typing import Any, Deque, NamedTuple
 
 import numpy as np
 
+from . import runs
+from .approach import BIN_MIN, ApproachProfile, entry_levels, ramp_levels, stored_config
 from .thermal_model import InstallCapability, on_threshold_kw, planned_draw_runs
 
 #: A metered draw at or below this is standby, circulation and controller
@@ -340,6 +342,7 @@ class DrawRange:
     floor_since: int = 0
     #: The steady-run map rows: never read by the window or the latch.
     map: MapRows = field(default_factory=MapRows)
+    approach: ApproachProfile = field(default_factory=ApproachProfile)
 
     def idle_kw(self) -> float | None:
         """The learned idle draw, or ``None`` while too few readings."""
@@ -553,6 +556,7 @@ class DrawRange:
             **({} if self.floor_kw is None else {"floor_kw": self.floor_kw}),
             # Absent with no rows: a store that never kept one is unchanged.
             **({"map_rows": self.map.as_columns()} if self.map.rows else {}),
+            **({"approach": self.approach.as_dict()} if self.approach.config is not None else {}),
         }
 
     @classmethod
@@ -569,13 +573,11 @@ class DrawRange:
         out.ceiling.extend(_stored_ceiling(data))
         out.overdraws = _stored_overdraws(data)
         out.map = _stored_map(data)
-        try:
-            lo, hi = (float(v) for v in data["config"])
-        except (TypeError, ValueError, OverflowError, KeyError, IndexError):
-            return out
-        if not (np.isfinite(lo) and np.isfinite(hi)):
+        out.approach = ApproachProfile.of_record(data)
+        config = stored_config(data)
+        if config is None:
             return out
-        out.config = (lo, hi)
+        out.config = lo, _ = config
         out.engaged = data.get("engaged") is True
         raw = data.get("samples")
         rows = raw if isinstance(raw, list) else []
@@ -776,6 +778,18 @@ def floor_in_force_kw(draw: DrawRange) -> float:
     return cfg_min if draw.floor_kw is None else draw.floor_kw
 
 
+def at_running_floor(draw: DrawRange, drawn_kw: float | None) -> bool:
+    """Whether an experiment's draw sat at the running floor in force (D2-s3-09).
+
+    Within ``AGREE_TOLERANCE`` above :func:`floor_in_force_kw`, or under it:
+    the house's load was below the pump's minimum, so the compressor ran its
+    floor whatever the ceiling set-point asked, and the draw says nothing of
+    the top. Stored as one, it narrowed the band every solve books.
+    """
+    floor = floor_in_force_kw(draw)
+    return drawn_kw is not None and floor > 0.0 and drawn_kw <= (1.0 + AGREE_TOLERANCE) * floor
+
+
 def floor_evidence(draw: DrawRange) -> tuple[float | None, int]:
     """``(low end, pairs)`` of the runs asked at the floor in force since it
     last moved (``floor_since``): asks within ``AGREE_TOLERANCE`` of it.
@@ -856,7 +870,8 @@ def fold(
     distorted: bool,
     defrost: bool,
     command: Any = None,
-    experiment_s: float | None = None,
+    ceiling_frozen: bool = False,
+    span: Span | None = None,
 ) -> None:
     """Fold one interval into ``draw`` when it is a running sample.
 
@@ -867,17 +882,54 @@ def fold(
     ``ceiling_c``), or ``None`` where nothing commands the draw. An interval
     held at the gate with no hot water asked is an idle reading.
 
-    ``experiment_s`` is the interval's start, epoch seconds, where the
-    system-identification experiment commanded it -- the mode the interval's
-    own action carried, captured beside its split and command, never the
-    action adopted since -- else ``None``. Such an interval that
+    ``span.experiment``: the system-identification experiment commanded the
+    interval -- the mode the interval's own action carried, captured beside
+    its split and command, never the action adopted since; its start keys the
+    ceiling store's sample. Such an interval that
     ``takes_ceiling`` goes to the ceiling store and NOT to the window, so no
     experiment's draw can trip the window's latch; every other interval
-    folds into the window as before.
+    folds into the window as before. ``ceiling_frozen`` refuses that store
+    sample alone (D2-s3-09, :func:`at_running_floor`): it is dropped, never
+    handed to the window either.
 
     First, whatever this interval: the map runs closed since the last fold
     become rows (``MapRows.commit_runs``) unless ``frozen`` or ``distorted``;
-    they never reach the window.
+    they never reach the window. Then, given a ``span`` (the interval's start
+    and end, epoch seconds), the approach learner folds it
+    (:func:`note_approach`). A wind-down is no idle reading. A sample inside
+    the learned approach adds no pair to the window, where it would read as a
+    pump that ignores its ask. A ``span.charged`` interval (a dwell that
+    saw hot water) moves only the approach's run clock: a charge before a space
+    run leaves the run an entry.
+    """
+    if span is not None and span.charged:
+        note_approach(draw, None, split, params, span, sample=False)
+        return
+    experiment_s = span.start_s if span is not None and span.experiment else None
+    kind = None if span is None else note_approach(
+        draw, drawn_kw, split, params, span,
+        sample=is_running_space(drawn_kw, *split, frozen=frozen, distorted=distorted, defrost=defrost) or not (frozen or distorted or defrost))
+    _fold_window(
+        draw, None if kind else drawn_kw, split, params, frozen=frozen, distorted=distorted, defrost=defrost,
+        command=command, experiment_s=experiment_s, ceiling_frozen=ceiling_frozen)
+
+
+def _fold_window(
+    draw: DrawRange,
+    drawn_kw: float | None,
+    split: tuple[float, float],
+    params: Any,
+    *,
+    frozen: bool,
+    distorted: bool,
+    defrost: bool,
+    command: Any = None,
+    experiment_s: float | None = None,
+    ceiling_frozen: bool = False,
+) -> None:
+    """:func:`fold`'s window, idle and ceiling arms (``drawn_kw`` ``None``
+    after the approach took the interval): the interval as a running sample,
+    an idle reading, or a ceiling-store sample.
     """
     space, dhw = split
     draw.map.commit_runs(keep=not (frozen or distorted))
@@ -888,7 +940,8 @@ def fold(
     ):
         return
     if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):
-        draw.observe_ceiling(drawn_kw, experiment_s)
+        if not ceiling_frozen:
+            draw.observe_ceiling(drawn_kw, experiment_s)
     else:
         draw.observe(
             drawn_kw, space, params.min_electrical_power, params.max_electrical_power,
@@ -896,6 +949,86 @@ def fold(
         )
 
 
+class Span(NamedTuple):
+    """One settled interval for :func:`fold`: its start and end, epoch
+    seconds, and whether its dwell saw hot water."""
+
+    start_s: float
+    end_s: float
+    charged: bool = False
+    #: The system-identification experiment commanded it (``fold``'s ceiling arm).
+    experiment: bool = False
+
+
+def inside_approach(draw: DrawRange | None) -> float | None:
+    """The draw :func:`expect` expected of the interval in hand where it sits
+    inside a run's learned approach, kW, else ``None``."""
+    return None if draw is None else draw.approach.expected_kw
+
+
+def approach_floor_kw(draw: DrawRange, params: Any) -> float:
+    """The floor an approach is read against: the learned floor where set,
+    else the live configured minimum (the window may be keyed to none yet)."""
+    return float(params.min_electrical_power) if draw.floor_kw is None else draw.floor_kw
+
+
+def note_approach(
+    draw: DrawRange, drawn_kw: float | None, split: tuple[float, float], params: Any,
+    span: Span | tuple[float, float], *, sample: bool,
+) -> str | None:
+    """Fold one interval into the approach learner and move its run clock:
+    ``"ramp"`` for a wind-down sample, ``"inside"`` for an entry sample at an
+    age the learned profile still covers, else ``None``. Every paired interval
+    comes here, a hot-water one with ``drawn_kw`` ``None``, so a charge before
+    a space run leaves the run an entry."""
+    floor = approach_floor_kw(draw, params)
+    configured = (float(params.min_electrical_power), float(params.max_electrical_power))
+    return draw.approach.observe(
+        drawn_kw, split, floor, span[0], span[1], sample=sample, standby_kw=RUNNING_FLOOR_KW,
+        tolerance=AGREE_TOLERANCE, config=configured,
+    )
+
+
+def solve_approach(draw: DrawRange | None, params: Any, now_s: float) -> runs.Approach | None:
+    """The learned approach a solve at ``now_s`` reads (``runs.received``),
+    or ``None``: no evidence above the floor, or evidence keyed to another
+    configured range."""
+    if draw is None or draw.approach.config != (float(params.min_electrical_power), float(params.max_electrical_power)):
+        return None
+    floor = approach_floor_kw(draw, params)
+    entry = entry_levels(draw.approach, floor, AGREE_TOLERANCE)
+    ramp = ramp_levels(draw.approach, floor, AGREE_TOLERANCE)
+    if entry.size == 0 and ramp.size == 0:
+        return None
+    return runs.Approach(entry, ramp, draw.approach.age_h(now_s), BIN_MIN / 60.0)
+
+
+def expect(
+    draw: DrawRange, split: tuple[float, float], params: Any, now_s: float, dt_h: float,
+) -> float:
+    """The draw the plan expects of the meter over the live step, kW: the
+    shipped total plus the learned approach's excess at the live age
+    (``runs.received`` on that step); with none, the shipped total. Kept on
+    the profile while the step sits inside the approach, for the interval's
+    readers when it settles (:func:`inside_approach`)."""
+    space, dhw = split
+    got = runs.received(
+        np.array([float(space)]), dhw, solve_approach(draw, params, now_s),
+        dt=dt_h, p_max=params.max_electrical_power)
+    excess = float(got[0]) - float(space)
+    total = float(space) + float(dhw) + excess
+    return draw.approach.expect(total, inside=excess > 0.0)
+
+
+def received_schedule(draw: DrawRange | None, params: Any, space: Any, dhw: Any, now: Any, dt_h: float) -> Any:
+    """A published space schedule as the pump draws it (``runs.received``):
+    the array the objective costed, for a reader that prices or compares it.
+    ``now``: the solve's time, a timezone-aware datetime."""
+    if not space:
+        return space
+    return runs.received(np.asarray(space, dtype=float), np.asarray(dhw if dhw else 0.0, dtype=float), solve_approach(draw, params, now.timestamp()), dt=dt_h, p_max=params.max_electrical_power)
+
+
 def planned_range(
     draw: DrawRange, params: Any, cap: InstallCapability
 ) -> tuple[float, float] | None:
@@ -965,6 +1098,9 @@ class SolveBand:
     min_reason: str = "awaiting"
     learned_min_kw: float | None = None
     min_samples: int = 0
+    #: The learned approach's entry energy above the floor this solve booked
+    #: per run out of a pause, kWh (``solve_approach``), or ``None``.
+    approach_kwh: float | None = None
 
     def as_dict(self) -> dict[str, Any]:
         return {
@@ -981,6 +1117,7 @@ class SolveBand:
             "min_reason": self.min_reason,
             "learned_min_kw": None if self.learned_min_kw is None else round(self.learned_min_kw, 3),
             "min_samples": self.min_samples,
+            "approach_kwh": None if self.approach_kwh is None else round(self.approach_kwh, 3),
         }
 
 
@@ -1009,6 +1146,8 @@ def solve_band(
     samples = len(draw.ceiling)
     bottom = _bottom_fields(draw, cfg_min, cfg_max, cap.plan_writes_power(), applies_floor)
     floor = bottom["learned_min_kw"] if bottom["min_source"] == "metered" else None
+    entry = solve_approach(draw, params, now_s)
+    bottom["approach_kwh"] = None if entry is None else entry.entry_kwh(approach_floor_kw(draw, params))
 
     def band(top: float, source: str, reason: str, learned: float | None = None) -> SolveBand:
         min_kw = cfg_min if floor is None and source == "configured" else min(floor or cfg_min, top)
diff --git a/custom_components/heatpump_optimizer/heat_energy.py b/custom_components/heatpump_optimizer/heat_energy.py
index f1a6fec074..9482f91fbe 100644
--- a/custom_components/heatpump_optimizer/heat_energy.py
+++ b/custom_components/heatpump_optimizer/heat_energy.py
@@ -60,6 +60,11 @@ SPAN_REFUSED_RESET = "counter_reset"
 SPAN_REFUSED_ROLLOVER = "counter_rollover"
 SPAN_REFUSED_RESOLUTION = "counter_resolution"
 SPAN_REFUSED_LONG = "span_too_long"
+#: An interval's tank rise past which a space-only, unobserved interval was a
+#: charge the plan did not ask for (#3760, D12-s3-03). Over a tank probe's
+#: quantisation and stratification wobble (a few tenths), under one charging
+#: cycle's rise (a 6 kW pump into 200 L lifts it about 6 K in 15 minutes).
+UNPLANNED_CHARGE_RISE_K = 1.0
 
 
 def _after(newer: datetime, older: datetime) -> bool:
@@ -279,6 +284,20 @@ def dhw_share(a: Attribution) -> float:
     return a.dhw / total if total > 1e-6 else 0.0
 
 
+def unplanned_charge(a: Attribution, tank_rise_k: float | None) -> bool:
+    """Whether an interval was a hot-water charge its plan split never asked for.
+
+    Unobserved (no dwell saw the duty), planned as space alone -- the
+    whole-unit rule :func:`space_heat_kw` applies -- and the tank thermometer
+    rose past :data:`UNPLANNED_CHARGE_RISE_K` over it. No reading, or no
+    tank thermometer, reads ``False``: the plan split stands, as before.
+    """
+    return (
+        not a.observed and a.dhw <= 0.0 < a.space
+        and tank_rise_k is not None and tank_rise_k > UNPLANNED_CHARGE_RISE_K
+    )
+
+
 class SpanEvidence(NamedTuple):
     """What a span hands its learners at its close: its energy, or why it was refused."""
 
@@ -292,6 +311,8 @@ class SpanEvidence(NamedTuple):
     #: The plan's ``(space, hot water)`` commanded kWh over the span.
     plan_kwh: tuple[float, float]
     attribution: Attribution
+    #: The tank's rise from the span's opening read to its close, or ``None``.
+    tank_rise_k: float | None = None
 
 
 class SpanHeat(NamedTuple):
@@ -358,6 +379,8 @@ class SpanClose(NamedTuple):
     lower: bool
     house: bool
     cop: bool
+    #: The span was a charge its plan never asked for (:func:`unplanned_charge`).
+    unplanned_charge: bool = False
 
 
 #: No span closed or was refused this cycle: no learner is reached.
@@ -388,6 +411,11 @@ class HeatEnergyMeter:
     _dhw_seen: bool = False
     _clean: dict[str, bool] = field(default_factory=dict)
     _plan: tuple[float, float] = (0.0, 0.0)
+    #: The tank thermometer at the previous and this cycle's reads, and at the
+    #: open span's opening read: runtime only, the evidence of
+    #: :func:`unplanned_charge`.
+    tank_c: tuple[float | None, float | None] = (None, None)
+    _span_tank_c: float | None = None
 
     def observe_mode(
         self, at: datetime, mode_key: str | None, live: bool, changed_at: datetime | None
@@ -397,7 +425,7 @@ class HeatEnergyMeter:
 
     def observe_cycle(
         self, at: datetime, signals: Any, heat: Any, elec_kwh: float | None, cadence_min: float,
-        bounds_h: tuple[float, float], params: Any,
+        bounds_h: tuple[float, float], params: Any, tank_c: float | None = None,
     ) -> None:
         """This cycle's mode and counter reads (#2261), as the coordinator holds them.
 
@@ -406,8 +434,10 @@ class HeatEnergyMeter:
         value only when it read, configured when it names an entity),
         ``cadence_min`` the optimization interval in minutes, ``bounds_h`` the
         interval learners' sample bounds and ``params`` the thermal parameters
-        whose nameplate heat bounds a rollover.
+        whose nameplate heat bounds a rollover; ``tank_c`` the tank
+        thermometer's usable reading, or ``None``.
         """
+        self.tank_c = (self.tank_c[1], tank_c)
         self.observe_mode(at, signals.mode.key, signals.mode_live, signals.mode_changed_at)
         self.observe_counters(
             at, heat.value if heat.ok else None, elec_kwh, configured=bool(heat.entity_id),
@@ -415,6 +445,28 @@ class HeatEnergyMeter:
             max_heat_kw=params.max_electrical_power * params.cop_nominal_floored,
         )
 
+    def unplanned_charge(self, plan_split: tuple[float, float]) -> bool:
+        """This cycle's interval, on ``plan_split``, was a charge the plan never asked for."""
+        prev, now = self.tank_c
+        rise = None if prev is None or now is None else now - prev
+        return unplanned_charge(self.attribution(plan_split), rise)
+
+    def booked_dhw_share(self, plan_split: tuple[float, float]) -> float:
+        """Hot water's share of this cycle's metered energy: all of it on an unplanned charge."""
+        if self.unplanned_charge(plan_split):
+            return 1.0
+        return dhw_share(self.attribution(plan_split))
+
+    def served_space_alone(self, plan_split: tuple[float, float] | None) -> bool:
+        """This cycle's interval heated the house alone: the whole-unit rule, never an unplanned charge.
+
+        Its attribution on ``plan_split`` (the dwell's where observed); no split is no answer, ``False``.
+        """
+        if plan_split is None:
+            return False
+        a = self.attribution(plan_split)
+        return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)
+
     def attribution(self, plan_split: tuple[float, float]) -> Attribution:
         """This cycle's interval, split by the dwell where observed, else by ``plan_split``."""
         return attribution(self.dwell.shares(*self.cycle), plan_split)
@@ -505,9 +557,13 @@ class HeatEnergyMeter:
         if (self.closed is not None or self.refusal is not None) and self._anchor is not None:
             e = self.closed
             shares = self.dwell.shares(e.start, e.end) if e is not None else None
+            now_c = self.tank_c[1]
             out = SpanEvidence(
-                e, self.refusal, *self._anchor, self._clean, self._plan, attribution(shares, self._plan)
+                e, self.refusal, *self._anchor, self._clean, self._plan, attribution(shares, self._plan),
+                None if now_c is None or self._span_tank_c is None else now_c - self._span_tank_c,
             )
+        if self._opened:
+            self._span_tank_c = self.tank_c[1]
         if self._opened and anchor[1] is not None:
             self._anchor, self._clean, self._plan = (anchor[0], anchor[1]), {}, (0.0, 0.0)
         elif self._opened:
@@ -571,7 +627,7 @@ def close_span(
         interval, got.space_kw, got.asked_kw, got.heat_kw, 0.0 if got.elec_kw is None else got.elec_kw,
         got.refusal or (unaligned if got.elec_kw is None else None), (got.heat_kw, ev.attribution),
         interval is not None and bool(ev.clean.get("lower")), interval is not None and bool(ev.clean.get("house")),
-        bool(ev.clean.get("cop")) or e is None,
+        bool(ev.clean.get("cop")) or e is None, unplanned_charge(ev.attribution, ev.tank_rise_k),
     )
     log_close(ev, close)
     return close
diff --git a/custom_components/heatpump_optimizer/learning_freeze.py b/custom_components/heatpump_optimizer/learning_freeze.py
new file mode 100644
index 0000000000..982f0615ee
--- /dev/null
+++ b/custom_components/heatpump_optimizer/learning_freeze.py
@@ -0,0 +1,200 @@
+"""Which interval a learner may ingest: the one freeze predicate (ADR-008).
+
+Pure: the coordinator builds :class:`Facts` once per ask from the cycle's
+own state, the module owning each piece of local evidence computes it into
+:class:`Evidence`, and :func:`reason` answers. No learner holds a facts
+value; a learner states only which kind of sample it folds (:class:`Sample`).
+
+Fail closed. A learner that pauses for an hour loses an hour of
+convergence; a learner that trains on a flatline or on heat it did not
+supply corrupts a parameter that is persisted to disk.
+
+The order is the root-cause order: a reason earlier in :func:`reason`
+outranks every later one, so the reason reported is the one a user should
+look at first. Reason strings are displayed (``learner_progress.pauses``,
+the freeze notes) and are kept verbatim.
+"""
+
+from __future__ import annotations
+
+import enum
+from collections.abc import Callable, Mapping
+from dataclasses import dataclass, field
+
+REASON_EXTERNAL_HEAT = "external_heat_source"
+REASON_DEFROSTING = "defrosting"
+REASON_VENTILATION = "ventilation"
+REASON_AWAY = "away"
+REASON_AWAY_RECOVERY = "away_recovery"
+REASON_UNPLANNED_CHARGE = "unplanned_charge"
+REASON_AT_RUNNING_FLOOR = "at_running_floor"
+REASON_CHARGE_OPEN = "charge_open"
+REASON_ASK_IGNORED = "ask_ignored"
+
+
+class Sample(enum.Enum):
+    """The kind of sample a learner folds; it decides which reasons refuse it."""
+
+    #: a plant reading with no room air in it (tank standby, buffer, COP)
+    PLANT = "plant"
+    #: a room-air reading (the fabric learners)
+    ROOM_AIR = "room_air"
+    #: a property of the occupied house (internal gains, the quiet-comfort evidence)
+    OCCUPANCY = "occupancy"
+    #: the comfort a resident reads (the curve learner)
+    COMFORT = "comfort"
+    #: heat the plan put into space heating, attributed by its split
+    SPACE_HEAT = "space_heat"
+    #: the same, on metered heat: no room air in the sample (R10-COP-GATE item E)
+    METERED_SPACE_HEAT = "metered_space_heat"
+    #: a running-draw ceiling sample of a draw-range experiment
+    CEILING = "ceiling"
+    #: the tank's draws and usage hours (no room air; occupied)
+    TANK_DRAW = "tank_draw"
+    #: the defrost derate's delivered-over-asked ratio
+    DELIVERED_RATIO = "delivered_ratio"
+
+
+#: Kinds the open-window detector refuses: every one with room air in it.
+_ROOM_AIR_KINDS = frozenset(
+    {Sample.ROOM_AIR, Sample.OCCUPANCY, Sample.COMFORT, Sample.SPACE_HEAT, Sample.CEILING}
+)
+#: Kinds an away period falsifies: the occupancy-borne ones.
+_AWAY_KINDS = frozenset({Sample.OCCUPANCY, Sample.COMFORT, Sample.TANK_DRAW})
+
+
+@dataclass(frozen=True)
+class Facts:
+    """The cycle's plant-wide facts, built by the coordinator per ask."""
+
+    external_heat: bool = False
+    #: ``PumpSignals.freeze_reason``: online, fault, cooling mode
+    signals: str | None = None
+    defrosting: bool = False
+    #: configured readings that are unusable: key -> problem
+    unusable: Mapping[str, str] = field(default_factory=dict)
+    ventilation: bool = False
+    #: the boost freeze's reason while it holds, else None
+    boost: str | None = None
+    #: the early cut, the supply hold or the unmetered power (``_tail_freeze``)
+    tail: str | None = None
+    away: bool = False
+    away_recovery: bool = False
+
+
+@dataclass(frozen=True)
+class Evidence:
+    """The interval's local evidence, each field computed by the module holding its inputs."""
+
+    #: ``heat_energy``: an unobserved interval the plan put no hot water in, over which the tank rose
+    unplanned_charge: bool = False
+    #: ``draw_range``: the experiment's draw sat at the running floor in force
+    at_running_floor: bool = False
+    #: ``dhw_learning``: the interval starts or ends on a heated sample of an open charge
+    charge_open: bool = False
+    #: ``accuracy``: ``MeasuredCop.scale_response`` reads the ask ignored
+    ask_ignored: bool = False
+
+
+NO_EVIDENCE = Evidence()
+
+
+def space_heat(metered: bool) -> Sample:
+    """The space-heat kind of a sample whose heat is ``metered``, or inferred from the room."""
+    return Sample.METERED_SPACE_HEAT if metered else Sample.SPACE_HEAT
+
+
+#: The additive reasons, after the shared ones and in this order: each with
+#: the kinds it refuses and the fact or evidence that raises it. An away
+#: setback sits below the floor the curve tracker reads and the recovery
+#: climbs back through it, so the recovery refuses the comfort kind alone.
+_ADDITIVE: tuple[tuple[str, frozenset[Sample], Callable[[Facts, Evidence], bool]], ...] = (
+    (REASON_AWAY, _AWAY_KINDS, lambda f, e: f.away),
+    (REASON_AWAY_RECOVERY, frozenset({Sample.COMFORT}), lambda f, e: f.away_recovery),
+    (REASON_UNPLANNED_CHARGE, frozenset({Sample.SPACE_HEAT, Sample.METERED_SPACE_HEAT}),
+     lambda f, e: e.unplanned_charge),
+    (REASON_AT_RUNNING_FLOOR, frozenset({Sample.CEILING}), lambda f, e: e.at_running_floor),
+    (REASON_CHARGE_OPEN, frozenset({Sample.TANK_DRAW}), lambda f, e: e.charge_open),
+    (REASON_ASK_IGNORED, frozenset({Sample.DELIVERED_RATIO}), lambda f, e: e.ask_ignored),
+)
+
+
+def reason(
+    facts: Facts, keys: tuple[str, ...], sample: Sample, evidence: Evidence = NO_EVIDENCE
+) -> str | None:
+    """Why a ``sample`` over ``keys`` must not be folded this interval, or ``None``.
+
+    The delivered ratio answers its own reason alone (#944): the caller's
+    power gate owns the shared reasons and exempts ``defrosting``, the
+    derate's own input.
+    """
+    if sample is not Sample.DELIVERED_RATIO:
+        shared = _shared(facts, keys, sample)
+        if shared is not None:
+            return shared
+    return next(
+        (why for why, kinds, raised in _ADDITIVE if sample in kinds and raised(facts, evidence)),
+        None,
+    )
+
+
+def _shared(facts: Facts, keys: tuple[str, ...], sample: Sample) -> str | None:
+    """The nine reasons every kind but the delivered ratio answers, in today's order."""
+    if facts.external_heat:
+        return REASON_EXTERNAL_HEAT
+    # v5.3.0: the plant-wide freezes, from the heat pump's own signals.
+    # They have a shape the key loop below cannot express: that loop asks
+    # "is the reading the caller named unusable" and freezes on the
+    # *absence* of a measurement, while these freeze on the *presence*
+    # of one -- the online flag says False, the fault flag says True,
+    # the mode says cooling. Each is a healthy, fresh reading that
+    # happens to be bad news and makes the whole interval misleading
+    # rather than one sensor unreadable, so they are not scoped to the
+    # caller's keys either, and they sit ahead of the key loop as the
+    # root cause when both fire: reporting the symptom would send a
+    # user looking at the wrong thing. See ``pump_signals.py`` for why
+    # the absence of these signals never freezes anything.
+    if facts.signals is not None:
+        return facts.signals
+    # #944 (round-4 D7-03): a fourth presence condition, kept out of
+    # ``freeze_reason`` because the derate still folds these intervals
+    # (the settlement exempts the reason it causes). A defrost reverses
+    # the cycle -- the interval's heat is negative while the learners
+    # replay the commanded power as if it had flowed -- and happens
+    # below the frost band too, where the COP learner's guard ends.
+    if facts.defrosting:
+        return REASON_DEFROSTING
+    # An unusable input outranks ventilation deliberately: the heat-loss
+    # learner treats "ventilation" as a pass-through to keep feeding
+    # the detector, and a flatline fed through that pass would
+    # drive the very detector that froze everything. With the input
+    # check first, the latch simply holds until real data returns.
+    #
+    # v5.1.3: freeze on ANY unusable reading, not only ``stale``.
+    # ``_update_current_state`` deliberately PINS the last good value when
+    # a read fails: right for the *input*, fatal for a *learner*, which
+    # then reads a frozen number as thermal behaviour and persists it (a
+    # dropped Zigbee sensor walked the house heat-loss scale from 1.0 to
+    # ~0.37 inside 48 h). The coordinator lists a reading here only when it
+    # has an entity: a slot the user never configured reads
+    # ``not_configured`` with none and must NOT freeze learning.
+    for key in keys:
+        problem = facts.unusable.get(key)
+        if problem is not None:
+            return f"{problem}:{key}"
+    # #26: training on an open window teaches a phantom heat loss the
+    # house does not have -- measured in degC-scale residuals, far above
+    # any learning signal. A sample with no room air in it is untouched.
+    if sample in _ROOM_AIR_KINDS and facts.ventilation:
+        return REASON_VENTILATION
+    # #1935: boost space heating -- either surface -- actuates heat the
+    # plan's trajectory never assumed, so every residual is warm-side
+    # garbage. Ranked below "ventilation" deliberately: that is the one
+    # reason the heat-loss learner looks past (its pass-through feeds the
+    # window CUSUM), and a boost window must not starve the detector.
+    if facts.boost is not None:
+        return facts.boost
+    # The early cut, then the held supply write, then the unmetered power
+    # (``coordinator._tail_freeze``): each an interval that did not run the
+    # commanded power.
+    return facts.tail
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 148e16c04a..88a90401ce 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -62,6 +62,7 @@ from .const import (
     WOOD_TANK_MAX_TEMP,
 )
 from .batchmath import row_sums
+from .dhw_charges import ChargeRuns
 from .dhw_planner import DhwPlanner
 from .drift import utc_step_starts
 from .entry_config import EntryConfig
@@ -202,6 +203,14 @@ def _engaged(opt: HeatPumpOptimizer) -> bool:
     return opt.config.start_price > 0 or opt.config.clamp_planned_levels
 
 
+def _charge_runs(opt: HeatPumpOptimizer, running: bool) -> ChargeRuns | None:
+    """What an engaged solve hands the hot-water planner so its charges ship
+    as runs too (``dhw_charges.commit_charges``); ``None`` unengaged."""
+    if not _engaged(opt):
+        return None
+    return ChargeRuns(opt.config.start_price, running, opt.config.clamp_planned_levels)
+
+
 #: The objectives a multi-start descends on in place of the true one
 #: (:func:`_descent_pair`): without the start term, and without the
 #: duty-switch term as well.
@@ -329,9 +338,11 @@ def _shipped_and_received(
 ) -> tuple[np.ndarray, np.ndarray | None, np.ndarray]:
     """The level each circuit ships at, and the space draw the house receives.
 
-    The two differ only where a priced stop keeps the compressor off for part
-    of a step (``duty_legs.delivered_space``); with no availability vector the
-    received draw is the shipped array itself, the same object. Space is
+    The two differ where a run's first steps or a pause's draw the learned
+    approach (``runs.received``, true objective only). They differ too where a
+    priced stop then keeps the compressor off for part of a step
+    (``duty_legs.delivered_space``). With neither, the received draw is the
+    shipped array itself, the same object. Space is
     scored as it stands, and what stands is a committed plan
     (:func:`_commit_runs`); hot water is its planner's, so a clamped install's
     ships as its projection, which a descent leaves out.
@@ -339,9 +350,11 @@ def _shipped_and_received(
     if dhw is not None and opt.config.clamp_planned_levels and not descent:
         dhw = project_planned_levels(
             dhw, opt.model.params.min_electrical_power, opt.model.params.max_electrical_power)
+    received = space if descent else runs.received(space, 0.0 if dhw is None else dhw, opt._approach, dt=opt.config.dt_hours, p_max=opt.model.params.max_electrical_power)
     if avail is None or dhw is None:
-        return space, dhw, space
-    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))
+        return space, dhw, received
+    return space, dhw, duty_legs.delivered_space(received, dhw, avail, _duty_floor(opt))
+
 
 
 def _switch_cost_fn(
@@ -540,7 +553,7 @@ def _run_plans(
     heats = (hi >= floor) & ((other <= 0.0) | (space >= floor / 2.0))
     masks = runs.candidates(
         space + other, h.prices, floor, hi + other, opt.config.start_price,
-        dt=h.dt, running=h.compressor_running,
+        dt=h.dt, running=h.compressor_running, entry_kwh=0.0 if opt._approach is None else opt._approach.entry_kwh(floor),
         forced=np.where((other > 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),
     )
     idle = np.where(cycled, space, lo)
@@ -2033,6 +2046,10 @@ def _combi_dhw_exo(
 #: (the `exchange` harness arm in dev/audit/harnesses/r10_combi_tank.py
 #: prints the rounds a plan takes).
 _COMBI_EXCHANGE_ROUNDS = 4
+#: How much further under the requirement the committed plan's store may
+#: fall than the exchange's own plan and still ship, K: the planners'
+#: shortfall tolerance.
+_COMBI_COMMIT_SLACK_K = 0.05
 
 
 def _combi_flux_exchange(
@@ -2048,23 +2065,51 @@ def _combi_flux_exchange(
     A feasibility repair, never a scored candidate: the first plan's store
     breaches the hot-water floor the space side drains, so its score bounds
     nothing, and a space re-solve would draw the repair straight back out.
+
+    The rounds exchange uncommitted plans, whose levels move with the flux,
+    from a planner handed no runs to commit. On a solve that plans runs, one
+    more build on the settled flux commits the charges
+    (``dhw_charges.commit_charges``), and is kept only where the
+    store, walked under the flux the committed plan itself leaves, falls no
+    further under the requirement than the last round's plan did.
     """
     model, store = opt.model, opt.model.params.dhw_store
     weather = WeatherSeries.from_horizon(h)
-    space_net = None
-    for _ in range(_COMBI_EXCHANGE_ROUNDS):
-        dhw_exo = _combi_dhw_exo(model, h, dhw_power, draw_rates, space_net)
+
+    def net_under(schedule: np.ndarray, prior: np.ndarray | None) -> np.ndarray:
+        """The space side's net flux into the store beside ``schedule``."""
+        dhw_exo = _combi_dhw_exo(model, h, schedule, draw_rates, prior)
         buffer_temps = model.simulate_trajectory(
             initial_state=h.initial_state, power_schedule=space_power,
             weather=_with_buffer_exo(weather, dhw_exo), dt_hours=h.dt,
             valve_targets=h.valve_targets, start_hour=float(h.step_hours[0]))[4]
-        space_net = combi_space_net_kw(store, buffer_temps, dhw_exo, h.dt)
-        plan, opt._dhw_requirement = _dhw_build(
-            planner, h, p_max, space_demand=space_power, tank_exo_kw=space_net)
-        if np.allclose(plan.schedule, dhw_power, atol=1e-4):
+        return combi_space_net_kw(store, buffer_temps, dhw_exo, h.dt)
+
+    def build(by: DhwPlanner, space_net: np.ndarray) -> np.ndarray:
+        plan, opt._dhw_requirement = _dhw_build(by, h, p_max, space_demand=space_power, tank_exo_kw=space_net)
+        return np.asarray(plan.schedule)
+
+    levels = DhwPlanner(opt.model, opt.config, opt._pv_surplus, opt._price_known)
+    space_net = None
+    for _ in range(_COMBI_EXCHANGE_ROUNDS):
+        space_net = net_under(dhw_power, space_net)
+        plan = build(levels, space_net)
+        if np.allclose(plan, dhw_power, atol=1e-4):
             break
-        dhw_power = plan.schedule
-    return dhw_power
+        dhw_power = plan
+    if planner.charge_runs is None or space_net is None:
+        return dhw_power
+    committed = build(planner, space_net)
+
+    def short(schedule: np.ndarray, net: np.ndarray) -> float:
+        """How far the store falls under the requirement at worst, K."""
+        gaps = planner._dhw_shortfall(
+            None, schedule, float(h.initial_state.dhw_temperature), h.outdoor_temps, draw_rates,
+            h.dt, h.humidity, np.asarray(opt._dhw_requirement), set(), net)[1]
+        return float(np.max(gaps))
+
+    kept = short(committed, net_under(committed, space_net)) <= short(dhw_power, space_net) + _COMBI_COMMIT_SLACK_K
+    return committed if kept else dhw_power
 
 
 def _price_guess_weights(prices: np.ndarray) -> np.ndarray:
@@ -3143,6 +3188,7 @@ class SolveInputs:
     #: The compressor runs at solve time: a run that continues from it is no
     #: start, in the start term and in the published count alike.
     compressor_running: bool = False
+    approach: runs.Approach | None = None  # a run's learned first steps, read as received draw
 
 
 def _horizon_weather(series: ForecastSeries, n_steps: int) -> WeatherSeries:
@@ -3491,6 +3537,7 @@ class HeatPumpOptimizer:
         #: The ``duty_legs.availability`` vector the last space solve scored
         #: with, riding beside its plan; ``None`` when no stop is charged.
         self._space_avail: np.ndarray | None = None
+        self._approach: runs.Approach | None = None
         #: The solve's starting buffer temperature; floors the settlement
         #: value cap so pre-stored heat cannot be drained for free.
         self._initial_buffer_temp: float | None = None
@@ -4378,18 +4425,12 @@ class HeatPumpOptimizer:
         # Only reduce slab pre-heating, not immediate comfort heating
         solar_reduction = 1.0 - 0.4 * solar_fraction  # max 40% reduction
 
-        # --- Wind analysis ---
-        # Look at future wind speeds and compute anticipated heat loss increase
-        wind_weights = np.exp(-np.arange(n) * dt_hours / 12.0)  # decay over 12h
-        wind_weights /= wind_weights.sum()
-        avg_future_wind = float(np.sum(wind_speeds * wind_weights))
+        # --- Wind and rain: upcoming, weighted by a 12 h decay, raise heat loss ---
+        future_weights = np.exp(-np.arange(n) * dt_hours / 12.0)
+        future_weights /= future_weights.sum()
+        avg_future_wind = float(np.sum(wind_speeds * future_weights))
         wind_anticipation = 1.0 + self.model.params.wind_sensitivity * avg_future_wind
-
-        # --- Rain analysis ---
-        # Upcoming rain increases heat loss
-        rain_weights = np.exp(-np.arange(n) * dt_hours / 12.0)
-        rain_weights /= rain_weights.sum()
-        avg_future_precip = float(np.sum(precipitation * rain_weights))
+        avg_future_precip = float(np.sum(precipitation * future_weights))
         rain_anticipation = 1.0
         if avg_future_precip > 0.1:
             rain_intensity = min(avg_future_precip / 2.0, 1.0)
@@ -4493,8 +4534,7 @@ class HeatPumpOptimizer:
         )
         # One hot-water planner per solve, from this solve's inputs (#1743).
         planner = DhwPlanner(
-            self.model, self.config, self._pv_surplus, self._price_known
-        )
+            self.model, self.config, self._pv_surplus, self._price_known, _charge_runs(self, inputs.compressor_running))
 
         # --- Analyze forecast trajectory for predictive signals ---
         forecast_analysis = self._analyze_forecast_trajectory(
@@ -4618,6 +4658,7 @@ class HeatPumpOptimizer:
         # #1295: the plan the caller hands in -- the coordinator seeds it from
         # the last shipped plan -- is one extra candidate on the FIRST solve
         # only; ``_warm_start_starts`` says why later solves get none.
+        self._approach = inputs.approach
         result = _solve(self._warm_start_starts(n_steps))
 
         # A blocked channel is withheld from the release loop entirely. Its
@@ -5468,7 +5509,7 @@ class HeatPumpOptimizer:
 
             # Electricity cost, piecewise in PV surplus. ``float()`` is
             # identity on the 1-D branch's return and states it.
-            drawn = combined if heat_power is space_power else heat_power + dhw_plan_power
+            drawn = combined if heat_power is space_power else heat_power + (0.0 if dhw_plan_power is None else dhw_plan_power)
             energy_cost = (
                 float(energy_cost_of(drawn)) * self.config.price_weight
             )
@@ -5534,7 +5575,7 @@ class HeatPumpOptimizer:
             )
             return self._cost_terms_batch(
                 traj,
-                grid_power if heat_matrix is space_matrix else heat_matrix + dhw_plan_power,
+                grid_power if heat_matrix is space_matrix else heat_matrix + (0.0 if dhw_plan_power is None else dhw_plan_power),
                 level_cost=_with_switch_cost(
                     _with_switch_cost(capacity_batch(grid_power), start_cost(grid_power, descent)),
                     switch_cost(space_matrix, dhw_plan_power, descent)),
@@ -5665,7 +5706,7 @@ class HeatPumpOptimizer:
             optimal_power = initial_power
             status = f"failed ({e})"
 
-        # Simulate with optimal schedule
+        # Simulate with optimal schedule, as received (``_shipped_and_received``)
         (
             room_temps,
             slab_temps,
@@ -5674,7 +5715,7 @@ class HeatPumpOptimizer:
             buffer_temps,
             _,
             wood_temps,
-        ) = _space_traj(optimal_power)
+        ) = _space_traj(_shipped_and_received(self, optimal_power, None, None)[2])
         # The achieved objective, for candidate comparison across valve
         # schedules. One extra evaluation, robust on the failure path too.
         achieved_objective = float(objective(optimal_power))
@@ -5916,8 +5957,7 @@ class HeatPumpOptimizer:
         )
         # Received through the vector the adopted solve scored with, never a
         # rebuilt one; the schedule and the achieved objective keep the level.
-        heat_space = optimal_space if self._space_avail is None else duty_legs.delivered_space(
-            optimal_space, optimal_dhw, self._space_avail, _duty_floor(self))
+        heat_space = _shipped_and_received(self, optimal_space, optimal_dhw, self._space_avail)[2]
 
         # Simulate with optimal schedule
         published_end: list[ThermalState] = []
diff --git a/custom_components/heatpump_optimizer/room_history.py b/custom_components/heatpump_optimizer/room_history.py
index e17bd4593a..9d346ff0a3 100644
--- a/custom_components/heatpump_optimizer/room_history.py
+++ b/custom_components/heatpump_optimizer/room_history.py
@@ -65,13 +65,16 @@ FLAT_IQR = 0.25
 
 @dataclass(frozen=True)
 class House:
-    """The house values one cycle hands in; None where not measured."""
+    """The house values one cycle hands in; None where not measured.
+
+    ``space_alone``: the cycle's interval heated the house and nothing else, as
+    ``heat_energy.HeatEnergyMeter.served_space_alone`` answers it.
+    """
 
     outdoor_c: float | None
     floor_return_c: float | None
     measured_kw: float | None
-    space_kw: float
-    dhw_kw: float
+    space_alone: bool
 
 
 @dataclass
@@ -125,7 +128,7 @@ def _accumulate(period: Period, readings: Sequence[RoomReading], house: House) -
         period.floor_return = floor_return
     if (kw := _centi(house.measured_kw, "power")) is not None:
         period.power.append(kw)
-    period.space += house.space_kw > 0.0 and house.dhw_kw <= 0.0
+    period.space += house.space_alone
     period.cycles += 1
 
 
diff --git a/custom_components/heatpump_optimizer/runs.py b/custom_components/heatpump_optimizer/runs.py
index 049e4734de..d2c32e05c6 100644
--- a/custom_components/heatpump_optimizer/runs.py
+++ b/custom_components/heatpump_optimizer/runs.py
@@ -26,7 +26,7 @@ shortest run and pause.
 from __future__ import annotations
 
 from datetime import timedelta
-from typing import Any
+from typing import Any, Callable, NamedTuple
 
 import numpy as np
 
@@ -54,6 +54,40 @@ _TIE_BREAK = 1e-9
 #: Float slack on a level or an energy compared against the floor, kW or kWh.
 _SLACK = 1e-9
 
+class Start(NamedTuple):
+    """What a start costs :func:`commit`: its price, and the learned entry's
+    energy above the level a run out of a pause draws (:meth:`Approach.entry_kwh`)."""
+
+    cost: float
+    entry_kwh: float = 0.0
+
+
+class Approach(NamedTuple):
+    """The learned approach a plan's runs draw (``approach.entry_levels``,
+    ``approach.ramp_levels``): levels by ``bin_h`` bin after a space-run
+    entry and after a run's end, kW, and the live run's age at step 0, hours
+    (``ApproachProfile.age_h``: ``0.0`` with none live, ``None`` unknown)."""
+
+    entry: np.ndarray
+    ramp: np.ndarray
+    age_h: float | None
+    bin_h: float
+
+    def entry_kwh(self, level: float) -> float:
+        """The entry's energy above ``level``, kWh: what a run started from a
+        pause draws beyond its shipped level."""
+        return float(np.sum(np.maximum(self.entry - level, 0.0))) * self.bin_h
+
+
+#: One thing a step may do in a program: from the scalars of the cells it
+#: leaves, and whether those cells were running, to the scalars it arrives
+#: with and what it pays (infinite where it may not be done).
+Action = Callable[[np.ndarray, bool], tuple[np.ndarray, Any]]
+#: A program's cell rule: from arriving scalars, and whether they arrive in
+#: a run, to their cells and whatever arriving there costs besides (infinite
+#: where the scalar is out of bounds).
+CellRule = Callable[[np.ndarray, bool], tuple[np.ndarray, np.ndarray]]
+
 
 def floor_kw(floor: float) -> float:
     """The running floor a start is counted against, kW; a configured 0 still
@@ -99,6 +133,64 @@ def edge_count(total: Any, running: bool = False) -> int:
     return int(np.sum(on & ~np.r_[bool(running), on[:-1]]))
 
 
+def _mean_excess(levels: np.ndarray, bin_h: float, age_h: float, dt: float, shipped: float) -> float:
+    """The mean over ``[age_h, age_h + dt)`` of ``levels`` (one per ``bin_h``
+    bin, none past the last) above ``shipped``, kW."""
+    total = 0.0
+    for j in range(max(int(age_h // bin_h), 0), min(levels.size, int(np.ceil((age_h + dt) / bin_h)))):
+        overlap = min(age_h + dt, (j + 1) * bin_h) - max(age_h, j * bin_h)
+        if overlap > 0.0:
+            total += max(float(levels[j]) - shipped, 0.0) * overlap
+    return total / dt
+
+
+def received(space: Any, dhw: Any, approach: Approach | None, *, dt: float, p_max: float) -> Any:
+    """The space draw the pump takes for a shipped space plan, kW per step,
+    given the learned ``approach``. A ``[B, n]`` batch is read row by row, so
+    each row is the one-row answer bit for bit.
+
+    A space run is read off the space plan alone (``MIN_RUNNING_DRAW_KW``): a
+    charge beside a run is no entry, a charge before one leaves it one. A step
+    inside a run at age ``a`` takes the shipped level plus the mean of
+    ``approach.entry`` above it over ``[a, a + dt)``: ``max(shipped, entry)``
+    at bin resolution. A pause's steps after a run's end take
+    ``approach.ramp`` alike, and every other step the shipped level. What is added never
+    takes the step above ``p_max`` less its hot water. ``approach.age_h`` is
+    the live run's age at step 0: ``0.0`` with no run live, ``None`` unknown,
+    which books no entry and no ramp until the plan's next edge. No approach
+    or no levels: ``space`` itself, the same object.
+    """
+    if approach is None or (approach.entry.size == 0 and approach.ramp.size == 0):
+        return space
+    shipped = np.asarray(space, dtype=float)
+    hot = np.broadcast_to(np.asarray(dhw, dtype=float), shipped.shape)
+    if shipped.ndim == 2:
+        return np.stack([_received_row(shipped[b], hot[b], approach, dt, p_max) for b in range(shipped.shape[0])])
+    return _received_row(shipped, hot, approach, dt, p_max)
+
+
+def _received_row(shipped: np.ndarray, hot: np.ndarray, approach: Approach, dt: float, p_max: float) -> np.ndarray:
+    """:func:`received` of one plan: a walk carrying the run's age and the
+    time since its end."""
+    out = shipped.copy()
+    age_h = approach.age_h
+    live = age_h is None or age_h > 0.0
+    age: float | None = None if age_h is None or age_h <= 0.0 else float(age_h)
+    for k in range(shipped.size):
+        on = bool(shipped[k] > MIN_RUNNING_DRAW_KW)
+        if on != live:
+            # an edge: a run entered starts its age at 0, a run left starts the pause's;
+            # a run of unknown age leaves no pause to time
+            age = 0.0 if on or age is not None else None
+        live = on
+        if age is None:
+            continue
+        add = _mean_excess(approach.entry if on else approach.ramp, approach.bin_h, age, dt, float(shipped[k]))
+        out[k] = shipped[k] + min(add, max(float(p_max) - float(hot[k]) - float(shipped[k]), 0.0))
+        age += dt
+    return out
+
+
 def realizable(total: Any, floor: float) -> bool:
     """Every step off or at the floor or above: the plan runs as it stands."""
     q = np.asarray(total, dtype=float)
@@ -106,7 +198,7 @@ def realizable(total: Any, floor: float) -> bool:
 
 
 def commit(
-    q: Any, prices: Any, floor: float, caps: Any, start_cost: float, band: int,
+    q: Any, prices: Any, floor: float, caps: Any, start_cost: float | Start, band: int,
     *, dt: float, running: bool = False, forced: Any = None,
     lengths: tuple[int, int] = (1, 1),
 ) -> tuple[np.ndarray, bool]:
@@ -124,10 +216,15 @@ def commit(
     cut a run or a pause short. A balance outside the band is held at the
     edge cell and pays :data:`OUT_OF_BAND` for the energy outside: ``False``
     says the mask left the band, a best effort and never a refusal.
+    A :class:`Start` carries the learned entry's energy above the level: a
+    run started out of a pause also moves the balance by it and pays its
+    step's price for it, so the energy an entry delivers is left out later.
+    At zero the run action is :func:`_shift`.
     """
     q = np.asarray(q, dtype=float)
     n = q.size
     min_on = lengths[0]
+    start_cost, entry_kwh = start_cost if isinstance(start_cost, Start) else Start(float(start_cost))
     f = floor_kw(floor)
     cap = np.broadcast_to(np.asarray(caps, dtype=float), (n,))
     want = np.full(n, np.nan) if forced is None else np.array(forced, dtype=float)[:n]
@@ -141,22 +238,22 @@ def commit(
     bal = np.zeros_like(cost)
     cost[min_on - 1 if running else sum(lengths) - 1, half] = 0.0
     trail = []
+
+    def cells(b: np.ndarray, _runs: bool) -> tuple[np.ndarray, np.ndarray]:
+        outside = np.maximum(np.abs(b) - half * quantum, 0.0)
+        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), fine * outside
+
     for k in range(n):
-        asked = bool(q[k] > 0.0)
-        step = (
-            ((level[k] - q[k]) * dt, price[k] * level[k] * dt + _TIE_BREAK * (not asked)),
-            (-q[k] * dt, _TIE_BREAK * asked),
-        )
-        cost, bal, back = _advance(
-            cost, bal, _moves(*lengths, want[k]), step, float(start_cost), (quantum, half, fine), min_on)
+        ran, paused = tie_break(bool(q[k] > 0.0))
+        cost, bal, back = advance(
+            cost, bal, state_moves(*lengths, want[k]),
+            ([_entry_action((level[k] - q[k]) * dt, price[k] * level[k] * dt + ran, entry_kwh, price[k])], [_shift(-q[k] * dt, paused)]),
+            float(start_cost), cells, min_on)
         trail.append(back)
     ending = cost + fine * np.maximum(np.abs(bal) - f * dt / 2.0, 0.0)
-    u, j = (int(a) for a in np.unravel_index(np.argmin(ending), ending.shape))
-    mask = np.zeros(n, dtype=bool)
-    for k in range(n - 1, -1, -1):
-        mask[k] = u < min_on
-        u, j = (int(v) for v in trail[k][:, u, j])
-    walk = np.cumsum(np.where(mask, level, 0.0) - q) * dt
+    mask = read_back(trail, ending, min_on)[0]
+    entered = mask & ~np.r_[bool(running), mask[:-1]]
+    walk = np.cumsum(np.where(mask, level, 0.0) * dt + entered * float(entry_kwh) - q * dt)
     tracked = bool(
         np.all(np.abs(walk) <= half * quantum + _SLACK) and abs(walk[-1]) <= f * dt / 2.0 + _SLACK)
     return mask, tracked
@@ -164,7 +261,7 @@ def commit(
 
 def candidates(
     q: Any, prices: Any, floor: float, caps: Any, start_cost: float,
-    *, dt: float, running: bool = False, forced: Any = None,
+    *, dt: float, running: bool = False, forced: Any = None, entry_kwh: float = 0.0,
 ) -> list[np.ndarray]:
     """:func:`commit`'s distinct masks over :data:`BANDS`, tightest first, at
     the step counts of :data:`MIN_RUN` and :data:`MIN_PAUSE`.
@@ -179,7 +276,7 @@ def candidates(
         if tracked and band > BANDS[-1]:
             break
         mask, exact = commit(
-            q, prices, floor, caps, start_cost, band, dt=dt, running=running,
+            q, prices, floor, caps, Start(float(start_cost), entry_kwh), band, dt=dt, running=running,
             forced=forced, lengths=lengths,
         )
         tracked |= exact
@@ -188,60 +285,97 @@ def candidates(
     return masks
 
 
-def _moves(min_on: int, min_off: int, want: float) -> list[tuple[int, int, bool]]:
+def tie_break(asked: bool) -> tuple[float, float]:
+    """What running and pausing a step pay for leaving the plan's own on/off
+    reading of it (``asked``): a mask that saves nothing keeps the plan's runs."""
+    return _TIE_BREAK * (not asked), _TIE_BREAK * asked
+
+
+def state_moves(min_on: int, min_off: int, want: float, may_start: bool = True) -> list[tuple[int, int, bool]]:
     """``(source, destination, starts)`` state moves one step allows.
 
     States ``0 .. min_on - 1`` are a run of that many steps plus one (the last
     one long enough to stop), then the pauses alike. A forced step may leave
-    any run or pause; otherwise only the long-enough one switches.
+    any run or pause; otherwise only the long-enough one switches. With
+    ``may_start`` false a free step begins no run: the caller's answer to
+    whether the pump would start there, which this leaf does not ask.
     """
     last_on, states = min_on - 1, min_on + min_off
     free = bool(np.isnan(want))
     out: list[tuple[int, int, bool]] = []
     if not want == 0.0:
         out += [(i, min(i + 1, last_on), False) for i in range(min_on)]
-        out += [(i, 0, True) for i in range(min_on, states) if not free or i == states - 1]
+        if may_start or not free:
+            out += [(i, 0, True) for i in range(min_on, states) if not free or i == states - 1]
     if not want == 1.0:
         out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]
         out += [(i, min_on, False) for i in range(min_on) if not free or i == last_on]
     return out
 
 
-def _advance(
-    cost: np.ndarray, bal: np.ndarray, moves: list[tuple[int, int, bool]],
-    step: tuple[tuple[float, float], tuple[float, float]], start_cost: float,
-    grid: tuple[float, int, float], min_on: int,
-) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
-    """One step of :func:`commit`: the cheapest arrival per cell, its exact
-    balance, and where it came from.
+def _shift(change: float, paid: float) -> Action:
+    """:func:`commit`'s action: the balance moved by ``change`` for ``paid``."""
+    return lambda bal, _ran: (bal + change, paid)
+
 
-    ``step`` is ``(balance change, cost)`` for running and for pausing;
-    ``grid`` is the cell width, the band's half width in cells and the price
-    of a kWh outside the band.
+def _entry_action(change: float, paid: float, entry_kwh: float, price: float) -> Action:
+    """:func:`commit`'s run action: :func:`_shift`, and out of a pause the
+    entry's energy above the level besides, at the step's price."""
+    if not entry_kwh > 0.0:
+        return _shift(change, paid)
+    return lambda bal, ran: (bal + change + (0.0 if ran else entry_kwh), paid + (0.0 if ran else price * entry_kwh))
+
+
+def advance(
+    cost: np.ndarray, val: np.ndarray, allowed: list[tuple[int, int, bool]],
+    actions: tuple[list[Action], list[Action]], start_cost: float, place: CellRule, min_on: int,
+) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
+    """One step of a program over (run or pause length, a scalar on a grid):
+    the cheapest arrival per cell, its exact scalar, and where it came from.
+
+    ``allowed`` is :func:`state_moves`' answer for the step; ``actions`` are what a
+    step into a run and into a pause may do; a start pays ``start_cost``
+    besides. ``place`` is the caller's cell rule. The
+    scalar is the caller's alone (an energy balance, a tank temperature):
+    its meaning, grid and bounds are in the two calls, and each cell keeps
+    the exact value of the cheapest path into it, so rounding does not
+    accrue. The third layer of the back pointers is the action taken.
     """
-    quantum, half, fine = grid
     width = cost.shape[1]
     new_cost = np.full_like(cost, np.inf)
-    new_bal = np.zeros_like(bal)
-    back = np.zeros((2,) + cost.shape, dtype=np.int32)
+    new_val = np.zeros_like(val)
+    back = np.zeros((3,) + cost.shape, dtype=np.int32)
     cells = np.arange(width)
-    for dest in sorted({m[1] for m in moves}):
-        srcs = [(s, starts) for s, d, starts in moves if d == dest]
-        change, paid = step[0] if dest < min_on else step[1]
-        b = np.concatenate([bal[s] + change for s, _ in srcs])
-        outside = np.maximum(np.abs(b) - half * quantum, 0.0)
-        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs]) + fine * outside
-        origin = np.concatenate([np.full(width, s) for s, _ in srcs])
-        came = np.tile(cells, len(srcs))
-        j = np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half)
+    for dest in sorted({m[1] for m in allowed}):
+        took = [
+            (s, starts, a, *act(val[s], s < min_on))
+            for s, d, starts in allowed if d == dest
+            for a, act in enumerate(actions[0] if dest < min_on else actions[1])
+        ]
+        b = np.concatenate([t[3] for t in took])
+        j, extra = place(b, dest < min_on)
+        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts, _, _, paid in took]) + extra
+        origin, action = (np.concatenate([np.full(width, t[i]) for t in took]) for i in (0, 2))
+        came = np.tile(cells, len(took))
         ok = np.isfinite(c)
         if not ok.any():
             continue
-        c, b, origin, came, j = c[ok], b[ok], origin[ok], came[ok], j[ok]
+        c, b, origin, came, action, j = c[ok], b[ok], origin[ok], came[ok], action[ok], j[ok]
         order = np.lexsort((c, j))
         first = order[np.r_[True, j[order][1:] != j[order][:-1]]]
         new_cost[dest, j[first]] = c[first]
-        new_bal[dest, j[first]] = b[first]
-        back[0, dest, j[first]] = origin[first]
-        back[1, dest, j[first]] = came[first]
-    return new_cost, new_bal, back
+        new_val[dest, j[first]] = b[first]
+        back[:, dest, j[first]] = origin[first], came[first], action[first]
+    return new_cost, new_val, back
+
+
+def read_back(trail: list[np.ndarray], ending: np.ndarray, min_on: int) -> tuple[np.ndarray, np.ndarray]:
+    """The cheapest path through ``trail`` (one :func:`advance` back pointer
+    per step) to the cheapest cell of ``ending``: per step, whether it ran
+    and the index of the action it took."""
+    u, j = (int(a) for a in np.unravel_index(np.argmin(ending), ending.shape))
+    mask, action = np.zeros(len(trail), dtype=bool), np.zeros(len(trail), dtype=np.int64)
+    for k in range(len(trail) - 1, -1, -1):
+        mask[k], action[k] = u < min_on, trail[k][2, u, j]
+        u, j = (int(v) for v in trail[k][:2, u, j])
+    return mask, action
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index ab1324a768..6b8b4bdc39 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -2201,7 +2201,7 @@ def _pump_min_power(band: Any) -> dict[str, Any]:
 _MAX_ROW = {k: k for k in ("configured_max_kw", "planned_max_kw", "learned_max_kw", "samples", "since_s")}
 _MIN_ROW = {
     "configured_min_kw": "configured_min_kw", "planned_min_kw": "planned_min_kw",
-    "learned_min_kw": "learned_min_kw", "samples": "min_samples",
+    "learned_min_kw": "learned_min_kw", "samples": "min_samples", "approach_kwh": "approach_kwh",
 }
 
 
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index a3ed10d0c4..2c10dc61c7 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -341,6 +341,13 @@ _ACCURACY: dict[str, Domain | str] = {
     # unset or 0 (_stored_floor) and costs only itself, never the record.
     "draw/floor_kw": Domain("real", _POS),
     "draw/floor_since": _COUNT,
+    # R11-OUTSIDE-START-APPROACH: the draw by age bin after a space-run entry
+    # and after a run's end, the configuration it is keyed to, and the run's
+    # clock; a bad cell or key costs only itself (ApproachProfile.from_dict).
+    "draw/approach/entry/#/#": _Z, "draw/approach/ramp/#/#": _Z,
+    "draw/approach/config/#": Domain("real", whole="the configuration keys the profile: unreadable, its evidence and clock are dropped with it"),
+    "draw/approach/entered_s": _R, "draw/approach/ended_s": _R, "draw/approach/seen_s": _R,
+    "draw/approach/running": _FLAG,
 }
 
 #: The COP health watch's memory, keyed ``_measured``: a heat measurement
diff --git a/custom_components/heatpump_optimizer/sysid.py b/custom_components/heatpump_optimizer/sysid.py
index 443bca4821..e828e49e39 100644
--- a/custom_components/heatpump_optimizer/sysid.py
+++ b/custom_components/heatpump_optimizer/sysid.py
@@ -376,9 +376,8 @@ class HousePlant:
 
 @dataclass
 class SysIdConfig:
-    """Gating conditions and step size."""
+    """Gating conditions and step size; the on/off switch is ``arm``'s argument (ADR-003)."""
 
-    enabled: bool = False
     #: Outdoor temperature band in which a step is both safe and informative.
     #: Too cold and the step risks comfort; too mild and ΔT is too small for
     #: the loss coefficient to be identifiable.
@@ -787,6 +786,21 @@ SLAB_LOG_ROOM_CAP_LO = float(np.log(1e-3))
 SLAB_LOG_ROOM_CAP_HI = float(np.log(1e3))
 
 
+def _fdjac(residual: Callable[[np.ndarray], np.ndarray], x: np.ndarray, value: np.ndarray) -> np.ndarray:
+    """Forward-difference Jacobian of ``residual`` at ``x`` (whose value is ``value``).
+
+    Step ``1e-6 * max(|x_i|, 1)`` per parameter: the one spelling the solver
+    and the profile interval share (ADR-001).
+    """
+    jac = np.empty((value.size, x.size))
+    for i in range(x.size):
+        step = 1e-6 * max(abs(float(x[i])), 1.0)
+        bumped = np.asarray(x, dtype=float).copy()
+        bumped[i] += step
+        jac[:, i] = (residual(bumped) - value) / step
+    return jac
+
+
 def _lm_solve(
     residual: Callable[[np.ndarray], np.ndarray],
     x0: np.ndarray,
@@ -809,12 +823,7 @@ def _lm_solve(
     cost = float(value @ value)
     damping = 1e-2
     for _ in range(max_iter):
-        jac = np.empty((value.size, x.size))
-        for i in range(x.size):
-            step = 1e-6 * max(abs(float(x[i])), 1.0)
-            bumped = x.copy()
-            bumped[i] += step
-            jac[:, i] = (residual(bumped) - value) / step
+        jac = _fdjac(residual, x, value)
         gram = jac.T @ jac
         gradient = jac.T @ value
         accepted = False
@@ -982,27 +991,29 @@ def _told_path_error(
     return told
 
 
-def _ridged(error: _PathError, prior_g: float) -> _PathError:
+def _ridged(error: _PathError, prior_g: float, width_kw: float) -> _PathError:
     """The fit's residual: the rollout error plus the D2-01 intercept ridge.
 
     A candidate whose rollout left the finite range reads as a huge finite
     cost instead of poisoning the Jacobian with a NaN, or raising out of the
     fit (R6 D7-03 #1396/#1397). The ridge is ONE pseudo-observation on G,
-    weighed against the whole room series through its width; deleting the
-    append is the mutation the ensemble test flips on.
+    weighed against the whole room series through its width ``width_kw``
+    (``SLAB_INTERCEPT_PRIOR_SD_KW`` at every caller); deleting the append is
+    the mutation the ensemble test flips on. The one spelling of the ridge:
+    the fit and every interval the gate reads take it from here.
     """
 
     def residual(x: np.ndarray) -> np.ndarray:
         e = error(x)
         if not bool(np.all(np.isfinite(e))):
             return np.full(e.size + 1, 1e12, dtype=float)
-        return np.append(e, (float(x[2]) - prior_g) / SLAB_INTERCEPT_PRIOR_SD_KW)
+        return np.append(e, (float(x[2]) - prior_g) / width_kw)
 
     return residual
 
 
 def _slab_ua_profile_halfwidth(
-    x_hat: np.ndarray, error: _PathError, samples: int, prior_g: float
+    x_hat: np.ndarray, error: _PathError, samples: int, prior_g: float, width_kw: float
 ) -> float:
     """The two-state fit's UA half-width, as the adoption gate reads it.
 
@@ -1016,10 +1027,7 @@ def _slab_ua_profile_halfwidth(
     narrow intervals the gate admits.
     """
 
-    def _residual(x: np.ndarray) -> np.ndarray:
-        return np.append(
-            error(x), (float(x[2]) - prior_g) / SLAB_INTERCEPT_PRIOR_SD_KW
-        )
+    _residual = _ridged(error, prior_g, width_kw)
 
     def _profiled_cost(t: float) -> float:
         def _inner(y: np.ndarray) -> np.ndarray:
@@ -1036,13 +1044,7 @@ def _slab_ua_profile_halfwidth(
     for sign in (1.0, -1.0):
         if _profiled_cost(x_hat[0] + sign * UA_ADOPTION_HALFWIDTH_BAR) <= threshold:
             return float("inf")
-    value = _residual(x_hat)
-    jac = np.empty((value.size, x_hat.size))
-    for i in range(x_hat.size):
-        step = 1e-6 * max(abs(float(x_hat[i])), 1.0)
-        bumped = np.asarray(x_hat, dtype=float).copy()
-        bumped[i] += step
-        jac[:, i] = (_residual(bumped) - value) / step
+    jac = _fdjac(_residual, x_hat, _residual(x_hat))
     cov = np.linalg.inv(jac.T @ jac) * sigma2
     se = float(np.sqrt(max(cov[0, 0], 0.0)))
     return _Z_975 * se
@@ -1086,7 +1088,7 @@ def _one_state_ua_halfwidth(
 
 
 def _slab_ua_prior_halfwidth(
-    x_hat: np.ndarray, error: _PathError, prior_g: float
+    x_hat: np.ndarray, error: _PathError, prior_g: float, width_kw: float
 ) -> float:
     """The UA interval the intercept prior ITSELF contributes (D7-01).
 
@@ -1118,19 +1120,19 @@ def _slab_ua_prior_halfwidth(
 
     def _shifted(shifted_prior: float) -> float:
         x, _cost = _lm_solve(
-            _ridged(error, shifted_prior),
+            _ridged(error, shifted_prior, width_kw),
             np.array([float(x_hat[0]), float(x_hat[1]), shifted_prior]),
         )
         return abs(float(x[0]) - float(x_hat[0]))
 
-    width = SLAB_INTERCEPT_PRIOR_SD_KW
     return _Z_975 * max(
-        _shifted(prior_g + width), _shifted(prior_g - width)
+        _shifted(prior_g + width_kw), _shifted(prior_g - width_kw)
     )
 
 
 def _slab_ua_told_halfwidth(
-    x_hat: np.ndarray, told_error: Callable[[float, float], _PathError], prior_g: float
+    x_hat: np.ndarray, told_error: Callable[[float, float], _PathError], prior_g: float,
+    width_kw: float,
 ) -> float:
     """The UA interval the told slab pair contributes (R9-P5, #1655).
 
@@ -1146,7 +1148,7 @@ def _slab_ua_told_halfwidth(
     for scales in (((up, 1.0), (down, 1.0)), ((1.0, up), (1.0, down))):
         moved = 0.0
         for m, t in scales:
-            x, _cost = _lm_solve(_ridged(told_error(m, t), prior_g), np.asarray(x_hat, float))
+            x, _cost = _lm_solve(_ridged(told_error(m, t), prior_g, width_kw), np.asarray(x_hat, float))
             moved = max(moved, abs(float(x[0]) - float(x_hat[0])))
         shifts.append(moved)
     return _Z_975 * math.hypot(*shifts)
@@ -1217,8 +1219,9 @@ def _declared_night_halfwidth(
     )
     told = _told_path_error((rooms, outdoors, np.append(powers, 0.0), dts), slab_pair, two_zone)
     x0 = np.array([np.log(max(ua0, 1e-3)), np.log(max(cr0, 1e-2)), g])
+    w = SLAB_INTERCEPT_PRIOR_SD_KW
     return float(np.hypot(
-        _slab_ua_prior_halfwidth(x0, told(1.0, 1.0), g), _slab_ua_told_halfwidth(x0, told, g)
+        _slab_ua_prior_halfwidth(x0, told(1.0, 1.0), g, w), _slab_ua_told_halfwidth(x0, told, g, w)
     ))
 
 
@@ -1439,7 +1442,7 @@ class SystemIdentification:
 
     def arm(
         self, now: datetime, plant: ThermalParameters | None = None,
-        learner_samples: int = 0, probe: DrawRange | None = None,
+        learner_samples: int = 0, probe: DrawRange | None = None, *, enabled: bool = True,
     ) -> bool:
         """Arm an experiment, to start when conditions allow.
 
@@ -1453,9 +1456,11 @@ class SystemIdentification:
         reason into the result, so it is published — instead of burning the
         night to have the fit's guards refuse it silently. Callers that do
         not declare a plant (a harness driving a synthetic one) are not
-        gated; production always declares it.
+        gated; production always declares it. ``enabled`` is the
+        configuration's switch, read by the caller per arm (ADR-003): nothing
+        stores it on the collaborator.
         """
-        if not self.config.enabled:
+        if not enabled:
             _LOGGER.info("System identification is disabled in the configuration")
             return False
         if self.active:
@@ -1981,18 +1986,18 @@ class SystemIdentification:
         except np.linalg.LinAlgError:
             return SysIdResult(completed=False, reason="fit failed")
         # --- D2-01: errors-in-variables correction -------------------------
-        # ``T_prev`` sits on BOTH sides of the regression -- in the rate
-        # (divided by dt) and in the delta column -- so sensor noise covaries
-        # the two and biases the UA/C slope UPWARD (the audit measured +44 %
-        # at 0.05 °C noise, +108 % at 0.10 °C, and biased fits cleared the
-        # 0.3 adoption gate). The noise variance is estimated from the room
-        # series itself and the KNOWN bias terms are subtracted from the
-        # normal equations: the delta column's own noise deflates X'X by
-        # n*sigma^2, and the rate/regressor noise covariance shifts X'y by
-        # sigma^2 * sum(1/dt). Clean data estimates sigma^2 ~ 0 and the
-        # correction vanishes; a window whose noise exceeds a third of the
-        # delta column's spread is refused outright -- there is no honest
-        # fit to be had there.
+        # The previous room reading (``usable[i - 1].room_temp``) sits on BOTH
+        # sides of the regression -- in the rate (divided by dt) and in the
+        # delta column -- so sensor noise covaries the two and biases the UA/C
+        # slope UPWARD (the audit measured +44 % at 0.05 °C noise, +108 % at
+        # 0.10 °C, and biased fits cleared the 0.3 adoption gate). The noise
+        # variance is estimated from the room series itself and the KNOWN bias
+        # terms are subtracted from the normal equations: the delta column's
+        # own noise deflates X'X by n*sigma^2, and the rate/regressor noise
+        # covariance shifts X'y by sigma^2 * sum(1/dt). Clean data estimates
+        # sigma^2 ~ 0 and the correction vanishes; a window whose noise exceeds
+        # a third of the delta column's spread is refused outright -- there is
+        # no honest fit to be had there.
         #
         # sigma^2 from second differences WITHIN a phase only: the step->
         # relax transition is a genuine kink in the signal (power drops to
@@ -2070,7 +2075,7 @@ class SystemIdentification:
             rhs[0] -= sigma2 * float(np.sum(1.0 / dts)) / col_scale[0]
         # The prior enters as its own pseudo-observation, exactly as the
         # stacked row did -- same algebra, normal-equation form, weighed
-        # against the data through prior_rel = prior_w / data_w.
+        # against the data through ``prior_rel = s_noise / prior_sd`` below.
         #
         # D2-07: the right-hand side term had one factor of col_scale[2] too
         # many, which is not a scaling nicety -- it made the prior pull the
@@ -2360,7 +2365,7 @@ class SystemIdentification:
             series, (slab_mass, slab_transfer), self._two_zone_plant
         )
         error = told_error(1.0, 1.0)
-        residual = _ridged(error, self.config.gains_prior_kw)
+        residual = _ridged(error, self.config.gains_prior_kw, SLAB_INTERCEPT_PRIOR_SD_KW)
         prior_g = self.config.gains_prior_kw
 
         # Multi-start over the room-capacity decade: the cost surface has a
@@ -2417,8 +2422,9 @@ class SystemIdentification:
         # clean residual is exactly what a prior-dominated, useless fit
         # looks like, so the interval — not the residual scatter — is the
         # quantity the gate bounds.
+        prior_g, width = self.config.gains_prior_kw, SLAB_INTERCEPT_PRIOR_SD_KW
         profile_halfwidth = _slab_ua_profile_halfwidth(
-            best_x, path_error, int(rooms.size), self.config.gains_prior_kw
+            best_x, path_error, int(rooms.size), prior_g, width
         )
         # ... and the interval the intercept prior itself contributes (round-7
         # D7-01, #1459): the profile term above holds prior_g FIXED, so on the
@@ -2426,7 +2432,7 @@ class SystemIdentification:
         # one prior-width moves UA by ~2.3 %, and only the pair of them is
         # what the adoption gate may read.
         prior_halfwidth = _slab_ua_prior_halfwidth(
-            best_x, path_error, self.config.gains_prior_kw
+            best_x, path_error, prior_g, width
         )
         # tau_fast re-derives from the fit. The split itself is never
         # adopted — see SysIdResult.slab_mode_tau_hours and the #996
@@ -2444,7 +2450,7 @@ class SystemIdentification:
             ua_profile_halfwidth=profile_halfwidth,
             ua_prior_halfwidth=prior_halfwidth,
             ua_told_halfwidth=_slab_ua_told_halfwidth(
-                best_x, told_error, self.config.gains_prior_kw
+                best_x, told_error, prior_g, width
             ),
             confidence=_slab_confidence(rooms, error),
             reason="ok",
@@ -2472,9 +2478,9 @@ def arm_from_config(
     The switch is the configuration's; the draw store is the probe's only
     where the install can run it (``thermal_model.ceiling_probe_install``).
     """
-    ident.config.enabled = config.system_identification_enabled
     probe = draw if ceiling_probe_install(config) else None
-    armed = ident.arm(now, plant=plant, learner_samples=learner_samples, probe=probe)
+    armed = ident.arm(now, plant=plant, learner_samples=learner_samples, probe=probe,
+                      enabled=config.system_identification_enabled)
     if armed:
         _LOGGER.info(
             "System identification armed (%s); it will start at the next mild, cheap night hour",
@@ -2499,7 +2505,7 @@ def arm_refusal(
     """
     if arm_from_config(ident, now, config, plant, learner_samples, draw):
         return None
-    if not ident.config.enabled:
+    if not config.system_identification_enabled:
         return ARM_REFUSED_DISABLED
     if ident.active:
         return "an experiment is already armed or running"
diff --git a/dev/audit/harnesses/ceiling_probe.py b/dev/audit/harnesses/ceiling_probe.py
index d1101c541b..07ca4e156e 100644
--- a/dev/audit/harnesses/ceiling_probe.py
+++ b/dev/audit/harnesses/ceiling_probe.py
@@ -141,7 +141,7 @@ def store_arm() -> None:
     house = sysid.HousePlant(ua=0.35, capacity=12.0, gains=0.3)
     for night in range(3):
         start = datetime(2026, 1, 10, 23, 0, tzinfo=timezone.utc) + timedelta(days=8 * night)
-        s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
+        s = sysid.SystemIdentification(sysid.SysIdConfig())
         if not s.arm(start, learner_samples=482, probe=store):
             print("store: night", night, "refused:", s.result.reason)
             return
@@ -153,7 +153,7 @@ def store_arm() -> None:
             if pending is not None:
                 dr.fold(store, 3.0 if pending["cmd"] is ceil else 1.5, (pending["kw"], 0.0), params,
                         frozen=False, distorted=False, defrost=False, command=pending["cmd"],
-                        experiment_s=pending["when"] if pending["sid"] else None)
+                        span=dr.Span(pending["when"], pending["when"], experiment=True) if pending["sid"] else None)
             kw = 1.5 if override is None else override
             pending = {"sid": override is not None, "kw": kw, "when": now.timestamp(),
                        "cmd": ceil if kw >= 5.0 else mid}
diff --git a/dev/audit/harnesses/cop_dither_fabric.py b/dev/audit/harnesses/cop_dither_fabric.py
index b69db5f023..00c80a6155 100644
--- a/dev/audit/harnesses/cop_dither_fabric.py
+++ b/dev/audit/harnesses/cop_dither_fabric.py
@@ -42,6 +42,7 @@ every arm, so that row measures the driver, not the dither, and is not printed.
 """
 from __future__ import annotations
 
+import collections
 import asyncio
 import math
 import sys
@@ -55,6 +56,7 @@ from homeassistant.util import dt as dt_util  # noqa: E402
 from profiles import house  # noqa: E402
 
 from heatpump_optimizer import accuracy, draw_range  # noqa: E402
+from heatpump_optimizer import coordinator as coord_module  # noqa: E402
 from heatpump_optimizer.const import CONF_INDOOR_TEMP_ENTITY  # noqa: E402
 from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
 from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries  # noqa: E402
@@ -82,6 +84,18 @@ def run(true: float, cycles: int = CYCLES, outdoor_c: float = 2.0, two_zone: boo
                          dhw_hours_since_legionella=20.0, buffer_tank_temperature=40.0)
     coord._current_state = state
     trace = []
+    # R11-SEAM-learners (carry 3): which refusal took each house cycle the fold did not
+    # take, by the house learner's own skip log (``log_skip``); cycles it names none for
+    # are ``unnamed``. Read only; the learners run exactly as before.
+    tally: collections.Counter = collections.Counter()
+    real_skip = coord_module.log_skip
+
+    def _skip(clean, what, why, *args):
+        if what == "house heat loss":
+            tally[(why % args) if args else why] += 1
+        return real_skip(clean, what, why, *args)
+
+    coord_module.log_skip = _skip
     try:
         for step in range(cycles):
             now = START + timedelta(hours=step * DT_H)
@@ -108,7 +122,10 @@ def run(true: float, cycles: int = CYCLES, outdoor_c: float = 2.0, two_zone: boo
             trace.append(coord._house_heat_loss_scale)
     finally:
         dt_util.freeze(None)
+        coord_module.log_skip = real_skip
+    tally["unnamed"] = cycles - coord._house_heat_loss_samples - sum(tally.values())
     return {
+        "refusals": ",".join(f"{k.replace(' ', '_')}:{v}" for k, v in sorted(tally.items()) if v),
         "house_scale": coord._house_heat_loss_scale,
         "house_samples": coord._house_heat_loss_samples,
         "lower_ratio": coord._lower_floor_loss_ratio,
@@ -145,6 +162,8 @@ def main() -> None:
             row(f"dither_{tag}", live, gap)
             row(f"null_dither0_{tag}", null)
             row(f"no_probe_{tag}", off)
+            for name, out in (("dither", live), ("null_dither0", null), ("no_probe", off)):
+                print(f"RESULT refusals_{name}_{tag}={out['refusals']}")
 
 
 if __name__ == "__main__":
diff --git a/dev/audit/harnesses/cop_duty_floor.py b/dev/audit/harnesses/cop_duty_floor.py
index e84b75d66d..aa05575f4e 100644
--- a/dev/audit/harnesses/cop_duty_floor.py
+++ b/dev/audit/harnesses/cop_duty_floor.py
@@ -261,10 +261,14 @@ def swing(n: int, kw: float, parts, seed: int, phase: float = 0.0) -> list[tuple
     return out
 
 
-def derate(pairs, outdoor: float) -> str:
+def derate(pairs, outdoor: float, verdict: str | None = None) -> str:
     """The defrost derate's inferred factor at ``outdoor`` °C after ``pairs``
-    (asked, drawn) intervals settle with no defrost flag, and its count."""
+    (asked, drawn) intervals settle with no defrost flag, and its count.
+    ``verdict`` plants the heat-ask probe's scale-response verdict first (the
+    state the ``selfset_2.2_swing*`` rows reach); ``None`` leaves it pending."""
     c = coord(p_max=4.0)
+    if verdict is not None:
+        c._measured_cop.probe.response = verdict
     t0 = datetime(2026, 1, 10, tzinfo=timezone.utc)
     for i, (ask, kw) in enumerate(pairs):
         window = c._defrost_window.close(t0 + timedelta(minutes=30 * i))
@@ -416,6 +420,10 @@ def main() -> None:
     for outdoor in (2.0, 8.0):
         for name, kw in (("selfset_2.2", 2.2), ("matched", None)):
             print(f"RESULT defrost_inferred_{name}_{outdoor:g}C={derate(flat(96, kw), outdoor)}")
+    # R11-SEAM-learners (carries 0-1): the same settles once the probe reads the ask
+    # ignored, the delivered-ratio ask's evidence; matched is the control.
+    for name, kw in (("selfset_2.2", 2.2), ("matched", None)):
+        print(f"RESULT defrost_inferred_{name}_2C_ignored={derate(flat(96, kw), 2.0, draw_range.ASK_IGNORED)}")
     for name, n in (("full", draw_range.WINDOW), ("filling", draw_range.WINDOW - 48)):
         print(f"RESULT held_{name}_heatled_true_0.8={run(depart, p_max=4.0, p_min=3.0, true=0.8, warm=[(2.6, 3.2)] * n).replace(' ', '_scale=')}")
 
diff --git a/dev/audit/harnesses/r10_dhw_charge_settle_p90.py b/dev/audit/harnesses/r10_dhw_charge_settle_p90.py
index 7b2de55267..e7127368ec 100644
--- a/dev/audit/harnesses/r10_dhw_charge_settle_p90.py
+++ b/dev/audit/harnesses/r10_dhw_charge_settle_p90.py
@@ -81,7 +81,7 @@ def run(
     learner = dl.DhwProfileLearner(
         None, "h", lambda: params,
         publish=lambda **k: usage_points.__setitem__(0, usage_points[0] + 1),
-        frozen=lambda *a: None,
+        frozen=lambda *a, **_kw: None,
         heating_active=lambda: heating[0],
         external_heat_active=lambda: False,
     )
diff --git a/dev/audit/harnesses/r10_dhw_start_hysteresis.py b/dev/audit/harnesses/r10_dhw_start_hysteresis.py
index ad2de645ee..ae7ddd7a04 100644
--- a/dev/audit/harnesses/r10_dhw_start_hysteresis.py
+++ b/dev/audit/harnesses/r10_dhw_start_hysteresis.py
@@ -33,7 +33,7 @@ RESULT lines, each a sum over the 18 solves:
   dhw_cost                               the planned hot-water energy at the day's prices
   plan_sha1                              sha1 over the 18 hot-water schedules and trajectories
   repair_rounds_max / placements         the most floor-repair calls one placement under a start
-                                         condition made (``dhw_planner.place_startable``), and
+                                         condition made (``dhw_charges.place_startable``), and
                                          how many placements were counted; "none" with no condition
 Null control: ``--hysteresis`` unset and ``--hysteresis 0`` print the
 plan_sha1 the merge base prints; a hysteresis of 4 prints
diff --git a/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
index 665fcad57a..aec4d93089 100644
--- a/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
+++ b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
@@ -18,26 +18,26 @@ W = sys.argv[1]
 CC = os.path.join(W, "custom_components/heatpump_optimizer")
 M = [
  ("M1 lift owner returns the configured lift", "thermal_model.py", "    return lift if hysteresis is None else max(lift, hysteresis)\n", "    return lift\n"),
- ("M2 drop_unstartable >= to >", "dhw_planner.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
+ ("M2 drop_unstartable >= to >", "dhw_charges.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
  ("M3 ledger not-startable branch removed", "pump_arbiter.py", '    if planned == "dhw" and actual == "idle" and _not_startable(row):\n        return "not-startable"\n', ""),
  ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]\n", ""),
- ("M5 startable_steps < to <=", "dhw_planner.py", "[: on.size] < start_below[: on.size]\n", "[: on.size] <= start_below[: on.size]\n"),
+ ("M5 startable_steps < to <=", "dhw_charges.py", "[: on.size] < start_below[: on.size]\n", "[: on.size] <= start_below[: on.size]\n"),
  ("M6 a zero hysteresis is a start condition", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis < 0.0:"),
  ("M7 the difference reader ignores the unit's scale", "inputs.py", "    delta_k = value * scale\n", "    delta_k = value\n"),
- ("M8 the cycle step judged against the everyday target", "dhw_planner.py", "        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)\n", "        pass\n"),
+ ("M8 the cycle step judged against the everyday target", "dhw_charges.py", "        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)\n", "        pass\n"),
  ("M9 notice at a minimum equal to the start temperature", "setpoint_check.py", "start is not None and floor > start,", "start is not None and floor >= start,"),
- ("M10 place_startable returns without the final drop", "dhw_planner.py", "        plan = fixed\n    return drop_unstartable(plan, start_below, temps_of)\n", "        plan = fixed\n    return plan\n"),
+ ("M10 place_startable returns without the final drop", "dhw_charges.py", "        plan = fixed\n    return drop_unstartable(plan, start_below, temps_of)\n", "        plan = fixed\n    return plan\n"),
  ("M11 coordinator does not read the options", "coordinator.py", "        read_start_hysteresis(state, self.hass, self.effective_config)\n", ""),
  ("M12 the floor write ignores the hysteresis", "pump_arbiter.py", 'start_flow_min_lift_k(inp.config, getattr(inp.state, "space_start_hysteresis_k", None)),', "start_flow_min_lift_k(inp.config, None),"),
  ("M13 the planner ignores the hysteresis", "dhw_planner.py", "dhw_start_temps(params, initial_state, n_steps, legionella_step)", "dhw_start_temps(params, type(initial_state)(), n_steps, legionella_step)"),
  ("M14 ledger start ignores the written target", "pump_arbiter.py", "dhw_start_below_c(_dhw_target(inp), hysteresis)", "dhw_start_below_c(dhw_step_target_c(inp.params, False), hysteresis)"),
  ("M15 delta reader accepts above the maximum", "inputs.py", "    return delta_k if 0.0 <= delta_k <= TEMPERATURE_DELTA_MAX_K else None", "    return delta_k if 0.0 <= delta_k else None"),
- ("M16 a run at step 0 is judged too", "dhw_planner.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on & ~np.append(False, on[:-1])):\n"),
- ("M17 the round bound is nine", "dhw_planner.py", "STARTABLE_ROUNDS = 8\n", "STARTABLE_ROUNDS = 9\n"),
- ("M18 a cycle on the first step is not a cycle step", "dhw_planner.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 < cycle_step < n_steps:"),
- ("M19 a run at the second step is not judged", "dhw_planner.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on[2:] & ~on[1:-1]) + 2:\n"),
- ("M20 the loop never ends early", "dhw_planner.py", "        if np.array_equal(fixed, plan):\n", "        if False:\n"),
- ("M21 a cycle past the horizon is written", "dhw_planner.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 <= cycle_step <= n_steps:"),
+ ("M16 a run at step 0 is judged too", "dhw_charges.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on & ~np.append(False, on[:-1])):\n"),
+ ("M17 the round bound is nine", "dhw_charges.py", "STARTABLE_ROUNDS = 8\n", "STARTABLE_ROUNDS = 9\n"),
+ ("M18 a cycle on the first step is not a cycle step", "dhw_charges.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 < cycle_step < n_steps:"),
+ ("M19 a run at the second step is not judged", "dhw_charges.py", "    for i in np.flatnonzero(on[1:] & ~on[:-1]) + 1:\n", "    for i in np.flatnonzero(on[2:] & ~on[1:-1]) + 2:\n"),
+ ("M20 the loop never ends early", "dhw_charges.py", "        if np.array_equal(fixed, plan):\n", "        if False:\n"),
+ ("M21 a cycle past the horizon is written", "dhw_charges.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 <= cycle_step <= n_steps:"),
  ("M22 the shared clamp zeroes a step on the runnable block", "dhw_planner.py", "        return np.where(plan < ctx.min_run_power - 1e-9, 0.0, plan)\n", "        return np.where(plan <= ctx.min_run_power - 1e-9, 0.0, plan)\n"),
  ("M23 no step is a cycle step for the write or the ledger", "pump_arbiter.py", '    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA or inp.disinfecting\n', "    cycle = False\n"),
  ("M24 the set-point check never reaches the start notice", "setpoint_check.py", "    _dhw_start(hass, config, params)\n", "    pass\n"),
@@ -45,22 +45,22 @@ M = [
  ("M26 a hysteresis under one kelvin is none", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis <= 1.0:"),
  ("M27 pinned hot water is not held to the tank's capacity", "dhw_planner.py", "            schedule = self._ctx_clamp(\n                ctx, initial_state.dhw_temperature, draw_rates, max_temp, schedule)\n", "            pass\n"),
  ("M28 the write and the ledger ignore the entity's grid", "pump_arbiter.py", 'return dhw_step_target_c(inp.params, cycle, _grid(inp, "dhw_setpoint"))', "return dhw_step_target_c(inp.params, cycle, None)"),
- ("M29 the planner ignores the entity's grid", "dhw_planner.py", "hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid\n", "hysteresis_k, grid = state.dhw_start_hysteresis_k, None\n"),
+ ("M29 the planner ignores the entity's grid", "dhw_charges.py", "hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid\n", "hysteresis_k, grid = state.dhw_start_hysteresis_k, None\n"),
  ("M30 the notice ignores the entity's grid", "setpoint_check.py", "dhw_step_target_c(params, False, setpoint_grid(hass, cfg.dhw_setpoint_entity))", "dhw_step_target_c(params, False)"),
  ("M31 the notice is raised with hot water disabled", "setpoint_check.py", "bool(params.dhw_enabled) and start is not None", "start is not None"),
  ("M32 the everyday target ignores the charge limit", "thermal_model.py", "(params.dhw_setpoint, params.dhw_max_temp) if target is None", "(params.dhw_setpoint, 1e9) if target is None"),
  ("M33 the cycle's target ignores the hard maximum", "thermal_model.py", "else (target, params.dhw_hard_max_temp)", "else (target, 1e9)"),
  ("M34 the input read leaves the grid off the state", "inputs.py", "    state.dhw_setpoint_grid = setpoint_grid(hass, cfg.dhw_setpoint_entity)\n", ""),
- ("M35 the step after a charge the pump would not start is startable", "dhw_planner.py", "        under_way = bool(on[i] and ok[i])\n", "        under_way = bool(on[i])\n"),
- ("M36 a charge at the first step carries nothing on", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = False\n"),
- ("M37 no charge under way carries on", "dhw_planner.py", "        ok[i] |= under_way\n", "        pass\n"),
+ ("M35 the step after a charge the pump would not start is startable", "dhw_charges.py", "        under_way = bool(on[i] and ok[i])\n", "        under_way = bool(on[i])\n"),
+ ("M36 a charge at the first step carries nothing on", "dhw_charges.py", "    under_way = bool(on[:1].any())\n", "    under_way = False\n"),
+ ("M37 no charge under way carries on", "dhw_charges.py", "        ok[i] |= under_way\n", "        pass\n"),
  ("M38 an entity with no state has a grid", "inputs.py", "    if not entity_id or hass.states.get(entity_id) is None:\n        return None\n    return _grid_of", "    if not entity_id:\n        return None\n    return _grid_of"),
  ("M39 with no entity the target ignores its bound", "thermal_model.py", "        return min(float(value), float(limit))\n", "        return float(value)\n"),
  ("M40 the hot-water write goes to an entity with no state", "pump_arbiter.py", 'return None if _grid(inp, "dhw_setpoint") is None else _dhw_target(inp)', "return _dhw_target(inp)"),
  ("M41 the bound is handed to the grid as the value's own", "thermal_model.py", "grid.bounded(float(value), hi=limit)", "grid.bounded(float(value), hi=float(value))"),
- ("M42 a charge kept at the first step is itself startable on a warm tank", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = bool(on[:1].any())\n    ok[:1] |= on[:1]\n"),
+ ("M42 a charge kept at the first step is itself startable on a warm tank", "dhw_charges.py", "    under_way = bool(on[:1].any())\n", "    under_way = bool(on[:1].any())\n    ok[:1] |= on[:1]\n"),
  ("M43 the notice is never raised", "setpoint_check.py", "        bool(params.dhw_enabled) and start is not None and floor > start,\n", "        False,\n"),
- ("NULL comment-only change", "dhw_planner.py", "    on = plan > 0.0\n    for i in", "    on = plan > 0.0  # null mutant\n    for i in"),
+ ("NULL comment-only change", "dhw_charges.py", "    on = plan > 0.0\n    for i in", "    on = plan > 0.0  # null mutant\n    for i in"),
 ]
 only = sys.argv[2:] 
 for name, f, old, new in M:
diff --git a/dev/audit/harnesses/r10_night_folds_alternatives.py b/dev/audit/harnesses/r10_night_folds_alternatives.py
index e95d309534..4f297e38c8 100644
--- a/dev/audit/harnesses/r10_night_folds_alternatives.py
+++ b/dev/audit/harnesses/r10_night_folds_alternatives.py
@@ -9,6 +9,10 @@
 Command (tree root): PYTHONPATH=tests/hastub:custom_components:tests python3 \\
     dev/audit/harnesses/r10_night_folds_alternatives.py
 This is a measurement record, not a gate.
+
+Production dropped the ridge (R11-SEAM-learners, D2-s3-11), so arm (b) applies
+the round-10 step ``g += a*y - ridge*(g - g0)`` here, after the production fold
+has gated the interval; the unridged arms read production as it stands.
 """
 import sys
 from datetime import datetime, timezone
@@ -41,14 +45,21 @@ class Seat:
         self._internal_gains_profile = None
         self._house_heat_loss_samples = 400
 
+    def _learning_frozen(self, *keys, **kw):
+        """The occupied house: no freeze reason (D7-s2-01 asks the predicate)."""
+        return None
+
 
-def drive(seat, residual_fn, n=400):
+def drive(seat, residual_fn, n=400, ridge=None):
     dark = ThermalState(room_temperature=21.0, outdoor_temperature=0.0)
+    cap = co._zone_capacity(seat._thermal_params)
     for _ in range(n):
         held = (seat._internal_gains_profile or [G0] * 24)[19]
-        Coord._fold_internal_gains(
-            seat, T0, dark, residual_fn(held), 0.5
-        )
+        residual = residual_fn(held)
+        Coord._fold_internal_gains(seat, T0, dark, residual, 0.5)
+        if ridge is not None:  # the round-10 step, ridge and all, from the held value
+            g = held + co.INTERNAL_GAINS_ALPHA * residual * cap / 0.5 - ridge * (held - G0)
+            seat._internal_gains_profile[19] = min(max(g, 0.0), co.INTERNAL_GAINS_MAX_FACTOR * max(G0, 0.05))
     prof = seat._internal_gains_profile or [G0] * 24
     return max(abs(g - G0) for g in prof) / G0
 
@@ -72,8 +83,6 @@ print("RESULT net_of_ua_part.positive_rel_dev=%.4f"
 
 # (b) a ridge that keeps the UA-error drive under 5 %.
 for ridge in (0.02, 0.5, 1.0, 1.5, 2.0):
-    co.INTERNAL_GAINS_RIDGE = ridge
-    ua = drive(Seat(), lambda held: ua_error_residual)
-    pos = drive(Seat(), lambda held: (0.6 - held) * DT / C)
+    ua = drive(Seat(), lambda held: ua_error_residual, ridge=ridge)
+    pos = drive(Seat(), lambda held: (0.6 - held) * DT / C, ridge=ridge)
     print(f"RESULT ridge{ridge:.2f}.ua_rel_dev={ua:.4f} positive_rel_dev={pos:.4f}")
-co.INTERNAL_GAINS_RIDGE = 0.02
diff --git a/dev/audit/harnesses/r10_two_zone_hhl_inert.py b/dev/audit/harnesses/r10_two_zone_hhl_inert.py
index 2cf788cd7b..5f2a21f060 100644
--- a/dev/audit/harnesses/r10_two_zone_hhl_inert.py
+++ b/dev/audit/harnesses/r10_two_zone_hhl_inert.py
@@ -89,7 +89,7 @@ def _sysid_steps(mode: str, extra: dict | None = None) -> list[float | None]:
     steps = []
     for hhl in SWEEP:
         params = _params(mode, hhl, extra)
-        ident = SystemIdentification(SysIdConfig(enabled=True))
+        ident = SystemIdentification(SysIdConfig())
         if not ident.arm(ARM_AT, plant=params):
             raise SystemExit(f"not armed: {ident.result}")
         kw = ident._size_step_power(5.0, 3.0, 20.0, 5.0, HousePlant.of_params(params))
diff --git a/dev/audit/harnesses/r11_honest_dhw_runs.py b/dev/audit/harnesses/r11_honest_dhw_runs.py
new file mode 100644
index 0000000000..eed55dd92f
--- /dev/null
+++ b/dev/audit/harnesses/r11_honest_dhw_runs.py
@@ -0,0 +1,446 @@
+"""R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges shipped as runs, measured on one tree.
+
+    PYTHONPATH=tests/hastub:custom_components:tests \\
+        python3 dev/audit/harnesses/r11_honest_dhw_runs.py fixtures|stores|hysteresis|kernel|tail|combi|seconds
+
+Synthetic throughout; no private data. The finding, the store program and
+the tail are outside pull request 3529's (Bankaifan), which has no finder
+harness; this one prints what the commit stage
+(``dhw_charges.commit_charges``) does to the plans the group's design note
+reads. Nothing here asserts; ``tests/features.py``'s block of the same name
+does.
+
+``fixtures``: the two golden plan scenarios that price a start
+(``cycling_cost``, ``everything_on``), each solved as the tree solves it and
+with the planner handed no ``ChargeRuns`` (the uncommitted plan, what the
+tree shipped before the commit stage). Per solve: hot-water charges, steps
+between the running rule and the floor (all, and those that are not a
+charge's last step), the same for the combined draw, the worst gap under
+the requirement, the start count of the combined draw and of the hot-water
+plan alone, the published starts, energy and ``predicted_cost``. Per build
+of the committed solve: whether a space plan was known, the program's
+rounds beside ``STARTABLE_ROUNDS``, each candidate with the clause that
+refused it or its ranked cost, and which shipped. On a tree without the
+commit stage the two solves are one and the per-build lines are absent.
+
+``stores``: the planner's linear store against its walk (the simulation)
+along each build's uncommitted plan, on the same two fixtures: the largest
+difference in kelvin, which ``_STORE_MARGIN_K`` is sized against.
+
+``hysteresis``: the two fixtures with a start hysteresis injected at ten
+values from 0.5 to 10 K (no golden sets one). Per cell and build: the
+program's rounds, the candidates' verdicts, and how many charges
+``drop_unstartable`` removes from what shipped (the acceptance's start
+clause read back; 0 where it held).
+
+``kernel``: a sha1 over ``runs.commit``'s masks and band verdicts on 1200
+random cases, which a tree before the kernel was generalised prints too: the
+two digests are what the change must not move. Then, on a tree with
+``runs.advance``, the kernel on an affine store with hard bounds and two
+levels against an exhaustive search over nine steps, at 800, 400, 100 and
+20 cells, and the same search with the bounds ignored (the null).
+
+``tail``: starts with a charge's tail allowed against refused on the three
+installs of ``r11_honest_starts_runs.py`` and the combi fixture. Allowed
+means the planner is told the install can end a run inside a step; the
+optimizer's own projection is left as it is, so on a clamped install a tail
+the planner writes is raised to the floor when it ships. Per cell: hot-water
+steps under the floor as planned and as shipped, starts of the combined
+draw, energy and the worst gap under the requirement.
+
+``combi``: the exchange on the combi fixture with a start priced, an install
+that cannot duty-cycle, and neither (the null): rounds, committed builds,
+whether the committed build shipped, steps under the floor and the worst
+gap under the requirement.
+
+``seconds``: CPU seconds (``time.process_time``) of the two fixtures' solves,
+the least of five, as the tree solves them and with the planner handed no
+``ChargeRuns``; on a tree without the commit stage the one arm. The second
+arm on this tree against the one arm on the base tree is the noise this box
+puts on the difference.
+"""
+from __future__ import annotations
+
+import hashlib
+import sys
+import time
+from dataclasses import replace
+from datetime import datetime
+from types import SimpleNamespace
+
+import numpy as np
+
+import heatpump_optimizer.dhw_planner as dp
+import heatpump_optimizer.optimizer as om
+from heatpump_optimizer import runs
+from heatpump_optimizer.thermal_model import MIN_RUNNING_DRAW_KW, ThermalModel, ThermalParameters, ThermalState
+from profiles import solve_inputs
+
+FIXTURES = ("cycling_cost", "everything_on")
+HAS_STAGE = hasattr(dp, "commit_charges")
+# The charge stage's own module where the tree has one; before the move the planner held it.
+try:
+    import heatpump_optimizer.dhw_charges as dc
+except ImportError:
+    dc = dp
+
+
+def low(plan, floor: float) -> tuple[int, int]:
+    """Steps between the running rule and the floor: all, and not a run's last."""
+    plan = np.asarray(plan, float)
+    under = (plan > MIN_RUNNING_DRAW_KW) & (plan < floor - 1e-9)
+    last = np.r_[plan[1:] <= 0.0, True] & np.r_[False, plan[:-1] >= floor - 1e-9]
+    return int(under.sum()), int(np.sum(under & ~last))
+
+
+def charges(plan) -> int:
+    on = np.asarray(plan, float) > 0.0
+    return int(np.sum(on & ~np.r_[False, on[:-1]]))
+
+
+class Watch:
+    """Records every ``commit_charges`` call of the solves run inside it."""
+
+    def __init__(self, committed: bool = True, tails: bool | None = None, hysteresis_k: float | None = None):
+        self.committed, self.tails, self.hysteresis_k = committed, tails, hysteresis_k
+        self.builds: list[dict] = []
+        self.opt = None
+
+    def __enter__(self):
+        self.kept = {"solve": om.HeatPumpOptimizer.optimize}
+        watch = self
+
+        def solve(opt, *, inputs):
+            watch.opt = opt
+            if watch.hysteresis_k is not None:
+                inputs = replace(inputs, state=replace(inputs.state, dhw_start_hysteresis_k=watch.hysteresis_k))
+            return watch.kept["solve"](opt, inputs=inputs)
+
+        om.HeatPumpOptimizer.optimize = solve
+        if not HAS_STAGE:
+            return self
+        self.kept.update(runs_arg=om._charge_runs, stage=dp.commit_charges, refusal=dc.charge_refusal,
+                         plan=dc._StoreProgram.plan)
+
+        def runs_arg(opt, running):
+            got = watch.kept["runs_arg"](opt, running)
+            if got is None or not watch.committed:
+                return None
+            return got if watch.tails is None else got._replace(clamped=not watch.tails)
+
+        def stage(planner, plan, store, limits, forced_off, start_below, space_demand):
+            if planner.charge_runs is None:
+                return watch.kept["stage"](planner, plan, store, limits, forced_off, start_below, space_demand)
+            build = {"space": space_demand is not None, "rounds": 0, "verdicts": [], "plan": np.array(plan)}
+            watch.builds.append(build)
+            ctx = store[0]
+            build["temps_of"] = lambda x: planner._ctx_temps(ctx, store[1], store[2], np.asarray(x, float))
+            build["start_below"], build["requirement"], build["store"] = start_below, limits[0], store
+            floor = runs.floor_kw(planner.model.params.min_electrical_power)
+            space = np.zeros(ctx.n_steps) if space_demand is None else np.clip(space_demand, 0.0, None)
+            build["cost"] = lambda x: float(np.sum(ctx.prices * x) * ctx.dt) + planner.charge_runs.start_cost * (
+                runs.start_count(space + x, floor, planner.charge_runs.running))
+            out = watch.kept["stage"](planner, plan, store, limits, forced_off, start_below, space_demand)
+            build["out"] = np.array(out)
+            return out
+
+        def refusal(candidate, start_below, temps_of, held):
+            got = watch.kept["refusal"](candidate, start_below, temps_of, held)
+            if watch.builds:
+                watch.builds[-1]["verdicts"].append((np.array(candidate), got))
+            return got
+
+        def plan(program, may_start):
+            if watch.builds:
+                watch.builds[-1]["rounds"] += 1
+                watch.builds[-1]["program"] = program
+            return watch.kept["plan"](program, may_start)
+
+        om._charge_runs, dp.commit_charges, dc.charge_refusal, dc._StoreProgram.plan = runs_arg, stage, refusal, plan
+        return self
+
+    def __exit__(self, *exc):
+        om.HeatPumpOptimizer.optimize = self.kept["solve"]
+        if HAS_STAGE:
+            om._charge_runs, dp.commit_charges = self.kept["runs_arg"], self.kept["stage"]
+            dc.charge_refusal, dc._StoreProgram.plan = self.kept["refusal"], self.kept["plan"]
+
+
+def solve_line(label: str, got, opt, floor: float = 1.0) -> None:
+    space, dhw = np.asarray(got["power_schedule"], float), np.asarray(got["dhw_power_schedule"], float)
+    gap = float(np.max(np.asarray(opt._dhw_requirement) - np.asarray(got["dhw_temp_trajectory"], float)[1:]))
+    print(f"{label}: charges {charges(dhw)}, hot-water steps under the floor {low(dhw, floor)[0]}"
+          f" (not a charge's last {low(dhw, floor)[1]}), combined {low(space + dhw, floor)[0]}"
+          f" ({low(space + dhw, floor)[1]}), worst gap {gap:.3f} K,"
+          f" start count combined {runs.start_count(space + dhw, floor):.2f} hot water alone"
+          f" {runs.start_count(dhw, floor):.2f}, published starts {got['compressor_starts']},"
+          f" energy_kwh {float(np.sum(space + dhw)) * 0.25:.2f}, predicted_cost {got['predicted_cost']:.2f}")
+
+
+def build_lines(builds: list[dict]) -> None:
+    for i, b in enumerate(builds):
+        if "out" not in b:
+            continue
+        shipped = "the uncommitted plan" if np.array_equal(b["out"], b["plan"]) else "a committed plan"
+        print(f"  build {i}: space plan known {b['space']}, uncommitted charges {charges(b['plan'])}"
+              f" under the floor {low(b['plan'], 1.0)[0]}, program rounds {b['rounds']} of {dc.STARTABLE_ROUNDS},"
+              f" shipped {shipped} at ranked cost {b['cost'](b['out']):.4f}"
+              f" (the uncommitted plan's {b['cost'](b['plan']):.4f})")
+        for candidate, verdict in b["verdicts"]:
+            kind = "lifted" if np.array_equal(candidate > 0, b["plan"] > 0) else "program"
+            print(f"    {kind} candidate, charges {charges(candidate)}:"
+                  f" {'accepted, ranked cost %.4f' % b['cost'](candidate) if verdict is None else 'refused %s at step %d' % verdict}")
+
+
+def fixtures() -> int:
+    import golden
+
+    for name in FIXTURES:
+        for committed in (True, False) if HAS_STAGE else (True,):
+            with Watch(committed) as w:
+                got = golden.capture(name, golden.SCENARIOS[name])
+            solve_line(f"{name} {'committed' if committed and HAS_STAGE else 'uncommitted'}", got, w.opt)
+            build_lines(w.builds)
+    return 0
+
+
+def stores() -> int:
+    import golden
+
+    if not HAS_STAGE:
+        print("this tree has no commit stage: no store program to compare")
+        return 0
+    for name in FIXTURES:
+        with Watch() as w:
+            golden.capture(name, golden.SCENARIOS[name])
+        for i, b in enumerate(w.builds):
+            if "program" not in b:
+                continue
+            program, (ctx, initial, draws) = b["program"], b["store"]
+            for label, plan in (("uncommitted", b["plan"]), ("shipped", b["out"])):
+                at, line = np.array([initial]), [initial]
+                for k in range(ctx.n_steps):
+                    at = ctx.coast(draws, k, at) + (program._rise(k, at, plan[k]) if plan[k] > 0 else 0.0)
+                    line.append(float(at[0]))
+                print(f"{name} build {i} {label} plan: linear store less walk, largest"
+                      f" {float(np.max(np.abs(np.array(line) - b['temps_of'](plan)))):.4f} K"
+                      f" (margin {dc._STORE_MARGIN_K} K)")
+    return 0
+
+
+def hysteresis() -> int:
+    import golden
+
+    if not HAS_STAGE:
+        print("this tree has no commit stage")
+        return 0
+    for name in FIXTURES:
+        for k in (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0):
+            with Watch(hysteresis_k=k) as w:
+                got = golden.capture(name, golden.SCENARIOS[name])
+            dhw = np.asarray(got["dhw_power_schedule"], float)
+            print(f"{name} hysteresis {k} K: shipped steps under the floor not a charge's last {low(dhw, 1.0)[1]}")
+            for i, b in enumerate(w.builds):
+                if "out" not in b:
+                    continue
+                lost = 0
+                if b["start_below"] is not None:
+                    kept = dc.drop_unstartable(b["out"], b["start_below"], b["temps_of"])
+                    lost = charges(b["out"]) - charges(kept)
+                verdicts = ", ".join("accepted" if v is None else f"{v[0]}@{v[1]}" for _c, v in b["verdicts"])
+                shipped = "uncommitted" if np.array_equal(b["out"], b["plan"]) else "committed"
+                print(f"  build {i}: start condition known {b['start_below'] is not None}, rounds {b['rounds']},"
+                      f" verdicts [{verdicts}], shipped {shipped}, charges drop_unstartable removes from it {lost}")
+    return 0
+
+
+def _small(seed: int, cells: int, bounds: bool = True) -> tuple[float, float]:
+    rng = np.random.default_rng(seed)
+    n, heats, decay, top = 9, (1.0, 2.5), 0.97, 20.0
+    price, drift = rng.uniform(0.5, 2.0, n), rng.uniform(-1.5, -0.2, n)
+    floors, ceiling = rng.uniform(2.0, 6.0, n), float(rng.uniform(9.0, 13.0))
+    start, first = float(rng.choice([0.0, 0.7])), float(rng.uniform(6.0, 9.0))
+    width = top / cells
+
+    def place(k):
+        def rule(v, _charged):
+            j = np.rint(v / width).astype(np.int64)
+            inside = (v >= floors[k]) & (v <= ceiling) & (j >= 0) & (j <= cells)
+            return np.clip(j, 0, cells), np.where(inside, 0.0, np.inf)
+        return rule
+
+    cost = np.full((2, cells + 1), np.inf)
+    val = np.zeros_like(cost)
+    cost[1, int(round(first / width))], val[1, int(round(first / width))] = 0.0, first
+    for k in range(n):
+        actions = ([lambda v, _r, h=h, k=k: (decay * v + drift[k] + h, price[k] * h) for h in heats],
+                   [lambda v, _r, k=k: (decay * v + drift[k], 0.0)])
+        cost, val, _back = runs.advance(cost, val, runs.state_moves(1, 1, np.nan), actions, start, place(k), 1)
+    grid = np.indices((3,) * n).reshape(n, -1).T
+    v, paid = np.full(len(grid), first), np.zeros(len(grid))
+    ok, was = np.ones(len(grid), dtype=bool), np.zeros(len(grid), dtype=bool)
+    for k in range(n):
+        on = grid[:, k] > 0
+        heat = np.where(on, np.take(heats, np.maximum(grid[:, k] - 1, 0)), 0.0)
+        v = decay * v + drift[k] + heat
+        paid += price[k] * heat + start * (on & ~was)
+        if bounds:
+            ok &= (v >= floors[k]) & (v <= ceiling)
+        was = on
+    return float(np.min(np.where(ok, paid, np.inf))), float(np.min(cost))
+
+
+def kernel() -> int:
+    rng = np.random.default_rng(7)
+    digest, cases = hashlib.sha1(), 1200
+    for _ in range(cases):
+        n, dt = int(rng.integers(4, 60)), float(rng.choice([1 / 12, 0.25, 0.5]))
+        floor = float(rng.choice([0.5, 1.0, 1.8]))
+        q = np.where(rng.random(n) < 0.4, 0.0, rng.uniform(0.05, 3.0, n))
+        prices, caps = rng.uniform(0.05, 0.6, n), np.where(rng.random(n) < 0.1, floor * 0.5, 4.0)
+        forced = np.where(rng.random(n) < 0.1, rng.integers(0, 2, n).astype(float), np.nan)
+        mask, tracked = runs.commit(
+            q, prices, floor, caps, float(rng.choice([0.0, 0.3, 1.5])), int(rng.choice(runs.BANDS)), dt=dt,
+            running=bool(rng.integers(0, 2)), forced=forced,
+            lengths=(runs.steps_at_least(runs.MIN_RUN, dt), runs.steps_at_least(runs.MIN_PAUSE, dt)))
+        digest.update(np.packbits(mask).tobytes() + bytes([tracked]))
+    print(f"runs.commit over {cases} random cases: sha1 {digest.hexdigest()}")
+    if not hasattr(runs, "advance"):
+        print("this tree has no runs.advance: no generalised kernel to compare")
+        return 0
+    for cells in (800, 400, 100, 20):
+        rows = [_small(s, cells) for s in range(60)]
+        live = [(b, c) for b, c in rows if np.isfinite(b)]
+        print(f"{cells} cells: kernel cost equals the exhaustive search's on"
+              f" {sum(abs(b - c) <= 1e-9 for b, c in live)} of {len(live)} feasible cases (60 drawn),"
+              f" beats it on {sum(c < b - 1e-9 for b, c in live)}, finds no plan on {sum(not np.isfinite(c) for _b, c in live)}")
+    null = [_small(s, 800, bounds=False) for s in range(60)]
+    print(f"null, the search with the bounds ignored: cheaper than the kernel on"
+          f" {sum(b < c - 1e-9 for b, c in null)} of 60, equal on {sum(abs(b - c) <= 1e-9 for b, c in null)}")
+    return 0
+
+
+def _install_solve(clamp: bool, p_min: float, watch: Watch):
+    params = ThermalParameters()
+    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
+    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
+    params.dhw_enabled = True
+    opt = om.HeatPumpOptimizer(ThermalModel(params), om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=0.3))
+    steps = np.arange(96)
+    outdoor = 2.0 + 3.0 * np.sin(2 * np.pi * (steps - 50) / 96.0)
+    with watch:
+        res = opt.optimize(inputs=solve_inputs(
+            initial_state=ThermalState(
+                room_temperature=20.5, upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+                slab_temperature=21.0, outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
+                dhw_temperature=45.0, dhw_hours_since_legionella=20.0),
+            prices=1.3 + 0.9 * np.sin(2 * np.pi * (steps - 30) / 96.0), outdoor_temps=outdoor,
+            start_time=datetime(2026, 1, 10)))
+    return opt, res
+
+
+def _tail_line(label: str, opt, res, watch: Watch, floor: float) -> None:
+    space, dhw = np.asarray(res.power_schedule, float), np.asarray(res.dhw_power_schedule, float)
+    gap = float(np.max(np.asarray(opt._dhw_requirement) - np.asarray(res.dhw_temp_trajectory, float)[1:]))
+    planned = [b["out"] for b in watch.builds if "out" in b]
+    print(f"{label}: hot-water steps under the floor as planned"
+          f" {low(planned[-1], floor)[0] if planned else 'n/a'} as shipped {low(dhw, floor)[0]},"
+          f" start count combined {runs.start_count(space + dhw, floor):.2f},"
+          f" energy_kwh {float(np.sum(space + dhw)) * 0.25:.2f}, worst gap {gap:.3f} K")
+
+
+def tail() -> int:
+    sys.path.insert(0, __file__.rsplit("/", 1)[0])
+    import r11_honest_starts_runs as hsr
+
+    if not HAS_STAGE:
+        print("this tree has no commit stage")
+        return 0
+    for name, clamp, p_min in hsr.INSTALLS:
+        for tails in (False, True):
+            watch = Watch(tails=tails)
+            opt, res = _install_solve(clamp, p_min, watch)
+            _tail_line(f"{name} (clamped {clamp}, floor {p_min}) tail {'allowed' if tails else 'refused'}",
+                       opt, res, watch, runs.floor_kw(p_min))
+    for tails in (False, True):
+        watch = Watch(tails=tails)
+        opt, res, _calls = _combi_solve(0.0, True, watch)
+        _tail_line(f"combi fixture (clamped True) tail {'allowed' if tails else 'refused'}", opt, res, watch, 1.0)
+    return 0
+
+
+def _combi_solve(cost: float, clamp: bool, watch: Watch | None = None):
+    sys.path.insert(0, __file__.rsplit("/", 1)[0])
+    import r10_combi_tank as ct
+
+    opt = ct.opt_for(ct.params())
+    opt.config = replace(opt.config, cycling_cost=cost, clamp_planned_levels=clamp)
+    real, build, calls = om._combi_flux_exchange, dp.DhwPlanner._build_dhw_requirements, []
+
+    def exchange(o, h, planner, *rest):
+        builds = []
+
+        def counted(self, *a, **k):
+            got = build(self, *a, **k)
+            builds.append((getattr(self, "charge_runs", None) is not None, np.array(got[0].schedule)))
+            return got
+
+        dp.DhwPlanner._build_dhw_requirements = counted
+        try:
+            out = real(o, h, planner, *rest)
+        finally:
+            dp.DhwPlanner._build_dhw_requirements = build
+        calls.append(SimpleNamespace(builds=builds, out=np.array(out)))
+        return out
+
+    om._combi_flux_exchange = exchange
+    prices = np.where((np.arange(96) // 4) % 24 < 6, 0.5, 2.0)
+    try:
+        with watch or Watch():
+            res = opt.optimize(inputs=solve_inputs(
+                initial_state=ct.state(50.0), prices=prices, outdoor_temps=np.full(96, 0.0),
+                wind_speeds=np.zeros(96), precipitation=np.zeros(96), solar_radiation=np.zeros(96),
+                start_time=datetime(2026, 1, 15)))
+    finally:
+        om._combi_flux_exchange = real
+    return opt, res, calls
+
+
+def combi() -> int:
+    for label, cost, clamp in (("a start priced", 0.5, False), ("cannot duty-cycle", 0.0, True), ("null, unengaged", 0.0, False)):
+        opt, res, calls = _combi_solve(cost, clamp)
+        last = calls[-1]
+        rounds = [s for c, s in last.builds if not c]
+        commits = [s for c, s in last.builds if c]
+        if not HAS_STAGE:  # every build is the one planner's, and none commits
+            rounds, commits = [s for _c, s in last.builds], []
+        dhw, space = np.asarray(res.dhw_power_schedule, float), np.asarray(res.power_schedule, float)
+        gap = float(np.max(np.asarray(opt._dhw_requirement) - np.asarray(res.dhw_temp_trajectory, float)[1:]))
+        print(f"combi, {label}: rounds {len(rounds)}, committed builds {len(commits)},"
+              f" committed build shipped {bool(commits) and np.array_equal(commits[-1], last.out)},"
+              f" hot-water steps under the floor {low(dhw, 1.0)[0]} (not a charge's last {low(dhw, 1.0)[1]}),"
+              f" combined {low(space + dhw, 1.0)[0]}, worst gap {gap:.3f} K, dhw_kwh {float(dhw.sum()) * 0.25:.2f}")
+    return 0
+
+
+def seconds() -> int:
+    import golden
+
+    for name in FIXTURES:
+        for committed in (True, False) if HAS_STAGE else (False,):
+            took = []
+            for _ in range(5):
+                with Watch(committed):
+                    t0 = time.process_time()
+                    golden.capture(name, golden.SCENARIOS[name])
+                    took.append(time.process_time() - t0)
+            print(f"{name} {'committed' if committed else 'uncommitted'}: {min(took):.2f} CPU s (least of 5)")
+    return 0
+
+
+ARMS = {"seconds": seconds, "fixtures": fixtures, "stores": stores, "hysteresis": hysteresis, "kernel": kernel, "tail": tail, "combi": combi}
+
+if __name__ == "__main__":
+    if len(sys.argv) != 2 or sys.argv[1] not in ARMS:
+        sys.exit(f"usage: r11_honest_dhw_runs.py {'|'.join(ARMS)}")
+    sys.exit(ARMS[sys.argv[1]]())
diff --git a/dev/audit/harnesses/r11_honest_starts_runs.py b/dev/audit/harnesses/r11_honest_starts_runs.py
index bb455c864b..71089c567a 100644
--- a/dev/audit/harnesses/r11_honest_starts_runs.py
+++ b/dev/audit/harnesses/r11_honest_starts_runs.py
@@ -1,12 +1,25 @@
 """R11-OUTSIDE-HONEST-STARTS-RUNS: what the committed runs ship, measured on one tree.
 
     PYTHONPATH=tests/hastub:custom_components:tests \\
-        python3 dev/audit/harnesses/r11_honest_starts_runs.py fixtures|c1|descents|grid|defaults|gradient|stress|kernels|identity|stage
+        python3 dev/audit/harnesses/r11_honest_starts_runs.py fixtures|c1|descents|grid|defaults|gradient|stress|kernels|identity|stage|approach
 
 Synthetic throughout; no private data. The finding is outside pull request
 3529 (Bankaifan), which has no finder harness; this one reproduces the pull
 request body's figures.
 
+``approach`` (R11-OUTSIDE-START-APPROACH, Bankaifan's comment 6944433306 on
+pull request 3670, whose series are one install's): series D's shape as
+1.25 kW falling 12.6 W/min to a 0.53 kW floor, 5-minute means. Printed: the
+excess over the floor (sum of (kW - 0.53) x 5/60), and runs of 15, 30, 45 and
+60 minutes from off as metered over floor energy; the same shape folded five
+times through ``draw_range.fold`` and the entry energy the learner reads;
+then a clamped 0.53 to 3.0 kW house solved with no approach and with the
+learned one: off-to-on edges per day, shipped and received energy, received
+energy cost, lowest room temperature, and the steps whose received space draw
+passes a 1.0 kW cap the shipped plan keeps. Null controls: a run already at
+the floor has no excess, and the plan with no approach receives its shipped
+array (exits 1 otherwise).
+
 ``fixtures``: the two golden plan scenarios that set a cycling cost
 (``cycling_cost``, ``everything_on``), captured by ``tests/golden.py`` on the
 tree this runs in. Printed per scenario: the space plan's steps between the
@@ -786,7 +799,55 @@ def kernels() -> int:
     return 1 if bad else 0
 
 
+def approach() -> int:
+    import dataclasses
+    from types import SimpleNamespace
+    from heatpump_optimizer import draw_range, runs
+    from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
+    from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState
+    from profiles import solve_inputs
+
+    floor, bin_h = 0.53, 5 / 60
+    shape = [max(1.25 - 0.0126 * 5 * i, floor) for i in range(13)]
+    excess = sum(kw - floor for kw in shape) * bin_h
+    print(f"series D shape: excess over the floor {excess:.3f} kWh over {len(shape) * 5} min")
+    for minutes in (15, 30, 45, 60):
+        k = minutes // 5
+        print(f"  run of {minutes} min from off: metered / floor energy {sum(shape[:k]) / (floor * k):.2f}")
+    null = sum(kw - floor for kw in [floor] * 13) * bin_h
+    print(f"null, a run at the floor: excess {null:.3f} kWh")
+    params = SimpleNamespace(min_electrical_power=floor, max_electrical_power=3.0)
+    draw, t = draw_range.DrawRange(), 1.0e9
+    rows = [(0.02, 0.0)] + ([(kw, floor) for kw in shape[:12]] + [(floor, floor)] * 12 + [(0.785, 0.0)] + [(0.02, 0.0)] * 11) * 5
+    for drawn, ask in rows:
+        draw_range.fold(draw, drawn, (ask, 0.0), params, frozen=False, distorted=False, defrost=False, span=draw_range.Span(t, t + 300))
+        t += 300
+    learned = draw_range.solve_approach(draw, params, t)
+    print(f"learned after five runs: entry {learned.entry_kwh(floor):.3f} kWh over the floor, ramp {learned.ramp}")
+    bad = 0
+    for label, ap in (("no approach", None), ("learned", learned)):
+        opt = HeatPumpOptimizer(
+            ThermalModel(dataclasses.replace(ThermalParameters(), min_electrical_power=floor, max_electrical_power=3.0)),
+            dataclasses.replace(OptimizationConfig(), clamp_planned_levels=True))
+        n, dt = opt.config.n_steps, opt.config.dt_hours
+        prices = 0.2 + 0.1 * np.sin(np.arange(n) * 4 * np.pi / n)
+        state = ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=5.0)
+        inputs = solve_inputs(initial_state=state, prices=prices, outdoor_temps=np.full(n, 5.0),
+                              start_time=datetime(2026, 1, 10, tzinfo=timezone.utc))
+        result = opt.optimize(inputs=dataclasses.replace(inputs, approach=ap))
+        shipped = np.asarray(result.power_schedule)
+        got = runs.received(shipped, 0.0, learned, dt=dt, p_max=3.0)
+        mine = runs.received(shipped, 0.0, ap, dt=dt, p_max=3.0)
+        if ap is None and mine is not shipped:
+            bad += 1
+        print(f"{label}: edges/day {edges(shipped) * 24 / (n * dt):.1f}, shipped {shipped.sum() * dt:.2f} kWh, "
+              f"received {got.sum() * dt:.2f} kWh, received cost {float(np.sum(got * prices)) * dt:.3f}, "
+              f"lowest room {min(result.room_temp_trajectory):.2f} C, steps over a 1.0 kW cap shipped "
+              f"{int(np.sum(shipped > 1.0))} received {int(np.sum(got > 1.0))}")
+    return 1 if bad else 0
+
+
 if __name__ == "__main__":
     sys.exit({"fixtures": fixtures, "c1": c1, "descents": descents, "grid": grid, "defaults": defaults, "gradient": gradient,
               "stress": stress_cost, "kernels": kernels,
-              "identity": identity, "stage": stage}[sys.argv[1]]())
+              "identity": identity, "stage": stage, "approach": approach}[sys.argv[1]]())
diff --git a/dev/audit/harnesses/r11_honest_starts_runs_mutants.json b/dev/audit/harnesses/r11_honest_starts_runs_mutants.json
index c06ae5735d..d762f8920d 100644
--- a/dev/audit/harnesses/r11_honest_starts_runs_mutants.json
+++ b/dev/audit/harnesses/r11_honest_starts_runs_mutants.json
@@ -140,8 +140,8 @@
  {
   "name": "OUT_OF_BAND_PENALTY",
   "file": "custom_components/heatpump_optimizer/runs.py",
-  "old": "        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs]) + fine * outside\n",
-  "new": "        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs])\n"
+  "old": "        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), fine * outside\n",
+  "new": "        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), 0.0 * outside\n"
  },
  {
   "name": "END_BALANCE_HALF_STEP",
@@ -158,8 +158,8 @@
  {
   "name": "START_COST_EDGE",
   "file": "custom_components/heatpump_optimizer/runs.py",
-  "old": "        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts in srcs]) + fine * outside\n",
-  "new": "        c = np.concatenate([cost[s] + paid for s, starts in srcs]) + fine * outside\n"
+  "old": "        c = np.concatenate([cost[s] + paid + start_cost * starts for s, starts, _, _, paid in took]) + extra\n",
+  "new": "        c = np.concatenate([cost[s] + paid for s, starts, _, _, paid in took]) + extra\n"
  },
  {
   "name": "RUN_PAUSE_COUNTS",
@@ -308,13 +308,13 @@
  {
   "name": "REV3_TIE_NOT_ASKED_SIDE_OFF",
   "file": "custom_components/heatpump_optimizer/runs.py",
-  "old": "price[k] * level[k] * dt + _TIE_BREAK * (not asked)),\n",
-  "new": "price[k] * level[k] * dt + 0.0 * (not asked)),\n"
+  "old": "    return _TIE_BREAK * (not asked), _TIE_BREAK * asked\n",
+  "new": "    return 0.0 * (not asked), _TIE_BREAK * asked\n"
  },
  {
   "name": "REV3_TIE_ASKED_SIDE_OFF",
   "file": "custom_components/heatpump_optimizer/runs.py",
-  "old": "            (-q[k] * dt, _TIE_BREAK * asked),\n",
-  "new": "            (-q[k] * dt, 0.0 * asked),\n"
+  "old": "    return _TIE_BREAK * (not asked), _TIE_BREAK * asked\n",
+  "new": "    return _TIE_BREAK * (not asked), 0.0 * asked\n"
  }
 ]
diff --git a/dev/audit/rounds/round10/study-ident/eta_rolling.py b/dev/audit/rounds/round10/study-ident/eta_rolling.py
index 9bc6604d6f..a3094dff1d 100644
--- a/dev/audit/rounds/round10/study-ident/eta_rolling.py
+++ b/dev/audit/rounds/round10/study-ident/eta_rolling.py
@@ -183,6 +183,11 @@ def drift_eta(series, n, cday, gain, rel_tol=0.03, abs_tol=0.0):
     return 0.0 if remaining <= tol else tau * math.log(remaining / tol)
 
 
+#: The round-10 gains ridge this study's figure was taken with; production
+#: deleted the term (R11-SEAM-learners, D2-s3-11), so the value lives here.
+_GAINS_RIDGE_R10 = 0.02
+
+
 def score(rec, truth, total, days, rel_tol=0.03):
     out = {}
     end = total - 1
@@ -192,7 +197,7 @@ def score(rec, truth, total, days, rel_tol=0.03):
     a_s = const_mod.SOLAR_APERTURE_ALPHA * f_up
     n90_s = const_mod.SOLAR_APERTURE_MIN_SAMPLES + math.log(0.1) / math.log(1.0 - a_s)
     # gains: g += a*y - ridge*(g - g0), y re-centred ~ upper-area share of the error
-    a_g = const_mod.INTERNAL_GAINS_ALPHA * 0.5 + const_mod.INTERNAL_GAINS_RIDGE
+    a_g = const_mod.INTERNAL_GAINS_ALPHA * 0.5 + _GAINS_RIDGE_R10
     n90_g = math.log(0.1) / math.log(1.0 - a_g)
     gn = np.cumsum(np.ones(len(rec["g"]))) / 24.0   # folds per hour bucket (4/day at 15 min)
     learners = {
diff --git a/dev/audit/rounds/round11/D2/s3/m5_crosscov.py b/dev/audit/rounds/round11/D2/s3/m5_crosscov.py
index 4ecdb3d001..f8d5a643b6 100644
--- a/dev/audit/rounds/round11/D2/s3/m5_crosscov.py
+++ b/dev/audit/rounds/round11/D2/s3/m5_crosscov.py
@@ -74,7 +74,10 @@ def run(noise, genuine, seed):
     h = SimpleNamespace(_house_heat_loss_scale=1.0, _house_heat_loss_samples=0,
                         _internal_gains_profile=None,
                         _config=SimpleNamespace(internal_gains_learning_enabled=True),
-                        _thermal_params=params)
+                        _thermal_params=params,
+                        # an occupied, clean interval: the fold's own freeze ask
+                        # (R11-SEAM-learners) answers nothing here, as before it
+                        _learning_frozen=lambda *keys, **kw: None)
     t0 = datetime(2026, 1, 1)
     n = int(A.days * 24 / DT_H)
     premature = 0
diff --git a/dev/audit/rounds/round11/D2/s3/m5_drawrange.py b/dev/audit/rounds/round11/D2/s3/m5_drawrange.py
index b8d4570e47..0045f415de 100644
--- a/dev/audit/rounds/round11/D2/s3/m5_drawrange.py
+++ b/dev/audit/rounds/round11/D2/s3/m5_drawrange.py
@@ -45,6 +45,11 @@ from heatpump_optimizer.thermal_model import InstallCapability, ThermalParameter
 
 ap = argparse.ArgumentParser()
 ap.add_argument("--perturb-floor", action="store_true")
+# R11-SEAM-learners companion: 60 run samples leave 29 asked at the configured floor, under
+# draw_range.MIN_SAMPLES (48), so the floor in force stays the configured 1.0 kW and the fix
+# (which reads the floor in force, never DrawRange.observed()) rightly leaves the cell alone.
+# More samples learn the floor the plan uses; the default keeps the finder's figures.
+ap.add_argument("--run-samples", type=int, default=60)
 A = ap.parse_args()
 
 if A.perturb_floor:
@@ -73,20 +78,32 @@ T0 = 1_800_000_000.0
 rng = np.random.default_rng(11)
 
 
+def _ceiling_ask(d, drawn):
+    """The coordinator's ceiling ask (``coordinator._ceiling_frozen``) on a clean cycle: the
+    production predicate on draw_range's evidence. Empty where the tree has neither (a
+    baseline export), so the same file runs at both ends."""
+    try:
+        from heatpump_optimizer import learning_freeze as lf
+    except ImportError:
+        return {}
+    ev = lf.Evidence(at_running_floor=draw_range.at_running_floor(d, drawn))
+    return {"ceiling_frozen": lf.reason(lf.Facts(), (), lf.Sample.CEILING, ev) is not None}
+
+
 def run(cell, top):
     d = draw_range.DrawRange()
     t = T0
-    for k in range(60):
+    for k in range(A.run_samples):
         ask = rng.uniform(1.0, 6.0) if cell == "uncensored" else rng.uniform(1.0, 1.4)
         drawn = max(ask, 1.5) if cell == "uncensored" else 1.5
         drawn = min(drawn, top)
         draw_range.fold(d, drawn, (ask, 0.0), P, frozen=False, distorted=False, defrost=False,
-                        command=None, experiment_s=None)
+                        command=None)
         t += 1800.0
     for k in range(14):
         drawn = top if cell == "uncensored" else 1.5
         draw_range.fold(d, drawn, (6.0, 0.0), P, frozen=False, distorted=False, defrost=False,
-                        command=CEIL, experiment_s=t)
+                        command=CEIL, span=draw_range.Span(t, t, experiment=True), **_ceiling_ask(d, drawn))
         t += 1800.0
     band = draw_range.solve_band(d, P, CAP, t)
     pr = draw_range.planned_range(d, P, CAP)
diff --git a/dev/audit/rounds/round11/D2/s3/m5_sysid.py b/dev/audit/rounds/round11/D2/s3/m5_sysid.py
index 88be0b0b20..a5b2832b56 100644
--- a/dev/audit/rounds/round11/D2/s3/m5_sysid.py
+++ b/dev/audit/rounds/round11/D2/s3/m5_sysid.py
@@ -37,6 +37,9 @@ from datetime import datetime, timedelta, timezone
 sys.path.insert(0, "custom_components")
 import harness  # noqa: F401,E402
 from heatpump_optimizer import sysid  # noqa: E402
+#: The switch: a config field before R11-SEAM-learners (ADR-003), arm's argument (default on)
+#: after it; so the same file runs at both ends.
+_SID_ON = {"enabled": True} if "enabled" in sysid.SysIdConfig.__dataclass_fields__ else {}
 from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
 
 ap = argparse.ArgumentParser()
@@ -89,7 +92,7 @@ def noisy(rows, kind, rng):
 
 
 def fit(samples):
-    si = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
+    si = sysid.SystemIdentification(sysid.SysIdConfig(**_SID_ON))
     si._slab_pair = (CS, KS)
     si._slab_prior = (UA0, CR0)
     si.config.gains_prior_kw = 0.3
diff --git a/dev/audit/rounds/round11/D2/s3/m5_tankfall.py b/dev/audit/rounds/round11/D2/s3/m5_tankfall.py
index ba9b110b48..c8e75ec855 100644
--- a/dev/audit/rounds/round11/D2/s3/m5_tankfall.py
+++ b/dev/audit/rounds/round11/D2/s3/m5_tankfall.py
@@ -71,18 +71,20 @@ def trace(shape, learner, t0, T0):
     T = T0
     t = t0
     dt = timedelta(minutes=10)
-    heat_on = {"short": (2, 2), "long_a": (2, 7), "long_b": (2, 7)}[shape]
+    # unplanned (R11-SEAM-learners, design section 5): long_a's charge with the plan's
+    # flag never set -- the pump charged on its own; the learner sees every sample unheated.
+    heat_on = {"short": (2, 2), "long_a": (2, 7), "long_b": (2, 7), "unplanned": (-1, -1)}[shape]
     for k in range(30):
         heating = heat_on[0] <= k <= heat_on[1]
         rows.append((t, T, heating))
         # evolve to next sample
         sb = learner._standby_rate(T) * (dt.total_seconds() / 3600.0)
         nxt = T - sb
-        if shape == "long_a" and k == 1:
+        if shape in ("long_a", "unplanned") and k == 1:
             nxt -= 4.0          # the dip lands at the first heated sample (k=2)
         if shape == "long_b" and k == 2:
             nxt -= 4.0          # the dip lands at the second heated sample (k=3)
-        if shape in ("long_a", "long_b") and 3 <= k <= 6:
+        if shape in ("long_a", "long_b", "unplanned") and 3 <= k <= 6:
             nxt += 3.0          # the charge climbs, heated
         if shape == "short" and k == 2:
             nxt -= 4.0          # the dip after the one-sample slot (settling)
@@ -93,13 +95,24 @@ def trace(shape, learner, t0, T0):
     return rows
 
 
+def _frozen(key, **kw):
+    """The production predicate on a clean cycle (R11-SEAM-learners), so a refusal the
+    learner asks for reaches it; a baseline export has neither and answers None, as its
+    one-argument fake did."""
+    try:
+        from heatpump_optimizer import learning_freeze as lf
+    except ImportError:
+        return None
+    return lf.reason(lf.Facts(), (key,), kw.get("sample", lf.Sample.ROOM_AIR), kw.get("evidence", lf.NO_EVIDENCE))
+
+
 async def run_cell(kind, shape):
     p = params_for(kind)
     assert p.combi_tank_active, kind
     state = {"heating": False}
     learner = dhw_learning.DhwProfileLearner(
         harness.FakeHass(), "e", lambda: p, publish=lambda **k: None,
-        frozen=lambda _e: None, heating_active=lambda: state["heating"],
+        frozen=_frozen, heating_active=lambda: state["heating"],
         external_heat_active=lambda: False)
 
     async def _noop(*a, **k):
@@ -119,17 +132,21 @@ async def run_cell(kind, shape):
 
 worst_long = 0.0
 worst_short = 0.0
+worst_unplanned = 0.0
 for kind in ("external_station", "internal_coil", "tank_in_tank"):
     parts = []
-    for shape in ("short", "long_a", "long_b"):
+    for shape in ("short", "long_a", "long_b", "unplanned"):
         booked, cap = asyncio.run(run_cell(kind, shape))
         parts.append(f"{shape}:booked={booked:.4f}kWh dip_equiv={4.0 * cap:.4f}kWh")
         if shape == "short":
             worst_short = max(worst_short, abs(booked))
+        elif shape == "unplanned":
+            worst_unplanned = max(worst_unplanned, booked)
         else:
             worst_long = max(worst_long, booked)
     print(f"CELL tank-fall-after-charge combi_tank={kind} cap={cap:.4f}kWh/K " + " ".join(parts))
 dt_util.freeze(None)
 print(f"RESULT booked_kwh_long_max={worst_long:.4f} kWh")
 print(f"RESULT booked_kwh_short_max={worst_short:.4f} kWh")
+print(f"RESULT booked_kwh_unplanned_max={worst_unplanned:.4f} kWh")
 footer()
diff --git a/dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py b/dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py
index e5cd24434b..7991792b1d 100644
--- a/dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py
+++ b/dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py
@@ -44,6 +44,9 @@ import numpy as np  # noqa: E402
 import harness  # noqa: E402,F401  (puts custom_components on the path)
 from heatpump_optimizer import presets  # noqa: E402
 from heatpump_optimizer import sysid as S  # noqa: E402
+#: The switch: a config field before R11-SEAM-learners (ADR-003), arm's argument (default on)
+#: after it; so the same file runs at both ends.
+_SID_ON = {"enabled": True} if "enabled" in S.SysIdConfig.__dataclass_fields__ else {}
 from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState  # noqa: E402
 from profiles import house as _house  # noqa: E402
 from stress import BUILDINGS  # noqa: E402
@@ -74,7 +77,7 @@ def drive(declared: ThermalParameters, true: ThermalParameters, sigma: float, se
     ua_true = true.heat_loss_coefficient * true.house_heat_loss_scale
     gains_true = float(true.internal_gains)
     ua_decl = declared.heat_loss_coefficient * declared.house_heat_loss_scale
-    sid = S.SystemIdentification(S.SysIdConfig(enabled=True, min_days_between_runs=0.0))
+    sid = S.SystemIdentification(S.SysIdConfig(**_SID_ON, min_days_between_runs=0.0))
     if not sid.arm(NOW, plant=declared):
         return sid, None, ua_true
     outdoor = 0.0
@@ -108,7 +111,7 @@ def drive(declared: ThermalParameters, true: ThermalParameters, sigma: float, se
 def verdict(result, declared):
     if result is None or not result.completed or result.heat_loss_kw_per_c is None:
         return None, False, (result.reason if result is not None else "not armed")
-    d = S.adoption_decision(result, declared, S.SysIdConfig(enabled=True))
+    d = S.adoption_decision(result, declared, S.SysIdConfig(**_SID_ON))
     WEIGHT[0] = d.weight
     return result.heat_loss_kw_per_c, d.admit, d.reason
 
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 8ee864b00d..c13a58a057 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=104 measured=104",
+  "result": "documented=107 measured=107",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=104, listed=104, missing=[], phantom=[]",
+  "result": "on disk=107, listed=107, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 1c8141bbcc..beed3c3fb8 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 25 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=25 measured=25 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=104 measured=104 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=104, listed=104, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=107 measured=107 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=107, listed=107, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=36 measured=36 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index c900984b12..6cc1c1ac98 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=104      (103 until R11-OUTSIDE-ROOMS-3B's comfort_floor.py; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=107      (106 until R11-OUTSIDE-ROOMS-3B's comfort_floor.py; 105 until R11-OWNER-FLOWCAP's flow_limit.py; 104 until R11-OUTSIDE-START-APPROACH's approach.py; 103 until R11-SEAM-learners's learning_freeze.py; 102 until R11-OUTSIDE-HONEST-DHW-RUNS's dhw_charges.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=104           (103 until R11-OUTSIDE-ROOMS-3B's comfort_floor.py; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=107           (106 until R11-OUTSIDE-ROOMS-3B's comfort_floor.py; 105 until R11-OWNER-FLOWCAP's flow_limit.py; 104 until R11-OUTSIDE-START-APPROACH's approach.py; 103 until R11-SEAM-learners's learning_freeze.py; 102 until R11-OUTSIDE-HONEST-DHW-RUNS's dhw_charges.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/audit/rounds/round4/D7/sysid_estimator_frontier.py b/dev/audit/rounds/round4/D7/sysid_estimator_frontier.py
index ef003fc108..7ac20c6d1e 100644
--- a/dev/audit/rounds/round4/D7/sysid_estimator_frontier.py
+++ b/dev/audit/rounds/round4/D7/sysid_estimator_frontier.py
@@ -121,6 +121,9 @@ from heatpump_optimizer.sysid import (
     slab_mode_identifiability,
     slab_mode_tau_fast,
 )
+#: The switch: a config field before R11-SEAM-learners (ADR-003), arm's argument (default on)
+#: after it; so the same file runs at both ends.
+_SID_ON = {"enabled": True} if "enabled" in SysIdConfig.__dataclass_fields__ else {}
 from heatpump_optimizer.thermal_model import (
     ThermalModel,
     ThermalParameters,
@@ -169,7 +172,7 @@ def _drive(p: ThermalParameters, sigma: float, seed: int):
     ua = p.heat_loss_coefficient * p.house_heat_loss_scale
     gains = float(p.internal_gains)
     sid = SystemIdentification(
-        SysIdConfig(enabled=True, min_days_between_runs=0.0)
+        SysIdConfig(**_SID_ON, min_days_between_runs=0.0)
     )
     assert sid.arm(START, plant=p)
     ks = max(float(p.slab_heat_transfer), 1e-9)
@@ -289,7 +292,7 @@ def main() -> int:
     for name in BUILDINGS:
         p = _plant(name)
         sy = SystemIdentification(
-            SysIdConfig(enabled=True, min_days_between_runs=0.0)
+            SysIdConfig(**_SID_ON, min_days_between_runs=0.0)
         )
         ok = sy.arm(START, plant=p)
         why = sy.result.reason
diff --git a/dev/programme/delivery/3805.md b/dev/programme/delivery/3805.md
new file mode 100644
index 0000000000..1330321e58
--- /dev/null
+++ b/dev/programme/delivery/3805.md
@@ -0,0 +1 @@
+- [#3805](https://github.com/tvofi/heatpump_optimizer/pull/3805) — **open**, R11-OUTSIDE-HONEST-DHW-RUNS: r11 outside honest dhw runs (R11-OUTSIDE-HONEST-DHW-RUNS)
diff --git a/dev/programme/delivery/3835.md b/dev/programme/delivery/3835.md
new file mode 100644
index 0000000000..9d509d8d64
--- /dev/null
+++ b/dev/programme/delivery/3835.md
@@ -0,0 +1 @@
+- [#3835](https://github.com/tvofi/heatpump_optimizer/pull/3835) — **open**, R11-SEAM-learners: one freeze predicate owns which interval a learner may ingest; the sysid switch is an argument of arm (R11-SEAM-learners)
diff --git a/dev/programme/delivery/3907.md b/dev/programme/delivery/3907.md
new file mode 100644
index 0000000000..a3b37bb848
--- /dev/null
+++ b/dev/programme/delivery/3907.md
@@ -0,0 +1 @@
+- [#3907](https://github.com/tvofi/heatpump_optimizer/pull/3907) — **open**, R11-OUTSIDE-START-APPROACH: a space run's approach to its floor, learned and priced (R11-OUTSIDE-START-APPROACH)
diff --git a/docs/architecture.md b/docs/architecture.md
index 55320afccc..9674e9c382 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 104 modules, of which 36 import the
+knows nothing about Home Assistant: 107 modules, of which 36 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -136,6 +136,7 @@ custom_components/heatpump_optimizer/
 ├── slot_drivers.py       # Why each step runs or idles: five signed driver weights,
 │                         #   and the current step's "why now" for the card
 ├── dhw_planner.py        # The hot-water planner one solve builds: floors, LP, repairs
+├── dhw_charges.py        # The charges the pump would start, and the plan committed as runs
 ├── batchmath.py          # The batched row reduction every batch twin owes its scalar
 ├── process_worker.py     # One-shot interpreter for GIL-bound solves
 ├── open_meteo.py         # Irradiance forecast and satellite observation client
@@ -180,7 +181,10 @@ custom_components/heatpump_optimizer/
 │
 │   # Learning, evidence and self-checks
 ├── accuracy.py           # Predicted versus realised, recorded per interval
+├── learning_freeze.py    # The one freeze predicate: which interval a learner
+│                         #   may ingest, by the kind of sample it folds
 ├── draw_range.py         # The metered running draw, and the range it clamps a plan to
+├── approach.py           # The draw by age after a space run's entry and end (Bankaifan)
 ├── diagnosis.py          # One-input-at-a-time attribution of the last interval's error
 ├── drift.py              # The CUSUM primitive shared by every drift detector
 ├── snapshots.py          # Weekly learner snapshots and the rollback alarm
@@ -297,7 +301,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-36 of the 104 modules import `homeassistant` at module level: `__init__`,
+36 of the 107 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency`, `debugger`, `defrost`,
@@ -306,7 +310,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 67 modules are deliberately free of it, so each can be driven
+The other 70 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/tests/block_duty.py b/tests/block_duty.py
index e469761696..d67d444161 100644
--- a/tests/block_duty.py
+++ b/tests/block_duty.py
@@ -809,7 +809,7 @@ def hysteresis_checks() -> None:
 
     import numpy as np
 
-    from heatpump_optimizer import dhw_planner as planner
+    from heatpump_optimizer import dhw_charges as charges
     from heatpump_optimizer import inputs as inputs_mod
     from heatpump_optimizer import thermal_model as tm
 
@@ -867,16 +867,16 @@ def hysteresis_checks() -> None:
     check("null control: with no cycle active a cycle step holds the everyday set-point",
           lambda: tm.dhw_step_target_c(nocyc, True) == 55.0)
     check("each step's start temperature is its own target less the hysteresis, the cycle step the cycle's",
-          lambda: list(planner.dhw_start_temps(cyc, _start_state(4.0), 6, 3)) == [51, 51, 51, 56, 51, 51]
-          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 6, None)) == [51.0] * 6)
+          lambda: list(charges.dhw_start_temps(cyc, _start_state(4.0), 6, 3)) == [51, 51, 51, 56, 51, 51]
+          and list(charges.dhw_start_temps(cyc, _start_state(4.0), 6, None)) == [51.0] * 6)
     check("a cycle on the first step is judged against its own target; one past the horizon moves no step",
-          lambda: list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 0)) == [56, 51, 51]
-          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 3)) == [51, 51, 51]
-          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 2)) == [51, 51, 56])
+          lambda: list(charges.dhw_start_temps(cyc, _start_state(4.0), 3, 0)) == [56, 51, 51]
+          and list(charges.dhw_start_temps(cyc, _start_state(4.0), 3, 3)) == [51, 51, 51]
+          and list(charges.dhw_start_temps(cyc, _start_state(4.0), 3, 2)) == [51, 51, 56])
     check("with no or zero hysteresis no step has a start temperature",
-          lambda: planner.dhw_start_temps(cyc, _start_state(None), 6, 3) is None
-          and planner.dhw_start_temps(cyc, _start_state(0.0), 6, 3) is None
-          and planner.dhw_start_temps(cyc, _start_state(0.0, _step(5)), 6, 3) is None)
+          lambda: charges.dhw_start_temps(cyc, _start_state(None), 6, 3) is None
+          and charges.dhw_start_temps(cyc, _start_state(0.0), 6, 3) is None
+          and charges.dhw_start_temps(cyc, _start_state(0.0, _step(5)), 6, 3) is None)
 
     # 5. One owner of the target: what the arbiter writes.
     check("the arbiter writes dhw_step_target_c: the everyday set-point with no cycle booked",
@@ -937,17 +937,17 @@ def hysteresis_checks() -> None:
     check("precondition: an everyday 58 on a 5 degC step is written 55, its cycle of 62 written 60",
           lambda: arb._dhw_write(five) == 55.0 and arb._dhw_write(five_cycle) == 60.0)
     check("on a stepped entity each step's start temperature is the written target less the hysteresis",
-          lambda: list(planner.dhw_start_temps(stepped, _start_state(4.0, _step(5)), 4, 2))
+          lambda: list(charges.dhw_start_temps(stepped, _start_state(4.0, _step(5)), 4, 2))
           == [arb._dhw_write(five) - 4.0] * 2 + [arb._dhw_write(five_cycle) - 4.0, arb._dhw_write(five) - 4.0]
           == [51.0, 51.0, 56.0, 51.0])
     check("null control: with no set-point entity the same parameters start below 58 and 62 less the hysteresis",
-          lambda: list(planner.dhw_start_temps(stepped, _start_state(4.0), 4, 2)) == [54.0, 54.0, 58.0, 54.0])
+          lambda: list(charges.dhw_start_temps(stepped, _start_state(4.0), 4, 2)) == [54.0, 54.0, 58.0, 54.0])
     check("the ledger's start temperature on the stepped entity is the planner's",
           lambda: arb._dhw_start_below_c(replace(five, state=_start_state(4.0, _step(5)))) == 51.0
           and arb._dhw_start_below_c(replace(five_cycle, state=_start_state(4.0, _step(5)))) == 56.0)
 
     # 6. Which steps the pump starts.
-    startable = planner.startable_steps
+    startable = charges.startable_steps
     check("a step is startable where it opens on a tank below its start temperature or follows a charge under way",
           lambda: list(startable(np.array([0, 0, 1, 0, 0.]), np.array([54, 52, 50, 53, 50.9, 50.]),
                                  np.full(5, 51.0))) == [False, False, True, True, True])
@@ -981,7 +981,7 @@ def hysteresis_checks() -> None:
 
     plan = np.array([1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0])
     kept = plan.copy()
-    drop = planner.drop_unstartable
+    drop = charges.drop_unstartable
     check("a charge begun above its start temperature is dropped whole; the first step and a cooled tank's run are kept",
           lambda: list(drop(plan, np.full(8, 51.0), temps_of)) == [1, 0, 0, 0, 0, 0, 0, 1])
     check("a tank exactly at the start temperature does not start",
@@ -1002,7 +1002,7 @@ def hysteresis_checks() -> None:
 
     marker = np.array([0.0, 1.0])
     check("with no start temperature the repair's own answer stands and no trajectory is read",
-          lambda: planner.place_startable(plan, None, raises, lambda plan: marker) is marker)
+          lambda: charges.place_startable(plan, None, raises, lambda plan: marker) is marker)
     calls, original = [], plan
 
     def stubborn(plan, start_below):
@@ -1010,16 +1010,16 @@ def hysteresis_checks() -> None:
         return original.copy()
 
     check("a repair that keeps re-placing the unstartable plan still leaves a plan with none, in bounded rounds",
-          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, stubborn))
+          lambda: list(charges.place_startable(plan, np.full(8, 51.0), temps_of, stubborn))
           == list(drop(plan, np.full(8, 51.0), temps_of))
-          and 1 <= len(calls) <= planner.STARTABLE_ROUNDS)
+          and 1 <= len(calls) <= charges.STARTABLE_ROUNDS)
     rounds = []
 
     def counting(plan, start_below):
         rounds.append(1)
         return plan
 
-    planner.place_startable(plan, np.full(8, 51.0), temps_of, counting)
+    charges.place_startable(plan, np.full(8, 51.0), temps_of, counting)
     check("a repair that changes nothing ends the loop: one round to drop, one to see the plan stand",
           lambda: len(rounds) == 2)
     turns = []
@@ -1031,12 +1031,12 @@ def hysteresis_checks() -> None:
         out[4] = float(len(turns) % 2)
         return out
 
-    settled = planner.place_startable(plan, np.full(8, 51.0), temps_of, restless)
+    settled = charges.place_startable(plan, np.full(8, 51.0), temps_of, restless)
     check("a repair that never settles is asked the documented eight rounds, and what leaves still holds no unstartable charge",
-          lambda: planner.STARTABLE_ROUNDS == 8 and len(turns) == 8
+          lambda: charges.STARTABLE_ROUNDS == 8 and len(turns) == 8
           and np.array_equal(settled, drop(settled, np.full(8, 51.0), temps_of)))
     check("an identity repair leaves the dropped plan",
-          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, lambda plan, start_below: plan))
+          lambda: list(charges.place_startable(plan, np.full(8, 51.0), temps_of, lambda plan, start_below: plan))
           == list(drop(plan, np.full(8, 51.0), temps_of)))
 
     # 8b. The clamp-then-zero step the placement stages share.
diff --git a/tests/closures.json b/tests/closures.json
index 8aa9d54129..7ec9255bf8 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -172,6 +172,7 @@
   "tests/arch_score_head.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -200,6 +201,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -230,6 +232,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -322,9 +325,11 @@
   "tests/backtest.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/comfort_floor.py",
    "custom_components/heatpump_optimizer/const.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
@@ -366,6 +371,7 @@
   "tests/block_duty.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -386,6 +392,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -414,6 +421,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -500,6 +508,7 @@
   "tests/boost_drift_replay.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -513,6 +522,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -539,6 +549,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -616,6 +627,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -629,6 +641,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -655,6 +668,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -746,6 +760,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -759,6 +774,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -785,6 +801,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -872,6 +889,7 @@
   "tests/config_flow_steps.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -892,6 +910,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -920,6 +939,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1025,6 +1045,7 @@
   "tests/cycle_lane.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1038,6 +1059,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1064,6 +1086,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1139,6 +1162,7 @@
   "tests/debug_collect.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1154,6 +1178,7 @@
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1181,6 +1206,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1264,6 +1290,7 @@
   "tests/deployment_shape.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1292,6 +1319,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1322,6 +1350,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1422,6 +1451,7 @@
    "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1442,6 +1472,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1471,6 +1502,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1717,9 +1749,11 @@
   "tests/edge.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/comfort_floor.py",
    "custom_components/heatpump_optimizer/const.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
@@ -1813,6 +1847,7 @@
    "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1841,6 +1876,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1871,6 +1907,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2366,6 +2403,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2394,6 +2432,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2424,6 +2463,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2584,6 +2624,7 @@
    "blueprints/automation/notifications.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2604,6 +2645,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2632,6 +2674,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2752,6 +2795,7 @@
   "tests/finite_boundary.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2772,6 +2816,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2800,6 +2845,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2901,6 +2947,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2929,6 +2976,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2959,6 +3007,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3120,6 +3169,7 @@
   "tests/guard_pins.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3133,6 +3183,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3159,6 +3210,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3295,6 +3347,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3315,6 +3368,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3344,6 +3398,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3708,6 +3763,7 @@
   "tests/manual_plan.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3724,6 +3780,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3751,6 +3808,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3857,9 +3915,11 @@
   "tests/optimality.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/comfort_floor.py",
    "custom_components/heatpump_optimizer/const.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
@@ -3901,6 +3961,7 @@
   "tests/plan_view.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3914,6 +3975,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3940,6 +4002,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -4018,6 +4081,7 @@
   "tests/solar_alignment.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4031,6 +4095,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4057,6 +4122,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -4131,9 +4197,11 @@
   "tests/stress.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/comfort_floor.py",
    "custom_components/heatpump_optimizer/const.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
@@ -4180,6 +4248,7 @@
   "tests/structure.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4200,6 +4269,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4228,6 +4298,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -4289,6 +4360,7 @@
   "tests/typing_ruler.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4309,6 +4381,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4337,6 +4410,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -4398,9 +4472,11 @@
   "tests/validate.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/comfort_floor.py",
    "custom_components/heatpump_optimizer/const.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
@@ -4441,6 +4517,7 @@
    "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4455,6 +4532,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4481,6 +4559,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -4960,6 +5039,7 @@
    "dev/audit/harnesses/r11_comments_ratchet_mutants.py",
    "dev/audit/harnesses/r11_comments_ratchet_reconcile.py",
    "dev/audit/harnesses/r11_denominator_planted.py",
+   "dev/audit/harnesses/r11_honest_dhw_runs.py",
    "dev/audit/harnesses/r11_honest_starts_runs.py",
    "dev/audit/harnesses/r11_kernel_step_agree.py",
    "dev/audit/harnesses/r11_main_cancel_mutants.py",
@@ -6313,7 +6393,7 @@
    "seconds": 3.3
   },
   "tests/doc_claims.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 31.0
   },
   "tests/dst_checks.py": {
@@ -6325,7 +6405,7 @@
    "seconds": 60.2
   },
   "tests/entities.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 1338.1
   },
   "tests/env_drift.py": {
@@ -6333,11 +6413,11 @@
    "seconds": 1.0
   },
   "tests/features.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 1616.7
   },
   "tests/finite_boundary.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 96.8
   },
   "tests/frontend.py": {
@@ -6350,14 +6430,14 @@
   },
   "tests/guard_pins.py": {
    "rc": 0,
-   "seconds": 18.2
+   "seconds": 8.7
   },
   "tests/ha_contract.py": {
    "rc": 0,
    "seconds": 0.2
   },
   "tests/harness_headers.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 159.7
   },
   "tests/layout.py": {
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index ddc4836ea5..d9bde0e09b 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 123
+records every read, so this lane's recorded closure is the package: all 126
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (122 until R11-OUTSIDE-ROOMS-3B's ``comfort_floor.py``, 121 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 120 until R11-SEAM-cycle-solve's ``solve_gate.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (125 until R11-OUTSIDE-ROOMS-3B's ``comfort_floor.py``, 124 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 123 until R11-OUTSIDE-START-APPROACH's ``approach.py``, 122 until R11-SEAM-learners's ``learning_freeze.py``, 121 until R11-OUTSIDE-HONEST-DHW-RUNS's ``dhw_charges.py``, 120 until R11-SEAM-cycle-solve's ``solve_gate.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
@@ -57,16 +57,21 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 184 of the 561 script pairs (34 choose 2) sharing 0.80 or more
-of their production-module closure (186 on R11-OUTSIDE-ROOMS-3B's branch and 182 on
-main before the merge joining them, main's R11-SEAM-entity-service services.yaml
-having taken config_flow_steps.py's pairs with debug_collect.py and wood_advisor.py
-under 0.80, 184 on main and 180 on that branch before it landed; on the rooms-3b
-branch, 184 on each side before the merge joining
-R11-OWNER-FLOWCAP's flow_limit.py and R11-OUTSIDE-ROOMS-3B's comfort_floor.py, which put
-card_drift.mjs and wood_advisor.py each with features.py at the 0.80 floor; 182
-before flow_limit.py on main and comfort_floor.py on its branch each lifted
-env_drift.py/manual_plan.py and golden.py/manual_plan.py to 0.80; 169 of 528 before R11-SEAM-tests's
+recording finds 192 of the 561 script pairs (34 choose 2) sharing 0.80 or more
+of their production-module closure (195 on R11-OUTSIDE-START-APPROACH's branch and 182 on main
+before the merge joining R11-SEAM-entity-service's services.yaml to approach.py's
+recordings; 184 on main and 180 on R11-SEAM-entity-service's branch before the
+merge joining them, the branch's services.yaml having taken config_flow_steps.py's
+pairs with debug_collect.py and wood_advisor.py under 0.80; 191 on
+R11-OUTSIDE-START-APPROACH's branch and 184 on main
+before the merge joining R11-OWNER-FLOWCAP's flow_limit.py to approach.py's
+recordings; 184 on R11-OUTSIDE-HONEST-DHW-RUNS's and
+R11-SEAM-learners's branches before R11-OUTSIDE-START-APPROACH re-recorded the
+28 closures that read approach.py; 182 on each side before the merge joining
+R11-SEAM-cycle-solve's solve_gate.py and R11-OUTSIDE-HONEST-DHW-RUNS's
+dhw_charges.py, which together lifted tests/golden.py/manual_plan.py and
+tests/env_drift.py/manual_plan.py to 0.80, and on main 182 before
+R11-OWNER-FLOWCAP's flow_limit.py joined its closures, adding the same two pairs; 169 of 528 before R11-SEAM-tests's
 cycle_lane.py, whose closure opens the whole package, and 180 on its branch
 before the merge bringing R11-SEAM-actuation-release's three production
 modules; 167 before both; 164 on each side before the merge joining
@@ -74,7 +79,7 @@ R11-OUTSIDE-ROOMS-P1's rooms.py, read by every closure that imports the
 coordinator, the input reader, the config flow or the sensor platform, and
 R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which joined
 config_flow_steps.py/debug_collect.py at 0.80; 162 before #3616 re-recorded the
-closures that import the coordinator), all 184 among the 435 pairs whose two
+closures that import the coordinator), all 192 among the 435 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
diff --git a/tests/dst_checks.py b/tests/dst_checks.py
index f15ac60f6b..1ce653e680 100644
--- a/tests/dst_checks.py
+++ b/tests/dst_checks.py
@@ -2045,7 +2045,7 @@ R.check(
 )
 
 # sysid: the 30-day arm gap and the phase clock
-_si = _sysid.SystemIdentification(_sysid.SysIdConfig(enabled=True))
+_si = _sysid.SystemIdentification(_sysid.SysIdConfig())
 _si.last_run = datetime(
     2026, 9, 25, 5, 0, tzinfo=STHLM
 )  # 30 true days and 30 min, 29 d 23 h 30 min wall
@@ -2057,7 +2057,7 @@ R.check(
 
 
 def _sysid_phase(started, now, phase):
-    si = _sysid.SystemIdentification(_sysid.SysIdConfig(enabled=True))
+    si = _sysid.SystemIdentification(_sysid.SysIdConfig())
     si.phase, si.phase_started, si._baseline_temp = phase, started, 20.0
     si.step(
         now=now,
@@ -2285,7 +2285,7 @@ def _sid_samples(label):
 
 
 def _sid_with(label):
-    si = _sysid.SystemIdentification(_sysid.SysIdConfig(enabled=True))
+    si = _sysid.SystemIdentification(_sysid.SysIdConfig())
     si.samples = _sid_samples(label)
     return si
 
diff --git a/tests/entities.py b/tests/entities.py
index a5678e6a4c..a2a77d354f 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4210,8 +4210,6 @@ def _p2_registry(sources):
                      "an elapsed time in hours (the pairing window's lower edge), not a power",
                  "dhw_learning.py::DhwProfileLearner.async_learn_usage":
                      "a tank draw intensity in K/h, not a power",
-                 "dhw_planner.py::DhwPlanner._dhw_shortfall":
-                     "a tank temperature gap in K, not a power",
                  "ledger.py::freeze_month_report":
                      "a month-report reconciliation tolerance in kWh and SEK, not a power",
                  "narrative.py::build":
@@ -4241,13 +4239,19 @@ def _p2_registry(sources):
              match=_p2_match_defrost_decides,
              owners=["freq_control.py::defrost_interval"],
              dispositions={
-                 "coordinator.py::HeatPumpOptimizerCoordinator._learning_frozen":
+                 # R11-SEAM-learners (ADR-008): the gate moved out of
+                 # ``_learning_frozen``; the coordinator reads the flag into
+                 # the facts, and the predicate module decides on it.
+                 "learning_freeze.py::_shared":
                      "the plant-wide gate: it decides whether ANY learner "
                      "ingests the interval and owns the reason string it "
                      "returns. The frequency map deliberately folds intervals "
                      "that gate freezes (external heat, #781), so the "
                      "frequency pair's own predicate decides the two "
                      "frequency questions the gate cannot express",
+                 "coordinator.py::_freeze_facts":
+                     "the gate's input: it copies the pump's defrost flag into "
+                     "the facts learning_freeze._shared decides on, deciding nothing",
              }),
         # R10-CLONE-2238 (#2238): the F5_clone instances, one fact per entry,
         # each routed through one owner in the module that held both copies.
@@ -4639,11 +4643,7 @@ _p2_planted = {
         {**_P2_SOURCES, "topology.py": _P2_SOURCES["topology.py"] + plant}, _P2_REGISTRY))
     for fact, plant in _P2_PLANTS.items()
 }
-_P2_FENCE_RECORD = (
-    "await _best_effort_cycle_step(\n"
-    "                self._record_accuracy, \"Accuracy pairing skipped: %s\"\n"
-    "            )"
-)
+_P2_FENCE_RECORD = 'await _best_effort_cycle_step(self._record_accuracy, "Accuracy pairing skipped: %s")'
 _p2_unfenced = _p2_fails(_p2_scan(
     {**_P2_SOURCES, "coordinator.py": _P2_SOURCES["coordinator.py"].replace(
         _P2_FENCE_RECORD, "await self._record_accuracy()")}, _P2_REGISTRY))
diff --git a/tests/features.py b/tests/features.py
index d6d6dd0124..76c4c557d7 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -978,7 +978,7 @@ R.check(
 # it is the null control: learning proceeds exactly as before.
 _np_dhw = DhwProfileLearner(
     FakeHass(), "np", **_owned_params(ThermalParameters()),
-    frozen=lambda *a: None, heating_active=lambda: False,
+    frozen=lambda *a, **_kw: None, heating_active=lambda: False,
     external_heat_active=lambda: False,
 )
 _np_refusal = _np_aio.run(_np_dhw.async_learn_dynamics(-127.0))
@@ -2621,7 +2621,7 @@ R.check(
 
 # D2-s4-02: the step is sized under the abort bound by the noise headroom, on
 # the heavy default house (#779's own cell), and still uses the rest of it.
-_r9f41_sid = SystemIdentification(SysIdConfig(enabled=True))
+_r9f41_sid = SystemIdentification(SysIdConfig())
 _r9f41_el = _r9f41_sid._size_step_power(6.0, 3.0, 21.0, 2.0, HousePlant(ua=0.20, capacity=8.0, gains=0.3))
 _r9f41_peak, _r9f41_final = _r9f41_sysid._predict_step_excursion_plant(
     HousePlant(ua=0.20, capacity=8.0, gains=0.3), 21.0, 2.0,
@@ -7913,12 +7913,12 @@ R.check(
 # ===========================================================================
 R.section("Active system identification (item 18)")
 
-sysid = SystemIdentification(SysIdConfig(enabled=True))
+sysid = SystemIdentification(SysIdConfig())
 R.check("arming works when enabled", sysid.arm(NOW) and sysid.phase == PHASE_ARMED)
 R.check("arming twice is a no-op", not sysid.arm(NOW))
 
-disabled_sysid = SystemIdentification(SysIdConfig(enabled=False))
-R.check("a disabled experiment cannot be armed", not disabled_sysid.arm(NOW))
+disabled_sysid = SystemIdentification(SysIdConfig())
+R.check("a disabled experiment cannot be armed", not disabled_sysid.arm(NOW, enabled=False))
 
 night = datetime(2026, 2, 1, 1, 0, tzinfo=UTC)
 cheap = np.linspace(0.5, 2.0, 96)
@@ -7946,7 +7946,6 @@ R.check(
 # A synthetic house, driven through a whole experiment.
 run_sysid = SystemIdentification(
     SysIdConfig(
-        enabled=True,
         settle_hours=0.5,
         step_hours=2.0,
         relax_hours=2.0,
@@ -8000,7 +7999,7 @@ if result.completed:
 
 # Comfort is a hard constraint on the experiment, not a cost term.
 strict = SystemIdentification(
-    SysIdConfig(enabled=True, settle_hours=0.0, max_excursion_c=0.2)
+    SysIdConfig(settle_hours=0.0, max_excursion_c=0.2)
 )
 strict.arm(night)
 strict.step(
@@ -8017,7 +8016,7 @@ R.check(
 )
 R.check("the abort is recorded with a reason", "excursion" in strict.result.reason)
 
-no_data = SystemIdentification(SysIdConfig(enabled=True))
+no_data = SystemIdentification(SysIdConfig())
 R.check(
     "a fit with no samples fails cleanly",
     not no_data.identify().completed,
@@ -8035,7 +8034,7 @@ from heatpump_optimizer.sysid import (
     SysIdSample as _SID_SAMPLE,
 )
 
-_impossible = SystemIdentification(SysIdConfig(enabled=True))
+_impossible = SystemIdentification(SysIdConfig())
 _impossible.samples = []
 _imp_room, _imp_when = 20.7, datetime(2026, 2, 1, 0, 0, tzinfo=UTC)
 for _imp_phase, _imp_power, _imp_steps in (
@@ -8058,7 +8057,7 @@ R.check(
     f"ua={_impossible_res.heat_loss_kw_per_c}",
 )
 
-repeat = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=30))
+repeat = SystemIdentification(SysIdConfig(min_days_between_runs=30))
 repeat.last_run = NOW - timedelta(days=2)
 R.check("a recent run blocks another", not repeat.arm(NOW))
 
@@ -8076,7 +8075,7 @@ from heatpump_optimizer.sysid import slab_mode_identifiability as _sid_idable
 _sid_plant = ThermalParameters()
 R.check(
     "the default plant passes the arm-time identifiability gate",
-    _sid_idable(_sid_plant, SysIdConfig(enabled=True))[0],
+    _sid_idable(_sid_plant, SysIdConfig())[0],
     "production arms with a declared plant; the gate must accept it, or the "
     "production sequence the pin below drives is not the production one",
 )
@@ -8101,7 +8100,6 @@ SystemIdentification.identify_slab = _sid_count(_sid_identify_slab, "identify_sl
 def _sid_drive(with_plant):
     experiment = SystemIdentification(
         SysIdConfig(
-            enabled=True,
             settle_hours=0.5,
             step_hours=2.0,
             relax_hours=2.0,
@@ -8601,7 +8599,7 @@ class _CopGate:
         self._flow_bias = flow_lift.FlowCurveBias()
         self.cop_health_calls: list = []
 
-    def _learning_frozen(self, *entities, room_air=True):
+    def _learning_frozen(self, *entities, **_kw):
         return None
 
     def _observe_cop_health(self, observed_cop, dhw_curve=False):
@@ -8688,7 +8686,7 @@ class _DhwUsage(DhwProfileLearner):
             FakeHass(),
             "dhw-usage",
             **_owned_params(ThermalParameters()),
-            frozen=lambda *_: None,
+            frozen=lambda *_, **_kw: None,
             heating_active=lambda: False,
             external_heat_active=lambda: False,
         )
@@ -9319,7 +9317,7 @@ _nf_learner = _DhwUsage()
 # (_DhwUsage overwrites its own seed with a flat profile).
 _nf_default = DhwProfileLearner(
     FakeHass(), "nf", **_owned_params(ThermalParameters()),
-    frozen=lambda *a: None, heating_active=lambda: False,
+    frozen=lambda *a, **_kw: None, heating_active=lambda: False,
     external_heat_active=lambda: False,
 ).hourly_profile
 _nf_profile = _nf_learner.normalize_profile(
@@ -12102,7 +12100,9 @@ _ct_blind = [n.lineno for n in _ct_walk_calls
 _ct_fns = {n.name: _ct_ast.get_source_segment(_ct_sources["dhw_planner.py"], n)
            for n in _ct_ast.walk(_ct_plan_tree) if isinstance(n, _ct_ast.FunctionDef)}
 _ct_affine = [f for f in ("_plan_dhw_min_cost", "_dhw_legionella_ceilings", "_clamp_dhw_to_capacity")
-              if "_exo_at(" not in _ct_fns.get(f, "")]
+              if "_exo_at(" not in _ct_fns.get(f, "")
+              # the linear program's recursion is the context's (R11-OUTSIDE-HONEST-DHW-RUNS)
+              and not ("ctx.coast(" in _ct_fns.get(f, "") and "_exo_at(self.tank_exo_kw" in _ct_fns.get("coast", ""))]
 _ct_space = [f for f in ("def simulate_trajectory(", "def simulate_trajectory_batch(")
              if f not in _ct_sources["thermal_model.py"]
              or "buffer_exo = weather.buffer_exo_kw" not in _ct_sources["thermal_model.py"].split(f)[1][:4000]]
@@ -23625,9 +23625,11 @@ _before53 = _c53._internal_gains_profile[19]
 for _ in range(200):
     _c53._fold_internal_gains(_when53, _st53d, 0.0, 0.5)
 R.check(
-    "with the evidence gone the ridge pulls the hour back toward the prior",
-    _c53._internal_gains_profile[19] < _before53
-    and _c53._internal_gains_profile[19] < _g0 + 0.05,
+    "with the evidence gone the hour holds what it learned: no ridge pulls it back toward the "
+    "prior, whose fixed point was alpha/(alpha+ridge) of the true gain (D2-s3-11); the clip "
+    "above and the convergence gate tether it",
+    _c53._internal_gains_profile[19] == _before53 and _before53 > _g0 + 0.1,
+    f"hour 19 {_c53._internal_gains_profile[19]} vs learned {_before53} prior {_g0}",
 )
 _st53s = replace(_c53._current_state)
 _st53s.solar_radiation = 300.0
@@ -29940,7 +29942,7 @@ def _drifting_sid_samples(
 
 
 def _sid_on(samples, **cfg):
-    _s = SystemIdentification(SysIdConfig(enabled=True, **cfg))
+    _s = SystemIdentification(SysIdConfig(**cfg))
     _s.samples = samples
     return _s.identify()
 
@@ -30035,7 +30037,7 @@ def _drive_sysid_step(ua, cap, gains, cop, max_el=5.0, cadence_min=30, size=True
     The sizer (#779) uses the two-state plant; these historical pins
     characterize ``identify()``, which is still a room-only lumped UA.
     """
-    sid = SystemIdentification(SysIdConfig(enabled=True))
+    sid = SystemIdentification(SysIdConfig())
     t0 = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
     sid.arm(t0)
     temp, tout = 21.0, 2.0
@@ -30075,7 +30077,7 @@ from heatpump_optimizer.thermal_model import ThermalState as _SidPlantState
 
 def _drive_sysid_step_plant(ua, cap, gains, cop, max_el=5.0, cadence_min=15, size=True):
     """Drive an experiment on the two-state plant the sizer uses (#779)."""
-    sid = SystemIdentification(SysIdConfig(enabled=True))
+    sid = SystemIdentification(SysIdConfig())
     t0 = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
     sid.arm(t0)
     tout = 2.0
@@ -30142,7 +30144,7 @@ R.check(
 )
 _g5_null = _drive_sysid_step(0.20, 8.0, 0.3, 1.0, max_el=6.0)
 _g5_sr = [s for s in _g5_null.samples if s.phase in (_PH_STEP, _PH_RELAX)]
-_g5_sr_sid = SystemIdentification(SysIdConfig(enabled=True))
+_g5_sr_sid = SystemIdentification(SysIdConfig())
 _g5_sr_sid.samples = _g5_sr
 _g5_sr_res = _g5_sr_sid.identify()
 _g5_full = _g5_null.identify()
@@ -30189,7 +30191,7 @@ R.check(
 
 # --- #779: size on the two-state plant, not the one-state exponential ------
 R.section("sysid step sized on the two-state plant (#779)")
-_779_sid = SystemIdentification(SysIdConfig(enabled=True))
+_779_sid = SystemIdentification(SysIdConfig())
 _779_el = _779_sid._size_step_power(6.0, 3.0, 21.0, 2.0, HousePlant(ua=0.20, capacity=8.0, gains=0.3))
 _779_q = (_779_el or 0.0) * 3.0
 _779_plant, _779_final = _predict_step_excursion_plant(
@@ -30212,7 +30214,7 @@ R.check(
     f"one-state {_779_one:.3f} plant {_779_plant:.3f}",
 )
 _settle_sid = SystemIdentification(
-    SysIdConfig(enabled=True, settle_hours=0.5, step_hours=2.0, relax_hours=2.0)
+    SysIdConfig(settle_hours=0.5, step_hours=2.0, relax_hours=2.0)
 )
 _settle_sid.arm(datetime(2026, 2, 1, 23, 0, tzinfo=UTC))
 _settle_t = datetime(2026, 2, 1, 23, 0, tzinfo=UTC)
@@ -34564,6 +34566,7 @@ class _Split:
         self._measured_power = measured
         self._immersion_active = False
         self._pump_signals = signals
+        self._accuracy = AccuracyTracker()  # R11-OUTSIDE-START-APPROACH: the tracking gate reads its draw window
 
 
 _sp_blind = _Split(PumpSignals())
@@ -38901,8 +38904,10 @@ _PKG_DIR = _Path("custom_components/heatpump_optimizer")
 class _SysIdHost:
     _run_system_identification = Coord._run_system_identification
     # #1523: the experiment consults the production freeze predicate, which
-    # reads these three besides the pump signals; all clear here.
+    # reads these four besides the pump signals; all clear here. Its ask is a
+    # space-heat one, so it reads the commanded split too (R11-SEAM-learners).
     _learning_frozen = Coord._learning_frozen
+    _commanded_split = Coord._commanded_split
 
     def __init__(self, signals) -> None:
         self.hass = FakeHass()  # #1658: the step is awaited off the loop
@@ -38910,8 +38915,9 @@ class _SysIdHost:
         self._external_heat_active = False
         self._input_health = None
         self._vent_cusum = type("_Vent", (), {"tripped": False})()
+        self._away_state = away_mode.AwayState()
         self._sysid = _SysIdModule.SystemIdentification(
-            _SysIdModule.SysIdConfig(enabled=True)
+            _SysIdModule.SysIdConfig()
         )
         self._sysid.arm(datetime(2026, 1, 5, 2, 0, tzinfo=UTC))
         self._current_action = {"power": 0.0, "heat_pump_on": False}
@@ -55290,7 +55296,7 @@ R.check(
     _g1401_short is None,
 )
 _g1401_window = SystemIdentification(
-    _SysIdModule.SysIdConfig(enabled=True, start_hour=1, end_hour=5)
+    _SysIdModule.SysIdConfig(start_hour=1, end_hour=5)
 )
 _g1401_window_ok, _g1401_window_why = _g1401_window.conditions_met(
     datetime(2026, 2, 1, 3, 0, tzinfo=UTC), 2.0, 0.55, np.linspace(0.5, 2.0, 96), 5
@@ -55305,7 +55311,7 @@ _g1401_plant = ThermalParameters()
 # non-positive room mass up on construction, so only the slab coupling can be
 # driven to zero here.
 _g1401_plant.slab_heat_transfer = 0.0
-_g1401_unseedable = SystemIdentification(_SysIdModule.SysIdConfig(enabled=True))
+_g1401_unseedable = SystemIdentification(_SysIdModule.SysIdConfig())
 _g1401_arm = _g1401_unseedable.arm(NOW, _g1401_plant)
 R.check(
     "#1401: arming on a plant whose slab pair cannot be seeded is refused, "
@@ -55469,7 +55475,7 @@ R.check(
 # regression -- which is exactly the fit the #991 predicate exists to keep off
 # a slow-slab plant. Admitting the arm above makes that fallback REACHABLE, so
 # it must refuse BY NAME rather than hand the plant to the regression.
-_fb1329 = SystemIdentification(_SysIdModule.SysIdConfig(enabled=True))
+_fb1329 = SystemIdentification(_SysIdModule.SysIdConfig())
 assert _fb1329.arm(_C1329_NOW)  # ungated: the pair is set by hand below
 _fb1329_p = _p942("typical_slab")
 _fb1329._slab_pair = (
@@ -55550,7 +55556,7 @@ def _ridge_drive(params, sigma_c, seed, declare_plant=True, gap_tick=None):
     ua_true = params.heat_loss_coefficient * params.house_heat_loss_scale
     gains = float(params.internal_gains)
     sid = SystemIdentification(
-        _SysIdModule.SysIdConfig(enabled=True, min_days_between_runs=0.0)
+        _SysIdModule.SysIdConfig(min_days_between_runs=0.0)
     )
     assert sid.arm(_RIDGE_NOW, plant=params if declare_plant else None)
     outdoor = 0.0
@@ -55879,7 +55885,7 @@ def _r6_drift_drive(drift_c_per_h, seconds=30):
     ua_true = float(params.heat_loss_coefficient * params.house_heat_loss_scale)
     gains = float(params.internal_gains)
     sid = SystemIdentification(
-        _SysIdModule.SysIdConfig(enabled=True, min_days_between_runs=0.0)
+        _SysIdModule.SysIdConfig(min_days_between_runs=0.0)
     )
     assert sid.arm(_RIDGE_NOW, plant=params)
     outdoor = 2.0
@@ -56025,7 +56031,7 @@ def _drift_drive(seed, cadence_min=30, sigma_c=0.02, drift_c_per_h=0.0):
     rng = np.random.default_rng(seed)
     sid = SystemIdentification(
         _SysIdModule.SysIdConfig(
-            enabled=True, settle_hours=1.0, step_hours=2.0, relax_hours=2.0,
+            settle_hours=1.0, step_hours=2.0, relax_hours=2.0,
             max_excursion_c=0.8, gains_prior_kw=_DRIFT_G,
             thermal_mass_prior=_DRIFT_C,
         )
@@ -56202,7 +56208,6 @@ _t4_arm_on = _t4_coord(system_identification_enabled=False)
 # the fast slab, because this check pins the option re-read and the arm.
 _t4_arm_on._thermal_params.slab_heat_transfer *= 100.0
 _t4_count_refresh(_t4_arm_on)
-_t4_arm_on_built = _t4_arm_on._sysid.config.enabled
 with_config(_t4_arm_on, {"system_identification_enabled": True})
 _t4_arm_on.arm_system_identification()
 _t4_arm_off = _t4_coord(system_identification_enabled=True)
@@ -56211,17 +56216,10 @@ with_config(_t4_arm_off, {"system_identification_enabled": False})
 _t4_arm_off.arm_system_identification()
 R.check(
     "arming re-reads the option at call time, so an edit needs no reload",
-    _t4_arm_on_built is False
-    and _t4_arm_on._sysid.config.enabled is True
-    and _t4_arm_on._sysid.phase == "armed"
-    and _t4_arm_off._sysid.config.enabled is False
-    and _t4_arm_off._sysid.phase == "idle",
-    f"built {_t4_arm_on_built!r} then edited to True -> config "
-    f"{_t4_arm_on._sysid.config.enabled!r}, phase "
-    f"{_t4_arm_on._sysid.phase!r}; built True then edited to False -> config "
-    f"{_t4_arm_off._sysid.config.enabled!r}, phase "
-    f"{_t4_arm_off._sysid.phase!r} -- both directions, because the push is "
-    "invisible whenever the constructed value already agrees",
+    _t4_arm_on._sysid.phase == "armed" and _t4_arm_off._sysid.phase == "idle",
+    f"built False then edited to True -> phase {_t4_arm_on._sysid.phase!r}; built True then "
+    f"edited to False -> phase {_t4_arm_off._sysid.phase!r} -- both directions, because the "
+    "re-read is invisible whenever the constructed value already agrees",
 )
 # The arm is a synchronous decision since D10-s1-02, so the press, not the
 # arm, schedules the refresh that publishes it: armed or refused alike.
@@ -57390,7 +57388,6 @@ R.check(
     "integer-typed",
 )
 _t6_sysid_on = _t6_coord()
-_t6_sysid_on._sysid.config.enabled = True
 _t6_sysid_on._sysid.arm(datetime(2026, 2, 1, 12, 0, 0))
 R.check(
     "the system-identification property follows the experiment, not a copy",
@@ -61010,7 +61007,7 @@ _G8_SID_FLAT = np.full(24, 1.0)
 
 
 def _g8_sid_new(**cfg):
-    return _G8Sid(_G8SidCfg(enabled=True, **cfg))
+    return _G8Sid(_G8SidCfg(**cfg))
 
 
 def _g8_sid_step(sid, when, room=21.0, outdoor=0.0, **kw):
@@ -64763,26 +64760,32 @@ R.check(
 # the settle window: 5 K is taken and 3 K stays booked, as in "draw".
 _chg_esc = _chg_seq((50.0, 47.0, 47.0, 46.0, 47.0, 48.0, 48.0), heated_at=(2,))
 _chg_cap3 = _chg_seq((50.0, 50.0, 42.0, 45.0, 48.0, 51.0, 51.0))
+# R11-SEAM-learners (D2-s3-08, design section 3.1): a charge-open interval books
+# no draw. Cap3's 8 K fall opens on the charge's heated sample. So it books
+# nothing, and the rises find nothing to take.
 R.check(
     "a charge's take-back stops at the energy its charge folded and at the dip bound",
-    abs(_chg_esc[0] - _chg_reheat_ctl[0]) < 0.01 and abs(_chg_cap3[0] - _chg_draw[0]) < 0.01,
+    abs(_chg_esc[0] - _chg_reheat_ctl[0]) < 0.01 and _chg_cap3[0] == 0.0 and _chg_cap3[1] == 0,
     f"(open kWh, ...) a 1 K dip recovering 2 K after a draw {_chg_esc} vs no dip (control) "
     f"{_chg_reheat_ctl}; three 3 K rises after an 8 K fall {_chg_cap3} vs a 3 K draw {_chg_draw}",
 )
 
+# R11-SEAM-learners (D2-s3-08, design section 3.1): a fall over a charge-open
+# interval books nothing, a real draw in it included (the design's cost). A fall
+# after the charge-open intervals still books. So does every fall with no charge
+# on record (the controls).
 R.check(
     "a charge-start dip that recovers is learned as neither a draw nor usage, "
-    "and a draw that does not recover keeps what main booked",
+    "a fall over a charge-open interval books nothing, and the fall after it books",
     _chg_dip[0] < 0.05 and _chg_dip[1] == 0
     and _chg_edge[0] < 0.05 and _chg_edge[1] == 0
-    and _chg_draw[0] > 0.5 and _chg_draw[1] == 1
+    and 0.0 < _chg_draw[0] < _chg_space_draw[0] - 0.3 and _chg_draw[1] == 1
     and _chg_space[0] > 0.5 and _chg_space[1] == 2
-    and abs(_chg_draw[0] - _chg_space_draw[0]) < 0.05
-    and _chg_midnight[0] == 0.0 and 0.0 < _chg_midnight[2][0] < _chg_draw[0]
+    and _chg_space_draw[0] > 0.5
+    and _chg_midnight[0] == 0.0 and _chg_midnight[2] == [0.0]
     and _chg_reheat[0] > 0.5 and abs(_chg_reheat[0] - _chg_reheat_ctl[0]) < 0.05
-    and abs(_chg_cap[0] - _chg_draw[0]) < 0.05
-    and _chg_heated_rise[0] > _chg_draw[0] + 0.1
-    and _chg_partial[1] == 1 and 0.0 < _chg_partial[0] < _chg_draw[0]
+    and _chg_cap[0] == 0.0 and _chg_heated_rise[0] == 0.0
+    and _chg_partial[1] == 1 and 0.0 < _chg_partial[0] < _chg_space_draw[0]
     and abs(_chg_late[0] - _chg_draw[0]) < 0.05
     and _chg_partial[3] == [1, 0] and _chg_partial_sat[3] == [0, 1]
     and _chg_dip[4] and _chg_partial[4],
@@ -69947,7 +69950,6 @@ def _p5_night(how):
         # price never starts an experiment -- so hourly rows span it.
         c._prices = [{"total": 1.0, "starts_at": (_P5_T0 + timedelta(hours=h)).isoformat()}
                      for h in range(-12, 13)]
-        c._sysid.config.enabled = True
         c._sysid.config.min_days_between_runs = 0.0
         c._sysid.arm(_P5_T0, plant=c._thermal_params)
         prices = np.full(48, 1.0)
@@ -70404,7 +70406,12 @@ R.check(
 # with the experiment's freeze consult removed finds #1523's seam.
 # The consult is hold_reason's frozen argument (sysid.hold_reason, this PR's
 # move of the stand-down decision): the mutant passes None in its place.
-_P5_CONSULT = "self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)"
+# R11-SEAM-learners: the consult asks the space-heat kind with the cycle's evidence.
+_P5_CONSULT = (
+    "self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, "
+    "sample=learning_freeze.Sample.SPACE_HEAT,\n"
+    "                                  evidence=_space_evidence(self, self._commanded_split()))"
+)
 _p5_src_now = _p5_inspect.getsource(_p5_coord_mod)
 _p5_mut = _p5_ast.parse(_p5_src_now.replace(_P5_CONSULT, "None"))
 R.check(
@@ -73212,6 +73219,8 @@ def _z1524_learned(declared, free_kw, hours=range(24)):
         _thermal_params=declared, _internal_gains_profile=None,
         # #2223: the profile folds only behind an identified heat-loss level.
         _house_heat_loss_samples=400,
+        # D7-s2-01: the fold asks the freeze predicate; this house is occupied and clean.
+        _learning_frozen=lambda *keys, **ask: None,
     )
     cap = (declared.upper_floor_thermal_mass if declared.two_zone_enabled
            else declared.room_thermal_mass)
@@ -73283,7 +73292,7 @@ def _z1524_run(
     for _ in range(2400):
         st = plant.simulate_step(st, electrical_power=hold, outdoor_temp=0.0)
     sid = _SysIdModule.SystemIdentification(
-        _SysIdModule.SysIdConfig(enabled=True, min_days_between_runs=0.0)
+        _SysIdModule.SysIdConfig(min_days_between_runs=0.0)
     )
     sid.arm(_z1524_night, plant=_z1524_replace(
         declared, internal_gains_profile=_z1524_learned(
@@ -74318,7 +74327,7 @@ _r9p5_decl = _z1524_replace(
     internal_gains=0.3,
 )
 _r9p5_sid = _SysIdModule.SystemIdentification(_SysIdModule.SysIdConfig(
-    enabled=True, min_days_between_runs=0.0, gains_prior_kw=0.3,
+    min_days_between_runs=0.0, gains_prior_kw=0.3,
 ))
 _r9p5_priors = []
 for _r9p5_hours in ((23, 0, 1, 2, 3, 4), range(9, 18), None):
@@ -74387,7 +74396,7 @@ def _r9p5_derived_night(structure, era):
     model.params.two_zone_enabled = False
     ua = float(decl.heat_loss_coefficient * decl.house_heat_loss_scale)
     sid = _SysIdModule.SystemIdentification(_SysIdModule.SysIdConfig(
-        enabled=True, min_days_between_runs=0.0,
+        min_days_between_runs=0.0,
         gains_prior_kw=float(decl.internal_gains),
     ))
     if not sid.arm(_z1524_night, plant=decl):
@@ -74448,7 +74457,7 @@ R.check(
 # would stop the learners removing. The open-window CUSUM read the heat-loss
 # replay residual against zero, so a model bias tripped it and the freeze
 # self-latched. The barrier the round-10 P5 sweep proposed, as a census: every
-# CUSUM whose trip ``_learning_frozen`` reads is found in the source (the scan
+# CUSUM whose trip ``_learning_frozen`` reads (through ``_freeze_facts``) is found in the source (the scan
 # refuses if it finds none, or loses the open-window one), must measure from a
 # tracked level, and is driven -- on a live coordinator, its own construction
 # -- with a constant cold bias across the range the heat-loss learner folds (up
@@ -74465,7 +74474,9 @@ _r10p5_tree = _r10p5_ast.parse(_r10p5_inspect.getsource(_r10p5_cmod))
 _r10p5_gated = {
     a.value.attr
     for f in _r10p5_ast.walk(_r10p5_tree)
-    if isinstance(f, _r10p5_ast.FunctionDef) and f.name == "_learning_frozen"
+    # R11-SEAM-learners (ADR-008): ``_learning_frozen`` asks ``_freeze_facts``,
+    # the one reader of the coordinator's trips; both are scanned.
+    if isinstance(f, _r10p5_ast.FunctionDef) and f.name in ("_learning_frozen", "_freeze_facts")
     for a in _r10p5_ast.walk(f)
     if isinstance(a, _r10p5_ast.Attribute) and a.attr == "tripped"
     and isinstance(a.value, _r10p5_ast.Attribute)
@@ -75721,12 +75732,14 @@ def _r9egb1_h2(**arm):
 
 _r9egb1_h2_e = _r9egb1_h2(economy=True)
 _r9egb1_h2_a = _r9egb1_h2(away=True)
+# R11-SEAM-learners (D7-s2-01): an away solve records no quiet period at all,
+# since away refuses the occupancy kind, so only the economy solve hands a band.
 R.check(
-    "#1736 H2: economy and away solves hand the quiet-period learner the "
-    "configured comfort band",
+    "#1736 H2: an economy solve hands the quiet-period learner the configured "
+    "comfort band, and an away solve hands it none (an empty house complains about nothing)",
     _r9egb1_h2_e[0] is None and _r9egb1_h2_a[0] is None
-    and len(_r9egb1_bands) == 2
-    and [b for _, b in _r9egb1_bands] == [_r9egb1_h2_e[1], _r9egb1_h2_a[1]],
+    and [b for _, b in _r9egb1_bands] == [_r9egb1_h2_e[1]]
+    and [arm for arm, _ in _r9egb1_bands] == [(("economy", True),)],
     f"bands {_r9egb1_bands}; configured {_r9egb1_h2_e[1]}, {_r9egb1_h2_a[1]}",
 )
 
@@ -81891,7 +81904,7 @@ def _wrr_folded(command, experiment_s=None):
     """A fresh store after one running 3.0 kW space interval held at ``command``."""
     d = _dr.DrawRange()
     _dr.fold(d, 3.0, (5.0, 0.0), _dr_params(1.5, 5.5), frozen=False, distorted=False,
-             defrost=False, command=command, experiment_s=experiment_s)
+             defrost=False, command=command, span=None if experiment_s is None else _dr.Span(experiment_s, experiment_s, experiment=True))
     return d
 
 
@@ -86327,7 +86340,7 @@ R.check(
 
 
 # --- R10-COP-GATE item E: the open-window latch freezes only room-air learners --
-# ``_learning_frozen(room_air=False)`` skips the ventilation reason alone. The
+# ``_learning_frozen(sample=Sample.PLANT)`` skips the ventilation reason alone. The
 # measured-heat COP paths (a counter span, a measured flow heat) and hot water
 # lift; the inferred COP, the flow-curve bias and every room-air learner keep
 # the freeze (dev/audit/harnesses/r10_cop_gate_vent.py measures each arm).
@@ -87917,20 +87930,24 @@ R.check(
     f"{_bt_tails}",
 )
 
-# Null control: the order of the freeze reasons in ``_learning_frozen`` is main's.
+# Null control: the order of the shared freeze reasons is main's. They live in
+# ``learning_freeze._shared`` since R11-SEAM-learners (ADR-008); the coordinator
+# supplies each as a fact (``_freeze_facts``: the boost from boost.FREEZE_REASON,
+# the tail from _tail_freeze).
 import ast as _bt_ast  # noqa: E402
 import inspect as _bt_inspect  # noqa: E402
 import textwrap as _bt_tw  # noqa: E402
+from heatpump_optimizer import learning_freeze as _bt_lf  # noqa: E402
 _bt_returns = [
     _bt_ast.unparse(n.value) for n in sorted(_bt_ast.walk(_bt_ast.parse(_bt_tw.dedent(_bt_inspect.getsource(
-        _he_cm.HeatPumpOptimizerCoordinator._learning_frozen)))), key=lambda n: getattr(n, "lineno", 0))
+        _bt_lf._shared)))), key=lambda n: getattr(n, "lineno", 0))
     if isinstance(n, _bt_ast.Return)
 ]
 R.check(
     "the freeze reasons keep main's order, the boost's after ventilation and before the tail freeze",
-    _bt_returns == ["'external_heat_source'", "signals.freeze_reason", "'defrosting'",
-                    "f'{reading.problem}:{key}'", "'ventilation'", "boost.FREEZE_REASON",
-                    "_tail_freeze(self)"],
+    _bt_returns == ["REASON_EXTERNAL_HEAT", "facts.signals", "REASON_DEFROSTING",
+                    "f'{problem}:{key}'", "REASON_VENTILATION", "facts.boost",
+                    "facts.tail"],
     f"{_bt_returns}",
 )
 
@@ -91886,7 +91903,7 @@ def _cp_params(lo=1.0, hi=5.0):
 
 def _cp_fold(d, drawn, command, experiment_s, split=(5.0, 0.0), hi=5.0):
     _cp_dr.fold(d, drawn, split, _cp_params(hi=hi), frozen=False, distorted=False,
-                defrost=False, command=command, experiment_s=experiment_s)
+                defrost=False, command=command, span=None if experiment_s is None else _cp_dr.Span(experiment_s, experiment_s, experiment=True))
 
 
 def _cp_store(values, newest_s=_CP_NOW):
@@ -92047,7 +92064,7 @@ _CP_WEE = _cp_sid.HousePlant(ua=0.05, capacity=1.2, gains=0.3)
 
 
 def _cp_cfg(**kw):
-    return _cp_sid.SysIdConfig(enabled=True, **kw)
+    return _cp_sid.SysIdConfig(**kw)
 
 
 R.check(
@@ -92269,7 +92286,7 @@ def _cp_sysid_cycle(host):
 
 
 _cp_frz = _cp_coord(**_CP_PROBE_CFG)
-_cp_frz._learning_frozen = lambda *keys: "an open window"
+_cp_frz._learning_frozen = lambda *keys, **_kw: "an open window"
 _cp_sysid_cycle(_cp_frz)
 _cp_frz_armed = (_cp_frz._sysid.phase, _cp_frz._sysid.held)
 _cp_frz._sysid.phase = _cp_sid.PHASE_STEP
@@ -92337,7 +92354,7 @@ def _cp_pump(house, nights, late=False, noise=0.02, seed=3):
                 drawn = (3.0 if pending["command"] is _CP_CEIL else 1.5) * (1.0 + noise * rng.standard_normal())
                 _cp_dr.fold(store, drawn, (pending["power"], 0.0), _cp_params(), frozen=False,
                             distorted=False, defrost=False, command=pending["command"],
-                            experiment_s=pending["when"] if key == "system_identification" else None)
+                            span=_cp_dr.Span(pending["when"], pending["when"], experiment=True) if key == "system_identification" else None)
             pending = {"mode": mode, "power": power, "when": now.timestamp(),
                        "command": _CP_CEIL if power >= 5.0 else _CP_MID}
             prev_mode = mode
@@ -92846,7 +92863,7 @@ try:
     _cp_quiet = _cp_coord(**_CP_PROBE_CFG, **_CP_ROOM, quiet_off_windows="22:00-23:30")
     _cp_loud = _cp_coord(**_CP_PROBE_CFG, **_CP_ROOM, quiet_off_windows="09:00-09:30")
     for _cp_c in (_cp_quiet, _cp_loud):
-        _cp_c._learning_frozen = lambda *keys: None  # the freeze is the check above's
+        _cp_c._learning_frozen = lambda *keys, **_kw: None  # the freeze is the check above's
     _cp_sysid_cycle(_cp_quiet)
     _cp_quiet_armed = (_cp_quiet._sysid.phase, _cp_quiet._sysid.held)
     _cp_quiet._sysid.phase = _cp_sid.PHASE_STEP
@@ -92882,17 +92899,20 @@ R.check(
     and _cp_hold(False, None, None) is None,
 )
 _cp_armed = _cp_sid.SystemIdentification(_cp_cfg())
-_cp_armed.config.enabled = False
+_cp_armed_before = dataclasses.asdict(_cp_armed.config)
+
+
 class _CpOffCfg(dict):
     system_identification_enabled = False
 
 
 _cp_off_cfg = _CpOffCfg()
 R.check(
-    "arm_from_config takes the switch from the entry's configuration: off arms nothing, whatever the sysid "
-    "config held before",
+    "arm_from_config hands the entry's switch to arm as its argument (ADR-003): off arms nothing and "
+    "writes nothing onto the collaborator's config",
     _cp_sid.arm_from_config(_cp_armed, _CP_T0, _cp_off_cfg, None, 0, None) is False
-    and _cp_armed.config.enabled is False and _cp_armed.phase == _cp_sid.PHASE_IDLE,
+    and _cp_armed.phase == _cp_sid.PHASE_IDLE and not hasattr(_cp_armed.config, "enabled")
+    and dataclasses.asdict(_cp_armed.config) == _cp_armed_before,
 )
 
 
@@ -95869,6 +95889,7 @@ R.check(
     "a plausible target raised a notice",
 )
 
+# --- R10-DUTY-SWITCH-PLANNER-PRICE block start
 R.section(
     "R10-DUTY-SWITCH-PLANNER-PRICE: the planner prices a duty switch that stops "
     "the compressor (pull request 3420, Bankaifan)"
@@ -96456,10 +96477,12 @@ def _dsp_same_plan(a, b):
 # with a start priced as a start that install plans runs, and on the 2 degC day
 # the plan it ships makes no priced switch at all (the mild day of the two
 # descents below), so the checks of a charged step and of the banned candidate
-# had nothing to read there.
+# had nothing to read there. 2 K colder again since R11-OUTSIDE-HONEST-DHW-RUNS:
+# with its hot water committed as runs the 0 degC plan makes no priced switch
+# either (dev/audit/harnesses/r11_honest_dhw_runs.py, switches).
 _DSP_INSTALLS = {
-    "duty-cycle": dict(clamp=False, out_mean=0.0),
-    "modulating clamped": dict(clamp=True),
+    "duty-cycle": dict(clamp=False, out_mean=-2.0),
+    "modulating clamped": dict(clamp=True, out_mean=0.0),
     "fixed-speed": dict(clamp=True, p_min=5.5),
 }
 _dsp_base = {name: _dsp_solve(None, **kw) for name, kw in _DSP_INSTALLS.items()}
@@ -97672,12 +97695,16 @@ R.check(
 # plan the true objective scores above the one that kept it. Such a solve
 # therefore descends twice, with the switch operand and as a solve that
 # prices no stop would, and the true objective judges the candidates of both.
-# Two duty-cycle days, one where each descent supplies the plan that ships:
-# the cells "duty-cycle price phase 30 outdoor 2.0" (mild) and "... outdoor
-# -4.0" (cold) that dev/audit/harnesses/r11_honest_starts_runs.py's
-# descents mode prints, both and each descent alone (design verdict r2).
-# The scores are of one non-convex solve per arm (``fixer.md`` step 15): the
-# margins measured on x86_64 are 0.07 and 0.39, the checks ask for 0.01.
+# Two duty-cycle days, one where each descent supplies the plan that ships.
+# Each is the duty-cycle solve at price phase 30 that
+# dev/audit/harnesses/r11_honest_starts_runs.py's descents mode runs, at an
+# outdoor mean of 1.0 (mild) and -1.0 (cold), both and each descent alone
+# (design verdict r2). The scores are of one
+# non-convex solve per arm (``fixer.md`` step 15). So each day is one whose
+# shipping arm stands apart, by the 0.01 the checks ask for, in each of four
+# kernel classes measured. They are OPENBLAS_CORETYPE unset with numpy's own
+# dispatch, Haswell without AVX-512, and Sandybridge and Nehalem without AVX,
+# numpy narrowed to match by NPY_DISABLE_CPU_FEATURES.
 _dsp_real_plans, _dsp_real_term = _dsp_om._relaxed_plans, _dsp_om._switch_cost_fn
 _dsp_descents = []
 
@@ -97705,18 +97732,68 @@ def _dsp_arm(arm, **kw):
 
 _dsp_days = {
     day: {arm: _dsp_arm(arm, **kw) for arm in ("both", "operand", "unpriced", "no operand")}
-    for day, kw in (("mild", {}), ("cold", {"out_mean": -4.0}))
+    # Both days moved with R11-OUTSIDE-HONEST-DHW-RUNS. With the hot water
+    # committed as runs both descents ship one plan at -4 degC. At 2 degC
+    # the operand's descent alone comes within 0.01 of the shipped plan once
+    # numpy's dispatch has no AVX.
+    for day, kw in (("mild", {"out_mean": 1.0}), ("cold", {"out_mean": -1.0}))
 }
+# What the commit stage guarantees is read where it decides: each commit call
+# scores the committed form of every relaxed plan (one per descent) on the
+# true objective, start term included, and ships the lowest. The solve's final
+# objective is not that score: stages after the commit move it. So which arm
+# alone ships the lower final objective is a property of one non-convex solve
+# per arm, and it moved with the CPU class (``fixer.md`` step 15). With hot
+# water committed as runs, the 2 degC day's operand arm alone scored under both
+# descents on one CI runner class and on arm64, and above them on another.
+# The 1 degC day chosen over four x86 kernel classes failed on arm64.
+_dsp_real_best, _dsp_real_commit = _dsp_om._best_runs, _dsp_om._commit_runs
+
+
+def _dsp_commit_calls(**kw):
+    """Per commit call of one priced duty-cycle solve with both descents:
+    each descent's committed (score, plan) and the plan that shipped."""
+    calls = []
+
+    def best(*args):
+        out = _dsp_real_best(*args)
+        calls[-1][0].append((float(out[0]), np.array(out[1], float)))
+        return out
+
+    def commit(*args, **kwargs):
+        calls.append(([], None))
+        out = _dsp_real_commit(*args, **kwargs)
+        calls[-1] = (calls[-1][0], np.array(out[0], float))
+        return out
+
+    _dsp_om._best_runs, _dsp_om._commit_runs = best, commit
+    try:
+        _dsp_solve(_DSP_PAIR, _DSP_OFF, **kw)
+    finally:
+        _dsp_om._best_runs, _dsp_om._commit_runs = _dsp_real_best, _dsp_real_commit
+    return calls
+
+
+_dsp_stage = {day: _dsp_commit_calls(**kw) for day, kw in (("mild", {}), ("cold", {"out_mean": -1.0}))}
+_dsp_stage_calls = [c for calls in _dsp_stage.values() for c in calls]
+_dsp_stage_scores = [[round(c[0], 6) for c in cands] for cands, _ in _dsp_stage_calls]
 R.check(
-    "a solve that prices a stop commits both descents and ships the lower: on "
-    "the mild day (duty-cycle, price phase 30, 2 degC) the unpriced descent's "
-    "plan, which the operand's descent alone scores above; on the cold day "
-    "(the same at -4 degC) the operand's, which the unpriced descent alone scores above",
-    _dsp_days["mild"]["both"] <= _dsp_days["mild"]["unpriced"] + 1e-9
-    and _dsp_days["mild"]["both"] < _dsp_days["mild"]["operand"] - 0.01
-    and _dsp_days["cold"]["both"] <= _dsp_days["cold"]["operand"] + 1e-9
-    and _dsp_days["cold"]["both"] < _dsp_days["cold"]["unpriced"] - 0.01,
-    f"{_dsp_days}",
+    "a solve that prices a stop commits both descents and ships the lower: on the "
+    "duty-cycle days at 2 and -1 degC every commit call scores one committed plan per "
+    "descent and ships the one that scores lowest",
+    bool(_dsp_stage_calls)
+    and all(
+        len(cands) == 2 and shipped is not None
+        and np.array_equal(shipped, min(cands, key=lambda c: c[0])[1])
+        for cands, shipped in _dsp_stage_calls
+    ),
+    f"{_dsp_stage_scores}",
+)
+R.check(
+    "and the choice is live: on some commit call the unpriced descent's committed plan "
+    "scores below the operand's, so shipping the first descent's plan would ship the higher",
+    any(len(cands) == 2 and cands[1][0] < cands[0][0] - 1e-9 for cands, _ in _dsp_stage_calls),
+    f"{_dsp_stage_scores}",
 )
 R.check(
     "the relaxed descent still leaves a priced switch: with the switch operand "
@@ -99733,6 +99810,736 @@ R.check(
 _sce_dt.freeze(None)
 
 
+
+# ---------------------------------------------------------------------------
+# R11-OUTSIDE-HONEST-DHW-RUNS (pull request 3529, Bankaifan): hot-water
+# charges ship as runs. On a solve that plans runs the planner commits its
+# plan (dhw_charges.commit_charges): the store program's plan or the lifted
+# plan, each only if charge_refusal passes it on the planner's own walk; the
+# uncommitted plan is the one unconditional fallback. The finding, the store
+# program and the tail are the contributor's.
+# ---------------------------------------------------------------------------
+R.section("R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed on the planner's own store")
+import golden as _hdr_golden  # noqa: E402
+import heatpump_optimizer.dhw_planner as _hdr_dp  # noqa: E402
+import heatpump_optimizer.dhw_charges as _hdr_dc  # noqa: E402
+import heatpump_optimizer.optimizer as _hdr_om  # noqa: E402
+from heatpump_optimizer import runs as _hdr_runs  # noqa: E402
+from heatpump_optimizer.thermal_model import MIN_RUNNING_DRAW_KW as _HDR_RUNS_AT  # noqa: E402
+
+_HDR_N = 32
+
+
+def _hdr_rig(*, start=0.5, clamped=False, running=False, prices=None, draws=None, t0=50.0, p_min=1.0, n=_HDR_N, dt=0.25,
+             p_run=4.8):
+    """A planner that plans runs, on the default 200 l tank, and its context."""
+    params = ThermalParameters(min_electrical_power=p_min, max_electrical_power=6.0)
+    planner = DhwPlanner(
+        ThermalModel(params), SimpleNamespace(pv_export_price=0.0),
+        charge_runs=_hdr_dc.ChargeRuns(start, running, clamped))
+    prices = np.full(n, 1.0) if prices is None else np.asarray(prices, dtype=float)
+    ctx = _dhw_ctx(prices=prices, outdoor=np.full(n, 5.0), n=n, dt=dt, c_dhw=params.dhw_store.capacity_kwh_per_c,
+                   p_dhw_max=p_run, params=params, min_run_power=0.6, max_lead_steps=n)
+    draws = np.zeros(n) if draws is None else np.asarray(draws, dtype=float)
+    return SimpleNamespace(
+        planner=planner, ctx=ctx, tank=(t0, draws), floor=_hdr_runs.floor_kw(p_min),
+        temps=lambda plan: planner._ctx_temps(ctx, t0, draws, np.asarray(plan, dtype=float)))
+
+
+def _hdr_commit(rig, plan, requirement, *, ceiling=55.0, start_below=None, space=None, forced_off=None):
+    n = rig.ctx.n_steps
+    return _hdr_dc.commit_charges(
+        rig.planner, np.asarray(plan, dtype=float), (rig.ctx, *rig.tank),
+        (np.broadcast_to(np.asarray(requirement, dtype=float), (n,)), np.full(n, ceiling)),
+        forced_off, start_below, space)
+
+
+def _hdr_under(plan, floor):
+    """Charging steps under the floor that are not a charge's last step."""
+    plan = np.asarray(plan, dtype=float)
+    low = (plan > _HDR_RUNS_AT) & (plan < floor - 1e-9)
+    last = np.r_[plan[1:] <= 0.0, True] & np.r_[False, plan[:-1] >= floor - 1e-9]
+    return int(np.sum(low & ~last))
+
+
+def _hdr_programs(fn, replace=None):
+    """``fn()`` with the store program's plans recorded, or replaced."""
+    seen, real = [], _hdr_dc._StoreProgram.plan
+
+    def plan(self, may_start):
+        out = real(self, may_start) if replace is None else replace(self, may_start)
+        seen.append(None if out is None else np.array(out))
+        return out
+
+    _hdr_dc._StoreProgram.plan = plan
+    try:
+        return fn(), seen
+    finally:
+        _hdr_dc._StoreProgram.plan = real
+
+
+# 1. The failing case, on the two goldens that price a start on an install
+# that can duty-cycle. Each is solved as the tree solves it and with the
+# planner handed no ChargeRuns (the uncommitted plan, what shipped before).
+def _hdr_capture(name, committed):
+    real, solve, seen = _hdr_om._charge_runs, _hdr_om.HeatPumpOptimizer.optimize, []
+    if not committed:
+        _hdr_om._charge_runs = lambda _opt, _running: None
+    _hdr_om.HeatPumpOptimizer.optimize = lambda self, **kw: (seen.append(self), solve(self, **kw))[1]
+    try:
+        got = _hdr_golden.capture(name, _hdr_golden.SCENARIOS[name])
+    finally:
+        _hdr_om._charge_runs, _hdr_om.HeatPumpOptimizer.optimize = real, solve
+    space, dhw = (np.asarray(got[k], dtype=float) for k in ("power_schedule", "dhw_power_schedule"))
+    short = np.asarray(seen[-1]._dhw_requirement) - np.asarray(got["dhw_temp_trajectory"], dtype=float)[1:]
+    return SimpleNamespace(
+        dhw=dhw, low=_hdr_under(dhw, 1.0), short=float(np.max(short)),
+        starts=_hdr_runs.start_count(space + dhw, 1.0), got=got)
+
+
+_hdr_fix = {name: (_hdr_capture(name, True), _hdr_capture(name, False)) for name in ("cycling_cost", "everything_on")}
+R.check(
+    "acceptance: on an install that can duty-cycle, with a start priced, no shipped hot-water step lies "
+    "between the running rule and the floor but a charge's last; the same solves with the planner handed "
+    "no ChargeRuns ship such steps (the plan before this group, the control)",
+    all(new.low == 0 and old.low > 0 for new, old in _hdr_fix.values()),
+    f"{ {k: (new.low, old.low) for k, (new, old) in _hdr_fix.items()} }",
+)
+R.check(
+    "the committed plans hold the tank no further under its floor than the uncommitted ones (0.05 K, the "
+    "planners' tolerance), and the combined draw starts no more often",
+    all(new.short <= max(old.short, 0.0) + 0.05 and new.starts <= old.starts + 1e-9 for new, old in _hdr_fix.values()),
+    f"{ {k: (round(new.short, 3), round(old.short, 3), new.starts, old.starts) for k, (new, old) in _hdr_fix.items()} }",
+)
+
+# Null control: a solve that plans no runs hands the planner nothing, and a
+# planner handed nothing returns its plan object untouched.
+_hdr_free_opt = _hsr_opt(0.0, False, 1.1)
+_hdr_none = _hdr_rig()
+_hdr_none.planner.charge_runs = None
+_hdr_trickle = np.zeros(_HDR_N)
+_hdr_trickle[[6, 14, 22, 29]] = 0.6
+R.check(
+    "unengaged (no start priced, an install that can duty-cycle) the optimizer hands the planner no "
+    "ChargeRuns, engaged it hands the start price the solve plans with (a clamped install configured "
+    "at zero: the clamped default, never the raw configured zero), the running reading and the clamp; a "
+    "planner handed none returns the plan it was given, the same object",
+    _hdr_om._charge_runs(_hdr_free_opt, True) is None
+    and _hdr_om._charge_runs(_hsr_opt(0.25, False, 1.1), True) == (0.25, True, False)
+    and _hdr_om._charge_runs(_hsr_opt(0.0, True, 1.1), False)
+    == (_hdr_om.CLAMPED_DEFAULT_START_PRICE, False, True)
+    and _hdr_commit(_hdr_none, _hdr_trickle, 50.0) is _hdr_trickle,
+    f"{_hdr_om._charge_runs(_hsr_opt(0.25, False, 1.1), True)}",
+)
+
+# 2a. Ruling b, the boolean. The tank sags under a 51 degC start temperature
+# before each of the plan's four trickles. The program's first plan charges
+# longer early, so the charge it opens later begins on a tank the pump would
+# not start; that step is cleared and the program runs again.
+_hdr_a = _hdr_rig(t0=51.2, draws=np.r_[np.zeros(8), np.full(24, 0.25)])
+_hdr_a_below = np.full(_HDR_N, 51.0)
+_hdr_a_out, _hdr_a_seen = _hdr_programs(lambda: _hdr_commit(_hdr_a, _hdr_trickle, 50.0, start_below=_hdr_a_below))
+R.check(
+    "ruling b: the store program is handed where the pump would start; a charge its own walk refuses "
+    "clears that step and the program runs again, and what ships is the program's last plan, committed, "
+    "in more than one round and fewer than STARTABLE_ROUNDS",
+    1 < len(_hdr_a_seen) < _hdr_dc.STARTABLE_ROUNDS
+    and np.array_equal(_hdr_a_out, _hdr_a_seen[-1])
+    and not np.array_equal(_hdr_a_seen[0], _hdr_a_seen[-1])
+    and _hdr_under(_hdr_a_out, 1.0) == 0 and bool(np.any(_hdr_a_out > 0.0))
+    and _hdr_dc.charge_refusal(_hdr_a_out, _hdr_a_below, _hdr_a.temps, np.full(_HDR_N, -np.inf)) is None
+    and _hdr_dc.charge_refusal(_hdr_a_seen[0], _hdr_a_below, _hdr_a.temps, np.full(_HDR_N, -np.inf))[0] == "start",
+    f"rounds {len(_hdr_a_seen)}, shipped on {np.flatnonzero(_hdr_a_out > 0).tolist()}",
+)
+# With no start condition known every charge is taken to start (verdict
+# item r7): the first plan ships, and drop_unstartable is never asked.
+_hdr_a_free, _hdr_a_free_seen = _hdr_programs(lambda: _hdr_commit(_hdr_a, _hdr_trickle, 50.0))
+R.check(
+    "with no start condition known the program runs once and its plan ships (null of the rounds above)",
+    len(_hdr_a_free_seen) == 1 and np.array_equal(_hdr_a_free, _hdr_a_free_seen[0])
+    and _hdr_dc.charge_refusal(_hdr_a_seen[0], None, _hdr_a.temps, np.full(_HDR_N, -np.inf)) is None,
+    f"{len(_hdr_a_free_seen)}",
+)
+
+# 2b. The start clause, called directly: a plan whose second charge opens on
+# a tank at its start temperature.
+_hdr_b_plan = np.zeros(8)
+_hdr_b_plan[[1, 5]] = 2.0
+_hdr_b_walk = np.array([49.0, 49.0, 52.0, 51.5, 51.2, 51.0, 54.0, 53.5, 53.0])
+R.check(
+    "the acceptance refuses a plan whose second charge opens at its start temperature on the supplied "
+    "walk, at that step; one degree lower it passes",
+    _hdr_dc.charge_refusal(_hdr_b_plan, np.full(8, 51.0), lambda _p: _hdr_b_walk, np.full(8, -np.inf)) == ("start", 5)
+    and _hdr_dc.charge_refusal(_hdr_b_plan, np.full(8, 52.0), lambda _p: _hdr_b_walk, np.full(8, -np.inf)) is None,
+    f"{_hdr_dc.charge_refusal(_hdr_b_plan, np.full(8, 51.0), lambda _p: _hdr_b_walk, np.full(8, -np.inf))}",
+)
+
+# 2c. The lifted plan passes through the acceptance too (design verdict
+# point 1). The program is handed no feasible plan; raising the first
+# trickle to the floor warms the second's opening step past its start
+# temperature, so the uncommitted plan ships. Null: with the floor at 0.7 kW
+# the lift is a quarter of that and the lifted plan ships.
+_hdr_c_plan = np.zeros(_HDR_N)
+_hdr_c_plan[[4, 16]] = 0.6
+
+
+def _hdr_lifted(p_min, plan=_hdr_c_plan, requirement=45.0, t0=50.0, start_below=None):
+    rig = _hdr_rig(t0=t0, p_min=p_min)
+    walk = rig.temps(plan)
+    below = np.full(_HDR_N, float(walk[16]) + 0.5) if start_below is None else start_below
+    out = _hdr_programs(lambda: _hdr_commit(rig, plan, requirement, start_below=below), lambda *_a: None)[0]
+    return out, rig, below
+
+
+_hdr_c_out, _hdr_c_rig, _hdr_c_below = _hdr_lifted(1.0)
+_hdr_c_null = _hdr_lifted(0.7)[0]
+_hdr_c_lift = np.where(_hdr_c_plan > 0.0, 1.0, 0.0)
+R.check(
+    "the lifted plan ships only through the acceptance: where raising a charge to the floor leaves a "
+    "later one unstartable the uncommitted plan ships, the same object; with a floor the lift does not "
+    "carry that far the lifted plan ships",
+    _hdr_c_out is _hdr_c_plan
+    and _hdr_dc.charge_refusal(_hdr_c_lift, _hdr_c_below, _hdr_c_rig.temps, np.full(_HDR_N, -np.inf)) == ("start", 16)
+    and np.array_equal(_hdr_c_null, np.where(_hdr_c_plan > 0.0, 0.7, 0.0)),
+    f"{np.round(_hdr_c_null[_hdr_c_null > 0], 2)}",
+)
+
+# 2d. The shortfall clause, cycling_cost's shape: two trickles fill the tank
+# to its ceiling. Lifted, the first leaves the second no room, the rating
+# clamp cuts it under a runnable block and zeroes it, and the tank ends
+# under the floor the uncommitted plan held.
+_hdr_d_plan = np.zeros(_HDR_N)
+_hdr_d_plan[[4, 5]] = 0.6
+_hdr_d_rig = _hdr_rig(t0=52.6)
+_hdr_d_req = np.where(np.arange(_HDR_N) >= 5, 54.5, 45.0)
+_hdr_d_out = _hdr_programs(lambda: _hdr_commit(_hdr_d_rig, _hdr_d_plan, _hdr_d_req), lambda *_a: None)[0]
+_hdr_d_lift = _hdr_d_rig.planner._ctx_clamp(
+    _hdr_d_rig.ctx, 52.6, _hdr_d_rig.tank[1], np.full(_HDR_N, 55.0), np.where(_hdr_d_plan > 0.0, 1.0, 0.0))
+_hdr_d_held = np.minimum(_hdr_d_req, _hdr_d_rig.temps(_hdr_d_plan)[1:])
+R.check(
+    "the acceptance refuses a lifted plan whose clamped tail leaves the tank under a floor the "
+    "uncommitted plan held, and the uncommitted plan ships; against no floor the same plan passes",
+    _hdr_d_out is _hdr_d_plan
+    and _hdr_d_lift[5] == 0.0 and _hdr_d_lift[4] == 1.0
+    and _hdr_dc.charge_refusal(_hdr_d_lift, None, _hdr_d_rig.temps, _hdr_d_held) == ("floor", 5)
+    and _hdr_dc.charge_refusal(_hdr_d_lift, None, _hdr_d_rig.temps, np.full(_HDR_N, -np.inf)) is None,
+    f"{_hdr_dc.charge_refusal(_hdr_d_lift, None, _hdr_d_rig.temps, _hdr_d_held)}, "
+    f"worst gap {float(np.max(_hdr_d_held - _hdr_d_rig.temps(_hdr_d_lift)[1:])):.3f} K",
+)
+
+# 3. The kernel both programs call (runs.advance, runs.read_back), driven
+# here on an affine store with hard bounds and two charging levels, against
+# an exhaustive search over every on/off/level sequence of nine steps. The
+# kernel's cost is read off its own read-back, so the action index is
+# pinned with it. Null: the search with the bounds ignored.
+def _hdr_small(seed, cells=800, bounds=True):
+    rng = np.random.default_rng(seed)
+    n, heats, decay, top = 9, (1.0, 2.5), 0.97, 20.0
+    price, drift = rng.uniform(0.5, 2.0, n), rng.uniform(-1.5, -0.2, n)
+    floors, ceiling = rng.uniform(2.0, 6.0, n), float(rng.uniform(9.0, 13.0))
+    start, first = float(rng.choice([0.0, 0.7])), float(rng.uniform(6.0, 9.0))
+    width = top / cells
+
+    def place(k):
+        def rule(v, _charged):
+            j = np.rint(v / width).astype(np.int64)
+            inside = (v >= floors[k]) & (v <= ceiling) & (j >= 0) & (j <= cells)
+            return np.clip(j, 0, cells), np.where(inside, 0.0, np.inf)
+        return rule
+
+    def actions(k):
+        return ([lambda v, _r, h=h: (decay * v + drift[k] + h, price[k] * h) for h in heats],
+                [lambda v, _r: (decay * v + drift[k], 0.0)])
+
+    cost = np.full((2, cells + 1), np.inf)
+    val = np.zeros_like(cost)
+    cost[1, int(round(first / width))], val[1, int(round(first / width))] = 0.0, first
+    trail = []
+    for k in range(n):
+        cost, val, back = _hdr_runs.advance(cost, val, _hdr_runs.state_moves(1, 1, np.nan), actions(k), start, place(k), 1)
+        trail.append(back)
+    grid = np.indices((3,) * n).reshape(n, -1).T  # 0 off, 1 and 2 the levels
+    v, paid, ok, was = np.full(len(grid), first), np.zeros(len(grid)), np.ones(len(grid), dtype=bool), np.zeros(len(grid), dtype=bool)
+    for k in range(n):
+        on = grid[:, k] > 0
+        heat = np.where(on, np.take(heats, np.maximum(grid[:, k] - 1, 0)), 0.0)
+        v = decay * v + drift[k] + heat
+        paid += price[k] * heat + start * (on & ~was)
+        ok &= (v >= floors[k]) & (v <= ceiling) if bounds else True
+        was = on
+    best = float(np.min(np.where(ok, paid, np.inf)))
+    if not np.isfinite(cost).any():
+        return best, np.inf, np.inf
+    mask, action = _hdr_runs.read_back(trail, cost, 1)
+    replay = sum(price[k] * heats[action[k]] for k in range(n) if mask[k]) + start * int(np.sum(mask & ~np.r_[False, mask[:-1]]))
+    return best, float(np.min(cost)), float(replay)
+
+
+_hdr_k = [_hdr_small(s) for s in range(60)]
+_hdr_k_null = [_hdr_small(s, bounds=False) for s in range(60)]
+_hdr_k_same = sum(abs(b - c) <= 1e-9 and abs(c - r) <= 1e-9 for b, c, r in _hdr_k if np.isfinite(b))
+_hdr_k_live = sum(bool(np.isfinite(b)) for b, _c, _r in _hdr_k)
+R.check(
+    "the generalised kernel's cost equals an exhaustive search's on every feasible nine-step case with "
+    "two levels and hard bounds at 800 cells, and the cost of the path its read-back returns (mask and "
+    "action index) is that cost; the kernel never beats the search, and declares no plan only where the "
+    "search finds none",
+    _hdr_k_live >= 30 and _hdr_k_same == _hdr_k_live
+    and all(c >= b - 1e-9 for b, c, _r in _hdr_k)
+    and all(np.isfinite(c) == np.isfinite(b) for b, c, _r in _hdr_k),
+    f"{_hdr_k_same} of {_hdr_k_live} feasible, of 60",
+)
+R.check(
+    "null control: a search that ignores the bounds finds a cheaper plan than the kernel in most cases, "
+    "so the agreement above is the bounds' and not the search's",
+    sum(b < c - 1e-9 for b, c, _r in _hdr_k_null) >= 40,
+    f"{sum(b < c - 1e-9 for b, c, _r in _hdr_k_null)} of 60",
+)
+R.check(
+    "the move rule begins no run on a free step it is told the pump would not start, and still does on "
+    "a forced-on step; told nothing it is the rule commit always had",
+    not any(s for _a, _b, s in _hdr_runs.state_moves(2, 2, np.nan, False))
+    and any(s for _a, _b, s in _hdr_runs.state_moves(2, 2, 1.0, False))
+    and _hdr_runs.state_moves(2, 2, np.nan) == _hdr_runs.state_moves(2, 2, np.nan, True)
+    and sum(s for _a, _b, s in _hdr_runs.state_moves(2, 2, np.nan)) == 1,
+    f"{_hdr_runs.state_moves(2, 2, np.nan, False)}",
+)
+
+# 4. Two levels (the contributor's forward-carry). Three trickles hold a
+# 51.5 degC floor late in the horizon, the steps before them dear. Two
+# steps at the floor hold it for less than a fill to the ceiling does, and
+# a whole step at the run power would pass the ceiling. Without the floor level the fill ships, dearer.
+_hdr_l_plan = np.zeros(_HDR_N)
+_hdr_l_plan[[17, 18, 19]] = 0.6
+_hdr_l_req = np.where(np.arange(_HDR_N) >= 19, 51.5, 45.0)
+_hdr_l_prices = np.where(np.arange(_HDR_N) < 16, 3.0, 1.0)  # dear early: no fill while the tank is warm
+
+
+def _hdr_levels(floor_level):
+    real = _hdr_dc._StoreProgram.__init__
+
+    def init(self, *a, **k):
+        real(self, *a, **k)
+        if not floor_level:
+            self.levels = self.levels[-1:]
+
+    _hdr_dc._StoreProgram.__init__ = init
+    try:
+        return _hdr_commit(_hdr_rig(prices=_hdr_l_prices), _hdr_l_plan, _hdr_l_req)
+    finally:
+        _hdr_dc._StoreProgram.__init__ = real
+
+
+_hdr_l_two, _hdr_l_one = _hdr_levels(True), _hdr_levels(False)
+R.check(
+    "a second level at the floor: the long charge at the floor ships where it is the cheaper one (every "
+    "step at the floor, more than one step), and with the floor level taken from the program the plan "
+    "that ships buys more energy",
+    np.all(_hdr_l_two[_hdr_l_two > 0] == 1.0) and int(np.sum(_hdr_l_two > 0)) > 1
+    and float(np.sum(_hdr_l_one)) > float(np.sum(_hdr_l_two)) + 0.5 and _hdr_under(_hdr_l_one, 1.0) == 0,
+    f"kW-steps {float(np.sum(_hdr_l_two)):.2f} with the floor level, {float(np.sum(_hdr_l_one)):.2f} without",
+)
+
+# 5. A start priced as one start, on the combined draw. Two candidates, the
+# same in both arms: the program's (replaced here by a fixed late charge,
+# less energy) and the lifted plan, whose charge follows a space run.
+_hdr_p_plan = np.zeros(_HDR_N)
+_hdr_p_plan[[12, 13]] = 0.6
+_hdr_p_late = np.zeros(_HDR_N)
+_hdr_p_late[20] = 1.0
+_hdr_p_space = np.zeros(_HDR_N)
+_hdr_p_space[8:12] = 2.0
+_hdr_p_req = np.where(np.arange(_HDR_N) >= 24, 49.4, 45.0)
+
+
+def _hdr_priced(space, start=2.0, replace=lambda *_a: _hdr_p_late.copy()):
+    return _hdr_programs(lambda: _hdr_commit(_hdr_rig(start=start), _hdr_p_plan, _hdr_p_req, space=space), replace)[0]
+
+
+_hdr_p_beside, _hdr_p_alone, _hdr_p_free = _hdr_priced(_hdr_p_space), _hdr_priced(None), _hdr_priced(_hdr_p_space, 0.0)
+R.check(
+    "the commit ranks its candidates by energy plus the starts of the combined draw: beside a space run "
+    "the charge that follows it ships though it buys more energy (no start of its own), with no space "
+    "plan the cheaper late charge ships (each is one start), and with no start priced the cheaper ships "
+    "beside the space run too",
+    np.array_equal(_hdr_p_beside, np.where(_hdr_p_plan > 0, 1.0, 0.0))
+    and np.array_equal(_hdr_p_alone, _hdr_p_late) and np.array_equal(_hdr_p_free, _hdr_p_late)
+    and _hdr_runs.start_count(_hdr_p_space + _hdr_p_beside, 1.0) == _hdr_runs.start_count(_hdr_p_space, 1.0) == 1.0,
+    f"{np.flatnonzero(_hdr_p_beside > 0).tolist()} {np.flatnonzero(_hdr_p_alone > 0).tolist()}",
+)
+# The program's own start price (design verdict item r11): what a start
+# pays inside the program is the share the space plan's step before leaves.
+_hdr_p_own = _hdr_priced(_hdr_p_space, replace=None)
+_hdr_p_own_alone = _hdr_priced(None, replace=None)
+R.check(
+    "the store program prices a start by the share of it the space plan's step before leaves open: "
+    "beside a space run its charge begins inside or straight after the run and adds no start to the "
+    "combined draw; with no space plan it stays on the plan's own steps",
+    _hdr_runs.start_count(_hdr_p_space + _hdr_p_own, 1.0) == 1.0
+    and 9 <= int(np.flatnonzero(_hdr_p_own > 0)[0]) <= 12
+    and set(np.flatnonzero(_hdr_p_own_alone > 0).tolist()) <= {12, 13}
+    and _hdr_runs.start_count(_hdr_p_own_alone, 1.0) == 1.0,
+    f"{np.flatnonzero(_hdr_p_own > 0).tolist()} {np.flatnonzero(_hdr_p_own_alone > 0).tolist()}",
+)
+
+# 8. Program cases (the contributor's). A floor at step 8 and a dearer
+# price there: the charge runs step 8 at the floor and fills the tank in
+# step 9, under the floor, ending inside it (the tail).
+_hdr_t_plan = np.zeros(_HDR_N)
+_hdr_t_plan[[7, 8, 9]] = 0.6
+_hdr_t_req = np.where(np.arange(_HDR_N) == 9, 54.85, np.where(np.arange(_HDR_N) == 8, 52.9, 45.0))
+_hdr_t_prices = np.where(np.arange(_HDR_N) == 9, 0.5, 1.0)
+_hdr_t = {
+    clamped: _hdr_commit(
+        _hdr_rig(clamped=clamped, t0=51.55, prices=_hdr_t_prices), _hdr_t_plan, _hdr_t_req)
+    for clamped in (False, True)
+}
+R.check(
+    "the tail: on an install that can end a run at any moment a charge that would pass the ceiling ends "
+    "inside its last step, under the floor, after a step at the floor; an install that cannot ships no "
+    "step under the floor for the same tank",
+    _hdr_t[False][8] == 1.0 and 0.6 <= _hdr_t[False][9] < 1.0 and _hdr_t[False][10] == 0.0
+    and _hdr_under(_hdr_t[False], 1.0) == 0
+    and bool(np.any(_hdr_t[True] > 0.0)) and float(np.min(_hdr_t[True][_hdr_t[True] > 0.0])) >= 1.0,
+    f"{np.round(_hdr_t[False][6:11], 3)} {np.round(_hdr_t[True][6:11], 3)}",
+)
+_hdr_f_off = np.zeros(_HDR_N, dtype=bool)
+_hdr_f_off[[17, 18]] = True
+_hdr_f_plan = np.zeros(_HDR_N)
+_hdr_f_plan[[14, 15]] = 0.9
+_hdr_f_out = _hdr_commit(_hdr_rig(prices=_hdr_l_prices), _hdr_f_plan, _hdr_l_req, forced_off=_hdr_f_off)
+_hdr_f_free = _hdr_commit(_hdr_rig(prices=_hdr_l_prices), _hdr_f_plan, _hdr_l_req)
+R.check(
+    "a forced-off step stays off in the committed plan; the same tank with none forced charges on one "
+    "of those steps (the control)",
+    bool(np.any(_hdr_f_out > 0.0)) and not np.any(_hdr_f_out[_hdr_f_off] > 0.0) and bool(np.any(_hdr_f_free[_hdr_f_off] > 0.0)),
+    f"{np.flatnonzero(_hdr_f_out > 0).tolist()} {np.flatnonzero(_hdr_f_free > 0).tolist()}",
+)
+_hdr_5_n = 96
+_hdr_5_plan = np.zeros(_hdr_5_n)
+_hdr_5_plan[[20, 40, 60, 80]] = 1.8
+_hdr_5_rig = _hdr_rig(n=_hdr_5_n, dt=1.0 / 12.0, draws=np.full(_hdr_5_n, 0.4))
+_hdr_5_out = _hdr_dc.commit_charges(
+    _hdr_5_rig.planner, _hdr_5_plan, (_hdr_5_rig.ctx, *_hdr_5_rig.tank),
+    (np.minimum(48.5, _hdr_5_rig.temps(_hdr_5_plan)[1:]), np.full(_hdr_5_n, 55.0)), None, None, None)
+_hdr_5_on = _hdr_5_out > 0.0
+_hdr_5_runs = [len(g) for g in "".join("1" if v else "0" for v in _hdr_5_on).split("0") if g]
+_hdr_5_gaps = [len(g) for g in "".join("1" if v else "0" for v in _hdr_5_on).strip("0").split("1") if g]
+R.check(
+    "at a 5-minute step every committed charge and every pause between two is at least the two steps "
+    "MIN_RUN and MIN_PAUSE cover, where the uncommitted plan's charges were one step each",
+    len(_hdr_5_runs) >= 1 and min(_hdr_5_runs) >= 2 and (not _hdr_5_gaps or min(_hdr_5_gaps) >= 2)
+    and not np.array_equal(_hdr_5_out, _hdr_5_plan),
+    f"runs {_hdr_5_runs}, pauses {_hdr_5_gaps}",
+)
+# Nothing to commit: a plan that already runs, with no start priced, ships
+# as it is (design verdict item r9: the rule that ships the uncommitted plan
+# is this one, not the ranking).
+_hdr_r_plan = np.zeros(_HDR_N)
+_hdr_r_plan[[17, 18]] = 1.4
+_hdr_r_seen = _hdr_programs(lambda: (
+    _hdr_commit(_hdr_rig(start=0.0), _hdr_r_plan, _hdr_l_req) is _hdr_r_plan,
+    _hdr_commit(_hdr_rig(start=0.0), _hdr_l_plan, _hdr_l_req) is _hdr_l_plan,
+    _hdr_commit(_hdr_rig(start=0.5), _hdr_r_plan, _hdr_l_req) is _hdr_r_plan))
+R.check(
+    "with no start priced a plan whose charges already run ships as it is, the same object, and the "
+    "program is not asked; one with a step under the floor, or with a start priced, is committed",
+    _hdr_r_seen[0][0] is True and _hdr_r_seen[0][1] is False and len(_hdr_r_seen[1]) == 2,
+    f"{_hdr_r_seen[0]}, program calls {len(_hdr_r_seen[1])}",
+)
+R.check(
+    "charges_run: a step under the floor is a charge that runs only as the last step of a charge whose "
+    "step before ran at the floor or above, and only where a run may end inside a step",
+    _hdr_dc.charges_run(np.array([0.0, 1.0, 0.7, 0.0]), 1.0, True)
+    and not _hdr_dc.charges_run(np.array([0.0, 1.0, 0.7, 0.0]), 1.0, False)
+    and not _hdr_dc.charges_run(np.array([0.0, 1.0, 0.7, 1.0]), 1.0, True)
+    and not _hdr_dc.charges_run(np.array([0.0, 0.7, 0.0, 0.0]), 1.0, True)
+    and not _hdr_dc.charges_run(np.array([0.0, 0.8, 0.7, 0.0]), 1.0, True)
+    and _hdr_dc.charges_run(np.array([1.0, 0.7]), 1.0, True)
+    and _hdr_dc.charges_run(np.array([0.0, 1.0, 3.0, 0.0]), 1.0, False),
+    "",
+)
+
+
+# 6. Combi (R10-COMBI-TANK's exchange). The rounds exchange uncommitted
+# plans; one committed build follows on the settled flux and ships only
+# where the store, under the flux that plan itself leaves, falls no further
+# under the requirement than the last round's.
+def _hdr_combi(cost, slack=None):
+    opt = _StoreOpt(ThermalModel(_ct_params()), _StoreCfg(
+        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0, cycling_cost=cost))
+    real, saved, calls = _hdr_om._combi_flux_exchange, _hdr_om._COMBI_COMMIT_SLACK_K, []
+
+    def exchange(o, h, planner, *rest):
+        build, charge = DhwPlanner._build_dhw_requirements, planner.charge_runs
+
+        def run(runs_planned):
+            builds = []
+
+            def counted(self, *a, **k):
+                got = build(self, *a, **k)
+                builds.append((self.charge_runs is not None, np.array(got[0].schedule)))
+                return got
+
+            DhwPlanner._build_dhw_requirements, planner.charge_runs = counted, runs_planned
+            try:
+                out = real(o, h, planner, *rest)
+            finally:
+                DhwPlanner._build_dhw_requirements, planner.charge_runs = build, charge
+            return SimpleNamespace(rounds=[s for c, s in builds if not c], commits=[s for c, s in builds if c], out=out)
+
+        # The same exchange with the planner handed no ChargeRuns, then as the solve runs it.
+        calls.append((run(None), run(charge)))
+        return calls[-1][1].out
+
+    _hdr_om._combi_flux_exchange = exchange
+    if slack is not None:
+        _hdr_om._COMBI_COMMIT_SLACK_K = slack
+    try:
+        opt.optimize(inputs=solve_inputs(
+            initial_state=ThermalState(room_temperature=21.0, slab_temperature=23.0, buffer_tank_temperature=50.0,
+                                       dhw_temperature=50.0, outdoor_temperature=0.0),
+            prices=_CT_PRICES, outdoor_temps=np.full(96, 0.0), wind_speeds=np.zeros(96),
+            precipitation=np.zeros(96), solar_radiation=np.zeros(96), start_time=datetime(2026, 1, 15)))
+    finally:
+        _hdr_om._combi_flux_exchange, _hdr_om._COMBI_COMMIT_SLACK_K = real, saved
+    return calls[-1]
+
+
+(_hdr_x_none, _hdr_x), (_hdr_xr_none, _hdr_x_refused), (_, _hdr_x_free) = _hdr_combi(0.5), _hdr_combi(0.5, slack=-np.inf), _hdr_combi(0.0)
+R.check(
+    "combi: the exchange's rounds build with a planner handed no runs to commit, the same number and "
+    "the same last plan as the same exchange with no ChargeRuns at all; that one and an unengaged solve "
+    "make no committed build, an engaged one makes one, after the rounds",
+    0 < len(_hdr_x.rounds) == len(_hdr_x_none.rounds) <= _hdr_om._COMBI_EXCHANGE_ROUNDS
+    and np.array_equal(_hdr_x.rounds[-1], _hdr_x_none.rounds[-1])
+    and not _hdr_x_none.commits and not _hdr_x_free.commits and len(_hdr_x.commits) == 1,
+    f"rounds {len(_hdr_x.rounds)} and {len(_hdr_x_none.rounds)}, committed builds {len(_hdr_x.commits)}",
+)
+R.check(
+    "combi: the committed build ships where the store under its own flux holds what the last round's "
+    "plan held, with no step under the floor but a charge's last; refused (the slack taken away), the "
+    "last round's plan ships, as it does with no ChargeRuns",
+    np.array_equal(_hdr_x.out, _hdr_x.commits[0]) and _hdr_under(_hdr_x.out, 1.0) == 0
+    and not np.array_equal(_hdr_x.out, _hdr_x_none.out)
+    and np.array_equal(_hdr_x_refused.out, _hdr_xr_none.out)
+    and not np.array_equal(_hdr_x_refused.out, _hdr_x_refused.commits[0]),
+    f"under the floor: committed {_hdr_under(_hdr_x.out, 1.0)}, last round {_hdr_under(_hdr_x_none.out, 1.0)}",
+)
+
+# The external-heat and peak-guard suppression runs after the commit point
+# (design verdict item r3): on a solve that plans runs it takes a committed
+# charge whole or leaves it whole.
+_hdr_s_plan = np.array([0.0, 1.0, 1.0, 0.7, 0.0, 1.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0])
+_hdr_s_mask = np.array([True, True, True, False, False, True, True, True, False, False, False, False])
+_hdr_s_kept = _hdr_dc.whole_charges(_hdr_dc.ChargeRuns(0.5, False, False), _hdr_s_plan, _hdr_s_mask)
+_hdr_s_left = np.where(_hdr_s_kept, 0.0, _hdr_s_plan)
+R.check(
+    "a suppression takes a committed charge whole or leaves it whole: the charge it would cut before its "
+    "tail stays (no lone step under the floor), the one it covers goes, and the steps outside any "
+    "charge stay suppressed; on a solve that plans no runs the mask is returned as it is, which leaves "
+    "the tail alone (the control)",
+    np.array_equal(_hdr_s_left, [0.0, 1.0, 1.0, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0])
+    and _hdr_dc.charges_run(_hdr_s_left, 1.0, True)
+    and bool(_hdr_s_kept[0] and _hdr_s_kept[7])
+    and _hdr_dc.whole_charges(None, _hdr_s_plan, _hdr_s_mask) is _hdr_s_mask
+    and not _hdr_dc.charges_run(np.where(_hdr_s_mask, 0.0, _hdr_s_plan), 1.0, True),
+    f"{_hdr_s_left}",
+)
+
+# The constants and the boundaries a mutant moved without a check failing.
+# The grid, the table spacing and the margin are design choices (the
+# contributor's spike on one install): pinned by value, so a change is a
+# decision and not a drift. The two tolerances are the planners' 0.05 K.
+R.check(
+    "the store program's grid is 0.25 K, its COP table 1 K and its margin 0.02 K, and the commit's and "
+    "the combi exchange's tolerances are the planners' 0.05 K (design choices, pinned by value)",
+    (_hdr_dc._STORE_GRID_K, _hdr_dc._COP_KNOT_K, _hdr_dc._STORE_MARGIN_K) == (0.25, 1.0, 0.02)
+    and _hdr_dc.SHORTFALL_K == _hdr_om._COMBI_COMMIT_SLACK_K == 0.05,
+    f"{_hdr_dc._STORE_GRID_K} {_hdr_dc._COP_KNOT_K} {_hdr_dc._STORE_MARGIN_K} {_hdr_om._COMBI_COMMIT_SLACK_K}",
+)
+_hdr_e_held = np.full(8, 50.05)
+_hdr_e_edge = _hdr_e_held - _hdr_dc.SHORTFALL_K
+R.check(
+    "the acceptance's floor clause passes a walk exactly the tolerance under the floor and refuses the "
+    "next float down",
+    _hdr_dc.charge_refusal(_hdr_b_plan, None, lambda _p: np.r_[50.0, _hdr_e_edge], _hdr_e_held) is None
+    and _hdr_dc.charge_refusal(
+        _hdr_b_plan, None, lambda _p: np.r_[50.0, np.nextafter(_hdr_e_edge, 0.0)], _hdr_e_held) == ("floor", 0),
+    "",
+)
+# What a start pays inside the program, read off the program itself.
+_hdr_q_space = np.r_[np.zeros(4), np.full(4, 2.0), np.full(4, 0.5), np.zeros(_HDR_N - 12)]
+
+
+def _hdr_start_price(running, space=_hdr_q_space):
+    rig = _hdr_rig(start=2.0, running=running)
+    return _hdr_dc._StoreProgram(
+        rig.planner, rig.ctx, _hdr_p_plan, rig.tank, (np.full(_HDR_N, 45.0), np.full(_HDR_N, 55.0)), None, space,
+    ).start_price
+
+
+R.check(
+    "the program's start price is the start cost less the share of a start the space plan's step before "
+    "carries: all of it after an idle step, none after a step at the floor or above, half after half the "
+    "floor, and none on the first step while the compressor runs",
+    np.array_equal(_hdr_start_price(False)[[0, 4, 5, 8, 9, 12, 13]], [2.0, 2.0, 0.0, 0.0, 1.0, 1.0, 2.0])
+    and _hdr_start_price(True)[0] == 0.0 and _hdr_start_price(True)[1] == 2.0,
+    f"{_hdr_start_price(False)[:14]}",
+)
+# A tank that starts over its ceiling coasts: the ceiling binds a charging
+# step only. A fill needs room: a tank already at its mark is not filled.
+_hdr_h_plan = np.zeros(_HDR_N)
+_hdr_h_plan[[26, 27]] = 0.6
+_hdr_h_rig = _hdr_rig(t0=56.0, draws=np.full(_HDR_N, 0.5))
+_hdr_h_out, _hdr_h_seen = _hdr_programs(lambda: _hdr_commit(
+    _hdr_h_rig, _hdr_h_plan, np.minimum(49.0, _hdr_h_rig.temps(_hdr_h_plan)[1:])))
+_hdr_h_prog = _hdr_dc._StoreProgram(
+    _hdr_h_rig.planner, _hdr_h_rig.ctx, _hdr_h_plan, _hdr_h_rig.tank,
+    (np.full(_HDR_N, 45.0), np.full(_HDR_N, 55.0)), None, np.zeros(_HDR_N))
+_hdr_h_mark = np.array([(55.0 - _hdr_dc._STORE_MARGIN_K - _hdr_h_rig.ctx.tank_decay[1]
+                         + 0.5 * 0.25 / _hdr_h_rig.ctx.c_dhw) / _hdr_h_rig.ctx.tank_decay[0]])
+R.check(
+    "a store that begins over its ceiling pauses there and the program still finds its plan (the ceiling "
+    "binds charging arrivals only); a tank that coasts onto its mark has no room and is not filled, one "
+    "a kelvin under is",
+    _hdr_h_seen[0] is not None and np.array_equal(_hdr_h_out, _hdr_h_seen[-1]) and _hdr_under(_hdr_h_out, 1.0) == 0
+    and abs(float(_hdr_h_rig.ctx.coast(_hdr_h_rig.tank[1], 0, _hdr_h_mark)[0]) - (55.0 - _hdr_dc._STORE_MARGIN_K)) < 1e-9
+    and not bool(_hdr_h_prog._to_ceiling(0, _hdr_h_mark + 1e-6)[1][0])
+    and bool(_hdr_h_prog._to_ceiling(0, _hdr_h_mark - 1.0)[1][0]),
+    f"{np.flatnonzero(_hdr_h_out > 0).tolist()}",
+)
+R.check(
+    "combi: the exchange leaves its rounds when a round's plan repeats the one before: the unengaged "
+    "solve stops short of the cap",
+    0 < len(_hdr_x_free.rounds) < _hdr_om._COMBI_EXCHANGE_ROUNDS,
+    f"{len(_hdr_x_free.rounds)} of {_hdr_om._COMBI_EXCHANGE_ROUNDS}; engaged {len(_hdr_x.rounds)}",
+)
+
+# The kernel hands an action whether the cells it leaves were running, and
+# the cell rule whether the arrival is in a run: one step from a pause.
+_hdr_g_cost = np.array([[np.inf], [0.0]])
+_hdr_g = _hdr_runs.advance(
+    _hdr_g_cost, np.zeros((2, 1)), _hdr_runs.state_moves(1, 1, np.nan),
+    ([lambda v, ran: (v, np.inf if ran else 1.0)], [lambda v, ran: (v, 5.0 if ran else 2.0)]), 0.0,
+    lambda v, charged: (np.zeros(v.size, dtype=np.int64), np.full(v.size, 10.0 if charged else 20.0)), 1)[0]
+R.check(
+    "from a pause the kernel tells a running and a pausing action their cells were not running, and "
+    "tells the cell rule which arrival is in a run",
+    _hdr_g[0, 0] == 11.0 and _hdr_g[1, 0] == 22.0,
+    f"{_hdr_g.ravel()}",
+)
+# Run and pause lengths are two numbers: with a 30-minute shortest pause at
+# a 15-minute step, a charge may be one step and no pause between two is.
+_hdr_m_real = _hdr_runs.MIN_PAUSE
+_hdr_runs.MIN_PAUSE = timedelta(minutes=30)
+try:
+    _hdr_m_rig = _hdr_rig(draws=np.full(_HDR_N, 0.9), running=True)
+    _hdr_m_plan = np.where(np.arange(_HDR_N) % 2 == 1, 0.8, 0.0)
+    _hdr_m_out = _hdr_commit(_hdr_m_rig, _hdr_m_plan, np.minimum(47.0, _hdr_m_rig.temps(_hdr_m_plan)[1:]))
+finally:
+    _hdr_runs.MIN_PAUSE = _hdr_m_real
+_hdr_m_on = "".join("1" if v else "0" for v in _hdr_m_out > 0.0)
+R.check(
+    "the shortest run and the shortest pause are held apart: with a two-step pause at a one-step run, "
+    "every pause between two committed charges is two steps or more, the plan charges on its first step "
+    "(the compressor runs, so that is no start and waits for no pause), and its charges hold the floors",
+    not np.array_equal(_hdr_m_out, _hdr_m_plan) and "101" not in _hdr_m_on and _hdr_m_on[0] == "1"
+    and _hdr_under(_hdr_m_out, 1.0) == 0
+    and _hdr_dc.charge_refusal(
+        _hdr_m_out, None, _hdr_m_rig.temps, np.minimum(47.0, _hdr_m_rig.temps(_hdr_m_plan)[1:])) is None,
+    _hdr_m_on,
+)
+# The program enters on a run while the compressor runs: a tank that must be
+# charged on the first step is held where the pump would not start a charge
+# then, and is not from a pause. Asked with every start allowed, both hold
+# it, so the entry alone decides.
+_hdr_y_draws = np.r_[3.0, np.zeros(_HDR_N - 1)]
+_hdr_y_blocked = np.r_[False, np.ones(_HDR_N - 1, dtype=bool)]
+
+
+def _hdr_entry(running, may_start):
+    rig = _hdr_rig(running=running, t0=46.0, draws=_hdr_y_draws)
+    return _hdr_dc._StoreProgram(
+        rig.planner, rig.ctx, np.zeros(_HDR_N), rig.tank, (np.full(_HDR_N, 45.0), np.full(_HDR_N, 55.0)), None,
+        np.zeros(_HDR_N),
+    ).plan(may_start.copy())
+
+
+_hdr_y_run, _hdr_y_pause = _hdr_entry(True, _hdr_y_blocked), _hdr_entry(False, _hdr_y_blocked)
+_hdr_y_free = [_hdr_entry(r, np.ones(_HDR_N, dtype=bool)) for r in (True, False)]
+R.check(
+    "while the compressor runs the store program enters on a run: a tank the first step's draw takes "
+    "under its floor is charged on that step where the pump would start no charge there, and from a "
+    "pause the same program has no plan; with every start allowed both enter to the same plan",
+    _hdr_y_run is not None and _hdr_y_run[0] > 0.0 and _hdr_y_pause is None
+    and all(p is not None and p[0] > 0.0 for p in _hdr_y_free) and np.array_equal(*_hdr_y_free)
+    and np.array_equal(_hdr_y_run, _hdr_y_free[0]),
+    f"{None if _hdr_y_run is None else np.round(_hdr_y_run[:4], 2)} {_hdr_y_pause is None}",
+)
+# The program says so where no mask keeps the store in bounds. A program
+# plan refused for anything but a start is not asked for again. A plan
+# the rating leaves with a step under the floor inside a charge is refused.
+_hdr_n_prog = _hdr_dc._StoreProgram(
+    _hdr_h_rig.planner, _hdr_h_rig.ctx, _hdr_h_plan, (50.0, np.zeros(_HDR_N)),
+    (np.full(_HDR_N, 70.0), np.full(_HDR_N, 55.0)), None, np.zeros(_HDR_N))
+_hdr_n_low = np.zeros(_HDR_N)
+_hdr_n_low[[17, 18, 19]] = [1.0, 0.7, 1.0]
+_hdr_n_out, _hdr_n_seen = _hdr_programs(
+    lambda: _hdr_commit(_hdr_rig(start=0.0), _hdr_l_plan, _hdr_l_req, start_below=np.full(_HDR_N, 80.0)),
+    lambda *_a: _hdr_n_low.copy())
+_hdr_n_cold, _hdr_n_cold_seen = _hdr_programs(
+    lambda: _hdr_commit(_hdr_rig(), _hdr_l_plan, _hdr_l_req, start_below=np.full(_HDR_N, 80.0)),
+    lambda *_a: np.zeros(_HDR_N))
+R.check(
+    "the store program returns no plan where a floor is over the ceiling; a program plan with a step "
+    "under the floor inside a charge does not ship though it is the cheapest and holds every floor, and "
+    "neither it nor one refused for a floor is asked for a second time",
+    _hdr_n_prog.plan(np.ones(_HDR_N, dtype=bool)) is None
+    and _hdr_dc.charge_refusal(_hdr_n_low, None, _hdr_rig().temps, np.minimum(_hdr_l_req, _hdr_rig().temps(_hdr_l_plan)[1:])) is None
+    and float(np.sum(_hdr_n_low)) < float(np.sum(_hdr_n_out)) and not np.array_equal(_hdr_n_out, _hdr_n_low)
+    and len(_hdr_n_seen) == 1 and len(_hdr_n_cold_seen) == 1 and bool(np.any(_hdr_n_cold > 0.0)),
+    f"{len(_hdr_n_seen)} {len(_hdr_n_cold_seen)} {np.round(_hdr_n_out[_hdr_n_out > 0], 2)}",
+)
+# A pump whose run power is its floor still commits: one level.
+_hdr_o_out = _hdr_commit(_hdr_rig(p_run=1.0), _hdr_l_plan, _hdr_l_req)
+_hdr_o_none = _hdr_commit(_hdr_rig(p_run=0.9), _hdr_l_plan, _hdr_l_req)
+R.check(
+    "a run power equal to the floor commits at that one level; a run power under the floor ships the "
+    "plan as it is, the same object",
+    bool(np.any(_hdr_o_out > 0.0)) and bool(np.all(_hdr_o_out[_hdr_o_out > 0.0] == 1.0)) and _hdr_o_none is _hdr_l_plan,
+    f"{np.round(_hdr_o_out[_hdr_o_out > 0], 2)}",
+)
+
+
+# The build hands the suppression its mask through whole_charges, with the
+# planner's own ChargeRuns: the external-heat golden, its planner told the
+# solve plans runs.
+def _hdr_suppressed():
+    real, runs_arg, seen = _hdr_dp.whole_charges, _hdr_om._charge_runs, []
+
+    def spy(charge_runs, plan, mask):
+        out = real(charge_runs, plan, mask)
+        seen.append((charge_runs, bool(np.all(out <= mask))))
+        return out
+
+    _hdr_dp.whole_charges, _hdr_om._charge_runs = spy, lambda _o, running: _hdr_dc.ChargeRuns(0.5, running, False)
+    try:
+        _hdr_golden.capture("external_heat_active", _hdr_golden.SCENARIOS["external_heat_active"])
+    finally:
+        _hdr_dp.whole_charges, _hdr_om._charge_runs = real, runs_arg
+    return seen
+
+
+_hdr_w = _hdr_suppressed()
+R.check(
+    "a build under external heat passes its suppression mask through whole_charges with the planner's "
+    "ChargeRuns, and what comes back suppresses no step the mask did not",
+    len(_hdr_w) >= 1 and all(c == (0.5, False, False) and within for c, within in _hdr_w),
+    f"{len(_hdr_w)} call(s)",
+)
+
+
 # -- R11-OUTSIDE-HONEST-METERED-FLOOR: the learned floor moves the plan -------
 # Group C of design/R11-OUTSIDE-HONEST-STARTS-RUNS for pull request 3529 by
 # Bankaifan: configured 0.53 kW against a metered running draw from 1.1 kW.
@@ -100028,7 +100835,7 @@ R.check(
     and _mf_set_attrs == _mf_cfg_attrs
     and _mf_min_attrs == {
         "pump_min_power": {"configured_min_kw": 0.53, "planned_min_kw": 1.1,
-                           "learned_min_kw": 1.1, "samples": 0},
+                           "learned_min_kw": 1.1, "samples": 0, "approach_kwh": None},
         "pump_min_power_source": "metered", "pump_min_power_reason": "measured"}
     and _mf_sensor._pump_min_power(_mf_within.as_dict())["pump_min_power"]["samples"]
     == _mf_within.min_samples != _mf_within.samples
@@ -100145,6 +100952,244 @@ R.check(
 )
 
 
+# The cell rule's floor bound, met exactly: a store that coasts onto the
+# floor less the tolerance, plus the margin, is inside it; one float higher
+# a floor puts the same coast outside, and the program charges at once.
+def _hdr_w_edge(t0=50.0):
+    rig = _hdr_rig(t0=t0, draws=np.full(_HDR_N, 0.5))
+    at = float(rig.ctx.coast(rig.tank[1], 0, np.array([t0]))[0])
+    edge = bound = at + _hdr_dc.SHORTFALL_K - _hdr_dc._STORE_MARGIN_K
+    for _ in range(64):
+        bound = edge - _hdr_dc.SHORTFALL_K + _hdr_dc._STORE_MARGIN_K
+        if bound == at:
+            break
+        edge = np.nextafter(edge, np.inf if bound < at else -np.inf)
+
+    def plan(first):
+        floors = np.full(_HDR_N, 45.0)
+        floors[0] = first
+        return _hdr_dc._StoreProgram(
+            rig.planner, rig.ctx, _hdr_l_plan, rig.tank, (floors, np.full(_HDR_N, 55.0)), None, np.zeros(_HDR_N),
+        ).plan(np.ones(_HDR_N, dtype=bool))
+
+    return bound == at, plan(edge), plan(np.nextafter(edge, np.inf))
+
+
+_hdr_w_met, _hdr_w_on, _hdr_w_over = _hdr_w_edge()
+R.check(
+    "the store program keeps a store that coasts exactly onto its floor bound (the floor less the tolerance, "
+    "plus the margin) in its cell and coasts through the first step; a first floor one float higher leaves "
+    "the coast outside and the program charges on the first step",
+    _hdr_w_met and _hdr_w_on is not None and _hdr_w_on[0] == 0.0
+    and _hdr_w_over is not None and _hdr_w_over[0] > 0.0,
+    f"{None if _hdr_w_on is None else np.flatnonzero(_hdr_w_on).tolist()} "
+    f"{None if _hdr_w_over is None else np.flatnonzero(_hdr_w_over).tolist()}",
+)
+# The grid's top: a combi flux that carries the store one cell past the
+# grid's top knot leaves it in no cell, and no mask keeps it in bounds; the
+# same flux onto the top knot itself plans (the control).
+_hdr_y_rig = _hdr_rig()
+_hdr_y_coast = float(_hdr_y_rig.ctx.coast(_hdr_y_rig.tank[1], 0, np.array([50.0]))[0])
+
+
+def _hdr_y_plan(top):
+    flux = np.zeros(_HDR_N)
+    flux[0] = (top - _hdr_y_coast) * _hdr_y_rig.ctx.c_dhw / _hdr_y_rig.ctx.dt
+    prog = _hdr_dc._StoreProgram(
+        _hdr_y_rig.planner, dataclasses.replace(_hdr_y_rig.ctx, tank_exo_kw=flux), _hdr_l_plan, _hdr_y_rig.tank,
+        (np.full(_HDR_N, 45.0), np.full(_HDR_N, 55.0)), None, np.zeros(_HDR_N))
+    return float(prog.knots[-1]), prog.plan(np.ones(_HDR_N, dtype=bool))
+
+
+_hdr_y_knot, _hdr_y_on = _hdr_y_plan(56.0)
+_hdr_y_past = _hdr_y_plan(56.0 + _hdr_dc._STORE_GRID_K)[1]
+R.check(
+    "the store program's grid ends at its top knot: a store a combi flux carries one cell past it has no "
+    "plan, and the same store carried onto the top knot plans",
+    _hdr_y_knot == 56.0 and _hdr_y_on is not None and _hdr_y_past is None,
+    f"top knot {_hdr_y_knot}; onto it {None if _hdr_y_on is None else np.flatnonzero(_hdr_y_on).tolist()}; "
+    f"past it {_hdr_y_past}",
+)
+# A space plan under zero is no space run: a charge the program plans under
+# it keeps its start, so the dear early charge does not undercut the plan
+# that ships with no space plan at all.
+_hdr_z_early = np.zeros(_HDR_N)
+_hdr_z_early[[14, 15]] = 1.0
+_hdr_z_space = np.where(_hdr_z_early > 0.0, -10.0, 0.0)
+_hdr_z_rig = _hdr_rig(start=2.0, prices=_hdr_l_prices)
+_hdr_z_none, _hdr_z_under = (
+    _hdr_programs(lambda s=s: _hdr_commit(_hdr_z_rig, _hdr_l_plan, _hdr_l_req, space=s), lambda *_a: _hdr_z_early.copy())[0]
+    for s in (np.zeros(_HDR_N), _hdr_z_space))
+R.check(
+    "a space plan under zero commits as no space plan: under the program's dear early charge it hides "
+    "no start, and the plan that ships is the one that ships with a zero space plan, not the early charge "
+    "(which the acceptance passes)",
+    np.array_equal(_hdr_z_under, _hdr_z_none) and not np.array_equal(_hdr_z_none, _hdr_z_early)
+    and _hdr_dc.charge_refusal(
+        _hdr_z_early, None, _hdr_z_rig.temps, np.minimum(_hdr_l_req, _hdr_z_rig.temps(_hdr_l_plan)[1:])) is None,
+    f"{np.flatnonzero(_hdr_z_none).tolist()} {np.flatnonzero(_hdr_z_under).tolist()}",
+)
+
+
+# The combi commit's tolerance, met exactly: the committed plan ships where
+# its store falls exactly the slack further under the requirement than the
+# plan the rounds settled on, and that plan where the slack is a float
+# short. Both plans are the ones the exchange's comparison reads. The
+# slack is set inside the solve, from the two worst gaps the exchange has
+# just read and before its comparison reads the slack, because one solve's
+# gaps need not be the next solve's to the float.
+def _hdr_k_combi(short):
+    real, exchange, saved, worst, inside, slacks, plans = (
+        DhwPlanner._dhw_shortfall, _hdr_om._combi_flux_exchange, _hdr_om._COMBI_COMMIT_SLACK_K, [], [], [], [])
+
+    def slack_for(committed, last):
+        slack = committed - last
+        for _ in range(64):
+            if last + slack == committed:
+                break
+            slack = np.nextafter(slack, np.inf if last + slack < committed else -np.inf)
+        if short:
+            slack = float(np.nextafter(committed, -np.inf)) - last
+            for _ in range(64):
+                if last + slack < committed:
+                    break
+                slack = float(np.nextafter(last + slack, -np.inf)) - last
+        return slack
+
+    def spy(self, *a, **k):
+        out = real(self, *a, **k)
+        if inside:
+            worst.append(float(np.max(out[1])))
+            plans.append(np.array(a[1]))
+            if len(worst) >= 2:
+                _hdr_om._COMBI_COMMIT_SLACK_K = slack_for(worst[-2], worst[-1])
+                slacks.append(_hdr_om._COMBI_COMMIT_SLACK_K)
+        return out
+
+    def within(*a, **k):
+        inside.append(True)
+        try:
+            return exchange(*a, **k)
+        finally:
+            inside.pop()
+
+    DhwPlanner._dhw_shortfall, _hdr_om._combi_flux_exchange = spy, within
+    try:
+        got = _hdr_combi(0.5)[1]
+        return got, worst[-2], worst[-1], float(slacks[-1]), plans[-2], plans[-1]
+    finally:
+        DhwPlanner._dhw_shortfall, _hdr_om._combi_flux_exchange = real, exchange
+        _hdr_om._COMBI_COMMIT_SLACK_K = saved
+
+
+_hdr_k_at, _hdr_k_c1, _hdr_k_r1, _hdr_k_s1, _hdr_k_pc1, _hdr_k_pr1 = _hdr_k_combi(False)
+_hdr_k_under, _hdr_k_c2, _hdr_k_r2, _hdr_k_s2, _hdr_k_pc2, _hdr_k_pr2 = _hdr_k_combi(True)
+_hdr_k_parts = (
+    _hdr_k_r1 + _hdr_k_s1 == _hdr_k_c1, _hdr_k_r2 + _hdr_k_s2 < _hdr_k_c2,
+    not np.array_equal(_hdr_k_pc1, _hdr_k_pr1), np.array_equal(_hdr_k_at.out, _hdr_k_pc1),
+    not np.array_equal(_hdr_k_pc2, _hdr_k_pr2), np.array_equal(_hdr_k_under.out, _hdr_k_pr2))
+R.check(
+    "combi: the committed build ships where its store falls exactly the slack further under the "
+    "requirement than the plan the rounds settled on, and that plan ships where the slack is a float short",
+    all(_hdr_k_parts),
+    f"{_hdr_k_parts}; committed {_hdr_k_c1!r} round {_hdr_k_r1!r} slack {_hdr_k_s1!r}; "
+    f"committed {_hdr_k_c2!r} round {_hdr_k_r2!r} slack {_hdr_k_s2!r}",
+)
+
+
+# The charge bound, met exactly: on 5-minute steps a floor-level charge
+# from 50 degC that ends exactly on step 0's ceiling less the margin, plus
+# the tolerance, is inside it. The fill to the ceiling sits more than
+# the tolerance under the floor there, so it is no stand-in. One float
+# lower, a ceiling leaves that charge outside, and the start moves off step 0.
+def _hdr_u_plans():
+    rig = _hdr_rig(dt=1.0 / 12.0, draws=np.full(_HDR_N, 0.5), prices=np.where(np.arange(_HDR_N) < 1, 0.2, 3.0))
+    floors = np.where(np.arange(_HDR_N) >= 4, 50.0, 45.0)
+
+    def program(first):
+        ceilings = np.full(_HDR_N, 60.0)
+        ceilings[0] = first
+        return _hdr_dc._StoreProgram(
+            rig.planner, rig.ctx, _hdr_l_plan, rig.tank, (floors, ceilings), None, np.zeros(_HDR_N))
+
+    lands = float(rig.ctx.coast(rig.tank[1], 0, np.array([50.0]))[0]) + float(
+        program(60.0)._rise(0, np.array([50.0]), rig.floor)[0])
+    edge = lands + _hdr_dc._STORE_MARGIN_K - 1e-9
+    for _ in range(64):
+        bound = edge - _hdr_dc._STORE_MARGIN_K + 1e-9
+        if bound == lands:
+            break
+        edge = np.nextafter(edge, np.inf if bound < lands else -np.inf)
+    on = program(edge)
+    fill = float(on._to_ceiling(0, np.array([50.0]))[0][0])
+    return (bound == lands, fill < rig.floor - 1e-9, on.plan(np.ones(_HDR_N, dtype=bool)),
+            program(np.nextafter(edge, -np.inf)).plan(np.ones(_HDR_N, dtype=bool)))
+
+
+_hdr_u_met, _hdr_u_under, _hdr_u_on, _hdr_u_off = _hdr_u_plans()
+R.check(
+    "the store program keeps a charge that ends exactly on its charge bound (the ceiling less the margin, "
+    "plus the tolerance) in its cell: on 5-minute steps a floor-level charge onto step 0's bound starts "
+    "the plan at step 0, where the fill to the ceiling sits under the floor; a ceiling one float lower "
+    "moves the start off step 0",
+    _hdr_u_met and _hdr_u_under and _hdr_u_on is not None and _hdr_u_on[0] == 1.0
+    and _hdr_u_off is not None and _hdr_u_off[0] == 0.0,
+    f"{None if _hdr_u_on is None else np.flatnonzero(_hdr_u_on).tolist()} "
+    f"{None if _hdr_u_off is None else np.flatnonzero(_hdr_u_off).tolist()}",
+)
+# The program's ceiling is the higher of the maximum and the uncommitted
+# plan's own walk: a plan that charges steps 0-2 at the run power over a
+# 55 degC maximum, in the cheap early hours, ships those steps. A program
+# held at the maximum alone cannot carry that walk, and moves the charge.
+_hdr_v_rig = _hdr_rig(prices=np.where(np.arange(_HDR_N) < 8, 0.5, 2.0), draws=np.full(_HDR_N, 0.3))
+_hdr_v_plan = np.where(np.arange(_HDR_N) < 3, 4.8, 0.0)
+_hdr_v_max = _hdr_commit(_hdr_v_rig, _hdr_v_plan, 45.0)
+R.check(
+    "the store program's ceiling is the higher of the maximum and the uncommitted plan's own walk: a plan "
+    "charging steps 0-2 at the run power past a 55 degC maximum ships exactly that plan",
+    float(np.max(_hdr_v_rig.temps(_hdr_v_plan))) > 55.0 and np.array_equal(_hdr_v_max, _hdr_v_plan),
+    f"walk max {float(np.max(_hdr_v_rig.temps(_hdr_v_plan))):.2f}; ships {np.flatnonzero(_hdr_v_max).tolist()}",
+)
+# The commit's early returns: a store with no capacity, and a plan that
+# charges nowhere, ship the plan given, the same object, unwalked (no walk
+# divides by a capacity of zero) and the program unasked. The null control,
+# the same rig and a plan that charges, walks it and asks the program.
+_hdr_x_rig = _hdr_rig()
+_hdr_x_empty = dataclasses.replace(
+    _hdr_x_rig.ctx, store=dataclasses.replace(_hdr_x_rig.ctx.store, capacity_kwh_per_c=0.0))
+
+
+def _hdr_x_commit(ctx, plan):
+    real, walks = DhwPlanner._ctx_temps, []
+
+    def walk(self, *a, **k):
+        walks.append(1)
+        return real(self, *a, **k)
+
+    DhwPlanner._ctx_temps = walk
+    try:
+        out, seen = _hdr_programs(lambda: _hdr_dc.commit_charges(
+            _hdr_x_rig.planner, plan, (ctx, *_hdr_x_rig.tank), (np.full(_HDR_N, 45.0), np.full(_HDR_N, 55.0)),
+            None, None, None))
+    finally:
+        DhwPlanner._ctx_temps = real
+    return out, len(seen) + len(walks)
+
+
+_hdr_x_zero = np.zeros(_HDR_N)
+(_hdr_x_a, _hdr_x_a_seen), (_hdr_x_b, _hdr_x_b_seen), (_hdr_x_c, _hdr_x_c_seen) = (
+    _hdr_x_commit(_hdr_x_empty, _hdr_l_plan), _hdr_x_commit(_hdr_x_rig.ctx, _hdr_x_zero),
+    _hdr_x_commit(_hdr_x_rig.ctx, _hdr_l_plan))
+R.check(
+    "commit_charges ships the plan given, unwalked and with the store program unasked, for a store with no "
+    "capacity and for a plan that charges nowhere; the same rig with a plan that charges walks it and asks",
+    _hdr_x_empty.c_dhw == 0.0 and _hdr_x_a is _hdr_l_plan and _hdr_x_a_seen == 0
+    and _hdr_x_b is _hdr_x_zero and _hdr_x_b_seen == 0 and _hdr_x_c_seen > 0,
+    f"no capacity: same {_hdr_x_a is _hdr_l_plan}, walks and programs {_hdr_x_a_seen}; nowhere: same "
+    f"{_hdr_x_b is _hdr_x_zero}, {_hdr_x_b_seen}; control: {_hdr_x_c_seen}",
+)
+
+
 R.section("#3616 R11-OUTSIDE-ROOMS-P1: a room list read, summarised, kept out of input health")
 
 # Phase 1 of room-level support (design/R11-OUTSIDE-ROOMS-P2): a list of room
@@ -102156,8 +103201,8 @@ _RH_T0 = _rh_dt(2026, 1, 5, tzinfo=_rh_tz.utc)
 _RH_M0 = int(_RH_T0.timestamp()) // 60
 
 
-def _rh_house(space_kw=2.0, kw=2.0, outdoor=-2.0):
-    return _rh.House(outdoor, 30.0, kw, space_kw, 0.0)
+def _rh_house(kw=2.0, outdoor=-2.0):
+    return _rh.House(outdoor, 30.0, kw, True)
 
 
 def _rh_feed(minutes, readings_at, history=None):
@@ -102303,7 +103348,7 @@ def _rh_simulate(days, interval, schedule, rooms=("climate.a", "climate.b"), see
         readings = [_RhReading(r, temps[r], 21.0, calls[r], "heat") for r in rooms]
         readings += [_RhReading(r, temps[r]) for r in sensor]
         fraction = sum(calls.values()) / len(calls)
-        house = _rh.House(outdoor, 30.0, 1.0 + 3.0 * fraction + rng.normal(0, 0.1), 2.0 * any(calls.values()), 0.0)
+        house = _rh.House(outdoor, 30.0, 1.0 + 3.0 * fraction + rng.normal(0, 0.1), any(calls.values()))
         period, _ = _rh.note(history, period, _RH_M0 + k * interval, readings, house)
         for r in temps:
             temps[r] += interval / 60 * (0.05 * (outdoor - temps[r]) + gain * calls.get(r, False)) + rng.normal(0, 0.02)
@@ -102383,14 +103428,14 @@ R.check(
     f"{_rh.identifiability_report(_rh_iqr)['house']}",
 )
 # The boundaries each threshold and range is read at (the mutation proof's survivors).
-_rh_cyc = [_rh.House(-2.0, 30.0, 2.0, 2.0, 0.0), _rh.House(-2.0, None, 2.0, 0.5, 0.0), _rh.House(-2.0, None, 2.0, 0.0, 0.0)]
+_rh_cyc = [_rh.House(-2.0, 30.0, 2.0, True), _rh.House(-2.0, None, 2.0, True), _rh.House(-2.0, None, 2.0, False)]
 _rh_bp = None
 _rh_bh = _rh.History()
 for _rh_k, _rh_hs in enumerate(_rh_cyc + [_rh_cyc[0]]):
     _rh_bp, _ = _rh.note(_rh_bh, _rh_bp, _RH_M0 + 10 * _rh_k, [_RhReading("sensor.a", 20.0 + _rh_k)], _rh_hs)
 R.check(
     "a sensor room keeps the period's first reading; a missing floor return keeps the last one read; "
-    "any space power counts the cycle as space heating and none does not",
+    "a cycle that heated the house alone counts as space heating and any other does not",
     _rh_bh.rooms["sensor.a"]["t"] == [2000] and _rh_bh.house["return"] == [3000] and _rh_bh.house["space"] == [6667],
     f"{_rh_bh.rooms} {_rh_bh.house}",
 )
@@ -102485,7 +103530,7 @@ R.check(
     f"{_rr.record_of(_rh_load_owner).history.times[:3]}",
 )
 _rh_bh2 = _rh.History()
-_rh_bp2 = _rh.note(_rh_bh2, _rh.note(_rh_bh2, None, _RH_M0, [_RhReading("sensor.a", 20.0)], _rh.House(None, None, None, 0.0, 0.0))[0],
+_rh_bp2 = _rh.note(_rh_bh2, _rh.note(_rh_bh2, None, _RH_M0, [_RhReading("sensor.a", 20.0)], _rh.House(None, None, None, False))[0],
                    _RH_M0 + 30, [_RhReading("sensor.a", 20.0)], _rh_house())
 R.check(
     "a period with no house value measured stores nulls: no outdoor, no floor return, no power, no space heating",
@@ -102609,10 +103654,10 @@ R.check(
 _rh_mix = _rh.History()
 _rh_mix_p = None
 for _rh_k, (_rh_rd, _rh_hs) in enumerate([
-    (_RhReading("climate.a", 20.0, 21.0, True, "heat"), _rh.House(-3.0, 28.0, 1.0, 2.5, 0.0)),
-    (_RhReading("climate.a", 21.0, 21.5, True, "heat", "stale"), _rh.House(-3.0, 28.0, 2.0, 2.5, 1.5)),
-    (_RhReading("climate.a", 22.0, 22.0, None, "heat"), _rh.House(-3.0, 28.0, 3.0, 2.5, 0.0)),
-    (_RhReading("climate.a", 23.0, 22.0, False, "heat"), _rh.House(-3.0, 28.0, 3.0, 2.5, 0.0)),
+    (_RhReading("climate.a", 20.0, 21.0, True, "heat"), _rh.House(-3.0, 28.0, 1.0, True)),
+    (_RhReading("climate.a", 21.0, 21.5, True, "heat", "stale"), _rh.House(-3.0, 28.0, 2.0, False)),
+    (_RhReading("climate.a", 22.0, 22.0, None, "heat"), _rh.House(-3.0, 28.0, 3.0, True)),
+    (_RhReading("climate.a", 23.0, 22.0, False, "heat"), _rh.House(-3.0, 28.0, 3.0, True)),
 ]):
     _rh_mix_p, _ = _rh.note(_rh_mix, _rh_mix_p, _RH_M0 + 7 * _rh_k, [_rh_rd], _rh_hs)
 _rh_mix_p, _ = _rh.note(_rh_mix, _rh_mix_p, _RH_M0 + 30, [], _rh_house())
@@ -102724,17 +103769,19 @@ _rh_cc_rec = _rr.record_of(_rh_cc)
 R.check(
     "a production coordinator's cycle hands the room history this cycle's outdoor reading (not the context "
     "the cycle started with: the first cycle reads -3.0, not the 5.0 default), the floor return (28.0), "
-    "metered power and the plan's space and hot-water kW, and the closed row holds them: outdoor the "
-    "period's last -500, return 2800, power the period's mean 200 (not the last 300), space heating two "
-    "cycles of three (the hot-water one not); null control, each value distinct from the one it could be "
-    "swapped for",
+    "metered power and whether the interval it settles heated the house alone (the previous cycle's plan: "
+    "none before the first), and the closed row holds them: outdoor the period's last -500, return 2800, "
+    "power the period's mean 200 (not the last 300), space heating one cycle of three (the one settling the "
+    "space-only plan, not the one planning it); null control, each value distinct from the one it could be "
+    "swapped for, and each cycle's own plan reads the other way on the second and third cycles",
     len(_rh_cc_seen) == len(_RH_CYCLES)
-    and [(h.outdoor_c, h.floor_return_c, h.measured_kw, h.space_kw, h.dhw_kw) for h in _rh_cc_seen]
-    == [(-3.0 - m / 10, 28.0, kw, s, d) for m, kw, s, d in _RH_CYCLES]
+    and [(h.outdoor_c, h.floor_return_c, h.measured_kw, h.space_alone) for h in _rh_cc_seen]
+    == [(-3.0 - m / 10, 28.0, kw, k > 0 and _RH_CYCLES[k - 1][2] > 0.0 >= _RH_CYCLES[k - 1][3])
+        for k, (m, kw, _s, _d) in enumerate(_RH_CYCLES)]
     and _rh_cc_rec is not None and _rh_cc_rec.history.times == [_RH_M0]
-    and _rh_cc_rec.history.house == {"outdoor": [-500], "return": [2800], "power": [200], "space": [6667]}
+    and _rh_cc_rec.history.house == {"outdoor": [-500], "return": [2800], "power": [200], "space": [3333]}
     and _rh_cc_rec.history.rooms["climate.a"]["call"] == [10000],
-    f"seen={[(h.outdoor_c, h.floor_return_c, h.measured_kw, h.space_kw, h.dhw_kw) for h in _rh_cc_seen]} "
+    f"seen={[(h.outdoor_c, h.floor_return_c, h.measured_kw, h.space_alone) for h in _rh_cc_seen]} "
     f"house={None if _rh_cc_rec is None else _rh_cc_rec.history.house}",
 )
 
@@ -102759,6 +103806,717 @@ R.check(
 )
 
 
+# --- R11-SEAM-learners: one freeze predicate (ADR-008, design/R11-SEAM-learners
+# at bee723ac). ``learning_freeze.reason`` owns which interval a learner may
+# ingest; the coordinator only builds the facts. Every check drives the
+# production predicate or a production learner through it.
+R.section("R11-SEAM-learners: the one freeze predicate")
+import asyncio as _lf_aio  # noqa: E402
+from datetime import timedelta as _lf_td  # noqa: E402
+from types import SimpleNamespace as _lf_NS  # noqa: E402
+from heatpump_optimizer import learning_freeze as _lf  # noqa: E402
+from heatpump_optimizer import coordinator as _lf_cm  # noqa: E402
+from homeassistant.util import dt as _lf_dt  # noqa: E402
+from heatpump_optimizer.const import CONF_DHW_TEMP_ENTITY as _LF_DHW  # noqa: E402
+
+_LF_K = _lf.Sample
+_LF_ALL = tuple(_LF_K)
+# The nine shared reasons in today's order, each alone, and the kinds each refuses:
+# every kind but the delivered ratio, ventilation only the room-air ones.
+_LF_ROOM = {_LF_K.ROOM_AIR, _LF_K.OCCUPANCY, _LF_K.COMFORT, _LF_K.SPACE_HEAT, _LF_K.CEILING}
+_LF_SHARED = [
+    (_lf.Facts(external_heat=True), "external_heat_source", set(_LF_ALL) - {_LF_K.DELIVERED_RATIO}),
+    (_lf.Facts(signals="heat_pump_fault"), "heat_pump_fault", set(_LF_ALL) - {_LF_K.DELIVERED_RATIO}),
+    (_lf.Facts(defrosting=True), "defrosting", set(_LF_ALL) - {_LF_K.DELIVERED_RATIO}),
+    (_lf.Facts(unusable={"k": "stale"}), "stale:k", set(_LF_ALL) - {_LF_K.DELIVERED_RATIO}),
+    (_lf.Facts(ventilation=True), "ventilation", _LF_ROOM),
+    (_lf.Facts(boost="boost_space"), "boost_space", set(_LF_ALL) - {_LF_K.DELIVERED_RATIO}),
+    (_lf.Facts(tail="early_cutoff"), "early_cutoff", set(_LF_ALL) - {_LF_K.DELIVERED_RATIO}),
+]
+_lf_table_bad = [
+    (want, kind.value) for facts, want, kinds in _LF_SHARED for kind in _LF_ALL
+    if _lf.reason(facts, ("k",), kind) != (want if kind in kinds else None)
+]
+# The order: every pair of shared facts answers the earlier one.
+_LF_FULL = _lf.Facts(external_heat=True, signals="heat_pump_fault", defrosting=True,
+                     unusable={"k": "stale"}, ventilation=True, boost="boost_space",
+                     tail="early_cutoff", away=True, away_recovery=True)
+_lf_order = []
+_lf_f = _LF_FULL
+for _lf_field, _lf_off in (("external_heat", False), ("signals", None), ("defrosting", False),
+                           ("unusable", {}), ("ventilation", False), ("boost", None), ("tail", None),
+                           ("away", False), ("away_recovery", False)):
+    _lf_order.append(_lf.reason(_lf_f, ("k",), _LF_K.COMFORT))
+    _lf_f = dataclasses.replace(_lf_f, **{_lf_field: _lf_off})
+_lf_order.append(_lf.reason(_lf_f, ("k",), _LF_K.COMFORT))
+R.check(
+    "each shared freeze reason refuses exactly its kinds, and the reasons rank in today's "
+    "order (external heat, signals, defrost, unusable key, ventilation, boost, tail), then "
+    "away and away recovery; an unusable key the ask does not name refuses nothing",
+    not _lf_table_bad
+    and _lf_order == ["external_heat_source", "heat_pump_fault", "defrosting", "stale:k",
+                      "ventilation", "boost_space", "early_cutoff", "away", "away_recovery", None]
+    and _lf.reason(_lf.Facts(unusable={"k": "stale"}), ("other",), _LF_K.ROOM_AIR) is None,
+    f"bad={_lf_table_bad} order={_lf_order}",
+)
+# The additive reasons: each refuses its own kind alone, never a plant or room-air ask.
+_LF_ADD = [
+    (_lf.Facts(away=True), _lf.NO_EVIDENCE, "away", {_LF_K.OCCUPANCY, _LF_K.COMFORT, _LF_K.TANK_DRAW}),
+    (_lf.Facts(away_recovery=True), _lf.NO_EVIDENCE, "away_recovery", {_LF_K.COMFORT}),
+    (_lf.Facts(), _lf.Evidence(unplanned_charge=True), "unplanned_charge",
+     {_LF_K.SPACE_HEAT, _LF_K.METERED_SPACE_HEAT}),
+    (_lf.Facts(), _lf.Evidence(at_running_floor=True), "at_running_floor", {_LF_K.CEILING}),
+    (_lf.Facts(), _lf.Evidence(charge_open=True), "charge_open", {_LF_K.TANK_DRAW}),
+    (_lf.Facts(), _lf.Evidence(ask_ignored=True), "ask_ignored", {_LF_K.DELIVERED_RATIO}),
+]
+_lf_add_bad = [
+    (want, kind.value) for facts, ev, want, kinds in _LF_ADD for kind in _LF_ALL
+    if _lf.reason(facts, ("k",), kind, ev) != (want if kind in kinds else None)
+]
+R.check(
+    "each additive reason refuses only its own kinds; a clean interval refuses nothing, and a "
+    "defrosting interval still reaches the delivered-ratio ask (#944)",
+    not _lf_add_bad
+    and all(_lf.reason(_lf.Facts(), ("k",), k) is None for k in _LF_ALL)
+    and _lf.reason(_lf.Facts(defrosting=True), ("k",), _LF_K.DELIVERED_RATIO) is None,
+    f"bad={_lf_add_bad}",
+)
+
+# Away on a real coordinator: the gains fold and the quiet-comfort record are
+# held, the curve tracker is held through the recovery; the home arm is the null.
+_lf_gate_n = next(n for n in range(10_000) if _lf_cm.internal_gains_gate_open(n))
+
+
+def _lf_gains(away):
+    c = _t2_coord(internal_gains_learning_enabled=True)
+    c._house_heat_loss_samples = _lf_gate_n
+    c._away_state.active = away
+    t = datetime(2026, 1, 12, 2, 0, tzinfo=UTC)
+    c._fold_internal_gains(t, _lf_NS(solar_radiation=0.0), 0.05, 0.25)
+    return c._internal_gains_profile
+
+
+def _lf_ask(kind, **away):
+    c = _t2_coord()
+    for k, v in away.items():
+        setattr(c._away_state, k, v)
+    return c._learning_frozen(_lf_cm.CONF_INDOOR_TEMP_ENTITY, sample=kind)
+
+
+R.check(
+    "away holds the internal-gains fold; at home the same interval folds (D7-s2-01)",
+    _lf_gains(True) is None and _lf_gains(False) is not None,
+    f"away={_lf_gains(True)} home={(_lf_gains(False) or [None])[:3]}",
+)
+R.check(
+    "on a real coordinator away refuses the occupancy and comfort asks and not a room-air or "
+    "plant one, and the recovery refuses the comfort ask alone (the curve tracker's own test, "
+    "moved into the predicate)",
+    _lf_ask(_LF_K.OCCUPANCY, active=True) == "away" and _lf_ask(_LF_K.COMFORT, active=True) == "away"
+    and _lf_ask(_LF_K.ROOM_AIR, active=True) is None and _lf_ask(_LF_K.PLANT, active=True) is None
+    and _lf_ask(_LF_K.COMFORT, recovery_active=True) == "away_recovery"
+    and _lf_ask(_LF_K.OCCUPANCY, recovery_active=True) is None
+    and _lf_ask(_LF_K.COMFORT) is None,
+    f"occ={_lf_ask(_LF_K.OCCUPANCY, active=True)} rec={_lf_ask(_LF_K.COMFORT, recovery_active=True)}",
+)
+
+
+def _lf_quiet(away):
+    c = _t2_coord(comfort_learning_enabled=True)
+    c._away_state.active = away
+    seen = []
+    c._optimization_result = _lf_NS(room_temp_trajectory=None)
+    real = c._learning_frozen
+
+    def spy(*keys, **kw):
+        seen.append(real(*keys, **kw))
+        return seen[-1]
+
+    c._learning_frozen = spy
+    c._record_quiet_comfort_period()
+    return seen
+
+
+R.check(
+    "the quiet-comfort record asks the occupancy kind: away refuses it, home does not",
+    _lf_quiet(True) == ["away"] and _lf_quiet(False) == [None],
+    f"away={_lf_quiet(True)} home={_lf_quiet(False)}",
+)
+
+
+def _lf_dhw(facts, fall_k):
+    """One interval of the production DHW learner, frozen through the real predicate."""
+    lrn = DhwProfileLearner(
+        FakeHass(), "lf", **_owned_params(ThermalParameters(dhw_enabled=True)),
+        frozen=lambda key, sample=_LF_K.ROOM_AIR, evidence=_lf.NO_EVIDENCE: _lf.reason(
+            facts, (key,), sample, evidence),
+        heating_active=lambda: False, external_heat_active=lambda: False,
+    )
+    lrn.last_temp_sample = 55.0
+    lrn.last_sample_time = _lf_dt.now() - _lf_td(hours=1)
+    lrn.heating_since_sample = False
+    profile, cooling = list(lrn.hourly_profile), lrn.cooling_samples
+    why = _lf_aio.run(lrn.async_learn_dynamics(55.0 - fall_k))
+    return why, lrn.cooling_samples - cooling, list(lrn.hourly_profile) != profile, lrn.draw_stats.as_dict()
+
+
+_lf_dhw_away = _lf_dhw(_lf.Facts(away=True), 2.0)
+_lf_dhw_home = _lf_dhw(_lf.Facts(), 2.0)
+_lf_sb_away = _lf_dhw(_lf.Facts(away=True), 0.3)
+_lf_sb_ext = _lf_dhw(_lf.Facts(external_heat=True), 0.3)
+R.check(
+    "away holds the tank's usage hours and draw booking, and returns the reason; the same "
+    "fall at home moves both (D7-s2-01)",
+    _lf_dhw_away[0] == "away" and not _lf_dhw_away[2] and _lf_dhw_away[3]["open_kwh"] == 0.0
+    and _lf_dhw_home[0] is None and _lf_dhw_home[2] and _lf_dhw_home[3]["open_kwh"] > 0.1,
+    f"away={_lf_dhw_away[:3]} {_lf_dhw_away[3]['open_kwh']} kWh home={_lf_dhw_home[:3]} "
+    f"{_lf_dhw_home[3]['open_kwh']} kWh",
+)
+R.check(
+    "away leaves the tank's standby cooling learning (a plant sample); external heat, a "
+    "shared reason, holds it",
+    _lf_sb_away[1] == 1 and _lf_sb_ext[1] == 0 and _lf_sb_ext[0] == "external_heat_source",
+    f"away cooling+={_lf_sb_away[1]} external cooling+={_lf_sb_ext[1]}",
+)
+
+
+
+def _lf_gains_step(residual):
+    """One dark gains fold on an hour already at a learned 0.6 kW, g0 the default."""
+    c = _t2_coord(internal_gains_learning_enabled=True)
+    c._house_heat_loss_samples = _lf_gate_n
+    g0 = float(c._ctx._thermal_params.internal_gains)
+    c._internal_gains_profile = [g0] * 24
+    c._internal_gains_profile[2] = 0.6
+    c._fold_internal_gains(datetime(2026, 1, 12, 2, 0, tzinfo=UTC), _lf_NS(solar_radiation=0.0),
+                           residual, 0.25)
+    return g0, c._internal_gains_profile[2]
+
+
+_lf_g0, _lf_g_still = _lf_gains_step(0.0)
+_lf_g_moved = _lf_gains_step(0.01)[1]
+R.check(
+    "the gains step's expectation is zero at the genuine gain: a zero residual leaves a learned "
+    "hour where it is, with no pull back to the configured constant (D2-s3-11); null control, "
+    "a nonzero residual moves it",
+    _lf_g0 != 0.6 and _lf_g_still == 0.6 and _lf_g_moved > 0.6,
+    f"g0={_lf_g0} after zero residual={_lf_g_still} after +0.01 K={_lf_g_moved}",
+)
+
+
+# --- R11-SEAM-learners: an unplanned charge is no space sample (#3760, D12-s3-03).
+# An unobserved interval the plan put no hot water in, over which the tank
+# thermometer rose past heat_energy.UNPLANNED_CHARGE_RISE_K, was a charge the
+# plan never asked for: every space-heat ask refuses it, the energy totals
+# book it as hot water. Each arm has its null: no rise, and (where the plan's
+# split decides) a planned hot-water share.
+R.section("R11-SEAM-learners: the unplanned-charge evidence")
+from unittest import mock as _uc_mock  # noqa: E402
+from heatpump_optimizer import heat_energy as _uc_he  # noqa: E402
+from heatpump_optimizer import sysid as _uc_sysid  # noqa: E402
+from heatpump_optimizer.accuracy import AccuracySample as _UcSample  # noqa: E402
+from heatpump_optimizer.accuracy import COP_REFUSED_FROZEN as _UC_FROZEN  # noqa: E402
+
+_UC_RISE = _uc_he.UNPLANNED_CHARGE_RISE_K + 2.0
+
+
+def _uc_tank(c, rise):
+    """This cycle's two tank reads, ``rise`` apart; no dwell: the interval is unobserved."""
+    _uc_he.meter_of(c).tank_c = (50.0, 50.0 + rise)
+    return c
+
+
+def _uc_flow(rise, dhw_kw=0.0, observed=False):
+    c = _uc_tank(_fl_coord(action={"power": 3.0, "dhw_power": dhw_kw}), rise)
+    if observed:
+        m, t0 = _uc_he.meter_of(c), datetime(2026, 1, 12, 2, 0, tzinfo=UTC)
+        m.dwell.observe(t0, _uc_he.SPACE, t0)
+        m.cycle = (t0, t0 + _lf_td(minutes=30))
+    c._flow_bias.observe_temps(flow_lift.curve_supply_temp(c._thermal_model, -5.0, c.target_temperature) + 6.0, 47.0)
+    _fold_flow_lift(c, _T6)
+    return c._flow_bias.samples, round(c._flow_bias.bias_k, 6)
+
+
+_uc_fl = {k: _uc_flow(*a) for k, a in {
+    "charge": (_UC_RISE,), "no_rise": (0.0,), "planned_share": (_UC_RISE, 0.3),
+    "observed": (_UC_RISE, 0.0, True)}.items()}
+R.check(
+    "an unobserved, plan-space-only cycle whose tank rose past the band folds no flow-curve bias "
+    "(its supply is the tank's charge temperature); null controls: no rise folds, a planned "
+    "hot-water share under the curve share folds (the plan put hot water in it), an observed "
+    "space cycle folds",
+    _uc_fl["charge"] == (0, 0.0) and _uc_fl["no_rise"][0] == 1
+    and _uc_fl["planned_share"][0] == 1 and _uc_fl["observed"][0] == 1,
+    f"{_uc_fl}",
+)
+
+
+def _uc_cop(rise, dhw_kw=0.0):
+    c = _uc_tank(_t2_coord(heat_pump_power_entity="sensor.hp_power"), rise)
+    c._current_action = {"power": 3.0, "dhw_power": dhw_kw}
+    c._measured_power = 2.6
+    return c._fold_measured_cop(None)
+
+
+_uc_cops = (_uc_cop(_UC_RISE), _uc_cop(0.0), _uc_cop(_UC_RISE, 1.0))
+R.check(
+    "the measured-COP fold refuses an unplanned charge as frozen; no rise, or a planned "
+    "hot-water share, is not frozen (null controls)",
+    _uc_cops[0] == _UC_FROZEN and _uc_cops[1] != _UC_FROZEN and _uc_cops[2] != _UC_FROZEN,
+    f"{_uc_cops}",
+)
+
+
+def _uc_totals(rise, pending_dhw=0.0):
+    """One settled interval's energy split; the NEXT interval's plan asks hot water."""
+    c = _uc_tank(_t2_coord(), rise)
+    c._current_action = {"power": 1.0, "dhw_power": 2.0}
+    pending = {"price": 2.0, "space_power": 2.0, "dhw_power": pending_dhw, "when": _T6}
+    c._accumulate_energy(_UcSample(when=_T6, actual_power_kw=2.0), 1.0, pending)
+    return round(c._energy_totals["space_energy_kwh"], 9), round(c._energy_totals["dhw_energy_kwh"], 9)
+
+
+_uc_tot = (_uc_totals(_UC_RISE), _uc_totals(0.0), _uc_totals(_UC_RISE, 0.5))
+R.check(
+    "the energy totals book an unplanned charge as hot water, read on the settled interval's own "
+    "split (the next interval's hot-water ask does not decide it); null controls: no rise books "
+    "space, a planned share books by the plan (review item c4e1a3b2)",
+    _uc_tot[0] == (0.0, 2.0) and _uc_tot[1] == (2.0, 0.0) and _uc_tot[2] == (1.6, 0.4),
+    f"{_uc_tot}",
+)
+
+
+# The predicate's own bounds (design section 3.2: an unobserved interval whose
+# plan put no hot water and some space in it, over which the tank rose by MORE
+# than the band). The band's value is a design choice, the fixer's: over a
+# probe's few-tenths wobble, under one charging cycle's rise (the D2 harness
+# tank rises 4 K a cycle and falls 0.5 K otherwise). A 1.5 K rise, a few
+# minutes of one charge, is a charge: a literal, so the value is pinned and not
+# only the comparison (a check relative to the constant moves with it).
+_UC_K = _uc_he.UNPLANNED_CHARGE_RISE_K
+_uc_split = _uc_he.Attribution(2.0, 0.0, False)
+_uc_bounds = {
+    "at_band": _uc_he.unplanned_charge(_uc_split, _UC_K),
+    "rise_1_5_k": _uc_he.unplanned_charge(_uc_split, 1.5),
+    "idle_plan": _uc_he.unplanned_charge(_uc_he.Attribution(0.0, 0.0, False), _UC_RISE),
+    "no_reading": _uc_he.unplanned_charge(_uc_split, None),
+}
+R.check(
+    "an unplanned charge is a rise past the band, not at it: a rise equal to "
+    "UNPLANNED_CHARGE_RISE_K is no charge, a 1.5 K rise is one; a plan with no space in it "
+    "(idle) is never one, whatever the tank did; no tank reading is never one (design 3.2)",
+    _uc_bounds == {"at_band": False, "rise_1_5_k": True, "idle_plan": False, "no_reading": False},
+    f"{_uc_bounds} band={_UC_K}",
+)
+
+
+# ``SystemIdentification.step`` books the plan's power x COP as delivered heat
+# while settling, and ``_step_power`` x COP while stepping. The step-phase line
+# is sysid.py:1795 at main 78d3b40221, not :1792 (review item c4e1a3b1). So an
+# interval whose heat went to the tank stands the experiment down first.
+def _uc_sid_run(rise):
+    c = _uc_tank(_t2_coord(), rise)
+    c._current_action = {"power": 3.0, "dhw_power": 0.0}
+    seen, downs = [], []
+    host = _lf_NS(active=True, stand_down=downs.append)
+    c._sysid = host
+    with _uc_mock.patch.object(_uc_sysid, "hold_reason", lambda s, frozen, cfg, now: seen.append(frozen) or frozen or "held"):
+        _lf_aio.run(c._run_system_identification(np.array([1.0])))
+    return seen, downs
+
+
+_uc_sid = (_uc_sid_run(_UC_RISE), _uc_sid_run(0.0))
+R.check(
+    "an unplanned charge during an experiment reaches its hold as the freeze and stands it down "
+    "through stand_down; no rise reaches it as no freeze (null control)",
+    _uc_sid[0] == (["unplanned_charge"], ["unplanned_charge"]) and _uc_sid[1][0] == [None],
+    f"{_uc_sid}",
+)
+
+
+def _uc_span(per_cycle_k, cycles=4):
+    """A heat counter's span over ``cycles`` half-hour reads, the tank rising ``per_cycle_k`` each."""
+    m = _uc_he.HeatEnergyMeter()
+    sig = _lf_NS(mode=_lf_NS(key=None), mode_live=False, mode_changed_at=None)
+    prm = _lf_NS(max_electrical_power=6.0, cop_nominal_floored=3.0)
+    t0, closes, cycle_evidence = datetime(2026, 1, 12, 2, 0, tzinfo=UTC), [], []
+    for i in range(cycles + 1):
+        at = t0 + _lf_td(minutes=30 * i)
+        m.observe_cycle(at, sig, _lf_NS(ok=True, value=10.0 + 2.5 * i, entity_id="sensor.heat"), 5.0 + 0.8 * i,
+                        30.0, (0.5, 2.0), prm, 50.0 + per_cycle_k * i)
+        cycle_evidence.append(m.unplanned_charge((2.0, 0.0)))
+        close = _uc_he.close_span(m, {"cop": True, "house": True, "lower": False}, (2.0, 0.0), "state", at,
+                                  3.0, "unaligned", lambda *a: a)
+        if close is not _uc_he.NO_SPAN:
+            closes.append(close.unplanned_charge)
+    return closes, any(cycle_evidence)
+
+
+_uc_spans = (_uc_span(0.8), _uc_span(0.0))
+R.check(
+    "a counter span whose tank rise is spread under the band on every cycle but past it over the "
+    "span is an unplanned charge at its close; a span with no rise is not (null control)",
+    _uc_spans[0] == ([True], False) and _uc_spans[1] == ([False], False),
+    f"{_uc_spans}",
+)
+
+
+def _uc_span_fold(rise):
+    """The span close on a real coordinator: what it hands the COP and house learners."""
+    c = _t2_coord(heat_pump_power_entity="sensor.hp_power")
+    reached = []
+    c._async_learn_house_heat_loss = lambda *a: reached.append("house") or _lf_aio.sleep(0)
+    c._fold_cop_evidence = lambda *a, **k: reached.append("cop")
+    close = _uc_he.SpanClose("interval", 2.0, 2.0, 6.0, 2.0, None,
+                             (6.0, _uc_he.Attribution(2.0, 0.0, False)), False, True, True, rise)
+    with _uc_mock.patch.object(_uc_he, "close_span", lambda *a, **k: close):
+        _lf_aio.run(_lf_cm._async_learn_heat_span(c, {}))
+    return reached, c._measured_cop.refusal, dict(c._learner_freezes)
+
+
+_uc_sf = (_uc_span_fold(True), _uc_span_fold(False))
+R.check(
+    "a span closed on an unplanned charge reaches neither the house learner nor the COP fold, "
+    "refuses the COP as frozen and notes the freeze once; the same span with no charge reaches "
+    "both (null control)",
+    _uc_sf[0] == ([], _UC_FROZEN, {"house": "unplanned_charge"})
+    and _uc_sf[1][0] == ["house", "cop"] and _uc_sf[1][2] == {},
+    f"{_uc_sf}",
+)
+
+
+
+def _uc_gate(rise, pending_dhw=0.0):
+    """The draw-range gate in ``_record_accuracy``: the ``frozen=`` it hands the fold."""
+    c = _uc_tank(_t2_coord(heat_pump_power_entity="sensor.hp_power"), rise)
+    c._measured_power = 2.6
+    c._pending_prediction = {"when": _lf_dt.now() - _lf_td(minutes=30), "split": (2.0, pending_dhw),
+                             "power": 2.0 + pending_dhw, "space_power": 2.0, "dhw_power": pending_dhw}
+    seen = []
+    with _uc_mock.patch.object(_lf_cm.draw_range, "fold", lambda *a, **k: seen.append(k["frozen"])):
+        try:
+            c._record_accuracy()
+        except Exception as err:  # noqa: BLE001 - only the fold's argument is judged
+            seen.append(type(err).__name__)
+    return seen
+
+
+_uc_gates = (_uc_gate(_UC_RISE), _uc_gate(0.0), _uc_gate(_UC_RISE, 0.5))
+R.check(
+    "the draw-range window refuses an unplanned charge on the pending interval's own split "
+    "(frozen=True, so no window sample and no map run commits); null controls: no rise, or a "
+    "planned hot-water share, hands frozen=False",
+    _uc_gates == ([True], [False], [False]),
+    f"{_uc_gates}",
+)
+
+
+
+# D2-s3-09: a draw-range experiment's ceiling sample at the running floor in
+# force says nothing of the top; ``ceiling_frozen`` drops it from the ceiling
+# store and from the window alike.
+from heatpump_optimizer import draw_range as _cf_dr  # noqa: E402
+
+_CF_P = dataclasses.replace(ThermalParameters(), min_electrical_power=1.0, max_electrical_power=6.0)
+_CF_CEIL = _lf_NS(written_c=55.0, gate_c=20.0, ceiling_c=55.0)
+
+
+def _cf_fold(drawn, floor_kw=None):
+    """One experiment interval at the ceiling set-point, its ceiling ask through the predicate."""
+    d = _cf_dr.DrawRange()
+    _cf_dr.fold(d, 3.0, (3.0, 0.0), _CF_P, frozen=False, distorted=False, defrost=False)  # keys the window
+    d.floor_kw = floor_kw
+    window = len(d.samples)
+    frozen = _lf.reason(_lf.Facts(), (), _LF_K.CEILING,
+                        _lf.Evidence(at_running_floor=_cf_dr.at_running_floor(d, drawn))) is not None
+    _cf_dr.fold(d, drawn, (6.0, 0.0), _CF_P, frozen=False, distorted=False, defrost=False,
+                command=_CF_CEIL, span=_cf_dr.Span(1.0e9, 1.0e9, experiment=True), ceiling_frozen=frozen)
+    return frozen, len(d.ceiling), len(d.samples) - window
+
+
+_cf = {k: _cf_fold(*a) for k, a in {"at_learned_floor": (1.5, 1.5), "at_configured_floor": (1.1,),
+                                     "top_4": (4.0, 1.5), "top_4_cfg": (4.0,),
+                                     "zero_floor": (0.0, 0.0),
+                                     "tolerance_edge": ((1.0 + _cf_dr.AGREE_TOLERANCE) * 1.5, 1.5)}.items()}
+R.check(
+    "a ceiling sample at the floor in force (learned 1.5 kW, or the configured 1.0 kW unlearned) "
+    "is ceiling-frozen and reaches neither the ceiling store nor the window; a 4.0 kW ceiling "
+    "sample is kept in the store (null control) (D2-s3-09, note 9b3d1e15); a floor in force of 0 kW "
+    "is no running floor, so a 0 kW draw under it is not ceiling-frozen (zero-floor null arm); a draw "
+    "exactly AGREE_TOLERANCE above the learned floor is still at it (the band is closed)",
+    _cf["at_learned_floor"] == (True, 0, 0) and _cf["at_configured_floor"] == (True, 0, 0)
+    and _cf["top_4"] == (False, 1, 0) and _cf["top_4_cfg"] == (False, 1, 0)
+    and not _cf["zero_floor"][0] and _cf["tolerance_edge"] == (True, 0, 0),
+    f"{_cf}",
+)
+
+
+# The coordinator's ceiling ask (``_ceiling_frozen``, what ``_record_accuracy``
+# hands ``draw_range.fold``): the metered draw at the learned floor is frozen,
+# a 4.0 kW draw is not, and with no draw read nothing is at the floor.
+from heatpump_optimizer.coordinator import _ceiling_frozen as _cf_ask  # noqa: E402
+
+
+def _cf_coord_ask(drawn):
+    c = _t2_coord()
+    c._accuracy.draw.floor_kw = 1.5
+    c._measured_power = drawn
+    return _cf_ask(c)
+
+
+_cf_asks = {k: _cf_coord_ask(v) for k, v in {"floor": 1.5, "top_4": 4.0, "unread": None}.items()}
+R.check(
+    "the coordinator's ceiling ask freezes a draw at the floor in force and keeps a 4.0 kW draw "
+    "and an unread one (null controls)",
+    _cf_asks == {"floor": True, "top_4": False, "unread": False},
+    f"{_cf_asks}",
+)
+
+
+# _interval_space_power on a commanded-only install: an unplanned charge leaves
+# the interval no space figure; no rise, or a planned hot-water share, leaves
+# the commanded space draw (the null controls).
+def _uc_space(rise, dhw_kw=0.0):
+    c = _uc_tank(_t2_coord(), rise)
+    c._current_action = {"power": 3.0, "dhw_power": dhw_kw}
+    return c._interval_space_power()
+
+
+_uc_spaces = (_uc_space(_UC_RISE), _uc_space(0.0), _uc_space(_UC_RISE, 1.0))
+R.check(
+    "the interval's space power is None on an unplanned charge; no rise, or a planned hot-water "
+    "share, gives the commanded space draw (null controls)",
+    _uc_spaces[0] is None and _uc_spaces[1] is not None and _uc_spaces[1] > 0.0
+    and _uc_spaces[2] is not None,
+    f"{_uc_spaces}",
+)
+
+
+# The wiring (review of c6c11df0b8): the tank thermometer reaches the meter only
+# through ``_observe_heat_energy``. Two real cycles read the configured tank
+# sensor, rising past the band over an unobserved, plan-space-only interval;
+# the interval's space power is refused. Null control: the tank flat. ``first_age``
+# is the first read's age in minutes: a stale read is no evidence (review of 3d8679b765).
+def _uc_wired(rise, first_age=1):
+    c = _t2_coord()
+    c._current_action = {"power": 3.0, "dhw_power": 0.0}
+    hass = FakeHass({})
+    reader = _fmReader(hass, {_LF_DHW: "sensor.tank"}, now=lambda: NOW)
+    for i, (temp, age) in enumerate(((50.0, first_age), (50.0 + rise, 1))):
+        at = NOW + _lf_td(minutes=30 * i)
+        hass.states._states["sensor.tank"] = FakeState(str(temp), last_updated=minutes_ago(age, NOW), unit="°C")
+        _lf_cm._observe_heat_energy(c, reader, at)
+    return _uc_he.meter_of(c).tank_c, c._interval_space_power()
+
+
+_uc_wire = (_uc_wired(_UC_RISE), _uc_wired(0.0))
+R.check(
+    "the coordinator's own cycle read hands the tank sensor to the meter: a rise past the band "
+    "over an unobserved, plan-space-only cycle leaves the interval no space power; the same "
+    "cycles with the tank flat give the commanded space draw (null control)",
+    _uc_wire[0] == ((50.0, 50.0 + _UC_RISE), None)
+    and _uc_wire[1][0] == (50.0, 50.0) and _uc_wire[1][1] is not None and _uc_wire[1][1] > 0.0,
+    f"{_uc_wire}",
+)
+
+
+# The stale arm: InputReader keeps a stale reading's value, so only the ``ok``
+# gate keeps it out. The fresh rise and fresh flat arms above are its controls.
+_uc_stale = _uc_wired(_UC_RISE, first_age=100000)
+R.check(
+    "a stale first tank read is no evidence: the meter's tank span opens on None and the "
+    "interval keeps its commanded space draw; the fresh rise and fresh flat arms above are "
+    "its controls (review of 3d8679b765)",
+    _uc_stale == ((None, 50.0 + _UC_RISE), 3.0),
+    f"{_uc_stale}",
+)
+
+
+# The room history's space share (#3616 phase 3a) reads the class (review of
+# fab2d371ed): its house line fits measured power over the cycles that heated
+# the house alone. The meter answers which, on the settled interval's split.
+def _uc_alone(rise, split=(2.0, 0.0), duty=None):
+    m = _uc_he.HeatEnergyMeter()
+    m.tank_c = (50.0, 50.0 + rise)
+    if duty is not None:
+        t0 = datetime(2026, 1, 12, 2, 0, tzinfo=UTC)
+        m.dwell.observe(t0, duty, t0)
+        m.cycle = (t0, t0 + _lf_td(minutes=30))
+    return m.served_space_alone(split)
+
+
+_uc_al = {k: _uc_alone(*a) for k, a in {
+    "charge": (_UC_RISE,), "no_rise": (0.0,), "planned_share": (0.0, (2.0, 0.5)), "idle": (0.0, (0.0, 0.0)),
+    "no_split": (0.0, None), "observed_space": (_UC_RISE, (2.0, 0.0), _uc_he.SPACE),
+    "observed_dhw": (0.0, (2.0, 0.0), _uc_he.DHW)}.items()}
+R.check(
+    "a cycle heated the house alone only by its attribution: an unplanned charge did not, nor a "
+    "planned hot-water share, an idle plan, no split, or an observed hot-water dwell the plan "
+    "called space; null controls: no rise, and an observed space dwell whatever the tank did",
+    _uc_al == {"charge": False, "no_rise": True, "planned_share": False, "idle": False, "no_split": False,
+               "observed_space": True, "observed_dhw": False},
+    f"{_uc_al}",
+)
+
+
+def _uc_room_cycle(rise, settled, upcoming=(2.0, 0.0)):
+    """One real cycle; the room history's space-alone tally of the House it is handed."""
+    c = Coord(_FakeHass(), _FakeEntry(data=_LC_DATA))
+    houses, real = [], _lf_cm._observe_heat_energy
+
+    async def prices():
+        c._prices = [{"total": 1.0, "starts_at": "2026-03-28T00:00:00Z"}] * 24
+
+    async def plan():
+        boost_mod.adopt_plan(c, {"mode": "plan", "power": upcoming[0], "dhw_power": upcoming[1]})
+
+    async def note(coord, now, readings, house):
+        houses.append(house)
+
+    def observe(coord, reader, at):
+        real(coord, reader, at)
+        _uc_he.meter_of(coord).tank_c = (50.0, 50.0 + rise)
+
+    c._fetch_tibber_prices, c.async_run_optimization = prices, plan
+    c._pending_prediction = {"when": _lf_dt.now() - _lf_td(minutes=30), "split": settled}
+    with _uc_mock.patch.object(_lf_cm.room_record, "async_note_cycle", note), \
+            _uc_mock.patch.object(_lf_cm, "_observe_heat_energy", observe):
+        _lf_aio.run(c._async_update_data())
+    period = _rh.Period(0)
+    for house in houses:
+        _rh._accumulate(period, [], house)
+    return len(houses), period.space
+
+
+_uc_rc = {k: _uc_room_cycle(*a) for k, a in {
+    "charge": (_UC_RISE, (2.0, 0.0)), "no_rise": (0.0, (2.0, 0.0)),
+    "settled_dhw": (0.0, (0.0, 2.0)), "upcoming_dhw": (0.0, (2.0, 0.0), (0.0, 2.0))}.items()}
+R.check(
+    "the room history counts a cycle as space heating on the settled interval's own split through "
+    "the meter: an unplanned charge is not, a settled hot-water interval is not though the next plan "
+    "asks space; null controls: no rise counts, and a settled space interval counts though the next "
+    "plan asks hot water (review of fab2d371ed, class E3)",
+    _uc_rc == {"charge": (1, 0), "no_rise": (1, 1), "settled_dhw": (1, 0), "upcoming_dhw": (1, 1)},
+    f"{_uc_rc}",
+)
+
+
+# The house and lower-floor learners' own per-cycle asks carry the cycle's
+# evidence (review of fab2d371ed, mutants O and P): both arms close no interval,
+# so only that evidence records why the learners paused, the cause the card shows.
+def _uc_card(rise):
+    c = _two_zone_learner(lower_entity="sensor.lower")
+    c._current_action = {"power": 3.0, "dhw_power": 0.0}
+    interval = _uc_tank(c, rise)._close_fabric_interval()
+    _lf_aio.run(c._async_learn_lower_floor_loss(interval))
+    _lf_aio.run(c._async_learn_house_heat_loss(interval))
+    return interval, dict(c._learner_freezes)
+
+
+_uc_cards = (_uc_card(_UC_RISE), _uc_card(0.0))
+R.check(
+    "an unplanned charge pauses the house and lower-floor learners as frozen on it, the reason "
+    "each records; the same cycle with no rise records nothing (null control), and neither arm "
+    "closes an interval",
+    _uc_cards[0] == (None, {"lower": "unplanned_charge", "house": "unplanned_charge"})
+    and _uc_cards[1] == (None, {}),
+    f"{_uc_cards}",
+)
+
+
+
+def _ch_trace(heated_k):
+    """The production DHW learner over a 10-minute trace: a 4 K fall reaching sample 2, then
+    three 3 K climbs; ``heated_k`` the samples the plan's flag marks. Booked kWh after it."""
+    state = {"heating": False}
+    lrn = DhwProfileLearner(
+        FakeHass(), "ch", **_owned_params(ThermalParameters(dhw_enabled=True)),
+        frozen=lambda key, sample=_LF_K.ROOM_AIR, evidence=_lf.NO_EVIDENCE: _lf.reason(
+            _lf.Facts(), (key,), sample, evidence),
+        heating_active=lambda: state["heating"], external_heat_active=lambda: False,
+    )
+    t0 = datetime(2026, 1, 14, 6, 0, tzinfo=UTC)
+    temps = [50.0, 50.0, 46.0, 49.0, 52.0, 55.0, 55.0]
+    try:
+        for k, temp in enumerate(temps):
+            _lf_dt.freeze(t0 + _lf_td(minutes=10 * k))
+            state["heating"] = k in heated_k
+            _lf_aio.run(lrn.async_learn_dynamics(temp))
+    finally:
+        _lf_dt.freeze(None)
+    return round(lrn.draw_stats.as_dict()["open_kwh"] + sum(sum(v) for v in lrn.draw_stats.reservoirs.values()), 4)
+
+
+_ch_charge, _ch_draw = _ch_trace({2, 3, 4, 5}), _ch_trace(set())
+R.check(
+    "a 60-minute charge whose start dip reaches a heated sample books no draw (the interval "
+    "ending on it is charge-open: no unheated rise ever takes the dip back) (D2-s3-08); null "
+    "control, the same 4 K fall with no charge flag books it",
+    _ch_charge == 0.0 and _ch_draw > 0.5,
+    f"charge={_ch_charge} kWh unflagged={_ch_draw} kWh",
+)
+
+
+def _ch_gap(minutes):
+    """The production DHW learner over one unheated 4 K fall sampled ``minutes`` apart: what it learned
+    (booked kWh, usage profile moved)."""
+    lrn = DhwProfileLearner(
+        FakeHass(), "gap", **_owned_params(ThermalParameters(dhw_enabled=True)),
+        frozen=lambda key, sample=_LF_K.ROOM_AIR, evidence=_lf.NO_EVIDENCE: _lf.reason(
+            _lf.Facts(), (key,), sample, evidence),
+        heating_active=lambda: False, external_heat_active=lambda: False,
+    )
+    t0, before = datetime(2026, 1, 14, 6, 0, tzinfo=UTC), list(lrn.hourly_profile)
+    try:
+        for at, temp in ((t0, 50.0), (t0 + _lf_td(minutes=minutes), 46.0)):
+            _lf_dt.freeze(at)
+            _lf_aio.run(lrn.async_learn_dynamics(temp))
+    finally:
+        _lf_dt.freeze(None)
+    booked = lrn.draw_stats.as_dict()["open_kwh"] + sum(sum(v) for v in lrn.draw_stats.reservoirs.values())
+    return round(booked, 4), lrn.hourly_profile != before
+
+
+_ch_gaps = {m: _ch_gap(m) for m in (0.5, 7 * 60, 10)}
+R.check(
+    "an unheated fall over an interval outside the sample window (30 s, or past "
+    "DHW_COOLING_MAX_SAMPLE_HOURS) teaches neither a draw nor the usage hours; null control, the "
+    "same 4 K fall over 10 minutes teaches both",
+    _ch_gaps[0.5] == (0.0, False) and _ch_gaps[420] == (0.0, False)
+    and _ch_gaps[10][0] > 0.0 and _ch_gaps[10][1],
+    f"{_ch_gaps}",
+)
+
+
+
+# Carries 0-1 (item 0116e1a6): the defrost derate's inference reads drawn over
+# asked; once the heat-ask probe reads the ask ignored (a pump that sets its own
+# power) that ratio is no delivery ratio, so the delivered-ratio ask refuses it.
+from heatpump_optimizer.draw_range import ASK_IGNORED as _DF_IGNORED  # noqa: E402
+
+
+def _df_settle(verdict=None, defrosting=False):
+    c = _t2_coord()
+    if verdict is not None:
+        c._measured_cop.probe.response = verdict
+    if defrosting:
+        c._pump_signals = dataclasses.replace(c._pump_signals, defrosting=True)
+    window = c._defrost_window.close(_lf_dt.now())
+    seen = []
+    c._defrost.observe = lambda *a: seen.append(a)
+    c._settle_defrost(_UcSample(when=_T6, predicted_power_kw=4.0, actual_power_kw=2.2, outdoor_temp=2.0), window)
+    return len(seen)
+
+
+R.check(
+    "the defrost inference folds no ratio once the probe reads the ask ignored; pending folds "
+    "it (null control), and so does a defrosting interval, the derate's own evidence (#944, "
+    "note 9b3d1e16)",
+    _df_settle(_DF_IGNORED) == 0 and _df_settle() == 1 and _df_settle(defrosting=True) == 1,
+    f"ignored={_df_settle(_DF_IGNORED)} pending={_df_settle()} defrosting={_df_settle(defrosting=True)}",
+)
+
+
 R.section("#3616 R11-OUTSIDE-ROOMS-3B: the room lift on the solve's record, the why-now row and the narrative")
 
 # design/R11-OUTSIDE-ROOMS-3B: the lift reaches the solve folded into
@@ -103016,4 +104774,433 @@ R.check(
     str(_oc_rows),
 )
 
+
+R.section("R11-OUTSIDE-START-APPROACH: a run's first steps draw what the pump draws (Bankaifan, comment 6944433306 on #3670)")
+# Series D's shape (Bankaifan's): from off, 1.25 kW falling 12.6 W/min to the
+# 0.53 kW floor; series H's: 0.785 kW for the first interval after the gate.
+# Figures are one install's; the checks pin the mechanism, not the install.
+from types import SimpleNamespace as _sa_NS  # noqa: E402
+import dataclasses as _sa_dc  # noqa: E402
+from heatpump_optimizer import approach as _sa_ap, draw_range as _sa_dr, runs as _sa_runs  # noqa: E402
+from heatpump_optimizer import optimizer as _sa_om  # noqa: E402
+from heatpump_optimizer.accuracy import COP_REFUSED_OFF_ASK as _SA_OFF_ASK, MeasuredCop as _SaCop  # noqa: E402
+
+_SA_P = _sa_NS(min_electrical_power=0.53, max_electrical_power=3.0)
+_SA_STEP_S = 300.0
+
+
+def _sa_feed(draw, rows, t0=1.0e9, params=_SA_P):
+    """Fold (drawn, space ask, hot water ask, gates) rows, 5 min each; the time after."""
+    t = t0
+    for drawn, space, dhw, *gates in rows:
+        g = {"frozen": False, "distorted": False, "defrost": False, **(gates[0] if gates else {})}
+        _sa_dr.fold(draw, drawn, (space, dhw), params, span=_sa_dr.Span(t, t + _SA_STEP_S), **g)
+        t += _SA_STEP_S
+    return t
+
+
+def _sa_run(n_floor=12, ramp=0.785):
+    """One series-D run from off, then a pause opening with series H's wind-down."""
+    return ([(1.25 - 0.0126 * 5 * i, 0.53, 0.0) for i in range(12)] + [(0.53, 0.53, 0.0)] * n_floor
+            + [(ramp, 0.0, 0.0)] + [(0.02, 0.0, 0.0)] * 11)
+
+
+def _sa_learned(runs_n=5, **kw):
+    d = _sa_dr.DrawRange()
+    t = _sa_feed(d, [(0.02, 0.0, 0.0)])
+    for _ in range(runs_n):
+        t = _sa_feed(d, _sa_run(**kw), t)
+    return d, t
+
+
+_sa_d, _sa_t = _sa_learned()
+# One outlier run (2.0 kW in its first bin) beside four of series D: a bin's
+# level is its median, so the first bin still reads 1.25 kW (a max or a mean moves).
+_sa_o, _sa_ot = _sa_learned(runs_n=4)
+_sa_ot = _sa_feed(_sa_o, [(2.0, 0.53, 0.0)] + _sa_run()[1:], _sa_ot)
+_sa_oa = _sa_dr.solve_approach(_sa_o, _SA_P, _sa_ot)
+_sa_a = _sa_dr.solve_approach(_sa_d, _SA_P, _sa_t)
+_sa_none, _ = _sa_learned(runs_n=0)
+_sa_two, _sa_t2 = _sa_learned(runs_n=2)
+# 3. The learner at both ends: zero evidence and a bin under its count read
+# none; five runs reproduce series D's excess within one bin's width
+# (5/60 h at 0.72 kW over the floor, 0.06 kWh; spike s1 read 0.377 kWh).
+R.check(
+    "approach learner: zero evidence and two runs (bins under MIN_COUNT) read no approach; five series-D "
+    "runs read an entry whose energy over the floor is series D's within one bin, and series H's ramp",
+    _sa_dr.solve_approach(_sa_none, _SA_P, 1e9) is None and _sa_dr.solve_approach(_sa_two, _SA_P, _sa_t2) is None
+    and _sa_a is not None and abs(_sa_a.entry_kwh(0.53) - 0.377) < 5 / 60 * 0.72
+    and _sa_a.ramp.size == 1 and abs(_sa_a.ramp[0] - 0.785) < 1e-9 and _sa_a.age_h == 0.0
+    and _sa_oa is not None and abs(_sa_oa.entry[0] - 1.25) < 1e-9,
+    f"entry {None if _sa_a is None else _sa_a.entry} kwh {None if _sa_a is None else _sa_a.entry_kwh(0.53)}",
+)
+
+
+def _sa_gated(**gates):
+    d, t = _sa_learned(runs_n=0)
+    for _ in range(5):
+        t = _sa_feed(d, [(r[0], r[1], r[2], gates) for r in _sa_run()], t)
+    return _sa_dr.solve_approach(d, _SA_P, t)
+
+
+_sa_high, _ = _sa_learned(runs_n=0)
+_sa_th = 1.0e9
+for _ in range(5):
+    _sa_th = _sa_feed(_sa_high, [(r[0], 1.5 if r[1] else 0.0, 0.0) for r in _sa_run(ramp=0.02)], _sa_th)
+R.check(
+    "approach learner folds nothing from a frozen, a distorted or a defrost interval, nor an entry asked above "
+    "the floor (a higher ask draws more by asking more)",
+    all(_sa_gated(**{k: True}) is None for k in ("frozen", "distorted", "defrost"))
+    and _sa_dr.solve_approach(_sa_high, _SA_P, _sa_th) is None,
+    str([_sa_gated(**{k: True}) for k in ("frozen", "distorted", "defrost")]),
+)
+_sa_stored = _sa_d.as_dict()
+_sa_stored["approach"]["entry"][0][0] = "x"
+_sa_back = _sa_dr.DrawRange.from_dict(_sa_stored)
+_sa_moved = _sa_dr.DrawRange.from_dict(_sa_d.as_dict())
+_sa_moved.approach.observe(0.02, (0.0, 0.0), 0.53, _sa_t, _sa_t + 300, sample=True, standby_kw=0.25,
+                           tolerance=0.15, config=(0.5, 3.0))
+R.check(
+    "a stored approach round-trips, a bad cell costs only that cell, and a changed configured range drops it",
+    _sa_dr.DrawRange.from_dict(_sa_d.as_dict()).approach.as_dict() == _sa_d.approach.as_dict()
+    and len(_sa_back.approach.entry[0]) == len(_sa_d.approach.entry[0]) - 1
+    and len(_sa_back.approach.entry[1]) == len(_sa_d.approach.entry[1])
+    and all(len(b) == 0 for b in _sa_moved.approach.entry),
+    str(_sa_back.approach.entry[0]),
+)
+# A restart (a gap longer than an interval) leaves the run's age unknown: no
+# entry is read across it, and the age reads None (books no entry at step 0).
+_sa_gap = _sa_dr.DrawRange.from_dict(_sa_d.as_dict())
+_sa_gap_t = _sa_feed(_sa_gap, [(1.25, 0.53, 0.0)], _sa_t + 3600)
+R.check(
+    "after a gap the live run's age is unknown and no entry sample is folded across it",
+    _sa_gap.approach.age_h(_sa_gap_t) is None
+    and [len(b) for b in _sa_gap.approach.entry] == [len(b) for b in _sa_d.approach.entry],
+    str(_sa_gap.approach.age_h(_sa_gap_t)),
+)
+
+# The learner's boundaries. Three runs (MIN_COUNT) already read a profile. An
+# ask exactly at the floor's tolerance is an entry sample; a draw exactly at
+# standby is no ramp sample. An interval starting exactly one interval after
+# the last ended is no gap, so the run continues; a gap inside a live run
+# leaves its age unknown. A sample at the age the profile covers is outside it.
+def _sa_obs(prof, drawn, space, t, **kw):
+    return prof.observe(drawn, (space, 0.0), 0.53, t, t + 300.0, sample=True, standby_kw=0.25,
+                        tolerance=0.15, config=(0.53, 3.0), **kw)
+
+
+_sa_three = _sa_dr.solve_approach(_sa_learned(runs_n=3)[0], _SA_P, _sa_learned(runs_n=3)[1])
+_sa_b = _sa_dr.DrawRange.from_dict(_sa_d.as_dict()).approach
+_sa_bt = _sa_t
+_sa_bn = len(_sa_b.entry[0])
+_sa_obs(_sa_b, 1.25, (1.0 + 0.15) * 0.53, _sa_bt)
+_sa_at_edge = len(_sa_b.entry[0]) == _sa_bn + 1
+_sa_cont = _sa_b.age_h(_sa_bt + 900.0)
+_sa_obs(_sa_b, 1.2, 0.53, _sa_bt + 600.0)
+_sa_cont_after = _sa_b.age_h(_sa_bt + 900.0)
+_sa_obs(_sa_b, 1.2, 0.53, _sa_bt + 7200.0)
+_sa_gap_age = _sa_b.age_h(_sa_bt + 7500.0)
+_sa_r0 = _sa_dr.DrawRange.from_dict(_sa_d.as_dict()).approach
+_sa_obs(_sa_r0, 0.6, 0.53, _sa_t)
+_sa_rk = len(_sa_r0.ramp[0])
+_sa_standby = _sa_obs(_sa_r0, 0.25, 0.0, _sa_t + 300.0)
+_sa_cov = _sa_dr.DrawRange.from_dict(_sa_d.as_dict()).approach
+_sa_obs(_sa_cov, 1.25, 0.53, _sa_t)
+_sa_edge_age = _sa_a.entry.size * 5 * 60.0
+_sa_kinds = [_sa_obs(_sa_cov, 0.6, 0.53, _sa_t + age) for age in np.arange(300.0, _sa_edge_age + 1.0, 300.0)][-2:]
+R.check(
+    "approach learner boundaries: three runs read a profile; an ask at the tolerance's edge is an entry sample; a "
+    "draw at standby is no ramp sample; an interval one interval after the last is no gap; a gap in a live run "
+    "reads its age unknown; the last covered bin is inside and the next is not",
+    _sa_three is not None and _sa_at_edge and _sa_cont_after is not None and _sa_cont_after > 0.0
+    and _sa_gap_age is None and _sa_standby is None and len(_sa_r0.ramp[0]) == _sa_rk
+    and _sa_kinds == ["inside", None],
+    f"three {_sa_three is not None} edge {_sa_at_edge} cont {_sa_cont_after} gap {_sa_gap_age} "
+    f"standby {_sa_standby} kinds {_sa_kinds}",
+)
+
+# 4. The ramp-down: the first pause interval after a space run is a ramp sample and
+# no idle reading (design note s3); with no run before it, it is the idle store's.
+_SA_GATE = _sa_NS(written_c=20.0, gate_c=20.0, ceiling_c=45.0)
+_sa_r, _sa_rt = _sa_learned(runs_n=1)
+_sa_r2 = _sa_dr.DrawRange.from_dict(_sa_r.as_dict())
+_sa_rt = _sa_feed(_sa_r2, [(1.0, 0.53, 0.0)], _sa_rt)
+_sa_idle0 = len(_sa_r2.idle)
+_sa_dr.fold(_sa_r2, 0.785, (0.0, 0.0), _SA_P, frozen=False, distorted=False, defrost=False, command=_SA_GATE, span=_sa_dr.Span(_sa_rt, _sa_rt + 300))
+_sa_r3 = _sa_dr.DrawRange.from_dict(_sa_r.as_dict())
+_sa_rt3 = _sa_feed(_sa_r3, [(0.02, 0.0, 0.0)], _sa_rt - 300)
+_sa_dr.fold(_sa_r3, 0.785, (0.0, 0.0), _SA_P, frozen=False, distorted=False, defrost=False, command=_SA_GATE, span=_sa_dr.Span(_sa_rt3, _sa_rt3 + 300))
+R.check(
+    "the first pause interval after a space run folds a ramp sample and no idle reading; after a pause "
+    "(null control) the same interval is an idle reading and no ramp sample",
+    len(_sa_r2.idle) == _sa_idle0 and len(_sa_r2.approach.ramp[0]) == len(_sa_r.approach.ramp[0]) + 1
+    and len(_sa_r3.idle) == len(_sa_r.idle) + 1 and len(_sa_r3.approach.ramp[0]) == len(_sa_r.approach.ramp[0]),
+    f"idle {_sa_idle0}->{len(_sa_r2.idle)}, null idle {len(_sa_r.idle)}->{len(_sa_r3.idle)}",
+)
+
+# The received draw. A 15-minute run at the floor from off takes the mean of
+# the profile's first three bins. A live run of unknown age books no entry. A
+# charge before a space run leaves it an entry (2: the space edge, not the start).
+_sa_plan = np.array([0.0, 0.53, 0.0, 0.0])
+_sa_got = _sa_runs.received(_sa_plan, 0.0, _sa_a, dt=0.25, p_max=3.0)
+_sa_unknown = _sa_runs.received(_sa_plan[1:], 0.0, _sa_a._replace(age_h=None), dt=0.25, p_max=3.0)
+_sa_charge = _sa_runs.received(np.array([0.0, 0.53, 0.53]), np.array([1.0, 0.0, 0.0]), _sa_a, dt=0.25, p_max=3.0)
+R.check(
+    "runs.received: a 15-minute run from off takes the mean of the first three bins, the pause after it the "
+    "ramp's share; unknown age books nothing; no approach is the shipped array itself",
+    abs(_sa_got[1] - float(np.mean(_sa_a.entry[:3]))) < 1e-9 and abs(_sa_got[2] - _sa_a.ramp[0] / 3) < 1e-9
+    and _sa_got[0] == 0.0 and np.array_equal(_sa_unknown, _sa_plan[1:])
+    and _sa_runs.received(_sa_plan, 0.0, None, dt=0.25, p_max=3.0) is _sa_plan
+    and _sa_runs.received(_sa_plan, 0.0, _sa_a, dt=0.25, p_max=0.8)[1] == 0.8,
+    f"{_sa_got} unknown {_sa_unknown}",
+)
+R.check(
+    "a charge before a space run leaves the run an entry while the combined draw starts once",
+    abs(_sa_charge[1] - float(np.mean(_sa_a.entry[:3]))) < 1e-9
+    and _sa_runs.edge_count(np.array([1.0, 0.53, 0.53])) == 1,
+    str(_sa_charge),
+)
+_sa_rows = np.stack([_sa_plan, np.array([0.53, 0.53, 0.0, 0.53])])
+_sa_b = _sa_runs.received(_sa_rows, 0.0, _sa_a._replace(age_h=0.5), dt=0.25, p_max=3.0)
+R.check(
+    "runs.received of a batch is the one-row answer per row, bit for bit, the live age continued at step 0",
+    all(np.array_equal(_sa_b[i], _sa_runs.received(_sa_rows[i], 0.0, _sa_a._replace(age_h=0.5), dt=0.25, p_max=3.0)) for i in range(2))
+    and abs(_sa_b[1][0] - float(np.mean(_sa_a.entry[6:9]))) < 1e-9,
+    str(_sa_b),
+)
+
+# 1. The objective: _shipped_and_received hands the true objective the received
+# draw, and a descent and an install with no approach the shipped one.
+_sa_opt = _sa_om.HeatPumpOptimizer(
+    _sa_om.ThermalModel(_sa_dc.replace(_sa_om.ThermalParameters(), min_electrical_power=0.53, max_electrical_power=3.0)),
+    _sa_dc.replace(_sa_om.OptimizationConfig(), clamp_planned_levels=True))
+_sa_opt._approach = _sa_a
+_sa_sr = _sa_om._shipped_and_received(_sa_opt, _sa_plan, None, None)
+_sa_sd = _sa_om._shipped_and_received(_sa_opt, _sa_plan, None, None, "relaxed")
+_sa_opt._approach = None
+_sa_s0 = _sa_om._shipped_and_received(_sa_opt, _sa_plan, None, None)
+R.check(
+    "the true objective's received draw is runs.received of the shipped plan; a descent and no approach "
+    "receive the shipped array itself",
+    np.array_equal(_sa_sr[2], _sa_got) and _sa_sr[0] is _sa_plan and _sa_sd[2] is _sa_plan and _sa_s0[2] is _sa_plan,
+    f"{_sa_sr[2]}",
+)
+
+# The published trajectory simulates the received draw the objective scored:
+# the simulation whose room trajectory a full solve publishes is runs.received
+# of the plan it ships. Null: with no approach it is the shipped plan itself.
+def _sa_solve(approach, dhw=False):
+    opt = _sa_om.HeatPumpOptimizer(
+        _sa_om.ThermalModel(_sa_dc.replace(_sa_om.ThermalParameters(), min_electrical_power=0.53, max_electrical_power=3.0, dhw_enabled=dhw)),
+        _sa_dc.replace(_sa_om.OptimizationConfig(), clamp_planned_levels=True))
+    n, seen, real = opt.config.n_steps, [], opt.model.simulate_trajectory
+
+    def spy(*a, **k):
+        out = real(*a, **k)
+        seen.append((np.array(k.get("power_schedule")), np.array(out[0])))
+        return out
+
+    opt.model.simulate_trajectory = spy
+    state = _sa_om.ThermalState(room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=9.0)
+    inputs = solve_inputs(initial_state=state, prices=0.2 + 0.1 * np.sin(np.arange(n) * 4 * np.pi / n),
+                          outdoor_temps=np.full(n, 9.0), start_time=datetime(2026, 1, 10, tzinfo=timezone.utc))
+    result = opt.optimize(inputs=_sa_dc.replace(inputs, approach=approach))
+    # The published simulation: the call whose room trajectory the result carries.
+    published = [p for p, room in seen if np.array_equal(room, np.asarray(result.room_temp_trajectory))]
+    return np.asarray(result.power_schedule), published[-1] if published else None
+
+
+for _sa_hw in (False, True):
+    _sa_ship1, _sa_pub1 = _sa_solve(_sa_a, _sa_hw)
+    _sa_ship0, _sa_pub0 = _sa_solve(None, _sa_hw)
+    R.check(
+        f"the published trajectory simulates runs.received of the shipped plan; with no approach, the shipped "
+        f"plan ({'hot-water' if _sa_hw else 'space-only'} solve)",
+        _sa_pub1 is not None and _sa_pub0 is not None
+        and np.allclose(_sa_pub1, _sa_runs.received(_sa_ship1, 0.0, _sa_a, dt=0.25, p_max=3.0))
+        and not np.allclose(_sa_pub1, _sa_ship1) and np.allclose(_sa_pub0, _sa_ship0),
+        f"published {_sa_pub1} shipped {np.round(_sa_ship1[:8], 3)}",
+    )
+
+# 7, the coordinator's wiring: the pending prediction it files for the live
+# step carries the expected draw (the accuracy sample's predicted power, the
+# cost error, the defrost derate's delivered ratio), and the day-ahead promise
+# is costed on the received schedule. Null: the same coordinator with no
+# learned approach files the shipped total and the shipped schedule.
+def _sa_coord(runs_n, **config):
+    """A coordinator whose window learned ``runs_n`` series-D runs, scaled to its own floor."""
+    c = _t2_coord(**config)
+    params = getattr(c, "_ctx", c)._thermal_params
+    k = params.min_electrical_power / 0.53
+    t = _sa_feed(c._accuracy.draw, [(0.02, 0.0, 0.0)], params=params)
+    for _ in range(runs_n):
+        t = _sa_feed(c._accuracy.draw, [(d * k, a * k, h) for d, a, h in _sa_run()], t, params)
+    c._current_action = {**c._current_action, "power": params.min_electrical_power, "dhw_power": 0.0}
+    c._pending_prediction = None
+    with _sa_frozen_now(t):
+        c._record_accuracy()
+    return c, params.min_electrical_power
+
+
+import contextlib as _sa_cl  # noqa: E402
+from unittest import mock as _sa_mock  # noqa: E402
+
+
+@_sa_cl.contextmanager
+def _sa_frozen_now(epoch_s):
+    """The coordinator's clock at ``epoch_s``: the learned run's clock reads it."""
+    at = datetime.fromtimestamp(epoch_s, tz=timezone.utc)
+    with _sa_mock.patch("heatpump_optimizer.coordinator.dt_util.now", lambda *a: at):
+        yield
+
+
+_sa_c1, _sa_f = _sa_coord(5)
+_sa_c0, _ = _sa_coord(0)
+_sa_pend1, _sa_pend0 = _sa_c1._pending_prediction["power"], _sa_c0._pending_prediction["power"]
+
+
+def _sa_promise(c, f):
+    """The space schedule the coordinator files as the day-ahead promise of a plan with one run."""
+    seen = []
+    c._mode = "auto"
+    c._file_dhw_lead_predictions = lambda *a: None
+    c._accuracy.note_promise = lambda *a: seen.append(list(a[3]))
+    plan = _sa_NS(sensor_trajectory=lambda _two: [21.0] * 5, power_schedule=[0.0, f, 0.0, 0.0, 0.0],
+                           dhw_power_schedule=[0.0] * 5, prices=[0.1] * 5)
+    c._file_lead_predictions(plan, datetime(2026, 1, 10, tzinfo=timezone.utc))
+    return seen[0] if seen else None
+
+
+_sa_prom1, _sa_prom0 = _sa_promise(_sa_c1, _sa_f), _sa_promise(_sa_c0, _sa_f)
+R.check(
+    "the coordinator files the expected draw as the interval's predicted power, above the shipped floor on an "
+    "entry, and the promise costed on the received schedule; with no learned approach the shipped total and "
+    "the shipped schedule",
+    _sa_pend1 > 1.5 * _sa_f and _sa_pend0 == _sa_f
+    and _sa_prom1 is not None and _sa_prom1[1] > 1.5 * _sa_f and _sa_prom0 == [0.0, _sa_f, 0.0, 0.0, 0.0],
+    f"pending {_sa_pend1} null {_sa_pend0} floor {_sa_f} promise {_sa_prom1} null {_sa_prom0}",
+)
+
+# The COP fold of the interval the coordinator filed inside the approach reads
+# it as off its ask; the same fold with no learned approach does not.
+def _sa_cop(c):
+    c._measured_power = 1.2
+    return c._fold_measured_cop(c._accuracy.draw)
+
+
+_sa_cop1, _sa_cop0 = _sa_cop(_sa_c1), _sa_cop(_sa_c0)
+# A charge between two space runs moves the run clock (``fold``'s ``charged``):
+# the run after it is an entry, its sample inside the profile adds no window pair.
+_sa_ch = _sa_dr.DrawRange.from_dict(_sa_d.as_dict())
+_sa_cht = _sa_feed(_sa_ch, [(0.53, 0.53, 0.0)] * 2, _sa_t)
+_sa_dr.fold(_sa_ch, 1.4, (0.0, 1.0), _SA_P, frozen=False, distorted=False, defrost=False, span=_sa_dr.Span(_sa_cht, _sa_cht + 300, True))
+_sa_chn = len(_sa_ch.samples)
+_sa_feed(_sa_ch, [(1.25, 0.53, 0.0)], _sa_cht + 300)
+R.check(
+    "the COP fold refuses the interval filed inside the approach as off its ask, and not with none learned; a "
+    "charge between two space runs leaves the second an entry",
+    _sa_cop1 == _SA_OFF_ASK and _sa_cop0 != _SA_OFF_ASK and len(_sa_ch.samples) == _sa_chn
+    and _sa_ch.approach.entered_s == _sa_cht + 300,
+    f"cop {_sa_cop1} null {_sa_cop0} pairs {_sa_chn}->{len(_sa_ch.samples)}",
+)
+
+# The fabric learner's tracking gate reads the expected draw: an entry metered
+# at series D's first-step level is kept (the metered figure, less no hot
+# water); with no learned approach the same reading is tracking and skipped.
+def _sa_fabric(runs_n):
+    c, f = _sa_coord(runs_n, heat_pump_power_entity="sensor.hp_power")
+    c._measured_power = 1.2 * f / 0.53
+    return c._interval_space_power(), c._measured_power
+
+
+_sa_fab1, _sa_fab0 = _sa_fabric(5), _sa_fabric(0)
+R.check(
+    "the fabric interval of an entry inside the learned approach keeps its metered space figure; with none "
+    "learned the tracking gate skips it (spike s3)",
+    _sa_fab1[0] == _sa_fab1[1] and _sa_fab0[0] is None,
+    f"kept {_sa_fab1} null {_sa_fab0}",
+)
+
+# The plan's band stamp carries the learned entry energy, and the status
+# sensor's pump_min_power row shows it. Null: none learned stamps None.
+from heatpump_optimizer import sensor as _sa_sensor  # noqa: E402
+
+_SA_CAP = _sa_NS(plan_writes_power=lambda: False)
+_sa_band1 = _sa_dr.solve_band(_sa_d, _SA_P, _SA_CAP, _sa_t).as_dict()
+_sa_band0 = _sa_dr.solve_band(_sa_none, _SA_P, _SA_CAP, 1e9).as_dict()
+R.check(
+    "the solve band stamps the learned entry energy above the floor and pump_min_power shows it; none learned "
+    "stamps None",
+    abs(_sa_band1["approach_kwh"] - round(_sa_a.entry_kwh(0.53), 3)) < 1e-9 and _sa_band0["approach_kwh"] is None
+    and _sa_sensor._pump_min_power(_sa_band1)["pump_min_power"]["approach_kwh"] == _sa_band1["approach_kwh"],
+    f"{_sa_band1['approach_kwh']} null {_sa_band0['approach_kwh']}",
+)
+
+# Under a priced stop the received draw passes through the stop's share after
+# the approach (design note s6): delivered_space of runs.received, never the
+# reverse. Null: with no approach it is delivered_space of the shipped plan.
+from heatpump_optimizer import duty_legs as _sa_legs  # noqa: E402
+
+_sa_opt._approach = _sa_a
+_sa_hw = np.array([0.0, 0.0, 1.0, 0.0])
+_sa_av = np.array([1.0, 0.5, 1.0, 1.0])
+_sa_st = _sa_om._shipped_and_received(_sa_opt, _sa_plan, _sa_hw, _sa_av)[2]
+_sa_want = _sa_legs.delivered_space(_sa_runs.received(_sa_plan, _sa_hw, _sa_a, dt=0.25, p_max=3.0), _sa_hw, _sa_av, _sa_om._duty_floor(_sa_opt))
+_sa_opt._approach = None
+_sa_st0 = _sa_om._shipped_and_received(_sa_opt, _sa_plan, _sa_hw, _sa_av)[2]
+R.check(
+    "under a priced stop the received draw is the stop's share of the approach's draw; with no approach, of "
+    "the shipped plan",
+    np.array_equal(_sa_st, _sa_want) and not np.array_equal(_sa_st, _sa_st0)
+    and np.array_equal(_sa_st0, _sa_legs.delivered_space(_sa_plan, _sa_hw, _sa_av, _sa_om._duty_floor(_sa_opt))),
+    f"{_sa_st} vs {_sa_st0}",
+)
+
+# 5. The generator: with no approach the masks are the base's; with one, a
+# run out of a pause books the entry's energy, so the committed plan runs
+# fewer floor steps for the same relaxed energy.
+_sa_q, _sa_pr = np.full(12, 0.3), np.linspace(0.1, 0.3, 12)
+_sa_m0 = _sa_runs.candidates(_sa_q, _sa_pr, 0.53, 3.0, 0.05, dt=0.25)
+_sa_m00 = _sa_runs.candidates(_sa_q, _sa_pr, 0.53, 3.0, 0.05, dt=0.25, entry_kwh=0.0)
+_sa_m1 = _sa_runs.candidates(_sa_q, _sa_pr, 0.53, 3.0, 0.05, dt=0.25, entry_kwh=_sa_a.entry_kwh(0.53))
+# Rule: a mask's energy is its floor steps at 0.53 kW x 0.25 h plus the entry's
+# energy per run begun out of a pause; the commit ends within half a floor step
+# of the relaxed plan's 0.9 kWh. Null: the same rule on the base masks with no entry.
+def _sa_energy(mask, entry):
+    begun = int(np.sum(mask & ~np.r_[False, mask[:-1]]))
+    return float(mask.sum()) * 0.53 * 0.25 + begun * entry
+
+
+R.check(
+    "runs.commit: no entry energy leaves the masks equal; with the learned entry the tightest mask's floor "
+    "steps plus one entry per run out of a pause meet the relaxed energy within half a floor step",
+    all(np.array_equal(a, b) for a, b in zip(_sa_m0, _sa_m00)) and len(_sa_m0) == len(_sa_m00)
+    and abs(_sa_energy(_sa_m1[0], _sa_a.entry_kwh(0.53)) - 0.9) <= 0.53 * 0.25 / 2
+    and abs(_sa_energy(_sa_m0[0], 0.0) - 0.9) <= 0.53 * 0.25 / 2 and int(_sa_m1[0].sum()) < int(_sa_m0[0].sum()),
+    f"{[int(m.sum()) for m in _sa_m0]} vs {[int(m.sum()) for m in _sa_m1]}, "
+    f"energy {_sa_energy(_sa_m1[0], _sa_a.entry_kwh(0.53))}",
+)
+
+# 7. The axis: the expected draw at an entry is the received total, which the
+# accuracy sample pairs with the meter; the COP judge refuses the interval; an
+# entry sample inside the profile adds no pair to the window. Null: no profile.
+_sa_e = _sa_dr.DrawRange.from_dict(_sa_d.as_dict())
+_sa_exp = _sa_dr.expect(_sa_e, (0.53, 0.0), _SA_P, _sa_t, 0.25)
+_sa_in = _sa_dr.inside_approach(_sa_e)
+_sa_n = _sa_dr.DrawRange.from_dict(_sa_none.as_dict())
+_sa_exp0 = _sa_dr.expect(_sa_n, (0.53, 0.0), _SA_P, 1e9, 0.25)
+_sa_pairs = len(_sa_e.samples)
+_sa_feed(_sa_e, [(1.25, 0.53, 0.0)], _sa_t)
+R.check(
+    "the expected draw of an entry step is the received total and flags the step inside the approach; the "
+    "COP judge refuses it as off its ask; its sample adds no window pair. Null: no profile expects the "
+    "shipped total, flags nothing, and the judge reads the floor as before",
+    abs(_sa_exp - float(np.mean(_sa_a.entry[:3]))) < 1e-9 and _sa_in == _sa_exp
+    and _SaCop.judge_floor(_sa_exp, 1.2, _sa_NS(flow_lift_power_floor_kw=0.2, min_electrical_power=0.53, max_electrical_power=3.0), None, False, True) == _SA_OFF_ASK
+    and _SaCop.judge_floor(_sa_exp, 1.2, _sa_NS(flow_lift_power_floor_kw=0.2, min_electrical_power=0.53, max_electrical_power=3.0), None, False, False) is None
+    and len(_sa_e.samples) == _sa_pairs
+    and _sa_exp0 == 0.53 and _sa_dr.inside_approach(_sa_n) is None,
+    f"expected {_sa_exp} null {_sa_exp0} pairs {_sa_pairs}->{len(_sa_e.samples)}",
+)
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/finite_boundary.py b/tests/finite_boundary.py
index d06ac60c6d..a2ab8231a7 100644
--- a/tests/finite_boundary.py
+++ b/tests/finite_boundary.py
@@ -487,7 +487,7 @@ async def _save_room_history(coord):
         rec.period, _ = room_history.note(
             rec.history, rec.period, start + 30 * k,
             [RoomReading("climate.a", 20.5, 21.0, k % 2 == 0, "heat"), RoomReading("sensor.b", 19.5)],
-            room_history.House(-3.0, 28.0, 1.5, 2.0, 0.0))
+            room_history.House(-3.0, 28.0, 1.5, True))
     await room_record._persist(rec)
 
 
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 08152a9fb9..9973ef1fbe 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -75,6 +75,8 @@ valve_storage_smart_write  # baseline_cost LOWER (129.949 -> 129.251)
 wood_coil  # baseline_cost LOWER (144.781 -> 144.082)
 wood_two_tank  # baseline_cost LOWER (129.949 -> 129.251)
 wood_two_tank_smart_write  # baseline_cost LOWER (129.949 -> 129.251)
+cycling_cost  # R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed as runs: hot-water steps under the floor 14 -> 0, combined draw 11 -> 0, charges 9 -> 3, starts 4 -> 3, energy 40.97 -> 42.45 kWh, predicted_cost 32.07 -> 33.76 (up: the committed charges buy what the trickles under the floor did not), worst gap under the hot-water requirement 0.557 -> 0.439 K
+everything_on  # R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed as runs: hot-water steps under the floor 10 -> 0, combined draw 4 -> 0, charges 5 -> 3, starts 4 -> 3, energy 67.09 -> 66.48 kWh, predicted_cost 60.71 -> 60.39 (down), worst gap under the hot-water requirement 0.550 -> 0.438 K
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
@@ -129,13 +131,15 @@ wood_two_tank_smart_write  # baseline_cost LOWER (129.949 -> 129.251)
 # keys (prices/outdoor_temps/price_known/baseline_cost) still fail. Remove
 # when drift lanes are pinned or the polish improvement scale leaves
 # 5e-5-2e-2.
-# may-drift: cycling_cost -- #1207 keep-gate (2e-2 -> 2e-5), owner directive
+# (R11-OUTSIDE-HONEST-DHW-RUNS suspends cycling_cost's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) cycling_cost -- #1207 keep-gate (2e-2 -> 2e-5), owner directive
 # #1207 comment c1329fe (2026-09-20): the move's margin is inside the noise
 # band (objective rel -1.7666e-04, deterministic on one box),
 # runner-conditional for the same reason; judged keys still fail. Remove
 # when drift lanes are pinned or the polish improvement scale leaves
 # 5e-5-2e-2.
-# may-drift: everything_on -- #1207 keep-gate (2e-2 -> 2e-5), owner
+# (R11-OUTSIDE-HONEST-DHW-RUNS suspends everything_on's may-drift entry for its claim below; restore it,
+#  verbatim, when the stamp empties the list) everything_on -- #1207 keep-gate (2e-2 -> 2e-5), owner
 # directive #1207 comment c1329fe (2026-09-20): the move's margin is inside
 # the noise band (objective rel -5.2974e-03, deterministic on one box),
 # runner-conditional for the same reason; judged keys still fail. Remove
diff --git a/tests/guard_pins.py b/tests/guard_pins.py
index c8f7cbcb44..9aebc581a8 100644
--- a/tests/guard_pins.py
+++ b/tests/guard_pins.py
@@ -59,7 +59,7 @@ class _Learner(DhwProfileLearner):
             FakeHass(),
             "guard-pins",
             **_owned_params(ThermalParameters()),
-            frozen=lambda *_: None,
+            frozen=lambda *_, **_kw: None,
             heating_active=lambda: False,
             external_heat_active=lambda: False,
         )
@@ -255,7 +255,7 @@ def _draw_folded_only_without_external_heat() -> bool:
             FakeHass(),
             "guard-pins-draws",
             **_owned_params(params),
-            frozen=lambda *_: None,
+            frozen=lambda *_, **_kw: None,
             heating_active=lambda: False,
             external_heat_active=lambda external=external: external,
         )
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.32289174.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.32289174.json
index 52b2a109c9..c5ddcc60b4 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.32289174.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature BOOLOP 25dfd051",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature BOOLOP 32289174",
   "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if value is not None or self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if value is not None or self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.32289174.json
similarity index 68%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.32289174.json
index 4c2a483d6d..f174a69bd6 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.32289174.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF 25dfd051",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF 32289174",
   "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
+  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.955886dd.json
similarity index 52%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.955886dd.json
index 63ac676bff..dae47ab630 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.955886dd.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF cd19f403",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_internal_gains GUARD_OFF 955886dd",
   "killed_by": "tests/features.py",
-  "old": "        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.OCCUPANCY) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.d3d77cdd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.d3d77cdd.json
deleted file mode 100644
index 8627fe3928..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.d3d77cdd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop BOOLOP d3d77cdd",
-  "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None or not heat_energy.meter_of(self).counter):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.07efdbdf.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.07efdbdf.json
index 84f259b026..40d98a1a0e 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.07efdbdf.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF d3d77cdd",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 07efdbdf",
   "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, sample=learning_freeze.space_heat(heat_kw is not None or heat_energy.meter_of(self).counter), evidence=_space_evidence(self, self._commanded_split())):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.5a195a77.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.5a195a77.json
new file mode 100644
index 0000000000..87ff434cc0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.5a195a77.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF 5a195a77",
+  "killed_by": "tests/features.py",
+  "old": "        if heat_energy.ran_hot_water((m := heat_energy.meter_of(self)).attribution(split := (commanded_space, dhw_share))) or m.unplanned_charge(split):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.BOOLOP.a70a3ddd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.BOOLOP.a70a3ddd.json
deleted file mode 100644
index 1cef75bb3f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.BOOLOP.a70a3ddd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen BOOLOP a70a3ddd",
-  "killed_by": "tests/features.py",
-  "old": "        if room_air and self._vent_cusum.tripped:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if room_air or self._vent_cusum.tripped:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=31."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.4aa09690.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.4aa09690.json
deleted file mode 100644
index b5772501af..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.4aa09690.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF 4aa09690",
-  "killed_by": "tests/features.py",
-  "old": "        if health is not None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=29."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.cd0382df.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.cd0382df.json
deleted file mode 100644
index c99d0349c4..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.cd0382df.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF cd0382df",
-  "killed_by": "tests/features.py",
-  "old": "        if self._external_heat_active:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json
deleted file mode 100644
index c42b539e06..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF f728b131",
-  "killed_by": "tests/features.py",
-  "old": "        if signals.defrosting:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.fe0eb2bc.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.fe0eb2bc.json
deleted file mode 100644
index b00c678925..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.fe0eb2bc.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF fe0eb2bc",
-  "killed_by": "tests/structure.py",
-  "old": "        if boost.space_learning_frozen(self):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 82d1f47f20c0557f6898f843960eaa64bb20cbfd: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.2050bdf3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.2050bdf3.json
deleted file mode 100644
index b40cdb30c8..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.2050bdf3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen RETURN_DEL 2050bdf3",
-  "killed_by": "tests/features.py",
-  "old": "        return _tail_freeze(self)",
-  "reason": "Recorded by applying the mutant on this branch: RETURN_DEL (`pass`) makes HeatPumpOptimizerCoordinator._learning_frozen return None on an unmetered switch-plus-setpoint install, and tests/features.py's check that the house learner freezes there expects unmetered_power. `mutation_table.py --pin-killed` records no verdict on this machine because tests/features.py's baseline is red on R9-F2.1 P3, the same pair origin/main fails."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.937e866c.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.937e866c.json
new file mode 100644
index 0000000000..6cbe18fb68
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.RETURN_DEL.937e866c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen RETURN_DEL 937e866c",
+  "killed_by": "tests/features.py",
+  "old": "        return learning_freeze.reason(_freeze_facts(self), keys, sample, evidence)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=77."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
deleted file mode 100644
index 55ee71d138..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.fe5030a3.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF fe5030a3",
-  "killed_by": "tests/features.py",
-  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending[\"split\"])):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_quiet_comfort_period.GUARD_OFF.955886dd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_quiet_comfort_period.GUARD_OFF.955886dd.json
new file mode 100644
index 0000000000..645e213a8c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_quiet_comfort_period.GUARD_OFF.955886dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_quiet_comfort_period GUARD_OFF 955886dd",
+  "killed_by": "tests/features.py",
+  "old": "        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.OCCUPANCY) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._settle_defrost.GUARD_OFF.b00f0008.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._settle_defrost.GUARD_OFF.b00f0008.json
deleted file mode 100644
index 680723786f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._settle_defrost.GUARD_OFF.b00f0008.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._settle_defrost GUARD_OFF b00f0008",
-  "killed_by": "tests/features.py",
-  "old": "        if ratio is not None and in_frost_band(outdoor) and not _cop_fold_blocked(self):",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.2de48876.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.2de48876.json
deleted file mode 100644
index e51e155a19..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.2de48876.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._track_curve_comfort GUARD_OFF 2de48876",
-  "killed_by": "tests/features.py",
-  "old": "        if (self._learning_frozen(CONF_INDOOR_TEMP_ENTITY) or learner_room_unread(ctx._config)) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.442286fa.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.442286fa.json
deleted file mode 100644
index f56ab545b2..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._track_curve_comfort.GUARD_OFF.442286fa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._track_curve_comfort GUARD_OFF 442286fa",
-  "killed_by": "tests/features.py",
-  "old": "        if self._away_state.active or self._away_state.recovery_active:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.23b8d2ba.json
similarity index 61%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
rename to tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.23b8d2ba.json
index d4aaf40705..c7830f4293 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.23b8d2ba.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF a70a3ddd",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_learn_heat_span GUARD_OFF 23b8d2ba",
   "killed_by": "tests/features.py",
-  "old": "        if room_air and self._vent_cusum.tripped:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+  "old": "        if close.house or close.lower:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.cee88ab2.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
rename to tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.cee88ab2.json
index 7e0808e417..a3f2cbf897 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_learn_heat_span.GUARD_OFF.cee88ab2.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c294c9b7",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_learn_heat_span GUARD_OFF cee88ab2",
   "killed_by": "tests/features.py",
-  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
+  "old": "        if close.cop:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.06010c5d.json b/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.06010c5d.json
deleted file mode 100644
index 8f7c08f96e..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_fold_flow_lift.GUARD_OFF.06010c5d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_fold_flow_lift GUARD_OFF 06010c5d",
-  "killed_by": "tests/features.py",
-  "old": "    if coord._learning_frozen(CONF_OUTDOOR_TEMP_ENTITY) is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_space_evidence.RETURN_DEL.051d6794.json b/tests/mutation_ledger/killed_by/coordinator.py/_space_evidence.RETURN_DEL.051d6794.json
new file mode 100644
index 0000000000..c17416afad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_space_evidence.RETURN_DEL.051d6794.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_space_evidence RETURN_DEL 051d6794",
+  "killed_by": "tests/features.py",
+  "old": "    return learning_freeze.Evidence(unplanned_charge=heat_energy.meter_of(coord).unplanned_charge(split))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.805aff0a.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.805aff0a.json
new file mode 100644
index 0000000000..4e1fcd591b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.805aff0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST 805aff0a",
+  "killed_by": "tests/features.py",
+  "old": "_STORE_MARGIN_K = 0.02",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_STORE_MARGIN_K = 0.04`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.819025de.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.819025de.json
new file mode 100644
index 0000000000..8f100f698d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.819025de.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST 819025de",
+  "killed_by": "tests/features.py",
+  "old": "_COP_KNOT_K = 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_COP_KNOT_K = 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.c95e30be.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.c95e30be.json
index 6778cf2e61..9b96ba4842 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.c95e30be.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:<module> CONST c95e30be",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST c95e30be",
   "killed_by": "tests/block_duty.py",
   "old": "STARTABLE_ROUNDS = 8",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`STARTABLE_ROUNDS = 16`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.ccd84963.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.ccd84963.json
new file mode 100644
index 0000000000..07357b167d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.ccd84963.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST ccd84963",
+  "killed_by": "tests/features.py",
+  "old": "SHORTFALL_K = 0.05",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SHORTFALL_K = 0.1`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.dce4c8cc.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.dce4c8cc.json
new file mode 100644
index 0000000000..5741e3d53f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.CONST.dce4c8cc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> CONST dce4c8cc",
+  "killed_by": "tests/features.py",
+  "old": "_STORE_GRID_K = 0.25",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_STORE_GRID_K = 0.5`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/@module.GUARD_OFF.e1433e05.json b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.GUARD_OFF.e1433e05.json
new file mode 100644
index 0000000000..3e816db2b9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/@module.GUARD_OFF.e1433e05.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:<module> GUARD_OFF e1433e05",
+  "killed_by": "tests/structure.py",
+  "old": "if TYPE_CHECKING:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.073c5b69.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.073c5b69.json
new file mode 100644
index 0000000000..59dfea130e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.073c5b69.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.__init__ CLAMP_DROP 073c5b69",
+  "killed_by": "tests/features.py",
+  "old": "            self.lo, float(np.ceil(max(self.initial, float(np.max(self.ceilings))))) + 2.0 * _COP_KNOT_K, _COP_KNOT_K)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`self.lo, float(np.ceil((self.initial))) + 2.0 * _COP_KNOT_K, _COP_KNOT_K)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.e3d37ae9.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.e3d37ae9.json
new file mode 100644
index 0000000000..1bb9441766
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.__init__.CLAMP_DROP.e3d37ae9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.__init__ CLAMP_DROP e3d37ae9",
+  "killed_by": "tests/features.py",
+  "old": "        self.lo = float(np.floor(min(self.initial, float(np.min(self.floors))))) - _COP_KNOT_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`self.lo = float(np.floor((self.initial))) - _COP_KNOT_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.CMP_BOUND.64eeed1c.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.CMP_BOUND.64eeed1c.json
new file mode 100644
index 0000000000..17874f309e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.CMP_BOUND.64eeed1c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions CMP_BOUND 64eeed1c",
+  "killed_by": "tests/features.py",
+  "old": "        ran, paused = runs.tie_break(bool(self.asked[k] > 0.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ran, paused = runs.tie_break(bool(self.asked[k] >= 0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.RETURN_DEL.43f64127.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.RETURN_DEL.43f64127.json
new file mode 100644
index 0000000000..7e46c9e62b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._actions.RETURN_DEL.43f64127.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions RETURN_DEL 43f64127",
+  "killed_by": "tests/features.py",
+  "old": "        return [*(at(level) for level in self.levels), fill], pauses",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._rise.RETURN_DEL.ad4cb87b.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._rise.RETURN_DEL.ad4cb87b.json
new file mode 100644
index 0000000000..bb38f95872
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram._rise.RETURN_DEL.ad4cb87b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._rise RETURN_DEL ad4cb87b",
+  "killed_by": "tests/features.py",
+  "old": "        return heat * self.ctx.dt / self.ctx.c_dhw",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.268a674c.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.268a674c.json
new file mode 100644
index 0000000000..50c58a16d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.268a674c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.accepted GUARD_OFF 268a674c",
+  "killed_by": "tests/features.py",
+  "old": "            if fitted is None or isinstance(fitted, np.ndarray):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.497d643e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.497d643e.json
new file mode 100644
index 0000000000..d9be76b3be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.GUARD_OFF.497d643e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.accepted GUARD_OFF 497d643e",
+  "killed_by": "tests/features.py",
+  "old": "            if fitted[0] != \"start\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.RETURN_DEL.d7923b87.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.RETURN_DEL.d7923b87.json
new file mode 100644
index 0000000000..2c777d9a35
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.accepted.RETURN_DEL.d7923b87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.accepted RETURN_DEL d7923b87",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "        return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.BOOLOP.b30ce7fa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.BOOLOP.b30ce7fa.json
new file mode 100644
index 0000000000..9cb8acdc0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.BOOLOP.b30ce7fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan BOOLOP b30ce7fa",
+  "killed_by": "tests/features.py",
+  "old": "                out[k] = self.levels[action[k]] if mask[k] and action[k] < len(self.levels) else float(",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`out[k] = self.levels[action[k]] if mask[k] or action[k] < len(self.levels) else float(`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.CMP_BOUND.b30ce7fa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.CMP_BOUND.b30ce7fa.json
new file mode 100644
index 0000000000..1c7dde9ba5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.CMP_BOUND.b30ce7fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan CMP_BOUND b30ce7fa",
+  "killed_by": "tests/features.py",
+  "old": "                out[k] = self.levels[action[k]] if mask[k] and action[k] < len(self.levels) else float(",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`out[k] = self.levels[action[k]] if mask[k] and action[k] <= len(self.levels) else float(`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.2f0256bb.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.2f0256bb.json
new file mode 100644
index 0000000000..3ae8298cc0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.2f0256bb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan GUARD_OFF 2f0256bb",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.isfinite(cost).any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.6a1d1d58.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.6a1d1d58.json
new file mode 100644
index 0000000000..28dd6926f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.GUARD_OFF.6a1d1d58.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan GUARD_OFF 6a1d1d58",
+  "killed_by": "tests/features.py",
+  "old": "            if mask[k] or action[k]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.RETURN_DEL.7edb83fa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.RETURN_DEL.7edb83fa.json
new file mode 100644
index 0000000000..967df2b040
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.RETURN_DEL.7edb83fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan RETURN_DEL 7edb83fa",
+  "killed_by": "tests/features.py",
+  "old": "        return out",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.3a89afa4.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.3a89afa4.json
new file mode 100644
index 0000000000..50db5344b1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.3a89afa4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place CMP_BOUND 3a89afa4",
+  "killed_by": "tests/features.py",
+  "old": "                    inside &= t <= self.ceilings[k] - _STORE_MARGIN_K + 1e-9",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`inside &= t < self.ceilings[k] - _STORE_MARGIN_K + 1e-9`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.GUARD_OFF.11ab4ed8.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.GUARD_OFF.11ab4ed8.json
new file mode 100644
index 0000000000..0bc1ea8e53
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.GUARD_OFF.11ab4ed8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place GUARD_OFF 11ab4ed8",
+  "killed_by": "tests/features.py",
+  "old": "                if charged:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.RETURN_DEL.ea9b6ec1.json b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.RETURN_DEL.ea9b6ec1.json
new file mode 100644
index 0000000000..05b17b52ae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/_StoreProgram.plan.place.RETURN_DEL.ea9b6ec1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place RETURN_DEL ea9b6ec1",
+  "killed_by": "tests/features.py",
+  "old": "                return np.clip(j, 0, width - 1), np.where(inside, 0.0, np.inf)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.CMP_BOUND.767963ce.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.CMP_BOUND.767963ce.json
new file mode 100644
index 0000000000..06b51864d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.CMP_BOUND.767963ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal CMP_BOUND 767963ce",
+  "killed_by": "tests/features.py",
+  "old": "    short = np.flatnonzero(temps_of(candidate)[1 : candidate.size + 1] < held - SHORTFALL_K)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`short = np.flatnonzero(temps_of(candidate)[1 : candidate.size + 1] <= held - SHORTFALL_K)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
new file mode 100644
index 0000000000..d942d4aade
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal GUARD_OFF 4763baed",
+  "killed_by": "tests/features.py",
+  "old": "    if start_below is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.c9743976.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.c9743976.json
new file mode 100644
index 0000000000..da0bce1db4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.c9743976.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal GUARD_OFF c9743976",
+  "killed_by": "tests/features.py",
+  "old": "        if lost.size:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.RETURN_DEL.6f93183b.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.RETURN_DEL.6f93183b.json
new file mode 100644
index 0000000000..fa2c65331f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.RETURN_DEL.6f93183b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal RETURN_DEL 6f93183b",
+  "killed_by": "tests/features.py",
+  "old": "    return (\"floor\", int(short[0])) if short.size else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.CMP_BOUND.bbc78afe.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.CMP_BOUND.bbc78afe.json
new file mode 100644
index 0000000000..53382068cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.CMP_BOUND.bbc78afe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charges_run CMP_BOUND bbc78afe",
+  "killed_by": "tests/features.py",
+  "old": "    on, low = plan > 0.0, (plan > 0.0) & (plan < floor - 1e-9)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on, low = plan >= 0.0, (plan > 0.0) & (plan < floor - 1e-9)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.RETURN_DEL.70fe77b1.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.RETURN_DEL.70fe77b1.json
new file mode 100644
index 0000000000..1b16e77bcf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charges_run.RETURN_DEL.70fe77b1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charges_run RETURN_DEL 70fe77b1",
+  "killed_by": "tests/features.py",
+  "old": "    return not bool(np.any(low & ~(ends & tails)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.BOOLOP.a48fe321.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.BOOLOP.a48fe321.json
new file mode 100644
index 0000000000..30e60ef683
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.BOOLOP.a48fe321.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges BOOLOP a48fe321",
+  "killed_by": "tests/features.py",
+  "old": "    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not charge.start_cost > 0 or charges_run(plan, floor, not charge.clamped):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.0f54c97d.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.0f54c97d.json
new file mode 100644
index 0000000000..5ab6a6c153
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.0f54c97d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CLAMP_DROP 0f54c97d",
+  "killed_by": "tests/features.py",
+  "old": "    held = np.minimum(limits[0], walk[1:])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`held = (limits[0])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.1e8af2ea.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.1e8af2ea.json
new file mode 100644
index 0000000000..b3710d3bdd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.1e8af2ea.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CLAMP_DROP 1e8af2ea",
+  "killed_by": "tests/features.py",
+  "old": "    program = _StoreProgram(planner, ctx, plan, tank, (held, np.maximum(limits[1], walk[1:])), forced_off, space)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`program = _StoreProgram(planner, ctx, plan, tank, (held, (limits[1])), forced_off, space)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.92461313.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.92461313.json
new file mode 100644
index 0000000000..d0f380f174
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CLAMP_DROP.92461313.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CLAMP_DROP 92461313",
+  "killed_by": "tests/features.py",
+  "old": "    space = np.zeros(ctx.n_steps) if space_demand is None else np.clip(space_demand, 0.0, None)",
+  "reason": "Killed by the check \"a space plan under zero commits as no space plan: ...\" in tests/features.py's R11-OUTSIDE-HONEST-DHW-RUNS block: CLAMP_DROP (`(space_demand)`) lets a space step of -10 kW under the program's dear early charge hide that charge's start, so the early charge ships; features_block.py over the block went from 1 failed (the block-mode baseline) to 2 failed with the mutant, the added failure being that check."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.a48fe321.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.a48fe321.json
new file mode 100644
index 0000000000..8393bcc816
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.a48fe321.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CMP_BOUND a48fe321",
+  "killed_by": "tests/features.py",
+  "old": "    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not charge.start_cost >= 0 and charges_run(plan, floor, not charge.clamped):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.e2cc9d77.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.e2cc9d77.json
new file mode 100644
index 0000000000..8e9e34a0c9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.CMP_BOUND.e2cc9d77.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CMP_BOUND e2cc9d77",
+  "killed_by": "tests/features.py",
+  "old": "    if charge is None or ctx.p_dhw_max < floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if charge is None or ctx.p_dhw_max <= floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 3 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.a48fe321.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.a48fe321.json
new file mode 100644
index 0000000000..d160762a4f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.a48fe321.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges GUARD_OFF a48fe321",
+  "killed_by": "tests/features.py",
+  "old": "    if not charge.start_cost > 0 and charges_run(plan, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.e2cc9d77.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.e2cc9d77.json
new file mode 100644
index 0000000000..c02bd55dec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.GUARD_OFF.e2cc9d77.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges GUARD_OFF e2cc9d77",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if charge is None or ctx.p_dhw_max < floor or ctx.c_dhw <= 0.0 or not np.any(plan > 0.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.RETURN_DEL.6881576e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.RETURN_DEL.6881576e.json
new file mode 100644
index 0000000000..4c6cc3d5b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.RETURN_DEL.6881576e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges RETURN_DEL 6881576e",
+  "killed_by": "tests/features.py",
+  "old": "    return min((c for c in proposed if isinstance(c, np.ndarray)), key=cost, default=plan)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.cost.RETURN_DEL.066c6846.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.cost.RETURN_DEL.066c6846.json
new file mode 100644
index 0000000000..fc5dfc528b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.cost.RETURN_DEL.066c6846.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.cost RETURN_DEL 066c6846",
+  "killed_by": "tests/features.py",
+  "old": "        return float(np.sum(ctx.prices * candidate) * ctx.dt) + charge.start_cost * starts",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.3b32803b.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.3b32803b.json
new file mode 100644
index 0000000000..7272457fc3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.3b32803b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits GUARD_OFF 3b32803b",
+  "killed_by": "tests/features.py",
+  "old": "        if not charges_run(candidate, floor, not charge.clamped):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.e8d52e79.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.e8d52e79.json
new file mode 100644
index 0000000000..00b0b5d737
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.GUARD_OFF.e8d52e79.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits GUARD_OFF e8d52e79",
+  "killed_by": "tests/features.py",
+  "old": "        if candidate is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.387565ce.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.387565ce.json
new file mode 100644
index 0000000000..bec19e26de
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.387565ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits RETURN_DEL 387565ce",
+  "killed_by": "tests/features.py",
+  "old": "        return charge_refusal(candidate, start_below, temps_of, held) or candidate",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.BOOLOP.6c096d09.json
similarity index 84%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.BOOLOP.6c096d09.json
index ab09d83fe4..3211a8a7a0 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.BOOLOP.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps BOOLOP 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps BOOLOP 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if cycle_step is not None or 0 <= cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.CMP_BOUND.6c096d09.json
similarity index 86%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.CMP_BOUND.6c096d09.json
index d702531e8c..4ffa0b64f0 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.CMP_BOUND.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps CMP_BOUND 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps CMP_BOUND 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if cycle_step is not None and 0 < cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.6c096d09.json
similarity index 82%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.6c096d09.json
index 3a532a0795..dd20b43472 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps GUARD_OFF 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
index a26a52429d..28bd8101ab 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF cccafcc1",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps GUARD_OFF cccafcc1",
   "killed_by": "tests/manual_plan.py",
   "old": "    if everyday is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.RETURN_DEL.87df096e.json
similarity index 79%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.RETURN_DEL.87df096e.json
index 5ed862def7..3edce0523d 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/dhw_start_temps.RETURN_DEL.87df096e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps RETURN_DEL 87df096e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:dhw_start_temps RETURN_DEL 87df096e",
   "killed_by": "tests/block_duty.py",
   "old": "    return start",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.064a19f6.json
similarity index 83%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.064a19f6.json
index a4e8b3a54d..5b4f6f6c40 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable CMP_BOUND 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if temps_of(plan)[i] > start_below[i]:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.b56fd264.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.b56fd264.json
index 3d43b90b16..a9eeae612b 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.CMP_BOUND.b56fd264.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND b56fd264",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable CMP_BOUND b56fd264",
   "killed_by": "tests/block_duty.py",
   "old": "    on = plan > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = plan >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=8."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.GUARD_OFF.064a19f6.json
similarity index 81%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.GUARD_OFF.064a19f6.json
index f68b057eb8..68a1bf5ab1 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.GUARD_OFF.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable GUARD_OFF 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable GUARD_OFF 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.RETURN_DEL.c913c48e.json
similarity index 79%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.RETURN_DEL.c913c48e.json
index bba12cc624..718843a931 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/drop_unstartable.RETURN_DEL.c913c48e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable RETURN_DEL c913c48e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:drop_unstartable RETURN_DEL c913c48e",
   "killed_by": "tests/block_duty.py",
   "old": "    return plan",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=9."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.99a579b8.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.99a579b8.json
index a9e44056f4..8973d5a037 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:place_startable GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.e4a2bfaa.json
similarity index 81%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.e4a2bfaa.json
index 0c4ceb6b59..43d58de22e 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.GUARD_OFF.e4a2bfaa.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF e4a2bfaa",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:place_startable GUARD_OFF e4a2bfaa",
   "killed_by": "tests/block_duty.py",
   "old": "        if np.array_equal(fixed, plan):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.RETURN_DEL.68208daf.json
similarity index 82%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.RETURN_DEL.68208daf.json
index 9e7ca6a749..a5089f7349 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/place_startable.RETURN_DEL.68208daf.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable RETURN_DEL 68208daf",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:place_startable RETURN_DEL 68208daf",
   "killed_by": "tests/block_duty.py",
   "old": "    return drop_unstartable(plan, start_below, temps_of)",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=5."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.BOOLOP.3d3ec5bc.json
similarity index 82%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.BOOLOP.3d3ec5bc.json
index 6443097405..e4836e1976 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.BOOLOP.3d3ec5bc.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps BOOLOP 3d3ec5bc",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps BOOLOP 3d3ec5bc",
   "killed_by": "tests/block_duty.py",
   "old": "        under_way = bool(on[i] and ok[i])",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`under_way = bool(on[i] or ok[i])`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.1edfe326.json
similarity index 83%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.1edfe326.json
index f11e540a53..f83ef0622d 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.1edfe326.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 1edfe326",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps CMP_BOUND 1edfe326",
   "killed_by": "tests/block_duty.py",
   "old": "    on = np.asarray(plan, dtype=float) > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = np.asarray(plan, dtype=float) >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.6e3a088f.json
similarity index 86%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.6e3a088f.json
index 94c3474d95..13bd54cc1e 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.CMP_BOUND.6e3a088f.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 6e3a088f",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps CMP_BOUND 6e3a088f",
   "killed_by": "tests/block_duty.py",
   "old": "    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] <= start_below[: on.size]`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.GUARD_OFF.99a579b8.json
similarity index 80%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.GUARD_OFF.99a579b8.json
index 26c5b81261..d4d39effe3 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.RETURN_DEL.82bc35de.json
similarity index 79%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.RETURN_DEL.82bc35de.json
index 1fc93528fd..737d23018a 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/startable_steps.RETURN_DEL.82bc35de.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps RETURN_DEL 82bc35de",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:startable_steps RETURN_DEL 82bc35de",
   "killed_by": "tests/block_duty.py",
   "old": "    return ok",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=4."
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.CMP_BOUND.2515841c.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.CMP_BOUND.2515841c.json
new file mode 100644
index 0000000000..da25c5c06f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.CMP_BOUND.2515841c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges CMP_BOUND 2515841c",
+  "killed_by": "tests/features.py",
+  "old": "    on, kept = np.r_[False, plan > 0.0, False], mask.copy()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on, kept = np.r_[False, plan >= 0.0, False], mask.copy()`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/arm_refusal.GUARD_OFF.2569c66f.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
similarity index 56%
rename from tests/mutation_ledger/killed_by/sysid.py/arm_refusal.GUARD_OFF.2569c66f.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
index 2b716d8e37..82d3290dba 100644
--- a/tests/mutation_ledger/killed_by/sysid.py/arm_refusal.GUARD_OFF.2569c66f.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:arm_refusal GUARD_OFF 2569c66f",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges GUARD_OFF cbabd675",
   "killed_by": "tests/features.py",
-  "old": "    if not ident.config.enabled:",
+  "old": "    if charge_runs is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.RETURN_DEL.d78a0d21.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.RETURN_DEL.d78a0d21.json
index 2cd18bdda4..1596ff6123 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.RETURN_DEL.e82fb19a.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.RETURN_DEL.d78a0d21.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance RETURN_DEL e82fb19a",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges RETURN_DEL d78a0d21",
   "killed_by": "tests/features.py",
-  "old": "    return new_cost, new_bal, back",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "old": "    return kept",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/dhw_learning.py/DhwProfileLearner.async_learn_dynamics.GUARD_OFF.efe52220.json b/tests/mutation_ledger/killed_by/dhw_learning.py/DhwProfileLearner.async_learn_dynamics.GUARD_OFF.efe52220.json
new file mode 100644
index 0000000000..3c0404c5d6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_learning.py/DhwProfileLearner.async_learn_dynamics.GUARD_OFF.efe52220.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_learning.py:DhwProfileLearner.async_learn_dynamics GUARD_OFF efe52220",
+  "killed_by": "tests/features.py",
+  "old": "        if occupied:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.cedbad00.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.cedbad00.json
deleted file mode 100644
index 6fff52f6b9..0000000000
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.cedbad00.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_shortfall CMP_BOUND cedbad00",
-  "killed_by": "tests/features.py",
-  "old": "        for i in np.where(gaps > 0.05)[0]:",
-  "reason": "Recorded by hand for R9-EG-A2 (#1874) on an export of the branch, 2026-10-03, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS): a kill is a red run naming a FAIL line or traceback the unmutated baseline does not. CMP_BOUND (`for i in np.where(gaps >= 0.05)[0]:`) took tests/features.py from rc=1 failed=2 to rc=1 failed=3, newly failing ['EG-A2 a DHW breach is a shortfall of MORE than 0.05 K: exactly 0.05 is met, 0.06 is the first breach']."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.f38f29c7.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.f38f29c7.json
new file mode 100644
index 0000000000..eec23a8832
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_shortfall.CMP_BOUND.f38f29c7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_shortfall CMP_BOUND f38f29c7",
+  "killed_by": "tests/features.py",
+  "old": "        for i in np.where(gaps > SHORTFALL_K)[0]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`for i in np.where(gaps >= SHORTFALL_K)[0]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.coast.RETURN_DEL.32c6aaf4.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.coast.RETURN_DEL.32c6aaf4.json
new file mode 100644
index 0000000000..204d8abc3f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_DhwPlanContext.coast.RETURN_DEL.32c6aaf4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_DhwPlanContext.coast RETURN_DEL 32c6aaf4",
+  "killed_by": "tests/block_duty.py",
+  "old": "        return decay * temp - (float(draw_rates[i]) - _exo_at(self.tank_exo_kw, i)) * self.dt / self.c_dhw + gain",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.BOOLOP.58d599ba.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.BOOLOP.58d599ba.json
deleted file mode 100644
index 3d4225c7d7..0000000000
--- a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.BOOLOP.58d599ba.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.from_dict BOOLOP 58d599ba",
-  "killed_by": "tests/features.py",
-  "old": "        if not (np.isfinite(lo) and np.isfinite(hi)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: BOOLOP (`if not (np.isfinite(lo) or np.isfinite(hi)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.GUARD_OFF.58d599ba.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.GUARD_OFF.58d599ba.json
deleted file mode 100644
index 8302dfb391..0000000000
--- a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.from_dict.GUARD_OFF.58d599ba.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.from_dict GUARD_OFF 58d599ba",
-  "killed_by": "tests/features.py",
-  "old": "        if not (np.isfinite(lo) and np.isfinite(hi)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against b2b6acd64cde652676a568e93c05f021571ebe5e: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.BOOLOP.dc29709b.json
similarity index 92%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.BOOLOP.dc29709b.json
index 704b09b3cd..f05a55d7e0 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.BOOLOP.dc29709b.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold BOOLOP dc29709b",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window BOOLOP dc29709b",
   "killed_by": "tests/features.py",
   "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if experiment_s is not None or draw.takes_ceiling(drawn_kw, command):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.8c264f30.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.8c264f30.json
similarity index 93%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.8c264f30.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.8c264f30.json
index d58eecf874..9b40a866dc 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.8c264f30.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.8c264f30.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF 8c264f30",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF 8c264f30",
   "killed_by": "tests/structure.py",
   "old": "    if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c <= command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):",
   "reason": "Recorded by `mutation_table.py --pin-killed` against d5cd003111277faa3f2abd7fbe6c9157d2e48ed7: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
new file mode 100644
index 0000000000..8271995631
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF d042d302",
+  "killed_by": "tests/features.py",
+  "old": "        if not ceiling_frozen:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.dc29709b.json
similarity index 90%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.dc29709b.json
index 33b15211f0..cb3dc2da4f 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.dc29709b.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF dc29709b",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF dc29709b",
   "killed_by": "tests/structure.py",
   "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.CMP_BOUND.9058b534.json b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.CMP_BOUND.9058b534.json
new file mode 100644
index 0000000000..dfae4b6695
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.CMP_BOUND.9058b534.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:at_running_floor CMP_BOUND 9058b534",
+  "killed_by": "tests/features.py",
+  "old": "    return drawn_kw is not None and floor > 0.0 and drawn_kw <= (1.0 + AGREE_TOLERANCE) * floor",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return drawn_kw is not None and floor >= 0.0 and drawn_kw <= (1.0 + AGREE_TOLERANCE) * floor`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.RETURN_DEL.9058b534.json b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.RETURN_DEL.9058b534.json
new file mode 100644
index 0000000000..e80087f479
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/at_running_floor.RETURN_DEL.9058b534.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:at_running_floor RETURN_DEL 9058b534",
+  "killed_by": "tests/features.py",
+  "old": "    return drawn_kw is not None and floor > 0.0 and drawn_kw <= (1.0 + AGREE_TOLERANCE) * floor",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/@module.CONST.ba3007dd.json b/tests/mutation_ledger/killed_by/heat_energy.py/@module.CONST.ba3007dd.json
new file mode 100644
index 0000000000..0ae9bb0b27
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/@module.CONST.ba3007dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:<module> CONST ba3007dd",
+  "killed_by": "tests/features.py",
+  "old": "UNPLANNED_CHARGE_RISE_K = 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`UNPLANNED_CHARGE_RISE_K = 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.GUARD_OFF.c6189501.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.GUARD_OFF.c6189501.json
new file mode 100644
index 0000000000..ef5a2dd80c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.GUARD_OFF.c6189501.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.booked_dhw_share GUARD_OFF c6189501",
+  "killed_by": "tests/features.py",
+  "old": "        if self.unplanned_charge(plan_split):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.RETURN_DEL.c46109ce.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.RETURN_DEL.c46109ce.json
new file mode 100644
index 0000000000..38cd14370c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.booked_dhw_share.RETURN_DEL.c46109ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.booked_dhw_share RETURN_DEL c46109ce",
+  "killed_by": "tests/features.py",
+  "old": "        return dhw_share(self.attribution(plan_split))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.BOOLOP.c90a604e.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.BOOLOP.c90a604e.json
new file mode 100644
index 0000000000..1a8d9bd550
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.BOOLOP.c90a604e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone BOOLOP c90a604e",
+  "killed_by": "tests/features.py",
+  "old": "        return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return a.dhw <= 0.0 < a.space or not self.unplanned_charge(plan_split)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.CMP_BOUND.c90a604e.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.CMP_BOUND.c90a604e.json
new file mode 100644
index 0000000000..efe36edb46
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.CMP_BOUND.c90a604e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone CMP_BOUND c90a604e",
+  "killed_by": "tests/features.py",
+  "old": "        return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return a.dhw < 0.0 < a.space and not self.unplanned_charge(plan_split)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.GUARD_OFF.0f67a887.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.GUARD_OFF.0f67a887.json
new file mode 100644
index 0000000000..a0761738fb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.GUARD_OFF.0f67a887.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone GUARD_OFF 0f67a887",
+  "killed_by": "tests/features.py",
+  "old": "        if plan_split is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.RETURN_DEL.c90a604e.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.RETURN_DEL.c90a604e.json
new file mode 100644
index 0000000000..30c30b8156
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.served_space_alone.RETURN_DEL.c90a604e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.served_space_alone RETURN_DEL c90a604e",
+  "killed_by": "tests/features.py",
+  "old": "        return a.dhw <= 0.0 < a.space and not self.unplanned_charge(plan_split)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.settle.GUARD_OFF.ded6790b.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.settle.GUARD_OFF.ded6790b.json
new file mode 100644
index 0000000000..7893ab01df
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.settle.GUARD_OFF.ded6790b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.settle GUARD_OFF ded6790b",
+  "killed_by": "tests/features.py",
+  "old": "        if self._opened:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.unplanned_charge.RETURN_DEL.5fd3d065.json b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.unplanned_charge.RETURN_DEL.5fd3d065.json
new file mode 100644
index 0000000000..c7171a8e8a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/HeatEnergyMeter.unplanned_charge.RETURN_DEL.5fd3d065.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:HeatEnergyMeter.unplanned_charge RETURN_DEL 5fd3d065",
+  "killed_by": "tests/features.py",
+  "old": "        return unplanned_charge(self.attribution(plan_split), rise)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.6ceb3cee.json b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.6ceb3cee.json
new file mode 100644
index 0000000000..24b321b1af
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.6ceb3cee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:unplanned_charge CMP_BOUND 6ceb3cee",
+  "killed_by": "tests/features.py",
+  "old": "        not a.observed and a.dhw <= 0.0 < a.space",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`not a.observed and a.dhw < 0.0 < a.space`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.8c76c4b6.json b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.8c76c4b6.json
new file mode 100644
index 0000000000..92e703c13a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_energy.py/unplanned_charge.CMP_BOUND.8c76c4b6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_energy.py:unplanned_charge CMP_BOUND 8c76c4b6",
+  "killed_by": "tests/features.py",
+  "old": "        and tank_rise_k is not None and tank_rise_k > UNPLANNED_CHARGE_RISE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and tank_rise_k is not None and tank_rise_k >= UNPLANNED_CHARGE_RISE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.BOOLOP.5944a80c.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.BOOLOP.5944a80c.json
new file mode 100644
index 0000000000..f8c38b2557
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.BOOLOP.5944a80c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared BOOLOP 5944a80c",
+  "killed_by": "tests/features.py",
+  "old": "    if sample in _ROOM_AIR_KINDS and facts.ventilation:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if sample in _ROOM_AIR_KINDS or facts.ventilation:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=22."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.093742d2.json
similarity index 51%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
rename to tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.093742d2.json
index bd324872f3..5f6b906736 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.093742d2.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF ac9b3721",
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 093742d2",
   "killed_by": "tests/features.py",
-  "old": "        if experiment:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "old": "        if problem is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=32."
 }
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.131f698a.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.131f698a.json
new file mode 100644
index 0000000000..111b69b737
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.131f698a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 131f698a",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.defrosting:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.20cd6c12.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.20cd6c12.json
new file mode 100644
index 0000000000..0a67368ddd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.20cd6c12.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 20cd6c12",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.boost is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.5944a80c.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.5944a80c.json
new file mode 100644
index 0000000000..1a4ed9554c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.5944a80c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 5944a80c",
+  "killed_by": "tests/structure.py",
+  "old": "    if sample in _ROOM_AIR_KINDS and facts.ventilation:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.8566cb75.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.8566cb75.json
new file mode 100644
index 0000000000..c6bea2d1ef
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.8566cb75.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF 8566cb75",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.signals is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.d88e9b76.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.d88e9b76.json
new file mode 100644
index 0000000000..55c438864d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.GUARD_OFF.d88e9b76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared GUARD_OFF d88e9b76",
+  "killed_by": "tests/features.py",
+  "old": "    if facts.external_heat:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.RETURN_DEL.e3a2add1.json b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.RETURN_DEL.e3a2add1.json
new file mode 100644
index 0000000000..9e5cf8a325
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/_shared.RETURN_DEL.e3a2add1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:_shared RETURN_DEL e3a2add1",
+  "killed_by": "tests/features.py",
+  "old": "    return facts.tail",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/reason.BOOLOP.fe66f904.json b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.BOOLOP.fe66f904.json
new file mode 100644
index 0000000000..ef86a4196c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.BOOLOP.fe66f904.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:reason BOOLOP fe66f904",
+  "killed_by": "tests/features.py",
+  "old": "        (why for why, kinds, raised in _ADDITIVE if sample in kinds and raised(facts, evidence)),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`(why for why, kinds, raised in _ADDITIVE if sample in kinds or raised(facts, evidence)),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.5f2c2f63.json b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.5f2c2f63.json
new file mode 100644
index 0000000000..36092af534
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.5f2c2f63.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:reason GUARD_OFF 5f2c2f63",
+  "killed_by": "tests/features.py",
+  "old": "        if shared is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=66."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.c4d5f7cd.json b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.c4d5f7cd.json
new file mode 100644
index 0000000000..c0d596cbb8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/reason.GUARD_OFF.c4d5f7cd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:reason GUARD_OFF c4d5f7cd",
+  "killed_by": "tests/features.py",
+  "old": "    if sample is not Sample.DELIVERED_RATIO:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=66."
+}
diff --git a/tests/mutation_ledger/killed_by/learning_freeze.py/space_heat.RETURN_DEL.0f2b23c3.json b/tests/mutation_ledger/killed_by/learning_freeze.py/space_heat.RETURN_DEL.0f2b23c3.json
new file mode 100644
index 0000000000..59bd16cc33
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/learning_freeze.py/space_heat.RETURN_DEL.0f2b23c3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/learning_freeze.py:space_heat RETURN_DEL 0f2b23c3",
+  "killed_by": "tests/features.py",
+  "old": "    return Sample.METERED_SPACE_HEAT if metered else Sample.SPACE_HEAT",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.b866fab8.json b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.b866fab8.json
new file mode 100644
index 0000000000..a02b202e72
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/@module.CONST.b866fab8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST b866fab8",
+  "killed_by": "tests/features.py",
+  "old": "_COMBI_COMMIT_SLACK_K = 0.05",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`_COMBI_COMMIT_SLACK_K = 0.1`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.GUARD_OFF.32c4a23e.json b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.GUARD_OFF.32c4a23e.json
new file mode 100644
index 0000000000..fe0f84b9ef
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.GUARD_OFF.32c4a23e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_charge_runs GUARD_OFF 32c4a23e",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if not _engaged(opt):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.RETURN_DEL.616b7fba.json b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.RETURN_DEL.616b7fba.json
new file mode 100644
index 0000000000..099827091d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_charge_runs.RETURN_DEL.616b7fba.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_charge_runs RETURN_DEL 616b7fba",
+  "killed_by": "tests/features.py",
+  "old": "    return ChargeRuns(opt.config.start_price, running, opt.config.clamp_planned_levels)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.CMP_BOUND.a94c3e31.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.CMP_BOUND.a94c3e31.json
new file mode 100644
index 0000000000..e361bb405f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.CMP_BOUND.a94c3e31.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange CMP_BOUND a94c3e31",
+  "killed_by": "tests/features.py",
+  "old": "    kept = short(committed, net_under(committed, space_net)) <= short(dhw_power, space_net) + _COMBI_COMMIT_SLACK_K",
+  "reason": "Killed by the check \"combi: the committed build ships where its store falls exactly the slack further under the requirement ...\" in tests/features.py's R11-OUTSIDE-HONEST-DHW-RUNS block, which sets the slack to the float that makes the two sides equal: CMP_BOUND (`<`) ships the last round's plan there; features_block.py over the block went from 1 failed (the block-mode baseline) to 2 failed with the mutant, the added failure being that check."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.5afe5330.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.5afe5330.json
index a532a51c97..a4c946d049 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.ba727eb5.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.5afe5330.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF ba727eb5",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF 5afe5330",
   "killed_by": "tests/features.py",
-  "old": "        if np.allclose(plan.schedule, dhw_power, atol=1e-4):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "        if np.allclose(plan, dhw_power, atol=1e-4):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.aab41faf.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.aab41faf.json
new file mode 100644
index 0000000000..f5430f3414
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.GUARD_OFF.aab41faf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange GUARD_OFF aab41faf",
+  "killed_by": "tests/features.py",
+  "old": "    if planner.charge_runs is None or space_net is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.e8792dae.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.e8792dae.json
index f1bc862fd8..316ba86b88 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.e8792dae.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received RETURN_DEL d631f182",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange RETURN_DEL e8792dae",
   "killed_by": "tests/features.py",
-  "old": "    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))",
+  "old": "    return committed if kept else dhw_power",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.build.RETURN_DEL.ea9b6925.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.build.RETURN_DEL.ea9b6925.json
new file mode 100644
index 0000000000..70a284bfe3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.build.RETURN_DEL.ea9b6925.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange.build RETURN_DEL ea9b6925",
+  "killed_by": "tests/features.py",
+  "old": "        return np.asarray(plan.schedule)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.net_under.RETURN_DEL.17cf83f0.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.net_under.RETURN_DEL.17cf83f0.json
new file mode 100644
index 0000000000..d574577d9c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.net_under.RETURN_DEL.17cf83f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange.net_under RETURN_DEL 17cf83f0",
+  "killed_by": "tests/structure.py",
+  "old": "        return combi_space_net_kw(store, buffer_temps, dhw_exo, h.dt)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.short.RETURN_DEL.0581556e.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.short.RETURN_DEL.0581556e.json
index b2cba62747..0fab3edeaf 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.RETURN_DEL.d235e41f.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_combi_flux_exchange.short.RETURN_DEL.0581556e.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange RETURN_DEL d235e41f",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_combi_flux_exchange.short RETURN_DEL 0581556e",
   "killed_by": "tests/features.py",
-  "old": "    return dhw_power",
+  "old": "        return float(np.max(gaps))",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.BOOLOP.78de307e.json b/tests/mutation_ledger/killed_by/room_history.py/_accumulate.BOOLOP.78de307e.json
deleted file mode 100644
index 5ee0e8a4ee..0000000000
--- a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.BOOLOP.78de307e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/room_history.py:_accumulate BOOLOP 78de307e",
-  "killed_by": "tests/features.py",
-  "old": "    period.space += house.space_kw > 0.0 and house.dhw_kw <= 0.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`period.space += house.space_kw > 0.0 or house.dhw_kw <= 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.CMP_BOUND.78de307e.json b/tests/mutation_ledger/killed_by/room_history.py/_accumulate.CMP_BOUND.78de307e.json
deleted file mode 100644
index ee712e0cae..0000000000
--- a/tests/mutation_ledger/killed_by/room_history.py/_accumulate.CMP_BOUND.78de307e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/room_history.py:_accumulate CMP_BOUND 78de307e",
-  "killed_by": "tests/features.py",
-  "old": "    period.space += house.space_kw > 0.0 and house.dhw_kw <= 0.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`period.space += house.space_kw >= 0.0 and house.dhw_kw <= 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
deleted file mode 100644
index a0591e68f6..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.faf454fb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP faf454fb",
-  "killed_by": "tests/features.py",
-  "old": "        j = np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`j = (np.rint(b / quantum).astype(np.int64) + half)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json b/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
deleted file mode 100644
index 4c13f622b6..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.CMP_BOUND.a2abb9b6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CMP_BOUND a2abb9b6",
-  "killed_by": "tests/features.py",
-  "old": "        change, paid = step[0] if dest < min_on else step[1]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`change, paid = step[0] if dest <= min_on else step[1]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_shift.RETURN_DEL.f8e0538e.json b/tests/mutation_ledger/killed_by/runs.py/_shift.RETURN_DEL.f8e0538e.json
new file mode 100644
index 0000000000..d7f5bf2912
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/_shift.RETURN_DEL.f8e0538e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:_shift RETURN_DEL f8e0538e",
+  "killed_by": "tests/features.py",
+  "old": "    return lambda bal, _ran: (bal + change, paid)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.25623db3.json b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.25623db3.json
new file mode 100644
index 0000000000..5075a44941
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.25623db3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance CMP_BOUND 25623db3",
+  "killed_by": "tests/features.py",
+  "old": "            for a, act in enumerate(actions[0] if dest < min_on else actions[1])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`for a, act in enumerate(actions[0] if dest <= min_on else actions[1])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=29."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.3909ec94.json b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.3909ec94.json
new file mode 100644
index 0000000000..597b9dd615
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.3909ec94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance CMP_BOUND 3909ec94",
+  "killed_by": "tests/features.py",
+  "old": "        j, extra = place(b, dest < min_on)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`j, extra = place(b, dest <= min_on)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.f2948235.json b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.f2948235.json
new file mode 100644
index 0000000000..3181b63d30
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.CMP_BOUND.f2948235.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance CMP_BOUND f2948235",
+  "killed_by": "tests/features.py",
+  "old": "            (s, starts, a, *act(val[s], s < min_on))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`(s, starts, a, *act(val[s], s <= min_on))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json b/tests/mutation_ledger/killed_by/runs.py/advance.GUARD_OFF.329931dd.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
rename to tests/mutation_ledger/killed_by/runs.py/advance.GUARD_OFF.329931dd.json
index c82853e3a0..22d6e7bca2 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.GUARD_OFF.329931dd.json
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.GUARD_OFF.329931dd.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance GUARD_OFF 329931dd",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance GUARD_OFF 329931dd",
   "killed_by": "tests/features.py",
   "old": "        if not ok.any():",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/runs.py/advance.RETURN_DEL.a247a21c.json b/tests/mutation_ledger/killed_by/runs.py/advance.RETURN_DEL.a247a21c.json
new file mode 100644
index 0000000000..7bff27325f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/advance.RETURN_DEL.a247a21c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:advance RETURN_DEL a247a21c",
+  "killed_by": "tests/features.py",
+  "old": "    return new_cost, new_val, back",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
deleted file mode 100644
index 556f4a03bc..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.056c259e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND 056c259e",
-  "killed_by": "tests/features.py",
-  "old": "        asked = bool(q[k] > 0.0)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`asked = bool(q[k] >= 0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.b415c985.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.b415c985.json
new file mode 100644
index 0000000000..54ef30a5a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.b415c985.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND b415c985",
+  "killed_by": "tests/features.py",
+  "old": "        ran, paused = tie_break(bool(q[k] > 0.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ran, paused = tie_break(bool(q[k] >= 0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json b/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
deleted file mode 100644
index 4bc0e47f2f..0000000000
--- a/tests/mutation_ledger/killed_by/runs.py/commit.CMP_BOUND.d914b133.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/runs.py:commit CMP_BOUND d914b133",
-  "killed_by": "tests/features.py",
-  "old": "        mask[k] = u < min_on",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`mask[k] = u <= min_on`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.3103be9a.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
rename to tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.3103be9a.json
index 82e9874454..e672ff4105 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_advance.CLAMP_DROP.3103be9a.json
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.3103be9a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_advance CLAMP_DROP 3103be9a",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit.cells CLAMP_DROP 3103be9a",
   "killed_by": "tests/features.py",
   "old": "        outside = np.maximum(np.abs(b) - half * quantum, 0.0)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`outside = (np.abs(b) - half * quantum)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`outside = (np.abs(b) - half * quantum)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.c77a9bdd.json b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.c77a9bdd.json
new file mode 100644
index 0000000000..c3ee0b1fd7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.cells.CLAMP_DROP.c77a9bdd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit.cells CLAMP_DROP c77a9bdd",
+  "killed_by": "tests/features.py",
+  "old": "        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), fine * outside",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (np.rint(b / quantum).astype(np.int64) + half), fine * outside`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/commit.cells.RETURN_DEL.c77a9bdd.json b/tests/mutation_ledger/killed_by/runs.py/commit.cells.RETURN_DEL.c77a9bdd.json
new file mode 100644
index 0000000000..f2395cde90
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/commit.cells.RETURN_DEL.c77a9bdd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:commit.cells RETURN_DEL c77a9bdd",
+  "killed_by": "tests/features.py",
+  "old": "        return np.clip(np.rint(b / quantum).astype(np.int64) + half, 0, 2 * half), fine * outside",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/read_back.CMP_BOUND.50ea6816.json b/tests/mutation_ledger/killed_by/runs.py/read_back.CMP_BOUND.50ea6816.json
new file mode 100644
index 0000000000..40ad80db11
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/read_back.CMP_BOUND.50ea6816.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:read_back CMP_BOUND 50ea6816",
+  "killed_by": "tests/features.py",
+  "old": "        mask[k], action[k] = u < min_on, trail[k][2, u, j]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`mask[k], action[k] = u <= min_on, trail[k][2, u, j]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=30."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/read_back.RETURN_DEL.3f4a837c.json b/tests/mutation_ledger/killed_by/runs.py/read_back.RETURN_DEL.3f4a837c.json
new file mode 100644
index 0000000000..d686774334
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/read_back.RETURN_DEL.3f4a837c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:read_back RETURN_DEL 3f4a837c",
+  "killed_by": "tests/features.py",
+  "old": "    return mask, action",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.89e6a09b.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.89e6a09b.json
index 65d574631c..8a1ace9abd 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.89e6a09b.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.89e6a09b.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP 89e6a09b",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves CLAMP_DROP 89e6a09b",
   "killed_by": "tests/features.py",
   "old": "        out += [(i, min(i + 1, states - 1), False) for i in range(min_on, states)]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on, states)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on, states)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.b33258f0.json
similarity index 62%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.b33258f0.json
index 84a00e6ada..056c5dabf1 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.CLAMP_DROP.b33258f0.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.CLAMP_DROP.b33258f0.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves CLAMP_DROP b33258f0",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves CLAMP_DROP b33258f0",
   "killed_by": "tests/features.py",
   "old": "        out += [(i, min(i + 1, last_on), False) for i in range(min_on)]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`out += [(i, (i + 1), False) for i in range(min_on)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=22."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.853776b6.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.853776b6.json
index 520a00450d..68f8418bc0 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.853776b6.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.853776b6.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF 853776b6",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves GUARD_OFF 853776b6",
   "killed_by": "tests/features.py",
   "old": "    if not want == 0.0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=39."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.8742274c.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.8742274c.json
new file mode 100644
index 0000000000..c5ecc37c61
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.8742274c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves GUARD_OFF 8742274c",
+  "killed_by": "tests/features.py",
+  "old": "        if may_start or not free:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=37."
+}
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.edbdf8a8.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.edbdf8a8.json
index 83e3505d83..0a02059388 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.GUARD_OFF.edbdf8a8.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.GUARD_OFF.edbdf8a8.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves GUARD_OFF edbdf8a8",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves GUARD_OFF edbdf8a8",
   "killed_by": "tests/features.py",
   "old": "    if not want == 1.0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=32."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json b/tests/mutation_ledger/killed_by/runs.py/state_moves.RETURN_DEL.a8227ccf.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
rename to tests/mutation_ledger/killed_by/runs.py/state_moves.RETURN_DEL.a8227ccf.json
index 7fec4cdf5a..46c67baa2a 100644
--- a/tests/mutation_ledger/killed_by/runs.py/_moves.RETURN_DEL.a8227ccf.json
+++ b/tests/mutation_ledger/killed_by/runs.py/state_moves.RETURN_DEL.a8227ccf.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/runs.py:_moves RETURN_DEL a8227ccf",
+  "anchor": "custom_components/heatpump_optimizer/runs.py:state_moves RETURN_DEL a8227ccf",
   "killed_by": "tests/features.py",
   "old": "    return out",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/runs.py/tie_break.RETURN_DEL.1cc6ddc1.json b/tests/mutation_ledger/killed_by/runs.py/tie_break.RETURN_DEL.1cc6ddc1.json
new file mode 100644
index 0000000000..d2cd574c1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/runs.py/tie_break.RETURN_DEL.1cc6ddc1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/runs.py:tie_break RETURN_DEL 1cc6ddc1",
+  "killed_by": "tests/features.py",
+  "old": "    return _TIE_BREAK * (not asked), _TIE_BREAK * asked",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.1be5d9b5.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.1be5d9b5.json
deleted file mode 100644
index 7a36937c2f..0000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.1be5d9b5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF 1be5d9b5",
-  "killed_by": "tests/features.py",
-  "old": "        if not self.config.enabled:",
-  "reason": "Recorded by `mutation_table.py --drain` against 1005e27a6fe2b60ded9fa530e03513c5c35c4ead: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.9912aac4.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.9912aac4.json
new file mode 100644
index 0000000000..3780744aec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.9912aac4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF 9912aac4",
+  "killed_by": "tests/features.py",
+  "old": "        if not enabled:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_fdjac.CLAMP_DROP.bcd1af89.json b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.CLAMP_DROP.bcd1af89.json
new file mode 100644
index 0000000000..0d8c1c6a3f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.CLAMP_DROP.bcd1af89.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:_fdjac CLAMP_DROP bcd1af89",
+  "killed_by": "tests/features.py",
+  "old": "        step = 1e-6 * max(abs(float(x[i])), 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`step = 1e-6 * (abs(float(x[i])))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_fdjac.RETURN_DEL.fb4c1dd0.json b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.RETURN_DEL.fb4c1dd0.json
new file mode 100644
index 0000000000..a7f1e9dca5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/_fdjac.RETURN_DEL.fb4c1dd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:_fdjac RETURN_DEL fb4c1dd0",
+  "killed_by": "tests/features.py",
+  "old": "    return jac",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_lm_solve.CLAMP_DROP.6f2a10e7.json b/tests/mutation_ledger/killed_by/sysid.py/_lm_solve.CLAMP_DROP.6f2a10e7.json
deleted file mode 100644
index 16afff8992..0000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/_lm_solve.CLAMP_DROP.6f2a10e7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:_lm_solve CLAMP_DROP 6f2a10e7",
-  "killed_by": "tests/features.py",
-  "old": "            step = 1e-6 * max(abs(float(x[i])), 1.0)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`step = 1e-6 * (abs(float(x[i])))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.be0146fa.json b/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.be0146fa.json
new file mode 100644
index 0000000000..296f89d389
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.be0146fa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:_ridged.residual RETURN_DEL be0146fa",
+  "killed_by": "tests/features.py",
+  "old": "        return np.append(e, (float(x[2]) - prior_g) / width_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.bec8ba9e.json b/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.bec8ba9e.json
deleted file mode 100644
index b234efb8fd..0000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/_ridged.residual.RETURN_DEL.bec8ba9e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:_ridged.residual RETURN_DEL bec8ba9e",
-  "killed_by": "tests/features.py",
-  "old": "        return np.append(e, (float(x[2]) - prior_g) / SLAB_INTERCEPT_PRIOR_SD_KW)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 5003d56f9d9f7617d5e4dc1372e49dbdbacd39bd: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.d335b51b.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.d335b51b.json
new file mode 100644
index 0000000000..dfdbd135d3
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.d335b51b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions.fill CMP_BOUND d335b51b",
+  "old": "            fills = fills & (under & (level >= ctx.min_run_power) & ran_before if tail else ~under)",
+  "reason": "Equivalent on every float input (CMP_BOUND, the tail's `level >= ctx.min_run_power` -> `>`): the two differ only where the fill's level equals the minimum run power exactly, and no input reaches that float. Measured on the block's rig (`_hdr_rig(t0=50.0, draws=0.5)`, min_run_power 0.6 kW): bisecting step 0's ceiling to two adjacent floats (50.894160773134445 and the next) gives levels 0.5999999999999979 and 0.6000000000000008, either side of 0.6 and some 26 ulps of it apart, so the level steps over the bound and the tie is never computed. Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.f5054d73.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.f5054d73.json
new file mode 100644
index 0000000000..c380450e78
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._actions.fill.CMP_BOUND.f5054d73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._actions.fill CMP_BOUND f5054d73",
+  "old": "            under = level < floor - 1e-9",
+  "reason": "Equivalent on every float input (CMP_BOUND, `level < floor - 1e-9` -> `<=`): the two differ only where the fill's level, `_StoreProgram._to_ceiling`'s `power_for_heat_per_cop_kw` of a share of the run power's heat, equals `floor - 1e-9` exactly, and no input reaches that float. Measured on the block's own rig (`_hdr_rig()`, a 50 degC tank, floor 1.0 kW): bisecting the step's ceiling to two adjacent floats (52.43492312513295 and the next) gives levels 0.9999999989999981 and 0.9999999990000011, either side of 0.999999999 and some 27 ulps apart, so the level steps over the bound and the tie is never computed; the 1e-9 itself is the tolerance that keeps a level a rounding under the floor from reading as a tail. Survived the pin drive's shard 1 (tests/mutation_table.py --pin-killed --scripts tests/features.py --shard 1/4) and features_block.py over the R11-OUTSIDE-HONEST-DHW-RUNS block with the mutant applied (no added failure).",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._to_ceiling.CMP_BOUND.83613a48.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._to_ceiling.CMP_BOUND.83613a48.json
new file mode 100644
index 0000000000..326ba6ff80
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram._to_ceiling.CMP_BOUND.83613a48.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram._to_ceiling CMP_BOUND 83613a48",
+  "old": "        fills = (share > 0.0) & (share < 1.0)",
+  "reason": "Both mutants of the line are equivalent. `share > 0.0` -> `>=` adds only share == 0.0, a tank whose coast lands exactly on the ceiling less the margin: the fill's level is then `power_for_heat_per_cop_kw` of no heat, 0.0 kW, which the run's fill refuses (`under`, 0.0 < floor - 1e-9) and the tail refuses (`level >= ctx.min_run_power`, every caller's minimum run power above 0), so the action is the idle coast either way. `share < 1.0` -> `<=` adds only share == 1.0, which no float input reaches: on the block's rig (`_hdr_rig(t0=50.0, draws=0.5)`, step 0, run power 4.8 kW) bisecting step 0's ceiling to two adjacent floats gives shares 0.9999999999999996 and 1.0000000000000002, so the quotient steps over 1.0, and where it would land the fill's level is the run power the `at(4.8)` action already takes to the same temperature. Measured with the share == 0 tie constructed exactly (room 0.0: level 0.0, fills False). Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CLAMP_DROP.ea9b6ec1.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CLAMP_DROP.ea9b6ec1.json
new file mode 100644
index 0000000000..a4367369ba
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CLAMP_DROP.ea9b6ec1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place CLAMP_DROP ea9b6ec1",
+  "old": "                return np.clip(j, 0, width - 1), np.where(inside, 0.0, np.inf)",
+  "reason": "Equivalent on every input (CLAMP_DROP, `np.clip(j, 0, width - 1)` -> `(j)`): a cell index the clip would move lies outside [0, width - 1], where `inside` (which requires `j >= 0` and `j < width`) is False, so the same arrival's extra cost is inf; runs.advance drops every arrival whose cost is not finite (`ok = np.isfinite(c)`, then `j = j[ok]`) before it indexes a cell with j, so no clipped index is ever read. Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.0637f071.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.0637f071.json
new file mode 100644
index 0000000000..f247193949
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/_StoreProgram.plan.place.CMP_BOUND.0637f071.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:_StoreProgram.plan.place CMP_BOUND 0637f071",
+  "old": "                inside = (t >= self.floors[k] - SHORTFALL_K + _STORE_MARGIN_K) & (j >= 0) & (j < width)",
+  "reason": "The line carries three CMP_BOUND mutants under one anchor, and the ledger pins an anchor killed only when every mutant is. Two are killed by tests/features.py's R11-OUTSIDE-HONEST-DHW-RUNS block: `t > ...` by the check \"the store program keeps a store that coasts exactly onto its floor bound ...\", and `j <= width` by \"the store program's grid ends at its top knot ...\" (features_block.py over the block: 1 failed at the block-mode baseline, 2 with each mutant). The third, `j >= 0` -> `j > 0`, is equivalent: `_StoreProgram.__init__` sets `lo = floor(min(initial, min(floors))) - _COP_KNOT_K`, so wherever the first conjunct holds, t >= floors[k] - 0.05 + 0.02 >= lo + 0.97 and j = rint((t - lo) / 0.25) >= 4; j == 0 arrives only where the first conjunct is already false, and `np.clip(j, 0, width - 1)` is untouched by the mutant. That mutant ran the block with no added failure.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/dhw_charges.py/commit_charges.CMP_BOUND.a8e7dc9b.json b/tests/mutation_ledger/survivor_triage/dhw_charges.py/commit_charges.CMP_BOUND.a8e7dc9b.json
new file mode 100644
index 0000000000..40cdbed8b6
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/dhw_charges.py/commit_charges.CMP_BOUND.a8e7dc9b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges CMP_BOUND a8e7dc9b",
+  "old": "        fits(np.where((plan > 0.0) & (plan < floor), floor, plan)),",
+  "reason": "The line carries two CMP_BOUND mutants under one anchor. `plan > 0.0` -> `>=` is killed by tests/features.py (it lifts every idle step to the floor). `plan < floor` -> `<=` is equivalent on every input: it adds only steps where plan == floor, and `np.where(mask, floor, plan)` writes floor there, the value the step already holds, so the lifted plan is the same array. Survived the unsharded pin drive (tests/mutation_table.py --pin-killed --base origin/main) on every driver in play.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/draw_range.py/fold.CMP_BOUND.8c264f30.json b/tests/mutation_ledger/survivor_triage/draw_range.py/_fold_window.CMP_BOUND.8c264f30.json
similarity index 97%
rename from tests/mutation_ledger/survivor_triage/draw_range.py/fold.CMP_BOUND.8c264f30.json
rename to tests/mutation_ledger/survivor_triage/draw_range.py/_fold_window.CMP_BOUND.8c264f30.json
index 9ef48a1684..cbe002a3b8 100644
--- a/tests/mutation_ledger/survivor_triage/draw_range.py/fold.CMP_BOUND.8c264f30.json
+++ b/tests/mutation_ledger/survivor_triage/draw_range.py/_fold_window.CMP_BOUND.8c264f30.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold CMP_BOUND 8c264f30",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window CMP_BOUND 8c264f30",
   "old": "    if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c <= command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):",
   "reason": "R10 mutation-anchor: the `killed_by: tests/entities.py` pin was vacuous. Re-driven at 0be5e2de5 by dev/audit/harnesses/r10_anchor_vacuous.py with the 2 ledger row(s) the mutant itself makes stale hidden from its tree, 0 of 1 site(s) were killed by tests/entities.py: the recorded kill was a check refusing a ledger row the mutant made stale (the --anchor self-test, or the survivor_triage staleness check), not one that saw the mutation. Was: Recorded by `mutation_table.py --pin-killed` against 52011c69ae04f8a725c82040669b7c158290f834: CMP_BOUND (`if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c < command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Not re-driven here against the other drivers in its closure, so a gap until one is shown to kill it.",
   "verdict": "gap"
diff --git a/tests/mutation_ledger/survivor_triage/sysid.py/_slab_ua_profile_halfwidth.CLAMP_DROP.dffcdea0.json b/tests/mutation_ledger/survivor_triage/sysid.py/_slab_ua_profile_halfwidth.CLAMP_DROP.dffcdea0.json
deleted file mode 100644
index 02f18b9a81..0000000000
--- a/tests/mutation_ledger/survivor_triage/sysid.py/_slab_ua_profile_halfwidth.CLAMP_DROP.dffcdea0.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:_slab_ua_profile_halfwidth CLAMP_DROP dffcdea0",
-  "old": "        step = 1e-6 * max(abs(float(x_hat[i])), 1.0)",
-  "reason": "arrived with origin/main, commit 96374e62 (\"gate sysid adoption on the fitted UA's profile-likelihood interval\", #1410/#1437); a real gap: dropping `max(..., 1.0)` shrinks the finite-difference step to `1e-6 * |x_hat[i]|` for any `|x_hat[i]| < 1` (a fitted G below 1), which moves the Jacobian and the published interval in its low digits -- inside the driver's margin to the bar, which reads a comparison and never the number. An assertion on the half-width's value would pin it. Survival measured UNMARKED at 467d3d9c on 2026-09-23: no driver in the recorded net (13 drivers) detects the mutant behaviourally. The one driver that reddens it is tests/entities.py's #1217 mark-staleness self-check, which fires solely because THIS entry exists -- a property of the record, not of the mutant, and one it shares with the instrument's own D3-07 `equivalent` marks (pump_mode.py:242, __init__.py:340), which redden identically. It is not a behavioural kill and is not recorded under `killed_by`: moving the mark there removes the mechanism (measured -- entities.py rc=0, ALL 1707 pass).",
-  "verdict": "gap"
-}
diff --git a/tests/replay.py b/tests/replay.py
index 9c954c1912..73f2ff67c2 100644
--- a/tests/replay.py
+++ b/tests/replay.py
@@ -2961,7 +2961,6 @@ def kernel_routes(arm: str, hours: float) -> dict:
 
         async def armed(self):
             if self._sysid.phase == sysid.PHASE_IDLE:
-                self._sysid.config.enabled = True
                 self._sysid.config.min_days_between_runs = 0.0
                 self._sysid.arm(cm.dt_util.now(), plant=self._thermal_params)
             out = await real_update(self)
diff --git a/tests/seam_map.json b/tests/seam_map.json
index 8645619a0d..e71031ec21 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -251,6 +251,9 @@
   "coordinator._space_pump_to_drive": "core",
   "coordinator._store_diagnosis": "core",
   "coordinator._tail_freeze": "learning",
+  "coordinator._freeze_facts": "learning",
+  "coordinator._space_evidence": "learning",
+  "coordinator._ceiling_frozen": "core",
   "coordinator._warm_seeded": "core",
   "coordinator._watch_lift": "learning",
   "coordinator._with_sensor_advisor": "core",
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 74ef86c8a0..1f17d19934 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17228,
+ "class_excess_loc": 17222,
  "const_modules_over_50": 4,
  "coordinator_attrs": 134,
  "coordinator_multiassigned_attrs": 101,
@@ -10,15 +10,15 @@
  "functions_cc_over_15": 26,
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
- "in_function_copies": 11,
+ "in_function_copies": 10,
  "max_cc": 44,
- "max_class_loc": 7821,
+ "max_class_loc": 7766,
  "max_method_loc": 373,
  "methods_over_150": 14,
- "methods_over_200": 7,
- "module_excess_loc": 21753,
+ "methods_over_200": 6,
+ "module_excess_loc": 21705,
  "name_kept_members": 38,
- "recorded_at": "d3d66c40408e76351ffc528686353cadf815a05c",
+ "recorded_at": "0e1eba2b4aafb5dbabbac7e0b0dc31b6ca1ad83e",
  "seam_cut_total": 413,
  "unloaded_package_imports": 5
 }
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 14d357721e..126cf0493e 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -547,6 +547,7 @@
     "custom_components/heatpump_optimizer/debugger.py",
     "custom_components/heatpump_optimizer/defrost.py",
     "custom_components/heatpump_optimizer/device_prefill.py",
+    "custom_components/heatpump_optimizer/dhw_charges.py",
     "custom_components/heatpump_optimizer/dhw_draws.py",
     "custom_components/heatpump_optimizer/dhw_learning.py",
     "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4207,6 +4208,7 @@
     "tests/mutation_ledger/killed_by/debugger.py",
     "tests/mutation_ledger/killed_by/defrost.py",
     "tests/mutation_ledger/killed_by/device_prefill.py",
+    "tests/mutation_ledger/killed_by/dhw_charges.py",
     "tests/mutation_ledger/killed_by/dhw_draws.py",
     "tests/mutation_ledger/killed_by/dhw_learning.py",
     "tests/mutation_ledger/killed_by/dhw_planner.py",
@@ -4294,6 +4296,7 @@
     "tests/mutation_ledger/survivor_triage/coordinator.py",
     "tests/mutation_ledger/survivor_triage/currency.py",
     "tests/mutation_ledger/survivor_triage/debugger.py",
+    "tests/mutation_ledger/survivor_triage/dhw_charges.py",
     "tests/mutation_ledger/survivor_triage/dhw_planner.py",
     "tests/mutation_ledger/survivor_triage/dhw_schedule.py",
     "tests/mutation_ledger/survivor_triage/draw_range.py",
@@ -8961,6 +8964,7 @@
     "tests/mutation_ledger/killed_by/debugger.py",
     "tests/mutation_ledger/killed_by/defrost.py",
     "tests/mutation_ledger/killed_by/device_prefill.py",
+    "tests/mutation_ledger/killed_by/dhw_charges.py",
     "tests/mutation_ledger/killed_by/dhw_draws.py",
     "tests/mutation_ledger/killed_by/dhw_learning.py",
     "tests/mutation_ledger/killed_by/dhw_planner.py",
@@ -9048,6 +9052,7 @@
     "tests/mutation_ledger/survivor_triage/coordinator.py",
     "tests/mutation_ledger/survivor_triage/currency.py",
     "tests/mutation_ledger/survivor_triage/debugger.py",
+    "tests/mutation_ledger/survivor_triage/dhw_charges.py",
     "tests/mutation_ledger/survivor_triage/dhw_planner.py",
     "tests/mutation_ledger/survivor_triage/dhw_schedule.py",
     "tests/mutation_ledger/survivor_triage/draw_range.py",
@@ -9487,6 +9492,7 @@
     "custom_components/heatpump_optimizer/datetime.py",
     "custom_components/heatpump_optimizer/debugger.py",
     "custom_components/heatpump_optimizer/defrost.py",
+    "custom_components/heatpump_optimizer/dhw_charges.py",
     "custom_components/heatpump_optimizer/dhw_draws.py",
     "custom_components/heatpump_optimizer/dhw_learning.py",
     "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -10230,6 +10236,7 @@
     "tests/mutation_ledger/killed_by/debugger.py",
     "tests/mutation_ledger/killed_by/defrost.py",
     "tests/mutation_ledger/killed_by/device_prefill.py",
+    "tests/mutation_ledger/killed_by/dhw_charges.py",
     "tests/mutation_ledger/killed_by/dhw_draws.py",
     "tests/mutation_ledger/killed_by/dhw_learning.py",
     "tests/mutation_ledger/killed_by/dhw_planner.py",
@@ -10317,6 +10324,7 @@
     "tests/mutation_ledger/survivor_triage/coordinator.py",
     "tests/mutation_ledger/survivor_triage/currency.py",
     "tests/mutation_ledger/survivor_triage/debugger.py",
+    "tests/mutation_ledger/survivor_triage/dhw_charges.py",
     "tests/mutation_ledger/survivor_triage/dhw_planner.py",
     "tests/mutation_ledger/survivor_triage/dhw_schedule.py",
     "tests/mutation_ledger/survivor_triage/draw_range.py",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
