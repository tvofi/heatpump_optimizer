Design review: approve 0e59437a8f19aae9d9243e2e3dbe2ceb7eb25aec

Delta review (later rounds review the delta only): git diff 79719c386a 0e59437a8f against the five points of design-verdict 3cc75463 and the owner's ruling (tvofi, 2026-11-22, "I want it as settings, default 10 min"). Code read at origin/main 3a98735a7e. Seat token count: not reported by the harness.

Prior points, resolved:
1. Options: resolved. The note names the option keys, `_F` rows with `_number(0, 15, 1, 'min')` beside CONF_PUMP_DUTY_MODE (config_flow.py:1763), EntryConfig fields beside pump_duty_mode (entry_config.py:246), the planner route through planner_fields into OptimizationConfig (defaults 0 = today), and the arbiter route through EntryConfig. It also defines the M > 10 collapse (T3 at M = 10, 12 and 15) and 0 = off.
2. config_flow.py payment: resolved. The named move is `_valid_months_spec` (config_flow.py:1115-1126, 12 lines, grid_fee-only logic) to grid_fee.py (517 lines, under the limit), with the stub at tests/config_flow_steps.py:5210 re-pointed. archscore is run before and after, and the budget-raise route under 6893738184 is the fallback.
3. User-facing text: resolved. docs/configuration.md, the pump_duty_mode data_description in strings.json and the three translations, and the doc_claims rows are now hot files, after FROST-HOLD and FAULT-HOLD.
4. Other paths: resolved. The root cause section now names the single-duty re-solve path, and duty_switch.enter_ok checks every entry into a new duty, which covers the old both-step skip. T1b fails on today's code and has an off-by-time null control.
5. Harness: resolved. Re-solves fall at off-boundary offsets, and the null (options 0) must show re-solve legs_under_10 > 0. The harness adds space_priced_minus_delivered_kwh, with a shipped-array availability pass if that figure exceeds the step-0 bound, and tank_unpriced_kwh, both reading 0 under the null. T8 and T10 now have null controls.

The orchestrator's order ruling (FROST-HOLD, FAULT-HOLD, MODE-LEGS, STEP-KICK) is applied. The frost and fault holds are out of exempt, and win downstream of _served by construction.

Notes for the fixer:
- The `_valid_months_spec` move is claimed only in this note. FLOWCAP (fa8cd134) lands first and leaves its config_flow.py move unnamed ("the build names the move"). If FLOWCAP's fixer takes it, this group names its next move, or the raise route. The orchestrator should place the claim in FLOWCAP's brief. Carry: R11-OWNER-MODE-LEGS (item config-flow-move-claim)
- enter_ok can drop a planned DHW or heating leg entirely when a pass first sees it with less than its minimum left (after a block ends or a held leg runs on). Count refused entries on the synthetic harness, and define the rec.leg-is-None case (after a restart, enter as today). Carry: R11-OWNER-MODE-LEGS (item entry-refusals)
- Absent-is-default turns the rule on for every install at upgrade. The release note states the change and how to turn it off (0) first, under the release-extra-steps practice. Carry: R11-OWNER-MODE-LEGS (item release-note-first)
- The round-1 carries stand as restated in the note: lease, frost-exempt, leg-history-owner, batch-cost, legrule-tuple.
