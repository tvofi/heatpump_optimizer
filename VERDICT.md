Fix review: merge 9461b3fecca70be1fc65b026b1822c16897bdb1f

bus-nonce: 4c6ece3e7ce349fa75260e3d3af287e3

Round 1. Record PR: head 9461b3fecca70be1fc65b026b1822c16897bdb1f measured from a detached worktree; three-dot diff changes exactly dev/programme/triage/s6-batch113.md and dev/programme/delivery/3171.md.

## Findings

- The record's heading says "session s10, batch 113" while the file name and PR title say s6 / s9; cosmetic only, the triage gate keys on the P371 entry. Carry: dismissed: cosmetic naming, no consumer reads the session label

## Evidence

- Re-derived at origin/main (8fcaf47e1, which contains dfb4ce2b5): decision 0013 line 103 holds "two pull requests ... the grader first"; line 58 holds "reopen the 1558"; fixer.md split/two-pull-requests grep hits only lines 249, 277, 314 (structure-ratchet sense and orchestrator split), as stated; ci_predict.py line 1107 prints "repair before the handoff", file is 1670 lines, in no budgets file.
- policy_lint --budgets at the head: fixer 314/315 lines 5216/5216 words, designer 60/60 878/878, design-review 53/53 778/778, role fixer ~6285 vs cap 5852+500=6352 (67 headroom): all match.
- Roster (origin/handoff/audit-r10-roster, wave-r10-groups.json): R10-FLY-CIPREDICT-RESTORING exists, stage queued, no PR; no group whose files list names fixer.md, designer.md, design-review.md or ci_predict.py is live (all such are done); R10-OPENER-REUSE has 10 carries, carry 10 is P363. #3160 merged as c7aa12165.
- Roster_edit.ruling_verdict: P371 reads ACCEPT, P372 None, flipped to DEFER reads DEFER, as the body states.
- Not re-derivable here: the seat-ledger lines 3772, 3840, 3884, 3890, 3521 and the 20 h 43 m / 12 h 45 m / 62% figures (the ledger is out of tree); P370 is not in the tree. Taken from the record, not verified.
- Standing checks: claim files, VERSION, manifest and RELEASE_NOTES untouched (diff is two files); no host path in added lines; merge-tree against origin/main exit 0; no Claude footer in commits; delivery row present in the diff. ## Head names the head; ## Red checks says none and no check concluded red at the head.
- CI: merge_train classify: GREEN 9461b3fecca70be1fc65b026b1822c16897bdb1f pending: none red: none.
- Each ACCEPT has a live destination, (d) DEFER has a testable reason and a stated condition; carry text is in the PR body, roster presence after merge is by design.
