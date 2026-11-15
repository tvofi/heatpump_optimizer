# R11-OUTSIDE-HONEST-METERED-FLOOR: the metered floor moves the plan, and converges

Designer seat, round 1. Group C of design/R11-OUTSIDE-HONEST-STARTS-RUNS at a63a2ca6cd (ruling c3's table; ruling c2), for outside pull request 3529 by Bankaifan (fork head 1f9daef4d93f, build commit 7eeb7cd676, rebuilt here). Base and code read at `origin/main` ebe83a1b82; no predecessor (`after` none), so no handoff head. R10-COP-LEARNER-DRAW-FLOOR is on main (acf912282f); group A is not (no runs module at the base). Owner ruling c2 (carry 1): the learned floor moves the plan; every notice-only sentence of the brief and of a63a2ca6cd is void here, the notice included (not built: the band publishes the figure, and nothing waits on the user). No finder harness: the contributor's report (their note at 054a866c94, the 0.53 kW datasheet floor never held, metered running draw 1.1 to 3.3 kW) is the evidence; test 1 is the synthetic fixture. Re-measured: the brief's "configured floor above what the pump draws" is the COP learner's end (#2066); this group's finding is the opposite, configured 0.53 under a metered 1.1.

## Finding

`solve_band` (`draw_range.py:697`) moves the top only; the bottom is configured or held under the top. The window already holds the low end (`DrawRange._run_asked`, `draw_range.py:237`, read by `power_floor_kw`, `draw_range.py:515`) and no solve reads it.

## The loop as built, and why it never settles

7eeb7cd676 files a sample into a second store only where the ask is at or under (1 + `AGREE_TOLERANCE`) x the **configured** floor, and lapses each sample `CEILING_LAPSE_DAYS` after it was taken. A plan floored at 1.1 never asks 0.61 again, so the store gets nothing, lapses, the band returns to 0.53, the plan asks 0.53, the pump draws 1.1, and the floor is learned again: period about 45 days plus the refill, by construction (the build's own comment says "the store lapses and the configured figure returns"). The evidence is defined against a level the moved plan stops asking; that is the defect, and the lapse is what closes the loop.

## Shape: evidence at the floor in force, held, reset on every move

Let f be the floor in force: the learned floor F where one is set, else the configured `min_electrical_power`.

- **Evidence E**: the pairs `_run_asked` returns, among the window samples folded since F last changed, whose ask lies within `AGREE_TOLERANCE` of f on both sides. With F unset this is the contributor's set (asks in [cfg_min, 1.15 cfg_min]); with F set it is the asks a floored plan issues when it wants its least.
- **Statistic, one**: the `LOW_PERCENTILE` of drawn over E, `None` under `MIN_SAMPLES` pairs. `power_floor_kw` and the floor read the same module helper over the same reader; `_run_asked` gains two keyword bounds (ask interval, trailing count) whose defaults are today's, so `power_floor_kw` is bit for bit (carry 0).
- **Raise**: the statistic above (1 + tol) f sets F to it. **Lower**: below (1 - tol) f sets F to it, or clears F (configured) where it is at or under (1 + tol) x configured; never under configured: the COP learner owns that end. **Hold**: otherwise, and whenever E is short. No age lapse.
- **Reset**: any move of F, and any reconfiguration (the window's key, `DrawRange.observe` already clears the samples), restarts E; reconfiguration also clears F.

**Convergence.** Let g(a) be the low-end draw of a run asked at a: stationary, and nondecreasing in a (a larger ask never draws less; `_band_kw` maps a step on the `planned_min_kw` it was solved on (`pump_arbiter.py:702`), so an ask at f writes the floor set-point and draws the pump's own least). Each move sets f to g(f), and only by more than a factor 1 +- tol. For nondecreasing g the sequence f, g(f), g(g(f)) is monotone (g(f0) > f0 gives g(g(f0)) >= g(f0)), it is bounded by the configured floor and the band top, and every step exceeds a fixed ratio: finitely many moves, no cycle. Cases: a pump that follows its ask above a true minimum m, g = max(a, m): one raise, to m. A controller-set draw c, g = c: one move. A meter reading idle draw i over the compressor, g = max(a, m) + i: monotone moves while i > tol f, so bounded, and none where i < tol x configured (null control b). The reset is what makes each move read g at the current f: without it E mixes draws under two floors (alternative 4).

**Why the moved plan does not erase its evidence.** E is defined against f, and a plan floored at f asks f whenever it wants its least, so the move generates exactly the evidence that keeps it; a week that never asks f (a cold spell) leaves E short and F held, never reverted. **The limit, stated:** a pump that follows its ask and whose true minimum falls below a learned F is never asked below F, so no plan evidence lowers it; its way down is a reconfiguration, and the published learned figure is how the user sees it. A pump whose own controller draws under the ask lowers it from E.

**Where it applies.** The floor is learned on every install the window folds and published always; it moves the band only on a solve whose shipped plan holds no running step under its floor, so E never reads a duty-cycle average: `levels_clamped` (`thermal_model.py:1575`) at the base, and group A's engaged predicate wherever A is on main at the fixer's merge base, read, never restated (A's invariant: no shipped step between `MIN_RUNNING_DRAW_KW` and the floor). Never where `plan_writes_power`, never with `draw.config` keyed to another range, never above the band's top.

**Interfaces.** `DrawRange` gains one field: F with its since-count, unset by default; `DrawRange.observe` gains one call to a module-level update (the class spans 277 of the 300 lines `class_excess_loc` counts from, at zero headroom, so the update lives outside it). `solve_band` gains one keyword, whether the band takes the floor, default false. `SolveBand` gains the floor's source (configured or metered floor), the learned floor raw (published applied or not) and the size of E; `as_dict` three keys, `planned_min_kw` the applied minimum. `_band_fields` (`coordinator.py:2429`) passes both figures when either end moved; `_solve_band` (`coordinator.py:2424`) passes the predicate. `store.DOMAINS` gains two leaves under `draw/` with `whole=_DRAW_KEY`, the latch's key; additive, no version bump, absent reads unset, the precedent `draw/overdraws` (055d5d57b6); read in `DrawRange.from_dict` through a module reader beside `_stored_ceiling`. No second sample store.

```
fold -> DrawRange.observe -> samples += (drawn, ask) ; floor update over E(f) -> F, since
solve -> _solve_band(predicate) -> solve_band -> SolveBand(min = min(F, top) if applied)
      -> _band_fields -> solve copy min_electrical_power -> optimizer -> result.solve_band
arbiter: _band_kw maps on planned_min_kw -> ask at f writes the floor set-point -> meter -> fold
```

## Alternatives

1. **As built (configured-floor asks, age lapse):** the 45-day cycle above; test 1's failing arm.
2. **Notice only:** refused by the owner (c2).
3. **The low end over every run ask (`power_floor_kw`'s own figure, unbounded):** a cold week of high asks raises it, and a floored plan never asks lower, so it latches at the season's draw with no way down.
4. **Floor-in-force asks without the reset, or recomputed per solve without persistence:** a lower read on fresh draws meets the raise read on draws under the old floor still in the window, a two-cycle while both are in it; unpersisted, a cold spell empties E and reverts the floor.
5. **A second store (the build's):** two holders of the same samples' low end; carry 0 refuses it.

## Sibling sites

`git grep -n -E "solve_band\(|_band_fields\(|planned_min_kw|_run_asked\(|power_floor_kw\(" -- custom_components` at the base: `draw_range.py` (the reader, `ask_evidence`, `power_floor_kw`, `solve_band`), `coordinator.py:2424`, `:2429`, `:962` (power floor, unchanged), `accuracy.py:922` and `:1077` (unchanged, bit for bit), `pump_arbiter.py:702` (reads `planned_min_kw`, covered: a floored plan maps on its own band). `planned_range` and `diagnostics_view` read no floor: unchanged.

## Evidence, by file

`tests/features.py`, failing at the base:
1. **The loop** (written first; red at the base, where no floor exists): a synthetic install, configured 0.53, g = max(a, 1.1), a plan that asks its floor on a fixed share of samples and higher otherwise, folded through `DrawRange.observe` and read through `solve_band` over at least 3 x `WINDOW` samples with a cold spell of `WINDOW` samples asking no floor: F reaches 1.1 within tol, moves once, holds through the spell. The same harness with the build's predicate and lapse (in the harness only, never production) shows the band returning to 0.53 at least twice: the cycle demonstrated, then refused.
2. **Down and out**: g = 0.8 under a floor at 1.1 lowers it; never under configured; reconfiguration clears it; the reset (a move reads only post-move pairs).
3. **Persistence**: round trip through `as_dict` and `from_dict`; a record without the leaves reads unset; a record keyed to another range drops F.
4. **Application**: applied only under the predicate; `planned_min_kw` is F; unapplied publishes F with the configured minimum.
5. **Carry 0**: `power_floor_kw` bit for bit on the existing COP-floor fixtures.

**Null controls**, each a full `optimize` twice with arrays equal: (a) configured 1.1, g = max(a, 1.1): no floor set, band and plan identical to the base; its perturbation, configured 0.53, moves the band, or the control is void. (b) g = a + i, i under tol x configured: nothing moves. (c) a cold week of high asks only: nothing moves. `python3 tests/env_drift.py --all`: no golden carries a draw window, none moves, both claim files byte-identical. **Mutation targets:** E's lower and upper ask bounds; the reset; raise and lower tolerances; the clear-to-configured line; the `MIN_SAMPLES` gate; reconfiguration clearing F; `min(F, top)`; the keyword's default; the predicate; `_band_fields`' either-end test; the store reader.

## Hot files, position, carries

`draw_range.py`, `coordinator.py`, `store.py`. R10-DRAW-MAP-EVIDENCE (approved, archive/design/R10-DRAW-MAP-EVIDENCE at 9aa450f55e; none on main) touches `draw_range.py`'s `fold`, `as_dict`, `from_dict` and `store.DOMAINS`' `draw/` leaves: a textual seam only (its map rows never reach `DrawRange.observe`); whichever lands second rebases. Receives carry 0 and carry 1, owes none. Size M; DESIGN FIRST, and the reviewer attacks the convergence claim. Every commit message and body credits Bankaifan and pull request 3529.

## Notes for the fixer

- g nondecreasing is the convergence premise: test 1 states it as a fixture property, and the body reports whether the contributor's install (1.1 to 3.3 kW metered) meets it. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f1)
- Run `python3 tests/structure.py` at base and head: `class_excess_loc` has no headroom and `DrawRange.from_dict` sits near the `functions_cc_over_15` line, which is why the update and the reader are module-level. Carry: R11-OUTSIDE-HONEST-METERED-FLOOR (item f2)
