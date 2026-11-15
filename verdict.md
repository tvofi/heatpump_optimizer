Fix review: merge 6606a53561c0c326396f554169bdf29c04b1099e

bus-nonce: b956b57116347a11933a4d3f9c947d8d
pending-ci: gate, tests / coverage

## Evidence
- Round 1, full scope. Diff: .github/workflows/governance.yml policy-docs timeout-minutes 5 to 10 plus a comment, and the delivery row dev/programme/delivery/3615.md. No custom_components/ change, so no mutation target, golden, claim, budget or closure movement (ev/diffstat.txt).
- RESULT merge-tree: git merge-tree --write-tree origin/main head rc=0, clean (ev/merge-tree.txt).
- RESULT version: VERSION, manifest and RELEASE_NOTES untouched (ev/version-touch.txt empty).
- RESULT rca: dev/audit/rca/R10-RCA-FAMILY-POLICY-DOCS-TIMEOUT.md exists on main and at head; it names state (d), cost test, and the 5 to 10 countermeasure the diff implements. The 170 s wall figure there is the RCA's own Mac measurement; I did not re-derive it.
- RESULT carry_audit: 0 finding items, 0 unrouted (review packet).
- CI at this head: classify prints WAIT pending (gate red: none) after about 35 minutes of polling; tests / coverage was still in_progress. No required context is red. Context names owed: gate, tests / coverage.
- A mutation proof is not applicable: the change is a CI timeout value, not production code. The only behaviour moved is a longer bound on a hung policy-docs run.
