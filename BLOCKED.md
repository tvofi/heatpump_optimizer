Question: the body repair for #3642 is ready, but the code head cannot be proven clean on current main, so which of (a) or (b) do you want?

The repair: `## Red checks` now names `budget-raise-gate / budget-raise-gate` in full and answers `pr-contract / pr-contract` as caused by that naming gap. `policy_lint.mjs --pr-body` prints 0 errors on it, and a `prepr.sh` body-only run (PREPR_SKIP_CLOSURES=1 PREPR_SKIP_CODE=1) reports `pr-body` ok and figures 0 refused.

What blocks the handoff: at 44766207b74e16930c42c268c67380ed5c0ad951, `git merge-tree --write-tree origin/main HEAD` (main e30408f788) reports a conflict in `dev/governance/config/policy_budgets.json`. Main's #3566 lowered `corpus_tokens` from 69333 to 65926, so this branch's raise to 69625 (main's cap plus this diff's 292) no longer rests on main's cap. `prepr.sh` therefore refuses `merged tree`, and its `figure blocks` step refuses 1 block (its base is the old merge base 31117b1029).

Resolving it moves the code head (a merge of origin/main) and changes the raise amount (65926 + 292 = 66218), which the owner's approval at the old value does not cover. Under fixer.md step 6 the head is frozen after handoff and only the orchestrator moves it.
(a) The orchestrator merges origin/main into the head, re-records `corpus_tokens` at main's cap plus this diff's growth, and re-takes the approval; I then re-push the body at the new head.
(b) The raise is dropped and the cap left at main's value if the measurement allows it.
