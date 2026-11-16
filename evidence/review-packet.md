# Review packet #3654
head: b197da1e6bf2c51ad95aa819a78ed020b3db2549
base: 31255c328918573ef29007dac22d7184a0f0247c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=133168418784 success
arch-score / arch-score id=133168109161 success
arm id=133167799558 skipped
budget-raise-gate / budget-raise-gate id=133168108762 success
cancel-superseded id=133167805259 success
codeql id=133168092247 skipped
codeql / Analyze (actions) id=133168108837 success
codeql / Analyze (javascript-typescript) id=133168108822 success
codeql / Analyze (python) id=133168108792 success
gate id=133168616724 failure
governance id=133168092712 skipped
governance / env-matrix id=133168109087 success
governance / instrument-self-tests id=133168108912 in_progress
governance / policy-docs id=133168108827 success
governance / record id=133168110542 skipped
governance / wave-script id=133168108808 success
hassfest id=133168092436 skipped
hassfest / hassfest id=133168108788 success
kernel-points id=133168111332 skipped
pr-contract id=133168618476 skipped
prelude id=133167805809 success
refresh id=133167805808 success
sweep-self id=133168938425 skipped
tests id=133168092434 skipped
tests / arch-instrument id=133168381876 in_progress
tests / briefs id=133168108806 success
tests / browser id=133168381889 success
tests / closure-scope id=133168108919 success
tests / closures id=133168381885 in_progress
tests / coverage id=133168381842 in_progress
tests / fast (3.14) id=133168381856 in_progress
tests / mutation id=133168108734 success
tests / mutation-autofix id=133168599499 skipped
tests / mutation-pins id=133168599211 skipped
tests / nightly-ha id=133168384411 skipped
tests / nightly-status id=133168108772 failure
tests / replay id=133168384138 skipped
tests / typing id=133168381955 success
validate id=133168092517 skipped
validate / validate-hacs id=133168108709 success

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 133168108912: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
required-wait: required context `gate` reads concluded failure at b197da1e6bf2c51ad95aa819a78ed020b3db2549 in the digest, but merge_train.py classify --pr reads WAIT (pending: gate red: none): classify decides, as bus.sh's dispatch does, and a pending check never refuses

## carry_audit at the head
NOTE body item 806e1101: R11-PRE-TOOLCHAIN-PIN
NOTE body item 9833c393: R11-PRE-TOOLCHAIN-PIN
NOTE body item a00789b0: R11-PRE-TOOLCHAIN-PIN
NOTE body item f7b54cbd: R11-PRE-TOOLCHAIN-PIN
NOTE body item 766671f4: R11-PRE-TOOLCHAIN-PIN
NOTE body item 1eaf8e55: R11-PRE-TOOLCHAIN-PIN
NOTE body item 6fd3d308: R11-PRE-TOOLCHAIN-PIN
NOTE body item 3e0749c4: R11-PRE-TOOLCHAIN-PIN
NOTE body item 0feb43b0: R11-PRE-PARALLEL-PIPELINE: R11-PRE-PARALLEL-PIPELINE resolved on origin/handoff/audit-r10-roster
NOTE body item a62b1fec: R11-PRE-TOOLCHAIN-PIN
NOTE body item 695d23a5: R11-PRE-TOOLCHAIN-PIN
CARRY-AUDIT: 11 finding item(s): 11 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified MODE: FULL -- every test script runs, nothing is scoped out.
             no segment of this names a program this check knows
  ok         python3 -I tools/audit/seat/toolchain.py --self-test
             `tools/audit/seat/toolchain.py` is in the tree at this head
  ok         python3 -I tools/ci/gate.py --self-test
             `tools/ci/gate.py` is in the tree at this head
  ok         python3 tools/audit/seat/prune_refs.py --self-test
             `tools/audit/seat/prune_refs.py` is in the tree at this head
  ok         python3 -I tools/audit/seat/beat_jobs.py --self-test
             `tools/audit/seat/beat_jobs.py` is in the tree at this head
  ok         python3 dev/audit/harnesses/r11_toolchain_mutants.py
             `dev/audit/harnesses/r11_toolchain_mutants.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py record --step toolchain --step ref-pruner
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 921214bf42 --workdir <dir>
             `tests/closure.py` is in the tree at this head
  ok         tools/ci/gate.py changes the gate itself
             `tools/ci/gate.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only
             `tests/env_drift.py` is in the tree at this head
  unverified git grep -n -E '\.\.origin/main|detach[^|]*origin/main|-B [^ ]+ origin/main|origin/main:\$?\{?(rel|tools)' -- tools/audit/seat tools/pr .claude/hooks ':!*selftest*' ':!*/instruments/*' ':!*/fixtures/*'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -ln "pr_args.sh" -- tools/audit/seat ':!*selftest*' ':!*.md'
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -l "pr_tools_fresh" -- tools/audit/seat
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -n -E 'fork_head\(|outside_is_mains' -- tools/audit/seat
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals

FIGURES: 16 resolved, 5 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e
Fix review: merge da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e

bus-nonce: 7675f737dcf9d1a8ebf4413275759678
pending-ci: tests / closures, tests / coverage-ratchet, tests / fast (3.14), tests / graders-head-copy

## Round

Second round, over the reviewed head 7a2b2cdef2283bf3c2f07d70d9a380f9fce0b04e. The packet's `## Review scope` reads delta. The previous verdict blocked only on a merge conflict with main and said that the diff itself was not reviewed. So the PR's own diff (`git diff $(git merge-base origin/main HEAD)...HEAD`, 16 files, instrument/CI only, nothing under `custom_components/`) was reviewed in full at this head, together with the hand-resolved merge da36537f13 (parents 7a2b2cdef2, d4968fe08b). No production delta exists, so nothing widens past the diff.

## Previous finding

- The merge-conflict block is resolved. `git merge-tree --write-tree origin/main da36537f13` exits 0 against origin/main f9b680fee4 (only `LEDGER-MERGE: resolved tests/closures.json`). The four formerly conflicting paths carry both sides at the head. `beat_jobs.py` ROWS/RUN hold main's `scorecard` and the PR's `toolchain-promote`. `governance.yml` holds main's round-metrics step and the PR's toolchain step. INSTRUMENTS.md and `beat_jobs.py.md` hold both entries.

## Head

- The PR's live head moved during review to 911384553f94d18fc6803b6674de27d700ebcb9f, `ci: merge main` by github-actions onto main's 315dda8f62 (#3648). `review_carry.py da36537f13 911384553f` prints `CARRY` (0 non-merge branch-only commits), and 911384553f's tree equals `git merge-tree --write-tree da36537f13 315dda8f62` (ddc49de3c7). By step 12 this verdict carries there through `app_approve.sh --carry`. No figure below was re-taken at 911384553f.

## Evidence

- Mutation proof, fixer's harness (the builder's, not a finder's; the body says no finder harness exists for this group): `python3 dev/audit/harnesses/r11_toolchain_mutants.py` at this head prints `RESULT mutants=26`, `RESULT survived=0`, and every M0 is `null-ok` (ev/selftest-r11_toolchain_mutants.py.txt).
- Reviewer's own mutants (ev/reviewer-mutants-driver.py, ev/reviewer-mutants.txt), each one exact replacement followed by the mutated file's self-test: 9 of 10 were killed. Killed: beat-refusal-silent, beat-no-statefile, beat-held-prefix, walk-no-movable, init-twice, held-runs-2, sha-nonsha-head, status-cancelled-green (gate `status` reading cancelled as green), prune-prefix-loose (`"toolchain" in name`). Survived: scan-unbounded (see Findings).
- Self-tests at this head: `toolchain self-test: 42 checks, 0 failed`; `gate self-test: 120 checks, 0 failed`; `SELF-TEST PASS (79 checks)` (prune_refs); `beat_jobs self-test: 273 checks, 0 failed`. Each matches the body except beat_jobs (see Notes).
- Step 6 class rule: the body's three enumerators re-run at merge base d4968fe08b and at the head give (a) 45/45, (b) 19/20, (c) 22/22. The only new (b) line is `tools/audit/seat/toolchain.py` (ev/enumerator-b-*.txt), which matches the body's claim. The seams they return are dispositioned in the body's Forward-carry.
- Step 4/5: the diff touches no claim file, `VERSION`, manifest, `RELEASE_NOTES.md` or `custom_components/`.
- Step 13: ev/merge-tree.txt; rc 0; no MERGE-CLAIM line.
- Step 7: the body names da36537f13 as its head.
- Step 16: no actuator write is touched.
- CI: `merge_train.py classify da36537f13 --pr 3654` was polled about every 77 s from 06:03 to 06:33 UTC and printed `WAIT da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e pending: gate red: none` throughout (ev/classify.log). Still running at 06:33: tests / closures, tests / coverage-ratchet, tests / fast (3.14), tests / graders-head-copy. Concluded red: `tests / nightly-status` and one `gate` run. Neither is in `merge_train.py owed-reds`, and classify reads gate red: none, so no `## Red checks` answer is owed.
- review_packet render: REFUSE introduced-red (instrument-self-tests in_progress at render); classify decides (ev/review-packet.md).

## Notes

- Note: body-figure: the body quotes `beat_jobs self-test: 261 checks, 0 failed`; this head prints 273 checks, 0 failed. The other twelve rows came in with main's merge, and the body's figures were taken at a2c094d8c0.
- Note: carry-own-group: the own-group carries `R11-PRE-TOOLCHAIN-PIN (item tp2)` were read against fixer.md's two exceptions. Item 806e1101 (ref init and who may push it) is a pending owner decision. The rest are the unbuilt remainder of the approved design's named parts p1/p2, which the body's Friction raises with the orchestrator as a part-line/design mismatch. They were taken as the split-part exception, not as a carry-missing block. The roster (handoff/audit-r10-roster, wave-r11-groups.json) already holds item 806e1101.

## Findings

- Follow-up: `toolchain.py` `choose`'s walk bound `[:SCAN_RUNS]` is unpinned. Removing it leaves `toolchain self-test: 42 checks, 0 failed`, so up to LIST_RUNS=30 runs' job listings could be read per pass with no check failing. It is a cost bound and not a correctness predicate: the walk still stops at the ref and at the first green. Carry: R11-PRE-TOOLCHAIN-PIN

## Delta diff: git diff da36537f137ad9bb8a1cbc8c2fdc60bd7c81df8e b197da1e6bf2c51ad95aa819a78ed020b3db2549
diff --git a/.claude/rules/ratchet-budgets.md b/.claude/rules/ratchet-budgets.md
index f8b475d8ed..71ca3105c5 100644
--- a/.claude/rules/ratchet-budgets.md
+++ b/.claude/rules/ratchet-budgets.md
@@ -14,19 +14,14 @@ paths:
 corpus: a policy file may shrink freely and never grow past its cap. Deliberately
 not the two-sided ratchet `tests/structure.py` applies to code — an "improved and
 not yet recorded" refusal on prose would charge a seat for deleting a paragraph,
-and deletion is what this corpus most needs. That asymmetry has a hole only
-visible when three caps are read together.
+and deletion is what this corpus most needs.
 
 **`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
 plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
 before a seat has read anything. Moving prose out of `CLAUDE.md` into a
-`paths:`-scoped rule therefore lowers it **without deleting a line**. Across the
-split that made `CLAUDE.md` an index the floor fell by more than half while
-`corpus_tokens` moved a fraction of a percent; run `--budgets` for both rather
-than carrying either here, which `brief-citations.md` calls an error outright.
-The scoping is a real improvement — what would be dishonest is recording that
-drop as the ratchet, which hands the next pull request headroom nobody earned and
-prices a scoped rule at zero however far it grows.
+`paths:`-scoped rule therefore lowers it **without deleting a line**. Recording that drop as the ratchet
+hands the next pull request headroom nobody earned and prices a scoped rule at
+zero however far it grows.
 
 **`corpus_tokens` does not move when prose moves — while every capped file is a
 measured one.** It sums the policy files the globs match, so a split between two
@@ -40,9 +35,7 @@ that cannot be complete.
 **`roles` charges a seat for what it loads once it opens a file.** Each entry
 gives an `opens` list — one representative file per surface that role touches —
 and the cap is the floor plus every scoped rule whose globs match one of them.
-The floor is not the cost: at the same split every role paid more than the floor,
-and the record seat more than the whole floor cap that preceded it. A cap only
-the empty session meets is not measuring the thing it is named for. `opens` is a
+`opens` is a
 fixed sample: widening it is an edit a reviewer sees, which stops a cap being met
 by re-measuring against fewer files.
 
@@ -62,9 +55,6 @@ the merged tree — is
 not needed for a collision inside the band, where neither branch edits the line.
 It stays the right move for one larger than the band.
 
-The ratchet is deferred, not disabled: a new brief-sized document is still
-refused, and that arm has to stay red for this to be a ratchet at all.
-
 **Re-record an aggregate down** when `--budgets` shows it more than `_band`
 below its cap, and on any reclassification — the case the next section names.
 
@@ -107,6 +97,16 @@ as a known defect is not a ratchet.
 production, and nonproduct lines per 1000 product lines. Each closes the
 other's hole (splitting production lowers the first, not the second; a pure
 move costs neither). Each cap takes its band as above; the window is frozen.
+
+**A target, not a record** (tvofi, 2026-11-13, card P2):
+`machinery_target_budgets.json` lowers `nonproduction_merges` by `step` every
+`every_merges` merges past its `anchor` (the rule: the program's THE TARGET;
+the enumerator: `--measure`, its target and merges past the anchor). It refuses a
+non-production pull request past it, never a production one or main's push. At
+a round start the orchestrator records the cap down to `--measure` and asks
+the owner for the round's anchor and step: a later anchor or a slower decline
+is a raise. **One in, one out:** a required check (the set
+`merge_train.py owed-reds` prints) enters only in the pull request retiring one.
 **The owner's exemption**: a change proving over 20% improvement in CI time,
 programme completion time, right-first-time or token usage appends its
 `exemptions` entry (number, measure, before, after, each one's command,
diff --git a/.cursor/rules/ratchet-budgets.mdc b/.cursor/rules/ratchet-budgets.mdc
index 92e0f77051..b9b2685906 100644
--- a/.cursor/rules/ratchet-budgets.mdc
+++ b/.cursor/rules/ratchet-budgets.mdc
@@ -9,19 +9,14 @@ alwaysApply: true
 corpus: a policy file may shrink freely and never grow past its cap. Deliberately
 not the two-sided ratchet `tests/structure.py` applies to code — an "improved and
 not yet recorded" refusal on prose would charge a seat for deleting a paragraph,
-and deletion is what this corpus most needs. That asymmetry has a hole only
-visible when three caps are read together.
+and deletion is what this corpus most needs.
 
 **`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
 plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
 before a seat has read anything. Moving prose out of `CLAUDE.md` into a
-`paths:`-scoped rule therefore lowers it **without deleting a line**. Across the
-split that made `CLAUDE.md` an index the floor fell by more than half while
-`corpus_tokens` moved a fraction of a percent; run `--budgets` for both rather
-than carrying either here, which `brief-citations.md` calls an error outright.
-The scoping is a real improvement — what would be dishonest is recording that
-drop as the ratchet, which hands the next pull request headroom nobody earned and
-prices a scoped rule at zero however far it grows.
+`paths:`-scoped rule therefore lowers it **without deleting a line**. Recording that drop as the ratchet
+hands the next pull request headroom nobody earned and prices a scoped rule at
+zero however far it grows.
 
 **`corpus_tokens` does not move when prose moves — while every capped file is a
 measured one.** It sums the policy files the globs match, so a split between two
@@ -35,9 +30,7 @@ that cannot be complete.
 **`roles` charges a seat for what it loads once it opens a file.** Each entry
 gives an `opens` list — one representative file per surface that role touches —
 and the cap is the floor plus every scoped rule whose globs match one of them.
-The floor is not the cost: at the same split every role paid more than the floor,
-and the record seat more than the whole floor cap that preceded it. A cap only
-the empty session meets is not measuring the thing it is named for. `opens` is a
+`opens` is a
 fixed sample: widening it is an edit a reviewer sees, which stops a cap being met
 by re-measuring against fewer files.
 
@@ -57,9 +50,6 @@ the merged tree — is
 not needed for a collision inside the band, where neither branch edits the line.
 It stays the right move for one larger than the band.
 
-The ratchet is deferred, not disabled: a new brief-sized document is still
-refused, and that arm has to stay red for this to be a ratchet at all.
-
 **Re-record an aggregate down** when `--budgets` shows it more than `_band`
 below its cap, and on any reclassification — the case the next section names.
 
@@ -102,6 +92,16 @@ as a known defect is not a ratchet.
 production, and nonproduct lines per 1000 product lines. Each closes the
 other's hole (splitting production lowers the first, not the second; a pure
 move costs neither). Each cap takes its band as above; the window is frozen.
+
+**A target, not a record** (tvofi, 2026-11-13, card P2):
+`machinery_target_budgets.json` lowers `nonproduction_merges` by `step` every
+`every_merges` merges past its `anchor` (the rule: the program's THE TARGET;
+the enumerator: `--measure`, its target and merges past the anchor). It refuses a
+non-production pull request past it, never a production one or main's push. At
+a round start the orchestrator records the cap down to `--measure` and asks
+the owner for the round's anchor and step: a later anchor or a slower decline
+is a raise. **One in, one out:** a required check (the set
+`merge_train.py owed-reds` prints) enters only in the pull request retiring one.
 **The owner's exemption**: a change proving over 20% improvement in CI time,
 programme completion time, right-first-time or token usage appends its
 `exemptions` entry (number, measure, before, after, each one's command,
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index a46806f70f..adb1e7efab 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -872,6 +872,7 @@ jobs:
           set -euo pipefail
           python3 -I tools/audit/archscore/gate.py --self-test
           python3 -I tools/audit/check_scopes.py --self-test --repo .
+          python3 -I tools/audit/enumerate.py --self-test
           python3 -I tools/audit/text_ledger.py --self-test
           # merge_throughput.py's `flow` subcommand (R10-FLOW-BOARD) rides
           # this same self-test: the fixture's exact counts, the unchanged
@@ -1462,7 +1463,7 @@ jobs:
           python3 -I tools/audit/seat/sweep_driver.py --self-test | tee "$RUNNER_TEMP/sweep-driver-self-test.txt"
           grep -Eq '^sweep_driver self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/sweep-driver-self-test.txt"
 
-      - name: Show the beat's Gantt and verdict-audit instruments (sweep_gantt.py, verdict_audit.py) refusing their own fixtures
+      - name: Show the beat's Gantt, verdict-audit and owed-watch instruments (sweep_gantt.py, verdict_audit.py, owed_watch.py) refusing their own fixtures
         id: gantt-and-verdict-audit
         if: ${{ !cancelled() && steps.scope.outputs.gantt-and-verdict-audit == 'true' }}
         run: |
@@ -1471,6 +1472,8 @@ jobs:
           grep -Eq '^sweep_gantt self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/sweep-gantt-self-test.txt"
           python3 -I tools/audit/seat/verdict_audit.py --self-test | tee "$RUNNER_TEMP/verdict-audit-self-test.txt"
           grep -Eq '^verdict_audit self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/verdict-audit-self-test.txt"
+          python3 -I tools/audit/seat/owed_watch.py --self-test | tee "$RUNNER_TEMP/owed-watch-self-test.txt"
+          grep -Eq '^owed_watch self-test: [1-9][0-9]* checks, 0 failed$' "$RUNNER_TEMP/owed-watch-self-test.txt"
 
       - name: Show the survivor-list check (tools/audit/seat/survivor_list.py) refusing its own fixtures
         id: survivor-list
diff --git a/dev/audit/README.md b/dev/audit/README.md
index 3a708b9930..0c0cce43a7 100644
--- a/dev/audit/README.md
+++ b/dev/audit/README.md
@@ -83,26 +83,18 @@ or fixes a red, meaning the required `gate` job's on main (`tools/ci/gate.py`)
 or a self-test red its own pull request introduces, never one inherited from
 main; the rest waits for an instrument window the owner opens. Each round-11
 machinery group names its ground; the merge seat checks it at admission. Of the owner's open-PR cap (`DEFAULT_CAPS` in
-`tools/plan/replan.py`), 10 slots (the owner's count, not a tree value) are reserved for
-`custom_components/` pull requests; a machinery PR never takes one, nor a
+`tools/plan/replan.py`), `PRODUCTION_SLOTS` are production's
+(`pr_cap.py dispatch-gate --machinery`); a machinery PR never takes one, nor a
 production one waits for a machinery slot. A proposal
-is accepted only when its friction blocks a production merge, else ruled LOG
-(`proposal-triage.md`, once per round at round end). Exempt from all three: a proposal proving over 20% on
+is accepted only when its friction blocks a production merge, else ruled LOG.
+Exempt from all three: a proposal proving over 20% on
 CI time, programme completion time, right-first-time rate or token usage,
 against a measured baseline and a null control
 (`dev/governance/rules/ratchet-budgets.md`).
 
 **Round 11's opening plan carries:**
 
-- An owner decision on moving the repository to an organization so the native
-  merge queue replaces the train (a merge-queue ruleset returns HTTP 422 on a
-  user-owned repository; round 10's D13 probe). Weigh plan, visibility, the
-  HACS redirect, App installations, deploy key, ruleset ids and owner-keyed
-  instruments; after a transfer re-probe queue latency, `merge_group` gate
-  names and CI minutes; adopt or decline, and close the held groups the queue
-  makes moot (R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY,
-  R10-FLY-CARRY-DOC-CONTEXT, R10-TRAIN-OVERLAP-GRADE, R10-FLOW-BODY-ONLY (a)).
-  Context: the Lean flow pre-study, section K9 (out of the tree).
+- The organization transfer is ruled out (tvofi, 2026-11-14; `dev/programme/HANDOVER.md`).
 - Intake's baseline: R10-PROTECTION-CENSUS's result,
   `dev/audit/rounds/round10/protection-census/`. On it, B1 (triage batch 245,
   P740) opens the round unless ordered into round 10: on an all-product diff
@@ -164,7 +156,10 @@ Before phase 1, the pickup; each later step is its owner's rule.
    `python3 -c "import sys,glob,json;sys.path[:0]=['tools/audit/seat'];from roster_lib import FINISHED_STAGES as F;r=max(glob.glob('dev/programme/rosters/wave-r*-groups.json'),key=lambda p:int(p.split('-r')[1].split('-')[0]));[print(g['group'],g['resume']['stage']) for g in json.load(open(r))['groups'] if g['resume']['stage'] not in F+('refused',)]"`
 2. Evaluation before the baseline: decision 0018, R11-PRE-OBJECTIVE-FUNCTION, `check_scopes.py`.
 3. Denominator, unreached remainder, added dimensions, D11, D13: R10-DIMENSIONS-FULL-COVERAGE part 2, carried on R11-INTAKE-R10-RESIDUE.
-4. Scope: an owner-filed or outside-filed item folds into the ongoing round
+4. Proposals: the prior round's proposals file and prototypes, in
+   `$HPO_STATE_DIR/r<N-1>/` (`orchestrator.md`, the instrument freeze), ruled by
+   its round-end batch in `dev/programme/triage/`; ACCEPTs are built before finders.
+5. Scope: an owner-filed or outside-filed item folds into the ongoing round
    unless its filer explicitly defers it; silence is not one. Record who, when
    and their words in the group's note (`roster_edit.py set-resume --field note`).
 
diff --git a/dev/audit/config/bundles.json b/dev/audit/config/bundles.json
new file mode 100644
index 0000000000..9c12a90d75
--- /dev/null
+++ b/dev/audit/config/bundles.json
@@ -0,0 +1,19 @@
+{
+  "_doc": "The installs that sent a diagnostics bundle, one entry per bundle: an opaque install label (never an address, a name or an entity id), the bundle's date, the round whose D15 seats read it, the steps of dev/governance/dimensions/D15.md run on it (that round's rotation.json coverage other than none) and the tracked evidence that names it. `python3 tools/audit/enumerate.py d15-installs` prints it and refuses an entry whose evidence is not in the tree. A round appends its bundles here in its register pull request; a round with none reports 0 of the lines printed.",
+  "bundles": [
+    {
+      "install": "install-1",
+      "date": "2026-10-14",
+      "round": 10,
+      "steps": [
+        "M1",
+        "M2",
+        "M3",
+        "M4",
+        "M6",
+        "M7"
+      ],
+      "evidence": "dev/audit/rounds/round10/D15/s1/intake.py"
+    }
+  ]
+}
diff --git a/dev/audit/config/identities.json b/dev/audit/config/identities.json
new file mode 100644
index 0000000000..6967ff841e
--- /dev/null
+++ b/dev/audit/config/identities.json
@@ -0,0 +1,323 @@
+{
+  "_doc": "The identities dev/governance/dimensions/D2.md executes, one entry per identity: the method step it belongs to, an id, the identity in a sentence, and its operating grid. A grid axis is a population axis by name (what `python3 tools/audit/check_scopes.py --repo . --population` prints), `golden` (the SCENARIOS of tests/golden.py), or an inline {axis, levels} where no tracked source holds the levels. `python3 tools/audit/enumerate.py d2-identities` prints the list and `--cells` each identity on each cell of its grid; an axis with no level is refused. An identity a finder executes that is not listed is added here by the round's register pull request.",
+  "identities": [
+    {
+      "step": "M1",
+      "id": "energy-conservation",
+      "identity": "enthalpy change equals delivered heat minus losses per step, to 1e-9 kWh",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M1",
+      "id": "dt-invariance",
+      "identity": "four 15-minute steps against one hour, to the integrator's order",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M1",
+      "id": "batch-parity",
+      "identity": "scalar simulate_step against simulate_trajectory_batch, bit for bit",
+      "grid": [
+        {
+          "axis": "input",
+          "levels": [
+            "space_only",
+            "dhw",
+            "valve",
+            "wood",
+            "coil",
+            "external_heat",
+            "pv"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M1",
+      "id": "power-monotone",
+      "identity": "more power never cools a store",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M1",
+      "id": "buffer-cap-rate",
+      "identity": "the buffer cap clamps a rate, never a state",
+      "grid": [
+        "layout"
+      ]
+    },
+    {
+      "step": "M1",
+      "id": "store-bounds",
+      "identity": "no store crosses a physical bound",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M1",
+      "id": "switch-back-slab",
+      "identity": "over a switch-back interval after a hot-water run the unsensed slab advances by space heat only",
+      "grid": [
+        "layout",
+        "combi_tank"
+      ]
+    },
+    {
+      "step": "M2",
+      "id": "cop-monotone",
+      "identity": "COP monotone in outdoor and flow temperature",
+      "grid": [
+        "climate"
+      ]
+    },
+    {
+      "step": "M2",
+      "id": "carnot-band",
+      "identity": "Carnot fraction inside the stated band",
+      "grid": [
+        "climate"
+      ]
+    },
+    {
+      "step": "M2",
+      "id": "derate-unit-interval",
+      "identity": "every derate in [0, 1]; the defrost derate bounded and continuous at its band edges",
+      "grid": [
+        "climate"
+      ]
+    },
+    {
+      "step": "M2",
+      "id": "capacity-envelope",
+      "identity": "capacity never below demand-at-derate without a reason code",
+      "grid": [
+        "climate",
+        "compressor_modulation"
+      ]
+    },
+    {
+      "step": "M2",
+      "id": "priced-inputs-surface",
+      "identity": "each input of the priced formula derived from the device's own control surface",
+      "grid": [
+        "space_setpoint_unit",
+        "compressor_modulation"
+      ]
+    },
+    {
+      "step": "M3",
+      "id": "predicted-cost-sum",
+      "identity": "predicted_cost equals the sum of price times power times dt",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M3",
+      "id": "savings-identity",
+      "identity": "booked savings equal baseline cost minus realised cost over the booked month",
+      "grid": [
+        "layout",
+        "mixing_valve_mode",
+        {
+          "axis": "month",
+          "levels": [
+            "whole",
+            "upgraded_mid_month_from_previous_release",
+            "buffer_above_curve"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M3",
+      "id": "terminal-credit",
+      "identity": "the terminal credit's sign and magnitude against a re-simulated continuation",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M3",
+      "id": "penalty-scaling",
+      "identity": "every penalty term scales with price_weight",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M3",
+      "id": "gradient-fd",
+      "identity": "the solver's gradient against a central finite difference at random points",
+      "grid": [
+        "golden"
+      ]
+    },
+    {
+      "step": "M4",
+      "id": "price-folding",
+      "identity": "15-minute and hourly prices fold into steps without loss",
+      "grid": [
+        "price_shape",
+        {
+          "axis": "resolution",
+          "levels": [
+            "15min",
+            "hourly"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M4",
+      "id": "dst-and-month-days",
+      "identity": "23-hour, 25-hour and month-boundary days priced once per step",
+      "grid": [
+        {
+          "axis": "day",
+          "levels": [
+            "23h",
+            "25h",
+            "month_boundary"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M4",
+      "id": "capacity-peak-once",
+      "identity": "the capacity tariff charges the monthly peak exactly once",
+      "grid": [
+        "price_shape"
+      ]
+    },
+    {
+      "step": "M4",
+      "id": "grid-fee-windows",
+      "identity": "grid-fee day, night and weekday windows applied piecewise",
+      "grid": [
+        "grid_fee_mode"
+      ]
+    },
+    {
+      "step": "M4",
+      "id": "currency-pv-export",
+      "identity": "currency conversion and the PV export price applied piecewise",
+      "grid": [
+        "price_source"
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "sysid-bias",
+      "identity": "sysid.identify bias, and the confidence gate against the bias it admits",
+      "grid": [
+        {
+          "axis": "noise",
+          "levels": [
+            "white",
+            "quantised_0.1C",
+            "drifting"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "learner-clamps",
+      "identity": "each learner at zero evidence and on its clamp",
+      "grid": [
+        {
+          "axis": "evidence",
+          "levels": [
+            "zero",
+            "on_clamp"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "cross-covariate",
+      "identity": "every learner driven together under error in another's covariate",
+      "grid": [
+        {
+          "axis": "noise",
+          "levels": [
+            "white",
+            "quantised_0.1C",
+            "drifting"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "power-entity-own-estimate",
+      "identity": "a learner fed a power entity that is the pump's own estimate learns nothing from it",
+      "grid": [
+        {
+          "axis": "power_source",
+          "levels": [
+            "metered",
+            "pump_estimate"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "covariate-moved",
+      "identity": "a covariate moved to another sensor resets or re-bases what it fed",
+      "grid": [
+        {
+          "axis": "covariate",
+          "levels": [
+            "indoor",
+            "outdoor",
+            "flow",
+            "tank"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "tank-fall-after-charge",
+      "identity": "the tank reading's fall in the minutes after a charge starts is not booked as draw",
+      "grid": [
+        "combi_tank"
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "draw-range-censored",
+      "identity": "a draw range learned from censored samples does not narrow below the draw it could not observe",
+      "grid": [
+        {
+          "axis": "samples",
+          "levels": [
+            "uncensored",
+            "censored_at_minimum_power"
+          ]
+        }
+      ]
+    },
+    {
+      "step": "M5",
+      "id": "booked-against-metered",
+      "identity": "the plan's booked space energy against a metered month's delivery",
+      "grid": [
+        "layout",
+        "emitter"
+      ]
+    }
+  ]
+}
diff --git a/dev/audit/config/rotation.json b/dev/audit/config/rotation.json
index cab583e94a..feb2ca071a 100644
--- a/dev/audit/config/rotation.json
+++ b/dev/audit/config/rotation.json
@@ -2,7 +2,7 @@
   "_rule": "One entry per dev/governance/dimensions/D<k>.md. steps are its numbered method steps in order: a line opening `<n>. ` is step M<n>, and the id is D<k>.M<n>. rounds[<round>] holds seats (each seat's step list, deep focus first), coverage (step -> deep|spot|none), unfinished ([{step, what}]), returned (seat key -> findings accepted at intake), leads ({raised, converted}) and yield (step -> judge-surviving findings). audit-find.js writes each round's entry (from round 9 its seats come from dev/audit/config/scopes.json, not from this ledger); tools/policy/check-wave-script.mjs refuses a dimension or step the briefs and this file disagree on.",
   "_seeded": "Round 8's seat focuses and reports were not reachable from the local tree (they live in the cloud thread's project files), so every rounds map starts empty. Round 9 dispatches from dev/audit/config/scopes.json, not from this ledger.",
   "D0": {
-    "steps": ["M1", "M2", "M3", "M4", "M5", "M6", "M7"],
+    "steps": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"],
     "rounds": {
       "10": {
         "coverage": {
@@ -749,7 +749,7 @@
     }
   },
   "D15": {
-    "steps": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"],
+    "steps": ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"],
     "rounds": {
       "10": {
         "coverage": {
diff --git a/dev/audit/config/scopes.json b/dev/audit/config/scopes.json
index 9daf5f6a18..57970e69a5 100644
--- a/dev/audit/config/scopes.json
+++ b/dev/audit/config/scopes.json
@@ -26,7 +26,8 @@
    "M4",
    "M5",
    "M6",
-   "M7"
+   "M7",
+   "M8"
   ],
   "axis": {
    "profile": [
@@ -93,7 +94,8 @@
       "**"
      ],
      "steps": [
-      "M7"
+      "M7",
+      "M8"
      ]
     }
    ]
@@ -1134,7 +1136,8 @@
    "M5",
    "M6",
    "M7",
-   "M8"
+   "M8",
+   "M9"
   ],
   "seats": {
    "s1": [
@@ -1168,7 +1171,8 @@
      ],
      "steps": [
       "M7",
-      "M8"
+      "M8",
+      "M9"
      ]
     }
    ]
diff --git a/dev/audit/harnesses/r11_relay_3358_skip.py b/dev/audit/harnesses/r11_relay_3358_skip.py
new file mode 100644
index 0000000000..366281f9f4
--- /dev/null
+++ b/dev/audit/harnesses/r11_relay_3358_skip.py
@@ -0,0 +1,132 @@
+#!/usr/bin/env python3
+"""R11-PRE-RELAY-REBUILD carry 0: #3358's silent skip, replayed on its real commits.
+
+#3358 (branch fix/r10-combi-tank-pr) sat behind handoff/r10-combi-tank-pr 62542627 for
+hours with no trace on the relay's level. This drives one `cloud_relay.sh pass` from a
+given seat directory against a scratch origin holding those commits (objects borrowed
+from this checkout through alternates, refs written directly, nothing pushed):
+
+  case     PR head    handoff/r10-combi-tank-pr   handoff/r10-combi-tank   bodied
+  defect   88f4d521   62542627 (+ body)            577c6974 (+ body)        r10-combi-tank's
+  null     d07f8e9e   62542627 (+ body)            577c6974 (+ body)        both
+
+577c6974 is the head's first parent and stands for the older handoff the relay had applied
+(its last update of #3358 ended OK on 2026-11-09 at an older tip); d07f8e9e is the head the
+handoff was applied at by hand, which contains 62542627. update_pr.sh, approve and dispatch
+are stubs; the stub update records its arguments. Prints, per case:
+
+  RESULT <case>_updated=<0|1> <case>_owed=<level lines naming the PR or the -pr handoff>
+
+Defect at the base seat: updated=0 owed=0 (the silent skip). At the fixed seat: updated=1.
+Null at either seat: updated=0 owed=0 (a head holding its handoff is owed nothing).
+
+    python3 dev/audit/harnesses/r11_relay_3358_skip.py --seat tools/audit/seat
+"""
+from __future__ import annotations
+
+import argparse
+import os
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
+ROOT = repo_root(__file__)
+sys.path.insert(0, str(ROOT / "tests"))
+from throwaway_git import throwaway_git_init  # noqa: E402  the scratch repositories' one builder
+PR = "3358"
+BRANCH = "fix/r10-combi-tank-pr"
+HEAD_DEFECT = "88f4d521eb55e62a5b11246396c3f298e932d5b9"
+HEAD_NULL = "d07f8e9ea5a78bf44ea405ef233ae11ad7e1c211"
+HANDOFF_PR = "6254262796cdec57bec1dec5c0d038ba933a215a"
+HANDOFF_OLD = "577c6974205926e7dbaa178b91af96a229ea02f3"
+MAIN = "b8f67a775137a8032d5c71b34ea64165c1d4613a"
+
+
+def git(*argv: str, cwd: Path, env=None, stdin: str | None = None) -> str:
+    return subprocess.run(["git", *argv], cwd=cwd, env=env, input=stdin, text=True,
+                          capture_output=True, check=True).stdout.strip()
+
+
+def body_commit(origin: Path, names: str) -> str:
+    """An orphan commit holding BODY.md that names the handoff tip (HELD-BODY reads its first 8)."""
+    blob = git("hash-object", "-w", "--stdin", cwd=origin, stdin=f"Closes #9999\n\nCode head: {names}\n")
+    tree = git("mktree", cwd=origin, stdin=f"100644 blob {blob}\tBODY.md\n")
+    env = dict(os.environ, GIT_AUTHOR_NAME="h", GIT_AUTHOR_EMAIL="h@h", GIT_COMMITTER_NAME="h",
+               GIT_COMMITTER_EMAIL="h@h")
+    return git("commit-tree", tree, "-m", "body", cwd=origin, env=env)
+
+
+def run_case(seat: Path, case: str, head: str, scratch: Path) -> "tuple[int, int]":
+    d = scratch / case
+    origin, work, state = d / "o.git", d / "w", d / "state"
+    for p in (origin, work, state, d / "bus"):
+        p.mkdir(parents=True)
+    objects = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=ROOT) + "/objects"
+    throwaway_git_init(origin, "-q", "--bare")
+    (origin / "objects" / "info" / "alternates").write_text(objects + "\n")
+    bodies = {t: body_commit(origin, tip) for t, tip in (("r10-combi-tank-pr", HANDOFF_PR), ("r10-combi-tank", HANDOFF_OLD))}
+    for ref, sha in (("main", MAIN), (BRANCH, head), ("handoff/r10-combi-tank-pr", HANDOFF_PR),
+                     ("handoff/r10-combi-tank", HANDOFF_OLD), ("handoff-body/r10-combi-tank-pr", bodies["r10-combi-tank-pr"]),
+                     ("handoff-body/r10-combi-tank", bodies["r10-combi-tank"])):
+        git("update-ref", f"refs/heads/{ref}", sha, cwd=origin)
+    throwaway_git_init(work, "-q")
+    (work / ".git" / "objects" / "info" / "alternates").write_text(objects + "\n")
+    git("remote", "add", "origin", str(origin), cwd=work)
+    applied = ["r10-combi-tank " + bodies["r10-combi-tank"]]
+    if case == "null":
+        applied.append("r10-combi-tank-pr " + bodies["r10-combi-tank-pr"])
+    (state / "cloud-handoff-bodied").write_text("\n".join(applied) + "\n")
+    stubs = d / "stubs"
+    stubs.mkdir()
+    for name, text in (("prs", f"printf '{PR}\\t{BRANCH}\\t{head}\\n'"), ("merged", ":"),
+                       ("update", f"echo \"$@\" >> {d}/updated"), ("approve", ":"),
+                       ("dispatch", "echo 'bus-nonce: 0123456789abcdef0123456789abcdef'")):
+        (stubs / name).write_text(f"#!/bin/sh\n{text}\n")
+        (stubs / name).chmod(0o755)
+    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "HPO_"))}
+    env.update(HPO_STATE_DIR=str(state), HPO_BUS_STATE=str(d / "bus"), HPO_RELAY_PRS=str(stubs / "prs"),
+               HPO_RELAY_MERGED=str(stubs / "merged"), HPO_RELAY_UPDATE=str(stubs / "update"),
+               HPO_RELAY_APPROVE=str(stubs / "approve"), HPO_RELAY_DISPATCH=str(stubs / "dispatch"))
+    log = state / "cloud-relay.log"
+    subprocess.run(["bash", str(seat / "cloud_relay.sh"), "pass", "--log", str(log)], cwd=work, env=env,
+                   capture_output=True, text=True, timeout=600)
+    updated = (d / "updated").read_text() if (d / "updated").exists() else ""
+    level = Path(str(log) + ".level")
+    owed = [l for l in (level.read_text().splitlines() if level.exists() else [])
+            if f"#{PR}" in l or "handoff/r10-combi-tank-pr" in l]
+    return int(f"{BRANCH} {HANDOFF_PR}" in updated), len(owed)
+
+
+def main(argv) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
+    ap.add_argument("--seat", default=str(ROOT / "tools" / "audit" / "seat"), help="the seat directory whose cloud_relay.sh runs")
+    a = ap.parse_args(argv)
+    seat = Path(a.seat).resolve()
+    for sha in (HEAD_DEFECT, HEAD_NULL, HANDOFF_PR, HANDOFF_OLD, MAIN):
+        if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT).returncode:
+            print(f"UNAVAILABLE: {sha} is not in this checkout (git fetch --unshallow origin)")
+            return 3
+    with tempfile.TemporaryDirectory(prefix="hpo-r11-3358-") as tmp:
+        for case, head in (("defect", HEAD_DEFECT), ("null", HEAD_NULL)):
+            u, o = run_case(seat, case, head, Path(tmp))
+            print(f"RESULT {case}_updated={u} {case}_owed={o}")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/dev/governance/config/machinery_budgets.json b/dev/governance/config/machinery_budgets.json
index 531694e94a..d338a9cd28 100644
--- a/dev/governance/config/machinery_budgets.json
+++ b/dev/governance/config/machinery_budgets.json
@@ -1,8 +1,8 @@
 {
   "_comment": "One-sided caps on what main's merges are spent on, graded by tools/audit/machinery_ratchet.py over the newest window_merges first-parent merges (the counting rule is that program's docstring). Each cap is compared against cap + its _band; re-record a cap down when the measurement falls more than its band below it. Policy: dev/governance/rules/ratchet-budgets.md, the machinery section.",
-  "_recorded": "Measured by `python3 tools/audit/machinery_ratchet.py --measure --window 580 --bands 150` at c3a279e3252a8b57bb00b5a677318cd4fe20387f. window_merges is the owner's fourteen-day count, frozen: a change to it is a raise.",
+  "_recorded": "Caps measured by `python3 tools/audit/machinery_ratchet.py --measure --window 580 --bands 150` at c3a279e3252a8b57bb00b5a677318cd4fe20387f; nonproduction_merges re-recorded down by `python3 tools/audit/machinery_ratchet.py --measure --head origin/main` at b3831ff64eca1936f0b618193ee86c3e337b51a9, more than its band below the cap (churn_per_kilo_product_lines stays: within its band). window_merges is the owner's fourteen-day count, frozen: a change to it is a raise.",
   "window_merges": 580,
-  "nonproduction_merges": 521,
+  "nonproduction_merges": 478,
   "nonproduction_merges_band": 5,
   "churn_per_kilo_product_lines": 14797,
   "churn_per_kilo_product_lines_band": 3636,
diff --git a/dev/governance/config/machinery_target_budgets.json b/dev/governance/config/machinery_target_budgets.json
new file mode 100644
index 0000000000..f28a78ec10
--- /dev/null
+++ b/dev/governance/config/machinery_target_budgets.json
@@ -0,0 +1,7 @@
+{
+  "_comment": "The declining target on machinery_budgets.json's nonproduction_merges (tvofi, 2026-11-13, card P2), graded by tools/audit/machinery_ratchet.py (THE TARGET in its docstring): the cap less `step` for every `every_merges` first-parent merges past `anchor`, binding a non-production candidate only. Policy: dev/governance/rules/ratchet-budgets.md, the machinery section.",
+  "_recorded": "Anchor: the commit nonproduction_merges was recorded at, by `python3 tools/audit/machinery_ratchet.py --measure --head origin/main`. every_merges is half the frozen window_merges (the owner's seven days of merges); step is 10% of the recorded cap, rounded half up (process convergence audit d5d7ff8187, section 6 row a2).",
+  "anchor": "b3831ff64eca1936f0b618193ee86c3e337b51a9",
+  "every_merges": 290,
+  "step": 48
+}
diff --git a/dev/governance/config/policy_budgets.json b/dev/governance/config/policy_budgets.json
index 8dcac4ff93..a1f265ff5a 100644
--- a/dev/governance/config/policy_budgets.json
+++ b/dev/governance/config/policy_budgets.json
@@ -6,7 +6,7 @@
   "_floor_is_not_the_cost": "always_loaded_tokens measures a session that opens nothing. Moving prose out of CLAUDE.md into a paths:-scoped rule lowers it without deleting a line: across the index split the floor fell by more than half while corpus_tokens moved a fraction of a percent. The two caps below are what stop that drop being recorded as headroom -- corpus_tokens does not move when prose moves, and roles charge a seat for what it loads once it opens a file. Policy: .claude/rules/ratchet-budgets.md.",
   "_band": 500,
   "_band_note": "Applies to the five aggregate caps only -- always_loaded_tokens, corpus_tokens and the three roles caps -- which are compared against cap+_band. Per-file caps below are compared exactly and keep zero headroom deliberately. A cap re-recorded to the measured value every time leaves the NEXT pull request refused by the previous seat's arithmetic rather than by its own prose: measured over 2026-09-08..17, twenty consecutive commits sat at exactly zero corpus headroom, 24 of 39 capped files sit there now, and the corpus still rose across a window where the cap was pinned at measured every commit. The recorded cap is the last measurement; the band is the room a seat works in without touching it. Re-record down when the measurement falls more than _band below the cap, and on any reclassification -- .claude/rules/ratchet-budgets.md.",
-  "corpus_tokens": 66226,
+  "corpus_tokens": 67155,
   "roles": {
     "fixer": {
       "opens": [
@@ -53,24 +53,24 @@
     "tests/README.md": 800,
     "tools/audit/README.md": 321,
     "tools/audit/briefs/COMMON.md": 108,
-    "tools/audit/briefs/D0.md": 66,
-    "tools/audit/briefs/D1.md": 60,
+    "tools/audit/briefs/D0.md": 76,
+    "tools/audit/briefs/D1.md": 72,
     "tools/audit/briefs/D10.md": 46,
     "tools/audit/briefs/D11.md": 126,
-    "tools/audit/briefs/D12.md": 71,
+    "tools/audit/briefs/D12.md": 74,
     "tools/audit/briefs/D13.md": 84,
     "tools/audit/briefs/D14.md": 35,
-    "dev/governance/dimensions/D15.md": 37,
+    "dev/governance/dimensions/D15.md": 40,
     "dev/governance/roles/design-review.md": 53,
     "dev/governance/roles/evaluator.md": 27,
     "dev/governance/roles/designer.md": 60,
-    "tools/audit/briefs/D2.md": 53,
+    "tools/audit/briefs/D2.md": 65,
     "tools/audit/briefs/D3.md": 46,
     "tools/audit/briefs/D4.md": 53,
     "tools/audit/briefs/D5.md": 48,
     "tools/audit/briefs/D6.md": 35,
     "tools/audit/briefs/D7.md": 45,
-    "tools/audit/briefs/D8.md": 56,
+    "tools/audit/briefs/D8.md": 63,
     "tools/audit/briefs/D9.md": 65,
     "tools/audit/briefs/fix-review.md": 140,
     "tools/audit/briefs/fixer.md": 315,
@@ -107,25 +107,25 @@
     "tests/README.md": 6686,
     "tools/audit/README.md": 6059,
     "tools/audit/briefs/COMMON.md": 1598,
-    "tools/audit/briefs/D0.md": 926,
-    "tools/audit/briefs/D1.md": 819,
+    "tools/audit/briefs/D0.md": 1112,
+    "tools/audit/briefs/D1.md": 989,
     "tools/audit/briefs/D10.md": 624,
     "tools/audit/briefs/D11.md": 1939,
-    "tools/audit/briefs/D12.md": 916,
+    "tools/audit/briefs/D12.md": 997,
     "tools/audit/briefs/D13.md": 1217,
     "tools/audit/briefs/D14.md": 472,
-    "dev/governance/dimensions/D15.md": 690,
+    "dev/governance/dimensions/D15.md": 824,
     "dev/governance/roles/design-review.md": 778,
     "dev/governance/roles/evaluator.md": 361,
     "dev/governance/roles/designer.md": 878,
-    "tools/audit/briefs/D2.md": 683,
+    "tools/audit/briefs/D2.md": 869,
     "tools/audit/briefs/D3.md": 607,
     "tools/audit/briefs/D4.md": 678,
     "tools/audit/briefs/D5.md": 624,
     "tools/audit/briefs/D6.md": 487,
     "tools/audit/briefs/D7.md": 607,
-    "tools/audit/briefs/D8.md": 808,
-    "tools/audit/briefs/D9.md": 857,
+    "tools/audit/briefs/D8.md": 915,
+    "tools/audit/briefs/D9.md": 901,
     "tools/audit/briefs/fix-review.md": 2775,
     "tools/audit/briefs/fixer.md": 5216,
     "tools/audit/briefs/judge.md": 469,
diff --git a/dev/governance/decisions/0017-outside-contributors-are-adopted-on-our-machine.md b/dev/governance/decisions/0017-outside-contributors-are-adopted-on-our-machine.md
index 5383002294..414348c31d 100644
--- a/dev/governance/decisions/0017-outside-contributors-are-adopted-on-our-machine.md
+++ b/dev/governance/decisions/0017-outside-contributors-are-adopted-on-our-machine.md
@@ -83,11 +83,21 @@ approvals remain in our machinery even for such PRs."*
    refuses every non-merge commit, whatever its subject or author says, and a
    merge whose merge-driver files are not main's. **No tool of ours pushes a
    fork's head to a branch of this repository**: that test would read it as
-   ours.
+   ours. A tool reading the head fetches `refs/pull/<pr>/head` into a local
+   ref only (the train to `refs/remotes/pull/<pr>/head`, where its recarry
+   worktree is detached).
 7. **Unchanged:** verdicts post as `hpo-approver` (0013); merges with main and
    code-owner approvals stay ours (the train merges main into the fork's
-   branch itself, automatically or not at all: on a conflict it parks naming
-   the fork and never resolves); no secret reaches a fork run (the three
+   branch itself, automatically or not at all: `remerge_main.sh --head-repo`
+   asks GitHub's `update-branch` as the hpo-author App at the expected head
+   and reads the result back as the automatic two-parent merge of that head
+   and main; on a conflict or a refused move it parks naming the fork and
+   never resolves). The train's `[OUTSIDE]` class is that park, and also
+   the contract's refusal, a pull request whose head repository and branch
+   could not be read, a checkout copy of the contract that is not
+   origin/main's, a fork head the train could not check out, and an
+   approval of item 5's verdict-driven writers it would post on a fork
+   head; no secret reaches a fork run (the three
    autofix jobs and `mutation-pins` require a same-repository head); a held
    fork run is approved by `hpo-runs` after a read of the diff.
 
diff --git a/dev/governance/decisions/0018-objective-function.md b/dev/governance/decisions/0018-objective-function.md
index 25295d32ad..bbdc86006e 100644
--- a/dev/governance/decisions/0018-objective-function.md
+++ b/dev/governance/decisions/0018-objective-function.md
@@ -412,7 +412,9 @@ measured at this record's landing.
   card. The orchestrator writes two
   things and no others: a closing round's objective record, once, which the
   evaluator re-reads term by term; and, into a card of the evaluation, the
-  owner's ruling in his words with where he gave it (`ruling`). The approving
+  owner's ruling in his words with where he gave it (`ruling`) and, on an
+  accepted card, whether that ruling makes it gate the finders
+  (`gates_finders`, true or false). The approving
   review that pull request owes is what makes the transcription his.
   The evaluator writes the rest of the evaluation and never a ruling. After
   this record lands, adding a term or an object class removes one.
@@ -464,8 +466,9 @@ builds yields a card.
   the `sha` it was given at), `objects` (file to `verdict`, `evidence`, and
   `card` unless `keep`) and `cards` (id to the proposal; the `object` or
   `paths` it changes; `threshold`, `criterion` or `unowned` where it answers
-  one; `decision` `accepted|rejected|deferred` with `ruling`; and `merged`,
-  the commit of an accepted one).
+  one; `decision` `accepted|rejected|deferred` with `ruling`, and
+  `gates_finders` on an accepted one; and `merged`, the commit of an
+  accepted one).
 - **Refuses**: `check_scopes.py --round N`, which `audit-find.js` runs at the
   baseline, exits 1 on a missing record; a term neither read nor NO-READ; a
   read with no finite number or with an enumerator that is no tracked
@@ -477,9 +480,13 @@ builds yields a card.
   reviewer that are one name under case and punctuation, or either the
   orchestrator; a review that is not `approve` at a commit holding these
   same verdicts; an unset owner value or an `unowned` item with no card; a
-  card with no decision or no `ruling`; or an accepted card whose `merged`
-  commit is not on the baseline, predates the review, or does not change the
-  card's file, or whose `threshold` or `criterion` is still unset.
+  card with no decision or no `ruling`; an accepted card with no boolean
+  `gates_finders`; or an accepted card whose `merged` commit is not on the
+  baseline, predates the review, or does not change the card's file, or
+  whose `threshold` or `criterion` is still unset. An accepted card that
+  gates no finder and is not merged is no gap: it builds beside the finders
+  (printed `PARALLEL`), and one still open when P3 starts is the architect's
+  input (`--open-cards`).
 - **Cannot read**: whether the evaluator worked the round it grades or was
   dispatched by the orchestrator it grades. A name is all the record holds,
   and one that hides the role (`orch-r10`) passes. Nor whether a tracked
diff --git a/dev/governance/dimensions/D0.md b/dev/governance/dimensions/D0.md
index d47e071682..344b487e70 100644
--- a/dev/governance/dimensions/D0.md
+++ b/dev/governance/dimensions/D0.md
@@ -31,9 +31,13 @@ schedules, the DHW/space decomposition, the terminal credit, horizon effects).
    challenger, and the gap to the outer bound.
 3. **Feasibility parity** before any "cheaper" verdict: per-step comfort floor
    and ceiling, DHW availability in windows, power bounds, manual pins.
-4. **The grid**: every price profile × weather profile in `tests/profiles.py`
-   (8 × 5), topologies single/two-zone, DHW on/off, valve storage, wood,
-   horizon 6/24/48 h, and the coordinator captures. Report per cell; the
+4. **The grid**: every line of `python3 tools/audit/enumerate.py d0-grid`
+   (price × weather × zones × DHW × plant × horizon) and the coordinator
+   captures. Two plants are there because round 10 drove neither:
+   `flow-setpoint-behind-valve` (pump power set through a flow set-point
+   behind a buffer and a mixing valve: the plan leaves the minimum level when
+   the price spread pays) and `manual-valve-buffer` (the plan differs from the
+   plan with no buffer). Report per cell, examined over that universe; the
    aggregate needs leave-one-out and the most-favourable-cell drop.
 5. **Null control**: the same race at `profiles.prices("flat")`. A gap that
    survives flat prices is not price optimality; name what it is. A real
@@ -43,6 +47,13 @@ schedules, the DHW/space decomposition, the terminal credit, horizon effects).
    not realised.
 7. **Decomposition**: does iterating DHW ↔ space more than once change cost?
    Does the terminal credit change the plan the way its docstring claims?
+8. **Same-information oracle** (decision 0018 section 1). Per grid cell, and
+   per install-day of each bundle `enumerate.py d15-installs` prints: the
+   least cost on the measured house given only the exogenous inputs that
+   existed at each decision time (published prices, the forecast as issued,
+   sensor readings to then, the configuration), never the learned model.
+   Record `C_real`, `C_same` and the model gap `|C_real - C_model|` side by
+   side per install-day; regret is `C_real - C_same`, under step 5's null.
 
 ## Reuse
 
diff --git a/dev/governance/dimensions/D1.md b/dev/governance/dimensions/D1.md
index de0ef9773e..4514d59581 100644
--- a/dev/governance/dimensions/D1.md
+++ b/dev/governance/dimensions/D1.md
@@ -13,40 +13,52 @@ Home Assistant semantics, not the test stub's.
 
 ## Method
 
+Each step's universe is an `enumerate.py` census; `--ledger TSV` (line,
+driving test) prints each line with its test or `not run`. Report examined
+over it.
+
 1. **A real-loop harness.** Subclass `tests/harness.py:FakeHass` so
-   `async_add_executor_job` runs in a `ThreadPoolExecutor` on a real
-   `asyncio` loop, and `async_create_task` schedules instead of closing.
-   Then setup → first refresh → reload mid-solve → unload mid-solve → setup
-   again. Assert no live task, listener, timer or executor future references
-   the torn-down coordinator (`asyncio.all_tasks`, `gc.get_referrers`), no
-   exception escapes, and the new instance's first cycle completes.
-2. **Store corruption fuzzing.** Enumerate every persisted payload
-   (`Store(`, `async_load`, `async_save`, snapshots, ledger, learners,
-   manual plan). Per store, at least 200 seeded mutants of the healthy
-   payload: type swaps, missing keys, `NaN`/`inf`, negative or huge numbers,
-   wrong nesting, truncation, strings where dicts go. Load through the real
-   loader, run one cycle, assert it completes, the corrupt part is quarantined
-   or reset with one log line, and the *next* cycle does not repeat the failure.
-   Add one perturbation to the store-fuzz set: an instant written by a clock ahead of
-   the one that reads it back, driven across a restart.
-3. **Staleness.** Drive the watchdog and every "age" sensor under a frozen
+   `async_add_executor_job` runs in a `ThreadPoolExecutor` on a real `asyncio`
+   loop, and `async_create_task` schedules instead of closing. Then setup →
+   first refresh → reload mid-solve → unload mid-solve → setup again, and a
+   stored override carried across restore then resolve. Per line of `python3
+   tools/audit/enumerate.py d1-lifecycle`, assert no live task, listener,
+   timer or executor future references the torn-down coordinator
+   (`asyncio.all_tasks`, `gc.get_referrers`), no exception escapes, and the
+   new instance's first cycle completes.
+2. **Store corruption fuzzing.** Per line of `enumerate.py d1-stores` (an
+   `upgrade` line is that version's record loaded by this one), at least 200
+   seeded mutants of the healthy payload: type swaps, missing keys,
+   `NaN`/`inf`, negative or huge numbers, wrong nesting, truncation, strings
+   where dicts go. Load through the real loader, run one cycle, assert it
+   completes, the corrupt part is quarantined or reset with one log line, and
+   the *next* cycle does not repeat the failure. Add one perturbation to the
+   store-fuzz set: an instant written by a clock ahead of the one that reads
+   it back, driven across a restart; a save during the learners' load; and the
+   previous release's persisted record driven to the first actuator write (a
+   hold no restart released).
+3. **Staleness.** Per line of `enumerate.py d1-inputs`: the input missing and
+   reporting again inside one interval, a presence entity changing between two
+   scheduled updates, and a price fetch that raises while the last prices
+   still cover now. Drive the watchdog and every "age" sensor under a frozen
    clock jumping forward/back, DST (`tests/hastub` `dt.freeze`,
    `tests/dst_checks.py`), `last_reported` in the future, `unknown` and
    `unavailable` states, a price list that stops updating and an empty
    forecast; check the published and booked value, not only the plan.
-4. **Executor boundary.** From `_solve_record` and `_solve_hubs`,
-   list every `self._*` the solve thread reads and every loop-side writer of
-   them; a race harness mutates each writer mid-solve and checks the plan and
-   the published payload for torn state.
-5. **Guards, waits.** Each swallowing `try/except`: logs once, sets
-   `last_update_success`, recovers, hides no bug? Inject it. Each peer wait
-   (pipe, child, lock): a live, silent peer (`silent_peer_waits.py`) must
+4. **Executor boundary.** `enumerate.py d1-solve-state` lists every `self._*`
+   the solve thread reads; find every loop-side writer of them; a race harness
+   mutates each writer mid-solve and checks the plan and the published payload
+   for torn state.
+5. **Guards, waits.** Each handler of `enumerate.py d1-excepts`: logs once,
+   sets `last_update_success`, recovers, hides no bug? Inject it. Each peer
+   wait (pipe, child, lock): a live, silent peer (`silent_peer_waits.py`) must
    time it out, freeing its hold, unless the wait is its own idle state.
-6. **External-input parsers.** Each parse of input the integration did not
-   produce — ECL110 MQTT, pump-signal states, the Tibber and Open-Meteo
-   responses, the forecast — driven with malformed, non-finite, oversized
-   and hostile payloads: the cycle completes, the failure logs once, the
-   arm is pinned (#1090 pins ECL110's NaN drop; drive the rest).
+6. **External-input parsers.** Each line of `enumerate.py d1-parsers` that
+   parses input the integration did not produce — ECL110 MQTT, pump-signal
+   states, the Tibber and Open-Meteo responses, the forecast — driven with
+   malformed, non-finite, oversized and hostile payloads: the cycle completes,
+   the failure logs once, the arm is pinned (#1090 pins ECL110's NaN drop;
+   drive the rest).
 
 ## Reuse
 
diff --git a/dev/governance/dimensions/D12.md b/dev/governance/dimensions/D12.md
index 5d4b8edb00..aebcccae82 100644
--- a/dev/governance/dimensions/D12.md
+++ b/dev/governance/dimensions/D12.md
@@ -23,22 +23,26 @@ quality-scale miss is out of dimension; carry it rather than re-file it.
 
 ## Method
 
-1. **Inventory the plant the tree already exposes**, from the options
-   pages and the optional entity slots, not from memory. Cross it with
-   `tests/golden.py` `coordinator_scenarios` (`coord_minimal`, `coord_dhw`,
-   `coord_two_zone`, `coord_grid_fee`, `coord_all_features`) and the golden
-   `SCENARIOS` that already toggle valve storage, wood, coil, two-tank and
-   DHW. Derive the cell count; do not carry one.
-2. **Installation axes.** For each cell: hydronic layout (single-zone,
-   two-zone, wood-valve via `thermal_model.py:wood_share`), DHW
-   present or absent, wood present or absent, solar/PV present or absent,
-   and every optional entity both mapped and omitted. Drive setup and one
-   coordinator cycle the way `tests/entities.py` `collect` and
-   `_capture_coordinator` already do.
+1. **Inventory the plant the tree already exposes**, from the options pages
+   and the optional entity slots, not from memory. Cross it with
+   `tests/golden.py` `coordinator_scenarios` and the golden `SCENARIOS` that
+   already toggle valve storage, wood, coil, two-tank and DHW. The universe is
+   `python3 tools/audit/check_scopes.py --repo . --population` (every level,
+   every pair of levels from two axes) plus the card and the blueprints;
+   `python3 tools/audit/enumerate.py d12-cells [--pairs]` prints each cell.
+   Tank volume and house size are continuous: their levels are the flow row's
+   minimum, default and maximum, declared in `dev/audit/config/objective.json`
+   `population`. Keep a cell ledger (TSV: cell, source, asserting test);
+   `d12-cells --ledger` prints each cell with its row or `not run`. A run that
+   asserts nothing examines nothing.
+2. **Installation axes.** For each cell, every optional entity both mapped and
+   omitted: drive setup and one coordinator cycle the way `tests/entities.py`
+   `collect` and `_capture_coordinator` already do.
 3. **Heat-pump axes.** On/off versus modulating (the frequency map and the
    on/off climate path), and the control surfaces the tree already has
-   (climate, number, switch, ECL110 MQTT, Tuya). A surface the tree does
-   not implement is not a cell.
+   (climate, number, switch, ECL110 MQTT, Tuya). A surface the tree does not
+   implement is not a cell. Also a counter-metered pump whose spans hold
+   hot-water charges, and a short boost.
 4. **Usable** means: setup finishes; a plan is published or a named
    refusal explains why not; no path invents a tank, a zone, a sensor or a
    compressor mode the config omitted; an omitted optional entity leaves
diff --git a/dev/governance/dimensions/D15.md b/dev/governance/dimensions/D15.md
index 92b63775e2..f5f4624e02 100644
--- a/dev/governance/dimensions/D15.md
+++ b/dev/governance/dimensions/D15.md
@@ -12,12 +12,15 @@ Read `COMMON.md` first.
 - **Null control:** `tools/replay/dbg_bundle_gen.py`'s synthetic bundle;
   every step runs on it first.
 
-**No real bundle: every step `unfinished`, no finding**; a synthetic-only
-anomaly is a lead.
+**The universe** is `python3 tools/audit/enumerate.py d15-installs`: each
+bundle an install sent, its date and the steps run on it
+(`dev/audit/config/bundles.json`; add this round's). **A round with no real
+bundle reports 0 of those lines, no finding**; a synthetic-only anomaly is
+a lead.
 
 ## Method
 
-1. **Intake and version seam.** Unwrap `debug`; a row's `version` is its release. For a row without one (`integration_version` is the download's): restart gaps are what `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/d15_restart_gaps.py --bundle B` prints; a cycle ran the newest tag (`git for-each-ref refs/tags`) dated before its last gap; a tag after that gap leaves it unknown, never the older. Attribute each anomaly so and re-check it at the baseline; old-version-only is a non-finding, with evidence. A gap is downtime, not a lead, unless the integration ran through it.
+1. **Intake and version seam.** Unwrap `debug`; a row's `version` is its release. For a row without one (`integration_version` is the download's): restart gaps are what `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/d15_restart_gaps.py --bundle B` prints; a cycle ran the newest tag (`git for-each-ref refs/tags`) dated before its last gap; a tag after that gap leaves it unknown, never the older. Attribute each anomaly so and re-check it at the baseline; old-version-only is a non-finding, with evidence. A gap is downtime, not a lead, unless the integration ran through it. A real download whose replay half is empty because one entity id escapes the mask is a finding here.
 2. **Privacy gate.** `tests/replay.py`'s `LEAK_PROBES` controls green, then `export.violations` over the bundle with a planted-credential arm; either failing stops the run.
 3. **Ingest.** `tools/replay/debug_ingest.py --bundle`; `--corrupt accuracy` is its perturbation; a check passing on an empty section is vacuous.
 4. **Store replay.** Each store document through its loader and `store._sanitize` against `store.DOMAINS`: quarantined leaves, refused versions.
@@ -25,6 +28,7 @@ anomaly is a lead.
 6. **Monitor re-run.** Bias and MAE per window, stated; `Cusum` and `SnapshotRing.observe_bias` against the recorded `accuracy_drift` latch.
 7. **Row scan.** `cycle_rows` and `payload_snapshots`: solve failures, `solve_wall_ms` outliers, stale feeds, action against plan, each self-test re-derived.
 8. **Anomaly to seam.** Each step-7 anomaly to its `tests/seam_map.json` seam, reproduced by `debug_replay.py --start/--end` over its window, with the perturbation that moves it.
+9. **Same-information oracle** (decision 0018 section 1; D0 step 8 owns the method). Per install-day of the bundle: `C_real`, `C_same` on the measured house from the exogenous inputs at each decision time, and the model gap beside both.
 
 **The bar.** The replay judges, `debug_ingest.py`'s checks and each step's
 re-derivation are the graders. A finding is re-run by one
diff --git a/dev/governance/dimensions/D2.md b/dev/governance/dimensions/D2.md
index 2e89ba6018..4c41d13a0d 100644
--- a/dev/governance/dimensions/D2.md
+++ b/dev/governance/dimensions/D2.md
@@ -13,13 +13,19 @@ tolerance, not by reading the code.
 
 ## Method
 
+The identities and their grid are the lines of `python3
+tools/audit/enumerate.py d2-identities --cells`
+(`dev/audit/config/identities.json`): each step executes its own and
+reports examined over them; add an identity you execute that is not listed.
+
 1. **Thermal model.** Energy conservation per step (enthalpy change equals
    delivered heat minus losses, to 1e-9 kWh); dt-invariance (four 15-minute
    steps versus one hour, to the integrator's order); scalar `simulate_step`
    versus `simulate_trajectory_batch` bit parity on space-only, DHW, valve,
    wood, coil, external-heat and PV inputs; more power never cools a store;
    the buffer cap clamps a rate, not a state; no store crosses a physical
-   bound in any golden scenario.
+   bound in any golden scenario; over a switch-back interval after a hot-water
+   run the unsensed slab advances by space heat only.
 2. **COP and derates.** COP monotone in outdoor and flow temperature, Carnot
    fraction within the stated band, every derate in [0, 1], defrost derate
    bounded and continuous at the band edges, capacity envelope never below
@@ -27,10 +33,12 @@ tolerance, not by reading the code.
    formula's inputs from the device's own control surface, and mark each a
    modelled term, a documented constant, or out of scope.
 3. **Objective.** `predicted_cost == Σ price·power·dt` on every golden
-   fixture; the savings identity; the terminal credit's sign and magnitude
-   versus a re-simulated continuation; every penalty term's scaling with
-   `price_weight`; the solver's gradient versus a central finite difference
-   at random points (relative error, and where it is worst).
+   fixture; the savings identity, also on a month booked from a valve house
+   with the buffer above the curve and on a ledger month upgraded mid-month
+   from the previous release; the terminal credit's sign and magnitude versus
+   a re-simulated continuation; every penalty term's scaling with
+   `price_weight`; the solver's gradient versus a central finite difference at
+   random points (relative error, and where it is worst).
 4. **Tariff and prices.** Folding 15-minute and hourly prices into steps,
    month boundaries, 23- and 25-hour DST days, the capacity tariff charging
    the monthly peak exactly once, grid-fee day/night and weekday windows,
@@ -38,7 +46,11 @@ tolerance, not by reading the code.
 5. **Estimators.** `sysid.identify` bias under white, quantised (0.1 °C) and
    drifting noise; the confidence gate versus the bias it admits; learner
    clamps; every learner driven together under error in another's covariate,
-   internal gains only at a converged heat-loss level with a genuine gain.
+   internal gains only at a converged heat-loss level with a genuine gain; a
+   power entity that is the pump's own estimate; a covariate moved to another
+   sensor; the tank reading's fall after a charge starts; a learned draw
+   range fed censored samples; the plan's booked space energy against a
+   metered month.
 
 ## Reuse
 
diff --git a/dev/governance/dimensions/D8.md b/dev/governance/dimensions/D8.md
index 427add151d..bfa582525d 100644
--- a/dev/governance/dimensions/D8.md
+++ b/dev/governance/dimensions/D8.md
@@ -12,29 +12,36 @@ Read `COMMON.md` first.
 ## Method
 
 1. **The matrix.** Topologies from `tests/golden.py:coordinator_scenarios()`
-   crossed with feature toggles (DHW, two-zone, valve storage, two-tank,
-   coil, wood, ECL110, PV, capacity tariff, grid fee, Tuya, away): build the
+   crossed with feature toggles (DHW, two-zone, valve storage, two-tank, coil,
+   wood, ECL110, PV, capacity tariff, grid fee, Tuya, away): build the
    coordinator the way `_capture_coordinator` does (inject prices and
    forecasts, run `_build_data_dict`), then construct every entity of every
-   platform through the real `async_setup_entry` (`tests/entities.py:collect`).
-   Run two cycles with changed inputs so staleness is observable.
-2. **Per cell, per entity**: state, availability, `device_class`, `state_class`,
-   unit, `entity_category`, `entity_id`, icon, attributes, `translation_key`,
-   `_attr_entity_registry_enabled_default`; not `None`/`unknown` where the
-   source key exists (map it via `native_value`), numeric where `MEASUREMENT`,
-   tz-aware where `TIMESTAMP`, a listed option where `ENUM`, unit matching
-   `device_class`, `orjson`-serialisable (no numpy scalars, no `NaN`), and the
-   value following the payload between the two cycles. An entity publishing an
-   operating state -- running, heating, idle, off, or a power attributed to
-   the pump -- is checked against the plan's own draw (`current_action["power"]`
-   + `dhw_power`, and `heat_pump_on`) in a DHW-only cell (the Tuya overlay
-   with space heating blocked) and at minimum modulation, never its own
-   derivation; a "summary of a dict" lead is resolved per entity against that
-   oracle, not hand-cleared.
+   platform through the real `async_setup_entry`
+   (`tests/entities.py:collect`). Run two cycles with changed inputs so
+   staleness is observable. The cells are the lines of `python3
+   tools/audit/enumerate.py d8-cells` (entity by state by language);
+   `--ledger TSV` (cell, pinning test) prints each with its test or
+   `not run`. Report examined over them.
+2. **Per cell, per entity**: state, availability, `device_class`,
+   `state_class`, unit, `entity_category`, `entity_id`, icon, attributes,
+   `translation_key`, `_attr_entity_registry_enabled_default`; not
+   `None`/`unknown` where the source key exists (map it via `native_value`),
+   numeric where `MEASUREMENT`, tz-aware where `TIMESTAMP`, a listed option
+   where `ENUM`, unit matching `device_class`, `orjson`-serialisable (no numpy
+   scalars, no `NaN`), and the value following the payload between the two
+   cycles. An entity publishing an operating state -- running, heating, idle,
+   off, or a power attributed to the pump -- is checked against the plan's own
+   draw (`current_action["power"]` + `dhw_power`, and `heat_pump_on`) in a
+   DHW-only cell (the Tuya overlay with space heating blocked) and at minimum
+   modulation, never its own derivation; a "summary of a dict" lead is
+   resolved per entity against that oracle, not hand-cleared. Also: a step's
+   reason on a house whose learned heat-loss scale is above 1.1 under flat
+   weather, and a merged plan slot's average-power attribute on a
+   non-modulating pump with a minimum power.
 3. **Ordering and naming.** Sort every `entity_id` and every display name;
    count where a declared family (`ENTITY_FAMILY_OVERRIDES`, else the key's
-   lead token) is split, and compare `strings.json` with both languages. An
-   undeclared grouping is a proposed declaration change, not a split.
+   lead token) is split, and compare `strings.json` with every translation
+   file. An undeclared grouping is a proposed declaration change, not a split.
 4. **Enabled by default.** Derive a "first hour" list from the README and the
    card, compare with the enabled set, and list what is on that a typical
    user never reads and what is off that the card or the README relies on.
diff --git a/dev/governance/dimensions/D9.md b/dev/governance/dimensions/D9.md
index 76c9677417..e3f6f40e3b 100644
--- a/dev/governance/dimensions/D9.md
+++ b/dev/governance/dimensions/D9.md
@@ -25,7 +25,8 @@ Read `COMMON.md` first. You have an isolated worktree for instrumentation.
   zero-range-bounds fallback (a manual pin; a DHW block consuming the whole
   cap), and each DHW planning loop.
 - **Full solves per cycle** = entries into `_multi_start_minimize` during
-  one coordinator cycle, split by path (main solve, shadow/what-if,
+  one coordinator cycle, split by path: the lines of `python3
+  tools/audit/enumerate.py d9-solves` (main solve, shadow/what-if,
   diagnose, any other).
 - **Longest contiguous GIL hold** = the maximum gap between 1 ms heartbeat
   ticks of a task on a real event loop while the solve runs in a
@@ -34,10 +35,10 @@ Read `COMMON.md` first. You have an isolated worktree for instrumentation.
 - **Loop-thread work per cycle** = `time.thread_time()` on the loop thread
   across one cycle, excluding the executor.
 - **Retained bytes** = `tracemalloc` and deep `sys.getsizeof` of every
-  coordinator collection after N cycles, as a slope per cycle, plus
+  coordinator collection (`enumerate.py d9-collections`) after N cycles, as a slope per cycle, plus
   `ru_maxrss` in a subprocess.
 - **Payload bytes** = JSON bytes of `_build_data_dict` and of every entity's
-  attributes, split by what `_unrecorded_attributes` excludes, per cycle
+  attributes (`enumerate.py d9-attributes`), split by what `_unrecorded_attributes` excludes, per cycle
   and per day.
 
 ## Method
@@ -46,6 +47,7 @@ Read `COMMON.md` first. You have an isolated worktree for instrumentation.
 see `dev/audit/README.md`), each with the header the contract requires, each hooking a named symbol and moving under
 a named perturbation (e.g. `maxiter`, horizon length, cycle count). Use
 `tests/stress.py:reference_solve` as the ruler for every "share of a solve".
+Each row reports examined over its metric's universe.
 2. Then: does the stress gate as shipped detect a synthetic 2× regression
 (inject work into the solve and run its checks)? What can it not see?
 
diff --git a/dev/governance/roles/architect-planner.md b/dev/governance/roles/architect-planner.md
index 5a6b8d1b3e..165fa34f4f 100644
--- a/dev/governance/roles/architect-planner.md
+++ b/dev/governance/roles/architect-planner.md
@@ -2,7 +2,7 @@
 
 You run **P3** of every audit round from round 11 (decision 0015): after the
 judge has verified the register (P2), before any fixer dispatches (P4). One
-opus seat, read-only on code, writing only the plan. The plan goes to
+opus seat, writing only the plan. The plan goes to
 `plan-review.md`, then to the owner; the orchestrator's P4 executes the
 approved plan and records each deviation against it (`orchestrator.md`
 section 2b).
@@ -12,9 +12,10 @@ class-grouped draft roster, an input never dispatched as is; the D7 brief and
 findings; `dev/audit/config/bugclasses.json`; the archscore vector, counters
 and tripwires at the round's fork SHA (`tools/audit/archscore/`);
 `tests/structure_budgets.json`; last round's plan, move ledger and re-chain
-history; the owner's dimension briefs.
+history; the owner's dimension briefs; the evaluation cards open at P3's start
+(`check_scopes.py --round <N> --open-cards`).
 
-**Method:** ATAM scenarios (sensitivity, tradeoff points), fitness functions,
+**Method:** ATAM scenarios, fitness functions,
 a Mikado prerequisite graph, ADRs, a C4 component view.
 
 1. **Draw the component view** at the fork SHA from the code, not last round's
@@ -24,8 +25,8 @@ a Mikado prerequisite graph, ADRs, a C4 component view.
    name, marking the sensitivity and tradeoff points touched.
 3. **Triage every verified finding** as keep, merge (same root at one seam),
    defer (to which round and why) or refuse (back to the judge, with the
-   reason, which only the judge undoes). Every finding appears in the plan
-   once; none is dropped silently.
+   reason, which only the judge undoes). Every finding and open card appears in
+   the plan once; none is dropped silently.
 4. **Group by owning seam, not by file or class.** Each group carries its
    findings, size, seam, hot files and an architect note; its edges come from
    the prerequisite graph. Two groups touching one file is a hot-file order
@@ -74,8 +75,7 @@ weights. It is met only when every condition holds, whatever dS reads:
 - **spread**: at least three scored classes improve, and no metric supplies
   more than 40% of the dS;
 - **checked against holdouts the score does not contain**, none regressing:
-  structure budgets, the tripwires, the behaviour inventory, mutation kill
-  rate and change coupling.
+  the first five fitness functions step 7 names.
 
 The target binds this plan, never a seat: a seat aims at sounder code and is
 never credited for dS alone (`fixer.md` step 17).
diff --git a/dev/governance/roles/orchestrator.md b/dev/governance/roles/orchestrator.md
index fafed23280..1469f9538e 100644
--- a/dev/governance/roles/orchestrator.md
+++ b/dev/governance/roles/orchestrator.md
@@ -105,12 +105,16 @@ whenever you merge.
   `OUTSIDE ... owed=triage` line (`tools/audit/seat/outside_intake.py`) is
   triaged or designed, then wired into a roster group or refused
   (`outside_intake.py refuse`); `owed=answer` goes to `standing-dispatch.md`.
-- **A proposal waits for the round-end triage** (`proposal-triage.md`, once per
-  round; tvofi 2026-11-14): a process, tooling or instrument proposal from the
-  sweep, a seat's result or a verdict is consolidated, never routed before its
-  ruling. Where a mandate lets you act on a recommendation absent the owner,
-  that means adding it to the batch; an ACCEPT reaches the next round's roster
-  citing its ruling. An instrument fix stays local and in-round.
+- **The instrument freeze** (card P11): an instrument fault is worked around
+  by a local prototype runnable in `$HPO_STATE_DIR/r<N>/proto/<id>/`, each use
+  a sweep line `WORKAROUND <id> onset=<UTC> cost=<min>`. Its permanent fix is
+  proposal `<id>` in `$HPO_STATE_DIR/r<N>/`, citing the prototype and its
+  measured effect: `proposal-triage.md` rules all proposals once at round end,
+  duplicates merged, uses and cost summed; ACCEPTs are built before the next
+  round's finders, others refused with numbers. A workaround never touches
+  production code, gates, budgets or reviews. Exempt: a production defect,
+  an owner order, a red required check on main, an owner or outside item. A mandate-taken
+  recommendation joins the batch.
 - **Establish the work is not already done or in flight.** One
   `list_pull_requests` over the open set, and the issue's comments.
 - **Give it the constraints that already exist**: findings carried into its
@@ -127,7 +131,7 @@ whenever you merge.
   shape); it binds them (`fixer.md` 17). A serial chain orders groups whose
   owning seams overlap, not groups that share a file.
 - **A round's scope freezes at its register**: a mid-round finding goes to the
-  next round's unless it is expedite or a size-S fly-in.
+  next round's unless expedite, a size-S fly-in, or an undeferred owner or outside item.
 - **An L or XL group with no approved design, pre-study or prototype is
   designed first** (decision 0014): dispatch `designer.md` when its last
   predecessor dispatches, `design-review.md` at the design's head, and its
diff --git a/dev/governance/rules/ratchet-budgets.md b/dev/governance/rules/ratchet-budgets.md
index f8b475d8ed..71ca3105c5 100644
--- a/dev/governance/rules/ratchet-budgets.md
+++ b/dev/governance/rules/ratchet-budgets.md
@@ -14,19 +14,14 @@ paths:
 corpus: a policy file may shrink freely and never grow past its cap. Deliberately
 not the two-sided ratchet `tests/structure.py` applies to code — an "improved and
 not yet recorded" refusal on prose would charge a seat for deleting a paragraph,
-and deletion is what this corpus most needs. That asymmetry has a hole only
-visible when three caps are read together.
+and deletion is what this corpus most needs.
 
 **`always_loaded_tokens` measures a session that opens nothing.** `CLAUDE.md`
 plus any `.claude/rules/*.md` with no `paths:` key — what the harness loads
 before a seat has read anything. Moving prose out of `CLAUDE.md` into a
-`paths:`-scoped rule therefore lowers it **without deleting a line**. Across the
-split that made `CLAUDE.md` an index the floor fell by more than half while
-`corpus_tokens` moved a fraction of a percent; run `--budgets` for both rather
-than carrying either here, which `brief-citations.md` calls an error outright.
-The scoping is a real improvement — what would be dishonest is recording that
-drop as the ratchet, which hands the next pull request headroom nobody earned and
-prices a scoped rule at zero however far it grows.
+`paths:`-scoped rule therefore lowers it **without deleting a line**. Recording that drop as the ratchet
+hands the next pull request headroom nobody earned and prices a scoped rule at
+zero however far it grows.
 
 **`corpus_tokens` does not move when prose moves — while every capped file is a
 measured one.** It sums the policy files the globs match, so a split between two
@@ -40,9 +35,7 @@ that cannot be complete.
 **`roles` charges a seat for what it loads once it opens a file.** Each entry
 gives an `opens` list — one representative file per surface that role touches —
 and the cap is the floor plus every scoped rule whose globs match one of them.
-The floor is not the cost: at the same split every role paid more than the floor,
-and the record seat more than the whole floor cap that preceded it. A cap only
-the empty session meets is not measuring the thing it is named for. `opens` is a
+`opens` is a
 fixed sample: widening it is an edit a reviewer sees, which stops a cap being met
 by re-measuring against fewer files.
 
@@ -62,9 +55,6 @@ the merged tree — is
 not needed for a collision inside the band, where neither branch edits the line.
 It stays the right move for one larger than the band.
 
-The ratchet is deferred, not disabled: a new brief-sized document is still
-refused, and that arm has to stay red for this to be a ratchet at all.
-
 **Re-record an aggregate down** when `--budgets` shows it more than `_band`
 below its cap, and on any reclassification — the case the next section names.
 
@@ -107,6 +97,16 @@ as a known defect is not a ratchet.
 production, and nonproduct lines per 1000 product lines. Each closes the
 other's hole (splitting production lowers the first, not the second; a pure
 move costs neither). Each cap takes its band as above; the window is frozen.
+
+**A target, not a record** (tvofi, 2026-11-13, card P2):
+`machinery_target_budgets.json` lowers `nonproduction_merges` by `step` every
+`every_merges` merges past its `anchor` (the rule: the program's THE TARGET;
+the enumerator: `--measure`, its target and merges past the anchor). It refuses a
+non-production pull request past it, never a production one or main's push. At
+a round start the orchestrator records the cap down to `--measure` and asks
+the owner for the round's anchor and step: a later anchor or a slower decline
+is a raise. **One in, one out:** a required check (the set
+`merge_train.py owed-reds` prints) enters only in the pull request retiring one.
 **The owner's exemption**: a change proving over 20% improvement in CI time,
 programme completion time, right-first-time or token usage appends its
 `exemptions` entry (number, measure, before, after, each one's command,
diff --git a/dev/programme/delivery/3620.md b/dev/programme/delivery/3620.md
new file mode 100644
index 0000000000..19fc464327
--- /dev/null
+++ b/dev/programme/delivery/3620.md
@@ -0,0 +1 @@
+- [#3620](https://github.com/tvofi/heatpump_optimizer/pull/3620) — **open**, R11-PRE-ROUND-CHECK-GATE: r11 pre round check gate (R11-PRE-ROUND-CHECK-GATE)
diff --git a/dev/programme/delivery/3625.md b/dev/programme/delivery/3625.md
new file mode 100644
index 0000000000..786cfcd28a
--- /dev/null
+++ b/dev/programme/delivery/3625.md
@@ -0,0 +1 @@
+- [#3625](https://github.com/tvofi/heatpump_optimizer/pull/3625) — **open**, R11-PRE-BRIEFS-CENSUS: r11 pre briefs census (R11-PRE-BRIEFS-CENSUS)
diff --git a/dev/programme/delivery/3627.md b/dev/programme/delivery/3627.md
new file mode 100644
index 0000000000..fbf3df267c
--- /dev/null
+++ b/dev/programme/delivery/3627.md
@@ -0,0 +1 @@
+- [#3627](https://github.com/tvofi/heatpump_optimizer/pull/3627) — **open**, R11-PRE-MACHINERY-LIMITER: r11 pre machinery limiter (R11-PRE-MACHINERY-LIMITER)
diff --git a/dev/programme/delivery/3635.md b/dev/programme/delivery/3635.md
new file mode 100644
index 0000000000..a89487468b
--- /dev/null
+++ b/dev/programme/delivery/3635.md
@@ -0,0 +1 @@
+- [#3635](https://github.com/tvofi/heatpump_optimizer/pull/3635) — **open**, R11-PRE-ACK-COMPLETION: r11 pre ack completion (R11-PRE-ACK-COMPLETION)
diff --git a/dev/programme/delivery/3648.md b/dev/programme/delivery/3648.md
new file mode 100644
index 0000000000..45b7976e60
--- /dev/null
+++ b/dev/programme/delivery/3648.md
@@ -0,0 +1 @@
+- [#3648](https://github.com/tvofi/heatpump_optimizer/pull/3648) — **open**, R11-PRE-RELAY-REBUILD: r11 pre relay rebuild (R11-PRE-RELAY-REBUILD)
diff --git a/dev/programme/delivery/3651.md b/dev/programme/delivery/3651.md
new file mode 100644
index 0000000000..e0a9831556
--- /dev/null
+++ b/dev/programme/delivery/3651.md
@@ -0,0 +1 @@
+- [#3651](https://github.com/tvofi/heatpump_optimizer/pull/3651) — **open**, R11-PRE-STANDING-SCRIPTS: r11 pre standing scripts (R11-PRE-STANDING-SCRIPTS)
diff --git a/dev/programme/delivery/3653.md b/dev/programme/delivery/3653.md
new file mode 100644
index 0000000000..986bdc129c
--- /dev/null
+++ b/dev/programme/delivery/3653.md
@@ -0,0 +1 @@
+- [#3653](https://github.com/tvofi/heatpump_optimizer/pull/3653) — **open**, R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3: r11 outside contributor cycle p3 (R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3)
diff --git a/tests/closure.py b/tests/closure.py
index a37fc88894..232f50e428 100644
--- a/tests/closure.py
+++ b/tests/closure.py
@@ -597,6 +597,10 @@ INERT_EXCEPT = (
     # their self-tests, so the tools/audit/seat/ INERT prefix must not hide them.
     "tools/audit/seat/ci_priority.py",
     "tools/audit/seat/ci_pause.py",
+    # R11-PRE-STANDING-SCRIPTS: the tick loads the owed watch (its fired-ledger,
+    # seat-on and FIRE-OWED reads moved there), so that self-test reads it. Same
+    # route as ci_priority.py: the prefix stays INERT, the file joins the closure.
+    "tools/audit/seat/owed_watch.py",
     # ... and that self-test reads these three (pr_cap.py, budget_raise_gate.py,
     # app_approve.sh), which ci_predict's self-test-reads arm names UNDER-SCOPED.
     "tools/audit/seat/pr_cap.py",
diff --git a/tests/closures.json b/tests/closures.json
index b6b5fc9f18..0b459d47fe 100644
--- a/tests/closures.json
+++ b/tests/closures.json
@@ -1999,6 +1999,7 @@
    "tools/audit/seat/ledger.py",
    "tools/audit/seat/merge_train.py",
    "tools/audit/seat/orchestrator_tick.py",
+   "tools/audit/seat/owed_watch.py",
    "tools/audit/seat/plan_page.py",
    "tools/audit/seat/plan_phases.py",
    "tools/audit/seat/plan_table.py",
@@ -4168,6 +4169,7 @@
    "tools/audit/seat/outside_intake.py",
    "tools/audit/seat/outside_intake_selftest.py",
    "tools/audit/seat/owed_unactioned.py",
+   "tools/audit/seat/owed_watch.py",
    "tools/audit/seat/plan_audit.py",
    "tools/audit/seat/plan_page.py",
    "tools/audit/seat/plan_phases.py",
@@ -4512,6 +4514,7 @@
    "dev/audit/harnesses/r10_water_setpoint_feedback.py",
    "dev/audit/harnesses/r10_weekday_range_twins.py",
    "dev/audit/harnesses/r11_plan_page_inventory.py",
+   "dev/audit/harnesses/r11_relay_3358_skip.py",
    "dev/audit/harnesses/r11_toolchain_mutants.py",
    "dev/audit/harnesses/r9_ci2b_closures_merge.py",
    "dev/audit/harnesses/r9_dbg2_selftest_price.py",
diff --git a/tests/layout.json b/tests/layout.json
index 2833b60af7..09758eb01e 100644
--- a/tests/layout.json
+++ b/tests/layout.json
@@ -109,7 +109,7 @@
     "tools/policy/**",
     "tools/pr/**",
     "tools/ci/**",
-    "tools/audit/{judge_batch.py,check_scopes.py,text_ledger.py,carry_audit.py,prepare_baseline.sh,merge_throughput.py,machinery_ratchet.py,worktree_gc.sh,prose_counts_census.py}",
+    "tools/audit/{judge_batch.py,check_scopes.py,enumerate.py,text_ledger.py,carry_audit.py,prepare_baseline.sh,merge_throughput.py,machinery_ratchet.py,worktree_gc.sh,prose_counts_census.py}",
     "tools/audit/seat/**",
     "tools/audit/archscore/**",
     "tools/plan/**",
diff --git a/tests/mutation_ledger/killed_by/__init__.py/_take_fresh_handover.GUARD_OFF.0f14c523.json b/tests/mutation_ledger/killed_by/__init__.py/_take_fresh_handover.GUARD_OFF.0f14c523.json
new file mode 100644
index 0000000000..9f34a87de7
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/__init__.py/_take_fresh_handover.GUARD_OFF.0f14c523.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/__init__.py:_take_fresh_handover GUARD_OFF 0f14c523",
+  "killed_by": "tests/manual_plan.py",
+  "old": "    if age_min > interval_minutes:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/AccuracyTracker.from_dict.GUARD_OFF.556b8211.json b/tests/mutation_ledger/killed_by/accuracy.py/AccuracyTracker.from_dict.GUARD_OFF.556b8211.json
new file mode 100644
index 0000000000..6161a7d54b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/AccuracyTracker.from_dict.GUARD_OFF.556b8211.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:AccuracyTracker.from_dict GUARD_OFF 556b8211",
+  "killed_by": "tests/features.py",
+  "old": "        if isinstance(raw_sigma, dict):",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=8."
+}
diff --git a/tests/mutation_ledger/killed_by/accuracy.py/delivered_ratio.GUARD_OFF.ba96e49d.json b/tests/mutation_ledger/killed_by/accuracy.py/delivered_ratio.GUARD_OFF.ba96e49d.json
new file mode 100644
index 0000000000..ba8d34f75a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/accuracy.py/delivered_ratio.GUARD_OFF.ba96e49d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/accuracy.py:delivered_ratio GUARD_OFF ba96e49d",
+  "killed_by": "tests/features.py",
+  "old": "    if sample.predicted_power_kw <= 0.05 or sample.actual_power_kw <= 0.05:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/away.py/interpret_presence.GUARD_OFF.f0619584.json b/tests/mutation_ledger/killed_by/away.py/interpret_presence.GUARD_OFF.f0619584.json
new file mode 100644
index 0000000000..fc6fff4237
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/away.py/interpret_presence.GUARD_OFF.f0619584.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/away.py:interpret_presence GUARD_OFF f0619584",
+  "killed_by": "tests/features.py",
+  "old": "    if domain in (\"person\", \"device_tracker\"):",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/binary_sensor.py/@module.CONST.c1442a72.json b/tests/mutation_ledger/killed_by/binary_sensor.py/@module.CONST.c1442a72.json
new file mode 100644
index 0000000000..dff59309a1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/binary_sensor.py/@module.CONST.c1442a72.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/binary_sensor.py:<module> CONST c1442a72",
+  "killed_by": "tests/entities.py",
+  "old": "PARALLEL_UPDATES = 0",
+  "reason": "Recorded by `mutation_table.py --drain`: CONST (`PARALLEL_UPDATES = 1.0`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.hvac_action.GUARD_OFF.239df7ad.json b/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.hvac_action.GUARD_OFF.239df7ad.json
new file mode 100644
index 0000000000..8a5cccf13b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/climate.py/HeatPumpOptimizerClimate.hvac_action.GUARD_OFF.239df7ad.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/climate.py:HeatPumpOptimizerClimate.hvac_action GUARD_OFF 239df7ad",
+  "killed_by": "tests/entities.py",
+  "old": "            if self.coordinator.mode == MODE_OFF:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow.async_step_building_describe.RETURN_DEL.fab63fb6.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow.async_step_building_describe.RETURN_DEL.fab63fb6.json
new file mode 100644
index 0000000000..a86bda800a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow.async_step_building_describe.RETURN_DEL.fab63fb6.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_building_describe RETURN_DEL fab63fb6",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            return await self.async_step_building_extras()",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow.async_step_reauth_confirm.RETURN_DEL.a40add26.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow.async_step_reauth_confirm.RETURN_DEL.a40add26.json
new file mode 100644
index 0000000000..ae62322f42
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerConfigFlow.async_step_reauth_confirm.RETURN_DEL.a40add26.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerConfigFlow.async_step_reauth_confirm RETURN_DEL a40add26",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "                return self.async_abort(reason=\"reauth_successful\")",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_quick_setup.GUARD_OFF.30300f01.json b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_quick_setup.GUARD_OFF.30300f01.json
new file mode 100644
index 0000000000..34f15965d2
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/HeatPumpOptimizerOptionsFlow.async_step_quick_setup.GUARD_OFF.30300f01.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:HeatPumpOptimizerOptionsFlow.async_step_quick_setup GUARD_OFF 30300f01",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "            if user_input.get(CONF_AFTER_SAVE) is not None:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json
new file mode 100644
index 0000000000..a4e95f9597
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_user_sensors_sections.GUARD_OFF.cc44e904.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_user_sensors_sections GUARD_OFF cc44e904",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "        if bucket:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.66ee310d.json b/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.66ee310d.json
new file mode 100644
index 0000000000..d0d5e3e457
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/config_flow.py/_widen_to_fit.GUARD_OFF.66ee310d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/config_flow.py:_widen_to_fit GUARD_OFF 66ee310d",
+  "killed_by": "tests/config_flow_steps.py",
+  "old": "    if fitted_high is not None:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/config_flow_steps.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.ee9a2c4c.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.ee9a2c4c.json
new file mode 100644
index 0000000000..2f085f8b70
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_drive_pumps.BOOLOP.ee9a2c4c.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_drive_pumps BOOLOP ee9a2c4c",
+  "killed_by": "tests/features.py",
+  "old": "        if not vvc_entity and not space_entity:",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if not vvc_entity or not space_entity:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.1b67efb1.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.1b67efb1.json
new file mode 100644
index 0000000000..dde79dd817
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_first_refresh_light.RETURN_DEL.1b67efb1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_first_refresh_light RETURN_DEL 1b67efb1",
+  "killed_by": "tests/features.py",
+  "old": "            return _republish_handover_ages(self, handover)",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_energy_totals.BOOLOP.ac0c5c8f.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_energy_totals.BOOLOP.ac0c5c8f.json
new file mode 100644
index 0000000000..90c230acca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._async_load_energy_totals.BOOLOP.ac0c5c8f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._async_load_energy_totals BOOLOP ac0c5c8f",
+  "killed_by": "tests/features.py",
+  "old": "            if isinstance(value, (int, float)) and np.isfinite(np.float64(value)):",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if isinstance(value, (int, float)) or np.isfinite(np.float64(value)):`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._commanded_power.RETURN_DEL.2d46e1fb.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._commanded_power.RETURN_DEL.2d46e1fb.json
new file mode 100644
index 0000000000..988e35401d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._commanded_power.RETURN_DEL.2d46e1fb.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._commanded_power RETURN_DEL 2d46e1fb",
+  "killed_by": "tests/features.py",
+  "old": "        return space + dhw",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._external_heat_override.BOOLOP.91361988.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._external_heat_override.BOOLOP.91361988.json
new file mode 100644
index 0000000000..0ce8655e9d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._external_heat_override.BOOLOP.91361988.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._external_heat_override BOOLOP 91361988",
+  "killed_by": "tests/features.py",
+  "old": "        if probe.ok and probe.value is not None:",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if probe.ok or probe.value is not None:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.8a8ebd20.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.8a8ebd20.json
new file mode 100644
index 0000000000..2ee5d647fe
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._fold_internal_gains.GUARD_OFF.8a8ebd20.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fold_internal_gains GUARD_OFF 8a8ebd20",
+  "killed_by": "tests/features.py",
+  "old": "        if self._internal_gains_profile is None:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._freq_view.GUARD_OFF.d0300875.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._freq_view.GUARD_OFF.d0300875.json
new file mode 100644
index 0000000000..f09efbfe2d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._freq_view.GUARD_OFF.d0300875.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._freq_view GUARD_OFF d0300875",
+  "killed_by": "tests/features.py",
+  "old": "        if mode != \"unconfigured\":",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json
new file mode 100644
index 0000000000..c42b539e06
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator._learning_frozen.GUARD_OFF.f728b131.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._learning_frozen GUARD_OFF f728b131",
+  "killed_by": "tests/features.py",
+  "old": "        if signals.defrosting:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_diagnose_interval.RETURN_DEL.23f341dc.json b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_diagnose_interval.RETURN_DEL.23f341dc.json
new file mode 100644
index 0000000000..95aa1f7690
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/coordinator.py/HeatPumpOptimizerCoordinator.async_diagnose_interval.RETURN_DEL.23f341dc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator.async_diagnose_interval RETURN_DEL 23f341dc",
+  "killed_by": "tests/features.py",
+  "old": "        return report",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/defrost.py/DefrostObservation.any_defrost.CMP_BOUND.1299c7b8.json b/tests/mutation_ledger/killed_by/defrost.py/DefrostObservation.any_defrost.CMP_BOUND.1299c7b8.json
new file mode 100644
index 0000000000..bcfaf57dca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/defrost.py/DefrostObservation.any_defrost.CMP_BOUND.1299c7b8.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/defrost.py:DefrostObservation.any_defrost CMP_BOUND 1299c7b8",
+  "killed_by": "tests/features.py",
+  "old": "        return self.observed and (self.events > 0 or self.duty > 0.0)",
+  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`return self.observed and (self.events >= 0 or self.duty > 0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/defrost.py/derate_from_duty.RETURN_DEL.ce4ef37d.json b/tests/mutation_ledger/killed_by/defrost.py/derate_from_duty.RETURN_DEL.ce4ef37d.json
new file mode 100644
index 0000000000..cad89d2dba
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/defrost.py/derate_from_duty.RETURN_DEL.ce4ef37d.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/defrost.py:derate_from_duty RETURN_DEL ce4ef37d",
+  "killed_by": "tests/features.py",
+  "old": "    return min(DERATE_MAX, max(DERATE_MIN, 1.0 - duty * DEFROST_LOSS_MULTIPLIER))",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._apply_dhw_pins.GUARD_OFF.cccc7c43.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._apply_dhw_pins.GUARD_OFF.cccc7c43.json
new file mode 100644
index 0000000000..c988782a16
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._apply_dhw_pins.GUARD_OFF.cccc7c43.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._apply_dhw_pins GUARD_OFF cccc7c43",
+  "killed_by": "tests/manual_plan.py",
+  "old": "            if pin >= 0.5:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.ae7084dd.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.ae7084dd.json
new file mode 100644
index 0000000000..5a6036d6af
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._dhw_window_floors.CLAMP_DROP.ae7084dd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._dhw_window_floors CLAMP_DROP ae7084dd",
+  "killed_by": "tests/features.py",
+  "old": "            ready_idx = max(0, start_idx - 1)",
+  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`ready_idx = (0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=18."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_cheapest_first.GUARD_OFF.6b97e738.json b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_cheapest_first.GUARD_OFF.6b97e738.json
new file mode 100644
index 0000000000..b9b62e694b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_planner.py/DhwPlanner._plan_dhw_cheapest_first.GUARD_OFF.6b97e738.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_planner.py:DhwPlanner._plan_dhw_cheapest_first GUARD_OFF 6b97e738",
+  "killed_by": "tests/features.py",
+  "old": "        if n_steps == 0 or c_dhw <= 0.0:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/hour_in_windows.CMP_BOUND.167f5778.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/hour_in_windows.CMP_BOUND.167f5778.json
new file mode 100644
index 0000000000..8a6f742df3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/hour_in_windows.CMP_BOUND.167f5778.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:hour_in_windows CMP_BOUND 167f5778",
+  "killed_by": "tests/guard_pins.py",
+  "old": "        if start <= h < end:",
+  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`if start < h < end:`) took tests/guard_pins.py from rc=0 failed=0 to rc=1 failed=2. Each of the 2 sites under this anchor was killed."
+}
diff --git a/tests/mutation_ledger/killed_by/dhw_schedule.py/spec_problem.GUARD_OFF.a35e3a61.json b/tests/mutation_ledger/killed_by/dhw_schedule.py/spec_problem.GUARD_OFF.a35e3a61.json
new file mode 100644
index 0000000000..a323ae776f
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/dhw_schedule.py/spec_problem.GUARD_OFF.a35e3a61.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/dhw_schedule.py:spec_problem GUARD_OFF a35e3a61",
+  "killed_by": "tests/features.py",
+  "old": "    if any(window_minutes(w) < MIN_WINDOW_MINUTES for w in windows):",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/drift.py/Cusum.update.BOOLOP.b55cebf2.json b/tests/mutation_ledger/killed_by/drift.py/Cusum.update.BOOLOP.b55cebf2.json
new file mode 100644
index 0000000000..34e6cac90a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/drift.py/Cusum.update.BOOLOP.b55cebf2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/drift.py:Cusum.update BOOLOP b55cebf2",
+  "killed_by": "tests/features.py",
+  "old": "        if not self.tripped and self.stat >= self.threshold:",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if not self.tripped or self.stat >= self.threshold:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=24."
+}
diff --git a/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatDetector._update_displacement.GUARD_OFF.daf090e0.json b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatDetector._update_displacement.GUARD_OFF.daf090e0.json
new file mode 100644
index 0000000000..029c912b16
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/external_heat.py/ExternalHeatDetector._update_displacement.GUARD_OFF.daf090e0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/external_heat.py:ExternalHeatDetector._update_displacement GUARD_OFF daf090e0",
+  "killed_by": "tests/features.py",
+  "old": "        if mean_temp is not None and obs.hp_tank_temp is not None:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/flow_lift.py/curve_supply_temp.RETURN_DEL.028c3544.json b/tests/mutation_ledger/killed_by/flow_lift.py/curve_supply_temp.RETURN_DEL.028c3544.json
new file mode 100644
index 0000000000..62119a575d
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/flow_lift.py/curve_supply_temp.RETURN_DEL.028c3544.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/flow_lift.py:curve_supply_temp RETURN_DEL 028c3544",
+  "killed_by": "tests/features.py",
+  "old": "    return curve if np.isfinite(curve) else None",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/freq_control.py/FrequencyWatchdog.note_report.GUARD_OFF.64373850.json b/tests/mutation_ledger/killed_by/freq_control.py/FrequencyWatchdog.note_report.GUARD_OFF.64373850.json
new file mode 100644
index 0000000000..5d29e86b56
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/freq_control.py/FrequencyWatchdog.note_report.GUARD_OFF.64373850.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/freq_control.py:FrequencyWatchdog.note_report GUARD_OFF 64373850",
+  "killed_by": "tests/features.py",
+  "old": "        if abs(float(reported) - self.commanded) <= FREQ_DIVERGENCE_HZ:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/grid_fee.py/_parse_rule.GUARD_OFF.96f08365.json b/tests/mutation_ledger/killed_by/grid_fee.py/_parse_rule.GUARD_OFF.96f08365.json
new file mode 100644
index 0000000000..42ef6b5172
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/grid_fee.py/_parse_rule.GUARD_OFF.96f08365.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/grid_fee.py:_parse_rule GUARD_OFF 96f08365",
+  "killed_by": "tests/features.py",
+  "old": "            if hours is not None:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/inputs.py/InputReader.read_bool.GUARD_OFF.1d38d74f.json b/tests/mutation_ledger/killed_by/inputs.py/InputReader.read_bool.GUARD_OFF.1d38d74f.json
new file mode 100644
index 0000000000..4d7a9eca6b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/inputs.py/InputReader.read_bool.GUARD_OFF.1d38d74f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/inputs.py:InputReader.read_bool GUARD_OFF 1d38d74f",
+  "killed_by": "tests/debug_collect.py",
+  "old": "            if reading.problem is None:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/debug_collect.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/manual_plan.py/@module.CONST.eb4c314f.json b/tests/mutation_ledger/killed_by/manual_plan.py/@module.CONST.eb4c314f.json
new file mode 100644
index 0000000000..d6bd743597
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/manual_plan.py/@module.CONST.eb4c314f.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/manual_plan.py:<module> CONST eb4c314f",
+  "killed_by": "tests/manual_plan.py",
+  "old": "PIN_OFF = 0.0",
+  "reason": "Recorded by `mutation_table.py --drain`: CONST (`PIN_OFF = 1.0`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/mixing_valve.py/emitter_delivery.CLAMP_DROP.99fbd6ee.json b/tests/mutation_ledger/killed_by/mixing_valve.py/emitter_delivery.CLAMP_DROP.99fbd6ee.json
new file mode 100644
index 0000000000..ba5d3c0b1e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/mixing_valve.py/emitter_delivery.CLAMP_DROP.99fbd6ee.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/mixing_valve.py:emitter_delivery CLAMP_DROP 99fbd6ee",
+  "killed_by": "tests/features.py",
+  "old": "    return max(0.0, ua * (mix_temp - zone_temp))",
+  "reason": "Recorded by `mutation_table.py --drain`: CLAMP_DROP (`return (0.0)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=46."
+}
diff --git a/tests/mutation_ledger/killed_by/narrative.py/build.BOOLOP.3cefd0cc.json b/tests/mutation_ledger/killed_by/narrative.py/build.BOOLOP.3cefd0cc.json
new file mode 100644
index 0000000000..5a6c78cf38
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/narrative.py/build.BOOLOP.3cefd0cc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/narrative.py:build BOOLOP 3cefd0cc",
+  "killed_by": "tests/features.py",
+  "old": "        if reason not in ZERO_ENERGY_REASONS and entry[\"kwh\"] < 0.05:",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if reason not in ZERO_ENERGY_REASONS or entry[\"kwh\"] < 0.05:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_survival.BOOLOP.2c71ff49.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_survival.BOOLOP.2c71ff49.json
new file mode 100644
index 0000000000..676efd3bf3
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._buffer_survival.BOOLOP.2c71ff49.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._buffer_survival BOOLOP 2c71ff49",
+  "killed_by": "tests/features.py",
+  "old": "            if solar_gains is not None and len(solar_gains)",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if solar_gains is not None or len(solar_gains)`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._publish_breach_reports.GUARD_OFF.979263b5.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._publish_breach_reports.GUARD_OFF.979263b5.json
new file mode 100644
index 0000000000..81fe23aa9a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer._publish_breach_reports.GUARD_OFF.979263b5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer._publish_breach_reports GUARD_OFF 979263b5",
+  "killed_by": "tests/features.py",
+  "old": "                if steps > 0:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.GUARD_OFF.42c879d9.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.GUARD_OFF.42c879d9.json
new file mode 100644
index 0000000000..f1a8ca2789
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.get_current_action.GUARD_OFF.42c879d9.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.get_current_action GUARD_OFF 42c879d9",
+  "killed_by": "tests/features.py",
+  "old": "        if now_s < starts[0]:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=6."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.BOOLOP.9d25ee00.json b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.BOOLOP.9d25ee00.json
new file mode 100644
index 0000000000..5ebb5d4a6c
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/HeatPumpOptimizer.optimize.BOOLOP.9d25ee00.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.optimize BOOLOP 9d25ee00",
+  "killed_by": "tests/manual_plan.py",
+  "old": "                if not rel_s and not rel_d:",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`if not rel_s or not rel_d:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=9."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/_savings_percentage.RETURN_DEL.6d06f326.json b/tests/mutation_ledger/killed_by/optimizer.py/_savings_percentage.RETURN_DEL.6d06f326.json
new file mode 100644
index 0000000000..075f9c62b4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/_savings_percentage.RETURN_DEL.6d06f326.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:_savings_percentage RETURN_DEL 6d06f326",
+  "killed_by": "tests/features.py",
+  "old": "    return float(np.clip(savings / baseline_cost * 100.0, -100.0, 100.0))",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/classify_dhw_steps.GUARD_OFF.1ad39ff0.json b/tests/mutation_ledger/killed_by/optimizer.py/classify_dhw_steps.GUARD_OFF.1ad39ff0.json
new file mode 100644
index 0000000000..22bc15c1b6
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/classify_dhw_steps.GUARD_OFF.1ad39ff0.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:classify_dhw_steps GUARD_OFF 1ad39ff0",
+  "killed_by": "tests/manual_plan.py",
+  "old": "        if legionella_step is not None and i == legionella_step:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/manual_plan.py from rc=0 failed=0 to rc=1 failed=7."
+}
diff --git a/tests/mutation_ledger/killed_by/optimizer.py/classify_space_steps.RETURN_DEL.11ee3edd.json b/tests/mutation_ledger/killed_by/optimizer.py/classify_space_steps.RETURN_DEL.11ee3edd.json
new file mode 100644
index 0000000000..d1c48ae25b
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/optimizer.py/classify_space_steps.RETURN_DEL.11ee3edd.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/optimizer.py:classify_space_steps RETURN_DEL 11ee3edd",
+  "killed_by": "tests/plan_view.py",
+  "old": "    return reasons",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/plan_view.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/presets.py/@module.CONST.38abf329.json b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.38abf329.json
new file mode 100644
index 0000000000..46c9e7fb03
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/presets.py/@module.CONST.38abf329.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/presets.py:<module> CONST 38abf329",
+  "killed_by": "tests/features.py",
+  "old": "_EMITTER_SLAB_TRANSFER_PER_M2 = 0.010",
+  "reason": "Recorded by `mutation_table.py --drain`: CONST (`_EMITTER_SLAB_TRANSFER_PER_M2 = 0.02`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/pump_mode.py/declares_current_option.RETURN_DEL.55305cf5.json b/tests/mutation_ledger/killed_by/pump_mode.py/declares_current_option.RETURN_DEL.55305cf5.json
new file mode 100644
index 0000000000..9dc546c1c4
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/pump_mode.py/declares_current_option.RETURN_DEL.55305cf5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/pump_mode.py:declares_current_option RETURN_DEL 55305cf5",
+  "killed_by": "tests/features.py",
+  "old": "    return any(_fold(option) == current for option in options)",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=17."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/SensorGapAdvisorSensor.native_value.RETURN_DEL.1d3d6803.json b/tests/mutation_ledger/killed_by/sensor.py/SensorGapAdvisorSensor.native_value.RETURN_DEL.1d3d6803.json
new file mode 100644
index 0000000000..92f081c1f9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/SensorGapAdvisorSensor.native_value.RETURN_DEL.1d3d6803.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:SensorGapAdvisorSensor.native_value RETURN_DEL 1d3d6803",
+  "killed_by": "tests/entities.py",
+  "old": "        return float(gaps[0][\"sek_per_month\"])",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/sensor.py/_AccumulatingSensor.extra_state_attributes.RETURN_DEL.91845384.json b/tests/mutation_ledger/killed_by/sensor.py/_AccumulatingSensor.extra_state_attributes.RETURN_DEL.91845384.json
new file mode 100644
index 0000000000..1d4518c0ca
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sensor.py/_AccumulatingSensor.extra_state_attributes.RETURN_DEL.91845384.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sensor.py:_AccumulatingSensor.extra_state_attributes RETURN_DEL 91845384",
+  "killed_by": "tests/entities.py",
+  "old": "        return attrs",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/entities.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/services.py/handle_run_optimization.GUARD_OFF.d465e2dc.json b/tests/mutation_ledger/killed_by/services.py/handle_run_optimization.GUARD_OFF.d465e2dc.json
new file mode 100644
index 0000000000..c798646307
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/services.py/handle_run_optimization.GUARD_OFF.d465e2dc.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/services.py:handle_run_optimization GUARD_OFF d465e2dc",
+  "killed_by": "tests/features.py",
+  "old": "    if not_run:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.observe_bias.GUARD_OFF.b6508d62.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.observe_bias.GUARD_OFF.b6508d62.json
new file mode 100644
index 0000000000..6fb740bd9e
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.observe_bias.GUARD_OFF.b6508d62.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.observe_bias GUARD_OFF b6508d62",
+  "killed_by": "tests/features.py",
+  "old": "        if not self.alarmed and self._bias_days >= BIAS_TRIP_DAYS:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=12."
+}
diff --git a/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.observe_bias.RETURN_DEL.da85b927.json b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.observe_bias.RETURN_DEL.da85b927.json
new file mode 100644
index 0000000000..e864a54023
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/snapshots.py/SnapshotRing.observe_bias.RETURN_DEL.da85b927.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/snapshots.py:SnapshotRing.observe_bias RETURN_DEL da85b927",
+  "killed_by": "tests/features.py",
+  "old": "            return True",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.identify.CMP_BOUND.7c1bc4f5.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.identify.CMP_BOUND.7c1bc4f5.json
new file mode 100644
index 0000000000..20d9042b04
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.identify.CMP_BOUND.7c1bc4f5.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.identify CMP_BOUND 7c1bc4f5",
+  "killed_by": "tests/features.py",
+  "old": "        if solution.shape[0] >= 4:",
+  "reason": "Recorded by `mutation_table.py --drain`: CMP_BOUND (`if solution.shape[0] > 4:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.identify.GUARD_OFF.e99b2bc2.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.identify.GUARD_OFF.e99b2bc2.json
new file mode 100644
index 0000000000..b6f8d37e79
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.identify.GUARD_OFF.e99b2bc2.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.identify GUARD_OFF e99b2bc2",
+  "killed_by": "tests/features.py",
+  "old": "        if len(d2_all) >= 3:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=4."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.0a5eb155.json b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.0a5eb155.json
new file mode 100644
index 0000000000..8b55003249
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/SystemIdentification.step.GUARD_OFF.0a5eb155.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:SystemIdentification.step GUARD_OFF 0a5eb155",
+  "killed_by": "tests/features.py",
+  "old": "            if elapsed >= cfg.relax_hours:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/sysid.py/_slab_series.GUARD_OFF.9cd2a896.json b/tests/mutation_ledger/killed_by/sysid.py/_slab_series.GUARD_OFF.9cd2a896.json
new file mode 100644
index 0000000000..6c69364fb9
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/sysid.py/_slab_series.GUARD_OFF.9cd2a896.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/sysid.py:_slab_series GUARD_OFF 9cd2a896",
+  "killed_by": "tests/features.py",
+  "old": "    if len(dts) < 5:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=2."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.from_config.GUARD_OFF.7c9a299b.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.from_config.GUARD_OFF.7c9a299b.json
new file mode 100644
index 0000000000..e5f0450cec
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.from_config.GUARD_OFF.7c9a299b.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.from_config GUARD_OFF 7c9a299b",
+  "killed_by": "tests/features.py",
+  "old": "        elif two_zone_mode == const.TWO_ZONE_MODE_OFF:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`elif False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=5."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.lower_floor_heat_loss_learned.RETURN_DEL.668b63b1.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.lower_floor_heat_loss_learned.RETURN_DEL.668b63b1.json
new file mode 100644
index 0000000000..f6bfbb5f7a
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.lower_floor_heat_loss_learned.RETURN_DEL.668b63b1.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.lower_floor_heat_loss_learned RETURN_DEL 668b63b1",
+  "killed_by": "tests/features.py",
+  "old": "        return self.lower_floor_heat_loss * self.lower_floor_loss_ratio",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.topology_layout.BOOLOP.02a1dce7.json b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.topology_layout.BOOLOP.02a1dce7.json
new file mode 100644
index 0000000000..7d0e5ae976
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/ThermalParameters.topology_layout.BOOLOP.02a1dce7.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:ThermalParameters.topology_layout BOOLOP 02a1dce7",
+  "killed_by": "tests/features.py",
+  "old": "        elif self.two_zone_enabled and self.wood_tank_configured:",
+  "reason": "Recorded by `mutation_table.py --drain`: BOOLOP (`elif self.two_zone_enabled or self.wood_tank_configured:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=1."
+}
diff --git a/tests/mutation_ledger/killed_by/thermal_model.py/wood_share.GUARD_OFF.4355e005.json b/tests/mutation_ledger/killed_by/thermal_model.py/wood_share.GUARD_OFF.4355e005.json
new file mode 100644
index 0000000000..c1a322f8f1
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/thermal_model.py/wood_share.GUARD_OFF.4355e005.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/thermal_model.py:wood_share GUARD_OFF 4355e005",
+  "killed_by": "tests/features.py",
+  "old": "    if wood_temp >= flow_set:",
+  "reason": "Recorded by `mutation_table.py --drain`: GUARD_OFF (`if False:`) took tests/features.py from rc=0 failed=0 to rc=1 failed=3."
+}
diff --git a/tests/mutation_ledger/killed_by/topology.py/_advisor_edge_params.RETURN_DEL.f181ca3e.json b/tests/mutation_ledger/killed_by/topology.py/_advisor_edge_params.RETURN_DEL.f181ca3e.json
new file mode 100644
index 0000000000..9255c6fd67
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/topology.py/_advisor_edge_params.RETURN_DEL.f181ca3e.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/topology.py:_advisor_edge_params RETURN_DEL f181ca3e",
+  "killed_by": "tests/env_drift.py",
+  "old": "    return dataclass_replace(params, buffer_cooling_rate=value)",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/env_drift.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tests/mutation_ledger/killed_by/topology.py/_place_home.RETURN_DEL.3c9b9a27.json b/tests/mutation_ledger/killed_by/topology.py/_place_home.RETURN_DEL.3c9b9a27.json
new file mode 100644
index 0000000000..ffe13a7977
--- /dev/null
+++ b/tests/mutation_ledger/killed_by/topology.py/_place_home.RETURN_DEL.3c9b9a27.json
@@ -0,0 +1,6 @@
+{
+  "anchor": "custom_components/heatpump_optimizer/topology.py:_place_home RETURN_DEL 3c9b9a27",
+  "killed_by": "tests/env_drift.py",
+  "old": "    return place",
+  "reason": "Recorded by `mutation_table.py --drain`: RETURN_DEL (`pass`) took tests/env_drift.py from rc=0 failed=0 to rc=1 failed=10."
+}
diff --git a/tools/audit/check_scopes.py b/tools/audit/check_scopes.py
index be342617ac..99b47b3220 100644
--- a/tools/audit/check_scopes.py
+++ b/tools/audit/check_scopes.py
@@ -30,8 +30,12 @@ round on rc != 0.
 N starts only when round N-1's OBJECTIVE.json and round N's EVALUATION.json are in the tree at
 --ref, every term is read or NO-READ with its reason, every object file has a verdict with
 evidence from an evaluator who is not its reviewer, and every card carries the owner's decision,
-an accepted one merged at --ref. Each gap is refused by the path or id it names; audit-find.js
-passes its round. --self-test drives a complete record (passes) and one perturbation per rule.
+an accepted one merged at --ref unless the owner's ruling sets its `gates_finders` false: such a
+card unmerged is no gap, printed `PARALLEL <card>` since it builds beside the finders. Each gap is
+refused by the path or id it names; audit-find.js passes its round. --open-cards (with --round)
+prints those cards still open at --ref as JSON {round, ref, open_cards, unmarked_cards} and exits,
+rc 1 with an `UNMARKED <card>` line while an accepted card carries no boolean: run at P3's
+start, it is the architect's input (architect-planner.md). --self-test drives a complete record (passes) and one perturbation per rule.
 The record also needs: an approving review at a commit in --ref's history whose EVALUATION.json
 graded the same objects, a ruling on every decided card, an accepted card's commit after that review
 and changing the card's file, reads that are numbers with a tracked enumerator, NO-READs that name
@@ -292,14 +296,16 @@ def open_builders(tree, show):
     return {k for k, g in groups.items() if roster_lib.carry_receivable(g)}
 
 
-def evaluation_gaps(rnd, tree, show, merged, anc, changed):
+def evaluation_gaps(rnd, tree, show, merged, anc, changed, parallel=None):
     """Why round `rnd` may not start, one line per gap, [] when it may.
     `show(path, at=None)` is the file's text at the ref (or at commit `at`);
     `merged(sha)` says whether the ref contains that commit, `anc(a, b)` whether
     a is an ancestor of or equal to b, `changed(sha)` the paths it changed
     against its first parent. The terms and the object globs come from
     OBJECTIVE at the ref, so the record is checked against the definition it
-    was written under, and neither list is carried here."""
+    was written under, and neither list is carried here. An accepted card
+    whose `gates_finders` (the owner's ruling) is false and that is not merged
+    at the ref is no gap: its id is appended to `parallel`, when given."""
     spec = json.loads(show(OBJECTIVE))
     prev, path = records(rnd)
     gaps, terms, builders, groups = [], {}, [], open_builders(tree, show)
@@ -331,7 +337,7 @@ def evaluation_gaps(rnd, tree, show, merged, anc, changed):
     ev = json.loads(show(path))
     if ev.get("round") != rnd or ev.get("reads") != prev:
         gaps.append(f"{path} is not round {rnd}'s evaluation of {prev}")
-    seat, rev = (norm(ev.get(k, "")) for k in ("evaluator", "reviewer"))
+    seat, rev = (norm(ev[k]) if full(ev.get(k)) else "" for k in ("evaluator", "reviewer"))
     if not seat or not rev or seat == rev or "orchestrator" in seat or "orchestrator" in rev:
         gaps.append(f"{path} evaluator {seat!r} and reviewer {rev!r} must be two seats, neither the orchestrator")
     cards, rows = ev.get("cards", {}), ev.get("objects", {})
@@ -373,6 +379,13 @@ def evaluation_gaps(rnd, tree, show, merged, anc, changed):
             continue
         c = card.get("merged")
         want = {x for x in (card.get("object"), *(card.get("paths") or ())) if x}
+        gating = card.get("gates_finders")
+        if not isinstance(gating, bool):
+            gaps.append(f"{path} card {cid} is accepted and carries no boolean gates_finders (the owner's ruling on whether it gates the finders)")
+        elif not gating and not (c and merged(c)):
+            if parallel is not None:
+                parallel.append(cid)
+            continue
         if not (c and merged(c)):
             gaps.append(f"{path} card {cid} is accepted and not merged at this ref")
         elif revsha and anc(c, revsha):
@@ -408,6 +421,57 @@ def evaluation_gaps(rnd, tree, show, merged, anc, changed):
     return gaps
 
 
+def open_cards_report(rnd, tree, show, merged, anc, changed):
+    """--open-cards: (JSON object, rc, UNMARKED lines). The accepted cards that
+    gate no finder and are unmerged at the ref are P3's input; an accepted card
+    with no boolean `gates_finders` could be either, so it is named and the
+    listing fails (rc 1) rather than printing a list that omits it."""
+    out = []
+    evaluation_gaps(rnd, tree, show, merged, anc, changed, out)
+    cards = json.loads(show(records(rnd)[1])).get("cards", {})
+    unmarked = sorted(cid for cid, c in cards.items()
+                      if c.get("decision") == "accepted" and not isinstance(c.get("gates_finders"), bool))
+    lines = [f"UNMARKED {cid}: accepted, no boolean gates_finders (the owner's ruling on finder gating)" for cid in unmarked]
+    return {"round": rnd, "open_cards": sorted(out), "unmarked_cards": unmarked}, 1 if unmarked else 0, lines
+
+
+def open_cards_cli():
+    """(marked, unmarked): `--open-cards --round 8` run whole, as a subprocess
+    of this file, on two commits of a scratch repository whose round-8 record
+    differs only in C2 and C3's `gates_finders`: booleans in the first, absent
+    and the string "true" in the second. C1 is accepted, non-gating, unmerged."""
+    prev, path = records(8)
+    cards = {"C1": {"decision": "accepted", "ruling": "R1", "gates_finders": False, "merged": "0" * 40},
+             "C2": {"decision": "accepted", "ruling": "R2", "gates_finders": True},
+             "C3": {"decision": "accepted", "ruling": "R3", "gates_finders": True},
+             "C4": {"decision": "rejected", "ruling": "R4"}}
+    unmarked = copy.deepcopy(cards)
+    del unmarked["C2"]["gates_finders"]
+    unmarked["C3"]["gates_finders"] = "true"
+    from throwaway_git import throwaway_git_init  # the one way to build a scratch repo; main() put tests/ on the path
+    with tempfile.TemporaryDirectory() as d:
+        env = throwaway_git_init(d, "-q")
+        git = lambda *a: subprocess.run(["git", "-C", d, *a], env=env, capture_output=True, text=True, check=True).stdout.strip()
+        runs = []
+        for cs in (cards, unmarked):
+            for f, body in ((OBJECTIVE, {"terms": [], "objects": {}}), (prev, {"terms": {}}),
+                            (path, {"round": 8, "reads": prev, "cards": cs})):
+                (Path(d) / f).parent.mkdir(parents=True, exist_ok=True)
+                (Path(d) / f).write_text(json.dumps(body))
+            git("add", "-A")
+            git("commit", "-q", "-m", "record")
+            runs.append(subprocess.run([sys.executable, str(Path(__file__).resolve()), "--repo", d, "--ref", git("rev-parse", "HEAD"),
+                                        "--round", "8", "--open-cards"], env=env, capture_output=True, text=True))
+    return tuple(runs)
+
+
+def json_or_none(text):
+    try:
+        return json.loads(text)
+    except ValueError:
+        return None
+
+
 def population(axes, tree, show):
     """(lines, ok): the install population's levels per axis as read from the
     sources at the ref, then the totals. An axis that cannot be read prints
@@ -546,16 +610,22 @@ def evaluation_self_test(tree, show):
     good = {"round": 8, "reads": prev, "evaluator": "evaluator-r8", "reviewer": "plan-review-r8",
             "review": {"verdict": "approve", "sha": "rev"},
             "objects": {f: {"verdict": "keep", "evidence": "e"} for f in objs},
-            "cards": {"C1": {"decision": "accepted", "ruling": "R1", "merged": "abc", "object": ME},
+            "cards": {"C1": {"decision": "accepted", "ruling": "R1", "gates_finders": True, "merged": "abc", "object": ME},
                       "C2": {"decision": "rejected", "ruling": "R2", "unowned": "u", "threshold": "floor", "criterion": "D4"}}}
     good["objects"][objs[0]] = {"verdict": "change", "evidence": "e", "card": "C1"}
     # commits: old is an ancestor of the review rev, abc is after it
-    def run(ev=good, tm=terms, drop=(), sp=spec, revdoc=None, merged=lambda sha: sha in ("abc", "rev", "old")):
+    def run(ev=good, tm=terms, drop=(), sp=spec, revdoc=None, merged=lambda sha: sha in ("abc", "rev", "old"), parallel=None, check=None):
         files = {OBJECTIVE: json.dumps(sp), prev: json.dumps({"terms": tm}), path: json.dumps(ev), roster: json.dumps(groups)}
         sh = lambda f, at=None: (revdoc or json.dumps({"objects": ev.get("objects")})) if at else files[f]
-        return evaluation_gaps(8, (tree | set(files)) - set(drop), sh, merged,
-                               lambda a, b: (a, b) in (("old", "rev"), ("rev", "rev")),
-                               lambda c: {"abc": {ME}, "old": {ME}}.get(c, set()))
+        args = (8, (tree | set(files)) - set(drop), sh, merged, lambda a, b: (a, b) in (("old", "rev"), ("rev", "rev")),
+                lambda c: {"abc": {ME}, "old": {ME}}.get(c, set()))
+        return check(*args) if check else evaluation_gaps(*args, parallel)
+    # --open-cards' report, the function main() prints: (JSON object, rc, UNMARKED lines).
+    report = lambda ev=good, **kw: run(ev, check=open_cards_report, **kw)
+    def beside(ev=good, **kw):
+        """(gaps, ids of the cards building beside the finders) of one run."""
+        out = []
+        return run(ev, parallel=out, **kw), out
     def edit(fn, base=good):
         c = copy.deepcopy(base)
         fn(c)
@@ -585,6 +655,38 @@ def evaluation_self_test(tree, show):
         "a change with no card is refused": only(run(edit(lambda c: c["objects"][objs[0]].pop("card"))), objs[0] + " names no card"),
         "an undecided card is refused": only(run(edit(lambda c: c["cards"]["C2"].pop("decision"))), "card C2 carries no owner decision"),
         "an accepted card not merged is refused": only(run(merged=lambda sha: sha != "abc"), "card C1 is accepted and not merged"),
+        # Finder gating (tvofi 2026-11-15): only a card the owner's ruling makes
+        # gate the finders (`gates_finders` true) holds the round's start; one
+        # that does not, unmerged, builds beside the finders, never a gap.
+        "a complete record lists nothing beside the finders": beside() == ([], []),
+        "a gating accepted card not merged is refused and not listed beside":
+            (lambda r: only(r[0], "card C1 is accepted and not merged") and r[1] == [])(beside(merged=lambda sha: sha != "abc")),
+        "a non-gating accepted card not merged passes and is listed beside":
+            beside(card("C1", gates_finders=False), merged=lambda sha: sha != "abc") == ([], ["C1"]),
+        "a non-gating unmerged card's unset value is no gap, it builds with the card":
+            beside(card("C1", gates_finders=False, threshold="floor"), merged=lambda sha: sha != "abc") == ([], ["C1"]),
+        "a non-gating merged card is checked as any accepted card":
+            only(run(card("C1", gates_finders=False, merged="old")), "is not after the review") and beside(card("C1", gates_finders=False)) == ([], []),
+        "an accepted card with no boolean gates_finders is refused, in every shape":
+            all(only(run(ev), "card C1 is accepted and carries no boolean gates_finders")
+                for ev in [edit(lambda c: c["cards"]["C1"].pop("gates_finders"))] + [card("C1", gates_finders=v) for v in (None, "yes", "no", 0, 1, "false")]),
+        "an accepted card with no gates_finders is refused even unmerged, and never listed beside":
+            (lambda r: len(r[0]) == 2 and r[1] == [])(beside(edit(lambda c: c["cards"]["C1"].pop("gates_finders")), merged=lambda sha: sha != "abc")),
+        # --open-cards, P3's input (fix review 3620): it lists what is open and
+        # never prints an empty list over cards that carry no gates_finders.
+        "--open-cards lists a non-gating unmerged card, rc 0":
+            report(card("C1", gates_finders=False), merged=lambda sha: sha != "abc") == ({"round": 8, "open_cards": ["C1"], "unmarked_cards": []}, 0, []),
+        "--open-cards lists nothing on a complete record whose gating card is merged (null control)":
+            report() == ({"round": 8, "open_cards": [], "unmarked_cards": []}, 0, []),
+        "--open-cards refuses an accepted card with no boolean gates_finders by name, rc 1":
+            all(report(ev, merged=m)[1:] == (1, ["UNMARKED C1: accepted, no boolean gates_finders (the owner's ruling on finder gating)"])
+                and report(ev, merged=m)[0]["unmarked_cards"] == ["C1"]
+                for ev in (edit(lambda c: c["cards"]["C1"].pop("gates_finders")), card("C1", gates_finders="no"))
+                for m in (lambda sha: sha != "abc", lambda sha: True)),
+        "a rejected or deferred card needs no gates_finders": "gates_finders" not in good["cards"]["C2"] and run(card("C2", decision="deferred")) == [],
+        "a null, absent or blank reviewer or evaluator is refused":
+            all(only(run(ev), "two seats") for ev in [edit(lambda c: c.update(**{k: v})) for k in ("reviewer", "evaluator") for v in (None, "", "  ", 0, [])]
+                + [edit(lambda c: c.pop(k)) for k in ("reviewer", "evaluator")]),
         "B1 a disguised orchestrator or the same seat respelled is refused":
             all(only(run(edit(lambda c: c.update(**{k: v}))), "two seats") for k, v in (
                 ("evaluator", "orchestrator-r10"), ("evaluator", "the orchestrator"), ("reviewer", "Orchestrator"), ("reviewer", "Evaluator R8"))),
@@ -708,6 +810,8 @@ def main():
     ap.add_argument("--seat", help="print the cells this seat (D<k>-s<n>) owns and exit")
     ap.add_argument("--round", type=int, help="also refuse this round's start without its start evaluation")
     ap.add_argument("--population", action="store_true", help="print the install population's levels read at --ref and exit")
+    ap.add_argument("--open-cards", action="store_true",
+                    help="with --round: print, as JSON, the accepted non-gating cards not merged at --ref (P3's input) and exit; rc 1 naming any accepted card with no boolean gates_finders")
     a = ap.parse_args()
     show = lambda f, at=None: subprocess.check_output(["git", "-C", a.repo, "show", f"{at or a.ref}:{f}"], text=True)
     anc = lambda x, y: subprocess.run(["git", "-C", a.repo, "merge-base", "--is-ancestor", str(x), y],
@@ -716,6 +820,15 @@ def main():
     changed = lambda c: set(subprocess.run(["git", "-C", a.repo, "diff", "--name-only", f"{c}^1", str(c)],
                                            capture_output=True, text=True).stdout.split())
     tree = set(subprocess.check_output(["git", "-C", a.repo, "ls-tree", "-r", "--name-only", a.ref], text=True).split())
+    if a.open_cards:
+        if a.round is None or records(a.round)[1] not in tree:
+            print(f"--open-cards needs --round <N> and {records(a.round or 0)[1]} tracked at {a.ref}", file=sys.stderr)
+            sys.exit(2)
+        listing, rc, lines = open_cards_report(a.round, tree, show, merged, anc, changed)
+        for line in lines:
+            print(line, file=sys.stderr)
+        print(json.dumps({**listing, "ref": subprocess.check_output(["git", "-C", a.repo, "rev-parse", a.ref], text=True).strip()}))
+        sys.exit(rc)
     if a.population:
         lines, ok = population(json.loads(show(OBJECTIVE)).get("population", []), tree, show)
         print("\n".join(lines))
@@ -905,7 +1018,22 @@ def main():
         run_r1 = default_run(scopes, "--round", "1")
         cov["--round exits 1 with no evaluation in the tree"] = (run_r1.returncode == 1 and cited in run_r1.stdout
             and "FAIL start evaluation" in run_r1.stdout and "round1/EVALUATION.json is not in the tree" in run_r1.stdout)
-        print(f"   evaluation arms: {sum(ev.values())}/{len(ev)} held; --round 1 rc={run_r1.returncode}")
+        run_oc = default_run(scopes, "--round", "1", "--open-cards")
+        cov["--open-cards refuses a round with no evaluation, never an empty list"] = (run_oc.returncode == 2
+            and "round1/EVALUATION.json tracked" in run_oc.stderr and "open_cards" not in run_oc.stdout)
+        # --open-cards run whole on a record with and without a boolean
+        # gates_finders on C2 and C3 (fix review 3620): main()'s exit code and
+        # its UNMARKED stderr lines, which the function arms above cannot reach.
+        oc_marked, oc_unmarked = open_cards_cli()
+        unmarked_lines = [l.split(":")[0] for l in oc_unmarked.stderr.splitlines() if l.startswith("UNMARKED")]
+        cov["--open-cards exits 0 with no UNMARKED line when every accepted card carries a boolean (null control)"] = (
+            oc_marked.returncode == 0 and "UNMARKED" not in oc_marked.stderr
+            and (json_or_none(oc_marked.stdout) or {}).get("open_cards") == ["C1"])
+        cov["--open-cards exits 1 naming on stderr each accepted card with no boolean gates_finders"] = (
+            oc_unmarked.returncode == 1 and unmarked_lines == ["UNMARKED C2", "UNMARKED C3"]
+            and (json_or_none(oc_unmarked.stdout) or {}).get("unmarked_cards") == ["C2", "C3"])
+        print(f"   evaluation arms: {sum(ev.values())}/{len(ev)} held; --round 1 rc={run_r1.returncode}; --open-cards rc={run_oc.returncode}, "
+              f"marked rc={oc_marked.returncode}, unmarked rc={oc_unmarked.returncode} {unmarked_lines}")
         pop = population_self_test()
         cov.update({"population: " + k: v for k, v in pop.items()})
         print(f"   population arms: {sum(pop.values())}/{len(pop)} held")
@@ -915,10 +1043,13 @@ def main():
         sys.exit(0 if good else 1)
     ok = verdict(scopes, tree, loc, *read_harnesses(a.repo, a.ref, tree), units=units)
     if a.round is not None:
-        gaps = evaluation_gaps(a.round, tree, show, merged, anc, changed)
-        print(f"{'ok' if not gaps else 'FAIL'} start evaluation round={a.round}: {len(gaps)} gap(s)")
+        beside = []
+        gaps = evaluation_gaps(a.round, tree, show, merged, anc, changed, beside)
+        print(f"{'ok' if not gaps else 'FAIL'} start evaluation round={a.round}: {len(gaps)} gap(s), {len(beside)} card(s) beside the finders")
         for g in gaps:
             print(f"   {g}")
+        for cid in sorted(beside):
+            print(f"   PARALLEL {cid} accepted, not merged, gates no finder: builds beside them; open at P3, it is the architect's input (--open-cards)")
         ok = ok and not gaps
     sys.exit(0 if ok else 1)
 
diff --git a/tools/audit/enumerate.py b/tools/audit/enumerate.py
new file mode 100644
index 0000000000..dba42026bf
--- /dev/null
+++ b/tools/audit/enumerate.py
@@ -0,0 +1,956 @@
+#!/usr/bin/env python3
+"""Print one audit universe, one item per line, so a finder can report `universe=N examined=n`.
+
+Usage: python3 -I tools/audit/enumerate.py <universe> [--repo DIR] [options]
+  d0-grid [--plane price-weather]   tests/profiles.py price x weather, x zones x dhw x plant x horizon
+  d0-modules             package-internal import closure of optimizer.py + dhw_planner.py, plus coordinator.py
+  d1-lifecycle           async_track_* / async_call_later / listener / task registrations and the entry points
+  d1-stores              store.py DOMAINS keys, and one `upgrade` line per earlier *_STORE_VERSION /
+                         CONFIG_ENTRY_VERSION step
+  d1-inputs              every configured entity slot: a config_flow.py `_F` key behind an entity selector,
+                         and each key entry_config.py's FACTORY_KEPT keeps as an entity assignment
+  d1-solve-state         every `self.<attr>` the solve-thread entries (SOLVE_FNS) touch
+  d1-excepts             every except handler, broad or narrow
+  d1-parsers             defs named *parse*, and json.loads / .json() / async_subscribe sites
+  d2-identities [--cells]   dev/audit/config/identities.json, one line per identity; --cells crosses each
+                         with its grid (population axes, tests/golden.py SCENARIOS, or levels the register states)
+  d3-sites [--state S] [--by-file] [--ast]   the mutation universe, `<file>:<line> <kind> <state>`, joined
+                         to the ledger through tests/mutation_table.py's own `inventory` and
+                         `disposition_matches`; --ast is the ledger-free fallback (if/ifexp/minmax/except)
+  d8-cells               strings.json entity name / state / attribute, once per translation file
+  d9-collections         coordinator.py `self.<attr>` bound to a container, once per class and attribute
+  d9-attributes          classes defining or assigning extra_state_attributes
+  d9-solves              calls of the solver entry, then of each function holding one, to a fixed point
+  d12-cells [--pairs]    every level `check_scopes.py --population` reads, the card and the blueprints
+                         (--pairs: every pair of levels from two axes), each `not run` until a ledger row
+  --ledger TSV           with any universe: each line beside its ledger row's asserting test, or `not run`
+                         (rows: item, test; for d12-cells: cell, source, test); a row naming no item,
+                         an unlisted source or no test is refused
+  d14-classes [--status open]   dev/audit/config/bugclasses.json entries that carry a status
+  d15-installs           dev/audit/config/bundles.json, one line per bundle an install sent
+  d16-writes [--cells]   actuator `services.async_call` and `log_held` sites; --cells crosses each
+                         with the PUMP_DUTY_MODES parsed from const.py and the four lifecycle conditions
+  d17-features           services.yaml keys, strings.json steps/fields/entities, blueprints
+  --briefs               the acceptance of a brief that names a universe: every `enumerate.py <universe>`
+                         a dev/governance/dimensions/D*.md cites, with its --cells or --pairs, runs
+                         non-empty; an unknown universe or a tree citing none is refused
+Stdout is the universe only (deterministic, sorted; `wc -l` is its size); a second identical item on
+one line gets a ` #2` suffix so no two lines are equal. Diagnostics go to stderr.
+Exit 0 on success. Exit 2 with a message on stderr when a source is missing or yields zero items: an
+empty universe is a refusal, never a pass.
+Null control: --self-test runs every universe on the live tree (>=1 line, sorted, no duplicates), and
+per universe plants a fake repo (--repo) whose count it states, deletes one item and reads the count
+move, then empties or removes the source and reads the refusal. It prints `SELF-TEST passed (N arms)`
+or names the failing arm and exits 1.
+"""
+import argparse, ast, collections, contextlib, io, json, os, re, shutil, subprocess, sys, tempfile
+from pathlib import Path
+
+PKG = "custom_components/heatpump_optimizer"
+OBJECTIVE, IDENTITIES, BUNDLES = "dev/audit/config/objective.json", "dev/audit/config/identities.json", "dev/audit/config/bundles.json"
+# the conditions the actuator-write dimension drives
+CONDITIONS = ("running", "restart", "upgrade", "unavailable")
+# D0.md step 4's axes; the last two plants are the cells round 10's escapes showed no seat drove
+TOPOLOGY, DHW, HORIZON_H = ("single-zone", "two-zone"), ("dhw", "no-dhw"), (6, 24, 48)
+PLANT = ("plain", "valve-storage", "wood", "manual-valve-buffer", "flow-setpoint-behind-valve")
+USER_PLATFORMS = ("switch", "button", "climate", "datetime", "number", "select")
+LIFE_CALLS = {"async_call_later", "async_on_unload", "async_create_task", "async_create_background_task",
+              "async_add_executor_job", "async_listen", "async_listen_once", "add_update_listener"}
+ENTRY_FNS = ("async_setup", "async_setup_entry", "async_unload_entry", "async_remove_entry",
+             "async_migrate_entry", "async_update_options")
+# D1.md step 4's solve-thread entries, D9.md's solver entry, and what counts as a retained collection
+SOLVE_FNS, SOLVER_ENTRY = ("_solve_record", "_solve_hubs"), "_multi_start_minimize"
+CONTAINERS = {"dict", "list", "set", "deque", "defaultdict", "OrderedDict", "Counter"}
+# decision 0018 section 1: the four sources that examine a generality cell
+SOURCES = ("simulation", "bundle", "install-report", "property-test")
+
+
+class Refuse(Exception):
+    pass
+
+
+def pkg_files(repo):
+    return sorted((repo / PKG).glob("*.py"))
+
+
+def rel(repo, p):
+    return p.relative_to(repo).as_posix()
+
+
+def parse(p):
+    return ast.parse(p.read_text())  # a missing source is an OSError, which run() refuses
+
+
+def scoped(tree):
+    """Like walk, but a def/class node's children see the def's dotted name."""
+    def go(node, q):
+        for c in ast.iter_child_nodes(node):
+            yield c, q
+            if isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+                yield from go(c, c.name if q == "<module>" else f"{q}.{c.name}")
+            else:
+                yield from go(c, q)
+    yield from go(tree, "<module>")
+
+
+def fname(call):
+    f = call.func
+    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
+
+
+def const_assign(tree, name):
+    """The value node of a module-level `name = ...` / `name: T = ...`, or None."""
+    for n in tree.body:
+        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
+            return n.value
+        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == name and n.value:
+            return n.value
+
+
+def d16(repo, cells=False, **_):
+    out = []
+    for p in pkg_files(repo):
+        for n, q in scoped(parse(p)):
+            if isinstance(n, ast.Call):
+                f = n.func
+                if isinstance(f, ast.Attribute) and f.attr == "async_call" and isinstance(f.value, ast.Attribute) and f.value.attr == "services":
+                    out.append(f"write {rel(repo, p)}:{n.lineno} {q}")
+                if fname(n) == "log_held":
+                    out.append(f"hold {rel(repo, p)}:{n.lineno} {q}")
+    if cells:
+        v = const_assign(parse(repo / PKG / "const.py"), "PUMP_DUTY_MODES")
+        modes = [e.value for e in getattr(v, "elts", []) if isinstance(e, ast.Constant)]
+        out = [f"{s} | duty={m} | {c}" for s in out for m in modes for c in CONDITIONS]
+    return out
+
+
+def d17(repo, **_):
+    out, base = [], repo / PKG
+    out += [f"service {m}" for m in re.findall(r"^([a-z_]+):", (base / "services.yaml").read_text(), re.M)]
+    s = json.loads((base / "strings.json").read_text())
+    for sec, kstep, kfield in (("config", "config-step", "config-field"), ("options", "options-step", "option")):
+        for step, body in s.get(sec, {}).get("step", {}).items():
+            out.append(f"{kstep} {step}")
+            out += [f"{kfield} {step}.{k}" for k in (body.get("data") or {})]
+    ent = s.get("entity", {})
+    out += [f"entity {pl}.{k}" for pl in USER_PLATFORMS for k in ent.get(pl, {})]
+    return out + [f"blueprint {b}" for b in sorted(tracked(repo)) if b.startswith("blueprints/")]
+
+
+def d14(repo, status=None, **_):
+    p = repo / "dev/audit/config/bugclasses.json"
+    return [f"{v['status']} {v.get('kind', '?')} {k}" for k, v in json.loads(p.read_text()).items()
+            if isinstance(v, dict) and "status" in v and status in (None, v["status"])]
+
+
+def d0grid(repo, plane=None, **_):
+    tree = parse(repo / "tests/profiles.py")
+    lits = {}
+    for fn in ("prices", "weather"):
+        lits[fn] = sorted({c.value for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == fn
+                           for n in ast.walk(f) if isinstance(n, ast.Compare) and isinstance(n.left, ast.Name)
+                           and n.left.id == "profile" for c in n.comparators if isinstance(c, ast.Constant)})
+    pw = [f"{a}/{b}" for a in lits["prices"] for b in lits["weather"]]
+    if plane == "price-weather":
+        return pw
+    return [f"{x}/{t}/{d}/{pl}/{h}h" for x in pw for t in TOPOLOGY for d in DHW for pl in PLANT for h in HORIZON_H]
+
+
+def imports(path, base):
+    out = set()
+    for n in ast.walk(parse(path)):
+        names = []
+        if isinstance(n, ast.ImportFrom):
+            if n.level == 1 and n.module:
+                names = [n.module.split(".")[0]]
+            elif n.level == 1:
+                names = [a.name for a in n.names]
+            elif n.level == 0 and n.module and n.module.startswith(PKG.replace("/", ".")):
+                tail = n.module[len(PKG):].lstrip(".")
+                names = [tail.split(".")[0]] if tail else [a.name for a in n.names]
+        elif isinstance(n, ast.Import):
+            names = [a.name[len(PKG) + 1:].split(".")[0] for a in n.names if a.name.startswith(PKG.replace("/", ".") + ".")]
+        out |= {x for x in names if (base / f"{x}.py").is_file()}
+    return out
+
+
+def d0modules(repo, **_):
+    base = repo / PKG
+    seen, todo = set(), ["optimizer", "dhw_planner"]
+    while todo:
+        m = todo.pop()
+        if m not in seen:
+            seen.add(m)
+            todo += sorted(imports(base / f"{m}.py", base))
+    if not (base / "coordinator.py").is_file():
+        raise Refuse(f"missing source {base / 'coordinator.py'}")
+    return [f"{PKG}/{m}.py" for m in seen | {"coordinator"}]
+
+
+def d1stores(repo, **_):
+    out = []
+    st = parse(repo / PKG / "store.py")
+    d = const_assign(st, "DOMAINS")
+    if not isinstance(d, ast.Dict):
+        raise Refuse("no DOMAINS dict literal in store.py")
+    for k in d.keys:
+        if isinstance(k, ast.Constant):
+            out.append(f"store {k.value}")
+        elif isinstance(k, ast.Name):
+            v = const_assign(st, k.id)
+            out.append(f"store {v.value if isinstance(v, ast.Constant) else k.id}")
+    for p in pkg_files(repo):
+        r = rel(repo, p)
+        for n in parse(p).body:
+            tg = n.targets[0] if isinstance(n, ast.Assign) and len(n.targets) == 1 else getattr(n, "target", None)
+            if isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(tg, ast.Name) and isinstance(n.value, ast.Constant) \
+                    and type(n.value.value) is int and (tg.id.endswith("STORE_VERSION") or (tg.id == "CONFIG_ENTRY_VERSION" and p.name == "const.py")):
+                v = n.value.value
+                out += [f"upgrade {r}:{tg.id} v{k}->{v}" for k in range(1, v)] or [f"upgrade {r}:{tg.id} v{v} (no earlier version)"]
+    return out
+
+
+def d1excepts(repo, **_):
+    out = []
+    for p in pkg_files(repo):
+        for n, q in scoped(parse(p)):
+            if isinstance(n, ast.ExceptHandler):
+                ts = n.type.elts if isinstance(n.type, ast.Tuple) else [n.type]
+                broad = n.type is None or any(isinstance(t, ast.Name) and t.id in ("Exception", "BaseException") for t in ts)
+                out.append(f"{rel(repo, p)}:{n.lineno} {'broad' if broad else 'narrow'} {q}")
+    return out
+
+
+def d1life(repo, **_):
+    out = []
+    for p in pkg_files(repo):
+        t = parse(p)
+        for n, q in scoped(t):
+            if isinstance(n, ast.Call):
+                k = fname(n)
+                if k.startswith("async_track_") or k in LIFE_CALLS:
+                    out.append(f"{k} {rel(repo, p)}:{n.lineno} {q}")
+        if p.name == "__init__.py":
+            out += [f"entry {n.name}" for n in t.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in ENTRY_FNS]
+    return out
+
+
+def d3(repo, state=None, by_file=False, ast_only=False, **_):
+    rows = []  # (file, "file:line kind", state)
+    if ast_only:
+        for p in pkg_files(repo):
+            for n, _q in scoped(parse(p)):
+                k = ("if" if isinstance(n, ast.If) else "ifexp" if isinstance(n, ast.IfExp) else "except" if isinstance(n, ast.ExceptHandler)
+                     else "minmax" if isinstance(n, ast.Call) and fname(n) in ("min", "max", "clip") else None)
+                if k:
+                    rows.append((rel(repo, p), f"{rel(repo, p)}:{n.lineno} {k}", None))
+    else:
+        mt = repo / "tests/mutation_table.py"
+        if not mt.is_file():
+            raise Refuse(f"missing source {mt} (use --ast for the ledger-free fallback)")
+        sys.path.append(str(repo / "tests"))
+        with contextlib.redirect_stdout(sys.stderr):
+            import mutation_table as m
+            b, inv = m.load_budgets(), m.inventory()
+        kb, tr = b.get("killed_by", {}), b.get("survivor_triage", {})
+        for s in inv:
+            a = s["anchor"]
+            st = "killed" if m.disposition_matches(kb.get(a), s) else "triaged" if m.disposition_matches(tr.get(a), s) else "unrecorded"
+            if state in (None, st):
+                rows.append((s["file"], f"{s['file']}:{s['line']} {s['kind']}", st))
+    if by_file:
+        c = collections.Counter(f for f, _l, _s in rows)
+        if ast_only:
+            return [f"{f} {c[f]}" for f in c]
+        return [f"{f} {c[f]} " + " ".join(str(sum(1 for r in rows if r[0] == f and r[2] == s)) for s in ("killed", "triaged", "unrecorded")) for f in c]
+    return [f"{l} {s}" if s else l for _f, l, s in rows]
+
+
+
+def flow_slots(repo):
+    """The keys config_flow.py's `_F` rows offer through an entity selector: a row whose widget is a
+    call of EntitySelector or of a def returning one, its key a name or a comprehension's loop name
+    over a tuple of names. An entity selector in no such row is refused: the census would be short."""
+    t = parse(repo / PKG / "config_flow.py")
+    defs = [d for d in ast.walk(t) if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef))]
+    fac = {d.name for d in defs if any(isinstance(r, ast.Return) and isinstance(r.value, ast.Call)
+                                       and fname(r.value) == "EntitySelector" for r in ast.walk(d))}
+    inside = {id(n) for d in defs if d.name in fac for n in ast.walk(d)}
+    loops = {}  # id(an _F call) -> {loop name: [the tuple's names]}
+    for c in ast.walk(t):
+        if isinstance(c, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
+            b = {g.target.id: [e.id for e in g.iter.elts] for g in c.generators if isinstance(g.target, ast.Name)
+                 and isinstance(g.iter, (ast.Tuple, ast.List)) and all(isinstance(e, ast.Name) for e in g.iter.elts)}
+            loops.update({id(n): b for n in ast.walk(c.elt)})
+    keys, rows = [], set()
+    for n in ast.walk(t):
+        if isinstance(n, ast.Call) and fname(n) == "_F":
+            a = {**dict(zip(("step", "key", "default", "widget"), n.args)), **{k.arg: k.value for k in n.keywords}}
+            w, k = a.get("widget"), a.get("key")
+            if isinstance(w, ast.Call) and (fname(w) in fac or fname(w) == "EntitySelector"):
+                rows.add(id(w))
+                if not isinstance(k, ast.Name):
+                    raise Refuse(f"config_flow.py:{n.lineno}: an entity selector row whose key is no name")
+                keys += loops.get(id(n), {}).get(k.id) or [k.id]
+    for n in ast.walk(t):
+        if isinstance(n, ast.Call) and id(n) not in inside and id(n) not in rows and (fname(n) in fac or fname(n) == "EntitySelector"):
+            raise Refuse(f"config_flow.py:{n.lineno}: an entity selector outside an `_F` row is in no census")
+    return keys
+
+
+def wiring_slots(repo):
+    """The keys entry_config.py's FACTORY_KEPT keeps for the reason its one comprehension gives (an
+    entity assignment): the const.py names that comprehension's startswith/endswith tests select,
+    and the dict entries FACTORY_KEPT spreads that give the same reason. Another test is refused."""
+    t = parse(repo / PKG / "entry_config.py")
+    fk = const_assign(t, "FACTORY_KEPT")
+    comps = [c for c in ast.walk(fk) if isinstance(c, ast.DictComp)] if fk else []
+    if len(comps) != 1 or not isinstance(comps[0].value, ast.Constant) or not isinstance(comps[0].generators[0].target, ast.Tuple):
+        raise Refuse("entry_config.py: no FACTORY_KEPT holding one comprehension over (name, key): re-read the entity rule")
+    c = comps[0]
+    reason, (nv, kv) = c.value.value, [e.id for e in c.generators[0].target.elts]
+    tests = []
+    for e in [x for i in c.generators[0].ifs for x in (i.values if isinstance(i, ast.BoolOp) else [i])]:
+        if isinstance(e, ast.Call) and fname(e) == "isinstance" and getattr(e.args[0], "id", None) == kv:
+            continue
+        if not (isinstance(e, ast.Call) and fname(e) in ("startswith", "endswith") and isinstance(e.func.value, ast.Name)
+                and e.func.value.id in (nv, kv) and len(e.args) == 1 and isinstance(e.args[0], ast.Constant)):
+            raise Refuse(f"entry_config.py:{e.lineno}: FACTORY_KEPT's entity rule holds a test this census cannot read")
+        tests.append((e.func.value.id == nv, fname(e), e.args[0].value))
+    keys = []
+    for n in parse(repo / PKG / "const.py").body:
+        tg = n.targets[0] if isinstance(n, ast.Assign) and len(n.targets) == 1 else getattr(n, "target", None)
+        v = getattr(n, "value", None)
+        if isinstance(tg, ast.Name) and isinstance(v, ast.Constant) and isinstance(v.value, str) \
+                and all(getattr(tg.id if on_name else v.value, how)(arg) for on_name, how, arg in tests):
+            keys.append(tg.id)
+    for d in [x for x in ast.walk(fk) if isinstance(x, ast.Dict)]:
+        for k, v in zip(d.keys, d.values):
+            src = const_assign(t, v.id) if k is None and isinstance(v, ast.Name) else None
+            pairs = zip(src.keys, src.values) if isinstance(src, ast.Dict) else [(k, v)] if k is not None else []
+            keys += [kk.attr if isinstance(kk, ast.Attribute) else kk.id for kk, vv in pairs
+                     if isinstance(kk, (ast.Attribute, ast.Name)) and isinstance(vv, ast.Constant) and vv.value == reason]
+    return keys
+
+
+def d1inputs(repo, **_):
+    """Step 3's inputs: every configured entity slot, by what the code treats as one: a key the
+    options flow offers through an entity selector, or one a factory reset keeps as an entity
+    assignment. A key in both prints once."""
+    return [f"input {k}" for k in sorted(set(flow_slots(repo)) | set(wiring_slots(repo)))]
+
+
+def d1solve(repo, **_):
+    """Step 4's reads: every `self.<attr>` the solve-thread entry functions touch."""
+    out, found = set(), set()
+    for n, _q in scoped(parse(repo / PKG / "coordinator.py")):
+        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in SOLVE_FNS:
+            found.add(n.name)
+            out |= {f"{n.name} self.{a.attr}" for a in ast.walk(n)
+                    if isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) and a.value.id == "self"}
+    if set(SOLVE_FNS) - found:
+        raise Refuse(f"coordinator.py lacks {sorted(set(SOLVE_FNS) - found)}: the solve-thread entry moved, re-point SOLVE_FNS")
+    return sorted(out)
+
+
+def d1parsers(repo, **_):
+    """Step 6's parsers: a def whose name holds `parse`, and each json.loads / .json() / async_subscribe site."""
+    out = []
+    for p in pkg_files(repo):
+        for n, q in scoped(parse(p)):
+            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and "parse" in n.name:
+                out.append(f"def {rel(repo, p)}:{n.lineno} {n.name}")
+            if isinstance(n, ast.Call):
+                f, k = n.func, fname(n)
+                if k == "loads" and isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "json":
+                    out.append(f"json {rel(repo, p)}:{n.lineno} {q}")
+                elif k == "json" and isinstance(f, ast.Attribute) and not n.args:
+                    out.append(f"response {rel(repo, p)}:{n.lineno} {q}")
+                elif k == "async_subscribe":
+                    out.append(f"subscribe {rel(repo, p)}:{n.lineno} {q}")
+    return out
+
+
+def tracked(repo):
+    r = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True, text=True)
+    fs = r.stdout.split("\n") if r.returncode == 0 and (repo / ".git").exists() else []
+    return {f for f in fs if f} or {rel(repo, Path(d) / f) for d, _, names in os.walk(repo) for f in names}
+
+
+def population_axes(repo):
+    """{axis: [levels]} as `check_scopes.py --population` reads them, by its own reader, and the
+    two totals it prints; a binary axis key is its own axis with levels present and absent."""
+    obj = repo / OBJECTIVE
+    sys.path.append(str(Path(__file__).resolve().parent))
+    import check_scopes
+    lines, ok = check_scopes.population(json.loads(obj.read_text()).get("population", []), tracked(repo), lambda f: (repo / f).read_text())
+    if not ok:
+        raise Refuse("the population is unreadable: " + "; ".join(l for l in lines if l.startswith("UNREADABLE")))
+    axes, totals = {}, {}
+    for l in lines:
+        if "\t" not in l:
+            k, _, v = l.partition(": ")
+            totals[k] = int(v)
+            continue
+        name, _, rest = l.partition("\t")
+        n, _, lv = rest.partition("\t")
+        if n == "NO-READ":
+            print(f"NO-READ axis {name}: no cell until {OBJECTIVE} declares its levels", file=sys.stderr)
+        elif n.endswith("binary axes"):
+            axes.update({k: ["absent", "present"] for k in lv.split(",")})
+        else:
+            axes[name] = lv.split(",")
+    return axes, totals
+
+
+def golden_scenarios(repo):
+    v = const_assign(parse(repo / "tests/golden.py"), "SCENARIOS")
+    return [k.value for k in getattr(v, "keys", []) if isinstance(k, ast.Constant)]
+
+
+def d2(repo, cells=False, **_):
+    """The identity register, one line per identity, or under --cells one per identity and
+    grid cell. A grid axis is a population axis by name, `golden` (tests/golden.py SCENARIOS),
+    or an inline {"axis", "levels"} the register states because no source holds it."""
+    p = repo / IDENTITIES
+    rows, out, pop = json.loads(p.read_text()).get("identities", []), [], None
+    for r in rows:
+        if not (re.fullmatch(r"M\d+", str(r.get("step"))) and r.get("id") and r.get("identity") and r.get("grid")):
+            raise Refuse(f"{IDENTITIES}: an identity needs step, id, identity and a non-empty grid: {r}")
+        grid = []
+        for g in r["grid"]:
+            if isinstance(g, dict):
+                name, lv = g.get("axis"), g.get("levels")
+            elif g == "golden":
+                name, lv = g, golden_scenarios(repo)
+            else:
+                pop = pop or population_axes(repo)[0]
+                name, lv = g, pop.get(g)
+            if not lv:
+                raise Refuse(f"{IDENTITIES}: identity {r['id']} names grid axis {name!r}, which has no level")
+            grid.append((name, lv))
+        if not cells:
+            out.append(f"{r['step']} {r['id']} grid=" + "x".join(n for n, _ in grid))
+            continue
+        combos = [[]]
+        for name, lv in grid:
+            combos = [c + [f"{name}={x}"] for c in combos for x in lv]
+        out += [f"{r['step']} {r['id']} | " + " ".join(c) for c in combos]
+    return out
+
+
+def d8(repo, **_):
+    """Entity by state by language: every name, state, attribute and attribute state strings.json
+    declares under `entity`, once per translation file (a file lacking the key is still a cell)."""
+    sj, tr = repo / PKG / "strings.json", repo / PKG / "translations"
+    langs = sorted(f.stem for f in tr.glob("*.json"))  # no translation file is no cell, which run() refuses
+    facets = []
+    for pl, ents in json.loads(sj.read_text()).get("entity", {}).items():
+        for k, body in ents.items():
+            facets.append(f"{pl}.{k} name")
+            facets += [f"{pl}.{k} state={s}" for s in body.get("state", {})]
+            for a, ab in body.get("state_attributes", {}).items():
+                facets.append(f"{pl}.{k} attr={a}")
+                facets += [f"{pl}.{k} attr={a}:state={s}" for s in (ab.get("state", {}) if isinstance(ab, dict) else {})]
+    return [f"{lang} {f}" for f in facets for lang in langs]
+
+
+def d9collections(repo, **_):
+    """Every `self.<attr>` of a coordinator.py class bound to a container literal, comprehension
+    or constructor, once per class and attribute, at its first binding."""
+    first = {}
+    for n, q in scoped(parse(repo / PKG / "coordinator.py")):
+        tg = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, ast.AnnAssign) and n.value else []
+        v = getattr(n, "value", None)
+        kind = ({ast.Dict: "dict", ast.List: "list", ast.Set: "set", ast.DictComp: "dict", ast.ListComp: "list", ast.SetComp: "set"}.get(type(v))
+                or (fname(v) if isinstance(v, ast.Call) and fname(v) in CONTAINERS else None))
+        for t in tg:
+            if kind and isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == "self" and "." in q:
+                first.setdefault(f"{q.split('.')[0]}.{t.attr}", f"{kind} {PKG}/coordinator.py:{n.lineno}")
+    return [f"{k} {v}" for k, v in first.items()]
+
+
+def d9attributes(repo, **_):
+    """Every class that publishes attributes: one defining or assigning `extra_state_attributes`."""
+    out = []
+    for p in pkg_files(repo):
+        for c in ast.walk(parse(p)):
+            if isinstance(c, ast.ClassDef) and any(
+                    (isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name == "extra_state_attributes")
+                    or (isinstance(m, (ast.Assign, ast.AnnAssign)) and any(isinstance(t, ast.Name) and t.id == "_attr_extra_state_attributes"
+                                                                          for t in (m.targets if isinstance(m, ast.Assign) else [m.target])))
+                    for m in c.body):
+                out.append(f"{rel(repo, p)}:{c.lineno} {c.name}")
+    return out
+
+
+def d9solves(repo, **_):
+    """The solve paths: each call of SOLVER_ENTRY, then each call of, or bare reference to (a
+    function handed to an executor is never called by name), a function that holds one, upward
+    by name inside the solver's own module; a site in another module is an entry into the
+    solver, printed and not climbed (a name shared with an unrelated function stops there)."""
+    sites, home = [], None
+    for p in pkg_files(repo):
+        t = parse(p)
+        if any(isinstance(n, ast.FunctionDef) and n.name == SOLVER_ENTRY for n in t.body):
+            home = rel(repo, p)
+        called = {id(n.func) for n in ast.walk(t) if isinstance(n, ast.Call)}
+        for n, q in scoped(t):
+            if isinstance(n, ast.Call) and fname(n):
+                sites.append((fname(n), "", rel(repo, p), n.lineno, q))
+            elif isinstance(n, (ast.Name, ast.Attribute)) and isinstance(n.ctx, ast.Load) and id(n) not in called:
+                sites.append((n.id if isinstance(n, ast.Name) else n.attr, " (ref)", rel(repo, p), n.lineno, q))
+    names, grown = {SOLVER_ENTRY}, set()
+    while names != grown:
+        grown = set(names)
+        names |= {q.split(".")[-1] for callee, _how, f, _line, q in sites if callee in grown and f == home and q != "<module>"}
+    return [f"{'solve' if callee == SOLVER_ENTRY else 'path'} {callee} <- {f}:{line} {q}{how}" for callee, how, f, line, q in sites if callee in names]
+
+
+def d12(repo, pairs=False, **_):
+    """The generality cells: every level `--population` reads, the card and each blueprint,
+    and under --pairs every pair of levels from two axes. The level and pair counts are asserted
+    against the command's own."""
+    axes, totals = population_axes(repo)
+    cells = [f"level {a}={x}" for a, lv in axes.items() for x in lv]
+    if len(cells) != totals.get("LEVELS"):
+        raise Refuse(f"{len(cells)} level cells against the population's LEVELS: {totals.get('LEVELS')}")
+    names = sorted(axes)
+    if pairs:
+        pc = [f"pair {a}={x} & {b}={y}" for i, a in enumerate(names) for b in names[i + 1:] for x in axes[a] for y in axes[b]]
+        if len(pc) != totals.get("PAIRS"):
+            raise Refuse(f"{len(pc)} pair cells against the population's PAIRS: {totals.get('PAIRS')}")
+        cells += pc
+    surf = [f"surface card {f}" for f in sorted(tracked(repo)) if f.startswith(f"{PKG}/www/") and f.endswith(".js")]
+    surf += [f"surface blueprint {f}" for f in sorted(tracked(repo)) if f.startswith("blueprints/")]
+    if not surf:
+        raise Refuse("no card and no blueprint is tracked")
+    return cells + surf
+
+
+def d15(repo, **_):
+    """The installs that sent a bundle, one line per bundle: its date, the round that read it and
+    the steps run on it. A round's examined count is its own lines; the universe is every line."""
+    p = repo / BUNDLES
+    out = []
+    for b in json.loads(p.read_text()).get("bundles", []):
+        if not (b.get("install") and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(b.get("date"))) and isinstance(b.get("round"), int)
+                and isinstance(b.get("steps"), list) and b.get("evidence")):
+            raise Refuse(f"{BUNDLES}: a bundle needs install, date (YYYY-MM-DD), round, steps and evidence: {b}")
+        if not (repo / b["evidence"]).exists():
+            raise Refuse(f"{BUNDLES}: evidence {b['evidence']} of {b['install']} {b['date']} is not in the tree")
+        out.append(f"{b['install']} {b['date']} round={b['round']} steps={','.join(b['steps']) or 'none'}")
+    return out
+
+
+UNIVERSES = {"d16-writes": d16, "d17-features": d17, "d14-classes": d14, "d0-grid": d0grid, "d0-modules": d0modules,
+             "d1-stores": d1stores, "d1-excepts": d1excepts, "d1-lifecycle": d1life, "d1-inputs": d1inputs,
+             "d1-solve-state": d1solve, "d1-parsers": d1parsers, "d2-identities": d2, "d3-sites": d3, "d8-cells": d8,
+             "d9-collections": d9collections, "d9-attributes": d9attributes, "d9-solves": d9solves,
+             "d12-cells": d12, "d15-installs": d15}
+
+
+def joined(name, items, ledger):
+    """Each item beside its ledger row, or `not run`: the census with the test that drives each
+    line. A row is item and asserting test, tab-separated; a generality cell also names, between
+    them, which of decision 0018's four sources examined it, and prints `not run` with no ledger."""
+    cell = name == "d12-cells"
+    if not ledger and not cell:
+        return items
+    rows = {}
+    for i, l in enumerate(Path(ledger).read_text().splitlines() if ledger else (), 1):
+        c = [x.strip() for x in l.split("\t")]
+        if not l.strip() or l.startswith("#"):
+            continue
+        if len(c) != 2 + cell or not c[-1] or (cell and c[1] not in SOURCES):
+            raise Refuse(f"{ledger}:{i}: a row is the item, " + (f"its source ({', '.join(SOURCES)}), " if cell else "")
+                         + "and its asserting test, tab-separated; a run that asserts nothing examines nothing")
+        if c[0] not in items:
+            raise Refuse(f"{ledger}:{i}: {c[0]!r} is no item of this universe as printed (check its options)")
+        rows[c[0]] = "\t".join(c[1:])
+    return [f"{x}\t{rows.get(x, 'not run')}" for x in items]
+
+
+def run(name, repo, ledger=None, **kw):
+    try:
+        lines = joined(name, sorted(_dedupe(UNIVERSES[name](Path(repo), **kw))), ledger)
+    except OSError as e:
+        raise Refuse(f"missing or unreadable source: {e}")
+    if not lines:
+        raise Refuse(f"{name} yields zero items: an empty universe is a refusal")
+    return lines
+
+
+def _dedupe(lines):
+    seen = collections.Counter()
+    for l in lines:
+        seen[l] += 1
+        yield l if seen[l] == 1 else f"{l} #{seen[l]}"
+
+
+def briefs(repo):
+    """One `ok` line per (brief, cited command); Refuse on a citation that names no universe,
+    one whose universe refuses, or a tree whose briefs cite none."""
+    out, bad = [], []
+    for f in sorted((repo / "dev/governance/dimensions").glob("D*.md")):
+        text = re.sub(r"\s+", " ", f.read_text())
+        for u, flags in sorted(set(re.findall(r"enumerate\.py (d\d+-[a-z-]+)((?: --(?:cells|pairs))*)", text))):
+            opt = {k: True for k in re.findall(r"--(cells|pairs)", flags)}
+            try:
+                if u not in UNIVERSES:
+                    raise Refuse("no such universe")
+                with contextlib.redirect_stderr(io.StringIO()):
+                    run(u, repo, **opt)
+                out.append(f"ok {f.stem} {u}{flags}")
+            except Refuse as e:
+                bad.append(f"{f.stem} cites `enumerate.py {u}{flags}`: {e}")
+    if bad or not out:
+        raise Refuse("; ".join(bad) or "no dimension brief cites a universe")
+    return out
+
+
+def plant(root):
+    P = root / PKG
+    for d in ("tests", "dev/audit/config", "blueprints/automation", f"{PKG}/translations", f"{PKG}/www"):
+        (root / d).mkdir(parents=True)
+    w = lambda p, t: (root / p).write_text(t)
+    w(f"{PKG}/x.py", "def f(hass):\n" + "    hass.services.async_call('a', 'b')\n" * 2 + "    log_held('x')\n"
+      "    try:\n        pass\n    except Exception:\n        pass\n    except ValueError:\n        pass\n"
+      "    async_track_time_interval(1)\n    hass.async_create_task(1)\n    hass.helpers.async_call('c')\n"
+      "    y = min(1, 2) if hass else 0\n    if y:\n        pass\n")
+    w(f"{PKG}/p.py", "import json\ndef parse_a(x):\n    return json.loads(x)\nasync def g(r, m):\n    await r.json()\n    r.json('k')\n"
+      "    await m.async_subscribe('t')\n")
+    w(f"{PKG}/e.py", "class E:\n    @property\n    def extra_state_attributes(self):\n        return {}\nclass F:\n    _attr_extra_state_attributes = {}\nclass G:\n    pass\ndef use(c):\n    return c.cycle()\n")
+    w(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'control')\nCONFIG_ENTRY_VERSION: Final = 3\n"
+      "CONF_A_ENTITY = 'a_entity'\nCONF_B_ENTITY: Final = 'b_entity'\nCONF_F_SENSOR = 'f_sensor'\nCONF_H1 = 'h1'\nCONF_H2 = 'h2'\n"
+      "CONF_W_SENSOR = 'w_sensor'\nCONF_NAME = 'n'\nX_ENTITY = 'x_entity'\nMODES = ('m1', 'm2')\n")
+    w(f"{PKG}/config_flow.py", "def _entity_of(d):\n    return selector.EntitySelector(d)\ndef _text():\n    return selector.TextSelector()\n"
+      "ROWS = (\n    _F('s', CONF_A_ENTITY, '', _entity_of('sensor')),\n    _F('s', CONF_F_SENSOR, '', widget=_entity_of('sensor')),\n"
+      "    *(_F('s', key, '', _entity_of('number')) for key in (CONF_H1, CONF_H2)),\n    _F('s', CONF_NAME, '', _text()),\n)\n")
+    w(f"{PKG}/entry_config.py", "_WIRING: dict = {const.CONF_W_SENSOR: 'an entity assignment', const.CONF_NAME: 'the name'}\n"
+      "FACTORY_KEPT = MappingProxyType({**{key: 'an entity assignment' for name, key in vars(const).items()\n"
+      "    if name.startswith('CONF_') and isinstance(key, str) and key.endswith('_entity')}, **_WIRING})\n")
+    w(f"{PKG}/store.py", "K = 'b'\nDOMAINS = {'a': {}, K: {}}\nLEDGER_STORE_VERSION = 2\nMAP_STORE_VERSION: Final = 1\n")
+    w(f"{PKG}/__init__.py", "".join(f"async def {f}(h, e):\n    pass\n" for f in ENTRY) + "def helper():\n    pass\n")
+    w(f"{PKG}/optimizer.py", "from .y import z\nfrom . import w\ndef _multi_start_minimize():\n    pass\ndef go(c):\n    return _multi_start_minimize() or go(c)\n")
+    w(f"{PKG}/y.py", "from custom_components.heatpump_optimizer.v import q\nimport custom_components.heatpump_optimizer.u\n"
+      "from custom_components.heatpump_optimizer import t\n")
+    w(f"{PKG}/coordinator.py", "class C:\n    def __init__(self):\n        self.a = {}\n        self.b = deque(maxlen=3)\n        self.c = 0\n        self.a = {}\n"
+      "    def _solve_record(self):\n        return self.a, self.c\n    def _solve_hubs(self):\n        return self.b\n    def cycle(self):\n        return go(self)\n    def held(self):\n        return submit(go)\n"
+      "def helper(self):\n    self.z = {}\n")
+    for n in ("w", "v", "u", "t", "dhw_planner"):
+        w(f"{PKG}/{n}.py", "")
+    w(f"{PKG}/services.yaml", "set_a:\n  fields: {}\nset_b:\n")
+    w(f"{PKG}/strings.json", json.dumps({"config": {"step": {"user": {"data": {"f1": "", "f2": ""}}}},
+                                         "options": {"step": {"init": {"data": {"o1": ""}}}},
+                                         "entity": {"switch": {"s1": {}}, "sensor": {"z": {"state": {"on": "", "off": ""}, "state_attributes": {"k": {"state": {"u": ""}}}}}}}))
+    w(f"{PKG}/translations/en.json", "{}"), w(f"{PKG}/translations/sv.json", "{}"), w(f"{PKG}/www/card.js", "")
+    w("blueprints/automation/b.yaml", "")
+    w("tests/profiles.py", "def prices(profile, s):\n    if profile == 'p1':\n        pass\n    elif profile == 'p2':\n        pass\n"
+      "def weather(profile, s):\n    if profile == 'w1':\n        pass\n")
+    w("tests/golden.py", "SCENARIOS: dict = {'g1': dict(), 'g2': dict()}\n")
+    w("dev/audit/config/bugclasses.json", json.dumps({"_note": "x", "A": {"status": "open", "kind": "production"},
+                                                       "B": {"status": "barriered", "kind": "instrument"}}))
+    w(OBJECTIVE, json.dumps({"population": [{"axis": "mode", "kind": "tuple", "file": f"{PKG}/const.py", "symbol": "MODES"},
+                                            {"axis": "price_shape", "kind": "compare", "file": "tests/profiles.py", "function": "prices", "argument": "profile"},
+                                            {"axis": "size", "kind": None, "no_read": "r", "builder": "G"}]}))
+    w(IDENTITIES, json.dumps({"identities": [{"step": "M1", "id": "i1", "identity": "x", "grid": ["mode"]},
+                                             {"step": "M3", "id": "i2", "identity": "y", "grid": ["golden", {"axis": "noise", "levels": ["a", "b", "c"]}]}]}))
+    plant_bundles(root)
+
+
+def plant_bundles(root):
+    (root / BUNDLES).write_text(json.dumps({"bundles": [{"install": f"i{k}", "date": "2026-01-02", "round": 1, "steps": ["M1"], "evidence": "tests/profiles.py"} for k in (1, 2)]}))
+
+
+def cut(path, old, new=""):
+    """An edit of the planted repo that refuses to match nothing."""
+    def go(root):
+        t = (root / path).read_text()
+        if old not in t:
+            raise AssertionError(f"self-test edit of {path} matched nothing: {old!r}")
+        (root / path).write_text(t.replace(old, new, 1))
+    return go
+
+
+def put(path, text):
+    return lambda root: (root / path).write_text(text)
+
+
+def rm(*paths):
+    return lambda root: [(root / p).unlink() for p in paths]
+
+
+def both(*fs):
+    return lambda root: [f(root) for f in fs]
+
+
+def edit_json(path, fn):
+    def go(root):
+        d = json.loads((root / path).read_text())
+        fn(d)
+        (root / path).write_text(json.dumps(d))
+    return go
+
+
+X, CO, CF = f"{PKG}/x.py", f"{PKG}/coordinator.py", f"{PKG}/config_flow.py"
+# the entry points the planted __init__.py defines, typed apart from ENTRY_FNS so a dropped one shows
+ENTRY = ("async_setup", "async_setup_entry", "async_unload_entry", "async_remove_entry", "async_migrate_entry", "async_update_options")
+# universe, options, the planted count, the edit deleting one item, the count after it, the edit emptying the source
+PLANTED = [
+    ("d0-grid", {}, 2 * 1 * 2 * 2 * 5 * 3, cut("tests/profiles.py", "    elif profile == 'p2':\n        pass\n"), 60,
+     put("tests/profiles.py", "def prices(profile, s):\n    pass\ndef weather(profile, s):\n    pass\n")),
+    ("d0-modules", {}, 8, cut(f"{PKG}/y.py", "import custom_components.heatpump_optimizer.u\n"), 7, rm(f"{PKG}/optimizer.py")),
+    ("d1-lifecycle", {}, 2 + len(ENTRY), cut(X, "    async_track_time_interval(1)\n"), 1 + len(ENTRY), both(put(X, ""), put(f"{PKG}/__init__.py", ""))),
+    ("d1-stores", {}, 6, cut(f"{PKG}/store.py", ", K: {}"), 5, put(f"{PKG}/store.py", "")),
+    ("d1-inputs", {}, 6, cut(CF, "    _F('s', CONF_F_SENSOR, '', widget=_entity_of('sensor')),\n"), 5,
+     both(put(CF, ""), put(f"{PKG}/entry_config.py", "FACTORY_KEPT = {}\n"))),
+    ("d1-solve-state", {}, 3, cut(CO, "return self.a, self.c", "return self.a"), 2, put(CO, "")),
+    ("d1-excepts", {}, 2, cut(X, "    except ValueError:\n        pass\n"), 1, put(X, "")),
+    ("d1-parsers", {}, 4, cut(f"{PKG}/p.py", "    await m.async_subscribe('t')\n"), 3, put(f"{PKG}/p.py", "")),
+    ("d2-identities", {}, 2, edit_json(IDENTITIES, lambda d: d["identities"].pop()), 1, edit_json(IDENTITIES, lambda d: d["identities"].clear())),
+    ("d2-identities", {"cells": True}, 2 + 2 * 3, cut("tests/golden.py", ", 'g2': dict()"), 2 + 1 * 3, put("tests/golden.py", "SCENARIOS = {}\n")),
+    ("d3-sites", {"ast_only": True}, 5, cut(X, "    except ValueError:\n        pass\n"), 4, put(X, "")),
+    ("d8-cells", {}, 6 * 2, rm(f"{PKG}/translations/sv.json"), 6, rm(f"{PKG}/translations/sv.json", f"{PKG}/translations/en.json")),
+    ("d9-collections", {}, 2, cut(CO, "self.b = deque(maxlen=3)", "self.b = None"), 1, put(CO, "")),
+    ("d9-attributes", {}, 2, cut(f"{PKG}/e.py", "    _attr_extra_state_attributes = {}", "    pass"), 1, put(f"{PKG}/e.py", "")),
+    ("d9-solves", {}, 4, cut(CO, "return submit(go)", "return None"), 3, cut(f"{PKG}/optimizer.py", "return _multi_start_minimize() or go(c)", "return None")),
+    ("d12-cells", {}, 4 + 2, rm("blueprints/automation/b.yaml"), 5, rm(OBJECTIVE)),
+    ("d12-cells", {"pairs": True}, 4 + 4 + 2, cut(f"{PKG}/const.py", "MODES = ('m1', 'm2')", "MODES = ('m1',)"), 3 + 2 + 2,
+     rm("blueprints/automation/b.yaml", f"{PKG}/www/card.js")),
+    ("d14-classes", {}, 2, edit_json("dev/audit/config/bugclasses.json", lambda d: d.pop("B")), 1, put("dev/audit/config/bugclasses.json", "{}")),
+    ("d15-installs", {}, 2, edit_json(BUNDLES, lambda d: d["bundles"].pop()), 1, edit_json(BUNDLES, lambda d: d["bundles"].clear())),
+    ("d16-writes", {}, 3, cut(X, "    hass.services.async_call('a', 'b')\n"), 2, put(X, "")),
+    ("d16-writes", {"cells": True}, 3 * 2 * 4, cut(f"{PKG}/const.py", "('off', 'control')", "('off',)"), 3 * 1 * 4,
+     cut(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'control')\n")),
+    ("d17-features", {}, 9, cut(f"{PKG}/services.yaml", "set_b:\n"), 8,
+     both(put(f"{PKG}/services.yaml", ""), put(f"{PKG}/strings.json", "{}"), rm("blueprints/automation/b.yaml"))),
+]
+
+
+def self_test():
+    arms, fails = 0, []
+
+    def arm(name, got, want):
+        nonlocal arms
+        arms += 1
+        if got != want:
+            fails.append(f"{name}: got {got!r}, want {want!r}")
+
+    def count(u, t, **opt):
+        try:
+            with contextlib.redirect_stderr(io.StringIO()):
+                return len(run(u, t, **opt))
+        except Refuse:
+            return "Refuse"
+
+    live = Path(".")
+    for u in UNIVERSES:
+        for opt in ({}, *[o for n, o, *_ in PLANTED if n == u and o and "ast_only" not in o], *([{"plane": "price-weather"}] if u == "d0-grid" else [])):
+            try:
+                with contextlib.redirect_stderr(io.StringIO()):
+                    ls = run(u, live, **opt)
+            except Refuse as e:
+                ls = []
+                fails.append(f"live {u} {opt}: {e}")
+            arm(f"live {u} {opt}", (len(ls) >= 1, ls == sorted(ls), len(ls) == len(set(ls))), (True, True, True))
+    try:
+        with contextlib.redirect_stderr(io.StringIO()):
+            d3_all = run("d3-sites", live)
+            by_state = {st: run("d3-sites", live, state=st) for st in ("killed", "triaged", "unrecorded") if any(l.split(" #")[0].endswith(" " + st) for l in d3_all)}
+            by_file = [l.split() for l in run("d3-sites", live, by_file=True)]
+        arm("live d3-sites: the --state filters partition the universe", sorted(l for ls in by_state.values() for l in ls), d3_all)
+        arm("live d3-sites: each --state filter holds only its state", all(l.split(" #")[0].endswith(" " + st) for st, ls in by_state.items() for l in ls), True)
+        arm("live d3-sites --by-file: each file's three state counts sum to its total, and the totals to the universe",
+            (all(int(r[1]) == sum(map(int, r[2:5])) for r in by_file), sum(int(r[1]) for r in by_file)), (True, len(d3_all)))
+    except Refuse as e:
+        fails.append(f"live d3-sites options: {e}")
+    try:
+        arm("live briefs", len(briefs(live)) >= 1, True)
+    except Refuse as e:
+        fails.append(f"live briefs: {e}")
+    arm("every universe has a planted arm", sorted({n for n, *_ in PLANTED}), sorted(UNIVERSES))
+    for u, opt, n, delete, after, empty in PLANTED:
+        for label, edit, want in (("planted", None, n), ("one item deleted", delete, after), ("source emptied", empty, "Refuse")):
+            t = Path(tempfile.mkdtemp())
+            try:
+                plant(t)
+                if edit:
+                    edit(t)
+                arm(f"{u} {opt or ''} {label}", count(u, t, **opt), want)
+            finally:
+                shutil.rmtree(t, ignore_errors=True)
+    t = Path(tempfile.mkdtemp())
+    try:
+        plant(t)
+        arm("d0-grid plane", run("d0-grid", t, plane="price-weather"), ["p1/w1", "p2/w1"])
+        arm("d14 open", run("d14-classes", t, status="open"), ["open production A"])
+        arm("d1-stores lines: DOMAINS keys, each earlier step of CONFIG_ENTRY_VERSION and of a *_STORE_VERSION, a v1 store once",
+            run("d1-stores", t), ["store a", "store b", f"upgrade {PKG}/const.py:CONFIG_ENTRY_VERSION v1->3", f"upgrade {PKG}/const.py:CONFIG_ENTRY_VERSION v2->3",
+                                  f"upgrade {PKG}/store.py:LEDGER_STORE_VERSION v1->2", f"upgrade {PKG}/store.py:MAP_STORE_VERSION v1 (no earlier version)"])
+        arm("d1-inputs lines: a flow key behind an entity selector (one outside the CONF_*_ENTITY shape, two a loop binds), "
+            "and a key the reset keeps as an entity assignment by the wiring's rule or its literal entry",
+            run("d1-inputs", t), [f"input {k}" for k in ("CONF_A_ENTITY", "CONF_B_ENTITY", "CONF_F_SENSOR", "CONF_H1", "CONF_H2", "CONF_W_SENSOR")])
+        for label, edit in (("an entity selector outside an `_F` row", cut(CF, "ROWS = (", "LOOSE = _entity_of('x')\nROWS = (")),
+                            ("an entity selector row whose key is no name", cut(CF, "_F('s', CONF_A_ENTITY,", "_F('s', 'a_entity',")),
+                            ("a wiring rule holding a test the census cannot read", cut(f"{PKG}/entry_config.py", "key.endswith('_entity')", "key[-7:] == '_entity'")),
+                            ("a FACTORY_KEPT holding a second comprehension", cut(f"{PKG}/entry_config.py", "**_WIRING})", "**_WIRING, **{k: 'other' for k in ()}})")),
+                            ("an isinstance test on the loop's name, not its value", cut(f"{PKG}/entry_config.py", "isinstance(key, str)", "isinstance(name, str)"))):
+            g = Path(tempfile.mkdtemp())
+            try:
+                plant(g)
+                edit(g)
+                arm(f"d1-inputs {label} is refused", count("d1-inputs", g), "Refuse")
+            finally:
+                shutil.rmtree(g, ignore_errors=True)
+        arm("d1-excepts lines carry broad or narrow", [l.split()[1] for l in run("d1-excepts", t)], ["broad", "narrow"])
+        arm("d1-lifecycle lines: an async_track_* call, a LIFE_CALLS call and every entry point",
+            run("d1-lifecycle", t), sorted([f"async_create_task {X}:12 f", f"async_track_time_interval {X}:11 f", *[f"entry {f}" for f in ENTRY]]))
+        arm("d16-writes lines: the .services.async_call sites and log_held, not an async_call on another receiver",
+            run("d16-writes", t), [f"hold {X}:4 f", f"write {X}:2 f", f"write {X}:3 f"])
+        arm("d1-parsers lines: a parse def, json.loads, a bare .json() and async_subscribe, not a .json(x) with an argument",
+            run("d1-parsers", t), [f"def {PKG}/p.py:2 parse_a", f"json {PKG}/p.py:3 parse_a", f"response {PKG}/p.py:5 g", f"subscribe {PKG}/p.py:7 g"])
+        arm("d0-modules follows `from <package> import <module>`", f"{PKG}/t.py" in run("d0-modules", t), True)
+        arm("d9-collections a module-level function's self is no class's collection", [l for l in run("d9-collections", t) if l.startswith("helper.")], [])
+        arm("d9-solves lines: the solver's call, the recursive call inside its module, the coordinator's call and its bare reference",
+            [(l.split(" <- ")[0], l.rsplit(" ", 1)[-1]) for l in run("d9-solves", t)],
+            [("path go", "C.cycle"), ("path go", "(ref)"), ("path go", "go"), ("solve _multi_start_minimize", "go")])
+        arm("d0-modules follows an absolute import of the package", f"{PKG}/u.py" in run("d0-modules", t), True)
+        arm("d3-sites --ast --by-file counts the sites per file", run("d3-sites", t, ast_only=True, by_file=True), [f"{X} 5"])
+        quiet = contextlib.redirect_stderr(io.StringIO())
+        cells = run("d0-grid", t)
+        arm("d0-grid a cell names D0.md step 4's axis levels", [sorted({c.split("/")[k] for c in cells}) for k in (2, 3, 4, 5)],
+            [sorted(TOPOLOGY), sorted(DHW), sorted(PLANT), ["24h", "48h", "6h"]])
+        arm("d0-grid the two plants round 10's escapes name are levels", {"manual-valve-buffer", "flow-setpoint-behind-valve"} <= set(PLANT), True)
+        arm("d3-sites with no ledger source and no --ast is refused", count("d3-sites", t), "Refuse")
+        rm(CO)(t)
+        arm("d0-modules with no coordinator.py is refused", count("d0-modules", t), "Refuse")
+        shutil.rmtree(t)
+        t.mkdir()
+        plant(t)
+        arm("d9-solves a caller outside the solver's module is printed and not climbed", [l for l in run("d9-solves", t) if "cycle <-" in l], [])
+        with quiet:
+            arm("d12 a cell with no ledger row is not run", {l.split("\t", 1)[1] for l in run("d12-cells", t)}, {"not run"})
+        led = t / "ledger.tsv"
+        for label, text, want in (("a ledger row is joined", "level mode=m1\tsimulation\ttests/x.py::t\n", 6),
+                                  ("an unknown source is refused", "level mode=m1\thearsay\ttests/x.py::t\n", "Refuse"),
+                                  ("a row asserting nothing is refused", "level mode=m1\tsimulation\t \n", "Refuse"),
+                                  ("a row naming no cell is refused", "level mode=m9\tsimulation\ttests/x.py::t\n", "Refuse"),
+                                  ("a pair row without --pairs is refused", "pair mode=m1 & price_shape=p1\tbundle\ttests/x.py::t\n", "Refuse")):
+            led.write_text(text)
+            arm(f"d12 ledger: {label}", count("d12-cells", t, ledger=str(led)), want)
+        led.write_text("level mode=m1\tsimulation\ttests/x.py::t\n")
+        with contextlib.redirect_stderr(io.StringIO()):
+            arm("d12 ledger: the joined row prints its source and test", [l for l in run("d12-cells", t, ledger=str(led)) if "not run" not in l],
+                ["level mode=m1\tsimulation\ttests/x.py::t"])
+        led.write_text("# a comment\nlevel mode=m9\tsimulation\ttests/x.py::t\n")
+        try:
+            with contextlib.redirect_stderr(io.StringIO()):
+                run("d12-cells", t, ledger=str(led))
+            msg = "passed"
+        except Refuse as e:
+            msg = str(e)
+        arm("a ledger refusal names the row's line", f"{led}:2:" in msg, True)
+        arm("d12 a missing ledger is refused", count("d12-cells", t, ledger=str(t / "none.tsv")), "Refuse")
+        arm("with no ledger a census prints its items alone", run("d1-inputs", t)[:2], ["input CONF_A_ENTITY", "input CONF_B_ENTITY"])
+        for label, text, want in (("a census line is joined to its driving test, the rest not run", "# c\n\ninput CONF_A_ENTITY\ttests/x.py::t\n",
+                                   ["input CONF_A_ENTITY\ttests/x.py::t"] + [f"input {k}\tnot run" for k in ("CONF_B_ENTITY", "CONF_F_SENSOR", "CONF_H1", "CONF_H2", "CONF_W_SENSOR")]),
+                                  ("a census row naming no test is refused", "input CONF_A_ENTITY\t\n", "Refuse"),
+                                  ("a census row with a source column is refused", "input CONF_A_ENTITY\tsimulation\ttests/x.py::t\n", "Refuse"),
+                                  ("a census row naming no item is refused", "input CONF_Z_ENTITY\ttests/x.py::t\n", "Refuse")):
+            led.write_text(text)
+            try:
+                got = run("d1-inputs", t, ledger=str(led))
+            except Refuse:
+                got = "Refuse"
+            arm(f"ledger: {label}", got, want)
+        bd = t / "dev/governance/dimensions"
+        bd.mkdir(parents=True)
+
+        def cited(text):
+            (bd / "D1.md").write_text(text)
+            try:
+                return briefs(t)
+            except Refuse:
+                return "Refuse"
+        arm("briefs: a cited universe that prints is ok, across a line wrap", cited("1. Per line of `python3 tools/audit/enumerate.py\n   d2-identities --cells`.\n"), ["ok D1 d2-identities --cells"])
+        arm("briefs: a citation of no universe is refused", cited("1. `enumerate.py d1-nothing`\n"), "Refuse")
+        arm("briefs: a tree whose briefs cite none is refused", cited("1. Enumerate by hand.\n"), "Refuse")
+        arm("briefs: one refused citation beside a good one refuses the tree", cited("1. `enumerate.py d1-inputs` and `enumerate.py d1-nothing`\n"), "Refuse")
+        arm("briefs: a citation's options are run as cited", (cut(f"{PKG}/const.py", "PUMP_DUTY_MODES: Final = ('off', 'control')\n")(t), cited("1. `enumerate.py d16-writes --cells`\n"))[1], "Refuse")
+        (t / BUNDLES).write_text('{"bundles": []}')
+        arm("briefs: a cited universe that is empty is refused", cited("1. `enumerate.py d15-installs`\n"), "Refuse")
+        plant_bundles(t)
+        edit_json(BUNDLES, lambda d: d["bundles"][0].update(evidence="tests/gone.py"))(t)
+        arm("d15 a bundle whose evidence is not in the tree is refused", count("d15-installs", t), "Refuse")
+        cut(CO, "    def _solve_hubs(self):\n        return self.b\n")(t)
+        arm("d1-solve-state a solve-thread entry that moved is refused, not read short", count("d1-solve-state", t), "Refuse")
+        edit_json(IDENTITIES, lambda d: d["identities"][0].update(grid=["no_such_axis"]))(t)
+        arm("d2 a grid axis with no level is refused", count("d2-identities", t), "Refuse")
+        edit_json(IDENTITIES, lambda d: d["identities"][0].update(grid=["mode"], id=""))(t)
+        arm("d2 an identity with no id is refused", count("d2-identities", t), "Refuse")
+        edit_json(IDENTITIES, lambda d: d["identities"][0].update(id="i1", step="S1"))(t)
+        arm("d2 an identity whose step is not M<n> is refused", count("d2-identities", t), "Refuse")
+        edit_json(BUNDLES, lambda d: d["bundles"][0].update(evidence="tests/profiles.py", date="yesterday"))(t)
+        arm("d15 a bundle with no date is refused", count("d15-installs", t), "Refuse")
+        for total in ("LEVELS", "PAIRS"):
+            real = population_axes
+            try:
+                globals()["population_axes"] = lambda repo: (real(repo)[0], {**real(repo)[1], total: 0})
+                arm(f"d12 a cell count that disagrees with the population's {total} is refused", count("d12-cells", t, pairs=True), "Refuse")
+            finally:
+                globals()["population_axes"] = real
+        edit_json(OBJECTIVE, lambda d: d["population"][0].update(symbol="NO_SUCH_TUPLE"))(t)
+        arm("d12 an unreadable population axis is refused", count("d12-cells", t), "Refuse")
+        g = Path(tempfile.mkdtemp())
+        try:
+            plant(g)
+            (g / "blueprints/automation/untracked.yaml").write_text("")
+            sys.path.append(str(Path(__file__).resolve().parents[2] / "tests"))
+            from throwaway_git import throwaway_git_init
+            env = throwaway_git_init(g, "-q")
+            for a in (["add", "-A", ":!blueprints/automation/untracked.yaml"], ["commit", "-q", "-m", "plant"]):
+                subprocess.run(["git", *a], cwd=g, env=env, capture_output=True, check=True)
+            arm("in a git checkout an untracked file is in no universe", [l for l in run("d17-features", g) if "blueprint" in l], ["blueprint blueprints/automation/b.yaml"])
+        finally:
+            shutil.rmtree(g, ignore_errors=True)
+    finally:
+        shutil.rmtree(t, ignore_errors=True)
+    if fails:
+        print("SELF-TEST FAILED: " + "; ".join(fails), file=sys.stderr)
+        return 1
+    print(f"SELF-TEST passed ({arms} arms)")
+    return 0
+
+
+def main(argv=None):
+    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
+    ap.add_argument("universe", nargs="?", choices=sorted(UNIVERSES))
+    ap.add_argument("--repo", default=".")
+    ap.add_argument("--cells", action="store_true")
+    ap.add_argument("--pairs", action="store_true")
+    ap.add_argument("--ledger")
+    ap.add_argument("--status")
+    ap.add_argument("--plane", choices=("price-weather",))
+    ap.add_argument("--state", choices=("killed", "triaged", "unrecorded"))
+    ap.add_argument("--by-file", action="store_true")
+    ap.add_argument("--ast", action="store_true")
+    ap.add_argument("--self-test", action="store_true")
+    ap.add_argument("--briefs", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    if not a.universe and not a.briefs:
+        ap.error("universe required")
+    try:
+        ls = briefs(Path(a.repo)) if a.briefs else run(a.universe, a.repo, cells=a.cells, pairs=a.pairs, ledger=a.ledger, status=a.status, plane=a.plane,
+                 state=a.state, by_file=a.by_file, ast_only=a.ast)
+    except (Refuse, SyntaxError, json.JSONDecodeError) as e:
+        print(f"REFUSE: {e}", file=sys.stderr)
+        return 2
+    print("\n".join(ls))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/tools/audit/machinery_ratchet.py b/tools/audit/machinery_ratchet.py
index acc96a6143..46a30f3d91 100644
--- a/tools/audit/machinery_ratchet.py
+++ b/tools/audit/machinery_ratchet.py
@@ -47,8 +47,21 @@ in the budgets file's `exemptions` list exempts merge M only when all hold:
     are read from M's tree too.
 An exempted merge leaves the window and the next older merge fills its slot.
 
-Exit 0: inside both caps. 1: a cap exceeded. 2: usage, an unreadable budgets
-file, or a history shorter than the window.
+THE TARGET (tvofi, 2026-11-13, card P2: a target that declines over a round,
+not a record of the status quo). `dev/governance/config/
+machinery_target_budgets.json` holds `anchor` (the commit the cap was recorded
+at), `every_merges` and `step`. With n the first-parent merges after the anchor
+up to the base (PR mode) or the head (push mode), the target is
+  nonproduction_merges - step * floor(n / every_merges), never below 0,
+compared against target plus nonproduction_merges' band, again by merge count,
+never hours. It refuses only a candidate that is not production and not
+exempted: a production candidate cannot raise the metric, and in push mode the
+target is a report line, so the schedule passing the window turns no check on
+main red. The caps above stay the ceiling in both modes. No file, no target.
+
+Exit 0: inside both caps. 1: a cap, or the target on its candidate, exceeded.
+2: usage, an unreadable budgets or target file, or a history shorter than the
+window.
 """
 from __future__ import annotations
 
@@ -63,6 +76,8 @@ from fractions import Fraction
 from pathlib import Path
 
 BUDGETS = "dev/governance/config/machinery_budgets.json"
+TARGET_BUDGETS = "dev/governance/config/machinery_target_budgets.json"
+TARGET_KEYS = ("every_merges", "step")
 PRODUCT_PREFIXES = ("custom_components/", "blueprints/")
 RECORD_PREFIXES = ("dev/programme/",)
 RECORD_FILES = ("RELEASE_NOTES.md", "VERSION")
@@ -308,6 +323,42 @@ def load_budgets(text: str) -> dict:
     return doc
 
 
+def load_target(repo: str, rev: str) -> dict | None:
+    """The target file at `rev`, None when it is absent, refused when it is
+    malformed or its anchor is not an ancestor of `rev`: an unreadable target
+    is never no target."""
+    r = _git(repo, "show", f"{rev}:{TARGET_BUDGETS}", check=False)
+    if r.returncode != 0:
+        return None
+    try:
+        doc = json.loads(r.stdout)
+    except ValueError as e:
+        raise Refusal(f"{TARGET_BUDGETS} does not parse ({e})")
+    if not isinstance(doc, dict):
+        raise Refusal(f"{TARGET_BUDGETS} is not an object")
+    extra = sorted(k for k in doc if not k.startswith("_") and k not in ("anchor", *TARGET_KEYS))
+    if extra:
+        raise Refusal(f"{TARGET_BUDGETS}: {extra} is not a key this ratchet reads")
+    for k in TARGET_KEYS:
+        v = doc.get(k)
+        if isinstance(v, bool) or not isinstance(v, int) or v < (1 if k == "every_merges" else 0):
+            raise Refusal(f"{TARGET_BUDGETS}: {k} is {v!r}")
+    a = doc.get("anchor")
+    if not isinstance(a, str) or not re.fullmatch(r"[0-9a-f]{40}", a):
+        raise Refusal(f"{TARGET_BUDGETS}: anchor is {a!r}, not a full commit sha")
+    return doc
+
+
+def scheduled_target(repo: str, tip: str, cap: int, tdoc: dict) -> tuple[int, int]:
+    """(the target, n merges past the anchor) at `tip`."""
+    a = tdoc["anchor"]
+    if _git(repo, "merge-base", "--is-ancestor", a, tip, check=False).returncode != 0:
+        raise Refusal(f"{TARGET_BUDGETS}: anchor {a[:12]} is not an ancestor of {tip}")
+    n = sum(1 for line in _git(repo, "rev-list", "--first-parent", "--parents", f"{a}..{tip}")
+            .stdout.splitlines() if len(line.split()) == 3)
+    return max(0, cap - tdoc["step"] * (n // tdoc["every_merges"])), n
+
+
 def measure(repo: str, head: str, budgets_doc: dict, base: str | None = None,
             pr: int | None = None, grader: Grader | None = None) -> tuple[dict, list, list]:
     """The window's metrics: push mode without `base`, PR mode with it."""
@@ -369,6 +420,18 @@ def check(repo: str, head: str, base: str | None, pr: int | None, out=print) ->
     for c in CAPS:
         cap, band = doc[c], doc[c + BAND_SUFFIX]
         out(f"  {'FAIL' if c in bad else 'ok  '} {c} {m[c]} <= {cap} + band {band}")
+    tdoc = load_target(repo, head)
+    if tdoc is not None:
+        c = CAPS[0]
+        t, n = scheduled_target(repo, base or head, doc[c], tdoc)
+        cand = rows[0] if base and rows and rows[0]["sha"] == head else None
+        binds = cand is not None and cand["kind"] != "production"
+        past = m[c] > t + doc[c + BAND_SUFFIX]
+        word = ("FAIL" if past else "ok  ") if binds else "info"
+        out(f"  {word} target {c} {m[c]} <= {t} + band {doc[c + BAND_SUFFIX]} ({n} merge(s) "
+            f"past anchor {tdoc['anchor'][:12]}, {tdoc['step']} down per {tdoc['every_merges']})")
+        if binds and past:
+            bad.append("target")
     if bad:
         out("machinery_ratchet: refused; pay by landing production work, record an exemption "
             "the change earns (ratchet-budgets.md), or ask the owner for a raise")
@@ -679,6 +742,73 @@ def self_test() -> int:
                 got = "refused"
             ok(f"load_budgets refuses {label}", got, "refused")
 
+        # 6. The target: a schedule over merges past its anchor, binding only a
+        # non-production, unexempted candidate. Window 3, cap 2, band 0; the
+        # target falls by 2 every 2 merges past the anchor.
+        r = fresh("target")
+        r.merge(1, PRODM); r.merge(2, MACH); r.merge(3, PRODM); r.merge(4, MACH)
+        anchor = r.tip
+        tgt = lambda **k: [("set", TARGET_BUDGETS, json.dumps(
+            {"_comment": "fixture", "anchor": anchor, "every_merges": 2, "step": 2, **k}))]
+        r.merge(5, PRODM + budgets_ops(caps(m1=2, w=3)) + tgt())
+        # 1 merge past the anchor: the target is still 2. Each candidate is
+        # cut from the base's own tree, so no earlier candidate's lines leak in.
+        at = {"files": dict(r.files)}
+
+        def cand(ops: list, drop: tuple = ()) -> tuple[int, str]:
+            r.files = {k: v for k, v in at["files"].items() if k not in drop}
+            return run_cli(r, "--check", "--base", r.tip, "--head", r.side(ops), "--pr", "9")
+        rc, txt = cand(MACH)
+        ok("target: 1 merge past the anchor is still 2, so a machinery candidate at 2 passes",
+           (rc, "ok   target nonproduction_merges 2 <= 2 + band 0 (1 merge(s) past" in txt), (0, True))
+        r.merge(6, RECM)                              # 2 merges past: target 0
+        at["files"] = dict(r.files)
+        rc, txt = cand(MACH)
+        ok("target: 2 merges past it falls to 0 and refuses the machinery candidate under its cap",
+           (rc, "FAIL target nonproduction_merges 2 <= 0" in txt, "ok   nonproduction_merges 2 <= 2" in txt),
+           (1, True, True))
+        ok("target: a record candidate is not production and is refused too", cand(RECM)[0], 1)
+        rc, txt = cand(PRODM)
+        ok("target: a production candidate is never refused by it (a report line)",
+           (rc, "info target" in txt), (0, True))
+        ok("target: an exempted machinery candidate passes",
+           cand(MACH + budgets_ops(caps(m1=2, w=3, ex=[entry(9)])) + [("set", "ev/proof.txt", "m\n")])[0], 0)
+        rc, txt = run_cli(r, "--check", "--head", r.tip)
+        ok("target: push mode reports it and stays green under the cap", (rc, "info target" in txt), (0, True))
+        ok("target: --measure prints it beside the metrics",
+           {k: json.loads(run_cli(r, "--measure", "--head", r.tip)[1])[k]
+            for k in ("target", "merges_past_anchor")}, {"target": 0, "merges_past_anchor": 2})
+        ok("target: no file, no target: the refused candidate passes (null control)",
+           cand(MACH, drop=(TARGET_BUDGETS,))[0], 0)
+        for label, ops in (("an unread key", tgt(open_groups=1)), ("a zero every_merges", tgt(every_merges=0)),
+                           ("a short anchor", tgt(anchor=anchor[:12])),
+                           ("an anchor off the history", tgt(anchor="0" * 40))):
+            ok(f"target: {label} is refused, never read as no target", cand(MACH + ops)[0], 2)
+        ok("target: a file that is not an object is refused",
+           cand(MACH + [("set", TARGET_BUDGETS, "[]")])[0], 2)
+        ok("target: every_merges 1 and step 0 are the bounds it reads (null control)",
+           [cand(MACH + tgt(every_merges=1, step=s_))[0] for s_ in (0, 2)], [0, 1])
+        ok("target: the band is added to it, at the boundary (2 <= 0 + 2 passes, 2 > 0 + 1 refuses)",
+           [cand(MACH + budgets_ops(caps(m1=2, m1b=b_, w=3)))[0] for b_ in (2, 1)], [0, 1])
+        rc, txt = cand(MACH + budgets_ops(caps(m1=2, m1b=2, w=3)) + tgt(step=5))
+        ok("target: a schedule driven past zero holds at 0, never below it",
+           (rc, "target nonproduction_merges 2 <= 0 + band 2" in txt), (0, True))
+        # A PR head's own first-parent chain is the branch's, and a merge of
+        # main into it is one merge there: the schedule is read on the base.
+        r.files = dict(at["files"])
+        r.change(MACH)
+        head = r._commit([r._commit([anchor], "work"), r.tip], "Merge branch 'main' into b9")
+        rc, txt = run_cli(r, "--check", "--base", r.tip, "--head", head, "--pr", "9")
+        ok("target: a PR head carrying a merge of main is scheduled on the base (2 past, target 0)",
+           (rc, "FAIL target nonproduction_merges 2 <= 0 + band 0 (2 merge(s) past" in txt), (1, True))
+        # A stamp is a first-parent commit that is not a merge: it moves no target.
+        r.files = dict(at["files"])
+        r.change([("set", REC, "stamped\n")])
+        r.tip = r._commit([r.tip], "v1.0.0: stamp")
+        ok("target: a non-merge first-parent commit past the anchor is not counted",
+           {k: json.loads(run_cli(r, "--measure", "--head", r.tip)[1])[k]
+            for k in ("target", "merges_past_anchor")}, {"target": 0, "merges_past_anchor": 2})
+
     ok("--check-event: a base and a PR number select PR mode",
        event_args({"MACHINERY_BASE": "b", "MACHINERY_HEAD": "h", "MACHINERY_PR": "7"}), ("h", "b", 7))
     ok("--check-event: a base with no PR number is push mode at the head",
@@ -717,6 +847,10 @@ def main(argv: list[str]) -> int:
             doc = ({WINDOW_KEY: a.window} if a.window
                    else load_budgets(_budgets_text(a.repo, a.head, BUDGETS)))
             m, _, skipped = measure(a.repo, a.head, doc, a.base, pr)
+            tdoc = None if a.window else load_target(a.repo, a.head)
+            if tdoc is not None:
+                m["target"], m["merges_past_anchor"] = scheduled_target(
+                    a.repo, a.base or a.head, doc[CAPS[0]], tdoc)
             print(json.dumps({"head": _git(a.repo, "rev-parse", a.head).stdout.strip(), **m,
                               "exempted": [s["sha"] for s in skipped]}, sort_keys=True))
             if a.bands:
diff --git a/tools/audit/seat/INSTRUMENTS.md b/tools/audit/seat/INSTRUMENTS.md
index 9e37583b07..893cae7d25 100644
--- a/tools/audit/seat/INSTRUMENTS.md
+++ b/tools/audit/seat/INSTRUMENTS.md
@@ -29,6 +29,7 @@ re-runnable measurement harnesses a fixer or judge lands with a PR — its
 - [`role_pack.py` (tools/policy/)](instruments/role_pack.py.md) — renders one seat's policy pack: its role contract, the rules its reads load and the INSTRUMENTS.md entries it names, verbatim, in one file
 - [`approve_held_runs.sh`](instruments/approve_held_runs.sh.md) — approves the workflow runs GitHub holds `action_required` on a branch
 - [`check_scopes.py`](instruments/check_scopes.py.md) — proves the finder scopes are disjoint and complete within each dimension
+- [`enumerate.py`](instruments/enumerate.py.md) — prints one audit universe, one item per line, so a finder reports examined over a command's output
 - [`text_ledger.py`](instruments/text_ledger.py.md) — enumerates every unit a D5 or D6 seat judges and refuses a ledger that skips one
 - [`fold_ledger.py`](instruments/fold_ledger.py.md) — folds a round's JUDGE.json and sweeps into `bugclasses.json`
 - [`judge_batch.py`](instruments/judge_batch.py.md) — re-runs every finding's harness, perturbation and null control serially under the gate lease
diff --git a/tools/audit/seat/beat_jobs.py b/tools/audit/seat/beat_jobs.py
index fe64a76a7c..7eed46abc1 100644
--- a/tools/audit/seat/beat_jobs.py
+++ b/tools/audit/seat/beat_jobs.py
@@ -128,6 +128,11 @@ ROWS (the job table's `interval_s` in brackets):
                      A failed slot-take or worktree add is `darwin-selftest: UNREADABLE
                      <step> rc=N: ...`, runs nothing and leaves the cycle where it was, so
                      the next pass retries it.
+  cp-owed [300]      owed_watch.py `cp-owed --repo R --fired <fire_ledger> --checkout <repo>`: one
+                     `CP-OWED <arm> <subject>` line per critical-path or outside step past its
+                     grace (owner directive tvofi 2026-11-09, "never let the critical path or
+                     outside PRs slip, ever"); `cp-owed: UNREADABLE` on a non-zero rc, never
+                     its partial lines.
   bottleneck [1800]  bottleneck_check.py `--checkout <repo> --train-log
                      <train_log> --wip-cap <plan_slots> --memory
                      state/bottleneck.json`: its `BOTTLENECK:` and
@@ -177,7 +182,7 @@ import time
 from pathlib import Path
 
 ROWS = ("tick-digest", "owed-check", "roster-drain", "plan-beat", "gantt", "verdict-audit", "pulse",
-        "cancel-sweep", "disk", "opener", "loop-cwd", "head-watch", "audit-dispatch", "outside-intake", "bottleneck",
+        "cancel-sweep", "disk", "opener", "loop-cwd", "head-watch", "audit-dispatch", "outside-intake", "cp-owed", "bottleneck",
         "scorecard", "ci-attempt", "toolchain-promote", "darwin-selftest")
 HOLD_STALE_S = 24 * 3600  # gap 6: a hold line never expired
 #: roster-drain starts no op past this many seconds into a pass; the rest wait for the next pass. At
@@ -187,7 +192,7 @@ ROSTER_PASS_BUDGET_S = 450
 #: The board's actionable family (carry 20's list), keyed on the texts
 #: orchestrator_tick.py and ledger.py print; the self-test pins each literal there.
 FAMILY = re.compile(
-    r"^(?:OWED\b|DISPATCH:|OWNER FLAG:|BLOCKED-UNFIXED:|DESIGN-BUILD:|UNREADABLE:|DESIGN OWED:"
+    r"^(?:OWED\b|DISPATCH:|OWNER FLAG:|BLOCKED-UNFIXED:|DESIGN-BUILD:|UNREADABLE:|DESIGN OWED:|DESIGN-REVIEW OWED:|UNDISPATCHED:|OUTSIDE-CHAIN-IDLE "
     r"|REVIEW OWED:|RECORD-OWED:|REVIEW STALLED:|UNLEVELLED:|APPROVAL-OWED:|MERGE-READY:|main-red "
     r"|main \S+: REQUIRED not green"
     r"|#\d+: (?:RAISE APPROVAL OWED|NOT REVIEWABLE|mergeable state DIRTY|RED unanswered"
@@ -693,6 +698,19 @@ def outside_intake(ctx: Ctx) -> None:
     write_job(ctx, "outside-intake", [why or f"outside-intake: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
 
 
+def cp_owed(ctx: Ctx) -> None:
+    """owed_watch.py cp-owed: one CP-OWED line per critical-path or outside step past its grace."""
+    got = ctx.need("cp-owed", "repo", "fire_ledger")
+    if got is None:
+        return
+    rc, out, err = ctx.py("tools/audit/seat/owed_watch.py", "cp-owed", "--repo", got[0], "--fired", got[1],
+                          "--checkout", str(ctx.repo))
+    if rc != 0:
+        why = next((ln for ln in out.splitlines() if ln.startswith("cp-owed: UNREADABLE")), None)
+        return write_job(ctx, "cp-owed", [why or f"cp-owed: UNREADABLE rc={rc}: {(err.strip().splitlines() or [''])[-1]}"])
+    write_job(ctx, "cp-owed", [ln for ln in out.splitlines() if ln.startswith("CP-OWED ")])
+
+
 def bottleneck(ctx: Ctx) -> None:
     """bottleneck_check.py: one line per flow metric past its threshold, held once per trip by its memory."""
     got = ctx.need("bottleneck", "train_log", "plan_slots")
@@ -842,8 +860,9 @@ def darwin_selftest(ctx: Ctx) -> None:
 RUN = {"tick-digest": tick_digest, "owed-check": owed_check, "roster-drain": roster_drain,
        "plan-beat": plan_beat, "gantt": gantt, "verdict-audit": verdict_audit, "pulse": pulse, "cancel-sweep": cancel_sweep, "disk": disk,
        "opener": opener, "loop-cwd": loop_cwd, "head-watch": head_watch, "audit-dispatch": audit_dispatch,
-       "outside-intake": outside_intake, "bottleneck": bottleneck, "scorecard": scorecard, "ci-attempt": ci_attempt,
-       "toolchain-promote": toolchain_promote, "darwin-selftest": darwin_selftest}
+       "outside-intake": outside_intake, "cp-owed": cp_owed, "bottleneck": bottleneck, "scorecard": scorecard,
+       "ci-attempt": ci_attempt, "toolchain-promote": toolchain_promote,
+       "darwin-selftest": darwin_selftest}
 
 
 def main(argv: list[str]) -> int:
diff --git a/tools/audit/seat/beat_jobs_selftest.py b/tools/audit/seat/beat_jobs_selftest.py
index d434391980..7784f368d6 100644
--- a/tools/audit/seat/beat_jobs_selftest.py
+++ b/tools/audit/seat/beat_jobs_selftest.py
@@ -242,7 +242,7 @@ def cases(bj) -> dict[str, bool]:
         digest(c) == (FIXTURE / "digest.txt").read_text())
     src = "".join((HERE / f).read_text() for f in ("orchestrator_tick.py", "ledger.py"))
     lits = ["OWED", "DISPATCH:", "OWNER FLAG:", "BLOCKED-UNFIXED:", "DESIGN-BUILD:", "UNREADABLE:",
-            "DESIGN OWED:", "REVIEW OWED:", "RECORD-OWED:", "REVIEW STALLED:", "UNLEVELLED:", "APPROVAL-OWED:",
+            "DESIGN OWED:", "DESIGN-REVIEW OWED:", "UNDISPATCHED:", "OUTSIDE-CHAIN-IDLE ", "REVIEW OWED:", "RECORD-OWED:", "REVIEW STALLED:", "UNLEVELLED:", "APPROVAL-OWED:",
             "MERGE-READY:", "main-red ", "REQUIRED not green", "RAISE APPROVAL OWED", "NOT REVIEWABLE",
             "mergeable state DIRTY", "RED unanswered", "code-owned with no ",
             "BOARD measured from origin/main at"]
@@ -803,6 +803,32 @@ def cases(bj) -> dict[str, bool]:
     bj.verdict_audit(c)
     res["verdict-audit null: nothing unheld writes no byte"] = not files(c)
 
+    # cp-owed
+    cpl = "CP-OWED DESIGN-REVIEW-OWED R11-X 64m past its 10m grace [OUTSIDE] -- design/R11-X at abc has no design review"
+    c, f = fresh(overlay={"repo": "o/r", "fire_ledger": "/fired"},
+                 answers={"owed_watch.py": (0, "note\n" + cpl + "\n", "")})
+    pre = "CP-OWED" not in digest(c)
+    bj.cp_owed(c)
+    v = (f.calls or [[]])[0]
+    res["cp-owed: a CP-OWED line reaches the digest, and the repo, ledger and checkout are handed on"] = (
+        pre and digest(c) == bj.norm(cpl) + "\n" and "cp-owed" in v and arg(v, "--repo") == "o/r"
+        and arg(v, "--fired") == "/fired" and arg(v, "--checkout") == str(root))
+    c, f = fresh(overlay={"repo": "o/r", "fire_ledger": "/fired"},
+                 answers={"owed_watch.py": (2, cpl + "\ncp-owed: UNREADABLE critical path: not JSON\n", "")})
+    bj.cp_owed(c)
+    res["cp-owed: rc 2 is its UNREADABLE line, never its partial lines"] = (
+        digest(c) == "cp-owed: UNREADABLE critical path: not JSON\n")
+    c, f = fresh(overlay={"repo": "o/r"})
+    bj.cp_owed(c)
+    res["cp-owed: an overlay with no fire_ledger is UNREADABLE and runs nothing"] = (
+        digest(c) == "cp-owed: UNREADABLE overlay lacks fire_ledger\n" and f.ran("owed_watch.py") == 0)
+    c, f = fresh(overlay={"repo": "o/r", "fire_ledger": "/fired"}, answers={"owed_watch.py": (0, "note\n", "")})
+    bj.cp_owed(c)
+    res["cp-owed null: nothing owed writes no byte"] = not files(c) and f.ran("owed_watch.py") == 1
+    row = [j for j in json.loads((HERE / "beatd.jobs.json").read_text())["jobs"] if j["name"] == "cp-owed"]
+    res["cp-owed: the table row runs every 300 s, under the shortest grace, and takes no class lock"] = (
+        len(row) == 1 and row[0]["interval_s"] <= 300 and row[0]["class"] is None)
+
     # pulse
     ok = "PULSE opener ok fine\npulse: 1 arms, 0 stopped, 0 unreadable at 2026-11-01T09:00:00Z\n"
     c, f = fresh(answers={"pulse.py": (0, ok, "")})
@@ -1401,6 +1427,14 @@ MUTANTS = {
                             "gantt: sweep_gantt is handed the plan, acks, roster, open PRs, live handoff rows and the fire ledger"),
     "verdict_filter_dropped": ('if ln.startswith("UNHELD ")])', "])",
                                "verdict-audit: an UNHELD line reaches the digest, and the repo, ledger and skip file are handed on"),
+    "cp_owed_filter_dropped": ('    write_job(ctx, "cp-owed", [ln for ln in out.splitlines() if ln.startswith("CP-OWED ")])',
+                               '    write_job(ctx, "cp-owed", out.splitlines())',
+                               "cp-owed: a CP-OWED line reaches the digest, and the repo, ledger and checkout are handed on"),
+    "cp_owed_rc_ignored": ('    if rc != 0:\n        why = next((ln for ln in out.splitlines() if ln.startswith("cp-owed: UNREADABLE"))',
+                           '    if False:\n        why = next((ln for ln in out.splitlines() if ln.startswith("cp-owed: UNREADABLE"))',
+                           "cp-owed: rc 2 is its UNREADABLE line, never its partial lines"),
+    "cp_owed_ledger_optional": ('got = ctx.need("cp-owed", "repo", "fire_ledger")', 'got = ctx.need("cp-owed", "repo", "repo")',
+                                "cp-owed: an overlay with no fire_ledger is UNREADABLE and runs nothing"),
     "verdict_rc_ignored": ('    if rc != 0:\n        return write_job(ctx, "verdict-audit",', '    if False:\n        return write_job(ctx, "verdict-audit",',
                            "verdict-audit: a failed run is UNREADABLE, never its partial lines"),
     "gantt_gh_rc_ignored": ('    if rc != 0:\n        return write_job(ctx, "gantt", [f"gantt: UNREADABLE gh pr list',
diff --git a/tools/audit/seat/beatd.jobs.json b/tools/audit/seat/beatd.jobs.json
index 11ae415e14..4c68b42507 100644
--- a/tools/audit/seat/beatd.jobs.json
+++ b/tools/audit/seat/beatd.jobs.json
@@ -280,6 +280,26 @@
       "class": null,
       "kind": "periodic"
     },
+    {
+      "name": "cp-owed",
+      "argv": [
+        "python3",
+        "-I",
+        "tools/audit/seat/beat_jobs.py",
+        "cp-owed",
+        "--state",
+        "$S"
+      ],
+      "cwd": "orch",
+      "interval_s": 300,
+      "timeout_s": 180,
+      "heartbeat_s": null,
+      "env_pass": [
+        "GH_TOKEN"
+      ],
+      "class": null,
+      "kind": "periodic"
+    },
     {
       "name": "bottleneck",
       "argv": [
diff --git a/tools/audit/seat/cloud_relay.sh b/tools/audit/seat/cloud_relay.sh
index 381e763672..095b3ceb2c 100644
--- a/tools/audit/seat/cloud_relay.sh
+++ b/tools/audit/seat/cloud_relay.sh
@@ -544,7 +544,18 @@ review_freeze() { # <pr> <head> <verdict refs file>: prints VERDICT, REVIEW or U
   v=$(awk -v p="$1" -v h="$2" '$1 == p && $2 == h { n = $4; at = $5 } END { if (n != "") print substr(n, 1, 8), (at == "" ? "-" : at) }' \
     "$bus/dispatched" 2>/dev/null)
   [ -n "$v" ] || return 1
-  echo "REVIEW dispatch=${v% *} at=${v#* }"
+  # The dispatch's verdict came back and the relay refused or disposed it (a pending-ci draft over a red,
+  # a blocked verdict refused, then disposed): that review is over, so it holds nothing (R10-RELAY-NOBODY-STALL,
+  # #3461 and #3479 held 15 and 12 min until a hand release). Else the line names the probe's state for the cure.
+  local pr8=refs/heads/probe/rev-$1-${v% *} ps led=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-relayed
+  ps=$(git ls-remote origin "$pr8" 2>/dev/null | awk 'NF { print $1; exit }')
+  if [ -n "$ps" ] && { grep -qxF "$pr8 $ps" "$led.refused" 2>/dev/null || disposed "$pr8" "$ps"; }; then  # mut:reviewrelease
+    echo "cloud_relay: RELEASED-REVIEW #$1: dispatch ${v% *}'s verdict ${ps:0:12} was refused or disposed" >&2; return 1
+  fi
+  if [ -z "$ps" ]; then ps="probe=none (in flight)"
+  elif grep -qxF "$pr8 $ps" "$led" 2>/dev/null; then ps="probe=${ps:0:8} relayed, not yet on verdict/$1"
+  else ps="probe=${ps:0:8} held by the relay (dispose it to release)"; fi
+  echo "REVIEW dispatch=${v% *} at=${v#* } $ps"
 }
 # THE TOOLS TREE (P283). update_pr.sh refuses a checkout behind origin/main under the tools
 # (pr_args.sh's pr_tools_fresh), and the relay's own checkout is stale whenever main moves them;
@@ -576,6 +587,9 @@ body_only_owed() { # <pr> <topic> <body sha> <head> <why>: a body-only handoff l
   echo "cloud_relay: BODY-ONLY #$1 handoff-body/$2 ${3:0:12} is newer than head ${4:0:12} and not applied: $5"
   level_line handoff-body-unapplied "refs/heads/handoff-body/$2" "$3" "#$1 $5" >> "$state/cloud-level-bodyonly.$$"
 }
+skip_owed() { # <pr> <topic> <handoff tip> <why>: a handoff the head lacks, left this pass, is owed on the level, never skipped in silence (#3358)
+  echo "cloud_relay: SKIPPED #$1 handoff/$2 ${3:0:12}: $4; the next pass retries" >&2
+  level_line handoff-skipped "refs/heads/handoff/$2" "$3" "#$1 $4" >> "$state/cloud-level-skip.$$"; }
 open_prs() { # the open PRs, `<number> <head ref> <head sha>` tab-separated: HPO_RELAY_PRS or gh
   if [ -n "${HPO_RELAY_PRS:-}" ]; then "$HPO_RELAY_PRS"
   else gh pr list -R "${HPO_RELAY_REPO:-tvofi/heatpump_optimizer}" --state open --limit 100 --json number,headRefName,headRefOid \
@@ -589,19 +603,20 @@ handoff_level() { # the handoff-no-pr and hold-stale levels, derived from this p
     grep -qxF "$l" <<< "$(cut -f1 "$state/cloud-prs.$$")" || level_line handoff-hold-stale "$(hold_file)" "#$l" "PR #$l is not open; remove the line" >> "$state/cloud-level-holdstale.$$"
   done
   level_set handoff-hold-stale "$state/cloud-level-holdstale.$$"
-  cut -f2 "$state/cloud-prs.$$" | sed -e 's,^fix/,,' -e 's,-pr$,,' > "$state/cloud-topics.$$"
+  # shellcheck disable=SC2046 # one word per branch name: a head ref holds no whitespace
+  python3 -I "$HERE/topic_grammar.py" handoff-topics $(cut -f2 "$state/cloud-prs.$$") > "$state/cloud-topics.$$"
   { if [ -n "${HPO_RELAY_MERGED:-}" ]; then "$HPO_RELAY_MERGED"
     else gh pr list -R "$repo" --state merged --limit 200 --json headRefName,mergedAt \
       -q '.[] | [.headRefName, .mergedAt] | @tsv'; fi; } > "$state/cloud-merged.$$" \
     || { echo "cloud_relay: could not list merged PRs; the handoff level stays as it was" >&2; return 0; }
-  awk -F'\t' 'NF == 2 { t = $1; sub(/^fix\//, "", t); sub(/-pr$/, "", t); print t " merged=" $2 }' "$state/cloud-merged.$$" >> "$state/cloud-topics.$$"
+  awk -F'\t' 'NF == 2 && sub(/^fix\//, "", $1) { print $1 " merged=" $2; if (sub(/-pr$/, "", $1) && $1 != "") print $1 " merged=" $2 }' "$state/cloud-merged.$$" >> "$state/cloud-topics.$$"
   ledger level "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" > "$state/cloud-level-handoff.$$"
   case $? in 0|1) level_set handoff-no-pr "$state/cloud-level-handoff.$$";;
     *) echo "cloud_relay: the ledger could not derive the handoff level; it stays as it was" >&2; rm -f "$state/cloud-level-handoff.$$";; esac
 }
 handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of its head
   local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} repo=${HPO_RELAY_REPO:-tvofi/heatpump_optimizer} f pr br head topic hs bs bd body iss nh nonce urc held_prs released upd why code
-  local bf bonly key seed="" tries n cls
+  local bf bonly key seed="" tries n cls ht
   f=$state/cloud-handoff-failed; mkdir -p "$state"
   # BODY-ONLY (R10-FLOW-BODY-ONLY part (c)): `<topic> <body sha>` per body this relay has applied, by an
   # update or a body-only run. With no file yet, this pass records every contained topic's body as
@@ -620,23 +635,37 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
   # one listing of the verdicts per pass, outside the loop: an unread listing would update a merge-verdicted head
   git ls-remote origin 'refs/heads/verdict/*' > "$state/cloud-vrefs.$$" \
     || { echo "cloud_relay: could not list verdict refs; will retry" >&2; rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-vrefs.$$"; return 0; }
-  : > "$state/cloud-level-update.$$"; : > "$state/cloud-level-held.$$"; : > "$state/cloud-level-stale.$$"; : > "$state/cloud-level-bodyonly.$$"
+  : > "$state/cloud-level-update.$$"; : > "$state/cloud-level-held.$$"; : > "$state/cloud-level-stale.$$"; : > "$state/cloud-level-bodyonly.$$"; : > "$state/cloud-level-skip.$$"
   handoff_level
   while IFS=$'\t' read -r pr br head; do
     [ -n "$pr" ] || continue
-    topic=$(python3 -I "$HERE/topic_grammar.py" pr-topic "$br")
-    hs=$(awk -v r="refs/heads/handoff/$topic" '$2 == r { print $1; exit }' "$state/cloud-hrefs.$$")
+    # The topic grammar's handoff topics, the first with a handoff ref deciding (review_packet.py's read):
+    # `fix/<t>-pr` is <t>-pr, then <t>. Reading <t> alone skipped #3358 for hours behind
+    # handoff/r10-combi-tank-pr, its handoff/r10-combi-tank an older tip already in the head.
+    topic= hs=
+    for ht in $(python3 -I "$HERE/topic_grammar.py" handoff-topics "$br"); do  # mut:handofftopics
+      hs=$(awk -v r="refs/heads/handoff/$ht" '$2 == r { print $1; exit }' "$state/cloud-hrefs.$$"); [ -z "$hs" ] || { topic=$ht; break; }
+    done
+    [ -n "$hs" ] || continue  # no handoff ref: nothing to apply, so nothing owed
     bs=$(awk -v r="refs/heads/handoff-body/$topic" '$2 == r { print $1; exit }' "$state/cloud-hrefs.$$")
-    [ -n "$hs" ] && [ -n "$bs" ] || continue
     git fetch -q origin "refs/heads/handoff/$topic" "refs/heads/$br" 2>/dev/null
-    git cat-file -e "$hs^{commit}" 2>/dev/null && git cat-file -e "$head^{commit}" 2>/dev/null || continue
+    git cat-file -e "$hs^{commit}" 2>/dev/null && git cat-file -e "$head^{commit}" 2>/dev/null \
+      || { skip_owed "$pr" "$topic" "$hs" "handoff/$topic or the head ${head:0:12} could not be fetched"; continue; }  # mut:skipunread
     # A head holding the handoff tip has its code; only a body this relay has not applied moves it,
     # and that move is body-only: update_pr.sh with code `-`, which PATCHes the body and pushes nothing.
+    # From here every skip of a handoff the head lacks is owed on the level, never silent (#3358).
     bonly=""; if git merge-base --is-ancestor "$hs" "$head"; then
+      [ -n "$bs" ] || continue
       grep -qxF "$topic $bs" "$bf" && continue
       [ -z "$seed" ] || { echo "$topic $bs" >> "$bf"; continue; }
-      bonly=1; fi
-    if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"; [ -z "$bonly" ] || body_only_owed "$pr" "$topic" "$bs" "$head" "held by the hold file" || :; continue; fi
+      bonly=1
+    elif [ -z "$bs" ]; then  # code pushed ahead of its body: partial work, as HELD-BODY below
+      echo "cloud_relay: HELD-NOBODY #$pr ${hs:0:8}"
+      level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr NOBODY" >> "$state/cloud-level-held.$$"; continue  # mut:nobody
+    fi
+    if grep -qxF "$pr" <<< "$held_prs"; then echo "cloud_relay: HELD #$pr $hs"  # the hold file's skip is owed on the level too (#3358)
+      if [ -n "$bonly" ]; then body_only_owed "$pr" "$topic" "$bs" "$head" "held by the hold file" || :
+      else level_line handoff-held "refs/heads/handoff/$topic" "$hs" "#$pr HOLD" >> "$state/cloud-level-held.$$"; fi; continue; fi  # mut:holdowed
     # a body-only move leaves the head under review where it is, so no review freezes it
     if [ -z "$bonly" ] && ! grep -qxF "$pr" <<< "$released" && why=$(review_freeze "$pr" "$head" "$state/cloud-vrefs.$$"); then
       echo "cloud_relay: HELD-${why%% *} #$pr $hs${why#"${why%% *}"} (head $head under review; merge it, or list #$pr in $(release_file) and re-dispatch)"
@@ -654,10 +683,10 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     # The body goes in a directory of this run's own, under the state dir: a file directly in a
     # shared temp root ($TMPDIR, /tmp) is refused by prepr's body-path check, so every relay
     # update failed there (#2469, #2471) -- and still raced the manual update it was meant to spare.
-    bd=$(mktemp -d "$state/cloud-body.XXXXXX") || { echo "cloud_relay: no body directory under $state" >&2; continue; }
+    bd=$(mktemp -d "$state/cloud-body.XXXXXX") || { skip_owed "$pr" "$topic" "$hs" "no body directory under $state"; continue; }
     body=$bd/BODY.md
     git fetch -q origin "refs/heads/handoff-body/$topic" 2>/dev/null \
-      && git show "$bs:BODY.md" > "$body" 2>/dev/null || { echo "cloud_relay: no BODY.md at handoff-body/$topic" >&2; rm -rf "$bd"; continue; }
+      && git show "$bs:BODY.md" > "$body" 2>/dev/null || { skip_owed "$pr" "$topic" "$hs" "no BODY.md at handoff-body/$topic ${bs:0:12}"; rm -rf "$bd"; continue; }
     # A body names the code head it was pushed for (body_push.sh's `Code:` trailer, V147). One
     # naming another head describes a tree the PR would not carry, so it waits, owed and unrecorded,
     # until the body for this head lands. A body with no `Code:` line predates the trailer: as before.
@@ -692,8 +721,9 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     if [ -z "${HPO_RELAY_UPDATE:-}" ]; then
       why=$(tools_level "$state"); urc=$?
       if [ "$urc" != 0 ]; then
-        echo "cloud_relay: REFUSED the update of #$pr: $why; the next pass retries" >&2
-        [ "$urc" = 75 ] || level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"
+        if [ "$urc" = 75 ]; then skip_owed "$pr" "$topic" "$hs" "BUSY: $why"  # mut:skiptools
+        else echo "cloud_relay: REFUSED the update of #$pr: $why; the next pass retries" >&2
+          level_line handoff-update "refs/heads/handoff/$topic" "$hs" "$why" >> "$state/cloud-level-update.$$"; fi
         rm -rf "$bd"; continue
       fi
       upd=(bash "$why/update_pr.sh")  # mut:toolsseat
@@ -706,7 +736,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
     cat "$bd/update.out" >&2
     # 75 is update_pr.sh's BUSY: another run (the orchestrator's) holds this branch's worktree. Not
     # a failure, so it is not recorded and the next pass retries once that run has ended.
-    if [ "$urc" = 75 ]; then echo "cloud_relay: update_pr busy on $br; the next pass retries" >&2; rm -rf "$bd"; continue; fi
+    if [ "$urc" = 75 ]; then skip_owed "$pr" "$topic" "$hs" "BUSY: update_pr: $(last_line "$(cat "$bd/update.out")")"; rm -rf "$bd"; continue; fi  # mut:skipbusy
     if [ "$urc" != 0 ]; then
       why=$(grep REFUSE "$bd/update.out" | tail -n 1); [ -n "$why" ] || why=$(last_line "$(cat "$bd/update.out")")
       # A refusal of a body-content step (unpinned sites, carry, figures, the body contract) clears only when the body
@@ -738,6 +768,7 @@ handoff_arm() { # one pass over open PRs; updates one whose handoff is ahead of
   level_set handoff-held "$state/cloud-level-held.$$"
   level_set handoff-body-stale "$state/cloud-level-stale.$$"
   level_set handoff-body-unapplied "$state/cloud-level-bodyonly.$$"
+  level_set handoff-skipped "$state/cloud-level-skip.$$"
   rm -f "$state/cloud-prs.$$" "$state/cloud-hrefs.$$" "$state/cloud-topics.$$" "$state/cloud-vrefs.$$" "$state/cloud-merged.$$"
 }
 
@@ -857,6 +888,34 @@ noreturn_arm() {
   rm -f "$state/cloud-nr.$$" "$state/cloud-nrr.$$"
 }
 
+# OWED RED TEXT (R10-RELAY-NOBODY-STALL carry 5, OWED-RED-TEXT-TO-CLOUD). A cloud seat has no gh, so when body_push.sh
+# refuses on the predictor over a check whose red is owed an answer (the set `merge_train.py owed-reds` prints), the
+# seat cannot read that check's failure; hotfix #3487 waited 45 min for a local seat. The relay, which has gh, reads
+# each owed check the BLOCKED.md's PREDICT lines name at the topic's open PR head (failure_logs.sh: name, conclusion,
+# error lines) into <state>/cloud-owed-red-<topic>.md, named on the carry-fold line the orchestrator's next message to
+# the seat carries. A refusal naming no owed red, or a topic with no open PR, adds no text. HPO_RELAY_OWED and
+# HPO_RELAY_FAILLOGS replace the two readers (the self-test's stubs).
+owed_red_text() { # <topic> <BLOCKED.md text>: prints `owed red text ... <file>`, or nothing
+  local owed name names= pr f d prs=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-prs-open.$$
+  if owed=$(${HPO_RELAY_OWED:-python3 -I "$HERE/merge_train.py" owed-reds} 2>/dev/null); then
+    while IFS= read -r name; do
+      [ -n "$name" ] && grep -qF "PREDICT $name " <<< "$2" && names+="$name"$'\n'
+    done <<< "$owed"
+    [ -n "$names" ] || return 0  # mut:owednone
+  else names=-; fi  # an unreadable set owes every red (defect-root-cause.md): each failing check at the head is read
+  pr=$( { [ -f "$prs" ] && cat "$prs" || open_prs; } 2>/dev/null | awk -F'\t' -v a="fix/$1" -v b="fix/$1-pr" '$2 == a || $2 == b { print $1; exit }')
+  [ -n "$pr" ] || return 0
+  d=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/failure-logs/$pr; f=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/cloud-owed-red-$1.md; mkdir -p "$d"
+  ${HPO_RELAY_FAILLOGS:-bash "$HERE/failure_logs.sh"} "$pr" "$d" > "$d.out" 2>&1
+  [ "$names" != - ] || names=$(cut -f1 "$d/failing.tsv" 2>/dev/null)
+  { echo "Owed red check(s) of #$pr for $1, read by cloud_relay.sh at $(sed -n 's/^head //p' "$d.out" | head -n 1) (the seat has no gh):"
+    while IFS= read -r name; do
+      [ -n "$name" ] || continue
+      awk -F'\t' -v n="$name" '$1 == n { c = $2 } END { print "- " n ": " (c == "" ? "no failing run at the head" : c) }' "$d/failing.tsv" 2>/dev/null
+      awk -v n="$name" 'index($0, n "\t") == 1 { f = 1; next } /^[^ ]/ { f = 0 } f' "$d.out"
+    done <<< "$names"; } > "$f"
+  echo "owed red text for the seat's next message: $f"
+}
 fold_judge() { # <memo> <level> <topic> <wip sha> <body sha> <outcome> <epoch> <BODY.md blob|-> <handoff tip|-> [<OWED level line>]: one judged topic, its level line set
   printf '%s %s %s %s %s %s %s%s\n' "$3" "$4" "${5:--}" "$6" "$7" "$8" "$9" "${10:+ ${10}}" >> "$1"; [ -z "${10:-}" ] || printf '%s\n' "${10}" >> "$2"; }
 fold_memo_stands() { # <outcome> <epoch> <now>: rc 0 while a judged outcome stands; a failure after the fold expires after 3600 s
@@ -875,7 +934,7 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
   # again once fold_memo_stands expires it: an ancestry red can clear with no ref moving. The body is pushed from a
   # worktree at a private ref fetched from handoff/<topic>, deleted after the push, never FETCH_HEAD, which a concurrent
   # fetch in this checkout overwrites, and only at that ref's ls-remote tip (P556).
-  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head mb mh blob fo fe fb fh fl
+  local state=${HPO_STATE_DIR:-$HOME/.local/state/hpo} sha ref topic bw bsha kinds wt body why rc memo now mo me ml htip head mb mh blob fo fe fb fh fl rt
   git ls-remote origin 'refs/heads/handoff-wip/*' 'refs/heads/handoff/*' > "$state/cloud-wip.$$" \
     || { echo "cloud_relay: could not list handoff-wip refs; the carry-fold level stays as it was" >&2; rm -f "$state/cloud-wip.$$"; return 0; }
   memo=$state/cloud-fold-judged; now=$(date +%s)
@@ -905,6 +964,7 @@ carry_fold_arm() { # one pass over handoff-wip/<topic> refs whose BLOCKED.md nam
     kinds=$(printf '%s\n' "$bw" | sed -n 's/^body_push: REFUSED \([A-Z-]*\)[[:space:]]*$/\1/p' | sort -u | tr '\n' ' ')
     if [ "$kinds" != "CARRY-LANDED " ] || [ -z "$bsha" ]; then  # mut:foldonly
       why="BLOCKED.md names ${kinds:-no refusal line}${bsha:+; }${bsha:-and no kept body}: not CARRY-LANDED alone, nothing folded"
+      case " $kinds" in *" PREDICTOR "*) rt=$(owed_red_text "$topic" "$bw") && [ -n "$rt" ] && why="$why; $rt";; esac  # mut:owedred
       echo "cloud_relay: OWED carry-fold $topic ${sha:0:12} $why"
       fold_judge "$memo.$$" "$state/cloud-level-fold.$$" "$topic" "$sha" "$bsha" blocked "$now" - "${htip:--}" "$(level_line carry-fold "$ref" "$sha" "$why")"; continue
     fi
@@ -1364,6 +1424,7 @@ EOF
   hc ahead; mkref handoff/topic-a; HS=$(git -C "$t/pr" rev-parse HEAD)
   handoff_arm >/dev/null 2>&1
   chk "a handoff with no body ref does nothing" 0 test ! -e "$t/updated"
+  chk "and is owed HELD-NOBODY on the level, never skipped in silence (#3358)" 0 grep -q "^OWED .* handoff-held refs/heads/handoff/topic-a $HS #41 NOBODY\$" "$LOG.level"
   # a handoff ahead of its PR fires the arm
   rm -rf "$t/b"; throwaway_git_init "$t/b" -q; printf 'Part of #201\n\nCloses #77 and fixes #78.\n' > "$t/b/BODY.md"
   git -C "$t/b" add BODY.md; git -C "$t/b" -c user.name=t -c user.email=t@t commit -qm body; mkref2() { # the body names the handoff tip it is pushed against (HELD-BODY otherwise)
@@ -1388,6 +1449,18 @@ EOF
   printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$NEW" > "$prs"; rm -f "$t/updated"
   handoff_arm >/dev/null 2>&1
   chk "a handoff already merged into its PR does nothing (null control)" 0 test ! -e "$t/updated"
+  # #3358's shape (R11-PRE-RELAY-REBUILD carry 0): handoff/topic-a is an older tip the head holds, its body applied, and the
+  # repair returned under handoff/topic-a-pr, fix/<t>-pr's other spelling; the arm reading <t> alone skipped it in silence.
+  hc repair; git -C "$t/o.git" fetch -qf "$t/pr" "HEAD:refs/heads/handoff/topic-a-pr"; HP=$(git -C "$t/pr" rev-parse HEAD)
+  rm -rf "$t/bp"; throwaway_git_init "$t/bp" -q; printf 'Closes #79\n\nCode head: %s\n' "$HP" > "$t/bp/BODY.md"; git -C "$t/bp" add BODY.md
+  git -C "$t/bp" -c user.name=t -c user.email=t@t commit -qm body; git -C "$t/o.git" fetch -qf "$t/bp" "HEAD:refs/heads/handoff-body/topic-a-pr"
+  rm -f "$t/updated"; handoff_arm >/dev/null 2>&1
+  chk "#3358's shape: fix/<t>-pr behind handoff/<t>-pr, handoff/<t> an older tip in its head, runs update_pr at handoff/<t>-pr" 0 grep -q "^fix/topic-a-pr $HP " "$t/updated"
+  git -C "$t/pr" reset -q --hard "$HP"; mkref fix/topic-a-pr; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$HP" > "$prs"; rm -f "$t/updated"; ho=$(handoff_arm 2>&1)
+  chk "#3358's null control: a head holding handoff/<t>-pr has neither an update nor a level line nor a skip line" 0 \
+    test ! -e "$t/updated" -a -z "$(grep -s topic-a "$LOG.level")" -a -z "$(grep 'SKIPPED\|HELD' <<< "$ho")"
+  git -C "$t/o.git" update-ref -d refs/heads/handoff/topic-a-pr; git -C "$t/o.git" update-ref -d refs/heads/handoff-body/topic-a-pr
+  git -C "$t/pr" reset -q --hard "$NEW"; mkref fix/topic-a-pr; printf '%s\t%s\t%s\n' 41 fix/topic-a-pr "$NEW" > "$prs"
   # the hold file: a listed PR is skipped with one HELD line per pass; a malformed file refuses the pass
   hf=$t/state/cloud-handoff-hold; hu=$t/hu.sh; printf '#!/bin/sh\necho "$1 $2${HPO_UPDATE_BODY_ONLY:+ body-only}" >> "%s/hupdated"\n' "$t" > "$hu"; chmod +x "$hu"; HPO_RELAY_UPDATE=$hu
   printf '41\n' > "$hf"; ho=$(handoff_arm 2>&1)
@@ -1398,6 +1471,7 @@ EOF
   chk "a held PR whose handoff is ahead is not updated" 0 test ! -e "$t/hupdated"
   chk "and prints HELD with the handoff tip it did not apply" 0 grep -q "HELD #41 $HS\$" <<< "$ho"
   chk "the HELD line is printed once per pass" 0 test "$(grep -c '^cloud_relay: HELD ' <<< "$ho")" = 1
+  chk "and owes handoff-held HOLD on the level, never skipped in silence (#3358)" 0 grep -q "^OWED .* handoff-held refs/heads/handoff/topic-a $HS #41 HOLD\$" "$LOG.level"
   chk "and the held pass dispatches no reviewer" 1 owes "reviewer-fire"
   hc held-moved; mkref handoff/topic-a; HS2=$(git -C "$t/pr" rev-parse HEAD)
   ho=$(handoff_arm 2>&1)
@@ -1487,9 +1561,21 @@ EOF
   printf '41 %s cloud %s 2026-10-29T17:07:00Z -\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
   chk "a dispatch at the head with no verdict holds the handoff: no update_pr call" 0 test ! -e "$t/hupdated"
   chk "and prints HELD-REVIEW naming the dispatch's nonce prefix and time (P288)" 0 \
-    grep -q "^cloud_relay: HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=2026-10-29T17:07:00Z (" <<< "$ho"
-  chk "and owes handoff-held REVIEW with that evidence in the level" 0 \
-    grep -q "^OWED .* handoff-held refs/heads/handoff/topic-a $HS2 #41 REVIEW dispatch=${n:0:8} at=2026-10-29T17:07:00Z\$" "$LOG.level"
+    grep -q "^cloud_relay: HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=2026-10-29T17:07:00Z probe=none (in flight) (" <<< "$ho"
+  chk "and owes handoff-held REVIEW with that evidence in the level, naming no probe ref (in flight)" 0 \
+    grep -q "^OWED .* handoff-held refs/heads/handoff/topic-a $HS2 #41 REVIEW dispatch=${n:0:8} at=2026-10-29T17:07:00Z probe=none (in flight)\$" "$LOG.level"
+  # R10-RELAY-NOBODY-STALL carry 2: the dispatch's verdict returned and refused or disposed by the relay releases the hold
+  pv=refs/heads/probe/rev-41-${n:0:8}; git -C "$t/o.git" update-ref "$pv" "$(git -C "$t/o.git" rev-parse refs/heads/main)"; pvs=$(git -C "$t/o.git" rev-parse "$pv"); frz
+  chk "a returned verdict neither relayed, refused nor disposed still holds, and the level names the probe's state" 0 \
+    grep -qF "handoff-held refs/heads/handoff/topic-a $HS2 #41 REVIEW dispatch=${n:0:8} at=2026-10-29T17:07:00Z probe=${pvs:0:8} held by the relay (dispose it to release)" "$LOG.level"
+  echo "$pv $pvs" >> "$t/state/cloud-relayed.refused"; frz
+  chk "the dispatch's verdict refused by the relay releases HELD-REVIEW: update_pr runs" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
+  chk "and says RELEASED-REVIEW naming the dispatch" 0 grep -q "^cloud_relay: RELEASED-REVIEW #41: dispatch ${n:0:8}'s verdict ${pvs:0:12} was refused or disposed" <<< "$ho"
+  grep -vxF "$pv $pvs" "$t/state/cloud-relayed.refused" > "$t/rf.tmp"; mv -f "$t/rf.tmp" "$t/state/cloud-relayed.refused"; frz
+  chk "null control: the same probe no longer refused holds again" 0 test ! -e "$t/hupdated"
+  dispose "$pv" "$pvs" >/dev/null 2>&1; frz
+  chk "the dispatch's verdict disposed releases HELD-REVIEW too" 0 grep -q "^fix/topic-a-pr $HS2\$" "$t/hupdated"
+  git -C "$t/o.git" update-ref -d "$pv"
   mkv "verdict: #41 Fix review: merge $h"; frz
   chk "a verdict at an older head does not dispose the review: still HELD-REVIEW" 0 grep -q "HELD-REVIEW #41 " <<< "$ho"
   mkv "verdict: #41 Fix review: blocked $PRH carry-missing: x"; frz
@@ -1510,7 +1596,7 @@ EOF
   chk "and prints no HELD-REVIEW" 1 grep -q "HELD-REVIEW #41 " <<< "$ho"
   printf '41 %s cloud %s\n' "$PRH" "$n" >> "$t/bus/dispatched"; frz
   chk "the same with a dispatch record at the head holds (a record without a time says at=-)" 0 \
-    grep -q "HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=- (" <<< "$ho"
+    grep -q "HELD-REVIEW #41 $HS2 dispatch=${n:0:8} at=- probe=none (in flight) (" <<< "$ho"
   cp "$t/bus/dispatched.keep" "$t/bus/dispatched"
   git worktree remove --force "$t/rw"
   # the release: the orchestrator passes the freeze over a listed PR; the hold file outranks it
@@ -1554,8 +1640,10 @@ EOF
   chk "and not noted as a failed update" 0 test -z "$(grep -s "topic-a $HS2" "$t/state/cloud-handoff-failed")"
   git -C "$TW" checkout -q -- .; sleep 30 & lp=$!; mkdir "$TW.lock"; echo "$lp" > "$TW.lock/pid"
   ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
-  chk "a tools tree held by a live relay is busy: no update, no level line" 0 \
+  chk "a tools tree held by a live relay is busy: no update" 0 \
     test -n "$(grep "is busy (pid $lp)" <<< "$ho")" -a ! -e "$t/tupdated"
+  chk "and owed handoff-skipped BUSY on the level, never skipped in silence (#3358)" 0 \
+    grep -q "^OWED .* handoff-skipped refs/heads/handoff/topic-a $HS2 #41 BUSY: the relay's tools tree .* is busy (pid $lp)\$" "$LOG.level"
   kill "$lp"; wait "$lp" 2>/dev/null
   ho=$(HPO_RELAY_UPDATE= handoff_arm 2>&1)
   chk "a lock whose pid is dead is taken over and the update runs" 0 test "$(cat "$t/tupdated" 2>/dev/null)" = "$TB fix/topic-a-pr $HS2"
@@ -1575,7 +1663,9 @@ EOF
   handoff_arm >/dev/null 2>&1; handoff_arm >/dev/null 2>&1
   chk "a busy update is tried again on the next pass" 0 test "$(wc -l < "$t/updated" | tr -d ' ')" = 2
   chk "and is not recorded failed" 0 test ! -s "$t/state/cloud-handoff-failed"
-  chk "nor owed" 1 grep -q "handoff-update" "$LOG.level"
+  chk "nor owed as a failed update" 1 grep -q "handoff-update" "$LOG.level"
+  chk "but owed handoff-skipped BUSY on the level, once, never skipped in silence (#3358)" 0 \
+    test "$(grep -c "^OWED .* handoff-skipped refs/heads/handoff/topic-a $HS2 #41 BUSY: update_pr: (no output)\$" "$LOG.level")" = 1
   bodyc() { git -C "$t/b" -c user.name=t -c user.email=t@t commit -q --allow-empty -m body ${1:+-m "Code: $1"}; mkref2; }
   # Carry 12: a refusal that clears with no ref moving is rerun after a backoff, three runs at most; a body-content refusal waits for the body.
   rt=$t/rt.sh; printf '#!/bin/sh\nn=$(cat "%s/rtn" 2>/dev/null || echo 0); echo $((n + 1)) > "%s/rtn"\ncase "$RT_MODE" in\n prepr) echo "  REFUSE   ci predict            r"; echo "  skip     unpinned sites        the diff adds no unpinned mutation site"; exit 1;;\n ok1) [ "$n" = 0 ] && { echo "update_pr: REFUSE: ancestry reds: r"; exit 1; }; exit 0;;\n *) echo "update_pr: REFUSE: $RT_MODE: r"; exit 1;;\nesac\n' "$t" "$t" > "$rt"; chmod +x "$rt"; HPO_RELAY_UPDATE=$rt
@@ -2143,6 +2233,21 @@ open(sys.argv[1], "w").close(); time.sleep(60)' "$t/stuck.held" "$t/state/pr/upd
   awk '$1 == "cf-l" { $6 = ""; $7 = ""; gsub(/  +/, " ") } 1' "$t/state/cloud-fold-judged" > "$t/memo" && mv "$t/memo" "$t/state/cloud-fold-judged"
   : > "$t/fetches"; cfo=$(git() { [ "$1" != fetch ] || echo "$*" >> "$t/fetches"; command git "$@"; }; carry_fold_arm 2>&1)
   chk "a memo record from before the blob and tip fields is judged again, not read with shifted fields" 0 grep -q "handoff-wip/cf-l\$" "$t/fetches"
+  # OWED-RED-TEXT-TO-CLOUD: a PREDICTOR refusal naming an owed red attaches that check's name, conclusion and error lines
+  printf '#!/bin/sh\nprintf "tests / fast (3.14)\\npr-contract / pr-contract\\n"\n' > "$t/owedstub"
+  printf '#!/bin/bash\necho "$1 $2" >> %s/fl.calls; printf "tests / fast (3.14)\\tfailure\\t9\\tu\\n" > "$2/failing.tsv"\necho "head %s"; printf "tests / fast (3.14)\\t9\\t8\\tf.log\\n    12:FAILED test_x\\n"; echo "failing checks: 1"\n' "$t" "$h" > "$t/flstub"
+  printf '#!/bin/sh\nprintf "77\\tfix/cf-m-pr\\t%s\\n78\\tfix/cf-n\\t%s\\n"\n' "$h" "$h" > "$t/oprs"
+  chmod +x "$t/owedstub" "$t/flstub" "$t/oprs"; export HPO_RELAY_OWED=$t/owedstub HPO_RELAY_FAILLOGS=$t/flstub
+  cfref handoff-wip/cf-m BLOCKED.md "$(printf 'PREDICT tests / fast (3.14) the self-test fails\nbody_push: REFUSED PREDICTOR')"; cfo=$(HPO_RELAY_PRS=$t/oprs carry_fold_arm 2>&1)
+  chk "a PREDICTOR refusal naming an owed red: the carry-fold level line names the owed red text for the seat's next message" 0 \
+    grep -qF "carry-fold refs/heads/handoff-wip/cf-m $(cftip handoff-wip/cf-m) BLOCKED.md names PREDICTOR and no kept body: not CARRY-LANDED alone, nothing folded; owed red text for the seat's next message: $t/state/cloud-owed-red-cf-m.md" "$LOG.level"
+  chk "... which carries the check's name, conclusion and error lines, read at PR #77's head" 0 test "$(sed -n '1p;2p;3p' "$t/state/cloud-owed-red-cf-m.md")" = "Owed red check(s) of #77 for cf-m, read by cloud_relay.sh at $h (the seat has no gh):
+- tests / fast (3.14): failure
+    12:FAILED test_x"
+  cfref handoff-wip/cf-n BLOCKED.md "$(printf 'PREDICT nightly-status the lane is red\nbody_push: REFUSED PREDICTOR')"; rm -f "$t/fl.calls"; cfo=$(HPO_RELAY_PRS=$t/oprs carry_fold_arm 2>&1)
+  chk "null control: a PREDICTOR refusal naming no owed red adds no text and reads no check" 0 \
+    test -z "$(grep 'cf-n.*owed red text' "$LOG.level")" -a ! -e "$t/state/cloud-owed-red-cf-n.md" -a ! -e "$t/fl.calls" -a -n "$(grep 'carry-fold refs/heads/handoff-wip/cf-n' "$LOG.level")"
+  unset HPO_RELAY_OWED HPO_RELAY_FAILLOGS
   unset HPO_RELAY_FOLD HPO_RELAY_BODYPUSH; cd "$t/w" || exit 1
   cd / && rm -rf "$t"
   echo "cloud_relay self-test: $((ok+bad)) checks, $bad failed"; [ "$bad" = 0 ]
diff --git a/tools/audit/seat/instruments/check_scopes.py.md b/tools/audit/seat/instruments/check_scopes.py.md
index 79bfbcadc7..a706e8f449 100644
--- a/tools/audit/seat/instruments/check_scopes.py.md
+++ b/tools/audit/seat/instruments/check_scopes.py.md
@@ -8,3 +8,7 @@
   over its `ledger.max_units` of `text_ledger.py` units, a D6 document or a
   D5 comment carrier (a suffix `text_ledger.D5_SUFFIXES` reads) neither
   measured nor named `static`, and a ledger dimension drawing no `classify`.
+  `--round N` adds decision 0018's start evaluation: an accepted card holds
+  the start only if its `gates_finders` is true; one that gates no finder and
+  is unmerged prints `PARALLEL <card>`. `--round N --open-cards` prints those
+  still open at `--ref` as JSON: P3's input (`architect-planner.md`).
diff --git a/tools/audit/seat/instruments/cloud_relay.sh.md b/tools/audit/seat/instruments/cloud_relay.sh.md
index ffb7370e63..b6ad9f0e9c 100644
--- a/tools/audit/seat/instruments/cloud_relay.sh.md
+++ b/tools/audit/seat/instruments/cloud_relay.sh.md
@@ -82,8 +82,11 @@
   with no dispatch for its PR, head and nonce is owed `undispatched` and never
   confirmed; a tip the relay did not push waits for the orchestrator's own
   read. It makes no `gh` call (`bus.sh confirm` posts).
-  Handoff arm: for each OPEN pull request, topic = `headRefName` less `fix/` and
-  `-pr`; if `handoff-body/<topic>` and `handoff/<topic>` exist and the handoff is
+  Handoff arm: for each OPEN pull request, topic = the first of
+  `topic_grammar.py handoff-topics <headRefName>` with a `handoff/` ref
+  (`fix/<t>-pr` is `<t>-pr`, then `<t>`: review_packet.py's read, so #3358's
+  `handoff/r10-combi-tank-pr` is not left behind an older `handoff/r10-combi-tank`);
+  if `handoff-body/<topic>` and `handoff/<topic>` exist and the handoff is
   not an ancestor of the PR head, it runs `update_pr.sh <branch> <code-sha>
   <BODY.md> <issues>` (issues = the body's closing keywords; BODY.md is written
   to a per-run `cloud-body.*` directory under the state dir and removed after,
@@ -107,7 +110,13 @@
   own checkout is (never moved: bash reads a running script as it goes). A
   dirty tree is refused by name, left untouched and owed as `handoff-update`;
   one held by a live relay (`relay-tools.lock`, a dead pid's taken over) is
-  busy and retried next pass.
+  busy, owed `handoff-skipped` for the pass, and retried next pass.
+  No skip of a handoff the head lacks is silent (#3358): a hold-file skip is
+  `handoff-held ... #<pr> HOLD`; no body ref is
+  `HELD-NOBODY` (`handoff-held ... #<pr> NOBODY`); an unreadable ref or head,
+  a busy tools tree, a BUSY update or an unreadable body is
+  `OWED <utc> handoff-skipped <ref> <tip> #<pr> <why>` in `<log>.level`, rewritten
+  every pass. A head holding its handoff is owed nothing.
   Freeze (R10-FLOW-ROSTER-FREEZE): a PR whose live head is under review is not
   updated either, so roster edits accumulate on the handoff ref and land between
   reviews: a `Fix review: merge <head>` tip on `verdict/<pr>` at that head
@@ -116,7 +125,12 @@
   registry and only it, P288; its nonce prefix and time are printed as
   `dispatch=<nonce8> at=<utc>`). A verdict ref the listing names but the fetch
   cannot read freezes too (`HELD-UNREAD`): it may be a merge at the head. A
-  blocked verdict, or one at an older head, freezes nothing. Each prints
+  blocked verdict, or one at an older head, freezes nothing. A review whose
+  verdict came back (`probe/rev-<pr>-<nonce8>`) and that the relay refused
+  (`cloud-relayed.refused`) or `dispose` took is over: `RELEASED-REVIEW`, and
+  the update runs. Else the HELD-REVIEW line names the probe's state:
+  `probe=none (in flight)`, `probe=<sha8> relayed, not yet on verdict/<pr>`, or
+  `probe=<sha8> held by the relay (dispose it to release)`. Each prints
   `HELD-<why> #<pr> <handoff tip>[ dispatch=<nonce8> at=<utc>]` once per pass and is
   `OWED <utc> handoff-held <ref> <tip> #<pr> <why>` in `<log>.level`;
   `cloud-handoff-release` (the hold file's grammar) releases a listed PR from the
@@ -153,7 +167,8 @@
   relay's stderr. An update that
   exits 75 is BUSY (another `open_pr.sh` or `update_pr.sh` run holds the branch's
   `upd-<branch>.lock`, typically the orchestrator's own update of that PR, or an `open_pr.sh` between its two pushes): it is
-  not recorded, and the next pass retries it. The update runs in a process
+  not recorded, is owed `handoff-skipped ... BUSY: update_pr: <last line>` for
+  that pass, and the next pass retries it. The update runs in a process
   group of its own, so a signal to the loop's whole group reaches it only
   through the loop's reap, and a KILL to that group leaves it to finish. The
   `handoff-no-pr` lines in `<log>.level` are `ledger.py level`'s fold of
@@ -197,3 +212,12 @@
   `HELD-PENDING-CI` line, retried next pass), RED refuses it, and a PR head that moved since the
   draft refuses it naming both heads. `HPO_RELAY_CLASSIFY` replaces the command. A fired session
   with no return ref after the bounded window is `SEAT ENDED NO RETURN` (the no-return arm above).
+- Owed red text (OWED-RED-TEXT-TO-CLOUD): a cloud seat has no `gh`. When the
+  carry-fold arm reads a `handoff-wip/<topic>` BLOCKED.md naming
+  `body_push: REFUSED PREDICTOR` whose `PREDICT <check> ...` lines name a check
+  in `merge_train.py owed-reds` (an unreadable set: every failing check), it reads
+  that check at the topic's open PR head (`failure_logs.sh`: name, conclusion,
+  error lines) into `<state>/cloud-owed-red-<topic>.md` and names that file on the
+  `carry-fold` level line, for the orchestrator's next message to the seat. A
+  refusal naming no owed red, or a topic with no open PR, adds no text.
+  `HPO_RELAY_OWED` and `HPO_RELAY_FAILLOGS` replace the two readers.
diff --git a/tools/audit/seat/instruments/enumerate.py.md b/tools/audit/seat/instruments/enumerate.py.md
new file mode 100644
index 0000000000..8daec72343
--- /dev/null
+++ b/tools/audit/seat/instruments/enumerate.py.md
@@ -0,0 +1,17 @@
+# `enumerate.py`
+
+- `enumerate.py` — prints one audit universe, one item per line, so a finder
+  reports `universe=N examined=n` against a command and not a recollection.
+  Path: `tools/audit/enumerate.py`; its docstring lists every universe and
+  the rule each is read by. When: a dimension brief names it as a step's
+  universe (D0, D1, D2, D8, D9, D12, D15; `d3-sites`, `d14-classes`,
+  `d16-writes` and `d17-features` are ported for the briefs that will cite
+  them). Two universes are registers a round's register pull request
+  appends to: `dev/audit/config/identities.json` (D2) and
+  `dev/audit/config/bundles.json` (D15). `--ledger TSV` joins a seat's
+  ledger to any universe, each line beside its asserting test or `not run`
+  (rows: item, test; `d12-cells`: cell, source, test), and refuses a row
+  that names no item, an unlisted source or no test. Refusal: exit 2 on a missing
+  source or an empty universe, never a pass. `--self-test` plants a fake
+  repo per universe, deletes one item and empties the source: the null
+  control.
diff --git a/tools/audit/seat/instruments/ledger.py.md b/tools/audit/seat/instruments/ledger.py.md
index 4d6473930b..f919a87545 100644
--- a/tools/audit/seat/instruments/ledger.py.md
+++ b/tools/audit/seat/instruments/ledger.py.md
@@ -5,7 +5,7 @@
   (`dispositions.tsv`, written only by `dispose`; `events.tsv`, append-only
   `open`/`close`/`attempt`) and one fold. Derived kinds are recomputed each pass
   (`level` derives `handoff-no-pr` for the relay; the tick derives
-  `design-build` and `review-owed`); event kinds are keyed on kind, subject and
+  `design-build`, `design-review` and `review-owed`); event kinds are keyed on kind, subject and
   sha, an open at a new sha superseding the old, and close by the producer's
   `close`, a moved or closed pull request, or the tick's read-back of the
   approver's comment (`verdict-unposted` only on its own first line: a relayed
diff --git a/tools/audit/seat/instruments/owed_unactioned.py.md b/tools/audit/seat/instruments/owed_unactioned.py.md
index 00dd970f97..ed68650d99 100644
--- a/tools/audit/seat/instruments/owed_unactioned.py.md
+++ b/tools/audit/seat/instruments/owed_unactioned.py.md
@@ -3,7 +3,7 @@
 - `owed_unactioned.py` — says which tick owed lines have outlived a sweep with
   no live acknowledgement (dev/audit/rca/R10-RCA-OWED-UNACTIONED.md). It reads
   the board's whole owed family (`-> OWED…`, `REVIEW OWED:`, `DISPATCH:`,
-  `OWNER FLAG:`, `DESIGN-BUILD:`, `MERGE-READY:`, `BLOCKED-UNFIXED:`, `APPROVAL-OWED:` (queue the PR for the train,
+  `OWNER FLAG:`, `DESIGN-BUILD:`, `DESIGN-REVIEW OWED:` (dispatch the design reviewer), `UNDISPATCHED:` (dispatch the group), `MERGE-READY:`, `BLOCKED-UNFIXED:`, `APPROVAL-OWED:` (queue the PR for the train,
   which posts the approval), `UNLEVELLED:` (read the state by hand), `REVIEW STALLED:` (re-fire the reviewer)), keys
   each line on its topic or `#<pr>` (a verdict level's head8 is its id, so a
   new head re-raises), and
diff --git a/tools/audit/seat/instruments/tick_loop.sh.md b/tools/audit/seat/instruments/tick_loop.sh.md
index 3a449c5398..8249503cd8 100644
--- a/tools/audit/seat/instruments/tick_loop.sh.md
+++ b/tools/audit/seat/instruments/tick_loop.sh.md
@@ -43,9 +43,17 @@
   and `behind`, the commits in `HEAD..origin/main` touching `tools/audit/seat`,
   `tools/pr` or `tools/audit/carry_audit.py`. Past `HPO_TICK_STALE_BOUND`
   (default 25) or on a commit touching `tick_loop.sh` or `cloud_relay.sh`, it
-  restarts between passes, at most once a pass: lock free, tree clean and
-  detached, `bash -n` passing on origin/main's copy, then a detached checkout
-  of origin/main and an exec with the same args (`TICK-RESTART`). Otherwise
+  restarts between passes, at most once a pass: lock free, tree clean,
+  `bash -n` passing on origin/main's copy, then a checkout of origin/main --
+  detached, or `checkout -B <branch> origin/main` for a branch-backed checkout
+  holding no commit outside origin/main -- and an exec with the same args
+  (`TICK-RESTART`). A branch with commits of its own is never moved. Otherwise
   a `TICK-STALE` line names why, the relay and sweep arms are skipped
-  (`relay=stale`) and the board is still written. Never a fast-forward in
-  place. `HPO_TICK_CODE_DIR` replaces the checkout.
+  (`relay=stale`) and the board is still written; from the second consecutive
+  stale pass (`<out>.stale`) the board ends with
+  `-> OWED relay-skipped code=<sha7> behind=<n>: <why> (stale <k> consecutive passes)`.
+  Never a fast-forward in place. `HPO_TICK_CODE_DIR` replaces the checkout.
+  Relay gap (S14-RELAY-CADENCE): in the sleep between passes the loop reaps a
+  finished relay (its `TICK-RELAY` line) and starts the next under the same lock
+  once `HPO_TICK_RELAY_GAP` s (default 120) have passed since it ended; the tick
+  keeps `--interval`. A stale pass starts none in its sleep, nor does a relay in flight.
diff --git a/tools/audit/seat/ledger.py b/tools/audit/seat/ledger.py
index b8a98f4a7f..b15cec7d8f 100644
--- a/tools/audit/seat/ledger.py
+++ b/tools/audit/seat/ledger.py
@@ -37,7 +37,7 @@ where its rewritten level `<log>.level` already lives:
 
 KINDS. DERIVED kinds are recomputed every pass from the live world and never
 accumulate: the relay rewrites them into `<log>.level` (`handoff-no-pr` through
-`level` here), the tick computes `design-build` and `review-owed`. EVENT kinds
+`level` here), the tick computes `design-build`, `design-review` and `review-owed`. EVENT kinds
 cannot be recomputed and live in events.tsv: an `open` at a new sha supersedes
 the subject's open entry (a moved subject closes the old one and opens one); a
 `close` at its sha, or at `-`, is the producer's disposal. The PR-keyed events
@@ -104,8 +104,8 @@ from merge_train import is_sha  # noqa: E402
 ROOT = Path(__file__).resolve().parents[3]
 KINDS = {
     "handoff-no-pr": "derived", "handoff-update": "derived", "probe-ref": "derived",
-    "handoff-hold-malformed": "derived", "handoff-held": "derived", "handoff-body-stale": "derived", "handoff-body-unapplied": "derived", "handoff-hold-stale": "derived",
-    "design-build": "derived", "review-owed": "derived", "record-owed": "derived",
+    "handoff-hold-malformed": "derived", "handoff-held": "derived", "handoff-body-stale": "derived", "handoff-body-unapplied": "derived", "handoff-hold-stale": "derived", "handoff-skipped": "derived",
+    "design-build": "derived", "design-review": "derived", "review-owed": "derived", "record-owed": "derived",
     "probe-refused": "derived", "handoff-verdict-held": "derived", "confirm-owed": "derived", "push-stuck": "derived",
     "seat-no-return": "derived", "carry-fold": "derived",
     "fixer-round": "derived", "recut": "derived", "train-parked": "derived", "dirty": "derived",
@@ -116,6 +116,7 @@ KINDS = {
 PR_KEYED = ("reviewer-fire", "verdict-unposted", "approve-held-runs", "dispatch")
 ARMS = (("refs/heads/probe/", "probe-ref"), ("refs/heads/handoff-body/", "handoff-no-pr"),
         ("refs/heads/handoff/", "handoff-no-pr"), ("refs/heads/design-verdict/", "design-build"),
+        ("refs/heads/design/", "design-review"),
         ("refs/heads/review/", "confirm-owed"), ("refs/heads/handoff-wip/", "blocked-stop"))
 STATE_REF = re.compile(r"^audit-r\d+-(?:plan|roster)$")
 RELAY_WRITE = re.compile(r"\b(ledger_open|level_line) ([a-z-]+) ")
@@ -648,6 +649,35 @@ def design_builds(verdicts: dict, designs: dict, stage_of, disp: dict) -> list[s
     return out
 
 
+DESIGN_REVIEW_STAGES = NOT_DISPATCHED + ("design", "design-review")
+VERDICT_SHA = re.compile(r"^Design review: (\S+) ([0-9a-f]{40})")
+
+
+def design_reviews_owed(designs: dict, firsts: dict, tip_at: dict, review_at: dict, stage_of,
+                        disp: dict, now: float, critical=()) -> list[str]:
+    """`DESIGN-REVIEW OWED` lines: a design/<t> tip that its design-verdict/<t>
+    does not name, with no design-reviewer dispatch committed since the tip.
+    designs {t: tip sha}, firsts {t: (verdict sha, verdict.md first line)},
+    tip_at {t: tip commit epoch}, review_at {t: epoch of the newest
+    dispatch/design-reviewer-<t> commit, absent with no ref}, all keyed
+    lowercased; stage_of(t) -> (group, stage), stage "closed" for a group that
+    is not open. A tip already disposed at its own sha is not owed."""
+    out = []
+    for t, tip in sorted(designs.items()):
+        group, stage = stage_of(t)
+        m = VERDICT_SHA.match(firsts.get(t, ("", ""))[1])
+        if (m and m.group(2) == tip) or stage not in DESIGN_REVIEW_STAGES \
+                or disp.get(f"refs/heads/design/{t}", ("",))[0] == tip:
+            continue
+        if t in review_at and review_at[t] >= tip_at[t]:
+            continue
+        out.append(f"DESIGN-REVIEW OWED:{' CP' if group in critical else ''} {group or '?'} design/{t} {tip[:12]} "
+                   f"-- verdict {m.group(1) if m else 'none'} {m.group(2)[:12] if m else '-'}, "
+                   f"no dispatch/design-reviewer-{t} since the tip ({(now - tip_at[t]) / 3600:.1f}h); "
+                   "dispatch the design reviewer")
+    return out
+
+
 def review_owed(prs: list, readback: dict, dispatched: set, carries=None, skip_branch=None,
                 recarry=None) -> list[str]:
     """`REVIEW OWED: #N <head12>` per open non-draft PR whose comments were
@@ -854,6 +884,8 @@ def self_test() -> int:
         check("each of the five arms classifies", [classify(f"refs/heads/{p}/x") for p in
               ("probe", "handoff", "handoff-body", "design-verdict", "review")]
               == ["probe-ref", "handoff-no-pr", "handoff-no-pr", "design-build", "confirm-owed"])
+        check("a design tip classifies as design-review, beside the verdict arm's design-build",
+              classify("refs/heads/design/x") == "design-review" and classify("refs/heads/design-verdict/x") == "design-build")
         check("a ref of no arm is refused, not guessed", refuses(lambda: classify("refs/heads/main")) == "Refused")
         h = D / "imp"
         h.mkdir()
@@ -888,6 +920,16 @@ def self_test() -> int:
             del os.environ["HPO_STATE_DIR"]
         check("null control: dispose into the default home prints nothing and writes",
               rc_d == 0 and err.getvalue() == "" and dispositions(dflt)["refs/heads/probe/n"][0] == C)
+        dispose(h, "refs/heads/design/g1", C, "test")
+        check("dispose records a design tip, and a disposition at its sha silences DESIGN-REVIEW OWED",
+              design_reviews_owed({"g1": C}, {}, {"g1": 0}, {}, lambda t: ("R10-G1", "not-started"), {}, 3600.0) != []
+              and design_reviews_owed({"g1": C}, {}, {"g1": 0}, {}, lambda t: ("R10-G1", "not-started"),
+                                      dispositions(h), 3600.0) == [])
+        dro = lambda crit: design_reviews_owed({"g1": C}, {}, {"g1": 0}, {}, lambda t: ("R10-G1", "not-started"), {}, 3600.0, crit)
+        check("DESIGN-REVIEW OWED carries the CP mark for a critical group, as DESIGN OWED does",
+              [x.startswith("DESIGN-REVIEW OWED: CP R10-G1 ") for x in dro({"R10-G1"})] == [True])
+        check("null control: a group off the critical path prints no CP mark",
+              [x.startswith("DESIGN-REVIEW OWED: R10-G1 ") for x in dro(set())] == [True])
         check("dispose refuses a ref of no arm", refuses(lambda: dispose(h, "refs/heads/main", A)) == "Refused")
         check("a missing store with no legacy file is first run: empty", dispositions(D / "none") == {})
         (D / "bad").mkdir()
diff --git a/tools/audit/seat/orchestrator_tick.py b/tools/audit/seat/orchestrator_tick.py
index a7d15fee4a..395302934b 100644
--- a/tools/audit/seat/orchestrator_tick.py
+++ b/tools/audit/seat/orchestrator_tick.py
@@ -125,9 +125,6 @@ ROOT = Path(__file__).resolve().parents[3]
 RULESET = "main-protect-checks"
 STUCK_FACTOR = 2  # a lane pending past this many critical-path medians is stuck (ETA and WAITING share it)
 RECUT_BLOCKED = 3          # the owner's three-round rule: the third blocked verdict owes a re-cut
-SEAT_WINDOW_MIN = 120      # "a seat is on it": a fire or a handoff ref move inside this window
-FIRE_GRACE_MIN = 15        # a rendered payload this old with no FIRED line is FIRE-OWED
-FIRED_STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z?)")
 GATE_CONTEXTS = {"gate", "pr-contract"}  # the contexts an early-gate race reddens
 STALL_MINUTES = 90  # P328: p95 dispatch-to-verdict is 70 min; 90 fires on ~2.6% of reviews
 #: Per merge_train.py (its self-test pins the two equal): under the umbrella
@@ -215,6 +212,12 @@ BOT_LANE = re.compile(r"autofix|nightly|record", re.I)
 ERR_LINE = re.compile(r"error|FAILED|refused|fail", re.I)
 DEFERRED_STAGES = ("deferred", "refused")
 UNBLOCKABLE_STAGES = (None, "", "not-started")
+#: UNDISPATCHED reads these too: a `carries-open` group's own part merged and
+#: its carries still owe a seat, which UNBLOCKABLE_STAGES (not-started) never named.
+SEATLESS_STAGES = UNBLOCKABLE_STAGES + ("carries-open",)
+START_AFTER = re.compile(r"start after #(\d+)")
+SEAT_REFS = ("refs/heads/dispatch/fixer-*", "refs/heads/handoff/*", "refs/heads/handoff-wip/*",
+             "refs/heads/handoff-body/*", "refs/heads/fix/*")
 #: The shared actions whose pin the whole lane rides; a pin drift on one of
 #: these is the class that reddened a composed proof on a twin SHA.
 STATE_ACTIONS = ("actions/checkout", "actions/setup-node", "actions/cache",
@@ -252,13 +255,16 @@ def _module(name: str, *candidates: str):
 mt = _module("merge_train_tick", "tools/audit/seat/merge_train.py")
 #: The CI-priority rule (owner, tvofi 2026-10-28): the one order owed PRs print in.
 cpri = _module("ci_priority_tick", "tools/audit/seat/ci_priority.py")
+#: The owed-event watch (R11-PRE-STANDING-SCRIPTS): the one owner of the fired-ledger read,
+#: "a seat is on it" and FIRE-OWED; the methods below delegate to it.
+owatch = _module("owed_watch_tick", "tools/audit/seat/owed_watch.py")
 #: A paused.json record older than this with no train running is owed (P267).
 PAUSED_OWED_MIN = 60
 
 
 def verdict_kind(line: str, head: str) -> "str | None":
     """'merge' or 'blocked' when the approver verdict line names exactly `head`."""
-    m = re.match(r"^Fix review: (merge|blocked) ([0-9a-f]{40})(?: |$)", line)
+    m = owatch.FIX_VERDICT.match(line)  # the one verdict-line grammar
     return m.group(1) if m and m.group(2) == head else None
 
 
@@ -275,7 +281,7 @@ class Tick:
                  mandate_id: int | None = None, stall_hours: float = 2.0,
                  grace_hours: float = 0.5, behind_max: int = 25,
                  mandate_since_days: int = 14,
-                 relay_log: str | None = None,
+                 relay_log: str | None = None, state_dir: str | None = None,
                  bus_state: str | None = None,
                  now: datetime.datetime | None = None,
                  gh=None, git=None, proc=None, bus=None, carry=None,
@@ -293,9 +299,8 @@ class Tick:
         self.stall_hours, self.grace_hours = stall_hours, grace_hours
         self.behind_max = behind_max
         # cloud_relay.sh's own default log (#2419): POSTED/OWED lines.
-        self.relay_log = relay_log or os.path.join(
-            os.environ.get("HPO_STATE_DIR") or os.path.expanduser("~/.local/state/hpo"),
-            "cloud-relay.log")
+        self.state_dir = state_dir or os.environ.get("HPO_STATE_DIR") or os.path.expanduser("~/.local/state/hpo")
+        self.relay_log = relay_log or os.path.join(self.state_dir, "cloud-relay.log")
         # bus.sh's dispatch record (`pr head thread nonce`), REVIEW OWED's "no live dispatch".
         self.bus_state = bus_state or os.environ.get("HPO_BUS_STATE") or os.path.expanduser("~/.zcode/bus")
         self.now = now or datetime.datetime.now(datetime.timezone.utc)
@@ -618,7 +623,8 @@ class Tick:
         HPO_WIP_CAP -- at the cap a new group is not dispatched, while opening
         and merging are always allowed; and the counted PRs whose three-dot
         diff touches the coordinator, against its cap of 2. A diff one_pr
-        could not read leaves the second count a floor: flagged. A roster or a
+        could not read leaves the second count a floor: flagged. Then the open
+        PRs by class against the machinery slots (`pr_cap.class_line`). A roster or a
         cap it cannot read is UNREADABLE, never a clean zero."""
         cap_mod = _module("pr_cap_tick", "tools/audit/seat/pr_cap.py")
         if cap_mod is None:
@@ -642,6 +648,11 @@ class Tick:
         if unread:
             text += f"; diff UNREADABLE at {', '.join('#' + str(x) for x in unread)}, so at least {k}"
         self.line(S, text, flag=k > kcap or bool(unread))
+        rule, slots = cap_mod.product_rule(), cap_mod.open_slots()
+        if rule is None or slots is None:
+            self.unreadable(S, "PR classes", "machinery_ratchet.is_product or replan.DEFAULT_CAPS")
+        else:
+            self.line(S, *cap_mod.class_line(cap_mod.by_class(counted, files, rule), slots))
 
     def _verdict_authors(self, pw) -> "tuple[set, int] | None":
         """The approver App's identity off app_approve.sh, through
@@ -815,27 +826,8 @@ class Tick:
             return None
 
     def _fired(self) -> "list[tuple]":
-        """[(utc or None, line)] for each FIRED line of the dispatch seat's ledger."""
-        try:
-            with open(self.fired_log, encoding="utf-8", errors="replace") as fh:
-                rows = [l.strip() for l in fh if "FIRED" in l]
-        except (OSError, TypeError):
-            return []
-        out = []
-        for l in rows:
-            m = FIRED_STAMP.match(l)
-            when = None
-            if m:
-                when = datetime.datetime.fromisoformat(m.group(1).rstrip("Z")).replace(
-                    tzinfo=datetime.timezone.utc)
-            out.append((when, l))
-        return out
-
-    def _fire_names(self, n: int, topics: list, line: str) -> bool:
-        """A FIRED line names a PR by number, topic or its payload file
-        (`payload-fix-<n>-r<k>.json`, `payload-<n>-r<k>.json`)."""
-        return bool(re.search(rf"#{n}(?!\d)|payload-(?:fix-)?{n}-r\d+\.json", line)) or any(
-            t and re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", line, re.I) for t in topics)
+        """[(utc or None, line)] for each FIRED line of the dispatch seat's ledger (owed_watch.fired)."""
+        return owatch.fired(self.fired_log)
 
     def _disposed(self, ref: str, sha: str) -> bool:
         """The obligations ledger holds a disposition for `ref` at exactly `sha` (an older sha
@@ -854,27 +846,8 @@ class Tick:
         return text if code == 0 else None
 
     def _seat_on(self, n: int, topics: list, heads: dict, kinds=("handoff-wip", "handoff", "handoff-body")) -> bool:
-        """A seat is on a PR when, inside SEAT_WINDOW_MIN, a FIRED line names it, or a
-        handoff-wip/, handoff/ or handoff-body/<topic> ref moved (`kinds` narrows the refs)."""
-        cutoff = self.now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
-        for when, l in self._fired():
-            if (when is None or when >= cutoff) and self._fire_names(n, topics, l):
-                return True
-        tg = _module("topic_grammar_tick", "tools/audit/seat/topic_grammar.py")
-        for t in topics:
-            for fam in kinds:
-                refs = [f"{fam}/{t}"]
-                if fam == "handoff-wip":  # a split seat step-pushes under the family's topic (topic-family.md)
-                    refs += sorted(k for k in heads if k.startswith("handoff-wip/")
-                                   and k != refs[0] and tg.family(t).fullmatch(k[len("handoff-wip/"):]))  # mut:wipfamily
-                for ref in refs:
-                    sha = heads.get(ref)
-                    if fam == "handoff-wip" and sha and self._blocked_md(sha) is not None:  # mut:blockedseat
-                        continue  # a stop on a question is owed by blocked_stops, not a seat on the PR
-                    age = self._age_min(ref, sha) if sha else None
-                    if age is not None and age <= SEAT_WINDOW_MIN:
-                        return True
-        return False
+        """owed_watch.seat_on over this tick's ledger, clock and git reads."""
+        return owatch.seat_on(n, topics, heads, self._fired(), self.now, self._age_min, self._blocked_md, kinds)
 
     @staticmethod
     def _topics(branch: str) -> list:
@@ -1084,15 +1057,11 @@ class Tick:
         return "review-owed", "", ""
 
     def payloads(self, S: str) -> None:
-        """FIRE-OWED: a rendered payload file older than FIRE_GRACE_MIN that no FIRED line names."""
+        """FIRE-OWED (owed_watch.fire_owed): a rendered payload past its grace that no FIRED line names."""
         if not self.payload_dir:
             return
-        fired = self._fired()
-        for f in sorted(Path(self.payload_dir).glob("payload-*.json")):
-            age = (self.now.timestamp() - f.stat().st_mtime) / 60
-            if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in fired):
-                self.line(S, f"OWED fire-owed {f.name} rendered {int(age)}m ago, no FIRED line "
-                             "(firing is a RemoteTrigger call: the orchestrator's turn)", flag=True)
+        for text in owatch.fire_owed(self.payload_dir, self._fired(), self.now):
+            self.line(S, text, flag=True)
 
     def _reviewer_ref_age(self, n: int) -> "int | None":
         """Minutes since the tip of `dispatch/reviewer-rev-<n>` (cloud_dispatch.py's
@@ -1657,6 +1626,7 @@ class Tick:
         groups = rl.groups_of(roster)
         open_g = rl.open_groups(roster)
         self.line(S, f"{len(open_g)} open group(s) of {len(groups)}")
+        self.outside_chain_idle(S, rl, roster)
         for gid, g in groups.items():
             stage = (g.get("resume") or {}).get("stage")
             # roster_lib closes refused and deferred groups (is_open is
@@ -1677,6 +1647,125 @@ class Tick:
                 self.line(S, f"{gid}: in progress (stage {stage})")
         self.design_builds(S, rl, roster)
         self.designs_owed(S, rl, roster)
+        self.undispatched(S, rl, roster)
+
+    def undispatched(self, S: str, rl, roster: dict) -> None:
+        """`UNDISPATCHED:[ CP] <group> <age>`: an open group in SEATLESS_STAGES
+        whose `after` groups are all done or carries-open (a) or whose pending
+        carry reads `start after #N` with #N merged (b), and that no seat ref
+        (dispatch/fixer-<topic>, handoff/<topic>, handoff-wip/<topic>) has
+        touched since its gate opened: its own merge (`resume.commit`) or #N's.
+        A ref whose time cannot be read counts as a live seat; a failed ref
+        listing is UNREADABLE, never an empty list."""
+        seats = self._seats(S, rl, roster, "undispatched groups")
+        if seats is None:
+            return
+        groups, open_g = rl.groups_of(roster), rl.open_groups(roster)
+        critical = set(rl.critical_path(roster))
+        clear = rl.RELEASING_STAGES + ("carries-open",)
+        for gid, g in groups.items():
+            res = g.get("resume") or {}
+            if gid not in open_g or res.get("stage") not in SEATLESS_STAGES:
+                continue
+            opened = None
+            if res.get("stage") == "carries-open" and all(
+                    (groups[a].get("resume") or {}).get("stage") in clear for a in g.get("after") or [] if a in groups):
+                opened = self._commit_at(res.get("commit"))
+            for c in g.get("carry") or []:
+                m = START_AFTER.search(c) if rl.carry_mark(c) is None else None
+                if m and opened is None:
+                    opened = self._merged_at(m.group(1))
+            if opened is None:
+                continue
+            if any((at := self._commit_at("origin/" + r)) is None or at >= opened for r in seats.get(gid, [])):
+                continue
+            hours = (self.now - opened).total_seconds() / 3600.0
+            self.line(S, f"UNDISPATCHED:{' CP' if gid in critical else ''} {gid} {hours:.1f}h -- no dispatch, "
+                         "handoff or handoff-wip ref since its gate opened; dispatch the next part", flag=True)
+
+    def _opener_last(self, od: Path, topic: str) -> str:
+        """` -- opener last: <log line>` (open_driver's own open-driver.log, its newest
+        line naming `topic`) and ` -- STUCK after <n>` from fails.json; empty when the
+        opener has no state or never touched the topic. Read, never written."""
+        try:
+            with open(od / "open-driver.log", "rb") as fh:
+                fh.seek(0, 2)
+                fh.seek(max(0, fh.tell() - 262144))
+                last = [x for x in fh.read().decode("utf-8", "replace").splitlines() if f" {topic} " in x or x.endswith(f" {topic}")]
+        except OSError:
+            last = []
+        try:
+            fails = [f for k, f in json.loads((od / "fails.json").read_text()).items() if k.split()[0] == topic]
+        except (OSError, ValueError, IndexError, AttributeError):
+            fails = []
+        stuck = f" -- STUCK after {max(f.get('n', 0) for f in fails)}" if any(f.get("n", 0) >= 3 for f in fails) else ""
+        return (f" -- opener last: {last[-1]}" if last else "") + stuck
+
+    def _seats(self, S: str, rl, roster: dict, what: str):
+        """{group: [seat refs]} over SEAT_REFS, one ls-remote; None (after the
+        UNREADABLE line) when it fails, never an empty map."""
+        code, o = self.git(["ls-remote", "origin", *SEAT_REFS])
+        if code:
+            return self.unreadable(S, what, o.strip()[-100:])
+        seats: dict = {}
+        for l in o.splitlines():
+            ref = l.split()[1] if len(l.split()) >= 2 else ""
+            t = ref.removeprefix("refs/heads/").split("/", 1)[-1].removeprefix("fixer-") if "/" in ref else ""
+            if t and (gid := rl.group_for_branch(roster, "x/" + t)):
+                seats.setdefault(gid, []).append(ref.removeprefix("refs/heads/"))
+        return seats
+
+    def outside_chain_idle(self, S: str, rl, roster: dict) -> None:
+        """`OUTSIDE-CHAIN-IDLE <G> (#issue): <path> idle <h>h`, flagged: an open
+        `source: outside` group G, each `after` edge walked transitively over
+        the groups that still gate (roster_lib.gates), prints one line per
+        deepest group of a blocking path that no seat ref (SEAT_REFS) has
+        moved inside SEAT_WINDOW_MIN. A path ending in a live seat prints
+        nothing; an unreadable ref listing is UNREADABLE, never a clean chain."""
+        groups, open_g = rl.groups_of(roster), rl.open_groups(roster)
+        outside = [g for g in open_g if open_g[g].get("source") == "outside"]
+        seats = self._seats(S, rl, roster, "outside chains") if outside else {}
+        if seats is None:
+            return
+        window = datetime.timedelta(minutes=SEAT_WINDOW_MIN)
+
+        def idle(gid):
+            at = [self._commit_at("origin/" + r) for r in seats.get(gid, [])]
+            if any(a is None or self.now - a <= window for a in at):
+                return None  # a live seat, or a ref whose time cannot be read: not provably idle
+            return (self.now - max(a for a in at if a)).total_seconds() / 3600.0 if at else float("inf")
+
+        for gid in outside:
+            deepest, stack = {}, [[gid]]
+            while stack:
+                path = stack.pop()
+                up = [a for a in groups[path[-1]].get("after") or []
+                      if a in groups and a not in path and a in open_g and rl.gates(groups[a])]
+                if up:
+                    stack += [path + [a] for a in sorted(up, reverse=True)]
+                else:
+                    deepest.setdefault(path[-1], path)
+            for last, path in sorted(deepest.items()):
+                h = idle(last)
+                if h is not None:
+                    issues = open_g[gid].get("issues") or ["?"]
+                    self.line(S, f"OUTSIDE-CHAIN-IDLE {gid} (#{str(issues[0]).lstrip('#')}): {' <- '.join(path)} idle "
+                                 f"{'with no seat ref' if h == float('inf') else f'{h:.1f}h'}", flag=True)
+
+    def _commit_at(self, ref):
+        """The committer instant of `ref`, or None (no ref, or unreadable)."""
+        code, o = self.git(["log", "-1", "--format=%cI", ref]) if ref else (1, "")
+        try:
+            return None if code else datetime.datetime.fromisoformat(o.strip().replace("Z", "+00:00"))
+        except ValueError:
+            return None
+
+    def _merged_at(self, pr):
+        code, o = self.gh(["api", f"repos/{self.repo}/pulls/{pr}", "--jq", ".merged_at"])
+        try:
+            return None if code else datetime.datetime.fromisoformat(o.strip().replace("Z", "+00:00"))
+        except ValueError:
+            return None
 
     def designs_owed(self, S: str, rl, roster: dict) -> None:
         """`DESIGN OWED:` an eligible group (size L or XL, decision 0014) whose
@@ -1737,13 +1826,15 @@ class Tick:
         reads `Design review: approve <sha>` at `design/<g>`'s tip. The verdict
         and design refs are read over git; a read that fails is UNREADABLE."""
         lg = _module("ledger_tick", "tools/audit/seat/ledger.py")
-        code, o = self.git(["ls-remote", "origin", "refs/heads/design/*", "refs/heads/design-verdict/*"])
+        code, o = self.git(["ls-remote", "origin", "refs/heads/design/*", "refs/heads/design-verdict/*",
+                            "refs/heads/dispatch/design-reviewer-*"])
         if lg is None or code:
             self.unreadable(S, "approved designs", "ledger.py absent" if lg is None else o.strip()[-100:])
             return
-        designs, verdicts, names = {}, {}, {}
+        designs, verdicts, reviewers, names = {}, {}, {}, {}
         for sha, ref in (l.split()[:2] for l in o.splitlines() if len(l.split()) >= 2):
-            for prefix, into in (("refs/heads/design-verdict/", verdicts), ("refs/heads/design/", designs)):
+            for prefix, into in (("refs/heads/design-verdict/", verdicts), ("refs/heads/design/", designs),
+                                 ("refs/heads/dispatch/design-reviewer-", reviewers)):
                 if ref.startswith(prefix):
                     into[ref[len(prefix):].lower()] = sha
                     names[(prefix, ref[len(prefix):].lower())] = ref
@@ -1770,6 +1861,36 @@ class Tick:
             return
         for text in lg.design_builds(firsts, designs, stage_of, disp):
             self.line(S, text, flag=True)
+        self.design_reviews_owed(S, rl, roster, lg, (designs, reviewers, firsts, disp), names)
+
+    def design_reviews_owed(self, S: str, rl, roster: dict, lg, seen: tuple, names: dict) -> None:
+        """`DESIGN-REVIEW OWED:` every pass (ledger.design_reviews_owed): the
+        design tips and design-reviewer dispatch tips are fetched once for their
+        committer times; a failed read is UNREADABLE, never an empty list."""
+        designs, reviewers, firsts, disp = seen
+        if not designs:
+            return
+        refs = [names[("refs/heads/design/", t)] for t in designs] \
+            + [names[("refs/heads/dispatch/design-reviewer-", t)] for t in reviewers]
+        if self.git(["fetch", "-q", "origin", *refs])[0]:
+            return self.unreadable(S, "design reviews owed", "could not fetch the design refs")
+        times = {}
+        for sha in {*designs.values(), *reviewers.values()}:
+            code, o = self.git(["log", "-1", "--format=%ct", sha])
+            if code or not o.strip().isdigit():
+                return self.unreadable(S, "design reviews owed", f"no commit time for {sha[:12]}")
+            times[sha] = int(o.strip())
+        groups, open_g = rl.groups_of(roster), rl.open_groups(roster)
+
+        def stage_of(t):
+            gid = rl.group_for_branch(roster, f"design/{t}")
+            if gid not in open_g:
+                return gid, "closed"
+            return gid, (groups[gid].get("resume") or {}).get("stage")
+        for text in lg.design_reviews_owed(designs, firsts, {t: times[s] for t, s in designs.items()},
+                                           {t: times[s] for t, s in reviewers.items()}, stage_of, disp,
+                                           self.now.timestamp(), set(rl.critical_path(roster))):
+            self.line(S, text, flag=True)
 
     # ---------------------------------------------------------------- MAIN
     def main(self) -> None:
@@ -2494,10 +2615,17 @@ class Tick:
             return
         stranded.sort(key=lambda l: bool(HELD_TOPIC.match(l)))  # stable: held last, each group in bus order
         held = sum(bool(HELD_TOPIC.match(l)) for l in stranded)
+        od = Path(self.state_dir) / "open-driver"
+        if stranded and not od.is_dir():
+            self.line(S, "OPENER ABSENT: open_driver.py has no state under $HPO_STATE_DIR -- a session-local "
+                         "opener is a defect (orchestrator.md 13)", flag=True)
         for l in stranded[:CAP_ORPHANS]:
-            self.line(S, f"OWED handoff: {l[len('ORPHAN '):]} -- no PR head "
+            body = l[len('ORPHAN '):]
+            if HELD_TOPIC.match(l):
+                body = body.replace("repair=opener", "held by ruling")
+            self.line(S, f"OWED handoff: {body} -- no PR head "
                          "carries it: open_pr.sh (opener), update_pr.sh "
-                         "(update) or a human decision (review)", flag=True)
+                         f"(update) or a human decision (review){self._opener_last(od, l.split()[1])}", flag=True)
         if len(stranded) > CAP_ORPHANS:
             self.line(S, f"OWED handoffs capped at {CAP_ORPHANS} of "
                          f"{len(stranded)} ({held} held, listed last); the rest print next pass once "
@@ -2897,6 +3025,7 @@ def self_test() -> int:
         gh.on(lambda argv: any(x.endswith("/comments?per_page=100") for x in argv), out="[]")
         git = Stub()
         git.on(("fetch",), out="")
+        git.on(("ls-remote", "refs/heads/dispatch/fixer-*"), out="")  # UNDISPATCHED: no seat refs unless an arm says
         git.on(("merge-base", "--is-ancestor"), rc=0)
         git.on(("merge-base", "origin/main"), out=V)
         git.on(("diff", "--no-renames", "--name-only"), out=kw.pop("files", "dev/programme/delivery/9.md"))
@@ -2930,6 +3059,9 @@ def self_test() -> int:
                out=str(behind_handover))
         git.on(("cat-file", "-e"), rc=1)  # rows missing unless a stub says otherwise
         kw.setdefault("relay_log", os.devnull)  # hermetic: never the host's relay log
+        if "state_dir" not in kw:  # nor its opener's state: a present, empty open-driver dir
+            (tmp / "state-ok" / "open-driver").mkdir(parents=True, exist_ok=True)
+            kw["state_dir"] = str(tmp / "state-ok")
         kw.setdefault("bus_state", str(tmp / "no-bus"))  # nor its dispatch record
         # hermetic: never the real carry_audit; the routing-invariants read is clean
         kw.setdefault("carry", lambda argv: (0, ["CARRY-ROSTER: stub; 0 stranded carry(ies)"]))
@@ -3948,6 +4080,46 @@ def self_test() -> int:
                      tick(bus_refs=live11 + [summ25.replace("25", "11")], bus_rc=1)))),
         ])
         total, failed = total + a, failed + f
+        # ---- OWED handoffs carry the opener's last result; OPENER ABSENT; held by ruling ----
+        op_dir = tmp / "state-op" / "open-driver"
+        op_dir.mkdir(parents=True)
+        (op_dir / "open-driver.log").write_text(
+            "2026-11-15T01:00:00Z START r10-live-0 bbbbbbbb\n"
+            "2026-11-15T01:02:00Z RESULT r10-live-0 bbbbbbbb rc=1 REFUSE: merge conflicts\n"
+            "2026-11-15T01:03:00Z NEEDS-TITLE r10-live-1 bbbbbbbb\n")
+        (op_dir / "fails.json").write_text(json.dumps({f"r10-live-0 {'b' * 40}": {"n": 3, "rc": 1, "why": "x"}}))
+        stk = tmp / "state-stuck"
+        stk.mkdir()
+        (stk / "fails.json").write_text(json.dumps({f"r10-t{n} {'b' * 40}": {"n": n, "rc": 1, "why": "x"} for n in (1, 2, 3)}))
+        mk = lambda sd, refs: (lambda tt: (tt.orphans("REPLAN"), tt)[1])(
+            tick(bus_refs=refs + [summ25.replace("25", str(len(refs)))], bus_rc=1, state_dir=str(sd)))
+        two = [live11[0], live11[1], held14[0]]
+        t_op, t_ab = mk(tmp / "state-op", two), mk(tmp / "state-none", two)
+        ow_op = [x["text"] for x in t_op.findings if x["text"].startswith("OWED handoff: ")]
+        ow_ab = [x["text"] for x in t_ab.findings if x["text"].startswith("OWED handoff: ")]
+        a, f = check("OWED handoffs opener state", [
+            ("a line carries the opener's newest log line for its topic and its STUCK count",
+             "opener last: 2026-11-15T01:02:00Z RESULT r10-live-0 bbbbbbbb rc=1 REFUSE: merge conflicts" in ow_op[0]
+             and ow_op[0].endswith("STUCK after 3")),
+            ("a NEEDS-TITLE result is carried and, below three failures, no STUCK",
+             "opener last: 2026-11-15T01:03:00Z NEEDS-TITLE r10-live-1" in ow_op[1] and "STUCK" not in ow_op[1]),
+            ("a triage topic reads `held by ruling`, not `repair=opener`",
+             "held by ruling" in ow_op[2] and "repair=opener" not in ow_op[2]),
+            ("a topic the opener never touched carries no opener clause",
+             "opener last" not in ow_op[2]),
+            ("below three failures there is no STUCK (n=1 and n=2); at three there is",
+             not any("STUCK" in t_op._opener_last(stk, f"r10-t{n}") for n in (1, 2))
+             and "STUCK after 3" in t_op._opener_last(stk, "r10-t3")),
+            ("with the state directory present no OPENER ABSENT prints",
+             not any(x["text"].startswith("OPENER ABSENT") for x in t_op.findings)),
+            ("null control: with no open-driver directory, one flagged OPENER ABSENT line prints and the owed lines still do",
+             sum(x["text"].startswith("OPENER ABSENT: open_driver.py has no state") for x in t_ab.findings) == 1
+             and len(ow_ab) == 3),
+            ("null control: an all-clear bus prints no OPENER ABSENT with no state directory",
+             not any(x["text"].startswith("OPENER ABSENT") for x in
+                     (lambda tt: (tt.orphans("REPLAN"), tt)[1])(tick(bus_refs=[BUS_CLEAR], state_dir=str(tmp / "state-none"))).findings)),
+        ])
+        total, failed = total + a, failed + f
         t = tick(bus_refs=[BUS_CLEAR])
         t.orphans("REPLAN")
         a, f = check("OWED handoffs all-clear", [
@@ -4394,13 +4566,13 @@ def self_test() -> int:
             fl.write_text(fired)
             tf = tick(prs=[], fired_log=str(fl), payload_dir=str(pd))
             tf.payloads("PRS")
-            return [x["text"] for x in tf.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed")]
+            return [x["text"] for x in tf.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed") and x["flag"]]
         fo, fo0 = fire_owed(""), fire_owed("FIRED payload-fix-86-r1.json\n")
         pd2 = tmp / "payloads-young"
         pd2.mkdir()
         pf2 = pd2 / "payload-fix-86-r2.json"
         pf2.write_text("{}")
-        os.utime(pf2, ((NOW - timedelta(minutes=FIRE_GRACE_MIN - 5)).timestamp(),) * 2)
+        os.utime(pf2, ((NOW - timedelta(minutes=owatch.FIRE_GRACE_MIN - 5)).timestamp(),) * 2)
         tfy = tick(prs=[], fired_log=os.devnull, payload_dir=str(pd2))
         tfy.payloads("PRS")
         fo_young = [x["text"] for x in tfy.sections.get("PRS", []) if x["text"].startswith("OWED fire-owed")]
@@ -4861,6 +5033,14 @@ def self_test() -> int:
             ("a diff it cannot read flags the coordinator count as a floor",
              one(unread, "coordinator.py PRs: ")["flag"] is True
              and "UNREADABLE at #2, so at least 0" in one(unread, "coordinator.py PRs: ")["text"]),
+            ("open PRs by class: the three touching a product path are production",
+             one(at, "open PRs by class: ") == {"flag": False, "text": "open PRs by class: 3 production, "
+                                                "3 machinery; machinery slots 3/10 (10 of 20 reserved for production)"}),
+            ("an unread diff is its own class, counted against the machinery slots",
+             one(unread, "open PRs by class: ")["text"].startswith(
+                 "open PRs by class: 0 production, 1 machinery, 1 unread; machinery slots 2/10")),
+            ("twenty machinery PRs fill the machinery slots: flagged (null: six above are not)",
+             one(board, "open PRs by class: ")["flag"] is True),
             ("an invalid HPO_WIP_CAP is UNREADABLE, never a count",
              any(l["flag"] and "UNREADABLE: WIP cap" in l["text"] for l in badcap)
              and not any(l["text"].startswith("WIP: ") for l in badcap)),
@@ -5247,6 +5427,7 @@ def self_test() -> int:
                                 f"{A40}\trefs/heads/design/R10-G1\n{B40}\trefs/heads/design-verdict/r10-g1\n"
                                 f"{A40}\trefs/heads/design/r10-g2\n{B40}\trefs/heads/design-verdict/r10-g2\n"))
             t._git.h.insert(0, ((f"{B40}:verdict.md",), 0, verdict_text))
+            t._git.h.insert(0, (("log", "-1", "--format=%ct"), 0, str(int(NOW.timestamp()))))
             t.design_builds("PLAN", rlm, droster)
             return flagged(t.sections.get("PLAN", []))
         db = dboard(f"Design review: approve {A40}\n- point\n")
@@ -5255,6 +5436,7 @@ def self_test() -> int:
         t_pl._git.h.insert(0, (("ls-remote", "refs/heads/design/*"), 0,
                                f"{A40}\trefs/heads/design/R10-G1\n{B40}\trefs/heads/design-verdict/r10-g1\n"))
         t_pl._git.h.insert(0, ((f"{B40}:verdict.md",), 0, f"Design review: approve {A40}\n"))
+        t_pl._git.h.insert(0, (("log", "-1", "--format=%ct"), 0, str(int(NOW.timestamp()))))
         t_pl.plan()
         db_plan = flagged(t_pl.sections.get("PLAN", []))
         db_rev = dboard(f"Design review: revise {A40} class-open\n")
@@ -5294,6 +5476,224 @@ def self_test() -> int:
         ])
         total, failed = total + a, failed + f
 
+        # ---- DESIGN-REVIEW OWED: a design tip no verdict names, no reviewer dispatched since ----
+        C40, D40, OLD40 = "c" * 40, "d" * 40, "1" * 40
+        hr = int(NOW.timestamp()) - 3 * 3600
+        rroster = {"groups": [{"group": "R10-G1", "resume": {"stage": "not-started"}},
+                              {"group": "R10-G9", "resume": {"stage": "done"}}]}
+
+        def rboard(verdict_text, reviewer_at=hr - 3600, stage="not-started", gid="R10-G1", disp=None):
+            hd = tmp / f"rb{len(list(tmp.glob('rb*')))}"
+            hd.mkdir()
+            for r, v in (disp or {}).items():  # through ledger.dispose, so a ref of no ledger arm is refused here too
+                _module("ledger_tick", "tools/audit/seat/ledger.py").dispose(hd, r, v[0])
+            t = tick(relay_log=str(hd / "relay.log"))
+            ls = f"{A40}\trefs/heads/design/{gid}\n"
+            if verdict_text is not None:
+                ls += f"{B40}\trefs/heads/design-verdict/{gid.lower()}\n"
+            if reviewer_at is not None:
+                ls += f"{D40}\trefs/heads/dispatch/design-reviewer-{gid.lower()}\n"
+            t._git.h.insert(0, (("ls-remote", "refs/heads/design/*"), 0, ls))
+            t._git.h.insert(0, ((f"{B40}:verdict.md",), 0, verdict_text or ""))
+            t._git.h.insert(0, (("log", "-1", "--format=%ct", A40), 0, str(hr)))
+            t._git.h.insert(0, (("log", "-1", "--format=%ct", D40), 0, str(reviewer_at or 0)))
+            tr = {"groups": [dict(rroster["groups"][0], group=gid, resume={"stage": stage})]}
+            t.design_builds("PLAN", rlm, tr)
+            return flagged(t.sections.get("PLAN", []))
+        ou = _module("owed_unactioned_tick", "tools/audit/seat/owed_unactioned.py")
+        _rv = rboard
+        rboard = lambda *a, **k: [x for x in _rv(*a, **k) if x.startswith("DESIGN-REVIEW OWED:")]
+        r_rev, r_none = rboard(f"Design review: revise {OLD40} class-open\n"), rboard(None, reviewer_at=None)
+        r_ok, r_new = rboard(f"Design review: approve {A40}\n"), rboard(f"Design review: revise {OLD40}\n", reviewer_at=hr + 60)
+        r_done, r_disp = rboard(f"Design review: revise {OLD40}\n", stage="done"), \
+            rboard(f"Design review: revise {OLD40}\n", disp={"refs/heads/design/r10-g1": (A40, "t", "h")})
+        r_dr = rboard(f"Design review: revise {OLD40}\n", stage="design-review")
+        def unread(**extra):  # raw PLAN lines of a board whose design-ref fetch or a commit-time read fails
+            hd = tmp / f"rbu{len(list(tmp.glob('rbu*')))}"
+            hd.mkdir()
+            t = tick(relay_log=str(hd / "relay.log"))
+            t._git.h.insert(0, (("ls-remote", "refs/heads/design/*"), 0, f"{A40}\trefs/heads/design/R10-G1\n"))
+            t._git.h.insert(0, (("log", "-1", "--format=%ct", A40), 0, str(hr)))
+            for m, rc2 in extra.items():
+                t._git.h.insert(0, (tuple(m.split("|")), rc2, "fatal: unreadable"))
+            t.design_builds("PLAN", rlm, {"groups": [{"group": "R10-G1", "resume": {"stage": "not-started"}}]})
+            return flagged(t.sections.get("PLAN", []))
+        r_ok0 = unread()
+        r_fetch = unread(**{"fetch|-q|origin|refs/heads/design/R10-G1": 1})
+        r_time = unread(**{f"log|-1|--format=%ct|{A40}": 1})
+        cproster = {"groups": [{"group": "R10-G1", "resume": {"stage": "not-started"}},
+                               {"group": "R10-G2", "after": ["R10-G1"], "resume": {"stage": "not-started"}},
+                               {"group": "R10-G3", "resume": {"stage": "not-started"}}]}
+        cpt = tick(relay_log=str(tmp / "cprb.log"))
+        cpt._git.h.insert(0, (("ls-remote", "refs/heads/design/*"), 0,
+                              f"{A40}\trefs/heads/design/R10-G2\n{C40}\trefs/heads/design/R10-G3\n"))
+        for sha_ in (A40, C40):
+            cpt._git.h.insert(0, (("log", "-1", "--format=%ct", sha_), 0, str(hr)))
+        cpt.design_builds("PLAN", rlm, cproster)
+        cp_lines = [x for x in flagged(cpt.sections.get("PLAN", [])) if x.startswith("DESIGN-REVIEW OWED:")]
+        a, f = check("DESIGN-REVIEW OWED", [
+            ("a critical-path group's line carries the CP mark, as DESIGN OWED does",
+             any(x.startswith("DESIGN-REVIEW OWED: CP R10-G2 design/r10-g2 ") for x in cp_lines)),
+            ("null control: a group off the critical path prints no CP mark",
+             any(x.startswith("DESIGN-REVIEW OWED: R10-G3 design/r10-g3 ") for x in cp_lines) and len(cp_lines) == 2),
+            ("null control: with both reads answering the tip is owed and nothing is UNREADABLE",
+             any(x.startswith("DESIGN-REVIEW OWED:") for x in r_ok0) and not any("UNREADABLE" in x for x in r_ok0)),
+            ("a failed fetch of the design refs is UNREADABLE and owes no line",
+             any(x.startswith("UNREADABLE: design reviews owed") and "fetch the design refs" in x for x in r_fetch)
+             and not any(x.startswith("DESIGN-REVIEW OWED:") for x in r_fetch)),
+            ("a failed commit-time read is UNREADABLE naming the sha, and owes no line",
+             any(x.startswith("UNREADABLE: design reviews owed") and f"no commit time for {A40[:12]}" in x for x in r_time)
+             and not any(x.startswith("DESIGN-REVIEW OWED:") for x in r_time)),
+            ("a revise verdict naming an older sha, a newer tip and an older reviewer dispatch give exactly one line",
+             len(r_rev) == 1 and f" R10-G1 design/r10-g1 {A40[:12]} " in r_rev[0]
+             and f"verdict revise {OLD40[:12]}" in r_rev[0] and "(3.0h)" in r_rev[0]),
+            ("no verdict and no reviewer ref is owed too, and reads `verdict none`",
+             len(r_none) == 1 and "verdict none -" in r_none[0]),
+            ("null controls: a verdict at the tip, a reviewer dispatched after the tip and a done group print nothing",
+             r_ok == [] and r_new == [] and r_done == []),
+            ("null control: a disposition at the tip's sha silences it", r_disp == []),
+            ("the stage `design-review` is owed too", len(r_dr) == 1),
+            ("the emitted line keys in owed_unactioned on design/<g> and the tip",
+             ou.key_of("-> " + r_rev[0]) == ("design/r10-g1", [A40[:12]]) and bool(ou.FAMILY.match("-> " + r_rev[0]))),
+        ])
+        total, failed = total + a, failed + f
+
+        # ---- UNDISPATCHED: a group whose gate is open and that no seat touched ----
+        ud_at = NOW - datetime.timedelta(hours=8)
+        udr = {"groups": [
+            {"group": "R10-DONE", "resume": {"stage": "done"}},
+            {"group": "R10-OI", "after": ["R10-DONE"], "carry": ["part 2 builds the intake"],
+             "resume": {"stage": "carries-open", "commit": "e" * 40}},
+            {"group": "R10-LATE", "carry": ["start after #3262, the second part"],
+             "resume": {"stage": "not-started"}},
+            {"group": "R10-HELD", "after": ["R10-OI", "R10-NEW"], "resume": {"stage": "carries-open", "commit": "e" * 40}},
+            {"group": "R10-NEW", "resume": {"stage": "in-progress"}}]}
+
+        def uboard(refs="", stage_of_oi="carries-open", ref_at=None, ls_rc=0):
+            t = tick()
+            t._git.h.insert(0, (("ls-remote", "refs/heads/dispatch/fixer-*"), ls_rc, refs))
+            t._git.h.insert(0, (("log", "-1", "--format=%cI", "e" * 40), 0, iso(ud_at) + "\n"))
+            if ref_at:
+                t._git.h.insert(0, (("log", "-1", "--format=%cI", "origin/"), 0, iso(ref_at) + "\n"))
+            t._gh.h.insert(0, (("pulls/3262", ".merged_at"), 0, iso(ud_at) + "\n"))
+            ro = json.loads(json.dumps(udr))
+            ro["groups"][1]["resume"]["stage"] = stage_of_oi
+            t.undispatched("PLAN", rlm, ro)
+            return [x for x in flagged(t.sections.get("PLAN", [])) if x.startswith(("UNDISPATCHED", "UNREADABLE"))]
+        u_none = uboard()
+        u_live = uboard(f"{A40}\trefs/heads/dispatch/fixer-r10-oi\n", ref_at=NOW - datetime.timedelta(hours=1))
+        u_old = uboard(f"{A40}\trefs/heads/dispatch/fixer-r10-oi\n", ref_at=NOW - datetime.timedelta(hours=20))
+        u_un = uboard(ls_rc=1)
+
+        class SeatStub(Stub):  # ls-remote answers only the planted refs the argv's patterns match, as origin does
+            planted = ""
+
+            def __call__(self, argv):
+                if argv[:2] == ["ls-remote", "origin"] and any("fixer-" in a for a in argv):
+                    self.calls.append(list(argv))
+                    rows = [l for l in self.planted.splitlines()
+                            if any(fnmatch.fnmatch(l.split()[1], pat) for pat in argv[2:])]
+                    return 0, "".join(r + "\n" for r in rows)
+                return super().__call__(argv)
+
+        def sboard(ref):  # one planted ref, a minute old, for R10-OI's topic
+            t = tick()
+            st = SeatStub()
+            st.h, st.planted = t._git.h, f"{A40}\t{ref}\n"
+            t._git = st
+            t._git.h.insert(0, (("log", "-1", "--format=%cI", "e" * 40), 0, iso(ud_at) + "\n"))
+            t._git.h.insert(0, (("log", "-1", "--format=%cI", "origin/"), 0, iso(NOW - datetime.timedelta(hours=1)) + "\n"))
+            ro = json.loads(json.dumps(udr))
+            t.undispatched("PLAN", rlm, ro)
+            return [x for x in flagged(t.sections.get("PLAN", [])) if x.startswith(("UNDISPATCHED", "UNREADABLE"))]
+        seat_fams = ("dispatch/fixer-", "handoff/", "handoff-wip/", "handoff-body/", "fix/")
+        seat_lines = {fam: sboard(f"refs/heads/{fam}r10-oi") for fam in seat_fams}
+        u_probe = sboard("refs/heads/probe/r10-oi")
+        a, f = check("UNDISPATCHED", [
+            ("a carries-open group whose gate is open and that has no seat ref prints the line with its age",
+             any(x.startswith("UNDISPATCHED: CP R10-OI 8.0h") for x in u_none)),
+            ("null control: a group off the critical path prints no CP mark",
+             any(x.startswith("UNDISPATCHED: R10-LATE 8.0h") for x in u_none)),
+            ("a `start after #N` carry whose #N merged prints it too", any(" R10-LATE 8.0h" in x for x in u_none)),
+            ("null control: a group held behind an unfinished after-group prints nothing",
+             not any("R10-HELD" in x for x in u_none)),
+            ("null control: a dispatch ref newer than the gate opening prints nothing for that group",
+             not any("R10-OI" in x for x in u_live) and any("R10-LATE" in x for x in u_live)),
+            ("a dispatch ref older than the gate opening is no seat", any("R10-OI" in x for x in u_old)),
+            ("every SEAT_REFS family is a seat: a fresh ref of each alone silences its group",
+             all(not any("R10-OI" in x for x in ls_) for ls_ in seat_lines.values())),
+            ("null control: a fresh ref of a family that is no seat leaves the group listed",
+             any("R10-OI" in x for x in u_probe)),
+            ("a group at stage `in-progress` with no start-after carry prints nothing",
+             not any("R10-NEW" in x for x in u_none) and not any("R10-DONE" in x for x in u_none)),
+            ("an unreadable ref listing is UNREADABLE", any("UNREADABLE: undispatched groups" in x for x in u_un)
+             and not any(x.startswith("UNDISPATCHED") for x in u_un)),
+            ("the emitted line keys in owed_unactioned on its group",
+             ou.key_of("-> " + u_none[0])[0] in ("R10-OI", "R10-LATE") and bool(ou.FAMILY.match("-> " + u_none[0]))),
+        ])
+        total, failed = total + a, failed + f
+
+        # ---- OUTSIDE-CHAIN-IDLE: an outside group's blocking path ends in no live seat ----
+        ocr = {"groups": [
+            {"group": "R10-OUT", "source": "outside", "issues": [3401], "after": ["R10-MID", "R10-FIN"], "resume": {"stage": "not-started"}},
+            {"group": "R10-MID", "after": ["R10-LEAF"], "resume": {"stage": "not-started"}},
+            {"group": "R10-LEAF", "resume": {"stage": "in-progress"}},
+            {"group": "R10-FIN", "resume": {"stage": "done"}},
+            {"group": "R10-PLAIN", "after": ["R10-LEAF"], "resume": {"stage": "not-started"}}]}
+
+        def cboard(refs, leaf_age_h=None, ls_rc=0, roster=ocr):
+            t = tick()
+            t._git.h.insert(0, (("ls-remote", "refs/heads/dispatch/fixer-*"), ls_rc, refs))
+            if leaf_age_h is not None:
+                t._git.h.insert(0, (("log", "-1", "--format=%cI", "origin/handoff/r10-leaf"), 0,
+                                    iso(NOW - datetime.timedelta(hours=leaf_age_h)) + "\n"))
+            t.outside_chain_idle("PLAN", rlm, roster)
+            return flagged(t.sections.get("PLAN", []))
+        leaf_ref = f"{A40}\trefs/heads/handoff/r10-leaf\n"
+        c_old, c_live, c_none, c_un = cboard(leaf_ref, 8.4), cboard(leaf_ref, 0.5), cboard(""), cboard("", ls_rc=1)
+        a, f = check("OUTSIDE-CHAIN-IDLE", [
+            ("an outside group blocked through MID by a LEAF whose seat ref is 8.4 h old prints the whole path and the idle hours",
+             c_old == ["OUTSIDE-CHAIN-IDLE R10-OUT (#3401): R10-OUT <- R10-MID <- R10-LEAF idle 8.4h"]),
+            ("a leaf with no seat ref at all says so, not a number",
+             c_none == ["OUTSIDE-CHAIN-IDLE R10-OUT (#3401): R10-OUT <- R10-MID <- R10-LEAF idle with no seat ref"]),
+            ("null control: a path ending in a seat ref inside the window prints nothing", c_live == []),
+            ("null control: a plain (non-outside) group's chain onto the same idle leaf prints nothing",
+             not any("R10-PLAIN" in x for x in c_old + c_none)),
+            ("an unreadable ref listing is UNREADABLE and owes nothing it cannot know",
+             any("UNREADABLE: outside chains" in x for x in c_un) and not any(x.startswith("OUTSIDE") for x in c_un)),
+        ])
+        total, failed = total + a, failed + f
+
+        # ---- class barrier (R10-RCA-TICK-BLIND section 2): a repair-discharges-line arm per owed-family kind ----
+        # The census reads owed_unactioned's FAMILY, the one list of lines an operator is told to repair:
+        # a kind is ARMED (an arm below runs its named repair in the fakes and the line goes, and one
+        # where the repair cannot run changes the line to say so) or is DEBT, owed an arm; a kind in
+        # neither, or in both, or one the family no longer holds, is a failure of the census itself.
+        fam = set(re.match(r"\^-> \((.*)\)$", ou.FAMILY.pattern).group(1).split("|"))
+        owed_ok = tick(bus_refs=[BUS_CLEAR], state_dir=str(tmp / "state-op"))
+        owed_ok.orphans("REPLAN")
+        armed = {
+            "OWED": [("the opener's repair (the ref carried) removes the OWED handoff line",
+                      not any(x["text"].startswith("OWED handoff:") for x in owed_ok.findings)),
+                     ("the repair that cannot run (3 failures) changes the line to say STUCK", ow_op[0].endswith("STUCK after 3")),
+                     ("the repair skipped by ruling changes it to `held by ruling`", "held by ruling" in ow_op[2]),
+                     ("the repair's missing precondition prints OPENER ABSENT",
+                      any(x["text"].startswith("OPENER ABSENT") for x in t_ab.findings))],
+            "DESIGN-REVIEW OWED:": [("dispatching the reviewer after the tip removes the line", r_new == []),
+                                    ("a verdict at the tip removes it", r_ok == []),
+                                    ("a precondition gone (the group done) removes it", r_done == [])],
+            "UNDISPATCHED:": [("a dispatch ref after the gate opened removes the line for its group",
+                               not any("R10-OI" in x for x in u_live))],
+            "DESIGN-BUILD:": [("a dispatched build removes the line", [x.split()[1] for x in db] == ["R10-G1"])],
+        }
+        debt = {"REVIEW OWED:", "RECORD-OWED:", "DISPATCH:", "OWNER FLAG:", "MERGE-READY:", "BLOCKED-UNFIXED:",
+                "APPROVAL-OWED:", "UNLEVELLED:", "REVIEW STALLED:"}
+        a, f = check("repair-discharges-line census", [
+            ("every owed-family kind is armed or debt, none both, none stale", set(armed) | debt == fam and not set(armed) & debt),
+            ("every armed kind has at least one arm and each arm holds", all(arms and all(ok for _, ok in arms) for arms in armed.values())),
+        ] + [(f"{k}: {label}", ok) for k, arms in sorted(armed.items()) for label, ok in arms])
+        total, failed = total + a, failed + f
+
         # ---- DESIGN OWED carries the dispatch age and a CP mark ----
         aroster = {"groups": [
             {"group": "R10-P", "size": "S", "resume": {"stage": "in-progress", "branch": "handoff/r10-p"}},
diff --git a/tools/audit/seat/owed_unactioned.py b/tools/audit/seat/owed_unactioned.py
index e09132c723..a3db74e3a7 100644
--- a/tools/audit/seat/owed_unactioned.py
+++ b/tools/audit/seat/owed_unactioned.py
@@ -15,7 +15,7 @@ asked again. On 2026-10-28 the critical-path handoff r10-orch-beatd (#2916) stoo
 two handoffs routed to the opener at 10:55Z stood 8 h.
 
 WHAT IT DOES. It reads the tick board's owed family -- every `-> ` line that
-starts `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:`, `DESIGN-BUILD:`,
+starts `OWED`, `REVIEW OWED:`, `DISPATCH:`, `OWNER FLAG:`, `DESIGN-BUILD:`, `DESIGN-REVIEW OWED:`, `UNDISPATCHED:`,
 `MERGE-READY:`, `BLOCKED-UNFIXED:`, `APPROVAL-OWED:`, `UNLEVELLED:`, `REVIEW STALLED:` or `RECORD-OWED:` -- and keys each on its obligation: the
 handoff topic, or `#<pr>`. A verdict level (`MERGE-READY: #N <head8>`) carries
 its head8 as the id, so an acknowledgement covers one head and a new head
@@ -55,7 +55,7 @@ import tempfile
 
 # The tick's cap notice (Tick.orphans) rides the OWED prefix but is no obligation: it names a count, not a topic (carry 10).
 CAP_NOTICE = re.compile(r"^-> OWED handoffs capped at \d+ of \d+(?: \([^)]*\))?;")
-FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|RECORD-OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:|MERGE-READY:|BLOCKED-UNFIXED:|APPROVAL-OWED:|UNLEVELLED:|REVIEW STALLED:)")
+FAMILY = re.compile(r"^-> (OWED|REVIEW OWED:|RECORD-OWED:|DISPATCH:|OWNER FLAG:|DESIGN-BUILD:|DESIGN-REVIEW OWED:|UNDISPATCHED:|MERGE-READY:|BLOCKED-UNFIXED:|APPROVAL-OWED:|UNLEVELLED:|REVIEW STALLED:)")
 BOARD = re.compile(r"^BOARD measured from origin/main at \S+, (\S+)")
 SHA = re.compile(r"\b[0-9a-f]{12,40}\b")
 REF = re.compile(r"\b(?:refs/heads/)?(?:handoff-body|handoff|design)/(\S+)")
@@ -116,6 +116,12 @@ def key_of(line: str) -> "tuple[str, list[str]]":
         r = REF.match(subj)
         return (r.group(1) if r else f"#{subj}" if subj.isdigit()
                 else subj.removeprefix("refs/heads/")), shas
+    m = re.match(r"UNDISPATCHED:(?: CP)? (\S+) ", body)  # the group is the subject; its age grows, no sha
+    if m:
+        return m.group(1), []
+    m = re.match(r"DESIGN-REVIEW OWED:(?: CP)? \S+ (design/\S+) ([0-9a-f]{12}) ", body)  # the tip is the id: a new tip re-raises
+    if m:
+        return m.group(1), [m.group(2)]
     m = REF.search(body)
     if m and re.match(r"(DISPATCH|OWNER FLAG|DESIGN-BUILD): ", body):
         return m.group(1), shas
diff --git a/tools/audit/seat/owed_watch.py b/tools/audit/seat/owed_watch.py
new file mode 100644
index 0000000000..5d6cb62b74
--- /dev/null
+++ b/tools/audit/seat/owed_watch.py
@@ -0,0 +1,699 @@
+#!/usr/bin/env python3
+"""owed_watch.py -- the owed-event watch: who was fired, whether a seat is on it, what is owed past its grace.
+
+    python3 -I tools/audit/seat/owed_watch.py cp-owed --repo O/R --fired LEDGER [--checkout DIR] [--roster-ref REF]
+    python3 -I tools/audit/seat/owed_watch.py --self-test
+
+WHY THIS EXISTS (R11-PRE-STANDING-SCRIPTS part 1, design/R11-PRE-STANDING-SCRIPTS 375ce7ff3f,
+approved at design-verdict be6cc24cae). The owner's directive (tvofi 2026-11-09, triage
+s6-batch141.md P515): "never let the critical path or outside PRs slip, ever". The watch ran only
+as a session-local loop. This module owns the fired-ledger read, the "a seat is on it" predicate
+and every owed-by-grace arm; orchestrator_tick.py imports the first two and its FIRE-OWED level,
+and the beat's `cp-owed` row (beat_jobs.py) runs `cp-owed` here.
+
+THE WATCHED SET is computed, never hand-kept: every open roster group `roster_lib.is_outside` is
+true for, plus every group `roster_lib.critical_path_read` publishes at the roster ref, and the
+open pull requests mapped to them (`group_for_branch`, else `group_for_pr`). An unreadable
+critical-path file is UNREADABLE, never an empty set.
+
+THE ARMS, one `CP-OWED <arm> <subject> ...` line per step past its grace (GRACE_MIN):
+  merge-no-approval  a `Fix review: merge <head>` verdict at the PR head, no APPROVED review at it
+  approved-unmerged  an APPROVED review at the head of a still-open PR
+  blocked-no-fire    a `Fix review: blocked <head>` verdict at the head, no FIRED line naming the PR
+                     and no handoff ref moved since the verdict
+  head-no-dispatch   no verdict at the head and no reviewer dispatch whose prompt names the head
+  UNFIRED            a dispatch ref of the group (fixer, designer, design reviewer, reviewer) with
+                     no FIRED line naming the group and no return ref moved since it was published
+  DESIGN-REVIEW-OWED a design tip no design verdict names (P510's predicate); a `seat-refused`
+                     verdict is no review; a tip whose note opens `Design blocked:` is a designer
+                     stop, owed by the dispatch drain, never here
+  FIXER-OWED         an approve at the design tip, no fixer dispatch and no handoff ref since
+  SEAT-SILENT        the group's newest FIRED line with no return ref moved since it, keyed on
+                     refs and never on a cloud session's status (a dead session reads running)
+"After" compares a FIRED line's leading UTC stamp with the step's commit time; an unstamped line
+is never "after" anything. Lines are ranked by `roster_lib.dispatch_rank` (hotfix, then
+critical path or outside), the critical path ahead of outside inside a rank, oldest first.
+Exit 0 with the lines, 2 with `cp-owed: UNREADABLE <what>` lines when a read failed.
+"""
+from __future__ import annotations
+
+import argparse
+import datetime
+import json
+import os
+import re
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+SEAT = Path(__file__).resolve().parent
+sys.path.insert(0, str(SEAT))
+import roster_lib  # noqa: E402
+import topic_grammar  # noqa: E402
+
+SEAT_WINDOW_MIN = 120      # "a seat is on it": a fire or a handoff ref move inside this window
+FIRE_GRACE_MIN = 15        # a rendered payload this old with no FIRED line is FIRE-OWED
+SEAT_KINDS = ("handoff-wip", "handoff", "handoff-body")
+FIRED_STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z?)")
+#: carry 4's graces, minutes. UNFIRED takes FIRE_GRACE_MIN (the same step as FIRE-OWED: published,
+#: not fired) and FIXER-OWED the design-review step's 10 (verdict in, next seat not dispatched);
+#: the carry names no figure for either.
+GRACE_MIN = {"merge-no-approval": 10, "approved-unmerged": 45, "blocked-no-fire": 15,
+             "head-no-dispatch": 25, "UNFIRED": FIRE_GRACE_MIN, "DESIGN-REVIEW-OWED": 10,
+             "FIXER-OWED": 10, "SEAT-SILENT": 90}
+FIX_VERDICT = re.compile(r"^Fix review: (merge|blocked) ([0-9a-f]{40})(?: |$)")
+DESIGN_VERDICT = re.compile(r"^Design review: ([a-z-]+) ([0-9a-f]{40})(.*)$")
+DESIGN_BLOCKED = "Design blocked:"
+FAMILIES = ("verdict", "dispatch", "design", "design-verdict", "handoff", "handoff-wip", "handoff-body", "probe")
+RETURN_FAMILIES = ("handoff", "handoff-wip", "handoff-body", "design", "design-verdict")
+
+
+# ------------------------------------------------------------ the fired ledger (moved from the tick)
+
+def fired(path) -> "list[tuple]":
+    """[(utc datetime or None, line)] for each FIRED line of the dispatch seat's ledger."""
+    try:
+        with open(path, encoding="utf-8", errors="replace") as fh:
+            rows = [l.strip() for l in fh if "FIRED" in l]
+    except (OSError, TypeError):
+        return []
+    out = []
+    for l in rows:
+        m = FIRED_STAMP.match(l)
+        when = None
+        if m:
+            when = datetime.datetime.fromisoformat(m.group(1).rstrip("Z")).replace(
+                tzinfo=datetime.timezone.utc)
+        out.append((when, l))
+    return out
+
+
+def fire_names(n: int, topics: list, line: str) -> bool:
+    """A FIRED line names a PR by number, topic or its payload file
+    (`payload-fix-<n>-r<k>.json`, `payload-<n>-r<k>.json`)."""
+    return bool(re.search(rf"#{n}(?!\d)|payload-(?:fix-)?{n}-r\d+\.json", line)) or any(
+        t and re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", line, re.I) for t in topics)
+
+
+def seat_on(n: int, topics: list, heads: dict, rows: list, now, age_min, blocked_md,
+            kinds=SEAT_KINDS) -> bool:
+    """A seat is on a PR when, inside SEAT_WINDOW_MIN, a FIRED line names it, or a
+    handoff-wip/, handoff/ or handoff-body/<topic> ref moved (`kinds` narrows the refs).
+    `age_min(ref, sha)` and `blocked_md(sha)` are the caller's git reads."""
+    cutoff = now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
+    for when, l in rows:
+        if (when is None or when >= cutoff) and fire_names(n, topics, l):
+            return True
+    for t in topics:
+        for fam in kinds:
+            refs = [f"{fam}/{t}"]
+            if fam == "handoff-wip":  # a split seat step-pushes under the family's topic (topic-family.md)
+                refs += sorted(k for k in heads if k.startswith("handoff-wip/")
+                               and k != refs[0] and topic_grammar.family(t).fullmatch(k[len("handoff-wip/"):]))  # mut:wipfamily
+            for ref in refs:
+                sha = heads.get(ref)
+                if fam == "handoff-wip" and sha and blocked_md(sha) is not None:  # mut:blockedseat
+                    continue  # a stop on a question is owed by blocked_stops, not a seat on the PR
+                age = age_min(ref, sha) if sha else None
+                if age is not None and age <= SEAT_WINDOW_MIN:
+                    return True
+    return False
+
+
+def fire_owed(payload_dir, rows: list, now) -> "list[str]":
+    """FIRE-OWED: a rendered payload file older than FIRE_GRACE_MIN that no FIRED line names."""
+    out = []
+    for f in sorted(Path(payload_dir).glob("payload-*.json")):
+        age = (now.timestamp() - f.stat().st_mtime) / 60
+        if age > FIRE_GRACE_MIN and not any(f.name in l for _, l in rows):
+            out.append(f"OWED fire-owed {f.name} rendered {int(age)}m ago, no FIRED line "
+                       "(firing is a RemoteTrigger call: the orchestrator's turn)")
+    return out
+
+
+# ------------------------------------------------------------------------------ cp-owed, pure
+
+def _names_group(g: dict, line: str) -> bool:
+    """A FIRED line names the group: its id, its topic, or one of its pull requests."""
+    return fire_names(-1, [g["gid"], g["topic"]], line) or any(fire_names(n, [], line) for n in g["prs"])
+
+
+def _fired_since(g: dict, rows: list, t: float) -> bool:
+    return any(when is not None and when >= t and _names_group(g, l) for when, l in rows)
+
+
+def _group_refs(g: dict, refs: dict, families) -> "list[str]":
+    """The group's refs in `families`: <family>/<topic> (any family member for handoff-wip and
+    dispatch/fixer-), <family>/<gid> (design refs carry the group's case), and per pull request
+    verdict/<n>, probe/rev-<n>-<nonce> and dispatch/reviewer-rev-<n>."""
+    fam_t, gid = topic_grammar.family(g["topic"]), g["gid"].lower()
+    out = []
+    for ref in refs:
+        family, _, rest = ref.partition("/")
+        if family not in families:
+            continue
+        low = rest.lower()
+        if family == "dispatch":
+            ok = (low.startswith("fixer-") and fam_t.fullmatch(low[6:])) or low in (
+                f"designer-{gid}", f"design-reviewer-{gid}") or any(low == f"reviewer-rev-{n}" for n in g["prs"])
+        elif family in ("design", "design-verdict"):
+            ok = low == gid
+        elif family == "verdict":
+            ok = any(low == str(n) for n in g["prs"])
+        elif family == "probe":
+            ok = any(low.startswith(f"rev-{n}-") for n in g["prs"])
+        else:
+            ok = bool(fam_t.fullmatch(low)) if family == "handoff-wip" else low == g["topic"]
+        if ok:
+            out.append(ref)
+    return out
+
+
+def _returned_since(g: dict, refs: dict, ctime: dict, t: float) -> bool:
+    return any(ctime[refs[r]] >= t for r in _group_refs(g, refs, RETURN_FAMILIES + ("verdict", "probe")))
+
+
+def cp_owed(groups: dict, prs: list, refs: dict, ctime: dict, first: dict, rows: list, now: float,
+            graces: dict = GRACE_MIN) -> "list[str]":
+    """The CP-OWED lines, ranked. groups: gid -> {gid, topic, tags, rank, prs}; prs: dicts
+    number/head/gid/head_t/approved_t; refs: `<family>/<name>` -> sha; ctime: sha -> epoch;
+    first: sha -> the first line of the tip's note (VERDICT.md, verdict.md, design.md, PROMPT.md);
+    rows: `fired()`'s output, stamps as epochs or None."""
+    owed = []
+
+    def owe(g, arm, subject, since, detail):
+        age = int((now - since) // 60)
+        if now - since > graces[arm] * 60:  # mut:grace
+            tags = " ".join(g["tags"])
+            owed.append(((g["rank"], "CP" not in g["tags"], -age),
+                         f"CP-OWED {arm} {subject} {age}m past its {graces[arm]}m grace [{tags}] -- {detail}"))
+
+    for p in prs:
+        g, n, head = groups[p["gid"]], p["number"], p["head"]
+        vsha = refs.get(f"verdict/{n}")
+        m = FIX_VERDICT.match(first.get(vsha, "")) if vsha else None
+        at_head = bool(m) and m[2] == head
+        if p.get("approved_t") is not None:
+            owe(g, "approved-unmerged", f"#{n}", p["approved_t"], f"approved at {head[:12]}, not merged")
+        elif at_head and m[1] == "merge":
+            owe(g, "merge-no-approval", f"#{n}", ctime[vsha], f"merge verdict at {head[:12]}, no approval")
+        if at_head and m[1] == "blocked":
+            t = ctime[vsha]
+            if not _fired_since(g, rows, t) and not any(  # mut:blockedfire
+                    ctime[refs[r]] >= t for r in _group_refs(g, refs, ("handoff", "handoff-wip", "handoff-body"))):
+                owe(g, "blocked-no-fire", f"#{n}", t, f"blocked at {head[:12]}, no fire and no repair since")
+        if not at_head:
+            dsha = refs.get(f"dispatch/reviewer-rev-{n}")
+            if not (dsha and f"at head {head}" in first.get(dsha, "")):  # mut:dispatchhead
+                owe(g, "head-no-dispatch", f"#{n}", p["head_t"], f"head {head[:12]} has no verdict and no reviewer dispatch")
+
+    for gid, g in groups.items():
+        for ref in _group_refs(g, refs, ("dispatch",)):
+            t = ctime[refs[ref]]
+            if not _fired_since(g, rows, t) and not _returned_since(g, refs, ctime, t):  # mut:unfired
+                owe(g, "UNFIRED", gid, t, f"{ref} published, no FIRED line and no return since")
+        dsha = refs.get(next((r for r in refs if r.lower() == f"design/{gid.lower()}"), ""))
+        if dsha and not first.get(dsha, "").startswith(DESIGN_BLOCKED):  # mut:designblocked
+            vsha = refs.get(next((r for r in refs if r.lower() == f"design-verdict/{gid.lower()}"), ""))
+            m = DESIGN_VERDICT.match(first.get(vsha, "")) if vsha else None
+            refused = bool(m) and m[3].split()[-1:] == ["seat-refused"]  # mut:seatrefused
+            kind = m[1] if m and m[2] == dsha and not refused else None  # the review at the tip, if any
+            if kind is None:
+                owe(g, "DESIGN-REVIEW-OWED", gid, ctime[dsha], f"design/{gid} at {dsha[:12]} has no design review")
+            elif kind == "approve":
+                t = ctime[vsha]
+                if not any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))
+                           if not r.startswith(("dispatch/design", "dispatch/reviewer-rev-"))):  # mut:fixerowed
+                    owe(g, "FIXER-OWED", gid, t, f"design approved at {dsha[:12]}, no fixer dispatched")
+        last = max((when for when, l in rows if when is not None and _names_group(g, l)), default=None)
+        if last is not None and not _returned_since(g, refs, ctime, last):  # mut:silent
+            owe(g, "SEAT-SILENT", gid, last, "fired, no return ref since")
+    return [line for _, line in sorted(owed)]
+
+
+# ------------------------------------------------------------------------------ cp-owed, live
+
+def sh(argv, cwd=None):
+    p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
+    return p.returncode, p.stdout + p.stderr
+
+
+class Unreadable(Exception):
+    pass
+
+
+def _epoch(iso: str) -> float:
+    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
+
+
+def read_world(repo: str, checkout: str, fired_path: str, roster_ref, run=sh):
+    """The pure core's inputs, read over gh and git; Unreadable names the first read that failed."""
+    git = lambda *a: run(["git", "-C", checkout, *a])
+    ref = roster_lib.reader_ref(checkout, roster_ref)
+    try:
+        roster = roster_lib.show_roster(checkout, ref)
+    except (roster_lib.RosterNotFound, ValueError) as e:
+        raise Unreadable(f"roster at {ref}: {e}")
+    cp, why = roster_lib.critical_path_read(checkout, ref)
+    if cp is None:
+        raise Unreadable(f"critical path: {why}")
+    groups = {}
+    for gid, g in roster_lib.open_groups(roster).items():
+        tags = [t for t, on in (("HOTFIX", roster_lib.is_hotfix(g)), ("CP", roster_lib.norm_group(gid) in cp),
+                                ("OUTSIDE", roster_lib.is_outside(g))) if on]
+        if "CP" in tags or "OUTSIDE" in tags:
+            groups[gid] = {"gid": gid, "topic": roster_lib.branch_of(g).split("/", 1)[-1].lower(), "tags": tags,
+                           "rank": roster_lib.dispatch_rank(roster, gid, cp), "prs": []}
+    code, o = run(["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "300",
+                   "--json", "number,headRefOid,headRefName,reviews"])
+    try:
+        listed = json.loads(o) if code == 0 else None
+        if not isinstance(listed, list):
+            raise ValueError(o.strip()[-120:])
+    except ValueError as e:
+        raise Unreadable(f"open pull requests: {e}")
+    prs = []
+    for p in listed:
+        gid = roster_lib.group_for_branch(roster, p.get("headRefName") or "") or roster_lib.group_for_pr(roster, p["number"])
+        if gid in groups:
+            groups[gid]["prs"].append(p["number"])
+            ok = [_epoch(r["submittedAt"]) for r in p.get("reviews") or ()
+                  if r.get("state") == "APPROVED" and (r.get("commit") or {}).get("oid") == p["headRefOid"]]
+            prs.append({"number": p["number"], "head": p["headRefOid"], "gid": gid,
+                        "approved_t": max(ok) if ok else None})
+    code, o = git("ls-remote", "origin", *(f"refs/heads/{f}/*" for f in FAMILIES))
+    if code:
+        raise Unreadable(f"ls-remote: {o.strip()[-120:]}")
+    every = {l.split()[1][len("refs/heads/"):]: l.split()[0] for l in o.splitlines()
+             if len(l.split()) == 2 and l.split()[1].startswith("refs/heads/")}
+    refs = {r: every[r] for g in groups.values() for r in _group_refs(g, every, FAMILIES)}
+    want = sorted(set(refs.values()) | {p["head"] for p in prs})
+    if want:
+        code, o = git("fetch", "-q", "origin", *(f"refs/heads/{r}" for r in sorted(refs)),
+                      *(f"refs/pull/{p['number']}/head" for p in prs))
+        if code:
+            raise Unreadable(f"fetch: {o.strip()[-120:]}")
+        code, o = git("log", "--no-walk", "--format=%H %ct", *want)
+        if code:
+            raise Unreadable(f"commit times: {o.strip()[-120:]}")
+    ctime = {l.split()[0]: float(l.split()[1]) for l in (o.splitlines() if want else []) if len(l.split()) == 2}
+    first = {}
+    for r, sha in refs.items():
+        note = {"verdict": "VERDICT.md", "design-verdict": "verdict.md", "design": "design.md",
+                "dispatch": "PROMPT.md"}.get(r.split("/", 1)[0])
+        if note:
+            code, o = git("show", f"{sha}:{note}")
+            first[sha] = (o.splitlines() or [""])[0] if code == 0 else ""
+    for p in prs:
+        p["head_t"] = ctime.get(p["head"])
+        if p["head_t"] is None:
+            raise Unreadable(f"#{p['number']}'s head {p['head'][:12]} commit time")
+    rows = [(w.timestamp() if w else None, l) for w, l in fired(fired_path)]
+    return groups, prs, refs, ctime, first, rows
+
+
+def main(argv=None) -> int:
+    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
+    ap.add_argument("cmd", nargs="?", choices=("cp-owed",))
+    ap.add_argument("--repo", default="tvofi/heatpump_optimizer")
+    ap.add_argument("--fired", help="the dispatch seat's fire ledger")
+    ap.add_argument("--checkout", default=".")
+    ap.add_argument("--roster-ref")
+    ap.add_argument("--self-test", action="store_true")
+    a = ap.parse_args(argv)
+    if a.self_test:
+        return self_test()
+    if a.cmd != "cp-owed" or not a.fired:
+        ap.error("cp-owed needs --fired")
+    try:
+        world = read_world(a.repo, a.checkout, a.fired, a.roster_ref)
+    except Unreadable as e:
+        print(f"cp-owed: UNREADABLE {e}")
+        return 2
+    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
+    for line in cp_owed(*world, now):
+        print(line)
+    return 0
+
+
+# ------------------------------------------------------------------------------ self-test
+SELF_TEST_MARK = "# " + "-" * 78 + " self-test"
+
+
+def _world(arm: str, grace0: bool):
+    """A planted world: one critical-path group CPG (PR #11) and one outside group OUT (PR #12),
+    every timestamp 60 min before now. `arm` plants exactly one owed step; "none" plants none."""
+    now, t = 1_800_000_000.0, 1_800_000_000.0 - 3600
+    h = {k: c * 40 for k, c in (("h11", "1"), ("h12", "2"), ("d", "d"), ("v", "e"), ("x", "f"))}
+    groups = {"CPG": {"gid": "CPG", "topic": "r11-cpg", "tags": ["CP"], "rank": 1, "prs": [11]},
+              "OUT": {"gid": "OUT", "topic": "r11-out", "tags": ["OUTSIDE"], "rank": 1, "prs": [12]}}
+    prs = [{"number": 11, "head": h["h11"], "gid": "CPG", "head_t": t, "approved_t": None},
+           {"number": 12, "head": h["h12"], "gid": "OUT", "head_t": t, "approved_t": None}]
+    refs = {"dispatch/reviewer-rev-11": "a1" * 20, "dispatch/reviewer-rev-12": "a2" * 20,
+            "verdict/12": "b2" * 20, "handoff/r11-cpg": "c1" * 20}
+    first = {"a1" * 20: f"CLOUD REVIEWER seat for PR #11, at head {h['h11']}. Bus nonce: x",
+             "a2" * 20: f"CLOUD REVIEWER seat for PR #12, at head {h['h12']}. Bus nonce: y",
+             "b2" * 20: f"Fix review: blocked {'0' * 40} code: old head"}
+    ctime = {h["h11"]: t, h["h12"]: t, "c1" * 20: t + 90, "b2" * 20: t + 90}  # each seat returned after its fire
+    rows = [(t + 60, "FIRED reviewer #11"), (t + 60, "FIRED reviewer #12")]
+    if arm == "merge-no-approval":
+        refs["verdict/11"], first["9" * 40] = "9" * 40, f"Fix review: merge {h['h11']}"
+    elif arm == "approved-unmerged":
+        refs["verdict/11"], first["9" * 40] = "9" * 40, f"Fix review: merge {h['h11']}"
+        prs[0]["approved_t"] = t
+    elif arm == "blocked-no-fire":
+        refs["verdict/12"], first["9" * 40] = "9" * 40, f"Fix review: blocked {h['h12']} code: x"
+        rows = [(t - 60, "FIRED reviewer #12"), (t + 60, "FIRED reviewer #11")]
+    elif arm == "head-no-dispatch":
+        first["a1" * 20] = f"CLOUD REVIEWER seat for PR #11, at head {'7' * 40}. Bus nonce: x"
+    elif arm == "UNFIRED":
+        refs["dispatch/designer-OUT"] = "8" * 40
+        ctime["8" * 40] = t + 120
+    elif arm in ("DESIGN-REVIEW-OWED", "seat-refused", "revise-at-tip", "design-blocked"):
+        refs["design/OUT"], first[h["d"]] = h["d"], ("Design blocked: ref_privacy refused" if arm == "design-blocked"
+                                                    else "# OUT: a design")
+        if arm in ("seat-refused", "revise-at-tip"):
+            refs["design-verdict/OUT"] = h["v"]
+            first[h["v"]] = f"Design review: revise {h['d']}" + (" seat-refused" if arm == "seat-refused" else "")
+    elif arm == "FIXER-OWED":
+        refs["design/OUT"], refs["design-verdict/OUT"] = h["d"], h["v"]
+        first[h["d"]], first[h["v"]] = "# OUT: a design", f"Design review: approve {h['d']}"
+        ctime[h["v"]] = t + 120
+    elif arm == "SEAT-SILENT":
+        rows.append((t + 300, "FIRED fixer for r11-out"))
+    for sha in refs.values():
+        ctime.setdefault(sha, t)
+    if grace0:
+        return groups, prs, refs, ctime, first, rows, now, dict.fromkeys(GRACE_MIN, 0)
+    return groups, prs, refs, ctime, first, rows, now, dict.fromkeys(GRACE_MIN, 24 * 60)
+
+
+ARMS = tuple(GRACE_MIN)
+
+
+def _aged(world):
+    """A planted world's refs and heads moved 1e8 s into the past, so a run at the real clock reads them old."""
+    groups, prs, refs, ctime, first, rows = world
+    return groups, prs, refs, {k: v - 1e8 for k, v in ctime.items()}, first, rows
+
+
+def cases(mod) -> "dict[str, bool]":
+    res = {}
+    run = lambda arm, g0=True: mod.cp_owed(*_world(arm, g0))
+    base = run("none")
+    res["null: every step answered, nothing is owed (grace 0)"] = base == []
+    for arm in ARMS:
+        got = run(arm)
+        res[f"planted {arm}: one line at grace 0"] = (
+            len(got) == 1 and got[0].startswith(f"CP-OWED {arm} ") and "past its 0m grace" in got[0])
+        res[f"null {arm}: inside its grace prints nothing"] = run(arm, False) == []
+    res["DESIGN-REVIEW-OWED: a seat-refused verdict at the tip is no review"] = (
+        [l.split()[1] for l in run("seat-refused")] == ["DESIGN-REVIEW-OWED"])
+    res["DESIGN-REVIEW-OWED null: a class-open revise at the tip is a review (the designer owes)"] = run("revise-at-tip") == []
+    res["DESIGN-REVIEW-OWED null: a `Design blocked:` tip is a designer stop, not a review owed"] = run("design-blocked") == []
+    w = list(_world("UNFIRED", True))
+    w[2]["handoff/r11-out"], w[3]["c9" * 20] = "c9" * 20, w[3]["8" * 40] + 60
+    res["UNFIRED null: a return ref newer than the dispatch is a fire"] = mod.cp_owed(*w) == []
+    def variant(arm, **extra):
+        """`arm`'s world with refs added: name -> (sha, seconds after the world's step time, first line)."""
+        w = list(_world(arm, True))
+        for ref, (sha, dt, line) in extra.items():
+            w[2][ref.replace("__", "/")], w[3][sha], w[4][sha] = sha, w[6] - 3600 + dt, line
+        return mod.cp_owed(*w)
+    got = variant("none", dispatch__fixer_x=("f1" * 20, 120, ""))
+    res["UNFIRED: only the group's own dispatch refs count (a stranger's fixer dispatch is not the group's)"] = got == []
+    got = variant("none", **{"dispatch__fixer-r11-out-p2": ("f1" * 20, 120, "")})
+    res["UNFIRED: a fixer dispatch of a family member (-p2) is the group's"] = (
+        [l.split()[1:3] for l in got] == [["UNFIRED", "OUT"]])
+    for name, ref, line in (("a design push", "design__OUT", "Design blocked: x"),
+                            ("a probe verdict", "probe__rev-12-abcd", ""),
+                            ("a family member's step push", "handoff-wip__r11-out-p1", "")):
+        res[f"SEAT-SILENT null: {name} after the fire is a return"] = variant("SEAT-SILENT", **{ref: ("f2" * 20, 400, line)}) == []
+    res["SEAT-SILENT: a design push of another group is no return"] = (
+        [l.split()[1] for l in variant("SEAT-SILENT", design__OUTX=("f2" * 20, 400, "Design blocked: x"))] == ["SEAT-SILENT"])
+    res["blocked-no-fire null: a handoff ref at the verdict's own second is a repair"] = (
+        variant("blocked-no-fire", **{"handoff__r11-out": ("f3" * 20, 0, "")}) == [])
+    w = list(_world("UNFIRED", True))
+    w[5] = w[5] + [(w[3]["8" * 40], "FIRED designer R11-out OUT")]
+    res["UNFIRED null: a FIRED line naming the group, stamped at the dispatch's own second, is a fire"] = not any(
+        l.split()[1] == "UNFIRED" for l in mod.cp_owed(*w))
+    w[5][-1] = (w[3]["8" * 40] - 1, "FIRED designer OUT")
+    res["UNFIRED: a FIRED line a second before the dispatch is no fire for it"] = (
+        [l.split()[1] for l in mod.cp_owed(*w) if l.split()[1] == "UNFIRED"] == ["UNFIRED"])
+    res["FIXER-OWED's age runs from the approve verdict, not from another ref"] = " 58m past " in (run("FIXER-OWED") or [""])[0]
+    res["the line names the step's age in whole minutes"] = " 60m past its 0m grace " in (run("merge-no-approval") or [""])[0]
+    w = list(_world("none", True))
+    w[0]["OUT"]["tags"], w[0]["OUT"]["rank"] = ["HOTFIX", "OUTSIDE"], 0
+    w[0]["CPG"]["tags"] = ["CP"]
+    w[2]["design/OUT"], w[2]["design/CPG"] = "d1" * 20, "d2" * 20
+    w[3]["d1" * 20] = w[3]["d2" * 20] = w[6] - 7200
+    ranked = mod.cp_owed(*w)
+    res["rank: a hotfix group ahead of a critical-path one (roster_lib.dispatch_rank)"] = (
+        [l.split()[2] for l in ranked] == ["OUT", "CPG"])
+    w[0]["OUT"]["tags"], w[0]["OUT"]["rank"] = ["OUTSIDE"], 1
+    res["rank: inside one rank the critical path is ahead of outside"] = (
+        [l.split()[2] for l in mod.cp_owed(*w)] == ["CPG", "OUT"])
+    return res
+
+
+#: one edit per arm, in a temp copy of this file; the named case must fail.
+MUTANTS = {
+    "grace_ignored": ("if now - since > graces[arm] * 60:  # mut:grace", "if True:  # mut:grace",
+                      "null merge-no-approval: inside its grace prints nothing"),
+    "approval_ignored": ('if p.get("approved_t") is not None:', "if False:", "planted approved-unmerged: one line at grace 0"),
+    "merge_arm": ('elif at_head and m[1] == "merge":', "elif False:", "planted merge-no-approval: one line at grace 0"),
+    "blocked_fire": ("if not _fired_since(g, rows, t) and not any(  # mut:blockedfire", "if any(  # mut:blockedfire",
+                     "planted blocked-no-fire: one line at grace 0"),
+    "dispatch_head": ('if not (dsha and f"at head {head}" in first.get(dsha, "")):  # mut:dispatchhead',
+                      "if not dsha:  # mut:dispatchhead", "planted head-no-dispatch: one line at grace 0"),
+    "unfired": ("if not _fired_since(g, rows, t) and not _returned_since(g, refs, ctime, t):  # mut:unfired",
+                "if not _fired_since(g, rows, t):  # mut:unfired",
+                "UNFIRED null: a return ref newer than the dispatch is a fire"),
+    "unfired_dropped": ('owe(g, "UNFIRED", gid, t,', 'None and owe(g, "UNFIRED", gid, t,', "planted UNFIRED: one line at grace 0"),
+    "design_blocked": ("if dsha and not first.get(dsha, \"\").startswith(DESIGN_BLOCKED):  # mut:designblocked",
+                       "if dsha:  # mut:designblocked",
+                       "DESIGN-REVIEW-OWED null: a `Design blocked:` tip is a designer stop, not a review owed"),
+    "seat_refused": ('refused = bool(m) and m[3].split()[-1:] == ["seat-refused"]  # mut:seatrefused',
+                     "refused = False  # mut:seatrefused",
+                     "DESIGN-REVIEW-OWED: a seat-refused verdict at the tip is no review"),
+    "design_review_dropped": ("            if kind is None:\n", "            if False:\n",
+                              "planted DESIGN-REVIEW-OWED: one line at grace 0"),
+    "fixer_owed": ('if not any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))',
+                   'if any(ctime[refs[r]] >= t for r in _group_refs(g, refs, ("dispatch", "handoff", "handoff-wip"))',
+                   "planted FIXER-OWED: one line at grace 0"),
+    "silent": ("if last is not None and not _returned_since(g, refs, ctime, last):  # mut:silent",
+               "if False:  # mut:silent", "planted SEAT-SILENT: one line at grace 0"),
+    "rank_cp_first": ('owed.append(((g["rank"], "CP" not in g["tags"], -age),', 'owed.append(((g["rank"], "CP" in g["tags"], -age),',
+                      "rank: inside one rank the critical path is ahead of outside"),
+    "rank_dropped": ('owed.append(((g["rank"], "CP" not in g["tags"], -age),', 'owed.append((("CP" not in g["tags"], -age),',
+                     "rank: a hotfix group ahead of a critical-path one (roster_lib.dispatch_rank)"),
+}
+
+
+def read_world_checks() -> "dict[str, bool]":
+    """read_world over a throwaway origin: the roster and critical-path file on main, the watched
+    groups' refs and two pull-request heads; gh answered by a fake, every git read real."""
+    sys.path.insert(0, str(SEAT.parents[2] / "tests"))
+    from throwaway_git import throwaway_git_clone, throwaway_git_environ, throwaway_git_init
+    res = {}
+    with tempfile.TemporaryDirectory() as d, throwaway_git_environ():
+        o, c = Path(d) / "o", Path(d) / "c"
+        throwaway_git_init(o, "-q", "-b", "main")
+        g = lambda *a, cwd=o: subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
+
+        def commit(branch, name, text, when):
+            g("checkout", "-q", "--orphan" if branch != "main" else "-B", branch)
+            g("rm", "-rqf", "--ignore-unmatch", ".")
+            (o / name).parent.mkdir(parents=True, exist_ok=True)
+            (o / name).write_text(text)
+            g("add", name)
+            env = {"GIT_COMMITTER_DATE": f"@{when} +0000", "GIT_AUTHOR_DATE": f"@{when} +0000"}
+            subprocess.run(["git", "commit", "-qm", branch], cwd=o, check=True, capture_output=True,
+                           env={**__import__("os").environ, **env})
+            return g("rev-parse", "HEAD")
+        roster = {"groups": [
+            {"group": "R11-CPG", "resume": {"stage": "not-started", "branch": "fix/r11-cpg"}},
+            {"group": "R11-OUT", "source": "outside", "resume": {"stage": "not-started", "pr": 12}},
+            {"group": "R11-OFF", "resume": {"stage": "not-started"}},
+            {"group": "R11-SHUT", "source": "outside", "resume": {"stage": "done"}}]}
+        commit("main", f"{roster_lib.ROSTERS_DIR}/wave-r11-groups.json", json.dumps(roster), 1_000)
+        (o / roster_lib.CRITICAL_PATH_NAME).write_text(json.dumps({"critical": ["R11-CPG"]}))
+        g("add", "-A")
+        g("commit", "-qm", "cp")
+        h11 = commit("work11", "x", "11", 2_000)
+        h12 = commit("work12", "x", "12", 3_000)
+        v12 = commit("verdict/12", "VERDICT.md", f"Fix review: merge {h12}\n", 4_000)
+        r11 = commit("dispatch/reviewer-rev-11", "PROMPT.md", f"CLOUD REVIEWER seat for PR #11, at head {h11}.\nRole\n", 5_000)
+        dz = commit("design/R11-OUT", "design.md", "# a design\n", 6_000)
+        commit("design/R11-OFF", "design.md", "# not watched\n", 6_000)
+        hf = commit("handoff/r11-cpg", "x", "h", 7_000)
+        g("update-ref", "refs/pull/11/head", h11)
+        g("update-ref", "refs/pull/12/head", h12)
+        g("checkout", "-q", "main")
+        throwaway_git_clone(o, c, "-q")
+        led = Path(d) / "fired.log"
+        led.write_text("2026-11-15T11:30:00Z FIRED reviewer #11\n")
+        prs = [{"number": 11, "headRefOid": h11, "headRefName": "fix/r11-cpg", "reviews": []},
+               {"number": 12, "headRefOid": h12, "headRefName": "patch-1", "reviews": [
+                   {"state": "APPROVED", "submittedAt": "2026-11-15T10:00:00Z", "commit": {"oid": h12}},
+                   {"state": "APPROVED", "submittedAt": "2026-11-15T11:00:00Z", "commit": {"oid": h11}},
+                   {"state": "CHANGES_REQUESTED", "submittedAt": "2026-11-15T12:00:00Z", "commit": {"oid": h12}}]},
+               {"number": 13, "headRefOid": h11, "headRefName": "fix/r11-off", "reviews": []}]
+        calls = []
+
+        def fake(answer):
+            def run(argv, cwd=None):
+                calls.append(argv)
+                return answer if argv[0] == "gh" else sh(argv, cwd)
+            return run
+        groups, got_prs, refs, ctime, first, rows = read_world("o/r", str(c), str(led), None, fake((0, json.dumps(prs))))
+        res["read_world: the watched set is the open critical-path and outside groups, nothing else"] = (
+            sorted(groups) == ["R11-CPG", "R11-OUT"] and groups["R11-CPG"]["tags"] == ["CP"]
+            and groups["R11-OUT"]["tags"] == ["OUTSIDE"] and groups["R11-CPG"]["topic"] == "r11-cpg")
+        res["read_world: a pull request maps by branch, else by resume.pr; an unwatched group's is dropped"] = (
+            [(p["number"], p["gid"]) for p in got_prs] == [(11, "R11-CPG"), (12, "R11-OUT")]
+            and groups["R11-OUT"]["prs"] == [12])
+        res["read_world: approval is the newest APPROVED review at the head, never at another commit"] = (
+            got_prs[1]["approved_t"] == _epoch("2026-11-15T10:00:00Z") and got_prs[0]["approved_t"] is None)
+        res["read_world: the watched groups' refs, never an unwatched group's"] = (
+            sorted(refs) == ["design/R11-OUT", "dispatch/reviewer-rev-11", "handoff/r11-cpg", "verdict/12"])
+        res["read_world: commit times from git, for every ref tip and pull-request head"] = (
+            [ctime.get(x) for x in (h11, h12, v12, r11, dz, hf)] == [2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0]
+            and [p["head_t"] for p in got_prs] == [2000.0, 3000.0])
+        res["read_world: each tip's note is read to its first line"] = (
+            first.get(v12) == f"Fix review: merge {h12}" and first.get(r11) == f"CLOUD REVIEWER seat for PR #11, at head {h11}."
+            and first.get(dz) == "# a design" and hf not in first)
+        res["read_world: the fire ledger's stamps are epochs"] = rows == [(_epoch("2026-11-15T11:30:00Z"), "2026-11-15T11:30:00Z FIRED reviewer #11")]
+        res["read_world: gh is asked for the open pull requests of the repo given"] = any(
+            a[:3] == ["gh", "pr", "list"] and "o/r" in a and "open" in a for a in calls)
+        for name, answer in (("a gh refusal", (1, "HTTP 403")), ("a non-list answer", (0, "{}"))):
+            try:
+                read_world("o/r", str(c), str(led), None, fake(answer))
+                res[f"read_world: {name} is Unreadable, never an empty list"] = False
+            except Unreadable as e:
+                res[f"read_world: {name} is Unreadable, never an empty list"] = "open pull requests" in str(e)
+        def failing(word, out=None):
+            def run(argv, cwd=None):
+                if argv[0] == "gh":
+                    return 0, json.dumps(prs)
+                if word in argv:
+                    return (0, out) if out is not None else (1, f"{word} refused")
+                return sh(argv, cwd)
+            return run
+        for word, out, why in (("ls-remote", None, "ls-remote"), ("fetch", None, "fetch"), ("log", None, "commit times"),
+                               ("log", f"{h12} 3000\n", "#11's head")):
+            try:
+                read_world("o/r", str(c), str(led), None, failing(word, out))
+                ok = False
+            except Unreadable as e:
+                ok = str(e).startswith(why)
+            res[f"read_world: a failed {word}{' missing a head' if out else ''} is Unreadable ({why})"] = ok
+        try:
+            read_world("o/r", str(c), str(led), "refs/heads/nope", fake((0, "[]")))
+            res["read_world: an unreadable roster ref is Unreadable"] = False
+        except Unreadable as e:
+            res["read_world: an unreadable roster ref is Unreadable"] = str(e).startswith("roster at refs/heads/nope")
+        g("checkout", "-q", "main", cwd=c)
+        (c / roster_lib.CRITICAL_PATH_NAME).write_text("not json")
+        g("commit", "-qam", "bad", cwd=c)
+        try:
+            read_world("o/r", str(c), str(led), "HEAD", fake((0, "[]")))
+            res["read_world: an unreadable critical-path file is Unreadable, never an empty set"] = False
+        except Unreadable as e:
+            res["read_world: an unreadable critical-path file is Unreadable, never an empty set"] = "critical path" in str(e)
+    return res
+
+
+def self_test() -> int:
+    import importlib.util
+    res = cases(sys.modules[__name__])
+    res.update(read_world_checks())
+    # the moved FIRE-OWED level and fired-ledger read, against the tick's own fixture shape
+    with tempfile.TemporaryDirectory() as d:
+        now = datetime.datetime(2026, 11, 15, 12, 0, tzinfo=datetime.timezone.utc)
+        pf = Path(d) / "payload-fix-86-r1.json"
+        pf.write_text("{}")
+        old = (now - datetime.timedelta(minutes=60)).timestamp()
+        os.utime(pf, (old, old))
+        led = Path(d) / "fired.log"
+        led.write_text("2026-11-15T11:30:00Z FIRED payload-fix-86-r1.json\nno fire here\nFIRED #3 unstamped\n")
+        rows = fired(led)
+        res["fired: FIRED lines only, stamped as UTC, an unstamped one None"] = (
+            [w and w.isoformat() for w, _ in rows] == ["2026-11-15T11:30:00+00:00", None])
+        res["fire_owed: an unfired payload past its grace owes; one a FIRED line names does not"] = (
+            len(fire_owed(d, [], now)) == 1 and fire_owed(d, rows, now) == []
+            and " rendered 60m ago" in (fire_owed(d, [], now) or [""])[0])
+        edge = (now - datetime.timedelta(minutes=FIRE_GRACE_MIN)).timestamp()
+        os.utime(pf, (edge, edge))
+        res["fire_owed: a payload exactly FIRE_GRACE_MIN old is still inside its grace"] = fire_owed(d, [], now) == []
+        res["graces are carry 4's figures, UNFIRED at FIRE_GRACE_MIN; the tick's two windows unchanged (120, 15)"] = (
+            GRACE_MIN == {"merge-no-approval": 10, "approved-unmerged": 45, "blocked-no-fire": 15, "head-no-dispatch": 25,
+                          "UNFIRED": 15, "DESIGN-REVIEW-OWED": 10, "FIXER-OWED": 10, "SEAT-SILENT": 90}
+            and (SEAT_WINDOW_MIN, FIRE_GRACE_MIN) == (120, 15))
+        edge = now - datetime.timedelta(minutes=SEAT_WINDOW_MIN)
+        on = lambda rows, age: seat_on(7, ["r11-a"], {"handoff/r11-a": "a" * 40} if age is not None else {}, rows, now,
+                                       lambda ref, sha: age, lambda sha: None)
+        res["seat_on: a fire or a ref move exactly SEAT_WINDOW_MIN old is still a seat; one minute older is not"] = (
+            on([(edge, "FIRED #7")], None) and not on([(edge - datetime.timedelta(minutes=1), "FIRED #7")], None)
+            and on([], SEAT_WINDOW_MIN) and not on([], SEAT_WINDOW_MIN + 1))
+        res["fire_names: #3 names PR 3, never PR 30; a topic matches as a whole word"] = (
+            fire_names(3, [], "FIRED #3 x") and not fire_names(3, [], "FIRED #30")
+            and fire_names(9, ["r11-a"], "FIRED fixer R11-A") and not fire_names(9, ["r11-a"], "FIRED r11-ab"))
+    import contextlib
+    import io
+    real = globals()["read_world"]
+    try:
+        for answer, rc_want, out_want in ((Unreadable("open pull requests: x"), 2, "cp-owed: UNREADABLE open pull requests: x\n"),
+                                          (_aged(_world("merge-no-approval", True)[:6]), 0, "CP-OWED merge-no-approval #11 ")):
+            def stub(*a, answer=answer):
+                if isinstance(answer, Exception):
+                    raise answer
+                return answer
+            globals()["read_world"] = stub
+            buf = io.StringIO()
+            with contextlib.redirect_stdout(buf):
+                rc = main(["cp-owed", "--fired", "/dev/null"])
+            res[f"main: cp-owed exits {rc_want} printing {out_want.split(':')[0].split(' #')[0].strip()}"] = (
+                rc == rc_want and buf.getvalue().startswith(out_want))
+        with contextlib.redirect_stderr(io.StringIO()):
+            try:
+                main(["cp-owed"])
+                res["main: cp-owed without --fired is a usage error"] = False
+            except SystemExit as e:
+                res["main: cp-owed without --fired is a usage error"] = e.code == 2
+    finally:
+        globals()["read_world"] = real
+    failed = 0
+    for name, ok in res.items():
+        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
+        failed += not ok
+    total = len(res)
+    full = Path(__file__).read_text()
+    cut = full.index(SELF_TEST_MARK)  # a site is counted and edited above the self-test only
+    src, rest = full[:cut], full[cut:]
+    with tempfile.TemporaryDirectory() as d:
+        for i, (mname, (old, new, case)) in enumerate(MUTANTS.items()):
+            total += 1
+            if src.count(old) != 1:
+                print(f"  FAIL mutant {mname}: its site appears {src.count(old)} times")
+                failed += 1
+                continue
+            p = Path(d) / f"owed_watch_m{i}.py"
+            p.write_text(src.replace(old, new) + rest)
+            spec = importlib.util.spec_from_file_location(f"owed_watch_m{i}", p)
+            m = importlib.util.module_from_spec(spec)
+            try:
+                spec.loader.exec_module(m)
+                killed = cases(m).get(case) is False
+            except Exception as e:  # a crash is no kill
+                print(f"    mutant {mname} crashed: {e.__class__.__name__}: {e}")
+                killed = False
+            print(f"  {'ok  ' if killed else 'FAIL'} mutant {mname} killed by: {case}")
+            failed += not killed
+    print(f"owed_watch self-test: {total} checks, {failed} failed")
+    return 1 if failed else 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
diff --git a/tools/audit/seat/pr_cap.py b/tools/audit/seat/pr_cap.py
index 72acbac659..6432c2cbec 100644
--- a/tools/audit/seat/pr_cap.py
+++ b/tools/audit/seat/pr_cap.py
@@ -4,7 +4,7 @@
     python3 -I tools/audit/seat/pr_cap.py info --repo OWNER/REPO
     python3 -I tools/audit/seat/pr_cap.py dispatch-gate [--repo PATH]
         [--roster-file PATH | --roster-ref GITREF [--roster-path PATH]]
-        [--over-cap REASON]
+        [--over-cap REASON] [--machinery OWNER/REPO]
     python3 -I tools/audit/seat/pr_cap.py --self-test
 
 THE RULING (tvofi, 2026-10-20, moving 2026-10-18's open-PR cap; restated
@@ -25,6 +25,15 @@ by it. Opening is how work LEAVES work-in-progress, not how it enters. So:
     `wip_groups`, M from `counted`, flagged at or over the cap. It does not
     dispatch and does not gate; it reports.
 
+THE PRODUCTION SLOTS (tvofi, 2026-11-01; `dev/audit/README.md`, "Production
+share"). Of the owner's open-pull-request slots (`DEFAULT_CAPS` in
+`tools/plan/replan.py`), PRODUCTION_SLOTS are reserved for production: a pull
+request whose diff touches a product path (`machinery_ratchet.is_product`, the
+one predicate) is production, any other machinery. `dispatch-gate --machinery
+OWNER/REPO` refuses a machinery group once machinery and unread pull requests
+fill the rest; a production group never waits for a machinery slot.
+`orchestrator_tick.py` prints `class_line` every pass.
+
 WHAT "BOT" MEANS HERE, a design choice. Every pull request this repository's
 seats open is authored by the hpo-author App (decision 0011), which GitHub
 reports as a bot. Excluding every bot would count nothing, so a bot is an author
@@ -37,6 +46,8 @@ Lines (one per call, on stderr; exit 0 to pass, 1 to refuse, 2 for usage):
       or --over-cap <reason>
   dispatch: OVER-CAP: WIP 6/6, overridden: <reason> (G1, ...)
   open_pr: 20 open PRs; the cap gates dispatch, not opening
+  dispatch: REFUSE: machinery slots: 10/10 (#1, ...); production holds the
+      other 10
 """
 from __future__ import annotations
 
@@ -58,6 +69,9 @@ COORDINATOR_PATH = "custom_components/heatpump_optimizer/coordinator.py"
 COORDINATOR_CAP = 2
 FIELDS = "number,title,author"
 SELF = os.path.abspath(__file__)
+ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(SELF))))
+PRODUCTION_SLOTS = 10  # the owner's count, 2026-11-01
+GH_FILES_LIMIT = 100  # gh lists at most this many files per pull request
 _RL = None
 
 
@@ -189,6 +203,96 @@ def coordinator_prs(files_by_pr: dict) -> "tuple[list, list]":
     return hit, unread
 
 
+def _load(name: str, rel: str):
+    """A module of the tree by path, None when this copy has no tree beside it
+    (pr_args.sh copies this file alone into a seat directory)."""
+    p = os.path.join(ROOT, rel)
+    if not os.path.isfile(p):
+        return None
+    spec = importlib.util.spec_from_file_location(name, p)
+    mod = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(mod)
+    return mod
+
+
+def product_rule():
+    """machinery_ratchet.is_product, or None when unreadable."""
+    m = _load("machinery_ratchet_pr_cap", "tools/audit/machinery_ratchet.py")
+    return getattr(m, "is_product", None)
+
+
+def open_slots(caps: "dict | None" = None) -> "int | None":
+    """replan.py's DEFAULT_CAPS slots (or `caps`'s), None when unreadable or
+    not above PRODUCTION_SLOTS, which would leave machinery no slot to count."""
+    if caps is None:
+        caps = getattr(_load("replan_pr_cap", "tools/plan/replan.py"), "DEFAULT_CAPS", None) or {}
+    v = caps.get("slots")
+    return v if isinstance(v, int) and v > PRODUCTION_SLOTS else None
+
+
+def by_class(prs: list, files_by_pr: dict, is_product) -> dict:
+    """{production, machinery, unread: [PR numbers]}: a diff it cannot read is
+    neither, never machinery by default nor production."""
+    out = {"production": [], "machinery": [], "unread": []}
+    for pr in prs:
+        fs = files_by_pr.get(pr["number"])
+        k = "unread" if fs is None else (  # mut:classunread
+            "production" if any(is_product(f) for f in fs) else "machinery")
+        out[k].append(pr["number"])
+    return out
+
+
+def class_line(classes: dict, slots: int) -> "tuple[str, bool]":
+    """(the tick's line, flagged): flagged once machinery and unread fill the
+    slots production does not hold."""
+    free = slots - PRODUCTION_SLOTS
+    m, u = len(classes["machinery"]), len(classes["unread"])
+    text = (f"open PRs by class: {len(classes['production'])} production, {m} machinery"
+            + (f", {u} unread" if u else "")
+            + f"; machinery slots {m + u}/{free} ({PRODUCTION_SLOTS} of {slots} reserved for production)")
+    return text, m + u >= free  # mut:classflag
+
+
+def machinery_gate(classes: "dict | None", why: str, slots: "int | None") -> "tuple[int, str]":
+    """(exit status, line) for dispatching a machinery group: refused once
+    machinery and unread pull requests fill the slots production does not hold."""
+    if classes is None or slots is None: return 1, f"dispatch: REFUSE: machinery slots: unread ({why}); no pass"  # mut:mslotunread
+    free = slots - PRODUCTION_SLOTS
+    taken = classes["machinery"] + classes["unread"]
+    ids = ", ".join(f"#{n}" for n in taken)
+    if len(taken) < free:
+        return 0, f"dispatch: machinery slots {len(taken)}/{free}: may dispatch a machinery group"
+    return 1, (f"dispatch: REFUSE: machinery slots: {len(taken)}/{free} ({ids}); "  # mut:mslot
+               f"production holds the other {PRODUCTION_SLOTS}")
+
+
+def read_classes(repo: str, gh=None, rule=None) -> "tuple[dict | None, str]":
+    """(by_class over the open pull requests read with their files, '') or
+    (None, why): a list or a file list gh may have truncated is unread."""
+    rule = rule or product_rule()
+    if rule is None:
+        return None, "machinery_ratchet.is_product is not beside this copy"
+    argv = ["pr", "list", "--repo", repo, "--state", "open", "--limit", "200",
+            "--json", FIELDS + ",files"]
+    if gh is not None:
+        rc, out = gh(argv)
+    else:
+        r = subprocess.run(["gh", *argv], capture_output=True, text=True)
+        rc, out = r.returncode, r.stdout + r.stderr
+    if rc != 0:
+        return None, f"gh exited {rc}: {out.strip()[-160:]}"
+    try:
+        prs = json.loads(out)
+    except ValueError as e:
+        return None, f"not JSON: {e}"
+    if not isinstance(prs, list) or len(prs) >= 200:
+        return None, "not a list, or 200 or more returned"
+    prs = counted(prs)
+    files = {p["number"]: (None if len(p.get("files") or []) >= GH_FILES_LIMIT
+                           else [f.get("path", "") for f in p.get("files") or []]) for p in prs}
+    return by_class(prs, files, rule), ""
+
+
 def _doc_stage() -> dict:
     """The first named group of stages, for the self-test's rosters."""
     return {"groups": [{"group": f"G{i}", "resume": {"stage": s}}
@@ -310,6 +414,56 @@ def self_test() -> int:
     hit, unread = coordinator_prs({1: [COORDINATOR_PATH], 2: ["x.py"], 3: None})
     ck("coordinator PRs: the diff that touches it counts, an unread diff is named apart",
        hit == [1] and unread == [3])
+    # ---- the production slots -------------------------------------------
+    prod = lambda f: f.startswith("custom_components/")
+    board = [{"number": i, "title": "t", "author": app} for i in range(1, 5)]
+    cls = by_class(board, {1: ["custom_components/a.py", "tools/x.py"], 2: ["tools/x.py"],
+                           3: [], 4: None}, prod)
+    ck("by class: a product path makes production, none machinery, an unread diff neither",
+       cls == {"production": [1], "machinery": [2, 3], "unread": [4]})
+    text, flag = class_line(cls, 13)
+    ck("the tick line names each class and the machinery slots, unread counted against them",
+       text == "open PRs by class: 1 production, 2 machinery, 1 unread; machinery slots 3/3 "
+       "(10 of 13 reserved for production)" and flag)
+    ck("null control: below the machinery slots the line is not flagged",
+       class_line(cls, 14)[1] is False)
+    rc, line = machinery_gate(cls, "", 13)
+    ck("a machinery group is refused once machinery and unread fill the free slots",
+       rc == 1 and line == "dispatch: REFUSE: machinery slots: 3/3 (#2, #3, #4); production holds the other 10")
+    ck("null control: one free machinery slot passes", machinery_gate(cls, "", 14)[0] == 0)
+    ck("unread classes or slots refuse, never a clean zero",
+       machinery_gate(None, "gh exited 1", 20)[0] == 1 and machinery_gate(cls, "", None)[0] == 1)
+    many = [{"path": f"tools/{i}"} for i in range(GH_FILES_LIMIT)]
+    got, _ = read_classes("o/r", gh=lambda a: (0, json.dumps(
+        [{"number": 7, "title": "t", "author": app, "files": many},
+         {"number": 8, "title": "t", "author": app, "files": many[:1]}])), rule=prod)
+    ck("a file list at gh's limit may be truncated: unread, not machinery",
+       got == {"production": [], "machinery": [8], "unread": [7]})
+    ck("slots at or below PRODUCTION_SLOTS are unread, never a negative allowance; 11 reads",
+       [open_slots({"slots": v}) for v in (10, 9, True, 11)] == [None, None, None, 11])
+    import contextlib, io
+    g = globals()
+    saved = g["read_classes"], g["open_slots"]
+    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
+        json.dump(roster(["done"]), fh)
+        done = fh.name
+    try:
+        g["open_slots"] = lambda: 13
+        outs = []
+        for seen, argv in ((cls, ["--machinery", "o/r"]), (by_class([], {}, prod), ["--machinery", "o/r"]),
+                           (cls, [])):
+            g["read_classes"] = lambda slug, _c=seen: (_c, "") if slug == "o/r" else (None, slug)
+            err = io.StringIO()
+            with contextlib.redirect_stderr(err):
+                outs.append((main(["dispatch-gate", "--roster-file", done, *argv]), err.getvalue()))
+    finally:
+        g["read_classes"], g["open_slots"] = saved
+        os.unlink(done)
+    ck("dispatch-gate --machinery refuses a full board after the WIP gate passes",
+       outs[0][0] == 1 and "REFUSE: machinery slots: 3/3 (#2, #3, #4)" in outs[0][1])
+    ck("null controls: an empty board passes it, and no --machinery never reads the board",
+       outs[1][0] == 0 and "machinery slots 0/3" in outs[1][1]
+       and outs[2][0] == 0 and "machinery" not in outs[2][1])
     print(f"pr_cap self-test: {total} checks, {failed} failed")
     return 1 if failed else 0
 
@@ -342,6 +496,10 @@ def main(argv: list) -> int:
         rc, line = dispatch_gate(roster, where, wip_cap_from_env(),
                                  _opt(argv, "--over-cap"))
         print(line, file=sys.stderr)
+        slug = _opt(argv, "--machinery")
+        if rc == 0 and slug is not None:
+            rc, line = machinery_gate(*read_classes(slug), open_slots())
+            print(line, file=sys.stderr)
         return rc
     print(__doc__.split("\n\n")[1], file=sys.stderr)
     return 2
diff --git a/tools/audit/seat/review_packet.py b/tools/audit/seat/review_packet.py
index 55b0500f98..13cd30a344 100644
--- a/tools/audit/seat/review_packet.py
+++ b/tools/audit/seat/review_packet.py
@@ -99,6 +99,7 @@ ROOT = Path(__file__).resolve().parents[3]
 sys.path.insert(0, str(ROOT / "tools" / "audit" / "seat"))
 import proof_watch  # noqa: E402  (the one Python reader of the verdict grammar)
 import ref_privacy  # noqa: E402
+import topic_grammar  # noqa: E402  (the handoff topics a PR branch carries)
 
 class Unavailable(Exception):
     """The packet's INPUTS are absent in this seat, not its facts bad.
@@ -324,11 +325,9 @@ def handoff_hot(touched: set[str], open_prs: list[dict], boarded: set[int], topi
     return hot_file_refusals(touched, open_prs, boarded, this_pr) + ([note] if note else [])
 
 
-def handoff_topics(branch: str) -> list[str]:
-    """The handoff topics a pull request's branch can carry: `fix/<t>` or
-    `fix/<t>-pr`, `open_pr.sh`'s two spellings; none for any other shape."""
-    t = branch[len("fix/"):] if branch.startswith("fix/") else ""
-    return [x for x in ([t, t[:-len("-pr")]] if t.endswith("-pr") else [t]) if x]
+# The handoff topics a pull request's branch can carry: the topic grammar's, which
+# cloud_relay.sh's handoff arm reads too (one owner, so the two cannot disagree on #3358's shape).
+handoff_topics = topic_grammar.handoff_topics
 
 
 def head_note_repair(head: str, branch: str | None) -> str:
diff --git a/tools/audit/seat/sweep_template.md b/tools/audit/seat/sweep_template.md
index 1a9f28dbae..01ad1ea8b9 100644
--- a/tools/audit/seat/sweep_template.md
+++ b/tools/audit/seat/sweep_template.md
@@ -51,7 +51,7 @@ rendered text that no overlay value supplied.
 | `train_state` | optional: the merge train's state dir; the `cancel-sweep` row passes it as `--train-state`, so a pull request in the train's queue or spool is never cancelled for a priority run; empty leaves the flag out |
 | `gantt_roster` | the roster the beat's `gantt` row reads, as `<branch>:<path>` (fetched to `refs/gantt/roster`, never a local branch) |
 | `gantt_acks` | the Gantt acks file `sweep_gantt.py --acks` reads, one `<ISO> <KEY> act\|defer\|accept [until=<ISO>] <reason>` line per answered slip |
-| `fire_ledger` | the session's fire ledger, one line per seat fired with its leading UTC stamp, which the `gantt` and `verdict-audit` rows hand on as `--fired` (a line within 12 h holds the pull request or topic it names) |
+| `fire_ledger` | the session's fire ledger, one line per seat fired with its leading UTC stamp, which the `gantt`, `verdict-audit` and `cp-owed` rows hand on as `--fired` (a line within 12 h holds the pull request or topic it names) |
 | `sweep_record` | optional: the day's sweep record file, rendered `scorecard.py --sweep-record FILE`; whose `recycle` lines of the standing dispatch and triage seats the `scorecard` row counts as K (absent: K prints unread) |
 | `train_glob` | the glob of live train logs `verdict_audit.py --train-glob` reads (a log modified within 3 h holds its queued pull requests) |
 | `train_log` | the live merge train's `train.log` (`$HOME/.local/state/hpo/merge_train/train.log`), which the beat's `bottleneck` and `plan-beat` rows hand on as `--train-log` (the skip-share alert and the plan page's train-skips table) |
@@ -74,7 +74,7 @@ ORCHESTRATOR SWEEP, round {{round}}, repository {{repo}}. Read {{seat_ledger}} f
 
 (4b) Record beat. The beat's `plan-beat` row runs `python3 tools/plan/replan.py --out {{plan_json}} --slots {{plan_slots}} --seats {{plan_seats}} {{plan_coordinator_cap}}`, then `tools/audit/seat/state_docs.py --push --mirror {{state_mirror}} --plan {{plan_json}}`, every 30 minutes, merge or none; it publishes the plan page as `PLAN.html` in the plan table's commit at the state ref and mirrors it as {{plan_page}}, republished at the same path. A `plan-beat: PLAN UNAVAILABLE` line in {{digest}}/digest.txt is the page UNAVAILABLE (the other docs are still pushed; the ref keeps the last good page): answer its reason and re-run that replan, never hand-run `plan_page.py` around the refusal; a `plan-beat: REFUSED` line is the docs push's own refusal. A `plan-beat: PLAN MOVED` line is a page that changed since the last beat: republish it at {{plan_page}} this sweep (owner ruling, 2026-11-06: every sweep updates the plan artifact). The beat's `gantt` row compares that plan with the Gantt baseline through `tools/audit/seat/sweep_gantt.py`: it reads the roster at {{gantt_roster}}, the fire ledger {{fire_ledger}} and the acks file {{gantt_acks}}; each `GANTT-SLIP` line of {{digest}}/digest.txt is owed `act`, `defer` or `accept`, appended to {{gantt_acks}} (owner ruling, 2026-11-01). The beat's `scorecard` row runs `python3 tools/audit/seat/scorecard.py report {{sweep_record}}` (its other arguments are the beat's own), report-only; K prints unread when no sweep record is given.
 
-(4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.
+(4c) Open pull requests. Reconcile every open pull request to one bucket, with its reason: in train, review out, fixer out, CI wait, or owner-held; none waits without one; critical path first. The beat's `verdict-audit` row (`tools/audit/seat/verdict_audit.py`, reading {{fire_ledger}}, the train logs {{train_glob}} and the skip file {{unheld_skip}}) prints an `UNHELD` line in {{digest}}/digest.txt for each pull request whose next step nobody holds: give each a holder this sweep, or put a pull request held by an owner ruling on {{unheld_skip}} (owner ruling, 2026-11-06: no pull request waits unheld). The beat's `cp-owed` row (`tools/audit/seat/owed_watch.py`, reading {{fire_ledger}}) prints a `CP-OWED <arm> <subject>` line for each step of a critical-path or outside group, or of its pull request, past its grace: act on each this sweep, critical path and outside first (owner directive, tvofi 2026-11-09: never let the critical path or outside pull requests slip). The beat's `bottleneck` row (`tools/audit/seat/bottleneck_check.py`, reading the train log {{train_log}} and the cap {{plan_slots}}) prints a `BOTTLENECK:` line in {{digest}}/digest.txt once per trip of a flow metric past the owner's threshold, with a suggested action: decide whether to act on it this sweep; the line takes no action itself (owner request, tvofi 2026-11-07). A `BOTTLENECK-UNREADABLE:` line is a metric the alert cannot see.
 
 (4d) Queue priority, for the train, review, fixer and CI queues alike: a push to main; then hotfix; then accepted outside issues and contributions (a roster group with `source: outside`, which `roster_edit.py set-source` writes) together with the critical path, one rank unordered between them (owner rulings tvofi 2026-11-07, triage P420, and 2026-11-08); then production pull requests with instrument pull requests saving 12 h or more; then other instruments by savings. A group's critical-path standing is the roster's `critical` list (`tools/audit/seat/roster_lib.py` `critical_path`); hotfix and top-rank standing are `roster_lib.dispatch_rank`'s, which `tools/pr/gate_priority.py` (hotfix the lease's top band, outside and critical path the next) and the tick's OWED order apply; `open_driver.py`, the train's drain and `tools/plan/replan.py`'s `dispatch_tier` (the plan page's tier) hold the same order from `roster_lib.is_outside`.
 
diff --git a/tools/audit/seat/tick_loop.sh b/tools/audit/seat/tick_loop.sh
index 0b35a54fa4..137c9ddafc 100644
--- a/tools/audit/seat/tick_loop.sh
+++ b/tools/audit/seat/tick_loop.sh
@@ -20,19 +20,31 @@
 #      the checkout this script runs from, and behind = the commits in HEAD..origin/main
 #      touching tools/audit/seat, tools/pr or tools/audit/carry_audit.py (the code the loop
 #      runs). Past HPO_TICK_STALE_BOUND (default 25), or on any commit touching tick_loop.sh
-#      or cloud_relay.sh, the loop restarts: with the relay lock free and the tree clean and
-#      detached, it checks out origin/main detached, runs `bash -n` on the new tick_loop.sh
-#      and execs it with the same arguments -- between passes, at most once per pass, never
-#      a fast-forward in place (bash reads a running script as it goes). When it cannot, one
+#      or cloud_relay.sh, the loop restarts: with the relay lock free and the tree clean, it
+#      checks out origin/main -- detached, or for a branch-backed checkout holding no commit
+#      outside origin/main (worktree_gc.sh leaves those), `checkout -B <its branch> origin/main`
+#      -- runs `bash -n` on the new tick_loop.sh and execs it with the same arguments -- between
+#      passes, at most once per pass, never a fast-forward in place (bash reads a running script
+#      as it goes). A branch with commits of its own is never moved. When it cannot, one
 #        TICK-STALE <utc> code=<sha7> behind=<n>: <why>; the relay and sweep arms are skipped
 #      line precedes the banner, the arms that act are skipped (relay=stale) and the board
-#      is still written: never exit, never act from stale code. A failed fetch is
-#      behind=unknown and the pass runs as before. HPO_TICK_CODE_DIR replaces the checkout.
+#      is still written: never exit, never act from stale code. A stale state persisting into
+#      a second consecutive pass (counted in <out>.stale) also ends the board with
+#        -> OWED relay-skipped code=<sha7> behind=<n>: <why> (stale <k> consecutive passes)
+#      so the board says what only the loop log said (S14-TICK-STALE-SILENT: ~4 h of relay dark
+#      over three episodes); one stale pass (a relay holding the lock) raises none. A failed
+#      fetch is behind=unknown and the pass runs as before. HPO_TICK_CODE_DIR replaces the checkout.
 # One banner line per pass on stdout:
 #   TICK-PASS <utc> relay=<ok|rc=N|running|absent|stale> tick=<rc> code=<sha7|none> behind=<n|unknown> out=<file>
 # The relay's output is printed when it is reaped; one that finished after its
 # pass's wait is reaped by the next pass, with its own line before that banner:
 #   TICK-RELAY <utc> relay=<ok|rc=N> started=<utc>
+# THE RELAY GAP (S14-RELAY-CADENCE). In the sleep between passes the loop reaps a finished
+# relay (its TICK-RELAY line) and starts the next one under the same lock once
+# HPO_TICK_RELAY_GAP seconds (default 120, digits only) have passed since that relay ended,
+# so a relay that ends early does not sit idle until the next tick pass (7 min observed).
+# The tick keeps --interval: a tick pass costs ~290 core API calls, a relay pass far fewer.
+# A stale pass starts none in its sleep; a relay still in flight is left alone.
 # A failing relay pass is reported and the tick still runs; a failing tick is
 # reported and the loop goes on. The loop drives; the tick itself stays read-only.
 #   3. --sweep only (R10-FLOW-AUTOTRAIN; off by default, and the first live sweep
@@ -97,7 +109,7 @@ if os.path.exists(r + ".rc"): sys.exit(76)
 t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
 with open(r + ".log", "w") as log:
     rc = subprocess.call(sys.argv[2:], stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
-with open(r + ".rc.part", "w") as o: o.write("%d %s\n" % (rc, t))
+with open(r + ".rc.part", "w") as o: o.write("%d %s %d\n" % (rc, t, int(time.time())))
 os.replace(r + ".rc.part", r + ".rc")'
 
 # The relay lock is free: rc 0 (the holder's flock, tried and released at once).
@@ -114,7 +126,7 @@ behind_count() { # <checkout> <paths...>: the commits in HEAD..origin/main touch
 }
 
 fresh_check() { # <out>: sets code, behind and stale (the acting arms are skipped); may exec the new loop
-  local top self why bound=${HPO_TICK_STALE_BOUND:-25}
+  local top self why bound=${HPO_TICK_STALE_BOUND:-25} br own
   case $bound in ''|*[!0-9]*) bound=25 ;; esac
   code=none behind=unknown stale=
   top=$(git -C "${HPO_TICK_CODE_DIR:-$HERE}" rev-parse --show-toplevel 2>/dev/null) || return 0
@@ -126,45 +138,67 @@ fresh_check() { # <out>: sets code, behind and stale (the acting arms are skippe
   self=$(behind_count "$top" "${SELF_PATHS[@]}") || self=1  # never-empty: SELF_PATHS is the literal two-path list above
   [ "$behind" -gt "$bound" ] || [ "$self" -gt 0 ] || return 0  # mut:bound
   stale=1
+  # A branch-backed checkout (worktree_gc.sh removes clean old detached worktrees) restarts on its own
+  # branch when it holds no commit outside origin/main; one with commits of its own is never moved.
+  br=$(git -C "$top" symbolic-ref -q --short HEAD 2>/dev/null) || br=
+  [ -z "$br" ] || own=$(git -C "$top" rev-list --count origin/main..HEAD 2>/dev/null) || own=unknown
   if [ -n "${HPO_TICK_RESTARTED:-}" ]; then why="restarted once this pass"
   elif ! python3 -I -c "$LOCK_FREE" "$1.relay.lock"; then why="a relay is in flight (the lock is held)"  # mut:lock
-  elif git -C "$top" symbolic-ref -q HEAD >/dev/null; then why="a branch is checked out, not a detached head"
+  elif [ -n "$br" ] && [ "$own" != 0 ]; then why="the branch $br holds $own commit(s) origin/main lacks; it is never moved"  # mut:branchown
   elif [ -n "$(git -C "$top" status --porcelain --untracked-files=no)" ]; then why="the tree is dirty"  # mut:dirty
   elif ! git -C "$top" show origin/main:tools/audit/seat/tick_loop.sh | bash -n 2>/dev/null; then  # mut:syntax
     why="bash -n refuses origin/main's tick_loop.sh"
-  elif ! git -C "$top" checkout -q --detach origin/main; then why="the checkout failed"
+  elif ! if [ -n "$br" ]; then git -C "$top" checkout -q -B "$br" origin/main; else git -C "$top" checkout -q --detach origin/main; fi; then  # mut:branchrestart
+    why="the checkout failed"
   else
     printf 'TICK-RESTART %s code=%s behind=%s -> %s\n' "$(date -u +%FT%TZ)" "$code" "$behind" \
       "$(git -C "$top" rev-parse --short=7 HEAD)"
     HPO_TICK_RESTARTED=1 exec bash "$top/tools/audit/seat/tick_loop.sh" ${ARGV[@]+"${ARGV[@]}"}  # mut:exec
   fi
+  stale_why=$why
   printf 'TICK-STALE %s code=%s behind=%s: %s; the relay and sweep arms are skipped\n' \
     "$(date -u +%FT%TZ)" "$code" "$behind" "$why"
 }
 
-relay_reap() { # <r> [late]: print a finished relay's output; sets rrc. 1: nothing to reap
-  local r=$1 st
+relay_reap() { # <r> [late]: print a finished relay's output; sets rrc and relay_ended (its end epoch). 1: nothing to reap
+  local r=$1 st en
   [ -f "$r.rc" ] || return 1
-  read -r rrc st < "$r.rc"
+  read -r rrc st en < "$r.rc"
+  case $en in ''|*[!0-9]*) en=$(date +%s) ;; esac; relay_ended=$en  # an rc from before the end field: ended by now
   cat "$r.log" 2>/dev/null; rm -f "$r.rc"
   [ "$rrc" = 0 ] && rrc=ok || rrc="rc=$rrc"
   [ -z "${2:-}" ] || printf 'TICK-RELAY %s relay=%s started=%s\n' "$(date -u +%FT%TZ)" "$rrc" "$st"
 }
 
-relay_start() { # <r> <relay>: start the relay detached, wait for it at most the bound; sets rrc
+relay_start() { # <r> <relay> [late]: start the relay detached, wait for it at most the bound; sets rrc
   local r=$1 relay=$2 hp hrc k=0 wait=${HPO_TICK_RELAY_WAIT:-30}
   case $wait in ''|*[!0-9]*) wait=30 ;; esac
+  relay_ended=
   python3 -I -c "$RELAY_HOLDER" "$r" bash "$relay" pass --confirm </dev/null >/dev/null 2>&1 & hp=$!  # mut:confirm
   while kill -0 "$hp" 2>/dev/null && [ $k -lt $((wait * 10)) ]; do sleep 0.1; k=$((k + 1)); done
   if kill -0 "$hp" 2>/dev/null; then rrc=running; return 0; fi  # mut:detach
   wait "$hp"; hrc=$?
   case $hrc in
-    0) relay_reap "$r" || rrc="rc=lost" ;;
+    0) relay_reap "$r" ${3:-} || rrc="rc=lost" ;;
     75) rrc=running ;;
     *) rrc="rc=holder-$hrc" ;;
   esac
 }
 
+relay_gap_sleep() { # <out> <seconds>: the inter-pass sleep, starting the next relay HPO_TICK_RELAY_GAP s after one ends
+  local r=$1.relay end=$(( $(date +%s) + $2 )) gap=${HPO_TICK_RELAY_GAP:-120} relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh} rrc
+  case $gap in ''|*[!0-9]*) gap=120 ;; esac
+  while [ "$(date +%s)" -lt "$end" ]; do
+    if [ -z "$last_stale" ] && [ -f "$relay" ]; then
+      [ ! -f "$r.rc" ] || relay_reap "$r" late
+      if [ -n "$relay_ended" ] && [ $(( $(date +%s) - relay_ended )) -ge "$gap" ] && python3 -I -c "$LOCK_FREE" "$r.lock"; then
+        relay_start "$r" "$relay" late  # mut:gapstart
+      fi
+    fi
+    sleep 1
+  done
+}
+
 sweep_pass() { # <out>: one merge-train sweep when one is due; prints its TICK-SWEEP line
   local log=$1.sweep.log at=$1.sweep.at src last every=${HPO_TICK_SWEEP_EVERY:-1800}
   case $every in ''|*[!0-9]*) every=1800 ;; esac
@@ -177,7 +211,7 @@ sweep_pass() { # <out>: one merge-train sweep when one is due; prints its TICK-S
 }
 
 tick_pass() { # <out> [tick args...]: one pass; prints the banner
-  local out=$1 relay rrc trc tmp now code behind stale g; shift
+  local out=$1 relay rrc trc tmp now code behind stale stale_why sn g; shift
   relay=${HPO_TICK_RELAY:-$HERE/cloud_relay.sh}
   # GH-BUCKET-SPENDER-UNLOGGED: a pass whose children's gh is not the shim spends unlogged.
   g=$(command -v gh)
@@ -186,8 +220,10 @@ tick_pass() { # <out> [tick args...]: one pass; prints the banner
       "$(date -u +%FT%TZ)" "${g:-none}" "$SEAT_BIN"
   mkdir -p "$(dirname -- "$out")"
   fresh_check "$out"
+  last_stale=$stale
   if [ -n "$stale" ]; then
     rrc=stale  # mut:skip
+    sn=$(cat "$out.stale" 2>/dev/null); case $sn in ''|*[!0-9]*) sn=0 ;; esac; sn=$((sn + 1)); echo "$sn" > "$out.stale"
   elif [ -f "$relay" ]; then
     relay_start "$out.relay" "$relay"
     # 76: an earlier pass's relay finished after its wait; reap it, then start this pass's.
@@ -195,9 +231,12 @@ tick_pass() { # <out> [tick args...]: one pass; prints the banner
   else
     rrc=absent
   fi
+  [ -n "$stale" ] || rm -f "$out.stale"
   tmp="$out.part.$$"
   if [ -n "${HPO_TICK_CMD:-}" ]; then $HPO_TICK_CMD "$@" > "$tmp" 2>&1; trc=$?
   else python3 "$HERE/orchestrator_tick.py" "$@" > "$tmp" 2>&1; trc=$?; fi
+  [ -z "$stale" ] || [ "$sn" -lt 2 ] || printf -- '-> OWED relay-skipped code=%s behind=%s: %s (stale %s consecutive passes)\n' \
+    "$code" "$behind" "$stale_why" "$sn" >> "$tmp"  # mut:staleowed
   mv -f "$tmp" "$out"
   now=$(date -u +%FT%TZ)
   printf 'TICK-PASS %s relay=%s tick=%s code=%s behind=%s out=%s\n' "$now" "$rrc" "$trc" "$code" "$behind" "$out"
@@ -301,6 +340,21 @@ done" ]
   k=0; while [ ! -f "$t/g.txt.relay.rc" ] && [ $k -lt 100 ]; do sleep 0.1; k=$((k + 1)); done
   [ -f "$t/g.txt.relay.rc" ]
   ck "a TERM to the loop's process group leaves the in-flight relay to write its rc" $?
+  # S14-RELAY-CADENCE: a relay that ends during the sleep is followed by the next after HPO_TICK_RELAY_GAP s, no tick between.
+  # Wall-clock rows (about 10 s): the outer run alone, as the nesting block is, so the nested copies stay inside the step's bound.
+  if [ -z "$nested" ]; then
+  rm -f "$t/order" "$t/gap.txt"*
+  out=$(HPO_TICK_RELAY_GAP=1 HPO_TICK_RELAY_WAIT=2 HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" timeout 4 bash "$0" --interval 60 --out "$t/gap.txt")
+  [ "$(sed -n 1,3p "$t/order")" = "relay pass --confirm
+tick 
+relay pass --confirm" ] && [ "$(grep -c '^tick' "$t/order")" = 1 ] && printf '%s\n' "$out" | grep -Eq '^TICK-RELAY [0-9T:-]+Z relay=ok started='
+  ck "a relay that ends during the sleep is followed by another after the gap, with no tick pass between" $?
+  rm -f "$t/slow" "$t/order" "$t/gap.txt"*
+  out=$(RELAY_SLEEP=5 HPO_TICK_RELAY_GAP=1 HPO_TICK_RELAY_WAIT=1 HPO_TICK_RELAY=$t/slow.sh HPO_TICK_CMD="bash $t/tick.sh" timeout 4 bash "$0" --interval 60 --out "$t/gap.txt")
+  [ "$(cat "$t/slow")" = start ] && [ "$(cat "$t/order")" = "tick " ]
+  ck "null control: a relay still in flight at the gap starts none" $?
+  k=0; while [ ! -f "$t/gap.txt.relay.rc" ] && [ $k -lt 80 ]; do sleep 0.1; k=$((k + 1)); done
+  fi
   # Stubbed and --once, so a mutant that accepts the interval cannot loop on the real tick.
   HPO_TICK_RELAY=$t/absent.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --interval x --out "$t/b.txt" > "$t/e" 2>&1
   [ $? = 2 ] && grep -q 'interval' "$t/e"
@@ -389,9 +443,22 @@ f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".
   printf '%s\n' "$out" | grep -q '^TICK-STALE .*: the tree is dirty' && printf '%s\n' "$out" | grep -q 'relay=stale' \
     && [ "$(cat "$t/order")" = "tick " ] && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
   ck "freshness: a dirty tree prints the banner, skips the relay and is never moved" $?
-  git -C "$t/c" checkout -q -b local; out=$(fr); git -C "$t/c" checkout -q --detach; git -C "$t/c" branch -qD local
-  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: a branch is checked out' && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
-  ck "freshness: a checked-out branch is never moved (restart needs a detached head)" $?
+  # S14-TICK-STALE-SILENT: a stale state into a second consecutive pass ends the board with one OWED line
+  rm -f "$t/f.txt.stale"; echo dirty >> "$t/c/tools/pr/x"; out=$(fr); b1=$(cat "$t/f.txt"); out=$(fr); git -C "$t/c" checkout -q -- tools/pr/x
+  [ "$b1" = BOARD ]
+  ck "freshness null control: one stale pass writes no OWED line on the board" $?
+  [ "$(grep -c '^-> OWED relay-skipped ' "$t/f.txt")" = 1 ] \
+    && grep -qx -- "-> OWED relay-skipped code=$at0 behind=2: the tree is dirty (stale 2 consecutive passes)" "$t/f.txt" \
+    && [ "$(head -n 1 "$t/f.txt")" = BOARD ]
+  ck "freshness: a second consecutive stale pass ends the board with one '-> OWED relay-skipped' line: why, code and behind" $?
+  out=$(HPO_TICK_CODE_DIR=$t/nogit HPO_TICK_RELAY=$t/relay.sh HPO_TICK_CMD="bash $t/tick.sh" bash "$0" --once --out "$t/f.txt")  # no checkout: never stale
+  [ "$(cat "$t/f.txt")" = BOARD ] && [ ! -e "$t/f.txt.stale" ] && printf '%s\n' "$out" | grep -q 'relay=ok'
+  ck "freshness: a fresh pass clears the count, and its board carries no OWED line" $?
+  git -C "$t/c" checkout -q -b local; echo own > "$t/c/own"; git -C "$t/c" add own; git -C "$t/c" commit -qm own; own=$(git -C "$t/c" rev-parse HEAD)
+  out=$(fr); git -C "$t/c" checkout -q --detach "$at0"; git -C "$t/c" branch -qD local
+  printf '%s\n' "$out" | grep -q '^TICK-STALE .*: the branch local holds 1 commit(s) origin/main lacks; it is never moved' \
+    && printf '%s\n' "$out" | grep -q 'relay=stale' && [ ! -f "$t/order" -o "$(cat "$t/order" 2>/dev/null)" = "tick " ] && [ -n "$own" ]
+  ck "freshness: a branch holding a commit origin/main lacks is never moved, and says why" $?
   out=$(HPO_TICK_RESTARTED=1 fr)
   printf '%s\n' "$out" | grep -q '^TICK-STALE .*: restarted once this pass' && [ "$(git -C "$t/c" rev-parse --short=7 HEAD)" = "$at0" ]
   ck "freshness: a pass already restarted does not exec again (at most once per pass)" $?
@@ -404,6 +471,12 @@ f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".
     && printf '%s\n' "$out" | grep -qx "NEW-LOOP --once --out $t/f.txt --sweep" \
     && [ "$(git -C "$t/c" rev-parse HEAD)" = "$(git -C "$t/c" rev-parse origin/main)" ] && [ ! -f "$t/order" ]
   ck "freshness: a loop-file change with a free lock and a clean detached tree checks out origin/main and execs it with the same args" $?
+  git -C "$t/c" checkout -q -b local "$at0"; out=$(fr --sweep)
+  printf '%s\n' "$out" | grep -q "^TICK-RESTART .* code=$at0 behind=4 -> " \
+    && printf '%s\n' "$out" | grep -qx "NEW-LOOP --once --out $t/f.txt --sweep" \
+    && [ "$(git -C "$t/c" symbolic-ref --short HEAD)" = local ] && [ "$(git -C "$t/c" rev-parse HEAD)" = "$(git -C "$t/c" rev-parse origin/main)" ]
+  ck "freshness: a clean branch-backed checkout behind origin/main with no commit of its own restarts on its branch at origin/main" $?
+  git -C "$t/c" checkout -q --detach; git -C "$t/c" branch -qD local
   # The self-test run as a live seat runs it -- from a checkout behind origin/main on the watched
   # paths, a branch and then a detached head, its state dir's bin holding the gh shim -- reads nothing of
   # that checkout and leaves its HEAD where it was; so does one a git hook's GIT_DIR names. (The
@@ -497,6 +570,7 @@ f = open(sys.argv[1], "a"); fcntl.flock(f, fcntl.LOCK_EX); open(sys.argv[1] + ".
 )
 
 ARGV=("$@")  # a restart execs the new loop with these
+relay_ended= last_stale=  # the relay gap's clock and the last pass's staleness (relay_gap_sleep)
 once=; sweep=; every=300; out=${HPO_STATE_DIR:-$HOME/.local/state/hpo}/tick.txt
 while [ $# -gt 0 ]; do
   case $1 in
@@ -515,5 +589,5 @@ while :; do
   tick_pass "$out" "$@"
   unset HPO_TICK_RESTARTED  # once per pass: the next pass may restart again
   [ -n "$once" ] && exit 0
-  sleep "$every"
+  relay_gap_sleep "$out" "$every"
 done
diff --git a/tools/audit/seat/topic_grammar.py b/tools/audit/seat/topic_grammar.py
index 40dbc8afbf..60be231759 100644
--- a/tools/audit/seat/topic_grammar.py
+++ b/tools/audit/seat/topic_grammar.py
@@ -2,6 +2,7 @@
 """The topic grammar: one owner for how a topic joins dispatch, return, PR and roster records.
 
     python3 tools/audit/seat/topic_grammar.py pr-topic <head>
+    python3 tools/audit/seat/topic_grammar.py handoff-topics <head>...
     python3 tools/audit/seat/topic_grammar.py family-refs <topic> <kind>[,<kind>...] < ls-remote-text
     python3 tools/audit/seat/topic_grammar.py --self-test
 
@@ -11,6 +12,11 @@ group. A split adds `-p<N>` partway through the work, so a join keyed on the exa
 (dev/audit/rca/topic-family.md). The rules:
 
   pr_topic    a PR head less `fix/` and one trailing `-pr`.
+  handoff_topics  the `handoff/<t>` topics a PR head can carry, the first with a ref deciding:
+              `fix/<t>-pr` is <t>-pr then <t> (a group whose own topic ends `-pr` returns under the
+              first), `fix/<t>` is <t>, any other shape none. review_packet.py's handoff-not-applied
+              and cloud_relay.sh's handoff arm both read it: the arm reading <t> alone left #3358
+              behind handoff/r10-combi-tank-pr while the dispatch read refused it (R11-PRE-RELAY-REBUILD).
   family      the topic less one trailing `-p<N>` is the base; the family is the base plus every
               `<base>-p<N>`. A bare `-<N>` is never a member: R10-ROSTER-OPS-2, R10-STALE-PATHS-2
               and R10-TICK-DRIVERS-2 are distinct groups.
@@ -36,6 +42,11 @@ def pr_topic(head: str) -> str:
     return t[:-len("-pr")] if t.endswith("-pr") else t
 
 
+def handoff_topics(head: str) -> "list[str]":
+    t = head[len("fix/"):] if head.startswith("fix/") else ""
+    return [x for x in ([t, t[:-len("-pr")]] if t.endswith("-pr") else [t]) if x]
+
+
 def base(topic: str) -> str:
     m = PART.fullmatch(topic)
     return m.group(1) if m else topic
@@ -108,6 +119,20 @@ def self_test() -> int:
 
     ck("pr_topic strips fix/ and one -pr", [pr_topic(h) for h in ("fix/a-p1-pr", "fix/a", "a-pr-pr", "handoff/x")]
        == ["a-p1", "a", "a-pr", "handoff/x"])
+    ck("handoff_topics: fix/<t>-pr reads <t>-pr then <t>, fix/<t> reads <t>, any other shape none",
+       [handoff_topics(h) for h in ("fix/a-pr", "fix/a", "a-pr", "fix/", "fix/-pr", "handoff/x")]
+       == [["a-pr", "a"], ["a"], [], [], ["-pr"], []])  # mut:tghandoff
+    import contextlib
+    import io
+
+    def cli(*argv):  # main's stdout and rc: the bash readers (cloud_relay.sh's handoff arm) read the CLI
+        out = io.StringIO()
+        with contextlib.redirect_stdout(out):
+            rc = main(list(argv))
+        return out.getvalue(), rc
+    ck("handoff-topics CLI: one topic per line over every head, in order, rc 0; no head prints nothing, rc 0",
+       cli("handoff-topics", "fix/a-pr", "fix/b", "record/x") == ("a-pr\na\nb\n", 0)
+       and cli("handoff-topics") == ("", 0))
     ck("the base drops one trailing -p<N> only", [base(t) for t in ("a-p2", "a", "a-p1-p2", "r10-roster-ops-2")]
        == ["a", "a", "a-p1", "r10-roster-ops-2"])
     ls = "\n".join(f"{c * 40}\trefs/heads/{r}" for c, r in (
@@ -142,6 +167,10 @@ def main(argv) -> int:
     if len(argv) == 2 and argv[0] == "pr-topic":
         print(pr_topic(argv[1]))
         return 0
+    if argv[:1] == ["handoff-topics"]:
+        for t in (t for head in argv[1:] for t in handoff_topics(head)):
+            print(t)
+        return 0
     if len(argv) == 3 and argv[0] == "family-refs":
         for sha, ref in family_refs(argv[1], sys.stdin.read(), argv[2].split(",")):
             print(sha, ref)
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index 5051a48e90..3b2fe89e61 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -260,6 +260,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
@@ -4209,6 +4210,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
@@ -4522,15 +4524,23 @@
    "git": []
   },
   "gantt-and-verdict-audit": {
-   "run_sha": "d1f9161e487c99eb5be4378579e90ac6800a56240f6f3d5a8bd71abdc277e1ae",
+   "run_sha": "16bbc5a7a78f977e26aabe9f3756fcab21ffc79c4ad03ac92f57d5a1fbfdc634",
    "files": [
+    "tools/audit/seat/owed_watch.py",
+    "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/sweep_gantt.py",
+    "tools/audit/seat/topic_grammar.py",
     "tools/audit/seat/verdict_audit.py"
    ],
    "probes": [
-    "."
+    ".",
+    "tools",
+    "tools/audit",
+    "tools/audit/seat"
+   ],
+   "dirs": [
+    "tools/audit/seat"
    ],
-   "dirs": [],
    "index": false,
    "objects": false,
    "git": []
@@ -4788,6 +4798,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
@@ -5299,6 +5310,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
@@ -5480,6 +5492,7 @@
     "tools/audit/seat/ledger.py",
     "tools/audit/seat/merge_train.py",
     "tools/audit/seat/orchestrator_tick.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/pr_cap.py",
     "tools/audit/seat/proof_watch.py",
     "tools/audit/seat/record_row.py",
@@ -5597,6 +5610,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
@@ -6716,6 +6730,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
@@ -8441,7 +8456,7 @@
    "git": []
   },
   "self-tests-outside-seat": {
-   "run_sha": "1e2fc0b8e9fbdd55f36a3f9b56f9b721100229ca4d7ed5af11986fae0b770dec",
+   "run_sha": "8201d5a6e42ed723e637542d3e8aa2ca0fb8f312d3b6d5607804ae0fa1e52304",
    "files": [
     ".claude/hooks/**",
     ".claude/rules/**",
@@ -8574,10 +8589,142 @@
    "dirs": [
     ".",
     ".github/workflows",
+    "custom_components/heatpump_optimizer",
+    "custom_components/heatpump_optimizer/brand",
+    "custom_components/heatpump_optimizer/translations",
+    "custom_components/heatpump_optimizer/www",
     "dev/governance/dimensions",
     "dev/governance/rules",
     "dev/programme/delivery",
     "tests",
+    "tests/mutation_ledger/killed_by",
+    "tests/mutation_ledger/killed_by/__init__.py",
+    "tests/mutation_ledger/killed_by/accuracy.py",
+    "tests/mutation_ledger/killed_by/away.py",
+    "tests/mutation_ledger/killed_by/batchmath.py",
+    "tests/mutation_ledger/killed_by/battery.py",
+    "tests/mutation_ledger/killed_by/binary_sensor.py",
+    "tests/mutation_ledger/killed_by/boost.py",
+    "tests/mutation_ledger/killed_by/button.py",
+    "tests/mutation_ledger/killed_by/climate.py",
+    "tests/mutation_ledger/killed_by/comfort_band.py",
+    "tests/mutation_ledger/killed_by/comfort_learning.py",
+    "tests/mutation_ledger/killed_by/config_flow.py",
+    "tests/mutation_ledger/killed_by/const.py",
+    "tests/mutation_ledger/killed_by/coordinator.py",
+    "tests/mutation_ledger/killed_by/currency.py",
+    "tests/mutation_ledger/killed_by/curve_learning.py",
+    "tests/mutation_ledger/killed_by/datetime.py",
+    "tests/mutation_ledger/killed_by/debugger.py",
+    "tests/mutation_ledger/killed_by/defrost.py",
+    "tests/mutation_ledger/killed_by/device_prefill.py",
+    "tests/mutation_ledger/killed_by/dhw_draws.py",
+    "tests/mutation_ledger/killed_by/dhw_learning.py",
+    "tests/mutation_ledger/killed_by/dhw_planner.py",
+    "tests/mutation_ledger/killed_by/dhw_schedule.py",
+    "tests/mutation_ledger/killed_by/diagnosis.py",
+    "tests/mutation_ledger/killed_by/diagnostics.py",
+    "tests/mutation_ledger/killed_by/disinfection.py",
+    "tests/mutation_ledger/killed_by/draw_range.py",
+    "tests/mutation_ledger/killed_by/drift.py",
+    "tests/mutation_ledger/killed_by/driving_grade.py",
+    "tests/mutation_ledger/killed_by/duty_legs.py",
+    "tests/mutation_ledger/killed_by/duty_switch.py",
+    "tests/mutation_ledger/killed_by/early_cutoff.py",
+    "tests/mutation_ledger/killed_by/entity.py",
+    "tests/mutation_ledger/killed_by/entry_config.py",
+    "tests/mutation_ledger/killed_by/external_heat.py",
+    "tests/mutation_ledger/killed_by/flow_lift.py",
+    "tests/mutation_ledger/killed_by/flow_meter.py",
+    "tests/mutation_ledger/killed_by/freq_control.py",
+    "tests/mutation_ledger/killed_by/frontend.py",
+    "tests/mutation_ledger/killed_by/grid_fee.py",
+    "tests/mutation_ledger/killed_by/heat_curve.py",
+    "tests/mutation_ledger/killed_by/heat_energy.py",
+    "tests/mutation_ledger/killed_by/inputs.py",
+    "tests/mutation_ledger/killed_by/issues.py",
+    "tests/mutation_ledger/killed_by/learner_progress.py",
+    "tests/mutation_ledger/killed_by/ledger.py",
+    "tests/mutation_ledger/killed_by/legionella.py",
+    "tests/mutation_ledger/killed_by/log_latch.py",
+    "tests/mutation_ledger/killed_by/manual_plan.py",
+    "tests/mutation_ledger/killed_by/mixing_valve.py",
+    "tests/mutation_ledger/killed_by/modbus_prefill.py",
+    "tests/mutation_ledger/killed_by/name_match.py",
+    "tests/mutation_ledger/killed_by/narrative.py",
+    "tests/mutation_ledger/killed_by/notifier.py",
+    "tests/mutation_ledger/killed_by/off_restore.py",
+    "tests/mutation_ledger/killed_by/open_meteo.py",
+    "tests/mutation_ledger/killed_by/optimizer.py",
+    "tests/mutation_ledger/killed_by/plan_slots.py",
+    "tests/mutation_ledger/killed_by/plan_step.py",
+    "tests/mutation_ledger/killed_by/power_guard.py",
+    "tests/mutation_ledger/killed_by/prefill_offer.py",
+    "tests/mutation_ledger/killed_by/presets.py",
+    "tests/mutation_ledger/killed_by/price_model.py",
+    "tests/mutation_ledger/killed_by/price_tiles.py",
+    "tests/mutation_ledger/killed_by/process_worker.py",
+    "tests/mutation_ledger/killed_by/pump_arbiter.py",
+    "tests/mutation_ledger/killed_by/pump_mode.py",
+    "tests/mutation_ledger/killed_by/pump_schedule.py",
+    "tests/mutation_ledger/killed_by/pump_signals.py",
+    "tests/mutation_ledger/killed_by/pv.py",
+    "tests/mutation_ledger/killed_by/quick_setup.py",
+    "tests/mutation_ledger/killed_by/quiet_windows.py",
+    "tests/mutation_ledger/killed_by/repairs.py",
+    "tests/mutation_ledger/killed_by/replay_doc.py",
+    "tests/mutation_ledger/killed_by/sensor.py",
+    "tests/mutation_ledger/killed_by/services.py",
+    "tests/mutation_ledger/killed_by/setpoint_check.py",
+    "tests/mutation_ledger/killed_by/silent_mode.py",
+    "tests/mutation_ledger/killed_by/slot_drivers.py",
+    "tests/mutation_ledger/killed_by/snapshots.py",
+    "tests/mutation_ledger/killed_by/store.py",
+    "tests/mutation_ledger/killed_by/supply_hold.py",
+    "tests/mutation_ledger/killed_by/switch.py",
+    "tests/mutation_ledger/killed_by/sysid.py",
+    "tests/mutation_ledger/killed_by/tariff.py",
+    "tests/mutation_ledger/killed_by/thermal_model.py",
+    "tests/mutation_ledger/killed_by/topology.py",
+    "tests/mutation_ledger/killed_by/wear.py",
+    "tests/mutation_ledger/killed_by/whatif.py",
+    "tests/mutation_ledger/killed_by/wood_fuel.py",
+    "tests/mutation_ledger/survivor_triage",
+    "tests/mutation_ledger/survivor_triage/accuracy.py",
+    "tests/mutation_ledger/survivor_triage/away.py",
+    "tests/mutation_ledger/survivor_triage/battery.py",
+    "tests/mutation_ledger/survivor_triage/binary_sensor.py",
+    "tests/mutation_ledger/survivor_triage/boost.py",
+    "tests/mutation_ledger/survivor_triage/config_flow.py",
+    "tests/mutation_ledger/survivor_triage/coordinator.py",
+    "tests/mutation_ledger/survivor_triage/debugger.py",
+    "tests/mutation_ledger/survivor_triage/dhw_planner.py",
+    "tests/mutation_ledger/survivor_triage/dhw_schedule.py",
+    "tests/mutation_ledger/survivor_triage/draw_range.py",
+    "tests/mutation_ledger/survivor_triage/drift.py",
+    "tests/mutation_ledger/survivor_triage/duty_switch.py",
+    "tests/mutation_ledger/survivor_triage/early_cutoff.py",
+    "tests/mutation_ledger/survivor_triage/entry_config.py",
+    "tests/mutation_ledger/survivor_triage/heat_energy.py",
+    "tests/mutation_ledger/survivor_triage/inputs.py",
+    "tests/mutation_ledger/survivor_triage/ledger.py",
+    "tests/mutation_ledger/survivor_triage/manual_plan.py",
+    "tests/mutation_ledger/survivor_triage/notifier.py",
+    "tests/mutation_ledger/survivor_triage/off_restore.py",
+    "tests/mutation_ledger/survivor_triage/optimizer.py",
+    "tests/mutation_ledger/survivor_triage/payload.py",
+    "tests/mutation_ledger/survivor_triage/pump_arbiter.py",
+    "tests/mutation_ledger/survivor_triage/pump_mode.py",
+    "tests/mutation_ledger/survivor_triage/quiet_windows.py",
+    "tests/mutation_ledger/survivor_triage/repairs.py",
+    "tests/mutation_ledger/survivor_triage/sensor.py",
+    "tests/mutation_ledger/survivor_triage/slot_drivers.py",
+    "tests/mutation_ledger/survivor_triage/store.py",
+    "tests/mutation_ledger/survivor_triage/sysid.py",
+    "tests/mutation_ledger/survivor_triage/tariff.py",
+    "tests/mutation_ledger/survivor_triage/thermal_model.py",
+    "tests/mutation_ledger/survivor_triage/whatif.py",
+    "tests/mutation_ledger/survivor_triage/wood_fuel.py",
     "tools/audit",
     "tools/audit/archscore",
     "tools/audit/archscore/metrics",
@@ -8740,6 +8887,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
@@ -9527,6 +9675,7 @@
     "tools/audit/seat/outside_intake.py",
     "tools/audit/seat/outside_intake_selftest.py",
     "tools/audit/seat/owed_unactioned.py",
+    "tools/audit/seat/owed_watch.py",
     "tools/audit/seat/plan_audit.py",
     "tools/audit/seat/plan_page.py",
     "tools/audit/seat/plan_public.py",
diff --git a/tools/policy/budget_raise_gate.py b/tools/policy/budget_raise_gate.py
index bf6f69f739..2424ef2237 100644
--- a/tools/policy/budget_raise_gate.py
+++ b/tools/policy/budget_raise_gate.py
@@ -254,6 +254,14 @@ SCHEMA: dict[str, list[tuple[tuple[str, ...], str]]] = {
         (("churn_per_kilo_product_lines",), MAX),
         (("churn_per_kilo_product_lines_band",), MAX),
     ],
+    # Its declining target (card P2): a later anchor restarts the decline, a
+    # longer stride or a smaller step slows it; each is a raise.
+    "dev/governance/config/machinery_target_budgets.json": [
+        (("_*",), FREE),
+        (("anchor",), FROZEN),
+        (("every_merges",), MAX),
+        (("step",), MIN),
+    ],
 }
 
 
@@ -953,6 +961,16 @@ def self_test() -> int:
           (True, True))
     check("machinery: a comment edited is routine", raised(G, g0, {**g0, "_comment": "y"}), False)
 
+    T = "dev/governance/config/machinery_target_budgets.json"
+    t0 = {"_recorded": "x", "anchor": "a" * 40, "every_merges": 290, "step": 48}
+    check("target: null control", raised(T, t0, t0), False)
+    check("target: a faster decline is routine",
+          (raised(T, t0, {**t0, "step": 49}), raised(T, t0, {**t0, "every_merges": 289})), (False, False))
+    check("target: a slower decline is a raise",
+          (raised(T, t0, {**t0, "step": 47}), raised(T, t0, {**t0, "every_merges": 291})), (True, True))
+    check("target: a moved anchor is a raise", raised(T, t0, {**t0, "anchor": "b" * 40}), True)
+    check("target: the file removed is a raise", raised(T, t0, None), True)
+
     U = "tests/new_budgets.json"
     check("unknown file: a change with no schema is a raise", raised(U, {"x": 1}, {"x": 0}), True)
     check("unknown file: added is a raise", raised(U, None, {"x": 1}), True)
diff --git a/tools/policy/check-wave-script.mjs b/tools/policy/check-wave-script.mjs
index 9607fcfcf1..5f8f9b73e8 100644
--- a/tools/policy/check-wave-script.mjs
+++ b/tools/policy/check-wave-script.mjs
@@ -1686,6 +1686,10 @@ await block('the P3 plan workflow', async () => {
   const FIND = (id) => ({ id, dimension: 'D7', severity: 'medium', title: id, class: 'P3', seam: 'coordinator' })
   const G = (group) => ({ group, issues: [1], fixes: [], findings: ['D7-s1-01'], severity: 'medium', files: ['coordinator.py'], after: [], architect_note: '' })
   const SHA = (c) => c.repeat(40)
+  // What is open when the finders finish: one card, one roster group (tvofi, 2026-11-15).
+  const OPEN = { open: { open_cards: ['E11-X'], open_groups: ['R11-G'], unmarked: [] }, open_rc: 0 }
+  const MOVES = (extra = {}) => ({ groups: [{ group: 'A', findings: ['D7-s1-01'], open_items: ['E11-X'] }], moves: [{ group: 'A', adr: 'ADR-1', metrics: {}, dS: 0 }],
+    dropped: [{ id: 'R11-G', reason: 'merged while the finders ran' }], projected_dS: 23, critical_chain: ['A'], depth: 1, hours: 8, risks: [], ...extra })
   const drive = async (over = {}) => {
     const calls = []
     let cur = over.publish?.sha ?? SHA('b')
@@ -1693,9 +1697,9 @@ await block('the P3 plan workflow', async () => {
     const agent = async (prompt, o) => {
       calls.push({ label: o.label, prompt })
       const label = o.label
-      if (label === 'plan/read') return over.read ?? { groups: [G('A')], findings: [FIND('D7-s1-01')], holdouts_path: 'h.json' }
+      if (label === 'plan/read') return over.read ?? { groups: [G('A')], findings: [FIND('D7-s1-01')], holdouts_path: 'h.json', ...OPEN }
       if (label === 'plan/architect') return over.architect ?? { components: ['coordinator'], scenarios: [{ quality: 'q', scenario: 's' }], triage: (over.read?.findings ?? [FIND('D7-s1-01')]).map((f) => ({ id: f.id, verdict: 'keep' })) }
-      if (label === 'plan/moves') return over.moves ?? { groups: [{ group: 'A', findings: ['D7-s1-01'] }], moves: [{ group: 'A', adr: 'ADR-1', metrics: {}, dS: 0 }], projected_dS: 23, critical_chain: ['A'], depth: 1, hours: 8, risks: [] }
+      if (label === 'plan/moves') return over.moves ?? MOVES()
       if (label === 'plan/write') return over.write ?? { brief_lint_rc: 0 }
       if (label === 'plan/publish') return over.publish ?? { sha: cur, pushed: true }
       if (/^plan\/review-/.test(label)) {
@@ -1724,9 +1728,9 @@ await block('the P3 plan workflow', async () => {
   await pthrows('an empty or absent draft roster stops P3', /draft roster .*empty or absent/, { read: { groups: [], findings: [] } })
   const two = [FIND('D7-s1-01'), FIND('D7-s1-02')]
   await pthrows('a triage that drops a verified finding stops P3', /dropped 1 verified finding/,
-    { read: { groups: [G('A')], findings: two }, architect: { components: [], scenarios: [], triage: [{ id: 'D7-s1-01', verdict: 'keep' }] } })
+    { read: { groups: [G('A')], findings: two, ...OPEN }, architect: { components: [], scenarios: [], triage: [{ id: 'D7-s1-01', verdict: 'keep' }] } })
   await pthrows('a triage that keeps one finding twice stops P3', /more than once/,
-    { read: { groups: [G('A')], findings: [FIND('D7-s1-01')] },
+    { read: { groups: [G('A')], findings: [FIND('D7-s1-01')], ...OPEN },
       architect: { components: [], scenarios: [], triage: [{ id: 'D7-s1-01', verdict: 'keep' }, { id: 'D7-s1-01', verdict: 'defer' }] } })
   await pthrows('a group with no move entry stops P3', /no move entry/,
     { moves: { groups: [{ group: 'A' }, { group: 'B' }], moves: [{ group: 'A', metrics: {} }], projected_dS: 23 } })

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
