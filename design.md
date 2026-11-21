# R11-OUTSIDE-ROOMS-3B: the room lift named on the solve's record, in the why-now row and in the narrative

Base: origin/main e698fc8ac374a1d72c230b55d938d75b03b7de67. Predecessor R11-OUTSIDE-ROOMS-P3 merged as #3711 (b486fe58fd) and has no open handoff head, so code was read at the base only and every line below is at the base. Extends the approved P2 note (design/R11-OUTSIDE-ROOMS-P2 4784b5940e, its carry 5a1c0e06) and leaves the P3 note (design/R11-OUTSIDE-ROOMS-P3 e36406c0f4) unchanged. Paths are under `custom_components/heatpump_optimizer/` unless they start with `tests/` or `docs/`. Names without backticks do not exist yet.

## Finding

No finder harness: owner report (#3616). The carries are P2 body item e98789a8 and P3 body item e82913fe. The lift reaches the solve folded into `min_temp_margins`, at `coordinator.py:6306` "rooms.lifted(rooms.hold(" and `coordinator.py:11328` "the baseline's lift". `_build_comfort_bounds` adds it at `optimizer.py:4877-4880` "comfort_floors = temp_min_bounds". From that point the solve cannot tell a room's share from the confidence margin. Two consequences follow. `classify_space_steps` labels a step the lift alone holds as `comfort_floor` (`optimizer.py:2364-2366` "room <= temp_min_bounds[i] + 0.15"). The narrative sums those labels (`coordinator.py:10586` `narrative.build`), and `space_drivers` puts the lift inside the comfort push (`slot_drivers.py:104-108` "h.comfort_floors if h.comfort_floors is not None").

Measured on the production solver with the spike below. On a cold day the floor holds 44 steps and 57.8 kWh with a 0.5 K lift. Of those, 12 steps and 10.9 kWh sit above the floor the same solve would have without the lift. Without the lift the floor holds 31 steps and 36.0 kWh. Today that 10.9 kWh is published as "holding the minimum temperature".

## Owning seam

**`optimizer.py` owns the attribution.** It records on `_Horizon` which part of the floor the solve held is the rooms' part, and it classifies steps from that. This is the precedent the away setback set (R10-WHY-NOW-WIDGET): one figure on `SolveLimits` (`optimizer.py:3117-3120` "Read by the why-now drivers"), turned per step into `_Horizon.away_floor_drops` (`optimizer.py:4529`, `optimizer.py:3054-3057`).

**`rooms.py` keeps the lift** and adds one function that returns the lift's per-step part beside the summed margins. The lift is computed once, in `lifted`, `rooms.py:280`.

**Readers only:**
- `slot_drivers.py` adds one row.
- `narrative.py`, `payload.py`, `icons.json`, `strings.json` and the three translations register one reason code.
- `www/heatpump-optimizer-card.js` registers one label and one driver.
- `coordinator.py` changes the argument form at two existing lines and adds none.

There is one owner per concern, so nothing here stops the design.

## Shape

```
coordinator (both SolveLimits builds) --**rooms floor limits(held, base, config, start, n)-->
    {min_temp_margins: base + lift | base,  room_lifts: lift | None}     (one computation)
optimizer._build_comfort_bounds: bounds with margins, and bounds with margins - room_lifts
    -> _Horizon.room_lifts = temp_min_bounds - unlifted bounds  (>= 0; None when input None)
    -> classify_space_steps(room_lifts=): floor step held only by the lift -> room_floor
    -> slot_drivers.space_drivers: comfort push against floor - room_lifts; room_lift row
narrative.build (unchanged arithmetic) groups room_floor; render: one sentence, 3 languages
```

**Interfaces.**

1. **`SolveLimits` gains a room-lifts field**, a per-step array or None, beside `away_floor_drop_c`. Its comment says what that one says: the lift is already in `min_temp_margins`, and this field is read for attribution only.
2. **`_Horizon` gains a room-lifts field beside `comfort_floors`.** It is the floor the solve held less the floor the same build would have held without the lift. It is computed in `_build_comfort_bounds` by the same margin, mold-maximum and ceiling-clip arithmetic run on `min_temp_margins` less room-lifts. So it is non-negative. It is 0 wherever the mold floor or the ceiling clip covers the lift, and equal to the input lift elsewhere. It is None exactly when the input is None.
3. **`rooms` gains a function** returning the two `SolveLimits` keyword arguments as one mapping, splatted at both builds. Today's `lifted` becomes the margins half of it, so both values come from one computation and the what-if reads the held lift, as P2 carry r4 pins.
4. **`classify_space_steps` gains a keyword room_lifts.** A heating step that meets the comfort-floor test against `temp_min_bounds` but not against temp_min_bounds less room_lifts is room_floor; every other step keeps its label. The step is ranked where `comfort_floor` is.
5. **payload gains REASON_ROOM_FLOOR, the string room_floor.** It is not idle and not in `_MANUAL_KEEP_REASONS`. The `manual_pin` gate (`rooms.py:194`) gives no lift while a space pin exists, so the pair cannot occur, and a test pins that.
6. **`slot_drivers.DRIVER_CODES` gains room_lift after `comfort_floor`.** The room-lift push is room_lifts over half, clipped to [0, 1]. The comfort push is computed against comfort_floors less room_lifts, and `half` is unchanged. The code is present in the drivers dict only when h.room_lifts is not None; `why_now_at` already skips absent codes (`slot_drivers.py:164` "if code in drivers").
7. **Naming the room.** The narrative sentence and the driver name the room lift as a cause, not the room. The entity is already published as `rooms.lift.entity` (`rooms.py:138` `_lift`), and a template placeholder for it would break the four-placeholder parity at `tests/features.py:25864-25879`.

**Invariants.**
- (i) **No room list, the flag off, or any gate firing:** `rooms.lifted` already returns `base`, so room-lifts is None. Every reason, every driver row (five codes, same weights) and every narrative line is then byte-identical. This is the null control.
- (ii) **Where neither the mold floor nor the ceiling clip binds,** comfort push plus room-lift push equals today's comfort push before its clip. The split moves weight between two rows and changes no total.
- (iii) **The plan is untouched:** no variable, constraint or objective term changes, and `temp_min_bounds` is the same array as today.
- (iv) **A room_floor step is a step that is `comfort_floor` today,** so `comfort_floor` energy plus room_floor energy equals today's `comfort_floor` energy.

**What moves for every install.** `plan_narrative`'s enum options (`sensor.py:2778`, `sorted(narrative.TEMPLATES["en"])`) gain room_floor whether or not a room list exists. That is the sensor's options list only, not a state.

## Cost on the production solver (spike, design seat, not in the tree)

**Setup.**
- Instrument: `HeatPumpOptimizer.optimize` through `tests/profiles.py` `solve_inputs`, with `tests/hastub` on the path.
- Horizon: 24 h at 15 min, `prices("winter_typical")`.
- Comfort settings: floor 19.5, target 20.0, ceiling 23.0, room 19.6, slab 20.6.
- Lift: `rooms.lifted(HeldLift(0.5, "climate.a", None, 0.1), None, config, start, 96)`.
- Single-threaded BLAS in the seat's Linux container.

"Lift-only" counts the `comfort_floor` steps whose next temperature sits above the floor less the lift plus 0.15, which is the rule in interface 4.

| set | solve ms | power sha1 | floor steps / kWh | lift-only steps / kWh |
|---|---|---|---|---|
| shoulder 12:00, None | 373 | b3e5cbaeaa | 0 / 0.00 | 0 / 0.00 |
| shoulder 12:00, zeros | 331 | b3e5cbaeaa | 0 / 0.00 | 0 / 0.00 |
| shoulder 12:00, 0.5 K ramped | 1090 | 5186f26bb7 | 14 / 9.90 | 1 / 0.07 |
| winter_cold 00:00, None | 1295 | fd7c7254d3 | 31 / 36.02 | 0 / 0.00 |
| winter_cold 00:00, zeros | 1430 | fd7c7254d3 | 31 / 36.02 | 0 / 0.00 |
| winter_cold 00:00, 0.5 K ramped | 984 | 6c22087847 | 44 / 57.82 | 12 / 10.92 |
| two-zone shoulder, 0.5 K (no lift is given there; P2 gate) | 3246 | d7a1807fcc | 9 / 1.16 | 9 / 1.16 |

**Added work per result.** The design adds no solve. It adds one extra pass of the bound arithmetic in `_build_comfort_bounds`, one comparison per heating step and one extra driver row. Timed together on 96 steps, the extra row and comparison take 6 to 8 µs; the solve takes 0.3 to 3.2 s. `tests/stress_budgets.json` is not raised, and the fixer re-measures with `tests/stress.py`.

**What the table shows.**
- The zeros row equals the None row by sha1 in both sets. That is the solver half of invariant (i).
- The lift-only column is what moves from comfort_floor to room_floor, by invariant (iv): 12 of 44 floor steps (10.92 of 57.82 kWh) on the cold day, 1 of 14 (0.07 of 9.90 kWh) on the shoulder day.

## Alternatives

- **`slot_drivers` and the narrative read `rooms.lift_of(coordinator)` directly.** Lost: both are pure functions of the result (`slot_drivers.py:9-12`), and the held scalar is not the per-step lift the solve was given (the ramp and the band clip at `rooms.py:310-312` "ramp = max"). The what-if's result would also read the live coordinator's lift instead of the one its solve used.
- **Put the held scalar on the result and re-derive the per-step lift in the reader.** Lost: the reader would restate the ramp and clip that `rooms` owns, which is P2 carry s2's trap. It would also miss the mold floor and ceiling clip that only `_build_comfort_bounds` sees.
- **An entity attribute on the `comfort_floor` driver row instead of a sixth row.** Lost: a row has one weight, so the card could name the room but not say how much of the push was the room's. `WhyNowDriver` would also gain a key that one code uses.
- **Pass `min_temp_margins` as confidence only and let the optimizer add the lift.** Lost: the band clip in `lifted` is computed against the confidence margins, so `rooms` would hand the optimizer half a computation. It would also need a second coordinator call at each site, at zero headroom.

## Sibling sites

- `git grep -n "min_temp_margins=" -- custom_components/heatpump_optimizer/coordinator.py` returns the two builds. Both take the splat.
- `git grep -n "comfort_floor\|REASON_COMFORT_FLOOR" -- . ':!dev' ':!tests/golden'` returns the reason-code registry:
  - `payload.py:58`
  - `optimizer.py:2366` and `optimizer.py:2455`
  - `narrative.py:46` "holding the minimum temperature" and its sv and de lines
  - `strings.json:2103` under the `plan_narrative` state, and the three translations
  - `icons.json:204`
  - `www/heatpump-optimizer-card.js:446` "reasons.comfort_floor" with its sv and de lines and the map at `www/heatpump-optimizer-card.js:3510`
- `git grep -n "DRIVER_CODES\|whynow\.\(driver\|explain\)_" -- . ':!dev' ':!tests/golden'` returns the driver registry:
  - `slot_drivers.py:28`
  - `www/heatpump-optimizer-card.js:923` "whynow.driver_comfort_floor" and its sv and de lines
  - `docs/dashboard-card.md`, which lists five driver names
- Out of scope:
  - `classify_dhw_steps` reads no room floor.
  - `idle_coasting` (`idle_codes`) compares against `temp_min_bounds` and keeps that meaning.
  - The settlement's `IDLE_REASONS` question is not asked of a heating code.

## Evidence, by file

**Failing tests first.** Each runs with the symbol absent, then with the assertion.

- **`tests/features.py`:**
  - **Classify.** Driven with a hand-built 4-step case: floor 19.5, lift 0.5 on steps 1 to 3, next temperatures 19.6 / 19.95 / 20.0 / 21.0, all heating. Expected `comfort_floor`, room_floor, room_floor, and step 3 keeps the label it has today.
  - **Drivers.** On `_Horizon` (the `tests/features.py:158` builder takes the new keyword), with a lift the room_lift weight is above 0 and comfort plus room equals today's comfort push where nothing clips (invariant ii).
  - **Narrative.** `narrative.build` groups room_floor apart, and its kWh plus `comfort_floor`'s equals the unsplit run's (invariant iv).
  - **Mold.** With a mold floor above the lifted floor, room-lifts is 0 at those steps.
  - **Null controls.** Room-lifts None and a zero lift that `rooms.lifted` turns into `base` each give five driver codes, byte-equal weights and byte-equal reasons, against the same horizon without the field. The what-if's room-lifts equal the baseline's after the readings change (carry r4).
- **`tests/validate.py` or `tests/edge.py`:** the cold-day production solve from the table, with and without the lift. The lift run has at least one room_floor step, the power schedule is byte-equal to a run passing the same margins without room-lifts (invariant iii), and the None run has none.
- **Goldens:** no fixture has a room list, so `tests/golden/` and both claim files stay byte-identical. That is the golden null control. `tests/golden.py:845` records `space_reasons`, and the fixer runs it in drift mode to show no move.
- **`tests/entities.py`:**
  - `tests/entities.py:27147-27156` (every `optimizer.REASON_*` in `TEMPLATES["en"]`)
  - `tests/entities.py:27002-27006` (the enum options)
  - `tests/entities.py:27222-27240` (icon keys)
  - `tests/entities.py:745` (strings parity)
  - All four pass once registered; none is edited.
- **`tests/card.mjs`:**
  - `tests/card.mjs:3187-3196` (`REASON_LABELS` covers payload) passes once registered.
  - The pinned five-name lists at `tests/card.mjs:13752-13755` are extended to six in `DRIVER_CODES` order.
  - The card renders a room_lift row from a fixture, and with no room_lift code the five-row render is byte-equal.
- **Harness headers:** no harness with `EXPECTED RESULT` lines reads reasons or drivers, so `tests/harness_headers.py` is untouched.
- **Mutation targets:**
  - the room_floor branch's second comparison and its `0.15`
  - the subtraction in the unlifted-bounds build
  - the room_lifts-is-None presence test in `space_drivers`
  - the room_lift row's clip bounds
  - the comfort push's subtraction of room_lifts
  - the splat's None for an unlifted solve

## Hot files, position, carries

- **Serial:** after R11-OUTSIDE-ROOMS-P3 (merged).
- **Hot files:** `optimizer.py`, `slot_drivers.py`, `rooms.py`, `coordinator.py` (two existing lines), `payload.py`, `narrative.py`, `strings.json` and the three translations, `icons.json`, `www/heatpump-optimizer-card.js`, `docs/dashboard-card.md`, `tests/features.py`, `tests/card.mjs`.
- **No pinned grader is added,** so there is no p1/p2 split.
- **Received and answered:** e98789a8 and e82913fe (the per-step lift on the solve's record, read by `slot_drivers` and `narrative.py`, card text in three languages, toggle-off control), and 5a1c0e06.

## Decisions routed

- decision: owner. The narrative and the why-now row name the room lift as a cause, and the room's entity stays on `rooms.lift.entity` (designed so; the alternative is a fifth template placeholder across every sentence).
- decision: owner. Card and narrative wording in en, sv and de. The fixer proposes, and the PR surfaces it.
- decision: orchestrator. Size L: about twelve production files and three card languages, with no golden moves.

## Notes for the fixer

- The plan must not move. Show the power sha1 equal with room-lifts passed and absent for the same margins before any reader change lands. Carry: R11-OUTSIDE-ROOMS-3B (item 3b1)
- Every key of `tests/structure_budgets.json` may sit at zero headroom (`python3 tests/structure.py`). The coordinator edit replaces arguments in place, and the optimizer lines are paid in the same pull request. Carry: R11-OUTSIDE-ROOMS-3B (item 3b2)
- Re-measure the spike's table at the merge base before quoting it, because solve milliseconds vary up to twofold run to run. Carry: R11-OUTSIDE-ROOMS-3B (item 3b3)

Seat tokens: one read-only scout, 70501 (harness figure); the harness reports none for the main loop.
