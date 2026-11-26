Fix review: merge 4ab51be4391657b622ad008c6fb4629846bf39c4

bus-nonce: 7f6d23a1ebc7e2efbf8f4d492667714c
pending-ci: tests / mutation-pins (1), tests / mutation-pins (2), tests / mutation-pins (3)

## Scope

Round 4 of #3869's review, a delta over the previous verdict's head 392fe0b7 (blocked metric-gamed). The PR's own commits in 392fe0b7..4ab51be4 are 08ade1c115 (code) and 6e1c645f65 (budget re-record). The rest of the range is two merges of origin/main: bf6c487691 (70f410e996 via bdcfee6dcc) and 4ab51be439 (8f22a3b284). `git show --remerge-diff` of both shows only ledger-driver resolutions (`tests/structure_budgets.json`, `tests/closures.json`) and no hand resolution (ev/remerge.txt). The delta touches `duty_legs.py`, `duty_switch.py` and `optimizer.py` only through entry_rule. CI already covers the rule it shares, so the scope is not widened. The review packet rendered `Review scope: full` only because it was given the same SHA for head and reviewed-head; the dispatch names 392fe0b7.

## Verdict on the previous block (metric-gamed)

Resolved. 08ade1c115 deletes ec6be8dbdf's re-wrap together with the call it wrapped. `duty_legs.entry_rule(split, cfg, before)` is now the only place that reads `cfg.mode_leg_heat_min_minutes`, `cfg.mode_leg_dhw_min_minutes` and the entry leg. Before, there were two spellings of that reading:
- the planner passed the values as three extra `leg_rule` parameters;
- the arbiter (`duty_switch.leg_rule`) called `split._replace(...)` over two lines.

Both now call entry_rule. `leg_rule` returns to main's three-parameter signature, and `optimizer._leg_rule`'s call is back to main's three-line layout with one nested call. The line that `module_excess_loc` gives back comes from the two minimum-leg arguments the call no longer lists. A re-wrap of an unchanged call would not produce it.

Step 14 control:
- Mechanism present (the extra-argument call): `module_excess_loc` measures 21756 at both 392fe0b7eb and ec6be8dbdf.
- Mechanism replaced by the shared rule: it measures 21755 at 6e1c645f65.
- The diff's only change in that range is the sharing. Packing the old call onto fewer lines would be the shape blocked in round 3, and this diff is not that shape.
- archscore over the payment alone, `score.py --diff c51360d13b` run on 08ade1c115's tree, reads `dS +0.0000 NULL`. This reproduces the body's figure, so the payment is not read as worse (ev/archscore_c51360_to_08ade1.txt).

## Evidence

- RESULT mutants (step 1): driver ev/mutant_driver.sh runs the whole of `tests/features.py` from a scratch worktree at the head. Baseline is `1 of 6243 FEATURE CHECKS FAILED`, the `_bootstrap` check, which fails outside run.sh's interpreter path as the body records. All 7 mutants on the shared rule are killed, each adding failures beyond that baseline (ev/mutant_summary.txt, ev/mutants.txt):

  | Mutant | Change | Checks failing |
  |---|---|---|
  | M1 | entry_rule heat_min -> 0 | 4 of 6243 (T9, T11, availability) |
  | M2 | dhw_min -> 0 | 8 |
  | M3 | before= dropped | 3 (T9, the solve's leg rule) |
  | M4 | planner before -> IDLE | 2 (the solve's leg rule) |
  | M5 | arbiter before -> IDLE | 2 (T9) |
  | M6 | planner bypasses entry_rule | 4 |
  | M7 | arbiter bypasses entry_rule | 7 |

  No survivors.
- RESULT re-record downward (`module_excess_loc`):
  - 6e1c645f65 records 21756 -> 21755, matching that SHA's measured 21755.
  - At the head the budget is 21745 and `tests/structure.py` reads `ok module_excess_loc 21745 <= 21745`, `STRUCTURE RATCHET PASSED` (ev/structure_head.txt).
  - origin/main 8f22a3b284's budget and measurement are both 21753, so the head is below main and no `*_budgets.json` row moves up (ev/budget_values.txt, ev/measure_structure_archscore.txt).
- RESULT merge: `git merge-tree --write-tree origin/main 4ab51be4` exits rc 0 with origin/main at 8f22a3b284, which the head already contains (ev/merge_tree.txt).
- RESULT step 5: the PR touches no VERSION, manifest version or notes heading. The own-commit delta is 4 code/test files plus `tests/structure_budgets.json`.
- RESULT CI at the head, read ~07:40Z (ev/checks_0740Z.txt, ev/classify_log.txt):
  - `merge_train.py classify` printed `WAIT ... pending: gate red: none` on every run from 06:03Z to 07:51Z, naming no context.
  - The only runs still in progress are `tests / mutation-pins (1)`, `(2)` and `(3)`, the pinning shards. The pending-ci line above names them.
  - `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / coverage-ratchet`, `tests / typing` and `governance / instrument-self-tests` are green, along with the rest of the owed set apart from the two listed next.
- RESULT owed reds:
  - `tests / mutation` is the predicted unpinned-sites red, which shards into the pin jobs. The body's `## Red checks` answers it as `mutation-autofix`'s normal state, with `ci_predict.py` named as the cheaper detector that already runs.
  - `gate`'s red jobs log `FAIL run(s) [45764677926] at this head are still being judged; their gate decides`. That is a pending aggregate, not a defect of the diff.
- RESULT body figures checked at this head:
  - The round-3 mutant claims are re-derived by M3 and M4.
  - The archscore NULL for the payment is re-derived.
  - `module_excess_loc` 21756 -> 21755 is re-derived.
  - One figure does not re-derive; see Notes.

## Notes

- Note: figure: the body's `## Head` says the ledger driver resolved `module_excess_loc` "21763 + both deltas = 21754" at bf6c487691. The driver's own line (`git show --remerge-diff bf6c487691`) and the file at bf6c487691 both read 21745, which is 21763 - 8 - 10, and the head measures 21745. The tree is correct; only the body's figure is transposed. Carry: dismissed: body paperwork, the tree's figure is right and measured; the next body edit corrects it

## Findings

none
