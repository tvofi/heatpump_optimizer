Fix review: blocked d1ad4de812df6c3a97bfeb84d37ec11c7ff0095d dispatch-mismatch: PR #2455 at this head is a record-only delivery-row PR and contains no tools/release/stamp.py change to review

bus-nonce: 6925d791e5ebc70c8ff30d8dd091a430

Round: first. No earlier `Fix review:` comment is on #2455, which is a record-class PR with no review seat.

## What was measured
- The head I measured is d1ad4de812df6c3a97bfeb84d37ec11c7ff0095d (ev/HEAD). The PR head matches it: `record/autofix`, base `5b9c33d`.
- Three-dot diff against the merge base: two files, `dev/programme/delivery/2454.md` and `dev/programme/delivery/2455.md`, +2/-1 (ev/diff-stat.txt). The `tools/release/stamp.py` diff has 0 lines (ev/stamp-py-diff-lines.txt).
- PR title: "record: delivery rows for #2454 (autofix)". Author: hpo-author[bot]. The body says it is record-class, and mutation proof is n/a.
- `git merge-tree --write-tree origin/main d1ad4de812df6c3a97bfeb84d37ec11c7ff0095d` exits 0, so the merge is clean (ev/merge-tree.txt).

## Why blocked
The dispatch describes a stamp.py fix that restores suspended may-drift entries verbatim when the stamp empties the claim list. #2455 contains no such change. That leaves nothing to test against the v7.0.0 claimed_drift.txt, no stale-note or malformed-note behaviour to mutate, and no stamp to simulate for `env_drift.py --claims-only HEAD^1`. Returning `merge` here would record the stamp fix as reviewed when it never was.

On origin, the branches that touch tools/release/stamp.py relative to main are `handoff/r10-stamp-claims` and `handoff-body/r10-stamp-claims` (ev/candidate-stamp-branches.txt). The fix is most likely there. It may not have a PR yet, or it may have a different number. The orchestrator should re-dispatch with the right PR number and head. I did not review those branches, because a review binds to the PR and head it was dispatched for.

This verdict says nothing about the record PR itself. Per its body it merges under `record_row.py --automerge-check` with no review seat.
