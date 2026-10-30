R10-FLY-OPENPR-ATOMIC (#2719, fly-in, lane F). `open_pr.sh` opened the PR on its first push and then pushed the PR's own delivery row second; when prepr refused that row push (#2625, #2629: a nightly-status red CI reported after the first push), the PR stayed open with no row and the tick found it. Now a refused row push returns the opener's own worktree to the pushed head (the P13 fold, unchanged: the stuck row commit lives in `$HPO_STATE_DIR/pr/<topic>/wt`, not an `update_pr.sh` auto-reset), posts a comment quoting the refusal through `tools/pr/gh_comment.py` (which reads it back), and closes the draft (`open_pr: CLOSED: #N`). Only a close that itself fails falls back to the old `ROWLESS` line, for `update_pr.sh`'s `ensure_row`.

The PR is created only after the body contract passes: `tools/pr/app_push.sh` runs `prepr.sh` (step 7c ancestry reds included) and then the `ref_privacy.py guard` (`judge_commits`) before it mints a token, pushes, or POSTs the pull request. That part needs no change, so this diff does not touch it. On the first push the ancestry-reds step skips because origin has no branch yet (prepr step 7c's "no remote ref" skip), as the brief expects. The optional read of main's nightly-status before the first push is not built: the close covers the same failure, and the read would add a network dependency to every open.

Alternatives: (a) put the row in the first push. The PR number is not known until the POST, so this needs a placeholder row and a rename, a second commit anyway. (b) retry the row push after writing the red's answer. An opener cannot honestly write that answer for a fixer. (c) leave the PR open as ROWLESS (the old behaviour), which the tick sees. Closing is the smallest change that keeps every open PR with its row.

A re-run of `open_pr.sh` after a close opens a new PR from `fix/<topic>-pr`, because the closed one's local branch is kept. This group's own roster carry (V141, the merged-leftover branch helper) already owns that cleanup.

Carries (roster group R10-FLY-OPENPR-ATOMIC, as `review_packet.py` numbers them):
- Carry 1 (#2625/#2629, rowless PR): closed in this diff. A refused row push closes the PR with a read-back comment and leaves no stranded worktree; the self-test arm replays a body whose row push is refused.
- Carry 2 (P-D, exit-trap release): already on main (`pr_exit_trap` with `PR_TIDY` = `pr_release_wt`), and unchanged.
- Carry 3 (detach as the opener's last step): already on main. `pr_release_wt` runs in the EXIT trap after the last push, and this diff adds no push after it.
- Carry 4 (P71, default the Closes list from roster `fixes`): not in this diff. It needs `roster_lib` at the default ref inside the opener and is separable; it stays on the roster for the orchestrator.
- Carry 5 (P72, remove a clean worktree origin never had on REFUSE/STOPPED): already on main (`pr_release_wt`'s remove arm). This diff's merge-conflict arm exercises it again.
- Carry 6 (V64, auto-open in `cloud_relay.sh`): not in this diff. It edits `cloud_relay.sh`, outside this group's files, and builds on this atomic open; it stays on the roster.
- Carry 7 (V141, delete a merged leftover branch): not in this diff. It touches `pr_args.sh`'s helper and `handoff_push.sh`, and it stays on the roster. A closed PR's re-run opens from `fix/<topic>-pr` until it lands.
- Carry 8 (conflicted main merge kept as dirty): closed for `open_pr.sh`. The opener aborts its own conflicted merge and refuses, so `pr_release_wt` removes the clean worktree. This follows `update_pr.sh`'s `mut:holdabort` and `remerge_main.sh`'s abort. The `handoff_push.sh` seams are not in this diff (its file is outside the group) and stay on the roster.

## Head

`f32c80504b70d99c3b1ba154dd6e1da2017aa9fe`, cut from origin/main `b646e83062b1dd0487e52ceba8bd7e8d10c5b60c`.

## Mutation proof

These are in-tree mutants in `pr_args.sh`'s self-test (`bash tools/audit/seat/open_pr.sh --self-test`), which deletes the `# mut:<name>` line:
- `mut:rowclose` (the `gh pr close` line): the PR stays open without its row (the defect). The arm `mutant mut:rowclose (its line deleted): the PR stays open without its row (the defect); the next update_pr.sh lands it` asserts that no close was recorded and that the output says `ROWLESS`.
- `mut:rowreset`: the row commit stays unpushed on the branch in the opener's worktree.
- `mut:mergeabort` (carry 8, the `git merge --abort` line): the conflicted worktree is kept as dirty work. The arm `mutant mut:mergeabort (its line deleted): the conflicted worktree is kept as dirty work (the defect)` asserts that the worktree remains and the output says `it is dirty`.

Failing test first: the new self-test was run against origin/main's `open_pr.sh`. It printed `FAIL open_pr: a refused row push closes the PR with a read-back comment naming the refusal, and leaves no stranded worktree` and `FAIL open_pr: a main merge that conflicts is aborted and refused, and its clean worktree is removed`, and exited 1. At the head it passes.

## Null control

At the head, the success path (`racerun -`) still lands the row and detaches the worktree: the `open_pr: an update_pr.sh on its branch during its second push is BUSY, and the PR's row reaches origin` and `a successful open leaves its worktree detached at the pushed head` arms both pass, and no close happens there. The unmodified tree (origin/main `open_pr.sh`) leaves the PR open without its row: the FAIL above.

## Figures

- self-test at the head: `bash tools/audit/seat/open_pr.sh --self-test` exits 0, and every arm prints `ok`. The `pr_args self-test: N checks, 0 failed` line prints N=154 at the head, against N=151 at the merge base: three checks more (`grep -c '^  ok'` of the same output counts 157 at the base and 160 at the head). The delivery_row line is 6 checks, 0 failed at both.
- self-test with origin/main's `open_pr.sh` and the head's `pr_args.sh`: exits 1, and the only FAILs are the close arm and the merge-conflict arm.
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

none

## Friction

none
