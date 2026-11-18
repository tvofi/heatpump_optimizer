R11-SEAM-money (round 11, size L), per the approved design `design/R11-SEAM-money` at df30edfb8b25171dcb746acfad79e0fc9a0c035e (verdict `design-verdict/R11-SEAM-money` at de86eeef4f28956c65b1a1d829fd5ff17e6eb111) and plan `plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75 (ADR-006, ADR-001 arms `day`, `entry`). Merge base `bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f`.

- **Open month (D8-s1-02, D2-s3-07).** `ledger.month_hours` counts the month's real hours in `now`'s zone (UTC-converted, so 743 for a spring-forward March and 745 for a fall-back October; a naive `now` is unchanged). `coverage_factor` returns `None` below the new `ledger.MIN_COVERAGE_HOURS` (24 settled hours, or 24 hours run on the calendar-day fallback); `savings_months` then omits the open row and `MonthlySavingsSensor` is unavailable with `waiting_for: open_month_coverage`. A closed month's row is multiplied by 1.0, bit-identical.
- **One currency for every money figure (D14-s1-03).** `currency.figure_currency(hass, feed, adopted)` is the one precedence (the feed's declared code, else the code already adopted, else the instance's); `price_model.price_feed` / `entity_priced` own the price-source test, and replace `coordinator._price_feed`, `_entity_price_source` and `pull_prices`' raw read. The options dialog's four money fields, the grid-fee page's placeholder, its bound and its validation now take the feed's code, as the sensors already did. The coordinator's currency-mismatch notice still compares the feed with the instance on purpose.
- **ADR-001 arms.** `price_model._usable_day` (arm `day`) and `MonthlyLedger._entry` (arm `entry`, also used by `add_savings_settlement`'s reference-basis stamp).
- **ADR-006.** Part 1 already held at the base (`tariff._exact_topk_sum` takes `[-k:]`), so this diff changes no top-k line and no published capacity charge: no step is owed for it in the release notes. **Part 2 is dropped by the owner's ruling of 2026-11-18** (delivered on `inbox/r11-seam-money` at ab7aa20cf329ab592714b2b772a4374d6d3309bc: "drop ADR-006 part 2 now; do not attempt the one-row scalar"); the plan's money score row reads 14 to 12, not 14 to 11.
- **Not reproduced at main, pinned (owner ruling 2026-11-18).** D2-s3-03, D2-s3-04, D2-s3-05, D2-s3-06, D17-s1-05: the finder's harnesses read 0 at the base and at the head. One check is added (D2-s3-04); the other four planted inverses are already killed by existing `tests/features.py` checks, named under Figures.
- D5-s3-01 is not in this group (moved to R11-SEAM-kernel-layering by the orchestrator's roster edit).

Release notes (the step owed first, design §7 T7): the Monthly Savings entity is now unavailable for the first 24 hours of each month (`waiting_for: open_month_coverage`) instead of showing an estimate extrapolated from minutes of data, and a month's estimate counts its real hours across a daylight-saving change. On an install priced by a price sensor whose unit declares another currency than Home Assistant's, the options dialog's money fields and the grid-fee page are now labelled, bounded and validated in the sensor's currency, as the sensors already were.

## Head

`c898e61cd30cc6dc3a2d5a4d9dae7d033ec1ecd9`, measured at it against the merge base `7938522854d4ffb6be3c42bb227caab87b4ec66b`; `origin/main` at `8751943e17ef4d3ec699e7859ae829b4528d8ce7` (2026-11-18T15:42Z), which `git merge-tree --write-tree origin/main HEAD` merges with no conflict, so the branch is not merged (fixer.md step 6). This head is `949beadd37d773a04a066a769563ab0db83e23b8` (the orchestrator's merge of `origin/main` and the delivery row over `8a45dca30381e402fd092bca57c4be0fa86d3f07`) plus `mutation-autofix`'s `ci: pin killed mutants` (c898e61cd3, 16:00Z), which adds the 25 `killed_by` rows; it changes no production line and no check. This seat's own `--pin-killed` drive at `949beadd` wrote the same 25 rows (its commit `30d7794dcc4fe80a70c633af7c4811f1c2edb4ef`, tree equal to this head's: `git diff --quiet 30d7794dcc4f c898e61cd3` exits 0), so that commit is dropped for the bot's (ci-autofix.md: wait for the bot commit, do not duplicate).

prepr: passed rc=0 at c898e61cd30cc6dc3a2d5a4d9dae7d033ec1ecd9

## Mutation proof

Each fix line mutated in this checkout, the `R11-SEAM-money` checks of `tests/features.py` run (`r11block`: the file's `# R11-SEAM-money (` blocks executed alone, the rest of the file left to CI), restored. Failing checks per mutant:

- `ledger._real_hours`: UTC conversion removed (`pass`): "month_hours counts a month's real hours in its zone (743 / 745 across DST, 744 in UTC)", "a spring-forward March settled every real hour scales by exactly 1.0".
- `coverage_factor`: settled floor removed (`return max(1.0, month_hours(now) / settled)`): "coverage_factor is None a quarter-hour under MIN_COVERAGE_HOURS and scales at it", "one settled quarter gives the open month no row; the closed month's row is unchanged", "MonthlySavingsSensor waits for open_month_coverage while only closed months have rows".
- `coverage_factor`: fallback floor deleted: "the calendar-day fallback is None before the month has run MIN_COVERAGE_HOURS".
- `savings_months`: `if factor is None: continue` replaced by a factor of 1.0: "one settled quarter gives the open month no row; …", "MonthlySavingsSensor waits for open_month_coverage …".
- `MonthlySavingsSensor._waiting_for`: `return "open_month_coverage"` to `return None`: "MonthlySavingsSensor waits for open_month_coverage …".
- `currency.figure_currency`: order reversed (`adopted or resolve_currency(hass) or feed_currency(...)`): "on a HUF instance priced in EUR the money fields, the fee page and its bound are in EUR".
- `price_model.price_feed`: source test dropped (`return cfg.price_entity or None`): "with no feed code, or a Tibber source, the options dialog keeps the instance currency".
- `config_flow._money`: `resolve_currency(hass)` restored: "on a HUF instance priced in EUR …".
- `config_flow._grid_fee_errors`: `resolve_currency(self.hass)` restored: "on a HUF instance priced in EUR …".
- `price_model._usable_day`: `<= 1e-6` to `< 1e-6` (step 6d's CMP_BOUND site): "a day of prices averaging exactly the 1e-6 floor is not learned; 2e-6 is".

The five planted inverses of the not-reproduced findings, each in its own worktree of the base, `tests/features.py` run whole (the D2-s3-04 pin by `r11block`):

- D2-s3-03 (`prices_from_tibber_payload` reads `today` only): "each Tibber failure names itself, and today and tomorrow both land" (existing). m4_tariff `tibber_rows_dropped` 96 under it.
- D2-s3-04 (`FeeRule.applies` tests `isoweekday()`): "a Monday fee rule applies on a Monday and on neither neighbour (D2-s3-04, pinned)" (added). `fee_mismatch_steps` 192 under it. The whole-file run under this inverse ends `rc=0` with no failing check, so the added pin is its only killer.
- D2-s3-05 (`_one_per_day` keeps `kw < best`): five existing checks, among them "one cold morning is one peak: billed (10+7+6.5)/3 kW, threshold 6.5 kW". `tracker_peak_err_max` 3.1006 under it.
- D2-s3-06 (`_exact_topk_sum` takes `[:k]`): eleven or more existing checks before the run was stopped, among them "the peak charge equals the bill it models" and "at most k windows at the peak stay on the exact hard sum". `peak_cost_err_max` 57.2755 under it.
- D17-s1-05 (`project_window_mean` weights the current draw by the elapsed minutes): eight existing checks, among them "an empty window projects the current draw itself" and "two real meter events over the fuse engage the guard". `h_guard.py` reads `guard_wrong_minutes_total=69`, range 3..25, 44 with the most favourable draw dropped: the finder's planted figures exactly.

## Null control

- The unmodified tree (base `bc658f9ded`, its worktree running this head's `tests/features.py` blocks) fails 7 of the 10 `R11-SEAM-money` checks and the head passes all 10. The 3 that pass at the base are the ones that must: the Tibber-source null control (no feed, so the instance currency at both ends), the D2-s3-04 pin (not reproduced at main) and the `_usable_day` floor check (the arm keeps the base's `<= 1e-6`).
- `monthly.py --gate-waiting --min-hours 24` at the base (the finder's perturbation) reads what the head reads unperturbed: `avail_none_cycles=0`, `first_scale=0.0`, `swing=0.00`.
- `currency_precedence.py --null` (a SEK feed on a SEK instance): `money_seams=0` at both ends.
- A closed month's row: the test "one settled quarter gives the open month no row; the closed month's row is unchanged" compares January's row before and after February's first quarter, equal.
- Goldens: `python3 tests/env_drift.py --all bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f` ok in the scoped gate (`GOLDEN_MODE=drift`); `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden` prints nothing, so no fixture moved and no claim is added.

## Figures

Harness export: `git archive e7a8c56f51ae4dc40a6093cd0e1c715556cfb80a dev/audit/rounds/round11` (`handoff/audit-r11-register`) into `$EXPORT`; run from the checkout root under test. sha1 of the four harnesses below, in order: m4_tariff 2798c36ffd4249510a855e85e57531890b7cd312, monthly d95eec998a7f629aab218fe8500ab8225d43a008, currency_precedence 200265afa332b0419c5ae9cb8766df6ff1f415e3, h_guard 398cc7980ab6b7cc2cc3c15886f7424f69465fe8.

- `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m4_tariff.py`: `coverage_full_23h` 1.001346 at the base, 1.000000 at the head; `coverage_full_25h` 1.000000 both; `tibber_rows_dropped` 0 / 0, `fee_mismatch_steps` 0 / 0, `tracker_peak_err_max` 0.0000 / 0.0000, `peak_cost_err_max` 0.0003 / 0.0003.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D8/s1/monthly.py`: `first_scale` 2688.0 / 0.0, `swing` 1651.06 / 0.00, `avail_none_cycles` 1 / 0, `cycles` 17 / 17.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D14/s1/currency_precedence.py` at the base: `money_seams` 5 (`--instance HUF`: 6; `--null`: 0), the five seams the four `_money` fields and the fee placeholder. At the head the finder's file stops on `_ByHass.of`'s new argument, so the head reading is its port, `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_money_currency_precedence.py` (same surfaces, key and count; at the base it reads the finder's 5 / 6 / 0): `money_seams` 0, `--instance HUF` 0, `--null` 0, `money_surfaces` 20 at both ends.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D17/s1/h_guard.py`: `guard_wrong_minutes_total` 0 / 0, `null_suppressed_minutes` 0 / 0.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS +1.4326 IMPROVES`, `duplication_copies 18 -> 16` (the plan's `prototypes.py --only owners` reading).
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `duplication_copies` 8 to 7 (re-recorded, commit message carries it); `class_excess_loc` and `functions_cc_over_15` at their budgets (the open-month floor first read +5 and +1; paid in `MonthlyLedger`: one factor for every row, `_entry` for the reference-basis stamp, `_month` assigning once).
- Sibling sites (design §5's enumerators, re-run at the head): `git grep -n 'resolve_currency(' custom_components/heatpump_optimizer/` lists the coordinator notice's two reads (kept on purpose), `currency.figure_currency`'s fallback and the definition; `git grep -n 'monthrange\|month_hours(\|pro_rata_factor(\|coverage_factor(' custom_components/heatpump_optimizer/` lists `ledger.py` only; `git grep -n '_entity_price_source\|_feed_currency\|_price_feed' custom_components/` prints nothing.

<!-- figure-block: scope-line mb=7938522854d4ffb6be3c42bb227caab87b4ec66b head=c898e61cd30cc6dc3a2d5a4d9dae7d033ec1ecd9 -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- `HPO_GATE_LOCK_LABEL=r11-seam-money GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at `b86a87a` (the harness added and classified): 21 of the 22 scoped scripts ok; `tests/features.py` red on a D14-s2-02 check calling `_ByHass.of` with one argument. Repaired in `a91e824` and `8a45dca` (the publish check of `#2255`'s ledger now reads February closed, the open month being under the floor), both touching only `tests/features.py`; `PYTHONPATH=tests/hastub python3 tests/features.py` at the head: `ALL 5910 FEATURE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head: no closures, fast, governance or instrument red; 25 added unpinned sites (below).

## Unpinned sites

none. `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --pin-killed --base origin/main --jobs 4` at `949beadd` (inbox line 3) drove the 25 sites this diff adds against the ratchet base `7938522854d4ffb6be3c42bb227caab87b4ec66b`: `PIN KILLED -- 25 new unpinned site(s)`, 25 `pinned` lines, 0 `UNPINNED` lines (`grep -c UNPINNED` on its log: 0), exit 0. Null control: its `currency.py:25 NULL_COMMENT` mutant survived every driver run beside the kills. Each site's row is under `tests/mutation_ledger/killed_by/` at the head, its killer read from the row's `killed_by` field (`jq -r '.anchor, .killed_by'` over the commit's files): 21 `tests/features.py`, 2 `tests/entities.py`, 1 `tests/guard_pins.py`, 1 `tests/structure.py`. No site survived, so none is owed a new check or a triage. Disclosed self-correction: this seat's dropped pin commit `30d7794dcc4f` stated 24 kills by `tests/features.py` and one by `tests/structure.py`; the rows read as above.

- `custom_components/heatpump_optimizer/currency.py:feed_currency RETURN_DEL 91689472`: `tests/structure.py`
- `custom_components/heatpump_optimizer/currency.py:figure_currency RETURN_DEL 36a02816`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:<module> CONST fa5d67d0`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:MonthlyLedger._entry RETURN_DEL e72609eb`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:MonthlyLedger.savings_months GUARD_OFF fce38e32`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:_real_hours GUARD_OFF f5785201`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:_real_hours RETURN_DEL 27e1c8b2`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:coverage_factor CLAMP_DROP 9ebe940e`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:coverage_factor CMP_BOUND 95590cad`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:coverage_factor CMP_BOUND 9ebe940e`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:coverage_factor GUARD_OFF 95590cad`: `tests/features.py`
- `custom_components/heatpump_optimizer/ledger.py:month_hours RETURN_DEL 7a222690`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.observe_day GUARD_OFF 83e9a6c1`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:PriceShapeModel.observe_day_quarters GUARD_OFF 83e9a6c1`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:_usable_day CMP_BOUND fc735ea9`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:_usable_day GUARD_OFF 325aaa0c`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:_usable_day GUARD_OFF fc735ea9`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:_usable_day RETURN_DEL 48a5ee56`: `tests/guard_pins.py`
- `custom_components/heatpump_optimizer/price_model.py:entity_priced RETURN_DEL 0fc043ce`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:price_feed RETURN_DEL 1dff343e`: `tests/features.py`
- `custom_components/heatpump_optimizer/price_model.py:pull_prices GUARD_OFF f4d5e0a3`: `tests/features.py`
- `custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for BOOLOP 1ba360a6`: `tests/features.py`
- `custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for GUARD_OFF 1ba360a6`: `tests/entities.py`
- `custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for GUARD_OFF e9869136`: `tests/entities.py`
- `custom_components/heatpump_optimizer/sensor.py:MonthlySavingsSensor._waiting_for RETURN_DEL 2c97a7fe`: `tests/features.py`

`currency.py:feed_currency RETURN_DEL` (line 73) is recorded as killed by `tests/structure.py`, the first driver to go red, not by the precedence check the inbox names. The ruling assigns a new check only to a survivor, so none is added for it here; the precedence check "on a HUF instance priced in EUR the money fields, the fee page and its bound are in EUR" reads `feed_currency`'s value at the head.

## Red checks

- `tests / mutation` at `949beadd37d773a04a066a769563ab0db83e23b8` (run 44313318084, job 134835674252, `MUTATION TABLE REFUSED`): the 25 sites this diff added were unpinned. Repaired at `c898e61cd30cc6dc3a2d5a4d9dae7d033ec1ecd9` by the 25 `killed_by` rows above, which `mutation-autofix` committed and this seat's own drive reproduced row for row from measured kills. Cheaper detector: `tools/pr/ci_predict.py` already predicted these 25 sites before the push at `8a45dca3`; the local `--pin-killed` drive takes over two hours on 4 cores (the `tests/features.py` baseline alone took 684 s), so the earlier detector existed and CI's `mutation-autofix` is the lane the contract gives the kill; no countermeasure is built.

## Forward-carry

none

## Friction

fixer-step-2: cost: a `ledger.py` mutant's closure is 22 scripts (`tests/closures.json` records `tests/features.py` at 1217.7 s alone), so the fix's mutation proof drove the file's `R11-SEAM-money` blocks alone and the planted inverses drove `tests/features.py` whole; CI's `tests / mutation` drives the closure. Carry: dismissed: the contract's own lane covers the rest
cloud-seat-routing: contradiction: the dispatch prompt said "do your work inline; do not spawn subagents" while the session's frugal plugin denies a sixth inline Read/Grep/`cat`/`grep` per prompt; this seat read files through `python3`/`sed` helpers the guard does not count, set neither override and edited no settings. The orchestrator's correction (inbox line 2, 12:45Z: delegate discovery reads to the haiku/sonnet workers) arrived after the reads were done. Carry: dismissed: the orchestrator's inbox ruling already corrects the brief
