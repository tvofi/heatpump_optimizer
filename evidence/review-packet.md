# Review packet #3564
head: a0784de911887f5690a6183123c556757cd63fe7
base: 513a07dfdc0daf09a054826974dbb64bfea9de27

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=132419456836 success
arm id=132418764786 skipped
budget-raise-gate / budget-raise-gate id=132419456936 queued
cancel-superseded id=132418767826 queued
codeql / Analyze (actions) id=132419456727 queued
codeql / Analyze (javascript-typescript) id=132419456709 queued
codeql / Analyze (python) id=132419456700 in_progress
governance / delivery-status id=132419456873 queued
governance / delivery-status-publish id=132419457528 skipped
governance / env-matrix id=132419456610 queued
governance / instrument-self-tests id=132419456549 queued
governance / policy-docs id=132419456640 queued
governance / record id=132419457793 skipped
governance / wave-script id=132419456880 queued
hassfest / hassfest id=132419456634 in_progress
kernel-points id=132419457786 skipped
prelude id=132418767810 queued
refresh id=132418767701 queued
tests / briefs id=132419456730 success
tests / closure-scope id=132419456742 queued
tests / mutation id=132419456720 in_progress
tests / nightly-status id=132419456764 queued
validate / validate-hacs id=132419456680 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 132419456549: queued has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
NOTE body item 2de47db2: R11-INTAKE-R10-RESIDUE
NOTE body item 9ae2be30: R11-INTAKE-R10-RESIDUE
NOTE body item 55051373: R11-INTAKE-R10-RESIDUE
NOTE body item 4ab03548: R11-INTAKE-R10-RESIDUE
NOTE body item af528396: R11-INTAKE-R10-RESIDUE
NOTE body item 31878861: R11-INTAKE-R10-RESIDUE
NOTE body item 734b6d33: R11-INTAKE-R10-RESIDUE
NOTE body item 452440fb: R11-INTAKE-R10-RESIDUE
NOTE body item 86aa4096: R11-INTAKE-R10-RESIDUE
NOTE body item a64a0285: R11-INTAKE-R10-RESIDUE
NOTE body item b30f48ba: R11-INTAKE-R10-RESIDUE
NOTE body item 6f36db0c: R11-INTAKE-R10-RESIDUE
NOTE body item bb5336e8: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 13 finding item(s): 13 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 dev/audit/rounds/round10/D6/flow_claims.py enumerate | tail -4
             `dev/audit/rounds/round10/D6/flow_claims.py` is in the tree at this head
  ok         python3 dev/audit/rounds/round10/D6/flow_claims.py distinct | tail -1
             `dev/audit/rounds/round10/D6/flow_claims.py` is in the tree at this head
  unverified python3 -c "import json; print(json.load(open('dev/audit/rounds/round10/D6/flow-claims.json'))['verdicts'])"
             python3 runs an inline script rather than a file
  unverified git diff --stat origin/main...HEAD -- custom_components/heatpump_optimizer/strings.json custom_components/heatpump_optimizer/translations/
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head
  ok         GOLDEN_MODE=drift python3 tests/golden.py
             `tests/golden.py` is in the tree at this head
  ok         node tests/card.mjs
             `tests/card.mjs` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git merge-tree --write-tree origin/main HEAD
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 6 resolved, 3 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
similarity index 60%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
index 3c3cb57df3..7674632b2b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 59013da4",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 87a4cba9",
   "killed_by": "tests/features.py",
-  "old": "        if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "        if held.written or held.retry or held.space_before is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
new file mode 100644
index 0000000000..d52a0f3f66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space GUARD_OFF bc2b348d",
+  "killed_by": "tests/features.py",
+  "old": "    if own:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
index f29be90584..eedc551b94 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL cbe69d47",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL ee5d5b70",
   "killed_by": "tests/features.py",
-  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER, baseline_c=baseline)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
index d5ce21b72b..6150d6a294 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP 605f504a",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP dd8cf122",
   "killed_by": "tests/guard_pins.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity, now)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
index 9a74fc5f22..febd8f790b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL 605f504a",
-  "killed_by": "tests/structure.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL dd8cf122",
+  "killed_by": "tests/features.py",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
new file mode 100644
index 0000000000..1ef3907eac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_own_space_write RETURN_DEL 98fa5cc9",
+  "killed_by": "tests/features.py",
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}


## Review scope: delta (later round over the reviewed head d6a7b00bba95068c5236805aa0a740b792d0d954)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at d6a7b00bba95068c5236805aa0a740b792d0d954
Fix review: merge d6a7b00bba95068c5236805aa0a740b792d0d954

bus-nonce: fca124fe4cbaa8cb902b9d9bdcdc53af
pending-ci: gate

## Findings

- Still open from round 1: a conflict with #3561 (a02783d4, not yet on main). It is the same adjacent-line edit in strings.json, en.json, sv.json and de.json. Round 1 measured it and resolved it by keeping both lines. This delta does not change it. Carry: dismissed: a hand resolution the orchestrator makes at the second merge, both sides kept; measured in round 1
- Still open from round 1: translations are not pinned. The written-slot arm reads only strings.json. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: the written-slot set (`pump_arbiter._entities`) is narrower than the set of entities that are written. `heat_pump_switch_entity` and `dhw_disinfection_switch_entity` are not covered. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: two record rows cite strings.json `menu_options` rather than the code that builds the menu. The delta does not change this. Carry: R11-INTAKE-R10-RESIDUE
- Still open from round 1: the `pump_duty_mode` text says "toward 5 °C", but the value is a temperature difference and should be in K. It predates the branch. Carry: R11-INTAKE-R10-RESIDUE
- Main added two hysteresis data_description texts that flow-claims.json does not cover. Its record is judged at merge base 154dbb4c. These texts are main's reviewed work, not this PR's. Carry: R11-INTAKE-R10-RESIDUE

## Evidence

- Scope: a delta round over the reviewed head 9a524d703f3a25325c71f1fe888a35ab53147189. The review packet's scope line reads `delta`, and I rendered the packet at this head (ev/review-packet.md). The previous verdict (verdict/3564 at 9cdcdd2c) blocked with `ci-red` for one reason only: `tests/features.py`'s weekend-clock check, which was red at main 50373173 as well.
- RESULT delta is main's content only: head d6a7b00b has one branch-only commit. It is a merge with parents 9a524d70 and c987209c, and c987209c is current origin/main (#3578, fix/r10-hotfix-features-weekend-clock). `git merge-tree --write-tree 9a524d70 c987209c` writes tree d3323dcc3020fdce49ebbc301e2bee2538e40154, which equals the head's tree. `git show --remerge-diff d6a7b00b` shows no resolution hunks. The merge is automatic, with no branch-authored change (ev/auto_merge_check.txt). `git diff --stat 9a524d70 d6a7b00b` (12 files, +144/-20) equals main's own diff from the merge base to c987209c (ev/delta_stat.txt). It includes the tests/features.py fix (+3/-1).
- RESULT review_carry: `review_carry.py 9a524d70 d6a7b00b` prints `CARRY`, rc 0: "0 of 1 branch-only commit(s) are non-merge" (ev/review_carry.txt).
- RESULT prior findings stay resolved: the sorted +/- lines of `git diff 50373173 9a524d70 -- custom_components` and `git diff origin/main d6a7b00b -- custom_components` are identical, so the production patch is the one reviewed. The net diff against main is the same 10 files as before: strings/de/en 112 lines each and sv 110, flow-claims.{json,md,py}, delivery/3564.md, closures.json and doc_claims.py. VERSION, the manifest, RELEASE_NOTES.md and both claim files do not differ from main (ev/patch_identity.txt). No production delta, so no widening (fix-review.md step 12).
- Merge with origin/main c987209c: `git merge-tree --write-tree origin/main d6a7b00b` rc 0 (ev/merge_tree_main.txt).
- Not re-derived locally: `tests/features.py` cannot run in this container because `homeassistant` is not installed (ev/features_local_unrunnable.txt). Whether the weekend-clock check is green comes from CI's gate at this head (below).
- `tests / nightly-status` shows failure in the packet's check list. It is not in the `owed-reds` set (ev/owed_reds.txt), so it is neither answered nor a block.
- CI at this head: I polled `merge_train.py classify` from 03:07 to 03:37 UTC, 75 s apart, and every run printed `WAIT d6a7b00b… pending: gate red: none`, rc 3 (ev/classify_poll.txt). Nothing was red. The review is otherwise a merge, so I return it with the `pending-ci: gate` line, for the relay to post once the gate is green at this head.

## Delta diff: git diff d6a7b00bba95068c5236805aa0a740b792d0d954 a0784de911887f5690a6183123c556757cd63fe7
diff --git a/RELEASE_NOTES.md b/RELEASE_NOTES.md
index 3bb0dfe9d3..2536024d45 100644
--- a/RELEASE_NOTES.md
+++ b/RELEASE_NOTES.md
@@ -127,6 +127,8 @@ Built from outside pull request #3439 by Bankaifan, with thanks. With Pump duty
 
 Turning the optimizer off, and every unload, now writes the space set-point that Pump duty control had changed back to the person's own baseline. The baseline is saved before the first write, a value the person sets between writes becomes the new baseline, and the restored value is kept within the entity's range and step. This replaces the earlier behaviour where off wrote nothing for that set-point. `docs/configuration.md` describes it under Pump duty control.
 
+Upgrade note, added 2026-11-13: after an upgrade from v7.1.11 or earlier, the space set-point is not written until it has been set once at the pump or in Home Assistant. Under Pump duty control this can leave the pump at its last idle set-point (25 °C on a flow set-point), boost included. Until the release that follows v7.1.15, set the set-point entity once by hand to release it; from that release the optimizer releases it on its own.
+
 ### #3469 Optional controller limits bound the water set-point (R10-WATER-SETPOINT-FEEDBACK, part 3)
 
 Two new optional entity options on the options page that carries the space set-point unit, shown for a water unit, name the controller's own lower and upper limit sensors for the written set-point. An upper limit that leaves no room above the off value for a heating write is ignored, so a placeholder or misplaced sensor can no longer make the loop write the off value or lower. The options have labels in every translation and in the card.
diff --git a/custom_components/heatpump_optimizer/away.py b/custom_components/heatpump_optimizer/away.py
index 9fad06b00d..375ced98bb 100644
--- a/custom_components/heatpump_optimizer/away.py
+++ b/custom_components/heatpump_optimizer/away.py
@@ -1,8 +1,8 @@
 """Away / holiday mode with deadline-driven recovery.
 
 A week away is the single largest saving a heating system can offer: a deep
-setback plus hot water suppressed entirely, except for a legionella cycle timed
-to complete before return.
+setback plus hot water held only at its away minimum; the legionella cycle
+keeps its usual interval.
 
 What makes this more than an ``input_number`` is the **return time**. Knowing
 when the house must be comfortable again lets the optimizer buy the recovery
@@ -73,11 +73,6 @@ class AwayConfig:
     #: Setback targets while away.
     away_temperature: float = 16.0
     away_dhw_min_temperature: float = 20.0
-    #: Whether to keep the anti-legionella cycle running while away. Kept on by
-    #: default: a tank sitting lukewarm for a week is exactly the condition the
-    #: cycle exists for, and it is much cheaper to run it in a chosen cheap
-    #: hour than to arrive home to an overdue one.
-    legionella_before_return: bool = True
 
 
 @dataclass
diff --git a/custom_components/heatpump_optimizer/off_restore.py b/custom_components/heatpump_optimizer/off_restore.py
index 6df838c235..be47b192b7 100644
--- a/custom_components/heatpump_optimizer/off_restore.py
+++ b/custom_components/heatpump_optimizer/off_restore.py
@@ -153,12 +153,16 @@ async def _save(held: _Held) -> None:
         _LOGGER.debug("Could not save the off-restore store: %s", err)
 
 
-async def async_arm(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, key: str) -> bool:
+async def async_arm(
+    hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, config: Any, key: str,
+    *, baseline_c: float | None = None,
+) -> bool:
     """Before a write by consumer ``key``: arm its restore; False refuses the write.
 
     The first arm captures the baseline of a consumer with no ``neutral`` and
-    persists it with its entity; a later arm, in this run or after a restart,
-    keeps it. An unreadable baseline refuses the write: what it would restore
+    persists it with its entity: ``baseline_c`` where the consumer knows the
+    reading is no baseline (its own last write), else the reading. A later
+    arm, in this run or after a restart, keeps it. An unreadable baseline refuses the write: what it would restore
     is unknown. A baseline entry for another entity, or under a neutral
     restorer, is restored first (rule R), and a failure refuses the write; a
     neutral entry under a baseline restorer is dropped unwritten, so a neutral
@@ -181,7 +185,8 @@ async def async_arm(hass: HomeAssistant, entry: HeatPumpOptimizerConfigEntry, co
             return False  # latched, still armed: nothing to save
     baseline = None
     if restorer.neutral is None:
-        baseline = restorer.baseline_of(hass, restorer.entity_id) if restorer.baseline_of else None
+        baseline = baseline_c if baseline_c is not None else (
+            restorer.baseline_of(hass, restorer.entity_id) if restorer.baseline_of else None)
         if log_held(entry, f"off_restore_baseline_{key}", baseline is None,
                     "No baseline readable from %s: not written, nothing to restore it to",
                     restorer.entity_id):
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index e3afe6c67d..4444eba2ea 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -115,7 +115,8 @@ write the arbiter arms :mod:`off_restore` (:data:`CONSUMER`), which captures
 the entity's reading, persisted, as the person's baseline and writes it back
 on the change into Off and on every unload, a reload and a Home Assistant
 stop included (the hook's one rule). A reading equal to the arbiter's own
-last write is never captured (:func:`_arm_space`). What a person sets while
+last write is never captured: the baseline row's own target is, and the write
+is sent (:func:`_arm_space`). What a person sets while
 the optimizer is off is captured at the next arm; one set between writes is
 adopted as the baseline (:func:`_edited`), bounded to the entity's own
 range, and, while active, still written over. The mode, the hot-water set-point and the silent switch are not
@@ -1055,7 +1056,7 @@ def _note_sent(held: ArbiterState, rec: FeedbackRun, out: float | None, base: fl
     moves at all drops the record, and an equal one is still not sent. The
     dropped record is the run's ``prev_c``, the bracket :func:`_cut_of`
     reads, and ``held.dropped`` until a restore ends it: it is still the
-    arbiter's last write, which the off restore's own-write refusal reads
+    arbiter's last write, which the off restore's own-write check reads
     (:func:`_arm_space`) after the run that dropped it has ended.
     """
     recorded = held.written.get("space_setpoint")
@@ -1460,7 +1461,24 @@ def _not_held(coord: Any, held: ArbiterState, slot: str, detail: str, now: datet
 
 
 def _forget(held: ArbiterState) -> None:
-    held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None
+    """Let go of the pump: every record goes but the arbiter's own last space write.
+
+    That value stays on ``held.dropped`` until a restore replaces it on the
+    entity (:func:`_space_restored`): with no baseline armed, Off writes
+    nothing there, so the entity still reads the optimizer's number, and the
+    arm after On must not capture it as the person's (:func:`_arm_space`).
+    """
+    own = _own_space_write(held)
+    held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None
+    held.dropped = {} if own is None else {"space_setpoint": own}
+
+
+def _own_space_write(held: ArbiterState) -> Any:
+    """The arbiter's own last space write, or ``None``: its record, else the
+    one a loop move dropped to be sent (:func:`_note_sent`), which
+    ``held.dropped`` keeps across the run's end and an Off (:func:`_forget`)."""
+    record = held.written.get("space_setpoint")
+    return record[0] if record is not None else held.dropped.get("space_setpoint")
 
 
 def _service(slot: str, state: Any, value: Any) -> tuple[str, dict[str, Any]] | None:
@@ -1591,33 +1609,34 @@ async def _held_back(
         return True
     if slot == "mode" and entity.split(".", 1)[0] not in _MODE_DOMAINS:
         return True
-    return slot == "space_setpoint" and not await _arm_space(inp, entry, held, entity)
+    return slot == "space_setpoint" and not await _arm_space(inp, entry, held, entity, now)
 
 
-async def _arm_space(inp: ArbiterInputs, entry: Any, held: ArbiterState, entity: str) -> bool:
+async def _arm_space(inp: ArbiterInputs, entry: Any, held: ArbiterState, entity: str, now: datetime) -> bool:
     """Arm the off restore before a space write; False holds the write.
 
     The first arm captures the entity's reading as the baseline off restores
     (:mod:`off_restore`), but never one equal to the arbiter's own last write
     -- a record from before this restore existed: that number is the
-    optimizer's, not the person's, so the write is held, latched, until the
-    controller reads anything else.
+    optimizer's, not the person's. The baseline captured in its place is the
+    baseline row's own space target (:func:`_space_target` with no duty), the
+    value the arbiter holds when the plan is not in charge, and the write is
+    sent. It used to be held until the controller read anything else, which
+    on an upgrade held every space write, a boost's included, with the pump
+    left on the optimizer's last gate (R10-HOTFIX-FLOW-SETPOINT-STUCK).
     """
     armed = await off_restore.async_armed_entry(inp.hass, entry, CONSUMER)
     reading = read_setpoint(inp.hass, entity)
-    record = held.written.get("space_setpoint")
-    # A loop move dropped the record to be sent (_note_sent); held.dropped
-    # keeps it across the run's end, which the loop resets on any stop.
-    last = record[0] if record is not None else held.dropped.get("space_setpoint")
+    last = _own_space_write(held)
     own = (armed is None or armed["entity_id"] != entity) and last is not None \
         and reading is not None and not _differs("space_setpoint", reading, last)
-    if log_held(inp.hass, f"space_baseline_own:{entity}", own,
-                "Pump duty: %s reads %s, the optimizer's own last write, which is no "
-                "baseline to restore on off; not writing it until it is set at the controller",
-                entity, reading):
-        return False
+    baseline = None
+    if own:
+        baseline = _space_target(inp, inp.plan, now, None)
+        _LOGGER.info("Pump duty: %s reads %s, the optimizer's own last write; turning the "
+                     "optimizer off restores %s instead", entity, reading, baseline)
     held.space_before = reading
-    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER)
+    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER, baseline_c=baseline)
 
 
 async def _command(coord: Any, inp: ArbiterInputs, command: PumpCommand, now: datetime) -> None:
@@ -1759,7 +1778,7 @@ async def _arbitrate(coord: Any, held: ArbiterState, inp: ArbiterInputs, mode: s
         # person's the moment the optimizer lets go of it. The space
         # set-point's baseline is restored by off_restore (tvofi, 2026-11-07,
         # "Arbiter too"), before this pass; its record is dropped here.
-        if held.written or held.retry or held.dropped or held.space_before is not None:
+        if held.written or held.retry or held.space_before is not None:
             # A pending retry dies with control, and so does its warning.
             _forget(held)
             issues.clear_issue(coord.hass, ISSUE_IGNORED)
diff --git a/custom_components/heatpump_optimizer/strings.json b/custom_components/heatpump_optimizer/strings.json
index 1e09b13a40..1f6dc0c71e 100644
--- a/custom_components/heatpump_optimizer/strings.json
+++ b/custom_components/heatpump_optimizer/strings.json
@@ -12,7 +12,7 @@
           "weather_entity": "Weather forecast"
         },
         "data_description": {
-          "name": "The name of this integration entry in Home Assistant's list of integrations. It is not part of entity names: they all start with \"Heat Pump Optimizer\".",
+          "name": "The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer.",
           "price_source": "Tibber uses your API token. Entity reads a Home Assistant price sensor such as Nord Pool.",
           "tibber_token": "Used to read your hourly electricity prices. Create one at developer.tibber.com. Leave as-is unless it has changed. Not required when the price source is an entity.",
           "price_entity": "Required when the price source is an entity. Typical attributes are raw_today and raw_tomorrow.",
@@ -592,8 +592,8 @@
             "data_description": {
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
-              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit tells the optimizer what the number means: with Pump duty control at Control it writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
+              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Use this instead if your compensation follows the spot price.",
           "pv_enabled": "Lets the plan run the heat pump on your own surplus instead of selling it for less than bought power costs.",
           "pv_peak_kw": "The array's rated peak output. Used to scale the production forecast.",
-          "pv_production_entity": "Optional. A live production sensor replaces the forecast for the current step with the measured output (capped at the installed capacity); later hours stay on the forecast from solar irradiance.",
+          "pv_production_entity": "Optional. A live production sensor replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "A person, device tracker, calendar, or occupancy sensor. The Plan-page toggle wins until it is turned off. A person being 'not home' still means away when the toggle is off.",
           "holiday_calendar_entity": "When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active.",
-          "away_dhw_min_temperature": "The anti-legionella cycle still runs, on its usual schedule; it is not timed to your return.",
+          "away_dhw_min_temperature": "The anti-legionella cycle still runs on its usual interval; it is not timed to your return.",
           "away_temperature": "The hold temperature while away. Low enough to save, high enough to protect the house and its plumbing.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observe reads the switch and never writes it. Control turns it on when an anti-legionella cycle starts and off when that cycle ends, but never turns it on while the pump's mode makes no hot water. It only turns off a switch it turned on itself: a switch that was already on when the cycle began is left alone. One limit: if you turn the switch on by hand while a cycle the optimizer started is running, it is turned off when that cycle ends, because the two cannot be told apart. Control needs the switch above.",
               "dhw_disinfection_switch_entity": "A switch or helper that starts the heat pump's own anti-legionella program. In observe mode its state is only read and shown on the hot water sensor's attributes; in control mode the integration turns it on when a disinfection cycle starts and off when that cycle ends.",
               "dhw_elastic_legionella_enabled": "Allow the anti-legionella cycle to run a day or two early when electricity is unusually cheap, instead of always waiting for its deadline. The deadline is still always honoured.",
-              "dhw_free_disinfection_enabled": "If a wood boiler, solar coil or immersion heater gets the tank to the anti-legionella temperature, that counts as a completed cycle instead of running another one. Off, reaching the temperature (within 1 °C) counts at once, however briefly; on, the tank has to hold it for 20 minutes first.",
+              "dhw_free_disinfection_enabled": "A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature is counted as a completed cycle either way. Off, it counts at once; on, only after the tank has held that temperature for 20 minutes, so a short peak credits nothing.",
               "dhw_legionella_min_interval_days": "With Let the anti-legionella cycle pick a cheap day on, a cycle may run early on a cheap day only after this many days since the last one. It never delays a cycle that is due at the regular interval, and does nothing while that option is off.",
               "dhw_quantile_targets_enabled": "Learn how much hot water each time frame actually uses on a heavy day, and make the tank ready for that instead of for the average day. Needs a tank temperature sensor, configured hot water time frames, and a couple of weeks of evidence."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set and hot water time frames are configured, the pump runs only during those time frames plus the lead time below; with no time frames, or with hot water off, it is kept on.",
+          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below. With hot water off or no time frames, it is left on.",
           "vvc_lead_minutes": "How long before a hot water time frame the circulation pump starts, so the loop is already hot when the time frame opens.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant; the headroom sensor then follows your capacity-tariff peak alone, and has no value if there is no capacity tariff either. There is no safe default to guess, and a wrong one would cap a bigger house.",
+          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant, and leaves the headroom sensor following the capacity-tariff peak alone, unavailable without a capacity tariff — there is no safe default to guess, and a wrong one would cap a bigger house.",
           "main_fuse_phases": "Nearly every Swedish house is 3-phase.",
           "fuse_guard_enabled": "Caps the heat pump's planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so on its sensors instead of silently going cold.",
           "peak_guard_enabled": "Watches the power meter live and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter; a cold tank or a breached comfort floor always wins over the guard.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Assume less sun after heavy snowfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest acceptable temperature by 1 °C (never below 15 °C) while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
+              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest indoor temperature the plan accepts by 1 °C, never below 15 °C, while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
               "outage_recovery_enabled": "After an outage everything restarts at once — cold house, cold tank, the whole neighbourhood — which is exactly when a new monthly capacity peak gets set. With this on, a long gap in updates opens a two-hour recovery window where the capacity charge is taken seriously from the first kW and hot water queues 45 minutes behind space heating, unless the tank is genuinely low.",
               "precip_type_enabled": "Rain soaks the building envelope and increases heat loss; snow does not. Without this, a snowy forecast is treated as rain and the plan buys heat for a wet wall that stays dry. Needs the Open-Meteo connection for the snow data.",
               "snow_roof_factor_enabled": "For two days after heavy snowfall, the modelled solar gain is halved — snow on roof glazing and low winter panes blocks the sun the plan was counting on. Deliberately crude: a factor and a holding period, not a melt model."
diff --git a/custom_components/heatpump_optimizer/translations/de.json b/custom_components/heatpump_optimizer/translations/de.json
index bd78fd8c7b..dd3a654ced 100644
--- a/custom_components/heatpump_optimizer/translations/de.json
+++ b/custom_components/heatpump_optimizer/translations/de.json
@@ -12,7 +12,7 @@
           "weather_entity": "Wettervorhersage"
         },
         "data_description": {
-          "name": "Der Name dieses Integrationseintrags in der Integrationsliste von Home Assistant. Er ist nicht Teil der Entitätsnamen: Diese beginnen alle mit „Heat Pump Optimizer“.",
+          "name": "Der Titel dieses Eintrags unter Geräte & Dienste. Entitätsnamen verwenden den festen Gerätenamen Heat Pump Optimizer.",
           "price_source": "Tibber verwendet dein API-Token. Entität liest einen Preissensor aus Home Assistant, z. B. Nord Pool.",
           "tibber_token": "Wird verwendet, um deine stündlichen Strompreise abzufragen. Erstelle eines unter developer.tibber.com. Unverändert lassen, solange es sich nicht geändert hat. Nicht erforderlich, wenn die Preisquelle eine Entität ist.",
           "price_entity": "Erforderlich, wenn die Preisquelle eine Entität ist. Typische Attribute sind raw_today und raw_tomorrow.",
@@ -592,8 +592,8 @@
             "data_description": {
               "indoor_temp_entity": "Optional. Die tatsächliche Raumtemperatur. Ohne sie vertraut der Optimierer seinem eigenen Modell, das mit der Zeit abdriftet.",
               "outdoor_temp_entity": "Optional. Ein lokales Außenthermometer ist für die aktuelle Stunde genauer als die Vorhersage.",
-              "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Dient nur dazu zu bemerken, wenn die Entität nicht gelesen werden kann. Der Optimierer schreibt nie einen empfohlenen Raumheizungs-Sollwert.",
-              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit teilt dem Optimierer mit, was die Zahl bedeutet: Bei „Steuerung der Pumpenfunktion“ auf „Steuern“ schreibt er die Raumtemperatur (Innentemperatur) bzw. die Wassertemperatur (Vorlauftemperatur, Rücklauftemperatur) des Plans in diese Entität.",
+              "space_setpoint_entity": "Optional. Eine Zahl, ein Helfer oder eine Climate-Entität, die der Sollwert der Raumheizung der Pumpe ist. Steht die Steuerung der Pumpenfunktion auf Steuern, schreibt der Optimierer sie in jedem Planschritt, wie die Steuerung der Pumpenfunktion beschreibt, und das Ausschalten von Optimierer aktiv schreibt den Wert zurück, den die Entität vor dem ersten Schreiben zeigte. Bei Aus oder Beobachten wird sie nur gelesen, um zu bemerken, wenn sie nicht gelesen werden kann.",
+              "space_setpoint_unit": "Innentemperatur ist richtig für einen Raum- oder Thermostat-Sollwert. Vorlauftemperatur gilt für einen Regler, dessen Sollwert eine Wassertemperatur ist, auf der er seinen Vorlauf hält. Rücklauftemperatur gilt für einen Regler, der den Sollwert als Ziel für das Rücklaufwasser nimmt (angenommen für eine Luxtronik über ihre Smart-Home-Schnittstelle); er wird wie ein Vorlauf-Sollwert geschrieben, wobei der Nennhaltewert, die Wetterkurve und die 25-°C-Schwelle um 5 K nach unten in Rücklaufwerte verschoben werden. Eine Version vor dieser Option liest Rücklauftemperatur als Innentemperatur: Stelle vor einem Downgrade wieder auf Vorlauftemperatur um. Würde ein Innentemperaturziel auf eine Vorlauf-Entität zeigen, würden etwa 21 °C an ein Gerät gesendet, das 35–45 °C erwartet, und das Haus würde stark unterheizt. Die Einheit ist eine Angabe: Der Optimizer leitet sie nie aus der Entität ab, nur das Vorausfüllen aus einem Wärmepumpengerät schlägt eine vor. Bei „Steuerung der Pumpenfunktion“ auf „Steuern“ schreibt der Optimizer die Raumtemperatur (Innentemperatur) bzw. die Wassertemperatur (Vorlauftemperatur, Rücklauftemperatur) des Plans in diese Entität.",
               "flow_min_lift_k": "Mit Steuerung der Pumpenfunktion auf Steuern ist der bei der niedrigsten Planleistung geschriebene Wasser-Sollwert das gemessene Eingangswasser plus dieser Wert: Wärmepumpen-Rücklauf, Pufferspeicher, Fußbodenrücklauf oder Ventilauslass, und bei einer Entität mit Rücklauftemperatur nur die ersten drei. 5 K passt zu einem Regler, der seinen Vorlauf auf dem Sollwert hält. Von einem Regler, der die Zahl als Ziel für das Rücklaufwasser nimmt, wird angenommen, dass er seinen Verdichter umso stärker laufen lässt, je weiter das Ziel über dem Rücklauf liegt, er will also wahrscheinlich weniger; 1–2 K ist ein Ausgangspunkt, der an der gemessenen Frequenz und Leistung des Verdichters zu prüfen ist, kein gemessener Wert.",
               "flow_heat_c": "Der bei voller Planleistung geschriebene Wasser-Sollwert und der höchste, der geschrieben wird, solange der Plan die Führung hat. 55 °C passt zu einem Vorlaufziel. Wähle ihn bei einer Entität mit Rücklauftemperatur über dem höchsten Rücklauf, den du im normalen Heizbetrieb siehst, plus dem Hub, und nicht höher, als der Regler annimmt; bei einer Niedertemperatur-Fußbodenheizung können 35–40 °C ein Ausgangspunkt sein, der an Messungen zu prüfen ist. Unter 30 °C wird nicht angeboten: Die Schwelle, die aus bedeutet, liegt bei 25 °C für ein Vorlaufziel und bei 20 °C für ein Rücklaufziel.",
               "space_setpoint_power_feedback": "Standardmäßig an. Wirkt nur mit Wärmepumpen-Betriebssteuerung auf Steuern, einer Einheit Vorlauf- oder Rücklauftemperatur und einem Leistungssensor der Wärmepumpe; sonst ändert sich nichts. Nach 5 Minuten Starthaltezeit wird der Wasser-Sollwert gesenkt, solange die gemessene Aufnahme über der geplanten Leistung liegt, angehoben, solange sie darunter liegt, und innerhalb von 10 % gehalten, statt dem steigenden Eingangswasser zu folgen. Aus schreibt das Eingangswasser plus den Hub. Anforderungen an den Regler: seine Heizungshysterese höchstens der Hub (Luxtronik: 0,5 K), sonst startet ein stehender Verdichter nicht; sein minimales Rücklaufziel unter dem Rücklauf der Heizperiode; seine Integration fragt ihn mindestens alle 10 Minuten ab und stellt nach einem Reglerneustart die Heizbetriebsart wieder her, denn eine Luxtronik Smart Home Interface verwirft nach 600 s ohne Zugriff alle gesetzten Werte; und kein zweites Werkzeug schreibt dieselben Register (eine Luxtronik verwirft Schreibvorgänge dann stillschweigend).",
@@ -1012,7 +1012,7 @@
               "building_preset_enabled": "Thermische Werte aus dem Gebäudetyp ableiten"
             },
             "data_description": {
-              "building_preset_enabled": "Wenn aktiviert, werden die Werte für thermische Masse, Wärmeverlust und Heizflächen auf der Seite „Thermisches Modell (Experte)“ bei jedem Speichern dieser Seite überschrieben."
+              "building_preset_enabled": "Wenn aktiviert, werden die Werte für thermische Masse, Wärmeverlust und Heizflächen auf der Seite „Thermisches Modell (Experten)“ bei jedem Speichern dieser Seite überschrieben."
             }
           },
           "climate": {
@@ -1033,7 +1033,7 @@
         }
       },
       "thermal_model": {
-        "title": "Thermisches Modell (Experte)",
+        "title": "Thermisches Modell (Experten)",
         "description": "Die Rohwerte hinter dem thermischen Modell, die sonst nur bei der Einrichtung abgefragt werden. Ein leer gelassenes Feld behält seinen aktuellen Wert und wird nie gespeichert, ein Haus mit einer Zone bleibt also ein Haus mit einer Zone. Die Zwei-Zonen-Werte stehen auf der Seite „Zwei-Zonen-Modell“: Steht „Zwei-Zonen-Modell“ auf „Automatisch“, schaltet das Speichern eines Zonenwerts das Zwei-Zonen-Modell ein; „An“ oder „Aus“ erzwingt es in die eine oder andere Richtung.\n\n{preset_warning}",
         "data": {
           "house_thermal_mass": "Thermische Masse des Hauses (kWh/°C)",
@@ -1061,7 +1061,7 @@
         }
       },
       "grid": {
-        "title": "Netz-Spitzentarif",
+        "title": "Lastspitzentarif des Netzes",
         "description": "Kosten, die nicht einfach der Preis pro kWh sind. Viele schwedische Netzbetreiber berechnen zusätzlich eine monatliche Leistungsgebühr auf Basis deiner höchsten Stunden – Warmwasser und Heizung in dieselbe günstige Stunde zu legen kann dann mehr kosten, als es spart.",
         "data": {
           "peak_tariff_enabled": "Meine Netzrechnung enthält eine Leistungsgebühr",
@@ -1089,7 +1089,7 @@
         }
       },
       "solar_pv": {
-        "title": "Solaranlage",
+        "title": "Solarmodule",
         "description": "Wenn du Solarstrom erzeugst, ist es besser, Warmwasser oder den Pufferspeicher mit Überschuss zu beheizen, als ihn zum Vergütungssatz einzuspeisen. Teile dem Optimierer mit, wie deine Anlage aussieht, und er bewertet jede Stunde mit den tatsächlichen Kosten des Verbrauchs.",
         "data": {
           "pv_enabled": "Ich habe eine Solaranlage",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Verwende stattdessen diese, wenn deine Vergütung dem Spotpreis folgt.",
           "pv_enabled": "Lässt den Plan die Wärmepumpe mit deinem eigenen Überschuss betreiben, statt ihn für weniger zu verkaufen, als Netzstrom kostet.",
           "pv_peak_kw": "Die Nennspitzenleistung der Anlage. Dient zur Skalierung der Erzeugungsprognose.",
-          "pv_production_entity": "Optional. Ein Live-Erzeugungssensor ersetzt die Prognose für den aktuellen Schritt durch die gemessene Leistung (begrenzt auf die installierte Leistung); spätere Stunden bleiben bei der Prognose aus der Sonneneinstrahlung.",
+          "pv_production_entity": "Optional. Ein Live-Erzeugungssensor ersetzt den aktuellen Schritt der Prognose durch das, was das Dach gerade liefert, begrenzt auf die installierte Leistung; spätere Schritte bleiben modelliert.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "Eine Person, ein Gerätetracker, ein Kalender oder ein Anwesenheitssensor. Der Schalter auf der Plan-Seite hat Vorrang, bis er ausgeschaltet wird. Eine Person, die „nicht zu Hause“ ist, bedeutet bei ausgeschaltetem Schalter weiterhin Abwesenheit.",
           "holiday_calendar_entity": "Wenn dieser Kalender eingeschaltet ist, ersetzen die Feiertags-Komfort- und Feiertags-Warmwasserfenster für diesen Tag das Paar aus Werktag und Wochenende. Die Abwesenheitsabsenkung hat weiterhin Vorrang, wenn Abwesenheit aktiv ist.",
-          "away_dhw_min_temperature": "Der Anti-Legionellen-Zyklus läuft weiterhin nach seinem üblichen Zeitplan; er wird nicht auf deine Rückkehr getaktet.",
+          "away_dhw_min_temperature": "Der Anti-Legionellen-Zyklus läuft weiterhin in seinem üblichen Intervall; er wird nicht auf deine Rückkehr abgestimmt.",
           "away_temperature": "Die Haltetemperatur während der Abwesenheit. Niedrig genug zum Sparen, hoch genug, um das Haus und seine Leitungen zu schützen.",
           "after_save": "Das Speichern wirkt sofort; hier wählst du, wohin der Dialog als Nächstes führt."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Beobachten liest den Schalter und schreibt ihn nie. Steuern schaltet ihn ein, wenn eine Legionellenschaltung startet, und aus, wenn sie endet, schaltet ihn aber nie ein, solange der Modus der Pumpe kein Warmwasser erzeugt. Es wird nur ein Schalter ausgeschaltet, den die Integration selbst eingeschaltet hat: Ein Schalter, der bei Beginn des Zyklus schon eingeschaltet war, bleibt unberührt. Eine Einschränkung: Wenn du den Schalter von Hand einschaltest, während ein vom Optimierer gestarteter Zyklus läuft, wird er am Ende dieses Zyklus ausgeschaltet, weil sich beides nicht unterscheiden lässt. Steuern benötigt den obigen Schalter.",
               "dhw_disinfection_switch_entity": "Ein Schalter oder Helfer, der das eigene Legionellenprogramm der Wärmepumpe startet. Im Beobachtungsmodus wird sein Zustand nur gelesen und in den Attributen des Warmwasser-Sensors angezeigt; im Steuerungsmodus schaltet die Integration ihn ein, wenn ein Desinfektionszyklus startet, und aus, wenn er endet.",
               "dhw_elastic_legionella_enabled": "Erlaubt der Legionellenschaltung, ein bis zwei Tage früher zu laufen, wenn Strom ungewöhnlich günstig ist, statt immer bis zur Frist zu warten. Die Frist wird weiterhin immer eingehalten.",
-              "dhw_free_disinfection_enabled": "Wenn ein Holzkessel, eine Solarspirale oder ein Heizstab den Speicher auf die Legionellentemperatur bringt, wird das als abgeschlossener Zyklus gezählt, statt einen weiteren auszuführen. Aus: Das Erreichen der Temperatur (innerhalb von 1 °C) zählt sofort, wie kurz auch immer; an: Der Speicher muss sie zuvor 20 Minuten halten.",
+              "dhw_free_disinfection_enabled": "Bringt ein Holzkessel, eine Solarspirale oder ein Heizstab den Speicher auf die Legionellentemperatur, wird das in jedem Fall als abgeschlossener Zyklus gezählt. Aus: sofort; ein: erst nachdem der Speicher diese Temperatur 20 Minuten gehalten hat, sodass eine kurze Spitze nichts anrechnet.",
               "dhw_legionella_min_interval_days": "Ist „Legionellenschaltung einen günstigen Tag wählen lassen“ eingeschaltet, darf ein Zyklus an einem günstigen Tag erst dann früher laufen, wenn seit dem letzten so viele Tage vergangen sind. Er verzögert nie einen Zyklus, der im regulären Intervall fällig ist, und bewirkt nichts, solange diese Option aus ist.",
               "dhw_quantile_targets_enabled": "Lernt, wie viel Warmwasser jeder Zeitraum an einem Tag mit hohem Verbrauch tatsächlich nutzt, und bereitet den Speicher darauf vor statt auf den Durchschnittstag. Benötigt einen Speichertemperatursensor, konfigurierte Warmwasser-Zeitfenster und einige Wochen an Daten."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "vvc_pump_entity": "Ein Schalter, der die Pumpe der Warmwasser-Zirkulation (VVC) steuert. Wenn gesetzt und Warmwasser-Zeitfenster konfiguriert sind, läuft die Pumpe nur in diesen Zeitfenstern plus der unten genannten Vorlaufzeit; ohne Zeitfenster oder bei ausgeschaltetem Warmwasser bleibt sie an.",
+          "vvc_pump_entity": "Ein Schalter, der die Pumpe der Warmwasser-Zirkulation (VVC) steuert. Wenn gesetzt, läuft die Pumpe nur in deinen Warmwasser-Zeitfenstern plus der unten genannten Vorlaufzeit. Ist Warmwasser aus oder gibt es keine Zeitfenster, bleibt sie an.",
           "vvc_lead_minutes": "Wie lange vor einem Warmwasser-Zeitfenster die Zirkulationspumpe startet, damit die Leitung bei Beginn des Zeitfensters schon heiß ist.",
           "after_save": "Das Speichern wirkt sofort; hier legst du fest, wohin der Dialog als Nächstes führt."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "Nach dem Speichern"
         },
         "data_description": {
-          "main_fuse_amperes": "Die Hauptsicherung des Hauses in Ampere, laut Netzanschlussvertrag. 0 lässt sie unkonfiguriert, wodurch der Sicherungsberater und der Sicherungswächter inaktiv bleiben; der Sensor für die Reserve folgt dann allein deiner Spitzentarif-Spitze und hat keinen Wert, wenn es auch keinen Spitzentarif gibt. Es gibt keinen sicheren Standardwert zum Raten, und ein falscher würde ein größeres Haus begrenzen.",
+          "main_fuse_amperes": "Die Hauptsicherung des Hauses in Ampere, laut Netzanschlussvertrag. 0 lässt sie unkonfiguriert, wodurch der Sicherungsberater und der Sicherungswächter inaktiv bleiben und der Sensor für die Reserve allein der Spitze des Lastspitzentarifs folgt, ohne Lastspitzentarif nicht verfügbar – es gibt keinen sicheren Standardwert zum Raten, und ein falscher würde ein größeres Haus begrenzen.",
           "main_fuse_phases": "Fast jedes schwedische Haus hat 3 Phasen.",
           "fuse_guard_enabled": "Begrenzt die geplante Leistung der Wärmepumpe auf das, was die Sicherung nach dem restlichen Haus noch übrig lässt. Wenn eine Begrenzung die Komfortuntergrenze unerreichbar machen würde, meldet der Plan das auf seinen Sensoren, statt stillschweigend kalt zu werden.",
           "peak_guard_enabled": "Überwacht den Stromzähler live und hält, wenn für das laufende Messfenster voraussichtlich eine neue abgerechnete Spitze entsteht, elektrisches Warmwasser zurück und senkt die Heizkurve für den Rest dieses Fensters leicht ab. Benötigt einen Stromzähler; ein kalter Speicher oder eine verletzte Komfortuntergrenze haben immer Vorrang vor dem Wächter.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Nach starkem Schneefall weniger Sonne annehmen"
             },
             "data_description": {
-              "open_window_relax_enabled": "Die Erkennung offener Fenster pausiert das Lernen immer – das ist kostenlos und stets aktiv. Zusätzlich senkt diese Option die niedrigste akzeptable Temperatur um 1 °C (nie unter 15 °C), solange ein Fenster offen zu sein scheint, damit die Wärmepumpe nicht dafür zahlt, den Garten zu heizen. Standardmäßig aus, weil sie echte Wärme verschiebt: Ein fälschlich erkanntes Fenster bedeutet ein etwas kühleres Haus.",
+              "open_window_relax_enabled": "Die Erkennung offener Fenster pausiert das Lernen immer – das ist kostenlos und stets aktiv. Zusätzlich senkt diese Option die niedrigste Raumtemperatur, die der Plan zulässt, um 1 °C, nie unter 15 °C, solange ein Fenster offen zu sein scheint, damit die Wärmepumpe nicht dafür zahlt, den Garten zu heizen. Standardmäßig aus, weil sie echte Wärme verschiebt: Ein fälschlich erkanntes Fenster bedeutet ein etwas kühleres Haus.",
               "outage_recovery_enabled": "Nach einem Ausfall läuft alles gleichzeitig wieder an – kaltes Haus, kalter Speicher, die ganze Nachbarschaft – und genau dann entsteht eine neue monatliche Leistungsspitze. Ist dies aktiviert, öffnet eine lange Lücke bei den Aktualisierungen ein zweistündiges Wiederanlauffenster, in dem der Leistungspreis vom ersten kW an ernst genommen wird und Warmwasser 45 Minuten hinter der Raumheizung ansteht, außer der Speicher ist wirklich knapp.",
               "precip_type_enabled": "Regen durchfeuchtet die Gebäudehülle und erhöht den Wärmeverlust; Schnee nicht. Ohne diese Option wird eine Schneeprognose wie Regen behandelt, und der Plan kauft Wärme für eine nasse Wand, die trocken bleibt. Benötigt die Open-Meteo-Verbindung für die Schneedaten.",
               "snow_roof_factor_enabled": "Für zwei Tage nach starkem Schneefall wird der modellierte solare Wärmeeintrag halbiert – Schnee auf Dachfenstern und tiefen Winterscheiben blockiert die Sonne, mit der der Plan gerechnet hat. Bewusst grob: ein Faktor und eine Haltedauer, kein Schmelzmodell."
@@ -1518,7 +1518,7 @@
         }
       },
       "modbus_prefill": {
-        "title": "Aus einem Wärmepumpen-Gerät vorbefüllen",
+        "title": "Aus einem Wärmepumpengerät vorbefüllen",
         "description": "Für eine Rotenso Windmi oder eine andere von GCHV gebaute Wärmepumpe, die über das Modbus-Paket des Projekts tuya_heat_pump oder über das eigene Home-Assistant-Gerät der Pumpe ausgelesen wird. Wähle das Gerät, oder lass es leer und nenne den Entitäts-Präfix des Pakets, und sende ab: Das nächste Formular schlägt Werte vor, die aus der Pumpe gelesen wurden – die Warmwasser-Sollwerte und den Zeitplan, die Legionellentage, den Nachtmodus-Zeitplan, die maximale elektrische Leistung der Pumpe (aus ihrer Gerätekapazität), ob die Pumpe nach Wassertemperatur regelt, und die eigenen Sensoren der Pumpe für noch leere Sensorplätze. Bearbeite oder leere beliebige davon; nur was du behältst, wird gespeichert, und ein geleertes Feld bleibt, wie es war. Nichts über das Haus oder sein Heizsystem lässt sich auf diese Weise auslesen.\n\nGelesene Entitäten: {found}. Register für den Typ des Zuheizers: {backup_heater_type} – jeder Wert außer 7 bedeutet, dass die Pumpe eine eigene elektrische Heizung hat, die von den Heizer-Plätzen bei der Wärmepumpen-Telemetrie überwacht werden soll.\n\nRollen, die aus dem NAMEN einer Entität statt aus einer veröffentlichten Definition gelesen wurden – die Seite kann diese nicht prüfen, prüfe daher jede vor dem Speichern: {name_matched}. Rollen aus veröffentlichten Definitionen, nach Quelle: {matched_sources}.",
         "data": {
           "prefill_device": "Wärmepumpen-Gerät (optional)",
diff --git a/custom_components/heatpump_optimizer/translations/en.json b/custom_components/heatpump_optimizer/translations/en.json
index 1e09b13a40..1f6dc0c71e 100644
--- a/custom_components/heatpump_optimizer/translations/en.json
+++ b/custom_components/heatpump_optimizer/translations/en.json
@@ -12,7 +12,7 @@
           "weather_entity": "Weather forecast"
         },
         "data_description": {
-          "name": "The name of this integration entry in Home Assistant's list of integrations. It is not part of entity names: they all start with \"Heat Pump Optimizer\".",
+          "name": "The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer.",
           "price_source": "Tibber uses your API token. Entity reads a Home Assistant price sensor such as Nord Pool.",
           "tibber_token": "Used to read your hourly electricity prices. Create one at developer.tibber.com. Leave as-is unless it has changed. Not required when the price source is an entity.",
           "price_entity": "Required when the price source is an entity. Typical attributes are raw_today and raw_tomorrow.",
@@ -592,8 +592,8 @@
             "data_description": {
               "indoor_temp_entity": "Optional. The actual room temperature. Without it the optimizer trusts its own model, which drifts over time.",
               "outdoor_temp_entity": "Optional. A local outdoor thermometer is more accurate than the forecast for the current hour.",
-              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. Used only to notice when the entity cannot be read. The optimizer never writes a recommended space set-point.",
-              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit tells the optimizer what the number means: with Pump duty control at Control it writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
+              "space_setpoint_entity": "Optional. A number, helper or climate entity that is the pump's space-heating set-point. With Pump duty control at Control the optimizer writes it on every plan step, as Pump duty control describes, and turning Optimizer active off writes back the value it read before its first write. With Pump duty control at Off or Observe it is only read, to notice when it cannot be read.",
+              "space_setpoint_unit": "Indoor temperature is correct for a room or thermostat set-point. Flow temperature is for a controller whose set-point is a water temperature it holds its supply at. Return temperature is for a controller that takes the set-point as its return-water target (assumed for a Luxtronik through its Smart Home Interface); it is written like a flow set-point, with the rated hold, the weather curve and the 25 °C gate moved 5 K down to return terms. A version before this option reads Return temperature as Indoor temperature: switch it back to Flow temperature before downgrading. Pointing an indoor target at a flow entity would command roughly 21 °C to something expecting 35–45 °C and badly underheat the house. The unit is a declaration: the optimizer never infers it from the entity, and only the heat-pump pre-fill suggests one. With Pump duty control at Control the optimizer writes the plan's room temperature (Indoor temperature) or water temperature (Flow temperature, Return temperature) to this entity.",
               "flow_min_lift_k": "With Pump duty control at Control, the water set-point written at the plan's lowest power is the measured inlet water plus this: heat-pump return, buffer tank, floor return or valve outlet, and for a Return temperature entity the first three only. 5 K suits a controller that holds its supply at the set-point. A controller that takes the number as its return-water target is assumed to run its compressor harder the further the target sits above the return, so it likely wants less; 1–2 K is a starting point to check against the compressor's measured frequency and power, not a measured value.",
               "flow_heat_c": "The water set-point written at full planned power, and the highest one written while the plan is in charge. 55 °C suits a supply target. For a Return temperature entity choose it above the highest return you see in normal heating plus the lift, and no higher than the controller accepts; on a low-temperature floor heating 35–40 °C may be a starting point to check against measurements. Below 30 °C is not offered: the gate that means off is 25 °C for a flow target and 20 °C for a return target.",
               "space_setpoint_power_feedback": "On by default. Acts only with Pump duty control at Control, a Flow or Return temperature unit and a heat-pump power sensor; otherwise nothing changes. After a 5-minute start hold, the water set-point is nudged down while the measured draw is above the planned level and up while it is below, and held while it is within 10 %, instead of following the rising inlet water. Off writes the inlet plus the lift. Requirements on the controller: its heating hysteresis at most the lift (Luxtronik: 0.5 K), or a stopped compressor is not started; its minimum return target below the heating-season return; its integration polling it at least every 10 minutes, and restoring its heating mode after a controller restart, since a Luxtronik Smart Home Interface drops every set value after 600 s without access; and no second tool writing the same registers (a Luxtronik then silently discards writes).",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Use this instead if your compensation follows the spot price.",
           "pv_enabled": "Lets the plan run the heat pump on your own surplus instead of selling it for less than bought power costs.",
           "pv_peak_kw": "The array's rated peak output. Used to scale the production forecast.",
-          "pv_production_entity": "Optional. A live production sensor replaces the forecast for the current step with the measured output (capped at the installed capacity); later hours stay on the forecast from solar irradiance.",
+          "pv_production_entity": "Optional. A live production sensor replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
       },
@@ -1123,7 +1123,7 @@
         "data_description": {
           "away_presence_entity": "A person, device tracker, calendar, or occupancy sensor. The Plan-page toggle wins until it is turned off. A person being 'not home' still means away when the toggle is off.",
           "holiday_calendar_entity": "When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active.",
-          "away_dhw_min_temperature": "The anti-legionella cycle still runs, on its usual schedule; it is not timed to your return.",
+          "away_dhw_min_temperature": "The anti-legionella cycle still runs on its usual interval; it is not timed to your return.",
           "away_temperature": "The hold temperature while away. Low enough to save, high enough to protect the house and its plumbing.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observe reads the switch and never writes it. Control turns it on when an anti-legionella cycle starts and off when that cycle ends, but never turns it on while the pump's mode makes no hot water. It only turns off a switch it turned on itself: a switch that was already on when the cycle began is left alone. One limit: if you turn the switch on by hand while a cycle the optimizer started is running, it is turned off when that cycle ends, because the two cannot be told apart. Control needs the switch above.",
               "dhw_disinfection_switch_entity": "A switch or helper that starts the heat pump's own anti-legionella program. In observe mode its state is only read and shown on the hot water sensor's attributes; in control mode the integration turns it on when a disinfection cycle starts and off when that cycle ends.",
               "dhw_elastic_legionella_enabled": "Allow the anti-legionella cycle to run a day or two early when electricity is unusually cheap, instead of always waiting for its deadline. The deadline is still always honoured.",
-              "dhw_free_disinfection_enabled": "If a wood boiler, solar coil or immersion heater gets the tank to the anti-legionella temperature, that counts as a completed cycle instead of running another one. Off, reaching the temperature (within 1 °C) counts at once, however briefly; on, the tank has to hold it for 20 minutes first.",
+              "dhw_free_disinfection_enabled": "A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature is counted as a completed cycle either way. Off, it counts at once; on, only after the tank has held that temperature for 20 minutes, so a short peak credits nothing.",
               "dhw_legionella_min_interval_days": "With Let the anti-legionella cycle pick a cheap day on, a cycle may run early on a cheap day only after this many days since the last one. It never delays a cycle that is due at the regular interval, and does nothing while that option is off.",
               "dhw_quantile_targets_enabled": "Learn how much hot water each time frame actually uses on a heavy day, and make the tank ready for that instead of for the average day. Needs a tank temperature sensor, configured hot water time frames, and a couple of weeks of evidence."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set and hot water time frames are configured, the pump runs only during those time frames plus the lead time below; with no time frames, or with hot water off, it is kept on.",
+          "vvc_pump_entity": "A switch controlling the hot water circulation (VVC) loop pump. When set, the pump only runs during your hot water time frames, plus the lead time below. With hot water off or no time frames, it is left on.",
           "vvc_lead_minutes": "How long before a hot water time frame the circulation pump starts, so the loop is already hot when the time frame opens.",
           "after_save": "Saving writes through immediately; this chooses where the dialog goes next."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "After saving"
         },
         "data_description": {
-          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant; the headroom sensor then follows your capacity-tariff peak alone, and has no value if there is no capacity tariff either. There is no safe default to guess, and a wrong one would cap a bigger house.",
+          "main_fuse_amperes": "The house's main fuse in amperes, from your grid contract. 0 leaves it unconfigured, which keeps the fuse advisor and the fuse guard dormant, and leaves the headroom sensor following the capacity-tariff peak alone, unavailable without a capacity tariff — there is no safe default to guess, and a wrong one would cap a bigger house.",
           "main_fuse_phases": "Nearly every Swedish house is 3-phase.",
           "fuse_guard_enabled": "Caps the heat pump's planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so on its sensors instead of silently going cold.",
           "peak_guard_enabled": "Watches the power meter live and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter; a cold tank or a breached comfort floor always wins over the guard.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Assume less sun after heavy snowfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest acceptable temperature by 1 °C (never below 15 °C) while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
+              "open_window_relax_enabled": "The open-window detector always pauses learning — that part is free and always on. This additionally lowers the coldest indoor temperature the plan accepts by 1 °C, never below 15 °C, while a window appears to be open, so the heat pump stops paying to heat the garden. Off by default because it moves real heat: a wrongly flagged window means a slightly cooler house.",
               "outage_recovery_enabled": "After an outage everything restarts at once — cold house, cold tank, the whole neighbourhood — which is exactly when a new monthly capacity peak gets set. With this on, a long gap in updates opens a two-hour recovery window where the capacity charge is taken seriously from the first kW and hot water queues 45 minutes behind space heating, unless the tank is genuinely low.",
               "precip_type_enabled": "Rain soaks the building envelope and increases heat loss; snow does not. Without this, a snowy forecast is treated as rain and the plan buys heat for a wet wall that stays dry. Needs the Open-Meteo connection for the snow data.",
               "snow_roof_factor_enabled": "For two days after heavy snowfall, the modelled solar gain is halved — snow on roof glazing and low winter panes blocks the sun the plan was counting on. Deliberately crude: a factor and a holding period, not a melt model."
diff --git a/custom_components/heatpump_optimizer/translations/sv.json b/custom_components/heatpump_optimizer/translations/sv.json
index 44ec92979f..fae04219e4 100644
--- a/custom_components/heatpump_optimizer/translations/sv.json
+++ b/custom_components/heatpump_optimizer/translations/sv.json
@@ -12,7 +12,7 @@
           "price_entity": "Prissensor (Nord Pool eller liknande)"
         },
         "data_description": {
-          "name": "Namnet på den här integrationsposten i Home Assistants lista över integrationer. Det ingår inte i entitetsnamnen: de börjar alla med \"Heat Pump Optimizer\".",
+          "name": "Titeln på den här posten under Enheter och tjänster. Entiteternas namn använder det fasta enhetsnamnet Heat Pump Optimizer.",
           "tibber_token": "Används för att läsa dina timpriser på el. Skapa en på developer.tibber.com. Lämna som den är om den inte har ändrats. Krävs inte när priskällan är en entitet.",
           "weather_entity": "Härifrån hämtas prognos för utomhustemperatur, vind och regn. Optimeringen planerar 24 timmar framåt och kräver därför en prognos.",
           "price_source": "Tibber använder din API-token. Entitet läser en Home Assistant-prissensor, till exempel Nord Pool.",
@@ -343,7 +343,7 @@
           "dhw_legionella_interval_days": "Intervall för legionellaskydd",
           "silent_mode_windows": "Pumpens eget nattläge-schema",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
-          "space_setpoint_unit": "Vad den börvärdesenheten förväntar sig",
+          "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
           "mixing_valve_write_target_kind": "Vad styrenheten förväntar sig",
           "compressor_freq_sensor": "Sensor för faktisk frekvens (rekommenderas för styrning)",
           "outdoor_temp_entity": "Utomhusgivare",
@@ -582,7 +582,7 @@
               "indoor_temp_entity": "Inomhusgivare",
               "outdoor_temp_entity": "Utomhusgivare",
               "space_setpoint_entity": "Börvärdesenhet för rumsuppvärmning (valfritt)",
-              "space_setpoint_unit": "Vad den börvärdesenheten förväntar sig",
+              "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
               "flow_min_lift_k": "Minsta höjning över inkommande vatten (K)",
               "flow_heat_c": "Högsta framledning vid värme (°C)",
               "space_setpoint_power_feedback": "Följ planerad effekt efter uppmätt förbrukning",
@@ -592,8 +592,8 @@
             "data_description": {
               "indoor_temp_entity": "Valfritt. Den verkliga rumstemperaturen. Utan den litar optimeringen på sin egen modell, som glider med tiden.",
               "outdoor_temp_entity": "Valfritt. En egen utegivare är mer exakt än prognosen för den aktuella timmen.",
-              "space_setpoint_entity": "Valfritt. En number-, helper- eller climate-enhet som är pumpens börvärde för rumsuppvärmning. Används bara för att märka när enheten inte går att läsa. Optimeringen skriver aldrig ett rekommenderat rumsuppvärmningsbörvärde.",
-              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsenhet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten talar om för optimeraren vad talet betyder: med Styrning av pumpens uppgift på Styrning skriver den planens rumstemperatur (Inomhustemperatur) eller vattentemperatur (Framledningstemperatur, Returtemperatur) till den här entiteten.",
+              "space_setpoint_entity": "Valfritt. En number-, helper- eller climate-enhet som är pumpens börvärde för rumsuppvärmning. Med Styrning av pumpens uppgift satt till Styrning skriver optimeraren det vid varje plansteg, som Styrning av pumpens uppgift beskriver, och när Optimeraren aktiv stängs av skrivs värdet tillbaka som enheten visade före den första skrivningen. Med Av eller Observera läses det bara, för att märka när det inte går att läsa.",
+              "space_setpoint_unit": "Inomhustemperatur är rätt för ett rums- eller termostatbörvärde. Framledningstemperatur är för en styrenhet vars börvärde är en vattentemperatur som den håller framledningen på. Returtemperatur är för en styrenhet som tar börvärdet som mål för returvattnet (antaget för en Luxtronik via dess Smart Home Interface); den skrivs som ett framledningsbörvärde, med det nominella hållvärdet, värmekurvan och grinden på 25 °C flyttade 5 K ned till returnivå. En version från före det här valet läser Returtemperatur som Inomhustemperatur: byt tillbaka till Framledningstemperatur innan du nedgraderar. Att peka ett inomhusmål mot en framledningsentitet skulle kommendera ungefär 21 °C till något som förväntar sig 35–45 °C och undervärma huset kraftigt. Enheten är en deklaration: optimeraren härleder den aldrig från entiteten, och bara förifyllningen från en värmepumpsenhet föreslår en. Med Styrning av pumpens uppgift på Styrning skriver optimeraren planens rumstemperatur (Inomhustemperatur) eller vattentemperatur (Framledningstemperatur, Returtemperatur) till den här entiteten.",
               "flow_min_lift_k": "Med Styrning av pumpens uppgift på Styrning skrivs vattenbörvärdet vid planens lägsta effekt som det uppmätta inkommande vattnet plus detta: värmepumpens retur, bufferttank, golvretur eller ventilens utlopp, och för en entitet med Returtemperatur bara de tre första. 5 K passar en styrenhet som håller sin framledning på börvärdet. En styrenhet som tar börvärdet som mål för returvattnet antas köra kompressorn hårdare ju högre målet ligger över returen och vill troligen ha mindre; 1–2 K är en startpunkt att kontrollera mot kompressorns uppmätta frekvens och effekt, inte ett uppmätt värde.",
               "flow_heat_c": "Vattenbörvärdet som skrivs vid full planerad effekt, och det högsta som skrivs medan planen styr. 55 °C passar ett framledningsmål. För en entitet med Returtemperatur väljs det över den högsta retur du ser vid normal uppvärmning plus höjningen, och inte högre än styrenheten accepterar; för en lågtemperatur-golvvärme kan 35–40 °C vara en startpunkt att kontrollera mot mätningar. Under 30 °C erbjuds inte: grinden som betyder av är 25 °C för ett framledningsmål och 20 °C för ett returmål.",
               "space_setpoint_power_feedback": "På som standard. Verkar bara med Styrning av pumpens uppgift på Styrning, enheten Framlednings- eller Returtemperatur och en effektgivare för värmepumpen; annars ändras ingenting. Efter 5 minuters starthållning sänks vattenbörvärdet medan den uppmätta förbrukningen ligger över planerad nivå, höjs medan den ligger under och hålls inom 10 %, i stället för att följa det stigande inkommande vattnet. Av skriver inkommande vatten plus höjningen. Krav på styrenheten: dess värmehysteres högst höjningen (Luxtronik: 0,5 K), annars startas inte en stoppad kompressor; dess lägsta returmål under returen under eldningssäsongen; dess integration läser den minst var 10:e minut och återställer värmeläget efter en omstart av styrenheten, eftersom ett Luxtronik Smart Home Interface släpper alla satta värden efter 600 s utan åtkomst; och inget annat verktyg skriver samma register (en Luxtronik kastar då skrivningar tyst).",
@@ -1106,7 +1106,7 @@
           "pv_export_price_entity": "Använd denna i stället om din ersättning följer spotpriset.",
           "pv_enabled": "Låter planen köra värmepumpen på ditt eget överskott i stället för att sälja det för mindre än vad köpt el kostar.",
           "pv_peak_kw": "Anläggningens installerade toppeffekt. Används för att skala produktionsprognosen.",
-          "pv_production_entity": "Valfritt. En sensor med faktisk produktion ersätter prognosen för det aktuella steget med den uppmätta effekten (begränsad till den installerade effekten); senare timmar förblir på prognosen från solinstrålning.",
+          "pv_production_entity": "Valfritt. En sensor med faktisk produktion ersätter prognosens aktuella steg med vad taket levererar just nu, högst den installerade effekten; senare steg förblir modellerade.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
       },
@@ -1122,7 +1122,7 @@
         },
         "data_description": {
           "away_presence_entity": "En person, enhetsspårare, kalender eller närvarosensor. Plan-sidans brytare vinner tills den slås av. Att en person är 'inte hemma' betyder fortfarande bortavaro när brytaren är av.",
-          "away_dhw_min_temperature": "Legionellacykeln körs fortfarande, enligt sitt vanliga schema; den tidsätts inte efter din återkomst.",
+          "away_dhw_min_temperature": "Legionellacykeln körs fortfarande med sitt vanliga intervall; den tidsätts inte efter din hemkomst.",
           "away_temperature": "Temperaturen som hålls under bortavaron. Låg nog att spara, hög nog att skydda hus och rör.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst.",
           "holiday_calendar_entity": "När den här kalendern är på ersätter lovets komfort och varmvattenfönster vardag/helg för den dagen. Bortasänkning vinner om bortaläget är aktivt."
@@ -1348,7 +1348,7 @@
               "dhw_disinfection_mode": "Observera läser brytaren och skriver aldrig till den. Styra slår på den när en legionellacykel börjar och av den när cykeln är slut, men slår aldrig på den medan pumpens driftläge inte gör varmvatten. Den slår bara av en brytare som den själv slog på: en brytare som redan var på när cykeln började lämnas i fred. En begränsning: om du slår på brytaren för hand medan en cykel som optimeraren startade pågår, slås den av när cykeln är slut, eftersom de två inte går att skilja åt. Styra kräver brytaren ovan.",
               "dhw_disinfection_switch_entity": "En brytare eller hjälpare som startar värmepumpens eget legionellaprogram. I läget observera läses bara dess tillstånd och visas bland varmvattensensorns attribut; i läget styra slår integrationen på den när en desinfektionscykel börjar och av den när cykeln är slut.",
               "dhw_elastic_legionella_enabled": "Låt legionellacykeln köras en dag eller två tidigare när elen är ovanligt billig, i stället för att alltid vänta till sista dagen. Sista dagen hålls alltid.",
-              "dhw_free_disinfection_enabled": "Om en vedpanna, solslinga eller elpatron får tanken till legionellatemperatur räknas det som en genomförd cykel i stället för att köra en till. Av: att nå temperaturen (inom 1 °C) räknas direkt, hur kort stund det än är; på: tanken måste först hålla den i 20 minuter.",
+              "dhw_free_disinfection_enabled": "En vedpanna, solslinga eller elpatron som får tanken till legionellatemperatur räknas som en genomförd cykel i båda lägena. Av: direkt; på: först när tanken har hållit den temperaturen i 20 minuter, så en kort topp räknas inte.",
               "dhw_legionella_min_interval_days": "Med Låt legionellacykeln välja en billig dag på får en cykel köras tidigt en billig dag först efter så här många dagar sedan den förra. Den fördröjer aldrig en cykel som är förfallen enligt det vanliga intervallet och gör ingenting medan det valet är av.",
               "dhw_quantile_targets_enabled": "Lär in hur mycket varmvatten varje tidsfönster faktiskt använder en tung dag, och gör tanken redo för det i stället för för genomsnittsdagen. Kräver tanktemperaturgivare, konfigurerade varmvattenfönster och ett par veckors underlag."
             }
@@ -1364,7 +1364,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "vvc_pump_entity": "En brytare som styr VVC-pumpen. När den är satt och varmvattenfönster är konfigurerade körs pumpen bara under de fönstren plus förvarmningstiden nedan; utan fönster, eller med varmvatten av, hålls den på.",
+          "vvc_pump_entity": "En brytare som styr VVC-pumpen. Om satt körs pumpen bara under dina varmvattenfönster, plus förvarmningstiden nedan. Med varmvattnet avslaget eller utan fönster lämnas den på.",
           "vvc_lead_minutes": "Hur långt före ett varmvattenfönster cirkulationspumpen startar, så att slingan redan är varm när fönstret öppnar.",
           "after_save": "Sparandet slår igenom direkt; detta val avgör vart dialogen går näst."
         }
@@ -1383,7 +1383,7 @@
           "after_save": "Efter sparande"
         },
         "data_description": {
-          "main_fuse_amperes": "Husets huvudsäkring i ampere, från ditt nätavtal. 0 lämnar den oinställd, vilket håller säkringsrådgivaren och säkringsvakten vilande; utrymmessensorn följer då bara din effekttariffstopp och saknar värde om det inte finns någon effekttariff heller. Det finns inget säkert standardvärde att gissa, och ett felaktigt skulle strypa ett större hus.",
+          "main_fuse_amperes": "Husets huvudsäkring i ampere, från ditt nätavtal. 0 lämnar den oinställd, vilket håller säkringsrådgivaren och säkringsvakten vilande medan utrymmessensorn bara följer effekttariffens topp, otillgänglig utan effekttariff — det finns inget säkert standardvärde att gissa, och ett felaktigt skulle strypa ett större hus.",
           "main_fuse_phases": "Nästan alla svenska hus har 3 faser.",
           "fuse_guard_enabled": "Begränsar värmepumpens planerade effekt till vad säkringen lämnar efter resten av huset. Om en begränsning skulle göra komfortgolvet onåbart säger planen det på sina sensorer i stället för att tyst bli kall.",
           "peak_guard_enabled": "Bevakar effektmätaren live och håller tillbaka eldrivet varmvatten samt sänker värmekurvan resten av mätfönstret när fönstret beräknas sätta en ny fakturerad topp. Kräver en effektmätare; en kall tank eller ett brutet komfortgolv vinner alltid över vakten.",
@@ -1434,7 +1434,7 @@
               "snow_roof_factor_enabled": "Räkna med mindre sol efter kraftigt snöfall"
             },
             "data_description": {
-              "open_window_relax_enabled": "Fönsterdetektorn pausar alltid inlärningen — den delen är gratis och alltid på. Detta sänker dessutom den kallaste acceptabla temperaturen med 1 °C (aldrig under 15 °C) medan ett fönster verkar stå öppet, så att värmepumpen slutar betala för att värma trädgården. Av som standard eftersom det flyttar riktig värme: ett felaktigt flaggat fönster betyder ett något svalare hus.",
+              "open_window_relax_enabled": "Fönsterdetektorn pausar alltid inlärningen — den delen är gratis och alltid på. Detta sänker dessutom den lägsta inomhustemperatur som planen godtar med 1 °C, aldrig under 15 °C, medan ett fönster verkar stå öppet, så att värmepumpen slutar betala för att värma trädgården. Av som standard eftersom det flyttar riktig värme: ett felaktigt flaggat fönster betyder ett något svalare hus.",
               "outage_recovery_enabled": "Efter ett avbrott startar allt samtidigt — kallt hus, kall tank, hela grannskapet — vilket är exakt när en ny månadstopp sätts. Med detta på öppnar ett långt uppehåll i uppdateringarna ett tvåtimmarsfönster där effektavgiften tas på allvar från första kW och varmvattnet köar 45 minuter bakom husvärmen, om inte tanken är riktigt låg.",
               "precip_type_enabled": "Regn blöter ner klimatskalet och ökar värmeförlusten; snö gör det inte. Utan detta behandlas en snöig prognos som regn och planen köper värme för en våt vägg som förblir torr. Kräver Open-Meteo-anslutningen för snödata.",
               "snow_roof_factor_enabled": "I två dygn efter kraftigt snöfall halveras den modellerade solvinsten — snö på takfönster och låga vinterrutor blockerar solen planen räknade med. Medvetet grovt: en faktor och en hålltid, ingen smältmodell."
@@ -1530,7 +1530,7 @@
           "dhw_legionella_interval_days": "Intervall för legionellaskydd",
           "silent_mode_windows": "Pumpens eget nattläge-schema",
           "heat_pump_max_power": "Värmepump max effekt (kW)",
-          "space_setpoint_unit": "Vad den börvärdesenheten förväntar sig",
+          "space_setpoint_unit": "Vad den börvärdesentiteten förväntar sig",
           "mixing_valve_write_target_kind": "Vad styrenheten förväntar sig",
           "outdoor_temp_entity": "Utomhusgivare",
           "dhw_temp_entity": "Givare för varmvattenberedarens temperatur",
diff --git a/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py b/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
index 607977916f..1fb60ff78a 100644
--- a/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
+++ b/dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
@@ -10,10 +10,20 @@ through ``tools/audit/seat/features_block.py``. Run from the repository root:
     python3 dev/audit/harnesses/r10_arbiter_off_restore_mutants.py
 
 It prints mutant_run's lines, ``SURVIVED NULL`` then ``KILLED <name>`` per
-mutant at the fix head, once for M01-M20 on the arbiter block and once for the
-seam mutants (M21 to M38; M33 retired) on the water-setpoint feedback block, and exits with
+mutant at the fix head, once for M01-M20 and M35 on the arbiter block and once for the
+seam mutants (M21 to M38; M33 and M36 retired) on the water-setpoint feedback block, and exits with
 mutant_run's status. A mutant whose ``old`` text no longer occurs exactly once
 is refused before anything runs.
+
+R10-HOTFIX-FLOW-SETPOINT-STUCK re-anchored M02, M03, M11, M13, M23, M35 and
+M37 on the lines it rewrote: the own-write check no longer holds the write but
+substitutes the baseline (M03 drops that check), and Off keeps the own space
+write until a restore replaces it (M35, renamed, forgets it, and moves to the
+arbiter block, whose stuck-install Off-and-On check kills it). M36 (Off's guard
+reads the dropped write) is retired: that guard no longer reads it, by design.
+The seam block now ends at the replay's `_fb_floor = _fb_sim(clamp=(26.4`: the
+bare `_fb_floor = _fb_sim(` marker matched an earlier simulation #3469 added,
+so the block stopped before every Carry 8 check and no seam mutant could die.
 """
 from __future__ import annotations
 
@@ -37,14 +47,14 @@ MUTANTS = json.loads(r"""
  {
   "name": "M02_no_arm",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
   "new": "    return False"
  },
  {
   "name": "M03_no_own_refusal",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "f\"space_baseline_own:{entity}\", own,",
-  "new": "f\"space_baseline_own:{entity}\", False,"
+  "old": "    if own:\n        baseline = _space_target(inp, inp.plan, now, None)\n",
+  "new": "    if False:\n        baseline = _space_target(inp, inp.plan, now, None)\n"
  },
  {
   "name": "M04_before_ignored",
@@ -91,8 +101,8 @@ MUTANTS = json.loads(r"""
  {
   "name": "M11_off_no_persist",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "new": "if held.written or held.retry or held.dropped:"
+  "old": "if held.written or held.retry or held.space_before is not None:",
+  "new": "if held.written or held.retry:"
  },
  {
   "name": "M12_no_grace",
@@ -103,8 +113,8 @@ MUTANTS = json.loads(r"""
  {
   "name": "M13_forget_keeps_before",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None",
-  "new": "held.written, held.misses, held.retry, held.dropped = {}, {}, {}, {}"
+  "old": "held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None",
+  "new": "held.written, held.misses, held.retry = {}, {}, {}"
  },
  {
   "name": "M14_factory_none",
@@ -147,21 +157,28 @@ MUTANTS = json.loads(r"""
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
   "old": "    if not entity:\n        return None\n    return off_restore.Restorer(",
   "new": "    return off_restore.Restorer("
+ },
+ {
+  "name": "M35_forget_drops_own_write",
+  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
+  "old": "    held.dropped = {} if own is None else {\"space_setpoint\": own}\n",
+  "new": "    held.dropped = {}\n"
  }
 ]
 """)
 #: The seam with R10-WATER-SETPOINT-FEEDBACK (the merge of #3405): the off
 #: restore's edit adoption reads the space slot before ``hold``, so a loop
 #: write's controller cut is ``_clamp_cut``'s, never a person's baseline; and
-#: the record a loop move drops (``_note_sent``) still refuses the optimizer's
-#: own write as the restore's baseline (roster Carry 8). Their checks sit in
+#: the record a loop move drops (``_note_sent``) still keeps the optimizer's
+#: own write from the restore's baseline (roster Carry 8). Their checks sit in
 #: the feedback block, which needs the arbiter block's imports.
 SEAM_BLOCK = (
     'env PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py '
     '--prelude "from harness import FakeEntry as _pa_entry" '
     '--prelude "from types import SimpleNamespace as _PaNS" '
     '--prelude "from heatpump_optimizer.const import MODE_AUTO as _PA_AUTO, MODE_OFF as _PA_OFF" '
-    '"# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380" "_fb_floor = _fb_sim("'
+    '--prelude "from heatpump_optimizer import off_restore as _pa_or" '
+    '"# --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380" "_fb_floor = _fb_sim(clamp=(26.4"'
 )
 SEAM_MUTANTS = json.loads(r"""
 [
@@ -180,8 +197,8 @@ SEAM_MUTANTS = json.loads(r"""
  {
   "name": "M23_arm_ignores_dropped_record",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "    last = record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
-  "new": "    last = record[0] if record is not None else None\n"
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
+  "new": "    return record[0] if record is not None else None\n"
  },
  {
   "name": "M24_prev_not_kept",
@@ -243,23 +260,11 @@ SEAM_MUTANTS = json.loads(r"""
   "old": "(held.written, held.misses, held.retry, held.dropped)",
   "new": "(held.written, held.misses, held.retry)"
  },
- {
-  "name": "M35_forget_keeps_dropped",
-  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "held.written, held.misses, held.retry, held.dropped, held.space_before = {}, {}, {}, {}, None",
-  "new": "held.written, held.misses, held.retry, held.space_before = {}, {}, {}, None"
- },
- {
-  "name": "M36_off_ignores_dropped",
-  "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "new": "if held.written or held.retry or held.space_before is not None:"
- },
  {
   "name": "M37_arm_reads_run",
   "file": "custom_components/heatpump_optimizer/pump_arbiter.py",
-  "old": "    last = record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
-  "new": "    last = record[0] if record is not None else None if held.feedback is None else held.feedback.prev_c\n"
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")\n",
+  "new": "    return record[0] if record is not None else None if held.feedback is None else held.feedback.prev_c\n"
  },
  {
   "name": "M38_load_unfiltered",
diff --git a/dev/audit/harnesses/r10_rca_setpoint_latch.py b/dev/audit/harnesses/r10_rca_setpoint_latch.py
new file mode 100644
index 0000000000..a6b5ccd72a
--- /dev/null
+++ b/dev/audit/harnesses/r10_rca_setpoint_latch.py
@@ -0,0 +1,162 @@
+"""R10-RCA-SETPOINT-LATCH-DEADLOCK detector: from every persisted arbiter state,
+the demanded space write reaches the entity with no person acting.
+
+    python3 -I dev/audit/harnesses/r10_rca_setpoint_latch.py --check <checkout> [--passes N]
+
+The pump-duty arbiter (``pump_arbiter.apply``) runs on a flow set-point
+install, with Control on and a plan that heats the house on every step. The
+stub device takes every write. A reference install with no persisted state
+gives the demanded target. Then each persisted starting state is driven for
+N one-minute passes (default 10): the space record (none, the idle gate
+``FLOW_GATE_C``, or the heating flow), the record a loop move dropped (none,
+or the gate; only where the tree has ``ArbiterState.dropped``), the entity's
+reading (the gate, 40, or the heating flow), and whether the off restore is
+already armed on the entity (only where the tree has ``pump_arbiter.CONSUMER``).
+Every state must end with the entity reading the demanded target.
+
+Exit codes: 0 every state converges; 1 a state never gets the demanded
+write (the defect); 2 the reference install was never written, so the
+harness can see no write (the skip control); 3 the modules were loaded from
+outside the named checkout (provenance refusal).
+"""
+from __future__ import annotations
+
+import argparse
+import asyncio
+import itertools
+import os
+import sys
+from datetime import datetime, timedelta, timezone
+from types import SimpleNamespace as NS
+
+UTC = timezone.utc
+T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
+TUYA = ("Heating", "DHW (Hot Water)", "Heating + DHW", "Cooling", "Cooling + DHW")
+SPACE = "number.water_set"
+
+
+def main() -> int:
+    ap = argparse.ArgumentParser()
+    ap.add_argument("--check", required=True, help="checkout root to measure")
+    ap.add_argument("--passes", type=int, default=10)
+    args = ap.parse_args()
+    root = os.path.realpath(args.check)
+    # Older trees read package data relative to the cwd: measure from the root.
+    os.chdir(root)
+    for sub in ("custom_components", "tests", "tests/hastub"):
+        sys.path.insert(0, os.path.join(root, sub))
+
+    import harness  # noqa: PLC0415
+    from heatpump_optimizer import pump_arbiter as pa  # noqa: PLC0415
+    from heatpump_optimizer.const import MODE_AUTO  # noqa: PLC0415
+    from heatpump_optimizer.entry_config import EntryConfig  # noqa: PLC0415
+
+    for mod in (harness, pa):
+        if not os.path.realpath(mod.__file__).startswith(root + os.sep):
+            print(f"REFUSED {mod.__name__} loaded from {mod.__file__}, not {root}")
+            return 3
+
+    def plan(n):
+        return NS(
+            timestamps=[T0 + timedelta(minutes=15 * i) for i in range(n)],
+            power_schedule=[1.5] * n,
+            dhw_power_schedule=[0.0] * n,
+            optimal_setpoints=[21.0] * n,
+        )
+
+    class Coord:
+        def __init__(self, reading: str, entry_id: str) -> None:
+            self.hass = harness.FakeHass({
+                "select.pump_mode": harness.FakeState("Heating", attributes={"options": list(TUYA)}),
+                "number.dhw_set": harness.FakeState("48", attributes={"min": 40, "max": 63}),
+                SPACE: harness.FakeState(reading, attributes={"min": 25, "max": 63}),
+            })
+            self._config = EntryConfig.from_mapping({
+                "pump_duty_mode": "control",
+                "heat_pump_mode_entity": "select.pump_mode",
+                "dhw_setpoint_entity": "number.dhw_set",
+                "space_setpoint_entity": SPACE,
+                "space_setpoint_unit": "flow",
+            })
+            self._mode = MODE_AUTO
+            self.stale = False
+            self._current_action = {"mode": "eco"}
+            self._optimization_result = plan(400)
+            self._thermal_model = NS(params=NS(min_electrical_power=0.4), curve_flow_temp=lambda _o: 34.2)
+            self._thermal_params = NS(dhw_setpoint=48.0, dhw_max_temp=48.0, dhw_cycle_temp=None)
+            self._current_state = NS(outdoor_temperature=0.0)
+            self.entry = harness.FakeEntry(entry_id=entry_id)
+
+        def _plan_is_stale(self) -> bool:
+            return self.stale
+
+        @property
+        def effective_config(self):
+            return self._config
+
+        @property
+        def thermal_params(self):
+            return self._thermal_params
+
+        def arbiter_inputs(self):
+            return pa.ArbiterInputs(
+                hass=self.hass, config=self._config, mode=self._mode,
+                plan=self._optimization_result, plan_stale=self.stale, entry_released=False,
+                state=self._current_state, thermal=self._thermal_model, params=self._thermal_params,
+                action=self._current_action, measured_power_kw=None, disinfecting=False,
+            )
+
+        async def async_set_mode(self, mode) -> None:
+            self._mode = mode
+
+    def converge(coord: Coord) -> float:
+        for i in range(args.passes):
+            asyncio.run(pa.apply(coord, T0 + timedelta(minutes=i)))
+            for _d, _s, data in coord.hass.services.calls:  # the device takes each write
+                value = data.get("option", data.get("value"))
+                coord.hass.states.get(data["entity_id"]).state = str(value)
+            coord.hass.services.calls.clear()
+        return float(coord.hass.states.get(SPACE).state)
+
+    ids = itertools.count()
+    ref_reading = "40"
+    target = converge(Coord(ref_reading, f"latch{next(ids)}"))
+    if target == float(ref_reading):
+        print(f"SKIP the reference install was never written (reads {target}): nothing to measure")
+        return 2
+
+    gate, heat = float(pa.FLOW_GATE_C), target
+    has_dropped = "dropped" in getattr(pa.ArbiterState, "__dataclass_fields__", {})
+    has_restore = hasattr(pa, "CONSUMER")
+    if has_restore:
+        from heatpump_optimizer import off_restore  # noqa: PLC0415
+    states = list(itertools.product(
+        (None, gate, heat),
+        (None, gate) if has_dropped else (None,),
+        (gate, 40.0, heat),
+        (False, True) if has_restore else (False,),
+    ))
+    failed = 0
+    for written, dropped, reading, armed in states:
+        coord = Coord(f"{reading:g}", f"latch{next(ids)}")
+        held = pa.state_for(coord)
+        held.loaded = True
+        if armed:
+            coord.entry.runtime_data = coord
+            asyncio.run(off_restore.async_arm(coord.hass, coord.entry, coord._config, pa.CONSUMER))
+        if written is not None:
+            held.written["space_setpoint"] = (written, T0 - timedelta(hours=1))
+        if dropped is not None:
+            held.dropped["space_setpoint"] = dropped
+        final = converge(coord)
+        if final != target:
+            failed += 1
+            print(f"FAIL written={written} dropped={dropped} reading={reading:g} armed={armed}: "
+                  f"reads {final:g} after {args.passes} passes, demanded {target:g}")
+    print(f"SUMMARY root={root} demanded={target:g} states={len(states)} failed={failed} "
+          f"passes={args.passes} dropped_axis={has_dropped} armed_axis={has_restore}")
+    return 1 if failed else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/programme/delivery/3561.md b/dev/programme/delivery/3561.md
new file mode 100644
index 0000000000..fb498f03e4
--- /dev/null
+++ b/dev/programme/delivery/3561.md
@@ -0,0 +1 @@
+- [#3561](https://github.com/tvofi/heatpump_optimizer/pull/3561) — **open**, R10-HOTFIX-FLOW-SETPOINT-STUCK: r10 hotfix flow setpoint stuck (R10-HOTFIX-FLOW-SETPOINT-STUCK)
diff --git a/dev/programme/delivery/3576.md b/dev/programme/delivery/3576.md
new file mode 100644
index 0000000000..84ac680f85
--- /dev/null
+++ b/dev/programme/delivery/3576.md
@@ -0,0 +1 @@
+- [#3576](https://github.com/tvofi/heatpump_optimizer/pull/3576) — **open**, Correct the away, disinfection, circulation and set-point-unit text to what the code does (R10-DOCS-STRINGS-RESIDUE)
diff --git a/dev/programme/delivery/3579.md b/dev/programme/delivery/3579.md
new file mode 100644
index 0000000000..4b5e4045ab
--- /dev/null
+++ b/dev/programme/delivery/3579.md
@@ -0,0 +1 @@
+- [#3579](https://github.com/tvofi/heatpump_optimizer/pull/3579) — **open**, R10-HOTFIX-ENTITIES-REDACTION-FLAKE: r10 hotfix entities redaction flake (R10-HOTFIX-ENTITIES-REDACTION-FLAKE)
diff --git a/dev/programme/delivery/3580.md b/dev/programme/delivery/3580.md
new file mode 100644
index 0000000000..afa5d6d8a8
--- /dev/null
+++ b/dev/programme/delivery/3580.md
@@ -0,0 +1 @@
+- [#3580](https://github.com/tvofi/heatpump_optimizer/pull/3580) — **open**, R10-DOCS-STRINGS-RESIDUE (part 2): r10 docs strings residue p2 (R10-DOCS-STRINGS-RESIDUE)
diff --git a/docs/configuration.md b/docs/configuration.md
index d8ded8775a..1ed78bccfc 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -71,7 +71,7 @@ reported as a connection problem rather than as a bad token.
 
 | Setting | Default | What it means |
 |---|---|---|
-| Name for this integration | Heat Pump Optimizer | Shown in front of every entity this integration creates. |
+| Name for this integration | Heat Pump Optimizer | The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer. |
 | Electricity price source | Tibber | Where hourly electricity prices come from: Tibber (needs the token below) or a price sensor entity you already have. |
 | Tibber API token | — (**required with the Tibber source**) | Reads your hourly electricity prices. Create one at developer.tibber.com. The field still shows when the price source is a price entity — not needed then, so leave it empty. |
 | Price sensor (Nord Pool or similar) | — (**required with the price-entity source**) | A `sensor` publishing the current electricity price, read instead of Tibber. |
@@ -527,7 +527,7 @@ device page and on the card, not here.
 | Away indicator | none | `person`, `device_tracker`, `calendar`, `binary_sensor` | Polarity is handled for you: a person being *not home* still means away when the Plan-page toggle is off. |
 | Holiday-profile calendar | none | a `calendar` | When this calendar is on, holiday comfort and holiday hot-water windows replace the weekday/weekend pair for that day. Away setback still wins if away is active. |
 | Temperature while away | 16.0 °C | 5–21, 0.5 steps | Low enough to save, high enough to protect the house and its plumbing. With the mold guard on, the mold-safe temperature outranks it and can hold the room near the comfort target in a humid house, so away then saves little space-heating energy ([Away and the mold guard](how-it-works.md#away-and-holiday-mode)). |
-| Hot water minimum while away | 20.0 °C | 10–55 | The anti-legionella cycle still runs, timed to finish before you get back. |
+| Hot water minimum while away | 20.0 °C | 10–55 | The anti-legionella cycle still runs on its usual interval; it is not timed to your return. |
 
 ### Quick setup
 
@@ -876,9 +876,12 @@ writes, at every 15-minute plan step:
   over it until you turn it off (outside the entity's own minimum and
   maximum, the nearest value it takes); a value set while it is off is read again
   when it next writes. A reading equal to the optimizer's own last write is
-  never taken as yours: after an upgrade from a version without this, the
-  set-point is not written until it reads anything else, so set it on the
-  pump once. The mode and the hot-water set-point are not restored.
+  never taken as yours: after an upgrade from a version without this, the value
+  restored is the one the optimizer holds when the plan is not in charge (35 °C
+  or the weather curve for a water set-point, the planned room temperature for
+  an indoor one), and the optimizer writes the set-point from its first pass.
+  Set it on the pump once while the optimizer is on to have your own
+  value restored instead. The mode and the hot-water set-point are not restored.
 - **A write the pump does not hold is retried.** If the value written back
   still does not hold, a warning repair notice is raised and the value is sent
   again every 5 minutes; the notice clears on the first write that holds, or
@@ -1060,7 +1063,7 @@ Tank size, daily draw, inlet water and the disinfection extras. The first-menu
 | Cold water inlet sensor | none | a temperature sensor | When set, its live reading replaces the model above. |
 | Greywater heat recovery effectiveness | 0.0 | 0–0.9, 0.05 steps | The fraction of drain heat a drain-water recovery unit returns. 0 means none installed. |
 | Learn heavy-day hot water targets | off | on/off | Makes the tank ready for a heavy day rather than an average one. Needs a tank sensor, configured time frames, and a couple of weeks of evidence. |
-| Credit disinfection from any heat source | off | on/off | If a wood boiler, solar coil or immersion heater already got the tank hot enough and held it there, count that as a completed cycle. |
+| Credit disinfection from any heat source | off | on/off | A wood boiler, solar coil or immersion heater that gets the tank to the anti-legionella temperature counts as a completed cycle either way. Off, it counts the moment the tank is within 1 °C of that temperature; on, only after the tank has spent 20 minutes within 0.5 °C of it, so a short peak credits nothing. |
 | Let the anti-legionella cycle pick a cheap day | off | on/off | Allows the cycle to run a day or two early when electricity is unusually cheap. The deadline is still always honoured. |
 | Earliest anti-legionella re-run | 5 days | 1–14 | A floor on how close together cycles may run, however cheap the day. |
 | Pump's disinfection switch | none | `switch` / `input_boolean` | A switch or helper that starts the heat pump's own anti-legionella program. Its state is read on every update and published on the hot water sensor's attributes as `dhw_disinfection_switch`; the attribute is absent while no switch is set. |
@@ -1074,7 +1077,7 @@ The DHW loop pump. The heating-circuit circulation pump lives on
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
-| Hot water circulation pump switch | none | `switch` / `input_boolean` | When set, the circulation loop pump runs only during your hot water time frames plus the lead time below. |
+| Hot water circulation pump switch | none | `switch` / `input_boolean` | When set, the circulation loop pump runs only during your hot water time frames plus the lead time below. With hot water off or no time frames, it is left on. |
 | Start circulation before a time frame | 20 min | 0–120, 5 steps | So the loop is already hot when the time frame opens. |
 
 ### Solar panels
@@ -1090,7 +1093,7 @@ what consuming actually costs you.
 | Overall system efficiency | 0.80 | 0.3–1.0, 0.01 steps | Everything between sunlight and the meter: inverter losses, panel temperature, dirt, orientation. |
 | Export compensation per kWh | 0.0 | 0–10, 0.01 steps | What you are paid for an exported kWh. While you have surplus, that is what an extra kWh of heating really costs. |
 | Export compensation entity | none | a sensor | Use this instead if your compensation follows the spot price. |
-| Solar production sensor | none | a `power` sensor | Lets the forecast correct itself against what the roof actually delivers. |
+| Solar production sensor | none | a `power` sensor | Replaces the forecast's current step with what the roof delivers now, capped at the installed capacity; later steps stay modelled. |
 
 ### Self-learning and diagnostics
 
@@ -1113,7 +1116,7 @@ opt-in learners are on **Advanced learning features**.
 | Setting | Default | Range | What it means |
 |---|---|---|---|
 | Staggered recovery after a power cut | off | on/off | After an outage everything restarts at once, which is exactly when a new monthly peak gets set. This opens a two-hour recovery window where hot water queues 45 minutes behind space heating unless the tank is genuinely low. A restart that finds the last saved heartbeat ahead of the clock (the clock was set back, so the gap cannot be known) counts as an outage too. |
-| Ease heating while a window is open | off | on/off | The detector always pauses learning; this additionally lowers the target by 1 °C while a window appears open. Off by default because it moves real heat. |
+| Ease heating while a window is open | off | on/off | The detector always pauses learning; this additionally lowers the coldest temperature the plan accepts by 1 °C, never below 15 °C, while a window appears open. Off by default because it moves real heat. |
 | Plan around immersion heater use | off | on/off | Repeated immersion use raises the hot-water planning margin so the heat pump gets there first. It also declares the immersion element: when the power meter reads more than the compressor's nameplate can draw, the excess books as its own ledger line. With this off and neither pump heater flag on, nothing books as resistive heat, because the meter alone cannot tell an element from a compressor over its configured nameplate. |
 | Tell snow from rain in the forecast | off | on/off | Rain soaks the envelope and raises heat loss; snow does not. Needs the Open-Meteo connection. |
 | Assume less sun after heavy snowfall | off | on/off | Halves modelled solar gain for two days after heavy snowfall. Deliberately crude. |
@@ -1126,7 +1129,7 @@ opt-in learners are on **Advanced learning features**.
 
 | Setting | Default | Range | What it means |
 |---|---|---|---|
-| Main fuse size | 0 A | 0–125 | From your grid contract. **0 means unconfigured**, which keeps the fuse advisor, the fuse guard and the headroom sensor dormant — there is no safe default to guess. |
+| Main fuse size | 0 A | 0–125 | From your grid contract. **0 means unconfigured**, which keeps the fuse advisor and the fuse guard dormant; the headroom sensor then follows the capacity-tariff peak alone and is unavailable without a capacity tariff — there is no safe default to guess. |
 | Phases | 3 | 1–3 | Nearly every Swedish house is 3-phase. |
 | Keep the plan under the main fuse | off | on/off | Caps planned power at what the fuse leaves after the rest of the house. If a cap would make the comfort floor unreachable, the plan says so instead of silently going cold. |
 | Live peak guard | off | on/off | Watches the power meter and, when the current metering window is projected to set a new billed peak, holds back electric hot water and nudges the heat curve down for the rest of that window. Needs a power meter. |
diff --git a/docs/dashboard-card.md b/docs/dashboard-card.md
index 4e1bb4d63c..43544808cb 100644
--- a/docs/dashboard-card.md
+++ b/docs/dashboard-card.md
@@ -575,8 +575,9 @@ capacity charge at the month's billed peak, the kWh a resistive heater drew
 beyond what the compressor can (the pump's own tank booster or backup heater
 while its flag is on, or an immersion heater you have declared), and
 compressor wear in starts. The total adds those lines and nothing else; a
-note under it says which lines it covers and that the savings figure
-compares spot cost only. Wear reads "not priced" until you set a
+note under it says which lines it covers and what the savings figure
+compares: the plan and the thermostat baseline are both priced at spot
+plus the per-kWh grid fee. Wear reads "not priced" until you set a
 compressor replacement cost. Beside it, **Where the money went** splits the
 spot line by the plan's reason for each kWh, largest first; the bars add up
 to the spot line. Every receipt the integration keeps (24 months) is on the
@@ -697,8 +698,8 @@ configured, the way it did before:
 - **Each ranked row carries its spread and an *estimated* badge.** The spread
   is in degrees the model's predictions can move — one unit, comparable
   between sensors. The line under the heading names what drove the replay:
-  your install's measured delivery where there is history, configured
-  defaults otherwise.
+  the mean electrical power your heat pump has measured where there is
+  history, half its configured maximum otherwise.
 - **A sensor the estimate cannot price is listed below the ranked rows, with
   its reason** — the outdoor probe whose job the weather entity already does,
   the floor-return probe that feeds a state estimate rather than a learned
@@ -724,7 +725,7 @@ on the Health page names which. The pill appears once that sensor has a state.
 
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="img/card/health-dark.png">
-  <img alt="The Health tab: a Plan column solved 12 minutes ago with the next solve, its 96 steps and the solve time, and a Still learning column with savings waiting for the first settled month; an Inputs row with a stale outdoor temperature sensor (its age and its limit) and fresh indoor and hot-water sensors; a What the model has learned block whose rows each carry a value, their evidence in words and a bar: house heat loss 142 W/K, not observable without a power meter, solar gain at a window scale of 1.15 and still learning, hot-water tank cooling at 0.9 °C per hour, heat pump efficiency normal at a COP scale of 0.97, and a 24-bar internal-gains strip peaking around 18:00; a Something looks wrong? row with a Download diagnostics button, a Debug collection row with a Start button, and the six-item first-plan checklist, three ticked, with Assign on the power meter and Show on the insight sensors" src="img/card/health-light.png">
+  <img alt="The Health tab: a Plan column solved 12 minutes ago with the next solve, its 96 steps and the solve time, and a Still learning column with savings waiting for the first month with a booked saving; an Inputs row with a stale outdoor temperature sensor (its age and its limit) and fresh indoor and hot-water sensors; a What the model has learned block whose rows each carry a value, their evidence in words and a bar: house heat loss 142 W/K, not observable without a power meter, solar gain at a window scale of 1.15 and still learning, hot-water tank cooling at 0.9 °C per hour, heat pump efficiency normal at a COP scale of 0.97, and a 24-bar internal-gains strip peaking around 18:00; a Something looks wrong? row with a Download diagnostics button, a Debug collection row with a Start button, and the six-item first-plan checklist, three ticked, with Assign on the power meter and Show on the insight sensors" src="img/card/health-light.png">
 </picture>
 
 *Everything here is read from the integration's sensors; the card computes no
@@ -735,8 +736,8 @@ figure of its own.* The page shows, top to bottom:
   solve took (the Optimization Status sensor's `solve_time_ms`). Its pill reads
   **Stale** once the plan is past the limit the header's own status pill uses.
   **Still learning** lists the sensors that are enabled by default and wait
-  for evidence, each with its reason in words: savings (the first settled
-  month), heat pump COP (a power meter, then some running time), prediction
+  for evidence, each with its reason in words: savings (the first month with a
+  booked saving), heat pump COP (a power meter, then some running time), prediction
   accuracy (the first scored interval) and the optimization score (the first
   scored day). Home Assistant hides an unavailable entity's attributes, so the
   card cannot read the sensor's own `waiting_for` code and the reason is keyed
diff --git a/docs/how-it-works.md b/docs/how-it-works.md
index ccbb2bb9c7..8d334740c5 100644
--- a/docs/how-it-works.md
+++ b/docs/how-it-works.md
@@ -617,9 +617,10 @@ redundant cycle.
 
 Two opt-in refinements:
 
-- **Free disinfection**: if another heat source holds the tank at the
-  disinfection temperature *long enough*, that counts as a completed cycle. It
-  is hold-verified, so a momentary blip at 60 °C credits nothing.
+- **Hold-verified disinfection**: with *Credit disinfection from any heat
+  source* on, a heat source resets the timer only once the tank has held the
+  disinfection temperature for 20 minutes, so a momentary blip at 60 °C credits
+  nothing; with it off, any observation resets it at once, as above.
 - **A price-aware cycle**: inside its interval the cycle may run a day or two
   early (no sooner than a configurable minimum, default 5 days) when a known
   price beats what a typical remaining day is expected to bottom out at. The
@@ -646,7 +647,8 @@ Everything here is inert until configured or until evidence exists:
   Advisor** reports the cheapest setpoint that still covers your learned heavy
   days — read-only, the decision stays yours.
 - **Circulation pumps** (opt-in): a VVC loop pump runs only around your demand
-  frames, with a lead (default 20 minutes) so the loop is hot when they open.
+  frames, with a lead (default 20 minutes) so the loop is hot when they open;
+  with hot water off or no frames it is left on.
   The space circulation pump pauses only in provably idle, warm slots, and is
   forced on whenever heat is planned, the heat curve is being driven, any room
   is near its comfort floor, or it is freezing outside.
@@ -921,7 +923,7 @@ that cannot save them anything should not be able to cost them anything.
 
 A week away is the largest single saving a heating system can offer: a deep
 setback plus hot water held only at its away minimum (20 °C unless you change
-it), except for a legionella cycle timed to complete before you return.
+it), while the legionella cycle keeps its usual interval.
 
 What makes this more than a manual setpoint is the **return time**. Knowing when
 the house must be comfortable again lets the recovery heat be bought in the
diff --git a/docs/setup.md b/docs/setup.md
index ebd69f7217..03cd658ae1 100644
--- a/docs/setup.md
+++ b/docs/setup.md
@@ -88,7 +88,7 @@ answers of the whole flow.*
 
 | Setting | What it asks |
 |---|---|
-| Name for this integration | Shown in front of every entity the integration creates. |
+| Name for this integration | The title of this entry under Devices & services. Entity names use the fixed device name, Heat Pump Optimizer. |
 | Electricity price source | `Tibber` uses your API token; `Price entity (Nord Pool or similar)` reads a Home Assistant price sensor. |
 | Tibber API token | Required only when the source is Tibber. Checked against Tibber before the flow continues — a network failure is reported as a connection problem, not as a bad token. |
 | Price sensor (Nord Pool or similar) | Required only when the source is an entity. |
diff --git a/tests/closures.json b/tests/closures.json
index 84537ffb10..f9bdfbc9f5 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -4352,6 +4352,7 @@
    "dev/audit/harnesses/r10_rca_name_kept_plant.py",
    "dev/audit/harnesses/r10_rca_roster_drain_replay.py",
    "dev/audit/harnesses/r10_rca_sav_estimate.py",
+   "dev/audit/harnesses/r10_rca_setpoint_latch.py",
    "dev/audit/harnesses/r10_rca_sweep_settle_loop.py",
    "dev/audit/harnesses/r10_readme_marketplace_pipeline.mjs",
    "dev/audit/harnesses/r10_recarry_head.py",
diff --git a/tests/doc_claims.py b/tests/doc_claims.py
index 7dadc4197c..5bff089bce 100644
--- a/tests/doc_claims.py
+++ b/tests/doc_claims.py
@@ -4664,6 +4664,164 @@ def check_power_feedback_claims() -> None:
             all(fact in (pa._clamp_cut.__doc__ or "") for fact in (comment_id, "10104", "10103")))
 
 
+# ---------------------------------------------------------------------------
+# R10-DOCS-STRINGS-RESIDUE carries 5 to 13: reader sentences and option texts
+# that described behaviour the code does not have. Each arm takes its fact
+# from the producing code, refuses the old wording in the reader corpus and in
+# all four string files, and requires the corrected sentence to state the fact.
+# ---------------------------------------------------------------------------
+_STRING_FILES = {
+    name: json.loads((PKG / rel).read_text())
+    for name, rel in (("strings.json", "strings.json"), ("en.json", "translations/en.json"),
+                      ("de.json", "translations/de.json"), ("sv.json", "translations/sv.json"))
+}
+
+#: (carry, the old wording in any language) -- the sentences these carries corrected.
+_RESIDUE_REFUSED = (
+    ("Carry 5", r"lowers the (?:heating )?target by|Heizziel um|värmemålet med"),
+    ("Carry 6", r"headroom sensor dormant|Reserve inaktiv|utrymmessensorn vilande"),
+    ("Carry 7", r"correct itself against|Prognose sich anhand|rätta sig efter"),
+    ("Carry 8", r"in front of every (?:entity|sensor)|vorangestellt|Visas framför"),
+    ("Carry 9", r"compares spot cost only"),
+    ("Carry 10", r"measured delivery"),
+    ("Carry 11", r"first settled month"),
+)
+
+
+def _string_leaves(tree: object):
+    if isinstance(tree, dict):
+        for value in tree.values():
+            yield from _string_leaves(value)
+    elif isinstance(tree, str):
+        yield tree
+
+
+def residue_hits(corpus: dict[str, str], string_files: dict[str, dict]) -> dict[str, list[str]]:
+    """Every refused wording still present, by carry: the document or string file it is in."""
+    texts = {**{k: " ".join(v.split()) for k, v in corpus.items()},
+             **{k: "\n".join(_string_leaves(v)) for k, v in string_files.items()}}
+    return {carry: hits for carry, pattern in _RESIDUE_REFUSED
+            if (hits := [name for name, text in texts.items() if re.search(pattern, text)])}
+
+
+def menu_title_mismatches(strings: dict) -> tuple[int, list[str]]:
+    """Every options-menu entry whose target step has a title: (pairs compared, the pairs whose names differ).
+
+    Design choice: the options flow only. Its menu entries name the page they open; the config flow's are
+    actions ("Continue setup", "Describe my building (recommended)") and legitimately differ from the title."""
+    pairs, bad = 0, []
+    for flow in ("options",):
+        steps = strings.get(flow, {}).get("step", {})
+        for body in steps.values():
+            for key, label in (body.get("menu_options") or {}).items():
+                title = steps.get(key, {}).get("title")
+                if title is None:
+                    continue
+                pairs += 1
+                if title != label:
+                    bad.append(f"{flow}.step.{key}: menu {label!r}, title {title!r}")
+    return pairs, bad
+
+
+def check_docs_strings_residue() -> None:
+    R.section("reader text against the code that produces it (R10-DOCS-STRINGS-RESIDUE carries 5 to 13)")
+    import inspect
+    import types
+    from heatpump_optimizer import away, const, coordinator, entry_config, ledger, topology
+
+    flat = {k: " ".join(v.split()) for k, v in DOCS.items()}
+    cfg, en = flat.get("configuration.md", ""), _STRING_FILES["en.json"]
+    opts = en["options"]["step"]
+    hits = residue_hits(CORPUS, _STRING_FILES)
+    R.check("no reader doc or string file keeps a corrected sentence's old wording", not hits, repr(hits))
+
+    # Carry 5: the open-window relax widens the floor and leaves the target.
+    relax, floor = const.OPEN_WINDOW_RELAX_C, const.ECONOMY_ABSOLUTE_FLOOR
+    fields = dict.fromkeys(away._OPT_FIELDS, None) | {"target_temp": 21.0, "min_temp": 20.0}
+    thermal = types.SimpleNamespace(**dict.fromkeys(away._DHW_FIELDS, 45.0))
+    banded, _ = away.solve_bands(types.SimpleNamespace(**fields), thermal, None, (relax,))
+    R.check("solve_bands lowers min_temp by OPEN_WINDOW_RELAX_C and leaves target_temp",
+            banded["min_temp"] == 20.0 - relax and banded["target_temp"] == 21.0, repr(banded))
+    low, _ = away.solve_bands(types.SimpleNamespace(**(fields | {"min_temp": floor})), thermal, None, (relax,))
+    R.check("solve_bands never takes min_temp below ECONOMY_ABSOLUTE_FLOOR", low["min_temp"] == floor, repr(low))
+    phrase = f"by {relax:g} °C, never below {floor:g} °C"
+    R.check(f"configuration.md's open-window row says the coldest accepted temperature drops {phrase}",
+            f"lowers the coldest temperature the plan accepts {phrase}" in cfg)
+    R.check(f"the open-window option text says {phrase}",
+            phrase in opts["learning_features"]["sections"]["weather"]["data_description"]["open_window_relax_enabled"])
+
+    # Carry 6: fuse 0 is no fuse, so the headroom follows the capacity-tariff peak alone.
+    def fuse(amps: int) -> float | None:
+        cfg_ = types.SimpleNamespace(main_fuse_amperes=amps, main_fuse_phases=3)
+        cfg_.fuse_kw_at = lambda a: entry_config.EntryConfig.fuse_kw_at(cfg_, a)
+        return entry_config.EntryConfig.fuse_kw(cfg_)
+
+    R.check("EntryConfig.fuse_kw answers None at main fuse 0, and a capacity at 16 A (control)",
+            fuse(0) is None and fuse(16) is not None, repr((fuse(0), fuse(16))))
+    R.check("configuration.md's main-fuse row says the headroom sensor follows the capacity-tariff peak",
+            "the headroom sensor then follows the capacity-tariff peak alone" in cfg)
+    R.check("the main-fuse option text says the headroom sensor follows the capacity-tariff peak",
+            "headroom sensor following the capacity-tariff peak alone"
+            in opts["grid_connection"]["data_description"]["main_fuse_amperes"])
+
+    # Carry 7: the measured production replaces step 0 only.
+    pv = re.search(r"production\[0\] = min\(self\._pv_production, config\.peak_kw\)",
+                   inspect.getsource(coordinator))
+    R.check("the coordinator replaces production[0] alone, capped at peak_kw (anchor)", pv is not None)
+    for where, text in (("configuration.md", cfg),
+                        ("the PV sensor option text", opts["solar_pv"]["data_description"]["pv_production_entity"])):
+        R.check(f"{where} says only the current step is replaced, capped at the installed capacity",
+                "current step" in text and "capped at the installed capacity" in text)
+
+    # Carry 8: every entity is named from the device, whose name is a literal.
+    device = re.search(r'DeviceInfo\(\s*identifiers=.*?name="([^"]+)"', inspect.getsource(coordinator), re.S)
+    R.check("the coordinator's DeviceInfo names the device by a literal (anchor)", device is not None)
+    name = device.group(1) if device else "<none>"
+    for where, text in (("setup.md", flat.get("setup.md", "")), ("configuration.md", cfg),
+                        ("the name option text", en["config"]["step"]["user"]["data_description"]["name"])):
+        R.check(f"{where} says entities use the fixed device name {name!r}",
+                f"fixed device name, {name}" in text)
+
+    # Carry 9: both sides of the saving are priced at spot plus the per-kWh fee.
+    R.check("observe_spot_and_settle_savings prices the settlement at spot + fee_per_kwh (anchor)",
+            "spot=spot + fee_per_kwh" in inspect.getsource(ledger.MonthlyLedger.observe_spot_and_settle_savings))
+    card = flat.get("dashboard-card.md", "")
+    R.check("dashboard-card.md says both sides are priced at spot plus the per-kWh grid fee",
+            "both priced at spot plus the per-kWh grid fee" in card)
+
+    # Carry 10: the replay's power is the measured mean, else a fraction of the maximum.
+    half = {0.5: "half"}.get(topology._ADVISOR_DUTY_FRACTION)
+    R.check("_ADVISOR_DUTY_FRACTION is a fraction the page can name", half is not None,
+            repr(topology._ADVISOR_DUTY_FRACTION))
+    R.check("dashboard-card.md names the measured mean power, else the configured maximum's fraction",
+            f"mean electrical power your heat pump has measured where there is history, {half} its configured maximum"
+            in card)
+
+    # Carry 11: the Health picture's alt text names the booked-saving wait.
+    R.check("dashboard-card.md's Health picture waits for the first month with a booked saving",
+            "savings waiting for the first month with a booked saving" in card)
+
+    # Carry 13: one options page, one name per language.
+    for fname, strings in _STRING_FILES.items():
+        pairs, bad = menu_title_mismatches(strings)
+        R.check(f"{fname}: every options-menu entry names its page by the page's title ({pairs} pairs)",
+                pairs > 0 and not bad, "; ".join(bad))
+
+    # Null controls: each old wording, put back, fires; a renamed page title fires.
+    for carry, old in (
+        ("Carry 5", "this additionally lowers the target by 1 °C"), ("Carry 6", "the headroom sensor dormant"),
+        ("Carry 7", "Lets the forecast correct itself against what the roof"),
+        ("Carry 8", "Shown in front of every entity"), ("Carry 9", "the savings figure compares spot cost only"),
+        ("Carry 10", "your install's measured delivery"), ("Carry 11", "waiting for the first settled month"),
+    ):
+        R.check(f"{carry}: the old wording, put back, is refused (null control)",
+                carry in residue_hits({"setup.md": old}, {}))
+    renamed = json.loads(json.dumps(_STRING_FILES["de.json"]))
+    renamed["options"]["step"]["grid"]["title"] = "Netz-Spitzentarif"
+    R.check("a de grid page titled apart from its menu entry is refused (null control)",
+            bool(menu_title_mismatches(renamed)[1]))
+
+
 def check_stateless() -> None:
     R.section("the user pages describe the integration as it is, with no change history (R10-USER-DOCS-FINAL)")
     pages = _user_pages()
@@ -4754,7 +4912,7 @@ def flow_number_pins() -> list[tuple[str, str, float]]:
         ("options.step.building.sections.valve.data_description.flow_curve_cop_enabled",
          r"at most to a (\d+) °C supply", flow_lift.FLOW_SUPPLY_MAX_C),
         ("options.step.hot_water_tank.sections.disinfection.data_description.dhw_free_disinfection_enabled",
-         r"hold it for (\d+) minutes", const.DHW_LEGIONELLA_HOLD_MINUTES),
+         r"held that temperature for (\d+) minutes", const.DHW_LEGIONELLA_HOLD_MINUTES),
         ("config.step.temperature.data_description.min_temperature",
          r"lowers it by a further (\d+(?:\.\d+)?) K", const.ECONOMY_MIN_TEMP_WIDENING),
         ("config.step.temperature.data_description.min_temperature",
@@ -4762,7 +4920,7 @@ def flow_number_pins() -> list[tuple[str, str, float]]:
         ("config.step.temperature.data_description.min_temperature",
          r"never below (\d+) °C", const.ECONOMY_ABSOLUTE_FLOOR),
         ("options.step.learning_features.sections.weather.data_description.open_window_relax_enabled",
-         r"by (\d+) °C \(never below", const.OPEN_WINDOW_RELAX_C),
+         r"accepts by (\d+) °C, never below", const.OPEN_WINDOW_RELAX_C),
     ]
     return pins
 
@@ -4862,9 +5020,13 @@ def check_flow_text_claims() -> None:
             not bad, "; ".join(bad))
     indoor = planted["options"]["step"]["entities"]["sections"]["indoor"]["data_description"]
     indoor["space_setpoint_unit"] = "The unit is a declaration: this integration never recommends a space set-point."
+    # Planted, not read from the tree: R10-HOTFIX-FLOW-SETPOINT-STUCK has replaced
+    # the shipped sentence, so only a plant still proves the exemption is all that
+    # hides it.
+    owned_key = "options.step.entities.sections.indoor.data_description.space_setpoint_entity"
+    indoor["space_setpoint_entity"] = _OWNED_ELSEWHERE[owned_key]
     R.check("null: the other group's sentence is found once it is not exempted",
-            "options.step.entities.sections.indoor.data_description.space_setpoint_entity"
-            in flow_write_findings(texts, slots, owned={}))
+            owned_key in flow_write_findings(planted, slots, owned={}))
     R.check("null: the pre-fix space set-point unit sentence is found",
             "options.step.entities.sections.indoor.data_description.space_setpoint_unit"
             in flow_write_findings(planted, slots))
@@ -4914,6 +5076,7 @@ def main() -> int:
     check_surface_coverage()
     check_power_feedback_claims()
     check_flow_text_claims()
+    check_docs_strings_residue()
     check_stateless()
     return R.close("checks")
 
diff --git a/tests/entities.py b/tests/entities.py
index fd2d94aeee..82b89583cc 100644
--- a/tests/entities.py
+++ b/tests/entities.py
@@ -25813,15 +25813,80 @@ R.check(
         if repr(_c) in _blob
     ),
 )
+def _diag_payload_at(when):
+    """The diagnostics payload with the clock pinned to ``when``."""
+    dt_util.freeze(when)
+    try:
+        _hass = FakeHass()
+        _entry = FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
+        _entry.runtime_data = integration.HeatPumpOptimizerCoordinator(
+            _hass, FakeEntry(data=dict(_DIAG_DATA), options=dict(_DIAG_OPTIONS))
+        )
+        return asyncio.run(_diag_mod.async_get_config_entry_diagnostics(_hass, _entry))
+    finally:
+        dt_util.freeze(None)
+
+
+def _clockless(a, b):
+    """``a`` with every value differing from ``b`` replaced by None, at any depth.
+
+    ``a`` and ``b`` are one payload taken at two pinned clocks, so what differs
+    is what the clock wrote (``exported_at``, the draw-range timestamp, any
+    later one) and no field is named here. A rounded coordinate such as "18.1"
+    is searched only in what is left, because a clock reading holds one by
+    chance (the check failed 1 of 2711 on main at 50373173).
+    """
+    if isinstance(a, dict) and isinstance(b, dict):
+        return {k: _clockless(v, b.get(k)) for k, v in a.items()}
+    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
+        return [_clockless(x, y) for x, y in zip(a, b)]
+    return a if a == b else None
+
+
+_CLOCK_A = datetime(2026, 1, 5, 3, 4, 5, tzinfo=UTC)
+_CLOCK_B = datetime(2026, 7, 9, 10, 11, 12, tzinfo=UTC)
+_ROUNDED = tuple(
+    str(round(_c, 1)) for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
+)
+
+
+def _rounded_hits(first, second):
+    """Each rounded coordinate found in the clock-free payload, with its context."""
+    blob = _json.dumps(_clockless(first, second), default=str)
+    return [
+        f"{r!r} in ...{blob[max(0, i - 40) : i + 20]}..."
+        for r in _ROUNDED
+        for i in [blob.find(r)]
+        if i >= 0
+    ]
+
+
+_diag_a = _diag_payload_at(_CLOCK_A)
+_diag_b = _diag_payload_at(_CLOCK_B)
 R.check(
     "the location is redacted whole, from data and from options, not coarsened",
     _diag_at(_diag, "config_setup", const.CONF_SOLAR_LOCATION) == _HA_REDACTED
     and _diag_at(_diag, "config", const.CONF_SOLAR_LOCATION) == _HA_REDACTED
-    and not any(
-        str(round(_c, 1)) in _blob
-        for _c in (_DIAG_LAT, _DIAG_LON, _DIAG_OPT_LAT, _DIAG_OPT_LON)
-    ),
-    repr(_diag_at(_diag, "config", const.CONF_SOLAR_LOCATION)),
+    and not _rounded_hits(_diag_a, _diag_b),
+    repr(_diag_at(_diag, "config", const.CONF_SOLAR_LOCATION))
+    + " / rounded matches: "
+    + "; ".join(_rounded_hits(_diag_a, _diag_b)),
+)
+# The flake, deterministically: a clock reading that holds a rounded coordinate
+# fails the whole-blob search and passes the clock-free one.
+_diag_p = _diag_payload_at(datetime(2026, 1, 5, 3, 4, 18, 100000, tzinfo=UTC))
+R.check(
+    "the rounded-coordinate search ignores a clock reading that contains one",
+    any(r in _json.dumps(_diag_p, default=str) for r in _ROUNDED)
+    and not _rounded_hits(_diag_p, _diag_a),
+    "poisoned clock: whole-blob hit expected, clock-free hit not",
+)
+# Null control: a genuinely coarsened coordinate still fails the new search.
+_coarse = {**_diag_a, "config": {**_diag_a["config"], "coarse_probe": _ROUNDED[0]}}
+_coarse_b = {**_diag_b, "config": {**_diag_b["config"], "coarse_probe": _ROUNDED[0]}}
+R.check(
+    "a genuinely coarsened coordinate in the payload still fails the clock-free search",
+    bool(_rounded_hits(_coarse, _coarse_b)),
 )
 R.check(
     "a coordinate nested below the top level, inside a list, is redacted",
diff --git a/tests/features.py b/tests/features.py
index 01a0f60761..536dde8d55 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -63652,17 +63652,125 @@ def _pa_upgraded(reading):
 
 _pa_up, _pa_up_first, _pa_up_sent = _pa_upgraded("30")
 _pa_up_n, _pa_up_n_first, _pa_up_n_sent = _pa_upgraded("31")
+# Re-pinned by R10-HOTFIX-FLOW-SETPOINT-STUCK: this check pinned "the write
+# waits", which on an upgrade held every space write, boosts included, until a
+# person set the controller. The own write is still never the baseline; the
+# baseline row's hold (35 degC: the curve's 34.2 under the rated hold) is.
 R.check(
     "R10-ARBITER-OFF-RESTORE: a reading equal to the arbiter's own last write is never captured as "
-    "the baseline, and the write waits; null control: a reading of the person's own is captured, "
-    "written over, and restored on off",
-    _pa_up_first == [] and _pa_up_sent == 0 and _pa_space(_pa_up) == []
+    "the baseline: the baseline row's 35 is, and the write is sent; null control: a reading of the "
+    "person's own is captured, written over, and restored on off",
+    _pa_up_first == [25.0] and _pa_up_sent == 1 and _pa_space(_pa_up) == [35.0]
     and _pa_up_n_first == [25.0] and _pa_up_n_sent == 1 and _pa_space(_pa_up_n) == [31.0],
     f"{_pa_up_first=} {_pa_up_sent=} {_pa_up.writes()=} / {_pa_up_n_first=} {_pa_up_n_sent=} "
     f"{_pa_up_n.writes()=}",
 )
 
 
+# R10-HOTFIX-FLOW-SETPOINT-STUCK (tvofi, 2026-11-13, a Rotenso on v7.1.15 held
+# at 25 degC through a boost): from any persisted arbiter state, a space step
+# or a boost under Control writes the space set-point within one pass. The
+# states: a record equal to the reading with no baseline armed, in memory and
+# loaded from the pre-#3404 store shape (an upgrade, then a restart).
+def _pa_stuck(duties, record, boost=False, stored=False):
+    """The space writes of one pass at minute 1; ``record`` the persisted last write or None."""
+    coord = _PaCoord(_PA_TUYA, duties=duties)
+    coord.device("number.water_set", "25")
+    at = _PA_T0 - timedelta(hours=1)
+    if record is not None and stored:
+        _pa_aio.run(_pa._store(coord).async_save({"written": {"space_setpoint": [record, at.isoformat()]}}))
+    elif record is not None:
+        held = _pa.state_for(coord)
+        held.loaded = True
+        held.written["space_setpoint"] = (record, at)
+    if boost:
+        boost_mod.held_for(coord).set("space", True, _PA_T0)
+    _pa_run(coord, 1)
+    return _pa_space(coord)
+
+
+_pa_stuck_rows = {
+    (duties, boost, stored): _pa_stuck(duties, 25.0, boost, stored)
+    for duties, boost in (("-", True), ("s", False)) for stored in (False, True)
+}
+_pa_stuck_null = {(duties, boost): _pa_stuck(duties, None, boost) for duties, boost in (("-", True), ("s", False))}
+R.check(
+    "R10-HOTFIX-FLOW-SETPOINT-STUCK: a boost over an idle step, and a space step, write the 55 degC "
+    "ceiling in one pass from a persisted own write of 25 equal to the reading with no baseline armed, "
+    "in memory and loaded from the store; null control: the same passes with no record write 55 too",
+    all(v == [55.0] for v in _pa_stuck_rows.values()) and all(v == [55.0] for v in _pa_stuck_null.values()),
+    f"{_pa_stuck_rows=} {_pa_stuck_null=}",
+)
+
+
+def _pa_stuck_off(hand=None):
+    """Off after the released write from a persisted own 25: what the restore writes.
+
+    ``hand``: a value the person sets at the controller before the pass.
+    """
+    coord = _PaCoord(_PA_TUYA, duties="ssss")
+    held = _pa.state_for(coord)
+    held.loaded = True
+    held.written["space_setpoint"] = (25.0, _PA_T0 - timedelta(hours=1))
+    coord.device("number.water_set", "25" if hand is None else hand)
+    _pa_settled(coord, 1)
+    return _pa_turn_off(coord), _pa_space(coord)
+
+
+
+
+def _pa_stuck_cycle():
+    """A stuck install (own 25 persisted, reading 25, nothing armed) turned Off and On again.
+
+    Returns what the Off restored, the space writes after On, and what a later Off restores.
+    """
+    coord = _PaCoord(_PA_TUYA, duties="ssss")
+    held = _pa.state_for(coord)
+    held.loaded = True
+    held.written["space_setpoint"] = (25.0, _PA_T0 - timedelta(hours=1))
+    coord.device("number.water_set", "25")
+    first = _pa_turn_off(coord)
+    coord._mode = _PA_AUTO
+    coord.hass.services.calls.clear()
+    _pa_settled(coord, 46)
+    coord.hass.services.calls.clear()
+    _pa_run(coord, 47)
+    on = _pa.state_for(coord).written.get("space_setpoint", (None,))[0]
+    coord.hass.services.calls.clear()
+    return first, on, _pa_turn_off(coord), _pa_space(coord)
+
+
+def _pa_dropped_over(written, dropped):
+    """The space writes of three passes from a written record over a dropped own 25, reading 25."""
+    coord = _PaCoord(_PA_TUYA, duties="ssss")
+    held = _pa.state_for(coord)
+    held.loaded = True
+    held.written["space_setpoint"] = (written, _PA_T0 - timedelta(hours=1))
+    held.dropped["space_setpoint"] = dropped
+    coord.device("number.water_set", "25")
+    for minute in (1, 2, 3):
+        _pa_settled(coord, minute)
+    return float(coord.hass.states.get("number.water_set").state)
+
+
+R.check(
+    "R10-HOTFIX-FLOW-SETPOINT-STUCK (R10-RCA-SETPOINT-LATCH-DEADLOCK (b)): a stuck install turned Off "
+    "(nothing armed, nothing restored) and On writes 55 at once, and a later Off restores the baseline "
+    "row's 35, never the 25 the optimizer left; (c): a written 55 over a dropped own 25 with the entity "
+    "reading 25 reaches 55; null control: a dropped 40 that is not the reading reaches 55 too",
+    _pa_stuck_cycle() == (0, 55.0, 1, [35.0])
+    and _pa_dropped_over(55.0, 25.0) == 55.0 and _pa_dropped_over(55.0, 40.0) == 55.0,
+    f"{_pa_stuck_cycle()=} {_pa_dropped_over(55.0, 25.0)=} {_pa_dropped_over(55.0, 40.0)=}",
+)
+R.check(
+    "R10-HOTFIX-FLOW-SETPOINT-STUCK: Optimizer off after the write a persisted own 25 no longer holds "
+    "restores the baseline row's 35, never the 25 gate; null control: a value set by hand, 40, is "
+    "restored as set",
+    _pa_stuck_off() == (1, [35.0]) and _pa_stuck_off("40") == (1, [40.0]),
+    f"{_pa_stuck_off()=} {_pa_stuck_off('40')=}",
+)
+
+
 def _pa_between(reading, switch_off=False, then=None):
     """Baseline 53; the gate 25, then a space step's target; then the entity reads ``reading``.
 
@@ -63811,13 +63919,17 @@ def _pa_restored_twice(via):
     _pa_run(again, 0)
     _pa_run(again, 30)
     again.hass.services.calls.clear()
-    return _pa_turn_off(again)
+    return _pa_turn_off(again), _pa_space(again)
 
 
+# The restored value, not only the count: since R10-HOTFIX-FLOW-SETPOINT-STUCK
+# an own write left on the record no longer refuses the arm but substitutes
+# the baseline row's 35, so only the value tells a record the restore dropped
+# (and saved) from one it kept.
 R.check(
     "R10-ARBITER-OFF-RESTORE: after an off or an unload restored a baseline equal to the plan's value, "
-    "a restart captures it again and the next off restores it",
-    _pa_restored_twice("unload") == 1 and _pa_restored_twice("off") == 1,
+    "a restart captures it again and the next off restores it, 25, not the baseline row's 35",
+    _pa_restored_twice("unload") == (1, [25.0]) and _pa_restored_twice("off") == (1, [25.0]),
     f"{_pa_restored_twice('unload')=} {_pa_restored_twice('off')=}",
 )
 _pa_subs = _PaCoord(_PA_TUYA)
@@ -88193,7 +88305,7 @@ R.check(
 import asyncio as _fb_aio  # noqa: E402
 
 
-def _fb_own(moves, wrote=True):
+def _fb_own(moves, wrote=True, arm=True):
     coord = _FbCoord()
     held = _fb_pa.state_for(coord)
     if wrote:
@@ -88201,23 +88313,35 @@ def _fb_own(moves, wrote=True):
         held.feedback = _fb_running(3600, 0)
     for target in moves:
         _fb_pa._note_sent(held, held.feedback, target, 26.4)
-    sent = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET))
+    sent = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET, _FB_NOW)) if arm else None
     return sent, coord, held
 
 
+def _fb_baseline(coord):
+    """The space baseline the off restore holds, or None when unarmed."""
+    armed = _fb_aio.run(_pa_or.async_armed_entry(coord.hass, coord.entry, _fb_pa.CONSUMER))
+    return None if armed is None else armed["value"]
+
+
+# Re-pinned by R10-HOTFIX-FLOW-SETPOINT-STUCK: the own write is no longer
+# refused, which held the write; the baseline row's 30.0 (the rated 35 in
+# return terms, under the 32 ceiling) is captured in its place.
 _fb_own_one, _fb_own_two, _fb_own_none = _fb_own([25.8]), _fb_own([25.8, 25.6]), _fb_own([], wrote=False)
 _fb_rs_coord, _fb_rs_held = _fb_own([25.8])[1:]
 _fb_rs_coord.entry.runtime_data = _fb_rs_coord
 _fb_pa._space_restored(_fb_rs_coord.entry, _FB_SET, 26.0)
 R.check(
     "R10-ARBITER-OFF-RESTORE x R10-WATER-SETPOINT-FEEDBACK (Carry 8): a loop move's "
-    "dropped record still refuses the optimizer's own 26.0 as an unarmed key's baseline, "
-    "after one move and after two with no write between; a restore ends the run; an "
-    "arbiter that never wrote captures it",
-    _fb_own_one[0] is False and _fb_own_two[0] is False and _fb_own_two[2].feedback.prev_c == 26.0
-    and _fb_rs_held.feedback is None and _fb_own_none[0] is True,
-    f"one {_fb_own_one[0]}, two {_fb_own_two[0]} (prev {_fb_own_two[2].feedback.prev_c}), "
-    f"restored run {_fb_rs_held.feedback}, never wrote {_fb_own_none[0]}",
+    "dropped record still keeps the optimizer's own 26.0 from an unarmed key's baseline, "
+    "after one move and after two with no write between, and the write is sent; a restore "
+    "ends the run; an arbiter that never wrote captures it",
+    _fb_own_one[0] is True and _fb_baseline(_fb_own_one[1]) == 30.0
+    and _fb_own_two[0] is True and _fb_baseline(_fb_own_two[1]) == 30.0
+    and _fb_own_two[2].feedback.prev_c == 26.0
+    and _fb_rs_held.feedback is None and _fb_own_none[0] is True and _fb_baseline(_fb_own_none[1]) == 26.0,
+    f"one {_fb_own_one[0]} {_fb_baseline(_fb_own_one[1])}, two {_fb_own_two[0]} {_fb_baseline(_fb_own_two[1])} "
+    f"(prev {_fb_own_two[2].feedback.prev_c}), restored run {_fb_rs_held.feedback}, "
+    f"never wrote {_fb_own_none[0]} {_fb_baseline(_fb_own_none[1])}",
 )
 # Round 2 of Carry 8 (#3404's verdict at 4a5abf4a): the loop run ends on
 # paths that are neither a write nor a restore -- a pass off the loop
@@ -88230,12 +88354,12 @@ R.check(
 
 
 def _fb_own_after(end):
-    sent, coord, held = _fb_own([25.8])
+    _sent, coord, held = _fb_own([25.8], arm=False)
     end(coord, held)
     held = _fb_pa.state_for(coord)  # a restart's is a fresh state
     run = held.feedback
-    after = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET))
-    return sent, None if run is None else run.prev_c, after
+    after = _fb_aio.run(_fb_pa._arm_space(coord.arbiter_inputs(), coord.entry, held, _FB_SET, _FB_NOW))
+    return _fb_baseline(coord), None if run is None else run.prev_c, after
 
 
 def _fb_end_stale(coord, held):
@@ -88265,29 +88389,32 @@ _fb_own_ends = {
 print("CARRY8-RUN-ENDS", _fb_own_ends)
 R.check(
     "R10-ARBITER-OFF-RESTORE x R10-WATER-SETPOINT-FEEDBACK (Carry 8, round 2): the "
-    "own-write refusal survives every end of the loop run while the dropped write is "
-    "held -- an off pass, a missing base, a compressor stop, a stale run, a restart",
-    all(sent is False and prev is None and after is False for sent, prev, after in _fb_own_ends.values()),
-    f"(before, run prev_c after, after) {_fb_own_ends}",
+    "own-write fact survives every end of the loop run while the dropped write is "
+    "held -- an off pass, a missing base, a compressor stop, a stale run, a restart: "
+    "the arm after it sends the write and captures 30.0, not the own 26.0",
+    all(after is True and prev is None and baseline == 30.0 for baseline, prev, after in _fb_own_ends.values()),
+    f"(baseline, run prev_c after, after) {_fb_own_ends}",
 )
 # Where the fact stops mattering or ends: once the person moves the
 # controller (25.0) the arm captures and the write lands, after which the
 # armed key never consults it -- the controller reading 26.0 again with the
-# record gone is not refused; a restore (_space_restored) and a release (Off
-# forgets the record, even one that is only the dropped write) end it, and
-# a stored value the arbiter could not have written is not loaded.
+# record gone is not refused; a restore (_space_restored) ends it, and a
+# stored value the arbiter could not have written is not loaded. Re-pinned by
+# R10-HOTFIX-FLOW-SETPOINT-STUCK: Off with no restore no longer ends it (the
+# entity still reads the optimizer's number, and the arm after On must not
+# take it as the person's), and a written record becomes the dropped one.
 # Control: before each, the fact is held.
-_fb_wr_sent, _fb_wr_coord, _fb_wr_held = _fb_own([25.8])
+_fb_wr_sent, _fb_wr_coord, _fb_wr_held = _fb_own([25.8], arm=False)
 _fb_wr_before = dict(_fb_wr_held.dropped)
 _fb_wr_coord.hass.states.set(_FB_SET, FakeState("25.0", attributes={"min": 15, "max": 45, "step": 0.1}))
 _fb_aio.run(_fb_pa._write(_fb_wr_coord, _fb_wr_coord.arbiter_inputs(), "space_setpoint", 25.8, _FB_NOW))
 _fb_wr_written = _fb_wr_held.written.pop("space_setpoint", (None,))[0]
 _fb_wr_coord.hass.states.set(_FB_SET, FakeState("26.0", attributes={"min": 15, "max": 45, "step": 0.1}))
-_fb_wr_after = _fb_aio.run(_fb_pa._arm_space(_fb_wr_coord.arbiter_inputs(), _fb_wr_coord.entry, _fb_wr_held, _FB_SET))
+_fb_wr_after = _fb_aio.run(_fb_pa._arm_space(_fb_wr_coord.arbiter_inputs(), _fb_wr_coord.entry, _fb_wr_held, _FB_SET, _FB_NOW))
 _fb_junk = _FbCoord()
 _fb_aio.run(_fb_pa._store(_fb_junk).async_save({"written": {}, "dropped": {"space_setpoint": "26.0 degC"}}))
 _fb_aio.run(_fb_pa._load(_fb_junk))
-_fb_off_coord, _fb_off_held = _fb_own([25.8])[1:]
+_fb_off_coord, _fb_off_held = _fb_own([25.8], arm=False)[1:]
 _fb_off_held.written.clear()
 _fb_off_before = dict(_fb_off_held.dropped)
 _fb_off_coord._mode = _PA_OFF
@@ -88295,11 +88422,11 @@ _fb_aio.run(_fb_pa._arbitrate(_fb_off_coord, _fb_off_held, _fb_off_coord.arbiter
                               _fb_pa.DUTY_CONTROL, _FB_NOW))
 R.check(
     "R10-ARBITER-OFF-RESTORE (Carry 8, round 2): the dropped own write is not consulted "
-    "once a write lands on the armed key, and ends when a restore writes the baseline or "
-    "Off releases the pump",
+    "once a write lands on the armed key, and ends when a restore writes the baseline; "
+    "Off with nothing restored keeps it",
     _fb_wr_before == {"space_setpoint": 26.0} and _fb_wr_written == 25.8 and _fb_wr_after is True
     and _fb_rs_held.dropped == {}
-    and _fb_off_before == {"space_setpoint": 26.0} and _fb_off_held.dropped == {}
+    and _fb_off_before == {"space_setpoint": 26.0} and _fb_off_held.dropped == {"space_setpoint": 26.0}
     and _fb_pa.state_for(_fb_junk).dropped == {},
     f"write {_fb_wr_before}, wrote {_fb_wr_written}, armed after {_fb_wr_after}, "
     f"restore {_fb_rs_held.dropped}, off {_fb_off_before} -> {_fb_off_held.dropped}, "
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
similarity index 60%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
index 3c3cb57df3..7674632b2b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.59013da4.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 59013da4",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 87a4cba9",
   "killed_by": "tests/features.py",
-  "old": "        if held.written or held.retry or held.dropped or held.space_before is not None:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+  "old": "        if held.written or held.retry or held.space_before is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
new file mode 100644
index 0000000000..d52a0f3f66
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space GUARD_OFF bc2b348d",
+  "killed_by": "tests/features.py",
+  "old": "    if own:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
similarity index 75%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
index f29be90584..eedc551b94 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.cbe69d47.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL cbe69d47",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL ee5d5b70",
   "killed_by": "tests/features.py",
-  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER, baseline_c=baseline)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
similarity index 64%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
index d5ce21b72b..6150d6a294 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP 605f504a",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP dd8cf122",
   "killed_by": "tests/guard_pins.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity, now)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
similarity index 50%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
index 9a74fc5f22..febd8f790b 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.605f504a.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL 605f504a",
-  "killed_by": "tests/structure.py",
-  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity)",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL dd8cf122",
+  "killed_by": "tests/features.py",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
new file mode 100644
index 0000000000..1ef3907eac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_own_space_write.RETURN_DEL.98fa5cc9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_own_space_write RETURN_DEL 98fa5cc9",
+  "killed_by": "tests/features.py",
+  "old": "    return record[0] if record is not None else held.dropped.get(\"space_setpoint\")",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
