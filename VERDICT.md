Fix review: merge 441adb4aef0b30145226f40e28fde4ceaee36b55

bus-nonce: f89d54412629646ae40049b28f585547

Review round 3, PR #1861 (R9-F10.6), fix-review.md. Measured head 441adb4aef0b30145226f40e28fde4ceaee36b55. It is the PR head at posting and the head the body's `## Head` names. origin/main is 68b8cb97. My briefs copy is current (the three-dot diff of tools/audit/briefs/ is empty).

What was reviewed:
- The authored delta, bdc14972.
- The two merges, which have no hand resolution:
  - edac88f4's tree equals `git merge-tree` of 307ecf6c with 68b8cb97.
  - The head's tree equals `git merge-tree` of 5009fe47 with bdc14972.

## Round-2 block: resolved

The probe now has tie-only controls.
- `equiv_probe.py` counts ties inside the compiled function and uses the review's tie-only controls. It cites rv_equiv_probe.py by sha1 6f7aee1d, which matches my file. That file is published in review/1861's evidence.
- Probe output:
  - `RESULT _holiday_span cases=49 ties=17 mutant_differs=0 control_differs_at_tie=17 control_differs_untied=0`
  - `RESULT _dhw_planner_draws cases=16 ties=11 mutant_differs=0 control_differs_at_tie=6 control_differs_untied=0`
  - `RESULT _dhw_planner_draws tied_cases_with_last_0=5`
- The 5 cases that do not move are exactly m=1 (4 cases) plus n=m=1 (1 case), all with `last == 0`.
- Perturbation, my own: I forced the probe's tie counter to `False`. The probe then reports `ties=0` and `control_differs_untied=17` / `6`. So the untied counter is a live self-check: a broken tie count cannot pass silently.
- Both triage rows and the body quote these counts.

## The moved triage row: a real move

#1858 moved this function into dhw_planner.py.
- `DhwPlanner._dhw_planner_draws` in dhw_planner.py at the head has an AST source segment identical to `HeatPumpOptimizer._dhw_planner_draws` in optimizer.py at 5009fe47 (768 characters each).
- optimizer.py no longer defines it.
- Exactly one inventory site carries `idx = i if i <= last else last`, at dhw_planner.py:679.
- The new row keeps the same digest (56f3545d), the same `old` pin and the same verdict.

The mutation table accepts it, and refuses the alternative:
- At the head it prints `4853 unpinned site(s) of 5466 candidate sites, 4855 at the ratchet base 68b8cb97...; the ledger agrees with the deterministic inventory`, then `MUTATION TABLE PASSED (empty scope)`.
- `--list CMP_BOUND` shows only away.py:558 and dhw_planner.py:679 as `pinned`, then `946 site(s) in 56 file(s), 944 unpinned, ratcheted`.
- Perturbation: with the old optimizer.py row restored and the new row removed, the table prints `MUTATION TABLE REFUSED ... disposition names no site the inventory generates`. Restored, it passes.

## Everything else, re-taken at this head

- My mutants.py: E1 (4 failed), M1 (1), M4 (1), R2 (2), R3 (2), R5 (3), R7 (3), R8 (1) and R10 (3) are killed. R6 and R9 survive, both equivalent as measured in round 1. M0 prints 0 failed.
- Inventory: `head sites=5466 sha1=3f04779a430a unpinned=4853` and `origin/main sites=4520 sha1=fe4c90319eb3 unpinned=3909`. The sha1 moved because of #1858's file move, not because of this diff. The difference, +946 sites, equals the CMP_BOUND stock.
- `mutation_budgets.json`: `keys_changed=['_comment']`, so no cap moved. VERSION, manifest, RELEASE_NOTES and both claim files are untouched (three-dot). `git merge-tree origin/main HEAD`: rc 0.
- Earlier rounds still hold:
  - The ratchet refuses one added one-line comparison and passes an `==` null (round 1).
  - D3-s1-01's -5.0 is kept by production and dropped by the mutant, and each bound's mutant differs only at its own bound (round 1).
  These rounds touched no operator code since round 2's entities.py change, which this mutants.py run re-covers.
- Code owner: `tests/mutation_table.py` is `@tvofi`'s. Its approving review at this head comes under tvofi's mandate and is not this verdict.

## CI (check-runs API, every run on 441adb4a; waitci DONE total=35)

The only non-green conclusions:
- `nightly-status=failure`. Its log reads `NIGHTLY ABSENT: ... mutation-ledger, mutation-ledger-push did not run in that scheduled run`. That is main's red. This PR's three-dot diff reaches no workflow, plan, HANDOVER or foreign delivery row, so the step-11 exemption applies and no Root cause section is owed.
- `pr-contract` and `budget-raise-gate` each have a `cancelled` run, superseded by a `success` run on the same head.
- bdc14972 and edac88f4 carry no red run.

Not run locally: entities.py in full, closures, features.py and the goldens. CI ran them on this head and they are green.
