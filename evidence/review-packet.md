# Review packet #3481
head: 70ef3055363512123e9e6f8e5632831830d31dbb
base: c987209cc7a891e0e4066d4ad8dc5cf55357c5ae

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132309248816 neutral
arch-score / arch-score id=132308322062 queued
arm id=132307405395 skipped
budget-raise-gate / budget-raise-gate id=132308321880 success
cancel-superseded id=132307405261 queued
codeql / Analyze (actions) id=132308321921 success
codeql / Analyze (javascript-typescript) id=132308321925 success
codeql / Analyze (python) id=132308321986 in_progress
governance / delivery-status id=132308321963 success
governance / delivery-status-publish id=132308323109 skipped
governance / env-matrix id=132308321926 in_progress
governance / instrument-self-tests id=132308322001 in_progress
governance / policy-docs id=132308322045 in_progress
governance / record id=132308323258 skipped
governance / wave-script id=132308321890 success
hassfest / hassfest id=132308321911 success
kernel-points id=132308323229 skipped
prelude id=132307405570 queued
refresh id=132307405590 queued
tests / arch-instrument id=132308580123 queued
tests / briefs id=132308321979 queued
tests / browser id=132308580198 queued
tests / closure-scope id=132308322037 success
tests / closures id=132308580191 queued
tests / coverage id=132308580172 queued
tests / fast (3.14) id=132308580225 queued
tests / mutation id=132308321907 failure
tests / mutation-pins (1) id=132308642972 queued
tests / mutation-pins (2) id=132308642743 queued
tests / nightly-ha id=132308582151 skipped
tests / nightly-status id=132308322036 queued
tests / replay id=132308580286 queued
tests / typing id=132308580192 queued
validate / validate-hacs id=132308321840 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132308322001: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 4c71fdf6: R11-INTAKE-R10-RESIDUE
NOTE body item b1063d93: R11-INTAKE-R10-RESIDUE
NOTE body item 2c18d19e: dismissed:disclosed in the docs paragraph, the option the design offered
NOTE body item 9b2740c4: R11-INTAKE-R10-RESIDUE
NOTE body item 7e175b79: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 5 finding item(s): 5 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff e23124ff6
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py
             `dev/audit/rounds/round4/D6/claims.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_seams.py fields
             `dev/audit/harnesses/r10_advisor_steady_seams.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         python3 tests/closure.py select --diff 154dbb4c6
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests python3 dev/audit/harnesses/r10_advisor_steady_bracket.py
             `dev/audit/harnesses/r10_advisor_steady_bracket.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_seams.py
             `dev/audit/harnesses/r10_advisor_steady_seams.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/replay.py
             `tests/replay.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/replay.py --fixture tests/replay/synthetic-dhw-only.json
             `tests/replay.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_seams.py [arm]
             `dev/audit/harnesses/r10_advisor_steady_seams.py` is in the tree at this head
  ok         tests/replay.py --one tests/replay/owner-2026-10-30-away.json
             `tests/replay.py` is in the tree at this head
  ok         PRICES=<series> OUTDOOR=<series> PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_bracket.py
             `dev/audit/harnesses/r10_advisor_steady_bracket.py` is in the tree at this head
  ok         AGE=<a> STEP=<s> PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_carrier.py
             `dev/audit/harnesses/r10_advisor_steady_carrier.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py whatif
             `dev/audit/harnesses/r10_advisor_residue.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:tests:custom_components python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/dst_checks.py
             `tests/dst_checks.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff ee64358be7eeccaec5178a923cb3b83a18a924a0
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 28 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._whatif_solve.GUARD_OFF.0816b83e.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._whatif_solve.GUARD_OFF.0816b83e.json
new file mode 100644
index 0000000000..514cfb251d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._whatif_solve.GUARD_OFF.0816b83e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._whatif_solve GUARD_OFF 0816b83e",
+  "killed_by": "tests/features.py",
+  "old": "        if \"power_cap_kw\" in overrides:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._whatif_solve.GUARD_OFF.64a65939.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._whatif_solve.GUARD_OFF.64a65939.json
new file mode 100644
index 0000000000..8944abfb7e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._whatif_solve.GUARD_OFF.64a65939.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._whatif_solve GUARD_OFF 64a65939",
+  "killed_by": "tests/features.py",
+  "old": "        if wood_err:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json
new file mode 100644
index 0000000000..970af6401d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.1550d375.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 1550d375",
+  "killed_by": "tests/features.py",
+  "old": "        ) if steady and days is None else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`) if steady or days is None else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json
new file mode 100644
index 0000000000..8a9575432a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.19646b85.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 19646b85",
+  "killed_by": "tests/features.py",
+  "old": "        banded = base is None and _whatif_banded(self._away_state)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`banded = base is None or _whatif_banded(self._away_state)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json
new file mode 100644
index 0000000000..0dafcbf4ce
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.BOOLOP.6e295277.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate BOOLOP 6e295277",
+  "killed_by": "tests/features.py",
+  "old": "        if limited and (kept := whatif.limited_answer(held, now)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if limited or (kept := whatif.limited_answer(held, now)) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.1b39ddc8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.1b39ddc8.json
deleted file mode 100644
index 0e29bc1adb..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.1b39ddc8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 1b39ddc8",
-  "killed_by": "tests/features.py",
-  "old": "        if \"dhw_windows\" in overrides:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json
new file mode 100644
index 0000000000..99ee505c09
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.6e295277.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF 6e295277",
+  "killed_by": "tests/structure.py",
+  "old": "        if limited and (kept := whatif.limited_answer(held, now)) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.eb71d2bd.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.eb71d2bd.json
deleted file mode 100644
index 34870144d5..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.GUARD_OFF.eb71d2bd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate GUARD_OFF eb71d2bd",
-  "killed_by": "tests/features.py",
-  "old": "            if key in overrides:",
-  "reason": "Recorded by `mutation_table.py --drain` against 59b76606e0190139eecc8496607687a87cb05054: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json
new file mode 100644
index 0000000000..862c349716
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_simulate.RETURN_DEL.c0eb7824~2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_simulate RETURN_DEL c0eb7824#2",
+  "killed_by": "tests/features.py",
+  "old": "            return {\"error\": str(err), \"rate_limited\": False}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.0f9db465.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.0f9db465.json
new file mode 100644
index 0000000000..9750875ad7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.0f9db465.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.optimize GUARD_OFF 0f9db465",
+  "killed_by": "tests/features.py",
+  "old": "        if inputs.held_start:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.fbb59803.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.fbb59803.json
deleted file mode 100644
index 09a1924b5e..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.fbb59803.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.optimize GUARD_OFF fbb59803",
-  "killed_by": "tests/features.py",
-  "old": "        if external_heat_kw is not None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.BOOLOP.dcbeb653.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.BOOLOP.dcbeb653.json
new file mode 100644
index 0000000000..bc0dc45cc4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.BOOLOP.dcbeb653.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.reference_day BOOLOP dcbeb653",
+  "killed_by": "tests/features.py",
+  "old": "            if day * dt >= 24.0 and targets not in day_kwh:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if day * dt >= 24.0 or targets not in day_kwh:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CLAMP_DROP.b9947f73.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CLAMP_DROP.b9947f73.json
new file mode 100644
index 0000000000..569b2ca789
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CLAMP_DROP.b9947f73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.reference_day CLAMP_DROP b9947f73",
+  "killed_by": "tests/features.py",
+  "old": "        n_steps = min(len(series.prices), len(series.outdoor_temps), self.config.n_steps)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`n_steps = (len(series.prices))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CLAMP_DROP.cbe42979.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CLAMP_DROP.cbe42979.json
new file mode 100644
index 0000000000..1c6b6181be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CLAMP_DROP.cbe42979.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.reference_day CLAMP_DROP cbe42979",
+  "killed_by": "tests/features.py",
+  "old": "        day = min(n_steps, int(round(24.0 / dt)))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`day = (n_steps)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CMP_BOUND.dcbeb653.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CMP_BOUND.dcbeb653.json
new file mode 100644
index 0000000000..41c7c9981a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.CMP_BOUND.dcbeb653.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.reference_day CMP_BOUND dcbeb653",
+  "killed_by": "tests/features.py",
+  "old": "            if day * dt >= 24.0 and targets not in day_kwh:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if day * dt > 24.0 and targets not in day_kwh:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.GUARD_OFF.dcbeb653.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.GUARD_OFF.dcbeb653.json
new file mode 100644
index 0000000000..5bc2449496
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.GUARD_OFF.dcbeb653.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.reference_day GUARD_OFF dcbeb653",
+  "killed_by": "tests/features.py",
+  "old": "            if day * dt >= 24.0 and targets not in day_kwh:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.RETURN_DEL.5b1941e5.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.RETURN_DEL.5b1941e5.json
new file mode 100644
index 0000000000..1cc7015ca5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.reference_day.RETURN_DEL.5b1941e5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.reference_day RETURN_DEL 5b1941e5",
+  "killed_by": "tests/features.py",
+  "old": "        return week, sum(day_kwh.get(tuple(week[k:k + day]), math.nan) for k in range(0, 7 * day, day)) / 7.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_day_mean_weather.flat.GUARD_OFF.83e9a6c1.json b/tests/mutation_ledger/killed_by/optimizer.py/_day_mean_weather.flat.GUARD_OFF.83e9a6c1.json
new file mode 100644
index 0000000000..8128ab5e9f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_day_mean_weather.flat.GUARD_OFF.83e9a6c1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_day_mean_weather.flat GUARD_OFF 83e9a6c1",
+  "killed_by": "tests/features.py",
+  "old": "        if values is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_day_mean_weather.flat.RETURN_DEL.bb2ac37d.json b/tests/mutation_ledger/killed_by/optimizer.py/_day_mean_weather.flat.RETURN_DEL.bb2ac37d.json
new file mode 100644
index 0000000000..323d19c61e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_day_mean_weather.flat.RETURN_DEL.bb2ac37d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_day_mean_weather.flat RETURN_DEL bb2ac37d",
+  "killed_by": "tests/features.py",
+  "old": "        return np.full(n_steps, float(np.mean(known)) if known.size else np.nan)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.CMP_BOUND.362ff97e.json b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.CMP_BOUND.362ff97e.json
new file mode 100644
index 0000000000..076a7c7aad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.CMP_BOUND.362ff97e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_horizon_weather CMP_BOUND 362ff97e",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.any(external_heat_kw > 0.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not np.any(external_heat_kw >= 0.0):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.094aad58.json b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.094aad58.json
new file mode 100644
index 0000000000..b822df43a5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.094aad58.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_horizon_weather GUARD_OFF 094aad58",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.any(np.isfinite(humidity)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.2b5657dc.json b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.2b5657dc.json
new file mode 100644
index 0000000000..43f3bb35ba
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.2b5657dc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_horizon_weather GUARD_OFF 2b5657dc",
+  "killed_by": "tests/features.py",
+  "old": "    if external_heat_kw is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.362ff97e.json b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.362ff97e.json
new file mode 100644
index 0000000000..ec8ca1041d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.362ff97e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_horizon_weather GUARD_OFF 362ff97e",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.any(external_heat_kw > 0.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.39006914.json b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.39006914.json
new file mode 100644
index 0000000000..ee2dd6eb85
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.39006914.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_horizon_weather GUARD_OFF 39006914",
+  "killed_by": "tests/features.py",
+  "old": "        if hum.size < n_steps:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.679f37e0.json b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.679f37e0.json
new file mode 100644
index 0000000000..0e547a327e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_horizon_weather.GUARD_OFF.679f37e0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_horizon_weather GUARD_OFF 679f37e0",
+  "killed_by": "tests/features.py",
+  "old": "    if humidity is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_step_clock.RETURN_DEL.0e0ac657.json b/tests/mutation_ledger/killed_by/optimizer.py/_step_clock.RETURN_DEL.0e0ac657.json
new file mode 100644
index 0000000000..1b8611ba07
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_step_clock.RETURN_DEL.0e0ac657.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_step_clock RETURN_DEL 0e0ac657",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return step_datetimes, np.array([d.hour + d.minute / 60.0 for d in step_datetimes])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/@module.CONST.1ac434f2.json b/tests/mutation_ledger/killed_by/price_tiles.py/@module.CONST.1ac434f2.json
new file mode 100644
index 0000000000..d3a7d35feb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/@module.CONST.1ac434f2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:<module> CONST 1ac434f2",
+  "killed_by": "tests/features.py",
+  "old": "STEADY_REFRESH_HOURS = 6.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`STEADY_REFRESH_HOURS = 12.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/realised_price.CMP_BOUND.3328d55d.json b/tests/mutation_ledger/killed_by/price_tiles.py/realised_price.CMP_BOUND.3328d55d.json
new file mode 100644
index 0000000000..342e6b0b73
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/realised_price.CMP_BOUND.3328d55d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:realised_price CMP_BOUND 3328d55d",
+  "killed_by": "tests/features.py",
+  "old": "    return float(result.predicted_cost) / kwh if kwh > 0.0 else math.nan",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return float(result.predicted_cost) / kwh if kwh >= 0.0 else math.nan`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/realised_price.RETURN_DEL.3328d55d.json b/tests/mutation_ledger/killed_by/price_tiles.py/realised_price.RETURN_DEL.3328d55d.json
new file mode 100644
index 0000000000..14a372b596
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/realised_price.RETURN_DEL.3328d55d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:realised_price RETURN_DEL 3328d55d",
+  "killed_by": "tests/features.py",
+  "old": "    return float(result.predicted_cost) / kwh if kwh > 0.0 else math.nan",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.BOOLOP.557f9e57.json b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.BOOLOP.557f9e57.json
new file mode 100644
index 0000000000..68016c51d4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.BOOLOP.557f9e57.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:schedule_figure BOOLOP 557f9e57",
+  "killed_by": "tests/features.py",
+  "old": "    priced = math.isfinite(shifted_price) and shifted_price > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`priced = math.isfinite(shifted_price) or shifted_price > 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.CMP_BOUND.557f9e57.json b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.CMP_BOUND.557f9e57.json
new file mode 100644
index 0000000000..d5c9a3ac96
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.CMP_BOUND.557f9e57.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:schedule_figure CMP_BOUND 557f9e57",
+  "killed_by": "tests/features.py",
+  "old": "    priced = math.isfinite(shifted_price) and shifted_price > 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`priced = math.isfinite(shifted_price) and shifted_price >= 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.GUARD_OFF.139172d0.json b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.GUARD_OFF.139172d0.json
new file mode 100644
index 0000000000..5a6aebc734
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.GUARD_OFF.139172d0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:schedule_figure GUARD_OFF 139172d0",
+  "killed_by": "tests/features.py",
+  "old": "    if not math.isfinite((sim_kwh - live_kwh) * mean_price):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.RETURN_DEL.9f21b160.json b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.RETURN_DEL.9f21b160.json
new file mode 100644
index 0000000000..5aaa86b74f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/schedule_figure.RETURN_DEL.9f21b160.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:schedule_figure RETURN_DEL 9f21b160",
+  "killed_by": "tests/structure.py",
+  "old": "    return {\"monthly_steady_cost_delta\": month(mean_price), SHIFTED_KEY: month(shifted_price) if priced else None}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/take.GUARD_OFF.708dc28c.json b/tests/mutation_ledger/killed_by/price_tiles.py/take.GUARD_OFF.708dc28c.json
new file mode 100644
index 0000000000..150ce3396d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/take.GUARD_OFF.708dc28c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:take GUARD_OFF 708dc28c",
+  "killed_by": "tests/features.py",
+  "old": "    if \"power_cap_kw\" in overrides:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/take.RETURN_DEL.36e2de4b.json b/tests/mutation_ledger/killed_by/price_tiles.py/take.RETURN_DEL.36e2de4b.json
deleted file mode 100644
index 51032064eb..0000000000
--- a/tests/mutation_ledger/killed_by/price_tiles.py/take.RETURN_DEL.36e2de4b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:take RETURN_DEL 36e2de4b",
-  "killed_by": "tests/features.py",
-  "old": "    return specs[cursor % len(specs)]",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against c5e1be1967de4b1d29b203aaf73162046dc85bd1: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/price_tiles.py/take.RETURN_DEL.67232359.json b/tests/mutation_ledger/killed_by/price_tiles.py/take.RETURN_DEL.67232359.json
new file mode 100644
index 0000000000..c164fca319
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/price_tiles.py/take.RETURN_DEL.67232359.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/price_tiles.py:take RETURN_DEL 67232359",
+  "killed_by": "tests/features.py",
+  "old": "    return name, overrides",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/schedule_days.RETURN_DEL.5d986d7f.json b/tests/mutation_ledger/killed_by/whatif.py/schedule_days.RETURN_DEL.5d986d7f.json
new file mode 100644
index 0000000000..3456bf4e31
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/schedule_days.RETURN_DEL.5d986d7f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:schedule_days RETURN_DEL 5d986d7f",
+  "killed_by": "tests/features.py",
+  "old": "    return None if live_targets == sim_targets else (live_kwh, sim_kwh)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.0d0ceab8.json b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.0d0ceab8.json
new file mode 100644
index 0000000000..56cb8a8409
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.0d0ceab8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:scratch_copies GUARD_OFF 0d0ceab8",
+  "killed_by": "tests/features.py",
+  "old": "        if key in overrides:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.0d0ceab8~2.json b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.0d0ceab8~2.json
new file mode 100644
index 0000000000..b40c93001a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.0d0ceab8~2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:scratch_copies GUARD_OFF 0d0ceab8#2",
+  "killed_by": "tests/features.py",
+  "old": "        if key in overrides:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.6d6bda25.json b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.6d6bda25.json
new file mode 100644
index 0000000000..5977353fdf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.GUARD_OFF.6d6bda25.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:scratch_copies GUARD_OFF 6d6bda25",
+  "killed_by": "tests/features.py",
+  "old": "    if \"dhw_windows\" in overrides:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.RETURN_DEL.1d248ed1.json b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.RETURN_DEL.1d248ed1.json
new file mode 100644
index 0000000000..d0fb3e31d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/scratch_copies.RETURN_DEL.1d248ed1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:scratch_copies RETURN_DEL 1d248ed1",
+  "killed_by": "tests/features.py",
+  "old": "    return scratch_config, scratch_params",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/steady_pair.GUARD_OFF.d4454575.json b/tests/mutation_ledger/killed_by/whatif.py/steady_pair.GUARD_OFF.d4454575.json
new file mode 100644
index 0000000000..622ae77c66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/steady_pair.GUARD_OFF.d4454575.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:steady_pair GUARD_OFF d4454575",
+  "killed_by": "tests/features.py",
+  "old": "        if kept is not None and kept[0] is anchor and kept[1] == key:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/steady_pair.RETURN_DEL.15fd7b46.json b/tests/mutation_ledger/killed_by/whatif.py/steady_pair.RETURN_DEL.15fd7b46.json
new file mode 100644
index 0000000000..46760ee8e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/steady_pair.RETURN_DEL.15fd7b46.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:steady_pair RETURN_DEL 15fd7b46",
+  "killed_by": "tests/features.py",
+  "old": "    return live, sim",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/whatif.py/steady_pair.RETURN_DEL.d7923b87.json b/tests/mutation_ledger/killed_by/whatif.py/steady_pair.RETURN_DEL.d7923b87.json
new file mode 100644
index 0000000000..cc39ec1d2f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/whatif.py/steady_pair.RETURN_DEL.d7923b87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:steady_pair RETURN_DEL d7923b87",
+  "killed_by": "tests/features.py",
+  "old": "        return None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.9ffd35ef.json b/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.9ffd35ef.json
deleted file mode 100644
index 296a9e29d8..0000000000
--- a/tests/mutation_ledger/survivor_triage/optimizer.py/HeatPumpOptimizer.optimize.GUARD_OFF.9ffd35ef.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.optimize GUARD_OFF 9ffd35ef",
-  "old": "            if not np.any(external_heat_kw > 0.0):",
-  "reason": "An all-zero free-heat forecast plans exactly as none: the guard only normalises zeros to None, and every downstream use adds the per-step value. Measured with the #1499 branch's probe (optimize() on the winter_cold / winter_typical profile, 12 h, space-only and with DHW): with the guard switched off, external_heat_kw=zeros and external_heat_kw=None give byte-identical power, DHW and room-temperature schedules and objective (sha1 prefixes 7a584e785045f9d5 and 31317c75945a2724 in both arms), while a 1 kW forecast moves both (c5b5e420dec7c4a8, 0204b401a95de984) -- the probe's null control that it can see free heat at all. Measured at 6c86f6ae, 2026-09-24.",
-  "verdict": "equivalent"
-}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_horizon_weather.CMP_BOUND.39006914.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_horizon_weather.CMP_BOUND.39006914.json
new file mode 100644
index 0000000000..929f319397
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_horizon_weather.CMP_BOUND.39006914.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_horizon_weather CMP_BOUND 39006914",
+  "old": "        if hum.size < n_steps:",
+  "reason": "Equivalent (CMP_BOUND, `<` to `<=`) in `_horizon_weather`: the only input the two tell apart is a humidity series exactly the horizon long, and there the branch appends `np.full(0, nan)`, an empty array, so the series is unchanged. Measured by python3 -c 'import numpy as np; h=np.array([1.,2.,3.,4.]); print(np.concatenate([h, np.full(0, np.nan)]).tolist())', which prints [1.0, 2.0, 3.0, 4.0]. The line's other operator (GUARD_OFF) is killed by tests/features.py, \"the horizon's weather, as every solve and reference_day read it\".",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/whatif.py/limited_answer.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/survivor_triage/whatif.py/limited_answer.RETURN_DEL.da9e8e97.json
new file mode 100644
index 0000000000..75533eb00e
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/whatif.py/limited_answer.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:limited_answer RETURN_DEL da9e8e97",
+  "old": "    return None",
+  "reason": "Equivalent (RETURN_DEL) in `limited_answer`: the mutated line is the function's last statement, `return None`; replaced by `pass` the function falls off its end and returns None all the same. The limited arm above it is pinned by tests/features.py, \"the user's slot is spent once\".",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/whatif.py/scratch_copies.GUARD_OFF.d061db3d.json b/tests/mutation_ledger/survivor_triage/whatif.py/scratch_copies.GUARD_OFF.d061db3d.json
new file mode 100644
index 0000000000..355acaadfe
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/whatif.py/scratch_copies.GUARD_OFF.d061db3d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/whatif.py:scratch_copies GUARD_OFF d061db3d",
+  "old": "        if not spec:",
+  "reason": "Equivalent (GUARD_OFF) in `scratch_copies`: with the guard off an empty `dhw_windows` spec goes to the parsers, and parse_windows('') is [] and parse_weekly_windows('') is None, the two values the guarded branch assigns; `spec` is already stripped. Measured by PYTHONPATH=tests/hastub:custom_components python3 -c 'from heatpump_optimizer.dhw_schedule import parse_windows, parse_weekly_windows; print(repr(parse_windows(\"\")), repr(parse_weekly_windows(\"\")))', which prints [] None. The guard stays for its comment: an empty schedule is a legitimate ask, not a parse error.",
+  "verdict": "equivalent"
+}


## Review scope: delta (later round over the reviewed head d712c2ba4a834afcb5d722468676d52ce3762681)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at d712c2ba4a834afcb5d722468676d52ce3762681
Fix review: blocked d712c2ba4a834afcb5d722468676d52ce3762681 ci-red: classify RED at the head, gate red; tests / fast (3.14) red on a features.py check main's own tree fails too

bus-nonce: b1a3df8bf73f585759b44a139c970262

Round 2 of the review (a delta review over the reviewed head 7c7f06081827bbf9c52da7b2345b3a5a81048649). Measured head d712c2ba4a834afcb5d722468676d52ce3762681. At 01:12Z it was still `refs/pull/3481/head`, and the body's `## Head` names it.

## Block

`python3 tools/audit/seat/merge_train.py classify d712c2ba4a834afcb5d722468676d52ce3762681 --pr 3481` printed WAIT from 00:56Z. At 01:23Z it changed to `RED d712c2ba4a834afcb5d722468676d52ce3762681 pending: none red: gate`, rc 1 (ev/classify.log). A red CI never carries a merge (fix-review.md step 12), so this verdict is a block. The code review found no defect.

The cause of the red, as far as this seat can read it:
- `tests / fast (3.14)` (job 132260951585, run 43534335461) concluded failure with `1 TEST SCRIPT(S) FAILED`. That check is in the `owed-reds` set. The job log the GitHub API returns is truncated to its last ~26 kB, so the failing script's name is not visible.
- On this container, tests/features.py at the head fails one real check: "a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked". It fails both in-tree (ev/features_intree_head.txt) and on a `git archive` copy (ev/features_ctl.txt).
- The same check fails the same way on a `git archive` copy of origin/main 50373173d (ev/features_main.txt). It came to main at 8fa60a926d, and this diff does not touch it (`git diff origin/main...d712c2ba -- tests/features.py | grep -c "charge-start dip"` prints 0).
- So the most likely red is main's, inherited through the merge, and not this branch's. That is not confirmed against CI's own log.
- `tests / mutation` (job 132259821824) also concluded failure. Its readable log tail shows only the shard setup (`count=2`), so the cause is unreadable here. `tests / mutation-pins (1)` was still in progress at 01:12Z.

Any one of these settles it:
- main's check is repaired and main is merged in again;
- the orchestrator confirms the fast red is main's and re-runs the lane;
- the gate goes green at this head.

A re-dispatch at an unchanged head needs only the live checks re-read. Every code finding below holds at d712c2ba.

## Findings

- main's tests/features.py check "a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked" fails at origin/main 50373173d on this container (3 of 5571 red on a `git archive` copy; the other two reds are copy artifacts, the #363 `recorded_at` and `_bootstrap` checks, which fail on every copy). It also fails in-tree at this head. Control to carry: run `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/features.py` at origin/main and read that title's line. A repair is shown red before it and green after. Whether CI's fast lane at this head fails on this check is not confirmed: the API log is truncated. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Setup: `cloud-setup.sh --check` printed OK. Role pack rendered. `git diff merge-base...origin/main -- dev/governance/roles/` is empty.
- Each prior finding:
  - The block (own-group carries 128b800e and c33b6f10) is resolved. The four design items are measured in this PR by dev/audit/harnesses/r10_advisor_steady_seams.py. weekday-day is fixed; pair-other-asks, measured-fields and pv-price are disclosed in docs/dashboard-card.md. The body's carries now read 5 to R11-INTAKE-R10-RESIDUE and 1 dismissed, and none names this group. `carry_audit.py check --body` gives 5 routed, 0 unrouted, 0 bad.
  - The stale `## Head` finding is resolved: the body now states that main is merged in.
- Delta, isolated from the main merges. `git merge-tree --write-tree origin/main 7c7f0608` builds the reviewed head on today's main. Its one conflict is optimizer.py, `_held_reference` beside main's `_held_unreachable`, and the head keeps both and changes nothing else in that hunk. Diffing that tree against d712c2ba's leaves 60 files. The production part is:
  - `reference_day`: the week loop.
  - `price_tiles.take`: the `Rotation` dataclass and the 6-hour steady clock.
  - the coordinator's None-spec return.
  - `whatif.state_for` as `setdefault`.
- The production review found no defect.
  - `reference_day` now calls `_build_comfort_bounds` with no margins or floors. The function's `[0]` return (comfort_targets) reads neither, so this changes nothing.
  - The only caller of `reference_day` is `whatif.schedule_days` (whatif.py:188), which compares setpoint lists element by element, so the week-length list is consistent there.
  - The cap tile's six-hour clock and the restart cost of up to six hours with no cap refresh are disclosed in the body and docs.
  - Nothing outside this was widened.
- Merge with main: `git merge-tree --write-tree origin/main d712c2ba` exits 0 (ev/merge_tree.txt).
- Step 5: `VERSION`, the manifest, `RELEASE_NOTES.md` and tests/golden/ are untouched (three-dot diff empty).
- Step 14: `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED (ev/structure.log). CI `arch-score / arch-score` and `budget-raise-gate` are success at this head.
- Step 1, mutation proof: tests/features.py whole, on `git archive` copies of the head. The control (no edit) has 3 reds: the copy's #363 `recorded_at` check, `_bootstrap`, and main's charge-start-dip check. Each mutant's extra reds over the control:
  - RESULT w1, the day offset dropped from `reference_day`'s step clock (seven copies of the asked day): +2, "#2257: with weekend temperatures the day energy is the week's average day ..." and "#2257: a weekend ask moves a setpoint on every weekday it is asked on ...".
  - RESULT w2, `reference_day` pricing the first day only (`range(1)`, divided by 1): +5, including "#2257: reference_day's setpoints open with ... a week of days", "a horizon under a day prices no day" and the two weekday checks.
  - RESULT t1, `take` not moving the stamp on a taken turn: +1, "#2257: the cap tile's steady pair is off the per-solve path ...".
  - RESULT t2, the first cap turn taken at once (stamp set 7 h back): +2, "a tile rotation: each degree tile is one solve ..." and the #2257 off-path check.
  - No survivor.
- Step 2 and the body's figures, re-derived with `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_steady_seams.py weekday fields` at the head (ev/seams_head_weekday_fields.log):
  - RESULT weekday with weekend comfort: 0 asks move with the weekday, 0 leave the schedule branch.
  - RESULT weekday null: 0 and 0.
  - RESULT weekday Friday sweep: 96 rows, 0 against the ask, 0 rounding to 0.00, 0 reading the pair.
  - RESULT fields, single-zone: holds 21.00, 0 against the ask.
  - RESULT fields, two-zone: holds 21.33, buffer moves 0.15 and 0.22.
  - RESULT fields, valve one tank: holds 19.88, 24 of 72 at 0 or against the ask.
  - RESULT fields, two-zone valve two-tank: holds 21.01, 0 against the ask.
  - Every null (same start) reads 0.00.
  - All of these match the body.
- The body's "before" figure (8 asks move with the weekday, 12 leave the branch) came from d120504a7, where this harness does not exist, so I did not re-derive it at that commit. I re-ran it on mutant w2, the head with `reference_day` restricted to the first day (ev/seams_mutant_firstday_weekday.log): 8 and 12, and the Friday sweep with 18 rounding to 0.00 and 6 reading the pair. That matches the body's before figures.
- Not re-run: the `pair` and `pv` arms, the bracket and carrier harnesses (unchanged since round 1's review, which re-ran them), tests/replay.py (CI `tests / replay` is success at this head) and card.mjs (CI fast lane).
- Step 11: `merge_train.py owed-reds` prints `tests / coverage-ratchet`, `tests / fast (3.14)`, `tests / mutation`, `tests / typing`, `validate / validate-hacs`.
  - At this head `tests / fast (3.14)` and `tests / mutation` are red. The body's Red checks section answers earlier runs of both, not these runs.
  - I make no root-cause-* call: not all of the head's workflows had concluded when I read them (`tests / mutation-pins (1)` was in progress), and the fast red reads as main's.
  - `tests / typing`, `validate / validate-hacs` and `tests / coverage-ratchet` are success.

## Delta diff: git diff d712c2ba4a834afcb5d722468676d52ce3762681 70ef3055363512123e9e6f8e5632831830d31dbb
diff --git a/RELEASE_NOTES.md b/RELEASE_NOTES.md
index 9f16af6fe3..3bb0dfe9d3 100644
--- a/RELEASE_NOTES.md
+++ b/RELEASE_NOTES.md
@@ -1,3 +1,27 @@
+## v7.1.16
+
+**Patch stamp: 13 merges since v7.1.15 (`git log --first-parent --merges --format=%h v7.1.15..HEAD | wc -l`): the hot-water and heating plans can take the pump's own start condition, the planner prices a hot-water to heating switch that stops the compressor, and the savings reference no longer books heat the pump could not deliver; the rest is tooling.**
+
+### #3531 The pump's start condition is an optional input per duty (R10-OUTSIDE-DHW-START-HYSTERESIS)
+
+With the new optional hot-water and heating hysteresis entities set, the plan no longer starts a charge on a tank at or above the pump's own start temperature, and buys back what the hot-water minimum still needs at steps where a charge can start. If the hot-water minimum is above that start temperature, a repair notice (`dhw_minimum_above_start`) says so. The heating flow floor never uses a lift below the heating hysteresis. Installs that leave the options unset plan as before. Based on outside pull request 3440 by Bankaifan.
+
+### #3526 The planner prices a duty switch that stops the compressor (R10-DUTY-SWITCH-PLANNER-PRICE)
+
+A switch between hot water and heating that the learner reports as stopping the compressor now carries a cost in the plan, including the running time the stop takes, and the planner tries one hot-water placement that avoids it. Built on the finding and table of outside pull request 3420 by Bankaifan.
+
+### #3511 The savings reference holds only a state the pump could deliver (R10-SAV-VALUATION-RESIDUE)
+
+The reference thermostat's held room state is now the highest temperature the reference step can hold within the pump's and the mixing valve's limits, so the reference no longer draws stored heat that nobody paid for. A reference that can hold the target is unchanged.
+
+### Developer tooling, CI and audit machinery only
+
+#3557, #3546, #3558, #3499, #3520, #3539, #3549.
+
+### Record only
+
+#3559 (delivery rows, autofix), #3555, #3554 (roster).
+
 ## v7.1.15
 
 **Patch stamp: 16 merges since v7.1.14 (`git log --first-parent --merges --format=%h v7.1.14..HEAD | wc -l`): the supply switch now keeps its minimum run and pause, the mixing-valve target is labelled as a room temperature, boosts keep the learners clean while their heat settles, and the dashboard card folds its detail sections; the rest is tooling.**
diff --git a/VERSION b/VERSION
index 6329380f96..682452864e 100644
--- a/VERSION
+++ b/VERSION
@@ -1 +1 @@
-7.1.15
+7.1.16
diff --git a/custom_components/heatpump_optimizer/manifest.json b/custom_components/heatpump_optimizer/manifest.json
index 0a11baa27b..b839ba97e5 100644
--- a/custom_components/heatpump_optimizer/manifest.json
+++ b/custom_components/heatpump_optimizer/manifest.json
@@ -25,5 +25,5 @@
     "scipy>=1.10.0",
     "threadpoolctl>=3.5.0"
   ],
-  "version": "7.1.15"
+  "version": "7.1.16"
 }
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 50cce5dd8a..be4a979ba5 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -11,7 +11,7 @@
 
 const CARD_TAG = "heatpump-optimizer-card";
 const EDITOR_TAG = "heatpump-optimizer-card-editor";
-const CARD_VERSION = "7.1.15";
+const CARD_VERSION = "7.1.16";
 
 // Home Assistant's default --primary-color (#03a9f4) is 2.63:1 on a white
 // card — too light for text or for white label text on a filled button.
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index ae32efe4f2..1ecd4a70fc 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -373,7 +373,7 @@
   "source": "manifest.json",
   "claim": "manifest version equals VERSION",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented='7.1.15' measured='7.1.15'",
+  "result": "documented='7.1.16' measured='7.1.16'",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 7672194ce7..98150cca47 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -45,7 +45,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C39 | `docs/architecture.md:module map` | sensor.py -- 62 sensors | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=62 measured=62 | **true** |  |
 | C40 | `docs/architecture.md:module map` | switch.py -- the comment names every switch the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'], the platform constructs ['Away', 'Block DHW', 'Block Space Heating', 'Boost Space Heating', 'DHW Boost', 'Optimizer Active'] | **true** |  |
 | C41 | `docs/architecture.md:module map` | binary_sensor.py -- the comment names every binary sensor the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'], the platform constructs ['Away Mode', 'External Heat Source', 'Input Problem', 'Mold Floor Breach', 'Open Window Detected', 'Wood Cheaper Than Heat Pump'] | **true** |  |
-| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='7.1.15' measured='7.1.15' | **true** |  |
+| C42 | `manifest.json` | manifest version equals VERSION | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='7.1.16' measured='7.1.16' | **true** |  |
 | C43 | `hacs.json` | hacs.json requires Home Assistant 2025.2.0 | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C44 | `README.md badge` | Home Assistant 2025.2.0+ badge matches hacs.json | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
 | C45 | `README.md Requirements` | Home Assistant 2025.2.0 or newer | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='2025.2.0' measured='2025.2.0' | **true** |  |
diff --git a/dev/programme/delivery/3572.md b/dev/programme/delivery/3572.md
new file mode 100644
index 0000000000..6356094349
--- /dev/null
+++ b/dev/programme/delivery/3572.md
@@ -0,0 +1 @@
+- [#3572](https://github.com/tvofi/heatpump_optimizer/pull/3572) — **open**, R10-DIMENSIONS-FULL-COVERAGE: r10 dimensions full coverage (R10-DIMENSIONS-FULL-COVERAGE)
diff --git a/dev/programme/delivery/3578.md b/dev/programme/delivery/3578.md
new file mode 100644
index 0000000000..74f5e0da84
--- /dev/null
+++ b/dev/programme/delivery/3578.md
@@ -0,0 +1 @@
+- [#3578](https://github.com/tvofi/heatpump_optimizer/pull/3578) — **open**, R10-HOTFIX-FEATURES-WEEKEND-CLOCK: pin the charge-settle check's clock to a weekday (R10-HOTFIX-FEATURES-WEEKEND-CLOCK)
diff --git a/tests/features.py b/tests/features.py
index fd0879f877..4c0337aa7a 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -63301,7 +63301,9 @@ def _chg_seq(temps, charged=True, start_hm=(8, 0), heated_at=(1,), saturday=Fals
     learner.async_save_draws = _save_draws
     module = _sys.modules[type(learner).__module__]
     real_dt = module.dt_util
-    start = dt_util.now().replace(hour=start_hm[0], minute=start_hm[1], second=0)
+    # Monday 2026-11-09, never today: the weekday booking must not depend on the day the suite runs.
+    start = dt_util.now().replace(
+        year=2026, month=11, day=9, hour=start_hm[0], minute=start_hm[1], second=0)
     if saturday:
         start += timedelta(days=(5 - start.weekday()) % 7)
     clock = [start]
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index 4c50cb6178..4e3b2fb18e 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -19,9 +19,9 @@
 #
 # The state names are the ones `node tests/card_drift.mjs --list` prints.
 #
-# claims-for: 7.1.15
+# claims-for: 7.1.16
 #
-# v7.1.15: Supply minimum run and pause, valve target label, boost settling, card folds. The stamp empties the list; the
+# v7.1.16: Pump start condition input, duty-switch pricing, savings reference fix. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
 
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index a107b76be2..8b6433462b 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -62,12 +62,11 @@
 # about one release's diff, it does not expire with the stamp and is not part
 # of the inherited-claims comparison.
 #
-# claims-for: 7.1.15
+# claims-for: 7.1.16
 #
-# v7.1.15: Supply minimum run and pause, valve target label, boost settling, card folds. The stamp empties the list; the
+# v7.1.16: Pump start condition input, duty-switch pricing, savings reference fix. The stamp empties the list; the
 # next branch restates its own footprint, claims included.
 #
-config_flow # R10-OUTSIDE-DHW-START-HYSTERESIS: the entities_pump page gains the two start-hysteresis pickers (space_hysteresis_entity, dhw_hysteresis_entity), so the plain render, the seeded render and the seed each gain those two keys; every leaf that moves is "present on one side only" and ADDED at this head. Float-free and compared exactly, so re-recorded in the committed file (golden.py --record --only config_flow). No plan reads the options unset: the other 55 fixtures are byte-identical to the merge base (env_drift.py --all, one environment), which is the null.
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tools/policy/check-wave-script.mjs b/tools/policy/check-wave-script.mjs
index be218608f5..806c32b394 100644
--- a/tools/policy/check-wave-script.mjs
+++ b/tools/policy/check-wave-script.mjs
@@ -69,6 +69,14 @@ let pass = 0, fail = 0
 // This is exactly how the control run for the verdict grammar died.
 const J = (x) => JSON.stringify(x ?? null) ?? 'undefined'
 const t = (n, c, d = '') => { c ? (pass++, console.log('  ok   ' + n)) : (fail++, console.log('  FAIL ' + n + ' ' + d)) }
+// THE ONE SWITCH, READ FROM UNPINNED DATA. `wave-script` grades a pull request
+// with the BASE's copy of this file (decision 0013), so this file lands first and
+// must pass over the tree before the driver that carries the denominator (carryOf,
+// seatCarry, denominatorGaps) and over the tree after it. The switch is whether
+// the finder report schema's coverage rows require an enumerator -- a data file
+// the same pull request that lands the driver changes, never the driver's own text.
+// When it is on, the driver MUST export all three and every denominator test runs.
+const DENOM = (JSON.parse(fs.readFileSync(at('dev/audit/config/finding.schema.json'), 'utf8')).properties?.coverage?.items?.required ?? []).includes('enumerator')
 // A block that throws reports as a failure, never as a truncated run. Every
 // grouped assertion below runs inside it: without that the first unexpected
 // throw ends the process and the remaining assertions are silently unreported,
@@ -805,10 +813,10 @@ await block('the finder report schema', async () => {
   const re = (k) => new RegExp(F.properties?.[k]?.pattern ?? '$^')
   const idRe = re('id'), scopeRe = re('scope')
   const ownerRe = new RegExp(S.properties?.leads?.items?.properties?.owner_seat?.pattern ?? '$^')
-  t('scope admits a scopes.json seat id and refuses a bare dimension (D1-s3 yes, D1 no)', scopeRe.test('D1-s3') && scopeRe.test('D14-s5') && !scopeRe.test('D1') && !scopeRe.test('D16-s1'), String(scopeRe))
+  t('scope admits a scopes.json seat id and refuses a bare dimension (D1-s3 yes, D1 no)', scopeRe.test('D1-s3') && scopeRe.test('D14-s5') && !scopeRe.test('D1') && !scopeRe.test('D18-s1') && (!DENOM || scopeRe.test('D17-s1')), String(scopeRe))
   t('a finding numbered under its seat is an id the schema admits (D13-s1-01, D1-s3-51)', idRe.test('D13-s1-01') && idRe.test('D1-s3-51'), String(idRe))
   t("a lead's owner_seat admits a seat id or unknown, and refuses a bare dimension, a file, or anything else (null control)",
-    ownerRe.test('D1-s3') && ownerRe.test('D14-s5') && ownerRe.test('unknown') && !ownerRe.test('D1') && !ownerRe.test('D16-s1') && !ownerRe.test('boost.py') && !ownerRe.test('') && !ownerRe.test('D1-s3 '), String(ownerRe))
+    ownerRe.test('D1-s3') && ownerRe.test('D14-s5') && ownerRe.test('unknown') && !ownerRe.test('D1') && !ownerRe.test('D18-s1') && (!DENOM || ownerRe.test('D17-s1')) &&!ownerRe.test('boost.py') && !ownerRe.test('') && !ownerRe.test('D1-s3 '), String(ownerRe))
   // A design choice, said so: the guess is refused unless it is a class the
   // ledger HAS, so a class the judge adds is added to bugclasses.json and to
   // this enum in one pull request -- this check fails until both carry it.
@@ -951,7 +959,9 @@ await block('the scoped round driver', async () => {
   if (!blk) return
   t('the dispatch block draws on no randomness and no clock', !/Math\.random|Date\b|performance\.now|crypto/.test(blk[0]), 'found one')
   t('and no planSeats: seats come from the scopes, not a rotation over the ledger', !/planSeats/.test(rd), 'audit-find.js still names planSeats')
-  const D = new Function(`${blk[0]}\nreturn { CADENCE, EVERY_DIM_ROUNDS, activeIn, seatsFromScopes, BOXES, CHROMIUM, boxGaps }`)()
+  const D = new Function(`${blk[0]}\nreturn { CADENCE, EVERY_DIM_ROUNDS, activeIn, seatsFromScopes, BOXES, CHROMIUM, boxGaps, carryOf: typeof carryOf === 'function' ? carryOf : undefined, seatCarry: typeof seatCarry === 'function' ? seatCarry : undefined, denominatorGaps: typeof denominatorGaps === 'function' ? denominatorGaps : undefined }`)()
+  t('a schema that requires a denominator has a driver that enforces one (carryOf, seatCarry, denominatorGaps in the DISPATCH block)',
+    !DENOM || [D.carryOf, D.seatCarry, D.denominatorGaps].every((f) => typeof f === 'function'), `schema requires an enumerator; exported: ${['carryOf', 'seatCarry', 'denominatorGaps'].filter((k) => typeof D[k] === 'function')}`)
   // The seat ids and boxes below are read off the committed scopes and the
   // DISPATCH block, never named here: a re-cut of either (round 10 gave every
   // dimension three seats) must not turn a control into a test of old names.
@@ -962,8 +972,12 @@ await block('the scoped round driver', async () => {
   // nor a multiple of three, `on6` is a multiple of six.
   const free = Array.from({ length: 60 }, (_, i) => i + 10).filter((r) => !every.includes(r))
   const off = free.find((r) => r % 2 !== 0 && r % 3 !== 0), on6 = free.find((r) => r % 6 === 0)
-  t(`...and the cadence is otherwise read from the round number (D11 and D5 off at ${off}, both on at ${on6}, D0 on at ${off})`,
-    !!off && !!on6 && !D.activeIn(off, 'D11') && D.activeIn(on6, 'D11') && D.activeIn(on6, 'D5') && !D.activeIn(off, 'D5') && D.activeIn(off, 'D0'), 'the cadence is not derived from the round')
+  // D11 and D13 are held to the driver's own table, not to a number here: the
+  // cadence a tree declares is the cadence it must run (tvofi 2026-11-13 made it
+  // every round, in the pull request that lands the denominator).
+  t(`...and the cadence is otherwise read from the round number (D5 off at ${off}, on at ${on6}; D0 on at ${off}; D11 and D13 follow their CADENCE entry)`,
+    !!off && !!on6 && !D.activeIn(off, 'D5') && D.activeIn(on6, 'D5') && D.activeIn(off, 'D0')
+      && ['D11', 'D13'].every((d) => D.activeIn(off, d) === (D.CADENCE[d] === 1) && D.activeIn(on6, d)), 'the cadence is not derived from the round')
   const ids = L.dims.flatMap((d) => D.seatsFromScopes(scopes, d).map((s) => s.id))
   const fileSeats = Object.entries(scopes).filter(([k]) => !k.startsWith('_')).flatMap(([d, x]) => Object.keys(x.seats).map((k) => `${d}-${k}`))
   t('one seat per scopes.json seat, id <dim>-s<n>, nothing added or dropped', J(ids) === J(fileSeats), `${ids.length} vs ${fileSeats.length}`)
@@ -1005,19 +1019,26 @@ await block('the scoped round driver', async () => {
   // export (or another seat's tree) is visible in its prompt.
   const isoDims = new Set(L.isolated)
   const PREP = { exportDir: '/x', worktrees: Object.fromEntries(fileSeats.filter((id) => isoDims.has(id.split('-')[0])).map((id) => [id, `/w/${id}`])), python: 'py', rotation_ok: true, scopes_ok: true, scopes_rc: 0, scopes_out: 'ok' }
+  // A closed denominator for a seat: one row per step it owns, every carried item answered examined.
+  const closed = (id, args) => {
+    const seat = D.seatsFromScopes(args.scopes, id.split('-')[0]).find((x) => x.id === id)
+    if (!seat) return []
+    const carry = D.seatCarry ? D.seatCarry(args.rotation, args.round, seat) : []
+    return seat.steps.map((m) => ({ step: `${seat.dim}.${m}`, depth: 'deep', enumerator: 'stub-enumerator', universe: 1, examined: 1, not_reached: [], redispatched: carry.filter((c) => c.step === m).map((c) => ({ item: c.id, state: 'examined' })), evidence: 'stub' }))
+  }
   const drive = async (args, { prep = {}, report = () => ({}), nullSeats = [], leadsOut = {}, gather } = {}) => {
     const calls = []
     const agent = async (prompt, o) => {
       calls.push({ label: o.label, prompt, schema: o.schema })
       if (o.label === 'prepare') return { ...PREP, ...prep }
       if (o.label === 'gather' && gather) return gather(prompt)
-      if (o.label === 'gather') return { reports: Object.fromEntries(fileSeats.map((id) => [id, { dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(id) }])), absent_boxes: [] }
+      if (o.label === 'gather') return { reports: Object.fromEntries(fileSeats.map((id) => [id, { dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: closed(id, args), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(id) }])), absent_boxes: [] }
       if (o.label === 'leads') return { report_path: '/r/leads', findings: [], non_findings: [], harnesses: [], converted: [], closed: [], ...leadsOut }
       if (nullSeats.includes(o.label)) return null
       if (o.label === 'intake') return { branch: 'b', registered: [], rejected: [] }
       if (o.label === 'quiet') return { quiet_path: '/q', d3_confirmed: [] }
       if (o.label.startsWith('collect-')) return { branch: 'b', commit: 'c' }
-      return { dimension: o.label.split('-')[0], report_path: `/r/${o.label}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(o.label) }
+      return { dimension: o.label.split('-')[0], report_path: `/r/${o.label}`, coverage: closed(o.label, args), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [], ...report(o.label) }
     }
     const fn = new Function('agent', 'log', 'phase', 'pipeline', 'args', `return (async () => { ${rbody} })()`)
     let out, error = ''
@@ -1068,7 +1089,7 @@ await block('the scoped round driver', async () => {
   const seatBoxes = Object.keys(D.BOXES).filter((b) => D.BOXES[b].heavy.length + D.BOXES[b].light.length)
   t(`from "intake" gathers once per box, each prompt naming its own box (${seatBoxes.length} boxes)`,
     gathers.length === seatBoxes.length && seatBoxes.every((b) => gathers.filter((c) => c.prompt.includes(`reports-${b}.json`)).length === 1), J(gathers.map((c) => (/reports-(B\d+)\.json/.exec(c.prompt) ?? [])[1])))
-  const rep = (id) => ({ dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: [], unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [] })
+  const rep = (id) => ({ dimension: id.split('-')[0], report_path: `/r/${id}`, coverage: closed(id, base), unfinished: [], findings: [], non_findings: [], harnesses: [], leads: [] })
   const boxIn = (prompt) => (/reports-(B\d+)\.json/.exec(prompt) ?? [])[1]
   const own = (b) => Object.fromEntries([...D.BOXES[b].heavy, ...D.BOXES[b].light].map((id) => [id, rep(id)]))
   const cutBox = bx
@@ -1100,7 +1121,7 @@ await block('the scoped round driver', async () => {
   t(`an unknown box is refused (${noBox})`, !D.BOXES[noBox] && /is not one of/.test((await drive({ ...base, box: noBox })).error), `${noBox} accepted`)
   const both = await drive({ ...base, box: 'B1', from: 'intake' })
   t('box and from "intake" together are refused before Prepare', /exclusive/.test(both.error) && both.labels.length === 0, both.error || J(both.labels))
-  // Round `off` runs neither D5, D6, D11 nor D13 (cadence 2 and 3): a box
+  // Round `off` runs neither D5 nor D6 (cadence 2; D11 and D13 run every round): a box
   // holding both active and inactive seats carries only the active ones, and
   // the placement check is taken over the active seats.
   const mixed = Object.keys(D.BOXES).find((b) => { const ss = [...D.BOXES[b].heavy, ...D.BOXES[b].light].map((s) => D.activeIn(off, s.split('-')[0])); return ss.includes(true) && ss.includes(false) })
@@ -1205,6 +1226,82 @@ await block('the scoped round driver', async () => {
     /handoff\/audit-r9-find-<box>/.test(glp) && !/handoff\/audit-r9-find-<box>/.test(lp), glp.slice(-400))
   t('and the round\'s ledger entry names every active dimension, one step list per seat',
     Object.keys(r9.out?.rotation_round ?? {}).length === L.dims.length && r9.out.rotation_round.D1.seats.length === Object.keys(scopes.D1.seats).length, J(Object.keys(r9.out?.rotation_round ?? {})))
+
+  // The denominator (COMMON.md; tvofi 2026-11-13): a report names what its steps
+  // range over, how much it examined and what it left, and what the round before
+  // left is the first work of this one. Each refusal has its null control here.
+  if (!DENOM) console.log("  skip   the denominator block: the schema's coverage rows require no enumerator at this tree")
+  else await block('the denominator', async () => {
+    const seat = { dim: 'D1', steps: ['M1', 'M2'] }
+    const row = (m, o = {}) => ({ step: `D1.${m}`, enumerator: 'e', universe: 2, examined: 2, not_reached: [], redispatched: [], evidence: 'x', ...o })
+    const ok = { coverage: [row('M1'), row('M2')] }
+    const gaps = (rep, carry = []) => D.denominatorGaps(seat, rep, carry)
+    const refuses = (name, rep, re, carry = []) => { const g = gaps(rep, carry); t(`denominatorGaps refuses ${name}`, g.length > 0 && g.some((x) => re.test(x)), J(g)) }
+    t('denominatorGaps passes a closed report, one row per step (null control)', J(gaps(ok)) === J([]), J(gaps(ok)))
+    refuses('a step with no row', { coverage: [row('M1')] }, /M2/)
+    refuses('two rows for one step', { coverage: [row('M1'), row('M1'), row('M2')] }, /M1/)
+    refuses('an empty enumerator', { coverage: [row('M1', { enumerator: ' ' }), row('M2')] }, /M1/)
+    refuses('examined above universe', { coverage: [row('M1', { examined: 3 }), row('M2')] }, /M1/)
+    refuses('a non-integer universe', { coverage: [row('M1', { universe: 1.5, examined: 1 }), row('M2')] }, /M1/)
+    refuses('examined below universe with nothing listed not reached', { coverage: [row('M1', { examined: 1 }), row('M2')] }, /M1/)
+    refuses('examined equal to universe with a not_reached list', { coverage: [row('M1', { not_reached: ['a'] }), row('M2')] }, /M1/)
+    refuses('an absent coverage', {}, /M1/)
+    const c1 = { id: 'C1', step: 'M1', item: 'x', age: 1, overdue: false }
+    const withAns = (state) => ({ coverage: [row('M1', state ? { universe: 2, examined: state === 'examined' ? 2 : 1, not_reached: state === 'examined' ? [] : ['x'], redispatched: [{ item: 'C1', state }] } : {}), row('M2')] })
+    refuses('a carried item left unanswered', ok, /C1/, [c1])
+    t('...and passes it answered examined, or answered not_reached when not overdue and the counts close (null control)', J(gaps(withAns('examined'), [c1])) === J([]) && J(gaps(withAns('not_reached'), [c1])) === J([]), J([gaps(withAns('examined'), [c1]), gaps(withAns('not_reached'), [c1])]))
+    refuses('an overdue carried item answered not_reached', withAns('not_reached'), /C1/, [{ ...c1, overdue: true }])
+    t('...and passes the same overdue item answered examined (null control)', J(gaps(withAns('examined'), [{ ...c1, overdue: true }])) === J([]), J(gaps(withAns('examined'), [{ ...c1, overdue: true }])))
+
+    const led = { D1: { steps: ['M1', 'M2', 'M3'], rounds: {
+      9: { coverage: { M3: { enumerator: 'e', universe: 3, examined: 1, not_reached: ['a', 'b'] } } },
+      10: { coverage: { M1: 'spot', M2: 'deep', M3: { enumerator: 'e', universe: 3, examined: 2, not_reached: ['a'] } }, unfinished: [{ step: 'D1.M2', what: 'left' }] } } } }
+    const co = D.carryOf(led, 11, 'D1')
+    t('carryOf at round 11 reads round 10: the whole step for M1, "a" aged 2 for M3, the unfinished entry for M2; nothing for deep M2, "b" not carried',
+      co.length === 3 && co.filter((c) => c.step === 'M1').length === 1 && /whole step/.test(co.find((c) => c.step === 'M1')?.item ?? '') && co.find((c) => c.step === 'M3')?.item === 'a' && co.find((c) => c.step === 'M3')?.age === 2
+      && co.filter((c) => c.step === 'M2').length === 1 && co.find((c) => c.step === 'M2')?.item === 'unfinished: left' && !co.some((c) => c.item === 'b'), J(co))
+    const co10 = D.carryOf(led, 10, 'D1')
+    t('...at round 10 it reads round 9 only: a and b, each aged 1', co10.length === 2 && co10.every((c) => c.step === 'M3' && c.age === 1) && J(co10.map((c) => c.item)) === J(['a', 'b']), J(co10))
+    t('...and a dimension with no earlier round carries nothing (null control)', J(D.carryOf(led, 9, 'D1')) === J([]) && J(D.carryOf(led, 11, 'D2')) === J([]), J(D.carryOf(led, 9, 'D1')))
+
+    const sc = D.seatCarry(led, 11, { dim: 'D1', steps: ['M3', 'M2'] })
+    t('seatCarry numbers C1.. in order and keeps only the seat\'s steps', J(sc.map((c) => [c.id, c.step])) === J([['C1', 'M3'], ['C2', 'M2']]) && J(D.seatCarry(led, 11, { dim: 'D1', steps: ['M1'] }).map((c) => c.id)) === J(['C1']), J(sc))
+    const ov = (rotate) => D.seatCarry({ D1: { ...led.D1, ...(rotate ? { rotate } : {}) } }, 11, { dim: 'D1', steps: ['M3'] })[0].overdue
+    t('seatCarry marks the age-2 item overdue at bound 3, not at bound 4, not with no rotate', ov({ M3: { bound: 3 } }) === true && ov({ M3: { bound: 4 } }) === false && ov(undefined) === false, J([ov({ M3: { bound: 3 } }), ov({ M3: { bound: 4 } }), ov(undefined)]))
+
+    // Driven: the real committed scopes and ledger at round 11.
+    const b11 = { ...base, round: 11 }
+    const empty = await drive(b11, { report: (l) => (l === 'D1-s1' ? { coverage: [] } : {}) })
+    t('a seat whose report carries no denominator is dispatched twice, ends missing, and intake does not run',
+      empty.labels.filter((l) => l === 'D1-s1').length === 2 && J(empty.out?.missing) === J(['D1-s1']) && !empty.labels.includes('intake'), J({ n: empty.labels.filter((l) => l === 'D1-s1').length, missing: empty.out?.missing, error: empty.error }))
+    const full11 = await drive(b11)
+    t('...and with the default stub every seat reports and intake runs (null control)', full11.error === '' && J(full11.out?.missing) === J([]) && full11.labels.includes('intake') && full11.labels.filter((l) => l === 'D1-s1').length === 1, J({ error: full11.error, missing: full11.out?.missing }))
+
+    const fp = (l) => full11.calls.find((c) => c.label === l)?.prompt ?? ''
+    t('a seat with carry (D4-s1, whose round-10 M1 was "spot") is told FIRST WORK with its C ids', fp('D4-s1').includes('FIRST WORK') && fp('D4-s1').includes('C1') && !fp('D4-s1').includes('handed your steps nothing not reached'), fp('D4-s1').slice(-400))
+    const none = await drive({ ...b11, rotation: { ...ledger, D4: { ...ledger.D4, rounds: {} } } })
+    const np = (l) => none.calls.find((c) => c.label === l)?.prompt ?? ''
+    const d4 = none.labels.filter((l) => /^D4-s\d+$/.test(l))
+    t('a dimension with no earlier round is told it was handed nothing, and no FIRST WORK (null control)', d4.length > 0 && d4.every((l) => np(l).includes('handed your steps nothing not reached') && !np(l).includes('FIRST WORK')), J(d4))
+
+    // The ledger entry is the sum over the seats that own the step.
+    const owners = (d, m) => D.seatsFromScopes(scopes, d).filter((x) => x.steps.includes(m)).map((x) => x.id)
+    const [sd, sm] = L.dims.filter((d) => scopes[d]).flatMap((d) => scopes[d].steps.map((m) => [d, m])).sort((a, b) => owners(b[0], b[1]).length - owners(a[0], a[1]).length)[0]
+    const led11 = full11.out?.rotation_round?.[sd]?.coverage?.[sm]
+    const k = owners(sd, sm).length
+    t(`the round's ledger coverage is exactly {enumerator, universe, examined, not_reached}, summed over the ${k} seat(s) owning ${sd}.${sm}`,
+      J(Object.keys(led11 ?? {}).sort()) === J(['enumerator', 'examined', 'not_reached', 'universe']) && led11.universe === k && led11.examined === k && J(led11.not_reached) === J([]), J(led11))
+    const s41 = D.seatsFromScopes(scopes, 'D4').find((x) => x.id === 'D4-s1')
+    const carry41 = D.seatCarry(ledger, 11, s41)
+    const m41 = carry41[0]?.step
+    const answered = await drive(b11, { report: (l) => (l !== 'D4-s1' ? {} : { coverage: closed('D4-s1', b11).map((r) => (r.step !== `D4.${m41}` ? r : { ...r, examined: 0, universe: 1, not_reached: ['z'], redispatched: [...r.redispatched.filter((x) => x.item !== 'C1'), { item: 'C1', state: 'not_reached' }] })) }) })
+    const nr = answered.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []
+    t('a carried item answered not_reached stays in the ledger under its original words, beside the seat\'s own not_reached',
+      !!m41 && carry41[0].overdue === false && nr.includes('z') && nr.includes(carry41[0].item), J({ m41, nr, item: carry41[0]?.item, error: answered.error, missing: answered.out?.missing }))
+    t('...and the default run keeps neither (null control)', !(full11.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []).includes('z') && !(full11.out?.rotation_round?.D4?.coverage?.[m41]?.not_reached ?? []).includes(carry41[0]?.item), J(full11.out?.rotation_round?.D4?.coverage?.[m41]))
+
+    t('the cadence: D11, D13, D16 and D17 run at round 11, D5 does not', D.activeIn(11, 'D11') && D.activeIn(11, 'D13') && D.activeIn(11, 'D16') && D.activeIn(11, 'D17') && !D.activeIn(11, 'D5'), J(['D11', 'D13', 'D16', 'D17', 'D5'].map((d) => [d, D.activeIn(11, d)])))
+  })
 })
 
 // THE ROUND-9 VERIFY DRIVER, ADMITTED BEFORE IT LANDS -- R1a's route for the

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
