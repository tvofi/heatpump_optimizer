# Design note: R10-WHY-NOW-WIDGET (architect note, extended)

Base: `c3a279e3252a8b57bb00b5a677318cd4fe20387f` (origin/main). The predecessor R10-GRADE-DRIVERS
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
direction is the sign of w, and |w| < 0.5 counts as neutral. So |w| sums to 100 ± rounding, the same
"shares of one push" contract as `envelope_drivers`.

**Payload.** Add a top-level key `why_now`, of a new `WhyNow` TypedDict in payload.py:
`{"t": iso, "drivers": [{"code", "direction": "run"|"idle"|"neutral", "weight"}]}`, sorted by |weight|
in descending order. The key is absent when there is no result, when now falls outside the plan, or
when `price_known` is False at the step, which the card text calls "no data". Make `_step_index`
public, or move it into slot_drivers.py: coordinator_private_reach refuses a new reach.

**Card.** A "Why now" block renders from `why_now` alone: one row per driver with ↑/↓/· and the signed
percent. When every weight is 0 it shows one all-neutral line. When the key is absent it shows the
no-data text. The hover on the block and on each row carries the brief's metric explanation, in en
and sv, verbatim.

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
- **Goldens.** The tests/golden/coord_*.json captures gain `why_now`, and those floats come from the
  trajectories. Claim them in tests/golden/claimed_drift.txt with the direction "key added".
- **Mutation proof.** Target the sign and normalisation lines in slot_drivers.py, and the absent-key
  branch in `_build_plan_views`.
- **Browser.** Screenshots from tests/card_browser.mjs: light and dark, phone and desktop.

## 7. Hot files and serial position
The hot files are www/heatpump-optimizer-card.js, coordinator.py, payload.py, and translations
en.json and sv.json. This group runs after R10-GRADE-DRIVERS. Before the fixer dispatches, the
designer re-reads that group's merged diff. Its driver row and hover helper must be reused here, not
duplicated: duplication_copies is ratcheted. The new module goes on the INERT list or into a closure.

## Notes for the fixer
Carry: R10-WHY-NOW-WIDGET (item 0) is owned here in full. Nothing in it is scoped out.
- `_build_result` sits inside the HeatPumpOptimizer class. Keep the addition to one call, and pay
  any class_excess_loc growth by moving the space_reasons assembly into slot_drivers.py with it.
- Re-measure the forecast scale (/10 °C) against one real winter golden. If one driver saturates
  at ±1 on most steps, record the scale you choose and why in the body.
