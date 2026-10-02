Fix review: merge b69961d780511b29af6e8d454c4ff829ec340783

PR #1842 (R9-F10.4 precursor), round 1. I measured code head b69961d7, which is still the PR head at posting. The PR is a draft with no delivery row yet; a row-only commit on top carries this verdict. Its base is main 492d8401, and `git merge-tree --write-tree origin/main b69961d7` exits 0. The diff is `.claude/workflows/brief_lint.mjs` only: +6/−3.

## Matrix (node brief_lint.mjs, outputs in this directory)

| linter | tree | `coordinator_loc` key | rc | 931dffe line |
|---|---|---|---|---|
| this PR | main 492d8401 | present | 0 | FIXTURE ok: 15 error(s) … (10 required) |
| main (null control) | main 492d8401 | present | 0 | FIXTURE ok: 15 error(s) … (10 required) |
| this PR | main, only the key removed | absent | 0 | FIXTURE ok: 14 … (9 required) |
| this PR | #1838 e37cefc6 | retired | 0 | FIXTURE ok: 14 … (9 required) |
| main (the red it fixes) | #1838 e37cefc6 | retired | 1 | FIXTURE VACUOUS … [W1-G8] metric: coordinator_loc |

## Mutants

- Literal-metric rule off on main's tree (`const metric = null && resolveMetricName(m[1])`): rc=1, with all three W1-G8 pins reported missing (coordinator_loc, methods 255, attrs 176). The filter cannot hide a broken rule while the key exists. This reproduces the body's mutation proof.
- The `held` filter dropped (`required.filter` in place of `held.filter`) on #1838's tree: rc=1, FIXTURE VACUOUS. This is the failure the change removes.
- Survivor, not blocking: a mutant that always drops the conditional pin stays green on main. Two pins still hold the literal-metric rule (`methods 255`, `attrs 176`), as the first mutant shows, so the pin it drops is redundant there.

## Other checks

- policy_lint.mjs rc=0 (0 errors across 40 policy files); rules_sync --check ok.
- Red checks: none on the body; I read no CI run.

## For the orchestrator, not a defect here

- brief_lint.mjs is policy, so merging needs tvofi's approving review.
- **Merging this makes #1838 conflict.** `git merge-tree b69961d7 e37cefc6` reports `CONFLICT (content)` in `.claude/workflows/brief_lint.mjs`: #1838 deletes the pin line, and this PR conditions it. Either side's resolution keeps #1838's tree green, as the matrix shows. The resolution delta returns to the #1838 reviewer.
