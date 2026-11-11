Triage batch 158 rules queue line 253: the orchestrator asked whether the gh shim batch 157 said to install is safe to install today. It holds one ruling: P570, ACCEPT.

- **P570, ACCEPT: S14-GH-SHIM-INSTALL-RISK.**
  - On main, the shim's record-issue guard admits a post only from the one tree whose `gh_comment.py` path the installer bakes in (`seat-gh` line 338).
  - `record_beat.py` and `outside_intake.py` run `gh_comment.py` from their own checkout. So installing the shim today would refuse their record posts from every other worktree.
  - Batch 157's owed item 1 is withdrawn as written. A log-only copy and a symlink bake are both rejected.
  - Open PR 3427 (R10-GH-READ-RESIDUE, P449) already admits any registered worktree's tracked `gh_comment.py`. It has a self-test, two null controls and a mutant.
  - The install follows that merge, from a branch-backed worktree that is never rotated. No carry.

The diff is one file against the merge base: `dev/programme/triage/s6-batch158.md`, the ruling. No product behaviour changes.

## Head

`6ab8a9b1005ae9c0b5808755915ef8349d81acda`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- A citation of P570 passes `triage_refusal`.
- With P570's verdict flipped to REJECT, its citation is refused as "not an ACCEPT ruling (REJECT)".

## Null control

- P571 is refused as "no such entry".
- With the file absent, a citation is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 444cf62fab...6ab8a9b1005ae9c0b5808755915ef8349d81acda`: 1 file, 1 commit.
- The line numbers come from origin/main `444cf62fab`. PR 3427's diff is three-dot against its merge base at head `7cbfa68013`.
- The worktree list comes from `git worktree list --porcelain` on this host.

## Red checks

`none`. The merge base is main `444cf62fab`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
