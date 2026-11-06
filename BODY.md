R10-HOTFIX-SAV-ESTIMATE part 2 (part 1 merged as #3220), topic r10-sav-wood-heat, repair round 2. It builds the two open carries and the seam the first fix review blocked on.

**Carry A (owner ruling, tvofi 2026-11-04).** The reference has no wood, and wood's heat counts in the saving. Wherever wood is configured, the saving the integration states says that it includes wood's heat and excludes firewood's cost.

**The block (review of `622be7c5`, class-open).** `sensor.py` `MonthlySavingsSensor` (`sensor.plan_monthly_savings`) published the wood house's metered saving with no wood statement. This round builds it:
- `wood_fuel.py` `saving_includes_wood(data)` is now the one definition. Both the receipt event (`notifier.py` `_monthly_receipt`) and the entity read it, so the entity does not carry a second grammar.
- The entity gains the attribute `saving_includes_wood`. It is `True` where wood is configured (`wood_fuel.show_whatif`) and `False` otherwise, as on the notifier.
- The README's sensor row states the attribute.
- The five `coord_*` golden captures each gain that one boolean key. This is a structure-only edit of the committed files, and no float moved. They are claimed by name in `tests/golden/claimed_drift.txt` and were never re-recorded.

**The class, by my own rule.** The enumeration rule (two commands, run at the head):
- `git grep -n -E 'savings_sek|savings_months|plan_monthly_savings|MonthlySavingsSensor' -- custom_components ':!*/translations/*'`
- `git grep -n -o -E "\b(savings|receipt|headline)\.[a-z_]+" -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`, with string-table definitions excluded and each use site grouped by its enclosing function.

Each returned seam and its disposition:

| seam (enclosing symbol) | what it states | disposition |
|---|---|---|
| `ledger.py` `savings_months` | the producer: reference with no wood, actuals metered, the floor | built (#3220); pinned (M1, M2) |
| `coordinator.py` `_grid_view` (`wood_configured=wood_furnace_on(...)`) | passes the house's wood flag to the ledger | built; pin added in round 1 (M4) |
| `notifier.py` `_monthly_receipt` | receipt event `saving_sek` and `saving_includes_wood` | built; now reads the one definition (M3, M10) |
| **`sensor.py` `MonthlySavingsSensor`** | **entity state = the first estimated row's `savings_sek`** | **built this round** (M7, M8, M9) |
| `payload.py` `SavingsMonth`, `Payload.savings_months` | type declarations | no stated saving: out of class |
| `optimizer.py` docstring (`ledger.savings_months`) | a comment | no stated saving: out of class |
| `icons.json`, `strings.json` `plan_monthly_savings` | entity icon and name | no figure: out of class |
| card entity alias maps (`_plan_monthly_savings`) | key aliases | no figure: out of class |
| card `receiptHtml` `receipt.saved` | "Saved {amount} ... against a plain thermostat" | built in round 1: `receipt-wood-note` (M6) |
| card `receiptHtml` `receipt.line_*`, `total`, `closed`, `col_*`, `covers`, `by_reason`, `peak`, `starts` | the month's cost lines and totals | a cost, not a saving against the reference: out of class |
| card `_savingsPageHtml` `savings.*` | the savings table | built: `savings.wood_note` (M5) |
| card `headlineHtml` `headline.savings*` (`_plan_predicted_savings`) | the plan's projection against unoptimized heating | not the metered reference saving: out of class (agrees with the review) |
| card `_render` `headline.score*` | the optimization score | no saving figure: out of class |

The review's other two out-of-class surfaces were re-checked, and this round agrees:
- `replayHtml` reads no `savings_sek` and no `savings.*` key. The first rule does not return it, and it states measured cost against promised cost.
- `health.learn_savings` appears only in the string tables; the `savings|receipt|headline` key rule does not return it. It shows status text with no figure.

**Carry B (the size of wood's unforeseen heat).** The `wood-plant` arm in `dev/audit/harnesses/r10_sav_wood_reference.py` puts the fire in the plant only, and the plan is never told of it. The plant pump follows the plan's own buffer trajectory over each `REPLAN` hold, so it draws less once wood carries the draw. The meter reads `m` times what the pump drew. The figure is the applied calibration's error against `m`, less the same error with no fire.

Re-taken at the head over 9 fires (4/8/12 kW, starting 06:00/17:00/22:00, 4 h each, never forecast):
- `m` 0.8 and 1.0: the error from the heat is 0.00 at every fire, because the floor absorbs it.
- `m` 1.2 (the model reads the meter low): the reference is booked low by mean 1.95 %, min 0, max 4.50 %, sd 1.47 (`RESULT wood_plant_error_m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`). The saving is understated by that share.

`docs/how-it-works.md` ("Wood furnaces and other external heat") states this size.
- The arm cannot show a real pump's control loop, a real fire's coupling to a house, or the coordinator's per-interval re-plan, so the figure is an upper bound for this simulated house.
- An install would need the heat pump's own electric sub-meter beside a wood-tank heat meter, or a logged fire start and end, to separate the meter's fall into the model's error and wood's heat.

**A measured limit, not changed here.** On a wood house the floor also stops the calibration correcting a model that reads the meter high, with or without a fire. At `m` 0.8 the booked reference is +25.00 % (that is 1/m - 1), and the row reads 44.9 % against 31.1 %. This follows from the two owner rulings as built. The docs paragraph says so, and changing it is the owner's call.

**Identity.** The commits before this round's merge, and the ledger pin `c9c846e89`, were authored as `seat` by earlier seats on this topic; this seat's own commit is the merge `37848a50a`, as `hpo-fixer`. A second seat pushed `c9c846e89` and the main merges `de4c0b2d8` and `a3a22950e` to `handoff-wip` while this seat was measuring. Its content beyond this seat's measured head `37848a50a` is that one ledger pin and main's tooling delta. This seat adopted it and merged `817c2b169` on top.

## Head

49c4bce874edbfb3fff2cafcf5c7ffc8ce7beecb (code at `handoff/r10-sav-wood-heat`). It merges `origin/main` at `817c2b169` (main's commit 2026-11-06T14:41:43Z, checked 2026-11-06T14:51:55Z).
- `git diff --quiet 37848a50a 49c4bce87 -- custom_components tests ':!tests/mutation_ledger' README.md docs dev/audit` exits 0. So the mutants and the scoped gate, which ran at `37848a50a` (the merge of `b36679cea`), measured the same production, test, doc and harness tree.
- `b36679cea..817c2b169` touches only `.github/workflows/release.yml`, `tools/release/stamp.py`, `tools/audit/seat/beat_jobs*` and its instrument note, `dev/programme/carries/carry-201.json` and delivery rows. The recomputed scope (`closure.py select`) is the same `scope.run`, `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- At `de4c0b2d8` (the merge of `33e60b5b7`), `structure.py` (STRUCTURE RATCHET PASSED), `entities.py` (ALL 2638 ENTITY CHECKS PASSED), `env_drift.py --claims-only`, `doc_claims.py` and `closure.py selftest` were re-run, and all exit 0.
- `HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh <this body>` ran at this head against `817c2b169`: `PRE-PR: 49c4bce874edbfb3fff2cafcf5c7ffc8ce7beecb ... rc=0`, merged structure passed, CI predict none. origin/main had not moved when it finished.

## Mutation proof

Every row was re-taken in this round. Each mutant was applied in its own worktree at `37848a50a` (the tree equal to the head, as above) and run against the script named, with `PYTHONPATH=tests/hastub`; the worktree was restored afterwards. Runner: one exact-string replacement per mutant, refused unless the pattern occurs exactly once. "Red" quotes the failing check; the `a3:*` FAIL lines both logs print are `entities.py`'s own negative self-tests and appear in the null run too.

| id | mutant (file, symbol: from → to) | command | red at the mutant |
|---|---|---|---|
| M1 | `ledger.py` `savings_months`: `calibration = max(1.0, calibration)` → `calibration = calibration` | `python3 tests/features.py` | rc 1, 3 of 4877 failed: `with wood configured a meter under the plan earns its saving: the calibration does not cancel it`; `with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied`; `the coordinator publishes the wood floor from the house's configuration, and no floor without wood` |
| M2 | `ledger.py` `savings_months`: `"savings_sek": None if old_basis else saved` → `saved` | `python3 tests/features.py` | rc 1, 1 failed: `an old-basis row keeps both columns and states no saving and no percent` |
| M3 | `notifier.py` `_monthly_receipt`: `saving_includes_wood(data)` → `False` | `python3 tests/features.py`; `python3 tests/entities.py` | features rc 1: `the receipt event carries what the card states: no saving on the old basis, the percent unclipped, wood stated`; entities rc 1, 1 of 2638: `MonthlySavingsSensor states that a wood house's saving includes wood's heat, as the receipt event does; False without wood` `((True, False), ...)` |
| M4 | `coordinator.py` `_grid_view`: `wood_configured=wood_furnace_on(_ctx_of(self)._config)` → `wood_configured=False` | `python3 tests/features.py` | rc 1, 1 failed: `the coordinator publishes the wood floor from the house's configuration, and no floor without wood` `[(50.0, 50.0)]` |
| M5 | card `_savingsPageHtml`: `const woodNote = wood` → `false` | `python3 tests/plan_view.py && node tests/card.mjs`; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` | card.mjs rc 0 (survives); card_browser rc 1: `a house with wood configured carries the disclaimer, painted within a phone's width` |
| M6 | card `receiptHtml`: the `receipt-wood-note` div → empty | `python3 tests/plan_view.py && node tests/card.mjs` | rc 1: `the receipt's saving on a wood house says it includes wood's heat, not firewood's cost (en, sv); none without wood` |
| M7 | `sensor.py` `MonthlySavingsSensor.extra_state_attributes`: the `saving_includes_wood` line deleted | `python3 tests/entities.py` | rc 1, 3 of 2638: the wood check `((None, True), (None, False), (None, False))`; `MonthlySavingsSensor publishes exactly its pinned attribute keys (#373)`; `the pinned attribute surface is the whole measured one (#373)` |
| M8 | `sensor.py` same line: `saving_includes_wood(data)` → `False` | `python3 tests/entities.py` | rc 1, 1 of 2638: the wood check `((False, True), (False, False), (False, False))` |
| M9 | `sensor.py` same line: `saving_includes_wood(data)` → `True` (the null leg) | `python3 tests/entities.py` | rc 1, 1 of 2638: the wood check `((True, True), (True, False), (True, False))` |
| M10 | `wood_fuel.py` `saving_includes_wood`: the return → `return False` | `python3 tests/entities.py`; `python3 tests/features.py` | entities rc 1, 1 of 2638: the wood check `((False, False), ...)`; features rc 1: the receipt-event check above |

Failing test first: M7 is the fix's production line deleted, which is the tree before this round's sensor change, and the new `entities.py` check fails there. `wood_fuel.py` `saving_includes_wood RETURN_DEL` is also pinned in the mutation ledger (`tests/mutation_ledger/.../saving_includes_wood.RETURN_DEL.62b7ac43.json`, killed by `features.py`).

## Null control

- The unmodified tree (`NULL`, the same runner with no edit, at `37848a50a`): `features.py` rc 0 (ALL 4877 FEATURE CHECKS PASSED), `entities.py` rc 0 (ALL 2638 ENTITY CHECKS PASSED), `plan_view.py && card.mjs` rc 0, `card_browser.mjs` rc 0.
- A house without wood carries no statement:
  - The new `entities.py` check builds the entity and the receipt event for three houses: wood configured and ready, wood present but not configured (`show_whatif` false), and no `wood_fuel` at all. It requires `(True, True), (False, False), (False, False)`, so the entity and the event agree on every house.
  - M9 (always `True`) is the leg that would pass were the null case not checked, and it goes red.
  - `card.mjs` asserts no `receipt-wood-note` on the same receipt without wood; `card_browser.mjs` asserts no table note without wood.
- Harness, no fire: plan 133.79 = drawn 133.79 kWh, and the error is 0.00 at `m` 1.0 and 1.2.
- Harness, perturbation (the largest fire with the pump blind to it, meter = plan): the error from the heat reads +0.00 % at `m` 0.8, 1.0 and 1.2; remove the meter's response to the unforeseen heat and the error goes to the null.
- Harness, flat prices with no fire: the row reads 7.59 % at `m` 1.0 and 1.2. That is the volume residual the `valve-flat` arm already accepts inside `FLAT_BAND_PCT`, and it is scale-invariant in `m`.
- Finder's harness (`r10_rca_sav_estimate.py census`, the copy at `d8eeae8f`, sha1 `04b644563c84d26378cad42a603dc050e7e5fd88`), run at the merge base `b36679cea` and at the head: the same six `RESULT census` lines at both ends (single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all ok), rc 0. It is flat at both ends by design, because part 1 (#3220) settled the census. The companion that reads this round's defect at the base and not at the head is the `entities.py` check (M7 is the base).

## Figures

- Class enumeration, every seam in the table above: the two `git grep` commands quoted under "The class, by my own rule", run at `37848a50a`; the first returns 30 lines over 9 files.
- Mutation table and null run: the commands in each row, with `PYTHONPATH=tests/hastub`, in worktrees at `37848a50a`.
- Carry B, every figure: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant`, at `37848a50a`. It prints `RESULT wood_plant_error_m0.8/1.0/1.2` (mean, min, max, sd over 9 fires), the no-fire, flat and perturbation lines, and per fire the plan and drawn kWh and calibration.
- Finder's census: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py census`, the `d8eeae8f` copy, at `b36679cea` and `37848a50a`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at `37848a50a` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`, `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` over 56 scenarios, `STRUCTURE RATCHET PASSED`, and exited 0. `card_browser.mjs`, which no scope selects, exits 0 in the null run.
- `python3 tests/structure.py` at the head: STRUCTURE RATCHET PASSED. No budget moved and none was raised.
- Protected files: `git diff --quiet origin/main HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden/card_claimed_drift.txt` exits 0. `tests/golden/claimed_drift.txt` differs only by the five `R10-SAV-WOOD-HEAT` claim lines; `claims-for:` is unchanged at the live `VERSION`.

## Red checks

none: the final head `49c4bce87` has not run CI. The previous PR head `622be7c5` had one red, the required `gate` context. Its two `CI edit` gate jobs each printed `FAIL run(s) [<the other edit run>] at this head are still being judged; their gate decides` and deferred to each other, while the `CI code` gate passed. That is CI tooling (`tools/ci/gate.py`), not this diff, and that head is superseded.

## Forward-carry

- The floor's cost on a wood house whose model reads the meter high (the +25.00 % reference at `m` 0.8, measured above) changes no later stage's method. It follows from two owner rulings as built and is stated in `docs/how-it-works.md`. Changing it is the owner's call. Carry: dismissed: owner ruling territory, stated for the owner in docs/how-it-works.md and this body

## Friction

- seat-concurrency: contradiction: a second seat pushed `c9c846e89`, `de4c0b2d8` and `a3a22950e` to `handoff-wip/r10-sav-wood-heat` while this resumed seat was measuring; the brief had called the earlier seat stalled. This seat adopted that head, since it was a superset of its own push. Carry: dismissed: a dispatch event, recorded for the orchestrator in this body
- frugal-routing: cost: a session plugin hook refuses a sixth inline command per prompt, so locate and extract steps went to cheap subagents. Carry: dismissed: a session plugin outside this repository's policy
- seat-identity: contradiction: the payload's setup line pins the identity `seat`, its brief says never to commit as `seat`, and the session hook exports `GIT_AUTHOR_NAME=seat`, which overrides `git config`. This seat committed as `hpo-fixer` by environment override. Carry: dismissed: a dispatch-payload wording, recorded for the orchestrator in this body
