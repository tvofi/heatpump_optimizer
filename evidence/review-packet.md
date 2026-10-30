# Review packet #2968
head: ddf75aaf8651c502794de257bbc76c044282f102
base: aced258937628590b92265eea4c01276cac43b24

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123981417726 neutral
arch-score / arch-score id=123981124845 success
arm id=123980952900 skipped
budget-raise-gate / budget-raise-gate id=123981125188 success
cancel-superseded id=123980957282 success
codeql / Analyze (actions) id=123981124946 success
codeql / Analyze (javascript-typescript) id=123981125064 success
codeql / Analyze (python) id=123981125094 in_progress
governance / delivery-status id=123981125250 success
governance / delivery-status-publish id=123981126862 skipped
governance / env-matrix id=123981124989 success
governance / instrument-self-tests id=123981125206 in_progress
governance / policy-docs id=123981125054 success
governance / record id=123981127777 skipped
governance / wave-script id=123981125110 success
hassfest / hassfest id=123981125117 success
kernel-points id=123981126882 skipped
prelude id=123980956891 success
refresh id=123980957079 success
tests / arch-instrument id=123981317375 in_progress
tests / briefs id=123981124899 success
tests / browser id=123981317497 success
tests / closure-scope id=123981124941 success
tests / closures id=123981317520 in_progress
tests / coverage id=123981317440 in_progress
tests / fast (3.14) id=123981317453 in_progress
tests / mutation id=123981124883 failure
tests / mutation-pins (1) id=123981348573 in_progress
tests / nightly-ha id=123981319314 skipped
tests / nightly-status id=123981124762 success
tests / replay id=123981317552 success
tests / typing id=123981317335 success
validate / validate-hacs id=123981125050 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 6ddd8a17: #2492
NOTE body item de44c3e4: dismissed:environment-only, the typing census runs in CI
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_actuation_phase.py
             `dev/audit/harnesses/r10_sav_actuation_phase.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  unverified git grep -n 'switch_supply(' -- custom_components/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n 'heat_pump_on_schedule\|plan_step_runs(' -- custom_components/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=88c6ad5bbec69bfe157e04597a74d0c9c3e4775c PYTHONPATH=tests/hastub ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 88c6ad5bbec69bfe157e04597a74d0c9c3e4775c HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --hooks tools/policy/fixtures/policy-rot/hooks/no-matcher.json
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head

FIGURES: 12 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.bb3f033b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.bb3f033b.json
deleted file mode 100644
index 081bc3030..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.bb3f033b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_action BOOLOP bb3f033b",
-  "killed_by": "tests/features.py",
-  "old": "        if switch_entity and not skip_off:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: BOOLOP (`if switch_entity or not skip_off:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.GUARD_OFF.bb3f033b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.GUARD_OFF.bb3f033b.json
deleted file mode 100644
index 8707c8da4..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.GUARD_OFF.bb3f033b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_action GUARD_OFF bb3f033b",
-  "killed_by": "tests/features.py",
-  "old": "        if switch_entity and not skip_off:",
-  "reason": "Recorded by `mutation_table.py --drain` against e30b24bbc45afd1174f64f7051d05021e31b6a89: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.BOOLOP.aa491430.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.BOOLOP.aa491430.json
new file mode 100644
index 000000000..ff6bc8cdb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.BOOLOP.aa491430.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._write_supply BOOLOP aa491430",
+  "killed_by": "tests/features.py",
+  "old": "        if switch_entity and value is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if switch_entity or value is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.GUARD_OFF.aa491430.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.GUARD_OFF.aa491430.json
new file mode 100644
index 000000000..27e0c57a5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.GUARD_OFF.aa491430.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._write_supply GUARD_OFF aa491430",
+  "killed_by": "tests/features.py",
+  "old": "        if switch_entity and value is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_apply_result_payload.BOOLOP.09efd8da.json b/tests/mutation_ledger/killed_by/coordinator.py/_apply_result_payload.BOOLOP.09efd8da.json
deleted file mode 100644
index bc58adb27..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_apply_result_payload.BOOLOP.09efd8da.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_apply_result_payload BOOLOP 09efd8da",
-  "killed_by": "tests/features.py",
-  "old": "                        if result.heat_pump_on_schedule and idx < len(result.heat_pump_on_schedule)",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if result.heat_pump_on_schedule or idx < len(result.heat_pump_on_schedule)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.BOOLOP.519a7ed9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.BOOLOP.519a7ed9.json
deleted file mode 100644
index 299e74c37..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.BOOLOP.519a7ed9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.get_current_action BOOLOP 519a7ed9",
-  "killed_by": "tests/stress.py",
-  "old": "            if result.dhw_power_schedule and i < len(result.dhw_power_schedule)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against bd79bc9e0e7ee5bb8d7fac6a400f5e077f3c3266: BOOLOP (`if result.dhw_power_schedule or i < len(result.dhw_power_schedule)`) took tests/stress.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
new file mode 100644
index 000000000..8b4be5e95
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index BOOLOP fe5ed606",
+  "killed_by": "tests/features.py",
+  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if i < 0 or (i == len(stamps) - 1 or now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
new file mode 100644
index 000000000..885b282bb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index CMP_BOUND fe5ed606",
+  "killed_by": "tests/features.py",
+  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i <= 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=72. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
new file mode 100644
index 000000000..554f0d548
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index GUARD_OFF fe5ed606",
+  "killed_by": "tests/features.py",
+  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
new file mode 100644
index 000000000..8ad75207e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index RETURN_DEL 67f638e2",
+  "killed_by": "tests/features.py",
+  "old": "    return i",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/live_power_kw.RETURN_DEL.2899b10f.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/live_power_kw.RETURN_DEL.2899b10f.json
new file mode 100644
index 000000000..b09e562ec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/live_power_kw.RETURN_DEL.2899b10f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:live_power_kw RETURN_DEL 2899b10f",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return reading.value if reading.ok else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/note_supply.GUARD_OFF.ed5e93ab.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/note_supply.GUARD_OFF.ed5e93ab.json
new file mode 100644
index 000000000..c623facd8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/note_supply.GUARD_OFF.ed5e93ab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:note_supply GUARD_OFF ed5e93ab",
+  "killed_by": "tests/features.py",
+  "old": "    if held.supply_unsub is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/release_supply.GUARD_OFF.7725d105.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/release_supply.GUARD_OFF.7725d105.json
new file mode 100644
index 000000000..e43f0472c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/release_supply.GUARD_OFF.7725d105.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:release_supply GUARD_OFF 7725d105",
+  "killed_by": "tests/features.py",
+  "old": "    if unsub is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.BOOLOP.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.BOOLOP.fe5ed606.json
deleted file mode 100644
index 40ed6ab0d..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.BOOLOP.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty BOOLOP fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 52f698905868c9140ed213ea542c44053fca7096: BOOLOP (`if i < 0 or (i == len(stamps) - 1 or now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.CMP_BOUND.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.CMP_BOUND.fe5ed606.json
deleted file mode 100644
index c398ff410..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.CMP_BOUND.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty CMP_BOUND fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 52f698905868c9140ed213ea542c44053fca7096: CMP_BOUND (`if i <= 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=72. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.45217e20.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.45217e20.json
new file mode 100644
index 000000000..af96c5305
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.45217e20.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty GUARD_OFF 45217e20",
+  "killed_by": "tests/guard_pins.py",
+  "old": "    if i is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.fe5ed606.json
deleted file mode 100644
index 5a8c61931..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty GUARD_OFF fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 52f698905868c9140ed213ea542c44053fca7096: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.030cf220.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.030cf220.json
new file mode 100644
index 000000000..116bf7d0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.030cf220.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply GUARD_OFF 030cf220",
+  "killed_by": "tests/features.py",
+  "old": "    if boosts.active(boost.CHANNEL_SPACE, now) or boosts.active(boost.CHANNEL_DHW, now):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.44d997bd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.44d997bd.json
new file mode 100644
index 000000000..723006ee5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.44d997bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply GUARD_OFF 44d997bd",
+  "killed_by": "tests/features.py",
+  "old": "    if (inp.action or {}).get(\"mode\") == \"system_identification\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.c58cb373.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.c58cb373.json
new file mode 100644
index 000000000..be535eb98
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.c58cb373.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply GUARD_OFF c58cb373",
+  "killed_by": "tests/features.py",
+  "old": "    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or inp.plan is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.RETURN_DEL.7f5bc4e7.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.RETURN_DEL.7f5bc4e7.json
new file mode 100644
index 000000000..c75de7057
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.RETURN_DEL.7f5bc4e7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply RETURN_DEL 7f5bc4e7",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return None if i is None or i >= len(inp.plan.power_schedule or ()) else plan_step_runs(inp.plan, i)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.3bc78a66.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.3bc78a66.json
new file mode 100644
index 000000000..7836f98c6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.3bc78a66.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF 3bc78a66",
+  "killed_by": "tests/features.py",
+  "old": "    if inp.entry_released:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.aa236a67.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.aa236a67.json
new file mode 100644
index 000000000..d7296832b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.aa236a67.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF aa236a67",
+  "killed_by": "tests/features.py",
+  "old": "    if on != last:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.dcaaed0d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.dcaaed0d.json
new file mode 100644
index 000000000..ca8df4587
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.dcaaed0d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF dcaaed0d",
+  "killed_by": "tests/harness_headers.py",
+  "old": "    if held.supply is None or held.supply[0] == step:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/harness_headers.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.f90e3098.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.f90e3098.json
new file mode 100644
index 000000000..ff770e19f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.f90e3098.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF f90e3098",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    if on is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.BOOLOP.92bdc254.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.BOOLOP.92bdc254.json
new file mode 100644
index 000000000..eca52d779
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.BOOLOP.92bdc254.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_write BOOLOP 92bdc254",
+  "killed_by": "tests/features.py",
+  "old": "    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if on or not ((signals.space_blocked or signals.dhw_blocked) or signals.mode.cooling):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.GUARD_OFF.92bdc254.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.GUARD_OFF.92bdc254.json
new file mode 100644
index 000000000..d8f3cd21d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.GUARD_OFF.92bdc254.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_write GUARD_OFF 92bdc254",
+  "killed_by": "tests/features.py",
+  "old": "    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.RETURN_DEL.da9e8e97.json
new file mode 100644
index 000000000..3c2205ee8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_write RETURN_DEL da9e8e97",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.BOOLOP.e5c45a76.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.BOOLOP.e5c45a76.json
new file mode 100644
index 000000000..43a251f28
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.BOOLOP.e5c45a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs BOOLOP e5c45a76",
+  "killed_by": "tests/features.py",
+  "old": "    if runs and i < len(runs):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if runs or i < len(runs):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.e5c45a76.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.e5c45a76.json
new file mode 100644
index 000000000..08a6b94be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.e5c45a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs CMP_BOUND e5c45a76",
+  "killed_by": "tests/features.py",
+  "old": "    if runs and i < len(runs):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if runs and i <= len(runs):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.f0f14778.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.f0f14778.json
new file mode 100644
index 000000000..97b6980e7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.f0f14778.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs CMP_BOUND f0f14778",
+  "killed_by": "tests/features.py",
+  "old": "    return planned_draw_runs(result.power_schedule[i], dhw[i] if i < len(dhw) else 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return planned_draw_runs(result.power_schedule[i], dhw[i] if i <= len(dhw) else 0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.GUARD_OFF.e5c45a76.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.GUARD_OFF.e5c45a76.json
new file mode 100644
index 000000000..a9f23b1bf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.GUARD_OFF.e5c45a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs GUARD_OFF e5c45a76",
+  "killed_by": "tests/features.py",
+  "old": "    if runs and i < len(runs):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.RETURN_DEL.f0f14778.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.RETURN_DEL.f0f14778.json
new file mode 100644
index 000000000..2dc9d74ae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.RETURN_DEL.f0f14778.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs RETURN_DEL f0f14778",
+  "killed_by": "tests/features.py",
+  "old": "    return planned_draw_runs(result.power_schedule[i], dhw[i] if i < len(dhw) else 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 88ac5122a..bd7a38ab2 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -335,6 +335,7 @@ from .thermal_model import (
     mold_safe_room_floor,
     learner_unmetered,
     on_threshold_kw,
+    plan_step_runs,
     planned_draw_runs,
     probe_install,
     reanchor_heat_loss,
@@ -2751,16 +2752,7 @@ def _apply_result_payload(
                         if result.displace_schedule and idx < len(result.displace_schedule)
                         else 0.0
                     ),
-                    "heat_pump_on": (
-                        result.heat_pump_on_schedule[idx]
-                        if result.heat_pump_on_schedule and idx < len(result.heat_pump_on_schedule)
-                        else planned_draw_runs(
-                            p,
-                            result.dhw_power_schedule[idx]
-                            if idx < len(result.dhw_power_schedule or ())
-                            else 0.0,
-                        )
-                    ),
+                    "heat_pump_on": plan_step_runs(result, idx),
                 }
                 for idx, (ts, p, s, pr, rt, ut, lt, sg) in enumerate(zip(
                     result.timestamps,
@@ -3767,7 +3759,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             thermal=self._thermal_model,
             params=ctx._thermal_params,
             action=self._current_action,
-            measured_power_kw=self._measured_power,
+            measured_power_kw=pump_arbiter.live_power_kw(self.hass, ctx._config),
             disinfecting=getattr(
                 getattr(self._legionella, "disinfect", None), "memo", None
             )
@@ -7515,22 +7507,23 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                           self._plan_age_minutes() or 0.0, self._solve_failures)
             return
 
-        # A cut-off holds the pump off for MIN_OFF across an early refresh.
-        heat_pump_on = early_cutoff.allow_on(early_cutoff.state_for(self), bool(self._current_action.get("heat_pump_on", False)))
+        on = bool(self._current_action.get("heat_pump_on", False))
+        await self._write_supply(on)
+        # Between cycles the step tick writes each step's change (#2492).
+        pump_arbiter.note_supply(pump_arbiter.state_for(self), pump_arbiter.SupplyWiring(self.arbiter_inputs, boost.held_for(self), self._write_supply), on)
+        # The ECL110 displace command
+        await self.async_publish_current_action(reason="scheduled_update")
 
-        # Skip OFF only when cooling or both channels are blocked. A
-        # single-channel heat block (DHW-only, heating-only) still
-        # commands OFF on an empty plan — otherwise a summer DHW pulse
-        # leaves the supply latched while the tank is supposed to drift.
-        both_blocked = (
-            self._pump_signals.space_blocked and self._pump_signals.dhw_blocked
-        )
-        skip_off = (not heat_pump_on) and (
-            both_blocked or self._pump_signals.mode.cooling
-        )
+    async def _write_supply(self, on: bool) -> None:
+        """Write the supply switch: the cycle's and the step tick's one gate.
+
+        A cut-off holds the pump off for MIN_OFF across an early refresh.
+        """
+        value = pump_arbiter.supply_write(
+            early_cutoff.allow_on(early_cutoff.state_for(self), on), self._pump_signals)
         switch_entity = getattr(self, "_ctx", self)._config.heat_pump_switch_entity
-        if switch_entity and not skip_off:
-            await pump_arbiter.switch_supply(self.hass, switch_entity, heat_pump_on)
+        if switch_entity and value is not None:
+            await pump_arbiter.switch_supply(self.hass, switch_entity, value)
         elif switch_entity:
             _LOGGER.debug(
                 "Not switching %s off: mode %s is cooling or blocks both "
@@ -7539,9 +7532,6 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 switch_entity,
                 self._pump_signals.mode.label,
             )
-
-        # The ECL110 displace command
-        await self.async_publish_current_action(reason="scheduled_update")
     # ------------------------------------------------------------------
     # Published state
     # ------------------------------------------------------------------
diff --git a/custom_components/heatpump_optimizer/early_cutoff.py b/custom_components/heatpump_optimizer/early_cutoff.py
index 21a82ae74..a58d8bb38 100644
--- a/custom_components/heatpump_optimizer/early_cutoff.py
+++ b/custom_components/heatpump_optimizer/early_cutoff.py
@@ -7,7 +7,10 @@ interval. This module listens to the room thermometer, as the peak guard
 listens to the meter. When the room passes the active comfort target plus
 :data:`MARGIN_K` on a step the plan gave to space heating, it switches the
 pump off once. The next cycle writes the plan's own action again, so the
-pump resumes then (decision recorded on #201, comment 6067353918).
+pump resumes then (decision recorded on #201, comment 6067353918). The step
+tick between cycles (``pump_arbiter.supply_tick``) writes only a step whose
+command differs from the last, so a cut holds across a step the plan keeps
+on, and a step the plan turns on passes :func:`allow_on` like the cycle's.
 
 **The threshold** is the higher of the active comfort target and the room
 temperature the plan predicts for the end of the current step, plus the margin. A plan that pre-heats
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 597ed1814..8d958e040 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -99,6 +99,7 @@ from .thermal_model import (
     _step_humidity,
     channel_heating_steps,
     levels_clamped,
+    plan_step_runs,
     planned_draw_runs,
     planned_draws_run,
     project_planned_levels,
@@ -5637,21 +5638,10 @@ class HeatPumpOptimizer:
             if result.displace_schedule and i < len(result.displace_schedule)
             else 0.0
         )
-        # The schedule is the authority; the fallback is the same owner on the
-        # same two circuits, for a result built without the field. Both read
-        # the plan's own running rule, never the meter's threshold, so a step
+        # The plan's own running rule, never the meter's threshold, so a step
         # this action declares off is a step the plan booked no heat for
-        # (R9 D12-s2-01).
-        dhw_power_at_i = (
-            result.dhw_power_schedule[i]
-            if result.dhw_power_schedule and i < len(result.dhw_power_schedule)
-            else 0.0
-        )
-        heat_pump_on = (
-            result.heat_pump_on_schedule[i]
-            if result.heat_pump_on_schedule and i < len(result.heat_pump_on_schedule)
-            else planned_draw_runs(power, dhw_power_at_i)
-        )
+        # (R9 D12-s2-01); one owner for every reader of the plan's switch.
+        heat_pump_on = plan_step_runs(result, i)
 
         p_norm = _power_fraction(power, self.model.params)
 
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 28192688b..28e1f706e 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -44,8 +44,9 @@ A block drops its duty out of :func:`_planned_duty` and again out of
 whatever :func:`_share` and the hot-water lease return, so a blocked
 duty is served as idle and a lease expiry cannot hand it back. The
 arbitration never writes the power switch; :func:`switch_supply` below is
-that switch's one writer, shared by the cycle's plan write and the early
-cut-off (``early_cutoff.py``), so the domain routing has one owner.
+that switch's one writer, shared by the cycle's plan write, the step tick
+(:func:`supply_tick`) and the early cut-off (``early_cutoff.py``), so the
+domain routing has one owner.
 
 **Two transports, one logic.** The Tuya fork offers DHW-only and Heating,
 so the mode is the gate there. The GCHV/Rotenso Modbus package's mode
@@ -106,7 +107,8 @@ both (:func:`_planned_duty`). Turning it off writes nothing.
 
 It acts at step boundaries: a one-minute tick (only while the option is not
 off) re-derives the step, since the solve runs every 30 minutes and a plan
-step is 15.
+step is 15. The power switch has its own one-minute tick, armed by the
+cycle's first switch write whatever the option says (:func:`supply_tick`).
 
 **Observe keeps a ledger**, in observe and in control: per 15-minute step,
 the planned duty against what the pump did, read from what the integration
@@ -127,7 +129,7 @@ import asyncio
 import bisect
 import logging
 from collections import Counter, deque
-from collections.abc import Mapping
+from collections.abc import Awaitable, Callable, Mapping
 from dataclasses import dataclass, field, replace
 from datetime import datetime, timedelta, timezone
 from typing import Any, TypeGuard
@@ -146,6 +148,7 @@ from .const import (
     CONF_BUFFER_TANK_TEMP_ENTITY,
     CONF_FLOOR_RETURN_TEMP_ENTITY,
     CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
+    CONF_POWER_ENTITY,
     CONF_VALVE_OUTLET_TEMP_ENTITY,
     DOMAIN,
     MODE_AUTO,
@@ -171,6 +174,7 @@ from .thermal_model import (
     flow_setpoint_for_level,
     modulation_floor_flow_c,
     on_threshold_kw,
+    plan_step_runs,
     planned_draw_runs,
     probe_install,
 )
@@ -241,6 +245,11 @@ class ArbiterState:
     loaded: bool = False
     unsubs: list[Any] = field(default_factory=list)
     lock: asyncio.Lock = field(default_factory=asyncio.Lock)
+    #: (step start, the supply the plan commanded for that step): written by
+    #: the cycle's switch write and moved by :func:`supply_tick` (#2492).
+    supply: tuple[datetime, bool] | None = None
+    #: The step tick's listener; dropped only at unload, never by duty mode.
+    supply_unsub: Callable[[], None] | None = None
 
 
 @dataclass(frozen=True)
@@ -344,11 +353,8 @@ def step_duty(result: Any, now: datetime) -> str | None:
     the loop, so the harm was the channel and the second piece of state that
     kept it clean, not a live race.
     """
-    stamps = list(getattr(result, "timestamps", None) or [])
-    i = bisect.bisect_right(stamps, now) - 1
-    # A step covers [stamp, stamp + one plan step): the last one ends where the
-    # next would start, the same half-open rule bisect gives every other step.
-    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):
+    i = _step_index(result, now)
+    if i is None:
         return None
     space = list(result.power_schedule or [])
     dhw = list(getattr(result, "dhw_power_schedule", None) or [])
@@ -360,6 +366,19 @@ def step_duty(result: Any, now: datetime) -> str | None:
     )
 
 
+def _step_index(result: Any, now: datetime) -> int | None:
+    """The index of the plan step covering ``now``, or ``None`` outside the plan.
+
+    A step covers [stamp, stamp + one plan step): the last one ends where the
+    next would start, the same half-open rule bisect gives every other step.
+    """
+    stamps = list(getattr(result, "timestamps", None) or [])
+    i = bisect.bisect_right(stamps, now) - 1
+    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):
+        return None
+    return i
+
+
 def own(coord: Any, signals: Any) -> Any:
     """``signals`` with a heating mode marked as the arbiter's, not a block.
 
@@ -508,6 +527,28 @@ FLOW_INLET_KEYS = (
 )
 
 
+def _reader(hass: Any, config: Mapping[str, Any]) -> InputReader:
+    """The arbiter's live entity reads, under the install's staleness rules."""
+    cfg = EntryConfig.from_mapping(config)
+    return InputReader(
+        hass, dict(config or {}),
+        enabled=cfg.staleness_watchdog_enabled,
+        scale=cfg.staleness_max_age_scale,
+    )
+
+
+def live_power_kw(hass: Any, config: Mapping[str, Any]) -> float | None:
+    """The pump's measured draw now, kW, or ``None`` when unread.
+
+    Read at each pass, not taken from the cycle's sample: the ledger folds
+    one reading per one-minute tick, and a sample frozen at the cycle made a
+    step's verdict depend on where the cycle fell against the step grid
+    (#2492).
+    """
+    reading = _reader(hass, config).read_power_kw(CONF_POWER_ENTITY)
+    return reading.value if reading.ok else None
+
+
 def _flow_inlet_c(inp: ArbiterInputs) -> float | None:
     """The first fresh reading of :data:`FLOW_INLET_KEYS`, °C, or ``None``.
 
@@ -515,12 +556,7 @@ def _flow_inlet_c(inp: ArbiterInputs) -> float | None:
     unconfigured slot is absent rather than guessed, and a slot left unset
     falls to the next rung.
     """
-    cfg = EntryConfig.from_mapping(inp.config)
-    reader = InputReader(
-        inp.hass, dict(inp.config or {}),
-        enabled=cfg.staleness_watchdog_enabled,
-        scale=cfg.staleness_max_age_scale,
-    )
+    reader = _reader(inp.hass, inp.config)
     readings = (reader.read(key) for key in FLOW_INLET_KEYS)
     return next(
         (reading.value for reading in readings if reading.ok), None
@@ -1126,6 +1162,104 @@ async def switch_supply(hass: Any, entity_id: str, on: bool) -> None:
         _LOGGER.error("Error toggling heat pump switch %s: %s", entity_id, err)
 
 
+def supply_write(on: bool, signals: Any) -> bool | None:
+    """The switch value to write for ``on``, or ``None`` to leave the switch.
+
+    OFF is skipped only when the pump's own mode is cooling or blocks both
+    channels: an empty plan is then this integration's doing, not a decision
+    to stop the pump. A single-channel block (DHW-only, heating-only) still
+    commands OFF, or a summer DHW pulse would leave the supply latched while
+    the tank is supposed to drift.
+    """
+    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):
+        return on
+    return None
+
+
+def step_supply(inp: ArbiterInputs, boosts: Any, now: datetime) -> bool | None:
+    """The supply the plan commands for the step covering ``now``, or ``None``.
+
+    ``None`` wherever the cycle's own write does not come from the plan's
+    step: a non-plan mode, an experiment's override, a stale or missing plan,
+    or an instant outside it. A live boost on either channel (``boosts``, the
+    coordinator's ``boost.BoostState``) is on, as ``boost.overlay`` makes the
+    action the cycle writes.
+    """
+    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or inp.plan is None:
+        return None
+    if (inp.action or {}).get("mode") == "system_identification":
+        return None
+    if boosts.active(boost.CHANNEL_SPACE, now) or boosts.active(boost.CHANNEL_DHW, now):
+        return True
+    i = _step_index(inp.plan, now)
+    return None if i is None or i >= len(inp.plan.power_schedule or ()) else plan_step_runs(inp.plan, i)
+
+
+@dataclass(frozen=True)
+class SupplyWiring:
+    """What the step tick reads and writes through; built by :func:`note_supply`.
+
+    Plain values, as ``early_cutoff`` takes them: the coordinator's
+    published ``arbiter_inputs`` builder, its boost record and its gated
+    switch write, never the coordinator itself.
+    """
+
+    inputs: Callable[[], ArbiterInputs]
+    boosts: Any
+    write: Callable[[bool], Awaitable[None]]
+
+
+def note_supply(held: ArbiterState, wiring: SupplyWiring, on: bool, now: datetime | None = None) -> None:
+    """Record the cycle's supply command for its step; arm the step tick once.
+
+    ``wiring.write`` is the coordinator's gated switch write, the cycle's
+    own, so the tick passes the same cut-off hold and blocked-mode skip.
+    """
+    held.supply = (plan_step_start(now or dt_util.now()), on)
+    if held.supply_unsub is not None:
+        return
+    inp = wiring.inputs()
+    if not EntryConfig.from_mapping(inp.config).heat_pump_switch_entity:
+        return
+
+    async def _tick(_now: Any = None) -> None:
+        await supply_tick(held, wiring)
+
+    held.supply_unsub = async_track_time_interval(inp.hass, _tick, _TICK)
+
+
+async def supply_tick(held: ArbiterState, wiring: SupplyWiring, now: datetime | None = None) -> None:
+    """At a step boundary, write the supply where the plan's command changes.
+
+    The cycle writes the switch once per interval, so without this a step
+    change reached the pump only at the next cycle, as late as one interval
+    after the boundary, and a step's duty verdict depended on the cycle's
+    phase against the step grid (#2492). Only a change is written: a step
+    that commands what the last one did leaves the switch alone, so an early
+    cut-off still holds until the next cycle, as ``early_cutoff`` documents.
+    """
+    now = now or dt_util.now()
+    step = plan_step_start(now)
+    if held.supply is None or held.supply[0] == step:
+        return
+    inp = wiring.inputs()
+    if inp.entry_released:
+        return
+    on = step_supply(inp, wiring.boosts, now)
+    if on is None:
+        return
+    last, held.supply = held.supply[1], (step, on)
+    if on != last:
+        await wiring.write(on)
+
+
+def release_supply(held: ArbiterState) -> None:
+    """Unload: drop the step tick; idempotent."""
+    unsub, held.supply_unsub = held.supply_unsub, None
+    if unsub is not None:
+        unsub()
+
+
 def _pump_off(inp: ArbiterInputs) -> bool:
     """Whether the configured power switch reads off.
 
@@ -1142,6 +1276,7 @@ async def release(coord: Any) -> None:
     """Unload: write the baseline over anything still owned, then let go."""
     release_listeners(coord)
     held = state_for(coord)
+    release_supply(held)
     inp = coord.arbiter_inputs()
     if held.written and duty_mode(inp.config) == DUTY_CONTROL and inp.mode != MODE_OFF:
         await _command(coord, inp, desired(coord, inp, None, dt_util.now()), dt_util.now())
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 88e32d123..58549ff0b 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -463,7 +463,15 @@ DOMAINS: dict[str, dict[str, Domain | str]] = {
     "away": {"active": _FLAG, "return_time": _AT0, "migrated_helpers": _FLAG},
     "pump_duty": {
         "written/mode/0": _TEXT, "written/dhw_setpoint/0": _R, "written/space_setpoint/0": _R,
-        **{f"written/{k}/1": _AT for k in ("mode", "dhw_setpoint", "space_setpoint")},
+        # The silent switch (#1911) and the GCHV night-mode registers (#1913)
+        # are held slots on the same record (``pump_arbiter._writable``).
+        "written/silent/0": _FLAG,
+        **{f"written/night_{e}_hour/0": Domain("int", 0, 23) for e in ("start", "end")},
+        **{f"written/night_{e}_minute/0": Domain("int", 0, 59) for e in ("start", "end")},
+        **{f"written/{k}/1": _AT for k in (
+            "mode", "dhw_setpoint", "space_setpoint", "silent",
+            "night_start_hour", "night_start_minute", "night_end_hour", "night_end_minute",
+        )},
     },
     "manual_plan": {
         **{f"{k}_slots": _ABSENT for k in ("space", "dhw")},
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index aede981f7..6e66e08be 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1357,6 +1357,22 @@ class InstallCapability:
         )
 
 
+def plan_step_runs(result: Any, i: int) -> bool:
+    """Whether the plan switches the pump on for its step ``i``.
+
+    The plan's ``heat_pump_on_schedule`` is the authority; a result built
+    without it falls back to :func:`planned_draw_runs` on that step's two
+    draws. One rule for every reader of the plan's switch: the action a cycle
+    actuates (``optimizer.get_current_action``), the schedule it publishes and
+    the supply the step tick writes (``pump_arbiter.supply_tick``, #2492).
+    """
+    runs = getattr(result, "heat_pump_on_schedule", None)
+    if runs and i < len(runs):
+        return bool(runs[i])
+    dhw = getattr(result, "dhw_power_schedule", None) or ()
+    return planned_draw_runs(result.power_schedule[i], dhw[i] if i < len(dhw) else 0.0)
+
+
 def probe_install(config: Any) -> InstallCapability:
     """The one install-capability probe (#1955)."""
     cfg = config or {}
diff --git a/dev/audit/harnesses/r10_sav_actuation_phase.py b/dev/audit/harnesses/r10_sav_actuation_phase.py
new file mode 100644
index 000000000..3babc4a33
--- /dev/null
+++ b/dev/audit/harnesses/r10_sav_actuation_phase.py
@@ -0,0 +1,97 @@
+#!/usr/bin/env python3
+"""R10-SAV-ACTUATION (#2492 carry 5, seam 2): do duty verdicts depend on the cycle's phase?
+
+WHY IT EXISTS. The carry's owed control: a synthetic install with the cycle
+phase at 0 and at 14 min must book identical duty verdicts. This drives the
+REAL coordinator's ``_apply_action`` once per 30-minute cycle at each phase,
+fires every one-minute interval timer ``pump_arbiter`` arms, applies each
+switch write to the switch's state and lets the meter follow the switch; the
+cycle's own power sample is taken at the cycle, as ``_update_current_state``
+takes it. It uses no symbol the fix added, so it runs at the merge base (the
+null) and at the head alike. ``tests/features.py`` (section "supply switch at
+step boundaries") pins the same install as checks.
+
+Prints, per phase, the ledger's verdict per step and the minutes at which the
+switch was written, then ``AGREE: yes`` or ``AGREE: no`` over steps 1.. (step 0
+precedes the phase-14 install's first cycle).
+
+    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_actuation_phase.py
+"""
+import asyncio
+from datetime import datetime, timedelta, timezone
+from types import SimpleNamespace
+
+from harness import FakeEntry, FakeHass, FakeState
+from homeassistant.util import dt as dt_util
+from heatpump_optimizer import boost
+from heatpump_optimizer import pump_arbiter as pa
+from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator
+
+T0 = datetime(2026, 1, 10, 6, 0, tzinfo=timezone.utc)
+#: The plan: 's' a space-heating step, '-' an idle one.
+DUTIES = "s-ss--s-s---ss-s"
+CYCLE_MIN = 30
+
+
+def plan():
+    n = len(DUTIES)
+    return SimpleNamespace(
+        timestamps=[T0 + timedelta(minutes=15 * i) for i in range(n)],
+        power_schedule=[1.5 if c == "s" else 0.0 for c in DUTIES],
+        dhw_power_schedule=[0.0] * n,
+        optimal_setpoints=[21.0] * n,
+    )
+
+
+async def install(phase):
+    ticks = []
+    armed = pa.async_track_time_interval
+    pa.async_track_time_interval = lambda _h, fn, _i: (ticks.append(fn), (lambda: None))[1]
+    hass = FakeHass({
+        "switch.hp": FakeState("off", last_updated=T0),
+        "sensor.hp_power": FakeState("0.0", unit="kW", last_updated=T0),
+    })
+    coord = HeatPumpOptimizerCoordinator(hass, FakeEntry(data={
+        "price_source": "entity", "price_entity": "sensor.prices", "weather_entity": "weather.home",
+        "heat_pump_switch_entity": "switch.hp", "heat_pump_power_entity": "sensor.hp_power",
+        "pump_duty_mode": "observe",
+    }))
+    coord._mode = "auto"
+    p = coord._optimization_result = plan()
+    writes = []
+    try:
+        for m in range(15 * len(DUTIES) + 1):
+            now = T0 + timedelta(minutes=m)
+            dt_util.freeze(now)
+            if m % CYCLE_MIN == phase:
+                coord._last_optimization = now
+                coord._measured_power = float(hass.states.get("sensor.hp_power").state)
+                i = min(m // 15, len(DUTIES) - 1)
+                boost.adopt_plan(coord, {"heat_pump_on": DUTIES[i] == "s", "power": p.power_schedule[i]})
+                await coord._apply_action()
+            for tick in list(ticks):
+                await tick(now)
+            for domain, service, _data in hass.services.calls:
+                if domain == "switch":
+                    writes.append((m, service))
+                    hass.states.set("switch.hp", FakeState(
+                        "on" if service == "turn_on" else "off", last_updated=now))
+            hass.services.calls.clear()
+            on = hass.states.get("switch.hp").state == "on"
+            hass.states.set("sensor.hp_power", FakeState("1.5" if on else "0.0", unit="kW", last_updated=now))
+        return [r["verdict"] for r in pa.diagnostics_view(coord)["ledger"]["steps"]], writes
+    finally:
+        dt_util.freeze(None)
+        pa.async_track_time_interval = armed
+
+
+def main():
+    runs = {phase: asyncio.run(install(phase)) for phase in (0, 14)}
+    for phase, (verdicts, writes) in runs.items():
+        print(f"phase {phase:2d} verdicts: {verdicts}")
+        print(f"phase {phase:2d} writes:   {writes}")
+    print("AGREE:", "yes" if runs[0][0][1:] == runs[14][0][1:] else "no")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/programme/delivery/2968.md b/dev/programme/delivery/2968.md
new file mode 100644
index 000000000..75d3bae03
--- /dev/null
+++ b/dev/programme/delivery/2968.md
@@ -0,0 +1 @@
+- [#2968](https://github.com/tvofi/heatpump_optimizer/pull/2968) — **open**, R10-SAV-ACTUATION: write the pump switch at the step boundary (R10-SAV-ACTUATION)
diff --git a/tests/closures.json b/tests/closures.json
index efc5debb3..81f232a28 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3943,6 +3943,7 @@
    "dev/audit/harnesses/r10_review_strength_mutants.py",
    "dev/audit/harnesses/r10_roster_push_race.sh",
    "dev/audit/harnesses/r10_roster_sync_base.py",
+   "dev/audit/harnesses/r10_sav_actuation_phase.py",
    "dev/audit/harnesses/r10_sav_baseline.py",
    "dev/audit/harnesses/r10_sav_baseline_mutants.py",
    "dev/audit/harnesses/r10_sav_null_terms.py",
diff --git a/tests/entities.py b/tests/entities.py
index 9f403adab..5bf88c382 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -40022,7 +40022,8 @@ _R10_COVERING_ALLOWED = {
                                                "entry is documented extrapolation, never published as current"),
     ("early_cutoff.py", "_planned_room"): (1, "index-bounded against the plan's own trajectory"),
     ("pump_arbiter.py", "_planned_room"): (1, "its caller's step_duty is None past the plan end"),
-    ("pump_arbiter.py", "step_duty"): (1, "returns None past the plan's last step"),
+    ("pump_arbiter.py", "_step_index"): (1, "returns None past the plan's last step; "
+                                             "step_duty and step_supply read it (#2492)"),
     ("pump_arbiter.py", "_share"): (1, "bounded by the plan's last step"),
 }
 
diff --git a/tests/features.py b/tests/features.py
index c86c95e14..15cf59a9b 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -73275,4 +73275,191 @@ R.check(
     f"{_he_l9_good.get('healthy')} {_he_l9_good.get('unhealthy_input')!r}",
 )
 
+R.section("supply switch at step boundaries (#2492, R10-SAV-ACTUATION)")
+# The cycle wrote the power switch once per interval, so a plan step's change
+# reached the pump at the next cycle, and a step's duty verdict depended on
+# where the cycle fell against the step grid. A synthetic install runs the
+# REAL coordinator's ``_apply_action`` at cycle phase 0 and 14 min, every
+# interval timer the arbiter arms fires each minute, the switch's writes are
+# applied to its state, and the meter follows the switch. The cycle's own
+# power sample is taken at the cycle, as ``_update_current_state`` takes it.
+from homeassistant.util import dt as _sa_dt
+from heatpump_optimizer import boost as _sa_boost
+from heatpump_optimizer import pump_arbiter as _sa_pa
+from heatpump_optimizer import store as _sa_store
+
+_SA_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
+_SA_DUTIES = "s-ss--s-s---ss-s"
+
+
+def _sa_plan():
+    n = len(_SA_DUTIES)
+    return SimpleNamespace(
+        timestamps=[_SA_T0 + timedelta(minutes=15 * i) for i in range(n)],
+        power_schedule=[1.5 if c == "s" else 0.0 for c in _SA_DUTIES],
+        dhw_power_schedule=[0.0] * n,
+        optimal_setpoints=[21.0] * n,
+    )
+
+
+async def _sa_install(phase, room_cut_at=None):
+    """Verdicts and switch writes of one synthetic install at cycle ``phase``."""
+    ticks = []
+    armed = _sa_pa.async_track_time_interval
+    _sa_pa.async_track_time_interval = lambda _h, fn, _i: (ticks.append(fn), (lambda: None))[1]
+    hass = FakeHass({
+        "switch.hp": FakeState("off", last_updated=_SA_T0),
+        "sensor.hp_power": FakeState("0.0", unit="kW", last_updated=_SA_T0),
+    })
+    coord = Coord(hass, FakeEntry(data={
+        **_LC_DATA, "heat_pump_switch_entity": "switch.hp",
+        "heat_pump_power_entity": "sensor.hp_power", "pump_duty_mode": "observe",
+    }))
+    coord._mode = "auto"
+    plan = coord._optimization_result = _sa_plan()
+    writes = []
+    try:
+        for m in range(15 * len(_SA_DUTIES) + 1):
+            now = _SA_T0 + timedelta(minutes=m)
+            _sa_dt.freeze(now)
+            if m % 30 == phase:
+                coord._last_optimization = now
+                coord._measured_power = float(hass.states.get("sensor.hp_power").state)
+                i = min(m // 15, len(_SA_DUTIES) - 1)
+                _sa_boost.adopt_plan(coord, {"heat_pump_on": _SA_DUTIES[i] == "s", "power": plan.power_schedule[i]})
+                await coord._apply_action()
+            if m == room_cut_at:
+                # An early cut-off, as ``early_cutoff.on_room_event`` writes it.
+                await _sa_pa.switch_supply(hass, "switch.hp", False)
+            for tick in list(ticks):
+                await tick(now)
+            for domain, service, _data in hass.services.calls:
+                if domain == "switch":
+                    writes.append((m, service))
+                    hass.states.set("switch.hp", FakeState(
+                        "on" if service == "turn_on" else "off", last_updated=now))
+            hass.services.calls.clear()
+            on = hass.states.get("switch.hp").state == "on"
+            hass.states.set("sensor.hp_power", FakeState("1.5" if on else "0.0", unit="kW", last_updated=now))
+        verdicts = [r["verdict"] for r in _sa_pa.diagnostics_view(coord)["ledger"]["steps"]]
+    finally:
+        _sa_dt.freeze(None)
+        _sa_pa.async_track_time_interval = armed
+    return verdicts, writes
+
+
+_sa_v0, _sa_w0 = _asyncio.run(_sa_install(0))
+_sa_v14, _sa_w14 = _asyncio.run(_sa_install(14))
+# Step 0 precedes the phase-14 install's first cycle, so it is the one step
+# the two installs may book apart.
+R.check(
+    "a synthetic install at cycle phase 0 and at 14 min books identical duty verdicts (#2492)",
+    len(_sa_v0) == len(_SA_DUTIES) and _sa_v0[1:] == _sa_v14[1:],
+    f"phase 0: {_sa_v0}; phase 14: {_sa_v14}",
+)
+_sa_boundaries = [m for m, _s in _sa_w14 if m % 15 == 0]
+R.check(
+    "the step tick writes the switch at the boundary of each step whose command changes",
+    [m // 15 for m in _sa_boundaries]
+    == [i for i in range(1, len(_SA_DUTIES)) if (_SA_DUTIES[i] == "s") != (_SA_DUTIES[i - 1] == "s")],
+    f"{_sa_w14}",
+)
+# A cut the cycle did not write holds across a step the plan keeps on: the
+# tick writes a change, never the same command again (early_cutoff.py).
+_sa_vc, _sa_wc = _asyncio.run(_sa_install(0, room_cut_at=34))
+R.check(
+    "an early cut-off holds across a step boundary the plan keeps on",
+    [w for w in _sa_wc if 34 < w[0] < 60] == [],
+    f"{_sa_wc}",
+)
+# The tick is a second writer of the switch, between cycles, so it writes only
+# where the cycle's own write would have come from the plan's step. One cycle
+# writes step 0's ON; the tick at step 1, whose plan command is off, writes OFF
+# unless ``guard`` holds the cycle's write off the plan. Each guard's null
+# control is the unguarded run, which writes the OFF.
+async def _sa_guarded(guard=None):
+    ticks, dropped = [], []
+    armed = _sa_pa.async_track_time_interval
+    _sa_pa.async_track_time_interval = lambda _h, fn, _i: (ticks.append(fn), (lambda: dropped.append(fn)))[1]
+    hass = FakeHass({"switch.hp": FakeState("off", last_updated=_SA_T0)})
+    coord = Coord(hass, FakeEntry(data={
+        **_LC_DATA, "heat_pump_switch_entity": "switch.hp", "pump_duty_mode": "observe",
+    }))
+    coord._mode = "auto"
+    coord._optimization_result = _sa_plan()
+    try:
+        _sa_dt.freeze(_SA_T0)
+        coord._last_optimization = _SA_T0
+        _sa_boost.adopt_plan(coord, {"heat_pump_on": True, "power": 1.5})
+        await coord._apply_action()
+        if guard == "unload":
+            await coord._apply_action()  # a second cycle arms nothing more
+        hass.services.calls.clear()
+        now = _SA_T0 + timedelta(minutes=15)
+        _sa_dt.freeze(now)
+        if guard == "boost":
+            _sa_boost.held_for(coord).until[_sa_boost.CHANNEL_SPACE] = now + timedelta(hours=1)
+        elif guard == "sysid":
+            coord._current_action = {**coord._current_action, "mode": "system_identification"}
+        elif guard == "comfort":
+            coord._mode = "comfort"
+        elif guard == "stale":
+            coord._last_optimization = now - timedelta(days=1)
+        elif guard == "released":
+            coord._entry_released = True
+        for tick in list(ticks):
+            await tick(now)
+        writes = [service for domain, service, _d in hass.services.calls if domain == "switch"]
+        held = _sa_pa.state_for(coord)
+        armed_before = held.supply_unsub is not None and not dropped
+        if guard == "unload":
+            await _sa_pa.release(coord)
+        return writes, armed_before, dropped == ticks and held.supply_unsub is None
+    finally:
+        _sa_dt.freeze(None)
+        _sa_pa.async_track_time_interval = armed
+
+
+_sa_g = {g: _asyncio.run(_sa_guarded(g)) for g in (None, "boost", "sysid", "comfort", "stale", "released", "unload")}
+R.check(
+    "the step tick writes the plan's OFF at a boundary when nothing holds the cycle's write off the plan",
+    _sa_g[None][0] == ["turn_off"],
+    f"{_sa_g[None]}",
+)
+for _sa_name, _sa_key in (
+    ("a live boost across a boundary whose plan step is off", "boost"),
+    ("a system_identification action", "sysid"),
+    ("a fixed (comfort) mode", "comfort"),
+    ("a stale plan", "stale"),
+    ("a released entry", "released"),
+):
+    R.check(
+        f"the step tick writes nothing at a boundary under {_sa_name}",
+        _sa_g[_sa_key][0] == [],
+        f"{_sa_g[_sa_key]}",
+    )
+R.check(
+    "unload drops the one step tick two cycles armed",
+    _sa_g["unload"][1] is True and _sa_g["unload"][2] is True and _sa_g[None][2] is False,
+    f"unload {_sa_g['unload']}; kept {_sa_g[None]}",
+)
+# The pump_duty record's held slots are declared, every one the arbiter can
+# write: the silent switch (D15 L5) and the GCHV night registers (#1913).
+_sa_record = {"written": {
+    **{slot: [v, _SA_T0.isoformat()] for slot, v in (
+        ("mode", "Heating"), ("dhw_setpoint", 50.0), ("space_setpoint", 35.0), ("silent", True),
+        ("night_start_hour", 22), ("night_start_minute", 0), ("night_end_hour", 6), ("night_end_minute", 30),
+    )},
+}}
+R.check(
+    "every slot the pump arbiter persists is declared in the pump_duty store domain",
+    sorted(_sa_record["written"]) == sorted(_sa_pa._SLOTS + _sa_pa._NIGHT_SLOTS)
+    and _sa_store.off_domain("heatpump_optimizer_e_pump_duty", _sa_record) == []
+    and _sa_store.off_domain(
+        "heatpump_optimizer_e_pump_duty", {"written": {"silent": ["on", _SA_T0.isoformat()]}}
+    ) == ["written/silent/0"],
+    f"{_sa_store.off_domain('heatpump_optimizer_e_pump_duty', _sa_record)}",
+)
+
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.bb3f033b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.bb3f033b.json
deleted file mode 100644
index 081bc3030..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.bb3f033b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_action BOOLOP bb3f033b",
-  "killed_by": "tests/features.py",
-  "old": "        if switch_entity and not skip_off:",
-  "reason": "Recorded by `mutation_table.py --drain` against aca6ea4567034a05e64edcfd8355d42a8079427d: BOOLOP (`if switch_entity or not skip_off:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.GUARD_OFF.bb3f033b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.GUARD_OFF.bb3f033b.json
deleted file mode 100644
index 8707c8da4..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.GUARD_OFF.bb3f033b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_action GUARD_OFF bb3f033b",
-  "killed_by": "tests/features.py",
-  "old": "        if switch_entity and not skip_off:",
-  "reason": "Recorded by `mutation_table.py --drain` against e30b24bbc45afd1174f64f7051d05021e31b6a89: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.BOOLOP.aa491430.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.BOOLOP.aa491430.json
new file mode 100644
index 000000000..ff6bc8cdb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.BOOLOP.aa491430.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._write_supply BOOLOP aa491430",
+  "killed_by": "tests/features.py",
+  "old": "        if switch_entity and value is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if switch_entity or value is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.GUARD_OFF.aa491430.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.GUARD_OFF.aa491430.json
new file mode 100644
index 000000000..27e0c57a5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._write_supply.GUARD_OFF.aa491430.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._write_supply GUARD_OFF aa491430",
+  "killed_by": "tests/features.py",
+  "old": "        if switch_entity and value is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_apply_result_payload.BOOLOP.09efd8da.json b/tests/mutation_ledger/killed_by/coordinator.py/_apply_result_payload.BOOLOP.09efd8da.json
deleted file mode 100644
index bc58adb27..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_apply_result_payload.BOOLOP.09efd8da.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_apply_result_payload BOOLOP 09efd8da",
-  "killed_by": "tests/features.py",
-  "old": "                        if result.heat_pump_on_schedule and idx < len(result.heat_pump_on_schedule)",
-  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if result.heat_pump_on_schedule or idx < len(result.heat_pump_on_schedule)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.BOOLOP.519a7ed9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.BOOLOP.519a7ed9.json
deleted file mode 100644
index 299e74c37..000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.BOOLOP.519a7ed9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.get_current_action BOOLOP 519a7ed9",
-  "killed_by": "tests/stress.py",
-  "old": "            if result.dhw_power_schedule and i < len(result.dhw_power_schedule)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against bd79bc9e0e7ee5bb8d7fac6a400f5e077f3c3266: BOOLOP (`if result.dhw_power_schedule or i < len(result.dhw_power_schedule)`) took tests/stress.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
new file mode 100644
index 000000000..8b4be5e95
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index BOOLOP fe5ed606",
+  "killed_by": "tests/features.py",
+  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if i < 0 or (i == len(stamps) - 1 or now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
new file mode 100644
index 000000000..885b282bb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index CMP_BOUND fe5ed606",
+  "killed_by": "tests/features.py",
+  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i <= 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=72. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
new file mode 100644
index 000000000..554f0d548
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index GUARD_OFF fe5ed606",
+  "killed_by": "tests/features.py",
+  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
new file mode 100644
index 000000000..8ad75207e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index RETURN_DEL 67f638e2",
+  "killed_by": "tests/features.py",
+  "old": "    return i",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/live_power_kw.RETURN_DEL.2899b10f.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/live_power_kw.RETURN_DEL.2899b10f.json
new file mode 100644
index 000000000..b09e562ec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/live_power_kw.RETURN_DEL.2899b10f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:live_power_kw RETURN_DEL 2899b10f",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return reading.value if reading.ok else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/note_supply.GUARD_OFF.ed5e93ab.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/note_supply.GUARD_OFF.ed5e93ab.json
new file mode 100644
index 000000000..c623facd8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/note_supply.GUARD_OFF.ed5e93ab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:note_supply GUARD_OFF ed5e93ab",
+  "killed_by": "tests/features.py",
+  "old": "    if held.supply_unsub is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/release_supply.GUARD_OFF.7725d105.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/release_supply.GUARD_OFF.7725d105.json
new file mode 100644
index 000000000..e43f0472c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/release_supply.GUARD_OFF.7725d105.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:release_supply GUARD_OFF 7725d105",
+  "killed_by": "tests/features.py",
+  "old": "    if unsub is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.BOOLOP.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.BOOLOP.fe5ed606.json
deleted file mode 100644
index 40ed6ab0d..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.BOOLOP.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty BOOLOP fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 52f698905868c9140ed213ea542c44053fca7096: BOOLOP (`if i < 0 or (i == len(stamps) - 1 or now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.CMP_BOUND.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.CMP_BOUND.fe5ed606.json
deleted file mode 100644
index c398ff410..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.CMP_BOUND.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty CMP_BOUND fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 52f698905868c9140ed213ea542c44053fca7096: CMP_BOUND (`if i <= 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=72. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.45217e20.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.45217e20.json
new file mode 100644
index 000000000..af96c5305
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.45217e20.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty GUARD_OFF 45217e20",
+  "killed_by": "tests/guard_pins.py",
+  "old": "    if i is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.fe5ed606.json
deleted file mode 100644
index 5a8c61931..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_duty.GUARD_OFF.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_duty GUARD_OFF fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 52f698905868c9140ed213ea542c44053fca7096: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.030cf220.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.030cf220.json
new file mode 100644
index 000000000..116bf7d0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.030cf220.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply GUARD_OFF 030cf220",
+  "killed_by": "tests/features.py",
+  "old": "    if boosts.active(boost.CHANNEL_SPACE, now) or boosts.active(boost.CHANNEL_DHW, now):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.44d997bd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.44d997bd.json
new file mode 100644
index 000000000..723006ee5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.44d997bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply GUARD_OFF 44d997bd",
+  "killed_by": "tests/features.py",
+  "old": "    if (inp.action or {}).get(\"mode\") == \"system_identification\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.c58cb373.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.c58cb373.json
new file mode 100644
index 000000000..be535eb98
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.GUARD_OFF.c58cb373.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply GUARD_OFF c58cb373",
+  "killed_by": "tests/features.py",
+  "old": "    if inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.plan_stale or inp.plan is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.RETURN_DEL.7f5bc4e7.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.RETURN_DEL.7f5bc4e7.json
new file mode 100644
index 000000000..c75de7057
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/step_supply.RETURN_DEL.7f5bc4e7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:step_supply RETURN_DEL 7f5bc4e7",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return None if i is None or i >= len(inp.plan.power_schedule or ()) else plan_step_runs(inp.plan, i)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.3bc78a66.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.3bc78a66.json
new file mode 100644
index 000000000..7836f98c6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.3bc78a66.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF 3bc78a66",
+  "killed_by": "tests/features.py",
+  "old": "    if inp.entry_released:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.aa236a67.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.aa236a67.json
new file mode 100644
index 000000000..d7296832b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.aa236a67.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF aa236a67",
+  "killed_by": "tests/features.py",
+  "old": "    if on != last:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.dcaaed0d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.dcaaed0d.json
new file mode 100644
index 000000000..ca8df4587
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.dcaaed0d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF dcaaed0d",
+  "killed_by": "tests/harness_headers.py",
+  "old": "    if held.supply is None or held.supply[0] == step:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/harness_headers.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.f90e3098.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.f90e3098.json
new file mode 100644
index 000000000..ff770e19f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.GUARD_OFF.f90e3098.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_tick GUARD_OFF f90e3098",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    if on is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.BOOLOP.92bdc254.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.BOOLOP.92bdc254.json
new file mode 100644
index 000000000..eca52d779
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.BOOLOP.92bdc254.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_write BOOLOP 92bdc254",
+  "killed_by": "tests/features.py",
+  "old": "    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if on or not ((signals.space_blocked or signals.dhw_blocked) or signals.mode.cooling):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.GUARD_OFF.92bdc254.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.GUARD_OFF.92bdc254.json
new file mode 100644
index 000000000..d8f3cd21d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.GUARD_OFF.92bdc254.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_write GUARD_OFF 92bdc254",
+  "killed_by": "tests/features.py",
+  "old": "    if on or not ((signals.space_blocked and signals.dhw_blocked) or signals.mode.cooling):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.RETURN_DEL.da9e8e97.json
new file mode 100644
index 000000000..3c2205ee8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/supply_write.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:supply_write RETURN_DEL da9e8e97",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.BOOLOP.e5c45a76.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.BOOLOP.e5c45a76.json
new file mode 100644
index 000000000..43a251f28
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.BOOLOP.e5c45a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs BOOLOP e5c45a76",
+  "killed_by": "tests/features.py",
+  "old": "    if runs and i < len(runs):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if runs or i < len(runs):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.e5c45a76.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.e5c45a76.json
new file mode 100644
index 000000000..08a6b94be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.e5c45a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs CMP_BOUND e5c45a76",
+  "killed_by": "tests/features.py",
+  "old": "    if runs and i < len(runs):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if runs and i <= len(runs):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.f0f14778.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.f0f14778.json
new file mode 100644
index 000000000..97b6980e7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.CMP_BOUND.f0f14778.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs CMP_BOUND f0f14778",
+  "killed_by": "tests/features.py",
+  "old": "    return planned_draw_runs(result.power_schedule[i], dhw[i] if i < len(dhw) else 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return planned_draw_runs(result.power_schedule[i], dhw[i] if i <= len(dhw) else 0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.GUARD_OFF.e5c45a76.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.GUARD_OFF.e5c45a76.json
new file mode 100644
index 000000000..a9f23b1bf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.GUARD_OFF.e5c45a76.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs GUARD_OFF e5c45a76",
+  "killed_by": "tests/features.py",
+  "old": "    if runs and i < len(runs):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.RETURN_DEL.f0f14778.json b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.RETURN_DEL.f0f14778.json
new file mode 100644
index 000000000..2dc9d74ae
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/plan_step_runs.RETURN_DEL.f0f14778.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:plan_step_runs RETURN_DEL f0f14778",
+  "killed_by": "tests/features.py",
+  "old": "    return planned_draw_runs(result.power_schedule[i], dhw[i] if i < len(dhw) else 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/seam_map.json b/tests/seam_map.json
index d58fe76fe..729e4bf64 100644
--- a/tests/seam_map.json
+++ b/tests/seam_map.json
@@ -6,6 +6,7 @@
   "_adopt_away_override": "core",
   "_adopt_system_identification": "core",
   "_apply_action": "core",
+  "_write_supply": "core",
   "_apply_buffer_cooling_rate": "core",
   "_apply_comfort_weight": "learning",
   "_apply_cop_scale": "learning",
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index b76cfb616..f7b4c0ac8 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17724,
+ "class_excess_loc": 17711,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -11,7 +11,7 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 8065,
+ "max_class_loc": 8063,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,

