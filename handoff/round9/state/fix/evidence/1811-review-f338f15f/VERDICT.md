Fix review: merge f338f15f54d118bd6af9246f0b61fac8a8eac31e
Fix review: merge d3cdbf7a5034ddea816c15434e802e3a55cbca8d

R9-F10.8 round 2 (v3 on main dc6c97e4), PR #1811. Reviewer: hpo-approver seat (opus).

- Round-1 block resolved: prepr.sh 6a now has `inh` (edits a note, keeps main's list -> 1:--drop-inherited) and `unt` (untouched -> 0:). Self-test 129/129 at f338f15f; at dbe33db1 (tests on main) `unt` fails as expected.
- Conflict resolution on F10.3's shape: judge_drift is unchanged; main() calls `claims = excusing_claims(repo, ref, claims)` before judge_drift, so drift excusal and the staleness rule read only authored lines. card_*.mjs, claim-files.md/.mdc and prepr.sh patches are line-identical to round 1+2; entities.py differs only in calling the new API and in a source pin on main()'s wiring.
- Red first at dbe33db1: entities 7 F10.8 checks fail, card 4, prepr 6a 1. At f338f15f: entities 2020/2020, card all pass, prepr 129/129.
- #213 closed: mutant `excusing_claims` returns raw claims -> killed ("a carried claim line does not excuse a moved fixture"); mutant dropping the main() call -> killed (source pin); mutant judgeCardClaims excusing = tree claims -> 3 card checks fail.
- Main's push shape (probe_main.py, new API): claims-only HEAD^1 is None after --no-ff claiming, non-claiming and squash merges; merged lines excuse, carried lines do not (DRIFT).
- PR head d3cdbf7a: 137e79f9's tree == f338f15f's; d3cdbf7a tree == merge-tree(f338f15f, c4f1c263) (340312c8); diff vs c4f1c263 is line-identical to v3's diff vs dc6c97e4. entities.py (auto-merged with #1813) passes 2021/2021 there; nightly_status.py passes.
- CI at d3cdbf7a when read (15:14Z): instrument-self-tests, pr-contract, typing, mutation, closures, browser, policy-docs, env-matrix, hassfest, budget-raise-gate green; fast (3.14), coverage and CodeQL python still running. Merge only once those are green.
- Not run here: typing_ruler --mypy and real-HA ha_contract (CI typing is green).
