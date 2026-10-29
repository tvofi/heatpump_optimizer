Fix review: merge c861c0e7b04f86e0626bbc0f8d8ecc7b26bf3b33

bus-nonce: 09fb33e45a6f24f62747f38b51ff15d1

## Scope

Delta review only: 2fda9547ec7f..c861c0e7b04f, the merge of origin/main ce5940c0d1d8 into fix/r10-cop-gate. The earlier merge verdict covers 2fda9547ec7f.

## Evidence

- RESULT: c861c0e7 has two parents, 2fda9547ec7f (the reviewed head) and ce5940c0d1d8 (main). Their merge base is 279578074a17. `git merge-tree --write-tree 2fda9547 ce5940c0` gives tree 238f49c4a811, which is the head's own tree. So the merge is git's automatic result and nothing was resolved by hand (ev/delta.txt).
- RESULT: tests/golden/claimed_drift.txt at c861c0e7 is blob 582f22ba, byte-identical to the reviewed head 2fda9547. Main's copy at ce5940c0 is ccd1d1a0, byte-identical to the merge base: main did not touch the file in that range. The correct three-way result is therefore the branch's file. card_claimed_drift.txt (1f470c06) and VERSION (7.0.5) are the same at all four commits.
- RESULT: claim rules at head (ev/claims_check.txt). `# claims-for: 7.0.5` equals VERSION 7.0.5. Five fixtures are claimed (coord_*, R10-COP-GATE) and none of them is also may-drift. Main kept its lines, because main added none since the base. The merge reinstated nothing the branch had deleted.
- RESULT: why the train refused. The carry check in tools/pr/app_approve.sh (line 290 on main) builds `want` as the sorted union of both parents' lines. The branch had already deleted 26 lines in reviewed commits before 2fda9547: main's R10-HOUSE-GRADE and R10-BUFFER-STORE claims and the suspension notes. In 535015a87 it restored the six may-drift entries verbatim, as claim-files.md requires ("a line excuses only the diff that wrote it"). All 26 lines exist at the base, and a naive union puts them back (ev/union_check_diff.txt). claim-files.md calls exactly that a defect ("merge=union would reinstate a claim the branch deleted"). The refusal is a false positive of the carry fast-path, not a defect of this merge.
- RESULT: the other 14 files in the delta are main's: delivery rows 2956/2957/2958, the RCA documents, bugclasses.json, proposal-triage.md, triage s6-batch60.md and tests/entities.py. The only file both sides changed since the base is tests/entities.py, and git merged it automatically (same tree as above). No production, test-logic or golden-value file changes in the delta, so the reviewed behaviour is unchanged.
- RESULT: the head merges with current origin/main e5ddba1fad5e. merge-tree rc=0, and the only driver resolution is LEDGER-MERGE on tests/closures.json (inert_reads set union). Main has not touched the claim files since ce5940c0.
- CI on c861c0e7, from the check-runs API: `gate` (the one required check) passed, as did pr-contract, arch-score, budget-raise-gate, tests/fast (3.14), closures, coverage, coverage-ratchet, replay, browser, typing, lane-proofs, CodeQL and the governance units. The autofix jobs were skipped.
- `tests / nightly-status` is failure. It is not a required check and does not block. It grades main's last scheduled Nightly run, and the delta touches none of its inputs, so per defect-root-cause.md it is the orchestrator's on main and the body owes it no answer.
- The review packet rendered with rc=0 and no refusal signal (ev/packet.md). Its "Gate digest: red" is the nightly-status row above.
- No mutation was run: the delta adds no code to mutate. The figures in the PR body were re-checked by the earlier verdict at 2fda9547 and this merge does not move them.

## Findings

- tools/pr/app_approve.sh's merge carry check compares a claim file against the plain line union of both parents. Every branch that drops main's inert claims, as claim-files.md prescribes, is refused as "resolves ... to something other than the union of its parents", even when the merge is git's own automatic three-way result. Here the cost was this extra delta review. A sounder check would compare against the claimnotes driver's three-way result, or accept the automatic merge when one side equals the base. Carry: dismissed: train-side tooling outside PR #2917's diff; reported to the orchestrator in this verdict, which owns that check
