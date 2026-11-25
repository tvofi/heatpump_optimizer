# RESULT merge-actw (R11-SEAM-actuation-writes, merge-main repair)

New head: 0708c57bbf7056e65a32b93604b2d80e0d676b42 on refs/heads/handoff/r11-seam-actuation-writes (fast-forward from a41db633a2).
- 794d649111 merge of origin/main d3d66c4040 into a41db633a2
- 0708c57bbf structure record: module_excess_loc 21742 -> 21740 (lowered, no raise)
Body: handoff-body/r11-seam-actuation-writes at 4e2afe76c6c9655c4a39668505d88aa4c65ab67c (read back identical to the pushed file).

## Resolution per conflicted file

- custom_components/heatpump_optimizer/pump_arbiter.py (content, 2 hunks):
  1. FeedbackRun/ArbiterState: the branch moved them to arbiter_record.py; main added `cooling_asked: bool = False` to ArbiterState. Kept the move; the field lands in arbiter_record.py after `held_until` (main's position).
  2. supply_tick: the branch split it into the step half and `_supply_half`; main added `retry = held.supply_held or held.cooling_asked`. Kept the split; main's retry guard is in `_supply_half` (its auto-merged `if on != last or retry:` reads it), docstring names the cooling-refused retry.
  Read back at 0708c57bbf: main's side: retry line, `on != last or retry`, `cooling_mode`, `cooling_asked` field, each present once; branch's side: `_supply_half`, `tail_lock`, `step_pending`, classes only in arbiter_record.py; no conflict marker.
- tests/mutation_ledger/killed_by/pump_arbiter.py/supply_tick.BOOLOP.2b7310d1.json, supply_tick.GUARD_OFF.2b7310d1.json, supply_tick.GUARD_OFF.f8d725b0.json (rename/delete + modify/delete): dropped (the branch's deletion kept). At the merged code `supply_tick` holds neither line: both are in `_supply_half` (pump_arbiter.py:2096, :2106), so no supply_tick site exists to pin. The `_supply_half` sites are listed in the body's `## Unpinned sites` for `mutation-autofix` (ci-autofix.md). They were re-measured with `mutation_table.py --anchor` against tests/features.py (verdicts below, when they finish). `--pin-killed` over the whole branch diff ran past 30 min and was stopped, and it recorded nothing.
- tests/structure_budgets.json, tests/closures.json: resolved by the repo's LEDGER-MERGE driver (structure deltas summed; closures merged as sets). structure.py then measured module_excess_loc 21740 against 21742 (the two `cooling_asked` lines in arbiter_record.py, not past-limit pump_arbiter.py) and the row was re-recorded at 0708c57bbf; recorded_at d3d66c4040. No budget raised.

## Gate (at 794d649111, the merge commit)

`GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=d3d66c4040 ./tests/run.sh`
- `MODE: SCOPED -- 30 script(s) run, 4 scoped out.` (frontend.py, ha_contract.py, open_meteo.py not run; layout.py run_always)
- `1 TEST SCRIPT(S) FAILED`, rc=1: tests/structure.py, exit 2, "1 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED" (module_excess_loc). The merge caused it, and 0708c57bbf records it; `python3 tests/structure.py` there exits 0.
- features.py: ALL 6224 FEATURE CHECKS PASSED; entities.py: ALL 2763 ENTITY CHECKS PASSED; stress.py, harness_headers.py ok.
- `node tools/policy/brief_lint.mjs`: exit 0, 0 errors, 0 warnings.
- `tools/audit/archscore/score.py --diff d3d66c4040 HEAD`: dS +0.0017 IMPROVES (coord_footprint 2531 -> 2528).

## Body update

Head, merge base, features/entities counts, the structure row, the post-merge gate line and the archscore line updated. `ci_predict.py --rekey-body --from a41db633` re-keyed 48 `## Unpinned sites` lines. 12 more were re-keyed by identical text at a41db633 (arbiter_record +2 past the new field, coordinator -7; pump_arbiter 2102 BOOLOP -> 2096 and 2112 GUARD_OFF -> 2106, whose text main's retry changed), and 2096 GUARD_OFF was added. `ci_predict.py --only mutation`: all 82 predicted sites listed, none missing.
Notes: body_push printed "no Prepr: trailer" (the open runs the full prepr) and "could not delete the kept body handoff-wip/r11-seam-actuation-writes-body".

## `_supply_half` anchor re-measure (`mutation_table.py --anchor ... --scripts tests/features.py`, records nothing)

- `pump_arbiter.py:_supply_half BOOLOP 2b7310d1` (line 2096): killed by tests/features.py; baseline rc=0 failed=0 (1451s); null control pump_arbiter.py:232 NULL_COMMENT survived.
- `_supply_half GUARD_OFF 2b7310d1` (2096) and `_supply_half GUARD_OFF f8d725b0` (2106): NOT RUN. The run hit its 90-minute background limit during the second anchor (about 25 minutes of features.py baseline per anchor). Both are under the body's `## Unpinned sites` for `mutation-autofix`.
