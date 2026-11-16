# R11-OUTSIDE-HONEST-METERED-FLOOR: the metered floor moves the plan, converges, and is shown on the entity

Designer seat, round 3, on top of ef9b12e7dd, answering the verdict at 45f646aa7a (revise ef9b12e7dd, golden-unclaimed). Group C of design/R11-OUTSIDE-HONEST-STARTS-RUNS at a63a2ca6cd (ruling c3's table; ruling c2), for outside pull request 3529 by Bankaifan (fork head 1f9daef4d93f, build commit 7eeb7cd676, rebuilt here). Base and code read at `origin/main` 824a016f75 (the payload's base); no predecessor (`after` none), so no handoff head. Every line number below is re-measured there; `draw_range.py`, `sensor.py`, `store.py` and `pump_arbiter.py` are unchanged from round 2's base 5825e1346c, and `coordinator.py`'s cited lines moved by one. Owner ruling c2 (carry 1): the learned floor moves the plan. No finder harness: the contributor's report (their note at 054a866c94: the 0.53 kW datasheet floor never held, metered running draw 1.1 to 3.3 kW) is the evidence; test 1 is the synthetic fixture.

## Answers to the verdict

- **Revise point 1 (golden-unclaimed): designed**, section "Goldens that move". The three new attributes are written with no band, as `None`, so the five coord captures move; each is claimed ADDED in `tests/golden/claimed_drift.txt` and its committed file patched in those three paths alone, as R10-COP-GATE-D did. Null control (a) is restated to "only those three added null keys". The parent note's sentence that C moves no golden (a63a2ca6cd) no longer holds once C publishes on the entity: this note supersedes it for group C.
- **Notice: the orchestrator's decision, still routed.** This note designs no notice; if one is ruled in scope, its shape is one `issues.set_issue` call raised while F is applied and cleared otherwise, its text checked against the reason codes below; nothing else here changes.
- **v2a** (the "agrees" text): the branch's code is now **unexceeded**, worded one-sided (User surface), so it is true where the statistic is below configured as well. **v2b**: test 7 extends the carry-6 check, not a second loop. **v2c**: the D6 claims register is regenerated at the head (Evidence).

## Finding

`solve_band` (`draw_range.py:697`) moves the top only; the bottom is configured or held under the top. The window already holds the low end (`DrawRange._run_asked`, `draw_range.py:237`, read by `power_floor_kw`, `draw_range.py:515`) and no solve reads it.

## The loop as built, and why it never settles

7eeb7cd676 files a sample into a second store only where the ask is at or under (1 + `AGREE_TOLERANCE`) x the **configured** floor, and lapses each sample `CEILING_LAPSE_DAYS` after it was taken. A plan floored at 1.1 never asks 0.61 again, so the store gets nothing, lapses, the band returns to 0.53, the plan asks 0.53, the pump draws 1.1, and the floor is learned again: a cycle by construction.

## Shape: evidence at the floor in force, held, reset on every move

f is the floor in force: the learned floor F where set, else the configured `min_electrical_power`.

- **Evidence E**: the pairs `_run_asked` returns among the trailing n samples, n F's since-count, whose ask lies within `AGREE_TOLERANCE` of f. `_run_asked` gains two keyword bounds (ask interval, trailing count) whose defaults are today's, so `power_floor_kw` is bit for bit (carry 0).
- **Statistic, one**: the `LOW_PERCENTILE` of drawn over E, `None` under `MIN_SAMPLES` pairs, through the helper `power_floor_kw` uses.
- **Raise** above (1 + tol) f sets F to it. **Lower** below (1 - tol) f sets F to it, or clears F where it is at or under (1 + tol) x configured; never under configured. **Hold** otherwise and whenever E is short. No age lapse. Applied as min(F, top). Hence F set implies F > (1 + tol) x configured.
- **Reset**: a move of F sets n to 0. **Alignment**: n counts appends since the move, read as min(n, len(samples)); `from_dict` (`draw_range.py:358`) stores n with the samples and re-clamps it after dropping unreadable rows; the `samples.clear()` in `observe` (`draw_range.py:304`) sets n to 0, holding F on the legacy-commands arm and dropping it on a configuration change.

**Convergence** (attacked twice, held). g(a), the low-end draw of a run asked at a, is nondecreasing; each move sets f to g(f) and only by more than a factor 1 +- tol, so f, g(f), g(g(f)) is monotone and bounded by configured and the top, each step a fixed ratio: finitely many moves, no cycle. Stronger: `_band_kw` maps on the stamped `planned_min_kw` (`pump_arbiter.py:702`), so an ask at f writes the floor set-point and draws the pump's own least m whatever f is; g_f(f) = m. Seasonal change in m is tracking, one move per step.

**Why the moved plan does not erase its evidence.** E is defined at f, and a plan floored at f asks f whenever it wants its least, so the move generates the evidence that keeps it; a week that never asks f leaves E short and F held, never reverted. **The limit:** a pump whose true minimum falls under F is never asked under F; its way down is a reconfiguration of **Heat pump min power**, and the entity row and docs paragraph below are how the user sees F and that way.

**Where it applies.** Learned wherever the window folds and published always; it moves the band only where `levels_clamped` (`thermal_model.py:1575`) holds, or group A's engaged predicate where A is on main at the fixer's merge base, read, never restated; never where `plan_writes_power`.

## Interfaces and data flow

`DrawRange` gains F and n, unset by default; `observe` gains one call to a module-level update (`class_excess_loc` has no headroom). `solve_band` gains one keyword, whether the band takes the floor, default false. `SolveBand` gains four fields and `as_dict` four keys: the minimum's source, its reason, the learned floor raw and the size of E; `planned_min_kw` is the applied minimum. `_band_fields` (`coordinator.py:2431`) passes both figures when either end moved (its `source == "configured"` test at `coordinator.py:2434` becomes both sources configured); `_solve_band` (`coordinator.py:2426`) passes the predicate. `store.DOMAINS` gains the two leaves as `whole=_DRAW_KEY`, precedent `draw/engaged` (`store.py:324`); additive, no version bump, absent reads unset, read in `from_dict` through a module reader beside `_stored_ceiling` (`draw_range.py:448`). No second sample store.

```
fold -> DrawRange.observe -> samples += (drawn, ask); n += 1; update over E(f) -> F, n
solve -> _solve_band(predicate) -> solve_band -> SolveBand(min = min(F, top) if applied)
      -> _band_fields -> optimizer -> result.solve_band (coordinator.py:6451, optimizer.py:2419)
      -> payload pump_max_power (coordinator.py:7982, payload.py:858) -> sensor._pump_max_power -> entity
arbiter: _band_kw maps on planned_min_kw -> ask at f writes the floor set-point -> meter -> fold
```

## User surface

**Payload.** `pump_max_power` already carries the whole `SolveBand.as_dict()` (`payload.py:858`); it keeps its name, its comment gains "both ends". A rename moves three sites and every diagnostics bundle's key for no behaviour.

**Entity.** `_pump_max_power` (`sensor.py:2095-2106`) adds, beside its three unchanged attributes, three on the Learning Model Status entity, named as their max counterparts with `max` read as `min` (planned, so not spelled: brief-citations.md remedy 1): a row holding the counterparts of `configured_max_kw` and `learned_max_kw`, plus `planned_min_kw` and `samples` (the size of E), `None` when no band; and the source and reason as top-level codes, translated by `state_attributes`. No floor key enters the max row. **Codes**, each with its branch and English text:

- source **configured**, F not applied: "Configured minimum"; source **metered**, F applied: "Measured by the meter at the minimum".
- reason `plan_writes_power`: "Configured: the plan writes the power itself, so the meter only echoes it".
- reason **awaiting**, F unset, E short: "Configured: too few metered runs at the minimum yet".
- reason **unexceeded**, F unset, E full (statistic at or under (1 + tol) x configured, above or below it): "Configured: the metered minimum does not clearly exceed it".
- reason **cycled**, F set, predicate false: "Configured: the plan cycles the pump below its minimum, so a measured minimum would not change it".
- reason **measured**, F applied (so F > (1 + tol) x configured): "Measured: the running pump draws clearly more than its configured minimum".

Into `strings.json` and `translations/en.json`, `de.json`, `sv.json` at the `learning_model_status` block (line 2154 in each), German and Swedish translated. **Pin:** `tests/entities.py:13063-13066`'s ModelStatusSensor set gains the three names. **Docs:** `docs/how-it-works.md:1220` gains, after the ceiling-probe paragraph, the metered minimum: learned from the low end of the metered draw on runs asked at the minimum in force, once enough such runs agree; used when more than 15 % above **Heat pump min power**; never under it nor above the maximum in use; no lapse; it comes down when the meter shows less at the minimum, or when the setting is changed, which clears it; published as the three attributes.

## Goldens that move (revise point 1)

`_pump_max_power` writes every key with no band, so each coord capture gains the three new attributes, each null, under `sensors.model_status.extra_state_attributes`, beside today's at `tests/golden/coord_minimal.json:1903-1905`. The set, by `git grep -l '"pump_max_power_source"' -- tests/golden/`: coord_all_features, coord_dhw, coord_grid_fee, coord_minimal, coord_two_zone. `data.pump_max_power` stays null (no plan), so no payload leaf moves. Two writes, after R10-COP-GATE-D (a3919c9301 and ee92b1b2f6):

1. **The committed fixtures**: the three null leaves spliced into each of the five files in that path alone, never `golden.py --record` (it re-records every value under the host's BLAS), so `tests/golden.py:1489`'s "new field" DIFF and env_drift's `rot.failed` stay clean.
2. **The claim**: in `tests/golden/claimed_drift.txt`, under the `claims-for:` line live at build time (it must equal `VERSION`; never touched by the branch), a comment block written as R10-COP-GATE-D's is (`claimed_drift.txt:744-753`): the three leaves are the whole diff in each fixture, each "present on one side only" and ADDED at this head, no other leaf moves, measured with `python3 tests/env_drift.py --all` against the merge base in one environment; then one line per fixture, `<fixture>  # R11-OUTSIDE-HONEST-METERED-FLOOR (Bankaifan, #3529): three pump floor keys added (null), nothing else moves`.

`tests/golden/card_claimed_drift.txt` stays byte-identical. The parent group's branch (fix/r11-outside-honest-starts-runs at 0260dd241d) claims cycling_cost and everything_on and no coord fixture; whichever of the two lands second merges its claim lines through the claimnotes driver, never by hand.

## Alternatives

1. **As built (configured-floor asks, age lapse):** the cycle above; test 1's failing arm.
2. **Notice only:** refused by the owner (c2).
3. **The low end over every run ask (`power_floor_kw`'s figure):** a cold week of high asks raises it and a floored plan never asks lower: latched at the season's draw.
4. **Floor-in-force asks without the reset, or unpersisted:** pre- and post-move draws mix, a two-cycle while both are in the window; unpersisted, a cold spell empties E and reverts F.
5. **A second store (the build's):** two holders of one window's low end; carry 0 refuses it.
6. **The floor inside the max row:** the row's name, source and reason describe the top; one enum cannot say both ends' state. It would also move the same five goldens, so it saves no claim.

## Sibling sites

`git grep -n -E "solve_band\(|_band_fields\(|planned_min_kw|_run_asked\(|power_floor_kw\(|solve_band\b|pump_max_power\b" -- custom_components tests/entities.py tests/golden docs`: `draw_range.py` (reader, `ask_evidence`, `power_floor_kw`, `solve_band`, `SolveBand`); `coordinator.py:2426`, `:2431` (covered), `:6451`, `:7982`, `:964` (unchanged); `optimizer.py:2419` (unchanged); `payload.py:858` (comment); `pump_arbiter.py:702` (covered); `sensor.py:2095-2106`, the four string files, `tests/entities.py:13063-13066`, `docs/how-it-works.md:1220` (covered); `accuracy.py:922` (unchanged, bit for bit); the five coord goldens (moved and claimed, above); `tests/golden/config_flow.json` (only `heat_pump_max_power`, the config field: unaffected).

## Evidence, by file

`tests/features.py`, failing at the base:
1. **The loop**, first: configured 0.53, three arms folded through `DrawRange.observe` and read through `solve_band` over at least 3 x `WINDOW` samples with a cold spell of `WINDOW` no-floor asks: g = max(a, 1.1); g_f(f) = m; a step change in m mid-run. At most one move per step, no move back without a new step, F held through the spell. The same harness with the build's predicate and lapse shows the band returning to 0.53 at least twice.
2. **Down and out**: g = 0.8 under F = 1.1 lowers it; never under configured; reconfiguration clears it; a move reads only post-move pairs.
3. **Persistence**: round trip; absent leaves read unset; a record keyed to another range drops F.
4. **Application**: only under the predicate; `planned_min_kw` is F; unapplied publishes F with **cycled**.
5. **Carry 0**: `power_floor_kw` bit for bit on the existing COP-floor fixtures.
6. **Alignment**: n after `WINDOW` + k appends is `WINDOW`; clamped after `from_dict` drops a row; 0 after the legacy-commands clear with F held.
7. **Surface**: each reason code reached by its fixture, **unexceeded** by both a statistic within tol and one below (1 - tol) x configured; the two min codes added to the carry-6 `_cpd_codes` table (`tests/features.py:87852-87873`) so its one loop checks all four string files, the reached-set equality extended to them; the max row and its codes byte for byte on a configured band.

**Null controls**, each a full `optimize` twice with arrays equal: (a) configured 1.1, g = max(a, 1.1): no F; band, plan and the three existing max attributes identical to the base, and each coord fixture's diff under `python3 tests/env_drift.py --all` is only the three added null keys; its perturbation, configured 0.53, moves the band, or the control is void. (b) g = a + i, i under tol x configured: nothing moves. (c) a cold week of high asks only: nothing moves. **Register:** `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` rerun at the head and `claims.json`/`claims.md` committed if they move (ee92b1b2f6's precedent). **Mutation targets:** E's ask bounds; the reset; the n clamp and each clear's reset; raise and lower tolerances; the clear-to-configured line; the `MIN_SAMPLES` gate; reconfiguration clearing F; `min(F, top)`; the keyword's default; the predicate; `_band_fields`' either-end test; the store reader; each reason branch.

## Hot files, position, carries

`draw_range.py`, `coordinator.py`, `store.py`, `sensor.py`, the four string files, `docs/how-it-works.md`, the five coord goldens, `tests/golden/claimed_drift.txt`. R10-DRAW-MAP-EVIDENCE (archive/design/R10-DRAW-MAP-EVIDENCE at 9aa450f55e; none on main) touches `fold`, `as_dict`, `from_dict` and the `draw/` leaves: a textual seam; whichever lands second rebases. Receives carries 0 and 1, owes none. Size M; DESIGN FIRST. Every commit message and body credits Bankaifan and pull request 3529.

## Notes for the fixer

- g nondecreasing (or g_f(f) = m) is the convergence premise: test 1 states it as a fixture property, and the body reports whether the contributor's install (1.1 to 3.3 kW metered) meets it. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f1)
- Run `python3 tests/structure.py` at base and head: `class_excess_loc` has no headroom and `DrawRange.from_dict` sits near the `functions_cc_over_15` line, which is why the update and the reader are module-level. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f2)
- The German and Swedish strings are translations, never copies of the English, and say what the English says of the same branch. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f3)
- The golden splice is by hand in three paths per file; check it with `python3 tests/golden.py` (no DIFF) and `python3 tests/env_drift.py --all` (only the claimed ADDED leaves) before the handoff, and keep the claim's `claims-for:` equal to `VERSION` after any rebase across a stamp. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f4)
