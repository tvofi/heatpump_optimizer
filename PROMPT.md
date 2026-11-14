CLOUD REVIEWER seat for PR #3569 of tvofi/heatpump_optimizer, at head b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b. Bus nonce: c39b5fde1e52f538cd00a3edfa0091d3. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the PR head with `git fetch origin b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b`; the PR body is in the PR. Start from the review packet, which you render here rather than read from the dispatcher, whose copy is a path on its own machine: `python3 -I tools/audit/seat/review_packet.py render --pr 3569 --head b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b --out $HOME/review-packet.md`. A refusal names its signal and the packet is still written unless the signal is `host-path`; re-read the live checks either way. Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). Wait for CI on this head only by re-running `python3 tools/audit/seat/merge_train.py classify b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b --pr 3569` in the background, at least 60 s between runs, until it exits 0 (GREEN), 1 (RED), 2 (unreadable: say so in the verdict) or 4 (APPROVAL-OWED: the only red is the budget raise's approval, which follows your verdict; judge the head as GREEN and quote the line); 3 is WAIT, so run it again. Never wait with `pgrep` or `pkill`, whose `-f` pattern matches the waiter's own command line, nor on a context the ruleset does not require, such as `prelude`. A review_packet `required-red` signal does not stop you while classify prints WAIT: classify decides. If your review is otherwise complete and classify still prints WAIT after about 30 minutes of polling, stop waiting: put the line `pending-ci: <the context names it printed>` straight after the `bus-nonce:` line and return the verdict as below; the relay posts it once CI is green at this head, refuses it over a red, and refuses it if the head moves. If the review is not complete then, push `Fix review: blocked b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b ci-wait: <the last classify line>` as below.
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b` or `Fix review: blocked b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: c39b5fde1e52f538cd00a3edfa0091d3`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict 3569 b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b") && git -C $R push -q origin $C:refs/heads/probe/rev-3569-c39b5fde`. That ref is the return signal. Do not post comments, approve or merge.
Every way your turn ends pushes a verdict to that ref: a setup or hook refusal that stops you pushes `Fix review: blocked b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b seat-refused: <the refusing line>`; never end your turn while a background poll runs. After the push, read the ref back with `git ls-remote origin refs/heads/probe/rev-3569-c39b5fde`, and push again if it does not print your commit.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires: when it refuses inline work, dispatch a haiku or sonnet Agent subagent to do it rather than bypassing the guard; never set FRUGAL_ALLOW_INLINE and never edit .claude/settings.json.

Brief (snapshotted when this payload was rendered):
# Review packet #3569
head: b61ee0b674cbae9ce5ba81f4f9b86af280b64e5b
base: 7aac3e7c044a6ea7c5e6f4271e7e563f2fdee424

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=132228411404 success
arch-score / arch-score id=132244001546 success
arm id=132225237202 skipped
budget-raise-gate / budget-raise-gate id=132244001633 success
cancel-superseded id=132243749861 skipped
codeql id=132238721232 skipped
codeql / Analyze (actions) id=132244001376 success
codeql / Analyze (javascript-typescript) id=132244001477 success
codeql / Analyze (python) id=132244001384 in_progress
gate id=132243066557 success
governance id=132238720128 skipped
governance / delivery-status id=132244003275 skipped
governance / delivery-status-publish id=132244003305 skipped
governance / env-matrix id=132244001559 success
governance / instrument-self-tests id=132244001493 success
governance / policy-docs id=132244001519 success
governance / record id=132244003636 skipped
governance / wave-script id=132244001446 success
hassfest id=132238721220 skipped
hassfest / hassfest id=132244001336 success
kernel-points id=132244003104 skipped
pr-contract id=132239377263 skipped
pr-contract / pr-contract id=132242492787 success
prelude id=132243684444 success
refresh id=132243685808 skipped
sweep-self id=132243552318 skipped
tests id=132238721043 skipped
tests / arch-instrument id=132244881300 success
tests / briefs id=132244001440 success
tests / browser id=132244881292 success
tests / ci-ratchet id=132242185399 skipped
tests / claims-autofix id=132241846484 skipped
tests / closure-scope id=132244001578 success
tests / closures id=132244881416 in_progress
tests / closures-autofix id=132242184922 skipped
tests / coverage id=132244881283 in_progress
tests / coverage-ratchet id=132241102651 success
tests / fast (3.14) id=132244881491 in_progress
tests / graders-head-copy id=132241102721 success
tests / lane-proofs id=132241843959 success
tests / mutation id=132244001575 in_progress
tests / mutation-autofix id=132238799319 skipped
tests / mutation-pins id=132238799269 skipped
tests / nightly-ha id=132244883914 skipped
tests / nightly-status id=132244003638 skipped
tests / replay id=132244882984 skipped
tests / typing id=132244881507 success
validate id=132238720984 skipped
validate / validate-hacs id=132244001534 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 179ba837: dismissed:one extra lookup, the refusal (a traceback naming the missing or mis-indented block) is loud
CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: SCOPED -- 22 script(s) run, 11 scoped out.
             no segment of this names a program this check knows
  ok         PYTHONPATH=tests/hastub python3 tools/audit/seat/features_block.py 'from types import SimpleNamespace as _DspNS'
             `tools/audit/seat/features_block.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh
             `tests/run.sh` is in the tree at this head
  unverified git diff --stat $(git merge-base origin/main HEAD)...HEAD -- tests/golden
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 3 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CLAMP_DROP.273aa7e9.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CLAMP_DROP.273aa7e9.json
new file mode 100644
index 0000000000..d32fdecc86
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CLAMP_DROP.273aa7e9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.decay CLAMP_DROP 273aa7e9",
+  "killed_by": "tests/features.py",
+  "old": "        factor = min(self.weights(when)[1], N_CAP) / n if n > 0.0 else 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`factor = (self.weights(when)[1]) / n if n > 0.0 else 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.273aa7e9.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.273aa7e9.json
new file mode 100644
index 0000000000..0229b8f3ac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.273aa7e9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.decay CMP_BOUND 273aa7e9",
+  "killed_by": "tests/features.py",
+  "old": "        factor = min(self.weights(when)[1], N_CAP) / n if n > 0.0 else 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`factor = min(self.weights(when)[1], N_CAP) / n if n >= 0.0 else 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.50222946.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.50222946.json
deleted file mode 100644
index 112ce1af0a..0000000000
--- a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.50222946.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.decay CMP_BOUND 50222946",
-  "killed_by": "tests/features.py",
-  "old": "        factor = self.weights(when)[1] / n if n > 0.0 else 1.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`factor = self.weights(when)[1] / n if n >= 0.0 else 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}


## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/custom_components/heatpump_optimizer/duty_switch.py b/custom_components/heatpump_optimizer/duty_switch.py
index 2beb1c35b7..e6cc14862c 100644
--- a/custom_components/heatpump_optimizer/duty_switch.py
+++ b/custom_components/heatpump_optimizer/duty_switch.py
@@ -34,7 +34,8 @@ weigh under five, and a sixth latches), spanning :data:`SPAN_DAYS_ON` days with
 the evidence that still weighs: under :data:`SPAN_FLOOR_N` the days are
 forgotten with it. Every threshold
 here is a named constant from one day on one install, not a measurement.
-``n`` is held at :data:`N_CAP` by scaling both counts alike at a booking, so
+``n`` is held at :data:`N_CAP` by scaling both counts alike at a booking and
+on each decay, so a record stored over it is held to it by the first pass,
 evidence from before a firmware change is outvoted in a bounded number of
 episodes and an install that stops switching unlatches in a bounded time.
 """
@@ -192,7 +193,7 @@ class Direction:
     def decay(self, when: datetime) -> bool:
         """Age the counts to ``when``; whether the latch or the span's days moved."""
         n = self.n
-        factor = self.weights(when)[1] / n if n > 0.0 else 1.0
+        factor = min(self.weights(when)[1], N_CAP) / n if n > 0.0 else 1.0
         self.k, self.kept_w = self.k * factor, self.kept_w * factor
         if self.decayed_at is None or utc_elapsed_seconds(when, self.decayed_at) > 0.0:
             self.decayed_at = when
diff --git a/dev/programme/delivery/3569.md b/dev/programme/delivery/3569.md
new file mode 100644
index 0000000000..4576fb661d
--- /dev/null
+++ b/dev/programme/delivery/3569.md
@@ -0,0 +1 @@
+- [#3569](https://github.com/tvofi/heatpump_optimizer/pull/3569) — **open**, R10-DUTY-SWITCH-PLANNER-PRICE: r10 duty switch planner price (R10-DUTY-SWITCH-PLANNER-PRICE)
diff --git a/docs/design/2026-11-10-duty-switch-restart-learning/design.md b/docs/design/2026-11-10-duty-switch-restart-learning/design.md
index 1abcb3d0ec..247ef91ce2 100644
--- a/docs/design/2026-11-10-duty-switch-restart-learning/design.md
+++ b/docs/design/2026-11-10-duty-switch-restart-learning/design.md
@@ -115,6 +115,7 @@ The text above is the approved design, unchanged. Part A (`duty_switch.py`) depa
 - **No read API.** "Read API for B and C, unused in A" was not built: an unused module-level function is refused by `tests/structure.py`'s `dead_top_level_symbols`. `Direction.usable`, `Direction.p` and `Direction.median_off_s` hold the three values; the part that first reads them adds the module-level reader together with its first caller. Control: a reader added with no caller turns that metric red.
 - **Stored record.** Version 1 stores, per direction, `k` and `kept_w` (the kept episodes' weight; n is their sum), the decay stamp, first and last day, the latch, the off list and the four integer tallies `stopped`, `kept`, `void`, `censored`. With k and n stored, `tests/finite_boundary.py`'s in-domain probe produced k over n. n has no ceiling but the load bound.
 - **Publication is conditional.** A direction publishes its attributes only once it holds a stopped, kept or void episode, and the median only once an off time exists: five `coord_*` goldens snapshot the starts sensor's attributes. A reader of those keys treats an absent key as no observation, never as zero. Control: with the condition removed (the body's mutant `publish_only_observed`) the section's attribute check fails.
+- **The planner's reader, as built by part C** (pull request 3526; items 3656875b, 036facc8). `duty_switch.planner_fields` is the module-level reader, added with its one caller, the coordinator's solve configuration (pinned by the part A section's check "the coordinator names it once, for the planner's read"). It reads `DutySwitchLearner.planner_pairs` from the in-memory learner, never a published key, so a conditional key's absence cannot reach the solve as zero: a direction whose latch is off, an empty learner and a pump never arbitrated read a probability of zero and no off time, which prices nothing. Control: the part C section's check that every below-threshold learner plans identically to today's solve. `n` has a ceiling, `N_CAP`, held at each booking and on each decay (the part C section's check "the cap is held on decay as well as at booking"; mutant: the ceiling on decay dropped turns it red).
 - **The feedback-loop void is wider.** An episode voids on any target the loop moved off the open-loop one (`FeedbackRun.sent_c` set), raised as well as lowered; it costs evidence only.
 - **Origin** (share, lease, other) is not in `SwitchContext`: nothing in A reads it.
 - **Source-leg age** is the age of the mode record the write replaced, not `dhw_since`, which `_leased` has reset by the pass that leaves hot water.
diff --git a/tests/features.py b/tests/features.py
index a663d02b74..5fcaaa7412 100644
--- a/tests/features.py
+++ b/tests/features.py
@@ -89767,6 +89767,22 @@ R.check(
     _dsp_kept(0, 28)[0].usable and not _dsp_kept(0, 29)[0].usable,
     f"n at 28 days {_dsp_kept(0, 28)[0].n!r}, at 29 {_dsp_kept(0, 29)[0].n!r}",
 )
+_dsp_over = _dsp_dir(4.0 * _dsp_ds.N_CAP, 0.0)
+_dsp_over.decay(_DSP_DAY)
+_dsp_over_n0 = _dsp_over.n
+_dsp_over.decay(_DSP_DAY + timedelta(days=29))
+_dsp_over_ctl = _dsp_dir(_dsp_ds.N_CAP, 0.0)
+_dsp_over_ctl.decay(_DSP_DAY + timedelta(days=28))
+R.check(
+    "the cap is held on decay as well as at booking: a record stored at four "
+    "times the cap is held to it by the first pass, p unchanged, and is off a "
+    "day past the 28 a capped direction stays latched (control: that capped "
+    "direction is still latched at 28 days)",
+    abs(_dsp_over_n0 - _dsp_ds.N_CAP) < 1e-9 and _dsp_over.p == 1.0
+    and not _dsp_over.usable and _dsp_over_ctl.usable,
+    f"n after the first pass {_dsp_over_n0!r}, after 29 days {_dsp_over.n!r} "
+    f"usable={_dsp_over.usable}; control usable={_dsp_over_ctl.usable}",
+)
 _dsp_rt = _dsp_ds.DutySwitchLearner({"dhw_space": _dsp_k12, "space_dhw": _dsp_fill})
 _dsp_rt_back = _dsp_ds.DutySwitchLearner.from_record(json.loads(json.dumps(_dsp_rt.stored_record())))
 R.check(
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CLAMP_DROP.273aa7e9.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CLAMP_DROP.273aa7e9.json
new file mode 100644
index 0000000000..d32fdecc86
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CLAMP_DROP.273aa7e9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.decay CLAMP_DROP 273aa7e9",
+  "killed_by": "tests/features.py",
+  "old": "        factor = min(self.weights(when)[1], N_CAP) / n if n > 0.0 else 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CLAMP_DROP (`factor = (self.weights(when)[1]) / n if n > 0.0 else 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.273aa7e9.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.273aa7e9.json
new file mode 100644
index 0000000000..0229b8f3ac
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.273aa7e9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.decay CMP_BOUND 273aa7e9",
+  "killed_by": "tests/features.py",
+  "old": "        factor = min(self.weights(when)[1], N_CAP) / n if n > 0.0 else 1.0",
+  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`factor = min(self.weights(when)[1], N_CAP) / n if n >= 0.0 else 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.50222946.json b/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.50222946.json
deleted file mode 100644
index 112ce1af0a..0000000000
--- a/tests/mutation_ledger/killed_by/duty_switch.py/Direction.decay.CMP_BOUND.50222946.json
+++ /dev/null
@@ -1,6 +0,0 @@
-{
-  "anchor": "custom_components/heatpump_optimizer/duty_switch.py:Direction.decay CMP_BOUND 50222946",
-  "killed_by": "tests/features.py",
-  "old": "        factor = self.weights(when)[1] / n if n > 0.0 else 1.0",
-  "reason": "Recorded by `mutation_table.py --pin-killed`: CMP_BOUND (`factor = self.weights(when)[1] / n if n >= 0.0 else 1.0`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
-}

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
