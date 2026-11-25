# Review packet #3877
head: f5744c8cf9d6607b195f45f012132bffec5d43d8
base: 24e3f37620f8f51022a2f9c82f863c7ba28fc6d4

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=138999382068 success
arch-score / arch-score id=139018657057 success
arm id=138998729892 skipped
budget-raise-gate / budget-raise-gate id=139018656589 success
cancel-superseded id=139018720308 success
codeql id=139018656973 skipped
codeql / Analyze (actions) id=138999020576 success
codeql / Analyze (javascript-typescript) id=138999020714 success
codeql / Analyze (python) id=138999020633 success
gate id=139018655319 success
governance id=139018656617 skipped
governance / env-matrix id=138999020627 success
governance / instrument-self-tests id=138999020660 success
governance / policy-docs id=138999020703 success
governance / record id=138999023223 skipped
governance / wave-script id=138999020756 success
hassfest id=139018716140 skipped
hassfest / hassfest id=138999020488 success
kernel-points id=139018656468 skipped
pr-contract id=139018657243 skipped
pr-contract / pr-contract id=139017336744 success
prelude id=139018655539 success
refresh id=139018655998 success
sweep-self id=139018963093 skipped
tests id=139018717945 skipped
tests / arch-instrument id=138999386576 success
tests / briefs id=138999020638 success
tests / browser id=138999386532 success
tests / ci-ratchet id=139015499138 skipped
tests / claims-autofix id=139013186893 skipped
tests / closure-scope id=138999020647 success
tests / closures id=138999386457 success
tests / closures-autofix id=139010953896 skipped
tests / coverage id=138999386398 success
tests / coverage-ratchet id=139015497320 success
tests / fast (3.14) id=138999386463 success
tests / graders-head-copy id=139015497309 success
tests / lane-proofs id=139015497308 success
tests / mutation id=138999020590 success
tests / mutation-autofix id=139017337777 skipped
tests / mutation-pins id=139017336494 skipped
tests / nightly-ha id=138999388558 skipped
tests / nightly-status id=138999020681 failure
tests / replay id=138999386424 success
tests / typing id=138999386388 success
validate id=139018656503 skipped
validate / validate-hacs id=138999020525 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: f5744c8cf9d6607b195f45f012132bffec5d43d8 lacks origin/main dc2b2bab316419ced8f919c256908275a2cc3e25; roster read at origin/main
NOTE body item dcfe9a0e: R11-OUTSIDE-HONEST-DHW-RUNS
NOTE body item f33991cf: dismissed:instrument outside this group's seam, recorded as a proposal for round-end triage
NOTE body item 5d3f59c3: dismissed:instrument outside this group's seam, recorded as a proposal for round-end triage
NOTE body item 95f0486b: dismissed:a run-time cost of the seat's host, no instrument change proposed
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         dev/audit/harnesses/r11_outside_3849_unlatched_price.py
             `dev/audit/harnesses/r11_outside_3849_unlatched_price.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r11_outside_3849_unlatched_price.py
             `dev/audit/harnesses/r11_outside_3849_unlatched_price.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff e3cb5c019b46
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff e3cb5c019b46 --workdir D
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=e3cb5c019b46 ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  ok         python3 tests/comment_ratchet.py
             `tests/comment_ratchet.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head

FIGURES: 10 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.415d247d.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.415d247d.json
new file mode 100644
index 0000000000..d67785e3c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.415d247d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule BOOLOP 415d247d",
+  "killed_by": "tests/features.py",
+  "old": "    stops = [p > 0 and not free for p, free in zip(stop_probability, unlatched)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`stops = [p > 0 or not free for p, free in zip(stop_probability, unlatched)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.9e0433b2.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.9e0433b2.json
new file mode 100644
index 0000000000..6ba0203f26
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.9e0433b2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule BOOLOP 9e0433b2",
+  "killed_by": "tests/features.py",
+  "old": "    first = \"space\" if stops[0] and not stops[1] else \"dhw\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`first = \"space\" if stops[0] or not stops[1] else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=31."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json
deleted file mode 100644
index 397987d0cd..0000000000
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule BOOLOP ac335b68",
-  "killed_by": "tests/features.py",
-  "old": "    first = \"space\" if stop_probability[0] > 0 and not stop_probability[1] > 0 else \"dhw\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`first = \"space\" if stop_probability[0] > 0 or not stop_probability[1] > 0 else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
-}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.415d247d.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.415d247d.json
new file mode 100644
index 0000000000..65397b0edc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.415d247d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND 415d247d",
+  "killed_by": "tests/features.py",
+  "old": "    stops = [p > 0 and not free for p, free in zip(stop_probability, unlatched)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`stops = [p >= 0 and not free for p, free in zip(stop_probability, unlatched)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json
deleted file mode 100644
index d8859abaa7..0000000000
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND 726b5c41",
-  "killed_by": "tests/features.py",
-  "old": "    return first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return first, (off_seconds[into] / 60.0 if stop_probability[into] >= 0 else None)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json
deleted file mode 100644
index be3c6d34a4..0000000000
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND ac335b68",
-  "killed_by": "tests/features.py",
-  "old": "    first = \"space\" if stop_probability[0] > 0 and not stop_probability[1] > 0 else \"dhw\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`first = \"space\" if stop_probability[0] >= 0 and not stop_probability[1] > 0 else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=21. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.3e796948.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json
rename to tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.3e796948.json
index 1f336579bc..76abb6147e 100644
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.3e796948.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule RETURN_DEL 726b5c41",
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule RETURN_DEL 3e796948",
   "killed_by": "tests/features.py",
-  "old": "    return first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)",
+  "old": "    return first, (off_seconds[into] / 60.0 if stops[into] else None)",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.priced.RETURN_DEL.674ac3db.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.priced.RETURN_DEL.674ac3db.json
new file mode 100644
index 0000000000..a4a0bd410f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.priced.RETURN_DEL.674ac3db.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.priced RETURN_DEL 674ac3db",
+  "killed_by": "tests/features.py",
+  "old": "        return self.p if self.usable else self.k / (self.n + PRIOR_N)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.04ef69d7.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
rename to tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.04ef69d7.json
index 5d0d9757be..db2165c4db 100644
--- a/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.04ef69d7.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:planner_fields RETURN_DEL 77cc0eae",
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.planner_pairs RETURN_DEL 04ef69d7",
   "killed_by": "tests/features.py",
-  "old": "    return {\"duty_switch_stop_probability\": stops, \"duty_switch_off_seconds\": off_s}",
+  "old": "        return (ds.priced, sd.priced), (offs[0], offs[1])",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.827431ae.json
similarity index 81%
rename from tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json
rename to tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.827431ae.json
index ecad4e45f0..8cac5217a0 100644
--- a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.827431ae.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.split RETURN_DEL e5fbd410",
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.split RETURN_DEL 827431ae",
   "killed_by": "tests/features.py",
-  "old": "        return duty_legs.leg_rule(*self.planner_pairs())",
+  "old": "        return duty_legs.leg_rule(*self.planner_pairs(), self.unlatched())",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.unlatched.RETURN_DEL.351a4555.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.unlatched.RETURN_DEL.351a4555.json
new file mode 100644
index 0000000000..5a80c44974
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.unlatched.RETURN_DEL.351a4555.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.unlatched RETURN_DEL 351a4555",
+  "killed_by": "tests/features.py",
+  "old": "        return not self.directions[DIRECTIONS[0]].usable, not self.directions[DIRECTIONS[1]].usable",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.c60f412a.json
similarity index 59%
rename from tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
rename to tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.c60f412a.json
index a10a5b3c92..133b5c0dd5 100644
--- a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.c60f412a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.planner_pairs RETURN_DEL fc67f05d",
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:planner_fields RETURN_DEL c60f412a",
   "killed_by": "tests/features.py",
-  "old": "        return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+  "old": "    return (rec.learner if rec is not None else DutySwitchLearner()).config_fields()",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }


## Review scope: full (no verdict on verdict/<pr> names the reviewed head fa76fdc4b0dd857aabf359118d5f0f84cea8d352, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/duty_legs.py b/custom_components/heatpump_optimizer/duty_legs.py
index 688a8da63a..fca775ddef 100644
--- a/custom_components/heatpump_optimizer/duty_legs.py
+++ b/custom_components/heatpump_optimizer/duty_legs.py
@@ -46,22 +46,29 @@ Legs = tuple[tuple[str, float], ...]
 DEFAULT_RULE: LegRule = ("dhw", None)
 
 
-def leg_rule(stop_probability: tuple[float, float], off_seconds: tuple[float, float]) -> LegRule:
+def leg_rule(
+    stop_probability: tuple[float, float],
+    off_seconds: tuple[float, float],
+    unlatched: tuple[bool, bool] = (False, False),
+) -> LegRule:
     """The leg order and whole-step rule of a both step, from the per-direction pairs.
 
     One rule for the arbiter, which serves the legs (``duty_switch``, fed by
-    the learner's latched pairs), and the planner, which prices them (fed by
-    the same pairs through its configuration). Space goes first only where
-    hot water to heating alone stops the compressor. Where the switch into
-    the second duty stops it, a second share shorter than
+    the learner's pairs), and the planner, which prices them (fed by the
+    same pairs through its configuration). A direction ``unlatched`` names
+    is priced before its learner latches and moves neither the order nor the
+    merge: the legs move on a latch only. Space goes first only where hot
+    water to heating alone stops the compressor. Where the switch into the
+    second duty stops it, a second share shorter than
     :data:`SPLIT_MIN_MINUTES` plus that direction's off time goes to the
     first duty when the next step serves the second. Its delivery then moves
-    one step and is not dropped. With no stop priced this is
+    one step and is not dropped. With no latched stop this is
     :data:`DEFAULT_RULE`.
     """
-    first = "space" if stop_probability[0] > 0 and not stop_probability[1] > 0 else "dhw"
+    stops = [p > 0 and not free for p, free in zip(stop_probability, unlatched)]
+    first = "space" if stops[0] and not stops[1] else "dhw"
     into = 0 if first == "dhw" else 1
-    return first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)
+    return first, (off_seconds[into] / 60.0 if stops[into] else None)
 
 
 def both_step_legs(
diff --git a/custom_components/heatpump_optimizer/duty_switch.py b/custom_components/heatpump_optimizer/duty_switch.py
index 9851bc3071..ee7c06f34b 100644
--- a/custom_components/heatpump_optimizer/duty_switch.py
+++ b/custom_components/heatpump_optimizer/duty_switch.py
@@ -9,8 +9,10 @@ recorded, persisted and published on the compressor-starts sensor. Its
 latches are read twice, through one leg rule: the arbiter's split of a both
 step (:func:`both_step_duty`, part B) and the planner (:func:`planner_fields`),
 which prices the switch through ``duty_legs``; both feed
-``duty_legs.leg_rule`` the same pairs (:meth:`DutySwitchLearner.split`), so
-the plan prices the legs the arbiter serves. A factory reset voids the store
+``duty_legs.leg_rule`` the same pairs and unlatched mask
+(:meth:`DutySwitchLearner.split`), so the plan prices the legs the arbiter
+serves. The planner prices a direction before its latch too, at the shrunk
+estimate (:attr:`Direction.priced`, issue 3849); the legs move on a latch only. A factory reset voids the store
 like every other learned estimate.
 
 **Observe** (:class:`DutySwitchLearner`, no Home Assistant object). An
@@ -90,6 +92,10 @@ SPAN_DAYS_ON = 2
 #: episode a half-life old. Without it the first day never moved, and a year-old
 #: episode made six stops on one day read as a year's span.
 SPAN_FLOOR_N = 0.5
+#: Kept episodes an unlatched direction's price is shrunk by: ``k / (n + PRIOR_N)``.
+#: No evidence prices nothing. It is :data:`N_ON`, so a direction that stopped
+#: at every switch is priced at half when it reaches the latch's weight.
+PRIOR_N = N_ON
 OFF_SAMPLES_MAX = 32
 #: Load bounds: a count or an off time past these was not written here.
 _N_MAX = 1e6
@@ -178,6 +184,13 @@ class Direction:
     def p(self) -> float:
         return self.k / self.n if self.n > 0.0 else 0.0
 
+    @property
+    def priced(self) -> float:
+        """The stop probability the planner prices: ``p`` once latched, else
+        ``k`` shrunk by :data:`PRIOR_N` kept episodes (issue 3849: three stops
+        in three switches priced nothing until the latch)."""
+        return self.p if self.usable else self.k / (self.n + PRIOR_N)
+
     @property
     def span_days(self) -> int:
         return 0 if self.first_day is None or self.last_day is None else (self.last_day - self.first_day).days + 1
@@ -392,21 +405,33 @@ class DutySwitchLearner:
 
     def planner_pairs(self) -> tuple[tuple[float, float], tuple[float, float]]:
         """Per direction, in :data:`DIRECTIONS`' order: the stop probability
-        and the median off seconds the planner prices a switch by. Zeros
-        unless the direction's latch is on, and no off time while every
-        stop's was censored."""
-        read = [d if d.usable else Direction() for d in map(self.directions.__getitem__, DIRECTIONS)]
-        return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)
+        (:attr:`Direction.priced`) and the median off seconds the planner
+        prices a switch by. No off time unless the direction's latch is on,
+        nor while every stop's was censored."""
+        ds: Direction = self.directions[DIRECTIONS[0]]
+        sd: Direction = self.directions[DIRECTIONS[1]]
+        offs = [(d.median_off_s or 0.0) if d.usable else 0.0 for d in (ds, sd)]
+        return (ds.priced, sd.priced), (offs[0], offs[1])
+
+    def unlatched(self) -> tuple[bool, bool]:
+        """Per direction, whether its latch is off: priced, never leg-moving."""
+        return not self.directions[DIRECTIONS[0]].usable, not self.directions[DIRECTIONS[1]].usable
 
     def split(self) -> duty_legs.LegRule:
         """The leg rule a both step is served by: ``duty_legs.leg_rule`` of
-        :meth:`planner_pairs`, the pairs the planner prices, so planner and
-        arbiter read one rule. Read only through the latches: ``n``, the
-        tallies and ``span_days`` are not read, so evidence accruing faster on
-        one set-point unit than another moves nothing here until a latch
-        moves. With no latch on this is ``duty_legs.DEFAULT_RULE``: hot water
-        first for its share."""
-        return duty_legs.leg_rule(*self.planner_pairs())
+        :meth:`planner_pairs` and :meth:`unlatched`, what the planner prices,
+        so planner and arbiter read one rule. It moves on the latches only: an
+        unlatched direction's shrunk estimate is priced and masked, so
+        evidence accruing faster on one set-point unit than another moves
+        nothing here until a latch moves. With no latch on this is
+        ``duty_legs.DEFAULT_RULE``: hot water first for its share."""
+        return duty_legs.leg_rule(*self.planner_pairs(), self.unlatched())
+
+    def config_fields(self) -> dict[str, tuple[Any, Any]]:
+        """The ``OptimizationConfig`` fields of :meth:`planner_pairs` and :meth:`unlatched`."""
+        stops, off_s = self.planner_pairs()
+        return {"duty_switch_stop_probability": stops, "duty_switch_off_seconds": off_s,
+                "duty_switch_unlatched": self.unlatched()}
 
     def stored_record(self) -> dict[str, Any]:
         return {"directions": {name: d.stored_row() for name, d in self.directions.items()}}
@@ -559,8 +584,7 @@ def running_now(rec: _Record, action: Any) -> bool:
     return running
 
 
-def planner_fields(coord: Any) -> dict[str, tuple[float, float]]:
+def planner_fields(coord: Any) -> dict[str, tuple[Any, Any]]:
     """The ``OptimizationConfig`` fields a solve prices a duty switch by; a pump never arbitrated reads zeros."""
     rec = _RECORDS.get(coord)
-    stops, off_s = (rec.learner if rec is not None else DutySwitchLearner()).planner_pairs()
-    return {"duty_switch_stop_probability": stops, "duty_switch_off_seconds": off_s}
+    return (rec.learner if rec is not None else DutySwitchLearner()).config_fields()
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index c54290f544..c4b9b06cfc 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -255,7 +255,7 @@ def _relaxed_plans(
 
 
 def _priced_stops(opt: HeatPumpOptimizer) -> tuple[float, float] | None:
-    """The learned stop probability per switch direction, ``None`` when no direction stops.
+    """The learned stop probability per switch direction, latched or not, ``None`` when none stops.
 
     The lost running time is charged on this alone; the price is this times
     ``start_price``, so an install that prices no start prices no switch.
@@ -265,11 +265,10 @@ def _priced_stops(opt: HeatPumpOptimizer) -> tuple[float, float] | None:
 
 
 def _leg_rule(opt: HeatPumpOptimizer) -> duty_legs.LegRule:
-    """The leg rule the arbiter serves a both step by, from the pairs this solve prices."""
+    """The leg rule the arbiter serves a both step by: the latched of the pairs this solve prices."""
     return duty_legs.leg_rule(
-        duty_legs.priced_pair(opt.config.duty_switch_stop_probability, 1.0),
-        duty_legs.priced_pair(opt.config.duty_switch_off_seconds),
-    )
+        _priced_stops(opt) or (0.0, 0.0), duty_legs.priced_pair(opt.config.duty_switch_off_seconds),
+        opt.config.duty_switch_unlatched)
 
 
 def _stop_availability(
@@ -2775,11 +2774,12 @@ class OptimizationConfig:
     #: measuring a slightly different optimizer from the integration.
     cycling_cost: float = DEFAULT_CYCLING_COST
     #: Per direction (hot water to heating, heating to hot water): the learned
-    #: probability that a duty switch stops the compressor, and the seconds it
-    #: then stays off. Zeros price nothing and leave every plan as it was;
-    #: ``duty_legs`` owns what they mean.
+    #: probability that a duty switch stops the compressor, the seconds it then
+    #: stays off, and whether its latch is off (priced, moving no leg). Zeros
+    #: price nothing and leave every plan as it was; ``duty_legs`` owns them.
     duty_switch_stop_probability: tuple[float, float] = (0.0, 0.0)
     duty_switch_off_seconds: tuple[float, float] = (0.0, 0.0)
+    duty_switch_unlatched: tuple[bool, bool] = (False, False)
 
     # --- Capacity tariff (item 8) --------------------------------------
     #: Currency per kW of new monthly peak, already divided by the number of
@@ -4506,9 +4506,8 @@ class HeatPumpOptimizer:
 
         dhw_enabled = self.model.params.dhw_enabled
 
-        # Hour of day at each step. Computed once: the comfort target, both
-        # temperature bounds and the DHW draw pattern all key off it, and it
-        # was previously rebuilt from scratch for each of the four.
+        # Hour of day at each step, computed once: the comfort target, both
+        # temperature bounds and the DHW draw pattern all key off it.
         step_datetimes, step_hours = _step_clock(start_time, n_steps, dt)
         # Weekday per step, for weekly DHW windows (#3) and the per-weekday
         # overrides (#1260); the helper returns None unless either is
diff --git a/dev/audit/harnesses/r11_outside_3849_unlatched_price.py b/dev/audit/harnesses/r11_outside_3849_unlatched_price.py
new file mode 100644
index 0000000000..5568e8505f
--- /dev/null
+++ b/dev/audit/harnesses/r11_outside_3849_unlatched_price.py
@@ -0,0 +1,95 @@
+"""R11-OUTSIDE-3849: what a solve prices a hot water to heating switch at before the latch.
+
+    PYTHONPATH=tests/hastub:custom_components \\
+        python3 dev/audit/harnesses/r11_outside_3849_unlatched_price.py
+
+Synthetic; no private data. The finding is outside issue 3849 (Bankaifan),
+which has no finder harness; this one reproduces its cases 2, 3 and 03:00 on
+the tree it runs in, and runs on a tree before the fix (it reads only
+``DutySwitchLearner.planner_pairs``, ``optimizer._switch_cost_fn`` and
+``optimizer._leg_rule``, and sets ``duty_switch_unlatched`` only where the
+configuration has it).
+
+The record is the issue's: hot water to heating stopped 3, kept 0, n = 2,
+unlatched; heating to hot water never seen. The plans are the issue's ledger
+around 03:00, one hot-water charge split by a single heating step
+(``split``), against the same steps with the charge whole (``whole``): hot
+water 2.0 kW, heating 1.0 kW, a 3.0 kW pump with a 0.53 kW floor, one start
+priced 1.0. The combined draw of both is on at every step, so the start term
+sees neither switch; the switch term is all that separates them.
+
+Printed per learner: the read (stop pair, off pair, mask), the leg rule the
+solve serves a both step by, the switch term of each plan and the split's
+excess. Null control: an empty learner prices nothing on either tree, and
+its leg rule is ``DEFAULT_RULE``; the harness exits 1 if it reads otherwise.
+"""
+from __future__ import annotations
+
+import dataclasses
+import sys
+from datetime import date
+
+import numpy as np
+
+import heatpump_optimizer.optimizer as om
+from heatpump_optimizer import duty_legs, duty_switch
+from heatpump_optimizer.thermal_model import ThermalModel, ThermalParameters
+
+DHW_KW, SPACE_KW, P_MAX, P_MIN, START = 2.0, 1.0, 3.0, 0.53, 1.0
+#: 02:30 02:45 03:00 03:15 03:30 03:45 04:00, the ledger's duties.
+SPLIT = ("dhw", "dhw", "space", "dhw", "dhw", "space", "space")
+WHOLE = ("dhw", "dhw", "dhw", "dhw", "space", "space", "space")
+
+
+def _plan(duties: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
+    space = np.array([SPACE_KW if d == "space" else 0.0 for d in duties])
+    dhw = np.array([DHW_KW if d == "dhw" else 0.0 for d in duties])
+    return space, dhw
+
+
+def _learners() -> dict[str, duty_switch.DutySwitchLearner]:
+    day = date(2026, 11, 21)
+    issue = duty_switch.Direction(k=2.0, kept_w=0.0, first_day=day, last_day=day, usable=False,
+                                  off_s=[455.0, 483.0, 450.0], stopped=3)
+    return {
+        "empty (null control)": duty_switch.DutySwitchLearner(),
+        "issue 3849 (stopped 3, kept 0, n = 2, unlatched)": duty_switch.DutySwitchLearner(
+            {"dhw_space": issue, "space_dhw": duty_switch.Direction()}),
+    }
+
+
+def _opt(learner: duty_switch.DutySwitchLearner) -> om.HeatPumpOptimizer:
+    params = ThermalParameters()
+    params.min_electrical_power, params.max_electrical_power = P_MIN, P_MAX
+    params.dhw_enabled = True
+    stops, off = learner.planner_pairs()
+    fields = {"cycling_cost": START, "duty_switch_stop_probability": stops,
+              "duty_switch_off_seconds": off}
+    names = {f.name for f in dataclasses.fields(om.OptimizationConfig)}
+    if "duty_switch_unlatched" in names:
+        fields["duty_switch_unlatched"] = learner.unlatched()
+    return om.HeatPumpOptimizer(ThermalModel(params), om.OptimizationConfig(**fields))
+
+
+def main() -> int:
+    bad = 0
+    for label, learner in _learners().items():
+        opt = _opt(learner)
+        term = om._switch_cost_fn(opt)
+        cost = {}
+        for name, duties in (("split", SPLIT), ("whole", WHOLE)):
+            value = term(*_plan(duties))
+            cost[name] = 0.0 if value is None else float(value)
+        rule = om._leg_rule(opt)
+        print(f"{label}: read {learner.planner_pairs()} mask "
+              f"{getattr(opt.config, 'duty_switch_unlatched', 'absent')} leg rule {rule}")
+        print(f"  switch term split {cost['split']:.4f} whole {cost['whole']:.4f} "
+              f"split excess {cost['split'] - cost['whole']:.4f} (start price {START})")
+        if label.startswith("empty") and (any(cost.values()) or rule != duty_legs.DEFAULT_RULE):
+            print("  NULL CONTROL FAILED: an empty learner priced a switch or moved the legs")
+            bad = 1
+    return bad
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3877.md b/dev/programme/delivery/3877.md
new file mode 100644
index 0000000000..312b7c599d
--- /dev/null
+++ b/dev/programme/delivery/3877.md
@@ -0,0 +1 @@
+- [#3877](https://github.com/tvofi/heatpump_optimizer/pull/3877) — **open**, Honest duty-switch price before the learner latches (R11-OUTSIDE-3849)
diff --git a/docs/architecture.md b/docs/architecture.md
index cc503207c7..e24ec8eb66 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -204,10 +204,10 @@ custom_components/heatpump_optimizer/
 ├── supply_hold.py        # The supply switch's minimum run and pause, held
 │                         #   across a re-solve, a cycle or a restart
 ├── duty_switch.py        # Learns per direction whether a duty switch stops
-│                         #   the running compressor; a latched direction's
-│                         #   estimate is what the solve prices that switch by
-│                         #   and what orders the legs of a both step the
-│                         #   arbiter serves
+│                         #   the running compressor; its estimate, shrunk
+│                         #   until a direction latches, is what the solve
+│                         #   prices that switch by; a latched one also orders
+│                         #   the legs of a both step the arbiter serves
 ├── heat_curve.py         # The heat-curve displace's outputs: the MQTT topics
 │                         #   and a number entity, kind offset or persistent
 ├── off_restore.py        # The one owner of the off and unload restore: what
diff --git a/docs/configuration.md b/docs/configuration.md
index 6b0ba394d7..ddbd357b03 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -861,12 +861,16 @@ writes, at every 15-minute plan step:
   the compressor running, the new duty asking for heat and the plan keeping
   that duty; a stop within 3 minutes of a counted switch counts against its
   direction, and a switch a person's own mode change explains is not
-  counted. Once a direction has
+  counted. From the first counted stop the plan charges that switch a share of
+  the **Cost of one compressor start**: the stops over the counted switches
+  plus 5, so three stops in three switches are charged 3/8 of a start, and
+  tries to place hot water where no such switch follows it (not on a combi
+  store). Once a direction has
   stopped the compressor on at least half of a weighted 5 or more switches,
-  seen on at least two calendar days (a switch weighs half after 14 days), the plan charges that switch a share of
-  the **Cost of one compressor start** and tries to place hot water where no
-  such switch follows it (not on a combi store). For a switch from hot water
-  to heating it also expects the median measured off time as heat not
+  seen on at least two calendar days (a switch weighs half after 14 days), the
+  share is the stops over the switches, and it is learned: only then does it
+  change the order of a split step (above). For a switch from hot water
+  to heating a learned direction also expects the median measured off time as heat not
   delivered in the heating that follows; a switch the other way is priced
   but costs no heat. With the start cost at 0 only that lost heat is planned
   for. The counts per direction are attributes of the
diff --git a/tests/closures.json b/tests/closures.json
index 7358ea0354..6982e060f0 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4768,6 +4768,7 @@
    "dev/audit/harnesses/r11_kernel_step_agree.py",
    "dev/audit/harnesses/r11_main_cancel_mutants.py",
    "dev/audit/harnesses/r11_money_currency_precedence.py",
+   "dev/audit/harnesses/r11_outside_3849_unlatched_price.py",
    "dev/audit/harnesses/r11_owner_criteria.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 062b8ee5b5..b0378091b3 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -938,9 +938,10 @@ def _late_delta_facts() -> dict[str, object]:
     Read by driving the deciding symbol, never a comment: the disinfection
     write on a 5 degC step, the wood tank's one-probe means, the flow-bias
     bounds, the both-step leg order with only hot water to heating stopping
-    the compressor, and the fixed transfer fee with no fee mode.
+    the compressor, the fixed transfer fee with no fee mode, and the price of
+    a switch that stopped the compressor three times in three, unlatched.
     """
-    from heatpump_optimizer import const, duty_legs, external_heat, flow_lift, grid_fee
+    from heatpump_optimizer import const, duty_legs, duty_switch, external_heat, flow_lift, grid_fee
     from heatpump_optimizer.inputs import SetpointGrid
     from heatpump_optimizer.thermal_model import ThermalParameters, dhw_step_target_c
 
@@ -956,6 +957,8 @@ def _late_delta_facts() -> dict[str, object]:
         "first_leg": duty_legs.leg_rule((1.0, 0.0), (60.0, 60.0))[0],
         "default_first": duty_legs.leg_rule((0.0, 0.0), (0.0, 0.0))[0],
         "fixed_fee_no_mode": fee.fixed,
+        "prior_n": duty_switch.PRIOR_N,
+        "three_of_three": duty_switch.Direction(k=3.0, usable=False).priced,
     }
 
 
@@ -970,6 +973,10 @@ _LATE_DELTA_BAD = {
              "minutes, then heating for the rest.",
     "fee": "| Fixed transfer fee | 0.0 per kWh | 0–5, 0.01 steps | A flat fee added in every "
            "hour, on top of any rules. |",
+    "switch_price": "Once a direction has stopped the compressor on at least half of a weighted "
+                    "5 or more switches, seen on at least two calendar days (a switch weighs half "
+                    "after 14 days), the plan charges that switch a share of the **Cost of one "
+                    "compressor start**",
 }
 
 
@@ -985,6 +992,10 @@ def _late_delta_true(facts: dict[str, object]) -> dict[str, object]:
             "Hot water runs first, unless the switch from hot water to heating" in t
             and "then heating runs first" in t),
         "fee": lambda t: facts["fixed_fee_no_mode"] == 0.0 and "Ignored while the grid transfer fee is None" in t,
+        "switch_price": lambda t: facts["three_of_three"] == 3.0 / (3.0 + facts["prior_n"]) == 3.0 / 8.0 and all(
+            phrase in " ".join(t.split()) for phrase in (
+                "From the first counted stop the plan charges",
+                f"the stops over the counted switches plus {facts['prior_n']:g}", "3/8 of a start")),
     }
 
 
@@ -994,12 +1005,14 @@ def check_late_delta_claims() -> None:
     says = _late_delta_true(facts)
     config = DOCS["configuration.md"]
     split = re.search(r"- \*\*A step the plan gives both duties is split\*\*.*?\n- ", config, re.S)
+    price = re.search(r"- \*\*A switch that stops the compressor is priced\.\*\*.*?\n- ", config, re.S)
     texts = {
         "cycle": next(iter(_sentences_with(config, "62 °C cycle")), ""),
         "wood": _row("configuration.md", "Wood tank bottom sensor"),
         "bias": _row("configuration.md", "Price the supply temperature lift (no mixing valve)"),
         "split": split.group(0) if split else "",
         "fee": _row("configuration.md", "Fixed transfer fee"),
+        "switch_price": price.group(0) if price else "",
     }
     for key, text in texts.items():
         R.check(f"docs/configuration.md {key}: the sentence states what the code decides",
diff --git a/tests/features.py b/tests/features.py
index 8672734d81..533eca2b55 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -27867,6 +27867,26 @@ R.check(
     f"never {_dsp_cfg_never.duty_switch_stop_probability}, read "
     f"{_dsp_cfg_read.duty_switch_stop_probability} {_dsp_cfg_read.duty_switch_off_seconds}",
 )
+# R11-OUTSIDE-3849: an unlatched record is priced shrunk and masked from the legs.
+_dsp_push_u = _dsp_push_ds.DutySwitchLearner({
+    "dhw_space": _dsp_push_d(k=2.0, kept_w=0.0, first_day=_dsp_push_day, last_day=_dsp_push_day,
+                             usable=False, off_s=[501.0]),
+    "space_dhw": _dsp_push_d(),
+})
+_dsp_cfg_unever, _dsp_cfg_uread, _ = _dsp_pushed(_dsp_push_u)
+R.check(
+    "the coordinator passes the unlatched mask with the pairs: none on a pump "
+    "never arbitrated (both directions unlatched, priced zero), the latched "
+    "learner's read latched, and an unlatched record's stop priced at "
+    "k / (n + PRIOR_N) beside its mask, its off time unread",
+    _dsp_cfg_never.duty_switch_unlatched == (True, True)
+    and _dsp_cfg_read.duty_switch_unlatched == (False, False)
+    and _dsp_cfg_uread.duty_switch_unlatched == (True, True)
+    and _dsp_cfg_uread.duty_switch_stop_probability == (2.0 / (2.0 + _dsp_push_ds.PRIOR_N), 0.0)
+    and _dsp_cfg_uread.duty_switch_off_seconds == (0.0, 0.0),
+    f"never {_dsp_cfg_never.duty_switch_unlatched} read {_dsp_cfg_read.duty_switch_unlatched} "
+    f"unlatched {_dsp_cfg_uread.duty_switch_stop_probability} {_dsp_cfg_uread.duty_switch_unlatched}",
+)
 
 _svc_sim_hass = FakeHass()
 _seed_prices(_svc_sim_hass)  # #924
@@ -94536,7 +94556,8 @@ R.check(
 )
 
 
-def _dsp_opt(pair=(0.0, 0.0), off=(0.0, 0.0), *, clamp=False, p_min=1.5, p_max=5.5, cyc=0.3):
+def _dsp_opt(pair=(0.0, 0.0), off=(0.0, 0.0), *, clamp=False, p_min=1.5, p_max=5.5, cyc=0.3,
+             unlatched=(False, False)):
     params = _DspTP()
     params.mixing_valve_mode = "none"
     params.buffer_tank_volume = 750.0
@@ -94545,6 +94566,7 @@ def _dsp_opt(pair=(0.0, 0.0), off=(0.0, 0.0), *, clamp=False, p_min=1.5, p_max=5
     cfg = _DspCfg(clamp_planned_levels=clamp, cycling_cost=cyc)
     if pair is not None:
         cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, off
+        cfg.duty_switch_unlatched = unlatched
     return _DspOpt(_DspTM(params), cfg)
 
 
@@ -94936,10 +94958,11 @@ R.check(
 )
 
 
-def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0, out_mean=2.0, **install):
+def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0, out_mean=2.0,
+               unlatched=(False, False), **install):
     """One full ``optimize``; the planner builds, the published simulation's
     inputs and the objective closures are recorded beside the result."""
-    opt = _dsp_opt(pair, off, **install)
+    opt = _dsp_opt(pair, off, unlatched=unlatched, **install)
     seen = _DspNS(
         builds=[], sims=[], objectives=[], solves=[], solved=[], min_runs=[],
         energy=[None], vectors=[0], vectors_outside=[0], solving=[0], stages=[], opt=opt,
@@ -96037,7 +96060,8 @@ R.check(
     f"{_dsp_rt_back.directions}",
 )
 
-# The read: both pairs in the leaf's order, zeros unless the stored latch is on.
+# The read: both pairs in the leaf's order; an off time only once the stored
+# latch is on, a stop probability shrunk by PRIOR_N before it (R11-OUTSIDE-3849).
 _dsp_table = _dsp_ds.DutySwitchLearner()
 for _dsp_i in range(6):
     _dsp_stop(_dsp_table, _DSP_DAY + timedelta(hours=7 * _dsp_i), 501)
@@ -96055,9 +96079,17 @@ _DSP_LEARNERS = {
     "an install whose every switch was kept": _dsp_ds.DutySwitchLearner(
         {"dhw_space": _dsp_dir(0.0, 10.0, usable=False), "space_dhw": _dsp_dir(0.0, 10.0, usable=False)}),
 }
-R.check(
-    "the read returns zeros while a direction is unlatched, its off times with it",
-    all(l.planner_pairs() == ((0.0, 0.0), (0.0, 0.0)) for l in _DSP_LEARNERS.values()),
+_DSP_NULL_LEARNERS = ("an empty learner", "an install whose every switch was kept")
+_DSP_UNDER = _DSP_LEARNERS["a learner under its on-threshold, off times stored"]
+R.check(
+    "the read returns no off time while a direction is unlatched, and its stop "
+    "probability shrunk to k / (n + PRIOR_N): zeros with no evidence and with "
+    "every switch kept, 4 / 9 for four stops under the on-threshold; every "
+    "direction of the three reads unlatched",
+    all(_DSP_LEARNERS[n].planner_pairs() == ((0.0, 0.0), (0.0, 0.0)) for n in _DSP_NULL_LEARNERS)
+    and _DSP_UNDER.planner_pairs() == ((4.0 / (4.0 + _dsp_ds.PRIOR_N), 0.0), (0.0, 0.0))
+    and _dsp_ds.PRIOR_N == 5.0
+    and all(l.unlatched() == (True, True) for l in _DSP_LEARNERS.values()),
     f"{ {n: l.planner_pairs() for n, l in _DSP_LEARNERS.items()} }",
 )
 _dsp_two = _dsp_ds.DutySwitchLearner({
@@ -96074,8 +96106,9 @@ R.check(
 # 4, the learner arm: each null state's read, handed to a full optimize.
 _dsp_arm_bad = []
 for _dsp_name, _dsp_kw in _DSP_INSTALLS.items():
-    for _dsp_label, _dsp_l in _DSP_LEARNERS.items():
-        _dsp_null = _dsp_solve(*_dsp_l.planner_pairs(), **_dsp_kw)
+    for _dsp_label in _DSP_NULL_LEARNERS:
+        _dsp_l = _DSP_LEARNERS[_dsp_label]
+        _dsp_null = _dsp_solve(*_dsp_l.planner_pairs(), unlatched=_dsp_l.unlatched(), **_dsp_kw)
         if (
             not _dsp_same_plan(_dsp_null, _dsp_base[_dsp_name])
             or _dsp_null.bans or _dsp_null.opt._space_avail is not None
@@ -96083,9 +96116,9 @@ for _dsp_name, _dsp_kw in _DSP_INSTALLS.items():
         ):
             _dsp_arm_bad.append((_dsp_name, _dsp_label))
 R.check(
-    "null controls from learner state: an empty learner, one under its "
-    "on-threshold and an install whose every switch was kept each read a plan "
-    "identical to today's on all three install classes",
+    "null controls from learner state: an empty learner and an install whose "
+    "every switch was kept each read a plan identical to today's on all three "
+    "install classes (one under its on-threshold is priced since R11-OUTSIDE-3849)",
     not _dsp_arm_bad,
     f"{_dsp_arm_bad}",
 )
@@ -96097,6 +96130,146 @@ R.check(
 )
 
 
+# R11-OUTSIDE-3849 (issue 3849, Bankaifan): the hot water to heating stop was
+# priced at zero until the learner latched (n >= N_ON over two days). An
+# install whose switch stopped the compressor three times in three was planned
+# as if it never did. Before the latch the planner now prices k / (n + PRIOR_N)
+# (``Direction.priced``); the arbiter's leg order and merge still move on a
+# latch only (``duty_legs.leg_rule``'s unlatched mask), so the plan prices the
+# legs the arbiter serves whatever the latch.
+def _dsp_3849(usable=False, k=2.0, kept_w=0.0, off_s=(501.0, 492.0, 530.0)):
+    """The issue's record: hot water to heating stopped 3, kept 0, n = 2."""
+    d = _dsp_dir(k, kept_w, usable=usable, off_s=off_s)
+    d.stopped = 3
+    return _dsp_ds.DutySwitchLearner({"dhw_space": d, "space_dhw": _dsp_ds.Direction()})
+
+
+_dsp_i49, _dsp_i49_on = _dsp_3849(), _dsp_3849(usable=True)
+R.check(
+    "issue 3849's record (three stops in three switches, n = 2, unlatched) prices "
+    "hot water to heating at 2 / (2 + PRIOR_N) and reads no off time; control: "
+    "the same record latched prices p = 1 and its median off time",
+    _dsp_i49.planner_pairs() == ((2.0 / (2.0 + _dsp_ds.PRIOR_N), 0.0), (0.0, 0.0))
+    and _dsp_i49.unlatched() == (True, True)
+    and _dsp_i49_on.planner_pairs() == ((1.0, 0.0), (501.0, 0.0))
+    and _dsp_i49_on.unlatched() == (False, True),
+    f"unlatched {_dsp_i49.planner_pairs()} latched {_dsp_i49_on.planner_pairs()}",
+)
+_dsp_grid = [(k / 2.0, w / 2.0) for k in range(int(2 * _dsp_ds.N_CAP) + 1)
+             for w in range(int(2 * _dsp_ds.N_CAP) + 1)]
+_dsp_shrunk_bad = [
+    (k, w, d.priced, d.p) for k, w in _dsp_grid
+    for d in [_dsp_dir(k, w, usable=False)]
+    if not (0.0 <= d.priced < 1.0 and (d.priced == 0.0) == (k == 0.0)
+            and (k == 0.0 or d.priced < d.p) and d.priced == k / (k + w + _dsp_ds.PRIOR_N))
+]
+_dsp_cap = _dsp_dir(_dsp_ds.N_CAP, 0.0, usable=False)
+R.check(
+    f"the shrunk price over every unlatched record on a half-episode grid to the "
+    f"cap ({len(_dsp_grid)} records): zero exactly where no stop weighs, under p "
+    "wherever one does, never a whole start; at the cap with every switch a stop "
+    "it is N_CAP / (N_CAP + PRIOR_N); latched it is p",
+    len(_dsp_grid) == (2 * int(_dsp_ds.N_CAP) + 1) ** 2 and not _dsp_shrunk_bad
+    and _dsp_cap.priced == _dsp_ds.N_CAP / (_dsp_ds.N_CAP + _dsp_ds.PRIOR_N)
+    and _dsp_dir(3.0, 1.0).priced == 0.75,
+    f"{_dsp_shrunk_bad[:5]} cap {_dsp_cap.priced!r}",
+)
+R.check(
+    "an unlatched direction moves neither the order nor the merge: issue "
+    "3849's read is DEFAULT_RULE, hot water first and never merged; control: "
+    "the same pairs read as latched serve space first",
+    _dsp_i49.split() == _dsp_dl.DEFAULT_RULE
+    and _dsp_dl.leg_rule(*_dsp_i49.planner_pairs()) == ("space", None)
+    and _dsp_i49_on.split() == ("space", None),
+    f"{_dsp_i49.split()} {_dsp_dl.leg_rule(*_dsp_i49.planner_pairs())} {_dsp_i49_on.split()}",
+)
+R.check(
+    "the mask is per direction: hot water to heating latched beside an unlatched, "
+    "priced switch the other way serves space first, as with that switch unpriced; "
+    "control: both latched serve hot water first and merge into heating",
+    _dsp_dl.leg_rule((1.0, 0.4), (501.0, 0.0), (False, True))
+    == _dsp_dl.leg_rule((1.0, 0.0), (501.0, 0.0)) == ("space", None)
+    and _dsp_dl.leg_rule((1.0, 0.4), (501.0, 0.0)) == ("dhw", 501.0 / 60.0)
+    and _dsp_dl.leg_rule((0.4, 1.0), (0.0, 300.0), (True, False)) == ("dhw", None)
+    and _dsp_dl.leg_rule((0.4, 1.0), (0.0, 300.0)) == ("dhw", 0.0),
+)
+# One rule, read twice: every learner state the census enumerates (each
+# direction empty, unlatched with a stop, latched with a stop, latched all kept)
+# gives the configuration the coordinator builds the leg rule the arbiter splits by.
+_dsp_states = {
+    "empty": lambda: _dsp_ds.Direction(),
+    "unlatched": lambda: _dsp_dir(2.0, 0.0, usable=False, off_s=[501.0]),
+    "latched": lambda: _dsp_dir(3.0, 1.0, off_s=[400.0, 620.0]),
+    "latched kept": lambda: _dsp_dir(0.0, 6.0),
+}
+_dsp_rule_pairs = [
+    (a, b, _dsp_ds.DutySwitchLearner({"dhw_space": _dsp_states[a](), "space_dhw": _dsp_states[b]()}))
+    for a in _dsp_states for b in _dsp_states
+]
+_dsp_rule_bad = [
+    (a, b) for a, b, l in _dsp_rule_pairs
+    if _dsp_om._leg_rule(_dsp_opt(*l.planner_pairs(), unlatched=l.unlatched())) != l.split()
+]
+_dsp_rule_nomask = [
+    (a, b) for a, b, l in _dsp_rule_pairs
+    if _dsp_om._leg_rule(_dsp_opt(*l.planner_pairs())) != l.split()
+]
+R.check(
+    f"the planner's leg rule is the arbiter's on all {len(_dsp_rule_pairs)} learner "
+    "states the census enumerates (four per direction); control: a configuration "
+    "without the mask disagrees exactly where an unlatched stop would move the "
+    "rule: hot water to heating unlatched beside anything, and heating to hot "
+    "water unlatched beside a latched stop the other way",
+    len(_dsp_rule_pairs) == len(_dsp_states) ** 2 and not _dsp_rule_bad
+    and sorted(_dsp_rule_nomask)
+    == sorted([("unlatched", b) for b in _dsp_states] + [("latched", "unlatched")]),
+    f"bad {_dsp_rule_bad} nomask {_dsp_rule_nomask}",
+)
+# A design choice, not an accident of the default. A configuration that never
+# sets the mask (a harness handed a pair, the R10 fixtures above) reads its
+# pair as latched. Every pair it prices then moves the legs as before.
+_dsp_nomask_cfg = _DspCfg()
+_dsp_nomask_cfg.duty_switch_stop_probability = (1.0, 0.0)
+R.check(
+    "a configuration that never sets the mask reads its pair as latched: hot "
+    "water to heating alone stopping serves space first",
+    _dsp_om._leg_rule(_DspOpt(_DspTM(_DspTP()), _dsp_nomask_cfg)) == ("space", None),
+)
+_dsp_i49_rec = _dsp_ds._Record(None, None, learner=_dsp_i49, loaded=True)
+_dsp_i49_start = datetime(2026, 11, 21, 12, 30, tzinfo=UTC)
+_dsp_i49_legs = [
+    _dsp_ds.both_step_duty(_dsp_i49_rec, _dsp_i49_start, _dsp_i49_start + timedelta(minutes=m),
+                           2.0, 2.0, 15.0, "space")
+    for m in (0, 7, 8, 14)
+]
+R.check(
+    "the arbiter serves issue 3849's both step as before the learner existed: "
+    "hot water for its share, then heating",
+    _dsp_i49_legs == ["dhw", "dhw", "space", "space"]
+    and _dsp_i49_rec.order[1] == _dsp_dl.both_step_legs(2.0, 2.0, 15.0),
+    f"{_dsp_i49_legs}",
+)
+_dsp_i49_solved = {
+    name: _dsp_solve(*_dsp_i49.planner_pairs(), unlatched=_dsp_i49.unlatched(), **kw)
+    for name, kw in _DSP_INSTALLS.items()
+}
+_dsp_i49_moved = [n for n, seen in _dsp_i49_solved.items() if not _dsp_same_plan(seen, _dsp_base[n])]
+_dsp_i49_w = {
+    n: (_dsp_dl.switch_weight(_dsp_base[n].space, _dsp_base[n].dhw, (1.0, 0.0), 5.5),
+        _dsp_dl.switch_weight(seen.space, seen.dhw, (1.0, 0.0), 5.5))
+    for n, seen in _dsp_i49_solved.items()
+}
+R.check(
+    "issue 3849's read reaches a full optimize: the switch is an operand of the "
+    "objective, the solve's leg rule is DEFAULT_RULE, and it moves the plan on "
+    "every install class (null control: the empty learner's read moves none, above)",
+    all(_dsp_om._switch_cost_fn(seen.opt)(seen.space, seen.dhw) is not None
+        and _dsp_om._leg_rule(seen.opt) == _dsp_dl.DEFAULT_RULE
+        for seen in _dsp_i49_solved.values())
+    and sorted(_dsp_i49_moved) == sorted(_DSP_INSTALLS),
+    f"moved {_dsp_i49_moved}; hot water to heating weight base -> priced {_dsp_i49_w}",
+)
+
 # R11-OUTSIDE-HONEST-STARTS-RUNS, the descents of a solve that prices a stop.
 # The relaxed descent weighs a switch at the combined draw and the true
 # objective in starts, so the descent that avoids a switch can commit to a
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.415d247d.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.415d247d.json
new file mode 100644
index 0000000000..d67785e3c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.415d247d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule BOOLOP 415d247d",
+  "killed_by": "tests/features.py",
+  "old": "    stops = [p > 0 and not free for p, free in zip(stop_probability, unlatched)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`stops = [p > 0 or not free for p, free in zip(stop_probability, unlatched)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.9e0433b2.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.9e0433b2.json
new file mode 100644
index 0000000000..6ba0203f26
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.9e0433b2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule BOOLOP 9e0433b2",
+  "killed_by": "tests/features.py",
+  "old": "    first = \"space\" if stops[0] and not stops[1] else \"dhw\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`first = \"space\" if stops[0] or not stops[1] else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=31."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json
deleted file mode 100644
index 397987d0cd..0000000000
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.BOOLOP.ac335b68.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule BOOLOP ac335b68",
-  "killed_by": "tests/features.py",
-  "old": "    first = \"space\" if stop_probability[0] > 0 and not stop_probability[1] > 0 else \"dhw\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`first = \"space\" if stop_probability[0] > 0 or not stop_probability[1] > 0 else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
-}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.415d247d.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.415d247d.json
new file mode 100644
index 0000000000..65397b0edc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.415d247d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND 415d247d",
+  "killed_by": "tests/features.py",
+  "old": "    stops = [p > 0 and not free for p, free in zip(stop_probability, unlatched)]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`stops = [p >= 0 and not free for p, free in zip(stop_probability, unlatched)]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json
deleted file mode 100644
index d8859abaa7..0000000000
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.726b5c41.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND 726b5c41",
-  "killed_by": "tests/features.py",
-  "old": "    return first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return first, (off_seconds[into] / 60.0 if stop_probability[into] >= 0 else None)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json
deleted file mode 100644
index be3c6d34a4..0000000000
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.CMP_BOUND.ac335b68.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule CMP_BOUND ac335b68",
-  "killed_by": "tests/features.py",
-  "old": "    first = \"space\" if stop_probability[0] > 0 and not stop_probability[1] > 0 else \"dhw\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`first = \"space\" if stop_probability[0] >= 0 and not stop_probability[1] > 0 else \"dhw\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=21. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.3e796948.json
similarity index 65%
rename from tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json
rename to tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.3e796948.json
index 1f336579bc..76abb6147e 100644
--- a/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.726b5c41.json
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_rule.RETURN_DEL.3e796948.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule RETURN_DEL 726b5c41",
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_rule RETURN_DEL 3e796948",
   "killed_by": "tests/features.py",
-  "old": "    return first, (off_seconds[into] / 60.0 if stop_probability[into] > 0 else None)",
+  "old": "    return first, (off_seconds[into] / 60.0 if stops[into] else None)",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.priced.RETURN_DEL.674ac3db.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.priced.RETURN_DEL.674ac3db.json
new file mode 100644
index 0000000000..a4a0bd410f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.priced.RETURN_DEL.674ac3db.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.priced RETURN_DEL 674ac3db",
+  "killed_by": "tests/features.py",
+  "old": "        return self.p if self.usable else self.k / (self.n + PRIOR_N)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.04ef69d7.json
similarity index 63%
rename from tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
rename to tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.04ef69d7.json
index 5d0d9757be..db2165c4db 100644
--- a/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.04ef69d7.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:planner_fields RETURN_DEL 77cc0eae",
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.planner_pairs RETURN_DEL 04ef69d7",
   "killed_by": "tests/features.py",
-  "old": "    return {\"duty_switch_stop_probability\": stops, \"duty_switch_off_seconds\": off_s}",
+  "old": "        return (ds.priced, sd.priced), (offs[0], offs[1])",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.827431ae.json
similarity index 81%
rename from tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json
rename to tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.827431ae.json
index ecad4e45f0..8cac5217a0 100644
--- a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.e5fbd410.json
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.split.RETURN_DEL.827431ae.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.split RETURN_DEL e5fbd410",
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.split RETURN_DEL 827431ae",
   "killed_by": "tests/features.py",
-  "old": "        return duty_legs.leg_rule(*self.planner_pairs())",
+  "old": "        return duty_legs.leg_rule(*self.planner_pairs(), self.unlatched())",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
 }
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.unlatched.RETURN_DEL.351a4555.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.unlatched.RETURN_DEL.351a4555.json
new file mode 100644
index 0000000000..5a80c44974
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.unlatched.RETURN_DEL.351a4555.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.unlatched RETURN_DEL 351a4555",
+  "killed_by": "tests/features.py",
+  "old": "        return not self.directions[DIRECTIONS[0]].usable, not self.directions[DIRECTIONS[1]].usable",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.c60f412a.json
similarity index 59%
rename from tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
rename to tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.c60f412a.json
index a10a5b3c92..133b5c0dd5 100644
--- a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.c60f412a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.planner_pairs RETURN_DEL fc67f05d",
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:planner_fields RETURN_DEL c60f412a",
   "killed_by": "tests/features.py",
-  "old": "        return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+  "old": "    return (rec.learner if rec is not None else DutySwitchLearner()).config_fields()",
   "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
 }
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f10f128938..7308ce2d73 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17301,
+ "class_excess_loc": 17300,
  "const_modules_over_50": 4,
  "coordinator_attrs": 135,
  "coordinator_multiassigned_attrs": 103,
@@ -16,9 +16,9 @@
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
- "module_excess_loc": 21775,
+ "module_excess_loc": 21774,
  "name_kept_members": 38,
- "recorded_at": "59b17e97ae1b65bd86c6b5423c0a5e993031c9a0",
+ "recorded_at": "e3cb5c019b464a770cc7c6fe2fbc858ed29debf7",
  "seam_cut_total": 413,
  "unloaded_package_imports": 14
 }

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
