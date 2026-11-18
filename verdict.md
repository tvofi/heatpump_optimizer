Fix review: merge 4d7c80e6eb05a70f68ab5498ebedfb42efa404ee

bus-nonce: 2f297ef6b20e5fca364293fca3c1bf38
pending-ci: gate

## Scope

Round 2, a delta round over the reviewed head bc02ae8701128c21146bee16d1260fa44e6e4bae (packet `## Review scope: delta`). The delta is one commit, 4d7c80e6eb, touching only dev/programme/round11/phases.json (records data, no custom_components/ change), so nothing widens the review.

## Previous finding

The previous verdict blocked on record-contradiction: round-start items marked done whose detail said still running or not dispatched, and #3717 listed under fix-waves while the phase was dated from 12:23Z. Resolved at this head:
- Every round-start item that kept a "running since", "in review", "in repair", "open" or "not yet dispatched" detail now has the detail removed or replaced by a merge timestamp. I checked each timestamp against GitHub's merged_at: #3611 2026-11-15T14:47:57Z, #3598 2026-11-15T21:29:46Z, #3602 2026-11-16T19:03:08Z, #3529 2026-11-18T11:32:11Z. All four match (ev/merge_times.txt).
- fix-waves `started` is now 2026-11-18T11:32:09Z, which is #3717's merged_at (the previous verdict quoted 11:32:08Z; GitHub reports 11:32:09Z). The other fix-wave merges come after it: #3720 13:03:08Z, #3714 13:09:53Z, #3721 13:21:23Z. The start also falls after planning finished at 11:26:49Z. No item now sits outside its phase's dates.

## Evidence

- Head: the PR head and the body's `## Head` are both 4d7c80e6eb05a70f68ab5498ebedfb42efa404ee (ev/HEAD.txt).
- Delta: ev/delta.diff, 1 file, +14/-25.
- Lint: `plan_phases.py --check dev/programme/round11/phases.json` at the head gives rc=0 (ev/plan_phases_check.txt).
- Merge: `git merge-tree --write-tree origin/main <head>` gives rc=0 against origin/main 9fe63d00b5, so there is no conflict (ev/merge_tree.txt).
- Version: VERSION, the manifest and the RELEASE_NOTES.md heading are untouched (a three-dot diff from the merge base is empty).
- Mutation: the delta writes no production line, so there is no mutant to draw. Steps 1 to 3 are n/a for a records-only change, and the body says so.
- Figures: the body quotes none. figure_lint at the head reports 0.
- Red checks: the body answers the inherited reds `tests / nightly-status` and code-scanning alerts 57 and 58. None of these is in the owed-reds set (coverage-ratchet, fast (3.14), mutation, typing, validate-hacs), so none is owed an answer.
- Owner card rulings: the detail "48 cards, 2 still to rule" was dropped under status done. No tree artefact checks the ruling count, so I could not re-derive it. Records paperwork only, not a block.
- CI: I polled `merge_train.py classify` from 15:12Z to 15:41Z and every result was `WAIT 4d7c80e6eb05a70f68ab5498ebedfb42efa404ee pending: gate red: none` (rc=3). There was no red. The last line is in ev/classify.txt, and the `pending-ci: gate` line above hands posting to the relay.

## Findings

none
