# Review packet #3047
head: d1662cf7b100fe99cc9938c2a536dbced55823f3
base: fb0a6d5a30aa2e3a0b1ce4dd926c057d34a32fa8

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=124865438441 neutral
arch-score / arch-score id=124864905144 success
arm id=124864662695 skipped
budget-raise-gate / budget-raise-gate id=124864905210 queued
cancel-superseded id=124864666521 success
codeql / Analyze (actions) id=124864905184 success
codeql / Analyze (javascript-typescript) id=124864905179 in_progress
codeql / Analyze (python) id=124864905255 in_progress
governance / delivery-status id=124864905316 queued
governance / delivery-status-publish id=124864906224 skipped
governance / env-matrix id=124864905823 queued
governance / instrument-self-tests id=124864905219 in_progress
governance / policy-docs id=124864905272 queued
governance / record id=124864906818 skipped
governance / wave-script id=124864905238 success
hassfest / hassfest id=124864905227 success
kernel-points id=124864906126 skipped
prelude id=124864666680 in_progress
refresh id=124864666833 queued
tests / arch-instrument id=124865808481 queued
tests / briefs id=124864905282 success
tests / browser id=124865808504 queued
tests / closure-scope id=124864905304 success
tests / closures id=124865808538 queued
tests / coverage id=124865808484 queued
tests / fast (3.14) id=124865808454 queued
tests / mutation id=124864905260 failure
tests / mutation-pins (1) id=124865908498 queued
tests / mutation-pins (2) id=124865908403 queued
tests / mutation-pins (3) id=124865908450 queued
tests / mutation-pins (4) id=124865908444 queued
tests / nightly-ha (2025.2.0) id=124865808518 queued
tests / nightly-ha (stable) id=124865808545 queued
tests / nightly-status id=124864905221 success
tests / replay id=124865808471 queued
tests / typing id=124865808614 queued
validate / validate-hacs id=124864905198 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 64b8977b: R10-FACTORY-RESET: R10-FACTORY-RESET resolved on origin/handoff/audit-r10-roster
NOTE body item 86fadb89: R10-LEARNED-STORE-LOAD: R10-LEARNED-STORE-LOAD resolved on origin/handoff/audit-r10-roster
NOTE body item a4676925: R10-LEARNED-STORE-LOAD: R10-LEARNED-STORE-LOAD resolved on origin/handoff/audit-r10-roster
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/typing_ruler.py --mypy
             `tests/typing_ruler.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f
             `tests/env_drift.py` is in the tree at this head
  ok         GOLDEN_MODE=strict PYTHONPATH=tests/hastub python3 tests/golden.py --only config_flow
             `tests/golden.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         node tests/md_tables.mjs
             `tests/md_tables.mjs` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         tests/closure.py select --diff 8fec54ee2
             `tests/closure.py` is in the tree at this head
  ok         tools/pr/ci_predict.py --base 92588d581fde4ce287af3db5e8bb61461dc28015
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  unverified PYTHONPATH=tests/hastub:custom_components python3 -c "from heatpump_optimizer.entry_config import FACTORY_KEPT; [print(k, '--', v) for k, v in FACTORY_KEPT.items()]"
             python3 runs an inline script rather than a file
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/finite_boundary.py
             `tests/finite_boundary.py` is in the tree at this head

FIGURES: 16 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.45d9e00a.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.45d9e00a.json
new file mode 100644
index 000000000..a6c6be541
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.45d9e00a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset GUARD_OFF 45d9e00a",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not user_input.get(\"confirm\"):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.8bc8eedc.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.8bc8eedc.json
new file mode 100644
index 000000000..ab6274a65
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.8bc8eedc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset GUARD_OFF 8bc8eedc",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if user_input is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.a0db8943.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.a0db8943.json
new file mode 100644
index 000000000..ee637273a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.a0db8943.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset GUARD_OFF a0db8943",
+  "killed_by": "tests/features.py",
+  "old": "        if (coord := getattr(self._entry, \"runtime_data\", None)) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.RETURN_DEL.f30dc257.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.RETURN_DEL.f30dc257.json
new file mode 100644
index 000000000..a464949d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.RETURN_DEL.f30dc257.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset RETURN_DEL f30dc257",
+  "killed_by": "tests/features.py",
+  "old": "        return self.async_abort(reason=\"factory_reset_done\" if done else \"factory_reset_not_applied\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.bc450a12.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_learner_payloads.GUARD_OFF.fbcfbdb6.json
similarity index 55%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.bc450a12.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_learner_payloads.GUARD_OFF.fbcfbdb6.json
index 995ab42b6..28a879b47 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.bc450a12.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_learner_payloads.GUARD_OFF.fbcfbdb6.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF bc450a12",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_learner_payloads GUARD_OFF fbcfbdb6",
   "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+  "old": "                if (value := finite_float(thermal.get(key))) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.CLAMP_DROP.1dc0e79b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.CLAMP_DROP.1dc0e79b.json
new file mode 100644
index 000000000..8f2d2d2b5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.CLAMP_DROP.1dc0e79b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning CLAMP_DROP 1dc0e79b",
+  "killed_by": "tests/features.py",
+  "old": "        self._snow_accum_cm = max(0.0, finite_float(stored.get(\"snow_accum_cm\"), 0.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`self._snow_accum_cm = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.41a865ec.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.41a865ec.json
deleted file mode 100644
index 3aa7e0279..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.41a865ec.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF 41a865ec",
-  "killed_by": "tests/features.py",
-  "old": "        if ratio is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against e3f3b312fff572904f24d78a44a2c4492b1a8ddb: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.798dac67.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.798dac67.json
new file mode 100644
index 000000000..3b65af358
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.798dac67.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF 798dac67",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, \"house_heat_loss_scale\", \"house_heat_loss_samples\", self._apply_house_heat_loss_scale)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=25."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.b39a405a.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.b39a405a.json
new file mode 100644
index 000000000..4cac576fb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.b39a405a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF b39a405a",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, \"buffer_cooling_rate\", \"buffer_cooling_samples\", self._apply_buffer_cooling_rate)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.dc87c807.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.dc87c807.json
new file mode 100644
index 000000000..0e019dd37
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.dc87c807.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF dc87c807",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, _COP_STORE_KEY, \"cop_samples\", self._apply_cop_scale)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.e9836e13.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.e9836e13.json
new file mode 100644
index 000000000..64c998c05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.e9836e13.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF e9836e13",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, \"lower_floor_loss_ratio\", \"lower_floor_loss_samples\", self._apply_lower_floor_loss_ratio)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=21."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.BOOLOP.45eae803.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.BOOLOP.45eae803.json
new file mode 100644
index 000000000..d67aa509c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.BOOLOP.45eae803.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._current_humidity BOOLOP 45eae803",
+  "killed_by": "tests/features.py",
+  "old": "        return value if value is not None and 0.0 <= value <= 100.0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return value if value is not None or 0.0 <= value <= 100.0 else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.RETURN_DEL.45eae803.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.RETURN_DEL.45eae803.json
new file mode 100644
index 000000000..c77bebdab
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.RETURN_DEL.45eae803.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._current_humidity RETURN_DEL 45eae803",
+  "killed_by": "tests/features.py",
+  "old": "        return value if value is not None and 0.0 <= value <= 100.0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_restore_learned_snapshot.GUARD_OFF.d20d64a4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_restore_learned_snapshot.GUARD_OFF.d20d64a4.json
new file mode 100644
index 000000000..19098aaf9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_restore_learned_snapshot.GUARD_OFF.d20d64a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_restore_learned_snapshot GUARD_OFF d20d64a4",
+  "killed_by": "tests/features.py",
+  "old": "        if \"before_reset\" in snap:  # a factory reset's undo point: stores and settings back",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # a factory reset's undo point: stores and settings back`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.0bcc5a76.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.0bcc5a76.json
new file mode 100644
index 000000000..d9fb0b2fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.0bcc5a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_rewrite_entry GUARD_OFF 0bcc5a76",
+  "killed_by": "tests/features.py",
+  "old": "    if not await hass.config_entries.async_unload(entry.entry_id):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.3602237b.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.3602237b.json
new file mode 100644
index 000000000..2ba151ef0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.3602237b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_rewrite_entry GUARD_OFF 3602237b",
+  "killed_by": "tests/features.py",
+  "old": "    if settings is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.RETURN_DEL.80a0007e.json
new file mode 100644
index 000000000..b2226ca79
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_rewrite_entry RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_store_documents.RETURN_DEL.e2917fe4.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_store_documents.RETURN_DEL.e2917fe4.json
new file mode 100644
index 000000000..cb047400b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_store_documents.RETURN_DEL.e2917fe4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_store_documents RETURN_DEL e2917fe4",
+  "killed_by": "tests/features.py",
+  "old": "    return {name: await store.async_load() for (name, _), store in zip(_FACTORY_VOID, _restored_stores(coord))}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_isoformat.GUARD_OFF.e71653f6.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_isoformat.GUARD_OFF.e71653f6.json
new file mode 100644
index 000000000..4d6112daa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_isoformat.GUARD_OFF.e71653f6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_isoformat GUARD_OFF e71653f6",
+  "killed_by": "tests/features.py",
+  "old": "    if not isinstance(raw, str):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.GUARD_OFF.49093545.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.GUARD_OFF.49093545.json
new file mode 100644
index 000000000..40f62f181
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.GUARD_OFF.49093545.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_learner GUARD_OFF 49093545",
+  "killed_by": "tests/features.py",
+  "old": "    if (value := stored.get(key)) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.5cb47597.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.5cb47597.json
new file mode 100644
index 000000000..5163af912
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.5cb47597.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_learner RETURN_DEL 5cb47597",
+  "killed_by": "tests/features.py",
+  "old": "    return count",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=19."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.d7923b87~2.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.d7923b87~2.json
new file mode 100644
index 000000000..9afe1c2ec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.d7923b87~2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_learner RETURN_DEL d7923b87#2",
+  "killed_by": "tests/features.py",
+  "old": "        return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json b/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json
new file mode 100644
index 000000000..cd6eacae1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:factory_settings RETURN_DEL 9521dcc2",
+  "killed_by": "tests/features.py",
+  "old": "    return with_settings((data, {**options, **pinned}), ({}, {}))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/with_settings.RETURN_DEL.80c79bfe.json b/tests/mutation_ledger/killed_by/entry_config.py/with_settings.RETURN_DEL.80c79bfe.json
new file mode 100644
index 000000000..4472f55a9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/with_settings.RETURN_DEL.80c79bfe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:with_settings RETURN_DEL 80c79bfe",
+  "killed_by": "tests/features.py",
+  "old": "    return {**rest[0], **kept[0]}, {**rest[1], **kept[1]}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/services.py/handle_factory_reset.RETURN_DEL.4bcd781f.json b/tests/mutation_ledger/killed_by/services.py/handle_factory_reset.RETURN_DEL.4bcd781f.json
new file mode 100644
index 000000000..ae5ebd5ac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/services.py/handle_factory_reset.RETURN_DEL.4bcd781f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/services.py:handle_factory_reset RETURN_DEL 4bcd781f",
+  "killed_by": "tests/features.py",
+  "old": "    return {\"reset\": data[\"entry_id\"], \"scope\": data[\"scope\"]}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.512dc888.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.512dc888.json
deleted file mode 100644
index dfaa9348a..000000000
--- a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.512dc888.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.best_restore GUARD_OFF 512dc888",
-  "killed_by": "tests/features.py",
-  "old": "            if not snap.get(\"healthy\"):",
-  "reason": "Recorded by `mutation_table.py --drain` against 9061fbd3d710d5894b7083d8a58b8203f9e7aa97: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.6541f9a5.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.6541f9a5.json
new file mode 100644
index 000000000..c2cf92fde
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.6541f9a5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.best_restore GUARD_OFF 6541f9a5",
+  "killed_by": "tests/features.py",
+  "old": "            if not snap.get(\"healthy\") or \"before_reset\" in snap:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.BOOLOP.ee22e5a2.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.BOOLOP.ee22e5a2.json
new file mode 100644
index 000000000..855215f44
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.BOOLOP.ee22e5a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.undo_target BOOLOP ee22e5a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.snapshots and \"before_reset\" in self.snapshots[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.snapshots or \"before_reset\" in self.snapshots[-1]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.GUARD_OFF.ee22e5a2.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.GUARD_OFF.ee22e5a2.json
new file mode 100644
index 000000000..49615c216
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.GUARD_OFF.ee22e5a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.undo_target GUARD_OFF ee22e5a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.snapshots and \"before_reset\" in self.snapshots[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.RETURN_DEL.da7502bd.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.RETURN_DEL.da7502bd.json
new file mode 100644
index 000000000..58029975a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.RETURN_DEL.da7502bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.undo_target RETURN_DEL da7502bd",
+  "killed_by": "tests/features.py",
+  "old": "        return self.best_restore()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}


## Three-dot diff
diff --git a/README.md b/README.md
index 423c8025d..e62f74c36 100644
--- a/README.md
+++ b/README.md
@@ -773,7 +773,7 @@ that deliver them.
 
 ## Services
 
-14 services are registered under the `heatpump_optimizer` domain. Field-level
+15 services are registered under the `heatpump_optimizer` domain. Field-level
 detail for each — including all 31 fields of `set_thermal_parameters` — is in
 [docs/configuration.md](./docs/configuration.md). Worked automation examples — an
 EV charger following the Cost Power Headroom sensor, mode switching on price — are in
@@ -791,6 +791,7 @@ EV charger following the Cost Power Headroom sensor, mode switching on price —
 | `clear_manual_plan` | Drop the manual plan and return to fully automatic planning | Optional |
 | `restore_learned_snapshot` | Roll every learner back to the last weekly snapshot taken with healthy inputs | Optional |
 | `reset_heat_loss_learners` | Return the learned house heat loss scale, the lower floor loss ratio, or both to 1.0 and re-plan; the other learners are left alone | Optional |
+| `factory_reset` | Return one entry's settings, learned values or both to a fresh installation, keeping the sensors and the house's wiring; `restore_learned_snapshot` undoes it | Optional |
 | `diagnose_interval` | Attribute the last interval's temperature error input by input | Optional |
 | `debug_collect` | Start, stop or read the week of debug data that Download diagnostics carries | Optional |
 | `assign_entity` | Assign or clear one optional sensor slot | Optional |
@@ -916,7 +917,7 @@ Full theory, with every mechanism and its defaults:
 ## Changing settings after setup
 
 Open the integration and choose **Configure**. Instead of one long form you get a
-menu of 23 pages — 22 you can edit plus a read-only overview — and each can be
+menu of 24 pages — 23 you can edit plus a read-only overview — and each can be
 edited independently. The pages you revisit sit at the top; everything you
 typically set once lives one click further, under **Advanced settings**.
 
@@ -948,6 +949,7 @@ typically set once lives one click further, under **Advanced settings**.
 | Fuse and peak guards | Main fuse, the fuse cap, the live peak guard |
 | Transfer fees and contract | DSO product, per-kWh fees, the fixed-contract comparison |
 | Heat curve control (ECL110) | MQTT topics, displace limits and the controller time constant |
+| Reset to factory defaults | The settings, the learned values or both back to a fresh installation, the sensors and wiring kept; `restore_learned_snapshot` undoes it |
 
 Every sensor you picked during setup can be re-pointed here, and clearing a field
 genuinely clears it. On the **Thermal model (expert)** page a field left empty
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index f05ec6884..f5d8ab932 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -39,6 +39,7 @@ class _ShowFormParent(Protocol):
     ) -> ConfigFlowResult: ...
 
 from .const import (
+    FACTORY_RESET_SCOPES,
     DOMAIN,
     CONFIG_ENTRY_VERSION,
     CONF_TIBBER_TOKEN,
@@ -1552,6 +1553,9 @@ _OPTION_PAGES: Final[tuple[_P, ...]] = (
     _P("grid_connection", "Fuse and peak guards", _ADVANCED),
     _P("grid_fees", "Transfer fees and contract", _ADVANCED),
     _P("heat_curve", "Heat curve control (ECL110)", _ADVANCED),
+    # R10-FACTORY-RESET: an action behind a confirmation, not a settings page;
+    # last, so no one meets it on the way to a setting.
+    _P("factory_reset", "Reset to factory defaults", _ADVANCED),
 )
 
 #: Every field the options flow presents, in the order each page renders them.
@@ -2364,6 +2368,13 @@ def _setup_overview_form(
     )
 
 
+#: The factory reset's one form: which scope, and the explicit confirmation.
+_FACTORY_RESET_SCHEMA: Final = vol.Schema({
+    vol.Required("scope", default=FACTORY_RESET_SCOPES[2]): _select(list(FACTORY_RESET_SCOPES), "factory_reset_scope"),
+    vol.Required("confirm", default=False): selector.BooleanSelector(),
+})
+
+
 class HeatPumpOptimizerConfigFlow(
     _StoredValuesAlwaysFit, config_entries.ConfigFlow, domain=DOMAIN
 ):
@@ -3287,6 +3298,22 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
         # no registry rows for the same reason.
         return _setup_overview_form(self, self._current)
 
+    async def async_step_factory_reset(
+        self, user_input: dict[str, Any] | None = None
+    ) -> ConfigFlowResult:
+        """R10-FACTORY-RESET: unconfirmed, back to the menu with nothing changed;
+        confirmed, the reset runs and closes the dialog, saying whether it applied."""
+        if user_input is None:
+            return self.async_show_form(step_id="factory_reset", data_schema=_FACTORY_RESET_SCHEMA)
+        if not user_input.get("confirm"):
+            return await self.async_step_advanced()
+        if (coord := getattr(self._entry, "runtime_data", None)) is None:
+            return self.async_abort(reason="factory_reset_not_loaded")
+        from .coordinator import async_factory_reset
+
+        done = await async_factory_reset(coord, user_input["scope"])
+        return self.async_abort(reason="factory_reset_done" if done else "factory_reset_not_applied")
+
     async def async_step_quick_setup(
         self, user_input: dict[str, Any] | None = None
     ) -> ConfigFlowResult:
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 6d97645a1..eb20d0e0a 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -681,6 +681,8 @@ SERVICE_DIAGNOSE_INTERVAL: Final = "diagnose_interval"
 SERVICE_DEBUG_COLLECT: Final = "debug_collect"
 #: R10-HOTFIX-LEARNER-INPUTS — the heat-loss learners back to the configuration.
 SERVICE_RESET_HEAT_LOSS: Final = "reset_heat_loss_learners"
+#: R10-FACTORY-RESET — one entry's settings, learners or both to their defaults.
+SERVICE_FACTORY_RESET: Final = "factory_reset"
 MANUAL_PLAN_STORE_VERSION: Final = 1
 # A full solve is seconds of CPU. Dragging a slider must not trigger one per
 # pixel, so simulation requests are rate-limited to this interval.
@@ -1433,6 +1435,9 @@ HEAT_LOSS_BASES: Final = ("commanded", "metered", "measured_heat")
 #: The heat-loss learners by their store key: what the one void path
 #: (``_void_heat_loss_learners``) resets and the reset action's ``learners`` offers.
 HEAT_LOSS_LEARNERS: Final = ("house_heat_loss_scale", "lower_floor_loss_ratio")
+#: A factory reset's scopes (R10-FACTORY-RESET), the service's ``scope`` and the
+#: options step's choice: the settings, every learned store, or both.
+FACTORY_RESET_SCOPES: Final = ("settings", "learners", "both")
 
 # DHW demand window defaults
 DEFAULT_DHW_SCHEDULE_ENABLED: Final = True
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 9268c8f1b..acd596599 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -29,7 +29,7 @@ from dataclasses import dataclass, field, replace
 from operator import attrgetter
 from datetime import datetime, timedelta, timezone
 from pathlib import Path
-from collections.abc import Callable, Mapping, Sequence
+from collections.abc import Awaitable, Callable, Mapping, Sequence
 from typing import TYPE_CHECKING, Any, Final, NamedTuple, NoReturn, cast
 
 import aiohttp
@@ -88,7 +88,7 @@ from .payload import (
     ThermalView,
 )
 from .store import QuarantiningStore, admitted, load_mapping
-from .entry_config import EntryConfig
+from .entry_config import EntryConfig, factory_settings, undo_point, undone_settings
 from homeassistant.util import dt as dt_util
 
 from .const import (
@@ -119,6 +119,7 @@ from .const import (
     HOUSE_HEAT_LOSS_SCALE_MAX,
     HOUSE_HEAT_LOSS_SCALE_MIN,
     DEFAULT_LOWER_FLOOR_LOSS_RATIO,
+    FACTORY_RESET_SCOPES,
     HEAT_LOSS_LEARNERS,
     LOWER_FLOOR_LOSS_RATIO_MAX,
     LOWER_FLOOR_LOSS_RATIO_MIN,
@@ -406,6 +407,31 @@ def _plain_types(value: Any) -> Any:
     return value
 
 
+def _stored_isoformat(raw: Any, kept: datetime | None) -> datetime | None:
+    """A stored ISO instant: ``kept`` where none is stored, None where it does not parse."""
+    if not isinstance(raw, str):
+        return kept
+    try:
+        return datetime.fromisoformat(raw)
+    except ValueError:
+        return None
+
+
+def _stored_learner(stored: Mapping[str, Any], key: str, samples: str, apply: Callable[[float], None]) -> int | None:
+    """Apply a scalar learner's stored ``key`` (the thermal store's four); its
+    ``samples`` count, or None where the key is absent or does not parse."""
+    if (value := stored.get(key)) is None:
+        return None
+    try:
+        apply(float(value))
+        count = _storable_sample_count(stored.get(samples, 0))
+    except (TypeError, ValueError, OverflowError) as err:
+        _LOGGER.debug("Could not load %s: %s", key, err)
+        return None
+    _LOGGER.info("Loaded learned %s %.3f (%d samples)", key, float(value), count)
+    return count
+
+
 def _storable_sample_count(raw: Any) -> int:
     """A stored sample count a fold could have written (D1-s2-03).
 
@@ -1349,6 +1375,96 @@ async def async_adopt_heat_loss_refit(coord: Any) -> bool:
     await coord.async_request_refresh()
     return True
 
+
+#: Each learned store by name, in ``_restored_stores``' order, with what a
+#: factory reset drops of it (R10-FACTORY-RESET): the keys that then load absent,
+#: their initial state, or None for a store learned throughout. The heat-loss
+#: pair is the void path's (``_void_heat_loss_learners``); the rest is fact --
+#: the anchors, the meter's last COP, snow memory, the frequency watchdog's
+#: latch, the billed peaks and the operation mode.
+_FACTORY_VOID: Final[tuple[tuple[str, tuple[str, ...] | None], ...]] = (
+    ("thermal_learning", (
+        "buffer_cooling_rate", "buffer_cooling_samples", _COP_STORE_KEY, "cop_samples",
+        "vent_cusum", "cop_baseline", "cop_health_cusum", "immersion_events",
+        "capacity_envelope", "solar_aperture", "internal_gains_profile",
+        "curve_learner", "freq_map", "flow_bias",
+    )),
+    ("dhw_profile", None),
+    ("dhw_draws", None),
+    ("price_model", None),
+    ("accuracy", ("accuracy", "dhw_accuracy", "defrost", "comfort")),
+)
+
+
+async def _async_store_documents(coord: Any) -> dict[str, Any]:
+    """Each learned store's document by name, the learners flushed to them first."""
+    await _async_save_restored(coord)
+    return {name: await store.async_load() for (name, _), store in zip(_FACTORY_VOID, _restored_stores(coord))}
+
+
+def voided_documents(stored: Mapping[str, Any]) -> dict[str, Any]:
+    """Each learned store's document with ``_FACTORY_VOID``'s keys dropped; None
+    for a store voided whole."""
+    return {name: None if keys is None else {k: v for k, v in (stored[name] or {}).items() if k not in keys}
+            for name, keys in _FACTORY_VOID}
+
+
+async def _async_rewrite_entry(coord: Any, documents: Callable[[], Awaitable[Mapping[str, Any]]],
+                               settings: tuple[dict[str, Any], dict[str, Any]] | None) -> bool:
+    """Unload; write ``documents()`` (None removes a store) and ``settings``; set up again. False if refused."""
+    entry, hass = coord.entry, coord.hass
+    if not await hass.config_entries.async_unload(entry.entry_id):
+        return False
+    written = await documents()
+    for (name, _), store in zip(_FACTORY_VOID, _restored_stores(coord)):
+        if name in written:
+            await (store.async_remove() if written[name] is None else store.async_save(written[name]))
+    if settings is not None:
+        hass.config_entries.async_update_entry(entry, data=settings[0], options=settings[1])
+    await hass.config_entries.async_setup(entry.entry_id)
+    return True
+
+
+async def async_factory_reset(coord: Any, scope: str) -> bool:
+    """``scope``'s settings, learners or both to their defaults (R10-FACTORY-RESET): the undo
+    point; then, unloaded so no save in flight writes the old state back, the heat-loss pair's
+    void path, the rest written, the entry set up again. False, only the undo point, if refused."""
+    for store in (*_restored_stores(coord), coord._snapshot_store):
+        await store.async_wait_for_read()
+    entry, documents = coord.entry, await _async_store_documents(coord)
+    coord._snapshot_ring.take(dt_util.now(), coord._learner_snapshot_payloads(), coord._accuracy.summary(),
+                              coord._inputs_unhealthy() is None,
+                              {**undo_point(scope, entry.data, entry.options), "stores": documents})
+    await coord._async_save_snapshots()
+
+    async def voided() -> dict[str, Any]:
+        if scope == FACTORY_RESET_SCOPES[0]:
+            return {}
+        await coord.async_reset_heat_loss_learners()
+        return voided_documents(await _async_store_documents(coord))
+
+    ctx = _ctx_of(coord)
+    settings = None if scope == FACTORY_RESET_SCOPES[1] else factory_settings(
+        entry.data, entry.options, two_zone=ctx._thermal_params.two_zone_enabled,
+        dhw=ctx._thermal_params.dhw_enabled, wood=wood_furnace_on(ctx._config))
+    done = await _async_rewrite_entry(coord, voided, settings)
+    _LOGGER.warning("Factory reset (%s) %s", scope, "applied; restore_learned_snapshot undoes it" if done
+                    else "not applied: Home Assistant refused to unload the entry")
+    return done
+
+
+async def _async_undo_factory_reset(coord: Any, snap: dict[str, Any]) -> bool:
+    """A reset's undo point back: its stores' documents and the settings it dropped,
+    over the wiring in force; spent, an ordinary snapshot. False where the unload is refused."""
+    undo = snap["before_reset"]
+
+    async def spent() -> Mapping[str, Any]:
+        del snap["before_reset"]
+        await coord._async_save_snapshots()
+        return undo.get("stores") or {}
+
+    return await _async_rewrite_entry(coord, spent, undone_settings(coord.entry.data, coord.entry.options, undo))
+
 #: Which configured entity backs each published temperature -- the table
 #: `_thermal_view` builds its ``reading_ok`` map from. ``ThermalState`` has
 #: constructor defaults (55.0 tank, 40.0 buffer, 22.0 slab, 21.0 either
@@ -4205,50 +4321,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             _LOGGER.debug("Could not load learned thermal parameters: %s", err)
             return
 
-        rate = stored.get("buffer_cooling_rate")
-        if rate is not None:
-            try:
-                self._apply_buffer_cooling_rate(float(rate))
-                self._buffer_cooling_samples = _storable_sample_count(
-                    stored.get("buffer_cooling_samples", 0)
-                )
-                _LOGGER.info(
-                    "Loaded learned buffer tank cooling rate %.2f °C/h (%d samples)",
-                    self._buffer_cooling_rate,
-                    self._buffer_cooling_samples,
-                )
-            except (TypeError, ValueError, OverflowError) as err:
-                _LOGGER.debug("Could not load buffer cooling rate: %s", err)
-
-        scale = stored.get("house_heat_loss_scale")
-        if scale is not None:
-            try:
-                self._apply_house_heat_loss_scale(float(scale))
-                self._house_heat_loss_samples = _storable_sample_count(
-                    stored.get("house_heat_loss_samples", 0)
-                )
-                _LOGGER.info(
-                    "Loaded learned house heat loss scale %.3f (%d samples)",
-                    self._house_heat_loss_scale,
-                    self._house_heat_loss_samples,
-                )
-            except (TypeError, ValueError, OverflowError) as err:
-                _LOGGER.debug("Could not load house heat loss scale: %s", err)
-
-        ratio = stored.get("lower_floor_loss_ratio")
-        if ratio is not None:
-            try:
-                self._apply_lower_floor_loss_ratio(float(ratio))
-                self._lower_floor_loss_samples = _storable_sample_count(
-                    stored.get("lower_floor_loss_samples", 0)
-                )
-                _LOGGER.info(
-                    "Loaded learned lower floor loss ratio %.3f (%d samples)",
-                    self._lower_floor_loss_ratio,
-                    self._lower_floor_loss_samples,
-                )
-            except (TypeError, ValueError, OverflowError) as err:
-                _LOGGER.debug("Could not load lower floor loss ratio: %s", err)
+        if (n := _stored_learner(stored, "buffer_cooling_rate", "buffer_cooling_samples", self._apply_buffer_cooling_rate)) is not None:
+            self._buffer_cooling_samples = n
+        if (n := _stored_learner(stored, "house_heat_loss_scale", "house_heat_loss_samples", self._apply_house_heat_loss_scale)) is not None:
+            self._house_heat_loss_samples = n
+        if (n := _stored_learner(stored, "lower_floor_loss_ratio", "lower_floor_loss_samples", self._apply_lower_floor_loss_ratio)) is not None:
+            self._lower_floor_loss_samples = n
 
         # Re-anchored before anything solves; gated write: `updated_at` defeats the hash skip.
         _had_anchor = all(k in stored for k in _HEAT_LOSS_ANCHOR_KEYS)
@@ -4256,18 +4334,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         if _reanchored or not _had_anchor:
             await self._async_save_thermal_learning()
 
-        cop_scale = stored.get(_COP_STORE_KEY)
-        if cop_scale is not None:
-            try:
-                self._apply_cop_scale(float(cop_scale))
-                self._cop_samples = _storable_sample_count(stored.get("cop_samples", 0))
-                _LOGGER.info(
-                    "Loaded learned COP scale %.3f (%d samples)",
-                    self._cop_scale,
-                    self._cop_samples,
-                )
-            except (TypeError, ValueError, OverflowError) as err:
-                _LOGGER.debug("Could not load COP scale: %s", err)
+        if (n := _stored_learner(stored, _COP_STORE_KEY, "cop_samples", self._apply_cop_scale)) is not None:
+            self._cop_samples = n
         self._measured_cop = MeasuredCop.from_dict(stored.get("measured_cop"))
 
         # v4.0.0 T4a — the detectors' memory. Absent from every pre-T4
@@ -4289,25 +4357,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         raw_events = stored.get("immersion_events")
         if isinstance(raw_events, list):
             self._immersion_events = _aware_instant_iso(raw_events)
-        try:
-            self._snow_accum_cm = max(0.0, float(stored.get("snow_accum_cm", 0.0)))
-        except (TypeError, ValueError, OverflowError):
-            self._snow_accum_cm = 0.0
-        raw_snow = stored.get("last_heavy_snow")
-        if isinstance(raw_snow, str):
-            try:
-                self._last_heavy_snow = datetime.fromisoformat(raw_snow)
-            except ValueError:
-                self._last_heavy_snow = None
+        self._snow_accum_cm = max(0.0, finite_float(stored.get("snow_accum_cm"), 0.0))
+        self._last_heavy_snow = _stored_isoformat(stored.get("last_heavy_snow"), self._last_heavy_snow)
         # The accumulator's clock persists too: without it a restart after
         # a multi-day outage skipped the decay and stale accumulation
         # could re-trip the roof-snow damping.
-        raw_snow_last = stored.get("snow_accum_last")
-        if isinstance(raw_snow_last, str):
-            try:
-                self._snow_accum_last = datetime.fromisoformat(raw_snow_last)
-            except ValueError:
-                self._snow_accum_last = None
+        self._snow_accum_last = _stored_isoformat(stored.get("snow_accum_last"), self._snow_accum_last)
         # T7 #61: the watchdog's stand-down latch, parsed HERE and not in
         # the shared learner parser on purpose — a learner rollback must
         # not re-arm a controller that stood down over a hardware fault;
@@ -9307,12 +9362,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 (self._apply_lower_floor_loss_ratio, "lower_floor_loss_ratio"),
                 (self._apply_cop_scale, _COP_STORE_KEY),
             ):
-                value = thermal.get(key)
-                if value is not None:
-                    try:
-                        setter(float(value))
-                    except (TypeError, ValueError):
-                        continue
+                if (value := finite_float(thermal.get(key))) is not None:
+                    setter(value)
             # T4b learners roll back through the same parser the store
             # loader uses, cleared first so a restore is a restore, not a
             # merge with the drifted state it replaces — ALL of them: a
@@ -9470,13 +9521,15 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # read still in flight lands on top of the restored learner.
         for store in _restored_stores(self):
             await store.async_wait_for_read()
-        snap = self._snapshot_ring.best_restore()
+        snap = self._snapshot_ring.undo_target()
         if snap is None:
             _LOGGER.warning(
                 "No snapshot qualifies for restore (healthy inputs and "
                 "in-band accuracy at capture time are required)"
             )
             return False
+        if "before_reset" in snap:  # a factory reset's undo point: stores and settings back
+            return await _async_undo_factory_reset(self, snap)
         self._apply_learner_payloads(snap.get("learners") or {})
         _LOGGER.info(
             "Learned state restored from the snapshot taken %s",
@@ -9673,13 +9726,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             )
             if best is None or distance < best[0]:
                 best = (distance, raw)
-        if best is None:
-            return None
-        try:
-            value = float(best[1])
-        except (TypeError, ValueError):
-            return None
-        return value if 0.0 <= value <= 100.0 else None
+        value = finite_float(best[1]) if best is not None else None
+        return value if value is not None and 0.0 <= value <= 100.0 else None
 
     def _settle_defrost(self, sample: AccuracySample, window: Any) -> None:
         """Teach the derate from the interval that has just been settled.
@@ -9903,18 +9951,10 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         """
         if not getattr(self, "_ctx", self)._config.dhw_temp_entity:
             return None
-        raw = self._dhw_temperature
-        if raw is None:
-            return None
-        try:
-            value = float(raw)
-        except (TypeError, ValueError):
-            return None
-        if not np.isfinite(value):
-            return None
-        if self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is not None:
-            return None
-        return value
+        value = finite_float(self._dhw_temperature)
+        if value is not None and self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is None:
+            return value
+        return None
 
     def _file_dhw_lead_predictions(
         self, result: OptimizationResult, solve_time: datetime, dt_h: float
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index aa24e56c2..2c63d6105 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -276,3 +276,113 @@ class EntryConfig(Mapping[str, Any]):
 def _restore(raw: dict[str, Any], parsed: dict[str, Any]) -> EntryConfig:
     """``EntryConfig.__reduce__``'s constructor: the stored values and their parse."""
     return EntryConfig(raw=MappingProxyType(raw), **parsed)
+
+
+# -- the factory reset (R10-FACTORY-RESET) ------------------------------------
+
+#: What a factory reset keeps: the wiring that connects the entry to the house,
+#: each with the reason. Every other stored key is a setting and is dropped.
+_WIRING: dict[str, str] = {
+    "name": "the entry's name (Home Assistant's CONF_NAME), not a setting",
+    const.CONF_COMPRESSOR_FREQ_SENSOR: "an entity assignment",
+    const.CONF_PRICE_SOURCE: "the price source",
+    const.CONF_TIBBER_TOKEN: "the price source's credential",
+    const.CONF_SOLAR_FORECAST_SOURCE: "the solar feed, the price source's sibling: "
+    "its default would leave an assigned radiation sensor unread",
+    const.CONF_TWO_ZONE_MODE: "zone topology, written as the settings in force derive it",
+    const.CONF_UPPER_EMITTER: "emitter topology",
+    const.CONF_LOWER_EMITTER: "emitter topology",
+    const.CONF_DHW_ENABLED: "tank topology, written as the settings in force derive it",
+    const.CONF_WOOD_FURNACE_ENABLED: "furnace topology, written as the settings in force derive it",
+    const.CONF_DHW_WOOD_COIL_ENABLED: "tank plumbing: a coil the furnace heats",
+    const.CONF_MIXING_VALVE_MODE: "valve topology",
+    const.CONF_MIXING_VALVE_WRITE_TARGET_KIND: "what the valve's write entity is",
+    const.CONF_SPACE_SETPOINT_UNIT: "what the setpoint entity's number means",
+    const.CONF_TOPOLOGY_LAYOUT: "the plant layout",
+    const.CONF_TOPOLOGY_POSITIONS: "the plant diagram's sensor positions",
+    const.CONF_ECL110_COMMAND_TOPIC: "the controller's MQTT wiring",
+    const.CONF_ECL110_DISPLACE_SET_TOPIC: "the controller's MQTT wiring",
+    const.CONF_ECL110_STATE_TOPIC: "the controller's MQTT wiring",
+    const.CONF_ECL110_QOS: "the controller's MQTT wiring",
+    const.CONF_ECL110_RETAIN: "the controller's MQTT wiring",
+    const.CONF_MODBUS_PREFILL_PREFIX: "the heat pump device the entities came from",
+    const.CONF_MAIN_FUSE_A: "the house's main fuse: a default arms the fuse guard "
+    "against a fuse the house does not have",
+    const.CONF_MAIN_FUSE_PHASES: "the house's main fuse",
+}
+FACTORY_KEPT: Mapping[str, str] = MappingProxyType({
+    **{
+        key: "an entity assignment"
+        for name, key in vars(const).items()
+        if name.startswith("CONF_") and isinstance(key, str) and key.endswith("_entity")
+    },
+    **_WIRING,
+})
+
+Settings = tuple[Mapping[str, Any], Mapping[str, Any]]
+
+
+def settings_of(data: Mapping[str, Any], options: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
+    """The (data, options) keys a factory reset drops: what its undo point keeps."""
+    return ({k: v for k, v in data.items() if k not in FACTORY_KEPT},
+            {k: v for k, v in options.items() if k not in FACTORY_KEPT})
+
+
+def with_settings(wiring: Settings, settings: Settings) -> tuple[dict[str, Any], dict[str, Any]]:
+    """``wiring``'s ``FACTORY_KEPT`` keys over ``settings``' others, per (data, options)."""
+    kept = [{k: v for k, v in side.items() if k in FACTORY_KEPT} for side in wiring]
+    rest = settings_of(*settings)
+    return {**rest[0], **kept[0]}, {**rest[1], **kept[1]}
+
+
+#: The kept keys a settings reset writes, in ``factory_settings``' order: the
+#: topology the dropped keys implied, so its undo point records them as they were.
+FACTORY_PINNED: Mapping[str, str] = MappingProxyType({
+    const.CONF_TWO_ZONE_MODE: "an auto-mode house is two-zone by the zone masses the reset drops",
+    const.CONF_DHW_ENABLED: "the tank's presence, implied by its settings",
+    const.CONF_WOOD_FURNACE_ENABLED: "the furnace's presence, implied by its settings",
+})
+
+
+def undo_point(scope: str, data: Mapping[str, Any], options: Mapping[str, Any]) -> dict[str, Any]:
+    """A reset's ``before_reset`` record: its scope, the settings it drops and,
+    per (data, options), the ``FACTORY_PINNED`` keys it writes as they were."""
+    if scope == const.FACTORY_RESET_SCOPES[1]:
+        return {"scope": scope}
+    pinned = [{k: side[k] for k in FACTORY_PINNED if k in side} for side in (data, options)]
+    return {"scope": scope, "settings": list(settings_of(data, options)), "pinned": pinned}
+
+
+def _side_pair(raw: Any) -> tuple[dict[str, Any], dict[str, Any]] | None:
+    """A stored (data, options) pair, as the snapshot store writes one, or None."""
+    if isinstance(raw, list) and len(raw) == 2 and all(isinstance(side, dict) for side in raw):
+        return raw[0], raw[1]
+    return None
+
+
+def undone_settings(
+    data: Mapping[str, Any], options: Mapping[str, Any], undo: Mapping[str, Any],
+) -> tuple[dict[str, Any], dict[str, Any]] | None:
+    """The (data, options) undoing a reset's ``undo_point`` over the wiring in force,
+    or None where the reset kept the settings (or the record is malformed)."""
+    settings, pinned = _side_pair(undo.get("settings")), _side_pair(undo.get("pinned"))
+    if settings is None or pinned is None:
+        return None
+    unpinned = [{k: v for k, v in side.items() if k not in FACTORY_PINNED} for side in (data, options)]
+    wiring = ({**unpinned[0], **pinned[0]}, {**unpinned[1], **pinned[1]})
+    return with_settings(wiring, (settings[0], settings[1]))
+
+
+def factory_settings(
+    data: Mapping[str, Any], options: Mapping[str, Any], *, two_zone: bool, dhw: bool, wood: bool,
+) -> tuple[dict[str, Any], dict[str, Any]]:
+    """The entry's (data, options) after a factory reset: ``FACTORY_KEPT`` alone.
+
+    A dropped key reads as its default through the parse that reads it absent,
+    so the defaults have one home. The topology a dropped key implied -- the
+    caller's parsed parameters, ``two_zone`` ``dhw`` ``wood`` -- is pinned
+    first: an auto-mode house is two-zone by its zone masses, and dropping
+    those would make it single-zone; the DHW and wood flags likewise.
+    """
+    pinned = dict(zip(FACTORY_PINNED, (const.TWO_ZONE_MODE_ON if two_zone else const.TWO_ZONE_MODE_OFF, dhw, wood)))
+    return with_settings((data, {**options, **pinned}), ({}, {}))
diff --git a/custom_components/heatpump_optimizer/icons.json b/custom_components/heatpump_optimizer/icons.json
index bbe71b405..0d13eb8e0 100644
--- a/custom_components/heatpump_optimizer/icons.json
+++ b/custom_components/heatpump_optimizer/icons.json
@@ -330,6 +330,9 @@
     "diagnose_interval": {
       "service": "mdi:stethoscope"
     },
+    "factory_reset": {
+      "service": "mdi:restore"
+    },
     "reset_heat_loss_learners": {
       "service": "mdi:home-thermometer-outline"
     },
diff --git a/custom_components/heatpump_optimizer/services.py b/custom_components/heatpump_optimizer/services.py
index 456411380..18718ca6f 100644
--- a/custom_components/heatpump_optimizer/services.py
+++ b/custom_components/heatpump_optimizer/services.py
@@ -1,4 +1,4 @@
-"""The domain's fourteen services: schemas, handlers and registration.
+"""The domain's fifteen services: schemas, handlers and registration.
 
 Moved verbatim from ``__init__.py`` (#222, the decomposition program's
 opener; the block used to be ``_async_register_services`` and the module
@@ -56,6 +56,7 @@ from .const import (
     DEFAULT_DHW_MIN_TEMP,
     DEFAULT_DHW_SETPOINT,
     DHW_MIN_TEMP_SETPOINT_MARGIN,
+    FACTORY_RESET_SCOPES,
     HEAT_LOSS_LEARNERS,
     CONF_TOPOLOGY_LAYOUT,
     CONF_TOPOLOGY_POSITIONS,
@@ -66,6 +67,7 @@ from .const import (
     SERVICE_CLEAR_MANUAL_PLAN,
     SERVICE_DEBUG_COLLECT,
     SERVICE_DIAGNOSE_INTERVAL,
+    SERVICE_FACTORY_RESET,
     SERVICE_RESET_HEAT_LOSS,
     SERVICE_RESTORE_SNAPSHOT,
     SERVICE_RUN_OPTIMIZATION,
@@ -84,6 +86,7 @@ from .coordinator import (
     HeatPumpOptimizerConfigEntry,
     HeatPumpOptimizerCoordinator,
     async_adopt_heat_loss_refit,
+    async_factory_reset,
 )
 from .dhw_schedule import (
     DHWWindowError,
@@ -297,6 +300,14 @@ SERVICE_SCHEMA_RESET_HEAT_LOSS = vol.Schema(
     }
 )
 
+# Required: a reset of every loaded entry at once is never what a call means.
+SERVICE_SCHEMA_FACTORY_RESET = vol.Schema(
+    {
+        vol.Required("entry_id"): cv.string,
+        vol.Required("scope"): vol.In(FACTORY_RESET_SCOPES),
+    }
+)
+
 SERVICE_SCHEMA_DIAGNOSE_INTERVAL = vol.Schema(
     {
         vol.Optional("entry_id"): cv.string,
@@ -1175,6 +1186,20 @@ async def handle_reset_heat_loss(hass: HomeAssistant, call: ServiceCall) -> dict
         reset.append(entry_id)
     return {"reset": reset, "learners": list(learners)}
 
+async def handle_factory_reset(hass: HomeAssistant, call: ServiceCall) -> dict[str, Any]:
+    """One entry's ``scope`` to its defaults, after an undo point; the entry is set up again."""
+    data = dict(call.data)
+    for _, coord in _manual_targets(hass, data["entry_id"]):
+        if not await async_factory_reset(coord, data["scope"]):
+            raise HomeAssistantError(
+                f"The factory reset of {data['entry_id']} was not applied: Home "
+                "Assistant refused to unload the entry; nothing was changed",
+                translation_domain=DOMAIN,
+                translation_key="factory_reset_not_applied",
+                translation_placeholders={"entry_id": data["entry_id"]},
+            )
+    return {"reset": data["entry_id"], "scope": data["scope"]}
+
 async def handle_restore_snapshot(hass: HomeAssistant, call: ServiceCall) -> dict[str, Any]:
     """Roll the learners back to the newest trustworthy snapshot (#42).
 
@@ -1333,6 +1358,13 @@ def async_register_services(hass: HomeAssistant) -> None:
         schema=SERVICE_SCHEMA_RESET_HEAT_LOSS,
         supports_response=SupportsResponse.OPTIONAL,
     )
+    hass.services.async_register(
+        DOMAIN,
+        SERVICE_FACTORY_RESET,
+        partial(handle_factory_reset, hass),
+        schema=SERVICE_SCHEMA_FACTORY_RESET,
+        supports_response=SupportsResponse.OPTIONAL,
+    )
     hass.services.async_register(
         DOMAIN,
         SERVICE_DIAGNOSE_INTERVAL,
diff --git a/custom_components/heatpump_optimizer/services.yaml b/custom_components/heatpump_optimizer/services.yaml
index 9cac097bc..6aaa0415e 100644
--- a/custom_components/heatpump_optimizer/services.yaml
+++ b/custom_components/heatpump_optimizer/services.yaml
@@ -547,6 +547,23 @@ reset_heat_loss_learners:
           options:
           - house_heat_loss_scale
           - lower_floor_loss_ratio
+factory_reset:
+  fields:
+    entry_id:
+      required: true
+      example: 01JABCDEFGHJKMNPQRSTVWXYZ0
+      selector:
+        text: null
+    scope:
+      required: true
+      example: settings
+      selector:
+        select:
+          translation_key: factory_reset_scope
+          options:
+          - settings
+          - learners
+          - both
 diagnose_interval:
   fields:
     entry_id:
diff --git a/custom_components/heatpump_optimizer/snapshots.py b/custom_components/heatpump_optimizer/snapshots.py
index 935afcb9e..31a474963 100644
--- a/custom_components/heatpump_optimizer/snapshots.py
+++ b/custom_components/heatpump_optimizer/snapshots.py
@@ -102,6 +102,7 @@ class SnapshotRing:
         learners: dict[str, dict[str, Any]],
         accuracy: Mapping[str, object],
         healthy: bool,
+        before_reset: Mapping[str, Any] | None = None,
     ) -> None:
         # Deep-copied via the same JSON round trip the real Store applies
         # on save: a snapshot holding references into live learner state
@@ -119,6 +120,10 @@ class SnapshotRing:
                 "alarmed_at_capture": self.alarmed,
                 "accuracy": json.loads(json.dumps(dict(accuracy or {}))),
                 "learners": json.loads(json.dumps(learners)),
+                # A factory reset's undo point (``undo_target``): the scope,
+                # and the settings it returns to defaults when it has any.
+                **({"before_reset": json.loads(json.dumps(dict(before_reset)))}
+                   if before_reset is not None else {}),
             }
         )
         del self.snapshots[:-RING_SIZE]
@@ -185,7 +190,8 @@ class SnapshotRing:
         snapshots taken BEFORE the out-of-band streak began qualify: a
         slow drift keeps its bias tag in band for days after the learners
         have already walked away, so in-band-at-capture alone is not
-        proof of innocence.
+        proof of innocence. A factory reset's undo point never qualifies:
+        ``undo_target`` hands it to the user alone.
 
         A malformed snapshot (e.g. a corrupt "accuracy" field from a
         partial write or a hand-edited store) is skipped with a warning
@@ -195,7 +201,7 @@ class SnapshotRing:
         raising (#D1-05).
         """
         for snap in reversed(self.snapshots):
-            if not snap.get("healthy"):
+            if not snap.get("healthy") or "before_reset" in snap:
                 continue
             if snap.get("alarmed_at_capture"):
                 continue
@@ -225,6 +231,18 @@ class SnapshotRing:
             return snap
         return None
 
+    def undo_target(self) -> dict[str, Any] | None:
+        """What the restore service rolls back to: a reset's undo point while it
+        is the newest snapshot, else ``best_restore``.
+
+        The undo point is the user's own, so no health or bias tag gates it, and
+        the drift rollback never takes it (``best_restore`` skips it): only the
+        user undoes a reset the user asked for.
+        """
+        if self.snapshots and "before_reset" in self.snapshots[-1]:
+            return self.snapshots[-1]
+        return self.best_restore()
+
     # -- persistence ---------------------------------------------------------------
 
     def as_dict(self) -> dict[str, Any]:
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 620895a80..f005021f9 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -442,6 +442,9 @@
     "run_optimization_no_prices": {
       "message": "The optimization did not run for {entry_ids}: fewer than four electricity price steps were available"
     },
+    "factory_reset_not_applied": {
+      "message": "The factory reset of {entry_id} was not applied: Home Assistant refused to unload the entry; nothing was changed"
+    },
     "run_optimization_solve_failed": {
       "message": "The optimization did not run for {entry_ids}: the solve failed; the error is in the integration's log"
     },
@@ -529,7 +532,8 @@
           "learning_features": "Advanced learning features",
           "grid_connection": "Fuse and peak guards",
           "grid_fees": "Transfer fees and contract",
-          "heat_curve": "Heat curve control (ECL110)"
+          "heat_curve": "Heat curve control (ECL110)",
+          "factory_reset": "Reset to factory defaults"
         }
       },
       "setup_overview": {
@@ -1500,6 +1504,18 @@
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next.",
           "prefill_offer": "When on, setting up a new entry offers this page if a heat-pump device added to this install can fill any of these settings. Off by default: the setup wizard is unchanged while it is off, and this switch is stored, so it survives a restart."
         }
+      },
+      "factory_reset": {
+        "title": "Reset to factory defaults",
+        "description": "Return the optimizer to the state of a fresh installation. Choose what to reset:\n\n- **Settings**: every setting on these pages (comfort, hot water, prices and fees, the thermal model, modes and features) goes back to its default. Your sensors and other assigned entities, the zones and emitters, the hot water tank, valve and furnace layout, the price source and the main fuse are kept, so the optimizer stays connected to your house.\n- **Learned values**: everything the optimizer has learned about your house is forgotten (heat loss, the lower floor's share, the comfort weight, COP, hot water cooling and use, defrost, the heat curve and the prediction accuracy history), and learning starts again from the settings.\n- **Both**.\n\nBefore anything changes, a snapshot is taken. Until the next weekly snapshot, about a week, the Restore learned snapshot action undoes the reset: the settings and learned values come back as they were, with your sensors as they are now. The integration then reloads and plans again straight away.",
+        "data": {
+          "scope": "What to reset",
+          "confirm": "Yes, reset"
+        },
+        "data_description": {
+          "scope": "Settings, learned values, or both.",
+          "confirm": "Nothing changes unless this is ticked: submitted unticked, the menu comes back."
+        }
       }
     },
     "error": {
@@ -1530,6 +1546,11 @@
       "flow_curve_needs_direct_plant": "Pricing the supply temperature lift is for a system with no mixing valve. With a valve the buffer tank's temperature already prices the lift, so this would count it twice. Set the valve to \"No mixing valve\" or turn this off.",
       "prefill_device_unreadable": "That device could not be read. Its integration has no mapping here yet, or none of its entities holds a value. Leave the device empty and name a Modbus package prefix instead.",
       "dhw_windows_day_selector": "This field already names its day, so enter plain times only, e.g. 06:00-08:30. Day selectors like 'weekdays' belong in the ordinary windows field above."
+    },
+    "abort": {
+      "factory_reset_done": "Reset done. The integration has reloaded and is planning again. To undo the reset, run the Restore learned snapshot action.",
+      "factory_reset_not_loaded": "The integration is not running, so there is nothing to reset. Fix what stopped it, then try again.",
+      "factory_reset_not_applied": "Not applied: Home Assistant refused to unload the integration, so nothing was changed. Try again, or restart Home Assistant first."
     }
   },
   "selector": {
@@ -1659,6 +1680,13 @@
         "observe": "Observe (log only)",
         "control": "Control (write mode and set-points)"
       }
+    },
+    "factory_reset_scope": {
+      "options": {
+        "settings": "Settings",
+        "learners": "Learned values",
+        "both": "Settings and learned values"
+      }
     }
   },
   "issues": {
@@ -2462,7 +2490,7 @@
     },
     "restore_learned_snapshot": {
       "name": "Restore Learned Snapshot",
-      "description": "Roll every learner back to the most recent weekly snapshot that was captured while all inputs were healthy and prediction accuracy was in band. Use this if the learned model has visibly gone wrong — after a sensor fed garbage for a while, for example. The drift watchdog does the same thing automatically when it can prove the inputs were healthy throughout; this service is the manual override for when you can see what it cannot. Nothing is lost permanently: learning simply continues from the restored point. The call fails with an error when no snapshot qualifies, instead of answering with an empty restore. With the source set to the heat-loss refit, it instead accepts the drift advisor's refit of the house heat-loss scale, offered while the drift alarm is raised and three settled days of evidence exist.",
+      "description": "Roll every learner back to the most recent weekly snapshot that was captured while all inputs were healthy and prediction accuracy was in band. Use this if the learned model has visibly gone wrong — after a sensor fed garbage for a while, for example. The drift watchdog does the same thing automatically when it can prove the inputs were healthy throughout; this service is the manual override for when you can see what it cannot. Nothing is lost permanently: learning simply continues from the restored point. The call fails with an error when no snapshot qualifies, instead of answering with an empty restore. With the source set to the heat-loss refit, it instead accepts the drift advisor's refit of the house heat-loss scale, offered while the drift alarm is raised and three settled days of evidence exist. Until the next weekly snapshot after a factory reset, it undoes that reset instead: the settings and learned values come back as they were before it, with the sensors and other entities as they are now.",
       "fields": {
         "entry_id": {
           "name": "Config entry",
@@ -2511,6 +2539,20 @@
           "description": "Restrict the action to one config entry. Leave empty to act on every configured heat pump."
         }
       }
+    },
+    "factory_reset": {
+      "name": "Reset to Factory Defaults",
+      "description": "Return one heat pump's settings, its learned values, or both to the state of a fresh installation. Sensors and other assigned entities, the zone, emitter, tank, valve and furnace layout, the price source and the main fuse are kept. A snapshot is taken first, and Restore learned snapshot undoes the reset until the next weekly snapshot. The integration reloads and plans again straight away.",
+      "fields": {
+        "entry_id": {
+          "name": "Config entry",
+          "description": "The config entry to reset."
+        },
+        "scope": {
+          "name": "Scope",
+          "description": "Settings, learned values, or both."
+        }
+      }
     }
   }
 }
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index ee58a784c..a1de54934 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -442,6 +442,9 @@
     "run_optimization_no_prices": {
       "message": "The optimization did not run for {entry_ids}: fewer than four electricity price steps were available"
     },
+    "factory_reset_not_applied": {
+      "message": "The factory reset of {entry_id} was not applied: Home Assistant refused to unload the entry; nothing was changed"
+    },
     "run_optimization_solve_failed": {
       "message": "The optimization did not run for {entry_ids}: the solve failed; the error is in the integration's log"
     },
@@ -529,7 +532,8 @@
           "learning_features": "Advanced learning features",
           "grid_connection": "Fuse and peak guards",
           "grid_fees": "Transfer fees and contract",
-          "heat_curve": "Heat curve control (ECL110)"
+          "heat_curve": "Heat curve control (ECL110)",
+          "factory_reset": "Reset to factory defaults"
         }
       },
       "setup_overview": {
@@ -1500,6 +1504,18 @@
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next.",
           "prefill_offer": "When on, setting up a new entry offers this page if a heat-pump device added to this install can fill any of these settings. Off by default: the setup wizard is unchanged while it is off, and this switch is stored, so it survives a restart."
         }
+      },
+      "factory_reset": {
+        "title": "Reset to factory defaults",
+        "description": "Return the optimizer to the state of a fresh installation. Choose what to reset:\n\n- **Settings**: every setting on these pages (comfort, hot water, prices and fees, the thermal model, modes and features) goes back to its default. Your sensors and other assigned entities, the zones and emitters, the hot water tank, valve and furnace layout, the price source and the main fuse are kept, so the optimizer stays connected to your house.\n- **Learned values**: everything the optimizer has learned about your house is forgotten (heat loss, the lower floor's share, the comfort weight, COP, hot water cooling and use, defrost, the heat curve and the prediction accuracy history), and learning starts again from the settings.\n- **Both**.\n\nBefore anything changes, a snapshot is taken. Until the next weekly snapshot, about a week, the Restore learned snapshot action undoes the reset: the settings and learned values come back as they were, with your sensors as they are now. The integration then reloads and plans again straight away.",
+        "data": {
+          "scope": "What to reset",
+          "confirm": "Yes, reset"
+        },
+        "data_description": {
+          "scope": "Settings, learned values, or both.",
+          "confirm": "Nothing changes unless this is ticked: submitted unticked, the menu comes back."
+        }
       }
     },
     "error": {
@@ -1530,6 +1546,11 @@
       "flow_curve_needs_direct_plant": "Pricing the supply temperature lift is for a system with no mixing valve. With a valve the buffer tank's temperature already prices the lift, so this would count it twice. Set the valve to \"No mixing valve\" or turn this off.",
       "prefill_device_unreadable": "That device could not be read. Its integration has no mapping here yet, or none of its entities holds a value. Leave the device empty and name a Modbus package prefix instead.",
       "dhw_windows_day_selector": "This field already names its day, so enter plain times only, e.g. 06:00-08:30. Day selectors like 'weekdays' belong in the ordinary windows field above."
+    },
+    "abort": {
+      "factory_reset_done": "Reset done. The integration has reloaded and is planning again. To undo the reset, run the Restore learned snapshot action.",
+      "factory_reset_not_loaded": "The integration is not running, so there is nothing to reset. Fix what stopped it, then try again.",
+      "factory_reset_not_applied": "Not applied: Home Assistant refused to unload the integration, so nothing was changed. Try again, or restart Home Assistant first."
     }
   },
   "selector": {
@@ -1659,6 +1680,13 @@
         "observe": "Observe (log only)",
         "control": "Control (write mode and set-points)"
       }
+    },
+    "factory_reset_scope": {
+      "options": {
+        "settings": "Settings",
+        "learners": "Learned values",
+        "both": "Settings and learned values"
+      }
     }
   },
   "issues": {
@@ -2462,7 +2490,7 @@
     },
     "restore_learned_snapshot": {
       "name": "Restore Learned Snapshot",
-      "description": "Roll every learner back to the most recent weekly snapshot that was captured while all inputs were healthy and prediction accuracy was in band. Use this if the learned model has visibly gone wrong — after a sensor fed garbage for a while, for example. The drift watchdog does the same thing automatically when it can prove the inputs were healthy throughout; this service is the manual override for when you can see what it cannot. Nothing is lost permanently: learning simply continues from the restored point. The call fails with an error when no snapshot qualifies, instead of answering with an empty restore. With the source set to the heat-loss refit, it instead accepts the drift advisor's refit of the house heat-loss scale, offered while the drift alarm is raised and three settled days of evidence exist.",
+      "description": "Roll every learner back to the most recent weekly snapshot that was captured while all inputs were healthy and prediction accuracy was in band. Use this if the learned model has visibly gone wrong — after a sensor fed garbage for a while, for example. The drift watchdog does the same thing automatically when it can prove the inputs were healthy throughout; this service is the manual override for when you can see what it cannot. Nothing is lost permanently: learning simply continues from the restored point. The call fails with an error when no snapshot qualifies, instead of answering with an empty restore. With the source set to the heat-loss refit, it instead accepts the drift advisor's refit of the house heat-loss scale, offered while the drift alarm is raised and three settled days of evidence exist. Until the next weekly snapshot after a factory reset, it undoes that reset instead: the settings and learned values come back as they were before it, with the sensors and other entities as they are now.",
       "fields": {
         "entry_id": {
           "name": "Config entry",
@@ -2511,6 +2539,20 @@
           "description": "Restrict the action to one config entry. Leave empty to act on every configured heat pump."
         }
       }
+    },
+    "factory_reset": {
+      "name": "Reset to Factory Defaults",
+      "description": "Return one heat pump's settings, its learned values, or both to the state of a fresh installation. Sensors and other assigned entities, the zone, emitter, tank, valve and furnace layout, the price source and the main fuse are kept. A snapshot is taken first, and Restore learned snapshot undoes the reset until the next weekly snapshot. The integration reloads and plans again straight away.",
+      "fields": {
+        "entry_id": {
+          "name": "Config entry",
+          "description": "The config entry to reset."
+        },
+        "scope": {
+          "name": "Scope",
+          "description": "Settings, learned values, or both."
+        }
+      }
     }
   }
 }
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 809e65019..122da6029 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -442,6 +442,9 @@
     "run_optimization_no_prices": {
       "message": "Optimeringen kördes inte för {entry_ids}: det fanns färre än fyra elprissteg tillgängliga"
     },
+    "factory_reset_not_applied": {
+      "message": "Fabriksåterställningen av {entry_id} utfördes inte: Home Assistant vägrade avlasta posten; inget ändrades"
+    },
     "run_optimization_solve_failed": {
       "message": "Optimeringen kördes inte för {entry_ids}: lösaren misslyckades; felet finns i integrationens logg"
     },
@@ -529,7 +532,8 @@
           "learning_features": "Avancerade inlärningsfunktioner",
           "grid_connection": "Säkring och effekttak",
           "grid_fees": "Överföringsavgifter och avtal",
-          "heat_curve": "Värmekurvestyrning (ECL110)"
+          "heat_curve": "Värmekurvestyrning (ECL110)",
+          "factory_reset": "Återställ till fabriksinställningar"
         }
       },
       "setup_overview": {
@@ -1500,6 +1504,18 @@
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst.",
           "prefill_offer": "När det är på erbjuder en ny installation den här sidan om en värmepumpsenhet som lagts till i installationen kan fylla någon av de här inställningarna. Avstängt som standard: installationsguiden är oförändrad så länge det är av, och reglaget sparas, så det överlever en omstart."
         }
+      },
+      "factory_reset": {
+        "title": "Återställ till fabriksinställningar",
+        "description": "Återställ optimeraren till samma läge som en nyinstallation. Välj vad som ska återställas:\n\n- **Inställningar**: varje inställning på de här sidorna (komfort, varmvatten, priser och avgifter, den termiska modellen, lägen och funktioner) återgår till sitt standardvärde. Dina givare och andra tilldelade entiteter, zonerna och värmesystemen, uppställningen med varmvattentank, ventil och vedpanna, priskällan och huvudsäkringen behålls, så att optimeraren förblir ansluten till huset.\n- **Inlärda värden**: allt optimeraren har lärt sig om huset glöms (värmeförlusten, nedervåningens andel, komfortvikten, COP, varmvattnets avsvalning och förbrukning, avfrostning, värmekurvan och historiken för prognosträffsäkerhet), och inlärningen börjar om från inställningarna.\n- **Båda**.\n\nInnan något ändras tas en ögonblicksbild. Fram till nästa veckovisa ögonblicksbild, ungefär en vecka, ångrar åtgärden Återställ inlärd ögonblicksbild återställningen: inställningarna och de inlärda värdena kommer tillbaka som de var, med givarna som de är nu. Integrationen laddas sedan om och planerar på nytt direkt.",
+        "data": {
+          "scope": "Vad som ska återställas",
+          "confirm": "Ja, återställ"
+        },
+        "data_description": {
+          "scope": "Inställningar, inlärda värden eller båda.",
+          "confirm": "Ingenting ändras om inte detta är ikryssat: skickat utan kryss kommer menyn tillbaka."
+        }
       }
     },
     "error": {
@@ -1530,6 +1546,11 @@
       "price_entity_required": "En prissensor krävs när priskällan är en entitet.",
       "prefill_device_unreadable": "Enheten kunde inte läsas. Dess integration har ingen mappning här ännu, eller så har ingen av dess entiteter något värde. Lämna enheten tom och ange ett prefix för ett Modbus-paket i stället.",
       "dhw_windows_day_selector": "Fältet namnger redan sin dag — skriv bara tider, t.ex. 06:00-08:30. Dagväljare som 'weekdays' hör hemma i fältet för de vanliga fönstren ovan."
+    },
+    "abort": {
+      "factory_reset_done": "Återställningen är klar. Integrationen har laddats om och planerar igen. Kör åtgärden Återställ inlärd ögonblicksbild för att ångra återställningen.",
+      "factory_reset_not_loaded": "Integrationen körs inte, så det finns inget att återställa. Åtgärda det som stoppade den och försök igen.",
+      "factory_reset_not_applied": "Inte utförd: Home Assistant vägrade avlasta integrationen, så inget ändrades. Försök igen, eller starta om Home Assistant först."
     }
   },
   "selector": {
@@ -1659,6 +1680,13 @@
         "observe": "Observera (bara logg)",
         "control": "Styrning (skriv läge och börvärden)"
       }
+    },
+    "factory_reset_scope": {
+      "options": {
+        "settings": "Inställningar",
+        "learners": "Inlärda värden",
+        "both": "Inställningar och inlärda värden"
+      }
     }
   },
   "issues": {
@@ -2462,7 +2490,7 @@
     },
     "restore_learned_snapshot": {
       "name": "Återställ inlärd ögonblicksbild",
-      "description": "Rulla tillbaka varje inlärningsmodell till den senaste veckovisa ögonblicksbild som togs medan alla insignaler var friska och prognosträffsäkerheten låg inom sitt band. Använd detta om den inlärda modellen synbart har gått fel — till exempel efter att en givare matat skräp en tid. Driftvakten gör samma sak automatiskt när den kan bevisa att insignalerna var friska hela tiden; den här tjänsten är det manuella ingreppet för när du ser vad den inte kan se. Ingenting går förlorat permanent: inlärningen fortsätter helt enkelt från den återställda punkten. Anropet svarar med ett fel när ingen ögonblicksbild kvalificerar sig, i stället för att svara med en tom återställning. Med källan satt till värmeförlustens omanpassning godtar den i stället driftrådgivarens nyanpassade skala för husets värmeförlust, som erbjuds medan driftlarmet är aktivt och tre lugna dagar med underlag finns.",
+      "description": "Rulla tillbaka varje inlärningsmodell till den senaste veckovisa ögonblicksbild som togs medan alla insignaler var friska och prognosträffsäkerheten låg inom sitt band. Använd detta om den inlärda modellen synbart har gått fel — till exempel efter att en givare matat skräp en tid. Driftvakten gör samma sak automatiskt när den kan bevisa att insignalerna var friska hela tiden; den här tjänsten är det manuella ingreppet för när du ser vad den inte kan se. Ingenting går förlorat permanent: inlärningen fortsätter helt enkelt från den återställda punkten. Anropet svarar med ett fel när ingen ögonblicksbild kvalificerar sig, i stället för att svara med en tom återställning. Med källan satt till värmeförlustens omanpassning godtar den i stället driftrådgivarens nyanpassade skala för husets värmeförlust, som erbjuds medan driftlarmet är aktivt och tre lugna dagar med underlag finns. Fram till nästa veckovisa ögonblicksbild efter en fabriksåterställning ångrar den i stället den återställningen: inställningarna och de inlärda värdena kommer tillbaka som de var före den, med givarna och andra entiteter som de är nu.",
       "fields": {
         "entry_id": {
           "name": "Konfigurationspost",
@@ -2511,6 +2539,20 @@
           "description": "Begränsa åtgärden till en konfigurationspost. Lämna tomt för att agera på varje konfigurerad värmepump."
         }
       }
+    },
+    "factory_reset": {
+      "name": "Återställ till fabriksinställningar",
+      "description": "Återställ en värmepumps inställningar, dess inlärda värden eller båda till samma läge som en nyinstallation. Givare och andra tilldelade entiteter, uppställningen med zoner, värmesystem, tank, ventil och vedpanna, priskällan och huvudsäkringen behålls. En ögonblicksbild tas först, och Återställ inlärd ögonblicksbild ångrar återställningen fram till nästa veckovisa ögonblicksbild. Integrationen laddas om och planerar på nytt direkt.",
+      "fields": {
+        "entry_id": {
+          "name": "Konfigurationspost",
+          "description": "Konfigurationsposten som ska återställas."
+        },
+        "scope": {
+          "name": "Omfattning",
+          "description": "Inställningar, inlärda värden eller båda."
+        }
+      }
     }
   }
 }
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index c338468bd..98e184732 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -128,18 +128,18 @@
  {
   "id": "C15",
   "source": "README.md:## Services",
-  "claim": "14 services are registered under the heatpump_optimizer domain",
+  "claim": "15 services are registered under the heatpump_optimizer domain",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=14 measured=14",
+  "result": "documented=15 measured=15",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C16",
   "source": "docs/configuration.md:## Services",
-  "claim": "14 services are registered",
+  "claim": "15 services are registered",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=14 measured=14",
+  "result": "documented=15 measured=15",
   "verdict": "true",
   "truth": ""
  },
@@ -148,7 +148,7 @@
   "source": "README.md:## Services",
   "claim": "the Services table names exactly services.yaml's keys",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan']",
+  "result": "documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'factory_reset', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'factory_reset', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan']",
   "verdict": "true",
   "truth": ""
  },
@@ -173,9 +173,9 @@
  {
   "id": "C20",
   "source": "docs/configuration.md",
-  "claim": "nine services accept an optional entry_id",
+  "claim": "ten services accept an optional entry_id",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=9 measured=9",
+  "result": "documented=10 measured=10",
   "verdict": "true",
   "truth": ""
  },
@@ -193,7 +193,7 @@
   "source": "services.yaml",
   "claim": "every services.yaml `example` payload passes its own service schema",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "services with examples=9, failures=[]",
+  "result": "services with examples=10, failures=[]",
   "verdict": "true",
   "truth": ""
  },
@@ -202,7 +202,7 @@
   "source": "README.md:## Services",
   "claim": "the Returns column is each service's registered SupportsResponse (\u2014 = none, Always = ONLY, Optional = OPTIONAL)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented={'run_optimization': '\u2014', 'set_away': '\u2014', 'set_mode': '\u2014', 'set_thermal_parameters': '\u2014', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'reset_heat_loss_learners': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'reset_heat_loss_learners': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[]",
+  "result": "documented={'run_optimization': '\u2014', 'set_away': '\u2014', 'set_mode': '\u2014', 'set_thermal_parameters': '\u2014', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'reset_heat_loss_learners': 'Optional', 'factory_reset': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'reset_heat_loss_learners': 'optional', 'factory_reset': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[]",
   "verdict": "true",
   "truth": ""
  },
@@ -227,45 +227,45 @@
  {
   "id": "C26",
   "source": "README.md",
-  "claim": "a menu of 23 pages",
+  "claim": "a menu of 24 pages",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=23 measured=23",
+  "result": "documented=24 measured=24",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C27",
   "source": "docs/configuration.md",
-  "claim": "There are 23 pages",
+  "claim": "There are 24 pages",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=23 measured=23",
+  "result": "documented=24 measured=24",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C28",
   "source": "docs/configuration.md",
-  "claim": "eight on the first menu and fifteen more behind Advanced settings",
+  "claim": "eight on the first menu and sixteen more behind Advanced settings",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=(8, 15) measured=(8, 15)",
+  "result": "documented=(8, 16) measured=(8, 16)",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C29",
   "source": "docs/architecture.md:module map",
-  "claim": "config_flow.py -- Setup flow plus 23 option pages behind two menus",
+  "claim": "config_flow.py -- Setup flow plus 24 option pages behind two menus",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=23 measured=23",
+  "result": "documented=24 measured=24",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C30",
   "source": "docs/configuration.md",
-  "claim": "every documented Default (92 rows) is the default the rendered options page actually carries",
+  "claim": "every documented Default (93 rows) is the default the rendered options page actually carries",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "92 compared, mismatches=[]",
+  "result": "93 compared, mismatches=[]",
   "verdict": "true",
   "truth": ""
  },
@@ -326,18 +326,18 @@
  {
   "id": "C37",
   "source": "docs/architecture.md:module map",
-  "claim": "__init__.py -- the 14 services",
+  "claim": "__init__.py -- the 15 services",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=14 measured=14",
+  "result": "documented=15 measured=15",
   "verdict": "true",
   "truth": ""
  },
  {
   "id": "C38",
   "source": "docs/architecture.md:module map",
-  "claim": "services.yaml -- The 14 service definitions",
+  "claim": "services.yaml -- The 15 service definitions",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=14 measured=14",
+  "result": "documented=15 measured=15",
   "verdict": "true",
   "truth": ""
  },
@@ -1118,9 +1118,9 @@
  {
   "id": "C125",
   "source": "strings.json:selector",
-  "claim": "every SelectSelector option on every options page has a translated label (44 selects)",
+  "claim": "every SelectSelector option on every options page has a translated label (45 selects)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "44 selects, untranslated=[]",
+  "result": "45 selects, untranslated=[]",
   "verdict": "true",
   "truth": ""
  }
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index a76f49f3b..3a93e4214 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -18,30 +18,30 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C12 | `README.md:### Binary Sensors` | the binary-sensor table names exactly the binary sensors the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] measured=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
 | C13 | `README.md:### Buttons` | the button table names exactly the buttons the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Reset Heat Loss', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] measured=['Learning Finalize Debug Collection', 'Learning Reset Comfort Weight', 'Learning Reset Heat Loss', 'Learning Run System Identification', 'Optimize Now', 'Prediction Accuracy Diagnose Last Interval'] | **true** |  |
 | C14 | `README.md:Switches` | Optimizer Active, Away, Block DHW, Block Space Heating, DHW Boost and Boost Space Heating are the switches | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] measured=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
-| C15 | `README.md:## Services` | 14 services are registered under the heatpump_optimizer domain | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
-| C16 | `docs/configuration.md:## Services` | 14 services are registered | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
-| C17 | `README.md:## Services` | the Services table names exactly services.yaml's keys | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] | **true** |  |
+| C15 | `README.md:## Services` | 15 services are registered under the heatpump_optimizer domain | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
+| C16 | `docs/configuration.md:## Services` | 15 services are registered | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
+| C17 | `README.md:## Services` | the Services table names exactly services.yaml's keys | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'factory_reset', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] measured=['apply_manual_plan', 'apply_schedule', 'apply_topology', 'assign_entity', 'clear_manual_plan', 'debug_collect', 'diagnose_interval', 'factory_reset', 'reset_heat_loss_learners', 'restore_learned_snapshot', 'run_optimization', 'set_away', 'set_mode', 'set_thermal_parameters', 'simulate_plan'] | **true** |  |
 | C18 | `README.md + docs/configuration.md` | set_thermal_parameters takes 31 fields | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=31 measured=31 | **true** |  |
 | C19 | `docs/configuration.md` | simulate_plan takes 19 optional fields | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=19 measured=19 | **true** |  |
-| C20 | `docs/configuration.md` | nine services accept an optional entry_id | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=9 measured=9 | **true** |  |
+| C20 | `docs/configuration.md` | ten services accept an optional entry_id | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=10 measured=10 | **true** |  |
 | C21 | `services.yaml` | services.yaml documents exactly the fields each voluptuous schema accepts | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | symmetric differences={}, catalogue gap=[] | **true** |  |
-| C22 | `services.yaml` | every services.yaml `example` payload passes its own service schema | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | services with examples=9, failures=[] | **true** |  |
-| C23 | `README.md:## Services` | the Returns column is each service's registered SupportsResponse (— = none, Always = ONLY, Optional = OPTIONAL) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented={'run_optimization': '—', 'set_away': '—', 'set_mode': '—', 'set_thermal_parameters': '—', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'reset_heat_loss_learners': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'reset_heat_loss_learners': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[] | **true** |  |
+| C22 | `services.yaml` | every services.yaml `example` payload passes its own service schema | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | services with examples=10, failures=[] | **true** |  |
+| C23 | `README.md:## Services` | the Returns column is each service's registered SupportsResponse (— = none, Always = ONLY, Optional = OPTIONAL) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented={'run_optimization': '—', 'set_away': '—', 'set_mode': '—', 'set_thermal_parameters': '—', 'simulate_plan': 'Always', 'apply_schedule': 'Optional', 'apply_manual_plan': 'Optional', 'clear_manual_plan': 'Optional', 'restore_learned_snapshot': 'Optional', 'reset_heat_loss_learners': 'Optional', 'factory_reset': 'Optional', 'diagnose_interval': 'Optional', 'debug_collect': 'Optional', 'assign_entity': 'Optional', 'apply_topology': 'Optional'}, registered={'run_optimization': 'none', 'set_mode': 'none', 'set_away': 'none', 'set_thermal_parameters': 'none', 'simulate_plan': 'only', 'apply_schedule': 'optional', 'assign_entity': 'optional', 'apply_topology': 'optional', 'apply_manual_plan': 'optional', 'clear_manual_plan': 'optional', 'restore_learned_snapshot': 'optional', 'reset_heat_loss_learners': 'optional', 'factory_reset': 'optional', 'diagnose_interval': 'optional', 'debug_collect': 'optional'}, mismatches=[] | **true** |  |
 | C24 | `docs/configuration.md` | assign_entity's `key` is one of 21 assignable configuration keys, listed | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['buffer_tank_temp_entity', 'dhw_temp_entity', 'external_heat_entity', 'floor_return_temp_entity', 'heat_pump_defrost_entity', 'heat_pump_energy_entity', 'heat_pump_fault_entity', 'heat_pump_mode_entity', 'heat_pump_online_entity', 'heat_pump_power_entity', 'heat_pump_switch_entity', 'house_power_entity', 'indoor_temp_entity', 'lower_floor_temp_entity', 'mixing_valve_target_entity', 'outdoor_temp_entity', 'pv_production_entity', 'solar_radiation_entity', 'valve_outlet_temp_entity', 'wood_tank_bottom_entity', 'wood_tank_top_entity'] measured=['buffer_tank_temp_entity', 'dhw_temp_entity', 'external_heat_entity', 'floor_return_temp_entity', 'heat_pump_defrost_entity', 'heat_pump_energy_entity', 'heat_pump_fault_entity', 'heat_pump_mode_entity', 'heat_pump_online_entity', 'heat_pump_power_entity', 'heat_pump_switch_entity', 'house_power_entity', 'indoor_temp_entity', 'lower_floor_temp_entity', 'mixing_valve_target_entity', 'outdoor_temp_entity', 'pv_production_entity', 'solar_radiation_entity', 'valve_outlet_temp_entity', 'wood_tank_bottom_entity', 'wood_tank_top_entity'] | **true** |  |
 | C25 | `docs/configuration.md` | the count in that sentence is 21 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=21 measured=21 | **true** |  |
-| C26 | `README.md` | a menu of 23 pages | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=23 measured=23 | **true** |  |
-| C27 | `docs/configuration.md` | There are 23 pages | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=23 measured=23 | **true** |  |
-| C28 | `docs/configuration.md` | eight on the first menu and fifteen more behind Advanced settings | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(8, 15) measured=(8, 15) | **true** |  |
-| C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 23 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=23 measured=23 | **true** |  |
-| C30 | `docs/configuration.md` | every documented Default (92 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 92 compared, mismatches=[] | **true** |  |
+| C26 | `README.md` | a menu of 24 pages | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
+| C27 | `docs/configuration.md` | There are 24 pages | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
+| C28 | `docs/configuration.md` | eight on the first menu and sixteen more behind Advanced settings | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(8, 16) measured=(8, 16) | **true** |  |
+| C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 24 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
+| C30 | `docs/configuration.md` | every documented Default (93 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 93 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (101 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 101 compared, mismatches=[] | **true** |  |
 | C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=84 measured=84 | **true** |  |
 | C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=84, listed=84, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=28 measured=28 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'issues.py', 'legionella.py', 'notifier.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'issues.py', 'legionella.py', 'notifier.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
-| C37 | `docs/architecture.md:module map` | __init__.py -- the 14 services | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
-| C38 | `docs/architecture.md:module map` | services.yaml -- The 14 service definitions | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=14 measured=14 | **true** |  |
+| C37 | `docs/architecture.md:module map` | __init__.py -- the 15 services | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
+| C38 | `docs/architecture.md:module map` | services.yaml -- The 15 service definitions | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
 | C39 | `docs/architecture.md:module map` | sensor.py -- 62 sensors | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=62 measured=62 | **true** |  |
 | C40 | `docs/architecture.md:module map` | switch.py -- the comment names every switch the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'], the platform constructs ['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
 | C41 | `docs/architecture.md:module map` | binary_sensor.py -- the comment names every binary sensor the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'], the platform constructs ['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
@@ -128,4 +128,4 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C122 | `docs/configuration.md` | set_mode takes auto, comfort, economy, boost or off | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['auto', 'boost', 'comfort', 'economy', 'off'] measured=['auto', 'boost', 'comfort', 'economy', 'off'] | **true** |  |
 | C123 | `DISCLAIMER.md` | the licence is MIT | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C124 | `DISCLAIMER.md` | the disclaimer states the software is not a safety device and carries no warranty | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 'not a safety device' present=True, 'no warranty' present=True | **true** |  |
-| C125 | `strings.json:selector` | every SelectSelector option on every options page has a translated label (44 selects) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 44 selects, untranslated=[] | **true** |  |
+| C125 | `strings.json:selector` | every SelectSelector option on every options page has a translated label (45 selects) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 45 selects, untranslated=[] | **true** |  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index a5cef8fd7..74549895f 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -51,7 +51,7 @@ against a document that is CORRECT.
     RESULT claims_false=0
     RESULT claims_stale=0
     RESULT claims_unverifiable=2    (1 with --links; the checker runs the default)
-    RESULT config_defaults_compared=92   (76 until #937's rows landed; 82
+    RESULT config_defaults_compared=93   (76 until #937's rows landed; 82
                                          until #1067's solver half documented
                                          the flow-curve lift option's default;
                                          83 until #1067's silent-mode half
@@ -73,7 +73,10 @@ against a document that is CORRECT.
                                          on the Comfort and temperatures table;
                                          92 with R10-USER-DOCS-FINAL, which
                                          gives every options field a row of
-                                         its own under its page)
+                                         its own under its page; 93 with
+                                         R10-FACTORY-RESET's "What to reset",
+                                         a select Default row on the Reset to
+                                         factory defaults table)
     RESULT config_ranges_compared=101    (76 until #937's rows landed; 86
                                          until #1067's silent-mode half
                                          documented the derate's range; 87
@@ -520,6 +523,7 @@ SCHEMAS = {
     "restore_learned_snapshot": svc.SERVICE_SCHEMA_RESTORE_SNAPSHOT,
     "diagnose_interval": svc.SERVICE_SCHEMA_DIAGNOSE_INTERVAL,
     "reset_heat_loss_learners": svc.SERVICE_SCHEMA_RESET_HEAT_LOSS,
+    "factory_reset": svc.SERVICE_SCHEMA_FACTORY_RESET,
     "debug_collect": svc.SERVICE_SCHEMA_DEBUG_COLLECT,
 }
 # The label is the sentence's own number, as C26's is: a label frozen at
diff --git a/dev/programme/delivery/3047.md b/dev/programme/delivery/3047.md
new file mode 100644
index 000000000..18a8adfb5
--- /dev/null
+++ b/dev/programme/delivery/3047.md
@@ -0,0 +1 @@
+- [#3047](https://github.com/tvofi/heatpump_optimizer/pull/3047) — **open**, R10-FACTORY-RESET: factory reset (R10-FACTORY-RESET)
diff --git a/docs/architecture.md b/docs/architecture.md
index ac2500895..347cba965 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -105,13 +105,13 @@ Read the diagram as four regions.
 
 ```text
 custom_components/heatpump_optimizer/
-├── __init__.py           # Setup and unload, the 14 services, entry migrations
+├── __init__.py           # Setup and unload, the 15 services, entry migrations
 ├── const.py              # Every config key, default and tuning constant
 ├── entry_config.py       # The entry's configuration, parsed once: one default
 │                         #   and one coercion per key
 ├── store.py              # The store-load boundary: a Store whose loads refuse
 │                         #   non-finite numeric leaves
-├── config_flow.py        # Setup flow plus 23 option pages behind two menus
+├── config_flow.py        # Setup flow plus 24 option pages behind two menus
 ├── coordinator.py        # The update loop: read, fetch, solve, actuate, learn, publish
 ├── payload.py            # The typed contract of the payload the coordinator publishes
 ├── notifier.py           # The documented events, fired from the payload on each update
@@ -229,7 +229,7 @@ custom_components/heatpump_optimizer/
 │                         #   Boost Space Heating, DHW Boost, Optimizer Active
 ├── datetime.py           # The away-override return instant, as one datetime entity
 ├── frontend.py           # Serves and registers the Lovelace card
-├── services.py           # The domain's 14 services: schemas, handlers and registration
+├── services.py           # The domain's 15 services: schemas, handlers and registration
 ├── debugger.py           # A week of cycle rows for one entry, kept across a
 │                         #   reload and carried by Download diagnostics
 ├── replay_doc.py         # The replay document's allowlist and sanitiser, one
@@ -240,7 +240,7 @@ custom_components/heatpump_optimizer/
 ├── www/                  # The dashboard card, one self-contained file
 ├── brand/                # Icon and logo
 ├── icon.png              # Integration icon
-├── services.yaml         # The 14 service definitions
+├── services.yaml         # The 15 service definitions
 ├── strings.json          # UI strings
 ├── translations/
 │   ├── en.json           # English
diff --git a/docs/configuration.md b/docs/configuration.md
index 37c815d39..3bb603b97 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -6,7 +6,7 @@ YAML — the integration is configured entirely through Home Assistant's UI, and
 this page follows the same order the UI does.
 
 - [Initial setup](#initial-setup) — the questions asked once, when you add the integration
-- [Changing settings later](#changing-settings-later) — the 23 options pages behind two menus
+- [Changing settings later](#changing-settings-later) — the 24 options pages behind two menus
 - [The hydronic layout catalog](#the-hydronic-layout-catalog) — which plumbing arrangements are modelled
 - [Services](#services) — every service and its fields
 
@@ -317,9 +317,10 @@ opens this screen. Enter a valid token and price updates resume.
 
 **Settings → Devices & services → Heat Pump Optimizer → Configure.**
 
-There are **23 pages**: eight on the first menu, and fifteen more behind
+There are **24 pages**: eight on the first menu, and sixteen more behind
 **Advanced settings**. One of the eight — *Your system, as configured* — is
-read-only. Each page saves on its own, so changing one setting never touches
+read-only, and the last advanced page, *Reset to factory defaults*, is an
+action behind a confirmation rather than settings. Each page saves on its own, so changing one setting never touches
 another page's values. Every page also ends with one shared navigation
 control, described once here rather than twenty-three times below:
 
@@ -355,6 +356,7 @@ control, described once here rather than twenty-three times below:
 | Fuse and peak guards | Main fuse, the fuse cap, the live peak guard, the heat pump's silent mode |
 | Transfer fees and contract | DSO product, per-kWh fees, the fixed-contract comparison |
 | Heat curve control (ECL110) | MQTT topics and displace limits |
+| Reset to factory defaults | The settings, the learned values, or both, back to a fresh installation; undone by `restore_learned_snapshot` |
 
 ### Your system, as configured
 
@@ -1003,6 +1005,38 @@ is set — an install without an ECL110 never touches these topics. See
 | Largest upward offset | 20 °C | 0–30, 0.5 steps | How far it may be shifted up when storing cheap heat. |
 | Controller response time | 1.5 h | 0.25–6.0, 0.25 steps | Roughly how long the controller takes to act on a new offset, so the optimizer does not ask for changes faster than the system can follow. |
 
+### Reset to factory defaults
+
+Returns the entry to the state of a fresh installation. Pick the scope and
+tick the confirmation; submitted unticked, the menu comes back and nothing
+changes, and closing the dialog cancels.
+
+| Setting | Default | Choices | What it means |
+|---|---|---|---|
+| What to reset | Settings and learned values | Settings · Learned values · Settings and learned values | Which half of the entry goes back to a fresh installation, or both. |
+| Yes, reset | off | on/off | The confirmation. Nothing changes unless it is ticked. |
+
+- **Settings**: every setting on these pages returns to its default. Kept, so
+  the optimizer stays connected to the house: every assigned entity, the zone
+  and emitter topology (the two-zone switch is written as the settings in force
+  imply it), the hot-water tank, valve and wood-furnace layout, the price and
+  solar-forecast sources and the Tibber token, the plant diagram, the ECL110
+  MQTT wiring, the pre-fill device and the main fuse.
+- **Learned values**: every learner starts again from the settings: the heat
+  loss scale and lower-floor ratio, the comfort weight, COP, buffer and hot
+  water cooling, the hot water profile and draws, defrost, the heat curve, the
+  price shape, the plant learners and the prediction accuracy history. The
+  billed peaks, the energy ledger, the operating mode, the frequency
+  watchdog's stand-down and any manual plan or override are kept.
+- **Both**.
+
+A snapshot of every learned store and of the settings the reset drops is taken
+first. Until the next weekly snapshot, about a week, `restore_learned_snapshot`
+undoes the reset, with the sensors as they are now, and puts the two-zone,
+hot-water and wood-furnace switches back as they were stored. The entry then
+reloads and plans again straight away. If Home Assistant refuses to unload the
+entry, the dialog says the reset was not applied, and nothing is changed.
+
 ---
 
 ## The hydronic layout catalog
@@ -1067,11 +1101,12 @@ feeding the buffer tank — its heat is folded in rather than stored separately.
 
 ## Services
 
-14 services are registered under the `heatpump_optimizer` domain. The nine
-that act on a specific config entry also accept an optional `entry_id`; omitting
-it applies the call to every loaded entry, which is what a single-heat-pump
-install wants. Of those nine, `assign_entity`, `apply_topology`,
-`apply_schedule` and `debug_collect` write configuration back into the entry —
+15 services are registered under the `heatpump_optimizer` domain. The ten
+that act on a specific config entry also accept an `entry_id`: optional on
+nine, where omitting it applies the call to every loaded entry, which is what a
+single-heat-pump install wants, and required on `factory_reset`. Of those ten,
+`assign_entity`, `apply_topology`, `apply_schedule`, `debug_collect` and
+`factory_reset` write configuration back into the entry —
 `debug_collect`'s start turns the collection option on, which reloads the
 entry — and the other five act on the running coordinator. `run_optimization`,
 `set_away`, `set_mode`, `set_thermal_parameters` and `simulate_plan` always act
@@ -1096,6 +1131,7 @@ or is not loaded — fails with a validation error rather than doing nothing.
 | `clear_manual_plan` | `entry_id` | optional |
 | `restore_learned_snapshot` | `entry_id` | optional |
 | `reset_heat_loss_learners` | `learners`, `entry_id` | optional |
+| `factory_reset` | `entry_id`, `scope` (both required) | optional |
 | `diagnose_interval` | `entry_id` | optional |
 | `debug_collect` | `action` (required), `entry_id` | optional |
 
@@ -1210,7 +1246,8 @@ breach a hard floor, and the legionella clock is never skipped.
 weekly snapshot — the manual counterpart of the drift watchdog. When no
 snapshot qualifies (healthy inputs and in-band accuracy at capture time are
 required) the call fails with an error instead of answering with an empty
-restore.
+restore. Until the next weekly snapshot after a factory reset, it undoes that
+reset instead: every learned store and the dropped settings come back.
 **`reset_heat_loss_learners`** returns the learned house heat loss scale and the
 learned lower floor loss ratio to 1.0, so the plan uses the heat loss values in
 the settings as they stand, and the learners start collecting evidence again
@@ -1220,6 +1257,11 @@ comfort weight and the hot-water, COP and defrost learners are left alone. The
 **Learning Reset Heat Loss** button resets both. Changing the indoor or the
 lower-floor temperature sensor resets the learner fitted on it the same way,
 because evidence fitted against one sensor says nothing about another.
+**`factory_reset`** returns one entry's `scope` — `settings`, `learners` or
+`both` — to its defaults, exactly as
+[Reset to factory defaults](#reset-to-factory-defaults) does, and answers with
+the entry and the scope; if Home Assistant refuses to unload the entry, the call
+fails and nothing is changed. Within a week of it, `restore_learned_snapshot` undoes it.
 **`diagnose_interval`** attributes the last interval's temperature error
 input by input and publishes the result on the Prediction Accuracy sensor.
 **`debug_collect`** takes `action`: `start`, `stop` or `status`. Collect a week of debug data is the learning page's option that turns the collection on. `start` turns
diff --git a/docs/setup.md b/docs/setup.md
index 0d22cbfe7..ebd69f721 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -258,7 +258,7 @@ defaults once you confirm one last overview of what will be created:
 on purpose — it is a sensor this setup could use and does not have.*
 
 Everything the overview shows can be changed afterwards: open the integration
-and choose **Configure**, which presents the 23 options pages described in
+and choose **Configure**, which presents the 24 options pages described in
 [configuration.md](configuration.md#changing-settings-later) — with **Quick
 setup** among the everyday pages, for an install that wants to answer the
 house questions now — and the
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index e038b02eb..6b0b58a37 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -1573,6 +1573,7 @@ async def options_menus():
             "grid_connection",
             "grid_fees",
             "heat_curve",
+            "factory_reset",
         ],
         str(list(advanced.get("menu_options", {}))),
     )
@@ -4087,6 +4088,10 @@ async def registry_drives_every_page():
     # one source the fresh form's defaults and derive's fallbacks also read,
     # so the allowance cannot drift from the fields the page renders).
     transient["quick_setup"] = set(quick_setup.SHIPPED_ANSWERS)
+    # R10-FACTORY-RESET: the reset's scope and its confirmation are read once
+    # and never stored -- the page aborts the flow after the reset, so nothing
+    # reaches the entry's options. Keyed on the production schema.
+    transient["factory_reset"] = {str(key) for key in config_flow._FACTORY_RESET_SCHEMA.schema}
     # The rest of that page's fields are not its own declarations but the
     # building pages': the questionnaire's one field list serves two flows by
     # design (``_questionnaire_fields``), and the two wood probes are the
@@ -5763,6 +5768,53 @@ async def untouched_option_pages_do_not_reload():
     )
 
 
+def _a5_refusals(shown_pages, current):
+    """(pages read, refusals): each shown form's schema applied to
+    ``option_resubmit``'s payload, the a5 walk's own."""
+    read, refused = 0, []
+    for step, shown in shown_pages:
+        if shown.get("type") != "form":
+            continue
+        read += 1
+        try:
+            shown["data_schema"](_nightly.option_resubmit(step, current))
+        except vol.Invalid as err:
+            refused.append(f"{step}: {err}")
+    return read, refused
+
+
+async def nightly_a5_resubmits_fit_every_page():
+    """`tests/nightly_ha.py`'s a5 walk posts `option_resubmit`'s payload to
+    every options page, and real Home Assistant validates it against the
+    page's shown schema before the handler runs. The stub validates nothing,
+    so a page whose schema refuses that payload -- the factory-reset page and
+    its after-save key, #3047 -- reached only the nightly lane as
+    `a5:pages_ok`'s `InvalidData`. Here the shown schema is applied to the
+    same payload, through the same function, for every page in the table."""
+    R.section("options: the nightly a5 walk's resubmit fits every page's schema")
+    shown_pages = []
+    for page in config_flow._OPTION_PAGES:
+        flow, entry, _ = fresh_options()
+        shown_pages.append((page.step, await getattr(flow, f"async_step_{page.step}")(None)))
+    current = {**dict(entry.data), **dict(entry.options)}
+    read, refused = _a5_refusals(shown_pages, current)
+    forms = sum(shown.get("type") == "form" for _, shown in shown_pages)
+    R.check(
+        "every options page's shown schema accepts the a5 walk's untouched resubmit, every form page read",
+        not refused and read == forms and read >= 20,
+        f"refused {refused[:4]}; read {read} of {forms} form page(s)",
+    )
+    # Null control, through the same reader: a page whose schema refuses the
+    # payload (a planted required field) is reported, so the sweep can refuse.
+    planted = ("factory_reset", {"type": "form", "data_schema": vol.Schema({vol.Required("planted"): str})})
+    p_read, p_refused = _a5_refusals([*shown_pages, planted], current)
+    R.check(
+        "null control: a planted page whose schema refuses the payload is read and refused by the same sweep",
+        p_read == read + 1 and len(p_refused) == len(refused) + 1 and "planted" in p_refused[-1],
+        f"read {p_read}, refused {p_refused[-1:]}",
+    )
+
+
 # ---------------------------------------------------------------------------
 # #1067 W1067-G7: the Modbus pre-fill page. One step answered three times:
 # the prefix, then the suggestions to edit, then the save. The entity ids are
@@ -7692,6 +7744,7 @@ async def main() -> int:
     await reconfigure_flow()
     await absent_fallbacks_are_proven()
     await untouched_option_pages_do_not_reload()
+    await nightly_a5_resubmits_fit_every_page()
     await options_modbus_prefill()
     await options_device_prefill()
     await config_flow_quick_setup()
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index d288b59a7..706e5caeb 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -1250,7 +1250,7 @@ def check_prose_tree_counts() -> None:
     # module counts are the false ones and this control's assertion is not
     # about them.
     stale = {
-        name: text.replace("the 23 options pages", "the 26 options pages", 1)
+        name: text.replace(f"the {facts['options_pages']} options pages", "the 99 options pages", 1)
         for name, text in CORPUS.items()
     }
     rows, _ = prose_count_census(stale, facts)
diff --git a/tests/entities.py b/tests/entities.py
index 526b84b2d..bcd4754e9 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -9087,8 +9087,10 @@ for _step in options._MENU_LABELS:
     if not _sresult.get("menu_options"):
         _odd_outcomes.append(f"{_step}: menu without menu_options")
         continue
-    if _step == "setup_overview":
-        # The one read-only page: back to the menu with nothing written.
+    if _step in ("setup_overview", "factory_reset"):
+        # The one read-only page: back to the menu with nothing written. And
+        # the factory reset (R10-FACTORY-RESET): untouched, it is unconfirmed,
+        # which is the menu back with nothing written -- its null control.
         if _sf._entry.options or _sf.hass.config_entries.updated:
             _unwritten_menus.append(_step)
         continue
@@ -15421,6 +15423,27 @@ R.check(
 )
 
 _heat_loss_reset = _svc_call(const.SERVICE_RESET_HEAT_LOSS, {"learners": ["lower_floor_loss_ratio"]})
+# The factory reset's handler (R10-FACTORY-RESET) hands the entry's coordinator
+# and the scope to ``coordinator.async_factory_reset``; the reset itself is
+# features.py's, over real stores.
+from heatpump_optimizer import services as _svc_module  # noqa: E402
+
+_svc_fr_real, _svc_fr_args = _svc_module.async_factory_reset, []
+
+
+async def _svc_fr_record(coord, scope):
+    _svc_fr_args.append((coord, scope))
+
+
+_svc_module.async_factory_reset = _svc_fr_record
+_svc_fr = _svc_call(const.SERVICE_FACTORY_RESET, {"entry_id": _svc_entry.entry_id, "scope": "learners"})
+_svc_module.async_factory_reset = _svc_fr_real
+R.check(
+    "factory_reset hands that entry's coordinator its scope and reports both",
+    _svc_fr_args == [(_svc_coord, "learners")]
+    and _svc_fr == {"reset": _svc_entry.entry_id, "scope": "learners"},
+    str(_svc_fr),
+)
 R.check(
     "reset_heat_loss_learners reaches the coordinator and reports what it reset",
     "reset_heat_loss" in _svc_log
@@ -15466,6 +15489,7 @@ _svc_covered = {
     const.SERVICE_DIAGNOSE_INTERVAL,
     const.SERVICE_DEBUG_COLLECT,
     const.SERVICE_RESET_HEAT_LOSS,
+    const.SERVICE_FACTORY_RESET,
 }
 R.check(
     "every registered service was invoked above",
@@ -40488,6 +40512,9 @@ _R10_LOG_ALLOWED_BY_REASON = {
         ("coordinator.py", "_async_load_thermal_learning"): 1,
         ("coordinator.py", "_async_setup_peak_guard"): 1,
         ("coordinator.py", "async_restore_learned_snapshot"): 1,
+        # R10-FACTORY-RESET: one line per reset the user asked for, applied
+        # or refused by Home Assistant's unload.
+        ("coordinator.py", "async_factory_reset"): 1,
         ("coordinator.py", "_thermal_param_changes"): 1, ("coordinator.py", "async_simulate"): 1,
         ("coordinator.py", "async_adopt_heat_loss_refit"): 1, ("coordinator.py", "async_shutdown"): 1,
     },
diff --git a/tests/features.py b/tests/features.py
index 327ec8d41..7fd3d9c3f 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -13164,6 +13164,570 @@ R.check(
 )
 
 
+# --- R10-FACTORY-RESET: settings, learners or both back to their defaults -----
+#
+# The owner's request (tvofi, 2026-10-30). Real coordinators over a two-zone
+# house with its wiring assigned, set up again the way the reset sets them up
+# (every learned store's loader), each expectation a property: kept keys
+# unchanged, every other setting reading its declared default, every learner
+# reading what a coordinator that never learned reads, and the undo point
+# putting both back.
+import ast as _fr_ast  # noqa: E402
+import dataclasses as _fr_dc  # noqa: E402
+from pathlib import Path as _FrPath  # noqa: E402
+
+from homeassistant.helpers import storage as _fr_storage  # noqa: E402
+from homeassistant.util import dt as _fr_dt  # noqa: E402
+from harness import FakeEntry as _fr_entry_cls, FakeServiceCall as _fr_call  # noqa: E402
+from heatpump_optimizer import config_flow as _fr_flow  # noqa: E402
+from heatpump_optimizer import const as _fr_const  # noqa: E402
+from heatpump_optimizer import entry_config as _fr_ec  # noqa: E402
+from heatpump_optimizer import services as _fr_services  # noqa: E402
+from heatpump_optimizer.coordinator import (  # noqa: E402
+    _FACTORY_VOID as _FR_VOID,
+    async_factory_reset as _fr_reset,
+)
+from heatpump_optimizer.wood_fuel import wood_furnace_on as _fr_wood  # noqa: E402
+
+R.section("A factory reset returns settings, learners or both to their defaults")
+
+_FR_THERMAL_KEYS, _FR_ACC_KEYS = dict(_FR_VOID)["thermal_learning"], dict(_FR_VOID)["accuracy"]
+
+_FR_DATA = dict(_ra_house(two_zone=True), name="My pump", indoor_temp_entity="sensor.indoor",
+                lower_floor_temp_entity="sensor.lower", outdoor_temp_entity="sensor.outdoor",
+                dhw_temp_entity="sensor.dhw", price_source="entity", price_entity="sensor.price",
+                main_fuse_amperes=20, upper_floor_emitter="radiator")
+_FR_OPTS = {"comfort_weight": 3.0, "target_temperature": 22.5, "price_weight": 2.0,
+            "heat_pump_cop_nominal": 3.9, "dhw_setpoint": 58.0, "freq_control_mode": "observe"}
+#: The wiring the body lists, key by key: the reset keeps exactly these.
+_FR_LISTED = {
+    "name", "compressor_freq_sensor", "price_source", "tibber_token", "solar_forecast_source",
+    "two_zone_mode", "upper_floor_emitter", "lower_floor_emitter", "dhw_enabled",
+    "wood_furnace_enabled", "dhw_wood_coil_enabled", "mixing_valve_mode",
+    "mixing_valve_write_target_kind", "space_setpoint_unit", "topology_layout",
+    "topology_positions", "ecl110_command_topic", "ecl110_displace_set_topic",
+    "ecl110_state_topic", "ecl110_mqtt_qos", "ecl110_mqtt_retain", "modbus_prefill_prefix",
+    "main_fuse_amperes", "main_fuse_phases",
+}
+#: Every key a ``CONF_`` constant names (a tuple names several: the weekday
+#: hot-water windows), and Home Assistant's own ``name``.
+_FR_OPTION_KEYS = {key for name, v in vars(_fr_const).items() if name.startswith("CONF_")
+                   for key in ((v,) if isinstance(v, str) else v if isinstance(v, tuple) else ())} | {"name"}
+_FR_ENTITY_KEYS = {k for k in _FR_OPTION_KEYS if k.endswith("_entity")}
+
+
+async def _fr_boot(hass, entry):
+    """What the reset's ``async_setup`` builds: a coordinator over every learned store."""
+    c = Coord(hass, entry)
+    for load in (c._dhw_learner.async_load_profile, c._dhw_learner.async_load_draws,
+                 c._async_load_thermal_learning, c._async_load_price_model,
+                 c._async_load_accuracy, c._async_load_snapshots):
+        await load()
+    entry.runtime_data, entry.state = c, _li_state.LOADED
+    return c
+
+
+def _fr_learn(c):
+    """Every learner the owner names moved off its initial state, saved by its own saver."""
+    c._apply_house_heat_loss_scale(1.4)
+    c._apply_lower_floor_loss_ratio(1.3)
+    c._house_heat_loss_samples, c._lower_floor_loss_samples = 60, 40
+    c._apply_cop_scale(1.13)
+    c._cop_samples = 20
+    c._apply_buffer_cooling_rate(c._buffer_cooling_rate * 1.5)
+    c._buffer_cooling_samples = 9
+    c._comfort_learner.evidence = -1.4
+    c._dhw_learner.apply_cooling_rate(c._dhw_learner.cooling_rate * 1.4)
+    c._dhw_learner.cooling_samples = 7
+    c._dhw_learner.hourly_profile = c._dhw_learner.normalize_profile([1.0] * 12 + [3.0] * 12)
+    c._defrost.factors[0][0] = 0.8
+    c._curve_learner.bias = -0.6
+    c._freq_fallback = True  # a fact the reset keeps: the watchdog's latch
+    c._accuracy.lead_sigma[1.0], c._accuracy.lead_counts[1.0] = 0.3, 12
+    c._price_learner.model.shapes[0][3] = 1.2
+    c._dhw_learner.draw_stats.fold(_fr_dt.now(), "06:00-09:00", 2.5)
+    _aio.run(c._async_save_thermal_learning())
+    _aio.run(c._dhw_learner.async_save_profile())
+    _aio.run(c._dhw_learner.async_save_draws())
+    _aio.run(c._async_save_accuracy())
+    _aio.run(c._async_save_price_model())
+
+
+def _fr_disk(entry_id):
+    """Every stored document of the entry, as the stub writes it."""
+    prefix = f"{_fr_const.DOMAIN}_{entry_id}_"
+    return {k[len(prefix):]: _fi_json.loads(v) for k, v in _fr_storage._DISK.items() if k.startswith(prefix)}
+
+
+def _fr_learned(c):
+    """The learners' persisted shapes without the save stamp and the watchdog's
+    latch, a fact the reset keeps (pinned on its own below)."""
+    out = c._learner_snapshot_payloads()
+    out["thermal_learning"] = {k: v for k, v in out["thermal_learning"].items()
+                               if k not in ("updated_at", "freq_fallback")}
+    return out
+
+
+def _fr_case(scope, entry_id, *, learn=True):
+    """Reset a learned entry under ``scope``; (before, after, entry, hass, old coordinator)."""
+    hass = FakeHass({})
+    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id=entry_id)
+    hass.config_entries.entries.append(entry)
+    c = _aio.run(_fr_boot(hass, entry))
+    if learn:
+        _fr_learn(c)
+    before = {"learned": _fr_learned(c), "disk": _fr_disk(entry_id), "config": {**entry.data, **entry.options}}
+
+    async def _setup(eid):
+        hass.config_entries.set_up.append(eid)
+        before.setdefault("at_setup", _fr_disk(entry_id))
+        await _fr_boot(hass, entry)
+        return True
+
+    hass.config_entries.async_setup = _setup
+    _aio.run(_fr_reset(c, scope))
+    return before, entry, hass, c
+
+
+def _fr_fresh(entry, entry_id):
+    """A coordinator that never learned, over the configuration the reset left."""
+    return _aio.run(_fr_boot(FakeHass({}), _fr_entry_cls(data=dict(entry.data), options=dict(entry.options),
+                                                       entry_id=entry_id)))
+
+
+# The enumeration: every option key the integration names, by its constants.
+R.check(
+    "the kept keys are the listed wiring and every entity assignment, each an option key",
+    set(_fr_ec.FACTORY_KEPT) == _FR_LISTED | _FR_ENTITY_KEYS
+    and set(_fr_ec.FACTORY_KEPT) <= _FR_OPTION_KEYS and len(_FR_ENTITY_KEYS) > 30,
+    f"kept-not-listed {sorted(set(_fr_ec.FACTORY_KEPT) - _FR_LISTED - _FR_ENTITY_KEYS)}, "
+    f"listed-not-kept {sorted((_FR_LISTED | _FR_ENTITY_KEYS) - set(_fr_ec.FACTORY_KEPT))}",
+)
+
+_fr_s_before, _fr_s_entry, _fr_s_hass, _fr_s_old = _fr_case("settings", "fr_settings")
+_fr_s_after = {**_fr_s_entry.data, **_fr_s_entry.options}
+_fr_s_new = _fr_s_entry.runtime_data
+_fr_parsed = _fr_ec.EntryConfig.from_mapping(_fr_s_after)
+_fr_not_default = sorted(
+    f.name for f in _fr_dc.fields(_fr_ec.EntryConfig)
+    if f.metadata and f.name not in _fr_ec.FACTORY_KEPT and getattr(_fr_parsed, f.name) != f.default
+)
+R.check(
+    "after a settings reset every tunable option reads its default",
+    not _fr_not_default and set(_fr_s_after) <= set(_fr_ec.FACTORY_KEPT),
+    f"not default {_fr_not_default}, stored beyond the wiring {sorted(set(_fr_s_after) - set(_fr_ec.FACTORY_KEPT))}",
+)
+_fr_kept_moved = sorted(k for k in _fr_s_before["config"] if k in _fr_ec.FACTORY_KEPT
+                        and _fr_s_after.get(k) != _fr_s_before["config"][k])
+R.check(
+    "after a settings reset every kept key is unchanged, and the topology it implied with it",
+    not _fr_kept_moved
+    and _fr_s_new._thermal_params.two_zone_enabled is _fr_s_old._thermal_params.two_zone_enabled is True
+    and _fr_s_new._thermal_params.dhw_enabled is _fr_s_old._thermal_params.dhw_enabled is True
+    and _fr_wood(_fr_s_after) == _fr_wood(_fr_s_before["config"]),
+    f"moved {_fr_kept_moved}, two-zone {_fr_s_new._thermal_params.two_zone_enabled}",
+)
+_fr_s_disk = _fr_disk("fr_settings")
+
+
+def _fr_unstamped(doc):
+    return {k: v for k, v in (doc or {}).items() if k != "updated_at"}
+
+
+# The reload is an options change, and a learner answers it as it answers any
+# options edit (a changed nameplate re-anchors or voids its own learner); what
+# the reset itself owes is to write no learned store.
+_fr_s_setup = _fr_s_before["at_setup"]
+R.check(
+    "a settings reset writes no learned store: each is as it was when the entry is set up again",
+    all(_fr_unstamped(_fr_s_setup.get(k)) == _fr_unstamped(_fr_s_before["disk"].get(k))
+        for k in ("thermal_learning", "dhw_profile", "price_model", "accuracy"))
+    and _fr_s_hass.config_entries.unloaded == _fr_s_hass.config_entries.set_up == ["fr_settings"],
+    str([k for k in ("thermal_learning", "dhw_profile", "price_model", "accuracy")
+         if _fr_unstamped(_fr_s_setup.get(k)) != _fr_unstamped(_fr_s_before["disk"].get(k))]),
+)
+
+_fr_l_before, _fr_l_entry, _fr_l_hass, _ = _fr_case("learners", "fr_learners")
+_fr_l_fresh = _fr_fresh(_fr_l_entry, "fr_learners_fresh")
+_fr_l_got, _fr_l_want = _fr_learned(_fr_l_entry.runtime_data), _fr_learned(_fr_l_fresh)
+_fr_named = ("thermal_learning", "dhw_profile", "comfort", "defrost", "accuracy", "price_model")
+R.check(
+    "the learned state before the reset is not the initial one, learner by learner (the control)",
+    all(_fr_l_before["learned"][k] != _fr_l_want[k] for k in _fr_named),
+    str([k for k in _fr_named if _fr_l_before["learned"][k] == _fr_l_want[k]]),
+)
+R.check(
+    "after a learners reset every learner reads what one that never learned reads",
+    _fr_l_got == _fr_l_want
+    and _fr_l_entry.runtime_data._dhw_accuracy.as_dict() == _fr_l_fresh._dhw_accuracy.as_dict()
+    and _li_state_of(_fr_l_entry.runtime_data) == (1.0, 1.0, 0, 0),
+    str({k: sorted(f for f in set(v) | set(_fr_l_want[k]) if v.get(f) != _fr_l_want[k].get(f))
+         for k, v in _fr_l_got.items() if v != _fr_l_want[k]}),
+)
+# The void list, key by key, against a list this test owns rather than
+# ``_FACTORY_VOID`` itself (an enumeration read from the list it checks pins
+# nothing): every key a learned store holds is a learner the reset drops, or
+# one of these facts it keeps. The heat-loss pair stays, voided by its own
+# path; the rest is the anchors, the meter's last COP, snow memory, the
+# frequency watchdog's latch, the billed peaks, the mode and the save stamp.
+_FR_FACTS = {
+    "thermal_learning": {
+        "house_heat_loss_scale", "house_heat_loss_samples", "lower_floor_loss_ratio",
+        "lower_floor_loss_samples", "house_heat_loss_anchor", "house_heat_loss_basis",
+        "lower_floor_loss_anchor", "heat_loss_zone_entities", "measured_cop", "snow_accum_cm",
+        "snow_accum_last", "last_heavy_snow", "freq_fallback", "updated_at",
+    },
+    "accuracy": {"peaks", "mode"},
+    "dhw_profile": set(), "dhw_draws": set(), "price_model": set(),
+}
+_fr_l_setup = _fr_l_before["at_setup"]
+_fr_learned_keys = sorted((n, k) for n, facts in _FR_FACTS.items()
+                          for k in (_fr_l_before["disk"].get(n) or {}) if k not in facts)
+R.check(
+    "before a learners reset every learned store is on disk and holds learned keys beyond its facts (the control)",
+    all(_fr_l_before["disk"].get(n) for n in _FR_FACTS)
+    and {n for n, _ in _fr_learned_keys} == set(_FR_FACTS) and len(_fr_learned_keys) >= 25,
+    f"stores absent {sorted(n for n in _FR_FACTS if not _fr_l_before['disk'].get(n))}, "
+    f"{len(_fr_learned_keys)} learned key(s)",
+)
+_fr_left = [(n, k) for n, k in _fr_learned_keys if k in (_fr_l_setup.get(n) or {})]
+_fr_facts_lost = sorted((n, k) for n, facts in _FR_FACTS.items() for k in facts
+                        if k in (_fr_l_before["disk"].get(n) or {}) and k not in (_fr_l_setup.get(n) or {}))
+R.check(
+    "a learners reset drops every learned key, key by key, and keeps every fact, before the entry is set up again",
+    not _fr_left and not _fr_facts_lost
+    and not any(n in _fr_l_setup for n, facts in _FR_FACTS.items() if not facts),
+    f"learned left {_fr_left}, facts lost {_fr_facts_lost}, "
+    f"whole stores left {sorted(n for n, f in _FR_FACTS.items() if not f and n in _fr_l_setup)}",
+)
+_fr_l_disk = _fr_disk("fr_learners")
+R.check(
+    "a learners reset keeps the settings and the stores' facts: the watchdog latch, peaks, mode",
+    {**_fr_l_entry.data, **_fr_l_entry.options} == _fr_l_before["config"]
+    and _fr_l_entry.runtime_data._freq_fallback is True
+    and _fr_l_disk["accuracy"].get("peaks") == _fr_l_before["disk"]["accuracy"].get("peaks")
+    and _fr_l_disk["accuracy"].get("mode") == _fr_l_before["disk"]["accuracy"].get("mode"),
+    f"freq_fallback {_fr_l_entry.runtime_data._freq_fallback}",
+)
+
+_fr_b_before, _fr_b_entry, _fr_b_hass, _ = _fr_case("both", "fr_both")
+_fr_b_new = _fr_b_entry.runtime_data
+_fr_b_fresh = _fr_fresh(_fr_b_entry, "fr_both_fresh")
+R.check(
+    "a reset of both leaves the wiring alone and every learner at its initial state",
+    _fr_learned(_fr_b_new) == _fr_learned(_fr_b_fresh)
+    and set({**_fr_b_entry.data, **_fr_b_entry.options}) <= set(_fr_ec.FACTORY_KEPT)
+    and _fr_b_entry.data["indoor_temp_entity"] == "sensor.indoor",
+    f"stored {sorted({**_fr_b_entry.data, **_fr_b_entry.options})}",
+)
+_fr_undo = _fr_b_new._snapshot_ring.snapshots[-1]
+R.check(
+    "the drift rollback never takes the reset's undo point; the restore does, while it is newest",
+    "before_reset" in _fr_undo and _fr_b_new._snapshot_ring.best_restore() is not _fr_undo
+    and _fr_b_new._snapshot_ring.undo_target() is _fr_undo,
+    f"undo {sorted(_fr_undo)}",
+)
+
+
+def _fr_counting_refresh(c):
+    """Record every refresh asked of ``c``: an undo asks the coordinator it unloaded for none."""
+    asked = []
+
+    async def _refresh(*_a, **_k):
+        asked.append(c)
+
+    c.async_request_refresh = _refresh
+    return asked
+
+
+_fr_b_reset_cfg = {**_fr_b_entry.data, **_fr_b_entry.options}
+R.check(
+    "the house is auto-mode before the reset and pinned two-zone by it (the undo's control)",
+    "two_zone_mode" not in _fr_b_before["config"] and _fr_b_reset_cfg.get("two_zone_mode") == "on",
+    f"before {_fr_b_before['config'].get('two_zone_mode')!r}, reset {_fr_b_reset_cfg.get('two_zone_mode')!r}",
+)
+_fr_b_asked = _fr_counting_refresh(_fr_b_new)
+_fr_restored = _aio.run(_fr_b_new.async_restore_learned_snapshot())
+_fr_undone = _fr_b_entry.runtime_data
+R.check(
+    "restore_learned_snapshot undoes the reset: every learner, the accuracy history and the settings exactly as before it",
+    _fr_restored is True and _fr_undone is not _fr_b_new and _fr_learned(_fr_undone) == _fr_b_before["learned"]
+    and _li_state_of(_fr_undone) == (1.4, 1.3, 60, 40)
+    and {**_fr_b_entry.data, **_fr_b_entry.options} == _fr_b_before["config"],
+    str({k: sorted(f for f in set(v) | set(_fr_b_before["learned"][k]) if v.get(f) != _fr_b_before["learned"][k].get(f))
+         for k, v in _fr_learned(_fr_undone).items() if v != _fr_b_before["learned"][k]})
+    + f" config moved {sorted(k for k in set(_fr_b_before['config']) | set({**_fr_b_entry.data, **_fr_b_entry.options}) if _fr_b_before['config'].get(k) != {**_fr_b_entry.data, **_fr_b_entry.options}.get(k))}",
+)
+R.check(
+    "the undo asks the coordinator it unloaded for nothing more: no refresh, no learner applied after it",
+    _fr_b_asked == [] and _fr_b_entry.runtime_data is _fr_undone,
+    f"refreshes asked {len(_fr_b_asked)}",
+)
+# The undo's pins, as stored: an explicit value, and one stored on the other
+# side (data versus options), each come back where and as they were.
+_FR_PIN_DATA = {"name": "x", "two_zone_mode": "auto", "comfort_weight": 3.0, "indoor_temp_entity": "sensor.in"}
+_FR_PIN_OPTS = {"dhw_enabled": False, "target_temperature": 22.0}
+_fr_pin_reset = _fr_ec.factory_settings(_FR_PIN_DATA, _FR_PIN_OPTS, two_zone=True, dhw=True, wood=False)
+_fr_pin_record = _fi_json.loads(_fi_json.dumps(_fr_ec.undo_point("both", _FR_PIN_DATA, _FR_PIN_OPTS)))
+R.check(
+    "an undo puts each pinned key back where and as it was stored, over the pins the reset wrote",
+    _fr_pin_reset != (_FR_PIN_DATA, _FR_PIN_OPTS)
+    and _fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record) == (_FR_PIN_DATA, _FR_PIN_OPTS),
+    f"reset {_fr_pin_reset}, undone {_fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record)}",
+)
+# A record missing either half, or holding a half that is not a (data,
+# options) pair, undoes no settings: the reset that wrote it kept them, or the
+# record is not one an undo point writes.
+_fr_pin_malformed = {
+    name: _fr_ec.undone_settings(*_fr_pin_reset, record)
+    for name, record in (
+        ("no pins", {k: v for k, v in _fr_pin_record.items() if k != "pinned"}),
+        ("no settings", {k: v for k, v in _fr_pin_record.items() if k != "settings"}),
+        ("one side", {**_fr_pin_record, "pinned": [{}]}),
+        ("not dicts", {**_fr_pin_record, "settings": [[], []]}),
+    )
+}
+R.check(
+    "an undo record missing either half, or holding a malformed one, undoes no settings",
+    all(v is None for v in _fr_pin_malformed.values())
+    and _fr_ec.undone_settings(*_fr_pin_reset, _fr_pin_record) is not None,
+    str({k: v is None for k, v in _fr_pin_malformed.items()}),
+)
+R.check(
+    "the spent undo point stays as an ordinary snapshot, so a second restore is the ordinary one",
+    not any("before_reset" in snap for snap in _fr_undone._snapshot_ring.snapshots)
+    and len(_fr_undone._snapshot_ring.snapshots) == 1,
+)
+
+
+# The undo of a learners reset: its record carries no settings, and the
+# settings are left exactly as they are.
+_fr_lu_before, _fr_lu_entry, _, _ = _fr_case("learners", "fr_undo_learners")
+_fr_lu_new = _fr_lu_entry.runtime_data
+_fr_lu_record = _fr_lu_new._snapshot_ring.snapshots[-1].get("before_reset", {})
+_fr_counting_refresh(_fr_lu_new)
+_fr_lu_ok = _aio.run(_fr_lu_new.async_restore_learned_snapshot())
+R.check(
+    "restore_learned_snapshot undoes a learners reset: every learner back, the settings untouched",
+    _fr_lu_ok is True and "settings" not in _fr_lu_record and _fr_lu_record.get("scope") == "learners"
+    and _fr_learned(_fr_lu_entry.runtime_data) == _fr_lu_before["learned"]
+    and _li_state_of(_fr_lu_entry.runtime_data) == (1.4, 1.3, 60, 40)
+    and {**_fr_lu_entry.data, **_fr_lu_entry.options} == _fr_lu_before["config"],
+    f"record {sorted(_fr_lu_record)}, restored {_fr_lu_ok}",
+)
+
+
+async def _fr_failed_unload(scope="both"):
+    """An unload Home Assistant refuses: the reset changes nothing but the undo point."""
+    hass = FakeHass({})
+    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id="fr_no_unload")
+    hass.config_entries.entries.append(entry)
+    c = await _fr_boot(hass, entry)
+    c._apply_house_heat_loss_scale(1.4)
+    c._apply_lower_floor_loss_ratio(1.3)
+    c._house_heat_loss_samples, c._lower_floor_loss_samples = 60, 40
+    await c._async_save_thermal_learning()
+    disk = _fr_disk("fr_no_unload")
+
+    async def _refuse(eid):
+        hass.config_entries.unloaded.append(eid)
+        return False
+
+    hass.config_entries.async_unload = _refuse
+    import logging as _fr_logging
+    from heatpump_optimizer import coordinator as _fr_coord_mod
+
+    said = []
+    handler = _fr_logging.Handler()
+    handler.emit = lambda record: said.append(record.getMessage())
+    _fr_coord_mod._LOGGER.addHandler(handler)
+    try:
+        done = await _fr_reset(c, scope)
+    finally:
+        _fr_coord_mod._LOGGER.removeHandler(handler)
+    after = {k: v for k, v in _fr_disk("fr_no_unload").items() if k != "snapshots"}
+    return entry, hass.config_entries, (disk, after), c, (done, said)
+
+
+_fr_nu_entry, _fr_nu_mgr, _fr_nu_disk, _fr_nu_c, (_fr_nu_done, _fr_nu_said) = _aio.run(_fr_failed_unload())
+R.check(
+    "a refused unload changes nothing but the undo point: settings, every store and the heat-loss pair as before",
+    _fr_nu_done is False
+    and {**_fr_nu_entry.data, **_fr_nu_entry.options} == {**_FR_DATA, **_FR_OPTS}
+    and _fr_nu_mgr.set_up == []
+    and all(_fr_unstamped(_fr_nu_disk[1].get(k)) == _fr_unstamped(v) for k, v in _fr_nu_disk[0].items() if k != "snapshots")
+    and _li_state_of(_fr_nu_c) == (1.4, 1.3, 60, 40)
+    and "before_reset" in _fr_nu_c._snapshot_ring.snapshots[-1]
+    and any("not applied" in m for m in _fr_nu_said) and not any(" applied;" in m for m in _fr_nu_said),
+    f"done {_fr_nu_done}, said {_fr_nu_said}, set up {_fr_nu_mgr.set_up}, heat loss {_li_state_of(_fr_nu_c)}, "
+    f"stores moved {sorted(k for k, v in _fr_nu_disk[0].items() if k != 'snapshots' and _fr_unstamped(_fr_nu_disk[1].get(k)) != _fr_unstamped(v))}",
+)
+_fr_nu_c.hass.config_entries.async_unload = _fr_nu_mgr.async_unload
+_fr_nu_undo = _aio.run(_fr_nu_c.async_restore_learned_snapshot())
+R.check(
+    "a refused unload refuses the undo too, and the undo point stays the undo point",
+    _fr_nu_undo is False and "before_reset" in _fr_nu_c._snapshot_ring.snapshots[-1]
+    and _fr_nu_mgr.set_up == [],
+    f"undo {_fr_nu_undo}",
+)
+# Once a weekly snapshot is newer, the restore is the ordinary one again.
+_fr_w_before, _fr_w_entry, _, _ = _fr_case("learners", "fr_weekly")
+_fr_w_ring = _fr_w_entry.runtime_data._snapshot_ring
+_fr_w_ring.take(_fr_dt.now(), _fr_w_entry.runtime_data._learner_snapshot_payloads(), {}, True)
+R.check(
+    "a weekly snapshot newer than the undo point takes the restore back from it",
+    _fr_w_ring.undo_target() is _fr_w_ring.snapshots[-1] and "before_reset" not in _fr_w_ring.snapshots[-1]
+    and "before_reset" in _fr_w_ring.snapshots[-2],
+)
+
+
+async def _fr_flow_case(user_input, entry_id, *, loaded=True):
+    hass = FakeHass({})
+    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id=entry_id)
+    hass.config_entries.entries.append(entry)
+    if loaded:
+        await _fr_boot(hass, entry)
+    flow = _fr_flow.HeatPumpOptimizerOptionsFlow(entry)
+    flow.hass = hass
+    disk = _fr_disk(entry_id)
+    config = ({**entry.data}, {**entry.options})
+    first = await flow.async_step_factory_reset()
+    second = await flow.async_step_factory_reset(user_input) if user_input is not None else None
+    changed = (_fr_disk(entry_id) != disk, ({**entry.data}, {**entry.options}) != config)
+    return first, second, changed, hass.config_entries
+
+
+_fr_cancel = _aio.run(_fr_flow_case({"scope": "both", "confirm": False}, "fr_flow_cancel"))
+R.check(
+    "the options step shows the scope and the confirmation; unconfirmed, nothing changes (null control)",
+    _fr_cancel[0]["type"] == "form" and _fr_cancel[0]["step_id"] == "factory_reset"
+    and set(map(str, _fr_cancel[0]["data_schema"].schema)) == {"scope", "confirm"}
+    and _fr_cancel[1]["type"] == "menu" and _fr_cancel[1]["step_id"] == "advanced"
+    and _fr_cancel[2] == (False, False) and _fr_cancel[3].unloaded == [] and _fr_cancel[3].set_up == [],
+    f"{_fr_cancel[1]}, changed {_fr_cancel[2]}",
+)
+_fr_go = _aio.run(_fr_flow_case({"scope": "both", "confirm": True}, "fr_flow_go"))
+R.check(
+    "confirmed, the options step resets, sets the entry up again and closes",
+    _fr_go[1]["type"] == "abort" and _fr_go[1]["reason"] == "factory_reset_done"
+    and _fr_go[2] == (True, True) and _fr_go[3].unloaded == ["fr_flow_go"] == _fr_go[3].set_up,
+    f"{_fr_go[1]}, changed {_fr_go[2]}",
+)
+
+
+async def _fr_flow_refused():
+    hass = FakeHass({})
+    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id="fr_flow_refused")
+    hass.config_entries.entries.append(entry)
+    await _fr_boot(hass, entry)
+
+    async def _refuse(eid):
+        return False
+
+    hass.config_entries.async_unload = _refuse
+    flow = _fr_flow.HeatPumpOptimizerOptionsFlow(entry)
+    flow.hass = hass
+    await flow.async_step_factory_reset()
+    shown = await flow.async_step_factory_reset({"scope": "both", "confirm": True})
+    try:
+        await _fr_services.handle_factory_reset(hass, _fr_call(
+            "heatpump_optimizer", "factory_reset",
+            _fr_services.SERVICE_SCHEMA_FACTORY_RESET({"entry_id": "fr_flow_refused", "scope": "learners"})))
+        raised = None
+    except Exception as err:  # HomeAssistantError
+        raised = err
+    return shown, raised
+
+
+_fr_refused = _aio.run(_fr_flow_refused())
+R.check(
+    "a refused unload is said as not applied, by the options step and by the service, never as done",
+    _fr_refused[0]["type"] == "abort" and _fr_refused[0]["reason"] == "factory_reset_not_applied"
+    and getattr(_fr_refused[1], "translation_key", None) == "factory_reset_not_applied"
+    and all(_fi_json.loads(_FrPath(p).read_text())["options"]["abort"].get("factory_reset_not_applied")
+            and _fi_json.loads(_FrPath(p).read_text())["exceptions"]["factory_reset_not_applied"]["message"]
+            for p in ("custom_components/heatpump_optimizer/strings.json",
+                      "custom_components/heatpump_optimizer/translations/en.json",
+                      "custom_components/heatpump_optimizer/translations/sv.json")),
+    f"{_fr_refused[0]}, raised {_fr_refused[1]!r}",
+)
+_fr_off = _aio.run(_fr_flow_case({"scope": "both", "confirm": True}, "fr_flow_off", loaded=False))
+R.check(
+    "an entry that is not running is not reset, confirmed or not",
+    _fr_off[1]["type"] == "abort" and _fr_off[1]["reason"] == "factory_reset_not_loaded"
+    and _fr_off[2] == (False, False) and _fr_off[3].unloaded == [],
+    f"{_fr_off[1]}, changed {_fr_off[2]}",
+)
+R.check(
+    "the advanced menu offers the reset, labelled by the translations",
+    "factory_reset" in _fr_flow.HeatPumpOptimizerOptionsFlow._ADVANCED_MENU
+    and all(_fi_json.loads(_FrPath(p).read_text())["options"]["step"]["advanced"]["menu_options"].get("factory_reset")
+            for p in ("custom_components/heatpump_optimizer/strings.json",
+                      "custom_components/heatpump_optimizer/translations/en.json",
+                      "custom_components/heatpump_optimizer/translations/sv.json")),
+)
+
+_fr_svc_refused = []
+for _fr_bad in ({"scope": "both"}, {"entry_id": "x", "scope": "everything"}, {"entry_id": "x"}):
+    try:
+        _fr_services.SERVICE_SCHEMA_FACTORY_RESET(_fr_bad)
+    except Exception:  # vol.Invalid
+        _fr_svc_refused.append(sorted(_fr_bad))
+
+
+async def _fr_service():
+    hass = FakeHass({})
+    entry = _fr_entry_cls(data=dict(_FR_DATA), options=dict(_FR_OPTS), entry_id="fr_svc")
+    hass.config_entries.entries.append(entry)
+    await _fr_boot(hass, entry)
+    answer = await _fr_services.handle_factory_reset(hass, _fr_call(
+        "heatpump_optimizer", "factory_reset",
+        _fr_services.SERVICE_SCHEMA_FACTORY_RESET({"entry_id": "fr_svc", "scope": "settings"})))
+    return answer, hass.config_entries, {**entry.data, **entry.options}
+
+
+_fr_svc = _aio.run(_fr_service())
+R.check(
+    "the service needs an entry and a known scope, and resets that entry",
+    len(_fr_svc_refused) == 3 and _fr_svc[0] == {"reset": "fr_svc", "scope": "settings"}
+    and _fr_svc[1].unloaded == ["fr_svc"] and set(_fr_svc[2]) <= set(_fr_ec.FACTORY_KEPT),
+    f"refused {_fr_svc_refused}, answer {_fr_svc[0]}",
+)
+
+# The store enumeration: every store the integration persists, by the AST walk
+# finite_boundary.py's arm 1 uses, each with its disposition.
+_FR_STORES = {
+    "thermal_learning": "voided: learned keys dropped, the heat-loss pair by its void path",
+    "accuracy": "voided: accuracy, dhw_accuracy, defrost, comfort; peaks and mode are facts",
+    "price_model": "voided",
+    "dhw_profile": "voided",
+    "dhw_draws": "voided",
+    "snapshots": "kept: the undo point lives here",
+    "ledger": "kept: billed energy",
+    "energy": "kept: metered totals",
+    "manual_plan": "kept: the user's own override",
+    "away": "kept: the user's own override",
+    "boost": "kept: the user's own override",
+    "dhw_legionella": "kept: the last disinfection, a safety fact",
+    "notifier": "kept: which notices were sent",
+    "pump_duty": "kept: what was last written to the pump",
+    "debug": "kept: a diagnostics collection",
+}
+_fr_found = set()
+for _fr_p in sorted(_FrPath("custom_components/heatpump_optimizer").glob("*.py")):
+    for _fr_n in _fr_ast.walk(_fr_ast.parse(_fr_p.read_text())):
+        if (isinstance(_fr_n, _fr_ast.Call) and isinstance(_fr_n.func, _fr_ast.Name)
+                and _fr_n.func.id == "QuarantiningStore"):
+            for _fr_arg in _fr_n.args:
+                if isinstance(_fr_arg, _fr_ast.JoinedStr):
+                    _fr_found.add(_fr_arg.values[-1].value.lstrip("_"))
+R.check(
+    "every store the integration persists has a factory-reset disposition",
+    _fr_found == set(_FR_STORES) and len(_fr_found) >= 15,
+    f"undispositioned {sorted(_fr_found - set(_FR_STORES))}, stale {sorted(set(_FR_STORES) - _fr_found)}",
+)
+
+
 R.section("Runtime parameter updates")
 
 import asyncio
@@ -25158,6 +25722,7 @@ _SVC_KEYS = {
     "restore_learned_snapshot_no_snapshot": ({"entry_ids"}, "hae"),
     "restore_learned_snapshot_no_refit": ({"entry_ids"}, "hae"),
     "set_thermal_params_invalid_dhw_windows": ({"windows", "error"}, "sve"),
+    "factory_reset_not_applied": ({"entry_id"}, "hae"),
 }
 
 
@@ -25205,6 +25770,15 @@ def _svc_check(name, outcome, key):
     R.check(name, not _svc_why(outcome, key), _svc_why(outcome, key) or "ok")
 
 
+# factory_reset's refusal, driven in the R10-FACTORY-RESET section through
+# the real service handler over an unload Home Assistant refuses.
+_svc_check(
+    "factory_reset over an unload Home Assistant refuses raises a translated operational failure",
+    ("raised", _fr_refused[1]) if _fr_refused[1] is not None else ("returned", None),
+    "factory_reset_not_applied",
+)
+
+
 # The driven state: one loaded entry, its coordinator holding no prices, no
 # plan and no snapshot -- what a fresh install (or a dead price feed) looks
 # like from a service call.
@@ -25669,6 +26243,7 @@ _HPO_MOVED = (
     "handle_restore_snapshot",
     "handle_diagnose_interval",
     "handle_reset_heat_loss",
+    "handle_factory_reset",
     "_manual_targets",
     "_loaded_entries",
     "_loaded_coordinators",
@@ -25740,6 +26315,7 @@ _HPO_SERVICE_MAP = {
     "diagnose_interval": "handle_diagnose_interval",
     "debug_collect": "handle_debug_collect",
     "reset_heat_loss_learners": "handle_reset_heat_loss",
+    "factory_reset": "handle_factory_reset",
 }
 _hpo_hass = FakeHass()
 _asyncio.run(_ha_setup_component(_integ, _hpo_hass))
@@ -37949,6 +38525,8 @@ _ET_KEYS = {
     # D10-s1-03: the refused token, through _raise_auth_failed.
     "tibber_auth_failed": {"error"},
     "debug_collect_inactive": {"entry_id"},
+    # R10-FACTORY-RESET: an unload Home Assistant refuses.
+    "factory_reset_not_applied": {"entry_id"},
 }
 
 
@@ -38022,7 +38600,8 @@ _et_check(
 # schema accepts, in both refusing states. Its preconditions: it drives the
 # whole catalog, each action's payload reaches the handler without an
 # entry_id, and the only refusal it accepts from a schema is of entry_id
-# itself (five actions act on every loaded entry and take none).
+# itself (five actions act on every loaded entry and take none;
+# factory_reset requires one).
 import voluptuous as _ger_vol  # noqa: E402
 
 #: The fields an action's schema requires; any other's smallest payload is {}.
@@ -38031,6 +38610,7 @@ _GER_REQUIRED = {
     "debug_collect": {"action": "status"},
     "assign_entity": {"key": "outdoor_temp_entity", "entity_id": ""},
     "apply_topology": {"layout": "no_valve"},
+    "factory_reset": {"scope": "settings"},
 }
 _ger_actions = sorted(_et_idle.services.async_services()[_DOMAIN])
 _ger_bad, _ger_unreached = [], []
@@ -38043,7 +38623,9 @@ for _ger_name in _ger_actions:
         try:
             _ger_err = _et_call(_et_idle, _ger_name, _ger_payload)
         except _ger_vol.Invalid as _ger_inv:
-            if "entry_id" not in _ger_payload or {
+            # A refusal of entry_id alone: an action taking none refuses the
+            # ghost, and factory_reset, which requires one, refuses its absence.
+            if {
                 tuple(_e.path) for _e in getattr(_ger_inv, "errors", [_ger_inv])
             } != {("entry_id",)}:
                 _ger_unreached.append(f"{_ger_name}: {_ger_inv}")
@@ -49914,6 +50496,16 @@ R.check(
     "parse, and a 140 % humidity selects a defrost bucket that does not "
     "describe any weather",
 )
+R.check(
+    "the range's two ends are humidities: 0 % and 100 % are read, just past either is refused",
+    _t6_humidity([{"humidity": 0, "datetime": _T6_HUM_NOW.isoformat()}]) == 0.0
+    and _t6_humidity([{"humidity": 100, "datetime": _T6_HUM_NOW.isoformat()}]) == 100.0
+    and _t6_humidity([{"humidity": 100.01, "datetime": _T6_HUM_NOW.isoformat()}]) is None
+    and _t6_humidity([{"humidity": -0.01, "datetime": _T6_HUM_NOW.isoformat()}]) is None,
+    f"0 -> {_t6_humidity([{'humidity': 0, 'datetime': _T6_HUM_NOW.isoformat()}])!r}, "
+    f"100 -> {_t6_humidity([{'humidity': 100, 'datetime': _T6_HUM_NOW.isoformat()}])!r} "
+    "-- a saturated or bone-dry forecast is weather, so the bounds are inclusive",
+)
 
 
 # -- `_shutdown_process_pool`: a shutdown that must not raise -------------
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 86133618a..8a7898c2d 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -58,7 +58,7 @@
 #
 # v7.1.0: Round-10 merge train: claim-carry barrier, train admission, COP gate and part-load, Health tab, Marketplace. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
-config_flow # r10-wood-notify: the wood_lighting_lead_minutes option joins the seeded wood group; one key added, no value moved
+config_flow # r10-wood-notify: the wood_lighting_lead_minutes option joins the seeded wood group; one key added, no value moved; R10-FACTORY-RESET: the factory_reset options page joins the advanced menu (16 entries, was 15), its two transient fields (scope, confirm) and its seeded copy; keys added, no value moved
 #
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index 7309e0d95..087fe7e60 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -985,6 +985,10 @@
    [
     "heat_curve",
     "Heat curve control (ECL110)"
+   ],
+   [
+    "factory_reset",
+    "Reset to factory defaults"
    ]
   ],
   "init": [
@@ -1036,6 +1040,7 @@
   "compressor_freq_entity": "sensor.seed_compressor_freq_entity",
   "compressor_freq_sensor": "sensor.seed_compressor_freq_sensor",
   "confidence_margins_enabled": true,
+  "confirm": true,
   "curve_learning_enabled": true,
   "debug_collect_enabled": true,
   "dhw_disinfection_switch_entity": "sensor.seed_dhw_disinfection_switch_entity",
@@ -2308,6 +2313,24 @@
     "selector": "SelectSelector"
    }
   },
+  "factory_reset": {
+   "confirm": {
+    "config": null,
+    "default": "False",
+    "required": "Required",
+    "selector": "BooleanSelector"
+   },
+   "scope": {
+    "config": {
+     "mode": "'dropdown'",
+     "options": "['settings', 'learners', 'both']",
+     "translation_key": "'factory_reset_scope'"
+    },
+    "default": "'both'",
+    "required": "Required",
+    "selector": "SelectSelector"
+   }
+  },
   "grid": {
    "after_save": {
     "config": {
@@ -4881,6 +4904,24 @@
    "selector": "SelectSelector"
   }
  },
+ "factory_reset": {
+  "confirm": {
+   "config": null,
+   "default": "False",
+   "required": "Required",
+   "selector": "BooleanSelector"
+  },
+  "scope": {
+   "config": {
+    "mode": "'dropdown'",
+    "options": "['settings', 'learners', 'both']",
+    "translation_key": "'factory_reset_scope'"
+   },
+   "default": "'both'",
+   "required": "Required",
+   "selector": "SelectSelector"
+  }
+ },
  "grid": {
   "after_save": {
    "config": {
diff --git a/tests/harness.py b/tests/harness.py
index 6f29b8e37..3a0e2c380 100644
--- a/tests/harness.py
+++ b/tests/harness.py
@@ -232,6 +232,8 @@ class FakeConfigEntries:
     def __init__(self) -> None:
         self.entries = []
         self.reloaded = []
+        self.unloaded = []
+        self.set_up = []
         # One name per async_update_entry call (#100): the options pages that
         # stay in the dialog persist through here, and tests assert both the
         # write and its count.
@@ -282,6 +284,15 @@ class FakeConfigEntries:
         self.reloaded.append(entry_id)
         return True
 
+    async def async_unload(self, entry_id):
+        """Recorded, as ``async_reload`` is: the factory reset unloads, then sets up."""
+        self.unloaded.append(entry_id)
+        return True
+
+    async def async_setup(self, entry_id):
+        self.set_up.append(entry_id)
+        return True
+
     async def async_forward_entry_setups(self, entry, platforms):
         return None
 
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.45d9e00a.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.45d9e00a.json
new file mode 100644
index 000000000..a6c6be541
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.45d9e00a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset GUARD_OFF 45d9e00a",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if not user_input.get(\"confirm\"):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.8bc8eedc.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.8bc8eedc.json
new file mode 100644
index 000000000..ab6274a65
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.8bc8eedc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset GUARD_OFF 8bc8eedc",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if user_input is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.a0db8943.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.a0db8943.json
new file mode 100644
index 000000000..ee637273a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.GUARD_OFF.a0db8943.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset GUARD_OFF a0db8943",
+  "killed_by": "tests/features.py",
+  "old": "        if (coord := getattr(self._entry, \"runtime_data\", None)) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.RETURN_DEL.f30dc257.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.RETURN_DEL.f30dc257.json
new file mode 100644
index 000000000..a464949d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_factory_reset.RETURN_DEL.f30dc257.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_factory_reset RETURN_DEL f30dc257",
+  "killed_by": "tests/features.py",
+  "old": "        return self.async_abort(reason=\"factory_reset_done\" if done else \"factory_reset_not_applied\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.bc450a12.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_learner_payloads.GUARD_OFF.fbcfbdb6.json
similarity index 55%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.bc450a12.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_learner_payloads.GUARD_OFF.fbcfbdb6.json
index 995ab42b6..28a879b47 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._dhw_probe_temperature.GUARD_OFF.bc450a12.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_learner_payloads.GUARD_OFF.fbcfbdb6.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._dhw_probe_temperature GUARD_OFF bc450a12",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_learner_payloads GUARD_OFF fbcfbdb6",
   "killed_by": "tests/features.py",
-  "old": "        if self._learning_frozen(CONF_DHW_TEMP_ENTITY, room_air=False) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+  "old": "                if (value := finite_float(thermal.get(key))) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.CLAMP_DROP.1dc0e79b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.CLAMP_DROP.1dc0e79b.json
new file mode 100644
index 000000000..8f2d2d2b5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.CLAMP_DROP.1dc0e79b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning CLAMP_DROP 1dc0e79b",
+  "killed_by": "tests/features.py",
+  "old": "        self._snow_accum_cm = max(0.0, finite_float(stored.get(\"snow_accum_cm\"), 0.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`self._snow_accum_cm = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.41a865ec.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.41a865ec.json
deleted file mode 100644
index 3aa7e0279..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.41a865ec.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF 41a865ec",
-  "killed_by": "tests/features.py",
-  "old": "        if ratio is not None:",
-  "reason": "Recorded by `mutation_table.py --drain` against e3f3b312fff572904f24d78a44a2c4492b1a8ddb: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.798dac67.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.798dac67.json
new file mode 100644
index 000000000..3b65af358
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.798dac67.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF 798dac67",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, \"house_heat_loss_scale\", \"house_heat_loss_samples\", self._apply_house_heat_loss_scale)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=25."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.b39a405a.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.b39a405a.json
new file mode 100644
index 000000000..4cac576fb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.b39a405a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF b39a405a",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, \"buffer_cooling_rate\", \"buffer_cooling_samples\", self._apply_buffer_cooling_rate)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.dc87c807.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.dc87c807.json
new file mode 100644
index 000000000..0e019dd37
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.dc87c807.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF dc87c807",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, _COP_STORE_KEY, \"cop_samples\", self._apply_cop_scale)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.e9836e13.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.e9836e13.json
new file mode 100644
index 000000000..64c998c05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_thermal_learning.GUARD_OFF.e9836e13.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_thermal_learning GUARD_OFF e9836e13",
+  "killed_by": "tests/features.py",
+  "old": "        if (n := _stored_learner(stored, \"lower_floor_loss_ratio\", \"lower_floor_loss_samples\", self._apply_lower_floor_loss_ratio)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=21."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.BOOLOP.45eae803.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.BOOLOP.45eae803.json
new file mode 100644
index 000000000..d67aa509c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.BOOLOP.45eae803.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._current_humidity BOOLOP 45eae803",
+  "killed_by": "tests/features.py",
+  "old": "        return value if value is not None and 0.0 <= value <= 100.0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return value if value is not None or 0.0 <= value <= 100.0 else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.RETURN_DEL.45eae803.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.RETURN_DEL.45eae803.json
new file mode 100644
index 000000000..c77bebdab
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._current_humidity.RETURN_DEL.45eae803.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._current_humidity RETURN_DEL 45eae803",
+  "killed_by": "tests/features.py",
+  "old": "        return value if value is not None and 0.0 <= value <= 100.0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_restore_learned_snapshot.GUARD_OFF.d20d64a4.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_restore_learned_snapshot.GUARD_OFF.d20d64a4.json
new file mode 100644
index 000000000..19098aaf9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_restore_learned_snapshot.GUARD_OFF.d20d64a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_restore_learned_snapshot GUARD_OFF d20d64a4",
+  "killed_by": "tests/features.py",
+  "old": "        if \"before_reset\" in snap:  # a factory reset's undo point: stores and settings back",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # a factory reset's undo point: stores and settings back`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.0bcc5a76.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.0bcc5a76.json
new file mode 100644
index 000000000..d9fb0b2fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.0bcc5a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_rewrite_entry GUARD_OFF 0bcc5a76",
+  "killed_by": "tests/features.py",
+  "old": "    if not await hass.config_entries.async_unload(entry.entry_id):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.3602237b.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.3602237b.json
new file mode 100644
index 000000000..2ba151ef0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.GUARD_OFF.3602237b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_rewrite_entry GUARD_OFF 3602237b",
+  "killed_by": "tests/features.py",
+  "old": "    if settings is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.RETURN_DEL.80a0007e.json
new file mode 100644
index 000000000..b2226ca79
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_rewrite_entry.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_rewrite_entry RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_async_store_documents.RETURN_DEL.e2917fe4.json b/tests/mutation_ledger/killed_by/coordinator.py/_async_store_documents.RETURN_DEL.e2917fe4.json
new file mode 100644
index 000000000..cb047400b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_async_store_documents.RETURN_DEL.e2917fe4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_async_store_documents RETURN_DEL e2917fe4",
+  "killed_by": "tests/features.py",
+  "old": "    return {name: await store.async_load() for (name, _), store in zip(_FACTORY_VOID, _restored_stores(coord))}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_isoformat.GUARD_OFF.e71653f6.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_isoformat.GUARD_OFF.e71653f6.json
new file mode 100644
index 000000000..4d6112daa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_isoformat.GUARD_OFF.e71653f6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_isoformat GUARD_OFF e71653f6",
+  "killed_by": "tests/features.py",
+  "old": "    if not isinstance(raw, str):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.GUARD_OFF.49093545.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.GUARD_OFF.49093545.json
new file mode 100644
index 000000000..40f62f181
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.GUARD_OFF.49093545.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_learner GUARD_OFF 49093545",
+  "killed_by": "tests/features.py",
+  "old": "    if (value := stored.get(key)) is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.5cb47597.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.5cb47597.json
new file mode 100644
index 000000000..5163af912
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.5cb47597.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_learner RETURN_DEL 5cb47597",
+  "killed_by": "tests/features.py",
+  "old": "    return count",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=19."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.d7923b87~2.json b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.d7923b87~2.json
new file mode 100644
index 000000000..9afe1c2ec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/_stored_learner.RETURN_DEL.d7923b87~2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_stored_learner RETURN_DEL d7923b87#2",
+  "killed_by": "tests/features.py",
+  "old": "        return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json b/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json
new file mode 100644
index 000000000..cd6eacae1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/factory_settings.RETURN_DEL.9521dcc2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:factory_settings RETURN_DEL 9521dcc2",
+  "killed_by": "tests/features.py",
+  "old": "    return with_settings((data, {**options, **pinned}), ({}, {}))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/entry_config.py/with_settings.RETURN_DEL.80c79bfe.json b/tests/mutation_ledger/killed_by/entry_config.py/with_settings.RETURN_DEL.80c79bfe.json
new file mode 100644
index 000000000..4472f55a9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entry_config.py/with_settings.RETURN_DEL.80c79bfe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entry_config.py:with_settings RETURN_DEL 80c79bfe",
+  "killed_by": "tests/features.py",
+  "old": "    return {**rest[0], **kept[0]}, {**rest[1], **kept[1]}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/services.py/handle_factory_reset.RETURN_DEL.4bcd781f.json b/tests/mutation_ledger/killed_by/services.py/handle_factory_reset.RETURN_DEL.4bcd781f.json
new file mode 100644
index 000000000..ae5ebd5ac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/services.py/handle_factory_reset.RETURN_DEL.4bcd781f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/services.py:handle_factory_reset RETURN_DEL 4bcd781f",
+  "killed_by": "tests/features.py",
+  "old": "    return {\"reset\": data[\"entry_id\"], \"scope\": data[\"scope\"]}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.512dc888.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.512dc888.json
deleted file mode 100644
index dfaa9348a..000000000
--- a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.512dc888.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.best_restore GUARD_OFF 512dc888",
-  "killed_by": "tests/features.py",
-  "old": "            if not snap.get(\"healthy\"):",
-  "reason": "Recorded by `mutation_table.py --drain` against 9061fbd3d710d5894b7083d8a58b8203f9e7aa97: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.6541f9a5.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.6541f9a5.json
new file mode 100644
index 000000000..c2cf92fde
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.best_restore.GUARD_OFF.6541f9a5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.best_restore GUARD_OFF 6541f9a5",
+  "killed_by": "tests/features.py",
+  "old": "            if not snap.get(\"healthy\") or \"before_reset\" in snap:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.BOOLOP.ee22e5a2.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.BOOLOP.ee22e5a2.json
new file mode 100644
index 000000000..855215f44
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.BOOLOP.ee22e5a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.undo_target BOOLOP ee22e5a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.snapshots and \"before_reset\" in self.snapshots[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.snapshots or \"before_reset\" in self.snapshots[-1]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.GUARD_OFF.ee22e5a2.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.GUARD_OFF.ee22e5a2.json
new file mode 100644
index 000000000..49615c216
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.GUARD_OFF.ee22e5a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.undo_target GUARD_OFF ee22e5a2",
+  "killed_by": "tests/features.py",
+  "old": "        if self.snapshots and \"before_reset\" in self.snapshots[-1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.RETURN_DEL.da7502bd.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.RETURN_DEL.da7502bd.json
new file mode 100644
index 000000000..58029975a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.undo_target.RETURN_DEL.da7502bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.undo_target RETURN_DEL da7502bd",
+  "killed_by": "tests/features.py",
+  "old": "        return self.best_restore()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/nightly_ha.py b/tests/nightly_ha.py
index e7e9f23de..fe77f07ec 100644
--- a/tests/nightly_ha.py
+++ b/tests/nightly_ha.py
@@ -1219,9 +1219,14 @@ def option_resubmit(step: str, current: dict) -> dict:
     The form schema is sectioned (``group`` → ``section()``); stored options
     are flat. Home Assistant validates the shown schema before the handler
     runs, so a flat resubmit is ``InvalidData`` on every grouped page.
-    ``setup_overview`` saves nothing.
+    Two pages save nothing and show no after-save choice, so each posts
+    ``{}``: ``setup_overview``, and ``factory_reset``, whose untouched submit
+    (unconfirmed) returns the advanced menu -- the after-save key alone is
+    ``InvalidData`` there (#3047). ``tests/config_flow_steps.py`` applies
+    every page's shown schema to this payload, so a third such page fails
+    there, not only here.
     """
-    if step == "setup_overview":
+    if step in ("setup_overview", "factory_reset"):
         return {}
     cf = _prod_mod("config_flow")
     const = _prod_mod("const")
diff --git a/tests/seam_map.json b/tests/seam_map.json
index a678a9b69..17772e9b2 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -226,6 +226,10 @@
   "configured_dhw_windows": "dhw",
   "coordinator._async_save_restored": "learning",
   "coordinator._restored_stores": "learning",
+  "coordinator.async_factory_reset": "learning",
+  "coordinator._async_rewrite_entry": "learning",
+  "coordinator._async_store_documents": "learning",
+  "coordinator._async_undo_factory_reset": "learning",
   "coordinator._cop_fold_blocked": "learning",
   "coordinator._ctx_of": "core",
   "coordinator._publish_params": "core",
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f85a64423..9de767669 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17653,
+ "class_excess_loc": 17648,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -11,11 +11,11 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 8059,
+ "max_class_loc": 7983,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "460d7754f48630a9fa0d84c31be78bc78d71c02b",
- "seam_cut_total": 422
+ "recorded_at": "8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f",
+ "seam_cut_total": 423
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
