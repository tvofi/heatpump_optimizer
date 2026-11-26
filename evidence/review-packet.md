# Review packet #3872
head: e4a8523d89c02aa9b4f7c477c6ecfabed09689ec
base: d9100de781ec174960655fdab1a5af48c303d7bd

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139574065844 success
arch-score / arch-score id=139619853197 success
arm id=139573163828 skipped
budget-raise-gate / budget-raise-gate id=139619854141 success
cancel-superseded id=139619915159 success
codeql id=139573651985 skipped
codeql / Analyze (actions) id=139619853439 success
codeql / Analyze (javascript-typescript) id=139619853185 success
codeql / Analyze (python) id=139619853399 success
gate id=139574370031 failure
governance id=139573651664 skipped
governance / env-matrix id=139619853139 success
governance / instrument-self-tests id=139619853257 success
governance / policy-docs id=139619853515 success
governance / record id=139619853551 skipped
governance / wave-script id=139619853460 success
hassfest id=139573652203 skipped
hassfest / hassfest id=139619853993 success
kernel-points id=139619853102 skipped
pr-contract id=139574372286 skipped
prelude id=139619851422 success
refresh id=139619852141 success
sweep-self id=139575042585 skipped
tests id=139573651238 skipped
tests / arch-instrument id=139619854431 success
tests / briefs id=139619853596 success
tests / browser id=139619855357 success
tests / ci-ratchet id=139619856149 skipped
tests / claims-autofix id=139619856394 skipped
tests / closure-scope id=139619853400 success
tests / closures id=139619854653 success
tests / closures-autofix id=139619856511 skipped
tests / coverage id=139619855006 success
tests / coverage-ratchet id=139619856472 success
tests / fast (3.14) id=139619855984 success
tests / graders-head-copy id=139619855423 success
tests / lane-proofs id=139619855954 success
tests / mutation id=139619853868 success
tests / mutation-autofix id=139619855007 skipped
tests / mutation-pins id=139619855286 skipped
tests / nightly-ha (2025.2.0) id=139619852700 failure
tests / nightly-ha (stable) id=139619852689 failure
tests / nightly-status id=139619851587 failure
tests / replay id=139619852838 in_progress
tests / typing id=139619854746 success
validate id=139573652739 skipped
validate / validate-hacs id=139619854274 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at e4a8523d89c02aa9b4f7c477c6ecfabed09689ec in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item b41faa3f: R11-OWNER-MODE-LEGS
NOTE body item 021db87b: R11-OWNER-FROST-HOLD
NOTE body item 041d2bd4: R11-OWNER-FAULT-TEXT
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=91773476edb3 ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/comment_ratchet.py
             `tests/comment_ratchet.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py HEAD
             `dev/audit/harnesses/r11_owner_fault_hold_mutants.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 7 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.9e9a864a.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.9e9a864a.json
new file mode 100644
index 0000000000..1917820518
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.9e9a864a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_action BOOLOP 9e9a864a",
+  "killed_by": "tests/features.py",
+  "old": "        await off_restore.async_cycle(self.hass, self.entry, _ctx_of(self)._config, self._mode == MODE_OFF, stale and not fault_hold.held(self.entry))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`await off_restore.async_cycle(self.hass, self.entry, _ctx_of(self)._config, self._mode == MODE_OFF, stale or not fault_hold.held(self.entry))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=31."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.0bf30dbd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.13e8b4c7.json
similarity index 62%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.0bf30dbd.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.13e8b4c7.json
index 99332cf198..f3772fea00 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.0bf30dbd.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.13e8b4c7.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._command_frequency GUARD_OFF 0bf30dbd",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._command_frequency GUARD_OFF 13e8b4c7",
   "killed_by": "tests/features.py",
-  "old": "        if not entity_id or self._freq_mode() != FREQ_MODE_CONTROL or self._mode == MODE_OFF or _plan_let_go(self):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "old": "        if not entity_id or self._freq_mode() != FREQ_MODE_CONTROL or self._mode == MODE_OFF or _plan_let_go(self) or fault_hold.held(self.entry):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json b/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json
index 017b4d79d1..62df02cc82 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:_missed GUARD_OFF f28578a3",
   "killed_by": "tests/block_duty.py",
   "old": "    if planned == \"dhw\" and actual == \"idle\" and _not_startable(row):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json
index 1227a261db..f317aa5943 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:_not_startable CMP_BOUND 452b7046",
   "killed_by": "tests/block_duty.py",
   "old": "    return start is not None and tank is not None and float(tank) >= start",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return start is not None and tank is not None and float(tank) > start`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return start is not None and tank is not None and float(tank) > start`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json
index 5dcf7ebe8b..0a64fb991f 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:_not_startable RETURN_DEL 452b7046",
   "killed_by": "tests/block_duty.py",
   "old": "    return start is not None and tank is not None and float(tank) >= start",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/observe.BOOLOP.a38120fc.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.BOOLOP.a38120fc.json
new file mode 100644
index 0000000000..6e5989dc0b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.BOOLOP.a38120fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe BOOLOP a38120fc",
+  "killed_by": "tests/features.py",
+  "old": "    if ran is not None and now - start >= RUN_SETTLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if ran is not None or now - start >= RUN_SETTLE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/observe.CMP_BOUND.a38120fc.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.CMP_BOUND.a38120fc.json
new file mode 100644
index 0000000000..af35c053b8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.CMP_BOUND.a38120fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe CMP_BOUND a38120fc",
+  "killed_by": "tests/features.py",
+  "old": "    if ran is not None and now - start >= RUN_SETTLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if ran is not None and now - start > RUN_SETTLE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.3c85dd51.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.3c85dd51.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.3c85dd51.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.3c85dd51.json
index 9fe3e74eb5..ec11b3b32d 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.3c85dd51.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.3c85dd51.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF 3c85dd51",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF 3c85dd51",
   "killed_by": "tests/features.py",
   "old": "    if row is None or row[\"start\"] != start:",
-  "reason": "pump-duty arbiter revision; `if row is None or row[\"start\"] != start:` -> `if False:` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `if row is None or row[\"start\"] != start:` -> `if False:` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.57f875bd.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.57f875bd.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.57f875bd.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.57f875bd.json
index ae3eb694aa..74b2dc9bff 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.57f875bd.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.57f875bd.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF 57f875bd",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF 57f875bd",
   "killed_by": "tests/features.py",
   "old": "        if row is not None:",
-  "reason": "pump-duty arbiter revision; `if row is not None:` -> `if False:` fails 3 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `if row is not None:` -> `if False:` fails 3 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.a38120fc.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.a38120fc.json
new file mode 100644
index 0000000000..1b28bcdf62
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.a38120fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF a38120fc",
+  "killed_by": "tests/features.py",
+  "old": "    if ran is not None and now - start >= RUN_SETTLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.f2ad4d4c.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.f2ad4d4c.json
similarity index 54%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.f2ad4d4c.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.f2ad4d4c.json
index 0c55cc7615..1296d847da 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.f2ad4d4c.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.f2ad4d4c.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF f2ad4d4c",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF f2ad4d4c",
   "killed_by": "tests/features.py",
   "old": "    elif row[\"plan\"] is not inp.plan:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json
index 2c46caa81c..f1f257d9dd 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict BOOLOP 2bdf9629",
   "killed_by": "tests/features.py",
   "old": "    elif actual == planned or (planned == \"both\" and actual != \"idle\"):",
-  "reason": "pump-duty arbiter revision; `elif actual == planned or (planned == \"both\" and actual != \"idle\"):` -> `elif actual == planned or (planned == \"both\" or actual != \"idle\"):` fails 1 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `elif actual == planned or (planned == \"both\" and actual != \"idle\"):` -> `elif actual == planned or (planned == \"both\" or actual != \"idle\"):` fails 1 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json
index b22b442fcb..6794122051 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict BOOLOP af494230",
   "killed_by": "tests/features.py",
   "old": "    rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C",
-  "reason": "pump-duty arbiter revision; `rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` -> `rose = None not in (tank, row[\"tank\"]) or float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` -> `rose = None not in (tank, row[\"tank\"]) or float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json
index 4b2b07e75b..17cf4238da 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict CMP_BOUND af494230",
   "killed_by": "tests/features.py",
   "old": "    rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C",
-  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) > TANK_RISE_C`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) > TANK_RISE_C`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json
index 0fd3bcfca8..d845cc58a6 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF 2bdf9629",
   "killed_by": "tests/features.py",
   "old": "    elif actual == planned or (planned == \"both\" and actual != \"idle\"):",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.af4ac328.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.af4ac328.json
new file mode 100644
index 0000000000..df21f438de
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.af4ac328.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF af4ac328",
+  "killed_by": "tests/features.py",
+  "old": "    elif planned is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.f7f7cbce.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.ca33e38f.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.f7f7cbce.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.ca33e38f.json
index a5c0d609f0..2ebf4fbdde 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.f7f7cbce.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.ca33e38f.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF f7f7cbce",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF ca33e38f",
   "killed_by": "tests/block_duty.py",
-  "old": "    if mode != DUTY_CONTROL or _pump_off(inp, held):",
+  "old": "    if row.get(\"faulted\"):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.d746330a.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.d746330a.json
deleted file mode 100644
index e745e4d393..0000000000
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.d746330a.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF d746330a",
-  "killed_by": "tests/features.py",
-  "old": "    if planned is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/on_room_event.GUARD_OFF.6501682d.json b/tests/mutation_ledger/killed_by/early_cutoff.py/on_room_event.GUARD_OFF.6501682d.json
new file mode 100644
index 0000000000..d89afd5662
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/on_room_event.GUARD_OFF.6501682d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:on_room_event GUARD_OFF 6501682d",
+  "killed_by": "tests/structure.py",
+  "old": "    if fault_hold.consult(wiring.entry, inp, now):  # a faulted pump is not switched off",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # a faulted pump is not switched off`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_clear.BOOLOP.e5dfa31c.json b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.BOOLOP.e5dfa31c.json
new file mode 100644
index 0000000000..05af71b255
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.BOOLOP.e5dfa31c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_clear BOOLOP e5dfa31c",
+  "killed_by": "tests/features.py",
+  "old": "    if not any(other.holding and other.hass is hass for other in list(_STATES.values())):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not any(other.holding or other.hass is hass for other in list(_STATES.values())):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_clear.GUARD_OFF.e5dfa31c.json b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.GUARD_OFF.e5dfa31c.json
new file mode 100644
index 0000000000..8c4d609b7f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.GUARD_OFF.e5dfa31c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_clear GUARD_OFF e5dfa31c",
+  "killed_by": "tests/features.py",
+  "old": "    if not any(other.holding and other.hass is hass for other in list(_STATES.values())):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.51d9802d.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.51d9802d.json
new file mode 100644
index 0000000000..295d093a33
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.51d9802d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move BOOLOP 51d9802d",
+  "killed_by": "tests/features.py",
+  "old": "    elif latch.holding and not on:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`elif latch.holding or not on:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.97208b64.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.97208b64.json
new file mode 100644
index 0000000000..5cd52fec60
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.97208b64.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move BOOLOP 97208b64",
+  "killed_by": "tests/features.py",
+  "old": "    if on and not latch.holding:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if on or not latch.holding:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.51d9802d.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.51d9802d.json
new file mode 100644
index 0000000000..d48f5d9e87
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.51d9802d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move GUARD_OFF 51d9802d",
+  "killed_by": "tests/features.py",
+  "old": "    elif latch.holding and not on:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.97208b64.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.97208b64.json
new file mode 100644
index 0000000000..a6441f7bd9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.97208b64.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move GUARD_OFF 97208b64",
+  "killed_by": "tests/features.py",
+  "old": "    if on and not latch.holding:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.RETURN_DEL.d2b1cb1d.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.RETURN_DEL.d2b1cb1d.json
new file mode 100644
index 0000000000..1098adb42d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.RETURN_DEL.d2b1cb1d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move RETURN_DEL d2b1cb1d",
+  "killed_by": "tests/features.py",
+  "old": "    return on",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/consult.RETURN_DEL.3a02bb96.json b/tests/mutation_ledger/killed_by/fault_hold.py/consult.RETURN_DEL.3a02bb96.json
new file mode 100644
index 0000000000..5e91f0cd2d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/consult.RETURN_DEL.3a02bb96.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:consult RETURN_DEL 3a02bb96",
+  "killed_by": "tests/features.py",
+  "old": "    return holding(entry, inp.hass, inp.config, off=inp.mode == MODE_OFF, released=inp.entry_released, now=now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/gate.GUARD_OFF.fb639107.json b/tests/mutation_ledger/killed_by/fault_hold.py/gate.GUARD_OFF.fb639107.json
new file mode 100644
index 0000000000..f5fcb2560b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/gate.GUARD_OFF.fb639107.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:gate GUARD_OFF fb639107",
+  "killed_by": "tests/features.py",
+  "old": "    if value is not False or not consult(entry, inp):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=77."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/held.BOOLOP.2e25e783.json b/tests/mutation_ledger/killed_by/fault_hold.py/held.BOOLOP.2e25e783.json
new file mode 100644
index 0000000000..3c883cd481
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/held.BOOLOP.2e25e783.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:held BOOLOP 2e25e783",
+  "killed_by": "tests/features.py",
+  "old": "    return latch is not None and latch.holding",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return latch is not None or latch.holding`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/held.RETURN_DEL.2e25e783.json b/tests/mutation_ledger/killed_by/fault_hold.py/held.RETURN_DEL.2e25e783.json
new file mode 100644
index 0000000000..5ff1300f5d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/held.RETURN_DEL.2e25e783.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:held RETURN_DEL 2e25e783",
+  "killed_by": "tests/features.py",
+  "old": "    return latch is not None and latch.holding",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.411a9678.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.411a9678.json
new file mode 100644
index 0000000000..1923a532e6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.411a9678.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding BOOLOP 411a9678",
+  "killed_by": "tests/features.py",
+  "old": "    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return _move(latch, hass, latch.since is not None or now - latch.since >= FAULT_HOLD_AFTER)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.f2e3b5f4.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.f2e3b5f4.json
new file mode 100644
index 0000000000..4890d441b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.f2e3b5f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding BOOLOP f2e3b5f4",
+  "killed_by": "tests/features.py",
+  "old": "    if reading.flag is False and reading.ok:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if reading.flag is False or reading.ok:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=34."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.CLAMP_DROP.ea67468b.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CLAMP_DROP.ea67468b.json
new file mode 100644
index 0000000000..b1ce1f8487
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CLAMP_DROP.ea67468b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding CLAMP_DROP ea67468b",
+  "killed_by": "tests/features.py",
+  "old": "        latch.since = min(dt_util.as_utc(changed), now) if changed is not None else now",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`latch.since = (dt_util.as_utc(changed)) if changed is not None else now`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.CMP_BOUND.411a9678.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CMP_BOUND.411a9678.json
new file mode 100644
index 0000000000..c2204bd049
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CMP_BOUND.411a9678.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding CMP_BOUND 411a9678",
+  "killed_by": "tests/features.py",
+  "old": "    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return _move(latch, hass, latch.since is not None and now - latch.since > FAULT_HOLD_AFTER)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.0bd5a755.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.0bd5a755.json
new file mode 100644
index 0000000000..08aa3d51dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.0bd5a755.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF 0bd5a755",
+  "killed_by": "tests/features.py",
+  "old": "    if released:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.8317e5f0.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.8317e5f0.json
new file mode 100644
index 0000000000..0f207792c8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.8317e5f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF 8317e5f0",
+  "killed_by": "tests/features.py",
+  "old": "    if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.e33caa55.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.e33caa55.json
new file mode 100644
index 0000000000..28543119a5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.e33caa55.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF e33caa55",
+  "killed_by": "tests/features.py",
+  "old": "    elif reading.flag and reading.ok and latch.since is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=34."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.f2e3b5f4.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.f2e3b5f4.json
new file mode 100644
index 0000000000..5625829c8d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.f2e3b5f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF f2e3b5f4",
+  "killed_by": "tests/features.py",
+  "old": "    if reading.flag is False and reading.ok:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.411a9678.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.411a9678.json
new file mode 100644
index 0000000000..c4411b2fa4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.411a9678.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding RETURN_DEL 411a9678",
+  "killed_by": "tests/features.py",
+  "old": "    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=35."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.6c549d41.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.6c549d41.json
new file mode 100644
index 0000000000..cd3fd38a6c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.6c549d41.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding RETURN_DEL 6c549d41",
+  "killed_by": "tests/features.py",
+  "old": "        return _move(latch, hass, False)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/release.BOOLOP.88f5261f.json b/tests/mutation_ledger/killed_by/fault_hold.py/release.BOOLOP.88f5261f.json
new file mode 100644
index 0000000000..d3d0aa213b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/release.BOOLOP.88f5261f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:release BOOLOP 88f5261f",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    was = latch is not None and latch.holding",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`was = latch is not None or latch.holding`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/release.GUARD_OFF.f01954aa.json b/tests/mutation_ledger/killed_by/fault_hold.py/release.GUARD_OFF.f01954aa.json
new file mode 100644
index 0000000000..c8699dcc0c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/release.GUARD_OFF.f01954aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:release GUARD_OFF f01954aa",
+  "killed_by": "tests/features.py",
+  "old": "    if was:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/release.RETURN_DEL.25a124b5.json b/tests/mutation_ledger/killed_by/fault_hold.py/release.RETURN_DEL.25a124b5.json
new file mode 100644
index 0000000000..158cb6689d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/release.RETURN_DEL.25a124b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:release RETURN_DEL 25a124b5",
+  "killed_by": "tests/features.py",
+  "old": "    return was",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/unload_holds.RETURN_DEL.d858ff0c.json b/tests/mutation_ledger/killed_by/fault_hold.py/unload_holds.RETURN_DEL.d858ff0c.json
new file mode 100644
index 0000000000..a0ba58aae6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/unload_holds.RETURN_DEL.d858ff0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:unload_holds RETURN_DEL d858ff0c",
+  "killed_by": "tests/features.py",
+  "old": "    return held(entry) or entry in _RELEASED_HOLDING",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_curve.py/publish.GUARD_OFF.e55abc27.json b/tests/mutation_ledger/killed_by/heat_curve.py/publish.GUARD_OFF.e55abc27.json
new file mode 100644
index 0000000000..89eed353ce
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_curve.py/publish.GUARD_OFF.e55abc27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_curve.py:publish GUARD_OFF e55abc27",
+  "killed_by": "tests/structure.py",
+  "old": "    if fault_hold.holding(entry, hass, config, off=mode_off, released=released):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.8444642c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.8444642c.json
new file mode 100644
index 0000000000..a362be50cd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.8444642c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 8444642c",
+  "killed_by": "tests/structure.py",
+  "old": "    if mode != DUTY_CONTROL or _pump_off(inp, held) or _fault_stands(inp.hass, held, faulted):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.88e2f26e.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.GUARD_OFF.6379a114.json
similarity index 77%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.88e2f26e.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.GUARD_OFF.6379a114.json
index 00db37f89b..1d0542261c 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.88e2f26e.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.GUARD_OFF.6379a114.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_release_row GUARD_OFF 88e2f26e",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_fault_stands GUARD_OFF 6379a114",
   "killed_by": "tests/features.py",
-  "old": "    if coord is None:",
+  "old": "    if faulted:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.RETURN_DEL.20ad27fb.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.RETURN_DEL.20ad27fb.json
new file mode 100644
index 0000000000..6496088a39
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.RETURN_DEL.20ad27fb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_fault_stands RETURN_DEL 20ad27fb",
+  "killed_by": "tests/features.py",
+  "old": "    return faulted",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.ba67817a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.bede1f64.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.ba67817a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.bede1f64.json
index 5085e99d55..7502577eb3 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.ba67817a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.bede1f64.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_lead_mode GUARD_OFF ba67817a",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_lead_mode GUARD_OFF bede1f64",
   "killed_by": "tests/features.py",
-  "old": "        if inp.entry_released or inp.mode == MODE_OFF or not _pump_off(inp, held):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "        if inp.entry_released or inp.mode == MODE_OFF or not _pump_off(inp, held) or fault_hold.held(coord.entry):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.BOOLOP.577b31a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.BOOLOP.577b31a4.json
deleted file mode 100644
index 8dd017cd61..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.BOOLOP.577b31a4.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe BOOLOP 577b31a4",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    if power is not None and now - start >= RUN_SETTLE:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if power is not None or now - start >= RUN_SETTLE:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.3cd6139b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.3cd6139b.json
new file mode 100644
index 0000000000..baee865a42
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.3cd6139b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe CMP_BOUND 3cd6139b",
+  "killed_by": "tests/features.py",
+  "old": "    duty_ledger.observe(held, inp, duty, now, ran=None if power is None else float(power) >= _ran_kw(inp),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`duty_ledger.observe(held, inp, duty, now, ran=None if power is None else float(power) > _ran_kw(inp),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.577b31a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.577b31a4.json
deleted file mode 100644
index 99e229cf71..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.577b31a4.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe CMP_BOUND 577b31a4",
-  "killed_by": "tests/features.py",
-  "old": "    if power is not None and now - start >= RUN_SETTLE:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if power is not None and now - start > RUN_SETTLE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.d24bfcb6.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.d24bfcb6.json
deleted file mode 100644
index 8d7fb873ff..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.d24bfcb6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe CMP_BOUND d24bfcb6",
-  "killed_by": "tests/features.py",
-  "old": "        row[\"ran\"] = row[\"ran\"] or float(power) >= _ran_kw(inp)",
-  "reason": "R9-EG-B6 (#1739) renamed the line's reads to the ArbiterInputs snapshot. Re-measured on a git-archive export at be777f2f: driving tests/features.py fails 3 of 3701 feature checks (`a draw exactly at the meter's threshold is a run; one hair below is not` among them), against the driver's baseline reds on the export (the #363 recorded_at check a git-archive copy cannot stamp, and the machine-sensitive R9-F2.1 P3 check, which fails identically at the merge base on this Mac) are named and excluded."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.BOOLOP.2a46488d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.BOOLOP.2a46488d.json
new file mode 100644
index 0000000000..9685978b94
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.BOOLOP.2a46488d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_release_row BOOLOP 2a46488d",
+  "killed_by": "tests/features.py",
+  "old": "    if coord is None or (reason == \"unload\" and fault_hold.unload_holds(coord.entry)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if coord is None or (reason == \"unload\" or fault_hold.unload_holds(coord.entry)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.577b31a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.2a46488d.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.577b31a4.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.2a46488d.json
index f4ea4c0ade..70875b1dd5 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.577b31a4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.2a46488d.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF 577b31a4",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_release_row GUARD_OFF 2a46488d",
   "killed_by": "tests/structure.py",
-  "old": "    if power is not None and now - start >= RUN_SETTLE:",
+  "old": "    if coord is None or (reason == \"unload\" and fault_hold.unload_holds(coord.entry)):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/survivor_triage/fault_hold.py/gate.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/survivor_triage/fault_hold.py/gate.RETURN_DEL.da9e8e97.json
new file mode 100644
index 0000000000..51e5d998f5
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/fault_hold.py/gate.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:gate RETURN_DEL da9e8e97",
+  "old": "    return None",
+  "reason": "Equivalent (RETURN_DEL) in `gate`: the mutated line is the function's last statement, `return None`; replaced by `pass` the function falls off its end and returns None all the same. The held-OFF arm above it is pinned by tests/features.py, \"the cycle's OFF under the hold is left, and the step tick writes it once the alarm clears\".",
+  "verdict": "equivalent"
+}


## Review scope: full (no verdict on verdict/<pr> names the reviewed head e4a8523d89c02aa9b4f7c477c6ecfabed09689ec, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/README.md b/README.md
index 90d9686625..17a0ff66e0 100644
--- a/README.md
+++ b/README.md
@@ -1085,6 +1085,7 @@ Each clears itself once the cause is gone.
 - **Valve target above comfort** — the mixing-valve target is read as the room temperature the circuit holds, not a water temperature, and it is above the top of your comfort band. Nothing is changed (it can be deliberate, for example slab charging); if it is a flow temperature, set the room temperature or 0 on **Mixing valve**.
 - **The heat pump's hot water set-point is below the configured temperature** — the pump's own set-point stops it reaching the disinfection or minimum temperature. The notice's fix writes the needed value to the pump's entity.
 - **The space-heating set-point entity is not reporting** — the set-point entity is missing or unreadable. Check it, or clear the slot.
+- **The heat pump reports a fault; the plan is suspended** — the pump's fault alarm has been on for 10 minutes, so the optimizer stops changing its mode and set-points and does not switch it off until the alarm clears; the notice then clears itself. Read the code on the pump's own display or app.
 - **The heat pump's mode reads cooling while the plan asks for heat** — the pump is in Cooling or Cooling + DHW, which a power cut, a reconnect or a fault reset can leave it in, and the plan or a boost asks for heat. The optimizer leaves a cooling pump alone, its power switch included, and never changes the mode back. Set a heating mode on the pump; the notice clears when the mode leaves cooling.
 - **The heat pump does not hold a setting the optimizer wrote** — the pump reads back something else after two writes. To change the pump by hand, turn **Optimizer Active** off first.
 - **Stored learning could not be read** — stored data from another version could not be read, so that part of what was learned starts again from defaults. The integration keeps running.
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 3416ad6933..0b3e85b11b 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -418,6 +418,8 @@ from .const import (
     DEFAULT_FREQ_CONTROL_MODE,
     CONF_PUMP_DUTY_MODE,
     DEFAULT_PUMP_DUTY_MODE,
+    CONF_FAULT_HOLD,
+    DEFAULT_FAULT_HOLD,
     PUMP_DUTY_MODES,
     CONF_SPACE_HYSTERESIS_ENTITY,
     CONF_DHW_HYSTERESIS_ENTITY,
@@ -1168,47 +1170,7 @@ def _select(options: list[str], translation_key: str) -> selector.SelectSelector
     )
 
 
-def _meter_source_selector() -> selector.SelectSelector:
-    """Meter, vendor estimate, or read from the entity's id (R10-HOTFIX-COP-UNMEASURED)."""
-    return selector.SelectSelector(
-        selector.SelectSelectorConfig(
-            options=[METER_SOURCE_AUTO, METER_SOURCE_METER, METER_SOURCE_ESTIMATE],
-            translation_key="meter_source",
-            mode=selector.SelectSelectorMode.DROPDOWN,
-        )
-    )
-
-
-def _freq_mode_selector() -> selector.SelectSelector:
-    """Observe or control (T7 #61).
-
-    An explicit two-option select rather than a boolean, because the
-    words matter: "control" is the moment actuation begins, and the user
-    should read that word, not flip an anonymous toggle.
-    """
-    return selector.SelectSelector(
-        selector.SelectSelectorConfig(
-            options=[FREQ_MODE_OBSERVE, FREQ_MODE_CONTROL],
-            translation_key="freq_control_mode",
-            mode=selector.SelectSelectorMode.DROPDOWN,
-        )
-    )
-
-
-def _solar_source_selector() -> selector.SelectSelector:
-    """Where irradiance comes from.
-
-    Kept as an explicit choice rather than "use Open-Meteo when no sensor
-    exists": silently calling an external API on a user's behalf is not a
-    decision an integration should make for them.
-    """
-    return selector.SelectSelector(
-        selector.SelectSelectorConfig(
-            options=list(SOLAR_SOURCES),
-            translation_key="solar_forecast_source",
-            mode=selector.SelectSelectorMode.DROPDOWN,
-        )
-    )
+_METER_SOURCES = [METER_SOURCE_AUTO, METER_SOURCE_METER, METER_SOURCE_ESTIMATE]
 
 
 def _solar_location_selector() -> selector.LocationSelector:
@@ -1743,12 +1705,14 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("entities", CONF_SPACE_SETPOINT_HIGH_LIMIT_C, _STORED, _WATER_LIMIT_C, when=_water_space_setpoint, group="indoor"),
     # -- entities_metering
     _F("entities_metering", CONF_SOLAR_RADIATION_ENTITY, _STORED, _entity_of('sensor'), group="solar"),
-    _F("entities_metering", CONF_SOLAR_FORECAST_SOURCE, DEFAULT_SOLAR_FORECAST_SOURCE, _solar_source_selector(), group="solar"),
+    # An explicit source, never "Open-Meteo when no sensor": an external call is the user's decision.
+    _F("entities_metering", CONF_SOLAR_FORECAST_SOURCE, DEFAULT_SOLAR_FORECAST_SOURCE, _select(list(SOLAR_SOURCES), "solar_forecast_source"), group="solar"),
     _F("entities_metering", CONF_SOLAR_LOCATION, _Computed(lambda cur, hass: _default_location(hass, cur)), _solar_location_selector(), group="solar"),
     _F("entities_metering", CONF_POWER_ENTITY, _STORED, _entity_of('sensor', 'power'), group="meters"),
-    _F("entities_metering", CONF_POWER_SOURCE, DEFAULT_METER_SOURCE, _meter_source_selector(), group="meters"),
+    # Meter, vendor estimate, or read from the entity's id (R10-HOTFIX-COP-UNMEASURED).
+    _F("entities_metering", CONF_POWER_SOURCE, DEFAULT_METER_SOURCE, _select(_METER_SOURCES, "meter_source"), group="meters"),
     _F("entities_metering", CONF_THERMAL_POWER_ENTITY, _STORED, _entity_of('sensor', 'power'), group="meters"),
-    _F("entities_metering", CONF_THERMAL_POWER_SOURCE, DEFAULT_METER_SOURCE, _meter_source_selector(), group="meters"),
+    _F("entities_metering", CONF_THERMAL_POWER_SOURCE, DEFAULT_METER_SOURCE, _select(_METER_SOURCES, "meter_source"), group="meters"),
     _F("entities_metering", CONF_ENERGY_ENTITY, _STORED, _entity_of('sensor', 'energy'), group="meters"),
     _F("entities_metering", CONF_HEAT_ENERGY_ENTITY, _STORED, _entity_of('sensor', 'energy'), group="meters"),
     _F("entities_metering", CONF_HEAT_METER_SEES_DHW, DEFAULT_HEAT_METER_SEES_DHW, selector.BooleanSelector(), group="meters"),
@@ -1756,7 +1720,8 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("entities_metering", CONF_COMPRESSOR_FREQ_ENTITY, _STORED, _entity_of('number'), group="compressor"),
     _F("entities_metering", CONF_COMPRESSOR_FREQ_SENSOR, _STORED, _entity_of('sensor', 'frequency'), group="compressor"),
     _F("entities_metering", CONF_FLOW_METER_ENTITY, _STORED, _entity_of('sensor'), group="compressor"),
-    _F("entities_metering", CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE, _freq_mode_selector(), group="compressor"),
+    # Two words, not a toggle: "control" is the moment actuation begins (T7 #61).
+    _F("entities_metering", CONF_FREQ_CONTROL_MODE, DEFAULT_FREQ_CONTROL_MODE, _select([FREQ_MODE_OBSERVE, FREQ_MODE_CONTROL], "freq_control_mode"), group="compressor"),
     _F("entities_metering", CONF_COMPRESSOR_FREQ_MIN_HZ, DEFAULT_COMPRESSOR_FREQ_MIN_HZ, _number(1, 250, 1, 'Hz'), group="compressor"),
     _F("entities_metering", CONF_COMPRESSOR_FREQ_MAX_HZ, DEFAULT_COMPRESSOR_FREQ_MAX_HZ, _number(1, 250, 1, 'Hz'), group="compressor"),
     # -- entities_pump
@@ -1770,6 +1735,7 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("entities_pump", CONF_HEAT_PUMP_DEFROST_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_DEFROST_ENTITY]))),
     _F("entities_pump", CONF_HEAT_PUMP_ONLINE_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_ONLINE_ENTITY]))),
     _F("entities_pump", CONF_HEAT_PUMP_FAULT_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_FAULT_ENTITY]))),
+    _F("entities_pump", CONF_FAULT_HOLD, DEFAULT_FAULT_HOLD, selector.BooleanSelector()),
     # The pump's own electric heat and its night mode. Options-only, with no
     # row in ``topology._SLOTS`` -- the precedent is the compressor-frequency
     # pair above, which is options-only for the same reason: they are not
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 181e139d87..ef12f44810 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -1076,6 +1076,10 @@ DEFAULT_DHW_DISINFECTION_MODE: Final = "observe"
 CONF_PUMP_DUTY_MODE: Final = "pump_duty_mode"
 DEFAULT_PUMP_DUTY_MODE: Final = "off"
 PUMP_DUTY_MODES: Final = ("off", "observe", "control")
+#: Suspend actuation while the fault alarm (``CONF_HEAT_PUMP_FAULT_ENTITY``)
+#: holds (fault_hold.py); on by default, off keeps the old behaviour.
+CONF_FAULT_HOLD: Final = "fault_hold"
+DEFAULT_FAULT_HOLD: Final = True
 #: The pump's own start hysteresis per duty, K, read from an entity as a
 #: temperature difference (``inputs.read_temperature_delta_k``) with no age
 #: gate: a setting changes only when someone changes it. Hot water: the pump
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 80785d4bc2..4dd4881995 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -259,7 +259,7 @@ from .accuracy import (
 )
 from .comfort_learning import ComfortLearner, OverrideEvent
 from .defrost import DefrostDerate, DefrostWindow, in_frost_band
-from . import duty_switch, early_cutoff, pump_arbiter, pump_signals, supply_hold
+from . import duty_switch, early_cutoff, fault_hold, pump_arbiter, pump_signals, supply_hold
 from . import issues, setpoint_check
 from . import quiet_windows
 from . import room_record, rooms, slab_seed
@@ -7664,7 +7664,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
         await heat_curve.publish(
             self.hass, self.entry, getattr(self, "_ctx", self)._config, displace_int, legacy_payload,
-            mode_off=self._mode == MODE_OFF,
+            mode_off=self._mode == MODE_OFF, released=self._entry_released,
         )
 
     async def async_publish_current_action(self, reason: str = "optimizer", heat_pump_on: bool | None = None) -> None:
@@ -7747,11 +7747,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         await _best_effort_cycle_step(
             lambda: pump_arbiter.apply(self), "Pump arbiter apply skipped: %s"
         )
-        await _best_effort_cycle_step(lambda: early_cutoff.arm(early_cutoff.state_for(self), self.arbiter_inputs, boost.held_for(self), _ctx_of(self)._opt_config, self.entry.async_on_unload), "Early cut-off arm skipped: %s")
-        # Off and a stale plan write nothing but the restore of what is still
-        # armed: the retry of one that failed, and the hand-back on staleness.
+        await _best_effort_cycle_step(lambda: early_cutoff.arm(early_cutoff.state_for(self), self.arbiter_inputs, boost.held_for(self), _ctx_of(self)._opt_config, self.entry.async_on_unload, entry=self.entry), "Early cut-off arm skipped: %s")
+        # Off and a stale plan write only the restore of what is still armed: a failed
+        # one's retry, and the hand-back on staleness, which a latched fault holds.
         stale = _plan_let_go(self)
-        await off_restore.async_cycle(self.hass, self.entry, _ctx_of(self)._config, self._mode == MODE_OFF, stale)
+        await off_restore.async_cycle(self.hass, self.entry, _ctx_of(self)._config, self._mode == MODE_OFF, stale and not fault_hold.held(self.entry))
         if not self._current_action or self._mode == MODE_OFF:
             return
         if stale:
@@ -7777,8 +7777,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
     async def _write_supply(self, on: bool) -> None:
         """The cycle's and the step tick's one supply gate: cut-off, mode, minimums."""
         held = pump_arbiter.state_for(self)
-        value = supply_hold.hold_supply(held, self.arbiter_inputs, boost.held_for(self), supply_hold.supply_write(
-            held, self.arbiter_inputs(), early_cutoff.allow_on(early_cutoff.state_for(self), on), self._pump_signals))
+        value = fault_hold.gate(self.entry, held, self.arbiter_inputs(), supply_hold.hold_supply(held, self.arbiter_inputs, boost.held_for(self), supply_hold.supply_write(
+            held, self.arbiter_inputs(), early_cutoff.allow_on(early_cutoff.state_for(self), on), self._pump_signals)))
         switch_entity = getattr(self, "_ctx", self)._config.heat_pump_switch_entity
         if switch_entity and value is not None:
             await pump_arbiter.write_supply(self, switch_entity, value)
@@ -10793,7 +10793,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         map with no evidence writes NOTHING: None is never a frequency.
         """
         entity_id = getattr(self, "_ctx", self)._config.compressor_freq_entity
-        if not entity_id or self._freq_mode() != FREQ_MODE_CONTROL or self._mode == MODE_OFF or _plan_let_go(self):
+        if not entity_id or self._freq_mode() != FREQ_MODE_CONTROL or self._mode == MODE_OFF or _plan_let_go(self) or fault_hold.held(self.entry):
             return
         _reported, hz_min, hz_max, _source = self._freq_entity_reading()
         target = self._freq_map.recommend(
diff --git a/custom_components/heatpump_optimizer/diagnostics.py b/custom_components/heatpump_optimizer/diagnostics.py
index c3a1b8681e..dd67e8ca1a 100644
--- a/custom_components/heatpump_optimizer/diagnostics.py
+++ b/custom_components/heatpump_optimizer/diagnostics.py
@@ -77,7 +77,7 @@ from homeassistant.core import HomeAssistant
 from homeassistant.util import dt as dt_util
 
 from . import heat_curve
-from . import accuracy, debugger, draw_range, early_cutoff, pump_arbiter, replay_doc, room_record
+from . import accuracy, debugger, draw_range, early_cutoff, fault_hold, pump_arbiter, replay_doc, room_record
 from .const import CONF_COP_SCALE, CONF_TIBBER_TOKEN, DOMAIN, LOCATION_KEYS, PRIVATE_ENTITY_ID
 from .drift import stored_age_seconds
 from .inputs import OUTRANKS_STALE, describe_problem, health_summary
@@ -375,6 +375,7 @@ def _never_breaks(view: Callable[[Any], Any], coord: Any) -> Any:
 _VIEWS: tuple[tuple[str, Callable[[Any], Any]], ...] = (
     ("pump_duty", pump_arbiter.diagnostics_view),
     ("early_cutoff", lambda c: early_cutoff.diagnostics_view(early_cutoff.state_for(c))),
+    ("fault_hold", lambda c: fault_hold.diagnostics_view(c.entry)),
     ("draw_range", lambda c: draw_range.diagnostics_view(
         c.accuracy.draw, c.thermal_params,
         probe_install(c.arbiter_inputs().config), dt_util.utcnow().timestamp())),
diff --git a/custom_components/heatpump_optimizer/duty_ledger.py b/custom_components/heatpump_optimizer/duty_ledger.py
index b165909b43..19dbc1fb6d 100644
--- a/custom_components/heatpump_optimizer/duty_ledger.py
+++ b/custom_components/heatpump_optimizer/duty_ledger.py
@@ -1,20 +1,69 @@
 """The pump arbiter's step verdicts: what the pump did over one step, against the plan.
 
-``pump_arbiter`` folds each pass into the step's ledger row (``_observe``);
-the row is closed here. A rise of :data:`TANK_RISE_C` over the step is hot
-water. Each step is ``delivered``, ``space-instead``, ``dhw-instead``,
-``idle-instead``, ``not-startable`` (a hot-water step left idle on a tank at
-or above the pump's own start temperature, the step's target less
-``dhw_hysteresis_entity``), ``unknown`` (no power meter and no tank rise) or
-``baseline``. A concurrent Heating + DHW run reads as hot water; a big draw
-can hide a tank rise. Pure: a row in, a verdict out.
+``pump_arbiter`` folds each pass into the step's ledger row (:func:`observe`);
+the row is closed here. Kept in observe and in control, from what the
+integration already reads -- the measured electrical draw (running or not),
+the mode select (DHW only) and the tank temperature (a rise of
+:data:`TANK_RISE_C` over the step is hot water). Each step gets one verdict:
+
+* ``delivered``, ``space-instead``, ``dhw-instead`` or ``idle-instead``;
+* ``not-startable``: a hot-water step left idle on a tank at or above the
+  pump's own start temperature, the step's target less ``dhw_hysteresis_entity``;
+* ``device-fault``: a pass inside the step found the pump's fault alarm
+  holding actuation (``fault_hold``);
+* ``unknown`` (no power meter and no tank rise) or ``baseline``.
+
+A concurrent Heating + DHW run reads as
+hot water; a big draw can hide a tank rise. A row is closed when its step
+ends, so the step in which a long fault began keeps its own verdict.
+
+A leaf over ``plan_step``: ``pump_arbiter`` computes what each pass read (the
+run threshold, the DHW mode, the start temperature) and passes it in, and owns
+the record (``ArbiterState``) the rows live on.
 """
 from __future__ import annotations
 
+from datetime import datetime, timedelta
 from typing import Any
 
-#: The tank rise over a step that reads as hot water, K.
+from .plan_step import plan_step_start
+
+#: A tank rise over one step that reads as hot water, K.
 TANK_RISE_C = 0.5
+#: How long into a step the meter still reads the last step (#2492 carry 8).
+#: The supply tick writes the switch in the step's first tick, and the
+#: arbiter's tick in that same minute reads the draw from before the write.
+RUN_SETTLE = timedelta(minutes=1)
+
+
+def observe(held: Any, inp: Any, duty: str | None, now: datetime, *, ran: bool | None,
+            dhw_mode: bool, start_below: Any, faulted: bool) -> None:
+    """Fold this pass into the current step's row; close the last one.
+
+    ``planned`` is re-frozen whenever a new plan is adopted inside the step.
+    The cycle's re-solve can move a slot onto the current step, and the
+    switch is written from that plan, so the step is scored against the
+    plan that actuated it, not the one in force at its first tick. ``ran`` is
+    ``None`` with no meter reading, or one inside :data:`RUN_SETTLE` of the
+    step's start, which folds into neither ``measured`` nor ``ran``.
+    """
+    held.last_duty = duty
+    start = plan_step_start(now)
+    tank = getattr(inp.state, "dhw_temperature", None)
+    row = held.step
+    if row is None or row["start"] != start:
+        if row is not None:
+            held.log.append(step_verdict(row, tank))
+        held.step = row = {"start": start, "planned": duty, "plan": inp.plan, "tank": tank,
+                           "measured": False, "ran": False, "dhw_mode": False, "faulted": False}
+        row["start_below"] = start_below
+    elif row["plan"] is not inp.plan:
+        row["planned"], row["plan"] = duty, inp.plan
+    if ran is not None and now - start >= RUN_SETTLE:
+        row["measured"] = True
+        row["ran"] = row["ran"] or ran
+    row["dhw_mode"] = row["dhw_mode"] or dhw_mode
+    row["faulted"] = row["faulted"] or faulted
 
 
 def _not_startable(row: dict[str, Any]) -> bool:
@@ -43,13 +92,15 @@ def step_verdict(row: dict[str, Any], tank: Any) -> dict[str, Any]:
     else:
         actual = "dhw" if rose else None
     planned = row["planned"]
-    if planned is None:
-        verdict = "baseline"
+    if row.get("faulted"):
+        result = "device-fault"
+    elif planned is None:
+        result = "baseline"
     elif actual is None:
-        verdict = "unknown"
+        result = "unknown"
     elif actual == planned or (planned == "both" and actual != "idle"):
-        verdict = "delivered"
+        result = "delivered"
     else:
-        verdict = _missed(row, planned, actual)
+        result = _missed(row, planned, actual)
     return {"start": row["start"].isoformat(), "planned": planned,
-            "actual": actual, "verdict": verdict}
+            "actual": actual, "verdict": result}
diff --git a/custom_components/heatpump_optimizer/early_cutoff.py b/custom_components/heatpump_optimizer/early_cutoff.py
index 715b436b51..3f7bcf85d7 100644
--- a/custom_components/heatpump_optimizer/early_cutoff.py
+++ b/custom_components/heatpump_optimizer/early_cutoff.py
@@ -76,6 +76,7 @@ from homeassistant.core import callback
 from homeassistant.helpers.event import async_track_state_change_event
 from homeassistant.util import dt as dt_util
 
+from . import fault_hold
 from .boost import CHANNEL_DHW, CHANNEL_SPACE, BoostState
 from .const import MODE_AUTO, MODE_ECONOMY, ROOM_AIR_RANGE_C
 from .entry_config import EntryConfig
@@ -134,6 +135,8 @@ class CutoffInputs:
     inputs: Callable[[], ArbiterInputs]
     boosts: BoostState
     opt_config: Any
+    #: The config entry, which keys the fault latch (:mod:`fault_hold`).
+    entry: Any
 
 
 #: Weak-keyed, so a value must not reach its key: ``wiring.inputs`` is the
@@ -154,6 +157,8 @@ async def arm(
     opt_config: Any,
     on_unload: Callable[[Callable[[], None]], Any],
     now: datetime | None = None,
+    *,
+    entry: Any,
 ) -> None:
     """Start a plan cycle: the cycle's own write resumes the pump.
 
@@ -166,7 +171,7 @@ async def arm(
         # Once per record, listener or not: the wiring below reaches the
         # coordinator and has to be dropped with the entry.
         on_unload(lambda: detach(held))
-    held.wiring = CutoffInputs(inputs, boosts, opt_config)
+    held.wiring = CutoffInputs(inputs, boosts, opt_config, entry)
     inp = inputs()
     cfg = EntryConfig.from_mapping(inp.config)
     # In UTC: local wall-clock arithmetic is an hour off across a DST change.
@@ -307,6 +312,9 @@ def on_room_event(held: CutoffState, wiring: CutoffInputs, event: Any) -> None:
         return
     if _exempt(inp, wiring.boosts, now) is not None:
         return
+    if fault_hold.consult(wiring.entry, inp, now):  # a faulted pump is not switched off
+        held.last_held = "fault"
+        return
     limit = threshold(inp, wiring.opt_config, now)
     if room <= limit:
         return
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index 620a43e0a1..2650b49e41 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -137,6 +137,7 @@ class EntryConfig(Mapping[str, Any]):
     grid_fee_entity: str | None = _entity_slot()
     heat_pump_capacity_limited_entity: str | None = _entity_slot()
     heat_pump_defrost_entity: str | None = _entity_slot()
+    heat_pump_fault_entity: str | None = _entity_slot()
     heat_pump_mode_entity: str | None = _entity_slot()
     heat_pump_power_entity: str | None = _entity_slot()
     heat_pump_supply_temp_entity: str | None = _entity_slot()
@@ -168,6 +169,7 @@ class EntryConfig(Mapping[str, Any]):
     dhw_quantile_targets_enabled: bool = _key(const.DEFAULT_DHW_QUANTILE_TARGETS_ENABLED, _flag)
     ecl110_mqtt_retain: bool = _key(const.DEFAULT_ECL110_RETAIN, _flag)
     external_heat_detection_enabled: bool = _key(const.DEFAULT_EXTERNAL_HEAT_ENABLED, _flag)
+    fault_hold: bool = _key(const.DEFAULT_FAULT_HOLD, _flag)
     fuse_guard_enabled: bool = _key(const.DEFAULT_FUSE_GUARD_ENABLED, _flag)
     immersion_feedback_enabled: bool = _key(const.DEFAULT_IMMERSION_FEEDBACK_ENABLED, _flag)
     internal_gains_learning_enabled: bool = _key(const.DEFAULT_INTERNAL_GAINS_LEARNING_ENABLED, _flag)
diff --git a/custom_components/heatpump_optimizer/fault_hold.py b/custom_components/heatpump_optimizer/fault_hold.py
new file mode 100644
index 0000000000..3c2f236f7f
--- /dev/null
+++ b/custom_components/heatpump_optimizer/fault_hold.py
@@ -0,0 +1,166 @@
+"""Suspend actuation while the pump reports a latched fault (R11-OWNER-FAULT-HOLD).
+
+A pump whose fault alarm stays on is not taking commands as the plan means
+them, and writing modes, set-points, an OFF, a frequency or a heat-curve
+offset into it only adds traffic a person then has to undo. A fault alarm that
+clears in well under a minute is the pump's own self-clearing kind, so the
+hold starts only once the alarm has been on for :data:`FAULT_HOLD_AFTER`.
+
+**Reading.** The fault slot (``CONF_HEAT_PUMP_FAULT_ENTITY``) is read with no
+age limit (``inputs.UNBOUNDED``): a fault a push-only source reported once and
+never again still reads on. Unavailable, unknown, not a flag and no slot are
+unusable: an unusable reading never starts a hold and never ends one. The
+60-minute horizon keeps governing the learner freeze in ``pump_signals``.
+
+**Latch**, in memory per config entry: ``since`` is the alarm state's
+``last_changed`` (bounded to now) at the first legible on, kept through a code
+change and through unusable readings; only a legible off resets it. Optimizer
+Off clears it, so the first consult after On re-seeds it from the entity's
+``last_changed`` and an old fault holds again at once; a reload does the same.
+
+**The one writer of the latch and of the ``pump_fault_hold`` repair**; every
+writer that suspends itself consults :func:`holding` or :func:`gate`. The
+repair is one domain-wide id, as ``pump_write_ignored`` is: it is cleared only
+when no entry holds. The solver keeps planning; only actuation stops.
+"""
+from __future__ import annotations
+
+import logging
+from dataclasses import dataclass
+from datetime import datetime, timedelta
+from typing import Any
+from weakref import WeakKeyDictionary, WeakSet
+
+from homeassistant.util import dt as dt_util
+
+from . import issues
+from .const import CONF_HEAT_PUMP_FAULT_ENTITY, MODE_OFF
+from .entry_config import EntryConfig
+from .inputs import UNBOUNDED, InputReader
+
+_LOGGER = logging.getLogger(__name__)
+
+#: How long the alarm reads on before actuation stops: past the owner's
+#: longest self-clearing fault (a few minutes), well short of a latched one.
+FAULT_HOLD_AFTER = timedelta(minutes=10)
+
+ISSUE = "pump_fault_hold"
+
+
+@dataclass
+class FaultLatch:
+    """One entry's latch: since when the alarm reads on, and whether it holds."""
+
+    since: datetime | None = None
+    holding: bool = False
+    entity: str | None = None
+    hass: Any = None
+
+
+_STATES: WeakKeyDictionary[Any, FaultLatch] = WeakKeyDictionary()
+#: Entries whose unload dropped a holding latch: the unload's restore runs
+#: again after :func:`release`, and its baseline row is still owed.
+_RELEASED_HOLDING: WeakSet[Any] = WeakSet()
+
+
+def _latch(entry: Any) -> FaultLatch:
+    return _STATES.setdefault(entry, FaultLatch())
+
+
+def holding(entry: Any, hass: Any, config: Any, *, off: bool, released: bool = False,
+            now: datetime | None = None) -> bool:
+    """Read the alarm, move the latch, raise or clear the repair on an edge.
+
+    ``off`` (the optimizer is Off) and the ``fault_hold`` option off clear the
+    latch and answer False; ``released`` (the entry is unloaded) answers False
+    and raises nothing.
+    """
+    latch = _latch(entry)
+    if released:
+        return False
+    _RELEASED_HOLDING.discard(entry)  # set up again: the latch reads afresh
+    cfg = EntryConfig.from_mapping(config)
+    if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:
+        latch.since = None
+        return _move(latch, hass, False)
+    now = dt_util.as_utc(now or dt_util.now())
+    reading = InputReader(hass, dict(config)).read_bool(CONF_HEAT_PUMP_FAULT_ENTITY, max_age_minutes=UNBOUNDED)
+    if reading.flag is False and reading.ok:
+        latch.since = None
+    elif reading.flag and reading.ok and latch.since is None:
+        changed = getattr(hass.states.get(reading.entity_id), "last_changed", None)
+        latch.since = min(dt_util.as_utc(changed), now) if changed is not None else now
+    latch.entity, latch.hass = reading.entity_id, hass
+    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)
+
+
+def _move(latch: FaultLatch, hass: Any, on: bool) -> bool:
+    """Set the hold; raise the repair on its rising edge, clear it on its falling one."""
+    if on and not latch.holding:
+        since = latch.since.isoformat() if latch.since is not None else ""
+        _LOGGER.warning("%s has reported a fault since %s: the optimizer stops actuating the pump "
+                        "until it clears", latch.entity, since)
+        issues.set_issue(hass, ISSUE, True, placeholders={"entity": str(latch.entity), "since": since})
+    elif latch.holding and not on:
+        latch.holding = False
+        _clear(hass)
+    latch.holding = on
+    return on
+
+
+def _clear(hass: Any) -> None:
+    """Clear the domain-wide repair once no entry holds."""
+    if not any(other.holding and other.hass is hass for other in list(_STATES.values())):
+        issues.clear_issue(hass, ISSUE)
+
+
+def consult(entry: Any, inp: Any, now: datetime | None = None) -> bool:
+    """:func:`holding` for one pass's ``ArbiterInputs``."""
+    return holding(entry, inp.hass, inp.config, off=inp.mode == MODE_OFF, released=inp.entry_released, now=now)
+
+
+def held(entry: Any) -> bool:
+    """The latch as last moved, with no read."""
+    latch = _STATES.get(entry)
+    return latch is not None and latch.holding
+
+
+def gate(entry: Any, held_state: Any, inp: Any, value: bool | None) -> bool | None:
+    """``value``, with an OFF turned into "leave" while the fault holds.
+
+    An ON passes. A left OFF marks ``held_state.supply_held`` (the arbiter's
+    record), so the step tick retries it each minute and it lands after the
+    clear; the cooling gate's message (``supply_hold.supply_write``) is
+    never printed for it, since that gate passed the OFF.
+    """
+    if value is not False or not consult(entry, inp):
+        return value
+    held_state.supply_held = True
+    _LOGGER.debug("Not switching the pump off: its fault alarm holds actuation")
+    return None
+
+
+def release(hass: Any, entry: Any) -> bool:
+    """Unload: whether the entry was holding; drop its latch and, if last, the repair.
+
+    A holding latch is remembered (:func:`unload_holds`) until the entry's
+    next consult, so the unload's second restore leaves the row owed too.
+    """
+    latch = _STATES.pop(entry, None)
+    was = latch is not None and latch.holding
+    if was:
+        _RELEASED_HOLDING.add(entry)
+        _clear(hass)
+    return was
+
+
+def unload_holds(entry: Any) -> bool:
+    """Whether an unload's restore leaves the baseline row owed: the latch holds, or held at release."""
+    return held(entry) or entry in _RELEASED_HOLDING
+
+
+def diagnostics_view(entry: Any) -> dict[str, Any]:
+    """The latch, for the diagnostics."""
+    latch = _STATES.get(entry) or FaultLatch()
+    return {"holding": latch.holding, "since": latch.since.isoformat() if latch.since else None,
+            "hold_after_minutes": FAULT_HOLD_AFTER.total_seconds() / 60.0}
diff --git a/custom_components/heatpump_optimizer/heat_curve.py b/custom_components/heatpump_optimizer/heat_curve.py
index 9cf36c7f03..d216c46d19 100644
--- a/custom_components/heatpump_optimizer/heat_curve.py
+++ b/custom_components/heatpump_optimizer/heat_curve.py
@@ -56,7 +56,7 @@ from weakref import WeakKeyDictionary
 
 from homeassistant.util import dt as dt_util
 
-from . import off_restore
+from . import fault_hold, off_restore
 from .const import DOMAIN, HEAT_CURVE_KIND_PERSISTENT
 from .payload import CurrentAction, Ecl110Payload
 from .inputs import NumberReading, number_reading, setpoint_step, write_setpoint
@@ -274,13 +274,18 @@ async def publish(
     legacy_payload: Ecl110Payload,
     *,
     mode_off: bool = False,
+    released: bool = False,
 ) -> None:
     """Fan one displace out: the MQTT arms first, then the entity arm.
 
     ``entry`` keys the arm's record and its latches, so the coordinator
     carries no attribute and is not handed in. Either arm is armed for the
-    off restore before it writes.
+    off restore before it writes. Nothing is sent while the pump's fault
+    alarm holds (:mod:`fault_hold`): this is every displace's one sink, so the
+    cycle, the peak guard's engage and its release are all suspended.
     """
+    if fault_hold.holding(entry, hass, config, off=mode_off, released=released):
+        return
     await off_restore.async_arm(hass, entry, config, MQTT_CONSUMER)  # no topic: no restorer, a no-op
     await publish_ecl110_topics(
         hass,
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 4c63b7d55e..ed0e218bb9 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -145,6 +145,10 @@ step by :mod:`duty_ledger`. The last
 is not persisted. It is what decides whether control is worth turning on:
 ``delivered`` over the other verdicts is how often the pump already does
 what the plan wanted.
+
+**A latched fault suspends control** (:mod:`fault_hold`): while the pump's
+fault alarm holds, a pass writes nothing, an unload leaves the baseline row
+owed, and the ledger scores the step ``device-fault``.
 """
 from __future__ import annotations
 
@@ -166,7 +170,7 @@ from homeassistant.helpers.event import (
 )
 from homeassistant.util import dt as dt_util
 
-from . import boost, draw_range, duty_ledger, duty_switch, flow_limit, issues, off_restore, pump_mode, quiet_windows
+from . import boost, draw_range, duty_ledger, duty_switch, fault_hold, flow_limit, issues, off_restore, pump_mode, quiet_windows
 from .const import (
     CONF_BUFFER_TANK_TEMP_ENTITY,
     CONF_FLOOR_RETURN_TEMP_ENTITY,
@@ -266,10 +270,6 @@ def log_steps() -> int:
 
 
 _TICK = timedelta(minutes=1)
-#: How long into a step the meter still reads the last step (#2492 carry 8):
-#: the supply tick writes the switch in the step's first tick, and the
-#: arbiter's tick in that same minute reads the draw from before the write.
-RUN_SETTLE = _TICK
 
 #: The power-feedback loop on a water set-point (R10-WATER-SETPOINT-FEEDBACK,
 #: outside report #3380): a controller that integrates on target minus inlet
@@ -1830,34 +1830,12 @@ async def _write_night_schedule(coord: Any, inp: ArbiterInputs, now: datetime) -
         await _write(coord, inp, slot, values[slot], now)
 
 
-def _observe(held: ArbiterState, inp: ArbiterInputs, duty: str | None, now: datetime) -> None:
-    """Fold this pass into the current step's ledger row; close the last one.
-
-    ``planned`` is re-frozen whenever a new plan is adopted inside the step:
-    the cycle's re-solve can move a slot onto the current step, and the
-    switch is written from that plan, so the step is scored against the
-    plan that actuated it, not the one in force at its first tick. A meter
-    reading inside ``RUN_SETTLE`` of the step's start is the last step's tail
-    and folds into neither ``measured`` nor ``ran``.
-    """
-    held.last_duty = duty
-    start = plan_step_start(now)
-    tank = getattr(inp.state, "dhw_temperature", None)
-    row = held.step
-    if row is None or row["start"] != start:
-        if row is not None:
-            held.log.append(duty_ledger.step_verdict(row, tank))
-        held.step = row = {"start": start, "planned": duty, "plan": inp.plan, "tank": tank,
-                           "measured": False, "ran": False, "dhw_mode": False}
-        row["start_below"] = _dhw_start_below_c(inp)
-    elif row["plan"] is not inp.plan:
-        row["planned"], row["plan"] = duty, inp.plan
+def _observe(held: ArbiterState, inp: ArbiterInputs, duty: str | None, now: datetime, faulted: bool = False) -> None:
+    """Fold this pass into the step ledger (:func:`duty_ledger.observe`) with what it read."""
     power = inp.measured_power_kw
-    if power is not None and now - start >= RUN_SETTLE:
-        row["measured"] = True
-        row["ran"] = row["ran"] or float(power) >= _ran_kw(inp)
     mode = pump_mode.resolve(getattr(_slot_state(inp, "mode"), "state", None))
-    row["dhw_mode"] = row["dhw_mode"] or mode == pump_mode.MODE_DHW
+    duty_ledger.observe(held, inp, duty, now, ran=None if power is None else float(power) >= _ran_kw(inp),
+                        dhw_mode=mode == pump_mode.MODE_DHW, start_below=_dhw_start_below_c(inp), faulted=faulted)
 
 
 def _dhw_start_below_c(inp: ArbiterInputs) -> float | None:
@@ -1874,7 +1852,9 @@ async def apply(coord: Any, now: datetime | None = None) -> None:
     """One arbitration pass; safe to call from the cycle and from the tick."""
     now = now or dt_util.now()
     held = state_for(coord)
-    mode = duty_mode(coord.arbiter_inputs().config)
+    inp = coord.arbiter_inputs()
+    faulted = fault_hold.consult(coord.entry, inp, now)  # every install, duty off too
+    mode = duty_mode(inp.config)
     if mode == DUTY_OFF:
         release_listeners(coord)
         return
@@ -1884,10 +1864,11 @@ async def apply(coord: Any, now: datetime | None = None) -> None:
         if inp.entry_released:
             return  # queued before the unload: arm and write nothing (D1-s3-02)
         _listen(coord)
-        await _arbitrate(coord, held, inp, mode, now)
+        await _arbitrate(coord, held, inp, mode, now, faulted)
 
 
-async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: str, now: datetime) -> None:
+async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: str, now: datetime,
+                     faulted: bool = False) -> None:
     if inp.mode == MODE_OFF or mode != DUTY_CONTROL:
         # Off writes nothing here: the baseline row and the space set-point's
         # baseline are written back by off_restore (tvofi, 2026-11-15; ROW,
@@ -1903,9 +1884,9 @@ async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: s
     if boost.release_blocked(coord, inp, now):
         await boost.persist(coord)
     duty = _step_duty(coord, held, inp, now)
-    _observe(held, inp, duty, now)
+    _observe(held, inp, duty, now, faulted)
     await duty_switch.note_pass(duty_switch.record_for(coord), now, _switch_context(boost.held_for(coord), held, inp, now))
-    if mode != DUTY_CONTROL or _pump_off(inp, held):
+    if mode != DUTY_CONTROL or _pump_off(inp, held) or _fault_stands(inp.hass, held, faulted):
         return
     await _adopt(inp, coord.entry, held, now)
     hold(coord, now)
@@ -1916,6 +1897,21 @@ async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: s
     await _write_night_schedule(coord, inp, now)
 
 
+def _fault_stands(hass: Any, held: ArbiterState, faulted: bool) -> bool:
+    """Whether a latched fault suspends this pass (:mod:`fault_hold`).
+
+    Nothing is compared or written: the space reading before the next write
+    is forgotten, as :func:`_pump_off` forgets it, and a pending retry dies
+    with its warning, so the pass after the clear writes the step's row and a
+    reset the fault left is never adopted as a person's edit.
+    """
+    if faulted:
+        held.space_before = None
+        held.retry.clear()
+        issues.clear_issue(hass, ISSUE_IGNORED)
+    return faulted
+
+
 def _step_duty(coord: Any, held: ArbiterState, inp: ArbiterInputs, now: datetime) -> str | None:
     """The step's duty after the block and the hot-water lease (which it advances)."""
     return _leased(inp, held, _without_block(coord, _planned_duty(coord, inp, now), now), now)
@@ -1941,7 +1937,7 @@ async def _lead_mode(coord: Any, on: bool) -> None:
     async with held.lock:
         await _load(coord)
         inp = coord.arbiter_inputs()
-        if inp.entry_released or inp.mode == MODE_OFF or not _pump_off(inp, held):
+        if inp.entry_released or inp.mode == MODE_OFF or not _pump_off(inp, held) or fault_hold.held(coord.entry):
             return
         duty = _step_duty(coord, held, inp, now)
         await _write(coord, inp, "mode", _mode_for(inp, _served(coord, inp, duty, now)), now)
@@ -2158,11 +2154,13 @@ async def release(coord: Any) -> None:
     """Unload: let go of the listeners and save the record; nothing is written.
 
     The unload's restore (:mod:`off_restore`) has written the baseline row
-    and the space set-point's baseline back already.
+    and the space set-point's baseline back already, unless a latched fault
+    (:mod:`fault_hold`) held it; the latch and its repair go here.
     """
     release_listeners(coord)
     held = state_for(coord)
     release_supply(held)
+    fault_hold.release(coord.hass, coord.entry)
     if held.loaded:
         await _persist(coord)
 
@@ -2181,14 +2179,15 @@ def baseline_row(coord: Any, inp: ArbiterInputs, now: datetime) -> PumpCommand:
 async def _release_row(_hass: Any, entry: Any, _config: Any, reason: str) -> bool:
     """The off restore of :data:`ROW`: write the baseline row; True once every slot took it.
 
-    While the power switch reads off the pump takes no write
-    (:func:`_pump_off`), so the row stays owed and the next cycle tries
-    again; an unload has no next cycle and writes regardless. Takes no
-    arbiter lock: a pass that forgets the record between two of these
-    writes drops only what is cleared here anyway.
+    While the power switch reads off the pump takes no write (:func:`_pump_off`),
+    so the row stays owed and the next cycle tries again; an unload has no next
+    cycle and writes regardless, but not into a latched fault (:mod:`fault_hold`),
+    on the restore run again after :func:`release` too: that row stays owed. Off
+    ends the hold, so its row is written. Takes no arbiter lock: a pass that
+    forgets the record between two of these writes drops only what is cleared here.
     """
     coord = getattr(entry, "runtime_data", None)
-    if coord is None:
+    if coord is None or (reason == "unload" and fault_hold.unload_holds(coord.entry)):
         return False
     inp, held, now = coord.arbiter_inputs(), state_for(coord), dt_util.now()
     if reason != "unload" and _pump_off(inp, held):
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index d8cca815cd..97990dd2bf 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -1285,6 +1285,7 @@
           "heat_pump_defrost_entity": "Defrosting",
           "heat_pump_online_entity": "Pump online",
           "heat_pump_fault_entity": "Fault alarm",
+          "fault_hold": "Fault hold",
           "heat_pump_backup_heater_entity": "Space backup heater",
           "heat_pump_dhw_booster_entity": "Hot water tank booster",
           "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
@@ -1300,6 +1301,7 @@
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
           "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
+          "fault_hold": "On by default. Once the fault alarm above has been on for 10 minutes, the optimizer stops changing the heat pump's mode, set-points, compressor frequency and heat-curve offset, never switches it off, and raises a repair until the alarm clears; the plan keeps being made. Short self-clearing faults change nothing. A fault entity that also reports non-blocking warnings holds too: turn this off to keep writing through them.",
           "heat_pump_backup_heater_entity": "Optional. On while the pump's own electric backup heater is running in the space heating circuit. Resistive kilowatts on the meter are not the compressor being inefficient, so while this is on the optimizer stops reading the meter as an efficiency measurement. The heat still counts: it is real heat into the house, and the house learners keep running. Useful mainly if your pump publishes no power meter, where there is otherwise no way to notice the element at all.",
           "heat_pump_dhw_booster_entity": "Optional. On while the electric heater in the hot water tank is running. Treated the same way as the backup heater above, and each time it switches on it is also recorded as a hot water rescue - if those keep recurring, and you have turned on the immersion feedback option, the plan starts heating the tank a little earlier instead of paying resistive prices for the difference.",
           "heat_pump_capacity_limited_entity": "Optional. On while the pump is running at a reduced compressor speed, which most units call night mode or silent mode. What the pump draws and delivers then is not what it would do unconstrained, so the optimizer stops learning efficiency and capacity from those intervals. It keeps using the measured power for cost and heat accounting, because a speed-capped compressor still draws exactly what the meter says.",
@@ -1923,6 +1925,10 @@
       "title": "The space-heating set-point entity is not reporting",
       "description": "The entity you chose as the space-heating set-point ({entity}) is missing or unreadable, so nothing can be said about the pump's current target. The space-heating set-point is never recommended; this notice only reports that the entity cannot be read. Check that it still exists and is available, or clear the slot. This notice clears as soon as the entity reports a temperature."
     },
+    "pump_fault_hold": {
+      "title": "The heat pump reports a fault; the plan is suspended",
+      "description": "{entity} has reported a fault since {since}. Until it clears, the optimizer stops changing the pump's mode and set-points and does not switch it off; this notice then clears itself. Read the fault code on the pump's own display or app. To switch the pump by hand, turn Optimizer active off first, or the optimizer switches it on again within a minute."
+    },
     "pump_mode_cooling": {
       "title": "The heat pump's mode reads cooling while the plan asks for heat",
       "description": "The heat pump's operating mode reads “{mode}”, and the plan or a boost asks the pump for heat. Cooling is left to you: while the mode reads cooling, the optimizer does not switch the pump on or off and does not change its mode or set-points, so the pump makes no heat for the house. If it should heat, set a heating mode on the pump or in its app; a power cut, a reconnect or a fault reset can leave the pump in cooling. This notice clears as soon as the mode no longer reads cooling."
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index 401753fe51..5699bc82f3 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -1285,6 +1285,7 @@
           "heat_pump_defrost_entity": "Abtauen",
           "heat_pump_online_entity": "Pumpe online",
           "heat_pump_fault_entity": "Störungsmeldung",
+          "fault_hold": "Störungspause",
           "heat_pump_backup_heater_entity": "Zuheizer für Raumheizung",
           "heat_pump_dhw_booster_entity": "Heizstab im Warmwasserspeicher",
           "heat_pump_capacity_limited_entity": "Leistung begrenzt (Nachtmodus)",
@@ -1300,6 +1301,7 @@
           "heat_pump_defrost_entity": "Optional. Ein, solange die Wärmepumpe den Kreislauf umkehrt, um Frost vom Außenwärmetauscher zu schmelzen. Der während einer Abtauung bezogene Strom geht in den Wärmetauscher statt ins Haus. Beachte, dass viele Wärmepumpen nur alle paar Minuten abgefragt werden, kurze Abtauvorgänge also komplett übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
           "heat_pump_online_entity": "Optional und bei einer cloudverbundenen Wärmepumpe dringend empfohlen. Ein, solange die Wärmepumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre letzten bekannten Werte weiter veröffentlichen, obwohl die Wärmepumpe selbst vom Netzwerk getrennt ist, sodass alle anderen Sensoren völlig aktuell aussehen; dies ist das einzige Signal, das etwas anderes sagt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar, und dies bringt wenig.",
           "heat_pump_fault_entity": "Optional. Ein, solange die Wärmepumpe eine Störung meldet. Verwendet wird nur, ob eine Störung vorliegt, nie der Code selbst.",
+          "fault_hold": "Standardmäßig ein. Sobald die Störungsmeldung oben 10 Minuten lang ein ist, ändert der Optimierer Betriebsart, Sollwerte, Verdichterfrequenz und Heizkurvenverschiebung der Wärmepumpe nicht mehr, schaltet sie nie aus und meldet eine Reparatur, bis die Störung vorbei ist; der Plan wird weiter erstellt. Kurze, selbst endende Störungen ändern nichts. Eine Störungsentität, die auch nicht blockierende Warnungen meldet, pausiert ebenfalls: Schalten Sie dies aus, um weiter zu schreiben.",
           "heat_pump_backup_heater_entity": "Optional. Ein, solange der eigene elektrische Zuheizer der Wärmepumpe im Raumheizkreis läuft. Resistive Kilowatt am Zähler bedeuten nicht, dass der Verdichter ineffizient ist; solange dies eingeschaltet ist, wertet der Optimierer den Zähler daher nicht als Effizienzmessung. Die Wärme zählt weiterhin: Sie ist echte Wärme im Haus, und die Hauslernmodelle laufen weiter. Vor allem nützlich, wenn deine Wärmepumpe keinen Leistungsmesser veröffentlicht, da es sonst keine Möglichkeit gibt, das Heizelement überhaupt zu bemerken.",
           "heat_pump_dhw_booster_entity": "Optional. Ein, solange der elektrische Heizstab im Warmwasserspeicher läuft. Wird wie der Zuheizer oben behandelt, und jedes Einschalten wird zusätzlich als Warmwasser-Notfall erfasst – wiederholt sich das und du hast die Option für die Heizstab-Rückmeldung eingeschaltet, beginnt der Plan, den Speicher etwas früher zu heizen, statt für die Differenz resistive Preise zu zahlen.",
           "heat_pump_capacity_limited_entity": "Optional. Ein, solange die Wärmepumpe mit reduzierter Verdichterdrehzahl läuft, was die meisten Geräte Nachtmodus oder Flüstermodus nennen. Was die Wärmepumpe dann aufnimmt und abgibt, entspricht nicht ihrem uneingeschränkten Verhalten, daher lernt der Optimierer aus diesen Intervallen weder Effizienz noch Leistung. Für Kosten und Wärmebilanz verwendet er weiterhin die gemessene Leistung, denn ein drehzahlbegrenzter Verdichter nimmt genau das auf, was der Zähler anzeigt.",
@@ -1923,6 +1925,10 @@
       "title": "Die Entität für den Sollwert der Raumheizung meldet nichts",
       "description": "Die Entität, die du als Sollwert der Raumheizung gewählt hast ({entity}), fehlt oder ist nicht lesbar, daher lässt sich nichts über das aktuelle Ziel der Pumpe sagen. Der Sollwert der Raumheizung wird nie empfohlen; dieser Hinweis meldet nur, dass die Entität nicht gelesen werden kann. Prüfe, ob sie noch existiert und verfügbar ist, oder leere das Feld. Dieser Hinweis verschwindet, sobald die Entität eine Temperatur meldet."
     },
+    "pump_fault_hold": {
+      "title": "Die Wärmepumpe meldet eine Störung; der Plan ist ausgesetzt",
+      "description": "{entity} meldet seit {since} eine Störung. Bis sie vorbei ist, ändert der Optimierer Betriebsart und Sollwerte der Pumpe nicht und schaltet sie nicht aus; diese Meldung verschwindet dann von selbst. Lesen Sie den Störungscode am Display oder in der App der Pumpe. Um die Pumpe von Hand zu schalten, schalten Sie zuerst Optimierer aktiv aus, sonst schaltet der Optimierer sie innerhalb einer Minute wieder ein."
+    },
     "pump_mode_cooling": {
       "title": "Der Modus der Wärmepumpe zeigt Kühlen, während der Plan Wärme anfordert",
       "description": "Der Betriebsmodus der Wärmepumpe zeigt „{mode}“, und der Plan oder ein Boost fordert Wärme von der Pumpe an. Kühlen bleibt dir überlassen: Solange der Modus Kühlen zeigt, schaltet der Optimierer die Pumpe weder ein noch aus und ändert weder ihren Modus noch ihre Sollwerte, sodass die Pumpe das Haus nicht heizt. Soll sie heizen, stelle an der Pumpe oder in ihrer App einen Heizmodus ein; ein Stromausfall, eine Neuverbindung oder ein Zurücksetzen nach einer Störung kann die Pumpe im Kühlmodus lassen. Dieser Hinweis verschwindet, sobald der Modus nicht mehr Kühlen zeigt."
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index d8cca815cd..97990dd2bf 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -1285,6 +1285,7 @@
           "heat_pump_defrost_entity": "Defrosting",
           "heat_pump_online_entity": "Pump online",
           "heat_pump_fault_entity": "Fault alarm",
+          "fault_hold": "Fault hold",
           "heat_pump_backup_heater_entity": "Space backup heater",
           "heat_pump_dhw_booster_entity": "Hot water tank booster",
           "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
@@ -1300,6 +1301,7 @@
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
           "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
+          "fault_hold": "On by default. Once the fault alarm above has been on for 10 minutes, the optimizer stops changing the heat pump's mode, set-points, compressor frequency and heat-curve offset, never switches it off, and raises a repair until the alarm clears; the plan keeps being made. Short self-clearing faults change nothing. A fault entity that also reports non-blocking warnings holds too: turn this off to keep writing through them.",
           "heat_pump_backup_heater_entity": "Optional. On while the pump's own electric backup heater is running in the space heating circuit. Resistive kilowatts on the meter are not the compressor being inefficient, so while this is on the optimizer stops reading the meter as an efficiency measurement. The heat still counts: it is real heat into the house, and the house learners keep running. Useful mainly if your pump publishes no power meter, where there is otherwise no way to notice the element at all.",
           "heat_pump_dhw_booster_entity": "Optional. On while the electric heater in the hot water tank is running. Treated the same way as the backup heater above, and each time it switches on it is also recorded as a hot water rescue - if those keep recurring, and you have turned on the immersion feedback option, the plan starts heating the tank a little earlier instead of paying resistive prices for the difference.",
           "heat_pump_capacity_limited_entity": "Optional. On while the pump is running at a reduced compressor speed, which most units call night mode or silent mode. What the pump draws and delivers then is not what it would do unconstrained, so the optimizer stops learning efficiency and capacity from those intervals. It keeps using the measured power for cost and heat accounting, because a speed-capped compressor still draws exactly what the meter says.",
@@ -1923,6 +1925,10 @@
       "title": "The space-heating set-point entity is not reporting",
       "description": "The entity you chose as the space-heating set-point ({entity}) is missing or unreadable, so nothing can be said about the pump's current target. The space-heating set-point is never recommended; this notice only reports that the entity cannot be read. Check that it still exists and is available, or clear the slot. This notice clears as soon as the entity reports a temperature."
     },
+    "pump_fault_hold": {
+      "title": "The heat pump reports a fault; the plan is suspended",
+      "description": "{entity} has reported a fault since {since}. Until it clears, the optimizer stops changing the pump's mode and set-points and does not switch it off; this notice then clears itself. Read the fault code on the pump's own display or app. To switch the pump by hand, turn Optimizer active off first, or the optimizer switches it on again within a minute."
+    },
     "pump_mode_cooling": {
       "title": "The heat pump's mode reads cooling while the plan asks for heat",
       "description": "The heat pump's operating mode reads “{mode}”, and the plan or a boost asks the pump for heat. Cooling is left to you: while the mode reads cooling, the optimizer does not switch the pump on or off and does not change its mode or set-points, so the pump makes no heat for the house. If it should heat, set a heating mode on the pump or in its app; a power cut, a reconnect or a fault reset can leave the pump in cooling. This notice clears as soon as the mode no longer reads cooling."
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 264ad2a317..47c71581da 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -1285,6 +1285,7 @@
           "heat_pump_defrost_entity": "Avfrostning",
           "heat_pump_online_entity": "Pumpen är uppkopplad",
           "heat_pump_fault_entity": "Felindikering",
+          "fault_hold": "Felpaus",
           "heat_pump_backup_heater_entity": "Elpatron för värme",
           "heat_pump_dhw_booster_entity": "Elpatron i varmvattenberedaren",
           "heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)",
@@ -1300,6 +1301,7 @@
           "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
           "heat_pump_online_entity": "Valfritt, men varmt rekommenderat för en molnansluten pump. På medan pumpen faktiskt går att nå. En molnintegration kan fortsätta publicera sina senast kända värden medan pumpen själv har tappat nätverket, vilket får alla andra givare att se alldeles färska ut. Det här är den enda signal som avslöjar det. Vid lokal anslutning (LAN) blir givarna otillgängliga av sig själva och fältet tillför då lite.",
           "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Bara om det finns ett fel används, aldrig själva felkoden.",
+          "fault_hold": "På som standard. När felindikeringen ovan har varit på i 10 minuter slutar optimeraren ändra värmepumpens läge, börvärden, kompressorfrekvens och värmekurvans förskjutning, stänger aldrig av den och visar en reparation tills larmet går över; planen fortsätter att göras. Korta fel som går över av sig själva ändrar ingenting. En felentitet som också rapporterar varningar som inte stoppar pumpen pausar också: stäng av detta för att fortsätta skriva genom dem.",
           "heat_pump_backup_heater_entity": "Valfritt. På medan pumpens egen elpatron går i värmekretsen. Resistiva kilowatt på mätaren betyder inte att kompressorn är ineffektiv, så medan detta är på slutar optimeringen läsa mätaren som ett mått på verkningsgrad. Värmen räknas fortfarande: det är verklig värme in i huset, och husets inlärning fortsätter. Framför allt användbart om din pump inte publicerar någon effektmätare alls, för då finns det annars inget sätt att märka patronen.",
           "heat_pump_dhw_booster_entity": "Valfritt. På medan elpatronen i varmvattenberedaren går. Hanteras på samma sätt som elpatronen för värme ovan, och varje gång den slår till noteras det dessutom som en varmvattenräddning - om de återkommer, och du har slagit på återkopplingen för elpatron, börjar planen värma beredaren något tidigare i stället för att betala resistiva priser för mellanskillnaden.",
           "heat_pump_capacity_limited_entity": "Valfritt. På medan pumpen går med sänkt kompressorvarvtal, vilket de flesta aggregat kallar nattläge eller tystläge. Vad pumpen drar och levererar då är inte vad den skulle göra obegränsad, så optimeringen slutar lära sig verkningsgrad och kapacitet av de intervallen. Den fortsätter använda den uppmätta effekten för kostnad och energiredovisning, eftersom en varvtalsbegränsad kompressor ändå drar exakt det mätaren säger.",
@@ -1923,6 +1925,10 @@
       "title": "Börvärdesenheten för rumsuppvärmning rapporterar inte",
       "description": "Enheten du valt som börvärde för rumsuppvärmning ({entity}) saknas eller går inte att läsa, så inget kan sägas om pumpens aktuella mål. Ett rumsuppvärmningsbörvärde rekommenderas aldrig; det här meddelandet säger bara att enheten inte går att läsa. Kontrollera att den fortfarande finns och är tillgänglig, eller töm fältet. Meddelandet försvinner så snart enheten rapporterar en temperatur."
     },
+    "pump_fault_hold": {
+      "title": "Värmepumpen rapporterar ett fel; planen är pausad",
+      "description": "{entity} har rapporterat ett fel sedan {since}. Tills det går över slutar optimeraren ändra pumpens läge och börvärden och stänger inte av den; meddelandet försvinner sedan av sig självt. Läs felkoden på pumpens egen display eller app. För att slå av eller på pumpen för hand, stäng först av Optimeraren aktiv, annars slår optimeraren på den igen inom en minut."
+    },
     "pump_mode_cooling": {
       "title": "Värmepumpens läge visar kyla medan planen begär värme",
       "description": "Värmepumpens driftläge visar ”{mode}”, och planen eller en boost begär värme av pumpen. Kyla lämnas åt dig: så länge läget visar kyla slår optimeraren varken på eller av pumpen och ändrar varken dess läge eller börvärden, så pumpen värmer inte huset. Om den ska värma, välj ett värmeläge på pumpen eller i dess app; ett strömavbrott, en återanslutning eller en felåterställning kan lämna pumpen i kylläge. Meddelandet försvinner så snart läget inte längre visar kyla."
diff --git a/dev/audit/harnesses/early_cutoff_closed_loop.py b/dev/audit/harnesses/early_cutoff_closed_loop.py
index 56512fd8dc..531f4333bf 100644
--- a/dev/audit/harnesses/early_cutoff_closed_loop.py
+++ b/dev/audit/harnesses/early_cutoff_closed_loop.py
@@ -59,7 +59,7 @@ from datetime import UTC, datetime, timedelta
 from types import SimpleNamespace
 
 import numpy as np
-from harness import FakeHass, FakeState
+from harness import FakeEntry, FakeHass, FakeState
 from homeassistant.util import dt as dt_util
 from profiles import house, prices, solve_inputs
 
@@ -160,7 +160,7 @@ def run(label: str, plant_kind: str, cutoff: bool) -> None:
         if cutoff:
             dt_util.freeze(t0)
             asyncio.run(early_cutoff.arm(held, lambda inp=inp: inp, BoostState(), cfg,
-                                         unloads.append, t0))
+                                         unloads.append, t0, entry=FakeEntry()))
         for m in range(30):
             level = plan[m // 15]
             if plant_kind in ("OWNMIN", "HOT", "LIGHT") and level > MIN_RUNNING_DRAW_KW:
diff --git a/dev/audit/harnesses/r11_owner_fault_hold_mutants.py b/dev/audit/harnesses/r11_owner_fault_hold_mutants.py
new file mode 100644
index 0000000000..dc2ea136ab
--- /dev/null
+++ b/dev/audit/harnesses/r11_owner_fault_hold_mutants.py
@@ -0,0 +1,122 @@
+#!/usr/bin/env python3
+"""R11-OWNER-FAULT-HOLD (#3856): the mutation proof, one production predicate at a time.
+
+Each mutant deletes or weakens one line of the fault hold (``fault_hold.py``,
+its consults in ``pump_arbiter.py``, ``duty_ledger.py``, ``heat_curve.py``,
+``early_cutoff.py`` and ``coordinator.py``) in a ``git archive`` copy of the
+tree at REF, then runs the fault-hold block of ``tests/features.py`` (through
+``tools/audit/seat/features_block.py``, its prelude emitted in the copy) and
+``tests/block_duty.py``. Printed per mutant: KILLED with the failing check
+names, or SURVIVED. The baseline line is the unmutated copy: 0 failing, or
+the run measures nothing. A mutant whose text no longer matches exactly once
+exits 2 rather than run a vacuous mutant.
+
+Command (repository root):
+    python3 dev/audit/harnesses/r11_owner_fault_hold_mutants.py [REF]   # REF: HEAD
+"""
+from __future__ import annotations
+
+import os
+import subprocess
+import sys
+import tempfile
+
+P = "custom_components/heatpump_optimizer/"
+START = 'R.section("R11-OWNER-FAULT-HOLD'
+END = 'R.section("duty-switch restart learning, part A'
+M = [
+ ("hold-after comparison", "fault_hold.py", "latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER", "latch.since is not None and now - latch.since > FAULT_HOLD_AFTER"),
+ ("hold-after dropped", "fault_hold.py", "latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER", "latch.since is not None"),
+ ("unbounded read", "fault_hold.py", "read_bool(CONF_HEAT_PUMP_FAULT_ENTITY, max_age_minutes=UNBOUNDED)", "read_bool(CONF_HEAT_PUMP_FAULT_ENTITY)"),
+ ("legible-off reset", "fault_hold.py", "    if reading.flag is False and reading.ok:\n        latch.since = None\n", "    if reading.flag is False and reading.ok:\n        pass\n"),
+ ("unusable resets", "fault_hold.py", "    if reading.flag is False and reading.ok:", "    if not (reading.flag and reading.ok):"),
+ ("unusable starts", "fault_hold.py", "    elif reading.flag and reading.ok and latch.since is None:", "    elif latch.since is None:"),
+ ("since bounded to now", "fault_hold.py", "min(dt_util.as_utc(changed), now)", "dt_util.as_utc(changed)"),
+ ("released guard", "fault_hold.py", "    if released:\n        return False\n", ""),
+ ("opt-out", "fault_hold.py", "if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:", "if off or not cfg.heat_pump_fault_entity:"),
+ ("off clears", "fault_hold.py", "if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:", "if not cfg.fault_hold or not cfg.heat_pump_fault_entity:"),
+ ("rising-edge repair", "fault_hold.py", "        issues.set_issue(hass, ISSUE, True,", "        (lambda *a, **k: None)(hass, ISSUE, True,"),
+ ("falling-edge clear", "fault_hold.py", "        latch.holding = False\n        _clear(hass)\n", "        latch.holding = False\n"),
+ ("same-hass filter", "fault_hold.py", "other.holding and other.hass is hass", "other.holding"),
+ ("gate False-only", "fault_hold.py", "    if value is not False or not consult(entry, inp):", "    if value is None or not consult(entry, inp):"),
+ ("gate held mark", "fault_hold.py", "    held_state.supply_held = True\n", ""),
+ ("release clears", "fault_hold.py", "        _RELEASED_HOLDING.add(entry)\n        _clear(hass)\n", "        _RELEASED_HOLDING.add(entry)\n"),
+ ("apply consult", "pump_arbiter.py", "faulted = fault_hold.consult(coord.entry, inp, now)", "faulted = False"),
+ ("_arbitrate return", "pump_arbiter.py", " or _fault_stands(inp.hass, held, faulted):", ":"),
+ ("retry drop", "pump_arbiter.py", "        held.retry.clear()\n", ""),
+ ("ignored-issue clear", "pump_arbiter.py", "        issues.clear_issue(hass, ISSUE_IGNORED)\n    return faulted", "    return faulted"),
+ ("space_before drop", "pump_arbiter.py", "    if faulted:\n        held.space_before = None\n", "    if faulted:\n"),
+ ("_lead_mode skip", "pump_arbiter.py", " or fault_hold.held(coord.entry):\n            return\n        duty = _step_duty", ":\n            return\n        duty = _step_duty"),
+ ("release row skip", "pump_arbiter.py", "if coord is None or (reason == \"unload\" and fault_hold.unload_holds(coord.entry)):", "if coord is None:"),
+ ("ledger faulted mark", "pump_arbiter.py", "start_below=_dhw_start_below_c(inp), faulted=faulted)", "start_below=_dhw_start_below_c(inp))"),
+ ("verdict fault-first", "duty_ledger.py", '    if row.get("faulted"):', '    if False:'),
+ ("observe keeps faulted", "duty_ledger.py", 'row["faulted"] = row["faulted"] or faulted', 'row["faulted"] = faulted'),
+ ("diagnostics row", "diagnostics.py", '    ("fault_hold", lambda c: fault_hold.diagnostics_view(c.entry)),\n', ''),
+ ("publish return", "heat_curve.py", "    if fault_hold.holding(entry, hass, config, off=mode_off, released=released):\n        return\n", ""),
+ ("cut-off consult", "early_cutoff.py", "    if fault_hold.consult(wiring.entry, inp, now):", "    if False:"),
+ ("frequency guard", "coordinator.py", " or _plan_let_go(self) or fault_hold.held(self.entry):", " or _plan_let_go(self):"),
+ ("switch gate wired", "coordinator.py", "value = fault_hold.gate(self.entry, held, self.arbiter_inputs(), supply_hold.hold_supply(", "value = (lambda *a: a[3])(self.entry, held, self.arbiter_inputs(), supply_hold.hold_supply("),
+ ("cut-off entry wired", "coordinator.py", "self.entry.async_on_unload, entry=self.entry)", "self.entry.async_on_unload)"),
+ ("Off row held too", "pump_arbiter.py", "if coord is None or (reason == \"unload\" and fault_hold.unload_holds(coord.entry)):", "if coord is None or fault_hold.unload_holds(coord.entry):"),
+ ("stale hand-back held", "coordinator.py", "stale and not fault_hold.held(self.entry))", "stale)"),
+ ("consult released", "fault_hold.py", "off=inp.mode == MODE_OFF, released=inp.entry_released", "off=inp.mode == MODE_OFF"),
+ ("consult Off", "fault_hold.py", "off=inp.mode == MODE_OFF, released=inp.entry_released", "off=False, released=inp.entry_released"),
+ ("publish mode_off", "heat_curve.py", "fault_hold.holding(entry, hass, config, off=mode_off, released=released)", "fault_hold.holding(entry, hass, config, off=False, released=released)"),
+ ("diagnostics since", "fault_hold.py", '"since": latch.since.isoformat() if latch.since else None', '"since": None'),
+ ("unload mark set", "fault_hold.py", "        _RELEASED_HOLDING.add(entry)\n", ""),
+ ("unload mark read", "fault_hold.py", "return held(entry) or entry in _RELEASED_HOLDING", "return held(entry)"),
+ ("unload mark cleared", "fault_hold.py", "    _RELEASED_HOLDING.discard(entry)  # set up again: the latch reads afresh\n", ""),
+]
+
+
+def run(copy: str, prelude: str) -> list[str]:
+    env = {**os.environ, "PYTHONPATH": "tests/hastub"}
+    out: list[str] = []
+    for cmd in ([sys.executable, "tools/audit/seat/features_block.py", "--prelude",
+                 f"exec(open({prelude!r}).read())", START, END],
+                [sys.executable, "tests/block_duty.py"]):
+        r = subprocess.run(cmd, cwd=copy, capture_output=True, text=True, env=env, timeout=1500)
+        txt = r.stdout + r.stderr
+        fails = [line.strip()[5:] for line in txt.splitlines() if line.strip().startswith("FAIL ")]
+        if not fails and r.returncode != 0:
+            fails = ["CRASH " + (txt.strip().splitlines() or ["no output"])[-1]]
+        out += fails
+    return out
+
+
+def main(argv: list[str]) -> int:
+    ref = argv[0] if argv else "HEAD"
+    with tempfile.TemporaryDirectory() as copy:
+        archive = subprocess.run(["git", "archive", ref, "custom_components", "tests", "tools"],
+                                 capture_output=True, check=True).stdout
+        subprocess.run(["tar", "-x", "-C", copy], input=archive, check=True)
+        prelude = os.path.join(copy, "fh_prelude.py")
+        subprocess.run([sys.executable, "tools/audit/seat/features_block.py", "--emit-prelude", prelude, START, END],
+                       cwd=copy, capture_output=True, check=True, env={**os.environ, "PYTHONPATH": "tests/hastub"})
+        base = run(copy, prelude)
+        print(f"BASELINE {len(base)} failing")
+        for b in base:
+            print(f"    - {b[:150]}")
+        survived = 0
+        for name, f, old, new in M:
+            path = os.path.join(copy, P + f)
+            src = open(path, encoding="utf-8").read()
+            if src.count(old) != 1:
+                print(f"STALE {name} ({f}): the mutant's text is not on this tree once")
+                return 2
+            open(path, "w", encoding="utf-8").write(src.replace(old, new))
+            try:
+                fails = run(copy, prelude)
+            finally:
+                open(path, "w", encoding="utf-8").write(src)
+            survived += not fails
+            print(f"{'KILLED' if fails else 'SURVIVED'} {name} ({f}): {len(fails)} failing")
+            for x in fails[:4]:
+                print(f"    - {x[:150]}")
+        print(f"RESULT mutants={len(M)}")
+        print(f"RESULT survived={survived}")
+    return 0 if survived == 0 and not base else 1
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/harnesses/r11_owner_fault_latch.py b/dev/audit/harnesses/r11_owner_fault_latch.py
new file mode 100644
index 0000000000..8365c29442
--- /dev/null
+++ b/dev/audit/harnesses/r11_owner_fault_latch.py
@@ -0,0 +1,122 @@
+#!/usr/bin/env python3
+"""R11-OWNER-FAULT-HOLD (#3856): a fault-alarm timeline replayed through the production latch.
+
+Drives ``fault_hold.holding`` minute by minute over a fault-alarm timeline and
+prints counts only: no entity id, state word or time of a bundle is printed. A
+bundle is a user's private data and is never committed.
+
+Arms (each prints RESULT lines):
+
+  synthetic  24 hours of one-minute control passes with one multi-hour latch
+             (03:00-07:30), four sub-minute faults and two few-minute faults
+             (3 and 6 minutes). A pass that is not held would actuate (mode,
+             set-points, an OFF), so it counts one actuating pass. Printed:
+             ``latched_actuating`` (actuating passes past FAULT_HOLD_AFTER of
+             the latch, expected 0), ``short_held`` (held passes inside the
+             short faults, expected 0) and ``repairs`` (rising edges).
+             ``--opt-out`` runs the same timeline with ``fault_hold`` off, the
+             null control: it reproduces today's counts, every pass actuating.
+  bundle     ``--timeline T``: a JSON list of ``[iso time, state]`` pairs, the
+             fault entity's history extracted from a diagnostics bundle or the
+             recorder. Printed: ``latches`` (holds that started), ``short_faults``
+             (on-spells shorter than FAULT_HOLD_AFTER) and ``short_held``.
+
+Command (repository root):
+    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_owner_fault_latch.py synthetic [--opt-out]
+    PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/r11_owner_fault_latch.py bundle --timeline T
+"""
+from __future__ import annotations
+
+import json
+import logging
+import sys
+from datetime import datetime, timedelta, timezone
+
+from harness import FakeEntry, FakeHass, FakeState
+
+from heatpump_optimizer import fault_hold
+
+ENTITY = "binary_sensor.pump_fault"
+T0 = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
+
+
+def _synthetic() -> list[tuple[datetime, str]]:
+    """The 24-hour timeline: (when, state) changes."""
+    out = [(T0, "off")]
+    spells = [(180, 450)]  # the latch, minutes from 00:00
+    spells += [(m, m + 0.5) for m in (60, 600, 900, 1200)]  # sub-minute
+    spells += [(720, 723), (1300, 1306)]  # few-minute
+    for on, off in sorted(spells):
+        out += [(T0 + timedelta(minutes=on), "on"), (T0 + timedelta(minutes=off), "off")]
+    return out
+
+
+def replay(changes: list[tuple[datetime, str]], *, hold: bool = True, step=timedelta(minutes=1)):
+    """Per pass: (when, alarm on, held), the latch driven at every ``step``."""
+    hass = FakeHass({})
+    entry = FakeEntry(entry_id="replay")
+    config = {"heat_pump_fault_entity": ENTITY, "fault_hold": hold}
+    changes = sorted(changes)
+    now, end, i, state, passes = changes[0][0], changes[-1][0] + timedelta(hours=1), 0, None, []
+    while now <= end:
+        while i < len(changes) and changes[i][0] <= now:
+            state = changes[i][1]
+            hass.states.set(ENTITY, FakeState(state, last_updated=changes[i][0]))
+            i += 1
+        passes.append((now, state == "on", fault_hold.holding(entry, hass, config, off=False, now=now)))
+        now += step
+    return passes, getattr(hass, "issues", [])
+
+
+def _spells(changes):
+    """(on, off) of each on-spell."""
+    out, start = [], None
+    for when, state in sorted(changes):
+        if state == "on" and start is None:
+            start = when
+        elif state != "on" and start is not None:
+            out.append((start, when))
+            start = None
+    return out
+
+
+def _counts(changes, passes):
+    after = fault_hold.FAULT_HOLD_AFTER
+    spells = _spells(changes)
+    short = [(a, b) for a, b in spells if b - a < after]
+    long_ = [(a, b) for a, b in spells if b - a >= after]
+    inside = lambda t, ss, lead=timedelta(0): any(a + lead <= t < b for a, b in ss)  # noqa: E731
+    return {
+        "latched_actuating": sum(1 for t, _on, held in passes if inside(t, long_, after) and not held),
+        "short_held": sum(1 for t, _on, held in passes if inside(t, short) and held),
+        "short_faults": len(short),
+        "latches": sum(1 for (_t, _o, h), (_t2, _o2, h2) in zip(passes, passes[1:]) if h2 and not h),
+    }
+
+
+def main(argv: list[str]) -> int:
+    logging.disable(logging.CRITICAL)  # the latch's warning names the entity
+    if argv[:1] == ["synthetic"]:
+        changes = _synthetic()
+        passes, issues = replay(changes, hold="--opt-out" not in argv)
+        counts = _counts(changes, passes)
+        print(f"RESULT latched_actuating={counts['latched_actuating']}")
+        print(f"RESULT short_held={counts['short_held']}")
+        print(f"RESULT short_faults={counts['short_faults']}")
+        print(f"RESULT repairs={counts['latches']}")
+        print(f"RESULT actuating_passes={sum(1 for _t, _o, h in passes if not h)}")
+        return 0
+    if argv[:1] == ["bundle"] and "--timeline" in argv:
+        raw = json.loads(open(argv[argv.index("--timeline") + 1], encoding="utf-8").read())
+        changes = [(datetime.fromisoformat(t).astimezone(timezone.utc), str(s)) for t, s in raw]
+        passes, _issues = replay(changes)
+        counts = _counts(changes, passes)
+        for key in ("latches", "short_faults", "short_held"):
+            print(f"RESULT {key}={counts[key]}")
+        return 0
+    print(__doc__)
+    return 2
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/rounds/round3/D5/option_doc_coverage.py b/dev/audit/rounds/round3/D5/option_doc_coverage.py
index 156e408ff3..d903166c06 100644
--- a/dev/audit/rounds/round3/D5/option_doc_coverage.py
+++ b/dev/audit/rounds/round3/D5/option_doc_coverage.py
@@ -105,9 +105,9 @@ EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
     is reached by a shell-out the closure recorder cannot see, so it does not
     go red on a pull request: it is re-measured in the commit that changes
     what the script prints, or main's forced-full run finds it):
-    RESULT option_fields_rendered=220 count   (219 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 218 until R11-OUTSIDE-ROOMS-P1's room list; 216 until the two start-hysteresis pickers; 211 until R10-COMBI-TANK's five combi fields; 208 until R10-GENERIC-HEAT-CURVE's three heat_curve fields)
+    RESULT option_fields_rendered=221 count   (220 until R11-OWNER-FAULT-HOLD's fault hold toggle; 219 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 218 until R11-OUTSIDE-ROOMS-P1's room list; 216 until the two start-hysteresis pickers; 211 until R10-COMBI-TANK's five combi fields; 208 until R10-GENERIC-HEAT-CURVE's three heat_curve fields)
     RESULT option_fields_undocumented=0 count
-    RESULT option_schema_keys_rendered=254 count   (253 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 252 until R11-OUTSIDE-ROOMS-P1's room list; 250 until the two start-hysteresis pickers; 244 until R10-COMBI-TANK; 241 until R10-GENERIC-HEAT-CURVE)
+    RESULT option_schema_keys_rendered=255 count   (254 until R11-OWNER-FAULT-HOLD's fault hold toggle; 253 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 252 until R11-OUTSIDE-ROOMS-P1's room list; 250 until the two start-hysteresis pickers; 244 until R10-COMBI-TANK; 241 until R10-GENERIC-HEAT-CURVE)
     RESULT wood_economics_fields_rendered=4 count
     RESULT wood_economics_doc_lines=8 count      (tolerance: exact;
     moved 6 -> 8 by #1645/F8.1: the Services section's `simulate_plan`
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index bc9dc7a0ff..b01d09c8c5 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=103 measured=103",
+  "result": "documented=104 measured=104",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=103, listed=103, missing=[], phantom=[]",
+  "result": "on disk=104, listed=104, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
@@ -301,7 +301,7 @@
   "source": "docs/architecture.md:The Home Assistant boundary",
   "claim": "the boundary sentence's count of modules importing `homeassistant` at module level",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=36 measured=36",
+  "result": "documented=37 measured=37",
   "verdict": "true",
   "truth": ""
  },
@@ -310,7 +310,7 @@
   "source": "docs/architecture.md:The Home Assistant boundary",
   "claim": "the named modules are the complete set of module-level importers",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[]",
+  "result": "named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_hold.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_hold.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[]",
   "verdict": "true",
   "truth": "unnamed module-level importers: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 26d7a00b5d..15f5706e88 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,10 +35,10 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 25 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=25 measured=25 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=103 measured=103 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=103, listed=103, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
-| C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=36 measured=36 | **true** |  |
-| C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=104 measured=104 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=104, listed=104, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=37 measured=37 | **true** |  |
+| C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_hold.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_hold.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
 | C37 | `docs/architecture.md:module map` | __init__.py -- the 15 services | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
 | C38 | `docs/architecture.md:module map` | services.yaml -- The 15 service definitions | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index c3b0a89384..99d1322915 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=103      (102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=104      (103 until R11-OWNER-FAULT-HOLD's fault_hold.py; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,13 +117,13 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=103           (102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=104           (103 until R11-OWNER-FAULT-HOLD's fault_hold.py; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
                                          architecture.md's module map)
     RESULT arch_map_missing=0            (was 11)
-    RESULT ha_module_level_importers=36  (35 until R11-SEAM-actuation-release's number_restore.py; 34 until its circulation.py; 33 until R11-OUTSIDE-ROOMS-P3's room_record.py; 32 until R10-START-COUNTER-EDGES's running_signal.py; 31 until the supply-hold PR's supply_hold.py; 30 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 28 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 27 until the live-fix wave's early_cutoff.py imports
+    RESULT ha_module_level_importers=37  (36 until R11-OWNER-FAULT-HOLD's fault_hold.py; 35 until R11-SEAM-actuation-release's number_restore.py; 34 until its circulation.py; 33 until R11-OUTSIDE-ROOMS-P3's room_record.py; 32 until R10-START-COUNTER-EDGES's running_signal.py; 31 until the supply-hold PR's supply_hold.py; 30 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 28 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 27 until the live-fix wave's early_cutoff.py imports
                                          homeassistant.core at module level;
                                          26 until R9-DBG-1's debugger.py imports
                                          homeassistant.core at module level;
diff --git a/dev/programme/delivery/3872.md b/dev/programme/delivery/3872.md
new file mode 100644
index 0000000000..1547ec1ba3
--- /dev/null
+++ b/dev/programme/delivery/3872.md
@@ -0,0 +1 @@
+- [#3872](https://github.com/tvofi/heatpump_optimizer/pull/3872) — **open**, Fault hold: suspend actuation while the pump reports a latched fault (R11-OWNER-FAULT-HOLD)
diff --git a/docs/architecture.md b/docs/architecture.md
index f145a75445..8ec0fafc01 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 103 modules, of which 36 import the
+knows nothing about Home Assistant: 104 modules, of which 37 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -201,6 +201,8 @@ custom_components/heatpump_optimizer/
 │                         #   plan step, and stands down on a manual change
 ├── duty_ledger.py        # The arbiter's step verdicts: what the pump did
 │                         #   over one step against the plan
+├── fault_hold.py         # Latches the pump's fault alarm after 10 minutes and
+│                         #   suspends every actuator write while it holds
 ├── supply_hold.py        # The supply switch's minimum run and pause, held
 │                         #   across a re-solve, a cycle or a restart
 ├── duty_switch.py        # Learns per direction whether a duty switch stops
@@ -295,11 +297,11 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-36 of the 103 modules import `homeassistant` at module level: `__init__`,
+37 of the 104 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency`, `debugger`, `defrost`,
-`dhw_learning`, `diagnostics`, `duty_switch`, `early_cutoff`, `entity`, `heat_curve`, `issues`, `legionella`, `notifier`, `number_restore`, `off_restore`, `pump_arbiter`, `repairs`, `room_record`, `running_signal`, `services`,
+`dhw_learning`, `diagnostics`, `duty_switch`, `early_cutoff`, `entity`, `fault_hold`, `heat_curve`, `issues`, `legionella`, `notifier`, `number_restore`, `off_restore`, `pump_arbiter`, `repairs`, `room_record`, `running_signal`, `services`,
 `store`, `supply_hold`. One module outside that set touches it at all: `inputs`
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
diff --git a/docs/configuration.md b/docs/configuration.md
index 75c1cc9296..64388bbd0d 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -665,7 +665,8 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Hot water start hysteresis | none | `sensor` / `number` / `input_number`, K | Optional. The pump's own hot water start hysteresis, a temperature difference; the plan places no charge on a tank at or above the hot water target less this. |
 | Defrosting | from setup | a binary sensor | On while the pump reverses to melt frost off the outdoor coil. |
 | Pump online | from setup | a binary sensor | On while the pump is actually reachable. |
-| Fault alarm | from setup | a binary sensor | On while the pump is reporting a fault. Only whether there is a fault is used. |
+| Fault alarm | from setup | a binary sensor | On while the pump is reporting a fault. Only whether there is a fault is used. With *Fault hold* on, a fault on for 10 minutes suspends actuation (see [A pump that reports a fault](#a-pump-that-reports-a-fault)). |
+| Fault hold (`fault_hold`) | On | on / off | Once the fault alarm has been on for 10 minutes, the optimizer stops changing the pump's mode, set-points, compressor frequency and heat-curve offset and never switches it off, until the alarm clears. A fault entity that also reports non-blocking warnings holds too: turn this off to keep writing through them. |
 | Space backup heater | none | a flag entity | On while the pump's own electric backup heater runs in the space heating circuit. Those kilowatts are not the compressor, so the optimizer stops reading the meter as an efficiency measurement while it is on — but the heat still counts, because it is real heat into the house. Worth filling in mainly on a pump that publishes no power meter, where there is otherwise no way to notice the element at all. |
 | Hot water tank booster | none | a flag entity | On while the electric heater in the hot water tank runs. Treated like the backup heater above, and each switch-on is also recorded as a hot water rescue: if those recur and you have turned on immersion feedback, the plan starts heating the tank a little earlier. |
 | Capacity limited (night mode) | none | a flag entity | On while the pump runs at a reduced compressor speed — night or silent mode on most units. Efficiency and capacity are not learned from those intervals, because what the machine shows then is the cap's. Cost and heat accounting still use the measured power: a speed-capped compressor draws exactly what the meter says. |
@@ -980,7 +981,7 @@ writes, at every 15-minute plan step:
 **Observe** writes nothing. In *Observe* and *Control* the optimizer keeps a
 ledger of the last 24 hours: per 15-minute step, the duty the plan wanted
 against what the pump did, and a verdict — *delivered*, *space-instead*,
-*dhw-instead*, *idle-instead*, *not-startable* (a hot-water step left idle on a tank at or above the pump's own start temperature), *unknown* or *baseline* (no plan duty). What the
+*dhw-instead*, *idle-instead*, *not-startable* (a hot-water step left idle on a tank at or above the pump's own start temperature), *device-fault* (a step in which the pump's fault alarm held actuation; the step in which a long fault began keeps its own verdict, because a row is closed when its step ends), *unknown* or *baseline* (no plan duty). What the
 pump did is read from what the integration already reads: the **power
 entity** (running or not), the operating mode (*DHW (Hot Water)*) and the
 **tank temperature** (a rise of 0.5 °C over the step counts as hot water).
@@ -992,6 +993,29 @@ whether *Control* is worth turning on: the share of *delivered* steps is how
 often the pump already does what the plan wanted. *Off* (the default) does
 neither.
 
+#### A pump that reports a fault
+
+With a **Fault alarm** entity configured and *Fault hold* on (the default),
+an alarm that has been on for 10 minutes suspends actuation until it reads
+off: no mode, set-point, silent-switch or night-schedule write, no compressor
+frequency, no heat-curve offset on either the MQTT topics or the entity, no
+early cut-off, and no switch-off (a switch-on still passes; a switch-off the
+plan wanted is written once the alarm clears). The plan keeps being made. A
+repair, *The heat pump reports a fault; the plan is suspended*, is raised for
+the duration and clears itself. Faults that clear within 10 minutes change
+nothing. The alarm is read at any age, so a fault a source reported once and
+never again still holds; *unavailable*, *unknown* and a word that is not a
+flag neither start a hold nor end one. A stale plan hands nothing back while
+the hold lasts (it does once the alarm clears), and an unload under the hold
+leaves the pump's mode and hot-water set-point as they are, owed to the next
+Off, unload or stale plan. Turning the optimizer Off
+ends the hold and hands everything back at once, and turning it On again holds
+at once on a fault that is still old. The
+diagnostics download shows the latch under `fault_hold`; the heat-curve
+displace the diagnostics report under the hold is the one computed, which was
+not sent. To switch the pump by hand while it is faulted, turn **Optimizer
+active** off first.
+
 ### Room thermometers
 
 | Setting | Default | Range | What it means |
diff --git a/tests/block_duty.py b/tests/block_duty.py
index e469761696..6e53bd75a1 100644
--- a/tests/block_duty.py
+++ b/tests/block_duty.py
@@ -23,6 +23,7 @@ from heatpump_optimizer import boost as boost_mod  # noqa: E402
 from heatpump_optimizer import duty_ledger  # noqa: E402
 from heatpump_optimizer import entity as entity_mod  # noqa: E402
 from heatpump_optimizer import pump_arbiter as arb  # noqa: E402
+from heatpump_optimizer import duty_ledger  # noqa: E402
 from heatpump_optimizer import setpoint_check  # noqa: E402
 from heatpump_optimizer import switch as switch_mod  # noqa: E402
 from heatpump_optimizer.const import (  # noqa: E402
@@ -1113,6 +1114,10 @@ def hysteresis_checks() -> None:
 
     check("an idle hot water step on a tank above the start temperature is not-startable",
           lambda: verdict() == "not-startable")
+    check("a step a pass held under a latched fault is device-fault, before every other verdict "
+          "(R11-OWNER-FAULT-HOLD)",
+          lambda: [verdict(planned=p, faulted=True) for p in ("dhw", "space", "both", None)]
+          == ["device-fault"] * 4 and verdict(faulted=False) == "not-startable")
     check("an idle hot water step on a tank exactly at the start temperature is not-startable",
           lambda: verdict(51.0) == "not-startable")
     check("an idle hot water step on a tank below the start temperature is idle-instead",
diff --git a/tests/closures.json b/tests/closures.json
index 244e2086d3..011ca92e98 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -216,6 +216,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -400,6 +401,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -525,6 +527,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -640,6 +643,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -769,6 +773,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -901,6 +906,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1045,6 +1051,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1161,6 +1168,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1298,6 +1306,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1447,6 +1456,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1843,6 +1853,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2394,6 +2405,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2603,6 +2615,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2770,6 +2783,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2926,6 +2940,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -3128,6 +3143,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -3310,6 +3326,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -3717,6 +3734,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -3905,6 +3923,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4021,6 +4040,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4189,6 +4209,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4297,6 +4318,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4440,6 +4462,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_hold.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4934,6 +4957,8 @@
    "dev/audit/harnesses/r11_money_currency_precedence.py",
    "dev/audit/harnesses/r11_outside_3849_unlatched_price.py",
    "dev/audit/harnesses/r11_owner_criteria.py",
+   "dev/audit/harnesses/r11_owner_fault_hold_mutants.py",
+   "dev/audit/harnesses/r11_owner_fault_latch.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
    "dev/audit/harnesses/r11_seam_config_silent_prefill.py",
@@ -6318,7 +6343,7 @@
   },
   "tests/guard_pins.py": {
    "rc": 0,
-   "seconds": 18.2
+   "seconds": 23.4
   },
   "tests/ha_contract.py": {
    "rc": 0,
@@ -6366,7 +6391,7 @@
   },
   "tests/typing_ruler.py": {
    "rc": 0,
-   "seconds": 0.6
+   "seconds": 44.2
   },
   "tests/validate.py": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 20740cc73c..5f6e08daec 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 122
+records every read, so this lane's recorded closure is the package: all 123
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (121 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 120 until R11-SEAM-cycle-solve's ``solve_gate.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (122 until R11-OWNER-FAULT-HOLD's ``fault_hold.py``, 121 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 120 until R11-SEAM-cycle-solve's ``solve_gate.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
@@ -57,10 +57,12 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 184 of the 561 script pairs (34 choose 2) sharing 0.80 or more
-of their production-module closure (182 before R11-OWNER-FLOWCAP's flow_limit.py
-joined main's closures, adding env_drift.py/manual_plan.py and
-golden.py/manual_plan.py; 169 of 528 before R11-SEAM-tests's
+recording finds 186 of the 561 script pairs (34 choose 2) sharing 0.80 or more
+of their production-module closure (184 on each side before the merge joining
+R11-OWNER-FLOWCAP's flow_limit.py and R11-OWNER-FAULT-HOLD's fault_hold.py, which put
+card_drift.mjs and wood_advisor.py each with features.py at the 0.80 floor; 182
+before flow_limit.py on main and fault_hold.py on its branch each lifted
+env_drift.py/manual_plan.py and golden.py/manual_plan.py to 0.80; 169 of 528 before R11-SEAM-tests's
 cycle_lane.py, whose closure opens the whole package, and 180 on its branch
 before the merge bringing R11-SEAM-actuation-release's three production
 modules; 167 before both; 164 on each side before the merge joining
@@ -68,7 +70,7 @@ R11-OUTSIDE-ROOMS-P1's rooms.py, read by every closure that imports the
 coordinator, the input reader, the config flow or the sensor platform, and
 R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which joined
 config_flow_steps.py/debug_collect.py at 0.80; 162 before #3616 re-recorded the
-closures that import the coordinator), all 184 among the 435 pairs whose two
+closures that import the coordinator), all 186 among the 435 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
@@ -117,7 +119,7 @@ count from 154 to 162; #3616's re-record moved it to 163, and
 R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which add runs.py, to 164).
 Eighteen of the pairs sit at exactly 1.00 -- arch_score_head.py/deployment_shape.py,
 arch_score_head.py/entities.py and deployment_shape.py/entities.py
-(98 shared production files each), doc_claims.py/harness_headers.py
+(100 shared production modules each, 98 before R11-OWNER-FAULT-HOLD), doc_claims.py/harness_headers.py
 (88), structure.py/typing_ruler.py, finite_boundary.py/structure.py and
 finite_boundary.py/typing_ruler.py (80 each), plan_view.py/solar_alignment.py,
 boost_drift_replay.py/plan_view.py and boost_drift_replay.py/solar_alignment.py
diff --git a/tests/dst_checks.py b/tests/dst_checks.py
index f15ac60f6b..892a80266e 100644
--- a/tests/dst_checks.py
+++ b/tests/dst_checks.py
@@ -2426,7 +2426,7 @@ def _ec_cut_at(arm_at, switch_since, reading_at):
     hass, inp = _ec_world(arm_at - timedelta(minutes=5), switch_since)
     cfg = SimpleNamespace(get_comfort_temp=lambda hour, when=None: 21.0)
     dt_util.freeze(arm_at)
-    asyncio.run(_ec.arm(held, lambda: inp, _EcBoost(), cfg, lambda _f: None, dt_util.now()))
+    asyncio.run(_ec.arm(held, lambda: inp, _EcBoost(), cfg, lambda _f: None, dt_util.now(), entry=FakeEntry()))
     dt_util.freeze(reading_at)
     _ec.on_room_event(held, held.wiring, SimpleNamespace(
         data={"new_state": FakeState("22.5", unit="°C")}))
diff --git a/tests/entities.py b/tests/entities.py
index 2697593345..2f2bd1dd11 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -3989,6 +3989,11 @@ def _p2_registry(sources):
                      "the pump's run length is the age of the switch's VALUE "
                      "(last_changed); state_stamp answers when the entity was "
                      "last heard from, which a re-reported 'on' resets",
+                 # R11-OWNER-FAULT-HOLD: when the alarm's VALUE turned on.
+                 "fault_hold.py::holding":
+                     "seeds the latch from the fault alarm's last_changed, the "
+                     "instant its VALUE turned on; state_stamp answers when the "
+                     "entity was last heard from, which a re-reported 'on' resets",
                  # R10-HEAT-METER: where a mode split falls, never an age.
                  "pump_signals.py::read":
                      "carries the live mode's last_changed as the instant its "
diff --git a/tests/features.py b/tests/features.py
index 734ba54a52..c08b111d3f 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -65046,11 +65046,13 @@ from heatpump_optimizer import off_restore as _pa_orr  # noqa: E402
 
 
 def _pa_unload(coord):
-    """The unload's two halves, as ``async_unload_entry`` runs them: the restore, which
-    writes the baseline row back (ADR-004), then the arbiter's release, which writes nothing."""
+    """The unload as ``async_unload_entry`` runs it: the restore, which writes the baseline
+    row back (ADR-004), the arbiter's release (``async_shutdown``), which writes nothing,
+    then the restore once more behind the released latch."""
     coord.entry.runtime_data = coord
     _pa_aio.run(_pa_orr.async_restore(coord.hass, coord.entry, coord._config, "unload"))
     _pa_aio.run(_pa.release(coord))
+    _pa_aio.run(_pa_orr.async_restore(coord.hass, coord.entry, coord._config, "unload"))
 
 
 def _pa_enter_off(coord):
@@ -82648,7 +82650,7 @@ class _EcCoord(_PaCoord):
 
     def arm(self, at=None):
         _pa_aio.run(_ec.arm(_ec.state_for(self), self.arbiter_inputs,
-                            _ec_boost_mod.held_for(self), self.opt, self.entry.async_on_unload, at))
+                            _ec_boost_mod.held_for(self), self.opt, self.entry.async_on_unload, at, entry=self.entry))
 
     def room(self, value):
         ev = _PaNS(data={"new_state": FakeState(str(value), unit="°C")})
@@ -89826,6 +89828,573 @@ import json  # noqa: E402
 from pathlib import Path as _DsPath  # noqa: E402
 from harness import FakeCoordinator as _DsFakeCoord, FakeEntry as _DsFakeEntry  # noqa: E402
 
+R.section("R11-OWNER-FAULT-HOLD: a latched fault suspends actuation (#3856)")
+# The pump's fault alarm held for hours while the arbiter kept switching its
+# mode and writing set-points into it. ``fault_hold`` latches the alarm after
+# FAULT_HOLD_AFTER (10 min) and every actuator consults it. Each check's null
+# control is the same fixture with the alarm on for less than the hold, or off,
+# or the option off: today's writes.
+from heatpump_optimizer import fault_hold as _fh  # noqa: E402
+from heatpump_optimizer import duty_ledger as _fh_dl  # noqa: E402
+from heatpump_optimizer import heat_curve as _fh_hc  # noqa: E402
+from heatpump_optimizer import issues as _fh_issues  # noqa: E402
+
+_FH_FAULT = "binary_sensor.pump_fault"
+
+
+def _fh_coord(since=-11, state="on", duties="dds-", duty="control", hold=True, entity=_FH_FAULT, switch=None):
+    """A control ``_PaCoord`` whose fault alarm reads ``state`` since minute ``since`` of 06:00."""
+    c = _PaCoord(_PA_TUYA, duties=duties, duty=duty)
+    extra = {"heat_pump_fault_entity": entity, "fault_hold": hold}
+    if switch is not None:
+        extra["heat_pump_switch_entity"] = "switch.hp"
+        c.hass.states.set("switch.hp", FakeState(switch, last_updated=_PA_T0 - timedelta(hours=1)))
+    c._config = EntryConfig.from_mapping({**dict(c._config), **extra})
+    if entity and state is not None:
+        c.hass.states.set(entity, FakeState(state, last_updated=_PA_T0 + timedelta(minutes=since)))
+    return c
+
+
+def _fh_fault(c, state, at):
+    c.hass.states.set(c._config["heat_pump_fault_entity"], FakeState(state, last_updated=_PA_T0 + timedelta(minutes=at)))
+
+
+def _fh_pump_writes(c):
+    return [w for w in c.writes() if w[0] in ("select", "number", "switch")]
+
+
+def _fh_issue(c, issue_id=_fh.ISSUE):
+    return [i for i in getattr(c.hass, "issues", []) if i[1] == issue_id]
+
+
+# 1. Control, the alarm on for 11 minutes: no mode, set-point or silent write.
+_fh_held = _fh_coord(since=-11)
+_pa_run(_fh_held, 0)
+_fh_short = _fh_coord(since=-9)
+_pa_run(_fh_short, 0)
+_fh_clear = _fh_coord(state="off")
+_pa_run(_fh_clear, 0)
+R.check("a fault alarm on for 11 minutes: the control pass writes nothing into the pump",
+        _fh_pump_writes(_fh_held) == [], f"{_fh_pump_writes(_fh_held)}")
+R.check("null control: the same pass with the alarm on for 9 minutes writes the step's row",
+        bool(_fh_pump_writes(_fh_short)) and _fh_pump_writes(_fh_short) == _fh_pump_writes(_fh_clear),
+        f"{_fh_pump_writes(_fh_short)} vs {_fh_pump_writes(_fh_clear)}")
+
+# 2. A step boundary Heating -> DHW under the hold writes no mode.
+def _fh_settle(c, minutes):
+    """One pass whose writes the device holds, as ``_pa_settled``; returns them."""
+    _pa_run(c, minutes)
+    got = c.writes()
+    for _domain, _svc, data in c.hass.services.calls:
+        c.device(data["entity_id"], str(data.get("option", data.get("value"))))
+    c.hass.services.calls.clear()
+    return got
+
+
+def _fh_boundary(**kw):
+    """The mode writes of the pass at the 06:15 boundary of a hot-water then heating plan."""
+    c = _fh_coord(duties="ds--", **kw)
+    for m in (0, 14):
+        _fh_settle(c, m)
+    return [w for w in _fh_settle(c, 15) if w[0] == "select"]
+
+
+_fh_step = _fh_boundary(since=-30)
+_fh_step_null = _fh_boundary(state="off")
+R.check("a step boundary under the hold writes no mode", _fh_step == [], f"{_fh_step}")
+R.check("null control: the same boundary with no fault writes the pump's mode",
+        bool(_fh_step_null), f"{_fh_step_null}")
+
+# 3. Drift under the hold: no re-send, the retry and its warning dropped; after
+# the clear the pump is written again and the reset never adopted.
+def _fh_drift_run(fault):
+    """Writes by phase when the pump resets its hot-water set-point a minute after the write."""
+    c = _fh_coord(state="off")
+    _fh_settle(c, 0)
+    held = _pa.state_for(c)
+    held.retry["mode"] = _PA_T0
+    _fh_issues.set_issue(c.hass, _pa.ISSUE_IGNORED, True, placeholders={"detail": "x"})
+    if fault:
+        _fh_fault(c, "on", -20)
+    c.device("number.dhw_set", "53")
+    during = (_fh_settle(c, 1), dict(held.retry), _fh_issue(c, _pa.ISSUE_IGNORED), held.space_before)
+    _fh_fault(c, "off", 2)
+    after = [w for m in range(3, 9) for w in _fh_settle(c, m)]
+    return during, after, c.set_modes
+
+
+_fh_drift = _fh_drift_run(True)
+_fh_drift_null = _fh_drift_run(False)
+R.check("drift under the hold is not re-sent, and the retry and the ignored-write warning are dropped",
+        _fh_drift[0] == ([], {}, [], None), f"{_fh_drift[0]}")
+R.check("after the clear the pump's reset set-point is written back, never adopted",
+        ("number", "set_value", 48) in _fh_drift[1] and _fh_drift[2] == [], f"{_fh_drift[1:]}")
+R.check("null control: with no fault the same reset is written back at once",
+        ("number", "set_value", 48) in _fh_drift_null[0][0], f"{_fh_drift_null[0]}")
+
+# 4. The switch gate: an OFF is left and marked held; an ON passes.
+_fh_g = _fh_coord(since=-30)
+_fh_gs = _pa.ArbiterState()
+_sa_dt.freeze(_PA_T0)
+_fh_gate = (_fh.gate(_fh_g.entry, _fh_gs, _fh_g.arbiter_inputs(), False), _fh_gs.supply_held,
+            _fh.gate(_fh_g.entry, _pa.ArbiterState(), _fh_g.arbiter_inputs(), True),
+            _fh.gate(_fh_g.entry, _pa.ArbiterState(), _fh_g.arbiter_inputs(), None))
+_fh_gn = _fh_coord(since=-9)
+_fh_gns = _pa.ArbiterState()
+_fh_gate_null = (_fh.gate(_fh_gn.entry, _fh_gns, _fh_gn.arbiter_inputs(), False), _fh_gns.supply_held)
+_sa_dt.freeze(None)
+R.check("the switch gate leaves an OFF under the hold and marks it held for the step tick; ON and None pass",
+        _fh_gate == (None, True, True, None), f"{_fh_gate}")
+R.check("null control: the same OFF with the alarm on for 9 minutes passes, unmarked",
+        _fh_gate_null == (False, False), f"{_fh_gate_null}")
+
+
+async def _fh_switch_run(fault):
+    """Switch calls by minute through the real coordinator: OFF at 06:00, the alarm clears at 06:03."""
+    ticks = []
+    armed = _sa_pa.async_track_time_interval
+    _sa_pa.async_track_time_interval = lambda _h, fn, _i: (ticks.append(fn), (lambda: None))[1]
+    hass = FakeHass({"switch.hp": FakeState("on", last_updated=_SA_T0 - timedelta(hours=1)),
+                     _FH_FAULT: FakeState("on" if fault else "off", last_updated=_SA_T0 - timedelta(minutes=30))})
+    coord = Coord(hass, FakeEntry(data={**_LC_DATA, "heat_pump_switch_entity": "switch.hp", "pump_duty_mode": "observe",
+                                        "heat_pump_fault_entity": _FH_FAULT}, entry_id=f"fh{next(_PA_IDS)}"))
+    coord._mode = "auto"
+    coord._optimization_result = SimpleNamespace(
+        timestamps=[_SA_T0 + timedelta(minutes=15 * i) for i in range(2)],
+        power_schedule=[0.0, 0.0], dhw_power_schedule=[0.0, 0.0], optimal_setpoints=[21.0, 21.0])
+    out = {}
+    try:
+        for m in range(6):
+            now = _SA_T0 + timedelta(minutes=m)
+            _sa_dt.freeze(now)
+            coord._last_optimization = now
+            if m == 3:
+                hass.states.set(_FH_FAULT, FakeState("off", last_updated=now))
+            if m == 0:
+                _sa_boost.adopt_plan(coord, {"heat_pump_on": False, "power": 0.0})
+                await coord._apply_action()
+            else:
+                for tick in list(ticks):
+                    await tick(now)
+            out[m] = [s for d, s, _d in hass.services.calls if d == "switch"]
+            hass.services.calls.clear()
+        out["cutoff_entry"] = _sa_ec.state_for(coord).wiring.entry is coord.entry
+    finally:
+        _sa_dt.freeze(None)
+        _sa_pa.async_track_time_interval = armed
+    return out
+
+
+_fh_sw = _asyncio.run(_fh_switch_run(True))
+_fh_sw_null = _asyncio.run(_fh_switch_run(False))
+R.check("the cycle's OFF under the hold is left, and the step tick writes it once the alarm clears",
+        _fh_sw[0] == [] and _fh_sw[1] == [] and _fh_sw[3] + _fh_sw[4] == ["turn_off"], f"{_fh_sw}")
+R.check("the cycle arms the early cut-off with its entry, the key of the fault latch",
+        _fh_sw["cutoff_entry"] is True, f"{_fh_sw}")
+R.check("null control: with no fault the cycle switches off at once",
+        _fh_sw_null[0] == ["turn_off"], f"{_fh_sw_null}")
+
+# 4b. A switch-on under the hold writes no mode ahead of it (``_lead_mode``).
+_fh_lead = _fh_coord(since=-30, switch="off")
+_fh_lead_null = _fh_coord(since=-30, switch="off", hold=False)
+_sa_dt.freeze(_PA_T0)
+for _fh_c in (_fh_lead, _fh_lead_null):
+    _pa_run(_fh_c, 0)
+    _fh_c.hass.services.calls.clear()
+    _asyncio.run(_pa._lead_mode(_fh_c, True))
+_sa_dt.freeze(None)
+R.check("a switch-on under the hold writes no mode ahead of it", _fh_lead.writes() == [], f"{_fh_lead.writes()}")
+R.check("null control: with the option off the same switch-on writes the step's mode first",
+        [w[0] for w in _fh_lead_null.writes()] == ["select"], f"{_fh_lead_null.writes()}")
+
+
+# 5. The early cut-off does not switch a faulted pump off.
+def _fh_cut(fault_since):
+    plan = SimpleNamespace(timestamps=[_PA_T0 + timedelta(minutes=15 * i) for i in range(8)],
+                           power_schedule=[1.5] * 8, dhw_power_schedule=[0.0] * 8,
+                           room_temp_trajectory=[21.0] * 9, duty_floor_kw=None)
+    hass = FakeHass({"switch.hp": FakeState("on", last_updated=_PA_T0 - timedelta(hours=1)),
+                     "sensor.room": FakeState("21.0"),
+                     _FH_FAULT: FakeState("on", last_updated=_PA_T0 + timedelta(minutes=fault_since))})
+    hass.async_create_task = lambda coro: _asyncio.run(coro)
+    held, entry = _sa_ec.CutoffState(), _pa_entry(entry_id=f"fh{next(_PA_IDS)}")
+    inp = _pa.ArbiterInputs(
+        hass=hass, config={"indoor_temp_entity": "sensor.room", "heat_pump_switch_entity": "switch.hp",
+                           "optimization_interval": 30, "heat_pump_fault_entity": _FH_FAULT},
+        mode=_PA_AUTO, plan=plan, plan_stale=False, entry_released=False,
+        state=SimpleNamespace(dhw_temperature=50.0, lower_floor_temperature=21.0),
+        thermal=None, params=SimpleNamespace(dhw_enabled=False, two_zone_enabled=False),
+        action={"heat_pump_on": True}, measured_power_kw=None, disinfecting=False, entry=entry)
+    cfg = SimpleNamespace(get_comfort_temp=lambda hour, when=None: 21.0)
+    _sa_dt.freeze(_PA_T0)
+    _asyncio.run(_sa_ec.arm(held, lambda: inp, _sa_boost.BoostState(), cfg, lambda _f: None, _PA_T0, entry=entry))
+    _sa_dt.freeze(_PA_T0 + timedelta(minutes=12))
+    _sa_ec.on_room_event(held, held.wiring, SimpleNamespace(data={"new_state": FakeState("22.5", unit="°C")}))
+    _sa_dt.freeze(None)
+    return [c[1] for c in hass.services.calls], held.last_held
+
+
+_fh_ec = _fh_cut(-30)
+_fh_ec_null = _fh_cut(5)
+R.check("a warm room under the hold does not cut the pump", _fh_ec == ([], "fault"), f"{_fh_ec}")
+R.check("null control: the alarm on for 7 minutes, the same reading cuts", _fh_ec_null[0] == ["turn_off"], f"{_fh_ec_null}")
+
+
+# 6. Every displace (cycle, peak-guard engage and release) goes through
+# ``heat_curve.publish``: nothing is sent under the hold.
+def _fh_publish(fault_since, released=False):
+    hass = FakeHass({_FH_FAULT: FakeState("on", last_updated=_PA_T0 + timedelta(minutes=fault_since))})
+    cfg = EntryConfig.from_mapping({"heat_pump_fault_entity": _FH_FAULT,
+                                    "ecl110_displace_set_topic": "ecl/displace/set"})
+    entry = _pa_entry(entry_id=f"fh{next(_PA_IDS)}")
+    _sa_dt.freeze(_PA_T0)
+    _asyncio.run(_fh_hc.publish(hass, entry, cfg, -3, {"displace": -3}, released=released))
+    _sa_dt.freeze(None)
+    return [c[0] for c in hass.services.calls], [i[1] for i in getattr(hass, "issues", [])]
+
+
+_fh_pub = _fh_publish(-30)
+_fh_pub_null = _fh_publish(-5)
+_fh_pub_rel = _fh_publish(-30, released=True)
+R.check("a displace under the hold is not published", _fh_pub == ([], [_fh.ISSUE]), f"{_fh_pub}")
+R.check("null control: the alarm on for 5 minutes, the displace is published",
+        "mqtt" in _fh_pub_null[0] and _fh_pub_null[1] == [], f"{_fh_pub_null}")
+R.check("an unloaded entry's displace raises no fault repair", _fh_pub_rel[1] == [], f"{_fh_pub_rel}")
+
+_fh_fq = _freq_coord(mode="control")
+_fh_fq_null = _freq_coord(mode="control")
+_fh.holding(_fh_fq.entry, FakeHass({_FH_FAULT: FakeState("on", last_updated=_PA_T0)}),
+            {"heat_pump_fault_entity": _FH_FAULT}, off=False, now=_PA_T0 + timedelta(minutes=11))
+_fh_fq_read = []
+for _fh_c in (_fh_fq, _fh_fq_null):
+    _fh_c._freq_entity_reading = lambda c=_fh_c: (_fh_fq_read.append(c), (None, 0.0, 0.0, "number"))[1]
+    _asyncio.run(_fh_c._command_frequency())
+R.check("the compressor frequency is not commanded under the hold: the guard returns before the target is read",
+        _fh_fq not in _fh_fq_read, f"{len(_fh_fq_read)}")
+R.check("null control: the same control-stage coordinator with no latch goes on to read its target",
+        _fh_fq_null in _fh_fq_read, f"{len(_fh_fq_read)}")
+
+
+# 7. The latch: Off -> On and a reload hold at once on an old fault; an
+# unusable reading never starts a hold and never ends one.
+def _fh_latch(states, steps, entity=_FH_FAULT, hold=True):
+    """``holding`` at each (minute, off, state-or-None) step; the state, given, is set first."""
+    hass = FakeHass(states)
+    entry = _pa_entry(entry_id=f"fh{next(_PA_IDS)}")
+    cfg = {"heat_pump_fault_entity": entity, "fault_hold": hold}
+    out = []
+    for minute, off, state in steps:
+        if state is not None:
+            hass.states.set(entity, state)
+        out.append(_fh.holding(entry, hass, cfg, off=off, now=_PA_T0 + timedelta(minutes=minute)))
+    return out, [i[1] for i in getattr(hass, "issues", [])], entry
+
+
+_fh_on70 = FakeState("on", last_updated=_PA_T0 - timedelta(minutes=70))
+_fh_r2 = _fh_latch({_FH_FAULT: _fh_on70}, [(0, False, None), (1, True, None), (2, False, None)])
+_fh_reload = _fh_latch({_FH_FAULT: _fh_on70}, [(0, False, None)])
+R.check("a fault on for 70 minutes on an on-change source holds at the first consult, after Off -> On and after a reload",
+        _fh_r2[0] == [True, False, True] and _fh_reload[0] == [True], f"{_fh_r2[0]} {_fh_reload[0]}")
+R.check("null control: the same source reading off holds at no consult",
+        _fh_latch({_FH_FAULT: FakeState("off", last_updated=_PA_T0 - timedelta(minutes=70))},
+                  [(0, False, None), (2, False, None)])[0] == [False, False])
+_fh_unus = {
+    word: _fh_latch({}, [(0, False, FakeState("on", last_updated=_PA_T0)), (5, False, FakeState(word, last_updated=_PA_T0 + timedelta(minutes=5))),
+                         (12, False, None), (13, False, FakeState("on", last_updated=_PA_T0 + timedelta(minutes=13)))])[0]
+    for word in ("unavailable", "unknown")
+}
+R.check("unavailable and unknown keep the latch's start: the hold comes at minute 10 of the first on, not the second",
+        all(v == [False, False, True, True] for v in _fh_unus.values()), f"{_fh_unus}")
+_fh_unus_end = {
+    word: _fh_latch({_FH_FAULT: _fh_on70}, [(0, False, None), (1, False, FakeState(word, last_updated=_PA_T0 + timedelta(minutes=1)))])[0]
+    for word in ("unavailable", "unknown")
+}
+R.check("an unusable reading never ends an active hold", all(v == [True, True] for v in _fh_unus_end.values()), f"{_fh_unus_end}")
+_fh_status = _fh_latch({"sensor.pump_status": FakeState("heating", last_updated=_PA_T0 - timedelta(hours=2))},
+                       [(0, False, None)], entity="sensor.pump_status")[0]
+_fh_unav = _fh_latch({_FH_FAULT: FakeState("unavailable", last_updated=_PA_T0 - timedelta(hours=2))}, [(0, False, None)])[0]
+R.check("a status word that is not a flag, and an unavailable alarm, never start a hold",
+        _fh_status == [False] and _fh_unav == [False], f"{_fh_status} {_fh_unav}")
+_fh_edge = [_fh_latch({_FH_FAULT: FakeState("on", last_updated=_PA_T0 - _fh.FAULT_HOLD_AFTER + timedelta(seconds=d))},
+                      [(0, False, None)])[0][0] for d in (0, 1)]
+R.check("the hold starts exactly at FAULT_HOLD_AFTER and not a second before it", _fh_edge == [True, False], f"{_fh_edge}")
+_fh_skew = _fh_latch({}, [(0, False, FakeState("on", last_updated=_PA_T0 + timedelta(minutes=5))), (10, False, None)])[0]
+R.check("a fault stamp ahead of the consult is bounded to it: the hold starts 10 minutes after the first legible on",
+        _fh_skew == [False, True], f"{_fh_skew}")
+R.check("a legible off ends the hold",
+        _fh_latch({_FH_FAULT: _fh_on70}, [(0, False, None), (1, False, FakeState("off", last_updated=_PA_T0 + timedelta(minutes=1)))])[0] == [True, False])
+
+# 8. The repair: raised on the rising edge, cleared on the falling edge, at Off and at unload.
+_fh_rep = {}
+for _fh_name, _fh_steps in (("rise", [(0, False, None)]),
+                            ("fall", [(0, False, None), (1, False, FakeState("off", last_updated=_PA_T0 + timedelta(minutes=1)))]),
+                            ("off", [(0, False, None), (1, True, None)])):
+    _fh_rep[_fh_name] = _fh_latch({_FH_FAULT: _fh_on70}, _fh_steps)[1]
+_fh_unl_hass = FakeHass({_FH_FAULT: _fh_on70})
+_fh_unl_entry = _pa_entry(entry_id=f"fh{next(_PA_IDS)}")
+_fh.holding(_fh_unl_entry, _fh_unl_hass, {"heat_pump_fault_entity": _FH_FAULT}, off=False, now=_PA_T0)
+_fh_rep["unload"] = (_fh.release(_fh_unl_hass, _fh_unl_entry), [i[1] for i in getattr(_fh_unl_hass, "issues", [])])
+_fh_rep["released"] = _fh_latch({_FH_FAULT: _fh_on70}, [])[1]
+_fh_relh = FakeHass({_FH_FAULT: _fh_on70})
+_fh_rep["released"] = (_fh.holding(_pa_entry(entry_id="fhrel"), _fh_relh, {"heat_pump_fault_entity": _FH_FAULT},
+                                   off=False, released=True, now=_PA_T0), getattr(_fh_relh, "issues", []))
+_fh_rep["nine"] = _fh_latch({_FH_FAULT: FakeState("on", last_updated=_PA_T0 - timedelta(minutes=9))}, [(0, False, None)])[1]
+R.check("the fault repair is raised on the hold's rising edge", _fh_rep["rise"] == [_fh.ISSUE], f"{_fh_rep}")
+R.check("and cleared on its falling edge, at Off and at unload",
+        _fh_rep["fall"] == [] and _fh_rep["off"] == [] and _fh_rep["unload"] == (True, []), f"{_fh_rep}")
+R.check("an unloaded entry and a 9-minute fault raise none",
+        _fh_rep["released"] == (False, []) and _fh_rep["nine"] == [], f"{_fh_rep}")
+_fh_two = FakeHass({_FH_FAULT: _fh_on70})
+_fh_e1, _fh_e2 = _pa_entry(entry_id="fh2a"), _pa_entry(entry_id="fh2b")
+for _fh_e in (_fh_e1, _fh_e2):
+    _fh.holding(_fh_e, _fh_two, {"heat_pump_fault_entity": _FH_FAULT}, off=False, now=_PA_T0)
+_fh.holding(_fh_e1, _fh_two, {"heat_pump_fault_entity": _FH_FAULT}, off=True, now=_PA_T0)
+_fh_two_kept = [i[1] for i in getattr(_fh_two, "issues", [])]
+_fh.holding(_fh_e2, _fh_two, {"heat_pump_fault_entity": _FH_FAULT}, off=True, now=_PA_T0)
+R.check("the one domain-wide repair stays while another entry still holds, and goes with the last",
+        _fh_two_kept == [_fh.ISSUE] and getattr(_fh_two, "issues", []) == [], f"{_fh_two_kept}")
+
+# 9. The ledger: a step in which any pass held is device-fault; a short fault
+# keeps today's verdict; the onset step keeps its own.
+def _fh_ledger(since, duty="observe", duties="dsds", state="on", onset=None, clear=None):
+    """Verdicts over an hour of passes; ``onset``/``clear``: the alarm turns on/off at that minute."""
+    c = _fh_coord(since=since, duties=duties, duty=duty, state="off" if onset is not None else state)
+    for m in range(0, 61):
+        if m == onset:
+            _fh_fault(c, "on", m)
+        if m == clear:
+            _fh_fault(c, "off", m)
+        _pa_run(c, m)
+    return [r["verdict"] for r in _pa.state_for(c).log]
+
+
+_fh_lg = _fh_ledger(-30)
+_fh_lg_short = _fh_ledger(-30, state="off")
+_fh_lg_onset = _fh_ledger(-30, onset=10)
+R.check("every held step of the ledger is device-fault (hot water, space)",
+        _fh_lg == ["device-fault"] * 4, f"{_fh_lg}")
+R.check("null control: the same steps with no fault keep today's verdicts",
+        "device-fault" not in _fh_lg_short and len(_fh_lg_short) == 4, f"{_fh_lg_short}")
+R.check("the step in which a fault began keeps its own verdict; the next is device-fault",
+        _fh_lg_onset[0] == _fh_lg_short[0] and _fh_lg_onset[1:] == ["device-fault"] * 3, f"{_fh_lg_onset}")
+_fh_lg_clear = _fh_ledger(-30, clear=20)
+R.check("a step whose fault clears inside it stays device-fault: any held pass marks the step",
+        _fh_lg_clear[:2] == ["device-fault"] * 2 and _fh_lg_clear[2:] == _fh_lg_short[2:], f"{_fh_lg_clear}")
+_fh_row = {"start": _PA_T0, "planned": "both", "tank": 50.0, "measured": True, "ran": True, "dhw_mode": True}
+R.check("device-fault is decided before every other verdict, a both step included",
+        _fh_dl.step_verdict({**_fh_row, "faulted": True}, 50.0)["verdict"] == "device-fault"
+        and _fh_dl.step_verdict(_fh_row, 50.0)["verdict"] == "delivered")
+
+# 9b. The diagnostics download carries the latch (``diagnostics._VIEWS``).
+from heatpump_optimizer import diagnostics as _fh_diag  # noqa: E402
+_fh_dv = dict(_fh_diag._VIEWS).get("fault_hold")
+_fh_dvc = _fh_coord(since=-30)
+_pa_run(_fh_dvc, 0)
+_fh_dv_null = _fh_coord(state="off")
+_pa_run(_fh_dv_null, 0)
+R.check("the diagnostics download shows the fault latch under fault_hold",
+        _fh_dv is not None and _fh_dv(_fh_dvc)["holding"] is True and _fh_dv(_fh_dv_null)["holding"] is False,
+        f"{_fh_dv and (_fh_dv(_fh_dvc), _fh_dv(_fh_dv_null))}")
+
+# 10. Duty off: the cycle's consult still moves the latch, so the switch,
+# the cut-off, the frequency and the curve are held there too.
+_fh_doff = _fh_coord(since=-30, duty="off")
+_pa_run(_fh_doff, 0)
+_fh_doff_null = _fh_coord(since=-30, duty="off", hold=False)
+_pa_run(_fh_doff_null, 0)
+R.check("with duty off a pass still latches the fault", _fh.held(_fh_doff.entry) and not _fh.held(_fh_doff_null.entry))
+
+# 11. A numeric bitmap holds like the binary alarm; zero does not.
+_fh_bits = {raw: _fh_latch({"sensor.fault_code": FakeState(raw, last_updated=_PA_T0 - timedelta(minutes=30))},
+                           [(0, False, None)], entity="sensor.fault_code")[0] for raw in ("3", "0")}
+R.check("a raw fault bitmap holds on non-zero and not on zero", _fh_bits == {"3": [True], "0": [False]}, f"{_fh_bits}")
+
+# 12. The off restore's baseline row (``pump_arbiter._release_row``) is not
+# written into a faulted pump at unload: it stays owed. Off ends the hold, so
+# entering Off hands the row back at once, as with no fault. The space
+# set-point's own restore is not the row and still runs (the design's
+# unload-row carry).
+def _fh_row_writes(c):
+    """The row's writes (mode select, hot-water set-point): every pump write but the space set-point's."""
+    return [(d, (data or {}).get("entity_id"), (data or {}).get("option", (data or {}).get("value")))
+            for d, _s, data in c.hass.services.calls
+            if d in ("select", "number", "switch") and (data or {}).get("entity_id") != "number.water_set"]
+
+
+def _fh_handback(fault, how):
+    """(row writes, latch held) of the hand-back after a written control pass; the alarm on 30 minutes when ``fault``."""
+    c = _fh_coord(state="off")
+    _pa_run(c, 0)
+    if fault:
+        _fh_fault(c, "on", -30)
+    _pa_run(c, 1)
+    c.hass.services.calls.clear()
+    _sa_dt.freeze(_PA_T0 + timedelta(minutes=2))
+    try:
+        if how == "unload":
+            _pa_unload(c)
+            return _fh_row_writes(c), _fh.held(c.entry)
+        _pa_enter_off(c)
+        at_change = _fh_row_writes(c)
+        _pa_run(c, 2)  # Off's own pass: its consult clears the latch
+        return at_change, _fh.held(c.entry)
+    finally:
+        _sa_dt.freeze(None)
+
+
+_fh_unl, _fh_unl_null = _fh_handback(True, "unload"), _fh_handback(False, "unload")
+R.check("unload under the hold writes no baseline row, and drops the latch", _fh_unl == ([], False), f"{_fh_unl}")
+R.check("null control: unload with no fault writes the baseline row", bool(_fh_unl_null[0]), f"{_fh_unl_null}")
+
+
+def _fh_reunload(consult):
+    """Row writes of an unload restore after an unload under the hold, the alarm since cleared;
+    the entry consulted again first (set up afresh) when ``consult``."""
+    c = _fh_coord(state="off")
+    _pa_run(c, 0)
+    _fh_fault(c, "on", -30)
+    _pa_run(c, 1)
+    _sa_dt.freeze(_PA_T0 + timedelta(minutes=2))
+    try:
+        _pa_unload(c)
+        _fh_fault(c, "off", 1)
+        if consult:
+            _fh.holding(c.entry, c.hass, c._config, off=False)
+        c.hass.services.calls.clear()
+        _pa_aio.run(_pa_orr.async_restore(c.hass, c.entry, c._config, "unload"))
+        return _fh_row_writes(c)
+    finally:
+        _sa_dt.freeze(None)
+
+
+_fh_reu, _fh_reu_null = _fh_reunload(True), _fh_reunload(False)
+R.check("the unload's held mark lasts only until the entry's next consult: the next unload writes the owed row",
+        bool(_fh_reu), f"{_fh_reu}")
+R.check("null control: with no consult between them the mark holds and the row stays owed",
+        _fh_reu_null == [], f"{_fh_reu_null}")
+_fh_off, _fh_off_null = _fh_handback(True, "off"), _fh_handback(False, "off")
+R.check("Off ends the hold: entering Off under it writes the baseline row at the mode change, and Off's pass clears the latch",
+        bool(_fh_off[0]) and _fh_off[0] == _fh_off_null[0] and _fh_off[1] is False, f"{_fh_off} vs {_fh_off_null}")
+R.check("null control: with no fault the same mode change writes the baseline row",
+        bool(_fh_off_null[0]), f"{_fh_off_null}")
+
+
+# 12b. A stale plan's hand-back (``off_restore.async_cycle``'s stale half:
+# supply on, frequency and valve back) is an actuation: under the hold the
+# cycle restores nothing, and the keys stay armed for after the clear.
+async def _fh_stale_scn(fault):
+    hass = _r11ar_hass()
+    hass.states.set(_FH_FAULT, FakeState("off", last_updated=_R11AR_T0 - timedelta(hours=2)))
+    entry = _r11ar_Entry(data={**_r11ar_config(), "heat_pump_fault_entity": _FH_FAULT},
+                         entry_id=f"fhst_{next(_R11AR_IDS)}")
+    c = _r11ar_coord(hass, entry)
+    await _r11ar_drive(c)
+    now = _R11AR_T0 + timedelta(minutes=61)
+    if fault:
+        hass.states.set(_FH_FAULT, FakeState("on", last_updated=now - timedelta(minutes=30)))
+    _r11ar_dt.freeze(now)
+    c._last_optimization = now - timedelta(hours=10)
+    await c._apply_action()
+    calls = _r11ar_settle(hass)
+    _r11ar_dt.freeze(None)
+    return c._plan_is_stale(), {e: _r11ar_n(calls, e) for e in _R11AR_FOUR[:3]}, _fh.held(entry)
+
+
+_fh_st = _r11ar_aio.run(_fh_stale_scn(True))
+_fh_st_null = _r11ar_aio.run(_fh_stale_scn(False))
+R.check("a stale plan under the hold hands nothing back: no supply, frequency or valve write",
+        _fh_st[0] is True and _fh_st[2] is True and set(_fh_st[1].values()) == {0}, f"{_fh_st!r}")
+R.check("null control: the same stale cycle with no fault writes the supply switch back",
+        _fh_st_null[0] is True and _fh_st_null[1]["switch.hp"] == 1, f"{_fh_st_null!r}")
+
+# 13. The opt-out: no hold, no repair over a 60-minute fault.
+_fh_opt = _fh_latch({_FH_FAULT: FakeState("on", last_updated=_PA_T0 - timedelta(minutes=60))},
+                    [(0, False, None), (30, False, None)], hold=False)
+R.check("fault_hold off: a 60-minute fault holds nothing and raises nothing", _fh_opt[:2] == ([False, False], []), f"{_fh_opt[:2]}")
+_fh_optc = _fh_coord(since=-60, hold=False)
+_pa_run(_fh_optc, 0)
+R.check("fault_hold off: the control pass writes as today", bool(_fh_pump_writes(_fh_optc)))
+
+# 14. The option: offered beside the fault alarm, on by default, translated.
+from heatpump_optimizer import config_flow as _fh_cf  # noqa: E402
+_fh_rows = [f for f in _fh_cf._OPTION_FIELDS if f.key == "fault_hold"]
+R.check("the options flow offers fault_hold on the pump page, on by default, after the fault alarm",
+        len(_fh_rows) == 1 and _fh_rows[0].default is True and _fh_rows[0].step == "entities_pump"
+        and [f.key for f in _fh_cf._OPTION_FIELDS].index("fault_hold")
+        == [f.key for f in _fh_cf._OPTION_FIELDS].index("heat_pump_fault_entity") + 1,
+        f"{_fh_rows}")
+_fh_tr = {}
+for _fh_lang in ("en", "sv", "de"):
+    _fh_doc = _json.loads((_Path(_fh_cf.__file__).parent / "translations" / f"{_fh_lang}.json").read_text(encoding="utf-8"))
+    _fh_tr[_fh_lang] = (bool(_fh_doc["options"]["step"]["entities_pump"]["data"].get("fault_hold")),
+                        set(_fh_doc["issues"].get(_fh.ISSUE, {})) == {"title", "description"})
+R.check("the option and the repair are translated in every shipped language",
+        _fh_tr == {k: (True, True) for k in ("en", "sv", "de")}, f"{_fh_tr}")
+
+# 15. Each call site hands the latch its own Off and unload: the checks above
+# drive ``holding`` directly, so these drive ``consult`` (through
+# ``pump_arbiter.apply``) and ``heat_curve.publish`` with the pass's own state.
+_fh_cs_rel = _fh_coord(since=-30)
+_fh_cs_rel._entry_released = True
+_pa_run(_fh_cs_rel, 0)
+_fh_cs_rel_null = _fh_coord(since=-30)
+_pa_run(_fh_cs_rel_null, 0)
+R.check("a pass queued before the unload (entry_released) with a 30-minute fault raises no fault repair",
+        _fh_issue(_fh_cs_rel) == [], f"{_fh_issue(_fh_cs_rel)}")
+R.check("null control: the same pass on a loaded entry raises the fault repair",
+        len(_fh_issue(_fh_cs_rel_null)) == 1, f"{_fh_issue(_fh_cs_rel_null)}")
+
+
+def _fh_then(mode):
+    """(held, repairs) after a held pass, then one more pass in ``mode``."""
+    c = _fh_coord(since=-30)
+    _pa_run(c, 0)
+    c._mode = mode
+    _pa_run(c, 1)
+    return _fh.held(c.entry), len(_fh_issue(c))
+
+
+_fh_cs_off = _fh_then(_PA_OFF)
+_fh_cs_off_null = _fh_then(_PA_AUTO)
+R.check("an Optimizer Off pass after a held pass clears the latch and the fault repair",
+        _fh_cs_off == (False, 0), f"{_fh_cs_off}")
+R.check("null control: the same next pass in auto keeps the latch and the repair",
+        _fh_cs_off_null == (True, 1), f"{_fh_cs_off_null}")
+
+
+def _fh_publish_then(mode_off):
+    """Calls, latch and repairs of a publish after a held one, the second at ``mode_off``."""
+    hass = FakeHass({_FH_FAULT: FakeState("on", last_updated=_PA_T0 - timedelta(minutes=30))})
+    cfg = EntryConfig.from_mapping({"heat_pump_fault_entity": _FH_FAULT,
+                                    "ecl110_displace_set_topic": "ecl/displace/set"})
+    entry = _pa_entry(entry_id=f"fh{next(_PA_IDS)}")
+    _sa_dt.freeze(_PA_T0)
+    try:
+        _asyncio.run(_fh_hc.publish(hass, entry, cfg, -3, {"displace": -3}))
+        first = ([c[0] for c in hass.services.calls], _fh.held(entry))
+        _asyncio.run(_fh_hc.publish(hass, entry, cfg, 0, {"displace": 0}, mode_off=mode_off))
+    finally:
+        _sa_dt.freeze(None)
+    return first, ([c[0] for c in hass.services.calls], _fh.held(entry), [i[1] for i in getattr(hass, "issues", [])])
+
+
+_fh_cs_pub = _fh_publish_then(True)
+_fh_cs_pub_null = _fh_publish_then(False)
+R.check("the Off displace under a held latch is published, and clears the latch and the fault repair",
+        _fh_cs_pub == (([], True), (["mqtt"], False, [])), f"{_fh_cs_pub}")
+R.check("null control: the same second displace outside Off is not published and the hold stays",
+        _fh_cs_pub_null == (([], True), ([], True, [_fh.ISSUE])), f"{_fh_cs_pub_null}")
+
+_fh_dv_since = {m: _fh_coord(since=m) for m in (-30, -45)}
+for _fh_c in _fh_dv_since.values():
+    _pa_run(_fh_c, 0)
+_fh_dv_since = {m: _fh_dv(c)["since"] for m, c in _fh_dv_since.items()}
+R.check("the diagnostics row's since is the latch's start, the alarm's last change",
+        _fh_dv_since == {m: (_PA_T0 + timedelta(minutes=m)).isoformat() for m in (-30, -45)}, f"{_fh_dv_since}")
+R.check("null control: with no fault the diagnostics row's since is empty",
+        _fh_dv(_fh_dv_null)["since"] is None, f"{_fh_dv(_fh_dv_null)}")
+
+
 R.section("duty-switch restart learning, part A (design duty-switch-restart-learning)")
 # A hot water -> heating mode write while the compressor runs stops it on some
 # pumps (Bankaifan, pull request 3420). Part A observes, estimates, persists
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 08152a9fb9..387440103b 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -75,6 +75,7 @@ valve_storage_smart_write  # baseline_cost LOWER (129.949 -> 129.251)
 wood_coil  # baseline_cost LOWER (144.781 -> 144.082)
 wood_two_tank  # baseline_cost LOWER (129.949 -> 129.251)
 wood_two_tank_smart_write  # baseline_cost LOWER (129.949 -> 129.251)
+config_flow # R11-OWNER-FAULT-HOLD (#3872): the pump-entities page gains the fault_hold option (a BooleanSelector, default on) beside the Fault alarm entity, so the seed, the seeded render and the plain render each gain the key; all three moved leaves are "present on one side only", ADDED at this head. Float-free and compared exactly, so re-recorded in the committed file (golden.py --record --only config_flow). No solve fixture stores the option, so every other fixture is byte-identical to the merge base (env_drift.py --all, one environment), which is the null.
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index 10a29606fd..b299d912cc 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -1065,6 +1065,7 @@
   "ecl110_mqtt_retain": true,
   "external_heat_detection_enabled": true,
   "external_heat_entity": "sensor.seed_external_heat_entity",
+  "fault_hold": true,
   "floor_return_temp_entity": "sensor.seed_floor_return_temp_entity",
   "flow_curve_cop_enabled": true,
   "flow_meter_entity": "sensor.seed_flow_meter_entity",
@@ -2331,6 +2332,12 @@
     "required": "Optional",
     "selector": "EntitySelector"
    },
+   "fault_hold": {
+    "config": null,
+    "default": "True",
+    "required": "Optional",
+    "selector": "BooleanSelector"
+   },
    "heat_pump_backup_heater_entity": {
     "config": {
      "filter": "[{'domain': ['binary_sensor', 'switch', 'input_boolean', 'sensor']}]"
@@ -5086,6 +5093,12 @@
    "required": "Optional",
    "selector": "EntitySelector"
   },
+  "fault_hold": {
+   "config": null,
+   "default": "True",
+   "required": "Optional",
+   "selector": "BooleanSelector"
+  },
   "heat_pump_backup_heater_entity": {
    "config": {
     "filter": "[{'domain': ['binary_sensor', 'switch', 'input_boolean', 'sensor']}]"
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.9e9a864a.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.9e9a864a.json
new file mode 100644
index 0000000000..1917820518
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._apply_action.BOOLOP.9e9a864a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._apply_action BOOLOP 9e9a864a",
+  "killed_by": "tests/features.py",
+  "old": "        await off_restore.async_cycle(self.hass, self.entry, _ctx_of(self)._config, self._mode == MODE_OFF, stale and not fault_hold.held(self.entry))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`await off_restore.async_cycle(self.hass, self.entry, _ctx_of(self)._config, self._mode == MODE_OFF, stale or not fault_hold.held(self.entry))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=31."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.0bf30dbd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.13e8b4c7.json
similarity index 62%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.0bf30dbd.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.13e8b4c7.json
index 99332cf198..f3772fea00 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.0bf30dbd.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._command_frequency.GUARD_OFF.13e8b4c7.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._command_frequency GUARD_OFF 0bf30dbd",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._command_frequency GUARD_OFF 13e8b4c7",
   "killed_by": "tests/features.py",
-  "old": "        if not entity_id or self._freq_mode() != FREQ_MODE_CONTROL or self._mode == MODE_OFF or _plan_let_go(self):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "old": "        if not entity_id or self._freq_mode() != FREQ_MODE_CONTROL or self._mode == MODE_OFF or _plan_let_go(self) or fault_hold.held(self.entry):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json b/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json
index 017b4d79d1..62df02cc82 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/_missed.GUARD_OFF.f28578a3.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:_missed GUARD_OFF f28578a3",
   "killed_by": "tests/block_duty.py",
   "old": "    if planned == \"dhw\" and actual == \"idle\" and _not_startable(row):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json
index 1227a261db..f317aa5943 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.CMP_BOUND.452b7046.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:_not_startable CMP_BOUND 452b7046",
   "killed_by": "tests/block_duty.py",
   "old": "    return start is not None and tank is not None and float(tank) >= start",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return start is not None and tank is not None and float(tank) > start`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return start is not None and tank is not None and float(tank) > start`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json
index 5dcf7ebe8b..0a64fb991f 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/_not_startable.RETURN_DEL.452b7046.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:_not_startable RETURN_DEL 452b7046",
   "killed_by": "tests/block_duty.py",
   "old": "    return start is not None and tank is not None and float(tank) >= start",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/observe.BOOLOP.a38120fc.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.BOOLOP.a38120fc.json
new file mode 100644
index 0000000000..6e5989dc0b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.BOOLOP.a38120fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe BOOLOP a38120fc",
+  "killed_by": "tests/features.py",
+  "old": "    if ran is not None and now - start >= RUN_SETTLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if ran is not None or now - start >= RUN_SETTLE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/observe.CMP_BOUND.a38120fc.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.CMP_BOUND.a38120fc.json
new file mode 100644
index 0000000000..af35c053b8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.CMP_BOUND.a38120fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe CMP_BOUND a38120fc",
+  "killed_by": "tests/features.py",
+  "old": "    if ran is not None and now - start >= RUN_SETTLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if ran is not None and now - start > RUN_SETTLE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.3c85dd51.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.3c85dd51.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.3c85dd51.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.3c85dd51.json
index 9fe3e74eb5..ec11b3b32d 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.3c85dd51.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.3c85dd51.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF 3c85dd51",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF 3c85dd51",
   "killed_by": "tests/features.py",
   "old": "    if row is None or row[\"start\"] != start:",
-  "reason": "pump-duty arbiter revision; `if row is None or row[\"start\"] != start:` -> `if False:` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `if row is None or row[\"start\"] != start:` -> `if False:` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.57f875bd.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.57f875bd.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.57f875bd.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.57f875bd.json
index ae3eb694aa..74b2dc9bff 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.57f875bd.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.57f875bd.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF 57f875bd",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF 57f875bd",
   "killed_by": "tests/features.py",
   "old": "        if row is not None:",
-  "reason": "pump-duty arbiter revision; `if row is not None:` -> `if False:` fails 3 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `if row is not None:` -> `if False:` fails 3 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.a38120fc.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.a38120fc.json
new file mode 100644
index 0000000000..1b28bcdf62
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.a38120fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF a38120fc",
+  "killed_by": "tests/features.py",
+  "old": "    if ran is not None and now - start >= RUN_SETTLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.f2ad4d4c.json b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.f2ad4d4c.json
similarity index 54%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.f2ad4d4c.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.f2ad4d4c.json
index 0c55cc7615..1296d847da 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.f2ad4d4c.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/observe.GUARD_OFF.f2ad4d4c.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF f2ad4d4c",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:observe GUARD_OFF f2ad4d4c",
   "killed_by": "tests/features.py",
   "old": "    elif row[\"plan\"] is not inp.plan:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json
index 2c46caa81c..f1f257d9dd 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.2bdf9629.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict BOOLOP 2bdf9629",
   "killed_by": "tests/features.py",
   "old": "    elif actual == planned or (planned == \"both\" and actual != \"idle\"):",
-  "reason": "pump-duty arbiter revision; `elif actual == planned or (planned == \"both\" and actual != \"idle\"):` -> `elif actual == planned or (planned == \"both\" or actual != \"idle\"):` fails 1 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `elif actual == planned or (planned == \"both\" and actual != \"idle\"):` -> `elif actual == planned or (planned == \"both\" or actual != \"idle\"):` fails 1 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json
index b22b442fcb..6794122051 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.BOOLOP.af494230.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict BOOLOP af494230",
   "killed_by": "tests/features.py",
   "old": "    rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C",
-  "reason": "pump-duty arbiter revision; `rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` -> `rose = None not in (tank, row[\"tank\"]) or float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24."
+  "reason": "pump-duty arbiter revision; `rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` -> `rose = None not in (tank, row[\"tank\"]) or float(tank) - float(row[\"tank\"]) >= TANK_RISE_C` crashes the arbiter section in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json
index 4b2b07e75b..17cf4238da 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.CMP_BOUND.af494230.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict CMP_BOUND af494230",
   "killed_by": "tests/features.py",
   "old": "    rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) >= TANK_RISE_C",
-  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) > TANK_RISE_C`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`rose = None not in (tank, row[\"tank\"]) and float(tank) - float(row[\"tank\"]) > TANK_RISE_C`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json
index 0fd3bcfca8..d845cc58a6 100644
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.2bdf9629.json
@@ -2,5 +2,5 @@
   "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF 2bdf9629",
   "killed_by": "tests/features.py",
   "old": "    elif actual == planned or (planned == \"both\" and actual != \"idle\"):",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7. Moved verbatim from pump_arbiter.py to duty_ledger.py by R11-OWNER-FAULT-HOLD; the same driver reaches it through pump_arbiter._observe."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.af4ac328.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.af4ac328.json
new file mode 100644
index 0000000000..df21f438de
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.af4ac328.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF af4ac328",
+  "killed_by": "tests/features.py",
+  "old": "    elif planned is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.f7f7cbce.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.ca33e38f.json
similarity index 53%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.f7f7cbce.json
rename to tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.ca33e38f.json
index a5c0d609f0..2ebf4fbdde 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.f7f7cbce.json
+++ b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.ca33e38f.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF f7f7cbce",
+  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF ca33e38f",
   "killed_by": "tests/block_duty.py",
-  "old": "    if mode != DUTY_CONTROL or _pump_off(inp, held):",
+  "old": "    if row.get(\"faulted\"):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.d746330a.json b/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.d746330a.json
deleted file mode 100644
index e745e4d393..0000000000
--- a/tests/mutation_ledger/killed_by/duty_ledger.py/step_verdict.GUARD_OFF.d746330a.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_ledger.py:step_verdict GUARD_OFF d746330a",
-  "killed_by": "tests/features.py",
-  "old": "    if planned is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/on_room_event.GUARD_OFF.6501682d.json b/tests/mutation_ledger/killed_by/early_cutoff.py/on_room_event.GUARD_OFF.6501682d.json
new file mode 100644
index 0000000000..d89afd5662
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/on_room_event.GUARD_OFF.6501682d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:on_room_event GUARD_OFF 6501682d",
+  "killed_by": "tests/structure.py",
+  "old": "    if fault_hold.consult(wiring.entry, inp, now):  # a faulted pump is not switched off",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # a faulted pump is not switched off`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_clear.BOOLOP.e5dfa31c.json b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.BOOLOP.e5dfa31c.json
new file mode 100644
index 0000000000..05af71b255
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.BOOLOP.e5dfa31c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_clear BOOLOP e5dfa31c",
+  "killed_by": "tests/features.py",
+  "old": "    if not any(other.holding and other.hass is hass for other in list(_STATES.values())):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not any(other.holding or other.hass is hass for other in list(_STATES.values())):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_clear.GUARD_OFF.e5dfa31c.json b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.GUARD_OFF.e5dfa31c.json
new file mode 100644
index 0000000000..8c4d609b7f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_clear.GUARD_OFF.e5dfa31c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_clear GUARD_OFF e5dfa31c",
+  "killed_by": "tests/features.py",
+  "old": "    if not any(other.holding and other.hass is hass for other in list(_STATES.values())):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.51d9802d.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.51d9802d.json
new file mode 100644
index 0000000000..295d093a33
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.51d9802d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move BOOLOP 51d9802d",
+  "killed_by": "tests/features.py",
+  "old": "    elif latch.holding and not on:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`elif latch.holding or not on:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.97208b64.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.97208b64.json
new file mode 100644
index 0000000000..5cd52fec60
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.BOOLOP.97208b64.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move BOOLOP 97208b64",
+  "killed_by": "tests/features.py",
+  "old": "    if on and not latch.holding:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if on or not latch.holding:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.51d9802d.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.51d9802d.json
new file mode 100644
index 0000000000..d48f5d9e87
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.51d9802d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move GUARD_OFF 51d9802d",
+  "killed_by": "tests/features.py",
+  "old": "    elif latch.holding and not on:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.97208b64.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.97208b64.json
new file mode 100644
index 0000000000..a6441f7bd9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.GUARD_OFF.97208b64.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move GUARD_OFF 97208b64",
+  "killed_by": "tests/features.py",
+  "old": "    if on and not latch.holding:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/_move.RETURN_DEL.d2b1cb1d.json b/tests/mutation_ledger/killed_by/fault_hold.py/_move.RETURN_DEL.d2b1cb1d.json
new file mode 100644
index 0000000000..1098adb42d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/_move.RETURN_DEL.d2b1cb1d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:_move RETURN_DEL d2b1cb1d",
+  "killed_by": "tests/features.py",
+  "old": "    return on",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/consult.RETURN_DEL.3a02bb96.json b/tests/mutation_ledger/killed_by/fault_hold.py/consult.RETURN_DEL.3a02bb96.json
new file mode 100644
index 0000000000..5e91f0cd2d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/consult.RETURN_DEL.3a02bb96.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:consult RETURN_DEL 3a02bb96",
+  "killed_by": "tests/features.py",
+  "old": "    return holding(entry, inp.hass, inp.config, off=inp.mode == MODE_OFF, released=inp.entry_released, now=now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/gate.GUARD_OFF.fb639107.json b/tests/mutation_ledger/killed_by/fault_hold.py/gate.GUARD_OFF.fb639107.json
new file mode 100644
index 0000000000..f5fcb2560b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/gate.GUARD_OFF.fb639107.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:gate GUARD_OFF fb639107",
+  "killed_by": "tests/features.py",
+  "old": "    if value is not False or not consult(entry, inp):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=77."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/held.BOOLOP.2e25e783.json b/tests/mutation_ledger/killed_by/fault_hold.py/held.BOOLOP.2e25e783.json
new file mode 100644
index 0000000000..3c883cd481
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/held.BOOLOP.2e25e783.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:held BOOLOP 2e25e783",
+  "killed_by": "tests/features.py",
+  "old": "    return latch is not None and latch.holding",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return latch is not None or latch.holding`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/held.RETURN_DEL.2e25e783.json b/tests/mutation_ledger/killed_by/fault_hold.py/held.RETURN_DEL.2e25e783.json
new file mode 100644
index 0000000000..5ff1300f5d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/held.RETURN_DEL.2e25e783.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:held RETURN_DEL 2e25e783",
+  "killed_by": "tests/features.py",
+  "old": "    return latch is not None and latch.holding",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.411a9678.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.411a9678.json
new file mode 100644
index 0000000000..1923a532e6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.411a9678.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding BOOLOP 411a9678",
+  "killed_by": "tests/features.py",
+  "old": "    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return _move(latch, hass, latch.since is not None or now - latch.since >= FAULT_HOLD_AFTER)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.f2e3b5f4.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.f2e3b5f4.json
new file mode 100644
index 0000000000..4890d441b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.BOOLOP.f2e3b5f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding BOOLOP f2e3b5f4",
+  "killed_by": "tests/features.py",
+  "old": "    if reading.flag is False and reading.ok:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if reading.flag is False or reading.ok:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=34."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.CLAMP_DROP.ea67468b.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CLAMP_DROP.ea67468b.json
new file mode 100644
index 0000000000..b1ce1f8487
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CLAMP_DROP.ea67468b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding CLAMP_DROP ea67468b",
+  "killed_by": "tests/features.py",
+  "old": "        latch.since = min(dt_util.as_utc(changed), now) if changed is not None else now",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`latch.since = (dt_util.as_utc(changed)) if changed is not None else now`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.CMP_BOUND.411a9678.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CMP_BOUND.411a9678.json
new file mode 100644
index 0000000000..c2204bd049
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.CMP_BOUND.411a9678.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding CMP_BOUND 411a9678",
+  "killed_by": "tests/features.py",
+  "old": "    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return _move(latch, hass, latch.since is not None and now - latch.since > FAULT_HOLD_AFTER)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.0bd5a755.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.0bd5a755.json
new file mode 100644
index 0000000000..08aa3d51dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.0bd5a755.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF 0bd5a755",
+  "killed_by": "tests/features.py",
+  "old": "    if released:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.8317e5f0.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.8317e5f0.json
new file mode 100644
index 0000000000..0f207792c8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.8317e5f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF 8317e5f0",
+  "killed_by": "tests/features.py",
+  "old": "    if off or not cfg.fault_hold or not cfg.heat_pump_fault_entity:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.e33caa55.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.e33caa55.json
new file mode 100644
index 0000000000..28543119a5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.e33caa55.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF e33caa55",
+  "killed_by": "tests/features.py",
+  "old": "    elif reading.flag and reading.ok and latch.since is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=34."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.f2e3b5f4.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.f2e3b5f4.json
new file mode 100644
index 0000000000..5625829c8d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.GUARD_OFF.f2e3b5f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding GUARD_OFF f2e3b5f4",
+  "killed_by": "tests/features.py",
+  "old": "    if reading.flag is False and reading.ok:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.411a9678.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.411a9678.json
new file mode 100644
index 0000000000..c4411b2fa4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.411a9678.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding RETURN_DEL 411a9678",
+  "killed_by": "tests/features.py",
+  "old": "    return _move(latch, hass, latch.since is not None and now - latch.since >= FAULT_HOLD_AFTER)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=35."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.6c549d41.json b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.6c549d41.json
new file mode 100644
index 0000000000..cd3fd38a6c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/holding.RETURN_DEL.6c549d41.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:holding RETURN_DEL 6c549d41",
+  "killed_by": "tests/features.py",
+  "old": "        return _move(latch, hass, False)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/release.BOOLOP.88f5261f.json b/tests/mutation_ledger/killed_by/fault_hold.py/release.BOOLOP.88f5261f.json
new file mode 100644
index 0000000000..d3d0aa213b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/release.BOOLOP.88f5261f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:release BOOLOP 88f5261f",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    was = latch is not None and latch.holding",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`was = latch is not None or latch.holding`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/release.GUARD_OFF.f01954aa.json b/tests/mutation_ledger/killed_by/fault_hold.py/release.GUARD_OFF.f01954aa.json
new file mode 100644
index 0000000000..c8699dcc0c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/release.GUARD_OFF.f01954aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:release GUARD_OFF f01954aa",
+  "killed_by": "tests/features.py",
+  "old": "    if was:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/release.RETURN_DEL.25a124b5.json b/tests/mutation_ledger/killed_by/fault_hold.py/release.RETURN_DEL.25a124b5.json
new file mode 100644
index 0000000000..158cb6689d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/release.RETURN_DEL.25a124b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:release RETURN_DEL 25a124b5",
+  "killed_by": "tests/features.py",
+  "old": "    return was",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_hold.py/unload_holds.RETURN_DEL.d858ff0c.json b/tests/mutation_ledger/killed_by/fault_hold.py/unload_holds.RETURN_DEL.d858ff0c.json
new file mode 100644
index 0000000000..a0ba58aae6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_hold.py/unload_holds.RETURN_DEL.d858ff0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:unload_holds RETURN_DEL d858ff0c",
+  "killed_by": "tests/features.py",
+  "old": "    return held(entry) or entry in _RELEASED_HOLDING",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/heat_curve.py/publish.GUARD_OFF.e55abc27.json b/tests/mutation_ledger/killed_by/heat_curve.py/publish.GUARD_OFF.e55abc27.json
new file mode 100644
index 0000000000..89eed353ce
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/heat_curve.py/publish.GUARD_OFF.e55abc27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/heat_curve.py:publish GUARD_OFF e55abc27",
+  "killed_by": "tests/structure.py",
+  "old": "    if fault_hold.holding(entry, hass, config, off=mode_off, released=released):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.8444642c.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.8444642c.json
new file mode 100644
index 0000000000..a362be50cd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.8444642c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 8444642c",
+  "killed_by": "tests/structure.py",
+  "old": "    if mode != DUTY_CONTROL or _pump_off(inp, held) or _fault_stands(inp.hass, held, faulted):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.88e2f26e.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.GUARD_OFF.6379a114.json
similarity index 77%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.88e2f26e.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.GUARD_OFF.6379a114.json
index 00db37f89b..1d0542261c 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.88e2f26e.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.GUARD_OFF.6379a114.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_release_row GUARD_OFF 88e2f26e",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_fault_stands GUARD_OFF 6379a114",
   "killed_by": "tests/features.py",
-  "old": "    if coord is None:",
+  "old": "    if faulted:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.RETURN_DEL.20ad27fb.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.RETURN_DEL.20ad27fb.json
new file mode 100644
index 0000000000..6496088a39
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_fault_stands.RETURN_DEL.20ad27fb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_fault_stands RETURN_DEL 20ad27fb",
+  "killed_by": "tests/features.py",
+  "old": "    return faulted",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.ba67817a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.bede1f64.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.ba67817a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.bede1f64.json
index 5085e99d55..7502577eb3 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.ba67817a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_lead_mode.GUARD_OFF.bede1f64.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_lead_mode GUARD_OFF ba67817a",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_lead_mode GUARD_OFF bede1f64",
   "killed_by": "tests/features.py",
-  "old": "        if inp.entry_released or inp.mode == MODE_OFF or not _pump_off(inp, held):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "        if inp.entry_released or inp.mode == MODE_OFF or not _pump_off(inp, held) or fault_hold.held(coord.entry):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.BOOLOP.577b31a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.BOOLOP.577b31a4.json
deleted file mode 100644
index 8dd017cd61..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.BOOLOP.577b31a4.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe BOOLOP 577b31a4",
-  "killed_by": "tests/guard_pins.py",
-  "old": "    if power is not None and now - start >= RUN_SETTLE:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if power is not None or now - start >= RUN_SETTLE:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.3cd6139b.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.3cd6139b.json
new file mode 100644
index 0000000000..baee865a42
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.3cd6139b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe CMP_BOUND 3cd6139b",
+  "killed_by": "tests/features.py",
+  "old": "    duty_ledger.observe(held, inp, duty, now, ran=None if power is None else float(power) >= _ran_kw(inp),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`duty_ledger.observe(held, inp, duty, now, ran=None if power is None else float(power) > _ran_kw(inp),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.577b31a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.577b31a4.json
deleted file mode 100644
index 99e229cf71..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.577b31a4.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe CMP_BOUND 577b31a4",
-  "killed_by": "tests/features.py",
-  "old": "    if power is not None and now - start >= RUN_SETTLE:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if power is not None and now - start > RUN_SETTLE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.d24bfcb6.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.d24bfcb6.json
deleted file mode 100644
index 8d7fb873ff..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.CMP_BOUND.d24bfcb6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe CMP_BOUND d24bfcb6",
-  "killed_by": "tests/features.py",
-  "old": "        row[\"ran\"] = row[\"ran\"] or float(power) >= _ran_kw(inp)",
-  "reason": "R9-EG-B6 (#1739) renamed the line's reads to the ArbiterInputs snapshot. Re-measured on a git-archive export at be777f2f: driving tests/features.py fails 3 of 3701 feature checks (`a draw exactly at the meter's threshold is a run; one hair below is not` among them), against the driver's baseline reds on the export (the #363 recorded_at check a git-archive copy cannot stamp, and the machine-sensitive R9-F2.1 P3 check, which fails identically at the merge base on this Mac) are named and excluded."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.BOOLOP.2a46488d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.BOOLOP.2a46488d.json
new file mode 100644
index 0000000000..9685978b94
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.BOOLOP.2a46488d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_release_row BOOLOP 2a46488d",
+  "killed_by": "tests/features.py",
+  "old": "    if coord is None or (reason == \"unload\" and fault_hold.unload_holds(coord.entry)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if coord is None or (reason == \"unload\" or fault_hold.unload_holds(coord.entry)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.577b31a4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.2a46488d.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.577b31a4.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.2a46488d.json
index f4ea4c0ade..70875b1dd5 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_observe.GUARD_OFF.577b31a4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_release_row.GUARD_OFF.2a46488d.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_observe GUARD_OFF 577b31a4",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_release_row GUARD_OFF 2a46488d",
   "killed_by": "tests/structure.py",
-  "old": "    if power is not None and now - start >= RUN_SETTLE:",
+  "old": "    if coord is None or (reason == \"unload\" and fault_hold.unload_holds(coord.entry)):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/survivor_triage/fault_hold.py/gate.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/survivor_triage/fault_hold.py/gate.RETURN_DEL.da9e8e97.json
new file mode 100644
index 0000000000..51e5d998f5
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/fault_hold.py/gate.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_hold.py:gate RETURN_DEL da9e8e97",
+  "old": "    return None",
+  "reason": "Equivalent (RETURN_DEL) in `gate`: the mutated line is the function's last statement, `return None`; replaced by `pass` the function falls off its end and returns None all the same. The held-OFF arm above it is pinned by tests/features.py, \"the cycle's OFF under the hold is left, and the step tick writes it once the alarm clears\".",
+  "verdict": "equivalent"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 62a1f44e78..04e8e923be 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -16,7 +16,7 @@
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
- "module_excess_loc": 21763,
+ "module_excess_loc": 21728,
  "name_kept_members": 38,
  "recorded_at": "3153a635b4012d3f8a157c2aaaa34f8da5c8d357",
  "seam_cut_total": 413,

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
