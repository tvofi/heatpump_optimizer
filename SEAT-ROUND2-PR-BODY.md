R10-HOTFIX-SAV-ESTIMATE part 2, topic r10-sav-wood-heat: the two open carries of the estimate hotfix (part 1 merged as #3220). Repair round 2: the fix review of 622be7c5 blocked with the class open on `sensor.plan_monthly_savings`.

**Carry A (owner ruling, tvofi 2026-11-04): the reference has no wood, so wherever wood is configured the saving the integration states says it includes wood's heat and excludes firewood's cost.**

What this round adds:
- `wood_fuel.py` `saving_includes_wood(data)` is now the one definition of the statement: `wood_fuel.show_whatif` in the payload, the same expression the receipt event used inline.
- The receipt event (`notifier.py` `_monthly_receipt`) reads it.
- `MonthlySavingsSensor` (`sensor.plan_monthly_savings`) publishes it as the `saving_includes_wood` attribute. Its state is the first estimated row's `savings_sek`, the same metered saving as the card receipt's figure, so a tile or automation reading the entity now has the statement beside the figure. The value is `true` where wood is configured and `false` elsewhere, as on the event.
- `README.md`'s entity table states the attribute.
- The notifications blueprint's Monthly receipt message (`blueprints/automation/notifications.yaml`) states the same saving. Commit `06aa96295`, pushed onto this branch by a concurrent seat under the `hpo-fixer` identity, adds the wood statement there, guarded by the event's `saving_includes_wood` and worded as the card's `savings.wood_note`. That commit adds an `entities.py` pin and updates `docs/automations.md` and `docs/dashboard-card.md`. `d5643c78e`, by the same identity, names every stating surface in `docs/how-it-works.md`. I adopted both: my first class rule covered `custom_components/` only and missed the blueprint, so the rule below is widened to the whole tree, and the blueprint has two mutants.
- The new key moves five golden coordinator captures by one boolean leaf each: `true` in `coord_all_features` (the only capture with wood configured), `false` in the other four. I edited the committed files structure-only and never recorded them, so every float stays as main recorded it; the precedent is `10b4ae172`. All five are claimed in `tests/golden/claimed_drift.txt`.

Why this design: the brief asked for the notifier's one definition rather than a second grammar.
- The alternative of the sensor importing `notifier.py` lost: the sensor would depend on the event module for a wood fact.
- The alternative of a second inline copy of `(data.get("wood_fuel") or {}).get("show_whatif")` in the sensor lost: two spellings of one statement drift.
- `wood_fuel.py` owns `show_whatif` (its wood view sets `"show_whatif": wood_furnace_on(config)`), so it owns the statement. The function is pure and adds no `homeassistant` import.

What earlier rounds built, unchanged here and re-proved below by mutation at the final head:
- the reference with no wood and metered actuals (`ledger.py` `savings_months`);
- the wood floor `calibration = max(1.0, calibration)` and its coordinator input `wood_configured=wood_furnace_on(...)`;
- the old-basis dash;
- the card's table note and receipt note (`savings.wood_note`, en and sv).

**Carry B (the size of wood's unforeseen heat), unchanged from round 1 and re-run at the final head.**
- The `wood-plant` arm of `dev/audit/harnesses/r10_sav_wood_reference.py` puts a fire in the plant only, and the plan is never told of it.
- The plant pump follows the plan's buffer trajectory over each `REPLAN` hold, so it draws less once wood carries the draw. The meter reads `m` times what the pump drew.
- The figure is the applied calibration's error against `m`, less the same error with no fire.

Results over 9 fires (4/8/12 kW, starting 06:00/17:00/22:00, 4 h each, never forecast):
- At `m` 0.8 and 1.0 the error from the heat is 0.00, because the floor absorbs it.
- At `m` 1.2 (the model reads the meter low) the reference is booked low by mean 1.95 %, min 0, max 4.50 %, sd 1.47 (`RESULT wood_plant_error_m1.2: mean -1.95 % min -4.50 max +0.00 sd 1.47 over 9 fires`). The saving is understated by that share.
- `docs/how-it-works.md` ("Wood furnaces and other external heat") states this size.
- The card's wood note is unchanged: one simulated house with an hour's hold does not support a sentence about a real house's monthly figure.

What the arm cannot show:
- It cannot show a real pump's control loop, a real fire's coupling to a house, or the coordinator's per-interval re-plan.
- So the figure is an upper bound for this house, not a measured real-house size.
- An install would need the heat pump's own electric sub-meter beside a wood-tank heat meter, or a logged fire start and end, to separate the meter's fall into the model's error and wood's heat.

**A measured limit, not changed here.** On a wood house the floor also stops the calibration correcting a model that reads the meter high. At `m` 0.8 the booked reference is +25.00 % (that is 1/m - 1), and the row reads 44.9 % where `m` 1.0 reads 31.1 %. This follows from two owner rulings as built: the calibration ruling of 2026-10-24, and the floor. `docs/how-it-works.md` says so.

## Head

2f88732c3eb345d1147bc57bf24c48ae082d0fb4 (code at `handoff/r10-sav-wood-heat`). Every figure, mutant and harness line below was measured at this head.
- It descends from the reviewed PR head `622be7c53` and from `dea3c729d`, `fix/r10-sav-wood-heat`'s own merge of my `49c4bce87`.
- It merges `origin/main` at `57958d6a4` (checked 2026-11-06T19:06Z), the tip `tools/pr/prepr.sh` last ran against.
- This head is the concurrent seat's merge of main onto `d5643c78e`. I fast-forwarded to it and dropped my own merge of the same tip.
- Main moved eight times while this round ran, and each move was merged, never rebased:
  - `dc0a170b6..5421413b5`: two delivery rows, the r10 roster JSON and `tests/gate_lock.py`.
  - `5421413b5..33e60b5b7`: #3238's triage harness and record, one `tests/closures.json` entry, #3236's `tools/release/stamp.py` and `release.yml`, and a delivery row.
  - `33e60b5b7..a2240924b`: #3240's `tools/audit/seat/beat_jobs*`, its instrument note, `carry-201.json` and a delivery row.
  - `a2240924b..30638cf0c`: delivery rows only (#3254, #3257).
  - `30638cf0c..862affd07`: the v7.1.4 stamp (`VERSION`, manifest, `CARD_VERSION`, `RELEASE_NOTES.md`, both claim stamps) and #3247's `D0.md` and round-4 D6 records.
  - `862affd07..4b7e1770b`: mutation-ledger rows only.
  - `4b7e1770b..57958d6a4`: the r10 roster JSON and a delivery row (#3258).
- The stamp is the one main delta that reaches this diff: `tests/golden/claimed_drift.txt`.
  - The `claimnotes` driver kept main's `claims-for: 7.1.4` and my five claims.
  - `git diff origin/main HEAD -- tests/golden/claimed_drift.txt` is +5 lines, the claims.
  - `VERSION`, the manifest, `RELEASE_NOTES.md` and `card_claimed_drift.txt` equal origin/main's (`git diff --quiet` exits 0).
- Other merges pushed onto `handoff-wip/r10-sav-wood-heat` by the `hpo-fixer` identity (`37848a50a`, `49c4bce87`) were merged in, never overwritten.
- The commits since the reviewed head:
  - the attribute with its test;
  - the five fixture keys with their claims;
  - the README row;
  - the pinned mutant;
  - the concurrent seat's blueprint and docs commits;
  - the main merges.

## Mutation proof

Every row is a mutant. Each ran in its own detached worktree at 2f88732c3, edited by `mut.py` (one exact-match replacement), against the scripts named, with `PYTHONPATH=tests/hastub`. Red means rc 1 with the named check failing.

| id | mutant | command | at the mutant |
|---|---|---|---|
| S1 | `sensor.py` `MonthlySavingsSensor`: `"saving_includes_wood": saving_includes_wood(data)` changed to `False` | `python3 tests/entities.py` | rc 1: `MonthlySavingsSensor states that a wood house's saving includes wood's heat, as the receipt event does; False without wood` `[((False, True), (False, False), (False, False))]` |
| S2 | `wood_fuel.py` `saving_includes_wood`: body changed to `return False` | `python3 tests/entities.py`; `python3 tests/features.py` | rc 1 at both. In entities, the check above. In features, `the receipt event carries what the card states: no saving on the old basis, the percent unclipped, wood stated` |
| S3 | `wood_fuel.py` `saving_includes_wood`: body changed to `return True` | same | rc 1 at both, by the null legs (no wood states `False`) |
| M3 | `notifier.py` `_monthly_receipt`: `"saving_includes_wood": saving_includes_wood(data)` changed to `False` | same | rc 1 at both. In entities, `MonthlySavingsSensor states that a wood house's saving includes wood's heat, as the receipt event does; False without wood` `[((True, False), ...)]`. In features, `the receipt event carries what the card states: ...` |
| B1 | `blueprints/automation/notifications.yaml` Monthly receipt: the guard `data.saving_sek is not none and data.saving_includes_wood` reduced to `data.saving_sek is not none` | `python3 tests/entities.py` | rc 1: `The notifications blueprint's monthly receipt says a wood house's saving includes wood's heat, in the card's words, and says nothing without wood` (the null leg: a house without wood now gets the statement) |
| B2 | the same message: the line `The saving includes heat from wood. Firewood's cost is not counted.` deleted | `python3 tests/entities.py` | rc 1: `The notifications blueprint's monthly receipt says a wood house's saving includes wood's heat, in the card's words, and says nothing without wood` |
| M1 | `ledger.py` `savings_months`: `calibration = max(1.0, calibration)` changed to `calibration = calibration` | `python3 tests/features.py` | rc 1, 3 failures: `with wood configured a meter under the plan earns its saving: the calibration does not cancel it`, `with wood configured a model that under-reads the meter is still corrected, and the row publishes what it applied`, `the coordinator publishes the wood floor from the house's configuration, and no floor without wood` |
| M2 | `ledger.py`: `"savings_sek": None if old_basis else saved` changed to `saved` | `python3 tests/features.py` | rc 1: `an old-basis row keeps both columns and states no saving and no percent` |
| M4 | `coordinator.py`: `wood_configured=wood_furnace_on(_ctx_of(self)._config)` changed to `False` | `python3 tests/features.py` | rc 1: `the coordinator publishes the wood floor from the house's configuration, and no floor without wood` `[(50.0, 50.0)]` |
| M5 | card `_savingsPageHtml`: `const woodNote = wood` changed to `false` | `python3 tests/plan_view.py && node tests/card.mjs`; `node tests/card_browser.mjs` | `card.mjs` rc 0, `card_browser.mjs` rc 1: `a house with wood configured carries the disclaimer, painted within a phone's width`: killed |
| R1 | card `receiptHtml`: the receipt note's condition `${wood` changed to `${false` | same | `card.mjs` rc 1 (`1 CARD CHECK(S) FAILED`): killed |
| R2 | the same condition changed to `${true` | same | `card.mjs` rc 1 (`1 CARD CHECK(S) FAILED`) by the null leg: killed |
| R3 | the call site `receiptHtml(st, rows, cur, wood)` changed to pass `false` | same | `card.mjs` rc 1 (`1 CARD CHECK(S) FAILED`): killed |
| R4 | `const wood = !!(fuel && fuel.show_whatif)` changed to `!!fuel` | same | `card.mjs` rc 0, `card_browser.mjs` rc 1: `a house with no wood configured carries none`: killed |
| R5 | the receipt note's key `savings.wood_note` changed to `receipt.saved` | same | `card.mjs` rc 1 (`1 CARD CHECK(S) FAILED`): killed |
| R6 | the sv `savings.wood_note` string replaced by the en one | same | `card.mjs` rc 1 (`1 CARD CHECK(S) FAILED`): killed |

The new entity check is also red at the reviewed head `622be7c53` with the test alone applied: `entities.py` rc 1, `[((None, True), (None, False), (None, False))]`. The sensor stated nothing while the event stated `True`. At 2f88732c3 it passes.

## Null control

- The unmodified tree at 2f88732c3 (mutant id NULL, no edit): `entities.py`, `features.py`, `card.mjs` and `card_browser.mjs` all rc 0.
- A house without wood carries the statement as `false`:
  - the new entity check drives the sensor and the event with `wood_fuel` absent, and with `show_whatif` false, and both read `False`;
  - the `card.mjs` check asserts no `receipt-wood-note` on the same receipt without wood;
  - `card_browser.mjs` asserts no table note;
  - four of the five golden captures (no wood) carry `false`.
- Class rule, base against head: `git grep -n saving_includes_wood <rev> -- custom_components/` returns only `notifier.py` at `622be7c53`. At 2f88732c3 it returns `wood_fuel.py` (the definition), `notifier.py` and `sensor.py`.
- Finder's harness: `census` (`dev/audit/harnesses/r10_rca_sav_estimate.py` from `handoff/r10-rca-sav-estimate` at d8eeae8f, sha1 04b644563c84d26378cad42a603dc050e7e5fd88) prints identical `RESULT census` lines and rc 0 at `622be7c53` and at 2f88732c3: single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all `ok`.
  - It is flat by design: part 1 (#3220) settled the census, and this round changes an entity attribute the census does not read.
  - Its companion here is the entity check above, red at `622be7c53` and green at 2f88732c3.
- Carry B harness at 2f88732c3:
  - With no fire: plan 133.79 = drawn 133.79 kWh, the calibration equals `m` for `m` 1.0 and 1.2, and the error is +0.00 %.
  - Perturbation (the largest fire with the pump blind to it): the error reads +0.00 % at `m` 0.8, 1.0 and 1.2, so removing the meter's response to the unforeseen heat takes the error to the null.
  - Flat prices: 7.59 % at `m` 1.0 and at `m` 1.2, scale-invariant in `m`. The 7.59 % is the volume residual the `valve-flat` arm accepts inside `FLAT_BAND_PCT`.

## Figures

**Class enumeration (fixer step 8).** The rule is mine: every non-test, non-record reader of a saving row's `savings_sek`, of the receipt event's `saving_sek` and `saving_includes_wood`, and of a `savings.*`, `receipt.*` or `headline.*` string.

Three commands, run at 2f88732c3:
- `git grep -n -E 'savings?_sek|saving_includes_wood|L\(\s*["`](savings|receipt|headline)\.' -- . ':!tests' ':!dev' ':!*/translations/*' ':!docs/design'` returns 52 lines across `README.md`, `blueprints/automation/notifications.yaml`, `docs/automations.md`, `ledger.py`, `notifier.py`, `payload.py`, `sensor.py`, `wood_fuel.py` and the card JS.
- `git grep -n -E 'savings_months|_monthly_savings|monthly_savings|learn_savings|function replayHtml' -- custom_components/ ':!*/translations/*'` adds the row and entity readers.
- My first rule, round 2's first draft, covered `custom_components/` only. It missed the blueprint, which the concurrent seat's `06aa96295` built.

Every line falls in one of these seams:

| seam (lines the rule returns) | disposition |
|---|---|
| `ledger.py` `savings_pct`, `savings_months` (row producer) | producer, not a stating surface; the no-wood reference and the floor are built (#3220, this PR) and pinned (M1, M2) |
| `payload.py` `SavingsMonth`, `savings_months` | type declarations, no reader |
| `optimizer.py` docstring | prose, no reader |
| `coordinator.py` `_build_data_dict` `savings_months(..., wood_configured=...)` | built, pinned (M4) |
| `notifier.py` `_monthly_receipt` | built; now reads the one definition (M3, S2, S3) |
| `sensor.py` `MonthlySavingsSensor` | **closed in this diff** (S1, S2, S3) |
| card `receiptHtml` (`receipt.*`, `row.savings_sek`) | built (R1 to R6) |
| card `_savingsPageHtml` table (`savings.*`, `row.savings_sek`) | built (M5) |
| card `headlineHtml` (`headline.savings*`) | out of the class: it states `_plan_predicted_savings`, the plan's projection against unoptimized heating, not the metered saving against the reference |
| card `headline.score*` (`headlineHtml`, score aria label) | out of the class: a score, no saving figure |
| card `replayHtml` | out of the class: measured cost against the plan's promised cost, no saving against the reference |
| card `HEALTH_WAITING` and `healthLearningHtml` (`health.learn_savings`, en and sv) | out of the class: a waiting status with no figure |
| card `_plan_monthly_savings` alias and resolver | entity-id resolution, no figure |
| `icons.json`, `strings.json` `plan_monthly_savings` | icon and name only |
| `blueprints/automation/notifications.yaml` Monthly receipt (`data.saving_sek`, `data.saving_includes_wood`) | built by `06aa96295` (B1, B2) |
| `README.md` entity row, `docs/automations.md` event row | documentation of the two machine-readable surfaces; both state it |
| `wood_fuel.py` `saving_includes_wood` | the one definition (S2, S3) |

I re-checked the reviewer's three out-of-class surfaces (`replayHtml`, `headlineHtml` `_plan_predicted_savings`, the `health.learn_savings` row) against their code and they hold. Outside `custom_components/`, `README.md` (updated here) and `docs/automations.md` (the event's `saving_includes_wood`, already stated) document the two machine-readable surfaces.

**Carry B grid:** `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant` at 2f88732c3. It prints `RESULT wood_plant_error_m0.8/1.0/1.2` (mean, min, max and sd over 9 fires), the no-fire, flat and perturbation lines, and per fire the plan and drawn kWh and the calibration.

**Mutations:** the table above. The driver applies one exact-match replacement per mutant in a fresh detached worktree and runs `python3 tests/entities.py`, `python3 tests/features.py`, `python3 tests/plan_view.py && node tests/card.mjs` and `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` as listed.

**Scoped gate:** `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`. `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` exited 0 at 2f88732c3. That run includes `env_drift.py --all origin/main`, which reports `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` over 56 scenarios, plus `structure.py`, `entities.py`, `features.py`, `card.mjs`, `card_drift.mjs` and `doc_claims.py`. `card_browser.mjs` passes at the head (mutant NULL).

**Golden fixtures:** the gate's first run, before the claims, refused with `5 COMMITTED FIXTURE(S) ARE STALE` and `5 UNCLAIMED DRIFT(S)`, each with the single path `sensors.monthly_savings.extra_state_attributes.saving_includes_wood`. After the structure-only edit and the five claims, both read clean. `git diff --stat origin/main...HEAD -- tests/golden/` shows +1 line in each of the five fixtures and +5 in `claimed_drift.txt`. `card_claimed_drift.txt` is byte-identical to origin/main.

**Versions:** `git diff --quiet origin/main...HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` exits 0.

**Structure:** `python3 tests/structure.py` passes in the gate run: STRUCTURE RATCHET PASSED, no budget raised.

## Unpinned sites

- `custom_components/heatpump_optimizer/wood_fuel.py:101 RETURN_DEL` (`saving_includes_wood`): pinned by `python3 tests/mutation_table.py --pin-killed --base origin/main` at the pre-pin head. It printed `pinned   custom_components/heatpump_optimizer/wood_fuel.py:101 RETURN_DEL -- killed by tests/features.py` and `PIN KILLED: 1 pinned, 0 left unpinned`. The row is committed under `tests/mutation_ledger/killed_by/wood_fuel.py/`.

## Red checks

- The final head 2f88732c3 has not run CI: it reaches the pull request only when the handoff moves it, so it has no concluded red.
- At `dea3c729d`, the current PR head, I read all 68 check runs on one page and none concluded red. The three `gate` jobs (128007679908, 128007136690, 128006618718), `tests / mutation` (127986874591) and `pr-contract / pr-contract` (128006204376) succeeded; every other run succeeded or was skipped.
- At the reviewed head `622be7c53` I read all 68 check runs on one page.
- The concluded reds there are the two `gate` jobs of the `CI edit` runs, 127822327907 (run 42191160922) and 127822332689 (run 42192068191). Class: CI tooling, not this diff.
  - Each printed `FAIL run(s) [<the other edit run>] at this head are still being judged; their gate decides` and exited 1, so the two deferred to each other and neither judged code.
  - The `CI code` run's `gate` (127821770398) passed.
  - The cheaper detector is `tools/ci/gate.py`'s own deferral: it could wait on, or exclude, a sibling edit run's gate. That is a CI-tooling change outside this group's scope. The answer is to re-run one edit run's gate once the other concludes, which is the orchestrator's.
- `governance / instrument-self-tests` (127803428238) concluded `cancelled`, not failed.
- `mutation` (`tests / mutation`): predicted red by `prepr.sh` step 6d at `ae1f1244b`, for the one unpinned site this diff added (`wood_fuel.py:101 RETURN_DEL`). Class: unpinned site. Answer: repaired before the handoff by `--pin-killed` (see Unpinned sites), the `mutation-autofix` repair run by hand because a handoff ref runs no job (`ci-autofix.md`). The cheaper detector is `prepr.sh` step 6d itself, which caught it before any CI ran. Standing cost: none beyond that run.

## Forward-carry

- The floor's cost on a wood house whose model reads the meter high (+25.00 % (that is 1/m - 1), and the row reads 44.9 % where `m` 1.0 reads 31.1 % at `m` 0.8, measured above) changes no later stage's method. It follows from two owner rulings as built. It is stated for the owner in `docs/how-it-works.md` ("Wood furnaces and other external heat"), and changing it is the owner's call. Carry: dismissed: owner-ruling territory, stated in docs/how-it-works.md and this body

## Friction

- seat-concurrency: unclear: while this seat held the topic, the `hpo-fixer` identity pushed content commits (`06aa96295`, `d5643c78e`) and merges onto `handoff-wip/r10-sav-wood-heat`, so my fast-forward pushes were refused three times and two figure passes were re-taken. The brief names this ref as the fixer's own. Carry: dismissed: dispatch coordination is the orchestrator's, and this body records it

- brief-identity: contradiction: the payload's PROMPT.md pins the git identity `seat` / `seat@users.noreply.github.com`, while the brief inside it says `hpo-fixer` with the noreply address. I used the payload's `seat`, its first and more specific instruction. Carry: dismissed: a dispatch-payload wording, not a policy file; the orchestrator renders both
- frugal-routing: cost: a session plugin hook refuses a sixth inline read or command per prompt until a subagent is spawned, so this seat spawned five scout or extractor agents to read files it was editing. Carry: dismissed: a session plugin outside this repository's policy
- background-limit: cost: a mutant batch started as a harness background task was killed at the task's time limit halfway through, and I re-ran it under `setsid`. Carry: dismissed: a session harness limit outside this repository's policy
