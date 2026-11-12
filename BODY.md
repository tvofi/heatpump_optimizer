The train now waits on a running stamp (carry 1, P447): a stamp that pushes publishes `refs/heads/stamp-hold`, and `Train.land` waits on it before each merge attempt. Part 1 of 4 of R10-TRAIN-RESIDUE-P2 (carries 0-4).

## Head

818466419f7b67b2b19982fb2d16ed37ee765ba5, measured 2026-11-12T07:30Z against origin/main 289c9b99 (merge base be86e36a).

## Mutation proof

Deleting the `self.stamp_hold_wait()` line in `land` and running `python3 tools/audit/seat/merge_train.py --self-test` turns red: `stamp hold: a live hold logs STAMP-HOLD and waits, and the merge runs only after it clears` and `stamp hold: a hold past the age bound is a dead holder's, taken over, and the merge runs`. Restored, all green. `stamp.py --self-test` covers the take/release arms (four `stamp hold:` checks).

## Null control

With no hold the merge runs as today with zero polls (`stamp hold: null control, no hold runs the merge as today with no wait`); a rehearsal (`batch/`) train never waits; an unarmed stamp (no `--push`, or `--dry-run`) pushes nothing.

## Figures

- `git grep -c -- '--require-rows' HEAD -- tools/release/stamp.py` (carry 4 precondition): 8, not 0.
- `python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/release/stamp.py --self-test`, `python3 tests/entities.py`, `python3 tests/doc_claims.py`: all pass at the head.

## Red checks

none

## Forward-carry

- Carry 0 (P444, undraft gap): no code in `tools/` drafts a pull request on the recarry/update path (`gh pr ready --undo` appears only in `open_pr.sh` and `handoff_push.sh`), so a head cannot become a draft through the train. The #3318 shape (a `--queue`/`build_queue` entry with no `draft` key) is the one carry 17 fixed at be86e36a (`record_drafts` reads it for every key-less entry; an author's later draft is left a hold, null control in the self-test). The train log naming #3318's admission path is not in this checkout, so that confirmation is not made here. Carry: dismissed: implemented at be86e36a5
- Carry 1: built in this pull request. stamp.py: `stamp_hold` (taken before rule 1, so the gate wait is covered; released on any exit); merge_train.py: `stamp_hold_wait` before each merge attempt in `land`, which both `batch` and `add`-started trains reach. `add` itself merges nothing. A hold at or past `STAMP_HOLD_MAX_AGE_S` is a dead holder's and is taken over. web-stamp.js is unchanged: it runs stamp.py, which takes the hold. Alternative rejected: a second flag file the workflow writes, which a crashed workflow would leave with no age. Carry: dismissed: built in this pull request
- Carry 2 (name the sender of live-head cancels, then P267's bounded pause): the sender is named from GitHub's run actors, which this seat cannot read, and the bounded pause is P267's. Carry: R10-CI-PRIORITY-PAUSE
- Carry 3 (App-actor cancels at a live head; whether a run's actor is its canceller is unestablished): needs the runs API and `dev/audit/harnesses/livehead_cancels.py`, not measured here. Carry: R10-CI-PRIORITY-PAUSE
- Carry 4 (delete Nightly's record-autofix beat): precondition not met, the `--require-rows` count above is 8. Carry: R10-CI-PRIORITY-PAUSE
- Carry 5: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 6: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 7: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 8: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 9: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 10: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 11: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 12: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 13: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 14: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 15: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 16: marked [implemented: be86e36a560fde88cc758cefcee322b9087a5deb] on the roster, not answered here. Carry: dismissed: implemented at be86e36a5
- Carry 17: marked [implemented: be86e36a560fde88cc758cefcee322b9087a5deb] on the roster, not answered here. Carry: dismissed: implemented at be86e36a5
- Carry 18: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 19: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 20: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 21: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it
- Carry 22: belongs to another part of this group and is not answered here. Carry: R10-TRAIN-RESIDUE-P2 | dismissed: not this part, its own part of the group answers it

## Friction

none
