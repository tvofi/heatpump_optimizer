# Review packet #3050
head: e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87
base: 2b6bef7453a8bdaf97d42f382a116ce226b35ccc

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124717926241 neutral
arch-score / arch-score id=124717803204 success
arm id=124717704385 skipped
budget-raise-gate / budget-raise-gate id=124717803253 success
cancel-superseded id=124717865489 success
codeql / Analyze (actions) id=124717803207 success
codeql / Analyze (javascript-typescript) id=124717803142 success
codeql / Analyze (python) id=124717803179 in_progress
governance / delivery-status id=124717803120 success
governance / delivery-status-publish id=124717804580 skipped
governance / env-matrix id=124717803167 in_progress
governance / instrument-self-tests id=124717803182 in_progress
governance / policy-docs id=124717803198 in_progress
governance / record id=124717804051 skipped
governance / wave-script id=124717803118 success
hassfest / hassfest id=124717803066 success
kernel-points id=124717803998 skipped
prelude id=124717865330 in_progress
refresh id=124717865124 success
tests / arch-instrument id=124717905647 success
tests / briefs id=124717803222 success
tests / browser id=124717905626 in_progress
tests / closure-scope id=124717803265 success
tests / closures id=124717905559 in_progress
tests / coverage id=124717905511 in_progress
tests / fast (3.14) id=124717905545 in_progress
tests / mutation id=124717803279 in_progress
tests / nightly-ha id=124717906545 skipped
tests / nightly-status id=124717803202 success
tests / replay id=124717905537 success
tests / typing id=124717905591 success
validate / validate-hacs id=124717803042 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 409c12f8: R10-COP-GATE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified - `pump_arbiter.py:497` `_experiment_kw`: duty and level.
             no segment of this names a program this check knows
  unverified - `pump_arbiter.py:661` `_flow_target`'s level.
             no segment of this names a program this check knows
  unverified - `pump_arbiter.py:796` `_planned_duty`'s plan step, now reached only by a non-experiment action.
             no segment of this names a program this check knows
  unverified - `coordinator.py:9756`, the fold's routing.
             no segment of this names a program this check knows
  unverified - `sensor.py:2045`, the outcome row.
             no segment of this names a program this check knows
  unverified - `coordinator.py:7713`, the view's publication (fields added).
             no segment of this names a program this check knows
  unverified - `pump_arbiter.py:1208` and `:1213`, `step_supply`: the tick writes nothing under an experiment. Item 31, tested.
             no segment of this names a program this check knows
  unverified - `boost.py:647`, `RELEASE_SYSID`: item 13, pinned by `a measurement experiment and a stale plan release either block`.
             no segment of this names a program this check knows
  unverified - `early_cutoff.py:225`, `_exempt`'s `step_duty`: the cut-off may still cut an experiment's step on a warm room. That is its comfort guard. A cut interval's spot reading is either the running draw or the idle draw, and the idle draw is dropped by `takes_ceiling`'s idle rule, so the store's value is not biased. At the base the same holds for the fit on a switch install.
             no segment of this names a program this check knows
  ok         D=$(mktemp -d); PYTHONPATH=tests/hastub python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=14ed135512e3d7db899081f2c2639ce5674b8f2a PYTHONPATH=tests/hastub bash tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/optimality.py
             `tests/optimality.py` is in the tree at this head
  ok         tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         tests/stress.py
             `tests/stress.py` is in the tree at this head
  ok         tests/env_drift.py --all
             `tests/env_drift.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 14ed135512e3d7db899081f2c2639ce5674b8f2a
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         dev/audit/harnesses/ceiling_probe.py
             `dev/audit/harnesses/ceiling_probe.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/ceiling_probe.py
             `dev/audit/harnesses/ceiling_probe.py` is in the tree at this head
  ok         python3 tools/audit/seat/features_block.py "# --- R10-CEILING-PROBE (#2498, #2808)"
             `tools/audit/seat/features_block.py` is in the tree at this head
  unverified git grep -n '"system_identification"' -- custom_components/heatpump_optimizer/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n '_step_kw(\|step_duty(\|plan_step_runs(' -- custom_components/heatpump_optimizer/pump_arbiter.py custom_components/heatpump_optimizer/early_cutoff.py
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n '_sysid_step_off_loop\|learner_samples=' -- custom_components/heatpump_optimizer/
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 14 resolved, 12 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.4aad47f0.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.4aad47f0.json
new file mode 100644
index 000000000..5da57da23
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.4aad47f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 4aad47f0",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_OVERDRAWS = 2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_OVERDRAWS = 4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.64815056.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.64815056.json
new file mode 100644
index 000000000..0777810c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.64815056.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 64815056",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_WINDOW = 48",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_WINDOW = 96`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.c9d292c3.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.c9d292c3.json
new file mode 100644
index 000000000..7386fb447
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.c9d292c3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST c9d292c3",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_LAPSE_DAYS = 45.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_LAPSE_DAYS = 90.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.db57fbad.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.db57fbad.json
new file mode 100644
index 000000000..ac2dc8191
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.db57fbad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST db57fbad",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_MIN_SAMPLES = 12",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_MIN_SAMPLES = 24`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.BOOLOP.c78c910d.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.BOOLOP.c78c910d.json
new file mode 100644
index 000000000..e16476457
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.BOOLOP.c78c910d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn BOOLOP c78c910d",
+  "killed_by": "tests/features.py",
+  "old": "        at_ceiling = command is not None and command[0] >= command[1] - CEILING_TOLERANCE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`at_ceiling = command is not None or command[0] >= command[1] - CEILING_TOLERANCE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.18307452.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.18307452.json
new file mode 100644
index 000000000..c47e87d44
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.18307452.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND 18307452",
+  "killed_by": "tests/features.py",
+  "old": "        if not at_ceiling or len(self.ceiling) < CEILING_MIN_SAMPLES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not at_ceiling or len(self.ceiling) <= CEILING_MIN_SAMPLES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c1c89739.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c1c89739.json
new file mode 100644
index 000000000..d26e8d398
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c1c89739.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND c1c89739",
+  "killed_by": "tests/features.py",
+  "old": "        if self.overdraws >= CEILING_OVERDRAWS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if self.overdraws > CEILING_OVERDRAWS:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c78c910d.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c78c910d.json
new file mode 100644
index 000000000..c54a97de8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c78c910d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND c78c910d",
+  "killed_by": "tests/features.py",
+  "old": "        at_ceiling = command is not None and command[0] >= command[1] - CEILING_TOLERANCE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`at_ceiling = command is not None and command[0] > command[1] - CEILING_TOLERANCE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.ea13b93a.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.ea13b93a.json
new file mode 100644
index 000000000..3a724fcb4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.ea13b93a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND ea13b93a",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw > (1.0 + AGREE_TOLERANCE) * self._ceiling_median():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if drawn_kw >= (1.0 + AGREE_TOLERANCE) * self._ceiling_median():`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.18307452.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.18307452.json
new file mode 100644
index 000000000..0d460606c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.18307452.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn GUARD_OFF 18307452",
+  "killed_by": "tests/features.py",
+  "old": "        if not at_ceiling or len(self.ceiling) < CEILING_MIN_SAMPLES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.c1c89739.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.c1c89739.json
new file mode 100644
index 000000000..3f901712b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.c1c89739.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn GUARD_OFF c1c89739",
+  "killed_by": "tests/structure.py",
+  "old": "        if self.overdraws >= CEILING_OVERDRAWS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.ea13b93a.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.ea13b93a.json
new file mode 100644
index 000000000..fd869cf0e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.ea13b93a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn GUARD_OFF ea13b93a",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw > (1.0 + AGREE_TOLERANCE) * self._ceiling_median():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.above_idle_kw.RETURN_DEL.57f929a4.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.above_idle_kw.RETURN_DEL.57f929a4.json
new file mode 100644
index 000000000..7129d0aca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.above_idle_kw.RETURN_DEL.57f929a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.above_idle_kw RETURN_DEL 57f929a4",
+  "killed_by": "tests/features.py",
+  "old": "        return 0.0 if idle is None else IDLE_MARGIN * idle",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.ceiling_since.RETURN_DEL.14a5174b.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.ceiling_since.RETURN_DEL.14a5174b.json
new file mode 100644
index 000000000..0bdfaec88
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.ceiling_since.RETURN_DEL.14a5174b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.ceiling_since RETURN_DEL 14a5174b",
+  "killed_by": "tests/features.py",
+  "old": "        return self.ceiling[-1][1] if self.ceiling else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.36f7cc06.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.36f7cc06.json
new file mode 100644
index 000000000..c7b5655d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.36f7cc06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw CMP_BOUND 36f7cc06",
+  "killed_by": "tests/features.py",
+  "old": "        if len(self.ceiling) < CEILING_MIN_SAMPLES or newest is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(self.ceiling) <= CEILING_MIN_SAMPLES or newest is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.793578eb.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.793578eb.json
new file mode 100644
index 000000000..d268c7882
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.793578eb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw CMP_BOUND 793578eb",
+  "killed_by": "tests/features.py",
+  "old": "        if not 0.0 <= now_s - newest <= CEILING_LAPSE_DAYS * 86400.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not 0.0 < now_s - newest <= CEILING_LAPSE_DAYS * 86400.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.36f7cc06.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.36f7cc06.json
new file mode 100644
index 000000000..ce3b177e8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.36f7cc06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw GUARD_OFF 36f7cc06",
+  "killed_by": "tests/features.py",
+  "old": "        if len(self.ceiling) < CEILING_MIN_SAMPLES or newest is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.793578eb.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.793578eb.json
new file mode 100644
index 000000000..24f972471
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.793578eb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw GUARD_OFF 793578eb",
+  "killed_by": "tests/structure.py",
+  "old": "        if not 0.0 <= now_s - newest <= CEILING_LAPSE_DAYS * 86400.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.RETURN_DEL.1f3a81af.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.RETURN_DEL.1f3a81af.json
new file mode 100644
index 000000000..0142443e0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.RETURN_DEL.1f3a81af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw RETURN_DEL 1f3a81af",
+  "killed_by": "tests/features.py",
+  "old": "        return self._ceiling_median()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.5dfdeab2.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.5dfdeab2.json
new file mode 100644
index 000000000..c4b0b9147
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.5dfdeab2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.takes_ceiling CMP_BOUND 5dfdeab2",
+  "killed_by": "tests/features.py",
+  "old": "            and command.written_c >= command.ceiling_c - CEILING_TOLERANCE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and command.written_c > command.ceiling_c - CEILING_TOLERANCE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.ace88f8a.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.ace88f8a.json
new file mode 100644
index 000000000..f1b5d4a21
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.ace88f8a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.takes_ceiling CMP_BOUND ace88f8a",
+  "killed_by": "tests/features.py",
+  "old": "            and drawn_kw > self.above_idle_kw()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and drawn_kw >= self.above_idle_kw()`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.CMP_BOUND.ef224f84.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.CMP_BOUND.ef224f84.json
new file mode 100644
index 000000000..106bdfb83
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.CMP_BOUND.ef224f84.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_ceiling CMP_BOUND ef224f84",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(drawn) and np.isfinite(when) and drawn > RUNNING_FLOOR_KW:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if np.isfinite(drawn) and np.isfinite(when) and drawn >= RUNNING_FLOOR_KW:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.GUARD_OFF.ef224f84.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.GUARD_OFF.ef224f84.json
new file mode 100644
index 000000000..b0843d4d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.GUARD_OFF.ef224f84.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_ceiling GUARD_OFF ef224f84",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(drawn) and np.isfinite(when) and drawn > RUNNING_FLOOR_KW:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.RETURN_DEL.23640190.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.RETURN_DEL.23640190.json
new file mode 100644
index 000000000..5931520a6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.RETURN_DEL.23640190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_ceiling RETURN_DEL 23640190",
+  "killed_by": "tests/features.py",
+  "old": "    return rows",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.CLAMP_DROP.9ccb0e19.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.CLAMP_DROP.9ccb0e19.json
new file mode 100644
index 000000000..ff66578c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.CLAMP_DROP.9ccb0e19.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_overdraws CLAMP_DROP 9ccb0e19",
+  "killed_by": "tests/features.py",
+  "old": "    return max(raw, 0) if type(raw) is int else 0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (raw) if type(raw) is int else 0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.RETURN_DEL.9ccb0e19.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.RETURN_DEL.9ccb0e19.json
new file mode 100644
index 000000000..c674138b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.RETURN_DEL.9ccb0e19.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_overdraws RETURN_DEL 9ccb0e19",
+  "killed_by": "tests/features.py",
+  "old": "    return max(raw, 0) if type(raw) is int else 0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
new file mode 100644
index 000000000..704b09b3c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold BOOLOP dc29709b",
+  "killed_by": "tests/features.py",
+  "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if experiment_s is not None or draw.takes_ceiling(drawn_kw, command):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
new file mode 100644
index 000000000..33b15211f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF dc29709b",
+  "killed_by": "tests/structure.py",
+  "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.GUARD_OFF.755ef4b5.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.GUARD_OFF.755ef4b5.json
new file mode 100644
index 000000000..4e586a874
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.GUARD_OFF.755ef4b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_experiment_kw GUARD_OFF 755ef4b5",
+  "killed_by": "tests/features.py",
+  "old": "    if action.get(\"mode\") != \"system_identification\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=64."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.RETURN_DEL.cd567d85.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.RETURN_DEL.cd567d85.json
new file mode 100644
index 000000000..089f8a6e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.RETURN_DEL.cd567d85.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_experiment_kw RETURN_DEL cd567d85",
+  "killed_by": "tests/features.py",
+  "old": "    return finite_float(action.get(\"power\")) or 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_command.GUARD_OFF.039fc422.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_command.GUARD_OFF.039fc422.json
new file mode 100644
index 000000000..879a421fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_command.GUARD_OFF.039fc422.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_flow_command GUARD_OFF 039fc422",
+  "killed_by": "tests/features.py",
+  "old": "    if written is None or inp.mode == MODE_OFF or not flow_setpoint_driven(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.44d997bd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.44d997bd.json
deleted file mode 100644
index cdd593b2f..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.44d997bd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_duty GUARD_OFF 44d997bd",
-  "killed_by": "tests/features.py",
-  "old": "    if (inp.action or {}).get(\"mode\") == \"system_identification\":",
-  "reason": "pump-duty arbiter revision; `if (coord._current_action or {}).get(\"mode\") == \"system_identification\":` -> `if False:` fails 1 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Re-measured on a git-archive export of 13a82a9d, 2026-10-05: 3 of 3698 feature checks fail, against the export baseline's two artefacts (#363 recorded_at, R9-F2.1 P3). Re-keyed by R9-EG-B6 (#1739): the collaborator-interface rename made the line `    if (coord._current_action or {}).get(\"mode\") == \"system_identification\":` into `    if (inp.action or {}).get(\"mode\") == \"system_identification\":`."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.be5476ee.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.be5476ee.json
new file mode 100644
index 000000000..1117d710b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.be5476ee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_duty GUARD_OFF be5476ee",
+  "killed_by": "tests/features.py",
+  "old": "    if experiment is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/quiet_windows.py/quiet_reason.RETURN_DEL.76b90284.json b/tests/mutation_ledger/killed_by/quiet_windows.py/quiet_reason.RETURN_DEL.76b90284.json
new file mode 100644
index 000000000..3f953a85d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/quiet_windows.py/quiet_reason.RETURN_DEL.76b90284.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/quiet_windows.py:quiet_reason RETURN_DEL 76b90284",
+  "killed_by": "tests/features.py",
+  "old": "    return {ACTION_OFF: \"inside a quiet off window\", ACTION_SILENT: \"inside a quiet silent window\"}.get(code)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/_sysid_outcome.GUARD_OFF.bc3478fe.json b/tests/mutation_ledger/killed_by/sensor.py/_sysid_outcome.GUARD_OFF.bc3478fe.json
new file mode 100644
index 000000000..cde5bd3d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/_sysid_outcome.GUARD_OFF.bc3478fe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:_sysid_outcome GUARD_OFF bc3478fe",
+  "killed_by": "tests/features.py",
+  "old": "    if not v:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.bb90ed59.json b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.bb90ed59.json
new file mode 100644
index 000000000..800cb0787
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.bb90ed59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:<module> CONST bb90ed59",
+  "killed_by": "tests/features.py",
+  "old": "PROBE_DAYS_UNLEARNED = 7.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROBE_DAYS_UNLEARNED = 14.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.de8e6cf0.json b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.de8e6cf0.json
new file mode 100644
index 000000000..c9eb8bfe5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.de8e6cf0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:<module> CONST de8e6cf0",
+  "killed_by": "tests/features.py",
+  "old": "PROBE_DAYS_LEARNED = 30.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROBE_DAYS_LEARNED = 60.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.e3d1827c.json b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.e3d1827c.json
new file mode 100644
index 000000000..320edcdff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.e3d1827c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:<module> CONST e3d1827c",
+  "killed_by": "tests/features.py",
+  "old": "PROBE_MIN_CYCLES = 2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROBE_MIN_CYCLES = 4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CLAMP_DROP.b1d752e0.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CLAMP_DROP.b1d752e0.json
new file mode 100644
index 000000000..b32665650
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CLAMP_DROP.b1d752e0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase CLAMP_DROP b1d752e0",
+  "killed_by": "tests/features.py",
+  "old": "                max_power_kw * max(cop, 0.1), self.config,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`max_power_kw * (cop), self.config,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.3fa6c8a7.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.3fa6c8a7.json
new file mode 100644
index 000000000..4948ac3cd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.3fa6c8a7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase CMP_BOUND 3fa6c8a7",
+  "killed_by": "tests/features.py",
+  "old": "            and house.ua > 1e-6",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and house.ua >= 1e-6`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.cbebfd71.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.cbebfd71.json
new file mode 100644
index 000000000..a8fd16767
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.cbebfd71.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase CMP_BOUND cbebfd71",
+  "killed_by": "tests/features.py",
+  "old": "            and house.capacity > 1e-6",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and house.capacity >= 1e-6`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.74462097.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.74462097.json
new file mode 100644
index 000000000..85d538823
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.74462097.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase GUARD_OFF 74462097",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.d23aa688.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.d23aa688.json
new file mode 100644
index 000000000..f0eb5ba38
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.d23aa688.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase GUARD_OFF d23aa688",
+  "killed_by": "tests/features.py",
+  "old": "            if hours is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._end_step.GUARD_OFF.74462097.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._end_step.GUARD_OFF.74462097.json
new file mode 100644
index 000000000..447f4322b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._end_step.GUARD_OFF.74462097.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._end_step GUARD_OFF 74462097",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._finish.GUARD_OFF.74462097.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._finish.GUARD_OFF.74462097.json
new file mode 100644
index 000000000..16d1e683f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._finish.GUARD_OFF.74462097.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._finish GUARD_OFF 74462097",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.BOOLOP.7aaadeee.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.BOOLOP.7aaadeee.json
new file mode 100644
index 000000000..f78ad480a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.BOOLOP.7aaadeee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm BOOLOP 7aaadeee",
+  "killed_by": "tests/features.py",
+  "old": "        if plant is not None and kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if plant is not None or kind == KIND_PROBE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=36."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.7aaadeee.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.7aaadeee.json
new file mode 100644
index 000000000..a3e969476
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.7aaadeee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF 7aaadeee",
+  "killed_by": "tests/features.py",
+  "old": "        if plant is not None and kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.cd63f7f7.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.cd63f7f7.json
new file mode 100644
index 000000000..5ba2f1baf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.cd63f7f7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF cd63f7f7",
+  "killed_by": "tests/features.py",
+  "old": "        if kind is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.ee0020d8.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.ee0020d8.json
new file mode 100644
index 000000000..0aa563d7e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.ee0020d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF ee0020d8",
+  "killed_by": "tests/features.py",
+  "old": "        elif plant is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=40."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.RETURN_DEL.7d8da489~3.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.RETURN_DEL.7d8da489~3.json
new file mode 100644
index 000000000..68827b403
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.RETURN_DEL.7d8da489~3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm RETURN_DEL 7d8da489#3",
+  "killed_by": "tests/features.py",
+  "old": "            return False",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.BOOLOP.9a396f27.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.BOOLOP.9a396f27.json
new file mode 100644
index 000000000..5541ac2e7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.BOOLOP.9a396f27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met BOOLOP 9a396f27",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_FIT and learner_samples >= cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.kind == KIND_FIT or learner_samples >= cfg.converged_samples:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.9a396f27.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.9a396f27.json
new file mode 100644
index 000000000..4e4bf6e48
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.9a396f27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met CMP_BOUND 9a396f27",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_FIT and learner_samples >= cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if self.kind == KIND_FIT and learner_samples > cfg.converged_samples:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.e36b992b.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.e36b992b.json
new file mode 100644
index 000000000..86e50ff5f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.e36b992b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met CMP_BOUND e36b992b",
+  "killed_by": "tests/features.py",
+  "old": "            price_horizon is None or not len(price_horizon) or np.ptp(price_horizon) <= 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`price_horizon is None or not len(price_horizon) or np.ptp(price_horizon) < 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.9a396f27.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.9a396f27.json
new file mode 100644
index 000000000..fa1cb15e0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.9a396f27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met GUARD_OFF 9a396f27",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_FIT and learner_samples >= cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.f28ecccb.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.f28ecccb.json
deleted file mode 100644
index cec38bc41..000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.f28ecccb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met GUARD_OFF f28ecccb",
-  "killed_by": "tests/features.py",
-  "old": "        if learner_samples >= cfg.converged_samples:",
-  "reason": "Recorded by `mutation_table.py --drain` against f637d24ab5d17e93cdabba092cd9245f440741f6: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.stand_down.GUARD_OFF.d35c12b9.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.stand_down.GUARD_OFF.d35c12b9.json
new file mode 100644
index 000000000..4957d091e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.stand_down.GUARD_OFF.d35c12b9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.stand_down GUARD_OFF d35c12b9",
+  "killed_by": "tests/features.py",
+  "old": "        if self.phase == PHASE_ARMED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.27c08492.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.27c08492.json
new file mode 100644
index 000000000..a2c4179c8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.27c08492.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step CMP_BOUND 27c08492",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= self._step_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if elapsed > self._step_hours:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.a7d6e527.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.a7d6e527.json
new file mode 100644
index 000000000..fc267b14c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.a7d6e527.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step CMP_BOUND a7d6e527",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= cfg.settle_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if elapsed > cfg.settle_hours:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.27c08492.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.27c08492.json
new file mode 100644
index 000000000..1f5e693c1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.27c08492.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step GUARD_OFF 27c08492",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= self._step_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.a7d6e527.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.a7d6e527.json
new file mode 100644
index 000000000..e11722b69
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.a7d6e527.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step GUARD_OFF a7d6e527",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= cfg.settle_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.160147fc.json b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.160147fc.json
new file mode 100644
index 000000000..c78d487e2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.160147fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable BOOLOP 160147fc",
+  "killed_by": "tests/features.py",
+  "old": "        (t for t in (probe.ceiling_since(), probe_run and probe_run.timestamp()) if t),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`(t for t in (probe.ceiling_since(), probe_run or probe_run.timestamp()) if t),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.55d7d1a6.json b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.55d7d1a6.json
new file mode 100644
index 000000000..8f3cbee38
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.55d7d1a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable BOOLOP 55d7d1a6",
+  "killed_by": "tests/features.py",
+  "old": "    if since is not None and (now.timestamp() - since) / 86400.0 < wait:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if since is not None or (now.timestamp() - since) / 86400.0 < wait:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.14a0382a.json b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.14a0382a.json
new file mode 100644
index 000000000..ed0878102
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.14a0382a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable CMP_BOUND 14a0382a",
+  "killed_by": "tests/features.py",
+  "old": "        if days is None or days >= cfg.min_days_between_runs:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if days is None or days > cfg.min_days_between_runs:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.55d7d1a6.json b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.55d7d1a6.json
new file mode 100644
index 000000000..d2f2a5dfc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.55d7d1a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable CMP_BOUND 55d7d1a6",
+  "killed_by": "tests/features.py",
+  "old": "    if since is not None and (now.timestamp() - since) / 86400.0 < wait:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if since is not None and (now.timestamp() - since) / 86400.0 <= wait:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.9fa5c399.json b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.9fa5c399.json
new file mode 100644
index 000000000..1503571f5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.9fa5c399.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable CMP_BOUND 9fa5c399",
+  "killed_by": "tests/features.py",
+  "old": "    if learner_samples < cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if learner_samples <= cfg.converged_samples:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.14a0382a.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.14a0382a.json
new file mode 100644
index 000000000..7ea77255a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.14a0382a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF 14a0382a",
+  "killed_by": "tests/features.py",
+  "old": "        if days is None or days >= cfg.min_days_between_runs:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.55d7d1a6.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.55d7d1a6.json
new file mode 100644
index 000000000..8cf4f87e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.55d7d1a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF 55d7d1a6",
+  "killed_by": "tests/features.py",
+  "old": "    if since is not None and (now.timestamp() - since) / 86400.0 < wait:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.9fa5c399.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.9fa5c399.json
new file mode 100644
index 000000000..dceebea0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.9fa5c399.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF 9fa5c399",
+  "killed_by": "tests/features.py",
+  "old": "    if learner_samples < cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.c3d7afef.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.c3d7afef.json
new file mode 100644
index 000000000..0d7802b74
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.c3d7afef.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF c3d7afef",
+  "killed_by": "tests/features.py",
+  "old": "    if probe is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.af591f59.json b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.af591f59.json
new file mode 100644
index 000000000..3a03a5c3b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.af591f59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable RETURN_DEL af591f59",
+  "killed_by": "tests/features.py",
+  "old": "        return None, f\"{why}; the ceiling probe ran {days:.1f} days ago, waiting for the {wait:.0f} day minimum\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.f69f5d2a.json b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.f69f5d2a.json
new file mode 100644
index 000000000..f1ec45b5b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.f69f5d2a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable RETURN_DEL f69f5d2a",
+  "killed_by": "tests/features.py",
+  "old": "    return KIND_PROBE, \"\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.CMP_BOUND.dc9c2ceb.json b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.CMP_BOUND.dc9c2ceb.json
new file mode 100644
index 000000000..c7599c41a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.CMP_BOUND.dc9c2ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:probe_step_hours CMP_BOUND dc9c2ceb",
+  "killed_by": "tests/features.py",
+  "old": "        if peak <= bound:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if peak < bound:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.GUARD_OFF.dc9c2ceb.json b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.GUARD_OFF.dc9c2ceb.json
new file mode 100644
index 000000000..5dbb4ead6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.GUARD_OFF.dc9c2ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:probe_step_hours GUARD_OFF dc9c2ceb",
+  "killed_by": "tests/features.py",
+  "old": "        if peak <= bound:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.BOOLOP.039bf6ed.json b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.BOOLOP.039bf6ed.json
new file mode 100644
index 000000000..c41d09e35
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.BOOLOP.039bf6ed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ceiling_probe_install BOOLOP 039bf6ed",
+  "killed_by": "tests/features.py",
+  "old": "    return flow_setpoint_driven(config) and probe_install(config).measured_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return flow_setpoint_driven(config) or probe_install(config).measured_power`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.RETURN_DEL.039bf6ed.json b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.RETURN_DEL.039bf6ed.json
new file mode 100644
index 000000000..c7e3296a2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.RETURN_DEL.039bf6ed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ceiling_probe_install RETURN_DEL 039bf6ed",
+  "killed_by": "tests/features.py",
+  "old": "    return flow_setpoint_driven(config) and probe_install(config).measured_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/survivor_triage/sysid.py/SystemIdentification._begin_step_phase.RETURN_DEL.a9322b69~2.json b/tests/mutation_ledger/survivor_triage/sysid.py/SystemIdentification._begin_step_phase.RETURN_DEL.a9322b69~2.json
deleted file mode 100644
index 2b3b40864..000000000
--- a/tests/mutation_ledger/survivor_triage/sysid.py/SystemIdentification._begin_step_phase.RETURN_DEL.a9322b69~2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase RETURN_DEL a9322b69#2",
-  "old": "                return False",
-  "reason": "R9 F4.2: equivalent. The line follows `self.abort(unadoptable)`, which sets phase PHASE_ABORTED (the method set PHASE_STEP on entry, so abort's `if not self.active` does not skip it). Deleting the return runs only the `injecting` debug log and `return True`; the one caller (SystemIdentification.step's settle branch) returns None on both return values, and the phase is ABORTED either way, so no step is injected and the published result is the abort's. Measured on a copy of the tree with the line replaced by `pass`: the #1524 through R9-P5 blocks of tests/features.py read fails=0, including `R9-P5 (D2-s4-81): a night the noise-free prediction stops never drives the pump above its hold power`, which the abort itself does pin (with the abort replaced by a bare result, that check and the D2-s4-81 check both fail), 2026-09-27.",
-  "verdict": "equivalent"
-}
diff --git a/tests/mutation_ledger/survivor_triage/sysid.py/probe_step_hours.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/survivor_triage/sysid.py/probe_step_hours.RETURN_DEL.da9e8e97.json
new file mode 100644
index 000000000..62d76b791
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/sysid.py/probe_step_hours.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:probe_step_hours RETURN_DEL da9e8e97",
+  "old": "    return None",
+  "reason": "R10-CEILING-PROBE: the last statement of probe_step_hours, after the loop that returns the first fitting duration. Deleting `return None` leaves the function to fall off its end, which returns None: indistinguishable at every input. Measured: the mutant passes all 55 checks of the R10-CEILING-PROBE block of tests/features.py (features_block.py), whose duration-search checks drive the None arm (a house no two-cycle step fits). Kept: the explicit `None` names the refusal arm the docstring states.",
+  "verdict": "equivalent"
+}


## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/accuracy.py b/custom_components/heatpump_optimizer/accuracy.py
index aa71a3969..ee5c77f96 100644
--- a/custom_components/heatpump_optimizer/accuracy.py
+++ b/custom_components/heatpump_optimizer/accuracy.py
@@ -436,7 +436,7 @@ class AccuracyTracker:
             if self.evidence_since is not None
             else {}
         )
-        draw = {"draw": self.draw.as_dict()} if self.draw.samples or self.draw.idle else {}
+        draw = {"draw": self.draw.as_dict()} if self.draw.samples or self.draw.idle or self.draw.ceiling else {}
         return {
             **since,
             **draw,
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 9268c8f1b..9dcfddd6a 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -326,6 +326,7 @@ from .thermal_model import (
     ThermalModel,
     ThermalParameters,
     ThermalState,
+    ceiling_probe_install,
     channel_heating_steps,
     is_sunlit_interval,
     heat_loss_anchor_pair,
@@ -9752,7 +9753,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         # (#2262), within the window the accuracy pairing below trusts; a
         # prediction recording no split, or a dwell that saw hot water, is none.
         if pending is not None and pending.get("split") is not None and pairs_interval(_utc_age_seconds(now, pending["when"]) / 3600.0) and not heat_energy.ran_hot_water(heat_energy.meter_of(self).attribution(pending["split"])):
-            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=power_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"))
+            draw_range.fold(self._accuracy.draw, self._measured_power, pending["split"], ctx._thermal_params, frozen=power_frozen is not None, distorted=_cop_fold_blocked(self), defrost=defrost_window.any_defrost, command=pending.get("flow_command"), experiment_s=pending["when"].timestamp() if pending.get("mode") == "system_identification" else None)
 
         # T5 #16: settle every matured lead-time promise against the same
         # measured temperature the one-step sample below uses. The window
@@ -9848,6 +9849,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "power": self._commanded_power(),
             "split": self._commanded_split(),
             "flow_command": pump_arbiter.flow_command(self),
+            "mode": self._current_action.get("mode"),  # routes draw_range.fold
             "space_power": float(self._current_action.get("power", 0.0)),
             "dhw_power": float(self._current_action.get("dhw_power", 0.0)),
             # T6: why the plan wanted this interval's draw, captured at
@@ -10816,14 +10818,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
 
     async def async_arm_system_identification(self) -> None:
         """Arm a step-response experiment for the next suitable moment."""
-        self._sysid.config.enabled = getattr(self, "_ctx", self)._config.system_identification_enabled
-        if self._sysid.arm(
-            dt_util.now(), plant=getattr(self, "_ctx", self)._thermal_params
-        ):
-            _LOGGER.info(
-                "System identification armed; it will start at the next mild, "
-                "cheap night hour"
-            )
+        ctx = getattr(self, "_ctx", self)
+        self._sysid.config.enabled = ctx._config.system_identification_enabled
+        if self._sysid.arm(dt_util.now(), plant=ctx._thermal_params, learner_samples=self._house_heat_loss_samples,
+                           probe=self._accuracy.draw if ceiling_probe_install(ctx._config) else None):
+            _LOGGER.info("System identification armed (%s) for the next mild, cheap night hour", self._sysid.kind)
         await self.async_request_refresh()
 
     async def _run_system_identification(self, prices: np.ndarray) -> None:
@@ -10837,17 +10836,16 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         ctx = getattr(self, "_ctx", self)
         if not self._sysid.active:
             return
-        # #1523: the experiment is a heat-loss learner, so it stands down on
-        # the house learner's own freeze (external heat, a defrost, an open
-        # window, an unusable or unconfigured room or outdoor reading) and on
-        # a mode that cannot heat. The room half is ``learner_room_unread``.
+        # #1523: a heat-loss learner, it stands down on the house learner's own freeze
+        # (external heat, a defrost, an open window, an unread room or outdoor), on a mode
+        # that cannot heat, and in a quiet window its override would not honour (R10-CEILING-PROBE).
         why = (
             f"heat pump mode {self._pump_signals.mode.label} cannot heat the house"
             if self._pump_signals.space_blocked
             else self._learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY)
-        ) or learner_room_unread(getattr(ctx, "_config", None))
+        ) or learner_room_unread(getattr(ctx, "_config", None)) or quiet_windows.quiet_reason(getattr(ctx, "_config", None) or {}, dt_util.now())
         if why is not None:
-            self._sysid.abort(why)
+            self._sysid.stand_down(why)
             return
         params = ctx._thermal_params
         state = ctx._current_state
diff --git a/custom_components/heatpump_optimizer/diagnostics.py b/custom_components/heatpump_optimizer/diagnostics.py
index a7e5922ff..cb4fe30b2 100644
--- a/custom_components/heatpump_optimizer/diagnostics.py
+++ b/custom_components/heatpump_optimizer/diagnostics.py
@@ -401,7 +401,7 @@ _VIEWS: tuple[tuple[str, Callable[[Any], Any]], ...] = (
     ("early_cutoff", lambda c: early_cutoff.diagnostics_view(early_cutoff.state_for(c))),
     ("draw_range", lambda c: draw_range.diagnostics_view(
         c.accuracy.draw, c.thermal_params,
-        probe_install(c.arbiter_inputs().config))),
+        probe_install(c.arbiter_inputs().config), dt_util.utcnow().timestamp())),
     # Why the observed-COP sensor has nothing yet: it is unavailable then, and
     # Home Assistant hides an unavailable entity's attributes.
     ("cop_learner", lambda c: accuracy.diagnostics_view(c.measured_cop, c.thermal_params, c.accuracy.draw)),
diff --git a/custom_components/heatpump_optimizer/draw_range.py b/custom_components/heatpump_optimizer/draw_range.py
index 7873f4453..125266a5e 100644
--- a/custom_components/heatpump_optimizer/draw_range.py
+++ b/custom_components/heatpump_optimizer/draw_range.py
@@ -85,6 +85,23 @@ IDLE_MARGIN = 1.25
 CEILING_TOLERANCE_K = 0.5
 #: A set-point within this of the gate commanded no heat.
 GATE_TOLERANCE_K = 0.25
+#: The ceiling store (R10-CEILING-PROBE): the draws of intervals the
+#: system-identification experiment commanded at the ceiling set-point. The
+#: window cannot learn the pump's top from them -- a set-point install's plan
+#: rarely writes the ceiling, and a run of them would trip the latch -- so
+#: they are kept apart, and their median is the learned top, published raw.
+#: Whether it agrees with the configured maximum is R10-COP-GATE's to judge.
+CEILING_WINDOW = 48
+#: The learned top waits for this many store samples (three default probe
+#: runs of four step intervals each) ...
+CEILING_MIN_SAMPLES = 12
+#: ... and lapses this many days after the newest, so a mild-night top is
+#: re-measured rather than kept into a cold season.
+CEILING_LAPSE_DAYS = 45.0
+#: An ordinary interval written at the ceiling that draws more than
+#: AGREE_TOLERANCE above the learned top is an overdraw; this many since the
+#: store's newest sample drop the store: the pump has shown it draws more.
+CEILING_OVERDRAWS = 2
 
 
 @dataclass
@@ -117,11 +134,76 @@ class DrawRange:
     commands_known: bool = True
     #: Metered draw while the held set-point was the gate, oldest first.
     idle: Deque[float] = field(default_factory=lambda: deque(maxlen=IDLE_WINDOW))
+    #: ``(drawn_kw, epoch_s)`` per ceiling-store sample, oldest first: one
+    #: interval the experiment commanded at the ceiling. The timestamps are
+    #: the run delimiter and the probe's persisted clock. Not keyed to
+    #: ``config``: the store meters the pump at the ceiling set-point, which
+    #: the configured power range does not set, so a reconfiguration keeps it.
+    ceiling: Deque[tuple[float, float]] = field(
+        default_factory=lambda: deque(maxlen=CEILING_WINDOW)
+    )
+    #: Overdraws of the learned top since the store's newest sample.
+    overdraws: int = 0
 
     def idle_kw(self) -> float | None:
         """The learned idle draw, or ``None`` while too few readings."""
         return float(np.median(self.idle)) if len(self.idle) >= MIN_IDLE else None
 
+    def above_idle_kw(self) -> float:
+        """A draw at or below this is the idle draw: no evidence."""
+        idle = self.idle_kw()
+        return 0.0 if idle is None else IDLE_MARGIN * idle
+
+    def ceiling_since(self) -> float | None:
+        """The newest ceiling-store sample's epoch seconds, or ``None``."""
+        return self.ceiling[-1][1] if self.ceiling else None
+
+    def learned_max_kw(self, now_s: float) -> float | None:
+        """The ceiling store's median draw, kW: the learned top, raw.
+
+        ``None`` below ``CEILING_MIN_SAMPLES`` samples, past
+        ``CEILING_LAPSE_DAYS`` after the newest, or with the newest ahead of
+        ``now_s``. No comparison with the configured maximum: that ruling is
+        R10-COP-GATE's, so its reason can tell a top that agrees from a store
+        still waiting for samples. Every sample counts once, whichever run
+        took it.
+        """
+        newest = self.ceiling_since()
+        if len(self.ceiling) < CEILING_MIN_SAMPLES or newest is None:
+            return None
+        if not 0.0 <= now_s - newest <= CEILING_LAPSE_DAYS * 86400.0:
+            return None  # lapsed, or stamped ahead of the clock: age unknowable
+        return self._ceiling_median()
+
+    def _ceiling_median(self) -> float:
+        return float(np.median([d for d, _ in self.ceiling]))
+
+    def takes_ceiling(self, drawn_kw: float, command: Any) -> bool:
+        """An experiment's interval is store evidence: the ceiling written
+        (``command``, a ``pump_arbiter.FlowCommand``), and the compressor
+        running above the idle draw."""
+        return (
+            command is not None
+            and command.written_c >= command.ceiling_c - CEILING_TOLERANCE_K
+            and drawn_kw > self.above_idle_kw()
+        )
+
+    def observe_ceiling(self, drawn_kw: float, when_s: float) -> None:
+        """Fold one ceiling-commanded experiment interval into the store."""
+        self.ceiling.append((float(drawn_kw), float(when_s)))
+        self.overdraws = 0
+
+    def _overdrawn(self, drawn_kw: float, command: tuple[float, float] | None) -> None:
+        """Count an ordinary ceiling-written draw above the learned top."""
+        at_ceiling = command is not None and command[0] >= command[1] - CEILING_TOLERANCE_K
+        if not at_ceiling or len(self.ceiling) < CEILING_MIN_SAMPLES:
+            return
+        if drawn_kw > (1.0 + AGREE_TOLERANCE) * self._ceiling_median():
+            self.overdraws += 1
+        if self.overdraws >= CEILING_OVERDRAWS:
+            self.ceiling.clear()
+            self.overdraws = 0
+
     def _evidence(self) -> list[tuple[float, float, bool]]:
         """``(drawn, asked, full)`` per sample that is the compressor running.
 
@@ -132,8 +214,7 @@ class DrawRange:
         BOOST), so a draw under one says nothing about the pump's maximum: the
         window would otherwise learn the set-points it was written.
         """
-        idle = self.idle_kw()
-        above = 0.0 if idle is None else IDLE_MARGIN * idle
+        above = self.above_idle_kw()
         return [
             (d, a, cmd is None or cmd[0] >= cmd[1] - CEILING_TOLERANCE_K)
             for (d, a), cmd in zip(self.samples, self._aligned())
@@ -207,6 +288,7 @@ class DrawRange:
         self.commands_known = True
         self.samples.append((float(drawn_kw), float(asked_kw)))
         self.commands.append(command)
+        self._overdrawn(float(drawn_kw), command)
         if self._disagrees(cfg_min):
             self.engaged = True
 
@@ -234,6 +316,7 @@ class DrawRange:
             "observed_max_kw": None if seen is None or seen[1] is None else round(seen[1], 3),
             "idle_kw": None if (idle := self.idle_kw()) is None else round(idle, 3),
             "engaged": self.engaged,
+            "ceiling_samples": len(self.ceiling),
         }
 
     def as_dict(self) -> dict[str, Any]:
@@ -244,20 +327,26 @@ class DrawRange:
         return {
             "samples": rows if self.commands_known else [r[:2] for r in rows],
             "engaged": self.engaged,
-            "config": None if self.config is None else list(self.config),
+            # Absent, not null, on a store-only record: nothing keyed it yet.
+            **({} if self.config is None else {"config": list(self.config)}),
             "idle": [round(v, 3) for v in self.idle],
+            "ceiling": [[round(d, 3), t] for d, t in self.ceiling],
+            "overdraws": self.overdraws,
         }
 
     @classmethod
     def from_dict(cls, data: Any) -> "DrawRange":
         """A stored range; an unreadable sample is dropped, not the record.
 
-        The configuration is the record's key: samples and latch are judged
-        against it, so without a readable one the record is dropped whole and
-        the evidence starts afresh -- never samples with nothing to judge them
-        against, which a reader of ``samples`` alone would misjudge.
+        The configuration is the window's key: samples and latch are judged
+        against it, so without a readable one they are dropped and the
+        evidence starts afresh -- never samples with nothing to judge them
+        against, which a reader of ``samples`` alone would misjudge. The
+        ceiling store is not keyed to it, and is kept.
         """
         out = cls()
+        out.ceiling.extend(_stored_ceiling(data))
+        out.overdraws = _stored_overdraws(data)
         try:
             lo, hi = (float(v) for v in data["config"])
         except (TypeError, ValueError, OverflowError, KeyError, IndexError):
@@ -335,6 +424,26 @@ def _stored_idle(raw: Any) -> list[float]:
     ]
 
 
+def _stored_ceiling(data: Any) -> list[tuple[float, float]]:
+    """The readable ceiling-store rows of a stored record; a bad one is dropped."""
+    raw = data.get("ceiling") if isinstance(data, dict) else None
+    rows = []
+    for entry in raw if isinstance(raw, list) else ():
+        try:
+            drawn, when = float(entry[0]), float(entry[1])
+        except (TypeError, ValueError, OverflowError, IndexError, KeyError):
+            continue
+        if np.isfinite(drawn) and np.isfinite(when) and drawn > RUNNING_FLOOR_KW:
+            rows.append((drawn, when))
+    return rows
+
+
+def _stored_overdraws(data: Any) -> int:
+    """A stored record's overdraw count; anything but a count reads 0."""
+    raw = data.get("overdraws") if isinstance(data, dict) else None
+    return max(raw, 0) if type(raw) is int else 0
+
+
 def _command_cells(entry: Any) -> tuple[float, float] | None:
     """A stored row's ``(written_c, ceiling_c)``, or ``None``."""
     try:
@@ -413,6 +522,7 @@ def fold(
     distorted: bool,
     defrost: bool,
     command: Any = None,
+    experiment_s: float | None = None,
 ) -> None:
     """Fold one interval into ``draw`` when it is a running sample.
 
@@ -422,13 +532,25 @@ def fold(
     (``pump_arbiter.flow_command``: ``written_c``, ``gate_c``,
     ``ceiling_c``), or ``None`` where nothing commands the draw. An interval
     held at the gate with no hot water asked is an idle reading.
+
+    ``experiment_s`` is the interval's start, epoch seconds, where the
+    system-identification experiment commanded it -- the mode the interval's
+    own action carried, captured beside its split and command, never the
+    action adopted since -- else ``None``. Such an interval that
+    ``takes_ceiling`` goes to the ceiling store and NOT to the window, so no
+    experiment's draw can trip the window's latch; every other interval
+    folds into the window as before.
     """
     space, dhw = split
     if drawn_kw is not None and not (frozen or distorted or defrost) and command is not None and command.written_c <= command.gate_c + GATE_TOLERANCE_K and not planned_draw_runs(dhw, modulation_floor=0.0):
         draw.observe_idle(drawn_kw)
-    if drawn_kw is not None and is_running_space(
+    if drawn_kw is None or not is_running_space(
         drawn_kw, space, dhw, frozen=frozen, distorted=distorted, defrost=defrost
     ):
+        return
+    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):
+        draw.observe_ceiling(drawn_kw, experiment_s)
+    else:
         draw.observe(
             drawn_kw, space, params.min_electrical_power, params.max_electrical_power,
             None if command is None else (command.written_c, command.ceiling_c),
@@ -462,11 +584,14 @@ def planned_range(
 
 
 def diagnostics_view(
-    draw: DrawRange, params: Any, cap: InstallCapability
+    draw: DrawRange, params: Any, cap: InstallCapability, now_s: float
 ) -> dict[str, Any]:
-    """The learned values and the range they would clamp the plan to."""
+    """The learned values, the range they would clamp the plan to, and the
+    ceiling store's learned top beside it (outside the latch)."""
     view = draw.summary()
     effective = planned_range(draw, params, cap)
+    learned = draw.learned_max_kw(now_s)
     view["effective_min_kw"] = None if effective is None else round(effective[0], 3)
     view["effective_max_kw"] = None if effective is None else round(effective[1], 3)
+    view["learned_max_kw"] = None if learned is None else round(learned, 3)
     return view
diff --git a/custom_components/heatpump_optimizer/payload.py b/custom_components/heatpump_optimizer/payload.py
index eae89d29f..5d9a01055 100644
--- a/custom_components/heatpump_optimizer/payload.py
+++ b/custom_components/heatpump_optimizer/payload.py
@@ -557,6 +557,11 @@ class SysIdView(TypedDict, total=False):
     active: bool
     samples: int
     last_run: str | None
+    # R10-CEILING-PROBE / #2808: the armed kind ("fit" or "ceiling_probe"),
+    # a learners' freeze holding the armed run, and the last arm press.
+    kind: str
+    held: str | None
+    last_attempt: str | None
     result: SysIdResultView
 
 
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index 28e1f706e..be370a0a2 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -171,12 +171,12 @@ from .drift import stored_instant
 from .store import QuarantiningStore, load_mapping
 from .thermal_model import (
     configured_flow_heat_c,
+    flow_setpoint_driven,
     flow_setpoint_for_level,
     modulation_floor_flow_c,
     on_threshold_kw,
     plan_step_runs,
     planned_draw_runs,
-    probe_install,
 )
 
 _LOGGER = logging.getLogger(__name__)
@@ -484,6 +484,21 @@ def _step_kw(result: Any, now: datetime) -> float | None:
     return finite_float(_planned_room(result, now, "power_schedule"))
 
 
+def _experiment_kw(inp: ArbiterInputs) -> float | None:
+    """The system-identification experiment's commanded space power, or
+    ``None`` when the action is not the experiment's.
+
+    The experiment overrides the action, not the plan (``coordinator.
+    _run_system_identification``), so its step -- the fit's sized level or
+    the ceiling probe's configured maximum -- is read here, before the plan's
+    ``power_schedule`` is consulted, or the plan's level would win.
+    """
+    action = inp.action or {}
+    if action.get("mode") != "system_identification":
+        return None
+    return finite_float(action.get("power")) or 0.0
+
+
 def _band_kw(inp: ArbiterInputs) -> tuple[Any, Any]:
     """``(p_min, p_max)`` from the model when the params snapshot lacks them."""
     params = inp.params
@@ -602,11 +617,7 @@ def _flow_command(inp: ArbiterInputs, state: Any) -> FlowCommand | None:
     censoring guard keys on.
     """
     written = state.written.get("space_setpoint")
-    if (
-        written is None or inp.mode == MODE_OFF or not _flow_unit(inp.config)
-        or duty_mode(inp.config) != DUTY_CONTROL
-        or probe_install(inp.config).plan_writes_power()
-    ):
+    if written is None or inp.mode == MODE_OFF or not flow_setpoint_driven(inp.config):
         return None
     gate = _gate_c(inp)
     ceiling = _bounded(
@@ -646,7 +657,10 @@ def _flow_target(inp: ArbiterInputs, duty: str | None, now: datetime) -> float |
         return _bounded(
             inp,
             "space_setpoint",
-            flow_setpoint_for_level(_step_kw(inp.plan, now), p_min, p_max, heat_c, floor_c),
+            flow_setpoint_for_level(
+                _step_kw(inp.plan, now) if (kw := _experiment_kw(inp)) is None else kw,
+                p_min, p_max, heat_c, floor_c,
+            ),
             FLOW_GATE_C,
             lo=min(floor_c, heat_c),
             hi=heat_c,
@@ -771,8 +785,12 @@ def _planned_duty(coord: Any, inp: ArbiterInputs, now: datetime) -> str | None:
         return "both"
     if inp.mode not in (MODE_AUTO, MODE_ECONOMY):
         return None
-    if (inp.action or {}).get("mode") == "system_identification":
-        return None
+    experiment = _experiment_kw(inp)
+    if experiment is not None:
+        # The experiment's own step, by the rule that books its
+        # ``heat_pump_on``: heating while it injects, the gate while it does
+        # not. Space only -- a hot-water charge would share the meter.
+        return "space" if planned_draw_runs(experiment) else "idle"
     held = boost.held_for(coord)
     result = None if inp.plan_stale else inp.plan
     duty = None if result is None else step_duty(result, now)
diff --git a/custom_components/heatpump_optimizer/quiet_windows.py b/custom_components/heatpump_optimizer/quiet_windows.py
index 724970592..92c636840 100644
--- a/custom_components/heatpump_optimizer/quiet_windows.py
+++ b/custom_components/heatpump_optimizer/quiet_windows.py
@@ -83,6 +83,7 @@ from .dhw_schedule import (
 from .inputs import state_power_kw
 from .modbus_prefill import night_mode_write_ids, package_prefix
 from .drift import utc_step_starts
+from .plan_step import PLAN_STEP_HOURS, plan_step_start
 
 #: The per-step action codes, as one int8 array element per step.
 ACTION_NONE: Final = 0
@@ -151,6 +152,21 @@ def step_actions(
     return out if bool(np.any(out)) else None
 
 
+def quiet_reason(config: Mapping[str, Any], now: datetime) -> str | None:
+    """Why the step covering ``now`` is inside a configured quiet window, or ``None``.
+
+    The solve honours the windows (``off_steps``, the silent cap); an action
+    that replaces the solve's -- the system-identification experiment's step
+    -- would not, so the experiment stands down inside one (R10-CEILING-PROBE).
+    """
+    actions = step_actions(
+        plan_step_start(now), 1, PLAN_STEP_HOURS,
+        config.get(CONF_QUIET_SILENT_WINDOWS), config.get(CONF_QUIET_OFF_WINDOWS),
+    )
+    code = ACTION_NONE if actions is None else int(actions[0])
+    return {ACTION_OFF: "inside a quiet off window", ACTION_SILENT: "inside a quiet silent window"}.get(code)
+
+
 def silent_control_usable(entity_id: Any) -> bool:
     """Whether the optimizer can hold a silent window through ``entity_id``.
 
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index 55e54f1ca..e477c2bc0 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -2042,10 +2042,27 @@ class ModelStatusSensor(HeatPumpOptimizerSensorBase):
             "internal_gains_kw": data.get("internal_gains_profile"),
             "capacity_envelope": _mapping(data.get("capacity_envelope")).get("buckets"),
             "system_identification": data.get("system_identification"),
+            "system_identification_outcome": _sysid_outcome(data.get("system_identification")),
             "learner_progress": data.get("learner_progress"),
         }
 
 
+def _sysid_outcome(view: Any) -> dict[str, Any] | None:
+    """The experiment's outcome, compact enough to record (#2808).
+
+    The kind armed, its phase, a freeze holding it, the result's reason and
+    the last arm press: the bulky view beside it stays unrecorded, so without
+    this row no history says why an arm was refused or what a run did.
+    """
+    v = _mapping(view)
+    if not v:
+        return None
+    return {
+        "kind": v.get("kind"), "phase": v.get("phase"), "held": v.get("held"),
+        "reason": _mapping(v.get("result")).get("reason"), "last_attempt": v.get("last_attempt"),
+    }
+
+
 # ---------------------------------------------------------------------------
 # Capacity tariff (item 8)
 # ---------------------------------------------------------------------------
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index 706aea6d1..835b23ba4 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -279,6 +279,8 @@ _RESTATED = "ledger.restate_total re-derives them from the receipt's own lines o
 _DHW_INTENSITY = Domain("real", 0.0, 3.5, whole=_PROFILE)
 
 _DRAW_KEY = "the configuration keys the record: unreadable, the samples and the latch are dropped with it"
+#: A metered running draw: one at or below standby is not a running one, and is dropped.
+_RUNNING_KW = Domain("real", math.nextafter(RUNNING_FLOOR_KW, math.inf))
 
 _ACCURACY: dict[str, Domain | str] = {
     "samples/#/t": _AT, "samples/#/predicted_power_kw": Domain("real", 0.0, null=True),
@@ -300,15 +302,19 @@ _ACCURACY: dict[str, Domain | str] = {
     # R9-UX-6: the plan's day-ahead promise per local date (plan_promise).
     "promises/~": _DAY, "promises/*/start": _AT, "promises/*/step_minutes": Domain("real", _POS),
     "promises/*/room/#": _R, "promises/*/cost/#": _R,
-    # The metered running draw beside the space level asked (draw_range):
-    # a sample at or below standby is not a running one, and is dropped.
-    "draw/samples/#/0": Domain("real", math.nextafter(RUNNING_FLOOR_KW, math.inf)),
+    # The metered running draw beside the space level asked (draw_range).
+    "draw/samples/#/0": _RUNNING_KW,
     "draw/samples/#/1": _Z,
     # R10-SETPOINT-BOOST: the flow set-point held and its ceiling, null where
     # nothing commanded the draw; and the readings taken at the gate.
     "draw/samples/#/2": _N,
     "draw/samples/#/3": _N,
     "draw/idle/#": _Z,
+    # R10-CEILING-PROBE: the experiment's ceiling-commanded draws, each beside
+    # its interval's start in epoch seconds, and the overdraws since.
+    "draw/ceiling/#/0": _RUNNING_KW,
+    "draw/ceiling/#/1": _R,
+    "draw/overdraws": _COUNT,
     "draw/engaged": Domain("flag", whole=_DRAW_KEY),
     "draw/config/#": Domain("real", whole=_DRAW_KEY),
 }
diff --git a/custom_components/heatpump_optimizer/sysid.py b/custom_components/heatpump_optimizer/sysid.py
index 0bbb41bca..ea1ead336 100644
--- a/custom_components/heatpump_optimizer/sysid.py
+++ b/custom_components/heatpump_optimizer/sysid.py
@@ -30,12 +30,17 @@ import logging
 import math
 from dataclasses import dataclass, replace
 from datetime import datetime
-from typing import Any, Callable
+from typing import Any, Callable, cast
 
 import numpy as np
 
 from .accuracy import utc_elapsed_seconds
-from .const import DEFAULT_SLAB_HEAT_TRANSFER, DEFAULT_SLAB_THERMAL_MASS
+from .const import (
+    DEFAULT_OPTIMIZATION_INTERVAL,
+    DEFAULT_SLAB_HEAT_TRANSFER,
+    DEFAULT_SLAB_THERMAL_MASS,
+)
+from .draw_range import DrawRange
 from .mixing_valve import is_throttling
 from .payload import SysIdResultView, SysIdView
 from .thermal_model import (
@@ -84,6 +89,19 @@ TWO_ZONE_SIZING_HEADROOM_C = 0.05
 #: the comfort promise and does not move.
 SIZING_NOISE_HEADROOM_C = 0.15
 
+#: The two experiments an arm can run (R10-CEILING-PROBE, #2808). The fit
+#: steps a sized heat into the house and identifies it; the ceiling probe
+#: commands the configured maximum, so a flow set-point install writes its
+#: ceiling and the meter reads the pump's real top into
+#: ``draw_range.DrawRange.ceiling``. The probe fits and adopts nothing.
+KIND_FIT = "fit"
+KIND_PROBE = "ceiling_probe"
+#: Days between probes while the store has no learned top, and once it has.
+PROBE_DAYS_UNLEARNED = 7.0
+PROBE_DAYS_LEARNED = 30.0
+#: A probe step shorter than this many cycles meters too few intervals.
+PROBE_MIN_CYCLES = 2
+
 
 def _predict_step_excursion(
     baseline: float,
@@ -400,6 +418,11 @@ class SysIdSample:
     identified parameters by the COP, and the error would look entirely
     plausible because the ratio between them — the time constant — stays
     correct.
+
+    A step sample books the heat COMMANDED for the interval that begins at
+    ``when`` -- the override the same ``step`` call returns governs it -- not
+    a metered draw: the meter's reading of that interval closes it a cycle
+    later, and reaches ``draw_range.fold`` (R10-CEILING-PROBE item 10).
     """
 
     when: datetime
@@ -1266,6 +1289,72 @@ def night_gains_prior_kw(plant: ThermalParameters, config: SysIdConfig) -> float
     ]))
 
 
+def armable(
+    cfg: SysIdConfig,
+    now: datetime,
+    last_run: datetime | None,
+    learner_samples: int,
+    probe: DrawRange | None,
+    probe_run: datetime | None,
+) -> tuple[str | None, str]:
+    """The kind one arm runs now, or ``None`` and why none can (#2808).
+
+    The fit while the house learner is unconverged and its own clock allows;
+    otherwise the ceiling probe, where the install can run one (``probe`` is
+    its draw store) and the probe's clock allows. The probe's clock is the
+    store's newest sample, which persists, or the probe step's start this
+    process saw (``probe_run``), whichever is newer.
+    """
+    if learner_samples < cfg.converged_samples:
+        days = None if last_run is None else utc_elapsed_seconds(now, last_run) / 86400.0
+        if days is None or days >= cfg.min_days_between_runs:
+            return KIND_FIT, ""
+        why = f"ran {days:.1f} days ago; waiting for the {cfg.min_days_between_runs:.0f} day minimum"
+    else:
+        why = "house already converged"
+    if probe is None:
+        return None, f"{why}, and no metered flow set-point to probe the ceiling on"
+    wait = PROBE_DAYS_LEARNED if probe.learned_max_kw(now.timestamp()) is not None else PROBE_DAYS_UNLEARNED
+    since = max(
+        (t for t in (probe.ceiling_since(), probe_run and probe_run.timestamp()) if t),
+        default=None,
+    )
+    if since is not None and (now.timestamp() - since) / 86400.0 < wait:
+        days = (now.timestamp() - since) / 86400.0
+        return None, f"{why}; the ceiling probe ran {days:.1f} days ago, waiting for the {wait:.0f} day minimum"
+    return KIND_PROBE, ""
+
+
+def probe_step_hours(
+    house: HousePlant,
+    two_zone: ThermalParameters | None,
+    baseline: float,
+    outdoor: float,
+    q_kw: float,
+    cfg: SysIdConfig,
+) -> float | None:
+    """The longest probe step, in whole cycles up to ``cfg.step_hours``,
+    whose predicted peak stays inside the comfort bound; ``None`` below
+    ``PROBE_MIN_CYCLES`` cycles.
+
+    ``q_kw`` is the thermal heat at the configured maximum. The bound is the
+    fit's less only the two-zone headroom: the probe fits nothing, so the
+    sensor-noise headroom the fit subtracts (``SIZING_NOISE_HEADROOM_C``) has
+    no noise to absorb. The peak includes the relax phase's overshoot; the
+    relax's final cooling is the plan's, which resumes after a probe.
+    """
+    cycle = DEFAULT_OPTIMIZATION_INTERVAL / 60.0
+    bound = cfg.max_excursion_c - (0.0 if two_zone is None else TWO_ZONE_SIZING_HEADROOM_C)
+    model = None if two_zone is None else ThermalModel(two_zone)
+    for n in range(int(cfg.step_hours / cycle + 1e-9), PROBE_MIN_CYCLES - 1, -1):
+        peak, _ = _predict_step_excursion_plant(
+            house, baseline, outdoor, q_kw, n * cycle, cfg.relax_hours, model=model,
+        )
+        if peak <= bound:
+            return n * cycle
+    return None
+
+
 def step_detached(
     experiment: "SystemIdentification", kwargs: dict[str, Any]
 ) -> tuple[dict[str, Any], float | None]:
@@ -1292,6 +1381,13 @@ class SystemIdentification:
         self.result: SysIdResult = SysIdResult()
         self._baseline_temp: float | None = None
         self._step_power: float = 0.0
+        #: The armed kind; its step length (a probe's is searched); the probe
+        #: step's last start; the last arm press; a freeze's hold (#2808).
+        self.kind: str = KIND_FIT
+        self._step_hours: float = self.config.step_hours
+        self.probe_run: datetime | None = None
+        self.last_attempt: datetime | None = None
+        self.held: str | None = None
         #: Slab pair (C_s, k_s) and initial-guess room pair (UA, C_r) from
         #: the plant declared at arm time, recorded ONLY when the #991
         #: identifiability gate passed on it. ``_finish`` routes the
@@ -1313,9 +1409,16 @@ class SystemIdentification:
     def active(self) -> bool:
         return self.phase in (PHASE_ARMED, PHASE_SETTLING, PHASE_STEP, PHASE_RELAX)
 
-    def arm(self, now: datetime, plant: ThermalParameters | None = None) -> bool:
+    def arm(
+        self, now: datetime, plant: ThermalParameters | None = None,
+        learner_samples: int = 0, probe: DrawRange | None = None,
+    ) -> bool:
         """Arm an experiment, to start when conditions allow.
 
+        :func:`armable` picks the kind; a refusal is published in ``result``.
+        ``probe`` is the install's draw store where it can run the ceiling
+        probe (``thermal_model.ceiling_probe_install``), else ``None``.
+
         ``plant`` is the house the experiment would run on, when the caller
         knows it. #942's identifiability gate then refuses to arm on a plant
         whose slab mode is too slow for the excitation window — naming the
@@ -1329,11 +1432,20 @@ class SystemIdentification:
             return False
         if self.active:
             return False
+        self.last_attempt, self.held = now, None
+        kind, why = armable(self.config, now, self.last_run, learner_samples, probe, self.probe_run)
+        if kind is None:
+            _LOGGER.info("System identification not armed: %s", why)
+            self.result = SysIdResult(completed=False, reason=why)
+            return False
+        self.kind, self._step_hours = kind, self.config.step_hours
         self._slab_pair = None
         self._slab_prior = None
         self._slab_fit_used = False
         self._two_zone_plant = None
-        if plant is not None:
+        if plant is not None and kind == KIND_PROBE:
+            self._two_zone_plant = replace(plant) if plant.two_zone_enabled else None
+        elif plant is not None:
             identifiable, why = slab_mode_identifiability(plant, self.config)
             if not identifiable:
                 _LOGGER.info("System identification not armed: %s", why)
@@ -1362,16 +1474,6 @@ class SystemIdentification:
                     _zone_heat_loss(plant) * float(plant.house_heat_loss_scale),
                     float(plant.upper_floor_thermal_mass + plant.lower_floor_thermal_mass),
                 )
-        if self.last_run is not None:
-            days = utc_elapsed_seconds(now, self.last_run) / 86400.0
-            if days < self.config.min_days_between_runs:
-                _LOGGER.info(
-                    "System identification ran %.1f days ago; waiting for the "
-                    "%.0f day minimum",
-                    days,
-                    self.config.min_days_between_runs,
-                )
-                return False
         self.phase = PHASE_ARMED
         self.phase_started = now
         self.samples = []
@@ -1384,6 +1486,14 @@ class SystemIdentification:
         self.phase = PHASE_ABORTED
         self.result = SysIdResult(completed=False, reason=reason)
 
+    def stand_down(self, reason: str) -> None:
+        """The learners' freeze: a started experiment aborts, since its
+        interval's heat cannot be attributed; an armed one waits, held."""
+        if self.phase == PHASE_ARMED:
+            self.held = reason
+        else:
+            self.abort(reason)
+
     # -- gating -------------------------------------------------------------
 
     def conditions_met(
@@ -1398,7 +1508,7 @@ class SystemIdentification:
         cfg = self.config
         if price is None:  # no published price covers now (#2229)
             return False, "no current electricity price"
-        if learner_samples >= cfg.converged_samples:
+        if self.kind == KIND_FIT and learner_samples >= cfg.converged_samples:
             return False, "house already converged"
         if not (cfg.min_outdoor_temp <= outdoor_temp <= cfg.max_outdoor_temp):
             return False, "outdoor temperature outside the safe band"
@@ -1412,6 +1522,10 @@ class SystemIdentification:
         if not in_window:
             return False, "outside the night window"
 
+        if self.kind == KIND_PROBE and (
+            price_horizon is None or not len(price_horizon) or np.ptp(price_horizon) <= 0.0
+        ):
+            return False, "a flat price has no cheap hour to probe in"
         if price_horizon is not None and len(price_horizon):
             cutoff = float(np.percentile(price_horizon, cfg.max_price_percentile))
             if price > cutoff:
@@ -1421,39 +1535,28 @@ class SystemIdentification:
     # -- execution ----------------------------------------------------------
 
     def _size_step_power(
-        self,
-        max_power_kw: float,
-        cop: float,
-        baseline: float,
-        outdoor_temp: float,
-        ua: float,
-        capacity: float,
-        gains: float,
-        slab_thermal_mass: float | None = None,
-        slab_heat_transfer: float | None = None,
+        self, max_power_kw: float, cop: float, baseline: float, outdoor_temp: float, house: HousePlant,
     ) -> float | None:
-        """Largest electrical step whose predicted excursion fits the bound."""
+        """Largest electrical step whose predicted excursion fits the bound.
+
+        ``house`` carries ``ua``, ``capacity`` and ``gains`` concretely.
+        """
         cfg = self.config
         cop = max(cop, 0.1)
         q_max = max_power_kw * cop
         # 0.01 kW thermal: the C=8 UA=0.35 kW/K needle is ~0.05 kW wide.
         # Binary search: each trial is a two-state rollout, not a closed form.
         best: float | None = None
+        ua, capacity, gains = cast("tuple[float, float, float]", (house.ua, house.capacity, house.gains))
         plant = (
-            _sizing_model(ua, capacity, gains, slab_thermal_mass, slab_heat_transfer)
+            _sizing_model(ua, capacity, gains, house.slab_mass, house.slab_transfer)
             if self._two_zone_plant is None
             else ThermalModel(self._two_zone_plant)
         )
-
         full = cfg.max_excursion_c - (
             0.0 if self._two_zone_plant is None else TWO_ZONE_SIZING_HEADROOM_C
         )
 
-        house = HousePlant(
-            ua=ua, capacity=capacity, gains=gains,
-            slab_mass=slab_thermal_mass, slab_transfer=slab_heat_transfer,
-        )
-
         def fits(q: float, bound: float) -> bool:
             peak, final = _predict_step_excursion_plant(
                 house, baseline, outdoor_temp, q,
@@ -1494,20 +1597,11 @@ class SystemIdentification:
                 break
         if best is not None:
             one_peak, _ = _predict_step_excursion(
-                baseline,
-                outdoor_temp,
-                ua,
-                capacity,
-                gains,
-                best * cop,
-                cfg.step_hours,
-                cfg.relax_hours,
+                baseline, outdoor_temp, ua, capacity, gains, best * cop, cfg.step_hours, cfg.relax_hours,
             )
             _LOGGER.debug(
                 "System identification sizer: two-state step %.2f kW; "
-                "one-state exponential predicted %.2f K",
-                best,
-                one_peak,
+                "one-state exponential predicted %.2f K", best, one_peak,
             )
         return best
 
@@ -1519,60 +1613,53 @@ class SystemIdentification:
         )
 
     def _begin_step_phase(
-        self,
-        now: datetime,
-        outdoor_temp: float,
-        max_power_kw: float,
-        cop: float,
-        house_ua: float | None,
-        house_capacity: float | None,
-        house_gains: float | None,
-        house_slab_mass: float | None = None,
-        house_slab_transfer: float | None = None,
-    ) -> bool:
-        """Enter PHASE_STEP with a comfort-bounded injection. False if none fits."""
+        self, now: datetime, outdoor_temp: float, max_power_kw: float, cop: float, house: HousePlant,
+    ) -> None:
+        """Enter PHASE_STEP with a comfort-bounded injection; abort if none fits.
+
+        A probe steps the configured maximum for the longest whole-cycle
+        duration that fits (:func:`probe_step_hours`); the fit sizes its power.
+        """
         self.phase = PHASE_STEP
         self.phase_started = now
+        if self.kind == KIND_PROBE:
+            hours = None if self._baseline_temp is None else probe_step_hours(
+                house, self._two_zone_plant, self._baseline_temp, outdoor_temp,
+                max_power_kw * max(cop, 0.1), self.config,
+            )
+            if hours is None:
+                self.abort("no probe step of two cycles fits within the comfort bound")
+                return
+            self._step_power, self._step_hours, self.probe_run = max_power_kw, hours, now
+            return
         if (
-            house_ua is not None
-            and house_capacity is not None
-            and house_gains is not None
-            and house_ua > 1e-6
-            and house_capacity > 1e-6
+            house.ua is not None
+            and house.capacity is not None
+            and house.gains is not None
+            and house.ua > 1e-6
+            and house.capacity > 1e-6
             and self._baseline_temp is not None
         ):
             why = _valve_regulates(
                 self._two_zone_plant, self._baseline_temp, outdoor_temp
             )
             sized = None if why else self._size_step_power(
-                max_power_kw,
-                cop,
-                self._baseline_temp,
-                outdoor_temp,
-                house_ua,
-                house_capacity,
-                house_gains,
-                house_slab_mass,
-                house_slab_transfer,
+                max_power_kw, cop, self._baseline_temp, outdoor_temp, house,
             )
             if sized is None:
                 self.abort(
                     VALVE_REGULATES_REASON if why
                     else "no step fits within the comfort bound"
                 )
-                return False
+                return
             self._step_power = sized
             unadoptable = self._unadoptable(sized * max(cop, 0.1), outdoor_temp)
             if unadoptable:
                 self.abort(unadoptable)
-                return False
+                return
         else:
             self._step_power = max_power_kw * 0.3
-        _LOGGER.debug(
-            "System identification step: injecting %.2f kW",
-            self._step_power,
-        )
-        return True
+        _LOGGER.debug("System identification step: injecting %.2f kW", self._step_power)
 
     def _unadoptable(self, step_kw: float, outdoor: float) -> str | None:
         """Why tonight's own noise-free fit could not be adopted, or ``None``.
@@ -1633,11 +1720,6 @@ class SystemIdentification:
         ``ThermalParameters`` defaults instead of on the house it heats
         (#943).
         """
-        house_ua = house.ua
-        house_capacity = house.capacity
-        house_gains = house.gains
-        house_slab_mass = house.slab_mass
-        house_slab_transfer = house.slab_transfer
         cfg = self.config
         if not self.active:
             return None
@@ -1651,7 +1733,8 @@ class SystemIdentification:
                     self.phase = PHASE_IDLE
                     self.result = SysIdResult(completed=False, reason=reason)
                 return None
-            _LOGGER.info("Starting system identification: %s", reason)
+            _LOGGER.info("Starting system identification (%s): %s", self.kind, reason)
+            self.held = None
             self.phase = PHASE_SETTLING
             self.phase_started = now
             self._baseline_temp = room_temp
@@ -1672,18 +1755,8 @@ class SystemIdentification:
             if self._over_excursion(room_temp):
                 self.abort("room temperature drifted beyond the allowed excursion")
                 return None
-            if elapsed >= cfg.settle_hours and not self._begin_step_phase(
-                now,
-                outdoor_temp,
-                max_power_kw,
-                cop,
-                house_ua,
-                house_capacity,
-                house_gains,
-                house_slab_mass,
-                house_slab_transfer,
-            ):
-                return None
+            if elapsed >= cfg.settle_hours:
+                self._begin_step_phase(now, outdoor_temp, max_power_kw, cop, house)
             return None
 
         if self._over_excursion(room_temp):
@@ -1692,9 +1765,8 @@ class SystemIdentification:
 
         if self.phase == PHASE_STEP:
             self.samples[-1].power_kw = self._step_power * thermal_cop
-            if elapsed >= cfg.step_hours:
-                self.phase = PHASE_RELAX
-                self.phase_started = now
+            if elapsed >= self._step_hours:
+                self._end_step(now)
             return self._step_power
 
         if self.phase == PHASE_RELAX:
@@ -1704,8 +1776,21 @@ class SystemIdentification:
 
         return None
 
+    def _end_step(self, now: datetime) -> None:
+        """A fit relaxes; a probe ends, and the plan resumes after this interval."""
+        if self.kind == KIND_PROBE:
+            self._finish(now)
+        else:
+            self.phase, self.phase_started = PHASE_RELAX, now
+
     def _finish(self, now: datetime) -> None:
         self.phase = PHASE_DONE
+        if self.kind == KIND_PROBE:
+            # Nothing is fitted: the meter's draws went to the ceiling store.
+            self.result = SysIdResult(completed=False, reason=(
+                f"ceiling probe ran {self._step_hours:.1f} h at {self._step_power:.2f} kW"
+            ))
+            return
         self.last_run = now
         # #942's wave: an experiment the arm-time gate admitted on a declared
         # plant is fitted in the two-state form (with the ported intercept
@@ -2343,5 +2428,8 @@ class SystemIdentification:
             "active": self.active,
             "samples": len(self.samples),
             "last_run": self.last_run.isoformat() if self.last_run else None,
+            "kind": self.kind,
+            "held": self.held,
+            "last_attempt": self.last_attempt.isoformat() if self.last_attempt else None,
             "result": self.result.as_dict(),
         }
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index 3632ea56c..4cd323f61 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -112,6 +112,7 @@ from .const import (
     topology_layout_valid,
 )
 from .flow_lift import FLOW_SUPPLY_MAX_C, curve_supply_temp
+from .entry_config import EntryConfig
 from .const import finite_float
 from .wood_fuel import wood_furnace_on
 from .dhw_schedule import (
@@ -1351,6 +1352,29 @@ def probe_install(config: Any) -> InstallCapability:
     )
 
 
+def flow_setpoint_driven(config: Any) -> bool:
+    """The pump-duty arbiter drives the space circuit through a flow set-point.
+
+    Control duty, the flow unit, and a plan that does not write the
+    compressor's power itself: where else the metered draw is the pump's own
+    choice or the plan's frequency echo, not a response to a set-point the
+    arbiter wrote. ``pump_arbiter._flow_command`` adds the run-time half (a
+    written record, the optimizer not off).
+    """
+    cfg = EntryConfig.from_mapping(config or {})
+    return (
+        cfg.pump_duty_mode == const.PUMP_DUTY_MODES[2]
+        and cfg.space_setpoint_unit == "flow"
+        and not probe_install(cfg).plan_writes_power()
+    )
+
+
+def ceiling_probe_install(config: Any) -> bool:
+    """The install can run the ceiling probe (R10-CEILING-PROBE): a meter to
+    read the draw, and a flow set-point the arbiter writes at the ceiling."""
+    return flow_setpoint_driven(config) and probe_install(config).measured_power
+
+
 def _configured(cap: InstallCapability, cfg: Any, key: str) -> bool:
     """The class's own config key holds an entity."""
     return bool(cfg.get(key))
diff --git a/dev/audit/harnesses/ceiling_probe.py b/dev/audit/harnesses/ceiling_probe.py
new file mode 100644
index 000000000..d1101c541
--- /dev/null
+++ b/dev/audit/harnesses/ceiling_probe.py
@@ -0,0 +1,170 @@
+"""R10-CEILING-PROBE harness: does the experiment's step reach a flow set-point
+install, and can its draws teach the band top?
+
+Four arms. The first two are the finder's harnesses (``probe_duty.py`` sha1
+0d3fbd4541c8a1b7aa0a4ed6304ba55c1828dff5, ``probe_draw.py`` sha1
+f4a4344c30aadf764929ec473d1ada2b11eb1e5f, carried on #2498), ported verbatim
+in what they print. The other two are their companions, applying the tree's
+own rule to the same inputs: the finder's duty arm reads ``_planned_duty``
+and a code-object name, and its draw arm drives ``DrawRange.observe``
+directly, which the fix rightly leaves alone, so both read flat at a head
+that routes the experiment elsewhere.
+
+  duty      the duty the arbiter serves while the experiment overrides the
+            action (5.0 kW), against a plan action of 5.0 kW
+  draw      what one probe run adds to the window's top, against 48 ceiling
+            samples in the window
+  level     the flow set-point one arbitration pass writes for an experiment
+            action at 5.0, 1.5 and 0.0 kW on a 1-5 kW band (FLOW_HEAT_C 55)
+  store     three default probe nights of a synthetic pump with a 3.0 kW
+            maximum behind a configured 5.0 kW, through the production fold;
+            the learned top and where the probe draws went
+
+Synthetic inputs only. Run from a worktree root (any tree; an arm whose
+symbols the tree lacks prints ``absent``):
+  PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/ceiling_probe.py
+"""
+from __future__ import annotations
+
+import asyncio
+from datetime import datetime, timedelta, timezone
+from types import SimpleNamespace as NS
+
+from harness import FakeHass, FakeState
+from heatpump_optimizer import draw_range as dr
+from heatpump_optimizer import pump_arbiter as pa
+from heatpump_optimizer import sysid
+from heatpump_optimizer.entry_config import EntryConfig
+
+NOW = datetime(2026, 10, 27, 1, 0, tzinfo=timezone.utc)
+
+
+def duty_arm() -> None:
+    plan = NS(timestamps=[NOW], power_schedule=[0.0], dhw_power_schedule=[0.0], optimal_setpoints=[20.0])
+
+    def inp(action):
+        return pa.ArbiterInputs(hass=None, config={}, mode="auto", plan=plan, plan_stale=False,
+                                entry_released=False, state=None, thermal=None, params=None, action=action,
+                                measured_power_kw=None, disinfecting=False)
+
+    class C:
+        pass
+
+    coord = C()
+    for label, action in (("sysid step 5.0 kW", {"mode": "system_identification", "power": 5.0}),
+                          ("null: plan action  5.0 kW", {"mode": "auto", "power": 5.0})):
+        print("duty:", label, "-> duty", repr(pa._planned_duty(coord, inp(action), NOW)),
+              "| plan step_duty", repr(pa.step_duty(plan, NOW)))
+    print("duty: flow target, duty None reads the plan/curve hold; duty 'space' reads plan power_schedule:",
+          "sysid power is not an input to _flow_target:", "action" not in pa._flow_target.__code__.co_names
+          and "action" not in pa._step_kw.__code__.co_names)
+
+
+def draw_arm() -> None:
+    cfg = sysid.SysIdConfig()
+    interval_h = 30 / 60  # DEFAULT_OPTIMIZATION_INTERVAL
+    per_run = int(cfg.step_hours / interval_h)
+
+    def run(n_ceiling):
+        d = dr.DrawRange()
+        for _ in range(dr.WINDOW - n_ceiling):  # set-point install: sub-ceiling commands
+            d.observe(1.5, 2.0, 1.0, 5.0, (35.0, 55.0))
+        for _ in range(n_ceiling):  # probe: ceiling written, pump draws 3 kW
+            d.observe(3.0, 5.0, 1.0, 5.0, (55.0, 55.0))
+        return d.observed(), d.engaged, d.planned(1.0, 5.0)
+
+    print("draw: samples per probe run", per_run, "| runs per", cfg.min_days_between_runs,
+          "days: 1 | MIN_SAMPLES", dr.MIN_SAMPLES)
+    print("draw: one probe   :", run(per_run))
+    print("draw: null 48 ceil:", run(dr.MIN_SAMPLES))
+
+
+class _Flow:
+    """The arbiter's coordinator surface on a flow set-point install, band 1-5 kW."""
+
+    def __init__(self, action):
+        self.hass = FakeHass({
+            "select.pump_mode": FakeState("Heating + DHW", attributes={
+                "options": ["Heating", "DHW (Hot Water)", "Heating + DHW"]}),
+            "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
+            "number.water_set": FakeState("53", attributes={"min": 25, "max": 63}),
+        })
+        self._config = EntryConfig.from_mapping({
+            "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
+            "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
+            "space_setpoint_unit": "flow",
+        })
+        self.action = action
+        self.params = NS(dhw_setpoint=48.0, min_electrical_power=1.0, max_electrical_power=5.0)
+        self.entry = NS(entry_id=f"cph{id(self)}")
+        self._plan = NS(timestamps=[NOW], power_schedule=[5.0], dhw_power_schedule=[0.0],
+                        optimal_setpoints=[21.0])
+
+    def _plan_is_stale(self):
+        return False
+
+    @property
+    def effective_config(self):
+        return self._config
+
+    @property
+    def thermal_params(self):
+        return self.params
+
+    def arbiter_inputs(self):
+        return pa.ArbiterInputs(
+            hass=self.hass, config=self._config, mode="auto", plan=self._plan, plan_stale=False,
+            entry_released=False, state=NS(outdoor_temperature=2.0, room_temperature=21.0),
+            thermal=NS(params=self.params, curve_flow_temp=lambda _o: 34.2), params=self.params,
+            action=self.action, measured_power_kw=None, disinfecting=False,
+        )
+
+
+def level_arm() -> None:
+    for kw in (5.0, 1.5, 0.0):
+        c = _Flow({"mode": "system_identification", "power": kw, "dhw_power": 0.0})
+        asyncio.run(pa.apply(c, NOW + timedelta(minutes=1)))
+        flow = [d.get("value") for dom, _s, d in c.hass.services.calls
+                if dom == "number" and (d or {}).get("entity_id") == "number.water_set"]
+        print(f"level: experiment {kw:.1f} kW (plan step 5.0 kW) -> flow written",
+              flow[-1] if flow else None)
+
+
+def store_arm() -> None:
+    if not hasattr(dr.DrawRange, "learned_max_kw"):
+        print("store: absent (no ceiling store in this tree)")
+        return
+    store = dr.DrawRange()
+    ceil = NS(written_c=55.0, gate_c=25.0, ceiling_c=55.0)
+    mid = NS(written_c=40.0, gate_c=25.0, ceiling_c=55.0)
+    params = NS(min_electrical_power=1.0, max_electrical_power=5.0)
+    house = sysid.HousePlant(ua=0.35, capacity=12.0, gains=0.3)
+    for night in range(3):
+        start = datetime(2026, 1, 10, 23, 0, tzinfo=timezone.utc) + timedelta(days=8 * night)
+        s = sysid.SystemIdentification(sysid.SysIdConfig(enabled=True))
+        if not s.arm(start, learner_samples=482, probe=store):
+            print("store: night", night, "refused:", s.result.reason)
+            return
+        pending = None
+        for k in range(9):
+            now = start + timedelta(minutes=30 * k)
+            override = s.step(now, 21.0, 2.0, 0.5, [0.5 + 0.03 * i for i in range(48)], 482, 5.0,
+                              cop=3.0, plan_power_kw=1.5, house=house)
+            if pending is not None:
+                dr.fold(store, 3.0 if pending["cmd"] is ceil else 1.5, (pending["kw"], 0.0), params,
+                        frozen=False, distorted=False, defrost=False, command=pending["cmd"],
+                        experiment_s=pending["when"] if pending["sid"] else None)
+            kw = 1.5 if override is None else override
+            pending = {"sid": override is not None, "kw": kw, "when": now.timestamp(),
+                       "cmd": ceil if kw >= 5.0 else mid}
+    top = store.learned_max_kw(store.ceiling_since() or 0.0)
+    print("store: probe samples", len(store.ceiling), "| learned top", top,
+          "| window samples at the ceiling", sum(1 for d, _a in store.samples if d > 2.5),
+          "| engaged", store.engaged)
+
+
+if __name__ == "__main__":
+    duty_arm()
+    draw_arm()
+    level_arm()
+    store_arm()
diff --git a/dev/audit/harnesses/r10_setpoint_boost.py b/dev/audit/harnesses/r10_setpoint_boost.py
index 6e25e0ca8..d7ebbadfd 100644
--- a/dev/audit/harnesses/r10_setpoint_boost.py
+++ b/dev/audit/harnesses/r10_setpoint_boost.py
@@ -61,7 +61,7 @@ def write(kw: float, tank: float, entity_min: float | None = 20, duty: str = "sp
                  floor_return_temperature=None),
         thermal=NS(params=None, curve_flow_temp=lambda _o: None),
         params=NS(min_electrical_power=CFG_MIN, max_electrical_power=CFG_MAX),
-        plan=NS(timestamps=[T0], power_schedule=[kw]),
+        plan=NS(timestamps=[T0], power_schedule=[kw]), action=None,
     ), duty, T0)
 
 
diff --git a/dev/programme/delivery/3050.md b/dev/programme/delivery/3050.md
new file mode 100644
index 000000000..b443deed0
--- /dev/null
+++ b/dev/programme/delivery/3050.md
@@ -0,0 +1 @@
+- [#3050](https://github.com/tvofi/heatpump_optimizer/pull/3050) — **open**, R10-CEILING-PROBE: ceiling probe (R10-CEILING-PROBE)
diff --git a/tests/closures.json b/tests/closures.json
index 583790b12..f4e898baf 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3852,6 +3852,7 @@
    "dev/audit/harnesses/archscore_layering_seam_census.py",
    "dev/audit/harnesses/archscore_shape_family_coverage.py",
    "dev/audit/harnesses/boost_replay_fork_parity.py",
+   "dev/audit/harnesses/ceiling_probe.py",
    "dev/audit/harnesses/ci-version-edit/pr_contract_shapes.py",
    "dev/audit/harnesses/ci-version-edit/recheck_stamp_forgery.py",
    "dev/audit/harnesses/ci_script_seconds.py",
diff --git a/tests/entities.py b/tests/entities.py
index 01660f41e..d1bca74f0 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -12444,7 +12444,7 @@ _PUBLISHED_ATTRS: dict[str, frozenset[str]] = {
     "ModelStatusSensor": frozenset({
         "capacity_envelope", "cop", "heat_loss", "heat_loss_w_per_k",
         "internal_gains_kw", "learner_progress", "lower_floor", "solar_aperture",
-        "system_identification", "tank_cooling"
+        "system_identification", "system_identification_outcome", "tank_cooling"
     }),
     "MonthlyPeakSensor": frozenset({
         "free_headroom_threshold_kw", "fuse_advisor", "month",
diff --git a/tests/features.py b/tests/features.py
index 327ec8d41..2d21d7207 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -2354,7 +2354,7 @@ R.check(
 # D2-s4-02: the step is sized under the abort bound by the noise headroom, on
 # the heavy default house (#779's own cell), and still uses the rest of it.
 _r9f41_sid = SystemIdentification(SysIdConfig(enabled=True))
-_r9f41_el = _r9f41_sid._size_step_power(6.0, 3.0, 21.0, 2.0, 0.20, 8.0, 0.3)
+_r9f41_el = _r9f41_sid._size_step_power(6.0, 3.0, 21.0, 2.0, HousePlant(ua=0.20, capacity=8.0, gains=0.3))
 _r9f41_peak, _r9f41_final = _r9f41_sysid._predict_step_excursion_plant(
     HousePlant(ua=0.20, capacity=8.0, gains=0.3), 21.0, 2.0,
     (_r9f41_el or 0.0) * 3.0, 2.0, 2.0
@@ -27494,7 +27494,7 @@ R.check(
 # --- #779: size on the two-state plant, not the one-state exponential ------
 R.section("sysid step sized on the two-state plant (#779)")
 _779_sid = SystemIdentification(SysIdConfig(enabled=True))
-_779_el = _779_sid._size_step_power(6.0, 3.0, 21.0, 2.0, 0.20, 8.0, 0.3)
+_779_el = _779_sid._size_step_power(6.0, 3.0, 21.0, 2.0, HousePlant(ua=0.20, capacity=8.0, gains=0.3))
 _779_q = (_779_el or 0.0) * 3.0
 _779_plant, _779_final = _predict_step_excursion_plant(
     HousePlant(ua=0.20, capacity=8.0, gains=0.3), 21.0, 2.0, _779_q, 2.0, 2.0
@@ -34623,24 +34623,37 @@ for _sig, _name in (
     (_DHW_ONLY_SIG, "a hot-water-only mode"),
     (_OFFLINE, "a pump that is off the network"),
 ):
+    # #2808 (R10-CEILING-PROBE): an armed experiment that has not started is
+    # held, not aborted -- it injects nothing, and the press is not lost to a
+    # passing freeze; a started one still aborts, its samples being the
+    # evidence the freeze says cannot be attributed.
     _si = _SysIdHost(_sig)
     _sysid_cycle(_si, np.full(48, 0.2))
+    _si_started = _SysIdHost(_sig)
+    _si_started._sysid.phase = _SysIdModule.PHASE_STEP
+    _sysid_cycle(_si_started, np.full(48, 0.2))
     R.check(
-        f"{_name} aborts an armed experiment instead of commanding heat",
-        not _si._sysid.active
-        and _si._sysid.phase == _SysIdModule.PHASE_ABORTED
-        and _si._current_action["power"] == 0.0,
-        f"phase {_si._sysid.phase} power {_si._current_action['power']} — a "
+        f"{_name} holds an armed experiment, and aborts a started one, instead of commanding heat",
+        _si._sysid.phase == _SysIdModule.PHASE_ARMED and _si._sysid.held
+        and _si._current_action["power"] == 0.0
+        and _si_started._sysid.phase == _SysIdModule.PHASE_ABORTED
+        and _si_started._current_action["power"] == 0.0,
+        f"phase {_si._sysid.phase} / {_si_started._sysid.phase} power "
+        f"{_si._current_action['power']} — a "
         f"step response measured through this is not a noisy measurement of "
         f"the house, and _adopt_system_identification persists what it fits",
     )
 _si_reason = _SysIdHost(_COOLING)
 _sysid_cycle(_si_reason, np.full(48, 0.2))
+_si_reason_started = _SysIdHost(_COOLING)
+_si_reason_started._sysid.phase = _SysIdModule.PHASE_STEP
+_sysid_cycle(_si_reason_started, np.full(48, 0.2))
 R.check(
-    "the aborted result carries the cause",
-    _si_reason._sysid.result.reason
-    and not _si_reason._sysid.result.completed,
-    f"{_si_reason._sysid.result.reason!r}",
+    "the held experiment and the aborted result each carry the cause",
+    _si_reason._sysid.held
+    and _si_reason_started._sysid.result.reason == _si_reason._sysid.held
+    and not _si_reason_started._sysid.result.completed,
+    f"{_si_reason._sysid.held!r} / {_si_reason_started._sysid.result.reason!r}",
 )
 
 
@@ -57616,7 +57629,10 @@ _pa_noplan = _PaCoord(_PA_TUYA)
 _pa_noplan._optimization_result = None
 _pa_run(_pa_noplan, 1)
 R.check(
-    "an experiment and a missing plan each get the baseline, not hot water only",
+    # R10-CEILING-PROBE: the experiment's action now carries its own duty (its
+    # zero step here is idle, the gate), where the missing plan keeps the
+    # baseline; neither writes hot water only.
+    "an experiment's zero step and a missing plan never write hot water only",
     all(
         ("select", "select_option", "DHW (Hot Water)") not in c.writes()
         and ("number", "set_value", 48.0) in c.writes()
@@ -66868,6 +66884,7 @@ def _sp_write(kw, slots, stale=()):
             thermal=_PaNS(params=None),
             params=_PaNS(min_electrical_power=1.5, max_electrical_power=5.5),
             plan=_PaNS(timestamps=[_PA_T0], power_schedule=[kw]),
+            action=None,
         ),
         "space",
         _PA_T0,
@@ -68778,6 +68795,7 @@ def _bst_write(kw, tank, entity_min=20, duty="space"):
             thermal=_BstNS(params=None, curve_flow_temp=lambda _o: None),
             params=_BstNS(min_electrical_power=1.5, max_electrical_power=5.5),
             plan=_BstNS(timestamps=[_BST_T0], power_schedule=[kw]),
+            action=None,
         ),
         duty, _BST_T0,
     )
@@ -74964,4 +74982,824 @@ R.check(
 )
 
 
+# --- R10-CEILING-PROBE (#2498, #2808): the cheap-night ceiling probe ----------
+# A set-point install's plan rarely writes the flow ceiling, so the metered
+# draw window is censored at the top and the plugin cannot learn the pump's
+# real maximum. The system-identification experiment gains a second kind, the
+# ceiling probe: it commands the configured maximum, the arbiter writes the
+# ceiling for it, and the metered draws of those intervals go to a separate
+# store on ``DrawRange`` whose raw median is the learned top. Every check
+# drives the production symbol; the design is dev/programme/designs/
+# R10-CEILING-PROBE.md as amended by its review (items 7-34).
+import asyncio as _cp_aio  # noqa: E402
+from types import SimpleNamespace as _CpNS  # noqa: E402
+
+from harness import FakeEntry as _CpEntry  # noqa: E402
+from heatpump_optimizer import boost as _cp_boost  # noqa: E402
+from heatpump_optimizer import coordinator as _cp_cmod  # noqa: E402
+from heatpump_optimizer import draw_range as _cp_dr  # noqa: E402
+from heatpump_optimizer import pump_arbiter as _cp_pa  # noqa: E402
+from heatpump_optimizer import sysid as _cp_sid  # noqa: E402
+from heatpump_optimizer.accuracy import AccuracyTracker as _CpTracker  # noqa: E402
+from heatpump_optimizer.entry_config import EntryConfig as _CpConfig  # noqa: E402
+from heatpump_optimizer.sensor import ModelStatusSensor as _CpStatus  # noqa: E402
+from heatpump_optimizer.store import admitted as _cp_admitted  # noqa: E402
+from heatpump_optimizer.thermal_model import ceiling_probe_install as _cp_eligible  # noqa: E402
+
+R.section("R10-CEILING-PROBE: the experiment's step reaches the pump; the ceiling store")
+
+_CP_T0 = datetime(2026, 1, 10, 23, 0, tzinfo=UTC)
+_CP_OPTS = ("Heating", "DHW (Hot Water)", "Heating + DHW")
+
+
+class _CpArb:
+    """The arbiter's coordinator surface on a flow set-point install, band 1-5 kW."""
+
+    def __init__(self, action, power_schedule=(1.5,)):
+        self.hass = FakeHass({
+            "select.pump_mode": FakeState("Heating + DHW", attributes={"options": list(_CP_OPTS)}),
+            "number.dhw_set": FakeState("53", attributes={"min": 40, "max": 63}),
+            "number.water_set": FakeState("53", attributes={"min": 25, "max": 63}),
+        })
+        self._config = _CpConfig.from_mapping({
+            "pump_duty_mode": "control", "heat_pump_mode_entity": "select.pump_mode",
+            "dhw_setpoint_entity": "number.dhw_set", "space_setpoint_entity": "number.water_set",
+            "space_setpoint_unit": "flow",
+        })
+        self._current_action = action
+        self._optimization_result = _CpNS(
+            timestamps=[_CP_T0], power_schedule=list(power_schedule),
+            dhw_power_schedule=[0.0], optimal_setpoints=[21.0],
+        )
+        self._thermal_params = _CpNS(dhw_setpoint=48.0, min_electrical_power=1.0, max_electrical_power=5.0)
+        self._thermal_model = _CpNS(params=self._thermal_params, curve_flow_temp=lambda _o: 34.2)
+        self.entry = _CpNS(entry_id=f"cp{id(self)}")
+
+    def _plan_is_stale(self):
+        return False
+
+    @property
+    def effective_config(self):
+        return self._config
+
+    @property
+    def thermal_params(self):
+        return self._thermal_params
+
+    def arbiter_inputs(self):
+        return _cp_pa.ArbiterInputs(
+            hass=self.hass, config=self._config, mode="auto", plan=self._optimization_result,
+            plan_stale=False, entry_released=False, state=_CpNS(outdoor_temperature=2.0,
+            room_temperature=21.0), thermal=self._thermal_model, params=self._thermal_params,
+            action=self._current_action, measured_power_kw=None, disinfecting=False,
+        )
+
+
+def _cp_arbitrate(action, power_schedule=(1.5,)):
+    """(duty, the flow set-point written, the mode written) for one pass."""
+    c = _CpArb(action, power_schedule)
+    duty = _cp_pa._planned_duty(c, c.arbiter_inputs(), _CP_T0)
+    _cp_aio.run(_cp_pa.apply(c, _CP_T0 + timedelta(minutes=1)))
+    calls = [(d, s, data or {}) for d, s, data in c.hass.services.calls]
+    flow = [x["value"] for d, s, x in calls if d == "number" and x.get("entity_id") == "number.water_set"]
+    mode = [x.get("option") for d, s, x in calls if d == "select"]
+    return duty, (flow[-1] if flow else None), (mode[-1] if mode else None)
+
+
+_CP_SID = {"mode": "system_identification", "dhw_power": 0.0}
+_cp_probe = _cp_arbitrate({**_CP_SID, "power": 5.0})
+_cp_fit = _cp_arbitrate({**_CP_SID, "power": 1.5})
+_cp_relax = _cp_arbitrate({**_CP_SID, "power": 0.0})
+_cp_plan_top = _cp_arbitrate({"mode": "eco", "power": 5.0}, power_schedule=(5.0,))
+_cp_plan_mid = _cp_arbitrate({"mode": "eco", "power": 1.5}, power_schedule=(1.5,))
+R.check(
+    "the probe's step (the configured 5.0 kW maximum) is heating at the flow ceiling",
+    _cp_probe[0] == "space" and _cp_probe[1] == 55.0 and _cp_probe[2] == "Heating",
+    f"{_cp_probe}",
+)
+R.check(
+    "the fit's sized 1.5 kW step writes its own level, below the ceiling, from the action "
+    "not the plan (whose step here is 5.0 kW)",
+    _cp_fit[0] == "space" and _cp_fit[1] == _cp_plan_mid[1] and _cp_fit[1] < 55.0
+    and _cp_arbitrate({**_CP_SID, "power": 1.5}, power_schedule=(5.0,))[1] == _cp_fit[1],
+    f"fit {_cp_fit} plan-mid {_cp_plan_mid}",
+)
+R.check(
+    "the experiment's zero step (the fit's relax) is idle: the gate is written",
+    _cp_relax[0] == "idle" and _cp_relax[1] == 25.0,
+    f"{_cp_relax}",
+)
+R.check(
+    "moving control: a plan at 5.0 and at 1.5 kW write two levels, the ceiling and "
+    "the fit's -- before the fix the experiment wrote the baseline at both",
+    _cp_plan_top[:2] == ("space", 55.0) and _cp_plan_mid[0] == "space" and _cp_plan_mid[1] < 55.0,
+    f"{_cp_plan_top} {_cp_plan_mid}",
+)
+# The duty threshold is the rule ``heat_pump_on`` books (``planned_draw_runs``),
+# never a literal: a step at MIN_RUNNING_DRAW_KW's edge reads the same in both.
+from heatpump_optimizer.thermal_model import MIN_RUNNING_DRAW_KW as _CP_RUN  # noqa: E402
+from heatpump_optimizer.thermal_model import planned_draw_runs as _cp_runs  # noqa: E402
+
+_cp_edge = [
+    (kw, _cp_arbitrate({**_CP_SID, "power": kw})[0], _cp_runs(kw))
+    for kw in (_CP_RUN, _CP_RUN * 1.5, 0.06, 0.04)
+]
+R.check(
+    "the experiment's duty is space exactly where its booked heat_pump_on is True",
+    all((duty == "space") == runs and duty in ("space", "idle") for _kw, duty, runs in _cp_edge),
+    f"{_cp_edge}",
+)
+
+# Carry 31: the supply switch a probe interval runs under. The cycle writes
+# heat_pump_on from planned_draw_runs(override); the one-minute step tick
+# leaves the switch alone under an experiment, so it is not turned off
+# between cycles. Both halves read the production functions.
+_cp_tick_inp = _CpArb({**_CP_SID, "power": 5.0}).arbiter_inputs()
+R.check(
+    "a probe interval: the cycle books the supply on, and the step tick writes nothing over it",
+    _cp_runs(5.0) is True
+    and _cp_pa.step_supply(_cp_tick_inp, _cp_boost.BoostState(), _CP_T0 + timedelta(minutes=15)) is None
+    and _cp_pa.step_supply(
+        _CpArb({"mode": "eco", "power": 0.0}, power_schedule=(0.0,)).arbiter_inputs(),
+        _cp_boost.BoostState(), _CP_T0 + timedelta(minutes=1),
+    ) is False,
+    "null control: a plan step at 0 kW is a tick write of off",
+)
+
+# -- the ceiling store -------------------------------------------------------
+_CP_CEIL = _CpNS(written_c=55.0, gate_c=25.0, ceiling_c=55.0)
+_CP_GATE = _CpNS(written_c=25.0, gate_c=25.0, ceiling_c=55.0)
+_CP_MID = _CpNS(written_c=40.0, gate_c=25.0, ceiling_c=55.0)
+_CP_DAY = 86400.0
+_CP_NOW = _CP_T0.timestamp()
+
+
+def _cp_params(lo=1.0, hi=5.0):
+    return _CpNS(min_electrical_power=lo, max_electrical_power=hi)
+
+
+def _cp_fold(d, drawn, command, experiment_s, split=(5.0, 0.0), hi=5.0):
+    _cp_dr.fold(d, drawn, split, _cp_params(hi=hi), frozen=False, distorted=False,
+                defrost=False, command=command, experiment_s=experiment_s)
+
+
+def _cp_store(values, newest_s=_CP_NOW):
+    d = _cp_dr.DrawRange()
+    for k, v in enumerate(values):
+        d.observe_ceiling(v, newest_s - (len(values) - 1 - k) * 1800.0)
+    return d
+
+
+R.check(
+    "item 29: the accessor is raw -- eleven samples give None, twelve their median",
+    _cp_store([3.0] * 11).learned_max_kw(_CP_NOW) is None
+    and _cp_store([3.0] * 12).learned_max_kw(_CP_NOW) == 3.0,
+)
+R.check(
+    "item 29: twelve at 4.5 kW on a 5.0 kW configuration publish 4.5 (within 15 % is "
+    "still published raw; the agreement ruling is R10-COP-GATE part D's); eleven, None",
+    _cp_store([4.5] * 12).learned_max_kw(_CP_NOW) == 4.5
+    and _cp_store([4.5] * 11).learned_max_kw(_CP_NOW) is None,
+)
+R.check(
+    "the top lapses 45 days after the newest sample, and a sample stamped ahead of "
+    "the clock has no knowable age",
+    _cp_store([3.0] * 12).learned_max_kw(_CP_NOW + 44 * _CP_DAY) == 3.0
+    and _cp_store([3.0] * 12).learned_max_kw(_CP_NOW + 46 * _CP_DAY) is None
+    and _cp_store([3.0] * 12, newest_s=_CP_NOW + 600.0).learned_max_kw(_CP_NOW) is None,
+)
+
+# The routing: an experiment's interval written at the ceiling, running above
+# the idle draw, goes to the store and not the window; everything else folds
+# into the window as before.
+_cp_route = _cp_dr.DrawRange()
+for _cp_v in (0.30,) * 12:
+    _cp_route.observe_idle(_cp_v)
+_cp_fold(_cp_route, 3.0, _CP_CEIL, _CP_NOW)
+_cp_routed = (len(_cp_route.ceiling), len(_cp_route.samples))
+_cp_fold(_cp_route, 3.0, _CP_CEIL, None)
+_cp_plan = (len(_cp_route.ceiling), len(_cp_route.samples))
+R.check(
+    "an experiment's ceiling interval writes the store, not the window; the same "
+    "interval the plan commanded writes the window, not the store",
+    _cp_routed == (1, 0) and _cp_plan == (1, 1),
+    f"experiment {_cp_routed} plan {_cp_plan}",
+)
+_cp_held = _cp_dr.DrawRange()
+for _cp_v in (1.1,) * 12:
+    _cp_held.observe_idle(_cp_v)
+_cp_fold(_cp_held, 1.4, _CP_GATE, _CP_NOW)
+_cp_fold(_cp_held, 1.3, _CP_CEIL, _CP_NOW)
+_cp_fold(_cp_held, 1.4, _CP_CEIL, _CP_NOW)
+_cp_fold(_cp_held, 2.6, _CP_MID, _CP_NOW)
+R.check(
+    "a gate-held 1.4 kW draw above a learned 1.1 kW idle is a running sample yet stores "
+    "nothing, nor does a ceiling draw at the idle draw or a sub-ceiling one; the same "
+    "1.4 kW with the ceiling written does",
+    _cp_dr.is_running_space(1.4, 5.0, 0.0, frozen=False, distorted=False, defrost=False)
+    and [d for d, _t in _cp_held.ceiling] == [1.4],
+    f"{list(_cp_held.ceiling)}",
+)
+# The latch (F6, F7): 48 ceiling samples through ``observe`` on an empty
+# window engage the clamp at append 48; the same 48 routed to the store leave
+# it disengaged and the window empty.
+_cp_latch_w = _cp_dr.DrawRange()
+_cp_latch_s = _cp_dr.DrawRange()
+for _cp_k in range(48):
+    _cp_latch_w.observe(3.0, 5.0, 1.0, 5.0, command=(55.0, 55.0))
+    _cp_fold(_cp_latch_s, 3.0, _CP_CEIL, _CP_NOW + _cp_k * 1800.0)
+R.check(
+    "reversal control: 48 ceiling draws through the window latch the clamp to the "
+    "experiment's own measurement; the same 48 in the store leave engaged False, "
+    "observed() unset and the top published beside the latch",
+    _cp_latch_w.engaged is True and _cp_latch_w.planned(1.0, 5.0) == (3.0, 3.0)
+    and _cp_latch_s.engaged is False and _cp_latch_s.observed() is None
+    and len(_cp_latch_s.samples) == 0 and _cp_latch_s.learned_max_kw(_CP_NOW + 47 * 1800.0) == 3.0
+    and _cp_dr.diagnostics_view(
+        _cp_latch_s, _cp_params(), _CpNS(plan_writes_power=lambda: False, can_duty_cycle=lambda: False),
+        _CP_NOW + 47 * 1800.0,
+    ) == {**_cp_latch_s.summary(), "effective_min_kw": None, "effective_max_kw": None,
+          "learned_max_kw": 3.0},
+    f"window {_cp_latch_w.engaged} {_cp_latch_w.planned(1.0, 5.0)} store {_cp_latch_s.engaged}",
+)
+
+# Item 8: the overdraw drop. A top learned on mild nights (3.0 kW) against
+# ordinary ceiling-written intervals drawing 20 % more at -10 degC: the store
+# drops on the second. Null control: 10 % more, five times, keeps it.
+_cp_over = _cp_store([3.0] * 12)
+_cp_fold(_cp_over, 3.6, _CP_CEIL, None)
+_cp_over_one = len(_cp_over.ceiling)
+_cp_fold(_cp_over, 3.6, _CP_CEIL, None)
+_cp_near = _cp_store([3.0] * 12)
+for _cp_k in range(5):
+    _cp_fold(_cp_near, 3.3, _CP_CEIL, None)
+_cp_mid_over = _cp_store([3.0] * 12)
+for _cp_k in range(5):
+    _cp_fold(_cp_mid_over, 3.6, _CP_MID, None)
+R.check(
+    "item 8: two ordinary ceiling-written draws 20 % over the learned top drop the "
+    "store; one does not, 10 % over never does, and a sub-ceiling draw is no test",
+    _cp_over_one == 12 and len(_cp_over.ceiling) == 0
+    and len(_cp_near.ceiling) == 12 and len(_cp_mid_over.ceiling) == 12,
+    f"{_cp_over_one} {len(_cp_over.ceiling)} {len(_cp_near.ceiling)} {len(_cp_mid_over.ceiling)}",
+)
+_cp_rearm = _cp_store([3.0] * 12)
+_cp_fold(_cp_rearm, 3.6, _CP_CEIL, None)
+_cp_rearm.observe_ceiling(3.0, _CP_NOW + 60.0)
+_cp_fold(_cp_rearm, 3.6, _CP_CEIL, None)
+R.check(
+    "a new probe sample restarts the overdraw count",
+    len(_cp_rearm.ceiling) == 13 and _cp_rearm.overdraws == 1,
+    f"{len(_cp_rearm.ceiling)} {_cp_rearm.overdraws}",
+)
+
+# Persistence (item 7's clock lives here): the store round-trips through the
+# accuracy document, a store-only record keeps it, and every cell is declared.
+_cp_doc_range = _cp_store([3.0] * 12)
+_cp_doc_range.overdraws = 1
+_cp_tracker = _CpTracker()
+_cp_tracker.draw = _cp_doc_range
+_cp_doc = _cp_tracker.as_dict()
+_cp_back = _CpTracker.from_dict(_cp_doc).draw
+R.check(
+    "the store and its overdraw count persist through the accuracy store, a store-only "
+    "record (no window, no configuration) included, and the domains admit every cell",
+    "draw" in _cp_doc and list(_cp_back.ceiling) == list(_cp_doc_range.ceiling)
+    and _cp_back.overdraws == 1 and _cp_back.config is None
+    and _cp_back.learned_max_kw(_CP_NOW) == 3.0
+    and _cp_admitted("accuracy", {"accuracy": {"draw": _cp_doc["draw"]}})
+    and "draw" not in _CpTracker().as_dict(),
+    f"{_cp_doc.get('draw')}",
+)
+_cp_junk = _cp_dr.DrawRange.from_dict({
+    "ceiling": [[3.0, _CP_NOW], ["x", 1.0], [float("nan"), 1.0], [0.1, 1.0], [3.0], [3.1, float("inf")]],
+    "overdraws": True,
+})
+R.check(
+    "an unreadable store row is dropped, not the record; a non-count overdraw reads 0",
+    list(_cp_junk.ceiling) == [(3.0, _CP_NOW)] and _cp_junk.overdraws == 0,
+    f"{list(_cp_junk.ceiling)} {_cp_junk.overdraws}",
+)
+
+# -- the experiment's kinds, clocks and gates ---------------------------------
+_CP_LEAKY = _cp_sid.HousePlant(ua=0.35, capacity=12.0, gains=0.3)
+_CP_TIGHT = _cp_sid.HousePlant(ua=0.12, capacity=4.0, gains=0.3)
+_CP_WEE = _cp_sid.HousePlant(ua=0.05, capacity=1.2, gains=0.3)
+
+
+def _cp_cfg(**kw):
+    return _cp_sid.SysIdConfig(enabled=True, **kw)
+
+
+R.check(
+    "the probe's duration search: 2.0 h on the leaky house, 1.0 h on the tight one "
+    "against the 0.8 K bound, none on a house no two-cycle step fits",
+    _cp_sid.probe_step_hours(_CP_LEAKY, None, 21.0, 2.0, 15.0, _cp_cfg()) == 2.0
+    and _cp_sid.probe_step_hours(_CP_TIGHT, None, 21.0, 2.0, 15.0, _cp_cfg()) == 1.0
+    and _cp_sid.probe_step_hours(_CP_WEE, None, 21.0, 2.0, 15.0, _cp_cfg()) is None,
+)
+R.check(
+    "item 14, both sides of the bound: the probe takes the full 0.8 K, where the fit's "
+    "noise-headroom bound (0.65 K) would leave the tight house one cycle and refuse it",
+    _cp_sid.probe_step_hours(
+        _CP_TIGHT, None, 21.0, 2.0, 15.0,
+        _cp_cfg(max_excursion_c=_cp_sid.DEFAULT_MAX_EXCURSION_C - _cp_sid.SIZING_NOISE_HEADROOM_C),
+    ) is None,
+)
+
+
+def _cp_probe_store(samples, newest_days_ago):
+    return _cp_store([3.0] * samples, newest_s=(_CP_T0 - timedelta(days=newest_days_ago)).timestamp())
+
+
+_cp_armable = {
+    "unconverged": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 150, None, None),
+    "199": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 199, None, None),
+    "converged, no probe": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 482, None, None),
+    "converged, probe": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 482, _cp_dr.DrawRange(), None),
+    "fit clock, probe": _cp_sid.armable(
+        _cp_cfg(), _CP_T0, _CP_T0 - timedelta(days=3), 150, _cp_dr.DrawRange(), None),
+    "unlearned 6 d": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 482, _cp_probe_store(4, 6), None),
+    "unlearned 8 d": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 482, _cp_probe_store(4, 8), None),
+    "learned 29 d": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 482, _cp_probe_store(12, 29), None),
+    "learned 31 d": _cp_sid.armable(_cp_cfg(), _CP_T0, None, 482, _cp_probe_store(12, 31), None),
+    "attempt 3 d": _cp_sid.armable(
+        _cp_cfg(), _CP_T0, None, 482, _cp_dr.DrawRange(), _CP_T0 - timedelta(days=3)),
+}
+R.check(
+    "the kind: the fit while unconverged (150, 199), the probe once converged where "
+    "the install can run one, and a published refusal where it cannot",
+    _cp_armable["unconverged"] == ("fit", "") and _cp_armable["199"] == ("fit", "")
+    and _cp_armable["converged, probe"] == ("ceiling_probe", "")
+    and _cp_armable["converged, no probe"][0] is None
+    and "house already converged" in _cp_armable["converged, no probe"][1]
+    and _cp_armable["fit clock, probe"] == ("ceiling_probe", ""),
+    f"{_cp_armable}",
+)
+R.check(
+    "each kind its own clock: the probe waits 7 days unlearned and 30 once learned, from "
+    "the store's newest sample or this process's last probe step",
+    _cp_armable["unlearned 6 d"][0] is None and _cp_armable["unlearned 8 d"][0] == "ceiling_probe"
+    and _cp_armable["learned 29 d"][0] is None and _cp_armable["learned 31 d"][0] == "ceiling_probe"
+    and _cp_armable["attempt 3 d"][0] is None,
+    f"{_cp_armable}",
+)
+
+
+def _cp_night(kind_samples=482, probe=True, **cfg):
+    """An armed experiment on the leaky house, its outcome and override per cycle."""
+    s = _cp_sid.SystemIdentification(_cp_cfg(**cfg))
+    armed = s.arm(_CP_T0, learner_samples=kind_samples, probe=_cp_dr.DrawRange() if probe else None)
+    return s, armed
+
+
+def _cp_step(s, k, room=21.0, prices=np.linspace(0.5, 2.0, 48), price=0.5, outdoor=2.0, at=_CP_T0):
+    return s.step(
+        at + timedelta(minutes=30 * k), room, outdoor, price, prices, 482, 5.0,
+        cop=3.0, plan_power_kw=1.5, house=_CP_LEAKY,
+    )
+
+
+_cp_run, _cp_run_armed = _cp_night()
+_cp_overrides = [_cp_step(_cp_run, k) for k in range(8)]
+R.check(
+    "a converged house arms a probe: it settles an hour on the plan, steps the configured "
+    "5.0 kW for four intervals, then hands back to the plan, fitting and adopting nothing",
+    _cp_run_armed and _cp_overrides == [None, None, None, 5.0, 5.0, 5.0, 5.0, None]
+    and _cp_run.phase == _cp_sid.PHASE_DONE and _cp_run.result.completed is False
+    and _cp_run.result.reason == "ceiling probe ran 2.0 h at 5.00 kW"
+    and _cp_run.last_run is None and _cp_run.probe_run == _CP_T0 + timedelta(hours=1),
+    f"{_cp_overrides} {_cp_run.phase} {_cp_run.result.reason!r}",
+)
+_cp_view = _cp_run.as_dict()
+R.check(
+    "the view names the kind and the last arm press",
+    _cp_view["kind"] == "ceiling_probe" and _cp_view["last_attempt"] == _CP_T0.isoformat()
+    and _cp_view["held"] is None,
+    f"{_cp_view}",
+)
+_cp_none, _cp_none_armed = _cp_night(probe=False)
+R.check(
+    "a converged house with no meter or no flow set-point is refused at the press, and "
+    "the refusal is published (it used to arm and idle in silence)",
+    _cp_none_armed is False and not _cp_none.active
+    and "house already converged" in _cp_none.result.reason
+    and "no metered flow set-point" in _cp_none.result.reason,
+    f"{_cp_none.result.reason!r}",
+)
+for _cp_label, _cp_kw in (
+    ("outside the night window", {"at": _CP_T0 - timedelta(hours=6)}),
+    ("outside the outdoor band", {"outdoor": 14.0}),
+    ("on an expensive hour", {"price": 1.9}),
+    ("on a flat price", {"prices": np.full(48, 1.0), "price": 1.0}),
+):
+    _cp_g, _ = _cp_night()
+    _cp_g_out = [_cp_step(_cp_g, k, **_cp_kw) for k in range(8)]
+    R.check(
+        f"the comfort and price gates hold the probe: none starts {_cp_label}",
+        _cp_g_out == [None] * 8 and _cp_g.phase == _cp_sid.PHASE_ARMED,
+        f"{_cp_g_out} {_cp_g.phase}",
+    )
+_cp_flat_fit = _cp_sid.SystemIdentification(_cp_cfg())
+_cp_flat_fit.arm(_CP_T0, learner_samples=0)
+R.check(
+    "flat-price null: the fit's gate is unchanged on a flat price (ready), the probe's "
+    "refuses it",
+    _cp_flat_fit.conditions_met(_CP_T0, 2.0, 1.0, np.full(48, 1.0), 0) == (True, "ready")
+    and _cp_g.conditions_met(_CP_T0, 2.0, 1.0, np.full(48, 1.0), 0)[0] is False,
+)
+_cp_hot, _ = _cp_night()
+_cp_hot_out = [_cp_step(_cp_hot, k, room=21.0 + (0.9 if k >= 4 else 0.0)) for k in range(6)]
+R.check(
+    "the comfort abort still stops a probe mid-step",
+    _cp_hot.phase == _cp_sid.PHASE_ABORTED and _cp_hot_out[-1] is None
+    and "excursion" in _cp_hot.result.reason,
+    f"{_cp_hot_out} {_cp_hot.phase}",
+)
+_cp_tightp = _cp_sid.SystemIdentification(_cp_cfg())
+_cp_tightp.arm(_CP_T0, learner_samples=482, probe=_cp_dr.DrawRange())
+_cp_tight_out = [
+    _cp_tightp.step(_CP_T0 + timedelta(minutes=30 * k), 21.0, 2.0, 0.5, np.linspace(0.5, 2.0, 48),
+                    482, 5.0, cop=3.0, plan_power_kw=1.5, house=_CP_TIGHT)
+    for k in range(7)
+]
+R.check(
+    "item 15: the searched duration is the one stepped -- the tight house's 1.0 h probe "
+    "steps two intervals, not the configured 2.0 h",
+    _cp_tight_out == [None, None, None, 5.0, 5.0, None, None]
+    and _cp_tightp.result.reason == "ceiling probe ran 1.0 h at 5.00 kW",
+    f"{_cp_tight_out} {_cp_tightp.result.reason!r}",
+)
+
+# The learners' freeze (#2808): an armed experiment is held with the reason
+# published; a started one still aborts.
+_cp_fz, _ = _cp_night()
+_cp_fz.stand_down("window open")
+_cp_fz_held = (_cp_fz.phase, _cp_fz.held, _cp_fz.as_dict()["held"])
+_cp_fz_out = [_cp_step(_cp_fz, k) for k in range(3)]
+_cp_fz.stand_down("window open")
+R.check(
+    "a freeze holds an armed experiment and publishes why; once started, it aborts",
+    _cp_fz_held == (_cp_sid.PHASE_ARMED, "window open", "window open")
+    and _cp_fz_out[0] is None and _cp_fz.phase == _cp_sid.PHASE_ABORTED
+    and _cp_fz.result.reason == "window open",
+    f"{_cp_fz_held} {_cp_fz.phase} {_cp_fz.result.reason!r}",
+)
+
+# -- the coordinator's wiring -------------------------------------------------
+_CP_COORD_DATA = {"tibber_token": "x", "weather_entity": "weather.home"}
+_CP_PROBE_CFG = {
+    "pump_duty_mode": "control", "space_setpoint_unit": "flow",
+    "space_setpoint_entity": "number.water_set", "heat_pump_power_entity": "sensor.hp_power",
+}
+R.check(
+    "eligibility is install-level and shared with the arbiter's flow-command rule: a "
+    "meter and a flow set-point driven in Control",
+    _cp_eligible(_CP_PROBE_CFG) is True
+    and _cp_eligible({**_CP_PROBE_CFG, "heat_pump_power_entity": ""}) is False
+    and _cp_eligible({**_CP_PROBE_CFG, "space_setpoint_unit": "indoor"}) is False
+    and _cp_eligible({**_CP_PROBE_CFG, "pump_duty_mode": "observe"}) is False,
+)
+
+
+def _cp_coord(samples=482, **config):
+    c = _cp_cmod.HeatPumpOptimizerCoordinator(FakeHass(), _CpEntry(data={**_CP_COORD_DATA, **config}))
+    c._house_heat_loss_samples = samples
+    with_config(c, {"system_identification_enabled": True})
+
+    async def _no_refresh():
+        return None
+
+    c.async_request_refresh = _no_refresh
+    _cp_aio.run(c.async_arm_system_identification())
+    return c
+
+
+_cp_c_probe = _cp_coord(**_CP_PROBE_CFG)
+_cp_c_none = _cp_coord()
+_cp_c_fit = _cp_coord(samples=150, **_CP_PROBE_CFG)
+R.check(
+    "the button's route: a converged flow-metered install arms the probe, a converged "
+    "duty-cycling one is refused with the reason, an unconverged one arms the fit",
+    _cp_c_probe._sysid.active and _cp_c_probe._sysid.kind == "ceiling_probe"
+    and not _cp_c_none._sysid.active and "house already converged" in _cp_c_none._sysid.result.reason
+    and _cp_c_fit._sysid.active and _cp_c_fit._sysid.kind == "fit",
+    f"{_cp_c_probe._sysid.kind} {_cp_c_none._sysid.result.reason!r} {_cp_c_fit._sysid.kind}",
+)
+# Item 7: the probe clock survives a restart, through the persisted store.
+_cp_restart_store = _cp_probe_store(4, 3)
+_cp_restarted = _cp_sid.SystemIdentification(_cp_cfg())
+R.check(
+    "item 7: a probe three days ago, read back from the stored record by a fresh "
+    "experiment object, still refuses the press; eight days ago arms",
+    _cp_restarted.arm(_CP_T0, learner_samples=482, probe=_cp_dr.DrawRange.from_dict(
+        _cp_restart_store.as_dict())) is False
+    and "ceiling probe ran 3.0 days ago" in _cp_restarted.result.reason
+    and _cp_sid.SystemIdentification(_cp_cfg()).arm(
+        _CP_T0, learner_samples=482,
+        probe=_cp_dr.DrawRange.from_dict(_cp_probe_store(4, 8).as_dict())) is True,
+    f"{_cp_restarted.result.reason!r}",
+)
+
+
+def _cp_sysid_cycle(host):
+    async def _unusable(hass, fn, *args):
+        raise _cp_cmod.ProcessWorkerUnavailable("features: executor route")
+
+    real, _cp_cmod._await_process = _cp_cmod._await_process, _unusable
+    try:
+        return _cp_aio.run(host._run_system_identification(np.array([1.0])))
+    finally:
+        _cp_cmod._await_process = real
+
+
+_cp_frz = _cp_coord(**_CP_PROBE_CFG)
+_cp_frz._learning_frozen = lambda *keys: "an open window"
+_cp_sysid_cycle(_cp_frz)
+_cp_frz_armed = (_cp_frz._sysid.phase, _cp_frz._sysid.held)
+_cp_frz._sysid.phase = _cp_sid.PHASE_STEP
+_cp_sysid_cycle(_cp_frz)
+R.check(
+    "the coordinator's freeze holds the armed probe with its reason, and aborts a started one",
+    _cp_frz_armed == (_cp_sid.PHASE_ARMED, "an open window")
+    and _cp_frz._sysid.phase == _cp_sid.PHASE_ABORTED,
+    f"{_cp_frz_armed} {_cp_frz._sysid.phase}",
+)
+
+
+# Item 30: the fold routes on the mode the interval's own action carried,
+# captured in ``_pending_prediction`` beside its split and command -- never on
+# the action adopted since. Two cycles half an hour apart (#2262).
+def _cp_pair(first, then):
+    c = _cp_cmod.HeatPumpOptimizerCoordinator(FakeHass(), _CpEntry(data=dict(_CP_COORD_DATA)))
+    c._measured_power = 3.0
+    c._current_action = dict(first)
+    c._record_accuracy()
+    c._pending_prediction["when"] -= timedelta(minutes=30)
+    c._pending_prediction["flow_command"] = _CP_CEIL
+    c._current_action = dict(then)
+    c._record_accuracy()
+    return len(c._accuracy.draw.ceiling), len(c._accuracy.draw.samples), c._pending_prediction["mode"]
+
+
+_CP_STEP = {"power": 5.0, "dhw_power": 0.0, "mode": "system_identification"}
+_CP_PLAN = {"power": 5.0, "dhw_power": 0.0, "mode": "eco"}
+_cp_last = _cp_pair(_CP_STEP, _CP_PLAN)
+_cp_before = _cp_pair(_CP_PLAN, _CP_STEP)
+R.check(
+    "item 30: a run's last step interval goes to the store although the plan has been "
+    "adopted since; a plan p_max interval just before a run goes to the window although "
+    "the experiment has started since",
+    _cp_last[:2] == (1, 0) and _cp_before[:2] == (0, 1)
+    and _cp_last[2] == "eco" and _cp_before[2] == "system_identification",
+    f"last {_cp_last} before {_cp_before}",
+)
+
+
+# The synthetic pump: a known 3.0 kW electrical maximum behind a configured
+# 5.0 kW, drawn whenever the ceiling is written (and 1.5 kW at the plan's
+# mid level). Probe nights through the production experiment, the pairing the
+# coordinator makes (the interval's own mode, split and command, read at the
+# next cycle), and the production fold. Recovered within 2 % at both step
+# lengths; the control routes on the mode one interval late, as reading the
+# action at the fold would.
+def _cp_pump(house, nights, late=False, noise=0.02, seed=3):
+    rng = np.random.default_rng(seed)
+    store = _cp_dr.DrawRange()
+    for night in range(nights):
+        start = _CP_T0 + timedelta(days=8 * night)
+        s = _cp_sid.SystemIdentification(_cp_cfg())
+        assert s.arm(start, learner_samples=482, probe=store), s.result.reason
+        pending, prev_mode = None, None
+        for k in range(9):
+            now = start + timedelta(minutes=30 * k)
+            override = s.step(now, 21.0, 2.0, 0.5, np.linspace(0.5, 2.0, 48), 482, 5.0,
+                              cop=3.0, plan_power_kw=1.5, house=house)
+            mode = "system_identification" if override is not None else "eco"
+            power = 1.5 if override is None else override
+            if pending is not None:
+                key = mode if late else pending["mode"]
+                drawn = (3.0 if pending["command"] is _CP_CEIL else 1.5) * (1.0 + noise * rng.standard_normal())
+                _cp_dr.fold(store, drawn, (pending["power"], 0.0), _cp_params(), frozen=False,
+                            distorted=False, defrost=False, command=pending["command"],
+                            experiment_s=pending["when"] if key == "system_identification" else None)
+            pending = {"mode": mode, "power": power, "when": now.timestamp(),
+                       "command": _CP_CEIL if power >= 5.0 else _CP_MID}
+            prev_mode = mode
+    return store, prev_mode
+
+
+_cp_pump_leaky, _ = _cp_pump(_CP_LEAKY, 3)
+_cp_pump_tight, _ = _cp_pump(_CP_TIGHT, 6)
+_cp_pump_late, _ = _cp_pump(_CP_TIGHT, 6, late=True)
+_cp_top = lambda d: d.learned_max_kw(d.ceiling_since() or 0.0)  # noqa: E731
+R.check(
+    "the synthetic pump's known 3.0 kW maximum is recovered within 2 %: three 2.0 h "
+    "probes (four store samples each) and six 1.0 h probes (two each)",
+    len(_cp_pump_leaky.ceiling) == 12 and abs(_cp_top(_cp_pump_leaky) - 3.0) <= 0.06
+    and len(_cp_pump_tight.ceiling) == 12 and abs(_cp_top(_cp_pump_tight) - 3.0) <= 0.06
+    and max(d for d, _a in _cp_pump_leaky.samples) < 2.0 and _cp_pump_leaky.engaged is False,
+    f"leaky {len(_cp_pump_leaky.ceiling)} {_cp_top(_cp_pump_leaky)} "
+    f"tight {len(_cp_pump_tight.ceiling)} {_cp_top(_cp_pump_tight)}",
+)
+R.check(
+    "control: routed on the mode one interval late, the 1.0 h probes store one sample "
+    "each and a probe interval reaches the window",
+    len(_cp_pump_late.ceiling) == 6 and _cp_top(_cp_pump_late) is None
+    and max(d for d, _a in _cp_pump_late.samples) > 2.5,
+    f"late {len(_cp_pump_late.ceiling)} window {len(_cp_pump_late.samples)}",
+)
+
+# #2808: the outcome is recorded. The bulky view stays unrecorded; a compact
+# outcome row beside it is recorded, so a refusal has a history.
+_cp_status = _CpStatus.__new__(_CpStatus)
+_cp_status._data = lambda: {"system_identification": _cp_none.as_dict()}
+_cp_attrs = _CpStatus.extra_state_attributes.fget(_cp_status)
+R.check(
+    "the recorded outcome names the kind, the phase, the refusal and the last press, "
+    "outside the unrecorded set, where the bulky view stays",
+    _cp_attrs["system_identification_outcome"] == {
+        "kind": "fit", "phase": "idle", "held": None,
+        "reason": _cp_none.result.reason, "last_attempt": _CP_T0.isoformat(),
+    }
+    and "system_identification_outcome" not in _CpStatus._unrecorded_attributes
+    and "system_identification" in _CpStatus._unrecorded_attributes,
+    f"{_cp_attrs.get('system_identification_outcome')}",
+)
+
+
+# The boundaries, each at its exact edge (the mutation inventory's CMP_BOUND
+# operator moves each by one), and the arms the checks above leave implicit.
+_CP_EDGE_T = _CP_T0 - timedelta(days=30)
+R.check(
+    "the fit's clock is inclusive: exactly 30 days after its last run arms it; 200 learner "
+    "samples is converged, 199 is not",
+    _cp_sid.armable(_cp_cfg(), _CP_T0, _CP_EDGE_T, 150, None, None) == ("fit", "")
+    and _cp_sid.armable(_cp_cfg(), _CP_T0, None, 200, None, None)[0] is None
+    and _cp_sid.armable(_cp_cfg(), _CP_T0, None, 199, None, None) == ("fit", ""),
+)
+R.check(
+    "the probe's clock is inclusive: exactly 7 days after the newest store sample arms it",
+    _cp_sid.armable(_cp_cfg(), _CP_T0, None, 482, _cp_probe_store(4, 7), None) == ("ceiling_probe", ""),
+)
+_cp_fit200 = _cp_sid.SystemIdentification(_cp_cfg())
+_cp_fit200.arm(_CP_T0, learner_samples=0)
+R.check(
+    "a fit armed unconverged stands down at the start once the learner reaches 200 samples",
+    _cp_fit200.conditions_met(_CP_T0, 2.0, 0.5, np.linspace(0.5, 2.0, 48), 200)
+    == (False, "house already converged")
+    and _cp_fit200.conditions_met(_CP_T0, 2.0, 0.5, np.linspace(0.5, 2.0, 48), 199) == (True, "ready"),
+)
+R.check(
+    "the lapse is inclusive: a top exactly 45 days old still stands",
+    _cp_store([3.0] * 12).learned_max_kw(_CP_NOW + 45 * _CP_DAY) == 3.0,
+)
+_cp_edge_store = _cp_dr.DrawRange()
+for _cp_v in (1.0,) * 12:
+    _cp_edge_store.observe_idle(_cp_v)
+R.check(
+    "the store's edges: a set-point exactly CEILING_TOLERANCE_K under the ceiling is the "
+    "ceiling, a draw exactly at the idle margin is the idle draw",
+    _cp_edge_store.takes_ceiling(3.0, _CpNS(written_c=54.5, gate_c=25.0, ceiling_c=55.0))
+    and not _cp_edge_store.takes_ceiling(3.0, _CpNS(written_c=54.25, gate_c=25.0, ceiling_c=55.0))
+    and not _cp_edge_store.takes_ceiling(1.25, _CP_CEIL)
+    and _cp_edge_store.takes_ceiling(1.26, _CP_CEIL),
+)
+_cp_edge_over = _cp_store([3.0] * 12)
+for _cp_k in range(2):
+    _cp_fold(_cp_edge_over, 3.6, _CpNS(written_c=54.5, gate_c=25.0, ceiling_c=55.0), None)
+R.check(
+    "an overdraw counts at a set-point exactly CEILING_TOLERANCE_K under the ceiling",
+    len(_cp_edge_over.ceiling) == 0,
+)
+_cp_full = _cp_store([3.0] * 49)
+R.check(
+    "the store keeps the newest 48 samples (CEILING_WINDOW)",
+    len(_cp_full.ceiling) == 48 and _cp_full.ceiling[0][1] == _CP_NOW - 47 * 1800.0,
+)
+_cp_rows = _cp_dr.DrawRange.from_dict({
+    "ceiling": [[_cp_dr.RUNNING_FLOOR_KW, _CP_NOW], [0.26, _CP_NOW]], "overdraws": -1,
+})
+R.check(
+    "a stored row at the standby floor is dropped, one above it kept; a negative count reads 0",
+    [d for d, _t in _cp_rows.ceiling] == [0.26] and _cp_rows.overdraws == 0,
+)
+_cp_plain = _cp_arbitrate({"mode": "eco", "power": 0.0}, power_schedule=(5.0,))
+R.check(
+    "a plan action's power is not the experiment's: the plan's own step (5.0 kW) decides "
+    "duty and level although the action reads 0 kW",
+    _cp_plain[:2] == ("space", 55.0),
+    f"{_cp_plain}",
+)
+_cp_status._data = lambda: {}
+R.check(
+    "no experiment view, no outcome row",
+    _CpStatus.extra_state_attributes.fget(_cp_status)["system_identification_outcome"] is None,
+)
+from heatpump_optimizer.thermal_model import ThermalParameters as _CpPlant  # noqa: E402
+
+_cp_planted = _cp_sid.SystemIdentification(_cp_cfg())
+_cp_prior = _cp_planted.config.gains_prior_kw
+_cp_planted_ok = _cp_planted.arm(_CP_T0, plant=_CpPlant(), learner_samples=482, probe=_cp_dr.DrawRange())
+R.check(
+    "a probe armed on a declared plant seeds no fit: no slab pair, no re-seeded gains prior",
+    _cp_planted_ok and _cp_planted.kind == "ceiling_probe" and _cp_planted._slab_pair is None
+    and _cp_planted._slab_prior is None and _cp_planted.config.gains_prior_kw == _cp_prior,
+    f"{_cp_planted._slab_pair} {_cp_planted.config.gains_prior_kw} {_cp_prior}",
+)
+_cp_nofit = _cp_sid.SystemIdentification(_cp_cfg())
+_cp_nofit.arm(_CP_T0, learner_samples=482, probe=_cp_dr.DrawRange())
+_cp_nofit_out = [
+    _cp_nofit.step(_CP_T0 + timedelta(minutes=30 * k), 21.0, 2.0, 0.5, np.linspace(0.5, 2.0, 48),
+                   482, 5.0, cop=3.0, plan_power_kw=1.5, house=_CP_WEE)
+    for k in range(5)
+]
+R.check(
+    "a house no two-cycle probe fits is aborted at the step with the reason, injecting nothing "
+    "and starting no probe clock",
+    _cp_nofit_out == [None] * 5 and _cp_nofit.phase == _cp_sid.PHASE_ABORTED
+    and _cp_nofit.result.reason == "no probe step of two cycles fits within the comfort bound"
+    and _cp_nofit.probe_run is None,
+    f"{_cp_nofit_out} {_cp_nofit.phase} {_cp_nofit.result.reason!r}",
+)
+
+_cp_eq_over = _cp_store([3.0] * 12)
+for _cp_k in range(3):
+    _cp_fold(_cp_eq_over, (1.0 + _cp_dr.AGREE_TOLERANCE) * 3.0, _CP_CEIL, None)
+R.check(
+    "a draw exactly AGREE_TOLERANCE over the learned top is no overdraw",
+    len(_cp_eq_over.ceiling) == 12 and _cp_eq_over.overdraws == 0,
+)
+_cp_peak, _ = _cp_sid._predict_step_excursion_plant(
+    _CP_LEAKY, 21.0, 2.0, 15.0, 2.0, _cp_sid.SysIdConfig().relax_hours)
+R.check(
+    "the duration search's bound is inclusive: a peak exactly at the bound keeps the 2.0 h "
+    "step, one ulp under it shortens to 1.5 h",
+    _cp_sid.probe_step_hours(_CP_LEAKY, None, 21.0, 2.0, 15.0, _cp_cfg(max_excursion_c=_cp_peak)) == 2.0
+    and _cp_sid.probe_step_hours(
+        _CP_LEAKY, None, 21.0, 2.0, 15.0, _cp_cfg(max_excursion_c=float(np.nextafter(_cp_peak, 0.0)))
+    ) == 1.5,
+)
+
+
+def _cp_begin(house, cop=3.0, kind="fit"):
+    s = _cp_sid.SystemIdentification(_cp_cfg())
+    s.arm(_CP_T0, learner_samples=0 if kind == "fit" else 482, probe=_cp_dr.DrawRange())
+    s.phase, s._baseline_temp = _cp_sid.PHASE_SETTLING, 21.0
+    s._begin_step_phase(_CP_T0, 2.0, 5.0, cop, house)
+    return s.phase == _cp_sid.PHASE_STEP, s._step_power, s.phase
+
+
+R.check(
+    "the fit's degenerate-house fallback is strict: a loss or a mass of exactly 1e-6 is "
+    "no house to size on, and steps 0.3 of the maximum",
+    _cp_begin(_cp_sid.HousePlant(ua=1e-6, capacity=4.0, gains=0.3))[:2] == (True, 1.5)
+    and _cp_begin(_cp_sid.HousePlant(ua=0.12, capacity=1e-6, gains=0.3))[:2] == (True, 1.5),
+)
+_CP_FLOORED = _cp_sid.HousePlant(ua=0.02, capacity=0.3, gains=0.3, slab_mass=0.05, slab_transfer=0.24)
+R.check(
+    "the probe prices its heat at the fit's COP floor (0.1): at a reported COP of 0.05 the "
+    "0.5 kW it injects fits no step on this house, where 0.25 kW would fit 2.0 h",
+    _cp_begin(_CP_FLOORED, cop=0.05, kind="probe")[2] == _cp_sid.PHASE_ABORTED
+    and _cp_sid.probe_step_hours(_CP_FLOORED, None, 21.0, 2.0, 0.25, _cp_cfg()) == 2.0,
+)
+
+
+# The quiet windows: the solve honours them (off steps, the silent cap), and
+# the experiment's override replaces the solve's action, so the experiment
+# stands down inside one -- held while armed, aborted once started.
+from heatpump_optimizer import quiet_windows as _cp_qw  # noqa: E402
+from homeassistant.util import dt as _cp_dt  # noqa: E402
+
+R.check(
+    "a step inside a quiet off or silent window is named; outside one, or with none set, it is not",
+    _cp_qw.quiet_reason({"quiet_off_windows": "22:00-23:30"}, _CP_T0) == "inside a quiet off window"
+    and _cp_qw.quiet_reason({"quiet_silent_windows": "22:00-23:30"}, _CP_T0) == "inside a quiet silent window"
+    and _cp_qw.quiet_reason({"quiet_off_windows": "09:00-09:30"}, _CP_T0) is None
+    and _cp_qw.quiet_reason({}, _CP_T0) is None,
+)
+_cp_dt.freeze(_CP_T0)
+try:
+    _CP_ROOM = {"indoor_temp_entity": "sensor.room", "outdoor_temp_entity": "sensor.out"}
+    _cp_quiet = _cp_coord(**_CP_PROBE_CFG, **_CP_ROOM, quiet_off_windows="22:00-23:30")
+    _cp_loud = _cp_coord(**_CP_PROBE_CFG, **_CP_ROOM, quiet_off_windows="09:00-09:30")
+    for _cp_c in (_cp_quiet, _cp_loud):
+        _cp_c._learning_frozen = lambda *keys: None  # the freeze is the check above's
+    _cp_sysid_cycle(_cp_quiet)
+    _cp_quiet_armed = (_cp_quiet._sysid.phase, _cp_quiet._sysid.held)
+    _cp_quiet._sysid.phase = _cp_sid.PHASE_STEP
+    _cp_sysid_cycle(_cp_quiet)
+    _cp_sysid_cycle(_cp_loud)
+finally:
+    _cp_dt.freeze(None)
+R.check(
+    "inside a quiet off window the coordinator holds an armed probe with the reason and aborts "
+    "a started one; a window elsewhere in the day holds nothing",
+    _cp_quiet_armed == (_cp_sid.PHASE_ARMED, "inside a quiet off window")
+    and _cp_quiet._sysid.phase == _cp_sid.PHASE_ABORTED
+    and _cp_loud._sysid.held is None,
+    f"{_cp_quiet_armed} {_cp_quiet._sysid.phase} {_cp_loud._sysid.held!r} {_cp_loud._sysid.result.reason!r}",
+)
+
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 86133618a..192bef671 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -734,8 +734,8 @@ config_flow # r10-wood-notify: the wood_lighting_lead_minutes option joins the s
 # valve_storage_low_target, whose plan leaves move too: the reference's energy
 # anchors three of the space solve's starts, so a valved plan can land in
 # another basin. Unvalved fixtures do not move.
-coord_all_features  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
-coord_dhw  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
-coord_grid_fee  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
-coord_minimal  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
-coord_two_zone  # R10-COP-GATE p5 (A): model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view (additions only)
+coord_all_features  # R10-COP-GATE p5 (A) and R10-CEILING-PROBE (#2498, #2808), both additions only: model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view; the system_identification view gains kind, held, last_attempt, and model_status records a system_identification_outcome row beside it
+coord_dhw  # R10-COP-GATE p5 (A) and R10-CEILING-PROBE (#2498, #2808), both additions only: model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view; the system_identification view gains kind, held, last_attempt, and model_status records a system_identification_outcome row beside it
+coord_grid_fee  # R10-COP-GATE p5 (A) and R10-CEILING-PROBE (#2498, #2808), both additions only: model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view; the system_identification view gains kind, held, last_attempt, and model_status records a system_identification_outcome row beside it
+coord_minimal  # R10-COP-GATE p5 (A) and R10-CEILING-PROBE (#2498, #2808), both additions only: model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view; the system_identification view gains kind, held, last_attempt, and model_status records a system_identification_outcome row beside it
+coord_two_zone  # R10-COP-GATE p5 (A) and R10-CEILING-PROBE (#2498, #2808), both additions only: model_status cop row gains cop_observability, cop_refusal, measured_cop_at, copied from the learning view; the system_identification view gains kind, held, last_attempt, and model_status records a system_identification_outcome row beside it
diff --git a/tests/golden/coord_all_features.json b/tests/golden/coord_all_features.json
index 67a6c297e..b3b42b419 100644
--- a/tests/golden/coord_all_features.json
+++ b/tests/golden/coord_all_features.json
@@ -572,6 +572,9 @@
   "stale_inputs": [],
   "system_identification": {
    "active": false,
+   "held": null,
+   "kind": "fit",
+   "last_attempt": null,
    "last_run": null,
    "phase": "idle",
    "result": {
@@ -2130,6 +2133,9 @@
     },
     "system_identification": {
      "active": false,
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
      "last_run": null,
      "phase": "idle",
      "result": {
@@ -2144,6 +2150,13 @@
      },
      "samples": 0
     },
+    "system_identification_outcome": {
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
+     "phase": "idle",
+     "reason": ""
+    },
     "tank_cooling": {
      "learned": false,
      "rate_c_per_h": 0.3,
diff --git a/tests/golden/coord_dhw.json b/tests/golden/coord_dhw.json
index f108e11ac..1895c8ffe 100644
--- a/tests/golden/coord_dhw.json
+++ b/tests/golden/coord_dhw.json
@@ -558,6 +558,9 @@
   "stale_inputs": [],
   "system_identification": {
    "active": false,
+   "held": null,
+   "kind": "fit",
+   "last_attempt": null,
    "last_run": null,
    "phase": "idle",
    "result": {
@@ -2051,6 +2054,9 @@
     },
     "system_identification": {
      "active": false,
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
      "last_run": null,
      "phase": "idle",
      "result": {
@@ -2065,6 +2071,13 @@
      },
      "samples": 0
     },
+    "system_identification_outcome": {
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
+     "phase": "idle",
+     "reason": ""
+    },
     "tank_cooling": {
      "learned": false,
      "rate_c_per_h": 0.3,
diff --git a/tests/golden/coord_grid_fee.json b/tests/golden/coord_grid_fee.json
index da1e9b46d..673db3b96 100644
--- a/tests/golden/coord_grid_fee.json
+++ b/tests/golden/coord_grid_fee.json
@@ -493,6 +493,9 @@
   "stale_inputs": [],
   "system_identification": {
    "active": false,
+   "held": null,
+   "kind": "fit",
+   "last_attempt": null,
    "last_run": null,
    "phase": "idle",
    "result": {
@@ -1894,6 +1897,9 @@
     },
     "system_identification": {
      "active": false,
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
      "last_run": null,
      "phase": "idle",
      "result": {
@@ -1908,6 +1914,13 @@
      },
      "samples": 0
     },
+    "system_identification_outcome": {
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
+     "phase": "idle",
+     "reason": ""
+    },
     "tank_cooling": null
    },
    "native_value": "learning"
diff --git a/tests/golden/coord_minimal.json b/tests/golden/coord_minimal.json
index 3ad9d21bb..81cf31074 100644
--- a/tests/golden/coord_minimal.json
+++ b/tests/golden/coord_minimal.json
@@ -493,6 +493,9 @@
   "stale_inputs": [],
   "system_identification": {
    "active": false,
+   "held": null,
+   "kind": "fit",
+   "last_attempt": null,
    "last_run": null,
    "phase": "idle",
    "result": {
@@ -1894,6 +1897,9 @@
     },
     "system_identification": {
      "active": false,
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
      "last_run": null,
      "phase": "idle",
      "result": {
@@ -1908,6 +1914,13 @@
      },
      "samples": 0
     },
+    "system_identification_outcome": {
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
+     "phase": "idle",
+     "reason": ""
+    },
     "tank_cooling": null
    },
    "native_value": "learning"
diff --git a/tests/golden/coord_two_zone.json b/tests/golden/coord_two_zone.json
index d0bbc0ebd..6a947b460 100644
--- a/tests/golden/coord_two_zone.json
+++ b/tests/golden/coord_two_zone.json
@@ -503,6 +503,9 @@
   "stale_inputs": [],
   "system_identification": {
    "active": false,
+   "held": null,
+   "kind": "fit",
+   "last_attempt": null,
    "last_run": null,
    "phase": "idle",
    "result": {
@@ -1940,6 +1943,9 @@
     },
     "system_identification": {
      "active": false,
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
      "last_run": null,
      "phase": "idle",
      "result": {
@@ -1954,6 +1960,13 @@
      },
      "samples": 0
     },
+    "system_identification_outcome": {
+     "held": null,
+     "kind": "fit",
+     "last_attempt": null,
+     "phase": "idle",
+     "reason": ""
+    },
     "tank_cooling": null
    },
    "native_value": "learning"
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.4aad47f0.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.4aad47f0.json
new file mode 100644
index 000000000..5da57da23
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.4aad47f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 4aad47f0",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_OVERDRAWS = 2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_OVERDRAWS = 4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.64815056.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.64815056.json
new file mode 100644
index 000000000..0777810c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.64815056.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST 64815056",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_WINDOW = 48",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_WINDOW = 96`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.c9d292c3.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.c9d292c3.json
new file mode 100644
index 000000000..7386fb447
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.c9d292c3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST c9d292c3",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_LAPSE_DAYS = 45.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_LAPSE_DAYS = 90.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.db57fbad.json b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.db57fbad.json
new file mode 100644
index 000000000..ac2dc8191
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/@module.CONST.db57fbad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:<module> CONST db57fbad",
+  "killed_by": "tests/features.py",
+  "old": "CEILING_MIN_SAMPLES = 12",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CEILING_MIN_SAMPLES = 24`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.BOOLOP.c78c910d.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.BOOLOP.c78c910d.json
new file mode 100644
index 000000000..e16476457
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.BOOLOP.c78c910d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn BOOLOP c78c910d",
+  "killed_by": "tests/features.py",
+  "old": "        at_ceiling = command is not None and command[0] >= command[1] - CEILING_TOLERANCE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`at_ceiling = command is not None or command[0] >= command[1] - CEILING_TOLERANCE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.18307452.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.18307452.json
new file mode 100644
index 000000000..c47e87d44
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.18307452.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND 18307452",
+  "killed_by": "tests/features.py",
+  "old": "        if not at_ceiling or len(self.ceiling) < CEILING_MIN_SAMPLES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not at_ceiling or len(self.ceiling) <= CEILING_MIN_SAMPLES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c1c89739.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c1c89739.json
new file mode 100644
index 000000000..d26e8d398
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c1c89739.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND c1c89739",
+  "killed_by": "tests/features.py",
+  "old": "        if self.overdraws >= CEILING_OVERDRAWS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if self.overdraws > CEILING_OVERDRAWS:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c78c910d.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c78c910d.json
new file mode 100644
index 000000000..c54a97de8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.c78c910d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND c78c910d",
+  "killed_by": "tests/features.py",
+  "old": "        at_ceiling = command is not None and command[0] >= command[1] - CEILING_TOLERANCE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`at_ceiling = command is not None and command[0] > command[1] - CEILING_TOLERANCE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.ea13b93a.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.ea13b93a.json
new file mode 100644
index 000000000..3a724fcb4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.CMP_BOUND.ea13b93a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn CMP_BOUND ea13b93a",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw > (1.0 + AGREE_TOLERANCE) * self._ceiling_median():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if drawn_kw >= (1.0 + AGREE_TOLERANCE) * self._ceiling_median():`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.18307452.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.18307452.json
new file mode 100644
index 000000000..0d460606c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.18307452.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn GUARD_OFF 18307452",
+  "killed_by": "tests/features.py",
+  "old": "        if not at_ceiling or len(self.ceiling) < CEILING_MIN_SAMPLES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.c1c89739.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.c1c89739.json
new file mode 100644
index 000000000..3f901712b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.c1c89739.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn GUARD_OFF c1c89739",
+  "killed_by": "tests/structure.py",
+  "old": "        if self.overdraws >= CEILING_OVERDRAWS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.ea13b93a.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.ea13b93a.json
new file mode 100644
index 000000000..fd869cf0e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange._overdrawn.GUARD_OFF.ea13b93a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange._overdrawn GUARD_OFF ea13b93a",
+  "killed_by": "tests/features.py",
+  "old": "        if drawn_kw > (1.0 + AGREE_TOLERANCE) * self._ceiling_median():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.above_idle_kw.RETURN_DEL.57f929a4.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.above_idle_kw.RETURN_DEL.57f929a4.json
new file mode 100644
index 000000000..7129d0aca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.above_idle_kw.RETURN_DEL.57f929a4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.above_idle_kw RETURN_DEL 57f929a4",
+  "killed_by": "tests/features.py",
+  "old": "        return 0.0 if idle is None else IDLE_MARGIN * idle",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.ceiling_since.RETURN_DEL.14a5174b.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.ceiling_since.RETURN_DEL.14a5174b.json
new file mode 100644
index 000000000..0bdfaec88
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.ceiling_since.RETURN_DEL.14a5174b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.ceiling_since RETURN_DEL 14a5174b",
+  "killed_by": "tests/features.py",
+  "old": "        return self.ceiling[-1][1] if self.ceiling else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.36f7cc06.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.36f7cc06.json
new file mode 100644
index 000000000..c7b5655d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.36f7cc06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw CMP_BOUND 36f7cc06",
+  "killed_by": "tests/features.py",
+  "old": "        if len(self.ceiling) < CEILING_MIN_SAMPLES or newest is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(self.ceiling) <= CEILING_MIN_SAMPLES or newest is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.793578eb.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.793578eb.json
new file mode 100644
index 000000000..d268c7882
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.CMP_BOUND.793578eb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw CMP_BOUND 793578eb",
+  "killed_by": "tests/features.py",
+  "old": "        if not 0.0 <= now_s - newest <= CEILING_LAPSE_DAYS * 86400.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not 0.0 < now_s - newest <= CEILING_LAPSE_DAYS * 86400.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.36f7cc06.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.36f7cc06.json
new file mode 100644
index 000000000..ce3b177e8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.36f7cc06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw GUARD_OFF 36f7cc06",
+  "killed_by": "tests/features.py",
+  "old": "        if len(self.ceiling) < CEILING_MIN_SAMPLES or newest is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.793578eb.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.793578eb.json
new file mode 100644
index 000000000..24f972471
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.GUARD_OFF.793578eb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw GUARD_OFF 793578eb",
+  "killed_by": "tests/structure.py",
+  "old": "        if not 0.0 <= now_s - newest <= CEILING_LAPSE_DAYS * 86400.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.RETURN_DEL.1f3a81af.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.RETURN_DEL.1f3a81af.json
new file mode 100644
index 000000000..0142443e0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.learned_max_kw.RETURN_DEL.1f3a81af.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.learned_max_kw RETURN_DEL 1f3a81af",
+  "killed_by": "tests/features.py",
+  "old": "        return self._ceiling_median()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.5dfdeab2.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.5dfdeab2.json
new file mode 100644
index 000000000..c4b0b9147
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.5dfdeab2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.takes_ceiling CMP_BOUND 5dfdeab2",
+  "killed_by": "tests/features.py",
+  "old": "            and command.written_c >= command.ceiling_c - CEILING_TOLERANCE_K",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and command.written_c > command.ceiling_c - CEILING_TOLERANCE_K`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.ace88f8a.json b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.ace88f8a.json
new file mode 100644
index 000000000..f1b5d4a21
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/DrawRange.takes_ceiling.CMP_BOUND.ace88f8a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:DrawRange.takes_ceiling CMP_BOUND ace88f8a",
+  "killed_by": "tests/features.py",
+  "old": "            and drawn_kw > self.above_idle_kw()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and drawn_kw >= self.above_idle_kw()`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.CMP_BOUND.ef224f84.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.CMP_BOUND.ef224f84.json
new file mode 100644
index 000000000..106bdfb83
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.CMP_BOUND.ef224f84.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_ceiling CMP_BOUND ef224f84",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(drawn) and np.isfinite(when) and drawn > RUNNING_FLOOR_KW:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if np.isfinite(drawn) and np.isfinite(when) and drawn >= RUNNING_FLOOR_KW:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.GUARD_OFF.ef224f84.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.GUARD_OFF.ef224f84.json
new file mode 100644
index 000000000..b0843d4d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.GUARD_OFF.ef224f84.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_ceiling GUARD_OFF ef224f84",
+  "killed_by": "tests/features.py",
+  "old": "        if np.isfinite(drawn) and np.isfinite(when) and drawn > RUNNING_FLOOR_KW:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.RETURN_DEL.23640190.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.RETURN_DEL.23640190.json
new file mode 100644
index 000000000..5931520a6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_ceiling.RETURN_DEL.23640190.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_ceiling RETURN_DEL 23640190",
+  "killed_by": "tests/features.py",
+  "old": "    return rows",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.CLAMP_DROP.9ccb0e19.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.CLAMP_DROP.9ccb0e19.json
new file mode 100644
index 000000000..ff66578c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.CLAMP_DROP.9ccb0e19.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_overdraws CLAMP_DROP 9ccb0e19",
+  "killed_by": "tests/features.py",
+  "old": "    return max(raw, 0) if type(raw) is int else 0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (raw) if type(raw) is int else 0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.RETURN_DEL.9ccb0e19.json b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.RETURN_DEL.9ccb0e19.json
new file mode 100644
index 000000000..c674138b7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/_stored_overdraws.RETURN_DEL.9ccb0e19.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:_stored_overdraws RETURN_DEL 9ccb0e19",
+  "killed_by": "tests/features.py",
+  "old": "    return max(raw, 0) if type(raw) is int else 0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
new file mode 100644
index 000000000..704b09b3c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/fold.BOOLOP.dc29709b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold BOOLOP dc29709b",
+  "killed_by": "tests/features.py",
+  "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if experiment_s is not None or draw.takes_ceiling(drawn_kw, command):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json b/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
new file mode 100644
index 000000000..33b15211f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/draw_range.py/fold.GUARD_OFF.dc29709b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/draw_range.py:fold GUARD_OFF dc29709b",
+  "killed_by": "tests/structure.py",
+  "old": "    if experiment_s is not None and draw.takes_ceiling(drawn_kw, command):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.GUARD_OFF.755ef4b5.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.GUARD_OFF.755ef4b5.json
new file mode 100644
index 000000000..4e586a874
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.GUARD_OFF.755ef4b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_experiment_kw GUARD_OFF 755ef4b5",
+  "killed_by": "tests/features.py",
+  "old": "    if action.get(\"mode\") != \"system_identification\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=64."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.RETURN_DEL.cd567d85.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.RETURN_DEL.cd567d85.json
new file mode 100644
index 000000000..089f8a6e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_experiment_kw.RETURN_DEL.cd567d85.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_experiment_kw RETURN_DEL cd567d85",
+  "killed_by": "tests/features.py",
+  "old": "    return finite_float(action.get(\"power\")) or 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_command.GUARD_OFF.039fc422.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_command.GUARD_OFF.039fc422.json
new file mode 100644
index 000000000..879a421fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_flow_command.GUARD_OFF.039fc422.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_flow_command GUARD_OFF 039fc422",
+  "killed_by": "tests/features.py",
+  "old": "    if written is None or inp.mode == MODE_OFF or not flow_setpoint_driven(inp.config):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.44d997bd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.44d997bd.json
deleted file mode 100644
index cdd593b2f..000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.44d997bd.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_duty GUARD_OFF 44d997bd",
-  "killed_by": "tests/features.py",
-  "old": "    if (inp.action or {}).get(\"mode\") == \"system_identification\":",
-  "reason": "pump-duty arbiter revision; `if (coord._current_action or {}).get(\"mode\") == \"system_identification\":` -> `if False:` fails 1 of the arbiter checks in tests/features.py's pump-duty arbiter section, against a green baseline. Measured by driving that section, 2026-09-24. Re-measured on a git-archive export of 13a82a9d, 2026-10-05: 3 of 3698 feature checks fail, against the export baseline's two artefacts (#363 recorded_at, R9-F2.1 P3). Re-keyed by R9-EG-B6 (#1739): the collaborator-interface rename made the line `    if (coord._current_action or {}).get(\"mode\") == \"system_identification\":` into `    if (inp.action or {}).get(\"mode\") == \"system_identification\":`."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.be5476ee.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.be5476ee.json
new file mode 100644
index 000000000..1117d710b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_duty.GUARD_OFF.be5476ee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_duty GUARD_OFF be5476ee",
+  "killed_by": "tests/features.py",
+  "old": "    if experiment is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/quiet_windows.py/quiet_reason.RETURN_DEL.76b90284.json b/tests/mutation_ledger/killed_by/quiet_windows.py/quiet_reason.RETURN_DEL.76b90284.json
new file mode 100644
index 000000000..3f953a85d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/quiet_windows.py/quiet_reason.RETURN_DEL.76b90284.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/quiet_windows.py:quiet_reason RETURN_DEL 76b90284",
+  "killed_by": "tests/features.py",
+  "old": "    return {ACTION_OFF: \"inside a quiet off window\", ACTION_SILENT: \"inside a quiet silent window\"}.get(code)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/_sysid_outcome.GUARD_OFF.bc3478fe.json b/tests/mutation_ledger/killed_by/sensor.py/_sysid_outcome.GUARD_OFF.bc3478fe.json
new file mode 100644
index 000000000..cde5bd3d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/_sysid_outcome.GUARD_OFF.bc3478fe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:_sysid_outcome GUARD_OFF bc3478fe",
+  "killed_by": "tests/features.py",
+  "old": "    if not v:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.bb90ed59.json b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.bb90ed59.json
new file mode 100644
index 000000000..800cb0787
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.bb90ed59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:<module> CONST bb90ed59",
+  "killed_by": "tests/features.py",
+  "old": "PROBE_DAYS_UNLEARNED = 7.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROBE_DAYS_UNLEARNED = 14.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.de8e6cf0.json b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.de8e6cf0.json
new file mode 100644
index 000000000..c9eb8bfe5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.de8e6cf0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:<module> CONST de8e6cf0",
+  "killed_by": "tests/features.py",
+  "old": "PROBE_DAYS_LEARNED = 30.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROBE_DAYS_LEARNED = 60.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.e3d1827c.json b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.e3d1827c.json
new file mode 100644
index 000000000..320edcdff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/@module.CONST.e3d1827c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:<module> CONST e3d1827c",
+  "killed_by": "tests/features.py",
+  "old": "PROBE_MIN_CYCLES = 2",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`PROBE_MIN_CYCLES = 4`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CLAMP_DROP.b1d752e0.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CLAMP_DROP.b1d752e0.json
new file mode 100644
index 000000000..b32665650
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CLAMP_DROP.b1d752e0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase CLAMP_DROP b1d752e0",
+  "killed_by": "tests/features.py",
+  "old": "                max_power_kw * max(cop, 0.1), self.config,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`max_power_kw * (cop), self.config,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.3fa6c8a7.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.3fa6c8a7.json
new file mode 100644
index 000000000..4948ac3cd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.3fa6c8a7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase CMP_BOUND 3fa6c8a7",
+  "killed_by": "tests/features.py",
+  "old": "            and house.ua > 1e-6",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and house.ua >= 1e-6`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.cbebfd71.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.cbebfd71.json
new file mode 100644
index 000000000..a8fd16767
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.CMP_BOUND.cbebfd71.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase CMP_BOUND cbebfd71",
+  "killed_by": "tests/features.py",
+  "old": "            and house.capacity > 1e-6",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`and house.capacity >= 1e-6`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.74462097.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.74462097.json
new file mode 100644
index 000000000..85d538823
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.74462097.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase GUARD_OFF 74462097",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.d23aa688.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.d23aa688.json
new file mode 100644
index 000000000..f0eb5ba38
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._begin_step_phase.GUARD_OFF.d23aa688.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase GUARD_OFF d23aa688",
+  "killed_by": "tests/features.py",
+  "old": "            if hours is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._end_step.GUARD_OFF.74462097.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._end_step.GUARD_OFF.74462097.json
new file mode 100644
index 000000000..447f4322b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._end_step.GUARD_OFF.74462097.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._end_step GUARD_OFF 74462097",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._finish.GUARD_OFF.74462097.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._finish.GUARD_OFF.74462097.json
new file mode 100644
index 000000000..16d1e683f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification._finish.GUARD_OFF.74462097.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._finish GUARD_OFF 74462097",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.BOOLOP.7aaadeee.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.BOOLOP.7aaadeee.json
new file mode 100644
index 000000000..f78ad480a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.BOOLOP.7aaadeee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm BOOLOP 7aaadeee",
+  "killed_by": "tests/features.py",
+  "old": "        if plant is not None and kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if plant is not None or kind == KIND_PROBE:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=36."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.7aaadeee.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.7aaadeee.json
new file mode 100644
index 000000000..a3e969476
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.7aaadeee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF 7aaadeee",
+  "killed_by": "tests/features.py",
+  "old": "        if plant is not None and kind == KIND_PROBE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.cd63f7f7.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.cd63f7f7.json
new file mode 100644
index 000000000..5ba2f1baf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.cd63f7f7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF cd63f7f7",
+  "killed_by": "tests/features.py",
+  "old": "        if kind is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.ee0020d8.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.ee0020d8.json
new file mode 100644
index 000000000..0aa563d7e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.GUARD_OFF.ee0020d8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm GUARD_OFF ee0020d8",
+  "killed_by": "tests/features.py",
+  "old": "        elif plant is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=40."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.RETURN_DEL.7d8da489~3.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.RETURN_DEL.7d8da489~3.json
new file mode 100644
index 000000000..68827b403
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.arm.RETURN_DEL.7d8da489~3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.arm RETURN_DEL 7d8da489#3",
+  "killed_by": "tests/features.py",
+  "old": "            return False",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.BOOLOP.9a396f27.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.BOOLOP.9a396f27.json
new file mode 100644
index 000000000..5541ac2e7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.BOOLOP.9a396f27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met BOOLOP 9a396f27",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_FIT and learner_samples >= cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self.kind == KIND_FIT or learner_samples >= cfg.converged_samples:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.9a396f27.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.9a396f27.json
new file mode 100644
index 000000000..4e4bf6e48
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.9a396f27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met CMP_BOUND 9a396f27",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_FIT and learner_samples >= cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if self.kind == KIND_FIT and learner_samples > cfg.converged_samples:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.e36b992b.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.e36b992b.json
new file mode 100644
index 000000000..86e50ff5f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.CMP_BOUND.e36b992b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met CMP_BOUND e36b992b",
+  "killed_by": "tests/features.py",
+  "old": "            price_horizon is None or not len(price_horizon) or np.ptp(price_horizon) <= 0.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`price_horizon is None or not len(price_horizon) or np.ptp(price_horizon) < 0.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.9a396f27.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.9a396f27.json
new file mode 100644
index 000000000..fa1cb15e0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.9a396f27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met GUARD_OFF 9a396f27",
+  "killed_by": "tests/features.py",
+  "old": "        if self.kind == KIND_FIT and learner_samples >= cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.f28ecccb.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.f28ecccb.json
deleted file mode 100644
index cec38bc41..000000000
--- a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.conditions_met.GUARD_OFF.f28ecccb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.conditions_met GUARD_OFF f28ecccb",
-  "killed_by": "tests/features.py",
-  "old": "        if learner_samples >= cfg.converged_samples:",
-  "reason": "Recorded by `mutation_table.py --drain` against f637d24ab5d17e93cdabba092cd9245f440741f6: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.stand_down.GUARD_OFF.d35c12b9.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.stand_down.GUARD_OFF.d35c12b9.json
new file mode 100644
index 000000000..4957d091e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.stand_down.GUARD_OFF.d35c12b9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.stand_down GUARD_OFF d35c12b9",
+  "killed_by": "tests/features.py",
+  "old": "        if self.phase == PHASE_ARMED:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.27c08492.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.27c08492.json
new file mode 100644
index 000000000..a2c4179c8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.27c08492.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step CMP_BOUND 27c08492",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= self._step_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if elapsed > self._step_hours:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.a7d6e527.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.a7d6e527.json
new file mode 100644
index 000000000..fc267b14c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.CMP_BOUND.a7d6e527.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step CMP_BOUND a7d6e527",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= cfg.settle_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if elapsed > cfg.settle_hours:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.27c08492.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.27c08492.json
new file mode 100644
index 000000000..1f5e693c1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.27c08492.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step GUARD_OFF 27c08492",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= self._step_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.a7d6e527.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.a7d6e527.json
new file mode 100644
index 000000000..e11722b69
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.a7d6e527.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step GUARD_OFF a7d6e527",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= cfg.settle_hours:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=15."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.160147fc.json b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.160147fc.json
new file mode 100644
index 000000000..c78d487e2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.160147fc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable BOOLOP 160147fc",
+  "killed_by": "tests/features.py",
+  "old": "        (t for t in (probe.ceiling_since(), probe_run and probe_run.timestamp()) if t),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`(t for t in (probe.ceiling_since(), probe_run or probe_run.timestamp()) if t),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.55d7d1a6.json b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.55d7d1a6.json
new file mode 100644
index 000000000..8f3cbee38
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.BOOLOP.55d7d1a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable BOOLOP 55d7d1a6",
+  "killed_by": "tests/features.py",
+  "old": "    if since is not None and (now.timestamp() - since) / 86400.0 < wait:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if since is not None or (now.timestamp() - since) / 86400.0 < wait:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.14a0382a.json b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.14a0382a.json
new file mode 100644
index 000000000..ed0878102
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.14a0382a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable CMP_BOUND 14a0382a",
+  "killed_by": "tests/features.py",
+  "old": "        if days is None or days >= cfg.min_days_between_runs:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if days is None or days > cfg.min_days_between_runs:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.55d7d1a6.json b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.55d7d1a6.json
new file mode 100644
index 000000000..d2f2a5dfc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.55d7d1a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable CMP_BOUND 55d7d1a6",
+  "killed_by": "tests/features.py",
+  "old": "    if since is not None and (now.timestamp() - since) / 86400.0 < wait:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if since is not None and (now.timestamp() - since) / 86400.0 <= wait:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.9fa5c399.json b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.9fa5c399.json
new file mode 100644
index 000000000..1503571f5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.CMP_BOUND.9fa5c399.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable CMP_BOUND 9fa5c399",
+  "killed_by": "tests/features.py",
+  "old": "    if learner_samples < cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if learner_samples <= cfg.converged_samples:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.14a0382a.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.14a0382a.json
new file mode 100644
index 000000000..7ea77255a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.14a0382a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF 14a0382a",
+  "killed_by": "tests/features.py",
+  "old": "        if days is None or days >= cfg.min_days_between_runs:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.55d7d1a6.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.55d7d1a6.json
new file mode 100644
index 000000000..8cf4f87e5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.55d7d1a6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF 55d7d1a6",
+  "killed_by": "tests/features.py",
+  "old": "    if since is not None and (now.timestamp() - since) / 86400.0 < wait:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.9fa5c399.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.9fa5c399.json
new file mode 100644
index 000000000..dceebea0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.9fa5c399.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF 9fa5c399",
+  "killed_by": "tests/features.py",
+  "old": "    if learner_samples < cfg.converged_samples:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.c3d7afef.json b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.c3d7afef.json
new file mode 100644
index 000000000..0d7802b74
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.GUARD_OFF.c3d7afef.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable GUARD_OFF c3d7afef",
+  "killed_by": "tests/features.py",
+  "old": "    if probe is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.af591f59.json b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.af591f59.json
new file mode 100644
index 000000000..3a03a5c3b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.af591f59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable RETURN_DEL af591f59",
+  "killed_by": "tests/features.py",
+  "old": "        return None, f\"{why}; the ceiling probe ran {days:.1f} days ago, waiting for the {wait:.0f} day minimum\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.f69f5d2a.json b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.f69f5d2a.json
new file mode 100644
index 000000000..f1ec45b5b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/armable.RETURN_DEL.f69f5d2a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:armable RETURN_DEL f69f5d2a",
+  "killed_by": "tests/features.py",
+  "old": "    return KIND_PROBE, \"\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.CMP_BOUND.dc9c2ceb.json b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.CMP_BOUND.dc9c2ceb.json
new file mode 100644
index 000000000..c7599c41a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.CMP_BOUND.dc9c2ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:probe_step_hours CMP_BOUND dc9c2ceb",
+  "killed_by": "tests/features.py",
+  "old": "        if peak <= bound:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if peak < bound:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.GUARD_OFF.dc9c2ceb.json b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.GUARD_OFF.dc9c2ceb.json
new file mode 100644
index 000000000..5dbb4ead6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/probe_step_hours.GUARD_OFF.dc9c2ceb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:probe_step_hours GUARD_OFF dc9c2ceb",
+  "killed_by": "tests/features.py",
+  "old": "        if peak <= bound:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.BOOLOP.039bf6ed.json b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.BOOLOP.039bf6ed.json
new file mode 100644
index 000000000..c41d09e35
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.BOOLOP.039bf6ed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ceiling_probe_install BOOLOP 039bf6ed",
+  "killed_by": "tests/features.py",
+  "old": "    return flow_setpoint_driven(config) and probe_install(config).measured_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return flow_setpoint_driven(config) or probe_install(config).measured_power`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.RETURN_DEL.039bf6ed.json b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.RETURN_DEL.039bf6ed.json
new file mode 100644
index 000000000..c7e3296a2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ceiling_probe_install.RETURN_DEL.039bf6ed.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ceiling_probe_install RETURN_DEL 039bf6ed",
+  "killed_by": "tests/features.py",
+  "old": "    return flow_setpoint_driven(config) and probe_install(config).measured_power",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/survivor_triage/sysid.py/SystemIdentification._begin_step_phase.RETURN_DEL.a9322b69~2.json b/tests/mutation_ledger/survivor_triage/sysid.py/SystemIdentification._begin_step_phase.RETURN_DEL.a9322b69~2.json
deleted file mode 100644
index 2b3b40864..000000000
--- a/tests/mutation_ledger/survivor_triage/sysid.py/SystemIdentification._begin_step_phase.RETURN_DEL.a9322b69~2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification._begin_step_phase RETURN_DEL a9322b69#2",
-  "old": "                return False",
-  "reason": "R9 F4.2: equivalent. The line follows `self.abort(unadoptable)`, which sets phase PHASE_ABORTED (the method set PHASE_STEP on entry, so abort's `if not self.active` does not skip it). Deleting the return runs only the `injecting` debug log and `return True`; the one caller (SystemIdentification.step's settle branch) returns None on both return values, and the phase is ABORTED either way, so no step is injected and the published result is the abort's. Measured on a copy of the tree with the line replaced by `pass`: the #1524 through R9-P5 blocks of tests/features.py read fails=0, including `R9-P5 (D2-s4-81): a night the noise-free prediction stops never drives the pump above its hold power`, which the abort itself does pin (with the abort replaced by a bare result, that check and the D2-s4-81 check both fail), 2026-09-27.",
-  "verdict": "equivalent"
-}
diff --git a/tests/mutation_ledger/survivor_triage/sysid.py/probe_step_hours.RETURN_DEL.da9e8e97.json b/tests/mutation_ledger/survivor_triage/sysid.py/probe_step_hours.RETURN_DEL.da9e8e97.json
new file mode 100644
index 000000000..62d76b791
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/sysid.py/probe_step_hours.RETURN_DEL.da9e8e97.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:probe_step_hours RETURN_DEL da9e8e97",
+  "old": "    return None",
+  "reason": "R10-CEILING-PROBE: the last statement of probe_step_hours, after the loop that returns the first fitting duration. Deleting `return None` leaves the function to fall off its end, which returns None: indistinguishable at every input. Measured: the mutant passes all 55 checks of the R10-CEILING-PROBE block of tests/features.py (features_block.py), whose duration-search checks drive the None arm (a house no two-cycle step fits). Kept: the explicit `None` names the refusal arm the docstring states.",
+  "verdict": "equivalent"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f85a64423..95ffc0962 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17653,
+ "class_excess_loc": 17649,
  "const_modules_over_50": 3,
  "coordinator_attrs": 142,
  "coordinator_multiassigned_attrs": 109,
@@ -11,7 +11,7 @@
  "functions_cc_over_25": 8,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 8059,
+ "max_class_loc": 8056,
  "max_method_loc": 373,
  "methods_over_150": 15,
  "methods_over_200": 8,

