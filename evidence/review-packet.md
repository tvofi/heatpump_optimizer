# Review packet #3532
head: 32c768ae03ddbed07c5f4975f458930a1054e35e
base: 9fdba3b8547f9762438dc19b98b310a63d34dcb1

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
arch-score / arch-score id=132558683100 success
budget-raise-gate / budget-raise-gate id=132558712766 success
cancel-superseded id=132558697254 success
codeql id=132558698571 skipped
codeql / Analyze (actions) id=132558638126 success
codeql / Analyze (javascript-typescript) id=132558638562 success
codeql / Analyze (python) id=132558638595 success
gate id=132558683183 success
governance id=132558711351 skipped
governance / delivery-status id=132558639228 success
governance / delivery-status-publish id=132558638807 skipped
governance / env-matrix id=132558638642 success
governance / instrument-self-tests id=132558638552 success
governance / policy-docs id=132558638533 success
governance / record id=132558667138 skipped
governance / wave-script id=132558638637 success
hassfest id=132558709789 skipped
hassfest / hassfest id=132558674549 success
kernel-points id=132558710654 skipped
pr-contract id=132558654521 skipped
pr-contract / pr-contract id=132558684111 success
prelude id=132558702380 success
refresh id=132558721542 success
sweep-self id=132558977384 skipped
tests id=132558693311 skipped
tests / arch-instrument id=132558639724 success
tests / briefs id=132558638498 success
tests / browser id=132558639750 success
tests / ci-ratchet id=132558640465 skipped
tests / claims-autofix id=132558639567 skipped
tests / closure-scope id=132558638578 success
tests / closures id=132558639757 success
tests / closures-autofix id=132558639695 skipped
tests / coverage id=132558639713 success
tests / coverage-ratchet id=132558639769 success
tests / fast (3.14) id=132558639813 success
tests / graders-head-copy id=132558639480 success
tests / lane-proofs id=132558640193 success
tests / mutation id=132558638628 success
tests / mutation-autofix id=132558640180 skipped
tests / mutation-pins id=132558639729 skipped
tests / nightly-ha id=132558639774 skipped
tests / nightly-status id=132558638421 failure
tests / replay id=132558639814 success
tests / typing id=132558639515 success
validate id=132558701683 skipped
validate / validate-hacs id=132558675637 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 27 script(s) run, 6 scoped out.
             no segment of this names a program this check knows
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=237fad44 ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/optimality.py
             `tests/optimality.py` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh
             `tools/pr/prepr.sh` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_section.py
             `dev/audit/harnesses/r10_duty_switch_section.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)
             `tools/audit/archscore/score.py` is in the tree at this head

FIGURES: 10 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8c5f2676.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8c5f2676.json
new file mode 100644
index 0000000000..a486ec72f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8c5f2676.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs CMP_BOUND 8c5f2676",
+  "killed_by": "tests/features.py",
+  "old": "    if extra is not None and next_duty in (second, \"both\") and step_minutes - first_min < SPLIT_MIN_MINUTES + extra:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if extra is not None and next_duty in (second, \"both\") and step_minutes - first_min <= SPLIT_MIN_MINUTES + extra:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8c5f2676.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8c5f2676.json
new file mode 100644
index 0000000000..6c867a0e65
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8c5f2676.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs GUARD_OFF 8c5f2676",
+  "killed_by": "tests/features.py",
+  "old": "    if extra is not None and next_duty in (second, \"both\") and step_minutes - first_min < SPLIT_MIN_MINUTES + extra:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.a22518ce.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json
rename to tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.a22518ce.json
index fa73675963..a4d13d0d1c 100644
--- a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.a22518ce.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs RETURN_DEL 123675c1",
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs RETURN_DEL a22518ce",
   "killed_by": "tests/features.py",
-  "old": "    return ((\"dhw\", dhw_min), (\"space\", step_minutes - dhw_min))",
+  "old": "    return ((first, first_min), (second, step_minutes - first_min))",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.3ab3f318.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.3ab3f318.json
new file mode 100644
index 0000000000..4ecc5f9a4c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.3ab3f318.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends CMP_BOUND 3ab3f318",
+  "killed_by": "tests/features.py",
+  "old": "        whole = split & next_second & (second_min < SPLIT_MIN_MINUTES + extra)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`whole = split & next_second & (second_min <= SPLIT_MIN_MINUTES + extra)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.GUARD_OFF.fe24fd6b.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.GUARD_OFF.fe24fd6b.json
new file mode 100644
index 0000000000..55c4842343
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.GUARD_OFF.fe24fd6b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends GUARD_OFF fe24fd6b",
+  "killed_by": "tests/features.py",
+  "old": "    if extra is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.4932ea42.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json
rename to tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.4932ea42.json
index cac585d618..7652f8a015 100644
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.4932ea42.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends RETURN_DEL 6b97afd0",
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends RETURN_DEL 4932ea42",
   "killed_by": "tests/features.py",
-  "old": "    return np.where(two, DHW, single), np.where(two, SPACE, single), two",
+  "old": "    return np.where(two, lead, single), np.where(two, trail, single), two",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json
new file mode 100644
index 0000000000..397987d0cd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule BOOLOP ac335b68",
+  "killed_by": "tests/features.py",
+  "old": "    first = \"space\" if stop_probability[0] > 0 and not stop_probability[1] > 0 else \"dhw\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`first = \"space\" if stop_probability[0] > 0 or not stop_probability[1] > 0 else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json
new file mode 100644
index 0000000000..d8859abaa7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND 726b5c41",
+  "killed_by": "tests/features.py",
+  "old": "    return first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return first, (off_seconds[into] / 60.0 if stop_probability[into] >= 0 else None)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json
new file mode 100644
index 0000000000..be3c6d34a4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND ac335b68",
+  "killed_by": "tests/features.py",
+  "old": "    first = \"space\" if stop_probability[0] > 0 and not stop_probability[1] > 0 else \"dhw\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`first = \"space\" if stop_probability[0] >= 0 and not stop_probability[1] > 0 else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=21. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json
new file mode 100644
index 0000000000..1f336579bc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule RETURN_DEL 726b5c41",
+  "killed_by": "tests/features.py",
+  "old": "    return first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.f22b5492.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.f22b5492.json
new file mode 100644
index 0000000000..2b6a8831b6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.f22b5492.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban GUARD_OFF f22b5492",
+  "killed_by": "tests/features.py",
+  "old": "        if rule[0] == \"dhw\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.CLAMP_DROP.12d1bbb1.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.CLAMP_DROP.12d1bbb1.json
new file mode 100644
index 0000000000..df1c8e705b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.CLAMP_DROP.12d1bbb1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.book CLAMP_DROP 12d1bbb1",
+  "killed_by": "tests/features.py",
+  "old": "        scale = min(1.0, N_CAP / self.n)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`scale = (1.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json
new file mode 100644
index 0000000000..ecad4e45f0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.split RETURN_DEL e5fbd410",
+  "killed_by": "tests/features.py",
+  "old": "        return duty_legs.leg_rule(*self.planner_pairs())",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.CMP_BOUND.5bea58be.json b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.CMP_BOUND.5bea58be.json
new file mode 100644
index 0000000000..74e43e4a49
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.CMP_BOUND.5bea58be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:both_step_duty CMP_BOUND 5bea58be",
+  "killed_by": "tests/features.py",
+  "old": "    return legs[0][0] if now - start < timedelta(minutes=legs[0][1]) else legs[-1][0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return legs[0][0] if now - start <= timedelta(minutes=legs[0][1]) else legs[-1][0]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.GUARD_OFF.560bc44e.json b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.GUARD_OFF.560bc44e.json
new file mode 100644
index 0000000000..7daa2286d9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.GUARD_OFF.560bc44e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:both_step_duty GUARD_OFF 560bc44e",
+  "killed_by": "tests/features.py",
+  "old": "        if rec.order is None or rec.order[0] != start:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.GUARD_OFF.fa002675.json
similarity index 71%
rename from tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json
rename to tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.GUARD_OFF.fa002675.json
index a620063d0e..5a625d6948 100644
--- a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.GUARD_OFF.fa002675.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.book GUARD_OFF 3e106b06",
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:both_step_duty GUARD_OFF fa002675",
   "killed_by": "tests/features.py",
-  "old": "        if self.n > N_CAP:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+  "old": "    if rec.loaded:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.RETURN_DEL.5bea58be.json b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.RETURN_DEL.5bea58be.json
new file mode 100644
index 0000000000..84168efae5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/both_step_duty.RETURN_DEL.5bea58be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:both_step_duty RETURN_DEL 5bea58be",
+  "killed_by": "tests/features.py",
+  "old": "    return legs[0][0] if now - start < timedelta(minutes=legs[0][1]) else legs[-1][0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.c672264a.json
similarity index 55%
rename from tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.c672264a.json
index 6cf8195176..e90404081f 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.c672264a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 95d10ca9",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND c672264a",
   "killed_by": "tests/features.py",
-  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor, _leg_rule(opt)) > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor, _leg_rule(opt)) >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json
deleted file mode 100644
index e5059f5c83..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 95d10ca9",
-  "killed_by": "tests/structure.py",
-  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.c672264a.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.c672264a.json
new file mode 100644
index 0000000000..e63c05ae77
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.c672264a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF c672264a",
+  "killed_by": "tests/features.py",
+  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor, _leg_rule(opt)) > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.e8ac8817.json
similarity index 51%
rename from tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.e8ac8817.json
index b8c8493e56..7c0dbab8dd 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.e8ac8817.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability RETURN_DEL 9325b601",
-  "killed_by": "tests/structure.py",
-  "old": "    return duty_legs.availability(space, tank, lost, _duty_floor(opt))",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability RETURN_DEL e8ac8817",
+  "killed_by": "tests/features.py",
+  "old": "    return duty_legs.availability(space, tank, lost, _duty_floor(opt), _leg_rule(opt))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=16."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json
deleted file mode 100644
index ac6a436217..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share CMP_BOUND 3eede229",
-  "killed_by": "tests/features.py",
-  "old": "    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return legs[0][0] if (now - result.timestamps[i]) <= first_ends else legs[-1][0]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json
deleted file mode 100644
index 1af67f301a..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share RETURN_DEL 3eede229",
-  "killed_by": "tests/features.py",
-  "old": "    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
-}
diff --git a/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json b/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json
deleted file mode 100644
index 2f2183aa51..0000000000
--- a/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.book CMP_BOUND 3e106b06",
-  "old": "        if self.n > N_CAP:",
-  "reason": "Equivalent (CMP_BOUND, `self.n > N_CAP` -> `self.n >= N_CAP`). The two differ only at n == N_CAP exactly, where the guarded body computes scale = N_CAP / self.n = 1.0 and multiplies k and kept_w by it: IEEE multiplication by 1.0 returns its operand, so both counts, and the latch read after them, are the same floats on either branch. Measured by the R10-DUTY-SWITCH-PLANNER-PRICE fixer's diff drive (tools/audit/seat/mutant_run.py --diff over the section harness dev/audit/harnesses/r10_duty_switch_price_section.py): SURVIVED, while the same line's GUARD_OFF and the section's cap mutants (no cap, the cap scaling the stops alone, three times the on-threshold) are each killed by the cap checks.",
-  "verdict": "equivalent"
-}


## Review scope: delta (later round over the reviewed head 32c768ae03ddbed07c5f4975f458930a1054e35e)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 32c768ae03ddbed07c5f4975f458930a1054e35e
Fix review: blocked 32c768ae03ddbed07c5f4975f458930a1054e35e root-cause-detectable: pr-contract / pr-contract refuses the body's stale scope-line figure block, and gate is red on it alone; figure_block.py verify shows it locally in seconds

bus-nonce: 76f4ef9ed9970c3189dd63618b7c3934

## Block

- The required check `pr-contract / pr-contract` concluded failure at this head on both runs, job 132550761259 and job 132553014911. The required `gate` (job 132553332629) fails only on it (`FAIL pr-contract / pr-contract: failure (this run)`). `merge_train.py classify 32c768ae… --pr 3532` reads `RED … pending: none red: gate` (rc=1, 19:03:05Z). Both contexts are in the `owed-reds` set. The body's `## Red checks` names neither (it answers only `tests / fast (3.14)` and `tests / mutation`).
- The cause is in the body, not the code. The `## Figures` block `<!-- figure-block: scope-line mb=9fdba3b8… head=32c768ae… -->` holds `MODE: FULL -- every test script runs, nothing is scoped out.`. At this head over that merge base, the registered instrument prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` I reproduced the refusal locally with `python3 -I tools/pr/figure_block.py verify <block> --base 9fdba3b8… --head 32c768ae…` (`1 refused`, ev/figure-block-verify.txt). `figure_block.py refresh` renders the SCOPED line (ev/body-figure-block-refreshed.md).
- A cheaper detector exists: `figure_block.py verify`, run on the body before it is set, costs about 1 s and is the same command CI runs. The body says the orchestrator's script set it without a push. Remedy: refresh the block (`figure_block.py refresh <body>`) and let `pr-contract` re-run. If that red recurs, answer it under `## Red checks`. No code change is owed: the resolution reviewed below is sound.

## Evidence

- Round: a later round (delta scope) over the reviewed head 3ab3d5b5ab (verdict `Fix review: merge 3ab3d5b5ab…`, nonce 6200efa5…). The delta has two merges. 5d630d46bd merges handoff 5e1fac78ad, which is 3ab3d5b5ab plus origin/main 237fad4453. 32c768ae03 then merges origin/main 9fdba3b854.
- Resolution: `git show --remerge-diff` (ev/remerge-*.txt). 5e1fac78ad resolves exactly one key, `options.step.entities.sections.indoor.data_description.space_setpoint_unit`, in strings.json and translations/en, de and sv, each to the 237fad44 (main) side. tests/closures.json was resolved by the LEDGER-MERGE driver, with no marker left. 5d630d46bd and 32c768ae03 have empty remerge diffs, so both merged clean.
- Four files equal main: the blob of each of the four files at the head equals its blob at 237fad4453 and at 9fdba3b854 (ev/four-files.txt). Each file has 1509 leaf keys (ev/key-counts.txt), and strings.json and en.json are the same blob (1dd5049033). This re-derives the body's "1509 keys each" and "strings.json equals en.json".
- Nothing else of the patch changed: the head tree equals `git merge-tree --write-tree 3ab3d5b5ab 9fdba3b854` except in those four files. The only differences there are the 4 marker and losing-side lines per file, 16 deletions in all (ev/tree-oracle.txt). Files that left the three-dot patch (patch-R.diff against patch-H.diff) are the train PRs' content, now on main. The `_share.RETURN_DEL.3eede229` ledger deletion is in both patches.
- No production delta widens scope: the only `custom_components/` change beyond main's own is the four string files, taken from main verbatim.
- VERSION, the manifest version and the notes heading are untouched in `git diff $(merge-base)...HEAD` (CI's version-edit step agrees: "no version edit").
- Merge with main: `git merge-tree --write-tree origin/main 32c768ae…` returned rc=0 at origin/main 5b8f05ba4e (ev/merge-tree.txt).
- CI: ev/classify.log. The poll read WAIT (pending gate) at 19:00:57Z and 19:02:01Z, then RED (red: gate) at 19:03:05Z. Other required contexts are green. `tests / nightly-status` is red but is not in the owed set.
- Previous finding (body duplicated sections): resolved. `## Mutation proof` through `## Unpinned sites` now each appear once.
- carry_audit check: rc 0 over this verdict (ev/carry-audit.txt). The PR body there is a stand-in holding its Forward-carry and Friction "none"; CI's pr-contract run of carry_audit over the live body printed 0 finding items.
- Head re-read before return: refs/heads/fix/r10-duty-switch-restart-learning-pr-b-p2 = 32c768ae03ddbed07c5f4975f458930a1054e35e (ev/head-reread.txt).

## Findings

- The `## Head` section repeats its first paragraph word for word ("`32c768ae…` is this PR's head, unchanged: … main merged cleanly …"). That holds for the last merge of main (9fdba3b8), but 5e1fac78 did conflict, which the next paragraph states. This is a body-text defect from the orchestrator's body script, with no code effect. Carry: dismissed: body text owned by the orchestrator's body script, fixed by the same body refresh the block requires; no code effect

## Delta diff: git diff 32c768ae03ddbed07c5f4975f458930a1054e35e 32c768ae03ddbed07c5f4975f458930a1054e35e

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
