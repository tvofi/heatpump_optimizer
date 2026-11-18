# Review packet #3662
head: 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7
base: 1da13aafb7c23cf34fbda51bb27cb95132b4089b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
arch-score / arch-score id=134520172475 success
budget-raise-gate / budget-raise-gate id=134520155712 success
cancel-superseded id=134520158880 success
codeql id=134520164478 skipped
codeql / Analyze (actions) id=134520150844 success
codeql / Analyze (javascript-typescript) id=134520089171 success
codeql / Analyze (python) id=134520090239 success
gate id=134520105095 failure
governance id=134520173143 skipped
governance / env-matrix id=134520127439 success
governance / instrument-self-tests id=134520155239 success
governance / policy-docs id=134520136363 success
governance / record id=134520088670 skipped
governance / wave-script id=134520089546 success
hassfest id=134520138045 skipped
hassfest / hassfest id=134520147139 success
kernel-points id=134520123627 skipped
pr-contract id=134520093986 skipped
pr-contract / pr-contract id=134520106639 failure
prelude id=134520150548 success
refresh id=134520133565 skipped
sweep-self id=134520589684 skipped
tests id=134520105812 skipped
tests / arch-instrument id=134520090519 success
tests / briefs id=134520131304 success
tests / browser id=134520090642 success
tests / ci-ratchet id=134520092126 skipped
tests / claims-autofix id=134520091272 skipped
tests / closure-scope id=134520151325 success
tests / closures id=134520090399 success
tests / closures-autofix id=134520091905 skipped
tests / coverage id=134520090622 success
tests / coverage-ratchet id=134520091437 success
tests / fast (3.14) id=134520090559 success
tests / graders-head-copy id=134520092536 skipped
tests / lane-proofs id=134520091602 skipped
tests / mutation id=134520144888 success
tests / mutation-autofix id=134520091682 skipped
tests / mutation-pins id=134520091221 skipped
tests / nightly-ha id=134520091365 skipped
tests / nightly-status id=134520104043 failure
tests / replay id=134520091620 skipped
tests / typing id=134520091510 success
validate id=134520137519 skipped
validate / validate-hacs id=134520119047 success

## Refusals
none

## Advisories
required-wait: required context `gate` reads concluded failure at 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item e5762bc3: dismissed:owner ruling 2026-11-16 accepts both as residuals
NOTE body item 0b01d5fd: R11-OUTSIDE-SELF-SETTING-PUMP: R11-OUTSIDE-SELF-SETTING-PUMP resolved on origin/handoff/audit-r10-roster
NOTE body item 06cb4f11: R11-OUTSIDE-SELF-SETTING-PUMP: R11-OUTSIDE-SELF-SETTING-PUMP resolved on origin/handoff/audit-r10-roster
NOTE body item 26742487: R11-OUTSIDE-SELF-SETTING-PUMP: R11-OUTSIDE-SELF-SETTING-PUMP resolved on origin/handoff/audit-r10-roster
NOTE body item dcd51e15: R11-INTAKE-R10-RESIDUE
NOTE body item 31f4e0ab: dismissed:the owner's carry 3 ruling (2026-11-16) accepts an unbounded release as a residual
NOTE body item 81891433: dismissed:the note stores one key, the base
NOTE body item c21810aa: dismissed:owner ruling 2026-11-16 accepts both as residuals
NOTE body item 7a9de240: dismissed:a one-off dispatch text, the file was found by listing the tree
NOTE body item d80b5e24: dismissed:repaired in the instrument this pull request lands
CARRY-AUDIT: 10 finding item(s): 10 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 27 script(s) run, 6 scoped out.
             no segment of this names a program this check knows
  unverified RESULT heatled_scale0=0.5: wrong=0/180 latched_off_configured=0
             no segment of this names a program this check knows
  unverified RESULT heatled_scale0=None: wrong=0/180 latched_off_configured=0
             no segment of this names a program this check knows
  unverified RESULT selfset_scale0=0.5: wrong=0/15 latched_off_configured=0
             no segment of this names a program this check knows
  unverified RESULT selfset_scale0=0.7: wrong=0/15 latched_off_configured=0
             no segment of this names a program this check knows
  unverified RESULT selfset_scale0=None: wrong=0/2340 latched_off_configured=0
             no segment of this names a program this check knows
  unverified RESULT pending_rows=382/2730 widest_band=1.000 most_probes=1
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py
             `dev/audit/harnesses/cop_duty_floor.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_scale_probe_sweep.py 3 > OUT
             `dev/audit/harnesses/cop_scale_probe_sweep.py` is in the tree at this head
  unverified git grep -n -e "step_response(" -e "draw_response(" -e "take_restore(" -e "_admit(" -e "scale_response" -e "_apply_cop_scale(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n -E "compute_cop(_dhw)?\(" -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=30991a6b0d4caaf796847956ebc9977cb4656505 PYTHONPATH=tests/hastub ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=6f422812d5d8b918beace0283419c153f6df66ce ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base 6f422812d5d8b918beace0283419c153f6df66ce
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff origin/main
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/features.py
             `tests/features.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 11 resolved, 9 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/@module.CONST.3ca6562f.json b/tests/mutation_ledger/killed_by/accuracy.py/@module.CONST.3ca6562f.json
new file mode 100644
index 0000000000..30ac02cc17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/@module.CONST.3ca6562f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:<module> CONST 3ca6562f",
+  "killed_by": "tests/features.py",
+  "old": "DITHER_SEED = 3662",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`DITHER_SEED = 7324`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/@module.CONST.6a3c5ccb.json b/tests/mutation_ledger/killed_by/accuracy.py/@module.CONST.6a3c5ccb.json
new file mode 100644
index 0000000000..e8164c3c09
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/@module.CONST.6a3c5ccb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:<module> CONST 6a3c5ccb",
+  "killed_by": "tests/features.py",
+  "old": "FOLLOW_BOUND_Z = 3.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`FOLLOW_BOUND_Z = 6.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/CopInterval.heat_ask_kw.RETURN_DEL.cbc0bc07.json b/tests/mutation_ledger/killed_by/accuracy.py/CopInterval.heat_ask_kw.RETURN_DEL.cbc0bc07.json
new file mode 100644
index 0000000000..b867b6307e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/CopInterval.heat_ask_kw.RETURN_DEL.cbc0bc07.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:CopInterval.heat_ask_kw RETURN_DEL cbc0bc07",
+  "killed_by": "tests/features.py",
+  "old": "        return float(self.asked_kw) * float(self.cop_scale)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._admits.RETURN_DEL.c30a3000.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._admits.RETURN_DEL.c30a3000.json
new file mode 100644
index 0000000000..dea150e8a7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._admits.RETURN_DEL.c30a3000.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._admits RETURN_DEL c30a3000",
+  "killed_by": "tests/features.py",
+  "old": "        return state == ASK_UNOBTAINABLE and draw is not None and not measured_heat",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.CLAMP_DROP.5ac3fff9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.CLAMP_DROP.5ac3fff9.json
new file mode 100644
index 0000000000..fa0ff15c13
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.CLAMP_DROP.5ac3fff9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio CLAMP_DROP 5ac3fff9",
+  "killed_by": "tests/features.py",
+  "old": "        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`if abs(ratio - ewma) / (ewma) > COP_TRACKING_ERROR_GATE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.CMP_BOUND.5ac3fff9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.CMP_BOUND.5ac3fff9.json
new file mode 100644
index 0000000000..acccb35595
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.CMP_BOUND.5ac3fff9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio CMP_BOUND 5ac3fff9",
+  "killed_by": "tests/features.py",
+  "old": "        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if abs(ratio - ewma) / max(ewma, 1e-6) >= COP_TRACKING_ERROR_GATE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.abce9d67.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.21198798.json
similarity index 62%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.abce9d67.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.21198798.json
index 8de455573a..07741d8ed3 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.abce9d67.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.21198798.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF abce9d67",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio GUARD_OFF 21198798",
   "killed_by": "tests/features.py",
-  "old": "        if min(asked_kw, drawn_kw) < power_floor_kw(draw, params):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+  "old": "        if verdict == ASK_PENDING or self.probe.unsettled:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
 }
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.5ac3fff9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.5ac3fff9.json
new file mode 100644
index 0000000000..c900f2e121
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.5ac3fff9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio GUARD_OFF 5ac3fff9",
+  "killed_by": "tests/features.py",
+  "old": "        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.6121b2eb.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.6121b2eb.json
new file mode 100644
index 0000000000..bfd190d69e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.6121b2eb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio GUARD_OFF 6121b2eb",
+  "killed_by": "tests/features.py",
+  "old": "        if verdict == ASK_FOLLOWS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.8002b5c9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.8002b5c9.json
similarity index 86%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.8002b5c9.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.8002b5c9.json
index afe897f579..24ae017c99 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.8002b5c9.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.8002b5c9.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio GUARD_OFF 8002b5c9",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio GUARD_OFF 8002b5c9",
   "killed_by": "tests/features.py",
   "old": "        if state == ASK_IGNORED:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.9a58605a.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.9a58605a.json
similarity index 86%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.9a58605a.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.9a58605a.json
index 0bafbe6bea..0857364c09 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.9a58605a.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.9a58605a.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio GUARD_OFF 9a58605a",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio GUARD_OFF 9a58605a",
   "killed_by": "tests/features.py",
   "old": "        if state == ASK_PENDING:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.9d967a75.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.9d967a75.json
similarity index 83%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.9d967a75.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.9d967a75.json
index d96644e4c2..703cf96dba 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.9d967a75.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.9d967a75.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio GUARD_OFF 9d967a75",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio GUARD_OFF 9d967a75",
   "killed_by": "tests/features.py",
   "old": "        if abs(ratio - 1.0) <= COP_ASK_TOLERANCE or state == ASK_FOLLOWS:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
 }
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.eadc0fa1.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.eadc0fa1.json
new file mode 100644
index 0000000000..a3e46368ec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.GUARD_OFF.eadc0fa1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio GUARD_OFF eadc0fa1",
+  "killed_by": "tests/features.py",
+  "old": "        if verdict == ASK_IGNORED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.870d5834.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.870d5834.json
similarity index 85%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.870d5834.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.870d5834.json
index b59ba08188..1a6a4099ae 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.870d5834.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.870d5834.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio RETURN_DEL 870d5834",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio RETURN_DEL 870d5834",
   "killed_by": "tests/features.py",
   "old": "        return None if self._base_folds(row, params) else COP_REFUSED_NO_EVIDENCE",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.ffec38c1.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.ffec38c1.json
new file mode 100644
index 0000000000..52feaf9957
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.ffec38c1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio RETURN_DEL ffec38c1",
+  "killed_by": "tests/features.py",
+  "old": "            return COP_REFUSED_NO_EVIDENCE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.ffec38c1~2.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.ffec38c1~2.json
new file mode 100644
index 0000000000..a8c6bc7227
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._judge_ratio.RETURN_DEL.ffec38c1~2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio RETURN_DEL ffec38c1#2",
+  "killed_by": "tests/features.py",
+  "old": "            return COP_REFUSED_NO_EVIDENCE",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.BOOLOP.0cacf25d.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.BOOLOP.0cacf25d.json
new file mode 100644
index 0000000000..ea049bc103
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.BOOLOP.0cacf25d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._stored_measurement BOOLOP 0cacf25d",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not np.isfinite(cop) or cop < 0.1 or (dhw or temp is None):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.CMP_BOUND.0cacf25d.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.CMP_BOUND.0cacf25d.json
new file mode 100644
index 0000000000..322978e7ff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.CMP_BOUND.0cacf25d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._stored_measurement CMP_BOUND 0cacf25d",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not np.isfinite(cop) or cop <= 0.1 or (dhw and temp is None):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.GUARD_OFF.0cacf25d.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.GUARD_OFF.0cacf25d.json
new file mode 100644
index 0000000000..0233016889
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.GUARD_OFF.0cacf25d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._stored_measurement GUARD_OFF 0cacf25d",
+  "killed_by": "tests/features.py",
+  "old": "        if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.GUARD_OFF.649d9952.json
similarity index 87%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.GUARD_OFF.649d9952.json
index 8d9f32542d..78e441edab 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.649d9952.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.GUARD_OFF.649d9952.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict GUARD_OFF 649d9952",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._stored_measurement GUARD_OFF 649d9952",
   "killed_by": "tests/features.py",
   "old": "        if (temp is not None and not np.isfinite(temp)) or (raw.get(\"at\") is not None and at is None):",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.RETURN_DEL.81cd12e3.json
similarity index 86%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.RETURN_DEL.81cd12e3.json
index 99b0be279f..71389048b6 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.81cd12e3.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop._stored_measurement.RETURN_DEL.81cd12e3.json
@@ -1,5 +1,5 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict RETURN_DEL 81cd12e3",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._stored_measurement RETURN_DEL 81cd12e3",
   "killed_by": "tests/features.py",
   "old": "        return cls(cop=cop, curve_dhw=dhw, dhw_temp=temp, at=at)",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.68568a66.json
similarity index 69%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.68568a66.json
index 9889b26052..6a3a8806a6 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.62858a00.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.as_dict.RETURN_DEL.68568a66.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.as_dict RETURN_DEL 62858a00",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.as_dict RETURN_DEL 68568a66",
   "killed_by": "tests/features.py",
-  "old": "        return {\"cop\": self.cop, \"curve_dhw\": self.curve_dhw, \"dhw_temp\": self.dhw_temp, \"at\": at}",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "        return {\"cop\": self.cop, \"curve_dhw\": self.curve_dhw, \"dhw_temp\": self.dhw_temp, \"at\": at, **self.probe.as_dict()}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
 }
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.0cacf25d.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.0cacf25d.json
deleted file mode 100644
index 97e331bb1d..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.BOOLOP.0cacf25d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict BOOLOP 0cacf25d",
-  "killed_by": "tests/features.py",
-  "old": "        if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: BOOLOP (`if not np.isfinite(cop) or cop < 0.1 or (dhw or temp is None):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.CMP_BOUND.0cacf25d.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.CMP_BOUND.0cacf25d.json
deleted file mode 100644
index a38e858bec..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.CMP_BOUND.0cacf25d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict CMP_BOUND 0cacf25d",
-  "killed_by": "tests/features.py",
-  "old": "        if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):",
-  "reason": "Hand-recorded by the #2066 fixer at 4bf7bdde1 against the ratchet base b2b6acd64, not by `--pin-killed` (whose baselines need CI's Linux floats). `CMP_BOUND` (if not np.isfinite(cop) or cop <= 0.1 or (dhw and temp is None):) flips the condition of tests/features.py's R.check \"an unreadable stored COP record loads as no measurement, whole\" -- the new check \"the store's 0.1 bar is exclusive\" reads False: `cop <= 0.1` drops a stored 0.1 the tree reads back. Measured by copying the package, rewriting that one line to the operator's own text and re-evaluating the check's condition: baseline True, mutant as stated (evidence table in the pull request's body, `## Unpinned sites`). CI's `--pin-killed` at a pull_request head re-measures the driver itself."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.0cacf25d.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.0cacf25d.json
deleted file mode 100644
index 70bf06c0eb..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.GUARD_OFF.0cacf25d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict GUARD_OFF 0cacf25d",
-  "killed_by": "tests/features.py",
-  "old": "        if not np.isfinite(cop) or cop < 0.1 or (dhw and temp is None):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.60cc1b2a.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.60cc1b2a.json
new file mode 100644
index 0000000000..3f1863d0e6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.from_dict.RETURN_DEL.60cc1b2a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.from_dict RETURN_DEL 60cc1b2a",
+  "killed_by": "tests/features.py",
+  "old": "        return record",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.BOOLOP.4801fdf9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.BOOLOP.4801fdf9.json
new file mode 100644
index 0000000000..4a426f7e5c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.BOOLOP.4801fdf9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor BOOLOP 4801fdf9",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw(draw, params):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if drawn_kw is not None or min(asked_kw, drawn_kw) < power_floor_kw(draw, params):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=31."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CLAMP_DROP.4801fdf9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CLAMP_DROP.4801fdf9.json
new file mode 100644
index 0000000000..617be8281c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CLAMP_DROP.4801fdf9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor CLAMP_DROP 4801fdf9",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw(draw, params):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`if drawn_kw is not None and (asked_kw) < power_floor_kw(draw, params):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CLAMP_DROP.abce9d67.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CLAMP_DROP.abce9d67.json
deleted file mode 100644
index 2816423d1b..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CLAMP_DROP.abce9d67.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor CLAMP_DROP abce9d67",
-  "killed_by": "tests/features.py",
-  "old": "        if min(asked_kw, drawn_kw) < power_floor_kw(draw, params):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`if (asked_kw) < power_floor_kw(draw, params):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CMP_BOUND.4801fdf9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CMP_BOUND.4801fdf9.json
new file mode 100644
index 0000000000..99ac07639a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CMP_BOUND.4801fdf9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor CMP_BOUND 4801fdf9",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw(draw, params):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if drawn_kw is not None and min(asked_kw, drawn_kw) <= power_floor_kw(draw, params):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CMP_BOUND.abce9d67.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CMP_BOUND.abce9d67.json
deleted file mode 100644
index aad2202a26..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.CMP_BOUND.abce9d67.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor CMP_BOUND abce9d67",
-  "killed_by": "tests/features.py",
-  "old": "        if min(asked_kw, drawn_kw) < power_floor_kw(draw, params):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if min(asked_kw, drawn_kw) <= power_floor_kw(draw, params):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.4801fdf9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.4801fdf9.json
new file mode 100644
index 0000000000..ac24fb8f5a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_floor.GUARD_OFF.4801fdf9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_floor GUARD_OFF 4801fdf9",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw is not None and min(asked_kw, drawn_kw) < power_floor_kw(draw, params):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.CLAMP_DROP.5ac3fff9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.CLAMP_DROP.5ac3fff9.json
deleted file mode 100644
index 76ab265cdf..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.CLAMP_DROP.5ac3fff9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio CLAMP_DROP 5ac3fff9",
-  "killed_by": "tests/features.py",
-  "old": "        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:",
-  "reason": "Hand-recorded by the #2066 fixer at 4bf7bdde1 against the ratchet base b2b6acd64, not by `--pin-killed` (whose baselines need CI's Linux floats). `CLAMP_DROP` (if abs(ratio - ewma) / (ewma) > COP_TRACKING_ERROR_GATE:) flips the condition of tests/features.py's R.check \"a 14 kW nameplate pump drawing 1.9-2.55 kW teaches the COP learner once the meter shows the draw follows the ask\" -- the new check \"the tracking gate divides by the clamped walking ratio\" raises ZeroDivisionError on `judge_ratio(0.5, 0.0, ...)` where the tree refuses as tracking_gate. Measured by copying the package, rewriting that one line to the operator's own text and re-evaluating the check's condition: baseline True, mutant as stated (evidence table in the pull request's body, `## Unpinned sites`). CI's `--pin-killed` at a pull_request head re-measures the driver itself."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.5ac3fff9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.5ac3fff9.json
deleted file mode 100644
index 4e687aadbb..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.5ac3fff9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio CMP_BOUND 5ac3fff9",
-  "killed_by": "tests/features.py",
-  "old": "        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:",
-  "reason": "Hand-recorded by the #2066 fixer at 4bf7bdde1 against the ratchet base b2b6acd64, not by `--pin-killed` (whose baselines need CI's Linux floats). `CMP_BOUND` (if abs(ratio - ewma) / max(ewma, 1e-6) >= COP_TRACKING_ERROR_GATE:) flips the condition of tests/features.py's R.check \"a 14 kW nameplate pump drawing 1.9-2.55 kW teaches the COP learner once the meter shows the draw follows the ask\" -- the new check \"the tracking gate is exclusive\" reads False: 1.5/5.0 is the double 0.3, so `>=` refuses a ratio the tree folds. Measured by copying the package, rewriting that one line to the operator's own text and re-evaluating the check's condition: baseline True, mutant as stated (evidence table in the pull request's body, `## Unpinned sites`). CI's `--pin-killed` at a pull_request head re-measures the driver itself."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.0e512205.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.0e512205.json
new file mode 100644
index 0000000000..66462db5f0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.0e512205.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio GUARD_OFF 0e512205",
+  "killed_by": "tests/features.py",
+  "old": "        if refusal is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.5ac3fff9.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.5ac3fff9.json
deleted file mode 100644
index 22a7d3e282..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.GUARD_OFF.5ac3fff9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio GUARD_OFF 5ac3fff9",
-  "killed_by": "tests/features.py",
-  "old": "        if abs(ratio - ewma) / max(ewma, 1e-6) > COP_TRACKING_ERROR_GATE:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.c3008ed6.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.c3008ed6.json
new file mode 100644
index 0000000000..0fe385e007
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.c3008ed6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio RETURN_DEL c3008ed6",
+  "killed_by": "tests/features.py",
+  "old": "        return refusal",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.ffec38c1.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.ffec38c1.json
deleted file mode 100644
index 04262c4ff4..0000000000
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.judge_ratio.RETURN_DEL.ffec38c1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio RETURN_DEL ffec38c1",
-  "killed_by": "tests/features.py",
-  "old": "            return COP_REFUSED_NO_EVIDENCE",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json
new file mode 100644
index 0000000000..c691d8a05a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.owed_scale.RETURN_DEL.a64e3c97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.owed_scale RETURN_DEL a64e3c97",
+  "killed_by": "tests/features.py",
+  "old": "        return self.probe.owed_scale(configured, now, self.refusal not in (COP_REFUSED_FROZEN, COP_REFUSED_NO_POWER))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.BOOLOP.50f90b0a.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.BOOLOP.50f90b0a.json
new file mode 100644
index 0000000000..a722838ae9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.BOOLOP.50f90b0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.release BOOLOP 50f90b0a",
+  "killed_by": "tests/features.py",
+  "old": "        return [r for r in rows if not waits and self._base_folds(r, params)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return [r for r in rows if not waits or self._base_folds(r, params)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.BOOLOP.acd6eeab.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.BOOLOP.acd6eeab.json
new file mode 100644
index 0000000000..907f76e9cb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.BOOLOP.acd6eeab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.release BOOLOP acd6eeab",
+  "killed_by": "tests/features.py",
+  "old": "        if waits := self.probe.owed is not None or (probed and state == ASK_PENDING):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if waits := self.probe.owed is not None or (probed or state == ASK_PENDING):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.GUARD_OFF.0de8d9b8.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.GUARD_OFF.0de8d9b8.json
new file mode 100644
index 0000000000..dc5d64f9d8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.GUARD_OFF.0de8d9b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.release GUARD_OFF 0de8d9b8",
+  "killed_by": "tests/features.py",
+  "old": "        if probed := self._admits(state, draw, measured_heat):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.GUARD_OFF.acd6eeab.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.GUARD_OFF.acd6eeab.json
new file mode 100644
index 0000000000..92ef3b1598
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.GUARD_OFF.acd6eeab.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.release GUARD_OFF acd6eeab",
+  "killed_by": "tests/features.py",
+  "old": "        if waits := self.probe.owed is not None or (probed and state == ASK_PENDING):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.RETURN_DEL.16313cfa.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.RETURN_DEL.50f90b0a.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.RETURN_DEL.16313cfa.json
rename to tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.RETURN_DEL.50f90b0a.json
index 219b20ca89..b9fffccfeb 100644
--- a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.RETURN_DEL.16313cfa.json
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.release.RETURN_DEL.50f90b0a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.release RETURN_DEL 16313cfa",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.release RETURN_DEL 50f90b0a",
   "killed_by": "tests/features.py",
-  "old": "        return [r for r in rows if self._base_folds(r, params)]",
+  "old": "        return [r for r in rows if not waits and self._base_folds(r, params)]",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.scale_response.RETURN_DEL.a2228e49.json b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.scale_response.RETURN_DEL.a2228e49.json
new file mode 100644
index 0000000000..8b217bd62c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/MeasuredCop.scale_response.RETURN_DEL.a2228e49.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.scale_response RETURN_DEL a2228e49",
+  "killed_by": "tests/features.py",
+  "old": "        return self.probe.response",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=35."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.CMP_BOUND.c731d6a2.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.CMP_BOUND.c731d6a2.json
new file mode 100644
index 0000000000..5d9011d0fb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.CMP_BOUND.c731d6a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.levels CMP_BOUND c731d6a2",
+  "killed_by": "tests/features.py",
+  "old": "        if base * half > COP_SCALE_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if base * half >= COP_SCALE_MAX:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.CMP_BOUND.d28b0df7.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.CMP_BOUND.d28b0df7.json
new file mode 100644
index 0000000000..0a210ca362
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.CMP_BOUND.d28b0df7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.levels CMP_BOUND d28b0df7",
+  "killed_by": "tests/features.py",
+  "old": "        if base / half < COP_SCALE_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if base / half <= COP_SCALE_MIN:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.GUARD_OFF.c731d6a2.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.GUARD_OFF.c731d6a2.json
new file mode 100644
index 0000000000..9e6ce8f0bb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.GUARD_OFF.c731d6a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.levels GUARD_OFF c731d6a2",
+  "killed_by": "tests/features.py",
+  "old": "        if base * half > COP_SCALE_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.GUARD_OFF.d28b0df7.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.GUARD_OFF.d28b0df7.json
new file mode 100644
index 0000000000..380975e8e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.GUARD_OFF.d28b0df7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.levels GUARD_OFF d28b0df7",
+  "killed_by": "tests/features.py",
+  "old": "        if base / half < COP_SCALE_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.RETURN_DEL.a0dd9691.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.RETURN_DEL.a0dd9691.json
new file mode 100644
index 0000000000..f38fee585f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.levels.RETURN_DEL.a0dd9691.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.levels RETURN_DEL a0dd9691",
+  "killed_by": "tests/features.py",
+  "old": "        return base / half, base * half",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.BOOLOP.3680824f.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.BOOLOP.3680824f.json
new file mode 100644
index 0000000000..1b956bdea6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.BOOLOP.3680824f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.step BOOLOP 3680824f",
+  "killed_by": "tests/features.py",
+  "old": "        if self.ahead is not None and not self.ahead[1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.ahead is not None or not self.ahead[1]:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.GUARD_OFF.3680824f.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.GUARD_OFF.3680824f.json
new file mode 100644
index 0000000000..d4197f7023
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.GUARD_OFF.3680824f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.step GUARD_OFF 3680824f",
+  "killed_by": "tests/features.py",
+  "old": "        if self.ahead is not None and not self.ahead[1]:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.GUARD_OFF.d7377f5d.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.GUARD_OFF.d7377f5d.json
new file mode 100644
index 0000000000..6320f3a1a9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.GUARD_OFF.d7377f5d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.step GUARD_OFF d7377f5d",
+  "killed_by": "tests/features.py",
+  "old": "        if not live:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.RETURN_DEL.113f2cbb.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.RETURN_DEL.113f2cbb.json
new file mode 100644
index 0000000000..1aecca0f0e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.RETURN_DEL.113f2cbb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.step RETURN_DEL 113f2cbb",
+  "killed_by": "tests/features.py",
+  "old": "        return self.levels(base)[(coin > 0) != second]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.RETURN_DEL.80ced7ac.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.RETURN_DEL.80ced7ac.json
new file mode 100644
index 0000000000..7b7ee66ec0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.step.RETURN_DEL.80ced7ac.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.step RETURN_DEL 80ced7ac",
+  "killed_by": "tests/features.py",
+  "old": "            return base",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.BOOLOP.7b8b796b.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.BOOLOP.7b8b796b.json
new file mode 100644
index 0000000000..288e24fb10
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.BOOLOP.7b8b796b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.take BOOLOP 7b8b796b",
+  "killed_by": "tests/features.py",
+  "old": "        if second and first is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if second or first is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.410b54bf.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.410b54bf.json
new file mode 100644
index 0000000000..9ca60f5f9b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.410b54bf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.take GUARD_OFF 410b54bf",
+  "killed_by": "tests/features.py",
+  "old": "        if self.reading is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.7b8b796b.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.7b8b796b.json
new file mode 100644
index 0000000000..f109355e66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.7b8b796b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.take GUARD_OFF 7b8b796b",
+  "killed_by": "tests/features.py",
+  "old": "        if second and first is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.d29ee146.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.d29ee146.json
new file mode 100644
index 0000000000..53183b38f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.take.GUARD_OFF.d29ee146.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.take GUARD_OFF d29ee146",
+  "killed_by": "tests/features.py",
+  "old": "            if coin * math.log(first.heat_ask_kw / row.heat_ask_kw) >= FOLLOW_SLOPE_MIN * step:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.811b6870.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.811b6870.json
new file mode 100644
index 0000000000..fa3f49760e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.811b6870.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.verdict CMP_BOUND 811b6870",
+  "killed_by": "tests/features.py",
+  "old": "        return ASK_IGNORED if mean + bound <= FOLLOW_SLOPE_MIN else ASK_PENDING",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return ASK_IGNORED if mean + bound < FOLLOW_SLOPE_MIN else ASK_PENDING`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.a4874b65.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.a4874b65.json
new file mode 100644
index 0000000000..01b01ba22b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.a4874b65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.verdict CMP_BOUND a4874b65",
+  "killed_by": "tests/features.py",
+  "old": "        if mean - bound >= FOLLOW_SLOPE_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if mean - bound > FOLLOW_SLOPE_MIN:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.f178fc81.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.f178fc81.json
new file mode 100644
index 0000000000..43e392c796
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.CMP_BOUND.f178fc81.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.verdict CMP_BOUND f178fc81",
+  "killed_by": "tests/features.py",
+  "old": "        if 2 * len(self.contrasts) < MIN_SAMPLES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if 2 * len(self.contrasts) <= MIN_SAMPLES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.GUARD_OFF.a4874b65.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.GUARD_OFF.a4874b65.json
new file mode 100644
index 0000000000..b66b95a48d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.GUARD_OFF.a4874b65.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.verdict GUARD_OFF a4874b65",
+  "killed_by": "tests/features.py",
+  "old": "        if mean - bound >= FOLLOW_SLOPE_MIN:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.GUARD_OFF.f178fc81.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.GUARD_OFF.f178fc81.json
new file mode 100644
index 0000000000..1d663e497c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.GUARD_OFF.f178fc81.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.verdict GUARD_OFF f178fc81",
+  "killed_by": "tests/features.py",
+  "old": "        if 2 * len(self.contrasts) < MIN_SAMPLES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.RETURN_DEL.811b6870.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.RETURN_DEL.811b6870.json
new file mode 100644
index 0000000000..40df78a646
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleDither.verdict.RETURN_DEL.811b6870.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.verdict RETURN_DEL 811b6870",
+  "killed_by": "tests/features.py",
+  "old": "        return ASK_IGNORED if mean + bound <= FOLLOW_SLOPE_MIN else ASK_PENDING",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.CLAMP_DROP.399d9150.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.CLAMP_DROP.399d9150.json
new file mode 100644
index 0000000000..7b5391ce25
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.CLAMP_DROP.399d9150.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed CLAMP_DROP 399d9150",
+  "killed_by": "tests/features.py",
+  "old": "            scale = float(np.clip(configured(), COP_SCALE_MIN, COP_SCALE_MAX))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`scale = float((configured()))`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.CMP_BOUND.c3e245af.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.CMP_BOUND.c3e245af.json
new file mode 100644
index 0000000000..20f687d4e6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.CMP_BOUND.c3e245af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed CMP_BOUND c3e245af",
+  "killed_by": "tests/features.py",
+  "old": "            if 0.0 <= utc_elapsed_seconds(now, self.parked_at) <= COP_HOLD_HORIZON_S:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if 0.0 < utc_elapsed_seconds(now, self.parked_at) <= COP_HOLD_HORIZON_S:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.3caddad9.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.3caddad9.json
new file mode 100644
index 0000000000..4d97de8899
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.3caddad9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed GUARD_OFF 3caddad9",
+  "killed_by": "tests/features.py",
+  "old": "        if self.owed is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.4a0bbd4e.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.4a0bbd4e.json
new file mode 100644
index 0000000000..f0d850c2dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.4a0bbd4e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed GUARD_OFF 4a0bbd4e",
+  "killed_by": "tests/features.py",
+  "old": "        if self.parked_at is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.bcf483aa.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.bcf483aa.json
new file mode 100644
index 0000000000..d00b525ec5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.bcf483aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed GUARD_OFF bcf483aa",
+  "killed_by": "tests/features.py",
+  "old": "            if self.response == ASK_PENDING:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.c26ecef9.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.c26ecef9.json
new file mode 100644
index 0000000000..c88d125a7e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.c26ecef9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed GUARD_OFF c26ecef9",
+  "killed_by": "tests/features.py",
+  "old": "        if self.base is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.c3e245af.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.c3e245af.json
new file mode 100644
index 0000000000..3431ceaf7d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.c3e245af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed GUARD_OFF c3e245af",
+  "killed_by": "tests/features.py",
+  "old": "            if 0.0 <= utc_elapsed_seconds(now, self.parked_at) <= COP_HOLD_HORIZON_S:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.f89d95e3.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.f89d95e3.json
new file mode 100644
index 0000000000..89b69b4a79
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.GUARD_OFF.f89d95e3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed GUARD_OFF f89d95e3",
+  "killed_by": "tests/features.py",
+  "old": "        if self.restore_due:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.17f27803.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.17f27803.json
new file mode 100644
index 0000000000..08614c3167
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.17f27803.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed RETURN_DEL 17f27803",
+  "killed_by": "tests/features.py",
+  "old": "        return self.dither.step(self.base, live)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.2320e72e.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.2320e72e.json
new file mode 100644
index 0000000000..f1245a4e9c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.2320e72e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed RETURN_DEL 2320e72e",
+  "killed_by": "tests/features.py",
+  "old": "            return scale",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.2f0b98e2.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.2f0b98e2.json
new file mode 100644
index 0000000000..c4f1bc9865
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe._owed.RETURN_DEL.2f0b98e2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe._owed RETURN_DEL 2f0b98e2",
+  "killed_by": "tests/features.py",
+  "old": "            return want",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.BOOLOP.bb9080cf.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.BOOLOP.bb9080cf.json
new file mode 100644
index 0000000000..67c2971edd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.BOOLOP.bb9080cf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit BOOLOP bb9080cf",
+  "killed_by": "tests/features.py",
+  "old": "            if not self.reseeded and not COP_SCALE_MIN < row.cop_scale < COP_SCALE_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not self.reseeded or not COP_SCALE_MIN < row.cop_scale < COP_SCALE_MAX:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.CMP_BOUND.3528de36.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.CMP_BOUND.3528de36.json
new file mode 100644
index 0000000000..d6342b5dea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.CMP_BOUND.3528de36.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit CMP_BOUND 3528de36",
+  "killed_by": "tests/features.py",
+  "old": "            if self.dither.rows < WINDOW:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if self.dither.rows <= WINDOW:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.CMP_BOUND.bb9080cf.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.CMP_BOUND.bb9080cf.json
new file mode 100644
index 0000000000..0f973644f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.CMP_BOUND.bb9080cf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit CMP_BOUND bb9080cf",
+  "killed_by": "tests/features.py",
+  "old": "            if not self.reseeded and not COP_SCALE_MIN < row.cop_scale < COP_SCALE_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not self.reseeded and not COP_SCALE_MIN <= row.cop_scale < COP_SCALE_MAX:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.0e7e3e58.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.0e7e3e58.json
new file mode 100644
index 0000000000..005e7aa92b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.0e7e3e58.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit GUARD_OFF 0e7e3e58",
+  "killed_by": "tests/features.py",
+  "old": "        if self.response == ASK_PENDING:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=25."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.3528de36.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.3528de36.json
new file mode 100644
index 0000000000..0cb03eaaf6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.3528de36.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit GUARD_OFF 3528de36",
+  "killed_by": "tests/features.py",
+  "old": "            if self.dither.rows < WINDOW:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=25."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.4a0bbd4e.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.4a0bbd4e.json
new file mode 100644
index 0000000000..8fb769ece2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.4a0bbd4e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit GUARD_OFF 4a0bbd4e",
+  "killed_by": "tests/features.py",
+  "old": "        if self.parked_at is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.8c43a3b0.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.8c43a3b0.json
new file mode 100644
index 0000000000..7512bd1bb3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.8c43a3b0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit GUARD_OFF 8c43a3b0",
+  "killed_by": "tests/features.py",
+  "old": "        elif self.response == ASK_FOLLOWS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.bb9080cf.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.bb9080cf.json
new file mode 100644
index 0000000000..09bac79c4d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.bb9080cf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit GUARD_OFF bb9080cf",
+  "killed_by": "tests/features.py",
+  "old": "            if not self.reseeded and not COP_SCALE_MIN < row.cop_scale < COP_SCALE_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.c26ecef9.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.c26ecef9.json
new file mode 100644
index 0000000000..abad0d398d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.c26ecef9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit GUARD_OFF c26ecef9",
+  "killed_by": "tests/features.py",
+  "old": "        if self.base is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.dcc4a838.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.dcc4a838.json
new file mode 100644
index 0000000000..5e7c078e5d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.GUARD_OFF.dcc4a838.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit GUARD_OFF dcc4a838",
+  "killed_by": "tests/features.py",
+  "old": "        if self.response != ASK_PENDING or self.restore_due:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.RETURN_DEL.04fb3288.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.RETURN_DEL.04fb3288.json
new file mode 100644
index 0000000000..465213f2ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.RETURN_DEL.04fb3288.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit RETURN_DEL 04fb3288",
+  "killed_by": "tests/features.py",
+  "old": "                return ASK_PENDING",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.RETURN_DEL.3d2dcdae.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.RETURN_DEL.3d2dcdae.json
new file mode 100644
index 0000000000..4de47971bd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.admit.RETURN_DEL.3d2dcdae.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.admit RETURN_DEL 3d2dcdae",
+  "killed_by": "tests/features.py",
+  "old": "        return self.response",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.as_dict.RETURN_DEL.c17c4047.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.as_dict.RETURN_DEL.c17c4047.json
new file mode 100644
index 0000000000..46ed85ea33
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.as_dict.RETURN_DEL.c17c4047.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.as_dict RETURN_DEL c17c4047",
+  "killed_by": "tests/features.py",
+  "old": "        return {\"scale_response\": self.response, \"scale_base\": self.base}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.BOOLOP.20a0764c.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.BOOLOP.20a0764c.json
new file mode 100644
index 0000000000..c6c0e9e3a3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.BOOLOP.20a0764c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.from_dict BOOLOP 20a0764c",
+  "killed_by": "tests/features.py",
+  "old": "            probe.base = base if base is not None and COP_SCALE_MIN <= base <= COP_SCALE_MAX else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`probe.base = base if base is not None or COP_SCALE_MIN <= base <= COP_SCALE_MAX else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.BOOLOP.431403cb.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.BOOLOP.431403cb.json
new file mode 100644
index 0000000000..d966c11bd2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.BOOLOP.431403cb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.from_dict BOOLOP 431403cb",
+  "killed_by": "tests/features.py",
+  "old": "        if isinstance(response, str) and response in (ASK_FOLLOWS, ASK_IGNORED):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(response, str) or response in (ASK_FOLLOWS, ASK_IGNORED):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.CMP_BOUND.20a0764c.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.CMP_BOUND.20a0764c.json
new file mode 100644
index 0000000000..55b8b37314
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.CMP_BOUND.20a0764c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.from_dict CMP_BOUND 20a0764c",
+  "killed_by": "tests/features.py",
+  "old": "            probe.base = base if base is not None and COP_SCALE_MIN <= base <= COP_SCALE_MAX else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`probe.base = base if base is not None and COP_SCALE_MIN < base <= COP_SCALE_MAX else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.GUARD_OFF.431403cb.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.GUARD_OFF.431403cb.json
new file mode 100644
index 0000000000..cdd4bf76be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.GUARD_OFF.431403cb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.from_dict GUARD_OFF 431403cb",
+  "killed_by": "tests/features.py",
+  "old": "        if isinstance(response, str) and response in (ASK_FOLLOWS, ASK_IGNORED):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.GUARD_OFF.e9d8acee.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.GUARD_OFF.e9d8acee.json
new file mode 100644
index 0000000000..5e8597df6b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.GUARD_OFF.e9d8acee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.from_dict GUARD_OFF e9d8acee",
+  "killed_by": "tests/features.py",
+  "old": "        elif isinstance(raw, dict):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.RETURN_DEL.bc51708b.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.RETURN_DEL.bc51708b.json
new file mode 100644
index 0000000000..f8af8af338
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.from_dict.RETURN_DEL.bc51708b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.from_dict RETURN_DEL bc51708b",
+  "killed_by": "tests/features.py",
+  "old": "        return probe",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.BOOLOP.1c4c08bd.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.BOOLOP.1c4c08bd.json
new file mode 100644
index 0000000000..596570be32
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.BOOLOP.1c4c08bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.owed_scale BOOLOP 1c4c08bd",
+  "killed_by": "tests/features.py",
+  "old": "        self.moved = want is not None and want != self.level",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`self.moved = want is not None or want != self.level`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.BOOLOP.9ba681bb.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.BOOLOP.9ba681bb.json
new file mode 100644
index 0000000000..af873c77bf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.BOOLOP.9ba681bb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.owed_scale BOOLOP 9ba681bb",
+  "killed_by": "tests/features.py",
+  "old": "        live = self.dither.admitted and read",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`live = self.dither.admitted or read`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.RETURN_DEL.345b4063.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.RETURN_DEL.345b4063.json
new file mode 100644
index 0000000000..5bfe8eac4d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.owed_scale.RETURN_DEL.345b4063.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.owed_scale RETURN_DEL 345b4063",
+  "killed_by": "tests/features.py",
+  "old": "        return want if self.moved else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.reset.BOOLOP.fb08584a.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.reset.BOOLOP.fb08584a.json
new file mode 100644
index 0000000000..98e47070d6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.reset.BOOLOP.fb08584a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.reset BOOLOP fb08584a",
+  "killed_by": "tests/features.py",
+  "old": "        self.restore_due = self.restore_due and not measured_heat",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`self.restore_due = self.restore_due or not measured_heat`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.unsettled.RETURN_DEL.206a2441.json b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.unsettled.RETURN_DEL.206a2441.json
new file mode 100644
index 0000000000..616250c627
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/ScaleProbe.unsettled.RETURN_DEL.206a2441.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleProbe.unsettled RETURN_DEL 206a2441",
+  "killed_by": "tests/features.py",
+  "old": "        return self.moved or self.owed is not None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.9227f8fe.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.9227f8fe.json
deleted file mode 100644
index ef6fc559a3..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.9227f8fe.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop BOOLOP 9227f8fe",
-  "killed_by": "tests/features.py",
-  "old": "        if self._measured_power is not None and (refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self._measured_power is not None or (refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.7fd7c6f3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.b36d784d.json
similarity index 55%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.7fd7c6f3.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.b36d784d.json
index 42e311a983..a7b4f364aa 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.7fd7c6f3.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.BOOLOP.b36d784d.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop BOOLOP 7fd7c6f3",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop BOOLOP b36d784d",
   "killed_by": "tests/features.py",
-  "old": "        if heat_kw is None and (refusal := self._measured_cop.judge_ratio(ewma, row, params, draw)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if heat_kw is None or (refusal := self._measured_cop.judge_ratio(ewma, row, params, draw)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
+  "old": "        if heat_kw is None and (refusal := self._measured_cop.judge_ratio(ewma, row, params, draw, measured_heat)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if heat_kw is None or (refusal := self._measured_cop.judge_ratio(ewma, row, params, draw, measured_heat)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=27."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.7fd7c6f3.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.b36d784d.json
similarity index 66%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.7fd7c6f3.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.b36d784d.json
index 85dfa6dfa9..e966df7872 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.7fd7c6f3.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.b36d784d.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 7fd7c6f3",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF b36d784d",
   "killed_by": "tests/features.py",
-  "old": "        if heat_kw is None and (refusal := self._measured_cop.judge_ratio(ewma, row, params, draw)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+  "old": "        if heat_kw is None and (refusal := self._measured_cop.judge_ratio(ewma, row, params, draw, measured_heat)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.9227f8fe.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.9227f8fe.json
rename to tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json
index 6ed38fc8ca..0a826b8c36 100644
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.9227f8fe.json
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.c41a3ead.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF 9227f8fe",
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF c41a3ead",
   "killed_by": "tests/features.py",
-  "old": "        if self._measured_power is not None and (refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+  "old": "        if (owed := self._measured_cop.owed_scale(lambda: ctx._config.cop_scale, dt_util.now())) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
 }
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json
new file mode 100644
index 0000000000..d2589c55da
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.GUARD_OFF.f61826c8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop GUARD_OFF f61826c8",
+  "killed_by": "tests/features.py",
+  "old": "        if refusal := MeasuredCop.judge_floor(commanded, self._measured_power, params, draw):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.b11bbc76~2.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.b11bbc76~2.json
deleted file mode 100644
index a0c02a36b1..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_measured_cop.RETURN_DEL.b11bbc76~2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_measured_cop RETURN_DEL b11bbc76#2",
-  "killed_by": "tests/features.py",
-  "old": "            return refusal",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 47b083b03a9dcbfb1e33679dc5f7d3313a5fed49: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.9d967a75.json b/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop._judge_ratio.CMP_BOUND.9d967a75.json
similarity index 81%
rename from tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.9d967a75.json
rename to tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop._judge_ratio.CMP_BOUND.9d967a75.json
index b1aacfa652..c167381f22 100644
--- a/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop.judge_ratio.CMP_BOUND.9d967a75.json
+++ b/tests/mutation_ledger/survivor_triage/accuracy.py/MeasuredCop._judge_ratio.CMP_BOUND.9d967a75.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop.judge_ratio CMP_BOUND 9d967a75",
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:MeasuredCop._judge_ratio CMP_BOUND 9d967a75",
   "old": "        if abs(ratio - 1.0) <= COP_ASK_TOLERANCE or state == ASK_FOLLOWS:",
-  "reason": "Equivalent (CMP_BOUND, `<=` -> `<`), carried from the triage of this comparison's previous text (`if abs(ratio - 1.0) <= COP_ASK_TOLERANCE:`, anchor d2c128b3), which R10-COP-LEARNER-DRAW-FLOOR rewrote by adding the `or state == ASK_FOLLOWS` operand and nothing else. The arms differ only where `abs(ratio - 1.0)` is exactly the double 0.15, and no double ratio reaches it: 1.0 + double(0.15) and 1.0 - double(0.15) are not doubles, and the doubles either side were measured at this head with math.nextafter -- ratio 1.15 gives 0.1499999999999999, its neighbours 0.1499999999999997 and 0.15000000000000013; ratio 0.85 gives 0.15000000000000002, its neighbours 0.15000000000000013 and 0.1499999999999999 -- none equal to 0.15. For a ratio in [0.5, 2] the subtraction is exact (Sterbenz), so these are the only candidates; outside it |ratio - 1.0| >= 0.5 and both arms take the same branch. Driven by prepr.sh's diff-mutant step over the two tests/features.py blocks that pin judge_ratio (from `# silence the learner. Synthetic numbers only.` to `R.section(\"R10-COP-GATE (#2262)`): the mutant survived.",
+  "reason": "Equivalent (CMP_BOUND, `<=` -> `<`), carried from the triage of this comparison's previous text (`if abs(ratio - 1.0) <= COP_ASK_TOLERANCE:`, anchor d2c128b3), which R10-COP-LEARNER-DRAW-FLOOR rewrote by adding the `or state == ASK_FOLLOWS` operand and nothing else. The arms differ only where `abs(ratio - 1.0)` is exactly the double 0.15, and no double ratio reaches it: 1.0 + double(0.15) and 1.0 - double(0.15) are not doubles, and the doubles either side were measured at this head with math.nextafter -- ratio 1.15 gives 0.1499999999999999, its neighbours 0.1499999999999997 and 0.15000000000000013; ratio 0.85 gives 0.15000000000000002, its neighbours 0.15000000000000013 and 0.1499999999999999 -- none equal to 0.15. For a ratio in [0.5, 2] the subtraction is exact (Sterbenz), so these are the only candidates; outside it |ratio - 1.0| >= 0.5 and both arms take the same branch. Driven by prepr.sh's diff-mutant step over the two tests/features.py blocks that pin judge_ratio (from `# silence the learner. Synthetic numbers only.` to `R.section(\"R10-COP-GATE (#2262)`): the mutant survived. R11-OUTSIDE-SELF-SETTING-PUMP moved the line, text unchanged, from MeasuredCop.judge_ratio into MeasuredCop._judge_ratio (judge_ratio now wraps it to log the refusal), so the anchor's qualname moved and nothing else.",
   "verdict": "equivalent"
 }
diff --git a/tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.step.CMP_BOUND.113f2cbb.json b/tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.step.CMP_BOUND.113f2cbb.json
new file mode 100644
index 0000000000..bbc3b23781
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.step.CMP_BOUND.113f2cbb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.step CMP_BOUND 113f2cbb",
+  "old": "        return self.levels(base)[(coin > 0) != second]",
+  "reason": "Equivalent (CMP_BOUND, `>` -> `>=`). `coin` is the first element of `ScaleDither.ahead`, which `step` alone writes, from `self.coin.choice((-1, 1))` or from the tuple it already holds: it is -1 or 1 and never 0, the one value on which the two comparisons differ. Driven by prepr.sh's diff-mutant step at 4fee736fbe over the tests/features.py block from `R.section(\"COP learner duty floor keys` to `R.section(\"R10-COP-GATE (#2262)`: the mutant survived.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.take.CMP_BOUND.d29ee146.json b/tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.take.CMP_BOUND.d29ee146.json
new file mode 100644
index 0000000000..175aa876bd
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/accuracy.py/ScaleDither.take.CMP_BOUND.d29ee146.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:ScaleDither.take CMP_BOUND d29ee146",
+  "old": "            if coin * math.log(first.heat_ask_kw / row.heat_ask_kw) >= FOLLOW_SLOPE_MIN * step:",
+  "reason": "Equivalent (CMP_BOUND, `>=` -> `>`). The arms differ only where `math.log(r)` for a double ratio `r` equals the double `FOLLOW_SLOPE_MIN * math.log(FOLLOW_ASK_SPAN)` (0.5 * log 1.15), signed by a coin of -1 or 1. No double reaches it: measured at 4fee736fbe with math.nextafter, log(1.0723805294763606) is under that product and log(1.0723805294763609), the next double, is over it by 6.9e-17, and the mirrored pair either side of 1/1.0723805294763609 for coin -1 behaves alike; `math.log` is monotone, so no other ratio lands between. Driven by prepr.sh's diff-mutant step at 4fee736fbe over the tests/features.py block from `R.section(\"COP learner duty floor keys` to `R.section(\"R10-COP-GATE (#2262)`: the mutant survived.",
+  "verdict": "equivalent"
+}


## Review scope: delta (later round over the reviewed head 9894911a81cdceb51eecec093a2527f93576d34e)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 9894911a81cdceb51eecec093a2527f93576d34e
Fix review: blocked 9894911a81cdceb51eecec093a2527f93576d34e red-check: pr-contract red at this head on the body's stale scope-line figure block (body-only; code review complete, no code finding)

bus-nonce: 726c78d84bb93219cfb28be599619661

## Block

`merge_train.py classify 9894911a81 --pr 3662` exits 1: `RED 9894911a81cdceb51eecec093a2527f93576d34e pending: none red: gate`. `gate` fails only on `FAIL pr-contract / pr-contract: failure (run 44147689564)`. The only error in that run is `[figure-block] line 171: block scope-line names head=f52f265d5b8b mb=30991a6b0d4c, this run is head=9894911a81cd mb=5e2ef89b4e73; re-render with figure_block.py refresh <body>`. This is paperwork (C5), and on its own it would be a Note under `merge`. A red head takes no `merge`, though (C8), so the verdict stays blocked until the body is refreshed. Refreshing the body with `figure_block.py refresh` re-runs pr-contract. The code, the tests and the harness below carry no finding, so a re-dispatch at an unchanged diff needs only the live checks re-read.

## Red checks

- `pr-contract / pr-contract` and `gate` are both in the owed-reds set. The cause is a body figure block left stale by the main merge 4e722000ab. The cheaper detector is `figure_block.py verify` on the body, run before the push that merged main. It takes seconds and is in the seat's prepr path. Classified root-cause-detectable. `tests / replay` (1 of 198 replay checks FAILED) and `tests / nightly-status` are red but not in `owed-reds`, so they are neither answered nor a block.

## Evidence

- Round: this is the third review of this PR. Round 1 at 1134fe3655 blocked it with class-open (probe/rev-3662-e230047b). Round 2 is probe/rev-3662-f2fe353e. The packet's scope reads `delta` over 1134fe3655. `review_carry.py 1134fe3655 9894911a81` prints FRESH-REVIEW: 37 branch-only commits, among them the dither-probe redesign d171c345d and the row-to-row judgement 0c822e649/511e53a8e. The delta is a production change in `custom_components/heatpump_optimizer/accuracy.py` (ScaleDither, ScaleProbe) and in `coordinator._fold_measured_cop`.
- Previous finding resolved. RESULT from the round-1 harness `ev/attack_drift_rows.py` (copied to ev/rows.py, 672 intervals, seed 1):
  - At 1134fe3655 it reproduces the block: ±15% p64, ±15% p80, ±30% p96 and the mix at π each give `follows` with the scale at 0.500.
  - At 9894911a81 every row gives `does_not_follow` at scale 1.000. That is identical to the null control, which reads swing0 → 1.000, does_not_follow (ev/B_head.txt, ev/B_prev.txt).
- Perturbation: with the dither removed (`step()` returns `base`), every row reads `pending` at 1.000 (ev/C_swing_under_dither_noop.txt). The harness moves under its own perturbation, and without the dither the probe cannot latch a false `follows`.
- Mutation proof. I made 7 hand mutants of accuracy.py and ran them one at a time through the features block driver (ev/drive.sh, ev/mut.py). All 7 were KILLED (ev/C_summary.txt):
  - dither_noop: 25 checks failed
  - coin_always_plus: 3
  - no_pair_differencing_levels: 17
  - follows_inverted: 18
  - no_bound: 2
  - drop_clamp_reseed: 3
  - follows_no_owed: 3

  The unmutated block prints `ALL 116 FEATURES BLOCK PASSED`.
- Full suite: `PYTHONPATH=tests/hastub python3 tests/features.py` at the head prints `ALL 5875 FEATURE CHECKS PASSED`, rc 0 (ev/D_features_head.txt).
- The commits since 1134fe3655 that are not merges are four `ci: pin killed mutants` commits, and they add only `tests/mutation_ledger/killed_by/*.json`. The `--remerge-diff` output of every first-parent merge is empty. The merge driver resolved `tests/structure_budgets.json` and `tests/closures.json` (LEDGER-MERGE: resolved).
- `git merge-tree --write-tree origin/main 9894911a81` exits 0 (ev/merge-tree.txt). There is no conflict, and the driver printed `LEDGER-MERGE: resolved tests/closures.json`.
- The three-dot diff from 5e2ef89b4e to 9894911a81 leaves VERSION, the manifest version and RELEASE_NOTES.md untouched.
- `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- The head re-read at the verdict is 9894911a81, which equals the PR branch tip (ev/HEAD.txt).
- Not re-derived: I ran rows.py with seed 1 only and did not re-run round 1's seed 1–5 sweep. The mutants ran on the features block only; the full script was not re-run per mutant. At the head the null control folds 0 of 672 intervals, against 48 at 1134fe3655. Over this window the probe stays at 1.000 without folding. The features block's follower rows still fail under follows_inverted, so true-follower detection is pinned by tests.

## Delta diff: git diff 9894911a81cdceb51eecec093a2527f93576d34e 454d4fc425a98e3bfbc8ab30c17d914f6f89b8c7
diff --git a/.claude/workflows/audit-plan.js b/.claude/workflows/audit-plan.js
index 0a06aa738b..ee596b3d2c 100644
--- a/.claude/workflows/audit-plan.js
+++ b/.claude/workflows/audit-plan.js
@@ -66,7 +66,8 @@ Read the class-grouped draft roster ${draft} and the verified register (dev/audi
 Measure the fork ${fork} once into the plan's evidence: run
   python3 tools/audit/seat/plan_audit.py snapshot --ref ${fork} --instrument ${fork} --out ${planDir}/holdouts/fork.json
 (it takes minutes; run it detached with tools/audit/seat/daemonize.py and wait on its exit, then read the file). It records the fork's score vector and gate-only tripwires, structure budgets, behaviour inventory, mutation kill rate and change coupling -- the holdouts the plan must not regress.
-Return JSON {draft_path, groups: [{group, issues, fixes, findings, severity, files, after, architect_note}], findings: [{id, dimension, severity, title, class, seam}], holdouts_path}. Refuse, by returning an empty groups array, if the draft roster is absent or carries no group: audit-verify must run first.`,
+If dev/audit/rounds/round${round - 1}/PLAN/PLAN.json carries an \`objective\` block, settle it (decision 0018): python3 tools/audit/seat/plan_audit.py settle --plan dev/audit/rounds/round${round - 1}/PLAN/PLAN.json --record dev/audit/yardstick/round${round - 1}/OBJECTIVE.json --json ${planDir}/PREVIOUS-SETTLEMENT.json, and return that path as previous_settlement (null when there is no such block: a first plan).
+Return JSON {draft_path, groups: [{group, issues, fixes, findings, severity, files, after, architect_note}], findings: [{id, dimension, severity, title, class, seam}], holdouts_path, previous_settlement}. Refuse, by returning an empty groups array, if the draft roster is absent or carries no group: audit-verify must run first.`,
   { label: 'plan/read', schema: { type: 'object', required: ['groups', 'findings'], properties: { groups: { type: 'array', items: { type: 'object' } }, findings: { type: 'array', items: { type: 'object' } }, holdouts_path: { type: 'string' } } } },
 )
 if (!draftRead) throw new Error('the draft read failed (agent returned null); relaunch')
@@ -96,8 +97,9 @@ const moves = await agent(
   `You are the architect/planner of audit round ${round}, continuing in ${worktree} after your triage ${JSON.stringify(triage)}: architect-planner.md steps 5-9 (ADRs, the moves to the programme target, fitness functions, the roster, the risks).
 Target: score.py --diff ${fork} <the round's stamp> reads dS >= ${targetDs} with the counters on, admissible end to end, at least three scored classes improving, and no metric supplying more than 40% of the dS. Plan findings first; where they fall short add refactor groups with no finding, each carrying its evidence and the scenario it serves. Every move names its metric(s), predicted dS per metric, its ADR and its fitness functions (structure budgets, gate-only tripwires, the behaviour inventory, mutation kill rate, change coupling, and any counter its metric can be gamed through). Never plan a move that deletes behaviour, renames or splits to dodge a counter, or edits the scorer.
 EVERY group gets one move entry, including a finding group expected to be score-neutral ("metrics: {}, dS: 0"): the stamp's move ledger reconciles each merged PR's own Architecture score block against this plan, and a group with no entry reads as a dS no move explains.
-Write the ADRs as ${planDir}/ADR-*.md (context, decision, alternatives, consequences, scenarios served) and ${planDir}/PLAN.md. Return JSON {groups: [{group, findings, size, seam, hot_files, after, architect_note}], moves: [{group, adr, metrics: {metric: predicted dS}, dS}], projected_dS, critical_chain: [group], depth, hours, risks: [{risk, check}]}.`,
-  { label: 'plan/moves', phase: 'Plan the architecture', schema: { type: 'object', required: ['groups', 'moves', 'projected_dS'], properties: { groups: { type: 'array', items: { type: 'object', required: ['group'] } }, moves: { type: 'array', items: { type: 'object', required: ['group', 'metrics'] } }, projected_dS: { type: 'number' } } } },
+Decision 0018's objective ranks the work and the target is its floor (architect-planner.md, the objective paragraph; the grammar is tools/audit/seat/instruments/plan_audit.py.md): return an objective block {baseline: {record: "dev/audit/yardstick/round${round - 1}/OBJECTIVE.json", tree}, terms: {<each term of dev/audit/config/objective.json>: {direction: up|down|hold with basis, or undecided with builder, the only value for a term NO-READ in that record}}, groups: {<every group>: {rank, removes, escapes, classes, cards, examined_by}}, edges: [{from, to, adr}] for every rank-1 group waiting on a rank-2 group, dispositions: {<each MISSED line of ${draftRead.previous_settlement ?? 'no previous settlement (a first plan)'}>: <group or card>}}. Write no hour, chain or date into it: the check projects them.
+Write the ADRs as ${planDir}/ADR-*.md (context, decision, alternatives, consequences, scenarios served) and ${planDir}/PLAN.md. Return JSON {groups: [{group, findings, size, seam, hot_files, after, architect_note}], moves: [{group, adr, metrics: {metric: predicted dS}, dS}], projected_dS, objective, critical_chain: [group], depth, hours, risks: [{risk, check}]}.`,
+  { label: 'plan/moves', phase: 'Plan the architecture', schema: { type: 'object', required: ['groups', 'moves', 'projected_dS', 'objective'], properties: { groups: { type: 'array', items: { type: 'object', required: ['group'] } }, moves: { type: 'array', items: { type: 'object', required: ['group', 'metrics'] } }, projected_dS: { type: 'number' }, objective: { type: 'object' } } } },
 )
 if (!moves) throw new Error('the move plan failed (agent returned null); relaunch')
 const planGroups = replyField(moves.groups, 'array', 'plan/moves: groups')
@@ -113,9 +115,11 @@ const planJson = {
   groups: planGroups, moves: planMoves, projected_dS: moves.projected_dS,
   critical_chain: moves.critical_chain ?? [], depth: moves.depth ?? null, hours: moves.hours ?? null,
   risks: moves.risks ?? [], holdouts: draftRead.holdouts_path ?? null,
+  objective: moves.objective,
 }
 const writePlan = await agent(
-  `In ${worktree}, write ${planDir}/PLAN.json with exactly this content (it is the plan the move ledger reads at the stamp):\n${JSON.stringify(planJson, null, 1)}\nAlso write the round's roster draft to ${draft} in the form audit-verify writes it (one entry per group, with its issues, findings, severity, files, after, size and architect note; resume.stage "planned", resume.branch "handoff/R${round}-<topic>" per group). Run node tools/policy/brief_lint.mjs and return its exit code and error lines, not the summary.`,
+  `In ${worktree}, write ${planDir}/PLAN.json with exactly this content (it is the plan the move ledger reads at the stamp):\n${JSON.stringify(planJson, null, 1)}\nThen set objective.pin in that file to {roster_path: "${draft}", roster_blob: <git hash-object ${draft}, after you write it>, start: <now, to the minute, as YYYY-MM-DDTHH:MM:00Z>, durations_blob: <git rev-parse HEAD:tools/plan/durations.json>}.
+Also write the round's roster draft to ${draft} in the form audit-verify writes it (one entry per group, with its issues, findings, severity, files, after, size and architect note; resume.stage "planned", resume.branch "handoff/R${round}-<topic>" per group). Run node tools/policy/brief_lint.mjs and return its exit code and error lines, not the summary.`,
   { label: 'plan/write', phase: 'Plan the architecture', schema: { type: 'object', required: ['brief_lint_rc'], properties: { brief_lint_rc: { type: 'integer' } } } },
 )
 if (!writePlan) throw new Error('the plan write failed (agent returned null); relaunch')
@@ -123,12 +127,15 @@ if (writePlan.brief_lint_rc !== 0) throw new Error(`the roster draft fails brief
 
 phase('Publish the plan')
 const publish = await agent(
-  `In ${worktree}, commit ${planDir}/ and ${draft} with the subject "audit round ${round}: P3 plan" (no footer, no session link) and publish that commit as the constant ref ${planRef}: run tools/audit/seat/ref_privacy.py guard --ref ${planRef} first, then git push origin HEAD:refs/heads/${planRef} and read back origin's tip. A refused or failed push is returned, never forced. Do not open a pull request.
-Return JSON {sha: <the published commit, 40 hex>, pushed: <bool>, readback: <string>, command: <the exact command line the orchestrator runs if pushed is false>}.`,
-  { label: 'plan/publish', phase: 'Publish the plan', schema: { type: 'object', required: ['sha'], properties: { sha: { type: 'string' }, pushed: { type: 'boolean' }, readback: { type: 'string' }, command: { type: 'string' } } } },
+  `In ${worktree}, commit ${planDir}/ and ${draft} with the subject "audit round ${round}: P3 plan" (no footer, no session link). Before any push, run the objective check at that commit (decision 0018): python3 tools/audit/seat/plan_audit.py objective-check --ref <the commit> --plan ${planDir}/PLAN.json --register dev/audit/rounds/round${round}/JUDGE.json${draftRead.previous_settlement ? ` --previous ${draftRead.previous_settlement}` : ''} --write, commit the ${planDir}/PROJECTION.json it writes, and run the same command without --write at the new commit. A non-zero exit is returned with its FAIL lines and nothing is pushed. Then publish that commit as the constant ref ${planRef}: run tools/audit/seat/ref_privacy.py guard --ref ${planRef} first, then git push origin HEAD:refs/heads/${planRef} and read back origin's tip. A refused or failed push is returned, never forced. Do not open a pull request.
+Return JSON {sha: <the published commit, 40 hex>, objective_rc: <the last objective-check exit code>, objective_fails: [<its FAIL lines>], pushed: <bool>, readback: <string>, command: <the exact command line the orchestrator runs if pushed is false>}.`,
+  { label: 'plan/publish', phase: 'Publish the plan', schema: { type: 'object', required: ['sha', 'objective_rc'], properties: { sha: { type: 'string' }, objective_rc: { type: 'integer' }, objective_fails: { type: 'array', items: { type: 'string' } }, pushed: { type: 'boolean' }, readback: { type: 'string' }, command: { type: 'string' } } } },
 )
 if (!publish) throw new Error('the plan publish failed (agent returned null); relaunch')
 if (!/^[0-9a-f]{40}$/.test(String(publish.sha))) throw new Error(`the plan publish returned ${JSON.stringify(publish.sha)}, not a 40-hex commit`)
+// An absent objective_rc is the schema's refusal (`required`); a reported
+// non-zero one stops P3 here, before the review reads an unchecked plan.
+if (publish.objective_rc !== undefined && publish.objective_rc !== 0) throw new Error(`the objective check refused the plan (rc=${publish.objective_rc}): ${JSON.stringify(publish.objective_fails ?? [])}; the plan is not published`)
 let planSha = String(publish.sha)
 log(`plan ${planRef} published at ${planSha}${publish.pushed === false ? ` (NOT PUSHED; the orchestrator runs: ${publish.command ?? '(no command returned)'})` : ''}`)
 
@@ -146,7 +153,7 @@ const review = (n, sha) => agent(
 2. attack the three largest groups and the three on the critical chain (is the owning seam real in the code? is any edge a file order edge?);
 3. re-derive each move's predicted dS from its prototype or prediction (a prediction resting on a renamed or split count, a deleted feature or a scorer change is metric-gamed);
 4. check the target's conditions: admissible end to end, the spread rule, the holdouts named, fitness functions per move;
-5. check the time: re-run the projection, the critical chain and the hot-file order;
+5. check the time and the objective: re-run python3 tools/audit/seat/plan_audit.py objective-check --ref ${sha} --plan ${planDir}/PLAN.json --register dev/audit/rounds/round${round}/JUDGE.json${draftRead.previous_settlement ? ` --previous ${draftRead.previous_settlement}` : ''} (it must print OBJECTIVE PASS), the critical chain and the hot-file order; attack three ranks and three keyed effects in the code, the rank-1 groups with most predicted dS per finding first; read the floor cost against point 4's cheap test;
 6. check the ADRs against the scenarios.
 Return JSON {verdict: "approve"|"revise", sha: "${sha}", points: [string]}.`,
   { label: `plan/review-${n}`, phase: 'Plan review', schema: { type: 'object', required: ['verdict', 'sha', 'points'], properties: { verdict: { type: 'string', enum: ['approve', 'revise'] }, sha: { type: 'string' }, points: { type: 'array', items: { type: 'string' } } } } },
@@ -156,7 +163,7 @@ let revisions = 0
 while (verdict.verdict === 'revise' && revisions < 2) {
   revisions += 1
   const revised = await agent(
-    `You are the architect/planner of audit round ${round}, in ${worktree}. The plan reviewer returned revise at ${planSha} with these points: ${JSON.stringify(verdict.points)}. Address each one in ${planDir}/ (the ADRs and PLAN.md; update PLAN.json's moves and projected dS if a prediction changes), re-run the roster's brief_lint, then commit with the subject "audit round ${round}: P3 plan revision ${revisions}" and push it as the constant ref ${planRef} after tools/audit/seat/ref_privacy.py guard --ref ${planRef}, with git push origin HEAD:refs/heads/${planRef}; read back the ref's tip. Do not argue a point away without a measurement: the reviewer's next pass reads the plan, not your reply. Return JSON {sha: <the pushed commit, 40 hex>, addressed: [string]}.`,
+    `You are the architect/planner of audit round ${round}, in ${worktree}. The plan reviewer returned revise at ${planSha} with these points: ${JSON.stringify(verdict.points)}. Address each one in ${planDir}/ (the ADRs and PLAN.md; update PLAN.json's moves, objective block and projected dS if a prediction changes), re-run the roster's brief_lint, then commit with the subject "audit round ${round}: P3 plan revision ${revisions}", re-run objective-check --write at that commit as the publish step did, commit PROJECTION.json, and only once the check without --write passes at the new commit push it as the constant ref ${planRef} after tools/audit/seat/ref_privacy.py guard --ref ${planRef}, with git push origin HEAD:refs/heads/${planRef}; read back the ref's tip. Do not argue a point away without a measurement: the reviewer's next pass reads the plan, not your reply. Return JSON {sha: <the pushed commit, 40 hex>, addressed: [string]}.`,
     { label: `plan/revise-${revisions}`, phase: 'Plan review', schema: { type: 'object', required: ['sha', 'addressed'], properties: { sha: { type: 'string' }, addressed: { type: 'array', items: { type: 'string' } } } } },
   )
   if (!revised) throw new Error(`the revision ${revisions} failed (agent returned null); relaunch`)
diff --git a/README.md b/README.md
index d2d90a75dc..9f326cfe7c 100644
--- a/README.md
+++ b/README.md
@@ -61,8 +61,9 @@ and a cool-only heat-curve correction are all estimated
 from your own house. Every learner is snapshotted weekly (the last eight are
 kept), and a drift watchdog can roll them back to the last healthy snapshot.
 
-**Knows what your electricity actually costs.** Tibber spot prices, time-of-use
-grid transfer fees, the monthly capacity (*effekt*) tariff and its billing clock,
+**Knows what your electricity actually costs.** Spot prices from Tibber or a
+price sensor, time-of-use grid transfer fees, the monthly capacity (*effekt*)
+tariff and its billing clock,
 PV self-consumption priced at what consuming actually costs you, and a learned
 diurnal price prior for the part of the horizon that has not been published yet.
 A live peak guard and a main-fuse headroom advisor act inside the metering window
@@ -128,7 +129,7 @@ or history. Monetary units follow your instance currency.
 ```mermaid
 flowchart LR
     subgraph inputs["Inputs"]
-        tibber["Tibber API<br/>hourly prices"]
+        tibber["Tibber API or a price sensor<br/>hourly prices"]
         weather["HA weather entity<br/>temperature, wind,<br/>rain, irradiance"]
         meteo["Open-Meteo<br/>optional irradiance"]
         ha["Your HA sensors<br/>temps, power, presence"]
@@ -150,7 +151,7 @@ flowchart LR
     subgraph out["Outputs"]
         ent["Entities<br/>sensors, binary sensors,<br/>buttons, switches,<br/>climate, datetime"]
         card["Dashboard card<br/>plan chart + editor"]
-        ctl["Heat pump switch /<br/>ECL110 displace /<br/>frequency advisor"]
+        ctl["Heat pump switch /<br/>heat-curve displace /<br/>frequency advisor"]
     end
 
     tibber --> pm
@@ -240,9 +241,9 @@ act on" — pricing and planning without actuating anything.
 | Control path | You provide | The optimizer writes |
 |---|---|---|
 | **On/off switch** | a `switch` that turns the heat pump on and off | may turn it off during expensive hours |
-| **ECL110 heat curve** | a Danfoss ECL110-compatible weather-compensated controller, reachable over MQTT | a heat-pump on/off decision and an integer parallel shift (*displace*) onto the controller's own heat curve |
-| **Heat-curve offset entity** | a controller whose volatile whole-curve offset is a `number` entity (for example a Luxtronik SHI heating offset) | the same displace as a temperature difference via `number.set_value`, bounded to ±3 K by default; 0 again when the optimizer is turned off or unloaded |
-| **Heat-curve stored parameter** | a controller with no volatile offset, whose stored curve setting is a `number` entity (kind *persistent*) | its value before the first write plus the displace, within ±3 K and at most 12 writes a day by default; that value written back when the optimizer is turned off or unloaded |
+| **Heat curve, over MQTT** | a weather-compensated controller that takes its curve offset over MQTT (for example a Danfoss ECL110 through an MQTT bridge) | a heat-pump on/off decision and an integer parallel shift (*displace*) onto the controller's own heat curve |
+| **Heat curve, offset entity** | a controller whose volatile whole-curve offset is a `number` entity (for example a Luxtronik SHI heating offset) | the same displace as a temperature difference via `number.set_value`, bounded to ±3 K by default; 0 again when the optimizer is turned off or unloaded |
+| **Heat curve, stored parameter** | a controller with no volatile offset, whose stored curve setting is a `number` entity (kind *persistent*) | its value before the first write plus the displace, within ±3 K and at most 12 writes a day by default; that value written back when the optimizer is turned off or unloaded |
 | **Compressor frequency** | the compressor frequency exposed as a `number` entity (typically from Modbus or ESPHome) | the recommended frequency via `number.set_value` — but only once you switch the mode to Control |
 
 The boundaries of each path — what it can reach and what it cannot — are
@@ -252,8 +253,9 @@ limitations that apply to the integration as a whole.
 Each path in full: [Switch and climate entity](#switches-climate-and-datetime-entities),
 [Inverter frequency: observe first, control if you say
 so](#inverter-frequency-observe-first-control-if-you-say-so),
-[ECL110 heat-curve control](#ecl110-heat-curve-control); the setup fields for
-all three live in [docs/configuration.md](./docs/configuration.md).
+[Heat-curve control](#heat-curve-control) (three ways: MQTT topics, an offset
+entity, a stored curve parameter); the setup fields for all three paths live
+in [docs/configuration.md](./docs/configuration.md).
 
 ## Known limitations
 
@@ -272,16 +274,17 @@ installing rather than discover it after:
   broadest path — any on/off `switch` will do, and the only one of the three
   that needs nothing from the pump's electronics — but any control finer than
   on-and-off needs one of the other paths.
-- **ECL110 control is MQTT-only; other controllers need an offset entity.** The
-  ECL110 path is for installs that have such a controller on MQTT, and
-  publishing goes through Home Assistant's own `mqtt.publish` service, "so the
-  MQTT integration has to be set up". The two command topics ship empty, so an
-  install without an ECL110 has nothing to clear on the options page. Without
-  MQTT, the displace reaches only a controller whose heat-curve offset is a
-  volatile `number` entity, 0 neutral; an absolute or stored curve parameter
-  is not supported in this version. Details in
-  [ECL110 heat-curve control](#ecl110-heat-curve-control) and
-  [docs/ecl110.md](./docs/ecl110.md).
+- **Heat-curve control needs MQTT or a `number` entity on your controller.**
+  Over MQTT, publishing goes through Home Assistant's own `mqtt.publish`
+  service, "so the MQTT integration has to be set up"; the two command topics
+  ship empty, so an install whose controller takes nothing over MQTT has
+  nothing to clear on the options page. Without MQTT, the displace reaches a
+  controller only through a `number` entity: a volatile offset, 0 neutral, or
+  a curve setting the controller stores, which wears its memory and is capped
+  at a few writes a day. An absolute curve point (an entity whose range
+  excludes 0) is refused as an offset. Details in
+  [Heat-curve control](#heat-curve-control) and
+  [docs/heat-curve.md](./docs/heat-curve.md).
 - **Frequency control needs a `number` entity and your explicit say-so.** The
   path exists only if the compressor frequency is exposed as a `number`
   entity (Modbus, ESPHome). The default Observe mode "learns and recommends
@@ -372,7 +375,7 @@ and every one of its entities and stops every command to the heat pump. Three
 things are left behind on purpose, because deleting them is your call:
 
 - **The heat pump keeps its last command.** The last setpoint the optimizer
-  wrote to your thermostat, or the last ECL110 displacement it published, stays
+  wrote to your thermostat, or the last heat-curve displacement it published over MQTT, stays
   in force until you set the pump's own controls back. Nothing else is restored on
   removal: a heat-curve entity is the one exception, written back when the
   integration unloads (0 for an offset, the value it held before the first
@@ -655,8 +658,8 @@ every sensor is created on every install regardless of which group it is in.
 |---|---|---|---|
 | Prediction Accuracy | °C | Mean indoor-temperature error, with the signed bias and the last diagnosis in attributes | Diagnostic; unavailable until an interval has been scored |
 | Learning Comfort Weight | — | The comfort weight in force, learned or configured | Diagnostic |
-| ECL110 Displace | °C | The parallel shift commanded to an ECL110 heat curve | Diagnostic; disabled by default unless an ECL110 MQTT topic is configured at setup; unavailable without one |
-| ECL110 Effective Displace | °C | The shift the controller has actually reached, after its own lag | Diagnostic; disabled by default unless an ECL110 MQTT topic is configured at setup; unavailable without one |
+| Heat-Curve Displace | °C | The parallel shift commanded to the controller's heat curve, over MQTT or to the heat-curve entity | Diagnostic; disabled by default unless a heat-curve MQTT topic or entity is configured at setup; unavailable without one |
+| Heat-Curve Effective Displace | °C | The shift the controller has actually reached, after its own lag | Diagnostic; disabled by default unless a heat-curve MQTT topic or entity is configured at setup; unavailable without one |
 | Valve Target Recommendation | °C | What to set a manual mixing valve to, and why | Diagnostic; disabled by default and unavailable until a throttling mixing-valve mode is configured (manual, smart read or smart write) — a valve-less install gets neither a hidden sensor nor one stuck at unknown |
 | Sensor-Gap Advisor | CUR | Estimated extra cost per month, in your currency, from the highest-value empty sensor slot | Diagnostic; outdoor, house meter, DHW probe |
 | Wood-Burn Night Advisor | — | 48 h light/skip advice when the wood furnace is on | Diagnostic; disabled by default; advisory only — never lights the stove |
@@ -665,7 +668,8 @@ every sensor is created on every install regardless of which group it is in.
 Disabled by default: Buffer Tank Temperature, Compressor Frequency
 Advisor, Compressor Starts, Cost Contract Comparison, Cost Monthly Peak Power,
 Cost Power Headroom, DHW Heavy Day Demand, DHW Mixed Water, DHW Temperature,
-ECL110 Displace, ECL110 Effective Displace, Floor Heating Return Temperature,
+Floor Heating Return Temperature, Heat-Curve Displace, Heat-Curve Effective
+Displace,
 Lower Floor Temperature, Measured Power, Slab Temperature (Estimated), Solar
 Surplus Forecast, Upper Floor Temperature, Valve Target Recommendation,
 Wood-Burn Night Advisor and Wood Cheaper Than Heat Pump.
@@ -852,7 +856,7 @@ hard-coded to the entity ids the examples assume.
 sequenceDiagram
     autonumber
     participant C as Coordinator
-    participant P as Prices (Tibber + learned prior)
+    participant P as Prices (Tibber or a price sensor, + learned prior)
     participant W as Weather entity (HA)
     participant S as Your sensors
     participant M as Thermal model
@@ -871,7 +875,7 @@ sequenceDiagram
     O->>O: solve: minimize cost + comfort penalty<br/>subject to comfort floor, tank limits,<br/>legionella clock, fuse and peak caps
     O-->>C: space + DHW slot plan
     C->>C: apply manual-plan pins,<br/>safety releases pinned-off slots
-    C->>E: publish plan sensors, switch the heat pump,<br/>ECL110 displace / frequency advice
+    C->>E: publish plan sensors, switch the heat pump,<br/>heat-curve displace / frequency advice
     Note over C: between plans the peak guard folds power-meter events<br/>and flips a flag (2 agree to engage, 2 to clear).<br/>It never solves — the next solve only reads the flag
     Note over M: afterwards: compare prediction against reality,<br/>nudge the learned parameters
 ```
@@ -1086,16 +1090,30 @@ Each clears itself once the cause is gone.
 - **Silent windows are not enforced** — the capacity-limited slot is not a switch the integration can hold. Assign the pump's own night-mode switch, or remove the silent windows.
 - **The heat pump cannot hold the hot water minimum** — You named a *Hot water start hysteresis* entity, and the hot water minimum sits above the temperature the pump starts a charge at (its hot water target less that hysteresis). The plan places no charge the pump would not start, so it shows the tank falling under the minimum before each charge. Lower the minimum to the start temperature or less, raise the hot water set-point, or reduce the hysteresis on the pump.
 
-## ECL110 heat-curve control
+## Heat-curve control
 
-The integration can drive a Danfoss ECL110-compatible controller over MQTT,
-publishing a heat-pump on/off decision and an integer parallel shift (*displace*)
-onto the controller's own heat curve. The ECL110 settings live only
-on the **Heat curve control** options page, not in initial setup, and
-both ECL110 sensors are disabled by default. The MQTT topics ship empty;
-nothing is published or subscribed until you set a topic, so an install without
-an ECL110 never touches the topics at all. Topics, payloads, options and the
-PI/PID lag handling are documented in [docs/ecl110.md](./docs/ecl110.md).
+<a id="ecl110-heat-curve-control"></a>
+
+The integration can shift a weather-compensated controller's own heat curve:
+up in cheap hours, down in expensive ones, as an integer parallel shift
+(*displace*). It reaches the controller one of three ways:
+
+- **Over MQTT**, to a controller that takes its offset there — for example a
+  Danfoss ECL110 through the strutsfarm/ecl110 bridge — with a heat-pump
+  on/off decision beside the displace;
+- **to an offset entity**, a volatile whole-curve offset Home Assistant
+  exposes as a `number` (for example a Luxtronik SHI heating offset), written
+  back to 0 when the optimizer is turned off or unloaded;
+- **to a stored curve parameter**, a `number` the controller keeps in memory,
+  displaced from its own value at most a few times a day and written back on
+  off.
+
+The settings live only on the **Heat curve control** options page, not in
+initial setup, and both heat-curve sensors are disabled by default. The MQTT
+topics ship empty; nothing is published or subscribed until you set a topic,
+so an install whose controller takes nothing over MQTT never touches the
+topics at all. The three ways, their options, payloads and the PI/PID lag
+handling are documented in [docs/heat-curve.md](./docs/heat-curve.md).
 
 ## Project status
 
@@ -1159,7 +1177,7 @@ before installing; it applies with full force.
 | [docs/dashboard-card.md](./docs/dashboard-card.md) | The card: options, interactions, editing limits |
 | [docs/automations.md](./docs/automations.md) | Complete automation examples using only the entities and services the integration creates |
 | [docs/architecture.md](./docs/architecture.md) | Module map and how a plan is made, for anyone reading or changing the code |
-| [docs/ecl110.md](./docs/ecl110.md) | ECL110 MQTT control |
+| [docs/heat-curve.md](./docs/heat-curve.md) | Heat-curve control, three ways: MQTT topics (for example a Danfoss ECL110), an offset entity, a stored curve parameter |
 | [DISCLAIMER.md](./DISCLAIMER.md) | The full disclaimer |
 
 ## Disclaimer
diff --git a/blueprints/automation/notifications.yaml b/blueprints/automation/notifications.yaml
index 58f79d70bb..d6eeaaee75 100644
--- a/blueprints/automation/notifications.yaml
+++ b/blueprints/automation/notifications.yaml
@@ -145,7 +145,7 @@ action:
                 elif data.cause == 'idle_other_channel' %}: the other channel
                 has the capacity{% elif data.cause == 'idle_solar' %}: the
                 plan is waiting for solar{% elif data.cause == 'idle_dearer'
-                %}: the hour is dearer than the hours used{% elif
+                %}: the hour is more expensive than the hours used{% elif
                 data.cause == 'idle_coasting' %}: the house is above the floor
                 and coasting{% elif data.peak_guard_suppressing %}: the peak
                 guard is holding heating back{% endif %}.
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index 0b4111fb08..a0b4d0c96e 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -608,6 +608,12 @@ OUTAGE_DHW_DELAY_MINUTES: Final = 45.0
 # the electricity, which is a trade worth taking; anyone who wants the starts
 # back has a knob denominated in real currency. `tests/validate.py` reports the
 # start count per scenario, which is how that decision gets made from evidence.
+# The option's default stays 0. One exception is applied at solve time, not
+# here: an install whose planned levels are clamped (it cannot duty-cycle)
+# and that prices no start plans at ``optimizer.CLAMPED_DEFAULT_START_PRICE``
+# (``OptimizationConfig.start_price``), because a clamped plan is committed to
+# whole runs and an unpriced commit can ship more starts than the plan it
+# replaced.
 CONF_CYCLING_COST: Final = "compressor_cycling_cost"
 DEFAULT_CYCLING_COST: Final = 0.0
 
diff --git a/custom_components/heatpump_optimizer/ledger.py b/custom_components/heatpump_optimizer/ledger.py
index 16eb3e733b..d53e5b4098 100644
--- a/custom_components/heatpump_optimizer/ledger.py
+++ b/custom_components/heatpump_optimizer/ledger.py
@@ -74,8 +74,10 @@ REFERENCE_BASIS_META = "reference_basis"
 #: booked as simulated. Bump when the booked reference changes: 1 spread a
 #: valved horizon by steady demand (released in v7.1.15), so its months are old;
 #: 2 held a valve-limited two-zone house at level floors below the plant's
-#: ceiling (released in v7.1.17), where pull request 3587 holds it at the valve top.
-REFERENCE_BASIS = 3
+#: ceiling (released in v7.1.17), where pull request 3587 holds it at the valve top;
+#: 3 held a single-zone valved house short of its setpoint, its curve missing the
+#: slab in series (released in v10.0.0), which R11-VALVE-REFERENCE's curve reaches.
+REFERENCE_BASIS = 4
 
 #: What ``migrate_ledger_v1`` stamps: every month a v1 store booked savings in predates it.
 OLD_REFERENCE_BASIS = 0
diff --git a/custom_components/heatpump_optimizer/mixing_valve.py b/custom_components/heatpump_optimizer/mixing_valve.py
index 0beace9193..89d9f038b6 100644
--- a/custom_components/heatpump_optimizer/mixing_valve.py
+++ b/custom_components/heatpump_optimizer/mixing_valve.py
@@ -81,6 +81,7 @@ def flow_setpoint(
     outdoor_temp: float,
     heat_loss_coefficient: float,
     emitter_ua: float,
+    free_heat_kw: float = 0.0,
 ) -> float:
     """The flow temperature the valve regulates to, in °C.
 
@@ -88,7 +89,10 @@ def flow_setpoint(
     *flow* temperature, following a weather-compensation curve. The curve here
     is derived rather than configured: the flow temperature that, in steady
     state, holds the house exactly at ``target_temp`` is the target plus the
-    house's standing loss spread over the emitter UA.
+    house's standing loss, less ``free_heat_kw`` the house gains without the
+    emitters, spread over ``emitter_ua``: the conductance from the flow to the
+    room, in kW/K, which a caller whose emitters heat the room through a slab
+    passes in series with it.
 
     This is what bounds discharge. The valve mixes return water into the flow,
     so the emitters never see raw tank water while the tank runs above the
@@ -106,7 +110,9 @@ def flow_setpoint(
     temperatures; the effective proportional gain is the emitter UA itself,
     in kW/K, which no step length can distort.
     """
-    q_hold = heat_loss_coefficient * max(0.0, target_temp - outdoor_temp)
+    q_hold = max(
+        0.0, heat_loss_coefficient * max(0.0, target_temp - outdoor_temp) - free_heat_kw
+    )
     return target_temp + q_hold / max(emitter_ua, 1e-6)
 
 
diff --git a/custom_components/heatpump_optimizer/narrative.py b/custom_components/heatpump_optimizer/narrative.py
index 3d0de3ff8b..426c66b33d 100644
--- a/custom_components/heatpump_optimizer/narrative.py
+++ b/custom_components/heatpump_optimizer/narrative.py
@@ -57,7 +57,7 @@ TEMPLATES: dict[str, dict[str, str]] = {
         "idle_other_channel": "idle for {hours} h because the other channel has the capacity",
         "idle_fuse": "idle for {hours} h, capped by the fuse",
         "idle_solar": "idle for {hours} h, waiting for solar",
-        "idle_dearer": "idle for {hours} h, dearer than the hours used",
+        "idle_dearer": "idle for {hours} h, more expensive than the hours used",
         "idle_coasting": "idle for {hours} h, above the floor and coasting",
         "pump_mode": "blocked by the heat pump's operating mode for {hours} h",
         "untagged": "{kwh} kWh outside the plan ({cost} {currency})",
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 267dd9e530..876fee23ad 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -198,7 +198,7 @@ def _engaged(opt: HeatPumpOptimizer) -> bool:
     :func:`_commit_runs`' candidates; unengaged it is the duty-cycle reading,
     with no start term to price.
     """
-    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels
+    return opt.config.start_price > 0 or opt.config.clamp_planned_levels
 
 
 #: The objectives a multi-start descends on in place of the true one
@@ -245,7 +245,7 @@ def _relaxed_plans(
     res = _multi_start_minimize(
         pair[0], starts, scope[0], args=(dhw_plan,), maxiter=300, batch_objective=pair[1])
     plans = [np.clip(res.x, 0.0, headroom)]
-    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:
+    if opt.config.start_price > 0 and _priced_stops(opt) is not None:
         free_room, free = rescope(None)
         pair = _descent_pair(opt, free[1], free[2], _UNPRICED)
         plans.append(np.clip(_multi_start_minimize(
@@ -258,7 +258,7 @@ def _priced_stops(opt: HeatPumpOptimizer) -> tuple[float, float] | None:
     """The learned stop probability per switch direction, ``None`` when no direction stops.
 
     The lost running time is charged on this alone; the price is this times
-    ``cycling_cost``, so an install that prices no cycle prices no switch.
+    ``start_price``, so an install that prices no start prices no switch.
     """
     stops = duty_legs.priced_pair(opt.config.duty_switch_stop_probability, 1.0)
     return stops if max(stops) > 0 else None
@@ -360,7 +360,7 @@ def _switch_cost_fn(
     floor, where the running share is flat; the unpriced descent has none.
     """
     stops, floor, rule = _priced_stops(opt), _duty_floor(opt), _leg_rule(opt)
-    p_max, cost = opt.model.params.max_electrical_power, opt.config.cycling_cost
+    p_max, cost = opt.model.params.max_electrical_power, opt.config.start_price
     p_min = opt.model.params.min_electrical_power
 
     def switch_cost(space: np.ndarray, dhw: np.ndarray | None, descent: str | None = None) -> Any:
@@ -381,13 +381,13 @@ def _with_switch_cost(level_cost: Any, switch_cost: Any) -> Any:
 
 
 def _start_cost_fn(opt: HeatPumpOptimizer, running: bool) -> Callable[[np.ndarray, str | None], Any]:
-    """The start term: ``cycling_cost`` per start of the combined draw (``runs``).
+    """The start term: ``start_price`` per start of the combined draw (``runs``).
 
     One entry per row of a ``[B, n]`` batch, a float for one plan. ``None``
     at zero cost and on a descent (:func:`_descent_pair`), and
     :func:`_with_switch_cost` then adds no operand.
     """
-    cost, p_min = opt.config.cycling_cost, opt.model.params.min_electrical_power
+    cost, p_min = opt.config.start_price, opt.model.params.min_electrical_power
 
     def start_cost(power: np.ndarray, descent: str | None) -> Any:
         if descent or not cost > 0:
@@ -447,7 +447,7 @@ def _avoid_priced_switches(
     """
     space, dhw, _ = incumbent
     stops = _priced_stops(opt)
-    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:
+    if stops is None or not opt.config.start_price > 0 or opt.model.params.dhw_store.combi:
         return incumbent
     floor = _duty_floor(opt)
     shipped, tank = _realize_joint(
@@ -539,7 +539,7 @@ def _run_plans(
     floor = runs.floor_kw(opt.model.params.min_electrical_power)
     heats = (hi >= floor) & ((other <= 0.0) | (space >= floor / 2.0))
     masks = runs.candidates(
-        space + other, h.prices, floor, hi + other, opt.config.cycling_cost,
+        space + other, h.prices, floor, hi + other, opt.config.start_price,
         dt=h.dt, running=h.compressor_running,
         forced=np.where((other > 0.0) | (lo > 0.0), 1.0, np.where(hi + other <= 0.0, 0.0, np.nan)),
     )
@@ -682,8 +682,8 @@ def _commit_runs(
     """A solve's relaxed plans as runs the pump can run, and the scope the
     plan that ships was scored in (Bankaifan, pull request 3529).
 
-    Identity on the first relaxed plan unengaged, and where no start has a
-    price and the projection changes nothing. Each relaxed plan is committed
+    Identity on the first relaxed plan unengaged; an engaged solve always
+    prices a start (:attr:`OptimizationConfig.start_price`). Each relaxed plan is committed
     on its own (:func:`_best_runs`) and the lowest score ships: a committed
     plan never scores above the first plan's projection, one more relaxed
     plan never raises the score, and a failure anywhere in this stage ships
@@ -693,8 +693,6 @@ def _commit_runs(
         return relaxed[0], scope
     _, hi, _, cycled = _stage_box(opt, scope[0], dhw)
     first = _projection(opt, relaxed[0], dhw, hi, cycled)
-    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):
-        return relaxed[0], scope
     try:
         return min((
             _best_runs(
@@ -2640,6 +2638,17 @@ class OptimizationResult:
         return self.room_temp_trajectory
 
 
+#: Currency per start a clamped install plans at when it prices no start
+#: (owner ruling Q2, R11-OUTSIDE-HONEST-STARTS-RUNS-P3). A clamped plan is
+#: committed to whole runs, and at no start price nothing stops that commit
+#: from shipping more starts than the duty-cycle plan it replaced; this is the
+#: smallest value on the ``defaults`` ladder of
+#: ``dev/audit/harnesses/r11_honest_starts_runs.py`` that returns both
+#: regressed rows to their start count before that commit, without lowering the
+#: lowest room. A configured price above zero is used as configured.
+CLAMPED_DEFAULT_START_PRICE: float = 0.1
+
+
 @dataclass
 class OptimizationConfig:
     """Configuration for the optimizer."""
@@ -2679,7 +2688,8 @@ class OptimizationConfig:
     # as a minimum-runtime constraint: that would make it a MILP, which is not
     # affordable inside a 30-second Home Assistant update on the hardware
     # this usually runs on.
-    #: Currency cost attributed to one compressor start.
+    #: Currency the user configured for one compressor start; every solve
+    #: prices ``start_price``, which reads it.
     #: Mirrors ``const.DEFAULT_CYCLING_COST`` rather than restating it, so the
     #: objective a harness builds directly is the objective that ships. The two
     #: had silently drifted apart once before, which meant the tests were
@@ -2734,6 +2744,17 @@ class OptimizationConfig:
     #: duty-cycle bounds, so their plans stay byte-identical.
     clamp_planned_levels: bool = False
 
+    @property
+    def start_price(self) -> float:
+        """Currency one planned compressor start costs: what every solve prices.
+
+        The configured ``cycling_cost``, except on a clamped install that
+        prices no start, which plans at :data:`CLAMPED_DEFAULT_START_PRICE`.
+        """
+        if self.clamp_planned_levels and not self.cycling_cost > 0:
+            return CLAMPED_DEFAULT_START_PRICE
+        return self.cycling_cost
+
     @property
     def n_steps(self) -> int:
         """Number of optimization steps."""
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 3eeedb705a..ba11b0cf09 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -594,12 +594,12 @@
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
               "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (a Luxtronik through its Smart Home Interface, for example, is assumed to be one); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
-              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
-              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
-              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
+              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (0.5 K on a Luxtronik, for example), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a controller can drop what was set when it goes unread (a Luxtronik Smart Home Interface, for one, drops every set value after 600 s without access); and no second tool writing the same registers (a Luxtronik, for one, then silently discards writes).",
+              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
+              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
             }
           },
           "plant": {
@@ -942,7 +942,7 @@
       },
       "heat_curve": {
         "title": "Heat curve control",
-        "description": "Shifts the heat curve up in cheap hours and down in expensive ones, through a Danfoss ECL110 over MQTT, a number entity that offsets your controller's curve, or both. Leave the topics and the entity empty if you have neither.",
+        "description": "Shifts your controller's heat curve up in cheap hours and down in expensive ones, three ways: over MQTT topics, to a controller that takes its offset there (a Danfoss ECL110 through an MQTT bridge, for example); to a number entity that offsets the curve; or to a curve setting the controller stores. The topics and the entity can be used together. Leave them all empty if your controller has none of these.",
         "data": {
           "ecl110_displace_set_topic": "Offset command topic",
           "ecl110_command_topic": "Legacy JSON command topic",
@@ -961,7 +961,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if you do not have a Danfoss ECL110.",
+          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if your controller does not take its offset over MQTT (a Danfoss ECL110 through an MQTT bridge is one that does).",
           "ecl110_command_topic": "Only needed for older setups that expect a JSON payload instead.",
           "ecl110_state_topic": "MQTT topic the controller reports its current state on.",
           "ecl110_mqtt_qos": "0 is fine for almost everyone.",
@@ -971,8 +971,8 @@
           "ecl110_pid_time_constant_hours": "Roughly how long the controller takes to act on a new offset. Used so the optimizer does not ask for changes faster than the system can follow.",
           "heat_curve_displace_entity": "A number entity that shifts your controller's heat curve. Kind offset: a whole-curve offset, 0 meaning no shift, that the controller forgets on a restart (for example a Luxtronik SHI heating offset); turning the optimizer off, or unloading it, writes 0. Kind persistent: a curve setting the controller stores; turning the optimizer off, or unloading it, writes back the value it held before the first write.",
           "heat_curve_target_kind": "Offset: a temperature difference, 0 neutral, not stored by the controller. Prefer it wherever your controller has one. Persistent: a curve setting the controller stores, displaced from its own value and written back on off; every write wears the controller's memory, so writes are limited per day.",
-          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
-          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
+          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
+          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
           "heat_curve_persistent_writes_per_day": "Writes in one local day, the write back on off included; one is always kept for it. 12 (six shift-and-return episodes) stays under the one documented manufacturer quota found (Daikin, 7000 a year); the margin below it is an estimate. 0 or 1 writes nothing. Above 19 exceeds that quota.",
           "heat_curve_persistent_min_dwell_minutes": "After a write, the next waits at least this long. 60 minutes is about three response times of a radiator system (a forum estimate); a slow floor may want 2 to 3 hours.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
@@ -1289,7 +1289,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "pump_duty_mode": "Off (the default) never writes the pump's operating mode or set-points. Observe writes none either and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). With any of the three, the heat pump on/off switch, if you have set one, is still switched by the plan. Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, unchanged on idle steps; on a step that plans both, hot water only for the hot-water share of the step and then heating, a share under 5 minutes going to the other duty; Heating + DHW while a boost or an anti-legionella cycle calls for both, and whenever the plan is not in charge), the hot water set-point entity (the hot water set-point configured on the hot water page, or the anti-legionella temperature during a cycle) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or the Heating flow ceiling) at full power, toward 5 °C (or the Minimum lift above the inlet water) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — on steps that heat the house, 25 °C on steps that do not (20 °C for a Return temperature set-point, or the entity's own minimum if that is higher), and 35 °C or the weather curve, whichever is higher, when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered instead: the hot water one to 30 °C, a flow set-point to the same 25 °C (20 °C for Return temperature), an indoor one to 5 °C, each never below the entity's own minimum. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. Where Capacity limited (night mode) is a switch and silent windows are scheduled, Control also holds that switch on inside a silent window and off outside one. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
-          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
+          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107, for example) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
           "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
@@ -1422,7 +1422,7 @@
         },
         "data_description": {
           "dso_product": "A dated Sweden-only table. Selecting a product writes transfer-fee rules and peak-tariff fields you can still edit, switches the transfer fee to Time-of-use rules and turns the peak tariff on. Verify against your bill: a product keeps writing its values after its end date. A product the table does not know writes nothing.",
-          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, so with it configured the plan finally sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
+          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, and a price sensor includes it only if you added it there yourself, so with it configured the plan sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
           "grid_fee_fixed": "A flat fee added in every hour, on top of the time-of-use rules or the live sensor's value. It only applies when Grid transfer fee is Time-of-use rules or Live sensor; with None it is ignored. Take it from your grid invoice.",
           "grid_fee_rules": "One rule per line, for example \"Nov-Mar Mon-Fri 06:00-22:00 = 0.25\". Month, weekday and time parts are each optional; overlapping rules add together, which matches a base fee plus a high-load surcharge. A comma between digits is a decimal separator, so \"0,25\" reads as 0.25 and never splits a rule.",
           "grid_fee_entity": "A sensor reporting the current fee in {currency}/kWh, for grids with dynamic fees. Its value is added to every planned hour.",
@@ -1534,7 +1534,7 @@
       },
       "modbus_prefill": {
         "title": "Pre-fill from a heat pump device",
-        "description": "For a Rotenso Windmi or another GCHV-built heat pump, read through the tuya_heat_pump project's Modbus package or through the pump's own Home Assistant device. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
+        "description": "Reads only what this page has a mapping for: a GCHV-built heat pump (a Rotenso Windmi, for example) through the tuya_heat_pump project's Modbus package, or a heat pump's own Home Assistant device, through its integration's published definitions where one is mapped here and otherwise by its entities' names. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
         "data": {
           "prefill_device": "Heat pump device (optional)",
           "modbus_prefill_prefix": "Modbus package entity prefix",
@@ -2004,10 +2004,10 @@
         "name": "DHW Temperature"
       },
       "ecl110_displace": {
-        "name": "ECL110 Displace"
+        "name": "Heat-Curve Displace"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 Effective Displace"
+        "name": "Heat-Curve Effective Displace"
       },
       "floor_heating_return_temperature": {
         "name": "Floor Heating Return Temperature"
@@ -2096,7 +2096,7 @@
           "dhw_window": "Heating hot water inside a hot water window",
           "idle": "Idle",
           "idle_coasting": "Above the floor, coasting",
-          "idle_dearer": "Dearer than the hours used",
+          "idle_dearer": "More expensive than the hours used",
           "idle_fuse": "Capped by the fuse",
           "idle_other_channel": "The other channel has the capacity",
           "idle_solar": "Waiting for solar",
@@ -2404,15 +2404,15 @@
           "description": "Heat loss multiplier when raining. 1.15 means 15% more heat loss in rain of 2 mm/h or more (wet building envelope effect); lighter rain scales it down in proportion, and 0.1 mm/h or less applies none of it."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID Time Constant",
-          "description": "Time constant (hours) for the ECL110 PI/PID response approximation. Lower values react faster, higher values are smoother."
+          "name": "Heat-Curve Controller Time Constant",
+          "description": "Time constant (hours) for the heat-curve controller's PI/PID response approximation. Lower values react faster, higher values are smoother."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 displace minimum",
+          "name": "Heat-curve displace minimum",
           "description": "Lowest parallel shift the optimizer may command, in °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 displace maximum",
+          "name": "Heat-curve displace maximum",
           "description": "Highest parallel shift the optimizer may command, in °C."
         },
         "quiet_silent_windows": {
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 6760bc994f..9966dbacb3 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -2266,16 +2266,27 @@ def _valve_flow_set(
 ) -> float:
     """The flow temperature the valve regulates to this step. A per-step
     ``valve_target`` (how a commanded valve holds its charge) beats the
-    configured target; an unconfigured one is the top of the comfort band."""
+    configured target; an unconfigured one is the top of the comfort band.
+
+    A single-zone valve feeds every emitter into the slab, which reaches the
+    room through ``slab_heat_transfer`` in series, and the room's
+    ``internal_gains`` cover part of its loss: the curve holds its target only
+    with both in it (R11-VALVE-REFERENCE). Two zones pass through unchanged."""
     if valve_target is not None:
         target = float(valve_target)
     else:
         target = p.mixing_valve_target or p.comfort_ceiling
+    free_heat_kw = 0.0
+    if not p.two_zone_enabled:
+        k_slab = p.slab_heat_transfer_floored
+        emitter_ua = emitter_ua * k_slab / (emitter_ua + k_slab)
+        free_heat_kw = p.internal_gains
     return mixing_valve.flow_setpoint(
         target_temp=target,
         outdoor_temp=outdoor_temp,
         heat_loss_coefficient=heat_loss_coefficient,
         emitter_ua=emitter_ua,
+        free_heat_kw=free_heat_kw,
     )
 
 
@@ -3487,11 +3498,12 @@ class ThermalModel:
         return u_wind
 
     def flow_target_for_indoor(self, indoor_target: float, outdoor_temp: float) -> float:
-        """Flow temperature `mixing_valve.flow_setpoint`'s curve implies for
-        `indoor_target` (#398) -- the same conversion `_simulate_step_two_zone`
-        uses to bound a dumb valve's delivery, reused rather than re-derived.
-        """
+        """The flow temperature the valve curve implies for `indoor_target` (#398): the plant's
+        own behind a single-zone valve, at zero wind; else `flow_setpoint` on both floors' loss."""
         p = self.params
+        if not p.two_zone_enabled and p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:
+            u = self.effective_heat_loss_coefficient(p.heat_loss_coefficient)
+            return _valve_flow_set(p, indoor_target, outdoor_temp, u, _valve_ua(p))
         heat_loss = self.effective_heat_loss_coefficient(
             p.upper_floor_heat_loss
         ) + self.effective_heat_loss_coefficient(p.lower_floor_heat_loss_learned)
@@ -4297,9 +4309,7 @@ class ThermalModel:
             # are uniform across it); a direct caller gets them computed as
             # the scalar branch does.
             valve_row = 0.0
-            if (p.mixing_valve_mode or mixing_valve.MODE_NONE) in (
-                mixing_valve.THROTTLING_MODES
-            ):
+            if p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:
                 if ua_valve is None:
                     ua_valve = (
                         p.max_electrical_power * p.cop_nominal_floored
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index f2f737d479..0c61d20d2c 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -540,7 +540,7 @@
           "learning_features": "Erweiterte Lernfunktionen",
           "grid_connection": "Sicherung und Spitzenwächter",
           "grid_fees": "Netzentgelte und Vertrag",
-          "heat_curve": "Heizkurvensteuerung (ECL110)",
+          "heat_curve": "Heizkurvensteuerung",
           "factory_reset": "Auf Werkseinstellungen zurücksetzen"
         }
       },
@@ -594,12 +594,12 @@
               "indoor_temp_entity": "Optional. Die tatsächliche Raumtemperatur. Ohne sie vertraut der Optimierer seinem eigenen Modell, das mit der Zeit abdriftet.",
               "outdoor_temp_entity": "Optional. Ein lokales Außenthermometer ist für die aktuelle Stunde genauer als die Vorhersage.",
               "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Steht die Steuerung der Pumpenfunktion auf Steuern, schreibt der Optimierer sie in jedem Planschritt, wie die Steuerung der Pumpenfunktion beschreibt, und das Ausschalten von Optimierer aktiv schreibt den Wert zurück, den die Entität vor dem ersten Schreiben zeigte. Bei Aus oder Beobachten wird sie nur gelesen, um zu bemerken, wenn sie nicht gelesen werden kann.",
-              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Der Optimizer leitet sie nie aus der Entität ab, nur das Vorausfüllen aus einem Wärmepumpengerät schlägt eine vor. Bei „Steuerung der Pumpenfunktion“ auf „Steuern“ schreibt der Optimizer die Raumtemperatur (Innentemperatur) bzw. die Wassertemperatur (Vorlauftemperatur, Rücklauftemperatur) des Plans in diese Entität.",
+              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen zum Beispiel für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Der Optimizer leitet sie nie aus der Entität ab, nur das Vorausfüllen aus einem Wärmepumpengerät schlägt eine vor. Bei „Steuerung der Pumpenfunktion“ auf „Steuern“ schreibt der Optimizer die Raumtemperatur (Innentemperatur) bzw. die Wassertemperatur (Vorlauftemperatur, Rücklauftemperatur) des Plans in diese Entität.",
               "flow_min_lift_k": "Mit Steuerung der Pumpenfunktion auf Steuern ist der bei der niedrigsten Planleistung geschriebene Wasser-Sollwert das gemessene Eingangswasser plus dieser Wert: Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass, und bei einer Entität mit Rücklauftemperatur nur die ersten drei. 5 K passt zu einem Regler, der seinen Vorlauf auf dem Sollwert hält. Von einem Regler, der die Zahl als Ziel für das Rücklaufwasser nimmt, wird angenommen, dass er seinen Verdichter umso stärker laufen lässt, je weiter das Ziel über dem Rücklauf liegt, er will also wahrscheinlich weniger; 1–2 K ist ein Ausgangspunkt, der an der gemessenen Frequenz und Leistung des Verdichters zu prüfen ist, kein gemessener Wert.",
               "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel. Ein Raumheizungs-Boost oder der Boost-Modus schreibt stattdessen in jedem Schritt das eigene Maximum der Sollwert-Entität (höchstens 70 °C); ein anderer Wert als 55 °C begrenzt auch das, also stelle bei einer Niedertemperatur-Fußbodenheizung einen ein.",
-              "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (Luxtronik: 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn eine Luxtronik Smart Home Interface verwirft nach 600 s ohne Zugriff alle gesetzten Werte; und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik verwirft Schreibvorgänge dann stillschweigend).",
-              "space_setpoint_low_limit_entity": "Optional. Ein Temperatursensor, der den niedrigsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (eine Luxtronik über ha-luxtronik-shi: \"Temperature: return target minimum\", Eingang 10104). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darunter, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts.",
-              "space_setpoint_high_limit_entity": "Optional. Ein Temperatursensor, der den höchsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (eine Luxtronik über ha-luxtronik-shi: \"Temperature: return limit\", Eingang 10103). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darüber, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts."
+              "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (bei einer Luxtronik zum Beispiel 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn ein Regler kann Gesetztes verwerfen, wenn er nicht abgefragt wird (eine Luxtronik Smart Home Interface etwa verwirft nach 600 s ohne Zugriff alle gesetzten Werte); und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik etwa verwirft Schreibvorgänge dann stillschweigend).",
+              "space_setpoint_low_limit_entity": "Optional. Ein Temperatursensor, der den niedrigsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (zum Beispiel eine Luxtronik über ha-luxtronik-shi: \"Temperature: return target minimum\", Eingang 10104). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darunter, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts.",
+              "space_setpoint_high_limit_entity": "Optional. Ein Temperatursensor, der den höchsten Wert meldet, den der Regler für die Sollwert-Entität oben annimmt (zum Beispiel eine Luxtronik über ha-luxtronik-shi: \"Temperature: return limit\", Eingang 10103). Damit sendet Geplanter Leistung über die gemessene Aufnahme folgen nie einen Wert darüber, statt die Grenze erst zu finden, wenn der Regler einen Schreibwert kappt. Nur von dieser Option verwendet; leer ändert sich nichts."
             }
           },
           "plant": {
@@ -941,8 +941,8 @@
         }
       },
       "heat_curve": {
-        "title": "Heizkurvensteuerung (ECL110)",
-        "description": "Für Danfoss-ECL110-Regler, die über MQTT angesteuert werden. Der Optimierer verschiebt die Heizkurve in günstigen Stunden nach oben und in teuren nach unten. Lass diese Felder leer, wenn du keinen solchen Regler hast.",
+        "title": "Heizkurvensteuerung",
+        "description": "Verschiebt die Heizkurve deines Reglers in günstigen Stunden nach oben und in teuren nach unten, auf drei Wegen: über MQTT-Topics an einen Regler, der seine Verschiebung dort annimmt (zum Beispiel ein Danfoss ECL110 über eine MQTT-Brücke); an eine Zahlenentität, die die Kurve verschiebt; oder an eine Kurveneinstellung, die der Regler speichert. Topics und Entität lassen sich zusammen nutzen. Lass alles leer, wenn dein Regler nichts davon bietet.",
         "data": {
           "ecl110_displace_set_topic": "Topic für Verschiebungsbefehl",
           "ecl110_command_topic": "Topic für Legacy-JSON-Befehl",
@@ -961,7 +961,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT-Topic, auf das die Parallelverschiebung der Heizkurve veröffentlicht wird. Solange dieses und das Legacy-Befehls-Topic unten leer sind, wird nichts veröffentlicht: Lass beide leer, wenn du keinen Danfoss ECL110 hast.",
+          "ecl110_displace_set_topic": "MQTT-Topic, auf das die Parallelverschiebung der Heizkurve veröffentlicht wird. Solange dieses und das Legacy-Befehls-Topic unten leer sind, wird nichts veröffentlicht: Lass beide leer, wenn dein Regler seine Verschiebung nicht über MQTT annimmt (ein Danfoss ECL110 über eine MQTT-Brücke tut das).",
           "ecl110_command_topic": "Nur für ältere Installationen nötig, die stattdessen eine JSON-Nutzlast erwarten.",
           "ecl110_state_topic": "MQTT-Topic, auf dem der Regler seinen aktuellen Zustand meldet.",
           "ecl110_mqtt_qos": "0 genügt für fast alle.",
@@ -971,8 +971,8 @@
           "ecl110_pid_time_constant_hours": "Ungefähr, wie lange der Regler braucht, um auf eine neue Verschiebung zu reagieren. Damit fordert der Optimierer keine schnelleren Änderungen an, als das System umsetzen kann.",
           "heat_curve_displace_entity": "Eine Zahlenentität, die die Heizkurve deines Reglers verschiebt. Typ Verschiebung: eine Verschiebung der ganzen Kurve, bei der 0 keine Verschiebung bedeutet und die der Regler bei einem Neustart vergisst (zum Beispiel eine Luxtronik-SHI-Heizverschiebung); Ausschalten oder Entladen des Optimierers schreibt 0. Typ beständig: eine Kurveneinstellung, die der Regler speichert; Ausschalten oder Entladen des Optimierers schreibt den Wert zurück, den sie vor dem ersten Schreiben hatte.",
           "heat_curve_target_kind": "Verschiebung: eine Temperaturdifferenz, 0 neutral, vom Regler nicht gespeichert. Nimm sie, wo immer dein Regler eine hat. Beständig: eine Kurveneinstellung, die der Regler speichert, von ihrem eigenen Wert verschoben und beim Ausschalten zurückgeschrieben; jeder Schreibvorgang nutzt den Speicher des Reglers ab, daher sind die Schreibvorgänge pro Tag begrenzt.",
-          "heat_curve_offset_band_k": "Der auf die Entität geschriebene Offset bleibt in beide Richtungen innerhalb so vieler Kelvin. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und Luxtroniks eigener Korrektur von ±5 K.",
-          "heat_curve_persistent_band_k": "Die gespeicherte Einstellung wird höchstens so viele Kelvin in jede Richtung von dem Wert verschoben, den sie vor dem ersten Schreiben hatte. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und Luxtroniks eigener Korrektur von ±5 K.",
+          "heat_curve_offset_band_k": "Der auf die Entität geschriebene Offset bleibt in beide Richtungen innerhalb so vieler Kelvin. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und der Benutzerkorrektur von ±5 K, die ein Regler bietet (der von Luxtronik).",
+          "heat_curve_persistent_band_k": "Die gespeicherte Einstellung wird höchstens so viele Kelvin in jede Richtung von dem Wert verschoben, den sie vor dem ersten Schreiben hatte. 3 K ist eine Schätzung zwischen einer SG-Ready-Anhebung um +1 bis +2 Stufen und der Benutzerkorrektur von ±5 K, die ein Regler bietet (der von Luxtronik).",
           "heat_curve_persistent_writes_per_day": "Schreibvorgänge an einem lokalen Tag, das Zurückschreiben beim Ausschalten eingeschlossen; einer wird dafür immer zurückgehalten. 12 (sechs Verschiebungen mit Rückkehr) liegt unter dem einzigen dokumentierten Herstellerkontingent, das gefunden wurde (Daikin, 7000 pro Jahr); der Abstand darunter ist eine Schätzung. 0 oder 1 schreibt nichts. Über 19 überschreitet dieses Kontingent.",
           "heat_curve_persistent_min_dwell_minutes": "Nach einem Schreibvorgang wartet der nächste mindestens so lange. 60 Minuten sind etwa drei Reaktionszeiten einer Heizkörperanlage (eine Schätzung aus einem Forum); eine träge Fußbodenheizung braucht eher 2 bis 3 Stunden.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
@@ -1289,7 +1289,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. Die eigene Modusauswahl der Wärmepumpe – Kühlen, Heizen, Warmwasser oder eine Kombination aus zwei. Nur lesend, außer die Steuerung der Pumpenfunktion steht auf Steuern. Eine Wärmepumpe im Kühl- oder reinen Warmwassermodus kann das Haus nicht heizen, und eine im reinen Heizmodus kann kein Warmwasser bereiten; ohne diese Angabe kann der Plan Wärme versprechen, die die Wärmepumpe gerade nicht liefern kann. Bleibt sie leer, geht der Optimierer davon aus, dass die Wärmepumpe alles kann.",
           "pump_duty_mode": "Aus (Standard) schreibt nie den Betriebsmodus oder die Sollwerte der Wärmepumpe. Beobachten schreibt ebenfalls nichts und führt in den Diagnosedaten ein 24-Stunden-Protokoll darüber, welche Funktion jeder Planschritt angefordert hat und was die Wärmepumpe getan hat (aus der Leistungsentität, dem Modus und der Speichertemperatur). Bei jeder der drei Einstellungen wird der Ein/Aus-Schalter der Wärmepumpe, falls du einen eingerichtet hast, weiterhin vom Plan geschaltet. Steuern schreibt den oben gewählten Betriebsmodus (nur Warmwasser bei reinen Warmwasserschritten, nur Heizen bei reinen Raumheizungsschritten, unverändert bei Leerlaufschritten; bei einem Schritt, der beides plant, nur Warmwasser für den Warmwasseranteil des Schritts und danach Heizen, wobei ein Anteil unter 5 Minuten der anderen Funktion zugeschlagen wird; Heizen + Warmwasser, solange ein Boost oder ein Anti-Legionellen-Zyklus beides verlangt, und immer dann, wenn der Plan nicht die Führung hat), die Entität für den Warmwasser-Sollwert (der auf der Warmwasserseite konfigurierte Warmwasser-Sollwert oder während eines Zyklus die Anti-Legionellen-Temperatur) und die Entität für den Raumheizungs-Sollwert (bei einem Vorlauf-Sollwert ein Ziel, das der geplanten Leistung folgt – die Heizungsvorlauftemperatur (55 °C, oder Obergrenze der Heizungsvorlauftemperatur) bei voller Leistung, in Richtung 5 °C (oder Mindesthub über dem Eingangswasser) über dem ersten aktuellen Wert von Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass (35 °C, wenn keiner konfiguriert ist) an der Modulationsuntergrenze – bei Schritten, die das Haus heizen, 25 °C bei Schritten, die es nicht tun (20 °C bei einem Rücklauftemperatur-Sollwert oder das eigene Minimum der Entität, falls höher), und 35 °C oder die Wetterkurve, je nachdem, was höher ist, wenn der Plan nicht die Führung hat; bei einem Raum-Sollwert die geplante Raumtemperatur). Wo der Modus keine Einzelfunktion anbietet, etwa beim GCHV-Modbus-Paket, wird stattdessen der Sollwert der anderen Funktion gesenkt: der für Warmwasser auf 30 °C, ein Vorlauf-Sollwert auf dieselben 25 °C (20 °C bei Rücklauftemperatur), ein Raum-Sollwert auf 5 °C, jeweils nie unter das eigene Minimum der Entität. Ein reiner Warmwasserabschnitt ist auf 90 Minuten begrenzt (30 unter -10 °C Außentemperatur), außer der Raum hat bereits seine geplante Temperatur. Wo Leistung begrenzt (Nachtmodus) ein Schalter ist und Ruhefenster geplant sind, hält Steuern diesen Schalter außerdem innerhalb eines Ruhefensters an und außerhalb aus. Solange Optimierer aktiv eingeschaltet ist, wird jede Änderung an diesen Entitäten, die der Optimierer nicht vorgenommen hat, sofort zurückgeschrieben; schalte Optimierer aktiv aus, um die Wärmepumpe von Hand zu ändern. Ein Wert, den die Wärmepumpe nicht übernimmt, löst eine Warnung aus und wird alle 5 Minuten erneut gesendet.",
-          "space_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe fürs Heizen als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Ihre Regelung beginnt erst zu heizen, wenn das Ziel so weit über dem Wasser liegt. Bei einem Vorlauf- oder Rücklauf-Sollwert ist die Anhebung über dem gemessenen Wasser auf der niedrigsten geplanten Stufe dann nie kleiner, sodass ein geplanter Heizschritt auch wirklich von der Pumpe gestartet wird. Eine Regelung, die nur die Startschwelle selbst veröffentlicht (bei einer Luxtronik der Bedarfsgrenzwert, Eingang 10107), braucht einen Template-Sensor aus Rücklaufziel minus dieser Schwelle. Bleibt sie leer oder unlesbar, gilt die konfigurierte Anhebung.",
+          "space_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe fürs Heizen als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Ihre Regelung beginnt erst zu heizen, wenn das Ziel so weit über dem Wasser liegt. Bei einem Vorlauf- oder Rücklauf-Sollwert ist die Anhebung über dem gemessenen Wasser auf der niedrigsten geplanten Stufe dann nie kleiner, sodass ein geplanter Heizschritt auch wirklich von der Pumpe gestartet wird. Eine Regelung, die nur die Startschwelle selbst veröffentlicht (zum Beispiel bei einer Luxtronik der Bedarfsgrenzwert, Eingang 10107), braucht einen Template-Sensor aus Rücklaufziel minus dieser Schwelle. Bleibt sie leer oder unlesbar, gilt die konfigurierte Anhebung.",
           "dhw_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe für Warmwasser als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Die Pumpe startet eine Ladung erst, wenn der Speicher unter dem Warmwasser-Sollwert minus diesem Wert liegt. Der Plan setzt dann keine Ladung auf einen wärmeren Speicher (eine für den aktuellen Schritt geplante Ladung bleibt, da sie schon laufen kann; eine Desinfektionsladung wird an der Desinfektionstemperatur gemessen), und das Funktionsprotokoll markiert einen Warmwasser-Leerlaufschritt auf so einem Speicher als not-startable statt idle-instead. Ein Warmwasser-Minimum über dieser Starttemperatur kann die Pumpe nicht halten und löst eine Warnung aus. Bleibt sie leer, unlesbar oder 0, gilt jede geplante Ladung als startend.",
           "heat_pump_defrost_entity": "Optional. Ein, solange die Wärmepumpe den Kreislauf umkehrt, um Frost vom Außenwärmetauscher zu schmelzen. Der während einer Abtauung bezogene Strom geht in den Wärmetauscher statt ins Haus. Beachte, dass viele Wärmepumpen nur alle paar Minuten abgefragt werden, kurze Abtauvorgänge also komplett übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
           "heat_pump_online_entity": "Optional und bei einer cloudverbundenen Wärmepumpe dringend empfohlen. Ein, solange die Wärmepumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre letzten bekannten Werte weiter veröffentlichen, obwohl die Wärmepumpe selbst vom Netzwerk getrennt ist, sodass alle anderen Sensoren völlig aktuell aussehen; dies ist das einzige Signal, das etwas anderes sagt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar, und dies bringt wenig.",
@@ -1422,7 +1422,7 @@
         },
         "data_description": {
           "dso_product": "Eine datierte Tabelle nur für Schweden. Die Auswahl eines Produkts schreibt Netzentgeltregeln und Felder für den Spitzentarif, die du weiterhin bearbeiten kannst, stellt das Netzentgelt auf „Zeitabhängige Regeln“ und schaltet den Spitzentarif ein. Prüfe sie anhand deiner Rechnung: Ein Produkt schreibt seine Werte auch nach seinem Enddatum weiter. Ein Produkt, das die Tabelle nicht kennt, schreibt nichts.",
-          "grid_fee_mode": "Das Entgelt, das dein Netzbetreiber pro übertragener kWh aufschlägt. Der Tibber-Preis enthält es nicht, sodass der Plan mit dieser Konfiguration endlich den gesamten Grenzpreis sieht. „Zeitabhängige Regeln“ verwendet den Zeitplan unten; „Live-Sensor“ folgt einer Entität.",
+          "grid_fee_mode": "Das Entgelt, das dein Netzbetreiber pro übertragener kWh aufschlägt. Der Tibber-Preis enthält es nicht, und ein Preissensor nur, wenn du es dort selbst eingerechnet hast, sodass der Plan mit dieser Konfiguration den gesamten Grenzpreis sieht. „Zeitabhängige Regeln“ verwendet den Zeitplan unten; „Live-Sensor“ folgt einer Entität.",
           "grid_fee_fixed": "Ein pauschales Entgelt, das in jeder Stunde zusätzlich zu den zeitabhängigen Regeln oder dem Wert des Live-Sensors aufgeschlagen wird. Es gilt nur, wenn Netzentgelt auf „Zeitabhängige Regeln“ oder „Live-Sensor“ steht; bei „Keine“ wird es ignoriert. Entnimm es deiner Netzrechnung.",
           "grid_fee_rules": "Eine Regel pro Zeile, zum Beispiel „Nov-Mar Mon-Fri 06:00-22:00 = 0.25“. Monats-, Wochentags- und Zeitteil sind jeweils optional; überlappende Regeln addieren sich, was einem Grundentgelt plus einem Hochlastzuschlag entspricht. Ein Komma zwischen Ziffern ist ein Dezimaltrenner, „0,25“ wird also als 0.25 gelesen und trennt nie eine Regel.",
           "grid_fee_entity": "Ein Sensor, der das aktuelle Entgelt in {currency}/kWh meldet, für Netze mit dynamischen Entgelten. Sein Wert wird zu jeder geplanten Stunde addiert.",
@@ -1534,7 +1534,7 @@
       },
       "modbus_prefill": {
         "title": "Aus einem Wärmepumpengerät vorbefüllen",
-        "description": "Für eine Rotenso Windmi oder eine andere von GCHV gebaute Wärmepumpe, die über das Modbus-Paket des Projekts tuya_heat_pump oder über das eigene Home-Assistant-Gerät der Pumpe ausgelesen wird. Wähle das Gerät, oder lass es leer und nenne den Entitäts-Präfix des Pakets, und sende ab: Das nächste Formular schlägt Werte vor, die aus der Pumpe gelesen wurden – die Warmwasser-Sollwerte und den Zeitplan, die Legionellentage, den Nachtmodus-Zeitplan, die maximale elektrische Leistung der Pumpe (aus ihrer Gerätekapazität), ob die Pumpe nach Wassertemperatur regelt, und die eigenen Sensoren der Pumpe für noch leere Sensorplätze. Bearbeite oder leere beliebige davon; nur was du behältst, wird gespeichert, und ein geleertes Feld bleibt, wie es war. Nichts über das Haus oder sein Heizsystem lässt sich auf diese Weise auslesen.\n\nGelesene Entitäten: {found}. Register für den Typ des Zuheizers: {backup_heater_type} – jeder Wert außer 7 bedeutet, dass die Pumpe eine eigene elektrische Heizung hat, die von den Heizer-Plätzen bei der Wärmepumpen-Telemetrie überwacht werden soll.\n\nRollen, die aus dem NAMEN einer Entität statt aus einer veröffentlichten Definition gelesen wurden – die Seite kann diese nicht prüfen, prüfe daher jede vor dem Speichern: {name_matched}. Rollen aus veröffentlichten Definitionen, nach Quelle: {matched_sources}.",
+        "description": "Liest nur, wofür diese Seite eine Zuordnung hat: eine von GCHV gebaute Wärmepumpe (zum Beispiel eine Rotenso Windmi) über das Modbus-Paket des Projekts tuya_heat_pump, oder das eigene Home-Assistant-Gerät einer Wärmepumpe, über die veröffentlichten Definitionen seiner Integration, wo hier eine zugeordnet ist, sonst über die Namen seiner Entitäten. Wähle das Gerät, oder lass es leer und nenne den Entitäts-Präfix des Pakets, und sende ab: Das nächste Formular schlägt Werte vor, die aus der Pumpe gelesen wurden – die Warmwasser-Sollwerte und den Zeitplan, die Legionellentage, den Nachtmodus-Zeitplan, die maximale elektrische Leistung der Pumpe (aus ihrer Gerätekapazität), ob die Pumpe nach Wassertemperatur regelt, und die eigenen Sensoren der Pumpe für noch leere Sensorplätze. Bearbeite oder leere beliebige davon; nur was du behältst, wird gespeichert, und ein geleertes Feld bleibt, wie es war. Nichts über das Haus oder sein Heizsystem lässt sich auf diese Weise auslesen.\n\nGelesene Entitäten: {found}. Register für den Typ des Zuheizers: {backup_heater_type} – jeder Wert außer 7 bedeutet, dass die Pumpe eine eigene elektrische Heizung hat, die von den Heizer-Plätzen bei der Wärmepumpen-Telemetrie überwacht werden soll.\n\nRollen, die aus dem NAMEN einer Entität statt aus einer veröffentlichten Definition gelesen wurden – die Seite kann diese nicht prüfen, prüfe daher jede vor dem Speichern: {name_matched}. Rollen aus veröffentlichten Definitionen, nach Quelle: {matched_sources}.",
         "data": {
           "prefill_device": "Wärmepumpen-Gerät (optional)",
           "modbus_prefill_prefix": "Entitäts-Präfix des Modbus-Pakets",
@@ -2004,10 +2004,10 @@
         "name": "Warmwassertemperatur"
       },
       "ecl110_displace": {
-        "name": "ECL110 Parallelverschiebung"
+        "name": "Heizkurven-Parallelverschiebung"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 Effektive Parallelverschiebung"
+        "name": "Heizkurven-Parallelverschiebung effektiv"
       },
       "floor_heating_return_temperature": {
         "name": "Rücklauftemperatur Fußbodenheizung"
@@ -2404,15 +2404,15 @@
           "description": "Multiplikator des Wärmeverlusts bei Regen. 1,15 bedeutet 15 % mehr Wärmeverlust bei Regen ab 2 mm/h (Effekt der nassen Gebäudehülle); schwächerer Regen verringert ihn anteilig, bei 0,1 mm/h oder weniger wirkt er gar nicht."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID-Zeitkonstante",
-          "description": "Zeitkonstante (Stunden) für die Näherung des PI/PID-Verhaltens des ECL110. Niedrigere Werte reagieren schneller, höhere sind gleichmäßiger."
+          "name": "PI/PID-Zeitkonstante des Heizkurvenreglers",
+          "description": "Zeitkonstante (Stunden) für die Näherung des PI/PID-Verhaltens des Heizkurvenreglers. Niedrigere Werte reagieren schneller, höhere sind gleichmäßiger."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 Verschiebung Minimum",
+          "name": "Heizkurvenverschiebung Minimum",
           "description": "Niedrigste Parallelverschiebung, die der Optimierer vorgeben darf, in °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 Verschiebung Maximum",
+          "name": "Heizkurvenverschiebung Maximum",
           "description": "Höchste Parallelverschiebung, die der Optimierer vorgeben darf, in °C."
         },
         "quiet_silent_windows": {
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 3eeedb705a..ba11b0cf09 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -594,12 +594,12 @@
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
               "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (a Luxtronik through its Smart Home Interface, for example, is assumed to be one); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target. A space boost or Boost mode writes the set-point entity's own maximum (up to 70 °C) on every step instead; a value other than 55 °C set here caps that too, so set one on a low-temperature floor heating.",
-              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
-              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
-              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
+              "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (0.5 K on a Luxtronik, for example), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a controller can drop what was set when it goes unread (a Luxtronik Smart Home Interface, for one, drops every set value after 600 s without access); and no second tool writing the same registers (a Luxtronik, for one, then silently discards writes).",
+              "space_setpoint_low_limit_entity": "Optional. A temperature sensor that reports the lowest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return target minimum\", input 10104). With it, Follow the planned power never sends a value below it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes.",
+              "space_setpoint_high_limit_entity": "Optional. A temperature sensor that reports the highest value the controller accepts for the set-point entity above (for example a Luxtronik through ha-luxtronik-shi: \"Temperature: return limit\", input 10103). With it, Follow the planned power never sends a value above it, instead of finding the limit when the controller cuts a write. Used by that option alone; left empty, nothing changes."
             }
           },
           "plant": {
@@ -942,7 +942,7 @@
       },
       "heat_curve": {
         "title": "Heat curve control",
-        "description": "Shifts the heat curve up in cheap hours and down in expensive ones, through a Danfoss ECL110 over MQTT, a number entity that offsets your controller's curve, or both. Leave the topics and the entity empty if you have neither.",
+        "description": "Shifts your controller's heat curve up in cheap hours and down in expensive ones, three ways: over MQTT topics, to a controller that takes its offset there (a Danfoss ECL110 through an MQTT bridge, for example); to a number entity that offsets the curve; or to a curve setting the controller stores. The topics and the entity can be used together. Leave them all empty if your controller has none of these.",
         "data": {
           "ecl110_displace_set_topic": "Offset command topic",
           "ecl110_command_topic": "Legacy JSON command topic",
@@ -961,7 +961,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if you do not have a Danfoss ECL110.",
+          "ecl110_displace_set_topic": "MQTT topic the parallel heat-curve offset is published to. Nothing is published while this and the legacy command topic below are empty: leave them empty if your controller does not take its offset over MQTT (a Danfoss ECL110 through an MQTT bridge is one that does).",
           "ecl110_command_topic": "Only needed for older setups that expect a JSON payload instead.",
           "ecl110_state_topic": "MQTT topic the controller reports its current state on.",
           "ecl110_mqtt_qos": "0 is fine for almost everyone.",
@@ -971,8 +971,8 @@
           "ecl110_pid_time_constant_hours": "Roughly how long the controller takes to act on a new offset. Used so the optimizer does not ask for changes faster than the system can follow.",
           "heat_curve_displace_entity": "A number entity that shifts your controller's heat curve. Kind offset: a whole-curve offset, 0 meaning no shift, that the controller forgets on a restart (for example a Luxtronik SHI heating offset); turning the optimizer off, or unloading it, writes 0. Kind persistent: a curve setting the controller stores; turning the optimizer off, or unloading it, writes back the value it held before the first write.",
           "heat_curve_target_kind": "Offset: a temperature difference, 0 neutral, not stored by the controller. Prefer it wherever your controller has one. Persistent: a curve setting the controller stores, displaced from its own value and written back on off; every write wears the controller's memory, so writes are limited per day.",
-          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
-          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and Luxtronik's own ±5 K correction.",
+          "heat_curve_offset_band_k": "The offset written to the entity stays within this many kelvin either way. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
+          "heat_curve_persistent_band_k": "The stored setting is moved at most this many kelvin either way from the value it held before the first write. 3 K is an estimate between a +1 to +2 step SG-Ready boost and the ±5 K user correction one controller offers (Luxtronik's).",
           "heat_curve_persistent_writes_per_day": "Writes in one local day, the write back on off included; one is always kept for it. 12 (six shift-and-return episodes) stays under the one documented manufacturer quota found (Daikin, 7000 a year); the margin below it is an estimate. 0 or 1 writes nothing. Above 19 exceeds that quota.",
           "heat_curve_persistent_min_dwell_minutes": "After a write, the next waits at least this long. 60 minutes is about three response times of a radiator system (a forum estimate); a slow floor may want 2 to 3 hours.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
@@ -1289,7 +1289,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "pump_duty_mode": "Off (the default) never writes the pump's operating mode or set-points. Observe writes none either and keeps a 24-hour ledger, in the diagnostics, of the duty each plan step asked for against what the pump did (from the power entity, the mode and the tank temperature). With any of the three, the heat pump on/off switch, if you have set one, is still switched by the plan. Control writes the operating mode above (hot water only on hot-water-only steps, heating only on space-heating-only steps, unchanged on idle steps; on a step that plans both, hot water only for the hot-water share of the step and then heating, a share under 5 minutes going to the other duty; Heating + DHW while a boost or an anti-legionella cycle calls for both, and whenever the plan is not in charge), the hot water set-point entity (the hot water set-point configured on the hot water page, or the anti-legionella temperature during a cycle) and the space set-point entity (for a flow set-point, a target that follows the planned power — the heating flow (55 °C, or the Heating flow ceiling) at full power, toward 5 °C (or the Minimum lift above the inlet water) above the first fresh reading of the heat-pump return, buffer tank, floor return or valve outlet (35 °C when none is configured) at the modulation floor — on steps that heat the house, 25 °C on steps that do not (20 °C for a Return temperature set-point, or the entity's own minimum if that is higher), and 35 °C or the weather curve, whichever is higher, when the plan is not in charge; for an indoor one, the planned room temperature). Where the mode offers no single-duty option, as on the GCHV Modbus package, the other duty's set-point is lowered instead: the hot water one to 30 °C, a flow set-point to the same 25 °C (20 °C for Return temperature), an indoor one to 5 °C, each never below the entity's own minimum. A hot-water-only stretch is capped at 90 minutes (30 below -10 °C outdoors), unless the room is already at its planned temperature. Where Capacity limited (night mode) is a switch and silent windows are scheduled, Control also holds that switch on inside a silent window and off outside one. While Optimizer active is on, any change to those entities the optimizer did not make is written back at once; turn Optimizer active off to change the pump by hand. A value the pump does not hold raises a warning and is sent again every 5 minutes.",
-          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
+          "space_hysteresis_entity": "Optional. A sensor or number holding the pump's own heating start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): its controller starts heating only once the target sits that far above the water. On a flow or return set-point the lift written above the measured water at the lowest planned level is then never smaller than it, so a planned heating step is one the pump starts. A controller that publishes only the start threshold itself (a Luxtronik's Demand border, input 10107, for example) needs a template sensor of the return target minus that threshold. Left empty or unreadable, the configured lift stands.",
           "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
@@ -1422,7 +1422,7 @@
         },
         "data_description": {
           "dso_product": "A dated Sweden-only table. Selecting a product writes transfer-fee rules and peak-tariff fields you can still edit, switches the transfer fee to Time-of-use rules and turns the peak tariff on. Verify against your bill: a product keeps writing its values after its end date. A product the table does not know writes nothing.",
-          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, so with it configured the plan finally sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
+          "grid_fee_mode": "The fee your grid company adds per kWh transferred. Tibber's price does not include it, and a price sensor includes it only if you added it there yourself, so with it configured the plan sees the whole marginal price. \"Time-of-use rules\" uses the schedule below; \"Live sensor\" follows an entity.",
           "grid_fee_fixed": "A flat fee added in every hour, on top of the time-of-use rules or the live sensor's value. It only applies when Grid transfer fee is Time-of-use rules or Live sensor; with None it is ignored. Take it from your grid invoice.",
           "grid_fee_rules": "One rule per line, for example \"Nov-Mar Mon-Fri 06:00-22:00 = 0.25\". Month, weekday and time parts are each optional; overlapping rules add together, which matches a base fee plus a high-load surcharge. A comma between digits is a decimal separator, so \"0,25\" reads as 0.25 and never splits a rule.",
           "grid_fee_entity": "A sensor reporting the current fee in {currency}/kWh, for grids with dynamic fees. Its value is added to every planned hour.",
@@ -1534,7 +1534,7 @@
       },
       "modbus_prefill": {
         "title": "Pre-fill from a heat pump device",
-        "description": "For a Rotenso Windmi or another GCHV-built heat pump, read through the tuya_heat_pump project's Modbus package or through the pump's own Home Assistant device. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
+        "description": "Reads only what this page has a mapping for: a GCHV-built heat pump (a Rotenso Windmi, for example) through the tuya_heat_pump project's Modbus package, or a heat pump's own Home Assistant device, through its integration's published definitions where one is mapped here and otherwise by its entities' names. Pick the device, or leave it empty and name the package's entity prefix, and submit: the next form suggests values read from the pump - the hot water set-points and schedule, the anti-legionella days, the night mode schedule, the pump's maximum electrical power (from its unit capacity), whether the pump steers on water temperature, and the pump's own sensors for sensor slots that are still empty. Edit or clear any of them; only what you keep is saved, and a field you clear is left as it was. Nothing about the house or its heating system can be read this way.\n\nEntities read: {found}. Backup heater type register: {backup_heater_type} - any value but 7 means the pump has electric heat of its own, which the heater slots on Heat pump telemetry are there to watch.\n\nRoles read from an entity's NAME rather than from a published definition - the page cannot verify those, so check each before saving: {name_matched}. Roles read from published definitions, by source: {matched_sources}.",
         "data": {
           "prefill_device": "Heat pump device (optional)",
           "modbus_prefill_prefix": "Modbus package entity prefix",
@@ -2004,10 +2004,10 @@
         "name": "DHW Temperature"
       },
       "ecl110_displace": {
-        "name": "ECL110 Displace"
+        "name": "Heat-Curve Displace"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 Effective Displace"
+        "name": "Heat-Curve Effective Displace"
       },
       "floor_heating_return_temperature": {
         "name": "Floor Heating Return Temperature"
@@ -2096,7 +2096,7 @@
           "dhw_window": "Heating hot water inside a hot water window",
           "idle": "Idle",
           "idle_coasting": "Above the floor, coasting",
-          "idle_dearer": "Dearer than the hours used",
+          "idle_dearer": "More expensive than the hours used",
           "idle_fuse": "Capped by the fuse",
           "idle_other_channel": "The other channel has the capacity",
           "idle_solar": "Waiting for solar",
@@ -2404,15 +2404,15 @@
           "description": "Heat loss multiplier when raining. 1.15 means 15% more heat loss in rain of 2 mm/h or more (wet building envelope effect); lighter rain scales it down in proportion, and 0.1 mm/h or less applies none of it."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID Time Constant",
-          "description": "Time constant (hours) for the ECL110 PI/PID response approximation. Lower values react faster, higher values are smoother."
+          "name": "Heat-Curve Controller Time Constant",
+          "description": "Time constant (hours) for the heat-curve controller's PI/PID response approximation. Lower values react faster, higher values are smoother."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 displace minimum",
+          "name": "Heat-curve displace minimum",
           "description": "Lowest parallel shift the optimizer may command, in °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 displace maximum",
+          "name": "Heat-curve displace maximum",
           "description": "Highest parallel shift the optimizer may command, in °C."
         },
         "quiet_silent_windows": {
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 1e849c6cbc..902571777f 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -594,12 +594,12 @@
               "indoor_temp_entity": "Valfritt. Den verkliga rumstemperaturen. Utan den litar optimeringen på sin egen modell, som glider med tiden.",
               "outdoor_temp_entity": "Valfritt. En egen utegivare är mer exakt än prognosen för den aktuella timmen.",
               "space_setpoint_entity": "Valfritt. En number-, helper- eller climate-enhet som är pumpens börvärde för rumsuppvärmning. Med Styrning av pumpens uppgift satt till Styrning skriver optimeraren det vid varje plansteg, som Styrning av pumpens uppgift beskriver, och när Optimeraren aktiv stängs av skrivs värdet tillbaka som enheten visade före den första skrivningen. Med Av eller Observera läses det bara, för att märka när det inte går att läsa.",
-              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsentitet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: optimeraren härleder den aldrig från entiteten, och bara förifyllningen från en värmepumpsenhet föreslår en. Med Styrning av pumpens uppgift på Styrning skriver optimeraren planens rumstemperatur (Inomhustemperatur) eller vattentemperatur (Framledningstemperatur, Returtemperatur) till den här entiteten.",
+              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget till exempel för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsentitet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: optimeraren härleder den aldrig från entiteten, och bara förifyllningen från en värmepumpsenhet föreslår en. Med Styrning av pumpens uppgift på Styrning skriver optimeraren planens rumstemperatur (Inomhustemperatur) eller vattentemperatur (Framledningstemperatur, Returtemperatur) till den här entiteten.",
               "flow_min_lift_k": "Med Styrning av pumpens uppgift på Styrning skrivs vattenbörvärdet vid planens lägsta effekt som det uppmätta inkommande vattnet plus detta: värmepumpens retur, bufferttank, golvretur eller ventilens utlopp, och för en entitet med Returtemperatur bara de tre första. 5 K passar en styrenhet som håller sin framledning på börvärdet. En styrenhet som tar börvärdet som mål för returvattnet antas köra kompressorn hårdare ju högre målet ligger över returen och vill troligen ha mindre; 1–2 K är en startpunkt att kontrollera mot kompressorns uppmätta frekvens och effekt, inte ett uppmätt värde.",
               "flow_heat_c": "Vattenbörvärdet som skrivs vid full planerad effekt, och det högsta som skrivs medan planen styr. 55 °C passar ett framledningsmål. För en entitet med Returtemperatur väljs det över den högsta retur du ser vid normal uppvärmning plus höjningen, och inte högre än styrenheten accepterar; för en lågtemperatur-golvvärme kan 35–40 °C vara en startpunkt att kontrollera mot mätningar. Under 30 °C erbjuds inte: grinden som betyder av är 25 °C för ett framledningsmål och 20 °C för ett returmål. En rumsvärmeboost eller Boost-läget skriver i stället börvärdesentitetens eget maximum (högst 70 °C) vid varje steg; ett annat värde än 55 °C här begränsar även det, så ange ett för en lågtemperatur-golvvärme.",
-              "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (Luxtronik: 0,5 K), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom ett Luxtronik Smart Home Interface släpper alla satta värden efter 600 s utan åtkomst; och inget annat verktyg skriver samma register (en Luxtronik kastar då skrivningar tyst).",
-              "space_setpoint_low_limit_entity": "Valfri. En temperaturgivare som rapporterar det lägsta värde styrenheten tar emot för börvärdesentiteten ovan (en Luxtronik via ha-luxtronik-shi: \"Temperature: return target minimum\", ingång 10104). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde under det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting.",
-              "space_setpoint_high_limit_entity": "Valfri. En temperaturgivare som rapporterar det högsta värde styrenheten tar emot för börvärdesentiteten ovan (en Luxtronik via ha-luxtronik-shi: \"Temperature: return limit\", ingång 10103). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde över det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting."
+              "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (0,5 K på till exempel en Luxtronik), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom en styrenhet kan släppa det som satts när den inte läses (ett Luxtronik Smart Home Interface till exempel släpper alla satta värden efter 600 s utan åtkomst); och inget annat verktyg skriver samma register (en Luxtronik till exempel kastar då skrivningar tyst).",
+              "space_setpoint_low_limit_entity": "Valfri. En temperaturgivare som rapporterar det lägsta värde styrenheten tar emot för börvärdesentiteten ovan (till exempel en Luxtronik via ha-luxtronik-shi: \"Temperature: return target minimum\", ingång 10104). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde under det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting.",
+              "space_setpoint_high_limit_entity": "Valfri. En temperaturgivare som rapporterar det högsta värde styrenheten tar emot för börvärdesentiteten ovan (till exempel en Luxtronik via ha-luxtronik-shi: \"Temperature: return limit\", ingång 10103). Med den skickar Följ planerad effekt efter uppmätt förbrukning aldrig ett värde över det, i stället för att hitta gränsen först när styrenheten kapar en skrivning. Används bara av det alternativet; lämnas den tom ändras ingenting."
             }
           },
           "plant": {
@@ -942,7 +942,7 @@
       },
       "heat_curve": {
         "title": "Värmekurvestyrning",
-        "description": "Förskjuter värmekurvan uppåt under billiga timmar och nedåt under dyra, via en Danfoss ECL110 över MQTT, en nummerentitet som förskjuter styrningens kurva, eller båda. Lämna ämnena och entiteten tomma om du inte har någon av dem.",
+        "description": "Förskjuter styrningens värmekurva uppåt under billiga timmar och nedåt under dyra, på tre sätt: via MQTT-topics till en styrning som tar emot sin förskjutning där (till exempel en Danfoss ECL110 via en MQTT-brygga); till en nummerentitet som förskjuter kurvan; eller till en kurvinställning som styrningen lagrar. Topics och entitet kan användas tillsammans. Lämna allt tomt om styrningen inte har något av detta.",
         "data": {
           "ecl110_displace_set_topic": "Topic för förskjutningskommando",
           "ecl110_command_topic": "Äldre JSON-kommandotopic",
@@ -961,7 +961,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "ecl110_displace_set_topic": "MQTT-topic dit parallellförskjutningen av värmekurvan publiceras. Inget publiceras så länge detta fält och den äldre kommandotopicen nedan är tomma: lämna dem tomma om du inte har en Danfoss ECL110.",
+          "ecl110_displace_set_topic": "MQTT-topic dit parallellförskjutningen av värmekurvan publiceras. Inget publiceras så länge detta fält och den äldre kommandotopicen nedan är tomma: lämna dem tomma om styrningen inte tar emot sin förskjutning över MQTT (en Danfoss ECL110 via en MQTT-brygga gör det).",
           "ecl110_command_topic": "Behövs bara för äldre installationer som förväntar sig JSON i stället.",
           "ecl110_state_topic": "MQTT-topic där regulatorn rapporterar sitt tillstånd.",
           "ecl110_mqtt_qos": "0 räcker för de allra flesta.",
@@ -971,8 +971,8 @@
           "ecl110_pid_time_constant_hours": "Ungefär hur lång tid regulatorn behöver för att verkställa en ny förskjutning. Används så att optimeringen inte begär snabbare ändringar än systemet hinner följa.",
           "heat_curve_displace_entity": "En nummerentitet som förskjuter styrningens värmekurva. Typen förskjutning: en förskjutning av hela kurvan, där 0 betyder ingen förskjutning, som styrningen glömmer vid en omstart (till exempel en Luxtronik SHI-värmeförskjutning); när optimeraren stängs av eller avlastas skrivs 0. Typen beständig: en kurvinställning som styrningen lagrar; när optimeraren stängs av eller avlastas skrivs värdet tillbaka som den hade före den första skrivningen.",
           "heat_curve_target_kind": "Förskjutning: en temperaturskillnad, 0 neutral, lagras inte av styrningen. Välj den där styrningen har en. Beständig: en kurvinställning som styrningen lagrar, förskjuten från sitt eget värde och återställd vid avstängning; varje skrivning sliter på styrningens minne, så skrivningarna begränsas per dygn.",
-          "heat_curve_offset_band_k": "Förskjutningen som skrivs till entiteten håller sig inom så här många kelvin åt båda hållen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och Luxtronik egen korrigering på ±5 K.",
-          "heat_curve_persistent_band_k": "Den lagrade inställningen flyttas högst så här många kelvin åt båda hållen från värdet den hade före den första skrivningen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och Luxtronik egen korrigering på ±5 K.",
+          "heat_curve_offset_band_k": "Förskjutningen som skrivs till entiteten håller sig inom så här många kelvin åt båda hållen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och den användarkorrigering på ±5 K som en styrning erbjuder (Luxtroniks).",
+          "heat_curve_persistent_band_k": "Den lagrade inställningen flyttas högst så här många kelvin åt båda hållen från värdet den hade före den första skrivningen. 3 K är en uppskattning mellan en SG-Ready-höjning på +1 till +2 steg och den användarkorrigering på ±5 K som en styrning erbjuder (Luxtroniks).",
           "heat_curve_persistent_writes_per_day": "Skrivningar under ett lokalt dygn, återställningen vid avstängning inräknad; en hålls alltid kvar för den. 12 (sex förskjutningar med återgång) ligger under den enda dokumenterade tillverkarkvot som hittats (Daikin, 7000 per år); marginalen under den är en uppskattning. 0 eller 1 skriver ingenting. Över 19 överskrider kvoten.",
           "heat_curve_persistent_min_dwell_minutes": "Efter en skrivning väntar nästa minst så här länge. 60 minuter är ungefär tre svarstider för ett radiatorsystem (en uppskattning från ett forum); ett trögt golv kan behöva 2 till 3 timmar.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
@@ -1289,7 +1289,7 @@
         "data_description": {
           "heat_pump_mode_entity": "Valfritt. Pumpens eget lägesval - kyla, värme, varmvatten eller en kombination av två. Läses bara av, om inte Styrning av pumpens uppgift står på Styrning. En pump som står i kylläge eller enbart varmvatten kan inte värma huset, och en som står i enbart värmeläge kan inte göra varmvatten. Utan det här kan planen alltså lova värme som pumpen just då inte kan leverera. Lämnas fältet tomt antar optimeringen att pumpen klarar allt.",
           "pump_duty_mode": "Av (standard) skriver aldrig pumpens driftläge eller börvärden. Observera skriver inte heller något och för en 24-timmarslogg, i diagnostiken, över vilken uppgift varje planerat steg bad om och vad pumpen gjorde (från effektentiteten, driftläget och tanktemperaturen). Med något av de tre styrs strömbrytaren för värmepumpen, om du har ställt in en, ändå av planen. Styrning skriver driftläget ovan (bara varmvatten på steg med bara varmvatten, bara värme på steg med bara rumsvärme, oförändrat på vilande steg; på ett steg som planerar båda bara varmvatten under stegets varmvattendel och sedan värme, där en andel under 5 minuter går till den andra uppgiften; Värme + varmvatten medan en boost eller en legionellacykel kräver båda, och närhelst planen inte styr), varmvattnets börvärdesentitet (varmvattnets börvärde från varmvattensidan, eller legionellatemperaturen under en cykel) och rumsvärmens börvärdesentitet (för ett framledningsbörvärde ett mål som följer den planerade effekten — värmeframledningen (55 °C, eller Högsta framledning vid värme) vid full effekt, mot 5 °C (eller Minsta höjning över inkommande vatten) över den första färska avläsningen av värmepumpens retur, ackumulatortanken, golvreturen eller ventilens utlopp (35 °C när ingen är inställd) vid moduleringsgolvet — på steg som värmer huset, 25 °C på steg som inte gör det (20 °C för ett Returtemperatur-börvärde, eller entitetens eget minimum om det är högre), och 35 °C eller värmekurvan, det som är högst, när planen inte styr; för ett inomhusbörvärde den planerade rumstemperaturen). Där driftläget saknar ett läge för bara en uppgift, som i GCHV Modbus-paketet, sänks i stället den andra uppgiftens börvärde: varmvattnets till 30 °C, ett framledningsbörvärde till samma 25 °C (20 °C för Returtemperatur), ett inomhusbörvärde till 5 °C, aldrig under entitetens eget minimum. En sträcka med bara varmvatten begränsas till 90 minuter (30 under -10 °C ute), om inte rummet redan har sin planerade temperatur. Där Begränsad effekt (nattläge) är en brytare och tysta tidsfönster är schemalagda håller Styrning också den brytaren på inom ett tyst fönster och av utanför ett. Medan Optimeraren aktiv är på skrivs varje ändring av entiteterna som optimeraren inte gjorde tillbaka direkt; stäng av Optimeraren aktiv för att ändra pumpen för hand. Ett värde som pumpen inte behåller ger en varning och skickas igen var 5:e minut.",
-          "space_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för uppvärmning som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): dess styrning börjar värma först när målet ligger så mycket över vattnet. För ett framlednings- eller returbörvärde blir lyftet över det uppmätta vattnet på den lägsta planerade nivån då aldrig mindre, så ett planerat värmesteg är ett som pumpen startar. En styrning som bara publicerar själva startgränsen (en Luxtroniks Demand border, ingång 10107) behöver en mallsensor av returmålet minus den gränsen. Lämnas fältet tomt eller oläsbart gäller det konfigurerade lyftet.",
+          "space_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för uppvärmning som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): dess styrning börjar värma först när målet ligger så mycket över vattnet. För ett framlednings- eller returbörvärde blir lyftet över det uppmätta vattnet på den lägsta planerade nivån då aldrig mindre, så ett planerat värmesteg är ett som pumpen startar. En styrning som bara publicerar själva startgränsen (till exempel en Luxtroniks Demand border, ingång 10107) behöver en mallsensor av returmålet minus den gränsen. Lämnas fältet tomt eller oläsbart gäller det konfigurerade lyftet.",
           "dhw_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för varmvatten som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): pumpen startar en laddning först när tanken ligger under varmvattenbörvärdet minus detta. Planen lägger då ingen laddning på en varmare tank (en laddning som planerats för det aktuella steget behålls, eftersom den kan redan pågå; en desinfektionsladdning bedöms mot desinfektionstemperaturen), och pumploggen märker ett vilande varmvattensteg på en sådan tank not-startable i stället för idle-instead. Ett varmvattenminimum över den starttemperaturen kan pumpen inte hålla och ger en varning. Lämnas fältet tomt, oläsbart eller 0 antas varje planerad laddning starta.",
           "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
           "heat_pump_online_entity": "Valfritt, men varmt rekommenderat för en molnansluten pump. På medan pumpen faktiskt går att nå. En molnintegration kan fortsätta publicera sina senast kända värden medan pumpen själv har tappat nätverket, vilket får alla andra givare att se alldeles färska ut. Det här är den enda signal som avslöjar det. Vid lokal anslutning (LAN) blir givarna otillgängliga av sig själva och fältet tillför då lite.",
@@ -1421,7 +1421,7 @@
           "dso_product": "Svensk nättariff (skriver fälten nedan)"
         },
         "data_description": {
-          "grid_fee_mode": "Avgiften ditt elnätsbolag lägger på varje överförd kWh. Tibbers pris innehåller den inte, så med den inställd ser planen äntligen hela marginalpriset. \"Tidsregler\" använder schemat nedan; \"Sensor\" följer en entitet.",
+          "grid_fee_mode": "Avgiften ditt elnätsbolag lägger på varje överförd kWh. Tibbers pris innehåller den inte, och en prissensor bara om du själv lagt in den där, så med den inställd ser planen hela marginalpriset. \"Tidsregler\" använder schemat nedan; \"Sensor\" följer en entitet.",
           "grid_fee_fixed": "En fast avgift som läggs på varje timme, utöver tidsreglerna eller livesensorns värde. Den gäller bara när Elnätets överföringsavgift är Tidsregler eller Sensor; med Ingen ignoreras den. Ta den från din elnätsfaktura.",
           "grid_fee_rules": "En regel per rad, till exempel \"Nov-Mar Mån-Fre 06:00-22:00 = 0.25\". Månads-, veckodags- och tidsdelarna är valfria var för sig; överlappande regler adderas, vilket motsvarar grundavgift plus höglastpåslag. Ett komma mellan siffror är en decimalseparator, så \"0,25\" läses som 0,25 och delar aldrig en regel.",
           "grid_fee_entity": "En sensor som anger aktuell avgift i {currency}/kWh, för nät med dynamiska avgifter. Värdet läggs på varje planerad timme.",
@@ -1534,7 +1534,7 @@
       },
       "modbus_prefill": {
         "title": "Förifyll från en värmepumpsenhet",
-        "description": "För en Rotenso Windmi eller en annan GCHV-byggd värmepump, som läses via tuya_heat_pump-projektets Modbus-paket eller via pumpens egen Home Assistant-enhet. Välj enheten, eller lämna tomt och ange paketets entitetsprefix, och skicka: nästa formulär föreslår värden som lästs från pumpen - varmvattnets börvärden och schema, dagarna för legionellaskydd, nattlägets schema, pumpens maximala eleffekt (ur dess enhetskapacitet), om pumpen styr på vattentemperatur, och pumpens egna givare för givarfält som fortfarande är tomma. Ändra eller töm vilket som helst av dem; bara det du behåller sparas, och ett fält du tömmer lämnas som det var. Inget om huset eller dess värmesystem går att läsa ut på det här sättet.\n\nLästa entiteter: {found}. Registret för tillsatsvärmens typ: {backup_heater_type} - allt utom 7 betyder att pumpen har egen elvärme, och det är den som elpatronfälten under Värmepumps telemetri finns till för att bevaka.\n\nRoller lästa ur en entitets NAMN i stället för ur en publicerad definition - sidan kan inte verifiera dem, så kontrollera var och en innan du sparar: {name_matched}. Roller lästa ur publicerade definitioner, per källa: {matched_sources}.",
+        "description": "Läser bara det som sidan har en mappning för: en GCHV-byggd värmepump (till exempel en Rotenso Windmi) via tuya_heat_pump-projektets Modbus-paket, eller en värmepumps egen Home Assistant-enhet, via dess integrations publicerade definitioner där en är mappad här och annars via entiteternas namn. Välj enheten, eller lämna tomt och ange paketets entitetsprefix, och skicka: nästa formulär föreslår värden som lästs från pumpen - varmvattnets börvärden och schema, dagarna för legionellaskydd, nattlägets schema, pumpens maximala eleffekt (ur dess enhetskapacitet), om pumpen styr på vattentemperatur, och pumpens egna givare för givarfält som fortfarande är tomma. Ändra eller töm vilket som helst av dem; bara det du behåller sparas, och ett fält du tömmer lämnas som det var. Inget om huset eller dess värmesystem går att läsa ut på det här sättet.\n\nLästa entiteter: {found}. Registret för tillsatsvärmens typ: {backup_heater_type} - allt utom 7 betyder att pumpen har egen elvärme, och det är den som elpatronfälten under Värmepumps telemetri finns till för att bevaka.\n\nRoller lästa ur en entitets NAMN i stället för ur en publicerad definition - sidan kan inte verifiera dem, så kontrollera var och en innan du sparar: {name_matched}. Roller lästa ur publicerade definitioner, per källa: {matched_sources}.",
         "data": {
           "prefill_device": "Värmepumpens enhet (valfritt)",
           "modbus_prefill_prefix": "Modbus-paketets entitetsprefix",
@@ -2004,10 +2004,10 @@
         "name": "Varmvattentemperatur"
       },
       "ecl110_displace": {
-        "name": "ECL110-förskjutning"
+        "name": "Värmekurvans förskjutning"
       },
       "ecl110_effective_displace": {
-        "name": "ECL110 effektiv förskjutning"
+        "name": "Värmekurvans effektiva förskjutning"
       },
       "floor_heating_return_temperature": {
         "name": "Golvvärmens returtemperatur"
@@ -2404,15 +2404,15 @@
           "description": "Multiplikator för värmeförlusten när det regnar. 1,15 betyder 15 % större värmeförlust vid regn på 2 mm/h eller mer (effekten av ett blött klimatskal); lättare regn skalar ned den i proportion, och vid 0,1 mm/h eller mindre tillämpas den inte alls."
         },
         "ecl110_pid_time_constant_hours": {
-          "name": "ECL110 PI/PID-tidskonstant",
-          "description": "Tidskonstant (timmar) för approximationen av ECL110:s PI/PID-svar. Lägre värden reagerar snabbare, högre värden ger jämnare gång."
+          "name": "Värmekurvestyrningens PI/PID-tidskonstant",
+          "description": "Tidskonstant (timmar) för approximationen av värmekurvestyrningens PI/PID-svar. Lägre värden reagerar snabbare, högre värden ger jämnare gång."
         },
         "ecl110_displace_min": {
-          "name": "ECL110 minsta parallellförskjutning",
+          "name": "Värmekurvans minsta parallellförskjutning",
           "description": "Den lägsta parallellförskjutning optimeringen får begära, i °C."
         },
         "ecl110_displace_max": {
-          "name": "ECL110 största parallellförskjutning",
+          "name": "Värmekurvans största parallellförskjutning",
           "description": "Den högsta parallellförskjutning optimeringen får begära, i °C."
         },
         "quiet_silent_windows": {
diff --git a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
index 266683d025..fcd21e3a39 100644
--- a/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
+++ b/custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
@@ -483,10 +483,10 @@ const STRINGS = {
     "why.sub_other": "the other channel has the capacity",
     "why.sub_fuse": "the fuse limit caps heating",
     "why.sub_solar": "the plan is waiting for solar",
-    "why.sub_dearer": "this hour is dearer than the hours the plan uses",
+    "why.sub_dearer": "this hour is pricier than the hours the plan uses",
     "why.sub_coasting": "the temperature is above the floor, so the plan is coasting",
     "why.price_rank":
-      "{price} {unit} is among the dearest {pct} % of the plan " +
+      "{price} {unit} is among the most expensive {pct} % of the plan " +
       "(cheapest {min})",
     "why.coast_space": "the house is coasting on heat stored {from}\u2013{to}",
     "why.coast_dhw": "the tank was heated {from}\u2013{to}",
@@ -629,7 +629,7 @@ const STRINGS = {
     // cost delta row
     "stats.no_plan_to_compare": "No plan data to compare against yet.",
     "stats.cheaper": "cheaper",
-    "stats.dearer": "dearer",
+    "stats.dearer": "pricier",
     "stats.the_same": "the same",
     "stats.delta_detail":
       "{verdict} than the saved plan ({planned} → {edited}&nbsp;{currency}, " +
@@ -919,7 +919,7 @@ const STRINGS = {
     "whynow.weight": "{sign}{w}%",
     "whynow.driver_price_rank": "Price rank",
     "whynow.explain_price_rank":
-      "How cheap this slot is against the rest of the plan: the cheapest slot pushes fully toward running, the dearest toward idle.",
+      "How cheap this slot is against the rest of the plan: the cheapest slot pushes fully toward running, the most expensive toward idle.",
     "whynow.driver_comfort_floor": "Comfort floor",
     "whynow.explain_comfort_floor":
       "How far the room is from the middle of its comfort band, above the comfort floor: below the middle pushes toward running, above it toward idle.",
diff --git a/dev/audit/README.md b/dev/audit/README.md
index d33fd2d49b..5f902ff344 100644
--- a/dev/audit/README.md
+++ b/dev/audit/README.md
@@ -29,7 +29,7 @@ or removed one goes red. Decision 0016 ties a round to its major version.
 | 1 mandate and rulings | the prior round's final state comment on #201 | the owner's mandate comment, scope and expiry, and rulings on #201 | `tools/policy/budget_raise_gate.py` reads a mandate's state | `dev/governance/decisions/0013-verdicts-post-as-the-approver-app.md`, `CLAUDE.md` | the mandate comment id |
 | 2 dimensions and finders | a baseline SHA pinned after `evaluator.md`'s evaluation | every scope reported | `.claude/workflows/audit-find.js`, `tools/audit/check_scopes.py` over `dev/audit/config/scopes.json` | `dev/governance/roles/COMMON.md`, `dev/governance/dimensions/` | reports under `dev/audit/rounds/` |
 | 3 verify and judge | the finders' reports | every finding judged, classes swept | `.claude/workflows/audit-verify.js` | `verifier.md`, `judge.md`, `dev/governance/rules/defect-root-cause.md` | the round's judge record, `dev/audit/config/bugclasses.json` |
-| 4 P3 plan and owner approval | the judged register | `Plan review: approve`, then the owner's approval | `.claude/workflows/audit-plan.js`, `tools/audit/archscore/`, `tools/audit/seat/plan_audit.py` | `architect-planner.md`, `plan-review.md`, decision 0015 | the plan branch, ADRs |
+| 4 P3 plan and owner approval | the judged register | `Plan review: approve`, then the owner's approval | `.claude/workflows/audit-plan.js`, `tools/audit/archscore/`, `tools/audit/seat/plan_audit.py` | `architect-planner.md`, `plan-review.md`, decisions 0015 and 0018 | the plan branch, ADRs, the projection record |
 | 5 roster and waves | the approved plan | the roster lints clean | `tools/audit/seat/roster_edit.py`, `tools/policy/brief_lint.mjs` | `standing-roster.md`, `dev/governance/rules/brief-citations.md` | `dev/programme/rosters/`, `critical-path.json` |
 | 6 dispatch under the lane caps | after-edges merged; the roster stage compared with the merged pull requests naming the group, so only arms not on main are briefed | a seat running | `tools/audit/seat/pr_cap.py dispatch-gate`, `tools/audit/seat/cloud_dispatch.py` | `standing-dispatch.md`, `orchestrator.md` sections 5 and 5b | the trigger payload |
 | 7 fixer and review, cloud seats and relay | a dispatched brief | a verdict at a frozen head | `tools/audit/seat/cloud-setup.sh`, `tools/pr/prepr.sh`, `tools/audit/seat/body_push.sh`, `tools/audit/seat/handoff_push.sh`, `tools/audit/seat/cloud_relay.sh` | `fixer.md`, `fix-review.md`, `designer.md`, `design-review.md`, `root-cause.md` | the handoff refs, the pull request, its verdict |
diff --git a/dev/audit/config/scopes.json b/dev/audit/config/scopes.json
index 129d7d5028..1c5db3d37a 100644
--- a/dev/audit/config/scopes.json
+++ b/dev/audit/config/scopes.json
@@ -311,7 +311,7 @@
   "mode": "cells",
   "universe": [
    "README.md",
-   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md",
+   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,heat-curve,how-it-works,setup}.md",
    "custom_components/heatpump_optimizer/*.py",
    "custom_components/heatpump_optimizer/www/*.js",
    "tools/**.{py,sh,js,mjs}",
@@ -487,7 +487,7 @@
    "docs/index.html",
    "docs/site/*.css",
    "tools/site/build_docs.mjs",
-   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md",
+   "docs/{CONTRIBUTING,architecture,automations,configuration,dashboard-card,ecl110,heat-curve,how-it-works,setup}.md",
    "custom_components/heatpump_optimizer/{services.yaml,strings.json,manifest.json}",
    "hacs.json",
    "blueprints/**",
@@ -546,7 +546,7 @@
       "docs/index.html",
       "docs/site/*.css",
       "tools/site/build_docs.mjs",
-      "docs/{architecture,automations,configuration,dashboard-card,ecl110,how-it-works,setup}.md"
+      "docs/{architecture,automations,configuration,dashboard-card,ecl110,heat-curve,how-it-works,setup}.md"
      ],
      "steps": [
       "M1",
diff --git a/dev/audit/harnesses/r10_sav_held_install.py b/dev/audit/harnesses/r10_sav_held_install.py
index 3b9acfd941..081afa9fda 100644
--- a/dev/audit/harnesses/r10_sav_held_install.py
+++ b/dev/audit/harnesses/r10_sav_held_install.py
@@ -11,12 +11,17 @@ outdoor (wind 3 m/s, no rain or sun):
   one-tank  the synthetic fixture pull request 3481's ``fields`` arm builds
             (``profiles.house()``, single zone, the first throttling mode, a
             500 l wood tank, valve target unset).
+  combi     R10-COMBI-TANK's install shape (``r10_combi_tank.params()``:
+            single zone, ``smart_write`` valve, combi tank), the carry's
+            precondition for a single-zone valve on an install's own layout.
 
 Per row: ``held`` is ``_thermostat_held_state``'s room, upper and lower floor;
 ``end`` the same three where ``_compute_baseline_power``'s 96-step day ends;
 ``plant`` where ``simulate_step`` at ``max_electrical_power`` for 288 steps
 from the held state leaves them -- the plant's own ceiling, its tank at the
-cap. ``gap`` is the largest of the six held-to-end and held-to-plant moves, K.
+cap -- and ``settled`` the same after 960 steps, where a single-zone slab has
+stopped moving (R11-VALVE-REFERENCE: its curve's target is ``comfort_ceiling``).
+``gap`` is the largest of the six held-to-end and held-to-plant moves, K.
 The control is ``valve off``: the install with ``mixing_valve_mode`` none,
 whose held floors read 21.000 (no plant column: an unvalved pump at its
 maximum has no ceiling below the target).
@@ -25,6 +30,7 @@ Precondition, asserted (exit 1): every held room lies in [outdoor, 21].
 """
 
 import sys
+from pathlib import Path
 
 import numpy as np
 
@@ -32,7 +38,10 @@ from heatpump_optimizer.optimizer import HeatPumpOptimizer, OptimizationConfig,
 from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters, ThermalState, WeatherSeries
 from profiles import house, replay_install
 
-STEPS, DT_H, WIND = 96, 0.25, 3.0
+sys.path.insert(0, str(Path(__file__).resolve().parent))
+import r10_combi_tank  # noqa: E402
+
+STEPS, DT_H, WIND, SETTLED = 96, 0.25, 3.0, 960
 
 
 def one_tank():
@@ -62,10 +71,12 @@ def row(label, params, outdoor, ceiling=True):
     line = f"{label} {outdoor:+.0f} C: held {fmt(held)} end {fmt(end)}"
     if ceiling:
         plant = held
-        for _ in range(3 * STEPS):
+        for step in range(SETTLED):
             plant = model.simulate_step(plant, params.max_electrical_power, outdoor, WIND, 0.0, 0.0, DT_H)
-        gap = max(abs(a - b) for other in (end, plant) for a, b in zip(zones(held), zones(other)))
-        line += f" plant {fmt(plant)} gap {gap:.3f}"
+            if step + 1 == 3 * STEPS:
+                pumped = plant
+        gap = max(abs(a - b) for other in (end, pumped) for a, b in zip(zones(held), zones(other)))
+        line += f" plant {fmt(pumped)} settled {fmt(plant)} gap {gap:.3f}"
     print(line)
     return min(outdoor, 21.0) <= held.room_temperature <= 21.0
 
@@ -76,6 +87,7 @@ def main():
         ok &= row("install", ThermalParameters.from_config(replay_install()), outdoor)
         ok &= row("valve off", ThermalParameters.from_config(replay_install(mixing_valve_mode="none")), outdoor, False)
         ok &= row("one-tank", one_tank(), outdoor)
+        ok &= row("combi", r10_combi_tank.params(), outdoor)
     if not ok:
         print("PRECONDITION FAILED: a held room outside [outdoor, 21]")
         return 1
diff --git a/dev/audit/harnesses/r11_honest_starts_runs.py b/dev/audit/harnesses/r11_honest_starts_runs.py
index 56032ae21c..8cd2c187e8 100644
--- a/dev/audit/harnesses/r11_honest_starts_runs.py
+++ b/dev/audit/harnesses/r11_honest_starts_runs.py
@@ -1,7 +1,7 @@
 """R11-OUTSIDE-HONEST-STARTS-RUNS: what the committed runs ship, measured on one tree.
 
     PYTHONPATH=tests/hastub:custom_components:tests \\
-        python3 dev/audit/harnesses/r11_honest_starts_runs.py fixtures|c1|descents|grid|gradient|stress|kernels|identity|stage
+        python3 dev/audit/harnesses/r11_honest_starts_runs.py fixtures|c1|descents|grid|defaults|gradient|stress|kernels|identity|stage
 
 Synthetic throughout; no private data. The finding is outside pull request
 3529 (Bankaifan), which has no finder harness; this one reproduces the pull
@@ -37,6 +37,24 @@ and clamped or not: steps under the floor, edges, energy and solve seconds
 (``time.process_time``) per cell. The unpriced duty-cycle cell is the null:
 it must never enter the candidate stage where the tree has one.
 
+``defaults``: owner ruling Q2's measurement (R11-OUTSIDE-HONEST-STARTS-RUNS-P3):
+what a default start price would do to an install with ``clamp_planned_levels``
+on and no configured price. The rule measured: the default replaces a
+configured cycling cost of zero on a clamped install and nothing else. For
+each candidate on ``DEFAULT_LADDER`` (zero, then across the options field's
+0 to 10 range), on the ``grid`` mode's clamped unpriced cell and on the two
+fixtures ``fixtures`` reads, each solved clamped at a configured price of
+zero, per solve: off-to-on edges of the combined draw, energy, the
+optimizer's ``predicted_cost`` (the objective carries the start price, so it
+is not comparable across candidates) and the lowest room temperature. Null
+controls, solved with no default and with the ladder's highest: the same
+three installs at their own configured price (clamped), and the same three
+unclamped at price zero; each pair must ship array-equal plans. Exits 1 when
+a null pair differs. On a tree that ships the default
+(``om.CLAMPED_DEFAULT_START_PRICE``) each candidate patches it and the tree's
+own rule applies it, so the nulls test that rule; on a tree without it the
+rule is applied by the harness and the nulls hold by construction.
+
 ``gradient``: what the batched finite-difference gradient simulates
 (``optimizer._batch_fd_gradient``, design note n6). Four goldens that fix
 part of the horizon (a committed mask, hot-water blocks) and one grid cell
@@ -233,8 +251,29 @@ def descents() -> int:
     return 1 if null_bad else 0
 
 
+GRID_PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0)
+
+
+def _grid_solve(cost: float, clamp: bool, p_min: float, loss: float, out_mean: float):
+    params = ThermalParameters()
+    params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
+    params.min_electrical_power, params.max_electrical_power = p_min, 5.5
+    params.dhw_enabled, params.house_heat_loss_scale = False, loss
+    opt = om.HeatPumpOptimizer(
+        ThermalModel(params), om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost))
+    outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
+    return opt.optimize(inputs=solve_inputs(
+        initial_state=ThermalState(
+            room_temperature=20.5, upper_floor_temperature=20.5,
+            lower_floor_temperature=20.5, slab_temperature=21.0,
+            outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
+            dhw_temperature=50.0,
+        ),
+        prices=GRID_PRICES, outdoor_temps=outdoor, start_time=T0,
+    ))
+
+
 def grid() -> int:
-    prices = 1.3 + 0.9 * np.sin(2 * np.pi * (STEPS - 30) / 96.0)
     staged, bad = [], 0
     kept = getattr(om, "_run_plans", None)
     if kept is not None:
@@ -244,24 +283,9 @@ def grid() -> int:
             (0.0, False, 1.1, 0.4, 8.0), (0.25, False, 1.1, 0.4, 8.0), (0.25, False, 0.53, 0.4, 8.0),
             (0.0, True, 1.1, 0.4, 8.0), (0.25, True, 1.1, 0.4, 8.0), (0.25, False, 1.1, 1.0, 2.0),
         ):
-            params = ThermalParameters()
-            params.mixing_valve_mode, params.buffer_tank_volume = "none", 750.0
-            params.min_electrical_power, params.max_electrical_power = p_min, 5.5
-            params.dhw_enabled, params.house_heat_loss_scale = False, loss
-            opt = om.HeatPumpOptimizer(
-                ThermalModel(params), om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost))
-            outdoor = out_mean + 3.0 * np.sin(2 * np.pi * (STEPS - 50) / 96.0)
             staged.clear()
             t = time.process_time()
-            result = opt.optimize(inputs=solve_inputs(
-                initial_state=ThermalState(
-                    room_temperature=20.5, upper_floor_temperature=20.5,
-                    lower_floor_temperature=20.5, slab_temperature=21.0,
-                    outdoor_temperature=float(outdoor[0]), buffer_tank_temperature=30.0,
-                    dhw_temperature=50.0,
-                ),
-                prices=prices, outdoor_temps=outdoor, start_time=T0,
-            ))
+            result = _grid_solve(cost, clamp, p_min, loss, out_mean)
             seconds = time.process_time() - t
             plan = np.asarray(result.power_schedule, float)
             print(f"cost {cost} clamp {clamp} p_min {p_min} loss {loss}: steps under the floor"
@@ -276,6 +300,77 @@ def grid() -> int:
     return 1 if bad else 0
 
 
+#: Candidate default start prices; the options field (``config_flow``'s wear
+#: group) takes 0 to 10 in steps of 0.05.
+DEFAULT_LADDER = (0.0, 0.05, 0.1, 0.25, 0.5, 1.0, 1.5, 2.5, 5.0, 10.0)
+
+
+def _default_installs():
+    """(label, configured price, solve(clamp, price)) for the grid cell and the two fixtures."""
+    import golden
+
+    def fixture(name):
+        spec = golden.SCENARIOS[name]
+
+        def solve(clamp, price):
+            opt = dict(spec.get("opt_overrides") or {}, clamp_planned_levels=clamp, cycling_cost=price)
+            got = golden.capture(name, dict(spec, opt_overrides=opt))
+            space = np.asarray(got["power_schedule"], float)
+            dhw = np.asarray(got.get("dhw_power_schedule") or np.zeros_like(space), float)
+            return space + dhw, float(got["predicted_cost"]), float(np.min(got["room_temp_trajectory"]))
+        return name, float(spec["opt_overrides"]["cycling_cost"]), solve
+
+    def grid_cell(clamp, price):
+        r = _grid_solve(price, clamp, 1.1, 0.4, 8.0)
+        return (np.asarray(r.power_schedule, float), float(r.predicted_cost),
+                float(np.min(r.room_temp_trajectory)))
+    return [("grid p_min 1.1 loss 0.4", 0.25, grid_cell), fixture("cycling_cost"), fixture("everything_on")]
+
+
+def _effective(clamp: bool, configured: float, default: float) -> float:
+    """The measured rule: the default replaces a configured zero on a clamped install only."""
+    return default if clamp and configured == 0 else configured
+
+
+def _at_default(solve, clamp: bool, configured: float, default: float):
+    """``solve`` with ``default`` as the clamped default start price.
+
+    Where the tree ships the default (``om.CLAMPED_DEFAULT_START_PRICE``),
+    the tree's own rule applies it, patched to the candidate; on a tree
+    without it, the measured rule above is applied here.
+    """
+    if not hasattr(om, "CLAMPED_DEFAULT_START_PRICE"):
+        return solve(clamp, _effective(clamp, configured, default))
+    kept = om.CLAMPED_DEFAULT_START_PRICE
+    om.CLAMPED_DEFAULT_START_PRICE = default
+    try:
+        return solve(clamp, configured)
+    finally:
+        om.CLAMPED_DEFAULT_START_PRICE = kept
+
+
+def defaults() -> int:
+    def line(plan, cost, room):
+        return (f"starts {edges(plan)}, energy_kwh {float(np.sum(plan)) * 0.25:.2f},"
+                f" predicted_cost {cost:.4f}, lowest_room {room:.2f}")
+
+    bad = 0
+    for label, priced, solve in _default_installs():
+        for default in DEFAULT_LADDER:
+            plan, cost, room = _at_default(solve, True, 0.0, default)
+            print(f"{label}, clamped, configured 0, default {default}: {line(plan, cost, room)}")
+        top = DEFAULT_LADDER[-1]
+        for arm, clamp, configured in (("priced clamped", True, priced), ("unpriced unclamped", False, 0.0)):
+            without = _at_default(solve, clamp, configured, 0.0)
+            with_ = _at_default(solve, clamp, configured, top)
+            same = np.array_equal(without[0], with_[0])
+            print(f"{label}, null {arm} (configured {configured}): without default {line(*without)};"
+                  f" default {top}: {line(*with_)}; array-equal {same}")
+            bad += not same
+    print(f"null pairs that differ {bad}")
+    return 1 if bad else 0
+
+
 def _metered(solve):
     """Run ``solve`` with the batched gradient metered; its plan and the meter."""
     kept = om._batch_fd_gradient
@@ -682,6 +777,6 @@ def kernels() -> int:
 
 
 if __name__ == "__main__":
-    sys.exit({"fixtures": fixtures, "c1": c1, "descents": descents, "grid": grid, "gradient": gradient,
+    sys.exit({"fixtures": fixtures, "c1": c1, "descents": descents, "grid": grid, "defaults": defaults, "gradient": gradient,
               "stress": stress_cost, "kernels": kernels,
               "identity": identity, "stage": stage}[sys.argv[1]]())
diff --git a/dev/audit/harnesses/r11_selftest_static_edge.py b/dev/audit/harnesses/r11_selftest_static_edge.py
new file mode 100644
index 0000000000..97bf018176
--- /dev/null
+++ b/dev/audit/harnesses/r11_selftest_static_edge.py
@@ -0,0 +1,76 @@
+#!/usr/bin/env python3
+"""R11-RCA-SELFTEST-TABLE-DRIFT harness, the rejected countermeasure: one-hop static detector of new reads by gated self-test steps.
+
+    python3 dev/audit/harnesses/r11_selftest_static_edge.py REPO BASE HEAD [--table-ref REF]
+
+For each gated step's committed entry (table at --table-ref, default HEAD), every
+file the diff BASE..HEAD changes that the entry already reads is scanned at BASE
+and HEAD for references to tracked paths (literal path strings, a bare file name
+resolved beside the file, Python imports); a reference new at HEAD that the entry
+does not name (files, dirs, probes) is printed: STEP KIND PATH VIA.
+"""
+import json, os, re, subprocess, sys
+
+repo, base, head = sys.argv[1:4]
+tref = sys.argv[sys.argv.index("--table-ref") + 1] if "--table-ref" in sys.argv else head
+
+
+def git(*a):
+    return subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True).stdout
+
+
+def show(ref, path):
+    r = subprocess.run(["git", "-C", repo, "show", f"{ref}:{path}"], capture_output=True)
+    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
+
+
+tracked = set(git("ls-tree", "-r", "--name-only", head).split("\n")) - {""}
+dirs = set()
+for p in tracked:
+    d = os.path.dirname(p)
+    while d:
+        dirs.add(d)
+        d = os.path.dirname(d)
+TOK = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]*")
+IMP = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import\s+([\w, ]+)|import\s+([\w., ]+))", re.M)
+
+
+def refs(path, text):
+    out = set()
+    here = os.path.dirname(path)
+    for t in TOK.findall(text):
+        t = t.rstrip("/.")
+        if t.startswith("./"):
+            t = t[2:]
+        for c in (t, os.path.normpath(os.path.join(here, t)) if "/" not in t or t.startswith("..") else None):
+            if c and c != path and (c in tracked or (c in dirs and "/" in c)):
+                out.add(c)
+    if path.endswith(".py"):
+        for m in IMP.finditer(text):
+            mods = [m.group(1)] if m.group(1) else [x.strip().split(" ")[0] for x in m.group(3).split(",")]
+            if m.group(1):
+                mods += [m.group(1) + "." + x.strip().split(" ")[0] for x in m.group(2).split(",")]
+            for mod in mods:
+                rel = mod.replace(".", "/")
+                for c in (rel + ".py", rel + "/__init__.py", os.path.join(here, rel + ".py")):
+                    if c in tracked and c != path:
+                        out.add(c)
+    return out
+
+
+table = json.loads(show(tref, "tools/ci/selftest_closures.json"))["steps"]
+changed = [l.split("\t") for l in git("diff", "--name-status", "--no-renames", base, head).splitlines()]
+changed = {p for s, p in changed if s != "D"}
+cache = {}
+n = 0
+for sid, e in sorted(table.items()):
+    known = set(e.get("files", [])) | set(e.get("dirs", [])) | set(e.get("probes", []))
+    for f in sorted(changed & set(e.get("files", []))):
+        if f not in cache:
+            h, b = show(head, f), show(base, f)
+            cache[f] = refs(f, h or "") - refs(f, b or "")
+        for r in sorted(cache[f] - known):
+            kind = "dirs" if r in dirs and r not in tracked else "files"
+            print(sid, kind, r, "via", f)
+            n += 1
+print(f"# {n} flagged, {len(changed)} changed files", file=sys.stderr)
diff --git a/dev/audit/harnesses/r11_why_hover_fit.mjs b/dev/audit/harnesses/r11_why_hover_fit.mjs
new file mode 100644
index 0000000000..eaea8ebb7f
--- /dev/null
+++ b/dev/audit/harnesses/r11_why_hover_fit.mjs
@@ -0,0 +1,86 @@
+// R11-OWNER-GENERIC-CONTROL-TEXT carry (#3643): does the chart hover's
+// explanation block (.tt-why) survive fitWhy once why.sub_dearer is reworded? Drives the
+// card at one git ref in Chromium at 375 and 500 px, on the tile chart and the
+// expanded dialog's chart, hovering the repository fixture's dearest idle space
+// step (tests/plan_view.py's payload through tests/card_rig.mjs's planStates,
+// its published reason idle_dearer). Per surface and width it prints the chart's
+// fitWhy cap, the tooltip's height with fitWhy disabled (natural) and enabled
+// (fitted), whether the explanation block is shown, and each line's rendered
+// height (one line is the computed line-height).
+//
+//    node dev/audit/harnesses/r11_why_hover_fit.mjs <ref> [plan.json]
+//
+// WHY_SUB_DEARER="<text>" replaces the English why.sub_dearer string in the
+// ref's card before it loads: the control arm, e.g. "this hour is more
+// expensive than the hours the plan uses". The plan payload defaults to the
+// per-checkout path tests/plan_view.py writes. Needs Playwright's Chromium.
+
+import { createRequire } from "node:module";
+import { execFileSync } from "node:child_process";
+import { createHash } from "node:crypto";
+import fs from "node:fs";
+import os from "node:os";
+import path from "node:path";
+import { fileURLToPath } from "node:url";
+const require = createRequire(import.meta.url);
+const { chromium } = require("playwright");
+const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
+const rig = await import(path.join(repo, "tests/card_rig.mjs"));
+const ref = process.argv[2];
+if (!ref) { console.error("usage: r11_why_hover_fit.mjs <ref> [plan.json]"); process.exit(2); }
+const planPath = process.argv[3] || process.env.HPO_PLANDATA ||
+  path.join("/tmp", `plandata-${createHash("sha256").update(path.join(repo, "tests")).digest("hex").slice(0, 12)}.json`);
+let src = execFileSync("git", ["-C", repo, "show", `${ref}:${rig.CARD_PATH}`], { encoding: "utf8", maxBuffer: 64 << 20 });
+if (process.env.WHY_SUB_DEARER) {
+  const re = /("why\.sub_dearer": )"[^"]*"/;
+  if (!re.test(src)) { console.error("why.sub_dearer not found in the card"); process.exit(2); }
+  src = src.replace(re, `$1${JSON.stringify(process.env.WHY_SUB_DEARER)}`);
+}
+const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "hpo-why-fit-"));
+const cardSrc = path.join(tmp, "card.js");
+fs.writeFileSync(cardSrc, src);
+const plan = JSON.parse(fs.readFileSync(planPath, "utf8"));
+const st = rig.planStates(plan);
+const idle = st[rig.DEFAULT_SPACE].attributes.forecast.filter((p) => !(Number(p.space_power) > 0.05));
+const maxP = Math.max(...idle.map((p) => p.price));
+const step = idle.find((p) => p.price === maxP);
+console.log(`ref=${ref} step=${step.t} reason=${step.reason}`);
+const browser = await chromium.launch();
+for (const dialog of [false, true]) for (const natural of [true, false]) for (const W of [375, 500]) {
+  const ctx = await browser.newContext({ viewport: { width: W, height: 800 }, deviceScaleFactor: 1 });
+  await ctx.clock.setFixedTime(Date.parse(plan.dhw_plan.forecast[0].t) + 6 * rig.HOUR);
+  const page = await ctx.newPage();
+  await page.setContent("<!doctype html><html><head></head><body></body></html>");
+  await page.addScriptTag({ path: cardSrc });
+  const r = await page.evaluate(async ([st, W, t, natural, dialog]) => {
+    // The card is a classic script, so its top-level fitWhy is a global binding.
+    if (natural) window.fitWhy = () => {};
+    const frame = () => new Promise((res) => requestAnimationFrame(() => requestAnimationFrame(res)));
+    const s = document.createElement("style");
+    s.textContent = `body{margin:0;padding:16px} heatpump-optimizer-card{display:block;width:${W}px}`;
+    document.head.appendChild(s);
+    const card = document.createElement("heatpump-optimizer-card");
+    document.body.appendChild(card);
+    card.setConfig({ type: "custom:heatpump-optimizer-card" });
+    card.hass = { states: st, language: "en", themes: { darkMode: false } };
+    await frame();
+    if (dialog) { card._onCardClick({}); await frame(); }
+    const root = card.shadowRoot, plot = card._plot;
+    const svgs = [...root.querySelectorAll(".chartwrap svg")];
+    const svg = svgs[svgs.length - 1];
+    const rect = svg.getBoundingClientRect();
+    const x = rect.left + (plot.scaleX(Date.parse(t) + 450000) / svg.viewBox.baseVal.width) * rect.width;
+    card._onPointerMove({ clientX: x, clientY: rect.top + rect.height * 0.45, currentTarget: svg });
+    const tt = svg.closest(".chartwrap").parentNode.querySelector(".tooltip") || root.querySelector(".tooltip");
+    const why = tt.querySelector(".tt-why");
+    const li = why ? [...why.querySelectorAll("li")] : [];
+    const lh = li.length ? parseFloat(getComputedStyle(li[0]).lineHeight) : 0;
+    return { cap: Math.round(rect.height - 16), h: tt.offsetHeight, shown: !!why,
+      lines: li.map((l) => Math.round(l.getBoundingClientRect().height / (lh || 1))), first: li.length ? li[0].textContent : "" };
+  }, [st, W, step.t, natural, dialog]);
+  console.log(`${dialog ? "dialog" : "tile"} ${natural ? "natural" : "fitted"} W=${W} cap=${r.cap} height=${r.h} ` +
+    `block=${r.shown} lines=${JSON.stringify(r.lines)} first="${r.first}"`);
+  await ctx.close();
+}
+await browser.close();
+fs.rmSync(tmp, { recursive: true, force: true });
diff --git a/dev/audit/harnesses/vendor_text_census.py b/dev/audit/harnesses/vendor_text_census.py
new file mode 100644
index 0000000000..7654e5b189
--- /dev/null
+++ b/dev/audit/harnesses/vendor_text_census.py
@@ -0,0 +1,114 @@
+#!/usr/bin/env python3
+"""Every vendor, model or integration name in the user-facing text.
+
+    python3 dev/audit/harnesses/vendor_text_census.py [--root DIR] [--counts]
+
+The user-facing surface is `README.md`, `docs/` (less `docs/design/`, the
+dated design notes, and the figure generators under `docs/img/`), the
+integration's `strings.json` and `translations/*.json` (values only, each
+reported at its key path), the card's `www/*.js` and `services.yaml`. Each
+line or JSON value is matched against `BRANDS`, case-insensitively, as a
+whole word: a name glued to `_` or a letter (`ecl110_displace_set_topic`, an
+option key or entity id) is an identifier, not prose, and is not a hit.
+
+One line per hit: `path:locator<TAB>brand<TAB>excerpt`. `--counts` prints
+only `brand<TAB>count` lines and a `total<TAB>N` line. Exit 0 always: this is an
+enumerator whose output a seat rules hit by hit (an example of a generic
+shape, a real restriction, or a leftover), not a gate.
+
+`BRANDS` was built from every capitalised token of the same surface, read
+by hand at main b3831ff64e; a name it lacks is a hit this census misses, so
+a new vendor named in the text joins the list in the same change.
+
+Perturbation: add the word `Thermia` to any README line and `--counts`
+prints `thermia 1` and a total one higher.
+"""
+from __future__ import annotations
+
+import json
+import re
+import subprocess
+import sys
+from pathlib import Path
+
+BRANDS = (
+    "Luxtronik", "Danfoss", "ECL110", "ECL", "Tibber", "Nord Pool",
+    "ENTSO-E", "Open-Meteo", "Met.no", "Daikin", "NIBE", "Novelan",
+    "Alpha Innotec", "Stiebel Eltron", "Stiebel", "Vaillant", "Panasonic",
+    "Mitsubishi", "Thermia", "Viessmann", "Bosch", "Homey", "Rotenso",
+    "Windmi", "GCHV", "Tuya", "Vattenfall", "Ellevio", "Shelly", "Tado",
+    "ESPHome", "Modbus", "Zigbee", "ApexCharts", "Bouni", "EKMBDXA",
+    "S1256PC", "LWDV", "GWF", "Kamstrup", "Smart Home Interface", "SHI",
+)
+_PATTERN = re.compile(
+    r"(?<![\w])("
+    + "|".join(re.escape(b).replace(r"\ ", r"[ -]?") for b in sorted(BRANDS, key=len, reverse=True))
+    + r")s?(?![\w])",
+    re.IGNORECASE,
+)
+_CANON = {b.lower().replace(" ", ""): b for b in BRANDS}
+
+
+def _canon(word: str) -> str:
+    return _CANON.get(re.sub(r"[ -]", "", word.lower()), _CANON.get(word.lower(), word))
+
+
+def _surface(root: Path) -> list[str]:
+    files = subprocess.run(
+        ["git", "-C", str(root), "ls-files", "README.md", "docs",
+         "custom_components/heatpump_optimizer/strings.json",
+         "custom_components/heatpump_optimizer/translations",
+         "custom_components/heatpump_optimizer/www",
+         "custom_components/heatpump_optimizer/services.yaml"],
+        check=True, capture_output=True, text=True,
+    ).stdout.split()
+    return [
+        f for f in files
+        if not f.startswith(("docs/design/", "docs/img/"))
+        and f.endswith((".md", ".json", ".js", ".yaml", ".html"))
+    ]
+
+
+def _json_values(obj, path: str):
+    if isinstance(obj, dict):
+        for key, value in obj.items():
+            yield from _json_values(value, f"{path}.{key}" if path else key)
+    elif isinstance(obj, list):
+        for i, value in enumerate(obj):
+            yield from _json_values(value, f"{path}[{i}]")
+    elif isinstance(obj, str):
+        yield path, obj
+
+
+def census(root: Path):
+    for rel in _surface(root):
+        text = (root / rel).read_text(encoding="utf-8")
+        if rel.endswith(".json"):
+            units = _json_values(json.loads(text), "")
+        else:
+            units = ((str(n), line) for n, line in enumerate(text.splitlines(), 1))
+        for locator, unit in units:
+            for match in _PATTERN.finditer(unit):
+                start = max(0, match.start() - 60)
+                excerpt = unit[start:match.end() + 60].replace("\n", " ").replace("\t", " ")
+                yield rel, locator, _canon(match.group(1)), excerpt.strip()
+
+
+def main(argv: list[str]) -> int:
+    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else Path.cwd()
+    hits = list(census(root))
+    if "--counts" in argv:
+        counts: dict[str, int] = {}
+        for _, _, brand, _ in hits:
+            counts[brand] = counts.get(brand, 0) + 1
+        for brand, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
+            print(f"{brand}\t{n}")
+        print(f"total\t{len(hits)}")
+        return 0
+    for rel, locator, brand, excerpt in hits:
+        print(f"{rel}:{locator}\t{brand}\t{excerpt}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md b/dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md
new file mode 100644
index 0000000000..90e64bb5ca
--- /dev/null
+++ b/dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md
@@ -0,0 +1,242 @@
+# R11-RCA-SELFTEST-TABLE-DRIFT: main's self-test read-set table lags the merges that add reads
+
+Root-cause seat beside R11-HOTFIX-MAIN-SELFTEST-DRIFT (`handoff/r11-hotfix-main-selftest-drift`,
+code `142926ec66`). It runs beside that fix and lands no code. Measured at `origin/main`
+`6f422812d5` on 2026-11-16. It extends `R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md` (the round-10
+family record) with round 11's instances. It also judges the PR-time detector the hotfix body
+proposes.
+
+## 1. The defect, reproduced
+
+Push run 43884631892 at `e352724335` (merge of #3645): `governance / instrument-self-tests`,
+step "Refuse a self-test read set the committed table misses", 27 `UNDER-SCOPED` refusals.
+Reproduced off-Linux from that run's `selftest-closures` artifact: `selftest_scope.drift(table
+at e352724335, artifact steps, job_steps(governance.yml at e352724335))` returns 27 refusals.
+Against the artifact itself it returns 0, and against `142926ec66`'s table it also returns 0.
+The added reads are 67 (step, kind, path) triples: 45 `files`, 13 `dirs`, 9 `probes`.
+
+**The reported attribution is partly wrong.** The hotfix body names #3644, #3625 and #3651.
+To check it, I took each read path the window added and found the first-parent merge that
+added it (`git log --first-parent --diff-filter=A 82e301585d..e352724335 -- PATH`):
+
+| merge | reads of paths it added |
+|---|---|
+| #3622 (`tools/audit/seat/plan_phases.py`, `dev/programme/round11/`) | 14 |
+| #3644 (`round_metrics.py`, `round_metrics_selftest.py`) | 8 |
+| #3625 (`tools/audit/enumerate.py`) | 7 |
+| #3640 (`tests/mutation_ledger/*/slab_seed.py`) | 6 |
+| #3627 (`dev/governance/config/machinery_target_budgets.json`) | 3 |
+| #3641 (`dev/governance/dimensions/criteria/`) | 2 |
+
+That accounts for 40 of the 67 reads. The other 27 are reads of older files, most of them in
+`plan-page` (8) and `orchestrator-tick` (8). #3651 added none of the read paths.
+
+The race in one example: #3652, the previous re-record, measured at `82e301585d`. #3622 merged
+at 04:16:31Z and #3652 at 04:20:42Z. So the largest group of reads in this instance landed four
+minutes before the hotfix meant to clear main's red.
+
+## 2. Named cause
+
+The table is measured only on a push to main. The drift step's `if:` reads
+`env.SELFTEST_TRACE != ''`, and `SELFTEST_TRACE` is set only when `github.event_name ==
+'push'` (`governance.yml` lines 313 and 1592). So no pull request can see that its merge adds a
+read. The repair is a hand re-record, as a hotfix pull request, measured at one main SHA. It
+merges 1 to 2.5 hours later, and in that time main merges about 1.6 pull requests an hour
+(77 first-parent merges from 2026-11-14T15:40Z to 2026-11-16T15:44Z). The hotfix therefore
+almost never catches up:
+
+- Over the 80 `ci.yml` push runs on main from 2026-11-14T14:59Z to 2026-11-16T15:50Z, the drift
+  step concluded 55 times. It failed 54 times and succeeded once, at `dd62a612a2` (#3606's own
+  merge). The run after it was red again. Source: the jobs API for each run, step "Refuse a
+  self-test read set the committed table misses".
+- The re-record merges #3629 and #3652 were red at their own merge commits (`f7ead6bb1f` and
+  `5aaf9c112f`).
+
+Every round-11 instance so far is a pull request that adds a file or an edge some gated step
+reads, merging after the last measurement. Some of those pull requests re-recorded their own new
+steps (#3644, #3625 and #3651 each touched the table); none re-measures the other steps.
+
+## 3. Process state: (c)
+
+**The process existed and was followed:**
+- The drift check ran on every push that reached it and refused 54 of its 55 conclusions.
+- A re-record hotfix was dispatched six times in 48 hours: #3589, #3595, #3606, #3629 and
+  #3652 were reviewed and merged, and `142926ec66` is handed off.
+
+**It did not produce the intended result.** The intent was a green main and a table that scopes
+pull requests correctly. Main got one green drift run in 55. The unit is wrong: a hand repair
+measured at one SHA cannot outrun a merge rate higher than its own turnaround.
+
+Why the other states do not fit:
+- **Not (a):** a check exists.
+- **Not (b):** no step was skipped.
+- **Not (d):** the table has lagged additions since #3315 introduced it. Nothing changed
+  underneath it.
+
+**Why the existing barriers do not reach these instances:**
+- `R10-SELFTEST-TABLE-SHRINK`'s barrier is the `union_record` that #3551 landed. It stops a
+  re-record from *dropping* reads. These instances *add* reads.
+- `R10-SELFTEST-RED-INTRODUCED`'s barrier, `merge_train.py introduced`, compares a pull
+  request's self-test steps at its head and at the merge base. The drift step does not run on a
+  pull request, so it is red at neither end.
+
+This agrees with the family record's state (c). Round 11 adds the measurement that the hotfix
+unit leaves main red even when it is followed promptly.
+
+## 4. Class reach
+
+- **The same class:** 13 hotfix re-records to date. That is the family record's ten (#3375 to
+  #3606), plus #3629, #3652 and `142926ec66`.
+- **The same shape elsewhere:** a measured file that is repaired by hand inside pull requests
+  while main measures it. The family record and loop card L9 name four such files:
+  - `tests/closures.json`, which `closures-autofix` already repairs on the pull request in CI;
+  - the figure blocks;
+  - the brief line pins;
+  - the claim files' stamp line.
+
+  This search found no fifth.
+- **Not yet in `dev/audit/config/bugclasses.json`.** The nearest class is
+  `R10-SELFTEST-TABLE-SHRINK`, which covers drops, not additions. Adding the class belongs to the
+  countermeasure's group, below.
+
+## 5. The detectors judged, measured over this instance's window
+
+The window is the 15 first-parent merges from `5aaf9c112f` (#3652) to `e352724335`. The truth
+set is the 67 reads `142926ec66` adds.
+
+**C1, the hotfix body's proposal: a static PR-time detector "like step 6d".** I built it as
+`dev/audit/harnesses/r11_selftest_static_edge.py`. For each gated step, it scans the files the
+diff changes that the step already reads, at the base and at the head, for:
+- literal tracked paths;
+- bare file names beside the file;
+- Python imports.
+
+It flags each new reference the step's entry lacks. I ran it per merge, against each merge's own
+table:
+
+| measure | result |
+|---|---|
+| reads caught | 14 of 67 (21%) |
+| flags raised | 333 unique flags (412 per-merge lines) |
+| precision | 14 of 333 (4%) |
+| flags per merge | about 22 per merge on average, up to 119 at #3641 |
+
+A second static rule flags a file the diff adds under a directory the step lists. It caught 8 of
+the 45 file reads with 384 flags.
+
+Static analysis misses because most new reads are not import edges from a changed file. They
+are:
+- a step listing a directory and reading what it finds (`dirs` and `probes`, 22 of the 67, which
+  include git's `config`, `objects` and `refs` probes);
+- a data-driven read through a list held elsewhere, such as `tests/closure.py`'s INERT entries;
+- a new file opened by a tool that walks the tree.
+
+With C1, 53 reads would still have reached main: main stays red and the hotfix is still owed.
+The detector avoids no instance and costs a seat about 22 false lines a merge to read. **It
+fails the cost test.**
+
+Step 6d is not static either. `tests/closures.json` closures are recorded dynamically:
+- Python lanes run under `sys.addaudithook`;
+- the inert dimension runs under strace on Linux.
+
+The faithful analogue is a traced run, priced as C3 and C4.
+
+**C2, a Darwin approximation.** Darwin has no strace. `selftest_scope precheck`, built on
+`fix/r11-pre-shared-files`, returns rc 3 (skip) there. An audit-hook tracer would see Python
+processes only. Not measured. At least the 9 git and directory probes in the truth set come from
+non-Python processes, so the most it could reach is 58 of 67. **Not recommended:** it would be
+a second, weaker recorder beside the strace one.
+
+**C3, `precheck` as built on `fix/r11-pre-shared-files` (`fe138c567b`).** It traces, on Linux
+in a scratch clone, only the gated steps whose own command-named script the diff changes. I ran
+its `touched_steps` per merge over the window:
+- it selects 6 of the 20 drifting steps;
+- those 6 steps hold 22 of the 67 reads (33%). That is an upper bound, because a touched step is
+  not always touched by the merge that added its read.
+
+Tracing every step whose recorded files the diff changes was its builder's first cut: 17 steps
+and 43 minutes for one diff. It was dropped on cost. **No change recommended to the build.** It
+would not have prevented this instance.
+
+**C4, tracing the selected steps in pull-request CI on Linux.** This is exact.
+
+Its cost, measured as `instrument-self-tests` job wall time:
+- untraced on a pull request: 18.9 to 23.8 minutes for 51 to 130 steps (six concluded runs on
+  2026-11-16);
+- traced on a push: 38.5 to 71.7 minutes over main's last 12 concluded push runs.
+
+So about +35 minutes per FULL pull-request job, over the 30-minute pull-request cap. The pull
+requests that drift (adding files under `tools/`) are exactly the ones that run FULL. The fix
+would also have to commit the table inside the pull request, which is a gate file. That is the
+hand-edit L9 directs away from. **It fails the cost test** (77 merges × ≥35 runner-minutes in
+the window, against six hotfixes), and the owner has ruled out CI widening.
+
+## 6. Cost test
+
+    cost(countermeasure, recurring) < cost(defect) x P(recurrence)
+
+**cost(defect), per instance:**
+- one hotfix pull request, open for 62, 64, 105, 129 and 152 minutes (#3589, #3595, #3606,
+  #3629, #3652; median 105), created to merged;
+- one fixer and one reviewer each;
+- one FULL CI run, because the table is a gate file;
+- the job left red on main. This hides any other step's red at job level, as #3629 found its
+  60-minute-cap cause inside it.
+
+**P(recurrence), measured:** 6 instances in 48 hours (2026-11-14T15:40Z to 2026-11-16T15:44Z), about 1 per 13 merges. That is up from the
+family record's 1 per 25. A hotfix also clears main's red in only 1 of 6 instances, so on
+present form the defect does not end.
+
+| option | standing cost | instances avoided | verdict |
+|---|---|---|---|
+| C1 static detector | about 22 false flags per merge | 0 of 1 in the window (21% recall) | fails |
+| C2 Darwin audit hook | a second recorder; recall not measured, at most 58 of 67 | not measured | not recommended |
+| C3 `precheck` (built) | already paid by its group | 0 of 1 (at most 33% recall) | keep as built |
+| C4 PR-time CI trace | about +35 min per FULL PR job, over the cap | all PR-made | fails |
+| C5 main-side absorb bot | zero on a green push; one bot commit per red push batch; no seat | every hotfix seat | **passes** |
+| C6 batch absorb, interim | one artifact data commit per record batch | at one batch a day, 4 of 6 hotfix pull requests (estimate) | **passes** |
+
+**C5** is countermeasure A's unbuilt half: P748 part 1, which the R11-PRE-SHARED-FILES fix
+body records as "not built", with placement D1/D2 still the owner's decision. Its standing cost
+on a green push is zero. It removes the fixer, the reviewer and the FULL CI run from every
+instance. It closes the race only if it keeps **one standing pull request**: every red push
+unions its artifact into it (`absorb --from`), and that pull request merges on the next train.
+A new pull request per measurement would race exactly as the hotfixes do.
+
+**C6** needs no tooling and is legal under the round-11 freeze. The drift red is a non-required
+red that every pull request inherits (owner ruling 2026-11-07: only owed reds block). So:
+- stop dispatching a hotfix per red;
+- once per record batch, commit main's latest push run's `selftest-closures` artifact as
+  `tools/ci/selftest_closures.json`. This is what `142926ec66` did, and the docstring's own
+  repair.
+
+Its residual cost: while the table lags, a pull request that edits a newly read file does not run
+the step that reads it. A break there is caught on main's FULL push run, one merge late. That
+is CLAUDE.md rule 1's stated design for a wrong closure, and the same exposure every lag window
+already has.
+
+## 7. Countermeasure
+
+- **Recommended: C5**, as proposal P-R11-41 in the round-11 proposals file, with C6 as its
+  interim until it lands. C5 addresses the state-(c) unit: the repair moves off hand-made
+  pull requests onto main's own measurement, with one standing pull request so it cannot fall
+  behind.
+- **Refused, with the numbers above:** C1 (the hotfix body's static detector), C2 and C4.
+- **C3** stays as its group built it.
+- **Owed by C5's group:**
+  - the `bugclasses.json` entry for this class (additions, as against `R10-SELFTEST-TABLE-SHRINK`),
+    citing this file;
+  - the demonstration the family record states: the job red on a planted unrecorded read and
+    green after the bot commit, and, as the null control, a green push that writes nothing.
+
+## Reproduction
+
+    W=<checkout at origin/main>
+    gh run download 43884631892 -n selftest-closures -D art
+    python3 -c 'import sys,json; sys.path.insert(0,"tools/ci"); import selftest_scope as s, subprocess as p
+    g=lambda r,f: p.check_output(["git","show",f"{r}:{f}"]).decode()
+    a=json.load(open("art/selftest_closures.json"))["steps"]; st=s.job_steps(g("e352724335",s.WORKFLOW))
+    print(len(s.drift(json.loads(g("e352724335",s.TABLE)),a,st)[0]), len(s.drift(json.loads(g("142926ec66",s.TABLE)),a,st)[0]))'
+    # 27 0
+    for m in $(git rev-list --first-parent 5aaf9c112f..e352724335); do
+      python3 dev/audit/harnesses/r11_selftest_static_edge.py . $m^1 $m; done   # C1's flags
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 140a991302..0cc3d68652 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -49,7 +49,7 @@
   "source": "README.md:Entities",
   "claim": "Twenty entities are disabled by default, and these are they (#1335)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor']",
+  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor']",
   "verdict": "true",
   "truth": ""
  },
@@ -67,7 +67,7 @@
   "source": "README.md:### Sensors",
   "claim": "the sensor table names exactly the sensors the platform constructs",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor']",
+  "result": "documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor']",
   "verdict": "true",
   "truth": ""
  },
@@ -724,7 +724,7 @@
   "source": "docs/ecl110.md",
   "claim": "both ECL110 sensors are disabled by default and diagnostic",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "[('ECL110 Displace', False, 'diagnostic'), ('ECL110 Effective Displace', False, 'diagnostic')]",
+  "result": "[('Heat-Curve Displace', False, 'diagnostic'), ('Heat-Curve Effective Displace', False, 'diagnostic')]",
   "verdict": "true",
   "truth": ""
  },
@@ -965,9 +965,9 @@
  {
   "id": "C108",
   "source": "README.md + docs/*.md",
-  "claim": "every relative link resolves (93 links)",
+  "claim": "every relative link resolves (98 links)",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "93 links, broken=[], of which removed-by-the-export=[]",
+  "result": "98 links, broken=[], of which removed-by-the-export=[]",
   "verdict": "true",
   "truth": ""
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index d2efbd77de..322f75a4e3 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -9,9 +9,9 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C3 | `README.md:### Binary Sensors` | Binary Sensors (6 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=6 measured=6 | **true** |  |
 | C4 | `README.md:### Buttons` | Buttons (6 total) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=6 measured=6 | **true** |  |
 | C5 | `docs/architecture.md:mermaid` | 82 entities / 62 sensors / 6 binary sensors / 6 buttons / 6 switches / 1 climate / 1 datetime | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=(82, 62, 6, 6, 6, 1, 1) measured=(82, 62, 6, 6, 6, 1, 1) | **true** |  |
-| C6 | `README.md:Entities` | Twenty entities are disabled by default, and these are they (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] | **true** |  |
+| C6 | `README.md:Entities` | Twenty entities are disabled by default, and these are they (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Contract Comparison', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Lower Floor Temperature', 'Measured Power', 'Slab Temperature (Estimated)', 'Solar Surplus Forecast', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood Cheaper Than Heat Pump', 'Wood-Burn Night Advisor'] | **true** |  |
 | C7 | `README.md:Entities` | exactly twenty entities are disabled by default (#1335) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=20 measured=20 | **true** |  |
-| C8 | `README.md:### Sensors` | the sensor table names exactly the sensors the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'ECL110 Displace', 'ECL110 Effective Displace', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] | **true** |  |
+| C8 | `README.md:### Sensors` | the sensor table names exactly the sensors the platform constructs | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] measured=['Buffer Tank Temperature', 'Compressor Frequency Advisor', 'Compressor Starts', 'Cost Baseline', 'Cost Contract Comparison', 'Cost Electricity Price (now)', 'Cost Monthly Peak Power', 'Cost Power Headroom', 'Cost Predicted', 'DHW Cost (lifetime)', 'DHW Energy (lifetime)', 'DHW Heating Cost (next 24 h)', 'DHW Heating Schedule', 'DHW Heavy Day Demand', 'DHW Mixed Water', 'DHW Setpoint Advisor', 'DHW Temperature', 'Floor Heating Return Temperature', 'Heat Pump Action', 'Heat-Curve Displace', 'Heat-Curve Effective Displace', 'Indoor Temperature (Optimizer)', 'Indoor Temperature (Predicted)', 'Last Optimization', 'Learning Comfort Weight', 'Learning Estimated COP', 'Learning Model Status', 'Learning Observed COP', 'Lifetime Space Heating Cost', 'Lifetime Space Heating Energy', 'Lifetime Total Energy', 'Lifetime Total Heating Cost', 'Lower Floor Temperature', 'Measured Power', 'Model Restart Advisor', 'Next Optimization', 'Optimal Setpoint', 'Optimization Mode', 'Optimization Schedule', 'Optimization Schedule Steps', 'Optimization Status', 'Outdoor Temperature (Optimizer)', 'Plan DHW Heating (next 24 h)', 'Plan Monthly Savings', 'Plan Narrative', 'Plan Optimization Score', 'Plan Predicted Savings', 'Plan Savings Percentage', 'Plan Space Heating (next 24 h)', 'Prediction Accuracy', 'Predictive Optimization Insight', 'Recommended Power', 'Sensor-Gap Advisor', 'Slab Temperature (Estimated)', 'Solar Heat Gain', 'Solar Irradiance', 'Solar Surplus Forecast', 'Thermal Battery Charge', 'Thermal Battery Energy', 'Upper Floor Temperature', 'Valve Target Recommendation', 'Wood-Burn Night Advisor'] | **true** |  |
 | C9 | `README.md:### Sensors` | every sensor row's Unit column is the unit the entity publishes (CUR = the instance currency) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 62 rows checked, mismatches=[] | **true** |  |
 | C10 | `README.md:### Sensors` | every row whose Notes begin `Diagnostic` is EntityCategory.DIAGNOSTIC, and no other row is | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | mismatches=[] | **true** |  |
 | C11 | `README.md:### Sensors` | every row whose Notes say `disabled by default` has entity_registry_enabled_default False, and no other row does | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | mismatches=[] | **true** |  |
@@ -84,7 +84,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C78 | `docs/ecl110.md` | the weather anticipation bias applies over the first eight hours | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C79 | `docs/ecl110.md` | the published displace is rounded to a whole number | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
 | C80 | `docs/ecl110.md` | comfort commands +4 °C or your maximum if lower; boost your maximum; off your minimum | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=True measured=True | **true** |  |
-| C81 | `docs/ecl110.md` | both ECL110 sensors are disabled by default and diagnostic | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | [('ECL110 Displace', False, 'diagnostic'), ('ECL110 Effective Displace', False, 'diagnostic')] | **true** |  |
+| C81 | `docs/ecl110.md` | both ECL110 sensors are disabled by default and diagnostic | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | [('Heat-Curve Displace', False, 'diagnostic'), ('Heat-Curve Effective Displace', False, 'diagnostic')] | **true** |  |
 | C82 | `README.md:Removal` | every entry keeps its learners and ledgers in twelve files under .storage/, named | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=['accuracy', 'away', 'boost', 'dhw_draws', 'dhw_legionella', 'dhw_profile', 'energy', 'ledger', 'manual_plan', 'price_model', 'snapshots', 'thermal_learning'] measured=['accuracy', 'away', 'boost', 'dhw_draws', 'dhw_legionella', 'dhw_profile', 'energy', 'ledger', 'manual_plan', 'price_model', 'snapshots', 'thermal_learning'] | **true** |  |
 | C83 | `README.md:Removal` | the count in that sentence is twelve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=12 measured=12 | **true** |  |
 | C84 | `README.md:Removal` | the registered Lovelace resource is /heatpump_optimizer_static/heatpump-optimizer-card.js | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented='/heatpump_optimizer_static/heatpump-optimizer-card.js' measured='/heatpump_optimizer_static/heatpump-optimizer-card.js' | **true** |  |
@@ -111,7 +111,7 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C105 | `docs/automations.md` | the Power Headroom sensor appears once anything bounds the house -- a main fuse OR a capacity tariff -- and a tariff-only install reads 0.0 kW with limit_source='capacity tariff with no peak reference yet' until the month's first metering window closes; with neither it stays unavailable | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | no fuse + capacity tariff enabled -> {'available': True, 'limit_kw': 0.0, 'headroom_kw': 0.0, 'baseline_source': 'planned power only (no meter)', 'limit_source': 'capacity tariff with no peak reference yet'}; fuse only -> available=True; neither -> available=False | **true** |  |
 | C106 | `docs/automations.md` | Power Headroom is min(main fuse, capacity threshold) - current house draw, clamped at zero, in kW | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | fuse 20 A 3-phase -> limit_kw=13.8, headroom_kw=13.8, limit_source='main fuse' | **true** |  |
 | C107 | `README.md + docs/*.md + the card` | every entity id quoted in the documentation is an entity the platforms construct | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 9 distinct ids cited, not constructed=[] | **true** |  |
-| C108 | `README.md + docs/*.md` | every relative link resolves (93 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 93 links, broken=[], of which removed-by-the-export=[] | **true** |  |
+| C108 | `README.md + docs/*.md` | every relative link resolves (98 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 98 links, broken=[], of which removed-by-the-export=[] | **true** |  |
 | C109 | `README.md + docs/how-it-works.md` | the links to docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md resolve | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | finder_wall in tools/audit/prepare_baseline.sh removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md; this tree cannot answer | **unverifiable** | not checkable in the export -- finder_wall removes docs/audit-*.md, dev/archive/audits/audit-*.md and dev/archive/backlog.md |
 | C110 | `README.md + docs/*.md` | every image the documentation embeds exists (21 images) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 21 images, missing=[] | **true** |  |
 | C111 | `README.md + docs/*.md` | every external link answers 200 to a HEAD request (21 links) | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py --links` | not run: pass --links | **unverifiable** | re-run with --links |
diff --git a/dev/governance/config/policy_budgets.json b/dev/governance/config/policy_budgets.json
index 271d260990..e91256e55a 100644
--- a/dev/governance/config/policy_budgets.json
+++ b/dev/governance/config/policy_budgets.json
@@ -80,14 +80,14 @@
     "tools/audit/briefs/orchestrator.md": 295,
     "tools/audit/briefs/root-cause.md": 84,
     "tools/audit/briefs/verifier.md": 39,
-    "dev/governance/roles/architect-planner.md": 85,
+    "dev/governance/roles/architect-planner.md": 89,
     "dev/governance/roles/standing.md": 50,
     "dev/governance/roles/standing-merge.md": 37,
     "dev/governance/roles/standing-dispatch.md": 39,
     "dev/governance/roles/proposal-triage.md": 40,
     "dev/governance/roles/standing-roster.md": 7,
     "dev/governance/roles/standing-tick.md": 6,
-    "dev/governance/roles/plan-review.md": 24,
+    "dev/governance/roles/plan-review.md": 27,
     "dev/governance/dimensions/criteria/D4-criteria.md": 52,
     "dev/governance/dimensions/criteria/D9-criteria.md": 49,
     "dev/governance/dimensions/criteria/D5-criteria.md": 43,
@@ -140,14 +140,14 @@
     "tools/audit/briefs/orchestrator.md": 4251,
     "tools/audit/briefs/root-cause.md": 998,
     "tools/audit/briefs/verifier.md": 612,
-    "dev/governance/roles/architect-planner.md": 1261,
+    "dev/governance/roles/architect-planner.md": 1325,
     "dev/governance/roles/standing.md": 553,
     "dev/governance/roles/standing-merge.md": 507,
     "dev/governance/roles/standing-dispatch.md": 509,
     "dev/governance/roles/proposal-triage.md": 563,
     "dev/governance/roles/standing-roster.md": 92,
     "dev/governance/roles/standing-tick.md": 83,
-    "dev/governance/roles/plan-review.md": 304,
+    "dev/governance/roles/plan-review.md": 360,
     "dev/governance/dimensions/criteria/D4-criteria.md": 656,
     "dev/governance/dimensions/criteria/D9-criteria.md": 641,
     "dev/governance/dimensions/criteria/D5-criteria.md": 546,
diff --git a/dev/governance/roles/architect-planner.md b/dev/governance/roles/architect-planner.md
index 5ab6f8c7f8..da83edb8ff 100644
--- a/dev/governance/roles/architect-planner.md
+++ b/dev/governance/roles/architect-planner.md
@@ -80,5 +80,10 @@ weights. It is met only when every condition holds, whatever dS reads:
 The target binds this plan, never a seat: a seat aims at sounder code and is
 never credited for dS alone (`fixer.md` step 17).
 
+Decision 0018's objective ranks the work and the target is its floor: the
+plan's `objective` block predicts each term, ranks and keys each group and
+pins the projection; `plan_audit.py objective-check` passes before the
+push; its guide holds the grammar.
+
 **You do not** write production code, dispatch seats, edit the scorer, or
 carry a target for any single pull request.
diff --git a/dev/governance/roles/plan-review.md b/dev/governance/roles/plan-review.md
index 488a818e12..e717a46df7 100644
--- a/dev/governance/roles/plan-review.md
+++ b/dev/governance/roles/plan-review.md
@@ -16,8 +16,11 @@ the plan to the owner.
 4. **Check the target's conditions**: admissible end to end, the spread rule,
    holdouts, fitness functions; a plan stopping at the floor with a cheap move
    left over is `revise`.
-5. **Check the time**: re-run the projection; the critical chain and the
-   hot-file order are as stated.
+5. **Check the time and the objective**: re-run `plan_audit.py
+   objective-check` at the plan SHA; the critical chain and the hot-file order
+   are as stated; attack three ranks and three keyed effects in the code, the
+   rank-1 groups with most predicted dS per finding first; read the floor cost
+   against step 4's cheap test.
 6. **Check the ADRs**: each serves a named scenario, its tradeoffs written.
 
 After two `revise` rounds the plan goes to the owner with the open points,
diff --git a/dev/programme/delivery/3663.md b/dev/programme/delivery/3663.md
new file mode 100644
index 0000000000..9430fcd741
--- /dev/null
+++ b/dev/programme/delivery/3663.md
@@ -0,0 +1 @@
+- [#3663](https://github.com/tvofi/heatpump_optimizer/pull/3663) — **merged `8e76c19`**, R11-OWNER-GENERIC-CONTROL-TEXT: r11 owner generic control text.
diff --git a/dev/programme/delivery/3676.md b/dev/programme/delivery/3676.md
new file mode 100644
index 0000000000..10101c8bd6
--- /dev/null
+++ b/dev/programme/delivery/3676.md
@@ -0,0 +1 @@
+- [#3676](https://github.com/tvofi/heatpump_optimizer/pull/3676) — **merged `a1d0b41`**, R11-PRE-PLAN-RENDER: r11 pre plan render.
diff --git a/dev/programme/delivery/3684.md b/dev/programme/delivery/3684.md
new file mode 100644
index 0000000000..c11a7f1fca
--- /dev/null
+++ b/dev/programme/delivery/3684.md
@@ -0,0 +1 @@
+- [#3684](https://github.com/tvofi/heatpump_optimizer/pull/3684) — **merged `b6e52b0`**, R11-RCA-SELFTEST-TABLE-DRIFT: r11 rca selftest table drift.
diff --git a/dev/programme/delivery/3685.md b/dev/programme/delivery/3685.md
new file mode 100644
index 0000000000..abcfd5a7e2
--- /dev/null
+++ b/dev/programme/delivery/3685.md
@@ -0,0 +1 @@
+- [#3685](https://github.com/tvofi/heatpump_optimizer/pull/3685) — **open**, R11-VALVE-REFERENCE: r11 valve reference (R11-VALVE-REFERENCE)
diff --git a/dev/programme/delivery/3697.md b/dev/programme/delivery/3697.md
new file mode 100644
index 0000000000..56e0e140b1
--- /dev/null
+++ b/dev/programme/delivery/3697.md
@@ -0,0 +1 @@
+- [#3697](https://github.com/tvofi/heatpump_optimizer/pull/3697) — **open**, Honest starts and runs, part 3 (R11-OUTSIDE-HONEST-STARTS-RUNS-P3) (R11-OUTSIDE-HONEST-STARTS-RUNS-P3)
diff --git a/dev/programme/delivery/3700.md b/dev/programme/delivery/3700.md
index dd36e8c902..32fa57bcbe 100644
--- a/dev/programme/delivery/3700.md
+++ b/dev/programme/delivery/3700.md
@@ -1 +1 @@
-- [#3700](https://github.com/tvofi/heatpump_optimizer/pull/3700) — **open**, R11-SERVICE-SCHEMA-P2: silent-mode 1.0 resets, legionella max 70
+- [#3700](https://github.com/tvofi/heatpump_optimizer/pull/3700) — **merged `6151223`**, R11-SERVICE-SCHEMA-P2: silent-mode 1.0 resets, legionella max 70.
diff --git a/dev/programme/delivery/3701.md b/dev/programme/delivery/3701.md
new file mode 100644
index 0000000000..01461cda6b
--- /dev/null
+++ b/dev/programme/delivery/3701.md
@@ -0,0 +1 @@
+- [#3701](https://github.com/tvofi/heatpump_optimizer/pull/3701) — **merged `91674d1`**, R11-PRE-HANDOFF-BOOKKEEPING (part 2): r11 pre handoff bookkeeping p2 p2.
diff --git a/dev/programme/delivery/3703.md b/dev/programme/delivery/3703.md
new file mode 100644
index 0000000000..a3d66b339a
--- /dev/null
+++ b/dev/programme/delivery/3703.md
@@ -0,0 +1 @@
+- [#3703](https://github.com/tvofi/heatpump_optimizer/pull/3703) — **merged `e3c7593`**, R11-ARCH-OBJECTIVE: r11 arch objective.
diff --git a/dev/programme/delivery/3704.md b/dev/programme/delivery/3704.md
index 47d65a2096..5a313a89a7 100644
--- a/dev/programme/delivery/3704.md
+++ b/dev/programme/delivery/3704.md
@@ -1 +1 @@
-- [#3704](https://github.com/tvofi/heatpump_optimizer/pull/3704) — **open**, R11-PRE-PRODUCT-READS (part 2): r11 pre product reads p2 (R11-PRE-PRODUCT-READS)
+- [#3704](https://github.com/tvofi/heatpump_optimizer/pull/3704) — **merged `33b1e08`**, R11-PRE-PRODUCT-READS (part 2): r11 pre product reads p2.
diff --git a/dev/programme/delivery/3707.md b/dev/programme/delivery/3707.md
index bf91f00a10..6aa4955c87 100644
--- a/dev/programme/delivery/3707.md
+++ b/dev/programme/delivery/3707.md
@@ -1 +1 @@
-- [#3707](https://github.com/tvofi/heatpump_optimizer/pull/3707) — **open**, R11-HOTFIX-MAIN-SELFTEST-DRIFT: re-record the self-test table from main run 44048908427 (R11-HOTFIX-MAIN-SELFTEST-DRIFT)
+- [#3707](https://github.com/tvofi/heatpump_optimizer/pull/3707) — **merged `5e2ef89`**, R11-HOTFIX-MAIN-SELFTEST-DRIFT: re-record the self-test table from main run 44048908427.
diff --git a/dev/programme/delivery/3710.md b/dev/programme/delivery/3710.md
new file mode 100644
index 0000000000..85aa4a862c
--- /dev/null
+++ b/dev/programme/delivery/3710.md
@@ -0,0 +1 @@
+- [#3710](https://github.com/tvofi/heatpump_optimizer/pull/3710) — **open**, record: delivery rows (autofix)
diff --git a/docs/architecture.md b/docs/architecture.md
index 6f146eb1a1..e0e2b86045 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -182,7 +182,7 @@ custom_components/heatpump_optimizer/
 ├── snapshots.py          # Weekly learner snapshots and the rollback alarm
 ├── learner_progress.py   # Each thermal learner's phase, progress and wait; a day count only to a counting gate
 ├── comfort_learning.py   # Revealed-preference comfort-weight tuning
-├── curve_learning.py     # Standing cool-only bias on the ECL110 heat curve
+├── curve_learning.py     # Standing cool-only bias on the heat-curve displace
 ├── sysid.py              # Active step-response identification
 ├── presets.py            # Building archetypes to thermal parameters
 ├── external_heat.py      # Wood-furnace detection with hysteresis and decay
@@ -204,8 +204,8 @@ custom_components/heatpump_optimizer/
 │                         #   estimate is what the solve prices that switch by
 │                         #   and what orders the legs of a both step the
 │                         #   arbiter serves
-├── heat_curve.py         # The heat-curve displace's outputs: the ECL110 MQTT
-│                         #   topics and an offset number entity
+├── heat_curve.py         # The heat-curve displace's outputs: the MQTT topics
+│                         #   and a number entity, kind offset or persistent
 ├── off_restore.py        # The one owner of the off and unload restore: what
 │                         #   a writer restores when the optimizer lets go
 ├── early_cutoff.py       # Switches a space-heating pump off inside the
diff --git a/docs/automations.md b/docs/automations.md
index 4e39024783..95b39f5962 100644
--- a/docs/automations.md
+++ b/docs/automations.md
@@ -1,6 +1,6 @@
 # Automations
 
-Without a heat pump on/off switch — and without the ECL110 or
+Without a heat pump on/off switch — and without the heat-curve or
 frequency-control paths — the optimizer's plan is published on sensors for
 your own automations to act on ([configuration.md](configuration.md) says
 exactly that where the trade-off is made). The examples below are complete and
diff --git a/docs/configuration.md b/docs/configuration.md
index 9bcd8d1246..ed7cb18556 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -85,7 +85,7 @@ Every picker on this second screen is optional; skip any you do not have. Withou
 |---|---|---|
 | Indoor temperature sensor | none | The real room temperature. Without it the optimizer trusts its own model, which drifts over time — this is the sensor worth finding first. |
 | Outdoor temperature sensor | none | A local thermometer beats the forecast for the current hour. |
-| Heat pump on/off switch | none | A `switch` the optimizer may turn off during expensive hours. In *auto* and *economy* mode it is never switched off less than 10 minutes after it came on, nor on less than 10 minutes after it went off, and a run the plan would end within 10 minutes is not started unless the step heats the tank and the tank needs heat now (below its minimum, or a disinfection hold); a held switch is retried every minute and changes once its 10 minutes have passed. The age is the switch's own, whoever switched it; after a Home Assistant restart it counts from the restart. A boost, the other modes and the measurement experiment are not held. Without it — and without the ECL110 or frequency-control paths — the plan is published on sensors for your own automations to act on ([worked examples](automations.md)). |
+| Heat pump on/off switch | none | A `switch` the optimizer may turn off during expensive hours. In *auto* and *economy* mode it is never switched off less than 10 minutes after it came on, nor on less than 10 minutes after it went off, and a run the plan would end within 10 minutes is not started unless the step heats the tank and the tank needs heat now (below its minimum, or a disinfection hold); a held switch is retried every minute and changes once its 10 minutes have passed. The age is the switch's own, whoever switched it; after a Home Assistant restart it counts from the restart. A boost, the other modes and the measurement experiment are not held. Without it — and without the heat-curve or frequency-control paths — the plan is published on sensors for your own automations to act on ([worked examples](automations.md)). |
 | Solar radiation sensor | none | Irradiance in W/m², the sun on the house now, which the learners read. The plan's later steps take the sun from the weather forecast; the sensor's reading stands in for the whole horizon only when no forecast is available. |
 | Solar irradiance source | Weather entity | `Weather entity` reads irradiance from your weather integration, which often does not publish any. `Open-Meteo` fetches a free forecast for the location below; no account needed. |
 | Solar irradiance location | your Home Assistant home location | The coordinate Open-Meteo is asked about. Only used when the source is Open-Meteo. |
@@ -98,12 +98,12 @@ Every picker on this second screen is optional; skip any you do not have. Withou
 | Pump online | none | Strongly recommended for a cloud-connected pump. On while the pump is actually reachable, which a stale cloud republish cannot tell you on its own. |
 | Fault alarm | none | On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself. |
 
-The heat-curve settings (the Danfoss ECL110 MQTT topics and the offset entity)
-are not asked during setup. Questions only owners of such a controller can
-answer do not belong on everyone's first screen, so they
-live on their own options page, where both MQTT topics ship empty and nothing
-is published or subscribed until a topic is set (see [ecl110.md](ecl110.md));
-an install without an ECL110 never touches the topics.
+The heat-curve settings (the MQTT topics and the entity, for the three ways
+in [heat-curve.md](heat-curve.md)) are not asked during setup. Questions only
+owners of such a controller can answer do not belong on everyone's first
+screen, so they live on their own options page, where both MQTT topics ship
+empty and nothing is published or subscribed until a topic is set; an install
+whose controller takes nothing over MQTT never touches the topics.
 
 ### 3 · The finish menu — Finish setup now?
 
@@ -490,7 +490,7 @@ warmth.
 | How hard to chase low prices | 1.0 | 0.1–10 | Higher moves more heating into cheap hours and allows more swing. |
 | How strictly to hold the temperature | 5.0 | 0.1–20 | The most effective knob you have. It is weighed against the range you allow, so widening that range makes the optimizer bolder. |
 | Recalculate every | 30 min | 10–120, 5 steps | More often reacts quicker and does more work. |
-| Cost of one compressor start | 0.0 | 0–10, 0.05 steps | In the same currency as your prices. Discourages plans that switch on and off repeatedly: above 0, the plan runs the pump in whole runs at or above its minimum power instead of averaging a lower level within a step. The **Compressor Starts** sensor counts *realised* starts and needs a power meter; the plan's own projected start count is not published on any entity. |
+| Cost of one compressor start | 0.0 | 0–10, 0.05 steps | In the same currency as your prices. Discourages plans that switch on and off repeatedly: above 0, the plan runs the pump in whole runs at or above its minimum power instead of averaging a lower level within a step. At 0 on an install that cannot run below its minimum power (it cannot duty-cycle), the plan prices each start at 0.1 instead, so committing the plan to whole runs does not add starts; any value above 0 is used as set. The **Compressor Starts** sensor counts *realised* starts and needs a power meter; the plan's own projected start count is not published on any entity. |
 | Caution with guessed prices | 0.0 | 0.0–2.0, 0.05 steps | Beyond the published horizon prices come from your learned daily shape. This adds a premium proportional to how wrong those guesses have tended to be. 0 trusts them at face value. |
 | Hold a safety margin where the model is unsure | off | on/off | Raises the comfort floor by the model's own expected error at that horizon, capped at 0.8 °C and shrinking as accuracy improves. |
 | Compressor replacement cost | 0 | 0–100 000, 100 steps | What a compressor swap costs including labour, in your price currency. Divided by the rated starts below it prices each realised start. 0 keeps the start counter pure observation. |
@@ -628,8 +628,8 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Minimum lift above the inlet water (`flow_min_lift_k`) | 5 K | 0.5–15 K, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at the plan's lowest power is the measured inlet water plus this (see [Pump duty control](#pump-duty-control)). |
 | Heating flow ceiling (`flow_heat_c`) | 55 °C | 30–70 °C, 0.5 steps | Shown when the unit above is *Flow* or *Return temperature*. The heating value at full planned power, and the highest heating value written while the plan is in charge. A space boost or Boost mode writes the set-point entity's own maximum instead (up to 70 °C), capped by a value here other than 55 °C. A stored value at or below the 25 °C gate is read as 55 °C. |
 | Follow the planned power on the measured draw (`space_setpoint_power_feedback`) | On | on / off | Shown when the unit above is *Flow* or *Return temperature*; acts only when a heat-pump power sensor is configured too. Closes the heating value on the measured draw (see [Pump duty control](#pump-duty-control)). Off writes the inlet plus the lift. |
-| Controller's minimum set-point sensor (`space_setpoint_low_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the lowest value the controller accepts for the set-point entity (a Luxtronik through ha-luxtronik-shi: “Temperature: return target minimum”, input 10104). *Follow the planned power* then never sends a value below it (see [Pump duty control](#pump-duty-control)). Empty changes nothing. |
-| Controller's maximum set-point sensor (`space_setpoint_high_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the controller accepts (a Luxtronik: “Temperature: return limit”, input 10103). *Follow the planned power* then never sends a value above it. Empty changes nothing. |
+| Controller's minimum set-point sensor (`space_setpoint_low_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the lowest value the controller accepts for the set-point entity (for example a Luxtronik through ha-luxtronik-shi: “Temperature: return target minimum”, input 10104). *Follow the planned power* then never sends a value below it (see [Pump duty control](#pump-duty-control)). Empty changes nothing. |
+| Controller's maximum set-point sensor (`space_setpoint_high_limit_entity`) | none | a temperature sensor | Shown when the unit above is *Flow* or *Return temperature*. Optional: the highest value the controller accepts (for example a Luxtronik: “Temperature: return limit”, input 10103). *Follow the planned power* then never sends a value above it. Empty changes nothing. |
 
 ### Power and solar sensors
 
@@ -717,8 +717,8 @@ writes, at every 15-minute plan step:
   fields appear once that unit is saved). Those defaults suit a controller
   that holds its **supply** at the set-point.
 - **For a *Return temperature* entity** — a controller that takes the
-  number as its **return-water** target, as a Luxtronik (alpha innotec,
-  Novelan) through its Smart Home Interface is assumed to — everything above
+  number as its **return-water** target, as, for example, a Luxtronik
+  (alpha innotec, Novelan) through its Smart Home Interface is assumed to — everything above
   applies, with these differences:
   - The values derived from a supply temperature — the 35 °C hold, the
     weather curve and the 25 °C gate — are written 5 K lower (the rated
@@ -748,12 +748,12 @@ writes, at every 15-minute plan step:
     level; check it against the measured frequency and power. Choose the
     ceiling above the highest return you see in normal heating plus the
     lift (otherwise a heating step writes a target below the return, and
-    such a controller presumably stops), and no higher than the controller accepts: a Luxtronik
+    such a controller presumably stops), and no higher than the controller accepts: a Luxtronik, for example,
     clamps the target to its own minimum return target and return limit, so a ceiling above the
     limit is written but not followed. A controller that starts heating only once the target sits
     its hysteresis above the return is not started by a smaller lift;
     it only keeps a running compressor near its minimum. That hysteresis is a setting of the
-    controller, not a fixed 2 K: a Luxtronik accepts 0.5 K at the least, and the start threshold in
+    controller, not a fixed 2 K: a Luxtronik, for example, accepts 0.5 K at the least, and the start threshold in
     effect (the return target less the hysteresis) is input 10107 of its Smart Home Interface, which
     ha-luxtronik-shi publishes as its *Demand border* sensor
     ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)).
@@ -763,8 +763,8 @@ writes, at every 15-minute plan step:
     frequency and power.
   - The integration that exposes the controller must poll it at least
     every 10 minutes and restore its heating mode after a controller
-    restart: a Luxtronik Smart Home Interface drops every value set through
-    it after 600 s without access and after each restart. Any access
+    restart, since a controller can drop what was set through it: a Luxtronik
+    Smart Home Interface, for one, drops every value set through it after 600 s without access and after each restart. Any access
     re-arms those 600 s, a read as much as a write, so polling alone keeps
     a written value; ha-luxtronik-shi polls every 30 s by default and
     offers 10–300 s, and restores what it wrote after a controller restart
@@ -772,7 +772,7 @@ writes, at every 15-minute plan step:
     ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)). A reverted
     set-point is noticed and written again; a reverted heating mode is not
     visible to this integration. No second tool may write the same
-    registers: a Luxtronik then silently discards writes (error 816).
+    registers: a Luxtronik, for one, then silently discards writes (error 816).
   - Downgrading: a version before this option reads *Return temperature* as
     *Indoor temperature* and writes the planned room temperature to the
     entity. Switch the unit back to *Flow temperature* before downgrading.
@@ -794,12 +794,12 @@ writes, at every 15-minute plan step:
   unchanged and start the loop over. Where the controller cuts a written
   value to its own limits, that cut is taken as the run's limit and no
   repair is raised. Preconditions on the controller:
-  - its heating hysteresis is at most the lift (Luxtronik: 0.5 K, its
-    minimum), or the first write of a run does not start a stopped
+  - its heating hysteresis is at most the lift (on a Luxtronik, for
+    example, 0.5 K, its minimum), or the first write of a run does not start a stopped
     compressor — the same limitation as without the loop;
   - its minimum return target sits below the return during the heating
     season, or the loop cannot wind the compressor down past it. A
-    Luxtronik cuts the set-point to its minimum return target (input 10104
+    Luxtronik, for example, cuts the set-point to its minimum return target (input 10104
     of its Smart Home Interface, parameter 979) and its return limit (input
     10103, parameter 87), both of which ha-luxtronik-shi publishes as
     sensors ([the contributor's answers](https://github.com/tvofi/heatpump_optimizer/pull/3372#issuecomment-6756915104)).
@@ -1195,12 +1195,14 @@ reads SEK, that is a label, not a constraint.
 
 ### Heat curve control
 
-For Danfoss ECL110 controllers driven over MQTT, or any controller whose
-heat-curve offset Home Assistant exposes as a `number`. The topics have no
-shipped default: each is exactly what you store, an empty or absent topic
-leaves that arm off, and nothing is published or subscribed until a topic
-is set — an install without an ECL110 never touches these topics. See
-[ecl110.md](ecl110.md) for the full picture.
+For a weather-compensated controller whose heat curve the optimizer shifts,
+three ways: over MQTT topics (a Danfoss ECL110 through an MQTT bridge, for
+example), to a volatile offset `number` entity, or to a stored curve
+parameter. The topics have no shipped default: each is exactly what you
+store, an empty or absent topic leaves that arm off, and nothing is published
+or subscribed until a topic is set — an install whose controller takes
+nothing over MQTT never touches these topics. See
+[heat-curve.md](heat-curve.md) for the full picture.
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
@@ -1213,10 +1215,10 @@ is set — an install without an ECL110 never touches these topics. See
 | Largest upward offset | 20 °C | 0–30, 0.5 steps | How far it may be shifted up when storing cheap heat. |
 | Controller response time | 1.5 h | 0.25–6.0, 0.25 steps | Roughly how long the controller takes to act on a new offset, so the optimizer does not ask for changes faster than the system can follow. |
 | Heat-curve offset entity | *(empty)* | a `number` or `input_number` | The same offset written to an entity instead of, or as well as, MQTT. Kind offset: a whole-curve offset, 0 neutral, that the controller forgets on a restart; turning the optimizer off, or unloading it, writes 0; refused when its own range excludes 0. Kind persistent: a curve setting the controller stores; off and unload write back the value it held before the first write; refused when it reads no value or one outside its own range. Refused when it is an entity the optimizer already writes. |
-| What the entity is | Offset | Offset, Persistent | Offset: a temperature difference, not stored by the controller; prefer it where the controller has one. Persistent: a stored curve setting, displaced from its own value with a daily write cap; see [ecl110.md](ecl110.md#kind-persistent-a-stored-curve-parameter). |
-| Largest offset written to the entity | 3 K | 0.5–5, 0.5 steps | The entity's offset stays within this many kelvin either way, whatever the MQTT range allows. 3 K is an estimate; see [ecl110.md](ecl110.md#without-mqtt-a-number-entity). |
+| What the entity is | Offset | Offset, Persistent | Offset: a temperature difference, not stored by the controller; prefer it where the controller has one. Persistent: a stored curve setting, displaced from its own value with a daily write cap; see [heat-curve.md](heat-curve.md#kind-persistent-a-stored-curve-parameter). |
+| Largest offset written to the entity | 3 K | 0.5–5, 0.5 steps | The entity's offset stays within this many kelvin either way, whatever the MQTT range allows. 3 K is an estimate; see [heat-curve.md](heat-curve.md#without-mqtt-a-number-entity). |
 | Largest displacement of a stored parameter | 3 K | 0.5–5, 0.5 steps | Kind persistent only: the stored setting stays within this many kelvin of its value before the first write. 3 K is an estimate. |
-| Most writes a day to a stored parameter | 12 | 0–48 | Kind persistent only: writes in one local day, the write back on off included, one always kept for it; 0 or 1 writes nothing. 12 rests partly on forum figures and estimates; see [ecl110.md](ecl110.md#kind-persistent-a-stored-curve-parameter). |
+| Most writes a day to a stored parameter | 12 | 0–48 | Kind persistent only: writes in one local day, the write back on off included, one always kept for it; 0 or 1 writes nothing. 12 rests partly on forum figures and estimates; see [heat-curve.md](heat-curve.md#kind-persistent-a-stored-curve-parameter). |
 | Least time between writes to a stored parameter | 60 min | 15–360, 15 steps | Kind persistent only: after a write, the next waits at least this long. 60 min is an estimate of three radiator response times. |
 
 ### Reset to factory defaults
@@ -1234,8 +1236,8 @@ changes, and closing the dialog cancels.
   the optimizer stays connected to the house: every assigned entity, the zone
   and emitter topology (the two-zone switch is written as the settings in force
   imply it), the hot-water tank, valve and wood-furnace layout, the price and
-  solar-forecast sources and the Tibber token, the plant diagram, the ECL110
-  MQTT wiring, the pre-fill device and the main fuse.
+  solar-forecast sources and the Tibber token, the plant diagram, the
+  heat-curve MQTT wiring, the pre-fill device and the main fuse.
 - **Learned values**: every learner starts again from the settings: the heat
   loss scale and lower-floor ratio, the comfort weight, COP, buffer and hot
   water cooling, the hot water profile and draws, defrost, the heat curve, the
@@ -1394,7 +1396,7 @@ would otherwise divide by zero inside the model:
   `dhw_legionella_interval_days` (0.01–60).
 - **Weather:** `wind_sensitivity_factor` (0–1),
   `rain_heat_loss_multiplier` (1–2).
-- **ECL110:** `ecl110_pid_time_constant_hours` (0.01–24),
+- **Heat curve:** `ecl110_pid_time_constant_hours` (0.01–24),
   `ecl110_displace_min` (−30–0), `ecl110_displace_max` (0–30).
 
 **`simulate_plan`** prices a hypothetical comfort choice against the current
@@ -1505,4 +1507,4 @@ file under `.storage/` that holds the rows.
 - [../README.md#removal](../README.md#removal) — removing the integration: what deleting the entry does, and what it leaves behind
 - [how-it-works.md](how-it-works.md) — the mechanisms behind these settings
 - [dashboard-card.md](dashboard-card.md) — the card, its own configuration keys, and the Setup tab
-- [ecl110.md](ecl110.md) — the heat-curve path in full: the Danfoss ECL110 over MQTT, and an offset `number` entity
+- [heat-curve.md](heat-curve.md) — heat-curve control in full, all three ways: MQTT topics (a Danfoss ECL110, for example), an offset `number` entity, and a stored curve parameter
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index f587694b94..5d804356ab 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -260,13 +260,13 @@ space heating and hot water together above 0.1 kW, and that channel's own
 share is above 0.05 kW; a smaller planned draw is idle, not a slow run. When the plan publishes an exact reason for that step the heading says
 *Because* and the list is that reason: the other channel has the capacity,
 the fuse limit caps heating, the plan is waiting for solar, the hour is
-dearer than the hours used, or the temperature is above the floor and the
-plan is coasting. Otherwise the heading says *Likely because*, and each line
+more expensive than the hours used, or the temperature is above the floor
+and the plan is coasting. Otherwise the heading says *Likely because*, and each line
 comes from what the plan sensors publish for that step and nothing else:
 
-- the step's price, when it is among the dearer half of the plan's horizon,
-  with the share of the horizon that is at least as dear and the cheapest
-  price in it;
+- the step's price, when it is among the more expensive half of the plan's
+  horizon, with the share of the horizon that is at least as dear and the
+  cheapest price in it;
 - the last run before it, which the house is coasting on, or when the tank
   was last heated;
 - the next run of that channel, with its time and price;
diff --git a/docs/ecl110.md b/docs/ecl110.md
index 86bec52334..785f1a1361 100644
--- a/docs/ecl110.md
+++ b/docs/ecl110.md
@@ -1,326 +1,7 @@
-# Danfoss ECL110 control over MQTT
+# Moved: heat-curve control
 
-Some heat pumps are driven by a separate weather-compensated controller rather
-than by a switch. The Danfoss ECL110 is the common one here: it runs its own
-heat curve, and the standard way to bias that curve is the manual *displace*
-value — a parallel shift of the whole curve, in degrees.
-
-This page is for installs that have such a controller on MQTT, or a controller
-whose heat-curve offset Home Assistant exposes as a `number` entity
-([Without MQTT](#without-mqtt-a-number-entity)). Everything else in the
-integration works without either.
-
-## What the integration sends
-
-Each optimization produces two outputs for the controller:
-
-- `heat_pump_on` — whether supply should be enabled. A step is ON when the
-  power the plan books for it, space plus hot water together, is above 0.1 kW.
-  A step below the pump's modulation floor is the plan duty-cycling within that
-  step: the plan has already priced that energy as delivered, so supply is
-  enabled and the pump's own thermostat does the cycling. Half the modulation
-  floor answers a different question — whether a *measured* draw means the
-  compressor ran — and is not what this flag uses.
-- `displace_value` — the parallel shift, in °C, that corresponds to the planned
-  power for that step.
-
-The displace schedule is derived from the power schedule, not chosen
-separately: planned power is normalised against the pump's min and max, mapped
-onto the configured displace range, given a weather anticipation bias over the
-first eight hours (wind and rain push it up, expected sun pulls it down), and
-nudged up slightly below 0 °C outdoors. The result is then passed through the
-same first-order lag the controller itself is assumed to have, so the optimizer
-never asks for a change faster than the loop can follow.
-
-Before publishing, the coordinator adds the learned heat-curve bias if curve
-learning is enabled (it may only cool an over-hot curve, never heat, and is
-clamped well inside your configured range), clamps the result to your
-configured range, and rounds to a whole number — the ECL110 takes integers.
-
-The fixed modes do not plan a displace at all: comfort commands +4 °C (or your
-maximum, if that is lower), boost commands your maximum, off your minimum.
-
-The live peak guard can override any of them mid-window: while it is
-suppressing, it publishes the plan's displace minus 2 °C, and re-publishes the
-plan's own value when it releases.
-
-## Topics and payloads
-
-The preferred path is a plain number on the direct set topic:
-
-- `ecl110_displace_set_topic` (no default: empty leaves this arm off)
-
-```text
-4
-```
-
-For a setup that expects JSON, the same command is also published to the
-legacy topic when it is configured:
-
-- `ecl110_command_topic` (no default: empty leaves this arm off)
-
-```json
-{
-  "source": "heatpump_optimizer",
-  "reason": "scheduled_update",
-  "timestamp": "2026-01-01T12:00:00+00:00",
-  "command": {
-    "type": "ecl110_control",
-    "heat_pump_on": true,
-    "displace": 4
-  },
-  "context": {
-    "price": 1.23,
-    "mode": "pre_heat",
-    "pre_heat_urgency": 0.6
-  }
-}
-```
-
-The status topic is subscribed to, not written. Both shapes are accepted: a
-bare number, or a JSON object carrying `displace` (or `command.displace`) and
-optionally `effective_displace`, which overrides the modelled value below.
-
-Publishing goes through Home Assistant's own `mqtt.publish` service, so the
-MQTT integration has to be set up. The topics have no shipped
-default: each one is exactly what you stored, an empty or absent topic leaves
-that arm off, and nothing is published or subscribed until a topic is set —
-so an install without an ECL110 never touches these topics at all.
-
-## Options
-
-All eleven settings live on the options page **Heat curve control**, under
-*Advanced settings*: the eight below, and the three of the
-[offset entity](#without-mqtt-a-number-entity). They are not asked during
-initial setup, because only owners of such a controller can answer them; installs that never open the
-page run no ECL110 surface at all — the topic options below suggest empty and
-a topic only exists once you store one.
-
-| Option | Default | What it is |
-|---|---|---|
-| `ecl110_displace_set_topic` | *(empty)* | Topic the offset is published to, as a plain number |
-| `ecl110_command_topic` | *(empty)* | Legacy JSON command topic |
-| `ecl110_state_topic` | *(empty)* | Topic the controller reports its state on |
-| `ecl110_mqtt_qos` | 1 | MQTT quality of service, 0–2 |
-| `ecl110_mqtt_retain` | off | Retain the last offset on the broker |
-| `ecl110_displace_min` | −20 °C | Largest downward shift allowed, −30 to 0 |
-| `ecl110_displace_max` | +20 °C | Largest upward shift allowed, 0 to +30 |
-| `ecl110_pid_time_constant_hours` | 1.5 h | Roughly how long the controller takes to act on a new offset, 0.25–6 |
-
-The min and max are worth setting to what your curve can actually tolerate.
-They bound both the plan and every override, including the peak guard's.
-
-## Sensors
-
-Two sensors report the ECL110 path. Both follow the MQTT topics and the offset
-entity: with none stored they are **unavailable and disabled by default**, and on an install
-whose topics were configured at setup they are enabled. Both are
-**diagnostic**, so they sit with the other advisories on the device page. On an
-install that adds the topics later, enable them from the integration's device
-page.
-
-| Sensor | Unit | What it shows |
-|---|---|---|
-| ECL110 Displace | °C | The displace the current plan step asks for, falling back to the last value commanded or reported |
-| ECL110 Effective Displace | °C | The modelled shift the controller has actually reached; its attributes carry the legacy command topic and the status topic |
-
-## PI/PID dynamics
-
-The ECL110 does not jump to a new offset. Its manual documents PI-style loop
-dynamics, so a commanded shift arrives gradually, and treating the command as
-if it took effect instantly would make the thermal model expect heat that has
-not been delivered yet.
-
-The integration models this as a first-order lag with the time constant you
-configure: each interval, the effective displace moves a fraction
-`interval / time constant` of the remaining distance toward the command, and
-the result is clamped to the same min/max range. That modelled value is what
-**ECL110 Effective Displace** publishes, and it is replaced by the controller's
-own figure whenever a status payload reports `effective_displace`.
-
-The lag is applied twice on purpose: the optimizer smooths its planned displace
-schedule with it, so the plan only asks for shifts the controller can follow,
-and the coordinator then tracks what the controller has reached, so the model
-prices the heat that has actually arrived rather than the heat requested.
-
-## Without MQTT: a number entity
-
-The same displace can be written to a Home Assistant `number` (or
-`input_number`) that offsets your controller's heat curve, instead of or as
-well as the MQTT topics. Set **Heat-curve offset entity** on the same page.
-Every source of the displace reaches it unchanged: the plan, the fixed modes,
-boost, the peak guard and the learned curve bias. With curve learning on, an
-entity-only install now moves the real pump, where with no topic it moved
-nothing.
-
-**What the entity must be (kind *offset*).**
-A whole-curve offset whose neutral value is 0, which the controller forgets on
-its own restart. Not an absolute curve point, and not a parameter the
-controller stores in its non-volatile memory: those are kind *persistent*
-([below](#kind-persistent-a-stored-curve-parameter)), with its own write budget.
-Prefer *offset* wherever your controller has such an entity. The
-integration cannot tell a volatile entity from a stored one; your choice of
-entity and kind is the declaration. It does check one thing: an entity whose own range
-excludes 0 (for example 20 to 70) is refused at save, and again at every write,
-because it is a curve point, not an offset. An absolute entity that declares a
-range including 0 passes that check, so pick the offset entity deliberately.
-An entity the optimizer already writes for something else (a set-point, the
-valve, the compressor frequency or the mode) is refused too.
-
-**What is written.** The displace integer, the one the MQTT topics carry, as a
-temperature difference in the entity's own unit: kelvin, °C or no unit as is,
-°F times 9/5; any other unit is refused. It is bounded to
-±**Largest offset written to the entity** (default 3 K, 0.5 to 5 K) and to the
-entity's own range; where the entity's range is the narrower one, the value
-saturates and a warning is logged once. The 3 K default and its 5 K ceiling
-come from a web survey of controller documentation (handoff-body/r10-ghc-research
-52f5a442, "Recommended defaults"): ±5 K is the user heating correction a
-Luxtronik controller offers *[documented, a third-party app's docs]*, and 3 K is
-an *[estimate]* between that and the +1 to +2 offset steps an SG-Ready boost
-uses on NIBE *[documented]*. No source states a generic value.
-
-**How often.** Nothing is written while the entity already reads the target
-(within half its step). Each write is recorded: a reading that still differs
-within 90 s proves nothing; after that one more write is sent, and if the
-entity still does not hold it a warning is logged and that value is not sent
-again until the target changes or the reading matches. More than
-2 × 1440 / *optimization interval* writes in 24 hours (96 at the default 30
-minutes) is treated as a loop bug: refused and logged. An entity that is
-missing, unavailable, of another domain or unit, or whose service call
-fails, is not written and the failure is logged once; the MQTT topics are
-published first and are never affected by it. A stale plan is not a reason
-for silence: the peak guard and a mode change publish without checking the
-plan's age, as they do over MQTT.
-
-**Turning it off.** Switching the optimizer to off writes 0 to the entity,
-and so does unloading the integration (a reload after an options change, a
-disable, or Home Assistant stopping), so the curve is back where the
-controller had it. Only a value the optimizer wrote is restored; an install
-that never wrote leaves the entity alone. The MQTT topics get the same:
-once the optimizer has published to them, off and unload publish displace 0
-to each configured topic, retained when retain is on. While off, nothing
-else is written.
-A write the optimizer made before a crash is restored at the next start's
-first off or unload. When Home Assistant is stopping, the controller's own
-integration may already be gone; the 0 is then attempted, the failure logged,
-and the restore kept for the next off or unload. The MQTT topics are not
-written on off.
-
-**Example: a Luxtronik controller with the SHI interface** (alpha innotec,
-Novelan and others). python-luxtronik (Bouni/python-luxtronik at
-`02afea84bd5bf3ee87445de6f2a42b8029983169`) describes the SHI holding
-`heating_offset` as an offset applied to the current return-temperature
-set-point, volatile, and in effect only while the SHI heating mode is
-`offset`; the `luxtronik_shi` integration exposes it as a number in K, −20 to
-20, step 0.5. Measured by one user on one installation (an alpha innotec
-LWDV 91-1/3, 2026-11-07):
-+2 K raised the return target from 27.7 °C to 29.7 °C at that operating point,
-and the same user reports +1 K giving exactly +1 K at another outdoor
-temperature, so on that installation it behaves as a parallel shift. The optimizer does not own the heating mode: after a controller
-restart the mode can fall back to off, the offset reads back as written, and it
-has no effect, which the integration cannot detect. Check the mode after a
-controller restart. The heating-curve parameters themselves (the end point,
-and the setting the controller calls *Parallelverschiebung*) are stored
-parameters: kind *persistent*, not this kind.
-
-## Kind persistent: a stored curve parameter
-
-For a controller with no volatile offset, set **What the entity is** to
-*Persistent* and name the curve setting the controller stores (a foot point,
-a parallel shift, an end point). The options page then shows three more
-settings. Every write lands in the controller's non-volatile memory, which
-wears, so this kind writes far less often than kind *offset*. Prefer kind
-*offset* wherever your controller has a volatile register: on a Luxtronik,
-python-luxtronik's README states that parameter writes go to the controller's
-NAND memory while the SHI offset registers are volatile *[documented]*.
-
-**The baseline.** Before its first write the optimizer reads the entity and
-records that value, with the entity it was read from, in its own store. That
-recorded value is the baseline: every write is the baseline plus the displace,
-as a difference in the entity's unit (°F times 9/5), in whole steps of the
-entity, never more than **Largest displacement of a stored parameter** away
-from the baseline (default 3 K, 0.5 to 5 K) and never outside the entity's own
-range. A restart keeps the baseline, so a value the optimizer wrote is never
-mistaken for yours. The entity must read a value inside its own range when you
-save the page, and at every write; otherwise nothing is written.
-
-**Your own change wins.** If the entity, after a write and its 90 s grace,
-reads neither what the optimizer wrote nor what it read before that write, the
-change is yours: the baseline moves by the same amount, logged once, and the
-optimizer keeps displacing from there. A change that would move the baseline
-outside the entity's own range moves it to that range's edge instead, so the
-write back on off is always a value the entity accepts; the optimizer then
-displaces from that edge, which can write over part of your change. A reading still at the value before the
-write is a write that did not land: it is sent once more, and if it still
-does not land a warning is logged and that value is not sent again until the
-target changes.
-
-**How often.** Nothing is written while the entity already reads the target.
-After a write, the next waits at least **Least time between writes to a stored
-parameter** (default 60 min, 15 min to 6 h), counted on the wall clock so it
-holds across a restart. Writes in one local day, the write back on off
-included, are capped at **Most writes a day to a stored parameter** (default
-12, 0 to 48), and one is always kept back for that write back: a displace that
-would leave none is refused, logged once a day. 0 writes nothing at all, and
-neither does 1: its one write is the one kept back. The
-offset kind's 24-hour loop guard does not apply to this kind; the daily cap
-replaces it.
-
-**Turning it off.** Switching the optimizer off, and every unload (a reload
-after an options change, a disable, Home Assistant stopping), writes the
-baseline back to the entity it was read from, even if you have since named
-another entity or cleared it; the new entity is only read and written after
-that. A write back that fails is logged, kept, and tried again at the next off
-or unload. Removing the integration writes nothing: if a baseline is still
-owed then, a warning names the entity and the value to set by hand.
-
-**Where the defaults come from.** A web survey of controller documentation
-(handoff-body/r10-ghc-research 52f5a442, BODY.md, "Recommended defaults";
-*[documented]*, *[forum]*, *[estimate]* and *[snippet only]* mark the evidence)
-found no manufacturer endurance figure for a generic curve parameter, so these
-rest partly on forum posts and estimates; lower them if your controller's maker
-documents a quota.
-
-- Band, 3 K: Luxtronik's own user heating correction is ±5 K (Homey Luxtronik
-  app *[documented, third party]*), so 5 K is the maximum; NIBE's SG-Ready
-  boost uses +1 to +2 offset steps (NIBE S1256PC manual, p. 44
-  *[documented]*, the step-to-kelvin size *[estimate]*); 3 K between them is an
-  *[estimate]*.
-- Writes a day, 12: the only manufacturer write quota found is Daikin's 7000
-  control commands a year, about 19 a day (Daikin EKMBDXA design guide, quoted
-  on a forum *[forum]*, and the budulinek Daikin-P1P2 gateway's docs
-  *[documented]*); 12 a day for 15 years is 66 % of a 100 000-cycle SLC NAND
-  cell (Micron datasheet *[documented]*); choosing 12 rather than 19 rests on
-  wear levelling *[estimate]*. That is six shift-and-return episodes a day.
-  48 is above Daikin's quota. A NIBE figure of one million writes per
-  position *[forum, snippet only]* and ioBroker write counts *[forum, snippet
-  only]* could not be verified; nothing was found for Vaillant, Stiebel
-  Eltron, Mitsubishi or Panasonic.
-- Dwell, 60 min: about three response times of a radiator system, which warms
-  in 10 to 20 minutes (enpal.de *[forum]*); SG-Ready's 10-minute minimum
-  (gridx.ai *[documented, secondary]*) is below the 15-minute floor; a floor
-  heating system responds in 2 to 3 hours (GWF Stuttgart sheet *[forum]*), so
-  the range reaches 6 h.
-
-**A stored curve parameter is rarely a parallel shift.** Kind *persistent*
-writes the baseline plus the displace, which moves the water target by the
-displace only if the parameter shifts the whole curve. Many controllers' curve
-settings are not shifts. On a Luxtronik (controller firmware V3.92.3, from one
-outside contributor's static analysis of its heating-curve function, checked
-against the targets that contributor's controller reported *[third party]*) the
-two curve parameters are the end point E and the *Parallelverschiebung* F,
-5 to 35 °C, and the target at outdoor temperature T is
-
-    F + (E − 20) × (F − T) / (20 − (T − F) / 2)
-
-before the circuit's minimum and maximum clamp it (the return target for the
-heating circuit, the flow target for a mixing circuit). F is the outdoor
-temperature at which the target equals the outdoor temperature, and moving it
-changes the slope too: it is neither a parallel shift nor a foot point the
-curve turns about. With E = 30, raising F from 22 to 23 °C raises the target
-by 1.15 K at −10 °C, 1.25 K at 6 °C and 1.35 K at 15 °C, so a displace d
-written to F moves the return target by more than d, by an amount that varies
-with the outdoor temperature. On a Luxtronik, use kind *offset* on the SHI
-heating offset, which is the parallel shift (above); kind *persistent* on F
-over-shifts. Whether another controller's stored setting is a true parallel
-shift was not measured here.
+This page is now [Heat-curve control](heat-curve.md). The Danfoss ECL110 over
+MQTT is one of the three ways described there:
+[Over MQTT: topics and payloads](heat-curve.md#over-mqtt-topics-and-payloads).
+The other two are an [offset entity](heat-curve.md#without-mqtt-a-number-entity)
+and a [stored curve parameter](heat-curve.md#kind-persistent-a-stored-curve-parameter).
diff --git a/docs/heat-curve.md b/docs/heat-curve.md
new file mode 100644
index 0000000000..8a3b595b87
--- /dev/null
+++ b/docs/heat-curve.md
@@ -0,0 +1,346 @@
+# Heat-curve control
+
+Many heat pumps are driven by a weather-compensated controller that runs its
+own heat curve, rather than by a switch. The optimizer can bias that curve:
+in cheap hours it shifts the curve up, in expensive ones down. The shift is a
+*displace* — a parallel shift of the whole curve, in degrees.
+
+It reaches your controller in one of three ways. Use the one your controller
+offers; which way, and which entity, is your declaration, because the
+integration does not detect what kind of controller it is talking to:
+
+| Way | Your controller | Details |
+|---|---|---|
+| MQTT topics | takes its curve offset as a number (or a JSON command) on an MQTT topic — for example a Danfoss ECL110 through the [strutsfarm/ecl110](https://github.com/strutsfarm/ecl110) bridge, the controller this way was first built for | [Over MQTT: topics and payloads](#over-mqtt-topics-and-payloads) |
+| An offset entity (kind *offset*) | exposes a volatile whole-curve offset as a Home Assistant `number` entity, 0 neutral — for example a Luxtronik's SHI heating offset | [Without MQTT: a number entity](#without-mqtt-a-number-entity) |
+| A stored curve parameter (kind *persistent*) | has no volatile offset, only a curve setting it stores, exposed as a `number` entity | [Kind persistent: a stored curve parameter](#kind-persistent-a-stored-curve-parameter) |
+
+The MQTT topics and an entity can be used together. Everything else in the
+integration works without any of the three.
+
+## What the integration sends
+
+Each optimization produces two outputs for the controller:
+
+- `heat_pump_on` — whether supply should be enabled. A step is ON when the
+  power the plan books for it, space plus hot water together, is above 0.1 kW.
+  A step below the pump's modulation floor is the plan duty-cycling within that
+  step: the plan has already priced that energy as delivered, so supply is
+  enabled and the pump's own thermostat does the cycling. Half the modulation
+  floor answers a different question — whether a *measured* draw means the
+  compressor ran — and is not what this flag uses.
+- `displace_value` — the parallel shift, in °C, that corresponds to the planned
+  power for that step.
+
+The displace schedule is derived from the power schedule, not chosen
+separately: planned power is normalised against the pump's min and max, mapped
+onto the configured displace range, given a weather anticipation bias over the
+first eight hours (wind and rain push it up, expected sun pulls it down), and
+nudged up slightly below 0 °C outdoors. The result is then passed through the
+same first-order lag the controller itself is assumed to have, so the optimizer
+never asks for a change faster than the loop can follow.
+
+Before publishing, the coordinator adds the learned heat-curve bias if curve
+learning is enabled (it may only cool an over-hot curve, never heat, and is
+clamped well inside your configured range), clamps the result to your
+configured range, and rounds to a whole number. The rounding applies to every
+way, not only the controller that needs it: the ECL110, the first controller
+this was built for, takes integers.
+
+The fixed modes do not plan a displace at all: comfort commands +4 °C (or your
+maximum, if that is lower), boost commands your maximum, off your minimum.
+
+The live peak guard can override any of them mid-window: while it is
+suppressing, it publishes the plan's displace minus 2 °C, and re-publishes the
+plan's own value when it releases.
+
+## Over MQTT: topics and payloads
+
+This way is for a controller that takes its curve offset over MQTT. A Danfoss
+ECL110 does, through the strutsfarm/ecl110 bridge; any controller listening
+for a plain number on a topic can use the first topic below.
+
+The preferred path is a plain number on the direct set topic:
+
+- `ecl110_displace_set_topic` (no default: empty leaves this arm off)
+
+```text
+4
+```
+
+For a setup that expects JSON, the same command is also published to the
+legacy topic when it is configured:
+
+- `ecl110_command_topic` (no default: empty leaves this arm off)
+
+```json
+{
+  "source": "heatpump_optimizer",
+  "reason": "scheduled_update",
+  "timestamp": "2026-01-01T12:00:00+00:00",
+  "command": {
+    "type": "ecl110_control",
+    "heat_pump_on": true,
+    "displace": 4
+  },
+  "context": {
+    "price": 1.23,
+    "mode": "pre_heat",
+    "pre_heat_urgency": 0.6
+  }
+}
+```
+
+The status topic is subscribed to, not written. Both shapes are accepted: a
+bare number, or a JSON object carrying `displace` (or `command.displace`) and
+optionally `effective_displace`, which overrides the modelled value below.
+
+Publishing goes through Home Assistant's own `mqtt.publish` service, so the
+MQTT integration has to be set up. The topics have no shipped
+default: each one is exactly what you stored, an empty or absent topic leaves
+that arm off, and nothing is published or subscribed until a topic is set —
+so an install whose controller takes nothing over MQTT never touches these
+topics at all.
+
+## Options
+
+All eleven settings live on the options page **Heat curve control**, under
+*Advanced settings*: the eight below, and the three of the
+[offset entity](#without-mqtt-a-number-entity). They are not asked during
+initial setup, because only owners of such a controller can answer them; installs that never open the
+page run no heat-curve surface at all — the topic options below suggest empty and
+a topic only exists once you store one.
+
+The `ecl110_` prefix on the option keys is historical, from when MQTT to an
+ECL110 was the only way. The topics, quality of service and retain apply to
+MQTT alone; the displace range and the response time apply to every way.
+
+| Option | Default | What it is |
+|---|---|---|
+| `ecl110_displace_set_topic` | *(empty)* | Topic the offset is published to, as a plain number |
+| `ecl110_command_topic` | *(empty)* | Legacy JSON command topic |
+| `ecl110_state_topic` | *(empty)* | Topic the controller reports its state on |
+| `ecl110_mqtt_qos` | 1 | MQTT quality of service, 0–2 |
+| `ecl110_mqtt_retain` | off | Retain the last offset on the broker |
+| `ecl110_displace_min` | −20 °C | Largest downward shift allowed, −30 to 0 |
+| `ecl110_displace_max` | +20 °C | Largest upward shift allowed, 0 to +30 |
+| `ecl110_pid_time_constant_hours` | 1.5 h | Roughly how long the controller takes to act on a new offset, 0.25–6 |
+
+The min and max are worth setting to what your curve can actually tolerate.
+They bound both the plan and every override, including the peak guard's.
+
+## Sensors
+
+Two sensors report the displace, whichever way it goes out. Both follow the
+MQTT topics and the entity: with none stored they are **unavailable and disabled by default**, and on an install
+whose topics were configured at setup they are enabled. Both are
+**diagnostic**, so they sit with the other advisories on the device page. On an
+install that adds the topics later, enable them from the integration's device
+page.
+
+| Sensor | Unit | What it shows |
+|---|---|---|
+| Heat-Curve Displace | °C | The displace the current plan step asks for, falling back to the last value commanded or reported |
+| Heat-Curve Effective Displace | °C | The modelled shift the controller has actually reached; its attributes carry the legacy command topic and the status topic |
+
+## PI/PID dynamics
+
+A weather-compensated controller does not jump to a new offset. The ECL110's
+manual, for one, documents PI-style loop dynamics, and the integration assumes
+the same of every controller: a commanded shift arrives gradually, and treating
+the command as if it took effect instantly would make the thermal model expect
+heat that has not been delivered yet.
+
+The integration models this as a first-order lag with the time constant you
+configure: each interval, the effective displace moves a fraction
+`interval / time constant` of the remaining distance toward the command, and
+the result is clamped to the same min/max range. That modelled value is what
+**Heat-Curve Effective Displace** publishes, and it is replaced by the controller's
+own figure whenever a status payload reports `effective_displace`.
+
+The lag is applied twice on purpose: the optimizer smooths its planned displace
+schedule with it, so the plan only asks for shifts the controller can follow,
+and the coordinator then tracks what the controller has reached, so the model
+prices the heat that has actually arrived rather than the heat requested.
+
+## Without MQTT: a number entity
+
+The same displace can be written to a Home Assistant `number` (or
+`input_number`) that offsets your controller's heat curve, instead of or as
+well as the MQTT topics. Set **Heat-curve offset entity** on the same page.
+Every source of the displace reaches it unchanged: the plan, the fixed modes,
+boost, the peak guard and the learned curve bias. With curve learning on, an
+entity-only install now moves the real pump, where with no topic it moved
+nothing.
+
+**What the entity must be (kind *offset*).**
+A whole-curve offset whose neutral value is 0, which the controller forgets on
+its own restart. Not an absolute curve point, and not a parameter the
+controller stores in its non-volatile memory: those are kind *persistent*
+([below](#kind-persistent-a-stored-curve-parameter)), with its own write budget.
+Prefer *offset* wherever your controller has such an entity. The
+integration cannot tell a volatile entity from a stored one; your choice of
+entity and kind is the declaration. It does check one thing: an entity whose own range
+excludes 0 (for example 20 to 70) is refused at save, and again at every write,
+because it is a curve point, not an offset. An absolute entity that declares a
+range including 0 passes that check, so pick the offset entity deliberately.
+An entity the optimizer already writes for something else (a set-point, the
+valve, the compressor frequency or the mode) is refused too.
+
+**What is written.** The displace integer, the one the MQTT topics carry, as a
+temperature difference in the entity's own unit: kelvin, °C or no unit as is,
+°F times 9/5; any other unit is refused. It is bounded to
+±**Largest offset written to the entity** (default 3 K, 0.5 to 5 K) and to the
+entity's own range; where the entity's range is the narrower one, the value
+saturates and a warning is logged once. The 3 K default and its 5 K ceiling
+come from a web survey of controller documentation (handoff-body/r10-ghc-research
+52f5a442, "Recommended defaults"): ±5 K is the user heating correction a
+Luxtronik controller offers *[documented, a third-party app's docs]*, and 3 K is
+an *[estimate]* between that and the +1 to +2 offset steps an SG-Ready boost
+uses on NIBE *[documented]*. No source states a generic value.
+
+**How often.** Nothing is written while the entity already reads the target
+(within half its step). Each write is recorded: a reading that still differs
+within 90 s proves nothing; after that one more write is sent, and if the
+entity still does not hold it a warning is logged and that value is not sent
+again until the target changes or the reading matches. More than
+2 × 1440 / *optimization interval* writes in 24 hours (96 at the default 30
+minutes) is treated as a loop bug: refused and logged. An entity that is
+missing, unavailable, of another domain or unit, or whose service call
+fails, is not written and the failure is logged once; the MQTT topics are
+published first and are never affected by it. A stale plan is not a reason
+for silence: the peak guard and a mode change publish without checking the
+plan's age, as they do over MQTT.
+
+**Turning it off.** Switching the optimizer to off writes 0 to the entity,
+and so does unloading the integration (a reload after an options change, a
+disable, or Home Assistant stopping), so the curve is back where the
+controller had it. Only a value the optimizer wrote is restored; an install
+that never wrote leaves the entity alone. The MQTT topics get the same:
+once the optimizer has published to them, off and unload publish displace 0
+to each configured topic, retained when retain is on. While off, nothing
+else is written.
+A write the optimizer made before a crash is restored at the next start's
+first off or unload. When Home Assistant is stopping, the controller's own
+integration may already be gone; the 0 is then attempted, the failure logged,
+and the restore kept for the next off or unload. The MQTT topics are not
+written on off.
+
+**Example: a Luxtronik controller with the SHI interface** (alpha innotec,
+Novelan and others). python-luxtronik (Bouni/python-luxtronik at
+`02afea84bd5bf3ee87445de6f2a42b8029983169`) describes the SHI holding
+`heating_offset` as an offset applied to the current return-temperature
+set-point, volatile, and in effect only while the SHI heating mode is
+`offset`; the `luxtronik_shi` integration exposes it as a number in K, −20 to
+20, step 0.5. Measured by one user on one installation (an alpha innotec
+LWDV 91-1/3, 2026-11-07):
++2 K raised the return target from 27.7 °C to 29.7 °C at that operating point,
+and the same user reports +1 K giving exactly +1 K at another outdoor
+temperature, so on that installation it behaves as a parallel shift. The optimizer does not own the heating mode: after a controller
+restart the mode can fall back to off, the offset reads back as written, and it
+has no effect, which the integration cannot detect. Check the mode after a
+controller restart. The heating-curve parameters themselves (the end point,
+and the setting the controller calls *Parallelverschiebung*) are stored
+parameters: kind *persistent*, not this kind.
+
+## Kind persistent: a stored curve parameter
+
+For a controller with no volatile offset, set **What the entity is** to
+*Persistent* and name the curve setting the controller stores (a foot point,
+a parallel shift, an end point). The options page then shows three more
+settings. Every write lands in the controller's non-volatile memory, which
+wears, so this kind writes far less often than kind *offset*. Prefer kind
+*offset* wherever your controller has a volatile register: on a Luxtronik,
+python-luxtronik's README states that parameter writes go to the controller's
+NAND memory while the SHI offset registers are volatile *[documented]*.
+
+**The baseline.** Before its first write the optimizer reads the entity and
+records that value, with the entity it was read from, in its own store. That
+recorded value is the baseline: every write is the baseline plus the displace,
+as a difference in the entity's unit (°F times 9/5), in whole steps of the
+entity, never more than **Largest displacement of a stored parameter** away
+from the baseline (default 3 K, 0.5 to 5 K) and never outside the entity's own
+range. A restart keeps the baseline, so a value the optimizer wrote is never
+mistaken for yours. The entity must read a value inside its own range when you
+save the page, and at every write; otherwise nothing is written.
+
+**Your own change wins.** If the entity, after a write and its 90 s grace,
+reads neither what the optimizer wrote nor what it read before that write, the
+change is yours: the baseline moves by the same amount, logged once, and the
+optimizer keeps displacing from there. A change that would move the baseline
+outside the entity's own range moves it to that range's edge instead, so the
+write back on off is always a value the entity accepts; the optimizer then
+displaces from that edge, which can write over part of your change. A reading still at the value before the
+write is a write that did not land: it is sent once more, and if it still
+does not land a warning is logged and that value is not sent again until the
+target changes.
+
+**How often.** Nothing is written while the entity already reads the target.
+After a write, the next waits at least **Least time between writes to a stored
+parameter** (default 60 min, 15 min to 6 h), counted on the wall clock so it
+holds across a restart. Writes in one local day, the write back on off
+included, are capped at **Most writes a day to a stored parameter** (default
+12, 0 to 48), and one is always kept back for that write back: a displace that
+would leave none is refused, logged once a day. 0 writes nothing at all, and
+neither does 1: its one write is the one kept back. The
+offset kind's 24-hour loop guard does not apply to this kind; the daily cap
+replaces it.
+
+**Turning it off.** Switching the optimizer off, and every unload (a reload
+after an options change, a disable, Home Assistant stopping), writes the
+baseline back to the entity it was read from, even if you have since named
+another entity or cleared it; the new entity is only read and written after
+that. A write back that fails is logged, kept, and tried again at the next off
+or unload. Removing the integration writes nothing: if a baseline is still
+owed then, a warning names the entity and the value to set by hand.
+
+**Where the defaults come from.** A web survey of controller documentation
+(handoff-body/r10-ghc-research 52f5a442, BODY.md, "Recommended defaults";
+*[documented]*, *[forum]*, *[estimate]* and *[snippet only]* mark the evidence)
+found no manufacturer endurance figure for a generic curve parameter, so these
+rest partly on forum posts and estimates; lower them if your controller's maker
+documents a quota.
+
+- Band, 3 K: Luxtronik's own user heating correction is ±5 K (Homey Luxtronik
+  app *[documented, third party]*), so 5 K is the maximum; NIBE's SG-Ready
+  boost uses +1 to +2 offset steps (NIBE S1256PC manual, p. 44
+  *[documented]*, the step-to-kelvin size *[estimate]*); 3 K between them is an
+  *[estimate]*.
+- Writes a day, 12: the only manufacturer write quota found is Daikin's 7000
+  control commands a year, about 19 a day (Daikin EKMBDXA design guide, quoted
+  on a forum *[forum]*, and the budulinek Daikin-P1P2 gateway's docs
+  *[documented]*); 12 a day for 15 years is 66 % of a 100 000-cycle SLC NAND
+  cell (Micron datasheet *[documented]*); choosing 12 rather than 19 rests on
+  wear levelling *[estimate]*. That is six shift-and-return episodes a day.
+  48 is above Daikin's quota. A NIBE figure of one million writes per
+  position *[forum, snippet only]* and ioBroker write counts *[forum, snippet
+  only]* could not be verified; nothing was found for Vaillant, Stiebel
+  Eltron, Mitsubishi or Panasonic.
+- Dwell, 60 min: about three response times of a radiator system, which warms
+  in 10 to 20 minutes (enpal.de *[forum]*); SG-Ready's 10-minute minimum
+  (gridx.ai *[documented, secondary]*) is below the 15-minute floor; a floor
+  heating system responds in 2 to 3 hours (GWF Stuttgart sheet *[forum]*), so
+  the range reaches 6 h.
+
+**A stored curve parameter is rarely a parallel shift.** Kind *persistent*
+writes the baseline plus the displace, which moves the water target by the
+displace only if the parameter shifts the whole curve. Many controllers' curve
+settings are not shifts. On a Luxtronik (controller firmware V3.92.3, from one
+outside contributor's static analysis of its heating-curve function, checked
+against the targets that contributor's controller reported *[third party]*) the
+two curve parameters are the end point E and the *Parallelverschiebung* F,
+5 to 35 °C, and the target at outdoor temperature T is
+
+    F + (E − 20) × (F − T) / (20 − (T − F) / 2)
+
+before the circuit's minimum and maximum clamp it (the return target for the
+heating circuit, the flow target for a mixing circuit). F is the outdoor
+temperature at which the target equals the outdoor temperature, and moving it
+changes the slope too: it is neither a parallel shift nor a foot point the
+curve turns about. With E = 30, raising F from 22 to 23 °C raises the target
+by 1.15 K at −10 °C, 1.25 K at 6 °C and 1.35 K at 15 °C, so a displace d
+written to F moves the return target by more than d, by an amount that varies
+with the outdoor temperature. On a Luxtronik, use kind *offset* on the SHI
+heating offset, which is the parallel shift (above); kind *persistent* on F
+over-shifts. Whether another controller's stored setting is a true parallel
+shift was not measured here.
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index ab6125273e..ea489c9ee6 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -55,7 +55,7 @@ survivable — a wrong guess about hour 20 is corrected forty times before hour
 sequenceDiagram
     autonumber
     participant C as Coordinator
-    participant P as Prices (Tibber + learned prior)
+    participant P as Prices (Tibber or a price sensor, + learned prior)
     participant W as Weather entity (HA)
     participant S as Your sensors
     participant M as Thermal model
@@ -74,7 +74,7 @@ sequenceDiagram
     O->>O: solve: hot water first (LP + repair),<br/>then space heating around it,<br/>then one co-optimization pass
     O-->>C: space + DHW slot plan
     C->>C: apply manual-plan pins (≤20 h),<br/>safety releases pinned-off slots
-    C->>E: publish plan sensors, switch heat pump,<br/>ECL110 displace / frequency advice
+    C->>E: publish plan sensors, switch heat pump,<br/>heat-curve displace / frequency advice
     Note over C: between plans the peak guard folds power-meter events<br/>and flips a flag (2 agree engage / 2 clear).<br/>It never solves — the next solve only reads the flag
     Note over M: afterwards: compare prediction vs reality,<br/>nudge learned parameters
 ```
@@ -88,8 +88,8 @@ repair passes against the real tank simulation — and space heating is then
 optimized around the fixed DHW blocks by multi-start L-BFGS-B.
 
 Solving them in sequence would let hot water fill the cheapest hours to the
-compressor ceiling and push space heating into dearer ones. Two things prevent
-that:
+compressor ceiling and push space heating into more expensive ones. Two
+things prevent that:
 
 - **A congestion premium** inside the DHW program. Taking compressor capacity
   in a step where space heating also wants it is charged the extra price of
@@ -166,7 +166,9 @@ counts it as the starts it is. With a start priced, or on an install that
 cannot duty-cycle, the solve first plans without the start cost, then commits
 that plan to whole runs at or above the minimum power, at the same energy: a
 step lifted to the minimum is paid for by a step left out. Several such plans
-are scored with the start cost included, and the cheapest ships. (Finding and
+are scored with the start cost included, and the cheapest ships. An install
+that cannot duty-cycle and prices no start is planned at a start price of 0.1,
+so that commit does not ship more starts than the plan it replaced. (Finding and
 method: Bankaifan, pull request 3529.)
 
 ### Weather anticipation is emergent, not a bonus
@@ -746,7 +748,8 @@ zero confidence.
 
 Added per kWh moved through the grid, and increasingly by time of day: several
 Swedish grid companies charge roughly 25 öre/kWh more on winter weekdays 06–22.
-Tibber's price does not include it. Configure it on the Grid costs page — as
+Tibber's price does not include it, and a price sensor includes it only if you
+added it there yourself. Configure it on the Grid costs page — as
 time-of-use rules like `Nov-Mar Mon-Fri 06:00-22:00 = 0.25`, as a flat figure,
 or as a live sensor — and every planned hour is priced at spot *plus* fee, which
 moves load to nights and weekends in winter even when spot alone would not. The
@@ -1450,5 +1453,5 @@ does raising your minimum temperature. Both work.
 - [architecture.md](architecture.md) — module layout and the internal data flow.
 - [dashboard-card.md](dashboard-card.md) — the card, its options, the plan
   editor and the Setup page.
-- [ecl110.md](ecl110.md) — the optional ECL110 MQTT control path.
+- [heat-curve.md](heat-curve.md) — the optional heat-curve control path, three ways: MQTT topics (for example a Danfoss ECL110), an offset entity, a stored curve parameter.
 - [the archive](../dev/archive/backlog.md) — the delivered archive and the open findings.
diff --git a/docs/img/readme/mermaid-how-the-pieces-fit-dark.png b/docs/img/readme/mermaid-how-the-pieces-fit-dark.png
index 58eb532a73..affcf605c6 100644
Binary files a/docs/img/readme/mermaid-how-the-pieces-fit-dark.png and b/docs/img/readme/mermaid-how-the-pieces-fit-dark.png differ
diff --git a/docs/img/readme/mermaid-how-the-pieces-fit.png b/docs/img/readme/mermaid-how-the-pieces-fit.png
index 0bd6e40dc4..cbba858ad9 100644
Binary files a/docs/img/readme/mermaid-how-the-pieces-fit.png and b/docs/img/readme/mermaid-how-the-pieces-fit.png differ
diff --git a/docs/img/readme/mermaid-one-interval-dark.png b/docs/img/readme/mermaid-one-interval-dark.png
index 3a29fe44f3..7d62805d7d 100644
Binary files a/docs/img/readme/mermaid-one-interval-dark.png and b/docs/img/readme/mermaid-one-interval-dark.png differ
diff --git a/docs/img/readme/mermaid-one-interval.png b/docs/img/readme/mermaid-one-interval.png
index be729a5172..d69985147c 100644
Binary files a/docs/img/readme/mermaid-one-interval.png and b/docs/img/readme/mermaid-one-interval.png differ
diff --git a/docs/img/readme/mermaid-setup-flow-dark.png b/docs/img/readme/mermaid-setup-flow-dark.png
index 0b1b423a82..6d09b243bd 100644
Binary files a/docs/img/readme/mermaid-setup-flow-dark.png and b/docs/img/readme/mermaid-setup-flow-dark.png differ
diff --git a/docs/img/readme/mermaid-setup-flow.png b/docs/img/readme/mermaid-setup-flow.png
index 8942fd6532..06f46e4b6d 100644
Binary files a/docs/img/readme/mermaid-setup-flow.png and b/docs/img/readme/mermaid-setup-flow.png differ
diff --git a/docs/img/readme/mermaid_figures.json b/docs/img/readme/mermaid_figures.json
index 15eda0aa8d..2163081bba 100644
--- a/docs/img/readme/mermaid_figures.json
+++ b/docs/img/readme/mermaid_figures.json
@@ -1,28 +1,28 @@
 {
  "generator": "docs/img/readme/render_mermaid.mjs",
- "mermaid": "12.2.0",
+ "mermaid": "12.3.0",
  "source": "README.md",
  "figures": [
   {
    "png": "docs/img/readme/mermaid-how-the-pieces-fit.png",
    "png_dark": "docs/img/readme/mermaid-how-the-pieces-fit-dark.png",
-   "block_sha256": "6ba9cc1e027334c1a7c602a43ea25a455915adba2a0df4899fa54fc0f3ca88ac",
-   "png_sha256": "eb8cdfed82662cbd8b9648613429ef291eac4ffd3dcc8be3baea9cfa7f8eefc2",
-   "png_dark_sha256": "01ce3b59e9f686c2137979c042dcd1b0941c155d0de91fab5544f4d7c78ead9f"
+   "block_sha256": "5cec01a40765b96e51f85a4cd8e65a223162c034c58701cc43acb088668dac57",
+   "png_sha256": "20b98c412361363d5fd1a5dd172f60630f5de432351d3168db0740ad52afb1f6",
+   "png_dark_sha256": "aa93a61d222e40baff87f1fad1bbdb16b252db64c729156f5b73bfb2e040f2c4"
   },
   {
    "png": "docs/img/readme/mermaid-setup-flow.png",
    "png_dark": "docs/img/readme/mermaid-setup-flow-dark.png",
    "block_sha256": "e14dda04c9aa932ef2255be95c1220aacb2475423f59db71972a7d84d51e0e64",
-   "png_sha256": "c73d2f2ef5abb6a37d3ad77c88014afe4597ab7528a1ea63e61379b65dfc9910",
-   "png_dark_sha256": "5db63c422a7f59702ba53a18b5bf4810cb6d022ed3851546ae4778e6e71f0320"
+   "png_sha256": "57b03429cdbed126c15494b4a1515517447730685f9a418ac03fee39a47b43b4",
+   "png_dark_sha256": "3fd4a950793a122073d89662333d1dfb016a7317bbad47077ece1a0041e482d5"
   },
   {
    "png": "docs/img/readme/mermaid-one-interval.png",
    "png_dark": "docs/img/readme/mermaid-one-interval-dark.png",
-   "block_sha256": "bb15e14e25b60cfea3092931d189455da33c117b2fb86f50be0c3ed56287b30c",
-   "png_sha256": "07d112b5c02d8b89feee1aa36f1b4d0c6b27618ee0bbdbbab1d3f4b81dac4a80",
-   "png_dark_sha256": "aba7cb5fe671636c480c0b8de9d36afed3d33b72f224a0fa9fb0297e5738bdb7"
+   "block_sha256": "a9e8fdb9d6f7956aff52a9a123766d95cdbdce1764536b2edf050447f088429a",
+   "png_sha256": "5efa80ae8c2358b86510bc67f9b1d3f3603a8c5a1adf9b8ad3bafa53afd10b84",
+   "png_dark_sha256": "e3cefd8a1dbd3b885586cc07b3444a9b2180ec778c8853a6636233bde308537e"
   }
  ]
 }
diff --git a/docs/index.html b/docs/index.html
index 5ef7433080..e3d2d8b420 100644
--- a/docs/index.html
+++ b/docs/index.html
@@ -251,7 +251,7 @@ pre.yaml .k { color: var(--accent) } pre.yaml .c { color: var(--ink-2) }
 .cp .pp > div { padding: 14px 18px 2px 0; display: grid; gap: 4px; align-content: start }
 .cp .pp > div + div { padding-left: 18px; border-left: 1px solid var(--line) }
 .cp .pp .one { grid-column: 1 / -1 }
-.cp:has(#cp1:checked) .p1, .cp:has(#cp2:checked) .p2, .cp:has(#cp3:checked) .p3, .cp:has(#cp0:checked) .p0 { display: grid }
+.cp:has(#cp1:checked) .p1, .cp:has(#cp2:checked) .p2, .cp:has(#cp4:checked) .p4, .cp:has(#cp5:checked) .p5, .cp:has(#cp3:checked) .p3, .cp:has(#cp0:checked) .p0 { display: grid }
 @supports not selector(:has(*)) { .cp .pp { display: grid; margin-top: 8px } }
 @media (max-width: 640px) { .cp .pp { grid-template-columns: 1fr } .cp .pp > div + div { padding-left: 0; border-left: 0; border-top: 1px solid var(--line) } }
 /* each answer's own name, shown only where every answer shows at once */
@@ -414,7 +414,7 @@ footer a { padding-block: 9px }
       </div></li>
       <li class="st" data-step="4"><div class="in">
         <h3 data-copy><span class="n" aria-hidden="true">4</span>Act</h3>
-        <p class="q" data-src="README.md#how-it-works">Publish plan sensors, switch the heat pump, ECL110 displace / frequency advice</p>
+        <p class="q" data-src="README.md#how-it-works">Publish plan sensors, switch the heat pump, heat-curve displace / frequency advice</p>
         <p data-src="README.md#known-limitations">The plan is re-solved once per optimization interval — 30 minutes by default — and holds until the next solve.</p>
       </div></li>
       <li class="st" data-step="5"><div class="in">
@@ -484,7 +484,7 @@ footer a { padding-block: 9px }
       <p>The heat-loss scale, tank cooling rates, the COP curve and its defrost derate, the solar aperture, internal gains, how the loss splits between floors, your hot-water draw statistics, your revealed comfort preference, and a cool-only heat-curve correction are all estimated from your own house. Every learner is snapshotted weekly (the last eight are kept), and a drift watchdog can roll them back to the last healthy snapshot.</p></article>
     <article class="feat" data-src="README.md#what-it-does"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg></span>
       <h3 data-feature>Knows what your electricity actually costs.</h3>
-      <p>Tibber spot prices, time-of-use grid transfer fees, the monthly capacity (effekt) tariff and its billing clock, PV self-consumption priced at what consuming actually costs you, and a learned diurnal price prior for the part of the horizon that has not been published yet. A live peak guard and a main-fuse headroom advisor act inside the metering window the plan never saw, and a contract comparison settles the month three ways so you can see what your tariff choice is worth.</p></article>
+      <p>Spot prices from Tibber or a price sensor, time-of-use grid transfer fees, the monthly capacity (effekt) tariff and its billing clock, PV self-consumption priced at what consuming actually costs you, and a learned diurnal price prior for the part of the horizon that has not been published yet. A live peak guard and a main-fuse headroom advisor act inside the metering window the plan never saw, and a contract comparison settles the month three ways so you can see what your tariff choice is worth.</p></article>
     <article class="feat" data-src="README.md#what-it-does"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4v6a4 4 0 0 0 4 4h8a4 4 0 0 1 4 4v2"/><circle cx="4" cy="4" r="1.5"/><circle cx="20" cy="20" r="1.5"/></svg></span>
       <h3 data-feature>Handles real plumbing.</h3>
       <p>A mixing valve is what lets a buffer tank store anything, so it is modelled explicitly. A wood furnace tank is a store of its own, drawn wood-first while it is usable, with an optional hot-water inlet coil. Your hydronic layout is picked from a catalog of drawn arrangements rather than described in prose, and circulation pumps — the hot-water loop and the space pump — are scheduled instead of left running.</p></article>
@@ -517,14 +517,18 @@ footer a { padding-block: 9px }
     <fieldset><legend><span class="eyebrow">Control path</span><span data-copy>How is your heat pump controlled?</span></legend>
       <div class="opts">
         <label><input type="radio" name="cp" id="cp1" checked>On/off switch</label>
-        <label><input type="radio" name="cp" id="cp2">ECL110 heat curve</label>
+        <label><input type="radio" name="cp" id="cp2">Heat curve, over MQTT</label>
+        <label><input type="radio" name="cp" id="cp4">Heat curve, offset entity</label>
+        <label><input type="radio" name="cp" id="cp5">Heat curve, stored parameter</label>
         <label><input type="radio" name="cp" id="cp3">Compressor frequency</label>
         <label data-copy><input type="radio" name="cp" id="cp0">None of these</label>
       </div>
     </fieldset>
     <div aria-live="polite">
       <div class="pp p1"><h3 class="pph">On/off switch</h3><div><span class="eyebrow">You provide</span><p>a switch that turns the heat pump on and off</p></div><div><span class="eyebrow">The optimizer writes</span><p>may turn it off during expensive hours</p></div></div>
-      <div class="pp p2"><h3 class="pph">ECL110 heat curve</h3><div><span class="eyebrow">You provide</span><p>a Danfoss ECL110-compatible weather-compensated controller, reachable over MQTT</p></div><div><span class="eyebrow">The optimizer writes</span><p>a heat-pump on/off decision and an integer parallel shift (displace) onto the controller's own heat curve</p></div></div>
+      <div class="pp p2"><h3 class="pph">Heat curve, over MQTT</h3><div><span class="eyebrow">You provide</span><p>a weather-compensated controller that takes its curve offset over MQTT (for example a Danfoss ECL110 through an MQTT bridge)</p></div><div><span class="eyebrow">The optimizer writes</span><p>a heat-pump on/off decision and an integer parallel shift (displace) onto the controller's own heat curve</p></div></div>
+      <div class="pp p4"><h3 class="pph">Heat curve, offset entity</h3><div><span class="eyebrow">You provide</span><p>a controller whose volatile whole-curve offset is a number entity (for example a Luxtronik SHI heating offset)</p></div><div><span class="eyebrow">The optimizer writes</span><p>the same displace as a temperature difference via number.set_value, bounded to ±3 K by default; 0 again when the optimizer is turned off or unloaded</p></div></div>
+      <div class="pp p5"><h3 class="pph">Heat curve, stored parameter</h3><div><span class="eyebrow">You provide</span><p>a controller with no volatile offset, whose stored curve setting is a number entity (kind persistent)</p></div><div><span class="eyebrow">The optimizer writes</span><p>its value before the first write plus the displace, within ±3 K and at most 12 writes a day by default; that value written back when the optimizer is turned off or unloaded</p></div></div>
       <div class="pp p3"><h3 class="pph">Compressor frequency</h3><div><span class="eyebrow">You provide</span><p>the compressor frequency exposed as a number entity (typically from Modbus or ESPHome)</p></div><div><span class="eyebrow">The optimizer writes</span><p>the recommended frequency via number.set_value — but only once you switch the mode to Control</p></div></div>
       <div class="pp p0"><h3 class="pph" data-copy>None of these</h3><div class="one"><span class="eyebrow" data-copy>With none of them</span><p>Each path is optional, the three are independent of each other, and with none of them configured “the plan is published on sensors for your own automations to act on”</p></div></div>
     </div>
@@ -597,7 +601,7 @@ footer a { padding-block: 9px }
     <a class="doc" data-doc="docs/dashboard-card.md" href="dashboard-card.html"><b>docs/dashboard-card.md</b><span>The card: options, interactions, editing limits</span></a>
     <a class="doc" data-doc="docs/automations.md" href="automations.html"><b>docs/automations.md</b><span>Complete automation examples using only the entities and services the integration creates</span></a>
     <a class="doc" data-doc="docs/architecture.md" href="architecture.html"><b>docs/architecture.md</b><span>Module map and how a plan is made, for anyone reading or changing the code</span></a>
-    <a class="doc" data-doc="docs/ecl110.md" href="ecl110.html"><b>docs/ecl110.md</b><span>ECL110 MQTT control</span></a>
+    <a class="doc" data-doc="docs/heat-curve.md" href="heat-curve.html"><b>docs/heat-curve.md</b><span>Heat-curve control, three ways: MQTT topics (for example a Danfoss ECL110), an offset entity, a stored curve parameter</span></a>
     <a class="doc" data-doc="DISCLAIMER.md" href="disclaimer.html"><b>DISCLAIMER.md</b><span>The full disclaimer</span></a>
   </div>
 </section>
diff --git a/docs/setup.md b/docs/setup.md
index 1ed4c1e750..0faf918229 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -42,6 +42,15 @@ Have two things to hand:
 Everything else — indoor and outdoor thermometers, tank probes, a power
 meter — is optional and can be pointed at later from the options pages.
 
+So is how the optimizer acts on the heat pump. The on/off switch is a picker on
+[Screen 2](#screen-2--optional-sensors); heat-curve control and compressor
+frequency control are not asked during setup and are set later from the
+options pages. Heat-curve control shifts your controller's own heat curve one
+of three ways: over MQTT topics (a Danfoss ECL110 through an MQTT bridge, for
+example), to an offset `number` entity, or to a curve setting the controller
+stores — see [heat-curve.md](heat-curve.md). With none of these, the plan is
+published on sensors for your own automations to act on.
+
 ## Adding the integration
 
 **Settings → Devices & services → Add integration → Heat Pump Cost
diff --git a/tests/card.mjs b/tests/card.mjs
index 4fdf7cdbd7..2248a847b8 100644
--- a/tests/card.mjs
+++ b/tests/card.mjs
@@ -816,7 +816,7 @@ check("an unknown reason code still shows something",
   check("UX-1 the explanation names the step's own quarter hour",
     dear.includes(`${clk(45)}\u2013${clk(60)}`), dear);
   check("UX-1 a dear idle step gives its price rank within the horizon",
-    dear.includes("3.00 SEK/kWh") && dear.includes("dearest 25 %") &&
+    dear.includes("3.00 SEK/kWh") && dear.includes("most expensive 25 %") &&
       dear.includes("cheapest 0.50"), dear);
   check("UX-1 it names the run it coasts on and the next run",
     dear.includes(`${clk(0)}\u2013${clk(30)}`) &&
@@ -829,14 +829,14 @@ check("an unknown reason code still shows something",
   check("UX-1 both channels idle share one block and one price line",
     (both.match(/class="tt-why"/g) || []).length === 1 &&
       /Space heating and hot water off/.test(both) &&
-      (both.match(/dearest/g) || []).length === 1 &&
+      (both.match(/most expensive/g) || []).length === 1 &&
       /next heating run/.test(both) &&
       /tank was heated/.test(both), both);
   check("UX-1 nothing is claimed the published fields cannot show",
     !/floor|fuse/i.test(dear), dear);
   const cheap = idleWhyHtml([row("space_power", 2, 0, "idle")], ctx);
   check("UX-1 a step in the cheaper half claims no price reason",
-    /Likely because/.test(cheap) && !/dearest/.test(cheap), cheap);
+    /Likely because/.test(cheap) && !/most expensive/.test(cheap), cheap);
   check("UX-1 an active step is not explained here",
     idleWhyHtml([row("space_power", 0, 2, "cheap_price")], ctx) === "");
   // A DHW step classified off the DHW path publishes no reason at all, so
@@ -862,7 +862,7 @@ check("an unknown reason code still shows something",
   const fused = idleWhyHtml([row("space_power", 3, 0, "idle_fuse")], ctx);
   check("UX-5 a published sub-code says because and replaces the inferred lines",
     /Because:/.test(fused) && !/Likely because/.test(fused) &&
-      /fuse limit caps heating/.test(fused) && !/dearest/.test(fused), fused);
+      /fuse limit caps heating/.test(fused) && !/most expensive/.test(fused), fused);
   check("UX-5 an idle step with no sub-code still says likely because",
     /Likely because/.test(dear) && !/Because:/.test(dear));
   check("UX-5 an idle sub-code is not also a reason label",
diff --git a/tests/closure.py b/tests/closure.py
index 3793f2c531..936bd297fb 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -708,6 +708,7 @@ INERT_EXCEPT = (
     # dependency, not inert prose, whatever directory it lives in.
     "docs/dashboard-card.md",
     "docs/ecl110.md",
+    "docs/heat-curve.md",
     "docs/how-it-works.md",
     "docs/setup.md",
     # R10-OUTSIDE-CONTRIBUTOR-CYCLE: the contributor guide is a reader doc
diff --git a/tests/closures.json b/tests/closures.json
index 9d112db74b..ce28e1a73f 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1354,6 +1354,7 @@
    "docs/configuration.md",
    "docs/dashboard-card.md",
    "docs/ecl110.md",
+   "docs/heat-curve.md",
    "docs/how-it-works.md",
    "docs/img/brand/coffee.svg",
    "docs/img/card/advisor-dark.png",
@@ -3336,6 +3337,7 @@
    "docs/configuration.md",
    "docs/dashboard-card.md",
    "docs/ecl110.md",
+   "docs/heat-curve.md",
    "docs/how-it-works.md",
    "docs/setup.md",
    "hacs.json",
@@ -3521,7 +3523,7 @@
    "docs/automations.md",
    "docs/configuration.md",
    "docs/dashboard-card.md",
-   "docs/ecl110.md",
+   "docs/heat-curve.md",
    "docs/how-it-works.md",
    "docs/setup.md",
    "tests/md_tables.mjs",
@@ -4585,7 +4587,9 @@
    "dev/audit/harnesses/r11_owner_criteria.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
+   "dev/audit/harnesses/r11_selftest_static_edge.py",
    "dev/audit/harnesses/r11_toolchain_mutants.py",
+   "dev/audit/harnesses/r11_why_hover_fit.mjs",
    "dev/audit/harnesses/r9_ci2b_closures_merge.py",
    "dev/audit/harnesses/r9_dbg2_selftest_price.py",
    "dev/audit/harnesses/r9_fr3_family_consumer.mjs",
@@ -4609,6 +4613,7 @@
    "dev/audit/harnesses/ux5_idle_codes.py",
    "dev/audit/harnesses/ux5_idle_codes_sites.py",
    "dev/audit/harnesses/ux9_flow_unit_guard.py",
+   "dev/audit/harnesses/vendor_text_census.py",
    "dev/audit/rounds/round10/D0/leads/tail_floor_own_bounds.py",
    "dev/audit/rounds/round10/D0/s1/race.py",
    "dev/audit/rounds/round10/D0/s2/ftol_race.py",
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 9b94ebbad1..bcbb4478f6 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -2804,6 +2804,8 @@ def check_product_page() -> None:
 # building nothing. The pages are then scanned for a third-party request.
 
 SITE_BUILD = ROOT / "tools" / "site" / "build_docs.mjs"
+# Old document path -> its new one; both addresses must resolve (build_docs.mjs's MOVED is the site half).
+MOVED_PAGES = {"docs/ecl110.md": "docs/heat-curve.md"}
 SITE_CHART = ROOT / "tools" / "site" / "day_chart.mjs"
 _BUILD_CACHE: dict[str, dict] = {}
 
@@ -2816,7 +2818,7 @@ def docs_build(root: pathlib.Path = ROOT) -> dict:
     key = str(root)
     if key in _BUILD_CACHE:
         return _BUILD_CACHE[key]
-    res: dict = {"rc": None, "fails": [], "stats": "", "pages": {}, "html": {}}
+    res: dict = {"rc": None, "fails": [], "stats": "", "pages": {}, "html": {}, "moved": {}}
     if not SITE_BUILD.is_file():
         res["fails"] = [f"{str(SITE_BUILD).removeprefix(str(ROOT) + os.sep)} does not exist"]
     else:
@@ -2839,6 +2841,8 @@ def docs_build(root: pathlib.Path = ROOT) -> dict:
                 if man.is_file():
                     res["pages"] = {b["src"]: b["out"] for b in json.loads(man.read_text())["built"]}
                     res["html"] = {b["out"]: (out / b["out"]).read_text() for b in json.loads(man.read_text())["built"]}
+                    res["moved"] = {m["src"]: (m["to"], (out / m["out"]).read_text())
+                                    for m in json.loads(man.read_text()).get("moved", [])}
     _BUILD_CACHE[key] = res
     return res
 
@@ -2873,6 +2877,17 @@ def check_docs_subpages() -> None:
     rows = {os.path.normpath(r) for r in re.findall(r"^\|\s*\[[^\]]+\]\(([^)#]+\.md)\)", _site_sections(README).get("documentation", ""), flags=re.M)}
     missing = sorted((rows | {"README.md"}) - set(b["pages"]))
     R.check("every README Documentation row is a built page", not missing, ", ".join(missing))
+    # A renamed page keeps its old address (R11-OWNER-GENERIC-CONTROL-TEXT): on GitHub the old file stays as a
+    # pointer to the new one, and on the site the build writes the old page name as a redirect to the new page.
+    for old, new in MOVED_PAGES.items():
+        to, page = b["moved"].get(old, ("", ""))
+        stub = (ROOT / old).read_text() if (ROOT / old).is_file() else ""
+        # The meta refresh drops the fragment; only the script line keeps it, so a deep link still lands.
+        keeps = f"location.replace({json.dumps(to)} + location.hash)" in page
+        R.check(f"{old} still resolves: a pointer to {new} in the tree, a redirect to its page on the site",
+                to == b["pages"].get(new) and f'url={to}"' in page and keeps and f"]({os.path.basename(new)})" in stub,
+                f"site redirect to {to or 'nothing'}, fragment kept: {keeps}; "
+                f"the in-tree file links {new}: {f']({os.path.basename(new)})' in stub}")
     bad = [f"{n}: {m}" for n, h in sorted(b["html"].items()) for _, m in subpage_findings(h)]
     R.check("no built page requests anything from a third party", bool(b["html"]) and not bad,
             "; ".join(bad[:4]) + (f" (+{len(bad) - 4})" if len(bad) > 4 else "") or "no page built")
@@ -3272,7 +3287,7 @@ def check_image_dimensions() -> None:
 WIRING_DOCS = ("docs/architecture.md", "README.md", "dev/README.md")
 # The user pages R10-USER-DOCS-FINAL drafts and R10-USER-DOCS-VERIFY re-checks. README.md is in both sets.
 USER_PAGES = ("README.md", "docs/setup.md", "docs/configuration.md", "docs/how-it-works.md", "docs/automations.md",
-              "docs/dashboard-card.md", "docs/ecl110.md")
+              "docs/dashboard-card.md", "docs/heat-curve.md")
 _COMMENT = re.compile(r"<!--.*?-->", re.S)
 # (e) reads every reader doc that draws a mermaid block, plus the onboarding.
 MERMAID_STYLE_DOCS = ("README.md", "docs/architecture.md", "docs/how-it-works.md", "docs/configuration.md",
diff --git a/tests/entities.py b/tests/entities.py
index 0c91347c82..378b5f9155 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -6712,9 +6712,9 @@ R.check(
 # Two the audit brief flagged and this PR deliberately leaves alone, pinned so
 # a future "consistency" pass does not add a device class to either.
 R.check(
-    "ECL110 Displace stays bare: it is a parallel shift, not a temperature",
-    getattr(by_name["ECL110 Displace"], "_attr_device_class", None) is None
-    and by_name["ECL110 Displace"]._attr_native_unit_of_measurement == "°C",
+    "Heat-Curve Displace stays bare: it is a parallel shift, not a temperature",
+    getattr(by_name["Heat-Curve Displace"], "_attr_device_class", None) is None
+    and by_name["Heat-Curve Displace"]._attr_native_unit_of_measurement == "°C",
     "a TEMPERATURE device class would have HA convert a delta as an absolute",
 )
 R.check(
diff --git a/tests/features.py b/tests/features.py
index 777038b31e..f0d651526d 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -11282,12 +11282,14 @@ _ua_sz = (
     _p_sz.max_electrical_power * _p_sz.cop_nominal_floored
     / _p_sz.emitter_design_delta_t_floored
 )
-_fs_sz = _mv.flow_setpoint(
-    target_temp=23.0, outdoor_temp=-5.0,
-    heat_loss_coefficient=_m_sz.effective_heat_loss_coefficient(
-        _p_sz.heat_loss_coefficient, 0.0, 0.0
-    ),
-    emitter_ua=_ua_sz,
+# The plant's own curve (R11-VALVE-REFERENCE: the slab in series, the gains
+# offset), read rather than re-derived: this check pins the energy balance.
+from heatpump_optimizer.thermal_model import _valve_flow_set as _vfs_sz  # noqa: E402
+
+_fs_sz = _vfs_sz(
+    _p_sz, None, -5.0,
+    _m_sz.effective_heat_loss_coefficient(_p_sz.heat_loss_coefficient, 0.0, 0.0),
+    _ua_sz,
 )
 _q_sz = _mv.emitter_delivery(mix_temp=min(50.0, _fs_sz), zone_temp=25.0, ua=_ua_sz)
 _stand_sz = _p_sz.buffer_tank_heat_loss_coefficient * (50.0 - 20.0)
@@ -11428,7 +11430,9 @@ def _zoned_store_capabilities(two_zone):
     _on, _off = ThermalModel(_zp), ThermalModel(_zq)
     _valved = _on.simulate_step(_zs(22.0, 60.0), 4.0, -5.0, dt_hours=0.25)
     _bare = _off.simulate_step(_zs(22.0, 60.0), 4.0, -5.0, dt_hours=0.25)
-    _on.simulate_step(_zs(25.0, 69.5), 5.0, -5.0, dt_hours=0.25)
+    # The cap arm's slab sits near the single-zone curve (31.2 C here since
+    # R11-VALVE-REFERENCE), so the draw stays below what the pump puts in.
+    _on.simulate_step(_zs(30.0, 69.5), 5.0, -5.0, dt_hours=0.25)
     _zopt = _StoreOpt(ThermalModel(_zp), _StoreCfg(
         horizon_hours=24, time_step_minutes=15,
         target_temp=21.0, min_temp=17.0, max_temp=23.0,
@@ -12148,12 +12152,20 @@ def _cg_rounds(moving):
     return runs
 
 
-_cg_still = _cg_rounds(False) if _ct_p is not None else []
+# The converging arm runs under a raised cap, so its rounds end because the
+# plan stopped moving, never because the cap ran out: on this fixture the
+# first exchange settles on its fourth build (R11-VALVE-REFERENCE's curve).
+_cg_round_cap = _optmod._COMBI_EXCHANGE_ROUNDS
+_optmod._COMBI_EXCHANGE_ROUNDS = 8
+try:
+    _cg_still = _cg_rounds(False) if _ct_p is not None else []
+finally:
+    _optmod._COMBI_EXCHANGE_ROUNDS = _cg_round_cap
 _cg_moving = _cg_rounds(True) if _ct_p is not None else []
 R.check(
-    "combi flux exchange: a plan that stops moving ends the rounds before the cap; one still "
+    "combi flux exchange: a plan that stops moving ends the rounds before a raised cap; one still "
     "moving is published after exactly four plan builds",
-    bool(_cg_still) and all(0 < n < 4 for n in _cg_still)
+    _cg_round_cap == 4 and bool(_cg_still) and all(0 < n < 8 for n in _cg_still)
     and bool(_cg_moving) and all(n == 4 for n in _cg_moving),
     f"builds per exchange: converging {_cg_still}, moving {_cg_moving}",
 )
@@ -47503,7 +47515,7 @@ _sb_meta = _sb_led.months["2026-02"]["meta"][_SB_META]
 R.check(
     "a month's first savings booking stamps the reference in force, once",
     # The literal is the persisted stamp this release writes: a bump is deliberate.
-    _sb_meta == {"sum": 3.0, "count": 1} and _SB_NOW == 3 and _sb_row["old_basis"] is False
+    _sb_meta == {"sum": 4.0, "count": 1} and _SB_NOW == 4 and _sb_row["old_basis"] is False
     and _sb_row["savings_sek"] is not None and _sb_row["savings_pct"] is not None,
     repr((_sb_meta, _sb_row)),
 )
@@ -47524,9 +47536,11 @@ R.check(
 )
 # A stamp 2.0 is what v7.1.17 wrote, before pull request 3587 held a valve-limited
 # two-zone reference at the valve top: a month it opened mixes two references
-# once it books on under this code. A stamp 3.0, this release's, keeps its saving.
+# once it books on under this code. A stamp 3.0 held a single-zone valved house
+# short of its setpoint, before R11-VALVE-REFERENCE's curve reached it. A stamp
+# 4.0, this release's, keeps its saving.
 _sb_by_stamp = {}
-for _sb_stamp in (2.0, 3.0):
+for _sb_stamp in (2.0, 3.0, 4.0):
     _sb_s = _sb_copy.deepcopy(_sb_led.as_dict())
     _sb_s["months"]["2026-02"]["meta"][_SB_META] = {"sum": _sb_stamp, "count": 1}
     _sb_s_led = _SavLedger.from_dict(_sb_s)
@@ -47542,11 +47556,19 @@ R.check(
 )
 _sb_v3_row, _sb_v3_meta = _sb_by_stamp[3.0]
 R.check(
-    "a month stamped 3, the reference in force, keeps stating its saving as it books on",
-    _sb_v3_row["old_basis"] is False and _sb_v3_row["savings_sek"] is not None
-    and _sb_v3_row["savings_pct"] is not None and _sb_v3_meta == {"sum": 3.0, "count": 1},
+    "a month stamped 3, booked before the single-zone valve reached its setpoint, states no saving after the change",
+    _sb_v3_row["old_basis"] is True and _sb_v3_row["savings_sek"] is None
+    and _sb_v3_row["savings_pct"] is None and _sb_v3_row["baseline_sek"] is not None
+    and _sb_v3_row["actual_sek"] is not None and _sb_v3_meta == {"sum": 3.0, "count": 1},
     repr(_sb_by_stamp[3.0]),
 )
+_sb_v4_row, _sb_v4_meta = _sb_by_stamp[4.0]
+R.check(
+    "a month stamped 4, the reference in force, keeps stating its saving as it books on",
+    _sb_v4_row["old_basis"] is False and _sb_v4_row["savings_sek"] is not None
+    and _sb_v4_row["savings_pct"] is not None and _sb_v4_meta == {"sum": 4.0, "count": 1},
+    repr(_sb_by_stamp[4.0]),
+)
 _sb_v1 = {"ledger": _sb_copy.deepcopy(_sb_led.as_dict()), "starts": {"kept": 1}}
 del _sb_v1["ledger"]["months"]["2026-02"]["meta"][_SB_META]
 _sb_lines = _sb_copy.deepcopy(_sb_v1["ledger"]["months"]["2026-02"]["lines"])
@@ -47612,6 +47634,189 @@ R.check(
     _sb_bare.savings_months(_SavDT(2026, 3, 2, 0, 0))[0]["old_basis"] is True,
     repr(_sb_bare.months),
 )
+# R11-VALVE-REFERENCE (carry 2): the booked reference, pinned. A digest of
+# `_compute_baseline_power`'s day (power to 1e-6 kW, its end room and tank) on
+# three installs at two outdoor levels with a sinusoid on them: the owner's
+# two-zone replay install with its manual valve, a single-zone house behind a
+# manual valve on one tank, and the same house with no valve. A diff that moves
+# the booked reference fails here until it re-records the digest and bumps
+# `REFERENCE_BASIS` and the stamp literal above with it.
+def _vr_one_tank():
+    from profiles import house as _vr_house
+
+    _vr_p = ThermalParameters.from_config(_vr_house(dhw=False))
+    _vr_p.dhw_enabled = False
+    _vr_p.mixing_valve_mode = "manual"
+    _vr_p.wood_tank_configured, _vr_p.wood_tank_volume = True, 500.0
+    return _vr_p
+
+
+def _vr_reference_digests():
+    import hashlib
+
+    from heatpump_optimizer.optimizer import HeatPumpOptimizer as _VrOpt
+    from heatpump_optimizer.optimizer import OptimizationConfig as _VrCfg
+    from heatpump_optimizer.thermal_model import WeatherSeries as _VrWeather
+    from profiles import house as _vr_house, replay_install as _vr_replay
+
+    _vr_n = 96
+    _vr_installs = {
+        "install": ThermalParameters.from_config(_vr_replay()),
+        "one-tank": _vr_one_tank(),
+        "no valve": ThermalParameters.from_config(_vr_house(dhw=False)),
+    }
+    _vr_out = {}
+    for _vr_name, _vr_p in _vr_installs.items():
+        for _vr_outdoor in (5.0, -15.0):
+            _vr_model = ThermalModel(_vr_p)
+            _vr_opt = _VrOpt(_vr_model, _VrCfg(horizon_hours=24, time_step_minutes=15, target_temp=21.0))
+            _vr_w = _VrWeather(
+                outdoor_temps=_vr_outdoor + 3.0 * np.sin(2.0 * np.pi * np.arange(_vr_n) / _vr_n),
+                wind_speeds=np.full(_vr_n, 3.0), precipitation=np.zeros(_vr_n),
+                solar_radiation=np.zeros(_vr_n))
+            _vr_start = ThermalState(
+                room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=_vr_outdoor,
+                upper_floor_temperature=21.0, lower_floor_temperature=21.0,
+                buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
+            _vr_power, _vr_end = _vr_opt._compute_baseline_power(
+                _vr_w, _vr_start, 0.25, np.full(_vr_n, 21.0))
+            _vr_text = ";".join(f"{float(v) + 0.0:.6f}" for v in _vr_power) + (
+                f"|{_vr_end.room_temperature + 0.0:.6f}|{_vr_end.buffer_tank_temperature + 0.0:.6f}")
+            _vr_out[f"{_vr_name} {_vr_outdoor:+.0f}"] = hashlib.sha256(_vr_text.encode()).hexdigest()[:16]
+    return _vr_out
+
+
+_vr_digests = _vr_reference_digests()
+R.check(
+    "the booked reference reproduces its recorded digest on every pinned install "
+    "(a change re-records it and bumps REFERENCE_BASIS)",
+    _vr_digests == {
+        "install +5": "2f088060f8fe63dd",
+        "install -15": "35cc1d0d71a4414b",
+        "one-tank +5": "ba516c4bb8328b78",
+        "one-tank -15": "cb3e0ea30949c952",
+        "no valve +5": "514d1532f1b30760",
+        "no valve -15": "0e396b7d1cc59e1a",
+    },
+    repr(_vr_digests),
+)
+# R11-VALVE-REFERENCE (carries 0, 1): a single-zone valve feeds the slab, which
+# reaches the room through `slab_heat_transfer` in series, and the house's own
+# gains offset part of its loss. The curve holds its target only with both in
+# it, and a thermostat behind that valve then reaches its setpoint.
+def _vr_single_zone_holds():
+    from heatpump_optimizer.optimizer import _thermostat_held_state as _vr_held
+    from heatpump_optimizer.thermal_model import WeatherSeries as _VrWeather
+
+    _vr_p = _vr_one_tank()
+    _vr_model = ThermalModel(_vr_p)
+    _vr_out = {}
+    for _vr_outdoor in (5.0, -5.0, -15.0):
+        _vr_start = ThermalState(
+            room_temperature=21.0, slab_temperature=22.0, outdoor_temperature=_vr_outdoor,
+            buffer_tank_temperature=40.0, wood_tank_temperature=20.0)
+        _vr_w = _VrWeather(
+            outdoor_temps=np.full(96, _vr_outdoor), wind_speeds=np.full(96, 3.0),
+            precipitation=np.zeros(96), solar_radiation=np.zeros(96))
+        _vr_h = _vr_held(_vr_model, _vr_start, _vr_w, 21.0)
+        _vr_s = _vr_h
+        for _ in range(960):
+            _vr_s = _vr_model.simulate_step(
+                _vr_s, _vr_p.max_electrical_power, _vr_outdoor, 3.0, 0.0, 0.0, 0.25)
+        _vr_out[_vr_outdoor] = (_vr_h.room_temperature, _vr_s.room_temperature)
+    return _vr_p.mixing_valve_target or _vr_p.comfort_ceiling, _vr_out
+
+
+_vr_target, _vr_holds = _vr_single_zone_holds()
+R.check(
+    "single-zone valve: the plant at its pump, settled, holds the curve's own target within 0.02 K",
+    all(abs(_vr_plant - _vr_target) < 0.02 for _, _vr_plant in _vr_holds.values()),
+    f"target {_vr_target}: " + ", ".join(
+        f"{o:+.0f} C {pl:.3f}" for o, (_, pl) in _vr_holds.items()),
+)
+R.check(
+    "single-zone valve: a thermostat set to 21 C holds 21 C behind it",
+    all(abs(_vr_room - 21.0) < 1e-3 for _vr_room, _ in _vr_holds.values()),
+    ", ".join(f"{o:+.0f} C {r:.4f}" for o, (r, _) in _vr_holds.items()),
+)
+
+
+def _vr_curve_agrees():
+    from heatpump_optimizer.thermal_model import _valve_flow_set, _valve_ua
+
+    _vr_cases = {
+        "one-tank": _vr_one_tank(),
+        "defaults": ThermalParameters(mixing_valve_mode="manual"),
+        "floors apart": ThermalParameters(
+            mixing_valve_mode="manual", upper_floor_heat_loss=0.12, lower_floor_heat_loss=0.09),
+    }
+    _vr_out = {}
+    for _vr_name, _vr_p in _vr_cases.items():
+        _vr_model = ThermalModel(_vr_p)
+        _vr_u = _vr_model.effective_heat_loss_coefficient(_vr_p.heat_loss_coefficient, 0.0, 0.0)
+        for _vr_outdoor in (5.0, -5.0, -15.0):
+            _vr_out[(_vr_name, _vr_outdoor)] = (
+                _vr_model.flow_target_for_indoor(21.0, _vr_outdoor),
+                _valve_flow_set(_vr_p, 21.0, _vr_outdoor, _vr_u, _valve_ua(_vr_p)))
+    return _vr_out
+
+
+_vr_agree = _vr_curve_agrees()
+R.check(
+    "single-zone valve: the curve the model reports is the plant's own, at zero wind and rain",
+    all(_vr_rep == _vr_plant for _vr_rep, _vr_plant in _vr_agree.values()),
+    repr(_vr_agree),
+)
+
+
+
+def _vr_mild_curve():
+    from heatpump_optimizer.thermal_model import _valve_flow_set, _valve_ua
+
+    _vr_p = _vr_one_tank()
+    _vr_u = ThermalModel(_vr_p).effective_heat_loss_coefficient(_vr_p.heat_loss_coefficient, 0.0, 0.0)
+    return _vr_p.internal_gains, _vr_u * 0.5, _valve_flow_set(_vr_p, 21.0, 20.5, _vr_u, _valve_ua(_vr_p))
+
+
+_vr_gains, _vr_loss, _vr_mild = _vr_mild_curve()
+R.check(
+    "single-zone valve: where the house's gains cover its loss the curve sits at its target, never below",
+    _vr_gains > _vr_loss and _vr_mild == 21.0,
+    f"gains {_vr_gains:.3f} kW, loss {_vr_loss:.4f} kW, curve {_vr_mild!r} C",
+)
+
+
+def _vr_direct_curve():
+    from heatpump_optimizer import mixing_valve as _vr_mv
+    from profiles import house as _vr_house
+
+    _vr_cfg = dict(flow_curve_cop_enabled=True, heat_pump_max_power=3.0,
+                   upper_floor_heat_loss=0.2, lower_floor_heat_loss=0.2)
+    _vr_p = ThermalParameters.from_config(_vr_house(**_vr_cfg))
+    _vr_p.flow_curve_bias = 5.0
+    _vr_model = ThermalModel(_vr_p)
+    # The new curve is reached only behind a throttling valve, and the price
+    # path reads a curve only with `flow_curve_cop`: `from_config` is what keeps
+    # the two apart, so a throttling mode must turn the priced curve off.
+    _vr_coupled = all(
+        ThermalParameters.from_config(_vr_house(mixing_valve_mode=_vr_mode, **_vr_cfg)).flow_curve_cop
+        is (not _vr_mv.is_throttling(_vr_mode))
+        for _vr_mode in (_vr_mv.MODE_NONE, *sorted(_vr_mv.THROTTLING_MODES)))
+    return _vr_p.flow_curve_cop, _vr_coupled, [
+        (_vr_model.flow_target_for_indoor(21.0, _vr_o), _vr_model.curve_flow_temp(_vr_o))
+        for _vr_o in (5.0, -5.0, -15.0)]
+
+
+_vr_priced, _vr_coupled, _vr_direct = _vr_direct_curve()
+R.check(
+    "no valve: the priced flow curve of a single-zone direct plant is unchanged, bit for bit",
+    _vr_priced is True and _vr_coupled is True and _vr_direct == [
+        (30.142857142857146, 35.142857142857146),
+        (35.85714285714286, 40.85714285714286),
+        (41.57142857142857, 46.57142857142857),
+    ],
+    repr((_vr_priced, _vr_coupled, _vr_direct)),
+)
 # R10-HOTFIX-SAV-ESTIMATE: the settlement books step 0 of a plan re-made every
 # interval, so behind a valve the first step must not be the stores' transient.
 # At one outdoor the steady demand is flat, so a sound step 0 is the horizon mean;
@@ -90338,18 +90543,22 @@ def _svh_case(two_zone, outdoor, **over):
     return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), nxt
 
 
-# -10 and -15 C sag far; at 14 C the two-zone house falls just short of the
-# target (a shortfall under 1 kW) and at 16 C holds it on a need under 1 kW.
+# -10 and -15 C sag far on two zones; at 14 C the two-zone house falls just short
+# of the target (a shortfall under 1 kW) and at 16 C holds it on a need under 1 kW.
+# A single-zone curve holds its target through the slab (R11-VALVE-REFERENCE), so
+# its held room is the setpoint at every row.
 _svh_rows = {(tz, t): _svh_case(tz, t) for tz in (True, False) for t in (-10.0, -15.0, 14.0, 16.0)}
 R.check(
     "R10-SAV-VALUATION-RESIDUE: behind a valve whose curve cannot hold the "
     "setpoint, the thermostat reference starts where that curve holds the "
     "house -- its first booked step draws no stored heat (the held 21 C "
     "drew it every step, booked as unpaid reference heat); both zonings, "
-    "from a deep shortfall to a mild day the curve holds",
+    "from a deep shortfall to a mild day the curve holds; a single-zone curve "
+    "holds the setpoint itself",
     all(abs(ds) < 0.02 for h, ds, _ in _svh_rows.values())
-    and all(_svh_rows[(tz, t)][0].room_temperature < 21.0 - 0.1
-            for tz in (True, False) for t in (-10.0, -15.0)),
+    and all(_svh_rows[(True, t)][0].room_temperature < 21.0 - 0.1 for t in (-10.0, -15.0))
+    and all(abs(_svh_rows[(False, t)][0].room_temperature - 21.0) < 1e-3
+            for t in (-10.0, -15.0, 14.0, 16.0)),
     {k: (round(h.room_temperature, 3), round(ds, 4)) for k, (h, ds, _) in _svh_rows.items()},
 )
 # Null control: a curve that holds the setpoint keeps the held state at target.
@@ -93124,7 +93333,12 @@ R.check(
     [_dsp_served(3.0, 2.0, m, None) for m in (5.99, 6.0, 6.01)] == ["dhw", "space", "space"],
     f"{[_dsp_served(3.0, 2.0, m, None) for m in (5.99, 6.0, 6.01)]}",
 )
-_dsp_mc = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, cyc=0.0)
+# A clamped install prices no start only with the clamped default patched to
+# zero (R11-OUTSIDE-HONEST-STARTS-RUNS-P3), as the two references below.
+from unittest import mock as _dsp_mock  # noqa: E402
+
+with _dsp_mock.patch.object(_dsp_om, "CLAMPED_DEFAULT_START_PRICE", 0.0):
+    _dsp_mc = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, cyc=0.0)
 _dsp_mc_avail = _dsp_mc.opt._space_avail
 _dsp_mc_fed = np.asarray(_dsp_mc.sims[-1]["space_power_schedule"], float)
 _dsp_mc_live = (
@@ -93192,7 +93406,11 @@ R.check(
 )
 # The switch term reads the shipped level: on the fixed-speed plan the
 # delivered draw of a charged step is under the floor and would be no leg.
-_dsp_fx_free = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, p_min=5.5, cyc=0.0)
+# The unpriced reference is clamped at a start price of zero, which since
+# R11-OUTSIDE-HONEST-STARTS-RUNS-P3 only a clamped default patched to zero
+# reaches (a clamped install configured at zero plans at the default).
+with _dsp_mock.patch.object(_dsp_om, "CLAMPED_DEFAULT_START_PRICE", 0.0):
+    _dsp_fx_free = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, p_min=5.5, cyc=0.0)
 _dsp_fx_obj, _dsp_fx_batch = _dsp_fx.objectives[-1][1], _dsp_fx.objectives[-1][2]
 _dsp_fx_score = float(_dsp_fx_obj(_dsp_fx.space, _dsp_fx.dhw, None, _dsp_fx_avail))
 _dsp_fx_level_terms = _dsp_fx.opt.config.price_weight * (
@@ -93648,10 +93866,14 @@ R.check(
 # zero price, no mask buys anything, so every band's mask is the relaxed
 # plan's own runs and each candidate of the stage is that plan. Corpus: 60
 # realizable plans of 24 steps, one charge each, from a stopped and a running
-# compressor. At a flat price the same plans get another candidate.
+# compressor. At a flat price the same plans get another candidate. A
+# clamped install prices no start only with the clamped default patched to
+# zero (R11-OUTSIDE-HONEST-STARTS-RUNS-P3).
 _dsp_tie_rng = np.random.default_rng(3602)
 _dsp_tie_opt = _dsp_opt(clamp=True, cyc=0.0)
 _dsp_tie_moved = {"zero price": 0, "flat price": 0}
+_dsp_tie_zero = _dsp_mock.patch.object(_dsp_om, "CLAMPED_DEFAULT_START_PRICE", 0.0)
+_dsp_tie_zero.start()
 for _dsp_tie_i in range(60):
     _dsp_tie_space = np.where(_dsp_tie_rng.random(24) < 0.5, 0.0, _dsp_tie_rng.uniform(1.5, 3.0, 24))
     _dsp_tie_dhw = np.zeros(24)
@@ -93663,6 +93885,7 @@ for _dsp_tie_i in range(60):
                 _dsp_tie_opt,
                 _DspNS(prices=np.full(24, _dsp_tie_price), dt=0.25, compressor_running=bool(_dsp_tie_i % 2)),
                 _dsp_tie_space, _dsp_tie_dhw, np.zeros(24), 5.5 - _dsp_tie_dhw, np.zeros(24, dtype=bool)))
+_dsp_tie_zero.stop()
 R.check(
     "beside a hot-water charge, at a zero price on an install that prices no "
     "start, every candidate of the stage is the realizable relaxed plan itself; "
@@ -94149,13 +94372,19 @@ R.check(
 # A realizable relaxed plan is a candidate, never a result the stage is held
 # to (design note round 3, test 4): the relaxed descent prices no start, so
 # such a plan carries starts nobody priced. The fixture is the plan the same
-# house ships clamped at no price, which already runs, handed as the relaxed
-# plan to the stage of the priced solve, in that solve's own scope: the stage
+# house ships clamped at a start price of zero, which already runs; since
+# R11-OUTSIDE-HONEST-STARTS-RUNS-P3 a clamped install plans at the clamped
+# default, so only a default patched to zero reaches that plan. It is handed as
+# the relaxed plan to the stage of the priced solve, in that solve's own scope: the stage
 # ships another plan, with fewer starts, that the scope it ships in scores
 # strictly below the plan handed in. One non-convex stage per arm
 # (``fixer.md`` step 15): the margin measured on x86_64 is 0.70, the check
 # asks for 0.01.
-_hsr_ran = _hsr_cells[(0.0, True, 1.1)].space
+from unittest import mock as _hsr_mock  # noqa: E402
+
+with _hsr_mock.patch.object(_hsr_om, "CLAMPED_DEFAULT_START_PRICE", 0.0):
+    _hsr_zero_clamped = _hsr_solve(0.0, True, 1.1)
+_hsr_ran = _hsr_zero_clamped.space
 _hsr_ran_stage = _hsr_cells[(0.25, False, 1.1)].stages[-1]
 _hsr_ran_shipped, _hsr_ran_scope = _hsr_om._commit_runs(
     *_hsr_ran_stage[:3], [_hsr_ran], *_hsr_ran_stage[4:])
@@ -94240,8 +94469,9 @@ R.check(
     _hsr_run_on.result.objective_value != _hsr_run_off.result.objective_value,
     f"{_hsr_run_on.result.objective_value} vs {_hsr_run_off.result.objective_value}",
 )
-# A realizable relaxed plan on a clamped install that prices no start ships
-# as it stands: the stage is the identity, the objective never called.
+# An unengaged solve ships its relaxed plan as it stands: the stage is the
+# identity, the objective never called. An engaged solve always prices a
+# start (R11-OUTSIDE-HONEST-STARTS-RUNS-P3), so it has no such identity.
 
 
 def _hsr_never(*_args, **_kw):
@@ -94258,10 +94488,10 @@ def _hsr_commit(opt, objective, batch, space, maxiter=5):
 
 
 R.check(
-    "null control, a realizable relaxed plan: a clamped install that prices no "
-    "start ships it unchanged, the very array, and an unengaged solve any plan",
-    _hsr_commit(_hsr_opt(0.0, True, 1.1), _hsr_never, _hsr_never, _hsr_real) is _hsr_real
-    and _hsr_commit(_hsr_opt(0.0, False, 1.1), _hsr_never, _hsr_never, _hsr_trickle) is _hsr_trickle,
+    "null control: an unengaged solve ships any relaxed plan unchanged, the very array, "
+    "the objective never consulted",
+    _hsr_commit(_hsr_opt(0.0, False, 1.1), _hsr_never, _hsr_never, _hsr_trickle) is _hsr_trickle
+    and _hsr_commit(_hsr_opt(0.0, False, 1.1), _hsr_never, _hsr_never, _hsr_real) is _hsr_real,
 )
 R.check(
     "and with a plan that is not realizable the same call ships the projection "
@@ -94572,6 +94802,51 @@ R.check(
     and _hsr_om._start_cost_fn(_hsr_opt(0.25, False, 1.1), True)(_hsr_real, None)
     == 0.25 * _hsr_count(_hsr_real, 1.1, True),
 )
+
+# R11-OUTSIDE-HONEST-STARTS-RUNS-P3 (owner ruling Q2): a clamped install that
+# prices no start plans at the clamped default start price, 0.1. Without it
+# the grid cell clamped at no price ships 5 starts where the tree before pull
+# request 3602 shipped 2 (dev/audit/harnesses/r11_honest_starts_runs.py,
+# ``grid`` and ``defaults``). The rule: the default replaces a configured
+# price of zero on a clamped install and nothing else. Nulls: a priced install
+# keeps its price below and above the default, an unclamped one keeps zero.
+import inspect as _hsr_inspect  # noqa: E402
+import re as _hsr_re  # noqa: E402
+
+_hsr_sp = {
+    (cost, clamp): getattr(
+        _hsr_om.OptimizationConfig(clamp_planned_levels=clamp, cycling_cost=cost), "start_price", None)
+    for cost in (0.0, 0.05, 0.25) for clamp in (False, True)
+}
+R.check(
+    "the start price a solve plans with: the configured price, except that a clamped install "
+    "configured at zero plans at the clamped default 0.1; a priced install keeps its own price "
+    "below and above the default, and an unclamped install keeps zero",
+    getattr(_hsr_om, "CLAMPED_DEFAULT_START_PRICE", None) == 0.1
+    and _hsr_sp == {(0.0, False): 0.0, (0.0, True): 0.1, (0.05, False): 0.05,
+                    (0.05, True): 0.05, (0.25, False): 0.25, (0.25, True): 0.25},
+    f"{_hsr_sp}",
+)
+_hsr_at_default = _hsr_solve(0.1, True, 1.1)
+R.check(
+    "failing case: the grid cell clamped at no configured price ships the plan it ships "
+    "configured at the clamped default, with no more than the 2 starts the tree before "
+    "pull request 3602 shipped (5 without the default) and fewer than the same install "
+    "ships with the default patched to zero",
+    np.array_equal(_hsr_cells[(0.0, True, 1.1)].space, _hsr_at_default.space)
+    and _hsr_edges(_hsr_cells[(0.0, True, 1.1)].space) <= 2
+    and _hsr_edges(_hsr_cells[(0.0, True, 1.1)].space) < _hsr_edges(_hsr_zero_clamped.space),
+    f"edges {_hsr_edges(_hsr_cells[(0.0, True, 1.1)].space)}, "
+    f"at the default {_hsr_edges(_hsr_at_default.space)}, "
+    f"default patched to zero {_hsr_edges(_hsr_zero_clamped.space)}",
+)
+_hsr_cost_readers = _hsr_re.findall(r"\.config\.cycling_cost\b", _hsr_inspect.getsource(_hsr_om))
+R.check(
+    "every optimizer reader of the start price reads start_price, never the raw "
+    "configured cycling_cost, which only the property reads",
+    not _hsr_cost_readers,
+    f"{len(_hsr_cost_readers)} raw readers",
+)
 # The humidity guard the two SolveInputs sites share.
 from heatpump_optimizer.coordinator import _humidity_with_data as _hsr_humidity  # noqa: E402
 
diff --git a/tests/golden/card_claimed_drift.txt b/tests/golden/card_claimed_drift.txt
index 50fe1c7672..06c81bd609 100644
--- a/tests/golden/card_claimed_drift.txt
+++ b/tests/golden/card_claimed_drift.txt
@@ -808,3 +808,10 @@
 # advisor_empty move on advisor.step_grid, advisor_page also on
 # advisor.basis_history, savings_page on receipt.covers; the other 18 render
 # the What-if panel and move on whatif.no_windows_hint. Text nodes only.
+
+# R11-OWNER-GENERIC-CONTROL-TEXT carry (#3643): dearer becomes pricier in stats.dearer
+# (the what-if delta hint) and in why.sub_dearer (the hover's Because line), the short
+# form because "more expensive" wraps both at 375 px. Text nodes only.
+draft_dirty_menu_open  # what-if delta hint: "pricier than the saved plan"
+draft_mid_drag  # what-if delta hint: "pricier than the saved plan"
+tooltip_hover  # the hovered idle step's Because line: "this hour is pricier than the hours the plan uses"
diff --git a/tests/layout.json b/tests/layout.json
index 6331e2d0ce..b87a33b5b7 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -31,7 +31,7 @@
    "name": "docs",
    "why": "product documentation, read by users; the page URLs stay stable for users and HACS",
    "globs": [
-    "docs/{setup,configuration,automations,dashboard-card,ecl110,how-it-works,architecture,CONTRIBUTING}.md",
+    "docs/{setup,configuration,automations,dashboard-card,ecl110,heat-curve,how-it-works,architecture,CONTRIBUTING}.md",
     "docs/img/brand/*",
     "docs/img/card/*",
     "docs/img/model/*",
diff --git a/tests/md_tables.mjs b/tests/md_tables.mjs
index c1de466a1b..7e64a1fc0c 100644
--- a/tests/md_tables.mjs
+++ b/tests/md_tables.mjs
@@ -3,7 +3,7 @@
 // (dev/audit/rounds/round9/D5/s1/md_tables.mjs, evidence commit 79aa98ec).
 //
 // Metric (one line, unchanged from the finder): source lines in README.md +
-// docs/{architecture,automations,configuration,dashboard-card,ecl110,
+// docs/{architecture,automations,configuration,dashboard-card,heat-curve,
 // how-it-works,setup}.md that render in the wrong block -- (a) prose lines
 // (not starting with "|") rendered as table rows ("swallowed"), plus (b)
 // pipe-table rows rendered as paragraph text with raw pipes ("orphaned")
@@ -38,7 +38,7 @@ const md = new MarkdownIt('commonmark').enable('table')
 const FILES = [
   'README.md',
   ...['architecture', 'automations', 'configuration', 'dashboard-card',
-    'ecl110', 'how-it-works', 'setup'].map((n) => `docs/${n}.md`),
+    'heat-curve', 'how-it-works', 'setup'].map((n) => `docs/${n}.md`),
 ]
 
 export function analyse(text) {
diff --git a/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.481451d2.json b/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.0e2b3d10.json
similarity index 61%
rename from tests/mutation_ledger/killed_by/ledger.py/@module.CONST.481451d2.json
rename to tests/mutation_ledger/killed_by/ledger.py/@module.CONST.0e2b3d10.json
index d9691447c1..07636a422b 100644
--- a/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.481451d2.json
+++ b/tests/mutation_ledger/killed_by/ledger.py/@module.CONST.0e2b3d10.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/ledger.py:<module> CONST 481451d2",
+  "anchor": "custom_components/heatpump_optimizer/ledger.py:<module> CONST 0e2b3d10",
   "killed_by": "tests/features.py",
-  "old": "REFERENCE_BASIS = 3",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`REFERENCE_BASIS = 6`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "REFERENCE_BASIS = 4",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`REFERENCE_BASIS = 8`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/mixing_valve.py/flow_setpoint.CLAMP_DROP.5650fea2.json b/tests/mutation_ledger/killed_by/mixing_valve.py/flow_setpoint.CLAMP_DROP.5650fea2.json
deleted file mode 100644
index d6dd131acd..0000000000
--- a/tests/mutation_ledger/killed_by/mixing_valve.py/flow_setpoint.CLAMP_DROP.5650fea2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/mixing_valve.py:flow_setpoint CLAMP_DROP 5650fea2",
-  "killed_by": "tests/features.py",
-  "old": "    q_hold = heat_loss_coefficient * max(0.0, target_temp - outdoor_temp)",
-  "reason": "Recorded by `mutation_table.py --drain` against c3530277373ddf87652858f9ecb0ee1cf36f4347: CLAMP_DROP (`q_hold = heat_loss_coefficient * (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/mixing_valve.py/flow_setpoint.CLAMP_DROP.68a59fb2.json b/tests/mutation_ledger/killed_by/mixing_valve.py/flow_setpoint.CLAMP_DROP.68a59fb2.json
new file mode 100644
index 0000000000..1ab4fea0f0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/mixing_valve.py/flow_setpoint.CLAMP_DROP.68a59fb2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/mixing_valve.py:flow_setpoint CLAMP_DROP 68a59fb2",
+  "killed_by": "tests/features.py",
+  "old": "        0.0, heat_loss_coefficient * max(0.0, target_temp - outdoor_temp) - free_heat_kw",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`0.0, heat_loss_coefficient * (0.0) - free_heat_kw`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.BOOLOP.76814d0c.json b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.BOOLOP.76814d0c.json
new file mode 100644
index 0000000000..1ec61719e7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.BOOLOP.76814d0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:OptimizationConfig.start_price BOOLOP 76814d0c",
+  "killed_by": "tests/features.py",
+  "old": "        if self.clamp_planned_levels and not self.cycling_cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.clamp_planned_levels or not self.cycling_cost > 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.CMP_BOUND.76814d0c.json b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.CMP_BOUND.76814d0c.json
new file mode 100644
index 0000000000..ea986ff13e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.CMP_BOUND.76814d0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:OptimizationConfig.start_price CMP_BOUND 76814d0c",
+  "killed_by": "tests/features.py",
+  "old": "        if self.clamp_planned_levels and not self.cycling_cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if self.clamp_planned_levels and not self.cycling_cost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.GUARD_OFF.76814d0c.json b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.GUARD_OFF.76814d0c.json
new file mode 100644
index 0000000000..56a8406c22
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.GUARD_OFF.76814d0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:OptimizationConfig.start_price GUARD_OFF 76814d0c",
+  "killed_by": "tests/features.py",
+  "old": "        if self.clamp_planned_levels and not self.cycling_cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.RETURN_DEL.a3ef75f4.json b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.RETURN_DEL.a3ef75f4.json
new file mode 100644
index 0000000000..0ea6d54d98
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/OptimizationConfig.start_price.RETURN_DEL.a3ef75f4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:OptimizationConfig.start_price RETURN_DEL a3ef75f4",
+  "killed_by": "tests/plan_view.py",
+  "old": "        return self.cycling_cost",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json
deleted file mode 100644
index fa48feb1d0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 7b6d787d",
-  "killed_by": "tests/features.py",
-  "old": "    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or not opt.config.cycling_cost >= 0 or opt.model.params.dhw_store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.dfb7f4b9.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.dfb7f4b9.json
new file mode 100644
index 0000000000..bff6c9d259
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.dfb7f4b9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND dfb7f4b9",
+  "killed_by": "tests/features.py",
+  "old": "    if stops is None or not opt.config.start_price > 0 or opt.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or not opt.config.start_price >= 0 or opt.model.params.dhw_store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json
deleted file mode 100644
index ba5f280182..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 7b6d787d",
-  "killed_by": "tests/plan_view.py",
-  "old": "    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.dfb7f4b9.json
similarity index 58%
rename from tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.dfb7f4b9.json
index e284c1cd91..de9dfcd530 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.GUARD_OFF.a5a6e190.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.dfb7f4b9.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs GUARD_OFF a5a6e190",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF dfb7f4b9",
   "killed_by": "tests/features.py",
-  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "    if stops is None or not opt.config.start_price > 0 or opt.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json
deleted file mode 100644
index 8b2a963bae..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.BOOLOP.a5a6e190.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs BOOLOP a5a6e190",
-  "killed_by": "tests/features.py",
-  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not opt.config.cycling_cost > 0 or np.array_equal(first, relaxed[0]):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json b/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json
deleted file mode 100644
index 4e309042f4..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_commit_runs.CMP_BOUND.a5a6e190.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_commit_runs CMP_BOUND a5a6e190",
-  "killed_by": "tests/features.py",
-  "old": "    if not opt.config.cycling_cost > 0 and np.array_equal(first, relaxed[0]):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not opt.config.cycling_cost >= 0 and np.array_equal(first, relaxed[0]):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json
deleted file mode 100644
index 162a778d06..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0d0861f2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged CMP_BOUND 0d0861f2",
-  "killed_by": "tests/features.py",
-  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return opt.config.cycling_cost >= 0 or opt.config.clamp_planned_levels`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0fcd7cc5.json b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0fcd7cc5.json
new file mode 100644
index 0000000000..df78262a29
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.CMP_BOUND.0fcd7cc5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged CMP_BOUND 0fcd7cc5",
+  "killed_by": "tests/features.py",
+  "old": "    return opt.config.start_price > 0 or opt.config.clamp_planned_levels",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return opt.config.start_price >= 0 or opt.config.clamp_planned_levels`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0fcd7cc5.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0fcd7cc5.json
index a0caaeb577..1bb480dfa1 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0d0861f2.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_engaged.RETURN_DEL.0fcd7cc5.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged RETURN_DEL 0d0861f2",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_engaged RETURN_DEL 0fcd7cc5",
   "killed_by": "tests/features.py",
-  "old": "    return opt.config.cycling_cost > 0 or opt.config.clamp_planned_levels",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+  "old": "    return opt.config.start_price > 0 or opt.config.clamp_planned_levels",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json
deleted file mode 100644
index be24e0d98e..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.70252daa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans BOOLOP 70252daa",
-  "killed_by": "tests/features.py",
-  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if opt.config.cycling_cost > 0 or _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.8a6228d6.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.8a6228d6.json
new file mode 100644
index 0000000000..e519a6e949
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.BOOLOP.8a6228d6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans BOOLOP 8a6228d6",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.start_price > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if opt.config.start_price > 0 or _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json
deleted file mode 100644
index 9fcbda06d8..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.70252daa.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CMP_BOUND 70252daa",
-  "killed_by": "tests/features.py",
-  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if opt.config.cycling_cost >= 0 and _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.8a6228d6.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.8a6228d6.json
new file mode 100644
index 0000000000..65bbbc0af9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.CMP_BOUND.8a6228d6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans CMP_BOUND 8a6228d6",
+  "killed_by": "tests/features.py",
+  "old": "    if opt.config.start_price > 0 and _priced_stops(opt) is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if opt.config.start_price >= 0 and _priced_stops(opt) is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.8a6228d6.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.8a6228d6.json
index e9c5cd543c..e7ac9d97ee 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.70252daa.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_relaxed_plans.GUARD_OFF.8a6228d6.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans GUARD_OFF 70252daa",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_relaxed_plans GUARD_OFF 8a6228d6",
   "killed_by": "tests/features.py",
-  "old": "    if opt.config.cycling_cost > 0 and _priced_stops(opt) is not None:",
+  "old": "    if opt.config.start_price > 0 and _priced_stops(opt) is not None:",
   "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
 }
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.12bdfb35.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.12bdfb35.json
new file mode 100644
index 0000000000..f3a67de7c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel._substeps_and_loss.GUARD_OFF.12bdfb35.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel._substeps_and_loss GUARD_OFF 12bdfb35",
+  "killed_by": "tests/features.py",
+  "old": "            if p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.BOOLOP.89896ff5.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.BOOLOP.89896ff5.json
new file mode 100644
index 0000000000..63eb49abbf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.BOOLOP.89896ff5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.flow_target_for_indoor BOOLOP 89896ff5",
+  "killed_by": "tests/features.py",
+  "old": "        if not p.two_zone_enabled and p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if not p.two_zone_enabled or p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.GUARD_OFF.89896ff5.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.GUARD_OFF.89896ff5.json
new file mode 100644
index 0000000000..a8d208ea16
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.GUARD_OFF.89896ff5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.flow_target_for_indoor GUARD_OFF 89896ff5",
+  "killed_by": "tests/features.py",
+  "old": "        if not p.two_zone_enabled and p.mixing_valve_mode in mixing_valve.THROTTLING_MODES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.RETURN_DEL.90b0d928.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.RETURN_DEL.90b0d928.json
new file mode 100644
index 0000000000..a6a6a3f00c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalModel.flow_target_for_indoor.RETURN_DEL.90b0d928.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalModel.flow_target_for_indoor RETURN_DEL 90b0d928",
+  "killed_by": "tests/features.py",
+  "old": "            return _valve_flow_set(p, indoor_target, outdoor_temp, u, _valve_ua(p))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/_valve_flow_set.GUARD_OFF.d85c286a.json b/tests/mutation_ledger/killed_by/thermal_model.py/_valve_flow_set.GUARD_OFF.d85c286a.json
new file mode 100644
index 0000000000..81c6f49837
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/_valve_flow_set.GUARD_OFF.d85c286a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:_valve_flow_set GUARD_OFF d85c286a",
+  "killed_by": "tests/features.py",
+  "old": "    if not p.two_zone_enabled:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index db306421af..8f925f20e3 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17383,
+ "class_excess_loc": 17382,
  "const_modules_over_50": 3,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
@@ -16,6 +16,6 @@
  "methods_over_150": 14,
  "methods_over_200": 7,
  "name_kept_members": 38,
- "recorded_at": "31255c328918573ef29007dac22d7184a0f0247c",
+ "recorded_at": "e352724335c136b65562cd3e71f728549ad04a82",
  "seam_cut_total": 415
 }
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index bc2555b42e..35570e8574 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -86,7 +86,7 @@ standing-seat liveness step keep the seats alive.
 - [`open_pr.sh`](instruments/open_pr.sh.md) — opens a draft PR from `handoff/<topic>` as `hpo-author`, adds its own delivery row, re-pushes, prints N and the head
 - [`orchestrator_tick.py`](instruments/orchestrator_tick.py.md) — the heartbeat's dispatch list
 - [`owed_unactioned.py`](instruments/owed_unactioned.py.md) — says which tick owed lines have outlived a sweep with no live acknowledgement
-- [`plan_audit.py`](instruments/plan_audit.py.md) — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the `audit-plan` workflow
+- [`plan_audit.py`](instruments/plan_audit.py.md) — P3's measuring half (R10-FLOW-AUDIT-PLAN, R11-ARCH-OBJECTIVE), beside the `audit-plan` workflow
 - [`plan_page.py`](instruments/plan_page.py.md) — renders the round's plan page (HTML) from `tools/plan/replan.py`'s plan.json, the roster through `roster_lib`
 - [`plan_table.py`](instruments/plan_table.py.md) — renders the plan artifact from a wave-groups roster
 - [`policy_reread_check.py`](instruments/policy_reread_check.py.md) — says whether a session owes a policy re-read
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index 7eed46abc1..6b24aec8ae 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -21,8 +21,9 @@ file is its only writer:
   new.txt        the lines the last changing fold added (empty when it added none);  by fold()
   gone.txt       the lines the last changing fold dropped (empty when it dropped none); by fold()
   new.stamp      touched (the fold's UTC) only when that fold added a line;
-  events.txt     `<utc> HEAD-MOVED #<n> <old12> <new12>` (head-watch) and
-                 `<utc> STUCK ...` (opener) lines, appended once each;
+  events.txt     `<utc> HEAD-MOVED #<n> <old12> <new12>` (head-watch),
+                 `<utc> STUCK ...` (opener) and `<utc> ROSTER-REFUSED ...`
+                 (roster-drain) lines, appended once each;
   heads.tsv      head-watch's last-seen head per open pull request;
   state/         each row's own memory (tick passes, roster marks, holds).
 fold() runs under `flock digest/.lock`. A null pass changes no byte; the wake
@@ -48,8 +49,11 @@ ROWS (the job table's `interval_s` in brackets):
   roster-drain [120] each pending op of `S/roster-drain.queue` through
                      roster_queue.py `run`, one at a time; every `roster:` line
                      it reports goes to the digest and the exact line (text and
-                     occurrence) is marked done in `state/` as soon as it ran,
-                     refused or not: a refusal is never retried, and a pass
+                     occurrence) is remembered in `state/` as soon as it ran,
+                     applied in roster-done.json, refused in roster-refused.json:
+                     a refusal is never retried, appends `ROSTER-REFUSED
+                     #<occurrence> <line>` to events.txt (the job file is
+                     replaced by the next pass that runs an op), and a pass
                      killed mid-queue replays at most the op it was killed in.
                      No op starts past ROSTER_PASS_BUDGET_S into a pass; the
                      rest wait for the next. `hold <tree-path> <op...>` waits
@@ -61,7 +65,10 @@ ROWS (the job table's `interval_s` in brackets):
                      because the worktree is on no origin ref (an earlier
                      refusal's leftover) stays pending under one `roster:
                      CASCADE` line. The lint clone is `S/roster-lint`, the
-                     orchestrator's to provision.
+                     orchestrator's to provision. Each op runs holding
+                     roster_lib's writer lease `S/roster-writer.lease`, taken
+                     without waiting: while an out-of-queue writer (carry_fold)
+                     holds it the pass starts no further op and writes no line.
   plan-beat [1800]   replan.py `--out`, then state_docs.py `--push --mirror
                      --plan`; `plan-beat: PLAN UNAVAILABLE` on a replan failure
                      or state_docs rc 1, `plan-beat: REFUSED` on its rc 2; on
@@ -181,6 +188,9 @@ import sys
 import time
 from pathlib import Path
 
+sys.path.insert(0, str(Path(__file__).resolve().parent))
+import roster_lib  # noqa: E402  the roster's one-writer lease
+
 ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "gantt", "verdict-audit", "pulse",
         "cancel-sweep", "disk", "opener", "loop-cwd", "head-watch", "audit-dispatch", "outside-intake", "cp-owed", "bottleneck",
         "scorecard", "ci-attempt", "toolchain-promote", "darwin-selftest")
@@ -393,6 +403,7 @@ def on_main(ctx: Ctx, path: str) -> bool:
 
 def roster_drain(ctx: Ctx) -> None:
     done = set(ctx.memory("roster-done.json", []))
+    refused = set(ctx.memory("roster-refused.json", []))
     holds = ctx.memory("roster-hold.json", {})
     lines, count, ran, cascade = [], collections.Counter(), False, 0
     # The queue is append-only. Only newline-terminated lines run: a last segment read mid-append waits
@@ -404,13 +415,18 @@ def roster_drain(ctx: Ctx) -> None:
     def save() -> None:  # after every op, not only at the pass's end: a killed pass keeps what it applied
         ctx.remember("roster-queue-lines.json", len(whole), 0)
         ctx.remember("roster-done.json", sorted(done), [])
+        ctx.remember("roster-refused.json", sorted(refused), [])
         ctx.remember("roster-hold.json", holds, {})
     if len(whole) < seen or ctx.memory("roster-shrank.json", False):
         ctx.remember("roster-shrank.json", True, False)  # sticky: the op queued after the clear must not vanish
         return write_job(ctx, "roster-drain", [
             f"roster: QUEUE-SHRANK {len(whole)} terminated line(s) now, {seen} drained before; the queue is "
-            "append-only; nothing ran. Rebaseline by deleting roster-done.json, roster-hold.json, "
-            "roster-queue-lines.json and roster-shrank.json under the digest state"])
+            "append-only; nothing ran. Rebaseline by deleting roster-done.json, roster-refused.json, "
+            "roster-hold.json, roster-queue-lines.json and roster-shrank.json under the digest state"])
+    def refuse(key: str) -> None:  # the job file is replaced by the next pass that runs an op; events.txt is not
+        refused.add(key)
+        n, _, text = key.partition("\t")
+        event(ctx, f"ROSTER-REFUSED #{n} {text}")
     start = ctx.clock()
     for raw in whole:
         text = raw.strip()
@@ -418,14 +434,14 @@ def roster_drain(ctx: Ctx) -> None:
             continue
         count[text] += 1
         key = f"{count[text]}\t{text}"
-        if key in done:
+        if key in done or key in refused:
             continue
         op = text
         if text.startswith("hold "):
             parts = text.split(None, 2)
             if len(parts) < 3:
                 lines.append(f"roster: refused malformed hold line: {text}")
-                done.add(key)
+                refuse(key)
                 continue
             first = holds.setdefault(key, ctx.now)
             if not on_main(ctx, parts[1]):
@@ -435,14 +451,20 @@ def roster_drain(ctx: Ctx) -> None:
             op = parts[2]
         if ctx.clock() - start >= ROSTER_PASS_BUDGET_S:
             break  # beatd kills the pass at timeout_s; this op and the rest run next pass
+        lease = roster_lib.writer_lease(ctx.state, 0)
+        if lease is None:
+            break  # an out-of-queue writer (carry_fold) holds the roster: this op and the rest run next pass
         one, report = ctx.digest / "state" / "roster-one.queue", ctx.digest / "state" / "roster-report.txt"
         atomic(one, op + "\n")
         report.unlink(missing_ok=True)
         ran = True
-        rc, out, err = ctx.py("tools/audit/seat/roster_queue.py", "run", "1", "1", "--mark", "--queue", str(one),
-                              "--report", str(report), "--edit-checkout", str(ctx.repo),
-                              "--worktree", str(ctx.digest / "state" / "roster-wt"),
-                              "--lint-clone", str(ctx.state / "roster-lint"))
+        try:
+            rc, out, err = ctx.py("tools/audit/seat/roster_queue.py", "run", "1", "1", "--mark", "--queue", str(one),
+                                  "--report", str(report), "--edit-checkout", str(ctx.repo),
+                                  "--worktree", str(ctx.digest / "state" / "roster-wt"),
+                                  "--lint-clone", str(ctx.state / "roster-lint"))
+        finally:
+            os.close(lease)
         said = [ln for ln in read(report).splitlines() if ln.startswith("roster: ")]
         mark = read(one).split("\n", 1)[0]  # `--mark` rewrites the exact line `#done <op>` or `#refused <op>`
         if not said and mark == op:  # no report line and no mark: roster_queue attempted nothing
@@ -452,10 +474,14 @@ def roster_drain(ctx: Ctx) -> None:
             cascade += 1  # the worktree an earlier refusal left detached refused it, not the lint gate
             continue
         lines += said or [f"roster: {op} {mark.split()[0]} rc={rc} no report line"]
-        if mark != op or not any("no op attempted" in ln for ln in said):
-            done.add(key)  # applied or refused: never retried past the lint gate
-            holds.pop(key, None)
-            save()
+        if mark == f"#refused {op}":
+            refuse(key)  # never retried past the lint gate, and durable past this pass's digest
+        elif mark != op or not any("no op attempted" in ln for ln in said):
+            done.add(key)  # applied: never re-run
+        else:
+            continue  # roster_queue attempted nothing: retried next pass
+        holds.pop(key, None)
+        save()
     if cascade:
         lines.append(f"roster: CASCADE {cascade} op(s) stay pending: the worktree "
                      f"{ctx.digest / 'state' / 'roster-wt'} is on no origin ref after an earlier refusal; "
@@ -472,7 +498,14 @@ def plan_beat(ctx: Ctx) -> None:
     plan, slots, seats, mirror, repo = got
     # the overlay's plan_coordinator_cap rides to replan.py; absent, replan's own default stands
     cap = ["--coordinator-cap", str(ctx.overlay["plan_coordinator_cap"])] if ctx.overlay.get("plan_coordinator_cap") else []
-    rc, _, err = ctx.py("tools/plan/replan.py", "--out", plan, "--slots", slots, "--seats", seats, *cap)
+    # Liveness by evidence, not the stage word (a stage-word read priced running
+    # groups as not started): the overlay's saved ref listing and in-flight PRs.
+    evidence: list = []
+    for key, flag in (("plan_live_refs", "--live-refs"), ("plan_in_flight", "--in-flight")):
+        if ctx.overlay.get(key):
+            evidence += [flag, str(ctx.overlay[key])]
+    rc, _, err = ctx.py("tools/plan/replan.py", "--out", plan, "--slots", slots, "--seats", seats,
+                        *cap, *evidence)
     if rc != 0:
         last = (err.strip().splitlines() or [""])[-1]
         return write_job(ctx, "plan-beat", [f"plan-beat: PLAN UNAVAILABLE replan rc={rc}: {last}"])
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index 7784f368d6..33d967bebd 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -311,6 +311,55 @@ def cases(bj) -> dict[str, bool]:
     bj.roster_drain(c)
     res["roster-drain: a REFUSE line arrives in the digest and is never retried"] = (
         "roster: append-carry G2 refused" in digest(c) and f.ran("roster_queue.py") == 1)
+    def ev(ctx):
+        return [ln.split(" ", 1)[1] for ln in bj.read(ctx.digest / "events.txt").splitlines()]
+    word = {"v": "refused rc=1 lint gate: TOTAL: 1"}
+    c, f = fresh(answers={"roster_queue.py": lambda a: roster(word["v"])(a)})
+    pre = not ev(c)
+    (c.state / "roster-drain.queue").write_text("append-group G9 @x\n")
+    bj.roster_drain(c)
+    word["v"] = "pushed 0123abcde"
+    (c.state / "roster-drain.queue").write_text("append-group G9 @x\nset-stage G1 done\n")
+    bj.roster_drain(c)
+    bj.roster_drain(c)
+    res["roster-drain: a refused op writes one events line that survives a following applied pass"] = (
+        pre and ev(c) == ["ROSTER-REFUSED #1 append-group G9 @x"]
+        and digest(c) == "roster: set-stage G1 pushed 0123abcde\n" and f.ran("roster_queue.py") == 2)
+    res["roster-drain: a refused key is remembered apart from the applied ones"] = (
+        c.memory("roster-refused.json", []) == ["1\tappend-group G9 @x"]
+        and c.memory("roster-done.json", []) == ["1\tset-stage G1 done"])
+    c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde")})
+    (c.state / "roster-drain.queue").write_text("set-stage G1 done\nhold only-a-path\n")
+    bj.roster_drain(c)
+    res["roster-drain null: an applied op writes no events line; a malformed hold writes one"] = (
+        ev(c) == ["ROSTER-REFUSED #1 hold only-a-path"] and c.memory("roster-refused.json", []) == ["1\thold only-a-path"])
+    import roster_lib
+    seen_held = []
+
+    def probe(argv):  # while an op runs, a fold's non-waiting take of the lease must fail
+        fd = roster_lib.writer_lease(Path(argv[argv.index("--lint-clone") + 1]).parent, 0)
+        seen_held.append(fd is None)
+        if fd is not None:
+            os.close(fd)
+        return roster("pushed 0123abcde")(argv)
+    c, f = fresh(answers={"roster_queue.py": probe})
+    (c.state / "roster-drain.queue").write_text("set-stage G1 done\nset-stage G2 done\n")
+    fold_fd = roster_lib.writer_lease(c.state, 0)
+    t0 = time.monotonic()
+    bj.roster_drain(c)
+    yielded = f.ran("roster_queue.py") == 0 and not digest(c) and time.monotonic() - t0 < 0.5  # yields, never waits
+    os.close(fold_fd)
+    bj.roster_drain(c)
+    res["roster-drain: no op starts while an out-of-queue writer holds the roster lease; the next pass runs them"] = (
+        yielded and f.ran("roster_queue.py") == 2 and seen_held == [True, True])
+    c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde")})
+    (c.state / "roster-drain.queue").write_text("set-stage G1 done\nset-stage G2 done\n")
+    bj.roster_drain(c)
+    after = roster_lib.writer_lease(c.state, 0)
+    res["roster-drain null: with no fold pending every op runs, and the lease is free after the pass"] = (
+        f.ran("roster_queue.py") == 2 and after is not None)
+    if after is not None:
+        os.close(after)
     on = {"v": 1}
     c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde"), "git": lambda a: (on["v"], "", "")})
     (c.state / "roster-drain.queue").write_text("hold dev/programme/triage/s9-batch1.md set-stage G3 x\n")
@@ -325,14 +374,15 @@ def cases(bj) -> dict[str, bool]:
         held and stale and f.ran("roster_queue.py") == 1 and "pushed" in digest(c))
     one = bj.read(c.digest / "state" / "roster-one.queue")
     res["roster-drain: a released hold hands roster_queue the held op, not the hold line"] = (
-        one == "#done set-stage G3 x\n" and digest(c) == "roster: set-stage G3 pushed 0123abcde\n")
+        one == "#done set-stage G3 x\n" and digest(c) == "roster: set-stage G3 pushed 0123abcde\n"
+        and c.memory("roster-hold.json", {}) == {})
 
     c, f = fresh(answers={"roster_queue.py": roster("pushed 0123abcde")})
     q = c.state / "roster-drain.queue"
     q.write_text("hold only-a-path\n")
     bj.roster_drain(c)
     first = digest(c) == "roster: refused malformed hold line: hold only-a-path\n"
-    marked = bool(c.memory("roster-done.json", []))
+    marked = bool(c.memory("roster-refused.json", []))
     q.write_text("hold only-a-path\nset-stage G1 done\n")
     bj.roster_drain(c)
     res["roster-drain: a malformed hold line is refused once and marked, never re-printed"] = (
@@ -445,6 +495,14 @@ def cases(bj) -> dict[str, bool]:
     bj.plan_beat(c)
     res["plan-beat: the overlay's plan_coordinator_cap is handed to replan as --coordinator-cap"] = (
         arg(f.calls[0], "--coordinator-cap") == "3")
+    res["plan-beat null: no evidence files leaves replan on the stage word"] = (
+        "--live-refs" not in a and "--in-flight" not in a)
+    c, f = fresh(overlay={"repo": "o/r", "plan_json": str(root / "pe.json"), "plan_slots": 10, "plan_seats": 99,
+                          "state_mirror": str(root / "pem"), "plan_live_refs": "/x/refs.txt",
+                          "plan_in_flight": "/x/prs.json"})
+    bj.plan_beat(c)
+    res["plan-beat: the overlay's ref listing and in-flight PRs reach replan (liveness by evidence)"] = (
+        arg(f.calls[0], "--live-refs") == "/x/refs.txt" and arg(f.calls[0], "--in-flight") == "/x/prs.json")
     c, f = fresh(answers={"state_docs.py": (0, "pushed handoff/audit-r10-plan at abc\n", "")})
     bj.plan_beat(c)
     gh = [x for x in f.calls if x[0] == "gh"]
@@ -1258,7 +1316,19 @@ MUTANTS = {
     "owed_rc1_dropped": ("    if rc == 1:\n", "    if rc == 9:\n", "owed-check: an UNACTIONED exit lands in new.txt"),
     "roster_no_mark": ("            done.add(key)  # applied", "            pass  # applied",
                        "roster-drain: a queue line drains once, is marked, and is not re-run"),
-    "roster_saved_at_pass_end": ("            holds.pop(key, None)\n            save()\n", "            holds.pop(key, None)\n",
+    "roster_lease_ignored": ("        if lease is None:\n            break", "        if lease is None:\n            lease = os.open(os.devnull, 0)",
+                             "roster-drain: no op starts while an out-of-queue writer holds the roster lease; the next pass runs them"),
+    "roster_lease_released_early": ("        lease = roster_lib.writer_lease(ctx.state, 0)\n",
+                                    "        lease = roster_lib.writer_lease(ctx.state, 0)\n        lease = lease and os.close(lease) or (None if lease is None else os.open(os.devnull, 0))\n",
+                                    "roster-drain: no op starts while an out-of-queue writer holds the roster lease; the next pass runs them"),
+    "roster_refusal_no_event": ('        event(ctx, f"ROSTER-REFUSED #{n} {text}")', '        pass',
+                                "roster-drain: a refused op writes one events line that survives a following applied pass"),
+    "roster_refused_as_done": ("    def refuse(key: str) -> None:  # the job file is replaced by the next pass that runs an op; events.txt is not\n        refused.add(key)",
+                               "    def refuse(key: str) -> None:  # the job file is replaced by the next pass that runs an op; events.txt is not\n        done.add(key)",
+                               "roster-drain: a refused key is remembered apart from the applied ones"),
+    "roster_refused_retried": ("        if key in done or key in refused:", "        if key in done:",
+                               "roster-drain: a refused op writes one events line that survives a following applied pass"),
+    "roster_saved_at_pass_end": ("        holds.pop(key, None)\n        save()\n", "        holds.pop(key, None)\n",
                                  "roster-drain: a pass killed mid-queue keeps its applied ops; the next applies each once"),
     "roster_pass_unbounded": ("        if ctx.clock() - start >= ROSTER_PASS_BUDGET_S:", "        if False:",
                               "roster-drain: a pass past ROSTER_PASS_BUDGET_S starts no op; the next pass resumes"),
@@ -1347,12 +1417,14 @@ MUTANTS = {
                                 "roster-drain: a cleared queue is refused as QUEUE-SHRANK, stays refused, and nothing runs"),
     "roster_shrink_ignored": ("    if len(whole) < seen or ", "    if False and ",
                               "roster-drain: a cleared queue is refused as QUEUE-SHRANK, stays refused, and nothing runs"),
-    "roster_noop_marked": ('        if mark != op or not any("no op attempted" in ln for ln in said):', '        if True:',
+    "roster_noop_marked": ('        elif mark != op or not any("no op attempted" in ln for ln in said):', '        elif True:',
                            "roster-drain: a no-op-attempted report is retried on the next pass"),
     "plan_rc2_unavailable": ('word = "PLAN UNAVAILABLE" if rc == 1 else "REFUSED"', 'word = "PLAN UNAVAILABLE"',
                              "plan-beat: state_docs rc 2 is REFUSED, not PLAN UNAVAILABLE"),
-    "plan_replan_args_dropped": ('"--out", plan, "--slots", slots, "--seats", seats, *cap)', '"--out", plan, *cap)',
+    "plan_replan_args_dropped": ('"--out", plan, "--slots", slots, "--seats", seats,\n                        *cap, *evidence)', '"--out", plan,\n                        *cap, *evidence)',
                                  "plan-beat: replan is handed the plan, slots and seats"),
+    "plan_evidence_dropped": ('            evidence += [flag, str(ctx.overlay[key])]', '            pass',
+                              "plan-beat: the overlay's ref listing and in-flight PRs reach replan (liveness by evidence)"),
     "pulse_unreadable_ignored": ("    if rc not in (0, 1, 2) or not out:", "    if not out:",
                                  "pulse: an rc outside 0-2 is UNREADABLE, whatever it printed"),
     "pulse_alive_dropped": ('        args += ["--seat-alive", e]', '        pass',
@@ -1374,7 +1446,7 @@ MUTANTS = {
                                          "tick-digest: a transient NOT REVIEWABLE gives nothing; on a second board it appears"),
     "roster_hold_op_unstripped": ("            op = parts[2]\n", "",
                                   "roster-drain: a released hold hands roster_queue the held op, not the hold line"),
-    "roster_malformed_hold_retried": ('lines.append(f"roster: refused malformed hold line: {text}")\n                done.add(key)',
+    "roster_malformed_hold_retried": ('lines.append(f"roster: refused malformed hold line: {text}")\n                refuse(key)',
                                       'lines.append(f"roster: refused malformed hold line: {text}")',
                                       "roster-drain: a malformed hold line is refused once and marked, never re-printed"),
     "plan_mirror_dropped": ('"--push", "--mirror", mirror, "--plan", plan, *train)', '"--push", "--plan", plan, *train)',
diff --git a/tools/audit/seat/carry_fold.py b/tools/audit/seat/carry_fold.py
index 0f1cdc2510..29e330376c 100755
--- a/tools/audit/seat/carry_fold.py
+++ b/tools/audit/seat/carry_fold.py
@@ -2,7 +2,7 @@
 """carry_fold.py -- the orchestrator writes each `Carry: <GROUP>` body item into its destination brief.
 
     python3 tools/audit/seat/carry_fold.py --body FILE --pr '#N' --topic T --worktree DIR
-        [--checkout DIR] [--roster-ref REF] [--branch BR]
+        [--checkout DIR] [--roster-ref REF] [--branch BR] [--state-dir D]
     python3 tools/audit/seat/carry_fold.py --self-test
 
 WHY. A seat that cannot write the roster strands its carry: `body_push.sh` refuses a body whose
@@ -17,6 +17,10 @@ Refusals (rc 1, nothing written for the first): a body item whose destination is
 (`bad destination`); an item still missing after the fold. rc 0: nothing missing, or all folded and
 asserted. rc 3: the roster is unreadable. The merge-time writer is `roster_sync.py`; this runs
 before it and `roster_edit.py` refuses an exact repeat, so the two never double-write.
+THE LEASE. The fold writes while holding roster_lib's writer lease in the beat's state directory
+(`--state-dir`, default `$HPO_STATE_DIR`), waiting up to LEASE_WAIT_S for the drain's op in flight;
+the drain starts no op while the fold holds it, so the two no longer race one push loop against the
+other. A lease still held past the wait is rc 1, `REFUSED`, nothing written.
 `--self-test` prints `carry_fold self-test: N checks, 0 failed`.
 """
 from __future__ import annotations
@@ -33,6 +37,21 @@ sys.path.insert(0, str(HERE.parent))
 import carry_audit  # noqa: E402
 import roster_lib  # noqa: E402
 
+#: One drain op is a lint and a push loop (1.5-4 min a lint, triage sweep 1520); two ops' worth.
+LEASE_WAIT_S = 600
+
+
+def leased(state_dir, wait_s: float, write, lease=roster_lib.writer_lease) -> tuple[int, list[str]]:
+    """`write()`'s (rc, lines), run holding the roster writer lease; a refusal when it stays held."""
+    fd = lease(state_dir, wait_s)
+    if fd is None:
+        return 1, [f"carry_fold: REFUSED the roster writer lease in {state_dir} is still held after {wait_s:.0f} s "
+                   "(the drain's op in flight); nothing written"]
+    try:
+        return write()
+    finally:
+        os.close(fd)
+
 
 def fold(body: str, load, apply, pr: str = "", topic: str = "") -> tuple[int, list[str]]:
     """(rc, lines). `load()` reads the destination roster as a `Dests` now; `apply(op)` runs one
@@ -69,6 +88,7 @@ def main(argv=None) -> int:
     p.add_argument("--checkout", default=".")
     p.add_argument("--roster-ref", default=None)
     p.add_argument("--branch", default=None)
+    p.add_argument("--state-dir", default=os.environ.get("HPO_STATE_DIR") or str(Path.home() / ".local/state/hpo"))
     a = p.parse_args(argv)
     git = roster_lib.git_in(a.checkout)
     branch = a.branch or a.roster_ref or roster_lib.round_ref(git)
@@ -88,7 +108,8 @@ def main(argv=None) -> int:
                                          "--branch", branch, "--push"])
 
     try:
-        rc, lines = fold(Path(a.body).read_text(), load, apply, a.pr, a.topic)
+        body = Path(a.body).read_text()
+        rc, lines = leased(a.state_dir, LEASE_WAIT_S, lambda: fold(body, load, apply, a.pr, a.topic))
     except (roster_lib.RosterNotFound, ValueError, OSError) as e:
         print(f"carry_fold: UNREAD the roster: {e}")
         return 3
@@ -148,6 +169,48 @@ def _self_test() -> int:
     state["R10-DEST"]["carry"].clear()
     rc, out = fold(body, load, lambda op: 2, "#9", "r10-x")
     check("a failed write refuses and says so", rc == 1 and "REFUSED" in out[-1])
+    import tempfile
+    with tempfile.TemporaryDirectory() as st:
+        inside = []
+
+        def write():  # a drain op starting now takes the lease without waiting
+            fd = roster_lib.writer_lease(st, 0)
+            inside.append(fd is None)
+            if fd is not None:
+                os.close(fd)
+            return 0, ["wrote"]
+        check("the fold writes holding the lease: a drain op cannot start meanwhile",
+              leased(st, 0, write) == (0, ["wrote"]) and inside == [True])
+        drain = roster_lib.writer_lease(st, 0)
+        inside.clear()
+        rc, out = leased(st, 0, write)
+        check("a lease the drain holds past the wait refuses the fold, nothing written",
+              rc == 1 and "REFUSED" in out[0] and inside == [])
+        os.close(drain)
+        check("null control: a free lease runs the fold once", leased(st, 0, write)[0] == 0 and inside == [True])
+    import contextlib
+    import io
+    global LEASE_WAIT_S
+    wait, LEASE_WAIT_S = LEASE_WAIT_S, 0
+    try:
+        with tempfile.TemporaryDirectory() as st, tempfile.TemporaryDirectory() as co:
+            (Path(st) / "body.md").write_text(body)
+            argv = ["--body", str(Path(st) / "body.md"), "--worktree", co, "--checkout", co,
+                    "--branch", "handoff/audit-r10-roster", "--state-dir", st]
+            drain = roster_lib.writer_lease(st, 0)
+            said = io.StringIO()
+            with contextlib.redirect_stdout(said):
+                rc = main(argv)
+            check("main folds holding the lease: a lease the drain holds refuses before any roster read",
+                  rc == 1 and "REFUSED the roster writer lease" in said.getvalue())
+            os.close(drain)
+            said = io.StringIO()
+            with contextlib.redirect_stdout(said):
+                rc = main(argv)
+            check("null control: with the lease free, main goes on to read the roster",
+                  "REFUSED the roster writer lease" not in said.getvalue())
+    finally:
+        LEASE_WAIT_S = wait
     print(f"carry_fold self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 095b3ceb2c..fa4a6c766b 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -920,6 +920,15 @@ fold_judge() { # <memo> <level> <topic> <wip sha> <body sha> <outcome> <epoch> <
   printf '%s %s %s %s %s %s %s%s\n' "$3" "$4" "${5:--}" "$6" "$7" "$8" "$9" "${10:+ ${10}}" >> "$1"; [ -z "${10:-}" ] || printf '%s\n' "${10}" >> "$2"; }
 fold_memo_stands() { # <outcome> <epoch> <now>: rc 0 while a judged outcome stands; a failure after the fold expires after 3600 s
   case $1:$2 in blocked:*|folded:*) return 0;; fold-failed:[0-9]*|push-failed:[0-9]*) [ $(($3 - $2)) -lt 3600 ];; *) return 1;; esac; }  # mut:foldttl
+fold_superseded() { # <topic> <wip sha> <handoff-body sha|empty> <merged fix branches file>: rc 0 when the topic moved on
+  # CARRY-FOLD-SUPERSEDED (P642): dispose refuses handoff-wip/ refs, so a stop whose topic returned a later body, or
+  # whose fix branch merged, stood on the carry-fold level until someone deleted the ref (14 of 20 lines, 2026-11-11).
+  grep -qxF -e "fix/$1" -e "fix/$1-pr" "$4" && return 0  # mut:foldmerged
+  [ -n "$3" ] || return 1
+  git fetch -q origin "refs/heads/handoff-wip/$1" "refs/heads/handoff-body/$1" 2>/dev/null || return 1
+  local w b; w=$(git log -1 --format=%ct "$2" 2>/dev/null) && b=$(git log -1 --format=%ct "$3" 2>/dev/null) || return 1
+  [ "$b" -gt "$w" ]  # mut:foldlater
+}
 carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md names CARRY-LANDED alone: fold the kept body's carries, re-run body_push.sh
   # A cloud fixer may not write the roster, so body_push.sh's CARRY-LANDED refusal (exit 4; each refusal prints
   # `body_push: REFUSED <KIND>` into the BLOCKED.md the fixer pushes) stranded it until a seat landed the carries
@@ -933,15 +942,20 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
   # stored line is set again, because level_set replaces the whole carry-fold level. A failure after the fold is judged
   # again once fold_memo_stands expires it: an ancestry red can clear with no ref moving. The body is pushed from a
   # worktree at a private ref fetched from handoff/<topic>, deleted after the push, never FETCH_HEAD, which a concurrent
-  # fetch in this checkout overwrites, and only at that ref's ls-remote tip (P556).
+  # fetch in this checkout overwrites, and only at that ref's ls-remote tip (P556). A topic fold_superseded reads as
+  # moved on (a later handoff-body/<topic>, or fix/<topic>[-pr] merged into origin/main by a local git log) is skipped:
+  # no level line, no fold, no memo.
   local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head mb mh blob fo fe fb fh fl rt
-  git ls-remote origin 'refs/heads/handoff-wip/*' 'refs/heads/handoff/*' > "$state/cloud-wip.$$" \
+  git ls-remote origin 'refs/heads/handoff-wip/*' 'refs/heads/handoff/*' 'refs/heads/handoff-body/*' > "$state/cloud-wip.$$" \
     || { echo "cloud_relay: could not list handoff-wip refs; the carry-fold level stays as it was" >&2; rm -f "$state/cloud-wip.$$"; return 0; }
   memo=$state/cloud-fold-judged; now=$(date +%s)
   mkdir -p "$state"; : > "$state/cloud-level-fold.$$"; : > "$memo.$$"
+  git log --merges --format=%s origin/main 2>/dev/null | sed -n 's|^Merge pull request #[0-9]* from [^/]*/\(fix/.*\)$|\1|p' > "$state/cloud-merged.$$"
   while read -r sha ref; do
     case $ref in refs/heads/handoff-wip/*) topic=${ref#refs/heads/handoff-wip/};; *) continue;; esac
     case $topic in ''|*/*|*-body|*-carries|*-body-*) continue;; esac
+    fold_superseded "$topic" "$sha" "$(awk -v r="refs/heads/handoff-body/$topic" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")" \
+      "$state/cloud-merged.$$" && continue  # mut:foldsuperseded
     bsha=$(awk -v r="refs/heads/handoff-wip/$topic-body" '$2 == r { print $1; exit }' "$state/cloud-wip.$$")
     htip=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-wip.$$"); blob=-
     mo= me= ml= mb= mh=; [ -f "$memo" ] && read -r _ _ _ mo me mb mh ml < <(awk -v t="$topic" -v w="$sha" -v b="${bsha:--}" '$1 == t && $2 == w && $3 == b { print; exit }' "$memo")
@@ -995,7 +1009,7 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
     else fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" push-failed "$now" "$blob" "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "$why")"
     fi
   done < "$state/cloud-wip.$$"
-  mv -f "$memo.$$" "$memo"; level_set carry-fold "$state/cloud-level-fold.$$"; rm -f "$state/cloud-wip.$$"
+  mv -f "$memo.$$" "$memo"; level_set carry-fold "$state/cloud-level-fold.$$"; rm -f "$state/cloud-wip.$$" "$state/cloud-merged.$$"
 }
 
 pass() { # [--confirm] [--log FILE] [--loop [--interval N]]
@@ -2233,6 +2247,24 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   awk '$1 == "cf-l" { $6 = ""; $7 = ""; gsub(/  +/, " ") } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
   : > "$t/fetches"; cfo=$(git() { [ "$1" != fetch ] || echo "$*" >> "$t/fetches"; command git "$@"; }; carry_fold_arm 2>&1)
   chk "a memo record from before the blob and tip fields is judged again, not read with shifted fields" 0 grep -q "handoff-wip/cf-l\$" "$t/fetches"
+  # CARRY-FOLD-SUPERSEDED (P642): a stop whose topic returned a later handoff-body, or whose fix branch merged, leaves the level.
+  GIT_COMMITTER_DATE="2010-01-01T00:00:00Z" cfref handoff-wip/cf-n BLOCKED.md "the fixer is stuck"
+  GIT_COMMITTER_DATE="2011-01-01T00:00:00Z" cfref handoff-body/cf-n BODY.md "the returned body N"
+  GIT_COMMITTER_DATE="2012-01-01T00:00:00Z" cfref handoff-wip/cf-o BLOCKED.md "the fixer is stuck"
+  GIT_COMMITTER_DATE="2011-01-01T00:00:00Z" cfref handoff-body/cf-o BODY.md "an earlier body O"
+  cfref handoff-wip/cf-p BLOCKED.md "body_push: REFUSED CARRY-LANDED"; cfref handoff-wip/cf-p-body BODY.md "the body P"
+  cfref handoff-wip/cf-q BLOCKED.md "the fixer is stuck"
+  rm -rf "$t/cfx"; throwaway_git_init "$t/cfx" -q; git -C "$t/cfx" commit -q --allow-empty -m base
+  git -C "$t/cfx" commit -q --allow-empty -m side; git -C "$t/cfx" reset -q --hard HEAD~1
+  git -C "$t/cfx" merge -q --no-ff -m "Merge pull request #9 from o/fix/cf-p-pr" HEAD@{1}
+  git -C "$t/cf.git" fetch -qf "$t/cfx" "HEAD:refs/heads/main"; git fetch -q origin main
+  : > "$t/folds"; cfo=$(carry_fold_arm 2>&1)
+  chk "a stop with a later handoff-body/<topic> leaves the carry-fold level (P642)" 1 grep -q "handoff-wip/cf-n " "$LOG.level"
+  chk "... and prints no OWED line" 1 grep -q "OWED carry-fold cf-n " <<< "$cfo"
+  chk "a stop whose fix/<topic>-pr merged into origin/main leaves the level" 1 grep -q "handoff-wip/cf-p " "$LOG.level"
+  chk "... and folds nothing, though its stop is CARRY-LANDED alone with a kept body" 1 grep -q -- "--topic cf-p " "$t/folds"
+  chk "null control: a handoff-body older than the stop keeps its OWED line" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-o " "$LOG.level"
+  chk "null control: a stop with no handoff-body and no merge keeps its OWED line" 0 grep -q "carry-fold refs/heads/handoff-wip/cf-q " "$LOG.level"
   # OWED-RED-TEXT-TO-CLOUD: a PREDICTOR refusal naming an owed red attaches that check's name, conclusion and error lines
   printf '#!/bin/sh\nprintf "tests / fast (3.14)\\npr-contract / pr-contract\\n"\n' > "$t/owedstub"
   printf '#!/bin/bash\necho "$1 $2" >> %s/fl.calls; printf "tests / fast (3.14)\\tfailure\\t9\\tu\\n" > "$2/failing.tsv"\necho "head %s"; printf "tests / fast (3.14)\\t9\\t8\\tf.log\\n    12:FAILED test_x\\n"; echo "failing checks: 1"\n' "$t" "$h" > "$t/flstub"
diff --git a/tools/audit/seat/instruments/plan_audit.py.md b/tools/audit/seat/instruments/plan_audit.py.md
index 029f0bc762..372f377ad5 100644
--- a/tools/audit/seat/instruments/plan_audit.py.md
+++ b/tools/audit/seat/instruments/plan_audit.py.md
@@ -1,7 +1,7 @@
 # `plan_audit.py`
 
-- `plan_audit.py` — P3's measuring half (R10-FLOW-AUDIT-PLAN), beside the
-  `audit-plan` workflow. `ledger` parses each merged PR's
+- `plan_audit.py` — P3's measuring half (R10-FLOW-AUDIT-PLAN, R11-ARCH-OBJECTIVE),
+  beside the `audit-plan` workflow. `ledger` parses each merged PR's
   `## Architecture score` block with the parser `score.py`'s own report
   answers to, reconciles it metric by metric against `PLAN.json`'s moves, and
   demands the moves' sum account for `score.py --diff <fork> HEAD` within
@@ -17,3 +17,33 @@
   the stamp compares it. Refusal: `ARCHSCORE_ABLATE` set; a plan naming a
   different fork; two snapshots read by different instruments; `--self-test`
   (`governance.yml` greps its `checks, 0 failed` line).
+- **The objective (decision 0018).** `PLAN.json`'s `objective` block holds
+  only `OBJECTIVE_KEYS`: `baseline` (the previous round's record, `BASELINE`),
+  `pin` (draft roster path and blob at the plan SHA, `--start`, the durations
+  blob), `terms` (each of `objective.json`'s, `up`/`down`/`hold` with a basis,
+  or `undecided` with a builder: the only value for a term NO-READ in the
+  baseline), `groups` (per planned group a `rank` its keys must give: 1 for a
+  verified `bug` finding or a `REGISTERED` id (an `in` row of the baseline's
+  escapes ledger, an open card by `check_scopes.py --open-cards`, a bug class);
+  else 2, with `examined_by`), `edges` (`from`, `to`, `adr`) and `dispositions`.
+  `objective-check --ref <plan SHA>` reads every input at that SHA and runs
+  that SHA's `replan.py` twice with the pin: A on the draft, B on A less every
+  rank-2 group no rank-1 group reaches through `after`, written under the
+  draft's basename. The floor cost is A less B; lead time is finish less the
+  pinned start, 0018's roster-entry clock. `--write` puts the derived figures
+  and the pin, never the plans or `VERSION`, in the projection record
+  beside the plan (its basename PROJECTION.json); without it a record unequal to the re-run's bytes refuses. Refusals:
+  no block, a key outside the grammar (a time-shaped one as authored time), a
+  verified bug deferred with no card, an unknown or doubly closed finding, an
+  unregistered escape, card or class, a baseline other than `BASELINE` of
+  round N-1 and one blob at the plan SHA, its tree and main's merge base
+  (`--main`), a rank its keys contradict, a rank-2 group with no
+  `examined_by`, a rank-1 group waiting on a rank-2 group with no `edges` ADR
+  among the moves, an open group A schedules with no rank, a ranked done
+  group (B keeps every done group), a stale pin, a B not that reduction, and a MISSED line of
+  `--previous` with no disposition. `settle` prints HELD, MISSED, UNDECIDED,
+  NOT-DUE or UNPREDICTED per prediction; only a HELD keyed effect credits a
+  term (`KEYED_TERMS`), cause, re-report and escape keys settle at the next
+  round's close, and a record without `keyed.<kind>` rows settles those
+  UNDECIDED. Not caught: whether an escape's seam is the group's, and a slot
+  or hot-file turn `replan.py` does not model (plan review's).
diff --git a/tools/audit/seat/plan_audit.py b/tools/audit/seat/plan_audit.py
index c1fd317d2a..81278ab280 100644
--- a/tools/audit/seat/plan_audit.py
+++ b/tools/audit/seat/plan_audit.py
@@ -6,6 +6,10 @@
         --fork SHA --head REF [--tolerance 1.0] [--json OUT]
     python3 tools/audit/seat/plan_audit.py snapshot --ref SHA [--instrument REF] --out FILE
     python3 tools/audit/seat/plan_audit.py compare --fork FILE --stamp FILE [--allow KIND:KEY]...
+    python3 tools/audit/seat/plan_audit.py objective-check --ref SHA --plan PATH --register PATH \\
+        [--previous SETTLEMENT.json] [--write]
+    python3 tools/audit/seat/plan_audit.py settle --plan PLAN.json --record OBJECTIVE.json \\
+        [--bodies DIR] [--json OUT]
     python3 tools/audit/seat/plan_audit.py --self-test
 
 R10-FLOW-AUDIT-PLAN. The architect's plan (`plan/r<N>`, `dev/governance/roles/
@@ -405,6 +409,582 @@ def snapshot(ref: str, instrument: str | None) -> dict:
             _drop_worktree(inst)
 
 
+# ------------------------------------------------------- the objective (0018)
+#
+# R11-ARCH-OBJECTIVE. Decision 0018's objective ranks the plan's work; the
+# score stays the floor `reconcile` and `compare` read. The plan commits to an
+# `objective` block in PLAN.json (the grammar is OBJECTIVE_KEYS); `check_block`
+# refuses a block that games either number, and `settle` credits a lagging read
+# only through a keyed effect. Hours stay `tools/plan/replan.py`'s: the check
+# runs it twice at the plan's pin and derives every time figure from the two
+# projections, never from the block.
+
+OBJECTIVE_CONFIG = Path("dev/audit/config/objective.json")
+BUGCLASSES = Path("dev/audit/config/bugclasses.json")
+REPLAN = Path("tools/plan/replan.py")
+# 0018 section 2's "target; direction" column: the way each term improves. A
+# design choice: objective.json carries no direction, so the self-test pins this
+# table's keys to that file's `terms` and an unknown term refuses.
+BETTER = {"regret": "down", "operation": "up", "generality": "up", "unowned": "down",
+          "escapes": "down", "injected": "down", "product_green": "up", "coverage": "up",
+          "unexamined": "down", "first_pass": "up", "lead_time": "down",
+          "closure_slip": "down", "tokens_per_change": "down"}
+RELATIVE_BAND = {"lead_time": "band_lead_time", "closure_slip": "band_closure_slip",
+                 "tokens_per_change": "band_tokens_per_change"}
+VERIFIED = ("verified", "weakened")
+DIRECTIONS = ("up", "down", "hold", "undecided")
+# Each keyed effect, and the terms its HELD line credits.
+# Every rank-1 key but `removes` (checked against the judge register), with the
+# register its ids must name: derived_rank and check_block both read this table,
+# so a rank-1 key cannot be added without a register (#3703 review, item 1).
+REGISTERED = {"escapes": ("escape", "the baseline's escapes ledger, ruled `in`"),
+              "cards": ("card", "the round's open cards, check_scopes.py --open-cards"),
+              "classes": ("class", "bugclasses.json")}
+BASELINE = "dev/audit/yardstick/round{}/OBJECTIVE.json"
+KEYED_TERMS = {"removes": ("escapes",), "escapes": ("escapes", "unowned"),
+               "classes": ("escapes", "injected"), "cards": (), "examined_by": ("unexamined",),
+               "injected": ("injected",), "rereport": ("escapes",)}
+OBJECTIVE_KEYS = {
+    "": {"baseline", "pin", "terms", "groups", "edges", "dispositions"},
+    "baseline": {"record", "tree"},
+    "pin": {"roster_path", "roster_blob", "start", "durations_blob"},
+    "term": {"direction", "basis", "builder"},
+    "group": {"rank", "removes", "escapes", "classes", "cards", "examined_by"},
+    "edge": {"from", "to", "adr"},
+}
+_TIME_KEY = re.compile(r"hour|chain|critical|closure|lead|wall|finish|start|eta|date|slip", re.I)
+_FRACTION = re.compile(r"(\d+)/(\d+)")
+
+
+def _grammar(block: dict) -> list[str]:
+    """Every key outside OBJECTIVE_KEYS, one line each; a time-shaped key is
+    named as authored time, since the projections own every hour."""
+    bad = []
+
+    def keys(obj, level: str, where: str) -> None:
+        if not isinstance(obj, dict):
+            bad.append(f"SHAPE {where or 'objective'}: not an object")
+            return
+        for key in obj:
+            if key not in OBJECTIVE_KEYS[level]:
+                kind = "AUTHORED time" if _TIME_KEY.search(key) else "UNKNOWN key"
+                bad.append(f"{kind} {where + '.' if where else ''}{key}: the block's grammar "
+                           f"is OBJECTIVE_KEYS; hours are replan.py's projections")
+    keys(block, "", "")
+    for level in ("baseline", "pin"):
+        keys(block.get(level, {}), level, level)
+    for term, entry in (block.get("terms") or {}).items():
+        keys(entry, "term", f"terms.{term}")
+    for group, entry in (block.get("groups") or {}).items():
+        keys(entry, "group", f"groups.{group}")
+    for i, edge in enumerate(block.get("edges") or []):
+        keys(edge, "edge", f"edges[{i}]")
+    return bad
+
+
+def derived_rank(entry: dict, bugs: set[str]) -> int:
+    """1 when the group carries a layer-1 key (a verified `bug` finding, an
+    escape row, an open card or an open class); 2 otherwise."""
+    if any(f in bugs for f in entry.get("removes") or []):
+        return 1
+    return 1 if any(entry.get(kind) for kind in REGISTERED) else 2
+
+
+def after_closure(name: str, projected: dict) -> set[str]:
+    """Every group `name` waits on through `after`, read off a replan.py plan."""
+    seen, todo = set(), list((projected.get(name) or {}).get("after") or [])
+    while todo:
+        cur = todo.pop()
+        if cur not in seen:
+            seen.add(cur)
+            todo.extend((projected.get(cur) or {}).get("after") or [])
+    return seen
+
+
+def kept_in_floor(block: dict, projected: dict) -> set[str]:
+    """Projection B's group names: projection A's less every open rank-2 group
+    no rank-1 group reaches through `after`. A done group stays, ranked or not:
+    A omits the `after` edges to it that the roster still names, and replan.py
+    refuses a roster whose edge names no group. Edges are A's, so no roster
+    grammar is re-declared here."""
+    ranks = {g: e.get("rank") for g, e in (block.get("groups") or {}).items()
+             if isinstance(e, dict)}
+    reached = set()
+    for group, rank in ranks.items():
+        if rank == 1:
+            reached |= after_closure(group, projected)
+    return {g for g, e in projected.items() if e.get("done") or ranks.get(g) != 2 or g in reached}
+
+
+def reduced_roster(roster: dict, keep: set[str]) -> dict:
+    return {**roster, "groups": [g for g in roster.get("groups") or [] if g.get("group") in keep]}
+
+
+def _hours(later: str, earlier: str) -> float:
+    from datetime import datetime
+    fmt = "%Y-%m-%dT%H:%M:%SZ"
+    return round((datetime.strptime(later, fmt) - datetime.strptime(earlier, fmt)).total_seconds()
+                 / 3600, 2)
+
+
+def _rank_pct(values: list[float], pct: int) -> float | None:
+    """Nearest-rank percentile; None over no value."""
+    if not values:
+        return None
+    ordered = sorted(values)
+    return ordered[max(0, -(-pct * len(ordered) // 100) - 1)]
+
+
+def projection_record(block: dict, a: dict, b: dict, production: set[str]) -> dict:
+    """The derived figures and the pin: never the two plans, and nothing the
+    checkout's VERSION writes (`generated.version`, `closure_stamp`)."""
+    start = a["generated"]["start"]
+    ranks = {g: e.get("rank") for g, e in (block.get("groups") or {}).items()}
+    lead = [_hours(g["finish"], start) for name, g in a["groups"].items()
+            if name in production and g.get("finish")]
+    delay = {}
+    for name, rank in sorted(ranks.items()):
+        fa, fb = (a["groups"].get(name) or {}).get("finish"), (b["groups"].get(name) or {}).get("finish")
+        if rank == 1 and fa and fb:
+            delay[name] = _hours(fa, fb)
+    return {
+        "pin": {**block.get("pin", {}), "caps": a["generated"].get("caps")},
+        "production": sorted(production),
+        "a": {"critical_path_hours": a["binding"]["critical_path_hours"],
+              "wall_hours": a["summary"]["wall_hours"], "closure": a["summary"]["closure"],
+              "lead_time_p50_hours": _rank_pct(lead, 50), "lead_time_p90_hours": _rank_pct(lead, 90)},
+        "b": {"critical_path_hours": b["binding"]["critical_path_hours"],
+              "wall_hours": b["summary"]["wall_hours"], "closure": b["summary"]["closure"],
+              "dropped": sorted(set(a["groups"]) - set(b["groups"]))},
+        "floor_cost": {
+            "critical_path_hours": round(a["binding"]["critical_path_hours"]
+                                         - b["binding"]["critical_path_hours"], 2),
+            "wall_hours": round(a["summary"]["wall_hours"] - b["summary"]["wall_hours"], 2),
+            "delay_hours": delay},
+    }
+
+
+def projection_refusals(block: dict, a: dict, b: dict) -> list[str]:
+    """Projection A is the pinned roster, B is exactly its floor reduction."""
+    bad = []
+    pin = block.get("pin") or {}
+    if a["generated"].get("roster_blob") != pin.get("roster_blob"):
+        bad.append(f"STALE pin: projection A read roster blob {a['generated'].get('roster_blob')!r}, "
+                   f"the plan pins {pin.get('roster_blob')!r}")
+    if a["generated"].get("start") != pin.get("start") or b["generated"].get("start") != pin.get("start"):
+        bad.append(f"STALE pin: the projections start at {a['generated'].get('start')!r} and "
+                   f"{b['generated'].get('start')!r}, the plan pins {pin.get('start')!r}")
+    want = kept_in_floor(block, a["groups"])
+    for extra in sorted(set(b["groups"]) - want):
+        bad.append(f"REDUCED roster keeps {extra}: a rank-2 group no rank-1 group reaches "
+                   f"through `after`, so the floor cost reads smaller than it is")
+    for gone in sorted(want - set(b["groups"])):
+        bad.append(f"REDUCED roster drops {gone}: B is A less the unreached rank-2 groups only")
+    return bad
+
+
+def escape_rows(ledger: str) -> set[str]:
+    """The groups an escapes ledger (a TSV under its `#` header) rules `in`."""
+    rows = [ln.split("\t") for ln in ledger.splitlines() if ln and not ln.startswith("#")]
+    if not rows or "group" not in rows[0] or "ruling" not in rows[0]:
+        return set()
+    g, r = rows[0].index("group"), rows[0].index("ruling")
+    return {row[g] for row in rows[1:] if len(row) > max(g, r) and row[r] == "in"}
+
+
+def baseline_refusals(plan: dict, baseline: dict, blobs: dict) -> list[str]:
+    """The baseline is derived, never the plan's choice: the previous round's
+    record at BASELINE, of that round, and the same blob at the plan SHA, at
+    any `baseline.tree` and where the plan's branch left main (#3703 review,
+    item 2). `blobs` maps each of those reads to its blob id, None if absent."""
+    rnd = (plan.get("round") or 0) - 1
+    want = BASELINE.format(rnd)
+    got = (((plan.get("objective") or {}).get("baseline")) or {}).get("record")
+    bad = []
+    if got != want:
+        bad.append(f"BASELINE {got!r}: the baseline is the previous round's record, {want}")
+    if baseline.get("round") != rnd:
+        bad.append(f"BASELINE round {baseline.get('round')!r}: {want} must record round {rnd}")
+    if blobs.get("plan") is None or len(set(blobs.values())) > 1:
+        bad.append(f"BASELINE edited: {want} is not one blob at the plan SHA, its tree and "
+                   f"main's merge base ({', '.join(f'{k} {v}' for k, v in sorted(blobs.items()))})")
+    return bad
+
+
+def check_block(plan: dict, register: list[dict], baseline: dict, terms: list[str],
+                previous: list[dict] | None, projected: dict, known: dict) -> list[str]:
+    """The P3 check on the plan's objective block, one refusal per line.
+
+    `register` is the judge's verdict list, `baseline` the previous round's
+    objective record, `terms` objective.json's, `previous` the previous plan's
+    settlement lines (None for a first plan), `projected` projection A's
+    `groups` and `known` each REGISTERED key's ids.
+    """
+    block = plan.get("objective")
+    if not isinstance(block, dict):
+        return ["NO objective block: PLAN.json commits to one (0018, architect-planner.md)"]
+    bad = _grammar(block)
+    ids = {f.get("id") for f in register}
+    bugs = {f["id"] for f in register
+            if f.get("verdict") in VERIFIED and f.get("stop_rule_class") == "bug"}
+    for row in plan.get("triage") or []:
+        if row.get("id") in bugs and row.get("verdict") == "defer" and not row.get("card"):
+            bad.append(f"DEFERRED bug {row['id']}: a verified `bug` finding deferred with no card "
+                       f"(its lead_time is bought with the round's)")
+    stated = block.get("terms") or {}
+    for term in terms:
+        entry = stated.get(term)
+        if not isinstance(entry, dict) or entry.get("direction") not in DIRECTIONS:
+            bad.append(f"TERM {term}: no predicted direction, one of {', '.join(DIRECTIONS)}")
+            continue
+        unread = "value" not in ((baseline.get("terms") or {}).get(term) or {})
+        if unread and entry["direction"] != "undecided":
+            bad.append(f"NO-READ {term} predicted {entry['direction']!r}: a term NO-READ in the "
+                       f"baseline takes only \"undecided\" with its builder")
+        if entry["direction"] == "undecided" and unread and not entry.get("builder"):
+            bad.append(f"NO-READ {term} undecided with no builder")
+        if entry["direction"] != "undecided" and not entry.get("basis"):
+            bad.append(f"TERM {term}: a predicted direction with no basis")
+    for term in sorted(set(stated) - set(terms)):
+        bad.append(f"TERM {term}: not a term of objective.json")
+    named = {g.get("group") for g in plan.get("groups") or []}
+    entries = block.get("groups") or {}
+    for group in sorted(named - set(entries)):
+        bad.append(f"RANK {group}: a planned group with no objective entry")
+    for group in sorted(set(entries) - named):
+        bad.append(f"RANK {group}: an objective entry for no planned group")
+    owner: dict[str, str] = {}
+    for group, entry in sorted(entries.items()):
+        if not isinstance(entry, dict):
+            continue
+        for fid in entry.get("removes") or []:
+            if fid not in ids:
+                bad.append(f"UNKNOWN finding {group} {fid}: not in the register")
+            elif fid in owner:
+                bad.append(f"DOUBLE closure {fid}: {owner[fid]} and {group} both remove it")
+            else:
+                owner[fid] = group
+        for kind, (noun, source) in REGISTERED.items():
+            for item in entry.get(kind) or []:
+                if item not in (known.get(kind) or set()):
+                    bad.append(f"UNKNOWN {noun} {group} {item}: not in {source}")
+        want = derived_rank(entry, bugs)
+        if entry.get("rank") != want:
+            bad.append(f"RANK {group} declares {entry.get('rank')!r}, its keys make it {want}")
+        if want == 2 and not entry.get("examined_by"):
+            bad.append(f"UNEXAMINED move {group}: a rank-2 group names the finder pass that "
+                       f"examines its diff before the close")
+    adrs = {m.get("adr") for m in plan.get("moves") or [] if m.get("adr")}
+    edges = {(e.get("from"), e.get("to")): e.get("adr") for e in block.get("edges") or []
+             if isinstance(e, dict)}
+    for group, entry in sorted(entries.items()):
+        if not isinstance(entry, dict) or entry.get("rank") != 1:
+            continue
+        for waits in sorted(after_closure(group, projected)):
+            if (entries.get(waits) or {}).get("rank") == 2 and edges.get((group, waits)) not in adrs:
+                bad.append(f"RANK edge {group} after {waits}: a rank-1 group waits on a rank-2 "
+                           f"group with no ADR among the plan's moves")
+    for name, g in sorted(projected.items()):
+        if not g.get("done") and name not in entries:
+            bad.append(f"UNRANKED open group {name}: projection A schedules it and the plan "
+                       f"gives it no rank")
+        elif g.get("done") and name in entries:
+            bad.append(f"RANKED done group {name}: a done group is kept unranked, and B keeps it")
+    dispositions = block.get("dispositions") or {}
+    for line in previous or []:
+        if line.get("status") == "MISSED" and not dispositions.get(line.get("key")):
+            bad.append(f"UNDISPOSED {line.get('key')}: the previous plan MISSED it; name a "
+                       f"group or a card")
+    return bad
+
+
+# -------------------------------------------------------------- the settlement
+
+def term_reading(entry: dict | None) -> dict | None:
+    """A term's value per enumerator, each as a number or a (k, n) share;
+    None when the term is NO-READ."""
+    if not entry or "value" not in entry or entry["value"] is None:
+        return None
+    values = entry["value"] if isinstance(entry["value"], dict) else {"": entry["value"]}
+    counts = entry.get("counts") if isinstance(entry.get("counts"), dict) else {"": entry.get("counts")}
+    out = {}
+    for name, value in values.items():
+        share = None
+        for k, n in _FRACTION.findall(str(counts.get(name) or "")):
+            if int(n) and round(int(k) / int(n), 4) == round(float(value), 4):
+                share = (int(k), int(n))
+                break
+        out[name] = share if share else value
+    return out
+
+
+def moved(term: str, was, now, thresholds: dict) -> str | None:
+    """"up", "down" or "tie" beyond 0018's band; None when no band reads it."""
+    if term in RELATIVE_BAND:
+        band = (thresholds.get(RELATIVE_BAND[term]) or {}).get("value")
+        if band is None or not isinstance(was, (int, float)) or not isinstance(now, (int, float)):
+            return None
+        width = band * abs(was)
+    elif isinstance(was, tuple) and isinstance(now, tuple):
+        (k1, n1), (k2, n2) = was, now
+        p1, p2 = k1 / n1, k2 / n2
+        width = 2 * (p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) ** 0.5
+        was, now = p1, p2
+    elif isinstance(was, int) and isinstance(now, int) and not isinstance(was, bool):
+        width = 2 * (was + now) ** 0.5
+    else:
+        return None
+    if abs(now - was) <= width:
+        return "tie"
+    return "up" if now > was else "down"
+
+
+def _keyed(record: dict, kind: str) -> list[dict] | None:
+    rows = (record.get("keyed") or {}).get(kind)
+    return rows if isinstance(rows, list) else None
+
+
+def settle(plan: dict, baseline: dict, record: dict, merged: set[str], thresholds: dict,
+           production: set[str]) -> list[dict]:
+    """One line per prediction: HELD, MISSED, UNDECIDED, NOT-DUE or UNPREDICTED.
+
+    A record of the plan's own round settles the terms and the effects due at
+    its close (a removal, a card, an examining pass); cause, re-report and
+    escape keys fall due at the next round's close (0018 section 4 link 3), so
+    they print NOT-DUE until a record of round + 1 is given. A record carries
+    keyed rows under `keyed.<kind>`; a kind with none prints UNDECIDED.
+    """
+    block = plan.get("objective") or {}
+    entries = block.get("groups") or {}
+    due_next = record.get("round") == (plan.get("round") or 0) + 1
+    lines = []
+
+    def line(key: str, status: str, detail: str, terms=()) -> None:
+        lines.append({"key": key, "status": status, "detail": detail, "terms": list(terms)})
+
+    def next_round(key: str, kind: str, hit) -> None:
+        terms = KEYED_TERMS[kind]
+        if not due_next:
+            line(key, "NOT-DUE", "falls due at the next round's close", terms)
+        elif (rows := _keyed(record, kind)) is None:
+            line(key, "UNDECIDED", f"the record carries no keyed `{kind}` rows", terms)
+        else:
+            found = [r for r in rows if hit(r)]
+            line(key, "MISSED" if found else "HELD", f"{len(found)} keyed row(s) match", terms)
+
+    for group, entry in sorted(entries.items()):
+        if not due_next:
+            for kind in ("removes", "cards"):
+                for item in entry.get(kind) or []:
+                    status = "HELD" if group in merged else "MISSED"
+                    line(f"{group}:{kind}:{item}", status,
+                         "its group merged" if group in merged else "its group did not merge",
+                         KEYED_TERMS[kind])
+            if entry.get("rank") == 2:
+                rows = _keyed(record, "examined_by")
+                if rows is None:
+                    line(f"{group}:examined_by", "UNDECIDED",
+                         "the record carries no keyed `examined_by` rows", KEYED_TERMS["examined_by"])
+                else:
+                    seen = any(r.get("group") == group for r in rows)
+                    line(f"{group}:examined_by", "HELD" if seen else "MISSED",
+                         f"examined before the close: {seen}", KEYED_TERMS["examined_by"])
+        for fid in entry.get("removes") or []:
+            next_round(f"{group}:rereport:{fid}", "rereport", lambda r, f=fid: r.get("finding") == f)
+        for row in entry.get("escapes") or []:
+            next_round(f"{group}:escapes:{row}", "escapes", lambda r, k=row: r.get("key") == k)
+        for cid in entry.get("classes") or []:
+            next_round(f"{group}:classes:{cid}", "classes", lambda r, c=cid: r.get("class") == c)
+        if group in production:
+            next_round(f"{group}:injected", "injected", lambda r, g=group: r.get("group") == g)
+    if due_next:
+        return lines
+    credited = {t for ln in lines if ln["status"] == "HELD" for t in ln["terms"]}
+    for term, entry in sorted((block.get("terms") or {}).items()):
+        was = term_reading((baseline.get("terms") or {}).get(term))
+        now = term_reading((record.get("terms") or {}).get(term))
+        if was is None or now is None:
+            line(f"term:{term}", "UNDECIDED", "NO-READ on one side")
+            continue
+        for name in sorted(set(was) & set(now)):
+            key = f"term:{term}" + (f":{name}" if name else "")
+            move = moved(term, was[name], now[name], thresholds)
+            want, better = entry.get("direction"), BETTER.get(term)
+            worse = {"up": "down", "down": "up"}.get(better)
+            if move is None:
+                line(key, "UNDECIDED", "no band reads this term (unset, or no denominator)")
+            elif move == better and term not in credited:
+                line(key, "UNPREDICTED", f"moved {move} with no HELD keyed effect; not banked")
+            elif want in ("up", "down"):
+                line(key, "HELD" if move == want else "MISSED", f"moved {move}, predicted {want}")
+            elif want == "hold":
+                line(key, "MISSED" if move == worse else "HELD", f"moved {move}, predicted hold")
+            else:
+                line(key, "UNDECIDED", f"moved {move}, predicted undecided")
+    return lines
+
+
+def projection_differs(committed: str | None, rerun: dict) -> list[str]:
+    want = json.dumps(rerun, indent=1, sort_keys=True) + "\n"
+    if committed is None:
+        return ["PROJECTION missing: commit the record `objective-check --write` prints"]
+    if committed != want:
+        return ["PROJECTION differs: the committed record is not the re-run's bytes at the pin"]
+    return []
+
+
+# ------------------------------------------------- the objective's command line
+
+def _show(ref: str, path: str) -> str:
+    return git("show", f"{ref}:{path}") + "\n"
+
+
+def _json_at(ref: str, path: str):
+    return json.loads(_show(ref, path))
+
+
+def _replan(tree: Path, out: Path, *args: str) -> dict:
+    run = subprocess.run([sys.executable, str(tree / REPLAN), "--repo", str(ROOT), *args,
+                          "--out", str(out)], cwd=str(tree), capture_output=True, text=True)
+    if run.returncode != 0:
+        raise SystemExit(f"replan.py refused (rc={run.returncode}): "
+                         f"{(run.stderr or run.stdout).strip()[-400:]}")
+    return json.loads(out.read_text())
+
+
+def _blob(ref: str, path: str) -> str | None:
+    run = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "-q", f"{ref}:{path}"],
+                         capture_output=True, text=True)
+    return run.stdout.strip() if run.returncode == 0 else None
+
+
+def open_cards(tree: Path, ref: str, rnd: int) -> set[str]:
+    """`check_scopes.py --open-cards` at the plan SHA: the cards a group may name."""
+    run = subprocess.run([sys.executable, str(tree / "tools/audit/check_scopes.py"), "--repo", str(ROOT),
+                          "--ref", ref, "--round", str(rnd), "--open-cards", "--roster-ref", ref],
+                         cwd=str(tree), capture_output=True, text=True)
+    if run.returncode not in (0, 1):
+        raise SystemExit(f"check_scopes.py --open-cards refused (rc={run.returncode}): "
+                         f"{(run.stderr or run.stdout).strip()[-400:]}")
+    return set(json.loads(run.stdout.strip().splitlines()[-1]).get("open_cards") or [])
+
+
+def run_projections(tree: Path, ref: str, block: dict, roster: dict) -> tuple[dict, dict]:
+    """Projection A (the pinned roster at the plan SHA) and B (A less the
+    unreached rank-2 groups), both by replan.py at the plan SHA with the
+    pinned start and durations, so a later model or VERSION moves neither."""
+    pin = block["pin"]
+    with tempfile.TemporaryDirectory(prefix="plan-objective-") as tmp:
+        durations = Path(tmp) / "durations.json"
+        durations.write_text(git("cat-file", "blob", pin["durations_blob"]) + "\n")
+        common = ("--durations", str(durations), "--start", pin["start"])
+        a = _replan(tree, Path(tmp) / "a.json", "--roster-ref", ref,
+                    "--roster-path", pin["roster_path"], *common)
+        # B is named as the round's roster is: roster_lib.roster_round reads
+        # the round off the basename (design verdict, item dr2-b).
+        floor = Path(tmp) / "floor" / Path(pin["roster_path"]).name
+        floor.parent.mkdir()
+        floor.write_text(json.dumps(reduced_roster(roster, kept_in_floor(block, a["groups"])),
+                                    indent=1))
+        b = _replan(tree, Path(tmp) / "b.json", "--roster-file", str(floor), *common)
+        return a, b
+
+
+def production_groups(ref: str, block: dict, roster: dict) -> set[str]:
+    """The plan's groups whose roster files touch a product path, by
+    `machinery_ratchet.is_product` at the plan SHA (0018: a production merge)."""
+    import importlib.util
+    with tempfile.TemporaryDirectory(prefix="plan-ratchet-") as tmp:
+        path = Path(tmp) / "machinery_ratchet.py"
+        path.write_text(_show(ref, "tools/audit/machinery_ratchet.py"))
+        spec = importlib.util.spec_from_file_location("plan_audit_ratchet", path)
+        mod = importlib.util.module_from_spec(spec)
+        spec.loader.exec_module(mod)
+    files = {g.get("group"): g.get("files") or [] for g in roster.get("groups") or []}
+    return {g for g in block.get("groups") or {} if any(mod.is_product(f) for f in files.get(g, []))}
+
+
+def objective_check(ref: str, plan_path: str, register_path: str, previous: str | None,
+                    write: bool, main: str = "origin/main") -> int:
+    plan = _json_at(ref, plan_path)
+    block = plan.get("objective")
+    bad = check_block(plan, [], {}, [], None, {}, {}) if not isinstance(block, dict) else []
+    pin = (block or {}).get("pin") or {}
+    if not bad and set(pin) != OBJECTIVE_KEYS["pin"]:
+        bad = [f"PIN incomplete: {sorted(OBJECTIVE_KEYS['pin'] - set(pin))}; nothing projects "
+               f"without it"]
+    if bad:
+        for line in bad:
+            print(f"  FAIL {line}")
+        print("OBJECTIVE FAIL")
+        return 1
+    register = _json_at(ref, register_path)
+    register = register.get("verdicts", []) if isinstance(register, dict) else register
+    rnd = plan.get("round") or 0
+    path = BASELINE.format(rnd - 1)
+    blobs = {"plan": _blob(ref, path),
+             "main": _blob(git("merge-base", ref, main), path)}
+    if (block.get("baseline") or {}).get("tree"):
+        blobs["tree"] = _blob(block["baseline"]["tree"], path)
+    baseline = _json_at(ref, path) if blobs["plan"] else {}
+    terms = _json_at(ref, str(OBJECTIVE_CONFIG))["terms"]
+    ledger = (((baseline.get("terms") or {}).get("escapes") or {}).get("by_hand") or {}).get("ledger")
+    roster = _json_at(ref, pin["roster_path"])
+    tree = _worktree(ref)
+    try:
+        known = {"classes": {k for k in _json_at(ref, str(BUGCLASSES)) if not k.startswith("_")},
+                 "escapes": escape_rows(_show(ref, ledger)) if ledger else set(),
+                 "cards": open_cards(tree, ref, rnd)}
+        a, b = run_projections(tree, ref, block, roster)
+    finally:
+        _drop_worktree(tree)
+    prev = json.loads(Path(previous).read_text()) if previous else None
+    bad = (baseline_refusals(plan, baseline, blobs)
+           + check_block(plan, register, baseline, terms, prev, a["groups"], known)
+           + projection_refusals(block, a, b))
+    record = projection_record(block, a, b, production_groups(ref, block, roster))
+    out = str(Path(plan_path).parent / "PROJECTION.json")
+    if write:
+        Path(out).parent.mkdir(parents=True, exist_ok=True)
+        Path(out).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
+        print(f"projection record -> {out}")
+    else:
+        try:
+            committed = _show(ref, out)
+        except subprocess.CalledProcessError:
+            committed = None
+        bad += projection_differs(committed, record)
+    print(f"projection A: critical path {record['a']['critical_path_hours']} h, wall "
+          f"{record['a']['wall_hours']} h, closure {record['a']['closure']}, lead time p50/p90 "
+          f"{record['a']['lead_time_p50_hours']}/{record['a']['lead_time_p90_hours']} h")
+    print(f"floor cost (A less B): critical path {record['floor_cost']['critical_path_hours']} h, "
+          f"wall {record['floor_cost']['wall_hours']} h, dropped {len(record['b']['dropped'])}")
+    for group, hours in record["floor_cost"]["delay_hours"].items():
+        print(f"  rank-1 {group} finishes {hours} h later than on the floor")
+    for line in bad:
+        print(f"  FAIL {line}")
+    print("OBJECTIVE " + ("FAIL" if bad else "PASS"))
+    return 1 if bad else 0
+
+
+def objective_settle(plan_path: str, record_path: str, bodies: str | None, out: str | None) -> int:
+    plan = json.loads(Path(plan_path).read_text())
+    baseline = json.loads((ROOT / BASELINE.format((plan.get("round") or 0) - 1)).read_text())
+    record = json.loads(Path(record_path).read_text())
+    projection = json.loads((Path(plan_path).parent / "PROJECTION.json").read_text())
+    thresholds = json.loads((ROOT / OBJECTIVE_CONFIG).read_text())["thresholds"]
+    merged = set(read_bodies(Path(bodies)).keys()) if bodies else set()
+    lines = settle(plan, baseline, record, merged, thresholds, set(projection.get("production") or []))
+    for ln in lines:
+        print(f"  {ln['status']:<11} {ln['key']}: {ln['detail']}")
+    if out:
+        Path(out).write_text(json.dumps(lines, indent=1, sort_keys=True) + "\n")
+    print(f"settlement: {len(lines)} line(s), HELD "
+          f"{sum(ln['status'] == 'HELD' for ln in lines)}, MISSED "
+          f"{sum(ln['status'] == 'MISSED' for ln in lines)}")
+    return 0
+
+
 # ------------------------------------------------------------------- self-test
 
 def self_test() -> int:
@@ -604,6 +1184,358 @@ def self_test() -> int:
           renamed["merges"] == 3 and renamed["cochange_per_100"] == round(100 / 3, 4),
           repr(renamed))
 
+    # ---- the objective block (R11-ARCH-OBJECTIVE): each planted plan beside
+    # its passing twin, the null control, on in-memory dicts (no replan.py run).
+    terms = json.loads((ROOT / OBJECTIVE_CONFIG).read_text())["terms"]
+    t("BETTER names exactly objective.json's terms (a new term refuses until 0018 gives it "
+      "a direction)", sorted(BETTER) == sorted(terms), repr(sorted(set(BETTER) ^ set(terms))))
+    register = [{"id": "D1-01", "verdict": "verified", "stop_rule_class": "bug"},
+                {"id": "D1-02", "verdict": "weakened", "stop_rule_class": "bug"},
+                {"id": "D7-01", "verdict": "verified", "stop_rule_class": "hygiene"}]
+    baseline = {"round": 10, "terms": {term: {"no_read": "x", "builder": "B"} for term in terms}}
+    baseline["terms"]["first_pass"] = {"value": 0.5, "counts": "first-pass 50/100"}
+    when = lambda h: f"2026-11-17T{h:02d}:00:00Z"  # noqa: E731
+    proj_a = {"G1": {"after": ["G2"], "done": False, "finish": when(9)},
+              "G2": {"after": [], "done": False, "finish": when(4)},
+              "G3": {"after": [], "done": False, "start": when(3), "finish": when(6)},
+              "OLD": {"after": [], "done": True, "finish": None}}
+
+    def objective_plan() -> dict:
+        return {"round": 11, "triage": [{"id": "D1-01", "verdict": "keep"},
+                                        {"id": "D1-02", "verdict": "defer", "card": "E11-1"}],
+                "groups": [{"group": g} for g in ("G1", "G2", "G3")],
+                "moves": [{"group": "G1", "adr": "ADR-1"}, {"group": "G2"}, {"group": "G3"}],
+                "objective": {
+                    "baseline": {"record": "dev/audit/yardstick/round10/OBJECTIVE.json", "tree": "c0"},
+                    "pin": {"roster_path": "r/wave-r11-groups.json", "roster_blob": "b0",
+                            "start": when(0), "durations_blob": "d0"},
+                    "terms": {**{term: {"direction": "undecided", "builder": "B"} for term in terms},
+                              "first_pass": {"direction": "up", "basis": "review clause"}},
+                    "groups": {"G1": {"rank": 1, "removes": ["D1-01"]},
+                               "G2": {"rank": 2, "removes": ["D7-01"], "examined_by": "D7 pass"},
+                               "G3": {"rank": 2, "examined_by": "D3 pass"}},
+                    "edges": [{"from": "G1", "to": "G2", "adr": "ADR-1"}]}}
+
+    known = {"classes": {"P1"}, "cards": {"E11-1"}, "escapes": {"G-ESC"}}
+
+    def refused(plan: dict, previous=None, projected=None) -> list[str]:
+        return check_block(plan, register, baseline, terms, previous,
+                           proj_a if projected is None else projected, known)
+
+    good_plan = objective_plan()
+    block_of = lambda plan: json.loads(json.dumps(plan["objective"]))  # noqa: E731
+    t("a plan with a sound objective block passes the P3 check (every arm's twin)",
+      refused(good_plan) == [], repr(refused(good_plan)))
+    t("a plan with no objective block is refused",
+      refused({k: v for k, v in good_plan.items() if k != "objective"})[0].startswith("NO objective"))
+
+    def planted(edit) -> list[str]:
+        plan = json.loads(json.dumps(good_plan))
+        edit(plan)
+        return refused(plan)
+
+    def has(lines: list[str], head: str) -> bool:
+        return any(line.startswith(head) for line in lines)
+
+    def defer_bug(p):
+        p["triage"][1].pop("card")
+    t("a verified bug deferred with no card is refused (lead_time bought)",
+      has(planted(defer_bug), "DEFERRED bug D1-02"))
+    t("the null control: deferring a hygiene finding needs no card",
+      not has(planted(lambda p: p["triage"].append({"id": "D7-01", "verdict": "defer"})), "DEFERRED"))
+    t("a group claiming an unregistered finding is refused (unexamined dressed as a fix)",
+      has(planted(lambda p: p["objective"]["groups"]["G2"]["removes"].append("D9-99")),
+          "UNKNOWN finding G2 D9-99"))
+    t("a hold predicted on a term NO-READ in the baseline is refused (free credit)",
+      has(planted(lambda p: p["objective"]["terms"].__setitem__(
+          "escapes", {"direction": "hold", "basis": "x"})), "NO-READ escapes"))
+    t("and undecided with no builder is refused, while undecided with one passes (above)",
+      has(planted(lambda p: p["objective"]["terms"].__setitem__(
+          "escapes", {"direction": "undecided"})), "NO-READ escapes undecided"))
+    t("a read term predicted with no basis is refused",
+      has(planted(lambda p: p["objective"]["terms"]["first_pass"].pop("basis")),
+          "TERM first_pass: a predicted"))
+    t("a term objective.json does not name is refused, and a missing one too",
+      has(planted(lambda p: p["objective"]["terms"].__setitem__(
+          "speed", {"direction": "up", "basis": "x"})), "TERM speed")
+      and has(planted(lambda p: p["objective"]["terms"].pop("regret")), "TERM regret"))
+    t("one finding closed by two groups is refused (lead_time and tokens counted twice)",
+      has(planted(lambda p: p["objective"]["groups"]["G3"].__setitem__("removes", ["D7-01"])),
+          "DOUBLE closure D7-01"))
+    t("a rank-1 group after a rank-2 group with no ADR edge is refused (dS first)",
+      has(planted(lambda p: p["objective"].__setitem__("edges", [])), "RANK edge G1 after G2"))
+    t("and an edge whose ADR no move carries is refused alike",
+      has(planted(lambda p: p["objective"]["edges"][0].__setitem__("adr", "ADR-9")), "RANK edge"))
+    t("a rank-2 group with no examining pass is refused (dS at unexamined's cost)",
+      has(planted(lambda p: p["objective"]["groups"]["G3"].pop("examined_by")), "UNEXAMINED move G3"))
+    t("a rank the keys contradict is refused both ways",
+      has(planted(lambda p: p["objective"]["groups"]["G3"].__setitem__("rank", 1)), "RANK G3 declares 1")
+      and has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("rank", 2)), "RANK G1 declares 2"))
+    t("an unknown class id is refused; a known one makes the group rank 1",
+      has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("classes", ["P9"])),
+          "UNKNOWN class G1 P9")
+      and not planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("classes", ["P1"])))
+    t("an hours key authored in the block is refused (cost hidden)",
+      has(planted(lambda p: p["objective"].__setitem__("critical_path_hours", 40)), "AUTHORED time")
+      and has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("finish", when(3))),
+              "AUTHORED time groups.G1.finish")
+      and has(planted(lambda p: p["objective"]["pin"].__setitem__("wall_hours", 9)), "AUTHORED time"))
+    t("and any other key outside the grammar is refused by name",
+      has(planted(lambda p: p["objective"]["groups"]["G1"].__setitem__("weight", 3)),
+          "UNKNOWN key groups.G1.weight"))
+    t("a planned group with no objective entry is refused, and an entry for no group",
+      has(planted(lambda p: p["groups"].append({"group": "G4"})), "RANK G4: a planned")
+      and has(planted(lambda p: p["objective"]["groups"].__setitem__(
+          "G5", {"rank": 2, "examined_by": "x"})), "RANK G5: an objective entry"))
+    t("an open group projection A schedules and the plan never ranks is refused (dr2-g)",
+      has(refused(good_plan, projected={**proj_a, "G6": {"after": [], "done": False}}),
+          "UNRANKED open group G6"))
+    t("the null control: a done group needs no rank",
+      refused(good_plan, projected={**proj_a, "G6": {"after": [], "done": True}}) == [])
+    missed = [{"key": "G1:removes:D1-01", "status": "MISSED"}, {"key": "G2:x", "status": "HELD"}]
+    t("plan N+1 silent on a MISSED line of plan N is refused",
+      refused(good_plan, previous=missed) == ["UNDISPOSED G1:removes:D1-01: the previous plan "
+                                             "MISSED it; name a group or a card"])
+    t("and passes once it disposes the line; a first plan has no previous settlement",
+      refused({**good_plan, "objective": {**good_plan["objective"],
+                                          "dispositions": {"G1:removes:D1-01": "card E12-1"}}},
+              previous=missed) == []
+      and refused(good_plan, previous=None) == [])
+
+    # The projections: B is A less the rank-2 groups no rank-1 group reaches.
+    block = good_plan["objective"]
+    t("the floor keeps a reached rank-2 group and drops an unreached one",
+      kept_in_floor(block, proj_a) == {"G1", "G2", "OLD"}, repr(kept_in_floor(block, proj_a)))
+    roster = {"cutover": 1, "groups": [{"group": g} for g in ("G1", "G2", "G3", "OLD")]}
+    t("the reduced roster filters entries by name and keeps the rest of the file",
+      [g["group"] for g in reduced_roster(roster, {"G1", "OLD"})["groups"]] == ["G1", "OLD"]
+      and reduced_roster(roster, set())["cutover"] == 1)
+
+    def plan_of(groups: dict, cp: float, wall: float, blob: str = "b0", version: str = "1.0.0") -> dict:
+        return {"generated": {"roster_blob": blob, "start": when(0), "version": version,
+                              "caps": {"slots": 20}},
+                "binding": {"critical_path_hours": cp},
+                "summary": {"wall_hours": wall, "closure": when(10), "closure_stamp": f"v{version}"},
+                "groups": groups}
+    a = plan_of(proj_a, 9.0, 10.0)
+    b = plan_of({k: {**v, "finish": when(7) if k == "G1" else v["finish"]}
+                 for k, v in proj_a.items() if k != "G3"}, 7.0, 8.0)
+    t("projections at the pin, B the exact reduction, pass",
+      projection_refusals(block, a, b) == [], repr(projection_refusals(block, a, b)))
+    t("projection A of another roster blob is refused (a stale pin)",
+      has(projection_refusals(block, plan_of(proj_a, 9.0, 10.0, blob="b1"), b), "STALE pin"))
+    t("a B that keeps an unreached rank-2 group is refused (the floor cost shrunk)",
+      has(projection_refusals(block, a, plan_of(proj_a, 9.0, 10.0)), "REDUCED roster keeps G3"))
+    record = projection_record(block, a, b, {"G1", "G3"})
+    t("lead time reads production groups only",
+      projection_record(block, a, b, {"G1"})["a"]["lead_time_p50_hours"] == 9.0)
+    t("the record holds the floor cost: A less B, and each rank-1 group's delay",
+      record["floor_cost"] == {"critical_path_hours": 2.0, "wall_hours": 2.0,
+                               "delay_hours": {"G1": 2.0}}
+      and record["b"]["dropped"] == ["G3"], repr(record["floor_cost"]))
+    t("lead time runs from the plan's start, the clock 0018 starts at the roster entry (dr2-a)",
+      record["a"]["lead_time_p50_hours"] == 6.0 and record["a"]["lead_time_p90_hours"] == 9.0,
+      repr(record["a"]))
+    t("the same inputs under another VERSION give the same record (dr2-c)",
+      projection_record(block, plan_of(proj_a, 9.0, 10.0, version="9.9.9"), b, {"G1", "G3"}) == record)
+    t("a committed record equal to the re-run's bytes passes; one edited is refused",
+      projection_differs(json.dumps(record, indent=1, sort_keys=True) + "\n", record) == []
+      and has(projection_differs(json.dumps({**record, "floor_cost": {}}, indent=1, sort_keys=True)
+                                 + "\n", record), "PROJECTION differs")
+      and has(projection_differs(None, record), "PROJECTION missing"))
+
+    # Arms the diff's mutants named (prepr step 6d): each pins one line by value.
+    shape = planted(lambda p: p["objective"]["terms"].__setitem__("escapes", "down"))
+    t("a term entry that is not an object is refused by shape, once, not read key by key",
+      has(shape, "SHAPE terms.escapes") and not has(shape, "UNKNOWN key terms.escapes."), repr(shape))
+    t("the grammar reaches a term's and an edge's keys",
+      has(planted(lambda p: p["objective"]["terms"]["first_pass"].__setitem__("weight", 2)),
+          "UNKNOWN key terms.first_pass.weight")
+      and has(planted(lambda p: p["objective"]["edges"][0].__setitem__("why", "x")),
+              "UNKNOWN key edges[0].why"))
+    t("a card alone makes a group rank 1 (no examining pass owed)",
+      planted(lambda p: p["objective"]["groups"].__setitem__("G3", {"rank": 1, "cards": ["E11-1"]})) == [])
+    # #3703 review item 1: every rank-1 key names a registered id, or a string ranks a group 1.
+    for kind, item in (("cards", "NO-SUCH-CARD"), ("escapes", "NO-SUCH-ROW"), ("classes", "P9")):
+        lines = planted(lambda p, k=kind, i=item: p["objective"]["groups"].__setitem__(
+            "G3", {"rank": 1, k: [i]}))
+        t(f"a rank-1 `{kind}` id no register holds is refused by name",
+          lines == [f"UNKNOWN {REGISTERED[kind][0]} G3 {item}: not in {REGISTERED[kind][1]}"], repr(lines))
+    t("an escape row ruled `in` makes a group rank 1",
+      planted(lambda p: p["objective"]["groups"].__setitem__("G3", {"rank": 1, "escapes": ["G-ESC"]})) == [])
+    t("every rank-1 key derived_rank reads is a REGISTERED key, checked against its register",
+      all(derived_rank({kind: ["x"]}, set()) == 1 for kind in REGISTERED)
+      and derived_rank({"removes": ["D7-01"], "examined_by": "x"}, set()) == 2)
+    ledger = ("# header\ngroup\tpr\truling\nG-ESC\t1\tin\nG-OUT\t-\tout\nshort\n")
+    t("the escapes ledger yields its `in` rows' groups; a ledger with no header yields none",
+      escape_rows(ledger) == {"G-ESC"} and escape_rows("G-ESC\t1\tin\n") == set())
+    b10 = {"round": 10}
+    same = {"plan": "x1", "tree": "x1", "main": "x1"}
+    t("the baseline is the previous round's record, one blob everywhere: passes",
+      baseline_refusals(good_plan, b10, same) == [])
+    t("a baseline path the plan chose is refused (#3703 review item 2)",
+      has(baseline_refusals({**good_plan, "objective": {**good_plan["objective"], "baseline": {
+          "record": "dev/audit/rounds/round11/PLAN/doctored.json"}}}, b10, same), "BASELINE 'dev/audit/rounds"))
+    t("a record of another round is refused",
+      baseline_refusals(good_plan, {"round": 9}, same)
+      == ["BASELINE round 9: dev/audit/yardstick/round10/OBJECTIVE.json must record round 10"])
+    t("a record edited on the plan's branch, or at its tree, is refused; an absent one too",
+      has(baseline_refusals(good_plan, b10, {**same, "plan": "x2"}), "BASELINE edited")
+      and has(baseline_refusals(good_plan, b10, {**same, "tree": "x2"}), "BASELINE edited")
+      and has(baseline_refusals(good_plan, b10, {"plan": None, "main": None}), "BASELINE edited"))
+    t("a ranked done group is refused by name (#3703 review item 4)",
+      refused({**good_plan, "groups": good_plan["groups"] + [{"group": "OLD"}],
+               "objective": {**block_of(good_plan), "groups": {**block_of(good_plan)["groups"],
+                                                               "OLD": {"rank": 2, "examined_by": "x"}}}})
+      == ["RANKED done group OLD: a done group is kept unranked, and B keeps it"])
+    t("and the floor keeps a done group whatever its rank",
+      "OLD" in kept_in_floor({"groups": {"OLD": {"rank": 2}}}, proj_a))
+    t("an objective entry that is not an object is refused by shape and read no further",
+      has(planted(lambda p: p["objective"]["groups"].__setitem__("G3", "x")), "SHAPE groups.G3"))
+    t("a rank-2 group waiting on a rank-2 group owes no edge",
+      refused(good_plan, projected={**proj_a, "G3": {**proj_a["G3"], "after": ["G2"]}}) == [])
+    t("a rank-1 group waiting on a rank-1 group owes no edge",
+      refused({**good_plan, "objective": {**block_of(good_plan), "groups": {
+          **block_of(good_plan)["groups"], "G3": {"rank": 1, "cards": ["E11-1"]}}}},
+              projected={**proj_a, "G1": {**proj_a["G1"], "after": ["G2", "G3"]}}) == [])
+    two = {"groups": {"G1": {"rank": 1}, "G3": {"rank": 2}, "G4": {"rank": 2}}}
+    t("the floor drops a rank-2 group only another rank-2 group reaches",
+      kept_in_floor(two, {**proj_a, "G3": {"after": ["G4"]}, "G4": {"after": []}})
+      == {"G1", "G2", "OLD"})
+    t("the rank edge reads the whole `after` closure, not the first hop",
+      has(refused(good_plan, projected={**proj_a, "G2": {**proj_a["G2"], "after": ["G3"]}}),
+          "RANK edge G1 after G3"))
+    t("hours are seconds over 3600, to the hundredth",
+      _hours("2026-11-21T04:00:00Z", when(0)) == 100.0
+      and _hours(when(1), "2026-11-17T00:00:20Z") == round(3580 / 3600, 2))
+    t("a percentile over no value is None, not an index error", _rank_pct([], 50) is None)
+    fine = projection_record(block, plan_of(proj_a, 9.125, 10.0), plan_of(proj_a, 7.0, 8.004), set())
+    t("the floor cost is rounded to the hundredth",
+      fine["floor_cost"]["critical_path_hours"] == 2.12 and fine["floor_cost"]["wall_hours"] == 2.0,
+      repr(fine["floor_cost"]))
+    late = plan_of({k: v for k, v in proj_a.items() if k != "G3"}, 7.0, 8.0)
+    late["generated"]["start"] = when(1)
+    t("a projection started at another instant than the pin is refused",
+      has(projection_refusals(block, a, late), "STALE pin: the projections start"))
+    t("a B missing a group the floor keeps is refused",
+      has(projection_refusals(block, a, plan_of({k: v for k, v in proj_a.items() if k not in ("G3", "G2")},
+                                                7.0, 8.0)), "REDUCED roster drops G2"))
+
+    # The settlement: only a HELD keyed effect is credit.
+    thresholds = {"band_lead_time": {"value": None}}
+    base10 = {"round": 10, "terms": {**baseline["terms"], "escapes": {"value": 20}}}
+    rec11 = {"round": 11, "terms": {**baseline["terms"], "escapes": {"value": 2}}}
+    sp = json.loads(json.dumps(good_plan))
+    sp["objective"]["terms"]["escapes"] = {"direction": "down", "basis": "G1 removes D1-01"}
+    status = lambda lines, key: next((ln["status"] for ln in lines if ln["key"] == key), None)  # noqa: E731
+    held = settle(sp, base10, rec11, {"G1", "G2", "G3"}, thresholds, {"G1"})
+    t("a term read on both sides, moved as predicted, with its keyed effect HELD: HELD",
+      status(held, "term:escapes") == "HELD" and status(held, "G1:removes:D1-01") == "HELD",
+      repr(held))
+    t("a term NO-READ on one side settles UNDECIDED, never HELD",
+      status(settle(sp, baseline, rec11, {"G1"}, thresholds, set()), "term:escapes") == "UNDECIDED")
+    unpredicted = settle(sp, base10, rec11, set(), thresholds, set())
+    t("a term that improved with no HELD keyed effect is UNPREDICTED, not banked",
+      status(unpredicted, "term:escapes") == "UNPREDICTED"
+      and status(unpredicted, "G1:removes:D1-01") == "MISSED", repr(unpredicted))
+    flipped = {**rec11, "terms": {**rec11["terms"], "escapes": {"value": 40}}}
+    diff = [x for x, y in zip(held, settle(sp, base10, flipped, {"G1", "G2", "G3"}, thresholds, {"G1"}))
+            if x != y]
+    t("perturbation: one record value flipped flips exactly one settlement line",
+      len(diff) == 1 and diff[0]["key"] == "term:escapes", repr(diff))
+    t("a share settles on its counts' band; a tie inside it is no move",
+      status(settle(good_plan, baseline, {**rec11, "terms": {**rec11["terms"], "first_pass": {
+          "value": 0.9, "counts": "first-pass 90/100"}}}, set(), thresholds, set()),
+          "term:first_pass") == "UNPREDICTED"
+      and moved("first_pass", (50, 100), (55, 100), thresholds) == "tie")
+    t("a relative band left unset by the owner is UNDECIDED",
+      moved("lead_time", 10.0, 2.0, thresholds) is None
+      and moved("lead_time", 10.0, 2.0, {"band_lead_time": {"value": 0.2}}) == "down")
+    t("cause, re-report and escape keys are NOT-DUE at the plan's own close",
+      status(held, "G1:injected") == "NOT-DUE" and status(held, "G1:rereport:D1-01") == "NOT-DUE")
+    nxt = {"round": 12, "terms": {}}
+    t("at the next close they settle on keyed rows, and with none they are UNDECIDED",
+      status(settle(good_plan, baseline, nxt, set(), thresholds, {"G1"}), "G1:injected") == "UNDECIDED"
+      and status(settle(good_plan, baseline, {**nxt, "keyed": {"injected": [{"group": "G1"}]}},
+                        set(), thresholds, {"G1"}), "G1:injected") == "MISSED"
+      and status(settle(good_plan, baseline, {**nxt, "keyed": {"injected": [{"group": "G9"}]}},
+                        set(), thresholds, {"G1"}), "G1:injected") == "HELD")
+
+    # #3703 review item 3: each settlement status choice, pinned by value.
+    t("perturbation: the flipped line's status flips, HELD to MISSED (a move against `down`)",
+      [d["status"] for d in diff] == ["HELD"]
+      and status(settle(sp, base10, flipped, {"G1", "G2", "G3"}, thresholds, {"G1"}),
+                 "term:escapes") == "MISSED")
+    up = json.loads(json.dumps(sp))
+    up["objective"]["terms"]["escapes"]["direction"] = "up"
+    t("a move the other way than an `up` prediction is MISSED",
+      status(settle(up, base10, rec11, {"G1"}, thresholds, {"G1"}), "term:escapes") == "MISSED")
+    hold = json.loads(json.dumps(sp))
+    hold["objective"]["terms"]["escapes"]["direction"] = "hold"
+    tie = {**rec11, "terms": {**rec11["terms"], "escapes": {"value": 22}}}
+    t("`hold` settles MISSED on a worse move, HELD on a tie and on a credited better move",
+      status(settle(hold, base10, flipped, set(), thresholds, set()), "term:escapes") == "MISSED"
+      and status(settle(hold, base10, tie, set(), thresholds, set()), "term:escapes") == "HELD"
+      and status(settle(hold, base10, rec11, {"G1"}, thresholds, set()), "term:escapes") == "HELD")
+    und = json.loads(json.dumps(sp))
+    und["objective"]["terms"]["escapes"] = {"direction": "undecided", "builder": "B"}
+    t("`undecided` on a read term settles UNDECIDED, whichever way it moved",
+      status(settle(und, base10, flipped, set(), thresholds, set()), "term:escapes") == "UNDECIDED")
+    lt = json.loads(json.dumps(sp))
+    lt["objective"]["terms"]["lead_time"] = {"direction": "down", "basis": "x"}
+    lead = {"lead_time": {"value": 10.0}}
+    t("a term no band reads settles UNDECIDED, named so",
+      [ln["detail"] for ln in settle(lt, {**base10, "terms": lead},
+                                     {**rec11, "terms": {"lead_time": {"value": 2.0}}}, set(),
+                                     thresholds, set()) if ln["key"] == "term:lead_time"]
+      == ["no band reads this term (unset, or no denominator)"])
+    t("only a rank-2 group owes an examining pass: UNDECIDED with no rows",
+      status(held, "G2:examined_by") == "UNDECIDED" and status(held, "G1:examined_by") is None)
+    seen = settle(sp, base10, {**rec11, "keyed": {"examined_by": [{"group": "G2"}]}}, set(),
+                  thresholds, set())
+    t("and with rows, HELD where a row names the group, MISSED where none does",
+      status(seen, "G2:examined_by") == "HELD" and status(seen, "G3:examined_by") == "MISSED")
+    ek = json.loads(json.dumps(good_plan))
+    ek["objective"]["groups"]["G1"].update({"escapes": ["G-ESC"], "classes": ["P1"]})
+    at12 = lambda keyed: settle(ek, baseline, {**nxt, "keyed": keyed}, set(), thresholds, set())  # noqa: E731
+    t("escape and class keys settle at the next close on their own rows",
+      status(at12({"escapes": [{"key": "G-ESC"}], "classes": [{"class": "P9"}]}), "G1:escapes:G-ESC")
+      == "MISSED"
+      and status(at12({"escapes": [], "classes": [{"class": "P1"}]}), "G1:classes:P1") == "MISSED"
+      and status(at12({"escapes": [], "classes": []}), "G1:classes:P1") == "HELD"
+      and status(at12({}), "G1:escapes:G-ESC") == "UNDECIDED")
+    t("the next close settles no term and no own-close effect",
+      not [ln for ln in at12({}) if ln["key"].startswith("term:") or ":examined_by" in ln["key"]])
+    t("only a production group owes an `injected` line",
+      status(held, "G2:injected") is None)
+    t("a plan with no round is round 0, so a round-1 record is its next close",
+      status(settle({k: v for k, v in good_plan.items() if k != "round"}, baseline, {"round": 1},
+                    set(), thresholds, {"G1"}), "G1:injected") == "UNDECIDED")
+    t("a share reads off its counts to four places; a zero denominator is no share",
+      term_reading({"value": 0.3333, "counts": "1/3"}) == {"": (1, 3)}
+      and term_reading({"value": 0.2, "counts": "1/3 then 1/5"}) == {"": (1, 5)}
+      and term_reading({"value": 0.5, "counts": "0/0"}) == {"": 0.5}
+      and term_reading({"value": None}) is None)
+    t("a count's band is twice the root of the two counts",
+      moved("escapes", 20, 32, thresholds) == "tie" and moved("escapes", 20, 36, thresholds) == "up"
+      and moved("escapes", 40, 20, thresholds) == "down")
+    t("a share's band is twice the pooled standard error",
+      moved("first_pass", (50, 100), (65, 100), thresholds) == "up"
+      and moved("first_pass", (50, 100), (63, 100), thresholds) == "tie")
+    t("a value that is neither a count nor a share has no band",
+      moved("escapes", 2.5, 9.0, thresholds) is None and moved("escapes", True, 9, thresholds) is None)
+
+    t("a ledger row too short to hold its ruling is skipped, not an index error",
+      escape_rows("group\tpr\truling\nG-X\t1\n") == set())
+    t("a plan with no round is round 0: its baseline is round -1's record",
+      has(baseline_refusals({"objective": {"baseline": {"record": BASELINE.format(10)}}}, {"round": -1},
+                            same), "BASELINE 'dev/audit/yardstick/round10/OBJECTIVE.json': the "
+                                   "baseline is the previous round's record, dev/audit/yardstick/round-1"))
+    t("a count move equal to its band is a tie",
+      moved("escapes", 4, 12, thresholds) == "tie" and moved("escapes", 4, 13, thresholds) == "up")
+    t("a blob reads off the checkout, and an absent path reads None",
+      bool(_blob("HEAD", "tools/audit/seat/plan_audit.py")) and _blob("HEAD", "no/such/path") is None)
+
     print(f"plan_audit self-test: {checks} checks, {failures} failed")
     return 1 if failures else 0
 
@@ -632,6 +1564,19 @@ def main(argv: list[str]) -> int:
     cmp_.add_argument("--fork", required=True)
     cmp_.add_argument("--stamp", required=True)
     cmp_.add_argument("--allow", action="append", default=[])
+    obj = sub.add_parser("objective-check")
+    obj.add_argument("--ref", required=True, help="the plan commit; every input is read at it")
+    obj.add_argument("--plan", required=True)
+    obj.add_argument("--register", required=True)
+    obj.add_argument("--previous", help="the previous plan's `settle --json` lines")
+    obj.add_argument("--write", action="store_true", help="write PROJECTION.json beside --plan")
+    obj.add_argument("--main", default="origin/main",
+                     help="main's ref; the baseline must be the blob the plan's branch left it at")
+    stl = sub.add_parser("settle")
+    stl.add_argument("--plan", required=True)
+    stl.add_argument("--record", required=True)
+    stl.add_argument("--bodies")
+    stl.add_argument("--json")
     args = ap.parse_args(argv)
 
     if args.self_test:
@@ -667,6 +1612,11 @@ def main(argv: list[str]) -> int:
         print(f"  behaviour { {k: len(v) for k, v in data['behaviour'].items()} }, "
               f"mutation {data['mutation']}, coupling {data['coupling']}")
         return 0
+    if args.cmd == "objective-check":
+        return objective_check(args.ref, args.plan, args.register, args.previous, args.write,
+                               args.main)
+    if args.cmd == "settle":
+        return objective_settle(args.plan, args.record, args.bodies, args.json)
     if args.cmd == "compare":
         fork = json.loads(Path(args.fork).read_text())
         stamp = json.loads(Path(args.stamp).read_text())
diff --git a/tools/audit/seat/plan_page.py b/tools/audit/seat/plan_page.py
index 7852a30610..5929f58ee5 100644
--- a/tools/audit/seat/plan_page.py
+++ b/tools/audit/seat/plan_page.py
@@ -250,7 +250,9 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
                if a in G and a not in discharged and roster_lib.gates(G[a])]
         if g in done:
             blk = []  # a merged group waits on nothing (the legend's not-yet-done rule)
-        part = sorted(delivered.get(g) or [])
+        # A closed group (absorbed) delivered no part of an open one: the label
+        # and the strip's count share this one predicate.
+        part = [] if g in done else sorted(delivered.get(g) or [])
         sfx = f", part merged #{', #'.join(map(str, part))}" if part else ""
         pr = ", ".join(f"#{n}" for n in open_pr.get(g, [])) or "—"
         if g in merged:
@@ -301,7 +303,7 @@ def build_rows(roster: dict, plan: dict, snap: dict) -> list:
             "blk": blk, "desc": roster_lib.one_line_brief(entry, 170),
             "crit": g in crit,
             "hot": g in gating_crit and g not in done and roster_lib.is_hotfix(entry),
-            "part": bool(part) and g not in done,
+            "part": bool(part),
             # An owner-stated price is the owner's word, not a measurement: the row says so.
             "owner_priced": bool(pg.get("owner_priced")),
             "wave": None if g in done else pg["wave"],
@@ -638,6 +640,93 @@ def flow_section(plan: dict, rows: list, flow: dict | None) -> str:
             + "</section>\n")
 
 
+def _chip(n, closer, is_open, title) -> str:
+    cls = "chip" + (" closer" if closer else "") + ("" if is_open else " closed")
+    return f'<span class="{cls}" title="{html.escape(title)}">#{n}</span>'
+
+
+def group_rows(rows: list) -> str:
+    """The Groups table's body: one row per group row, the page's one drawing of it."""
+    e, chip = html.escape, _chip
+    return "".join(
+        f'<tr class="{r["st"]}" data-st="{r["st"]}" data-part="{int(r["part"])}"><td class="g">'
+        + ('<span class="cp" title="critical path">◆</span>' if r["crit"] else "")
+        + ('<span class="cp hotcp" title="hotfix blocking a critical-path group">▲</span>'
+           if r["hot"] else "")
+        + f'{e(short(r["g"]))}<div class="lanec">{e(r["lane"])}</div></td>'
+        f'<td class="d">{e(r["desc"])}</td>'
+        f'<td class="st">{pill(r["st"], r["label"])}</td>'
+        f'<td class="tier">{r["tier"] if r["tier"] is not None else "—"}</td>'
+        f'<td class="mono">{e(r["pr"])}</td>'
+        f'<td>{"".join(chip(*i) for i in r["issues"]) or "—"}</td>'
+        f'<td class="blk">{e(", ".join(map(short, r["blk"]))) or "—"}</td>'
+        f'<td class="mono" title="{e(r["why"])}">{r["finish"] or "—"}'
+        f'{" <span class=owner-priced>owner-stated price, not measured</span>" if r["owner_priced"] else ""}</td>'
+        f'<td class="mono">{r["wave"] or "—"}</td></tr>' for r in rows)
+
+
+def next_round_pane(roster: dict, plan: dict, snap: dict) -> str:
+    """The second tab: the next round's groups on their own preliminary Gantt,
+    from the plan's `next_round` (replan.build_round_plan), which prices them on
+    the same duration model and caps, from this round's closure. Pure."""
+    e = html.escape
+    nr = plan["next_round"]
+    n, cur = nr["round"], plan["generated"]["round"]
+    head = (f'  <h2>Round {n} (preliminary)</h2>\n'
+            f'  <p class="note preliminary">Preliminary: round {n}\'s groups, priced on the same '
+            f'duration model and caps as round {cur}, starting at round {cur}\'s planned closure '
+            f'({e(_when(nr["starts_at"]))} UTC). It moves when that closure does and when the '
+            f'roster changes; round {cur}\'s tab, lanes and closure do not count these groups.'
+            + (f' {nr["beyond"]} more group(s) belong to rounds after {n} and are not scheduled.'
+               if nr.get("beyond") else "") + '</p>\n')
+    if "plan" not in nr:
+        return ('<section id="next-round">\n' + head
+                + f'  <p class="note flag">UNAVAILABLE: {e(nr.get("unavailable") or "no plan")}</p>\n'
+                '</section>\n')
+    sub = nr["plan"]
+    ids = set(sub["groups"])
+    nroster = {**roster, "groups": [g for g in roster.get("groups", []) if g["group"] in ids]}
+    rows = build_rows(nroster, sub, snap)
+    svg, _ = swimlanes(sub, rows)
+    svg = svg.replace('<g class="grp"', '<g class="grp" data-tab="next"')
+    stamps = "".join(
+        f'<tr><td class="mono">{e(x["version"])}</td><td class="mono">{_when(x["at"])}</td>'
+        f'<td>{e(", ".join(map(short, x["carries"])) or "—")}</td>'
+        f'<td class="mono">{e(x["kind"])}</td></tr>' for x in sub["stamps"])
+    return ('<section id="next-round">\n' + head
+            + f'  <p class="note">{len(rows)} groups; preliminary closure '
+              f'{e(_t(sub["summary"]["closure"]).strftime("%a %d %b %H:%M"))} UTC, stamp '
+              f'{e(sub["summary"]["closure_stamp"])}.</p>\n'
+            + f'  <h3>Swimlanes (preliminary)</h3>\n  <div class="scroll">{svg}</div>\n'
+            + '  <h3>Groups</h3>\n  <div class="scroll"><table>\n    <thead><tr><th>Group</th>'
+              '<th>Description</th><th>Status</th><th>Tier</th><th>PR</th><th>Issues</th>'
+              '<th>Blocked by</th><th>ETA (UTC)</th><th>Wave</th></tr></thead>\n'
+            + f'    <tbody id="rows-next">{group_rows(rows)}</tbody>\n  </table></div>\n'
+            + '  <h3>Planned stamps (preliminary)</h3>\n  <div class="scroll"><table>\n'
+              '    <thead><tr><th>Version</th><th>Projected (UTC)</th><th>Carries</th>'
+              f'<th>Kind</th></tr></thead>\n    <tbody>{stamps}</tbody>\n  </table></div>\n'
+            + '</section>\n')
+
+
+_TABS_NAV = (
+    '\n<nav class="tabs" role="tablist" aria-label="Round">'
+    '<button type="button" role="tab" data-tab="cur" aria-selected="true">Round {cur}</button>'
+    '<button type="button" role="tab" data-tab="next" aria-selected="false">'
+    'Round {nxt} (preliminary)</button></nav>')
+
+_TABS_JS = """<script>
+(function(){
+  var ts=document.querySelectorAll('.tabs button');
+  ts.forEach(function(t){t.addEventListener('click',function(){
+    ts.forEach(function(x){x.setAttribute('aria-selected',x===t?'true':'false')});
+    document.getElementById('tab-cur').hidden=t.getAttribute('data-tab')!=='cur';
+    document.getElementById('tab-next').hidden=t.getAttribute('data-tab')!=='next';
+  })});
+})();
+</script>
+"""
+
+
 def _when(s: str) -> str:
     return _t(s).strftime("%a %d %b %H:%M")
 
@@ -646,6 +735,17 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
            flow: dict | None = None, phases: tuple | None = None) -> str:
     """The page. Pure: every input is an argument. `phases` is the round's
     phases file as `(doc, violations, shown path)`, drawn above the lanes."""
+    # The page covers the plan's round only: a later round's groups are the
+    # second tab's (`next_round_pane`), and the issues only they carry are not
+    # this round's open issues.
+    whole, round_n = roster, plan["generated"].get("round")
+    later = (roster_lib.next_round_groups(roster, round_n) if isinstance(round_n, int) else {})
+    roster = roster_lib.round_roster(roster, round_n) if later else roster
+    theirs = {i for g in later.values() for i in (*(g.get("issues") or []), *(g.get("fixes") or []))}
+    mine = {i for g in roster.get("groups", []) for i in (*(g.get("issues") or []), *(g.get("fixes") or []))}
+    full_snap = snap
+    if theirs - mine:
+        snap = {**snap, "issues": [i for i in snap["issues"] if i["number"] not in theirs - mine]}
     rows = build_rows(roster, plan, snap)
     svg, drawn = swimlanes(plan, rows)
     gen, summ = plan["generated"], plan["summary"]
@@ -666,26 +766,9 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
     sizes = ", ".join(f"{k} {v:g} h" for k, v in sorted(
         model["sizes_hours"].items(), key=lambda kv: (order.get(kv[0], 99), kv[0])))
     e = html.escape
+    tabbed = bool(later and plan.get("next_round"))
 
-    def chip(n, closer, is_open, title):
-        cls = "chip" + (" closer" if closer else "") + ("" if is_open else " closed")
-        return f'<span class="{cls}" title="{e(title)}">#{n}</span>'
-
-    trs = "".join(
-        f'<tr class="{r["st"]}" data-st="{r["st"]}" data-part="{int(r["part"])}"><td class="g">'
-        + ('<span class="cp" title="critical path">◆</span>' if r["crit"] else "")
-        + ('<span class="cp hotcp" title="hotfix blocking a critical-path group">▲</span>'
-           if r["hot"] else "")
-        + f'{e(short(r["g"]))}<div class="lanec">{e(r["lane"])}</div></td>'
-        f'<td class="d">{e(r["desc"])}</td>'
-        f'<td class="st">{pill(r["st"], r["label"])}</td>'
-        f'<td class="tier">{r["tier"] if r["tier"] is not None else "—"}</td>'
-        f'<td class="mono">{e(r["pr"])}</td>'
-        f'<td>{"".join(chip(*i) for i in r["issues"]) or "—"}</td>'
-        f'<td class="blk">{e(", ".join(map(short, r["blk"]))) or "—"}</td>'
-        f'<td class="mono" title="{e(r["why"])}">{r["finish"] or "—"}'
-        f'{" <span class=owner-priced>owner-stated price, not measured</span>" if r["owner_priced"] else ""}</td>'
-        f'<td class="mono">{r["wave"] or "—"}</td></tr>' for r in rows)
+    trs = group_rows(rows)
     stamps = "".join(
         f'<tr><td class="mono">{e(s["version"])}</td><td class="mono">{_when(s["at"])}</td>'
         f'<td>{e(", ".join(map(short, s["carries"])) or "—")}</td>'
@@ -707,7 +790,14 @@ def render(roster: dict, roster_src: str, plan: dict, snap: dict,
         "now": _t(gen["start"]).strftime("%d %b %H:%M"),
         "source": e(f'{roster_src} @ {gen["roster_blob"][:12]}'),
         "tracking": str(TRACKING_ISSUE), "open_iss": open_iss,
-        "phases": plan_phases.section(*phases, axis=time_axis(plan)) if phases else "",
+        "tabs_nav": (_TABS_NAV.format(cur=round_n, nxt=plan["next_round"]["round"])
+                     if tabbed else ""),
+        "pane_open": '<div id="tab-cur" class="tabpane">\n' if tabbed else "",
+        "next_pane": ('</div>\n<div id="tab-next" class="tabpane" hidden>\n'
+                      + next_round_pane(whole, plan, full_snap) + '</div>\n' + _TABS_JS
+                      if tabbed else ""),
+        "phases": plan_phases.section(*phases, axis=time_axis(plan),
+                                                      phase_hours=model.get("phase_hours")) if phases else "",
         "issues_chart": issues_section(roster, plan, snap),
         "flow": flow_section(plan, rows, flow),
         "end": _t(summ["closure"]).strftime("%a %d %b %H:%M"),
@@ -1361,6 +1451,21 @@ def _self_test() -> int:
                      for x in (sec, swimlanes(plan, build_rows(roster, plan, snap))[0])]
             check("groups and phases: the phases are drawn on the swimlanes' own time axis",
                   ticks[0] and ticks[0] == ticks[1], ticks)
+            # durations.json, then build_plan, then render: the production path.
+            plan_m = replan.build_plan(r_, dict(durations, phase_hours={"finders": 7.5}),
+                                       dict(replan.DEFAULT_CAPS), start, "v1.0.0", ref_, blob_,
+                                       round_n=roster_lib.roster_round(str(rpath)))
+            measured = render(roster, src, plan_m, snap, None, fx)
+            check("a phase durations.json prices reaches the plan's model and the page prints "
+                  "its figure; one it does not prints 'duration unmeasured', never a zero or a "
+                  "typed constant; the rest a dash",
+                  plan_m["generated"]["model"].get("phase_hours") == {"finders": 7.5}
+                  and "phase_hours" not in plan["generated"]["model"]
+                  and replan.check_plan(plan_m) == []
+                  and "7.5 h (plan model)" in measured and "duration unmeasured" in measured
+                  and "duration unmeasured" in both and "plan model)" not in both
+                  and measured.count("duration unmeasured") == both.count("duration unmeasured") - 1,
+                  (both.count("duration unmeasured"), measured.count("duration unmeasured")))
             check("null control, groups only: no phases section, nothing of the phases drawn",
                   'id="phases"' not in groups_only and "PHASES UNAVAILABLE" not in groups_only)
             empty = replan.build_plan({"groups": []}, json.loads(
@@ -1374,6 +1479,134 @@ def _self_test() -> int:
                   and '<tbody id="rows"></tbody>' in phases_only, phases_only[:200])
             check("null control, phases only: the same empty roster with no phases file draws none",
                   'id="phases"' not in render({"groups": []}, src, empty, snap))
+            # A round's page covers that round's groups only; the next round's are
+            # the second tab, on a preliminary schedule from this round's closure
+            # (owner, 2026-11-13). The roster of round 9 plus two groups of round 10.
+            def later_roster(*extra):
+                return {"groups": roster["groups"] + [
+                    grp("R10-NEXT-A", "IN", issues=(77,)),
+                    grp("R10-NEXT-B", "IN", after=("R10-NEXT-A", "R9-LIVE"), size="M")]
+                    + [grp(x, "IN") for x in extra]}
+            caps_ = dict(replan.DEFAULT_CAPS)
+
+            def planned(r):
+                return replan.build_round_plan(r, durations, caps_, start, "v1.0.0", "main",
+                                               "", round_n=9)
+            p0, p2, p3 = planned(roster), planned(later_roster()), planned(later_roster("R10-NEXT-C"))
+            snap77 = dict(snap, issues=snap["issues"] + [
+                {"number": 77, "title": "seventy-seven", "state": "OPEN"}])
+            check("a roster with a next-round group plans the same closure, groups, stamps "
+                  "and waves as the roster without it (null control: the plans differ in "
+                  "next_round alone)",
+                  {k: v for k, v in p2.items() if k != "next_round"} == p0
+                  and "next_round" not in p0 and p2["next_round"]["round"] == 10,
+                  [k for k in p0 if p0[k] != p2.get(k)])
+            nsub = p2["next_round"]["plan"]
+            check("the next round is scheduled apart, from this round's closure, on the same "
+                  "model; an after-edge to this round's group is dropped, one inside it kept",
+                  set(nsub["groups"]) == {"R10-NEXT-A", "R10-NEXT-B"}
+                  and nsub["generated"]["start"] == p2["summary"]["closure"]
+                  and nsub["groups"]["R10-NEXT-B"]["after"] == ["R10-NEXT-A"]
+                  and nsub["groups"]["R10-NEXT-B"]["start"] >= nsub["groups"]["R10-NEXT-A"]["finish"]
+                  and nsub["generated"]["model"] == p2["generated"]["model"]
+                  and nsub["summary"]["closure_stamp"] == "v10.0.0"
+                  and replan.check_plan(p2) == [], str(nsub["summary"])[:200])
+            try:
+                replan.build_round_plan({"groups": roster["groups"] + [
+                    grp("R10-NEXT-A", "IN"), grp("R9-BAD", "IN", after=("R10-NEXT-A",))]},
+                    durations, caps_, start, "v1.0.0", "main", "", round_n=9)
+                check("a group of this round waiting on a later round's group is refused", False)
+            except replan.PlanError as exc:
+                check("a group of this round waiting on a later round's group is refused",
+                      "later round" in str(exc), str(exc))
+            only = render(roster, src, p0, snap)
+            tabbed = render(later_roster(), src, p2, snap77)
+            tabbed3 = render(later_roster("R10-NEXT-C"), src, p3, snap77)
+
+            def panes(page):
+                a_ = page.index('<div id="tab-cur" class="tabpane">\n') + len('<div id="tab-cur" class="tabpane">\n')
+                b_ = page.index('</div>\n<div id="tab-next"')
+                return page[a_:b_], page[b_:]
+            cur2, nxt2 = panes(tabbed)
+            cur3, nxt3 = panes(tabbed3)
+            check("the current round's tab is the page without the next round's groups: strip, "
+                  "closure, lanes, rows and every section, though a next-round group carries an "
+                  "open issue",
+                  cur2 == only[only.index('<div class="strip">'):only.index("</main>")],
+                  [ln for ln in cur2.splitlines() if ln not in only][:3])
+            check("adding a next-round group changes nothing on the current tab and adds one "
+                  "bar to the other",
+                  cur3 == cur2 and nxt2.count('<g class="grp" data-tab="next"') == 2
+                  and nxt3.count('<g class="grp" data-tab="next"') == 3
+                  and 'data-name="NEXT-' not in cur3)
+            check("the second tab is labelled preliminary, names the closure it starts at, and "
+                  "lists its groups; the first tab names none of them",
+                  "Round 10 (preliminary)" in tabbed and "Preliminary: round 10" in nxt2
+                  and _when(p2["summary"]["closure"]) in nxt2 and "NEXT-A" in nxt2
+                  and "NEXT-A" not in cur2 and 'id="rows-next"' in nxt2)
+            check("null control: a page whose roster has no next-round group has no tabs",
+                  'class="tabs"' not in only and "tab-next" not in only)
+            check("a plan recorded without a next-round schedule draws no round-10 row and no tab",
+                  "NEXT-A" not in render(later_roster(), src, p0, snap)
+                  and "tab-next" not in render(later_roster(), src, p0, snap))
+            broken = {**p2, "next_round": {**{k: v for k, v in p2["next_round"].items()
+                                              if k != "plan"}, "unavailable": "boom"}}
+            check("a next round that cannot be planned is an UNAVAILABLE tab, never an absent one",
+                  "UNAVAILABLE: boom" in render(later_roster(), src, broken, snap))
+            bad_nxt = json.loads(json.dumps(p2))
+            del bad_nxt["next_round"]["plan"]["generated"]["model"]
+            check("check_plan checks the next round's plan: a violation in it is the round "
+                  "plan's, named by the next round (null control: p2 reads [] above)",
+                  replan.check_plan(bad_nxt)
+                  == ["next round 10: model: the plan records no duration model (generated.model)"],
+                  replan.check_plan(bad_nxt))
+            unplannable = later_roster()
+            unplannable["groups"][-2] = dict(unplannable["groups"][-2], savings="lots")
+            try:
+                pu = planned(unplannable)
+                nu = pu["next_round"]
+                check("a later round the model refuses is next_round.unavailable, the round's "
+                      "own plan unchanged, drawn as an UNAVAILABLE tab",
+                      "plan" not in nu and "R10-NEXT-A: savings is not a number" in nu["unavailable"]
+                      and {k: v for k, v in pu.items() if k != "next_round"} == p0
+                      and "UNAVAILABLE: R10-NEXT-A: savings is not a number"
+                      in render(unplannable, src, pu, snap77), nu)
+            except replan.PlanError as exc:
+                check("a later round the model refuses is next_round.unavailable, the round's "
+                      "own plan unchanged, drawn as an UNAVAILABLE tab", False, str(exc))
+            far = later_roster("R11-FAR-A", "R12-FAR-B")
+            pf_ = planned(far)
+            check("groups of rounds past the nearest are counted in beyond, not scheduled, and "
+                  "the tab says so (null control: a roster with none counts 0 and says nothing)",
+                  pf_["next_round"]["round"] == 10 and pf_["next_round"]["beyond"] == 2
+                  and set(pf_["next_round"]["plan"]["groups"]) == {"R10-NEXT-A", "R10-NEXT-B"}
+                  and "2 more group(s) belong to rounds after 10" in render(far, src, pf_, snap77)
+                  and p2["next_round"]["beyond"] == 0 and "more group(s) belong" not in tabbed,
+                  pf_["next_round"].get("beyond"))
+            # Carry 3: a figure on the page equals the rows it counts.
+            part_snap = dict(snap, merged_prs=snap["merged_prs"] + [
+                {"number": 24, "title": "R9-HELD: part", "head_ref": "fix/held",
+                 "merge_commit_sha": "f" * 40, "merged_at": "2026-01-04T00:00:00Z"}])
+            pp = render(roster, src, p0, part_snap)
+            n_strip = int(re.search(r"<b>(\d+)</b><span>part merged", pp).group(1))
+            n_rows = pp.count('data-part="1"><td class="g">')
+            n_label = len(re.findall(r'<span class="pill [a-z]+"[^>]*>[^<]*part merged', pp))
+            check("the strip's part-merged count equals the rows that read part merged "
+                  "(an absorbed group a merged PR names is not one)",
+                  n_strip == n_rows == n_label and n_strip >= 1
+                  and "part merged" not in {r["g"]: r for r in build_rows(
+                      roster, p0, part_snap)}["R9-HELD"]["label"], (n_strip, n_rows, n_label))
+            n_open = len(re.findall(r'<tr class="(?!done)[a-z]+" data-st', pp))
+            m_ = re.search(r"of the (\d+) the table lists as not merged; the other (\d+) are held", pp)
+            check("the lede's open-group figures equal the rows: not-merged rows, and the "
+                  "held remainder against the plan's scheduled groups",
+                  m_ and int(m_.group(1)) == n_open
+                  and int(m_.group(2)) == n_open - p0["summary"]["groups_open"], (m_ and m_.groups(), n_open))
+            check("a markdown brief renders as its title or first sentence, never a bare list marker",
+                  roster_lib.one_line_brief({"brief": "1. N-x (#1): does a thing. More."}) == "N-x (#1): does a thing."
+                  and roster_lib.one_line_brief({"brief": "# Fixer brief X: land Y\nState found: z."})
+                  == "Fixer brief X: land Y"
+                  and roster_lib.one_line_brief({"brief": "Plain. Two."}) == "Plain.")
             pf = Path(td) / "outside" / "phases.json"
             pf.parent.mkdir()
             pf.write_text(json.dumps(plan_phases.fixture()), encoding="utf-8")
@@ -1567,6 +1800,11 @@ td.st{min-width:11rem}
 .filters button[aria-pressed="true"]{background:var(--fg);color:var(--panel);border-color:var(--fg)}
 .filters button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
 .note{color:var(--muted);font-size:.85rem;max-width:72ch}
+.tabs{display:flex;gap:8px;margin-top:10px}
+.tabs button{font:600 .9rem var(--body);background:var(--bg);color:var(--fg);border:1px solid var(--line);border-radius:6px 6px 0 0;padding:6px 16px;cursor:pointer}
+.tabs button[aria-selected="true"]{background:var(--fg);color:var(--panel);border-color:var(--fg)}
+.tabpane{display:flex;flex-direction:column;gap:22px}
+.tabpane[hidden]{display:none}
 .tip{position:fixed;z-index:20;max-width:300px;background:var(--panel);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:7px 10px;font:12px/1.4 var(--body);box-shadow:0 8px 22px rgba(0,0,0,.18);pointer-events:none}
 .tip b{font-family:var(--mono);font-size:12.5px}
 .tip span{color:var(--muted)}
@@ -1575,9 +1813,9 @@ td.st{min-width:11rem}
 <header>
   <h1>{{title}}</h1>
   <p class="sub">heatpump_optimizer audit programme · snapshot {{now}} UTC · schedule read from <code>plan.json</code> (roster {{source}}) · tracking issue #{{tracking}}</p>
-</header>
+</header>{{tabs_nav}}
 
-<div class="strip">
+{{pane_open}}<div class="strip">
   <div class="stat"><b>{{n_done}}</b><span>groups merged</span></div>
   <div class="stat"><b>{{n_live}}</b><span>fixers working</span></div>
   <div class="stat"><b>{{n_ready}}</b><span>ready, not started</span></div>
@@ -1648,7 +1886,7 @@ td.st{min-width:11rem}
   <h2>How the ETAs are computed</h2>
   <p class="note">Every figure on this page is <code>plan.json</code>'s, written by <code>tools/plan/replan.py</code>; this renderer draws it and computes no schedule of its own. A wave is the set of groups dispatched at one moment, and the next opens as soon as one of {{slots}} pull-request slots frees, so a wave never waits for the previous one to drain; the cap limits concurrency, not the wave boundary. Duration is dispatch to merge by roster size, as the plan recorded it from <code>tools/plan/durations.json</code>: {{sizes}}. {{sizes_provenance}} A group whose fixer is already working gets {{live_pct}}% of its size duration as the remaining estimate, and starts now, past the slot cap, unless an unmerged dependency holds it; a held (carries-open) group is priced by its open carries, not its size. Hover an ETA for the group's tier, why it starts when it does, its duration basis and its sort key, all the plan's own fields. Those are measured lead times, not effort: review rounds and queueing are inside them. The batching window is {{window}} minutes; its measured trade is in <code>durations.json</code>.</p>
 </section>
-</main>
+{{next_pane}}</main>
 <div id="tip" class="tip" hidden></div>
 <script>
 (function(){
@@ -1670,7 +1908,7 @@ td.st{min-width:11rem}
     g.addEventListener('mouseleave',function(){tip.hidden=true});
   });
   var bs=document.querySelectorAll('.filters button'), rows=document.querySelectorAll('#rows tr'),
-      bars=document.querySelectorAll('svg g.grp'), hide=document.getElementById('hide-done'), f='all';
+      bars=document.querySelectorAll('svg g.grp:not([data-tab])'), hide=document.getElementById('hide-done'), f='all';
   function shown(st,part){ return (f==='all'||st===f||(f==='partial'&&part==='1')) && !(hide.checked && st==='done'); }
   function apply(){
     rows.forEach(function(r){ r.hidden=!shown(r.getAttribute('data-st'),r.getAttribute('data-part')); });
diff --git a/tools/audit/seat/plan_phases.py b/tools/audit/seat/plan_phases.py
index 9ed8ff8e9e..aeac81b480 100644
--- a/tools/audit/seat/plan_phases.py
+++ b/tools/audit/seat/plan_phases.py
@@ -286,7 +286,28 @@ ul.items li{margin:2px 0;break-inside:avoid}
 </style>"""
 
 
-def section(doc, bad: list | None = None, where: str = "", axis: tuple | None = None) -> str:
+#: The phases whose duration the plan's model prices: `phase_hours`, keyed by
+#: these ids, which `replan.build_plan` copies from `durations.json` into
+#: `generated.model` (`replan.MODEL_FIELDS`) and `plan_page.render` hands to
+#: `section`. One the model has no figure for is printed "duration
+#: unmeasured", never a typed constant or a zero.
+MODEL_TIMED = ("finders", "verify-judge", "plan")
+
+
+def _model_duration(r: dict, phase_hours: dict | None) -> str:
+    """The Planned cell of a phase with no forecast: the model's duration for a
+    phase it prices (not done), "duration unmeasured" where it has none, a dash
+    for every other phase."""
+    if r["status"] == "done" or r["phase"] not in MODEL_TIMED:
+        return "—"
+    h = (phase_hours or {}).get(r["phase"])
+    if isinstance(h, bool) or not isinstance(h, (int, float)) or h <= 0:
+        return "duration unmeasured"
+    return f"{h:g} h (plan model)"
+
+
+def section(doc, bad: list | None = None, where: str = "", axis: tuple | None = None,
+            phase_hours: dict | None = None) -> str:
     """The phases section for the plan page: a timeline and one row per phase,
     the running phases' items under them. `bad` (from `violations`) draws the
     UNAVAILABLE section instead, naming the first refusal. `axis` is the plan
@@ -301,7 +322,7 @@ def section(doc, bad: list | None = None, where: str = "", axis: tuple | None =
     for r in rows:
         fc = r.get("forecast")
         planned = (f'start {_when(fc["start_from"])} to {_when(fc["start_to"])}'
-                   f'<div class="lanec">{e(fc["basis"])}</div>' if fc else "—")
+                   f'<div class="lanec">{e(fc["basis"])}</div>' if fc else _model_duration(r, phase_hours))
         items = ""
         if r.get("items") and r["status"] != "done":
             items = '<tr class="items"><td></td><td colspan="6"><ul class="items">' + "".join(
diff --git a/tools/audit/seat/postmerge.py b/tools/audit/seat/postmerge.py
index 963487f9fc..ed6b01af3d 100644
--- a/tools/audit/seat/postmerge.py
+++ b/tools/audit/seat/postmerge.py
@@ -2,7 +2,7 @@
 """After a merge: the bookkeeping no contract hands an agent (`standing-merge.md`).
 
     python3 tools/audit/seat/postmerge.py [--repo O/R] [--state-dir D] [--dry-run] [--retry] <PR>
-    python3 tools/audit/seat/postmerge.py --self-test
+    python3 tools/audit/seat/postmerge.py --self-test [--no-mutants]
 
 Both merge paths (`merge_pr.sh`, and `merge_train.py`'s landing) call it once
 the merge is confirmed. It runs, in order, and a failure in any is printed as
@@ -11,9 +11,30 @@ the merge is confirmed. It runs, in order, and a failure in any is printed as
   record   `record_beat.py`: one record-issue line from the fixed template, posted by
            `tools/pr/gh_comment.py` with a byte-identical read-back.
   stage    `roster_sync.py --apply` derives the group's `done` stage from the
-           merged pull request. A refused sync prints `set-stage owed <GROUP>
-           <merge sha>`, the group resolved from the roster (`record_beat.
-           resolve_group`) or `no-group <merge sha>`, never guessed.
+           merged pull request, the group resolved from the roster
+           (`record_beat.resolve_group`), never guessed. A refused or raced
+           sync queues `set-stage <GROUP> done --at-sha <merge sha>` on the
+           beat's roster drain (below) and prints `stage QUEUED <line>`: the
+           direct push is kept first, and the drain, which retries nothing it
+           refused but records each refusal in its events, is the one writer
+           of the retry (a second push loop here lost every race against a
+           backlogged drain). With no group, or a queue it cannot write, it
+           prints `set-stage owed <GROUP>|no-group <merge sha>` and is owed.
+  marks    each merged-body line `Carry N: built here (<KEY>, ...)` or `Carry
+           N: dismissed (<KEY>, <reason>)` is one `mark-carry <GROUP> --match
+           <KEY> implemented <merge sha>|dismissed <reason>` op on the drain,
+           keyed on KEY because the body counts carries from 1 and the roster
+           from 0. KEY must be contained in exactly one carry of the group; a
+           line naming no key, or one hitting zero or two carries, prints
+           `OWED mark: ...` and queues nothing. A carry already marked is
+           skipped. Marks queue before the stage op, so `done` reads them.
+
+THE QUEUE is `<state dir>/roster-drain.queue`, the file beat_jobs.py's
+roster-drain row runs. Every line postmerge appends ends `# postmerge <merge
+sha>` (roster_queue's grammar drops a `#` word and what follows); a line
+already in the queue, marked or not, is not appended again, so a rerun for one
+merge queues nothing. The new lines go in one `O_APPEND` write, each
+newline-terminated: the drain runs only terminated lines.
   main     `merge_train.py classify <merge sha> --main`: main's own suite
            state, the one rule the train and the sweep read (no third). RED or
            unreadable is owed; WAIT (the push's checks still running) is not.
@@ -31,12 +52,20 @@ from __future__ import annotations
 
 import argparse
 import os
+import re
+import shlex
 import sys
 from pathlib import Path
 
 SEAT = Path(__file__).resolve().parent
 sys.path.insert(0, str(SEAT))
 import record_beat as rb  # noqa: E402
+import roster_lib  # noqa: E402  the carry-mark grammar
+
+QUEUE = "roster-drain.queue"
+#: A body's carry disposition line: bullet optional, the key the first comma-separated
+#: field inside the parentheses. "Carry N: not built here" does not match.
+DISPOSED = re.compile(r"^[ \t]*(?:[-*][ \t]+)?Carry (\d+): (built here|dismissed)\b(?: \(([^)\n]*)\))?", re.M)
 
 ROOT = rb.ROOT
 PY = [sys.executable, "-I"]
@@ -61,6 +90,51 @@ def refusal_detail(o: str) -> str:
     return " | ".join(errs + [lines[-1]])[:300]
 
 
+def derive_marks(body: str, roster: "dict | None", group: str, sha: str) -> "tuple[list[str], list[str]]":
+    """(mark-carry op lines, owed reasons) for the body's DISPOSED lines,
+    each keyed on its quoted text and checked to hit exactly one carry."""
+    lines = list(DISPOSED.finditer(body or ""))
+    g = next((x for x in (roster or {}).get("groups", []) if x.get("group") == group), None)
+    if lines and g is None:
+        return [], [f"{len(lines)} carry disposition line(s) and no roster group {group}"]
+    ops, owed = [], []
+    for m in lines:
+        n, kind, inner = m.groups()
+        key, _, why = (inner or "").partition(",")
+        key, why = key.strip(), why.strip()
+        hits = [c for c in g.get("carry", []) if key and key in c]
+        if not key or len(hits) != 1:
+            owed.append(f"Carry {n}: {kind} key {key!r} hits {len(hits)} carries of {group}, not one")
+            continue
+        if roster_lib.carry_mark(hits[0]):
+            continue  # marked already: a second mark is refused, so none is queued
+        if kind == "dismissed" and (not why or "]" in why):
+            owed.append(f"Carry {n}: dismissed names no reason a mark can hold: {why!r}")
+            continue
+        mark = f"implemented {sha}" if kind == "built here" else f"dismissed {shlex.quote(why)}"
+        ops.append(f"mark-carry {group} --match {shlex.quote(key)} {mark}")
+    return ops, owed
+
+
+def enqueue(state_dir: Path, ops: "list[str]", sha: str) -> "list[str]":
+    """Append each op not already queued for this merge; return the appended lines."""
+    path = state_dir / QUEUE
+    have = set()
+    for raw in (path.read_text().splitlines() if path.exists() else ()):
+        text = raw.strip()
+        for pre in ("#done ", "#refused ", "#held "):
+            text = text[len(pre):] if text.startswith(pre) else text
+        have.add(text)
+    new = [line for line in (f"{op}  # postmerge {sha}" for op in ops) if line not in have]
+    if new:
+        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
+        try:
+            os.write(fd, "".join(line + "\n" for line in new).encode())
+        finally:
+            os.close(fd)
+    return new
+
+
 def postmerge(pr: int, repo: str, state_dir: Path, dry: bool, retry: bool = False,
               run=rb.sh, out=print, roster=None) -> int:
     owed: "list[tuple[str, str]]" = []
@@ -70,11 +144,14 @@ def postmerge(pr: int, repo: str, state_dir: Path, dry: bool, retry: bool = Fals
         out(f"OWED record: {e}")
         return 1  # no full sha: nothing below can name its subject
     sha = f["sha"]
-    group = rb.resolve_group(roster if roster is not None else rb.load_roster(run), f["branch"], pr)
+    roster_now = roster if roster is not None else rb.load_roster(run)
+    group = rb.resolve_group(roster_now, f["branch"], pr)
     try:
         rb.record(pr, repo, state_dir, f, group, dry, run, out)
     except rb.Owed as e:
         owed.append(("record", str(e)))
+    marks, unkeyed = derive_marks(f.get("body", ""), roster_now, group, sha) if group != rb.NO_GROUP else ([], [])
+    owed += [("mark", why) for why in unkeyed]
     for name, argv, mutating in steps(pr, repo, state_dir, sha, group):
         if dry:
             out(f"DRY-RUN {name}: " + " ".join(argv))
@@ -85,10 +162,31 @@ def postmerge(pr: int, repo: str, state_dir: Path, dry: bool, retry: bool = Fals
             out(f"main {last}")
             if code == 3:  # WAIT: the push's own checks are still running
                 continue
+        if name == "stage":
+            queued = marks + ([f"set-stage {group} done --at-sha {sha}"] if code != 0 else [])
+            if not queued:
+                continue  # a clean sync and no mark: nothing to queue, nothing owed
+            try:
+                if group == rb.NO_GROUP:
+                    raise OSError("no group to queue")
+                new = enqueue(state_dir, queued, sha)
+            except OSError as e:
+                if code == 0:
+                    owed.append(("mark", f"queue: {e}"))
+                    continue
+                owed.append((name, f"rc {code}: {last}"))
+                out(f"set-stage owed {group} {sha}" if group != rb.NO_GROUP else f"set-stage owed no-group {sha}")
+                continue
+            if code != 0:
+                out(f"stage refused rc {code}: {last}")
+            for line in new:
+                out(f"{'stage' if line.startswith('set-stage ') else 'mark'} QUEUED {line}")
+            continue
         if code != 0:
             owed.append((name, f"rc {code}: {last}"))
-            if name == "stage":
-                out(f"set-stage owed {group} {sha}" if group != rb.NO_GROUP else f"set-stage owed no-group {sha}")
+    if dry:
+        for op in marks:
+            out(f"DRY-RUN queue: {op}  # postmerge {sha}")
     for name, why in owed:
         out(f"OWED {name}: {why}")
     ledger = [*PY, f"{SEAT}/ledger.py"]
@@ -110,16 +208,40 @@ def main(argv=None) -> int:
     ap.add_argument("--dry-run", action="store_true")
     ap.add_argument("--retry", action="store_true", help="a rerun of an owed merge: a clean run closes the event")
     ap.add_argument("--self-test", action="store_true")
+    ap.add_argument("--no-mutants", action="store_true", help="the self-test without its mutant pass")
     a = ap.parse_args(argv)
     if a.self_test:
-        return self_test()
+        return self_test(mutants=not a.no_mutants)
     if a.pr is None:
         ap.error("give the merged <PR>")
     return postmerge(a.pr, a.repo, Path(a.state_dir), a.dry_run, a.retry)
 
 
-def self_test() -> int:
+#: (site, replacement, the case it must turn red), each run on a temp copy.
+MUTANTS = {
+    "null": ("", "", ""),  # no edit: the copy must pass whole, or a crash would read as every kill
+    "no_newline": ('os.write(fd, "".join(line + "\\n" for line in new).encode())',
+                   'os.write(fd, "".join(line for line in new).encode())',
+                   "(i) a refused or raced stage queues exactly one terminated line for the merge, owing nothing"),
+    "no_idempotence_key": ('    new = [line for line in (f"{op}  # postmerge {sha}" for op in ops) if line not in have]',
+                           '    new = [line for line in (f"{op}  # postmerge {sha}" for op in ops)]',
+                           "(ii) a second postmerge run for that merge queues nothing, the first line marked or not"),
+    "marks_by_index": ('        hits = [c for c in g.get("carry", []) if key and key in c]',
+                       '        hits = [c for c in g.get("carry", [])[int(n):int(n) + 1]]\n        key = hits[0][:20] if hits else key',
+                       "(i) #3470's body yields exactly the two marks batch 236 queued by hand, keyed on text"),
+    "two_hits_taken": ('        if not key or len(hits) != 1:', '        if not key or not hits:',
+                       "a key hitting two carries, none, or no key is OWED and queues nothing; a marked carry is skipped"),
+    "empty_queue_owed": ("            if not queued:\n                continue", "            if False:\n                continue",
+                         "a clean sync with no roster group owes nothing, queues nothing and opens no ledger event"),
+    "stage_not_queued": ('            queued = marks + ([f"set-stage {group} done --at-sha {sha}"] if code != 0 else [])',
+                         '            queued = marks',
+                         "(i) a refused or raced stage queues exactly one terminated line for the merge, owing nothing"),
+}
+
+
+def self_test(mutants: bool = True) -> int:
     import json
+    import subprocess
     import tempfile
     fails, n = [], [0]
 
@@ -155,11 +277,17 @@ def self_test() -> int:
             return 0, ""
         return run, log
 
-    def go(rc=None, dry=False, retry=False, said=None):
+    def go(rc=None, dry=False, retry=False, said=None, state=None, body="", ros=None):
         run, log = fake(rc, said)
         lines = []
-        with tempfile.TemporaryDirectory() as td:
-            code = postmerge(7, rb.DEFAULT_REPO, Path(td), dry, retry, run, lines.append, roster)
+        real = rb.facts
+        rb.facts = lambda *a, **k: {**real(*a, **k), "body": body}  # the fake's gh answer carries no body
+        try:
+            with tempfile.TemporaryDirectory() as td:
+                code = postmerge(7, rb.DEFAULT_REPO, Path(state or td), dry, retry, run, lines.append,
+                                 roster if ros is None else ros)
+        finally:
+            rb.facts = real
         return code, lines, [" ".join(map(str, a)) for a in log]
 
     code, lines, log = go()
@@ -175,7 +303,7 @@ def self_test() -> int:
           and [l.split(":")[0] for l in lines[1:4]] == ["DRY-RUN command", "DRY-RUN stage", "DRY-RUN main"]
           and not any(k in c for c in log for k in ("gh_comment", "roster_sync", "classify", "ledger")),
           lines)
-    for key, step in (("gh_comment.py", "record"), ("roster_sync.py", "stage"), ("classify", "main")):
+    for key, step in (("gh_comment.py", "record"), ("classify", "main")):
         code, lines, log = go({key: 1})
         owed = [l for l in lines if l.startswith("OWED ")]
         check(f"a refused {step} step prints OWED {step}, exits non-zero, after the other steps ran",
@@ -183,14 +311,101 @@ def self_test() -> int:
               and sum("roster_sync.py" in c or "gh_comment" in c for c in log) >= 2, lines)
         check(f"... and opens postmerge-owed for the pull request and the full merge sha ({step})",
               any(f"ledger.py open postmerge-owed 7 {full} " in c for c in log), log)
-    code, lines, _ = go({"roster_sync.py": 1})
-    check("a refused stage names the resolved group: set-stage owed <GROUP> <merge sha>",
-          f"set-stage owed R10-X {full}" in lines, lines)
+    import roster_queue as rq
+    stage_line = f"set-stage R10-X done --at-sha {full}  # postmerge {full}"
+    with tempfile.TemporaryDirectory() as st:
+        q = Path(st) / QUEUE
+        code, lines, _ = go({"roster_sync.py": 1}, state=st)
+        first = q.read_text() if q.exists() else ""
+        check("(i) a refused or raced stage queues exactly one terminated line for the merge, owing nothing",
+              code == 0 and first == stage_line + "\n" and f"stage QUEUED {stage_line}" in lines
+              and not any(l.startswith("OWED") for l in lines), (first, lines))
+        check("... and that line parses as the set-stage op it names, replay-safe",
+              rq.parse_line(first) == ("set-stage", "R10-X", "done", ["--at-sha", full])
+              and rq.replay_unsafe("set-stage", ["--at-sha", full]) is None, rq.parse_line(first))
+        q.write_text(f"#done {first}" + "set-stage R10-Y done\n")
+        code, lines, _ = go({"roster_sync.py": 1}, state=st)
+        check("(ii) a second postmerge run for that merge queues nothing, the first line marked or not",
+              q.read_text() == f"#done {stage_line}\nset-stage R10-Y done\n"
+              and not any("QUEUED" in l for l in lines), lines)
+    with tempfile.TemporaryDirectory() as st:
+        code, lines, _ = go(state=st)
+        check("(iii) null control: a sync that landed queues nothing and creates no queue",
+              code == 0 and not (Path(st) / QUEUE).exists() and not any("QUEUED" in l for l in lines), lines)
+    with tempfile.TemporaryDirectory() as st:
+        (Path(st) / QUEUE).mkdir()  # a queue that cannot be written
+        code, lines, log = go({"roster_sync.py": 1}, state=st)
+        check("a refused stage whose queue cannot be written is owed: set-stage owed <GROUP> <merge sha>",
+              code == 1 and f"set-stage owed R10-X {full}" in lines
+              and any(l.startswith("OWED stage: rc 1:") for l in lines)
+              and any(f"ledger.py open postmerge-owed 7 {full} " in c for c in log), lines)
+    with tempfile.TemporaryDirectory() as st:
+        code, lines, _ = go({"roster_sync.py": 1}, state=st, ros={"groups": []})
+        check("a refused stage with no roster group queues nothing and is owed as no-group",
+              code == 1 and f"set-stage owed no-group {full}" in lines and not (Path(st) / QUEUE).exists(), lines)
+    with tempfile.TemporaryDirectory() as st:
+        code, lines, log = go(state=st, ros={"groups": []}, body="- x. Carry 1: built here")
+        check("a clean sync with no roster group owes nothing, queues nothing and opens no ledger event",
+              code == 0 and lines[-1].endswith("nothing owed") and not any(l.startswith("OWED") for l in lines)
+              and not (Path(st) / QUEUE).exists() and not any("ledger.py open" in c for c in log), lines)
     gate = ("roster_edit: LINT GATE REFUSED the push\n  ERROR   [G-1] cite: a.py:9 moved\n\n"
             "TOTAL: 1 error(s) across 1 file(s)\nthe commit is local at 0123 in /w; nothing pushed\n")
     code, lines, _ = go({"roster_sync.py": 3}, said={"roster_sync.py": gate})
-    check("a stage refused by the lint gate owes its ERROR line, not only the last line (P435)",
-          any(l.startswith("OWED stage: rc 3: ") and "[G-1] cite: a.py:9" in l for l in lines), lines)
+    check("a stage refused by the lint gate prints its ERROR line, not only the last line (P435)",
+          any(l.startswith("stage refused rc 3: ") and "[G-1] cite: a.py:9" in l for l in lines), lines)
+    # (v) replay of #3447 (merge ceb3070ccb, group R10-OUTSIDE-DIAG-REDACT-LOCATION), whose stage was routed by hand
+    merged = "ceb3070ccb49fe6dfc9d403458e8a3cc03c5595e"
+    with tempfile.TemporaryDirectory() as st:
+        enqueue(Path(st), [f"set-stage R10-OUTSIDE-DIAG-REDACT-LOCATION done --at-sha {merged}"], merged)
+        got = (Path(st) / QUEUE).read_text()
+    parsed = rq.parse_line(got)
+    check("(v) #3447's derived stage op passes roster_queue.parse_line and replay_unsafe",
+          parsed == ("set-stage", "R10-OUTSIDE-DIAG-REDACT-LOCATION", "done", ["--at-sha", merged])
+          and rq.replay_unsafe(parsed[0], parsed[3]) is None, got)
+    # marks: the #3470 replay (merge be86e36a56, R10-TRAIN-RESIDUE-P2; triage batch 236 queued its two marks by hand)
+    m3470 = "be86e36a560fde88cc758cefcee322b9087a5deb"
+    owed_key = "Carry 3: left for a later part; it stays on the roster."
+    body3470 = ("Builds carries 17 and 18.\n\n" + "".join(f"- Carry {i}: left for a later part; it stays on the roster.\n"
+                                                       for i in range(1, 17))
+                + "- Carry 17: built here (TRAIN-POLICY-REASON-STALE-CONTEXT, `rollup_states`).\n"
+                "- Carry 18: built here (TRAIN-UNDRAFT-EVERY-ROUTE, `record_drafts` and the `land` draft arm).\n")
+    carries = [f"C{i} owed text" for i in range(16)] + [
+        "TRAIN-POLICY-REASON-STALE-CONTEXT (triage: x#P608), in merge_train.py policy_refusal",
+        "TRAIN-UNDRAFT-EVERY-ROUTE (triage: x#P609), in merge_train.py undraft()"] + [f"C{i} tail" for i in range(18, 23)]
+    r3470 = {"groups": [{"group": "R10-TRAIN-RESIDUE-P2", "carry": carries}]}
+    ops, why = derive_marks(body3470, r3470, "R10-TRAIN-RESIDUE-P2", m3470)
+    want = [f"mark-carry R10-TRAIN-RESIDUE-P2 --match TRAIN-POLICY-REASON-STALE-CONTEXT implemented {m3470}",
+            f"mark-carry R10-TRAIN-RESIDUE-P2 --match TRAIN-UNDRAFT-EVERY-ROUTE implemented {m3470}"]
+    check("(i) #3470's body yields exactly the two marks batch 236 queued by hand, keyed on text", ops == want and not why,
+          (ops, why))
+    check("... each passes roster_queue.parse_line and replay_unsafe as a --match op",
+          all(rq.parse_line(o)[:2] == ("mark-carry", "R10-TRAIN-RESIDUE-P2")
+              and rq.replay_unsafe("mark-carry", rq.parse_line(o)[3]) is None for o in ops), ops)
+    check("(iii) null control: a body with no built or dismissed line yields no op and owes nothing",
+          derive_marks("Carry 1: left for a later part.\n- Carry 2: not built here. Carry: R10-X\n" + owed_key,
+                        r3470, "R10-TRAIN-RESIDUE-P2", m3470) == ([], []))
+    two = {"groups": [{"group": "G", "carry": ["KEY-A one", "KEY-A two", "KEY-B [implemented: abc1234]", "plain"]}]}
+    ops, why = derive_marks("- Carry 1: built here (KEY-A, x)\n- Carry 2: built here.\n- Carry 3: built here (NONE)\n"
+                            "- Carry 4: built here (KEY-B)\n- Carry 5: dismissed (plain, superseded by #12)\n"
+                            "- Carry 6: dismissed (plain)\n", two, "G", m3470)
+    check("a key hitting two carries, none, or no key is OWED and queues nothing; a marked carry is skipped",
+          ops == ["mark-carry G --match plain dismissed 'superseded by #12'"]
+          and [w.split(":")[0] for w in why] == ["Carry 1", "Carry 2", "Carry 3", "Carry 6"], (ops, why))
+    check("a dismissed op's reason survives roster_queue's grammar whole, its '#' inside quotes",
+          rq.parse_line(ops[0] + f"  # postmerge {m3470}") == ("mark-carry", "G", "", ["--match", "plain", "dismissed",
+                                                                                       "superseded by #12"]),
+          rq.parse_line(ops[0]))
+    with tempfile.TemporaryDirectory() as st:
+        code, lines, _ = go({"roster_sync.py": 1}, state=st, body=body3470,
+                            ros={"groups": [{**r3470["groups"][0], "group": "R10-X", "resume": {"branch": "fix/r10-x"}}]})
+        got = (Path(st) / QUEUE).read_text().splitlines()
+        check("the marks queue before the stage op, all in one append, each ending the merge's tag",
+              [g.split()[0] for g in got] == ["mark-carry", "mark-carry", "set-stage"]
+              and all(g.endswith(f"  # postmerge {full}") for g in got)
+              and sum(l.startswith("mark QUEUED ") for l in lines) == 2, (got, lines))
+    code, lines, _ = go(body="- Carry 1: built here (NOPE)\n")
+    check("an unkeyed body line is owed as `OWED mark:` and the run exits non-zero",
+          code == 1 and any(l.startswith("OWED mark: Carry 1:") for l in lines), lines)
     code, lines, log = go({"classify": 3})
     check("main WAIT (checks still running) is printed, not owed", code == 0 and
           any(l.startswith("main ") for l in lines) and not any(l.startswith("OWED") for l in lines), lines)
@@ -220,6 +435,24 @@ def self_test() -> int:
           handed(owner) == [], handed(owner))
     check("a contract handing an agent `roster_sync.py --apply` is caught (null control)",
           handed(owner + "\n- After each merge: run `roster_sync.py --apply`.") == ["roster_sync.py"])
+    if mutants:
+        src = Path(__file__).read_text()
+        code_part, sep, table = src.partition("\n#: (site, replacement")  # sites are counted in the code, not this table
+        for name, (old, new, case) in MUTANTS.items():
+            n[0] += 1
+            if old and code_part.count(old) != 1:
+                check(f"mutant {name}: its site appears once", False, code_part.count(old))
+                continue
+            with tempfile.TemporaryDirectory() as td:
+                mp = Path(td) / "postmerge.py"
+                mp.write_text(code_part.replace(old, new) + sep + table)
+                r = subprocess.run([sys.executable, str(mp), "--self-test", "--no-mutants"],  # not -I: PYTHONPATH finds the seat modules
+                                   capture_output=True, text=True, cwd=str(ROOT),
+                                   env={**os.environ, "PYTHONPATH": str(SEAT)})
+            killed = f"FAIL {case}" in r.stdout if case else ("0 failed" in r.stdout and "FAIL" not in r.stdout)
+            print(f"  {'ok  ' if killed else 'FAIL'} mutant {name} " + (f"killed by: {case}" if case else "passes whole"), flush=True)
+            if not killed:
+                fails.append(f"mutant {name}")
     print(f"postmerge self-test: {n[0]} checks, {len(fails)} failed")
     return 1 if fails else 0
 
diff --git a/tools/audit/seat/record_beat.py b/tools/audit/seat/record_beat.py
index e05a848150..a2d2c447f7 100644
--- a/tools/audit/seat/record_beat.py
+++ b/tools/audit/seat/record_beat.py
@@ -85,9 +85,9 @@ def load_roster(run=sh) -> "dict | None":
 
 
 def facts(pr: int, repo: str, run=sh) -> dict:
-    """{sha, branch, issues} of a MERGED pull request, the sha full and from git."""
+    """{sha, branch, issues, body} of a MERGED pull request, the sha full and from git."""
     code, o = run(["gh", "pr", "view", str(pr), "--repo", repo, "--json",
-                   "state,mergeCommit,headRefName,closingIssuesReferences"])
+                   "state,mergeCommit,headRefName,closingIssuesReferences,body"])
     try:
         d = json.loads(o) if code == 0 else None
     except ValueError:
@@ -106,7 +106,7 @@ def facts(pr: int, repo: str, run=sh) -> dict:
     if code != 0 or not SHA.match(full):
         raise Owed(f"#{pr}'s merge commit {oid[:12]} does not resolve to a full sha in git")
     issues = sorted(n["number"] for n in d.get("closingIssuesReferences") or ())
-    return {"sha": full, "branch": d.get("headRefName") or "", "issues": issues}
+    return {"sha": full, "branch": d.get("headRefName") or "", "issues": issues, "body": d.get("body") or ""}
 
 
 def render(pr: int, sha: str, group: str, issues: list) -> str:
@@ -199,7 +199,8 @@ def self_test() -> int:
             if argv[:3] == ["gh", "pr", "view"]:
                 return 0, json.dumps({"state": state, "mergeCommit": {"oid": oid},
                                       "headRefName": "fix/r9-fr-1",
-                                      "closingIssuesReferences": [{"number": 9}, {"number": 3}]})
+                                      "closingIssuesReferences": [{"number": 9}, {"number": 3}],
+                                      **({"body": "the merged body"} if "body" in argv[-1].split(",") else {})})
             if "rev-parse" in j:
                 return (0, full + "\n") if resolves else (1, "")
             if "gh_comment.py" in j:
@@ -212,6 +213,8 @@ def self_test() -> int:
         f = facts(7, DEFAULT_REPO, run)
         check("the merge sha is the full 40 characters, resolved by git", f["sha"] == full, f)
         check("issues closed by the merge are sorted", f["issues"] == [3, 9], f)
+        check("the merged body is asked of gh and returned (postmerge derives its marks from it)",
+              f.get("body") == "the merged body", f)
         lines = []
         text = record(7, DEFAULT_REPO, Path(td), f, "R9-FR-1", True, run, lines.append)
         check("the dry run prints the exact comment", lines[0] == "DRY-RUN comment: " + text.rstrip("\n")
diff --git a/tools/audit/seat/roster_lib.py b/tools/audit/seat/roster_lib.py
index c7b02453a2..b7181a3a57 100644
--- a/tools/audit/seat/roster_lib.py
+++ b/tools/audit/seat/roster_lib.py
@@ -198,6 +198,31 @@ def roster_round(path: str) -> int:
     return int(m.group(1))
 
 
+_GROUP_ROUND = re.compile(r"\AR(\d+)-")
+
+
+def group_round(name: str) -> int | None:
+    """The round a group id names (`R11-PRE-X` -> 11); None for an id with no
+    round prefix. The one rule by which a group belongs to a round's plan."""
+    m = _GROUP_ROUND.match(name)
+    return int(m.group(1)) if m else None
+
+
+def next_round_groups(roster: dict, round_n: int) -> dict:
+    """{id: entry} of the groups that belong to a round after `round_n`: its
+    pre-finder groups, its intake group, the groups deferred to it. A plan of
+    round `round_n` neither draws nor counts them (owner, 2026-11-13)."""
+    return {n: g for n, g in groups_of(roster).items()
+            if (r := group_round(n)) is not None and r > round_n}
+
+
+def round_roster(roster: dict, round_n: int) -> dict:
+    """`roster` without the groups of a round after `round_n`."""
+    later = next_round_groups(roster, round_n)
+    return {**roster, "groups": [g for g in roster.get("groups", [])
+                                 if g["group"] not in later]}
+
+
 def newest_roster(names) -> str | None:
     """Of the paths or basenames given, the roster with the highest round, as
     a `ROSTERS_DIR` path; None when none of them is a roster."""
@@ -712,8 +737,14 @@ def one_line_brief(group: dict, limit: int = 160) -> str:
     """
     text = (group.get("brief") or "").strip()
     # A brief written as a markdown document opens with a heading marker; the
-    # row is plain text, so the marker goes and the lines join.
-    text = re.sub(r"\A\s*#{1,6}[ \t]*", "", text)
+    # row is plain text, so the marker goes, and the heading line is the
+    # description: its next lines are the body, which joined on would run the
+    # title into the first loose line.
+    if re.match(r"\s*#{1,6}[ \t]", text):
+        text = re.sub(r"\A\s*#{1,6}[ \t]*", "", text).split("\n", 1)[0]
+    # An opening list marker ("1. ", "2) ", "- ") is not a sentence end: left
+    # in, the cut below ends the description at the marker.
+    text = re.sub(r"\A\s*(?:\d+[.)]|[-*])[ \t]+", "", text)
     text = re.sub(r"\s*\n\s*", " ", text)
     text = _ATTRIBUTION.sub("", text)
     cut = re.split(r"(?<=\.)\s", text, maxsplit=1)[0]
@@ -1102,6 +1133,41 @@ def critical_path_groups(repo: str, ref: str) -> set[str] | None:
     return groups or None
 
 
+# ------------------------------------------------------------- the writer lease
+#
+# ROSTER-PUSH-LEASE (triage s6-batch233 P706): the beat's roster drain and an
+# out-of-queue writer (carry_fold.py) both push the round's roster branch through
+# `roster_edit.py --push`, each re-applying across a lint window, and with no
+# shared lock each lost the other's races (a fold lost 3 of 3 tries against a
+# 21-op drain). One flock in the beat's state directory makes one writer of
+# record: the drain takes it per op without waiting and yields the rest of its
+# pass while it is held; carry_fold waits for it. flock is released when the
+# holder's process ends, so a killed holder leaves no stale lease.
+WRITER_LEASE = "roster-writer.lease"
+
+
+def writer_lease(state_dir, wait_s: float, sleep=None, clock=None):
+    """An fd holding the exclusive flock on `<state_dir>/roster-writer.lease`,
+    or None when another holder kept it for `wait_s` seconds; `os.close(fd)`
+    releases it."""
+    import fcntl
+    import os
+    import time
+    sleep, clock = sleep or time.sleep, clock or time.monotonic
+    Path(state_dir).mkdir(parents=True, exist_ok=True)
+    fd = os.open(Path(state_dir) / WRITER_LEASE, os.O_RDWR | os.O_CREAT, 0o644)
+    end = clock() + wait_s
+    while True:
+        try:
+            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
+            return fd
+        except BlockingIOError:
+            if clock() >= end:
+                os.close(fd)
+                return None
+            sleep(1)
+
+
 # ------------------------------------------------------------------ self-test
 def _self_test() -> int:
     """Which roster, offline in a throwaway repository: the newest of two
@@ -1602,6 +1668,18 @@ def _self_test() -> int:
         check("an override behind an unreadable tree refuses with git's read, "
               "not 'is not a file'",
               "cannot read" in why and "is not a file" not in why, why)
+    import os
+    with tempfile.TemporaryDirectory() as st:
+        held = writer_lease(st, 0)
+        other = writer_lease(st, 0)
+        waits = []
+        late = writer_lease(st, 3, sleep=waits.append, clock=lambda t=iter(range(0, 99)): next(t))
+        check("writer_lease: a held lease refuses a second holder, at once or after its wait",
+              held is not None and other is None and late is None and waits == [1, 1], (other, late, waits))
+        os.close(held)
+        again = writer_lease(st, 0)
+        check("writer_lease: a released lease is taken (null control)", again is not None, again)
+        os.close(again)
     # gates_finders (R11-PRE-ROUND-CHECK-GATE part 2, tvofi 2026-11-15): every
     # open group the finders do not wait for is the architect's input when they
     # finish; an unmarked one is listed and flagged, never read as gating.
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 01ad1ea8b9..a84b69a073 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -35,6 +35,8 @@ rendered text that no overlay value supplied.
 | `plan_slots` | `replan.py --slots`: concurrent fixer slots the plan schedules (10 unless the owner set another) |
 | `plan_seats` | `replan.py --seats`: seats the plan may use (99 unless the owner set another) |
 | `plan_coordinator_cap` | `replan.py --coordinator-cap`: the plan's coordinator cap (replan's own default when absent) |
+| `plan_live_refs` | `replan.py --live-refs`: a saved `git ls-remote --heads` listing, so the plan prices a group with a fixer, handoff or dispatch ref as working and not by its stage word (absent: the stage word) |
+| `plan_in_flight` | `replan.py --in-flight`: a JSON list of open pull requests (`number`, `headRefOid`, `headRefName`, `isDraft`), the other half of that evidence (absent: the stage word) |
 | `plan_json` | the plan JSON `replan.py --out` writes and `state_docs.py --plan` draws |
 | `plan_page` | the plan page, `PLAN.html` in the state mirror (`state_docs.py --plan` writes it), republished at the same path |
 | `state_mirror` | the directory `state_docs.py --mirror` writes |
@@ -72,7 +74,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4) After each merge (`dev/governance/roles/standing-merge.md`: `tools/audit/seat/postmerge.py` runs after each merge and prints what is still `OWED`): read the merge seat's `merged` report and its read-back of the issues the merge closed (`dev/governance/roles/orchestrator.md` section 4), queue `set-stage` for a roster group to the `roster-drain` row, make one #3394 comment through `tools/pr/gh_comment.py` with its read-back, and remove the finished seat's worktrees under {{seat_root}} and its scratch; the `disk` row (step 8) runs `worktree_gc.sh`.
 
-(4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.
+(4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}` (plus `--live-refs {{plan_live_refs}} --in-flight {{plan_in_flight}}` when the overlay names those files, so a group with a fixer ref or an open pull request is priced as working, not by its stage word), then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.
 
 (4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `cp-owed` row (`tools/audit/seat/owed_watch.py`, reading {{fire_ledger}}) prints a `CP-OWED <arm> <subject>` line for each step of a critical-path or outside group, or of its pull request, past its grace: act on each this sweep, critical path and outside first (owner directive, tvofi 2026-11-09: never let the critical path or outside pull requests slip). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.
 
diff --git a/tools/plan/replan.py b/tools/plan/replan.py
index 0b41437fa2..fce466147e 100644
--- a/tools/plan/replan.py
+++ b/tools/plan/replan.py
@@ -585,12 +585,14 @@ def group_hours(group: dict, durations: dict, is_live: bool, where: str,
     return hours, why
 
 
-#: The measured fields (`tools/plan/size_durations.py`) a plan records and
-#: `--check` requires: the rounds model and the held-stage model.
+#: The fields of `durations.json` a plan records in `generated.model`: the
+#: measured rounds and held-stage models (`tools/plan/size_durations.py`;
+#: `model_refusals` names the ones `--check` requires) and `phase_hours`, the
+#: round phases' durations the plan page prints (`plan_phases.MODEL_TIMED`).
 MODEL_FIELDS = ("first_round_hours", "first_round_by_class_hours", "review_rounds",
                 "review_rounds_by_class", "round_hours", "carry_baseline", "carry_hours",
                 "carry_part_hours", "carries_per_part", "sizes_percentile",
-                "carry_provenance")
+                "carry_provenance", "phase_hours")
 SIZE_ORDER = ("XS", "S", "M", "L", "XL")
 
 
@@ -1587,6 +1589,58 @@ def build_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
     return plan
 
 
+def build_round_plan(roster: dict, durations: dict, caps: dict, start: dt.datetime,
+                     version: str, roster_ref: str = "", roster_blob: str = "",
+                     roster_path: str = "", *, round_n: int, since_tag: list | None = None,
+                     evidence: dict | None = None, legacy: dict | None = None) -> dict:
+    """`build_plan` over the groups of round `round_n` only, plus the next
+    round's preliminary plan under `next_round` when the roster holds its
+    groups. A round's plan, closure and lanes cover that round's groups
+    (owner, 2026-11-13); a group of a later round is priced apart, from this
+    round's closure. A group of this round cannot wait on one of a later
+    round. `build_plan` itself plans every group it is given."""
+    later = roster_lib.next_round_groups(roster, round_n)
+    if not later:
+        return build_plan(roster, durations, caps, start, version, roster_ref, roster_blob,
+                          roster_path, round_n=round_n, since_tag=since_tag,
+                          evidence=evidence, legacy=legacy)
+    for n, g in groups_of(roster).items():
+        a = next((a for a in g.get("after") or [] if a in later), None)
+        if n not in later and a:
+            raise PlanError(f"{n}: after-edge names a group of a later round: {a}")
+    plan = build_plan(roster_lib.round_roster(roster, round_n), durations, caps, start, version,
+                      roster_ref, roster_blob, roster_path, round_n=round_n,
+                      since_tag=since_tag, evidence=evidence, legacy=legacy)
+    plan["next_round"] = next_round_preview(later, durations, caps, plan, roster_ref,
+                                            roster_blob, roster_path, evidence, legacy)
+    return plan
+
+
+def next_round_preview(later: dict, durations: dict, caps: dict,
+                       plan: dict, roster_ref: str, roster_blob: str, roster_path: str,
+                       evidence: dict | None, legacy: dict | None) -> dict:
+    """The next round's preliminary plan: its groups on the same duration model
+    and caps, starting at `plan`'s closure. Only the nearest later round is
+    scheduled; groups of rounds past it are counted in `beyond`. An
+    `after`-edge to a group of an earlier round is dropped: that round is
+    closed by the time this one starts. A round that cannot be planned is
+    `{"unavailable": reason}`, never an absent tab."""
+    nxt = min(roster_lib.group_round(n) for n in later)
+    mine = {n: g for n, g in later.items() if roster_lib.group_round(n) == nxt}
+    out = {"round": nxt, "preliminary": True, "starts_at": plan["summary"]["closure"],
+           "beyond": len(later) - len(mine)}
+    sub = {"groups": [{**g, "after": [a for a in g.get("after") or [] if a in mine]}
+                      for g in mine.values()]}
+    at = dt.datetime.strptime(plan["summary"]["closure"], "%Y-%m-%dT%H:%M:%SZ")
+    try:
+        out["plan"] = build_plan(sub, durations, caps, at, plan["summary"]["closure_stamp"],
+                                 roster_ref, roster_blob, roster_path, round_n=nxt,
+                                 evidence=evidence, legacy=legacy)
+    except PlanError as exc:
+        out["unavailable"] = str(exc)
+    return out
+
+
 def bump(version: str, n: int) -> str:
     """The `n`th interim patch stamp after `version`."""
     maj, mi, pa = (int(x) for x in version.lstrip("v").split(".")[:3])
@@ -1845,6 +1899,9 @@ def check_plan(plan: dict) -> list:
         bad += model_refusals(plan["generated"]["model"])
     else:
         bad.append("model: the plan records no duration model (generated.model)")
+    nxt = (plan.get("next_round") or {}).get("plan")
+    if nxt:
+        bad += [f"next round {plan['next_round']['round']}: {b}" for b in check_plan(nxt)]
     return bad
 
 
@@ -3462,9 +3519,9 @@ def main(argv=None) -> int:
             args.repo, f"{roster_lib.ROSTERS_DIR}/{src.rsplit('/', 1)[-1]}")
     except roster_lib.RosterNotFound as exc:
         raise PlanError(f"the carry cut-over: {exc}") from exc
-    plan = build_plan(roster, durations, caps, start, version, ref, blob,
-                      roster_path=src, round_n=round_n, since_tag=since_tag, evidence=evidence,
-                      legacy=legacy)
+    plan = build_round_plan(roster, durations, caps, start, version, ref, blob,
+                            roster_path=src, round_n=round_n, since_tag=since_tag,
+                            evidence=evidence, legacy=legacy)
     bad = check_plan(plan)
     if bad:
         print("the model produced a violating plan; refusing to write it", file=sys.stderr)
diff --git a/tools/policy/check-wave-script.mjs b/tools/policy/check-wave-script.mjs
index 3657c9bc61..5012c5f108 100644
--- a/tools/policy/check-wave-script.mjs
+++ b/tools/policy/check-wave-script.mjs
@@ -1662,19 +1662,19 @@ await block('the P3 plan workflow', async () => {
   // to the base's copy in CI) passes both before and after that refusal lands.
   const OPEN = { open: { open_cards: ['E11-X'], open_groups: ['R11-G'], unmarked: [] }, open_rc: 0 }
   const MOVES = (extra = {}) => ({ groups: [{ group: 'A', findings: ['D7-s1-01'], open_items: ['E11-X'] }], moves: [{ group: 'A', adr: 'ADR-1', metrics: {}, dS: 0 }],
-    dropped: [{ id: 'R11-G', reason: 'merged while the finders ran' }], projected_dS: 23, critical_chain: ['A'], depth: 1, hours: 8, risks: [], ...extra })
+    dropped: [{ id: 'R11-G', reason: 'merged while the finders ran' }], projected_dS: 23, objective: { groups: { A: { rank: 1, removes: ['D7-s1-01'] } } }, critical_chain: ['A'], depth: 1, hours: 8, risks: [], ...extra })
   const drive = async (over = {}) => {
     const calls = []
     let cur = over.publish?.sha ?? SHA('b')
     let rev = 0
     const agent = async (prompt, o) => {
-      calls.push({ label: o.label, prompt })
+      calls.push({ label: o.label, prompt, schema: o.schema })
       const label = o.label
       if (label === 'plan/read') return over.read ?? { groups: [G('A')], findings: [FIND('D7-s1-01')], holdouts_path: 'h.json', ...OPEN }
       if (label === 'plan/architect') return over.architect ?? { components: ['coordinator'], scenarios: [{ quality: 'q', scenario: 's' }], triage: (over.read?.findings ?? [FIND('D7-s1-01')]).map((f) => ({ id: f.id, verdict: 'keep' })) }
       if (label === 'plan/moves') return over.moves ?? MOVES()
       if (label === 'plan/write') return over.write ?? { brief_lint_rc: 0 }
-      if (label === 'plan/publish') return over.publish ?? { sha: cur, pushed: true }
+      if (label === 'plan/publish') return over.publish ?? { sha: cur, objective_rc: 0, pushed: true }
       if (/^plan\/review-/.test(label)) {
         const r = over.reviewImpl ? over.reviewImpl(label, cur) : null
         return r ?? { verdict: 'approve', sha: cur, points: [] }
@@ -1708,7 +1708,13 @@ await block('the P3 plan workflow', async () => {
   await pthrows('a group with no move entry stops P3', /no move entry/,
     { moves: { groups: [{ group: 'A' }, { group: 'B' }], moves: [{ group: 'A', metrics: {} }], projected_dS: 23 } })
   await pthrows('a publish that is not a 40-hex commit stops P3', /not a 40-hex commit/,
-    { publish: { sha: 'abc', pushed: true } })
+    { publish: { sha: 'abc', objective_rc: 0, pushed: true } })
+  // R11-ARCH-OBJECTIVE: decision 0018's check gates the publish; its twin is
+  // the approved run below, whose publish reports rc 0.
+  await pthrows('a plan the objective check refuses is not published (P3 stops)', /objective check refused the plan \(rc=1\)/,
+    { publish: { sha: SHA('b'), objective_rc: 1, objective_fails: ['RANK edge A after B'], pushed: false } })
+  // An absent objective_rc is refused by the publish schema's `required`
+  // (the runtime validates it); this pins that the schema carries it.
   await pthrows('a reviewer answering for another tree stops P3', /answered for/,
     { reviewImpl: () => ({ verdict: 'approve', sha: SHA('c'), points: [] }) })
   await pthrows('a recorded verdict that is not a 40-hex commit stops P3', /not a 40-hex commit/,
@@ -1725,7 +1731,20 @@ await block('the P3 plan workflow', async () => {
   const read = ok.calls.find((c) => c.label === 'plan/read')?.prompt ?? ''
   t('the read step is pointed at the audit-verify draft and measures the fork holdouts',
     read.includes('wave-r11-groups.json') && read.includes('plan_audit.py snapshot --ref deadbeefcafe'))
+  const movesP = ok.calls.find((c) => c.label === 'plan/moves')?.prompt ?? ''
+  const publishP = ok.calls.find((c) => c.label === 'plan/publish')?.prompt ?? ''
+  t('the architect returns the objective block and the publish runs objective-check before the push (R11-ARCH-OBJECTIVE)',
+    /objective block/.test(movesP) && /no hour, chain or date/.test(movesP)
+    && publishP.indexOf('plan_audit.py objective-check') >= 0
+    && publishP.indexOf('plan_audit.py objective-check') < publishP.indexOf('git push origin HEAD:refs/heads/plan/r11'), publishP.slice(0, 200))
+  t('and the PLAN.json written carries the block the architect returned',
+    (ok.calls.find((c) => c.label === 'plan/write')?.prompt ?? '').includes('"removes": [\n     "D7-s1-01"'))
+  t('and the publish schema requires objective_rc, so a publish that reports no check is refused',
+    (ok.calls.find((c) => c.label === 'plan/publish')?.schema?.required ?? []).includes('objective_rc'))
+  t('and the moves schema requires the objective block, so a reply without one is refused',
+    (ok.calls.find((c) => c.label === 'plan/moves')?.schema?.required ?? []).includes('objective'))
   const review1 = ok.calls.find((c) => c.label === 'plan/review-1')?.prompt ?? ''
+  t('the reviewer re-runs objective-check at the plan SHA', review1.includes('objective-check --ref ' + SHA('b')))
   t('the reviewer is pointed at the published plan ref and its SHA',
     review1.includes('plan/r11 = ' + SHA('b')) && /plan-review\.md/.test(review1))
   const verdict = ok.calls.find((c) => c.label === 'plan/verdict')?.prompt ?? ''
diff --git a/tools/site/build_docs.mjs b/tools/site/build_docs.mjs
index 0fbd7f1e42..f38826355f 100644
--- a/tools/site/build_docs.mjs
+++ b/tools/site/build_docs.mjs
@@ -35,6 +35,9 @@ const BLOB = 'https://github.com/tvofi/heatpump_optimizer/blob/main/'
 const TREEURL = 'https://github.com/tvofi/heatpump_optimizer/tree/main/'
 // Rows of the README Documentation table the site links to GitHub instead of rendering, each with its reason.
 const EXCLUDE = {}
+// Documents that moved: the old page name keeps resolving, as a redirect to the new page with the fragment kept, so a
+// link to the old address still lands (docs/ecl110.md became docs/heat-curve.md; the old file stays as a pointer).
+const MOVED = { 'docs/ecl110.md': 'docs/heat-curve.md' }
 const errors = []
 const stats = { pages: 0, pageLinks: 0, anchors: 0, githubLinks: 0, images: 0, badges: 0, external: 0, mermaid: 0 }
 
@@ -244,8 +247,25 @@ ${mermaidJs(r.mermaid)}
   fs.writeFileSync(path.join(OUT, r.out), page)
 })
 stats.pages = rendered.length
+stats.redirects = 0
+const redirects = []
+for (const [from, to] of Object.entries(MOVED)) {
+  const target = PUBLISHED.get(to), old = outName(from)
+  // A tree without the old file has nothing to redirect (tests/doc_claims.py pins that this one keeps it).
+  if (!TREE.has(from)) continue
+  if (!target) { errors.push(`MOVED names ${to}, which is not a built page`); continue }
+  if ([...PUBLISHED.values()].includes(old)) { errors.push(`MOVED ${from}: ${old} is also a built page`); continue }
+  fs.writeFileSync(path.join(OUT, old), `<!doctype html>
+<html lang="en"><head><meta charset="utf-8"><title>Moved</title>
+<meta http-equiv="refresh" content="0; url=${esc(target)}"><link rel="canonical" href="${esc(target)}">
+<script>location.replace(${JSON.stringify(target)} + location.hash)</script></head>
+<body><p>This page moved to <a href="${esc(target)}">${esc(target)}</a>.</p></body></html>
+`)
+  redirects.push({ src: from, out: old, to: target })
+  stats.redirects++
+}
 if (!rendered.length) errors.push('ANCHOR: zero pages built')
-fs.writeFileSync(path.join(OUT, 'docs-manifest.json'), JSON.stringify({ built: rendered.map((r) => ({ src: r.src, out: r.out, mermaid: r.mermaid })), excluded: EXCLUDE }, null, 1))
+fs.writeFileSync(path.join(OUT, 'docs-manifest.json'), JSON.stringify({ built: rendered.map((r) => ({ src: r.src, out: r.out, mermaid: r.mermaid })), excluded: EXCLUDE, moved: redirects }, null, 1))
 console.log(Object.entries(stats).map(([k, v]) => `${k} ${v}`).join(', '))
 console.log(`built ${rendered.length} page(s): ${rendered.map((r) => r.out).join(', ')}; excluded ${Object.keys(EXCLUDE).join(', ') || 'none'}`)
 for (const e of errors) console.log('FAIL', e)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
