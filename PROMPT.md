CLOUD REVIEWER seat for PR #3561 of tvofi/heatpump_optimizer, at head 30b069508f194240f90ddd05cb5cfee0613814e1. Bus nonce: ff2b1f4c7c38a33fa032981c5120be5d. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin 30b069508f194240f90ddd05cb5cfee0613814e1`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3561 --head 30b069508f194240f90ddd05cb5cfee0613814e1 --reviewed-head 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1 --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. This is a later round over the reviewed head 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1: its scope is the packet's `## Review scope` line, the delta and the previous verdict's findings when it reads `delta`, widened only to the exact already-reviewed code a production (custom_components/) delta puts at non-obvious risk that CI would not detect, the verdict naming path and risk; an instrument, test, policy or body delta never widens it (fix-review.md step 12). Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify 30b069508f194240f90ddd05cb5cfee0613814e1 --pr 3561` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked 30b069508f194240f90ddd05cb5cfee0613814e1 ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge 30b069508f194240f90ddd05cb5cfee0613814e1` or `Fix review: blocked 30b069508f194240f90ddd05cb5cfee0613814e1 <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: ff2b1f4c7c38a33fa032981c5120be5d`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `30b069508f194240f90ddd05cb5cfee0613814e1` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3561 30b069508f194240f90ddd05cb5cfee0613814e1") && git -C $R push -q origin $C:refs/heads/probe/rev-3561-ff2b1f4c`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked 30b069508f194240f90ddd05cb5cfee0613814e1 seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3561-ff2b1f4c`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3561
head: 30b069508f194240f90ddd05cb5cfee0613814e1
base: e23124ff6e45bac1d48b4a775dad555a37965355

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arm id=132241104633 skipped
cancel-superseded id=132241055427 queued
prelude id=132241055830 queued
refresh id=132241055815 queued

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE stale tree: e23124ff6e45bac1d48b4a775dad555a37965355 lacks origin/main 50373173d486faf394b24637c177ab38b691b394; roster read at origin/main
NOTE body item 86f47084: R11-INTAKE-R10-RESIDUE
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I dev/audit/harnesses/r10_rca_setpoint_latch.py --check <origin/main worktree>
             `dev/audit/harnesses/r10_rca_setpoint_latch.py` is in the tree at this head

FIGURES: 1 resolved, 0 not verified, 0 refused

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


## Review scope: delta (later round over the reviewed head 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1
Fix review: merge 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1

bus-nonce: e906dc502affb1232ff8d9c46f600bd8

## Summary

Round 1, handoff review of R10-HOTFIX-FLOW-SETPOINT-STUCK at the handoff tip 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1. The handoff ref still pointed there when this verdict was written (ev/HEAD.txt). The fix sends the space write where an own-write reading used to hold it. In that case the baseline it captures is the baseline row's own target, not the reading. #3404's guarantee still holds: the optimizer's own number is never captured as the person's baseline. Only the deadlocking wait is removed. The detector moves from rc 1 at main to rc 0 at the head, and every mutant of the added production lines is killed.

## Evidence

- RESULT detector at head 90eb45f69f51: rc 0, `SUMMARY ... demanded=55 states=36 failed=0 passes=10 dropped_axis=True armed_axis=True` (ev/detector_head.txt).
- RESULT detector at origin/main e23124ff6e: rc 1, `failed=4` of 36, the four `reads 25 after 10 passes, demanded 55` rows the body lists (ev/detector_main.txt). At merge base 154dbb4c61: rc 1, the same 4 (ev/detector_base.txt). Both match the body. Note: this detector is the root-cause seat's instrument, landed in this PR. It is not an audit finder's harness, because none exists for a hotfix the owner reported.
- RESULT #3404's checks at the head: the pump-duty arbiter block gives `ALL 57 FEATURES BLOCK PASSED` and the feedback seam block gives `ALL 53 FEATURES BLOCK PASSED` (ev/blocks_head.txt, run by ev/blocks.sh). The feedback block's prelude was emitted by `features_block.py --emit-prelude` (ev/fb_prelude.py). It is 4 statements and includes `off_restore as _pa_or`, not the arbiter block's first four imports the body describes. Same count, different set. The 57 and 53 figures re-derive.
- Re-pinned assertions, read in the three-dot diff: `_pa_upgraded` now pins `_pa_up_first == [25.0]`, `_pa_up_sent == 1`, and Off restores `[35.0]`. The reading is still never captured, and the null control (a person's 31 is captured and restored) is unchanged. In the Carry 8 checks, `_arm_space` now returns True and the captured baseline is 30.0, never 26.0. An arbiter that never wrote still captures 26.0. The run-end survival check now pins baseline 30.0 after each of the five ends. Each change matches the body's table, and no other #3404 check text or predicate changed.
- RESULT fail-first: the head's tests/features.py on the merge base's production code gives `4 of 57 FEATURES BLOCK FAILED`: the re-pinned `_pa_upgraded` and the three R10-HOTFIX checks (ev/failfirst_base_prod_head_tests.txt). The feedback block dies with a `TypeError` on `_arm_space`'s new `now` argument (ev/failfirst_base_fb.txt). The body's `3 of 56` was taken at the first commit's tests. I did not re-take it there. My figure at the head's tests is consistent with it plus the one check added later.
- RESULT mutation: `mutant_run.py --diff 154dbb4c61...HEAD --cmd 'bash ev/blocks.sh'` at the head ran 14 mutants (listed by `--list`). It reported no SURVIVED and no FORKCAP line and exited rc 0 (ev/mutant_run_head.txt). The driver prints nothing for a kill, and the unedited baseline passed, or it would have exited rc 3. Manual spot check: `if own:` -> `if False:` at pump_arbiter.py:1645 gives `3 of 57 FEATURES BLOCK FAILED`, rc 1 (ev/manual_mutant_1645_GUARD_OFF.txt).
- Null controls: `_pa_stuck_null` (no record, so 55 is written), `_pa_stuck_off("40")` (restores 40) and `_pa_dropped_over(55.0, 40.0)` all pass inside the 57/57 arbiter block. I did not re-run the detector's own skip control (rc 2), and neither did the body.
- Claim files and goldens: the three-dot diff touches neither claim file nor anything under tests/golden/. env_drift has no drift to compare.
- VERSION and the manifest are untouched. RELEASE_NOTES.md gains one paragraph under v7.1.12's `### #3404`, and no line starting `#` is added or removed.
- Merge: `git merge-tree --write-tree origin/main 90eb45f6` against origin/main e23124ff6e exits 0. The ledger driver printed `LEDGER-MERGE: resolved tests/closures.json` (merged as a set). No MERGE-CLAIM line appeared (ev/merge_tree.txt). Main has moved past the c67c1933be the body names, and the merge is still clean.
- CI: no pull request exists yet, so there are no check runs and no review packet to read. `merge_train.py owed-reds` prints `tests / mutation`, `tests / typing` and `validate / validate-hacs`. None has run on this head. The body answers the predicted `tests / mutation` red (6 unpinned sites for mutation-autofix). The other two cannot be judged until CI runs on the PR.
- Class: the body names one seam, an actuator-write refusal released only by a person, at `_arm_space`/`_held_back`. The detector enumerates the 36 persisted starting states (written x dropped x reading x armed). No enumeration rule beyond that is named. I read this as a one-seam class, which the detector's state space covers, not as proof of compliance elsewhere.
- Fallback domain I checked: `_space_target(inp, inp.plan, now, None)` can return None. On an indoor unit that happens with no plan step covering now, the misdeclared-indoor latch, or an entity with no state. On a flow or return unit it happens only with an entity with no state. With `baseline_c=None`, `off_restore.async_arm` falls back to the reading, which is the own write. On today's paths this is unreachable, because the indoor write target comes from the same `_space_target`: no target means no write and no arm. A flow entity with no state reads None, so `own` is False. Carried below as a latent coupling.
- Owner-requested pause check (owner 2026-11-13): the only hold-off #3404 introduced is the own-write wait, and this PR deliberately replaces it. `ECHO_GRACE_S` (both checks pass), `_pump_off` and `hold()` are untouched by the production diff.
- Forward-carry: the body's two `Carry: R11-INTAKE-R10-RESIDUE` items are text and harness residue, owned by a later intake. Neither changes how a later stage of this hotfix must work.

## Findings

- Follow-up: in `_arm_space`, an own-write reading with `_space_target(..., None)` returning None passes `baseline_c=None`, and `off_restore.async_arm` then silently captures the reading, the optimizer's own write, as the person's baseline. That is #3404's forbidden case. It is unreachable today because the write target and the baseline row share `_space_target`'s None conditions. A later change that writes a space value the baseline row cannot compute would reopen it. Carry: R11-INTAKE-R10-RESIDUE

## Friction

- In diff mode, `mutant_run.py` prints nothing for a kill, so an all-killed run's log reads `rc=0` alone. The first background run's empty log looked like a lost run until the docstring was read. Carry: dismissed: documented behaviour of the driver (its docstring says "nothing for a kill"), no defect

## Delta diff: git diff 90eb45f69f511811ddd2ed9e7c6570ab8b2abdd1 30b069508f194240f90ddd05cb5cfee0613814e1
diff --git a/custom_components/heatpump_optimizer/coordinator.py b/custom_components/heatpump_optimizer/coordinator.py
index a362be579d..d7503a17af 100644
--- a/custom_components/heatpump_optimizer/coordinator.py
+++ b/custom_components/heatpump_optimizer/coordinator.py
@@ -256,7 +256,7 @@ from .accuracy import (
 )
 from .comfort_learning import ComfortLearner, OverrideEvent
 from .defrost import DefrostDerate, DefrostWindow, in_frost_band
-from . import early_cutoff, pump_arbiter, pump_signals, supply_hold
+from . import duty_switch, early_cutoff, pump_arbiter, pump_signals, supply_hold
 from . import issues, setpoint_check
 from . import quiet_windows
 from . import price_tiles
@@ -6220,13 +6220,14 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
         share no mutable state with the event loop (#240).
         """
         ctx = getattr(self, "_ctx", self)
+        now = dt_util.now()
         tariff = self._capacity_tariff()
         threshold = self._peak_tracker.threshold_kw(tariff)
         # Post-outage recovery (#22): every neighbour restarts at once, so
         # the fresh-month "no reference yet" free pass is exactly wrong now.
         # Force the peak term active by pricing from zero when the threshold
         # would otherwise be infinite.
-        if self._outage_recovery_active(dt_util.now()) and not np.isfinite(threshold):
+        if self._outage_recovery_active(now) and not np.isfinite(threshold):
             threshold = 0.0
         config_bands: dict[str, float] = {}
         dhw_bands: dict[str, float] = {}
@@ -6241,17 +6242,16 @@ class HeatPumpOptimizerCoordinator(DataUpdateCoordinator[Payload]):
             price_risk_lambda=ctx._config.price_risk_lambda,
             baseline_load_kw=self._baseline_house_load(n_steps),
             cycling_cost=self._effective_cycling_cost(),
+            **duty_switch.planner_fields(self),
             # The optimizer prices surplus consumption at this; an
             # entity-supplied compensation can change between runs.
             pv_export_price=self._pv_export_price(),
             comfort_weight=self._comfort_weight(),
             holiday_dates=away_mode.holiday_dates(
-                self.hass, ctx._config.holiday_calendar_entity,
-                dt_util.now(),
+                self.hass, ctx._config.holiday_calendar_entity, now,
             ),
             **config_bands,
         )
-        now = dt_util.now()
         params = replace(
             copy.deepcopy(ctx._thermal_params),
             **dhw_bands,
diff --git a/custom_components/heatpump_optimizer/dhw_planner.py b/custom_components/heatpump_optimizer/dhw_planner.py
index 03b5171370..fc4b26a157 100644
--- a/custom_components/heatpump_optimizer/dhw_planner.py
+++ b/custom_components/heatpump_optimizer/dhw_planner.py
@@ -137,6 +137,18 @@ def _forced_off_with(
     return forced_off | mask
 
 
+def _with_placement_ban(
+    forced_off: np.ndarray | None, ban: np.ndarray | None, n_steps: int
+) -> np.ndarray | None:
+    """``forced_off`` with a caller's placement ban OR'd in; unchanged with none.
+
+    The optimizer's duty-switch candidate enters here and nowhere else: unlike
+    ``off_steps`` a ban moves no disinfection step, and a manual force-on pin
+    inside it still wins, because the pins are overlaid after the placement.
+    """
+    return forced_off if ban is None else _forced_off_with(forced_off, ban, n_steps)
+
+
 def _legionella_off_mask(off_steps: Any, n_steps: int) -> np.ndarray | None:
     """The Off window as a horizon mask, or None when there is no window."""
     if off_steps is None:
@@ -959,6 +971,7 @@ class DhwPlanner:
         off_steps: np.ndarray | None = None,
         wood_temps: np.ndarray | None = None,
         tank_exo_kw: np.ndarray | None = None,
+        placement_ban: np.ndarray | None = None,
     ) -> tuple[DhwPlan, np.ndarray]:
         """Build the DHW availability requirements and a cheapest-first plan.
 
@@ -1087,6 +1100,7 @@ class DhwPlanner:
             # remain. Not a pin: the window is a scheduled decision, so the
             # pin-safety release loop in ``optimize`` never frees these.
             forced_off = _forced_off_with(forced_off, off_steps, n_steps)
+        forced_off = _with_placement_ban(forced_off, placement_ban, n_steps)
 
         # Pre-heating is allowed anywhere in the horizon: the planners price the
         # standby losses of storing heat, so an early cheap hour wins only when
diff --git a/custom_components/heatpump_optimizer/duty_legs.py b/custom_components/heatpump_optimizer/duty_legs.py
new file mode 100644
index 0000000000..ecb3c6b38f
--- /dev/null
+++ b/custom_components/heatpump_optimizer/duty_legs.py
@@ -0,0 +1,236 @@
+"""The legs a plan step is served in, the switches between them, and what a stop costs.
+
+One concern with one owner, on ``plan_step.py``'s own argument: the pump
+arbiter serves a planned both step as a hot-water leg and a heating leg, and
+the optimizer prices the switches that serving makes, so two modules need one
+rule and neither may import the other. A leaf: numpy, the plan's running rule
+and the step width, nothing of Home Assistant.
+
+A switch between duties at constant draw is invisible to the cycling term,
+which prices the swing of the combined draw. On an install whose compressor
+stops at such a switch (pull request 3420, Bankaifan: hot water to heating,
+three times out of three) the stop turns the swing ``|a - b|`` into ``a + b``.
+The difference, ``2 * min(a, b)``, is ``min(a, b) / p_max`` cycles in the
+cycling term's own unit, and that is the weight a switch carries here, taken
+with the learned probability that the direction stops the compressor.
+
+A pair of per-direction values is always ``(hot water to heating, heating to
+hot water)``.
+"""
+from __future__ import annotations
+
+import math
+from typing import Any
+
+import numpy as np
+
+from .batchmath import row_sums
+from .plan_step import PLAN_STEP_MINUTES
+from .thermal_model import MIN_RUNNING_DRAW_KW
+
+#: The shortest single-duty share of a both step; a shorter share goes to
+#: the other duty for the whole step (valve travel and compressor cycling).
+SPLIT_MIN_MINUTES = 5.0
+
+#: Leg codes of :func:`leg_ends`.
+IDLE, SPACE, DHW = 0, 1, 2
+
+
+def both_step_legs(
+    space_kw: float, dhw_kw: float, step_minutes: float = PLAN_STEP_MINUTES
+) -> tuple[tuple[str, float], ...]:
+    """The legs of a step both circuits run in, in order, each with its minutes.
+
+    Hot water's share is the step's hot-water power over its total (tvofi,
+    2026-09-27); a share under :data:`SPLIT_MIN_MINUTES` on either side
+    collapses the step onto the other duty. Hot water goes first.
+    """
+    dhw_min = step_minutes * dhw_kw / (space_kw + dhw_kw)
+    if dhw_min < SPLIT_MIN_MINUTES:
+        return (("space", step_minutes),)
+    if step_minutes - dhw_min < SPLIT_MIN_MINUTES:
+        return (("dhw", step_minutes),)
+    return (("dhw", dhw_min), ("space", step_minutes - dhw_min))
+
+
+def _runs(kw: np.ndarray, floor: float | None) -> np.ndarray:
+    """``planned_draw_runs`` for one circuit, elementwise (pinned equal by test)."""
+    on = kw > MIN_RUNNING_DRAW_KW
+    return on if floor is None else on & ~(kw < floor)
+
+
+def leg_ends(
+    space_kw: Any,
+    dhw_kw: Any,
+    floor: float | None = None,
+    step_minutes: float = PLAN_STEP_MINUTES,
+) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
+    """Per step: the first leg, the last leg, and whether the step has two.
+
+    The arbiter's rule elementwise: ``step_duty`` reads each circuit alone
+    against the plan's ``floor``, and a both step splits by
+    :func:`both_step_legs`. ``space_kw`` may be a ``[B, n]`` batch against one
+    ``[n]`` hot-water plan.
+    """
+    space = np.asarray(space_kw, dtype=float)
+    dhw = np.asarray(dhw_kw, dtype=float)
+    s_on, d_on = _runs(space, floor), _runs(dhw, floor)
+    both = s_on & d_on
+    dhw_min = step_minutes * dhw / np.where(both, space + dhw, 1.0)
+    to_space = both & (dhw_min < SPLIT_MIN_MINUTES)
+    to_dhw = both & ~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)
+    two = both & ~to_space & ~to_dhw
+    single = np.where(
+        (s_on & ~d_on) | to_space, SPACE, np.where((d_on & ~s_on) | to_dhw, DHW, IDLE)
+    )
+    return np.where(two, DHW, single), np.where(two, SPACE, single), two
+
+
+def priced_pair(values: Any, upper: float = math.inf) -> tuple[float, float]:
+    """A per-direction pair as two floats in ``[0, upper]``, else zero."""
+    try:
+        pair = [float(v) for v in values]
+    except (TypeError, ValueError):
+        return 0.0, 0.0
+    if len(pair) != 2:
+        return 0.0, 0.0
+    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)
+    return a, b
+
+
+#: A boundary pairs each step but the last with the step after it; the legs
+#: that meet there and the levels they run at are read through the same pair.
+_BEFORE, _AFTER = np.s_[:, :-1], np.s_[:, 1:]
+
+
+def switch_weights_batch(
+    space_matrix: np.ndarray,
+    dhw_kw: np.ndarray,
+    stop_probability: tuple[float, float],
+    p_max: float,
+    floor: float | None = None,
+) -> np.ndarray:
+    """Expected compressor stops at duty switches, in cycles, per row of plans.
+
+    Every pair of consecutive legs of different duty with no idle step
+    between weighs ``p * level / p_max``: inside a two-leg step both legs run
+    at the step's combined level; across a boundary the stop adds the smaller
+    of the two levels. ``row_sums`` reduces each row on its own, so a row is
+    :func:`switch_weight` of that plan bit for bit.
+    """
+    space = np.asarray(space_matrix, dtype=float)
+    p_ds, p_sd = stop_probability
+    if p_max <= 0:
+        return np.zeros(space.shape[0])
+    first, last, two = leg_ends(space, dhw_kw, floor)
+    level = space + np.asarray(dhw_kw, dtype=float)
+    before, after = last[_BEFORE], first[_AFTER]
+    stops = np.where(
+        (before == DHW) & (after == SPACE),
+        p_ds,
+        np.where((before == SPACE) & (after == DHW), p_sd, 0.0),
+    )
+    across = stops * np.minimum(level[_BEFORE], level[_AFTER])
+    inside = np.where(two, p_ds * level, 0.0)
+    return row_sums(np.concatenate([inside, across], axis=1)) / p_max
+
+
+def switch_weight(
+    space_kw: np.ndarray,
+    dhw_kw: np.ndarray,
+    stop_probability: tuple[float, float],
+    p_max: float,
+    floor: float | None = None,
+) -> float:
+    """The one-row case of :func:`switch_weights_batch`."""
+    return float(switch_weights_batch(
+        np.asarray(space_kw, dtype=float)[None, :], dhw_kw, stop_probability, p_max, floor
+    )[0])
+
+
+def lost_share(
+    stop_probability: tuple[float, float],
+    off_seconds: tuple[float, float],
+    step_minutes: float = PLAN_STEP_MINUTES,
+) -> float:
+    """The share of one step a hot-water to heating stop keeps the compressor off.
+
+    Only that direction carries lost time: its stop shortens the heating leg
+    that follows, and no install has measured an off time the other way.
+    """
+    return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))
+
+
+def availability(
+    space_start_kw: np.ndarray,
+    dhw_kw: np.ndarray,
+    lost: float,
+    floor: float | None = None,
+) -> np.ndarray | None:
+    """Per step, the share of it the compressor can run after a priced stop.
+
+    One step is charged per hot-water block end: the step holding the heating
+    leg that follows the hot-water leg in ``space_start_kw``, the profile the
+    solve starts from, because which step that is is the solve's own variable.
+    ``None`` when nothing is charged, so the caller makes today's calls on
+    today's arrays instead of multiplying by ones.
+    """
+    if not lost > 0:
+        return None
+    first, last, two = leg_ends(space_start_kw, dhw_kw, floor)
+    charged = two.copy()
+    charged[1:] |= (last[:-1] == DHW) & (first[1:] == SPACE)
+    if not charged.any():
+        return None
+    return np.where(charged, 1.0 - lost, 1.0)
+
+
+def space_headroom(
+    p_max: float, dhw_kw: np.ndarray, avail: np.ndarray | None, floor: float | None
+) -> np.ndarray:
+    """The space draw a hot-water plan leaves, less a stop's lost running time.
+
+    On a duty-cycle install (no ``floor``) a schedule value is a step average
+    and the stop is part of the off time, so the bound carries it. On a
+    clamped install a value is the level the compressor runs at and the bound
+    is today's; :func:`delivered_space` carries the lost time there.
+    """
+    if avail is None or floor is not None:
+        return np.maximum(0.0, p_max - dhw_kw)
+    charged: np.ndarray = np.maximum(0.0, avail * p_max - dhw_kw)
+    return charged
+
+
+def delivered_space(
+    space_kw: np.ndarray, dhw_kw: np.ndarray, avail: np.ndarray, floor: float | None
+) -> np.ndarray:
+    """The step average the house receives from a shipped space level.
+
+    On a clamped install the compressor is off for ``1 - avail`` of a step it
+    runs at level ``space + dhw``, and hot water keeps the level its planner
+    booked. On a duty-cycle install the shipped draw is already the average.
+    """
+    if floor is None:
+        return space_kw
+    delivered: np.ndarray = np.maximum(0.0, space_kw - (1.0 - avail) * (space_kw + dhw_kw))
+    return delivered
+
+
+def switch_ban(
+    space_kw: np.ndarray, stop_probability: tuple[float, float], floor: float | None
+) -> np.ndarray:
+    """The steps hot water may not be placed on to avoid a priced switch.
+
+    For hot water to heating: where heating runs in that step or the next, so
+    a block can only end into a planned stop or into more hot water. For
+    heating to hot water it mirrors onto the previous step.
+    """
+    on = _runs(np.asarray(space_kw, dtype=float), floor)
+    ban = np.zeros(on.shape, dtype=bool)
+    if stop_probability[0] > 0:
+        ban |= on
+        ban[:-1] |= on[1:]
+    if stop_probability[1] > 0:
+        ban |= on
+        ban[1:] |= on[:-1]
+    return ban
diff --git a/custom_components/heatpump_optimizer/duty_switch.py b/custom_components/heatpump_optimizer/duty_switch.py
index 802bfc8624..2beb1c35b7 100644
--- a/custom_components/heatpump_optimizer/duty_switch.py
+++ b/custom_components/heatpump_optimizer/duty_switch.py
@@ -4,9 +4,10 @@ Design: ``docs/design/2026-11-10-duty-switch-restart-learning/design.md``,
 part A. On some pumps a mode write from hot water to heating while the
 compressor runs stops it: the controller judges the heating request on a
 return the hot-water leg has just heated. Whether it does, and for how long
-the pump then stays off, is learned per install and per direction. **Nothing
-reads the estimate to change a plan or a write**; it is recorded, persisted
-and published on the compressor-starts sensor.
+the pump then stays off, is learned per install and per direction. It is
+recorded, persisted and published on the compressor-starts sensor, and a
+latched direction is read by the planner (:func:`planner_fields`), which
+prices the switch through ``duty_legs``. No write reads it.
 
 **Observe** (:class:`DutySwitchLearner`, no Home Assistant object). An
 episode opens at a landed mode write between the two single duties while the
@@ -33,6 +34,9 @@ weigh under five, and a sixth latches), spanning :data:`SPAN_DAYS_ON` days with
 the evidence that still weighs: under :data:`SPAN_FLOOR_N` the days are
 forgotten with it. Every threshold
 here is a named constant from one day on one install, not a measurement.
+``n`` is held at :data:`N_CAP` by scaling both counts alike at a booking, so
+evidence from before a firmware change is outvoted in a bounded number of
+episodes and an install that stops switching unlatches in a bounded time.
 """
 from __future__ import annotations
 
@@ -69,6 +73,11 @@ HEATED_MARGIN_K = 2.0
 SOURCE_LEG_MIN_S = 60.0
 HALF_LIFE_DAYS = 14.0
 N_ON, N_OFF = 5.0, 2.5
+#: The most decayed episodes a direction holds, twice the on-threshold. With
+#: every later episode kept, ``p`` falls from 1 by 10/11 per booking and is
+#: under :data:`P_OFF` at the thirteenth; with none, ``n`` is under
+#: :data:`N_OFF` just past two half-lives.
+N_CAP = 2.0 * N_ON
 P_ON, P_OFF = 0.5, 0.3
 SPAN_DAYS_ON = 2
 #: Decayed episodes under which a direction's days span nothing any more: one
@@ -213,6 +222,9 @@ class Direction:
                 self.censored += 1
             else:
                 self.off_s = [*self.off_s, off_s][-OFF_SAMPLES_MAX:]
+        if self.n > N_CAP:
+            scale = N_CAP / self.n
+            self.k, self.kept_w = self.k * scale, self.kept_w * scale
         self._latch()
 
     def stored_row(self) -> dict[str, Any]:
@@ -373,6 +385,14 @@ class DutySwitchLearner:
             out.update({f"duty_switch_{name}_{key}": value for key, value in row.items() if value is not None})
         return out
 
+    def planner_pairs(self) -> tuple[tuple[float, float], tuple[float, float]]:
+        """Per direction, in :data:`DIRECTIONS`' order: the stop probability
+        and the median off seconds the planner prices a switch by. Zeros
+        unless the direction's latch is on, and no off time while every
+        stop's was censored."""
+        read = [d if d.usable else Direction() for d in map(self.directions.__getitem__, DIRECTIONS)]
+        return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)
+
     def stored_record(self) -> dict[str, Any]:
         return {"directions": {name: d.stored_row() for name, d in self.directions.items()}}
 
@@ -503,3 +523,10 @@ def starts_attributes(coord: Any) -> dict[str, float]:
     """The compressor-starts sensor's duty-switch attributes; a pump never arbitrated reads empty."""
     rec = _RECORDS.get(coord)
     return (rec.learner if rec is not None else DutySwitchLearner()).published(dt_util.now())
+
+
+def planner_fields(coord: Any) -> dict[str, tuple[float, float]]:
+    """The ``OptimizationConfig`` fields a solve prices a duty switch by; a pump never arbitrated reads zeros."""
+    rec = _RECORDS.get(coord)
+    stops, off_s = (rec.learner if rec is not None else DutySwitchLearner()).planner_pairs()
+    return {"duty_switch_stop_probability": stops, "duty_switch_off_seconds": off_s}
diff --git a/custom_components/heatpump_optimizer/optimizer.py b/custom_components/heatpump_optimizer/optimizer.py
index 45f71299ac..a7bb65b82e 100644
--- a/custom_components/heatpump_optimizer/optimizer.py
+++ b/custom_components/heatpump_optimizer/optimizer.py
@@ -111,6 +111,7 @@ from .thermal_model import (
     project_space_against,
     valve_charge_demand,
     valve_hold_temperature,
+    valve_top_draw,
     weather_or_calm,
     power_for_heat_per_cop_kw,
     added_power_for_heat_per_cop_kw,
@@ -128,6 +129,7 @@ from .tariff import (
     window_factors,
 )
 from .dhw_schedule import format_resolved_day_spec
+from . import duty_legs
 
 _LOGGER = logging.getLogger(__name__)
 
@@ -192,6 +194,215 @@ def _scores_rounded(opt: HeatPumpOptimizer) -> bool:
     return opt.config.clamp_planned_levels and not opt._levels_relaxed
 
 
+def _priced_stops(opt: HeatPumpOptimizer) -> tuple[float, float] | None:
+    """The learned stop probability per switch direction, ``None`` when no direction stops.
+
+    The lost running time is charged on this alone; the price is this times
+    ``cycling_cost``, so an install that prices no cycle prices no switch.
+    """
+    stops = duty_legs.priced_pair(opt.config.duty_switch_stop_probability, 1.0)
+    return stops if max(stops) > 0 else None
+
+
+def _stop_availability(
+    opt: HeatPumpOptimizer, start: np.ndarray, dhw_plan: np.ndarray, p_max: float
+) -> np.ndarray | None:
+    """The running share a priced stop leaves each step of the profile a solve starts from.
+
+    Read on the levels that profile ships, so the charged step holds a
+    heating leg the arbiter serves. ``None`` unless a stop with a measured off
+    time is priced: the caller then makes today's calls.
+    """
+    stops = _priced_stops(opt)
+    if stops is None:
+        return None
+    lost = duty_legs.lost_share(
+        stops, duty_legs.priced_pair(opt.config.duty_switch_off_seconds)
+    )
+    space, tank = _realize_joint(
+        opt.config.clamp_planned_levels,
+        np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),
+        dhw_plan, opt.model.params.min_electrical_power, p_max,
+    )
+    return duty_legs.availability(space, tank, lost, _duty_floor(opt))
+
+
+def _with_stop_availability(
+    opt: HeatPumpOptimizer,
+    start: np.ndarray,
+    dhw_plan: np.ndarray,
+    p_max: float,
+    objective: Callable[..., float],
+    objective_batch: Callable[..., np.ndarray],
+) -> tuple[np.ndarray, Callable[..., float], Callable[..., np.ndarray]]:
+    """What a priced stop changes about one space solve: its bound and its objectives.
+
+    The heat pump serves one circuit at a time, so a DHW block eats into the
+    capacity available for space heating during that step, and a stop after
+    it into the step that follows. The availability vector is constant for
+    the solve and is kept on the optimizer beside the requirement, so the
+    plan that is adopted publishes with the vector it was scored with. With
+    none, the bound is ``p_max - dhw`` and the objectives the ones handed in.
+    """
+    avail = opt._space_avail = _stop_availability(opt, start, dhw_plan, p_max)
+    headroom = duty_legs.space_headroom(p_max, dhw_plan, avail, _duty_floor(opt))
+    if avail is None:
+        return headroom, objective, objective_batch
+    return headroom, partial(objective, avail=avail), partial(objective_batch, avail=avail)
+
+
+def _shipped_and_received(
+    opt: HeatPumpOptimizer,
+    space: np.ndarray,
+    dhw: np.ndarray | None,
+    avail: np.ndarray | None,
+) -> tuple[np.ndarray, np.ndarray | None, np.ndarray]:
+    """The level each circuit ships at, and the space draw the house receives.
+
+    The two differ only where a priced stop keeps the compressor off for part
+    of a step (``duty_legs.delivered_space``); with no availability vector the
+    received draw is the shipped array itself, the same object. A relaxed
+    start of a clamped install gets the clamped reading on its unrounded
+    level: the stop is the install's, whatever the rounding.
+    """
+    space, dhw = _realize_draw(
+        _scores_rounded(opt), space, dhw,
+        opt.model.params.min_electrical_power, opt.model.params.max_electrical_power,
+    )
+    if avail is None or dhw is None:
+        return space, dhw, space
+    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))
+
+
+def _switch_cost_fn(
+    opt: HeatPumpOptimizer,
+) -> Callable[[np.ndarray, np.ndarray | None], Any]:
+    """The duty-switch term of shipped plans, beside the cycling term.
+
+    One entry per row of a ``[B, n]`` batch, a float for one plan: the
+    one-row case of the same reduction, so the two agree bit for bit.
+    ``None`` when no direction is priced or there is no hot-water plan, and
+    :func:`_with_switch_cost` then adds no operand at all.
+    """
+    stops, floor = _priced_stops(opt), _duty_floor(opt)
+    p_max, cost = opt.model.params.max_electrical_power, opt.config.cycling_cost
+
+    def switch_cost(space: np.ndarray, dhw: np.ndarray | None) -> Any:
+        if stops is None or dhw is None or not cost > 0:
+            return None
+        term = cost * duty_legs.switch_weights_batch(
+            np.atleast_2d(space), dhw, stops, p_max, floor)
+        return term if np.ndim(space) == 2 else float(term[0])
+
+    return switch_cost
+
+
+def _with_switch_cost(level_cost: Any, switch_cost: Any) -> Any:
+    """The cycling and capacity terms plus the duty-switch term, when there is one."""
+    return level_cost if switch_cost is None else level_cost + switch_cost
+
+
+def _dhw_build(
+    planner: DhwPlanner, h: _Horizon, p_max: float, **extra: Any
+) -> tuple[Any, np.ndarray]:
+    """One hot-water build, with what every pass of a solve hands the planner.
+
+    The block honours an external ceiling through one scalar, the horizon's
+    minimum -- the same conservative, never-over-the-line approximation the
+    fuse guard's cap already makes. A quiet silent window's cap therefore
+    bounds every block the same way (#1910); its OFF steps are per-step,
+    through the forced-off door where the energy is re-bought elsewhere. The
+    mode's block rides every build (#1747): a replan without it plans hot
+    water the mode cannot make, and masks the breach.
+    """
+    return planner._build_dhw_requirements(
+        h,
+        p_max=p_max,
+        p_run_cap=(
+            float(np.min(h.power_caps_extra))
+            if h.power_caps_extra is not None
+            else None
+        ),
+        blocked=h.dhw_blocked,
+        off_steps=h.off_steps,
+        **extra,
+    )
+
+
+def _avoid_priced_switches(
+    opt: HeatPumpOptimizer,
+    h: _Horizon,
+    planner: DhwPlanner,
+    solve_space: Callable[..., Any],
+    objective: Callable[..., float],
+    p_max: float,
+    incumbent: tuple[np.ndarray, np.ndarray, str],
+) -> tuple[np.ndarray, np.ndarray, str]:
+    """Try one hot-water plan placed where no priced switch follows it.
+
+    Where the block sits is combinatorial, so it is taken by candidate and
+    score, as ``_co_optimize`` takes its own: hot water is banned from the
+    steps whose heating would make the switch, and the plan is adopted only
+    if it scores lower on the same objective, keeps off every banned step a
+    manual pin does not force on, and holds its own requirement wherever the
+    incumbent holds its. A refused candidate leaves the incumbent's
+    requirement and availability in place. Not on a combi store, whose
+    hot-water plan is a feasibility repair and never a scored candidate.
+    """
+    space, dhw, _ = incumbent
+    stops = _priced_stops(opt)
+    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:
+        return incumbent
+    floor = _duty_floor(opt)
+    shipped, tank = _realize_joint(
+        opt.config.clamp_planned_levels, space, dhw,
+        opt.model.params.min_electrical_power, p_max,
+    )
+    kept_avail, kept_requirement = opt._space_avail, opt._dhw_requirement
+    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:
+        return incumbent
+    try:
+        ban = duty_legs.switch_ban(shipped, stops, floor)
+        plan, requirement = _dhw_build(
+            planner, h, p_max,
+            wood_temps=planner._dhw_coil_wood_forecast(h), placement_ban=ban,
+        )
+        forced_on = (
+            np.zeros(ban.shape, dtype=bool) if h.dhw_pins is None
+            else np.nan_to_num(_padded(h.dhw_pins, ban.size)) >= 0.5
+        )
+
+        def first_short(
+            schedule: np.ndarray, floor_temps: np.ndarray, excused: set[int]
+        ) -> tuple[Any, int | None]:
+            """The planner's own tank walk and shortfall rule, past ``excused`` steps."""
+            temps, _, step = planner._dhw_shortfall(
+                temps_of.get(id(schedule)), schedule, h.initial_state.dhw_temperature,
+                h.outdoor_temps, plan.draw_rates, h.dt, h.humidity, floor_temps, excused,
+            )
+            temps_of[id(schedule)] = temps
+            return temps, step
+
+        # The steps the incumbent is itself short on excuse the candidate there.
+        temps_of: dict[int, Any] = {}
+        unheld: set[int] = set()
+        while (step := first_short(dhw, kept_requirement, unheld)[1]) is not None:
+            unheld.add(step)
+        if (
+            not np.any(plan.schedule[ban & ~forced_on] > 0)
+            and first_short(plan.schedule, requirement, unheld)[1] is None
+        ):
+            base = float(objective(space, dhw, None, kept_avail))
+            candidate_space, candidate_status, score = solve_space(plan.schedule, space)
+            if score < base - 1e-9:
+                opt._dhw_requirement = requirement
+                return candidate_space, plan.schedule, candidate_status
+    except Exception as err:  # noqa: BLE001 - a candidate is optional: the incumbent stands
+        _LOGGER.debug("Duty-switch candidate pass skipped: %s", err)
+    opt._space_avail = kept_avail
+    return incumbent
+
+
 def _relaxed_starts(
     opt: HeatPumpOptimizer,
     objective: Callable[..., float],
@@ -579,46 +790,77 @@ def _wood_covered_share(model: ThermalModel, state: ThermalState, reference_kwh:
     return min(1.0, usable_kwh_th / p.cop_nominal_floored / reference_kwh)
 
 
+def _held_zones(
+    model: ThermalModel, state: ThermalState, weather0: tuple[float, float, float, float],
+    temp: float,
+) -> ThermalState:
+    """``state`` with the zones at ``temp`` and the slab at the temperature that
+    delivers the floor's steady demand there -- the cascade's own slab target
+    with no pull-back."""
+    q_floor = _floor_demand_at_target(model, temp, *weather0)
+    return replace(
+        state,
+        room_temperature=temp,
+        upper_floor_temperature=temp,
+        lower_floor_temperature=temp,
+        slab_temperature=temp + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,
+    )
+
+
+#: Bisection steps for the held zone temperature: 2**-40 of the
+#: outdoor-to-target span, far below any sensor's resolution.
+_HELD_BISECTIONS = 40
+
+
 def _thermostat_held_state(
     model: ThermalModel, state: ThermalState, weather: WeatherSeries, target: float
 ) -> ThermalState:
     """``state`` as a thermostat holding ``target`` all along would have it (#2255).
 
-    The zones at ``target`` and the slab at the temperature that delivers the
-    step's demand -- the cascade's own slab target with no pull-back -- so the
-    first step draws the steady holding power. Behind a valve its tank sits at
-    the temperature that delivers the need, whatever the plan left in the
-    measured one. Every other field stays as measured.
+    The zones at ``target`` (``_held_zones``), so the first step draws the
+    steady holding power. Behind a valve its tank sits at the temperature
+    that delivers the need, whatever the plan left in the measured one.
+    Where the reference cannot deliver that steady heat at ``target`` --
+    either bound its own step clips at (``_held_unreachable``) -- a
+    thermostat running all along has sagged to where it can: the zones sit
+    at the highest temperature the step can hold, an equilibrium, so the
+    booked steps draw no stored heat (R10-SAV-VALUATION-RESIDUE).
+    Every other field stays as measured.
     """
     if not len(weather.outdoor_temps):
         return state
     assert weather.wind_speeds is not None and weather.precipitation is not None
     assert weather.solar_radiation is not None
-    q_floor = _floor_demand_at_target(
-        model, target, float(weather.outdoor_temps[0]), float(weather.wind_speeds[0]),
-        float(weather.precipitation[0]), float(weather.solar_radiation[0]),
-    )
-    held = replace(
-        state,
-        room_temperature=target,
-        upper_floor_temperature=target,
-        lower_floor_temperature=target,
-        slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,
-    )
+    outdoor, wind = float(weather.outdoor_temps[0]), float(weather.wind_speeds[0])
+    rain, solar = float(weather.precipitation[0]), float(weather.solar_radiation[0])
+    weather0 = (outdoor, wind, rain, solar)
+    humidity = None if weather.humidity is None else float(weather.humidity[0])
     p = model.params
-    if not mixing_valve.is_throttling(p.mixing_valve_mode):
-        return held
-    wind, rain = float(weather.wind_speeds[0]), float(weather.precipitation[0])
-    outdoor = float(weather.outdoor_temps[0])
+    valved = mixing_valve.is_throttling(p.mixing_valve_mode)
     zoned = _thermostat_demand_two_zone if p.two_zone_enabled else _thermostat_demand_single
-    need = zoned(
-        model, held, target, outdoor, wind, rain, float(weather.solar_radiation[0]),
-        0.25, p.slab_heat_transfer_floored,
-    )
-    held.buffer_tank_temperature = (
-        valve_hold_temperature(model, held, need, outdoor, wind, rain)
-        if need > 0.0 else held.buffer_tank_temperature
-    )
+
+    def need(h: ThermalState) -> float:
+        # Zones level at their own temperature: no pull-back, the steady need.
+        return zoned(model, h, h.room_temperature, *weather0, 0.25, p.slab_heat_transfer_floored)
+
+    def held_at(temp: float) -> ThermalState:
+        h = _held_zones(model, state, weather0, temp)
+        if valved and (h_need := need(h)) > 0.0:
+            h.buffer_tank_temperature = valve_hold_temperature(
+                model, h, h_need, outdoor, wind, rain)
+        return h
+
+    def unreachable(h: ThermalState) -> bool:
+        return _held_unreachable(model, h, need(h), weather0, humidity)
+
+    held = held_at(target)
+    if unreachable(held):
+        # Unreachable needs heat, so the outdoor is below the target: the span is ordered.
+        lo, hi = min(outdoor, target), target
+        for _ in range(_HELD_BISECTIONS):
+            mid = 0.5 * (lo + hi)
+            lo, hi = (lo, mid) if unreachable(held_at(mid)) else (mid, hi)
+        held = held_at(lo)
     if p.two_tank_modelled:
         # The reference has no wood: below every zone the valve takes nothing
         # from this side (``wood_share`` 0), so the step is the plain valve's.
@@ -626,6 +868,33 @@ def _thermostat_held_state(
     return held
 
 
+def _held_unreachable(
+    model: ThermalModel, held: ThermalState, need_kw: float,
+    weather0: tuple[float, float, float, float], humidity: float | None,
+) -> bool:
+    """Whether the reference's own step cannot deliver ``need_kw``, the held
+    zones' steady emitter need, from ``held``: every bound on the heat it
+    delivers (R10-SAV-VALUATION-RESIDUE).
+
+    Behind a valve, the curve's top draw (``valve_top_draw``): a hotter tank
+    reaches no emitter. On every install, the pump: the steady heat the
+    step makes (``_thermostat_demand``, the tank's standing loss on top)
+    needs a draw past ``max_electrical_power`` at the step's own COP
+    (``_reference_cop``, defrost and part-load included), where the step
+    clips. Nothing else bounds it: the wood side is off in the reference and
+    ``buffer_max_temp`` caps the curve's top.
+    """
+    p = model.params
+    outdoor, wind, rain, solar = weather0
+    if mixing_valve.is_throttling(p.mixing_valve_mode) and need_kw > valve_top_draw(
+            model, held, outdoor, wind, rain):
+        return True
+    made = _thermostat_demand(
+        model, held, held.room_temperature, *weather0, 0.25, p.slab_heat_transfer_floored)
+    cop = _reference_cop(model, held, outdoor, humidity)
+    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)
+
+
 def _thermostat_demand_single(
     model: ThermalModel,
     state: ThermalState,
@@ -1457,11 +1726,8 @@ def _combi_flux_exchange(
             weather=_with_buffer_exo(weather, dhw_exo), dt_hours=h.dt,
             valve_targets=h.valve_targets, start_hour=float(h.step_hours[0]))[4]
         space_net = combi_space_net_kw(store, buffer_temps, dhw_exo, h.dt)
-        plan, opt._dhw_requirement = planner._build_dhw_requirements(
-            h, p_max=p_max, space_demand=space_power,
-            p_run_cap=None if h.power_caps_extra is None else float(np.min(h.power_caps_extra)),
-            blocked=h.dhw_blocked, off_steps=h.off_steps, tank_exo_kw=space_net,
-        )
+        plan, opt._dhw_requirement = _dhw_build(
+            planner, h, p_max, space_demand=space_power, tank_exo_kw=space_net)
         if np.allclose(plan.schedule, dhw_power, atol=1e-4):
             break
         dhw_power = plan.schedule
@@ -2142,6 +2408,12 @@ class OptimizationConfig:
     #: had silently drifted apart once before, which meant the tests were
     #: measuring a slightly different optimizer from the integration.
     cycling_cost: float = DEFAULT_CYCLING_COST
+    #: Per direction (hot water to heating, heating to hot water): the learned
+    #: probability that a duty switch stops the compressor, and the seconds it
+    #: then stays off. Zeros price nothing and leave every plan as it was;
+    #: ``duty_legs`` owns what they mean.
+    duty_switch_stop_probability: tuple[float, float] = (0.0, 0.0)
+    duty_switch_off_seconds: tuple[float, float] = (0.0, 0.0)
 
     # --- Capacity tariff (item 8) --------------------------------------
     #: Currency per kW of new monthly peak, already divided by the number of
@@ -2753,6 +3025,9 @@ class HeatPumpOptimizer:
         # loop: the tank temperature the plan must keep the DHW trajectory
         # above. Assigned at each build, so the last build of a solve wins.
         self._dhw_requirement: np.ndarray | None = None
+        #: The ``duty_legs.availability`` vector the last space solve scored
+        #: with, riding beside its plan; ``None`` when no stop is charged.
+        self._space_avail: np.ndarray | None = None
         #: The solve's starting buffer temperature; floors the settlement
         #: value cap so pre-stored heat cannot be drained for free.
         self._initial_buffer_temp: float | None = None
@@ -2907,9 +3182,8 @@ class HeatPumpOptimizer:
         traj: dict[str, np.ndarray],
         grid_power: np.ndarray,
         *,
+        level_cost: np.ndarray,
         energy_cost_of: Callable[[np.ndarray], Any],
-        cycling_batch: Callable[[np.ndarray], np.ndarray],
-        capacity_batch: Callable[[np.ndarray], np.ndarray],
         terminal_cost_batch: Callable[[dict[str, np.ndarray]], np.ndarray],
         comfort_targets: np.ndarray,
         temp_min_bounds: np.ndarray,
@@ -2930,6 +3204,8 @@ class HeatPumpOptimizer:
         path -- because the energy, cycling and capacity terms are
         properties of the combined draw, while the comfort and terminal
         terms read ``traj``, which the space schedule alone produces.
+        ``level_cost`` is what the caller priced on the shipped level, which
+        a priced stop makes differ from that draw: cycling, capacity, switches.
         """
         weight = self.config.price_weight
         penalty, comfort_cost = self._comfort_terms_batch(
@@ -2942,7 +3218,7 @@ class HeatPumpOptimizer:
             energy_cost_of(grid_power) * weight
             + penalty
             + comfort_cost
-            + (cycling_batch(grid_power) + capacity_batch(grid_power)) * weight
+            + level_cost * weight
             + terminal_cost_batch(traj)
         )
 
@@ -3345,7 +3621,8 @@ class HeatPumpOptimizer:
         it (``combi_space_net_kw``, R10-COMBI-TANK), the flux exchange.
         """
         try:
-            headroom = np.maximum(0.0, p_max - dhw_power)
+            headroom = duty_legs.space_headroom(
+                p_max, dhw_power, self._space_avail, _duty_floor(self))
             # Where space heating sits hard against the ceiling hot water left
             # it, it wanted more power than it could have; its unconstrained
             # demand there is at least the full compressor.
@@ -3364,30 +3641,22 @@ class HeatPumpOptimizer:
             if not bool(np.any(pinned)) and not coil_replan:
                 return space_power, dhw_power, status
 
-            replanned_plan, self._dhw_requirement = planner._build_dhw_requirements(
-                h,
-                p_max=p_max,
+            replanned_plan, self._dhw_requirement = _dhw_build(
+                planner, h, p_max,
                 space_demand=np.where(pinned, p_max, space_power),
-                p_run_cap=(
-                    float(np.min(h.power_caps_extra))
-                    if h.power_caps_extra is not None
-                    else None
-                ),
-                # The first build's block (#1747): a replan without it plans
-                # hot water the mode cannot make, and masks the breach.
-                blocked=h.dhw_blocked,
-                off_steps=h.off_steps,
                 wood_temps=wood_temps,
             )
             replanned = replanned_plan.schedule
             if np.allclose(replanned, dhw_power, atol=1e-4):
                 return space_power, dhw_power, status
 
+            kept_avail = self._space_avail
             candidate_space, candidate_status, score = solve_space(
                 replanned, space_power
             )
             if score < best_score - 1e-9:
                 return candidate_space, replanned, candidate_status
+            self._space_avail = kept_avail
         except Exception as err:  # pragma: no cover - defensive
             _LOGGER.debug("DHW/space co-optimization pass skipped: %s", err)
 
@@ -4367,9 +4636,9 @@ class HeatPumpOptimizer:
         objective_batch: Callable[..., np.ndarray],
     ) -> tuple[np.ndarray, str, float]:
         """Optimize space heating around a fixed DHW schedule."""
-        # The heat pump serves one circuit at a time, so a DHW block eats
-        # into the capacity available for space heating during that step.
-        headroom = np.maximum(0.0, p_max - dhw_plan)
+        guess = init_base if warm_start is None else warm_start
+        headroom, objective, objective_batch = _with_stop_availability(
+            self, guess, dhw_plan, p_max, objective, objective_batch)
         if h.power_caps is not None:
             headroom = np.minimum(headroom, h.power_caps)
         if h.power_caps_extra is not None:
@@ -4381,7 +4650,6 @@ class HeatPumpOptimizer:
                 headroom,
                 np.maximum(0.0, h.power_caps_extra - dhw_plan),
             )
-        guess = init_base if warm_start is None else warm_start
         guess = np.minimum(np.clip(guess, 0.0, p_max), headroom)
         bounds = [(0.0, float(headroom[i])) for i in range(n_steps)]
         # Manual space pins apply here just as in the DHW-free path. Forcing
@@ -4759,9 +5027,7 @@ class HeatPumpOptimizer:
         initial_state, prices, dt, comfort_targets = (
             h.initial_state, h.prices, h.dt, h.comfort_targets
         )
-        outdoor_temps, wind_speeds, precipitation, solar_radiation = (
-            h.outdoor_temps, h.wind_speeds, h.precipitation, h.solar_radiation
-        )
+        outdoor_temps = h.outdoor_temps
         weather = WeatherSeries.from_horizon(h)
         temp_min_bounds, temp_max_bounds = h.temp_min_bounds, h.temp_max_bounds
 
@@ -4777,6 +5043,7 @@ class HeatPumpOptimizer:
             self._grid_terms(h.n_steps, dt, h.start_time)
         )
         energy_cost_of = self._energy_cost_fn(prices, dt)
+        switch_cost = _switch_cost_fn(self)
 
         def _space_traj(power_schedule: np.ndarray, buffer_exo_kw: Any = None) -> Any:
             return self.model.simulate_trajectory(
@@ -4792,14 +5059,13 @@ class HeatPumpOptimizer:
             space_power: np.ndarray,
             dhw_plan_power: np.ndarray | None = None,
             buffer_exo_kw: np.ndarray | None = None,
+            avail: np.ndarray | None = None,
         ) -> float:
             """Compute the total cost with predictive weather anticipation."""
-            space_power, dhw_plan_power = _realize_draw(
-                _scores_rounded(self), space_power, dhw_plan_power,
-                self.model.params.min_electrical_power, self.model.params.max_electrical_power,
-            )
+            space_power, dhw_plan_power, heat_power = _shipped_and_received(
+                self, space_power, dhw_plan_power, avail)
             room_temps, slab_temps, upper_temps, lower_temps, buffer_temps, _, _ = (
-                _space_traj(space_power, buffer_exo_kw)
+                _space_traj(heat_power, buffer_exo_kw)
             )
 
             # The compressor is one machine: the grid sees the *combined*
@@ -4813,8 +5079,9 @@ class HeatPumpOptimizer:
 
             # Electricity cost, piecewise in PV surplus. ``float()`` is
             # identity on the 1-D branch's return and states it.
+            drawn = combined if heat_power is space_power else heat_power + dhw_plan_power
             energy_cost = (
-                float(energy_cost_of(combined)) * self.config.price_weight
+                float(energy_cost_of(drawn)) * self.config.price_weight
             )
 
             penalty, comfort_cost = self._comfort_terms(
@@ -4831,7 +5098,9 @@ class HeatPumpOptimizer:
                 # Currency terms scale with price_weight as the energy cost
                 # does, or a non-default weight silently re-prices starts and
                 # peaks relative to the electricity they trade against.
-                + (cycling(combined) + capacity(combined))
+                + float(_with_switch_cost(
+                    cycling(combined) + capacity(combined),
+                    switch_cost(space_power, dhw_plan_power)))
                 * self.config.price_weight
                 + terminal_cost(
                     room_temps,
@@ -4846,6 +5115,7 @@ class HeatPumpOptimizer:
             space_matrix: np.ndarray,
             dhw_plan_power: np.ndarray | None = None,
             buffer_exo_kw: np.ndarray | None = None,
+            avail: np.ndarray | None = None,
         ) -> np.ndarray:
             """The same objective, for B schedules at once (issue #97).
 
@@ -4857,13 +5127,11 @@ class HeatPumpOptimizer:
             asserted by test, because a divergence here would move plans
             silently.
             """
-            space_matrix, dhw_plan_power = _realize_draw(
-                _scores_rounded(self), space_matrix, dhw_plan_power,
-                self.model.params.min_electrical_power, self.model.params.max_electrical_power,
-            )
+            space_matrix, dhw_plan_power, heat_matrix = _shipped_and_received(
+                self, space_matrix, dhw_plan_power, avail)
             traj = self.model.simulate_trajectory_batch(
                 initial_state=initial_state,
-                power_matrix=space_matrix,
+                power_matrix=heat_matrix,
                 weather=_with_buffer_exo(weather, buffer_exo_kw),
                 dt_hours=dt,
                 valve_targets=h.valve_targets,
@@ -4875,10 +5143,12 @@ class HeatPumpOptimizer:
                 else space_matrix + dhw_plan_power
             )
             return self._cost_terms_batch(
-                traj, grid_power,
+                traj,
+                grid_power if heat_matrix is space_matrix else heat_matrix + dhw_plan_power,
+                level_cost=_with_switch_cost(
+                    cycling_batch(grid_power) + capacity_batch(grid_power),
+                    switch_cost(space_matrix, dhw_plan_power)),
                 energy_cost_of=energy_cost_of,
-                cycling_batch=cycling_batch,
-                capacity_batch=capacity_batch,
                 terminal_cost_batch=terminal_cost_batch,
                 comfort_targets=comfort_targets,
                 temp_min_bounds=temp_min_bounds,
@@ -5165,8 +5435,7 @@ class HeatPumpOptimizer:
         initial_state, prices, dt, n_steps = (
             h.initial_state, h.prices, h.dt, h.n_steps
         )
-        outdoor_temps, wind_speeds = h.outdoor_temps, h.wind_speeds
-        precipitation, solar_radiation = h.precipitation, h.solar_radiation
+        outdoor_temps = h.outdoor_temps
         weather = WeatherSeries.from_horizon(h)
         comfort_targets = h.comfort_targets
         step_hours, solar_gains_per_step = h.step_hours, h.solar_gains
@@ -5192,24 +5461,8 @@ class HeatPumpOptimizer:
         # hot water must be available; outside it there is no requirement, so
         # the only reason to run the pump is to be ready for the *next* window
         # — and the energy-cost term then decides *when* that happens.
-        dhw_plan, self._dhw_requirement = planner._build_dhw_requirements(
-            h,
-            p_max=p_max,
-            # The DHW block honours an external ceiling through this scalar,
-            # the horizon's minimum — the same conservative, never-over-the-
-            # line approximation the fuse guard's cap already makes here. A
-            # quiet silent window's cap therefore bounds every DHW block the
-            # same way (#1910); its OFF steps are per-step, below, through
-            # the forced-off door where the energy is re-bought elsewhere.
-            p_run_cap=(
-                float(np.min(h.power_caps_extra))
-                if h.power_caps_extra is not None
-                else None
-            ),
-            blocked=h.dhw_blocked,
-            off_steps=h.off_steps,
-            wood_temps=planner._dhw_coil_wood_forecast(h),
-        )
+        dhw_plan, self._dhw_requirement = _dhw_build(
+            planner, h, p_max, wood_temps=planner._dhw_coil_wood_forecast(h))
 
         dhw_floor_temps = dhw_plan.floor_temps
         dhw_ready_temps = dhw_plan.ready_temps
@@ -5286,10 +5539,18 @@ class HeatPumpOptimizer:
             planner=planner,
             draw_rates=dhw_draw_rates,
         )
+        optimal_space, optimal_dhw, status = _avoid_priced_switches(
+            self, h, planner, solve_space, objective, p_max,
+            (optimal_space, optimal_dhw, status),
+        )
         optimal_space, optimal_dhw = _realize_joint(
             self.config.clamp_planned_levels, optimal_space, optimal_dhw,
             p_min, p_max,
         )
+        # Received through the vector the adopted solve scored with, never a
+        # rebuilt one; the schedule and the achieved objective keep the level.
+        heat_space = optimal_space if self._space_avail is None else duty_legs.delivered_space(
+            optimal_space, optimal_dhw, self._space_avail, _duty_floor(self))
 
         # Simulate with optimal schedule
         published_end: list[ThermalState] = []
@@ -5303,7 +5564,7 @@ class HeatPumpOptimizer:
             wood_temps,
         ) = self.model.simulate_trajectory_with_dhw(
             initial_state=initial_state,
-            space_power_schedule=optimal_space,
+            space_power_schedule=heat_space,
             dhw_power_schedule=optimal_dhw,
             weather=WeatherSeries.from_horizon(h),
             start_hour=start_hour,
@@ -5319,6 +5580,7 @@ class HeatPumpOptimizer:
             combi_dhw_net_series(
                 self.model, buffer_temps, optimal_dhw, dhw_draw_rates, outdoor_temps, h.humidity)
             if self.model.params.dhw_store.combi else None,
+            self._space_avail,
         ))
 
         # Baseline cost. The reference holds the comfort schedule, not the comfort the plan
@@ -5329,7 +5591,7 @@ class HeatPumpOptimizer:
         baseline_dhw, baseline_cost, predicted_cost, dhw_cost = (
             planner._baseline_dhw_economics(
                 initial_state, outdoor_temps, n_steps, dhw_setpoint,
-                energy_cost_of, baseline_power, optimal_space, optimal_dhw, h.humidity,
+                energy_cost_of, baseline_power, heat_space, optimal_dhw, h.humidity,
             )
         )
 
diff --git a/custom_components/heatpump_optimizer/pump_arbiter.py b/custom_components/heatpump_optimizer/pump_arbiter.py
index ef1b85eb0f..6de206bca3 100644
--- a/custom_components/heatpump_optimizer/pump_arbiter.py
+++ b/custom_components/heatpump_optimizer/pump_arbiter.py
@@ -194,6 +194,7 @@ from .log_latch import log_held
 from .payload import REASON_LEGIONELLA, CurrentAction
 from .plan_step import PLAN_STEP_HOURS, PLAN_STEP_MINUTES, plan_step_start
 from .drift import utc_elapsed_seconds, utc_shift
+from .duty_legs import both_step_legs
 from .drift import stored_instant
 from .store import QuarantiningStore, load_mapping
 from .thermal_model import (
@@ -246,9 +247,6 @@ ISSUE_MANUAL = "pump_manual_change"
 ISSUE_IGNORED = "pump_write_ignored"
 #: How long an ignored write waits before it is sent again.
 RETRY_MINUTES = 5.0
-#: The shortest single-duty share of a both step; a shorter share goes to
-#: the other duty for the whole step (valve travel and compressor cycling).
-SPLIT_MIN_MINUTES = 5.0
 TANK_RISE_C = 0.5
 _STORE_VERSION = 1
 
@@ -1826,13 +1824,11 @@ def _share(coord: Any, inp: ArbiterInputs, duty: str | None, now: datetime) -> s
         return duty
     result = inp.plan
     i = bisect.bisect_right(result.timestamps, now) - 1
-    space, dhw = result.power_schedule[i], result.dhw_power_schedule[i]
-    dhw_min = PLAN_STEP_MINUTES * dhw / (space + dhw)
-    if dhw_min < SPLIT_MIN_MINUTES:
-        return "space"
-    if PLAN_STEP_MINUTES - dhw_min < SPLIT_MIN_MINUTES:
-        return "dhw"
-    return "dhw" if (now - result.timestamps[i]) < timedelta(minutes=dhw_min) else "space"
+    legs = both_step_legs(
+        result.power_schedule[i], result.dhw_power_schedule[i], PLAN_STEP_MINUTES
+    )
+    first_ends = timedelta(minutes=legs[0][1])
+    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]
 
 
 def on_off_service(entity_id: str, on: bool) -> tuple[str, str]:
diff --git a/custom_components/heatpump_optimizer/thermal_model.py b/custom_components/heatpump_optimizer/thermal_model.py
index b297aaf44c..20c8f0db92 100644
--- a/custom_components/heatpump_optimizer/thermal_model.py
+++ b/custom_components/heatpump_optimizer/thermal_model.py
@@ -2291,6 +2291,17 @@ def valve_hold_temperature(
     return float(np.interp(need_kw, [_circuit_draw(circuits, k) for k in kinks], kinks))
 
 
+def valve_top_draw(
+    model: "ThermalModel", state: ThermalState, outdoor_temp: float,
+    wind_speed: float, precipitation: float,
+) -> float:
+    """The most the emitters can draw behind the valve, kW: the tank at the
+    curve's top (or ``buffer_max_temp``), past which a hotter tank adds nothing."""
+    circuits = _valve_draw_circuits(
+        model, state, outdoor_temp, wind_speed, precipitation)
+    return _circuit_draw(circuits, model.params.buffer_max_temp)
+
+
 def valve_charge_demand(
     model: "ThermalModel", state: ThermalState, need_kw: float,
     outdoor_temp: float, wind_speed: float, precipitation: float,
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
diff --git a/dev/audit/harnesses/r10_duty_switch_price_section.py b/dev/audit/harnesses/r10_duty_switch_price_section.py
new file mode 100644
index 0000000000..6f6895aca6
--- /dev/null
+++ b/dev/audit/harnesses/r10_duty_switch_price_section.py
@@ -0,0 +1,223 @@
+#!/usr/bin/env python3
+"""Run R10-DUTY-SWITCH-PLANNER-PRICE's section of ``tests/features.py`` alone, and its mutants.
+
+WHY IT EXISTS. ``tests/features.py`` has no section filter, and the mutation
+proof of the group (the leg rule's leaf, the switch term, the lost running
+time, the banned candidate, the learner's count cap and its read for the
+planner) runs the section once per mutant. This cuts the section out of the
+script at its two markers, binds the six names the script had bound by then,
+and runs it. It executes the tree's own text: a check edited in
+``tests/features.py`` is the check run here.
+
+It refuses (exit 2) when a marker is missing or the section holds no check,
+so a moved marker cannot read as a pass.
+
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py
+    PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_duty_switch_price_section.py --mutants [name ...]
+
+``--mutants`` copies the package and ``tests/`` to a private directory per
+mutant, applies one edit there (the tree is never written), runs the section
+on the copy and prints the checks that went red. An unmutated copy runs
+first as the control and must pass. A mutant whose pattern is not found
+exactly once, or that turns no check red, is printed as such and the exit
+code is 1. The coordinator's one argument is outside the section (its check
+sits beside #1512's in the lifecycle part of the script) and is proven by a
+whole run of ``tests/features.py``.
+"""
+from __future__ import annotations
+
+import os
+import shutil
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
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
+ROOT = repo_root(os.environ.get("DSP_SECTION_ROOT") or __file__)
+START = "from types import SimpleNamespace as _DspNS"
+END = '\nsys.exit(R.close("FEATURE CHECKS"))'
+PRELUDE = """
+from datetime import datetime, timedelta
+import numpy as np
+from harness import Results, UTC
+from profiles import solve_inputs
+R = Results("R10-DUTY-SWITCH-PLANNER-PRICE's section of tests/features.py")
+"""
+PKG = "custom_components/heatpump_optimizer/"
+
+#: name, file, the text to find exactly once, its replacement.
+MUTANTS: list[tuple[str, str, str, str]] = [
+    ("optimizer: a candidate is tried with no requirement to hold it to", PKG + "optimizer.py",
+     "if kept_requirement is None or not duty_legs.switch_weight(", "if not duty_legs.switch_weight("),
+    ("optimizer: a candidate pass that raises is not caught", PKG + "optimizer.py",
+     "    except Exception as err:  # noqa: BLE001 - a candidate is optional", "    except KeyError as err:  # a candidate is optional"),
+    ("learner: no count cap", PKG + "duty_switch.py",
+     "        if self.n > N_CAP:\n", "        if False:\n"),
+    ("learner: the cap scales the stops alone", PKG + "duty_switch.py",
+     "self.k, self.kept_w = self.k * scale, self.kept_w * scale", "self.k = self.k * scale"),
+    ("learner: the cap is three times the on-threshold", PKG + "duty_switch.py",
+     "N_CAP = 2.0 * N_ON", "N_CAP = 3.0 * N_ON"),
+    ("learner: the read ignores the latch", PKG + "duty_switch.py",
+     "read = [d if d.usable else Direction() for", "read = [d for"),
+    ("learner: the read swaps the directions", PKG + "duty_switch.py",
+     "return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+     "return (read[1].p, read[0].p), (read[1].median_off_s or 0.0, read[0].median_off_s or 0.0)"),
+    ("learner: the read hands the off time of the other direction", PKG + "duty_switch.py",
+     "(read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+     "(read[1].median_off_s or 0.0, read[0].median_off_s or 0.0)"),
+    ("leaf: the hot-water-to-heating switch reads the other direction", PKG + "duty_legs.py",
+     "(before == DHW) & (after == SPACE),\n        p_ds,", "(before == DHW) & (after == SPACE),\n        p_sd,"),
+    ("leaf: the switch weight takes the larger neighbouring draw", PKG + "duty_legs.py",
+     "np.minimum(level[_BEFORE], level[_AFTER])", "np.maximum(level[_BEFORE], level[_AFTER])"),
+    ("leaf: the in-step weight draws the smaller circuit, not the combined draw", PKG + "duty_legs.py",
+     "np.where(two, p_ds * level, 0.0)",
+     "np.where(two, p_ds * np.minimum(space, np.asarray(dhw_kw, dtype=float)), 0.0)"),
+    ("leaf: the weight is not divided by the maximum draw", PKG + "duty_legs.py",
+     "axis=1)) / p_max", "axis=1))"),
+    ("leaf: a small hot-water share no longer collapses to heating", PKG + "duty_legs.py",
+     "to_space = both & (dhw_min < SPLIT_MIN_MINUTES)", "to_space = both & (dhw_min > SPLIT_MIN_MINUTES)"),
+    ("leaf: a small heating share no longer collapses to hot water", PKG + "duty_legs.py",
+     "~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)",
+     "~to_space & (step_minutes - dhw_min > SPLIT_MIN_MINUTES)"),
+    ("leaf: the leg classification ignores the duty floor", PKG + "duty_legs.py",
+     "_runs(space, floor), _runs(dhw, floor)", "_runs(space, None), _runs(dhw, None)"),
+    # The leaf has no zero-pair return: zero probabilities weigh zero on the
+    # full path, and the optimizer never calls it without a priced direction.
+    ("leaf: a pump with no maximum draw is not returned early", PKG + "duty_legs.py",
+     "    if p_max <= 0:\n        return np.zeros(space.shape[0])", "    if p_max < 0:\n        return np.zeros(space.shape[0])"),
+    ("leaf: a negative learned value is kept", PKG + "duty_legs.py",
+     "max(v, 0.0) if math.isfinite(v) and v <= upper", "v if math.isfinite(v) and v <= upper"),
+    ("leaf: a learned value on its upper bound reads as zero", PKG + "duty_legs.py",
+     "max(v, 0.0) if math.isfinite(v) and v <= upper", "max(v, 0.0) if math.isfinite(v) and v < upper"),
+    ("leaf: the early return is one entry per step, not per row", PKG + "duty_legs.py",
+     "return np.zeros(space.shape[0])", "return np.zeros(space.shape[1])"),
+    ("optimizer: no priced direction still returns a pair", PKG + "optimizer.py",
+     "return stops if max(stops) > 0 else None", "return stops"),
+    ("leaf: the charged step is the hot-water block's last step", PKG + "duty_legs.py",
+     "charged[1:] |= (last[:-1] == DHW) & (first[1:] == SPACE)",
+     "charged[:-1] |= (last[:-1] == DHW) & (first[1:] == SPACE)"),
+    ("leaf: the delivered draw is keyed on the clamped install", PKG + "duty_legs.py",
+     "    if floor is None:\n        return space_kw", "    if floor is not None:\n        return space_kw"),
+    ("leaf: the delivered draw loses only the space share", PKG + "duty_legs.py",
+     "(1.0 - avail) * (space_kw + dhw_kw)", "(1.0 - avail) * space_kw"),
+    ("optimizer: the switch term is handed the delivered draw", PKG + "optimizer.py",
+     "switch_cost(space_power, dhw_plan_power)", "switch_cost(heat_power, dhw_plan_power)"),
+    ("optimizer: the simulation is handed the shipped draw", PKG + "optimizer.py",
+     "_space_traj(heat_power, buffer_exo_kw)", "_space_traj(space_power, buffer_exo_kw)"),
+    ("optimizer: the energy cost is handed the shipped draw", PKG + "optimizer.py",
+     "drawn = combined if heat_power is space_power else heat_power + dhw_plan_power",
+     "drawn = combined"),
+    ("optimizer: the publication drops the solve's availability vector", PKG + "optimizer.py",
+     "heat_space = optimal_space if self._space_avail is None else duty_legs",
+     "heat_space = optimal_space if True else duty_legs"),
+    ("planner: the placement ban is not OR'd into forced_off", PKG + "dhw_planner.py",
+     "return forced_off if ban is None else _forced_off_with(forced_off, ban, n_steps)",
+     "return forced_off"),
+    ("optimizer: a candidate short of its requirement is adopted", PKG + "optimizer.py",
+     "            and first_short(plan.schedule, requirement, unheld)[1] is None\n",
+     "            and True\n"),
+    ("optimizer: a candidate with hot water on a banned step is adopted", PKG + "optimizer.py",
+     "            not np.any(plan.schedule[ban & ~forced_on] > 0)\n", "            True\n"),
+    ("optimizer: the candidate is adopted on a higher score", PKG + "optimizer.py",
+     "if score < base - 1e-9:", "if score > base - 1e-9:"),
+    ("leaf: the lost share is not capped at one", PKG + "duty_legs.py",
+     "return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))",
+     "return stop_probability[0] * off_seconds[0] / (step_minutes * 60.0)"),
+    ("leaf: the lost share ignores the stop probability", PKG + "duty_legs.py",
+     "min(1.0, stop_probability[0] * off_seconds[0] /", "min(1.0, off_seconds[0] /"),
+    # The fix reviewer's three survivors at ee89d50b2b (R5, R9, R11), its texts.
+    ("optimizer: the co-optimisation headroom ignores the availability vector", PKG + "optimizer.py",
+     "p_max, dhw_power, self._space_avail, _duty_floor(self))", "p_max, dhw_power, None, _duty_floor(self))"),
+    ("optimizer: the availability vector is classified with no duty floor", PKG + "optimizer.py",
+     "return duty_legs.availability(space, tank, lost, _duty_floor(opt))",
+     "return duty_legs.availability(space, tank, lost, None)"),
+    ("optimizer: the candidate pass runs on a combi store", PKG + "optimizer.py",
+     "or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
+     "or not opt.config.cycling_cost > 0:"),
+    ("optimizer: the co-optimisation headroom is handed no duty floor", PKG + "optimizer.py",
+     "p_max, dhw_power, self._space_avail, _duty_floor(self))", "p_max, dhw_power, self._space_avail, None)"),
+    # Repair round 2: the two clamps left on the line the availability reads
+    # its start through, the mutation table's CLAMP_DROP twins of one anchor.
+    ("optimizer: the start is read with no cap beside hot water", PKG + "optimizer.py",
+     "np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),", "(start),"),
+    ("optimizer: the start is capped at zero in every step", PKG + "optimizer.py",
+     "np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),", "np.minimum(start, (0.0)),"),
+    ("arbiter: the share serves the legs in reverse order", PKG + "pump_arbiter.py",
+     "return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
+     "return legs[-1][0] if (now - result.timestamps[i]) < first_ends else legs[0][0]"),
+]
+
+
+def run_section(root: Path) -> int:
+    text = (root / "tests" / "features.py").read_text()
+    if text.count(START) != 1 or text.count(END) != 1:
+        print("REFUSED: a section marker is missing or repeated in tests/features.py")
+        return 2
+    section = text[text.index(START):text.index(END)]
+    sys.path[:0] = [str(root / "tests"), str(root / "custom_components")]
+    scope: dict = {"__name__": "duty_switch_price_section"}
+    exec(compile(PRELUDE + section, "tests/features.py[duty-switch-price]", "exec"), scope)
+    results = scope["R"]
+    if not results.checks:
+        print("REFUSED: the section ran no check")
+        return 2
+    return results.close("DUTY-SWITCH PLANNER-PRICE SECTION CHECKS")
+
+
+def _copy_run(edit: tuple[str, str, str] | None) -> tuple[int | None, list[str]]:
+    """The section's exit code and red check names on a private copy, ``None`` when the pattern is not there once."""
+    with tempfile.TemporaryDirectory() as tmp:
+        copy = Path(tmp)
+        for part in ("custom_components", "tests"):
+            shutil.copytree(ROOT / part, copy / part, ignore=shutil.ignore_patterns("__pycache__", "golden"))
+        if edit is not None:
+            path, old, new = edit
+            text = (copy / path).read_text()
+            if text.count(old) != 1:
+                return None, []
+            (copy / path).write_text(text.replace(old, new))
+        env = {**os.environ, "DSP_SECTION_ROOT": str(copy / "custom_components"),
+               "PYTHONPATH": str(copy / "tests" / "hastub"), "PYTHONDONTWRITEBYTECODE": "1"}
+        out = subprocess.run([sys.executable, __file__], cwd=copy, env=env, capture_output=True, text=True)
+        red = [line[7:].split("  [")[0] for line in out.stdout.splitlines() if line.startswith("  FAIL ")]
+        if "SECTION CHECKS" not in out.stdout:  # a traceback exits 1 too, and closes nothing
+            red.append(f"the section stopped: {(out.stderr.strip().splitlines() or ['no output'])[-1]}")
+        return out.returncode, red
+
+
+def run_mutants(names: list[str]) -> int:
+    code, red = _copy_run(None)
+    print(f"== control, no edit: exit {code}, {len(red)} red")
+    if code != 0:
+        print("\n".join(f"     {name}" for name in red))
+        return 1
+    bad = 0
+    for name, path, old, new in MUTANTS:
+        if names and name not in names:
+            continue
+        code, red = _copy_run((path, old, new))
+        verdict = "PATTERN NOT FOUND ONCE" if code is None else f"{len(red)} red" if red else "SURVIVED"
+        bad += not red
+        print(f"== {name}: {verdict}")
+        print("\n".join(f"     {check}" for check in red), end="\n" if red else "")
+    print(f"RESULT mutants_not_killed={bad}")
+    return 1 if bad else 0
+
+
+if __name__ == "__main__":
+    os.chdir(ROOT)
+    sys.exit(run_mutants(sys.argv[2:]) if sys.argv[1:2] == ["--mutants"] else run_section(ROOT))
diff --git a/dev/audit/harnesses/r10_sav_held_capacity_census.py b/dev/audit/harnesses/r10_sav_held_capacity_census.py
new file mode 100644
index 0000000000..5b597dec0c
--- /dev/null
+++ b/dev/audit/harnesses/r10_sav_held_capacity_census.py
@@ -0,0 +1,100 @@
+"""R10-SAV-VALUATION-RESIDUE: the held state's census over every bound on the reference's heat.
+
+    PYTHONPATH=tests/hastub:tests:custom_components \\
+        python3 dev/audit/harnesses/r10_sav_held_capacity_census.py
+
+Drives ``_thermostat_held_state`` over a grid of installs -- no valve and the
+three throttling valve modes, both zonings, the derived and the
+``two_tank_4way`` layout, pumps of 4, 6 and 9 kW, valve targets 21 to 40 C,
+outdoor -25 to 18 C -- and books one reference step from each held state at
+``_compute_baseline_power``'s power on a one-step horizon (nothing to
+apportion). The property is the phenomenon's, not an instance's: a held state
+the reference step can keep draws no stored heat on its first booked step.
+Prints the case count, the worst first-step store change in kWh_th and the
+count over 0.02 kWh_th, then the capacity control: at -25 C a 9 kW pump holds
+21 C (valved and not), a 4 kW pump does not.
+
+Preconditions, asserted (exit 1): every grid case ran without an exception,
+every held room lies in [min(outdoor, 21), 21], and the case count is the
+grid's product.
+"""
+
+import itertools
+import sys
+
+import numpy as np
+
+from heatpump_optimizer.optimizer import (
+    HeatPumpOptimizer,
+    OptimizationConfig,
+    _thermostat_held_state,
+)
+from heatpump_optimizer.thermal_model import (
+    ThermalModel,
+    ThermalParameters,
+    ThermalState,
+    WeatherSeries,
+)
+from profiles import house
+
+TARGET_C = 21.0
+MODES = ("none", "manual", "smart_read", "smart_write")
+ZONINGS = (True, False)
+LAYOUTS = (None, "two_tank_4way")
+PUMPS_KW = (4.0, 6.0, 9.0)
+VALVE_TARGETS_C = (21.0, 25.0, 30.0, 40.0)
+OUTDOORS_C = (-25.0, -15.0, -5.0, 0.0, 5.0, 10.0, 14.0, 16.0, 18.0)
+
+
+def first_step(mode, two_zone, layout, pump_kw, valve_target, outdoor):
+    """The held state and its first booked reference step's store change, kWh_th."""
+    cfg = {"buffer_tank_volume": 750.0, "buffer_max_temperature": 56.0,
+           "heat_pump_max_power": pump_kw}
+    if mode != "none":
+        cfg.update(mixing_valve_mode=mode, mixing_valve_target=valve_target)
+    if layout:
+        cfg["topology_layout"] = layout
+    model = ThermalModel(ThermalParameters.from_config(house(two_zone=two_zone, dhw=False, **cfg)))
+    opt = HeatPumpOptimizer(model, OptimizationConfig(
+        horizon_hours=1, time_step_minutes=15, target_temp=TARGET_C))
+    weather = WeatherSeries(outdoor_temps=np.array([outdoor]), wind_speeds=np.zeros(1),
+                            precipitation=np.zeros(1), solar_radiation=np.zeros(1))
+    start = ThermalState(room_temperature=20.5, slab_temperature=22.0,
+                         outdoor_temperature=outdoor, upper_floor_temperature=20.5,
+                         lower_floor_temperature=20.5, buffer_tank_temperature=30.0)
+    held = _thermostat_held_state(model, start, weather, TARGET_C)
+    power = float(opt._compute_baseline_power(weather, start, 0.25)[0][0])
+    nxt = model.simulate_step(held, power, outdoor, 0.0, 0.0, 0.0, 0.25)
+    return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), power
+
+
+def main() -> int:
+    grid = list(itertools.product(MODES, ZONINGS, LAYOUTS, PUMPS_KW, VALVE_TARGETS_C, OUTDOORS_C))
+    ran, worst, worst_case, over, refused = 0, 0.0, None, 0, []
+    for case in grid:
+        try:
+            held, ds, power = first_step(*case)
+        except Exception as exc:  # a refusal is a precondition failure, reported
+            refused.append((case, repr(exc)[:120]))
+            continue
+        ran += 1
+        outdoor = case[-1]
+        if not min(outdoor, TARGET_C) - 1e-9 <= held.room_temperature <= TARGET_C:
+            refused.append((case, f"held room {held.room_temperature:.3f} out of range"))
+        if abs(ds) > abs(worst):
+            worst, worst_case = ds, (*case, round(held.room_temperature, 3), round(power, 3))
+        over += abs(ds) > 0.02
+    print(f"RESULT census: cases {ran} of {len(grid)}, worst first-step dS {worst:+.4f} kWh_th "
+          f"at {worst_case}, over 0.02 kWh_th {over}")
+    for mode in ("none", "manual"):
+        for pump_kw in (4.0, 9.0):
+            held, ds, power = first_step(mode, True, None, pump_kw, 40.0, -25.0)
+            print(f"RESULT control two-zone -25 C mode={mode} pump {pump_kw} kW: held room "
+                  f"{held.room_temperature:.3f} power {power:.3f} first-step dS {ds:+.4f} kWh_th")
+    for case, why in refused[:10]:
+        print("REFUSED", case, why)
+    return 1 if refused or ran != len(grid) else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/dev/audit/rounds/round4/D6/claims.json b/dev/audit/rounds/round4/D6/claims.json
index e67593e30e..e3d6e2186d 100644
--- a/dev/audit/rounds/round4/D6/claims.json
+++ b/dev/audit/rounds/round4/D6/claims.json
@@ -283,7 +283,7 @@
   "source": "docs/architecture.md",
   "claim": "45 modules",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "documented=90 measured=90",
+  "result": "documented=91 measured=91",
   "verdict": "true",
   "truth": ""
  },
@@ -292,7 +292,7 @@
   "source": "docs/architecture.md",
   "claim": "the module map is the package's module list",
   "command": "PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py",
-  "result": "on disk=90, listed=90, missing=[], phantom=[]",
+  "result": "on disk=91, listed=91, missing=[], phantom=[]",
   "verdict": "true",
   "truth": "0 modules are absent from the map: "
  },
diff --git a/dev/audit/rounds/round4/D6/claims.md b/dev/audit/rounds/round4/D6/claims.md
index 95033a6826..e4521e8162 100644
--- a/dev/audit/rounds/round4/D6/claims.md
+++ b/dev/audit/rounds/round4/D6/claims.md
@@ -35,8 +35,8 @@ Generated by `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.
 | C29 | `docs/architecture.md:module map` | config_flow.py -- Setup flow plus 24 option pages behind two menus | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=24 measured=24 | **true** |  |
 | C30 | `docs/configuration.md` | every documented Default (97 rows) is the default the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 97 compared, mismatches=[] | **true** |  |
 | C31 | `docs/configuration.md` | every documented Range (104 rows) is the NumberSelector min/max the rendered options page actually carries | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 104 compared, mismatches=[] | **true** |  |
-| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=90 measured=90 | **true** |  |
-| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=90, listed=90, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
+| C32 | `docs/architecture.md` | 45 modules | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=91 measured=91 | **true** |  |
+| C33 | `docs/architecture.md` | the module map is the package's module list | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | on disk=91, listed=91, missing=[], phantom=[] | **true** | 0 modules are absent from the map:  |
 | C34 | `docs/architecture.md:The Home Assistant boundary` | the boundary sentence's count of modules importing `homeassistant` at module level | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | documented=32 measured=32 | **true** |  |
 | C35 | `docs/architecture.md:The Home Assistant boundary` | the named modules are the complete set of module-level importers | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | named=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], measured=['__init__.py', 'accuracy.py', 'away.py', 'binary_sensor.py', 'boost.py', 'button.py', 'climate.py', 'config_flow.py', 'coordinator.py', 'currency.py', 'datetime.py', 'debugger.py', 'defrost.py', 'dhw_learning.py', 'diagnostics.py', 'duty_switch.py', 'early_cutoff.py', 'entity.py', 'frontend.py', 'heat_curve.py', 'issues.py', 'legionella.py', 'notifier.py', 'off_restore.py', 'open_meteo.py', 'pump_arbiter.py', 'repairs.py', 'sensor.py', 'services.py', 'store.py', 'supply_hold.py', 'switch.py'], unnamed=[] | **true** | unnamed module-level importers:  |
 | C36 | `docs/architecture.md:The Home Assistant boundary` | everything outside the named set is free of homeassistant, so each module can be driven with no Home Assistant running | `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` | 0 modules outside the named set import homeassistant at module level | **true** | modules outside the named set import homeassistant at module level and cannot be imported without it:  |
diff --git a/dev/audit/rounds/round4/D6/claims.py b/dev/audit/rounds/round4/D6/claims.py
index 6c6056f2b9..53645fb18f 100644
--- a/dev/audit/rounds/round4/D6/claims.py
+++ b/dev/audit/rounds/round4/D6/claims.py
@@ -91,7 +91,7 @@ against a document that is CORRECT.
                                          Range row on the expert thermal-model
                                          table; 101 with R10-USER-DOCS-FINAL's
                                          per-field rows on the options pages)
-    RESULT arch_modules_on_disk=90       (89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_modules_on_disk=91       (90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 85 until R10-WHY-NOW-WIDGET's slot_drivers.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          65 until #1588's pump_arbiter.py; 64
                                          until #1408's store.py;
@@ -117,7 +117,7 @@ against a document that is CORRECT.
                                          bytes of, so nothing compared these
                                          numbers to a run between 2026-09-17
                                          and then)
-    RESULT arch_map_listed=90            (89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
+    RESULT arch_map_listed=91            (90 until R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py; 89 until the supply-hold PR's supply_hold.py; 88 until R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py; 86 until R10-GENERIC-HEAT-CURVE's heat_curve.py and off_restore.py; 84 until R10-GRADE-DRIVERS's driving_grade.py; 83 until R10-ADVISOR-WHATIF's plan_slots.py; 82 until R10-HEAT-METER's heat_energy.py; 81 until R10-LEARNER-ETA's learner_progress.py; 80 until R10-ADVISOR's price_tiles.py; 79 until R10-DIAG-REPLAY's replay_doc.py; 78 until R10-PUMP-MODEL's plan_step.py; 77 until R10-N-log-flood's log_latch.py; 76 until R10-FAHRENHEIT's issues.py; 75 until the live-fix wave's early_cutoff.py; 74 until the live power clamp's draw_range.py; 72 until R9-UX-9's flow_meter.py and R9-EG-B11's entry_config.py; 70 until R9-DBG-1's debugger.py and R9-SW-1's quiet_windows.py; 69 until R9-UX-4's notifier.py; 68 until R9-EG-B3a's payload.py; 67 until R9 EG-B5's dhw_planner.py;
                                          66 until R9 F2.5's batchmath.py;
                                          was 45; 11 were missing; 66 with
                                          #1588's pump_arbiter.py added to
diff --git a/dev/programme/delivery/3499.md b/dev/programme/delivery/3499.md
index ab08e8486e..e6f9d2f65f 100644
--- a/dev/programme/delivery/3499.md
+++ b/dev/programme/delivery/3499.md
@@ -1 +1 @@
-- [#3499](https://github.com/tvofi/heatpump_optimizer/pull/3499) — **open**, R10-GATE-DEFER-BARRIER: r10 gate defer barrier (R10-GATE-DEFER-BARRIER)
+- [#3499](https://github.com/tvofi/heatpump_optimizer/pull/3499) — **merged `6142f48`**, R10-GATE-DEFER-BARRIER: r10 gate defer barrier (R10-GATE-DEFER-BARRIER).
diff --git a/dev/programme/delivery/3511.md b/dev/programme/delivery/3511.md
new file mode 100644
index 0000000000..071ec1a8dc
--- /dev/null
+++ b/dev/programme/delivery/3511.md
@@ -0,0 +1 @@
+- [#3511](https://github.com/tvofi/heatpump_optimizer/pull/3511) — **merged `90c6bc3`**, R10-SAV-VALUATION-RESIDUE: r10 sav valuation residue.
diff --git a/dev/programme/delivery/3520.md b/dev/programme/delivery/3520.md
index 99ff6e09e8..622ef34ae4 100644
--- a/dev/programme/delivery/3520.md
+++ b/dev/programme/delivery/3520.md
@@ -1 +1 @@
-- [#3520](https://github.com/tvofi/heatpump_optimizer/pull/3520) — **open**, R10-HOTFIX-TICK-SELFTEST-CHECKOUT: r10 hotfix tick selftest checkout (R10-HOTFIX-TICK-SELFTEST-CHECKOUT)
+- [#3520](https://github.com/tvofi/heatpump_optimizer/pull/3520) — **merged `ad95665`**, R10-HOTFIX-TICK-SELFTEST-CHECKOUT: r10 hotfix tick selftest checkout.
diff --git a/dev/programme/delivery/3526.md b/dev/programme/delivery/3526.md
new file mode 100644
index 0000000000..34a6cfc62c
--- /dev/null
+++ b/dev/programme/delivery/3526.md
@@ -0,0 +1 @@
+- [#3526](https://github.com/tvofi/heatpump_optimizer/pull/3526) — **merged `c67c193`**, R10-DUTY-SWITCH-PLANNER-PRICE: r10 duty switch planner price (R10-DUTY-SWITCH-PLANNER-PRICE).
diff --git a/dev/programme/delivery/3539.md b/dev/programme/delivery/3539.md
index 80a5e06e48..310486959d 100644
--- a/dev/programme/delivery/3539.md
+++ b/dev/programme/delivery/3539.md
@@ -1 +1 @@
-- [#3539](https://github.com/tvofi/heatpump_optimizer/pull/3539) — **open**, R10-REVIEW-DISPATCH-RESIDUE (part 6): r10 review dispatch residue p6 (R10-REVIEW-DISPATCH-RESIDUE)
+- [#3539](https://github.com/tvofi/heatpump_optimizer/pull/3539) — **merged `1906e79`**, R10-REVIEW-DISPATCH-RESIDUE (part 6): r10 review dispatch residue p6.
diff --git a/dev/programme/delivery/3546.md b/dev/programme/delivery/3546.md
new file mode 100644
index 0000000000..375ea41b10
--- /dev/null
+++ b/dev/programme/delivery/3546.md
@@ -0,0 +1 @@
+- [#3546](https://github.com/tvofi/heatpump_optimizer/pull/3546) — **open**, R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: r10 hotfix updatepr figure refresh (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH)
diff --git a/dev/programme/delivery/3549.md b/dev/programme/delivery/3549.md
index b2769f696d..7ceb24fe6f 100644
--- a/dev/programme/delivery/3549.md
+++ b/dev/programme/delivery/3549.md
@@ -1 +1 @@
-- [#3549](https://github.com/tvofi/heatpump_optimizer/pull/3549) — **open**, R10-HOTFIX-OPENER-REFUSALS: open_pr.sh shares one body file across two runs, and ci_predict reads a stale roster ref (R10-HOTFIX-OPENER-REFUSALS)
+- [#3549](https://github.com/tvofi/heatpump_optimizer/pull/3549) — **merged `cfa8683`**, R10-HOTFIX-OPENER-REFUSALS: open_pr.sh shares one body file across two runs, and ci_predict reads a stale roster ref (R10-HOTFIX-OPENER-REFUSALS).
diff --git a/dev/programme/delivery/3554.md b/dev/programme/delivery/3554.md
index 8c6d8f8d39..2d2eff2c46 100644
--- a/dev/programme/delivery/3554.md
+++ b/dev/programme/delivery/3554.md
@@ -1 +1 @@
-- [#3554](https://github.com/tvofi/heatpump_optimizer/pull/3554) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster ce60e992 (v7.1.15) (R10-ROSTER-BATCH24)
+- [#3554](https://github.com/tvofi/heatpump_optimizer/pull/3554) — **merged `e28a310`**, roster: land the round-10 roster from handoff/audit-r10-roster ce60e992 (v7.1.15).
diff --git a/dev/programme/delivery/3555.md b/dev/programme/delivery/3555.md
index 04eb95d993..4d785d436a 100644
--- a/dev/programme/delivery/3555.md
+++ b/dev/programme/delivery/3555.md
@@ -1 +1 @@
-- [#3555](https://github.com/tvofi/heatpump_optimizer/pull/3555) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster b1697d36 (carry-201 entry 6 remeasure) (R10-ROSTER-BATCH24)
+- [#3555](https://github.com/tvofi/heatpump_optimizer/pull/3555) — **merged `154dbb4`**, roster: land the round-10 roster from handoff/audit-r10-roster b1697d36 (carry-201 entry 6 remeasure).
diff --git a/dev/programme/delivery/3558.md b/dev/programme/delivery/3558.md
new file mode 100644
index 0000000000..ba59b6fa03
--- /dev/null
+++ b/dev/programme/delivery/3558.md
@@ -0,0 +1 @@
+- [#3558](https://github.com/tvofi/heatpump_optimizer/pull/3558) — **open**, R10-HOTFIX-TICK-BASH32: r10 hotfix tick bash32 (R10-HOTFIX-TICK-BASH32)
diff --git a/dev/programme/delivery/3559.md b/dev/programme/delivery/3559.md
new file mode 100644
index 0000000000..c2150aeb02
--- /dev/null
+++ b/dev/programme/delivery/3559.md
@@ -0,0 +1 @@
+- [#3559](https://github.com/tvofi/heatpump_optimizer/pull/3559) — **open**, record: delivery rows (autofix)
diff --git a/dev/programme/delivery/3561.md b/dev/programme/delivery/3561.md
new file mode 100644
index 0000000000..fb498f03e4
--- /dev/null
+++ b/dev/programme/delivery/3561.md
@@ -0,0 +1 @@
+- [#3561](https://github.com/tvofi/heatpump_optimizer/pull/3561) — **open**, R10-HOTFIX-FLOW-SETPOINT-STUCK: r10 hotfix flow setpoint stuck (R10-HOTFIX-FLOW-SETPOINT-STUCK)
diff --git a/docs/architecture.md b/docs/architecture.md
index 779d4e609c..b8d322ea01 100644
--- a/docs/architecture.md
+++ b/docs/architecture.md
@@ -5,7 +5,7 @@ integration does rather than how it is built, start with
 [how-it-works.md](how-it-works.md).
 
 The shape is a thin Home Assistant layer wrapped around a much larger core that
-knows nothing about Home Assistant: 90 modules, of which 32 import the
+knows nothing about Home Assistant: 91 modules, of which 32 import the
 `homeassistant` package at module level, one more touches it inside a single
 function, and the rest take numbers in and give numbers back. The glue reads
 entity states, writes actuators and persists learned state. Keeping those two
@@ -126,6 +126,8 @@ custom_components/heatpump_optimizer/
 ├── optimizer.py          # The MPC solve: DHW by LP, space by L-BFGS-B, reason codes
 ├── plan_step.py          # The plan step: its width, and which step an instant
 │                         #   falls in, for the solve and the pump arbiter
+├── duty_legs.py          # The legs a step is served in, the switches between
+│                         #   them, and what a stop at one costs the plan
 ├── plan_slots.py         # A channel's step schedule as the heating slots a plan publishes
 ├── slot_drivers.py       # Why each step runs or idles: five signed driver weights,
 │                         #   and the current step's "why now" for the card
@@ -189,7 +191,8 @@ custom_components/heatpump_optimizer/
 ├── supply_hold.py        # The supply switch's minimum run and pause, held
 │                         #   across a re-solve, a cycle or a restart
 ├── duty_switch.py        # Learns per direction whether a duty switch stops
-│                         #   the running compressor; observes, changes nothing
+│                         #   the running compressor; a latched direction's
+│                         #   estimate is what the solve prices that switch by
 ├── heat_curve.py         # The heat-curve displace's outputs: the ECL110 MQTT
 │                         #   topics and an offset number entity
 ├── off_restore.py        # The one owner of the off and unload restore: what
@@ -270,7 +273,7 @@ custom_components/heatpump_optimizer/
 
 ## The Home Assistant boundary
 
-32 of the 90 modules import `homeassistant` at module level: `__init__`,
+32 of the 91 modules import `homeassistant` at module level: `__init__`,
 `config_flow`, `coordinator`, `open_meteo`, `frontend`, the six entity
 platforms `sensor`, `binary_sensor`, `button`, `climate`, `switch`, `datetime`,
 and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`, `defrost`,
@@ -279,7 +282,7 @@ and the supporting modules `accuracy`, `away`, `boost`, `currency`, `debugger`,
 reaches for `homeassistant.util.dt` inside a function, as the fallback when no
 clock function was injected.
 
-The other 57 modules are deliberately free of it, so each can be driven
+The other 58 modules are deliberately free of it, so each can be driven
 directly by `tests/features.py` with no Home Assistant running. That matters
 because the failure mode of this integration is a *plausible* plan: a detector
 that never fires, or a watchdog that lets a flatline through, produces output
diff --git a/docs/configuration.md b/docs/configuration.md
index d541756be6..de6110392b 100644
--- a/docs/configuration.md
+++ b/docs/configuration.md
@@ -877,8 +877,8 @@ writes, at every 15-minute plan step:
   never taken as yours: after an upgrade from a version without this, the value
   restored is the one the optimizer holds when the plan is not in charge (35 °C
   or the weather curve for a water set-point, the planned room temperature for
-  an indoor one), and the optimizer writes the set-point from its first pass
-  as before. Set it on the pump once while the optimizer is on to have your own
+  an indoor one), and the optimizer writes the set-point from its first pass.
+  Set it on the pump once while the optimizer is on to have your own
   value restored instead. The mode and the hot-water set-point are not restored.
 - **A write the pump does not hold is retried.** If the value written back
   still does not hold, a warning repair notice is raised and the value is sent
diff --git a/tests/closures.json b/tests/closures.json
index a348d731ff..1c16bc7483 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -208,6 +208,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -315,6 +316,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -324,6 +326,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -367,6 +370,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -469,6 +473,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -571,6 +576,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -687,6 +693,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -805,6 +812,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -939,6 +947,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -1063,6 +1072,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -1199,6 +1209,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -1401,6 +1412,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -1410,6 +1422,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -1520,6 +1533,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2042,6 +2056,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2238,6 +2253,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2392,6 +2408,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2535,6 +2552,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2724,6 +2742,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -2892,6 +2911,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3283,6 +3303,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3401,6 +3422,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -3410,6 +3432,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -3453,6 +3476,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3556,6 +3580,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3642,6 +3667,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -3651,6 +3677,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/presets.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
@@ -3706,6 +3733,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3801,6 +3829,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -3875,6 +3904,7 @@
    "custom_components/heatpump_optimizer/dhw_schedule.py",
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/entry_config.py",
    "custom_components/heatpump_optimizer/flow_lift.py",
    "custom_components/heatpump_optimizer/freq_control.py",
@@ -3884,6 +3914,7 @@
    "custom_components/heatpump_optimizer/mixing_valve.py",
    "custom_components/heatpump_optimizer/optimizer.py",
    "custom_components/heatpump_optimizer/payload.py",
+   "custom_components/heatpump_optimizer/plan_step.py",
    "custom_components/heatpump_optimizer/pv.py",
    "custom_components/heatpump_optimizer/slot_drivers.py",
    "custom_components/heatpump_optimizer/tariff.py",
@@ -3927,6 +3958,7 @@
    "custom_components/heatpump_optimizer/draw_range.py",
    "custom_components/heatpump_optimizer/drift.py",
    "custom_components/heatpump_optimizer/driving_grade.py",
+   "custom_components/heatpump_optimizer/duty_legs.py",
    "custom_components/heatpump_optimizer/duty_switch.py",
    "custom_components/heatpump_optimizer/early_cutoff.py",
    "custom_components/heatpump_optimizer/entity.py",
@@ -4208,6 +4240,7 @@
    "dev/audit/harnesses/r10_dhw_lift_law_grid.py",
    "dev/audit/harnesses/r10_diag_ages_export.py",
    "dev/audit/harnesses/r10_disinfection_setpoint.py",
+   "dev/audit/harnesses/r10_duty_switch_price_section.py",
    "dev/audit/harnesses/r10_duty_switch_section.py",
    "dev/audit/harnesses/r10_envmatrix_noremote.sh",
    "dev/audit/harnesses/r10_errexit_capture.py",
@@ -4316,6 +4349,7 @@
    "dev/audit/harnesses/r10_sav_actuation_phase.py",
    "dev/audit/harnesses/r10_sav_baseline.py",
    "dev/audit/harnesses/r10_sav_baseline_mutants.py",
+   "dev/audit/harnesses/r10_sav_held_capacity_census.py",
    "dev/audit/harnesses/r10_sav_null_settled.py",
    "dev/audit/harnesses/r10_sav_null_terms.py",
    "dev/audit/harnesses/r10_sav_receipt_render.py",
@@ -5160,7 +5194,7 @@
   },
   "tests/edge.py": {
    "rc": 0,
-   "seconds": 17.9
+   "seconds": 21.5
   },
   "tests/entities.py": {
    "rc": 0,
@@ -5195,7 +5229,7 @@
    "seconds": 0.2
   },
   "tests/harness_headers.py": {
-   "rc": 1,
+   "rc": 0,
    "seconds": 118.2
   },
   "tests/layout.py": {
@@ -5228,7 +5262,7 @@
   },
   "tests/stress.py": {
    "rc": 0,
-   "seconds": 443.5
+   "seconds": 463.0
   },
   "tests/structure.py": {
    "rc": 2,
@@ -5236,7 +5270,7 @@
   },
   "tests/typing_ruler.py": {
    "rc": 0,
-   "seconds": 0.4
+   "seconds": 33.9
   },
   "tests/validate.py": {
    "rc": 0,
diff --git a/tests/deployment_shape.py b/tests/deployment_shape.py
index 05ea531ba6..7c74c96fb5 100644
--- a/tests/deployment_shape.py
+++ b/tests/deployment_shape.py
@@ -37,9 +37,10 @@ child from ``inspect.getfile``.
 
 COST OF THE SHAPE (#1218, round-5 D3-08). Materialising the shape copies the
 tracked package file by file (``_materialise``, below), and the gate's tracer
-records every read, so this lane's recorded closure is the package: all 109
+records every read, so this lane's recorded closure is the package: all 110
 files under ``custom_components/heatpump_optimizer/``, Python and non-Python
-alike (108 until the supply-hold PR's ``supply_hold.py``, 107 until
+alike (109 until R10-DUTY-SWITCH-PLANNER-PRICE's ``duty_legs.py``, 108 until the supply-hold PR's
+``supply_hold.py``, 107 until
 R10-DUTY-SWITCH-RESTART-LEARNING's ``duty_switch.py``, 78 until R9 F2.5's ``batchmath.py``, 79 until R9 UI-1's six brand
 images, 85 until R9 EG-B5's ``dhw_planner.py``, 86 until R9-EG-B3a's
 ``payload.py``, 87 until R9-UX-4's ``notifier.py``, 88 until R9-SW-1's
@@ -91,7 +92,11 @@ reads the catalogues, moved card.mjs with config_flow_steps.py from 0.800 to
 off_restore.py, read by every closure that imports the coordinator, moved it
 from 145 to 146; R10-DUTY-SWITCH-RESTART-LEARNING's duty_switch.py, read by every
 closure that imports the arbiter, the sensor platform or the store, from 146 to 148; the supply-hold PR's
-supply_hold.py, read by every closure that imports the coordinator, from 148 to 154).
+supply_hold.py, read by every closure that imports the coordinator, from 148 to 154;
+R10-DUTY-SWITCH-PLANNER-PRICE's duty_legs.py, read by every closure that
+imports the optimizer or the arbiter, left it at 154: measured alone on the
+148 recording it moves the same count to 154, the pairs it lifts being ones
+supply_hold.py lifts too).
 Eighteen of the pairs sit at exactly 1.00 -- arch_score_head.py/deployment_shape.py,
 arch_score_head.py/entities.py and deployment_shape.py/entities.py
 (98 shared production files each), doc_claims.py/harness_headers.py
diff --git a/tests/features.py b/tests/features.py
index dd22d8ed9a..3221731e47 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -27662,6 +27662,45 @@ R.check(
     f"(solve, hub): config False -> {_dd_off!r}, default -> {_dd_default!r}",
 )
 
+# R10-DUTY-SWITCH-PLANNER-PRICE: and the duty-switch learner's read for the
+# planner, by the same copy.
+from heatpump_optimizer import duty_switch as _dsp_push_ds  # noqa: E402
+
+
+def _dsp_pushed(learner):
+    hass = FakeHass()
+    _seed_prices(hass)
+    entry = FakeEntry(data={**_LC_DATA}, entry_id="dsp_push")
+    _asyncio.run(_ha_setup_entry(_integ, hass, entry))
+    coord = entry.runtime_data
+    coord._prices = list(_svc_crash_coord._prices)
+    never = coord._solve_hubs(4, banded=True)[0]
+    _dsp_push_ds.record_for(coord).learner = learner
+    return never, coord._solve_hubs(4, banded=True)[0], coord._opt_config
+
+
+_dsp_push_d = _dsp_push_ds.Direction
+_dsp_push_day = datetime(2026, 11, 10, tzinfo=UTC).date()
+_dsp_push_l = _dsp_push_ds.DutySwitchLearner({
+    "dhw_space": _dsp_push_d(k=3.0, kept_w=1.0, first_day=_dsp_push_day, last_day=_dsp_push_day,
+                             usable=True, off_s=[400.0, 501.0, 620.0, 700.0]),
+    "space_dhw": _dsp_push_d(k=2.0, kept_w=2.0, first_day=_dsp_push_day, last_day=_dsp_push_day, usable=True),
+})
+_dsp_cfg_never, _dsp_cfg_read, _dsp_cfg_hub = _dsp_pushed(_dsp_push_l)
+R.check(
+    "the coordinator passes the learner's read to the solve's configuration "
+    "copy: zeros on a pump never arbitrated, both pairs once latched, and the "
+    "configured hub keeps its zeros",
+    (_dsp_cfg_never.duty_switch_stop_probability, _dsp_cfg_never.duty_switch_off_seconds)
+    == ((0.0, 0.0), (0.0, 0.0))
+    and (_dsp_cfg_read.duty_switch_stop_probability, _dsp_cfg_read.duty_switch_off_seconds)
+    == ((0.75, 0.5), (560.5, 0.0))
+    and _dsp_cfg_hub.duty_switch_stop_probability == (0.0, 0.0)
+    and _dsp_cfg_hub.duty_switch_off_seconds == (0.0, 0.0),
+    f"never {_dsp_cfg_never.duty_switch_stop_probability}, read "
+    f"{_dsp_cfg_read.duty_switch_stop_probability} {_dsp_cfg_read.duty_switch_off_seconds}",
+)
+
 _svc_sim_hass = FakeHass()
 _seed_prices(_svc_sim_hass)  # #924
 _svc_sim_entry = FakeEntry(data=_LC_DATA, entry_id="sim_pump")
@@ -63878,13 +63917,17 @@ def _pa_restored_twice(via):
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
@@ -83626,7 +83669,8 @@ from harness import FakeCoordinator as _DsFakeCoord, FakeEntry as _DsFakeEntry
 R.section("duty-switch restart learning, part A (design duty-switch-restart-learning)")
 # A hot water -> heating mode write while the compressor runs stops it on some
 # pumps (Bankaifan, pull request 3420). Part A observes, estimates, persists
-# and publishes; nothing reads the estimate. The learner is driven directly
+# and publishes; the planner's read of it is R10-DUTY-SWITCH-PLANNER-PRICE's
+# section. The learner is driven directly
 # with the install's own table, then through ``pump_arbiter.apply`` and the
 # listener ``duty_switch`` arms.
 _DS_T0 = datetime(2026, 1, 10, 0, 0, tzinfo=UTC)
@@ -84694,8 +84738,11 @@ R.check(
     and all(calls != [] for calls, _split in _ds_flat_runs[0]),
     f"{[split for _c, split in _ds_flat_runs[0]]} {[split for _c, split in _ds_flat_runs[1]]}",
 )
-# Both controls hold by construction: only the arbiter (which reports) and the
-# sensor (which publishes) name the module, and neither reads the estimate.
+# Both controls hold by construction: the arbiter (which reports) and the
+# sensor (which publishes) never read the estimate. Its one reader is the
+# coordinator, which hands the planner's read to a solve's configuration
+# (R10-DUTY-SWITCH-PLANNER-PRICE): the estimate reaches a write only through
+# the plan, and both controls hold the plan fixed.
 _ds_pkg = _DsPath("custom_components/heatpump_optimizer")
 _ds_readers = sorted(
     p.name for p in _ds_pkg.glob("*.py") if p.name != "duty_switch.py" and any(
@@ -84704,19 +84751,23 @@ _ds_readers = sorted(
 _ds_uses = sorted({
     n.attr for name in ("pump_arbiter.py", "sensor.py") for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / name).read_text()))
     if isinstance(n, _ds_ast.Attribute) and isinstance(n.value, _ds_ast.Name) and n.value.id == "duty_switch"})
+_ds_plan_uses = sorted(
+    n.attr for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "coordinator.py").read_text()))
+    if isinstance(n, _ds_ast.Attribute) and isinstance(n.value, _ds_ast.Name) and n.value.id == "duty_switch")
 _ds_own = {n.module for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "duty_switch.py").read_text()))
            if isinstance(n, _ds_ast.ImportFrom) and n.level == 1} | {
     a.name for n in _ds_ast.walk(_ds_ast.parse((_ds_pkg / "duty_switch.py").read_text()))
     if isinstance(n, _ds_ast.ImportFrom) and n.level == 1 and n.module is None for a in n.names}
 R.check(
-    "only the arbiter and the sensor name duty_switch, through its report, attach and publish calls and "
-    "never a read of the estimate; the module imports neither of them; the pure half of wear stays pure",
-    _ds_readers == ["pump_arbiter.py", "sensor.py"]
+    "the arbiter and the sensor name duty_switch through its report, attach and publish calls and never a "
+    "read of the estimate; the coordinator names it once, for the planner's read; the module imports none "
+    "of the three; the pure half of wear stays pure",
+    _ds_readers == ["coordinator.py", "pump_arbiter.py", "sensor.py"] and _ds_plan_uses == ["planner_fields"]
     and _ds_uses == ["Reader", "STOP_WINDOW_S", "SwitchContext", "attach", "detach", "note_mode_write", "note_pass", "record_for",
                      "starts_attributes"]
     and not _ds_own & {"pump_arbiter", "sensor", "coordinator"}
     and "homeassistant" not in (_ds_pkg / "wear.py").read_text(),
-    f"{_ds_readers} {_ds_uses} {_ds_own}",
+    f"{_ds_readers} {_ds_uses} {_ds_plan_uses} {_ds_own}",
 )
 # Published on the compressor-starts sensor, beside the counter, off the payload.
 from heatpump_optimizer import sensor as _ds_sensor  # noqa: E402
@@ -87203,6 +87254,154 @@ R.check(
 )
 
 
+# --- R10-SAV-VALUATION-RESIDUE: the reference held where its valve curve can hold it ---
+from profiles import house as _svh_house  # noqa: E402
+from heatpump_optimizer.optimizer import _thermostat_held_state as _svh_held  # noqa: E402
+from heatpump_optimizer.thermal_model import WeatherSeries as _SVH_WS  # noqa: E402
+
+_SVH_VALVE = {"mixing_valve_mode": "manual", "mixing_valve_target": 21.0,
+              "buffer_tank_volume": 750.0, "buffer_max_temperature": 56.0,
+              "heat_pump_max_power": 4.0}
+
+
+def _svh_case(two_zone, outdoor, **over):
+    """The held state, the stored-heat change of its first reference step, the step's room."""
+    p = _SVR_PARAMS.from_config(_svh_house(two_zone=two_zone, dhw=False, **{**_SVH_VALVE, **over}))
+    model = _SVR_MODEL(p)
+    opt = _SVR_OPT(model, _SVR_CFG(horizon_hours=1, time_step_minutes=15, target_temp=21.0))
+    w = _SVH_WS(outdoor_temps=np.array([outdoor]), wind_speeds=np.zeros(1),
+                precipitation=np.zeros(1), solar_radiation=np.zeros(1))
+    start = _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=outdoor,
+                       upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+                       buffer_tank_temperature=30.0)
+    held = _svh_held(model, start, w, 21.0)
+    # A one-step horizon books the simulated step itself (nothing to apportion).
+    power = float(opt._compute_baseline_power(w, start, 0.25)[0][0])
+    nxt = model.simulate_step(held, power, outdoor, 0.0, 0.0, 0.0, 0.25)
+    return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), nxt
+
+
+# -10 and -15 C sag far; at 14 C the two-zone house falls just short of the
+# target (a shortfall under 1 kW) and at 16 C holds it on a need under 1 kW.
+_svh_rows = {(tz, t): _svh_case(tz, t) for tz in (True, False) for t in (-10.0, -15.0, 14.0, 16.0)}
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: behind a valve whose curve cannot hold the "
+    "setpoint, the thermostat reference starts where that curve holds the "
+    "house -- its first booked step draws no stored heat (the held 21 C "
+    "drew it every step, booked as unpaid reference heat); both zonings, "
+    "from a deep shortfall to a mild day the curve holds",
+    all(abs(ds) < 0.02 for h, ds, _ in _svh_rows.values())
+    and all(_svh_rows[(tz, t)][0].room_temperature < 21.0 - 0.1
+            for tz in (True, False) for t in (-10.0, -15.0)),
+    {k: (round(h.room_temperature, 3), round(ds, 4)) for k, (h, ds, _) in _svh_rows.items()},
+)
+# Null control: a curve that holds the setpoint keeps the held state at target.
+_svh_ok = {tz: _svh_case(tz, -10.0, mixing_valve_target=40.0) for tz in (True, False)}
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: null control -- a valve curve able to hold "
+    "the setpoint leaves the held state's zones at the target",
+    all(h.room_temperature == 21.0 and h.upper_floor_temperature == 21.0
+        and h.lower_floor_temperature == 21.0 for h, _, _ in _svh_ok.values()),
+    {tz: round(h.room_temperature, 4) for tz, (h, _, _) in _svh_ok.items()},
+)
+
+# The pump's capacity is the held state's other bound, valved or not: at -25 C
+# a 4 kW pump cannot hold 21 C (the held 21 C drew ~1.07 kWh_th of stored
+# heat per booked step), a 9 kW one can.
+_SVH_CAP = {"buffer_tank_volume": 750.0, "buffer_max_temperature": 56.0}
+
+
+def _svh_cap(two_zone, valved, hp):
+    cfg = {**_SVH_CAP, "heat_pump_max_power": hp}
+    if valved:
+        cfg.update(mixing_valve_mode="manual", mixing_valve_target=40.0)
+    p = _SVR_PARAMS.from_config(_svh_house(two_zone=two_zone, dhw=False, **cfg))
+    model = _SVR_MODEL(p)
+    opt = _SVR_OPT(model, _SVR_CFG(horizon_hours=1, time_step_minutes=15, target_temp=21.0))
+    w = _SVH_WS(outdoor_temps=np.array([-25.0]), wind_speeds=np.zeros(1),
+                precipitation=np.zeros(1), solar_radiation=np.zeros(1),
+                humidity=np.array([85.0]))
+    start = _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=-25.0,
+                       upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+                       buffer_tank_temperature=30.0)
+    held = _svh_held(model, start, w, 21.0)
+    power = float(opt._compute_baseline_power(w, start, 0.25)[0][0])
+    nxt = model.simulate_step(held, power, -25.0, 0.0, 0.0, 0.0, 0.25)
+    return held, opt._stored_thermal_energy(nxt) - opt._stored_thermal_energy(held), power
+
+
+_svh_caps = {(tz, v, hp): _svh_cap(tz, v, hp)
+             for tz in (True, False) for v in (True, False) for hp in (4.0, 9.0)}
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: a pump too small to hold the setpoint starts "
+    "the reference where its capacity holds the house, valved or not -- the "
+    "first booked step runs at max power and draws no stored heat",
+    all(abs(ds) < 0.02 for h, ds, _ in _svh_caps.values())
+    and all(_svh_caps[(tz, v, 4.0)][0].room_temperature < 21.0 - 0.1
+            for tz in (True, False) for v in (True, False)),
+    {k: (round(h.room_temperature, 3), round(ds, 4), round(pw, 3))
+     for k, (h, ds, pw) in _svh_caps.items()},
+)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: null control -- a pump able to hold the "
+    "setpoint leaves the held state's zones at the target, valved or not",
+    all(_svh_caps[(tz, v, 9.0)][0].room_temperature == 21.0
+        for tz in (True, False) for v in (True, False)),
+    {k: round(h.room_temperature, 4) for k, (h, _, _) in _svh_caps.items() if k[2] == 9.0},
+)
+
+# A warm day under a pump too small for the tank's standing loss: unreachable
+# needs no zone heat there, so the held zones stay at the target, never above.
+_svh_warm_p = _SVR_PARAMS.from_config(_svh_house(
+    two_zone=True, dhw=False, buffer_tank_volume=2000.0, heat_pump_max_power=0.01))
+_svh_warm = _svh_held(
+    _SVR_MODEL(_svh_warm_p),
+    _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=25.0,
+               upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+               buffer_tank_temperature=80.0),
+    _SVH_WS(outdoor_temps=np.array([25.0]), wind_speeds=np.zeros(1),
+            precipitation=np.zeros(1), solar_radiation=np.zeros(1)), 21.0)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: outdoors above the target, a pump unable to "
+    "cover the tank's standing loss leaves the held zones at the target, not "
+    "at the outdoor temperature",
+    _svh_warm.room_temperature == 21.0,
+    round(_svh_warm.room_temperature, 4),
+)
+
+# The reference has no wood: a modelled wood tank is emptied in the held state.
+_svh_wood_p = _SVR_PARAMS.from_config(_svh_house(
+    two_zone=True, dhw=False, wood_tank_top_entity="sensor.w", **_SVH_VALVE))
+_svh_wood = _svh_held(
+    _SVR_MODEL(_svh_wood_p),
+    _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=-10.0,
+               upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+               buffer_tank_temperature=30.0, wood_tank_temperature=80.0),
+    _SVH_WS(outdoor_temps=np.array([-10.0]), wind_speeds=np.zeros(1),
+            precipitation=np.zeros(1), solar_radiation=np.zeros(1)), 21.0)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: a modelled wood tank holds no heat in the "
+    "thermostat reference's held state, whatever was measured in it",
+    _svh_wood_p.two_tank_modelled and _svh_wood.wood_tank_temperature == 0.0,
+    (_svh_wood_p.two_tank_modelled, _svh_wood.wood_tank_temperature),
+)
+
+# At zero demand (a warm day, two zones: each zone's need floors at exactly
+# 0.0) the valve-held tank keeps its measured temperature.
+_svh_idle = _svh_held(
+    _SVR_MODEL(_SVR_PARAMS.from_config(_svh_house(two_zone=True, dhw=False, **_SVH_VALVE))),
+    _SVR_STATE(room_temperature=20.5, slab_temperature=22.0, outdoor_temperature=25.0,
+               upper_floor_temperature=20.5, lower_floor_temperature=20.5,
+               buffer_tank_temperature=30.0),
+    _SVH_WS(outdoor_temps=np.array([25.0]), wind_speeds=np.zeros(1),
+            precipitation=np.zeros(1), solar_radiation=np.zeros(1)), 21.0)
+R.check(
+    "R10-SAV-VALUATION-RESIDUE: behind a valve at zero demand the held tank "
+    "keeps its measured temperature and the zones the target",
+    _svh_idle.buffer_tank_temperature == 30.0 and _svh_idle.room_temperature == 21.0,
+    (_svh_idle.buffer_tank_temperature, _svh_idle.room_temperature),
+)
+
 # --- R10-WATER-SETPOINT-FEEDBACK (outside report #3380, adopted by design
 # note design/R10-WATER-SETPOINT-FEEDBACK at 1442f906, approved d3623f5b):
 # a water set-point under Pump duty control was inlet + lift, re-anchored on
@@ -88305,4 +88504,1459 @@ R.check(
     "a plausible target raised a notice",
 )
 
+R.section(
+    "R10-DUTY-SWITCH-PLANNER-PRICE: the planner prices a duty switch that stops "
+    "the compressor (pull request 3420, Bankaifan)"
+)
+
+from types import SimpleNamespace as _DspNS  # noqa: E402
+
+import heatpump_optimizer.optimizer as _dsp_om  # noqa: E402
+from heatpump_optimizer import duty_legs as _dsp_dl, pump_arbiter as _dsp_pa  # noqa: E402
+from heatpump_optimizer.const import MODE_AUTO as _DSP_AUTO  # noqa: E402
+from heatpump_optimizer.dhw_planner import DhwPlanner as _DspPlanner  # noqa: E402
+from heatpump_optimizer.optimizer import (  # noqa: E402
+    HeatPumpOptimizer as _DspOpt,
+    OptimizationConfig as _DspCfg,
+    count_compressor_starts as _dsp_starts,
+    cycling_penalty as _dsp_cyc,
+)
+from heatpump_optimizer.thermal_model import (  # noqa: E402
+    ThermalModel as _DspTM,
+    ThermalParameters as _DspTP,
+    ThermalState as _DspTS,
+)
+
+_DSP_T0 = datetime(2026, 1, 10, 6, 0, tzinfo=UTC)
+_DSP_STEPS = np.arange(96)
+_DSP_PRICES = 1.3 + 0.9 * np.sin(2 * np.pi * (_DSP_STEPS - 30) / 96.0)
+#: Bankaifan's table: every hot water to heating switch stopped the compressor,
+#: none the other way, median off time 501 s (8.2 and 8.5 minutes).
+_DSP_PAIR, _DSP_OFF = (1.0, 0.0), (501.0, 0.0)
+
+
+def _dsp_w(space, dhw, pair, floor=None, p_max=6.0):
+    return _dsp_dl.switch_weight(
+        np.asarray(space, float), np.asarray(dhw, float), pair, p_max, floor
+    )
+
+
+# 1. The finding. Equal draw on both sides of the switch: the cycling term
+# sees no swing; the switch weight is p x draw / p_max.
+R.check(
+    "a hot-water step into a heating step at equal draw costs the cycling term "
+    "nothing and weighs p x draw / p_max as a switch",
+    _dsp_cyc(np.array([3.0, 3.0]), 2.0, 6.0) == 0.0
+    and _dsp_w([0, 3], [3, 0], (0.8, 0.0)) == 0.8 * 3.0 / 6.0,
+    f"{_dsp_cyc(np.array([3.0, 3.0]), 2.0, 6.0)}, {_dsp_w([0, 3], [3, 0], (0.8, 0.0))}",
+)
+R.check(
+    "the stop adds the smaller of the two levels across a boundary",
+    _dsp_w([0, 2], [3, 0], (0.8, 0.0)) == 0.8 * 2.0 / 6.0
+    and _dsp_w([0, 3], [2, 0], (0.8, 0.0)) == 0.8 * 2.0 / 6.0,
+)
+R.check(
+    "an idle step between the two duties is no switch",
+    _dsp_w([0, 0, 3], [3, 0, 0], (0.8, 0.6)) == 0.0,
+)
+R.check(
+    "the reverse order is the other direction: unpriced with a zero there, "
+    "priced by its own probability",
+    _dsp_w([3, 0], [0, 3], (0.8, 0.0)) == 0.0
+    and _dsp_w([3, 0], [0, 3], (0.8, 0.6)) == 0.6 * 3.0 / 6.0,
+)
+R.check(
+    "a two-leg both step alone weighs p x (space + dhw) / p_max: both legs run "
+    "at the step's combined level",
+    _dsp_w([2], [2], (0.8, 0.0)) == 0.8 * 4.0 / 6.0,
+    f"{_dsp_w([2], [2], (0.8, 0.0))}",
+)
+R.check(
+    "a both step followed by heating is one switch, not two: its last leg is "
+    "already heating",
+    _dsp_w([2, 3], [2, 0], (0.8, 0.0)) == 0.8 * 4.0 / 6.0,
+)
+R.check(
+    "null control: a zero pair weighs every one of those plans zero",
+    all(
+        _dsp_w(s, d, (0.0, 0.0)) == 0.0
+        for s, d in (([0, 3], [3, 0]), ([2], [2]), ([3, 0], [0, 3]))
+    ),
+)
+
+
+def _dsp_opt(pair=(0.0, 0.0), off=(0.0, 0.0), *, clamp=False, p_min=1.5, p_max=5.5, cyc=0.3):
+    params = _DspTP()
+    params.mixing_valve_mode = "none"
+    params.buffer_tank_volume = 750.0
+    params.min_electrical_power, params.max_electrical_power = p_min, p_max
+    params.dhw_enabled = True
+    cfg = _DspCfg(clamp_planned_levels=clamp, cycling_cost=cyc)
+    if pair is not None:
+        cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = pair, off
+    return _DspOpt(_DspTM(params), cfg)
+
+
+_dsp_term_opt = _dsp_opt((0.8, 0.0), cyc=2.0, p_max=6.0)
+_dsp_term = _dsp_om._switch_cost_fn(_dsp_term_opt)
+_dsp_term_pair = (np.array([0.0, 3.0]), np.array([3.0, 0.0]))
+R.check(
+    "the objective's term is cycling_cost x that weight, a float for one plan "
+    "and one entry per row for a batch",
+    _dsp_term(*_dsp_term_pair) == 2.0 * (0.8 * 3.0 / 6.0)
+    and _dsp_term(np.stack([_dsp_term_pair[0]] * 2), _dsp_term_pair[1]).tolist()
+    == [2.0 * (0.8 * 3.0 / 6.0)] * 2,
+    f"{_dsp_term(*_dsp_term_pair)}",
+)
+R.check(
+    "and it is no operand at all with a zero pair, a zero cycling cost or no "
+    "hot-water plan",
+    _dsp_om._switch_cost_fn(_dsp_opt((0.0, 0.0), cyc=2.0))(*_dsp_term_pair) is None
+    and _dsp_om._switch_cost_fn(_dsp_opt((0.8, 0.0), cyc=0.0))(*_dsp_term_pair) is None
+    and _dsp_term(_dsp_term_pair[0], None) is None
+    and _dsp_om._with_switch_cost(1.25, None) == 1.25,
+)
+R.check(
+    "a non-finite, negative, over-one or misshapen learned pair reads as zero",
+    [
+        _dsp_dl.priced_pair(v, 1.0)
+        for v in ((float("nan"), 0.5), (-0.1, 1.5), (0.4,), None, ("x", 0.2), (1.0, 0.0))
+    ]
+    == [(0.0, 0.5), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1.0, 0.0)]
+    and _dsp_dl.priced_pair((float("inf"), 30.0)) == (0.0, 30.0),
+)
+
+# 2. Leg-rule agreement: drive step_duty, then _share, and compare what the
+# arbiter serves with the legs the leaf reads from the same two draws.
+_DSP_NAMES = {_dsp_dl.IDLE: "idle", _dsp_dl.SPACE: "space", _dsp_dl.DHW: "dhw"}
+
+
+class _DspCoord:
+    """A coordinator with no boost held: ``_share`` reads nothing else of it."""
+
+
+_dsp_coord = _DspCoord()
+
+
+def _dsp_served(space, dhw, minute, floor):
+    plan = _DspNS(
+        timestamps=[_DSP_T0], power_schedule=[space], dhw_power_schedule=[dhw],
+        optimal_setpoints=[21.0], duty_floor_kw=floor,
+    )
+    now = _DSP_T0 + timedelta(minutes=minute)
+    inp = _DspNS(mode=_DSP_AUTO, disinfecting=False, plan=plan)
+    return _dsp_pa._share(_dsp_coord, inp, _dsp_pa.step_duty(plan, now), now)
+
+
+def _dsp_leg_mismatches(cells, floor):
+    """Cells where the arbiter's serving is not the leaf's legs, and the two-leg count."""
+    bad, two_leg = [], 0
+    for space, dhw in cells:
+        first, last, two = (v[0] for v in _dsp_dl.leg_ends([space], [dhw], floor))
+        served = [_dsp_served(space, dhw, m, floor) for m in (0.0, 4.9, 5.1, 7.4, 9.9, 10.1, 14.9)]
+        two_leg += int(two)
+        ends = (_DSP_NAMES[int(first)], _DSP_NAMES[int(last)])
+        if (
+            (served[0], served[-1]) != ends
+            or not set(served) <= set(ends)
+            or (len(set(served)) == 2) != bool(two)
+        ):
+            bad.append((space, dhw, floor, served, ends, bool(two)))
+    return bad, two_leg
+
+
+_DSP_LEVELS = (0.0, 0.05, 0.1, 0.11, 0.5, 1.0, 1.49, 1.5, 2.0, 3.0, 4.0, 5.5)
+_DSP_CELLS = [(s, d) for s in _DSP_LEVELS for d in _DSP_LEVELS]
+_dsp_grid = {floor: _dsp_leg_mismatches(_DSP_CELLS, floor) for floor in (None, 1.5)}
+R.check(
+    "the leaf's legs are what step_duty and _share serve over the probe grid, "
+    "floor unset and set: idle, one duty, both collapse edges and two legs",
+    not _dsp_grid[None][0] and not _dsp_grid[1.5][0],
+    f"{_dsp_grid[None][0][:3]} {_dsp_grid[1.5][0][:3]}",
+)
+R.check(
+    "and the grid holds what it claims: two-leg cells under both floors, fewer "
+    "with the floor set, and both exact collapse edges (shares of 5 and 10 minutes)",
+    _dsp_grid[None][1] > _dsp_grid[1.5][1] > 0
+    and (2.0, 1.0) in _DSP_CELLS and (1.0, 2.0) in _DSP_CELLS
+    and [bool(_dsp_dl.leg_ends([s], [d])[2][0]) for s, d in ((2.0, 1.0), (1.0, 2.0), (2.0, 0.5), (0.5, 2.0))]
+    == [True, True, False, False],
+    f"{_dsp_grid[None][1]}, {_dsp_grid[1.5][1]}",
+)
+
+
+def _dsp_realised_cells(p_min, p_max):
+    out = []
+    for space, dhw in _DSP_CELLS:
+        s, d = _dsp_om._realize_joint(True, np.array([space]), np.array([dhw]), p_min, p_max)
+        out.append((float(s[0]), float(d[0])))
+    return out
+
+
+_dsp_mod_cells = _dsp_realised_cells(1.5, 5.5)
+_dsp_fix_cells = _dsp_realised_cells(5.5, 5.5)
+_dsp_mod_grid = _dsp_leg_mismatches(_dsp_mod_cells, 1.5)
+_dsp_fix_grid = _dsp_leg_mismatches(_dsp_fix_cells, 5.5)
+R.check(
+    "the same agreement on the levels a clamped install ships: a modulating "
+    "pump keeps two-leg steps, each circuit at or above p_min",
+    not _dsp_mod_grid[0] and _dsp_mod_grid[1] > 0,
+    f"{_dsp_mod_grid[0][:3]}, two-leg {_dsp_mod_grid[1]}",
+)
+R.check(
+    "and on a fixed-speed pump the leaf never returns two legs, while the row "
+    "still holds heating-only and hot-water-only steps",
+    not _dsp_fix_grid[0] and _dsp_fix_grid[1] == 0
+    and {(5.5, 0.0), (0.0, 5.5)} <= set(_dsp_fix_cells),
+    f"{_dsp_fix_grid[0][:3]}, two-leg {_dsp_fix_grid[1]}",
+)
+
+# 3. Scalar against batch, bit for bit per row, the way the cycling term is pinned.
+_dsp_rng = np.random.default_rng(3420)
+_dsp_rows = _dsp_rng.uniform(0.0, 5.5, size=(64, 96))
+_dsp_rows[_dsp_rng.uniform(size=_dsp_rows.shape) < 0.35] = 0.0
+_dsp_tank = np.zeros(96)
+_dsp_tank[[5, 6, 20, 40, 41, 42, 70, 95]] = (4.4, 4.4, 2.0, 1.2, 4.4, 0.6, 3.0, 4.4)
+_dsp_batch_w = {
+    floor: _dsp_dl.switch_weights_batch(_dsp_rows, _dsp_tank, (0.7, 0.4), 5.5, floor)
+    for floor in (None, 1.5)
+}
+_dsp_row_bad = [
+    (floor, b)
+    for floor in (None, 1.5)
+    for b in range(_dsp_rows.shape[0])
+    if _dsp_batch_w[floor][b] != _dsp_dl.switch_weight(_dsp_rows[b], _dsp_tank, (0.7, 0.4), 5.5, floor)
+]
+R.check(
+    "switch_weights_batch is switch_weight on every row, bit for bit, floor "
+    "unset and set",
+    not _dsp_row_bad and len(set(_dsp_batch_w[None].tolist())) > 32,
+    f"divergent rows: {_dsp_row_bad[:5]}",
+)
+_dsp_no_pmax = _dsp_dl.switch_weights_batch(_dsp_rows, _dsp_tank, (0.7, 0.4), 0.0)
+R.check(
+    "a pump with no maximum draw weighs every row zero, one finite entry per "
+    "row and not per step, on the rows the priced pair weighs above",
+    _dsp_no_pmax.shape == (_dsp_rows.shape[0],)
+    and _dsp_rows.shape[0] != _dsp_rows.shape[1]
+    and not _dsp_no_pmax.any()
+    and bool(_dsp_batch_w[None].any()),
+    f"shape {_dsp_no_pmax.shape}",
+)
+
+# Availability: one step charged per block end, on the profile the solve starts from.
+_dsp_blk = np.array([0.0, 3.0, 3.0, 0.0, 0.0, 0.0])
+
+
+def _dsp_charged(start, lost=0.5, floor=None, tank=_dsp_blk):
+    avail = _dsp_dl.availability(np.asarray(start, float), tank, lost, floor)
+    return None if avail is None else (np.flatnonzero(avail < 1.0).tolist(), sorted(set(avail.tolist())))
+
+
+R.check(
+    "a block end charges one step, the one holding the heating leg that "
+    "follows it: the step after the block when heating starts there, not the "
+    "block's last",
+    _dsp_charged([1, 0, 0, 2, 2, 0]) == ([3], [0.5, 1.0]),
+    f"{_dsp_charged([1, 0, 0, 2, 2, 0])}",
+)
+R.check(
+    "the block's own last step when it is a two-leg step, and then not the "
+    "step after",
+    _dsp_charged([0, 0, 2, 2, 0, 0]) == ([2], [0.5, 1.0]),
+    f"{_dsp_charged([0, 0, 2, 2, 0, 0])}",
+)
+R.check(
+    "no vector at all with a zero lost share, with an idle step after the "
+    "block, or with no hot water: the caller makes today's calls",
+    _dsp_charged([1, 0, 0, 2, 2, 0], lost=0.0) is None
+    and _dsp_charged([1, 0, 0, 0, 2, 0]) is None
+    and _dsp_charged([1, 1, 1, 1, 1, 1], tank=np.zeros(6)) is None,
+)
+R.check(
+    "the lost share is p x off seconds over the step, capped at the whole "
+    "step, and only hot water to heating carries one",
+    _dsp_dl.lost_share((1.0, 0.0), (501.0, 0.0)) == 501.0 / 900.0
+    and _dsp_dl.lost_share((0.5, 1.0), (501.0, 900.0)) == 0.5 * 501.0 / 900.0
+    and _dsp_dl.lost_share((1.0, 0.0), (5000.0, 0.0)) == 1.0
+    and _dsp_dl.lost_share((0.0, 1.0), (0.0, 501.0)) == 0.0,
+)
+R.check(
+    "a duty-cycle install carries the lost time on the bound, a clamped one on "
+    "the delivered draw, and neither moves anything with no vector",
+    _dsp_dl.space_headroom(6.0, _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), None).tolist()
+    == [6.0, 3.0, 3.0, 3.0, 6.0, 6.0]
+    and _dsp_dl.space_headroom(6.0, _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), 6.0).tolist()
+    == _dsp_dl.space_headroom(6.0, _dsp_blk, None, None).tolist()
+    == [6.0, 3.0, 3.0, 6.0, 6.0, 6.0]
+    and _dsp_dl.delivered_space(
+        np.array([0, 0, 0, 6.0, 6.0, 0]), _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), 6.0
+    ).tolist() == [0.0, 0.0, 0.0, 3.0, 6.0, 0.0],
+)
+_dsp_same = np.array([0, 0, 0, 6.0, 6.0, 0])
+R.check(
+    "on a duty-cycle install the delivered draw is the shipped array itself",
+    _dsp_dl.delivered_space(_dsp_same, _dsp_blk, np.array([1, 1, 1, 0.5, 1, 1.0]), None)
+    is _dsp_same,
+)
+R.check(
+    "in a charged two-leg step the stop takes its share of the combined level "
+    "from the heating draw, and never below zero",
+    _dsp_dl.delivered_space(
+        np.array([2.0, 0.5]), np.array([2.0, 4.0]), np.array([0.75, 0.5]), 1.5
+    ).tolist() == [1.0, 0.0],
+)
+# Item r16: on a modulating clamped install the charged step is chosen on the
+# levels the start profile ships, so it never holds a heating level under p_min.
+_dsp_mod_opt = _dsp_opt(_DSP_PAIR, _DSP_OFF, clamp=True)
+_dsp_r16_tank = np.zeros(8)
+_dsp_r16_tank[[1, 4]] = 4.4
+_dsp_r16_start = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 3.0, 3.0, 0.0])
+_dsp_r16_avail = _dsp_om._stop_availability(_dsp_mod_opt, _dsp_r16_start, _dsp_r16_tank, 5.5)
+_dsp_r16_ship = _dsp_om._realize_joint(True, _dsp_r16_start, _dsp_r16_tank, 1.5, 5.5)[0]
+R.check(
+    "on a modulating clamped install no charged step ships heating under the "
+    "floor: a start under p_min after a block is charged only once it ships at "
+    "p_min or above",
+    _dsp_r16_avail is not None
+    and bool(np.all(_dsp_r16_ship[_dsp_r16_avail < 1.0] >= 1.5))
+    and np.flatnonzero(_dsp_r16_avail < 1.0).tolist()
+    == [i for i in (2, 5) if _dsp_r16_ship[i] >= 1.5],
+    f"{_dsp_r16_avail}, shipped {_dsp_r16_ship}",
+)
+# The same item on a both step: heating shipped under p_min beside hot water is
+# no leg the arbiter serves, so the stop belongs to the heating step after it.
+_dsp_r16_both = (np.array([0.0, 1.0, 2.5, 0.0]), np.array([0.0, 2.0, 0.0, 0.0]))
+_dsp_r16_both_avail = _dsp_om._stop_availability(_dsp_mod_opt, *_dsp_r16_both, 5.5)
+_dsp_r16_both_ship = _dsp_om._realize_joint(True, *_dsp_r16_both, 1.5, 5.5)[0]
+_dsp_r16_both_dc = _dsp_om._stop_availability(_dsp_opt(_DSP_PAIR, _DSP_OFF), *_dsp_r16_both, 5.5)
+R.check(
+    "on a modulating clamped install heating shipped under p_min beside hot "
+    "water takes no charge: the stop is charged to the heating step after the "
+    "both step, and no charged step ships heating under the floor",
+    _dsp_r16_both_ship.tolist() == [0.0, 1.0, 2.5, 0.0]
+    and _dsp_r16_both_avail is not None
+    and np.flatnonzero(_dsp_r16_both_avail < 1.0).tolist() == [2]
+    and bool(np.all(_dsp_r16_both_ship[_dsp_r16_both_avail < 1.0] >= 1.5)),
+    f"{_dsp_r16_both_avail}, shipped {_dsp_r16_both_ship}",
+)
+R.check(
+    "null control: with no duty floor (a duty-cycle install) the same arrays "
+    "charge the both step itself, so the floor is what moved the charge",
+    _dsp_r16_both_dc is not None
+    and np.flatnonzero(_dsp_r16_both_dc < 1.0).tolist() == [1],
+    f"{_dsp_r16_both_dc}",
+)
+# The start profile is capped at what hot water leaves and never raised: a step
+# the start leaves idle after a block holds no heating leg to charge.
+_dsp_idle_after = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 0.0, -0.4, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]), 5.5
+)
+_dsp_run_after = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 0.0, 2.0, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]), 5.5
+)
+R.check(
+    "a start that is idle, or below zero, in the step after a block charges "
+    "nothing; the same block followed by heating charges that step",
+    _dsp_idle_after is None
+    and _dsp_run_after is not None and np.flatnonzero(_dsp_run_after < 1.0).tolist() == [2],
+    f"{_dsp_idle_after}, {_dsp_run_after}",
+)
+# The cap is the reading's own: a start that asks for heating beside hot water
+# at p_max ships none there, so that step holds no heating leg and the idle step
+# after it charges nothing. Beside a block that leaves room the same start is a
+# two-leg step, and charged.
+_dsp_full_blk = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 3.0, 0.0, 0.0]), np.array([0.0, 5.5, 0.0, 0.0]), 5.5
+)
+_dsp_part_blk = _dsp_om._stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 3.0, 0.0, 0.0]), np.array([0.0, 2.5, 0.0, 0.0]), 5.5
+)
+R.check(
+    "heating asked beside hot water at p_max is no heating leg: nothing is "
+    "charged; beside a block that leaves room the same start is charged there",
+    _dsp_full_blk is None
+    and _dsp_part_blk is not None and np.flatnonzero(_dsp_part_blk < 1.0).tolist() == [1],
+    f"{_dsp_full_blk}, {_dsp_part_blk}",
+)
+# The reading takes the start as it comes: the cap, the running threshold and
+# the clamped projection already read a value under zero as idle and one over
+# p_max as the cap, so clipping the start into [0, p_max] first moves no step
+# of it, on either install kind. The grid holds starts outside the band, and
+# blocks that charge a step, or the comparison would be of nothing.
+import itertools as _dsp_it  # noqa: E402
+
+_DSP_BAND_STARTS = [np.array(s) for s in _dsp_it.product((-0.4, 0.0, 1.0, 3.0, 9.0), repeat=4)]
+_DSP_BAND_TANKS = [np.array(t) for t in ((0.0, 2.5, 0.0, 0.0), (4.4, 0.0, 5.5, 0.0), (0.0, 0.0, 2.0, 2.0))]
+
+
+def _dsp_band_read(clamp, start, tank):
+    avail = _dsp_om._stop_availability(_dsp_opt(_DSP_PAIR, _DSP_OFF, clamp=clamp), start, tank, 5.5)
+    return None if avail is None else avail.tolist()
+
+
+_dsp_band_rows = [
+    (_dsp_band_read(clamp, start, tank), _dsp_band_read(clamp, np.clip(start, 0.0, 5.5), tank), start)
+    for clamp in (False, True) for tank in _DSP_BAND_TANKS for start in _DSP_BAND_STARTS
+]
+_dsp_band_moved = [(raw, clipped, start.tolist()) for raw, clipped, start in _dsp_band_rows if raw != clipped]
+R.check(
+    "a start outside [0, p_max] reads as the same start clipped into it, on a "
+    "duty-cycle and on a clamped install; the grid holds starts outside the "
+    "band and readings that charge a step",
+    not _dsp_band_moved
+    and any(raw is not None for raw, _, _ in _dsp_band_rows)
+    and any(raw is None for raw, _, _ in _dsp_band_rows)
+    and sum(bool(np.any((start < 0.0) | (start > 5.5))) for _, _, start in _dsp_band_rows) > len(_dsp_band_rows) // 2,
+    f"{len(_dsp_band_moved)} of {len(_dsp_band_rows)} moved, first {_dsp_band_moved[:1]}",
+)
+R.check(
+    "the bound is what hot water leaves and never under zero: 0.5 kW beside "
+    "5.5 of 6, nothing beside 7, with no vector and with one",
+    _dsp_dl.space_headroom(6.0, np.array([5.5, 7.0]), None, None).tolist() == [0.5, 0.0]
+    and _dsp_dl.space_headroom(6.0, np.array([5.5, 7.0]), np.array([1.0, 0.5]), None).tolist()
+    == [0.5, 0.0],
+)
+R.check(
+    "a pump under 1 kW weighs its switch like any other: p x draw / p_max at "
+    "a maximum draw of 0.5 kW",
+    _dsp_dl.switch_weight(np.array([0.0, 0.4]), np.array([0.4, 0.0]), (1.0, 0.0), 0.5) == 0.8,
+)
+
+
+def _dsp_obj_a(*_a, **_k):
+    return 0.0
+
+
+def _dsp_obj_b(*_a, **_k):
+    return np.zeros(1)
+
+
+_dsp_plain_solve = _dsp_om._with_stop_availability(
+    _dsp_opt(None, None), np.array([0.0, 0.0, 2.0, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]),
+    5.5, _dsp_obj_a, _dsp_obj_b,
+)
+_dsp_vector_solve = _dsp_om._with_stop_availability(
+    _dsp_opt(_DSP_PAIR, _DSP_OFF), np.array([0.0, 0.0, 2.0, 2.0]), np.array([0.0, 2.0, 0.0, 0.0]),
+    5.5, _dsp_obj_a, _dsp_obj_b,
+)
+R.check(
+    "with no vector a space solve gets the two objectives it handed in, the "
+    "same objects, and today's bound; with one it gets them bound to the vector",
+    _dsp_plain_solve[1] is _dsp_obj_a and _dsp_plain_solve[2] is _dsp_obj_b
+    and _dsp_plain_solve[0].tolist() == [5.5, 3.5, 5.5, 5.5]
+    and _dsp_vector_solve[1] is not _dsp_obj_a
+    and np.flatnonzero(_dsp_vector_solve[1].keywords["avail"] < 1.0).tolist() == [2]
+    and _dsp_vector_solve[2].keywords["avail"] is _dsp_vector_solve[1].keywords["avail"],
+)
+
+
+def _dsp_solve(pair=(0.0, 0.0), off=(0.0, 0.0), *, pins=None, legionella_h=20.0, **install):
+    """One full ``optimize``; the planner builds, the published simulation's
+    inputs and the objective closures are recorded beside the result."""
+    opt = _dsp_opt(pair, off, **install)
+    seen = _DspNS(
+        builds=[], sims=[], objectives=[], solves=[], solved=[], min_runs=[],
+        energy=[None], vectors=[0], opt=opt,
+    )
+    real_build = _DspPlanner._build_dhw_requirements
+    real_sim, real_objectives = opt.model.simulate_trajectory_with_dhw, opt._solve_objectives
+    real_solve, real_min_run = opt._solve_space, _DspPlanner._apply_dhw_min_run
+
+    real_energy, real_vector = opt._energy_cost_fn, _dsp_om._stop_availability
+
+    def solve_space(*args):
+        seen.solves.append(args)
+        seen.solved.append(real_solve(*args))
+        return seen.solved[-1]
+
+    def energy_cost_fn(*args):
+        cost_of = real_energy(*args)
+
+        def recorded(power):
+            seen.energy[0] = np.array(power, float)
+            return cost_of(power)
+        return recorded
+
+    def vector(*args):
+        seen.vectors[0] += 1
+        return real_vector(*args)
+
+    def min_run(self, **kwargs):
+        out = real_min_run(self, **kwargs)
+        seen.min_runs.append((np.array(kwargs["plan"], float), np.array(out, float)))
+        return out
+
+    def build(self, h, **kwargs):
+        out = real_build(self, h, **kwargs)
+        seen.builds.append((kwargs, out, h, self))
+        return out
+
+    def sim(**kwargs):
+        seen.sims.append(kwargs)
+        return real_sim(**kwargs)
+
+    def objectives(h):
+        out = real_objectives(h)
+        seen.objectives.append(out)
+        return out
+
+    opt.model.simulate_trajectory_with_dhw, opt._solve_objectives = sim, objectives
+    opt._solve_space, opt._energy_cost_fn = solve_space, energy_cost_fn
+    _dsp_om._stop_availability = vector
+    _DspPlanner._build_dhw_requirements = build
+    _DspPlanner._apply_dhw_min_run = min_run
+    outdoor = 2.0 + 3.0 * np.sin(2 * np.pi * (_DSP_STEPS - 50) / 96.0)
+    try:
+        seen.result = opt.optimize(inputs=solve_inputs(
+            initial_state=_DspTS(
+                room_temperature=20.5, upper_floor_temperature=20.5,
+                lower_floor_temperature=20.5, slab_temperature=21.0,
+                outdoor_temperature=float(outdoor[0]),
+                buffer_tank_temperature=30.0, dhw_temperature=45.0,
+                dhw_hours_since_legionella=legionella_h,
+            ),
+            prices=_DSP_PRICES, outdoor_temps=outdoor,
+            start_time=datetime(2026, 1, 10, tzinfo=UTC), dhw_pins=pins,
+        ))
+    finally:
+        _DspPlanner._build_dhw_requirements = real_build
+        _DspPlanner._apply_dhw_min_run = real_min_run
+        _dsp_om._stop_availability = real_vector
+    seen.space = np.asarray(seen.result.power_schedule, float)
+    seen.dhw = np.asarray(seen.result.dhw_power_schedule, float)
+    seen.bans = [k["placement_ban"] for k, *_ in seen.builds if "placement_ban" in k]
+    return seen
+
+
+def _dsp_same_plan(a, b):
+    return (
+        np.array_equal(a.space, b.space) and np.array_equal(a.dhw, b.dhw)
+        and a.result.room_temp_trajectory == b.result.room_temp_trajectory
+        and a.result.objective_value == b.result.objective_value
+        and a.result.predicted_cost == b.result.predicted_cost
+        and a.result.status == b.result.status
+    )
+
+
+_DSP_INSTALLS = {
+    "duty-cycle": dict(clamp=False),
+    "modulating clamped": dict(clamp=True),
+    "fixed-speed": dict(clamp=True, p_min=5.5),
+}
+_dsp_base = {name: _dsp_solve(None, **kw) for name, kw in _DSP_INSTALLS.items()}
+_dsp_priced = {name: _dsp_solve(_DSP_PAIR, _DSP_OFF, **kw) for name, kw in _DSP_INSTALLS.items()}
+
+# 4. Null controls, each a full optimize whose arrays are compared equal with
+# the plan a config that never heard of the fields returns.
+_DSP_NULLS = {
+    "an empty learner (zero pair, no off time)": ((0.0, 0.0), (0.0, 0.0)),
+    "a learner under its on-threshold (zero pair, an off time stored)": ((0.0, 0.0), (501.0, 0.0)),
+    "a learned pair that is not a probability": ((float("nan"), 1.7), (501.0, 501.0)),
+}
+_dsp_null_bad = []
+for _dsp_name, _dsp_kw in _DSP_INSTALLS.items():
+    for _dsp_label, (_dsp_p, _dsp_o) in _DSP_NULLS.items():
+        _dsp_null = _dsp_solve(_dsp_p, _dsp_o, **_dsp_kw)
+        if (
+            not _dsp_same_plan(_dsp_null, _dsp_base[_dsp_name])
+            or _dsp_null.bans or _dsp_null.opt._space_avail is not None
+            or len(_dsp_null.builds) != len(_dsp_base[_dsp_name].builds)
+        ):
+            _dsp_null_bad.append((_dsp_name, _dsp_label))
+R.check(
+    "null controls: an empty learner, one under its threshold and a pair that "
+    "is no probability each leave the plan identical on all three install "
+    "classes, with no availability vector, no banned build and the planner "
+    "called as often",
+    not _dsp_null_bad,
+    f"{_dsp_null_bad}",
+)
+_dsp_free = _dsp_solve(_DSP_PAIR, (0.0, 0.0), cyc=0.0)
+R.check(
+    "null control: a stopping switch with no measured off time on an install "
+    "that prices no cycle moves nothing either",
+    _dsp_same_plan(_dsp_free, _dsp_solve(None, cyc=0.0)) and not _dsp_free.bans,
+)
+R.check(
+    "and the nulls have something to detect: with the contributor's pair the "
+    "plan moves on every install class",
+    all(not _dsp_same_plan(_dsp_priced[n], _dsp_base[n]) for n in _DSP_INSTALLS),
+    f"{[n for n in _DSP_INSTALLS if _dsp_same_plan(_dsp_priced[n], _dsp_base[n])]}",
+)
+
+
+# 5. Acceptance, on the contributor's table.
+def _dsp_plan_weight(seen, name):
+    kw = {"clamp": False, "p_min": 1.5, **_DSP_INSTALLS[name]}
+    return _dsp_dl.switch_weight(
+        seen.space, seen.dhw, _DSP_PAIR, 5.5, kw["p_min"] if kw["clamp"] else None
+    )
+
+
+def _dsp_old_under_new(name):
+    """The unpriced plan's score under the priced solve's own objective."""
+    old, new = _dsp_base[name], _dsp_priced[name]
+    avail = _dsp_om._stop_availability(new.opt, old.space, old.dhw, 5.5)
+    return float(new.objectives[-1][1](old.space, old.dhw, None, avail))
+
+
+_dsp_accept = {
+    name: (
+        _dsp_plan_weight(_dsp_base[name], name), _dsp_plan_weight(_dsp_priced[name], name),
+        _dsp_old_under_new(name), float(_dsp_priced[name].result.objective_value),
+    )
+    for name in ("duty-cycle", "modulating clamped")
+}
+R.check(
+    "acceptance: priced on the contributor's table the plan carries a lower "
+    "summed switch weight, on a duty-cycle and on a modulating clamped install",
+    all(new_w < old_w and old_w > 0 for old_w, new_w, _, _ in _dsp_accept.values()),
+    f"{_dsp_accept}",
+)
+R.check(
+    "at no higher cost under the plan's own objective: the new plan scores no "
+    "higher than the old plan does under the priced objective",
+    all(new_s <= old_s + 1e-9 for _, _, old_s, new_s in _dsp_accept.values()),
+    f"{_dsp_accept}",
+)
+R.check(
+    "the published objective of a priced plan is its closure's value on the "
+    "arrays that ship, with the vector the solve scored with",
+    all(
+        float(s.objectives[-1][1](s.space, s.dhw, None, s.opt._space_avail))
+        == float(s.result.objective_value)
+        for s in _dsp_priced.values()
+    ),
+)
+_dsp_dc = _dsp_priced["duty-cycle"]
+_dsp_dc_avail = _dsp_dc.opt._space_avail
+R.check(
+    "on the duty-cycle install the solved heating in every charged step is at "
+    "most avail x p_max - dhw, and a charged step exists",
+    _dsp_dc_avail is not None and bool(np.any(_dsp_dc_avail < 1.0))
+    and bool(np.all(
+        _dsp_dc.space <= np.maximum(0.0, _dsp_dc_avail * 5.5 - _dsp_dc.dhw) + 1e-9
+    )),
+    f"{None if _dsp_dc_avail is None else np.flatnonzero(_dsp_dc_avail < 1.0).tolist()}",
+)
+R.check(
+    "and there the simulation is fed the shipped schedule itself: the bound "
+    "carried the lost time",
+    np.array_equal(_dsp_dc.sims[-1]["space_power_schedule"], _dsp_dc.space),
+)
+
+# 9. A fixed-speed install: the level cannot carry the lost time.
+_dsp_fx, _dsp_fx0 = _dsp_priced["fixed-speed"], _dsp_base["fixed-speed"]
+_dsp_fx_avail = _dsp_fx.opt._space_avail
+_dsp_fx_charged = [] if _dsp_fx_avail is None else np.flatnonzero(_dsp_fx_avail < 1.0).tolist()
+_dsp_fx_total = _dsp_fx.space + _dsp_fx.dhw
+#: The charged steps the solve kept its heating leg on. Where it moved the leg
+#: off one, that block end's lost time is uncharged (its pair is still
+#: priced): the design's stated residual, at most one step's share per block end.
+_dsp_fx_live = [i for i in _dsp_fx_charged if _dsp_fx.space[i] > 0]
+R.check(
+    "fixed-speed: every shipped total is 0 or p_max and the plan's duty floor "
+    "is p_min, with a hot-water block followed by a charged heating step",
+    bool(np.all((_dsp_fx_total == 0.0) | (_dsp_fx_total == 5.5)))
+    and _dsp_fx.result.duty_floor_kw == 5.5
+    and bool(_dsp_fx_live)
+    and all(_dsp_fx.dhw[i - 1] == 5.5 and _dsp_fx.space[i] == 5.5 for i in _dsp_fx_live),
+    f"charged {_dsp_fx_charged}, live {_dsp_fx_live}",
+)
+R.check(
+    "fixed-speed: step_duty inside a charged step returns space, and the leaf "
+    "weighs the block end into it p x 1 from the result's own schedules and floor",
+    all(
+        _dsp_pa.step_duty(_dsp_fx.result, _dsp_fx.result.timestamps[i] + timedelta(minutes=7))
+        == "space"
+        and _dsp_dl.switch_weight(
+            _dsp_fx.space[i - 1 : i + 1], _dsp_fx.dhw[i - 1 : i + 1], _DSP_PAIR, 5.5,
+            _dsp_fx.result.duty_floor_kw,
+        ) == 1.0
+        for i in _dsp_fx_live
+    ),
+)
+_dsp_fx_sim = _dsp_fx.sims[-1]
+_dsp_fx_fed = np.asarray(_dsp_fx_sim["space_power_schedule"], float)
+_dsp_fx_expect = _dsp_fx.space.copy()
+_dsp_fx_expect[_dsp_fx_live] = (1.0 - 501.0 / 900.0) * 5.5
+_dsp_fx_at_level = _dsp_fx.opt.model.simulate_trajectory_with_dhw(
+    **{**_dsp_fx_sim, "space_power_schedule": _dsp_fx.space, "end_state": []}
+)
+_dsp_fx_at_avail = _dsp_fx.opt.model.simulate_trajectory_with_dhw(
+    **{**_dsp_fx_sim, "space_power_schedule": _dsp_fx_expect, "end_state": []}
+)
+R.check(
+    "fixed-speed: the published room trajectory is the simulation at "
+    "avail x p_max in the charged steps that hold heating and at the shipped "
+    "level everywhere else, and differs from the one at p_max",
+    np.array_equal(_dsp_fx_fed, _dsp_fx_expect)
+    and list(_dsp_fx_at_avail[0]) == list(_dsp_fx.result.room_temp_trajectory)
+    and list(_dsp_fx_at_level[0]) != list(_dsp_fx.result.room_temp_trajectory),
+    f"fed {_dsp_fx_fed[_dsp_fx_charged]}, live {_dsp_fx_live}",
+)
+R.check(
+    "fixed-speed: the published start count is count_compressor_starts on the "
+    "shipped total, unchanged by the pairs on the same arrays",
+    _dsp_fx.result.compressor_starts == _dsp_starts(_dsp_fx_total)
+    and _dsp_base["fixed-speed"].result.compressor_starts
+    == _dsp_starts(_dsp_fx0.space + _dsp_fx0.dhw),
+    f"{_dsp_fx.result.compressor_starts}",
+)
+R.check(
+    "fixed-speed null control: with a zero pair the simulation is fed the "
+    "shipped schedule and no vector exists",
+    np.array_equal(_dsp_fx0.sims[-1]["space_power_schedule"], _dsp_fx0.space)
+    and _dsp_fx0.opt._space_avail is None,
+)
+
+# 6. The banned candidate: its channel, its ban, its guard.
+R.check(
+    "a priced plan with a priced switch tries exactly one more hot-water plan, "
+    "the first build's own arguments plus the ban, and no unpriced solve "
+    "builds one",
+    all(
+        len(s.bans) == 1
+        and sorted(s.builds[-1][0]) == sorted([*s.builds[0][0], "placement_ban"])
+        and np.array_equal(
+            s.bans[0],
+            _dsp_dl.switch_ban(
+                _dsp_om._realize_joint(
+                    s.opt.config.clamp_planned_levels, s.solves[-1][1], s.solves[0][0],
+                    s.opt.model.params.min_electrical_power, 5.5,
+                )[0],
+                _DSP_PAIR, _dsp_om._duty_floor(s.opt),
+            ),
+        )
+        for s in _dsp_priced.values()
+    )
+    and not any(s.bans for s in _dsp_base.values()),
+    f"{[(n, len(s.bans), len(s.builds), len(s.solves)) for n, s in _dsp_priced.items()]}",
+)
+R.check(
+    "the ban is the steps heating runs in or runs in next, for hot water to "
+    "heating, and mirrors onto the previous step for the other direction",
+    _dsp_dl.switch_ban(np.array([0, 0, 2.0, 0, 0]), (1.0, 0.0), None).tolist()
+    == [False, True, True, False, False]
+    and _dsp_dl.switch_ban(np.array([0, 0, 2.0, 0, 0]), (0.0, 1.0), None).tolist()
+    == [False, False, True, True, False]
+    and not _dsp_dl.switch_ban(np.array([0, 0, 2.0, 0, 0]), (1.0, 0.0), 3.0).any(),
+)
+_dsp_ban_writes = [
+    (name, np.flatnonzero(out[0].schedule[kwargs["placement_ban"]] > 0).tolist())
+    for name, s in _dsp_priced.items()
+    for kwargs, out, *_ in s.builds
+    if "placement_ban" in kwargs
+]
+_dsp_min_run_moves = [
+    int(np.sum(before != after))
+    for s in _dsp_priced.values()
+    for (kwargs, *_), (before, after) in zip(s.builds, s.min_runs)
+    if "placement_ban" in kwargs
+]
+R.check(
+    "the ban holds: the candidate's schedule is zero on every banned step, on "
+    "builds whose min-run stage rewrote the plan",
+    all(not steps for _, steps in _dsp_ban_writes)
+    and len(_dsp_min_run_moves) == 3 and all(n > 0 for n in _dsp_min_run_moves),
+    f"{_dsp_ban_writes}, min-run rewrote {_dsp_min_run_moves} steps",
+)
+
+# The channel: a due disinfection, no Off window, a manual force-on pin.
+_dsp_pin = np.full(96, np.nan)
+_dsp_pin[12] = 1.0
+_dsp_leg = _dsp_solve(None, legionella_h=200.0, pins=_dsp_pin)
+_dsp_leg_kw, (_dsp_leg_plan, _dsp_leg_req), _dsp_leg_h, _dsp_leg_planner = _dsp_leg.builds[0]
+_dsp_leg_ban = np.zeros(96, dtype=bool)
+_dsp_leg_ban[:16] = True
+_dsp_by_ban = _dsp_leg_planner._build_dhw_requirements(
+    _dsp_leg_h, **_dsp_leg_kw, placement_ban=_dsp_leg_ban
+)
+_dsp_by_off = _dsp_leg_planner._build_dhw_requirements(
+    _dsp_leg_h, **{**_dsp_leg_kw, "off_steps": _dsp_leg_ban}
+)
+_dsp_by_none = _dsp_leg_planner._build_dhw_requirements(
+    _dsp_leg_h, **_dsp_leg_kw, placement_ban=None
+)
+R.check(
+    "the ban's channel: with a disinfection due inside it and no Off window, a "
+    "banned build returns the same legionella_step and the same requirement, "
+    "and a manual force-on pin inside the ban survives",
+    _dsp_leg_plan.legionella_due and _dsp_leg_plan.legionella_step is not None
+    and bool(_dsp_leg_ban[_dsp_leg_plan.legionella_step])
+    and _dsp_by_ban[0].legionella_step == _dsp_leg_plan.legionella_step
+    and np.array_equal(_dsp_by_ban[1], _dsp_leg_req)
+    and _dsp_by_ban[0].schedule[12] > 0
+    and not np.any(np.delete(_dsp_by_ban[0].schedule[:16], 12) > 0),
+    f"step {_dsp_by_ban[0].legionella_step} vs {_dsp_leg_plan.legionella_step}, "
+    f"banned {np.flatnonzero(_dsp_by_ban[0].schedule[:16] > 0).tolist()}",
+)
+R.check(
+    "and the check tells the two doors apart: the same mask through off_steps "
+    "moves the disinfection step and zeroes the pinned step",
+    _dsp_by_off[0].legionella_step != _dsp_leg_plan.legionella_step
+    and _dsp_by_off[0].schedule[12] == 0,
+    f"step {_dsp_by_off[0].legionella_step}",
+)
+R.check(
+    "null control: a build with no ban is the build the solve made",
+    np.array_equal(_dsp_by_none[0].schedule, _dsp_leg_plan.schedule)
+    and np.array_equal(_dsp_by_none[1], _dsp_leg_req)
+    and _dsp_by_none[0].legionella_step == _dsp_leg_plan.legionella_step,
+)
+
+# The guard, on that disinfection fixture: heating right after the run-up
+# makes a priced switch, the ban then forbids the run-up steps, and the banned
+# candidate cannot hold the requirement the planner returns beside it.
+_dsp_g_opt = _dsp_opt(_DSP_PAIR, _DSP_OFF)
+_dsp_g_step = int(_dsp_leg_plan.legionella_step)
+_dsp_g_space = np.zeros(96)
+_dsp_g_space[_dsp_g_step + 1 : _dsp_g_step + 3] = 3.0
+_dsp_g_dhw = np.asarray(_dsp_leg_plan.schedule, float)
+_dsp_g_incumbent = (_dsp_g_space, _dsp_g_dhw, "optimal")
+_dsp_g_avail = np.ones(96)
+_dsp_g_calls = []
+
+
+def _dsp_g_solve(score):
+    def solve_space(dhw_plan, warm_start):
+        _dsp_g_calls.append(np.array(dhw_plan, float))
+        _dsp_g_opt._space_avail = None
+        return np.asarray(warm_start, float) * 0.5, "candidate", score
+    return solve_space
+
+
+def _dsp_g_run(score, shortfall=None, requirement=True):
+    """One candidate pass; returns what it returned and what it left behind."""
+    _dsp_g_opt._dhw_requirement = _dsp_leg_req if requirement else None
+    _dsp_g_opt._space_avail = _dsp_g_avail
+    del _dsp_g_calls[:]
+    planner = _dsp_leg_planner
+    if shortfall is not None:
+        planner = _DspNS(
+            _build_dhw_requirements=_dsp_leg_planner._build_dhw_requirements,
+            _dhw_coil_wood_forecast=_dsp_leg_planner._dhw_coil_wood_forecast,
+            _dhw_shortfall=shortfall,
+        )
+    out = _dsp_om._avoid_priced_switches(
+        _dsp_g_opt, _dsp_leg_h, planner, _dsp_g_solve(score),
+        lambda *a: 0.0, 5.5, _dsp_g_incumbent,
+    )
+    return out, _dsp_g_opt._dhw_requirement, _dsp_g_opt._space_avail, len(_dsp_g_calls)
+
+
+_dsp_g_ban = _dsp_dl.switch_ban(_dsp_g_space, _DSP_PAIR, None)
+_dsp_g_short = _dsp_g_run(-1e9)
+R.check(
+    "the guard's fixture is the one it names: the incumbent holds a priced "
+    "switch after the disinfection run-up and the ban forbids the run-up step",
+    _dsp_dl.switch_weight(_dsp_g_space, _dsp_g_dhw, _DSP_PAIR, 5.5) > 0
+    and bool(_dsp_g_ban[_dsp_g_step]) and _dsp_g_dhw[_dsp_g_step] > 0,
+)
+R.check(
+    "a banned candidate that scores lower but falls short of its returned "
+    "requirement where the incumbent holds its own is refused before any "
+    "solve, and the incumbent's requirement and availability stay in place",
+    _dsp_g_short[0] is _dsp_g_incumbent and _dsp_g_short[1] is _dsp_leg_req
+    and _dsp_g_short[2] is _dsp_g_avail and _dsp_g_short[3] == 0,
+    f"{_dsp_g_short[3]} solves, incumbent kept {_dsp_g_short[0] is _dsp_g_incumbent}",
+)
+_dsp_g_held = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+R.check(
+    "control: the same candidate with the shortfall reading zero is adopted on "
+    "its lower score, with the requirement returned beside it",
+    _dsp_g_held[0] is not _dsp_g_incumbent and _dsp_g_held[0][2] == "candidate"
+    and _dsp_g_held[1] is not _dsp_leg_req and _dsp_g_held[3] == 1
+    and not np.any(_dsp_g_held[0][1][_dsp_g_ban & ~(np.nan_to_num(_dsp_pin) >= 0.5)] > 0),
+    f"{_dsp_g_held[3]} solves",
+)
+_dsp_g_dear = _dsp_g_run(1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+R.check(
+    "a candidate that does not score lower is refused after its solve, and the "
+    "incumbent's requirement and availability are put back",
+    _dsp_g_dear[0] is _dsp_g_incumbent and _dsp_g_dear[1] is _dsp_leg_req
+    and _dsp_g_dear[2] is _dsp_g_avail and _dsp_g_dear[3] == 1,
+)
+_dsp_g_bare = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None), requirement=False)
+R.check(
+    "an incumbent with no requirement to hold a candidate to gets no candidate: "
+    "the pass the control adopts from returns the incumbent without a solve",
+    _dsp_g_bare[0] is _dsp_g_incumbent and _dsp_g_bare[1] is None
+    and _dsp_g_bare[2] is _dsp_g_avail and _dsp_g_bare[3] == 0,
+    f"{_dsp_g_bare[3]} solves, incumbent kept {_dsp_g_bare[0] is _dsp_g_incumbent}",
+)
+
+
+def _dsp_g_raises(*_a):
+    raise RuntimeError("the planner's tank walk failed")
+
+
+_dsp_g_broke = _dsp_g_run(-1e9, shortfall=_dsp_g_raises)
+R.check(
+    "a candidate pass that raises is skipped: the incumbent, its requirement "
+    "and its availability stand, and nothing is solved",
+    _dsp_g_broke[0] is _dsp_g_incumbent and _dsp_g_broke[1] is _dsp_leg_req
+    and _dsp_g_broke[2] is _dsp_g_avail and _dsp_g_broke[3] == 0,
+)
+_dsp_g_real_build = _dsp_om._dhw_build
+_dsp_om._dhw_build = lambda *a, **k: (_dsp_leg_plan, _dsp_leg_req)
+try:
+    _dsp_g_on_ban = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+finally:
+    _dsp_om._dhw_build = _dsp_g_real_build
+R.check(
+    "a candidate with hot water on a banned step no pin forces on is refused "
+    "before any solve",
+    _dsp_g_on_ban[0] is _dsp_g_incumbent and _dsp_g_on_ban[3] == 0
+    and _dsp_g_on_ban[1] is _dsp_leg_req,
+)
+# The pin rule is the planner's own (``_apply_dhw_pins``): a pin of 0.5 forces on.
+_dsp_g_pins = _dsp_leg_h.dhw_pins
+_dsp_g_half = np.full(96, np.nan)
+_dsp_g_half[_dsp_g_ban & (np.asarray(_dsp_leg_plan.schedule, float) > 0)] = 0.5
+_dsp_om._dhw_build = lambda *a, **k: (_dsp_leg_plan, _dsp_leg_req)
+try:
+    object.__setattr__(_dsp_leg_h, "dhw_pins", _dsp_g_half)
+    _dsp_g_half_on = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+finally:
+    object.__setattr__(_dsp_leg_h, "dhw_pins", _dsp_g_pins)
+    _dsp_om._dhw_build = _dsp_g_real_build
+R.check(
+    "the same candidate with each of those steps pinned at 0.5, which the "
+    "planner's pin rule forces on, is solved and adopted on its lower score",
+    int(np.sum(_dsp_g_half == 0.5)) > 0
+    and _dsp_g_half_on[3] == 1 and _dsp_g_half_on[0][2] == "candidate"
+    and _dsp_g_half_on[0][1] is _dsp_leg_plan.schedule,
+    f"{_dsp_g_half_on[3]} solve(s), {int(np.sum(_dsp_g_half == 0.5))} pinned step(s)",
+)
+_dsp_g_trickle = np.asarray(_dsp_leg_plan.schedule, float).copy()
+_dsp_g_trickle[_dsp_g_ban] = np.where(_dsp_g_trickle[_dsp_g_ban] > 0, 0.8, 0.0)
+_dsp_om._dhw_build = lambda *a, **k: (
+    _DspNS(schedule=_dsp_g_trickle, draw_rates=_dsp_leg_plan.draw_rates), _dsp_leg_req
+)
+try:
+    _dsp_g_low_on_ban = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+finally:
+    _dsp_om._dhw_build = _dsp_g_real_build
+R.check(
+    "any hot water on a banned step refuses the candidate, 0.8 kW as much as "
+    "a full block",
+    bool(np.any(_dsp_g_trickle[_dsp_g_ban] == 0.8))
+    and _dsp_g_low_on_ban[0] is _dsp_g_incumbent and _dsp_g_low_on_ban[3] == 0,
+    f"{_dsp_g_low_on_ban[3]} solve(s)",
+)
+_dsp_g_tie = _dsp_g_run(-1e-9, shortfall=lambda *a: (None, np.zeros(96), None))
+R.check(
+    "a candidate lower by exactly the 1e-9 margin, and so by no more than "
+    "it, is a tie: refused after its solve, as _co_optimize refuses its own",
+    _dsp_g_tie[0] is _dsp_g_incumbent and _dsp_g_tie[3] == 1
+    and _dsp_g_tie[1] is _dsp_leg_req and _dsp_g_tie[2] is _dsp_g_avail,
+    f"{_dsp_g_tie[3]} solve(s)",
+)
+_dsp_g_walks = []
+
+
+def _dsp_g_walk(temps, schedule, *rest):
+    """A tank walk short at step 5 until that step is excused."""
+    _dsp_g_walks.append(temps)
+    return "walked", np.zeros(96), (None if rest[-1] else 5)
+
+
+_dsp_g_run(-1e9, shortfall=_dsp_g_walk)
+R.check(
+    "the incumbent's tank is walked once: the read past its excused step is "
+    "handed the first walk's temperatures",
+    _dsp_g_walks[:2] == [None, "walked"],
+    f"{_dsp_g_walks}",
+)
+R.check(
+    "a configuration that never heard of the learner holds a zero pair in "
+    "both fields, and an optimizer that has solved nothing holds no vector",
+    _DspCfg().duty_switch_stop_probability == (0.0, 0.0)
+    and _DspCfg().duty_switch_off_seconds == (0.0, 0.0)
+    and _dsp_opt(None, None)._space_avail is None,
+)
+_dsp_g_opt.config.duty_switch_stop_probability = (0.0, 0.0)
+_dsp_g_unpriced = _dsp_g_run(-1e9, shortfall=lambda *a: (None, np.zeros(96), None))
+_dsp_g_opt.config.duty_switch_stop_probability = _DSP_PAIR
+R.check(
+    "null control: with a zero pair the pass returns the incumbent without a "
+    "build or a solve",
+    _dsp_g_unpriced[0] is _dsp_g_incumbent and _dsp_g_unpriced[3] == 0,
+)
+
+# 8. The term's edges. Hot water under a third of p_max puts both collapse
+# edges of a both step inside the bounds; warm starts sit two finite-difference
+# steps either side of each, and one at the running threshold.
+_dsp_e = _dsp_solve(_DSP_PAIR, (0.0, 0.0))
+_dsp_e0 = _dsp_solve((0.0, 0.0), (501.0, 0.0))
+_dsp_e_tank = np.zeros(96)
+_dsp_e_tank[[40, 41]] = 1.5
+_DSP_EPS = 2.0 * _dsp_om._LBFGSB_FD_EPS
+
+
+def _dsp_e_start(step, level):
+    start = np.full(96, 2.0)
+    start[step] = level
+    return start
+
+
+_DSP_E_STARTS = {
+    "under the lower collapse edge": _dsp_e_start(40, 0.75 - _DSP_EPS),
+    "over the lower collapse edge": _dsp_e_start(40, 0.75 + _DSP_EPS),
+    "under the upper collapse edge": _dsp_e_start(41, 3.0 - _DSP_EPS),
+    "over the upper collapse edge": _dsp_e_start(41, 3.0 + _DSP_EPS),
+    "at the running threshold": _dsp_e_start(42, 0.1 + _DSP_EPS),
+}
+
+
+def _dsp_e_solve(seen, start):
+    args = seen.solves[0]
+    power, status, score = seen.opt._solve_space(_dsp_e_tank, start, *args[2:])
+    return power, status, score, float(args[8](start, _dsp_e_tank))
+
+
+_dsp_e_runs = {
+    label: (_dsp_e_solve(_dsp_e, start), _dsp_e_solve(_dsp_e0, start), _dsp_e_solve(_dsp_base["duty-cycle"], start))
+    for label, start in _DSP_E_STARTS.items()
+}
+R.check(
+    "the edge fixture is the one it names: 1.5 kW of hot water under a third "
+    "of p_max, and the starts straddle a change in the legs",
+    1.5 < 5.5 / 3.0
+    and [bool(_dsp_dl.leg_ends(s, _dsp_e_tank)[2][i]) for s, i in (
+        (_DSP_E_STARTS["under the lower collapse edge"], 40),
+        (_DSP_E_STARTS["over the lower collapse edge"], 40),
+        (_DSP_E_STARTS["under the upper collapse edge"], 41),
+        (_DSP_E_STARTS["over the upper collapse edge"], 41),
+    )] == [False, True, True, False],
+)
+R.check(
+    "from each edge start the priced solve returns a score no higher than its "
+    "start's, with a solver status no worse than the same start solved unpriced",
+    all(
+        priced[2] <= priced[3] + 1e-9 and (priced[1] == null[1] or priced[1] == "optimal")
+        for priced, null, _ in _dsp_e_runs.values()
+    ),
+    f"{[(k, round(p[3] - p[2], 4), p[1], n[1]) for k, (p, n, _) in _dsp_e_runs.items()]}",
+)
+R.check(
+    "null control: with a zero pair the same starts return the arrays of a "
+    "config that never heard of the fields",
+    all(
+        np.array_equal(null[0], plain[0]) and null[1:] == plain[1:]
+        for _, null, plain in _dsp_e_runs.values()
+    ),
+)
+
+# Item r14: a relaxed start of a clamped install scores unrounded levels; the
+# delivered draw gives it the clamped reading on that unrounded level.
+_dsp_rx_opt = _dsp_opt(_DSP_PAIR, _DSP_OFF, clamp=True)
+_dsp_rx_args = (np.array([0.7, 3.0]), np.array([0.0, 0.0]), np.array([0.5, 0.5]))
+_dsp_rx_rounded = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args)
+_dsp_rx_opt._levels_relaxed = True
+try:
+    _dsp_rx_relaxed = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args)
+finally:
+    _dsp_rx_opt._levels_relaxed = False
+R.check(
+    "a relaxed start carrying a vector is charged on its unrounded level, the "
+    "rounded objective on the level that ships",
+    _dsp_rx_relaxed[0].tolist() == [0.7, 3.0] and _dsp_rx_relaxed[2].tolist() == [0.35, 1.5]
+    and _dsp_rx_rounded[0].tolist() != [0.7, 3.0]
+    and _dsp_rx_rounded[2].tolist() == (_dsp_rx_rounded[0] * 0.5).tolist(),
+    f"{_dsp_rx_relaxed[2]}, {_dsp_rx_rounded[0]}, {_dsp_rx_rounded[2]}",
+)
+_dsp_rx_plain = _dsp_om._shipped_and_received(_dsp_rx_opt, *_dsp_rx_args[:2], None)
+R.check(
+    "and with no vector the received draw is the shipped array itself",
+    _dsp_rx_plain[2] is _dsp_rx_plain[0],
+)
+
+# What reads the shipped level and what reads the delivered draw, on a
+# modulating clamped install that prices no cycle (so nothing steers the plan
+# off its charged steps) and on the fixed-speed plan above.
+R.check(
+    "the plan's duty floor reaches the switch weight: heating under the floor "
+    "after a block is no leg and no switch",
+    _dsp_w([0, 1.0], [3, 0], (0.8, 0.0)) == 0.8 * 1.0 / 6.0
+    and _dsp_w([0, 1.0], [3, 0], (0.8, 0.0), floor=1.5) == 0.0,
+)
+R.check(
+    "at the exact minute the hot-water share ends the arbiter serves heating "
+    "(a strict <, as before the rule moved)",
+    [_dsp_served(3.0, 2.0, m, None) for m in (5.99, 6.0, 6.01)] == ["dhw", "space", "space"],
+    f"{[_dsp_served(3.0, 2.0, m, None) for m in (5.99, 6.0, 6.01)]}",
+)
+_dsp_mc = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, cyc=0.0)
+_dsp_mc_avail = _dsp_mc.opt._space_avail
+_dsp_mc_fed = np.asarray(_dsp_mc.sims[-1]["space_power_schedule"], float)
+_dsp_mc_live = (
+    [] if _dsp_mc_avail is None
+    else [i for i in np.flatnonzero(_dsp_mc_avail < 1.0).tolist() if _dsp_mc.space[i] > 0]
+)
+_dsp_mc_obj, _dsp_mc_batch, _dsp_mc_energy = (_dsp_mc.objectives[-1][i] for i in (1, 2, 3))
+_dsp_mc_rebuilt = (
+    None if _dsp_mc_avail is None
+    else _dsp_om._stop_availability(_dsp_mc.opt, _dsp_mc.space, _dsp_mc.dhw, 5.5)
+)
+R.check(
+    "modulating clamped: the simulation is fed the delivered draw of the "
+    "vector the adopted solve scored with, which is not the vector the final "
+    "plan would rebuild",
+    bool(_dsp_mc_live)
+    and np.array_equal(
+        _dsp_mc_fed, _dsp_dl.delivered_space(_dsp_mc.space, _dsp_mc.dhw, _dsp_mc_avail, 1.5)
+    )
+    and not np.array_equal(_dsp_mc_fed, _dsp_mc.space)
+    and (_dsp_mc_rebuilt is None or not np.array_equal(
+        _dsp_mc_fed, _dsp_dl.delivered_space(_dsp_mc.space, _dsp_mc.dhw, _dsp_mc_rebuilt, 1.5)
+    )),
+    f"live {_dsp_mc_live}",
+)
+R.check(
+    "the vector is built once per space solve and never at publication, on "
+    "every priced solve above",
+    all(s.vectors[0] == len(s.solves) for s in [*_dsp_priced.values(), _dsp_mc]),
+    f"{[(s.vectors[0], len(s.solves)) for s in [*_dsp_priced.values(), _dsp_mc]]}",
+)
+R.check(
+    "modulating clamped (item r15): the achieved objective is the closure on "
+    "the shipped arrays with that vector, not on the delivered draw, which "
+    "would charge the lost time twice",
+    bool(_dsp_mc_live)
+    and float(_dsp_mc_obj(_dsp_mc.space, _dsp_mc.dhw, None, _dsp_mc_avail))
+    == float(_dsp_mc.result.objective_value)
+    != float(_dsp_mc_obj(_dsp_mc_fed, _dsp_mc.dhw, None, _dsp_mc_avail))
+    and float(_dsp_mc_obj(_dsp_mc.space, _dsp_mc.dhw)) != float(_dsp_mc.result.objective_value),
+)
+R.check(
+    "modulating clamped: the predicted cost is the energy of the delivered "
+    "draw, not of the shipped level",
+    bool(_dsp_mc_live)
+    and float(_dsp_mc.result.predicted_cost) == float(_dsp_mc_energy(_dsp_mc_fed + _dsp_mc.dhw))
+    != float(_dsp_mc_energy(_dsp_mc.space + _dsp_mc.dhw)),
+)
+_dsp_mc_scalar = float(_dsp_mc_obj(_dsp_mc.space, _dsp_mc.dhw, None, _dsp_mc_avail))
+_dsp_mc_scalar_energy = _dsp_mc.energy[0]
+_dsp_mc_rows = float(
+    _dsp_mc_batch(np.stack([_dsp_mc.space, _dsp_mc.space]), _dsp_mc.dhw, None, _dsp_mc_avail)[1]
+)
+_dsp_mc_batch_energy = _dsp_mc.energy[0]
+R.check(
+    "the scalar and the batch objective both price the energy of the "
+    "delivered draw plus hot water, and agree bit for bit with a vector",
+    np.array_equal(_dsp_mc_scalar_energy, _dsp_mc_fed + _dsp_mc.dhw)
+    and np.array_equal(_dsp_mc_batch_energy[1], _dsp_mc_fed + _dsp_mc.dhw)
+    and _dsp_mc_rows == _dsp_mc_scalar,
+    f"{_dsp_mc_rows} vs {_dsp_mc_scalar}",
+)
+# The switch term reads the shipped level: on the fixed-speed plan the
+# delivered draw of a charged step is under the floor and would be no leg.
+_dsp_fx_free = _dsp_solve(_DSP_PAIR, _DSP_OFF, clamp=True, p_min=5.5, cyc=0.0)
+_dsp_fx_obj, _dsp_fx_batch = _dsp_fx.objectives[-1][1], _dsp_fx.objectives[-1][2]
+_dsp_fx_score = float(_dsp_fx_obj(_dsp_fx.space, _dsp_fx.dhw, None, _dsp_fx_avail))
+_dsp_fx_level_terms = _dsp_fx.opt.config.price_weight * (
+    _dsp_cyc(_dsp_fx_total, 0.3, 5.5)
+    + 0.3 * _dsp_dl.switch_weight(_dsp_fx.space, _dsp_fx.dhw, _DSP_PAIR, 5.5, 5.5)
+)
+_dsp_fx_unpriced = float(
+    _dsp_fx_free.objectives[-1][1](_dsp_fx.space, _dsp_fx.dhw, None, _dsp_fx_avail)
+)
+R.check(
+    "fixed-speed: what pricing a cycle adds to a plan's score is the cycling "
+    "term plus cycling_cost x the switch weight of the shipped levels",
+    _dsp_dl.switch_weight(_dsp_fx.space, _dsp_fx.dhw, _DSP_PAIR, 5.5, 5.5) > 0
+    and abs(_dsp_fx_score - _dsp_fx_unpriced - _dsp_fx_level_terms) < 1e-9,
+    f"{_dsp_fx_score - _dsp_fx_unpriced} vs {_dsp_fx_level_terms}",
+)
+R.check(
+    "fixed-speed: the batch objective is the scalar one bit for bit with a "
+    "priced pair and a vector",
+    float(
+        _dsp_fx_batch(np.stack([_dsp_fx.space, _dsp_fx.space]), _dsp_fx.dhw, None, _dsp_fx_avail)[1]
+    ) == _dsp_fx_score,
+)
+_dsp_quiet = _dsp_solve(_DSP_PAIR, _DSP_OFF, legionella_h=200.0)
+R.check(
+    "a priced install whose plan holds no priced switch builds no candidate",
+    _dsp_dl.switch_weight(_dsp_quiet.space, _dsp_quiet.dhw, _DSP_PAIR, 5.5) == 0.0
+    and not _dsp_quiet.bans and len(_dsp_quiet.builds) == 1,
+    f"{len(_dsp_quiet.bans)} banned build(s) of {len(_dsp_quiet.builds)}",
+)
+# _co_optimize's own candidate: refused, it leaves the incumbent's vector.
+_dsp_co = _dsp_base["fixed-speed"]
+_dsp_co_calls = []
+
+
+def _dsp_co_solve(dhw_plan, warm_start):
+    _dsp_co_calls.append(1)
+    _dsp_co.opt._space_avail = None
+    return np.asarray(warm_start, float), "candidate", 0.0
+
+
+_dsp_co_kept = _dsp_co.opt._space_avail = np.ones(96)
+_dsp_co_out = _dsp_co.opt._co_optimize(
+    _dsp_co.builds[0][2],
+    space_power=_dsp_co.solved[0][0],
+    dhw_power=np.asarray(_dsp_co.builds[0][1][0].schedule, float),
+    status="first", best_score=-1e9, solve_space=_dsp_co_solve, p_max=5.5,
+    planner=_dsp_co.builds[0][3],
+)
+R.check(
+    "a refused co-optimisation candidate leaves the vector its incumbent was "
+    "scored with",
+    len(_dsp_co_calls) == 1 and _dsp_co_out[2] == "first"
+    and _dsp_co.opt._space_avail is _dsp_co_kept,
+    f"{len(_dsp_co_calls)} candidate solve(s), status {_dsp_co_out[2]}",
+)
+# _co_optimize's headroom is the charged bound: on a duty-cycle install heating
+# solved hard against avail x p_max - dhw wanted more than it could have, so
+# the step is pinned and hot water is re-planned against a full compressor.
+_dsp_hr_dhw = np.zeros(96)
+_dsp_hr_dhw[40] = 2.0
+_dsp_hr_avail = np.ones(96)
+_dsp_hr_avail[40] = 1.0 - _dsp_dl.lost_share(_DSP_PAIR, _DSP_OFF)
+_dsp_hr_at_bound = np.zeros(96)
+_dsp_hr_at_bound[40] = _dsp_hr_avail[40] * 5.5 - 2.0
+_dsp_hr_at_bound[41] = 2.0
+_dsp_hr_at_plain = _dsp_hr_at_bound.copy()
+_dsp_hr_at_plain[40] = 5.5 - 2.0
+
+
+def _dsp_hr_demand(space, avail, **install):
+    """The space demand ``_co_optimize`` hands its replan, ``None`` when it builds none."""
+    opt = _dsp_opt(_DSP_PAIR, _DSP_OFF, **install)
+    opt._space_avail = avail
+    seen = []
+
+    def build(h, **kw):
+        seen.append(np.asarray(kw["space_demand"], float))
+        return _DspNS(schedule=_dsp_hr_dhw.copy()), None
+
+    opt._co_optimize(
+        _dsp_co.builds[0][2], space_power=space, dhw_power=_dsp_hr_dhw,
+        status="first", best_score=0.0, solve_space=_dsp_g_raises, p_max=5.5,
+        planner=_DspNS(
+            _dhw_coil_wood_forecast=lambda *a: None, _build_dhw_requirements=build
+        ),
+    )
+    return seen[0] if seen else None
+
+
+_dsp_hr_pinned = _dsp_hr_demand(_dsp_hr_at_bound, _dsp_hr_avail)
+R.check(
+    "the co-optimisation reads the charged bound: on a duty-cycle install "
+    "heating at avail x p_max - dhw in a charged step is pinned, and the "
+    "replan is built against a full compressor there and nowhere else",
+    _dsp_hr_at_bound[40] < 5.5 - 2.0 - 1e-3
+    and _dsp_hr_pinned is not None
+    and np.flatnonzero(_dsp_hr_pinned == 5.5).tolist() == [40]
+    and _dsp_hr_pinned[41] == 2.0,
+    f"{None if _dsp_hr_pinned is None else np.flatnonzero(_dsp_hr_pinned == 5.5).tolist()}",
+)
+R.check(
+    "null controls: the same heating with no vector, or with the vector on a "
+    "clamped install whose bound carries no lost time, is under its bound and "
+    "builds no replan; at the uncharged bound each of the two builds one",
+    _dsp_hr_demand(_dsp_hr_at_bound, None) is None
+    and _dsp_hr_demand(_dsp_hr_at_bound, _dsp_hr_avail, clamp=True) is None
+    and _dsp_hr_demand(_dsp_hr_at_plain, None) is not None
+    and _dsp_hr_demand(_dsp_hr_at_plain, _dsp_hr_avail, clamp=True) is not None,
+)
+
+# The candidate pass is not for a combi store, whose hot-water plan is a
+# feasibility repair scored with no buffer flux: nothing is built or solved.
+import heatpump_optimizer.mixing_valve as _dsp_mv  # noqa: E402
+
+
+def _dsp_combi_pass(combi):
+    """What the candidate pass asks of its planner on a store-buffer install."""
+    params = _DspTP(
+        buffer_tank_volume=504.0, mixing_valve_mode=_dsp_mv.MODE_SMART_WRITE,
+        dhw_enabled=True, dhw_tank_volume=200.0, dhw_combi_tank_enabled=combi,
+    )
+    params.min_electrical_power, params.max_electrical_power = 1.5, 5.5
+    cfg = _DspCfg(cycling_cost=0.3)
+    cfg.duty_switch_stop_probability, cfg.duty_switch_off_seconds = _DSP_PAIR, _DSP_OFF
+    opt = _DspOpt(_DspTM(params), cfg)
+    opt._dhw_requirement, opt._space_avail = _dsp_leg_req, _dsp_g_avail
+    asked = []
+
+    def build(h, **kw):
+        asked.append(kw.get("placement_ban"))
+        raise RuntimeError("the fixture's build")
+
+    out = _dsp_om._avoid_priced_switches(
+        opt, _dsp_leg_h,
+        _DspNS(_dhw_coil_wood_forecast=lambda *a: asked.append(None), _build_dhw_requirements=build),
+        _dsp_g_raises, lambda *a: 0.0, 5.5, _dsp_g_incumbent,
+    )
+    return opt.model.params.dhw_store.combi, out, asked, opt
+
+
+_dsp_combi_on, _dsp_combi_off = _dsp_combi_pass(True), _dsp_combi_pass(False)
+R.check(
+    "on a combi store the candidate pass asks its planner nothing and returns "
+    "the incumbent, its requirement and its availability in place, on an "
+    "incumbent holding a priced switch",
+    _dsp_combi_on[0] is True and _dsp_combi_on[1] is _dsp_g_incumbent
+    and _dsp_combi_on[2] == []
+    and _dsp_combi_on[3]._dhw_requirement is _dsp_leg_req
+    and _dsp_combi_on[3]._space_avail is _dsp_g_avail,
+    f"combi {_dsp_combi_on[0]}, {len(_dsp_combi_on[2])} planner call(s)",
+)
+R.check(
+    "null control: the same install with the store's hot water in its own "
+    "tank reaches the banned build",
+    _dsp_combi_off[0] is False and _dsp_combi_off[1] is _dsp_g_incumbent
+    and len(_dsp_combi_off[2]) == 2 and _dsp_combi_off[2][1] is not None,
+    f"combi {_dsp_combi_off[0]}, {len(_dsp_combi_off[2])} planner call(s)",
+)
+
+
+# 7. The learner's side: the bound on the decayed count, and the read the
+# planner prices by. Everything below needs the predecessor's module.
+import json  # noqa: E402
+
+from heatpump_optimizer import duty_switch as _dsp_ds, pump_mode as _dsp_pm  # noqa: E402
+
+_DSP_DAY = datetime(2026, 11, 10, tzinfo=UTC)
+
+
+def _dsp_stop(learner, at, off_s):
+    """One hot water to heating switch at ``at`` that stops the compressor 19 s
+    later, void-checked on the next pass, restarting after ``off_s``."""
+    ctx = _dsp_ds.SwitchContext(
+        mode_written_at=at, last_write_at=at, inlet_c=44.2, water_setpoint_c=32.0,
+        target_demand=True, plan_stays=True)
+    learner.mode_write(at, _dsp_pm.MODE_DHW, _dsp_pm.MODE_HEAT, True, ctx)
+    learner.edge(at + timedelta(seconds=19), False)
+    learner.note_pass(at + timedelta(seconds=60), ctx, False)
+    learner.edge(at + timedelta(seconds=19 + off_s), True)
+
+
+def _dsp_dir(k, kept_w, usable=True, off_s=()):
+    return _dsp_ds.Direction(k=k, kept_w=kept_w, decayed_at=_DSP_DAY, first_day=_DSP_DAY.date(),
+                 last_day=_DSP_DAY.date() + timedelta(days=1), usable=usable, off_s=list(off_s))
+
+
+def _dsp_kept(count, days=0):
+    """A direction latched at the cap on stops alone, then ``count`` kept
+    episodes at one instant, then aged ``days``; and the largest n it held."""
+    d = _dsp_dir(_dsp_ds.N_CAP, 0.0)
+    held = d.n
+    for _ in range(count):
+        d.book(_DSP_DAY, False, None)
+        held = max(held, d.n)
+    d.decay(_DSP_DAY + timedelta(days=days))
+    return d, held
+
+
+_dsp_fill = _dsp_ds.Direction()
+_dsp_fill_n = []
+for _dsp_i in range(40):
+    _dsp_fill.book(_DSP_DAY + timedelta(hours=_dsp_i), _dsp_i % 3 != 0, 501.0)
+    _dsp_fill_n.append(_dsp_fill.n)
+R.check(
+    "the decayed count is held at the cap, twice the on-threshold: forty "
+    "bookings an hour apart end on it and none leaves it above (to 1e-9, the "
+    "rounding of two scaled addends)",
+    _dsp_ds.N_CAP == 10.0 == 2 * _dsp_ds.N_ON
+    and max(_dsp_fill_n) <= _dsp_ds.N_CAP + 1e-9 and abs(_dsp_fill_n[-1] - _dsp_ds.N_CAP) < 0.05
+    and _dsp_fill_n[8] < _dsp_ds.N_CAP - 0.5,
+    f"largest n {max(_dsp_fill_n)!r}, last {_dsp_fill_n[-1]!r}, after nine {_dsp_fill_n[8]!r}",
+)
+_dsp_mix = _dsp_dir(6.0, 4.0)
+_dsp_mix.book(_DSP_DAY, True, None)
+R.check(
+    "the cap scales both counts alike: a stop booked on six of ten leaves "
+    "p at seven of eleven",
+    abs(_dsp_mix.p - 7.0 / 11.0) < 1e-12 and abs(_dsp_mix.n - _dsp_ds.N_CAP) < 1e-9,
+    f"p={_dsp_mix.p!r} n={_dsp_mix.n!r}",
+)
+_dsp_k12, _dsp_k12_held = _dsp_kept(12)
+_dsp_k13, _dsp_k13_held = _dsp_kept(13)
+R.check(
+    "from p = 1 at the cap the latch holds after twelve kept episodes and "
+    "drops at the thirteenth, each multiplying p by 10/11",
+    _dsp_k12.usable and not _dsp_k13.usable
+    and abs(_dsp_k12.p - (10.0 / 11.0) ** 12) < 1e-9 and abs(_dsp_k13.p - (10.0 / 11.0) ** 13) < 1e-9
+    and max(_dsp_k12_held, _dsp_k13_held) <= _dsp_ds.N_CAP + 1e-9,
+    f"p after 12 {_dsp_k12.p!r} usable={_dsp_k12.usable}; after 13 {_dsp_k13.p!r} usable={_dsp_k13.usable}",
+)
+R.check(
+    "with no episodes a capped direction is latched at 28 days and not the day after",
+    _dsp_kept(0, 28)[0].usable and not _dsp_kept(0, 29)[0].usable,
+    f"n at 28 days {_dsp_kept(0, 28)[0].n!r}, at 29 {_dsp_kept(0, 29)[0].n!r}",
+)
+_dsp_rt = _dsp_ds.DutySwitchLearner({"dhw_space": _dsp_k12, "space_dhw": _dsp_fill})
+_dsp_rt_back = _dsp_ds.DutySwitchLearner.from_record(json.loads(json.dumps(_dsp_rt.stored_record())))
+R.check(
+    "a capped record round-trips through its stored form",
+    _dsp_rt_back.directions == _dsp_rt.directions and _dsp_rt_back.directions["dhw_space"].usable,
+    f"{_dsp_rt_back.directions}",
+)
+
+# The read: both pairs in the leaf's order, zeros unless the stored latch is on.
+_dsp_table = _dsp_ds.DutySwitchLearner()
+for _dsp_i in range(6):
+    _dsp_stop(_dsp_table, _DSP_DAY + timedelta(hours=7 * _dsp_i), 501)
+R.check(
+    "six stopping switches over two days, each off 501 s, latch the direction "
+    "and the planner reads the acceptance fixture's pairs from the learner",
+    _dsp_table.directions["dhw_space"].usable
+    and _dsp_table.planner_pairs() == (_DSP_PAIR, _DSP_OFF),
+    f"{_dsp_table.planner_pairs()} against {(_DSP_PAIR, _DSP_OFF)}",
+)
+_DSP_LEARNERS = {
+    "an empty learner": _dsp_ds.DutySwitchLearner(),
+    "a learner under its on-threshold, off times stored": _dsp_ds.DutySwitchLearner(
+        {"dhw_space": _dsp_dir(4.0, 0.0, usable=False, off_s=[501.0, 492.0]), "space_dhw": _dsp_ds.Direction()}),
+    "an install whose every switch was kept": _dsp_ds.DutySwitchLearner(
+        {"dhw_space": _dsp_dir(0.0, 10.0, usable=False), "space_dhw": _dsp_dir(0.0, 10.0, usable=False)}),
+}
+R.check(
+    "the read returns zeros while a direction is unlatched, its off times with it",
+    all(l.planner_pairs() == ((0.0, 0.0), (0.0, 0.0)) for l in _DSP_LEARNERS.values()),
+    f"{ {n: l.planner_pairs() for n, l in _DSP_LEARNERS.items()} }",
+)
+_dsp_two = _dsp_ds.DutySwitchLearner({
+    "dhw_space": _dsp_dir(3.0, 1.0, off_s=[400.0, 501.0, 620.0, 700.0]),
+    "space_dhw": _dsp_dir(2.0, 2.0),
+})
+R.check(
+    "a latched direction reads its own p and median off time in its own slot, "
+    "hot water to heating first, and no off time while every stop's was censored",
+    _dsp_two.planner_pairs() == ((0.75, 0.5), (560.5, 0.0)),
+    f"{_dsp_two.planner_pairs()}",
+)
+
+# 4, the learner arm: each null state's read, handed to a full optimize.
+_dsp_arm_bad = []
+for _dsp_name, _dsp_kw in _DSP_INSTALLS.items():
+    for _dsp_label, _dsp_l in _DSP_LEARNERS.items():
+        _dsp_null = _dsp_solve(*_dsp_l.planner_pairs(), **_dsp_kw)
+        if (
+            not _dsp_same_plan(_dsp_null, _dsp_base[_dsp_name])
+            or _dsp_null.bans or _dsp_null.opt._space_avail is not None
+            or len(_dsp_null.builds) != len(_dsp_base[_dsp_name].builds)
+        ):
+            _dsp_arm_bad.append((_dsp_name, _dsp_label))
+R.check(
+    "null controls from learner state: an empty learner, one under its "
+    "on-threshold and an install whose every switch was kept each read a plan "
+    "identical to today's on all three install classes",
+    not _dsp_arm_bad,
+    f"{_dsp_arm_bad}",
+)
+R.check(
+    "and that arm has something to detect: the latched learner's read returns "
+    "the priced plan on every install class",
+    all(_dsp_same_plan(_dsp_solve(*_dsp_table.planner_pairs(), **kw), _dsp_priced[n])
+        for n, kw in _DSP_INSTALLS.items()),
+)
+
+
 sys.exit(R.close("FEATURE CHECKS"))
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.3f0ec24b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.3f0ec24b.json
new file mode 100644
index 0000000000..7ad128228f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.3f0ec24b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs BOOLOP 3f0ec24b",
+  "killed_by": "tests/features.py",
+  "old": "        if self._outage_recovery_active(now) and not np.isfinite(threshold):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if self._outage_recovery_active(now) or not np.isfinite(threshold):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.855f1fe1.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.855f1fe1.json
deleted file mode 100644
index 730dc42456..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.BOOLOP.855f1fe1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs BOOLOP 855f1fe1",
-  "killed_by": "tests/features.py",
-  "old": "        if self._outage_recovery_active(dt_util.now()) and not np.isfinite(threshold):",
-  "reason": "Recorded by hand for R9-EG-B1 (#1736) on the branch worktree, 2026-10-04, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS; green on CI). The drive is mutation_table's own pool, mutant application, driver invocation and kill rule, run with the red baseline kept: a kill is a failing-check count the unmutated baseline does not already have, here against 1913f0dd736cb66b800b5eabfa6973a917459d83: BOOLOP (`if self._outage_recovery_active(dt_util.now()) or not np.isfinite(threshold):`) took tests/features.py from rc=1 failed=2 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.3f0ec24b.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.3f0ec24b.json
new file mode 100644
index 0000000000..98e0d67655
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.3f0ec24b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs GUARD_OFF 3f0ec24b",
+  "killed_by": "tests/features.py",
+  "old": "        if self._outage_recovery_active(now) and not np.isfinite(threshold):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.855f1fe1.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.855f1fe1.json
deleted file mode 100644
index 68a52c8a16..0000000000
--- a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._solve_hubs.GUARD_OFF.855f1fe1.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._solve_hubs GUARD_OFF 855f1fe1",
-  "killed_by": "tests/features.py",
-  "old": "        if self._outage_recovery_active(dt_util.now()) and not np.isfinite(threshold):",
-  "reason": "Recorded by hand for R9-EG-B1 (#1736) on the branch worktree, 2026-10-04, because `mutation_table.py --pin-killed` refuses on this machine (tests/features.py's baseline is red for the environment: R9-F2.1 P3, BLAS; green on CI). The drive is mutation_table's own pool, mutant application, driver invocation and kill rule, run with the red baseline kept: a kill is a failing-check count the unmutated baseline does not already have, here against 1913f0dd736cb66b800b5eabfa6973a917459d83: GUARD_OFF (`if False:`) took tests/features.py from rc=1 failed=2 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/_with_placement_ban.RETURN_DEL.d48232ce.json b/tests/mutation_ledger/killed_by/dhw_planner.py/_with_placement_ban.RETURN_DEL.d48232ce.json
new file mode 100644
index 0000000000..824fb6b1d7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/_with_placement_ban.RETURN_DEL.d48232ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:_with_placement_ban RETURN_DEL d48232ce",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    return forced_off if ban is None else _forced_off_with(forced_off, ban, n_steps)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/@module.CONST.eef42148.json b/tests/mutation_ledger/killed_by/duty_legs.py/@module.CONST.eef42148.json
new file mode 100644
index 0000000000..77e37b81a7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/@module.CONST.eef42148.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:<module> CONST eef42148",
+  "killed_by": "tests/features.py",
+  "old": "SPLIT_MIN_MINUTES = 5.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CONST (`SPLIT_MIN_MINUTES = 10.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=27."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.2759517c.json b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.2759517c.json
new file mode 100644
index 0000000000..ac236d62b2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.2759517c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:_runs CMP_BOUND 2759517c",
+  "killed_by": "tests/features.py",
+  "old": "    on = kw > MIN_RUNNING_DRAW_KW",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`on = kw >= MIN_RUNNING_DRAW_KW`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.ad1b10bc.json b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.ad1b10bc.json
new file mode 100644
index 0000000000..f0a0669888
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.CMP_BOUND.ad1b10bc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:_runs CMP_BOUND ad1b10bc",
+  "killed_by": "tests/features.py",
+  "old": "    return on if floor is None else on & ~(kw < floor)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return on if floor is None else on & ~(kw <= floor)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=13."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/_runs.RETURN_DEL.ad1b10bc.json b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.RETURN_DEL.ad1b10bc.json
new file mode 100644
index 0000000000..53a11e8033
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/_runs.RETURN_DEL.ad1b10bc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:_runs RETURN_DEL ad1b10bc",
+  "killed_by": "tests/features.py",
+  "old": "    return on if floor is None else on & ~(kw < floor)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/availability.CMP_BOUND.7944d7be.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.CMP_BOUND.7944d7be.json
new file mode 100644
index 0000000000..a9bfee0d6f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.CMP_BOUND.7944d7be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability CMP_BOUND 7944d7be",
+  "killed_by": "tests/features.py",
+  "old": "    if not lost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if not lost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.7944d7be.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.7944d7be.json
new file mode 100644
index 0000000000..5fe8ddf5cc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.7944d7be.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability GUARD_OFF 7944d7be",
+  "killed_by": "tests/features.py",
+  "old": "    if not lost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.c8a3376c.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.c8a3376c.json
new file mode 100644
index 0000000000..4c0fa43148
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.GUARD_OFF.c8a3376c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability GUARD_OFF c8a3376c",
+  "killed_by": "tests/features.py",
+  "old": "    if not charged.any():",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/availability.RETURN_DEL.1e8a99b4.json b/tests/mutation_ledger/killed_by/duty_legs.py/availability.RETURN_DEL.1e8a99b4.json
new file mode 100644
index 0000000000..8b77a58bd7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/availability.RETURN_DEL.1e8a99b4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:availability RETURN_DEL 1e8a99b4",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(charged, 1.0 - lost, 1.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8cc0b854.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8cc0b854.json
new file mode 100644
index 0000000000..5b9f922606
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.8cc0b854.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs CMP_BOUND 8cc0b854",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if dhw_min <= SPLIT_MIN_MINUTES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.b7055f00.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.b7055f00.json
new file mode 100644
index 0000000000..281083ad1c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.CMP_BOUND.b7055f00.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs CMP_BOUND b7055f00",
+  "killed_by": "tests/features.py",
+  "old": "    if step_minutes - dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if step_minutes - dhw_min <= SPLIT_MIN_MINUTES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8cc0b854.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8cc0b854.json
new file mode 100644
index 0000000000..8bf42582fa
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.8cc0b854.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs GUARD_OFF 8cc0b854",
+  "killed_by": "tests/features.py",
+  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.b7055f00.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.b7055f00.json
new file mode 100644
index 0000000000..a78fee0176
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.GUARD_OFF.b7055f00.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs GUARD_OFF b7055f00",
+  "killed_by": "tests/features.py",
+  "old": "    if step_minutes - dhw_min < SPLIT_MIN_MINUTES:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json
new file mode 100644
index 0000000000..fa73675963
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/both_step_legs.RETURN_DEL.123675c1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:both_step_legs RETURN_DEL 123675c1",
+  "killed_by": "tests/features.py",
+  "old": "    return ((\"dhw\", dhw_min), (\"space\", step_minutes - dhw_min))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.CLAMP_DROP.e5a67d12.json b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.CLAMP_DROP.e5a67d12.json
new file mode 100644
index 0000000000..26a3168afc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.CLAMP_DROP.e5a67d12.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:delivered_space CLAMP_DROP e5a67d12",
+  "killed_by": "tests/features.py",
+  "old": "    delivered: np.ndarray = np.maximum(0.0, space_kw - (1.0 - avail) * (space_kw + dhw_kw))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`delivered: np.ndarray = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.GUARD_OFF.756d2076.json b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.GUARD_OFF.756d2076.json
new file mode 100644
index 0000000000..5fbb4f2f56
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.GUARD_OFF.756d2076.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:delivered_space GUARD_OFF 756d2076",
+  "killed_by": "tests/features.py",
+  "old": "    if floor is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.RETURN_DEL.e6a4147a.json b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.RETURN_DEL.e6a4147a.json
new file mode 100644
index 0000000000..f14739b0f2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/delivered_space.RETURN_DEL.e6a4147a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:delivered_space RETURN_DEL e6a4147a",
+  "killed_by": "tests/features.py",
+  "old": "    return delivered",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.c6cf73a1.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.c6cf73a1.json
new file mode 100644
index 0000000000..a4272a0a60
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.c6cf73a1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends CMP_BOUND c6cf73a1",
+  "killed_by": "tests/features.py",
+  "old": "    to_space = both & (dhw_min < SPLIT_MIN_MINUTES)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`to_space = both & (dhw_min <= SPLIT_MIN_MINUTES)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.d90f16a9.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.d90f16a9.json
new file mode 100644
index 0000000000..f780f7f6c2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.CMP_BOUND.d90f16a9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends CMP_BOUND d90f16a9",
+  "killed_by": "tests/features.py",
+  "old": "    to_dhw = both & ~to_space & (step_minutes - dhw_min < SPLIT_MIN_MINUTES)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`to_dhw = both & ~to_space & (step_minutes - dhw_min <= SPLIT_MIN_MINUTES)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json
new file mode 100644
index 0000000000..cac585d618
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/leg_ends.RETURN_DEL.6b97afd0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:leg_ends RETURN_DEL 6b97afd0",
+  "killed_by": "tests/features.py",
+  "old": "    return np.where(two, DHW, single), np.where(two, SPACE, single), two",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.CLAMP_DROP.2b3e0bf8.json b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.CLAMP_DROP.2b3e0bf8.json
new file mode 100644
index 0000000000..f52deda746
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.CLAMP_DROP.2b3e0bf8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:lost_share CLAMP_DROP 2b3e0bf8",
+  "killed_by": "tests/features.py",
+  "old": "    return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (1.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.RETURN_DEL.2b3e0bf8.json b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.RETURN_DEL.2b3e0bf8.json
new file mode 100644
index 0000000000..fc492f71dd
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/lost_share.RETURN_DEL.2b3e0bf8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:lost_share RETURN_DEL 2b3e0bf8",
+  "killed_by": "tests/features.py",
+  "old": "    return min(1.0, stop_probability[0] * off_seconds[0] / (step_minutes * 60.0))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.BOOLOP.8175604f.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.BOOLOP.8175604f.json
new file mode 100644
index 0000000000..2e112ac8dc
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.BOOLOP.8175604f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair BOOLOP 8175604f",
+  "killed_by": "tests/features.py",
+  "old": "    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`a, b = (max(v, 0.0) if math.isfinite(v) or v <= upper else 0.0 for v in pair)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CLAMP_DROP.8175604f.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CLAMP_DROP.8175604f.json
new file mode 100644
index 0000000000..eac72596e1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CLAMP_DROP.8175604f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair CLAMP_DROP 8175604f",
+  "killed_by": "tests/features.py",
+  "old": "    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`a, b = ((v) if math.isfinite(v) and v <= upper else 0.0 for v in pair)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CMP_BOUND.8175604f.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CMP_BOUND.8175604f.json
new file mode 100644
index 0000000000..d51ffb60ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.CMP_BOUND.8175604f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair CMP_BOUND 8175604f",
+  "killed_by": "tests/features.py",
+  "old": "    a, b = (max(v, 0.0) if math.isfinite(v) and v <= upper else 0.0 for v in pair)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`a, b = (max(v, 0.0) if math.isfinite(v) and v < upper else 0.0 for v in pair)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.GUARD_OFF.f30e646b.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.GUARD_OFF.f30e646b.json
new file mode 100644
index 0000000000..ae5de54bf4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.GUARD_OFF.f30e646b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair GUARD_OFF f30e646b",
+  "killed_by": "tests/features.py",
+  "old": "    if len(pair) != 2:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.RETURN_DEL.8a3f76e4.json b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.RETURN_DEL.8a3f76e4.json
new file mode 100644
index 0000000000..0f37aa2b17
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/priced_pair.RETURN_DEL.8a3f76e4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:priced_pair RETURN_DEL 8a3f76e4",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return a, b",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.311fd6bd.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.311fd6bd.json
new file mode 100644
index 0000000000..cd4f589a5b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.311fd6bd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom CLAMP_DROP 311fd6bd",
+  "killed_by": "tests/features.py",
+  "old": "    charged: np.ndarray = np.maximum(0.0, avail * p_max - dhw_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`charged: np.ndarray = (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.f6750244.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.f6750244.json
new file mode 100644
index 0000000000..87c84d51eb
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.CLAMP_DROP.f6750244.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom CLAMP_DROP f6750244",
+  "killed_by": "tests/plan_view.py",
+  "old": "        return np.maximum(0.0, p_max - dhw_kw)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`return (0.0)`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.GUARD_OFF.bc40ec59.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.GUARD_OFF.bc40ec59.json
new file mode 100644
index 0000000000..7a9c12aa4b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.GUARD_OFF.bc40ec59.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom GUARD_OFF bc40ec59",
+  "killed_by": "tests/plan_view.py",
+  "old": "    if avail is None or floor is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.RETURN_DEL.013354f1.json b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.RETURN_DEL.013354f1.json
new file mode 100644
index 0000000000..ec5f61af9b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/space_headroom.RETURN_DEL.013354f1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:space_headroom RETURN_DEL 013354f1",
+  "killed_by": "tests/features.py",
+  "old": "    return charged",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.0b540c5f.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.0b540c5f.json
new file mode 100644
index 0000000000..11cd93ab9a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.0b540c5f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban CMP_BOUND 0b540c5f",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[1] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stop_probability[1] >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.44023c38.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.44023c38.json
new file mode 100644
index 0000000000..61fb080bd0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.CMP_BOUND.44023c38.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban CMP_BOUND 44023c38",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[0] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stop_probability[0] >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.0b540c5f.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.0b540c5f.json
new file mode 100644
index 0000000000..c397ca41c3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.0b540c5f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban GUARD_OFF 0b540c5f",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[1] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.44023c38.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.44023c38.json
new file mode 100644
index 0000000000..29c4b165af
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.GUARD_OFF.44023c38.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban GUARD_OFF 44023c38",
+  "killed_by": "tests/features.py",
+  "old": "    if stop_probability[0] > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.RETURN_DEL.1f9c227b.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.RETURN_DEL.1f9c227b.json
new file mode 100644
index 0000000000..bfe95e968e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_ban.RETURN_DEL.1f9c227b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_ban RETURN_DEL 1f9c227b",
+  "killed_by": "tests/features.py",
+  "old": "    return ban",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CLAMP_DROP.22691b9b.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CLAMP_DROP.22691b9b.json
new file mode 100644
index 0000000000..c15ca2b5b9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CLAMP_DROP.22691b9b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch CLAMP_DROP 22691b9b",
+  "killed_by": "tests/features.py",
+  "old": "    across = stops * np.minimum(level[_BEFORE], level[_AFTER])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`across = stops * (level[_BEFORE])`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CMP_BOUND.ba504464.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CMP_BOUND.ba504464.json
new file mode 100644
index 0000000000..f624b4f139
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.CMP_BOUND.ba504464.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch CMP_BOUND ba504464",
+  "killed_by": "tests/features.py",
+  "old": "    if p_max <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if p_max < 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.ba504464.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.ba504464.json
new file mode 100644
index 0000000000..b672965db5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.GUARD_OFF.ba504464.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch GUARD_OFF ba504464",
+  "killed_by": "tests/features.py",
+  "old": "    if p_max <= 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.RETURN_DEL.8d49450a.json b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.RETURN_DEL.8d49450a.json
new file mode 100644
index 0000000000..873a7bf127
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_legs.py/switch_weights_batch.RETURN_DEL.8d49450a.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_legs.py:switch_weights_batch RETURN_DEL 8d49450a",
+  "killed_by": "tests/features.py",
+  "old": "    return row_sums(np.concatenate([inside, across], axis=1)) / p_max",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json
new file mode 100644
index 0000000000..a620063d0e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.book.GUARD_OFF.3e106b06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.book GUARD_OFF 3e106b06",
+  "killed_by": "tests/features.py",
+  "old": "        if self.n > N_CAP:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
new file mode 100644
index 0000000000..a10a5b3c92
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/DutySwitchLearner.planner_pairs.RETURN_DEL.fc67f05d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:DutySwitchLearner.planner_pairs RETURN_DEL fc67f05d",
+  "killed_by": "tests/features.py",
+  "old": "        return (read[0].p, read[1].p), (read[0].median_off_s or 0.0, read[1].median_off_s or 0.0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
new file mode 100644
index 0000000000..5d0d9757be
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/planner_fields.RETURN_DEL.77cc0eae.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:planner_fields RETURN_DEL 77cc0eae",
+  "killed_by": "tests/features.py",
+  "old": "    return {\"duty_switch_stop_probability\": stops, \"duty_switch_off_seconds\": off_s}",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.CLAMP_DROP.f79618d7.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.CLAMP_DROP.f79618d7.json
deleted file mode 100644
index 653d27989e..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._co_optimize.CLAMP_DROP.f79618d7.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._co_optimize CLAMP_DROP f79618d7",
-  "killed_by": "tests/env_drift.py",
-  "old": "            headroom = np.maximum(0.0, p_max - dhw_power)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`headroom = (0.0)`) took tests/env_drift.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.4ad2d781.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.4ad2d781.json
deleted file mode 100644
index 8829d1f7f0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._solve_space.CLAMP_DROP.4ad2d781.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._solve_space CLAMP_DROP 4ad2d781",
-  "killed_by": "tests/plan_view.py",
-  "old": "        headroom = np.maximum(0.0, p_max - dhw_plan)",
-  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`headroom = (0.0)`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.11566350.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.11566350.json
new file mode 100644
index 0000000000..a5ed8ad60c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.11566350.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 11566350",
+  "killed_by": "tests/features.py",
+  "old": "            if score < base - 1e-9:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if score <= base - 1e-9:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.1cd8047f.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.1cd8047f.json
new file mode 100644
index 0000000000..0f8c0eb779
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.1cd8047f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 1cd8047f",
+  "killed_by": "tests/features.py",
+  "old": "            else np.nan_to_num(_padded(h.dhw_pins, ban.size)) >= 0.5",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`else np.nan_to_num(_padded(h.dhw_pins, ban.size)) > 0.5`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json
new file mode 100644
index 0000000000..fa48feb1d0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.7b6d787d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 7b6d787d",
+  "killed_by": "tests/features.py",
+  "old": "    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or not opt.config.cycling_cost >= 0 or opt.model.params.dhw_store.combi:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json
new file mode 100644
index 0000000000..6cf8195176
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.95d10ca9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND 95d10ca9",
+  "killed_by": "tests/features.py",
+  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CMP_BOUND.76b8fad3.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.fdd63b1a.json
similarity index 55%
rename from tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CMP_BOUND.76b8fad3.json
rename to tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.fdd63b1a.json
index 7c9f2e5ea1..77e81068d3 100644
--- a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CMP_BOUND.76b8fad3.json
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.CMP_BOUND.fdd63b1a.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state CMP_BOUND 76b8fad3",
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches CMP_BOUND fdd63b1a",
   "killed_by": "tests/features.py",
-  "old": "        if need > 0.0 else held.buffer_tank_temperature",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if need >= 0.0 else held.buffer_tank_temperature`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "            not np.any(plan.schedule[ban & ~forced_on] > 0)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`not np.any(plan.schedule[ban & ~forced_on] >= 0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
 }
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.11566350.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.11566350.json
new file mode 100644
index 0000000000..195f6f6c2b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.11566350.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 11566350",
+  "killed_by": "tests/features.py",
+  "old": "            if score < base - 1e-9:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json
new file mode 100644
index 0000000000..ba5f280182
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.7b6d787d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 7b6d787d",
+  "killed_by": "tests/plan_view.py",
+  "old": "    if stops is None or not opt.config.cycling_cost > 0 or opt.model.params.dhw_store.combi:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json
new file mode 100644
index 0000000000..e5059f5c83
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.GUARD_OFF.95d10ca9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches GUARD_OFF 95d10ca9",
+  "killed_by": "tests/structure.py",
+  "old": "    if kept_requirement is None or not duty_legs.switch_weight(shipped, tank, stops, p_max, floor) > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.98a00538.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.98a00538.json
new file mode 100644
index 0000000000..0fbe7e8d76
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.98a00538.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches RETURN_DEL 98a00538",
+  "killed_by": "tests/features.py",
+  "old": "                return candidate_space, plan.schedule, candidate_status",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.b66b6c96.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.b66b6c96.json
new file mode 100644
index 0000000000..a4ef8f8ec0
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.RETURN_DEL.b66b6c96.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches RETURN_DEL b66b6c96",
+  "killed_by": "tests/features.py",
+  "old": "    return incumbent",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.first_short.RETURN_DEL.d8594a7d.json b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.first_short.RETURN_DEL.d8594a7d.json
new file mode 100644
index 0000000000..3059c08a57
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_avoid_priced_switches.first_short.RETURN_DEL.d8594a7d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_avoid_priced_switches.first_short RETURN_DEL d8594a7d",
+  "killed_by": "tests/features.py",
+  "old": "            return temps, step",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_held_unreachable.RETURN_DEL.ebd24b04.json b/tests/mutation_ledger/killed_by/optimizer.py/_held_unreachable.RETURN_DEL.ebd24b04.json
new file mode 100644
index 0000000000..2f21f5a74e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_held_unreachable.RETURN_DEL.ebd24b04.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_held_unreachable RETURN_DEL ebd24b04",
+  "killed_by": "tests/features.py",
+  "old": "    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json b/tests/mutation_ledger/killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json
new file mode 100644
index 0000000000..ffc4d68e52
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_held_zones.CLAMP_DROP.afb64a55.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_held_zones CLAMP_DROP afb64a55",
+  "killed_by": "tests/features.py",
+  "old": "        slab_temperature=temp + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`slab_temperature=temp + (0.0) / model.params.slab_heat_transfer_floored,`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.CMP_BOUND.5a0db715.json b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.CMP_BOUND.5a0db715.json
new file mode 100644
index 0000000000..3a61ffa90f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.CMP_BOUND.5a0db715.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_priced_stops CMP_BOUND 5a0db715",
+  "killed_by": "tests/features.py",
+  "old": "    return stops if max(stops) > 0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return stops if max(stops) >= 0 else None`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.RETURN_DEL.5a0db715.json b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.RETURN_DEL.5a0db715.json
new file mode 100644
index 0000000000..76b7d07cbf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_priced_stops.RETURN_DEL.5a0db715.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_priced_stops RETURN_DEL 5a0db715",
+  "killed_by": "tests/features.py",
+  "old": "    return stops if max(stops) > 0 else None",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.dfc20e22.json b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.dfc20e22.json
new file mode 100644
index 0000000000..956c2f31c5
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.GUARD_OFF.dfc20e22.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received GUARD_OFF dfc20e22",
+  "killed_by": "tests/features.py",
+  "old": "    if avail is None or dhw is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
new file mode 100644
index 0000000000..f1bc862fd8
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_shipped_and_received.RETURN_DEL.d631f182.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_shipped_and_received RETURN_DEL d631f182",
+  "killed_by": "tests/features.py",
+  "old": "    return space, dhw, duty_legs.delivered_space(space, dhw, avail, _duty_floor(opt))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.CLAMP_DROP.13234cde.json b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.CLAMP_DROP.13234cde.json
new file mode 100644
index 0000000000..1ad9e15a67
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.CLAMP_DROP.13234cde.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability CLAMP_DROP 13234cde",
+  "killed_by": "tests/features.py",
+  "old": "        np.minimum(start, np.maximum(0.0, p_max - dhw_plan)),",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`(start),`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.GUARD_OFF.1bb04241.json b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.GUARD_OFF.1bb04241.json
new file mode 100644
index 0000000000..1c267e14ee
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.GUARD_OFF.1bb04241.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability GUARD_OFF 1bb04241",
+  "killed_by": "tests/plan_view.py",
+  "old": "    if stops is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json
new file mode 100644
index 0000000000..b8c8493e56
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_stop_availability.RETURN_DEL.9325b601.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_stop_availability RETURN_DEL 9325b601",
+  "killed_by": "tests/structure.py",
+  "old": "    return duty_legs.availability(space, tank, lost, _duty_floor(opt))",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/structure.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.RETURN_DEL.0bf003bf.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.RETURN_DEL.0bf003bf.json
new file mode 100644
index 0000000000..fd1ab2e18d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.RETURN_DEL.0bf003bf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn RETURN_DEL 0bf003bf",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return switch_cost",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
new file mode 100644
index 0000000000..318c16b96c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.CMP_BOUND.b0a491aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost CMP_BOUND b0a491aa",
+  "killed_by": "tests/features.py",
+  "old": "        if stops is None or dhw is None or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if stops is None or dhw is None or not cost >= 0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
new file mode 100644
index 0000000000..899cb46f4a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.GUARD_OFF.b0a491aa.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost GUARD_OFF b0a491aa",
+  "killed_by": "tests/plan_view.py",
+  "old": "        if stops is None or dhw is None or not cost > 0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.RETURN_DEL.0f24df73.json b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.RETURN_DEL.0f24df73.json
new file mode 100644
index 0000000000..0ec1daa260
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_switch_cost_fn.switch_cost.RETURN_DEL.0f24df73.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_switch_cost_fn.switch_cost RETURN_DEL 0f24df73",
+  "killed_by": "tests/features.py",
+  "old": "        return term if np.ndim(space) == 2 else float(term[0])",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.5c7d4c36.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.5c7d4c36.json
deleted file mode 100644
index d98970a2c9..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.5c7d4c36.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state CLAMP_DROP 5c7d4c36",
-  "killed_by": "tests/stress.py",
-  "old": "        slab_temperature=target + max(0.0, q_floor) / model.params.slab_heat_transfer_floored,",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against 413944b6772fa7f2f38cef7ea2f667a64d79251a: CLAMP_DROP (`slab_temperature=target + (0.0) / model.params.slab_heat_transfer_floored,`) took tests/stress.py from rc=0 failed=0 to rc=1 failed=1."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.c7dd28c1.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.c7dd28c1.json
new file mode 100644
index 0000000000..6074494c36
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.CLAMP_DROP.c7dd28c1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state CLAMP_DROP c7dd28c1",
+  "killed_by": "tests/features.py",
+  "old": "        lo, hi = min(outdoor, target), target",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`lo, hi = (outdoor), target`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.1ecfa785.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.1ecfa785.json
new file mode 100644
index 0000000000..2d50218447
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.1ecfa785.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state GUARD_OFF 1ecfa785",
+  "killed_by": "tests/features.py",
+  "old": "    if unreachable(held):",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.5c05badb.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.5c05badb.json
deleted file mode 100644
index 6b9fa738c0..0000000000
--- a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.GUARD_OFF.5c05badb.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state GUARD_OFF 5c05badb",
-  "killed_by": "tests/env_drift.py",
-  "old": "    if not mixing_valve.is_throttling(p.mixing_valve_mode):",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/env_drift.py from rc=0 failed=0 to rc=1 failed=5."
-}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.BOOLOP.1b4f8e62.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.BOOLOP.1b4f8e62.json
new file mode 100644
index 0000000000..80cbda2495
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.BOOLOP.1b4f8e62.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at BOOLOP 1b4f8e62",
+  "killed_by": "tests/features.py",
+  "old": "        if valved and (h_need := need(h)) > 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`if valved or (h_need := need(h)) > 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.CMP_BOUND.1b4f8e62.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.CMP_BOUND.1b4f8e62.json
new file mode 100644
index 0000000000..62565cb378
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.CMP_BOUND.1b4f8e62.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at CMP_BOUND 1b4f8e62",
+  "killed_by": "tests/features.py",
+  "old": "        if valved and (h_need := need(h)) > 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if valved and (h_need := need(h)) >= 0.0:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.GUARD_OFF.1b4f8e62.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.GUARD_OFF.1b4f8e62.json
new file mode 100644
index 0000000000..7485dcd3ea
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.GUARD_OFF.1b4f8e62.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at GUARD_OFF 1b4f8e62",
+  "killed_by": "tests/features.py",
+  "old": "        if valved and (h_need := need(h)) > 0.0:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.RETURN_DEL.b87482f7.json b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.RETURN_DEL.b87482f7.json
new file mode 100644
index 0000000000..efc2598a06
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_thermostat_held_state.held_at.RETURN_DEL.b87482f7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_thermostat_held_state.held_at RETURN_DEL b87482f7",
+  "killed_by": "tests/plan_view.py",
+  "old": "        return h",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.GUARD_OFF.ee2cd78c.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.GUARD_OFF.ee2cd78c.json
new file mode 100644
index 0000000000..9e0692cadf
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.GUARD_OFF.ee2cd78c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_stop_availability GUARD_OFF ee2cd78c",
+  "killed_by": "tests/features.py",
+  "old": "    if avail is None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.RETURN_DEL.f73e18ce.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.RETURN_DEL.f73e18ce.json
new file mode 100644
index 0000000000..7d6d925b39
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_stop_availability.RETURN_DEL.f73e18ce.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_stop_availability RETURN_DEL f73e18ce",
+  "killed_by": "tests/features.py",
+  "old": "    return headroom, partial(objective, avail=avail), partial(objective_batch, avail=avail)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_with_switch_cost.RETURN_DEL.65006bb8.json b/tests/mutation_ledger/killed_by/optimizer.py/_with_switch_cost.RETURN_DEL.65006bb8.json
new file mode 100644
index 0000000000..bbb19961f6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_with_switch_cost.RETURN_DEL.65006bb8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_with_switch_cost RETURN_DEL 65006bb8",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return level_cost if switch_cost is None else level_cost + switch_cost",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/@module.CONST.eef42148.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/@module.CONST.eef42148.json
deleted file mode 100644
index 8634d02df4..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/@module.CONST.eef42148.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:<module> CONST eef42148",
-  "killed_by": "tests/features.py",
-  "old": "SPLIT_MIN_MINUTES = 5.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cfa2cb07b1474ed3b405787d3b41978e9be61d2f: CONST (`SPLIT_MIN_MINUTES = 10.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
new file mode 100644
index 0000000000..7674632b2b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arbitrate.GUARD_OFF.87a4cba9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arbitrate GUARD_OFF 87a4cba9",
+  "killed_by": "tests/features.py",
+  "old": "        if held.written or held.retry or held.space_before is not None:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.4f254e46.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
similarity index 67%
rename from tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.4f254e46.json
rename to tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
index 076c143a46..d52a0f3f66 100644
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.4f254e46.json
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.GUARD_OFF.bc2b348d.json
@@ -1,6 +1,6 @@
 {
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share GUARD_OFF 4f254e46",
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space GUARD_OFF bc2b348d",
   "killed_by": "tests/features.py",
-  "old": "    if PLAN_STEP_MINUTES - dhw_min < SPLIT_MIN_MINUTES:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+  "old": "    if own:",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
 }
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
new file mode 100644
index 0000000000..eedc551b94
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_arm_space.RETURN_DEL.ee5d5b70.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_arm_space RETURN_DEL ee5d5b70",
+  "killed_by": "tests/features.py",
+  "old": "    return await off_restore.async_arm(inp.hass, entry, inp.config, CONSUMER, baseline_c=baseline)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=20."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
new file mode 100644
index 0000000000..6150d6a294
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.BOOLOP.dd8cf122.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back BOOLOP dd8cf122",
+  "killed_by": "tests/guard_pins.py",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: BOOLOP (`return slot == \"space_setpoint\" or not await _arm_space(inp, entry, held, entity, now)`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
new file mode 100644
index 0000000000..febd8f790b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_held_back.RETURN_DEL.dd8cf122.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_held_back RETURN_DEL dd8cf122",
+  "killed_by": "tests/features.py",
+  "old": "    return slot == \"space_setpoint\" and not await _arm_space(inp, entry, held, entity, now)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=14."
+}
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
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json
new file mode 100644
index 0000000000..ac6a436217
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.3eede229.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share CMP_BOUND 3eede229",
+  "killed_by": "tests/features.py",
+  "old": "    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`return legs[0][0] if (now - result.timestamps[i]) <= first_ends else legs[-1][0]`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.4f254e46.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.4f254e46.json
deleted file mode 100644
index a6d4dc03ea..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.CMP_BOUND.4f254e46.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share CMP_BOUND 4f254e46",
-  "killed_by": "tests/features.py",
-  "old": "    if PLAN_STEP_MINUTES - dhw_min < SPLIT_MIN_MINUTES:",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`if PLAN_STEP_MINUTES - dhw_min <= SPLIT_MIN_MINUTES:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.8cc0b854.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.8cc0b854.json
deleted file mode 100644
index f4206bfefb..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.GUARD_OFF.8cc0b854.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share GUARD_OFF 8cc0b854",
-  "killed_by": "tests/features.py",
-  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cfa2cb07b1474ed3b405787d3b41978e9be61d2f: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.0008eae9.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.0008eae9.json
deleted file mode 100644
index ccfca9bee7..0000000000
--- a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.0008eae9.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share RETURN_DEL 0008eae9",
-  "killed_by": "tests/features.py",
-  "old": "    return \"dhw\" if (now - result.timestamps[i]) < timedelta(minutes=dhw_min) else \"space\"",
-  "reason": "Recorded by `mutation_table.py --pin-killed` against cfa2cb07b1474ed3b405787d3b41978e9be61d2f: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
-}
diff --git a/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json
new file mode 100644
index 0000000000..1af67f301a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_arbiter.py/_share.RETURN_DEL.3eede229.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share RETURN_DEL 3eede229",
+  "killed_by": "tests/features.py",
+  "old": "    return legs[0][0] if (now - result.timestamps[i]) < first_ends else legs[-1][0]",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=11."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/valve_top_draw.RETURN_DEL.21d92eb4.json b/tests/mutation_ledger/killed_by/thermal_model.py/valve_top_draw.RETURN_DEL.21d92eb4.json
new file mode 100644
index 0000000000..ea6965068f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/valve_top_draw.RETURN_DEL.21d92eb4.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:valve_top_draw RETURN_DEL 21d92eb4",
+  "killed_by": "tests/features.py",
+  "old": "    return _circuit_draw(circuits, model.params.buffer_max_temp)",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json b/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json
new file mode 100644
index 0000000000..2f2183aa51
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/duty_switch.py/Direction.book.CMP_BOUND.3e106b06.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.book CMP_BOUND 3e106b06",
+  "old": "        if self.n > N_CAP:",
+  "reason": "Equivalent (CMP_BOUND, `self.n > N_CAP` -> `self.n >= N_CAP`). The two differ only at n == N_CAP exactly, where the guarded body computes scale = N_CAP / self.n = 1.0 and multiplies k and kept_w by it: IEEE multiplication by 1.0 returns its operand, so both counts, and the latch read after them, are the same floats on either branch. Measured by the R10-DUTY-SWITCH-PLANNER-PRICE fixer's diff drive (tools/audit/seat/mutant_run.py --diff over the section harness dev/audit/harnesses/r10_duty_switch_price_section.py): SURVIVED, while the same line's GUARD_OFF and the section's cap mutants (no cap, the cap scaling the stops alone, three times the on-threshold) are each killed by the cap checks.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.4bcd4baf.json b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.4bcd4baf.json
new file mode 100644
index 0000000000..19f0e79441
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/@module.CONST.4bcd4baf.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:<module> CONST 4bcd4baf",
+  "old": "_HELD_BISECTIONS = 40",
+  "reason": "Equivalent to every reader's resolution, and measured (CONST, 40 -> 80). `_HELD_BISECTIONS` is the bisection count `_thermostat_held_state` uses to find the highest zone temperature the reference step can hold under both of `_held_unreachable`'s bounds. At 40 the bracket is 2**-40 of the outdoor-to-target span, under 4e-11 K for a 46 K span; 80 only narrows it further. Measured against the group's block (`features_block.py` from `# --- R10-SAV-VALUATION-RESIDUE: stored heat` to `# --- R10-WATER-SETPOINT-FEEDBACK`): `ALL 10 FEATURES BLOCK PASSED` under the mutant. No reader of the held state (the booked reference and the start's stored-heat settlement) resolves a change that size.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/optimizer.py/_held_unreachable.CMP_BOUND.ebd24b04.json b/tests/mutation_ledger/survivor_triage/optimizer.py/_held_unreachable.CMP_BOUND.ebd24b04.json
new file mode 100644
index 0000000000..f5f9d850b5
--- /dev/null
+++ b/tests/mutation_ledger/survivor_triage/optimizer.py/_held_unreachable.CMP_BOUND.ebd24b04.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_held_unreachable CMP_BOUND ebd24b04",
+  "old": "    return bool(power_for_heat_per_cop_kw(p, made / cop) > p.max_electrical_power)",
+  "reason": "Equivalent on every reachable input, and measured (CMP_BOUND, `>` -> `>=`). The two arms differ only where the steady heat's draw equals `max_electrical_power` to the last bit, which is the pump-bound equilibrium itself. At the target the mutant then bisects and lands within 2**-40 of the span below it; inside the bisection either branch keeps a bracket holding that equilibrium. Both move the held zones by under the final bracket, 4e-11 K. The group's block (the 4 kW and 9 kW pumps at -25 C, valved and not, both zonings) reads `ALL 10 FEATURES BLOCK PASSED` under the mutant.",
+  "verdict": "equivalent"
+}
diff --git a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_share.CMP_BOUND.8cc0b854.json b/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_share.CMP_BOUND.8cc0b854.json
deleted file mode 100644
index 994b799f7b..0000000000
--- a/tests/mutation_ledger/survivor_triage/pump_arbiter.py/_share.CMP_BOUND.8cc0b854.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/pump_arbiter.py:_share CMP_BOUND 8cc0b854",
-  "old": "    if dhw_min < SPLIT_MIN_MINUTES:",
-  "reason": "R10 mutation-anchor: the `killed_by: tests/entities.py` pin was vacuous. Re-driven at 0be5e2de5 by dev/audit/harnesses/r10_anchor_vacuous.py with the 2 ledger row(s) the mutant itself makes stale hidden from its tree, 0 of 1 site(s) were killed by tests/entities.py: the recorded kill was a check refusing a ledger row the mutant made stale (the --anchor self-test, or the survivor_triage staleness check), not one that saw the mutation. Was: Recorded by `mutation_table.py --drain` against 816547efe270a08e18e3b92f52185fe8c1fee2ef: CMP_BOUND (`if dhw_min <= SPLIT_MIN_MINUTES:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1. Not re-driven here against the other drivers in its closure, so a gap until one is shown to kill it.",
-  "verdict": "gap"
-}
diff --git a/tests/structure_budgets.json b/tests/structure_budgets.json
index 34471a37be..c9a4648ed9 100644
--- a/tests/structure_budgets.json
+++ b/tests/structure_budgets.json
@@ -1,5 +1,5 @@
 {
- "class_excess_loc": 17522,
+ "class_excess_loc": 17514,
  "const_modules_over_50": 3,
  "coordinator_attrs": 139,
  "coordinator_multiassigned_attrs": 108,
@@ -16,6 +16,6 @@
  "methods_over_150": 15,
  "methods_over_200": 8,
  "name_kept_members": 38,
- "recorded_at": "8c10361eb1fea539dc5acb8f7442eac2810faa47",
+ "recorded_at": "005eed2573da9e946fa4838de147401d0ff36cc1",
  "seam_cut_total": 421
 }
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 72b0b6dca2..c89b3c07f0 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -126,7 +126,7 @@ standing-seat liveness step keep the seats alive.
 - [`sweep_gantt.py`](instruments/sweep_gantt.py.md) — compares the live state to the plan's Gantt and prints each unacknowledged `GANTT-SLIP`
 - [`verdict_audit.py`](instruments/verdict_audit.py.md) — maps every open PR to its latest verdict and holder; prints `UNHELD` lines
 - [`survivor_list.py`](instruments/survivor_list.py.md) — refuses a `mutation-vacuous` verdict that omits a survivor its evidence's driver output reports; `bus.sh push-verdict` runs it
-- [`bare_array.py`](instruments/bare_array.py.md) — refuses a bare `"${name[@]}"` in any tracked `tools/**/*.sh` script (a sourced library runs under its caller's `set -u`), which macOS bash 3.2 dies on when the array is empty (`--check`, `--self-test`)
+- [`bare_array.py`](instruments/bare_array.py.md) — refuses two macOS bash 3.2 failures in tracked `tools/**/*.sh`: a bare `"${name[@]}"` (empty under a caller's `set -u`) and a `case` pattern lacking its `(` in `$( )` (`--check`, `--self-test`)
 - [`tmp_paths.py`](instruments/tmp_paths.py.md) — refuses a tracked script, workflow or decision record that depends on a temp or machine path (`--check`, `--self-test`)
 - [`update_pr.sh`](instruments/update_pr.sh.md) — brings an open PR branch to its head + a code SHA (merge) + origin/main (merge), adds the PR's own delivery row when the head lacks it (`delivery_row.sh`), prefixes ## Head with what happened, pushes as `hpo-author`
 - [`wt_sync.sh`](instruments/wt_sync.sh.md) — snapshots every worktree whose state is not already on origin (unpushed commits, uncommitted or untracked files) to `origin/wip-sync/<slug>`
diff --git a/tools/audit/seat/bare_array.py b/tools/audit/seat/bare_array.py
index 1d3386a916..676db44d89 100644
--- a/tools/audit/seat/bare_array.py
+++ b/tools/audit/seat/bare_array.py
@@ -1,5 +1,5 @@
 #!/usr/bin/env python3
-"""Refuse a bare `"${name[@]}"` in a tracked tools/ shell script.
+"""Refuse two bash-3.2-only failures in a tracked tools/ shell script.
 
     python3 -I tools/audit/seat/bare_array.py --check [--ref <commit>]
     python3 -I tools/audit/seat/bare_array.py --self-test
@@ -24,6 +24,19 @@ the mutant line by that marker at the line's end (`pr_args.sh`'s header), so a
 reason appended after the marker unanchors the mutant, and any line carrying
 one is refused. `"${name[*]}"`, `${#name[@]}` and `"${name[@]:...}"` are not
 matched.
+
+THE SECOND RULE: a `case` pattern without its leading `(` inside a `$( ... )`
+command substitution, or a `<( ... )`/`>( ... )` process substitution, quoted
+or not. Bash 3.2 finds the end of a substitution by counting parentheses, so
+the pattern's `)` closes it early: unquoted, `bash -n` fails (`tick_loop.sh`,
+PR 3520, the tick loop's own freshness check refusing on every pass); inside
+double quotes `bash -n` passes and the substitution dies at run time. Bash 4+
+parses both. The way out is the pattern's own `(`: `(func) ...;;`. A case in a
+plain `( ... )` subshell, in backquotes, or at top level is not refused, since
+3.2 parses those; there is no opt-out marker, because a refused site never
+parses on 3.2. Comments, quotes and here-document bodies are skipped (an
+unbalanced `)` in a here-document inside a substitution is a 3.2 hazard of its
+own, which this rule does not judge).
 """
 from __future__ import annotations
 
@@ -61,6 +74,88 @@ def sites(text: str) -> list[tuple[int, str]]:
     return [(n, lines[n - 1].strip()) for n in sorted(out)]
 
 
+WORD = re.compile(r"\w+")  # a word; only case, in and esac are read
+HEREDOC = re.compile(r"""<<(-?)[ \t]*(['"]?)\\?([A-Za-z_][A-Za-z0-9_]*)\2""")
+COMMAND = re.compile(r"(?:\A|[\n;&|(){!`]|(?:\A|\W)(?:then|do|else|time))[ \t]*\Z")  # `case` is a keyword here
+BEFORE, AFTER = " \t\n;&|(){`", " \t\n;&|()`"
+EOL = re.compile(r".*")  # to the end of the line, the newline left
+SQUOTE = re.compile(r"'[^']*'?")
+PATTERN = re.compile(r"""(?:\\.|'[^']*'?|"(?:\\.|[^"\\])*"?|[^)'"\\])*\)?""", re.S)  # through its `)`
+
+
+def case_sites(text: str) -> list[tuple[int, str]]:
+    """(line number, line) of each case pattern lacking `(` inside a substitution."""
+    stack: list = []  # "sub", "paren", "dq", "bt", "param", or a case: [case, head|pat|body]
+    hits, docs, i, n = set(), [], 0, len(text)
+    lines = text.splitlines()
+    while i < n:
+        c, t = text[i], stack[-1] if stack else None
+        if isinstance(t, list) and t[1] == "pat":
+            m = WORD.match(text, i)
+            if c in " \t\n":
+                i += 1
+            elif c == "#":
+                i = EOL.match(text, i).end()
+            elif m and m.group() == "esac" and text[m.end():m.end() + 1] in AFTER:
+                stack.pop()  # the keyword is then read again, in the enclosing context
+            else:
+                outer = [e for e in stack if e in ("sub", "bt")]
+                if c != "(" and outer[-1:] == ["sub"]:
+                    hits.add(text.count("\n", 0, i) + 1)
+                t[1], i = "body", PATTERN.match(text, i + (c == "(")).end()
+            continue
+        if t == "dq" and c not in "\\$`":
+            stack.pop() if c == '"' else None
+            i += 1
+            continue
+        word = text[i - 1:i] in BEFORE  # at i == 0 the slice is "", which is in any string
+        m = WORD.match(text, i) if word else None
+        kw = m.group() if m and text[m.end():m.end() + 1] in AFTER else None
+        if c == "\\":
+            i += 1
+        elif c == "}" and t == "param":
+            stack.pop()
+        elif c == "#" and word and t != "param":
+            i = EOL.match(text, i).end() - 1
+        elif c == "'" and t != "dq":
+            i = SQUOTE.match(text, i).end() - 1
+        elif c == '"':
+            stack.append("dq")
+        elif c == "`":
+            stack.pop() if t == "bt" else stack.append("bt")
+        elif text.startswith(("$(", "<(", ">("), i):
+            stack.append("sub")  # `$((` too: its `((` and `))` then pair as a paren
+            i += 1
+        elif text.startswith("${", i):
+            stack.append("param")
+        elif c == "(":
+            stack.append("paren")
+        elif c == ")" and t in ("sub", "paren"):
+            stack.pop()
+        elif HEREDOC.match(text, i) and not text.startswith("<<<", i):
+            h = HEREDOC.match(text, i)
+            docs.append(re.compile("^" + "\t*" * len(h.group(1)) + h.group(3) + "$", re.M))
+        elif c == "\n" and docs:
+            for d in docs:  # each body in turn, to its delimiter line or the end
+                e = d.search(text, i + 1)
+                i = e.end() if e else n
+            docs = []
+            continue
+        elif isinstance(t, list) and t[1] == "body" and text.startswith((";;", ";&"), i):
+            t[1] = "pat"
+            i += 2 if text.startswith(";;&", i) else 1
+        elif m:
+            if kw == "case" and COMMAND.search(text, max(0, i - 9), i):
+                stack.append(["case", "head"])
+            elif kw == "in" and t == ["case", "head"]:
+                t[1] = "pat"
+            elif kw == "esac" and t == ["case", "body"]:
+                stack.pop()
+            i = m.end() - 1
+        i += 1
+    return [(k, lines[k - 1].strip()) for k in sorted(hits)]
+
+
 def scan(ref: str | None = None) -> list[str]:
     """`path:line: text` per refused site across tracked tools/**/*.sh."""
     root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
@@ -76,7 +171,7 @@ def scan(ref: str | None = None) -> list[str]:
             text = subprocess.check_output(["git", "show", f"{ref}:{p}"], text=True, cwd=root)
         else:
             text = (Path(root) / p).read_text()
-        out += [f"{p}:{n}: {t}" for n, t in sites(text)]
+        out += [f"{p}:{n}: {t}" for n, t in sorted(set(sites(text) + case_sites(text)))]
     return out
 
 
@@ -121,6 +216,85 @@ def self_test() -> int:
        "a reason after a mut marker is refused in a judged file on a guarded line")
     st(sites(head + 'f x  # never-empty: argv  # mut:x\n'), [],
        "a judged file's non-bare line with the reason before the marker passes (null)")
+    # The second rule: the line numbers each text refuses. Run against bash 3.2.57, every refused
+    # shape fails, at `bash -n` or (quoted, or in backquotes) at run time.
+    def cs(text, want, name):
+        st([k for k, _ in case_sites(text)], want, name)
+
+    tick = ('out=$(export A=1\n  case $1 in\n    func) . "$t/e"; export -f exec; "$B" --n ;;\n'
+            '    bashenv) BASH_ENV=$t/e "$B" --n ;;\n    none) "$B" --n ;;\n  esac 2>&1); src=$?\n')
+    cs(tick, [3, 4, 5], "planted: tick_loop.sh's shape at PR 3520, three bare patterns in $( )")
+    cs(tick.replace("func)", "(func)").replace("bashenv)", "(bashenv)").replace("none)", "(none)"), [],
+       "the same with each pattern's own ( passes (null)")
+    cs("case a in a) x=$(echo 1);; esac\n", [], "a case at top level passes, its body's $( ) too")
+    cs("( case a in a) :;; esac )\nx=`case a in a) :;; esac`\n", [], "a subshell or backquotes pass")
+    cs("x=$(y=`case a in a) :;; esac`)\n", [], "backquotes inside $( ) reset it")
+    cs("x=$(y=`echo $(case a in a) :;; esac)`)\n", [1], "a $( ) inside those backquotes counts")
+    cs("cat <(case a in a) :;; esac)\ncat >(case a in\n b) :;; esac)\n", [1, 3],
+       "a process substitution counts, either direction")
+    cs('x="$(case a in a) :;; esac)"\n', [1], "a quoted $( ) counts: bash -n passes, the run dies")
+    cs("x=$(case a in (a|b) :;& c) :;; esac)\nx=$(case a in (a) :;;& (b) :;; d) :;; esac)\n", [1, 2],
+       "a bare pattern after ;& or ;;& is refused, a led one after ;; passes")
+    cs("x=$(case a in (a) :;; esac; echo b)\nx=$(echo)\ncase a in a) :;; esac\n", [],
+       "esac and the closing ) end the substitution's reach")
+    cs("x=$(case a in\n  # c) a comment\n  (a) :;;\nesac; echo '# case a in a)' \"case a in a)\")\n", [],
+       "comments and quoted text are not patterns")
+    cs("x=$(echo a#b $# \"\\\"\" \"$(echo \\\")\"; case a in a) :;; esac)\n", [1],
+       "a mid-word # is no comment; escapes in and out of quotes")
+    cs("x=$(echo \\)\ncase a in a) :;; esac)\n", [2], "an escaped ) does not close the substitution")
+    cs("x=$(cat <<E\ncase a in a) x;; esac\nE\ncat <<-'F'\n\tb) )\n\tF\ncase a in a) :;; esac)\n", [7],
+       "here-document bodies are skipped, and scanning resumes after the delimiter")
+    cs("x=$(cat <<<case; case a in a) :;; esac)\n", [1], "a here-string is not a here-document")
+    cs("x=$(echo $(( (1)+2 )) ${y:-z}; case a in a) :;; esac)\nx=$(( (1) ))${y}\ncase a in a) :;; esac\n",
+       [1], "arithmetic and ${ } nest and close")
+    cs("x=$(f() { case a in a) :;; esac; }; ( case b in b) :;; esac ))\n", [1],
+       "a function or subshell inside $( ) is still inside it")
+    cs("x=$(if t; then case a in a) :;; esac; fi; while t; do case b in\n b) :;; esac; done)\n", [1, 2],
+       "case after then and do is a keyword")
+    cs("x=$(t && case a in a) :;; esac)\nx=$(case a in (a) case b in b) :;; esac;; esac)\n", [1, 2],
+       "case after && and a nested case after a pattern are keywords")
+    cs("local rt case\ncase=$(echo case a in b)\nx=$(mycase a in b)\n", [],
+       "case as an argument, a variable or inside a word is not the keyword")
+    cs('x=$(case "$y" in ("a)") :;; \'b)\'|c) :;; esac)\n', [1], "a pattern's quoted ) is not its end")
+    cs("$(case a in a) :;; esac)\n\nx=$(case a in (a\\'\"\") :;;\n c) :;; esac)\n", [1, 4],
+       "a $( ) at the text's start; an escaped quote and an empty quote inside a led pattern")
+    cs("\n# $(\ncase a in a) :;; esac\nx=$(case a in (a);;\n b) :;; esac)\n", [5],
+       "a leading newline counts; a comment opens no $( ); ;; right after a pattern")
+    cs("x=$(echo ')' '' \")\" ${#a} $((1)) $(((1)+(2))); case a in a) :;; esac)\n", [1],
+       "quoted ), an empty quote, ${#...}, arithmetic: none closes the substitution")
+    cs("x=$(echo $((1)))\ncase a in a) :;; esac\nx=${y}$(case a in a) :;; esac)\n", [3],
+       "arithmetic and ${ } close where they end")
+    cs("x=$(echo # )\ncase a in a) :;; esac)\nx=$(case a in (a) :;;&(b) :;;\n c) :;; esac)\n", [2, 4],
+       "a comment's ) closes nothing; ;;& is consumed whole")
+    cs("x=$(cat <<E\nE\ncase a in a) :;; esac)\nx=$(case a in (a) :\nesac)\ncase b in b) :;; esac\n", [3],
+       "a here-document's delimiter can be its first line; esac after a body without ;; ends the case")
+    cs("x=$(cat <<-E\n\t\tE\ncase a in a) :;; esac)\nx=$(cat <<E\n\tE\ncase a in a) :;; esac\nE\n)\n", [3],
+       "<<- strips tabs before its delimiter, << does not")
+    cs("x=`echo $(case a in a) :;; esac)`; y=$(z=`case a in a) :;; esac`)\n", [1],
+       "case right after a backquote is a keyword; a $( ) inside backquotes counts")
+    # The CLI over a scratch repository: both rules, `--check` on the tree and at a ref.
+    import tempfile
+    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tests"))
+    from throwaway_git import throwaway_git_init
+    with tempfile.TemporaryDirectory() as d:
+        env = throwaway_git_init(d, "-q")
+        (Path(d) / "tools").mkdir()
+        (Path(d) / "tools/a.sh").write_text('f "${a[@]}"\nx=$(case a in a) :;; esac)\n')
+        (Path(d) / "tools/b.txt").write_text('f "${a[@]}"\n')
+
+        def cli(*args):
+            r = subprocess.run([sys.executable, "-I", __file__, *args], cwd=d, env=env,
+                               capture_output=True, text=True)
+            return r.returncode, r.stdout.split("\n")[:-1]
+
+        subprocess.run(["git", "add", "-A"], cwd=d, env=env, check=True)
+        subprocess.run(["git", "commit", "-qm", "x"], cwd=d, env=env, check=True)
+        want = (1, ['tools/a.sh:1: f "${a[@]}"', "tools/a.sh:2: x=$(case a in a) :;; esac)"])
+        st(cli("--check"), want, "--check prints each site of both rules in .sh files, rc 1")
+        (Path(d) / "tools/a.sh").write_text("x=$(case a in (a) :;; esac)\n")
+        st(cli("--check"), (0, []), "--check on the repaired tree passes (null)")
+        st(cli("--check", "--ref", "HEAD"), want, "--check --ref reads the commit, not the tree")
+        st(cli()[0], 2, "no arm prints the usage, rc 2")
     for f in fails:
         print("FAIL", f)
     print("bare_array self-test:", "FAILED" if fails else "ok")
@@ -133,7 +307,8 @@ if __name__ == "__main__":
     if "--check" in sys.argv:
         ref = sys.argv[sys.argv.index("--ref") + 1] if "--ref" in sys.argv else None
         hits = scan(ref)
-        print("\n".join(hits))
+        if hits:
+            print("\n".join(hits))
         sys.exit(1 if hits else 0)
     print(__doc__)
     sys.exit(2)
diff --git a/tools/audit/seat/instruments/bare_array.py.md b/tools/audit/seat/instruments/bare_array.py.md
index 529187f451..f3c694b6b2 100644
--- a/tools/audit/seat/instruments/bare_array.py.md
+++ b/tools/audit/seat/instruments/bare_array.py.md
@@ -11,3 +11,9 @@
   on the line or on a comment-only line directly above it; a line ending in
   `# mut:<name>` takes the reason above, and a reason placed after that marker
   is refused on any line, because it unanchors the self-test's mutant.
+  Second rule: a `case` pattern without its leading `(` inside a `$( ... )`,
+  `<( ... )` or `>( ... )` substitution, quoted or not, is refused: bash 3.2
+  ends the substitution at the pattern's `)`, so `bash -n` fails (PR 3520 put
+  one in `tick_loop.sh`, whose freshness check then refused every tick pass),
+  or, quoted, the run dies. The way out is the `(`, as in `(func) ...;;`; no
+  marker excuses one, since 3.2 never parses it.
diff --git a/tools/audit/seat/instruments/update_pr.sh.md b/tools/audit/seat/instruments/update_pr.sh.md
index f964bc717c..eac78f7f29 100644
--- a/tools/audit/seat/instruments/update_pr.sh.md
+++ b/tools/audit/seat/instruments/update_pr.sh.md
@@ -17,6 +17,7 @@
   body move of a PR whose head holds its handoff, with `HPO_UPDATE_BODY_ONLY=1`:
   a run that would then move the head (a DIRTY PR's clean main merge, an added
   row) refuses and pushes nothing, since that move skipped the review freeze.
+  A body carrying a generated figure block has it re-rendered (`figure_block.py refresh`, as `open_pr.sh` does) at the head the run pushes or patches, on both paths, before app_push.sh or body_patch.sh; a failed refresh refuses, pushing and patching nothing; a body with no block is untouched.
   When: updating a PR after review prep or a main merge, or re-bodying it.
   Refusal: as `remerge_main.sh` — a conflict stops, it is never resolved
   silently; no open PR at the branch stops before any push. Up front, each an
diff --git a/tools/audit/seat/pr_args.sh b/tools/audit/seat/pr_args.sh
index 63c2e08c89..dbf53479dc 100644
--- a/tools/audit/seat/pr_args.sh
+++ b/tools/audit/seat/pr_args.sh
@@ -485,9 +485,17 @@ pr_pushers() { # [<root>] [<rev>]: the census; one line per seam, exit 1 on any
 # copyin carries ref_privacy.py for the same reason: handoff_push.sh's guard
 # fails closed without it, so its reap arms never reached a push (#2668's CI).
 pr_args_self_test() (
-  local src t f=0 n=0 o m base code side body i reapsha UNREL
+  local src seat t f=0 n=0 o m base code side body i reapsha UNREL
   src=$PR_ARGS_DIR
   t=$(mktemp -d) || { echo "pr_args self-test: no temporary directory"; return 1; }
+  # The programs under test are copied from a snapshot of them taken here, never from the live
+  # checkout: a job step that moves the checkout mid-run (tick_loop.sh's restart onto origin/main)
+  # would otherwise hand the later arms the base's copies (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH).
+  # Only the files the arms copy in, and roster_lib.py, which pr_cap.py loads from beside itself: an arm
+  # naming one not listed fails at its cp, never reads the tree.
+  seat=$t/seat; mkdir "$seat" && (cd "$src" && cp -p delivery_row.sh gh_read.py handoff_push.sh open_pr.sh \
+    pr_args.sh pr_cap.py ref_privacy.py remerge_main.sh roster_lib.py update_pr.sh "$seat/") \
+    || { echo "pr_args self-test: no snapshot of the programs under test"; rm -rf "$t"; return 1; }
   # The pusher stubs the reap arms drive read this directory ($T is open_pr's topic).
   REAP_DIR=$t; export REAP_DIR
   # A stopped pusher's stub app_push: it records itself and a two-level sleep
@@ -542,8 +550,8 @@ STUB
   copyin() { # <mutant|->: copies of the scripts, less the named mutant's line
     local g
     for g in open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh pr_cap.py ref_privacy.py gh_read.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
   }
   i=0
@@ -692,8 +700,8 @@ STUB
   git -C "$o" reset -q --hard "$base"
   relsrc() { # <mutant|-> <fresh clone> <sibling>: source by a relative path, cd to the sibling, ask
     mkdir -p "$2/tools/audit/seat"
-    if [ "$1" = - ]; then cp "$src/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
-    else grep -v "# mut:$1\$" "$src/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
+    if [ "$1" = - ]; then cp "$seat/pr_args.sh" "$2/tools/audit/seat/pr_args.sh"
+    else grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$2/tools/audit/seat/pr_args.sh"; fi
     ( unset PR_ARGS_DIR; cd "$2" && . ./tools/audit/seat/pr_args.sh && cd "$3" && PR_NAME=fresh pr_tools_fresh ) > "$t/out" 2>&1
   }
   relsrc - "$t/fr" "$t/st"; ck "pr_args: sourced by a relative path from a fresh clone, then cd'd into a stale sibling, passes" $?
@@ -1259,8 +1267,8 @@ STUB
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null
     git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v -e "# mut:${1%%+*}\$" -e "# mut:${1##*+}\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi  # a+b: two mutants at once
     done
     cp "$t/body.md" "$t/bR.md"
     HPO_STATE_DIR=$sd STUB_DIR=$sdir BR=fix/r BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" r "$codeR" T G > "$t/outo" 2>&1 & op=$!
@@ -1412,7 +1420,7 @@ STUB
     sd=$(cd "$sd" && pwd -P); rm -rf "$sdir"; mkdir -p "$sdir"; figbody "$2"
     printf 'z\n' > "$o/zz" && git -C "$o" add zz && git -C "$o" -c user.name=t -c user.email=t@t commit -q -m "main file"
     for g in open_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd STUB_DIR=$sdir bash "$m/tools/audit/seat/open_pr.sh" f "$codeF" T G > "$t/fo" 2>&1; echo $? > "$t/frc"
     git -C "$o" cat-file -e fix/f-pr:dev/programme/delivery/5.md 2>/dev/null && echo 1 > "$t/frow" || echo 0 > "$t/frow"
@@ -1435,6 +1443,59 @@ STUB
   ck "open_pr: a re-run after an open closed at its row push clears the left-over branch and worktree and opens" $?
   figrun opfig2 block; figrun opclear block keep; [ "$(cat "$t/frc")" != 0 ] && [ "$(cat "$t/frow")" = 0 ]
   ck "  mutant mut:opclear (its line deleted): the re-run fails at git worktree add -b on the left-over branch (the defect)" $?
+  # R10-HOTFIX-UPDATEPR-FIGURE-REFRESH: update_pr.sh re-renders the body's figure blocks at the head it
+  # pushes (moved-head path, before app_push) or patches (body-only path, before body_patch.sh), as
+  # open_pr.sh's op_figures does. fix/g starts at $base; handoff/f's pusher stub is lint's figure-block
+  # head check; the stub figure_block.py rewrites head= to HEAD, notes each call and fails while $t/figfail exists.
+  cat > "$m/tools/pr/figure_block.py" <<STUBF
+import os, re, subprocess, sys
+open("$t/figcalled", "a").close()
+if os.path.exists("$t/figfail"): sys.exit(1)
+f = sys.argv[sys.argv.index("refresh") + 1]
+h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
+t = re.sub(r"head=[0-9a-f]{40}", "head=" + h, open(f).read())
+open(f, "w").write(t)
+STUBF
+  cp "$t/bin/gh" "$t/gh.orig"
+  printf '#!/bin/sh\ncase "$*" in *--head*) echo 5 ;; *mergeStateStatus*) echo CLEAN ;; "pr view"*) echo "a title" ;; *) exit 99 ;; esac\n' > "$t/bin/gh"
+  printf '#!/bin/bash\necho called >> "%s/ubp.log"\nh=$(grep -o "^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*" "$5" | grep -o "head=.*" | cut -c6-)\n[ -z "$h" ] || [ "$h" = "$4" ] || { echo "body_patch: REFUSE: figure-block scope-line names another head ($h)"; exit 1; }\necho "body_patch: OK"\n' "$t" > "$t/ubp.sh"
+  ufig() { # <mutant|-> <code sha|-> <block|none>: update_pr.sh fix/g over a body with (or without) a figure block naming the code head
+    rm -f "$t/figcalled"
+    if [ "$3" = block ]; then printf '## Head\n\nthe body\n\n## Figures\n\n<!-- figure-block: scope-line mb=%s head=%s -->\n~~~text\nx\n~~~\n<!-- /figure-block -->\n' "$base" "$codeF" > "$t/bu.md"
+    else printf '## Head\n\nthe body\n' > "$t/bu.md"; fi
+    git -C "$o" rev-parse fix/g > "$t/ubefore" 2>/dev/null || echo none > "$t/ubefore"
+    HANDOFF_TOPIC=f HPO_BODY_PATCH=$t/ubp.sh run "$1" update_pr.sh fix/g "$2" "$t/bu.md"
+    git -C "$o" rev-parse fix/g > "$t/uafter"
+  }
+  ufresh() { git -C "$o" branch -f fix/g "$base"; rm -f "$t/figfail" "$t/ubp.log"; }
+  ubody() { grep -o '^<!-- figure-block: [a-z-]* mb=[0-9a-f]* head=[0-9a-f]*' "$t/bu.md" | grep -o 'head=.*' | cut -c6-; }
+  ufresh; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(cat "$t/uafter")" != "$(cat "$t/ubefore")" ]
+  ck "update_pr: a moved head with a figure block pushes a body whose block names the new head" $?
+  ufresh; ufig updfig1 "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig1 (its line deleted): the push carries a block naming another head and is refused" $?
+  ufresh; touch "$t/figfail"; ufig - "$codeF" block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the head to push failed" "$t/out" && [ "$(cat "$t/uafter")" = "$base" ]
+  ck "update_pr: a failing refresh at the head to push refuses and pushes nothing" $?
+  ufresh; ufig - "$codeF" block; rm -f "$t/ubp.log"
+  ufig - - block
+  [ "$(cat "$t/rc")" = 0 ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ] && grep -qF "update_pr: BODY-ONLY" "$t/out" && [ "$(ubody)" = "$(cat "$t/uafter")" ] && [ "$(wc -l < "$t/ubp.log")" = 1 ]
+  ck "update_pr: a body-only run over a block naming the code head patches a body naming the live head" $?
+  ufig updfig2 - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "body_patch: REFUSE: figure-block scope-line names another head" "$t/out"
+  ck "  mutant mut:updfig2 (its line deleted): body_patch.sh is handed a block naming another head and refuses" $?
+  rm -f "$t/ubp.log"; touch "$t/figfail"; ufig - - block
+  [ "$(cat "$t/rc")" != 0 ] && grep -qF "update_pr: REFUSE: the figure-block refresh at the unmoved head failed" "$t/out" && [ ! -e "$t/ubp.log" ] && [ "$(cat "$t/ubefore")" = "$(cat "$t/uafter")" ]
+  ck "update_pr: a failing refresh on the body-only path refuses and patches nothing" $?
+  ufresh; ufig - "$codeF" none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && ! grep -q 'figure-block' "$t/bu.md"
+  ck "null control: a body with no figure block never reaches the refresh and is pushed as before" $?
+  ufresh; ufig - "$codeF" none; ufig - - none
+  [ "$(cat "$t/rc")" = 0 ] && [ ! -e "$t/figcalled" ] && grep -qF "update_pr: BODY-ONLY" "$t/out"
+  ck "null control: a body-only run over a body with no figure block never reaches the refresh" $?
+  git -C "$o" branch -qD fix/g; git -C "$o" reset -q --hard "$base"; cp "$t/gh.orig" "$t/bin/gh"
+  git -C "$m" worktree prune; git -C "$m" branch -qD fix/g 2>/dev/null; git -C "$m" update-ref -d refs/remotes/origin/fix/g; true
   # R10-FLOW-BODY-ONLY parts (a) and (b), ruling R4: update_pr.sh merges origin/main only when the PR
   # is DIRTY or the merge would conflict, and a head the run leaves unmoved is re-bodied by
   # body_patch.sh (here a stub, HPO_BODY_PATCH) with no push. handoff/v carries a push stub that
@@ -1558,7 +1619,7 @@ GH
     rm -rf "$sd" "$sdir"; mkdir -p "$sdir" "$sd"; sd=$(cd "$sd" && pwd -P)
     git -C "$m" worktree prune; git -C "$m" branch -qD fix/r 2>/dev/null; git -C "$o" branch -qD fix/r 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     case ${2:-} in edit) touch "$sdir/editfail" ;; postpush) touch "$sdir/p2postfail" ;; selftest) touch "$sdir/p2selftest" ;; host) touch "$sdir/p2selftest" "$sdir/hostfail" ;; stmix|body) touch "$sdir/p2$2" "$sdir/hostfail" ;;
       stalefig) touch "$sdir/hostfail" "$sdir/figfail"; mkdir -p "$sd/pr/r" && printf '  REFUSE   self-test             FAIL x\n' > "$sd/pr/r/p2.log" ;; *) touch "$sdir/p2fail" ;; esac
@@ -1650,11 +1711,11 @@ STUB
   }
   hrlib() { # <-|mutant|ret:tag|shared>: the library the next hrrun sources; ret:<tag> turns that line's `|| return 1` into `|| return 0`
     case $1 in
-      -) cp "$src/pr_args.sh" "$t/hr/lib.sh" ;;
-      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      -) cp "$seat/pr_args.sh" "$t/hr/lib.sh" ;;
+      ret:*) sed "/# $1\$/s/|| return 1/|| return 0/" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
       # one tree for every measurement, replaced by whichever run starts next: the blocked head's pr_step_sig
-      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
-      *) grep -v "# mut:$1\$" "$src/pr_args.sh" > "$t/hr/lib.sh" ;;
+      shared) sed '/# ret:sigpriv$/s|w=.*|w=$3/tree; git -C "$1" worktree remove --force "$w" >/dev/null 2>\&1; rm -rf "$w"; mkdir -p "$w"|' "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
+      *) grep -v "# mut:$1\$" "$seat/pr_args.sh" > "$t/hr/lib.sh" ;;
     esac
   }
   hrrun() { # <head sha> [main sha] [log] -> pr_host_refusal's status
@@ -1823,7 +1884,7 @@ STUB
     local sd=$t/mconf-$1 g
     rm -rf "$sd"; mkdir -p "$sd"; sd=$(cd "$sd" && pwd -P); git -C "$m" worktree prune; git -C "$m" branch -qD fix/q 2>/dev/null
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"; else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     HPO_STATE_DIR=$sd BR=fix/q BR_FIXED=1 bash "$m/tools/audit/seat/open_pr.sh" q "$codeR" T G > "$t/outq" 2>&1; echo $? > "$t/rcq"
     [ -d "$sd/pr/q/wt" ] && echo kept > "$t/wtq" || echo gone > "$t/wtq"
@@ -1846,8 +1907,8 @@ STUB
     local sd=$t/unp-$1-$2-${3:--} g
     rm -rf "$sd" "$sd.link" "$t/s$i"; git -C "$m" worktree prune; git -C "$m" branch -qD fix/u 2>/dev/null; mkdir -p "$sd/pr/u"; sd=$(cd "$sd" && pwd -P)
     for g in open_pr.sh update_pr.sh delivery_row.sh pr_args.sh pr_cap.py; do
-      if [ "$1" = - ]; then cp "$src/$g" "$m/tools/audit/seat/$g"
-      else grep -v "# mut:$1\$" "$src/$g" > "$m/tools/audit/seat/$g"; fi
+      if [ "$1" = - ]; then cp "$seat/$g" "$m/tools/audit/seat/$g"
+      else grep -v "# mut:$1\$" "$seat/$g" > "$m/tools/audit/seat/$g"; fi
     done
     git -C "$m" fetch -q origin fix/u && git -C "$m" worktree add -q -b fix/u "$sd/pr/u/wt" origin/fix/u || return 1
     [ "$2" = 0 ] || { printf 'row\n' > "$sd/pr/u/wt/row" && git -C "$sd/pr/u/wt" add row && git -C "$sd/pr/u/wt" commit -q -m row; }
@@ -1948,7 +2009,7 @@ STUB
   fi
   rmrun() { # <mutant|-> <branch>: remerge_main.sh on <branch> in worktree $t/rmw; the output in $t/out
     local g; git -C "$t/rmm" worktree remove --force "$t/rmw" 2>/dev/null; rm -rf "$t/rmw"; git -C "$t/rmm" worktree prune
-    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$src/$g" > "$t/rmm/tools/audit/seat/$g"; done
+    for g in remerge_main.sh pr_args.sh gh_read.py; do grep -v "# mut:$1\$" "$seat/$g" > "$t/rmm/tools/audit/seat/$g"; done
     git -C "$t/rmm" fetch -q origin "$2" && git -C "$t/rmm" worktree add -q -B "$2" "$t/rmw" "origin/$2" \
       && PATH="$t/rmgit:$PATH" bash "$t/rmm/tools/audit/seat/remerge_main.sh" 7 "$t/rmw" "$2" "$t/body.md" > "$t/out" 2>&1
     echo $? > "$t/rc"
@@ -2113,7 +2174,7 @@ print(n)' "$1"
   # line above leaves that line running on into the next (round 2's first mut:fggc did, and its arm
   # read the broken copy as a pass). mutshape <files...>: exit 1 naming each such line.
   mutshape() { awk 'prev ~ /\\$/ && /# mut:[A-Za-z0-9]+$/ { print FILENAME ":" FNR; bad = 1 } { prev = $0 } END { exit bad }' "$@"; }
-  (cd "$src" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
+  (cd "$seat" && mutshape open_pr.sh update_pr.sh handoff_push.sh remerge_main.sh delivery_row.sh pr_args.sh)
   ck "every # mut: line is a whole statement, never one continued from the line above" $?
   printf 'a \\\n  b  # mut:x\n' > "$t/mutshape.sh"; ! mutshape "$t/mutshape.sh" >/dev/null
   ck "null control: a # mut: line continued from the line above is named" $?
@@ -2125,7 +2186,7 @@ print(n)' "$1"
   rkrun() { # <mutant|-> <stub rc> -> $t/rk.argv: what the stub saw; $t/rk.err: the statement's stderr
     : > "$t/rk.argv"
     printf '#!/bin/bash\necho "$*" >> "%s/rk.argv"\nexit %s\n' "$t" "$2" > "$t/rkseat/bus.sh"
-    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$src/open_pr.sh"; else grep -h '# mut:rekey$' "$src/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
+    if [ "$1" = - ]; then grep -h '# mut:rekey$' "$seat/open_pr.sh"; else grep -h '# mut:rekey$' "$seat/open_pr.sh" | grep -v "# mut:$1\$"; fi > "$t/rk.line"
     SEAT=$t/rkseat PR_NAME=open_pr T=ht N=77 bash "$t/rk.line" 2> "$t/rk.err"
     echo $? > "$t/rk.rc"
   }
@@ -2138,7 +2199,7 @@ print(n)' "$1"
   rkrun rekey 0; [ ! -s "$t/rk.argv" ]
   ck "  mutant mut:rekey (its line deleted) re-keys nothing" $?
   # The cap's own counting rule, which orchestrator_tick.py imports too.
-  python3 -I "$src/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
+  python3 -I "$seat/pr_cap.py" --self-test > "$t/cap.out" 2>&1 && grep -q 'pr_cap self-test: [1-9][0-9]* checks, 0 failed' "$t/cap.out"
   ck "pr_cap.py --self-test: its tally says 0 failed" $?
   reap
   kill "$UNREL" 2>/dev/null; wait "$UNREL" 2>/dev/null || :
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index d0b7147789..0b35a54fa4 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -463,9 +463,9 @@ f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".
       local v=$t/victim-$1.git; rm -f "$t/shadow"; throwaway_git_init "$v" -q --bare || return 1
       out=$(export HPO_HEARTBEAT_REMOTE=$v TICK_RC=1
         case $1 in
-          func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
-          bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
-          none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (func) . "$t/execfn"; export -f exec; "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (bashenv) BASH_ENV=$t/execfn "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
+          (none) "$BASH" "$HERE/tick_loop.sh" --self-test --nested ;;
         esac 2>&1); src=$?
       refs=$(git -C "$v" for-each-ref | grep -c .); }
     for c in func bashenv; do
diff --git a/tools/audit/seat/update_pr.sh b/tools/audit/seat/update_pr.sh
index 611d4360f3..bd00868f07 100755
--- a/tools/audit/seat/update_pr.sh
+++ b/tools/audit/seat/update_pr.sh
@@ -97,6 +97,15 @@ TTL=$(gh pr view "$N" -R $R --json title -q .title)
 _added=$(ensure_row . "$N" "$(row_line "$N" $R "$TTL")")
 ROW=""; [ -z "$_added" ] || ROW="adds one commit containing only this PR's own row, \`$_added\`"
 M=$(git rev-parse --short origin/main); H=$(git rev-parse HEAD)
+# A generated figure block names the head it was rendered at (figure_block.py refresh, as open_pr.sh's
+# op_figures), and the merges and the row above moved it: re-render at the head this run pushes or patches,
+# before either. A body with no block is untouched; a failed refresh refuses, pushing and patching nothing.
+upd_figures() { # <where>
+  grep -q '^<!-- figure-block: ' "$B" || return 0
+  python3 -I "$PRT/figure_block.py" refresh "$B" --base origin/main --head HEAD > $WT.fig.log 2>&1 && return 0
+  pr_refuse "the figure-block refresh $1 failed; nothing is pushed or patched:
+$(tail -n 20 $WT.fig.log)"
+}
 # HPO_UPDATE_BODY_ONLY (cloud_relay.sh's handoff_arm, on a body-only move it does not review-freeze):
 # the head must stay the live head, so a DIRTY merge of main or an added row refuses, pushing nothing
 # (#3089 review round 2): only the orchestrator, past the freeze, moves a head under review.
@@ -117,6 +126,7 @@ import sys; from head_note import prefix
 p,H=sys.argv[1:3]; s=open(p).read()
 s=prefix(s,"`%s` is this PR's head, unchanged: its code was already in it and main merged cleanly, so the orchestrator's script set this body without a push.\n\n"%H); open(p,'w').write(s)
 E
+  upd_figures "at the unmoved head"  # mut:updfig2
   rc=0; ( cd "$WT" && bash "${HPO_BODY_PATCH:-$SEAT/body_patch.sh}" --repo $R "$N" "$H" "$B" ) > $WT.log 2>&1 || rc=$?
   cat $WT.log
   [ "$rc" = 0 ] || pr_refuse "body-only: body_patch.sh refused #$N at $H (exit $rc); its log is $WT.log"
@@ -131,6 +141,7 @@ if MM: pre="`%s` "%H + ((N+" and then ") if N else "") + "merges origin/main `%s
 else: pre="`%s` "%H + " and then ".join(x for x in (N, R) if x) + ".\n\n"  # main merged cleanly: not merged (R4)
 s=prefix(s,pre); open(p,'w').write(s)
 E
+upd_figures "at the head to push"  # mut:updfig1
 if test -f tools/audit/app_push.sh; then _push=tools/audit/app_push.sh; else _push=tools/pr/app_push.sh; fi
 RO=""; [ "$(git rev-parse "$H^@")" != "$LIVE" ] || RO=--row-only  # mut:rowonly
 [ -n "$RO" ] || RO=--reuse  # mut:updreuse
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index d56ec9a60d..f5a326bae7 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -1387,22 +1387,7 @@
     "dev/audit/rounds/round4/D1/verify2_d102.py",
     "dev/audit/rounds/round4/D1/verify2_d1inst.py",
     "dev/audit/rounds/round4/D10",
-    "dev/audit/rounds/round4/D10/coverage_measure.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-01.sh",
-    "dev/audit/rounds/round4/D10/d10_own_D10-02.py",
-    "dev/audit/rounds/round4/D10/d10_own_D10-03.py",
-    "dev/audit/rounds/round4/D10/log_when_unavailable.py",
-    "dev/audit/rounds/round4/D10/mypy_arms.sh",
-    "dev/audit/rounds/round4/D10/qs_rules.out.txt",
-    "dev/audit/rounds/round4/D10/qs_rules.py",
-    "dev/audit/rounds/round4/D10/quality_scale.draft.yaml",
-    "dev/audit/rounds/round4/D10/reports",
-    "dev/audit/rounds/round4/D10/reports/FINDER.md",
-    "dev/audit/rounds/round4/D10/verify-0-1.md",
-    "dev/audit/rounds/round4/D10/verify-0-2.md",
-    "dev/audit/rounds/round4/D10/verify-0-3.md",
-    "dev/audit/rounds/round4/D10/verify3",
+    "dev/audit/rounds/round4/D10/**",
     "dev/audit/rounds/round4/D10/verify3/**",
     "dev/audit/rounds/round4/D11",
     "dev/audit/rounds/round4/D11/d11_own_D11-01.py",
@@ -1664,9 +1649,7 @@
     "dev/audit/rounds/round4/resume_row.py",
     "dev/audit/rounds/round5",
     "dev/audit/rounds/round5-fix",
-    "dev/audit/rounds/round5-fix/R5-D7",
-    "dev/audit/rounds/round5-fix/R5-D7/learner_guard_ends.py",
-    "dev/audit/rounds/round5-fix/R5-INST-01",
+    "dev/audit/rounds/round5-fix/**",
     "dev/audit/rounds/round5-fix/R5-INST-01/**",
     "dev/audit/rounds/round5/D0",
     "dev/audit/rounds/round5/D0/seat-a",
@@ -1709,9 +1692,7 @@
     "dev/audit/rounds/round5/D4/seat-a",
     "dev/audit/rounds/round5/D4/seat-a/sweep.mjs",
     "dev/audit/rounds/round5/D7",
-    "dev/audit/rounds/round5/D7/seat-a",
-    "dev/audit/rounds/round5/D7/seat-a/sysid_step_bias.py",
-    "dev/audit/rounds/round5/D7/seat-b",
+    "dev/audit/rounds/round5/D7/**",
     "dev/audit/rounds/round5/D7/seat-b/**",
     "dev/audit/rounds/round5/D8",
     "dev/audit/rounds/round5/D8/seat-b",
@@ -2419,23 +2400,8 @@
     "tools/audit/seat/wt_sync.sh",
     "tools/audit/worktree_gc.sh",
     "tools/ci",
-    "tools/ci/alert_list.py",
-    "tools/ci/alert_list_mutants.sh",
-    "tools/ci/codescan_wait.py",
-    "tools/ci/fixtures",
-    "tools/ci/fixtures/gate_busy_defer_runs.json",
-    "tools/ci/fixtures/ruleset",
+    "tools/ci/**",
     "tools/ci/fixtures/ruleset/**",
-    "tools/ci/gate.py",
-    "tools/ci/ghapi.py",
-    "tools/ci/prelude.py",
-    "tools/ci/ruleset_cutover.py",
-    "tools/ci/selftest_closures.json",
-    "tools/ci/selftest_scope.py",
-    "tools/ci/selftest_scope_mutants.sh",
-    "tools/ci/selftest_step.sh",
-    "tools/ci/sweep.py",
-    "tools/ci/sweep_selftest.py",
     "tools/coverage",
     "tools/coverage/**",
     "tools/devices",
@@ -9159,6 +9125,7 @@
     "-",
     ".",
     "config",
+    "dev/programme/delivery/5.md",
     "objects",
     "packed-refs",
     "refs",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
