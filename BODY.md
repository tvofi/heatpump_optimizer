R10-HOTFIX-SAV-ESTIMATE part 2 (part 1 merged as #3220), topic r10-sav-wood-heat. This is repair round 5, after fix review round 4 blocked `8bc540e0` as ci-red on CodeQL code-scanning alert 50.

## Re-cut

This is past the third round, so this body replaces the earlier ones. Every figure below was re-taken in this pass, at the head named under `## Head`.

**Carry A (owner ruling, tvofi 2026-11-04).** The reference has no wood, and wood's heat counts in the saving. Wherever wood is configured, the saving the integration states says that it includes wood's heat and excludes firewood's cost.

**What the PR builds.**
- `wood_fuel.py` `saving_includes_wood(data)` is the one definition. It is `True` where wood is configured (`show_whatif`).
- The receipt event (`notifier.py` `_monthly_receipt`) and the `MonthlySavingsSensor` attribute `saving_includes_wood` both read that definition.
- The card's receipt (`receiptHtml`) and savings table (`_savingsPageHtml`) show `savings.wood_note` on a wood house.
- The "Monthly receipt" message in `blueprints/automation/notifications.yaml` appends the card's `savings.wood_note` text, guarded by `data.saving_sek is not none and data.saving_includes_wood`. There is one wording, the card's.
- `docs/automations.md`, `docs/dashboard-card.md`, `docs/how-it-works.md` and the README's sensor row say so.
- `tools/policy/agreement.mjs` `SHARED_GRAMMARS` registers the card-string extractor that the pin and the render harness share, as `identical:`.
- The five `coord_*` golden captures each gain the one boolean key. They are claimed in `tests/golden/claimed_drift.txt` and were not re-recorded.

**This round: the CodeQL red, fixed at the root.** `dev/audit/harnesses/r10_sav_receipt_render.py` built `jinja2.Environment()`, whose autoescape is off, and CodeQL flagged that as alert 50, `py/jinja2/autoescape-false`. The harness now builds `jinja2.Environment(autoescape=True)`. The alert is not suppressed or dismissed.
- Why `autoescape=True` and not `select_autoescape()`: `select_autoescape()` keys on a template file's extension. This harness builds its template from a string, so the result would depend on that function's `default_for_string` argument. `autoescape=True` states the setting directly.
- The reviewer's warning, handled deliberately: autoescape escapes only an expression's output (`{{ … }}`), never a template's literal text. The note is literal text in the blueprint, outside any `{{ }}`, so its apostrophe is not escaped. The harness therefore counts the note as written, with no escaped form and no `Markup` wrapper. The expressions in the message render numbers and the currency code, which contain no escapable character. So the rendered text is the same as what Home Assistant's template engine (a sandboxed environment with autoescape off) sends.
- The perturbation that shows the warning was real but does not apply here: on a copy of the blueprint with the note moved inside a `{{ "…" }}` expression, the harness reads `RESULT wood notes=0 want=1 DEFECT`. The apostrophe becomes `&#39;` there. So if a later edit moves the note into an expression, the wood arm goes red loudly rather than passing silently.
- Alternatives considered. Dismissing the alert with a reason: rejected, because the brief requires a root fix and a dismissal leaves the pattern in the tree. `select_autoescape(default_for_string=False)`: rejected, because it is still autoescape-off for this string template, and CodeQL's query reads it the same way.

**The pin and why it is a source pin.** `tests/entities.py` loads the blueprint and finds the "Monthly receipt" option. It requires three things: the card's `savings.wood_note` text occurs exactly once in the message; it sits inside `{% if data.saving_sek is not none and data.saving_includes_wood %}`; and the event declares `saving_includes_wood` (`notifier.EVENT_DATA`). It does not render the template, because CI's interpreter (`venv-ci`) has no jinja2. That is a design choice, stated here. The render harness measures the rendering under `venv-ha`.

**The class rule.** The question: where does the integration state the metered saving to a user?
- R1: `git grep -n -E 'savings_sek|saving_sek|savings_months|plan_monthly_savings|MonthlySavingsSensor|EVENT_MONTHLY_RECEIPT|monthly_receipt|saving_includes_wood' -- custom_components blueprints docs README.md ':!docs/design' ':!custom_components/heatpump_optimizer/www'`
- R2 (prose that states the saving without naming a key): `git grep -n -i -E 'monthly receipt|savings page|plan monthly savings|than a plain thermostat' -- docs README.md blueprints ':!docs/design'`
- R3 (the card's keys): `git grep -n -o -E '\b(savings|receipt|headline)\.[a-z_]+' -- custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`

`docs/design/2026-09-05-monthly-savings-history/` is excluded. It is a dated design record that recounts a past design (fixer step 10).

| seam | what it states | disposition |
|---|---|---|
| `ledger.py` `savings_months` | the producer | built (#3220) |
| `coordinator.py` (`savings_months` into the payload) | passes the rows | built (#3220) |
| `notifier.py` `_monthly_receipt`, `EVENT_DATA` | receipt event `saving_sek`, `saving_includes_wood` | built; killed by N1 |
| `sensor.py` `MonthlySavingsSensor` | entity state is the open month's `savings_sek` | built; killed by S1, S2 |
| `wood_fuel.py` `saving_includes_wood` | the one definition | built |
| `payload.py`, `optimizer.py` | type declarations and a docstring | no stated saving: out of class |
| `icons.json`, `strings.json`, `translations/en.json`, `translations/sv.json` | the entity's icon and name | no figure: out of class |
| `blueprints/automation/notifications.yaml` "Monthly receipt" | the saving against a plain thermostat | built; killed by B1 to B4 |
| `blueprints/automation/notifications.yaml` trigger and condition | the event type | no figure: out of class |
| `docs/automations.md` event table and blueprint line | `saving_sek`, `saving_includes_wood`, the message | built |
| `README.md` Plan Monthly Savings row | the sensor | built |
| `README.md` Notifications blueprint line | the events the blueprint sends | no saving stated: out of class |
| `docs/dashboard-card.md` savings page | the receipt and table | built |
| `docs/dashboard-card.md` `currency` option row | the unit | no saving: out of class |
| `docs/how-it-works.md` "Wood furnaces and other external heat" | the saving's composition | built |
| card `receiptHtml` `receipt.saved` | "Saved {amount} …" | built: `receipt-wood-note`; killed by C1 |
| card `_savingsPageHtml` `savings.*` | the savings table | built: `savings.wood_note`; killed by C2, C3 |
| card `receiptHtml` `receipt.line_*`, `total`, `closed`, `col_*`, `covers`, `by_reason`, `peak`, `starts` | the month's cost lines | a cost, not a saving: out of class |
| card `headlineHtml` `headline.savings*` | the plan's projection | not the metered saving: out of class |
| card `_render` `headline.score*` | the optimization score | no saving: out of class |

**Carry B (wood's unforeseen heat).** The `wood-plant` arm of `dev/audit/harnesses/r10_sav_wood_reference.py` puts the fire in the plant only, unknown to the plan, over 9 fires (4, 8 and 12 kW; 06:00, 17:00 and 22:00; 4 h each). The figure is the applied calibration's error against the true meter factor `m`, less the same error with no fire. At `m` 0.8 and 1.0 it is +0.00 % at every fire. At `m` 1.2 it is mean −1.95 %, min −4.50, max +0.00, sd 1.47. `docs/how-it-works.md` states that as an upper bound for this simulated house.

**A measured limit, not changed here.** On a wood house the floor (calibration at least 1.0) also stops the calibration correcting a model that reads the meter high. With no fire at `m` 0.8 the error is +25.00 % (1/m − 1), and the row reads 44.9 % against 31.1 % at `m` 1.0. This follows from two owner rulings as built. `docs/how-it-works.md` says so, and changing it is the owner's call.

## Head

07461bb3756bd7189f51c60677f5c0c092680610 (code at `handoff/r10-sav-wood-heat`).
- It is the review head `8bc540e0`, then the merge `992dd8a58` of `origin/main` at `f2a015142714` (the merge base), then the one harness commit `07461bb37`. `git diff --stat 992dd8a5 07461bb3` lists only `dev/audit/harnesses/r10_sav_receipt_render.py`. `git diff --quiet 8bc540e0 992dd8a5 -- custom_components blueprints docs README.md tests/entities.py tests/features.py tests/card.mjs tests/card_browser.mjs dev/audit/harnesses tests/golden` exits 0, so main's merge changed none of the files this PR's figures read.
- `origin/main` has not moved since the merge: it read `f2a015142714` at the `prepr.sh` run and again before the handoff, so no second merge was owed.
- Every figure below was taken at this head. The mutants ran in a detached worktree at this head.

## Mutation proof

Each mutant is one exact-string replacement, refused unless the pattern occurs exactly once. Each ran in a detached worktree at the head with `PYTHONPATH=tests/hastub`. The file was restored afterwards, and `git status --porcelain` was clean after each mutant. "Red" quotes the failing check. The `a*:` and `hb:` FAIL lines that `entities.py` prints are its own negative self-tests, and the null run prints them too.

| id | mutant (file, symbol: from → to) | command | red at the mutant |
|---|---|---|---|
| B1 | `notifications.yaml` "Monthly receipt": the note line deleted | `python3 tests/entities.py`; render harness | entities rc 1, 1 of 2642: `The notifications blueprint's monthly receipt says a wood house's saving includes wood's heat, in the card's words, and says nothing without wood`; render rc 1: `RESULT wood notes=0 want=1 DEFECT` |
| B2 | same: guard `data.saving_sek is not none and data.saving_includes_wood` → `data.saving_sek is not none` | same | entities rc 1, the same check; render rc 1: `RESULT no-wood notes=1 want=0 DEFECT` |
| B3 | same: the note → `The saving includes heat from wood.` | same | entities rc 1, the same check; render rc 1: `RESULT wood notes=0 want=1 DEFECT` |
| B4 | same: guard → `data.saving_includes_wood` | same | entities rc 1, the same check; render rc 1: `RESULT no-saving notes=1 want=0 DEFECT` |
| S1 | `sensor.py` `MonthlySavingsSensor`: `"saving_includes_wood": saving_includes_wood(data),` → `False` | `python3 tests/entities.py` | rc 1, 1 of 2642: `MonthlySavingsSensor states that a wood house's saving includes wood's heat, as the receipt event does; False without wood` `[((False, True), (False, False), (False, False))]` |
| S2 | same line → `True` | `python3 tests/entities.py` | rc 1: the same check `[((True, True), (True, False), (True, False))]` |
| N1 | `notifier.py` `_monthly_receipt`: `"saving_includes_wood": saving_includes_wood(data),` → `False` | `python3 tests/features.py`; `python3 tests/entities.py` | features rc 1, 1 of 4877: `the receipt event carries what the card states: no saving on the old basis, the percent unclipped, wood stated`; entities rc 1: the sensor check `[((True, False), (False, False), (False, False))]` |
| C1 | card `receiptHtml`: the `receipt-wood-note` div → empty | `python3 tests/plan_view.py && node tests/card.mjs` | rc 1, 1 CARD CHECK(S) FAILED: `the receipt's saving on a wood house says it includes wood's heat, not firewood's cost (en, sv); none without wood` |
| C2 | card `_savingsPageHtml`: `const wood = !!(fuel && fuel.show_whatif);` → `const wood = true;` | same | rc 1: the same check |
| C3 | card `_savingsPageHtml`: `const woodNote = wood` → `false` | same; `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers node tests/card_browser.mjs` | card.mjs rc 0 (survives); card_browser rc 1, 1 BROWSER CHECK(S) FAILED: `a house with wood configured carries the disclaimer, painted within a phone's width` |

The harness's own line, `autoescape=True` → `autoescape=False`, is not a mutant any in-tree check kills, and none should: the render output is identical either way (see `## Null control`). Its detector is CodeQL's `py/jinja2/autoescape-false` query, which read alert 50 on exactly that form.

Failing test first: B1 is the blueprint before part 2's blueprint change, and the `entities.py` check fails there.

## Null control

- The unmodified head, the same runner with no edit (`NULL`): `entities.py` rc 0 (ALL 2642 ENTITY CHECKS PASSED), `features.py` rc 0 (ALL 4877 FEATURE CHECKS PASSED), `plan_view.py && card.mjs` rc 0 (ALL CARD CHECKS PASSED), `card_browser.mjs` rc 0 (ALL BROWSER CHECKS PASSED), render harness rc 0.
- The autoescape change, before and after: the render harness's full output at `8bc540e0`'s harness (autoescape off) and at the head (autoescape on), run on the same blueprint, compared with `diff before after && echo IDENTICAL`, printed `IDENTICAL`. Both read rc 0 and:
  - `RESULT wood notes=1 want=1 ok message="Heating and hot water cost 812.0 SEK, 204.0 SEK (20.0 %) less than a plain thermostat would have. The saving includes heat from wood. Firewood's cost is not counted."`
  - `RESULT no-wood notes=0 want=0 ok message='Heating and hot water cost 812.0 SEK, 204.0 SEK (20.0 %) less than a plain thermostat would have.'`
  - `RESULT no-saving notes=0 want=0 ok message='Heating and hot water cost 812.0 SEK.'`
- The harness at the head on the merge base `af56818b5`'s blueprint reads `RESULT wood notes=0 want=1 DEFECT`, rc 1. So it reads the defect at the base and not at the head.
- The escape perturbation: the note moved into a `{{ "…" }}` expression reads `RESULT wood notes=0 want=1 DEFECT` (see `## Re-cut`). So the harness can tell the difference between escaped and unescaped text.
- The class rule's own null: R1 at `dea3c729` (the head before the blueprint change), restricted to `-- blueprints`, returns 4 lines, none of them a `saving_includes_wood` guard. At the head it returns 5, the fifth being the guard.
- Finder's harness (`r10_rca_sav_estimate.py census`, from `handoff/r10-rca-sav-estimate`, sha1 `04b644563c84d26378cad42a603dc050e7e5fd88`), run in `git archive` exports of `af56818b5` and of the head: both print the same six `RESULT census` lines, checked with `diff base head && echo CENSUS-IDENTICAL`, which printed `CENSUS-IDENTICAL` (single 1.00, unvalved 0.92, valve-at-curve 1.00, valve-charged 1.00, wood-warm 1.00, wood-hot 1.00, all ok), and rc 0 at both ends. It is flat by design, because part 1 (#3220) settled the census. The companion that reads this PR's defect at the base and not at the head is the render harness.
- Carry B's controls (the same `wood-plant` run): with no fire, plan 133.79 = drawn 133.79 kWh. With the pump blind to the fire (the perturbation), the error is +0.00 % at `m` 0.8, 1.0 and 1.2. With flat prices and no fire, the row reads 7.59 % at `m` 1.0 and 1.2.

## Figures

- Class seams: R1, R2 and R3 as quoted, run at the head. R1 returns 43 lines over 15 files, R2 returns 12 lines and R3 returns 102 key uses (each counted with `| wc -l`, files with `cut -d: -f1 | sort -u | wc -l`).
- Mutants and NULL: `python3 -I mut.py` (a scratch runner: one exact replacement per mutant, the commands in each row, restore, `git status --porcelain`) in a detached worktree at the head.
- Render harness: `/opt/hpo/venv-ha/bin/python -I dev/audit/harnesses/r10_sav_receipt_render.py [<blueprint.yaml>]`, sha1 `6af7338b358bd552bcd65c49d7e0343de4debc9e` at the head; before the change, the same command on the `8bc540e0` harness (sha1 `b97e785bf7c062d384a5783b3bee9fbfe844b1e7`).
- Carry B: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_wood_reference.py wood-plant` (sha1 `dfcdcc46269eca76bbdeffacd758522b45165b35`) in an export of the head, rc 0.
- Finder's census: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_rca_sav_estimate.py census` in exports of `af56818b5` and of the head.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh` at the head, exit 0. It printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out`, `STRUCTURE RATCHET PASSED`, `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out`.
- `HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh` at the head: rc 0. It printed `CI PREDICT: no closures, fast, governance or instrument red predicted`, `AGREEMENT ok` and `STRUCTURE RATCHET PASSED` (HEAD merged with origin/main).
- Protected files: `git diff --quiet origin/main HEAD -- VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md tests/golden/card_claimed_drift.txt` exits 0. `tests/golden/claimed_drift.txt` differs from main only by the five `coord_*` claim lines.

## Red checks

At the review head `8bc540e0`, every check run (68 in total, one page of up to 100) was read. Five concluded `failure`; every other run was `success` or `skipped`.

| check run | class | answer |
|---|---|---|
| `CodeQL` (128216329154): `code-scanning alert 50 (py/jinja2/autoescape-false)` | the diff's own | Alert 50 is fixed at `07461bb3`. Root fix: the render harness now builds `jinja2.Environment(autoescape=True)`, and its output is byte-identical (`## Null control`). The cheaper detector would be ruff's bandit rule S701 (`jinja2-autoescape-false`), run before the push. No ruff or bandit is in this repository's toolchain (`venv-ci`), so its standing cost would be a new linter dependency and lane for the one harness directory. CodeQL caught it on the first CI run, before any merge, so this seat builds nothing more; the analysis is `root-cause.md`'s seat if the orchestrator opens one. |
| `pr-contract / pr-contract` (128227675815) | consequence | It refused the body because `## Red checks` did not name `code-scanning alert 50 (py/jinja2/autoescape-false)`. This table names it by that literal check name. |
| `gate` (128227976173, code run 42312136574) | consequence | It failed on `pr-contract / pr-contract: failure (this run)`. It clears with the two rows above. |
| `gate` (128216468204, run 42312137479) and `gate` (128218621028, run 42312767404) | consequence | The edit-run gates deferred to the code run's verdict (`FAIL run(s) [42312136574] at this head are still being judged; their gate decides`). They clear with it. |

No main-wide red: every other check run at `8bc540e0` concluded `success` or `skipped`. The final head has not run CI yet, because it reaches the pull request with this handoff.

## Forward-carry

- The floor's cost on a wood house whose model reads the meter high (the +25.00 % reference at `m` 0.8, measured above) changes no later stage's method. It follows from two owner rulings as built and is stated in `docs/how-it-works.md`. Changing it is the owner's call. Carry: dismissed: owner ruling territory, stated for the owner in docs/how-it-works.md and this body
- The card mutant C3 (`woodNote = false`) survives `tests/card.mjs` and dies only in `tests/card_browser.mjs`, which CI's `tests / browser` lane runs. Carry: R10-HOTFIX-SAV-ESTIMATE | dismissed: covered by the tests browser lane

## Friction

- frugal-routing: cost: a session plugin hook refuses a sixth inline command per prompt, so one locate step went to a cheap subagent. Carry: dismissed: a session plugin outside this repository's policy
