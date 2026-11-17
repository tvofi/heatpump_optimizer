Fix review: merge 3eedf54288cd1ce6ebbc4702758a8023e3619431

bus-nonce: 6b6b607ad07df3b88887a38a343f0ef8

Round 2, scope `delta` over the reviewed head 2eee862d2d61b2fe2431c979048360d1b4392cfa. The PR's own delta is f51c5bde89 and 24f6fe48b5 (`tools/audit/seat/plan_audit.py`, `tools/audit/seat/instruments/plan_audit.py.md`, `tools/policy/check-wave-script.mjs`). The two merge commits 4cf9b98ae7 and 3eedf54288 have trees equal to `git merge-tree --write-tree` of their parents, so neither carries a resolution. No `custom_components/` delta, so the review is not widened. The contract is current: `git diff <merge base>...origin/main -- dev/governance/roles/` is empty (`ev/contract-current.txt`).

## Evidence

- Item 1 (unregistered `cards`/`escapes`) is resolved. `REGISTERED` feeds both `derived_rank` and the `check_block` loop. Hand-mutant g (the loop's predicate set to `False`) gives `112 checks, 4 failed`. Mutant h (`cards` dropped from `REGISTERED`) crashes with `KeyError: 'cards'`. Mutant a (`row[r] == "in"` set to `True` in `escape_rows`) gives 1 failed (`ev/mutants-head-reviewer.txt`). In the real-run control A, a fixture card from `check_scopes.py --open-cards` (`E11-GATE-REDS`) prints `OBJECTIVE PASS`, rc 0 (`ev/realrun-baseline.txt`).
- Item 2 (plan-chosen baseline) is resolved. The record is read at `BASELINE.format(round-1)`. Mutants b (path), c (round) and d (blob predicate) each fail the self-test. Real run B: `tree` removed and the record doctored in place on the plan's branch prints `FAIL BASELINE edited: ... (main 745c2a99..., plan e03d2e4a...)`, rc 1. The undoctored twin D prints `OBJECTIVE PASS`, rc 0.
- Item 3 (settlement status choices unpinned) is resolved. The previous round's `driver-mut.py`, re-run at this head, kills b01-b12, b14-b21, r01-r05 and r07-r29. b13 and r06 no longer match because their lines were rewritten; their re-anchored forms (my mutants e and g) are killed (`ev/mutants-head-prevspec.txt`). I ran the in-tree `mutant_run.py --diff 2eee862d...HEAD --path tools/audit/seat/plan_audit.py --cmd "python3 tools/audit/seat/plan_audit.py --self-test"` over the delta: 155 mutants, 81 SURVIVED. None is in `check_block`, `settle`, `baseline_refusals`, `escape_rows`, `kept_in_floor`, `derived_rank`, `moved` or `term_reading`. 28 are in the command-line layer (`_blob` through `objective_settle`), 2 in `main`, and 51 on the self-test's own lines (`ev/mutant_run-delta.txt`, `ev/delta-survivor-src.txt`). `check-wave-script.mjs` prints `255 passed, 0 failed`, and `254 passed, 1 failed` with `'objective'` dropped from the `plan/moves` schema's `required` (`ev/mutants-audit-plan-js.txt`).
- Item 4 (a ranked done group crashing `replan.py`) is resolved. Mutant f (the `RANKED done group` branch set to `False`) and mutant e (`e.get("done") or ` removed from `kept_in_floor`) each fail 1 check. In the real-run fixture, the previous round's ranking of every roster group printed `RANKED done group` FAILs by name, with no `replan.py` refusal. The control was then cut to open groups only.
- The command-line layer stays out of the self-test, as the design's "one real run" allows and the body's `## Unpinned sites` states. Hand-mutant i (the `"main"` merge-base blob dropped in `objective_check`) survives the self-test (`112 checks, 0 failed`) but is killed by the real run. Case C (the B fixture with the mutant applied) prints `OBJECTIVE PASS`, rc 0, where B refuses. This blob is the only guard against in-place doctoring when the plan names no `baseline.tree`, so the real run is what pins it. The body's own real-run fixtures are out of tree, so its `fake-card`, `fake-escape` and `doctored-baseline` lines are not re-derived. Mine are reviewer-built from the previous round's `driver-mkfix.py`, with the card swapped and done groups filtered.
- RESULT self-test at the head: `plan_audit self-test: 112 checks, 0 failed`. This matches the body.
- RESULT real-run control A: `projection A: critical path 88.7 h, wall 90.7 h`, `floor cost ... dropped 43`, `OBJECTIVE PASS`. These match the body's base figures. Lead time printed `26.8/86.47 h`; the body does not quote it.
- `VERSION`, `custom_components/`, `RELEASE_NOTES.md` and `tests/golden/` are untouched in the three-dot diff (`ev/untouched.txt`). No claim file moves.
- `git merge-tree --write-tree origin/main 3eedf542...` exits 0 at origin/main 8e76c192d269e0837a80d0606f3ac12ebecb223d (`ev/merge-tree.txt`).
- The body's `## Head` names 3eedf54288cd1ce6ebbc4702758a8023e3619431. `git ls-remote` reads the same SHA for the branch and for `refs/pull/3703/head` (`ev/head-readback.txt`).
- The architecture score, the entity count and the budgets are CI's (`arch-score / arch-score`, `tests / fast (3.14)` and `pr-contract / pr-contract` success at this head); I did not re-run them.

## Red checks

- `merge_train.py classify 3eedf542... --pr 3703`: `APPROVAL-OWED 3eedf54288cd1ce6ebbc4702758a8023e3619431 4 budget raise(s), first .claude/workflows/policy_budgets.json: files.dev/governance/roles/architect-planner.md: 85 -> 89 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`, rc 4 (`ev/classify.txt`). Judged as GREEN. `gate` and `budget-raise-gate / budget-raise-gate` are in the `owed-reds` set (`ev/owed-reds.txt`), are red only on that approval, and the body's `## Red checks` answers both.
- `tests / nightly-status` is red and outside the `owed-reds` set.

## Findings

none
