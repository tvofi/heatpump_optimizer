# Review packet #3555
head: f8b7a41a1e639c8dacbf188ad8054baeb8ffabe7
base: ad95665ea3162167a93b92879c618db5c3a18c93

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=131948855586 success
arch-score / arch-score id=131948760500 success
arm id=131948328105 skipped
budget-raise-gate / budget-raise-gate id=131948760480 success
cancel-superseded id=131948327849 success
codeql id=131948763189 skipped
codeql / Analyze (actions) id=131948744604 success
codeql / Analyze (javascript-typescript) id=131948744706 success
codeql / Analyze (python) id=131948744647 success
gate id=131949484256 failure
governance id=131948762594 skipped
governance / delivery-status id=131948744721 success
governance / delivery-status-publish id=131948747135 skipped
governance / env-matrix id=131948744662 in_progress
governance / instrument-self-tests id=131948744842 in_progress
governance / policy-docs id=131948744685 success
governance / record id=131948747132 skipped
governance / wave-script id=131948744445 success
hassfest id=131948763328 skipped
hassfest / hassfest id=131948744490 success
kernel-points id=131948762611 skipped
pr-contract id=131949485813 skipped
prelude id=131948327693 success
refresh id=131948327258 success
sweep-self id=131949917727 skipped
tests id=131948763551 skipped
tests / arch-instrument id=131949150698 success
tests / briefs id=131948744686 success
tests / browser id=131949150919 success
tests / ci-ratchet id=131951885032 skipped
tests / claims-autofix id=131951657998 skipped
tests / closure-scope id=131948744803 success
tests / closures id=131949150957 success
tests / closures-autofix id=131951884071 skipped
tests / coverage id=131949153879 skipped
tests / coverage-ratchet id=131949154932 skipped
tests / fast (3.14) id=131949150752 success
tests / graders-head-copy id=131949152849 success
tests / lane-proofs id=131951654255 success
tests / mutation id=131948744740 success
tests / mutation-autofix id=131949298801 skipped
tests / mutation-pins id=131949298514 skipped
tests / nightly-ha id=131949153766 skipped
tests / nightly-status id=131948744728 success
tests / replay id=131949153981 skipped
tests / typing id=131949150873 success
validate id=131948762749 skipped
validate / validate-hacs id=131948744705 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 131948744842: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at f8b7a41a1e639c8dacbf188ad8054baeb8ffabe7 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --numstat origin/main...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head

FIGURES: 3 resolved, 1 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: full (first round: no --reviewed-head)

## Three-dot diff
diff --git a/dev/programme/delivery/3555.md b/dev/programme/delivery/3555.md
new file mode 100644
index 0000000000..04eb95d993
--- /dev/null
+++ b/dev/programme/delivery/3555.md
@@ -0,0 +1 @@
+- [#3555](https://github.com/tvofi/heatpump_optimizer/pull/3555) — **open**, roster: land the round-10 roster from handoff/audit-r10-roster b1697d36 (carry-201 entry 6 remeasure) (R10-ROSTER-BATCH24)
diff --git a/dev/programme/rosters/wave-r10-groups.json b/dev/programme/rosters/wave-r10-groups.json
index d1cd7d8568..f47f21caa6 100644
--- a/dev/programme/rosters/wave-r10-groups.json
+++ b/dev/programme/rosters/wave-r10-groups.json
@@ -24983,9 +24983,9 @@
    "architect_note": "",
    "brief": "The self-test of tools/audit/seat/tick_loop.sh runs its TICK-GH rows (lines near 205-215) before it points HPO_TICK_CODE_DIR at its scratch (line near 218), so those rows read the callers real checkout. On a branch checkout behind origin/main on the watched paths one extra TICK-STALE line fails the row grep -c ^TICK- = 2, and ci predict then refuses the handoff of an unrelated group (R10-PROCESS-SLIM part 2, PR 3451). On a detached checkout behind main the restart arm moves the callers HEAD to origin/main. Fix: no self-test row may read or move the callers checkout; failing test first for both shapes (branch checkout behind, detached checkout behind) with a HEAD-unmoved assertion; null control: behind=0 passes before and after. Evidence and controls are in BLOCKED.md at handoff-wip/r10-process-slim-p2 sha 1b45b89b9abfb4313cf661cf4c6712b5a51a86fa. Closure test (owner ruling 2026-11-12): it enters round 10 because every fixer handoff from a branch checkout behind main hits it.",
    "resume": {
-    "stage": "in-progress",
+    "stage": "done",
     "branch": null,
-    "commit": null,
+    "commit": "ad95665ea3162167a93b92879c618db5c3a18c93",
     "last_step": null,
     "next_step": "dispatch a sonnet fixer now",
     "note": "BLOCKED.md of the process-slim-p2 merge repair, sha 1b45b89b",
@@ -25777,7 +25777,8 @@
     "Moved from r10-ci-priority-pause body item ebd4600d on 2026-11-13: Enabling `priority_cancel` needs the after measure above. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL)",
     "Moved from r10-ci-priority-pause body item 1655cf71 on 2026-11-13: `roster_lib.is_hotfix` still treats `kind == \"bug\"` as a hotfix beside `hotfix: true` and the name rule (the existing dispatch-rank checks pin it); carry 3 defines it as the flag or the name only. (into the round-11 opening list held by R10-ROUND-PLAYBOOK-FINAL)",
     "Moved from R10-ROUND-PLAYBOOK-FINAL carry 45 (0-based) on 2026-11-13: Round 11: the scaled settling tail. Measured on `dev/audit/harnesses/boost_press_tail_walk.py`, with both slopes and the heat-free `freeze` twins as the null control: neither formula keeps every press arm within `press_120x1_full`'s |worst| on `tests/boost_drift_replay.py`'s replay. The freeze with no heat walks the scale as far as the press does (-0.0232 vs -0.0237), so the walk comes from the freeze's sample selection, not from the heat. Precondition a future formula must meet: every press arm of the harness within the absolute bound under `slope<new>` at its own merge base, re-measured and not carried from these figures, plus an explanation of the freeze-skip walk. The data such a formula prices on already ships: `BoostState.space_boosted`, persisted as `space_settle/boosted_h`.",
-    "Moved from R10-HOTFIX-LEGACY-CONTROL-DATA carry 0 (0-based) on 2026-11-13 (instrument residue, owner ruling 2026-11-12; the group's data hotfixes 3525 and 3552 are merged): From r10-advisor-steady-start, body item 526f4054: tools/policy/brief_lint.mjs `assertLegacyControl` reads a legacy carry as repaired when its controls lint clean, and a control whose only error is a stale path:line citation lints clean whenever an unrelated line holding the anchor word drifts into the one-line window (this pull request, carry-1412.json, anchor `p_max`). The files left in `LEGACY_CONTROL_FILES` were not surveyed for the same shape. Control to carry: for each member, the carry linted with `legacy: new Set()` and its errors listed by kind; a member whose errors are all of kind `path:line` can turn any later diff's `tests / briefs` red the same way. The destination's brief on handoff/audit-r10-roster 0ff6f3368a already names this survey as its part 2 and cites this item by its earlier id 00444e5b."
+    "Moved from R10-HOTFIX-LEGACY-CONTROL-DATA carry 0 (0-based) on 2026-11-13 (instrument residue, owner ruling 2026-11-12; the group's data hotfixes 3525 and 3552 are merged): From r10-advisor-steady-start, body item 526f4054: tools/policy/brief_lint.mjs `assertLegacyControl` reads a legacy carry as repaired when its controls lint clean, and a control whose only error is a stale path:line citation lints clean whenever an unrelated line holding the anchor word drifts into the one-line window (this pull request, carry-1412.json, anchor `p_max`). The files left in `LEGACY_CONTROL_FILES` were not surveyed for the same shape. Control to carry: for each member, the carry linted with `legacy: new Set()` and its errors listed by kind; a member whose errors are all of kind `path:line` can turn any later diff's `tests / briefs` red the same way. The destination's brief on handoff/audit-r10-roster 0ff6f3368a already names this survey as its part 2 and cites this item by its earlier id 00444e5b.",
+    "carry-201 entry 6 (file removed), remeasure (verbatim from carry-201.json carries[6], omitted when the entry was folded): At your own merge base: `git cat-file -e <base>:tools/audit/seat/tmp_paths.py` must succeed before any job can restore it from the base; then add it to a pinned job's `git checkout \"$PINNED\" --` list in .github/workflows/governance.yml, declare it in tools/policy/field_coverage.mjs's DECLARED map (that program is pinned, so the declaration must already be on main when the pin lands), and run `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` (must report it PINNED, uncovered_files=0), `node tools/policy/field_coverage.mjs` (FIELD COVERAGE ok) and `bash tools/pr/prepr.sh` (its pinned-graders step names a local path for it)."
    ],
    "resume": {
     "stage": "not-started",
@@ -25957,9 +25958,9 @@
    "brief": "HOTFIX, two opener refusals that were not the body's fault (root-cause seat R10-RCA-OPENER-REFUSALS, 2026-11-13). Part 1, open_pr.sh: two openers on one topic (a seat's hand run and open_driver.py's run) share the topic-keyed state dir, but the lock is keyed on the branch, and line 44 renames a second run to fix/<topic>-pr whenever a local fix/<topic> exists. The second run takes another lock, rewrites the shared body.md from handoff-body with no head note, then refuses in op_clear_leftover, and the first run's prepr step 7 refuses the overwritten body ('## Head does not name <merge>'). This happened three times tonight (03:20Z, 04:10Z, 06:10Z). Fix: line 44 does not rename when the topic's opener worktree is registered (git worktree list --porcelain lists it), so the second run takes the same lock and exits BUSY (75) before writing anything. Add a pr_args.sh self-test case run without BR_FIXED, with two openers on one topic. It must fail before the fix (the second run's rc is not 75 and body.md changes) and pass after (rc 75, body.md byte-identical). Null control: a lone run with a stale local fix/<topic> and no registered worktree still takes the -pr name. Tag the new clause with a mut: marker so deleting it fails the case. Also pin the head note: the main-moved fixture's stub pusher refuses a body whose ## Head does not name HEAD, and the note lines carry a mut: marker. Part 2, ci_predict.py: grader_preds runs carry_audit.py check in the ci_tree_run clone without the pr-contract step's round-roster fetch (pr-contract.yml, the step 'Every finding the body records names its destination'). The clone's origin/handoff/audit-r10-roster is therefore the shared repo's stale LOCAL branch, or absent, and a carry routed to a group appended to the round roster since then is predicted BAD-DEST where CI passes. In ci_tree_run, give the clone the round-roster refs the step's fetch yields. Self-test: a body routing to a group present on the root's origin/handoff/audit-r10-roster but absent from a stale local branch predicts BAD-DEST before the fix and nothing after. Null control: a group absent from both refs is still predicted BAD-DEST. Do not change carry_audit.py or the workflow. Verification the body must show: both fail-before and pass-after pairs, both null controls, and bash tools/audit/seat/open_pr.sh --self-test plus python3 tools/pr/ci_predict.py --self-test passing.",
    "carry": [],
    "resume": {
-    "stage": "in-progress",
+    "stage": "done",
     "branch": null,
-    "commit": null,
+    "commit": "cfa868394685dbb2360844aec43d7a8cac4736ab",
     "last_step": null,
     "next_step": "cloud fixer (sonnet)",
     "note": "intake: root-cause seat R10-RCA-OPENER-REFUSALS, 2026-11-13; three opener collisions and one false grader red tonight; overlap admitted (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH): root-cause seat s14 rca-open-pr: two openers collide on one topic body; ci_predict reads a stale roster ref; blocks chain PR opens (intake rule: block on a chain PR)",

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
