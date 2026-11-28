# Review packet #3907
head: 8c3f64114f6eb60679562cbd6e0f6a1fdab4b588
base: a59a1b0d9ac782fabbe01eb84f4d4ff5a17aee43

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=141060342091 success
arch-score / arch-score id=141060145871 success
arm id=141059781520 skipped
budget-raise-gate / budget-raise-gate id=141060145882 failure
cancel-superseded id=141059868066 success
codeql id=141060120628 skipped
codeql / Analyze (actions) id=141060145802 success
codeql / Analyze (javascript-typescript) id=141060145810 success
codeql / Analyze (python) id=141060145825 success
gate id=141060597777 failure
governance id=141060120748 skipped
governance / env-matrix id=141060145862 success
governance / instrument-self-tests id=141060145929 success
governance / policy-docs id=141060145944 success
governance / record id=141060147220 skipped
governance / wave-script id=141060145901 success
hassfest id=141060120090 skipped
hassfest / hassfest id=141060145803 success
kernel-points id=141060147347 skipped
pr-contract id=141060599260 skipped
prelude id=141059868357 success
sweep-self id=141060863926 skipped
tests id=141060120579 skipped
tests / arch-instrument id=141060416067 success
tests / briefs id=141060145834 success
tests / browser id=141060416109 success
tests / ci-ratchet id=141073373604 skipped
tests / claims-autofix id=141066035499 success
tests / closure-scope id=141060145817 success
tests / closures id=141060416096 success
tests / closures-autofix id=141073327039 skipped
tests / coverage id=141060416141 success
tests / coverage-ratchet id=141073372098 success
tests / fast (3.14, 1/4) id=141060416123 failure
tests / fast (3.14, 2/4) id=141060416166 success
tests / fast (3.14, 3/4) id=141060416129 success
tests / fast (3.14, 4/4) id=141060416134 success
tests / graders-head-copy id=141073372129 success
tests / lane-proofs id=141073372053 success
tests / mutation id=141060145860 failure
tests / mutation-pins (1) id=141060540138 in_progress
tests / mutation-pins (10) id=141060540129 queued
tests / mutation-pins (11) id=141060540151 queued
tests / mutation-pins (12) id=141060540103 queued
tests / mutation-pins (2) id=141060540121 in_progress
tests / mutation-pins (3) id=141060540173 in_progress
tests / mutation-pins (4) id=141060540162 in_progress
tests / mutation-pins (5) id=141060540163 queued
tests / mutation-pins (6) id=141060540130 queued
tests / mutation-pins (7) id=141060540118 queued
tests / mutation-pins (8) id=141060540154 queued
tests / mutation-pins (9) id=141060540136 queued
tests / nightly-ha id=141060417735 skipped
tests / nightly-status id=141060145829 failure
tests / replay id=141060416097 success
tests / typing id=141060416111 success
validate id=141060120592 skipped
validate / validate-hacs id=141060145785 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 8c3f64114f6eb60679562cbd6e0f6a1fdab4b588 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

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
  ok         bash tools/pr/prepr.sh --self-test
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git diff 6ade1643e2 e50d72615a --stat
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git diff --name-only d972dae309 HEAD -- custom_components | wc -l
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 13 resolved, 8 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
deleted file mode 100644
index 7e0808e417..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c294c9b7",
-  "killed_by": "tests/features.py",
-  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
-}
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
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
similarity index 51%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
index bd324872f3..d942d4aade 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF ac9b3721",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal GUARD_OFF 4763baed",
   "killed_by": "tests/features.py",
-  "old": "        if experiment:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "old": "    if start_below is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
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
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.33f4dbe6.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.33f4dbe6.json
new file mode 100644
index 0000000000..8a3ade8608
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.33f4dbe6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits RETURN_DEL 33f4dbe6",
+  "killed_by": "tests/features.py",
+  "old": "        return charge_refusal(candidate, start_below, temps_of, held, charge_running) or candidate",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=19."
+}
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
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
new file mode 100644
index 0000000000..82d3290dba
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges GUARD_OFF cbabd675",
+  "killed_by": "tests/features.py",
+  "old": "    if charge_runs is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
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
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.d042d302.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
similarity index 89%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.d042d302.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
index bae72c78be..8271995631 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.d042d302.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF d042d302",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF d042d302",
   "killed_by": "tests/features.py",
   "old": "        if not ceiling_frozen:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
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


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/accuracy.py b/custom_components/heatpump_optimizer/accuracy.py
index 01a17e149b..65d8392ba2 100644
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
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 41aa71b030..10d1ecaeaa 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -5065,7 +5065,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # fabricates a confident 0 kW sample. Same gate, same reasoning as
         # the COP fold: a large total gap is tracking, not measurement, so
         # the interval carries no usable split (v4.0.5 review).
-        commanded_total = commanded_space + dhw_share
+        commanded_total = draw_range.inside_approach(self._accuracy.draw) or commanded_space + dhw_share  # inside a run's learned approach, the expected draw
         if (
             abs(float(self._measured_power) - commanded_total)
             / max(commanded_total, 0.5)
@@ -5346,7 +5346,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             self._fold_cop_evidence(row.asked_kw, row.drawn_kw, None, row.reference, row.cop_scale)
         if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now(), not experiment)) is not None:
             self._apply_cop_scale(owed)
-        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):
+        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment, draw_range.inside_approach(draw) is not None):
             return refusal
 
         # In the frosting band the shortfall belongs to the defrost derate,
@@ -6309,6 +6309,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             state=pump_signals.with_dhw_under_way(state, self._pump_signals, running := duty_switch.running_now(duty_switch.record_for(self), self._current_action), self._current_action),
             start_time=solve_now,
             compressor_running=running,
+            approach=draw_range.solve_approach(self._accuracy.draw, params, solve_now.timestamp()),
             forecast=ForecastSeries(
                 prices=horizon.prices,
                 outdoor_temps=horizon.outdoor_temps,
@@ -9932,11 +9933,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # The meter read now closes the interval ``pending`` governed, so the
         # draw pairs with that interval's ask and set-point, not the next one's
         # (#2262), within the window the accuracy pairing below trusts; a
-        # prediction recording no split, or a dwell that saw hot water, is none.
-        if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending["split"])):
+        # prediction recording no split is none, and a dwell that saw hot water moves only the approach's run clock.
+        if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0):
             # An unplanned charge is no running space sample (#3760): the pending split's own evidence.
             space_frozen = self._learning_frozen(CONF_POWER_ENTITY, sample=learning_freeze.Sample.SPACE_HEAT, evidence=_space_evidence(self, pending["split"]))
-            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=space_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"), experiment_s=pending["when"].timestamp() if pending.get("mode") == "system_identification" else None, ceiling_frozen=_ceiling_frozen(self))
+            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=space_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"), ceiling_frozen=_ceiling_frozen(self), span=draw_range.Span(pending["when"].timestamp(), now.timestamp(), heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending["split"])), pending.get("mode") == "system_identification"))
 
         # T5 #16: settle every matured lead-time promise against the same
         # measured temperature the one-step sample below uses. The window
@@ -10022,11 +10023,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
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
@@ -10143,9 +10142,9 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
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
@@ -11236,6 +11235,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             start_time=solve_at,
             held_start=held_start,
             compressor_running=duty_switch.record_for(self).solved_running,
+            approach=draw_range.solve_approach(self._accuracy.draw, scratch_params, solve_at.timestamp()),
             forecast=ForecastSeries(
                 prices=horizon.prices,
                 outdoor_temps=horizon.outdoor_temps,
diff --git a/custom_components/heatpump_optimizer/dhw_charges.py b/custom_components/heatpump_optimizer/dhw_charges.py
new file mode 100644
index 0000000000..956195199e
--- /dev/null
+++ b/custom_components/heatpump_optimizer/dhw_charges.py
@@ -0,0 +1,298 @@
+"""Hot-water charges the pump would start and run, for the planner's plan.
+
+The stage ``DhwPlanner._build_dhw_requirements`` calls after the floor
+repair under the pump's start condition (``dhw_start.place_startable``).
+The commit (:func:`commit_charges`), on a solve that plans runs
+(:class:`ChargeRuns`): the plan as charges that run at the pump's floor or
+above, chosen between the store program's plan (:class:`_StoreProgram`)
+and the lifted one. Each is kept only where the pump would start its
+charges under the same start condition.
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
+from .dhw_start import STARTABLE_ROUNDS, drop_unstartable, startable_steps
+from .thermal_model import heat_per_cop_kw, power_for_heat_per_cop_kw
+
+if TYPE_CHECKING:
+    from .dhw_planner import DhwPlanner, _DhwPlanContext
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
+    charge_running: bool = True,
+) -> tuple[str, int] | None:
+    """Why the commit may not ship ``candidate``, or ``None`` where it may.
+
+    ``("start", step)``: on the candidate's own walk the pump would not start
+    the charge that opens there (:func:`drop_unstartable` removes it).
+    ``("floor", step)``: the walk falls under ``held``, the floors the
+    uncommitted plan held, by more than the planners' tolerance. With no
+    start condition known every charge is taken to start; a charge at the
+    first step starts only while ``charge_running`` says one is under way
+    or the tank is below its start temperature there.
+    """
+    if start_below is not None:
+        lost = np.flatnonzero(drop_unstartable(candidate, start_below, temps_of, charge_running) != candidate)
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
+    charge_running: bool = True,
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
+    which ``place_startable`` already left startable. ``start_below`` and
+    ``charge_running`` are the floor repair's: the start condition
+    (``dhw_start.dhw_start_temps``) and whether a charge is under way at
+    solve time (``ThermalState.dhw_charge_under_way``).
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
+        return charge_refusal(candidate, start_below, temps_of, held, charge_running) or candidate
+
+    def cost(candidate: np.ndarray) -> float:
+        starts = runs.start_count(space + candidate, floor, charge.running)
+        return float(np.sum(ctx.prices * candidate) * ctx.dt) + charge.start_cost * starts
+
+    program = _StoreProgram(planner, ctx, plan, tank, (held, np.maximum(limits[1], walk[1:])), forced_off, space)
+    proposed = (
+        program.accepted(startable_steps(plan, walk, start_below, charge_running), fits),
+        fits(np.where((plan > 0.0) & (plan < floor), floor, plan)),
+    )
+    return min((c for c in proposed if isinstance(c, np.ndarray)), key=cost, default=plan)
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index df4c77b4b9..de408e0a03 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -29,6 +29,7 @@ from scipy.optimize import linprog
 
 from . import pv
 from .const import DHW_QUANTILE_MIN_EVENTS
+from .dhw_charges import SHORTFALL_K, ChargeRuns, commit_charges, whole_charges
 from .dhw_draws import window_label as draw_window_label
 from .dhw_schedule import (
     FULL_DAY,
@@ -304,6 +305,13 @@ class _DhwPlanContext:
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
@@ -359,7 +367,7 @@ class DhwPlanner:
 
     Every input is explicit and fixed at construction. ``pv_surplus`` and
     ``price_known`` default to None, which is what a fresh optimizer held
-    before its first solve.
+    before its first solve. ``charge_runs``: :class:`ChargeRuns`, or None.
     """
 
     def __init__(
@@ -368,11 +376,13 @@ class DhwPlanner:
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
@@ -1197,6 +1207,7 @@ class DhwPlanner:
             max_temp=max_temp,
             forced_off=forced_off,
         ), running)
+        schedule = commit_charges(self, schedule, tank, (requirement, max_temp), forced_off, start_below, space_demand, running)
         # Not re-clamped here, because the repair now carries the clamp
         # inside its own loop: every top-up it places is followed by one,
         # so a plan leaves this stage already bounded by the per-step
@@ -1234,6 +1245,7 @@ class DhwPlanner:
             mask[:horizon] = covered[:horizon]
             if legionella_step is not None:
                 mask[legionella_step] = False
+            mask = whole_charges(self.charge_runs, schedule, mask)
             schedule = np.where(mask, 0.0, schedule)
 
         next_window = _dhw_next_window_hours(h.start_time, hours_mod, step_weekdays, windows, params, holiday_flags)
@@ -1378,16 +1390,13 @@ class DhwPlanner:
 
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
@@ -1560,7 +1569,7 @@ class DhwPlanner:
                 plan, initial_temp, outdoor_temps, draw_rates, dt, humidity, exo_kw
             )
         gaps = requirement - temps[1 : plan.size + 1]
-        for i in np.where(gaps > 0.05)[0]:
+        for i in np.where(gaps > SHORTFALL_K)[0]:
             if int(i) not in unreachable:
                 return temps, gaps, int(i)
         return temps, gaps, None
diff --git a/custom_components/heatpump_optimizer/draw_range.py b/custom_components/heatpump_optimizer/draw_range.py
index e18f0a5099..ca8ec138bd 100644
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
@@ -868,8 +870,8 @@ def fold(
     distorted: bool,
     defrost: bool,
     command: Any = None,
-    experiment_s: float | None = None,
     ceiling_frozen: bool = False,
+    span: Span | None = None,
 ) -> None:
     """Fold one interval into ``draw`` when it is a running sample.
 
@@ -880,10 +882,10 @@ def fold(
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
     folds into the window as before. ``ceiling_frozen`` refuses that store
@@ -892,7 +894,42 @@ def fold(
 
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
@@ -912,6 +949,86 @@ def fold(
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
@@ -981,6 +1098,9 @@ class SolveBand:
     min_reason: str = "awaiting"
     learned_min_kw: float | None = None
     min_samples: int = 0
+    #: The learned approach's entry energy above the floor this solve booked
+    #: per run out of a pause, kWh (``solve_approach``), or ``None``.
+    approach_kwh: float | None = None
 
     def as_dict(self) -> dict[str, Any]:
         return {
@@ -997,6 +1117,7 @@ class SolveBand:
             "min_reason": self.min_reason,
             "learned_min_kw": None if self.learned_min_kw is None else round(self.learned_min_kw, 3),
             "min_samples": self.min_samples,
+            "approach_kwh": None if self.approach_kwh is None else round(self.approach_kwh, 3),
         }
 
 
@@ -1025,6 +1146,8 @@ def solve_band(
     samples = len(draw.ceiling)
     bottom = _bottom_fields(draw, cfg_min, cfg_max, cap.plan_writes_power(), applies_floor)
     floor = bottom["learned_min_kw"] if bottom["min_source"] == "metered" else None
+    entry = solve_approach(draw, params, now_s)
+    bottom["approach_kwh"] = None if entry is None else entry.entry_kwh(approach_floor_kw(draw, params))
 
     def band(top: float, source: str, reason: str, learned: float | None = None) -> SolveBand:
         min_kw = cfg_min if floor is None and source == "configured" else min(floor or cfg_min, top)
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index f19377797c..f3c3cfec86 100644
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
@@ -200,6 +201,14 @@ def _engaged(opt: HeatPumpOptimizer) -> bool:
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
@@ -327,9 +336,11 @@ def _shipped_and_received(
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
@@ -337,9 +348,11 @@ def _shipped_and_received(
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
@@ -538,7 +551,7 @@ def _run_plans(
     heats = (hi >= floor) & ((other <= 0.0) | (space >= floor / 2.0))
     masks = runs.candidates(
         space + other, h.prices, floor, hi + other, opt.config.start_price,
-        dt=h.dt, running=h.compressor_running,
+        dt=h.dt, running=h.compressor_running, entry_kwh=0.0 if opt._approach is None else opt._approach.entry_kwh(floor),
         forced=np.where((other > 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),
     )
     idle = np.where(cycled, space, lo)
@@ -2028,6 +2041,10 @@ def _combi_dhw_exo(
 #: (the `exchange` harness arm in dev/audit/harnesses/r10_combi_tank.py
 #: prints the rounds a plan takes).
 _COMBI_EXCHANGE_ROUNDS = 4
+#: How much further under the requirement the committed plan's store may
+#: fall than the exchange's own plan and still ship, K: the planners'
+#: shortfall tolerance.
+_COMBI_COMMIT_SLACK_K = 0.05
 
 
 def _combi_flux_exchange(
@@ -2043,23 +2060,51 @@ def _combi_flux_exchange(
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
             valve_targets=h.valve_targets, step_hours=h.step_hours)[4]
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
@@ -3138,6 +3183,7 @@ class SolveInputs:
     #: The compressor runs at solve time: a run that continues from it is no
     #: start, in the start term and in the published count alike.
     compressor_running: bool = False
+    approach: runs.Approach | None = None  # a run's learned first steps, read as received draw
 
 
 def _horizon_weather(series: ForecastSeries, n_steps: int) -> WeatherSeries:
@@ -3486,6 +3532,7 @@ class HeatPumpOptimizer:
         #: The ``duty_legs.availability`` vector the last space solve scored
         #: with, riding beside its plan; ``None`` when no stop is charged.
         self._space_avail: np.ndarray | None = None
+        self._approach: runs.Approach | None = None
         #: The solve's starting buffer temperature; floors the settlement
         #: value cap so pre-stored heat cannot be drained for free.
         self._initial_buffer_temp: float | None = None
@@ -4371,18 +4418,12 @@ class HeatPumpOptimizer:
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
@@ -4486,8 +4527,7 @@ class HeatPumpOptimizer:
         )
         # One hot-water planner per solve, from this solve's inputs (#1743).
         planner = DhwPlanner(
-            self.model, self.config, self._pv_surplus, self._price_known
-        )
+            self.model, self.config, self._pv_surplus, self._price_known, _charge_runs(self, inputs.compressor_running))
 
         # --- Analyze forecast trajectory for predictive signals ---
         forecast_analysis = self._analyze_forecast_trajectory(
@@ -4611,6 +4651,7 @@ class HeatPumpOptimizer:
         # #1295: the plan the caller hands in -- the coordinator seeds it from
         # the last shipped plan -- is one extra candidate on the FIRST solve
         # only; ``_warm_start_starts`` says why later solves get none.
+        self._approach = inputs.approach
         result = _solve(self._warm_start_starts(n_steps))
 
         # A blocked channel is withheld from the release loop entirely. Its
@@ -5460,7 +5501,7 @@ class HeatPumpOptimizer:
 
             # Electricity cost, piecewise in PV surplus. ``float()`` is
             # identity on the 1-D branch's return and states it.
-            drawn = combined if heat_power is space_power else heat_power + dhw_plan_power
+            drawn = combined if heat_power is space_power else heat_power + (0.0 if dhw_plan_power is None else dhw_plan_power)
             energy_cost = (
                 float(energy_cost_of(drawn)) * self.config.price_weight
             )
@@ -5526,7 +5567,7 @@ class HeatPumpOptimizer:
             )
             return self._cost_terms_batch(
                 traj,
-                grid_power if heat_matrix is space_matrix else heat_matrix + dhw_plan_power,
+                grid_power if heat_matrix is space_matrix else heat_matrix + (0.0 if dhw_plan_power is None else dhw_plan_power),
                 level_cost=_with_switch_cost(
                     _with_switch_cost(capacity_batch(grid_power), start_cost(grid_power, descent)),
                     switch_cost(space_matrix, dhw_plan_power, descent)),
@@ -5657,7 +5698,7 @@ class HeatPumpOptimizer:
             optimal_power = initial_power
             status = f"failed ({e})"
 
-        # Simulate with optimal schedule
+        # Simulate with optimal schedule, as received (``_shipped_and_received``)
         (
             room_temps,
             slab_temps,
@@ -5666,7 +5707,7 @@ class HeatPumpOptimizer:
             buffer_temps,
             _,
             wood_temps,
-        ) = _space_traj(optimal_power)
+        ) = _space_traj(_shipped_and_received(self, optimal_power, None, None)[2])
         # The achieved objective, for candidate comparison across valve
         # schedules. One extra evaluation, robust on the failure path too.
         achieved_objective = float(objective(optimal_power))
@@ -5905,8 +5946,7 @@ class HeatPumpOptimizer:
         )
         # Received through the vector the adopted solve scored with, never a
         # rebuilt one; the schedule and the achieved objective keep the level.
-        heat_space = optimal_space if self._space_avail is None else duty_legs.delivered_space(
-            optimal_space, optimal_dhw, self._space_avail, _duty_floor(self))
+        heat_space = _shipped_and_received(self, optimal_space, optimal_dhw, self._space_avail)[2]
 
         # Simulate with optimal schedule
         published_end: list[ThermalState] = []
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
index 46fbd27dff..1cf27a2c23 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -351,6 +351,13 @@ _ACCURACY: dict[str, Domain | str] = {
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
diff --git a/dev/audit/harnesses/ceiling_probe.py b/dev/audit/harnesses/ceiling_probe.py
index eb00b933af..07ca4e156e 100644
--- a/dev/audit/harnesses/ceiling_probe.py
+++ b/dev/audit/harnesses/ceiling_probe.py
@@ -153,7 +153,7 @@ def store_arm() -> None:
             if pending is not None:
                 dr.fold(store, 3.0 if pending["cmd"] is ceil else 1.5, (pending["kw"], 0.0), params,
                         frozen=False, distorted=False, defrost=False, command=pending["cmd"],
-                        experiment_s=pending["when"] if pending["sid"] else None)
+                        span=dr.Span(pending["when"], pending["when"], experiment=True) if pending["sid"] else None)
             kw = 1.5 if override is None else override
             pending = {"sid": override is not None, "kw": kw, "when": now.timestamp(),
                        "cmd": ceil if kw >= 5.0 else mid}
diff --git a/dev/audit/harnesses/r10_dhw_start_hysteresis.py b/dev/audit/harnesses/r10_dhw_start_hysteresis.py
index ad2de645ee..55a7a0edc7 100644
--- a/dev/audit/harnesses/r10_dhw_start_hysteresis.py
+++ b/dev/audit/harnesses/r10_dhw_start_hysteresis.py
@@ -33,7 +33,7 @@ RESULT lines, each a sum over the 18 solves:
   dhw_cost                               the planned hot-water energy at the day's prices
   plan_sha1                              sha1 over the 18 hot-water schedules and trajectories
   repair_rounds_max / placements         the most floor-repair calls one placement under a start
-                                         condition made (``dhw_planner.place_startable``), and
+                                         condition made (``dhw_start.place_startable``), and
                                          how many placements were counted; "none" with no condition
 Null control: ``--hysteresis`` unset and ``--hysteresis 0`` print the
 plan_sha1 the merge base prints; a hysteresis of 4 prints
diff --git a/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
index f0d2f3e8dc..d958a77542 100644
--- a/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
+++ b/dev/audit/harnesses/r10_dhw_start_hysteresis_mutants.py
@@ -20,7 +20,7 @@ M = [
  ("M1 lift owner returns the configured lift", "thermal_model.py", "    return lift if hysteresis is None else max(lift, hysteresis)\n", "    return lift\n"),
  ("M2 drop_unstartable >= to >", "dhw_start.py", "        if temps_of(plan)[i] >= start_below[i]:", "        if temps_of(plan)[i] > start_below[i]:"),
  ("M3 ledger not-startable branch removed", "pump_arbiter.py", '    if planned == "dhw" and actual == "idle" and _not_startable(row):\n        return "not-startable"\n', ""),
- ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below, charge_running)[lo : b + 1]\n", ""),
+ ("M4 repair places without the start mask", "dhw_planner.py", "            usable &= startable_steps(plan, temps, start_below)[lo : b + 1]\n", ""),
  ("M5 startable_steps < to <=", "dhw_start.py", "[: on.size] < start_below[: on.size]\n", "[: on.size] <= start_below[: on.size]\n"),
  ("M6 a zero hysteresis is a start condition", "thermal_model.py", "hysteresis is None or hysteresis <= 0.0:", "hysteresis is None or hysteresis < 0.0:"),
  ("M7 the difference reader ignores the unit's scale", "inputs.py", "    delta_k = value * scale\n", "    delta_k = value\n"),
diff --git a/dev/audit/harnesses/r11_honest_dhw_runs.py b/dev/audit/harnesses/r11_honest_dhw_runs.py
new file mode 100644
index 0000000000..ba8cafd9ba
--- /dev/null
+++ b/dev/audit/harnesses/r11_honest_dhw_runs.py
@@ -0,0 +1,447 @@
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
+        def stage(planner, plan, store, limits, forced_off, start_below, space_demand, *running):
+            if planner.charge_runs is None:
+                return watch.kept["stage"](planner, plan, store, limits, forced_off, start_below, space_demand, *running)
+            build = {"space": space_demand is not None, "rounds": 0, "verdicts": [], "plan": np.array(plan)}
+            watch.builds.append(build)
+            ctx = store[0]
+            build["temps_of"] = lambda x: planner._ctx_temps(ctx, store[1], store[2], np.asarray(x, float))
+            build["start_below"], build["requirement"], build["store"] = start_below, limits[0], store
+            build["running"] = running
+            floor = runs.floor_kw(planner.model.params.min_electrical_power)
+            space = np.zeros(ctx.n_steps) if space_demand is None else np.clip(space_demand, 0.0, None)
+            build["cost"] = lambda x: float(np.sum(ctx.prices * x) * ctx.dt) + planner.charge_runs.start_cost * (
+                runs.start_count(space + x, floor, planner.charge_runs.running))
+            out = watch.kept["stage"](planner, plan, store, limits, forced_off, start_below, space_demand, *running)
+            build["out"] = np.array(out)
+            return out
+
+        def refusal(candidate, start_below, temps_of, held, *running):
+            got = watch.kept["refusal"](candidate, start_below, temps_of, held, *running)
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
+                    kept = dc.drop_unstartable(b["out"], b["start_below"], b["temps_of"], *b["running"])
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
diff --git a/dev/audit/rounds/round11/D2/s3/m5_drawrange.py b/dev/audit/rounds/round11/D2/s3/m5_drawrange.py
index 9983f6d1d4..0045f415de 100644
--- a/dev/audit/rounds/round11/D2/s3/m5_drawrange.py
+++ b/dev/audit/rounds/round11/D2/s3/m5_drawrange.py
@@ -98,12 +98,12 @@ def run(cell, top):
         drawn = max(ask, 1.5) if cell == "uncensored" else 1.5
         drawn = min(drawn, top)
         draw_range.fold(d, drawn, (ask, 0.0), P, frozen=False, distorted=False, defrost=False,
-                        command=None, experiment_s=None)
+                        command=None)
         t += 1800.0
     for k in range(14):
         drawn = top if cell == "uncensored" else 1.5
         draw_range.fold(d, drawn, (6.0, 0.0), P, frozen=False, distorted=False, defrost=False,
-                        command=CEIL, experiment_s=t, **_ceiling_ask(d, drawn))
+                        command=CEIL, span=draw_range.Span(t, t, experiment=True), **_ceiling_ask(d, drawn))
         t += 1800.0
     band = draw_range.solve_band(d, P, CAP, t)
     pr = draw_range.planned_range(d, P, CAP)
diff --git a/dev/programme/delivery/3805.md b/dev/programme/delivery/3805.md
new file mode 100644
index 0000000000..1330321e58
--- /dev/null
+++ b/dev/programme/delivery/3805.md
@@ -0,0 +1 @@
+- [#3805](https://github.com/tvofi/heatpump_optimizer/pull/3805) — **open**, R11-OUTSIDE-HONEST-DHW-RUNS: r11 outside honest dhw runs (R11-OUTSIDE-HONEST-DHW-RUNS)
diff --git a/dev/programme/delivery/3907.md b/dev/programme/delivery/3907.md
new file mode 100644
index 0000000000..a3b37bb848
--- /dev/null
+++ b/dev/programme/delivery/3907.md
@@ -0,0 +1 @@
+- [#3907](https://github.com/tvofi/heatpump_optimizer/pull/3907) — **open**, R11-OUTSIDE-START-APPROACH: a space run's approach to its floor, learned and priced (R11-OUTSIDE-START-APPROACH)
diff --git a/docs/architecture.md b/docs/architecture.md
index 9a8c828a66..7a2194a823 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -137,6 +137,7 @@ custom_components/heatpump_optimizer/
 │                         #   and the current step's "why now" for the card
 ├── dhw_planner.py        # The hot-water planner one solve builds: floors, LP, repairs
 ├── dhw_start.py          # The pump's hot-water start condition: which planned charges it starts
+├── dhw_charges.py        # The plan committed as charges that run at the pump's floor or above
 ├── batchmath.py          # The batched row reduction every batch twin owes its scalar
 ├── process_worker.py     # One-shot interpreter for GIL-bound solves
 ├── open_meteo.py         # Irradiance forecast and satellite observation client
@@ -184,6 +185,7 @@ custom_components/heatpump_optimizer/
 ├── learning_freeze.py    # The one freeze predicate: which interval a learner
 │                         #   may ingest, by the kind of sample it folds
 ├── draw_range.py         # The metered running draw, and the range it clamps a plan to
+├── approach.py           # The draw by age after a space run's entry and end (Bankaifan)
 ├── diagnosis.py          # One-input-at-a-time attribution of the last interval's error
 ├── drift.py              # The CUSUM primitive shared by every drift detector
 ├── snapshots.py          # Weekly learner snapshots and the rollback alarm
diff --git a/tests/closures.json b/tests/closures.json
index 5e1d7a268c..15d3ea2c44 100644
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
@@ -324,9 +326,11 @@
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
@@ -369,6 +373,7 @@
   "tests/block_duty.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -389,6 +394,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -505,6 +511,7 @@
   "tests/boost_drift_replay.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -518,6 +525,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -623,6 +631,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -636,6 +645,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -755,6 +765,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -768,6 +779,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -883,6 +895,7 @@
   "tests/config_flow_steps.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -903,6 +916,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1038,6 +1052,7 @@
   "tests/cycle_lane.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1051,6 +1066,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1154,6 +1170,7 @@
   "tests/debug_collect.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1169,6 +1186,7 @@
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1281,6 +1299,7 @@
   "tests/deployment_shape.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1309,6 +1328,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1441,6 +1461,7 @@
    "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1461,6 +1482,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -1738,9 +1760,11 @@
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
@@ -1835,6 +1859,7 @@
    "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -1863,6 +1888,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2394,6 +2420,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2422,6 +2449,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2614,6 +2642,7 @@
    "blueprints/automation/notifications.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2634,6 +2663,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2784,6 +2814,7 @@
   "tests/finite_boundary.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2804,6 +2835,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -2935,6 +2967,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -2963,6 +2996,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3156,6 +3190,7 @@
   "tests/guard_pins.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3169,6 +3204,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3333,6 +3369,7 @@
    "VERSION",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3353,6 +3390,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3749,6 +3787,7 @@
   "tests/manual_plan.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3765,6 +3804,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -3900,9 +3940,11 @@
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
@@ -3945,6 +3987,7 @@
   "tests/plan_view.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -3958,6 +4001,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4064,6 +4108,7 @@
   "tests/solar_alignment.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4077,6 +4122,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4179,9 +4225,11 @@
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
@@ -4229,6 +4277,7 @@
   "tests/structure.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4249,6 +4298,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4340,6 +4390,7 @@
   "tests/typing_ruler.py": [
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4360,6 +4411,7 @@
    "custom_components/heatpump_optimizer/debugger.py",
    "custom_components/heatpump_optimizer/defrost.py",
    "custom_components/heatpump_optimizer/device_prefill.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -4451,9 +4503,11 @@
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
@@ -4495,6 +4549,7 @@
    "blueprints/automation/notify_wood_cheaper_window.yaml",
    "custom_components/heatpump_optimizer/__init__.py",
    "custom_components/heatpump_optimizer/accuracy.py",
+   "custom_components/heatpump_optimizer/approach.py",
    "custom_components/heatpump_optimizer/away.py",
    "custom_components/heatpump_optimizer/batchmath.py",
    "custom_components/heatpump_optimizer/battery.py",
@@ -4509,6 +4564,7 @@
    "custom_components/heatpump_optimizer/currency.py",
    "custom_components/heatpump_optimizer/curve_learning.py",
    "custom_components/heatpump_optimizer/defrost.py",
+   "custom_components/heatpump_optimizer/dhw_charges.py",
    "custom_components/heatpump_optimizer/dhw_draws.py",
    "custom_components/heatpump_optimizer/dhw_learning.py",
    "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -5024,6 +5080,7 @@
    "dev/audit/harnesses/r11_fast_shards_mutants.py",
    "dev/audit/harnesses/r11_fast_shards_random.sh",
    "dev/audit/harnesses/r11_fast_shards_readers.py",
+   "dev/audit/harnesses/r11_honest_dhw_runs.py",
    "dev/audit/harnesses/r11_honest_starts_runs.py",
    "dev/audit/harnesses/r11_kernel_step_agree.py",
    "dev/audit/harnesses/r11_main_cancel_mutants.py",
@@ -6396,7 +6453,7 @@
    "seconds": 60.2
   },
   "tests/entities.py": {
-   "rc": 0,
+   "rc": 1,
    "seconds": 1067.1
   },
   "tests/env_drift.py": {
@@ -6404,11 +6461,11 @@
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
@@ -6421,14 +6478,14 @@
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
    "seconds": 320.0
   },
   "tests/layout.py": {
diff --git a/tests/entities.py b/tests/entities.py
index 8911ccba36..79d6bbe37e 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4225,8 +4225,6 @@ def _p2_registry(sources):
                      "an elapsed time in hours (the pairing window's lower edge), not a power",
                  "dhw_learning.py::DhwProfileLearner.async_learn_usage":
                      "a tank draw intensity in K/h, not a power",
-                 "dhw_planner.py::DhwPlanner._dhw_shortfall":
-                     "a tank temperature gap in K, not a power",
                  "ledger.py::freeze_month_report":
                      "a month-report reconciliation tolerance in kWh and SEK, not a power",
                  "narrative.py::build":
diff --git a/tests/features.py b/tests/features.py
index c8644d7cf5..0ce51f5de4 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -12476,7 +12476,9 @@ _ct_blind = [n.lineno for n in _ct_walk_calls
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
@@ -34989,6 +34991,7 @@ class _Split:
         self._measured_power = measured
         self._immersion_active = False
         self._pump_signals = signals
+        self._accuracy = AccuracyTracker()  # R11-OUTSIDE-START-APPROACH: the tracking gate reads its draw window
 
 
 _sp_blind = _Split(PumpSignals())
@@ -82651,7 +82654,7 @@ def _wrr_folded(command, experiment_s=None):
     """A fresh store after one running 3.0 kW space interval held at ``command``."""
     d = _dr.DrawRange()
     _dr.fold(d, 3.0, (5.0, 0.0), _dr_params(1.5, 5.5), frozen=False, distorted=False,
-             defrost=False, command=command, experiment_s=experiment_s)
+             defrost=False, command=command, span=None if experiment_s is None else _dr.Span(experiment_s, experiment_s, experiment=True))
     return d
 
 
@@ -92655,7 +92658,7 @@ def _cp_params(lo=1.0, hi=5.0):
 
 def _cp_fold(d, drawn, command, experiment_s, split=(5.0, 0.0), hi=5.0):
     _cp_dr.fold(d, drawn, split, _cp_params(hi=hi), frozen=False, distorted=False,
-                defrost=False, command=command, experiment_s=experiment_s)
+                defrost=False, command=command, span=None if experiment_s is None else _cp_dr.Span(experiment_s, experiment_s, experiment=True))
 
 
 def _cp_store(values, newest_s=_CP_NOW):
@@ -93106,7 +93109,7 @@ def _cp_pump(house, nights, late=False, noise=0.02, seed=3):
                 drawn = (3.0 if pending["command"] is _CP_CEIL else 1.5) * (1.0 + noise * rng.standard_normal())
                 _cp_dr.fold(store, drawn, (pending["power"], 0.0), _cp_params(), frozen=False,
                             distorted=False, defrost=False, command=pending["command"],
-                            experiment_s=pending["when"] if key == "system_identification" else None)
+                            span=_cp_dr.Span(pending["when"], pending["when"], experiment=True) if key == "system_identification" else None)
             pending = {"mode": mode, "power": power, "when": now.timestamp(),
                        "command": _CP_CEIL if power >= 5.0 else _CP_MID}
             prev_mode = mode
@@ -96769,6 +96772,7 @@ R.check(
     "a plausible target raised a notice",
 )
 
+# --- R10-DUTY-SWITCH-PLANNER-PRICE block start
 R.section(
     "R10-DUTY-SWITCH-PLANNER-PRICE: the planner prices a duty switch that stops "
     "the compressor (pull request 3420, Bankaifan)"
@@ -97356,10 +97360,12 @@ def _dsp_same_plan(a, b):
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
@@ -98572,12 +98578,16 @@ R.check(
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
 
@@ -98605,18 +98615,68 @@ def _dsp_arm(arm, **kw):
 
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
@@ -100658,6 +100718,789 @@ R.check(
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
+# 2d. A charge at the first step (#3863's start rule, dhw_start): the commit
+# judges it as the floor repair does. On a tank at its start temperature it
+# starts only while a charge is under way (ThermalState.dhw_charge_under_way);
+# commit_charges hands that reading to the acceptance and to the program's
+# start mask. Null: under way, the same charge passes. Called without the
+# reading, both take a charge to be under way, as dhw_start's functions do.
+_hdr_d0_plan = np.zeros(8)
+_hdr_d0_plan[0] = 2.0
+_hdr_d0_walk = np.array([52.0, 54.0, 53.8, 53.6, 53.4, 53.2, 53.0, 52.8, 52.6])
+_hdr_d0 = [
+    _hdr_dc.charge_refusal(_hdr_d0_plan, np.full(8, 51.0), lambda _p: _hdr_d0_walk, np.full(8, -np.inf), running)
+    for running in (False, True)
+] + [_hdr_dc.charge_refusal(_hdr_d0_plan, np.full(8, 51.0), lambda _p: _hdr_d0_walk, np.full(8, -np.inf))]
+_hdr_d0_rig = _hdr_rig(t0=52.0)
+_hdr_d0_seen = []
+_hdr_d0_kept = (_hdr_dc.charge_refusal, _hdr_dc.startable_steps)
+_hdr_dc.charge_refusal = lambda *a: _hdr_d0_seen.append(("refusal", a[4:])) or _hdr_d0_kept[0](*a)
+_hdr_dc.startable_steps = lambda *a: _hdr_d0_seen.append(("mask", a[3:])) or _hdr_d0_kept[1](*a)
+try:
+    for _hdr_d0_running in ((False,), (True,), ()):
+        _hdr_d0_seen.append(("run", _hdr_d0_running))
+        _hdr_dc.commit_charges(
+            _hdr_d0_rig.planner, np.where(np.arange(_HDR_N) < 2, 0.6, 0.0), (_hdr_d0_rig.ctx, *_hdr_d0_rig.tank),
+            (np.full(_HDR_N, 45.0), np.full(_HDR_N, 55.0)), None, np.full(_HDR_N, 51.0), None, *_hdr_d0_running)
+finally:
+    _hdr_dc.charge_refusal, _hdr_dc.startable_steps = _hdr_d0_kept
+R.check(
+    "a charge at the first step on a tank at its start temperature is refused for its start unless a "
+    "charge is under way, and the commit hands that reading to the acceptance and the program's start mask",
+    _hdr_d0 == [("start", 0), None, None]
+    and set(_hdr_d0_seen[_hdr_d0_seen.index(("run", (False,))) + 1 : _hdr_d0_seen.index(("run", (True,)))])
+    == {("refusal", (False,)), ("mask", (False,))}
+    and set(_hdr_d0_seen[_hdr_d0_seen.index(("run", (True,))) + 1 :]) - {("run", ())}
+    == {("refusal", (True,)), ("mask", (True,))},
+    f"{_hdr_d0}, {sorted(set(_hdr_d0_seen))}",
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
+def _hdr_combi(cost, slack=None, plans=None):
+    opt = _StoreOpt(ThermalModel(_ct_params()), _StoreCfg(
+        horizon_hours=24, time_step_minutes=15, target_temp=21.0, min_temp=19.0, max_temp=23.0, cycling_cost=cost))
+    real, saved, calls = _hdr_om._combi_flux_exchange, _hdr_om._COMBI_COMMIT_SLACK_K, []
+    dhw_build = _hdr_om._dhw_build
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
+            def handed(by, *a, **k):
+                got, req = dhw_build(by, *a, **k)
+                return SimpleNamespace(schedule=plans(len(builds), np.asarray(got.schedule))), req
+
+            DhwPlanner._build_dhw_requirements, planner.charge_runs = counted, runs_planned
+            if plans is not None:
+                _hdr_om._dhw_build = handed
+            try:
+                out = real(o, h, planner, *rest)
+            finally:
+                DhwPlanner._build_dhw_requirements, planner.charge_runs = build, charge
+                _hdr_om._dhw_build = dhw_build
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
+# Whether a real solve's exchange settles before the cap is the solver's
+# arithmetic: the unengaged solve above stops short of it on one BLAS build
+# and oscillates to it on another (round-to-round moves of 4.0, 4.0 and
+# 0.6 kW). The exit is pinned on builds the check hands the rounds instead:
+# one plan built again and again repeats from the second round, and a plan
+# that alternates never repeats, so only the exit tells the two apart.
+_hdr_x_same = _hdr_combi(0.0, plans=lambda n, built: np.full(built.shape, 1.0))[0]
+_hdr_x_flip = _hdr_combi(0.0, plans=lambda n, built: np.full(built.shape, 1.0 + n % 2))[0]
+R.check(
+    "combi: the exchange leaves its rounds when a round's plan repeats the one before: a build that "
+    "repeats stops short of the cap, one that alternates runs to it",
+    0 < len(_hdr_x_same.rounds) <= 2 < len(_hdr_x_flip.rounds) == _hdr_om._COMBI_EXCHANGE_ROUNDS,
+    f"repeating {len(_hdr_x_same.rounds)}, alternating {len(_hdr_x_flip.rounds)} of {_hdr_om._COMBI_EXCHANGE_ROUNDS}",
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
@@ -100953,7 +101796,7 @@ R.check(
     and _mf_set_attrs == _mf_cfg_attrs
     and _mf_min_attrs == {
         "pump_min_power": {"configured_min_kw": 0.53, "planned_min_kw": 1.1,
-                           "learned_min_kw": 1.1, "samples": 0},
+                           "learned_min_kw": 1.1, "samples": 0, "approach_kwh": None},
         "pump_min_power_source": "metered", "pump_min_power_reason": "measured"}
     and _mf_sensor._pump_min_power(_mf_within.as_dict())["pump_min_power"]["samples"]
     == _mf_within.min_samples != _mf_within.samples
@@ -101070,6 +101913,244 @@ R.check(
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
@@ -104262,7 +105343,7 @@ def _cf_fold(drawn, floor_kw=None):
     frozen = _lf.reason(_lf.Facts(), (), _LF_K.CEILING,
                         _lf.Evidence(at_running_floor=_cf_dr.at_running_floor(d, drawn))) is not None
     _cf_dr.fold(d, drawn, (6.0, 0.0), _CF_P, frozen=False, distorted=False, defrost=False,
-                command=_CF_CEIL, experiment_s=1.0e9, ceiling_frozen=frozen)
+                command=_CF_CEIL, span=_cf_dr.Span(1.0e9, 1.0e9, experiment=True), ceiling_frozen=frozen)
     return frozen, len(d.ceiling), len(d.samples) - window
 
 
@@ -104806,6 +105887,474 @@ R.check(
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
+# 8. The solve's wiring. Both coordinator roads into the optimizer are the
+# scheduled record and the what-if scratch solve. Each hands SolveInputs the
+# profile draw_range.solve_approach reads off the coordinator's own window,
+# for that road's params, at the solve's instant. The optimizer prices that
+# field (inputs.approach) and nothing else. Null: a coordinator that learned
+# no runs hands None on both roads.
+from heatpump_optimizer import whatif as _sa_whatif  # noqa: E402
+from heatpump_optimizer.plan_step import plan_step_start as _sa_pss  # noqa: E402
+
+
+def _sa_roads(c):
+    """The approach each solve road hands the optimizer, each beside
+    solve_approach's own answer for that road's params at that instant."""
+    now = _sa_pss(dt_util.now())
+    horizon = c._forecast_arrays(now)
+    rec = c._solve_record(now, horizon)
+    config, params, state = c._solve_hubs(len(horizon.prices), banded=False)
+    w_inputs = c._whatif_solve({}, config, params, state, horizon, now, False)[1]
+    w_params = _sa_whatif.scratch_copies(config, params, {})[1]
+    return (rec.inputs.approach, _sa_dr.solve_approach(c._accuracy.draw, rec.params, now.timestamp()),
+            w_inputs.approach, _sa_dr.solve_approach(c._accuracy.draw, w_params, now.timestamp()))
+
+
+def _sa_same(a, b):
+    """Two profiles agree field by field, neither absent."""
+    return (a is not None and b is not None and np.array_equal(a.entry, b.entry)
+            and np.array_equal(a.ramp, b.ramp) and a.age_h == b.age_h and a.bin_h == b.bin_h)
+
+
+_sa_w1, _sa_w0 = _sa_roads(_sa_c1), _sa_roads(_sa_c0)
+R.check(
+    "the scheduled solve record and the what-if scratch solve hand the optimizer the approach solve_approach "
+    "reads off the coordinator's window at the solve's instant, a profile with entry levels; null: the "
+    "coordinator that learned no runs hands None on both roads",
+    _sa_same(_sa_w1[0], _sa_w1[1]) and _sa_same(_sa_w1[2], _sa_w1[3]) and _sa_w1[0].entry.size > 0
+    and _sa_w0 == (None, None, None, None),
+    f"record {_sa_w1[0]} want {_sa_w1[1]}; what-if {_sa_w1[2]} want {_sa_w1[3]}; null {_sa_w0}",
+)
+
 # R11-SEAM-store-p2 (round-11 sweep P1, store loaders): a stored flag where a number is declared.
 # Python counts ``True`` as an int, so six loaders admitted a stored ``true`` as
 # 1.0. The store's load boundary reads it as absent, by the store's DOMAINS
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 610597bd75..c31e88878f 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -67,6 +67,8 @@
 # v10.1.7: Unread state deleted; round-11 mutant kills pinned. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
+cycling_cost  # R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed as runs: hot-water steps under the floor 14 -> 0, combined draw 11 -> 0, charges 9 -> 3, starts 4 -> 3, energy 40.97 -> 42.45 kWh, predicted_cost 32.07 -> 33.76 (up: the committed charges buy what the trickles under the floor did not), worst gap under the hot-water requirement 0.557 -> 0.439 K
+everything_on  # R11-OUTSIDE-HONEST-DHW-RUNS: hot-water charges committed as runs: hot-water steps under the floor 10 -> 0, combined draw 4 -> 0, charges 5 -> 3, starts 4 -> 3, energy 67.09 -> 66.48 kWh, predicted_cost 60.71 -> 60.39 (down), worst gap under the hot-water requirement 0.550 -> 0.438 K
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
@@ -117,13 +119,15 @@
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
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
deleted file mode 100644
index 7e0808e417..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c294c9b7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c294c9b7",
-  "killed_by": "tests/features.py",
-  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw, experiment):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
-}
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
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
similarity index 51%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
rename to tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
index bd324872f3..d942d4aade 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.ac9b3721.json
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/charge_refusal.GUARD_OFF.4763baed.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF ac9b3721",
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:charge_refusal GUARD_OFF 4763baed",
   "killed_by": "tests/features.py",
-  "old": "        if experiment:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+  "old": "    if start_below is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
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
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.33f4dbe6.json b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.33f4dbe6.json
new file mode 100644
index 0000000000..8a3ade8608
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/commit_charges.fits.RETURN_DEL.33f4dbe6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:commit_charges.fits RETURN_DEL 33f4dbe6",
+  "killed_by": "tests/features.py",
+  "old": "        return charge_refusal(candidate, start_below, temps_of, held, charge_running) or candidate",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=19."
+}
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
diff --git a/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
new file mode 100644
index 0000000000..82d3290dba
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_charges.py/whole_charges.GUARD_OFF.cbabd675.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_charges.py:whole_charges GUARD_OFF cbabd675",
+  "killed_by": "tests/features.py",
+  "old": "    if charge_runs is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
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
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.d042d302.json b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
similarity index 89%
rename from tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.d042d302.json
rename to tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
index bae72c78be..8271995631 100644
--- a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.d042d302.json
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_fold_window.GUARD_OFF.d042d302.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF d042d302",
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_fold_window GUARD_OFF d042d302",
   "killed_by": "tests/features.py",
   "old": "        if not ceiling_frozen:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
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
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 6363b1e4b1..e374181a04 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17191,
+ "class_excess_loc": 17186,
  "const_modules_over_50": 4,
  "coordinator_attrs": 133,
  "coordinator_multiassigned_attrs": 100,
@@ -10,13 +10,13 @@
  "functions_cc_over_15": 26,
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
- "in_function_copies": 11,
+ "in_function_copies": 10,
  "max_cc": 44,
  "max_class_loc": 7753,
  "max_method_loc": 373,
  "methods_over_150": 14,
- "methods_over_200": 7,
- "module_excess_loc": 21598,
+ "methods_over_200": 6,
+ "module_excess_loc": 21647,
  "name_kept_members": 38,
  "recorded_at": "e84856520dc4de8d70b68d67a206c6f2278351ad",
  "seam_cut_total": 413,
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 85f658791d..804445d786 100644
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
@@ -4278,6 +4279,7 @@
     "tests/mutation_ledger/killed_by/debugger.py",
     "tests/mutation_ledger/killed_by/defrost.py",
     "tests/mutation_ledger/killed_by/device_prefill.py",
+    "tests/mutation_ledger/killed_by/dhw_charges.py",
     "tests/mutation_ledger/killed_by/dhw_draws.py",
     "tests/mutation_ledger/killed_by/dhw_learning.py",
     "tests/mutation_ledger/killed_by/dhw_planner.py",
@@ -4365,6 +4367,7 @@
     "tests/mutation_ledger/survivor_triage/coordinator.py",
     "tests/mutation_ledger/survivor_triage/currency.py",
     "tests/mutation_ledger/survivor_triage/debugger.py",
+    "tests/mutation_ledger/survivor_triage/dhw_charges.py",
     "tests/mutation_ledger/survivor_triage/dhw_planner.py",
     "tests/mutation_ledger/survivor_triage/dhw_schedule.py",
     "tests/mutation_ledger/survivor_triage/draw_range.py",
@@ -9032,6 +9035,7 @@
     "tests/mutation_ledger/killed_by/debugger.py",
     "tests/mutation_ledger/killed_by/defrost.py",
     "tests/mutation_ledger/killed_by/device_prefill.py",
+    "tests/mutation_ledger/killed_by/dhw_charges.py",
     "tests/mutation_ledger/killed_by/dhw_draws.py",
     "tests/mutation_ledger/killed_by/dhw_learning.py",
     "tests/mutation_ledger/killed_by/dhw_planner.py",
@@ -9119,6 +9123,7 @@
     "tests/mutation_ledger/survivor_triage/coordinator.py",
     "tests/mutation_ledger/survivor_triage/currency.py",
     "tests/mutation_ledger/survivor_triage/debugger.py",
+    "tests/mutation_ledger/survivor_triage/dhw_charges.py",
     "tests/mutation_ledger/survivor_triage/dhw_planner.py",
     "tests/mutation_ledger/survivor_triage/dhw_schedule.py",
     "tests/mutation_ledger/survivor_triage/draw_range.py",
@@ -9558,6 +9563,7 @@
     "custom_components/heatpump_optimizer/datetime.py",
     "custom_components/heatpump_optimizer/debugger.py",
     "custom_components/heatpump_optimizer/defrost.py",
+    "custom_components/heatpump_optimizer/dhw_charges.py",
     "custom_components/heatpump_optimizer/dhw_draws.py",
     "custom_components/heatpump_optimizer/dhw_learning.py",
     "custom_components/heatpump_optimizer/dhw_planner.py",
@@ -10301,6 +10307,7 @@
     "tests/mutation_ledger/killed_by/debugger.py",
     "tests/mutation_ledger/killed_by/defrost.py",
     "tests/mutation_ledger/killed_by/device_prefill.py",
+    "tests/mutation_ledger/killed_by/dhw_charges.py",
     "tests/mutation_ledger/killed_by/dhw_draws.py",
     "tests/mutation_ledger/killed_by/dhw_learning.py",
     "tests/mutation_ledger/killed_by/dhw_planner.py",
@@ -10388,6 +10395,7 @@
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
