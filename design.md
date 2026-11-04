# Design note: R10-WHY-NOW-WIDGET (architect note, extended)

Base: `c3a279e3252a8b57bb00b5a677318cd4fe20387f` (origin/main; round 2, unchanged from round 1's base, so
every round-1 citation stands). Round 2 answers revise point 1 (card footprint, §3 "Card" and §6
"Goldens") and folds the verdict's fixer notes r1-a..r1-c. The predecessor R10-GRADE-DRIVERS
has been dispatched but has no `handoff/` head, so this note reads the code at that base. Its seam is
decided: drivers are published by the coordinator and rendered by the card, mirroring
`envelope_drivers`. This note relies on that seam only. Size L. There is no finder harness: this is
an owner report (tvofi 2026-11-01, rulings card 2 option (c) part (b), on R10-UX-HEALTH carry 14).

## 1. Measured at the base
- The solver publishes one string code per step and nothing else: `space_reasons` comes from
  `classify_space_steps` (custom_components/heatpump_optimizer/optimizer.py, built in `_build_result`).
  That code is a ranked post-hoc label. It carries no direction and no weight, and its docstring says
  no term of the scalar objective "wins".
- The mold guard reaches the solver as `SolveLimits.min_temp_floors`, from the coordinator's
  `_mold_floor_series`, which returns None when the guard is off or has no reading. It is merged into
  `temp_min_bounds` in `_build_comfort_bounds`, and the mold floor is not kept separately on `_Horizon`.
- Away mode is not a solver input. The coordinator lowers the comfort numbers before the solve
  (`solve_bands` in custom_components/heatpump_optimizer/away.py, and `_fold_away` in coordinator.py:
  the solved floor is min(configured, away target)). Holiday days reach the solver as `holiday_flags`
  and the holiday comfort pair on `OptimizationConfig`.
- The step that contains now is `_step_index` in custom_components/heatpump_optimizer/pump_arbiter.py,
  which is private. The coordinator has no current-step helper of its own.
- The card (custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js) has no live widget.
  Its strings live in the in-file `STRINGS` table.

## 2. Owning seam
**The solver seam owns this change.** A new pure module (new file, not yet in the tree) `slot_drivers.py` in the package
(numpy only, beside plan_slots.py), computes the drivers, and `HeatPumpOptimizer._build_result` calls it
once. The coordinator (`_build_plan_views`, "views" in tests/seam_map.json) only selects the current
step and copies it into the payload. The card only renders. Away is the one fact the coordinator owns.
It enters as a solver input, the same way the mold floor does. This is not a split concern.

## 3. Shape
**Solver input.** Add `SolveLimits.away_floor_drop_c: float | None`: the configured floor minus the
floor solved against, at least 0. It is None when away mode is inactive or in recovery. The coordinator
takes it from the same arithmetic `_fold_away` uses. **Horizon.** Add two optional `_Horizon` fields:
`mold_floors`, the padded `min_temp_floors`, and `comfort_floors`, the floor before mold. Both are
captured in `_build_comfort_bounds`. `temp_min_bounds` is unchanged.

**Result.** Add `OptimizationResult.space_drivers: dict[str, list[float]]`, mapping each code to one
signed weight per step. Plain lists keep it pickle-safe and small (5 x n floats). The codes are
`price_rank`, `comfort_floor`, `mold_guard`, `away` and `forecast`.

**Push.** Each code has a raw push p in [-1, 1], read only from the inputs the solve used at step i.
Positive means "run". B is max((ceiling - comfort_floor)/2, 0.5) and L is 8 h, the lookahead of
`_anticipatory_weights`.

| code | push p_i |
|---|---|
| price_rank | 1 - 2r, where r is the rank of prices[i] among all horizon steps (ties count 0.5). The cheapest step is near +1 and a flat day is 0. |
| comfort_floor | clip((mid - room_i)/B, -1, 1). room_i is the trajectory at the start of the step (the initial state at step 0), and mid is the centre of comfort_floor and ceiling. |
| mold_guard | clip((mold_floor_i - comfort_floor_i)/B, 0, 1). It is 0 when there are no floors. |
| away | -clip(drop_i/B, 0, 1). drop_i is `away_floor_drop_c`, or on a holiday step the configured floor minus the holiday floor from `get_temp_bounds`. |
| forecast | clip((out_i - mean out[i:i+L])/10 + (mean hlf[i:i+L] - hlf_i) - (mean solar[i:i+L] - solar_i)/max(p_max, 1), -1, 1) |

**Weight.** w_k = 100 · p_k / Σ|p_j|, rounded to 0.1. All weights are 0 when Σ|p_j| is 0. The
direction is the sign of w, and |w| < 0.5 counts as neutral. So |w| sums to 100 ± rounding. This is
not `envelope_drivers`' contract: that is `[{code, points}]` with points summing to grade minus
mid-scale (coordinator.py:3130); `why_now` weights are signed percents of one push (r1-a).

**Payload.** Add a top-level key `why_now`, of a new `WhyNow` TypedDict in payload.py:
`{"t": iso, "drivers": [{"code", "direction": "run"|"idle"|"neutral", "weight"}]}`, sorted by |weight|
in descending order. The key is absent when there is no result, when now falls outside the plan, or
when `price_known` is False at the step, which the card text calls "no data". Make `_step_index`
public, or move it into slot_drivers.py: coordinator_private_reach refuses a new reach.

**Carrier.** The space-plan sensor (sensor.py, the attribute block around :1524) publishes
`data.get("why_now")` as attribute `why_now`; the card reads it from the space-plan entity it already
resolves, and from nothing else.

**Card.** A "Why now" block renders from `why_now` alone: one row per driver with ↑/↓/· and the signed
percent. When every weight is 0 it shows one all-neutral line. When the key is absent it shows the
no-data text. The hover on the block and on each row carries the brief's metric explanation, in en
and sv, verbatim. **Mount: inside `headlineHtml`'s `<div class="headline">`
(www/heatpump-optimizer-card.js:9061), after the narrative list**, so it shows wherever the headline
shows (main card and plan dialog, `_render` :14616) and inherits its gate: no headline (`show_stats`
off, or no stat sensor and no narrative line, :9044) means no block and no no-data line.

```
solve inputs ─► _build_comfort_bounds ─► _Horizon(+mold_floors, comfort_floors)
coordinator ─► SolveLimits.away_floor_drop_c ─┘        │
                                   _build_result ─► slot_drivers.space_drivers(h, room) ─► result.space_drivers
coordinator._build_plan_views ─► step_index(result, now) ─► data["why_now"] ─► card renderWhyNow
```

**Invariants.**
1. The plan is byte-identical: the drivers are read after the solve and never written back.
2. No optimality figure moves.
3. The card derives nothing. Every number comes from `why_now`.

## 4. Alternatives, and why each lost
- **Derive the drivers in the coordinator from payload arrays.** The mold and comfort floors exist
  only inside `_Horizon`, so the coordinator would re-derive them. That is a second copy of
  `_build_comfort_bounds`, and coordinator.py is at its max_class_loc and class_excess_loc ratchet.
- **Sensitivity attribution by re-solving with each input neutralised.** It costs 5 extra L-BFGS-B
  solves per cycle on a Pi-class target (D9). The solves are penalty-based, so there is no dual to read.
- **Add weights to `classify_space_steps`' strings.** That changes a published per-step string that
  `plan_slots`, the goldens and the mutation ledger pin, for a different contract.

## 5. Sibling sites
`grep -rn "space_reasons\|classify_space_steps" custom_components/ tests/*.py` finds the current
consumers. None of them changes. `grep -n "min_temp_floors=" custom_components/heatpump_optimizer/coordinator.py`
finds two solve call sites: the plan, and the what-if around line 11133. Both pass
`away_floor_drop_c`, or the what-if passes None and the note in its body says why. DHW is out of
scope: the five reasons are space-heating reasons, and the brief names no DHW driver.

## 6. Evidence plan
- **Failing tests.** In tests/features.py, a solve on a day where step 0 is the cheapest, with room
  mid-band, flat weather, no mold floor and no away, must have `space_drivers` rank `price_rank`
  first and positive. It fails at the base with AttributeError. A case in tests/card.mjs renders the
  rows with marks and weights, and the no-data text when `why_now` is absent.
- **Null control.** A flat-price day at mid-band gives every weight 0, and the card shows the
  all-neutral line. `power_schedule` is equal with and without the module (patch it to return {}).
  `python3 tests/optimality.py` runs before and after with an identical figure.
- **Perturbation.** With `away_floor_drop_c` = 3, `away` is negative and price_rank's share changes.
  A mold floor above the comfort floor moves `mold_guard` from 0 to positive.
- **Goldens, solver.** The tests/golden/coord_*.json captures gain `why_now`, and those floats come
  from the trajectories. Claim them in tests/golden/claimed_drift.txt with the direction "key added".
- **Goldens, card (revise point 1).** `node tests/card_drift.mjs --list` prints 45 states at the base.
  All take the sensors from `planStates` (tests/card_rig.mjs:161), which copies a fixed attribute list
  and so carries no `why_now`; only `score_open` adds the stat sensors (`statStates`,
  tests/card_drift.mjs:101, :232), so it is the only state whose headline renders. Measured with a
  throwaway spike (a no-data `div` after the narrative list, scratch worktree at the base, never
  pushed): `score_open` DRIFT, 44 identical. The claim is therefore exactly one line in
  tests/golden/card_claimed_drift.txt: `score_open`, direction "Why now block added, showing the
  no-data line" (the fixture publishes no `why_now`). Leave `planStates` and plan_view.py's attribute
  copy unchanged, so the drift stays that one state; the card.mjs case feeds its own `why_now`. If the
  fixer instead adds `why_now` to the rig, the direction becomes "block added with rows" and the
  same single state moves; any other moved state is outside this shape and is a stop, not a claim.
- **docs/img/*.svg.** card_drift.mjs:23 warns they may go stale. The two chart figures
  (docs/img/card/chart-anatomy.svg, chart-dashed-lines.svg) are drawn by
  docs/img/card/make_card_figures.mjs from `planStates(plan)` (:77) with no stat sensor, so the headline
  and the block are absent and they should not move. Control owed in the body: regenerate them at the
  merge base and at the head with the generator's header commands; both byte-identical. If either
  moves, regenerate and commit it in the same pull request.
- **Mutation proof.** Target the sign and normalisation lines in slot_drivers.py, and the absent-key
  branch in `_build_plan_views`.
- **Browser.** Screenshots from tests/card_browser.mjs: light and dark, phone and desktop.

## 7. Hot files and serial position
The hot files are www/heatpump-optimizer-card.js, coordinator.py, payload.py, and translations
en.json and sv.json. This group runs after R10-GRADE-DRIVERS. Before the fixer dispatches, the
designer re-reads that group's merged diff. Its driver row and hover helper must be reused here, not
duplicated: duplication_copies is ratcheted. The new module goes on the INERT list or into a closure.
Received (verdict, routed to the orchestrator): R10-ADVISOR-WHATIF (design/R10-ADVISOR-WHATIF) also
holds www/heatpump-optimizer-card.js and coordinator.py hot, including the what-if solve at
coordinator.py:11133 this note touches; the serial order of the two is the orchestrator's call, not
this note's.

## Notes for the fixer
Carry: R10-WHY-NOW-WIDGET (item 0) is owned here in full. Nothing in it is scoped out.
- `_build_result` sits inside the HeatPumpOptimizer class. Keep the addition to one call, and pay
  any class_excess_loc growth by moving the space_reasons assembly into slot_drivers.py with it.
- Re-measure the forecast scale (/10 °C) against one real winter golden. If one driver saturates
  at ±1 on most steps, record the scale you choose and why in the body.

Carry: R10-WHY-NOW-WIDGET (item r1-a). `why_now` weights are signed percents with |w| summing to 100,
not `envelope_drivers`' points (§3 corrected). Reuse R10-GRADE-DRIVERS' row and hover helper with a
field mapping in its call (code, weight, direction for its code, points, sign), not a second row
renderer: duplication_copies is ratcheted.
Carry: R10-WHY-NOW-WIDGET (item r1-b). HeatPumpOptimizerCoordinator is the largest class and sets
max_class_loc, and it still grows here (the `_build_plan_views` addition, `away_floor_drop_c` at two
solve sites). Keep step selection and the `WhyNow` dict build in slot_drivers.py as one module
function (it also absorbs the `_step_index` move of §3), so the coordinator adds one call per site;
name the coordinator payment in the body before pushing.
Carry: R10-WHY-NOW-WIDGET (item r1-c). The null control's "flat weather" also holds hlf and solar flat
over the 8 h lookahead, or the forecast term is not zero.
Carry: R10-WHY-NOW-WIDGET (item r2-a). The card footprint is `score_open` only (§6); a card.mjs or
card_rig.mjs edit that widens it is a design change, not a claim to add.
