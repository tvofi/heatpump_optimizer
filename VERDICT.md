Fix review: merge 5a529f15155b00eb1885a3a5ac39b2ad2ffb218c

bus-nonce: feff3bb57c28a6216fb320591c0e7902

## Scope

Round 2 of the fix review of #2758 (triage s6 batch 15, P84, record lane), a body-only re-check. Measured head: `5a529f15155b00eb1885a3a5ac39b2ad2ffb218c`, still the PR head when this verdict was written. Role contract: `git diff 4944b20d5...origin/main -- dev/governance/roles/` is empty, so it is current.

## Evidence

- RESULT head: the body's `## Head` names `5a529f15155b00eb1885a3a5ac39b2ad2ffb218c`, the live head, and says it merges origin/main `4944b20d5` into the previous head `7f91e684`, which it describes as the ruling commits (the latest `feb44bd8`) plus one commit holding only the delivery row `dev/programme/delivery/2758.md`. That matches `git log`: cf58e6a84 and feb44bd88 are the rulings, 7f91e6842 is the row, and 5a529f151 is the main merge. The round-1 block, `body-head-stale`, is repaired.
- RESULT body contract: `policy_lint.mjs --pr-body` at this head prints 0 errors, and `prepr.sh --body-check` prints `pr-body ok` (ev/body-checks.txt).
- RESULT non-body diff: the branch's contribution over its main merge (`git diff 4944b20d5 5a529f15155b00eb1885a3a5ac39b2ad2ffb218c`) is byte-identical to `git diff a260e5630...7f91e684`: 2 files, 21 insertions (`dev/programme/triage/s6-batch15.md` and the delivery row). Nothing beyond the main merge and the row changed. `VERSION`, the manifest and the notes are not touched (ev/contrib-diff.txt).
- RESULT merge: `git merge-tree --write-tree origin/main(12b222007) 5a529f15155b00eb1885a3a5ac39b2ad2ffb218c` exits 0, with no conflict and no MERGE-CLAIM line (ev/merge-tree.txt).
- RESULT figures, re-counted at this head: 1 ACCEPT verdict line. `ruling_verdict` returns ACCEPT for P84 and None for P99, which is the null control. `merge_train.py` is 4174 lines at a260e5630. `policy_gate`, `MANDATE_CITE`, `MANDATE_COVERS_POLICY` and `mandate_state` exist where the ruling places them. `--corpus-filter` classes the triage and delivery probe paths as non-policy.
- RESULT cause, cost and risk: the ruling's cause is 3 ad-hoc-shell defects, taken from proposals.md V19. The body says these were not re-counted from logs, and I could not re-derive them either, because `par<N>.log` is out of tree. The cost of about 25-40 lines in merge_train.py and the medium risk bounded by `policy_gate` staying the sole judge are consistent with the tree. R10-TRAIN-UPGRADE is a live group in `dev/programme/rosters/wave-r10-groups.json` at origin/main, so the destination resolves.
- RESULT carry lint: the carry text, appended to a scratch not-started R10-TRAIN-UPGRADE brief from origin/main's roster, gives brief_lint 0 errors. The same text with `merge_train.py` misspelt gives 1 error (`path: tools/audit/seat/merge_trian.py: not in the tree`), so the linter reads it (ev/brief_lint_carry.txt). `carry_audit.py --roster-ref origin/main check` on the body finds 0 finding items, 0 unrouted.
- RESULT CI: the only red at `7f91e684` is `pr-contract` (run 40127337036). The body names it, gives `prepr.sh --body-check` as the cheaper detector, and the re-run (40131058585) concluded success. At `5a529f15155b00eb1885a3a5ac39b2ad2ffb218c`, pushed at 02:18Z, the workflows were still queued when read at 02:2xZ (ev/check-runs.txt). That CI is the merge train's to wait on, and no red at this head is unanswered.
- RESULT mutation: n/a, because the diff writes no production or check code.

## Findings

- The body's `## Head` still keeps two round-2 sentences that the orchestrator's automatic main merge has since outdated: "Not merged up to main ... clean against origin/main `5c0ee1093`", and in the intro "handoff/triage-s6-batch15 is `7f91e684` itself". Both describe the previous head correctly. The section's first line, which names the real head and the merge, settles the head for rule 7, and the body lint accepts it. Carry: dismissed: stale wording created by the orchestrator's merge script, not by the fixer, and it changes no measurement.
- `tools/policy/brief_lint.mjs` lints only a roster group's `brief` field, never its `carry` list (lintFile, around lines 984-988). A carry added with `roster_edit.py append-carry` is therefore never citation-checked unless someone copies it into a brief, as I did here. Carry: dismissed: pre-existing instrument scope outside this ruling record; the carry text here was checked by hand above, and widening the linter is a separate proposal for the orchestrator to weigh.
