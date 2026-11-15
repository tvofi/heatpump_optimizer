# Review packet #3451
head: 93ba227138a2c024bf81e44e74f2b11cb572bd76
base: 13cbe48de4236b7979c754640cc5b1a099ef7475

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: red
CodeQL id=132734176039 success
arch-score / arch-score id=132745271831 success
arm id=132733912363 skipped
budget-raise-gate / budget-raise-gate id=132745294630 failure
cancel-superseded id=132745287707 success
codeql id=132745271740 skipped
codeql / Analyze (actions) id=132743746654 success
codeql / Analyze (javascript-typescript) id=132743739843 success
codeql / Analyze (python) id=132743741435 success
gate id=132745271028 failure
governance id=132745288234 skipped
governance / env-matrix id=132743745912 success
governance / instrument-self-tests id=132743707932 success
governance / policy-docs id=132743706674 success
governance / record id=132743745255 skipped
governance / wave-script id=132743739711 success
hassfest id=132745284876 skipped
hassfest / hassfest id=132743730911 success
kernel-points id=132745271377 skipped
pr-contract id=132745272135 skipped
pr-contract / pr-contract id=132744478963 success
prelude id=132745292780 success
refresh id=132745284554 success
sweep-self id=132745484659 skipped
tests id=132745295485 skipped
tests / arch-instrument id=132743708217 success
tests / briefs id=132743739361 success
tests / browser id=132743708643 success
tests / ci-ratchet id=132743708897 skipped
tests / claims-autofix id=132743708725 skipped
tests / closure-scope id=132743742444 success
tests / closures id=132743708522 success
tests / closures-autofix id=132743708790 skipped
tests / coverage id=132743708398 success
tests / coverage-ratchet id=132743708579 success
tests / fast (3.14) id=132743708557 success
tests / graders-head-copy id=132743708511 success
tests / lane-proofs id=132743708998 success
tests / mutation id=132743707696 success
tests / mutation-autofix id=132743708499 skipped
tests / mutation-pins id=132743707693 skipped
tests / nightly-ha id=132743708743 skipped
tests / nightly-status id=132743708207 success
tests / replay id=132743708811 skipped
tests / typing id=132743708502 success
validate id=132745291008 skipped
validate / validate-hacs id=132743733762 success

## Refusals
none

## Advisories
hot-file: HPO_BUS_TRAIN_STATE is unset, so every merge verdict reads unboarded
approval-owed: required context `gate` concluded failure at 93ba227138a2c024bf81e44e74f2b11cb572bd76 only on a budget raise's owed approval (merge_train.approval_owed): 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.dev/governance/roles/proposal-triage.md: 36 -> 40 (a cap went up): a raise is the owner's (0013): tvofi's approval is on 939c91fc0e31, not this head 93ba227138a2: an approval covers only the commit it was given on

## carry_audit at the head
NOTE body item fc1e3f51: dismissed:already landed in R10-TRAIN-RESIDUE's roster brief ("the deletion of the record-autofix beat with the train-hold and stamp-hold arms once no stamp rule reads the rows", origin/handoff/audit-r10-roster dbff400dec), a group now carries-open at PR #3424, which carry_audit.py no longer accepts as a destination
NOTE body item 21f5d930: dismissed:unmeasured, and deleting a live train path is beyond the cards' scope.
NOTE body item f9a606c8: dismissed:the card's risk line accepts review starting early, never a merge at red.
NOTE body item 9323e541: dismissed:environment setup, not this diff's code; the measured fix is one `mkdir`.
NOTE body item 37e09a96: dismissed:a predictor false red with a one-command local remedy, outside this group's cards; the orchestrator may route it.
NOTE body item 3aa844a6: dismissed:a fast-forward step commit over the stale ref needs neither a delete nor a guard exception.
CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git diff --name-status $(git merge-base origin/main <r>)...<r> -- dev/governance/roles/proposal-triage.md
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git grep -c proposal-triage <r> -- CLAUDE.md dev/governance/roles/orchestrator.md dev/governance/dimensions/D11.md dev/audit/README.md tools/audit/seat/outside_intake.py tools/audit/seat/roster_edit.py tools/audit/seat/sweep_template.md dev/governance/config/policy_budgets.json
             `git grep` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs --budgets
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         node tools/policy/rules_sync.mjs --check
             `tools/policy/rules_sync.mjs` is in the tree at this head
  ok         node tools/policy/brief_lint.mjs
             `tools/policy/brief_lint.mjs` is in the tree at this head
  ok         bash tools/pr/app_approve.sh --self-test
             `tools/pr/app_approve.sh` is in the tree at this head
  ok         python3 tools/audit/seat/roster_edit.py --self-test
             `tools/audit/seat/roster_edit.py` is in the tree at this head
  ok         python3 tools/audit/seat/outside_intake.py --self-test
             `tools/audit/seat/outside_intake.py` is in the tree at this head
  ok         bash tools/audit/seat/bus.sh --self-test
             `tools/audit/seat/bus.sh` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff d7004eaa
             `tests/closure.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff d7004eaa HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 HPO_GATE_PRIORITY=0 bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  unverified git merge-tree --write-tree origin/main 1ce773ca
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tests/gate_lock.py
             `tests/gate_lock.py` is in the tree at this head
  ok         tools/audit/seat/bus.sh
             `tools/audit/seat/bus.sh` is in the tree at this head
  unverified git merge-tree --write-tree origin/main HEAD
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff a18e2e9d
             `tests/closure.py` is in the tree at this head
  ok         bash tools/audit/seat/tick_loop.sh --self-test
             `tools/audit/seat/tick_loop.sh` is in the tree at this head
  unverified git rev-parse HEAD
             `git rev-parse` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git merge-tree --write-tree --name-only origin/main 4bc2f3bc
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff 0b276e8c --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only origin/main
             `tests/env_drift.py` is in the tree at this head
  ok         tests/closure.py selftest
             `tests/closure.py` is in the tree at this head
  ok         tests/layout.py
             `tests/layout.py` is in the tree at this head
  ok         tests/structure.py
             `tests/structure.py` is in the tree at this head
  unverified git diff --quiet origin/main HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/seat/review_packet.py --self-test
             `tools/audit/seat/review_packet.py` is in the tree at this head
  ok         node tools/policy/check-wave-script.mjs
             `tools/policy/check-wave-script.mjs` is in the tree at this head
  unverified git diff --shortstat 0b276e8c...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git merge-tree --write-tree --name-only origin/main c453a377
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff 2cfa3d7d --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only 2cfa3d7d
             `tests/env_drift.py` is in the tree at this head
  ok         tests/harness_headers.py
             `tests/harness_headers.py` is in the tree at this head
  unverified git diff --shortstat 2cfa3d7d...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         bash tools/pr/prepr.sh BODY.md
             `tools/pr/prepr.sh` is in the tree at this head
  ok         HPO_GATE_PRIORITY=2 PYTHONPATH=tests/hastub python3 tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff a7628041 --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         tests/env_drift.py --claims-only a7628041
             `tests/env_drift.py` is in the tree at this head
  unverified git merge-tree --write-tree --name-only origin/main d094fbc5
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --shortstat a7628041...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/audit/seat/ref_privacy.py guard --ref refs/heads/handoff/r10-process-slim-p2 --commits HEAD --over origin/main -C .
             `tools/audit/seat/ref_privacy.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff dbd1ab5b --workdir $D
             `tests/closure.py` is in the tree at this head
  unverified git merge-tree --write-tree --name-only origin/main 9da744f7
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff d08ed310 --workdir $D
             `tests/closure.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  unverified git merge-tree --write-tree origin/main f5af5b513b1978d732fd41902c203890e3a0247b
             `git merge-tree` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tools/policy/role_pack.py --self-test
             `tools/policy/role_pack.py` is in the tree at this head
  ok         python3 tools/audit/seat/orchestrator_tick.py --self-test
             `tools/audit/seat/orchestrator_tick.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 0a8033305d7b03494eb63453e6181a13ffa55c05 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  unverified git diff --shortstat 0a8033305d7b03494eb63453e6181a13ffa55c05...HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --quiet origin/main HEAD -- .github/workflows/nightly.yml
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         python3 tests/closure.py select --diff 0a8033305d7b03494eb63453e6181a13ffa55c05
             `tests/closure.py` is in the tree at this head
  ok         python3 tools/audit/seat/merge_train.py --self-test
             `tools/audit/seat/merge_train.py` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py --self-test
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         bash tools/audit/seat/body_push.sh --self-test
             `tools/audit/seat/body_push.sh` is in the tree at this head
  ok         python3 -I tools/release/stamp.py --self-test
             `tools/release/stamp.py` is in the tree at this head
  ok         bash tools/audit/seat/handoff_push.sh --self-test
             `tools/audit/seat/handoff_push.sh` is in the tree at this head
  ok         python3 tools/audit/seat/postmerge.py --self-test
             `tools/audit/seat/postmerge.py` is in the tree at this head
  ok         python3 tools/audit/machinery_ratchet.py --self-test
             `tools/audit/machinery_ratchet.py` is in the tree at this head
  ok         python3 tools/audit/seat/selftest_wiring.py --check
             `tools/audit/seat/selftest_wiring.py` is in the tree at this head
  ok         python3 tools/audit/archscore/score.py --diff 6457496aba7b1076b1ed60c374c5badafdf66fc1 HEAD
             `tools/audit/archscore/score.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 6457496aba7b1076b1ed60c374c5badafdf66fc1
             `tests/closure.py` is in the tree at this head
  unverified git show origin/main:...
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --name-only origin/main HEAD
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git diff --name-only fdc8d21a 491177c4
             `git diff` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head

FIGURES: 50 resolved, 19 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head 93ba227138a2c024bf81e44e74f2b11cb572bd76)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at 93ba227138a2c024bf81e44e74f2b11cb572bd76
Fix review: blocked 93ba227138a2c024bf81e44e74f2b11cb572bd76 ci-red: gate is red because governance / policy-docs was cancelled at its 5-minute timeout in run 43688486622; re-run that job, and the delta review below holds

bus-nonce: 546905d0ae546008ea6b475c6ccf1f5c

## Block

- `merge_train.py classify 93ba227138a2c024bf81e44e74f2b11cb572bd76 --pr 3451` exits 1: `RED 93ba227138a2c024bf81e44e74f2b11cb572bd76 pending: none red: gate` (ev/classify_log.txt, ev/classify_last.txt). This is not APPROVAL-OWED (exit 4), unlike the previous round.
- The gate job 132741691093 (run 43688486622) prints `FAIL governance / policy-docs: cancelled (this run)` next to the expected `budget-raise-gate` red. Both `gate` and `governance / policy-docs` are in the `merge_train.py owed-reds` set (ev/owed_reds.txt).
- The job `governance / policy-docs` 132734039270 started at 07:07:47Z and ended `cancelled` at 07:12:51Z. That is the job's `timeout-minutes: 5` in `.github/workflows/governance.yml` (ev/ci_gate_red.txt).
- I ran the job's content steps locally at the head, and each one passes (ev/policy_docs_steps_head.txt):
  - `rules_sync.mjs --check`: rc 0, 0 s.
  - `codeowners_gap.py --check`: rc 0, 2 s.
  - `policy_lint.mjs`: rc 0, 36 s.
  - `fragments_sync.mjs`: rc 0, 1 s.
  - `policy_lint.mjs --hooks`: rc 0, 6 s.
  - I did not run `machinery_ratchet.py --check-event`, which needs the CI event.
- So nothing in the tree is known to fail. The required check simply never concluded.
- **What unblocks it.** Re-run `governance / policy-docs` at this head. Once the gate reads GREEN, or APPROVAL-OWED for the budget raise alone, every finding of this review stands as a merge, with no further review owed for an unchanged head.
- If the job times out again at this head, the PR body owes a `## Red checks` answer for it (defect-root-cause.md).

## Findings

- Residual: line 9 of the PR body is stale at this head, as it already was at 7f4a9be8. It says "39 files changed, 578 insertions, 761 deletions (`git diff --shortstat 0a8033305d...HEAD`)". That command now prints `2216 files changed, 138804 insertions(+), 9608 deletions(-)` because 0a8033305d is far behind the merge base. The PR's own diff, `git diff --shortstat $(git merge-base origin/main HEAD)...HEAD`, is `40 files changed, 602 insertions(+), 755 deletions(-)`, the same at 7f4a9be8 and at this head (ev/delta_checks.txt). The sentence's claim, deletion over machinery, still holds. Only the figure and its base are stale. The fixer can refresh it at the next body edit. Carry: dismissed: body hygiene, no later stage reads the figure, and the PR's own measured diff (40/602/755) still deletes more than it adds

## Evidence

- **Round.** This is a delta round over the reviewed head 7f4a9be89c98d6ff59dc396c479b95b73b761cf6 (`Fix review: merge`). verdict/3451 holds 6 verdicts before this one (ev/verdict_ref_history.txt), so this is at least round 7. The rounds since the merge verdicts have been merge-of-main reconciles. The brief scopes this round as a delta and does not ask me to judge a re-cut.
- **Delta structure.**
  - `review_carry.py 7f4a9be8 93ba2271` prints FRESH-REVIEW, because c3149607 is a hand-resolved merge.
  - 1efe8398 and 93ba2271 are each the automatic merge of their parents. Their trees equal `git merge-tree --write-tree` of the parents: b7b0e388 and cd15f7d7 (ev/delta_checks.txt).
  - No `custom_components/` line is in the delta, so the scope does not widen.
- **The PR's own patch is unchanged.**
  - At 7f4a9be8 it is `git diff 29b3e5a74c...7f4a9be8`; at this head it is `git diff 13cbe48de4...93ba2271`. Both are `40 files changed, 602 insertions(+), 755 deletions(-)`.
  - Their sorted `+`/`-` line sets are identical: diff rc 0 (ev/delta_checks.txt).
  - So none of this PR's slimming is undone. Every line of the head outside the patch equals main at 13cbe48de4, so none of main's changes is lost, including the 12 lines main added to `bus.sh` in #3491.
- **The bus.sh conflict resolution.**
  - `git merge-tree --write-tree 2c69fb35 7f4a9be8` reports `CONFLICT (content)` in `tools/audit/seat/bus.sh` alone, as the body says.
  - At the head, main's `HPO_SEAT_GEN` guard is at the top of `dispatch()` (bus.sh:727-729), and main's two seat_gen arms come right before the PR's card C4 `dhid()` helper and the card C5 arm.
  - `bash tools/audit/seat/bus.sh --self-test` at the head on Linux prints `bus self-test: 239 checks, 0 failed`, rc 0 (ev/bus_selftest_head.txt). That is 237 + 2, as the body says. The body's two macOS-only FAILs do not reproduce on Linux, which matches its account.
  - **Mutant A, main's side.** I deleted the `HPO_SEAT_GEN` guard (bus.sh:727-729). The run prints `239 checks, 2 failed`, rc 1, with FAIL on `dispatch under a superseded HPO_SEAT_GEN refuses and records nothing` and on its null control. The control fails because the unrefused G1 dispatch records a row and shifts the count (ev/bus_selftest_mutantA_no_seatgen_guard.txt). So main's guard and arms are live inside the resolved block.
  - **Mutant B, this PR's side.** I deleted the card C4 `dhid()` helper. The run prints `239 checks, 34 failed`, rc 1 (ev/bus_selftest_mutantB_no_dhid.txt). So the PR's half of the union is load-bearing.
- **The two refreshed body lines match the tree at the head.**
  - Line 52: `grep -c proposal-triage dev/governance/config/policy_budgets.json` prints 2 at 93ba2271 and 2 at origin/main 60aefaf7.
  - The `budget-raise-gate` line under `## Red checks`: `git diff origin/main 93ba2271 -- dev/governance/config/policy_budgets.json` moves exactly `proposal-triage.md` lines 36 -> 40 and tokens 489 -> 563. `policy_lint.mjs --budgets` at the head prints `dev/governance/roles/proposal-triage.md 40 40 563 563` (ev/budgets_head.txt).
  - These resolve both findings of the previous verdict.
  - The `## Head` paragraph is also correct:
    - It names 93ba2271.
    - #3600, #3491, #3599 and #3603 are the merges in 29b3e5a7..2c69fb35.
    - `git merge-tree --write-tree 946eb6d2 c3149607` exits 0.
    - The conflict is in bus.sh alone.
- **The owner ruling on proposal-triage.md still holds.** `git diff --name-status $(git merge-base origin/main H)...H -- dev/governance/roles/proposal-triage.md` prints `M`, not `D`. `git diff 7f4a9be8 93ba2271 -- dev/governance/roles/proposal-triage.md` is empty, so the once-per-round shape the previous round verified is unchanged (ev/proposal_triage_diff.txt).
- **Budgets on the head merged with origin/main.**
  - `git merge-tree --write-tree origin/main 93ba2271` at origin/main 60aefaf7b0d1f53a932f184e1e41efc206c435d4 exits 0, tree b3b4f7bd0f0138deabf82497dd1a52dbd023fe4d (ev/merge_tree.txt). It merges cleanly.
  - On a commit of that tree, `node tools/policy/policy_lint.mjs --budgets` prints `corpus: ~69077 tokens, cap 69333 +band 500 = 69833`, rc 0 (ev/budgets_merged.txt). That is within the corpus cap.
  - It also prints:
    - `always-loaded ~3604 / 3849`
    - `CLAUDE.md 213 221 3604 3605`
    - `role fixer ~6279 / 6352`
    - `role record ~7236 / 7905`
    - `role policy ~10012 / 10458`
- **Versions.** The PR's own patch is identical to the one the previous round reviewed, which touches no `VERSION`, manifest, `RELEASE_NOTES.md` or claim file.
- **CI at this head, live.** The reds are:
  - `gate`: the owed block above.
  - `budget-raise-gate`: the owner's approval for the raise, which follows the verdict.
  - `governance / policy-docs`: cancelled.

  Everything else that is required is green. That includes `tests / closures`, `tests / fast (3.14)`, `governance / instrument-self-tests`, `tests / mutation` and `pr-contract / pr-contract` (run 43688486622).
- **Mutation.** The delta writes no production line. The targeted mutants are A and B above.

## Delta diff: git diff 93ba227138a2c024bf81e44e74f2b11cb572bd76 93ba227138a2c024bf81e44e74f2b11cb572bd76

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
