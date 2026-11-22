# Review packet #3835
head: c6c11df0b85b569718a0a41a49544b9ddec3467e
base: 4ebd430fbff9a7b19582ca530a817f34abbafa16

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
arch-score / arch-score id=137030156440 success
arm id=137029323172 skipped
budget-raise-gate / budget-raise-gate id=137030156428 success
cancel-superseded id=137029339040 success
codeql id=137030157956 skipped
codeql / Analyze (actions) id=137030086979 queued
codeql / Analyze (javascript-typescript) id=137030086967 in_progress
codeql / Analyze (python) id=137030086956 queued
gate id=137030815237 in_progress
governance id=137030157505 skipped
governance / env-matrix id=137030087051 in_progress
governance / instrument-self-tests id=137030087039 in_progress
governance / policy-docs id=137030087052 queued
governance / record id=137030088240 skipped
governance / wave-script id=137030087004 success
hassfest id=137030157446 skipped
hassfest / hassfest id=137030087033 success
kernel-points id=137030157885 skipped
pr-contract id=137030817007 skipped
prelude id=137029339259 success
refresh id=137029339270 success
tests id=137030157704 skipped
tests / arch-instrument id=137031058989 queued
tests / briefs id=137030087016 failure
tests / browser id=137031058886 queued
tests / closure-scope id=137030087050 success
tests / closures id=137031058947 queued
tests / coverage id=137031058937 queued
tests / fast (3.14) id=137031058996 queued
tests / mutation id=137030086948 failure
tests / mutation-pins (1) id=137030404432 in_progress
tests / mutation-pins (2) id=137030404431 queued
tests / mutation-pins (3) id=137030404458 queued
tests / mutation-pins (4) id=137030404456 queued
tests / mutation-pins (5) id=137030404471 queued
tests / mutation-pins (6) id=137030404441 in_progress
tests / mutation-pins (7) id=137030404463 queued
tests / mutation-pins (8) id=137030404449 queued
tests / nightly-ha id=137031060482 skipped
tests / nightly-status id=137030087059 success
tests / replay id=137031058920 queued
tests / typing id=137031058948 queued
validate id=137030157846 skipped
validate / validate-hacs id=137030086924 success

## Refusals
red-unanswered: concluded red check `tests / briefs` is not named in ## Red checks
introduced-red: unreadable: head governance / instrument-self-tests job 137030087039: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 9757f161: #3767
NOTE body item 1d6e7396: #3769
NOTE body item 58ac8d3e: dismissed:stated cost, the design's own acceptance
NOTE body item d24b20e2: dismissed:reported to the orchestrator in this seat's handoff result; it constrains no stage brief
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 31 script(s) run, 2 scoped out.
             no segment of this names a program this check knows
  unverified PYTHONPATH=tests/hastub python3 <path>
             the path `<path>` is a template or an expansion, not a literal
  ok         dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py
             `dev/audit/rounds/round11/D7/s2/m3_learner_freeze.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D12/s3/counter_spans.py --sees-dhw --no-mode
             `dev/audit/rounds/round11/D12/s3/counter_spans.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D2/s3/m5_tankfall.py
             `dev/audit/rounds/round11/D2/s3/m5_tankfall.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D2/s3/m5_drawrange.py --run-samples 200
             `dev/audit/rounds/round11/D2/s3/m5_drawrange.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D2/s3/m5_crosscov.py
             `dev/audit/rounds/round11/D2/s3/m5_crosscov.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D5/s4/comments.py --file custom_components/heatpump_optimizer/sysid.py
             `dev/audit/rounds/round11/D5/s4/comments.py` is in the tree at this head
  ok         dev/audit/harnesses/cop_duty_floor.py
             `dev/audit/harnesses/cop_duty_floor.py` is in the tree at this head
  ok         dev/audit/harnesses/cop_dither_fabric.py
             `dev/audit/harnesses/cop_dither_fabric.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py
             `dev/audit/rounds/round11/D7/s2/m2_sysid_plant.py` is in the tree at this head
  ok         dev/audit/rounds/round11/D2/s3/m5_sysid.py
             `dev/audit/rounds/round11/D2/s3/m5_sysid.py` is in the tree at this head
  unverified git grep -n -E '<pattern>' <rev> -- <paths> | wc -l
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         tests/derive_closures.sh --scripts-from <list> --record-only --out-dir D
             `tests/derive_closures.sh` is in the tree at this head
  ok         python3 tests/closure.py merge --in-dir D --partial --allow-failures
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git diff
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/arch_score.py
             `tests/arch_score.py` is in the tree at this head
  ok         tests/arch_score_head.py
             `tests/arch_score_head.py` is in the tree at this head
  ok         tests/frontend.py
             `tests/frontend.py` is in the tree at this head
  ok         tests/open_meteo.py
             `tests/open_meteo.py` is in the tree at this head
  ok         tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         tests/md_tables.mjs
             `tests/md_tables.mjs` is in the tree at this head
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/card_drift.mjs
             `tests/card_drift.mjs` is in the tree at this head
  ok         tests/guard_pins.py
             `tests/guard_pins.py` is in the tree at this head
  ok         tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         tests/edge.py
             `tests/edge.py` is in the tree at this head
  ok         tests/backtest.py
             `tests/backtest.py` is in the tree at this head
  ok         tests/optimality.py
             `tests/optimality.py` is in the tree at this head
  ok         tests/validate.py
             `tests/validate.py` is in the tree at this head
  ok         tests/block_duty.py
             `tests/block_duty.py` is in the tree at this head
  ok         tests/plan_view.py
             `tests/plan_view.py` is in the tree at this head
  ok         tests/debug_collect.py
             `tests/debug_collect.py` is in the tree at this head
  ok         tests/finite_boundary.py
             `tests/finite_boundary.py` is in the tree at this head
  ok         tests/manual_plan.py
             `tests/manual_plan.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         tests/wood_advisor.py
             `tests/wood_advisor.py` is in the tree at this head
  ok         tests/solar_alignment.py
             `tests/solar_alignment.py` is in the tree at this head
  ok         tests/boost_drift_replay.py
             `tests/boost_drift_replay.py` is in the tree at this head
  ok         tests/env_drift.py
             `tests/env_drift.py` is in the tree at this head
  ok         tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/replay.py
             `tests/replay.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/replay.py --one tests/replay/synthetic-dhw-only.json
             `tests/replay.py` is in the tree at this head
  unverified python3 -m cProfile
             python3 runs an inline script rather than a file
  ok         tests/dst_checks.py
             `tests/dst_checks.py` is in the tree at this head

FIGURES: 47 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
deleted file mode 100644
index 52b2a109c9..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature BOOLOP 25dfd051",
-  "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if value is not None or self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
deleted file mode 100644
index 4c2a483d6d..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF 25dfd051",
-  "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
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
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
deleted file mode 100644
index 84f259b026..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF d3d77cdd",
-  "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
deleted file mode 100644
index 63ac676bff..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF cd19f403",
-  "killed_by": "tests/features.py",
-  "old": "        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
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
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
deleted file mode 100644
index d4aaf40705..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF a70a3ddd",
-  "killed_by": "tests/features.py",
-  "old": "        if room_air and self._vent_cusum.tripped:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
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


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 233a4eff49..410622e0bc 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -1208,15 +1208,12 @@ SOLAR_APERTURE_MIN_SAMPLES: Final = 30
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
index 4dbd33b29a..10edffb5a8 100644
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
@@ -960,7 +960,9 @@ def _fold_flow_lift(coord: Any, now: datetime) -> None:
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
@@ -1113,13 +1115,25 @@ def _observe_heat_energy(coord: Any, reader: Any, at: datetime) -> None:
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
@@ -1173,6 +1187,15 @@ async def _async_learn_heat_span(coord: Any, clean: dict[str, bool]) -> None:
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
@@ -3463,6 +3486,31 @@ def _tail_freeze(coord: Any) -> str | None:
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
 
@@ -3750,7 +3798,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             entry.entry_id,
             lambda: _ctx_of(self)._thermal_params,
             publish=functools.partial(_publish_params, self),
-            frozen=functools.partial(self._learning_frozen, room_air=False),
+            frozen=self._learning_frozen,
             heating_active=lambda: bool(planned().get("dhw_heating_active", False)),
             # The live detector, never a solve's copy of it: no solve runs
             # in comfort, boost or off to refresh one (#1736 H4).
@@ -4014,7 +4062,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # --- Active system identification (item 18) ------------------------
         self._sysid = SystemIdentification(
             SysIdConfig(
-                enabled=ctx._config.system_identification_enabled,
                 # The fit's intercept ridge pulls toward these CONFIGURED priors;
                 # arm() re-seeds the gains from the learned profile (#1655).
                 gains_prior_kw=float(ctx._thermal_params.internal_gains),
@@ -4996,11 +5043,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -5294,7 +5341,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if self._measured_power is None and not heat_energy.meter_of(self).counter:
             return COP_REFUSED_NO_POWER
         heat_kw = self._flow_bias.heat_output_kw  # read first: an open window moves no measured heat
-        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):
+        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, sample=learning_freeze.space_heat(heat_kw is not None or heat_energy.meter_of(self).counter), evidence=_space_evidence(self, self._commanded_split())):
             self._measured_cop.frozen_refusals += 1  # machine_evidence's tally
             return COP_REFUSED_FROZEN
 
@@ -5729,7 +5776,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # #2508: no room entity is the raw freeze, so it ranks before the
         # ventilation pass-through below and leaves no counter span clean.
         raw = learner_room_unread(ctx._config) or self._learning_frozen(
-            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY)
+            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY,
+            sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, self._commanded_split()))
         heat_kw, clean, frozen, fold = _replay_gate(self, interval, span_heat_kw, raw)
         # "ventilation" is the one reason to look past: the detector below
         # clears it and needs the residual to see the window close. Any other
@@ -5888,7 +5936,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if not params.two_zone_enabled or not ctx._config.lower_floor_temp_entity:
             return False
         heat_kw, clean, frozen, fold = _replay_gate(self, interval, span_heat_kw, self._learning_frozen(
-            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_LOWER_FLOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY
+            CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_LOWER_FLOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY,
+            sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, self._commanded_split()),
         ))
         if frozen:
             self._learner_freezes.note_freeze("lower", frozen)
@@ -6834,86 +6883,18 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -9197,13 +9178,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -9383,9 +9364,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -9395,6 +9376,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             getattr(self, "_house_heat_loss_samples", 0)
         ):
             return
+        # D7-s2-01: the occupied house's gains; an away residual is the empty house's.
+        if self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, sample=learning_freeze.Sample.OCCUPANCY) is not None:
+            return
         if is_sunlit_interval(previous_state.solar_radiation):
             return
         if previous_time is None or dt_h <= 1e-6:
@@ -9409,8 +9393,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -9949,7 +9935,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -9978,7 +9968,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # (#2262), within the window the accuracy pairing below trusts; a
         # prediction recording no split, or a dwell that saw hot water, is none.
         if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending["split"])):
-            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=power_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"), experiment_s=pending["when"].timestamp() if pending.get("mode") == "system_identification" else None)
+            # An unplanned charge is no running space sample (#3760): the pending split's own evidence.
+            space_frozen = self._learning_frozen(CONF_POWER_ENTITY, sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, pending["split"]))
+            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=space_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"), experiment_s=pending["when"].timestamp() if pending.get("mode") == "system_identification" else None, ceiling_frozen=_ceiling_frozen(self))
 
         # T5 #16: settle every matured lead-time promise against the same
         # measured temperature the one-step sample below uses. The window
@@ -10130,7 +10122,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if not getattr(self, "_ctx", self)._config.dhw_temp_entity:
             return None
         value = finite_float(self._dhw_temperature)
-        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:
+        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, sample=learning_freeze.Sample.PLANT) is None:
             return value
         return None
 
@@ -10295,9 +10287,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
 
@@ -10943,8 +10935,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -11019,9 +11012,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
diff --git a/custom_components/heatpump_optimizer/dhw_learning.py b/custom_components/heatpump_optimizer/dhw_learning.py
index c912d13db2..a9e89d87c5 100644
--- a/custom_components/heatpump_optimizer/dhw_learning.py
+++ b/custom_components/heatpump_optimizer/dhw_learning.py
@@ -41,6 +41,7 @@ from .const import (
 from .dhw_draws import DrawStats, labels_for, window_label as draw_window_label
 from .inputs import plausible_c
 from .thermal_model import TANK_ROOM_AMBIENT_TEMP, ThermalParameters
+from .learning_freeze import Evidence, Sample
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -163,7 +164,7 @@ class DhwProfileLearner:
         params: Callable[[], ThermalParameters],
         *,
         publish: Callable[..., None],
-        frozen: Callable[[str], str | None],
+        frozen: Callable[..., str | None],
         heating_active: Callable[[], bool],
         external_heat_active: Callable[[], bool],
     ) -> None:
@@ -438,35 +439,44 @@ class DhwProfileLearner:
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
diff --git a/custom_components/heatpump_optimizer/draw_range.py b/custom_components/heatpump_optimizer/draw_range.py
index 31f668c4a3..e18f0a5099 100644
--- a/custom_components/heatpump_optimizer/draw_range.py
+++ b/custom_components/heatpump_optimizer/draw_range.py
@@ -776,6 +776,18 @@ def floor_in_force_kw(draw: DrawRange) -> float:
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
@@ -857,6 +869,7 @@ def fold(
     defrost: bool,
     command: Any = None,
     experiment_s: float | None = None,
+    ceiling_frozen: bool = False,
 ) -> None:
     """Fold one interval into ``draw`` when it is a running sample.
 
@@ -873,7 +886,9 @@ def fold(
     action adopted since -- else ``None``. Such an interval that
     ``takes_ceiling`` goes to the ceiling store and NOT to the window, so no
     experiment's draw can trip the window's latch; every other interval
-    folds into the window as before.
+    folds into the window as before. ``ceiling_frozen`` refuses that store
+    sample alone (D2-s3-09, :func:`at_running_floor`): it is dropped, never
+    handed to the window either.
 
     First, whatever this interval: the map runs closed since the last fold
     become rows (``MapRows.commit_runs``) unless ``frozen`` or ``distorted``;
@@ -888,7 +903,8 @@ def fold(
     ):
         return
     if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):
-        draw.observe_ceiling(drawn_kw, experiment_s)
+        if not ceiling_frozen:
+            draw.observe_ceiling(drawn_kw, experiment_s)
     else:
         draw.observe(
             drawn_kw, space, params.min_electrical_power, params.max_electrical_power,
diff --git a/custom_components/heatpump_optimizer/heat_energy.py b/custom_components/heatpump_optimizer/heat_energy.py
index f1a6fec074..5e80d1dd75 100644
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
@@ -415,6 +445,18 @@ class HeatEnergyMeter:
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
     def attribution(self, plan_split: tuple[float, float]) -> Attribution:
         """This cycle's interval, split by the dwell where observed, else by ``plan_split``."""
         return attribution(self.dwell.shares(*self.cycle), plan_split)
@@ -505,9 +547,13 @@ class HeatEnergyMeter:
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
@@ -571,7 +617,7 @@ def close_span(
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
diff --git a/custom_components/heatpump_optimizer/sysid.py b/custom_components/heatpump_optimizer/sysid.py
index d73375a0a0..2a2c0f039f 100644
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
@@ -787,6 +786,23 @@ SLAB_LOG_ROOM_CAP_LO = float(np.log(1e-3))
 SLAB_LOG_ROOM_CAP_HI = float(np.log(1e3))
 
 
+def _fdjac(
+    residual: Callable[[np.ndarray], np.ndarray], x: np.ndarray, value: np.ndarray
+) -> np.ndarray:
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
@@ -809,12 +825,7 @@ def _lm_solve(
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
@@ -982,27 +993,29 @@ def _told_path_error(
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
 
@@ -1016,10 +1029,7 @@ def _slab_ua_profile_halfwidth(
     narrow intervals the gate admits.
     """
 
-    def _residual(x: np.ndarray) -> np.ndarray:
-        return np.append(
-            error(x), (float(x[2]) - prior_g) / SLAB_INTERCEPT_PRIOR_SD_KW
-        )
+    _residual = _ridged(error, prior_g, width_kw)
 
     def _profiled_cost(t: float) -> float:
         def _inner(y: np.ndarray) -> np.ndarray:
@@ -1036,13 +1046,7 @@ def _slab_ua_profile_halfwidth(
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
@@ -1086,7 +1090,7 @@ def _one_state_ua_halfwidth(
 
 
 def _slab_ua_prior_halfwidth(
-    x_hat: np.ndarray, error: _PathError, prior_g: float
+    x_hat: np.ndarray, error: _PathError, prior_g: float, width_kw: float
 ) -> float:
     """The UA interval the intercept prior ITSELF contributes (D7-01).
 
@@ -1118,19 +1122,19 @@ def _slab_ua_prior_halfwidth(
 
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
 
@@ -1146,7 +1150,7 @@ def _slab_ua_told_halfwidth(
     for scales in (((up, 1.0), (down, 1.0)), ((1.0, up), (1.0, down))):
         moved = 0.0
         for m, t in scales:
-            x, _cost = _lm_solve(_ridged(told_error(m, t), prior_g), np.asarray(x_hat, float))
+            x, _cost = _lm_solve(_ridged(told_error(m, t), prior_g, width_kw), np.asarray(x_hat, float))
             moved = max(moved, abs(float(x[0]) - float(x_hat[0])))
         shifts.append(moved)
     return _Z_975 * math.hypot(*shifts)
@@ -1217,8 +1221,9 @@ def _declared_night_halfwidth(
     )
     told = _told_path_error((rooms, outdoors, np.append(powers, 0.0), dts), slab_pair, two_zone)
     x0 = np.array([np.log(max(ua0, 1e-3)), np.log(max(cr0, 1e-2)), g])
+    w = SLAB_INTERCEPT_PRIOR_SD_KW
     return float(np.hypot(
-        _slab_ua_prior_halfwidth(x0, told(1.0, 1.0), g), _slab_ua_told_halfwidth(x0, told, g)
+        _slab_ua_prior_halfwidth(x0, told(1.0, 1.0), g, w), _slab_ua_told_halfwidth(x0, told, g, w)
     ))
 
 
@@ -1439,7 +1444,7 @@ class SystemIdentification:
 
     def arm(
         self, now: datetime, plant: ThermalParameters | None = None,
-        learner_samples: int = 0, probe: DrawRange | None = None,
+        learner_samples: int = 0, probe: DrawRange | None = None, *, enabled: bool = True,
     ) -> bool:
         """Arm an experiment, to start when conditions allow.
 
@@ -1453,9 +1458,11 @@ class SystemIdentification:
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
@@ -1981,18 +1988,18 @@ class SystemIdentification:
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
@@ -2070,7 +2077,7 @@ class SystemIdentification:
             rhs[0] -= sigma2 * float(np.sum(1.0 / dts)) / col_scale[0]
         # The prior enters as its own pseudo-observation, exactly as the
         # stacked row did -- same algebra, normal-equation form, weighed
-        # against the data through prior_rel = prior_w / data_w.
+        # against the data through ``prior_rel = s_noise / prior_sd`` below.
         #
         # D2-07: the right-hand side term had one factor of col_scale[2] too
         # many, which is not a scaling nicety -- it made the prior pull the
@@ -2360,7 +2367,7 @@ class SystemIdentification:
             series, (slab_mass, slab_transfer), self._two_zone_plant
         )
         error = told_error(1.0, 1.0)
-        residual = _ridged(error, self.config.gains_prior_kw)
+        residual = _ridged(error, self.config.gains_prior_kw, SLAB_INTERCEPT_PRIOR_SD_KW)
         prior_g = self.config.gains_prior_kw
 
         # Multi-start over the room-capacity decade: the cost surface has a
@@ -2417,8 +2424,9 @@ class SystemIdentification:
         # clean residual is exactly what a prior-dominated, useless fit
         # looks like, so the interval — not the residual scatter — is the
         # quantity the gate bounds.
+        width = SLAB_INTERCEPT_PRIOR_SD_KW
         profile_halfwidth = _slab_ua_profile_halfwidth(
-            best_x, path_error, int(rooms.size), self.config.gains_prior_kw
+            best_x, path_error, int(rooms.size), self.config.gains_prior_kw, width
         )
         # ... and the interval the intercept prior itself contributes (round-7
         # D7-01, #1459): the profile term above holds prior_g FIXED, so on the
@@ -2426,7 +2434,7 @@ class SystemIdentification:
         # one prior-width moves UA by ~2.3 %, and only the pair of them is
         # what the adoption gate may read.
         prior_halfwidth = _slab_ua_prior_halfwidth(
-            best_x, path_error, self.config.gains_prior_kw
+            best_x, path_error, self.config.gains_prior_kw, width
         )
         # tau_fast re-derives from the fit. The split itself is never
         # adopted — see SysIdResult.slab_mode_tau_hours and the #996
@@ -2444,7 +2452,7 @@ class SystemIdentification:
             ua_profile_halfwidth=profile_halfwidth,
             ua_prior_halfwidth=prior_halfwidth,
             ua_told_halfwidth=_slab_ua_told_halfwidth(
-                best_x, told_error, self.config.gains_prior_kw
+                best_x, told_error, self.config.gains_prior_kw, width
             ),
             confidence=_slab_confidence(rooms, error),
             reason="ok",
@@ -2472,9 +2480,9 @@ def arm_from_config(
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
diff --git a/dev/audit/harnesses/ceiling_probe.py b/dev/audit/harnesses/ceiling_probe.py
index d1101c541b..eb00b933af 100644
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
index b8d4570e47..9983f6d1d4 100644
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
@@ -73,10 +78,22 @@ T0 = 1_800_000_000.0
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
@@ -86,7 +103,7 @@ def run(cell, top):
     for k in range(14):
         drawn = top if cell == "uncensored" else 1.5
         draw_range.fold(d, drawn, (6.0, 0.0), P, frozen=False, distorted=False, defrost=False,
-                        command=CEIL, experiment_s=t)
+                        command=CEIL, experiment_s=t, **_ceiling_ask(d, drawn))
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
index 9df6faeb19..408add3b72 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=98 measured=98",
+  "result": "documented=99 measured=99",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=98, listed=98, missing=[], phantom=[]",
+  "result": "on disk=99, listed=99, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 1edc4327a9..1f0e85e8a5 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 25 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=25 measured=25 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=98 measured=98 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=98, listed=98, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=99 measured=99 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=99, listed=99, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=34 measured=34 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 8444cd49e3..6f5aa38de1 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=98       (96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=99       (98 until R11-SEAM-learners's learning_freeze.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=98            (96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=99            (98 until R11-SEAM-learners's learning_freeze.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
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
diff --git a/dev/programme/carries/carry-3767.json b/dev/programme/carries/carry-3767.json
new file mode 100644
index 0000000000..157a3fcc2d
--- /dev/null
+++ b/dev/programme/carries/carry-3767.json
@@ -0,0 +1,16 @@
+{
+  "_comment": [
+    "Carry destination for the R11-P5 class (#3767): the three priced terms of design/R11-SEAM-learners section 3.3, routed out of R11-SEAM-learners by the orchestrator's answer (option c) to that group's blocked-stop. Shape: dev/governance/rules/finding-propagation.md; linted by tools/policy/brief_lint.mjs."
+  ],
+  "issue": 3767,
+  "stage": "a design revision of design/R11-SEAM-learners section 3.3 that prices the sysid adoption gate's three new terms (D7-s2-02 unlearned intercept width, D2-s3-10 regressor noise, the told COP and outdoor widths) against liveness, then the fix that builds what it keeps",
+  "carries": [
+    {
+      "from": "R11-SEAM-learners (handoff/r11-seam-learners): the pull request that ships section 3.3's mechanical parts only (the arm switch, the shared forward-difference Jacobian, one ridge spelling taking its width) and leaves the three priced terms unbuilt",
+      "effect": "narrows",
+      "control": "Measured by the R11-SEAM-learners fixer at commit 5ec5f3d9f056f9e3f9021080085fee48af630bd4, which built all three terms as section 3.3 specifies, with the derived-preset noise-free nights of tests/features.py's liveness check (_r9p5_derived_night) (the check requires at least 6 of 8 to adopt) as the driver, each term switched on alone by patching module attributes: none of the three adopts 7 of 8; the 0.3 kW unlearned intercept width alone adopts 0 of 8; the regressor-noise term alone 4 of 8; the told COP 0.03 log and outdoor 0.5 K widths alone 1 of 8; all three 0 of 8. The keep table over the 20 derived presets with the 0.3 kW width and the noise term in place read 0 of 20 at every told-width pair it reached, so P5's widths cannot be priced until the intercept width is settled. The null control is the none-of-three arm (7 of 8 adopt), which is the tree's behaviour at the R11-SEAM-learners head.",
+      "remeasure": "These counts are snapshots at 5ec5f3d9f0. Re-take them at your own merge base: the driver that produced them is the harness sysid_told_keep under dev/audit/harnesses at commit 0c859e0ca4951032c5b76e0c949f4d4a06b76a95 (removed from the tree because it patches symbols the shipped head does not have). The finders' harnesses for D7-s2-02 (biased_admitted) and D2-s3-10 (miss share per noisy arm), named under the P5 class in dev/audit/rounds/round11/ISSUES.json, read flat at both ends of R11-SEAM-learners.",
+      "brief": "Do not build any of the three terms as section 3.3 states them: each alone refuses most noise-free nights the liveness check reads, and the intercept width refuses every install without a learned gains profile, which is every new install. Price each term separately against liveness with its own keep table (adopted nights over the derived presets, and the finder's biased-admitted count, per candidate width), the intercept width first, and put the P5 widths to the owner from their table (decision: owner). The ridge already takes its width as an argument (sysid _ridged), so a per-install width is one value passed at the fit and interval call sites."
+    }
+  ]
+}
diff --git a/dev/programme/carries/carry-3769.json b/dev/programme/carries/carry-3769.json
new file mode 100644
index 0000000000..783365d626
--- /dev/null
+++ b/dev/programme/carries/carry-3769.json
@@ -0,0 +1,16 @@
+{
+  "_comment": [
+    "Carry destination for the R11-N-event-misattribution class (#3769): the residual instance R11-SEAM-learners measured and did not build. Shape: dev/governance/rules/finding-propagation.md; linted by tools/policy/brief_lint.mjs."
+  ],
+  "issue": 3769,
+  "stage": "the fix of the plan-flag-off charge's start dip booked as a hot-water draw (DhwProfileLearner on a charge the plan never flagged), on the self-setting pump's seam",
+  "carries": [
+    {
+      "from": "R11-SEAM-learners (handoff/r11-seam-learners): fixes D2-s3-08 (the planned charge's dip) and measures design section 5's plan-flag-off charge arm without building it",
+      "effect": "invalidates",
+      "control": "dev/audit/rounds/round11/D2/s3/m5_tankfall.py's unplanned arm (booked_kwh_unplanned_max) reads the same booked energy at both ends of R11-SEAM-learners, far past the 0.05 kWh band, while its long arms (booked_kwh_long_max, the planned charge) fall to zero at the head: the planned-charge fix does not reach a charge the plan never flagged. The design's mechanism (open ChargeSettle with its dip credit on an unheated interval whose tank rose past the evidence band, so ChargeSettle.advance takes the dip back) is a no-op on DrawStats.take_back, which takes back charge-folded energy only; widening take_back erases the real draw that starts a self-setting pump's own charge.",
+      "remeasure": "Re-run the D2-s3-08 harness (named under the N-event-misattribution class in dev/audit/rounds/round11/ISSUES.json) at your merge base and read booked_kwh_unplanned_max against booked_kwh_long_max (the planned-charge control).",
+      "brief": "The assumption that ChargeSettle's dip credit covers an unflagged charge does not hold: DrawStats.take_back only returns charge-folded energy. A fix must tell the start dip of the pump's own unflagged charge from a real draw that triggers it (a self-setting pump charges because someone drew water), so it needs the tank rise evidence (heat_energy.unplanned_charge) and a rule for the triggering draw, measured with the draw-then-charge shape as its null control."
+    }
+  ]
+}
diff --git a/dev/programme/delivery/3835.md b/dev/programme/delivery/3835.md
new file mode 100644
index 0000000000..9d509d8d64
--- /dev/null
+++ b/dev/programme/delivery/3835.md
@@ -0,0 +1 @@
+- [#3835](https://github.com/tvofi/heatpump_optimizer/pull/3835) — **open**, R11-SEAM-learners: one freeze predicate owns which interval a learner may ingest; the sysid switch is an argument of arm (R11-SEAM-learners)
diff --git a/docs/architecture.md b/docs/architecture.md
index 17319c4fa4..13c5dabc17 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 98 modules, of which 34 import the
+knows nothing about Home Assistant: 99 modules, of which 34 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -178,6 +178,8 @@ custom_components/heatpump_optimizer/
 │
 │   # Learning, evidence and self-checks
 ├── accuracy.py           # Predicted versus realised, recorded per interval
+├── learning_freeze.py    # The one freeze predicate: which interval a learner
+│                         #   may ingest, by the kind of sample it folds
 ├── draw_range.py         # The metered running draw, and the range it clamps a plan to
 ├── diagnosis.py          # One-input-at-a-time attribution of the last interval's error
 ├── drift.py              # The CUSUM primitive shared by every drift detector
@@ -286,7 +288,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-34 of the 98 modules import `homeassistant` at module level: `__init__`,
+34 of the 99 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -295,7 +297,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 63 modules are deliberately free of it, so each can be driven
+The other 64 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/tests/closures.json b/tests/closures.json
index a777fe84eb..03f00d2c8a 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -226,6 +226,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -403,6 +404,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -522,6 +524,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -632,6 +635,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -756,6 +760,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -885,6 +890,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1025,6 +1031,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1160,6 +1167,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1303,6 +1311,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1693,6 +1702,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -1823,6 +1833,8 @@
    "dev/governance/roles/verifier.md",
    "dev/programme/HANDOVER.md",
    "dev/programme/carries/carry-1645.json",
+   "dev/programme/carries/carry-3767.json",
+   "dev/programme/carries/carry-3769.json",
    "dev/programme/rosters/critical-path.json",
    "dev/programme/rosters/wave-r9-groups.json",
    "docs/architecture.md",
@@ -2236,6 +2248,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2438,6 +2451,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2600,6 +2614,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2753,6 +2768,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -2947,6 +2963,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3125,6 +3142,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3526,6 +3544,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3708,6 +3727,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3819,6 +3839,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -3983,6 +4004,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -4086,6 +4108,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -4223,6 +4246,7 @@
    "custom_components/heatpump_optimizer/inputs.py",
    "custom_components/heatpump_optimizer/issues.py",
    "custom_components/heatpump_optimizer/learner_progress.py",
+   "custom_components/heatpump_optimizer/learning_freeze.py",
    "custom_components/heatpump_optimizer/ledger.py",
    "custom_components/heatpump_optimizer/legionella.py",
    "custom_components/heatpump_optimizer/log_latch.py",
@@ -6000,7 +6024,7 @@
    "seconds": 3.3
   },
   "tests/doc_claims.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 31.0
   },
   "tests/dst_checks.py": {
@@ -6012,7 +6036,7 @@
    "seconds": 60.2
   },
   "tests/entities.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 1338.1
   },
   "tests/env_drift.py": {
@@ -6021,7 +6045,7 @@
   },
   "tests/features.py": {
    "rc": 0,
-   "seconds": 422.7
+   "seconds": 1092.0
   },
   "tests/finite_boundary.py": {
    "rc": 0,
@@ -6045,7 +6069,7 @@
   },
   "tests/harness_headers.py": {
    "rc": 0,
-   "seconds": 327.6
+   "seconds": 157.7
   },
   "tests/layout.py": {
    "rc": 0,
@@ -6085,7 +6109,7 @@
   },
   "tests/typing_ruler.py": {
    "rc": 0,
-   "seconds": 0.6
+   "seconds": 31.3
   },
   "tests/validate.py": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 35be7f2db5..70a6d0419d 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 117
+records every read, so this lane's recorded closure is the package: all 118
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (117 until R11-SEAM-learners's ``learning_freeze.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
diff --git a/tests/dst_checks.py b/tests/dst_checks.py
index 8a4491abf6..c62a8f49bb 100644
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
index 1b9dbfc752..d7fddd37c2 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4229,13 +4229,19 @@ def _p2_registry(sources):
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
diff --git a/tests/features.py b/tests/features.py
index 658969c8a4..e10ef5ab6b 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -967,7 +967,7 @@ R.check(
 # it is the null control: learning proceeds exactly as before.
 _np_dhw = DhwProfileLearner(
     FakeHass(), "np", **_owned_params(ThermalParameters()),
-    frozen=lambda *a: None, heating_active=lambda: False,
+    frozen=lambda *a, **_kw: None, heating_active=lambda: False,
     external_heat_active=lambda: False,
 )
 _np_refusal = _np_aio.run(_np_dhw.async_learn_dynamics(-127.0))
@@ -2580,7 +2580,7 @@ R.check(
 
 # D2-s4-02: the step is sized under the abort bound by the noise headroom, on
 # the heavy default house (#779's own cell), and still uses the rest of it.
-_r9f41_sid = SystemIdentification(SysIdConfig(enabled=True))
+_r9f41_sid = SystemIdentification(SysIdConfig())
 _r9f41_el = _r9f41_sid._size_step_power(6.0, 3.0, 21.0, 2.0, HousePlant(ua=0.20, capacity=8.0, gains=0.3))
 _r9f41_peak, _r9f41_final = _r9f41_sysid._predict_step_excursion_plant(
     HousePlant(ua=0.20, capacity=8.0, gains=0.3), 21.0, 2.0,
@@ -7741,12 +7741,12 @@ R.check(
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
@@ -7774,7 +7774,6 @@ R.check(
 # A synthetic house, driven through a whole experiment.
 run_sysid = SystemIdentification(
     SysIdConfig(
-        enabled=True,
         settle_hours=0.5,
         step_hours=2.0,
         relax_hours=2.0,
@@ -7828,7 +7827,7 @@ if result.completed:
 
 # Comfort is a hard constraint on the experiment, not a cost term.
 strict = SystemIdentification(
-    SysIdConfig(enabled=True, settle_hours=0.0, max_excursion_c=0.2)
+    SysIdConfig(settle_hours=0.0, max_excursion_c=0.2)
 )
 strict.arm(night)
 strict.step(
@@ -7845,7 +7844,7 @@ R.check(
 )
 R.check("the abort is recorded with a reason", "excursion" in strict.result.reason)
 
-no_data = SystemIdentification(SysIdConfig(enabled=True))
+no_data = SystemIdentification(SysIdConfig())
 R.check(
     "a fit with no samples fails cleanly",
     not no_data.identify().completed,
@@ -7863,7 +7862,7 @@ from heatpump_optimizer.sysid import (
     SysIdSample as _SID_SAMPLE,
 )
 
-_impossible = SystemIdentification(SysIdConfig(enabled=True))
+_impossible = SystemIdentification(SysIdConfig())
 _impossible.samples = []
 _imp_room, _imp_when = 20.7, datetime(2026, 2, 1, 0, 0, tzinfo=UTC)
 for _imp_phase, _imp_power, _imp_steps in (
@@ -7886,7 +7885,7 @@ R.check(
     f"ua={_impossible_res.heat_loss_kw_per_c}",
 )
 
-repeat = SystemIdentification(SysIdConfig(enabled=True, min_days_between_runs=30))
+repeat = SystemIdentification(SysIdConfig(min_days_between_runs=30))
 repeat.last_run = NOW - timedelta(days=2)
 R.check("a recent run blocks another", not repeat.arm(NOW))
 
@@ -7904,7 +7903,7 @@ from heatpump_optimizer.sysid import slab_mode_identifiability as _sid_idable
 _sid_plant = ThermalParameters()
 R.check(
     "the default plant passes the arm-time identifiability gate",
-    _sid_idable(_sid_plant, SysIdConfig(enabled=True))[0],
+    _sid_idable(_sid_plant, SysIdConfig())[0],
     "production arms with a declared plant; the gate must accept it, or the "
     "production sequence the pin below drives is not the production one",
 )
@@ -7929,7 +7928,6 @@ SystemIdentification.identify_slab = _sid_count(_sid_identify_slab, "identify_sl
 def _sid_drive(with_plant):
     experiment = SystemIdentification(
         SysIdConfig(
-            enabled=True,
             settle_hours=0.5,
             step_hours=2.0,
             relax_hours=2.0,
@@ -8429,7 +8427,7 @@ class _CopGate:
         self._flow_bias = flow_lift.FlowCurveBias()
         self.cop_health_calls: list = []
 
-    def _learning_frozen(self, *entities, room_air=True):
+    def _learning_frozen(self, *entities, **_kw):
         return None
 
     def _observe_cop_health(self, observed_cop, dhw_curve=False):
@@ -8516,7 +8514,7 @@ class _DhwUsage(DhwProfileLearner):
             FakeHass(),
             "dhw-usage",
             **_owned_params(ThermalParameters()),
-            frozen=lambda *_: None,
+            frozen=lambda *_, **_kw: None,
             heating_active=lambda: False,
             external_heat_active=lambda: False,
         )
@@ -9147,7 +9145,7 @@ _nf_learner = _DhwUsage()
 # (_DhwUsage overwrites its own seed with a flat profile).
 _nf_default = DhwProfileLearner(
     FakeHass(), "nf", **_owned_params(ThermalParameters()),
-    frozen=lambda *a: None, heating_active=lambda: False,
+    frozen=lambda *a, **_kw: None, heating_active=lambda: False,
     external_heat_active=lambda: False,
 ).hourly_profile
 _nf_profile = _nf_learner.normalize_profile(
@@ -23295,9 +23293,11 @@ _before53 = _c53._internal_gains_profile[19]
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
@@ -29580,7 +29580,7 @@ def _drifting_sid_samples(
 
 
 def _sid_on(samples, **cfg):
-    _s = SystemIdentification(SysIdConfig(enabled=True, **cfg))
+    _s = SystemIdentification(SysIdConfig(**cfg))
     _s.samples = samples
     return _s.identify()
 
@@ -29675,7 +29675,7 @@ def _drive_sysid_step(ua, cap, gains, cop, max_el=5.0, cadence_min=30, size=True
     The sizer (#779) uses the two-state plant; these historical pins
     characterize ``identify()``, which is still a room-only lumped UA.
     """
-    sid = SystemIdentification(SysIdConfig(enabled=True))
+    sid = SystemIdentification(SysIdConfig())
     t0 = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
     sid.arm(t0)
     temp, tout = 21.0, 2.0
@@ -29715,7 +29715,7 @@ from heatpump_optimizer.thermal_model import ThermalState as _SidPlantState
 
 def _drive_sysid_step_plant(ua, cap, gains, cop, max_el=5.0, cadence_min=15, size=True):
     """Drive an experiment on the two-state plant the sizer uses (#779)."""
-    sid = SystemIdentification(SysIdConfig(enabled=True))
+    sid = SystemIdentification(SysIdConfig())
     t0 = datetime(2026, 1, 15, 23, 0, tzinfo=UTC)
     sid.arm(t0)
     tout = 2.0
@@ -29782,7 +29782,7 @@ R.check(
 )
 _g5_null = _drive_sysid_step(0.20, 8.0, 0.3, 1.0, max_el=6.0)
 _g5_sr = [s for s in _g5_null.samples if s.phase in (_PH_STEP, _PH_RELAX)]
-_g5_sr_sid = SystemIdentification(SysIdConfig(enabled=True))
+_g5_sr_sid = SystemIdentification(SysIdConfig())
 _g5_sr_sid.samples = _g5_sr
 _g5_sr_res = _g5_sr_sid.identify()
 _g5_full = _g5_null.identify()
@@ -29829,7 +29829,7 @@ R.check(
 
 # --- #779: size on the two-state plant, not the one-state exponential ------
 R.section("sysid step sized on the two-state plant (#779)")
-_779_sid = SystemIdentification(SysIdConfig(enabled=True))
+_779_sid = SystemIdentification(SysIdConfig())
 _779_el = _779_sid._size_step_power(6.0, 3.0, 21.0, 2.0, HousePlant(ua=0.20, capacity=8.0, gains=0.3))
 _779_q = (_779_el or 0.0) * 3.0
 _779_plant, _779_final = _predict_step_excursion_plant(
@@ -29852,7 +29852,7 @@ R.check(
     f"one-state {_779_one:.3f} plant {_779_plant:.3f}",
 )
 _settle_sid = SystemIdentification(
-    SysIdConfig(enabled=True, settle_hours=0.5, step_hours=2.0, relax_hours=2.0)
+    SysIdConfig(settle_hours=0.5, step_hours=2.0, relax_hours=2.0)
 )
 _settle_sid.arm(datetime(2026, 2, 1, 23, 0, tzinfo=UTC))
 _settle_t = datetime(2026, 2, 1, 23, 0, tzinfo=UTC)
@@ -38428,8 +38428,10 @@ _PKG_DIR = _Path("custom_components/heatpump_optimizer")
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
@@ -38437,8 +38439,9 @@ class _SysIdHost:
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
@@ -54532,7 +54535,7 @@ R.check(
     _g1401_short is None,
 )
 _g1401_window = SystemIdentification(
-    _SysIdModule.SysIdConfig(enabled=True, start_hour=1, end_hour=5)
+    _SysIdModule.SysIdConfig(start_hour=1, end_hour=5)
 )
 _g1401_window_ok, _g1401_window_why = _g1401_window.conditions_met(
     datetime(2026, 2, 1, 3, 0, tzinfo=UTC), 2.0, 0.55, np.linspace(0.5, 2.0, 96), 5
@@ -54547,7 +54550,7 @@ _g1401_plant = ThermalParameters()
 # non-positive room mass up on construction, so only the slab coupling can be
 # driven to zero here.
 _g1401_plant.slab_heat_transfer = 0.0
-_g1401_unseedable = SystemIdentification(_SysIdModule.SysIdConfig(enabled=True))
+_g1401_unseedable = SystemIdentification(_SysIdModule.SysIdConfig())
 _g1401_arm = _g1401_unseedable.arm(NOW, _g1401_plant)
 R.check(
     "#1401: arming on a plant whose slab pair cannot be seeded is refused, "
@@ -54713,7 +54716,7 @@ R.check(
 # regression -- which is exactly the fit the #991 predicate exists to keep off
 # a slow-slab plant. Admitting the arm above makes that fallback REACHABLE, so
 # it must refuse BY NAME rather than hand the plant to the regression.
-_fb1329 = SystemIdentification(_SysIdModule.SysIdConfig(enabled=True))
+_fb1329 = SystemIdentification(_SysIdModule.SysIdConfig())
 assert _fb1329.arm(_C1329_NOW)  # ungated: the pair is set by hand below
 _fb1329_p = _p942("typical_slab")
 _fb1329._slab_pair = (
@@ -54794,7 +54797,7 @@ def _ridge_drive(params, sigma_c, seed, declare_plant=True, gap_tick=None):
     ua_true = params.heat_loss_coefficient * params.house_heat_loss_scale
     gains = float(params.internal_gains)
     sid = SystemIdentification(
-        _SysIdModule.SysIdConfig(enabled=True, min_days_between_runs=0.0)
+        _SysIdModule.SysIdConfig(min_days_between_runs=0.0)
     )
     assert sid.arm(_RIDGE_NOW, plant=params if declare_plant else None)
     outdoor = 0.0
@@ -55123,7 +55126,7 @@ def _r6_drift_drive(drift_c_per_h, seconds=30):
     ua_true = float(params.heat_loss_coefficient * params.house_heat_loss_scale)
     gains = float(params.internal_gains)
     sid = SystemIdentification(
-        _SysIdModule.SysIdConfig(enabled=True, min_days_between_runs=0.0)
+        _SysIdModule.SysIdConfig(min_days_between_runs=0.0)
     )
     assert sid.arm(_RIDGE_NOW, plant=params)
     outdoor = 2.0
@@ -55269,7 +55272,7 @@ def _drift_drive(seed, cadence_min=30, sigma_c=0.02, drift_c_per_h=0.0):
     rng = np.random.default_rng(seed)
     sid = SystemIdentification(
         _SysIdModule.SysIdConfig(
-            enabled=True, settle_hours=1.0, step_hours=2.0, relax_hours=2.0,
+            settle_hours=1.0, step_hours=2.0, relax_hours=2.0,
             max_excursion_c=0.8, gains_prior_kw=_DRIFT_G,
             thermal_mass_prior=_DRIFT_C,
         )
@@ -55447,7 +55450,6 @@ _t4_arm_on = _t4_coord(system_identification_enabled=False)
 # the fast slab, because this check pins the option re-read and the arm.
 _t4_arm_on._thermal_params.slab_heat_transfer *= 100.0
 _t4_count_refresh(_t4_arm_on)
-_t4_arm_on_built = _t4_arm_on._sysid.config.enabled
 with_config(_t4_arm_on, {"system_identification_enabled": True})
 _t4_drive(_t4_arm_on, "async_arm_system_identification")
 _t4_arm_off = _t4_coord(system_identification_enabled=True)
@@ -55456,17 +55458,10 @@ with_config(_t4_arm_off, {"system_identification_enabled": False})
 _t4_drive(_t4_arm_off, "async_arm_system_identification")
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
 R.check(
     "a refused arm still refreshes, which is what publishes the refusal",
@@ -56615,7 +56610,6 @@ R.check(
     "integer-typed",
 )
 _t6_sysid_on = _t6_coord()
-_t6_sysid_on._sysid.config.enabled = True
 _t6_sysid_on._sysid.arm(datetime(2026, 2, 1, 12, 0, 0))
 R.check(
     "the system-identification property follows the experiment, not a copy",
@@ -60228,7 +60222,7 @@ _G8_SID_FLAT = np.full(24, 1.0)
 
 
 def _g8_sid_new(**cfg):
-    return _G8Sid(_G8SidCfg(enabled=True, **cfg))
+    return _G8Sid(_G8SidCfg(**cfg))
 
 
 def _g8_sid_step(sid, when, room=21.0, outdoor=0.0, **kw):
@@ -63968,26 +63962,32 @@ R.check(
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
@@ -67575,7 +67575,6 @@ def _p5_night(how):
         # price never starts an experiment -- so hourly rows span it.
         c._prices = [{"total": 1.0, "starts_at": (_P5_T0 + timedelta(hours=h)).isoformat()}
                      for h in range(-12, 13)]
-        c._sysid.config.enabled = True
         c._sysid.config.min_days_between_runs = 0.0
         c._sysid.arm(_P5_T0, plant=c._thermal_params)
         prices = np.full(48, 1.0)
@@ -68032,7 +68031,12 @@ R.check(
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
@@ -70797,6 +70801,8 @@ def _z1524_learned(declared, free_kw, hours=range(24)):
         _thermal_params=declared, _internal_gains_profile=None,
         # #2223: the profile folds only behind an identified heat-loss level.
         _house_heat_loss_samples=400,
+        # D7-s2-01: the fold asks the freeze predicate; this house is occupied and clean.
+        _learning_frozen=lambda *keys, **ask: None,
     )
     cap = (declared.upper_floor_thermal_mass if declared.two_zone_enabled
            else declared.room_thermal_mass)
@@ -70868,7 +70874,7 @@ def _z1524_run(
     for _ in range(2400):
         st = plant.simulate_step(st, electrical_power=hold, outdoor_temp=0.0)
     sid = _SysIdModule.SystemIdentification(
-        _SysIdModule.SysIdConfig(enabled=True, min_days_between_runs=0.0)
+        _SysIdModule.SysIdConfig(min_days_between_runs=0.0)
     )
     sid.arm(_z1524_night, plant=_z1524_replace(
         declared, internal_gains_profile=_z1524_learned(
@@ -71900,7 +71906,7 @@ _r9p5_decl = _z1524_replace(
     internal_gains=0.3,
 )
 _r9p5_sid = _SysIdModule.SystemIdentification(_SysIdModule.SysIdConfig(
-    enabled=True, min_days_between_runs=0.0, gains_prior_kw=0.3,
+    min_days_between_runs=0.0, gains_prior_kw=0.3,
 ))
 _r9p5_priors = []
 for _r9p5_hours in ((23, 0, 1, 2, 3, 4), range(9, 18), None):
@@ -71969,7 +71975,7 @@ def _r9p5_derived_night(structure, era):
     model.params.two_zone_enabled = False
     ua = float(decl.heat_loss_coefficient * decl.house_heat_loss_scale)
     sid = _SysIdModule.SystemIdentification(_SysIdModule.SysIdConfig(
-        enabled=True, min_days_between_runs=0.0,
+        min_days_between_runs=0.0,
         gains_prior_kw=float(decl.internal_gains),
     ))
     if not sid.arm(_z1524_night, plant=decl):
@@ -72030,7 +72036,7 @@ R.check(
 # would stop the learners removing. The open-window CUSUM read the heat-loss
 # replay residual against zero, so a model bias tripped it and the freeze
 # self-latched. The barrier the round-10 P5 sweep proposed, as a census: every
-# CUSUM whose trip ``_learning_frozen`` reads is found in the source (the scan
+# CUSUM whose trip ``_learning_frozen`` reads (through ``_freeze_facts``) is found in the source (the scan
 # refuses if it finds none, or loses the open-window one), must measure from a
 # tracked level, and is driven -- on a live coordinator, its own construction
 # -- with a constant cold bias across the range the heat-loss learner folds (up
@@ -72047,7 +72053,9 @@ _r10p5_tree = _r10p5_ast.parse(_r10p5_inspect.getsource(_r10p5_cmod))
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
@@ -73298,12 +73306,14 @@ def _r9egb1_h2(**arm):
 
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
 
@@ -83761,7 +83771,7 @@ R.check(
 
 
 # --- R10-COP-GATE item E: the open-window latch freezes only room-air learners --
-# ``_learning_frozen(room_air=False)`` skips the ventilation reason alone. The
+# ``_learning_frozen(sample=Sample.PLANT)`` skips the ventilation reason alone. The
 # measured-heat COP paths (a counter span, a measured flow heat) and hot water
 # lift; the inferred COP, the flow-curve bias and every room-air learner keep
 # the freeze (dev/audit/harnesses/r10_cop_gate_vent.py measures each arm).
@@ -85324,20 +85334,24 @@ R.check(
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
 
@@ -89142,7 +89156,7 @@ _CP_WEE = _cp_sid.HousePlant(ua=0.05, capacity=1.2, gains=0.3)
 
 
 def _cp_cfg(**kw):
-    return _cp_sid.SysIdConfig(enabled=True, **kw)
+    return _cp_sid.SysIdConfig(**kw)
 
 
 R.check(
@@ -89368,7 +89382,7 @@ def _cp_sysid_cycle(host):
 
 
 _cp_frz = _cp_coord(**_CP_PROBE_CFG)
-_cp_frz._learning_frozen = lambda *keys: "an open window"
+_cp_frz._learning_frozen = lambda *keys, **_kw: "an open window"
 _cp_sysid_cycle(_cp_frz)
 _cp_frz_armed = (_cp_frz._sysid.phase, _cp_frz._sysid.held)
 _cp_frz._sysid.phase = _cp_sid.PHASE_STEP
@@ -89945,7 +89959,7 @@ try:
     _cp_quiet = _cp_coord(**_CP_PROBE_CFG, **_CP_ROOM, quiet_off_windows="22:00-23:30")
     _cp_loud = _cp_coord(**_CP_PROBE_CFG, **_CP_ROOM, quiet_off_windows="09:00-09:30")
     for _cp_c in (_cp_quiet, _cp_loud):
-        _cp_c._learning_frozen = lambda *keys: None  # the freeze is the check above's
+        _cp_c._learning_frozen = lambda *keys, **_kw: None  # the freeze is the check above's
     _cp_sysid_cycle(_cp_quiet)
     _cp_quiet_armed = (_cp_quiet._sysid.phase, _cp_quiet._sysid.held)
     _cp_quiet._sysid.phase = _cp_sid.PHASE_STEP
@@ -89981,17 +89995,20 @@ R.check(
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
 
 
@@ -99143,4 +99160,524 @@ R.check(
     f"before={_rh_ul_before} after={_rh_ul_doc}",
 )
 
+
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
+                command=_CF_CEIL, experiment_s=1.0e9, ceiling_frozen=frozen)
+    return frozen, len(d.ceiling), len(d.samples) - window
+
+
+_cf = {k: _cf_fold(*a) for k, a in {"at_learned_floor": (1.5, 1.5), "at_configured_floor": (1.1,),
+                                     "top_4": (4.0, 1.5), "top_4_cfg": (4.0,)}.items()}
+R.check(
+    "a ceiling sample at the floor in force (learned 1.5 kW, or the configured 1.0 kW unlearned) "
+    "is ceiling-frozen and reaches neither the ceiling store nor the window; a 4.0 kW ceiling "
+    "sample is kept in the store (null control) (D2-s3-09, note 9b3d1e15)",
+    _cf["at_learned_floor"] == (True, 0, 0) and _cf["at_configured_floor"] == (True, 0, 0)
+    and _cf["top_4"] == (False, 1, 0) and _cf["top_4_cfg"] == (False, 1, 0),
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
 sys.exit(R.close("FEATURE CHECKS"))
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
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
deleted file mode 100644
index 52b2a109c9..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.BOOLOP.25dfd051.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature BOOLOP 25dfd051",
-  "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if value is not None or self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
deleted file mode 100644
index 4c2a483d6d..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.25dfd051.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF 25dfd051",
-  "killed_by": "tests/features.py",
-  "old": "        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
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
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
deleted file mode 100644
index 84f259b026..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.d3d77cdd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF d3d77cdd",
-  "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
deleted file mode 100644
index 63ac676bff..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._interval_space_power.GUARD_OFF.cd19f403.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._interval_space_power GUARD_OFF cd19f403",
-  "killed_by": "tests/features.py",
-  "old": "        if heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution((commanded_space, dhw_share))):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
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
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
deleted file mode 100644
index d4aaf40705..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.a70a3ddd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF a70a3ddd",
-  "killed_by": "tests/features.py",
-  "old": "        if room_air and self._vent_cusum.tripped:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
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
index 3f77543780..4338dcf6d9 100644
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
index f465fe713d..ab574ed970 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7868,
+ "max_class_loc": 7814,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "8751943e17ef4d3ec699e7859ae829b4528d8ce7",
+ "recorded_at": "78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f",
  "seam_cut_total": 413
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
