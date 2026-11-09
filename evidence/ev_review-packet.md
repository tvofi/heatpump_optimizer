# Review packet #3360
head: c84a5fb197aa66c174e726eefd9de38051d0ef14
base: 0a8033305d7b03494eb63453e6181a13ffa55c05

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=129036411075 neutral
arch-score / arch-score id=129038014000 queued
arm id=129035973563 skipped
budget-raise-gate / budget-raise-gate id=129038014165 success
cancel-superseded id=129037786934 success
codeql id=129038015194 skipped
codeql / Analyze (actions) id=129036125564 success
codeql / Analyze (javascript-typescript) id=129036125601 success
codeql / Analyze (python) id=129036125597 in_progress
gate id=129036742473 failure
governance id=129038016070 skipped
governance / delivery-status id=129036125604 failure
governance / delivery-status-publish id=129036127386 skipped
governance / env-matrix id=129036125580 success
governance / instrument-self-tests id=129036125643 in_progress
governance / policy-docs id=129036125573 success
governance / record id=129036127459 skipped
governance / wave-script id=129036125632 success
hassfest id=129038016188 skipped
hassfest / hassfest id=129036125492 success
kernel-points id=129038016247 skipped
pr-contract id=129036744238 skipped
prelude id=129037786709 success
refresh id=129037787006 in_progress
tests id=129038015852 skipped
tests / arch-instrument id=129036361527 success
tests / briefs id=129036125539 success
tests / browser id=129036361486 success
tests / closure-scope id=129036125599 success
tests / closures id=129036361576 in_progress
tests / coverage id=129036361597 in_progress
tests / fast (3.14) id=129036361600 in_progress
tests / mutation id=129036125633 in_progress
tests / nightly-ha id=129036363301 skipped
tests / nightly-status id=129036125470 success
tests / replay id=129036361556 in_progress
tests / typing id=129036361609 success
validate id=129038015712 skipped
validate / validate-hacs id=129036125486 success

## Refusals
required-red: required context `gate` concluded failure at c84a5fb197aa66c174e726eefd9de38051d0ef14

## Advisories
none

## carry_audit at the head
NOTE body item 96d5f3b4: dismissed:the export is on no ref, so no seat can re-run the arm
NOTE body item c6e1fe74: dismissed:measured and stated as the brief required, no later stage changes
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py <arm>
             `dev/audit/harnesses/r10_sav_wood_reference.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/fold_ledger.py check
             `tools/audit/fold_ledger.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  unverified git grep -n "savings_sek\|savings_pct" custom_components/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 7 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.CMP_BOUND.cfc26759.json b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.CMP_BOUND.cfc26759.json
new file mode 100644
index 000000000..c1d7c3316
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.CMP_BOUND.cfc26759.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/external_heat.py:ExternalHeatState.heating CMP_BOUND cfc26759",
+  "killed_by": "tests/features.py",
+  "old": "        return self.active or self.fading or self.displacement > 0.0 or self.free_heat_kw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return self.active or self.fading or self.displacement >= 0.0 or self.free_heat_kw > 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.RETURN_DEL.cfc26759.json b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.RETURN_DEL.cfc26759.json
new file mode 100644
index 000000000..03596c64b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.RETURN_DEL.cfc26759.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/external_heat.py:ExternalHeatState.heating RETURN_DEL cfc26759",
+  "killed_by": "tests/features.py",
+  "old": "        return self.active or self.fading or self.displacement > 0.0 or self.free_heat_kw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.cc7ba91e.json b/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.cc7ba91e.json
new file mode 100644
index 000000000..28568c036
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.cc7ba91e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:<module> CONST cc7ba91e",
+  "killed_by": "tests/features.py",
+  "old": "METER_FLOOR = 0.5",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`METER_FLOOR = 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger._prune.CLAMP_DROP.efe7ff98.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger._prune.CLAMP_DROP.efe7ff98.json
new file mode 100644
index 000000000..62f7c7330
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger._prune.CLAMP_DROP.efe7ff98.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger._prune CLAMP_DROP efe7ff98",
+  "killed_by": "tests/features.py",
+  "old": "        for key in sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`for key in sorted(self.months)[: (0)]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.GUARD_OFF.c9f8a17d.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.add_savings_settlement.GUARD_OFF.6cc86672.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.GUARD_OFF.c9f8a17d.json
rename to tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.add_savings_settlement.GUARD_OFF.6cc86672.json
index b69235dd5..3621e8b72 100644
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.GUARD_OFF.c9f8a17d.json
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.add_savings_settlement.GUARD_OFF.6cc86672.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months GUARD_OFF c9f8a17d",
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.add_savings_settlement GUARD_OFF 6cc86672",
   "killed_by": "tests/features.py",
-  "old": "            if wood_configured and calibration is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "            if wood_free:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.line.RETURN_DEL.e3d647a1.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.line.RETURN_DEL.e3d647a1.json
new file mode 100644
index 000000000..55505c6c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.line.RETURN_DEL.e3d647a1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.line RETURN_DEL e3d647a1",
+  "killed_by": "tests/features.py",
+  "old": "        return {\"kwh\": float(entry.get(\"kwh\", 0.0)), \"sek\": float(entry.get(\"sek\", 0.0))}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.66109ecf.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.66109ecf.json
deleted file mode 100644
index 8c7d6c0b1..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.66109ecf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration CMP_BOUND 66109ecf",
-  "killed_by": "tests/features.py",
-  "old": "        if SAVINGS_PLAN_LINE not in lines or plan_kwh < MIN_CALIBRATION_KWH:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: CMP_BOUND (`if SAVINGS_PLAN_LINE not in lines or plan_kwh <= MIN_CALIBRATION_KWH:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.735c54e2.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.735c54e2.json
new file mode 100644
index 000000000..9c6b52a18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.735c54e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration CMP_BOUND 735c54e2",
+  "killed_by": "tests/features.py",
+  "old": "        if plan_kwh < MIN_CALIBRATION_KWH:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if plan_kwh <= MIN_CALIBRATION_KWH:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.66109ecf.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.66109ecf.json
deleted file mode 100644
index e7f146ec2..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.66109ecf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration GUARD_OFF 66109ecf",
-  "killed_by": "tests/features.py",
-  "old": "        if SAVINGS_PLAN_LINE not in lines or plan_kwh < MIN_CALIBRATION_KWH:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.735c54e2.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.735c54e2.json
new file mode 100644
index 000000000..b2c4090fe
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.735c54e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration GUARD_OFF 735c54e2",
+  "killed_by": "tests/features.py",
+  "old": "        if plan_kwh < MIN_CALIBRATION_KWH:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.085ffc24.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.085ffc24.json
new file mode 100644
index 000000000..a61265c9b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.085ffc24.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration RETURN_DEL 085ffc24",
+  "killed_by": "tests/features.py",
+  "old": "        return self.line(month, actual_line)[\"kwh\"] / plan_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.fbe6bc9f.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.fbe6bc9f.json
deleted file mode 100644
index 1ed994e90..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.fbe6bc9f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration RETURN_DEL fbe6bc9f",
-  "killed_by": "tests/features.py",
-  "old": "        return self.line(month, \"savings_actual\")[\"kwh\"] / plan_kwh",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.5a9e8e3d.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.5a9e8e3d.json
new file mode 100644
index 000000000..0759dade8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.5a9e8e3d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months BOOLOP 5a9e8e3d",
+  "killed_by": "tests/features.py",
+  "old": "            below_floor = not old_basis and below_meter_floor(self.line(key, \"savings_baseline\")[\"kwh\"], actual[\"kwh\"])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`below_floor = not old_basis or below_meter_floor(self.line(key, \"savings_baseline\")[\"kwh\"], actual[\"kwh\"])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.c9f8a17d.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.c9f8a17d.json
deleted file mode 100644
index aa74cefdd..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.c9f8a17d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months BOOLOP c9f8a17d",
-  "killed_by": "tests/features.py",
-  "old": "            if wood_configured and calibration is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if wood_configured or calibration is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.CLAMP_DROP.c2367089.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.CLAMP_DROP.c2367089.json
deleted file mode 100644
index fa1c46941..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.CLAMP_DROP.c2367089.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months CLAMP_DROP c2367089",
-  "killed_by": "tests/features.py",
-  "old": "                calibration = max(1.0, calibration)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`calibration = (1.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.CLAMP_DROP.e865fbd0.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.CLAMP_DROP.e865fbd0.json
new file mode 100644
index 000000000..2254d844d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.CLAMP_DROP.e865fbd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration CLAMP_DROP e865fbd0",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1.0, measured), \"wood_floor\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (1.0), \"wood_floor\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.70a72deb.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.70a72deb.json
new file mode 100644
index 000000000..e52c94f8c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.70a72deb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration GUARD_OFF 70a72deb",
+  "killed_by": "tests/features.py",
+  "old": "    if not wood_configured:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.9bb7edf2.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.9bb7edf2.json
new file mode 100644
index 000000000..b17308527
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.9bb7edf2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration GUARD_OFF 9bb7edf2",
+  "killed_by": "tests/features.py",
+  "old": "    if measured is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.e390a09b.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.e390a09b.json
new file mode 100644
index 000000000..e7b5c0cfc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.e390a09b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration GUARD_OFF e390a09b",
+  "killed_by": "tests/features.py",
+  "old": "    if wood_free is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.RETURN_DEL.e865fbd0.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.RETURN_DEL.e865fbd0.json
new file mode 100644
index 000000000..c713a1462
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.RETURN_DEL.e865fbd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration RETURN_DEL e865fbd0",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1.0, measured), \"wood_floor\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.BOOLOP.a9737861.json b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.BOOLOP.a9737861.json
new file mode 100644
index 000000000..be8abe342
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.BOOLOP.a9737861.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:below_meter_floor BOOLOP a9737861",
+  "killed_by": "tests/features.py",
+  "old": "    return metered_kwh >= MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return metered_kwh >= MIN_CALIBRATION_KWH or booked_kwh < METER_FLOOR * metered_kwh`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.CMP_BOUND.a9737861.json b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.CMP_BOUND.a9737861.json
new file mode 100644
index 000000000..185dc0cc6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.CMP_BOUND.a9737861.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:below_meter_floor CMP_BOUND a9737861",
+  "killed_by": "tests/features.py",
+  "old": "    return metered_kwh >= MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return metered_kwh > MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.RETURN_DEL.a9737861.json b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.RETURN_DEL.a9737861.json
new file mode 100644
index 000000000..89f447849
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.RETURN_DEL.a9737861.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:below_meter_floor RETURN_DEL a9737861",
+  "killed_by": "tests/features.py",
+  "old": "    return metered_kwh >= MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/notifier.py/_monthly_receipt.BOOLOP.68515705.json b/tests/mutation_ledger/killed_by/notifier.py/_monthly_receipt.BOOLOP.68515705.json
new file mode 100644
index 000000000..6eaa1c5fe
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/notifier.py/_monthly_receipt.BOOLOP.68515705.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/notifier.py:_monthly_receipt BOOLOP 68515705",
+  "killed_by": "tests/features.py",
+  "old": "        \"saving_below_meter_floor\": bool(saving and saving.get(\"below_meter_floor\")),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`\"saving_below_meter_floor\": bool(saving or saving.get(\"below_meter_floor\")),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}


## Three-dot diff
diff --git a/blueprints/automation/notifications.yaml b/blueprints/automation/notifications.yaml
index f14ac0a66..58f79d70b 100644
--- a/blueprints/automation/notifications.yaml
+++ b/blueprints/automation/notifications.yaml
@@ -124,6 +124,9 @@ action:
                 {%- if data.saving_sek is not none and data.saving_includes_wood %}
                 The saving includes heat from wood. Firewood's cost is not counted.
                 {%- endif %}
+                {%- if data.saving_below_meter_floor %}
+                No saving is stated for a month whose baseline used under half the energy the meter recorded: a baseline that low is a fault, not a saving.
+                {%- endif %}
       - alias: Comfort at risk
         conditions:
           - "{{ trigger.event.event_type == 'heatpump_optimizer_comfort_at_risk' }}"
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index aee0ae2b8..a9724339b 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -10082,10 +10082,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # coarser configured interval starves forever. A stale, frozen or
         # unconfigured (#2508: the 21.0 C default) indoor sensor scores no
         # room: none is a measurement, and an EWMA poisoned persists weeks.
-        interval_h = (
-            ctx._config.optimization_interval
-            / 60.0
-        )
+        interval_h = ctx._config.optimization_interval / 60.0
         actual_now = None if learner_room_unread(ctx._config) else ctx._current_state.room_temperature
         indoor_frozen = self._learning_frozen(CONF_INDOOR_TEMP_ENTITY)
         if actual_now is not None and indoor_frozen is None:
@@ -10193,6 +10190,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # T6 #52: the assumptions this interval starts under, for the
             # diagnosis re-run when it settles.
             "diag": self._capture_diagnosis_inputs(), **{k: self._current_action.get(k) for k in SETTLEMENT_KEYS},
+            # On a wood house, whether wood heats it: the ledger calibrates from those it does not.
+            "wood_heated": self._external_heat.state.heating() if wood_furnace_on(ctx._config) else None,
         }
     def _dhw_probe_temperature(self) -> float | None:
         """The tank's MEASURED temperature, or ``None`` when there is none.
diff --git a/custom_components/heatpump_optimizer/external_heat.py b/custom_components/heatpump_optimizer/external_heat.py
index 0a9e87381..d75deb3e3 100644
--- a/custom_components/heatpump_optimizer/external_heat.py
+++ b/custom_components/heatpump_optimizer/external_heat.py
@@ -144,6 +144,12 @@ class ExternalHeatState:
     #: ``None`` when the tank pair is not sensed.
     wood_energy_kwh: float | None = None
 
+    def heating(self) -> bool:
+        """Whether the external source heats the house now: a fire active or
+        fading, any displacement, or any free heat. The savings settlement
+        calibrates a wood house from the intervals this reads False."""
+        return self.active or self.fading or self.displacement > 0.0 or self.free_heat_kw > 0.0
+
     def as_dict(self) -> ExternalHeat:
         return {
             "active": self.active,
diff --git a/custom_components/heatpump_optimizer/ledger.py b/custom_components/heatpump_optimizer/ledger.py
index a5c7a7bf8..6a206f4ae 100644
--- a/custom_components/heatpump_optimizer/ledger.py
+++ b/custom_components/heatpump_optimizer/ledger.py
@@ -102,6 +102,18 @@ SAVINGS_COMFORT_LINE = "savings_comfort"
 #: the plan's power levels, so the thermostat stays at modelled power.
 MIN_CALIBRATION_KWH = 1.0
 
+#: The plan's and the meter's kWh on the intervals wood did not heat (the
+#: pending snapshot's ``wood_heated`` False), booked on a wood house only: its
+#: month calibrates from this pair, which no fire moves (R10-SAV-METER-FLOOR).
+SAVINGS_WOOD_FREE_LINES = ("savings_plan_wood_free", "savings_actual_wood_free")
+
+#: Booked reference kWh over metered kWh below which a row states no saving.
+#: A thermostat that used under half the pump's metered energy over a month of
+#: the same weather is a collapsed reference, not a saving. The reference holds
+#: no wood term and wood only lowers the meter, so wood cannot trip it. A
+#: low-side check only: a ratio above it validates nothing (triage P387).
+METER_FLOOR = 0.5
+
 #: The lines that are metered energy at the spot price: what every contract
 #: settles on. The resistive lines are spot energy carved out of ``spot``
 #: (#11), one per source (#2729).
@@ -159,6 +171,34 @@ def savings_pct(baseline_sek: float, savings_sek: float) -> float | None:
     return savings_sek / baseline_sek * 100.0
 
 
+def applied_calibration(
+    measured: float | None, wood_free: float | None, wood_configured: bool
+) -> tuple[float | None, str | None]:
+    """A row's applied calibration and its basis, from ``meter_calibration``'s two reads.
+
+    With no wood, the month's meter (``"meter"``). With wood, the intervals wood
+    did not heat (``"wood_free"``), so a model that reads the meter high is
+    corrected down and one that reads it low up. Where those booked under
+    ``MIN_CALIBRATION_KWH`` of plan (``wood_free`` None), the month's meter,
+    only ever raising the thermostat (``"wood_floor"``): a meter under the plan
+    there is what an unforeseen fire looks like, and scaling down by it would
+    cancel wood's heat from the saving.
+    """
+    if measured is None:
+        return None, None
+    if not wood_configured:
+        return measured, "meter"
+    if wood_free is not None:
+        return wood_free, "wood_free"
+    return max(1.0, measured), "wood_floor"
+
+
+def below_meter_floor(booked_kwh: float, metered_kwh: float) -> bool:
+    """Whether a row's booked reference kWh is under ``METER_FLOOR`` of its
+    metered kWh, over at least ``MIN_CALIBRATION_KWH`` metered."""
+    return metered_kwh >= MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh
+
+
 def migrate_ledger_v1(stored: dict[str, Any]) -> dict[str, Any]:
     """A v1 ledger document at v2: every month it booked savings in is on the old basis.
 
@@ -228,8 +268,7 @@ class MonthlyLedger:
         return month
 
     def _prune(self) -> None:
-        extra = sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]
-        for key in extra:
+        for key in sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]:
             del self.months[key]
 
     # -- writing ------------------------------------------------------------
@@ -292,7 +331,8 @@ class MonthlyLedger:
         fee_per_kwh = float(fee) if isinstance(fee, (int, float)) and math.isfinite(fee) else 0.0
         self.add_savings_settlement(
             when, actual_kwh=actual_kwh, spot=spot + fee_per_kwh, dt=dt,
-            planned_kw=pending.get("power"), **{key: pending.get(key) for key in SETTLEMENT_KEYS},
+            planned_kw=pending.get("power"), wood_free=pending.get("wood_heated") is False,
+            **{key: pending.get(key) for key in SETTLEMENT_KEYS},
         )
 
     def add_savings_settlement(
@@ -307,6 +347,7 @@ class MonthlyLedger:
         stored_kw_th: float | None = None,
         comfort_kw: float | None = None,
         steady_cop: float | None = None,
+        wood_free: bool = False,
     ) -> None:
         """Book the savings lines, or none.
 
@@ -317,6 +358,8 @@ class MonthlyLedger:
         month whose savings lines began without it never gains one, which
         would calibrate a share of its thermostat only. The plan step's
         ``stored_kw_th`` (with its ``steady_cop``) and ``comfort_kw`` book theirs.
+        ``wood_free`` (wood did not heat it) also books the ``SAVINGS_WOOD_FREE_LINES`` pair.
+        Every line is priced at the interval's ``spot``.
         """
         if baseline_kw is None or not all(np.isfinite(v) for v in (baseline_kw, actual_kwh, spot, dt)):
             return
@@ -325,24 +368,22 @@ class MonthlyLedger:
         calibrated = SAVINGS_PLAN_LINE in lines or "savings_baseline" not in lines
         if "savings_baseline" not in lines:
             month["meta"].setdefault(REFERENCE_BASIS_META, {"sum": float(REFERENCE_BASIS), "count": 1})
-        base_kwh = float(baseline_kw) * float(dt)
-        self.add(
-            when, "savings_baseline", kwh=base_kwh, sek=base_kwh * float(spot)
-        )
-        self.add(
-            when,
-            "savings_actual",
-            kwh=float(actual_kwh),
-            sek=float(actual_kwh) * float(spot),
-        )
+
+        def book(name: str, kwh: float) -> None:
+            self.add(when, name, kwh=kwh, sek=kwh * float(spot))
+
+        book("savings_baseline", float(baseline_kw) * float(dt))
+        book("savings_actual", float(actual_kwh))
         if calibrated and planned_kw is not None and np.isfinite(planned_kw):
-            plan_kwh = float(planned_kw) * float(dt)
-            self.add(when, SAVINGS_PLAN_LINE, kwh=plan_kwh, sek=plan_kwh * float(spot))
+            book(SAVINGS_PLAN_LINE, plan_kwh := float(planned_kw) * float(dt))
+            if wood_free:
+                book(SAVINGS_WOOD_FREE_LINES[0], plan_kwh)
+                book(SAVINGS_WOOD_FREE_LINES[1], float(actual_kwh))
         if stored_kw_th is not None and steady_cop is not None and np.isfinite(steady_cop):
             self.add(when, SAVINGS_STORED_LINE, kwh=float(stored_kw_th) * float(dt), sek=0.0)
             self.observe_meta_mean(when, STEADY_COP_META, max(float(steady_cop), 1e-3))
         if comfort_kw is not None:
-            self.add(when, SAVINGS_COMFORT_LINE, kwh=comfort_kw * dt, sek=comfort_kw * dt * spot)
+            book(SAVINGS_COMFORT_LINE, comfort_kw * dt)
 
     # -- reading ------------------------------------------------------------
 
@@ -351,10 +392,7 @@ class MonthlyLedger:
         entry = self.months.get(month, {}).get("lines", {}).get(name)
         if not isinstance(entry, dict):
             return {"kwh": 0.0, "sek": 0.0}
-        return {
-            "kwh": float(entry.get("kwh", 0.0)),
-            "sek": float(entry.get("sek", 0.0)),
-        }
+        return {"kwh": float(entry.get("kwh", 0.0)), "sek": float(entry.get("sek", 0.0))}
 
     def meta_mean(self, month: str, name: str) -> float | None:
         entry = self.months.get(month, {}).get("meta", {}).get(name)
@@ -415,19 +453,19 @@ class MonthlyLedger:
             "sek": sum(part["sek"] for part in parts),
         }
 
-    def meter_calibration(self, month: str) -> float | None:
+    def meter_calibration(self, month: str, *, wood_free: bool = False) -> float | None:
         """Metered kWh over the plan's modelled kWh, on the same intervals.
 
         The factor that puts the modelled thermostat at the power levels the
-        pump recorded (owner specification, 2026-10-24). ``None`` where the
-        month has no plan line (booked before it existed) or the plan booked
-        under ``MIN_CALIBRATION_KWH``.
+        pump recorded (owner specification, 2026-10-24); ``wood_free``, on the
+        ``SAVINGS_WOOD_FREE_LINES``. ``None`` where the plan booked under
+        ``MIN_CALIBRATION_KWH``, or nothing (a month older than its line).
         """
-        lines = self.months.get(month, {}).get("lines") or {}
-        plan_kwh = self.line(month, SAVINGS_PLAN_LINE)["kwh"]
-        if SAVINGS_PLAN_LINE not in lines or plan_kwh < MIN_CALIBRATION_KWH:
+        plan_line, actual_line = SAVINGS_WOOD_FREE_LINES if wood_free else (SAVINGS_PLAN_LINE, "savings_actual")
+        plan_kwh = self.line(month, plan_line)["kwh"]  # 0.0 where never booked
+        if plan_kwh < MIN_CALIBRATION_KWH:
             return None
-        return self.line(month, "savings_actual")["kwh"] / plan_kwh
+        return self.line(month, actual_line)["kwh"] / plan_kwh
 
     def savings_months(self, now: datetime, *, wood_configured: bool = False) -> list[SavingsMonth]:
         """Published rows: months that booked savings_baseline, oldest first.
@@ -435,9 +473,8 @@ class MonthlyLedger:
         One basis for every cell: the intervals a plan covered, priced at
         spot plus the per-kWh grid fee on both sides. ``actual_sek`` is the
         metered energy's cost; ``baseline_sek`` is the modelled thermostat's,
-        scaled to the meter by ``meter_calibration``, so its power levels
-        are the pump's recorded ones and a model that under-reads the meter
-        is not booked as a loss; ``savings_sek`` is the one less the other.
+        scaled to the pump's recorded power levels by ``applied_calibration``;
+        ``savings_sek`` is the one less the other.
         At one flat price the saving is the volume difference alone. The
         reference has no wood, so wood's heat counts in the saving and firewood's
         cost nowhere; the plan's stored-heat change settles into ``baseline_sek``
@@ -448,8 +485,8 @@ class MonthlyLedger:
 
         The open month is an estimate: every figure is scaled by
         ``coverage_factor``. A month booked against another reference
-        (``REFERENCE_BASIS_META``) states its two columns and no saving. With
-        wood configured the calibration only raises the thermostat.
+        (``REFERENCE_BASIS_META``) states its two columns and no saving, as does
+        one ``below_meter_floor`` reads.
         """
         open_key = month_key(now)
         rows: list[SavingsMonth] = []
@@ -457,12 +494,8 @@ class MonthlyLedger:
             lines = self.months[key].get("lines") or {}
             if "savings_baseline" not in lines:
                 continue
-            calibration = self.meter_calibration(key)
-            if wood_configured and calibration is not None:
-                # A meter under the plan is what a fire the plan did not foresee
-                # looks like; scaling down by it would cancel wood's heat from
-                # the saving. Only an under-read model is corrected here.
-                calibration = max(1.0, calibration)
+            calibration, calibration_basis = applied_calibration(
+                self.meter_calibration(key), self.meter_calibration(key, wood_free=True), wood_configured)
             scale = 1.0 if calibration is None else calibration
             actual, cop = self.line(key, "savings_actual"), self.meta_mean(key, STEADY_COP_META)
             stored_sek = 0.0 if cop is None or actual["kwh"] <= 0 else scale * (
@@ -478,16 +511,21 @@ class MonthlyLedger:
             baseline_sek, actual_sek = round(baseline_sek, 2), round(actual_sek, 2)
             saved = round(baseline_sek - actual_sek, 2)
             old_basis = self.meta_mean(key, REFERENCE_BASIS_META) != REFERENCE_BASIS
+            # The booked lines, never the calibrated column, which cancels the meter.
+            below_floor = not old_basis and below_meter_floor(self.line(key, "savings_baseline")["kwh"], actual["kwh"])
+            withheld = old_basis or below_floor
             rows.append(
                 {
                     "month": key,
                     "baseline_sek": baseline_sek,
                     "actual_sek": actual_sek,
-                    "savings_sek": None if old_basis else saved,
-                    "savings_pct": None if old_basis else savings_pct(baseline_sek, saved),
+                    "savings_sek": None if withheld else saved,
+                    "savings_pct": None if withheld else savings_pct(baseline_sek, saved),
                     "old_basis": old_basis,
+                    "below_meter_floor": below_floor,
                     "estimated": estimated,
                     "meter_calibration": None if calibration is None else round(calibration, 3),
+                    "calibration_basis": calibration_basis,
                     "stored_heat_sek": round(stored_sek, 2),
                     "comfort_sek": round(comfort_sek, 2),
                 }
diff --git a/custom_components/heatpump_optimizer/notifier.py b/custom_components/heatpump_optimizer/notifier.py
index a8febd212..0c8253838 100644
--- a/custom_components/heatpump_optimizer/notifier.py
+++ b/custom_components/heatpump_optimizer/notifier.py
@@ -55,7 +55,7 @@ EVENT_MANUAL_PLAN_RELEASED = f"{DOMAIN}_manual_plan_released"
 EVENT_DATA: dict[str, tuple[str, ...]] = {
     EVENT_MONTHLY_RECEIPT: (
         "entry_id", "month", "total_sek", "saving_sek", "saving_pct", "currency",
-        "saving_old_basis", "saving_includes_wood",
+        "saving_old_basis", "saving_includes_wood", "saving_below_meter_floor",
     ),
     EVENT_COMFORT_AT_RISK: (
         "entry_id", "predicted_min_c", "at", "floor_c",
@@ -102,6 +102,8 @@ def _monthly_receipt(data: Payload) -> Detected:
         # and not its cost.
         "saving_old_basis": bool(saving and saving.get("old_basis")),
         "saving_includes_wood": saving_includes_wood(data),
+        # The reference booked under the meter floor: no saving, and why.
+        "saving_below_meter_floor": bool(saving and saving.get("below_meter_floor")),
     })}
 
 
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index 77b37e80d..e21c1bc8e 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -273,10 +273,17 @@ class SavingsMonth(TypedDict, total=False):
     savings_pct: float | None
     # Booked against a retired reference: the two columns stand, no saving does.
     old_basis: bool
+    # Booked reference kWh under ``ledger.METER_FLOOR`` of metered kWh: the
+    # reference collapsed, so the two columns stand and no saving does.
+    below_meter_floor: bool
     estimated: bool
     # Metered over modelled kWh on the row's intervals: the factor the
     # thermostat's cost is scaled by; None where it was left at modelled.
     meter_calibration: float | None
+    # Which kWh it came from: "meter" (the month's), "wood_free" (the
+    # intervals wood did not heat) or "wood_floor" (the month's, only
+    # raising the thermostat); None with the calibration.
+    calibration_basis: str | None
     # The plan's stored-heat change over the row, priced at the row's
     # metered kWh price: already inside ``baseline_sek`` (R10-SAV-COMFORT).
     stored_heat_sek: float
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index a64b21026..949d44643 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -328,6 +328,8 @@ const STRINGS = {
     "savings.col_pct": "%",
     "savings.estimated": "estimated",
     "savings.old_basis": "old basis",
+    "savings.below_meter_floor": "no saving stated",
+    "savings.meter_floor_note": "No saving is stated for a month whose baseline used under half the energy the meter recorded: a baseline that low is a fault, not a saving.",
     "savings.wood_note": "The saving includes heat from wood. Firewood's cost is not counted.",
     "savings.empty": "No settled savings months yet.",
     "receipt.closed": "{month} \u00b7 closed",
@@ -1209,6 +1211,8 @@ const STRINGS = {
     "savings.col_pct": "%",
     "savings.estimated": "uppskattat",
     "savings.old_basis": "gammalt underlag",
+    "savings.below_meter_floor": "inget sparande anges",
+    "savings.meter_floor_note": "Inget sparande anges för en månad vars referens använde under hälften av den energi mätaren registrerade: en så låg referens är ett fel, inte ett sparande.",
     "savings.wood_note": "Sparandet inkluderar värme från ved. Vedens kostnad räknas inte.",
     "savings.empty": "Inga avräknade sparandemånader ännu.",
     "receipt.closed": "{month} \u00b7 avslutad",
@@ -10042,7 +10046,9 @@ function receiptHtml(st, rows, cur, wood) {
       }))}</div>${wood
         ? `<div class="receipt-sub receipt-wood-note">${esc(L("savings.wood_note"))}</div>`
         : ""}`
-    : "";
+    : row && row.below_meter_floor
+      ? `<div class="receipt-sub receipt-floor-note">${esc(L("savings.meter_floor_note"))}</div>`
+      : "";
   const covers = basis.map((n) => L(`receipt.line_${n}`).toLowerCase()).join(", ");
   const reasons = Object.entries(r.reasons || {})
     .filter(([, e]) => e && finiteNum(e.sek) && e.sek > 0)
@@ -15045,8 +15051,11 @@ class HeatpumpOptimizerCard extends HTMLElement {
       const old = row.old_basis
         ? ` <span class="savings-est savings-old">${esc(L("savings.old_basis"))}</span>`
         : "";
+      const floor = row.below_meter_floor
+        ? ` <span class="savings-est savings-floor">${esc(L("savings.below_meter_floor"))}</span>`
+        : "";
       return `<tr class="${row.estimated ? "estimated" : ""}">
-        <td>${esc(String(row.month || ""))}${est}${old}</td>
+        <td>${esc(String(row.month || ""))}${est}${old}${floor}</td>
         <td class="num">${money(row.baseline_sek)}</td>
         <td class="num">${money(row.actual_sek)}</td>
         <td class="num">${mag(row.savings_sek)}<span class="sv-val">${money(row.savings_sek)}</span></td>
@@ -15060,6 +15069,10 @@ class HeatpumpOptimizerCard extends HTMLElement {
     const woodNote = wood
       ? `<div class="savings-wood-note" style="margin-top:.6em;font-size:.9em;color:var(--secondary-text-color)">${esc(L("savings.wood_note"))}</div>`
       : "";
+    // R10-SAV-METER-FLOOR: a month withheld under the meter floor says why.
+    const floorNote = rows.some((r) => r && r.below_meter_floor)
+      ? `<div class="savings-floor-note" style="margin-top:.6em;font-size:.9em;color:var(--secondary-text-color)">${esc(L("savings.meter_floor_note"))}</div>`
+      : "";
     return `${top}<table class="savings-table">
       <thead><tr>
         <th>${esc(L("savings.col_month"))}</th>
@@ -15069,7 +15082,7 @@ class HeatpumpOptimizerCard extends HTMLElement {
         <th class="num">${esc(L("savings.col_pct"))}</th>
       </tr></thead>
       <tbody>${rows.map(tr).join("")}</tbody>
-    </table>${woodNote}`;
+    </table>${woodNote}${floorNote}`;
   }
 
   // The sensor advisor page's renderer and wiring live at module level
diff --git a/dev/audit/config/bugclasses.json b/dev/audit/config/bugclasses.json
index a7cd387b6..bbbd32f4a 100644
--- a/dev/audit/config/bugclasses.json
+++ b/dev/audit/config/bugclasses.json
@@ -4676,10 +4676,11 @@
       "parts_missing": [
         "the census's pass at the fix's head",
         "wiring the census as a tests/ script",
-        "the meter band"
+        "the meter floor",
+        "an inflated reference on a wood house has no meter oracle (owner ruling)"
       ],
       "process_state": "(c) step 6 ran and recorded 12/12 SOUND on the fixer's metric and population: the spread of step 0 across room and slab starts reads SOUND on a constant zero, no savings harness names a valve or a wood tank, and #2887's valved arm reads the horizon sum while the ledger books step 0",
-      "countermeasure": "proposed barrier: census of installs and tank states booked through get_current_action (red at v7.0.4, v7.1.1 and main), plus a meter band on the published row; at most 2.1 h/release against 6.8 h/release",
+      "countermeasure": "proposed barrier: census of installs and tank states booked through get_current_action (red at v7.0.4, v7.1.1 and main), plus a meter floor on the published row (R10-SAV-METER-FLOOR: booked reference kWh under METER_FLOOR 0.5 of metered kWh states no saving; its ceiling rejected by the owner's no-wood ruling, triage P387), so the high side has no meter oracle; at most 2.1 h/release against 6.8 h/release",
       "landed": null,
       "in_tree_home": "dev/audit/rca/R10-RCA-SAV-ESTIMATE.md",
       "doc": [
@@ -5313,7 +5314,7 @@
     "total": 6,
     "max_per_round": 6,
     "detector": "PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py census",
-    "detector_idea": "The census of installs and tank states as a tests/ script once the fix lands, plus a meter band on the published row (dev/audit/rca/R10-RCA-SAV-ESTIMATE.md)",
+    "detector_idea": "The census of installs and tank states as a tests/ script once the fix lands, plus a meter floor on the published row (dev/audit/rca/R10-RCA-SAV-ESTIMATE.md)",
     "barrier": null,
     "status": "detector",
     "nearest_existing": "P11",
diff --git a/dev/audit/harnesses/r10_rca_sav_estimate.py b/dev/audit/harnesses/r10_rca_sav_estimate.py
index 497405c7f..3ecc239dd 100644
--- a/dev/audit/harnesses/r10_rca_sav_estimate.py
+++ b/dev/audit/harnesses/r10_rca_sav_estimate.py
@@ -15,7 +15,7 @@ at any tree:
 Arms:
 
   ledger BUNDLE   Ratios only, from a diagnostics export: each month's booked
-                  thermostat kWh over its metered kWh, over the row's band.
+                  thermostat kWh over its metered kWh, against the row's floor.
   attrib BUNDLE   The export's snapshots through `_compute_baseline_power`, with
                   the tanks measured, the wood tank cold, the buffer at the
                   curve, and both: step 0 over the horizon mean.
@@ -39,7 +39,7 @@ from datetime import datetime
 
 import numpy as np
 
-from heatpump_optimizer import mixing_valve
+from heatpump_optimizer import ledger, mixing_valve
 from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig
 from heatpump_optimizer.thermal_model import (
     ThermalModel,
@@ -57,9 +57,9 @@ DT = 0.25
 #: differ only by what the measured tanks do to step 0. Wide, because the
 #: reference's first hours may honestly differ; the defect reads 0.00.
 BAND = (0.5, 1.5)
-#: The month row's band: a thermostat cannot use a third of a metered pump's
-#: energy, nor three times it, on one house over a month of the same weather.
-METER_BAND = (0.5, 2.0)
+#: The month row's floor is production's own rule (``ledger.below_meter_floor``,
+#: R10-SAV-METER-FLOOR). It has no ceiling: wood raises the ratio without limit
+#: (triage P387).
 
 
 def _valved(volume: float, **over) -> dict:
@@ -161,8 +161,9 @@ def arm_ledger(path: str) -> int:
         lines = body["lines"]
         if "savings_baseline" not in lines:
             continue
-        ratio = lines["savings_baseline"]["kwh"] / lines["savings_actual"]["kwh"]
-        verdict = "in band" if METER_BAND[0] <= ratio <= METER_BAND[1] else "OUT OF BAND"
+        booked, metered = lines["savings_baseline"]["kwh"], lines["savings_actual"]["kwh"]
+        ratio = booked / metered
+        verdict = "UNDER THE FLOOR" if ledger.below_meter_floor(booked, metered) else "not under the floor"
         print(f"RESULT ledger {month}: booked thermostat over metered {ratio:.2f} {verdict}")
     for snap in data["debug"]["payload_snapshots"]:
         rows = snap["data"].get("savings_months") or []
diff --git a/dev/audit/harnesses/r10_sav_wood_reference.py b/dev/audit/harnesses/r10_sav_wood_reference.py
index 764134aff..58c0fd183 100644
--- a/dev/audit/harnesses/r10_sav_wood_reference.py
+++ b/dev/audit/harnesses/r10_sav_wood_reference.py
@@ -44,7 +44,20 @@ control loop, a fire's coupling on a real house, or the coordinator's
 per-interval re-plan (the hold is ``REPLAN`` intervals, a wider window for the
 meter to leave the plan than production's one).
 
-    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py [--quick] [--no-settlement] [arm ...]
+R10-SAV-METER-FLOOR. Every wood loop passes the pending snapshot's
+``wood_heated``, so a wood month calibrates from the intervals wood did not
+heat. The harness has no detector: ``_wood_heated`` reads the plant's burn,
+active or within the detector's fading tail (``ExternalHeatConfig.decay_minutes``),
+and ignores its confirmation lag. ``--no-wood-flag`` books no flag, a month
+booked before the pair existed: the null control that must read what the merge
+base reads. ``meter-floor`` (asserted) runs the valve and wood closed loops and
+the wood-plant rows and requires each to publish; zeroes the booked reference
+(withheld) and drops the check (``METER_FLOOR`` 0: published); runs a month
+under ``MIN_CALIBRATION_KWH`` metered (published); and measures a resistive-heavy
+month, an immersion's kWh added to the meter at ``IMMERSION_SHARE`` of the pump's,
+printing booked over metered and whether the row is withheld.
+
+    PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py [--quick] [--no-settlement] [--no-wood-flag] [arm ...]
 """
 from __future__ import annotations
 
@@ -54,6 +67,8 @@ from datetime import datetime, timedelta
 import numpy as np
 
 from profiles import DT, house, prices, solve_inputs, weather
+from heatpump_optimizer import ledger as ledger_mod
+from heatpump_optimizer.external_heat import ExternalHeatConfig
 from heatpump_optimizer.ledger import MonthlyLedger
 from heatpump_optimizer.optimizer import (
     HeatPumpOptimizer, OptimizationConfig, _floor_demand_at_target, _reference_cop,
@@ -70,6 +85,17 @@ DAYS = 1.0 if "--quick" in sys.argv else 2.0
 #: The null control for R10-SAV-COMFORT's stored-heat settlement: book the
 #: baseline and power alone, as before the plan step carried its readings.
 NO_SETTLEMENT = "--no-settlement" in sys.argv
+#: The null control for the wood-free calibration: no ``wood_heated`` booked.
+NO_WOOD_FLAG = "--no-wood-flag" in sys.argv
+#: The detector's fading tail after a burn, hours.
+FADE_H = ExternalHeatConfig().decay_minutes / 60.0
+
+
+def _wood_heated(ext, k: int, wood: bool):
+    """The pending snapshot's ``wood_heated`` at interval k: None with no wood."""
+    if not wood or NO_WOOD_FLAG:
+        return None
+    return bool(np.max(ext[max(0, k - int(round(FADE_H / DT))):k + 1]) > 0.0)
 VALVE_CFG = {
     "mixing_valve_mode": "manual", "mixing_valve_target": 21.0, "buffer_tank_volume": 750.0,
     "buffer_max_temperature": 56.0, "heat_pump_max_power": 4.0,
@@ -93,8 +119,14 @@ def _install(wood: bool, two_zone: bool = True):
     )), model
 
 
-def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", metered=None, foresee: bool = True):
-    """A solve per ``REPLAN`` on a plant equal to the model; the row and the terms."""
+def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", metered=None, foresee: bool = True,
+                zero_reference: bool = False, added_kwh: float = 0.0):
+    """A solve per ``REPLAN`` on a plant equal to the model; the row and the terms.
+
+    ``zero_reference`` books a 0 kW thermostat (the collapsed reference the
+    meter floor exists for); ``added_kwh`` adds that many kWh per interval to
+    the meter and the spot line, the pump's plan unchanged (an immersion).
+    """
     opt, model = _install(wood)
     total, hs = int(DAYS * 24 / DT), int(24 / DT)
     span = total + hs + 4
@@ -142,12 +174,13 @@ def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", me
         plan_heat += power * DT * model.compute_cop(
             float(out[k]), flow_temp=state.buffer_tank_temperature
         )
-        meter = power * DT * (1.0 if metered is None else metered(now))
+        meter = power * DT * (1.0 if metered is None else metered(now)) + added_kwh
         # The production snapshot: the plan step's settlement readings (stored
         # heat, comfort, steady COP), the baseline re-read from THIS state.
         step = {} if NO_SETTLEMENT else dict(_settlement_at(plan, k % REPLAN))
         led.observe_spot_and_settle_savings(
-            now, float(pr[k]), {**step, "baseline_kw": booked, "power": power}, meter, DT
+            now, float(pr[k]), {**step, "baseline_kw": 0.0 if zero_reference else booked, "power": power,
+                                "wood_heated": _wood_heated(ext, k, wood)}, meter, DT
         )
         led.add(now, "spot", kwh=meter, sek=meter * float(pr[k]))
         states.append((state, series))
@@ -157,7 +190,11 @@ def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", me
         )
         rooms.append(state.room_temperature)
     row = led.savings_months(datetime(2026, 2, 1), wood_configured=wood)[0]
+    booked_kwh, metered_kwh = led.line("2026-01", "savings_baseline")["kwh"], led.line("2026-01", "savings_actual")["kwh"]
     print(f"  row: baseline {row['baseline_sek']} actual {row['actual_sek']} saved {row['savings_sek']} pct {row['savings_pct']}")
+    print(f"  floor: booked over metered {booked_kwh / metered_kwh if metered_kwh > 0 else float('nan'):.3f}"
+          f" ({booked_kwh:.2f} / {metered_kwh:.2f} kWh); below_meter_floor {row.get('below_meter_floor')};"
+          f" calibration_basis {row.get('calibration_basis')}")
     print(f"  row: stored_heat_sek {row['stored_heat_sek']} comfort_sek {row['comfort_sek']}"
           f"{' (--no-settlement)' if NO_SETTLEMENT else ''}")
     # The month row's meter calibration, read off: what it does to the percent.
@@ -186,7 +223,7 @@ def closed_loop(wood: bool, burn_kw, wood0, buf0: float, price: str = "flat", me
     print(f"  plan kWh {plan_kwh:.2f} at COP {cop:.3f}; booked reference {ref_kwh:.2f} at COP {cop_ref_mean:.3f}; gap {ref_kwh - plan_kwh:+.2f}; mean room {room:.2f} C against 21.00")
     print(f"  comfort term {comfort:+.2f} kWh_e (the reference's warmer house); stored term {stored:+.2f} kWh_e (the plan's store change)")
     print(f"  residual: reference less comfort, plus stored, {settled:.2f} kWh against plan {plan_kwh:.2f}: {residual:+.2f} %")
-    return row, residual
+    return {**row, "metered_kwh": metered_kwh}, residual
 
 
 INSTALLS = {
@@ -308,10 +345,11 @@ def plant_loop(burn_kw, price: str, respond: bool = True, foresee: bool = False,
         drawn = _pump_response(model, state, power, args, float(ext[k]), target) if respond else power
         booked = float(opt._compute_baseline_power(series, state, DT)[0][0])
         step = {} if NO_SETTLEMENT else dict(_settlement_at(plan, k % REPLAN))
+        heated = _wood_heated(ext, k, True)
         for m, led in leds.items():
             meter = drawn * DT * m
             led.observe_spot_and_settle_savings(
-                now, float(pr[k]), {**step, "baseline_kw": booked, "power": power}, meter, DT
+                now, float(pr[k]), {**step, "baseline_kw": booked, "power": power, "wood_heated": heated}, meter, DT
             )
             led.add(now, "spot", kwh=meter, sek=meter * float(pr[k]))
         plan_kwh += power * DT
@@ -338,6 +376,7 @@ def wood_plant() -> None:
     print(f"  no fire ({price}): plan {base_plan:.2f} kWh, drawn {base_drawn:.2f} kWh")
     for m in METER_OVER_MODEL:
         print(f"    m {m}: pct {base_rows[m]['savings_pct']} calibration {base_rows[m]['meter_calibration']}"
+              f" ({base_rows[m].get('calibration_basis')})"
               f" error {_booking_error_pct(base_rows[m], m):+.2f} %; flat pct {flat_rows[m]['savings_pct']}")
     errs = {m: [] for m in METER_OVER_MODEL}
     for kw in FIRE_KW:
@@ -349,7 +388,8 @@ def wood_plant() -> None:
                 e = _booking_error_pct(rows[m], m) - _booking_error_pct(base_rows[m], m)
                 errs[m].append(e)
                 print(f"  fire {kw:4.1f} kW from {h0:02d}:00 ({fire_kwh:.1f} kWh_th): plan {plan_kwh:.2f} drawn {drawn_kwh:.2f};"
-                      f" m {m}: calibration {rows[m]['meter_calibration']} pct {rows[m]['savings_pct']}"
+                      f" m {m}: calibration {rows[m]['meter_calibration']} ({rows[m].get('calibration_basis')})"
+                      f" pct {rows[m]['savings_pct']}"
                       f" (no fire {base_rows[m]['savings_pct']}); booking error from the heat {e:+.2f} %")
     for m, e in errs.items():
         a = np.asarray(e)
@@ -362,8 +402,54 @@ def wood_plant() -> None:
                       for m in METER_OVER_MODEL))
 
 
+#: The resistive-heavy month: an immersion's kWh per interval, as a share of
+#: the valve-flat plan's mean pump kWh per interval.
+IMMERSION_SHARE = (0.5, 1.0, 1.5, 2.0)
+
+
+def meter_floor() -> bool:
+    """R10-SAV-METER-FLOOR's acceptance; rc 1 on any arm off its expectation."""
+    ok = True
+
+    def expect(name, row, withheld):
+        nonlocal ok
+        got = row.get("below_meter_floor") is True and row["savings_pct"] is None
+        bad = got != withheld
+        ok = ok and not bad
+        print(f"  {name}: {'withheld' if got else 'published'} (expected {'withheld' if withheld else 'published'})"
+              f" pct {row['savings_pct']}{' BAD' if bad else ''}")
+    for name in ("valve-flat", "valve-vary"):
+        expect(name, closed_loop(False, lambda t: 0.0, None, 30.0, "flat" if name == "valve-flat" else "winter_typical")[0], False)
+    for name, run in OWED.items():
+        if name != "wood-plant":
+            expect(name, run()[0], False)
+    for fire in (False, True):
+        burn = (lambda t: 12.0 if 17 <= t.hour < 17 + FIRE_HOURS else 0.0) if fire else (lambda t: 0.0)
+        rows, *_ = plant_loop(burn, "winter_typical")
+        for m, row in rows.items():
+            expect(f"wood-plant {'fire 12 kW 17:00' if fire else 'no fire'} m {m}", row, False)
+    flat_row, _ = closed_loop(False, lambda t: 0.0, None, 30.0, "flat")
+    expect("mutant: booked reference zeroed", closed_loop(False, lambda t: 0.0, None, 30.0, "flat", zero_reference=True)[0], True)
+    floor, ledger_mod.METER_FLOOR = ledger_mod.METER_FLOOR, 0.0
+    try:
+        expect("mutant: booked reference zeroed, check dropped (METER_FLOOR 0)",
+               closed_loop(False, lambda t: 0.0, None, 30.0, "flat", zero_reference=True)[0], False)
+    finally:
+        ledger_mod.METER_FLOOR = floor
+    expect("booked reference zeroed, metered under MIN_CALIBRATION_KWH",
+           closed_loop(False, lambda t: 0.0, None, 30.0, "flat", zero_reference=True,
+                       metered=lambda t: 0.0, added_kwh=0.5 / (DAYS * 24 / DT))[0], False)
+    # Measured, not asserted: the immersion's share at which the floor fires.
+    pump_kwh = flat_row["metered_kwh"]
+    for share in IMMERSION_SHARE:
+        row, _ = closed_loop(False, lambda t: 0.0, None, 30.0, "flat", added_kwh=share * pump_kwh / (DAYS * 24 / DT))
+        print(f"RESULT meter_floor_immersion_share{share}: below_meter_floor {row.get('below_meter_floor')} pct {row['savings_pct']}")
+    return ok
+
+
 ARMS = {
     "first": first_step,
+    "meter-floor": meter_floor,
     "valve-flat": lambda: valve_arm("flat"),
     "valve-vary": lambda: valve_arm("winter_typical"),
 }
@@ -385,7 +471,7 @@ OWED = {
 
 
 def main(argv: list[str]) -> int:
-    names = [a for a in argv if a not in ("--quick", "--no-settlement")] or list(ARMS)
+    names = [a for a in argv if a not in ("--quick", "--no-settlement", "--no-wood-flag")] or list(ARMS)
     failed = []
     for name in names:
         print(name)
diff --git a/dev/audit/rca/R10-RCA-SAV-ESTIMATE.md b/dev/audit/rca/R10-RCA-SAV-ESTIMATE.md
index 9aa37282b..61a5644fd 100644
--- a/dev/audit/rca/R10-RCA-SAV-ESTIMATE.md
+++ b/dev/audit/rca/R10-RCA-SAV-ESTIMATE.md
@@ -24,8 +24,11 @@ named beside them.
 - **Audit class.** Yes: six instances in round 10, so a barrier is owed rather
   than a refusal.
 - **Countermeasure.** A two-part barrier. A census of installs and tank states in
-  CI, shown red on the defect, and a meter band on the published row, which is the
-  only part that reaches installs no fixture has.
+  CI, shown red on the defect, and a meter floor on the published row, which is the
+  only part that reaches installs no fixture has. Its ceiling is rejected (the
+  owner's no-wood ruling, triage `dev/programme/triage/s6-batch122.md#P387`), so
+  the class is not fully barriered: an inflated reference on a wood house has no
+  meter oracle.
 
 ## The cause, reproduced
 
@@ -222,8 +225,9 @@ release, over the eight release intervals v7.0.0 to v7.1.2.
   - 33 of the 757 touch `optimizer`, `thermal_model`, `ledger`, `mixing_valve` or
     `dhw_planner`: about 4 per release, and at 3 gate runs each, 12 PR runs.
   - (95 + 12) x 71 s = 2.1 h. At the CPU figure it is 0.6 h.
-- **cost(countermeasure, meter band): about zero.** One ratio per published row;
-  no CI lane.
+- **cost(countermeasure, meter floor): one fix group.** R10-SAV-METER-FLOOR, a
+  fixer seat and a reviewer seat; at run time one comparison per published row,
+  and no CI lane.
 
 **Verdict: passes**, by a factor of 3.2 contended and about 11 at CPU cost. The
 margin is modest for the census at its contended figure. The solve is the whole
@@ -264,20 +268,27 @@ The census covers enumerated installs only. "A harness's configurations are its
 parameters, not its population" (`fix-review.md`), so it cannot be the whole
 barrier, which is why part 2 exists.
 
-### 2. The meter band (production, proposed): the part that reaches the population
-
-`savings_months` gives each row's booked thermostat kWh over its metered kWh and
-publishes no percentage outside a band, saying why instead. `METER_BAND` is 0.5 to
-2.0, from one month of one install plus #2411's null, so it needs its own review.
-
-- **On the defect:** `ledger` reads 2026-09 at 3.30 and 2026-11 at 0.18, both `OUT
-  OF BAND`, and 2026-10 at 0.72, in band. It fires on the row of the 2026-10-14
-  report and on today's.
-- **Null:** #2411's flat-price loop reads 128.4 / 112.6 = 1.14, in band.
-- **Known limit:** it is coarse. It would not catch October's -23 %, and #2411's
-  pre-fix null at 1.78 is also in band.
-- **Owed:** the passing run on a fixed install's row, which the export cannot give
-  because the booked lines predate the fix.
+### 2. The meter floor (production, R10-SAV-METER-FLOOR): the part that reaches the population
+
+`savings_months` reads each row's booked thermostat kWh over its metered kWh and,
+where that is under `METER_FLOOR` (0.5, `ledger.py`) on a row of the current
+reference basis with at least `MIN_CALIBRATION_KWH` metered, publishes no saving
+and says why (`below_meter_floor`). The ceiling the band first had (2.0) is
+rejected under the owner's no-wood ruling: the reference holds no wood term, so
+wood raises the ratio without limit and a high ratio on a wood house cannot be
+told from wood by the meter. Do not build a ceiling without a measured instance
+above it on an install with no wood (triage P387).
+
+- **On the defect:** `ledger` reads 2026-09 at 3.30, above the floor and so not
+  caught, and 2026-11 under it. The 2026-11 figure (0.18 above) is this seat's
+  reading of the owner's export, which is on no ref; the R10-SAV-METER-FLOOR
+  fixer could not re-run the arm on it, so the figure is unverified, not
+  re-derived.
+- **Null:** the flat-price arm `valve-flat` of
+  `dev/audit/harnesses/r10_sav_wood_reference.py` publishes; its `meter-floor`
+  arm runs every valve and wood arm through the floor and asserts each publishes.
+- **Known limit:** a low-side check only. It would not catch October's -23 %, nor
+  any reference inflated above the meter.
 
 This changes production and what the card shows, so it needs its own fixer. It
 changes no policy. Nothing here asks for a rule change, and the #2411 state being
@@ -288,5 +299,5 @@ changes no policy. Nothing here asks for a rule change, and the #2411 state bein
 - **To the fix (`handoff/r10-hotfix-sav-estimate`):** the second cause (a fix on the
   wood term alone stays at 0, 0, 0, 0 on v7.1.x); valved installs with no wood; the
   already-booked rows; wiring the census.
-- **`notifier.py:90`** sends the row too, so the band must gate it as well as the
-  card and the sensor.
+- **`notifier.py` `_monthly_receipt`** sends the row too, so the floor gates it as
+  well as the card and the sensor: the event carries `saving_below_meter_floor`.
diff --git a/dev/programme/delivery/3360.md b/dev/programme/delivery/3360.md
new file mode 100644
index 000000000..9f8d6b10a
--- /dev/null
+++ b/dev/programme/delivery/3360.md
@@ -0,0 +1 @@
+- [#3360](https://github.com/tvofi/heatpump_optimizer/pull/3360) — **open**, R10-SAV-METER-FLOOR: sav meter floor (R10-SAV-METER-FLOOR)
diff --git a/docs/automations.md b/docs/automations.md
index 58205f5eb..4e3902478 100644
--- a/docs/automations.md
+++ b/docs/automations.md
@@ -143,7 +143,7 @@ temperature and back on successive refreshes, which fires at each crossing.
 
 | Event | Fires when | Data |
 |---|---|---|
-| `heatpump_optimizer_monthly_receipt` | a month has closed and its receipt is published | `entry_id`, `month` (`YYYY-MM`), `total_sek`, `saving_sek` and `saving_pct` (against a plain thermostat with no wood, `null` when the month has no savings row or was booked on an older reference), `currency`, `saving_old_basis` (`true` for that older reference), `saving_includes_wood` (`true` where wood is configured: the saving includes its heat, and firewood's cost is not counted) |
+| `heatpump_optimizer_monthly_receipt` | a month has closed and its receipt is published | `entry_id`, `month` (`YYYY-MM`), `total_sek`, `saving_sek` and `saving_pct` (against a plain thermostat with no wood, `null` when the month has no savings row, was booked on an older reference, or is under the meter floor), `currency`, `saving_old_basis` (`true` for that older reference), `saving_includes_wood` (`true` where wood is configured: the saving includes its heat, and firewood's cost is not counted), `saving_below_meter_floor` (`true` when the month's baseline used under half the energy the meter recorded, so no saving is stated) |
 | `heatpump_optimizer_comfort_at_risk` | the coldest step of the plan is below your minimum temperature | `entry_id`, `predicted_min_c`, `at` (the step's time), `floor_c`, `peak_guard_suppressing` (the peak guard is holding heating back), `cause` (the coldest step's published reason, for example `idle_fuse`, or null when the plan has none) |
 | `heatpump_optimizer_input_stale` | a required input has not updated within its limit; once per input | `entry_id`, `input`, `age_minutes`, `max_age_minutes` |
 | `heatpump_optimizer_plan_stale` | the plan is older than three solve cycles (at least 90 minutes) | `entry_id`, `age_minutes` |
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index 7c5f7f8d3..384300bdc 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -562,7 +562,13 @@ month is an estimate until it closes, and is badged as one; a month with no
 settled rows yet says so in words rather than drawing an empty table. The
 baseline has no wood, so where wood is configured the receipt and the table
 both say the saving includes heat from wood and that firewood's cost is not
-counted.
+counted. On a wood house the baseline is scaled to the meter over the hours
+wood did not heat, and only where too few of those were metered is it scaled
+by the whole month, upwards only. A month whose booked baseline used under
+half the energy the meter recorded (`METER_FLOOR` in `ledger.py`, over at least
+1 kWh metered) keeps its two columns and states no saving, with the reason in
+the table and on the receipt. That is a low-side check, not a validation of
+the figure: a baseline above it can still be wrong.
 
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="img/card/savings-dark.png">
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index 0518284f8..9e9669b05 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -887,16 +887,17 @@ view, up to 95 °C. The savings reference has no wood at all, so wood's heat
 counts in the saving and firewood's cost is not counted; the savings page, the
 Plan Monthly Savings sensor and the notifications blueprint's monthly receipt
 say so where wood is configured. The reference is scaled to the meter, and on a
-wood house that scale only raises it, so a meter that falls under the plan
-during a fire cannot cancel wood's heat. A fire the plan did not foresee moves
+wood house only over the intervals wood did not heat, so a meter that falls
+under the plan during a fire cannot cancel wood's heat; where too few such
+intervals were metered, the whole month's scale applies and only raises it. A fire the plan did not foresee moves
 the meter off the plan only until the next re-plan reads the warmer tank. In a
 simulated house (the `wood-plant` arm of
 `dev/audit/harnesses/r10_sav_wood_reference.py`: 4 to 12 kW, 4-hour fires,
 each plan held an hour, where the integration re-plans every interval), the
 pump drew between 0 and 4.5 % less than its plan.
-Where the model reads the meter low, the reference is booked low by that
-share, so the saving is understated by up to that much. Where the model reads
-the meter high, the reference is not scaled down at all on a wood house. Without the probe, or
+Where the model reads the meter high or low, the wood-free intervals correct
+it either way; only a month that falls back to the whole month's scale keeps a
+model that reads high uncorrected. Without the probe, or
 while it is stale, the wood tank is not a store of its own: the model keeps the
 one buffer tank, and a burn is the bounded free heat described above.
 
diff --git a/tests/card.mjs b/tests/card.mjs
index dbf3c1b1a..4314abae2 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -2848,6 +2848,34 @@ check("the hand-scheduled reason has a label",
     rcpWoodNote(rcpWood("sv-SE")) === "Sparandet inkluderar värme från ved. Vedens kostnad räknas inte." &&
     !/receipt-wood-note/.test(rcpPage),
     `${rcpWoodNote(rcpWood("en"))} | ${rcpWoodNote(rcpWood("sv-SE"))}`);
+  // R10-SAV-METER-FLOOR: a month whose booked reference fell under the meter
+  // floor states no saving; the receipt and the table say why, in en and sv.
+  // The null control is the page above: no row under the floor, no note.
+  const rcpFloor = (lang) => {
+    const st = JSON.parse(JSON.stringify(rcpStates));
+    Object.assign(st["sensor.heat_pump_optimizer_monthly_savings"].attributes.savings_months[0],
+      { savings_sek: null, savings_pct: null, below_meter_floor: true });
+    const c = build(st);
+    c.hass = { states: st, language: lang };
+    c._onCardClick({});
+    c.dialog.page = "savings";
+    c._render();
+    return collect(c.shadowRoot).join("\n");
+  };
+  const rcpFloorNotes = (page) => [
+    (page.match(/receipt-floor-note">([^<]*)/) || [])[1] || "",
+    (page.match(/savings-floor-note"[^>]*>([^<]*)/) || [])[1] || "",
+    (page.match(/savings-floor">([^<]*)/) || [])[1] || "",
+  ];
+  const rcpFloorEn = rcpFloorNotes(rcpFloor("en"));
+  const rcpFloorSv = rcpFloorNotes(rcpFloor("sv-SE"));
+  const floorEn = "No saving is stated for a month whose baseline used under half the energy the meter recorded: a baseline that low is a fault, not a saving.";
+  const floorSv = "Inget sparande anges för en månad vars referens använde under hälften av den energi mätaren registrerade: en så låg referens är ett fel, inte ett sparande.";
+  check("a month under the meter floor states no saving and says why on the receipt and the table (en, sv); none above it",
+    rcpFloorEn[0] === floorEn && rcpFloorEn[1] === floorEn && rcpFloorEn[2] === "no saving stated" &&
+    rcpFloorSv[0] === floorSv && rcpFloorSv[1] === floorSv && rcpFloorSv[2] === "inget sparande anges" &&
+    !/floor-note|savings-floor/.test(rcpPage) && !/Saved 148\.00/.test(rcpFloor("en")),
+    JSON.stringify([rcpFloorEn, rcpFloorSv]));
   check("UX-6: the money goes by reason, largest first",
     /Where the money went/.test(rcpPage) &&
     rcpPage.indexOf("Cheapest hours") < rcpPage.indexOf("Keeping the house at target"));
diff --git a/tests/entities.py b/tests/entities.py
index 8f6fa04eb..ded35f92f 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -12498,6 +12498,24 @@ R.check(
     ) is not None,
     _sav_bp_msg,
 )
+# R10-SAV-METER-FLOOR: the receipt states why a month under the meter floor has
+# no saving, in the card's savings.meter_floor_note words, guarded by the
+# event's own flag; the null leg is a month above the floor, which gets none.
+_sav_bp_floor = re.search(
+    r'"savings\.meter_floor_note": "([^"]+)"',
+    (_sav_bp_root / ROOT / "www/heatpump-optimizer-card.js").read_text(),
+).group(1)
+R.check(
+    "The notifications blueprint's monthly receipt says why a month under the meter floor states no saving, "
+    "in the card's words, and only for that month",
+    "saving_below_meter_floor" in _sav_notifier.EVENT_DATA[_sav_notifier.EVENT_MONTHLY_RECEIPT]
+    and _sav_bp_msg.count(_sav_bp_floor) == 1
+    and re.search(
+        r"\{%-? if data\.saving_below_meter_floor %\}\s*" + re.escape(_sav_bp_floor) + r"\s*\{%-? endif %\}",
+        _sav_bp_msg,
+    ) is not None,
+    _sav_bp_msg,
+)
 
 
 #: The one publisher whose attribute KEYS are data rather than API:
diff --git a/tests/features.py b/tests/features.py
index 7851bf475..3f21f45e9 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -43525,6 +43525,114 @@ R.check(
     and _sb_meter_row(0.5, True)["meter_calibration"] == 1.0,
     repr(_sb_up),
 )
+# R10-SAV-METER-FLOOR carry 1: the floor above also kept a model that reads the
+# meter high from being corrected. A wood house calibrates from the intervals
+# wood did not heat (the pending snapshot's ``wood_heated``), floored only where
+# too few of those were metered.
+def _sb_wood_free_row(free_meter, fire_meter, *, wood=True, flag=True, free_hours=12, price=1.0):
+    led = _SavLedger()
+    for hour in range(24):
+        fire = hour >= free_hours
+        pending = {"baseline_kw": 2.0, "power": 1.0, **({"wood_heated": fire} if flag else {})}
+        led.observe_spot_and_settle_savings(
+            _SavDT(2026, 2, 9, hour, 0), price, pending, fire_meter if fire else free_meter, 1.0
+        )
+    return led.savings_months(_SavDT(2026, 3, 2, 0, 0), wood_configured=wood)[0]
+
+
+_sb_wf = _sb_wood_free_row(0.8, 0.2)
+R.check(
+    "a wood house whose wood-free hours meter 0.8 of the plan publishes that calibration, not the floor's 1.0",
+    _sb_wf["meter_calibration"] == 0.8 and _sb_wf.get("calibration_basis") == "wood_free"
+    and _sb_wf["baseline_sek"] == round(48.0 * 0.8, 2),
+    repr(_sb_wf),
+)
+_sb_wf_low = _sb_wood_free_row(1.5, 0.2)
+R.check(
+    "a wood house's model that reads the meter low on its wood-free hours is still corrected up",
+    _sb_wf_low["meter_calibration"] == 1.5 and _sb_wf_low.get("calibration_basis") == "wood_free",
+    repr(_sb_wf_low),
+)
+# Null (a): at one flat price the saving is volume alone, the calibrated
+# reference's kWh less the metered kWh, priced at 1.0.
+R.check(
+    "at one flat price the wood-free calibrated row's saving is the volume difference alone",
+    _sb_wf["savings_sek"] == round(48.0 * 0.8 - (12 * 0.8 + 12 * 0.2), 2) and _sb_wf["actual_sek"] == 12.0,
+    repr(_sb_wf),
+)
+# Null (b) and the fallback: each row as it read before the pair existed, field by field.
+_sb_fields = ("meter_calibration", "baseline_sek", "actual_sek", "savings_sek", "savings_pct")
+_sb_plain_rows = {f: {k: _sb_meter_row(f, False)[k] for k in _sb_fields} for f in (1.0, 0.5, 0.25)}
+R.check(
+    "a no-wood row is unchanged field by field at a meter of 1.0, 0.5 and 0.25 of the plan, the pair or not",
+    _sb_plain_rows == {f: {"meter_calibration": f, "baseline_sek": 48.0 * f, "actual_sek": 24.0 * f,
+                           "savings_sek": 24.0 * f, "savings_pct": 50.0} for f in (1.0, 0.5, 0.25)}
+    and {k: _sb_wood_free_row(0.8, 0.2, wood=False)[k] for k in _sb_fields}
+    == {k: _sb_wood_free_row(0.8, 0.2, wood=False, flag=False)[k] for k in _sb_fields},
+    repr(_sb_plain_rows),
+)
+_sb_fallback = {k: _sb_wood_free_row(0.8, 0.2, free_hours=0)[k] for k in _sb_fields}
+R.check(
+    "a wood month with too few wood-free kWh, or booked before the pair existed, keeps the floor's row exactly",
+    _sb_fallback == {"meter_calibration": 1.0, "baseline_sek": 48.0, "actual_sek": 4.8,
+                     "savings_sek": 43.2, "savings_pct": 90.0}
+    and {k: _sb_wood_free_row(0.8, 0.2, flag=False)[k] for k in _sb_fields}
+    == {"meter_calibration": 1.0, "baseline_sek": 48.0, "actual_sek": 12.0, "savings_sek": 36.0, "savings_pct": 75.0}
+    and _sb_wood_free_row(0.8, 0.2, free_hours=0).get("calibration_basis") == "wood_floor"
+    and _sb_meter_row(1.0, False).get("calibration_basis") == "meter",
+    repr(_sb_fallback),
+)
+# R10-SAV-METER-FLOOR: a row whose booked reference is under METER_FLOOR of its
+# metered kWh states no saving and says why. The booked lines decide, because
+# the calibrated column cancels the meter.
+from heatpump_optimizer.ledger import METER_FLOOR as _sb_floor
+
+
+def _sb_floor_row(baseline_kw, meter_kwh, *, old=False):
+    led = _SavLedger()
+    for hour in range(24):
+        led.observe_spot_and_settle_savings(
+            _SavDT(2026, 2, 9, hour, 0), 1.0, {"baseline_kw": baseline_kw, "power": 1.0}, meter_kwh, 1.0
+        )
+    if old:
+        led.months["2026-02"]["meta"]["reference_basis"] = {"sum": 0.0, "count": 1}
+    return led.savings_months(_SavDT(2026, 3, 2, 0, 0))[0]
+
+
+_sb_collapsed = _sb_floor_row(0.2, 1.0)
+_sb_at_floor = _sb_floor_row(_sb_floor, 1.0)
+_sb_tiny = _sb_floor_row(0.001, 0.04)
+_sb_old_low = _sb_floor_row(0.2, 1.0, old=True)
+R.check(
+    "a booked reference under the meter floor of its metered kWh states no saving, keeps both columns and says why",
+    _sb_floor == 0.5 and _sb_collapsed.get("below_meter_floor") is True
+    and _sb_collapsed["savings_sek"] is None and _sb_collapsed["savings_pct"] is None
+    and _sb_collapsed["baseline_sek"] == 4.8 and _sb_collapsed["actual_sek"] == 24.0,
+    repr(_sb_collapsed),
+)
+R.check(
+    "the meter floor is strict, skips a month under MIN_CALIBRATION_KWH metered, and leaves an old-basis row as old basis",
+    _sb_at_floor.get("below_meter_floor") is False and _sb_at_floor["savings_sek"] == -12.0
+    and _sb_tiny.get("below_meter_floor") is False and _sb_tiny["savings_sek"] is not None
+    and _sb_old_low.get("below_meter_floor") is False and _sb_old_low["old_basis"] is True,
+    repr((_sb_at_floor, _sb_tiny, _sb_old_low)),
+)
+from heatpump_optimizer.ledger import MIN_CALIBRATION_KWH as _sb_min_cal
+from heatpump_optimizer.ledger import below_meter_floor as _sb_below_floor
+
+R.check(
+    "the meter floor's two bounds: exactly MIN_CALIBRATION_KWH metered is floored, a booked kWh of exactly METER_FLOOR of metered is not",
+    _sb_below_floor(0.25 * _sb_min_cal, _sb_min_cal) is True
+    and _sb_below_floor(_sb_floor * 4.0, 4.0) is False
+    and _sb_below_floor(_sb_floor * 4.0 - 0.25, 4.0) is True,
+    repr((_sb_below_floor(0.25 * _sb_min_cal, _sb_min_cal), _sb_below_floor(_sb_floor * 4.0, 4.0))),
+)
+R.check(
+    "wood cannot trip the meter floor: a meter under the plan raises booked over metered",
+    all(_sb_meter_row(f, True).get("below_meter_floor") is False for f in (1.0, 0.5, 0.25))
+    and _sb_wf.get("below_meter_floor") is False,
+    repr([_sb_meter_row(f, True).get("below_meter_floor") for f in (1.0, 0.5, 0.25)]),
+)
 from heatpump_optimizer.notifier import _monthly_receipt as _sb_receipt
 
 
@@ -43544,6 +43652,14 @@ R.check(
     and _sb_ev_new["saving_includes_wood"] is False,
     repr((_sb_ev_old, _sb_ev_new)),
 )
+_sb_ev_floor = _sb_event({"month": "2026-09", "savings_sek": None, "savings_pct": None, "old_basis": False,
+                          "below_meter_floor": True}, False)
+R.check(
+    "the receipt event says a row under the meter floor states no saving, and an ordinary row says it is not",
+    _sb_ev_floor["saving_sek"] is None and _sb_ev_floor.get("saving_below_meter_floor") is True
+    and _sb_ev_new.get("saving_below_meter_floor") is False,
+    repr(_sb_ev_floor),
+)
 _sb_plain = _sb_first_steps(True, False)[(20.0, None)]
 _sb_wood = _sb_first_steps(True, True)
 _sb_gap = max(abs(v - _sb_plain).max() for v in _sb_wood.values())
@@ -43768,8 +43884,8 @@ _cal_gapless_model = _sav_cal_month(_sav_vary, _sav_therm, _sav_plan, 1.0, with_
 R.check(
     "#2492: an install whose meter reads its model keeps the modelled figures byte-identical",
     _cal_gapless["meter_calibration"] == 1.0
-    and {k: v for k, v in _cal_gapless.items() if k != "meter_calibration"}
-    == {k: v for k, v in _cal_gapless_model.items() if k != "meter_calibration"},
+    and {k: v for k, v in _cal_gapless.items() if k not in ("meter_calibration", "calibration_basis")}
+    == {k: v for k, v in _cal_gapless_model.items() if k not in ("meter_calibration", "calibration_basis")},
     f"{_cal_gapless} / {_cal_gapless_model}",
 )
 # A month whose savings lines began before the plan line existed (an upgrade
@@ -43851,8 +43967,8 @@ R.check(
     "R10-SAV-COMFORT null control: an interval without either reading settles nothing",
     _st_null.savings_months(_SavDT(2026, 2, 10))[0]
     == {"month": "2026-01", "baseline_sek": 4.0, "actual_sek": 3.0, "savings_sek": 1.0,
-        "savings_pct": 25.0, "old_basis": False, "estimated": False, "meter_calibration": None,
-        "stored_heat_sek": 0.0, "comfort_sek": 0.0},
+        "savings_pct": 25.0, "old_basis": False, "below_meter_floor": False, "estimated": False,
+        "meter_calibration": None, "calibration_basis": None, "stored_heat_sek": 0.0, "comfort_sek": 0.0},
     repr(_st_null.savings_months(_SavDT(2026, 2, 10))),
 )
 _st_z = _SavLedger()
@@ -70528,6 +70644,36 @@ R.check(
 )
 
 
+# R10-SAV-METER-FLOOR: the interval's pending snapshot carries whether wood
+# heats it, read from the detector's own predicate, on a wood house only.
+def _cg_wood_flag(wood, **detector):
+    cfg = dict(_L5_CFG, heat_pump_max_power=14.0, heat_pump_min_power=1.0)
+    if wood:
+        cfg["wood_furnace_enabled"] = True
+    coord = _Coord(_FakeHass(dict(_CF_STATES)), _FakeEntry(data=cfg))
+    for key, value in detector.items():
+        setattr(coord._external_heat.state, key, value)
+    coord._current_action = {"power": 1.0, "dhw_power": 0.0}
+    coord._record_accuracy()
+    return coord._pending_prediction.get("wood_heated", "absent")
+
+
+_cg_flags = {
+    "plain, fire": _cg_wood_flag(False, active=True),
+    "wood, quiet": _cg_wood_flag(True),
+    "wood, active": _cg_wood_flag(True, active=True),
+    "wood, fading": _cg_wood_flag(True, fading=True),
+    "wood, displacing": _cg_wood_flag(True, displacement=0.3),
+    "wood, free heat": _cg_wood_flag(True, free_heat_kw=0.5),
+}
+R.check(
+    "the pending snapshot carries wood_heated from the detector on a wood house, and None on a plain one",
+    _cg_flags == {"plain, fire": None, "wood, quiet": False, "wood, active": True, "wood, fading": True,
+                  "wood, displacing": True, "wood, free heat": True},
+    repr(_cg_flags),
+)
+
+
 # The meter read at a cycle closes the interval the PREVIOUS cycle's plan
 # governed; _record_accuracy runs after the solve adopted the next action, so
 # the draw window pairs each reading with the pending prediction's ask, never
diff --git a/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.CMP_BOUND.cfc26759.json b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.CMP_BOUND.cfc26759.json
new file mode 100644
index 000000000..c1d7c3316
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.CMP_BOUND.cfc26759.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/external_heat.py:ExternalHeatState.heating CMP_BOUND cfc26759",
+  "killed_by": "tests/features.py",
+  "old": "        return self.active or self.fading or self.displacement > 0.0 or self.free_heat_kw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return self.active or self.fading or self.displacement >= 0.0 or self.free_heat_kw > 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.RETURN_DEL.cfc26759.json b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.RETURN_DEL.cfc26759.json
new file mode 100644
index 000000000..03596c64b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatState.heating.RETURN_DEL.cfc26759.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/external_heat.py:ExternalHeatState.heating RETURN_DEL cfc26759",
+  "killed_by": "tests/features.py",
+  "old": "        return self.active or self.fading or self.displacement > 0.0 or self.free_heat_kw > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.cc7ba91e.json b/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.cc7ba91e.json
new file mode 100644
index 000000000..28568c036
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.cc7ba91e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:<module> CONST cc7ba91e",
+  "killed_by": "tests/features.py",
+  "old": "METER_FLOOR = 0.5",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`METER_FLOOR = 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger._prune.CLAMP_DROP.efe7ff98.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger._prune.CLAMP_DROP.efe7ff98.json
new file mode 100644
index 000000000..62f7c7330
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger._prune.CLAMP_DROP.efe7ff98.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger._prune CLAMP_DROP efe7ff98",
+  "killed_by": "tests/features.py",
+  "old": "        for key in sorted(self.months)[: max(0, len(self.months) - KEEP_MONTHS)]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`for key in sorted(self.months)[: (0)]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.GUARD_OFF.c9f8a17d.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.add_savings_settlement.GUARD_OFF.6cc86672.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.GUARD_OFF.c9f8a17d.json
rename to tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.add_savings_settlement.GUARD_OFF.6cc86672.json
index b69235dd5..3621e8b72 100644
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.GUARD_OFF.c9f8a17d.json
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.add_savings_settlement.GUARD_OFF.6cc86672.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months GUARD_OFF c9f8a17d",
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.add_savings_settlement GUARD_OFF 6cc86672",
   "killed_by": "tests/features.py",
-  "old": "            if wood_configured and calibration is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "            if wood_free:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.line.RETURN_DEL.e3d647a1.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.line.RETURN_DEL.e3d647a1.json
new file mode 100644
index 000000000..55505c6c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.line.RETURN_DEL.e3d647a1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.line RETURN_DEL e3d647a1",
+  "killed_by": "tests/features.py",
+  "old": "        return {\"kwh\": float(entry.get(\"kwh\", 0.0)), \"sek\": float(entry.get(\"sek\", 0.0))}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.66109ecf.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.66109ecf.json
deleted file mode 100644
index 8c7d6c0b1..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.66109ecf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration CMP_BOUND 66109ecf",
-  "killed_by": "tests/features.py",
-  "old": "        if SAVINGS_PLAN_LINE not in lines or plan_kwh < MIN_CALIBRATION_KWH:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: CMP_BOUND (`if SAVINGS_PLAN_LINE not in lines or plan_kwh <= MIN_CALIBRATION_KWH:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.735c54e2.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.735c54e2.json
new file mode 100644
index 000000000..9c6b52a18
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.CMP_BOUND.735c54e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration CMP_BOUND 735c54e2",
+  "killed_by": "tests/features.py",
+  "old": "        if plan_kwh < MIN_CALIBRATION_KWH:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if plan_kwh <= MIN_CALIBRATION_KWH:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.66109ecf.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.66109ecf.json
deleted file mode 100644
index e7f146ec2..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.66109ecf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration GUARD_OFF 66109ecf",
-  "killed_by": "tests/features.py",
-  "old": "        if SAVINGS_PLAN_LINE not in lines or plan_kwh < MIN_CALIBRATION_KWH:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.735c54e2.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.735c54e2.json
new file mode 100644
index 000000000..b2c4090fe
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.GUARD_OFF.735c54e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration GUARD_OFF 735c54e2",
+  "killed_by": "tests/features.py",
+  "old": "        if plan_kwh < MIN_CALIBRATION_KWH:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.085ffc24.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.085ffc24.json
new file mode 100644
index 000000000..a61265c9b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.085ffc24.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration RETURN_DEL 085ffc24",
+  "killed_by": "tests/features.py",
+  "old": "        return self.line(month, actual_line)[\"kwh\"] / plan_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.fbe6bc9f.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.fbe6bc9f.json
deleted file mode 100644
index 1ed994e90..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.meter_calibration.RETURN_DEL.fbe6bc9f.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.meter_calibration RETURN_DEL fbe6bc9f",
-  "killed_by": "tests/features.py",
-  "old": "        return self.line(month, \"savings_actual\")[\"kwh\"] / plan_kwh",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 806aa2ce89aeb6c00cf756195f31026ab798f3ca: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.5a9e8e3d.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.5a9e8e3d.json
new file mode 100644
index 000000000..0759dade8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.5a9e8e3d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months BOOLOP 5a9e8e3d",
+  "killed_by": "tests/features.py",
+  "old": "            below_floor = not old_basis and below_meter_floor(self.line(key, \"savings_baseline\")[\"kwh\"], actual[\"kwh\"])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`below_floor = not old_basis or below_meter_floor(self.line(key, \"savings_baseline\")[\"kwh\"], actual[\"kwh\"])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.c9f8a17d.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.c9f8a17d.json
deleted file mode 100644
index aa74cefdd..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.BOOLOP.c9f8a17d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months BOOLOP c9f8a17d",
-  "killed_by": "tests/features.py",
-  "old": "            if wood_configured and calibration is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if wood_configured or calibration is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.CLAMP_DROP.c2367089.json b/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.CLAMP_DROP.c2367089.json
deleted file mode 100644
index fa1c46941..000000000
--- a/tests/mutation_ledger/killed_by/ledger.py/MonthlyLedger.savings_months.CLAMP_DROP.c2367089.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months CLAMP_DROP c2367089",
-  "killed_by": "tests/features.py",
-  "old": "                calibration = max(1.0, calibration)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`calibration = (1.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.CLAMP_DROP.e865fbd0.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.CLAMP_DROP.e865fbd0.json
new file mode 100644
index 000000000..2254d844d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.CLAMP_DROP.e865fbd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration CLAMP_DROP e865fbd0",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1.0, measured), \"wood_floor\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (1.0), \"wood_floor\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.70a72deb.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.70a72deb.json
new file mode 100644
index 000000000..e52c94f8c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.70a72deb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration GUARD_OFF 70a72deb",
+  "killed_by": "tests/features.py",
+  "old": "    if not wood_configured:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.9bb7edf2.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.9bb7edf2.json
new file mode 100644
index 000000000..b17308527
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.9bb7edf2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration GUARD_OFF 9bb7edf2",
+  "killed_by": "tests/features.py",
+  "old": "    if measured is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.e390a09b.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.e390a09b.json
new file mode 100644
index 000000000..e7b5c0cfc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.GUARD_OFF.e390a09b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration GUARD_OFF e390a09b",
+  "killed_by": "tests/features.py",
+  "old": "    if wood_free is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.RETURN_DEL.e865fbd0.json b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.RETURN_DEL.e865fbd0.json
new file mode 100644
index 000000000..c713a1462
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/applied_calibration.RETURN_DEL.e865fbd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:applied_calibration RETURN_DEL e865fbd0",
+  "killed_by": "tests/features.py",
+  "old": "    return max(1.0, measured), \"wood_floor\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.BOOLOP.a9737861.json b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.BOOLOP.a9737861.json
new file mode 100644
index 000000000..be8abe342
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.BOOLOP.a9737861.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:below_meter_floor BOOLOP a9737861",
+  "killed_by": "tests/features.py",
+  "old": "    return metered_kwh >= MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return metered_kwh >= MIN_CALIBRATION_KWH or booked_kwh < METER_FLOOR * metered_kwh`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.CMP_BOUND.a9737861.json b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.CMP_BOUND.a9737861.json
new file mode 100644
index 000000000..185dc0cc6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.CMP_BOUND.a9737861.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:below_meter_floor CMP_BOUND a9737861",
+  "killed_by": "tests/features.py",
+  "old": "    return metered_kwh >= MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return metered_kwh > MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.RETURN_DEL.a9737861.json b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.RETURN_DEL.a9737861.json
new file mode 100644
index 000000000..89f447849
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/ledger.py/below_meter_floor.RETURN_DEL.a9737861.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:below_meter_floor RETURN_DEL a9737861",
+  "killed_by": "tests/features.py",
+  "old": "    return metered_kwh >= MIN_CALIBRATION_KWH and booked_kwh < METER_FLOOR * metered_kwh",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/notifier.py/_monthly_receipt.BOOLOP.68515705.json b/tests/mutation_ledger/killed_by/notifier.py/_monthly_receipt.BOOLOP.68515705.json
new file mode 100644
index 000000000..6eaa1c5fe
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/notifier.py/_monthly_receipt.BOOLOP.68515705.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/notifier.py:_monthly_receipt BOOLOP 68515705",
+  "killed_by": "tests/features.py",
+  "old": "        \"saving_below_meter_floor\": bool(saving and saving.get(\"below_meter_floor\")),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`\"saving_below_meter_floor\": bool(saving or saving.get(\"below_meter_floor\")),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/plan_view.py b/tests/plan_view.py
index 23d23d1be..ac1d0ae9f 100644
--- a/tests/plan_view.py
+++ b/tests/plan_view.py
@@ -140,6 +140,8 @@ if abs(slot_d - dw) > 0.01:
 # a ledger settled through the production path -- a closed month whose meter
 # exceeds the plan's model by a fixed factor, and an open one priced over a
 # varying profile -- beside the ledger's own rows, which card.mjs compares.
+# The closed month's booked reference stays above ledger.METER_FLOOR of its
+# meter (0.6 kW against 1.56 x a 0.65 kW plan), so its saving publishes.
 from harness import FakeCoordinator, FakeEntry
 from heatpump_optimizer.ledger import MonthlyLedger
 from heatpump_optimizer.sensor import MonthlySavingsSensor
@@ -148,7 +150,7 @@ for _h in range(48):
     for _month, _spot in ((9, 1.0 + 0.5 * (_h % 4)), (10, 0.8 + 0.3 * (_h % 3))):
         _ledger.observe_spot_and_settle_savings(
             datetime(2026, _month, 3 + _h // 24, _h % 24, 0), _spot,
-            {"baseline_kw": 0.5 if _month == 9 else 1.2, "power": 0.9 if _h % 2 else 0.4, "grid_fee": 0.3},
+            {"baseline_kw": 0.6 if _month == 9 else 1.2, "power": 0.9 if _h % 2 else 0.4, "grid_fee": 0.3},
             1.56 * (0.9 if _h % 2 else 0.4), 1.0,
         )
 _savings_now = datetime(2026, 10, 5, 0, 0)
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index e8fe5d7fe..c96927bff 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,21 +1,21 @@
 {
- "class_excess_loc": 17557,
+ "class_excess_loc": 17554,
  "const_modules_over_50": 3,
  "coordinator_attrs": 141,
  "coordinator_multiassigned_attrs": 108,
  "coordinator_private_reach": 0,
  "dead_methods": 0,
  "dead_top_level_symbols": 1,
- "duplication_copies": 10,
+ "duplication_copies": 9,
  "functions_cc_over_15": 26,
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7932,
+ "max_class_loc": 7931,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "dee8b413fd7da7b07f13e28a93d7d49b4a9e978a",
+ "recorded_at": "0a8033305d7b03494eb63453e6181a13ffa55c05",
  "seam_cut_total": 423
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
