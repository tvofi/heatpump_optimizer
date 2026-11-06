# Design note: R10-WHY-NOW-WIDGET (architect note, extended)

Base: `b88684a218923f85de66f1e8fb1833e31a76a154` (origin/main). Round 3: revalidation (designer.md step 9).
Rounds 1–2 read `c3a279e3`; since then the predecessor R10-GRADE-DRIVERS merged (PR 3198, merge
`0a7c84fa2`) and R10-SAV-COMFORT added a per-step schedule read through the current action. Two
things the round-2 note relied on moved: the current-step owner (§1, §3 "Selection") and the card
helper it said to reuse (§3 "Card"). Every citation below is re-measured at this base. Round 1's
revise point (card footprint) stays answered in §6. No finder harness: owner report (tvofi
2026-11-01, rulings card 2 option (c) part (b), on R10-UX-HEALTH carry 14).

## 1. Measured at the base
- The solver publishes one string code per step: `space_reasons`, from `classify_space_steps`
  (custom_components/heatpump_optimizer/optimizer.py:1608, set in `_build_result` :3014). It is a
  ranked post-hoc label with no direction and no weight.
- **The step covering now has one owner: `HeatPumpOptimizer.get_current_action` (optimizer.py:5801).**
  Its comments say it "already owns the one search for the step covering now" and that a second copy
  is "a second chance to disagree". It already carries per-step solver outputs: `space_reason`, and
  since R10-SAV-COMFORT `_settlement_at(result, i)` (:522) over `OptimizationResult.settlement_schedule`.
  The coordinator calls it once per cycle (coordinator.py:6288) and hands the action as a value to the
  module-level `_apply_result_payload(data, result, current_action, plan_views)` (coordinator.py:2848).
  `pump_arbiter._step_index` (:379) is a private second search; the round-2 note wrongly built on it.
- Mold guard: `SolveLimits.min_temp_floors` (optimizer.py:2319), from the coordinator's
  `_mold_floor_series` (coordinator.py:9022), merged into `temp_min_bounds` in `_build_comfort_bounds`
  (optimizer.py:3964); `_Horizon` (:2186) keeps no separate mold floor.
- Away is not a solver input: the coordinator lowers the comfort numbers before the solve
  (`solve_bands`, custom_components/heatpump_optimizer/away.py:363; `_fold_away`, coordinator.py:2271).
  Holiday days reach the solver as `holiday_flags` and `get_temp_bounds` (optimizer.py:2140).
- The card (custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js) has no live widget.
  R10-GRADE-DRIVERS left three score helpers: `scoreDrivers` (:8940, `score.driver_<code>` labels,
  whole points, a per-part "typical" fallback), `scoreBreakdownHtml` (:8979, the `sb-row` markup, now
  with a `title` hover) and `scoreRowTitle`/`scoreLine` (:9002, :9007).

## 2. Owning seam
**The solver seam owns this change.** A new pure module `slot_drivers.py` (new file, beside plan_slots.py,
numpy only) computes the drivers; `_build_result` calls it once, and `get_current_action` reads step
i's entry. The coordinator only passes the away drop in and copies one key out ("views" in
tests/seam_map.json owns `_build_data_dict`); the card only renders. Away is the one coordinator fact;
it enters as a solver input, as the mold floor does. One owner per concern, no split.

## 3. Shape
**Solver input.** `SolveLimits.away_floor_drop_c: float | None`: configured floor minus the floor
solved against, at least 0; None when away is inactive or recovering; from `_fold_away`'s arithmetic.
**Horizon.** Two optional `_Horizon` fields captured in `_build_comfort_bounds`: `mold_floors` (padded
`min_temp_floors`) and `comfort_floors` (the floor before mold). `temp_min_bounds` is unchanged.

**Result.** `OptimizationResult.space_drivers: dict[str, list[float]]`, code → one signed weight per
step; plain lists, pickle-safe. Codes: `price_rank`, `comfort_floor`, `mold_guard`, `away`, `forecast`.

**Push** (unchanged from round 2). Raw p in [-1, 1] from the solve's own inputs at step i, positive =
run; B = max((ceiling − comfort_floor)/2, 0.5); L = 8 h (`_anticipatory_weights`, optimizer.py:2588).
price_rank 1 − 2r (r the rank of prices[i] in the horizon, ties 0.5); comfort_floor
clip((mid − room_i)/B, −1, 1); mold_guard clip((mold_floor_i − comfort_floor_i)/B, 0, 1); away
−clip(drop_i/B, 0, 1) (holiday: configured minus holiday floor); forecast clip((out_i − mean
out[i:i+L])/10 + (mean hlf[i:i+L] − hlf_i) − (mean solar[i:i+L] − solar_i)/max(p_max, 1), −1, 1).
**Weight.** w_k = 100·p_k/Σ|p_j|, rounded to 0.1; all 0 when Σ|p_j| = 0; |w| < 0.5 is neutral, the
sign otherwise gives the direction. Signed percents of one push, not `envelope_drivers`' points.

**Selection (revised).** `slot_drivers.why_now_at(result, i) -> WhyNow | None` builds
`{"t": iso, "drivers": [{"code", "direction": "run"|"idle"|"neutral", "weight"}]}` sorted by |weight|
descending, None when `space_drivers` is empty, i is past it, or the step's price is unknown.
`get_current_action` sets `action["why_now"]` from it at the i it already found, beside
`_settlement_at`. `_apply_result_payload` adds top-level `why_now` only when the action carries one,
so the key is absent otherwise (the card's "no data"). New TypedDict `WhyNow` in payload.py; the
optional key on `CurrentAction` (payload.py:154) and on the payload. No current-step search is added,
`_step_index` stays private, and `HeatPumpOptimizerCoordinator` gains no method body.

**Carrier.** The space-plan sensor's attribute block (`_PlanSensorBase.extra_state_attributes`,
sensor.py:1441, read by `SpaceHeatingPlanSensor` :1593) adds `why_now` from `data.get("why_now")`;
the card reads it from the space-plan entity it already resolves, and from nothing else.

**Card (revised).** A "Why now" block rendered from `why_now` alone: one row per driver, ↑/↓/· and the
signed percent; one all-neutral line when every weight is 0; the no-data text when the key is absent.
The block and each row carry the brief's metric explanation as `title`, en and sv, verbatim. Reuse is
of the **row markup**, not of `scoreDrivers`: extract `scoreBreakdownHtml`'s `sb-row` template into one
`breakdownRow({key, label, valueText, barPct, sub, title})` both blocks call. `scoreDrivers` stays the
score's: its label namespace, whole-point rounding and "typical" fallback have no why-now meaning.
Mount: inside `headlineHtml`'s `<div class="headline">` after the `hl-narrative` list (heatpump-optimizer-card.js:9146);
one call site (:14697). It inherits the headline's gates (`show_stats` :9063, and no stat and no
narrative line returns "" :9126): no headline, no block.

```
solve inputs ─► _build_comfort_bounds ─► _Horizon(+mold_floors, comfort_floors)
coordinator ─► SolveLimits.away_floor_drop_c ─┘        │
                        _build_result ─► slot_drivers.space_drivers(h, room) ─► result.space_drivers
coordinator ─► get_current_action(result, now) ─► i ─► why_now_at(result, i) ─► action["why_now"]
            ─► _apply_result_payload ─► data["why_now"] ─► space-plan attr ─► card whyNowHtml
```
**Invariants.** (1) The plan is byte-identical: drivers are read after the solve, never written back.
(2) No optimality figure moves. (3) The card derives nothing. (4) The widget explains the step the
action being applied came from: one search, one i.

## 4. Alternatives, and why each lost
- **Round 2's selection: `_build_plan_views` picks the step via a public `_step_index`.** A second
  current-step search beside `get_current_action`'s, which that method's comments name as the defect
  to avoid; it also grows `HeatPumpOptimizerCoordinator`, which sets the class-size ratchet.
- **Drivers derived in the coordinator from payload arrays.** The floors exist only in `_Horizon`; a
  second copy of `_build_comfort_bounds` in the largest class.
- **Re-solve with each input neutralised.** Five extra L-BFGS-B solves per cycle on a Pi-class target
  (D9); penalty-based solves have no dual to read.
- **Weights inside `classify_space_steps`' strings.** Changes a published per-step string that
  plan_slots, goldens and the mutation ledger pin, for another contract.
- **Reuse `scoreDrivers` with a field mapping** (round-2 carry r1-a). It filters codes against
  `score.driver_*`, rounds to points and falls back to a per-part "typical" line; a mapping would
  pass percent through a points path. Sharing the row markup removes the duplicate without that.

## 5. Sibling sites
`grep -rn "space_reasons\|classify_space_steps" custom_components/ tests/*.py`: consumers unchanged.
`grep -n "min_temp_floors=" custom_components/heatpump_optimizer/coordinator.py`: two solve sites,
the plan (:6153) and the what-if (:11185); the plan passes `away_floor_drop_c`, the what-if passes
None and says why in the body. `grep -n "_settlement_at\|space_reason\"" custom_components/heatpump_optimizer/optimizer.py`:
the per-step readers in `get_current_action`; `why_now` joins them, nothing else reads a step. DHW out
of scope: the five reasons are space-heating reasons and the brief names no DHW driver.

## 6. Evidence plan
- **Failing tests.** tests/features.py: a solve where step 0 is cheapest, room mid-band, flat weather,
  no mold floor, no away; `space_drivers` ranks `price_rank` first and positive, and
  `get_current_action(result, start)["why_now"]` lists it first. Fails at the base (AttributeError,
  KeyError). tests/card.mjs: rows with marks and weights from a fed `why_now`; no-data when absent.
- **Null control.** Flat prices, mid-band, hlf and solar flat over L: all weights 0, all-neutral line.
  `power_schedule` equal with `space_drivers` patched to {}. `python3 tests/optimality.py` before and
  after, identical figure.
- **Perturbation.** `away_floor_drop_c` = 3: `away` negative, price_rank's share changes. A mold floor
  above the comfort floor: `mold_guard` 0 → positive.
- **Goldens, solver.** tests/golden/coord_*.json capture the data dict at START, so they gain
  `why_now`: claim in tests/golden/claimed_drift.txt, direction "key added".
- **Goldens, card.** Re-measured at this base with a throwaway spike (a no-data `div` after the
  narrative list, scratch worktree, never pushed): `node tests/card_drift.mjs` renders 45 states,
  `score_open` DRIFT, 44 identical. The claim is one line in tests/golden/card_claimed_drift.txt
  (empty after the v7.1.3 stamp): `score_open`, "Why now block added, showing the no-data line".
  `planStates` (tests/card_rig.mjs:161) stays without `why_now`; any other moved state is a stop.
- **docs/img.** docs/img/card/make_card_figures.mjs draws from `planStates(plan)` with no stat
  sensor, so no headline: regenerate both figures at base and head, byte-identical, or commit them.
- **Mutation proof.** The sign and normalisation lines in slot_drivers.py; the None branch of
  `why_now_at`; the presence test in `_apply_result_payload`.
- **Browser.** tests/card_browser.mjs screenshots, light and dark, phone and desktop, after the P9
  clip-check fix below so a clipped why-now row cannot pass.

## 7. Hot files and serial position
Hot: www/heatpump-optimizer-card.js, coordinator.py, optimizer.py, payload.py, sensor.py,
translations en.json and sv.json, tests/card_browser.mjs. Predecessor R10-GRADE-DRIVERS is merged;
nothing in its diff remains to wait on. `slot_drivers.py` goes into a measured closure or `INERT`.
Received: R10-ADVISOR-WHATIF also holds the card and coordinator.py hot, including the what-if solve
(:11185) — `decision: orchestrator` on the serial order, routed in round 1, not this note's call.
Received: the P9 clip-check defect (PR 3198 item 7c609975), taken in full below.

## Notes for the fixer
Carry: R10-WHY-NOW-WIDGET (item 0) is owned here in full; nothing in it is scoped out.
Carry: R10-WHY-NOW-WIDGET (item 7c609975). `unreachable()` in tests/card_browser.mjs (:835) starts its
walk at `parentOf(run.el)` (:838), so a run clipped by its own box passes. Start the walk at `run.el`;
perturbation: a why-now row given `overflow:hidden` and a width narrower than its text is reported;
control: the base card's P9 overflow list before and after, each newly reported run named in the body.
Carry: R10-WHY-NOW-WIDGET (item r1-a). Weights are signed percents, |w| summing to 100, not points.
Its reuse half is superseded by r3-a.
Carry: R10-WHY-NOW-WIDGET (item r1-b). Superseded by r3-b: the coordinator now adds a kwarg at two
solve sites and one key copy in a module function; name that as its whole growth in the body.
Carry: R10-WHY-NOW-WIDGET (item r1-c). Flat weather in the null control holds hlf and solar flat over L.
Carry: R10-WHY-NOW-WIDGET (item r2-a). The card footprint is `score_open` only; widening it is a
design change, not a claim to add.
Carry: R10-WHY-NOW-WIDGET (item r3-a). Share `scoreBreakdownHtml`'s row markup through one row
helper; do not route percents through `scoreDrivers` (§4).
Carry: R10-WHY-NOW-WIDGET (item r3-b). Select the step only in `get_current_action`; do not make
`_step_index` public or search timestamps anywhere new.
- Keep `_build_result`'s addition to one call; pay any class growth by moving code into slot_drivers.py.
- Re-measure the forecast scale (/10 °C) against one winter golden; record the chosen scale if one
  driver saturates on most steps.
