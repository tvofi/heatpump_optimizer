# Review packet #3728
head: 0bfce347d8aa2d26f8401f656576a044ef6e815f
base: a8efe1d1c2a8f1e0b44cdf1046a0ea4ca2155a3b

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=136936933500 success
arch-score / arch-score id=136936705283 success
arm id=136936476251 skipped
budget-raise-gate / budget-raise-gate id=136936705385 success
cancel-superseded id=136936434379 success
codeql id=136936706655 skipped
codeql / Analyze (actions) id=136936700264 success
codeql / Analyze (javascript-typescript) id=136936700299 success
codeql / Analyze (python) id=136936700277 success
gate id=136937205840 failure
governance id=136936707209 skipped
governance / env-matrix id=136936700339 in_progress
governance / instrument-self-tests id=136936700262 in_progress
governance / policy-docs id=136936700303 success
governance / record id=136936701903 skipped
governance / wave-script id=136936700276 success
hassfest id=136936707047 skipped
hassfest / hassfest id=136936700274 success
kernel-points id=136936706542 skipped
pr-contract id=136937206900 skipped
prelude id=136936434118 success
refresh id=136936434361 success
sweep-self id=136937495917 skipped
tests id=136936707728 skipped
tests / arch-instrument id=136936985247 success
tests / briefs id=136936700410 success
tests / browser id=136936985129 in_progress
tests / closure-scope id=136936700379 success
tests / closures id=136936985266 in_progress
tests / coverage id=136936985196 in_progress
tests / fast (3.14) id=136936985264 in_progress
tests / mutation id=136936700381 in_progress
tests / nightly-ha id=136936986238 skipped
tests / nightly-status id=136936700396 success
tests / replay id=136936985273 in_progress
tests / typing id=136936985142 success
validate id=136936707157 skipped
validate / validate-hacs id=136936700154 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 136936700262: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at 0bfce347d8aa2d26f8401f656576a044ef6e815f in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item 8e61967e: dismissed:owed to R11-SEAM-actuation-release (the second to merge re-runs the restore harness; it is second while its branch is off main)
NOTE body item 96de72e6: dismissed:ADR-001 part 2 already binds both groups to plan_step's step owner, and the barrier enforces it
NOTE body item 96426282: dismissed:the D7-s3 finder's recorded non-finding (its report: reported and not raised, since no pair of production predicates answers differently for a state Home Assistant delivers)
NOTE body item 0ec2300d: dismissed:reported in this seat's return to the orchestrator, which owns the instrument
CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 29 script(s) run, 4 scoped out.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_kernel_step_agree.py $EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py
             `dev/audit/harnesses/r11_kernel_step_agree.py` is in the tree at this head
  unverified git archive
             `git archive` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/archscore/score.py --diff bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_kernel_step_agree.py --seams
             `dev/audit/harnesses/r11_kernel_step_agree.py` is in the tree at this head
  unverified git grep -n 'astimezone(' -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n 'astimezone()' -- custom_components
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/closure.py select --diff bc658f9ded
             `tests/closure.py` is in the tree at this head
  ok         tests/open_meteo.py
             `tests/open_meteo.py` is in the tree at this head
  ok         HASTUB_TZ=Europe/Stockholm tests/dst_checks.py
             `tests/dst_checks.py` is in the tree at this head
  ok         tests/debug_collect.py
             `tests/debug_collect.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  unverified git merge-tree --write-tree origin/main 224f5007
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/closure.py select --diff 2999486b
             `tests/closure.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/manual_plan.py
             `tests/manual_plan.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --base origin/main
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=e83a2c919f ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head

FIGURES: 15 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.77d24bf8.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.77d24bf8.json
deleted file mode 100644
index 67dad5178f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.77d24bf8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND 77d24bf8",
-  "killed_by": "tests/features.py",
-  "old": "        return None if i < 0 else i",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`return None if i <= 0 else i`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9473dbd6.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9473dbd6.json
deleted file mode 100644
index 2932a712c7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9473dbd6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND 9473dbd6",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or i + 1 < len(starts):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`if i <= 0 or i + 1 < len(starts):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9689ca65.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9689ca65.json
deleted file mode 100644
index 137d68024f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9689ca65.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND 9689ca65",
-  "killed_by": "tests/features.py",
-  "old": "    span = starts[i] - starts[i - 1] if i > 0 else lone_span",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`span = starts[i] - starts[i - 1] if i >= 0 else lone_span`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.c5024eaf.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.c5024eaf.json
deleted file mode 100644
index 7230dcce7f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.c5024eaf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND c5024eaf",
-  "killed_by": "tests/features.py",
-  "old": "    return i if now < starts[i] + span else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`return i if now <= starts[i] + span else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.GUARD_OFF.9473dbd6.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.GUARD_OFF.9473dbd6.json
deleted file mode 100644
index abcf870035..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.GUARD_OFF.9473dbd6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index GUARD_OFF 9473dbd6",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or i + 1 < len(starts):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.RETURN_DEL.c5024eaf.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.RETURN_DEL.c5024eaf.json
deleted file mode 100644
index 0c7af96ea2..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.RETURN_DEL.c5024eaf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index RETURN_DEL c5024eaf",
-  "killed_by": "tests/features.py",
-  "old": "    return i if now < starts[i] + span else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/@module.CONST.f812625b.json b/tests/mutation_ledger/killed_by/drift.py/@module.CONST.f812625b.json
new file mode 100644
index 0000000000..2f37de3f19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/@module.CONST.f812625b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:<module> CONST f812625b",
+  "killed_by": "tests/features.py",
+  "old": "EVIDENCE_KEEP = 6",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`EVIDENCE_KEEP = 12`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/drift.py/_as_utc.GUARD_OFF.17aa8591.json b/tests/mutation_ledger/killed_by/drift.py/_as_utc.GUARD_OFF.17aa8591.json
deleted file mode 100644
index 425e16e204..0000000000
--- a/tests/mutation_ledger/killed_by/drift.py/_as_utc.GUARD_OFF.17aa8591.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/drift.py:_as_utc GUARD_OFF 17aa8591",
-  "killed_by": "tests/features.py",
-  "old": "    if value.tzinfo is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/_as_utc.RETURN_DEL.cb3b8685.json b/tests/mutation_ledger/killed_by/drift.py/_as_utc.RETURN_DEL.cb3b8685.json
deleted file mode 100644
index 13cd374274..0000000000
--- a/tests/mutation_ledger/killed_by/drift.py/_as_utc.RETURN_DEL.cb3b8685.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/drift.py:_as_utc RETURN_DEL cb3b8685",
-  "killed_by": "tests/finite_boundary.py",
-  "old": "    return value.astimezone(timezone.utc)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0: RETURN_DEL (`pass`) took tests/finite_boundary.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.4021bb75.json b/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.4021bb75.json
deleted file mode 100644
index 55c481c09f..0000000000
--- a/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.4021bb75.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_elapsed_seconds RETURN_DEL 4021bb75",
-  "killed_by": "tests/finite_boundary.py",
-  "old": "    return (_as_utc(newer) - _as_utc(older)).total_seconds()",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0: RETURN_DEL (`pass`) took tests/finite_boundary.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.f1feda0c.json b/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.f1feda0c.json
new file mode 100644
index 0000000000..a3f0b970e0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.f1feda0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_elapsed_seconds RETURN_DEL f1feda0c",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return (utc_instant(newer) - utc_instant(older)).total_seconds()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_instant.GUARD_OFF.17aa8591.json b/tests/mutation_ledger/killed_by/drift.py/utc_instant.GUARD_OFF.17aa8591.json
new file mode 100644
index 0000000000..cdd6fe9467
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/utc_instant.GUARD_OFF.17aa8591.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_instant GUARD_OFF 17aa8591",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    if value.tzinfo is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_instant.RETURN_DEL.cb3b8685.json b/tests/mutation_ledger/killed_by/drift.py/utc_instant.RETURN_DEL.cb3b8685.json
new file mode 100644
index 0000000000..720f0bb81b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/utc_instant.RETURN_DEL.cb3b8685.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_instant RETURN_DEL cb3b8685",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return value.astimezone(timezone.utc)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.BOOLOP.f921ad22.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.BOOLOP.f921ad22.json
new file mode 100644
index 0000000000..d7602c5f79
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.BOOLOP.f921ad22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room BOOLOP f921ad22",
+  "killed_by": "tests/features.py",
+  "old": "    return [float(trajectory[i + 1])] if i is not None and i < len(trajectory) - 1 else []",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return [float(trajectory[i + 1])] if i is not None or i < len(trajectory) - 1 else []`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.2cb216c6.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.2cb216c6.json
deleted file mode 100644
index 2d8d1eef26..0000000000
--- a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.2cb216c6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room CMP_BOUND 2cb216c6",
-  "killed_by": "tests/features.py",
-  "old": "    return [float(trajectory[i + 1])] if 0 <= i < len(trajectory) - 1 else []",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6be88834e8c4658b3e4832cd24c00aa97b3da2d3: CMP_BOUND (`return [float(trajectory[i + 1])] if 0 < i < len(trajectory) - 1 else []`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.f921ad22.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.f921ad22.json
new file mode 100644
index 0000000000..faafc212f4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.f921ad22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room CMP_BOUND f921ad22",
+  "killed_by": "tests/features.py",
+  "old": "    return [float(trajectory[i + 1])] if i is not None and i < len(trajectory) - 1 else []",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return [float(trajectory[i + 1])] if i is not None and i <= len(trajectory) - 1 else []`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.2cb216c6.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.2cb216c6.json
deleted file mode 100644
index 394bc12ed3..0000000000
--- a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.2cb216c6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room RETURN_DEL 2cb216c6",
-  "killed_by": "tests/features.py",
-  "old": "    return [float(trajectory[i + 1])] if 0 <= i < len(trajectory) - 1 else []",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.f921ad22.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.f921ad22.json
new file mode 100644
index 0000000000..f001395837
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.f921ad22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room RETURN_DEL f921ad22",
+  "killed_by": "tests/features.py",
+  "old": "    return [float(trajectory[i + 1])] if i is not None and i < len(trajectory) - 1 else []",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/entity.py/payload_number.BOOLOP.14c9991a.json b/tests/mutation_ledger/killed_by/entity.py/payload_number.BOOLOP.14c9991a.json
new file mode 100644
index 0000000000..2d62562605
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entity.py/payload_number.BOOLOP.14c9991a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entity.py:payload_number BOOLOP 14c9991a",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(value, float) and not math.isfinite(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(value, float) or not math.isfinite(value):`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/entity.py/payload_number.GUARD_OFF.14c9991a.json b/tests/mutation_ledger/killed_by/entity.py/payload_number.GUARD_OFF.14c9991a.json
new file mode 100644
index 0000000000..11891c3ec7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entity.py/payload_number.GUARD_OFF.14c9991a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entity.py:payload_number GUARD_OFF 14c9991a",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(value, float) and not math.isfinite(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.GUARD_OFF.81f7f114.json b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.GUARD_OFF.81f7f114.json
deleted file mode 100644
index c0863a67d3..0000000000
--- a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.GUARD_OFF.81f7f114.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/manual_plan.py:_instant GUARD_OFF 81f7f114",
-  "killed_by": "tests/features.py",
-  "old": "    if when.tzinfo is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6793659caed93f5a47bc7cc940f119b9e2abcbeb: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.0bd90ec9.json b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.0bd90ec9.json
deleted file mode 100644
index dd1253affa..0000000000
--- a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.0bd90ec9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/manual_plan.py:_instant RETURN_DEL 0bd90ec9",
-  "killed_by": "tests/manual_plan.py",
-  "old": "    return when.replace(tzinfo=timezone.utc).timestamp()",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6793659caed93f5a47bc7cc940f119b9e2abcbeb: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.c80445fe.json b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.c80445fe.json
new file mode 100644
index 0000000000..db1575130b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.c80445fe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/manual_plan.py:_instant RETURN_DEL c80445fe",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    return utc_instant(when).timestamp()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.374ff5e5.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.374ff5e5.json
deleted file mode 100644
index 38060666ec..0000000000
--- a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.374ff5e5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block GUARD_OFF 374ff5e5",
-  "killed_by": "tests/open_meteo.py",
-  "old": "        if parsed.tzinfo is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.429ea648.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.429ea648.json
new file mode 100644
index 0000000000..08f3578832
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.429ea648.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND 429ea648",
+  "killed_by": "tests/features.py",
+  "old": "        span = starts[i] - starts[i - 1] if i > 0 else lone_span",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`span = starts[i] - starts[i - 1] if i >= 0 else lone_span`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.bc6e5385.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.bc6e5385.json
new file mode 100644
index 0000000000..7301b48862
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.bc6e5385.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND bc6e5385",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if i < 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i <= 0:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.c5024eaf.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.c5024eaf.json
new file mode 100644
index 0000000000..06925197f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.c5024eaf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND c5024eaf",
+  "killed_by": "tests/features.py",
+  "old": "    return i if now < starts[i] + span else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return i if now <= starts[i] + span else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.d088310e.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.d088310e.json
new file mode 100644
index 0000000000..4a5f4c2c96
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.d088310e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND d088310e",
+  "killed_by": "tests/features.py",
+  "old": "    if i + 1 < len(starts):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i + 1 <= len(starts):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bbda03c6.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bbda03c6.json
new file mode 100644
index 0000000000..9209644158
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bbda03c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index GUARD_OFF bbda03c6",
+  "killed_by": "tests/features.py",
+  "old": "    if last_span is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bc6e5385.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bc6e5385.json
new file mode 100644
index 0000000000..0dfa2b8036
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bc6e5385.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index GUARD_OFF bc6e5385",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if i < 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.d088310e.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.d088310e.json
new file mode 100644
index 0000000000..412c78d04b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.d088310e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index GUARD_OFF d088310e",
+  "killed_by": "tests/features.py",
+  "old": "    if i + 1 < len(starts):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.RETURN_DEL.c5024eaf.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.RETURN_DEL.c5024eaf.json
new file mode 100644
index 0000000000..5e35ea2d20
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.RETURN_DEL.c5024eaf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index RETURN_DEL c5024eaf",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return i if now < starts[i] + span else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/plan_step_index.RETURN_DEL.ce01525a.json b/tests/mutation_ledger/killed_by/plan_step.py/plan_step_index.RETURN_DEL.ce01525a.json
new file mode 100644
index 0000000000..50e48787da
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/plan_step_index.RETURN_DEL.ce01525a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:plan_step_index RETURN_DEL ce01525a",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return covering_index(stamps, now, PLAN_STEP, PLAN_STEP)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.BOOLOP.747e63dd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.BOOLOP.747e63dd.json
new file mode 100644
index 0000000000..b93b33e4ce
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.BOOLOP.747e63dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room BOOLOP 747e63dd",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return points[i] if i is not None and i < len(points) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return points[i] if i is not None or i < len(points) else None`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.CMP_BOUND.747e63dd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.CMP_BOUND.747e63dd.json
new file mode 100644
index 0000000000..dfb5a00585
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.CMP_BOUND.747e63dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room CMP_BOUND 747e63dd",
+  "killed_by": "tests/features.py",
+  "old": "    return points[i] if i is not None and i < len(points) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return points[i] if i is not None and i <= len(points) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.747e63dd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.747e63dd.json
new file mode 100644
index 0000000000..b78cecf88f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.747e63dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room RETURN_DEL 747e63dd",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return points[i] if i is not None and i < len(points) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.e5ceb396.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.e5ceb396.json
deleted file mode 100644
index b48d7da8a1..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.e5ceb396.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room RETURN_DEL e5ceb396",
-  "killed_by": "tests/entities.py",
-  "old": "    return points[i] if 0 <= i < len(points) else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 67a0cb9816565113447bb54415989090706435b4: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
deleted file mode 100644
index 8b4be5e958..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index BOOLOP fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if i < 0 or (i == len(stamps) - 1 or now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
deleted file mode 100644
index 885b282bb9..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index CMP_BOUND fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i <= 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=72. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
deleted file mode 100644
index 554f0d548f..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index GUARD_OFF fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
deleted file mode 100644
index 8ad75207e0..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index RETURN_DEL 67f638e2",
-  "killed_by": "tests/features.py",
-  "old": "    return i",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.4941c1dc.json b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.4941c1dc.json
deleted file mode 100644
index f67250f5d7..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.4941c1dc.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:numeric GUARD_OFF 4941c1dc",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    if not isinstance(state, (str, int, float)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.dfa5414f.json b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.dfa5414f.json
new file mode 100644
index 0000000000..7c0aec8e34
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.dfa5414f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:numeric GUARD_OFF dfa5414f",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(state, bool) or not isinstance(state, (str, int, float)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.RETURN_DEL.80a0007e.json
deleted file mode 100644
index a19cf7180d..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.RETURN_DEL.80a0007e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:numeric RETURN_DEL 80a0007e",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    return True",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/_in_zone.RETURN_DEL.a2f14772.json b/tests/mutation_ledger/killed_by/wood_fuel.py/_in_zone.RETURN_DEL.a2f14772.json
new file mode 100644
index 0000000000..f90ed1112c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/_in_zone.RETURN_DEL.a2f14772.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:_in_zone RETURN_DEL a2f14772",
+  "killed_by": "tests/wood_advisor.py",
+  "old": "    return utc_instant(ts).astimezone(local_tz) if local_tz is not None else ts",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.08c8c646.json b/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.08c8c646.json
new file mode 100644
index 0000000000..60d25ec8b4
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.08c8c646.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:forecast_outdoor_now CMP_BOUND 08c8c646",
+  "old": "        index = 0 if now < starts[0] else covering_index(starts, now, timedelta(hours=1))",
+  "reason": "Equivalent (CMP_BOUND, `now < starts[0]` -> `now <= starts[0]`): the two differ only at `now == starts[0]` exactly, and there the other arm is taken by both -- `covering_index(starts, starts[0], span)` (plan_step.covering_index since round 11; the coordinator's `_covering_index` before it, the same body) returns 0 (measured: `covering_index([T0, T0+1h, ...], T0, 1h)` is 0, because `bisect_right` lands one past the first start and index 0 passes both of the helper's tests). So at that single instant the mutant's branch and the original's helper return the same index, and every other `now` takes the same branch in both. measured at fba6de8de: a 9-point grid over one forecast -- 2 h before the first entry, 1 min before it, exactly on it, 1 microsecond after it, +30 min, +1 h, the last entry's last minute, the end, and 50 h past -- drives the original and the mutant form to 0 disagreements; the mutant applied to a `git archive` of HEAD and driven under `tests/features.py`'s R10-FEEDS block gives rc=0 (`#2229: the forecast's outdoor 'now' and the open-loop plan seed end with their series` and `fc_before` pass unchanged). The line's other bounds are disposed elsewhere: the head-of-list rule itself is pinned by the `fc_before` arm, and the past-the-end `None` by `fc_past`.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.a439030d.json b/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.a439030d.json
deleted file mode 100644
index 609b576f02..0000000000
--- a/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.a439030d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:forecast_outdoor_now CMP_BOUND a439030d",
-  "old": "        index = 0 if now < starts[0] else _covering_index(starts, now, timedelta(hours=1))",
-  "reason": "Equivalent (CMP_BOUND, `now < starts[0]` -> `now <= starts[0]`): the two differ only at `now == starts[0]` exactly, and there the other arm is taken by both -- `_covering_index(starts, starts[0], span)` returns 0 (measured: `_covering_index([T0, T0+1h, ...], T0, 1h)` is 0, because `bisect_right` lands one past the first start and index 0 passes both of the helper's tests). So at that single instant the mutant's branch and the original's helper return the same index, and every other `now` takes the same branch in both. measured at fba6de8de: a 9-point grid over one forecast -- 2 h before the first entry, 1 min before it, exactly on it, 1 microsecond after it, +30 min, +1 h, the last entry's last minute, the end, and 50 h past -- drives the original and the mutant form to 0 disagreements; the mutant applied to a `git archive` of HEAD and driven under `tests/features.py`'s R10-FEEDS block gives rc=0 (`#2229: the forecast's outdoor 'now' and the open-loop plan seed end with their series` and `fc_before` pass unchanged). The line's other bounds are disposed elsewhere: the head-of-list rule itself is pinned by the `fc_before` arm, and the past-the-end `None` by `fc_past`.",
-  "verdict": "equivalent"
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index d21804be3e..233a4eff49 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -212,8 +212,13 @@ POWER_UNIT_TO_KW: Final = {
 
 #: Water density the flow conversion uses, kg per litre (#2016).
 WATER_KG_PER_L: Final = 0.998
-#: Water's specific heat, kJ per kg per K (#2016).
-WATER_CP_KJ_PER_KG_K: Final = 4.186
+#: The heat that warms one litre of water by one kelvin, kWh per litre per K:
+#: the package's one value of it (round-11 D7-s3-04). The tank-geometry helpers
+#: and ``thermal_model`` read it here rather than the reverse.
+WATER_SPECIFIC_HEAT: Final = 0.00116
+#: The same heat per kilogram in kJ, for a flow read in kg/s (#2016): derived,
+#: never a second value -- a literal 4.186 here read 0.04 % off the tank's.
+WATER_CP_KJ_PER_KG_K: Final = WATER_SPECIFIC_HEAT * 3600.0 / WATER_KG_PER_L
 #: Flow units the flow meter may report in, normalised to kg/s: a volume rate
 #: goes through :data:`WATER_KG_PER_L`. An unlisted unit is no reading, never
 #: a guess.
@@ -1462,9 +1467,8 @@ BUFFER_COOLING_RATE_MAX: Final = 30.0  # °C/h
 # six hours from a 26.1 kWh charge -- 168 % of the charge. The clamp floor is
 # worse than the default, because it stops the *learner* from ever finding the
 # truth: at 0.5 °C/h a 750 L tank still models 17 W/K against a real ~2 W/K.
-# Canonical home for this: the tank-geometry helpers below need it, and
-# `thermal_model` imports from here rather than the reverse.
-WATER_SPECIFIC_HEAT: Final = 0.00116  # kWh per litre per K
+# The heat capacity these tanks are modelled with is :data:`WATER_SPECIFIC_HEAT`,
+# defined once beside the water density above.
 
 
 # Bounds on how well or badly a tank can physically be insulated, in W/m2K.
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index 89aba9fd96..05e66b7f49 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -30,7 +30,7 @@ from types import SimpleNamespace
 from bisect import bisect_right
 from dataclasses import dataclass, field, replace
 from operator import attrgetter
-from datetime import datetime, timedelta, timezone
+from datetime import datetime, timedelta
 from pathlib import Path
 from collections.abc import Awaitable, Callable, Mapping, Sequence
 from typing import TYPE_CHECKING, Any, Final, NamedTuple, NoReturn, cast
@@ -285,7 +285,7 @@ from .price_model import (
 from . import sysid
 from .sysid import HousePlant, SysIdConfig, SystemIdentification, adoption_decision, step_detached
 from .plan_slots import plan_slots
-from .plan_step import PLAN_STEP_MINUTES, plan_step_start
+from .plan_step import PLAN_STEP_MINUTES, covering_index, plan_step_start
 from .tariff import CapacityTariff, PeakTracker
 from .grid_fee import (
     GridFeeError,
@@ -302,7 +302,7 @@ from .disinfection import DisinfectionSwitch
 from .curve_learning import CurveLearner, worst_zone_margin_k
 from .currency import feed_currency, figure_currency, resolve_currency
 from .drift import utc_shift
-from .drift import Cusum, stored_instant, utc_step_starts
+from .drift import Cusum, EvidenceLog, stored_instant, utc_instant, utc_step_starts
 from .ledger import (
     SETTLEMENT_KEYS,
     MonthlyLedger,
@@ -585,30 +585,12 @@ def _comparable_ts(raw: Any, reference: datetime) -> datetime | None:
     except (TypeError, ValueError):
         return None
     if ts.tzinfo is None and reference.tzinfo is not None:
-        return ts.replace(tzinfo=timezone.utc)
+        return utc_instant(ts)
     if ts.tzinfo is not None and reference.tzinfo is None:
         return dt_util.as_local(ts).replace(tzinfo=None)
     return ts
 
 
-def _covering_index(starts: list[Any], now: Any, lone_span: Any) -> int | None:
-    """The index of the entry whose ``[start, end)`` covers ``now``, or None.
-
-    ``starts`` is sorted. An entry ends where the next begins; the last ends
-    one predecessor's span after its own start (``lone_span`` when it is the
-    only entry), so a series its source stopped extending stops covering now
-    (R10 N-no-expiry, #2229: ``bisect_right(...) - 1`` alone held the last
-    entry current forever, and a stale price was published and booked). Before
-    the first entry nothing covers ``now`` either; a caller wanting the head
-    there says so itself. ``_known_prices_for``'s end rule, extracted.
-    """
-    i = bisect_right(starts, now) - 1
-    if i < 0 or i + 1 < len(starts):
-        return None if i < 0 else i
-    span = starts[i] - starts[i - 1] if i > 0 else lone_span
-    return i if now < starts[i] + span else None
-
-
 #: R10 N-log-flood (#2226): the transition latch lives in ``log_latch.py``, a
 #: leaf module, so the pump arbiter and the input reader can route a persisting
 #: condition through it without importing this module (which imports them all).
@@ -785,7 +767,7 @@ def forecast_outdoor_now(forecast: list[dict[str, Any]], now: datetime) -> float
     )
     if timed:
         starts = [ts for ts, _ in timed]
-        index = 0 if now < starts[0] else _covering_index(starts, now, timedelta(hours=1))
+        index = 0 if now < starts[0] else covering_index(starts, now, timedelta(hours=1))
         if index is None:
             return None
         entry = timed[index][1]
@@ -2547,7 +2529,7 @@ def _open_loop_plan_value(
         return float(trajectory[0]) if starts[0] - now_s <= 900.0 else None
     # The step covering ``now``; past the plan's last step the plan says
     # nothing (#2229: it seeded a 47 h old prediction as the tank's state).
-    index = _covering_index(starts, now_s, FORECAST_STEP.total_seconds())
+    index = covering_index(starts, now_s, FORECAST_STEP.total_seconds())
     return None if index is None else float(trajectory[index])
 
 
@@ -3632,7 +3614,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         self._immersion_active: bool = False
         self._immersion_over_count: int = 0
         self._immersion_clear_count: int = 0
-        self._immersion_evidence: list[str] = []
+        self._immersion_log = EvidenceLog()
         self._immersion_events: list[str] = []
         # #42: the weekly ring of learner snapshots.
         self._snapshot_ring = SnapshotRing()
@@ -7268,7 +7250,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         starts = [ts for ts, _ in entries]
         known: list[float] = []
         for step_start in step_starts:
-            idx = _covering_index(starts, step_start, timedelta(hours=1))
+            idx = covering_index(starts, step_start, timedelta(hours=1))
             if idx is None:
                 break
             known.append(entries[idx][1])
@@ -7993,7 +7975,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             "ventilation_active": self._vent_cusum.tripped,
             "ventilation_evidence": list(self._vent_cusum.evidence),
             "immersion_active": self._immersion_active,
-            "immersion_evidence": list(self._immersion_evidence),
+            "immersion_evidence": list(self._immersion_log.evidence),
             "cop_health": {
                 "watched_buckets": _watched_cop_buckets(self._cop_baseline),
                 "alarm": self._cop_health_cusum.tripped,
@@ -9087,12 +9069,11 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             self._immersion_clear_count = 0
             if not self._immersion_active and self._immersion_over_count >= 2:
                 self._immersion_active = True
-                self._immersion_evidence.append(
-                    f"{now.isoformat(timespec='seconds')}: measured "
-                    f"{measured:.1f} kW over {params.max_electrical_power:.1f} kW nameplate; "
-                    "immersion element running"
+                self._immersion_log.note(
+                    now,
+                    f"measured {measured:.1f} kW over {params.max_electrical_power:.1f} kW "
+                    "nameplate; immersion element running",
                 )
-                del self._immersion_evidence[:-6]
                 self._immersion_events.append(now.isoformat())
                 del self._immersion_events[:-20]
                 _LOGGER.info(
@@ -9106,11 +9087,7 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             self._immersion_over_count = 0
             if self._immersion_active and self._immersion_clear_count >= 2:
                 self._immersion_active = False
-                self._immersion_evidence.append(
-                    f"{now.isoformat(timespec='seconds')}: draw back under "
-                    "nameplate; released"
-                )
-                del self._immersion_evidence[:-6]
+                self._immersion_log.note(now, "draw back under nameplate; released")
         if self._pump_signals.electric_heat.dhw_booster_started:
             self._immersion_events.append(now.isoformat())
             del self._immersion_events[:-20]
diff --git a/custom_components/heatpump_optimizer/drift.py b/custom_components/heatpump_optimizer/drift.py
index 6604ad3bcd..a3b2bde73e 100644
--- a/custom_components/heatpump_optimizer/drift.py
+++ b/custom_components/heatpump_optimizer/drift.py
@@ -36,8 +36,14 @@ STAT_CAP_FACTOR = 1.5
 REFERENCE_PRIOR_COV = 1.0
 
 
-def _as_utc(value: datetime) -> datetime:
-    """Home Assistant's ``as_utc`` rule: naive is UTC, aware is converted."""
+def utc_instant(value: datetime) -> datetime:
+    """``value`` as an aware UTC instant: naive is read as UTC, aware is converted.
+
+    This is the package's one reading of a naive instant's zone (round-11
+    D7-s3-04). The stored and solver stamps are UTC-walked, so a naive one is
+    UTC, never the host's zone. ``open_meteo`` read it with ``astimezone`` and
+    landed nine hours off under a Tokyo host.
+    """
     if value.tzinfo is None:
         return value.replace(tzinfo=timezone.utc)
     return value.astimezone(timezone.utc)
@@ -51,7 +57,7 @@ def utc_elapsed_seconds(newer: datetime, older: datetime) -> float:
     both to UTC first measures the instants. A naive pair keeps its wall
     difference, which is what the identity-zone test clock means by it.
     """
-    return (_as_utc(newer) - _as_utc(older)).total_seconds()
+    return (utc_instant(newer) - utc_instant(older)).total_seconds()
 
 
 def utc_shift(when: datetime, delta: timedelta) -> datetime:
@@ -126,8 +132,37 @@ def stored_age_seconds(raw: Any, now: datetime) -> float | None:
     return age if age >= 0.0 else None
 
 
+#: Evidence lines a detector keeps, newest last.
+EVIDENCE_KEEP = 6
+
+
+class EvidenceNotes:
+    """The evidence log a detector publishes: timestamped lines, the newest few kept.
+
+    The one owner of the line's shape and of the cap (round-11 D7-s1-05, the
+    ``note`` arm). The drift detectors, the peak guard and the coordinator's
+    immersion inference publish the same list, so they write it through the
+    same method; each subclass declares its own ``evidence`` field.
+    """
+
+    evidence: list[str]
+
+    def note(self, when: datetime, text: str) -> None:
+        """Append ``text`` stamped ``when``, keeping the newest :data:`EVIDENCE_KEEP`."""
+        self.evidence.append(f"{when.isoformat(timespec='seconds')}: {text}")
+        del self.evidence[:-EVIDENCE_KEEP]
+
+
 @dataclass
-class Cusum:
+class EvidenceLog(EvidenceNotes):
+    """An evidence log with no detector state around it: the coordinator's
+    immersion inference keeps its trail here rather than trimming its own list."""
+
+    evidence: list[str] = field(default_factory=list)
+
+
+@dataclass
+class Cusum(EvidenceNotes):
     """A one-sided CUSUM with a drift allowance and hysteresis release.
 
     ``update`` folds one residual; the statistic accumulates
@@ -192,7 +227,7 @@ class Cusum:
         )
         if not self.tripped and self.stat >= self.threshold:
             self.tripped = True
-            self._note(
+            self.note(
                 when,
                 f"accumulated {self.stat:.2f} over threshold "
                 f"{self.threshold:.2f}; tripped",
@@ -200,7 +235,7 @@ class Cusum:
             return True
         if self.tripped and self.stat <= release_at:
             self.tripped = False
-            self._note(when, f"decayed to {self.stat:.2f}; released")
+            self.note(when, f"decayed to {self.stat:.2f}; released")
             return True
         return False
 
@@ -277,16 +312,12 @@ class Cusum:
             return False
         self.tripped = False
         self.stat = 0.0
-        self._note(
+        self.note(
             now,
             f"no residuals for {max_gap_hours:.0f} h; released as stale",
         )
         return True
 
-    def _note(self, when: datetime, text: str) -> None:
-        self.evidence.append(f"{when.isoformat(timespec='seconds')}: {text}")
-        del self.evidence[:-6]
-
     def as_dict(self) -> dict[str, Any]:
         data = {
             "stat": round(self.stat, 4),
@@ -322,7 +353,7 @@ class Cusum:
         self.tripped = data.get("tripped") is True
         raw = data.get("evidence")
         if isinstance(raw, list):
-            self.evidence = [str(e) for e in raw[-6:]]
+            self.evidence = [str(e) for e in raw[-EVIDENCE_KEEP:]]
         raw_fed = data.get("last_fed")
         if isinstance(raw_fed, str):
             self.last_fed = stored_instant(raw_fed)
diff --git a/custom_components/heatpump_optimizer/early_cutoff.py b/custom_components/heatpump_optimizer/early_cutoff.py
index 95baee29fa..39de3411b3 100644
--- a/custom_components/heatpump_optimizer/early_cutoff.py
+++ b/custom_components/heatpump_optimizer/early_cutoff.py
@@ -64,7 +64,6 @@ receives the coordinator itself, except :func:`state_for`, which keys on it.
 """
 from __future__ import annotations
 
-import bisect
 import logging
 from collections.abc import Callable
 from dataclasses import dataclass
@@ -80,6 +79,7 @@ from .boost import CHANNEL_DHW, CHANNEL_SPACE, BoostState
 from .const import MODE_AUTO, MODE_ECONOMY, ROOM_AIR_RANGE_C
 from .entry_config import EntryConfig
 from .inputs import parse_bool, temperature_c
+from .plan_step import plan_step_index
 from .pump_arbiter import ArbiterInputs, step_duty, supply_switch, switch_supply
 from .runs import MIN_PAUSE, MIN_RUN
 from .supply_hold import switch_age, tank_reason
@@ -256,9 +256,9 @@ def _planned_room(plan: Any, now: datetime) -> list[float]:
     solve measured, so a room already warm at the solve would raise its own
     threshold and the cut-off could never act on it.
     """
-    i = bisect.bisect_right(list(getattr(plan, "timestamps", None) or []), now) - 1
+    i = plan_step_index(plan, now)
     trajectory = list(getattr(plan, "room_temp_trajectory", None) or [])
-    return [float(trajectory[i + 1])] if 0 <= i < len(trajectory) - 1 else []
+    return [float(trajectory[i + 1])] if i is not None and i < len(trajectory) - 1 else []
 
 
 def _cycle_guard(inp: ArbiterInputs, held: CutoffState, now: datetime) -> str | None:
diff --git a/custom_components/heatpump_optimizer/entity.py b/custom_components/heatpump_optimizer/entity.py
index bcc36d6ecb..2062082c4f 100644
--- a/custom_components/heatpump_optimizer/entity.py
+++ b/custom_components/heatpump_optimizer/entity.py
@@ -135,12 +135,19 @@ def payload_number(
     had drifted from this four ways (D7-s2-60), so every entity that publishes
     a payload number reads it here. A numpy scalar is read as the Python
     value it holds, the order ``_finite`` takes for the same reason: a
-    ``numpy.bool_`` is then a bool, and a ``numpy.int64`` an ``int``.
+    ``numpy.bool_`` is then a bool, and a ``numpy.int64`` an ``int``. NaN and
+    infinity are not numbers a state publishes (``_finite`` makes them unknown
+    at the boundary anyway), so they are ``None`` here, where a guard reading
+    the value decides on it (round-11 D7-s3-04). The domain differs from
+    ``const.finite_float`` only in text: a stored or configured number may be
+    spelled, a payload number may not.
     """
     if isinstance(value, np.generic):
         value = value.item()
     if isinstance(value, bool) or not isinstance(value, types):
         return None
+    if isinstance(value, float) and not math.isfinite(value):
+        return None
     return value
 
 
diff --git a/custom_components/heatpump_optimizer/manual_plan.py b/custom_components/heatpump_optimizer/manual_plan.py
index bdb05b6b17..d9a7f93365 100644
--- a/custom_components/heatpump_optimizer/manual_plan.py
+++ b/custom_components/heatpump_optimizer/manual_plan.py
@@ -26,10 +26,10 @@ Three things carry subtle intent and are worth stating once here:
 from __future__ import annotations
 
 from dataclasses import dataclass, field
-from datetime import datetime, timedelta, timezone
+from datetime import datetime, timedelta
 from typing import Any
 
-from .drift import utc_shift
+from .drift import utc_instant, utc_shift
 from .const import MANUAL_PLAN_WINDOW_HOURS
 from .payload import ReleasedStep
 
@@ -64,9 +64,7 @@ class ManualPlanError(ValueError):
 
 def _instant(when: datetime) -> float:
     """``when`` as epoch seconds; a naive stamp keeps its wall order (read as UTC)."""
-    if when.tzinfo is not None:
-        return when.timestamp()
-    return when.replace(tzinfo=timezone.utc).timestamp()
+    return utc_instant(when).timestamp()
 
 
 def _coerce_awareness(value: datetime, reference: datetime) -> datetime:
@@ -79,9 +77,9 @@ def _coerce_awareness(value: datetime, reference: datetime) -> datetime:
     """
     if reference.tzinfo is None:
         if value.tzinfo is not None:
-            # Express the instant in local wall time, then drop the offset to
-            # match a naive reference.
-            return value.astimezone().replace(tzinfo=None)
+            # A naive reference is UTC (``_instant``), so the instant drops
+            # its offset in UTC; the host's zone would move it by its offset.
+            return utc_instant(value).replace(tzinfo=None)
         return value
     if value.tzinfo is None:
         return value.replace(tzinfo=reference.tzinfo)
diff --git a/custom_components/heatpump_optimizer/open_meteo.py b/custom_components/heatpump_optimizer/open_meteo.py
index 5032c1bdca..b145f9ed6e 100644
--- a/custom_components/heatpump_optimizer/open_meteo.py
+++ b/custom_components/heatpump_optimizer/open_meteo.py
@@ -37,7 +37,7 @@ import logging
 import math
 from collections import Counter
 from dataclasses import dataclass
-from datetime import datetime, timedelta, timezone
+from datetime import datetime, timedelta
 from typing import Any, Awaitable, TypedDict
 
 import aiohttp
@@ -52,6 +52,7 @@ from .const import (
     OPEN_METEO_SATELLITE_URL,
     OPEN_METEO_TIMEOUT_SECONDS,
 )
+from .drift import utc_instant
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -74,20 +75,6 @@ _VARIABLE_SNOWFALL = "snowfall"
 _MAX_PLAUSIBLE_GHI = 1400.0
 
 
-def _ensure_utc(value: datetime) -> datetime:
-    """Normalise a caller-supplied instant to UTC.
-
-    Home Assistant's ``dt_util.now()`` normally returns an aware local
-    datetime, but it yields a naive one when no timezone is configured. Naive
-    values are interpreted as system local time, which is what that function
-    means by them; the alternative, comparing a naive and an aware datetime,
-    raises TypeError inside the coordinator's update loop and takes the whole
-    optimization down over a timezone detail.
-    """
-    # astimezone() interprets a naive datetime as system local time, which is
-    # exactly what dt_util.now() means by one, and is a no-op relabelling for
-    # an aware one.
-    return value.astimezone(timezone.utc)
 
 
 class SolarDiagnostics(TypedDict):
@@ -140,8 +127,8 @@ class IrradianceSeries:
         """
         if not self.times:
             return None
-        start = _ensure_utc(start)
-        end = _ensure_utc(end)
+        start = utc_instant(start)
+        end = utc_instant(end)
         if end <= start:
             return None
 
@@ -168,7 +155,7 @@ class IrradianceSeries:
 
     def latest_before(self, when: datetime, max_age: timedelta) -> float | None:
         """Most recent sample at or before ``when``, if fresh enough."""
-        when = _ensure_utc(when)
+        when = utc_instant(when)
         best: tuple[datetime, float] | None = None
         for t, v in zip(self.times, self.values):
             if t <= when and (best is None or t > best[0]):
@@ -222,9 +209,7 @@ def _parse_block(
             parsed = datetime.fromisoformat(str(raw_t))
         except ValueError:
             continue
-        if parsed.tzinfo is None:
-            parsed = parsed.replace(tzinfo=timezone.utc)
-        times.append(parsed.astimezone(timezone.utc))
+        times.append(utc_instant(parsed))
         values.append(value)
 
     if len(times) < 2:
diff --git a/custom_components/heatpump_optimizer/plan_step.py b/custom_components/heatpump_optimizer/plan_step.py
index b037af3426..aa224e1f42 100644
--- a/custom_components/heatpump_optimizer/plan_step.py
+++ b/custom_components/heatpump_optimizer/plan_step.py
@@ -7,11 +7,17 @@ and its width apart until R10-PUMP-MODEL -- ``coordinator._solve_anchor`` on
 ``FORECAST_STEP_MINUTES``, ``pump_arbiter._step_start`` on a literal 15 -- and
 they agreed only while the two widths happened to be equal. A leaf module, so
 both import it and neither imports the other.
+
+It owns "the step covering an instant" too (round-11 ADR-001 part 2,
+D7-s3-03): four readers bisected the plan's stamps apart, and the two with no
+end rule held the last step's value at any instant past the plan.
 """
 from __future__ import annotations
 
-from datetime import datetime
-from typing import Final
+from bisect import bisect_right
+from collections.abc import Sequence
+from datetime import datetime, timedelta
+from typing import Any, Final
 
 #: Resolution the optimizer plans at, and therefore the resolution every
 #: forecast series is resampled to and the pump arbiter's ledger is keyed on.
@@ -20,6 +26,9 @@ PLAN_STEP_MINUTES: Final = 15
 #: One plan step in hours, the unit ``quiet_windows.step_actions`` takes.
 PLAN_STEP_HOURS: Final = PLAN_STEP_MINUTES / 60
 
+#: One plan step as a span, the width of a plan's last step.
+PLAN_STEP: Final = timedelta(minutes=PLAN_STEP_MINUTES)
+
 
 def plan_step_start(now: datetime) -> datetime:
     """``now`` floored onto the plan's step grid, on the solver's clock.
@@ -39,3 +48,44 @@ def plan_step_start(now: datetime) -> datetime:
     """
     step = int(PLAN_STEP_MINUTES)
     return now.replace(minute=(now.minute // step) * step, second=0, microsecond=0)
+
+
+def covering_index(
+    starts: Sequence[Any], now: Any, lone_span: Any, last_span: Any = None
+) -> int | None:
+    """The index of the entry whose ``[start, end)`` covers ``now``, or ``None``.
+
+    ``starts`` is sorted. An entry ends where the next begins. The last ends
+    one predecessor's span after its own start (``lone_span`` when it is the
+    only entry). So a series its source stopped extending stops covering now
+    (R10 N-no-expiry, #2229: ``bisect_right(...) - 1`` alone held the last
+    entry current forever, and a stale price was published and booked). Before
+    the first entry nothing covers ``now`` either; a caller wanting the head
+    there says so itself. A series on a fixed grid passes its width as
+    ``last_span``: its last entry is that wide whatever gap precedes it. Works
+    on any ordered stamps whose difference adds back to a stamp: datetimes
+    with timedelta spans, or epoch seconds.
+    """
+    i = bisect_right(starts, now) - 1
+    if i < 0:
+        return None
+    if i + 1 < len(starts):
+        return i
+    if last_span is not None:
+        span = last_span
+    else:
+        span = starts[i] - starts[i - 1] if i > 0 else lone_span
+    return i if now < starts[i] + span else None
+
+
+def plan_step_index(result: Any, now: datetime) -> int | None:
+    """The index of the plan step covering ``now``, or ``None`` outside the plan.
+
+    The one reading of a plan's ``timestamps`` that every series lookup takes
+    its index from (:func:`covering_index`). A plan is on the step grid, so
+    its last step is one :data:`PLAN_STEP` wide, whatever gap precedes it --
+    the arbiter's ``_step_index`` rule this replaced: past it the plan says
+    nothing.
+    """
+    stamps = list(getattr(result, "timestamps", None) or [])
+    return covering_index(stamps, now, PLAN_STEP, PLAN_STEP)
diff --git a/custom_components/heatpump_optimizer/power_guard.py b/custom_components/heatpump_optimizer/power_guard.py
index f83f0d822c..14fa0b0815 100644
--- a/custom_components/heatpump_optimizer/power_guard.py
+++ b/custom_components/heatpump_optimizer/power_guard.py
@@ -32,7 +32,7 @@ from datetime import datetime
 
 import numpy as np
 
-from .drift import utc_elapsed_seconds
+from .drift import EvidenceNotes, utc_elapsed_seconds
 
 #: Consecutive agreeing projections needed to engage or release.
 HYSTERESIS_SAMPLES = 2
@@ -67,7 +67,7 @@ def project_window_mean(
 
 
 @dataclass
-class GuardState:
+class GuardState(EvidenceNotes):
     """The guard's memory between meter events."""
 
     #: Whether electric DHW is currently being held back.
@@ -116,7 +116,7 @@ class GuardState:
             self._clear_count = 0
             if self.suppressing:
                 self.suppressing = False
-                self._note(now, "window closed; released")
+                self.note(now, "window closed; released")
                 window_changed = True
 
         if floor_hold:
@@ -124,7 +124,7 @@ class GuardState:
             self._clear_count = 0
             if self.suppressing:
                 self.suppressing = False
-                self._note(now, "floor takes precedence; released")
+                self.note(now, "floor takes precedence; released")
                 return True
             return window_changed
 
@@ -137,7 +137,7 @@ class GuardState:
             self._clear_count = 0
             if not self.suppressing and self._over_count >= HYSTERESIS_SAMPLES:
                 self.suppressing = True
-                self._note(
+                self.note(
                     now,
                     f"projected {projection_kw:.2f} kW over "
                     f"{threshold_kw:.2f}−{margin_kw:.2f} kW; suppressing",
@@ -148,12 +148,8 @@ class GuardState:
             self._over_count = 0
             if self.suppressing and self._clear_count >= HYSTERESIS_SAMPLES:
                 self.suppressing = False
-                self._note(
+                self.note(
                     now, f"projection back to {projection_kw:.2f} kW; released"
                 )
                 return True
         return window_changed
-
-    def _note(self, now: datetime, text: str) -> None:
-        self.evidence.append(f"{now.isoformat(timespec='seconds')}: {text}")
-        del self.evidence[:-6]
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index d5cfa8a975..c6c030113c 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -147,7 +147,6 @@ what the plan wanted.
 from __future__ import annotations
 
 import asyncio
-import bisect
 import logging
 import math
 from collections import Counter, deque
@@ -199,7 +198,7 @@ from .inputs import (
 )
 from .log_latch import log_held
 from .payload import REASON_LEGIONELLA, CurrentAction
-from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_start
+from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_index, plan_step_start
 from .drift import utc_elapsed_seconds, utc_shift
 from .drift import stored_instant
 from .store import QuarantiningStore, load_mapping
@@ -527,7 +526,7 @@ def step_duty(result: Any, now: datetime) -> str | None:
     the loop, so the harm was the channel and the second piece of state that
     kept it clean, not a live race.
     """
-    i = _step_index(result, now)
+    i = plan_step_index(result, now)
     if i is None:
         return None
     space = list(result.power_schedule or [])
@@ -540,19 +539,6 @@ def step_duty(result: Any, now: datetime) -> str | None:
     )
 
 
-def _step_index(result: Any, now: datetime) -> int | None:
-    """The index of the plan step covering ``now``, or ``None`` outside the plan.
-
-    A step covers [stamp, stamp + one plan step): the last one ends where the
-    next would start, the same half-open rule bisect gives every other step.
-    """
-    stamps = list(getattr(result, "timestamps", None) or [])
-    i = bisect.bisect_right(stamps, now) - 1
-    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):
-        return None
-    return i
-
-
 def own(coord: Any, signals: Any) -> Any:
     """``signals`` with a heating mode marked as the arbiter's, not a block.
 
@@ -611,11 +597,10 @@ def _grid(inp: ArbiterInputs, slot: str) -> SetpointGrid | None:
 def _planned_room(
     result: Any, now: datetime, attr: str = "optimal_setpoints"
 ) -> float | None:
-    """The plan series ``attr`` for the step covering ``now``."""
-    stamps = list(getattr(result, "timestamps", None) or [])
-    i = bisect.bisect_right(stamps, now) - 1
+    """The plan series ``attr`` for the step covering ``now``, ``None`` outside the plan."""
+    i = plan_step_index(result, now)
     points = list(getattr(result, attr, None) or [])
-    return points[i] if 0 <= i < len(points) else None
+    return points[i] if i is not None and i < len(points) else None
 
 
 def _space_target(
@@ -1935,11 +1920,11 @@ def _share(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) -> s
     A boost, a disinfection hold or a non-plan mode keeps Heating + DHW.
     """
     held = boost.held_for(coord)
-    if (duty != "both" or inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.disinfecting
+    result = inp.plan
+    i = plan_step_index(result, now)
+    if (i is None or duty != "both" or inp.mode not in (MODE_AUTO, MODE_ECONOMY) or inp.disinfecting
             or held.active(boost.CHANNEL_SPACE, now) or held.active(boost.CHANNEL_DHW, now)):
         return duty
-    result = inp.plan
-    i = bisect.bisect_right(result.timestamps, now) - 1
     start = result.timestamps[i]
     return duty_switch.both_step_duty(
         duty_switch.record_for(coord), start, now, result.power_schedule[i], result.dhw_power_schedule[i],
@@ -2011,7 +1996,7 @@ def step_supply(inp: ArbiterInputs, boosts: Any, now: datetime) -> bool | None:
         return None
     if boosts.active(boost.CHANNEL_SPACE, now) or boosts.active(boost.CHANNEL_DHW, now):
         return True
-    i = _step_index(inp.plan, now)
+    i = plan_step_index(inp.plan, now)
     return None if i is None or i >= len(inp.plan.power_schedule or ()) else plan_step_runs(inp.plan, i)
 
 
diff --git a/custom_components/heatpump_optimizer/replay_doc.py b/custom_components/heatpump_optimizer/replay_doc.py
index 13d8c7e4f2..374f949139 100644
--- a/custom_components/heatpump_optimizer/replay_doc.py
+++ b/custom_components/heatpump_optimizer/replay_doc.py
@@ -30,6 +30,7 @@ from __future__ import annotations
 import hashlib
 import hmac
 import json
+import math
 import re
 from collections.abc import Callable, Iterable, Mapping
 from typing import Any, cast
@@ -178,13 +179,18 @@ def choose_price_entity(
 
 
 def numeric(state: object) -> bool:
-    if not isinstance(state, (str, int, float)):
+    """Whether a recorded state is a finite number or its spelling.
+
+    ``const.finite_float``'s domain (round-11 D7-s3-04: this copy admitted
+    ``True``, ``"nan"`` and ``"inf"``), written out because this file imports
+    no sibling; ``tests/debug_collect.py`` drives both with the same probes.
+    """
+    if isinstance(state, bool) or not isinstance(state, (str, int, float)):
         return False
     try:
-        float(state)
-    except ValueError:
+        return math.isfinite(float(state))
+    except (ValueError, OverflowError):
         return False
-    return True
 def json_decimal_places(value: object) -> int | None:
     """Decimal places in the JSON spelling -- ``tests/nightly_ha.py``'s rule."""
     if isinstance(value, bool):
diff --git a/custom_components/heatpump_optimizer/sensor.py b/custom_components/heatpump_optimizer/sensor.py
index 1967164252..ed05156011 100644
--- a/custom_components/heatpump_optimizer/sensor.py
+++ b/custom_components/heatpump_optimizer/sensor.py
@@ -40,6 +40,7 @@ from .const import (
     MANUAL_PLAN_WINDOW_HOURS,
     OPTIMIZATION_MODE_STATES,
     SOLAR_APERTURE_MIN_SAMPLES,
+    WATER_SPECIFIC_HEAT,
 )
 from .coordinator import (
     HeatPumpOptimizerConfigEntry,
@@ -3052,7 +3053,7 @@ def _gap_probe_terms(
     # An install with no hot water has no tank to coast (D8-s1-01): the
     # model's own answer, so the default volume is never priced for it.
     if dhw_enabled_from_config(config):
-        terms["dhw_extra_kwh"] = volume * band * (4.187 / 3600.0) * 30.0
+        terms["dhw_extra_kwh"] = volume * band * WATER_SPECIFIC_HEAT * 30.0
     terms["dhw_price"] = rate
     return terms
 
diff --git a/custom_components/heatpump_optimizer/wood_fuel.py b/custom_components/heatpump_optimizer/wood_fuel.py
index efa00e052e..cfeb5e5d26 100644
--- a/custom_components/heatpump_optimizer/wood_fuel.py
+++ b/custom_components/heatpump_optimizer/wood_fuel.py
@@ -6,7 +6,7 @@ from datetime import datetime, timedelta, tzinfo
 from itertools import zip_longest
 from typing import Any
 
-from .drift import utc_elapsed_seconds
+from .drift import utc_elapsed_seconds, utc_instant
 from .const import (
     CONF_DHW_WOOD_COIL_ENABLED,
     CONF_EXTERNAL_HEAT_ENABLED,
@@ -164,6 +164,12 @@ def cheaper_hour_count(
     return sum(cheaper_steps(wood_sek, prices, cops, runs))
 
 
+def _in_zone(ts: datetime, local_tz: tzinfo | None) -> datetime:
+    """A plan stamp on ``local_tz``'s wall clock; a naive one is UTC
+    (``drift.utc_instant``), never the host's zone (PR #3728 review)."""
+    return utc_instant(ts).astimezone(local_tz) if local_tz is not None else ts
+
+
 def cheaper_windows(
     timestamps: Sequence[datetime],
     cheaper: Sequence[bool],
@@ -179,7 +185,7 @@ def cheaper_windows(
         return []
 
     def day(ts: datetime) -> object:
-        return (ts.astimezone(local_tz) if local_tz is not None else ts).date()
+        return _in_zone(ts, local_tz).date()
 
     today = day(timestamps[0])
     # One step's length, read off the plan's own grid.
@@ -553,7 +559,7 @@ def _attach_windows(
         return
 
     def iso(ts: datetime) -> str:
-        return (ts.astimezone(local_tz) if local_tz is not None else ts).isoformat()
+        return _in_zone(ts, local_tz).isoformat()
 
     windows: list[WoodWindow] = [
         {"start": iso(start), "end": iso(end)} for start, end in runs
diff --git a/dev/audit/harnesses/r11_kernel_step_agree.py b/dev/audit/harnesses/r11_kernel_step_agree.py
new file mode 100644
index 0000000000..118f38ad52
--- /dev/null
+++ b/dev/audit/harnesses/r11_kernel_step_agree.py
@@ -0,0 +1,128 @@
+"""Round-11 R11-SEAM-kernel-step: the finder's agreement harness, run at a tree past the fix.
+
+Metric (one line): the `disagreements` m8_agree.py prints per family, with the
+three private names this group's fix deleted bound to the owners that replaced
+them, so the finder's harness reads the fixed tree unchanged.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_kernel_step_agree.py \
+        $EXPORT/dev/audit/rounds/round11/D7/s3/m8_agree.py --only step_covering_now
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_kernel_step_agree.py --seams
+
+``$EXPORT`` is a ``git archive`` of plan/r11 (819aa2e354b4e5baaf824b8568fd72bea8168a75);
+m8_agree.py is the D7-s3 finder's harness (sha1 aaef9a3b34b9c3d8a523eb24410ff97f7ce6b0d1),
+which stays out of the tree. The bindings, each the owner the deleted copy became:
+
+    coordinator._covering_index -> plan_step.covering_index
+    pump_arbiter._step_index    -> plan_step.plan_step_index
+    open_meteo._ensure_utc      -> drift.utc_instant
+    drift._as_utc               -> drift.utc_instant  (read by --perturb only)
+
+At the merge base every name exists and the adapter binds none; at the head
+each is bound. Nothing else is touched, so every count is the finder's.
+Null control: run at the merge base it binds none ("bound: none" prints) and
+reads exactly what the harness alone reads.
+"""
+from __future__ import annotations
+
+import os
+import re
+import runpy
+import sys
+
+
+
+def repo_root(start):
+    """The directory holding custom_components/heatpump_optimizer/manifest.json."""
+    from pathlib import Path
+    here = Path(start).resolve()
+    if here.is_file():
+        here = here.parent
+    marker = Path("custom_components") / "heatpump_optimizer" / "manifest.json"
+    for cand in (here, *here.parents):
+        if (cand / marker).is_file():
+            return cand
+    raise RuntimeError(f"no repository root above {start}")
+
+
+ROOT = str(repo_root(__file__))
+sys.path[:0] = [ROOT]
+
+# The package as m8_agree.py imports it (``custom_components.heatpump_optimizer``),
+# so a binding lands on the module object the harness reads.
+from custom_components.heatpump_optimizer import (  # noqa: E402
+    coordinator,
+    drift,
+    open_meteo,
+    plan_step,
+    pump_arbiter,
+)
+
+BINDINGS = (
+    (coordinator, "_covering_index", lambda: plan_step.covering_index),
+    (pump_arbiter, "_step_index", lambda: plan_step.plan_step_index),
+    (open_meteo, "_ensure_utc", lambda: drift.utc_instant),
+    (drift, "_as_utc", lambda: drift.utc_instant),
+)
+
+
+#: ``--seams``: the D7-s3-04 finder's D002 seam rule (m8_enum.py), every line of
+#: the package matching it, each classed by the rule it applies. Only the
+#: naive-to-UTC relabel is "the zone of a naive instant"; P2's
+#: ``naive_instant_zone`` registry entry holds that class to drift.utc_instant.
+D002 = re.compile(r"tzinfo is None|\.replace\(tzinfo=|\.astimezone\(|as_utc\(")
+CLASSES = (
+    ("text", lambda s: s.startswith(("#", '"')) or "``" in s),
+    ("naive-to-UTC relabel: the naive-zone fact",
+     lambda s: re.search(r"replace\(tzinfo=(timezone\.utc|UTC)\)", s)),
+    ("Home Assistant's dt_util.as_utc", lambda s: "dt_util.as_utc(" in s),
+    ("a naive stamp aligned to a reference's zone, for comparison",
+     lambda s: re.search(r"replace\(tzinfo=(naive_zone|(\w+\.)?tzinfo|tz)\b", s)),
+    ("a zone stripped after conversion, for a naive reference", lambda s: "replace(tzinfo=None)" in s),
+    ("a zone conversion read through drift.utc_instant first",
+     lambda s: "utc_instant(" in s and ".astimezone(" in s),
+    # Shape cannot see a guard: every site here is dispositioned by hand in
+    # the PR body (a tzinfo test before it, or an aware-only input).
+    ("an aware conversion", lambda s: ".astimezone(" in s),
+    ("a naive test guarding one of the above", lambda s: "tzinfo is None" in s),
+)
+
+
+def seams() -> None:
+    """Print every D002 site with its class; a site in no class prints UNCLASSED."""
+    pkg = os.path.join(ROOT, "custom_components", "heatpump_optimizer")
+    counts: dict[str, int] = {}
+    for name in sorted(os.listdir(pkg)):
+        if not name.endswith(".py"):
+            continue
+        with open(os.path.join(pkg, name), encoding="utf-8") as fh:
+            for no, line in enumerate(fh, 1):
+                if not D002.search(line):
+                    continue
+                text = line.strip()
+                cls = next((c for c, test in CLASSES if test(text)), "UNCLASSED")
+                counts[cls] = counts.get(cls, 0) + 1
+                print(f"SITE {name}:{no} [{cls}] {text[:100]}")
+    for cls, n in counts.items():
+        print(f"RESULT {cls}={n}")
+    print(f"RESULT total={sum(counts.values())}")
+
+
+def main() -> None:
+    if sys.argv[1:2] == ["--seams"]:
+        seams()
+        return
+    if len(sys.argv) < 2:
+        raise SystemExit("usage: r11_kernel_step_agree.py <m8_agree.py> [m8_agree args]")
+    bound = []
+    for module, name, owner in BINDINGS:
+        if not hasattr(module, name):
+            setattr(module, name, owner())
+            bound.append(f"{module.__name__.rsplit('.', 1)[-1]}.{name}")
+    print("bound: " + (", ".join(bound) if bound else "none"))
+    harness = sys.argv[1]
+    sys.argv = [harness, *sys.argv[2:]]
+    runpy.run_path(harness, run_name="__main__")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/dev/programme/delivery/3728.md b/dev/programme/delivery/3728.md
new file mode 100644
index 0000000000..32273bfc3b
--- /dev/null
+++ b/dev/programme/delivery/3728.md
@@ -0,0 +1 @@
+- [#3728](https://github.com/tvofi/heatpump_optimizer/pull/3728) — **open**, R11-SEAM-kernel-step: one plan step kernel (R11-SEAM-kernel-step)
diff --git a/tests/closures.json b/tests/closures.json
index 8658ec4177..29629afb53 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -3623,6 +3623,7 @@
   ],
   "tests/open_meteo.py": [
    "custom_components/heatpump_optimizer/const.py",
+   "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/open_meteo.py",
    "tests/open_meteo.py"
   ],
@@ -4694,6 +4695,7 @@
    "dev/audit/harnesses/r11_comments_ratchet_reconcile.py",
    "dev/audit/harnesses/r11_denominator_planted.py",
    "dev/audit/harnesses/r11_honest_starts_runs.py",
+   "dev/audit/harnesses/r11_kernel_step_agree.py",
    "dev/audit/harnesses/r11_main_cancel_mutants.py",
    "dev/audit/harnesses/r11_money_currency_precedence.py",
    "dev/audit/harnesses/r11_owner_criteria.py",
diff --git a/tests/debug_collect.py b/tests/debug_collect.py
index f829b9b41f..fed82dca7b 100644
--- a/tests/debug_collect.py
+++ b/tests/debug_collect.py
@@ -1178,6 +1178,19 @@ R.check(
     [replay_doc.numeric(v) for v in ("1.5", 3, 2.5, "warm", None, ["1"])]
     == [True, True, True, False, False, False],
 )
+# Round-11 D7-s3-04: numeric is const.finite_float's domain, written out because
+# replay_doc imports no sibling; the census drives both with the same probes,
+# among them the three this copy once admitted (a bool, "nan", "inf").
+_numeric_probes = ("1.5", " 7 ", 3, 2.5, -0.0, True, False, "warm", "", None, ["1"],
+                   float("nan"), float("inf"), "nan", "inf", "-inf", "1e400")
+_numeric_split = [(v, replay_doc.numeric(v), const_mod.finite_float(v) is not None) for v in _numeric_probes]
+R.check(
+    "replay_doc.numeric answers exactly as const.finite_float on every probe, "
+    "refusing a bool, NaN and infinity in any spelling",
+    all(a == b for _, a, b in _numeric_split)
+    and not any(replay_doc.numeric(v) for v in (True, "nan", "inf", float("nan"))),
+    f"{[(v, a, b) for v, a, b in _numeric_split if a != b]}",
+)
 R.check(
     "replay_doc.json_decimal_places counts the JSON spelling's decimals, a string's as "
     "written, and answers None for a bool, a word or a non-number",
diff --git a/tests/dst_checks.py b/tests/dst_checks.py
index 6b15152943..8a4491abf6 100644
--- a/tests/dst_checks.py
+++ b/tests/dst_checks.py
@@ -2374,7 +2374,7 @@ def _imports_of(name):
     return sibs, ext
 
 
-_loaded = ("const", "open_meteo")
+_loaded = ("const", "drift", "open_meteo")
 _loader_sibs = set().union(*(_imports_of(m)[0] for m in _loaded))
 _loader_ext = set().union(*(_imports_of(m)[1] for m in _loaded))
 R.check(
diff --git a/tests/entities.py b/tests/entities.py
index a6f3388cd1..1b9dbfc752 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -3893,6 +3893,21 @@ def _p2_proxies(sources):
     return out
 
 
+#: Water's heat capacity as a literal, in any unit the package has spelled it:
+#: kJ per kg per K, kJ per litre, kWh per litre per K (D7-s3-04).
+_P2_WATER_HEAT = re.compile(r"^(4\.1[89]\d*|1\.16\d*|0\.0011[56]\d*)$")
+
+
+def _p2_match_water_heat(n, parents):
+    """A float literal that reads as water's heat capacity, outside const.py."""
+    return (isinstance(n, ast.Constant) and isinstance(n.value, float)
+            and not isinstance(n.value, bool)
+            and bool(_P2_WATER_HEAT.match(repr(n.value))))
+
+
+_p2_match_water_heat.live = True
+
+
 def _p2_registry(sources):
     """owners: ``file.py::Qual.name`` where the shape may live. dispositions:
     sites the shape returns that are not the fact's decision, with why."""
@@ -4271,6 +4286,32 @@ def _p2_registry(sources):
                  ast.IfExp, r"if \w+ is None else \w+\.astimezone\(timezone\.utc\)$",
                  lambda n: isinstance(n.test, ast.Compare)),
              owners=["tariff.py::_window_starts"], dispositions={}),
+        # D7-s3-04 (R11-SEAM-kernel-step): the heat that warms a litre of
+        # water by one kelvin is const.WATER_SPECIFIC_HEAT, and the per-kg
+        # form is derived from it there (const.py is not scanned). Any
+        # water-heat literal elsewhere is a second value: the sensor-gap
+        # advisor's 4.187 / 3600 read 0.26 % off the tank model's.
+        dict(fact="water_heat_capacity", finding="D7-s3-04",
+             match=_p2_match_water_heat, owners=[], dispositions={}),
+        # D7-s3-04: a naive instant's zone is UTC, decided by drift.utc_instant;
+        # open_meteo's own reading (astimezone: the host's zone) and
+        # manual_plan's copy read it there now. The shape is the naive-to-UTC
+        # relabel; every other site it returns is dispositioned.
+        dict(fact="naive_instant_zone", finding="D7-s3-04",
+             match=_p2_match_node(
+                 (ast.Call,), r"\.replace\(tzinfo=(timezone\.utc|UTC|dt_timezone\.utc)\)$",
+                 lambda n: getattr(n.func, "attr", None) == "replace"
+                 and any(k.arg == "tzinfo" for k in n.keywords)),
+             owners=["drift.py::utc_instant"], dispositions={}),
+        # D7-s1-05 (the note arm): the evidence line's cap is EVIDENCE_KEEP,
+        # written by EvidenceNotes.note alone; the guard, the CUSUM and the
+        # coordinator's immersion trail each trimmed their own list to a
+        # literal 6 before.
+        dict(fact="evidence_cap", finding="D7-s1-05",
+             match=_p2_match_node(
+                 (ast.Delete,), r"evidence\[:-",
+                 lambda n: True),
+             owners=["drift.py::EvidenceNotes.note"], dispositions={}),
     ]
 
 
@@ -4314,6 +4355,16 @@ _P2_CENSUSES = {
     "finite_float_owner": (
         "tests/finite_boundary.py",
         "every finite-float coercion is const.finite_float or a dispositioned site"),
+    # D7-s3-04 (R11-SEAM-kernel-step): replay_doc.numeric is finite_float's
+    # domain, written out because the export loads that file with no sibling.
+    "replay_numeric_domain": (
+        "tests/debug_collect.py",
+        "replay_doc.numeric answers exactly as const.finite_float on every probe"),
+    # D7-s3-03: every reader of the plan step covering now takes plan_step's
+    # index; the census drives the four on one plan, past its end included.
+    "plan_step_covering": (
+        "tests/features.py",
+        "D7-s3-03: plan_step_index, covering_index and both _planned_room copies agree"),
     # D7-s2-51: the scrub wraps the property Home Assistant resolves, a
     # runtime-object mixin's included.
     "finite_scrub_resolves_mro": (
@@ -42400,17 +42451,15 @@ def _r10_covering_lookups(sources):
     return found
 
 
-#: Every covering lookup that is not ``coordinator._covering_index``'s, and why
-#: it may hold its last entry open (the R10 sweep's dispositions).
+#: Every covering lookup that is not ``plan_step.covering_index``'s, and why
+#: it may hold its last entry open (the R10 sweep's dispositions). The plan's
+#: readers (``pump_arbiter`` and ``early_cutoff``) take their index from
+#: ``plan_step.plan_step_index`` since round 11 (ADR-001 part 2, D7-s3-03), so
+#: none of them bisects on its own.
 _R10_COVERING_ALLOWED = {
-    ("coordinator.py", "_covering_index"): (1, "the helper: its end bound is `now < starts[i] + span`"),
+    ("plan_step.py", "covering_index"): (1, "the helper: its end bound is `now < starts[i] + span`"),
     ("coordinator.py", "_weather_series"): (1, "builds the future horizon; padding past the last "
                                                "entry is documented extrapolation, never published as current"),
-    ("early_cutoff.py", "_planned_room"): (1, "index-bounded against the plan's own trajectory"),
-    ("pump_arbiter.py", "_planned_room"): (1, "its caller's step_duty is None past the plan end"),
-    ("pump_arbiter.py", "_step_index"): (1, "returns None past the plan's last step; "
-                                             "step_duty and step_supply read it (#2492)"),
-    ("pump_arbiter.py", "_share"): (1, "bounded by the plan's last step"),
 }
 
 
@@ -42424,18 +42473,21 @@ _r10_cov_found = _r10_covering_lookups(_r10_sources)
 _r10_cov_planted = _r10_covering_lookups({
     "planted.py": "from bisect import bisect_right\n"
                   "def current(s, now):\n    return s[bisect_right(s, now) - 1]\n",
-    "pump_arbiter.py": _r10_sources["pump_arbiter.py"]
-    + "\ndef _share(s, now):\n    return bisect_right(s, now) - 1, bisect_right(s, now) - 1\n",
+    "coordinator.py": _r10_sources["coordinator.py"]
+    + "\ndef _weather_series(s, now):\n    return bisect_right(s, now) - 1, bisect_right(s, now) - 1\n",
 })
 R.check(
     "R10 N-no-expiry barrier: every 'entry covering now' lookup goes through "
-    "_covering_index or is on the reasoned list with its exact count",
+    "plan_step.covering_index or is on the reasoned list with its exact count",
     not _r10_covering_verdict(_r10_cov_found)
-    and sum(_r10_cov_found.values()) >= 6 and len(_r10_sources) >= 70
+    # The reach floor is the two lookups left once round 11 (ADR-001 part 2)
+    # moved the plan's four readers onto plan_step.plan_step_index: the owner's
+    # own and _weather_series's padding; six before.
+    and sum(_r10_cov_found.values()) >= 2 and len(_r10_sources) >= 70
     # null control and perturbation: a planted unbounded lookup, and a second
     # lookup inside an allow-listed function, are each refused
     and ("planted.py", "current") in _r10_covering_verdict(_r10_cov_planted)
-    and ("pump_arbiter.py", "_share") in _r10_covering_verdict(_r10_cov_planted),
+    and ("coordinator.py", "_weather_series") in _r10_covering_verdict(_r10_cov_planted),
     f"mismatch {_r10_covering_verdict(_r10_cov_found)}; read {sum(_r10_cov_found.values())} "
     f"lookups in {len(_r10_sources)} modules",
 )
diff --git a/tests/features.py b/tests/features.py
index 54c6e99697..fac3d5b95d 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -21334,7 +21334,7 @@ _ci._detect_immersion()
 R.check(
     "two agreeing samples latch, with evidence and an event on record",
     _ci._immersion_active
-    and _ci._immersion_evidence
+    and _ci._immersion_log.evidence
     and len(_ci._immersion_events) == 1,
 )
 _ci._measured_power = 3.0
@@ -79782,10 +79782,13 @@ R.check(
     and _fm_norm(5.0, None) is None,
 )
 # A planted flow and temperature difference: 0.25 kg/s of water cooling 5 K
-# at c_p 4.186 kJ/(kg K) hands over 0.25 * 4.186 * 5 = 5.2325 kW.
+# is 0.25 / 0.998 L/s. At the one water heat capacity, 0.00116 kWh per
+# litre per K (const.WATER_SPECIFIC_HEAT, round-11 D7-s3-04; 4.186 kJ/(kg K)
+# and 5.2325 kW before), it hands over 0.25 / 0.998 * 0.00116 * 3600 * 5 =
+# 5.230461 kW.
 R.check(
-    "a planted 0.25 kg/s over a 5 K drop is 5.2325 kW",
-    abs(_fm.thermal_output_kw(0.25, 45.0, 40.0) - 5.2325) < 1e-9,
+    "a planted 0.25 kg/s over a 5 K drop is 5.230461 kW",
+    abs(_fm.thermal_output_kw(0.25, 45.0, 40.0) - 5.230460921843687) < 1e-9,
     f"{_fm.thermal_output_kw(0.25, 45.0, 40.0)}",
 )
 R.check(
@@ -79822,7 +79825,7 @@ _fm_r, _fm_cfg = _fm_reader({}, "15.0")
 _fm_kw = _fm.read_heat_output_kw(_fm_r, _fm_cfg)
 R.check(
     "the estimate follows the sensor: 15 L/min over a 5 K drop",
-    _fm_kw is not None and abs(_fm_kw - 15.0 / 60.0 * 0.998 * 4.186 * 5.0) < 1e-6,
+    _fm_kw is not None and abs(_fm_kw - 5.22) < 1e-9,
     f"{_fm_kw}",
 )
 _fm_r2, _fm_cfg2 = _fm_reader({}, "30.0")
@@ -80161,11 +80164,12 @@ for _frs_file in ("strings.json", *SHIPPED_CATALOGUES):
 # meter, a stale reading, a negative one, an unreadable one, an unknown unit,
 # an unset key, and an interval the plan gave partly to hot water.
 #
-# 15 L/min at 0.998 kg/L over the planted 5 K drop is 5.222035 kW: the figure
+# 15 L/min (0.25 L/s) over the planted 5 K drop at 0.00116 kWh per litre per K
+# is 5.22 kW (5.222035 at the 4.186 kJ/(kg K) of before round 11): the figure
 # the R9-UX-9 block above derives from these same three states, quoted here as
 # the literal the issue's acceptance names, so this block pins the wiring and
 # not a second copy of the arithmetic.
-_FM_LEARN_KW = 5.222035
+_FM_LEARN_KW = 5.22
 _FM_FLOW_CFG = {
     _fb_const.CONF_FLOW_METER_ENTITY: "sensor.flow",
     _fb_const.CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY: "sensor.sup",
@@ -80321,7 +80325,7 @@ _LOWER_LEARNER = "_async_learn_lower_floor_loss"
 _fm_seen, _fm_coord = _fm_replay(_HOUSE_LEARNER)
 R.check(
     "a planted 15 L/min over a 5 K drop reaches the house heat-loss replay as "
-    "5.222035 kW",
+    "5.22 kW",
     _fm_coord._t2_escaped is None
     and _fm_coord._house_heat_loss_samples == 1
     and _fm_seen["kwargs"].get("measured_heat_kw") is not None
@@ -81433,18 +81437,21 @@ def _fd_logged(fn):
 
 
 # -- N-no-expiry (#2229): the covering rule has an end --------------------
+# Its owner is plan_step.covering_index (round-11 ADR-001 part 2); the
+# coordinator reads it there.
+from heatpump_optimizer.plan_step import covering_index as _fd_covering_index  # noqa: E402
 _fd_starts = [_FD_T0 + timedelta(hours=k) for k in range(4)]
 _fd_cov = {
-    "before": _fd_cm._covering_index(_fd_starts, _FD_T0 - timedelta(minutes=1), timedelta(hours=1)),
-    "first": _fd_cm._covering_index(_fd_starts, _FD_T0, timedelta(hours=1)),
-    "inner": _fd_cm._covering_index(_fd_starts, _FD_T0 + timedelta(minutes=90), timedelta(hours=1)),
-    "last": _fd_cm._covering_index(_fd_starts, _FD_T0 + timedelta(minutes=239), timedelta(hours=1)),
-    "end": _fd_cm._covering_index(_fd_starts, _FD_T0 + timedelta(hours=4), timedelta(hours=1)),
-    "past": _fd_cm._covering_index(_fd_starts, _FD_T0 + timedelta(hours=50), timedelta(hours=1)),
-    "lone_in": _fd_cm._covering_index([0.0], 899.0, 900.0),
-    "lone_out": _fd_cm._covering_index([0.0], 900.0, 900.0),
-    "quarter_last": _fd_cm._covering_index([0.0, 900.0], 1799.0, 3600.0),
-    "quarter_out": _fd_cm._covering_index([0.0, 900.0], 1800.0, 3600.0),
+    "before": _fd_covering_index(_fd_starts, _FD_T0 - timedelta(minutes=1), timedelta(hours=1)),
+    "first": _fd_covering_index(_fd_starts, _FD_T0, timedelta(hours=1)),
+    "inner": _fd_covering_index(_fd_starts, _FD_T0 + timedelta(minutes=90), timedelta(hours=1)),
+    "last": _fd_covering_index(_fd_starts, _FD_T0 + timedelta(minutes=239), timedelta(hours=1)),
+    "end": _fd_covering_index(_fd_starts, _FD_T0 + timedelta(hours=4), timedelta(hours=1)),
+    "past": _fd_covering_index(_fd_starts, _FD_T0 + timedelta(hours=50), timedelta(hours=1)),
+    "lone_in": _fd_covering_index([0.0], 899.0, 900.0),
+    "lone_out": _fd_covering_index([0.0], 900.0, 900.0),
+    "quarter_last": _fd_covering_index([0.0, 900.0], 1799.0, 3600.0),
+    "quarter_out": _fd_covering_index([0.0, 900.0], 1800.0, 3600.0),
 }
 R.check(
     "#2229: an entry covers [start, next start); the last one its predecessor's span, "
@@ -81455,6 +81462,159 @@ R.check(
     repr(_fd_cov),
 )
 
+
+# -- round-11 ADR-001 (R11-SEAM-kernel-step): each small rule read from one owner --
+# D7-s3-03: every reader of "the plan step covering now" takes plan_step's index,
+# so past the plan's last step none of them answers. The census drives all four
+# with the same probes and asserts its own precondition: probes on both sides of
+# the plan's end, or it proves nothing about the end rule.
+from types import SimpleNamespace as _k11_ns  # noqa: E402
+
+from heatpump_optimizer import const as _k11_const  # noqa: E402
+from heatpump_optimizer import drift as _k11_drift  # noqa: E402
+from heatpump_optimizer import early_cutoff as _k11_ec  # noqa: E402
+from heatpump_optimizer import entity as _k11_entity  # noqa: E402
+from heatpump_optimizer import flow_meter as _k11_fm  # noqa: E402
+from heatpump_optimizer import manual_plan as _k11_mp  # noqa: E402
+from heatpump_optimizer import open_meteo as _k11_om  # noqa: E402
+from heatpump_optimizer import power_guard as _k11_pg  # noqa: E402
+from heatpump_optimizer import pump_arbiter as _k11_pa  # noqa: E402
+from heatpump_optimizer.plan_step import PLAN_STEP as _k11_step  # noqa: E402
+from heatpump_optimizer.plan_step import plan_step_index as _k11_idx  # noqa: E402
+
+_k11_stamps = [_FD_T0 + k * _k11_step for k in range(8)]
+_k11_plan = _k11_ns(timestamps=_k11_stamps, optimal_setpoints=[20.0 + k for k in range(8)],
+                    room_temp_trajectory=[19.0 + 0.1 * k for k in range(9)])
+_k11_probes = {
+    "before": _FD_T0 - _k11_step, "first": _FD_T0, "mid": _FD_T0 + 3.5 * _k11_step,
+    "last": _k11_stamps[-1] + _k11_step / 2, "end_edge": _k11_stamps[-1] + _k11_step,
+    "a_day_past": _k11_stamps[-1] + timedelta(days=1),
+}
+_k11_rows = {
+    name: (_k11_idx(_k11_plan, now) is not None,
+           _fd_covering_index(_k11_stamps, now, _k11_step) is not None,
+           _k11_pa._planned_room(_k11_plan, now) is not None,
+           bool(_k11_ec._planned_room(_k11_plan, now)))
+    for name, now in _k11_probes.items()
+}
+_k11_inside = {"first", "mid", "last"}
+R.check(
+    "D7-s3-03: plan_step_index, covering_index and both _planned_room copies agree on "
+    "every probe -- inside the plan a step covers now, at and past its end none does",
+    any(now >= _k11_stamps[-1] + _k11_step for now in _k11_probes.values())
+    and _k11_rows == {name: (name in _k11_inside,) * 4 for name in _k11_probes},
+    f"{_k11_rows}",
+)
+
+# A plan is on the step grid: its last step is one PLAN_STEP wide whatever gap
+# precedes it, as the arbiter's _step_index held before the move. A series
+# lookup with no grid width takes the predecessor's gap; null control, that one
+# reads the same plan as ended a gap after its last stamp.
+_k11_short = [_FD_T0, _FD_T0 + timedelta(minutes=2)]
+_k11_short_plan = _k11_ns(timestamps=_k11_short, optimal_setpoints=[20.0, 21.0])
+_k11_short_rows = (
+    _k11_idx(_k11_short_plan, _k11_short[-1] + _k11_step / 2),
+    _k11_idx(_k11_short_plan, _k11_short[-1] + _k11_step),
+    _k11_pa._planned_room(_k11_short_plan, _k11_short[-1] + _k11_step / 2),
+    _fd_covering_index(_k11_short, _k11_short[-1] + _k11_step / 2, _k11_step),
+)
+R.check(
+    "D7-s3-03: a plan's last step is one PLAN_STEP wide after a shorter gap (covered at half a step, "
+    "not at a step), and the arbiter's planned room reads it; null control, the series lookup with no "
+    "grid width ends it one gap after its stamp",
+    _k11_short_rows == (1, None, 21.0, None),
+    f"{_k11_short_rows}",
+)
+
+# D7-s1-05 (the note arm): the peak guard, the CUSUM and the coordinator's
+# immersion log write their evidence through drift's one owner, which keeps the
+# newest EVIDENCE_KEEP lines.
+_k11_guard = _k11_pg.GuardState()
+_k11_cusum = _k11_drift.Cusum(threshold=1.0, drift=0.0)
+for _k11_n in range(_k11_drift.EVIDENCE_KEEP + 2):
+    _k11_guard.note(_FD_T0 + timedelta(minutes=_k11_n), f"n{_k11_n}")
+    _k11_cusum.note(_FD_T0 + timedelta(minutes=_k11_n), f"n{_k11_n}")
+R.check(
+    "D7-s1-05 note: GuardState, Cusum and the immersion log write evidence through "
+    "EvidenceNotes.note, the newest EVIDENCE_KEEP lines kept, the same line for the same note",
+    _k11_pg.GuardState.note is _k11_drift.EvidenceNotes.note
+    and _k11_drift.Cusum.note is _k11_drift.EvidenceNotes.note
+    and _k11_drift.EvidenceLog.note is _k11_drift.EvidenceNotes.note
+    and _k11_guard.evidence == _k11_cusum.evidence
+    and len(_k11_guard.evidence) == _k11_drift.EVIDENCE_KEEP
+    and _k11_guard.evidence[0].endswith(": n2") and _k11_guard.evidence[-1].endswith(": n7"),
+    f"{_k11_guard.evidence} / {_k11_cusum.evidence}",
+)
+
+# D7-s3-04, water: the heat that warms a litre by one kelvin, read through each
+# path that uses it -- the tank model, the flow meter, the sensor-gap advisor.
+from heatpump_optimizer import sensor as _k11_sensor  # noqa: E402
+from heatpump_optimizer.thermal_model import ThermalParameters as _k11_TP  # noqa: E402
+
+_k11_tp = _k11_TP()
+_k11_terms = _k11_sensor._gap_probe_terms(
+    {_k11_const.CONF_DHW_ENABLED: True}, [1.0], [1.0], 1.0
+)
+_k11_band = float(_k11_const.DEFAULT_DHW_SETPOINT) - float(_k11_const.DEFAULT_DHW_MIN_TEMP)
+_k11_vol = EntryConfig.from_mapping({}).dhw_tank_volume
+_k11_water = {
+    "const": _k11_const.WATER_SPECIFIC_HEAT,
+    "tank model": _k11_tp.dhw_tank_thermal_mass / float(_k11_tp.dhw_tank_volume),
+    "flow meter": _k11_fm.thermal_output_kw(_k11_const.WATER_KG_PER_L, 1.0, 0.0) / 3600.0,
+    "gap advisor": _k11_terms["dhw_extra_kwh"] / (_k11_vol * _k11_band * 30.0),
+}
+R.check(
+    "D7-s3-04 water: the tank model, the flow meter and the gap advisor read one "
+    "heat capacity, const.WATER_SPECIFIC_HEAT (kWh per litre per K)",
+    max(_k11_water.values()) - min(_k11_water.values()) < 1e-12 * _k11_const.WATER_SPECIFIC_HEAT,
+    f"{_k11_water}",
+)
+
+# D7-s3-04, naive instant: one zone for a naive stamp, UTC, whatever the host's
+# zone -- open_meteo read it as the host's and landed nine hours off under Tokyo.
+import os as _k11_os  # noqa: E402
+import time as _k11_time  # noqa: E402
+
+_k11_saved_tz = _k11_os.environ.get("TZ")
+_k11_os.environ["TZ"] = "Asia/Tokyo"
+_k11_time.tzset()
+try:
+    _k11_naive = datetime(2026, 1, 10, 12, 0)
+    _k11_aware = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
+    _k11_zone = {
+        "drift": _k11_drift.utc_instant(_k11_naive) == _k11_aware,
+        "open_meteo": _k11_om.utc_instant is _k11_drift.utc_instant,
+        "manual_plan": _k11_mp._instant(_k11_naive) == _k11_aware.timestamp(),
+        "manual_plan coerce": _k11_mp._coerce_awareness(_k11_aware, _k11_naive) == _k11_naive,
+        "aware kept": _k11_drift.utc_instant(_k11_aware.astimezone()) == _k11_aware,
+    }
+finally:
+    if _k11_saved_tz is None:
+        _k11_os.environ.pop("TZ", None)
+    else:
+        _k11_os.environ["TZ"] = _k11_saved_tz
+    _k11_time.tzset()
+R.check(
+    "D7-s3-04 naive instant: drift.utc_instant reads a naive stamp as UTC under a "
+    "Tokyo host; open_meteo and manual_plan (its instant and its naive-reference coercion) read it there",
+    all(_k11_zone.values()),
+    f"{_k11_zone}",
+)
+
+# D7-s3-04, finite: a payload number is a finite one; it differs from
+# const.finite_float only in refusing text, which its docstring names.
+_k11_fin = [1, 1.5, True, None, "1.5", float("nan"), float("inf"), float("-inf"),
+            np.float64("nan"), np.float64(2.0), np.int64(3)]
+_k11_pay = [_k11_entity.payload_number(v) is not None for v in _k11_fin]
+_k11_ff = [_k11_const.finite_float(v.item() if isinstance(v, np.generic) else v) is not None
+           and not isinstance(v, str) for v in _k11_fin]
+R.check(
+    "D7-s3-04 finite: payload_number refuses NaN and infinity, and agrees with "
+    "finite_float on every probe but text",
+    _k11_pay == _k11_ff and _k11_pay.count(True) == 4,
+    f"payload {_k11_pay} / finite_float less text {_k11_ff}",
+)
+
 _fd_spot = _fd_coord()
 _fd_spot._prices = [{"total": round(1.0 + 0.1 * k, 2), "starts_at": (_FD_T0 + timedelta(hours=k)).isoformat(),
                      "level": "NORMAL"} for k in range(-2, 4)]
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.77d24bf8.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.77d24bf8.json
deleted file mode 100644
index 67dad5178f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.77d24bf8.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND 77d24bf8",
-  "killed_by": "tests/features.py",
-  "old": "        return None if i < 0 else i",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`return None if i <= 0 else i`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9473dbd6.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9473dbd6.json
deleted file mode 100644
index 2932a712c7..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9473dbd6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND 9473dbd6",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or i + 1 < len(starts):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`if i <= 0 or i + 1 < len(starts):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9689ca65.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9689ca65.json
deleted file mode 100644
index 137d68024f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.9689ca65.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND 9689ca65",
-  "killed_by": "tests/features.py",
-  "old": "    span = starts[i] - starts[i - 1] if i > 0 else lone_span",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`span = starts[i] - starts[i - 1] if i >= 0 else lone_span`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.c5024eaf.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.c5024eaf.json
deleted file mode 100644
index 7230dcce7f..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.CMP_BOUND.c5024eaf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index CMP_BOUND c5024eaf",
-  "killed_by": "tests/features.py",
-  "old": "    return i if now < starts[i] + span else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: CMP_BOUND (`return i if now <= starts[i] + span else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.GUARD_OFF.9473dbd6.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.GUARD_OFF.9473dbd6.json
deleted file mode 100644
index abcf870035..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.GUARD_OFF.9473dbd6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index GUARD_OFF 9473dbd6",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or i + 1 < len(starts):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.RETURN_DEL.c5024eaf.json b/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.RETURN_DEL.c5024eaf.json
deleted file mode 100644
index 0c7af96ea2..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/_covering_index.RETURN_DEL.c5024eaf.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:_covering_index RETURN_DEL c5024eaf",
-  "killed_by": "tests/features.py",
-  "old": "    return i if now < starts[i] + span else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 0570b86e9351dfeda88d630093cfe4d442a6d664: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/@module.CONST.f812625b.json b/tests/mutation_ledger/killed_by/drift.py/@module.CONST.f812625b.json
new file mode 100644
index 0000000000..2f37de3f19
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/@module.CONST.f812625b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:<module> CONST f812625b",
+  "killed_by": "tests/features.py",
+  "old": "EVIDENCE_KEEP = 6",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`EVIDENCE_KEEP = 12`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/drift.py/_as_utc.GUARD_OFF.17aa8591.json b/tests/mutation_ledger/killed_by/drift.py/_as_utc.GUARD_OFF.17aa8591.json
deleted file mode 100644
index 425e16e204..0000000000
--- a/tests/mutation_ledger/killed_by/drift.py/_as_utc.GUARD_OFF.17aa8591.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/drift.py:_as_utc GUARD_OFF 17aa8591",
-  "killed_by": "tests/features.py",
-  "old": "    if value.tzinfo is None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/_as_utc.RETURN_DEL.cb3b8685.json b/tests/mutation_ledger/killed_by/drift.py/_as_utc.RETURN_DEL.cb3b8685.json
deleted file mode 100644
index 13cd374274..0000000000
--- a/tests/mutation_ledger/killed_by/drift.py/_as_utc.RETURN_DEL.cb3b8685.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/drift.py:_as_utc RETURN_DEL cb3b8685",
-  "killed_by": "tests/finite_boundary.py",
-  "old": "    return value.astimezone(timezone.utc)",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0: RETURN_DEL (`pass`) took tests/finite_boundary.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.4021bb75.json b/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.4021bb75.json
deleted file mode 100644
index 55c481c09f..0000000000
--- a/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.4021bb75.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_elapsed_seconds RETURN_DEL 4021bb75",
-  "killed_by": "tests/finite_boundary.py",
-  "old": "    return (_as_utc(newer) - _as_utc(older)).total_seconds()",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 90335cbd6ee6a0e4423cd1effc2c8c962e2ac0a0: RETURN_DEL (`pass`) took tests/finite_boundary.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.f1feda0c.json b/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.f1feda0c.json
new file mode 100644
index 0000000000..a3f0b970e0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/utc_elapsed_seconds.RETURN_DEL.f1feda0c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_elapsed_seconds RETURN_DEL f1feda0c",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return (utc_instant(newer) - utc_instant(older)).total_seconds()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_instant.GUARD_OFF.17aa8591.json b/tests/mutation_ledger/killed_by/drift.py/utc_instant.GUARD_OFF.17aa8591.json
new file mode 100644
index 0000000000..cdd6fe9467
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/utc_instant.GUARD_OFF.17aa8591.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_instant GUARD_OFF 17aa8591",
+  "killed_by": "tests/open_meteo.py",
+  "old": "    if value.tzinfo is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/drift.py/utc_instant.RETURN_DEL.cb3b8685.json b/tests/mutation_ledger/killed_by/drift.py/utc_instant.RETURN_DEL.cb3b8685.json
new file mode 100644
index 0000000000..720f0bb81b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/utc_instant.RETURN_DEL.cb3b8685.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:utc_instant RETURN_DEL cb3b8685",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    return value.astimezone(timezone.utc)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.BOOLOP.f921ad22.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.BOOLOP.f921ad22.json
new file mode 100644
index 0000000000..d7602c5f79
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.BOOLOP.f921ad22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room BOOLOP f921ad22",
+  "killed_by": "tests/features.py",
+  "old": "    return [float(trajectory[i + 1])] if i is not None and i < len(trajectory) - 1 else []",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return [float(trajectory[i + 1])] if i is not None or i < len(trajectory) - 1 else []`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.2cb216c6.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.2cb216c6.json
deleted file mode 100644
index 2d8d1eef26..0000000000
--- a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.2cb216c6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room CMP_BOUND 2cb216c6",
-  "killed_by": "tests/features.py",
-  "old": "    return [float(trajectory[i + 1])] if 0 <= i < len(trajectory) - 1 else []",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6be88834e8c4658b3e4832cd24c00aa97b3da2d3: CMP_BOUND (`return [float(trajectory[i + 1])] if 0 < i < len(trajectory) - 1 else []`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.f921ad22.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.f921ad22.json
new file mode 100644
index 0000000000..faafc212f4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.CMP_BOUND.f921ad22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room CMP_BOUND f921ad22",
+  "killed_by": "tests/features.py",
+  "old": "    return [float(trajectory[i + 1])] if i is not None and i < len(trajectory) - 1 else []",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return [float(trajectory[i + 1])] if i is not None and i <= len(trajectory) - 1 else []`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.2cb216c6.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.2cb216c6.json
deleted file mode 100644
index 394bc12ed3..0000000000
--- a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.2cb216c6.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room RETURN_DEL 2cb216c6",
-  "killed_by": "tests/features.py",
-  "old": "    return [float(trajectory[i + 1])] if 0 <= i < len(trajectory) - 1 else []",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.f921ad22.json b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.f921ad22.json
new file mode 100644
index 0000000000..f001395837
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/early_cutoff.py/_planned_room.RETURN_DEL.f921ad22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/early_cutoff.py:_planned_room RETURN_DEL f921ad22",
+  "killed_by": "tests/features.py",
+  "old": "    return [float(trajectory[i + 1])] if i is not None and i < len(trajectory) - 1 else []",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/entity.py/payload_number.BOOLOP.14c9991a.json b/tests/mutation_ledger/killed_by/entity.py/payload_number.BOOLOP.14c9991a.json
new file mode 100644
index 0000000000..2d62562605
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entity.py/payload_number.BOOLOP.14c9991a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entity.py:payload_number BOOLOP 14c9991a",
+  "killed_by": "tests/entities.py",
+  "old": "    if isinstance(value, float) and not math.isfinite(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if isinstance(value, float) or not math.isfinite(value):`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/entity.py/payload_number.GUARD_OFF.14c9991a.json b/tests/mutation_ledger/killed_by/entity.py/payload_number.GUARD_OFF.14c9991a.json
new file mode 100644
index 0000000000..11891c3ec7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/entity.py/payload_number.GUARD_OFF.14c9991a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/entity.py:payload_number GUARD_OFF 14c9991a",
+  "killed_by": "tests/features.py",
+  "old": "    if isinstance(value, float) and not math.isfinite(value):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.GUARD_OFF.81f7f114.json b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.GUARD_OFF.81f7f114.json
deleted file mode 100644
index c0863a67d3..0000000000
--- a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.GUARD_OFF.81f7f114.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/manual_plan.py:_instant GUARD_OFF 81f7f114",
-  "killed_by": "tests/features.py",
-  "old": "    if when.tzinfo is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6793659caed93f5a47bc7cc940f119b9e2abcbeb: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.0bd90ec9.json b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.0bd90ec9.json
deleted file mode 100644
index dd1253affa..0000000000
--- a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.0bd90ec9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/manual_plan.py:_instant RETURN_DEL 0bd90ec9",
-  "killed_by": "tests/manual_plan.py",
-  "old": "    return when.replace(tzinfo=timezone.utc).timestamp()",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 6793659caed93f5a47bc7cc940f119b9e2abcbeb: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.c80445fe.json b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.c80445fe.json
new file mode 100644
index 0000000000..db1575130b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/manual_plan.py/_instant.RETURN_DEL.c80445fe.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/manual_plan.py:_instant RETURN_DEL c80445fe",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    return utc_instant(when).timestamp()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.374ff5e5.json b/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.374ff5e5.json
deleted file mode 100644
index 38060666ec..0000000000
--- a/tests/mutation_ledger/killed_by/open_meteo.py/_parse_block.GUARD_OFF.374ff5e5.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/open_meteo.py:_parse_block GUARD_OFF 374ff5e5",
-  "killed_by": "tests/open_meteo.py",
-  "old": "        if parsed.tzinfo is None:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/open_meteo.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.429ea648.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.429ea648.json
new file mode 100644
index 0000000000..08f3578832
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.429ea648.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND 429ea648",
+  "killed_by": "tests/features.py",
+  "old": "        span = starts[i] - starts[i - 1] if i > 0 else lone_span",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`span = starts[i] - starts[i - 1] if i >= 0 else lone_span`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.bc6e5385.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.bc6e5385.json
new file mode 100644
index 0000000000..7301b48862
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.bc6e5385.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND bc6e5385",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if i < 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i <= 0:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.c5024eaf.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.c5024eaf.json
new file mode 100644
index 0000000000..06925197f3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.c5024eaf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND c5024eaf",
+  "killed_by": "tests/features.py",
+  "old": "    return i if now < starts[i] + span else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return i if now <= starts[i] + span else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.d088310e.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.d088310e.json
new file mode 100644
index 0000000000..4a5f4c2c96
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.CMP_BOUND.d088310e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index CMP_BOUND d088310e",
+  "killed_by": "tests/features.py",
+  "old": "    if i + 1 < len(starts):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i + 1 <= len(starts):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bbda03c6.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bbda03c6.json
new file mode 100644
index 0000000000..9209644158
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bbda03c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index GUARD_OFF bbda03c6",
+  "killed_by": "tests/features.py",
+  "old": "    if last_span is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bc6e5385.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bc6e5385.json
new file mode 100644
index 0000000000..0dfa2b8036
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.bc6e5385.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index GUARD_OFF bc6e5385",
+  "killed_by": "tests/block_duty.py",
+  "old": "    if i < 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.d088310e.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.d088310e.json
new file mode 100644
index 0000000000..412c78d04b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.GUARD_OFF.d088310e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index GUARD_OFF d088310e",
+  "killed_by": "tests/features.py",
+  "old": "    if i + 1 < len(starts):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/covering_index.RETURN_DEL.c5024eaf.json b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.RETURN_DEL.c5024eaf.json
new file mode 100644
index 0000000000..5e35ea2d20
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/covering_index.RETURN_DEL.c5024eaf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:covering_index RETURN_DEL c5024eaf",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return i if now < starts[i] + span else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/plan_step.py/plan_step_index.RETURN_DEL.ce01525a.json b/tests/mutation_ledger/killed_by/plan_step.py/plan_step_index.RETURN_DEL.ce01525a.json
new file mode 100644
index 0000000000..50e48787da
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/plan_step.py/plan_step_index.RETURN_DEL.ce01525a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/plan_step.py:plan_step_index RETURN_DEL ce01525a",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return covering_index(stamps, now, PLAN_STEP, PLAN_STEP)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.BOOLOP.747e63dd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.BOOLOP.747e63dd.json
new file mode 100644
index 0000000000..b93b33e4ce
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.BOOLOP.747e63dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room BOOLOP 747e63dd",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return points[i] if i is not None and i < len(points) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return points[i] if i is not None or i < len(points) else None`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=23."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.CMP_BOUND.747e63dd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.CMP_BOUND.747e63dd.json
new file mode 100644
index 0000000000..dfb5a00585
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.CMP_BOUND.747e63dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room CMP_BOUND 747e63dd",
+  "killed_by": "tests/features.py",
+  "old": "    return points[i] if i is not None and i < len(points) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return points[i] if i is not None and i <= len(points) else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.747e63dd.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.747e63dd.json
new file mode 100644
index 0000000000..b78cecf88f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.747e63dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room RETURN_DEL 747e63dd",
+  "killed_by": "tests/block_duty.py",
+  "old": "    return points[i] if i is not None and i < len(points) else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/block_duty.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.e5ceb396.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.e5ceb396.json
deleted file mode 100644
index b48d7da8a1..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_planned_room.RETURN_DEL.e5ceb396.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_planned_room RETURN_DEL e5ceb396",
-  "killed_by": "tests/entities.py",
-  "old": "    return points[i] if 0 <= i < len(points) else None",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 67a0cb9816565113447bb54415989090706435b4: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
deleted file mode 100644
index 8b4be5e958..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.BOOLOP.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index BOOLOP fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if i < 0 or (i == len(stamps) - 1 or now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=26."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
deleted file mode 100644
index 885b282bb9..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.CMP_BOUND.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index CMP_BOUND fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if i <= 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=72. Each of the 2 sites under this anchor was killed."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
deleted file mode 100644
index 554f0d548f..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.GUARD_OFF.fe5ed606.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index GUARD_OFF fe5ed606",
-  "killed_by": "tests/features.py",
-  "old": "    if i < 0 or (i == len(stamps) - 1 and now - stamps[i] >= timedelta(minutes=PLAN_STEP_MINUTES)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
deleted file mode 100644
index 8ad75207e0..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_step_index.RETURN_DEL.67f638e2.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_step_index RETURN_DEL 67f638e2",
-  "killed_by": "tests/features.py",
-  "old": "    return i",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.4941c1dc.json b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.4941c1dc.json
deleted file mode 100644
index f67250f5d7..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.4941c1dc.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:numeric GUARD_OFF 4941c1dc",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    if not isinstance(state, (str, int, float)):",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 55dc8d9c2c59c2ab614cb7c5d4b0ae9807401b50: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.dfa5414f.json b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.dfa5414f.json
new file mode 100644
index 0000000000..7c0aec8e34
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.GUARD_OFF.dfa5414f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:numeric GUARD_OFF dfa5414f",
+  "killed_by": "tests/debug_collect.py",
+  "old": "    if isinstance(state, bool) or not isinstance(state, (str, int, float)):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/replay_doc.py/numeric.RETURN_DEL.80a0007e.json
deleted file mode 100644
index a19cf7180d..0000000000
--- a/tests/mutation_ledger/killed_by/replay_doc.py/numeric.RETURN_DEL.80a0007e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/replay_doc.py:numeric RETURN_DEL 80a0007e",
-  "killed_by": "tests/debug_collect.py",
-  "old": "    return True",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8: RETURN_DEL (`pass`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/wood_fuel.py/_in_zone.RETURN_DEL.a2f14772.json b/tests/mutation_ledger/killed_by/wood_fuel.py/_in_zone.RETURN_DEL.a2f14772.json
new file mode 100644
index 0000000000..f90ed1112c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/wood_fuel.py/_in_zone.RETURN_DEL.a2f14772.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/wood_fuel.py:_in_zone RETURN_DEL a2f14772",
+  "killed_by": "tests/wood_advisor.py",
+  "old": "    return utc_instant(ts).astimezone(local_tz) if local_tz is not None else ts",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/wood_advisor.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.08c8c646.json b/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.08c8c646.json
new file mode 100644
index 0000000000..60d25ec8b4
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.08c8c646.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:forecast_outdoor_now CMP_BOUND 08c8c646",
+  "old": "        index = 0 if now < starts[0] else covering_index(starts, now, timedelta(hours=1))",
+  "reason": "Equivalent (CMP_BOUND, `now < starts[0]` -> `now <= starts[0]`): the two differ only at `now == starts[0]` exactly, and there the other arm is taken by both -- `covering_index(starts, starts[0], span)` (plan_step.covering_index since round 11; the coordinator's `_covering_index` before it, the same body) returns 0 (measured: `covering_index([T0, T0+1h, ...], T0, 1h)` is 0, because `bisect_right` lands one past the first start and index 0 passes both of the helper's tests). So at that single instant the mutant's branch and the original's helper return the same index, and every other `now` takes the same branch in both. measured at fba6de8de: a 9-point grid over one forecast -- 2 h before the first entry, 1 min before it, exactly on it, 1 microsecond after it, +30 min, +1 h, the last entry's last minute, the end, and 50 h past -- drives the original and the mutant form to 0 disagreements; the mutant applied to a `git archive` of HEAD and driven under `tests/features.py`'s R10-FEEDS block gives rc=0 (`#2229: the forecast's outdoor 'now' and the open-loop plan seed end with their series` and `fc_before` pass unchanged). The line's other bounds are disposed elsewhere: the head-of-list rule itself is pinned by the `fc_before` arm, and the past-the-end `None` by `fc_past`.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.a439030d.json b/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.a439030d.json
deleted file mode 100644
index 609b576f02..0000000000
--- a/tests/mutation_ledger/survivor_triage/coordinator.py/forecast_outdoor_now.CMP_BOUND.a439030d.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:forecast_outdoor_now CMP_BOUND a439030d",
-  "old": "        index = 0 if now < starts[0] else _covering_index(starts, now, timedelta(hours=1))",
-  "reason": "Equivalent (CMP_BOUND, `now < starts[0]` -> `now <= starts[0]`): the two differ only at `now == starts[0]` exactly, and there the other arm is taken by both -- `_covering_index(starts, starts[0], span)` returns 0 (measured: `_covering_index([T0, T0+1h, ...], T0, 1h)` is 0, because `bisect_right` lands one past the first start and index 0 passes both of the helper's tests). So at that single instant the mutant's branch and the original's helper return the same index, and every other `now` takes the same branch in both. measured at fba6de8de: a 9-point grid over one forecast -- 2 h before the first entry, 1 min before it, exactly on it, 1 microsecond after it, +30 min, +1 h, the last entry's last minute, the end, and 50 h past -- drives the original and the mutant form to 0 disagreements; the mutant applied to a `git archive` of HEAD and driven under `tests/features.py`'s R10-FEEDS block gives rc=0 (`#2229: the forecast's outdoor 'now' and the open-loop plan seed end with their series` and `fc_before` pass unchanged). The line's other bounds are disposed elsewhere: the head-of-list rule itself is pinned by the `fc_before` arm, and the past-the-end `None` by `fc_past`.",
-  "verdict": "equivalent"
-}
diff --git a/tests/open_meteo.py b/tests/open_meteo.py
index 5ab1127308..0b92a1c87e 100644
--- a/tests/open_meteo.py
+++ b/tests/open_meteo.py
@@ -74,14 +74,17 @@ def _install_ha_stubs() -> None:
 
 
 def _load_module():
-    """Load open_meteo.py with its relative import of .const intact."""
+    """Load open_meteo.py with its relative imports of .const and .drift intact.
+
+    ``drift`` holds the package's one reading of a naive instant (round 11),
+    and imports nothing from the package and no Home Assistant module."""
     _install_ha_stubs()
 
     pkg = types.ModuleType("hpo")
     pkg.__path__ = [SRC]
     sys.modules["hpo"] = pkg
 
-    for name in ("const", "open_meteo"):
+    for name in ("const", "drift", "open_meteo"):
         spec = importlib.util.spec_from_file_location(
             f"hpo.{name}", os.path.join(SRC, f"{name}.py")
         )
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index f3676b586c..63130e5f77 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,17 +1,17 @@
 {
- "class_excess_loc": 17322,
+ "class_excess_loc": 17317,
  "const_modules_over_50": 3,
  "coordinator_attrs": 136,
  "coordinator_multiassigned_attrs": 104,
  "coordinator_private_reach": 0,
  "dead_methods": 0,
  "dead_top_level_symbols": 1,
- "duplication_copies": 7,
+ "duplication_copies": 5,
  "functions_cc_over_15": 26,
  "functions_cc_over_25": 7,
  "import_cycle_modules": 0,
  "max_cc": 44,
- "max_class_loc": 7873,
+ "max_class_loc": 7868,
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
diff --git a/tests/wood_advisor.py b/tests/wood_advisor.py
index 0e90ed3666..600841d59e 100644
--- a/tests/wood_advisor.py
+++ b/tests/wood_advisor.py
@@ -260,6 +260,42 @@ R.check(
     == [{"start": "2026-01-15T23:00:00+01:00", "end": "2026-01-16T00:00:00+01:00"}],
     repr(_local.get("cheaper_windows")),
 )
+# PR #3728 review (wood_fuel cheaper_windows/_attach_windows): a naive plan
+# stamp is UTC under any host zone (drift.utc_instant), never the host's. The
+# same 22:00-23:00 UTC cheap steps, naive, built under a Tokyo host, must give
+# the aware build's windows; read with the host zone they land nine hours off.
+import os as _os
+import time as _time
+
+_saved_host_tz = _os.environ.get("TZ")
+_os.environ["TZ"] = "Asia/Tokyo"
+_time.tzset()
+try:
+    _host_took = _time.localtime(1768435200).tm_gmtoff == 9 * 3600  # 2026-01-15
+    _naive_local = build_wood_fuel_view(
+        _WOOD_READY,
+        prices=[4.0 if i in (22, 23) else 1.0 for i in range(30)],
+        cops=[3.0] * 30,
+        runs=[True] * 30,
+        timestamps=[ts.replace(tzinfo=None) for ts in _STAMPS],
+        forecast_kw=[],
+        local_tz=_CET,
+    )
+finally:
+    if _saved_host_tz is None:
+        _os.environ.pop("TZ", None)
+    else:
+        _os.environ["TZ"] = _saved_host_tz
+    _time.tzset()
+R.check(
+    "a naive plan stamp is UTC under a non-UTC host zone: the windows and the "
+    "lighting window equal the aware build's",
+    _host_took
+    and _naive_local.get("cheaper_windows") == _local.get("cheaper_windows")
+    and _lighting(_naive_local) == _lighting(_local),
+    f"host zone took {_host_took}, {_naive_local.get('cheaper_windows')!r} "
+    f"{_lighting(_naive_local)!r}",
+)
 from heatpump_optimizer.wood_fuel import cheaper_windows as _cheaper_windows
 
 _one_step = _cheaper_windows(_STAMPS[:1], [True], _tz.utc)

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
