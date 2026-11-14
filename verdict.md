Fix review: merge 2c121b9e1469abe060a53d912bcb76c88ff6e251

bus-nonce: 31993a8aababd739ceb971702f1216cb
pending-ci: gate

## Scope

Round 4 by this seat's count: a07c37b273 blocked, 12a6617f07 merge, d713ca529a blocked, and now 2c121b9e14. Delta review: `git diff d713ca529a8803eae031184d7f34f49ea5085fa3 2c121b9e1469abe060a53d912bcb76c88ff6e251`. The head is a merge of 23ff522a7c into d713ca529a, and `git diff 23ff522a7c 2c121b9e14` is empty. `review_carry.py d713ca52 2c121b9e` printed `FRESH-REVIEW`. The production delta is one statement plus its docstring: the `OffStepNotice.check` gate at `custom_components/heatpump_optimizer/legionella.py:104-106`. It touches no already-reviewed code beyond that statement, so the scope is not widened.

## Prior block (b04a1f7a, equivalence-refuted): resolved

- **The verdict's probe at this head.** `ev/probe_75.py` (copied from verdict/3581) gives `ev/probe_75_head.txt`: all 18 rows return `None`. At d713ca52, 15 of those 18 rows raised `below = above = target` (`ev/probe_75_at_d713ca52.txt`). Above the 70 °C cap the off-step notice no longer rises, and the unreachable notice stands. That is pinned by `a hard-cap shortfall leaves the unreachable notice's hardware advice standing`.
- **The `survivor_triage` row is gone.** At the head, `ev/ledger_rows.txt` lists no `survivor_triage` row for `OffStepNotice.check`. The restated statement's site is pinned at `killed_by/.../OffStepNotice.check.CMP_BOUND.9fc86b4c.json`. 9fc86b4c is the sha1 prefix of the head's line 104 (`ev/gate_line.txt`). The stale GUARD_OFF 03f00051 row was removed with its line. `ci_predict.py --base origin/main --only mutation` reports no unpinned site (`ev/ci_predict_mutation.txt`).
- **The fixer's claim that the 55/62 pin kills the verdict's suggested shape holds.** Mutant `verdict_suggested` (`target <= above_c <= params.dhw_hard_max_temp`) and mutant `verdict_suggested_range` (`written_c < above_c <= params.dhw_hard_max_temp`) both give guard_pins rc=1 with 13 FAIL lines, the first being `55/62 on step 5 is named: 62 configured, 60 written, 60 and 65 on the step`. Both differ from the head on all 2883 raising census rows. The reason: `params.dhw_hard_max_temp` = min(70, max(everyday, target)) equals the target whenever target ≤ 70 and everyday ≤ target. A raised row always has `above_c > target`, so that bound refuses every legitimate notice. The head's `replace(params, dhw_legionella_temp=above_c).dhw_hard_max_temp` reduces to `above_c <= 70` on the cycle path: mutant `hard_literal70` matches the head on all 51660 census rows, as expected. It reads the cap from its owner and is not a defect.

## Attacks on the restated gate (reviewer's driver `ev/mutants.sh`, reviewer's census `ev/census.py`)

The census has 51660 rows:
- entity min 30, 60 or 61
- entity max 55-80, including the off-step maxima 67.5 and 68.3
- steps 0.5, 1, 2.5, 3 and 5
- everyday 55, 65 or 72
- disinfection 55-75 in steps of 0.5
- both credit rules

This is wider than guard_pins' 2856-row census, which uses min 30/60, steps 0.5/1/3/5, everyday 55 and integer targets.

| mutant | guard_pins | census rows differing from the head |
|---|---|---|
| `range_le` (`written_c <= above_c`) | rc=1, 3 FAIL (range-cap pins, census) | 17613 |
| `range_dropped` | rc=1, 3 FAIL | 17613 |
| `hard_dropped` | rc=1, 4 FAIL (hard-cap pins, census) | 2403 |
| `hard_lt` (`<` the hard maximum) | rc=1, 13 FAIL | 2883 |
| `hard_at_target` (`replace(..., =target)`) | rc=1, 13 FAIL | 2883 |
| `verdict_suggested`, `verdict_suggested_range` | rc=1, 13 FAIL | 2883 |
| `above_minus_margin` (`written_c < above_c - margin`) | rc=0, ALL 88 PASSED | 0 |
| `old_plus_hard` (`target <= above_c <= hard`) | rc=0, ALL 88 PASSED | 0 |
| `hard_literal70` | rc=0, ALL 88 PASSED | 0 |

- **The range clause `written_c < above_c`.** Its equivalence to `above_c >= target` once the hard clause holds (`old_plus_hard`) survives the wider census with 0 differing rows. That includes off-step maxima, min 61 over targets 55-60, and an everyday set-point above the target. The body's argument checks out: where the entity's maximum binds, both `written_c` and `above_c` clamp to it and are equal. An `above_c` under the target with `written_c < above_c` needs `above_c` over the hard maximum, which the second clause refuses. `<=` and dropping the clause are killed.
- **The `above_minus_margin` survivor.** It is equivalent on this census (0 rows differ). That matches the body's argument, which no longer needs the ≤ 70 bound: where `above_c >= target`, `written_c < target - margin` implies `written_c < above_c - margin`, and where the range binds, `written_c == above_c` falsifies both forms. The body says the ledger inventory generates no operator site for it. `ci_predict` lists no unpinned site, which agrees.
- **Head invariant.** Every one of the 2883 raised census rows reads `below < target <= above <= min(max, 70)`, `above - below == step` and `written < target - margin` (`ev/census_check.py`: `CENSUS-CHECK raised=2883 bad=0`).

## Evidence

- `ev/HEAD.txt`: 2c121b9e1469abe060a53d912bcb76c88ff6e251, the head measured. Its PR body names this head under `## Head`.
- `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` at the head: `ALL 88 GUARD PIN CHECKS PASSED`, rc=0 (`ev/guard_pins_head.txt`). This matches the body's 88. The body's census figure `277 of 2856` is asserted by the pin `_RANGE_CENSUS = (2856, 277)`, which passes.
- `git merge-tree --write-tree origin/main 2c121b9e`: rc=0, no conflict (`ev/merge_tree.txt`).
- VERSION, manifest and RELEASE_NOTES: `git diff --stat merge-base...head` over those three paths is empty.
- Required checks: `merge_train.py classify 2c121b9e --pr 3581` printed `WAIT 2c121b9e1469abe060a53d912bcb76c88ff6e251 pending: gate red: none` on every poll from 06:42 to 07:13 UTC (`ev/classify.txt`). The review is otherwise complete, so it returns with `pending-ci: gate` and the relay holds it until green. The previous rounds' `tests / mutation` red is answered in the body's `## Red checks`, which names the check and its cheaper detector (prepr ci_predict, step 6d).
- Forward-carry: the service's 71-75 range against the 70 °C cap is carried to R11-INTAKE-R10-RESIDUE. The packet's carry_audit reports it routed: `1 routed, 0 unrouted, 0 bad destination(s)`.
- Not re-derived: the body's `mutation_table.py --max 0` figures (`2305 unpinned ... 7521 candidate sites`), which come from a CI-heavy run. CI's `tests / mutation` at this head is the evidence for them.
- Round count: by this seat's count this is the fourth review round, but the body carries no `## Re-cut`. fixer.md says the fourth round re-cuts the body and that `bus.sh dispatch` requires it. The dispatcher accepted this round without one. Whether the merge-verdicted 12a6617f07 round counts is the dispatcher's tally, not this review's to settle. Carry: dismissed: evidence, not a finding; the dispatch gate that enforces the re-cut ran on the orchestrator's side.

## Findings

none

## Friction

none
