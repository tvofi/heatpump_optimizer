Fix review: merge dc974231e4a1ead408defa2447cf7ba37186011c

bus-nonce: 9985b23f803fb7f291458bafb6527037

## Evidence

Round 1. Diff is record text only (bugclasses.json, the RCA doc, a delivery row); no production, test or instrument line, so mutation of production code and a finder's harness are not applicable. Steps 4 and 5: no claim file, VERSION, manifest or notes heading in the diff.

- CI: merge_train classify GREEN at the head, pending none, red none; no owed red.
- Merges cleanly with origin/main (merge-tree rc 0).
- Body's mutation proof reproduced: deleting the _rca entry prints UNKNOWN-RCA and 1 violation; restored, 0 violations over 181 entries; main has 180 (null control holds).
- The 17 cited commits resolve; the design lines 69 and 98 quoted in section 3 read as quoted at 20cafac7df; main at 726e5bbc32 carries no module_excess_loc key; 59 first-parent commits re-derived for the stated window.
- Not re-derived: the six job log lines and job timings (no Actions log access from this seat), the 33-commit count over every budget file, and the overlay prototype runs (out-of-tree, sha1 a0ff4e25ac). The body's Figures section is none, so these are record text, not body figures.
- Note: stale-record: section 1 says main's budget file has no module_excess_loc key; true at its stated measurement base 726e5bbc32, since changed by #3735's merge (59b17e97ae). Carry: dismissed: evidence, not a finding; the section names its measurement base

## Findings

- Mutant B survives: removing R11-RCA-BOTMERGE-ROW from N-postreview-merge-red's rca list while keeping the _rca index entry leaves fold_ledger check at 0 violations, so an orphaned _rca entry is not detected. The PR claims only the opposite direction (UNKNOWN-RCA), which reproduces. Carry: dismissed: the orphan direction is outside this PR's stated control, and the tooling freeze bars an instrument change in this record-only PR
