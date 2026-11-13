# R10-COP-LEARNER-DRAW-FLOOR: the COP learner's floor and ask-following judgement (architect note)

Base and code read: `e23124ff6e45bac1d48b4a775dad555a37965355` (origin/main; no predecessor, After: none). Brief: `PROMPT.md` at dispatch commit 3fe62ad4. Size L, design first (0014). No finder harness for carries 0 and 1: the instrument is the #2066 fixer's `dev/audit/harnesses/cop_duty_floor.py`, named by `dev/programme/carries/carry-2065.json` as the control. "Design note S4" that carry cites is in no tree or design ref (`git grep -i "observed running draw"`); the observed running draw it means is `DrawRange.observed` in `custom_components/heatpump_optimizer/draw_range.py`.

## Owning seam

One judgement seam, one owner: `MeasuredCop` in `custom_components/heatpump_optimizer/accuracy.py` (`judge_floor`, `judge_ratio`). `draw_range.py` supplies evidence readers to it, as `follows_ask` does today; `thermal_model.py` supplies configured figures (`flow_lift_power_floor_kw`, `nameplate_power_floor_kw`, `on_threshold_kw`) and does not change. `coordinator.py` (`_fold_measured_cop` seam "learning", `coordinator._fold_flow_lift` seam "core" in `tests/seam_map.json`) only calls. `thermal_model.py` cannot own the cap: `draw_range.py` imports it, not the reverse.

## Shape

**Carry 0, the capped floor.** A new module function in `draw_range.py`, beside `follows_ask`, taking the draw window and the live parameters and returning kW:

    floor = params.flow_lift_power_floor_kw
    seen = draw.observed()            # None below MIN_SAMPLES, or draw is None
    if seen is not None: floor = max(on_threshold_kw(params), min(floor, seen[0]))

It is the only reader of `flow_lift_power_floor_kw` outside `thermal_model.py`. `MeasuredCop.judge_floor` gains the draw window as an argument and reads the function; `coordinator._fold_flow_lift` and `accuracy.diagnostics_view` (`power_floor_kw`) read the same function. The cap is the low end itself, not 0.8 x it: `observed` already returns a 10th percentile above the idle margin, and `_metered_range` books that same figure as the plan's minimum.
Invariants, each a test: (a) the cap only lowers: result <= `flow_lift_power_floor_kw` always; (b) never below `on_threshold_kw`; (c) no evidence, no change (zero-evidence end bit-identical to base); (d) the evidence is not censored by the floor it caps: `draw_range.fold` admits on `is_running_space`, which reads no duty floor; (e) a changed configured range clears the window (`DrawRange.observe`), so the floor reverts with it.
Measured limit, stated before building: `on_threshold_kw` is 0.5 x the configured minimum, so the cap moves the floor from 0.8 x to at most 0.5 x an overstated minimum. On the harness's 3.0 kW install it is 1.5 kW (`RESULT on_threshold_kw` scales with the minimum): draws of 1.0 and 1.2 kW stay refused, which the carry's remeasure clause admits when named.

**Carry 1, hold-then-replay.** `follows_ask` returns None for two different states; the judgement needs them apart. A second reader in `draw_range.py`, sharing `follows_ask`'s pair extraction, says whether evidence is still *pending* (fewer than `MIN_SAMPLES` qualifying pairs) as against *unobtainable from this window* (enough pairs, asks never span `FOLLOW_ASK_SPAN`).
`MeasuredCop.judge_ratio`, unchanged order, one branch changed: a departure beyond `COP_ASK_TOLERANCE` with evidence pending returns a new `COP_REFUSED_*` code (held); with evidence unobtainable, base's rule stands as today (`nameplate_power_floor_kw`, else `COP_REFUSED_NO_EVIDENCE`), so a flat-ask install keeps base's reach and cannot deadlock a real efficiency shift.
`MeasuredCop` owns the held intervals: a bounded deque (`draw_range.WINDOW` rows), each row what `_fold_cop_evidence` consumed plus the scale it was read against: commanded kW, metered kW, the reference tuple from `_cop_reference_curve`, `_cop_scale` at hold time, the instant. Not persisted (`as_dict` unchanged, no `store.py` schema row): a restart drops them, which is a refusal, never a wrong fold.
A release method on `MeasuredCop`, called by `_fold_measured_cop` once per interval after `judge_ratio`, is the only place a held interval is judged: `follows_ask` True returns all rows oldest first and clears; False clears and returns none; unobtainable returns the rows base's rule folds and clears; pending returns none. The coordinator folds each returned row through `_fold_cop_evidence` with the row's stored scale as `cop_evidence`'s scale argument.

    _fold_measured_cop -> MeasuredCop.judge_ratio -> held code -> MeasuredCop holds the row
    _fold_measured_cop -> MeasuredCop release (reads draw_range) -> rows -> _fold_cop_evidence each

Fix 3's "extra draw is not low COP" refusal is not built here (no finding in this brief states its predicate); when built it is one more code returned by `judge_ratio`.

**Carry 2, measurement, no build in this group.** Re-run at the base: `python3 dev/audit/harnesses/r10_cop_gate_band.py` prints `fit=none` for both files under `tests/replay/` (`steps=1 distinct_c=1`; `steps=0`); its control `--synthetic` prints `gain_kw_per_k=0.1 max_resid_kw=0.0`. Missing: at least 3 distinct written flow set-points strictly between gate and ceiling, each held in heat mode with a power reading inside the interval (`fit` refuses fewer). Owner data that closes it: a diagnostics download with the week of debug data on, from a set-point install whose pump ran across the band. Decision rule, fixed now: on that bundle, `max_resid_kw` above `draw_range.AGREE_TOLERANCE` x the fitted draw at the ceiling is non-linear and goes to a new design; at or below it, a recorded refusal with the number. Flat-price null: a flat-price bundle must print `fit=none` (one set-point); a fit from one means the reader counts noise as steps.

## Alternatives, and why each lost

- Cap inside `ThermalParameters.flow_lift_power_floor_kw`: needs the draw window in `thermal_model.py`, an import cycle with `draw_range.py`, and learned state on a configuration dataclass.
- Cap as a local statistic in `_fold_measured_cop`: #2066 refused it; `_fold_flow_lift` and the diagnostics would read a different floor, three sites for one figure.
- Refuse without replay (hold = drop): a heat-led install's first `MIN_SAMPLES` departures are lost and the `true_<s>` rows converge later; and with no pending/unobtainable split a flat-ask install never folds a departure again.
- Persist the held rows: a `store.py` schema entry and `from_dict` validation for rows whose loss costs one pending period of departures.
- Hold state on the coordinator: `class_excess_loc` and `coordinator_attrs` have no headroom, and the judgement would have a second home.

## Sibling sites

`git grep -n -e flow_lift_power_floor_kw -e nameplate_power_floor_kw -e judge_floor -e judge_ratio -e "follows_ask(" -- custom_components`. Covered: `judge_floor` and its two callers in `coordinator.py` (the cycle, and the heat-counter span close, which must pass the window too), `_fold_flow_lift`, `accuracy.diagnostics_view`, `judge_ratio`. Out of scope: the optimizer's `duty_floor_kw` (`optimizer.py`, `pump_arbiter.py`), a different quantity per `diagnostics_view`'s docstring; `draw_range.planned_range`, the plan's clamp, which already reads `observed`.

## Evidence plan

- Failing tests first, `tests/features.py`, importing the production symbols: invariants (a)-(e) on the floor function; `judge_ratio` returning the held code only when pending; release's four verdicts; replay folding against the stored scale.
- Harness, both ends, `dev/audit/harnesses/cop_duty_floor.py` at base and head. The `min3_*` rows feed 15 intervals, under `MIN_SAMPLES`, so they cannot show the cap: add a warmed variant (window filled first). Move: warmed `min3_running_folded` up to every draw at or above 1.5 kW. Null: warmed `min3_idle_folded`, `min3_standby_folded`, `min3_duty_cycled_folded` stay 0; `min1_*` unchanged, warmed or not.
- Carry 1 move: `selfmod_independent`, `selfmod_independent_4kw`, `selfset_hourly` to 0 folded and scale 1.000 (base: 5/96 0.987, 29/96 0.789, 5/96 0.985). Null: `selfmod_matched`, every `true_<s>` row's scale (zero-evidence end, departures held then replayed), `true_0.7_4kw`, `p4_follow_*`, `true_0.7_reload150`; the self-setting flat-ask row stays 1.000 (unobtainable branch).
- Goldens: run `GOLDEN_MODE=drift` at the merge base; a moved value-bearing fixture is claimed in `tests/golden/claimed_drift.txt` with its direction.
- Mutation targets: the `min` and the `max` of the floor function; the pending test in `judge_ratio`; release's False branch (drop) and its stored-scale argument.

## Hot files, position, carries

Hot: `coordinator.py` (roster overlap admitted by the owner 2026-11-13). Serial position: none (After: none); rebase after any overlapping merge and re-run the harness. No new pinned-grader registration is known, so no p1/p2 split; the fixer confirms with `git grep -n awaiting_draw_evidence` for registries of refusal codes. Receives carries 84e73ec4, 35931f4b and the R10-COP-GATE-E band carry; never holds the v10.0.0 stamp.

## Notes for the fixer

- `tests/structure.py`: `class_excess_loc` and `coordinator_attrs` sit at budget. Candidate payment that improves the seam: move the walking ratio (`_cop_ratio_ewma`, read only in `_fold_measured_cop`) into `MeasuredCop` beside the judgement that reads it; measure with `tools/audit/archscore/` before and after. Carry: R10-COP-LEARNER-DRAW-FLOOR (item n1)
- A replay folds many rows in one cycle, each clamped by `COP_LEARNING_MAX_STEP`; report the largest one-cycle scale move the `true_0.6` row shows. Carry: R10-COP-LEARNER-DRAW-FLOOR (item n2)
- Update `judge_ratio`'s and `diagnostics_view`'s docstrings and the `COP_REFUSED_*` comment block in the same change; `tests/features.py` pins `power_floor_kw == 2.4` on an install with no window, which invariant (c) keeps. Carry: R10-COP-LEARNER-DRAW-FLOOR (item n3)
- `DrawRange.commands` stores the written set-point and ceiling beside each drawn sample; if a diagnostics download publishes those rows, the band fit can run on them without the debug week. Check before asking the owner for data. Carry: R11-INTAKE-R10-RESIDUE (item n4)
- The band measurement itself stays open on the named owner data. Carry: R11-INTAKE-R10-RESIDUE (item n5)
