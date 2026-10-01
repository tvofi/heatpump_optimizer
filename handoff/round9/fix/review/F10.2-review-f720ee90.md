Fix review: merge f720ee90dfc5a0ebf0d8486a92bc0db0bbffb165

Merge-delta check, PR #1803. Head f720ee90 is the live PR head as posted. It is a merge commit with parents 1bb04b29 (merge-verdicted in round 2) and cc00ed85 (main, #1802 F6.3, which is in origin/main). I judged only the delta from 1bb04b29 to f720ee90.

- No hand resolution: the tree git merge-tree 1bb04b29 cc00ed85 writes on its own is identical to f720ee90's tree (an empty diff). So the bugclasses.json resolution is the automatic one.
- The delta is exactly main's change: six files (carry-1757.json, CODEOWNERS, heatpump-optimizer-card.js, tests/card.mjs, tests/card_browser.mjs, bugclasses.json). For each of the five non-bugclasses files, the patch-id of 1bb04b29..f720ee90 equals the patch-id of 6793659c..cc00ed85 (main's own change since the merge base).
- bugclasses.json at f720ee90 parses as JSON. It keeps all of F10.2's entries (six "F10.2" mentions, as at 1bb04b29: N-solve-recompute barriered, I1.barrier_parts N-cpu-gate-blind) and adds main's P9 entry (detector, barrier, status barriered). The two sides touch different classes.
- No interaction: main touched none of F10.2's files (tests/stress.py, tests/replay.py, tests/stress_budgets.json, tests/closures.json, tests/README.md), and F10.2 touched none of the card files.

CI at f720ee90 when posted: mutation, budget-raise-gate, pr-contract, policy-docs, briefs, closure-scope, nightly-status, delivery-status, env-matrix, instrument-self-tests, hassfest and validate-hacs are green. fast (3.14), browser, typing, coverage and closures were still running. The merge seat merges only on CI green at this head. tvofi's approving review at this head is still owed.
