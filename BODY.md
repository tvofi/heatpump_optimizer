R10-PROCESS-SLIM: cards C4, C5, C8 and C6 (a) of the slip study, plus the merge train's two defects (the post-merge docs step and the carry-ancestry park). Content approved by tvofi in chat 2026-11-05. C6 (a) is folded in by the main seat's ruling. Its half (b), the wake stream, is out of tree and not here.

**This round's change, by the orchestrator's ruling of 2026-11-08: C5 no longer deletes Nightly's `record-autofix` beat.** `tools/release/stamp.py` (code-owned) still depends on that beat in two places:
- its flush (rules 3-4) dispatches nightly.yml so that the beat merges a record pull request;
- its rule 5 (`--require-rows`) refuses a merged PR without the row the beat writes.

R10-FLY-STAMP-FLUSH-COST (#3296) is changing that flush now, so the beat's deletion is forward-carried to it (Forward-carry). `.github/workflows/nightly.yml` is byte-identical to origin/main again (`git diff --quiet origin/main HEAD -- .github/workflows/nightly.yml` exits 0).

Deletion over machinery throughout: 39 files changed, 557 insertions, 743 deletions (`git diff --shortstat fdc8d21adaa50a7feee534f08ee5edde9bda81ed...HEAD` at the head below). The diff writes 0 files under `custom_components/` (`git diff --name-only fdc8d21adaa50a7feee534f08ee5edde9bda81ed...HEAD -- custom_components` is empty). One cap pair is removed, for a deleted file (Raise justification). Claim files, `VERSION`, the manifest version and the notes heading are byte-identical to the merge base (prepr steps `no version edit` and `claim files`).

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

### This round's commits

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

## Head

491177c4b361a6a75a18e1e9e1d0f1533d630dc6 (`handoff/r10-process-slim`).

**Head note: this round is a merge-only resolution, for the same reviewer** (`fixer.md` step 6; no re-cut).
- 491177c4b361a6a75a18e1e9e1d0f1533d630dc6 merges origin/main fdc8d21adaa50a7feee534f08ee5edde9bda81ed into f30fb9a9f0c7e54587844adda6a2d75a37da3280 (no conflict), which merged origin/main 425b858495432c8dceb89d8d13866550352ba54f into 53ceaf58b04d110386afbb334e08bb471037a168 (no conflict), which merged origin/main daf8b349fd30cc60786eeca333a426b693aa4c5f (no conflict) into 97c49a85813a4971a5ba6bc537ef4481f51e15fd, the previous resolution head, which merged origin/main bb7dfb9b into the PR head 565f9f2b8a5efd9de1d260c241ee657aedc52576. The PR head is an ancestor of this head.
- The conflict, confirmed first: `git merge-tree --write-tree origin/main 565f9f2b` exits 1 with `CONFLICT (content)` in `dev/governance/roles/orchestrator.md` and `tools/audit/seat/INSTRUMENTS.md`; `git merge-tree --write-tree origin/main 97c49a85` exits 0, so none of this seat's three merges needed a hand edit (main moved to 425b8584, then fdc8d21a, while prepr ran, so it was merged again each time and prepr re-run). The resolution is 97c49a85's union, re-verified in this seat:
  - `orchestrator.md`: main's section-5 bullet "Each outside submission reaches a disposition" (tvofi 2026-11-06) is kept, followed by this branch's "A proposal is ruled directly" bullet, which replaces main's unchanged proposal-triage bullet (card C6 deletes `proposal-triage.md`). Main's two trims (the 2026-09-07 sentences in the preamble, the Round-10 sentences under "Look the instrument up") are kept; this branch's section-9 and L6 rewordings are kept.
  - `INSTRUMENTS.md`: main's `plan_public.py`, `outside_intake.py` and `hooks_setup.py` lines are kept, with this branch's `postmerge.py` wording.
- `git merge-base origin/main HEAD` is fdc8d21adaa50a7feee534f08ee5edde9bda81ed, the base of every three-dot figure here. `git diff --shortstat fdc8d21adaa50a7feee534f08ee5edde9bda81ed...HEAD`: `39 files changed, 557 insertions(+), 743 deletions(-)`, the same as at 97c49a85 against bb7dfb9b.
- Not in this head: the earlier step ref's 747e9065b, which moved `HOLD_MAX_AGE_S` into merge_train.py. With the beat kept, the constant stays in nightly.yml, as on main.

## Mutation proof

Each changed line was mutated by hand. A mutant was graded by the self-test or check named, and the file was restored after.
- **The beat (a210a9cec), whose deletion is the mutant.** At d70186a59, with the restored pins and without the beat:
  - `python3 -I tools/release/stamp.py --self-test` prints `FAIL hold: the bound is nightly.yml's own HOLD_MAX_AGE_S by source read` and `RESULT stamp_self_test=fail`;
  - `python3 tools/audit/seat/orchestrator_tick.py --self-test` prints `283 checks, 2 failed` (`FAIL MAIN D-1: nightly.yml's push-run jobs are exactly the record beat`, and its red-named pair);
  - `python3 tools/audit/seat/merge_train.py --self-test` prints `FAIL record_row.py takes every option the bot sweep passes, and the record beat merges behind the same --automerge-check ... --head ... --require-green guard`;
  - `PYTHONPATH=tests/hastub python3 tests/entities.py` stops with `ValueError: substring not found` at `_RAF_JOB_RAW = _workflow_job(_NIGHTLY_YML, "record-autofix")`.
  - At a210a9cec and at this head, the first three print `RESULT stamp_self_test=pass`, `283 checks, 0 failed` and `475 checks, 0 failed`. entities.py runs to its end, and its only reds are this container's two (Null control).
- **The fixture repair (e6a4a7dd3).** Without the two stub lines, `merge_train.py --self-test` prints `475 checks, 1 failed` (`FAIL a first TERM in batch 1's closing release stops the train`), three runs of three. With them it prints `0 failed`, three runs of three. The arm's own mutants (the old `SIG_IGN`, and a defer that never re-raises) still print `ok`, so the arm still separates them.
- **The policy text (2600a6b28)** has no executable line. `node tools/policy/rules_sync.mjs --check` exits 0, and `node tools/policy/policy_lint.mjs` prints `0 error(s)`.
- **The cards' own mutants are the earlier rounds'**, in `dev/audit/harnesses/r10_seat_selftests_mutants.py`. Their planted files are not changed by this round except the S12/S27 wrappers, which are back to main's text. MUTANT_CMD was left unset (prepr's diff-mutant step is report-only).

## Null control

- **origin/main 17e11579, the same container:**
  - `stamp.py --self-test` prints `pass`;
  - `merge_train.py --self-test` prints `472 checks, 0 failed`;
  - `entities.py` prints `2 of 2656 ENTITY CHECKS FAILED`. The two are "the coverage job reuses only an entry main's push run saved" and "the release ZIP holds the integration folder at its root". This head prints the same two, as `2 of 2648`; the 8 fewer checks are C5's delivery-status pins.
- **The container's, not the branch's:**
  - `bus.sh --self-test` prints `FAIL an ordinary append with no intervening fetch is the same commit object as before`, and `ref_privacy.py --self-test` prints `113 checks, 1 failed` (the machine-email author arm). Both fail identically at origin/main here, with or without the seat's `GIT_AUTHOR_*` variables, so they are left to CI.
  - `ci_predict.py --self-test` printed `1 failed` until `/opt/hpo/runner-temp`, the `RUNNER_TEMP` that this container's `BASH_ENV` sets, existed. It then printed `0 failed`.
- **The merge commit 5fa6b6a9c, before the restoration:** `stamp.py --self-test` prints `RESULT stamp_self_test=fail`, the red the previous seat measured on CI (`tests / fast (3.14)`, `governance / instrument-self-tests`).

## Figures

All re-taken in this seat at 491177c4b361a6a75a18e1e9e1d0f1533d630dc6, origin/main fdc8d21adaa50a7feee534f08ee5edde9bda81ed (read 2026-11-08T23:45Z):
- `python3 -I tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`.
- `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `283 checks, 0 failed`.
- `python3 tools/audit/seat/merge_train.py --self-test`: `567 checks, 0 failed` (the count is main's, which grew since the previous head's 475).
- `bash tools/audit/seat/handoff_push.sh --self-test`: `6 checks, 0 failed`.
- `bash tools/audit/seat/body_push.sh --self-test`: `35 checks, 0 failed`.
- `python3 tools/audit/seat/postmerge.py --self-test`: `18 checks, 0 failed` (main's count; 15 at daf8b349).
- `python3 tools/pr/ci_predict.py --self-test`: `0 failed` at 53ceaf58 (with `/opt/hpo/runner-temp` created; Friction 3); at this head it runs inside prepr's `ci predict` step.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs --budgets`: exit 0. `node tools/policy/policy_lint.mjs`: `0 error(s) across 49 policy file(s)`.
- `python3 tools/audit/seat/selftest_wiring.py --check`: `124 self-testing, 124 wired, 0 unwired`, `0 index gap(s)`.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tools/audit/archscore/score.py --diff fdc8d21adaa50a7feee534f08ee5edde9bda81ed HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff fdc8d21a...`: `MODE: FULL` (`.github/workflows/tests.yml changes the gate itself`), so CI runs the suite.
- **Resolution check, both conflicted files.** Rule: every `^#` heading of origin/main and of origin/fix/r10-process-slim is in the merged file (`comm -23` of sorted headings): all present for both sides in both files. Then every non-blank line of each side absent from the merged file was listed, and each one is the other side's deliberate edit since the merge base 4fe7d5934 (main's lines absent are this branch's rewrites of the proposal bullet, section 9 and L6, and the old `postmerge.py` line; this branch's lines absent are main's two trims). Null control: at the conflicted state those listings would include conflict markers and one side's whole hunk.
- **The merge carries the branch's delta unchanged.** Rule: `git diff --name-only origin/main HEAD` equals `git diff --name-only 4fe7d5934 origin/fix/r10-process-slim` (39 files each, `diff` exits 0), and for each of the 39 files the added and removed lines of `origin/main..HEAD` equal those of `4fe7d5934..565f9f2b`: `same delta` for 39 of 39. A file where the resolution dropped or added a line prints `DELTA DIFFERS`.
- `bash tools/pr/prepr.sh <body>`: clean at this head, `PRE-PR: 491177c4b361a6a75a18e1e9e1d0f1533d630dc6 00000000000000000000000000000000 rc=0` (gate mode `MODE: FULL`). origin/main read again at 2026-11-09T00:07:06Z: fdc8d21adaa5; unmoved since that run, so no second run is owed.
  - At 491177c4 the preceding run at f30fb9a9 refused in `ci predict` with `OSError: [Errno 39] Directory not empty: '/tmp/.../bg'`: orphaned background self-test processes of the replay (killed by PID) were still writing the directory being cleaned; the run below is clean.
  - Its `ci predict` step first refused at 53ceaf58 (`GRADER carry_audit.py check ... REFUSED by the base's copy ... 1 bad destination(s)`): the item `Carry: R10-FLY-STAMP-FLUSH-COST`, a group that exists only on the round's roster branch `handoff/audit-r10-roster` (05437723a). pr-contract's own step fetches that branch before `carry_audit.py check` (`.github/workflows/pr-contract.yml`, "Every finding the body records names its destination"), and `finding-propagation.md` counts it as in the tree; ci_predict's `ci_tree_run` grades in a `--shared` throwaway clone whose `origin/*` are the local repository's branches, so the ref was absent there. Control, a clone of origin/main daf8b349 alone: `carry_audit.py check` prints `BAD-DEST body item ada60feb: R10-FLY-STAMP-FLUSH-COST ... is not a group of the roster`; after fetching the round ref into it: `4 routed, 0 unrouted, 0 bad destination(s)`. The local branch `handoff/audit-r10-roster` was set to that ref (mirroring CI's fetch, nothing pushed) and prepr re-run. Friction r10-process-slim-4 records it.

## Red checks

At 491177c4b361a6a75a18e1e9e1d0f1533d630dc6 no check has run: a handoff ref runs no workflow.

The PR's present head is 565f9f2b8a5efd9de1d260c241ee657aedc52576, an ancestor of this head. Its check-runs (`pull_request_read get_check_runs`, 53 runs, one page):
- `gate` (128732022666, run 42472252325, `KIND: edit`) failed in 34 s with `FAIL run(s) [42472252157] at this head are still being judged; their gate decides`. It is the umbrella gate refusing to judge while the PR's main run was in flight; `gate` 128732517765 in that run 42472252157 passed two minutes later. Root-cause trigger: no cheaper detector exists — it is no defect of this diff but the gate's own wait answer, superseded by its pass.
- Every other concluded check is success or skipped, including `tests / fast (3.14)` (128731752355), `governance / instrument-self-tests` (128731775155), `pr-contract / pr-contract` (128732077508), `budget-raise-gate / budget-raise-gate` (128731750783) and `tests / nightly-status` (128731751712).
- The required gate reads red because the PR is `DIRTY` against main: GitHub cannot build the merge ref, so main's newer commits have not run against it. This head resolves that.
- Earlier reds at b2381acd5004e85a8b85a4643bc0939d25a3bf75 (`tests / fast (3.14)`, `governance / instrument-self-tests`: `stamp.py --self-test`'s hold check) were fixed by keeping the beat (Mutation proof), and are green at the PR head.

## Unpinned sites

n/a: the diff writes no line under `custom_components/`. This round's executable change is the restored nightly.yml, pinned by the restored checks, and one self-test fixture line, which its own arm and mutants grade.

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
- **The score:** re-run in this seat at 491177c4b361a6a75a18e1e9e1d0f1533d630dc6 (`python3 tools/audit/archscore/score.py --diff fdc8d21adaa50a7feee534f08ee5edde9bda81ed HEAD`).
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
- r10-process-slim-4: unenforced: `tools/pr/ci_predict.py`'s grader replay clones the local repository with `--shared`, so a carry to a group that lives only on the round's roster branch reads `BAD-DEST` there unless the seat holds a local `handoff/audit-r<N>-roster` branch, while pr-contract's own step fetches that ref and routes it (Figures, prepr). Carry: dismissed: a predictor false red with a one-command local remedy, outside this group's cards; the orchestrator may route it.
