Fix review: merge 1f8ca9d96731a2720148ce7993ba1e23545f0803

bus-nonce: 020f259e6ad8e38a8e3ad9bdf92f35a8

## Round

First round of fix review for #3192 (R10-MACHINERY-RATCHETS part 1b, grader registration first). Measured head 1f8ca9d96731a2720148ce7993ba1e23545f0803; re-read before return, still the PR head (refs/pull/3192/head). Roles diff three-dot against origin/main is empty, so the contract read is current.

## Evidence

- RESULT mutation: four targeted mutants of registryRun's pending branch in tools/policy/field_coverage.mjs, each killed by --self-test: (M1) pending predicate replaced by false fails "a pending DECLARED key the set does not yield is printed, not DEAD" and turns --only registry red with DEAD machinery_ratchet.py, rc=1, as the body quotes; (M2) .trim() dropped fails the empty-reason pin; (M3) the set.includes continue disabled fails "a pending DECLARED key the set yields is graded like any other"; (M4) the DEAD else-branch disabled fails two pins. File restored, tree clean. ev/mutants.txt.
- RESULT null control: origin/main's field_coverage.mjs on part 2's tree prints REFUSED registry machinery_ratchet.py unregistered, refused=1; this head's copy on that tree grades the entry none, dead=0 refused=0, FIELD COVERAGE ok; this head on its own tree prints pending, dead=0 refused=0. Re-derived at handoff-wip/r10-machinery-ratchets-p2 ee19e1f5, not the body's 3ffd1c43: that ref has moved since. The result is the same. ev/nullcontrol_merge.txt.
- RESULT figures: self-test ok with three new pins; registry ok dead=0 refused=0; STRUCTURE RATCHET PASSED; RULES-SYNC ok. I did not re-run closure select or prepr myself. CI's closure-scope, closures and pr-contract are green at this head, and the packet's figure_lint resolved all 5 figures.
- Merge: git merge-tree --write-tree origin/main(8e90d814) head exits 0, tree ed3b2997. No conflict and no claim file touched.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched (the three-dot diff touches only field_coverage.mjs and the delivery row).
- Finder's harness: none. This is an unblocking grader-bootstrap part (P371 split), not an audited finding, and its harness is the self-test pins plus the part-2 null control above.
- Class: one seam. The other pending-shaped tolerance, jsonRun's IGNORE PENDING, already exists, and CENSUS_EXEMPT has no bootstrap need in this group.
- CI: merge_train classify returned GREEN 1f8ca9d96731a2720148ce7993ba1e23545f0803 pending: none red: none, rc=0 (ev/classify.txt). Of the head's checks, only tests / nightly-status is red, and it is not this PR's: the diff reaches no nightly input (defect-root-cause.md). pr-contract and gate are green. The mutation lane is green, but a diff writing only a .mjs grader draws no production mutant, so my targeted mutants above are the proof.
- Body "Red checks: none" holds for the gate checks.

## Findings

- Follow-up: part 2 owes dropping the `pending` key from DECLARED['pinned tools/audit/machinery_ratchet.py'], which makes the entry strict again. That obligation sits in this body and in the printed reason, but not in the group's roster brief or resume (whose next_step is still the stale "re-fire a fixer from 790328a8b"). If part 2 rebases without dropping it, the entry silently keeps a DEAD-tolerance. Precondition for part 2's handoff: field_coverage.mjs on main carries no `pending` on that key. Carry: dismissed: no live destination, the roster marks R10-MACHINERY-RATCHETS done while parts 1b and 2 are open; the orchestrator reopens the group and lands this as part 2's precondition (see Friction)
- Residual (instrument, metric-gamed shape not used by this diff): a DECLARED `pending` with any non-blank reason silences DEAD indefinitely, with no expiry and no link to a live group. A planted key 'check gone-forever' { pending: 'someday' } passes as FIELD COVERAGE ok, dead=0 (ev/plant_pending.txt). The existing IGNORE PENDING has the same shape. This diff's own use is sound and time-boxed by part 2, so this is an instrument finding, not a block. One countermeasure is for the machinery ratchet, or field_coverage itself, to count surviving pending entries on main and cap them at zero once their follow-up has merged. Carry: dismissed: no live destination, R10-MACHINERY-RATCHETS is marked done on the roster; the orchestrator routes it with the group's reopening (see Friction)

## Friction

- carry_audit refuses R10-MACHINERY-RATCHETS as a destination because the roster (handoff/audit-r10-roster 13b2fbdd) has its resume.stage as done, at p1's #3165 commit 8fcaf47e. #3192 (part 1b) is open under it, and part 2 waits at handoff-wip/r10-machinery-ratchets-p2 ee19e1f5. Its next_step is stale too. R10-FLY-CLOSURE-MAJOR, which lists it in `after`, is also done. Both findings above are therefore routed `dismissed:` and handed to the orchestrator here. Reopening the group (resume stage, pr 3192) gives them a live destination.
