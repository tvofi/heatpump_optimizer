Triage batch 160 rules queue line 255 and records batch 157's owed P569 sampler result. It holds two rulings.

- **P572, ACCEPT, new group R10-HOTFIX-RESTORE-BASE-SKEW: PR-CONTRACT-GRADER-SKEW.**
  - On PR 3424, pr-contract checked out the merge ref 427c4ca874, whose base is main c620ebba96. It restored `roster_lib.py` from the payload's `pull_request.base.sha`, d08ed31049, which predates #3417. `carry_audit.py` is not restored, so it came from the merge ref and called a function the restored `roster_lib.py` lacks.
  - `base.sha` does not follow main, and a head push does not refresh it. 19 of 23 open PRs carry a stale one.
  - The same event base drives 18 restore sites in 6 workflows. The fix restores from the merge commit's first parent, kept separate from the diff bases, through one shared resolver.
  - The proposed planted-tree self-test is REJECTED. The detector question goes to the root-cause seat.
- **P573, DEFER: P569's condition is met only marginally.** The window 03:24:37Z-04:24:37Z peaked at 80.02%, crossing 4000 by one call. Scheduled callers (tick+beat+relay) were 50.8% by gh process-seconds and 45.4% by calls seen.

The diff is one file against the merge base: `dev/programme/triage/s6-batch160.md`, the rulings. No product behaviour changes.

## Head

`e4b28b394d7e04cc1b6ba105dab7f3f5d064c3f4`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P572 passes `triage_refusal`.
- A citation of P573 is refused as "not an ACCEPT ruling (DEFER)".

## Null control

- P574 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat dbd1ab5b07...e4b28b394d7e04cc1b6ba105dab7f3f5d064c3f4`: 1 file, 1 commit.
- Job log 130312858296 and the open pulls list come from the GitHub API at about 04:30Z, 2 calls.
- The sampler figures come from `rate2.log` and `ghproc.log` (local).
- The line numbers come from origin/main `dbd1ab5b07`.

## Red checks

`none`. The merge base is main `dbd1ab5b07`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
