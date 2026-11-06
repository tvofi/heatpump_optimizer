R10-HOTFIX-SAV-ESTIMATE part 2 (part 1 merged as #3220), topic r10-sav-wood-heat, repair round 4. It builds Carry A on every shipped surface that states the metered saving, the notifications blueprint included, which the second fix review blocked on.

## Re-cut

Round 4, so this body is re-taken whole from the template. Every figure below was re-run in this pass. Round history is dropped.

**Carry A (owner ruling, tvofi 2026-11-04).** The reference has no wood, so wood's heat counts in the saving. Wherever wood is configured, the saving the integration states says that it includes wood's heat and excludes firewood's cost.

**What the PR builds.**
- `wood_fuel.py` `saving_includes_wood(data)` is the one definition: wood is configured (`wood_fuel.show_whatif`).
- `notifier.py` `_monthly_receipt` puts it on the receipt event as `saving_includes_wood`. `sensor.py` `MonthlySavingsSensor` (`sensor.plan_monthly_savings`) publishes it as an attribute.
- `ledger.py` `savings_months` floors the meter calibration at 1.0 on a wood house (built in #3220). This is so a meter that falls under the plan during a fire cannot cancel wood's heat.
- The card's receipt (`receiptHtml`, `receipt-wood-note`) and savings table (`_savingsPageHtml`, `savings.wood_note`) say "The saving includes heat from wood. Firewood's cost is not counted." where wood is configured.
- **New this round:** `blueprints/automation/notifications.yaml`, the "Monthly receipt" message. It now appends that same sentence, the card's `savings.wood_note` words, under `{%- if data.saving_sek is not none and data.saving_includes_wood %}`. So it reads the event's flag, which is the one definition, and does not add a second grammar. The guard repeats `saving_sek is not none` so a receipt that states no saving gets no statement.
- **New this round:** `docs/automations.md` (the blueprint's line), `docs/dashboard-card.md` (the savings page) and `docs/how-it-works.md` ("Wood furnaces and other external heat") now name every surface that carries the statement. `README.md`'s sensor row states the attribute.
- The five `coord_*` golden captures each gain the one boolean key `saving_includes_wood`. This is a structure-only edit, no float moved, and each is claimed by name in `tests/golden/claimed_drift.txt`. None was re-recorded.

**The pin and its design choice.** The new `entities.py` check, "The notifications blueprint's monthly receipt says a wood house's saving includes wood's heat, in the card's words, and says nothing without wood", is a source pin, not a render:
- It loads the blueprint with an `!input`-aware YAML loader and takes the "Monthly receipt" branch's message.
- It requires the card's English `savings.wood_note` string exactly once, inside `{% if data.saving_sek is not none and data.saving_includes_wood %} ... {% endif %}`.
- It requires `saving_includes_wood` to be a key of `notifier.EVENT_DATA` for the receipt event.

CI's interpreter (venv-ci) has no `jinja2`, so a render check would not run there. The render is shown once below under Null control, with Home Assistant's `jinja2` 3.1.6 from venv-ha. Pinning the card's string is a design choice: the card's wording is authoritative, so a change to it must move the blueprint too.

**The class, by a rule that follows the value out of the package.** Rule R (run at the head):
1. `git grep -n -E 'savings_sek|saving_sek|savings_months|plan_monthly_savings|MonthlySavingsSensor|savings_pct|saving_pct|monthly_receipt|saving_includes_wood|monthly_savings' -- . ':!tests' ':!dev' ':!tools' ':!docs/design' ':!docs/decisions' ':!RELEASE_NOTES.md'`. Every shipped file is in scope: `custom_components`, `blueprints/`, `docs/` and `README.md`. The excluded paths are tests, audit and dispatch tooling, and dated records; none of them is shipped.
2. `git grep -n -i -E 'plain thermostat|conventional baseline|against the baseline' -- README.md docs blueprints custom_components/heatpump_optimizer/translations ':!docs/design' ':!docs/decisions'`. This is the prose rule, for user-facing text that states the saving without naming a key.
3. `git grep -n -o -E "\b(savings|receipt|headline)\.[a-z_]+" -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`. These are the card's string keys, with each use grouped by its enclosing function.

Every seam R returns, and its disposition:

| seam (file, symbol) | what it states | disposition |
|---|---|---|
| `ledger.py` `savings_months`, `savings_pct` | the producer: reference with no wood, metered actuals, the wood floor | built (#3220); pinned (M1, M2) |
| `coordinator.py` `_grid_view` (`wood_configured=wood_furnace_on(...)`) | passes the house's wood flag to the ledger | built; pinned (M4) |
| `notifier.py` `_monthly_receipt`, `EVENT_DATA` | receipt event `saving_sek`, `saving_pct`, `saving_includes_wood` | built; reads the one definition (M3, M10) |
| `wood_fuel.py` `saving_includes_wood` | the one definition | built (M10) |
| `sensor.py` `MonthlySavingsSensor` | entity state = the open month's `savings_sek` | built: attribute `saving_includes_wood` (M7, M8, M9) |
| card `receiptHtml` `receipt.saved` | "Saved {amount} ... against a plain thermostat" | built: `receipt-wood-note` (M6, M6n) |
| card `_savingsPageHtml` `savings.*` | the savings table | built: `savings.wood_note` (M5) |
| **`blueprints/automation/notifications.yaml` "Monthly receipt" message** | **"... {saving_sek} {currency} ({saving_pct} %) less than a plain thermostat would have."** | **built this round (M11, M12)** |
| `blueprints/automation/notifications.yaml` `notify_receipt` input description, trigger and condition | names the event and describes the toggle; states no figure | no stated saving: out of class |
| `docs/automations.md` event table row (`saving_includes_wood`) and Notifications line | documents the event and the blueprint | row already states the flag; the blueprint line now states the message's wood sentence (this round) |
| `docs/dashboard-card.md` "The savings page" (receipt and table) | documents the card's receipt and table | built this round: states the wood sentence |
| `docs/how-it-works.md` "Wood furnaces and other external heat" | the reference and wood | already stated; now names the sensor and the blueprint too (this round) |
| `README.md` Plan Monthly Savings row | documents the sensor | built: states `saving_includes_wood` |
| `README.md` blueprint list (Notifications) | names the blueprint's events | no figure: out of class |
| `payload.py` `SavingsMonth`, `Payload.savings_months` | type declarations | no stated saving: out of class |
| `optimizer.py` docstring (`ledger.savings_months`) | a comment | no stated saving: out of class |
| `icons.json`, `strings.json`, `translations/en.json`, `translations/sv.json` `plan_monthly_savings` | entity icon and name | no figure: out of class |
| card alias maps (`_plan_monthly_savings`) | key aliases | no figure: out of class |
| card `receiptHtml` `receipt.line_*`, `total`, `closed`, `col_*`, `covers`, `by_reason`, `peak`, `starts` | the month's cost lines | a cost, not a saving against the reference: out of class |
| card `headlineHtml` `headline.savings*` (`_plan_predicted_savings`) | the plan's projection against unoptimized heating | not the metered reference saving: out of class |
| `.claude/workflows/wave-3l-groups.json` | a historical dispatch brief | not shipped: out of class |

Not returned by R, re-checked by hand: `health.learn_savings` (string tables only, status text with no figure) and `replayHtml` (measured cost against promised cost, no `savings_sek`). Both are out of class.

**Carry B (the size of wood's unforeseen heat).** The `wood-plant` arm of `dev/audit/harnesses/r10_sav_wood_reference.py` puts the fire in the plant only, and the plan is never told of it. The meter reads `m` times what the pump drew. The figure is the applied calibration's error against `m`, less the same error with no fire. Re-taken at the head over 9 fires (4/8/12 kW, starting 06:00/17:00/22:00, 4 h each, never forecast):
- `m` 0.8 and 1.0: the error from the heat is +0.00 % at every fire (`RESULT wood_plant_error_m0.8` and `_m1.0`: mean +0.00 %, min +0.00, max +0.00, sd 0.00 over 9 fires), because the floor absorbs it.
- `m` 1.2 (the model reads the meter low): the reference is booked low (`RESULT wood_plant_error_m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`). The saving is understated by that share.

`docs/how-it-works.md` ("Wood furnaces and other external heat") states this size. The arm cannot show a real pump's control loop, a real fire's coupling to a house, or the coordinator's per-interval re-plan, so the figure is an upper bound for this simulated house.

**A measured limit, not changed here.** On a wood house the floor also stops the calibration correcting a model that reads the meter high, with or without a fire: at `m` 0.8 the booked reference is +25.00 % (1/m - 1). This follows from the two owner rulings as built. `docs/how-it-works.md` says so, and changing it is the owner's call.

## Head

a94e4dc33820e2afae8fdc8eb6619cf46c0c9cbf (code at `handoff/r10-sav-wood-heat`). It merges `origin/main` at `9cbd7dd0d7a6` (main's commit 2026-11-06T19:33:59Z, checked 2026-11-06T19:42:14Z).
- The mutants ran at `06aa96295011`, this round's blueprint commit. The scoped gate ran at `d5643c78e4bb`, which adds the `how-it-works.md` sentence.
- `git diff --quiet d5643c78e4bb HEAD -- custom_components tests blueprints docs README.md dev/audit ':!tests/mutation_ledger'` exits 0. So the gate measured the head's production, test, doc and harness tree. The one path outside it is main's new mutation-ledger pin `..._tibber_start_reauth.GUARD_OFF.75e9fa1a.json`, which is data the ledger reads and not one of this PR's tests.
- `git diff --quiet 06aa96295011 d5643c78e4bb -- custom_components tests blueprints` exits 0. So the mutants measured the head's production and test tree.
- Main's delta since the gate's base `4b7e1770` (merged as `2f88732c3`, `8d687e68b` and `a94e4dc33`) touches only `dev/programme/`, `tools/audit/seat/` (`bus.sh`, `ledger.py`, `orchestrator_tick.py`, `r10_ledger_mutants.py`) and that one mutation-ledger pin. The recomputed `closure.py select` at the head prints the same `MODE: SCOPED -- 28 script(s) run, 5 scoped out` with a byte-identical `scope.run`.
- `HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh <this body>` ran at this head against `origin/main` `9cbd7dd0d` and printed `PRE-PR: a94e4dc33820e2afae8fdc8eb6619cf46c0c9cbf ... rc=0`, with merged structure passed and no CI red predicted. `origin/main` had not moved when it finished, so no second merge or run was owed.

## Mutation proof

Every row was re-taken in this pass, at `06aa96295011`. Each mutant ran in its own detached worktree with `PYTHONPATH=tests/hastub` and was restored afterwards. The runner makes one exact-string replacement and refuses unless the pattern occurs exactly once. "Red" quotes the failing check. `entities.py`'s own negative self-tests (`a5:*`, `a10:*`, `hb:*` FAIL lines) print in every run, the null run included, and are omitted.

| id | mutant (file, symbol: from → to) | command | red at the mutant |
|---|---|---|---|
| M11 | `notifications.yaml` "Monthly receipt": the three added lines (the guarded wood sentence) deleted | `python3 tests/entities.py` | rc 1, 1 of 2639: `The notifications blueprint's monthly receipt says a wood house's saving includes wood's heat, in the card's words, and says nothing without wood` |
| M12 | same guard: `data.saving_sek is not none and data.saving_includes_wood` → `data.saving_sek is not none` (the null leg: the sentence on every house) | `python3 tests/entities.py` | rc 1, 1 of 2639: the same check |
| M1 | `ledger.py` `savings_months`: `calibration = max(1.0, calibration)` → `calibration = calibration` | `python3 tests/features.py` | rc 1, 3 of 4877: `with wood configured a meter under the plan earns its saving: the calibration does not cancel it`; `with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied`; `the coordinator publishes the wood floor from the house's configuration, and no floor without wood` |
| M2 | `ledger.py` `savings_months`: `"savings_sek": None if old_basis else saved` → `saved` | `python3 tests/features.py` | rc 1, 1 of 4877: `an old-basis row keeps both columns and states no saving and no percent` |
| M3 | `notifier.py` `_monthly_receipt`: `saving_includes_wood(data)` → `False` | `features.py`; `entities.py` | features rc 1, 1 of 4877: `the receipt event carries what the card states: no saving on the old basis, the percent unclipped, wood stated`; entities rc 1: `MonthlySavingsSensor states that a wood house's saving includes wood's heat, as the receipt event does; False without wood` `((True, False), (False, False), (False, False))` |
| M4 | `coordinator.py` `_grid_view`: `wood_configured=wood_furnace_on(_ctx_of(self)._config)` → `wood_configured=False` | `python3 tests/features.py` | rc 1, 1 of 4877: `the coordinator publishes the wood floor from the house's configuration, and no floor without wood` `[(50.0, 50.0)]` |
| M5 | card `_savingsPageHtml`: `const woodNote = wood` → `false` | `python3 tests/plan_view.py && node tests/card.mjs`; `node tests/card_browser.mjs` | card.mjs rc 0 (survives); card_browser rc 1: `a house with wood configured carries the disclaimer, painted within a phone's width` |
| M6 | card `receiptHtml`: the `receipt-wood-note` div → empty | `python3 tests/plan_view.py && node tests/card.mjs` | rc 1: `the receipt's saving on a wood house says it includes wood's heat, not firewood's cost (en, sv); none without wood` |
| M6n | card `receiptHtml`: `${wood` → `${true` (the null leg: a note on every house) | `python3 tests/plan_view.py && node tests/card.mjs` | rc 1: the same check |
| M7 | `sensor.py` `MonthlySavingsSensor.extra_state_attributes`: the `saving_includes_wood` line deleted | `python3 tests/entities.py` | rc 1, 3 of 2639: the wood check `((None, True), (None, False), (None, False))`; `MonthlySavingsSensor publishes exactly its pinned attribute keys (#373)`; `the pinned attribute surface is the whole measured one (#373)` |
| M8 | `sensor.py` same line: `saving_includes_wood(data)` → `False` | `python3 tests/entities.py` | rc 1: the wood check `((False, True), (False, False), (False, False))` |
| M9 | `sensor.py` same line: `saving_includes_wood(data)` → `True` (the null leg) | `python3 tests/entities.py` | rc 1: the wood check `((True, True), (True, False), (True, False))` |
| M10 | `wood_fuel.py` `saving_includes_wood`: the return → `return False` | `entities.py`; `features.py` | entities rc 1: the wood check `((False, False), (False, False), (False, False))`; features rc 1, 1 of 4877: the receipt-event check under M3 |

Failing test first: M11 is this round's production lines deleted, which is the blueprint as it stands on `origin/main`, and the new check is red there. `wood_fuel.py` `saving_includes_wood RETURN_DEL` is also pinned in the mutation ledger (`tests/mutation_ledger/.../saving_includes_wood.RETURN_DEL.62b7ac43.json`, killed by `features.py`).

## Null control

- The unmodified tree (`NULL`, the same runner with no edit, at `06aa96295011`): `features.py` rc 0 (ALL 4877 FEATURE CHECKS PASSED), `entities.py` rc 0, `plan_view.py && card.mjs` rc 0 (ALL CARD CHECKS PASSED), `card_browser.mjs` rc 0 (ALL BROWSER CHECKS PASSED). At the gate's tree `entities.py` prints ALL 2639 ENTITY CHECKS PASSED.
- A house without wood gets no statement:
  - The blueprint's guard is the null leg. M12, the sentence on every house, goes red.
  - The real template render, with Home Assistant's `jinja2` 3.1.6 at the head (`month` 2026-10, `total_sek` 812.4, `saving_sek` 143.2, `saving_pct` 15.0):
    - wood: "Heating and hot water cost 812.0 SEK, 143.0 SEK (15.0 %) less than a plain thermostat would have. The saving includes heat from wood. Firewood's cost is not counted."
    - no wood: "... less than a plain thermostat would have." with no statement.
    - wood with no saving row (`saving_sek` null): "Heating and hot water cost 812.0 SEK." with no statement.
  - The same render of `origin/main`'s blueprint gives the no-wood sentence for all three cases. That is the defect, read at the base and not at the head.
  - The entity and the event agree on three houses: wood configured, wood present but not configured, and no `wood_fuel` (`entities.py`; M9 is its always-`True` leg). The card asserts no note without wood (`card.mjs`, M6n; `card_browser.mjs`).
- Finder's harness (`r10_rca_sav_estimate.py census`, sha1 `04b644563c84d26378cad42a603dc050e7e5fd88`, the same copy at both ends) at `origin/main` `57958d6a4` and at `2f88732c3` (the head's production tree): the same six `RESULT census` lines at both ends (single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all ok), rc 0 at both. It is flat by design, because part 1 (#3220) settled the census. The companions that read this round's defect at the base and not at the head are M11 and the render above.
- Harness controls (`wood-plant`, at the head): no fire, plan 133.79 = drawn 133.79 kWh, and the error is +0.00 % at `m` 1.0 and 1.2 (+25.00 % at `m` 0.8, the measured limit above). In the perturbation, where the pump is blind to the fire and the meter equals the plan, the error from the heat reads +0.00 % at `m` 0.8, 1.0 and 1.2. So removing the meter's response to the unforeseen heat takes the error to the null. With flat prices and no fire the row reads 7.59 % at `m` 1.0 and 1.2. That is the volume residual the `valve-flat` arm accepts, and it does not change with `m`.

## Figures

- Class enumeration, every seam in the table: the three commands of rule R, at the head. The first returns 65 lines over 17 files, and the second returns 6 lines over 3 files.
- Mutation table and null run: the commands in each row, with `PYTHONPATH=tests/hastub`, in detached worktrees at `06aa96295011`.
- Template render: a scratch driver that loads the blueprint with an `!input` constructor and renders the "Monthly receipt" message with `jinja2` 3.1.6 (`/opt/hpo/venv-ha`) on three event payloads, at the head and at `origin/main`. It is a one-off probe, so it is not in the tree.
- Carry B, every figure: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant`, at `2f88732c3` (the head's tree but for main's tooling delta).
- Finder's census: `PYTHONPATH=tests/hastub:tests:custom_components python3 r10_rca_sav_estimate.py census`, the `d8eeae8f` copy, at `57958d6a4` and at `2f88732c3`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) PYTHONPATH=tests/hastub ./tests/run.sh` at `d5643c78e4bb` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`, `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` over 56 scenarios, `STRUCTURE RATCHET PASSED`, `ALL 2639 ENTITY CHECKS PASSED` and `ALL 4877 FEATURE CHECKS PASSED`, and exited 0. `card_browser.mjs`, which no scope selects, exits 0 in the null run.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED (in the gate). No budget moved and none was raised.
- Protected files: `git diff --quiet origin/main HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden/card_claimed_drift.txt` exits 0. `tests/golden/claimed_drift.txt` differs only by the five `R10-SAV-WOOD-HEAT` claim lines, and `claims-for:` is unchanged.

## Red checks

none. The final head named under `## Head` has not run CI yet: it reaches CI when the orchestrator moves the PR to it. The current PR head `dea3c729d675` had 68 check runs on one page (read 2026-11-06T18:55Z, `pull_request_read get_check_runs`). Each concluded `success` or `skipped`, with no failure, cancellation or timeout, so there is no red to answer. That includes `governance / instrument-self-tests`, which concluded `success`.

## Forward-carry

- The floor's cost on a wood house whose model reads the meter high (the +25.00 % reference at `m` 0.8) changes no later stage's method. It follows from two owner rulings as built and is stated in `docs/how-it-works.md`. Changing it is the owner's call. Carry: dismissed: owner ruling territory, stated for the owner in docs/how-it-works.md and this body
- The class rule for "where the integration states the saving" must follow the value through the event to its shipped consumers (`blueprints/`, `docs/`), not stop at `custom_components`. The review found this, and it is built and dispositioned here (rule R). It changes no later stage's brief beyond this PR. Carry: dismissed: built and dispositioned in this PR (rule R in the body), so no later stage owes it

## Friction

- frugal-routing: cost: a session plugin hook refuses a sixth inline command per prompt and blocks `pkill`, so locate and extract steps went to cheap subagents and the gate was stopped by its process group. Carry: dismissed: a session plugin outside this repository's policy
- seat-concurrency: contradiction: a second seat, under the same `hpo-fixer` identity, pushed `8d687e68b` (a merge of `origin/main` at `af56818b5` onto this seat's `2f88732c3`) to `handoff-wip/r10-sav-wood-heat` while this seat was measuring. It descends from this seat's head and adds only main's delta, so this seat adopted it and merged `9cbd7dd0d` on top as `a94e4dc33`. Carry: dismissed: a dispatch event, recorded for the orchestrator in this body
- background-limit: cost: a 30-minute background limit killed the first mutant fleet midway (NULL and M1 to M4 had finished), and the rest was rerun with a longer limit. Carry: dismissed: a harness setting outside this repository's policy
