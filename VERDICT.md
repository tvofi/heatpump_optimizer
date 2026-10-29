Fix review: merge a361e454f1058a44e7c545270dc66a1b8330f3f3

bus-nonce: dbdfc774c73dd7b6b01e8ab2a967d421

## Scope
Delta review: the prior merge verdict was at 2a5bd4dd2dace72699a1f09709ca35d37e2e505f. Head a361e454f1058a44e7c545270dc66a1b8330f3f3 is the bot's "ci: merge main" (parents 2a5bd4dd2 and main's 2033b876e, merge base e5ddba1fa). review_carry.py prints FRESH-REVIEW only because tests/golden/claimed_drift.txt is not the union of its parents. The brief's two checks were run at this head.

## Evidence
- (1) Claim file: running main's tests/env_drift.py --merge-claim-file on base, PR parent and main parent prints `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt` with rc=0, and its output is byte-identical (cmp) to the head's tests/golden/claimed_drift.txt. Output in ev/claim.txt.
- (2) No other content changed: `git merge-tree --write-tree` of the two parents, run with this checkout's claimnotes and ledgermerge drivers, gives tree 821c724dddce, which equals the head's tree. `git show --remerge-diff` on the head prints 0 lines. The PR's three-dot content (`e5ddba1...2a5bd4dd` compared with `2033b876...a361e454f1058a44e7c545270dc66a1b8330f3f3`, leaving out the three driver-merged files) is identical apart from hunk-header line offsets. tests/structure_budgets.json and tests/closures.json were resolved by the ledgermerge driver ("LEDGER-MERGE: resolved"). Output in ev/delta.txt and ev/pr-content-diff.txt.
- VERSION, the manifest and RELEASE_NOTES.md are untouched in e5ddba1...a361e454f1058a44e7c545270dc66a1b8330f3f3.
- Merge with current origin/main 2fde526340bd: `git merge-tree --write-tree` rc=0, so no conflict.
- The head was re-read just before posting: refs/pull/2917/head = a361e454f1058a44e7c545270dc66a1b8330f3f3.
- CI on this head, from the check-runs API at verdict time: the only red is tests / nightly-status (id 123766374102). It is not this PR's: the delta is a main merge only, and the diff does not reach what it reads (fix-review.md 11). Everything else that has concluded is green or skipped. Still in progress at verdict time: tests / fast (3.14), closures, coverage, mutation, codeql python, governance / instrument-self-tests, and the second run's prelude and refresh. Under fix-review.md 11 they are cited, not re-run. They have not concluded, so their green is not verified here and the merge train's required-check gate decides on them.
- Review packet rendered at this head (ev/review-packet.md): no refusals, no advisories. CARRY-AUDIT reports 8 routed and 0 unrouted. FIGURES: 14 resolved and 5 not verified, the 5 being template or inline-command forms. They are unchanged from the merge-verdicted head and were not re-derived in this delta review.
- The mutation proof, the finder's harness and the body figures were not re-taken. The PR's content is identical to the verdicted head 2a5bd4dd, so those results stand from that review.
