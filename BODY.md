R10-PROCESS-SLIM: cards C4, C5, C8 and C6 (a) of the slip study, plus the merge train's two defects (the post-merge docs step and the carry-ancestry park). Content approved by tvofi in chat 2026-11-05. C6 (a) is folded in by the main seat's ruling. Its half (b), the wake stream, is out of tree and not here.

**The previous round's change, by the orchestrator's ruling of 2026-11-08: C5 no longer deletes Nightly's `record-autofix` beat.** `tools/release/stamp.py` (code-owned) still depends on that beat in two places:
- its flush (rules 3-4) dispatches nightly.yml so that the beat merges a record pull request;
- its rule 5 (`--require-rows`) refuses a merged PR without the row the beat writes.

R10-FLY-STAMP-FLUSH-COST (#3296) is changing that flush now, so the beat's deletion is forward-carried to it (Forward-carry). `.github/workflows/nightly.yml` is byte-identical to origin/main again (`git diff --quiet origin/main HEAD -- .github/workflows/nightly.yml` exits 0).

Deletion over machinery throughout: 39 files changed, 557 insertions, 743 deletions (`git diff --shortstat bb7dfb9bd6c68548d1a956adc411be91e02965e0...HEAD` at the head below). The diff writes 0 files under `custom_components/` (`git diff --name-only bb7dfb9bd6c68548d1a956adc411be91e02965e0...HEAD -- custom_components` is empty). One cap pair is removed, for a deleted file (Raise justification). Claim files, `VERSION`, the manifest version and the notes heading are byte-identical to the merge base (prepr steps `no version edit` and `claim files`).

### What changes, per card

- **C4 (verdict carry):** when `bus.sh dispatch` is given no `--reviewed-head`, it derives one from `verdict/<pr>`'s latest `Fix review: merge <sha>` (`last_merge_verdict`).
  - The existing `review_carry.py` refusal therefore applies by default, and a second reviewer at the very head that a merge verdict names is refused.
  - The carry predicate is unchanged (`app_approve.sh --carry`).
  - `fix-review.md` step 12 states it.
- **C5 (paperwork is a note):** `fix-review.md` blocks only on code, tests and harness. `carry-missing` and `root-cause-*` become `Note:` lines, and a note on `custom_components/` is still a block. No seat writes a per-PR delivery row:
  - `bus.sh dispatch` no longer demands a row;
  - `handoff_push.sh` no longer writes one;
  - `governance / delivery-status` and `delivery-status-publish` are deleted;
  - `governance / record`'s refusal step is report-only;
  - **kept, unlike the earlier rounds:** Nightly's `record-autofix` beat, its `push:` trigger and `HOLD_MAX_AGE_S`. The beat still rows each merge from API facts. `record_row.py`'s plan covers both a rowless merge and a merged PR whose row reads `**open**`, so a PR that `handoff_push.sh` no longer rows is still rowed for rule 5.
- **C8 (review after the cheap checks):** `bus.sh dispatch` on a WAIT head refuses while any of `CHEAP_CHECKS` is still in flight. `bus.sh post` refuses a `merge` verdict at a head that `merge_train.py classify` calls RED, or whose classification it cannot read.
- **C6 (a):** `dev/governance/roles/proposal-triage.md` is deleted. Its two cap keys and its phantom `tests/closures.json` entry go with it.
- **Train docs step: removed** from `postmerge.py`. `release_worktrees` logs `released <wt> (already collected)` for a worktree that `worktree_gc.sh` already collected.
- **Train carry ancestry: fixed** in `app_approve.sh carry()`.
- **Carry 2, superseded by main:** main's R10-HOTFIX-SELFTEST-TIMEOUT now starts the slow self-tests detached (timeout 30), so this branch's timeout-40 hunk and its `open_pr.sh`/`update_pr.sh` change are dropped in favour of main's (Merge resolution).

### The previous round's commits

- 5fa6b6a9c: merges origin/main 17e1157925908bd69addb58ed824c1ac22bfa82f. `git merge-tree --write-tree origin/main b2381acd` reported a conflict (rc 1), so the merge was owed under the 2026-11-07 ruling.
- d70186a59: restores main's pins on the beat, unchanged, failing first:
  - `tests/entities.py`: the record-autofix wiring, the train hold, the batch gate, the rate-limit and the push-trigger checks;
  - `merge_train.py`: the batch self-test's guard read;
  - `orchestrator_tick.py`: the MAIN D-1 push-run pin.
- a210a9cec: `nightly.yml` restored to origin/main.
- 2600a6b28: the record text corrected. `delivery-status-tracking.md` item 1, CLAUDE.md's index row, `orchestrator.md` section 9 and `dev/README.md` said that no row is written and that merged rows gate nothing. Both claims are false while the beat runs. They now say that no seat writes a row and that the beat does, which the stamp reads.
- e6a4a7dd3: a test-only repair of a semantic merge interaction in `merge_train.py`'s unwind self-test (Merge resolution).

### Merge resolution (origin/main 17e11579)

- **`.github/workflows/governance.yml` (three hunks).** Main's R10-HOTFIX-SELFTEST-TIMEOUT runs `open_pr.sh`, `pr_args.sh` and `update_pr.sh`'s self-tests detached, and its read steps grep `pr_args self-test` in the output of `open_pr.sh` and `update_pr.sh`.
  - Kept: main's timeout comment and `timeout-minutes: 30`, and main's removal of the in-line open-pr and update-pr steps.
  - Because main's steps read the `pr_args` tally, `open_pr.sh`, `update_pr.sh` and the harness's S12/S27 wrapper mutants take main's text. This branch's carry 2 is superseded.
- **`dev/governance/roles/fix-review.md` (one hunk):** union, with main's "Evidence names differ beyond case." inside the branch's paragraph.
  - The union was 9 tokens over the file's `files_tokens` cap.
  - Paid by dropping two attribution dates from the branch's own added lines (C4's and C5's).
  - `node tools/policy/policy_lint.mjs`: `0 error(s) across 49 policy file(s)`.
- **The semantic interaction, repaired in a test only (e6a4a7dd3).**
  - The interaction: main's new batch-seam arm, "a first TERM in batch 1's closing release stops the train", waits for a stubbed `git worktree remove`. This branch's `release_worktrees` skips a worktree that git does not list and that does not exist. The driver's stub listed none, so `/x` was skipped and the arm failed.
  - The repair: the stub now lists `/x`, as in life. Production is unchanged.

### Merge resolution (origin/main bb7dfb9b, this round)

The merge train skipped PR head 565f9f2b8a5efd9de1d260c241ee657aedc52576: `git merge-tree --write-tree origin/main 565f9f2b8a5efd9de1d260c241ee657aedc52576` reported two conflicts (rc 1). Commit 97c49a85813a4971a5ba6bc537ef4481f51e15fd merges origin/main bb7dfb9bd6c68548d1a956adc411be91e02965e0 into it. It changes nothing beyond the resolution.

**The two conflicted files:**
- **`dev/governance/roles/orchestrator.md`, section 5 (one hunk).**
  - Kept from main: its new bullet "Each outside submission reaches a disposition (tvofi, 2026-11-06)", which names `outside_intake.py`, verbatim.
  - Kept from this branch: its bullet "A proposal is ruled directly, by the owner or by you" (card C6), verbatim.
  - Main's bullet "A proposal goes to `proposal-triage.md` before it is routed" is dropped. Main did not change that bullet (`git diff 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50 origin/main -- dev/governance/roles/orchestrator.md` shows no edit to it). It is the text this branch replaced, because card C6 deletes `proposal-triage.md`.
  - Main's two silent edits to this file (two shortened paragraphs: the opening "Your pull requests are reviewed" and section 13's "Look the instrument up") merged without conflict and are kept.
- **`tools/audit/seat/INSTRUMENTS.md` (one hunk).**
  - Kept from main: its two new index lines, `plan_public.py` and `outside_intake.py`, verbatim.
  - Kept from this branch: its `postmerge.py` line, "the state docs are the plan-beat's".
  - Main did not edit the `postmerge.py` line.

**The files git merged without conflict**, each read back:
- `.github/workflows/governance.yml`: main's two new instrument-self-tests steps (`plan_public.py`, `outside_intake.py`) are present. This branch's deletion of the `delivery-status` and `delivery-status-publish` jobs and its record step's `continue-on-error` are also present. The hunks do not overlap.
- `dev/governance/roles/standing-dispatch.md`: this branch's Dispatch line ("cards C4, C8 refuse there", no delivery-row check) and main's reworded fire-owed sentence are both present. So are main's **Answer** `owed=answer` sentence and its two shortened paragraphs.
- `tools/audit/seat/sweep_template.md`: main's `intake_since` overlay row and step (5b) are present, and so is this branch's step (7), the direct ruling.
- `tests/entities.py`: main's Pages plan-page check is present, and this branch's removal of the delivery-status pins is kept.
- `tests/closures.json`, merged by the ledger driver: main's three new `tools/audit/seat` entries are present (`outside_intake.py`, `outside_intake_selftest.py`, `plan_public.py`). This branch's removal of the phantom `proposal-triage.md` entry is kept.
- **Budget files:** main changes no `*_budgets.json` since the merge base (`git diff --name-only 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50 origin/main -- '*budgets*.json'` is empty). This branch's `policy_budgets.json` change is therefore unchanged, and no cap moves in the merge.

**Whole-diff proof that neither side lost content.** The branch's three-dot diff against main has the same changed lines before and after the merge:
- the changed-line set of `git diff 4fe7d5934b0a4bc092c9398f29b579fbd2df8b50...565f9f2b8a5efd9de1d260c241ee657aedc52576` equals that of `git diff bb7dfb9bd6c68548d1a956adc411be91e02965e0...HEAD`, line for line;
- `--numstat` is identical too.

So every line this PR changed is still changed, and every line main added is in the head, because it is absent from the branch's diff (Figures).

**Left as main wrote it: a semantic interaction.** Main's new `tools/audit/seat/outside_intake.py` has a docstring, at its `triage or design it` line, that cites `proposal-triage.md`. This branch deletes that file.
- Nothing in prepr refuses this: `policy_lint`, `brief_lint` and the self-test step are all ok.
- The citation is in main's own new file, so editing it is beyond this resolution. The next seat touching `outside_intake.py` should point the citation at `orchestrator.md` section 5. It is not a Carry line here, because this seat may not write the round's roster, which `body_push.sh` needs a carry landed on; it is left to the orchestrator to route.

## Head

97c49a85813a4971a5ba6bc537ef4481f51e15fd (`handoff/r10-process-slim`).
- It is the merge of origin/main bb7dfb9bd6c68548d1a956adc411be91e02965e0 into the PR head 565f9f2b8a5efd9de1d260c241ee657aedc52576 (first parent).
- `git merge-base origin/main HEAD` is bb7dfb9bd6c68548d1a956adc411be91e02965e0, the diff base for every three-dot figure here.
- Every figure here was measured at this head.
- `handoff-wip/r10-process-slim` was kept fast-forward with a wip side merge whose tree is this head's tree, as the earlier rounds did. That wip commit is not this head.

## Mutation proof

This round is a conflict resolution. It adds no executable line: the two resolved hunks are Markdown. The earlier rounds' mutation proof covers the cards' own lines and is unchanged. Its record is in this PR's previous body: the beat's restored pins, the fixture repair e6a4a7dd3 and `dev/audit/harnesses/r10_seat_selftests_mutants.py`.

**Diff mutants (owner ruling 2026-11-07).** The run covered every Python line this PR adds against bb7dfb9b, all 75 mutants that `mutant_run.py --list` enumerates (30 in `merge_train.py`, 4 in `postmerge.py`, 41 in `ci_predict.py`).
- **prepr's own diff-mutant step could not run them.** With `MUTANT_CMD` set to the three self-tests, it printed `BASELINE FAILS: the command fails on the unedited tree; no mutant was run`.
  - The cause is that prepr runs the step in its default `git archive` copy. In that copy `ci_predict.py --self-test` fails on the unedited tree with `FAIL the plants have a landed retired file to re-add ...`, because its fixtures need a git checkout.
  - `postmerge.py` and `merge_train.py` pass in that copy.
- **So the run was made directly, in place, in a clean detached worktree at this head:**
  `python3 -I tools/audit/seat/mutant_run.py --diff bb7dfb9bd6c68548d1a956adc411be91e02965e0...HEAD --cmd "bash <scratch>/mutcmd_inplace.sh" --in-place --max-mutants 0 --report-only`
  - The command runs the self-test of whichever of the three files differs from HEAD.
  - Its baseline runs all three, and it passed: no `BASELINE FAILS` line was printed.
- **Result:** 20 SURVIVED and 55 killed, rc 0 (report-only), wall time 6691 s. Each survivor has a disposition under Unpinned sites.

## Null control

- **The resolution proof can fail.** Diffing the unmerged PR head against the new main, `git diff bb7dfb9bd6c68548d1a956adc411be91e02965e0 565f9f2b8a5efd9de1d260c241ee657aedc52576`, does not give the branch's changed-line set: `diff -q` reports DIFFERS, across 64 files, +603/-2120. That diff shows main's newer content as reverted. The merged head reproduces the branch's own set exactly.
- **`tests/entities.py` at origin/main bb7dfb9b, in this container:** `3 of 2666 ENTITY CHECKS FAILED`. The three are:
  - "the coverage job reuses only an entry main's push run saved";
  - "the release ZIP holds the integration folder at its root";
  - "the Pages workflow stages the round's plan page ...".
- **At this head:** `3 of 2658 ENTITY CHECKS FAILED`, the same three names. The 8 fewer checks are C5's delivery-status pins, as in the previous round. These three are this container's reds, not the branch's.
- **The diff-mutant step:** `ci_predict.py --self-test` prints `0 failed` in the git worktree and fails in a `git archive` copy. That is why prepr's step read BASELINE FAILS (Mutation proof).

## Figures

- `bash tools/pr/prepr.sh` at 97c49a85813a4971a5ba6bc537ef4481f51e15fd: `PRE-PR: 97c49a85813a4971a5ba6bc537ef4481f51e15fd ... rc=0`. Its details:
  - gate mode `MODE: FULL`;
  - `closures` skipped by prepr itself ("the diff cannot be scoped, so CI re-records every closure");
  - `diff mutants` printed BASELINE FAILS (Mutation proof).
  - origin/main then moved to 8a4974d1522f979f5b1c837df8e3a76b535bf35e (read 2026-11-08T16:05Z). `git merge-tree --write-tree origin/main HEAD` reports no conflict (rc 0). So, under the owner's 2026-11-07 ruling, main is not merged and prepr is not re-run; the merge train re-carries the head on the current main.
- `git diff --numstat` of `4fe7d5934b0a4bc092c9398f29b579fbd2df8b50...565f9f2b8a5efd9de1d260c241ee657aedc52576` against that of `bb7dfb9bd6c68548d1a956adc411be91e02965e0...HEAD`: `diff` exits 0. The changed-line sets of the same two diffs (the `^[+-]` lines minus file headers) also give `diff` exit 0.
- `git diff --shortstat bb7dfb9bd6c68548d1a956adc411be91e02965e0...HEAD`: 39 files changed, 557 insertions(+), 743 deletions(-).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/rules_sync.mjs --check`: rc 0. `node tools/policy/policy_lint.mjs`: its last line is the fixture line, `FIXTURE ok`; prepr's `policy_lint` step is ok.
- `python3 tools/audit/archscore/score.py --diff bb7dfb9bd6c68548d1a956adc411be91e02965e0 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: `0 index gap(s)`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `567 checks, 0 failed`.
- `python3 tools/audit/seat/postmerge.py --self-test`: `15 checks, 0 failed`.
- `python3 tools/pr/ci_predict.py --self-test`: `0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: `3 of 2658` at this head and `3 of 2666` at origin/main (Null control).
- `tools/audit/seat/mutant_run.py --diff` in place: 75 mutants, 20 SURVIVED, wall time 6691 s (Mutation proof).
- `bash tools/audit/seat/cloud-setup.sh --check`: OK, with python3 from venv-ci.

## Red checks

At 97c49a85813a4971a5ba6bc537ef4481f51e15fd no check has run: a handoff ref runs no workflow.

**At the PR head 565f9f2b8a5efd9de1d260c241ee657aedc52576**, read once with the check-runs API (`filter=latest`, 53 runs), the only failure is:
- **`gate`** (128732022666), which printed `FAIL run(s) [42472252157] at this head are still being judged; their gate decides`. That is an early sweep at the head while its runs were in flight, not a content red. This head supersedes it.

**Earlier pushed commits of this branch** (prepr's ancestry read names `budget-raise-gate / budget-raise-gate`, `governance / instrument-self-tests`, `tests / fast (3.14)` and `tests / nightly-status`). They were answered by the previous round at b2381acd5004e85a8b85a4643bc0939d25a3bf75, and the answers stand:
- **`tests / fast (3.14)`** (128481970498) and **`governance / instrument-self-tests`** (128481970080). Class: this PR's diff, through its merge with main. Both fail on `stamp.py --self-test`'s `FAIL hold: the bound is nightly.yml's own HOLD_MAX_AGE_S by source read`. Main's #3280 added that check after the old merge base, and C5's beat deletion removed the line it reads. Answer: fixed here, because the beat is kept and `stamp_self_test=pass` (Mutation proof). Root-cause trigger: the cheaper detector exists. It is prepr's self-test step at a head merged with main, which is what this round ran. Its standing cost is nil beyond the merge the ruling already owes on a conflict, so no countermeasure is added.
- **`pr-contract / pr-contract`** (128493151057): it refused a body that did not name `tests / fast (3.14)`. Answered by this entry. `prepr.sh --body-check` runs the same check before the push.
- **`gate`** (128493523507, 128481472549, 128476564557): the umbrella over the reds above. It clears with them.
- **`budget-raise-gate / budget-raise-gate`** (128481970199, 128480546680, 128476230798). Class: policy, expected. It reads the removal of the deleted `proposal-triage.md`'s two caps as a raise, and clears on the owner's review or on the mandate line under Raise justification.
- **`tests / nightly-status`** (128481970037). Class: inherited from main. It graded main's cancelled dispatch 42369836867, and main's next dispatch, 42382408131, concluded success. The grader reads nightly.yml's lanes, and nightly.yml is now main's byte for byte.
- Code-scanning alerts were not read in this seat: `local_alerts.py` got HTTP 403 on `code-scanning/analyses`. pr-contract reads them and fails closed.

## Unpinned sites

The diff writes no line under `custom_components/`. The 20 diff-mutant survivors are all on lines the earlier rounds of this PR added; this round adds none. This seat's brief bars any change beyond the resolution, so no pin is added here. Each survivor's disposition follows.

**`tools/audit/seat/merge_train.py`, 4 sites, all inside `--self-test`'s own fixtures and assertions, none in production:**
- 5125 CONST_SWAP: the worktree-list stub's rc.
- 5141 CONST_SWAP: the `Train(...)` fixture's argument `1`.
- 5150 CALL_DEL: one `check(...)` call, the null control "while one still registered is removed".
- 5151 CONST_SWAP: `remove_rc=128` becomes 129, an equivalent mutant.

A self-test fixture or assertion is not behaviour a mutant measures. The release arm's production lines killed their own mutants.

**`tools/pr/ci_predict.py`, 16 sites, in the STEP REPLAY arm** (`instrument_steps`, `names_changed`, `replay_step`, `step_replay_preds`, `step_replay_self_test`) and its remediation hint:
- 521 to 525 (GUARD_OFF, CMP_BOUND and CONST_SWAP on `at < 0`; RETURN_DEL; the two `+ 1` slice bounds): the missing-job guard and the job slice. Unpinned: no fixture has a governance.yml without the job, or a job at offset 0.
- 549 RETURN_DEL: `names_changed`'s final `return False`. It is equivalent in truthiness (`None`).
- 560 CONST_SWAP: `capture_output=False` only lets output through, so it is equivalent for the rc.
- 562 RETURN_DEL and CONST_SWAP: the timeout's rc 124. No fixture times out.
- 576 to 577 GUARD_OFF and RETURN_DEL: the no-reds early return. It is equivalent in output: with no reds the loop appends nothing, and only a needless worktree is made.
- 595 CALL_DEL: the base worktree's `remove` in `finally`. It is cleanup the self-test does not observe.
- 603 CALL_DEL and CONST_SWAP: the self-test's `sys.path.insert` of `tests/`. It is equivalent when `tests/` is already on the path.
- 1222 GUARD_OFF: the STEP REPLAY remediation hint. No fixture prints the hint.

They are not a Carry line here, for the same reason: this seat may not land a carry on the roster branch. The orchestrator routes them. The pins should land with the next code change to the STEP REPLAY arm, or as survivor_triage records under `tests/mutation_ledger/survivor_triage/` for the equivalents (549, 560, 576-577, 603). CI's mutation-autofix lane does not reach `tools/`.

## Approval

Content approved by tvofi in chat 2026-11-05 (cards C2-C9 accepted; C4, C5, C8 and C6 (a) are this group's). tvofi posts the approving review at the head.

**Policy sentences this round changes**, beyond the round-2 list the verdict holds:
- `delivery-status-tracking.md` item 1 changes. It read "There is no per-PR `dev/programme/delivery/<N>.md` row and no record pull request ... the rows already merged stay as history, read by nothing that gates". It now reads "No seat writes a per-PR ... row (card C5 ...). Nightly's `record-autofix` beat still rows each merge from API facts, because `tools/release/stamp.py`'s flush and `--require-rows` read those rows (orchestrator ruling 2026-11-08, until R10-FLY-STAMP-FLUSH-COST retires them)."
- CLAUDE.md's `delivery-status-tracking.md` row: "no per-PR row" becomes "no seat writes a per-PR row".
- `orchestrator.md` section 9: "no per-PR row (card C5)" becomes "no per-PR row from you (card C5)".
- `fix-review.md`: main's "Evidence names differ beyond case." is unioned in, and "(card C5, tvofi 2026-11-05)" and "(card C4, tvofi 2026-11-05; #1667, 2026-10-27)" lose their dates. That is the cap payment.

The round-2 sentences that said the beat is deleted are no longer in the diff.

## Raise justification

Raise approved under mandate (comment 6624093439, scope all) by the orchestrator 2026-11-06 14:4xZ: cap removal for a deleted file, no payment possible.
- **What moves:** no cap rises in substance. The two caps removed belong to `dev/governance/roles/proposal-triage.md` (`files` 36, `files_tokens` 489, in `dev/governance/config/policy_budgets.json`), and card C6 (a) deletes that file.
- **Why a cap must go:** `policy_lint.mjs --budgets` refuses a cap on a missing file, so keeping them is refused too.

Payments tried: keeping the caps (refused by `policy_lint.mjs --budgets`); keeping the file as an on-demand contract (rejected, because card C6 retires the seat and an unread contract is spent prose).

- **The other policy files:** each one this diff touches is paid inside its own cap. This round's `fix-review.md` union is paid by the two dates.
- **The score:** re-run in this seat at 97c49a85813a4971a5ba6bc537ef4481f51e15fd (`python3 tools/audit/archscore/score.py --diff bb7dfb9bd6c68548d1a956adc411be91e02965e0 HEAD`).
Architecture score: dS +0.0000 NULL

## Forward-carry

- Delete Nightly's `record-autofix` beat once no stamp rule reads it. That deletion covers:
  - its `push:` trigger and `HOLD_MAX_AGE_S`;
  - `merge_train.py`'s train hold (`hold_refresh`, `HOLD_REF`) and the stamp's `hold_bound_s`/`train_hold`/`record_flush` arms;
  - `record_row.py`'s `governance / delivery-status` red name (that job is deleted by this PR);
  - the pins this PR restored in `tests/entities.py`, `merge_train.py` and `orchestrator_tick.py`.

  The stamp's flush (rules 3-4) and rule 5 (`--require-rows`) still read the beat, and that group is changing the flush now (orchestrator ruling 2026-11-08). Carry: R10-FLY-STAMP-FLUSH-COST

## Carries

- **Carry 1** is the roster's carry on R10-PROCESS-SLIM: a repair body's `## Head` named the previous handoff. `tools/audit/seat/body_push.sh` now refuses `head-stale` when `## Head` does not name `handoff/<topic>`'s code sha. The check runs after the identity guard (round 3) and pushes nothing. It is unchanged by this round, and `body_push.sh --self-test` prints `35 checks, 0 failed`.
- **Carry 2** is the instrument-self-tests timeout. Main's R10-HOTFIX-SELFTEST-TIMEOUT answers it now, by running the slow self-tests detached under the 30-minute timeout. This branch's own answer (`open_pr.sh` and `update_pr.sh` no longer re-running `pr_args.sh`'s self-test, and a 40-minute timeout) is dropped in the merge in favour of main's (Merge resolution).

## Friction

- r10-process-slim-1: cost: with the record stream retired, `merge_train.py --bot-prs` (`sweep_bots`) likely has nothing left to merge; this was not measured here. Carry: dismissed: unmeasured, and deleting a live train path is beyond the cards' scope.
- r10-process-slim-2: unenforced: `bus.sh`'s C8 gate cannot see a cheap check GitHub has not yet created. Carry: dismissed: the card's risk line accepts review starting early, never a merge at red.
- r10-process-slim-3: unenforced: the container's `BASH_ENV` sets a `RUNNER_TEMP` it does not create, so `ci_predict.py`'s STEP REPLAY self-test reads red in a fresh cloud seat until the directory exists. Carry: dismissed: environment setup, not this diff's code; the measured fix is one `mkdir`.
