R10-HOTFIX-SAV-ESTIMATE, its two open carries (part 1 merged as #3220), topic r10-sav-wood-heat.

**Carry A (owner ruling, tvofi 2026-11-04): the reference has no wood, wood's heat counts in the saving, and a disclaimer appears where wood is configured.** I read the tree at merge base `0a7c84fa2` to see what was already built:

| part | at the merge base | this PR |
|---|---|---|
| reference with no wood, actuals metered (`ledger.py` `REFERENCE_BASIS`, `savings_months`) | built (#3220) | mutation proof only |
| dash on two-tank houses | already gone: `savings_sek` is `None` only on `old_basis` (`ledger.py` `savings_months`); no tank-keyed path in ledger, coordinator, payload or card | none |
| old-basis rows keep the dash | built; pinned | mutation proof only |
| card savings table disclaimer, en and sv (`savings.wood_note`) | built; pinned by `card_browser.mjs` | mutation proof only |
| receipt event (`notifier.py` `saving_includes_wood`) | built; pinned | mutation proof only |
| **card monthly receipt's "Saved ... against a plain thermostat" line** | **missing: no disclaimer** | **built**, failing test first |
| coordinator passes `wood_configured=wood_furnace_on(config)` | built, **unpinned**: its mutant survived `features.py` | **pin added** |

**Carry B (the size of wood's unforeseen heat).** The `wood-unforeseen` arm's meter is a fixed multiplier, so it tested the floor's arithmetic and not the heat. The new `wood-plant` arm in `dev/audit/harnesses/r10_sav_wood_reference.py` puts the fire in the plant only; the plan is never told of it. The plant pump follows the plan's own buffer trajectory over each `REPLAN` hold, so it draws less once wood carries the draw. The meter reads `m` times what the pump drew, where `m` is the model's own meter error, which the calibration exists to correct. The figure is the applied calibration's error against `m`, less the same error with no fire.

Measured (Figures): over 9 fires (4/8/12 kW, starting 06:00/17:00/22:00, 4 h each, never forecast), the meter fell 0.03 to 4.5 % under the plan.
- `m` 0.8 and 1.0: the error from the heat is 0.00 at every fire, because the floor absorbs it.
- `m` 1.2 (the model reads the meter low): the reference is booked low by mean 1.95 %, min 0, max 4.50 %, sd 1.47. The saving is understated by that share.

The docs' savings limits paragraph (`docs/how-it-works.md`, "Wood furnaces and other external heat") now states this size. I left the card's wood note unchanged: the figure comes from one simulated house with an hour's hold, and that does not support a sentence about a real house's monthly figure.

**What the arm cannot show, and the instrument an install would need.**
- It cannot show a real pump's control loop, a real fire's coupling to a house, or the coordinator's per-interval re-plan. Its hold is 4 intervals.
- A one-step target probe (the plan re-read every interval, the probe described under Null control) read the pump's draw equal to the plan's, 48.57 against 48.57 kWh, over a 12 kW fire.
- So the figure is an upper bound for this house, not a measured real-house size.
- An install would need the heat pump's own electric sub-meter beside a wood-tank heat meter, or a logged fire start and end, to separate the meter's fall into the model's error and wood's heat.

**A measured limit, not changed here.** On a wood house the floor also stops the calibration correcting a model that reads the meter high, with or without a fire. At `m` 0.8 the booked reference is +25.00 % (that is 1/m - 1) and the row reads 44.9 % against 31.1 %. This follows from the two owner rulings as built (calibration 2026-10-24, the floor). The docs paragraph says so. Changing it is the owner's call.

## Head

df4172cae30c402c674297922a1acccca4192ac1 (code at `handoff/r10-sav-wood-heat`). It merges `origin/main` at `dc0a170b6` (main's commit 2026-11-06T08:05Z, checked 2026-11-06T08:11Z). origin/main had not moved since then when `tools/pr/prepr.sh` last ran.
- The harness grid was re-run after merging `8a39977cb` and reproduced every figure exactly.
- Main's later deltas reach no file the harness imports. `8a39977cb..24547e39a` touches CI tooling, CI harnesses, `tests/entities.py`, `tests/ci_ratchet.py` and `tests/closures.json`. `24547e39a..9315526f8` is the v7.1.3 stamp: VERSION, the manifest, the card's `CARD_VERSION`, release notes, claim files and delivery rows.
- The full scoped gate ran green at `8ec4fcf98`, the merge of `24547e39a`.
- `9315526f8..dc0a170b6` adds one delivery row and one triage record; `entities.py` was re-run at this head and exits 0.
- After the stamp merge (`711bdb5bf`), the checks its delta reaches were re-run: `structure.py`, `entities.py`, `doc_claims.py`, `env_drift.py --claims-only`, `plan_view.py` then `card.mjs`, `card_drift.mjs`, and `card_browser.mjs`. All exit 0.

## Mutation proof

Each mutant was run in a separate worktree at the head, against the closure script named, and restored afterwards.
- M1, `ledger.py` `savings_months`: `calibration = max(1.0, calibration)` changed to `calibration = calibration`. `features.py` rc 1, 2 failures: `with wood configured a meter under the plan earns its saving: the calibration does not cancel it` and `with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied`.
- M2, `ledger.py`: `"savings_sek": None if old_basis else saved` changed to `saved`. `features.py` rc 1: `an old-basis row keeps both columns and states no saving and no percent`.
- M3, `notifier.py`: `saving_includes_wood` set to `False`. `features.py` rc 1: `the receipt event carries what the card states: no saving on the old basis, the percent unclipped, wood stated`.
- M4, `coordinator.py` `_grid_view`: `wood_configured=wood_furnace_on(...)` changed to `wood_configured=False`.
  - Before this PR it SURVIVED `features.py` (rc 0).
  - With the new pin, `features.py` rc 1: `the coordinator publishes the wood floor from the house's configuration, and no floor without wood` `[(50.0, 50.0)]`.
- M5, card `_savingsPageHtml`: `const woodNote = wood` changed to `false`. It survives `card.mjs`; `card_browser.mjs` rc 1: `a house with wood configured carries the disclaimer, painted within a phone's width`. This pin is already on main, so nothing is added.
- M6, the receipt disclaimer this PR adds (`receiptHtml`'s `receipt-wood-note`): at the merge base, without the fix, `card.mjs` rc 1: `the receipt's saving on a wood house says it includes wood's heat, not firewood's cost (en, sv); none without wood`. With the fix it passes.

## Null control

- A house without wood publishes the same row and no disclaimer.
  - The new `card.mjs` check asserts no `receipt-wood-note` on the same receipt without `wood_fuel.show_whatif`.
  - The new `features.py` check publishes 50.0 % on the plain coordinator: the calibration cancels, the same row as before.
  - `card_browser.mjs` asserts no table note without wood.
- Harness, no fire: plan 133.79 = drawn 133.79 kWh. Calibration equals `m` for `m` ≥ 1, and the error is 0.00.
- Harness, perturbation: the largest fire with the pump blind to it (meter = plan). The error from the heat reads +0.00 % at `m` 0.8, 1.0 and 1.2. Remove the meter's response to the unforeseen heat and the error goes to the null.
- Harness, flat prices with no fire: the row reads 7.59 % at `m` 1.0 and 7.59 % at `m` 1.2. That is not zero: it is the volume residual the `valve-flat` arm already accepts inside `FLAT_BAND_PCT` (10). It is scale-invariant in `m`, so the calibration adds nothing to it. The error figure is a kWh ratio and does not depend on price.
- One-step target probe (`--quick`, 12 kW fire 02:00-06:00 on a 15 °C wood tank, target re-solved from the current state): drawn 48.57 = plan 48.57 kWh, calibration = `m`. With the plan's 4-interval trajectory as target, the same fire reads drawn 48.23 against plan 50.20. The cut needs a hold.

## Figures

- Carry B grid, every row above: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant`, at 7a1429f0565c4aa2bda423904e3709ee4d4ed5ee (the first merge; see Head). It prints `RESULT wood_plant_error_m0.8/1.0/1.2` (mean, min, max, sd over 9 fires), the no-fire, flat and perturbation lines, and per fire the plan and drawn kWh and calibration.
- Mutation results: each mutant's closure script, `python3 tests/features.py`, `node tests/card.mjs` (after `python3 tests/plan_view.py`), and `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs`, with `PYTHONPATH=tests/hastub`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 10 script(s) run, 23 scoped out`. Every script in `scope.run` exits 0 at the head: `arch_score_head.py`, `deployment_shape.py`, `doc_claims.py`, `entities.py`, `features.py`, `harness_headers.py`, `plan_view.py`, `md_tables.mjs`, `card.mjs`, `card_drift.mjs`. So do `card_browser.mjs` (run by CI past the handoff) and the run_always lines `env_drift.py --claims-only`, `closure.py selftest` and `layout.py`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. No ratchet movement and no budget raise.
- Claim files and `VERSION`: `git diff --quiet origin/main -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt VERSION` exits 0. No golden fixture moves.

## Red checks

none: no pull request has run CI on this head yet; `prepr.sh` step 6d predicted no red (its log is cited below the run).

## Forward-carry

- The floor's cost on a wood house whose model reads the meter high (the +25.00 % reference at `m` 0.8, measured above) changes no later stage's method. It follows from two owner rulings as built, it is stated in `docs/how-it-works.md`, and changing it is the owner's call. Carry: dismissed: owner ruling territory, stated for the owner in the docs and this body

## Friction

frugal-routing: cost: a session plugin hook refuses a sixth inline read or command per prompt and resets only on a delegated subagent call, so this seat spawned about 10 scout or extractor agents just to keep reading files it was editing. Carry: dismissed: a session plugin outside this repository's policy
