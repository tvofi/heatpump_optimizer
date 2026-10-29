# Review packet #2917
head: c9bf05dfe0a1b29eb18dd444a8a32983ea781d77
base: 66974d47312caa46e9817b9aeae7186e9764e560

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=123397110263 neutral
arch-score / arch-score id=123396748817 success
arm id=123396517934 skipped
budget-raise-gate / budget-raise-gate id=123396748851 success
cancel-superseded id=123396547405 success
codeql / Analyze (actions) id=123396748497 success
codeql / Analyze (javascript-typescript) id=123396748532 success
codeql / Analyze (python) id=123396748528 in_progress
governance / delivery-status id=123396748628 success
governance / delivery-status-publish id=123396750460 skipped
governance / env-matrix id=123396748570 in_progress
governance / instrument-self-tests id=123396748808 in_progress
governance / policy-docs id=123396748912 in_progress
governance / record id=123396750578 skipped
governance / wave-script id=123396748544 success
hassfest / hassfest id=123396748487 success
kernel-points id=123396750265 skipped
prelude id=123396547293 success
refresh id=123396547091 success
tests / arch-instrument id=123396986546 in_progress
tests / briefs id=123396748475 success
tests / browser id=123396986509 in_progress
tests / closure-scope id=123396748454 success
tests / closures id=123396986872 in_progress
tests / coverage id=123396986684 in_progress
tests / fast (3.14) id=123396986568 in_progress
tests / mutation id=123396748501 in_progress
tests / nightly-ha id=123396989492 skipped
tests / nightly-status id=123396748525 failure
tests / replay id=123396986715 in_progress
tests / typing id=123396986627 in_progress
validate / validate-hacs id=123396748493 success

## Refusals
red-unanswered: concluded red check `tests / nightly-status` is not named in ## Red checks

## Advisories
none

## carry_audit at the head
NOTE body item 8e11a43d: R10-COP-GATE
NOTE body item a8c294f4: R10-COP-GATE
NOTE body item bdb8b040: R10-COP-GATE
NOTE body item 67905fec: R10-COP-GATE
NOTE body item b73ff537: R10-COP-GATE
NOTE body item cfcf943f: R10-COP-GATE
NOTE body item 4a8f4129: R10-COP-GATE
NOTE body item bfe8d487: R10-COP-GATE
CARRY-AUDIT: 8 finding item(s): 8 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         tools/audit/seat/seat_venv.sh
             `tools/audit/seat/seat_venv.sh` is in the tree at this head
  ok         python3 tests/closure.py select --diff b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa --workdir D
             `tests/closure.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  unverified PYTHONPATH=tests/hastub GOLDEN_REF=b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa python3 tests/<script>
             the path `tests/<script>` is a template or an expansion, not a literal
  unverified node
             node with no script argument
  ok         tests/finite_boundary.py
             `tests/finite_boundary.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/finite_boundary.py
             `tests/finite_boundary.py` is in the tree at this head
  unverified python3 -m coverage run --include='*/store.py' tests/finite_boundary.py
             python3 runs an inline script rather than a file
  unverified python3 -m coverage report
             python3 runs an inline script rather than a file
  ok         dev/audit/harnesses/r10_cop_gate.py
             `dev/audit/harnesses/r10_cop_gate.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate.py
             `dev/audit/harnesses/r10_cop_gate.py` is in the tree at this head
  unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         dev/audit/rounds/round10/study-ident/owner_rows.py
             `dev/audit/rounds/round10/study-ident/owner_rows.py` is in the tree at this head
  ok         dev/audit/harnesses/cop_duty_floor.py
             `dev/audit/harnesses/cop_duty_floor.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main
             `tests/mutation_table.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 14 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json
new file mode 100644
index 000000000..9889b2605
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.as_dict RETURN_DEL 62858a00",
+  "killed_by": "tests/features.py",
+  "old": "        return {\"cop\": self.cop, \"curve_dhw\": self.curve_dhw, \"dhw_temp\": self.dhw_temp, \"at\": at}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.6f8909cf.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.6f8909cf.json
deleted file mode 100644
index 45b224539..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.6f8909cf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.as_dict RETURN_DEL 6f8909cf",
-  "killed_by": "tests/features.py",
-  "old": "        return {\"cop\": self.cop, \"curve_dhw\": self.curve_dhw, \"dhw_temp\": self.dhw_temp}",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.4cb095ac.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.4cb095ac.json
deleted file mode 100644
index 92fe18ad9..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.4cb095ac.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict BOOLOP 4cb095ac",
-  "killed_by": "tests/features.py",
-  "old": "        if temp is not None and not np.isfinite(temp):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: BOOLOP (`if temp is not None or not np.isfinite(temp):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.4cb095ac.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.4cb095ac.json
deleted file mode 100644
index 2740799f8..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.4cb095ac.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict GUARD_OFF 4cb095ac",
-  "killed_by": "tests/features.py",
-  "old": "        if temp is not None and not np.isfinite(temp):",
-  "reason": "Hand-recorded by the #2066 fixer at 4bf7bdde1 against the ratchet base b2b6acd64, not by `--pin-killed` (whose baselines need CI's Linux floats). `GUARD_OFF` (if False:) flips the condition of tests/features.py's R.check \"an unreadable stored COP record loads as no measurement, whole\" -- the new check \"a non-finite tank temperature drops the record whole\" reads False: switching the guard off keeps cop 2.0 with a nan temperature. Measured by copying the package, rewriting that one line to the operator's own text and re-evaluating the check's condition: baseline True, mutant as stated (evidence table in the pull request's body, `## Unpinned sites`). CI's `--pin-killed` at a pull_request head re-measures the driver itself."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json
new file mode 100644
index 000000000..8d9f32542
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict GUARD_OFF 649d9952",
+  "killed_by": "tests/features.py",
+  "old": "        if (temp is not None and not np.isfinite(temp)) or (raw.get(\"at\") is not None and at is None):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.7c227e9b.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.7c227e9b.json
deleted file mode 100644
index 2dc963923..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.7c227e9b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict RETURN_DEL 7c227e9b",
-  "killed_by": "tests/features.py",
-  "old": "        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json
new file mode 100644
index 000000000..99b0be279
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict RETURN_DEL 81cd12e3",
+  "killed_by": "tests/features.py",
+  "old": "        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp, at=at)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.602baa33.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.602baa33.json
new file mode 100644
index 000000000..b1e54f706
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.602baa33.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio GUARD_OFF 602baa33",
+  "killed_by": "tests/features.py",
+  "old": "        if follows is False:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.4c7c13c0.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.4c7c13c0.json
deleted file mode 100644
index 9a98ff8de..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.4c7c13c0.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio RETURN_DEL 4c7c13c0",
-  "killed_by": "tests/features.py",
-  "old": "        return None if follows else COP_REFUSED_OFF_ASK",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.BOOLOP.460915d8.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.BOOLOP.460915d8.json
new file mode 100644
index 000000000..6a037103b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.BOOLOP.460915d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual BOOLOP 460915d8",
+  "killed_by": "tests/features.py",
+  "old": "        if self.curve_dhw and self.dhw_temp is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.curve_dhw or self.dhw_temp is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.CMP_BOUND.92047180.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.CMP_BOUND.92047180.json
new file mode 100644
index 000000000..99a932ad3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.CMP_BOUND.92047180.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual CMP_BOUND 92047180",
+  "killed_by": "tests/features.py",
+  "old": "        if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.460915d8.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.460915d8.json
new file mode 100644
index 000000000..634115f14
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.460915d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual GUARD_OFF 460915d8",
+  "killed_by": "tests/features.py",
+  "old": "        if self.curve_dhw and self.dhw_temp is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.92047180.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.92047180.json
new file mode 100644
index 000000000..51459c6fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.92047180.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual GUARD_OFF 92047180",
+  "killed_by": "tests/features.py",
+  "old": "        if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.RETURN_DEL.dfd25e72.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.RETURN_DEL.dfd25e72.json
new file mode 100644
index 000000000..aa448a757
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.RETURN_DEL.dfd25e72.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual RETURN_DEL dfd25e72",
+  "killed_by": "tests/features.py",
+  "old": "        return round(float(self.cop) - float(modelled), 3)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
new file mode 100644
index 000000000..95594139b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF ac5ca5ae",
+  "killed_by": "tests/features.py",
+  "old": "    if measured_heat:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
new file mode 100644
index 000000000..c64de4327
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF c1dafc5f",
+  "killed_by": "tests/features.py",
+  "old": "    if follows is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.f1e23bc3.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.f1e23bc3.json
new file mode 100644
index 000000000..5a0eee47e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.f1e23bc3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF f1e23bc3",
+  "killed_by": "tests/features.py",
+  "old": "    if not electric:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
new file mode 100644
index 000000000..57131144a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability RETURN_DEL e75e96f9",
+  "killed_by": "tests/features.py",
+  "old": "    return COP_DRAW_FOLLOWS if follows else COP_NOT_MEASURABLE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.CMP_BOUND.62f6b3b0.json b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.CMP_BOUND.62f6b3b0.json
new file mode 100644
index 000000000..fa4e849d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.CMP_BOUND.62f6b3b0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:pairs_interval CMP_BOUND 62f6b3b0",
+  "killed_by": "tests/features.py",
+  "old": "    return 0.05 <= elapsed_h <= 2.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return 0.05 < elapsed_h <= 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.RETURN_DEL.62f6b3b0.json b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.RETURN_DEL.62f6b3b0.json
new file mode 100644
index 000000000..9d1813586
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.RETURN_DEL.62f6b3b0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:pairs_interval RETURN_DEL 62f6b3b0",
+  "killed_by": "tests/features.py",
+  "old": "    return 0.05 <= elapsed_h <= 2.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.6cac1c2f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.6cac1c2f.json
new file mode 100644
index 000000000..d7fa362d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.6cac1c2f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF 6cac1c2f",
+  "killed_by": "tests/features.py",
+  "old": "            if pairs_interval(elapsed):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
new file mode 100644
index 000000000..cf6a9c195
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF b36c07ff",
+  "killed_by": "tests/features.py",
+  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.204c8b17.json b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.204c8b17.json
new file mode 100644
index 000000000..ecb786441
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.204c8b17.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:ObservedCOPSensor._waiting_for GUARD_OFF 204c8b17",
+  "killed_by": "tests/entities.py",
+  "old": "        if data.get(\"cop_observability\") == COP_NOT_MEASURABLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_electric.RETURN_DEL.1cbe4cb2.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_electric.RETURN_DEL.1cbe4cb2.json
new file mode 100644
index 000000000..71d1cda3f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_electric.RETURN_DEL.1cbe4cb2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_electric RETURN_DEL 1cbe4cb2",
+  "killed_by": "tests/features.py",
+  "old": "        return self.electric_counter if self.heat_counter else self.measured_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json b/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json
new file mode 100644
index 000000000..511f45f00
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio RETURN_DEL d7923b87",
+  "old": "        return None",
+  "reason": "Equivalent (RETURN_DEL, `return None` -> `pass`): the statement is the last one in MeasuredCop.judge_ratio, after `if` arms that each return, so deleting it lets the method fall off its own end and return None -- the same value, on every input, to every reader. Measured by the R10-COP-GATE repair seat's `mutation_table.py --pin-killed --base origin/main` over every driver in play (tests/features.py, tests/entities.py, tests/finite_boundary.py, tests/stress.py among them): the site lived, against 15 of the 21 new sites killed in the same drive, among them this method's own `if follows is False` guard (killed by tests/features.py).",
+  "verdict": "equivalent"
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/accuracy.py b/custom_components/heatpump_optimizer/accuracy.py
index 859cf60eb..aa71a3969 100644
--- a/custom_components/heatpump_optimizer/accuracy.py
+++ b/custom_components/heatpump_optimizer/accuracy.py
@@ -781,6 +781,12 @@ def heat_loss_refit(
     }
 
 
+def pairs_interval(elapsed_h: float) -> bool:
+    """A pending prediction this many hours old still describes the interval
+    that just closed: not a re-run minutes later, not across a restart or gap."""
+    return 0.05 <= elapsed_h <= 2.0
+
+
 # -- the COP learner's last word -------------------------------------------
 
 #: Why the COP learner turned an interval away: one code per guard of
@@ -810,6 +816,33 @@ COP_REFUSED_UNALIGNED = "unaligned_meters"
 #: (``MeasuredCop.judge_ratio``).
 COP_ASK_TOLERANCE = 0.15
 
+#: Whether this install can observe its COP at all (#2262; ``cop_observability``):
+#: a heat reading over an electrical one measures it; without a heat reading
+#: the ratio of draw to ask is an efficiency reading only where the draw follows
+#: the ask, which ``draw_range.follows_ask`` judges.
+COP_HEAT_METERED = "heat_metered"
+COP_DRAW_FOLLOWS = "draw_follows_plan"
+COP_NOT_MEASURABLE = "not_measurable"
+COP_NO_ELECTRIC = "no_electric_meter"
+
+
+def cop_observability(*, electric: bool, measured_heat: bool, follows: bool | None) -> str:
+    """This install's COP observability: one of the ``COP_*`` states above, or
+    ``COP_REFUSED_NO_EVIDENCE`` while the draw window cannot say yet.
+
+    ``electric``: an electrical figure the COP divides by (the power entity,
+    or the electric counter a heat counter's span reads); ``measured_heat``:
+    ``probe_install(...).measured_heat``, the heat counter or the thermal power
+    entity; ``follows``: ``follows_ask`` on the running-draw window.
+    """
+    if not electric:
+        return COP_NO_ELECTRIC
+    if measured_heat:
+        return COP_HEAT_METERED
+    if follows is None:
+        return COP_REFUSED_NO_EVIDENCE
+    return COP_DRAW_FOLLOWS if follows else COP_NOT_MEASURABLE
+
 
 @dataclass
 class MeasuredCop:
@@ -822,6 +855,10 @@ class MeasuredCop:
     included. The curve *choice* is kept rather than the modelled value: the
     residual is taken at the settling sample's own outdoor temperature.
 
+    ``at`` is when that COP folded, persisted with it: the latch outlives
+    every later refusal, so its age is part of the reading (``None``: a record
+    stored before the instant was, whose age is unknown).
+
     ``refusal`` is one of the ``COP_REFUSED_*`` codes for the latest interval
     (``None`` once one folds). It is not persisted, and diagnostics publish it
     (:func:`diagnostics_view`): the observed-COP sensor is unavailable exactly
@@ -833,6 +870,7 @@ class MeasuredCop:
     curve_dhw: bool = False
     dhw_temp: float | None = None
     refusal: str | None = None
+    at: datetime | None = None
 
     @staticmethod
     def judge_floor(asked_kw: float, drawn_kw: float, params: Any) -> str | None:
@@ -850,12 +888,12 @@ class MeasuredCop:
 
         ``ewma`` is the walking ratio BEFORE this interval, so an interval
         cannot vouch for itself. ``COP_REFUSED_TRACKING``: a one-off blip off
-        the walking ratio (v4.0.5). A departure from the ask beyond
-        ``COP_ASK_TOLERANCE`` is then judged on ``draw_range.follows_ask``:
-        evidence that the draw follows the ask lets it fold (an efficiency
-        shift); evidence that it does not refuses it (``COP_REFUSED_OFF_ASK``:
-        a pump that sets its own power, whose departures would fold as a COP
-        shortfall); with no evidence yet it folds only where base would have
+        the walking ratio (v4.0.5). Evidence that the draw does not follow
+        the ask (``draw_range.follows_ask`` False) refuses every interval,
+        within the tolerance or not (``COP_REFUSED_OFF_ASK``: a pump that sets
+        its own power, whose ratio would fold as a COP shift, #2262). A
+        departure beyond ``COP_ASK_TOLERANCE`` then folds on evidence that the
+        draw follows the ask (an efficiency shift); with no evidence yet it folds only where base would have
         -- the ask and the draw both clear the nameplate third -- and is
         otherwise ``COP_REFUSED_NO_EVIDENCE``. So no install folds a departure
         base refused before the evidence says the draw follows its ask; one
@@ -863,22 +901,46 @@ class MeasuredCop:
         """
         if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:
             return COP_REFUSED_TRACKING
+        follows = follows_ask(draw)
+        if follows is False:
+            # #2262: a draw the evidence shows does not follow its ask is no
+            # efficiency reading at ANY ratio; one within the tolerance only
+            # happened to land near the ask.
+            return COP_REFUSED_OFF_ASK
         if abs(ratio - 1.0) <= COP_ASK_TOLERANCE:
             return None
-        follows = follows_ask(draw)
         if follows is None:
             if min(asked_kw, ratio * asked_kw) >= params.nameplate_power_floor_kw:
                 return None
             return COP_REFUSED_NO_EVIDENCE
-        return None if follows else COP_REFUSED_OFF_ASK
+        return None
 
-    def record(self, cop: float, curve_dhw: bool, dhw_temp: float | None) -> None:
-        """One folded interval's COP and its curve, together."""
+    def record(self, cop: float, curve_dhw: bool, dhw_temp: float | None, at: datetime) -> None:
+        """One folded interval's COP, its curve and when it folded, together."""
         self.cop, self.curve_dhw, self.dhw_temp = round(float(cop), 2), curve_dhw, dhw_temp
+        self.at = at
+
+    def residual(self, since: datetime, outdoor: float | None, model: Any) -> float | None:
+        """Observed minus modelled COP for an interval that began at ``since``.
+
+        ``None`` unless the latch folded after ``since``: a COP latched on an
+        earlier interval re-subtracted on every later sample is a function of
+        outdoor temperature alone (#2262), not a reading of this one. The
+        modelled curve is the one the observation was referenced to; no
+        outdoor temperature, no residual.
+        """
+        if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) <= 0.0:
+            return None
+        if self.curve_dhw and self.dhw_temp is not None:
+            modelled = model.compute_cop_dhw(outdoor, self.dhw_temp)
+        else:
+            modelled = model.compute_cop(outdoor)
+        return round(float(self.cop) - float(modelled), 3)
 
     def as_dict(self) -> dict[str, Any]:
         """The measurement only; a refusal describes one interval."""
-        return {"cop": self.cop, "curve_dhw": self.curve_dhw, "dhw_temp": self.dhw_temp}
+        at = None if self.at is None else self.at.isoformat()
+        return {"cop": self.cop, "curve_dhw": self.curve_dhw, "dhw_temp": self.dhw_temp, "at": at}
 
     @classmethod
     def from_dict(cls, raw: Any) -> MeasuredCop:
@@ -891,13 +953,14 @@ class MeasuredCop:
         try:
             cop, dhw = float(raw["cop"]), raw.get("curve_dhw") is True
             temp = None if raw.get("dhw_temp") is None else float(raw["dhw_temp"])
+            at = None if raw.get("at") is None else stored_instant(raw["at"])
         except (TypeError, ValueError, KeyError, AttributeError, OverflowError):
             return cls()
         if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):
             return cls()
-        if temp is not None and not np.isfinite(temp):
+        if (temp is not None and not np.isfinite(temp)) or (raw.get("at") is not None and at is None):
             return cls()
-        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp)
+        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp, at=at)
 
 
 def diagnostics_view(record: MeasuredCop, params: Any, draw: DrawRange | None) -> dict[str, Any]:
@@ -912,6 +975,7 @@ def diagnostics_view(record: MeasuredCop, params: Any, draw: DrawRange | None) -
     return {
         "last_refusal": record.refusal,
         "measured_cop": record.cop,
+        "measured_at": None if record.at is None else record.at.isoformat(),
         "power_floor_kw": round(float(params.flow_lift_power_floor_kw), 3),
         "draw_follows_ask": follows_ask(draw),
     }
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 2dab5a6c6..27a6cdafa 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -235,6 +235,8 @@ from .accuracy import (
     COP_REFUSED_UNALIGNED,
     LEAD_BUCKETS,
     MeasuredCop,
+    cop_observability,
+    pairs_interval,
     AccuracySample,
     AccuracyTracker,
     delivered_ratio,
@@ -5164,7 +5166,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         )
         if not np.isfinite(observed_cop) or observed_cop <= 0.1:
             return COP_REFUSED_OBSERVED
-        self._measured_cop.record(observed_cop, cop_curve_dhw, cop_dhw_temp)
+        self._measured_cop.record(observed_cop, cop_curve_dhw, cop_dhw_temp, dt_util.now())
 
         alpha = COP_LEARNING_ALPHA
         new_scale = (1.0 - alpha) * self._cop_scale + alpha * target_scale
@@ -7742,6 +7744,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         ctx = _ctx_of(self)
         ring = self._snapshot_ring
         snaps = ring.snapshots
+        install = probe_install(ctx._config)
         return {
             "dhw_cooling_rate": round(self._dhw_learner.cooling_rate, 3),
             "dhw_cooling_samples": self._dhw_learner.cooling_samples,
@@ -7771,6 +7774,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "cop_scale": round(self._cop_scale, 3),
             "cop_samples": self._cop_samples,
             "measured_cop": self._measured_cop.cop,
+            "measured_cop_at": None if self._measured_cop.at is None else self._measured_cop.at.isoformat(),
+            "cop_refusal": self._measured_cop.refusal,
+            "cop_observability": cop_observability(
+                electric=install.cop_electric(), measured_heat=install.measured_heat,
+                follows=draw_range.follows_ask(self._accuracy.draw),
+            ),
             "defrost_derate": self._defrost.factor(
                 ctx._current_state.outdoor_temperature, self._current_humidity()
             ),
@@ -9831,7 +9840,12 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # the same timestamp. Inert until a supply slot is mapped.
         _fold_flow_lift(self, now)
         power_frozen = self._learning_frozen(CONF_POWER_ENTITY)  # read once: the defrost settlement below gates on it too
-        draw_range.fold(self._accuracy.draw, self._measured_power, self._commanded_split(), ctx._thermal_params, frozen=power_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pump_arbiter.flow_command(self))
+        # The meter read now closes the interval ``pending`` governed, so the
+        # draw pairs with that interval's ask and set-point, not the action the
+        # solve just adopted for the next one (#2262), within the window the
+        # accuracy pairing below trusts; a prediction recording no split is none.
+        if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0):
+            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=power_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"))
 
         # T5 #16: settle every matured lead-time promise against the same
         # measured temperature the one-step sample below uses. The window
@@ -9865,7 +9879,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             elapsed = _utc_age_seconds(now, pending["when"]) / 3600.0
             # Only pair up predictions with the interval they were actually
             # about; a restart or a long gap makes the pairing meaningless.
-            if 0.05 <= elapsed <= 2.0:
+            if pairs_interval(elapsed):
                 price = pending.get("price")  # None: no price covered it (#2229)
                 sample = AccuracySample(
                     when=now,
@@ -9893,35 +9907,13 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
                 # T4a: observed-minus-modelled COP rides on the sample, so
                 # the snapshots' accuracy tags and #12's history both see
                 # efficiency, not just temperature error.
-                if (
-                    self._measured_cop.cop is not None
-                    and sample.outdoor_temp is not None
-                ):
-                    try:
-                        # v5.3.0: subtract the curve the observation was
-                        # actually referenced to. Recomputing the space curve
-                        # for a hot-water interval would put back exactly the
-                        # mismatch ``_cop_reference_curve`` removes — the
-                        # residual would show ~16 % and nothing would be wrong
-                        # with the pump. Without a mode entity the flag is
-                        # never set and this is the v5.1.5 expression.
-                        if (
-                            self._measured_cop.curve_dhw
-                            and self._measured_cop.dhw_temp is not None
-                        ):
-                            modelled = self._thermal_model.compute_cop_dhw(
-                                sample.outdoor_temp, self._measured_cop.dhw_temp
-                            )
-                        else:
-                            modelled = self._thermal_model.compute_cop(
-                                sample.outdoor_temp
-                            )
-                        sample.cop_residual = round(
-                            float(self._measured_cop.cop) - float(modelled),
-                            3,
-                        )
-                    except Exception:  # noqa: BLE001 - tag is best-effort
-                        sample.cop_residual = None
+                # Only a COP folded on this interval (MeasuredCop.residual).
+                try:
+                    sample.cop_residual = self._measured_cop.residual(
+                        pending["when"], sample.outdoor_temp, self._thermal_model
+                    )
+                except Exception:  # noqa: BLE001 - tag is best-effort
+                    sample.cop_residual = None
                 # D7-03/D7-05: skip the accuracy sample when ``indoor_frozen``
                 # above is set — open window, external heat, pump fault, or
                 # an unusable indoor sensor. Energy below is still
@@ -9947,6 +9939,8 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             # heating alone made every hot-water charge look like the unit
             # under-delivering, which fed straight into the defrost derate.
             "power": self._commanded_power(),
+            "split": self._commanded_split(),
+            "flow_command": pump_arbiter.flow_command(self),
             "space_power": float(self._current_action.get("power", 0.0)),
             "dhw_power": float(self._current_action.get("dhw_power", 0.0)),
             # T6: why the plan wanted this interval's draw, captured at
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index bd6d9f7c9..ff71705b9 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -795,6 +795,11 @@ class LearningView(TypedDict, total=False):
     cop_scale: float
     cop_samples: int
     measured_cop: float | None
+    #: When ``measured_cop`` folded (ISO), the latest interval's refusal code,
+    #: and ``accuracy.cop_observability`` (#2262).
+    measured_cop_at: str | None
+    cop_refusal: str | None
+    cop_observability: str
     defrost_derate: float
     defrost_samples: int
     defrost_measured_samples: int
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index 817159c87..6c142575f 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -22,6 +22,7 @@ from homeassistant.helpers.entity_platform import AddEntitiesCallback
 
 from . import narrative
 from . import topology
+from .accuracy import COP_NOT_MEASURABLE
 from .const import (
     CONF_BUFFER_TANK_TEMP_ENTITY,
     CONF_DHW_TEMP_ENTITY,
@@ -1685,6 +1686,10 @@ class ObservedCOPSensor(
         data = self._data()
         if not data.get("measured_power_available"):
             return "measured_power_entity"
+        if data.get("cop_observability") == COP_NOT_MEASURABLE:
+            # #2262: the draw does not follow the plan's ask, so its ratio to
+            # the ask is no COP; only a heat reading measures one here.
+            return "heat_meter"
         if self._payload_number() is None:
             # A power entity is not a COP: the learner needs the pump to run,
             # against a known outdoor temperature, for long enough to divide.
@@ -1699,6 +1704,12 @@ class ObservedCOPSensor(
             "waiting_for": self._waiting_for,
             _cop: data.get(_cop),
             "cop_samples": data.get("cop_samples"),
+            # The latch outlives every later refusal, so its time is part of
+            # the reading; the refusal is the latest interval's own code
+            # (``span_open``: a heat counter's span still open, not a refusal).
+            "measured_at": data.get("measured_cop_at"),
+            "last_refusal": data.get("cop_refusal"),
+            "observability": data.get("cop_observability"),
             # The same curve the Estimated COP sensor publishes, so observed
             # and modelled can be compared side by side. The previous source,
             # current_action["cop"], is a key nothing ever writes.
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 1b77e6672..88e32d123 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -330,7 +330,7 @@ DOMAINS: dict[str, dict[str, Domain | str]] = {
         **{f"{k}_samples": _COUNT for k in ("buffer_cooling", "house_heat_loss", "lower_floor_loss", "cop")},
         # MeasuredCop.from_dict: the learner refuses a COP at or under 0.1 before rounding.
         "measured_cop/cop": Domain("real", 0.1, null=True),
-        "measured_cop/curve_dhw": _FLAG, "measured_cop/dhw_temp": _N,
+        "measured_cop/curve_dhw": _FLAG, "measured_cop/dhw_temp": _N, "measured_cop/at": _AT0,
         # The cap, as Cusum.as_dict rounds it (1.2 * 1.5 is 1.7999999999999998).
         "vent_cusum/stat": Domain("real", 0.0, round(c.VENT_CUSUM_THRESHOLD_C * STAT_CAP_FACTOR, 4)),
         "cop_health_cusum/stat": Domain("real", 0.0, round(c.COP_HEALTH_THRESHOLD * STAT_CAP_FACTOR, 4)),
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 4d2609673..6dff5a003 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -1277,13 +1277,22 @@ class InstallCapability:
     ``writes`` is a subset of ``switch``, ``setpoint`` and ``frequency``.
     ``measured_power`` is a power entity. ``frequency`` is a frequency
     entity or sensor, read or write. ``measured_heat`` is a thermal power
-    entity (fold e). (a), (c), (d) and (e) all read this probe.
+    entity or a heat counter (fold e). ``heat_counter`` is the heat counter
+    alone and ``electric_counter`` the electric counter its span divides by.
+    (a), (c), (d) and (e) all read this probe.
     """
 
     writes: frozenset[str]
     measured_power: bool
     frequency: bool
     measured_heat: bool = False
+    heat_counter: bool = False
+    electric_counter: bool = False
+
+    def cop_electric(self) -> bool:
+        """An electrical figure a COP divides by: a heat counter's span reads
+        the electric counter, every other reading the power entity (#2262)."""
+        return self.electric_counter if self.heat_counter else self.measured_power
 
     def can_duty_cycle(self) -> bool:
         """A sub-minimum average is realizable.
@@ -1345,6 +1354,8 @@ def probe_install(config: Any) -> InstallCapability:
         measured_heat=bool(
             cfg.get(const.CONF_HEAT_ENERGY_ENTITY) or cfg.get(const.CONF_THERMAL_POWER_ENTITY)
         ),
+        heat_counter=bool(cfg.get(const.CONF_HEAT_ENERGY_ENTITY)),
+        electric_counter=bool(cfg.get(const.CONF_ENERGY_ENTITY)),
     )
 
 
diff --git a/dev/audit/harnesses/r10_cop_gate.py b/dev/audit/harnesses/r10_cop_gate.py
new file mode 100644
index 000000000..8f416f6e3
--- /dev/null
+++ b/dev/audit/harnesses/r10_cop_gate.py
@@ -0,0 +1,131 @@
+#!/usr/bin/env python3
+"""R10-COP-GATE (#2262): COP observability on an install without a heat meter.
+
+Companion to the finder's ``dev/audit/rounds/round10/study-ident/owner_rows.py``
+(fixer.md step 3): that harness reads the gate pass shares, which this fix
+leaves alone; this one applies the tree's own rule to the same inputs and reads
+what the fix changes.
+
+Two arms, both through the production symbols:
+
+  * ``owner`` (needs the PRIVATE bundle path; derived ratios only): the
+    accuracy store's metered rows feed ``draw_range.DrawRange`` as the
+    finder's harness does (``is_running_space``, the owner's configured
+    range), ``follows_ask`` judges that window, and
+    ``accuracy.MeasuredCop.judge_ratio`` replays each row past the duty
+    floor against it. ``folds_within_tolerance`` is the count of rows that
+    fold within ``COP_ASK_TOLERANCE`` of the ask while the window says the
+    draw does not follow it (the defect: nonzero at the base, 0 at the head).
+  * ``synthetic`` (no bundle): a 14 kW / 1.0 kW install whose draw is 2.2 kW
+    whatever it is asked (``selfset``, a flow set-point's shape), and its null
+    control whose draw is 1.3 x the ask (``follows``); 12 intervals asked
+    2.1 kW drawn 2.2 kW (inside the tolerance) through the coordinator's
+    ``_learn_measured_cop``. ``selfset`` folds 12 at the base, 0 at the head;
+    ``follows`` folds 12 at both ends.
+
+``observability`` is ``accuracy.cop_observability`` on the arm's meters, or
+``absent`` where the tree has no such state (the base).
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_cop_gate.py [BUNDLE.json]
+
+Perturbation: ``--slope-follow`` replaces the owner's draws with 1.3 x the ask;
+``follows_ask`` must turn True and ``folds_within_tolerance`` must stay 0
+(nothing departs), while the folds count rises (direction: up).
+Null control: the ``follows`` synthetic arm folds every interval at both ends.
+"""
+from __future__ import annotations
+
+import argparse
+import json
+import sys
+
+sys.path.insert(0, "tests")
+sys.path.insert(0, "custom_components")
+
+from harness import FakeEntry, FakeHass, FakeState  # noqa: E402
+
+from heatpump_optimizer import accuracy, draw_range  # noqa: E402
+from heatpump_optimizer.accuracy import COP_ASK_TOLERANCE, MeasuredCop  # noqa: E402
+from heatpump_optimizer.coordinator import HeatPumpOptimizerCoordinator  # noqa: E402
+from heatpump_optimizer.thermal_model import ThermalParameters  # noqa: E402
+
+CFG = {
+    "tibber_token": "x", "weather_entity": "weather.home",
+    "indoor_temp_entity": "sensor.indoor", "outdoor_temp_entity": "sensor.outdoor",
+    "heat_pump_power_entity": "sensor.pump_power",
+    "heat_pump_max_power": 14.0, "heat_pump_min_power": 1.0,
+}
+STATES = {
+    "sensor.indoor": FakeState("21.0", unit="°C"),
+    "sensor.outdoor": FakeState("8.0", unit="°C"),
+    "sensor.pump_power": FakeState("2200", unit="W"),
+}
+
+
+def observability(electric: bool, heat: bool, follows: bool | None) -> str:
+    rule = getattr(accuracy, "cop_observability", None)
+    return "absent" if rule is None else rule(electric=electric, measured_heat=heat, follows=follows)
+
+
+def synthetic(shape: str) -> tuple[int, str | None, str]:
+    coord = HeatPumpOptimizerCoordinator(FakeHass(dict(STATES)), FakeEntry(data=dict(CFG)))
+    window = draw_range.DrawRange()
+    for i in range(96):
+        ask = (1.2, 1.6, 2.0, 2.4)[i % 4]
+        window.observe(2.2 if shape == "selfset" else 1.3 * ask, ask, 1.0, 14.0)
+    coord._accuracy.draw = window
+    coord._cop_ratio_ewma = 1.0
+    for _ in range(12):
+        coord._current_action = {"power": 2.1, "dhw_power": 0.0}
+        coord._measured_power = 2.2
+        coord._current_state.outdoor_temperature = 8.0
+        coord._learn_measured_cop(coord._accuracy.draw)
+    return coord._cop_samples, coord._measured_cop.refusal, observability(True, False, draw_range.follows_ask(window))
+
+
+def owner(path: str, slope_follow: bool) -> None:
+    data = json.load(open(path))["data"]
+    cfg = dict(data["config"])
+    stores = data["debug"]["stores"]
+    rows = []
+    for s in stores[next(k for k in stores if k.endswith("_accuracy"))]["accuracy"]["samples"]:
+        ask, drawn = s.get("predicted_power_kw"), s.get("actual_power_kw")
+        if ask is None or drawn is None:
+            continue
+        rows.append((float(ask), 1.3 * float(ask) if slope_follow else float(drawn)))
+    p = ThermalParameters.from_config(cfg)
+    window = draw_range.DrawRange()
+    for ask, drawn in rows:
+        if draw_range.is_running_space(drawn, ask, 0.0, frozen=False, distorted=False, defrost=False):
+            window.observe(drawn, ask, p.min_electrical_power, p.max_electrical_power)
+    follows = draw_range.follows_ask(window)
+    folds = within = 0
+    ewma = 1.0
+    for ask, drawn in rows:
+        if ask <= 0.0 or MeasuredCop.judge_floor(ask, drawn, p) is not None:
+            continue
+        ratio = drawn / max(ask, 1e-6)
+        prev, ewma = ewma, 0.9 * ewma + 0.1 * ratio
+        if MeasuredCop.judge_ratio(ratio, prev, ask, p, window) is None:
+            folds += 1
+            within += int(abs(ratio - 1.0) <= COP_ASK_TOLERANCE)
+    heat = bool(cfg.get("heat_pump_heat_energy_entity") or cfg.get("heat_pump_thermal_power_entity"))
+    print(f"RESULT owner.rows={len(rows)} running_pairs={len(window.samples)} follows_ask={follows}")
+    print(f"RESULT owner.folds={folds} folds_within_tolerance={within}")
+    print(f"RESULT owner.heat_metered={heat} observability={observability(bool(cfg.get('heat_pump_power_entity')), heat, follows)}")
+
+
+def main() -> None:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("bundle", nargs="?")
+    ap.add_argument("--slope-follow", action="store_true")
+    a = ap.parse_args()
+    for shape in ("selfset", "follows"):
+        n, why, obs = synthetic(shape)
+        print(f"RESULT synthetic.{shape}.folded={n}/12 refusal={why} observability={obs}")
+    if a.bundle:
+        owner(a.bundle, a.slope_follow)
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/audit/rounds/round10/study-ident/owner_rows.py b/dev/audit/rounds/round10/study-ident/owner_rows.py
index 9667938b2..655684e5e 100644
--- a/dev/audit/rounds/round10/study-ident/owner_rows.py
+++ b/dev/audit/rounds/round10/study-ident/owner_rows.py
@@ -234,7 +234,8 @@ def main():
     n_replay = sum(sum(c.values()) for c in per_bin_day.values())
     for label, rate in (("production", (tl.get("cop_samples") or 0) / max(span_days, 1e-9)),
                         ("replay", n_replay / max(span_days, 1e-9))):
-        counts = collections.Counter({int(k): int(v[1]) for k, v in stored.items()})
+        # space bins only: a "<bin>:dhw" key is the hot-water curve's (#2262 port)
+        counts = collections.Counter({int(k): int(v[1]) for k, v in stored.items() if ":" not in k})
         first, reached = None, {}
         for day in range(1, 366):
             mu = a.t_mean + a.t_slope * day
diff --git a/dev/programme/delivery/2917.md b/dev/programme/delivery/2917.md
new file mode 100644
index 000000000..ba91c3ef3
--- /dev/null
+++ b/dev/programme/delivery/2917.md
@@ -0,0 +1 @@
+- [#2917](https://github.com/tvofi/heatpump_optimizer/pull/2917) — **open**, R10-COP-GATE part 1: COP observability state, L3 draw-follows refusal, latch time, draw pairing
diff --git a/tests/closures.json b/tests/closures.json
index 5b8a18073..af5ada08b 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3696,6 +3696,7 @@
    "dev/audit/harnesses/r10_cloud_setup_toolchain.py",
    "dev/audit/harnesses/r10_codescan_wait_race.py",
    "dev/audit/harnesses/r10_configflow_pages.py",
+   "dev/audit/harnesses/r10_cop_gate.py",
    "dev/audit/harnesses/r10_critpath_archive_parity.py",
    "dev/audit/harnesses/r10_dead_rate_limit.py",
    "dev/audit/harnesses/r10_demand_overbook.py",
diff --git a/tests/entities.py b/tests/entities.py
index 94258619f..36e58ddb6 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4077,7 +4077,7 @@ def _p2_registry(sources):
                      "a temperature gap in K (target minus room), not a power",
                  "coordinator.py::HeatPumpOptimizerCoordinator._maybe_run_fuse_advisor":
                      "a comfort shortfall in K (the fuse advisor's breach), not a power",
-                 "coordinator.py::HeatPumpOptimizerCoordinator._record_accuracy":
+                 "accuracy.py::pairs_interval":
                      "an elapsed time in hours (the pairing window's lower edge), not a power",
                  "dhw_learning.py::DhwProfileLearner.async_learn_usage":
                      "a tank draw intensity in K/h, not a power",
@@ -6139,6 +6139,37 @@ R.check(
     == "measured_power_entity",
 )
 
+# R10-COP-GATE (#2262): where the draw does not follow the plan's ask and no
+# heat reading exists, a latched COP is no reading of this install: the sensor
+# waits for a heat meter instead of showing it. A heat counter's open span is
+# its own code beside a measured COP, never a refusal, and the latch's time
+# rides with it.
+_cg_cop = {
+    obs: sensor.ObservedCOPSensor(FakeCoordinator({
+        **DATA, "measured_cop": 2.4, "cop_observability": obs,
+        "cop_refusal": "span_open" if obs == "heat_metered" else "draw_off_ask",
+        "measured_cop_at": "2026-10-24T03:00:00+00:00",
+    }), ENTRY)
+    for obs in ("not_measurable", "heat_metered", "draw_follows_plan")
+}
+_cg_view = {
+    obs: (ent.available, ent.extra_state_attributes.get("waiting_for"),
+          ent.extra_state_attributes.get("last_refusal"),
+          ent.extra_state_attributes.get("measured_at"))
+    for obs, ent in _cg_cop.items()
+}
+R.check(
+    "a COP not measurable here waits for a heat meter; a heat-metered COP "
+    "between span closes stays measured with span_open as its code; a draw "
+    "that follows the plan keeps its COP (null); each carries its fold time",
+    _cg_view == {
+        "not_measurable": (False, "heat_meter", "draw_off_ask", "2026-10-24T03:00:00+00:00"),
+        "heat_metered": (True, None, "span_open", "2026-10-24T03:00:00+00:00"),
+        "draw_follows_plan": (True, None, "draw_off_ask", "2026-10-24T03:00:00+00:00"),
+    },
+    f"{_cg_view!r}",
+)
+
 # --- a failed refresh reaches every entity ----------------------------------
 R.section("A failed refresh reaches every entity")
 
@@ -12379,7 +12410,8 @@ _PUBLISHED_ATTRS: dict[str, frozenset[str]] = {
     ),
     "ObservedCOPSensor": frozenset({
         "cop_samples", "cop_scale", "defrost_buckets", "defrost_derate",
-        "defrost_samples", "modelled_cop", "waiting_for"
+        "defrost_samples", "modelled_cop", "waiting_for",
+        "measured_at", "last_refusal", "observability",  # R10-COP-GATE (#2262)
     }),
     "OptimizationScoreSensor": frozenset(),  # scores + price_tiles; #405
     "OptimizationStatusSensor": frozenset({
diff --git a/tests/features.py b/tests/features.py
index 377f3e1ae..3c3382a94 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -60497,6 +60497,8 @@ _P3_FILES = (
     # against moved here from ``_cop_reference_curve``, so its calls stay
     # under the rule instead of leaving it with the move.
     "flow_meter.py",
+    # R10-COP-GATE (#2262): the accuracy residual moved to MeasuredCop.residual.
+    "accuracy.py",
 )
 _P3_ALLOWED = {
     # (file, function, callee, first argument): why the current humidity
@@ -60510,9 +60512,9 @@ _P3_ALLOWED = {
         "the same reference, at the supply a metered interval ran at",
     ("coordinator.py", "_cop_reference_curve", "compute_cop_dhw", "outdoor"):
         "the same reference, for a hot-water interval",
-    ("coordinator.py", "_record_accuracy", "compute_cop_dhw", "sample.outdoor_temp"):
+    ("accuracy.py", "residual", "compute_cop_dhw", "outdoor"):
         "the residual of the interval that just ended",
-    ("coordinator.py", "_record_accuracy", "compute_cop", "sample.outdoor_temp"):
+    ("accuracy.py", "residual", "compute_cop", "outdoor"):
         "the same residual, for a space interval",
     ("coordinator.py", "_run_system_identification", "compute_cop",
      "state.outdoor_temperature"): "the experiment step running now",
@@ -67089,6 +67091,168 @@ R.check(
 )
 
 
+# ---------------------------------------------------------------------------
+R.section("R10-COP-GATE (#2262): COP observability, the latch's time, and the draw pairing")
+
+# Without a heat reading the ratio of draw to ask is a COP only while the draw
+# follows the ask. Once the running-draw window shows it does not
+# (follows_ask False), an interval that lands within COP_ASK_TOLERANCE of its
+# ask only happened to: a pump whose own controller (or a flow set-point) sets
+# the draw folds nothing, while one whose draw follows still folds.
+from heatpump_optimizer import accuracy as _cg_acc  # noqa: E402
+
+
+def _cg_fold_near_ask(window_pairs, n=12):
+    coord = _cf_coord()
+    coord._accuracy.draw = _cf_window(window_pairs)
+    coord._cop_ratio_ewma = 1.0
+    for _ in range(n):
+        coord._current_action = {"power": 2.1, "dhw_power": 0.0}
+        coord._measured_power = 2.2  # 4.8 % over the ask: inside the tolerance
+        coord._current_state.outdoor_temperature = 8.0
+        coord._learn_measured_cop(coord._accuracy.draw)
+    return coord
+
+
+_cg_selfset = _cg_fold_near_ask([(a, 2.2) for a, _ in _cf_prop])
+_cg_follows = _cg_fold_near_ask([(a, 1.3 * a) for a, _ in _cf_prop])
+R.check(
+    "a draw the window shows ignores its ask folds nothing, even within the ask "
+    "tolerance; a draw that follows its ask still folds every interval (null)",
+    _cf_drm.follows_ask(_cg_selfset._accuracy.draw) is False
+    and _cg_selfset._cop_samples == 0
+    and _cf_last(_cg_selfset, "refusal") == _cg_acc.COP_REFUSED_OFF_ASK
+    and _cf_drm.follows_ask(_cg_follows._accuracy.draw) is True
+    and _cg_follows._cop_samples == 12,
+    f"self-set {_cg_selfset._cop_samples}/12 ({_cf_last(_cg_selfset, 'refusal')}); "
+    f"follows {_cg_follows._cop_samples}/12",
+)
+
+# The observability state the payload publishes: a heat reading (the heat
+# counter, or the thermal power entity) measures the COP whatever the draw
+# does; without one, the draw window decides; without an electrical figure to
+# divide by there is none. A heat counter divides by its electric counter.
+_cg_obs = _cg_acc.cop_observability
+R.check(
+    "cop_observability: heat metered beats a draw that ignores the ask; no "
+    "electrical figure is no COP; the draw window decides the rest",
+    _cg_obs(electric=True, measured_heat=True, follows=False) == "heat_metered"
+    and _cg_obs(electric=False, measured_heat=True, follows=True) == "no_electric_meter"
+    and _cg_obs(electric=True, measured_heat=False, follows=False) == "not_measurable"
+    and _cg_obs(electric=True, measured_heat=False, follows=True) == "draw_follows_plan"
+    and _cg_obs(electric=True, measured_heat=False, follows=None) == "awaiting_draw_evidence",
+)
+
+
+def _cg_install_obs(selfset=True, **extra):
+    cfg = dict(_L5_CFG, heat_pump_max_power=14.0, heat_pump_min_power=1.0, **extra)
+    coord = _Coord(_FakeHass(dict(_CF_STATES)), _FakeEntry(data=cfg))
+    coord._accuracy.draw = _cf_window([(a, 2.2 if selfset else 1.3 * a) for a, _ in _cf_prop])
+    return coord._learning_view()["cop_observability"]
+
+
+_cg_states = {
+    "power, self-set draw": _cg_install_obs(),
+    "power, following draw": _cg_install_obs(selfset=False),
+    "thermal power, self-set draw": _cg_install_obs(heat_pump_thermal_power_entity="sensor.heat_kw"),
+    "heat counter, no electric counter": _cg_install_obs(heat_pump_heat_energy_entity="sensor.heat_kwh"),
+    "heat counter and electric counter": _cg_install_obs(
+        heat_pump_heat_energy_entity="sensor.heat_kwh", heat_pump_energy_entity="sensor.elec_kwh"),
+}
+R.check(
+    "the coordinator's state: a self-set draw with no heat reading is not "
+    "measurable, a thermal-power install never is, and a heat counter without "
+    "an electric counter has nothing to divide by",
+    _cg_states == {
+        "power, self-set draw": "not_measurable",
+        "power, following draw": "draw_follows_plan",
+        "thermal power, self-set draw": "heat_metered",
+        "heat counter, no electric counter": "no_electric_meter",
+        "heat counter and electric counter": "heat_metered",
+    },
+    f"{_cg_states!r}",
+)
+
+# The latch outlives every later refusal, so the time it folded is kept with
+# it, round-trips the store, and a record stored before the instant was loads
+# with its age unknown, never now.
+_cg_t = _cf_coord()
+_cf_learn(_cg_t, 2.0, 1)
+_cg_at = _cg_t._measured_cop.at
+_cg_back = _cf_MC.from_dict(_cg_t._measured_cop.as_dict())
+R.check(
+    "a folded COP carries the instant it folded, through the store and back; an "
+    "old record loads with no instant, and a malformed one drops whole",
+    _cg_at is not None and _cg_back.at == _cg_at and _cg_back.cop == _cg_t._measured_cop.cop
+    and _cf_MC.from_dict({"cop": 2.0}).at is None and _cf_MC.from_dict({"cop": 2.0}).cop == 2.0
+    and _cf_MC.from_dict({"cop": 2.0, "at": "not a time"}).cop is None,
+    f"at {_cg_at!r} -> {_cg_back.at!r}",
+)
+R.check(
+    "the accuracy residual reads the latch only for the interval it folded in: "
+    "an interval opened at or after the fold gets none (#2262 seam 3), one "
+    "opened before it gets observed minus modelled",
+    _cg_t._measured_cop.residual(_cg_at + timedelta(minutes=1), 8.0, _cg_t._thermal_model) is None
+    and _cg_t._measured_cop.residual(_cg_at, 8.0, _cg_t._thermal_model) is None
+    and _cg_t._measured_cop.residual(_cg_at - timedelta(minutes=30), 8.0, _cg_t._thermal_model)
+    == round(_cg_t._measured_cop.cop - _cg_t._thermal_model.compute_cop(8.0), 3),
+)
+# The residual is referenced to the curve the COP was observed on: the
+# hot-water curve only where the fold said so AND named its tank temperature.
+_cg_model = _cg_t._thermal_model
+_cg_space, _cg_dhw = _cf_MC(), _cf_MC()
+_cg_space.record(3.0, False, 50.0, _cg_at)
+_cg_dhw.record(3.0, True, 50.0, _cg_at)
+_cg_since = _cg_at - timedelta(minutes=30)
+R.check(
+    "the residual subtracts the curve the COP folded on: a space-heating fold "
+    "that happens to carry a tank temperature reads the space curve, a "
+    "hot-water fold the hot-water curve at its tank temperature",
+    _cg_model.compute_cop_dhw(8.0, 50.0) != _cg_model.compute_cop(8.0)
+    and _cg_space.residual(_cg_since, 8.0, _cg_model) == round(3.0 - _cg_model.compute_cop(8.0), 3)
+    and _cg_dhw.residual(_cg_since, 8.0, _cg_model) == round(3.0 - _cg_model.compute_cop_dhw(8.0, 50.0), 3),
+    f"space {_cg_space.residual(_cg_since, 8.0, _cg_model)!r}, dhw {_cg_dhw.residual(_cg_since, 8.0, _cg_model)!r}",
+)
+from heatpump_optimizer.accuracy import pairs_interval as _cg_pairs  # noqa: E402
+R.check(
+    "a pending prediction pairs with the interval that closed from 3 minutes to "
+    "2 hours old, both ends included; a re-run sooner or a gap longer pairs nothing",
+    _cg_pairs(0.05) and _cg_pairs(2.0) and _cg_pairs(1.0)
+    and not _cg_pairs(0.049) and not _cg_pairs(2.001),
+)
+
+
+# The meter read at a cycle closes the interval the PREVIOUS cycle's plan
+# governed; _record_accuracy runs after the solve adopted the next action, so
+# the draw window pairs each reading with the pending prediction's ask, never
+# the next step's.
+def _cg_pair(next_ask):
+    coord = _cf_coord()
+    coord._current_state.outdoor_temperature = 8.0
+    coord._current_action = {"power": 1.5, "dhw_power": 0.0}
+    coord._measured_power = 1.5
+    coord._record_accuracy()
+    coord._pending_prediction["when"] -= timedelta(minutes=30)
+    coord._measured_cop.record(3.0, False, None, coord._pending_prediction["when"] - timedelta(hours=5))
+    coord._current_action = {"power": next_ask, "dhw_power": 0.0}
+    coord._measured_power = 1.5
+    coord._record_accuracy()
+    last = coord._accuracy.samples[-1] if coord._accuracy.samples else None
+    return list(coord._accuracy.draw.samples), getattr(last, "cop_residual", "<none>")
+
+
+_cg_moved, _cg_moved_res = _cg_pair(3.0)
+_cg_same, _ = _cg_pair(1.5)
+R.check(
+    "the draw window pairs the closed interval's reading with that interval's "
+    "own ask (1.5 kW), not the 3.0 kW the solve adopted next; an unchanged ask "
+    "pairs alike (null); a COP latched hours earlier leaves the sample's "
+    "residual empty",
+    _cg_moved == [(1.5, 1.5)] and _cg_same == [(1.5, 1.5)] and _cg_moved_res is None,
+    f"moved {_cg_moved!r} residual {_cg_moved_res!r}; same {_cg_same!r}",
+)
+
+
 # R9-UX-6: money and memory -- the receipt, the capacity line, the replay
 # ---------------------------------------------------------------------------
 from harness import FakeEntry as _ux6_Entry, FakeHass as _ux6_Hass  # noqa: E402
@@ -67724,7 +67888,16 @@ for _dr_label, _dr_args in (
     )
 
 
-# The fold, from the coordinator's per-cycle settlement.
+# The fold, from the coordinator's per-cycle settlement. The meter read at a
+# cycle closes the interval the previous cycle's prediction governed (#2262),
+# so a settlement is two cycles half an hour apart: the first records the
+# prediction, the second folds the reading against it.
+def _dr_settle(c):
+    c._record_accuracy()
+    c._pending_prediction["when"] -= timedelta(minutes=30)
+    c._record_accuracy()
+
+
 def _dr_coord(**extra):
     c = _DrCoord(FakeHass(), _dr_entry(data={
         "tibber_token": "x", "weather_entity": "weather.home", **extra}))
@@ -67734,7 +67907,7 @@ def _dr_coord(**extra):
 
 
 _dr_cycle = _dr_coord()
-_dr_cycle._record_accuracy()
+_dr_settle(_dr_cycle)
 R.check(
     "the per-cycle settlement folds one running sample: (drawn, space asked)",
     list(_dr_cycle._accuracy.draw.samples) == [(2.3, 6.0)],
@@ -67747,14 +67920,14 @@ for _dr_label, _dr_mut in (
 ):
     _dr_c = _dr_coord()
     _dr_mut(_dr_c)
-    _dr_c._record_accuracy()
+    _dr_settle(_dr_c)
     R.check(
         f"and folds nothing under {_dr_label}",
         len(_dr_c._accuracy.draw.samples) == 0,
     )
 _dr_frost = _dr_coord()
 _dr_frost._defrost_window.close = lambda now: _DrDefrost(events=1, observed=True)
-_dr_frost._record_accuracy()
+_dr_settle(_dr_frost)
 R.check(
     "and folds nothing for an interval whose closed window saw a defrost",
     len(_dr_frost._accuracy.draw.samples) == 0,
@@ -68039,7 +68212,7 @@ def _bst_coord(**extra):
     c._current_action = {"power": 6.0, "dhw_power": 0.0}
     c._measured_power = 2.3
     _bst_pa.state_for(c).written["space_setpoint"] = (40.0, _BST_T0)
-    c._record_accuracy()
+    _dr_settle(c)
     return list(getattr(c._accuracy.draw, "commands", [None]))
 
 
diff --git a/tests/finite_boundary.py b/tests/finite_boundary.py
index 0a23a3789..b91409b92 100644
--- a/tests/finite_boundary.py
+++ b/tests/finite_boundary.py
@@ -1723,7 +1723,7 @@ def _a6_enrich(coord, t0) -> None:
         dhw_slots=None, expires_at=_A4_NOW + _dt.timedelta(hours=6), created_at=t0)
     coord._away_state.migrated_helpers = True
     coord._flow_bias.bias_k, coord._flow_bias.samples = 2.5, 4
-    coord._measured_cop.record(3.17, True, 52.5)
+    coord._measured_cop.record(3.17, True, 52.5, t0 - _dt.timedelta(hours=2))
     learner = coord._dhw_learner
     for name, low in (("hourly_profile", 0.5), ("profile_weekday", 0.75), ("profile_weekend", 0.25)):
         # Dyadic, mean exactly 1: the loader's renormalisation is the identity
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index ccd1d1a06..582f22ba1 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -67,6 +67,15 @@
 # env_drift --all against origin/main df478d40b in one environment: exactly
 # these five move, in that one key, "present on one side only". The committed
 # files were patched in that path alone; no other leaf was re-recorded.
+# R10-COP-GATE (#2262): the payload gains `measured_cop_at` (when the latched
+# COP folded), `cop_refusal` (the latest interval's refusal code) and
+# `cop_observability` (accuracy.cop_observability), and the observed-COP
+# sensor publishes them as `measured_at`, `last_refusal` and `observability`.
+# Direction: ADD-ONLY, six leaves per coord fixture: null, null and
+# "no_electric_meter" in all five (no capture configures a power entity). The
+# committed files were patched in exactly those 30 paths from
+# golden.capture_coordinator at the head (a json round-trip of each file is
+# byte-identical before the patch); no other leaf was re-recorded.
 # R10-CARD-VOICE: describe_setup publishes the wood-coil option itself as
 # `dhw_wood_coil_configured`, beside the model's `dhw_wood_coil` gate, so the
 # card can say "configured, not modelled". Direction: ADD-ONLY, one leaf in
@@ -122,16 +131,11 @@
 # one was restored.
 #
 #
-# (R10-BUFFER-STORE suspends valve_storage_smart_write's may-drift entry for its claim below; restore it,
-#  verbatim, when the stamp empties the list) valve_storage_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
-# (R10-BUFFER-STORE suspends wood_two_tank's may-drift entry for its claim below; restore it,
-#  verbatim, when the stamp empties the list) wood_two_tank -- machine-sensitive; the DHW plan can reach it, per local optimum
-# (R10-BUFFER-STORE suspends wood_two_tank_smart_write's may-drift entry for its claim below; restore it,
-#  verbatim, when the stamp empties the list) wood_two_tank_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
-# (R10-BUFFER-STORE suspends wood_coil's may-drift entry for its claim below; restore it,
-#  verbatim, when the stamp empties the list) wood_coil -- machine-sensitive; the DHW plan can reach it, per local optimum
-# (R10-BUFFER-STORE suspends valve_upper_direct_slab's may-drift entry for its claim below; restore it,
-#  verbatim, when the stamp empties the list) valve_upper_direct_slab -- machine-sensitive; the DHW plan can reach it, per local optimum
+# may-drift: valve_storage_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
+# may-drift: wood_two_tank -- machine-sensitive; the DHW plan can reach it, per local optimum
+# may-drift: wood_two_tank_smart_write -- machine-sensitive; the DHW plan can reach it, per local optimum
+# may-drift: wood_coil -- machine-sensitive; the DHW plan can reach it, per local optimum
+# may-drift: valve_upper_direct_slab -- machine-sensitive; the DHW plan can reach it, per local optimum
 # may-drift: winter_two_zone_no_dhw -- #1208 polish-every-candidate, owner
 # ruling #1208 comment 208bed25 (option (a)): the move's margin is inside the
 # noise band (objective rel -1.3365e-03, predicted_cost rel +8.39e-03),
@@ -216,8 +220,7 @@
 # byte-identical on the dev box), runner-conditional for the same reason;
 # judged keys still fail. Remove when drift lanes are pinned or the polish
 # improvement scale leaves 5e-5-2e-2.
-# (R10-BUFFER-STORE suspends valve_storage's may-drift entry for its claim below; restore it,
-#  verbatim, when the stamp empties the list) valve_storage -- #1207 keep-gate (2e-2 -> 2e-5), widened to
+# may-drift: valve_storage -- #1207 keep-gate (2e-2 -> 2e-5), widened to
 # the runner's union by the owner's ruling (i) on the options recorded in
 # #1207 comment 1ec15c8 (2026-09-20): 625 leaves moved on the CI
 # x86_64/py3.14 runner only (as recorded on that comment; byte-identical
@@ -763,11 +766,11 @@
 # was re-recorded: a claim excuses drift but not a structurally stale fixture
 # (`env_drift --all`'s `rot.failed`), which is the `tests / fast` red that
 # patch answers.
-coord_all_features  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
-coord_dhw  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
-coord_grid_fee  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
-coord_minimal  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
-coord_two_zone  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers and sensors.optimization_score.extra_state_attributes.envelope_drivers added
+coord_all_features  # R10-COP-GATE (#2262): data.measured_cop_at|cop_refusal|cop_observability and sensors.observed_cop.extra_state_attributes.measured_at|last_refusal|observability added
+coord_dhw  # R10-COP-GATE (#2262): data.measured_cop_at|cop_refusal|cop_observability and sensors.observed_cop.extra_state_attributes.measured_at|last_refusal|observability added
+coord_grid_fee  # R10-COP-GATE (#2262): data.measured_cop_at|cop_refusal|cop_observability and sensors.observed_cop.extra_state_attributes.measured_at|last_refusal|observability added
+coord_minimal  # R10-COP-GATE (#2262): data.measured_cop_at|cop_refusal|cop_observability and sensors.observed_cop.extra_state_attributes.measured_at|last_refusal|observability added
+coord_two_zone  # R10-COP-GATE (#2262): data.measured_cop_at|cop_refusal|cop_observability and sensors.observed_cop.extra_state_attributes.measured_at|last_refusal|observability added
 # R10-BUFFER-STORE (#2887 review 1): behind a valve the savings reference
 # charges its tank only to the configured curve (`valve_charge_demand`) and
 # prices its draw at the tank's flow COP (`_reference_cop`), as the step
@@ -782,12 +785,3 @@ coord_two_zone  # R10-HOUSE-GRADE (#2816): data.insight.scores.envelope_drivers
 # valve_storage_low_target, whose plan leaves move too: the reference's energy
 # anchors three of the space solve's starts, so a valved plan can land in
 # another basin. Unvalved fixtures do not move.
-valve_storage_smart_write  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 146.865 -> 129.695 here; no plan key judged
-valve_upper_direct_slab  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost UP 125.709 -> 126.782 here; no plan key judged
-wood_coil  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 150.751 -> 129.566 here; no plan key judged
-wood_two_tank  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 141.475 -> 120.254 here; no plan key judged
-wood_two_tank_smart_write  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 141.475 -> 120.254 here; no plan key judged
-valve_storage  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 146.865 -> 129.695 here; no plan key judged
-valve_storage_flat_prices  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 113.116 -> 102.374 here; plan leaves move with the reference-anchored starts
-valve_storage_low_target  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 195.205 -> 111.103 here; plan leaves move with the reference-anchored starts
-valve_storage_small_tank  # R10-BUFFER-STORE: tank-aware savings reference; baseline_cost DOWN 151.266 -> 128.078 here, predicted_savings and deferred_energy_cost with it
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index 0545d231a..931c703fe 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -106,6 +106,8 @@
    "evidence": [],
    "watched_buckets": 0
   },
+  "cop_observability": "no_electric_meter",
+  "cop_refusal": null,
   "cop_samples": 0,
   "cop_scale": 1.0,
   "currency": "SEK",
@@ -374,6 +376,7 @@
   "lower_floor_temperature": 21.0,
   "max_temperature": 23.0,
   "measured_cop": null,
+  "measured_cop_at": null,
   "measured_energy": null,
   "measured_heat_output_kw": null,
   "measured_house_power": null,
@@ -2171,7 +2174,10 @@
     "defrost_buckets": [],
     "defrost_derate": 1.0,
     "defrost_samples": 0,
+    "last_refusal": null,
+    "measured_at": null,
     "modelled_cop": 3.32,
+    "observability": "no_electric_meter",
     "waiting_for": "measured_power_entity"
    },
    "native_value": null
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index 84078c1fc..9f29db493 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -106,6 +106,8 @@
    "evidence": [],
    "watched_buckets": 0
   },
+  "cop_observability": "no_electric_meter",
+  "cop_refusal": null,
   "cop_samples": 0,
   "cop_scale": 1.0,
   "currency": "SEK",
@@ -374,6 +376,7 @@
   "lower_floor_temperature": 21.0,
   "max_temperature": 23.0,
   "measured_cop": null,
+  "measured_cop_at": null,
   "measured_energy": null,
   "measured_heat_output_kw": null,
   "measured_house_power": null,
@@ -2092,7 +2095,10 @@
     "defrost_buckets": [],
     "defrost_derate": 1.0,
     "defrost_samples": 0,
+    "last_refusal": null,
+    "measured_at": null,
     "modelled_cop": 3.32,
+    "observability": "no_electric_meter",
     "waiting_for": "measured_power_entity"
    },
    "native_value": null
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index 74b69a15c..3087f9e10 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -96,6 +96,8 @@
    "evidence": [],
    "watched_buckets": 0
   },
+  "cop_observability": "no_electric_meter",
+  "cop_refusal": null,
   "cop_samples": 0,
   "cop_scale": 1.0,
   "currency": "SEK",
@@ -309,6 +311,7 @@
   "lower_floor_temperature": 21.0,
   "max_temperature": 23.0,
   "measured_cop": null,
+  "measured_cop_at": null,
   "measured_energy": null,
   "measured_heat_output_kw": null,
   "measured_house_power": null,
@@ -1931,7 +1934,10 @@
     "defrost_buckets": [],
     "defrost_derate": 1.0,
     "defrost_samples": 0,
+    "last_refusal": null,
+    "measured_at": null,
     "modelled_cop": 3.32,
+    "observability": "no_electric_meter",
     "waiting_for": "measured_power_entity"
    },
    "native_value": null
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index bc4938d73..bccc3b3a7 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -96,6 +96,8 @@
    "evidence": [],
    "watched_buckets": 0
   },
+  "cop_observability": "no_electric_meter",
+  "cop_refusal": null,
   "cop_samples": 0,
   "cop_scale": 1.0,
   "currency": "SEK",
@@ -309,6 +311,7 @@
   "lower_floor_temperature": 21.0,
   "max_temperature": 23.0,
   "measured_cop": null,
+  "measured_cop_at": null,
   "measured_energy": null,
   "measured_heat_output_kw": null,
   "measured_house_power": null,
@@ -1931,7 +1934,10 @@
     "defrost_buckets": [],
     "defrost_derate": 1.0,
     "defrost_samples": 0,
+    "last_refusal": null,
+    "measured_at": null,
     "modelled_cop": 3.32,
+    "observability": "no_electric_meter",
     "waiting_for": "measured_power_entity"
    },
    "native_value": null
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index 321cc5250..20caa9416 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -106,6 +106,8 @@
    "evidence": [],
    "watched_buckets": 0
   },
+  "cop_observability": "no_electric_meter",
+  "cop_refusal": null,
   "cop_samples": 0,
   "cop_scale": 1.0,
   "currency": "SEK",
@@ -319,6 +321,7 @@
   "lower_floor_temperature": 21.0,
   "max_temperature": 23.0,
   "measured_cop": null,
+  "measured_cop_at": null,
   "measured_energy": null,
   "measured_heat_output_kw": null,
   "measured_house_power": null,
@@ -1977,7 +1980,10 @@
     "defrost_buckets": [],
     "defrost_derate": 1.0,
     "defrost_samples": 0,
+    "last_refusal": null,
+    "measured_at": null,
     "modelled_cop": 3.32,
+    "observability": "no_electric_meter",
     "waiting_for": "measured_power_entity"
    },
    "native_value": null
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json
new file mode 100644
index 000000000..9889b2605
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.as_dict RETURN_DEL 62858a00",
+  "killed_by": "tests/features.py",
+  "old": "        return {\"cop\": self.cop, \"curve_dhw\": self.curve_dhw, \"dhw_temp\": self.dhw_temp, \"at\": at}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.6f8909cf.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.6f8909cf.json
deleted file mode 100644
index 45b224539..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.6f8909cf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.as_dict RETURN_DEL 6f8909cf",
-  "killed_by": "tests/features.py",
-  "old": "        return {\"cop\": self.cop, \"curve_dhw\": self.curve_dhw, \"dhw_temp\": self.dhw_temp}",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.4cb095ac.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.4cb095ac.json
deleted file mode 100644
index 92fe18ad9..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.4cb095ac.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict BOOLOP 4cb095ac",
-  "killed_by": "tests/features.py",
-  "old": "        if temp is not None and not np.isfinite(temp):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: BOOLOP (`if temp is not None or not np.isfinite(temp):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.4cb095ac.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.4cb095ac.json
deleted file mode 100644
index 2740799f8..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.4cb095ac.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict GUARD_OFF 4cb095ac",
-  "killed_by": "tests/features.py",
-  "old": "        if temp is not None and not np.isfinite(temp):",
-  "reason": "Hand-recorded by the #2066 fixer at 4bf7bdde1 against the ratchet base b2b6acd64, not by `--pin-killed` (whose baselines need CI's Linux floats). `GUARD_OFF` (if False:) flips the condition of tests/features.py's R.check \"an unreadable stored COP record loads as no measurement, whole\" -- the new check \"a non-finite tank temperature drops the record whole\" reads False: switching the guard off keeps cop 2.0 with a nan temperature. Measured by copying the package, rewriting that one line to the operator's own text and re-evaluating the check's condition: baseline True, mutant as stated (evidence table in the pull request's body, `## Unpinned sites`). CI's `--pin-killed` at a pull_request head re-measures the driver itself."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json
new file mode 100644
index 000000000..8d9f32542
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict GUARD_OFF 649d9952",
+  "killed_by": "tests/features.py",
+  "old": "        if (temp is not None and not np.isfinite(temp)) or (raw.get(\"at\") is not None and at is None):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.7c227e9b.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.7c227e9b.json
deleted file mode 100644
index 2dc963923..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.7c227e9b.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict RETURN_DEL 7c227e9b",
-  "killed_by": "tests/features.py",
-  "old": "        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json
new file mode 100644
index 000000000..99b0be279
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict RETURN_DEL 81cd12e3",
+  "killed_by": "tests/features.py",
+  "old": "        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp, at=at)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.602baa33.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.602baa33.json
new file mode 100644
index 000000000..b1e54f706
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.602baa33.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio GUARD_OFF 602baa33",
+  "killed_by": "tests/features.py",
+  "old": "        if follows is False:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.4c7c13c0.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.4c7c13c0.json
deleted file mode 100644
index 9a98ff8de..000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.4c7c13c0.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio RETURN_DEL 4c7c13c0",
-  "killed_by": "tests/features.py",
-  "old": "        return None if follows else COP_REFUSED_OFF_ASK",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.BOOLOP.460915d8.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.BOOLOP.460915d8.json
new file mode 100644
index 000000000..6a037103b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.BOOLOP.460915d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual BOOLOP 460915d8",
+  "killed_by": "tests/features.py",
+  "old": "        if self.curve_dhw and self.dhw_temp is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.curve_dhw or self.dhw_temp is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.CMP_BOUND.92047180.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.CMP_BOUND.92047180.json
new file mode 100644
index 000000000..99a932ad3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.CMP_BOUND.92047180.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual CMP_BOUND 92047180",
+  "killed_by": "tests/features.py",
+  "old": "        if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) < 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.460915d8.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.460915d8.json
new file mode 100644
index 000000000..634115f14
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.460915d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual GUARD_OFF 460915d8",
+  "killed_by": "tests/features.py",
+  "old": "        if self.curve_dhw and self.dhw_temp is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.92047180.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.92047180.json
new file mode 100644
index 000000000..51459c6fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.GUARD_OFF.92047180.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual GUARD_OFF 92047180",
+  "killed_by": "tests/features.py",
+  "old": "        if outdoor is None or self.cop is None or self.at is None or utc_elapsed_seconds(self.at, since) <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.RETURN_DEL.dfd25e72.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.RETURN_DEL.dfd25e72.json
new file mode 100644
index 000000000..aa448a757
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.residual.RETURN_DEL.dfd25e72.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.residual RETURN_DEL dfd25e72",
+  "killed_by": "tests/features.py",
+  "old": "        return round(float(self.cop) - float(modelled), 3)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
new file mode 100644
index 000000000..95594139b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.ac5ca5ae.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF ac5ca5ae",
+  "killed_by": "tests/features.py",
+  "old": "    if measured_heat:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
new file mode 100644
index 000000000..c64de4327
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.c1dafc5f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF c1dafc5f",
+  "killed_by": "tests/features.py",
+  "old": "    if follows is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.f1e23bc3.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.f1e23bc3.json
new file mode 100644
index 000000000..5a0eee47e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.GUARD_OFF.f1e23bc3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability GUARD_OFF f1e23bc3",
+  "killed_by": "tests/features.py",
+  "old": "    if not electric:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
new file mode 100644
index 000000000..57131144a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/cop_observability.RETURN_DEL.e75e96f9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:cop_observability RETURN_DEL e75e96f9",
+  "killed_by": "tests/features.py",
+  "old": "    return COP_DRAW_FOLLOWS if follows else COP_NOT_MEASURABLE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.CMP_BOUND.62f6b3b0.json b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.CMP_BOUND.62f6b3b0.json
new file mode 100644
index 000000000..fa4e849d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.CMP_BOUND.62f6b3b0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:pairs_interval CMP_BOUND 62f6b3b0",
+  "killed_by": "tests/features.py",
+  "old": "    return 0.05 <= elapsed_h <= 2.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return 0.05 < elapsed_h <= 2.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.RETURN_DEL.62f6b3b0.json b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.RETURN_DEL.62f6b3b0.json
new file mode 100644
index 000000000..9d1813586
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/pairs_interval.RETURN_DEL.62f6b3b0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:pairs_interval RETURN_DEL 62f6b3b0",
+  "killed_by": "tests/features.py",
+  "old": "    return 0.05 <= elapsed_h <= 2.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.6cac1c2f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.6cac1c2f.json
new file mode 100644
index 000000000..d7fa362d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.6cac1c2f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF 6cac1c2f",
+  "killed_by": "tests/features.py",
+  "old": "            if pairs_interval(elapsed):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
new file mode 100644
index 000000000..cf6a9c195
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._record_accuracy.GUARD_OFF.b36c07ff.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._record_accuracy GUARD_OFF b36c07ff",
+  "killed_by": "tests/features.py",
+  "old": "        if pending is not None and pending.get(\"split\") is not None and pairs_interval(_utc_age_seconds(now, pending[\"when\"]) / 3600.0):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.204c8b17.json b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.204c8b17.json
new file mode 100644
index 000000000..ecb786441
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/ObservedCOPSensor._waiting_for.GUARD_OFF.204c8b17.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:ObservedCOPSensor._waiting_for GUARD_OFF 204c8b17",
+  "killed_by": "tests/entities.py",
+  "old": "        if data.get(\"cop_observability\") == COP_NOT_MEASURABLE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_electric.RETURN_DEL.1cbe4cb2.json b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_electric.RETURN_DEL.1cbe4cb2.json
new file mode 100644
index 000000000..71d1cda3f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/InstallCapability.cop_electric.RETURN_DEL.1cbe4cb2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:InstallCapability.cop_electric RETURN_DEL 1cbe4cb2",
+  "killed_by": "tests/features.py",
+  "old": "        return self.electric_counter if self.heat_counter else self.measured_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json b/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json
new file mode 100644
index 000000000..511f45f00
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.d7923b87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio RETURN_DEL d7923b87",
+  "old": "        return None",
+  "reason": "Equivalent (RETURN_DEL, `return None` -> `pass`): the statement is the last one in MeasuredCop.judge_ratio, after `if` arms that each return, so deleting it lets the method fall off its own end and return None -- the same value, on every input, to every reader. Measured by the R10-COP-GATE repair seat's `mutation_table.py --pin-killed --base origin/main` over every driver in play (tests/features.py, tests/entities.py, tests/finite_boundary.py, tests/stress.py among them): the site lived, against 15 of the 21 new sites killed in the same drive, among them this method's own `if follows is False` guard (killed by tests/features.py).",
+  "verdict": "equivalent"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index cbc958f16..d492586bc 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17814,
+ "class_excess_loc": 17806,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -11,9 +11,9 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 8155,
+ "max_class_loc": 8147,
  "max_method_loc": 373,
- "methods_over_150": 16,
+ "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
  "recorded_at": "b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa",

