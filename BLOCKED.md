# BLOCKED: r11-outside-self-setting-pump-p2 (carries 5, 6, 7)

Fixer seat, worktree cut from origin/main 3f7f29e778e009f12a2008318b1f879f531ef3a1 (the merge base; #3662's merge). No production line changed.

Question: carries 5 and 6 can each be fixed only by departing from a rule the approved note (`design.md` at design/R11-OUTSIDE-SELF-SETTING-PUMP, owner decisions 2026-11-16) states. The brief says a departure is raised, not made. Does the owner (or a design seat) approve departure A for carry 5, and which of B1/B2 for carry 6? Carry 7 waits on the answer, because its full-cycle measurement is taken at the head the answers produce.

## Reproduction at the merge base

`PYTHONPATH=tests/hastub:custom_components:tests python3 dev/audit/harnesses/cop_duty_floor.py` at 3f7f29e778 (106 RESULT lines, 25 s):

- `sub_min_true_0.6_x288=0/288_scale=1.000`, `_x384=0/384`, `_x480=0/480`, `_x1440=0/1440_scale=1.000` (carry 5 reproduces: nothing folds at any length).
- `repriced_heat1.2_true_0.8_x672=0/672_scale=0.933 lowest=0.933 highest=1.072 off5=140 probes=56 band=0.500 verdict=pending` (carry 6 reproduces).
- Control: `heatled_true_0.8_flat_x672=672/672_scale=0.800 ... probes=1 band=0.500 verdict=follows`.
- Null control 1: `null_dither0_heatled_true_0.8=0/672_scale=1.000 ... verdict=pending`, `null_dither0_selfset_2.2=0/672 ... verdict=pending`.

## Carry 5: why every fix is a departure

In `sub_min` one cycle in three is admitted (asks 1.9/2.2 kW sit under the duty floor, 2.55 kW clears it), so no two admitted rows are consecutive. `ScaleDither.step(base, live=False)` voids the pair in flight and returns `base`. That is the note's rule "a refused or frozen cycle between them voids the pair instead of stretching it", and design-verdict item 76b936b7 as #3662 pinned it ("from the second [cycle with no row] on the scale is at the base, for any length of idle"; checks "mid-probe, a pump that goes off"). A pair needs two admitted rows. Here none are consecutive, so any rule that ever completes a pair must stretch it across a cycle with no row. That contradicts both texts. Re-timing the coin cannot help: starting a fresh pair after a void still never completes one.

Departure A (proposed): on a cycle that was read but admitted no row (duty floor, tracking, not judged on the heat ask), the pair in flight is kept and the scale stays at its level until an admitted row is read under it. The pair is void past `COP_HOLD_HORIZON_S` from its first row, and the scale returns to `base`. A frozen or unread cycle still voids, as now (carry 1's freeze gate unchanged). Cost: during an idle stretch the scale can sit at a dither level (inside the ±7.2 % band of owner decision 1) for up to the horizon, not one cycle, and the probe's duration grows with the admitted rows' spacing. The coin stays independent of the draw. Admission that depends on the draw biases a pair's contrast as it already does for consecutive rows, so the stretch adds no bias the current rule lacks. The check pinning 76b936b7 changes. Not built, so no figures yet: A gets the harness at both ends, the null control and the gap checks once approved.

## Carry 6: identification under a re-pricing plan

Under a plan that re-prices (asked = heat / scale), the heat ask `asked_kw × cop_scale` is invariant to the scale. The scale dither then cannot move it, which is why every pair is void (#3662 item 1b98ae3f). Draw = heat / true is flat. A self-setting pump at a constant draw produces the same rows, and a fold walks it to heat / draw, the D4 defect. So no estimator on the scale dither separates the two pumps here: the base's 377/672 to 0.800 is the same rule that walks a self-setting pump. Identification needs the heat ask itself moved, which is the note's option (c1). The note rejected it as L, two owners (planner and learner), a stop under the designer contract.

The non-identifying part, 56 probes without end, has two candidate fixes, each a departure:

- B1: a cap across resets. After N probes that end in a reset with no completed pair, stay pending and hold until `COP_HOLD_HORIZON_S` (owner decision 3's park, extended to resets). The install then learns nothing, as now, but stops dithering.
- B2: route carry 6 to a design seat for (c1), the closed-loop harness and the planner-side dither, as the note's follow-up describes.

Which is wanted, or both (B1 now, B2 as its own group)?

## Carry 7

Not started. It is a measurement of `thermal_model.simulate_step` replays (`_async_learn_house_heat_loss`, `_async_learn_lower_floor_loss`, the path from them to `simulate_step` not yet read) under the dither against null control 1. Its subject is the dither, so its numbers depend on the answers above. If the dither changes, the measurement is taken at that head.
