# Review packet #3198
head: 25e478a7fe7315710064e953bea1f0de3ace607e
base: 6125b263d94e7ea8c43d31eb483869f8d8c83019

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=127080212795 neutral
arch-score / arch-score id=127079887798 success
arm id=127079712181 skipped
budget-raise-gate / budget-raise-gate id=127079887794 success
cancel-superseded id=127079717319 success
codeql / Analyze (actions) id=127079887809 success
codeql / Analyze (javascript-typescript) id=127079887931 success
codeql / Analyze (python) id=127079887739 in_progress
governance / delivery-status id=127079888159 failure
governance / delivery-status-publish id=127079890107 skipped
governance / env-matrix id=127079887826 success
governance / instrument-self-tests id=127079887833 in_progress
governance / policy-docs id=127079887818 success
governance / record id=127079889450 skipped
governance / wave-script id=127079887757 success
hassfest / hassfest id=127079887837 success
kernel-points id=127079889419 skipped
prelude id=127079717623 success
refresh id=127079717575 success
tests / arch-instrument id=127080097901 success
tests / briefs id=127079887951 success
tests / browser id=127080097838 success
tests / closure-scope id=127079887825 success
tests / closures id=127080097724 in_progress
tests / coverage id=127080097749 in_progress
tests / fast (3.14) id=127080097853 in_progress
tests / mutation id=127079887780 in_progress
tests / nightly-ha id=127080098966 skipped
tests / nightly-status id=127079887914 failure
tests / replay id=127080097682 in_progress
tests / typing id=127080097720 success
validate / validate-hacs id=127079887651 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         NODE_PATH=/opt/node22/lib/node_modules PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs
             `tests/card_browser.mjs` is in the tree at this head
  ok         bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --only under-scoped
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_scores_envelope.py
             `dev/audit/harnesses/r10_scores_envelope.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  unverified python3 -c 'import numpy,scipy;print(numpy.__version__,scipy.__version__)'
             python3 runs an inline script rather than a file
  ok         bash tools/audit/seat/cloud-setup.sh
             `tools/audit/seat/cloud-setup.sh` is in the tree at this head

FIGURES: 12 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.da4f6087.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.da4f6087.json
new file mode 100644
index 000000000..d4b12c6cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.da4f6087.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop RETURN_DEL da4f6087",
+  "killed_by": "tests/features.py",
+  "old": "            return COP_REFUSED_FROZEN",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.CLAMP_DROP.7a634b7b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.CLAMP_DROP.7a634b7b.json
deleted file mode 100644
index 870199965..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.CLAMP_DROP.7a634b7b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample CLAMP_DROP 7a634b7b",
-  "killed_by": "tests/features.py",
-  "old": "            book[\"kwh\"] = finite_float(book.get(\"kwh\"), 0.0) + max(0.0, kwh)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`book[\"kwh\"] = finite_float(book.get(\"kwh\"), 0.0) + (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.05bb5b4f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.05bb5b4f.json
deleted file mode 100644
index 9765dbd07..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.05bb5b4f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample GUARD_OFF 05bb5b4f",
-  "killed_by": "tests/features.py",
-  "old": "        if spot_known and np.isfinite(sek):  # #2229: an unpriced kWh pays nothing",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: GUARD_OFF (`if False:  # #2229: an unpriced kWh pays nothing`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.16f2087d.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.16f2087d.json
new file mode 100644
index 000000000..18eb346e3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.16f2087d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample GUARD_OFF 16f2087d",
+  "killed_by": "tests/features.py",
+  "old": "        if spot_known:  # #2229: an unpriced kWh pays nothing",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # #2229: an unpriced kWh pays nothing`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.BOOLOP.58685ad7.json b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.BOOLOP.58685ad7.json
new file mode 100644
index 000000000..28558f7bd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.BOOLOP.58685ad7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:compose_scores BOOLOP 58685ad7",
+  "killed_by": "tests/features.py",
+  "old": "    if machine[0] is None and machine_waits_on is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if machine[0] is None or machine_waits_on is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.GUARD_OFF.58685ad7.json b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.GUARD_OFF.58685ad7.json
new file mode 100644
index 000000000..300d0767a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.GUARD_OFF.58685ad7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:compose_scores GUARD_OFF 58685ad7",
+  "killed_by": "tests/features.py",
+  "old": "    if machine[0] is None and machine_waits_on is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.RETURN_DEL.e5451d75.json b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.RETURN_DEL.e5451d75.json
new file mode 100644
index 000000000..b6dc9c331
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.RETURN_DEL.e5451d75.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:compose_scores RETURN_DEL e5451d75",
+  "killed_by": "tests/features.py",
+  "old": "    return scores",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.4fe0081d.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.4fe0081d.json
deleted file mode 100644
index d9a50c983..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.4fe0081d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score CLAMP_DROP 4fe0081d",
-  "killed_by": "tests/features.py",
-  "old": "    return (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0, None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 4e38e7d7b3138b24c97e7d0fbea74965c1d43d62: CLAMP_DROP (`return (1.0 - float((cusum_stat / COP_HEALTH_THRESHOLD))) * 100.0, None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.be6c0635.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.be6c0635.json
new file mode 100644
index 000000000..8d6932087
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.be6c0635.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score CLAMP_DROP be6c0635",
+  "killed_by": "tests/features.py",
+  "old": "    grade = (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`grade = (1.0 - float((cusum_stat / COP_HEALTH_THRESHOLD))) * 100.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.4fe0081d.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.4fe0081d.json
deleted file mode 100644
index ca0985ce8..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.4fe0081d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score RETURN_DEL 4fe0081d",
-  "killed_by": "tests/features.py",
-  "old": "    return (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0, None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 4e38e7d7b3138b24c97e7d0fbea74965c1d43d62: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.e0823a01.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.e0823a01.json
new file mode 100644
index 000000000..a53bd4224
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.e0823a01.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score RETURN_DEL e0823a01",
+  "killed_by": "tests/features.py",
+  "old": "    return grade, None, [{\"code\": \"cop_shortfall\", \"points\": grade - SCORE_REFERENCE[\"machine\"]}]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.363c2e9c.json b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.363c2e9c.json
new file mode 100644
index 000000000..bb22683ff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.363c2e9c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:<module> CONST 363c2e9c",
+  "killed_by": "tests/features.py",
+  "old": "REFERENCE = 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`REFERENCE = 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.a755fc85.json b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.a755fc85.json
new file mode 100644
index 000000000..3178a477b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.a755fc85.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:<module> CONST a755fc85",
+  "killed_by": "tests/features.py",
+  "old": "FULL_SAVING = 0.2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`FULL_SAVING = 0.4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/as_stored.RETURN_DEL.4a99c2f5.json b/tests/mutation_ledger/killed_by/driving_grade.py/as_stored.RETURN_DEL.4a99c2f5.json
new file mode 100644
index 000000000..1a8beb249
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/as_stored.RETURN_DEL.4a99c2f5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:as_stored RETURN_DEL 4a99c2f5",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return dict(drivers) if grade is not None else {}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/book_keys.RETURN_DEL.6a115196.json b/tests/mutation_ledger/killed_by/driving_grade.py/book_keys.RETURN_DEL.6a115196.json
new file mode 100644
index 000000000..02acdf050
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/book_keys.RETURN_DEL.6a115196.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:book_keys RETURN_DEL 6a115196",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return tuple(key for key in (\"kwh_lo\", \"sek_lo\") if key in day)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.BOOLOP.459abf3a.json b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.BOOLOP.459abf3a.json
new file mode 100644
index 000000000..40ab26723
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.BOOLOP.459abf3a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:day_drivers BOOLOP 459abf3a",
+  "killed_by": "tests/features.py",
+  "old": "    scale = sample / total if sample > 0.0 and total > 0.0 else 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`scale = sample / total if sample > 0.0 or total > 0.0 else 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.CMP_BOUND.459abf3a.json b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.CMP_BOUND.459abf3a.json
new file mode 100644
index 000000000..eb07b053e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.CMP_BOUND.459abf3a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:day_drivers CMP_BOUND 459abf3a",
+  "killed_by": "tests/features.py",
+  "old": "    scale = sample / total if sample > 0.0 and total > 0.0 else 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`scale = sample / total if sample >= 0.0 and total > 0.0 else 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.RETURN_DEL.de93dde0.json b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.RETURN_DEL.de93dde0.json
new file mode 100644
index 000000000..24b3bd4bd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.RETURN_DEL.de93dde0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:day_drivers RETURN_DEL de93dde0",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return {code: value * scale for code, value in saved.items()}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/fold.CLAMP_DROP.53f5bf1a.json b/tests/mutation_ledger/killed_by/driving_grade.py/fold.CLAMP_DROP.53f5bf1a.json
new file mode 100644
index 000000000..467283f9d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/fold.CLAMP_DROP.53f5bf1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:fold CLAMP_DROP 53f5bf1a",
+  "killed_by": "tests/features.py",
+  "old": "    sample = float(np.clip(saved_fraction / FULL_SAVING, 0.0, 1.0)) * 100.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`sample = float((saved_fraction / FULL_SAVING)) * 100.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/fold.GUARD_OFF.40cc2060.json b/tests/mutation_ledger/killed_by/driving_grade.py/fold.GUARD_OFF.40cc2060.json
new file mode 100644
index 000000000..4d94d3efb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/fold.GUARD_OFF.40cc2060.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:fold GUARD_OFF 40cc2060",
+  "killed_by": "tests/features.py",
+  "old": "    if grade is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/fold.RETURN_DEL.c42c3b7a.json b/tests/mutation_ledger/killed_by/driving_grade.py/fold.RETURN_DEL.c42c3b7a.json
new file mode 100644
index 000000000..fd39bd31f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/fold.RETURN_DEL.c42c3b7a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:fold RETURN_DEL c42c3b7a",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return sample",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/held.RETURN_DEL.7522a45a.json b/tests/mutation_ledger/killed_by/driving_grade.py/held.RETURN_DEL.7522a45a.json
new file mode 100644
index 000000000..74eb29a6f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/held.RETURN_DEL.7522a45a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:held RETURN_DEL 7522a45a",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return _DRIVERS_BY_OWNER.setdefault(owner, {})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/published.GUARD_OFF.bfca7a08.json b/tests/mutation_ledger/killed_by/driving_grade.py/published.GUARD_OFF.bfca7a08.json
new file mode 100644
index 000000000..7d4b617dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/published.GUARD_OFF.bfca7a08.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:published GUARD_OFF bfca7a08",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    if grade is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/published.RETURN_DEL.974e5580.json b/tests/mutation_ledger/killed_by/driving_grade.py/published.RETURN_DEL.974e5580.json
new file mode 100644
index 000000000..9e8cbc8d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/published.RETURN_DEL.974e5580.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:published RETURN_DEL 974e5580",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return [{\"code\": code, \"points\": value} for code, value in points.items()]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/restore.BOOLOP.91eb33c9.json b/tests/mutation_ledger/killed_by/driving_grade.py/restore.BOOLOP.91eb33c9.json
new file mode 100644
index 000000000..04270b578
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/restore.BOOLOP.91eb33c9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:restore BOOLOP 91eb33c9",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(stored, Mapping) and admitted(stored):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(stored, Mapping) or admitted(stored):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/restore.GUARD_OFF.91eb33c9.json b/tests/mutation_ledger/killed_by/driving_grade.py/restore.GUARD_OFF.91eb33c9.json
new file mode 100644
index 000000000..590108102
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/restore.GUARD_OFF.91eb33c9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:restore GUARD_OFF 91eb33c9",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(stored, Mapping) and admitted(stored):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.15ec03d2.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.15ec03d2.json
new file mode 100644
index 000000000..9dd9658a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.15ec03d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally BOOLOP 15ec03d2",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(spot) and hours > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if np.isfinite(spot) or hours > 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.986a86f9.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.986a86f9.json
new file mode 100644
index 000000000..ede0362a1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.986a86f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally BOOLOP 986a86f9",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(sek) and spot < book[\"spot_sum\"] / book[\"spot_h\"]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if np.isfinite(sek) or spot < book[\"spot_sum\"] / book[\"spot_h\"]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.3611eb0b.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.3611eb0b.json
new file mode 100644
index 000000000..b4dbefb02
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.3611eb0b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CLAMP_DROP 3611eb0b",
+  "killed_by": "tests/features.py",
+  "old": "        _add(book, \"kwh\", max(0.0, kwh))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`_add(book, \"kwh\", (0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.4e14db88.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.4e14db88.json
new file mode 100644
index 000000000..9a2328e32
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.4e14db88.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CLAMP_DROP 4e14db88",
+  "killed_by": "tests/features.py",
+  "old": "            _add(book, \"kwh_lo\", max(0.0, kwh))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`_add(book, \"kwh_lo\", (0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.15ec03d2.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.15ec03d2.json
new file mode 100644
index 000000000..985d9514f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.15ec03d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CMP_BOUND 15ec03d2",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(spot) and hours > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if np.isfinite(spot) and hours >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.986a86f9.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.986a86f9.json
new file mode 100644
index 000000000..cdead06f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.986a86f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CMP_BOUND 986a86f9",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(sek) and spot < book[\"spot_sum\"] / book[\"spot_h\"]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if np.isfinite(sek) and spot <= book[\"spot_sum\"] / book[\"spot_h\"]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.15ec03d2.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.15ec03d2.json
new file mode 100644
index 000000000..9211c1489
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.15ec03d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally GUARD_OFF 15ec03d2",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(spot) and hours > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.72ccbc15.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.72ccbc15.json
new file mode 100644
index 000000000..4e46d224d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.72ccbc15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally GUARD_OFF 72ccbc15",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(sek):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.986a86f9.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.986a86f9.json
new file mode 100644
index 000000000..a43220076
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.986a86f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally GUARD_OFF 986a86f9",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(sek) and spot < book[\"spot_sum\"] / book[\"spot_h\"]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.RETURN_DEL.22c4e90c.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.RETURN_DEL.22c4e90c.json
new file mode 100644
index 000000000..90c8795ab
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.RETURN_DEL.22c4e90c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally RETURN_DEL 22c4e90c",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return book",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.BOOLOP.05bb5b4f.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.BOOLOP.05bb5b4f.json
deleted file mode 100644
index f6089b082..000000000
--- a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.BOOLOP.05bb5b4f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample BOOLOP 05bb5b4f",
-  "old": "        if spot_known and np.isfinite(sek):  # #2229: an unpriced kWh pays nothing",
-  "reason": "Equivalent (BOOLOP, `and` -> `or`): the two differ only when `spot_known != np.isfinite(sek)`, and `spot_known` is not free -- it is `pending.get(\"spot_price\") is not None`, whose ONLY writer is `_pending_prediction`'s `\"spot_price\": self._current_spot_price()` (coordinator.py:9877), and that getter is `float | None` over values `_known_prices_for` admitted through `_raw_value`, which requires a FINITE float. So on every input the writer can produce: `spot_known` False means `spot` is None, `_as_float(None, nan)` is nan, and `sek = energy * nan` is non-finite, so `and` and `or` are both False; `spot_known` True means `spot` is a finite float, so `sek` is finite and both are True. The mutant is separated only by a `spot_price` that is neither None nor a finite float -- a private dict the coordinator writes and nothing else does. Measured at fba6de8de: the mutant applied to a `git archive` of HEAD and driven under `tests/features.py`'s R10-FEEDS block (the block that pins this line) gives rc=0, and the #2229 arms -- `an interval no price covered books its energy, no cost and no spot sample` and its priced null control -- pass unchanged. The line's OTHER mutant is pinned and not involved: GUARD_OFF (`if False:`) is killed by this same block (the body's M12).",
-  "verdict": "equivalent"
-}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/accuracy.py b/custom_components/heatpump_optimizer/accuracy.py
index ee5c77f96..cef4c9248 100644
--- a/custom_components/heatpump_optimizer/accuracy.py
+++ b/custom_components/heatpump_optimizer/accuracy.py
@@ -871,6 +871,9 @@ class MeasuredCop:
     dhw_temp: float | None = None
     refusal: str | None = None
     at: datetime | None = None
+    #: Intervals a learner freeze refused since start (not persisted): the
+    #: heat-pump grade's no-grade evidence (``coordinator.machine_evidence``).
+    frozen_refusals: int = 0
 
     @staticmethod
     def judge_floor(asked_kw: float, drawn_kw: float, params: Any) -> str | None:
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index b337f865f..d591f32e4 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -216,6 +216,7 @@ from .external_heat import (
 )
 from . import away as away_mode
 from . import boost
+from . import driving_grade
 from . import battery as battery_view
 from . import comfort_band
 from . import draw_range
@@ -3118,17 +3119,44 @@ def envelope_score(
     return grade, None, drivers
 
 
+#: Each grade's reference, where its drivers sum to zero (#2816): the house
+#: at typical for its type and era, the pump at its own COP history, and
+#: driving at buying flat at the day's mean price.
+SCORE_REFERENCE: dict[str, float] = {
+    "envelope": 50.0, "machine": 100.0, "operation": driving_grade.REFERENCE}
+
+
 def machine_score(
     baseline: Mapping[Any, Any], cusum_stat: float
-) -> tuple[float | None, str | None]:
-    """The heat pump grade (#65) and, when it is None, the code saying why.
+) -> tuple[float | None, str | None, list[dict[str, Any]]]:
+    """The heat pump grade (#65), the code saying why it is None, and its drivers.
 
     100 while the COP watch (#12) accumulates no shortfall; the grade falls
     as the Cusum climbs toward its alarm. No watched bucket is no evidence.
+    Its one driver, ``cop_shortfall``, is the grade's distance below 100,
+    the pump matching its own COP history (``SCORE_REFERENCE``).
     """
     if not _watched_cop_buckets(baseline):
-        return None, "cop_watch_learning"
-    return (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0, None
+        return None, "cop_watch_learning", []
+    grade = (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0
+    return grade, None, [{"code": "cop_shortfall", "points": grade - SCORE_REFERENCE["machine"]}]
+
+
+def machine_evidence(baseline: Mapping[Any, Any], frozen_refusals: int) -> dict[str, Any]:
+    """What the heat pump grade waits on: samples per 3 degC outdoor band.
+
+    Each COP baseline bucket against ``COP_BASELINE_MIN_SAMPLES`` (one bucket
+    at it starts the watch, ``_watched_cop_buckets``), most samples first,
+    and the intervals a learner freeze refused since start.
+    """
+    bands = [
+        {"outdoor_c": 3 * band, "hot_water": curve is True, "samples": int(entry[1])}
+        for (band, curve), entry in baseline.items()
+        if np.isfinite(entry[1])
+    ]
+    bands.sort(key=lambda b: (-b["samples"], b["outdoor_c"]))
+    return {"required": COP_BASELINE_MIN_SAMPLES, "bands": bands,
+            "refused_frozen": int(frozen_refusals)}
 
 
 def operation_reason(score_day: Mapping[str, Any]) -> str:
@@ -3139,33 +3167,41 @@ def operation_reason(score_day: Mapping[str, Any]) -> str:
 
 def compose_scores(
     envelope: tuple[float | None, str | None, list[dict[str, Any]]],
-    machine: tuple[float | None, str | None],
-    operation: tuple[float | None, str | None],
+    machine: tuple[float | None, str | None, list[dict[str, Any]]],
+    operation: tuple[float | None, str | None, list[dict[str, Any]]],
+    machine_waits_on: dict[str, Any] | None = None,
 ) -> Scores:
-    """#65: envelope, machine and operation on one 0-100 scale, each a (grade, why).
+    """#65: envelope, machine and operation on one 0-100 scale, each a (grade, why, drivers).
 
     Envelope is the house; it stays in the breakdown. Overall is machine and
     operation only -- averaging the house in is how a DHW-only cheap-hour plan
     reads as 5/100. None is no evidence and is never 0: each None carries one
-    code in ``reasons`` (#2258), and a grade carries none. The house grade's
-    drivers ride ``envelope_drivers`` (#2816).
+    code in ``reasons`` (#2258), and a grade carries none. Each part's
+    drivers ride ``<part>_drivers`` (#2816), signed points summing to the
+    grade minus the part's ``SCORE_REFERENCE``, and are empty with no grade;
+    a heat pump with none says what it waits on in ``machine_evidence``.
     """
-    house = envelope[:2]
-    parts = {"envelope": house, "machine": machine, "operation": operation}
-    reasons = {key: why for key, (_grade, why) in parts.items() if why is not None}
-    available = [g for g, _why in (machine, operation) if g is not None]
+    parts = {"envelope": envelope, "machine": machine, "operation": operation}
+    reasons = {key: part[1] for key, part in parts.items() if part[1] is not None}
+    available = [part[0] for part in (machine, operation) if part[0] is not None]
     if not available:
         reasons["overall"] = "first_scored_day"
-    return {
-        "envelope": None if house[0] is None else round(house[0], 1),
+    def drivers(part: tuple[Any, Any, list[dict[str, Any]]]) -> list[dict[str, Any]]:
+        return [{"code": d["code"], "points": round(d["points"], 1)} for d in part[2]]
+
+    scores: Scores = {
+        "envelope": None if envelope[0] is None else round(envelope[0], 1),
         "machine": None if machine[0] is None else round(machine[0], 1),
         "operation": None if operation[0] is None else round(operation[0], 1),
         "overall": round(float(np.mean(available)), 1) if available else None,
         "reasons": reasons,
-        "envelope_drivers": [
-            {"code": d["code"], "points": round(d["points"], 1)} for d in envelope[2]
-        ],
+        "envelope_drivers": drivers(envelope),
+        "machine_drivers": drivers(machine),
+        "operation_drivers": drivers(operation),
     }
+    if machine[0] is None and machine_waits_on is not None:
+        scores["machine_evidence"] = machine_waits_on
+    return scores
 
 
 def _entity_price_source(config: Mapping[str, Any]) -> bool:
@@ -5094,6 +5130,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             return COP_REFUSED_NO_POWER
         heat_kw = self._flow_bias.heat_output_kw  # read first: an open window moves no measured heat
         if self._learning_frozen(CONF_POWER_ENTITY, CONF_OUTDOOR_TEMP_ENTITY, CONF_THERMAL_POWER_ENTITY, room_air=heat_kw is None and not heat_energy.meter_of(self).counter):
+            self._measured_cop.frozen_refusals += 1  # machine_evidence's tally
             return COP_REFUSED_FROZEN
 
         commanded = self._commanded_power()
@@ -8115,7 +8152,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # operation sample, never the loop.
             try:
                 # A day-less book is the free-day close's #908 streak alone.
-                keys = ("kwh", "sek", "spot_sum", "spot_h") if "day" in day else ()
+                keys = ("kwh", "sek", "spot_sum", "spot_h", *driving_grade.book_keys(day)) if "day" in day else ()
                 numbers = {key: float(day.get(key, 0.0)) for key in (*keys, "free_streak")}
                 cleaned = {"day": str(day["day"]), **numbers} if keys else numbers
                 if admitted("ledger", {"score_day": cleaned}):  # finite, and in its domain
@@ -8125,6 +8162,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         score = stored.get("operation_score")
         if isinstance(score, (int, float)) and np.isfinite(score):
             self._operation_score = float(np.clip(score, 0.0, 100.0))
+        driving_grade.restore(driving_grade.held(self), stored.get("operation_drivers"), lambda drivers: admitted(
+            "ledger", {"operation_drivers": drivers}))
         price_tiles.restore(price_tiles.book(self), stored.get("price_tiles"), lambda name, part: admitted(
             "ledger", {"price_tiles": {name: part}}))
 
@@ -8143,6 +8182,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                     "month_reports": self._month_reports,
                     "score_day": self._score_day,
                     "operation_score": self._operation_score,
+                    "operation_drivers": driving_grade.as_stored(driving_grade.held(self), self._operation_score),
                     "fuse_advisor": dict(self._fuse_advisor),
                     "price_tiles": price_tiles.book(self),
                     "fuse_advisor_at": (
@@ -10375,14 +10415,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             book.update(
                 {"day": day, "kwh": 0.0, "sek": 0.0, "spot_sum": 0.0, "spot_h": 0.0}
             )
-        if spot_known and np.isfinite(sek):  # #2229: an unpriced kWh pays nothing
-            book["kwh"] = finite_float(book.get("kwh"), 0.0) + max(0.0, kwh)
-            book["sek"] = finite_float(book.get("sek"), 0.0) + sek
-        if spot_known and np.isfinite(spot) and elapsed_hours > 0:
-            book["spot_sum"] = (
-                finite_float(book.get("spot_sum"), 0.0) + spot * elapsed_hours
-            )
-            book["spot_h"] = finite_float(book.get("spot_h"), 0.0) + elapsed_hours
+        if spot_known:  # #2229: an unpriced kWh pays nothing
+            self._score_day = driving_grade.tally(book, kwh, sek, spot, elapsed_hours)
 
     def _close_score_day(self) -> None:
         """Replay yesterday against its own realised prices, fold the score.
@@ -10410,12 +10444,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             if streak >= SCORE_FREE_SPAN_RESET:
                 self._operation_score = None
         else:
-            paid_mean = finite_float(book.get("sek"), 0.0) / kwh
-            saved_fraction = 1.0 - paid_mean / mean_spot
-            sample = float(np.clip(saved_fraction / 0.2, 0.0, 1.0)) * 100.0
-            if self._operation_score is not None:
-                sample = (1.0 - SCORE_ALPHA) * self._operation_score + SCORE_ALPHA * sample
-            self._operation_score = sample
+            drivers = driving_grade.held(self)
+            self._operation_score = driving_grade.fold(drivers, self._operation_score, book, mean_spot)
         self._schedule_ledger_save()
 
     def _scores_view(self, advice: Mapping[str, Any]) -> Scores:
@@ -10431,7 +10461,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 getattr(self, "_ctx", self)._config,
             ),
             machine_score(self._cop_baseline, self._cop_health_cusum.stat),
-            (operation, None if operation is not None else operation_reason(self._score_day)),
+            (operation, None if operation is not None else operation_reason(self._score_day),
+             driving_grade.published(driving_grade.held(self), operation)),
+            machine_evidence(self._cop_baseline, self._measured_cop.frozen_refusals),
         )
 
     def _narrative_view(self) -> Narrative:
diff --git a/custom_components/heatpump_optimizer/driving_grade.py b/custom_components/heatpump_optimizer/driving_grade.py
new file mode 100644
index 000000000..ef46e5d1e
--- /dev/null
+++ b/custom_components/heatpump_optimizer/driving_grade.py
@@ -0,0 +1,127 @@
+"""The Driving grade (#65) and the drivers that move it (#2816).
+
+The grade replays each priced day's energy against that day's flat
+time-mean spot price: buying ``FULL_SAVING`` below flat scores 100, at or
+above flat scores 0, folded over days by ``SCORE_ALPHA``. Its drivers split
+the day's saving against the flat replay exactly in two -- the energy bought
+below the day's running mean as it was bought (``tally``), and the rest --
+each weighed against the day's own mean, and fold with the grade's own EMA,
+so they sum to it (``REFERENCE``: flat buying scores 0).
+
+The coordinator owns the day book and the grade; the drivers ride this
+module's per-coordinator side table (``held``), persisted beside the grade.
+Only ``held`` sees the coordinator; the rest take the book or the drivers.
+"""
+
+from __future__ import annotations
+
+from collections.abc import Callable, Mapping
+from typing import Any
+from weakref import WeakKeyDictionary
+
+import numpy as np
+
+from .const import SCORE_ALPHA, finite_float
+
+#: The drivers a day's saving splits into, in display order.
+CODES = ("cheap_hours", "dear_hours")
+#: Buying this fraction below the day's flat price scores 100.
+FULL_SAVING = 0.2
+#: The grade the drivers move from: buying flat at the day's mean price.
+REFERENCE = 0.0
+
+_DRIVERS_BY_OWNER: WeakKeyDictionary[Any, dict[str, float]] = WeakKeyDictionary()
+
+
+def _add(book: dict[str, Any], key: str, value: float) -> None:
+    book[key] = finite_float(book.get(key), 0.0) + value
+
+
+def held(owner: Any) -> dict[str, float]:
+    """``owner``'s drivers, folded with its grade (empty until a day folds)."""
+    return _DRIVERS_BY_OWNER.setdefault(owner, {})
+
+
+def tally(day: Mapping[str, Any], kwh: float, sek: float, spot: float, hours: float) -> dict[str, Any]:
+    """The day book with one priced interval booked in it, as a new book.
+
+    The kWh and the SEK paid for them (SIGNED: a paid negative-price hour
+    lowers the day's mean paid price), the time-weighted spot price, and --
+    for an interval bought below the day's running mean, ``spot_sum /
+    spot_h`` with this interval already in it -- the cheap side's share.
+    """
+    book = dict(day)
+    if np.isfinite(sek):
+        _add(book, "kwh", max(0.0, kwh))
+        _add(book, "sek", sek)
+    if np.isfinite(spot) and hours > 0:
+        _add(book, "spot_sum", spot * hours)
+        _add(book, "spot_h", hours)
+        if np.isfinite(sek) and spot < book["spot_sum"] / book["spot_h"]:
+            _add(book, "kwh_lo", max(0.0, kwh))
+            _add(book, "sek_lo", sek)
+    return book
+
+
+def book_keys(day: Mapping[str, Any]) -> tuple[str, ...]:
+    """The cheap side's day-book keys a stored ``day`` carries (absent: none booked)."""
+    return tuple(key for key in ("kwh_lo", "sek_lo") if key in day)
+
+
+def day_drivers(book: Mapping[str, Any], mean_spot: float, sample: float) -> dict[str, float]:
+    """One priced day's ``sample`` split into its signed drivers, summing to it.
+
+    ``cheap_hours`` pushes the grade up, ``dear_hours`` down; a clipped
+    sample scales both, and one of 0 leaves both at 0.
+    """
+    kwh, sek = finite_float(book.get("kwh"), 0.0), finite_float(book.get("sek"), 0.0)
+    kwh_lo, sek_lo = finite_float(book.get("kwh_lo"), 0.0), finite_float(book.get("sek_lo"), 0.0)
+    saved = {
+        "cheap_hours": mean_spot * kwh_lo - sek_lo,
+        "dear_hours": mean_spot * (kwh - kwh_lo) - (sek - sek_lo),
+    }
+    total = sum(saved.values())
+    scale = sample / total if sample > 0.0 and total > 0.0 else 0.0
+    return {code: value * scale for code, value in saved.items()}
+
+
+def fold(drivers: dict[str, float], grade: float | None, book: Mapping[str, Any], mean_spot: float) -> float:
+    """Fold one priced day into ``grade`` (None seeds it) and ``drivers``; the new grade."""
+    paid_mean = finite_float(book.get("sek"), 0.0) / finite_float(book.get("kwh"), 0.0)
+    saved_fraction = 1.0 - paid_mean / mean_spot
+    sample = float(np.clip(saved_fraction / FULL_SAVING, 0.0, 1.0)) * 100.0
+    day = day_drivers(book, mean_spot, sample)
+    if grade is not None:
+        sample = (1.0 - SCORE_ALPHA) * grade + SCORE_ALPHA * sample
+        day = {
+            code: (1.0 - SCORE_ALPHA) * finite_float(drivers.get(code), 0.0) + SCORE_ALPHA * value
+            for code, value in day.items()
+        }
+    drivers.clear()
+    drivers.update(day)
+    return sample
+
+
+def published(drivers: Mapping[str, float], grade: float | None) -> list[dict[str, Any]]:
+    """The published drivers of ``grade``: none without one.
+
+    What the held drivers do not account for -- a grade folded before they
+    were kept -- is ``earlier_days``, decaying with the EMA.
+    """
+    if grade is None:
+        return []
+    points = {code: finite_float(drivers.get(code), 0.0) for code in CODES}
+    points["earlier_days"] = grade - REFERENCE - sum(points.values())
+    return [{"code": code, "points": value} for code, value in points.items()]
+
+
+def restore(drivers: dict[str, float], stored: Any, admitted: Callable[[Any], bool]) -> None:
+    """Adopt into ``drivers`` what ``as_stored`` wrote, when the store ``admitted`` it."""
+    if isinstance(stored, Mapping) and admitted(stored):
+        drivers.clear()
+        drivers.update({code: float(stored[code]) for code in CODES if code in stored})
+
+
+def as_stored(drivers: Mapping[str, float], grade: float | None) -> dict[str, float]:
+    """The drivers to persist beside ``grade``: none without one."""
+    return dict(drivers) if grade is not None else {}
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index aba9b11ad..e2af2eb88 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -277,9 +277,14 @@ class Scores(TypedDict, total=False):
     envelope: float | None
     #: One code per score that is None, and only for those (#2258).
     reasons: dict[str, str]
-    #: What moves the house grade off 50: ``code`` and signed ``points``,
-    #: summing to ``envelope - 50`` (#2816).
+    #: What moves each grade off its ``coordinator.SCORE_REFERENCE``: ``code``
+    #: and signed ``points`` summing to the grade minus it (#2816); empty with
+    #: no grade.
     envelope_drivers: list[dict[str, Any]]
+    machine_drivers: list[dict[str, Any]]
+    operation_drivers: list[dict[str, Any]]
+    #: What an ungraded heat pump waits on (``coordinator.machine_evidence``).
+    machine_evidence: dict[str, Any]
 
 
 class CompressorStarts(TypedDict, total=False):
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 835b23ba4..7e87dec28 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -438,6 +438,9 @@ DOMAINS: dict[str, dict[str, Domain | str]] = {
         "score_day/day": _DAY, "score_day/kwh": _R, "score_day/sek": _R,
         "score_day/spot_sum": _R, "score_day/spot_h": _Z, "score_day/free_streak": _Z,
         "operation_score": Domain("real", 0.0, 100.0, null=True),
+        "score_day/kwh_lo": _R, "score_day/sek_lo": _R,
+        "operation_drivers/~": Domain("choice", choices=("cheap_hours", "dear_hours")),
+        "operation_drivers/*": _R,
         "fuse_advisor/month": _MONTH, "fuse_advisor/current_fuse_a": Domain("real", _POS),
         "fuse_advisor/candidate_fuse_a": Domain("real", _POS),
         "fuse_advisor/candidate_kw": Domain("real", _POS), "fuse_advisor/feasible": _FLAG,
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 8f094f78a..dedcb151e 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -843,13 +843,16 @@ const STRINGS = {
       "era. 50 is typical for that type and era; above is tighter, below " +
       "leakier. Never 0 — that is only for no data.",
     "score.part_machine":
-      "Machine: the heat pump's observed efficiency against its own " +
-      "baseline. Low points at the pump drawing more electricity than its " +
-      "history says it should — see the COP health diagnostics.",
+      "Heat pump: the measured COP — heat delivered per kWh of electricity " +
+      "— in each 3 °C outdoor band, against the pump's own history in that " +
+      "band. 100 is matching its history; each point below is a lasting " +
+      "COP shortfall (see the COP health diagnostics). A band is watched " +
+      "once it holds 20 samples; no grade yet means no band does — not a zero.",
     "score.part_operation":
-      "Driving: whether the plan buys at the cheap hours. Yesterday's " +
-      "energy replayed against the day's flat average price — buying 20% " +
-      "below flat scores 100, buying at or above flat scores 0.",
+      "Driving: whether the plan buys at the cheap hours. Each day's " +
+      "energy is priced against that day's flat mean spot price — buying " +
+      "20% below flat scores 100, at or above flat scores 0 — and the grade " +
+      "averages recent days. No grade means no priced day scored yet — not a zero.",
     "score.no_evidence": "No evidence yet — not a zero.",
     // Why a score has no grade: one line per code the coordinator
     // publishes in the score sensor's `reasons` (#2258).
@@ -871,6 +874,20 @@ const STRINGS = {
     "score.driver_learned_heat_loss": "learned heat loss vs configured",
     "score.driver_thermal_mass": "thermal-mass correction",
     "score.driver_typical": "typical for its type and era",
+    // The heat-pump and Driving grades' drivers (`machine_drivers`,
+    // `operation_drivers`), and their lines when none moves a point.
+    "score.driver_cop_shortfall": "COP below its own history",
+    "score.driver_cheap_hours": "energy bought below the day's mean price",
+    "score.driver_dear_hours": "energy bought above the day's mean price",
+    "score.driver_earlier_days": "days scored before these drivers were kept",
+    "score.driver_typical_machine": "matches its own COP history",
+    "score.driver_typical_operation": "bought at the day's flat mean price",
+    // What an ungraded heat pump waits on (`machine_evidence`).
+    "score.evidence_bands": "samples per outdoor band, {required} needed: {bands}",
+    "score.evidence_band": "{lo} to {hi} °C {n}",
+    "score.evidence_band_dhw": "{lo} to {hi} °C hot water {n}",
+    "score.evidence_empty": "no COP samples yet",
+    "score.evidence_frozen": "{n} refused while learning was frozen",
     "score.label_machine": "Heat pump",
     "score.label_operation": "Driving",
     // The percent is a template because the spacing is orthographic:
@@ -1651,13 +1668,16 @@ const STRINGS = {
       "byggperioden. 50 är typiskt för den typen och perioden; över är " +
       "tätare, under läckigare. Aldrig 0 — det betyder bara inget underlag.",
     "score.part_machine":
-      "Maskinen: värmepumpens uppmätta effektivitet mot sitt eget " +
-      "baslinjevärde. Lågt pekar på att pumpen drar mer el än sitt eget " +
-      "historik säger — se COP-hälsodiagnostiken.",
+      "Värmepumpen: uppmätt COP — levererad värme per kWh el — i varje " +
+      "utomhusband om 3 °C, mot pumpens egen historik i det bandet. 100 är " +
+      "som historiken; varje poäng under är ett bestående COP-underskott " +
+      "(se COP-hälsodiagnostiken). Ett band bevakas när det har 20 prov; " +
+      "inget betyg ännu betyder att inget band har det — inte noll.",
     "score.part_operation":
-      "Körningen: om planen köper på de billiga timmarna. Gårdagens " +
-      "energi omspelad mot dagens platta medelpris — 20% under platt " +
-      "ger 100, på eller över platt ger 0.",
+      "Körningen: om planen köper på de billiga timmarna. Varje dags " +
+      "energi prissätts mot dagens platta medelspotpris — 20 % under platt " +
+      "ger 100, på eller över platt ger 0 — och betyget är ett medel av de " +
+      "senaste dagarna. Inget betyg betyder att ingen dag med pris bedömts ännu — inte noll.",
     "score.no_evidence": "Inget underlag ännu — inte noll.",
     "score.reason_no_house_model":
       "Ingen husmodell: värmetröghet eller värmeförlust saknas i inställningarna.",
@@ -1674,6 +1694,17 @@ const STRINGS = {
     "score.driver_learned_heat_loss": "inlärd värmeförlust mot inställd",
     "score.driver_thermal_mass": "korrigering för värmetröghet",
     "score.driver_typical": "typiskt för sin typ och period",
+    "score.driver_cop_shortfall": "COP under sin egen historik",
+    "score.driver_cheap_hours": "energi köpt under dagens medelpris",
+    "score.driver_dear_hours": "energi köpt över dagens medelpris",
+    "score.driver_earlier_days": "dagar bedömda innan dessa drivare sparades",
+    "score.driver_typical_machine": "som sin egen COP-historik",
+    "score.driver_typical_operation": "köpt till dagens platta medelpris",
+    "score.evidence_bands": "prov per utomhusband, {required} krävs: {bands}",
+    "score.evidence_band": "{lo} till {hi} °C {n}",
+    "score.evidence_band_dhw": "{lo} till {hi} °C varmvatten {n}",
+    "score.evidence_empty": "inga COP-prov ännu",
+    "score.evidence_frozen": "{n} avvisade medan inlärningen var fryst",
     "score.label_machine": "Värmepumpen",
     "score.label_operation": "Körningen",
     "headline.savings_pct": "({pct} %)",
@@ -7841,6 +7872,11 @@ function valueGrid(axis, plotL, plotR, scaleY, axisName) {
   return out.join("");
 }
 
+// The vertical room a value label's digits need, in em: the chart's sans
+// face sets digits about 0.72 em tall, so 0.8 em clears them by a hair
+// and keeps every label that never touched its neighbour (`valueAxis`).
+const VALUE_LABEL_CLEAR_EM = 0.8;
+
 function valueAxis(
   axis, xBase, plotT, plotB, plotH, side, inset, scaleY, axisName, unit,
   font, titleAnchor
@@ -7850,13 +7886,22 @@ function valueAxis(
   const x = side === "left" ? xBase - inset : xBase + inset;
   const anchor = side === "left" ? "end" : "start";
   const tx = side === "left" ? x - 5 : x + 5;
+  // Labelled as often as the panel's height allows, like `timeAxis`: a
+  // label whose digits would reach the last one drawn is dropped and its
+  // tick mark kept. The tick count is fixed before the panels are sized, so
+  // a short panel -- one squeezed by the wood lane at 375 px -- would
+  // otherwise stack its labels into one another (#2841).
+  let lastLabelY = null;
   for (const tick of axis.ticks) {
     const y = scaleY(tick, axisName);
-    out.push(
-      `<text x="${tx}" y="${y + size / 3}" font-size="${size}" text-anchor="${anchor}" fill="var(--secondary-text-color,#888)">${esc(
-          fmtTick(tick)
-        )}</text>`
-    );
+    if (lastLabelY === null || Math.abs(y - lastLabelY) >= size * VALUE_LABEL_CLEAR_EM) {
+      lastLabelY = y;
+      out.push(
+        `<text x="${tx}" y="${y + size / 3}" font-size="${size}" text-anchor="${anchor}" fill="var(--secondary-text-color,#888)">${esc(
+            fmtTick(tick)
+          )}</text>`
+      );
+    }
     const t1 = side === "left" ? x - 3 : x + 3;
     out.push(
       `<line x1="${x}" y1="${y}" x2="${t1}" y2="${y}" stroke="var(--secondary-text-color,#aaa)" stroke-width="0.75"/>`
@@ -8878,23 +8923,40 @@ function scoreParts(plan) {
     const value = readNumber(attrs[key]);
     return { key, label: L(`score.label_${key}`), value,
       reason: value === null ? scoreReasonText(reasons[key]) : null,
-      drivers: value !== null ? scoreDrivers(key, attrs[`${key}_drivers`]) : "" };
+      drivers: value !== null ? scoreDrivers(key, attrs[`${key}_drivers`])
+        : key === "machine" ? machineEvidence(attrs.machine_evidence) : "" };
   });
 }
 
-/** What moves a sub-score off 50 (#2816): each driver the coordinator
- * published (`envelope_drivers`, `machine_drivers`) with its signed whole
- * points, or "typical" when none moves it a point -- so every shown grade
- * carries at least one reason. A part with no drivers published has none to
- * show; an unknown code is skipped rather than shown raw. */
+/** What moves a sub-score off its reference (#2816): each driver the
+ * coordinator published (`<part>_drivers`) with its signed whole points, or
+ * the part's "typical" line when none moves it a point -- so every shown
+ * grade carries at least one reason. A part with no drivers published has
+ * none to show; an unknown code is skipped rather than shown raw. */
 function scoreDrivers(part, drivers) {
   if (part !== "envelope" && !Array.isArray(drivers)) return "";
   const shown = (Array.isArray(drivers) ? drivers : [])
     .filter((d) => STRINGS.en[`score.driver_${d.code}`] !== undefined)
     .map((d) => ({ code: d.code, pts: Math.round(Number(d.points) || 0) }))
     .filter((d) => d.pts !== 0)
-    .map((d) => `${L(`score.driver_${d.code}`)}${d.pts ? ` ${d.pts > 0 ? "+" : "−"}${Math.abs(d.pts)}` : ""}`);
-  return shown.length ? shown.join("; ") : L("score.driver_typical");
+    .map((d) => `${L(`score.driver_${d.code}`)} ${d.pts > 0 ? "+" : "−"}${Math.abs(d.pts)}`);
+  return shown.length ? shown.join("; ")
+    : L(part === "envelope" ? "score.driver_typical" : `score.driver_typical_${part}`);
+}
+
+/** What an ungraded heat pump waits on (`machine_evidence`): the four
+ * fullest 3 °C outdoor bands' samples against the requirement, and the
+ * intervals a learner freeze refused; nothing when none was published. */
+function machineEvidence(ev) {
+  if (!ev || !Array.isArray(ev.bands)) return "";
+  const bands = ev.bands.slice(0, 4).map((b) => L(
+    b.hot_water ? "score.evidence_band_dhw" : "score.evidence_band",
+    { lo: b.outdoor_c, hi: Number(b.outdoor_c) + 3, n: b.samples }));
+  const parts = [bands.length
+    ? L("score.evidence_bands", { required: ev.required, bands: bands.join(", ") })
+    : L("score.evidence_empty")];
+  if (Number(ev.refused_frozen) > 0) parts.push(L("score.evidence_frozen", { n: ev.refused_frozen }));
+  return parts.join("; ");
 }
 
 /** The words for a score's no-grade code; an unknown code is no evidence. */
@@ -8918,7 +8980,7 @@ function scoreBreakdownHtml(plan) {
           : `<span class="sb-val">${Math.round(p.value)}/100</span>`;
       const bar = p.value === null ? "" : `<span class="sb-bar"><span class="sb-fill" style="width:${Math.max(0, Math.min(100, p.value))}%"></span></span>`;
       return (
-        `<div class="sb-row" data-part="${p.key}">` +
+        `<div class="sb-row" data-part="${p.key}" title="${esc(scoreRowTitle(p))}">` +
         `<div class="sb-head"><span class="sb-name">${esc(p.label)}</span>` +
         `${bar}${value}</div>` +
         (p.drivers ? `<div class="sb-text sb-drivers">${esc(p.drivers)}</div>` : "") +
@@ -8930,6 +8992,18 @@ function scoreBreakdownHtml(plan) {
   return `<div class="score-breakdown">${rows}</div>`;
 }
 
+/** One sub-score's hover: its grade or reason, its drivers or what it
+ * waits on, and its metric in plain words -- the headline's line for it. */
+function scoreRowTitle(p) {
+  return `${scoreLine(p)}\n${L(`score.part_${p.key}`)}`;
+}
+
+/** A sub-score in one line: its name, grade or reason, and its drivers. */
+function scoreLine(p) {
+  const value = p.value === null ? `— ${p.reason}` : `${Math.round(p.value)}/100`;
+  return `${p.label}: ${value}${p.drivers ? ` (${p.drivers})` : ""}`;
+}
+
 /** The currency a savings figure is denominated in: the sensor's own
  * declared unit through `currency()` (R7-D4-03, #1456), so both savings
  * surfaces and the price axis resolve in one chain.
@@ -9016,14 +9090,7 @@ function headlineHtml(plan, cfg, scoreOpen) {
     // -- an owner staring at 5/100 wants to know where the 95 went
     // before deciding anything.
     const parts = scoreParts(plan);
-    const breakdown = parts
-      .map(
-        (p) =>
-          `${p.label}: ${
-              p.value === null ? `— ${p.reason}` : `${Math.round(p.value)}/100`
-            }${p.drivers ? ` (${p.drivers})` : ""}`
-      )
-      .join(" · ");
+    const breakdown = parts.map(scoreLine).join(" · ");
     items.push({
       cls: "score",
       title:
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 271985a54..49403453d 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=84 measured=84",
+  "result": "documented=85 measured=85",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=84, listed=84, missing=[], phantom=[]",
+  "result": "on disk=85, listed=85, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index df30e27e2..7eec4faee 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 24 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (93 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 93 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (101 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 101 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=84 measured=84 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=84, listed=84, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=85 measured=85 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=85, listed=85, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=28 measured=28 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'issues.py', 'legionella.py', 'notifier.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'issues.py', 'legionella.py', 'notifier.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 74549895f..078e749cc 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -89,7 +89,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=84       (83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=85       (84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -115,7 +115,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=84            (83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=85            (84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/programme/delivery/3198.md b/dev/programme/delivery/3198.md
new file mode 100644
index 000000000..c192341d3
--- /dev/null
+++ b/dev/programme/delivery/3198.md
@@ -0,0 +1 @@
+- [#3198](https://github.com/tvofi/heatpump_optimizer/pull/3198) — **open**, R10-GRADE-DRIVERS: grade drivers (R10-GRADE-DRIVERS)
diff --git a/docs/architecture.md b/docs/architecture.md
index 347cba965..6961b1c08 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 84 modules, of which 28 import the
+knows nothing about Home Assistant: 85 modules, of which 28 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -133,6 +133,7 @@ custom_components/heatpump_optimizer/
 │   # Prices, tariffs and money
 ├── price_model.py        # Learned diurnal price shape for the unpublished tail
 ├── price_tiles.py        # The what-if price tiles: a degree held, over 30 days
+├── driving_grade.py      # The Driving grade's daily fold and the drivers that move it
 ├── tariff.py             # Monthly capacity (effekt) tariff and peak tracking
 ├── grid_fee.py           # Time-of-use DSO transfer fees layered on the spot price
 ├── ledger.py             # Month-keyed ledger of settled energy and money
@@ -250,7 +251,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-28 of the 84 modules import `homeassistant` at module level: `__init__`,
+28 of the 85 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -259,7 +260,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 55 modules are deliberately free of it, so each can be driven
+The other 56 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/tests/card.mjs b/tests/card.mjs
index bd09965b7..addc0046b 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -5694,8 +5694,8 @@ function ctxL(card, key) {
     !clickOpenedDialog);
   check("each row carries its plain-language explanation",
     /corrected for thermal mass/.test(openDump) &&
-    /against its own\s+baseline/.test(openDump) &&
-    /buying at or above flat scores 0/.test(openDump),
+    /against the pump's own history/.test(openDump) &&
+    /at or above flat scores 0/.test(openDump),
     (openDump.match(/score-breakdown[\s\S]{0,900}/) || [""])[0]);
   check("an unmeasured part shows no-evidence, never 0/100",
     /sb-na">— No evidence yet/.test(openDump) && !/sb-na">0\/100/.test(openDump));
@@ -5794,6 +5794,74 @@ function ctxL(card, key) {
     /House: 50\/100 \(typical for its type and era\)/.test(typicalHouse.title || ""),
     typicalHouse.title);
 
+  // R10-GRADE-DRIVERS: the heat-pump and Driving grades carry the house
+  // grade's driver interface, and every score hover -- the headline's and each
+  // breakdown row's -- carries both the metric and its current reasons.
+  const EN = fn("STRINGS.en");
+  const esc0 = fn("esc");
+  const opDrivers = (dear) => [{ code: "cheap_hours", points: 70.4 },
+    { code: "dear_hours", points: dear }, { code: "earlier_days", points: 0.0 }];
+  const rowTitle = (s, key) => ((s.open.match(new RegExp(`data-part="${key}" title="([^"]*)"`)) || [null, ""])[1]);
+  const driving = surfaces(withScore("62", {
+    envelope: null, machine: 75, operation: 61.8, overall: 68,
+    reasons: { envelope: "heat_loss_learning" },
+    machine_drivers: [{ code: "cop_shortfall", points: -25.0 }],
+    operation_drivers: opDrivers(-8.6) }));
+  check("R10-GRADE-DRIVERS: the Driving hover lists each driver with its sign and weight, and the metric",
+    /Driving: 62\/100 \(energy bought below the day's mean price \+70; energy bought above the day's mean price −9\)/.test(driving.title || "")
+    && driving.title.includes(EN["score.part_operation"])
+    && /energy bought above the day's mean price −9/.test(rowTitle(driving, "operation")),
+    driving.title);
+  check("R10-GRADE-DRIVERS: the heat-pump hover names its shortfall against its own history",
+    /Heat pump: 75\/100 \(COP below its own history −25\)/.test(driving.title || "")
+    && driving.title.includes(EN["score.part_machine"]), driving.title);
+  const flipped = surfaces(withScore("62", {
+    envelope: null, machine: 75, operation: 61.8, overall: 68,
+    reasons: { envelope: "heat_loss_learning" },
+    machine_drivers: [{ code: "cop_shortfall", points: -25.0 }],
+    operation_drivers: opDrivers(8.6) }));
+  check("R10-GRADE-DRIVERS perturbation: a driver's flipped sign flips its direction mark",
+    /energy bought above the day's mean price \+9\)/.test(flipped.title || "")
+    && !/energy bought above the day's mean price −9/.test(flipped.title || ""), flipped.title);
+  const flat = surfaces(withScore("40", {
+    envelope: 35.2, machine: null, operation: 0, overall: 0,
+    reasons: { machine: "cop_watch_learning" },
+    envelope_drivers: [{ code: "learned_heat_loss", points: -14.8 }],
+    operation_drivers: [{ code: "cheap_hours", points: 0.0 }, { code: "dear_hours", points: 0.0 },
+      { code: "earlier_days", points: 0.0 }] }));
+  const flatNoOp = surfaces(withScore("40", {
+    envelope: 35.2, machine: null, operation: 0, overall: 0,
+    reasons: { machine: "cop_watch_learning" },
+    envelope_drivers: [{ code: "learned_heat_loss", points: -14.8 }] }));
+  check("R10-GRADE-DRIVERS null control: all-zero Driving drivers show the metric and no reason rows, House unchanged",
+    /Driving: 0\/100 \(bought at the day's flat mean price\)/.test(flat.title || "")
+    && !/energy bought/.test(flat.title || "")
+    && flat.title.includes(EN["score.part_operation"])
+    && rowTitle(flat, "envelope") === rowTitle(flatNoOp, "envelope")
+    && /House: 35\/100 \(learned heat loss vs configured −15\)/.test(flat.title || ""), flat.title);
+  const noDrive = surfaces(withScore("60", {
+    envelope: null, machine: 60, operation: null, overall: 60,
+    reasons: { envelope: "heat_loss_learning", operation: "no_scored_day" },
+    machine_drivers: [{ code: "cop_shortfall", points: -40.0 }] }));
+  check("R10-GRADE-DRIVERS: an ungraded Driving row says why and what no grade means",
+    /Driving: — Waiting for the first scored day\./.test(noDrive.title || "")
+    && /No grade means no priced day scored yet/.test(rowTitle(noDrive, "operation")), noDrive.title);
+  const waiting = surfaces(withScore("60", {
+    envelope: null, machine: null, operation: 60, overall: 60,
+    reasons: { envelope: "heat_loss_learning", machine: "cop_watch_learning" },
+    machine_drivers: [], operation_drivers: opDrivers(-10.4),
+    machine_evidence: { required: 20, refused_frozen: 2, bands: [
+      { outdoor_c: -3, hot_water: false, samples: 12 }, { outdoor_c: 0, hot_water: true, samples: 5 }] } }));
+  check("R10-GRADE-DRIVERS: an ungraded heat pump shows samples per outdoor band against the requirement, and freeze refusals",
+    /Heat pump: — Not enough COP data yet to watch the heat pump\. \(samples per outdoor band, 20 needed: -3 to 0 °C 12, 0 to 3 °C hot water 5; 2 refused while learning was frozen\)/.test(waiting.title || "")
+    && /data-part="machine"[^>]*>[\s\S]*?sb-drivers">samples per outdoor band, 20 needed/.test(waiting.open)
+    && /A band is watched once it holds 20 samples/.test(rowTitle(waiting, "machine")), waiting.title);
+  check("R10-GRADE-DRIVERS: every breakdown row's hover carries its metric and its current reasons",
+    [driving, waiting, noDrive].every((s) => ["envelope", "machine", "operation"].every((k) => {
+      const t = rowTitle(s, k);
+      return t.includes(esc0(EN[`score.part_${k}`])) && /\((?:[^)]+)\)|— /.test(t.split("\n")[0]);
+    })), JSON.stringify([driving, waiting, noDrive].map((s) => ["envelope", "machine", "operation"].map((k) => rowTitle(s, k)))));
+
   // One message everywhere: for every score input -- a grade, or null with
   // each code the coordinator can publish for it -- the headline, the hover
   // and the breakdown say one number or one reason, never both and never a
diff --git a/tests/card_browser.mjs b/tests/card_browser.mjs
index 50c6ef82b..9eade190c 100644
--- a/tests/card_browser.mjs
+++ b/tests/card_browser.mjs
@@ -1182,6 +1182,10 @@ async function p9Grid({ browser, check, plan, cardSrc, log = () => {} }) {
       const tag = `${st.name}/${cell.vp[0]}/${cell.theme}${cell.os ? "-on-" + cell.os : ""}/${cell.lang}`;
       try {
         await page.goto("http://hpo.test/");
+        // Each state starts from empty storage: one context serves the whole
+        // cell, so a choice an earlier state persists (hidden_series's chips)
+        // would otherwise hold for every later one (#2841).
+        await page.evaluate(() => { localStorage.clear(); sessionStorage.clear(); });
         await page.addScriptTag({ content: cardSrc });
         await page.addScriptTag({ content: `(${instrument.toString()})();` });
         await page.evaluate(([themeCss, w, cfg, states2, lang, svc, dark]) => {
diff --git a/tests/closures.json b/tests/closures.json
index ee4efaa73..2ad53fa1c 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -199,6 +199,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -350,6 +351,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -446,6 +448,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -542,6 +545,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -651,6 +655,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -763,6 +768,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -890,6 +896,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -1008,6 +1015,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -1137,6 +1145,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -1431,6 +1440,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -1922,6 +1932,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -2111,6 +2122,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -2256,6 +2268,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -2393,6 +2406,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -2575,6 +2589,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -2737,6 +2752,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -3119,6 +3135,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -3282,6 +3299,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -3379,6 +3397,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -3522,6 +3541,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -3611,6 +3631,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -3730,6 +3751,7 @@
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/driving_grade.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
@@ -4851,7 +4873,7 @@
   },
   "tests/config_flow_steps.py": {
    "rc": 0,
-   "seconds": 17.0
+   "seconds": 37.1
   },
   "tests/debug_collect.py": {
    "rc": 0,
@@ -4915,7 +4937,7 @@
   },
   "tests/manual_plan.py": {
    "rc": 0,
-   "seconds": 19.1
+   "seconds": 19.4
   },
   "tests/md_tables.mjs": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 87c1fc9a5..77385907c 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,7 +37,7 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 102
+records every read, so this lane's recorded closure is the package: all 103
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
 alike (78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
 images, 85 until R9 EG-B5's ``dhw_planner.py``, 86 until R9-EG-B3a's
@@ -46,7 +46,7 @@ images, 85 until R9 EG-B5's ``dhw_planner.py``, 86 until R9-EG-B3a's
 R9-EG-B11's ``entry_config.py``, 91 until R9-UX-9's ``flow_meter.py``, 92
 until the live power clamp's ``draw_range.py``, 93 until the live-fix wave's
 ``early_cutoff.py``, 94 until R10-FAHRENHEIT's ``issues.py``, 95 until
-R10-N-log-flood's ``log_latch.py``, 96 until R10-PUMP-MODEL's ``plan_step.py``, 97 until R10-DIAG-REPLAY's ``replay_doc.py``, 98 until R10-ADVISOR's ``price_tiles.py``, 99 until R10-LEARNER-ETA's ``learner_progress.py``, 100 until R10-HEAT-METER's ``heat_energy.py``, 101 until R10-ADVISOR-WHATIF's ``plan_slots.py``) -- one of the three closures in ``tests/closures.json`` that reach
+R10-N-log-flood's ``log_latch.py``, 96 until R10-PUMP-MODEL's ``plan_step.py``, 97 until R10-DIAG-REPLAY's ``replay_doc.py``, 98 until R10-ADVISOR's ``price_tiles.py``, 99 until R10-LEARNER-ETA's ``learner_progress.py``, 100 until R10-HEAT-METER's ``heat_energy.py``, 101 until R10-ADVISOR-WHATIF's ``plan_slots.py``, 102 until R10-GRADE-DRIVERS's ``driving_grade.py``) -- one of the three closures in ``tests/closures.json`` that reach
 every production file; the second is ``tests/arch_score_head.py``'s
 (R9-EG-A1), which measures today's tree with the architecture score and so
 must read all of it, and the third is ``tests/entities.py``'s (round 9),
@@ -54,8 +54,8 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 134 of the 528 script pairs (33 choose 2) sharing 0.80 or more
-of their production-module closure, all 134 among the 406 pairs whose two
+recording finds 144 of the 528 script pairs (33 choose 2) sharing 0.80 or more
+of their production-module closure, all 144 among the 406 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
@@ -74,7 +74,15 @@ pins (#2819) grew guard_pins.py's closure to coordinator.py and sensor.py,
 adding its 9 pairs at >= 0.80 and moving the count from 122 to 131;
 R10-WOOD-NOTIFY's wood_advisor.py closure gained binary_sensor.py, lifting
 its pairs with finite_boundary.py, structure.py and typing_ruler.py from
-0.798 to 0.81 and the count from 131 to 134).
+0.798 to 0.81 and the count from 131 to 134; R10-GRADE-DRIVERS's
+driving_grade.py re-recorded every closure that imports the coordinator,
+putting block_duty.py and boost_drift_replay.py each with finite_boundary.py
+and structure.py, plan_view.py with both, and card.mjs with features.py at
+the 0.80 floor, and the count from 134 to 141; the bot's closure re-record
+then added driving_grade.py to typing_ruler.py's closure, which had been
+recorded without it, putting block_duty.py, boost_drift_replay.py and
+plan_view.py each with typing_ruler.py at the 0.80 floor, and the count from
+141 to 144).
 Eighteen of the pairs sit at exactly 1.00 -- arch_score_head.py/deployment_shape.py,
 arch_score_head.py/entities.py and deployment_shape.py/entities.py
 (96 shared production files each), doc_claims.py/harness_headers.py
diff --git a/tests/features.py b/tests/features.py
index 59415d86e..b94378101 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -23690,6 +23690,142 @@ R.check(
     },
     f"{_fresh6}",
 )
+
+# --- R10-GRADE-DRIVERS: the heat-pump and Driving grades publish drivers in
+# the house grade's shape (#2816): signed points summing to the grade minus
+# the part's reference, empty with no grade.
+from heatpump_optimizer.coordinator import SCORE_REFERENCE as _gd_ref  # noqa: E402
+from heatpump_optimizer import driving_grade as _gd_mod  # noqa: E402
+R.check(
+    "R10-GRADE-DRIVERS: an ungraded heat pump says what it waits on -- samples "
+    "per outdoor band against the requirement, and freeze refusals -- and no "
+    "part publishes a driver without a grade",
+    _fresh6["machine_drivers"] == [] and _fresh6["operation_drivers"] == []
+    and _fresh6["machine_evidence"] == {"required": 20, "bands": [], "refused_frozen": 0},
+    f"{_fresh6}",
+)
+_gd_m = _t2_coord()
+_gd_m._cop_baseline[(-1, False)] = [3.1, 12]
+_gd_m._cop_baseline[(0, True)] = [2.4, 5]
+_gd_m._measured_power = 1.0
+_gd_m._learning_frozen = lambda *a, **k: True
+_gd_codes = [_gd_m._fold_measured_cop(None), _gd_m._fold_measured_cop(None)]
+del _gd_m._learning_frozen
+_gd_m._measured_power = None
+_gd_codes.append(_gd_m._fold_measured_cop(None))  # refused, but not by a freeze
+_gd_wait = _gd_m._scores_view(_rs_advice(_gd_m))
+R.check(
+    "R10-GRADE-DRIVERS: the heat pump's evidence lists each band's samples, most "
+    "first, and counts only the intervals a freeze refused",
+    _gd_wait["machine"] is None
+    and _gd_wait["machine_evidence"] == {"required": 20, "bands": [
+        {"outdoor_c": -3, "hot_water": False, "samples": 12},
+        {"outdoor_c": 0, "hot_water": True, "samples": 5}], "refused_frozen": 2}
+    and _gd_codes[:2] == ["learners_frozen"] * 2 and _gd_codes[2] != "learners_frozen",
+    f"{_gd_wait} {_gd_codes}",
+)
+_gd_m._cop_baseline[(-1, False)] = [3.1, 20]
+_gd_full = _gd_m._scores_view(_rs_advice(_gd_m))
+_gd_m._cop_health_cusum.stat = 0.2
+_gd_short = _gd_m._scores_view(_rs_advice(_gd_m))
+R.check(
+    "R10-GRADE-DRIVERS: a graded heat pump drops its evidence and carries one "
+    "driver, its distance below its own COP history: none at 100, and a Cusum "
+    "a quarter of the way to its alarm takes 25 points",
+    "machine_evidence" not in _gd_full
+    and _gd_full["machine"] == 100.0
+    and _gd_full["machine_drivers"] == [{"code": "cop_shortfall", "points": 0.0}]
+    and _gd_short["machine"] == 75.0
+    and _gd_short["machine_drivers"] == [{"code": "cop_shortfall", "points": -25.0}]
+    and _gd_ref["machine"] == 100.0,
+    f"{_gd_full['machine_drivers']} / {_gd_short}",
+)
+
+
+def _gd_day(coord, d, spots, kwh_at):
+    for h in range(24):
+        k = kwh_at.get(h, 0.0)
+        coord._fold_score_sample(
+            _jun908 + timedelta(days=d, hours=h), k, k * spots[h], spots[h], 1.0, True
+        )
+
+
+_gd_spots = {h: (0.24 if h in (2, 3, 4) else 0.40 if h == 18 else 0.30) for h in range(24)}
+_gd_o = _t2_coord()
+_gd_day(_gd_o, 0, _gd_spots, {2: 1.0, 3: 1.0, 18: 0.5})
+_gd_o._close_score_day()
+_gd_one = _gd_o._scores_view(_rs_advice(_gd_o))["operation_drivers"]
+_gd_pts = {d["code"]: d["points"] for d in _gd_one}
+for _d in range(1, 6):
+    _gd_day(_gd_o, _d, _gd_spots, {2: 1.0, 3: 1.0, 18: 0.5})
+_gd_o._close_score_day()
+_gd_s6 = _gd_o._scores_view(_rs_advice(_gd_o))
+R.check(
+    "R10-GRADE-DRIVERS: the Driving grade's drivers split it exactly -- energy "
+    "bought under the day's mean pushes it up, energy bought over pulls it "
+    "down -- and keep summing to it through the EMA",
+    _gd_pts["cheap_hours"] > 0 > _gd_pts["dear_hours"]
+    and abs(_gd_pts["earlier_days"]) < 0.05
+    and abs(sum(_gd_pts.values()) - _gd_o._operation_score) < 0.25
+    and abs(sum(d["points"] for d in _gd_s6["operation_drivers"]) - _gd_s6["operation"]) < 0.25
+    and _gd_ref["operation"] == 0.0,
+    f"{_gd_one} / {_gd_s6}",
+)
+_gd_flat = _t2_coord()
+_gd_day(_gd_flat, 0, _gd_spots, {h: 0.2 for h in range(24)})
+_gd_flat._close_score_day()
+_gd_flat_s = _gd_flat._scores_view(_rs_advice(_gd_flat))
+R.check(
+    "R10-GRADE-DRIVERS null control: buying flat through the day scores 0 and "
+    "no driver moves it a point",
+    _gd_flat_s["operation"] == 0.0
+    and all(abs(d["points"]) < 0.05 for d in _gd_flat_s["operation_drivers"]),
+    f"{_gd_flat_s}",
+)
+_gd_r = _t2_coord()
+_gd_saved = {}
+
+
+async def _gd_save(data):
+    _gd_saved.update(data)
+
+
+async def _gd_wait_read():
+    return None
+
+
+_gd_o._ledger_store.async_save = _gd_save
+_gd_o._ledger_store.async_wait_for_read = _gd_wait_read
+_asyncio.run(_gd_o._async_save_ledger())
+
+
+async def _gd_load(_p=_gd_saved):
+    return _p
+
+
+_gd_r._ledger_store.async_load = _gd_load
+_asyncio.run(_gd_r._async_load_ledger())
+_gd_up = _t2_coord()
+
+
+async def _gd_load_old(_p={"ledger": {"months": {}}, "operation_score": 55.0}):
+    return _p
+
+
+_gd_up._ledger_store.async_load = _gd_load_old
+_asyncio.run(_gd_up._async_load_ledger())
+_gd_up_s = _gd_up._scores_view(_rs_advice(_gd_up))
+R.check(
+    "R10-GRADE-DRIVERS: the Driving drivers ride the store across a restart, and "
+    "a grade stored before they were kept reads as earlier days, never as a "
+    "driver it did not measure",
+    _gd_mod.held(_gd_r) == _gd_mod.held(_gd_o) != {}
+    and _gd_r._scores_view(_rs_advice(_gd_r))["operation_drivers"] == _gd_s6["operation_drivers"]
+    and _gd_up_s["operation_drivers"] == [
+        {"code": "cheap_hours", "points": 0.0}, {"code": "dear_hours", "points": 0.0},
+        {"code": "earlier_days", "points": 55.0}],
+    f"{_gd_saved.get('operation_drivers')} / {_gd_up_s['operation_drivers']}",
+)
 _ce._operation_score = None
 _ce._cop_baseline.clear()
 _ce._thermal_params.heat_loss_coefficient = 6.0 * _ce_mid
@@ -77238,4 +77374,86 @@ R.check(
 )
 
 
+# R10-GRADE-DRIVERS: value checks on the boundaries of the driver arithmetic.
+from heatpump_optimizer.const import SCORE_ALPHA as _DG_ALPHA  # noqa: E402
+
+_dg_nan = float("nan")
+_dg_zero_h = _gd_mod.tally({}, 1.0, 5.0, 1.0, 0.0)
+R.check(
+    "R10-GRADE-DRIVERS tally: a zero-hour interval books no spot time",
+    "spot_sum" not in _dg_zero_h and "spot_h" not in _dg_zero_h,
+    f"{_dg_zero_h}",
+)
+_dg_nan_spot = _gd_mod.tally({}, 1.0, 5.0, _dg_nan, 1.0)
+R.check(
+    "R10-GRADE-DRIVERS tally: a non-finite spot books no spot time",
+    "spot_sum" not in _dg_nan_spot and "spot_h" not in _dg_nan_spot,
+    f"{_dg_nan_spot}",
+)
+_dg_first = _gd_mod.tally({}, 1.0, 5.0, 2.0, 1.0)
+R.check(
+    "R10-GRADE-DRIVERS tally: the first interval is at the running mean, not below it",
+    "kwh_lo" not in _dg_first and _dg_first["spot_h"] == 1.0,
+    f"{_dg_first}",
+)
+_dg_empty = _gd_mod.day_drivers({}, 2.0, 50.0)
+R.check(
+    "R10-GRADE-DRIVERS day_drivers: an empty book splits a positive sample into zeros",
+    _dg_empty == {"cheap_hours": 0.0, "dear_hours": 0.0},
+    f"{_dg_empty}",
+)
+_dg_book = {"kwh": 2.0, "sek": 2.0, "kwh_lo": 1.0, "sek_lo": 0.5}
+_dg_neg = _gd_mod.day_drivers(_dg_book, 1.0, -10.0)
+R.check(
+    "R10-GRADE-DRIVERS day_drivers: a negative sample leaves both drivers at 0",
+    _dg_neg == {"cheap_hours": 0.0, "dear_hours": 0.0},
+    f"{_dg_neg}",
+)
+_dg_zero = _gd_mod.day_drivers(_dg_book, 1.0, 0.0)
+R.check(
+    "R10-GRADE-DRIVERS day_drivers: a zero sample leaves both drivers at 0",
+    all(v == 0.0 for v in _dg_zero.values()),
+    f"{_dg_zero}",
+)
+_dg_negzero = _gd_mod.day_drivers(_dg_book, 2.0, -0.0)
+_dg_zero2 = _gd_mod.day_drivers(_dg_book, 2.0, 0.0)
+R.check(
+    "R10-GRADE-DRIVERS day_drivers: a negative-zero sample books the same zeros as a zero one, sign included",
+    {k: repr(v) for k, v in _dg_negzero.items()} == {k: repr(v) for k, v in _dg_zero2.items()}
+    and all(v > 0.0 for v in _gd_mod.day_drivers(_dg_book, 2.0, 5.0).values()),
+    f"{_dg_negzero} vs {_dg_zero2}",
+)
+_dg_neg_total = _gd_mod.day_drivers({"kwh": 1.0, "sek": 2.0}, 1.0, 50.0)
+R.check(
+    "R10-GRADE-DRIVERS day_drivers: a day that saved nothing scales to 0",
+    all(v == 0.0 for v in _dg_neg_total.values()),
+    f"{_dg_neg_total}",
+)
+_dg_d: dict[str, float] = {}
+_dg_seed = _gd_mod.fold(_dg_d, None, _dg_book, 1.0)
+_dg_d2 = dict(_dg_d)
+_dg_next = _gd_mod.fold(_dg_d2, 40.0, _dg_book, 1.0)
+_dg_blend = (1 - _DG_ALPHA) * 40.0 + _DG_ALPHA * _dg_seed
+R.check(
+    "R10-GRADE-DRIVERS fold: None seeds the grade, a held grade blends by SCORE_ALPHA",
+    abs(_dg_next - _dg_blend) < 1e-9
+    and abs(_dg_seed - sum(_dg_d.values())) < 1e-9
+    and abs(sum(_dg_d2.values()) - _DG_ALPHA * _dg_seed) < 1e-9,
+    f"{_dg_seed} {_dg_next} {_dg_d} {_dg_d2}",
+)
+_dg_held: dict[str, float] = {"cheap_hours": 1.0}
+_gd_mod.restore(_dg_held, 5, lambda _s: True)
+_dg_held_b: dict[str, float] = {"cheap_hours": 1.0}
+_gd_mod.restore(_dg_held_b, {"cheap_hours": 9.0}, lambda _s: False)
+_dg_held_c: dict[str, float] = {"cheap_hours": 1.0}
+_gd_mod.restore(_dg_held_c, {"cheap_hours": 9.0}, lambda _s: True)
+R.check(
+    "R10-GRADE-DRIVERS restore: adopts only a mapping the store admitted",
+    _dg_held == {"cheap_hours": 1.0}
+    and _dg_held_b == {"cheap_hours": 1.0}
+    and _dg_held_c == {"cheap_hours": 9.0},
+    f"{_dg_held} {_dg_held_b} {_dg_held_c}",
+)
+
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index ccd8e7877..bde260cf7 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -772,3 +772,4 @@
 # not only the house's when it has drivers (the owner's hover spec, carry 14);
 # it is the state that renders the score with its hover. The other 43 states
 # were rendered and stayed identical.
+score_open  # R10-GRADE-DRIVERS: each breakdown row gains a hover with its grade or reason, its drivers or evidence and its metric; the heat-pump and Driving metric texts are rewritten in plain words
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 26645cda1..caafcfaf6 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -74,6 +74,11 @@ coord_dhw  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else
 coord_grid_fee  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
 coord_minimal  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
 coord_two_zone  # R10-COP-GATE-D: four pump_max_power keys added (null), nothing else moves
+coord_all_features  # R10-GRADE-DRIVERS, additions only: the scores gain machine_drivers and operation_drivers (empty with no grade) and, for the ungraded heat pump, machine_evidence (samples per outdoor band against the requirement, freeze refusals); no value moved
+coord_dhw  # R10-GRADE-DRIVERS, additions only: the scores gain machine_drivers and operation_drivers (empty with no grade) and, for the ungraded heat pump, machine_evidence (samples per outdoor band against the requirement, freeze refusals); no value moved
+coord_grid_fee  # R10-GRADE-DRIVERS, additions only: the scores gain machine_drivers and operation_drivers (empty with no grade) and, for the ungraded heat pump, machine_evidence (samples per outdoor band against the requirement, freeze refusals); no value moved
+coord_minimal  # R10-GRADE-DRIVERS, additions only: the scores gain machine_drivers and operation_drivers (empty with no grade) and, for the ungraded heat pump, machine_evidence (samples per outdoor band against the requirement, freeze refusals); no value moved
+coord_two_zone  # R10-GRADE-DRIVERS, additions only: the scores gain machine_drivers and operation_drivers (empty with no grade) and, for the ungraded heat pump, machine_evidence (samples per outdoor band against the requirement, freeze refusals); no value moved
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index 0b8b10450..0174eb088 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -323,7 +323,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
@@ -2207,7 +2214,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "price_tiles": {},
     "reasons": {
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index 573f6e817..f82b3bcdf 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -323,7 +323,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
@@ -2128,7 +2135,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "price_tiles": {},
     "reasons": {
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index 4ea16f016..71eb46759 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -258,7 +258,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
@@ -1967,7 +1974,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "price_tiles": {},
     "reasons": {
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index 853ee5b02..9246a0920 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -258,7 +258,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
@@ -1967,7 +1974,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "price_tiles": {},
     "reasons": {
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index 6998095e4..d1a0347d0 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -268,7 +268,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "reasons": {
      "envelope": "heat_loss_learning",
@@ -2013,7 +2020,14 @@
     "envelope": null,
     "envelope_drivers": [],
     "machine": null,
+    "machine_drivers": [],
+    "machine_evidence": {
+     "bands": [],
+     "refused_frozen": 0,
+     "required": 20
+    },
     "operation": null,
+    "operation_drivers": [],
     "overall": null,
     "price_tiles": {},
     "reasons": {
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.da4f6087.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.da4f6087.json
new file mode 100644
index 000000000..d4b12c6cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.da4f6087.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop RETURN_DEL da4f6087",
+  "killed_by": "tests/features.py",
+  "old": "            return COP_REFUSED_FROZEN",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.CLAMP_DROP.7a634b7b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.CLAMP_DROP.7a634b7b.json
deleted file mode 100644
index 870199965..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.CLAMP_DROP.7a634b7b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample CLAMP_DROP 7a634b7b",
-  "killed_by": "tests/features.py",
-  "old": "            book[\"kwh\"] = finite_float(book.get(\"kwh\"), 0.0) + max(0.0, kwh)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`book[\"kwh\"] = finite_float(book.get(\"kwh\"), 0.0) + (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.05bb5b4f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.05bb5b4f.json
deleted file mode 100644
index 9765dbd07..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.05bb5b4f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample GUARD_OFF 05bb5b4f",
-  "killed_by": "tests/features.py",
-  "old": "        if spot_known and np.isfinite(sek):  # #2229: an unpriced kWh pays nothing",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: GUARD_OFF (`if False:  # #2229: an unpriced kWh pays nothing`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.16f2087d.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.16f2087d.json
new file mode 100644
index 000000000..18eb346e3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.GUARD_OFF.16f2087d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample GUARD_OFF 16f2087d",
+  "killed_by": "tests/features.py",
+  "old": "        if spot_known:  # #2229: an unpriced kWh pays nothing",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:  # #2229: an unpriced kWh pays nothing`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.BOOLOP.58685ad7.json b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.BOOLOP.58685ad7.json
new file mode 100644
index 000000000..28558f7bd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.BOOLOP.58685ad7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:compose_scores BOOLOP 58685ad7",
+  "killed_by": "tests/features.py",
+  "old": "    if machine[0] is None and machine_waits_on is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if machine[0] is None or machine_waits_on is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.GUARD_OFF.58685ad7.json b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.GUARD_OFF.58685ad7.json
new file mode 100644
index 000000000..300d0767a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.GUARD_OFF.58685ad7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:compose_scores GUARD_OFF 58685ad7",
+  "killed_by": "tests/features.py",
+  "old": "    if machine[0] is None and machine_waits_on is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.RETURN_DEL.e5451d75.json b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.RETURN_DEL.e5451d75.json
new file mode 100644
index 000000000..b6dc9c331
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/compose_scores.RETURN_DEL.e5451d75.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:compose_scores RETURN_DEL e5451d75",
+  "killed_by": "tests/features.py",
+  "old": "    return scores",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.4fe0081d.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.4fe0081d.json
deleted file mode 100644
index d9a50c983..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.4fe0081d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score CLAMP_DROP 4fe0081d",
-  "killed_by": "tests/features.py",
-  "old": "    return (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0, None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 4e38e7d7b3138b24c97e7d0fbea74965c1d43d62: CLAMP_DROP (`return (1.0 - float((cusum_stat / COP_HEALTH_THRESHOLD))) * 100.0, None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.be6c0635.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.be6c0635.json
new file mode 100644
index 000000000..8d6932087
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.CLAMP_DROP.be6c0635.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score CLAMP_DROP be6c0635",
+  "killed_by": "tests/features.py",
+  "old": "    grade = (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`grade = (1.0 - float((cusum_stat / COP_HEALTH_THRESHOLD))) * 100.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.4fe0081d.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.4fe0081d.json
deleted file mode 100644
index ca0985ce8..000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.4fe0081d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score RETURN_DEL 4fe0081d",
-  "killed_by": "tests/features.py",
-  "old": "    return (1.0 - float(np.clip(cusum_stat / COP_HEALTH_THRESHOLD, 0.0, 1.0))) * 100.0, None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 4e38e7d7b3138b24c97e7d0fbea74965c1d43d62: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.e0823a01.json b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.e0823a01.json
new file mode 100644
index 000000000..a53bd4224
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/machine_score.RETURN_DEL.e0823a01.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:machine_score RETURN_DEL e0823a01",
+  "killed_by": "tests/features.py",
+  "old": "    return grade, None, [{\"code\": \"cop_shortfall\", \"points\": grade - SCORE_REFERENCE[\"machine\"]}]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.363c2e9c.json b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.363c2e9c.json
new file mode 100644
index 000000000..bb22683ff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.363c2e9c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:<module> CONST 363c2e9c",
+  "killed_by": "tests/features.py",
+  "old": "REFERENCE = 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`REFERENCE = 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.a755fc85.json b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.a755fc85.json
new file mode 100644
index 000000000..3178a477b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/@module.CONST.a755fc85.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:<module> CONST a755fc85",
+  "killed_by": "tests/features.py",
+  "old": "FULL_SAVING = 0.2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`FULL_SAVING = 0.4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/as_stored.RETURN_DEL.4a99c2f5.json b/tests/mutation_ledger/killed_by/driving_grade.py/as_stored.RETURN_DEL.4a99c2f5.json
new file mode 100644
index 000000000..1a8beb249
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/as_stored.RETURN_DEL.4a99c2f5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:as_stored RETURN_DEL 4a99c2f5",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return dict(drivers) if grade is not None else {}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/book_keys.RETURN_DEL.6a115196.json b/tests/mutation_ledger/killed_by/driving_grade.py/book_keys.RETURN_DEL.6a115196.json
new file mode 100644
index 000000000..02acdf050
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/book_keys.RETURN_DEL.6a115196.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:book_keys RETURN_DEL 6a115196",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return tuple(key for key in (\"kwh_lo\", \"sek_lo\") if key in day)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.BOOLOP.459abf3a.json b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.BOOLOP.459abf3a.json
new file mode 100644
index 000000000..40ab26723
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.BOOLOP.459abf3a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:day_drivers BOOLOP 459abf3a",
+  "killed_by": "tests/features.py",
+  "old": "    scale = sample / total if sample > 0.0 and total > 0.0 else 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`scale = sample / total if sample > 0.0 or total > 0.0 else 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.CMP_BOUND.459abf3a.json b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.CMP_BOUND.459abf3a.json
new file mode 100644
index 000000000..eb07b053e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.CMP_BOUND.459abf3a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:day_drivers CMP_BOUND 459abf3a",
+  "killed_by": "tests/features.py",
+  "old": "    scale = sample / total if sample > 0.0 and total > 0.0 else 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`scale = sample / total if sample >= 0.0 and total > 0.0 else 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.RETURN_DEL.de93dde0.json b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.RETURN_DEL.de93dde0.json
new file mode 100644
index 000000000..24b3bd4bd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/day_drivers.RETURN_DEL.de93dde0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:day_drivers RETURN_DEL de93dde0",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return {code: value * scale for code, value in saved.items()}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/fold.CLAMP_DROP.53f5bf1a.json b/tests/mutation_ledger/killed_by/driving_grade.py/fold.CLAMP_DROP.53f5bf1a.json
new file mode 100644
index 000000000..467283f9d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/fold.CLAMP_DROP.53f5bf1a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:fold CLAMP_DROP 53f5bf1a",
+  "killed_by": "tests/features.py",
+  "old": "    sample = float(np.clip(saved_fraction / FULL_SAVING, 0.0, 1.0)) * 100.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`sample = float((saved_fraction / FULL_SAVING)) * 100.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/fold.GUARD_OFF.40cc2060.json b/tests/mutation_ledger/killed_by/driving_grade.py/fold.GUARD_OFF.40cc2060.json
new file mode 100644
index 000000000..4d94d3efb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/fold.GUARD_OFF.40cc2060.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:fold GUARD_OFF 40cc2060",
+  "killed_by": "tests/features.py",
+  "old": "    if grade is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/fold.RETURN_DEL.c42c3b7a.json b/tests/mutation_ledger/killed_by/driving_grade.py/fold.RETURN_DEL.c42c3b7a.json
new file mode 100644
index 000000000..fd39bd31f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/fold.RETURN_DEL.c42c3b7a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:fold RETURN_DEL c42c3b7a",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return sample",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/held.RETURN_DEL.7522a45a.json b/tests/mutation_ledger/killed_by/driving_grade.py/held.RETURN_DEL.7522a45a.json
new file mode 100644
index 000000000..74eb29a6f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/held.RETURN_DEL.7522a45a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:held RETURN_DEL 7522a45a",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return _DRIVERS_BY_OWNER.setdefault(owner, {})",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/published.GUARD_OFF.bfca7a08.json b/tests/mutation_ledger/killed_by/driving_grade.py/published.GUARD_OFF.bfca7a08.json
new file mode 100644
index 000000000..7d4b617dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/published.GUARD_OFF.bfca7a08.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:published GUARD_OFF bfca7a08",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    if grade is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/published.RETURN_DEL.974e5580.json b/tests/mutation_ledger/killed_by/driving_grade.py/published.RETURN_DEL.974e5580.json
new file mode 100644
index 000000000..9e8cbc8d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/published.RETURN_DEL.974e5580.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:published RETURN_DEL 974e5580",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return [{\"code\": code, \"points\": value} for code, value in points.items()]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/restore.BOOLOP.91eb33c9.json b/tests/mutation_ledger/killed_by/driving_grade.py/restore.BOOLOP.91eb33c9.json
new file mode 100644
index 000000000..04270b578
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/restore.BOOLOP.91eb33c9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:restore BOOLOP 91eb33c9",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(stored, Mapping) and admitted(stored):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(stored, Mapping) or admitted(stored):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/restore.GUARD_OFF.91eb33c9.json b/tests/mutation_ledger/killed_by/driving_grade.py/restore.GUARD_OFF.91eb33c9.json
new file mode 100644
index 000000000..590108102
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/restore.GUARD_OFF.91eb33c9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:restore GUARD_OFF 91eb33c9",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(stored, Mapping) and admitted(stored):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.15ec03d2.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.15ec03d2.json
new file mode 100644
index 000000000..9dd9658a0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.15ec03d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally BOOLOP 15ec03d2",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(spot) and hours > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if np.isfinite(spot) or hours > 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.986a86f9.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.986a86f9.json
new file mode 100644
index 000000000..ede0362a1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.BOOLOP.986a86f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally BOOLOP 986a86f9",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(sek) and spot < book[\"spot_sum\"] / book[\"spot_h\"]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if np.isfinite(sek) or spot < book[\"spot_sum\"] / book[\"spot_h\"]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.3611eb0b.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.3611eb0b.json
new file mode 100644
index 000000000..b4dbefb02
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.3611eb0b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CLAMP_DROP 3611eb0b",
+  "killed_by": "tests/features.py",
+  "old": "        _add(book, \"kwh\", max(0.0, kwh))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`_add(book, \"kwh\", (0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.4e14db88.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.4e14db88.json
new file mode 100644
index 000000000..9a2328e32
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CLAMP_DROP.4e14db88.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CLAMP_DROP 4e14db88",
+  "killed_by": "tests/features.py",
+  "old": "            _add(book, \"kwh_lo\", max(0.0, kwh))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`_add(book, \"kwh_lo\", (0.0))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.15ec03d2.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.15ec03d2.json
new file mode 100644
index 000000000..985d9514f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.15ec03d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CMP_BOUND 15ec03d2",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(spot) and hours > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if np.isfinite(spot) and hours >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.986a86f9.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.986a86f9.json
new file mode 100644
index 000000000..cdead06f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.CMP_BOUND.986a86f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally CMP_BOUND 986a86f9",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(sek) and spot < book[\"spot_sum\"] / book[\"spot_h\"]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if np.isfinite(sek) and spot <= book[\"spot_sum\"] / book[\"spot_h\"]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.15ec03d2.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.15ec03d2.json
new file mode 100644
index 000000000..9211c1489
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.15ec03d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally GUARD_OFF 15ec03d2",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(spot) and hours > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.72ccbc15.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.72ccbc15.json
new file mode 100644
index 000000000..4e46d224d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.72ccbc15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally GUARD_OFF 72ccbc15",
+  "killed_by": "tests/features.py",
+  "old": "    if np.isfinite(sek):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.986a86f9.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.986a86f9.json
new file mode 100644
index 000000000..a43220076
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.GUARD_OFF.986a86f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally GUARD_OFF 986a86f9",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(sek) and spot < book[\"spot_sum\"] / book[\"spot_h\"]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/driving_grade.py/tally.RETURN_DEL.22c4e90c.json b/tests/mutation_ledger/killed_by/driving_grade.py/tally.RETURN_DEL.22c4e90c.json
new file mode 100644
index 000000000..90c8795ab
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/driving_grade.py/tally.RETURN_DEL.22c4e90c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/driving_grade.py:tally RETURN_DEL 22c4e90c",
+  "killed_by": "tests/typing_ruler.py",
+  "old": "    return book",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/typing_ruler.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.BOOLOP.05bb5b4f.json b/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.BOOLOP.05bb5b4f.json
deleted file mode 100644
index f6089b082..000000000
--- a/tests/mutation_ledger/survivor_triage/coordinator.py/HeatPumpOptimizerCoordinator._fold_score_sample.BOOLOP.05bb5b4f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_score_sample BOOLOP 05bb5b4f",
-  "old": "        if spot_known and np.isfinite(sek):  # #2229: an unpriced kWh pays nothing",
-  "reason": "Equivalent (BOOLOP, `and` -> `or`): the two differ only when `spot_known != np.isfinite(sek)`, and `spot_known` is not free -- it is `pending.get(\"spot_price\") is not None`, whose ONLY writer is `_pending_prediction`'s `\"spot_price\": self._current_spot_price()` (coordinator.py:9877), and that getter is `float | None` over values `_known_prices_for` admitted through `_raw_value`, which requires a FINITE float. So on every input the writer can produce: `spot_known` False means `spot` is None, `_as_float(None, nan)` is nan, and `sek = energy * nan` is non-finite, so `and` and `or` are both False; `spot_known` True means `spot` is a finite float, so `sek` is finite and both are True. The mutant is separated only by a `spot_price` that is neither None nor a finite float -- a private dict the coordinator writes and nothing else does. Measured at fba6de8de: the mutant applied to a `git archive` of HEAD and driven under `tests/features.py`'s R10-FEEDS block (the block that pins this line) gives rc=0, and the #2229 arms -- `an interval no price covered books its energy, no cost and no spot sample` and its priced null control -- pass unchanged. The line's OTHER mutant is pinned and not involved: GUARD_OFF (`if False:`) is killed by this same block (the body's M12).",
-  "verdict": "equivalent"
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 98bc6e02c..6bb3700b1 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17618,
+ "class_excess_loc": 17614,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
@@ -11,7 +11,7 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7960,
+ "max_class_loc": 7956,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
