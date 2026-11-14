R10-DISINFECTION-STEP-NOTICE: product ruling (2) of origin/handoff-body/r10-product-ruling-dhw-hard-max at d507c499 ("respect-and-surface"), completing outside pull request 3439's request. A disinfection cycle whose write the hot-water entity's step leaves under the credit threshold in force is named before it runs, with the configured, written and on-step temperatures, and credited nothing.

What changed, by owner:
- `pump_arbiter.py`: `cycle_write` exposes the cycle write for the parameters in force — `thermal_model.dhw_step_target_c` on a cycle step, on the hot-water entity's `inputs.SetpointGrid`, the one statement `_dhw_write` itself reads — with the disinfection temperature on the step down and up (`SetpointGrid.bounded`) and the entity's step (`SetpointGrid.step`); `None` outside control, with no set-point entity state, or with no cycle temperature. The quantisation has one owner (`SetpointGrid`) and the guard never restates it.
- `legionella.py`: `OffStepNotice`, a small class beside `LegionellaGuard`, in `check_ceiling`'s signature-and-`set_issue` shape, not persistent, raises `dhw_legionella_off_step`. Active when hot water and the cycle are active, the arbiter writes a set-point entity, and that write is under target less `CREDIT_INSTANT_MARGIN_K` (1.0), or less `CREDIT_HOLD_MARGIN_K` (0.5) under `dhw_free_disinfection_enabled`. The margins are the guard's own credit literals named, values unchanged, read by `async_track`, `async_track_cycle` and the notice alike. Only a step gap: the notice also requires the step above the target to be writable (`write.above_c >= target`). Where the entity's own maximum binds (a hot-water set-point capped at 60 under a 65 disinfection temperature), no step is the remedy, so no off-step notice rises and `dhw_legionella_unreachable` keeps its immersion-heater advice, as at base.
- Which notice shows: the off-step one. Raising it clears `dhw_legionella_unreachable`, and `raise_unreachable_issue` clears instead of raising while it stands, so its immersion-heater advice never shows for a rounding gap.
- `strings.json`, `translations/en.json`, `de.json`, `sv.json`: the notice text (placeholders `legionella_temp`, `written`, `step`, `below`, `above`); `README.md`'s notice list beside "Hot water is not reaching the disinfection temperature". User-facing text for its own text review: it names the cause, says no hardware is needed, and offers the step above (at least as hot as chosen) before the step below.
- No change to the arbiter's write, `dhw_hard_max_temp`, the thresholds or `DHW_LEGIONELLA_RETRY_HOURS`.

Placement: the brief puts the notice "beside `check_ceiling`". A method on `LegionellaGuard` measured `class_excess_loc` +47 (the class is over `GOD_CLASS_LOC_LIMIT`); the notice is one concern with its own state, so it is its own class under the limit in the same module, and the guard holds it. The guard's remaining two wiring lines are paid by naming the margins in the peak-rule comment: re-recorded `class_excess_loc` -1, reason in the commit. Alternatives: a guard method (+47, a raise for no gain in code); a callable through the coordinator's constructor (adds to the coordinator class, also over the limit).

Carry 0 of the brief (from #3452, item 9ac8c410) is discharged here: the shortfall the hard maximum leaves is surfaced, the ceiling stays.

Carry 1 of the brief (the owner ruling of 2026-11-13 folding this outside-sourced group into round 10) is a scheduling ruling, not a change: this pull request is that fold, and it carries no code of its own.

## Head

`4328fc4245939ca37c7e4dfb6b503379d9ed164b` (measured `2026-11-14T05:45Z`, origin/main `f7e7a0244a3d5f7763c4ec15d193d03ef4bb3274`): the pull request's head `12a6617f07` (4312a91719 plus update_pr's merges, reviewed `merge`) plus `4328fc4245`, ledger only. CI's `tests / mutation` refused 12a6617f07 with `MUTATION TABLE REFUSED -- 2307 unpinned site(s) against 2309 at the ratchet base 513a07dfdc, 2 of them added by this diff`. mutation-autofix reported `1 added site(s) left alive: custom_components/heatpump_optimizer/legionella.py:100 CMP_BOUND`. The two added sites are the two mutants of the one anchor `legionella.py:OffStepNotice.check CMP_BOUND 03f00051`. `4328fc4245` records that anchor under `survivor_triage` as `equivalent`, with the argument in `## Unpinned sites`, and the ledger normalized by `mutation_table.py --normalize`. At this head, `python3 tests/mutation_table.py --base origin/main --max 0` on the tree merged with origin/main f7e7a0244a reports `2305 unpinned site(s) of 7523 candidate sites, 2309 at the ratchet base` and `MUTATION TABLE PASSED`. `ci_predict.py --base origin/main` reports `no closures, fast, governance or instrument red predicted` and no unpinned site.

`4312a9171962c17e4301427d866bf740d10b07a5` (measured `2026-11-14T03:40Z`, origin/main `c987209cc7a891e0e4066d4ad8dc5cf55357c5ae`): `ebc79b0e86` plus two commits, ledger only, no production or test change. First, merge `451cf391fb` of the pull request's branch (`8551fc9f78` mutation-autofix's pins at 47dd9c3594, `1a74f9018f` the delivery row), a clean merge. Then `4312a91719`. The update's prepr refused three of those pins as stale: `STALE PIN custom_components/heatpump_optimizer/legionella.py:OffStepNotice.check BOOLOP / CMP_BOUND / GUARD_OFF b41b8887` (the predicate line before the range gate). `4312a91719` removes them and pins the new line's GUARD_OFF with `python3 tests/mutation_table.py --pin-killed --scripts tests/guard_pins.py`: `pinned   custom_components/heatpump_optimizer/legionella.py:100 GUARD_OFF -- killed by tests/guard_pins.py`. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at this head: `no closures, fast, governance or instrument red predicted`, and one unpinned site, answered under the unpinned-sites section.

`ebc79b0e86c9924707db0ff41082258b2f38f653` (measured `2026-11-14T03:25Z`, origin/main `c987209cc7a891e0e4066d4ad8dc5cf55357c5ae`): `47dd9c3594` plus the fix review's block repaired (verdict on `probe/revt-r10-disinfection-step-notice-591f84c2`: an entity range cap read as a step gap), in two commits, test first: `9d9fc02b38` (`tests/guard_pins.py` only) and `ce4b63531c` (`legionella.py`, `OffStepNotice.check`'s predicate and its docstring). Then a clean merge of origin/main c987209cc7, which carries PR 3578's weekend-clock fix (no file of this group). The reviewer's delta is `git diff 47dd9c3594 ebc79b0e86 -- custom_components/heatpump_optimizer/legionella.py tests/guard_pins.py`. The rest of that range is main's. At this head a full `tools/pr/prepr.sh` (no skip flags; `MUTANT_CMD` is `tests/guard_pins.py`) printed `PRE-PR: ebc79b0e86... rc=0`, with `diff mutants`: no survivor among the diff's first 40 mutants. Its closures step skipped as the non-Linux seat's default: the scoped recordings are left to CI's `closures` context.

`47dd9c3594bd1a365a274cc6d5949e91b3d1b834` (measured `2026-11-14T02:34Z`, origin/main `8af37bdf444d46715272a8bc2fdda02e1d8376e3`): `a07c37b273744ade8cc2c48d07d4a79c58365196` plus a clean merge of origin/main 8af37bdf44 (`git merge-tree --write-tree` reported no conflict), whose only change under `custom_components/` is the v7.1.16 stamp (`manifest.json`, the card's version string). At this head `tests/guard_pins.py` prints `ALL 79 GUARD PIN CHECKS PASSED`, `tests/block_duty.py` `ALL 153 BLOCK DUTY CHECKS PASSED`, and `tests/structure.py` `class_excess_loc 17502 <= 17502`. `ci_predict.py --only mutation` lists the same 13 sites as at a07c37b273, and `pump_arbiter.py:1224 GUARD_OFF` is `cycle_write`'s guard, which this branch adds. The opener's 7d refusal of that key came from a pre-repair body that still keyed 5c961851a2's lines (1257, 1259); this body names it.

`a07c37b273744ade8cc2c48d07d4a79c58365196` (measured `2026-11-14T00:56Z`, origin/main `50373173d486faf394b24637c177ab38b691b394`): the handed-off head `5c961851a2aa13501912dc5f959f8270ba7885c0` plus merge `a07c37b273744ade8cc2c48d07d4a79c58365196` of origin/main 50373173d4, the repair the opener's `merging origin/main into 5c961851a2 conflicts` refusal asked for. The reviewer's delta is `git diff 5c961851a2aa13501912dc5f959f8270ba7885c0 HEAD`, resolved file by file:
- `pump_arbiter.py` (content conflict, three hunks): main moved `_bounded`'s body into `inputs.SetpointGrid.bounded` (`_grid`, `setpoint_grid`) and `_dhw_write`'s cycle and everyday arms into `thermal_model.dhw_step_target_c` (`_dhw_target`), the same quantisation this branch had split into `_bounded_on` and `_cycle_c`. Union: main's import line, `_bounded`, `_grid`, `_dhw_write` and `_dhw_target` taken whole; this branch's `CycleWrite` and `cycle_write` kept with their contract, re-expressed on main's owners (`setpoint_grid` in place of `_bounded_on`'s entity-state check, `dhw_step_target_c(params, True, grid)` in place of `_cycle_c`, `grid.bounded(target, rounding=...)` for below and above, `grid.step` in place of `setpoint_step`). `_bounded_on`, `_cycle_c` and the `setpoint_step` import are gone: main's grid is their one owner. Read back: every main-side line of the three hunks is in the merged file (`git diff origin/main HEAD -- custom_components/heatpump_optimizer/pump_arbiter.py` is the `CycleWrite`/`cycle_write` addition alone), and the branch-side clauses survive as `cycle_write`'s three `None` arms and its four fields. One semantic delta, named: the branch's `cycle_write` returned `None` with no `dhw_cycle_temp` through `_cycle_c`; the merged one tests `params.dhw_cycle_temp is None` itself, since `dhw_step_target_c` falls back to the everyday target there.
- `tests/mutation_ledger/killed_by/pump_arbiter.py/_bounded.GUARD_OFF.835d5167.json`, `_bounded.RETURN_DEL.f7af5135.json` (rename/delete): main's rows kept. The branch deleted their predecessors (`ebd65023`, `d4401a97`) because its `_bounded` changed; the merged `_bounded` is main's, and each row's `old` line is in the merged file (sha1 of the line, first 8 hex, is the row's suffix: `mutation_table.py` anchor rule). Re-derived by the ledger's own tool, not by hand: main's ledger checked out, then `python3 tests/mutation_table.py --carry-rows e23124ff6e45bac1d48b4a775dad555a37965355 5c961851a2aa13501912dc5f959f8270ba7885c0` printed `CARRIED` and left the ledger byte-identical to main's (`git status --short tests/mutation_ledger` lists only main's own staged rows): the six rows the branch deleted have no file in the merged tree.
- `tests/structure_budgets.json`: auto-resolved by the ledger merge driver (`class_excess_loc` 17514 + both deltas = 17502); `python3 tests/structure.py` at the merged head: `STRUCTURE RATCHET PASSED`, `class_excess_loc 17502 <= 17502`.
- `strings.json`, `translations/{en,de,sv}.json`, `README.md`: auto-merged, read back. Key parity across all four: 1509 leaf keys each, none missing or extra against `strings.json` (a `json` walk of each file). Main's #3531 and #3557 added the hysteresis entities and `dhw_minimum_above_start`; neither touches `legionella.py` (`git diff --stat e23124ff6e 50373173d4 -- custom_components/` lists no `legionella.py`). Re-verified sentence: the `dhw_legionella_off_step` description's "so it writes {written} °C", against the merged `cycle_write`, whose `written_c` is `dhw_step_target_c` on a cycle step, the value `_dhw_write` returns there; pinned by `55/62 on step 5 is named: 62 configured, 60 written, 60 and 65 on the step` in `tests/guard_pins.py`, passing at the merged head. Its "retried about a day later" reads `DHW_LEGIONELLA_RETRY_HOURS` in `legionella.py`, unchanged by main.

## Mutation proof

Each mutant applied to `legionella.py` alone, `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` run, restored (at 5c961851a2; `legionella.py` is unchanged by the merge):
- M1 threshold constants swapped between the two rules: FAIL `R10-DISINFECTION-STEP-NOTICE the slider grid raises 201 of 1750 under the instant rule`, `... 436 of 1750 under the hold rule`, `... the instant rule's 201 are all at step 5`, `... the harness grid raises 34 / 71 of 330 (instant / hold)`.
- M2 the write restated as `round(target / step) * step` in place of `cycle_write`'s: the same four FAIL.
- M3 cycle predicate dropped (`cycle = True`): FAIL `R10-DISINFECTION-STEP-NOTICE null: hot water disabled raises none`. With the cycle itself disabled the arbiter's answer is already `None` (`dhw_cycle_temp` is `None`), so the predicate's live arm is hot water disabled.
- M4 `raise_unreachable_issue` raising under the off-step notice: FAIL `R10-DISINFECTION-STEP-NOTICE the off-step notice shows, not the unreachable notice's hardware advice`.
- M5 the unreachable notice not cleared when the off-step notice rises: the same FAIL.
- The credit edges, through `LegionellaGuard.async_track` (`_credit_edges`): `>=` to `>` or `if False:` on the hold rule FAIL `... hold credit counts target less 0.5 and not 0.01 under`; `<` to `<=` or `elif False:` on the instant rule FAIL `... instant credit counts target less 1.0 and not 0.01 under`. The notice's memo `if False:` FAILs `... an unchanged off-step signature does not re-raise the notice`.

The merged `cycle_write`, at the merged head, `tests/guard_pins.py` (driver `/root/mut.sh`-shaped: `sed` one line, run, `cp` the original back, `cmp` confirms the mutant applied and the restore):
- `if grid is None or params.dhw_cycle_temp is None:` to `if False:`: rc=1, `AttributeError: 'NoneType' object has no attribute 'bounded'` in `cycle_write`.
- `dhw_step_target_c(params, True, grid)` to `grid.bounded(float(params.dhw_cycle_temp))` (the hard maximum dropped): FAIL the four count pins of M1.
- `grid.step` to `1.0`: FAIL `55/62 on step 5 is named: 62 configured, 60 written, 60 and 65 on the step`.
- `rounding="down"` dropped from `below_c` (nearest): survived at a07c37b273 (`ALL 79 GUARD PIN CHECKS PASSED`). Now killed by the `63 on step 5` row below.

The repair at `ebc79b0e86` was checked with `python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'env PYTHONPATH=tests/hastub python3 tests/guard_pins.py'` (a git-archive copy; NULL first): `SURVIVED NULL`. The following were KILLED:
- `range_gate_off` (the `write.above_c >= target` clause dropped, the head's predicate as reviewed)
- `below_rounding_nearest` (the finding's mutant)
- `above_rounding_nearest`
- `margins_swapped`
- `cycle_true`
- `memo_off`
- `unreachable_not_cleared`
- `unreachable_raised_under_off_step`
- `hold_edge_strict`
- `instant_edge_le`
- `cycle_write_guard_off`
- `hard_max_dropped`
- `step_constant` (`grid.step` to `1.0`)

Two SURVIVED, both equivalent on the configuration's domain:
- `range_gate_cmp_strict` (`above_c >= target` to `above_c > target`). `above_c == target` means the target is on the step, so the write (`dhw_step_target_c`, the cycle temperature at least the target, bounded with `hi` at the hard maximum, itself at least the target) is not under it, and the first clause is already false.
- `range_gate_above_minus_margin` (`above_c >= target - margin`). `above_c < target` only where the entity's maximum binds, and then `written_c` and `above_c` are both that maximum on the step: `written_c` is the cycle temperature at or above the target, clamped there, so `written_c == above_c`, and the two clauses cannot both hold.
- Both rest on `dhw_legionella_temp` <= 70 (`config_flow.py`'s slider, 55-70), so the hard maximum is never under the target.

Ledger operator sites of the new predicate, measured by `python3 tests/mutation_table.py --anchor "custom_components/heatpump_optimizer/legionella.py:OffStepNotice.check <KIND> 03f00051" --scripts tests/guard_pins.py` (baseline rc=0 failed=0, NULL_COMMENT null control survived):
- `killed by tests/guard_pins.py: custom_components/heatpump_optimizer/legionella.py:100 CMP_BOUND`. The anchor covers 2 mutants and prints one line per key. `--pin-killed` at `4312a91719` separates them: `UNPINNED ...legionella.py:100 CMP_BOUND -- killed by tests/guard_pins.py, but its anchor also covers a site no run killed` and `UNPINNED ...legionella.py:100 CMP_BOUND -- lives`. The live one is `range_gate_cmp_strict` above, which is equivalent.
- `killed by tests/guard_pins.py: custom_components/heatpump_optimizer/legionella.py:100 GUARD_OFF`

Failing test first, repair: `9d9fc02b38` (the pins) on `47dd9c3594`'s production code: `3 of 84 GUARD PIN CHECKS FAILED`, namely `a range-capped write (max 60 under 65, step 1) raises no off-step notice, either rule`, `a range-capped write leaves the unreachable notice's hardware advice standing` and `entity-range census: 683 of 1632 rows raise, ...`. At `ce4b63531c` and at `ebc79b0e86`: `ALL 84 GUARD PIN CHECKS PASSED`.

Failing test first: the pins landed in 028dae841d ahead of the fix. The head's `tests/guard_pins.py` run against the base's production code: `8 of 79 GUARD PIN CHECKS FAILED`; at 5c961851a2 and at the merged head `ALL 79 GUARD PIN CHECKS PASSED`.

## Null control

In `tests/guard_pins.py`, `_off_step_notice_pins`, every count asserted beside the rows it drove (the census asserts its own preconditions): 0 notices over the 1314 on-step slider rows and over the 169 on-step harness-grid rows, under both rules; 0 at steps 0.1 and 0.5; 0 with the cycle disabled, with hot water disabled, with no set-point entity, and with an arbiter that writes nothing (`pump_duty_mode` observe); the stock 55/60 raises none on any step under either rule. All pass at the merged head.

Entity-range enumeration (fixer.md step 8; `_range_census` in `tests/guard_pins.py`), 1632 rows:
- entity min 30 or 60
- entity max 55, 58, 60, 62, 64, 65, 66, 68, 70 or 80 (above the min)
- step 0.5, 1 or 5
- disinfection 55-70
- everyday 55
- both credit rules

This covers min-capped rows (min 60 over a 55-59 target), max-capped rows (max under the target), rows capped at both ends (min 60, max 62-66), and free rows.

Each row is compared with an oracle the test computes itself (`math.floor`/`math.ceil` on the step, no production import): the notice is owed exactly where `min <= floor_step(target) < target - margin` and `ceil_step(target) <= max`. Every raised row must also read `below < target <= above <= max` and `above - below == step`. So `{below}` and `{above}` can no longer be equal, and `{above}` can no longer sit under the chosen temperature.

Result: `154 of 1632` rows raise and 0 disagree with the oracle. At `47dd9c3594`, 683 raised and 1058 rows disagreed.

The range-cap pin uses the reviewer's probe: entity `{"min":30,"max":60,"step":1}`, everyday 55, disinfection 65. Under both rules no off-step notice rises, and after a short cycle `dhw_legionella_above_setpoint` and `dhw_legionella_unreachable` stand, as at base 50373173d4. Its null is a max-80, step-5 entity at 62: the off-step notice still rises and stands in place of the unreachable notice.

Harness, base against 5c961851a2: `dev/audit/harnesses/r10_disinfection_setpoint.py` (sha1 6ced0aeb71d5fc00734eaf4098e65e5e665891e8, unchanged by this diff) run with `--grid` and in its default mode from the base worktree and the head worktree, compared by `cmp`: both byte-identical. Not re-run at the merged head: the merge changes no file the harness's credit thresholds come from.

## Figures

Rows: the slider grid is the config flow's integer sliders (everyday 40-65, disinfection 55-70, disinfection above everyday) on a 30-80 °C number of step 0.1, 0.5, 1, 2, 5; the harness grid is `r10_disinfection_setpoint.py`'s `GRID_TEMPS` cycle rows (disinfection above everyday, at most 70) on the same steps. A row raises when `OffStepNotice` raises after one `LegionellaGuard.async_observe` pass.
- `201 of 1750` slider rows under the instant rule, all at step 5; `436 of 1750` under the hold rule; `0 of 1314` on-step slider rows; `34 / 71 of 330` harness-grid rows; `0 of 169` on-step harness-grid rows: `PYTHONPATH=tests/hastub python3 tests/guard_pins.py` (`ALL 79 GUARD PIN CHECKS PASSED` at the merged head)
- `PYTHONPATH=tests/hastub python3 tests/block_duty.py`: `ALL 153 BLOCK DUTY CHECKS PASSED` at `ebc79b0e86`
- `154 of 1632` entity-range census rows raise, 0 against the oracle; `ALL 84 GUARD PIN CHECKS PASSED` at `ebc79b0e86`
- `class_excess_loc` 17502 <= 17502: `python3 tests/structure.py`
- Architecture score: dS +0.0000 NULL: `python3 tools/audit/archscore/score.py --diff origin/main` at `ebc79b0e86` (origin/main c987209cc7)

Not measured: money (no flat-price arm); Fahrenheit entities, where `step` is in the entity's unit.

## Unpinned sites

None at `4328fc4245`: `ci_predict.py --base origin/main` lists no unpinned site the diff adds. The last one, `custom_components/heatpump_optimizer/legionella.py:100 CMP_BOUND*2` (anchor `legionella.py:OffStepNotice.check CMP_BOUND 03f00051`), now carries a recorded disposition: `tests/mutation_ledger/survivor_triage/legionella.py/OffStepNotice.check.CMP_BOUND.03f00051.json`, verdict `equivalent`. The two mutants of that anchor:
- `written_c < target - margin` to `<=`: killed by `tests/guard_pins.py` (`mutation_table.py --pin-killed` at `4312a91719`).
- `above_c >= target` to `>`: `lives`, and is equivalent. It differs only where `above_c == target`: the target is then on the step and inside the entity's range, so the write (`dhw_step_target_c`, the cycle temperature, at least the target, bounded with `hi` at the hard maximum, also at least the target while `dhw_legionella_temp` <= 70, `config_flow.py`'s 55-70 slider) is not under it, and the first clause is already false.

The ledger disposes per anchor, so the one `survivor_triage` row covers both, and its reason names the killed one. Every other key is pinned under `killed_by` (`8551fc9f78` mutation-autofix, `4312a91719`).

## Red checks

`tests / mutation`: the diff adds sites no ledger pin names yet (the named margins, the new notice and `cycle_write`), so the mutation lane is red until mutation-autofix pins them after the push. Mutation-autofix pinned them at `8551fc9f78`; this head re-keys the predicate's pins (`4312a91719`). The one site left, `legionella.py:100 CMP_BOUND*2`, was red at `12a6617f07`: the table needs a recorded disposition, not a body line. `4328fc4245` records it under `survivor_triage` as equivalent. The cheaper detector is prepr's ci predict, which listed it as a warning and not a red. That warning's standing cost is the gap this round paid for once. The cheaper detector is prepr.sh step 6d, which listed every site before the push; its standing cost is one static read. The merge removed the branch's own `_bounded_on` and `_cycle_c` sites (main's `SetpointGrid` owns them), so the earlier body's `pump_arbiter.py` lines at 595-621, 1221 and 1259 are gone from the list, and main's `_bounded` rows stand.

`tests / closures` and `tests / fast (3.14)`: prepr's closures step was skipped at this head (PREPR_SKIP_CLOSURES=1) because tests/features.py's charge-start-dip day-type check ("a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked") reads the real clock and fails on Saturdays and Sundays at origin/main (from PR 3444); the fix is PR 3578, owned by R10-HOTFIX-FEATURES-WEEKEND-CLOCK; no cheaper detector in this group; CI's closures job judges the head once the hotfix is on main. PR 3578 merged at origin/main c987209cc7, which `ebc79b0e86` contains; the closures step's result at that head is in `## Head`.

## Forward-carry

none

## Friction

none
