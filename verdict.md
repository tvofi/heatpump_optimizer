Fix review: blocked 71b95e42daf4d32031ce116b01c469b81f2a23a0 ci-red: pr-contract refuses the body, whose Red checks section names budget-raise-gate but not the check's full name budget-raise-gate / budget-raise-gate

bus-nonce: 07a7e0b1900d4a8ab381fbeba79be7a7

## Block

Round 2 (a repair after the scope-rule-widened block). Measured head 71b95e42daf4d32031ce116b01c469b81f2a23a0; it is still the PR head.

`merge_train.py classify 71b95e42daf4d32031ce116b01c469b81f2a23a0 --pr 3379` prints `RED 71b95e42daf4d32031ce116b01c469b81f2a23a0 pending: none red: gate` (rc 1), not APPROVAL-OWED (rc 4). `gate` fails on two contexts: `budget-raise-gate / budget-raise-gate` (the raise is waiting for approval, as expected) and `pr-contract / pr-contract`. The pr-contract job (129475298214) gives one error: `[pr-body] check \`budget-raise-gate / budget-raise-gate\` is red and \`## Red checks\` does not name it`. The body's `## Red checks` answers the trigger in substance, but it uses the short name `budget-raise-gate`, so `policy_lint.mjs --pr-body` does not match it. This review_packet render raised the same refusal (`red-unanswered`).

The repair touches the body only. In `## Red checks`, name the context exactly as `budget-raise-gate / budget-raise-gate`, and name `pr-contract / pr-contract` with its answer. The cheaper detector is `policy_lint.mjs --pr-body ... --red 'budget-raise-gate / budget-raise-gate'`, run before the body is posted; prepr.sh already runs it. Then re-run pr-contract. Once only the budget raise's approval is red, classify should return 4 and this patch carries: no code delta is owed.

## Evidence

- Mutation proof re-run at the head: `python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py` ends `MUTANTS: 9 run, 0 not as required` (M0 PASS, M1-M8 KILLED). This matches the body.
- My own mutant: I removed `(\`custom_components/\`)` from step 12 of fix-review.md and `review_packet.py --self-test` went to `81 checks, 1 failed` (FAIL fix-review.md step 12 ...). After the restore it is `81 checks, 0 failed`, which matches the body.
- `node tools/policy/policy_lint.mjs --budgets`: the fix-review.md row is `143 143 2549 2549`, at its caps, which matches the body. The raise needs the owner's approving review at the head (code-owned policy file plus the budget raise); this verdict does not stand in for it.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`, which matches the body.
- `git merge-tree --write-tree origin/main 71b95e42daf4d32031ce116b01c469b81f2a23a0`: rc 0, tree cc98919842dc252a6bc9ddf64fe287c16684795f, `LEDGER-MERGE: resolved tests/closures.json`. No conflict.
- VERSION, the manifest version and the notes heading are untouched (three-dot diff is empty for those paths; pr-contract prints `no version edit`).
- dev/governance/roles/ has not drifted on main since merge base 2f6d699e504d6dc0bb6040d99c21c5b015a290e4.
- The body's Head section names 71b95e42daf4d32031ce116b01c469b81f2a23a0, which merges the authored code head e03c12274504ad7ede68b6f09b235029b990e404.
- figure_lint at the head: `FIGURES: 4 resolved, 0 not verified, 0 refused`. carry_audit at the head: 0 finding items.
- Class rule: the body names one seam, step 12 wording, stated in three places (fix-review.md, review_packet.py, cloud_dispatch.py). The harness pins all three and bus.sh's hand-off of --reviewed-head (M5, M6). I found no unenumerated site.
- No production code (`custom_components/`) changes, so there is no golden or claim drift to compare.
