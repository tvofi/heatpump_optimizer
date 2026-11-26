# Review packet #3870
head: 5f8e2cdb5fe2d236f71c62f8d41b31836df88107
base: 8f22a3b2842987bf6da13dedb08c4b99b7447f1f

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=139741375921 success
arch-score / arch-score id=139780289303 success
arm id=139740422966 skipped
budget-raise-gate / budget-raise-gate id=139780290486 success
cancel-superseded id=139780288644 success
codeql id=139780290170 skipped
codeql / Analyze (actions) id=139740778936 success
codeql / Analyze (javascript-typescript) id=139740778840 success
codeql / Analyze (python) id=139740778863 success
gate id=139780288846 success
governance id=139780290265 skipped
governance / env-matrix id=139740778889 success
governance / instrument-self-tests id=139740778886 success
governance / policy-docs id=139740778839 success
governance / record id=139740780982 skipped
governance / wave-script id=139740778904 success
hassfest id=139780357060 skipped
hassfest / hassfest id=139740778807 success
kernel-points id=139780363489 skipped
pr-contract id=139780291188 skipped
pr-contract / pr-contract id=139778863785 success
prelude id=139780338448 success
refresh id=139780334727 success
sweep-self id=139780757928 skipped
tests id=139780290457 skipped
tests / arch-instrument id=139742199873 success
tests / briefs id=139740778902 success
tests / browser id=139742199649 success
tests / ci-ratchet id=139761985798 skipped
tests / claims-autofix id=139754487422 skipped
tests / closure-scope id=139740779172 success
tests / closures id=139742199606 success
tests / closures-autofix id=139761985138 skipped
tests / coverage id=139742199789 success
tests / coverage-ratchet id=139760742584 success
tests / fast (3.14) id=139742199775 success
tests / graders-head-copy id=139760742492 success
tests / lane-proofs id=139760742812 success
tests / mutation id=139740779005 success
tests / mutation-autofix id=139778865970 skipped
tests / mutation-pins id=139778865248 skipped
tests / nightly-ha (2025.2.0) id=139742199784 failure
tests / nightly-ha (stable) id=139742199796 failure
tests / nightly-status id=139740778867 failure
tests / replay id=139742202101 skipped
tests / typing id=139742199715 success
validate id=139780290641 skipped
validate / validate-hacs id=139740778781 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item f5297374: dismissed:named in the round-4 handoff report to the orchestrator, who owns routing it to the mutation-table owner.
NOTE body item b9c2dda5: R11-OWNER-FAULT-HOLD
NOTE body item b69938d1: dismissed:a read-back miss after a verified push, recorded here and re-checked by hand
CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show <rev>:tests/closures.json
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git merge-tree --write-tree
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/deployment_shape.py
             `tests/deployment_shape.py` is in the tree at this head
  ok         PYTHONPATH=tests/hastub python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 7a666abfe9
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/features.py
             `tests/features.py` is in the tree at this head
  unverified git show 170e96ec5c3d003f8fa7f4e09b5424dfd0d087d1:evidence/probe_failed_setup.py
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff 9f133225f7
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/comment_ratchet.py
             `tests/comment_ratchet.py` is in the tree at this head
  ok         dev/audit/harnesses/r11_owner_fault_text.py
             `dev/audit/harnesses/r11_owner_fault_text.py` is in the tree at this head
  unverified git grep -n "CONF_HEAT_PUMP_FAULT_ENTITY\|CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES\|heat_pump_fault_entity\|heat_pump_fault_text_entities" 41b57b2daf -- 'custom_components/heatpump_optimizer/*.py'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 8ef450936a1786abf4bb9610dc3336da4e77e8de
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/comment_ratchet.py
             `tests/comment_ratchet.py` is in the tree at this head
  ok         tests/derive_closures.sh --scripts-from <16 scripts whose closure held __init__.py or diagnostics.py and that set an entry up> --record-only
             `tests/derive_closures.sh` is in the tree at this head
  ok         tests/closure.py merge --partial --allow-failures
             `tests/closure.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         HPO_GATE_LOCK_LABEL=fault-text-gate GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=8ef450936a ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  ok         tests/typing_ruler.py
             `tests/typing_ruler.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         tests/config_flow_steps.py
             `tests/config_flow_steps.py` is in the tree at this head
  ok         tests/env_drift.py --all 8ef450936a
             `tests/env_drift.py` is in the tree at this head

FIGURES: 20 resolved, 4 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_entity_of.RETURN_DEL.3138a791.json b/tests/mutation_ledger/killed_by/config_flow.py/_entity_of.RETURN_DEL.3138a791.json
new file mode 100644
index 0000000000..34ceb3ca0a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_entity_of.RETURN_DEL.3138a791.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_entity_of RETURN_DEL 3138a791",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return selector.EntitySelector({**config, \"multiple\": True} if multiple else config)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.CMP_BOUND.870e4050.json b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.CMP_BOUND.870e4050.json
new file mode 100644
index 0000000000..4d5f72e674
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.CMP_BOUND.870e4050.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_fault_text_errors CMP_BOUND 870e4050",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    too_many = len(submit.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES) or ()) > FAULT_TEXT_ENTITIES_MAX",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`too_many = len(submit.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES) or ()) >= FAULT_TEXT_ENTITIES_MAX`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.RETURN_DEL.d348472e.json b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.RETURN_DEL.d348472e.json
new file mode 100644
index 0000000000..e4e70ad1e9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.RETURN_DEL.d348472e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_fault_text_errors RETURN_DEL d348472e",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return {CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: \"too_many_fault_text_entities\"} if too_many else {}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json
deleted file mode 100644
index a4e95f9597..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections GUARD_OFF cc44e904",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if bucket:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.e7efd72e.json b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.e7efd72e.json
deleted file mode 100644
index c29595553e..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.e7efd72e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections GUARD_OFF e7efd72e",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if key not in placed:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.RETURN_DEL.cd4695fb.json b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.RETURN_DEL.cd4695fb.json
deleted file mode 100644
index 26cd2e4983..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.RETURN_DEL.cd4695fb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections RETURN_DEL cd4695fb",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "    return fields",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.25f29392.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.25f29392.json
new file mode 100644
index 0000000000..1eac8baae7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.25f29392.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST 25f29392",
+  "killed_by": "tests/features.py",
+  "old": "TEXT_MAX_CHARS = 160",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`TEXT_MAX_CHARS = 320`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.4b08d3cd.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.4b08d3cd.json
new file mode 100644
index 0000000000..ab9837d610
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.4b08d3cd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST 4b08d3cd",
+  "killed_by": "tests/features.py",
+  "old": "CODES_MAX = 32",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CODES_MAX = 64`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.84182824.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.84182824.json
new file mode 100644
index 0000000000..497774c0fd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.84182824.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST 84182824",
+  "killed_by": "tests/features.py",
+  "old": "SAVE_MIN_S = 60.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SAVE_MIN_S = 120.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.a2232314.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.a2232314.json
new file mode 100644
index 0000000000..4aed75c889
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.a2232314.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST a2232314",
+  "killed_by": "tests/features.py",
+  "old": "FAULT_LOG_STORE_VERSION = 1",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`FAULT_LOG_STORE_VERSION = 2`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.e8da4cb8.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.e8da4cb8.json
new file mode 100644
index 0000000000..d05b7c89a3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.e8da4cb8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST e8da4cb8",
+  "killed_by": "tests/features.py",
+  "old": "EPISODES_MAX = 200",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`EPISODES_MAX = 400`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.f34207b8.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.f34207b8.json
new file mode 100644
index 0000000000..74dc5cc7e1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.f34207b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST f34207b8",
+  "killed_by": "tests/features.py",
+  "old": "REGISTER_MAX = 0xFFFFFFFF",
+  "reason": "CONST (doubled) on the 32-bit register cap this diff added. The inventory's textual mutant is `REGISTER_MAX = 8589934590xFFFFFFFF`: `_NUM` matches only the leading `0` of a hex literal, so `--pin-killed` reports it SKIP-UNPARSEABLE and never drives it. Applied as the value the operator names, `REGISTER_MAX = 0x1FFFFFFFE`, in a detached worktree at 08fc04fe96: `PYTHONPATH=tests/hastub:tools/devices python3 tools/audit/seat/features_block.py --prelude 'exec(open(OUT).read())' 'from heatpump_optimizer import fault_log as _fl' '# 7: the ring and the tally.'` (OUT from `--emit-prelude`) went from rc=0, 7 passed to rc=1, 1 of 7 failed: `the flag slot: ... null control, the same state on a binary_sensor reads through the flag path` (`str(0x100000000)` read as code `0x100000000` instead of NO_CODE). Null control: the same value written `4294967295` keeps rc=0, 7 passed. Measured 2026-11-25."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.8eff0fa3.json b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.8eff0fa3.json
new file mode 100644
index 0000000000..b1b960dd0c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.8eff0fa3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_apply GUARD_OFF 8eff0fa3",
+  "killed_by": "tests/features.py",
+  "old": "    if not read:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.ce287381.json b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.ce287381.json
new file mode 100644
index 0000000000..d65fa56faf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.ce287381.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_apply GUARD_OFF ce287381",
+  "killed_by": "tests/features.py",
+  "old": "    if note(rec.log, max(s for s, _t in read), read[-1][1], late=late):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_clip.CMP_BOUND.2173cf15.json b/tests/mutation_ledger/killed_by/fault_log.py/_clip.CMP_BOUND.2173cf15.json
new file mode 100644
index 0000000000..edcfebc8c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_clip.CMP_BOUND.2173cf15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_clip CMP_BOUND 2173cf15",
+  "killed_by": "tests/features.py",
+  "old": "    return item if len(item) <= TEXT_MAX_CHARS else \"\u2026\" + item[-TEXT_MAX_CHARS:]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return item if len(item) < TEXT_MAX_CHARS else \"\u2026\" + item[-TEXT_MAX_CHARS:]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_clip.RETURN_DEL.2173cf15.json b/tests/mutation_ledger/killed_by/fault_log.py/_clip.RETURN_DEL.2173cf15.json
new file mode 100644
index 0000000000..3fb79d63aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_clip.RETURN_DEL.2173cf15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_clip RETURN_DEL 2173cf15",
+  "killed_by": "tests/features.py",
+  "old": "    return item if len(item) <= TEXT_MAX_CHARS else \"\u2026\" + item[-TEXT_MAX_CHARS:]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.10b8b75c.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.10b8b75c.json
new file mode 100644
index 0000000000..e34fe8b9f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.10b8b75c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading GUARD_OFF 10b8b75c",
+  "killed_by": "tests/features.py",
+  "old": "    if read is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.a12b4eaf.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.a12b4eaf.json
new file mode 100644
index 0000000000..2cb7e83c0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.a12b4eaf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading GUARD_OFF a12b4eaf",
+  "killed_by": "tests/features.py",
+  "old": "    if rec.kind == \"text\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.c24cbf8a.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.c24cbf8a.json
new file mode 100644
index 0000000000..b7e6cd8c4c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.c24cbf8a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading GUARD_OFF c24cbf8a",
+  "killed_by": "tests/structure.py",
+  "old": "    if not isinstance(raw, str) or raw.strip().lower() in _UNREAD:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.79c7192e.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.79c7192e.json
new file mode 100644
index 0000000000..ba412b6773
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.79c7192e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading RETURN_DEL 79c7192e",
+  "killed_by": "tests/structure.py",
+  "old": "        return (True, code_text([rec.last.get(e) for e in rec.entities]))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.af2be7f3.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.af2be7f3.json
new file mode 100644
index 0000000000..f99dd78893
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.af2be7f3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading RETURN_DEL af2be7f3",
+  "killed_by": "tests/features.py",
+  "old": "    return (True, read[1])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.a6134d1e.json b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.a6134d1e.json
new file mode 100644
index 0000000000..8242c336ba
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.a6134d1e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_release GUARD_OFF a6134d1e",
+  "killed_by": "tests/features.py",
+  "old": "    if rec.closed:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.f2dc0db1.json b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.f2dc0db1.json
new file mode 100644
index 0000000000..5634949abb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.f2dc0db1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_release GUARD_OFF f2dc0db1",
+  "killed_by": "tests/features.py",
+  "old": "        if release is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_release.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/fault_log.py/_release.RETURN_DEL.80a0007e.json
new file mode 100644
index 0000000000..31b9dd4a69
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_release.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_release RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_request_save.CMP_BOUND.538cf5fd.json b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.CMP_BOUND.538cf5fd.json
new file mode 100644
index 0000000000..b1bcd6814b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.CMP_BOUND.538cf5fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_request_save CMP_BOUND 538cf5fd",
+  "killed_by": "tests/features.py",
+  "old": "    if wait <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if wait < 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.538cf5fd.json b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.538cf5fd.json
new file mode 100644
index 0000000000..6aa5e0e961
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.538cf5fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_request_save GUARD_OFF 538cf5fd",
+  "killed_by": "tests/features.py",
+  "old": "    if wait <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.b244e192.json b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.b244e192.json
new file mode 100644
index 0000000000..162894350e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.b244e192.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_request_save GUARD_OFF b244e192",
+  "killed_by": "tests/features.py",
+  "old": "    if rec.closed or rec.timer is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_seconds.RETURN_DEL.adc95fe0.json b/tests/mutation_ledger/killed_by/fault_log.py/_seconds.RETURN_DEL.adc95fe0.json
new file mode 100644
index 0000000000..e03ef0a015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_seconds.RETURN_DEL.adc95fe0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_seconds RETURN_DEL adc95fe0",
+  "killed_by": "tests/features.py",
+  "old": "    return int(stamp.timestamp()) if isinstance(stamp, datetime) else _now_s()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_tally.CMP_BOUND.4c126e21.json b/tests/mutation_ledger/killed_by/fault_log.py/_tally.CMP_BOUND.4c126e21.json
new file mode 100644
index 0000000000..bf7375e39b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_tally.CMP_BOUND.4c126e21.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_tally CMP_BOUND 4c126e21",
+  "killed_by": "tests/features.py",
+  "old": "    key = text if text in log.codes or len(log.codes) < CODES_MAX else OTHER",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`key = text if text in log.codes or len(log.codes) <= CODES_MAX else OTHER`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_tally.GUARD_OFF.e6901531.json b/tests/mutation_ledger/killed_by/fault_log.py/_tally.GUARD_OFF.e6901531.json
new file mode 100644
index 0000000000..51a11e0b87
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_tally.GUARD_OFF.e6901531.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_tally GUARD_OFF e6901531",
+  "killed_by": "tests/features.py",
+  "old": "    if text == NO_CODE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_close.BOOLOP.91a18c0a.json b/tests/mutation_ledger/killed_by/fault_log.py/async_close.BOOLOP.91a18c0a.json
new file mode 100644
index 0000000000..a22ae7204d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_close.BOOLOP.91a18c0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_close BOOLOP 91a18c0a",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if rec is not None and _release(rec):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if rec is not None or _release(rec):`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_close.GUARD_OFF.91a18c0a.json b/tests/mutation_ledger/killed_by/fault_log.py/async_close.GUARD_OFF.91a18c0a.json
new file mode 100644
index 0000000000..514c4a6e72
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_close.GUARD_OFF.91a18c0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_close GUARD_OFF 91a18c0a",
+  "killed_by": "tests/features.py",
+  "old": "    if rec is not None and _release(rec):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup.BOOLOP.735d6589.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.BOOLOP.735d6589.json
new file mode 100644
index 0000000000..38919a7726
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.BOOLOP.735d6589.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup BOOLOP 735d6589",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if old is not None and old.ending is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if old is not None or old.ending is not None:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.57b55919.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.57b55919.json
new file mode 100644
index 0000000000..2b2b1a6dff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.57b55919.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup GUARD_OFF 57b55919",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if source is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.735d6589.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.735d6589.json
new file mode 100644
index 0000000000..353f9dfbb2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.735d6589.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup GUARD_OFF 735d6589",
+  "killed_by": "tests/features.py",
+  "old": "    if old is not None and old.ending is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup._changed.GUARD_OFF.16b948e4.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._changed.GUARD_OFF.16b948e4.json
new file mode 100644
index 0000000000..e9bc96c820
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._changed.GUARD_OFF.16b948e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup._changed GUARD_OFF 16b948e4",
+  "killed_by": "tests/features.py",
+  "old": "        if not rec.closed:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup._ended.GUARD_OFF.bacd1d14.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._ended.GUARD_OFF.bacd1d14.json
new file mode 100644
index 0000000000..ca0352edef
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._ended.GUARD_OFF.bacd1d14.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup._ended GUARD_OFF bacd1d14",
+  "killed_by": "tests/features.py",
+  "old": "        if _release(rec):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.6c26d72e.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.6c26d72e.json
new file mode 100644
index 0000000000..06183ff102
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.6c26d72e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text BOOLOP 6c26d72e",
+  "killed_by": "tests/features.py",
+  "old": "        if kept and length + add > TEXT_MAX_CHARS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if kept or length + add > TEXT_MAX_CHARS:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.7ab93919.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.7ab93919.json
new file mode 100644
index 0000000000..3845bdeda2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.7ab93919.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text BOOLOP 7ab93919",
+  "killed_by": "tests/features.py",
+  "old": "        if state is not None and state.strip().casefold() not in HEALTHY",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if state is not None or state.strip().casefold() not in HEALTHY`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.CMP_BOUND.6c26d72e.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.CMP_BOUND.6c26d72e.json
new file mode 100644
index 0000000000..dcfe903d1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.CMP_BOUND.6c26d72e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text CMP_BOUND 6c26d72e",
+  "killed_by": "tests/features.py",
+  "old": "        if kept and length + add > TEXT_MAX_CHARS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if kept and length + add >= TEXT_MAX_CHARS:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.1cb525c8.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.1cb525c8.json
new file mode 100644
index 0000000000..a3cbb1e4e9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.1cb525c8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text GUARD_OFF 1cb525c8",
+  "killed_by": "tests/features.py",
+  "old": "    if not items:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.6c26d72e.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.6c26d72e.json
new file mode 100644
index 0000000000..e9982e43ee
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.6c26d72e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text GUARD_OFF 6c26d72e",
+  "killed_by": "tests/features.py",
+  "old": "        if kept and length + add > TEXT_MAX_CHARS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.RETURN_DEL.7b6f84a2.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.RETURN_DEL.7b6f84a2.json
new file mode 100644
index 0000000000..d9b93fc539
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.RETURN_DEL.7b6f84a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text RETURN_DEL 7b6f84a2",
+  "killed_by": "tests/features.py",
+  "old": "    return \", \".join(kept) + (f\" +{dropped}\" if dropped else \"\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.CLAMP_DROP.392df3a8.json b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.CLAMP_DROP.392df3a8.json
new file mode 100644
index 0000000000..88a41d3880
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.CLAMP_DROP.392df3a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:diagnostics_view CLAMP_DROP 392df3a8",
+  "killed_by": "tests/features.py",
+  "old": "            \"start\": _iso(log.open[0]), \"seconds\": max(0, now_s - log.open[0]),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`\"start\": _iso(log.open[0]), \"seconds\": (0),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.GUARD_OFF.44ed6e87.json b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.GUARD_OFF.44ed6e87.json
new file mode 100644
index 0000000000..7a369efa03
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.GUARD_OFF.44ed6e87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:diagnostics_view GUARD_OFF 44ed6e87",
+  "killed_by": "tests/features.py",
+  "old": "    if rec is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.BOOLOP.bba5c3da.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.BOOLOP.bba5c3da.json
new file mode 100644
index 0000000000..4b17fb53ad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.BOOLOP.bba5c3da.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text BOOLOP bba5c3da",
+  "killed_by": "tests/features.py",
+  "old": "    source = \"bitmap\" if number is not None and number.is_integer() else \"flag\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`source = \"bitmap\" if number is not None or number.is_integer() else \"flag\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.1d76026d.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.1d76026d.json
new file mode 100644
index 0000000000..db2e7d4e11
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.1d76026d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text GUARD_OFF 1d76026d",
+  "killed_by": "tests/features.py",
+  "old": "    if flag is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.385ce0f0.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.385ce0f0.json
new file mode 100644
index 0000000000..0179a1b966
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.385ce0f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text GUARD_OFF 385ce0f0",
+  "killed_by": "tests/features.py",
+  "old": "    if not flag:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.4ea770b7.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.4ea770b7.json
new file mode 100644
index 0000000000..a0c431998d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.4ea770b7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text GUARD_OFF 4ea770b7",
+  "killed_by": "tests/structure.py",
+  "old": "    if source == \"bitmap\" and number is not None and 0 < number <= REGISTER_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.RETURN_DEL.6dd50371.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.RETURN_DEL.6dd50371.json
new file mode 100644
index 0000000000..caf751cb4a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.RETURN_DEL.6dd50371.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text RETURN_DEL 6dd50371",
+  "killed_by": "tests/features.py",
+  "old": "    return (source, NO_CODE)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/loaded.BOOLOP.77a723dd.json b/tests/mutation_ledger/killed_by/fault_log.py/loaded.BOOLOP.77a723dd.json
new file mode 100644
index 0000000000..1547163196
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/loaded.BOOLOP.77a723dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:loaded BOOLOP 77a723dd",
+  "killed_by": "tests/features.py",
+  "old": "        open=list(opened) if isinstance(opened, list) and len(opened) == 2 else None,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`open=list(opened) if isinstance(opened, list) or len(opened) == 2 else None,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/loaded.GUARD_OFF.821696d2.json b/tests/mutation_ledger/killed_by/fault_log.py/loaded.GUARD_OFF.821696d2.json
new file mode 100644
index 0000000000..9e87f310c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/loaded.GUARD_OFF.821696d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:loaded GUARD_OFF 821696d2",
+  "killed_by": "tests/structure.py",
+  "old": "    if not isinstance(raw, Mapping) or not raw or not admitted(\"fault_log\", raw):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.60e27395.json b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.60e27395.json
new file mode 100644
index 0000000000..510b870f05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.60e27395.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note BOOLOP 60e27395",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is not None and log.open[1] == text:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if log.open is not None or log.open[1] == text:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.cf6b21fd.json b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.cf6b21fd.json
new file mode 100644
index 0000000000..3fbb1a95b4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.cf6b21fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note BOOLOP cf6b21fd",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is None and text is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if log.open is None or text is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.CLAMP_DROP.240a7557.json b/tests/mutation_ledger/killed_by/fault_log.py/note.CLAMP_DROP.240a7557.json
new file mode 100644
index 0000000000..848f4a3776
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.CLAMP_DROP.240a7557.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note CLAMP_DROP 240a7557",
+  "killed_by": "tests/features.py",
+  "old": "        end_s = max(now_s, start_s)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`end_s = (now_s)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.CMP_BOUND.45ba8896.json b/tests/mutation_ledger/killed_by/fault_log.py/note.CMP_BOUND.45ba8896.json
new file mode 100644
index 0000000000..5263c16564
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.CMP_BOUND.45ba8896.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note CMP_BOUND 45ba8896",
+  "killed_by": "tests/features.py",
+  "old": "        if len(log.episodes) > EPISODES_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(log.episodes) >= EPISODES_MAX:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.2a982e58.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.2a982e58.json
new file mode 100644
index 0000000000..2d153b97dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.2a982e58.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 2a982e58",
+  "killed_by": "tests/features.py",
+  "old": "    if text is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.45ba8896.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.45ba8896.json
new file mode 100644
index 0000000000..67ba0eff61
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.45ba8896.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 45ba8896",
+  "killed_by": "tests/features.py",
+  "old": "        if len(log.episodes) > EPISODES_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.60e27395.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.60e27395.json
new file mode 100644
index 0000000000..4e53de6730
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.60e27395.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 60e27395",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is not None and log.open[1] == text:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.9aa017ad.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.9aa017ad.json
new file mode 100644
index 0000000000..f88aaa2888
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.9aa017ad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 9aa017ad",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.cf6b21fd.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.cf6b21fd.json
new file mode 100644
index 0000000000..3c9318eeed
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.cf6b21fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF cf6b21fd",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is None and text is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/fault_log.py/note.RETURN_DEL.80a0007e.json
new file mode 100644
index 0000000000..9969d93b66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/sources.GUARD_OFF.91f3668a.json b/tests/mutation_ledger/killed_by/fault_log.py/sources.GUARD_OFF.91f3668a.json
new file mode 100644
index 0000000000..ed55943400
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/sources.GUARD_OFF.91f3668a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:sources GUARD_OFF 91f3668a",
+  "killed_by": "tests/features.py",
+  "old": "    if members:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/sources.RETURN_DEL.a5bac6c6.json b/tests/mutation_ledger/killed_by/fault_log.py/sources.RETURN_DEL.a5bac6c6.json
new file mode 100644
index 0000000000..3e57f2f8b6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/sources.RETURN_DEL.a5bac6c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:sources RETURN_DEL a5bac6c6",
+  "killed_by": "tests/features.py",
+  "old": "    return (\"flag\", [flag]) if flag else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.BOOLOP.0d125c94.json b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.BOOLOP.0d125c94.json
new file mode 100644
index 0000000000..9fd3d1b00f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.BOOLOP.0d125c94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/modbus_prefill.py:infer BOOLOP 0d125c94",
+  "killed_by": "tests/features.py",
+  "old": "    if listed is not None and not current.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if listed is not None or not current.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.GUARD_OFF.0d125c94.json b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.GUARD_OFF.0d125c94.json
new file mode 100644
index 0000000000..eecb39c709
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.GUARD_OFF.0d125c94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/modbus_prefill.py:infer GUARD_OFF 0d125c94",
+  "killed_by": "tests/features.py",
+  "old": "    if listed is not None and not current.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/survivor_triage/fault_log.py/flag_text.CMP_BOUND.4ea770b7.json b/tests/mutation_ledger/survivor_triage/fault_log.py/flag_text.CMP_BOUND.4ea770b7.json
new file mode 100644
index 0000000000..6ce7aa38d1
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/fault_log.py/flag_text.CMP_BOUND.4ea770b7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text CMP_BOUND 4ea770b7",
+  "old": "    if source == \"bitmap\" and number is not None and 0 < number <= REGISTER_MAX:",
+  "reason": "Equivalent (CMP_BOUND, `0 < number` -> `0 <= number`): the line is reached only on a reading parse_bool took as a fault, and parse_bool reads a number as a fault exactly when it is non-zero, so number is never 0 here and the two bounds pick the same branch on every input. Measured by the R11-OWNER-FAULT-TEXT fixer's mutant_run.py drive of the diff's fault_log.py mutants over the fault-record block of tests/features.py: SURVIVED rc=0; the same block kills the bound's other side (`1 < number`, by the reading 1 giving 0x0001) and the register cap (`0 < number` alone, by 2**32 giving no code).",
+  "verdict": "equivalent"
+}


## Review scope: full (no verdict on verdict/<pr> names the reviewed head 5f8e2cdb5fe2d236f71c62f8d41b31836df88107, so there is no finding to confirm resolved)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/__init__.py b/custom_components/heatpump_optimizer/__init__.py
index 2ef73de4ed..33f388c169 100644
--- a/custom_components/heatpump_optimizer/__init__.py
+++ b/custom_components/heatpump_optimizer/__init__.py
@@ -360,6 +360,9 @@ async def async_setup_entry(
         hass, entry, coordinator
     )
 
+    # The pump's fault record (R11-OWNER-FAULT-TEXT): its own listener and store.
+    await (await _async_lazy(hass, "fault_log")).async_setup(hass, entry, EntryConfig.from_mapping(config))
+
     # Serve and register the Lovelace dashboard card (idempotent; runs once).
     await (await _async_lazy(hass, "frontend")).async_register_frontend(
         hass, coordinator.integration_version
@@ -451,6 +454,7 @@ async def async_unload_entry(
         restore = (await _async_lazy(hass, "off_restore")).async_restore
         await restore(hass, entry, coordinator.effective_config, "unload")
         await (await _async_lazy(hass, "room_record")).async_flush(coordinator)
+        await (await _async_lazy(hass, "fault_log")).async_close(entry)
         await coordinator.async_shutdown()
         # Once more behind the released latch: a write that raced the first
         # pass armed again, and nothing can arm after it.
diff --git a/custom_components/heatpump_optimizer/config_flow.py b/custom_components/heatpump_optimizer/config_flow.py
index 13c3332913..7e4b09985a 100644
--- a/custom_components/heatpump_optimizer/config_flow.py
+++ b/custom_components/heatpump_optimizer/config_flow.py
@@ -63,6 +63,8 @@ from .const import (
     CONF_HEAT_PUMP_DEFROST_ENTITY,
     CONF_HEAT_PUMP_ONLINE_ENTITY,
     CONF_HEAT_PUMP_FAULT_ENTITY,
+    CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES,
+    FAULT_TEXT_ENTITIES_MAX,
     CONF_HEAT_PUMP_BACKUP_HEATER_ENTITY,
     CONF_HEAT_PUMP_DHW_BOOSTER_ENTITY,
     CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
@@ -1139,7 +1141,7 @@ def _valid_months_spec(spec: Any) -> bool:
 
 
 def _entity_of(
-    domain: str | list[str], device_class: str | None = None
+    domain: str | list[str], device_class: str | None = None, *, multiple: bool = False
 ) -> selector.EntitySelector:
     """An entity picker, optionally narrowed to a device class.
 
@@ -1156,9 +1158,8 @@ def _entity_of(
     }
     if device_class is not None:
         entity_filter["device_class"] = [device_class]
-    return selector.EntitySelector(
-        selector.EntitySelectorConfig(filter=[entity_filter])
-    )
+    config = selector.EntitySelectorConfig(filter=[entity_filter])
+    return selector.EntitySelector({**config, "multiple": True} if multiple else config)
 
 
 def _room_thermometers() -> selector.EntitySelector:
@@ -1436,31 +1437,18 @@ def _user_sensors_fields(hass: HomeAssistant) -> dict[Any, Any]:
 
     Flat, and deliberately so: this is the reconfigure path's key source and
     ``_first_screen_schema`` merges it, both of which want the bare markers.
-    ``_user_sensors_sections`` is what the setup page renders (#824).
+    ``_user_sensors_sections`` is what the setup page renders (#824). The keys
+    are ``_USER_SENSORS_GROUPS``'s, each rendered by its registry row; two
+    carry a default.
     """
+    defaults = {
+        CONF_SOLAR_FORECAST_SOURCE: DEFAULT_SOLAR_FORECAST_SOURCE,
+        CONF_SOLAR_LOCATION: _default_location(hass, {}),
+    }
     return {
-        vol.Optional(CONF_INDOOR_TEMP_ENTITY): _prefill_row(CONF_INDOOR_TEMP_ENTITY).widget,
-        vol.Optional(CONF_OUTDOOR_TEMP_ENTITY): _prefill_row(CONF_OUTDOOR_TEMP_ENTITY).widget,
-        vol.Optional(CONF_HEAT_PUMP_SWITCH_ENTITY): _prefill_row(CONF_HEAT_PUMP_SWITCH_ENTITY).widget,
-        vol.Optional(CONF_SOLAR_RADIATION_ENTITY): _prefill_row(CONF_SOLAR_RADIATION_ENTITY).widget,
-        vol.Optional(
-            CONF_SOLAR_FORECAST_SOURCE,
-            default=DEFAULT_SOLAR_FORECAST_SOURCE,
-        ): _prefill_row(CONF_SOLAR_FORECAST_SOURCE).widget,
-        vol.Optional(
-            CONF_SOLAR_LOCATION,
-            default=_default_location(hass, {}),
-        ): _prefill_row(CONF_SOLAR_LOCATION).widget,
-        vol.Optional(CONF_FLOOR_RETURN_TEMP_ENTITY): _prefill_row(CONF_FLOOR_RETURN_TEMP_ENTITY).widget,
-        vol.Optional(CONF_LOWER_FLOOR_TEMP_ENTITY): _prefill_row(CONF_LOWER_FLOOR_TEMP_ENTITY).widget,
-        vol.Optional(CONF_DHW_TEMP_ENTITY): _prefill_row(CONF_DHW_TEMP_ENTITY).widget,
-        vol.Optional(
-            CONF_BUFFER_TANK_TEMP_ENTITY
-        ): _prefill_row(CONF_BUFFER_TANK_TEMP_ENTITY).widget,
-        vol.Optional(CONF_HEAT_PUMP_MODE_ENTITY): _prefill_row(CONF_HEAT_PUMP_MODE_ENTITY).widget,
-        vol.Optional(CONF_HEAT_PUMP_DEFROST_ENTITY): _prefill_row(CONF_HEAT_PUMP_DEFROST_ENTITY).widget,
-        vol.Optional(CONF_HEAT_PUMP_ONLINE_ENTITY): _prefill_row(CONF_HEAT_PUMP_ONLINE_ENTITY).widget,
-        vol.Optional(CONF_HEAT_PUMP_FAULT_ENTITY): _prefill_row(CONF_HEAT_PUMP_FAULT_ENTITY).widget,
+        (vol.Optional(key, default=defaults[key]) if key in defaults else vol.Optional(key)):
+            _prefill_row(key).widget
+        for _group, keys in _USER_SENSORS_GROUPS for key in keys
     }
 
 
@@ -1500,23 +1488,18 @@ _USER_SENSORS_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
 
 
 def _user_sensors_sections(hass: HomeAssistant) -> dict[Any, Any]:
-    """The setup page's fourteen pickers, grouped as the options flow groups them."""
+    """The setup page's fourteen pickers, grouped as the options flow groups them.
+
+    ``_user_sensors_fields`` is built from the same table, so no picker can be
+    left out of a section: the grouping cannot drop one (the defect #824's
+    flat-field fallback guarded against while the two were separate lists).
+    """
     flat = _user_sensors_fields(hass)
     by_key = {str(getattr(marker, "schema", marker)): marker for marker in flat}
-    placed: set[str] = set()
-    fields: dict[Any, Any] = {}
-    for group, keys in _USER_SENSORS_GROUPS:
-        bucket = {by_key[k]: flat[by_key[k]] for k in keys if k in by_key}
-        placed.update(k for k in keys if k in by_key)
-        if bucket:
-            fields[group] = section(vol.Schema(bucket), {"collapsed": False})
-    # Any field the table above forgot stays visible and flat rather than
-    # vanishing -- a grouping that silently drops a picker is worse than an
-    # ungrouped page, which is the defect this replaces.
-    for key, marker in by_key.items():
-        if key not in placed:
-            fields[marker] = flat[marker]
-    return fields
+    return {
+        group: section(vol.Schema({by_key[k]: flat[by_key[k]] for k in keys}), {"collapsed": False})
+        for group, keys in _USER_SENSORS_GROUPS
+    }
 
 
 def _first_screen_schema(hass: HomeAssistant) -> vol.Schema:
@@ -1785,6 +1768,9 @@ _OPTION_FIELDS: Final[tuple[_F, ...]] = (
     _F("entities_pump", CONF_HEAT_PUMP_DEFROST_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_DEFROST_ENTITY]))),
     _F("entities_pump", CONF_HEAT_PUMP_ONLINE_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_ONLINE_ENTITY]))),
     _F("entities_pump", CONF_HEAT_PUMP_FAULT_ENTITY, _STORED, _entity_of(list(topology.ASSIGNABLE_KEYS[CONF_HEAT_PUMP_FAULT_ENTITY]))),
+    # The fault's own code text, 1 to FAULT_TEXT_ENTITIES_MAX entities, read only
+    # by ``fault_log``; options-only like the flags below.
+    _F("entities_pump", CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES, _STORED, _entity_of(['sensor', 'text', 'input_text'], multiple=True)),
     # The pump's own electric heat and its night mode. Options-only, with no
     # row in ``topology._SLOTS`` -- the precedent is the compressor-frequency
     # pair above, which is options-only for the same reason: they are not
@@ -2684,6 +2670,12 @@ def _clear_absent(
     return cleaned
 
 
+async def _fault_text_errors(submit: dict[str, Any], _current: dict[str, Any]) -> dict[str, str]:
+    """A fault-text list is at most ``FAULT_TEXT_ENTITIES_MAX`` entities: the selector caps nothing."""
+    too_many = len(submit.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES) or ()) > FAULT_TEXT_ENTITIES_MAX
+    return {CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: "too_many_fault_text_entities"} if too_many else {}
+
+
 async def _room_list_errors(submit: dict[str, Any], _current: dict[str, Any]) -> dict[str, str]:
     """A room list is at most ``rooms.ROOMS_MAX`` entities."""
     too_many = len(submit.get(CONF_ROOM_TEMPERATURE_ENTITIES) or ()) > rooms.ROOMS_MAX
@@ -3815,7 +3807,7 @@ class HeatPumpOptimizerOptionsFlow(_StoredValuesAlwaysFit, config_entries.Option
             errors[CONF_FREQ_CONTROL_MODE] = "freq_control_needs_number"
         return errors
 
-    async_step_entities_pump = _registry_step("entities_pump")
+    async_step_entities_pump = _registry_step("entities_pump", _fault_text_errors)
 
     async_step_rooms = _registry_step("rooms", _room_list_errors)
 
diff --git a/custom_components/heatpump_optimizer/const.py b/custom_components/heatpump_optimizer/const.py
index f30638dd17..b8166588cf 100644
--- a/custom_components/heatpump_optimizer/const.py
+++ b/custom_components/heatpump_optimizer/const.py
@@ -143,12 +143,20 @@ CONF_HOUSE_POWER_ENTITY: Final = "house_power_entity"
 #     the outdoor coil; the interval's electricity bought no room heat at all.
 #   * Online. The one signal that closes a real gap in cloud mode — see the
 #     horizon comment below.
-#   * Fault. Non-zero means the unit is reporting a problem. The code itself
-#     is discarded by the source integration, so what reaches us is a flag.
+#   * Fault. Non-zero means the unit is reporting a problem. This slot is
+#     read as a flag; the codes themselves come from the fault-text slot
+#     below, which only ``fault_log.py`` reads.
 CONF_HEAT_PUMP_MODE_ENTITY: Final = "heat_pump_mode_entity"
 CONF_HEAT_PUMP_DEFROST_ENTITY: Final = "heat_pump_defrost_entity"
 CONF_HEAT_PUMP_ONLINE_ENTITY: Final = "heat_pump_online_entity"
 CONF_HEAT_PUMP_FAULT_ENTITY: Final = "heat_pump_fault_entity"
+#: The pump's fault-description entities (R11-OWNER-FAULT-TEXT): 1 to
+#: ``FAULT_TEXT_ENTITIES_MAX`` sensors whose state is ``OK`` or a comma list of
+#: codes -- the Tuya integration's "Fault Description", the GCHV package's four
+#: "HP Alarm bitmap" sensors. Options-only; the options step enforces the cap,
+#: which a multiple entity selector does not.
+CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: Final = "heat_pump_fault_text_entities"
+FAULT_TEXT_ENTITIES_MAX: Final = 4
 
 # --- What the pump's own electric heat and its night mode are doing --------
 #
diff --git a/custom_components/heatpump_optimizer/device_prefill.py b/custom_components/heatpump_optimizer/device_prefill.py
index a8b23a184c..595118d0f6 100644
--- a/custom_components/heatpump_optimizer/device_prefill.py
+++ b/custom_components/heatpump_optimizer/device_prefill.py
@@ -56,6 +56,8 @@ from . import name_match
 from .const import (
     CONF_DHW_TEMP_ENTITY,
     CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
+    CONF_HEAT_PUMP_FAULT_ENTITY,
+    CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES,
     CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
     CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
     CONF_OUTDOOR_TEMP_ENTITY,
@@ -128,6 +130,10 @@ _TUYA_HEAT_PUMP: dict[tuple[str, str], tuple[str, float]] = {
     ("sensor", "Tin"): (CONF_HEAT_PUMP_RETURN_TEMP_ENTITY, 1.0),
     ("switch", "night_mode"): (CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY, 1.0),
     ("number", "DHWSET"): ("r404", 1.0),
+    # R11-OWNER-FAULT-TEXT (owner ruling 2026-11-22): the model's Fault Alarm
+    # and its dp 20 "Fault Description" (``OK`` or a comma list of codes).
+    ("binary_sensor", "fault"): (CONF_HEAT_PUMP_FAULT_ENTITY, 1.0),
+    ("sensor", "fault_description"): (CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES, 1.0),
 }
 
 #: The pairs above that no other model file in that repo defines at
diff --git a/custom_components/heatpump_optimizer/diagnostics.py b/custom_components/heatpump_optimizer/diagnostics.py
index c3a1b8681e..71a44956f1 100644
--- a/custom_components/heatpump_optimizer/diagnostics.py
+++ b/custom_components/heatpump_optimizer/diagnostics.py
@@ -77,7 +77,7 @@ from homeassistant.core import HomeAssistant
 from homeassistant.util import dt as dt_util
 
 from . import heat_curve
-from . import accuracy, debugger, draw_range, early_cutoff, pump_arbiter, replay_doc, room_record
+from . import accuracy, debugger, draw_range, early_cutoff, fault_log, pump_arbiter, replay_doc, room_record
 from .const import CONF_COP_SCALE, CONF_TIBBER_TOKEN, DOMAIN, LOCATION_KEYS, PRIVATE_ENTITY_ID
 from .drift import stored_age_seconds
 from .inputs import OUTRANKS_STALE, describe_problem, health_summary
@@ -381,6 +381,8 @@ _VIEWS: tuple[tuple[str, Callable[[Any], Any]], ...] = (
     # Why the observed-COP sensor has nothing yet: it is unavailable then, and
     # Home Assistant hides an unavailable entity's attributes.
     ("cop_learner", lambda c: accuracy.diagnostics_view(c.measured_cop, c.thermal_params, c.accuracy.draw)),
+    # The pump's fault codes, start and end: null with no fault source configured.
+    ("fault_log", lambda c: fault_log.diagnostics_view(c.entry)),
 )
 
 
diff --git a/custom_components/heatpump_optimizer/entry_config.py b/custom_components/heatpump_optimizer/entry_config.py
index 620a43e0a1..cb47239929 100644
--- a/custom_components/heatpump_optimizer/entry_config.py
+++ b/custom_components/heatpump_optimizer/entry_config.py
@@ -137,6 +137,7 @@ class EntryConfig(Mapping[str, Any]):
     grid_fee_entity: str | None = _entity_slot()
     heat_pump_capacity_limited_entity: str | None = _entity_slot()
     heat_pump_defrost_entity: str | None = _entity_slot()
+    heat_pump_fault_entity: str | None = _entity_slot()
     heat_pump_mode_entity: str | None = _entity_slot()
     heat_pump_power_entity: str | None = _entity_slot()
     heat_pump_supply_temp_entity: str | None = _entity_slot()
@@ -158,6 +159,8 @@ class EntryConfig(Mapping[str, Any]):
     weather_entity: str | None = _entity_slot()
     # The room thermometers (#3616): an entity list, not a slot.
     room_temperature_entities: tuple[str, ...] = _key((), _entities)
+    # The pump's fault-description entities (R11-OWNER-FAULT-TEXT), a list too.
+    heat_pump_fault_text_entities: tuple[str, ...] = _key((), _entities)
 
     # Switches.
     capacity_curve_enabled: bool = _key(const.DEFAULT_CAPACITY_CURVE_ENABLED, _flag)
diff --git a/custom_components/heatpump_optimizer/fault_log.py b/custom_components/heatpump_optimizer/fault_log.py
new file mode 100644
index 0000000000..70f1d77aef
--- /dev/null
+++ b/custom_components/heatpump_optimizer/fault_log.py
@@ -0,0 +1,374 @@
+"""The pump's fault record (R11-OWNER-FAULT-TEXT): each fault's code, start and end.
+
+One record per config entry, in a ``WeakKeyDictionary`` keyed by the entry
+(``off_restore``'s precedent), with its own ``QuarantiningStore``. The source is
+one rule per install:
+
+* ``text``: the fault-text slot, 1 to 4 entities whose state is ``OK`` or a
+  comma list of codes. A member is healthy when its state is in
+  :data:`HEALTHY`; every other text is recorded as the code, because the slot
+  exists for vocabularies this integration does not know.
+* ``bitmap`` / ``flag``: no text slot, so the fault-alarm flag slot, read as
+  ``InputReader.read_bool`` reads it. An integral number is kept as hex (the
+  register), anything else as a time span with no code.
+* neither: no record, no listener, no store.
+
+A state-change listener stamps every change with the state's ``last_changed``,
+so a fault that clears inside an update cycle is still a row. The record is
+saved on every row opened or closed, at most once per :data:`SAVE_MIN_S`: a
+save asked for inside that window is deferred to its end, never dropped.
+
+Only ``__init__`` (setup, unload) and ``diagnostics`` (the view) import this.
+The pure core -- :func:`note`, :func:`code_text`, :func:`flag_text`,
+:func:`loaded`, :func:`stored` -- runs without Home Assistant.
+"""
+from __future__ import annotations
+
+import logging
+import time
+from collections.abc import Awaitable, Callable, Mapping, Sequence
+from dataclasses import dataclass, field
+from datetime import datetime, timezone
+from typing import Any
+from weakref import WeakKeyDictionary
+
+from homeassistant.const import EVENT_HOMEASSISTANT_STOP
+from homeassistant.core import HomeAssistant, callback
+from homeassistant.helpers.event import async_call_later, async_track_state_change_event
+
+from .const import DOMAIN, FAULT_TEXT_ENTITIES_MAX
+from .entry_config import EntryConfig
+from .inputs import AMBIGUOUS_ACTIVITY_TOKENS, BOOL_FALSE, is_flag_domain, parse_bool
+from .store import QuarantiningStore, admitted, load_mapping
+
+_LOGGER = logging.getLogger(__name__)
+
+FAULT_LOG_STORE_VERSION = 1
+#: Closed rows kept, oldest evicted first (a row is at most ~361 B in memory).
+EPISODES_MAX = 200
+#: Distinct code texts tallied; the rest fold into :data:`OTHER`.
+CODES_MAX = 32
+OTHER = "other"
+#: A row's code text keeps whole items within this many characters.
+TEXT_MAX_CHARS = 160
+#: At most one save per this many seconds; a 1 Hz flap writes once a minute.
+SAVE_MIN_S = 60.0
+#: A member reading one of these, stripped and case-folded, reports no fault.
+HEALTHY: frozenset[str] = frozenset(
+    {"ok", "none", "normal", "no fault", ""} | BOOL_FALSE | AMBIGUOUS_ACTIVITY_TOKENS
+)
+#: The widest register read as a code (32 bits); a larger number is a flag, so
+#: a row's text stays within its bound.
+REGISTER_MAX = 0xFFFFFFFF
+#: A flag-slot fault with no code: recorded as a span, shown with a null code.
+NO_CODE = ""
+_UNREAD = ("unavailable", "unknown")
+
+
+@dataclass
+class Log:
+    """The pure record: closed rows, the open one, the per-code tally."""
+
+    since_s: int
+    source: str | None = None
+    #: ``[start_s, end_s, text, late]``, oldest first.
+    episodes: list[list[Any]] = field(default_factory=list)
+    dropped: int = 0
+    #: ``[start_s, text]`` while a fault is open.
+    open: list[Any] | None = None
+    #: ``text -> [count, total_s, last_end_s]``.
+    codes: dict[str, list[int]] = field(default_factory=dict)
+
+
+def _tally(log: Log, text: str, start_s: int, end_s: int) -> None:
+    if text == NO_CODE:
+        return
+    key = text if text in log.codes or len(log.codes) < CODES_MAX else OTHER
+    row = log.codes.setdefault(key, [0, 0, 0])
+    row[0] += 1
+    row[1] += end_s - start_s
+    row[2] = end_s
+
+
+def note(log: Log, now_s: int, text: str | None, *, late: bool = False) -> bool:
+    """Apply one reading: ``text`` is the fault's code text, ``None`` healthy.
+
+    Whether a row opened or closed. A change of text while open closes the row
+    and opens the next at the same instant. ``late`` marks the row this
+    reading closes as one that ended while nothing was watching.
+    """
+    if log.open is not None and log.open[1] == text:
+        return False
+    if log.open is None and text is None:
+        return False
+    if log.open is not None:
+        start_s, was = log.open
+        end_s = max(now_s, start_s)
+        log.episodes.append([start_s, end_s, was, late])
+        _tally(log, was, start_s, end_s)
+        if len(log.episodes) > EPISODES_MAX:
+            del log.episodes[0]
+            log.dropped += 1
+        log.open = None
+    if text is not None:
+        log.open = [now_s, text]
+    return True
+
+
+def _clip(item: str) -> str:
+    """An item longer than the cap keeps its tail: GCHV names end in the code."""
+    return item if len(item) <= TEXT_MAX_CHARS else "…" + item[-TEXT_MAX_CHARS:]
+
+
+def code_text(states: Sequence[str | None]) -> str | None:
+    """The fault members' items in slot order, or ``None`` when every member is healthy.
+
+    ``None`` members (never read) count as healthy. Items are kept whole while
+    the text stays within :data:`TEXT_MAX_CHARS`; `` +N`` counts those dropped.
+    """
+    items = [
+        part.strip()
+        for state in states
+        if state is not None and state.strip().casefold() not in HEALTHY
+        for part in state.split(",")
+        if part.strip()
+    ]
+    if not items:
+        return None
+    kept: list[str] = []
+    length = 0
+    for item in map(_clip, items):
+        add = len(item) + (2 if kept else 0)
+        if kept and length + add > TEXT_MAX_CHARS:
+            break
+        kept.append(item)
+        length += add
+    dropped = len(items) - len(kept)
+    return ", ".join(kept) + (f" +{dropped}" if dropped else "")
+
+
+def flag_text(entity_id: str, state: str) -> tuple[str, str | None] | None:
+    """The flag slot's reading as ``(source, text)``, or ``None`` when it is no reading.
+
+    The canonical strict read: free text that only names an activity is no
+    evidence. An integral number is a register (``bitmap``), healthy at zero,
+    and a positive one is the fault's code, in hex.
+    """
+    flag = parse_bool(state, strict=not is_flag_domain(entity_id))
+    if flag is None:
+        return None
+    try:
+        number: float | None = float(state)
+    except (TypeError, ValueError):
+        number = None
+    source = "bitmap" if number is not None and number.is_integer() else "flag"
+    if not flag:
+        return (source, None)
+    if source == "bitmap" and number is not None and 0 < number <= REGISTER_MAX:
+        return (source, f"0x{int(number):04X}")
+    return (source, NO_CODE)
+
+
+def stored(log: Log) -> dict[str, Any]:
+    """The record as its store document, copied: the store serialises it off the loop."""
+    return {
+        "since_s": log.since_s, "source": log.source, "episodes": [list(r) for r in log.episodes],
+        "dropped": log.dropped, "open": None if log.open is None else list(log.open),
+        "codes": {k: list(v) for k, v in log.codes.items()},
+    }
+
+
+def loaded(raw: Any, now_s: int) -> Log:
+    """A store document as a record; one outside its declaration starts afresh at ``now_s``."""
+    if not isinstance(raw, Mapping) or not raw or not admitted("fault_log", raw):
+        return Log(now_s)
+    episodes = [list(row) for row in raw.get("episodes") or () if len(row) == 4][-EPISODES_MAX:]
+    opened = raw.get("open")
+    return Log(
+        since_s=int(raw.get("since_s", now_s)),
+        source=raw.get("source"),
+        episodes=episodes,
+        dropped=int(raw.get("dropped", 0)),
+        open=list(opened) if isinstance(opened, list) and len(opened) == 2 else None,
+        codes={k: list(v) for k, v in (raw.get("codes") or {}).items() if len(v) == 3},
+    )
+
+
+def sources(config: EntryConfig) -> tuple[str, list[str]] | None:
+    """``("text", members)`` or ``("flag", [slot])`` from the entry's config, else ``None``."""
+    members = list(config.heat_pump_fault_text_entities)
+    if members:
+        return ("text", members[:FAULT_TEXT_ENTITIES_MAX])
+    flag = config.heat_pump_fault_entity
+    return ("flag", [flag]) if flag else None
+
+
+@dataclass
+class _Record:
+    hass: HomeAssistant
+    store: QuarantiningStore[dict[str, Any]]
+    kind: str
+    entities: list[str]
+    log: Log
+    #: Each text member's last readable state; an unavailable one keeps it.
+    last: dict[str, str] = field(default_factory=dict)
+    #: True until the first reading after load decides the restored open row.
+    fresh: bool = True
+    closed: bool = False
+    #: What release cancels: the state listener.
+    releases: list[Callable[[], None]] = field(default_factory=list)
+    timer: Callable[[], None] | None = None
+    saved_at: float | None = None
+    #: The save a failed setup's on_unload callback leaves running.
+    ending: Awaitable[None] | None = None
+
+
+_RECORDS: WeakKeyDictionary[Any, _Record] = WeakKeyDictionary()
+
+
+def _now_s() -> int:
+    return int(datetime.now(timezone.utc).timestamp())
+
+
+def _seconds(state: Any) -> int:
+    """When ``state`` last changed, in epoch seconds; now where it carries no stamp."""
+    stamp = getattr(state, "last_changed", None)
+    return int(stamp.timestamp()) if isinstance(stamp, datetime) else _now_s()
+
+
+def _reading(rec: _Record, entity_id: str, state: Any) -> tuple[bool, str | None]:
+    """``(readable, text)`` after ``entity_id`` reads ``state``."""
+    raw = getattr(state, "state", None)
+    if not isinstance(raw, str) or raw.strip().lower() in _UNREAD:
+        return (False, None)
+    if rec.kind == "text":
+        rec.last[entity_id] = raw
+        rec.log.source = "text"
+        return (True, code_text([rec.last.get(e) for e in rec.entities]))
+    read = flag_text(entity_id, raw)
+    if read is None:
+        return (False, None)
+    rec.log.source = read[0]
+    return (True, read[1])
+
+
+def _apply(rec: _Record, changes: Sequence[tuple[str, Any]]) -> None:
+    """Note what ``changes`` leave the source reading, stamped by the latest of them.
+
+    Setup hands every member at once, so a restored open row is decided on the
+    whole slot, never on its first member alone.
+    """
+    read = [(_seconds(state), text) for entity_id, state in changes
+            for ok, text in [_reading(rec, entity_id, state)] if ok]
+    if not read:
+        return
+    late, rec.fresh = rec.fresh, False
+    if note(rec.log, max(s for s, _t in read), read[-1][1], late=late):
+        _request_save(rec)
+
+
+def _request_save(rec: _Record) -> None:
+    """Save now, or once the window since the last save has passed."""
+    if rec.closed or rec.timer is not None:
+        return
+    wait = 0.0 if rec.saved_at is None else rec.saved_at + SAVE_MIN_S - time.monotonic()
+    if wait <= 0:
+        rec.hass.async_create_task(_save(rec))
+        return
+
+    @callback
+    def _due(_now: Any) -> None:
+        rec.timer = None
+        rec.hass.async_create_task(_save(rec))
+
+    rec.timer = async_call_later(rec.hass, wait, _due)
+
+
+async def _save(rec: _Record) -> None:
+    rec.saved_at = time.monotonic()
+    try:
+        await rec.store.async_save(stored(rec.log))
+    except Exception as err:  # noqa: BLE001 - the next open or close saves again
+        _LOGGER.debug("Could not save the fault record: %s", err)
+
+
+async def async_setup(hass: HomeAssistant, entry: Any, config: EntryConfig) -> None:
+    """Build the entry's record afresh, load it, read once, subscribe, hook the stop."""
+    old = _RECORDS.pop(entry, None)
+    if old is not None and old.ending is not None:
+        await old.ending  # the previous record's last save lands before this load
+    source = sources(config)
+    if source is None:
+        return
+    kind, entities = source
+    store: QuarantiningStore[dict[str, Any]] = QuarantiningStore(
+        hass, FAULT_LOG_STORE_VERSION, f"{DOMAIN}_{entry.entry_id}_fault_log")
+    raw = await load_mapping(store, "the fault record")
+    rec = _RECORDS[entry] = _Record(
+        hass, store, kind, entities, loaded(raw, _now_s()))
+    _apply(rec, [(e, s) for e in entities if (s := hass.states.get(e)) is not None])
+
+    @callback
+    def _changed(event: Any) -> None:
+        if not rec.closed:
+            _apply(rec, [(event.data.get("entity_id"), event.data.get("new_state"))])
+
+    rec.releases.append(async_track_state_change_event(hass, entities, _changed))
+
+    async def _stop(_event: Any) -> None:
+        await async_close(entry)
+
+    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _stop))
+
+    @callback
+    def _ended() -> None:
+        """A setup that fails after this one runs only these callbacks, never the unload."""
+        if _release(rec):
+            rec.ending = hass.async_create_task(_save(rec))
+
+    entry.async_on_unload(_ended)
+
+
+def _release(rec: _Record) -> bool:
+    """Unsubscribe and cancel the deferred save, once: whether this call did it."""
+    if rec.closed:
+        return False
+    rec.closed = True
+    for release in (*rec.releases, rec.timer):
+        if release is not None:
+            release()
+    return True
+
+
+async def async_close(entry: Any) -> None:
+    """Unsubscribe, cancel the deferred save, then save; a second call does nothing."""
+    rec = _RECORDS.get(entry)
+    if rec is not None and _release(rec):
+        await _save(rec)
+
+
+def _iso(seconds: int) -> str:
+    return datetime.fromtimestamp(seconds, timezone.utc).isoformat()
+
+
+def diagnostics_view(entry: Any) -> dict[str, Any] | None:
+    """The download's section: ``None`` with no source configured."""
+    rec = _RECORDS.get(entry)
+    if rec is None:
+        return None
+    log = rec.log
+    now_s = _now_s()
+    return {
+        "source": log.source,
+        "entities": list(rec.entities),
+        "open": None if log.open is None else {
+            "start": _iso(log.open[0]), "seconds": max(0, now_s - log.open[0]),
+            "code": log.open[1] or None},
+        "episodes": [
+            {"start": _iso(s), "end": _iso(e), "seconds": e - s, "code": t or None, "late": late}
+            for s, e, t, late in log.episodes
+        ],
+        "dropped": log.dropped,
+        "codes": {k: {"count": n, "seconds": total, "last_end": _iso(end)} for k, (n, total, end) in log.codes.items()},
+        "since": _iso(log.since_s),
+    }
diff --git a/custom_components/heatpump_optimizer/modbus_prefill.py b/custom_components/heatpump_optimizer/modbus_prefill.py
index 9b85c79519..be64493bbc 100644
--- a/custom_components/heatpump_optimizer/modbus_prefill.py
+++ b/custom_components/heatpump_optimizer/modbus_prefill.py
@@ -55,6 +55,8 @@ from .const import (
     CONF_DHW_WINDOWS,
     CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY,
     CONF_HEAT_PUMP_COP_NOMINAL,
+    CONF_HEAT_PUMP_FAULT_ENTITY,
+    CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES,
     CONF_HEAT_PUMP_MAX_POWER,
     CONF_HEAT_PUMP_RETURN_TEMP_ENTITY,
     CONF_HEAT_PUMP_SUPPLY_TEMP_ENTITY,
@@ -100,6 +102,8 @@ _NAMED = {
     CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: (
         "binary_sensor.{p}_night_mode_frequency_reduction_active"
     ),
+    # "HP Alarm": an OR over the four alarm registers, warnings included.
+    CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.{p}_alarm",
 }
 
 #: Day bitmaps put Monday on bit 7 and Sunday on bit 1; bit 0 is no day.
@@ -266,6 +270,12 @@ def infer(
     for slot in _NAMED:
         if slot in snap and slot != "unit_capacity" and not current.get(slot):
             suggestions[slot] = snap[slot][0]
+    # The one list slot, suggested as a one-member list while empty. Only a
+    # device table fills it; the GCHV package's four alarm-text sensors are the
+    # person's to pick (docs/configuration.md).
+    listed = snap.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES)
+    if listed is not None and not current.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES):
+        suggestions |= {CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: [listed[0]]}
     return suggestions
 
 
diff --git a/custom_components/heatpump_optimizer/store.py b/custom_components/heatpump_optimizer/store.py
index a3ed10d0c4..255ed6263b 100644
--- a/custom_components/heatpump_optimizer/store.py
+++ b/custom_components/heatpump_optimizer/store.py
@@ -572,6 +572,19 @@ DOMAINS: dict[str, dict[str, Domain | str]] = {
         **{f"house/{f}": Domain("text", whole="a bad cell nulls the house columns")
            for f in ("outdoor", "return", "power", "space")},
     },
+    # fault_log.py: closed rows [start_s, end_s, code, late], the open row
+    # [start_s, code] and the per-code tally [count, total_s, last_end_s].
+    "fault_log": {
+        path: domain._replace(whole="fault_log.loaded starts the record afresh on any field outside this")
+        for path, domain in {
+            "since_s": _COUNT, "dropped": _COUNT,
+            "source": Domain("choice", null=True, choices=("text", "bitmap", "flag")),
+            "episodes/#/0": _COUNT, "episodes/#/1": _COUNT, "episodes/#/2": Domain("text", null=True),
+            "episodes/#/3": _FLAG,
+            "open": _ABSENT, "open/0": _COUNT, "open/1": Domain("text", null=True),
+            "codes/~": _TEXT, **{f"codes/*/{i}": _COUNT for i in range(3)},
+        }.items()
+    },
     "manual_plan": {
         **{f"{k}_slots": _ABSENT for k in ("space", "dhw")},
         **{f"{k}_slots/#/{e}": _AT for k in ("space", "dhw") for e in ("start", "end")},
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 3a9dc14f72..f716ae8943 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -230,7 +230,7 @@
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
-          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself."
+          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. The optimizer pauses its learning while it is on. Without a Fault text entity, each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex."
         },
         "sections": {
           "indoor": {
@@ -275,7 +275,7 @@
               "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
               "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
               "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
-              "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
+              "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. The optimizer pauses its learning while it is on. Without a Fault text entity, each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex.",
               "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
               "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
               "heat_pump_switch_entity": "Optional. A switch used to turn the heat pump off during expensive hours.",
@@ -351,7 +351,9 @@
           "dhw_temp_entity": "Hot water tank temperature sensor",
           "heat_pump_supply_temp_entity": "Supply (flow) water temperature",
           "heat_pump_return_temp_entity": "Return water temperature",
-          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)"
+          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
+          "heat_pump_fault_entity": "Fault alarm",
+          "heat_pump_fault_text_entities": "Fault text"
         },
         "data_description": {
           "prefill_device": "The pump's own device. Its entities are mapped to settings by that integration's published definitions, or by their names where nothing is published - not from a reading of your unit - so check the suggestions before keeping them. Leave it empty to continue setup without the pre-fill.",
@@ -370,7 +372,9 @@
           "dhw_temp_entity": "The heat pump's hot water tank temperature sensor, suggested only while this slot is empty.",
           "heat_pump_supply_temp_entity": "The heat pump's leaving water temperature (T1) sensor, suggested only while this slot is empty.",
           "heat_pump_return_temp_entity": "The heat pump's entering water temperature (Tw-in) sensor, suggested only while this slot is empty.",
-          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty."
+          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty.",
+          "heat_pump_fault_entity": "The pump's fault alarm (the Tuya integration's Fault Alarm, the GCHV package's HP Alarm), suggested only while this slot is empty. Keeping it pauses the optimizer's learning while the pump reports a fault, and discards a duty-switch measurement with a fault in it. The GCHV alarm registers also report non-blocking warnings, which read as a fault here too.",
+          "heat_pump_fault_text_entities": "The pump's fault description sensor (the Tuya integration's Fault Description), suggested only while this slot is empty. Each fault's codes, start and end are then kept for Download diagnostics."
         }
       }
     },
@@ -1291,6 +1295,7 @@
           "heat_pump_defrost_entity": "Defrosting",
           "heat_pump_online_entity": "Pump online",
           "heat_pump_fault_entity": "Fault alarm",
+          "heat_pump_fault_text_entities": "Fault text",
           "heat_pump_backup_heater_entity": "Space backup heater",
           "heat_pump_dhw_booster_entity": "Hot water tank booster",
           "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
@@ -1305,7 +1310,8 @@
           "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
-          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
+          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. The optimizer pauses its learning while it is on. Without a Fault text entity, each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex.",
+          "heat_pump_fault_text_entities": "Optional. Up to 4 entities whose state is the pump's fault description: OK, or a comma list of codes such as \"E5, P3\" - the Tuya integration's Fault Description, or the GCHV Modbus package's four HP Alarm bitmap sensors. Each fault's codes, start and end are kept for the last 200 faults and appear in Download diagnostics. Any text other than OK, normal or an idle word is recorded as a code, whatever the entity is, so pick a fault description rather than a status sensor.",
           "heat_pump_backup_heater_entity": "Optional. On while the pump's own electric backup heater is running in the space heating circuit. Resistive kilowatts on the meter are not the compressor being inefficient, so while this is on the optimizer stops reading the meter as an efficiency measurement. The heat still counts: it is real heat into the house, and the house learners keep running. Useful mainly if your pump publishes no power meter, where there is otherwise no way to notice the element at all.",
           "heat_pump_dhw_booster_entity": "Optional. On while the electric heater in the hot water tank is running. Treated the same way as the backup heater above, and each time it switches on it is also recorded as a hot water rescue - if those keep recurring, and you have turned on the immersion feedback option, the plan starts heating the tank a little earlier instead of paying resistive prices for the difference.",
           "heat_pump_capacity_limited_entity": "Optional. On while the pump is running at a reduced compressor speed, which most units call night mode or silent mode. What the pump draws and delivers then is not what it would do unconstrained, so the optimizer stops learning efficiency and capacity from those intervals. It keeps using the measured power for cost and heat accounting, because a speed-capped compressor still draws exactly what the meter says.",
@@ -1566,6 +1572,8 @@
           "heat_pump_return_temp_entity": "Return water temperature",
           "compressor_freq_sensor": "Actual frequency sensor (recommended for control)",
           "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
+          "heat_pump_fault_entity": "Fault alarm",
+          "heat_pump_fault_text_entities": "Fault text",
           "after_save": "After saving",
           "prefill_offer": "Offer this pre-fill at setup"
         },
@@ -1588,6 +1596,8 @@
           "heat_pump_return_temp_entity": "The package's entering water temperature (Tw-in) sensor, suggested only while this slot is empty.",
           "compressor_freq_sensor": "The package's actual compressor frequency sensor, suggested only while this slot is empty.",
           "heat_pump_capacity_limited_entity": "The package's night mode (frequency reduction) active sensor, suggested only while this slot is empty.",
+          "heat_pump_fault_entity": "The pump's fault alarm (the Tuya integration's Fault Alarm, the GCHV package's HP Alarm), suggested only while this slot is empty. Keeping it pauses the optimizer's learning while the pump reports a fault, and discards a duty-switch measurement with a fault in it. The GCHV alarm registers also report non-blocking warnings, which read as a fault here too.",
+          "heat_pump_fault_text_entities": "The pump's fault description sensor (the Tuya integration's Fault Description), suggested only while this slot is empty. Each fault's codes, start and end are then kept for Download diagnostics.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next.",
           "prefill_offer": "When on, setting up a new entry offers this page if a heat-pump device added to this install can fill any of these settings. Off by default: the setup wizard is unchanged while it is off, and this switch is stored, so it survives a restart."
         }
@@ -1639,7 +1649,8 @@
       "heat_curve_unreadable": "That entity holds no reading now, so the value it would be returned to on off is unknown. Choose an entity that reports a value, or save again once it does.",
       "heat_curve_out_of_range": "That entity reads a value outside its own declared range, so it cannot be displaced safely. Check the entity in its integration first.",
       "heat_curve_entity_in_use": "The heat-curve offset entity is already written by the optimizer for another purpose (a set-point, the valve, the compressor or the mode). Choose a different entity for one of them.",
-      "too_many_rooms": "At most 32 room thermometers can be listed."
+      "too_many_rooms": "At most 32 room thermometers can be listed.",
+      "too_many_fault_text_entities": "At most 4 fault text entities can be listed."
     },
     "abort": {
       "factory_reset_done": "Reset done. The integration has reloaded and is planning again. To undo the reset, run the Restore learned snapshot action.",
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index 741147c2f1..d9eb65bbaa 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -230,7 +230,7 @@
           "heat_pump_mode_entity": "Optional. Die eigene Betriebsartwahl der Pumpe – Kühlen, Heizen, Warmwasser oder eine Kombination aus zwei. Nur lesend, es sei denn, die Steuerung der Pumpenaufgabe ist auf „Steuern“ gesetzt. Eine Pumpe im Kühl- oder reinen Warmwasserbetrieb kann das Haus nicht heizen, und eine im reinen Heizbetrieb kann kein Warmwasser bereiten; ohne diese Angabe kann der Plan also Wärme versprechen, die die Pumpe gerade nicht liefern kann. Bleibt das Feld leer, geht der Optimierer davon aus, dass die Pumpe alles kann.",
           "heat_pump_defrost_entity": "Optional. Ein, solange die Pumpe den Kreislauf umkehrt, um Reif vom Außenregister zu schmelzen. Der während einer Abtauung eingekaufte Strom geht ins Register statt ins Haus. Beachte, dass viele Pumpen nur alle paar Minuten abgefragt werden, sodass kurze Abtauungen völlig übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
           "heat_pump_online_entity": "Optional, aber bei einer cloudverbundenen Pumpe dringend empfohlen. Ein, solange die Pumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre zuletzt bekannten Werte weiter veröffentlichen, obwohl die Pumpe selbst vom Netzwerk getrennt ist; dadurch wirken alle anderen Sensoren völlig aktuell, und dies ist das einzige Signal, das etwas anderes anzeigt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar und dies bringt wenig.",
-          "heat_pump_fault_entity": "Optional. Ein, solange die Pumpe eine Störung meldet. Verwendet wird nur, ob eine Störung vorliegt, nie der Code selbst."
+          "heat_pump_fault_entity": "Optional. Ein, solange die Wärmepumpe eine Störung meldet. Der Optimierer pausiert sein Lernen, solange sie ein ist. Ohne eine Störungstext-Entität werden Beginn und Ende jeder Störung für Diagnose herunterladen gespeichert, bei einem numerischen Wert mit dem Code in Hex."
         },
         "sections": {
           "indoor": {
@@ -275,7 +275,7 @@
               "dhw_temp_entity": "Optional, aber empfohlen. Die tatsächliche Speichertemperatur. Ermöglicht außerdem, dass ein manueller Warmwasser-Boost den Legionellen-Timer zurücksetzt.",
               "floor_return_temp_entity": "Optional. Ein Sensor im Fußbodenkreis selbst: das Wasser, das aus den Fußbodenkreisen zurückkommt, nach Pufferspeicher oder Mischventil. Damit wird geschätzt, wie viel Wärme der Estrich hält. Nicht den Rücklaufsensor der Wärmepumpe verwenden: Bei einer Anlage mit Pufferspeicher misst er den Kreis der Wärmepumpe, weit wärmer als der Boden, und der Plan hielte den Estrich für voll und plante keine Heizung. Ein Wert mehr als 12 K über dem Raum wird ignoriert und meldet einen Reparaturhinweis. Leer lassen, wenn es keinen Sensor im Fußbodenkreis gibt.",
               "heat_pump_defrost_entity": "Optional. Ein, solange die Pumpe den Kreislauf umkehrt, um Reif vom Außenregister zu schmelzen. Der während einer Abtauung eingekaufte Strom geht ins Register statt ins Haus. Beachte, dass viele Pumpen nur alle paar Minuten abgefragt werden, sodass kurze Abtauungen völlig übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
-              "heat_pump_fault_entity": "Optional. Ein, solange die Pumpe eine Störung meldet. Verwendet wird nur, ob eine Störung vorliegt, nie der Code selbst.",
+              "heat_pump_fault_entity": "Optional. Ein, solange die Wärmepumpe eine Störung meldet. Der Optimierer pausiert sein Lernen, solange sie ein ist. Ohne eine Störungstext-Entität werden Beginn und Ende jeder Störung für Diagnose herunterladen gespeichert, bei einem numerischen Wert mit dem Code in Hex.",
               "heat_pump_mode_entity": "Optional. Die eigene Betriebsartwahl der Pumpe – Kühlen, Heizen, Warmwasser oder eine Kombination aus zwei. Nur lesend, es sei denn, die Steuerung der Pumpenaufgabe ist auf „Steuern“ gesetzt. Eine Pumpe im Kühl- oder reinen Warmwasserbetrieb kann das Haus nicht heizen, und eine im reinen Heizbetrieb kann kein Warmwasser bereiten; ohne diese Angabe kann der Plan also Wärme versprechen, die die Pumpe gerade nicht liefern kann. Bleibt das Feld leer, geht der Optimierer davon aus, dass die Pumpe alles kann.",
               "heat_pump_online_entity": "Optional, aber bei einer cloudverbundenen Pumpe dringend empfohlen. Ein, solange die Pumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre zuletzt bekannten Werte weiter veröffentlichen, obwohl die Pumpe selbst vom Netzwerk getrennt ist; dadurch wirken alle anderen Sensoren völlig aktuell, und dies ist das einzige Signal, das etwas anderes anzeigt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar und dies bringt wenig.",
               "heat_pump_switch_entity": "Optional. Ein Schalter, mit dem die Wärmepumpe in teuren Stunden ausgeschaltet wird.",
@@ -351,7 +351,9 @@
           "dhw_temp_entity": "Temperatursensor Warmwasserspeicher",
           "heat_pump_supply_temp_entity": "Vorlauftemperatur",
           "heat_pump_return_temp_entity": "Rücklauftemperatur",
-          "heat_pump_capacity_limited_entity": "Leistung begrenzt (Nachtmodus)"
+          "heat_pump_capacity_limited_entity": "Leistung begrenzt (Nachtmodus)",
+          "heat_pump_fault_entity": "Störungsmeldung",
+          "heat_pump_fault_text_entities": "Störungstext"
         },
         "data_description": {
           "prefill_device": "Das eigene Gerät der Pumpe. Seine Entitäten werden anhand der veröffentlichten Definitionen dieser Integration oder, wo nichts veröffentlicht ist, anhand ihrer Namen den Einstellungen zugeordnet – nicht aus einer Auslesung deines Geräts –, prüfe die Vorschläge daher, bevor du sie übernimmst. Lass es leer, um die Einrichtung ohne Vorausfüllung fortzusetzen.",
@@ -370,7 +372,9 @@
           "dhw_temp_entity": "Der Temperatursensor des Warmwasserspeichers der Wärmepumpe, wird nur vorgeschlagen, solange dieser Platz leer ist.",
           "heat_pump_supply_temp_entity": "Der Sensor für die Austrittswassertemperatur (T1) der Wärmepumpe, wird nur vorgeschlagen, solange dieser Platz leer ist.",
           "heat_pump_return_temp_entity": "Der Sensor für die Eintrittswassertemperatur (Tw-in) der Wärmepumpe, wird nur vorgeschlagen, solange dieser Platz leer ist.",
-          "heat_pump_capacity_limited_entity": "Der Sensor der Wärmepumpe für aktiven Nachtmodus (Frequenzreduzierung), wird nur vorgeschlagen, solange dieser Platz leer ist."
+          "heat_pump_capacity_limited_entity": "Der Sensor der Wärmepumpe für aktiven Nachtmodus (Frequenzreduzierung), wird nur vorgeschlagen, solange dieser Platz leer ist.",
+          "heat_pump_fault_entity": "Die Störungsmeldung der Wärmepumpe (Fault Alarm der Tuya-Integration, HP Alarm des GCHV-Pakets), nur vorgeschlagen, solange dieser Platz leer ist. Wird sie übernommen, pausiert der Optimierer sein Lernen, solange die Wärmepumpe eine Störung meldet, und verwirft eine Messung des Betriebswechsels mit einer Störung darin. Die GCHV-Alarmregister melden auch nicht blockierende Warnungen, die hier ebenfalls als Störung gelten.",
+          "heat_pump_fault_text_entities": "Der Störungsbeschreibungs-Sensor der Wärmepumpe (Fault Description der Tuya-Integration), nur vorgeschlagen, solange dieser Platz leer ist. Codes, Beginn und Ende jeder Störung werden dann für Diagnose herunterladen gespeichert."
         }
       }
     },
@@ -1291,6 +1295,7 @@
           "heat_pump_defrost_entity": "Abtauen",
           "heat_pump_online_entity": "Pumpe online",
           "heat_pump_fault_entity": "Störungsmeldung",
+          "heat_pump_fault_text_entities": "Störungstext",
           "heat_pump_backup_heater_entity": "Zuheizer für Raumheizung",
           "heat_pump_dhw_booster_entity": "Heizstab im Warmwasserspeicher",
           "heat_pump_capacity_limited_entity": "Leistung begrenzt (Nachtmodus)",
@@ -1305,7 +1310,8 @@
           "dhw_hysteresis_entity": "Optional. Ein Sensor oder eine Zahl mit der eigenen Starthysterese der Pumpe für Warmwasser als Temperaturdifferenz in K (°C gilt unverändert, °F wird umgerechnet; 0 bis 20 K): Die Pumpe startet eine Ladung erst, wenn der Speicher unter dem Warmwasser-Sollwert minus diesem Wert liegt. Der Plan setzt dann keine Ladung auf einen wärmeren Speicher (eine für den aktuellen Schritt geplante Ladung bleibt, da sie schon laufen kann; eine Desinfektionsladung wird an der Desinfektionstemperatur gemessen), und das Funktionsprotokoll markiert einen Warmwasser-Leerlaufschritt auf so einem Speicher als not-startable statt idle-instead. Ein Warmwasser-Minimum über dieser Starttemperatur kann die Pumpe nicht halten und löst eine Warnung aus. Bleibt sie leer, unlesbar oder 0, gilt jede geplante Ladung als startend.",
           "heat_pump_defrost_entity": "Optional. Ein, solange die Wärmepumpe den Kreislauf umkehrt, um Frost vom Außenwärmetauscher zu schmelzen. Der während einer Abtauung bezogene Strom geht in den Wärmetauscher statt ins Haus. Beachte, dass viele Wärmepumpen nur alle paar Minuten abgefragt werden, kurze Abtauvorgänge also komplett übersehen werden: Dies ist eine Stichprobe der Abtauaktivität, keine Stoppuhr.",
           "heat_pump_online_entity": "Optional und bei einer cloudverbundenen Wärmepumpe dringend empfohlen. Ein, solange die Wärmepumpe tatsächlich erreichbar ist. Eine Cloud-Integration kann ihre letzten bekannten Werte weiter veröffentlichen, obwohl die Wärmepumpe selbst vom Netzwerk getrennt ist, sodass alle anderen Sensoren völlig aktuell aussehen; dies ist das einzige Signal, das etwas anderes sagt. Bei einer lokalen Verbindung (LAN) werden die Sensoren von selbst nicht verfügbar, und dies bringt wenig.",
-          "heat_pump_fault_entity": "Optional. Ein, solange die Wärmepumpe eine Störung meldet. Verwendet wird nur, ob eine Störung vorliegt, nie der Code selbst.",
+          "heat_pump_fault_entity": "Optional. Ein, solange die Wärmepumpe eine Störung meldet. Der Optimierer pausiert sein Lernen, solange sie ein ist. Ohne eine Störungstext-Entität werden Beginn und Ende jeder Störung für Diagnose herunterladen gespeichert, bei einem numerischen Wert mit dem Code in Hex.",
+          "heat_pump_fault_text_entities": "Optional. Bis zu 4 Entitäten, deren Zustand die Störungsbeschreibung der Wärmepumpe ist: OK oder eine kommagetrennte Liste von Codes wie \"E5, P3\" - die Fault Description der Tuya-Integration oder die vier HP Alarm bitmap-Sensoren des GCHV-Modbus-Pakets. Codes, Beginn und Ende jeder Störung werden für die letzten 200 Störungen gespeichert und erscheinen in Diagnose herunterladen. Jeder andere Text als OK, normal oder ein Ruhe-Wort wird als Code gespeichert, gleich welche Entität es ist, daher eine Störungsbeschreibung wählen und keinen Statussensor.",
           "heat_pump_backup_heater_entity": "Optional. Ein, solange der eigene elektrische Zuheizer der Wärmepumpe im Raumheizkreis läuft. Resistive Kilowatt am Zähler bedeuten nicht, dass der Verdichter ineffizient ist; solange dies eingeschaltet ist, wertet der Optimierer den Zähler daher nicht als Effizienzmessung. Die Wärme zählt weiterhin: Sie ist echte Wärme im Haus, und die Hauslernmodelle laufen weiter. Vor allem nützlich, wenn deine Wärmepumpe keinen Leistungsmesser veröffentlicht, da es sonst keine Möglichkeit gibt, das Heizelement überhaupt zu bemerken.",
           "heat_pump_dhw_booster_entity": "Optional. Ein, solange der elektrische Heizstab im Warmwasserspeicher läuft. Wird wie der Zuheizer oben behandelt, und jedes Einschalten wird zusätzlich als Warmwasser-Notfall erfasst – wiederholt sich das und du hast die Option für die Heizstab-Rückmeldung eingeschaltet, beginnt der Plan, den Speicher etwas früher zu heizen, statt für die Differenz resistive Preise zu zahlen.",
           "heat_pump_capacity_limited_entity": "Optional. Ein, solange die Wärmepumpe mit reduzierter Verdichterdrehzahl läuft, was die meisten Geräte Nachtmodus oder Flüstermodus nennen. Was die Wärmepumpe dann aufnimmt und abgibt, entspricht nicht ihrem uneingeschränkten Verhalten, daher lernt der Optimierer aus diesen Intervallen weder Effizienz noch Leistung. Für Kosten und Wärmebilanz verwendet er weiterhin die gemessene Leistung, denn ein drehzahlbegrenzter Verdichter nimmt genau das auf, was der Zähler anzeigt.",
@@ -1566,6 +1572,8 @@
           "heat_pump_return_temp_entity": "Rücklauftemperatur",
           "compressor_freq_sensor": "Sensor der Ist-Frequenz (für die Steuerung empfohlen)",
           "heat_pump_capacity_limited_entity": "Leistung begrenzt (Nachtmodus)",
+          "heat_pump_fault_entity": "Störungsmeldung",
+          "heat_pump_fault_text_entities": "Störungstext",
           "after_save": "Nach dem Speichern",
           "prefill_offer": "Diese Vorbefüllung bei der Einrichtung anbieten"
         },
@@ -1588,6 +1596,8 @@
           "heat_pump_return_temp_entity": "Der Sensor für die Eintrittswassertemperatur (Tw-in) des Pakets, nur vorgeschlagen, solange dieser Platz leer ist.",
           "compressor_freq_sensor": "Der Sensor für die tatsächliche Verdichterfrequenz des Pakets, nur vorgeschlagen, solange dieser Platz leer ist.",
           "heat_pump_capacity_limited_entity": "Der Sensor des Pakets für aktiven Nachtmodus (Frequenzreduzierung), nur vorgeschlagen, solange dieser Platz leer ist.",
+          "heat_pump_fault_entity": "Die Störungsmeldung der Wärmepumpe (Fault Alarm der Tuya-Integration, HP Alarm des GCHV-Pakets), nur vorgeschlagen, solange dieser Platz leer ist. Wird sie übernommen, pausiert der Optimierer sein Lernen, solange die Wärmepumpe eine Störung meldet, und verwirft eine Messung des Betriebswechsels mit einer Störung darin. Die GCHV-Alarmregister melden auch nicht blockierende Warnungen, die hier ebenfalls als Störung gelten.",
+          "heat_pump_fault_text_entities": "Der Störungsbeschreibungs-Sensor der Wärmepumpe (Fault Description der Tuya-Integration), nur vorgeschlagen, solange dieser Platz leer ist. Codes, Beginn und Ende jeder Störung werden dann für Diagnose herunterladen gespeichert.",
           "after_save": "Das Speichern wirkt sofort; hier legst du fest, wohin der Dialog als Nächstes führt.",
           "prefill_offer": "Wenn aktiviert, bietet das Einrichten eines neuen Eintrags diese Seite an, falls ein zu dieser Installation hinzugefügtes Wärmepumpen-Gerät eine dieser Einstellungen füllen kann. Standardmäßig aus: Der Einrichtungsassistent bleibt unverändert, solange sie aus ist, und dieser Schalter wird gespeichert, übersteht also einen Neustart."
         }
@@ -1639,7 +1649,8 @@
       "heat_curve_unreadable": "Diese Entität hat gerade keinen Wert, daher ist unbekannt, auf welchen Wert sie beim Ausschalten zurückgesetzt würde. Wähle eine Entität, die einen Wert meldet, oder speichere erneut, sobald sie es tut.",
       "heat_curve_out_of_range": "Diese Entität zeigt einen Wert außerhalb ihres eigenen angegebenen Bereichs, daher kann sie nicht sicher verschoben werden. Prüfe die Entität zuerst in ihrer Integration.",
       "heat_curve_entity_in_use": "Die Offset-Entität der Heizkurve wird vom Optimierer bereits für einen anderen Zweck geschrieben (einen Sollwert, das Ventil, den Verdichter oder den Modus). Wähle für einen davon eine andere Entität.",
-      "too_many_rooms": "Es können höchstens 32 Raumthermometer angegeben werden."
+      "too_many_rooms": "Es können höchstens 32 Raumthermometer angegeben werden.",
+      "too_many_fault_text_entities": "Es können höchstens 4 Störungstext-Entitäten angegeben werden."
     },
     "abort": {
       "factory_reset_done": "Zurücksetzen abgeschlossen. Die Integration wurde neu geladen und plant wieder. Um das Zurücksetzen rückgängig zu machen, führe die Aktion „Gelernte Momentaufnahme wiederherstellen“ aus.",
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 3a9dc14f72..f716ae8943 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -230,7 +230,7 @@
           "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
-          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself."
+          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. The optimizer pauses its learning while it is on. Without a Fault text entity, each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex."
         },
         "sections": {
           "indoor": {
@@ -275,7 +275,7 @@
               "dhw_temp_entity": "Optional but recommended. The real tank temperature. Also lets a manual hot water boost reset the anti-legionella timer.",
               "floor_return_temp_entity": "Optional. A sensor in the floor loop itself: the water coming back from the floor loops, after any buffer tank or mixing valve. It gauges how much heat the slab is holding. Do not use the heat pump's own return sensor: on a plant with a buffer tank it reads the heat pump's circuit, far warmer than the floor, and the plan would believe the slab is already full and plan no heating. A reading more than 12 K above the room is ignored and raises a repair notice. Leave empty if there is no sensor in the floor loop.",
               "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
-              "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
+              "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. The optimizer pauses its learning while it is on. Without a Fault text entity, each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex.",
               "heat_pump_mode_entity": "Optional. The pump's own mode selector - cooling, heating, hot water, or a combination of two. Read only, unless Pump duty control is set to Control. A pump in a cooling or hot-water-only mode cannot heat the house, and one in a heating-only mode cannot make hot water, so without this the plan can promise heat the pump is not currently able to deliver. Left empty, the optimizer assumes the pump can do everything.",
               "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
               "heat_pump_switch_entity": "Optional. A switch used to turn the heat pump off during expensive hours.",
@@ -351,7 +351,9 @@
           "dhw_temp_entity": "Hot water tank temperature sensor",
           "heat_pump_supply_temp_entity": "Supply (flow) water temperature",
           "heat_pump_return_temp_entity": "Return water temperature",
-          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)"
+          "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
+          "heat_pump_fault_entity": "Fault alarm",
+          "heat_pump_fault_text_entities": "Fault text"
         },
         "data_description": {
           "prefill_device": "The pump's own device. Its entities are mapped to settings by that integration's published definitions, or by their names where nothing is published - not from a reading of your unit - so check the suggestions before keeping them. Leave it empty to continue setup without the pre-fill.",
@@ -370,7 +372,9 @@
           "dhw_temp_entity": "The heat pump's hot water tank temperature sensor, suggested only while this slot is empty.",
           "heat_pump_supply_temp_entity": "The heat pump's leaving water temperature (T1) sensor, suggested only while this slot is empty.",
           "heat_pump_return_temp_entity": "The heat pump's entering water temperature (Tw-in) sensor, suggested only while this slot is empty.",
-          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty."
+          "heat_pump_capacity_limited_entity": "The heat pump's night mode (frequency reduction) active sensor, suggested only while this slot is empty.",
+          "heat_pump_fault_entity": "The pump's fault alarm (the Tuya integration's Fault Alarm, the GCHV package's HP Alarm), suggested only while this slot is empty. Keeping it pauses the optimizer's learning while the pump reports a fault, and discards a duty-switch measurement with a fault in it. The GCHV alarm registers also report non-blocking warnings, which read as a fault here too.",
+          "heat_pump_fault_text_entities": "The pump's fault description sensor (the Tuya integration's Fault Description), suggested only while this slot is empty. Each fault's codes, start and end are then kept for Download diagnostics."
         }
       }
     },
@@ -1291,6 +1295,7 @@
           "heat_pump_defrost_entity": "Defrosting",
           "heat_pump_online_entity": "Pump online",
           "heat_pump_fault_entity": "Fault alarm",
+          "heat_pump_fault_text_entities": "Fault text",
           "heat_pump_backup_heater_entity": "Space backup heater",
           "heat_pump_dhw_booster_entity": "Hot water tank booster",
           "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
@@ -1305,7 +1310,8 @@
           "dhw_hysteresis_entity": "Optional. A sensor or number holding the pump's own hot water start hysteresis as a temperature difference in K (°C reads the same, °F is scaled; 0 to 20 K): the pump starts a charge only once the tank is below the hot water target minus this. The plan then places no charge on a tank warmer than that (a charge planned for the current step is kept, as it may already be running; a disinfection charge is judged against the disinfection temperature), and the duty ledger marks an idle hot water step on such a tank not-startable instead of idle-instead. A hot water minimum above that start temperature cannot be held by the pump and raises a warning. Left empty, unreadable or 0, every planned charge is taken to start.",
           "heat_pump_defrost_entity": "Optional. On while the pump reverses to melt frost off the outdoor coil. The electricity bought during a defrost goes into the coil rather than into the house. Note that many pumps are only polled every few minutes, so short defrosts are missed entirely: this is a sample of defrost activity, not a stopwatch.",
           "heat_pump_online_entity": "Optional, and strongly recommended for a cloud-connected pump. On while the pump is actually reachable. A cloud integration can keep republishing its last known readings while the pump itself has dropped off the network, which leaves every other sensor looking perfectly fresh; this is the one signal that says otherwise. On a local (LAN) connection the sensors go unavailable by themselves and this adds little.",
-          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself.",
+          "heat_pump_fault_entity": "Optional. On while the pump is reporting a fault. The optimizer pauses its learning while it is on. Without a Fault text entity, each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex.",
+          "heat_pump_fault_text_entities": "Optional. Up to 4 entities whose state is the pump's fault description: OK, or a comma list of codes such as \"E5, P3\" - the Tuya integration's Fault Description, or the GCHV Modbus package's four HP Alarm bitmap sensors. Each fault's codes, start and end are kept for the last 200 faults and appear in Download diagnostics. Any text other than OK, normal or an idle word is recorded as a code, whatever the entity is, so pick a fault description rather than a status sensor.",
           "heat_pump_backup_heater_entity": "Optional. On while the pump's own electric backup heater is running in the space heating circuit. Resistive kilowatts on the meter are not the compressor being inefficient, so while this is on the optimizer stops reading the meter as an efficiency measurement. The heat still counts: it is real heat into the house, and the house learners keep running. Useful mainly if your pump publishes no power meter, where there is otherwise no way to notice the element at all.",
           "heat_pump_dhw_booster_entity": "Optional. On while the electric heater in the hot water tank is running. Treated the same way as the backup heater above, and each time it switches on it is also recorded as a hot water rescue - if those keep recurring, and you have turned on the immersion feedback option, the plan starts heating the tank a little earlier instead of paying resistive prices for the difference.",
           "heat_pump_capacity_limited_entity": "Optional. On while the pump is running at a reduced compressor speed, which most units call night mode or silent mode. What the pump draws and delivers then is not what it would do unconstrained, so the optimizer stops learning efficiency and capacity from those intervals. It keeps using the measured power for cost and heat accounting, because a speed-capped compressor still draws exactly what the meter says.",
@@ -1566,6 +1572,8 @@
           "heat_pump_return_temp_entity": "Return water temperature",
           "compressor_freq_sensor": "Actual frequency sensor (recommended for control)",
           "heat_pump_capacity_limited_entity": "Capacity limited (night mode)",
+          "heat_pump_fault_entity": "Fault alarm",
+          "heat_pump_fault_text_entities": "Fault text",
           "after_save": "After saving",
           "prefill_offer": "Offer this pre-fill at setup"
         },
@@ -1588,6 +1596,8 @@
           "heat_pump_return_temp_entity": "The package's entering water temperature (Tw-in) sensor, suggested only while this slot is empty.",
           "compressor_freq_sensor": "The package's actual compressor frequency sensor, suggested only while this slot is empty.",
           "heat_pump_capacity_limited_entity": "The package's night mode (frequency reduction) active sensor, suggested only while this slot is empty.",
+          "heat_pump_fault_entity": "The pump's fault alarm (the Tuya integration's Fault Alarm, the GCHV package's HP Alarm), suggested only while this slot is empty. Keeping it pauses the optimizer's learning while the pump reports a fault, and discards a duty-switch measurement with a fault in it. The GCHV alarm registers also report non-blocking warnings, which read as a fault here too.",
+          "heat_pump_fault_text_entities": "The pump's fault description sensor (the Tuya integration's Fault Description), suggested only while this slot is empty. Each fault's codes, start and end are then kept for Download diagnostics.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next.",
           "prefill_offer": "When on, setting up a new entry offers this page if a heat-pump device added to this install can fill any of these settings. Off by default: the setup wizard is unchanged while it is off, and this switch is stored, so it survives a restart."
         }
@@ -1639,7 +1649,8 @@
       "heat_curve_unreadable": "That entity holds no reading now, so the value it would be returned to on off is unknown. Choose an entity that reports a value, or save again once it does.",
       "heat_curve_out_of_range": "That entity reads a value outside its own declared range, so it cannot be displaced safely. Check the entity in its integration first.",
       "heat_curve_entity_in_use": "The heat-curve offset entity is already written by the optimizer for another purpose (a set-point, the valve, the compressor or the mode). Choose a different entity for one of them.",
-      "too_many_rooms": "At most 32 room thermometers can be listed."
+      "too_many_rooms": "At most 32 room thermometers can be listed.",
+      "too_many_fault_text_entities": "At most 4 fault text entities can be listed."
     },
     "abort": {
       "factory_reset_done": "Reset done. The integration has reloaded and is planning again. To undo the reset, run the Restore learned snapshot action.",
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index cd218c75a5..dcbaffc658 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -230,7 +230,7 @@
           "heat_pump_mode_entity": "Valfritt. Pumpens eget lägesval - kyla, värme, varmvatten eller en kombination av två. Läses bara av, om inte Styrning av pumpens uppgift står på Styrning. En pump som står i kylläge eller enbart varmvatten kan inte värma huset, och en som står i enbart värmeläge kan inte göra varmvatten. Utan det här kan planen alltså lova värme som pumpen just då inte kan leverera. Lämnas fältet tomt antar optimeringen att pumpen klarar allt.",
           "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
           "heat_pump_online_entity": "Valfritt, men varmt rekommenderat för en molnansluten pump. På medan pumpen faktiskt går att nå. En molnintegration kan fortsätta publicera sina senast kända värden medan pumpen själv har tappat nätverket, vilket får alla andra givare att se alldeles färska ut. Det här är den enda signal som avslöjar det. Vid lokal anslutning (LAN) blir givarna otillgängliga av sig själva och fältet tillför då lite.",
-          "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Bara om det finns ett fel används, aldrig själva felkoden."
+          "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Optimeringen pausar sin inlärning medan den är på. Utan en feltextentitet sparas varje fels start och slut för Ladda ned diagnostik, med en numerisk avläsnings kod i hex."
         },
         "sections": {
           "indoor": {
@@ -275,7 +275,7 @@
               "dhw_temp_entity": "Valfritt men rekommenderas. Beredarens verkliga temperatur. Gör också att en manuell varmvattenkörning nollställer legionellatimern.",
               "floor_return_temp_entity": "Valfri. En givare i själva golvslingan: vattnet som kommer tillbaka från golvslingorna, efter ackumulatortank eller shuntventil. Den används för att uppskatta hur mycket värme plattan håller. Använd inte värmepumpens egen returgivare: i en anläggning med ackumulatortank mäter den värmepumpens krets, långt varmare än golvet, och planen skulle tro att plattan redan är full och inte planera någon värme. Ett värde mer än 12 K över rummet ignoreras och ger ett reparationsmeddelande. Lämna tomt om det inte finns någon givare i golvslingan.",
               "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
-              "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Bara om det finns ett fel används, aldrig själva felkoden.",
+              "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Optimeringen pausar sin inlärning medan den är på. Utan en feltextentitet sparas varje fels start och slut för Ladda ned diagnostik, med en numerisk avläsnings kod i hex.",
               "heat_pump_mode_entity": "Valfritt. Pumpens eget lägesval - kyla, värme, varmvatten eller en kombination av två. Läses bara av, om inte Styrning av pumpens uppgift står på Styrning. En pump som står i kylläge eller enbart varmvatten kan inte värma huset, och en som står i enbart värmeläge kan inte göra varmvatten. Utan det här kan planen alltså lova värme som pumpen just då inte kan leverera. Lämnas fältet tomt antar optimeringen att pumpen klarar allt.",
               "heat_pump_online_entity": "Valfritt, men varmt rekommenderat för en molnansluten pump. På medan pumpen faktiskt går att nå. En molnintegration kan fortsätta publicera sina senast kända värden medan pumpen själv har tappat nätverket, vilket får alla andra givare att se alldeles färska ut. Det här är den enda signal som avslöjar det. Vid lokal anslutning (LAN) blir givarna otillgängliga av sig själva och fältet tillför då lite.",
               "heat_pump_switch_entity": "Valfritt. En strömbrytare som används för att stänga av värmepumpen under dyra timmar.",
@@ -351,7 +351,9 @@
           "dhw_temp_entity": "Givare för varmvattenberedarens temperatur",
           "heat_pump_supply_temp_entity": "Framledningstemperatur",
           "heat_pump_return_temp_entity": "Returtemperatur",
-          "heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)"
+          "heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)",
+          "heat_pump_fault_entity": "Felindikering",
+          "heat_pump_fault_text_entities": "Feltext"
         },
         "data_description": {
           "prefill_device": "Pumpens egen enhet. Dess entiteter mappas till inställningar av integrationens publicerade definitioner, eller av deras namn där inget publiceras - inte från en avläsning av din enhet - så kontrollera förslagen innan du behåller dem. Lämna tomt för att fortsätta installationen utan förifyllningen.",
@@ -370,7 +372,9 @@
           "dhw_temp_entity": "Värmepumpens givare för varmvattenberedarens temperatur, föreslås bara medan fältet är tomt.",
           "heat_pump_supply_temp_entity": "Värmepumpens givare för utgående vattentemperatur (T1), föreslås bara medan fältet är tomt.",
           "heat_pump_return_temp_entity": "Värmepumpens givare för ingående vattentemperatur (Tw-in), föreslås bara medan fältet är tomt.",
-          "heat_pump_capacity_limited_entity": "Värmepumpens givare för aktivt nattläge (frekvensbegränsning), föreslås bara medan fältet är tomt."
+          "heat_pump_capacity_limited_entity": "Värmepumpens givare för aktivt nattläge (frekvensbegränsning), föreslås bara medan fältet är tomt.",
+          "heat_pump_fault_entity": "Pumpens fellarm (Tuya-integrationens Fault Alarm, GCHV-paketets HP Alarm), föreslås bara medan fältet är tomt. Behålls den pausar optimeringen sin inlärning medan pumpen larmar, och en mätning av driftbytet med ett fel i kasseras. GCHV-larmregistren rapporterar också icke-blockerande varningar, som läses som fel även här.",
+          "heat_pump_fault_text_entities": "Pumpens felbeskrivningsgivare (Tuya-integrationens Fault Description), föreslås bara medan fältet är tomt. Varje fels koder, start och slut sparas då för Ladda ned diagnostik."
         }
       }
     },
@@ -1291,6 +1295,7 @@
           "heat_pump_defrost_entity": "Avfrostning",
           "heat_pump_online_entity": "Pumpen är uppkopplad",
           "heat_pump_fault_entity": "Felindikering",
+          "heat_pump_fault_text_entities": "Feltext",
           "heat_pump_backup_heater_entity": "Elpatron för värme",
           "heat_pump_dhw_booster_entity": "Elpatron i varmvattenberedaren",
           "heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)",
@@ -1305,7 +1310,8 @@
           "dhw_hysteresis_entity": "Valfritt. En sensor eller ett tal med pumpens egen starthysteres för varmvatten som temperaturskillnad i K (°C läses likadant, °F räknas om; 0 till 20 K): pumpen startar en laddning först när tanken ligger under varmvattenbörvärdet minus detta. Planen lägger då ingen laddning på en varmare tank (en laddning som planerats för det aktuella steget behålls, eftersom den kan redan pågå; en desinfektionsladdning bedöms mot desinfektionstemperaturen), och pumploggen märker ett vilande varmvattensteg på en sådan tank not-startable i stället för idle-instead. Ett varmvattenminimum över den starttemperaturen kan pumpen inte hålla och ger en varning. Lämnas fältet tomt, oläsbart eller 0 antas varje planerad laddning starta.",
           "heat_pump_defrost_entity": "Valfritt. På medan pumpen vänder cykeln för att smälta bort frost från utomhusbatteriet. Elen som köps under en avfrostning går till batteriet i stället för in i huset. Tänk på att många pumpar bara avfrågas med några minuters mellanrum, så korta avfrostningar missas helt: det här är ett stickprov på avfrostning, inte ett tidtagarur.",
           "heat_pump_online_entity": "Valfritt, men varmt rekommenderat för en molnansluten pump. På medan pumpen faktiskt går att nå. En molnintegration kan fortsätta publicera sina senast kända värden medan pumpen själv har tappat nätverket, vilket får alla andra givare att se alldeles färska ut. Det här är den enda signal som avslöjar det. Vid lokal anslutning (LAN) blir givarna otillgängliga av sig själva och fältet tillför då lite.",
-          "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Bara om det finns ett fel används, aldrig själva felkoden.",
+          "heat_pump_fault_entity": "Valfritt. På medan pumpen larmar om ett fel. Optimeringen pausar sin inlärning medan den är på. Utan en feltextentitet sparas varje fels start och slut för Ladda ned diagnostik, med en numerisk avläsnings kod i hex.",
+          "heat_pump_fault_text_entities": "Valfritt. Upp till 4 entiteter vars tillstånd är pumpens felbeskrivning: OK, eller en kommaseparerad lista med koder som \"E5, P3\" - Tuya-integrationens Fault Description, eller GCHV-Modbuspaketets fyra HP Alarm bitmap-givare. Varje fels koder, start och slut sparas för de senaste 200 felen och visas i Ladda ned diagnostik. All annan text än OK, normal eller ett viloord sparas som en kod, vilken entitet det än är, så välj en felbeskrivning och inte en statusgivare.",
           "heat_pump_backup_heater_entity": "Valfritt. På medan pumpens egen elpatron går i värmekretsen. Resistiva kilowatt på mätaren betyder inte att kompressorn är ineffektiv, så medan detta är på slutar optimeringen läsa mätaren som ett mått på verkningsgrad. Värmen räknas fortfarande: det är verklig värme in i huset, och husets inlärning fortsätter. Framför allt användbart om din pump inte publicerar någon effektmätare alls, för då finns det annars inget sätt att märka patronen.",
           "heat_pump_dhw_booster_entity": "Valfritt. På medan elpatronen i varmvattenberedaren går. Hanteras på samma sätt som elpatronen för värme ovan, och varje gång den slår till noteras det dessutom som en varmvattenräddning - om de återkommer, och du har slagit på återkopplingen för elpatron, börjar planen värma beredaren något tidigare i stället för att betala resistiva priser för mellanskillnaden.",
           "heat_pump_capacity_limited_entity": "Valfritt. På medan pumpen går med sänkt kompressorvarvtal, vilket de flesta aggregat kallar nattläge eller tystläge. Vad pumpen drar och levererar då är inte vad den skulle göra obegränsad, så optimeringen slutar lära sig verkningsgrad och kapacitet av de intervallen. Den fortsätter använda den uppmätta effekten för kostnad och energiredovisning, eftersom en varvtalsbegränsad kompressor ändå drar exakt det mätaren säger.",
@@ -1566,6 +1572,8 @@
           "heat_pump_return_temp_entity": "Returtemperatur",
           "compressor_freq_sensor": "Sensor för faktisk frekvens (rekommenderas för styrning)",
           "heat_pump_capacity_limited_entity": "Begränsad effekt (nattläge)",
+          "heat_pump_fault_entity": "Felindikering",
+          "heat_pump_fault_text_entities": "Feltext",
           "after_save": "Efter sparande",
           "prefill_offer": "Erbjud förifyllningen vid installation"
         },
@@ -1588,6 +1596,8 @@
           "heat_pump_return_temp_entity": "Paketets givare för ingående vattentemperatur (Tw-in), föreslås bara medan fältet är tomt.",
           "compressor_freq_sensor": "Paketets givare för kompressorns faktiska frekvens, föreslås bara medan fältet är tomt.",
           "heat_pump_capacity_limited_entity": "Paketets givare för aktivt nattläge (frekvensbegränsning), föreslås bara medan fältet är tomt.",
+          "heat_pump_fault_entity": "Pumpens fellarm (Tuya-integrationens Fault Alarm, GCHV-paketets HP Alarm), föreslås bara medan fältet är tomt. Behålls den pausar optimeringen sin inlärning medan pumpen larmar, och en mätning av driftbytet med ett fel i kasseras. GCHV-larmregistren rapporterar också icke-blockerande varningar, som läses som fel även här.",
+          "heat_pump_fault_text_entities": "Pumpens felbeskrivningsgivare (Tuya-integrationens Fault Description), föreslås bara medan fältet är tomt. Varje fels koder, start och slut sparas då för Ladda ned diagnostik.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst.",
           "prefill_offer": "När det är på erbjuder en ny installation den här sidan om en värmepumpsenhet som lagts till i installationen kan fylla någon av de här inställningarna. Avstängt som standard: installationsguiden är oförändrad så länge det är av, och reglaget sparas, så det överlever en omstart."
         }
@@ -1639,7 +1649,8 @@
       "heat_curve_unreadable": "Den entiteten har inget värde just nu, så värdet den skulle återställas till vid avstängning är okänt. Välj en entitet som rapporterar ett värde, eller spara igen när den gör det.",
       "heat_curve_out_of_range": "Den entiteten visar ett värde utanför sitt eget angivna intervall, så den kan inte förskjutas säkert. Kontrollera entiteten i dess integration först.",
       "heat_curve_entity_in_use": "Entiteten för värmekurvans förskjutning skrivs redan av optimeraren för ett annat syfte (ett börvärde, ventilen, kompressorn eller driftläget). Välj en annan entitet för en av dem.",
-      "too_many_rooms": "Högst 32 rumstermometrar kan anges."
+      "too_many_rooms": "Högst 32 rumstermometrar kan anges.",
+      "too_many_fault_text_entities": "Högst 4 feltextentiteter kan anges."
     },
     "abort": {
       "factory_reset_done": "Återställningen är klar. Integrationen har laddats om och planerar igen. Kör åtgärden Återställ inlärd ögonblicksbild för att ångra återställningen.",
diff --git a/dev/audit/harnesses/r11_owner_fault_text.py b/dev/audit/harnesses/r11_owner_fault_text.py
new file mode 100644
index 0000000000..9cabb205a6
--- /dev/null
+++ b/dev/audit/harnesses/r11_owner_fault_text.py
@@ -0,0 +1,60 @@
+#!/usr/bin/env python3
+"""Counts from the pump's fault record in a downloaded diagnostics bundle (R11-OWNER-FAULT-TEXT).
+
+    python3 dev/audit/harnesses/r11_owner_fault_text.py BUNDLE.json
+
+Reads the download's ``coordinator.fault_log`` section (``fault_log.diagnostics_view``)
+and prints counts only, never a code or a time, so its output can be quoted from
+a private bundle: ``source``, ``episodes`` (closed rows kept), ``dropped``,
+``open`` (0 or 1), ``distinct_texts`` (tally keys, ``other`` included) and
+``late`` (rows closed at a restart's first read). A bundle from a release
+without the record, or an install with no fault source, prints
+``fault_log absent`` and exits 1. Exit 0 otherwise.
+
+The bundle is never committed; the owner runs this on one.
+
+Perturbation: delete one entry of the section's ``episodes`` list and the
+``episodes`` line prints one fewer.
+"""
+from __future__ import annotations
+
+import json
+import sys
+from typing import Any
+
+
+def section(bundle: Any) -> dict[str, Any] | None:
+    """The fault record's section, whether the bundle is wrapped in ``data`` or not."""
+    root = bundle.get("data", bundle) if isinstance(bundle, dict) else {}
+    view = (root.get("coordinator") or {}).get("fault_log") if isinstance(root, dict) else None
+    return view if isinstance(view, dict) else None
+
+
+def counts(view: dict[str, Any]) -> dict[str, Any]:
+    episodes = view.get("episodes") or []
+    return {
+        "source": view.get("source"),
+        "episodes": len(episodes),
+        "dropped": int(view.get("dropped") or 0),
+        "open": int(view.get("open") is not None),
+        "distinct_texts": len(view.get("codes") or {}),
+        "late": sum(1 for row in episodes if row.get("late")),
+    }
+
+
+def main(argv: list[str]) -> int:
+    if len(argv) != 1:
+        print(__doc__.strip().splitlines()[2].strip())
+        return 2
+    with open(argv[0], encoding="utf-8") as handle:
+        view = section(json.load(handle))
+    if view is None:
+        print("fault_log absent")
+        return 1
+    for key, value in counts(view).items():
+        print(f"{key}\t{value}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/audit/rounds/round3/D5/option_doc_coverage.py b/dev/audit/rounds/round3/D5/option_doc_coverage.py
index 156e408ff3..a6dc533532 100644
--- a/dev/audit/rounds/round3/D5/option_doc_coverage.py
+++ b/dev/audit/rounds/round3/D5/option_doc_coverage.py
@@ -105,9 +105,9 @@ EXPECTED on this tree (ae36eff printed option_fields_rendered=174 and
     is reached by a shell-out the closure recorder cannot see, so it does not
     go red on a pull request: it is re-measured in the commit that changes
     what the script prints, or main's forced-full run finds it):
-    RESULT option_fields_rendered=220 count   (219 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 218 until R11-OUTSIDE-ROOMS-P1's room list; 216 until the two start-hysteresis pickers; 211 until R10-COMBI-TANK's five combi fields; 208 until R10-GENERIC-HEAT-CURVE's three heat_curve fields)
+    RESULT option_fields_rendered=221 count   (220 until R11-OWNER-FAULT-TEXT's fault-text list; 219 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 218 until R11-OUTSIDE-ROOMS-P1's room list; 216 until the two start-hysteresis pickers; 211 until R10-COMBI-TANK's five combi fields; 208 until R10-GENERIC-HEAT-CURVE's three heat_curve fields)
     RESULT option_fields_undocumented=0 count
-    RESULT option_schema_keys_rendered=254 count   (253 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 252 until R11-OUTSIDE-ROOMS-P1's room list; 250 until the two start-hysteresis pickers; 244 until R10-COMBI-TANK; 241 until R10-GENERIC-HEAT-CURVE)
+    RESULT option_schema_keys_rendered=255 count   (254 until R11-OWNER-FAULT-TEXT's fault-text list; 253 until R11-OUTSIDE-ROOMS-P2's room lift toggle; 252 until R11-OUTSIDE-ROOMS-P1's room list; 250 until the two start-hysteresis pickers; 244 until R10-COMBI-TANK; 241 until R10-GENERIC-HEAT-CURVE)
     RESULT wood_economics_fields_rendered=4 count
     RESULT wood_economics_doc_lines=8 count      (tolerance: exact;
     moved 6 -> 8 by #1645/F8.1: the Services section's `simulate_plan`
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index 8ee864b00d..b89f3abcdd 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=104 measured=104",
+  "result": "documented=105 measured=105",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=104, listed=104, missing=[], phantom=[]",
+  "result": "on disk=105, listed=105, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
@@ -301,7 +301,7 @@
   "source": "docs/architecture.md:The Home Assistant boundary",
   "claim": "the boundary sentence's count of modules importing `homeassistant` at module level",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=36 measured=36",
+  "result": "documented=37 measured=37",
   "verdict": "true",
   "truth": ""
  },
@@ -310,7 +310,7 @@
   "source": "docs/architecture.md:The Home Assistant boundary",
   "claim": "the named modules are the complete set of module-level importers",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[]",
+  "result": "named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_log.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_log.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[]",
   "verdict": "true",
   "truth": "unnamed module-level importers: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 1c8141bbcc..a2b667a516 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,10 +35,10 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 25 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=25 measured=25 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=104 measured=104 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=104, listed=104, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
-| C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=36 measured=36 | **true** |  |
-| C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=105 measured=105 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=105, listed=105, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=37 measured=37 | **true** |  |
+| C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_log.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'circulation.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'fault_log.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'number_restore.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'room_record.py', 'running_signal.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
 | C37 | `docs/architecture.md:module map` | __init__.py -- the 15 services | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
 | C38 | `docs/architecture.md:module map` | services.yaml -- The 15 service definitions | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=15 measured=15 | **true** |  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index c900984b12..92b4b47b2c 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=104      (103 until R11-OUTSIDE-ROOMS-3B's comfort_floor.py; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=105      (104 until the merge joining R11-OWNER-FAULT-TEXT's fault_log.py and R11-OUTSIDE-ROOMS-3B's comfort_floor.py, 103 until either; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,13 +117,13 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=104           (103 until R11-OUTSIDE-ROOMS-3B's comfort_floor.py; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=105           (104 until the merge joining R11-OWNER-FAULT-TEXT's fault_log.py and R11-OUTSIDE-ROOMS-3B's comfort_floor.py, 103 until either; 102 until R11-OWNER-FLOWCAP's flow_limit.py; 101 until R11-SEAM-cycle-solve's solve_gate.py; 99 until R11-SEAM-actuation-release's duty_ledger.py and number_restore.py; 98 until R11-SEAM-actuation-release's circulation.py; 96 until R11-OUTSIDE-ROOMS-P3's room_history.py and room_record.py; 95 until R11-OUTSIDE-ROOMS-P1's rooms.py; 94 until R11-OUTSIDE-HONEST-STARTS-RUNS's runs.py; 93 until #3616's slab_seed.py; 92 until R10-START-COUNTER-EDGES's running_signal.py; 91 until R10-ADVISOR-STEADY-START's whatif.py; 90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
                                          architecture.md's module map)
     RESULT arch_map_missing=0            (was 11)
-    RESULT ha_module_level_importers=36  (35 until R11-SEAM-actuation-release's number_restore.py; 34 until its circulation.py; 33 until R11-OUTSIDE-ROOMS-P3's room_record.py; 32 until R10-START-COUNTER-EDGES's running_signal.py; 31 until the supply-hold PR's supply_hold.py; 30 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 28 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 27 until the live-fix wave's early_cutoff.py imports
+    RESULT ha_module_level_importers=37  (36 until R11-OWNER-FAULT-TEXT's fault_log.py; 35 until R11-SEAM-actuation-release's number_restore.py; 34 until its circulation.py; 33 until R11-OUTSIDE-ROOMS-P3's room_record.py; 32 until R10-START-COUNTER-EDGES's running_signal.py; 31 until the supply-hold PR's supply_hold.py; 30 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 28 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 27 until the live-fix wave's early_cutoff.py imports
                                          homeassistant.core at module level;
                                          26 until R9-DBG-1's debugger.py imports
                                          homeassistant.core at module level;
diff --git a/dev/programme/delivery/3870.md b/dev/programme/delivery/3870.md
new file mode 100644
index 0000000000..e8befefb57
--- /dev/null
+++ b/dev/programme/delivery/3870.md
@@ -0,0 +1 @@
+- [#3870](https://github.com/tvofi/heatpump_optimizer/pull/3870) — **open**, R11-OWNER-FAULT-TEXT: record the pump's fault codes with start and end and show them in Download diagnostics (R11-OWNER-FAULT-TEXT)
diff --git a/docs/architecture.md b/docs/architecture.md
index 55320afccc..1ab94f5ec5 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 104 modules, of which 36 import the
+knows nothing about Home Assistant: 105 modules, of which 37 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -142,6 +142,7 @@ custom_components/heatpump_optimizer/
 ├── inputs.py             # Guarded state reads with a staleness watchdog
 ├── room_history.py       # Room history: the half-hour ring, its store document and the per-room identifiability report
 ├── room_record.py        # One room-history ring per coordinator, its store, saved every 6 h and at unload
+├── fault_log.py          # The pump's fault record: each fault's code, start and end, its store, the diagnostics view
 ├── rooms.py              # The room thermometer list: its reading record, mean and spread
 │                         #   and the lift a cold room gives the planned comfort floor
 ├── issues.py             # The repair-notice writer: raise, clear, the docs link
@@ -297,11 +298,11 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-36 of the 104 modules import `homeassistant` at module level: `__init__`,
+37 of the 105 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `circulation`, `currency`, `debugger`, `defrost`,
-`dhw_learning`, `diagnostics`, `duty_switch`, `early_cutoff`, `entity`, `heat_curve`, `issues`, `legionella`, `notifier`, `number_restore`, `off_restore`, `pump_arbiter`, `repairs`, `room_record`, `running_signal`, `services`,
+`dhw_learning`, `diagnostics`, `duty_switch`, `early_cutoff`, `entity`, `fault_log`, `heat_curve`, `issues`, `legionella`, `notifier`, `number_restore`, `off_restore`, `pump_arbiter`, `repairs`, `room_record`, `running_signal`, `services`,
 `store`, `supply_hold`. One module outside that set touches it at all: `inputs`
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
diff --git a/docs/configuration.md b/docs/configuration.md
index 9a855d8b88..d7e71dee11 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -96,7 +96,7 @@ Every picker on this second screen is optional; skip any you do not have. Withou
 | Heat pump operating mode | none | The pump's own mode selector — cooling, heating, hot water, or a combination of two. Read only unless **Pump duty control** is set to Control. Left empty, the optimizer assumes the pump can do everything. |
 | Defrosting | none | On while the pump reverses to melt frost off the outdoor coil. A sample of defrost activity, not a stopwatch — many pumps are only polled every few minutes. |
 | Pump online | none | Strongly recommended for a cloud-connected pump. On while the pump is actually reachable, which a stale cloud republish cannot tell you on its own. |
-| Fault alarm | none | On while the pump is reporting a fault. Only whether there is a fault is used, never the code itself. |
+| Fault alarm | none | On while the pump is reporting a fault. The optimizer pauses its learning while it is on, and discards a duty-switch measurement with a fault in it. Without a Fault text entity (options, Heat pump telemetry), each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex. |
 
 The heat-curve settings (the MQTT topics and the entity, for the three ways
 in [heat-curve.md](heat-curve.md)) are not asked during setup. Questions only
@@ -160,6 +160,8 @@ empty skips the screen. Where each suggestion comes from is listed under
 | Return water temperature | read from the device | Suggested only while the slot is empty. |
 | Actual frequency sensor (recommended for control) | read from the device | Suggested only while the slot is empty. |
 | Capacity limited (night mode) | read from the device | Suggested only while the slot is empty. |
+| Fault alarm | read from the device | Suggested only while the slot is empty: the Tuya integration's *Fault Alarm*, the GCHV Modbus package's *HP Alarm*. Keeping it brings the install under the readers of that slot: learning pauses while the pump reports a fault, and a duty-switch measurement with a fault in it is discarded. The GCHV alarm registers also report non-blocking warnings, and *HP Alarm* reads on for those too. |
+| Fault text | read from the device | Suggested only while the slot is empty, as a one-entity list: the Tuya integration's *Fault Description*. A GCHV package's four alarm sensors are not suggested; pick them on **Heat pump telemetry**. |
 | After saving | Menu | The options page's own navigation control, shown on this form too; setup continues to the finish menu whatever it says. |
 
 ### 4 · Temperature Settings
@@ -580,7 +582,7 @@ What the second form can suggest, and where each value comes from:
 | Heat pump max power (kW) | Unit capacity (1006H) | the unit's thermal capacity divided by the nominal COP in force |
 | What that set-point entity expects | Control mode (100DH) | *flow* when the unit runs on water temperature control |
 | What the control entity expects | Control mode (100DH) | *flow* on water temperature control, and only where the two-zone model the building page requires for it is configured |
-| Outdoor temperature sensor, Hot water tank temperature sensor, Supply (flow) water temperature, Return water temperature, Actual frequency sensor (recommended for control), Capacity limited (night mode) | the package's own sensors | suggested only while that slot is empty |
+| Outdoor temperature sensor, Hot water tank temperature sensor, Supply (flow) water temperature, Return water temperature, Actual frequency sensor (recommended for control), Capacity limited (night mode), Fault alarm (*HP Alarm*) | the package's own sensors | suggested only while that slot is empty |
 
 A register that is missing or unreadable suggests nothing, a value equal to the
 one already in force is not suggested, and a value outside its field's own
@@ -665,7 +667,8 @@ are on **Power and solar sensors**; mode / defrost / online / fault are on
 | Hot water start hysteresis | none | `sensor` / `number` / `input_number`, K | Optional. The pump's own hot water start hysteresis, a temperature difference; the plan places no charge on a tank at or above the hot water target less this. |
 | Defrosting | from setup | a binary sensor | On while the pump reverses to melt frost off the outdoor coil. |
 | Pump online | from setup | a binary sensor | On while the pump is actually reachable. |
-| Fault alarm | from setup | a binary sensor | On while the pump is reporting a fault. Only whether there is a fault is used. |
+| Fault alarm | from setup | a binary sensor | On while the pump is reporting a fault. The optimizer pauses its learning while it is on, and discards a duty-switch measurement with a fault in it. Without a Fault text entity, each fault's start and end are kept for Download diagnostics, with a numeric reading's code in hex. |
+| Fault text | none | 1 to 4 `sensor` / `text` / `input_text` entities | The pump's fault description: `OK`, or a comma list of codes such as `E5, P3`. Each fault's codes, start and end are kept for the last 200 faults, across restarts, and appear under `fault_log` in Download diagnostics; a fault that clears inside a minute is still recorded. A state of `OK`, `normal`, `none`, `no fault`, empty, or an off or idle word is no fault; **any other text is recorded as a code**, whatever the entity is, a status sensor or your own `input_text` included, so pick a fault description. On the Tuya integration this is the *Fault Description* sensor (pre-filled). On the GCHV Modbus package pick its four *HP Alarm bitmap 1–4* sensors: each reads `OK` or the names of its set bits, ending in the code, such as `IPM protection (P6)`. |
 | Space backup heater | none | a flag entity | On while the pump's own electric backup heater runs in the space heating circuit. Those kilowatts are not the compressor, so the optimizer stops reading the meter as an efficiency measurement while it is on — but the heat still counts, because it is real heat into the house. Worth filling in mainly on a pump that publishes no power meter, where there is otherwise no way to notice the element at all. |
 | Hot water tank booster | none | a flag entity | On while the electric heater in the hot water tank runs. Treated like the backup heater above, and each switch-on is also recorded as a hot water rescue: if those recur and you have turned on immersion feedback, the plan starts heating the tank a little earlier. |
 | Capacity limited (night mode) | none | a flag entity | On while the pump runs at a reduced compressor speed — night or silent mode on most units. Efficiency and capacity are not learned from those intervals, because what the machine shows then is the cap's. Cost and heat accounting still use the measured power: a speed-capped compressor draws exactly what the meter says. |
diff --git a/tests/closures.json b/tests/closures.json
index 8aa9d54129..47e021398f 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -217,6 +217,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -403,6 +404,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -908,6 +910,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1171,6 +1174,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1309,6 +1313,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1459,6 +1464,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -1858,6 +1864,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2411,6 +2418,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2621,6 +2629,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2789,6 +2798,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -2946,6 +2956,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -3332,6 +3343,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -3740,6 +3752,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4217,6 +4230,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4326,6 +4340,7 @@
    "custom_components/heatpump_optimizer/entity.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/external_heat.py",
+   "custom_components/heatpump_optimizer/fault_log.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/flow_limit.py",
    "custom_components/heatpump_optimizer/flow_meter.py",
@@ -4966,6 +4981,7 @@
    "dev/audit/harnesses/r11_money_currency_precedence.py",
    "dev/audit/harnesses/r11_outside_3849_unlatched_price.py",
    "dev/audit/harnesses/r11_owner_criteria.py",
+   "dev/audit/harnesses/r11_owner_fault_text.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
    "dev/audit/harnesses/r11_relay_3358_skip.py",
    "dev/audit/harnesses/r11_seam_config_silent_prefill.py",
diff --git a/tests/config_flow_steps.py b/tests/config_flow_steps.py
index 7249c94c95..f55a3e0e5e 100644
--- a/tests/config_flow_steps.py
+++ b/tests/config_flow_steps.py
@@ -1743,6 +1743,50 @@ async def options_room_list():
     )
 
 
+async def options_fault_text_list():
+    """R11-OWNER-FAULT-TEXT: the fault-text list on Heat pump telemetry, capped at four."""
+    R.section("options: the fault-text list saves up to four entities and refuses a fifth")
+    key = const.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES
+    flow, entry, _ = fresh_options()
+    shown = await flow.async_step_entities_pump(None)
+    widget = next((v for k, v in shown["data_schema"].schema.items() if str(k) == key), None)
+    check(
+        "opt_fault_text",
+        "happy",
+        "the telemetry page renders the fault-text field, a selector taking several sensor, text or "
+        "input_text entities, beside the fault alarm",
+        shows(shown, "entities_pump") and widget is not None and widget.config.get("multiple") is True
+        and widget.config["filter"][0]["domain"] == ["sensor", "text", "input_text"]
+        and [str(k) for k in shown["data_schema"].schema].index(key)
+        == [str(k) for k in shown["data_schema"].schema].index(const.CONF_HEAT_PUMP_FAULT_ENTITY) + 1,
+        f"{shown.get('step_id')!r}",
+    )
+    members = [f"sensor.hp_alarm_bitmap_{i}" for i in range(1, 6)]
+    refused = await submit(flow, "entities_pump", {key: members})
+    check(
+        "opt_fault_text",
+        "error",
+        "five fault-text entities are refused with their own error; null control, four save",
+        shows(refused, "entities_pump")
+        and refused.get("errors", {}).get(key) == "too_many_fault_text_entities"
+        and key not in entry.options
+        and shows_menu(await submit(flow, "entities_pump", {key: members[:4]}), "advanced")
+        and entry.options.get(key) == members[:4],
+        f"errors={refused.get('errors')!r} saved={entry.options.get(key)!r}",
+    )
+    await recover(flow, "entities_pump", {key: members[:4], **SAVE_CLOSE})
+    flow2, entry2, _ = fresh_options(pre_options={key: ["sensor.fd"]})
+    await flow2.async_step_entities_pump(None)
+    await submit(flow2, "entities_pump", {})
+    check(
+        "opt_fault_text",
+        "happy",
+        "an emptied submit clears the stored list (null control: the list was stored)",
+        key in entry2.options and entry2.options[key] is None,
+        f"options={entry2.options.get(key, 'absent')!r}",
+    )
+
+
 async def options_menus():
     R.section("options: the two menus")
     flow, entry, _ = fresh_options()
@@ -3673,12 +3717,10 @@ async def residual_statement_branches():
         f"suggested={suggested_value(form, const.CONF_HOUSE_POWER_ENTITY)!r}",
     )
 
-    # _user_sensors_sections' forgotten-field fallback: a picker the grouping
-    # table does not name stays visible and flat rather than vanishing from
-    # the setup page. The grouping table is rebound for this one check -- it
-    # is the only seam the function reads -- and restored immediately; the
-    # intact-table control beside it is what makes the fallback's firing
-    # specific to a forgotten field rather than unconditional.
+    # One table: the setup page's flat fields and its sections are both built
+    # from _USER_SENSORS_GROUPS. A picker cannot sit in one and not the other,
+    # the drift #824's flat fallback guarded against. Rebinding the table moves
+    # both alike; the intact table beside it is the control.
     real_groups = config_flow._USER_SENSORS_GROUPS
     try:
         config_flow._USER_SENSORS_GROUPS = (
@@ -3687,28 +3729,31 @@ async def residual_statement_branches():
                 (const.CONF_INDOOR_TEMP_ENTITY, const.CONF_OUTDOOR_TEMP_ENTITY),
             ),
         )
-        forgotten = config_flow._user_sensors_sections(FakeHass())
+        one_sections = config_flow._user_sensors_sections(FakeHass())
+        one_flat = {str(getattr(k, "schema", k)) for k in config_flow._user_sensors_fields(FakeHass())}
     finally:
         config_flow._USER_SENSORS_GROUPS = real_groups
-    forgotten_keys = {str(getattr(k, "schema", k)) for k in forgotten}
-    intact_keys = {
+    intact = config_flow._user_sensors_sections(FakeHass())
+    intact_flat = {str(getattr(k, "schema", k)) for k in config_flow._user_sensors_fields(FakeHass())}
+    in_sections = {
         str(getattr(k, "schema", k))
-        for k in config_flow._user_sensors_sections(FakeHass())
+        for value in intact.values() for k in value.schema.schema
     }
     check(
         "user_sensors",
         "happy",
-        "a picker the grouping table forgot stays on the page, flat",
-        const.CONF_SOLAR_RADIATION_ENTITY in forgotten_keys
-        and const.CONF_HEAT_PUMP_MODE_ENTITY in forgotten_keys,
-        f"flat top-level keys={sorted(forgotten_keys)}",
+        "the flat fields and the sections are one table: rebound to one group, both hold exactly its two pickers",
+        set(one_sections) == {"indoor"}
+        and one_flat == {const.CONF_INDOOR_TEMP_ENTITY, const.CONF_OUTDOOR_TEMP_ENTITY},
+        f"sections={sorted(one_sections)} flat={sorted(one_flat)}",
     )
     check(
         "user_sensors",
         "happy",
-        "the intact grouping table hides nothing: only the three sections",
-        intact_keys == {"indoor", "solar", "plant"},
-        f"keys={sorted(intact_keys)}",
+        "the intact grouping table hides nothing: only the three sections, holding every flat field",
+        set(intact) == {"indoor", "solar", "plant"} and in_sections == intact_flat and len(intact_flat) == 14
+        and all(value.options == {"collapsed": False} for value in intact.values()),
+        f"keys={sorted(intact)} missing={sorted(intact_flat - in_sections)}",
     )
 
     # _omit_unstored_computed's recompute-failure arm: a value whose computed
@@ -4794,6 +4839,8 @@ async def registry_walk_recurses():
         const.CONF_HEAT_PUMP_DEFROST_ENTITY,
         const.CONF_HEAT_PUMP_ONLINE_ENTITY,
         const.CONF_HEAT_PUMP_FAULT_ENTITY,
+        # R11-OWNER-FAULT-TEXT: the fault's code text, a list beside the alarm.
+        const.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES,
         # #1067: the pump's own electric heat and its night mode, on the same
         # page. Named here rather than counted for the reason above -- a
         # count would go on agreeing while a picker stopped rendering.
@@ -5904,7 +5951,9 @@ _NOOP_ALT = {
 }
 # diagnostics.py echoes the stored entry verbatim, so every key differs there
 # by construction; config_flow.py is the writer under test; const.py names.
-_NOOP_STATIC_SKIP = ("config_flow.py", "const.py", "diagnostics.py")
+# device_prefill.py reads no configuration: it is handed registry records, and
+# a key there is a role its tables resolve.
+_NOOP_STATIC_SKIP = ("config_flow.py", "const.py", "device_prefill.py", "diagnostics.py")
 
 
 def _noop_hass(now):
@@ -8176,10 +8225,16 @@ def _page_stored_entities(step, base):
 
 def _stored_seed(row, tag):
     """A distinct stored value for a ``_STORED`` row: an entity id for a
-    picker, an in-range number for the one optional number
-    (``space_setpoint_high_limit_c``), which clears the same way."""
+    picker (a one-element list for a list slot), an in-range number for the
+    one optional number (``space_setpoint_high_limit_c``), which clears the
+    same way."""
     if isinstance(row.widget, selector.NumberSelector):
         return float(row.widget.config["min"]) + 1.0
+    # A list slot (a selector taking several entities) stores a list: a
+    # string seeded there is a value no save writes, and the page's own
+    # cap check refuses every submit carrying it.
+    if row.widget.config.get("multiple"):
+        return [f"sensor.stored_{tag}"]
     return f"sensor.stored_{tag}"
 
 
@@ -8605,6 +8660,7 @@ async def main() -> int:
     await options_rejected_page_rerenders_the_clear()
     await options_cleared_price_entity_is_refused()
     await options_room_list()
+    await options_fault_text_list()
 
     rendered, recovered = LEDGER.error_triples()
     residual = sorted(f"{k}/{s}/{c}" for k, s, c in rendered - recovered)
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index ddc4836ea5..289a554940 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,9 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 123
+records every read, so this lane's recorded closure is the package: all 124
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (122 until R11-OUTSIDE-ROOMS-3B's ``comfort_floor.py``, 121 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 120 until R11-SEAM-cycle-solve's ``solve_gate.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
+alike (123 until the merge joining R11-OWNER-FAULT-TEXT's ``fault_log.py`` and R11-OUTSIDE-ROOMS-3B's ``comfort_floor.py``, 122 until either, 121 until R11-OWNER-FLOWCAP's ``flow_limit.py``, 120 until R11-SEAM-cycle-solve's ``solve_gate.py``, 118 until R11-SEAM-actuation-release's ``duty_ledger.py`` and ``number_restore.py``, 117 until its ``circulation.py``, 115 until R11-OUTSIDE-ROOMS-P3's ``room_history.py`` and ``room_record.py``, 114 until R11-OUTSIDE-ROOMS-P1's ``rooms.py``, 113 until R11-OUTSIDE-HONEST-STARTS-RUNS's ``runs.py``, 112 until #3616's ``slab_seed.py``, 111 until R10-START-COUNTER-EDGES's ``running_signal.py``, 110 until
 R10-ADVISOR-STEADY-START's ``whatif.py``, 109 until R10-DUTY-SWITCH-PLANNER-PRICE's
 ``duty_legs.py``, 108 until the supply-hold PR's ``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
@@ -57,16 +57,19 @@ which drives the CI ratchet's archscore measurement and so opens the package
 the way this lane's recorder does. A diff touching any production file
 therefore selects this lane. That is a selection cost, not a
 duplicate-assertion one: the same
-recording finds 184 of the 561 script pairs (34 choose 2) sharing 0.80 or more
-of their production-module closure (186 on R11-OUTSIDE-ROOMS-3B's branch and 182 on
-main before the merge joining them, main's R11-SEAM-entity-service services.yaml
-having taken config_flow_steps.py's pairs with debug_collect.py and wood_advisor.py
-under 0.80, 184 on main and 180 on that branch before it landed; on the rooms-3b
-branch, 184 on each side before the merge joining
-R11-OWNER-FLOWCAP's flow_limit.py and R11-OUTSIDE-ROOMS-3B's comfort_floor.py, which put
-card_drift.mjs and wood_advisor.py each with features.py at the 0.80 floor; 182
-before flow_limit.py on main and comfort_floor.py on its branch each lifted
-env_drift.py/manual_plan.py and golden.py/manual_plan.py to 0.80; 169 of 528 before R11-SEAM-tests's
+recording finds 182 of the 561 script pairs (34 choose 2) sharing 0.80 or more
+of their production-module closure (182 on the merge joining main's 184, which R11-OUTSIDE-ROOMS-3B's comfort_floor.py lifted from 182 (rooms-3b's own branch having been 184 on each side before the merge joining flow_limit.py and comfort_floor.py, 186 after), to this branch's 181, the union of the two histories that follow: this branch's, 184 before R11-OWNER-FAULT-TEXT's
+fault_log.py, read by config_flow_steps.py's closure but not by
+boost_drift_replay.py's or plan_view.py's, moved each of those two pairs with
+config_flow_steps.py from 0.800 to 0.792; 182 before R11-OWNER-FLOWCAP's
+flow_limit.py joined main's closures, adding env_drift.py/manual_plan.py and
+golden.py/manual_plan.py; and main's, 184 on main and 180 on R11-SEAM-entity-service's
+branch before the merge joining them, the branch's services.yaml having taken
+config_flow_steps.py's pairs with debug_collect.py and wood_advisor.py under 0.80;
+182 on main before R11-OWNER-FLOWCAP's flow_limit.py joined its closures, adding
+env_drift.py/manual_plan.py and golden.py/manual_plan.py, and 167 on the branch
+before the earlier merge joining it to that main;
+169 of 528 before R11-SEAM-tests's
 cycle_lane.py, whose closure opens the whole package, and 180 on its branch
 before the merge bringing R11-SEAM-actuation-release's three production
 modules; 167 before both; 164 on each side before the merge joining
@@ -74,7 +77,7 @@ R11-OUTSIDE-ROOMS-P1's rooms.py, read by every closure that imports the
 coordinator, the input reader, the config flow or the sensor platform, and
 R11-OUTSIDE-HONEST-STARTS-RUNS's recordings, which joined
 config_flow_steps.py/debug_collect.py at 0.80; 162 before #3616 re-recorded the
-closures that import the coordinator), all 184 among the 435 pairs whose two
+closures that import the coordinator), all 182 among the 435 pairs whose two
 scripts each have a non-empty production closure (``tests/arch_score.py``,
 ``tests/ha_contract.py``, ``tests/layout.py`` and ``tests/md_tables.mjs`` have none;
 ``tests/harness_headers.py`` joined the comparable set, and ten pairs, when
diff --git a/tests/entities.py b/tests/entities.py
index a5678e6a4c..139942ff21 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -4006,7 +4006,13 @@ def _p2_registry(sources):
                  # #2234: which age TABLE applies, never the age itself.
                  "inputs.py::source_polls":
                      "compares last_reported with last_updated, the re-report "
-                     "that marks a polling source; the age stays state_stamp's"}),
+                     "that marks a polling source; the age stays state_stamp's",
+                 # R11-OWNER-FAULT-TEXT: where a fault row starts or ends.
+                 "fault_log.py::_seconds":
+                     "stamps a fault row's start or end at the instant the "
+                     "fault's VALUE changed (last_changed); state_stamp answers "
+                     "when the entity was last heard from, which a re-reported "
+                     "code resets"}),
         # D12-s2-01: whether a step's draw means "on", held at four sites.
         dict(fact="on_threshold_kw", finding="D12-s2-01",
              match=_p2_match_node(
diff --git a/tests/features.py b/tests/features.py
index d6d6dd0124..1384439339 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -15326,6 +15326,7 @@ _FR_STORES = {
     "debug": "kept: a diagnostics collection",
     "off_restore": "kept: what the optimizer still owes an entity it wrote, at off or unload",
     "room_history": "kept: measured room readings; the report is re-derived on every read",
+    "fault_log": "kept: the pump's own fault reports, a record of what happened, nothing learned",
 }
 _fr_found = set()
 for _fr_p in sorted(_FrPath("custom_components/heatpump_optimizer").glob("*.py")):
@@ -61681,6 +61682,9 @@ _G7B_EXPECTED = {
     _g7_c.CONF_HEAT_PUMP_CAPACITY_LIMITED_ENTITY: (
         f"switch.{_G7B_SLUG}_night_mode_silent", 1.0),
     "r404": (f"number.{_G7B_SLUG}_dhw_setpoint", 1.0),
+    # R11-OWNER-FAULT-TEXT: the Fault Alarm and the dp 20 Fault Description.
+    _g7_c.CONF_HEAT_PUMP_FAULT_ENTITY: (f"binary_sensor.{_G7B_SLUG}_fault_alarm", 1.0),
+    _g7_c.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: (f"sensor.{_G7B_SLUG}_fault_description", 1.0),
 }
 _g7b_resolved = _g7b_dp.resolve(_g7b_records())
 R.check(
@@ -70491,6 +70495,8 @@ _P6_READ_ONLY = {
     # #3616: room thermostats' attributes are read by inputs.read_room; phase 1
     # writes no room thermostat.
     hp_const.CONF_ROOM_TEMPERATURE_ENTITIES: "room thermostats inputs.read_room reads",
+    # R11-OWNER-FAULT-TEXT: a text or input_text helper may hold the fault text.
+    hp_const.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: "the pump's fault text fault_log's listener reads",
 }
 
 
@@ -102758,6 +102764,568 @@ R.check(
     f"before={_rh_ul_before} after={_rh_ul_doc}",
 )
 
+# ---------------------------------------------------------------------------
+# R11-OWNER-FAULT-TEXT (#3857): the pump's fault record, shown in diagnostics
+# ---------------------------------------------------------------------------
+R.section("The pump's fault record (R11-OWNER-FAULT-TEXT)")
+import asyncio as _fl_aio  # noqa: E402
+import types as _fl_types  # noqa: E402
+from datetime import datetime as _fl_dt, timezone as _fl_tz  # noqa: E402
+from homeassistant.const import CONF_NAME as _FL_CONF_NAME, EVENT_HOMEASSISTANT_STOP as _FL_STOP  # noqa: E402
+from homeassistant.helpers import storage as _fl_storage  # noqa: E402
+from harness import FakeEntry as _fl_entry  # noqa: E402
+from heatpump_optimizer import diagnostics as _fl_diag  # noqa: E402
+from heatpump_optimizer import const as _FL_C  # noqa: E402
+from heatpump_optimizer import fault_log as _fl  # noqa: E402
+from heatpump_optimizer.entry_config import EntryConfig as _FlConfig  # noqa: E402
+from heatpump_optimizer import replay_doc as _fl_rd  # noqa: E402
+from heatpump_optimizer.store import admitted as _fl_storage_admitted  # noqa: E402
+
+
+def _fl_feed(readings, log=None):
+    """``(seconds, [member states])`` readings into a record, through code_text and note."""
+    log = log or _fl.Log(0)
+    for t, states in readings:
+        _fl.note(log, t, _fl.code_text(states))
+    return log
+
+
+# 1 and 2: rows from a single member.
+_fl_one = _fl_feed([(0, ["OK"]), (10, ["E5"]), (50, ["OK"])])
+_fl_null = _fl_feed([(0, ["OK"]), (40, ["OK"])])
+R.check(
+    "OK, E5, OK 40 s apart is one row of 40 s with E5; null control, OK then OK makes no row; "
+    "ok, Ok and OK all read healthy",
+    _fl_one.episodes == [[10, 50, "E5", False]] and _fl_one.open is None and _fl_null.episodes == []
+    and _fl_null.open is None and all(_fl.code_text([w]) is None for w in ("ok", "Ok", "OK", " OK "))
+    and _fl.note(_fl.Log(0), 5, None) is False and _fl.note(_fl.Log(0), 5, "E5") is True
+    and _fl.note(_fl.Log(0, open=[1, "E5"]), 5, "E5") is False,
+    f"{_fl_one.episodes} {_fl_null.episodes}",
+)
+_fl_two = _fl_feed([(0, ["E5"]), (10, ["E5, P3"])])
+R.check(
+    "E5 then E5, P3 closes the E5 row and opens the next at the same instant",
+    _fl_two.episodes == [[0, 10, "E5", False]] and _fl_two.open == [10, "E5, P3"],
+    f"{_fl_two.episodes} {_fl_two.open}",
+)
+
+# 3: several members, truncation.
+_FL_B3 = "IPM protection (P6), 3x high discharge temp in 100 min (H6)"
+_fl_gchv = _fl.code_text(["Low pressure (P3)", "OK", _FL_B3, "OK"])
+_fl_many_items = [f"item {i} (E{i})" for i in range(30)]
+_fl_many = _fl.code_text([", ".join(_fl_many_items)])
+_fl_kept = _fl_many.rsplit(" +", 1)[0].split(", ")
+_fl_long = "x" * 200 + " overheat (H9)" + "y" * 86
+_fl_tail = _fl.code_text([_fl_long])
+_fl_at = _fl.code_text(["a" * 79 + ", " + "b" * 79 + ", c"])
+_fl_over = _fl.code_text(["a" * 79 + ", " + "b" * 80])
+_fl_whole = _fl.code_text(["z" * 160])
+R.check(
+    "the 160-character budget is inclusive: two items joining to exactly 160 characters are both kept, "
+    "one character more drops the second; a single item of exactly 160 is kept whole, without an ellipsis",
+    _fl_at == "a" * 79 + ", " + "b" * 79 + " +1" and _fl_over == "a" * 79 + " +1" and _fl_whole == "z" * 160,
+    f"{_fl_at[-6:]!r} {_fl_over[-6:]!r} {len(_fl_whole)}",
+)
+R.check(
+    "two faulted GCHV members keep their items in slot order and the (P6) and (H6) names whole; "
+    "30 items keep a whole-item prefix with +N counting the rest, within 168 characters; a single "
+    "300-character item keeps its last 160 characters behind an ellipsis",
+    _fl_gchv == "Low pressure (P3), " + _FL_B3
+    and _fl_kept == _fl_many_items[:len(_fl_kept)] and _fl_many.endswith(f" +{30 - len(_fl_kept)}")
+    and len(_fl_kept) < 30 and len(_fl_many) <= 168
+    and _fl_tail == "…" + _fl_long[-160:] and len(_fl_tail) == 161,
+    f"{_fl_gchv!r} {_fl_many!r} {len(_fl_many)} {_fl_tail[:12]!r}",
+)
+
+# 4 and 5: the flag slot's strict reading, and the text slot's decision.
+R.check(
+    "the flag slot: on and off on a binary sensor read as a flag fault and healthy; 2080 and 2080.0 "
+    "give 0x0820; heating on a sensor fault slot is no reading (strict); null control, the same "
+    "state on a binary_sensor reads through the flag path",
+    _fl.flag_text("binary_sensor.f", "on") == ("flag", _fl.NO_CODE)
+    and _fl.flag_text("binary_sensor.f", "off") == ("flag", None)
+    and _fl.flag_text("sensor.f", "2080") == _fl.flag_text("sensor.f", "2080.0") == ("bitmap", "0x0820")
+    and _fl.flag_text("sensor.f", "1.5") == ("flag", _fl.NO_CODE)
+    and _fl.flag_text("sensor.f", "1") == ("bitmap", "0x0001")
+    and _fl.flag_text("sensor.f", "-5") == ("bitmap", _fl.NO_CODE)
+    and _fl.flag_text("sensor.f", "0") == ("bitmap", None)
+    and _fl.flag_text("sensor.f", str(0xFFFFFFFF)) == ("bitmap", "0xFFFFFFFF")
+    and _fl.flag_text("sensor.f", str(0x100000000)) == ("bitmap", _fl.NO_CODE)
+    and _fl.flag_text("sensor.f", "heating") is None
+    and _fl.flag_text("binary_sensor.f", "heating") == ("flag", _fl.NO_CODE),
+    f"{_fl.flag_text('sensor.f', 'heating')} {_fl.flag_text('binary_sensor.f', 'heating')}",
+)
+R.check(
+    "the text slot: heating and idle record nothing; defrosting and Unit in heat mode are recorded as codes",
+    _fl.code_text(["heating"]) is None and _fl.code_text(["idle"]) is None
+    and _fl.code_text(["defrosting"]) == "defrosting"
+    and _fl.code_text(["Unit in heat mode"]) == "Unit in heat mode",
+    f"{_fl.code_text(['defrosting'])}",
+)
+R.check(
+    "an empty item between or after commas records nothing: E5, reads E5 and E5,,E6 reads E5, E6; "
+    "null control, a lone comma is no item, so the member reads healthy",
+    _fl.code_text(["E5,"]) == "E5" and _fl.code_text(["E5,,E6"]) == "E5, E6"
+    and _fl.code_text([" , "]) is None and _fl.code_text(["E5, E6"]) == "E5, E6",
+    f"{_fl.code_text(['E5,'])!r} {_fl.code_text(['E5,,E6'])!r} {_fl.code_text([' , '])!r}",
+)
+
+# 7: the ring and the tally.
+_fl_ring = _fl.Log(0)
+for _fl_i in range(250):
+    _fl.note(_fl_ring, 100 * _fl_i, f"E{_fl_i % 40}")
+    _fl.note(_fl_ring, 100 * _fl_i + 7 + _fl_i % 3, None)
+R.check(
+    "250 episodes keep the newest 200 and count 50 dropped; 40 texts tally 32 plus other, and the "
+    "tallied seconds equal the sum over all 250 episodes",
+    len(_fl_ring.episodes) == _fl.EPISODES_MAX == 200 and _fl_ring.dropped == 50
+    and _fl_ring.episodes[0][0] == 5000
+    and len(_fl_ring.codes) == 33 and _fl.OTHER in _fl_ring.codes
+    and sum(c[0] for c in _fl_ring.codes.values()) == 250
+    and sum(c[1] for c in _fl_ring.codes.values()) == sum(7 + i % 3 for i in range(250)),
+    f"{len(_fl_ring.episodes)} {_fl_ring.dropped} {len(_fl_ring.codes)}",
+)
+_fl_back = _fl.Log(0, open=[100, "E5"])
+_fl.note(_fl_back, 40, None)
+_fl_fwd = _fl.Log(0, open=[100, "E5"])
+_fl.note(_fl_fwd, 130, None)
+R.check(
+    "a reading stamped before the open row's start closes it at its start: zero seconds, never a "
+    "negative row or tally; null control, a reading 30 s after the start closes a 30 s row",
+    _fl_back.episodes == [[100, 100, "E5", False]] and _fl_back.codes == {"E5": [1, 0, 100]}
+    and _fl_fwd.episodes == [[100, 130, "E5", False]] and _fl_fwd.codes == {"E5": [1, 30, 130]},
+    f"{_fl_back.episodes} {_fl_back.codes} {_fl_fwd.episodes}",
+)
+_fl_short = _fl.loaded({**_fl.stored(_fl_ring), "episodes": [[1, 2, "E5"], [3, 4, "P3", False]]}, 77)
+_fl_off = _fl.loaded({**_fl.stored(_fl_ring), "dropped": -1}, 77)
+_fl_bare = _fl.loaded({"since_s": 5}, 77)
+R.check(
+    "the store round-trips the record and declares every field; a row of the wrong shape is dropped "
+    "alone; a field outside its declaration starts the record afresh at the load's time",
+    _fl.stored(_fl.loaded(_fl.stored(_fl_ring), 1)) == _fl.stored(_fl_ring)
+    and _fl_storage_admitted("fault_log", _fl.stored(_fl_ring))
+    and _fl_short.episodes == [[3, 4, "P3", False]] and _fl_short.since_s == 0
+    and _fl_off.episodes == [] and _fl_off.since_s == 77 and _fl_off.codes == {}
+    and (_fl_bare.since_s, _fl_bare.dropped, _fl_bare.episodes, _fl_bare.open) == (5, 0, [], None),
+    f"{_fl_short.episodes} {_fl_off.since_s}",
+)
+_FL_ROWS = [[i, i + 1, "E5", False] for i in range(250)]
+_fl_big = _fl.loaded({**_fl.stored(_fl_ring), "episodes": _FL_ROWS}, 77)
+_fl_cap = _fl.loaded({**_fl.stored(_fl_ring), "episodes": _FL_ROWS[:200]}, 77)
+R.check(
+    "a stored document of 250 rows, which the store's declaration admits, loads as its newest 200; "
+    "null control, a document of exactly 200 rows loads whole",
+    _fl_storage_admitted("fault_log", {**_fl.stored(_fl_ring), "episodes": _FL_ROWS})
+    and _fl_big.episodes == _FL_ROWS[-200:] and _fl_cap.episodes == _FL_ROWS[:200],
+    f"{len(_fl_big.episodes)} {_fl_big.episodes[0]} {len(_fl_cap.episodes)}",
+)
+
+
+# 6: the listener, the save limiter, stop, unload and restart, through async_setup.
+class _FlHass(FakeHass):
+    """Runs the record's save tasks on the test's loop, as Home Assistant does."""
+
+    def async_create_task(self, coro):
+        return _fl_aio.get_running_loop().create_task(coro)
+
+
+_FL_CLOCK = [1000.0]
+_fl.time = _fl_types.SimpleNamespace(monotonic=lambda: _FL_CLOCK[0])
+_FL_T0 = _fl_dt(2026, 11, 1, tzinfo=_fl_tz.utc)
+_FL_TEXT = {_FL_C.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: ["sensor.fd"]}
+
+
+def _fl_state(text, seconds):
+    return FakeState(text, last_updated=_fl_dt.fromtimestamp(_FL_T0.timestamp() + seconds, _fl_tz.utc))
+
+
+async def _fl_fire(hass, entity_id, text, seconds):
+    for ids, action in list(getattr(hass, "state_listeners", [])):
+        if entity_id in ids:
+            action(_fl_types.SimpleNamespace(data={"entity_id": entity_id, "new_state": _fl_state(text, seconds)}))
+    for _ in range(3):
+        await _fl_aio.sleep(0)
+
+
+def _fl_key(entry):
+    return f"heatpump_optimizer_{entry.entry_id}_fault_log"
+
+
+async def _fl_flaps(entry_id, min_s):
+    _fl.SAVE_MIN_S, saved_min = min_s, _fl.SAVE_MIN_S
+    try:
+        hass, entry = _FlHass({"sensor.fd": _fl_state("OK", 0)}), _fl_entry(entry_id=entry_id)
+        await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
+        for k in range(120):
+            _FL_CLOCK[0] += 1.0
+            await _fl_fire(hass, "sensor.fd", "E5" if k % 2 == 0 else "OK", k + 1)
+        timers = list(getattr(hass, "timers", []))
+        _FL_DELAYS[entry_id] = [delay for delay, _a in timers]
+        for _delay, action in timers:
+            action(None)
+        for _ in range(3):
+            await _fl_aio.sleep(0)
+        doc = _fi_json.loads(_fl_storage._DISK.get(_fl_key(entry), "{}"))
+        saves = _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0)
+        live = _fl.stored(_fl._RECORDS[entry].log)
+        _FL_CLOCK[0] += 61.0
+        await _fl_fire(hass, "sensor.fd", "P3", 200)
+        _FL_AFTER[entry_id] = _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0) - saves
+        return saves, doc.get("data", doc), live
+    finally:
+        _fl.SAVE_MIN_S = saved_min
+
+
+_FL_DELAYS, _FL_AFTER = {}, {}
+_fl_saves, _fl_last_doc, _fl_live = _fl_aio.run(_fl_flaps("fl_flap", _fl.SAVE_MIN_S))
+_fl_saves0, _, _ = _fl_aio.run(_fl_flaps("fl_flap_null", 0.0))
+R.check(
+    "120 flaps in 120 s write at most 3 saves, the last state saved by the deferred timer; null "
+    "control, with the limiter's window at zero every one of the 120 opens and closes is a save",
+    1 <= _fl_saves <= 3 and _fl_last_doc == _fl_live and len(_fl_live["episodes"]) == 60
+    and _fl_saves0 == 120 and _FL_DELAYS["fl_flap"] == [_fl.SAVE_MIN_S - 1.0] == [59.0]
+    and _FL_AFTER["fl_flap"] == 1,
+    f"saves={_fl_saves} null={_fl_saves0} rows={len(_fl_live['episodes'])}",
+)
+
+
+async def _fl_restart():
+    hass, entry = _FlHass({"sensor.fd": _fl_state("OK", 0)}), _fl_entry(entry_id="fl_restart")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
+    await _fl_fire(hass, "sensor.fd", "E5", 30)
+    unavailable_open = None
+    await _fl_fire(hass, "sensor.fd", "unavailable", 40)
+    unavailable_open = list(_fl._RECORDS[entry].log.open or [])
+    stops = hass.bus.listeners_for(_FL_STOP)
+    before = _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0)
+    for stop in stops:
+        await stop(None)
+    _FL_STOPPED.extend([_fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0) - before, len(hass.state_listeners)])
+    hass2, entry2 = _FlHass({"sensor.fd": _fl_state("E5", 30)}), _fl_entry(entry_id="fl_restart")
+    await _fl.async_setup(hass2, entry2, _FlConfig.from_mapping(_FL_TEXT))
+    continued = _fl._RECORDS[entry2].log
+    return len(stops), unavailable_open, continued.open, continued.episodes
+
+
+_FL_STOPPED = []
+_fl_stops, _fl_unav, _fl_cont_open, _fl_cont_rows = _fl_aio.run(_fl_restart())
+_FL_S30 = int(_FL_T0.timestamp()) + 30
+R.check(
+    "unavailable mid-episode does not close the row; open, the stop event, then a reload whose first "
+    "read is the same code: the row continues with its original start",
+    _fl_stops == 1 and _fl_unav == [_FL_S30, "E5"] and _fl_cont_open == [_FL_S30, "E5"] and _fl_cont_rows == []
+    and _FL_STOPPED == [1, 0],
+    f"stops={_fl_stops} unavailable={_fl_unav} open={_fl_cont_open} rows={_fl_cont_rows}",
+)
+
+
+async def _fl_unload():
+    hass, entry = _FlHass({"sensor.fd": _fl_state("OK", 0)}), _fl_entry(entry_id="fl_unload")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
+    _FL_CLOCK[0] += 1000.0
+    await _fl_fire(hass, "sensor.fd", "P3", 10)
+    action = hass.state_listeners[0][1]
+    await _fl.async_close(entry)
+    await _fl.async_close(entry)
+    saves = _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0)
+    action(_fl_types.SimpleNamespace(data={"entity_id": "sensor.fd", "new_state": _fl_state("OK", 20)}))
+    for _ in range(3):
+        await _fl_aio.sleep(0)
+    rec = _fl._RECORDS[entry]
+    return (saves, _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0), rec.log.open, rec.log.episodes,
+            hass.state_listeners, getattr(hass, "timers", []))
+
+
+_fl_ul = _fl_aio.run(_fl_unload())
+R.check(
+    "open, then unload, then an event fired after close: no row and no save, the listener is gone "
+    "and a second close saves nothing",
+    _fl_ul[0] == _fl_ul[1] == 2 and _fl_ul[2] == [int(_FL_T0.timestamp()) + 10, "P3"] and _fl_ul[3] == []
+    and _fl_ul[4] == [] and _fl_ul[5] == [],
+    f"{_fl_ul}",
+)
+
+
+async def _fl_failed_setup(failed):
+    """An open row closed inside the save window, the entry's end, a second setup, one event."""
+    hass, entry = _FlHass({"sensor.fd": _fl_state("OK", 0)}), _fl_entry(entry_id=f"fl_failed_{failed}")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
+    _FL_CLOCK[0] += 1000.0
+    await _fl_fire(hass, "sensor.fd", "P3", 5)
+    await _fl_fire(hass, "sensor.fd", "OK", 6)  # deferred: only the entry's end saves this row
+    if not failed:  # the unload path: async_unload_entry closes, then Home Assistant runs the callbacks
+        await _fl.async_close(entry)
+    # A setup that raises after fault_log's runs only the entry's on_unload callbacks.
+    for unload in list(entry._on_unload):
+        unload()
+    entry._on_unload.clear()
+    left = len(hass.state_listeners), len(getattr(hass, "timers", []))
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))  # no yield first
+    restored = [list(r) for r in _fl._RECORDS[entry].log.episodes]
+    for _ in range(3):
+        await _fl_aio.sleep(0)
+    _FL_CLOCK[0] += 1000.0
+    before = _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0)
+    await _fl_fire(hass, "sensor.fd", "E5", 10)
+    return (*left, restored, len(hass.state_listeners),
+            _fl_storage.SAVE_COUNTS.get(_fl_key(entry), 0) - before)
+
+
+_fl_fs = _fl_aio.run(_fl_failed_setup(True))
+_fl_fs_null = _fl_aio.run(_fl_failed_setup(False))
+_FL_P3 = [[int(_FL_T0.timestamp()) + 5, int(_FL_T0.timestamp()) + 6, "P3", False]]
+R.check(
+    "a setup that fails after the record's (only the entry's on_unload callbacks run) releases the "
+    "listener and the deferred save, and its last save lands before the next setup loads: that setup "
+    "holds the P3 row watched to its end, one listener, and one event is one save; null control, the "
+    "unload path (close, then the callbacks) reads the same, the callbacks releasing nothing twice",
+    _fl_fs == _fl_fs_null == (0, 0, _FL_P3, 1, 1),
+    f"failed={_fl_fs} unload={_fl_fs_null}",
+)
+
+
+async def _fl_late():
+    hass, entry = _FlHass({"sensor.fd": _fl_state("P3", 5)}), _fl_entry(entry_id="fl_late")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
+    await _fl.async_close(entry)
+    hass2, entry2 = _FlHass({"sensor.fd": _fl_state("OK", 500)}), _fl_entry(entry_id="fl_late")
+    await _fl.async_setup(hass2, entry2, _FlConfig.from_mapping(_FL_TEXT))
+    await _fl_fire(hass2, "sensor.fd", "E5", 600)
+    await _fl_fire(hass2, "sensor.fd", "OK", 640)
+    return _fl._RECORDS[entry2].log
+
+
+_fl_late_log = _fl_aio.run(_fl_late())
+R.check(
+    "a stored P3 whose first read after a restart is OK closes at that read, marked late; the next row, "
+    "watched from start to end, is not",
+    _fl_late_log.open is None
+    and _fl_late_log.episodes == [[int(_FL_T0.timestamp()) + 5, int(_FL_T0.timestamp()) + 500, "P3", True],
+                                  [int(_FL_T0.timestamp()) + 600, int(_FL_T0.timestamp()) + 640, "E5", False]],
+    f"{_fl_late_log.episodes}",
+)
+
+
+async def _fl_members():
+    states = {"sensor.b1": _fl_state("OK", 0), "sensor.b3": _fl_state(_FL_B3, 0)}
+    hass, entry = _FlHass(dict(states)), _fl_entry(entry_id="fl_members")
+    config = {_FL_C.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: ["sensor.b1", "sensor.b3"]}
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(config))
+    await _fl.async_close(entry)
+    hass2, entry2 = _FlHass(dict(states)), _fl_entry(entry_id="fl_members")
+    await _fl.async_setup(hass2, entry2, _FlConfig.from_mapping(config))
+    return _fl._RECORDS[entry2].log
+
+
+_fl_mem = _fl_aio.run(_fl_members())
+R.check(
+    "a restart whose first member reads OK and second still carries the code continues the row: the "
+    "slot is read whole, never its first member alone",
+    _fl_mem.episodes == [] and _fl_mem.open == [int(_FL_T0.timestamp()), _FL_B3],
+    f"{_fl_mem.episodes} {_fl_mem.open}",
+)
+
+
+async def _fl_none():
+    hass, entry = _FlHass({}), _fl_entry(entry_id="fl_none")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping({}))
+    return _fl.diagnostics_view(entry), getattr(hass, "state_listeners", []), hass.bus.listeners
+
+
+_fl_no = _fl_aio.run(_fl_none())
+R.check(
+    "no fault source: no record, no listener, no stop hook, no store, and the section is null",
+    _fl_no == (None, [], []) and _fl_key(_fl_entry(entry_id="fl_none")) not in _fl_storage._DISK,
+    f"{_fl_no}",
+)
+
+
+async def _fl_view():
+    hass, entry = _FlHass({"binary_sensor.alarm": _fl_state("off", 0)}), _fl_entry(entry_id="fl_view")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping({_FL_C.CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.alarm"}))
+    await _fl_fire(hass, "binary_sensor.alarm", "on", 60)
+    await _fl_fire(hass, "binary_sensor.alarm", "off", 90)
+    rec = _fl._RECORDS[entry]
+    rec.log.episodes.append([int(_FL_T0.timestamp()) + 100, int(_FL_T0.timestamp()) + 160, "Pumphouse", False])
+    rec.log.codes["Pumphouse"] = [1, 60, int(_FL_T0.timestamp()) + 160]
+    return _fl.diagnostics_view(entry)
+
+
+_fl_v = _fl_aio.run(_fl_view())
+_fl_private = frozenset(_fl_diag._private_values([{_FL_CONF_NAME: "Pumphouse"}, {}]))
+_fl_red = _fl_diag._without_values({"fault_log": _fl_v}, _fl_private)["fault_log"]
+R.check(
+    "the flag slot's section: source flag, the 30 s row with a null code, newest last; a code text "
+    "equal to the entry's name comes out redacted, row and tally key alike, while E-codes are kept",
+    _fl_v["source"] == "flag" and _fl_v["entities"] == ["binary_sensor.alarm"]
+    and _fl_v["episodes"][0]["seconds"] == 30 and _fl_v["episodes"][0]["code"] is None
+    and _fl_v["episodes"][0]["start"] == _fl_dt.fromtimestamp(_FL_T0.timestamp() + 60, _fl_tz.utc).isoformat()
+    and len("Pumphouse") >= _fl_rd.LEAK_MIN_CHARS
+    and _fl_red["episodes"][1]["code"] != "Pumphouse" and "Pumphouse" not in _fl_red["codes"]
+    and _fl_v["open"] is None and _fl_v["dropped"] == 0 and set(_fl_v["codes"]) == {"Pumphouse"},
+    f"{_fl_v} {_fl_red}",
+)
+
+async def _fl_bitmap():
+    hass, entry = _FlHass({"sensor.fault_code": _fl_state("0", 0)}), _fl_entry(entry_id="fl_bitmap")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping({_FL_C.CONF_HEAT_PUMP_FAULT_ENTITY: "sensor.fault_code"}))
+    await _fl_fire(hass, "sensor.fault_code", "2080", 10)
+    mid = list(_fl._RECORDS[entry].log.open or [])
+    await _fl_fire(hass, "sensor.fault_code", "heating", 20)
+    held = list(_fl._RECORDS[entry].log.open or [])
+    await _fl_fire(hass, "sensor.fault_code", "0", 30)
+    return mid, held, _fl.diagnostics_view(entry)
+
+
+_fl_bm_mid, _fl_bm_held, _fl_bm = _fl_aio.run(_fl_bitmap())
+_FL_S10 = int(_FL_T0.timestamp()) + 10
+R.check(
+    "a sensor fault slot reading a register: 2080 opens a 0x0820 row, heating mid-episode is no reading "
+    "and leaves it open, 0 closes it after 20 s; the section names the source bitmap",
+    _fl_bm_mid == _fl_bm_held == [_FL_S10, "0x0820"] and _fl_bm["source"] == "bitmap"
+    and [(e["seconds"], e["code"]) for e in _fl_bm["episodes"]] == [(20, "0x0820")],
+    f"{_fl_bm_mid} {_fl_bm_held} {_fl_bm}",
+)
+
+async def _fl_edges():
+    hass, entry = _FlHass({"sensor.fd": _fl_state("OK", 0)}), _fl_entry(entry_id="fl_edges")
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
+    rec = _fl._RECORDS[entry]
+    rec.saved_at = _FL_CLOCK[0] - (_fl.SAVE_MIN_S - 1.0)
+    _fl._request_save(rec)
+    delays = [delay for delay, _a in getattr(hass, "timers", [])]
+
+    class _Refusing:
+        async def async_save(self, data):
+            raise OSError("disk full")
+
+    rec.store = _Refusing()
+    await _fl._save(rec)
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping({}))
+    return delays, _fl.diagnostics_view(entry)
+
+
+_fl_edge_delays, _fl_edge_view = _fl_aio.run(_fl_edges())
+R.check(
+    "one second before the save window ends a change waits one second, never saves at once; a save that "
+    "raises is logged, not raised; setting the entry up again with no fault slot drops the old record",
+    _fl_edge_delays == [1.0] and _fl_edge_view is None,
+    f"{_fl_edge_delays} {_fl_edge_view}",
+)
+
+
+async def _fl_v1(version):
+    """A record an install saved at store ``version``, then a setup whose first read is the same code."""
+    hass, entry = _FlHass({"sensor.fd": _fl_state("E5", 900)}), _fl_entry(entry_id=f"fl_v{version}")
+    _fl_storage._DISK[_fl_key(entry)] = _fi_json.dumps(
+        _fl.stored(_fl.Log(7, source="text", episodes=[[1, 2, "P3", False]], open=[100, "E5"],
+                           codes={"P3": [1, 1, 2]})))
+    _fl_storage._VERSIONS[_fl_key(entry)] = version
+    await _fl.async_setup(hass, entry, _FlConfig.from_mapping(_FL_TEXT))
+    log = _fl._RECORDS[entry].log
+    await _fl.async_close(entry)
+    return log.since_s, log.episodes, log.open, _fl_storage._VERSIONS[_fl_key(entry)]
+
+
+_fl_v1_read = _fl_aio.run(_fl_v1(1))
+_fl_v2_read = _fl_aio.run(_fl_v1(2))
+R.check(
+    "a fault record saved at store version 1 loads whole and saves back at 1: its row, its open E5 "
+    "continued by an E5 read, its start; null control, a document stamped version 2 is refused, so the "
+    "record starts afresh with the E5 opened at the read",
+    _fl_v1_read == (7, [[1, 2, "P3", False]], [100, "E5"], 1)
+    and _fl_v2_read[1] == [] and _fl_v2_read[2] == [int(_FL_T0.timestamp()) + 900, "E5"]
+    and _fl_v2_read[0] != 7,
+    f"v1={_fl_v1_read} v2={_fl_v2_read}",
+)
+
+_fl_now_real = _fl._now_s
+_fl._now_s = lambda: 5000  # noqa: E731
+_fl_entry_key = _fl_entry(entry_id="fl_skew")
+try:
+    _fl._RECORDS[_fl_entry_key] = _fl._Record(
+        None, None, "text", ["sensor.fd"], _fl.Log(4000, source="text", open=[5300, "E5"]))
+    _fl_skew = _fl.diagnostics_view(_fl_entry_key)["open"]
+    _fl._RECORDS[_fl_entry_key].log.open = [4970, "E5"]
+    _fl_skew_null = _fl.diagnostics_view(_fl_entry_key)["open"]
+finally:
+    _fl._now_s = _fl_now_real
+R.check(
+    "an open row stamped 300 s after the view's clock (a state's last_changed ahead of this host) shows "
+    "0 open seconds, never a negative span; null control, one stamped 30 s before shows 30",
+    _fl_skew["seconds"] == 0 and _fl_skew["code"] == "E5" and _fl_skew_null["seconds"] == 30,
+    f"{_fl_skew} {_fl_skew_null}",
+)
+
+# 9: the prefill rows (the device route's roles are pinned in W1067-G7b-1's table above).
+_fl_dev = {"sensor.rw_fault_description": FakeState("OK"), "binary_sensor.rw_fault_alarm": FakeState("off")}
+_fl_dev_roles = {
+    _FL_C.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: _g7_mp.ResolvedRole(("sensor.rw_fault_description",)),
+    _FL_C.CONF_HEAT_PUMP_FAULT_ENTITY: _g7_mp.ResolvedRole(("binary_sensor.rw_fault_alarm",)),
+}
+_fl_dev_snap = _g7_mp.snapshot(_fl_dev.get, _fl_dev_roles)
+_fl_gchv_snap = _g7_mp.snapshot({"binary_sensor.hp_alarm": FakeState("off")}.get, _g7_mp.candidates("hp"))
+_fl_set = {_FL_C.CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.mine",
+           _FL_C.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: ["sensor.mine"]}
+R.check(
+    "pre-fill: a signed Tuya device suggests a one-member text list and its fault binary sensor; a GCHV "
+    "prefix suggests binary_sensor.<p>_alarm and no text slot; null controls, slots already set are not "
+    "suggested, and a device whose records lack the signature resolves neither",
+    {k: v for k, v in _g7_mp.infer(_fl_dev_snap, {}).items() if "fault" in k} == {
+        _FL_C.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: ["sensor.rw_fault_description"],
+        _FL_C.CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.rw_fault_alarm"}
+    and {k: v for k, v in _g7_mp.infer(_fl_gchv_snap, {}).items() if "fault" in k} == {
+        _FL_C.CONF_HEAT_PUMP_FAULT_ENTITY: "binary_sensor.hp_alarm"}
+    and not any("fault" in k for k in _g7_mp.infer(_fl_dev_snap, _fl_set))
+    and not any("fault" in k for k in _g7b_dp.resolve(_g7b_records(drop={
+        f"{_G7B_SLUG}_T4", f"{_G7B_SLUG}_Tin", f"{_G7B_SLUG}_night_mode", f"{_G7B_SLUG}_DHWSET"}))),
+    f"{_g7_mp.infer(_fl_dev_snap, {})} {_g7_mp.infer(_fl_gchv_snap, {})}",
+)
+
+# The entry's own path: setup subscribes, the download carries the section, unload saves.
+async def _fl_entry_path(entry_id, options):
+    hass = FakeHass({"sensor.fd": FakeState("E5")})
+    _seed_prices(hass)
+    entry = FakeEntry(data=_LC_DATA, options=options, entry_id=entry_id)
+    await _ha_setup_entry(_integ, hass, entry)
+    diag = await _fl_diag.async_get_config_entry_diagnostics(hass, entry)
+    unloaded = await _ha_unload_entry(_integ, hass, entry)
+    doc = _fi_json.loads(_fl_storage._DISK.get(_fl_key(entry), "null") or "null")
+    return diag["coordinator"].get("fault_log", "missing"), unloaded, doc
+
+
+_fl_ep_view, _fl_ep_ok, _fl_ep_doc = _fl_aio.run(
+    _fl_entry_path("fl_entry", {_FL_C.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: ["sensor.fd"]}))
+_fl_ep_null = _fl_aio.run(_fl_entry_path("fl_entry_none", {}))
+R.check(
+    "through async_setup_entry: the download's coordinator.fault_log shows the open E5 read at setup, and "
+    "async_unload_entry saves it; null control, an entry with no fault slot has a null section and no store",
+    _fl_ep_ok and _fl_ep_view["source"] == "text" and _fl_ep_view["open"]["code"] == "E5"
+    and (_fl_ep_doc or {}).get("data", _fl_ep_doc or {}).get("open", [None, None])[1] == "E5"
+    and _fl_ep_null[0] is None and _fl_ep_null[1] and _fl_ep_null[2] is None,
+    f"view={_fl_ep_view} doc={_fl_ep_doc} null={_fl_ep_null}",
+)
+
+# 10: a synthetic day (no install data): one multi-hour P3 and twelve sub-minute E5s.
+_fl_day = [(0, ["OK"]), (2 * 3600, ["P3"]), (6 * 3600, ["OK"])]
+for _fl_h in range(8, 20):
+    _fl_day += [(_fl_h * 3600 + 600, ["E5"]), (_fl_h * 3600 + 640, ["OK"])]
+
+
+def _fl_state_at(t):
+    return next(s for at, s in reversed(_fl_day) if at <= t)
+
+
+_fl_events = _fl_feed(_fl_day)
+_fl_cycles = _fl_feed([(t, _fl_state_at(t)) for t in range(0, 86400, 1800)])
+R.check(
+    "a synthetic day of one 4-hour P3 and twelve 40-second E5s gives 13 rows and an E5 tally of 12; "
+    "null control, sampling the same day once per 30-minute cycle, today's path, sees at most 2",
+    len(_fl_events.episodes) == 13 and _fl_events.codes["E5"][0] == 12 and _fl_events.codes["P3"][1] == 4 * 3600
+    and _fl_events.codes["E5"][2] == 19 * 3600 + 640
+    and len(_fl_cycles.episodes) <= 2,
+    f"events={len(_fl_events.episodes)} cycles={len(_fl_cycles.episodes)}",
+)
 
 R.section("#3616 R11-OUTSIDE-ROOMS-3B: the room lift on the solve's record, the why-now row and the narrative")
 
diff --git a/tests/finite_boundary.py b/tests/finite_boundary.py
index d06ac60c6d..e84d0ae052 100644
--- a/tests/finite_boundary.py
+++ b/tests/finite_boundary.py
@@ -273,6 +273,7 @@ def _healthy_payloads() -> dict[str, dict]:
     _off.armed.update({"heat_curve": None, "stand_in": 21.5})
     run(off_restore._save(_off))
     run(_save_room_history(coord))
+    run(_save_fault_log(coord))
     run(_save_notifier(coord))
     run(_save_debug(coord))
     disk = {k: json.loads(v) for k, v in _storage._DISK.items()}
@@ -491,6 +492,28 @@ async def _save_room_history(coord):
     await room_record._persist(rec)
 
 
+_FAULT_LOG_CONFIG = {const.CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: ["sensor.fault_description"]}
+
+
+async def _load_fault_log(coord):
+    """The fault record's one loader: setup, which loads before it reads or subscribes."""
+    from heatpump_optimizer import fault_log
+    from heatpump_optimizer.entry_config import EntryConfig
+    await fault_log.async_setup(coord.hass, coord.entry, EntryConfig.from_mapping(_FAULT_LOG_CONFIG))
+
+
+async def _save_fault_log(coord):
+    """Seed every field: two closed rows (one late, one with no code), the tally and an open row."""
+    from heatpump_optimizer import fault_log
+    await _load_fault_log(coord)
+    rec = fault_log._RECORDS[coord.entry]
+    t0 = int(_dt.datetime(2026, 1, 1, 12, 0, 0, tzinfo=_dt.timezone.utc).timestamp())
+    for t, text in ((t0, "E5"), (t0 + 40, None), (t0 + 60, ""), (t0 + 90, "P3, E5")):
+        fault_log.note(rec.log, t, text, late=t == t0 + 40)
+    rec.log.source = "text"
+    await fault_log._save(rec)
+
+
 # The reach arm's wiring: which real loader consumes which store. This is the
 # instrument's configuration, not the seam set — the seam set is Arm 1's AST
 # walk, and the equality check below holds this map to it.
@@ -513,6 +536,7 @@ LOADERS = {
     "debug": _load_debug,
     "off_restore": lambda c: __import__("heatpump_optimizer.off_restore", fromlist=["x"])._armed_record(c.hass, c.entry),
     "room_history": lambda c: (lambda m: m._load(m._record_for(c)))(__import__("heatpump_optimizer.room_record", fromlist=["x"])),
+    "fault_log": _load_fault_log,
 }
 
 R.check(
@@ -1277,6 +1301,7 @@ def _a4_seed(enrich=None) -> dict[str, dict]:
                        "earlier": 20.5})
     run(off._save(held))
     run(_save_room_history(coord))
+    run(_save_fault_log(coord))
     run(_save_notifier(coord))
     run(_save_debug(coord))
     disk = {k: json.loads(v) for k, v in _storage._DISK.items()}
@@ -1959,6 +1984,7 @@ def _a6_savers():
         "debug": _save_debug,
         "off_restore": lambda c: mod("off_restore")._save(mod("off_restore")._RECORDS[c.entry]),
         "room_history": lambda c: mod("room_record")._persist(mod("room_record")._record_for(c)),
+        "fault_log": lambda c: mod("fault_log")._save(mod("fault_log")._RECORDS[c.entry]),
     }
 
 
diff --git a/tests/golden/claimed_drift.txt b/tests/golden/claimed_drift.txt
index 08152a9fb9..8281c3c397 100644
--- a/tests/golden/claimed_drift.txt
+++ b/tests/golden/claimed_drift.txt
@@ -75,6 +75,7 @@ valve_storage_smart_write  # baseline_cost LOWER (129.949 -> 129.251)
 wood_coil  # baseline_cost LOWER (144.781 -> 144.082)
 wood_two_tank  # baseline_cost LOWER (129.949 -> 129.251)
 wood_two_tank_smart_write  # baseline_cost LOWER (129.949 -> 129.251)
+config_flow # R11-OWNER-FAULT-TEXT (#3857): Heat pump telemetry gains the fault-text list (heat_pump_fault_text_entities, a multiple entity selector of sensor, text and input_text), so the plain render, the seeded render and the seed each gain it; the 3 leaves that move are each "present on one side only", ADDED at this head. Float-free and compared exactly, so re-recorded in the committed file (golden.py --record --only config_flow). No plan reads the slot: the other 55 fixtures are byte-identical to the merge base (env_drift.py --all, one environment), which is the null.
 # may-drift: flat_prices -- #1208 polish-every-candidate, owner ruling #1208 comment 208bed25
 # (option (a)): the move's margin is inside the noise band (objective rel
 # -1.2171e-03, deterministic on one box), so which runner sees it move is the
diff --git a/tests/golden/config_flow.json b/tests/golden/config_flow.json
index 10a29606fd..6891d3af31 100644
--- a/tests/golden/config_flow.json
+++ b/tests/golden/config_flow.json
@@ -1078,6 +1078,7 @@
   "heat_pump_dhw_booster_entity": "sensor.seed_heat_pump_dhw_booster_entity",
   "heat_pump_energy_entity": "sensor.seed_heat_pump_energy_entity",
   "heat_pump_fault_entity": "sensor.seed_heat_pump_fault_entity",
+  "heat_pump_fault_text_entities": "sensor.seed_heat_pump_fault_text_entities",
   "heat_pump_heat_energy_entity": "sensor.seed_heat_pump_heat_energy_entity",
   "heat_pump_mode_entity": "sensor.seed_heat_pump_mode_entity",
   "heat_pump_online_entity": "sensor.seed_heat_pump_online_entity",
@@ -2371,6 +2372,15 @@
     "required": "Optional",
     "selector": "EntitySelector"
    },
+   "heat_pump_fault_text_entities": {
+    "config": {
+     "filter": "[{'domain': ['sensor', 'text', 'input_text']}]",
+     "multiple": "True"
+    },
+    "default": "'sensor.seed_heat_pump_fault_text_entities'",
+    "required": "Optional",
+    "selector": "EntitySelector"
+   },
    "heat_pump_mode_entity": {
     "config": {
      "filter": "[{'domain': ['select', 'sensor', 'input_select']}]"
@@ -5126,6 +5136,15 @@
    "required": "Optional",
    "selector": "EntitySelector"
   },
+  "heat_pump_fault_text_entities": {
+   "config": {
+    "filter": "[{'domain': ['sensor', 'text', 'input_text']}]",
+    "multiple": "True"
+   },
+   "default": null,
+   "required": "Optional",
+   "selector": "EntitySelector"
+  },
   "heat_pump_mode_entity": {
    "config": {
     "filter": "[{'domain': ['select', 'sensor', 'input_select']}]"
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_entity_of.RETURN_DEL.3138a791.json b/tests/mutation_ledger/killed_by/config_flow.py/_entity_of.RETURN_DEL.3138a791.json
new file mode 100644
index 0000000000..34ceb3ca0a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_entity_of.RETURN_DEL.3138a791.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_entity_of RETURN_DEL 3138a791",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return selector.EntitySelector({**config, \"multiple\": True} if multiple else config)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.CMP_BOUND.870e4050.json b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.CMP_BOUND.870e4050.json
new file mode 100644
index 0000000000..4d5f72e674
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.CMP_BOUND.870e4050.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_fault_text_errors CMP_BOUND 870e4050",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    too_many = len(submit.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES) or ()) > FAULT_TEXT_ENTITIES_MAX",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`too_many = len(submit.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES) or ()) >= FAULT_TEXT_ENTITIES_MAX`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.RETURN_DEL.d348472e.json b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.RETURN_DEL.d348472e.json
new file mode 100644
index 0000000000..e4e70ad1e9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_fault_text_errors.RETURN_DEL.d348472e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_fault_text_errors RETURN_DEL d348472e",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    return {CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES: \"too_many_fault_text_entities\"} if too_many else {}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json
deleted file mode 100644
index a4e95f9597..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections GUARD_OFF cc44e904",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if bucket:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.e7efd72e.json b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.e7efd72e.json
deleted file mode 100644
index c29595553e..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.e7efd72e.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections GUARD_OFF e7efd72e",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "        if key not in placed:",
-  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.RETURN_DEL.cd4695fb.json b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.RETURN_DEL.cd4695fb.json
deleted file mode 100644
index 26cd2e4983..0000000000
--- a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.RETURN_DEL.cd4695fb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections RETURN_DEL cd4695fb",
-  "killed_by": "tests/config_flow_steps.py",
-  "old": "    return fields",
-  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.25f29392.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.25f29392.json
new file mode 100644
index 0000000000..1eac8baae7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.25f29392.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST 25f29392",
+  "killed_by": "tests/features.py",
+  "old": "TEXT_MAX_CHARS = 160",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`TEXT_MAX_CHARS = 320`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.4b08d3cd.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.4b08d3cd.json
new file mode 100644
index 0000000000..ab9837d610
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.4b08d3cd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST 4b08d3cd",
+  "killed_by": "tests/features.py",
+  "old": "CODES_MAX = 32",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`CODES_MAX = 64`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.84182824.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.84182824.json
new file mode 100644
index 0000000000..497774c0fd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.84182824.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST 84182824",
+  "killed_by": "tests/features.py",
+  "old": "SAVE_MIN_S = 60.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SAVE_MIN_S = 120.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.a2232314.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.a2232314.json
new file mode 100644
index 0000000000..4aed75c889
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.a2232314.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST a2232314",
+  "killed_by": "tests/features.py",
+  "old": "FAULT_LOG_STORE_VERSION = 1",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`FAULT_LOG_STORE_VERSION = 2`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.e8da4cb8.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.e8da4cb8.json
new file mode 100644
index 0000000000..d05b7c89a3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.e8da4cb8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST e8da4cb8",
+  "killed_by": "tests/features.py",
+  "old": "EPISODES_MAX = 200",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`EPISODES_MAX = 400`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.f34207b8.json b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.f34207b8.json
new file mode 100644
index 0000000000..74dc5cc7e1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/@module.CONST.f34207b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:<module> CONST f34207b8",
+  "killed_by": "tests/features.py",
+  "old": "REGISTER_MAX = 0xFFFFFFFF",
+  "reason": "CONST (doubled) on the 32-bit register cap this diff added. The inventory's textual mutant is `REGISTER_MAX = 8589934590xFFFFFFFF`: `_NUM` matches only the leading `0` of a hex literal, so `--pin-killed` reports it SKIP-UNPARSEABLE and never drives it. Applied as the value the operator names, `REGISTER_MAX = 0x1FFFFFFFE`, in a detached worktree at 08fc04fe96: `PYTHONPATH=tests/hastub:tools/devices python3 tools/audit/seat/features_block.py --prelude 'exec(open(OUT).read())' 'from heatpump_optimizer import fault_log as _fl' '# 7: the ring and the tally.'` (OUT from `--emit-prelude`) went from rc=0, 7 passed to rc=1, 1 of 7 failed: `the flag slot: ... null control, the same state on a binary_sensor reads through the flag path` (`str(0x100000000)` read as code `0x100000000` instead of NO_CODE). Null control: the same value written `4294967295` keeps rc=0, 7 passed. Measured 2026-11-25."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.8eff0fa3.json b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.8eff0fa3.json
new file mode 100644
index 0000000000..b1b960dd0c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.8eff0fa3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_apply GUARD_OFF 8eff0fa3",
+  "killed_by": "tests/features.py",
+  "old": "    if not read:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.ce287381.json b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.ce287381.json
new file mode 100644
index 0000000000..d65fa56faf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_apply.GUARD_OFF.ce287381.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_apply GUARD_OFF ce287381",
+  "killed_by": "tests/features.py",
+  "old": "    if note(rec.log, max(s for s, _t in read), read[-1][1], late=late):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_clip.CMP_BOUND.2173cf15.json b/tests/mutation_ledger/killed_by/fault_log.py/_clip.CMP_BOUND.2173cf15.json
new file mode 100644
index 0000000000..edcfebc8c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_clip.CMP_BOUND.2173cf15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_clip CMP_BOUND 2173cf15",
+  "killed_by": "tests/features.py",
+  "old": "    return item if len(item) <= TEXT_MAX_CHARS else \"\u2026\" + item[-TEXT_MAX_CHARS:]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return item if len(item) < TEXT_MAX_CHARS else \"\u2026\" + item[-TEXT_MAX_CHARS:]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_clip.RETURN_DEL.2173cf15.json b/tests/mutation_ledger/killed_by/fault_log.py/_clip.RETURN_DEL.2173cf15.json
new file mode 100644
index 0000000000..3fb79d63aa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_clip.RETURN_DEL.2173cf15.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_clip RETURN_DEL 2173cf15",
+  "killed_by": "tests/features.py",
+  "old": "    return item if len(item) <= TEXT_MAX_CHARS else \"\u2026\" + item[-TEXT_MAX_CHARS:]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.10b8b75c.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.10b8b75c.json
new file mode 100644
index 0000000000..e34fe8b9f8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.10b8b75c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading GUARD_OFF 10b8b75c",
+  "killed_by": "tests/features.py",
+  "old": "    if read is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.a12b4eaf.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.a12b4eaf.json
new file mode 100644
index 0000000000..2cb7e83c0f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.a12b4eaf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading GUARD_OFF a12b4eaf",
+  "killed_by": "tests/features.py",
+  "old": "    if rec.kind == \"text\":",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.c24cbf8a.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.c24cbf8a.json
new file mode 100644
index 0000000000..b7e6cd8c4c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.GUARD_OFF.c24cbf8a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading GUARD_OFF c24cbf8a",
+  "killed_by": "tests/structure.py",
+  "old": "    if not isinstance(raw, str) or raw.strip().lower() in _UNREAD:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.79c7192e.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.79c7192e.json
new file mode 100644
index 0000000000..ba412b6773
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.79c7192e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading RETURN_DEL 79c7192e",
+  "killed_by": "tests/structure.py",
+  "old": "        return (True, code_text([rec.last.get(e) for e in rec.entities]))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.af2be7f3.json b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.af2be7f3.json
new file mode 100644
index 0000000000..f99dd78893
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_reading.RETURN_DEL.af2be7f3.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_reading RETURN_DEL af2be7f3",
+  "killed_by": "tests/features.py",
+  "old": "    return (True, read[1])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.a6134d1e.json b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.a6134d1e.json
new file mode 100644
index 0000000000..8242c336ba
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.a6134d1e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_release GUARD_OFF a6134d1e",
+  "killed_by": "tests/features.py",
+  "old": "    if rec.closed:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.f2dc0db1.json b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.f2dc0db1.json
new file mode 100644
index 0000000000..5634949abb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_release.GUARD_OFF.f2dc0db1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_release GUARD_OFF f2dc0db1",
+  "killed_by": "tests/features.py",
+  "old": "        if release is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_release.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/fault_log.py/_release.RETURN_DEL.80a0007e.json
new file mode 100644
index 0000000000..31b9dd4a69
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_release.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_release RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_request_save.CMP_BOUND.538cf5fd.json b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.CMP_BOUND.538cf5fd.json
new file mode 100644
index 0000000000..b1bcd6814b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.CMP_BOUND.538cf5fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_request_save CMP_BOUND 538cf5fd",
+  "killed_by": "tests/features.py",
+  "old": "    if wait <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if wait < 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.538cf5fd.json b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.538cf5fd.json
new file mode 100644
index 0000000000..6aa5e0e961
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.538cf5fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_request_save GUARD_OFF 538cf5fd",
+  "killed_by": "tests/features.py",
+  "old": "    if wait <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.b244e192.json b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.b244e192.json
new file mode 100644
index 0000000000..162894350e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_request_save.GUARD_OFF.b244e192.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_request_save GUARD_OFF b244e192",
+  "killed_by": "tests/features.py",
+  "old": "    if rec.closed or rec.timer is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_seconds.RETURN_DEL.adc95fe0.json b/tests/mutation_ledger/killed_by/fault_log.py/_seconds.RETURN_DEL.adc95fe0.json
new file mode 100644
index 0000000000..e03ef0a015
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_seconds.RETURN_DEL.adc95fe0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_seconds RETURN_DEL adc95fe0",
+  "killed_by": "tests/features.py",
+  "old": "    return int(stamp.timestamp()) if isinstance(stamp, datetime) else _now_s()",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_tally.CMP_BOUND.4c126e21.json b/tests/mutation_ledger/killed_by/fault_log.py/_tally.CMP_BOUND.4c126e21.json
new file mode 100644
index 0000000000..bf7375e39b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_tally.CMP_BOUND.4c126e21.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_tally CMP_BOUND 4c126e21",
+  "killed_by": "tests/features.py",
+  "old": "    key = text if text in log.codes or len(log.codes) < CODES_MAX else OTHER",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`key = text if text in log.codes or len(log.codes) <= CODES_MAX else OTHER`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/_tally.GUARD_OFF.e6901531.json b/tests/mutation_ledger/killed_by/fault_log.py/_tally.GUARD_OFF.e6901531.json
new file mode 100644
index 0000000000..51a11e0b87
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/_tally.GUARD_OFF.e6901531.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:_tally GUARD_OFF e6901531",
+  "killed_by": "tests/features.py",
+  "old": "    if text == NO_CODE:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_close.BOOLOP.91a18c0a.json b/tests/mutation_ledger/killed_by/fault_log.py/async_close.BOOLOP.91a18c0a.json
new file mode 100644
index 0000000000..a22ae7204d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_close.BOOLOP.91a18c0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_close BOOLOP 91a18c0a",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if rec is not None and _release(rec):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if rec is not None or _release(rec):`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_close.GUARD_OFF.91a18c0a.json b/tests/mutation_ledger/killed_by/fault_log.py/async_close.GUARD_OFF.91a18c0a.json
new file mode 100644
index 0000000000..514c4a6e72
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_close.GUARD_OFF.91a18c0a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_close GUARD_OFF 91a18c0a",
+  "killed_by": "tests/features.py",
+  "old": "    if rec is not None and _release(rec):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup.BOOLOP.735d6589.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.BOOLOP.735d6589.json
new file mode 100644
index 0000000000..38919a7726
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.BOOLOP.735d6589.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup BOOLOP 735d6589",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if old is not None and old.ending is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if old is not None or old.ending is not None:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.57b55919.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.57b55919.json
new file mode 100644
index 0000000000..2b2b1a6dff
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.57b55919.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup GUARD_OFF 57b55919",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if source is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.735d6589.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.735d6589.json
new file mode 100644
index 0000000000..353f9dfbb2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup.GUARD_OFF.735d6589.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup GUARD_OFF 735d6589",
+  "killed_by": "tests/features.py",
+  "old": "    if old is not None and old.ending is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup._changed.GUARD_OFF.16b948e4.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._changed.GUARD_OFF.16b948e4.json
new file mode 100644
index 0000000000..e9bc96c820
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._changed.GUARD_OFF.16b948e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup._changed GUARD_OFF 16b948e4",
+  "killed_by": "tests/features.py",
+  "old": "        if not rec.closed:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/async_setup._ended.GUARD_OFF.bacd1d14.json b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._ended.GUARD_OFF.bacd1d14.json
new file mode 100644
index 0000000000..ca0352edef
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/async_setup._ended.GUARD_OFF.bacd1d14.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:async_setup._ended GUARD_OFF bacd1d14",
+  "killed_by": "tests/features.py",
+  "old": "        if _release(rec):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.6c26d72e.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.6c26d72e.json
new file mode 100644
index 0000000000..06183ff102
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.6c26d72e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text BOOLOP 6c26d72e",
+  "killed_by": "tests/features.py",
+  "old": "        if kept and length + add > TEXT_MAX_CHARS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if kept or length + add > TEXT_MAX_CHARS:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.7ab93919.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.7ab93919.json
new file mode 100644
index 0000000000..3845bdeda2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.BOOLOP.7ab93919.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text BOOLOP 7ab93919",
+  "killed_by": "tests/features.py",
+  "old": "        if state is not None and state.strip().casefold() not in HEALTHY",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if state is not None or state.strip().casefold() not in HEALTHY`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.CMP_BOUND.6c26d72e.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.CMP_BOUND.6c26d72e.json
new file mode 100644
index 0000000000..dcfe903d1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.CMP_BOUND.6c26d72e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text CMP_BOUND 6c26d72e",
+  "killed_by": "tests/features.py",
+  "old": "        if kept and length + add > TEXT_MAX_CHARS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if kept and length + add >= TEXT_MAX_CHARS:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.1cb525c8.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.1cb525c8.json
new file mode 100644
index 0000000000..a3cbb1e4e9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.1cb525c8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text GUARD_OFF 1cb525c8",
+  "killed_by": "tests/features.py",
+  "old": "    if not items:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.6c26d72e.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.6c26d72e.json
new file mode 100644
index 0000000000..e9982e43ee
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.GUARD_OFF.6c26d72e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text GUARD_OFF 6c26d72e",
+  "killed_by": "tests/features.py",
+  "old": "        if kept and length + add > TEXT_MAX_CHARS:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/code_text.RETURN_DEL.7b6f84a2.json b/tests/mutation_ledger/killed_by/fault_log.py/code_text.RETURN_DEL.7b6f84a2.json
new file mode 100644
index 0000000000..d9b93fc539
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/code_text.RETURN_DEL.7b6f84a2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:code_text RETURN_DEL 7b6f84a2",
+  "killed_by": "tests/features.py",
+  "old": "    return \", \".join(kept) + (f\" +{dropped}\" if dropped else \"\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.CLAMP_DROP.392df3a8.json b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.CLAMP_DROP.392df3a8.json
new file mode 100644
index 0000000000..88a41d3880
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.CLAMP_DROP.392df3a8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:diagnostics_view CLAMP_DROP 392df3a8",
+  "killed_by": "tests/features.py",
+  "old": "            \"start\": _iso(log.open[0]), \"seconds\": max(0, now_s - log.open[0]),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`\"start\": _iso(log.open[0]), \"seconds\": (0),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.GUARD_OFF.44ed6e87.json b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.GUARD_OFF.44ed6e87.json
new file mode 100644
index 0000000000..7a369efa03
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/diagnostics_view.GUARD_OFF.44ed6e87.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:diagnostics_view GUARD_OFF 44ed6e87",
+  "killed_by": "tests/features.py",
+  "old": "    if rec is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.BOOLOP.bba5c3da.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.BOOLOP.bba5c3da.json
new file mode 100644
index 0000000000..4b17fb53ad
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.BOOLOP.bba5c3da.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text BOOLOP bba5c3da",
+  "killed_by": "tests/features.py",
+  "old": "    source = \"bitmap\" if number is not None and number.is_integer() else \"flag\"",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`source = \"bitmap\" if number is not None or number.is_integer() else \"flag\"`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.1d76026d.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.1d76026d.json
new file mode 100644
index 0000000000..db2e7d4e11
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.1d76026d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text GUARD_OFF 1d76026d",
+  "killed_by": "tests/features.py",
+  "old": "    if flag is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.385ce0f0.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.385ce0f0.json
new file mode 100644
index 0000000000..0179a1b966
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.385ce0f0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text GUARD_OFF 385ce0f0",
+  "killed_by": "tests/features.py",
+  "old": "    if not flag:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.4ea770b7.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.4ea770b7.json
new file mode 100644
index 0000000000..a0c431998d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.GUARD_OFF.4ea770b7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text GUARD_OFF 4ea770b7",
+  "killed_by": "tests/structure.py",
+  "old": "    if source == \"bitmap\" and number is not None and 0 < number <= REGISTER_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/flag_text.RETURN_DEL.6dd50371.json b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.RETURN_DEL.6dd50371.json
new file mode 100644
index 0000000000..caf751cb4a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/flag_text.RETURN_DEL.6dd50371.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text RETURN_DEL 6dd50371",
+  "killed_by": "tests/features.py",
+  "old": "    return (source, NO_CODE)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/loaded.BOOLOP.77a723dd.json b/tests/mutation_ledger/killed_by/fault_log.py/loaded.BOOLOP.77a723dd.json
new file mode 100644
index 0000000000..1547163196
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/loaded.BOOLOP.77a723dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:loaded BOOLOP 77a723dd",
+  "killed_by": "tests/features.py",
+  "old": "        open=list(opened) if isinstance(opened, list) and len(opened) == 2 else None,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`open=list(opened) if isinstance(opened, list) or len(opened) == 2 else None,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/loaded.GUARD_OFF.821696d2.json b/tests/mutation_ledger/killed_by/fault_log.py/loaded.GUARD_OFF.821696d2.json
new file mode 100644
index 0000000000..9e87f310c7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/loaded.GUARD_OFF.821696d2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:loaded GUARD_OFF 821696d2",
+  "killed_by": "tests/structure.py",
+  "old": "    if not isinstance(raw, Mapping) or not raw or not admitted(\"fault_log\", raw):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.60e27395.json b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.60e27395.json
new file mode 100644
index 0000000000..510b870f05
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.60e27395.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note BOOLOP 60e27395",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is not None and log.open[1] == text:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if log.open is not None or log.open[1] == text:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.cf6b21fd.json b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.cf6b21fd.json
new file mode 100644
index 0000000000..3fbb1a95b4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.BOOLOP.cf6b21fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note BOOLOP cf6b21fd",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is None and text is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if log.open is None or text is None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.CLAMP_DROP.240a7557.json b/tests/mutation_ledger/killed_by/fault_log.py/note.CLAMP_DROP.240a7557.json
new file mode 100644
index 0000000000..848f4a3776
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.CLAMP_DROP.240a7557.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note CLAMP_DROP 240a7557",
+  "killed_by": "tests/features.py",
+  "old": "        end_s = max(now_s, start_s)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`end_s = (now_s)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.CMP_BOUND.45ba8896.json b/tests/mutation_ledger/killed_by/fault_log.py/note.CMP_BOUND.45ba8896.json
new file mode 100644
index 0000000000..5263c16564
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.CMP_BOUND.45ba8896.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note CMP_BOUND 45ba8896",
+  "killed_by": "tests/features.py",
+  "old": "        if len(log.episodes) > EPISODES_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if len(log.episodes) >= EPISODES_MAX:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.2a982e58.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.2a982e58.json
new file mode 100644
index 0000000000..2d153b97dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.2a982e58.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 2a982e58",
+  "killed_by": "tests/features.py",
+  "old": "    if text is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.45ba8896.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.45ba8896.json
new file mode 100644
index 0000000000..67ba0eff61
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.45ba8896.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 45ba8896",
+  "killed_by": "tests/features.py",
+  "old": "        if len(log.episodes) > EPISODES_MAX:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.60e27395.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.60e27395.json
new file mode 100644
index 0000000000..4e53de6730
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.60e27395.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 60e27395",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is not None and log.open[1] == text:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.9aa017ad.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.9aa017ad.json
new file mode 100644
index 0000000000..f88aaa2888
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.9aa017ad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF 9aa017ad",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.cf6b21fd.json b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.cf6b21fd.json
new file mode 100644
index 0000000000..3c9318eeed
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.GUARD_OFF.cf6b21fd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note GUARD_OFF cf6b21fd",
+  "killed_by": "tests/features.py",
+  "old": "    if log.open is None and text is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/note.RETURN_DEL.80a0007e.json b/tests/mutation_ledger/killed_by/fault_log.py/note.RETURN_DEL.80a0007e.json
new file mode 100644
index 0000000000..9969d93b66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/note.RETURN_DEL.80a0007e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:note RETURN_DEL 80a0007e",
+  "killed_by": "tests/features.py",
+  "old": "    return True",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/sources.GUARD_OFF.91f3668a.json b/tests/mutation_ledger/killed_by/fault_log.py/sources.GUARD_OFF.91f3668a.json
new file mode 100644
index 0000000000..ed55943400
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/sources.GUARD_OFF.91f3668a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:sources GUARD_OFF 91f3668a",
+  "killed_by": "tests/features.py",
+  "old": "    if members:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/fault_log.py/sources.RETURN_DEL.a5bac6c6.json b/tests/mutation_ledger/killed_by/fault_log.py/sources.RETURN_DEL.a5bac6c6.json
new file mode 100644
index 0000000000..3e57f2f8b6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/fault_log.py/sources.RETURN_DEL.a5bac6c6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:sources RETURN_DEL a5bac6c6",
+  "killed_by": "tests/features.py",
+  "old": "    return (\"flag\", [flag]) if flag else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.BOOLOP.0d125c94.json b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.BOOLOP.0d125c94.json
new file mode 100644
index 0000000000..9fd3d1b00f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.BOOLOP.0d125c94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/modbus_prefill.py:infer BOOLOP 0d125c94",
+  "killed_by": "tests/features.py",
+  "old": "    if listed is not None and not current.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if listed is not None or not current.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.GUARD_OFF.0d125c94.json b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.GUARD_OFF.0d125c94.json
new file mode 100644
index 0000000000..eecb39c709
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/modbus_prefill.py/infer.GUARD_OFF.0d125c94.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/modbus_prefill.py:infer GUARD_OFF 0d125c94",
+  "killed_by": "tests/features.py",
+  "old": "    if listed is not None and not current.get(CONF_HEAT_PUMP_FAULT_TEXT_ENTITIES):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/survivor_triage/fault_log.py/flag_text.CMP_BOUND.4ea770b7.json b/tests/mutation_ledger/survivor_triage/fault_log.py/flag_text.CMP_BOUND.4ea770b7.json
new file mode 100644
index 0000000000..6ce7aa38d1
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/fault_log.py/flag_text.CMP_BOUND.4ea770b7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/fault_log.py:flag_text CMP_BOUND 4ea770b7",
+  "old": "    if source == \"bitmap\" and number is not None and 0 < number <= REGISTER_MAX:",
+  "reason": "Equivalent (CMP_BOUND, `0 < number` -> `0 <= number`): the line is reached only on a reading parse_bool took as a fault, and parse_bool reads a number as a fault exactly when it is non-zero, so number is never 0 here and the two bounds pick the same branch on every input. Measured by the R11-OWNER-FAULT-TEXT fixer's mutant_run.py drive of the diff's fault_log.py mutants over the fault-record block of tests/features.py: SURVIVED rc=0; the same block kills the bound's other side (`1 < number`, by the reading 1 giving 0x0001) and the register cap (`0 < number` alone, by 2**32 giving no code).",
+  "verdict": "equivalent"
+}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 74ef86c8a0..1a545fd67f 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -16,7 +16,7 @@
  "max_method_loc": 373,
  "methods_over_150": 14,
  "methods_over_200": 7,
- "module_excess_loc": 21753,
+ "module_excess_loc": 21745,
  "name_kept_members": 38,
  "recorded_at": "d3d66c40408e76351ffc528686353cadf815a05c",
  "seam_cut_total": 413,

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
