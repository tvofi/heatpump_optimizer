Fix review: merge 9b4e2cec93f60fb7d78e213ce82ba2755a3d85f8

PR #1839 (R9-EG-B2), round 2. Measured at 9b4e2cec93f60fb7d78e213ce82ba2755a3d85f8, which is the live PR head. The body (b1d9cad7, then 02f4db88) names that SHA. Merge base and origin/main: c168ec0a. `git merge-tree --write-tree origin/main 9b4e2cec` rc=0.

## Round-1 block resolved

RESULT briefs: at 9b4e2cec, `node .claude/workflows/brief_lint.mjs` rc=0. Its ERROR set is identical to main 777c2318's (diff empty). CI `briefs` is green at 9b4e2cec (job 110731333255).
- efe4502a re-cites all five carry-1645.json lines.
- I read four of them at the head: tests/doc_claims.py:463 `def check_initial_setup_menu`, :474 the `split("## Initial setup")` line, :552 `def check_simulate_plan_fields`, and :599 the `_mutated_span.group(1)` line. Each holds the source its carry text quotes.
- The body's "Red checks" section names `briefs`, gives its cause and names the cheaper detector (brief_lint.mjs locally, about 3 s). That answers fix-review.md step 11.

## Delta since round 1

RESULT delta: `git diff 777c2318 b8929353` equals `git diff c168ec0a 9b4e2cec` with three paths excluded (diff empty, CODE_DELTA_IDENTICAL). The excluded paths are the only additions:
- `.claude/workflows/carry-1645.json`: the re-cite;
- `tests/mutation_ledger`: six killed_by pins committed by github-actions[bot] in 0ef1442c, one for each of the six sites the fixer drove by hand;
- `docs/delivery/1839.md`: this PR's own row.

The c168ec0a merge (#1840) shares no file with this branch.

## Re-run at 9b4e2cec (Python 3.13.14)

- doc_claims: ALL 84 PASSED.
- structure: RATCHET PASSED.
- entities: 2 of 2060 failed. They are the same 2 docs/HANDOVER.md `updated-for` ancestry checks that fail at main in this clone (shallow history), so they are not this diff's.

## Carried from round 1 (EG-B2-review-e81eb129)

The package .py files are byte-identical to b8929353 apart from main's own changes, so these hold:
- identity snapshot: 75/75 rows identical across base and head, en and sv. The instrument moves 46 rows under my object-id perturbation.
- private reaches: 0 in the surface files.
- the 4 deleted coordinator properties have no attribute reader in the tree.
- 7 of my 8 mutants were killed. The survivor, diagnostics `mode` back to `_mode`, is an equivalent mutant.
- budgets only move down. VERSION, the manifest and the notes heading are untouched.

## Not this review's

- The fixer's local `tests/stress.py` CPU-budget red appears on main too on that box. CI is the judge.
- CI at 9b4e2cec was still running at posting: fast (3.14), mutation, closures, coverage, typing and browser. The merge seat's CI-green condition covers them.
- `docs/delivery/1839.md` carries the PR title "Merge remote-tracking branch 'origin/main' into work/eg-b2". The PR needs retitling.
