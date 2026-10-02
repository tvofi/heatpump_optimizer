Fix review: merge c5dad85002d0482d5f78d834c39948be71843232

bus-nonce: 7d86ec73d40a2b5a9655e835989e93fd

PR #1845, roster group R9-EG-B5a, issue #1743. Round 2. I re-read the live head before posting,
and it is still c5dad850. origin/main is aab94eea.

Round 1 blocked edb67c66 as root-cause-unanswered, because `mutation` was red and `## Red checks`
said "none". The body now names `mutation` in `## Red checks` and calls it the ci-autofix.md
unpinned-sites case. It cites the pin step (`PIN KILLED: 2 pinned, 0 left unpinned`) and the bot
commit dfd383ae, records "Cheaper detector: none worth building", and notes that `pr-contract` was
red only for the missing name. `## Head` names c5dad850, then dfd383ae, edb67c66 and dafa803c.
The block is cleared.

## Delta since round 1 (edb67c66 -> c5dad850)
- edb67c66 -> dfd383ae: github-actions[bot] `ci: pin killed mutants`. It adds two
  tests/mutation_ledger/killed_by rows for `_solve_objectives` (CLAMP_DROP, killed by
  env_drift.py; RETURN_DEL, killed by doc_claims.py) and nothing else.
- dfd383ae -> c5dad850: a merge of origin/main aab94eea (#1849).
  - RESULT resolution-delta empty: `git merge-tree --write-tree dfd383ae aab94eea` gives
    3dd37b06, which equals the head's tree.
  - RESULT 8 of 8 files in `git diff --name-only dfd383ae c5dad850` have the head's blob equal to
    aab94eea's: budget_raise_gate.py, required-contexts.json, budget-raise-gate.yml, HANDOVER.md,
    decision 0013, delivery/1843.md, delivery/1849.md, tests/entities.py.
  - RESULT custom_components is identical between edb67c66 and c5dad850.
- I re-measured at c5dad850 instead of relying on a carry.
  - tests/structure.py: rc=0, duplication_copies=59, max_method_loc=385, methods_over_150=18,
    methods_over_200=10.
  - Closure AST equivalence against base 2b6c5b87, the same instruments as round 1: the DHW path's
    three closures are equal. The space-only `_space_traj` is equal, and its objective and batch
    twin are equal once the builder is specialised to dhw_plan_power=None.
  - Claim files, VERSION, the manifest and RELEASE_NOTES: `git diff MB...HEAD` is empty.
  - `git merge-tree --write-tree origin/main HEAD`: rc=0.

## This head's CI (35 check-runs: 24 success, 9 skipped, 2 cancelled, 0 failure)
- Required numeric lanes passed: fast (3.14), env-matrix, closures, mutation, coverage,
  coverage-ratchet, typing, instrument-self-tests. pr-contract, budget-raise-gate,
  policy-docs, briefs, delivery-status and nightly-status passed too.
- The two cancels are superseded duplicates: pr-contract 110873174596 and budget-raise-gate
  110873175543. Each has a successful re-run at this head (110873423078 and 110873188721).
- `mutation` log, read rather than taken from the tick: `MUTATION TABLE PASSED`.
  - It reports 3909 unpinned sites against 3911 at the ratchet base aab94eea, and says the ledger
    agrees with the deterministic inventory.
  - Lazy drivers are `LAZY AND NEVER RUN` because every mutant run of them was green, so the pass
    is not an INCONCLUSIVE baseline. mutation-autofix and closures-autofix were skipped, so no
    further repair was owed. No red check at this head needs an answer.

## Carried from round 1, still true at this head
- The refactor is AST-equivalent to both old paths.
- Each perturbation moves the instrument aimed at it: M1, M2, operand swap, passing a plan on the
  space path, and deleting comfort_band. The unperturbed head is the null control.
- CI's pin step showed a numeric perturbation of the builder (CLAMP_DROP on comfort_band) killed
  by tests/env_drift.py.
- Not re-run on this Mac, which has no numpy and no container: features.py M1/M2 and env_drift's
  count of 56. The numeric checks rest on this head's green CI lanes cited above.
- "Part of #1743" is correct, and #1743 stays owed. This group has `fixes: []`; R9-EG-B5
  (`fixes: [1743]`) does the planner extraction the issue asks for.

The PR touches custom_components/, which is code-owned. This comment approves nothing, and the
merge still needs tvofi's approving review at this head.

Evidence: evidence/HEAD.txt names the head. delta.txt, structure_head.txt, closure_ast_eq*.txt,
checkruns-final.tsv and mutation_excerpt.txt are there too; round1/ is the round-1 evidence.
