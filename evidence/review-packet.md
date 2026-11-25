# Review packet #3863
head: 3f8fb54ffcf92146097881fe4762866340446fe8
base: 5594a34a49404109b8e0f18bd5be18ddbb667cdf

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=138974059029 success
arch-score / arch-score id=138973603163 success
arm id=138973180613 skipped
budget-raise-gate / budget-raise-gate id=138973603312 success
cancel-superseded id=138973201758 success
codeql id=138973584212 skipped
codeql / Analyze (actions) id=138973603233 success
codeql / Analyze (javascript-typescript) id=138973603274 success
codeql / Analyze (python) id=138973603199 success
gate id=138974218122 failure
governance id=138973583998 skipped
governance / env-matrix id=138973603254 success
governance / instrument-self-tests id=138973603361 success
governance / policy-docs id=138973603241 success
governance / record id=138973605534 skipped
governance / wave-script id=138973603279 success
hassfest id=138973584230 skipped
hassfest / hassfest id=138973603030 success
kernel-points id=138973604816 skipped
pr-contract id=138974219774 skipped
prelude id=138973201748 success
refresh id=138973201424 success
sweep-self id=138974673604 skipped
tests id=138973583682 skipped
tests / arch-instrument id=138973961336 success
tests / briefs id=138973603135 success
tests / browser id=138973961350 success
tests / closure-scope id=138973603042 success
tests / closures id=138973961498 success
tests / closures-autofix id=138985579369 skipped
tests / coverage id=138973961226 success
tests / coverage-ratchet id=138983926787 success
tests / fast (3.14) id=138973961273 in_progress
tests / graders-head-copy id=138983926731 success
tests / mutation id=138973603147 success
tests / mutation-autofix id=138984749903 skipped
tests / mutation-pins id=138984748879 skipped
tests / nightly-ha id=138973962656 skipped
tests / nightly-status id=138973603104 failure
tests / replay id=138973961275 cancelled
tests / typing id=138973961287 success
validate id=138973583217 skipped
validate / validate-hacs id=138973602945 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 3f8fb54ffcf92146097881fe4762866340446fe8 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 4 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json b/tests/mutation_ledger/killed_by/dhw_start.py/@module.CONST.c95e30be.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/@module.CONST.c95e30be.json
index 6778cf2e61..65de3f1dee 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/@module.CONST.c95e30be.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:<module> CONST c95e30be",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:<module> CONST c95e30be",
   "killed_by": "tests/block_duty.py",
   "old": "STARTABLE_ROUNDS = 8",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`STARTABLE_ROUNDS = 16`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.BOOLOP.6c096d09.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.BOOLOP.6c096d09.json
index ab09d83fe4..99e05888bb 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.BOOLOP.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps BOOLOP 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps BOOLOP 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if cycle_step is not None or 0 <= cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.CMP_BOUND.6c096d09.json
similarity index 77%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.CMP_BOUND.6c096d09.json
index d702531e8c..90184ccd02 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.CMP_BOUND.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps CMP_BOUND 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps CMP_BOUND 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if cycle_step is not None and 0 < cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.6c096d09.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.6c096d09.json
index 3a532a0795..5b90f97e8f 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps GUARD_OFF 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
similarity index 68%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
index a26a52429d..c902d97677 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF cccafcc1",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps GUARD_OFF cccafcc1",
   "killed_by": "tests/manual_plan.py",
   "old": "    if everyday is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.RETURN_DEL.87df096e.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.RETURN_DEL.87df096e.json
index 5ed862def7..8db9e90f6c 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.RETURN_DEL.87df096e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps RETURN_DEL 87df096e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps RETURN_DEL 87df096e",
   "killed_by": "tests/block_duty.py",
   "old": "    return start",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.064a19f6.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.064a19f6.json
index a4e8b3a54d..3cfa474834 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable CMP_BOUND 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if temps_of(plan)[i] > start_below[i]:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.b56fd264.json
similarity index 68%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.b56fd264.json
index 3d43b90b16..2ce30c34ba 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.b56fd264.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND b56fd264",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable CMP_BOUND b56fd264",
   "killed_by": "tests/block_duty.py",
   "old": "    on = plan > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = plan >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=8."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.GUARD_OFF.064a19f6.json
similarity index 70%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.GUARD_OFF.064a19f6.json
index f68b057eb8..e853afa2d5 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.GUARD_OFF.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable GUARD_OFF 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable GUARD_OFF 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.RETURN_DEL.c913c48e.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.RETURN_DEL.c913c48e.json
index bba12cc624..9eac33c137 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.RETURN_DEL.c913c48e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable RETURN_DEL c913c48e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable RETURN_DEL c913c48e",
   "killed_by": "tests/block_duty.py",
   "old": "    return plan",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=9."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.99a579b8.json
similarity index 69%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.99a579b8.json
index a9e44056f4..5086594868 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:place_startable GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.e4a2bfaa.json
similarity index 70%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.e4a2bfaa.json
index 0c4ceb6b59..77aba7ba6f 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.e4a2bfaa.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF e4a2bfaa",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:place_startable GUARD_OFF e4a2bfaa",
   "killed_by": "tests/block_duty.py",
   "old": "        if np.array_equal(fixed, plan):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.RETURN_DEL.474cf0a0.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/place_startable.RETURN_DEL.474cf0a0.json
index 9e7ca6a749..27a80dbde5 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.RETURN_DEL.474cf0a0.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable RETURN_DEL 68208daf",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:place_startable RETURN_DEL 474cf0a0",
   "killed_by": "tests/block_duty.py",
-  "old": "    return drop_unstartable(plan, start_below, temps_of)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "    return drop_unstartable(plan, start_below, temps_of, charge_running)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=8."
 }
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.3d3ec5bc.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.3d3ec5bc.json
index 6443097405..4168f9479e 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.3d3ec5bc.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps BOOLOP 3d3ec5bc",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps BOOLOP 3d3ec5bc",
   "killed_by": "tests/block_duty.py",
   "old": "        under_way = bool(on[i] and ok[i])",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`under_way = bool(on[i] or ok[i])`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.b3507faf.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.b3507faf.json
new file mode 100644
index 0000000000..aae4b5f71d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.b3507faf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps BOOLOP b3507faf",
+  "killed_by": "tests/block_duty.py",
+  "old": "    under_way = bool(on[:1].any()) and (charge_running or bool(ok[:1].any()))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`under_way = bool(on[:1].any()) or (charge_running or bool(ok[:1].any()))`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.1edfe326.json
similarity index 73%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.1edfe326.json
index f11e540a53..e71a081651 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.1edfe326.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 1edfe326",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps CMP_BOUND 1edfe326",
   "killed_by": "tests/block_duty.py",
   "old": "    on = np.asarray(plan, dtype=float) > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = np.asarray(plan, dtype=float) >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.6e3a088f.json
similarity index 78%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.6e3a088f.json
index 94c3474d95..3aa762de5d 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.6e3a088f.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 6e3a088f",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps CMP_BOUND 6e3a088f",
   "killed_by": "tests/block_duty.py",
   "old": "    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] <= start_below[: on.size]`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.GUARD_OFF.99a579b8.json
similarity index 69%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.GUARD_OFF.99a579b8.json
index 26c5b81261..ee268c5433 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.RETURN_DEL.82bc35de.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.RETURN_DEL.82bc35de.json
index 1fc93528fd..5b19a72ce1 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.RETURN_DEL.82bc35de.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps RETURN_DEL 82bc35de",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps RETURN_DEL 82bc35de",
   "killed_by": "tests/block_duty.py",
   "old": "    return ok",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=4."
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.557fbb7b.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.557fbb7b.json
new file mode 100644
index 0000000000..7b35905d84
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.557fbb7b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way BOOLOP 557fbb7b",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return replace(state, dhw_charge_under_way=running and (not signals.mode_observed or dhw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return replace(state, dhw_charge_under_way=running or (not signals.mode_observed or dhw))`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.c726e2be.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.c726e2be.json
new file mode 100644
index 0000000000..214535fdc0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.c726e2be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way BOOLOP c726e2be",
+  "killed_by": "tests/block_duty.py",
+  "old": "    dhw = mode.dhw and (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) > 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`dhw = mode.dhw or (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) > 0.0)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.CMP_BOUND.c726e2be.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.CMP_BOUND.c726e2be.json
new file mode 100644
index 0000000000..ac2cd92a19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.CMP_BOUND.c726e2be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way CMP_BOUND c726e2be",
+  "killed_by": "tests/block_duty.py",
+  "old": "    dhw = mode.dhw and (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) > 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`dhw = mode.dhw and (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) >= 0.0)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.RETURN_DEL.557fbb7b.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.RETURN_DEL.557fbb7b.json
new file mode 100644
index 0000000000..547e2ea755
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.RETURN_DEL.557fbb7b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way RETURN_DEL 557fbb7b",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return replace(state, dhw_charge_under_way=running and (not signals.mode_observed or dhw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 2b4d71b8ce..4851dd8c26 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -6263,9 +6263,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             caps = env_caps if caps is None else np.minimum(caps, env_caps)
         quiet = quiet_windows.compose_with_silent(caps, ctx._config, ctx.hass.states.get, solve_now, n, config.dt_hours, params.max_electrical_power, optimizer_active=self._mode != MODE_OFF)
         return SolveRecord(config, params, SolveInputs(
-            state=state,
+            state=pump_signals.with_dhw_under_way(state, self._pump_signals, running := duty_switch.running_now(duty_switch.record_for(self), self._current_action), self._current_action),
             start_time=solve_now,
-            compressor_running=duty_switch.running_now(duty_switch.record_for(self), self._current_action),
+            compressor_running=running,
             forecast=ForecastSeries(
                 prices=horizon.prices,
                 outdoor_temps=horizon.outdoor_temps,
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index cd0e495d1c..63747dbb41 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -38,6 +38,7 @@ from .dhw_schedule import (
     parse_windows,
     windows_for_day,
 )
+from .dhw_start import dhw_start_temps, place_startable, startable_steps
 from .manual_plan import _pin_is_free
 from .thermal_model import (
     TANK_ROOM_AMBIENT_TEMP,
@@ -52,8 +53,6 @@ from .thermal_model import (
     dhw_draw_scale,
     added_power_for_heat_per_cop_kw,
     delivered_heat_kw,
-    dhw_start_below_c,
-    dhw_step_target_c,
     heat_per_cop_kw,
     power_for_heat_per_cop_kw,
 )
@@ -211,108 +210,6 @@ def _drop_off_steps(mask: np.ndarray, off: np.ndarray | None) -> np.ndarray:
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
 
@@ -1297,7 +1194,7 @@ class DhwPlanner:
         # before each breach until the simulated trajectory honours the
         # requirement, then re-apply the rating, which always wins.
         start_below = dhw_start_temps(params, initial_state, n_steps, legionella_step)
-        tank = (ctx, initial_state.dhw_temperature, draw_rates)
+        tank, running = (ctx, initial_state.dhw_temperature, draw_rates), initial_state.dhw_charge_under_way
         schedule = place_startable(schedule, start_below, partial(self._ctx_temps, *tank), partial(
             self._repair_dhw_floor,
             ctx,
@@ -1305,8 +1202,8 @@ class DhwPlanner:
             draw_rates=draw_rates,
             requirement=requirement,
             max_temp=max_temp,
-            forced_off=forced_off,
-        ))
+            forced_off=forced_off, charge_running=running,
+        ), running)
         # Not re-clamped here, because the repair now carries the clamp
         # inside its own loop: every top-up it places is followed by one,
         # so a plan leaves this stage already bounded by the per-step
@@ -1731,7 +1628,7 @@ class DhwPlanner:
         requirement: np.ndarray,
         max_temp: np.ndarray,
         forced_off: np.ndarray | None = None,
-        start_below: np.ndarray | None = None,
+        start_below: np.ndarray | None = None, charge_running: bool = True,
     ) -> np.ndarray:
         """Top up the plan until the SIMULATED trajectory meets the floor.
 
@@ -1803,7 +1700,7 @@ class DhwPlanner:
             usable = headroom > 1e-6
             if forced_off is not None:
                 usable &= ~np.asarray(forced_off[lo : b + 1], dtype=bool)
-            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]
+            usable &= startable_steps(plan, temps, start_below, charge_running)[lo : b + 1]
             # Degrees of room under the ceiling for heat added at each
             # candidate. The heat is stored from the candidate to the breach,
             # decaying as it leaks away, so the bound is the tightest of
diff --git a/custom_components/heatpump_optimizer/dhw_start.py b/custom_components/heatpump_optimizer/dhw_start.py
new file mode 100644
index 0000000000..704a489914
--- /dev/null
+++ b/custom_components/heatpump_optimizer/dhw_start.py
@@ -0,0 +1,126 @@
+"""The pump's hot-water start condition: where a planned charge is one the pump makes.
+
+A heat pump starts a hot-water charge only on a tank below its set-point less
+its start hysteresis (``thermal_model.dhw_start_below_c``). Here that rule
+becomes the per-step start temperature (:func:`dhw_start_temps`) and the
+steps a charge may be bought on (:func:`startable_steps`). It also becomes the
+floor repair that drops a charge the pump would never start and re-buys the
+floor elsewhere (:func:`drop_unstartable`, :func:`place_startable`).
+``dhw_planner.DhwPlanner`` calls them; they hold no state and read only their
+arguments.
+"""
+from __future__ import annotations
+
+from typing import Callable
+
+import numpy as np
+
+from .thermal_model import ThermalParameters, ThermalState, dhw_start_below_c, dhw_step_target_c
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
+    plan: np.ndarray, temps: np.ndarray, start_below: np.ndarray | None, charge_running: bool = True
+) -> np.ndarray:
+    """The steps where charging is something the pump does.
+
+    A step that opens on a tank below its start temperature (``temps[i]``,
+    the simulated level at its start), and the step after one of a charge
+    under way, which runs on to its target. A charge is under way from the
+    step it opens below its start temperature, or from the first step when
+    ``charge_running`` (``ThermalState.dhw_charge_under_way``) says one runs
+    now. A charge the pump would not start carries nothing on, so the repair
+    buys neither inside it nor behind it. Every step where no start condition
+    is known (``start_below`` ``None``).
+    """
+    on = np.asarray(plan, dtype=float) > 0.0
+    if start_below is None:
+        return np.ones(on.size, dtype=bool)
+    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]
+    under_way = bool(on[:1].any()) and (charge_running or bool(ok[:1].any()))
+    for i in range(1, on.size):
+        ok[i] |= under_way
+        under_way = bool(on[i] and ok[i])
+    return ok
+
+
+def drop_unstartable(
+    plan: np.ndarray,
+    start_below: np.ndarray,
+    temps_of: Callable[[np.ndarray], np.ndarray],
+    charge_running: bool = True,
+) -> np.ndarray:
+    """``plan`` without the charges the pump would never start.
+
+    Each run is judged in time order on the trajectory ``temps_of`` simulates
+    for the runs kept before it: one that begins on a tank at or above its
+    step's start temperature is removed whole. A run at the first step is
+    kept while ``charge_running``, a charge under way (Bankaifan, #3440); with
+    none running, it is judged like any other.
+    """
+    plan = np.array(plan, dtype=float)
+    on = plan > 0.0
+    for i in np.flatnonzero(on & ~np.append(charge_running, on[:-1])[: on.size]):
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
+    charge_running: bool = True,
+) -> np.ndarray:
+    """The floor repair of ``plan`` under the pump's start condition.
+
+    With no condition, ``repair(plan=plan)``, the call as it always was. With
+    one, the charges the pump would not start are dropped and ``repair``,
+    handed the condition so it places only on :func:`startable_steps`,
+    re-buys what the floor still needs; a top-up warms the tank under every
+    later charge, so the two repeat until the plan stands, at most
+    :data:`STARTABLE_ROUNDS` times. The plan that leaves holds no charge the
+    pump would not start, and is short of the floor only where no startable
+    step can hold it. ``charge_running`` is :func:`drop_unstartable`'s;
+    ``repair`` is handed it already bound.
+    """
+    if start_below is None:
+        return repair(plan=plan)
+    for _ in range(STARTABLE_ROUNDS):
+        fixed = repair(plan=drop_unstartable(plan, start_below, temps_of, charge_running), start_below=start_below)
+        if np.array_equal(fixed, plan):
+            break
+        plan = fixed
+    return drop_unstartable(plan, start_below, temps_of, charge_running)
diff --git a/custom_components/heatpump_optimizer/pump_signals.py b/custom_components/heatpump_optimizer/pump_signals.py
index 221ba9fa6b..84444ddc75 100644
--- a/custom_components/heatpump_optimizer/pump_signals.py
+++ b/custom_components/heatpump_optimizer/pump_signals.py
@@ -72,7 +72,7 @@ additive there, not a second mechanism fighting the first.
 from __future__ import annotations
 
 import logging
-from dataclasses import dataclass, field
+from dataclasses import dataclass, field, replace
 from datetime import datetime
 from typing import Any
 
@@ -365,6 +365,23 @@ class PumpSignals:
         }
 
 
+def with_dhw_under_way(state: Any, signals: PumpSignals, running: bool, action: Any) -> Any:
+    """``state`` with ``dhw_charge_under_way`` set: whether a hot-water charge runs now.
+
+    The compressor runs (``running``, ``duty_switch.running_now``) and the
+    observed mode serves hot water: hot water only, or a combined mode while
+    the executing step (``action``) plans hot water. A combined mode is what
+    the arbiter writes for a hot-water duty on a select with no hot-water
+    only option. With no mode observed a running compressor keeps the first
+    step's charge as before, and so does an unsettled or missing running
+    signal, which ``running_now`` answers from the planned draw. A pump
+    heating, or stopped, has no charge under way.
+    """
+    mode = signals.mode
+    dhw = mode.dhw and (not mode.space_heat or float(action.get("dhw_power", 0.0)) > 0.0)
+    return replace(state, dhw_charge_under_way=running and (not signals.mode_observed or dhw))
+
+
 def read_electric_heat(
     reader: Any, previous: PumpSignals | None = None
 ) -> PumpElectricHeat:
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 0a14a852e1..73705d7394 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -2032,9 +2032,9 @@ class ThermalState:
     # planned charge and every heating write is taken to start the pump.
     dhw_start_hysteresis_k: float | None = None
     space_start_hysteresis_k: float | None = None
-    # The grid the hot-water set-point entity is written on
-    # (``inputs.SetpointGrid``); None with no entity to write.
+    # The hot-water set-point entity's grid (``inputs.SetpointGrid``); None with no entity to write.
     dhw_setpoint_grid: Any = None
+    dhw_charge_under_way: bool = True  # a hot-water charge runs now (``pump_signals.with_dhw_under_way``)
 
     # ECL110 control state
     ecl110_displace_command: float = 0.0  # °C requested parallel shift
diff --git a/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
index 665fcad57a..f0d2f3e8dc 100644
--- a/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
+++ b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
@@ -18,26 +18,26 @@ W = sys.argv[1]
 CC = os.path.join(W, "custom_components/heatpump_optimizer")
 M = [
  ("M1 lift owner returns the configured lift", "thermal_model.py", "    return lift if hysteresis is None else max(lift, hysteresis)\n", "    return lift\n"),
- ("M2 drop_unstartable >= to >", "dhw_planner.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
+ ("M2 drop_unstartable >= to >", "dhw_start.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
  ("M3 ledger not-startable branch removed", "pump_arbiter.py", '    if planned == "dhw" and actual == "idle" and _not_startable(row):\n        return "not-startable"\n', ""),
- ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]\n", ""),
- ("M5 startable_steps < to <=", "dhw_planner.py", "[: on.size] < start_below[: on.size]\n", "[: on.size] <= start_below[: on.size]\n"),
+ ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below, charge_running)[lo : b + 1]\n", ""),
+ ("M5 startable_steps < to <=", "dhw_start.py", "[: on.size] < start_below[: on.size]\n", "[: on.size] <= start_below[: on.size]\n"),
  ("M6 a zero hysteresis is a start condition", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis < 0.0:"),
  ("M7 the difference reader ignores the unit's scale", "inputs.py", "    delta_k = value * scale\n", "    delta_k = value\n"),
- ("M8 the cycle step judged against the everyday target", "dhw_planner.py", "        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)\n", "        pass\n"),
+ ("M8 the cycle step judged against the everyday target", "dhw_start.py", "        start[cycle_step] = dhw_start_below_c(dhw_step_target_c(params, True, grid), hysteresis_k)\n", "        pass\n"),
  ("M9 notice at a minimum equal to the start temperature", "setpoint_check.py", "start is not None and floor > start,", "start is not None and floor >= start,"),
- ("M10 place_startable returns without the final drop", "dhw_planner.py", "        plan = fixed\n    return drop_unstartable(plan, start_below, temps_of)\n", "        plan = fixed\n    return plan\n"),
+ ("M10 place_startable returns without the final drop", "dhw_start.py", "        plan = fixed\n    return drop_unstartable(plan, start_below, temps_of, charge_running)\n", "        plan = fixed\n    return plan\n"),
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
+ ("M16 a run at step 0 is judged too", "dhw_start.py", "    for i in np.flatnonzero(on & ~np.append(charge_running, on[:-1])[: on.size]):\n", "    for i in np.flatnonzero(on & ~np.append(False, on[:-1])[: on.size]):\n"),
+ ("M17 the round bound is nine", "dhw_start.py", "STARTABLE_ROUNDS = 8\n", "STARTABLE_ROUNDS = 9\n"),
+ ("M18 a cycle on the first step is not a cycle step", "dhw_start.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 < cycle_step < n_steps:"),
+ ("M19 a run at the second step is not judged", "dhw_start.py", "    for i in np.flatnonzero(on & ~np.append(charge_running, on[:-1])[: on.size]):\n", "    for i in np.flatnonzero(on[2:] & ~on[1:-1]) + 2:\n"),
+ ("M20 the loop never ends early", "dhw_start.py", "        if np.array_equal(fixed, plan):\n", "        if False:\n"),
+ ("M21 a cycle past the horizon is written", "dhw_start.py", "if cycle_step is not None and 0 <= cycle_step < n_steps:", "if cycle_step is not None and 0 <= cycle_step <= n_steps:"),
  ("M22 the shared clamp zeroes a step on the runnable block", "dhw_planner.py", "        return np.where(plan < ctx.min_run_power - 1e-9, 0.0, plan)\n", "        return np.where(plan <= ctx.min_run_power - 1e-9, 0.0, plan)\n"),
  ("M23 no step is a cycle step for the write or the ledger", "pump_arbiter.py", '    cycle = (inp.action or {}).get("dhw_reason") == REASON_LEGIONELLA or inp.disinfecting\n', "    cycle = False\n"),
  ("M24 the set-point check never reaches the start notice", "setpoint_check.py", "    _dhw_start(hass, config, params)\n", "    pass\n"),
@@ -45,22 +45,22 @@ M = [
  ("M26 a hysteresis under one kelvin is none", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis <= 1.0:"),
  ("M27 pinned hot water is not held to the tank's capacity", "dhw_planner.py", "            schedule = self._ctx_clamp(\n                ctx, initial_state.dhw_temperature, draw_rates, max_temp, schedule)\n", "            pass\n"),
  ("M28 the write and the ledger ignore the entity's grid", "pump_arbiter.py", 'return dhw_step_target_c(inp.params, cycle, _grid(inp, "dhw_setpoint"))', "return dhw_step_target_c(inp.params, cycle, None)"),
- ("M29 the planner ignores the entity's grid", "dhw_planner.py", "hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid\n", "hysteresis_k, grid = state.dhw_start_hysteresis_k, None\n"),
+ ("M29 the planner ignores the entity's grid", "dhw_start.py", "hysteresis_k, grid = state.dhw_start_hysteresis_k, state.dhw_setpoint_grid\n", "hysteresis_k, grid = state.dhw_start_hysteresis_k, None\n"),
  ("M30 the notice ignores the entity's grid", "setpoint_check.py", "dhw_step_target_c(params, False, setpoint_grid(hass, cfg.dhw_setpoint_entity))", "dhw_step_target_c(params, False)"),
  ("M31 the notice is raised with hot water disabled", "setpoint_check.py", "bool(params.dhw_enabled) and start is not None", "start is not None"),
  ("M32 the everyday target ignores the charge limit", "thermal_model.py", "(params.dhw_setpoint, params.dhw_max_temp) if target is None", "(params.dhw_setpoint, 1e9) if target is None"),
  ("M33 the cycle's target ignores the hard maximum", "thermal_model.py", "else (target, params.dhw_hard_max_temp)", "else (target, 1e9)"),
  ("M34 the input read leaves the grid off the state", "inputs.py", "    state.dhw_setpoint_grid = setpoint_grid(hass, cfg.dhw_setpoint_entity)\n", ""),
- ("M35 the step after a charge the pump would not start is startable", "dhw_planner.py", "        under_way = bool(on[i] and ok[i])\n", "        under_way = bool(on[i])\n"),
- ("M36 a charge at the first step carries nothing on", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = False\n"),
- ("M37 no charge under way carries on", "dhw_planner.py", "        ok[i] |= under_way\n", "        pass\n"),
+ ("M35 the step after a charge the pump would not start is startable", "dhw_start.py", "        under_way = bool(on[i] and ok[i])\n", "        under_way = bool(on[i])\n"),
+ ("M36 a charge at the first step carries nothing on", "dhw_start.py", "    under_way = bool(on[:1].any()) and (charge_running or bool(ok[:1].any()))\n", "    under_way = False\n"),
+ ("M37 no charge under way carries on", "dhw_start.py", "        ok[i] |= under_way\n", "        pass\n"),
  ("M38 an entity with no state has a grid", "inputs.py", "    if not entity_id or hass.states.get(entity_id) is None:\n        return None\n    return _grid_of", "    if not entity_id:\n        return None\n    return _grid_of"),
  ("M39 with no entity the target ignores its bound", "thermal_model.py", "        return min(float(value), float(limit))\n", "        return float(value)\n"),
  ("M40 the hot-water write goes to an entity with no state", "pump_arbiter.py", 'return None if _grid(inp, "dhw_setpoint") is None else _dhw_target(inp)', "return _dhw_target(inp)"),
  ("M41 the bound is handed to the grid as the value's own", "thermal_model.py", "grid.bounded(float(value), hi=limit)", "grid.bounded(float(value), hi=float(value))"),
- ("M42 a charge kept at the first step is itself startable on a warm tank", "dhw_planner.py", "    under_way = bool(on[:1].any())\n", "    under_way = bool(on[:1].any())\n    ok[:1] |= on[:1]\n"),
+ ("M42 a charge kept at the first step is itself startable on a warm tank", "dhw_start.py", "    under_way = bool(on[:1].any()) and (charge_running or bool(ok[:1].any()))\n", "    under_way = bool(on[:1].any()) and (charge_running or bool(ok[:1].any()))\n    ok[:1] |= on[:1]\n"),
  ("M43 the notice is never raised", "setpoint_check.py", "        bool(params.dhw_enabled) and start is not None and floor > start,\n", "        False,\n"),
- ("NULL comment-only change", "dhw_planner.py", "    on = plan > 0.0\n    for i in", "    on = plan > 0.0  # null mutant\n    for i in"),
+ ("NULL comment-only change", "dhw_start.py", "    on = plan > 0.0\n    for i in", "    on = plan > 0.0  # null mutant\n    for i in"),
 ]
 only = sys.argv[2:] 
 for name, f, old, new in M:
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index efbb1e8a9b..f5e031c3a4 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=101 measured=101",
+  "result": "documented=102 measured=102",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=101, listed=101, missing=[], phantom=[]",
+  "result": "on disk=102, listed=102, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index e9fabb12fb..f3e350fa67 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 25 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=25 measured=25 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=101 measured=101 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=101, listed=101, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=102 measured=102 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=102, listed=102, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=36 measured=36 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 3027afe504..e0af29ba0f 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=101      (99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=102      (101 until R11-OUTSIDE-3848's dhw_start.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=101           (99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=102           (101 until R11-OUTSIDE-3848's dhw_start.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/programme/delivery/3863.md b/dev/programme/delivery/3863.md
new file mode 100644
index 0000000000..8add213001
--- /dev/null
+++ b/dev/programme/delivery/3863.md
@@ -0,0 +1 @@
+- [#3863](https://github.com/tvofi/heatpump_optimizer/pull/3863) — **open**, fix(dhw): judge a step-0 DHW run unless a charge is under way (supersedes #3848) (R11-OUTSIDE-3848)
diff --git a/docs/architecture.md b/docs/architecture.md
index cc503207c7..f4f3272a79 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 101 modules, of which 36 import the
+knows nothing about Home Assistant: 102 modules, of which 36 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -134,6 +134,7 @@ custom_components/heatpump_optimizer/
 ├── slot_drivers.py       # Why each step runs or idles: five signed driver weights,
 │                         #   and the current step's "why now" for the card
 ├── dhw_planner.py        # The hot-water planner one solve builds: floors, LP, repairs
+├── dhw_start.py          # The pump's hot-water start condition: which planned charges it starts
 ├── batchmath.py          # The batched row reduction every batch twin owes its scalar
 ├── process_worker.py     # One-shot interpreter for GIL-bound solves
 ├── open_meteo.py         # Irradiance forecast and satellite observation client
@@ -292,7 +293,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-36 of the 101 modules import `homeassistant` at module level: `__init__`,
+36 of the 102 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency`, `debugger`, `defrost`,
@@ -301,7 +302,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 64 modules are deliberately free of it, so each can be driven
+The other 65 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/tests/block_duty.py b/tests/block_duty.py
index e469761696..fbcd967144 100644
--- a/tests/block_duty.py
+++ b/tests/block_duty.py
@@ -809,7 +809,7 @@ def hysteresis_checks() -> None:
 
     import numpy as np
 
-    from heatpump_optimizer import dhw_planner as planner
+    from heatpump_optimizer import dhw_start as start
     from heatpump_optimizer import inputs as inputs_mod
     from heatpump_optimizer import thermal_model as tm
 
@@ -867,16 +867,16 @@ def hysteresis_checks() -> None:
     check("null control: with no cycle active a cycle step holds the everyday set-point",
           lambda: tm.dhw_step_target_c(nocyc, True) == 55.0)
     check("each step's start temperature is its own target less the hysteresis, the cycle step the cycle's",
-          lambda: list(planner.dhw_start_temps(cyc, _start_state(4.0), 6, 3)) == [51, 51, 51, 56, 51, 51]
-          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 6, None)) == [51.0] * 6)
+          lambda: list(start.dhw_start_temps(cyc, _start_state(4.0), 6, 3)) == [51, 51, 51, 56, 51, 51]
+          and list(start.dhw_start_temps(cyc, _start_state(4.0), 6, None)) == [51.0] * 6)
     check("a cycle on the first step is judged against its own target; one past the horizon moves no step",
-          lambda: list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 0)) == [56, 51, 51]
-          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 3)) == [51, 51, 51]
-          and list(planner.dhw_start_temps(cyc, _start_state(4.0), 3, 2)) == [51, 51, 56])
+          lambda: list(start.dhw_start_temps(cyc, _start_state(4.0), 3, 0)) == [56, 51, 51]
+          and list(start.dhw_start_temps(cyc, _start_state(4.0), 3, 3)) == [51, 51, 51]
+          and list(start.dhw_start_temps(cyc, _start_state(4.0), 3, 2)) == [51, 51, 56])
     check("with no or zero hysteresis no step has a start temperature",
-          lambda: planner.dhw_start_temps(cyc, _start_state(None), 6, 3) is None
-          and planner.dhw_start_temps(cyc, _start_state(0.0), 6, 3) is None
-          and planner.dhw_start_temps(cyc, _start_state(0.0, _step(5)), 6, 3) is None)
+          lambda: start.dhw_start_temps(cyc, _start_state(None), 6, 3) is None
+          and start.dhw_start_temps(cyc, _start_state(0.0), 6, 3) is None
+          and start.dhw_start_temps(cyc, _start_state(0.0, _step(5)), 6, 3) is None)
 
     # 5. One owner of the target: what the arbiter writes.
     check("the arbiter writes dhw_step_target_c: the everyday set-point with no cycle booked",
@@ -937,17 +937,17 @@ def hysteresis_checks() -> None:
     check("precondition: an everyday 58 on a 5 degC step is written 55, its cycle of 62 written 60",
           lambda: arb._dhw_write(five) == 55.0 and arb._dhw_write(five_cycle) == 60.0)
     check("on a stepped entity each step's start temperature is the written target less the hysteresis",
-          lambda: list(planner.dhw_start_temps(stepped, _start_state(4.0, _step(5)), 4, 2))
+          lambda: list(start.dhw_start_temps(stepped, _start_state(4.0, _step(5)), 4, 2))
           == [arb._dhw_write(five) - 4.0] * 2 + [arb._dhw_write(five_cycle) - 4.0, arb._dhw_write(five) - 4.0]
           == [51.0, 51.0, 56.0, 51.0])
     check("null control: with no set-point entity the same parameters start below 58 and 62 less the hysteresis",
-          lambda: list(planner.dhw_start_temps(stepped, _start_state(4.0), 4, 2)) == [54.0, 54.0, 58.0, 54.0])
+          lambda: list(start.dhw_start_temps(stepped, _start_state(4.0), 4, 2)) == [54.0, 54.0, 58.0, 54.0])
     check("the ledger's start temperature on the stepped entity is the planner's",
           lambda: arb._dhw_start_below_c(replace(five, state=_start_state(4.0, _step(5)))) == 51.0
           and arb._dhw_start_below_c(replace(five_cycle, state=_start_state(4.0, _step(5)))) == 56.0)
 
     # 6. Which steps the pump starts.
-    startable = planner.startable_steps
+    startable = start.startable_steps
     check("a step is startable where it opens on a tank below its start temperature or follows a charge under way",
           lambda: list(startable(np.array([0, 0, 1, 0, 0.]), np.array([54, 52, 50, 53, 50.9, 50.]),
                                  np.full(5, 51.0))) == [False, False, True, True, True])
@@ -981,7 +981,7 @@ def hysteresis_checks() -> None:
 
     plan = np.array([1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0])
     kept = plan.copy()
-    drop = planner.drop_unstartable
+    drop = start.drop_unstartable
     check("a charge begun above its start temperature is dropped whole; the first step and a cooled tank's run are kept",
           lambda: list(drop(plan, np.full(8, 51.0), temps_of)) == [1, 0, 0, 0, 0, 0, 0, 1])
     check("a tank exactly at the start temperature does not start",
@@ -995,6 +995,27 @@ def hysteresis_checks() -> None:
           lambda: list(drop(np.array([0.0, 1.0, 0.0]), np.full(3, 51.0), temps_of)) == [0, 0, 0])
     check("a run at the first step is kept on a warm tank, with nothing planned at the horizon's end",
           lambda: list(drop(np.array([1.0, 0.0, 0.0]), np.full(3, 51.0), temps_of)) == [1, 0, 0])
+    check("a first-step charge on a warm tank with no charge under way is dropped, and nothing carries it on",
+          lambda: list(drop(np.array([1.0, 1.0, 0.0]), np.full(3, 51.0), temps_of, False)) == [0, 0, 0]
+          and list(startable(np.array([1.0, 0.0, 0.0]), warm, np.full(3, 51.0), False)) == [False] * 3
+          and list(start.place_startable(np.array([1.0, 0.0]), np.full(2, 51.0), temps_of,
+                                           lambda plan, start_below: plan, False)) == [0, 0])
+    check("with no charge under way a first-step charge on a cold tank starts and carries on",
+          lambda: list(startable(np.array([1.0, 0.0, 0.0]), np.array([50.0, 53.0, 52.0]), np.full(3, 51.0), False))
+          == [True, True, False])
+
+    from heatpump_optimizer import pump_mode, pump_signals
+    from heatpump_optimizer.thermal_model import ThermalState
+
+    def under_way(running, mode, dhw_kw=0.0):
+        signals = pump_signals.PumpSignals(mode=pump_mode.capability(mode or "?"), mode_observed=mode is not None)
+        return pump_signals.with_dhw_under_way(ThermalState(), signals, running,
+                                               {"dhw_power": dhw_kw}).dhw_charge_under_way
+
+    check("a charge is under way only with the compressor running in a mode serving the step's hot water",
+          lambda: [under_way(False, "DHW", 2.0), under_way(True, "Heating"), under_way(True, "DHW"),
+                   under_way(True, "Heating + DHW", 2.0), under_way(True, "Heating + DHW"),
+                   under_way(True, None)] == [False, False, True, True, False, True])
 
     # 8. The repair loop.
     def raises(_plan):
@@ -1002,7 +1023,7 @@ def hysteresis_checks() -> None:
 
     marker = np.array([0.0, 1.0])
     check("with no start temperature the repair's own answer stands and no trajectory is read",
-          lambda: planner.place_startable(plan, None, raises, lambda plan: marker) is marker)
+          lambda: start.place_startable(plan, None, raises, lambda plan: marker) is marker)
     calls, original = [], plan
 
     def stubborn(plan, start_below):
@@ -1010,16 +1031,16 @@ def hysteresis_checks() -> None:
         return original.copy()
 
     check("a repair that keeps re-placing the unstartable plan still leaves a plan with none, in bounded rounds",
-          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, stubborn))
+          lambda: list(start.place_startable(plan, np.full(8, 51.0), temps_of, stubborn))
           == list(drop(plan, np.full(8, 51.0), temps_of))
-          and 1 <= len(calls) <= planner.STARTABLE_ROUNDS)
+          and 1 <= len(calls) <= start.STARTABLE_ROUNDS)
     rounds = []
 
     def counting(plan, start_below):
         rounds.append(1)
         return plan
 
-    planner.place_startable(plan, np.full(8, 51.0), temps_of, counting)
+    start.place_startable(plan, np.full(8, 51.0), temps_of, counting)
     check("a repair that changes nothing ends the loop: one round to drop, one to see the plan stand",
           lambda: len(rounds) == 2)
     turns = []
@@ -1031,12 +1052,12 @@ def hysteresis_checks() -> None:
         out[4] = float(len(turns) % 2)
         return out
 
-    settled = planner.place_startable(plan, np.full(8, 51.0), temps_of, restless)
+    settled = start.place_startable(plan, np.full(8, 51.0), temps_of, restless)
     check("a repair that never settles is asked the documented eight rounds, and what leaves still holds no unstartable charge",
-          lambda: planner.STARTABLE_ROUNDS == 8 and len(turns) == 8
+          lambda: start.STARTABLE_ROUNDS == 8 and len(turns) == 8
           and np.array_equal(settled, drop(settled, np.full(8, 51.0), temps_of)))
     check("an identity repair leaves the dropped plan",
-          lambda: list(planner.place_startable(plan, np.full(8, 51.0), temps_of, lambda plan, start_below: plan))
+          lambda: list(start.place_startable(plan, np.full(8, 51.0), temps_of, lambda plan, start_below: plan))
           == list(drop(plan, np.full(8, 51.0), temps_of)))
 
     # 8b. The clamp-then-zero step the placement stages share.
diff --git a/tests/closures.json b/tests/closures.json
index d2c295d09b..782dd29d29 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -203,6 +203,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -324,6 +325,7 @@
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/duty_legs.py",
@@ -385,6 +387,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -509,6 +512,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -622,6 +626,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -749,6 +754,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -879,6 +885,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -1021,6 +1028,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -1134,6 +1142,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -1269,6 +1278,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -1416,6 +1426,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -1689,6 +1700,7 @@
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/duty_legs.py",
@@ -1809,6 +1821,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -2356,6 +2369,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -2563,6 +2577,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -2728,6 +2743,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -2882,6 +2898,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -3083,6 +3100,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -3261,6 +3279,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -3667,6 +3686,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -3799,6 +3819,7 @@
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/duty_legs.py",
@@ -3853,6 +3874,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -3967,6 +3989,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -4066,6 +4089,7 @@
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/duty_legs.py",
@@ -4132,6 +4156,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -4238,6 +4263,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/diagnostics.py",
    "custom_components/heatpump_optimizer/disinfection.py",
@@ -4326,6 +4352,7 @@
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/duty_legs.py",
@@ -4380,6 +4407,7 @@
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
    "custom_components/heatpump_optimizer/dhw_schedule.py",
+   "custom_components/heatpump_optimizer/dhw_start.py",
    "custom_components/heatpump_optimizer/diagnosis.py",
    "custom_components/heatpump_optimizer/disinfection.py",
    "custom_components/heatpump_optimizer/draw_range.py",
@@ -6217,7 +6245,7 @@
   },
   "tests/cycle_lane.py": {
    "rc": 0,
-   "seconds": 61.7
+   "seconds": 317.8
   },
   "tests/debug_collect.py": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index c6e8b5ecef..9e639839a2 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 120
+records every read, so this lane's recorded closure is the package: all 121
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (120 until #3848's ``dhw_start.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
diff --git a/tests/features.py b/tests/features.py
index 64c08e4dde..3dcc269204 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -41033,7 +41033,7 @@ R.check(
 # repair's own ceiling, and what left the ramp short.
 def _lg_whole_tail_repair(
     self, ctx, *, plan, initial_temp, draw_rates, requirement, max_temp,
-    forced_off=None,
+    forced_off=None, charge_running=True,
 ):
     outdoor_temps = ctx.outdoor_temps
     dt = ctx.dt
@@ -97139,9 +97139,34 @@ R.check(
     "the what-if solve takes the reading the live plan was solved with, not a "
     "fresh one: the two start counts the card compares share r[-1]",
     "compressor_running=duty_switch.record_for(self).solved_running" in _hsr_inspect.getsource(Coord._whatif_solve)
-    and "compressor_running=duty_switch.running_now(duty_switch.record_for(self), self._current_action)"
+    and "duty_switch.running_now(duty_switch.record_for(self), self._current_action)"
     in _hsr_inspect.getsource(Coord._solve_record),
 )
+# The same reading tells the planner whether a hot-water charge runs now
+# (pump_signals.with_dhw_under_way): the scheduled solve's state carries it.
+from heatpump_optimizer import pump_mode as _hsr_pm, pump_signals as _hsr_ps  # noqa: E402
+
+
+def _hsr_under_way(mode, action):
+    _hsr_live._pump_signals = _hsr_ps.PumpSignals(mode=_hsr_pm.capability(mode), mode_observed=True)
+    _hsr_live._current_action = action
+    now = _hsr_pss(datetime(2026, 1, 10, 12, 0, tzinfo=UTC))
+    return _hsr_live._solve_record(now, _hsr_live._forecast_arrays(now)).inputs.state.dhw_charge_under_way
+
+
+_hsr_under = [
+    _hsr_under_way("DHW", {"power": 0.0, "dhw_power": 2.0}),
+    _hsr_under_way("Heating", {"power": 3.0, "dhw_power": 0.0}),
+    _hsr_under_way("DHW", {}),
+]
+_hsr_live._pump_signals = _hsr_ps.PumpSignals()
+R.check(
+    "the scheduled solve's state holds a hot-water charge under way only while the "
+    "compressor runs in a mode serving hot water: running on hot water, not running "
+    "on heating, not stopped",
+    _hsr_under == [True, False, False],
+    f"{_hsr_under}",
+)
 
 # What the commit program is told is fixed: a forced-on pin and a step hot
 # water runs in are on, a step with no room at all is off, the rest are free.
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json b/tests/mutation_ledger/killed_by/dhw_start.py/@module.CONST.c95e30be.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/@module.CONST.c95e30be.json
index 6778cf2e61..65de3f1dee 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/@module.CONST.c95e30be.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/@module.CONST.c95e30be.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:<module> CONST c95e30be",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:<module> CONST c95e30be",
   "killed_by": "tests/block_duty.py",
   "old": "STARTABLE_ROUNDS = 8",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`STARTABLE_ROUNDS = 16`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.BOOLOP.6c096d09.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.BOOLOP.6c096d09.json
index ab09d83fe4..99e05888bb 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.BOOLOP.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.BOOLOP.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps BOOLOP 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps BOOLOP 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if cycle_step is not None or 0 <= cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.CMP_BOUND.6c096d09.json
similarity index 77%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.CMP_BOUND.6c096d09.json
index d702531e8c..90184ccd02 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.CMP_BOUND.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.CMP_BOUND.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps CMP_BOUND 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps CMP_BOUND 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if cycle_step is not None and 0 < cycle_step < n_steps:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1. Each of the 2 sites under this anchor was killed."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.6c096d09.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.6c096d09.json
index 3a532a0795..5b90f97e8f 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.6c096d09.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.6c096d09.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF 6c096d09",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps GUARD_OFF 6c096d09",
   "killed_by": "tests/block_duty.py",
   "old": "    if cycle_step is not None and 0 <= cycle_step < n_steps:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=2."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
similarity index 68%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
index a26a52429d..c902d97677 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.GUARD_OFF.cccafcc1.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps GUARD_OFF cccafcc1",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps GUARD_OFF cccafcc1",
   "killed_by": "tests/manual_plan.py",
   "old": "    if everyday is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.RETURN_DEL.87df096e.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.RETURN_DEL.87df096e.json
index 5ed862def7..8db9e90f6c 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/dhw_start_temps.RETURN_DEL.87df096e.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/dhw_start_temps.RETURN_DEL.87df096e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:dhw_start_temps RETURN_DEL 87df096e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:dhw_start_temps RETURN_DEL 87df096e",
   "killed_by": "tests/block_duty.py",
   "old": "    return start",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.064a19f6.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.064a19f6.json
index a4e8b3a54d..3cfa474834 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable CMP_BOUND 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if temps_of(plan)[i] > start_below[i]:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.b56fd264.json
similarity index 68%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.b56fd264.json
index 3d43b90b16..2ce30c34ba 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.CMP_BOUND.b56fd264.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.CMP_BOUND.b56fd264.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable CMP_BOUND b56fd264",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable CMP_BOUND b56fd264",
   "killed_by": "tests/block_duty.py",
   "old": "    on = plan > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = plan >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=8."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.GUARD_OFF.064a19f6.json
similarity index 70%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.GUARD_OFF.064a19f6.json
index f68b057eb8..e853afa2d5 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.GUARD_OFF.064a19f6.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.GUARD_OFF.064a19f6.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable GUARD_OFF 064a19f6",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable GUARD_OFF 064a19f6",
   "killed_by": "tests/block_duty.py",
   "old": "        if temps_of(plan)[i] >= start_below[i]:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.RETURN_DEL.c913c48e.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.RETURN_DEL.c913c48e.json
index bba12cc624..9eac33c137 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/drop_unstartable.RETURN_DEL.c913c48e.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/drop_unstartable.RETURN_DEL.c913c48e.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:drop_unstartable RETURN_DEL c913c48e",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:drop_unstartable RETURN_DEL c913c48e",
   "killed_by": "tests/block_duty.py",
   "old": "    return plan",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=9."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.99a579b8.json
similarity index 69%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.99a579b8.json
index a9e44056f4..5086594868 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:place_startable GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.e4a2bfaa.json
similarity index 70%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.e4a2bfaa.json
index 0c4ceb6b59..77aba7ba6f 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.GUARD_OFF.e4a2bfaa.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.GUARD_OFF.e4a2bfaa.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable GUARD_OFF e4a2bfaa",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:place_startable GUARD_OFF e4a2bfaa",
   "killed_by": "tests/block_duty.py",
   "old": "        if np.array_equal(fixed, plan):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.RETURN_DEL.474cf0a0.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/place_startable.RETURN_DEL.474cf0a0.json
index 9e7ca6a749..27a80dbde5 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/place_startable.RETURN_DEL.68208daf.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/place_startable.RETURN_DEL.474cf0a0.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:place_startable RETURN_DEL 68208daf",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:place_startable RETURN_DEL 474cf0a0",
   "killed_by": "tests/block_duty.py",
-  "old": "    return drop_unstartable(plan, start_below, temps_of)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "    return drop_unstartable(plan, start_below, temps_of, charge_running)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=8."
 }
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.3d3ec5bc.json
similarity index 72%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.3d3ec5bc.json
index 6443097405..4168f9479e 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.BOOLOP.3d3ec5bc.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.3d3ec5bc.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps BOOLOP 3d3ec5bc",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps BOOLOP 3d3ec5bc",
   "killed_by": "tests/block_duty.py",
   "old": "        under_way = bool(on[i] and ok[i])",
   "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`under_way = bool(on[i] or ok[i])`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.b3507faf.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.b3507faf.json
new file mode 100644
index 0000000000..aae4b5f71d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.BOOLOP.b3507faf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps BOOLOP b3507faf",
+  "killed_by": "tests/block_duty.py",
+  "old": "    under_way = bool(on[:1].any()) and (charge_running or bool(ok[:1].any()))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`under_way = bool(on[:1].any()) or (charge_running or bool(ok[:1].any()))`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.1edfe326.json
similarity index 73%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.1edfe326.json
index f11e540a53..e71a081651 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.1edfe326.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.1edfe326.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 1edfe326",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps CMP_BOUND 1edfe326",
   "killed_by": "tests/block_duty.py",
   "old": "    on = np.asarray(plan, dtype=float) > 0.0",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = np.asarray(plan, dtype=float) >= 0.0`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=6."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.6e3a088f.json
similarity index 78%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.6e3a088f.json
index 94c3474d95..3aa762de5d 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.CMP_BOUND.6e3a088f.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.CMP_BOUND.6e3a088f.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps CMP_BOUND 6e3a088f",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps CMP_BOUND 6e3a088f",
   "killed_by": "tests/block_duty.py",
   "old": "    ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] < start_below[: on.size]",
   "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`ok: np.ndarray = np.asarray(temps, dtype=float)[: on.size] <= start_below[: on.size]`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.GUARD_OFF.99a579b8.json
similarity index 69%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.GUARD_OFF.99a579b8.json
index 26c5b81261..ee268c5433 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.GUARD_OFF.99a579b8.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.GUARD_OFF.99a579b8.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps GUARD_OFF 99a579b8",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps GUARD_OFF 99a579b8",
   "killed_by": "tests/manual_plan.py",
   "old": "    if start_below is None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.RETURN_DEL.82bc35de.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
rename to tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.RETURN_DEL.82bc35de.json
index 1fc93528fd..5b19a72ce1 100644
--- a/tests/mutation_ledger/killed_by/dhw_planner.py/startable_steps.RETURN_DEL.82bc35de.json
+++ b/tests/mutation_ledger/killed_by/dhw_start.py/startable_steps.RETURN_DEL.82bc35de.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:startable_steps RETURN_DEL 82bc35de",
+  "anchor": "custom_components/heatpump_optimizer/dhw_start.py:startable_steps RETURN_DEL 82bc35de",
   "killed_by": "tests/block_duty.py",
   "old": "    return ok",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=4."
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.557fbb7b.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.557fbb7b.json
new file mode 100644
index 0000000000..7b35905d84
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.557fbb7b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way BOOLOP 557fbb7b",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return replace(state, dhw_charge_under_way=running and (not signals.mode_observed or dhw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return replace(state, dhw_charge_under_way=running or (not signals.mode_observed or dhw))`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.c726e2be.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.c726e2be.json
new file mode 100644
index 0000000000..214535fdc0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.BOOLOP.c726e2be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way BOOLOP c726e2be",
+  "killed_by": "tests/block_duty.py",
+  "old": "    dhw = mode.dhw and (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) > 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`dhw = mode.dhw or (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) > 0.0)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.CMP_BOUND.c726e2be.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.CMP_BOUND.c726e2be.json
new file mode 100644
index 0000000000..ac2cd92a19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.CMP_BOUND.c726e2be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way CMP_BOUND c726e2be",
+  "killed_by": "tests/block_duty.py",
+  "old": "    dhw = mode.dhw and (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) > 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`dhw = mode.dhw and (not mode.space_heat or float(action.get(\"dhw_power\", 0.0)) >= 0.0)`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.RETURN_DEL.557fbb7b.json b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.RETURN_DEL.557fbb7b.json
new file mode 100644
index 0000000000..547e2ea755
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_signals.py/with_dhw_under_way.RETURN_DEL.557fbb7b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_signals.py:with_dhw_under_way RETURN_DEL 557fbb7b",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return replace(state, dhw_charge_under_way=running and (not signals.mode_observed or dhw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f10f128938..22e4f4bd79 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -16,9 +16,9 @@
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
- "module_excess_loc": 21775,
+ "module_excess_loc": 21672,
  "name_kept_members": 38,
- "recorded_at": "59b17e97ae1b65bd86c6b5423c0a5e993031c9a0",
+ "recorded_at": "3a98735a7ecc59e7ecc095a0429cdf6251d956ec",
  "seam_cut_total": 413,
  "unloaded_package_imports": 14
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
