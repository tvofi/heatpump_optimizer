Design review: approve bee723ac4d64b5cce282ddcfa79dbc75e51a7b4f

Group R11-SEAM-learners, note design.md at bee723ac4d (revision 2, answering verdict 6b72a4ab21 at 429223e197). This is the third design-review note of three. It is a delta review: `git diff 429223e197 bee723ac4d -- design.md` (209+/41-) plus the prior revise point. Code read at origin/main 78d3b40221.

## Prior revise point (verdict 6b72a4ab21)

1 (class-open, `_fold_flow_lift`) is resolved. The §3.2 row matches the code. `coordinator.py:975` is the outdoor-only room-air ask. `:979-980` reads the attribution of `_commanded_split()` against `_COP_CURVE_SHARE` (0.15, `:5244`). `:989` folds `last_supply_c` into `_flow_bias`, which is persisted at `store.py:394-395`. The note adds a §6 failing test with two nulls (no rise; a planned share under 0.15) and a mutation target (room-air restored must fail).

## Class enumeration (§5), re-run here at origin/main 78d3b40221

E1 prints 35 lines. Every one maps to a listed row (`:979-980`, `:1011-1012`, `:1184`, `:5013-5014`, `:5276`, `:9998`, `:10316-10317`, `heat_energy.py:325-326`), an excluded row (`:1105-1106`, `:1146`, `:1292-1293`, `:4991`, `:10090`, `heat_energy.py:509/540/612`), or a definition (`:1263`, `:10279`, `draw_range.py:427/436/455`, `heat_energy.py:232/239/255/276/418-420/530`).

E3 prints 14 lines. All map, except `:3149`, which copies `dhw_heating_active` into the published payload and is not a fold.

E2 prints 57 lines. Every learner fold maps to a row, the downstream set or the excluded table. The unnamed lines are not learners of an attributed sample, so no class member is missing. They are listed in the note below, because the fixer's item 9b3d1e22 would otherwise stop the PR on them.

A grep of every other `design/*` ref for `_fold_flow_lift`, `_accumulate_energy`, `_run_system_identification`, `energy_totals` and `flow_bias` found nothing, so the new rows claim no sibling's seam.

## The four new §3.2 rows, against the code

All four rows match the code.

- flow lift: as above.
- span close COP: `close.cop` at `coordinator.py:1192-1194`, on the span's `reference`, gated today only by the per-cycle clean AND.
- sysid experiment: `:11042-11047` feeds `_learning_frozen(indoor, outdoor)` to `sysid.hold_reason` and `stand_down`. `step` books `plan_power_kw * cop` while settling (`sysid.py:1782`) and `_step_power * cop` while stepping (`sysid.py:1795`; the note says `:1792`, see the carry below).
- energy totals: `:10316-10322` books `dhw_share` of the plan split's attribution.

## §6 tests on today's code

- Flow lift: fails, because no tank condition gates `:989`. The `_fl_coord` fixture is at `tests/features.py:34994`.
- sysid stand-down: fails, because `hold_reason` sees no tank evidence.
- Span COP rise under the band: fails, because the per-cycle AND does not read the tank.
- Energy totals: fails, because an unobserved interval books by the plan split to space.
- `ceiling_frozen`: fails, because the keyword does not exist today.
- #944 and the #3737 map run are preservation and after-merge tests, and the note scopes them that way.
- `HeatEnergyMeter.observe_cycle` has no direct caller in `tests/` at 78d3b40221, as item 9b3d1e19 states.

## Notes for the fixer

- When re-running E2 (item 9b3d1e22), exclude these lines, which are not folds of an attributed sample: `coordinator.py:1121/1129` (the meter's own observe, the evidence owner), `:2169`, `:2768`, `:3139` and `:3218` (dict and vars updates), `:2452` (`_record_manual_release`, solve releases), `:2481` (`_fold_away`, the away payload view), `:6749` (`rooms.record`, a per-cycle readings cache), `:6784` and `:8706` (`_defrost_window`, the defrost flag), `:8798` (`_peak_guard`, the whole meter), `:9650` (snapshot health), `:10297` (ledger spot and savings on the whole meter) and `:10694` (`price_tiles.record`, user answers). E3's `:3149` is the published payload. Carry: R11-SEAM-learners (item c4e1a3b0)
- The step phase books delivered heat at `sysid.py:1795`, not `:1792`. Correct the anchor in the PR body and the test's comment. Carry: R11-SEAM-learners (item c4e1a3b1)
- The energy-totals row settles the pending interval. Read the evidence of that same interval (the one the draw-range gate reads as "the pending split's evidence"), not the following cycle's. Pin this with the totals test. Carry: R11-SEAM-learners (item c4e1a3b2)

## Routed

Carry 2 (§9, item c25b53cc) is ruled. The coordinator relayed the owner's ruling as option A, built after option C's closed-loop harness ("go with the recommendation"). It is not yet in `dev/programme/RULINGS.md` at origin/main. The fixer builds §9 to A after C, in the second pull request §9 names, and cites the ruling once it is recorded. The two P5 widths (§3.3) stay `decision: owner`. The owner picks them from the fixer's keep table. Neither blocks this verdict.
