Fix review: merge 5c62333144fbd04f26d0f0f5b2ecac45d9088267

bus-nonce: 1874e532f90d9dd07d6684fe317a3dce

Round 1. Head measured and re-read: 5c62333144fbd04f26d0f0f5b2ecac45d9088267 (a docs-only triage record; no production code, so no mutation proof of a production line applies).

## Evidence
- CI: merge_train.py classify at this head prints GREEN, pending none, red none (ev/classify.txt). No required check went red, so no root-cause answer is owed; the body's "Red checks: none" holds.
- Merge: git merge-tree --write-tree origin/main head exits 0, clean tree (ev/merge-tree.txt).
- Diff is two files: dev/programme/triage/s6-batch138.md and dev/programme/delivery/3392.md. The body says "one file" and cites 226818f593 for it; the second file is the delivery row, added after. review_carry.py 226818f593 -> head prints CARRY (ev/review_carry.txt), so the earlier patch is the one reviewed. VERSION, manifest and RELEASE_NOTES are untouched; no governance, claim or budget file is in the diff.
- Citations re-read at origin/main 3fdaa9da9a (an ancestor of origin/main): body_push.sh 181-182 (--topic passed), bus.sh 232-233 (--pr "#N", no topic), carry_audit.py own_group 586-594 and own_carry_status call at 626, plan_page.py 255/260/264/340/342/524, ledger.py landed at 464, codeql.yml timeout-minutes 45 at line 116, entities.py _analyze_cap at 21857 all match the quoted text. P459's mechanism (own_group returns None for a "#N"-only source) is confirmed by reading the code.
- Destinations: R10-DISPATCH-AT-HANDOFF, R10-TICK-LEVELS and R10-OUTSIDE-INTAKE are carries-open at the roster tip; R10-CI-PRIORITY-PAUSE is stage refused, as P460 says. The roster tip's R10-HOTFIX-CODEQL-HEADROOM already holds the P463 note and set-files widening to tests/entities.py.
- carry_audit at the head: 0 finding items (packet). Own-group Carry lines in the file name each ruling's destination.
- Not re-derived: the figures drawn from the orchestrator's local logs (cloud-relay.daemon.log, s11/ci_priority.log, queue lines, plan.html, the 20-run job listing, the 480-job enumerator, 11-in-1 and 4-of-13 recurrence counts) are outside the tree and this seat's reach. They are the proposal's own record, unverified here; the rulings do not hinge on a figure that moves them across a bar except P460's 2.7 % (cited to P428, not re-read).
- No finder harness is named; the packet shows none and none is owed for a triage ruling.

## Findings
- Residual: the roster tip's R10-HOTFIX-CODEQL-HEADROOM reads resume.stage done (pr 3367) while P463 carries a fresh part-2 fixer to it; the finding-propagation rule says a done group is not a destination. The note names topic r10-hotfix-codeql-headroom-p2, so the orchestrator appears to be handling it, but this seat could not confirm the group is dispatchable. Carry: dismissed: the group is stage done at the roster tip by the orchestrator's own P463 op, which names part-2 topic r10-hotfix-codeql-headroom-p2 as the dispatch; a done group is no destination, and the orchestrator owns that dispatch
- Residual: the PR body says the diff is one file against 3fdaa9da9a and cites 226818f593; the head also holds the delivery row. Cosmetic. Carry: dismissed: cosmetic, the delivery row is the per-PR record and the patch carries
