R10-HOTFIX-SAV-ESTIMATE part 2 (part 1 merged as #3220), topic r10-sav-wood-heat. This is repair round 4, after fix review round 2 blocked `dea3c729` as class-open.

## Re-cut

This is the fourth round, so this body replaces the earlier ones. Every figure below was re-taken in this pass, at the head named under `## Head` or at a tree byte-equal to it in what the figure reads.

**Carry A (owner ruling, tvofi 2026-11-04).** The reference has no wood, and wood's heat counts in the saving. Wherever wood is configured, the saving the integration states says that it includes wood's heat and excludes firewood's cost.

**What the PR builds.**
- `wood_fuel.py` `saving_includes_wood(data)` is the one definition. It is `True` where wood is configured (`show_whatif`).
- The receipt event (`notifier.py` `_monthly_receipt`) and the `MonthlySavingsSensor` attribute `saving_includes_wood` both read that definition.
- The card's receipt (`receiptHtml`) and savings table (`_savingsPageHtml`) show `savings.wood_note` on a wood house.
- **This round:** the "Monthly receipt" message in `blueprints/automation/notifications.yaml` appends the same note, guarded by the event's `saving_includes_wood`. That was the review's block. The wording is the card's `savings.wood_note` string, "The saving includes heat from wood. Firewood's cost is not counted.", so there is one wording and no second grammar.
- The guard also requires `data.saving_sek is not none`: on an old-basis row, where the message states no saving, there is nothing to qualify.
- `docs/automations.md` (the blueprint's line), `docs/dashboard-card.md`, `docs/how-it-works.md` and the README's sensor row say so.
- `tools/policy/agreement.mjs` `SHARED_GRAMMARS` registers the card-string extractor that the pin and the render harness share, as `identical:`.
- The five `coord_*` golden captures each gain the one boolean key. They are claimed in `tests/golden/claimed_drift.txt` and were not re-recorded.

**The pin and why it is a source pin.** `tests/entities.py` loads the blueprint and finds the "Monthly receipt" option. It requires three things:
- the card's `savings.wood_note` text occurs exactly once in the message;
- that text sits inside `{% if data.saving_sek is not none and data.saving_includes_wood %}`;
- the event declares `saving_includes_wood` (`notifier.EVENT_DATA`).

The check reads the shipped YAML and the card's string table, so it pins what a user installs (fixer step 11). It does not render the template: CI's interpreter (`venv-ci`) has no jinja2, and `python3 -c "import jinja2"` fails there with `ModuleNotFoundError`. This is a design choice, stated here. The rendering is measured by a harness that lands in this PR, `dev/audit/harnesses/r10_sav_receipt_render.py`. It runs under `venv-ha`, whose Home Assistant brings jinja2. It renders the message a user receives for a wood house, for the null leg (the same saving, no wood), and for a wood house with no saving.

**Alternatives considered.**
- Add jinja2 to CI's lock so `entities.py` can render. Rejected: it adds a dependency to the gate interpreter for one check, while the source pin already kills every mutant below.
- The reviewer's literal wording, with a semicolon. Rejected: it is a second spelling of the card's sentence. The card's string is the one definition the brief asks to reuse, and the pin reads it from the card, so a change to the card's wording reddens the blueprint pin until the two agree.

**The class rule, widened.** The question is: where does the integration state the metered saving to a user? The rule follows the value from the ledger, through the receipt event, to the shipped consumers outside the package:
- R1: `git grep -n -E 'savings_sek|saving_sek|savings_months|plan_monthly_savings|MonthlySavingsSensor|EVENT_MONTHLY_RECEIPT|monthly_receipt|saving_includes_wood' -- custom_components blueprints docs README.md ':!docs/design' ':!custom_components/heatpump_optimizer/www'`
- R2 (prose that states the saving without naming a key): `git grep -n -i -E 'monthly receipt|savings page|plan monthly savings|than a plain thermostat' -- docs README.md blueprints ':!docs/design'`
- R3 (the card's keys, each use grouped by its enclosing function): `git grep -n -o -E '\b(savings|receipt|headline)\.[a-z_]+' -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`

`docs/design/2026-09-05-monthly-savings-history/` is excluded from R1 and R2. It is a dated design record that recounts the September design, not text a user reads for the saving (fixer step 10).

| seam | what it states | disposition |
|---|---|---|
| `ledger.py` `savings_months` | the producer: reference with no wood, actual metered, the floor | built (#3220) |
| `coordinator.py` (`savings_months` into the payload) | passes the rows | built (#3220) |
| `notifier.py` `_monthly_receipt`, `EVENT_DATA` | receipt event `saving_sek`, `saving_includes_wood` | built; killed by N1 |
| `sensor.py` `MonthlySavingsSensor` | entity state is the open month's `savings_sek` | built; killed by S1, S2 |
| `wood_fuel.py` `saving_includes_wood` | the one definition | built |
| `payload.py`, `optimizer.py` | type declarations and a docstring | no stated saving: out of class |
| `icons.json`, `strings.json`, `translations/en.json`, `translations/sv.json` | the entity's icon and name | no figure: out of class |
| **`blueprints/automation/notifications.yaml` "Monthly receipt"** | **"… {saving_sek} {currency} ({saving_pct} %) less than a plain thermostat would have."** | **built this round; killed by B1 to B3** |
| `blueprints/automation/notifications.yaml` trigger and condition (`heatpump_optimizer_monthly_receipt`) | the event type | no figure: out of class |
| `docs/automations.md` event table (`heatpump_optimizer_monthly_receipt`) | documents `saving_sek` and `saving_includes_wood` (wood's heat in, firewood's cost out) | already states it (from #3220) |
| `docs/automations.md` Notifications blueprint line | describes the message | built this round |
| `README.md` Plan Monthly Savings row | the sensor | built (`saving_includes_wood` stated) |
| `README.md` Notifications blueprint line | lists the events the blueprint sends | no saving stated: out of class |
| `docs/dashboard-card.md` savings page (`## The savings page`, the `receipts` attribute, the `savings_months` rows) | describes the receipt and table | built: wood sentence at the end of the table paragraph |
| `docs/dashboard-card.md` `currency` option row | the unit | no saving: out of class |
| `docs/how-it-works.md` "Wood furnaces and other external heat" | the saving's composition | built: names the page, the sensor and the blueprint's receipt |
| card `receiptHtml` `receipt.saved` | "Saved {amount} …" | built: `receipt-wood-note`; killed by C1, C2 |
| card `_savingsPageHtml` `savings.*` | the savings table | built: `savings.wood_note`; killed by C3 (card_browser) |
| card `receiptHtml` `receipt.line_*`, `total`, `closed`, `col_*`, `covers`, `by_reason`, `peak`, `starts` | the month's cost lines | a cost, not a saving against the reference: out of class |
| card `headlineHtml` `headline.savings*` (`_plan_predicted_savings`) | the plan's projection | not the metered saving: out of class (the review agrees) |
| card `_render` `headline.score*` | the optimization score | no saving: out of class |

R1's surfaces outside the package are `blueprints/`, `docs/automations.md`, `docs/dashboard-card.md` and `README.md`. Each is listed in the table. No other file outside `custom_components` states the saving.

**Carry B (the size of wood's unforeseen heat), re-taken.** The `wood-plant` arm in `dev/audit/harnesses/r10_sav_wood_reference.py` puts the fire in the plant only, and the plan is never told of it. It runs 9 fires (4, 8 and 12 kW, starting 06:00, 17:00 and 22:00, 4 h each). The figure is the applied calibration's error against the true meter factor `m`, less the same error with no fire:
- `m` 0.8 and 1.0: 0.00 % at every fire.
- `m` 1.2: mean −1.95 %, min −4.50, max 0.00, sd 1.47.

So where the model reads the meter low, the saving is understated by up to 4.5 % in this simulated house. `docs/how-it-works.md` states that, as an upper bound for this simulated house.

**A measured limit, not changed here.** On a wood house the floor (calibration at least 1.0) also stops the calibration correcting a model that reads the meter high. In the no-fire run at `m` 0.8, the error is +25.00 % (that is 1/m − 1), and the row reads 44.9 % against 31.1 % at `m` 1.0. This follows from the two owner rulings as built. `docs/how-it-works.md` says so, and changing it is the owner's call.

## Head

2c147208a00da5956ada04b3abe6e787dc3723fb (code at `handoff/r10-sav-wood-heat`). It merges `origin/main` at `28482ecee` (main's #3242 and #3253: merge-train, roster and seat tooling, harnesses and instrument notes, no production, test or doc file), after the PR branch's own merge `a25821255`, which carries no content past this branch. `git diff --stat b4b3889e d120c5bf` lists only `tools/policy/agreement.mjs`.
- The full scoped gate ran at `d120c5bf` and again at `67e1bb927` (that merged with main's #3242). The run at `67e1bb927` is the one quoted under `## Figures`.
- `git diff --name-only d120c5bf HEAD` returns 23 files, every one from main. Read against `tests/closures.json`, the only `scope.run` script whose recorded closure holds any of them is `tests/entities.py` (it holds `.claude/workflows/web-stamp.js`, `tools/audit/seat/merge_train.py`, `roster_edit.py` and `roster_lib.py`). So `entities.py`, `structure.py` and `prepr.sh` were re-run at this head (`## Figures`). The scope `closure.py select` derives is the same `scope.run` at every one of these heads.
- The mutants ran in a worktree at `8d687e68b`, and the blueprint mutants in one at `8d687e68b` plus the new harness file. `git diff --quiet 8d687e68b HEAD -- custom_components blueprints tests/entities.py tests/features.py tests/card.mjs tests/card_browser.mjs tests/plan_view.py docs README.md` exits 0. So the mutants measured the same production, test and doc tree as the head. What differs is main's `tests/mutation_ledger` record, the new harness and its `tests/closures.json` entry.

## Mutation proof

Each mutant is one exact-string replacement, refused unless the pattern occurs once. Each ran against the script named, with `PYTHONPATH=tests/hastub`, and the file was restored afterwards; `git status --porcelain` was clean after each runner. "Red" quotes the failing check. The `a3:*`, `a4:*`, `a5:*`, `a10:*` and `a16:*` FAIL lines that `entities.py` and `features.py` print are those scripts' own negative self-tests, and they appear in the null run too.

| id | mutant (file, symbol: from → to) | command | red at the mutant |
|---|---|---|---|
| B1 | `notifications.yaml` "Monthly receipt": the note line deleted (the tree before this round) | `python3 tests/entities.py` | rc 1, 1 of 2639: `The notifications blueprint's monthly receipt says a wood house's saving includes wood's heat, in the card's words, and says nothing without wood` |
| B2 | same: guard `data.saving_sek is not none and data.saving_includes_wood` → `data.saving_sek is not none` (the null leg: a note on every house) | `python3 tests/entities.py` | rc 1, 1 of 2639: the same check |
| B3 | same: the note → `The saving includes heat from wood.` (a second wording) | `python3 tests/entities.py` | rc 1, 1 of 2639: the same check |
| S1 | `sensor.py` `MonthlySavingsSensor`: `"saving_includes_wood": saving_includes_wood(data),` → `False` | `python3 tests/entities.py` | rc 1: `MonthlySavingsSensor states that a wood house's saving includes wood's heat, as the receipt event does; False without wood` `[((False, True), (False, False), (False, False))]` |
| S2 | same line → `True` (the null leg) | `python3 tests/entities.py` | rc 1: the same check `[((True, True), (True, False), (True, False))]` |
| N1 | `notifier.py` `_monthly_receipt`: `saving_includes_wood(data)` → `False` | `python3 tests/features.py`; `python3 tests/entities.py` | features rc 1: `the receipt event carries what the card states: no saving on the old basis, the percent unclipped, wood stated`; entities rc 1: the sensor check `[((True, False), (False, False), (False, False))]` |
| C1 | card `receiptHtml`: the `receipt-wood-note` div → empty | `python3 tests/plan_view.py && node tests/card.mjs` | rc 1: `the receipt's saving on a wood house says it includes wood's heat, not firewood's cost (en, sv); none without wood` |
| C2 | card `_savingsPageHtml`: `const wood = !!(fuel && fuel.show_whatif);` → `const wood = true;` (the null leg: a note on every house) | `python3 tests/plan_view.py && node tests/card.mjs` | rc 1: the same check |
| C3 | card `_savingsPageHtml`: `const woodNote = wood` → `false` | `python3 tests/plan_view.py && node tests/card.mjs`; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` | card.mjs rc 0 (survives); card_browser rc 1: `a house with wood configured carries the disclaimer, painted within a phone's width` |

Failing test first: B1 is the blueprint at the previous PR head `dea3c729`, and the new `entities.py` check fails there.

The render harness, on the same mutants, run on a blueprint file passed as its argument:
- B2 reads `RESULT no-wood notes=1 want=0 DEFECT`, rc 1.
- B4 (the guard reduced to `data.saving_includes_wood`) reads `RESULT no-saving notes=1 want=0 DEFECT`, rc 1. B4 also breaks the `entities.py` pin's guard pattern, so it dies there by the same check as B2.

## Null control

- The unmodified tree (`NULL`, the same runner with no edit, at `8d687e68b`): `entities.py` rc 0 (ALL 2639 ENTITY CHECKS PASSED), `features.py` rc 0, `plan_view.py && card.mjs` rc 0 (ALL CARD CHECKS PASSED), `card_browser.mjs` rc 0 (ALL BROWSER CHECKS PASSED).
- A house without wood gets no note. The render harness at the head prints `RESULT no-wood notes=0 want=0 ok`, rc 0, with the message `Heating and hot water cost 812.0 SEK, 204.0 SEK (20.0 %) less than a plain thermostat would have.`
- The wood house at the head reads `notes=1 want=1 ok`, and the message ends `… would have. The saving includes heat from wood. Firewood's cost is not counted.`
- The same harness on the blueprint of the previous PR head `dea3c729` and of the merge base `af56818b5` prints `RESULT wood notes=0 want=1 DEFECT`, rc 1. So the harness reads the defect at the base and not at the head.
- The class rule's own null: R1 run on the previous PR head (`git grep … dea3c729 -- blueprints`) returns four lines of `notifications.yaml`, and two of them (119, 120) state `saving_sek` with no `saving_includes_wood` line. So the widened rule returns the seam the review found, where round 2's rule (`-- custom_components`) could not. At the head it returns five lines, the fifth being the guard (124).
- Finder's harness (`r10_rca_sav_estimate.py census`, sha1 `04b644563c84d26378cad42a603dc050e7e5fd88`, the same file at both ends), at the merge base `af56818b5` and at `8d687e68b`: the same six `RESULT census` lines (single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all ok), rc 0 at both ends. It is flat by design, because part 1 (#3220) settled the census. The companion that reads this round's defect at the base and not at the head is the render harness above.
- Carry B's controls (the same `wood-plant` run):
  - With no fire, plan 133.79 = drawn 133.79 kWh.
  - With the pump blind to the fire (the perturbation), the error is +0.00 % at `m` 0.8, 1.0 and 1.2.
  - With flat prices and no fire, the row reads 7.59 % at `m` 1.0 and 1.2. That is the volume residual the `valve-flat` arm accepts.

## Figures

- Class seams, the table above: R1, R2 and R3 as quoted, run at the head. R1 returns 43 lines over 15 files, R2 returns 12 lines and R3 returns 102 key uses.
- Blueprint mutants B1 to B3 and their null: an in-place `sed` per mutant, then `PYTHONPATH=tests/hastub python3 tests/entities.py`, then `git checkout` of the blueprint, in the worktree at `8d687e68b` plus the harness file.
- Mutants S1, S2, N1, C1 to C3 and NULL: the commands in each row, in a detached worktree at `8d687e68b`.
- Render harness: `/opt/hpo/venv-ha/bin/python -I dev/audit/harnesses/r10_sav_receipt_render.py [<blueprint.yaml>]` (sha1 `b97e785bf7c062d384a5783b3bee9fbfe844b1e7`) on the head's blueprint, on `git show dea3c729:blueprints/automation/notifications.yaml`, on the merge base's, and on the B2 and B4 copies.
- Carry B, every figure: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant` (sha1 `dfcdcc46269eca76bbdeffacd758522b45165b35`) at `8d687e68b`, rc 0.
- Finder's census: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py census`, at `af56818b5` and `8d687e68b`.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at `67e1bb927` (see `## Head` for why that run stands for this head). It printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`, `NO UNCLAIMED DRIFT` and `NO STALE FIXTURE` over 56 scenarios, and `STRUCTURE RATCHET PASSED`, and it exited 0.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head: ALL 2639 ENTITY CHECKS PASSED, rc 0.
- `python3 tests/structure.py` at the head: STRUCTURE RATCHET PASSED. No budget moved and none was raised.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED, after the harness took the canonical `repo_root`. The first gate run had refused its depth root (see `## Red checks`).
- Agreement lane: `python3 -I tools/policy/agreement_py.py --out <json> && node tools/policy/agreement.mjs --py-json <json>` first refused one `UNREGISTERED` grammar, the card's `savings.wood_note` extractor, in `tests/entities.py` and the render harness: the same card-string extractor in two readers. The `SHARED_GRAMMARS` entry this PR adds (`identical:`) registers it, and the re-run prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` and `AGREEMENT ok`. `node tools/policy/agreement.mjs --self-test`: SELF-TEST 233 of 233 probes held.
- `python3 tools/pr/ci_predict.py --base origin/main`: one predicted `closures` INERT READS red, for the new harness under `tests/harness_headers.py`. `--apply-inert` wrote it, and the re-run predicts none.
- Protected files: `git diff --quiet origin/main HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden/card_claimed_drift.txt` exits 0. `tests/golden/claimed_drift.txt` differs from main only by the five `coord_*` claim lines; `claims-for:` is unchanged.

## Red checks

none: the final head has not run CI, because it reaches the pull request with this handoff. The previous PR head `dea3c729` was classified `GREEN … red: none` by the round-2 review (`merge_train.py classify`).

The one red this seat's own runs turned is answered here. The first local scoped gate failed `tests/harness_headers.py` (`every inlined walk matches the canonical helper and no depth root remains`) on the new harness's `parents[3]` root. The harness now inlines `repo_root`. The cheaper detector already exists: `prepr.sh`'s scoped gate selects `harness_headers.py` for any new harness, and it caught this before the push.

## Forward-carry

- The floor's cost on a wood house whose model reads the meter high (the +25.00 % reference at `m` 0.8, measured above) changes no later stage's method. It follows from two owner rulings as built and is stated in `docs/how-it-works.md`. Changing it is the owner's call. Carry: dismissed: owner ruling territory, stated for the owner in docs/how-it-works.md and this body

## Friction

- seat-concurrency: contradiction: another `hpo-fixer` push (`a94e4dc33`, a merge of `origin/main` at 19:41Z) landed on `handoff-wip/r10-sav-wood-heat` over this seat's own step push `8d687e68b` while this seat was measuring, so this seat's next fast-forward push was refused. This seat merged it, since its only content is main's `tests/mutation_ledger` record. Carry: dismissed: a dispatch event, recorded for the orchestrator in this body
- frugal-routing: cost: a session plugin hook refuses a sixth inline command per prompt, so one locate step went to a cheap subagent. Carry: dismissed: a session plugin outside this repository's policy
