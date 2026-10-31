Fix review: merge 62634ab02d7edd335f4da68102ad560b8138b635

bus-nonce: 22a539774297ff13434b7c8ec576748c

Round 1. Measured head 62634ab02d7edd335f4da68102ad560b8138b635; merge base a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0.

## Findings

None. This PR leaves no defect, deferral or follow-up unsettled.

## Evidence

- RESULT harness base: the real writer's pr_body fed to policy_lint.mjs --pr-body with the three full names (governance / record, tests / nightly-status, governance / delivery-status) gives rc=1, "3 error(s)". The finder's failure reproduces. See ev/harness.txt.
- RESULT harness head: the same call gives rc=0, "0 error(s)".
- RESULT single definition: RED_CHECKS is defined once (record_row.py:122-126). The body text goes through _red_names_line() and f-strings over RED_CHECKS, and the self-test passes list(RED_CHECKS.values()). grep finds no second hand-typed copy of the full names. The section names each reporter by full name with the short name beside it.
- RESULT mutation: reverting the body to short names only at the head fails exactly one self-test arm: "body check passes the generated body over the reporter reds (rc 1: 3 error(s))". Restored afterwards.
- RESULT self-test: at the head, record_row.py --self-test passes all checks.
- RESULT null control: the stripped-names arm (the nightly lane, the delivery reporter) still refuses, now under --red "tests / nightly-status". The self-test passes, so the arm holds.
- RESULT merge: git merge-tree --write-tree origin/main <head> exits 0 with no conflict. The three-dot diff touches only dev/programme/delivery/3056.md and tools/audit/seat/record_row.py.
- RESULT scope: merge_train.py and merge_train.NOT_GATING are untouched. No golden, claim file, VERSION or manifest is in the diff. The claim files are byte-identical to main.
- RESULT structure: tests/structure.py prints STRUCTURE RATCHET PASSED.
- RESULT gate scope: closure select prints "MODE: SCOPED -- 1 script(s) run, 32 scoped out".
- RESULT CI: merge_train.py classify 62634ab02d7edd335f4da68102ad560b8138b635 exits 0, GREEN, with nothing pending and nothing red. The packet's gate digest shows no red check run at the head, so the body's ## Red checks owes no concluded red. The packet reports no refusals and no advisories, and carry_audit finds 0 items.
- RESULT instrument doc: instruments/record_row.py.md is unchanged and its text says nothing about red-check names, so nothing in it is stale. I did not re-derive "updated" as an edit to that file.
- RESULT architecture: the change is a constant plus a helper, adds no new file, and the delivery row is present.
- Not re-derived: the mutation and coverage lanes. I cite CI's green runs for them and did not re-run them.
