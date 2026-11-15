# R11-OUTSIDE-HONEST-METERED-FLOOR: the metered floor moves the plan, converges, and is shown on the entity

Designer seat, round 2, on top of 4da49f23d0, answering the verdict at 570f9b7743 (revise 4da49f23d0, class-open). Group C of design/R11-OUTSIDE-HONEST-STARTS-RUNS at a63a2ca6cd (ruling c3's table; ruling c2), for outside pull request 3529 by Bankaifan (fork head 1f9daef4d93f, build commit 7eeb7cd676, rebuilt here). Base and code read at `origin/main` 5825e1346c; no predecessor (`after` none), so no handoff head. Every line number below is re-measured there (verdict note r3). Owner ruling c2 (carry 1): the learned floor moves the plan. No finder harness: the contributor's report (their note at 054a866c94: the 0.53 kW datasheet floor never held, metered running draw 1.1 to 3.3 kW) is the evidence; test 1 is the synthetic fixture.

## Answers to the verdict

- **Revise point 1 (user surface): designed**, section "User surface". The floor gets its own three attributes beside the maximum's, two translated enums in all four string files, the entities pin and a docs paragraph; the maximum's three attributes stay byte for byte.
- **Decision routed (notice): orchestrator's.** This note designs no notice; the entity attribute and the docs are the user channel, which is what makes the limit sentence true. Reason: the plan already acts on F, so a notice would stand raised on every install where the floor works, and nothing the user does clears it short of a reconfiguration that throws the evidence away. If the orchestrator rules a notice is in scope, its shape is one `issues.set_issue` call raised while F is applied, cleared otherwise, with the same placeholders as the attribute row, its text checked against the reason codes below; no other part of this note changes.
- **Notes r1, r2**: folded into tests 1 and 6. **r3**: re-measured. **r4**: F and its since-count are `whole=_DRAW_KEY` leaves, precedent `draw/engaged` (`store.py:324`), not `draw/overdraws`.

## Finding

`solve_band` (`draw_range.py:697`) moves the top only; the bottom is configured or held under the top. The window already holds the low end (`DrawRange._run_asked`, `draw_range.py:237`, read by `power_floor_kw`, `draw_range.py:515`) and no solve reads it.

## The loop as built, and why it never settles

7eeb7cd676 files a sample into a second store only where the ask is at or under (1 + `AGREE_TOLERANCE`) x the **configured** floor, and lapses each sample `CEILING_LAPSE_DAYS` after it was taken. A plan floored at 1.1 never asks 0.61 again, so the store gets nothing, lapses, the band returns to 0.53, the plan asks 0.53, the pump draws 1.1, and the floor is learned again: a cycle by construction. The evidence is defined against a level the moved plan stops asking; the lapse closes the loop.

## Shape: evidence at the floor in force, held, reset on every move

f is the floor in force: the learned floor F where set, else the configured `min_electrical_power`.

- **Evidence E**: the pairs `_run_asked` returns among the trailing n samples, n F's since-count, whose ask lies within `AGREE_TOLERANCE` of f. `_run_asked` gains two keyword bounds (ask interval, trailing count) whose defaults are today's, so `power_floor_kw` is bit for bit (carry 0).
- **Statistic, one**: the `LOW_PERCENTILE` of drawn over E, `None` under `MIN_SAMPLES` pairs, through the helper `power_floor_kw` uses.
- **Raise** above (1 + tol) f sets F to it. **Lower** below (1 - tol) f sets F to it, or clears F where it is at or under (1 + tol) x configured; never under configured (the COP learner's end). **Hold** otherwise and whenever E is short. No age lapse. Never above the band's top: applied as min(F, top).
- **Reset**: a move of F sets n to 0. **Alignment (r2)**: n counts samples appended since the move and is read as min(n, len(samples)), so `WINDOW` eviction cannot over-count; `from_dict` stores n with the samples and re-clamps it after dropping unreadable rows (`draw_range.py:383-391`); every `samples.clear()` in `observe` (`draw_range.py:303-307`) sets n to 0, the legacy-commands clear holding F and the configuration clear dropping it.

**Convergence** (attacked and held, verdict). g(a) is the low-end draw of a run asked at a, nondecreasing. Each move sets f to g(f) and only by more than a factor 1 +- tol; f, g(f), g(g(f)) is monotone, bounded by the configured floor and the top, each step a fixed ratio: finitely many moves, no cycle. The premise is stronger than nondecreasing: `_band_kw` maps a step on the stamped `planned_min_kw` (`pump_arbiter.py:702`), so an ask at f writes the floor set-point and draws the pump's own least m whatever f is; g_f(f) = m, and f does not feed back into E's statistic. Seasonal change in m is tracking, one move per step, not a loop.

**Why the moved plan does not erase its evidence.** E is defined at f, and a plan floored at f asks f whenever it wants its least, so the move generates the evidence that keeps it; a week that never asks f leaves E short and F held, never reverted. **The limit:** a pump that follows its ask and whose true minimum falls under F is never asked under F, so no plan evidence lowers it; its way down is a reconfiguration of **Heat pump min power**, and the entity's floor row and the docs paragraph below are how the user sees F and that way down.

**Where it applies.** Learned on every install the window folds and published always; it moves the band only where the plan's levels clamp (`levels_clamped`, `thermal_model.py:1575`), or group A's engaged predicate where A is on main at the fixer's merge base, read, never restated; never where `plan_writes_power`.

## Interfaces and data flow

`DrawRange` gains F and n, unset by default; `DrawRange.observe` gains one call to a module-level update (`class_excess_loc` has no headroom). `solve_band` gains one keyword, whether the band takes the floor, default false. `SolveBand` gains four fields and `as_dict` four keys: the minimum's source, its reason, the learned floor raw (published applied or not) and the size of E; `planned_min_kw` is the applied minimum. `_band_fields` (`coordinator.py:2430`) passes both figures when either end moved (its `source == "configured"` test becomes both sources configured); `_solve_band` (`coordinator.py:2425`) passes the predicate. `store.DOMAINS` gains the two leaves; additive, no version bump, absent reads unset, read in `DrawRange.from_dict` through a module reader beside `_stored_ceiling`. No second sample store.

```
fold -> DrawRange.observe -> samples += (drawn, ask); n += 1; update over E(f) -> F, n
solve -> _solve_band(predicate) -> solve_band -> SolveBand(min = min(F, top) if applied)
      -> _band_fields -> solve copy -> optimizer -> result.solve_band (coordinator.py:6450, optimizer.py:2419)
      -> payload pump_max_power (coordinator.py:7981, payload.py:859) -> sensor._pump_max_power -> entity
arbiter: _band_kw maps on planned_min_kw -> ask at f writes the floor set-point -> meter -> fold
```

## User surface (revise point 1)

**Payload.** The `pump_max_power` field already carries the whole `SolveBand.as_dict()` (`payload.py:858` says so); it keeps its name, and its comment gains "both ends". A rename was rejected: three sites and every diagnostics bundle's key move for no behaviour.

**Entity.** `_pump_max_power` (`sensor.py:2095-2106`) becomes the one band reader and adds, beside its three unchanged attributes, three on the Learning Model Status entity. **Names** (planned, so stated by rule, not spelled: brief-citations.md remedy 1): each is the name of its max counterpart with `max` read as `min`. The row (`pump_max_power`'s counterpart) holds the counterparts of `configured_max_kw` and `learned_max_kw`, plus `planned_min_kw` and `samples` (the size of E); None when no band. The source and reason (counterparts of `pump_max_power_source` and `pump_max_power_reason`) are top-level codes, so `state_attributes` translates them. No floor key enters the max row. **Codes** (single words, so none is a planned symbol), each with the branch that returns it and its English text:

- source **configured**, F not applied: "Configured minimum"; source **metered**, F applied: "Measured by the meter at the minimum".
- reason `plan_writes_power`, the capability test: "Configured: the plan writes the power itself, so the meter only echoes it".
- reason **awaiting**, F unset, E short: "Configured: too few metered runs at the minimum yet".
- reason **agrees**, F unset, E full: "Configured: the metered minimum agrees with it".
- reason **cycled**, F set, predicate false: "Configured: the plan cycles the pump below its minimum, so a measured minimum would not change it".
- reason **measured**, F applied: "Measured: the running pump draws clearly more than its configured minimum".

**Text.** Each English sentence above is true of the branch that returns its code (brief binding 4), and test 7 reaches each branch. Into `strings.json` and `translations/en.json`, `translations/de.json`, `translations/sv.json` at the `learning_model_status` block (line 2150 in each), German and Swedish translated, never copied.

**Pin.** `tests/entities.py:13064`'s ModelStatusSensor set gains the three names.

**Docs.** `docs/how-it-works.md:1220` ("pump_max_power_source") gains, after the ceiling-probe paragraph, the metered minimum: learned from the low end of the metered draw on runs asked at the minimum in force, once enough such runs agree (the floor's sample gate); used when more than 15 % above **Heat pump min power**; never under it nor above the maximum in use; no lapse; it comes down when the meter shows less at the minimum, or when the setting is changed, which clears it; published as the three attributes. The sentence naming the three max attributes names the three min ones too.

## Alternatives

1. **As built (configured-floor asks, age lapse):** the cycle above; test 1's failing arm.
2. **Notice only:** refused by the owner (c2).
3. **The low end over every run ask (`power_floor_kw`'s own figure):** a cold week of high asks raises it and a floored plan never asks lower: latched at the season's draw.
4. **Floor-in-force asks without the reset, or unpersisted:** pre- and post-move draws mix, a two-cycle while both are in the window; unpersisted, a cold spell empties E and reverts the floor.
5. **A second store (the build's):** two holders of one window's low end; carry 0 refuses it.
6. **The floor inside the max row (no new attributes):** the row's name says maximum and its source and reason codes describe the top; one enum cannot say both ends' state.

## Sibling sites

`git grep -n -E "solve_band\(|_band_fields\(|planned_min_kw|_run_asked\(|power_floor_kw\(|solve_band\b|pump_max_power\b" -- custom_components tests/entities.py docs`: `draw_range.py` (the reader, `ask_evidence`, `power_floor_kw`, `solve_band`, `SolveBand`); `coordinator.py:2425`, `:2430`, `:6450` (stamp, unchanged), `:7981` (payload, unchanged), `:963` (power floor, unchanged); `optimizer.py:2419` (field, unchanged); `payload.py:859` (comment); `pump_arbiter.py:702` (covered: maps on the applied minimum); `sensor.py:2101-2105`, the four string files, `tests/entities.py:13064`, `docs/how-it-works.md:1220` (all covered above); `accuracy.py:922`, `:1077` (unchanged, bit for bit). `planned_range` and `diagnostics_view` read no floor: unchanged.

## Evidence, by file

`tests/features.py`, failing at the base:
1. **The loop**, first: configured 0.53, three arms folded through `DrawRange.observe` and read through `solve_band` over at least 3 x `WINDOW` samples with a cold spell of `WINDOW` no-floor asks: g = max(a, 1.1); g_f(f) = m, the arbiter's mapping; a step change in m mid-run. Assert at most one move per step, no move back without a new step, F held through the spell (r1). The same harness with the build's predicate and lapse (harness only) shows the band returning to 0.53 at least twice.
2. **Down and out**: g = 0.8 under F = 1.1 lowers it; never under configured; reconfiguration clears it; a move reads only post-move pairs.
3. **Persistence**: `as_dict`/`from_dict` round trip; absent leaves read unset; a record keyed to another range drops F.
4. **Application**: only under the predicate; `planned_min_kw` is F; unapplied publishes F with the predicate-false reason.
5. **Carry 0**: `power_floor_kw` bit for bit on the existing COP-floor fixtures.
6. **Alignment (r2)**: n after `WINDOW` + k appends is `WINDOW`; after `from_dict` drops a row it is clamped; after the legacy-commands clear it is 0 with F held.
7. **Surface**: each reason code reached by its fixture, and every code `solve_band` returns present in all four string files; the max row and its two codes byte for byte on a configured band.

**Null controls**, each a full `optimize` twice with arrays equal: (a) configured 1.1, g = max(a, 1.1): no floor, band, plan and max attributes identical to the base; its perturbation, configured 0.53, moves the band, or the control is void. (b) g = a + i, i under tol x configured: nothing moves. (c) a cold week of high asks only: nothing moves. `python3 tests/env_drift.py --all`: no golden carries a draw window; both claim files byte-identical. **Mutation targets:** E's ask bounds; the reset; the n clamp and each clear's reset; raise and lower tolerances; the clear-to-configured line; the `MIN_SAMPLES` gate; reconfiguration clearing F; `min(F, top)`; the keyword's default; the predicate; `_band_fields`' either-end test; the store reader; each reason branch.

## Hot files, position, carries

`draw_range.py`, `coordinator.py`, `store.py`, `sensor.py`, the four string files, `docs/how-it-works.md`. R10-DRAW-MAP-EVIDENCE (archive/design/R10-DRAW-MAP-EVIDENCE at 9aa450f55e; none on main) touches `draw_range.py`'s `fold`, `as_dict`, `from_dict` and `store.DOMAINS`' `draw/` leaves: a textual seam only; whichever lands second rebases. Receives carry 0 and carry 1, owes none. Size M; DESIGN FIRST. Every commit message and body credits Bankaifan and pull request 3529.

## Notes for the fixer

- g nondecreasing (or g_f(f) = m) is the convergence premise: test 1 states it as a fixture property, and the body reports whether the contributor's install (1.1 to 3.3 kW metered) meets it. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f1)
- Run `python3 tests/structure.py` at base and head: `class_excess_loc` has no headroom and `DrawRange.from_dict` sits near the `functions_cc_over_15` line, which is why the update and the reader are module-level. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f2)
- The German and Swedish strings are translations, never copies of the English, and say what the English says of the same branch. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f3)
