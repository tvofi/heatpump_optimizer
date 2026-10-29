Fix review: blocked 3efeea2176fa570ae8c52a13996c483f02cb1d52 carry-missing: the three restoring jobs outside governance.yml (briefs, pr-contract, budget-raise-gate) are left open in the record and body but carried to no stage

bus-nonce: abd1bb9ec79997216a3a132c9597b3dd

Round 6 (past the third: fixer.md owes a re-cut, and this one is a minimal re-cut by claim narrowing). Reviewed head: 3efeea2176fa570ae8c52a13996c483f02cb1d52. review_carry.py 2c62c682d -> head prints FRESH-REVIEW (d379cfa43 carries the record change), so the range was re-read in full.

## Block

The r5 finding (class-open: budget-raise-gate) is closed as a claim matter: the record's summary and section 7 now scope the arm to governance.yml's restoring jobs, which is what restore_jobs reads, and the body says the same. The enumeration rule the body names returns six jobs at the head and at origin/main; the three outside governance.yml (budget-raise-gate.yml:66, pr-contract.yml:93, tests.yml:603) are each named in section 7 as not covered. The body's claim matches the code.

But narrowing does not remove those jobs from the class the record measures (a grader CI restores from the base, editing which the local predictor cannot see); it leaves them open seams. finding-propagation.md: an open seam the enumeration rule returns "goes to a new issue filed by the same pull request, or a carry file", and "the record [is] not propagation". The body says in terms that they "are not routed to a later stage from this body", that no issue, roster entry or carry file was written, and that a handoff note asks the orchestrator for a group. fixer.md step 8 admits three dispositions (closed in this diff, already guarded, or a distinct finding named by id); "left open, group to be created" names no id. carry_audit at the head counts one finding item (R10-RECORD-API-O1) and none for these three. Merged this way, the seat that next edits budget_raise_gate.py, pr-contract's checker or brief_lint.mjs has nowhere to read that its edit is graded by the base copy unpredicted.

Repair (no code): the orchestrator files the issue or creates the group (the round-5 split); the body gains one `Carry:` line naming it for the three jobs, with the enumeration rule as the control and the precondition that pr-contract and budget-raise-gate instances are unmeasured (section 4's census read briefs only). A carry-only body edit leaves every code figure below standing.

## Findings

- none beyond the block: its single item is owed in this pull request, not handed on.

## Evidence

- Mutation proof re-run at this head (`dev/audit/rca/prepr-head-graders/mutants.py .`): M1 bad 5, M2 bad 1, M3 bad 1, M4 bad 1, M5 bad 3, matching the body (ev/mutants.txt). Null control: `ci_predict.py --self-test` prints `ci_predict self-test: 0 failed`, rc 0 (ev/selftest.txt).
- Enumeration: six hits at head and at origin/main 3042dcd4f, same file:line at both (ev/enumeration.txt). The body's "shifted governance.yml lines" was against b87019b86; at the current main the lines do not shift. `grep -c budget-raise-gate` on the record: 0 at 2c62c682d, 2 at head, as the body says.
- `git merge-tree --write-tree origin/main 3efeea2176fa570ae8c52a13996c483f02cb1d52` exits 0, tree f21dc054e (ev/merge-tree.txt). VERSION, manifest, RELEASE_NOTES.md and both claim files untouched in the three-dot diff.
- CI at this head, read from the check-runs API: every completed run success or skipped except `tests / nightly-status` failure, which grades main's Nightly; this diff touches nothing it reads, so it is not this PR's. pr-contract run 123481999292 started 13:38:34Z, after the last workflow concluded, and is green.
- Not re-taken: the plant timings, jobtime.py and keycount.py cost census (record section 5); this round's diff changes no code they measure. The 57 s / 85 s cost figures were not re-derived by this seat.
- Head re-read before publishing: PR head is still 3efeea2176fa570ae8c52a13996c483f02cb1d52.
