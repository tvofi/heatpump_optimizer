Fix review: merge a36d0a6e56cc5f5af6754a9dec2cd10e41be919d

bus-nonce: 6769501e6df369db55a12fb9959d412d

Round 1. Measured head a36d0a6e56cc5f5af6754a9dec2cd10e41be919d (PR head at read).

## Findings

- Residual: the countermeasure (driver change, entities test, claim_merge_mutants case, claim-files.md sentence) is not landed and waits on the owner's approval; the RCA records this. Carry: dismissed: proposal for the owner, no stage is waiting on it.

## Evidence

- Diff is 5 files (RCA doc, bugclasses.json entry + class, finding.schema.json enum, audit-find.js generated block, delivery row); no production code, VERSION, manifest, notes heading, golden or claim file, budget, closures touched. Carry: dismissed: evidence, not a finding.
- merge-tree origin/main vs head: rc 0, clean. Carry: dismissed: evidence, not a finding.
- merge_train classify at head: GREEN (rc 0), pending none, red none. Carry: dismissed: evidence, not a finding.
- fold_ledger.py check: 0 violations. agreement.mjs: divergent=0 at head and at origin/main (the refused=6 lines are the missing --py-json file, identical at both). Carry: dismissed: evidence, not a finding.
- Reproduced the RCA's null control myself: branch appending one claim line at the stamp's parent 2a3c05644^ merged into 2a3c05644 prints MERGE-CLAIM: refused with "CONFLICTING CLAIMS: both sides changed claims under different"; same append on a branch cut at v7.1.5 prints MERGE-CLAIM: resolved. Base at 2a3c05644^ holds 6 claim lines. Carry: dismissed: evidence, not a finding.
- Cited code anchors exist (env_drift.py both_changed / stamps guard lines ~1805-1806; stamp.py rewrite_claims "delete every bare claim"). Carry: dismissed: evidence, not a finding.
- Not re-derived: the per-stamp refused-branch counts, the ~1 h per branch cost, and the section 5 patched-driver demonstration (prototype not in tree); the RCA marks the durations as estimates. Carry: dismissed: evidence, not a finding.
- Mutation proof n/a (no production line); no red gate check on the head, so item 11 owes nothing; the body's prepr entities note is environmental and not a gate check. Carry: dismissed: evidence, not a finding.
