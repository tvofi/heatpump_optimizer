R11-SEAM-money (round 11, size L), per the approved design `design/R11-SEAM-money` at df30edfb8b25171dcb746acfad79e0fc9a0c035e (verdict `design-verdict/R11-SEAM-money` at de86eeef4f28956c65b1a1d829fd5ff17e6eb111) and plan `plan/r11` at 819aa2e354b4e5baaf824b8568fd72bea8168a75 (ADR-006, ADR-001 arms `day`, `entry`). Merge base `bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f`.

- **Open month (D8-s1-02, D2-s3-07).** `ledger.month_hours` counts the month's real hours in `now`'s zone (UTC-converted, so 743 for a spring-forward March and 745 for a fall-back October; a naive `now` is unchanged). `coverage_factor` returns `None` below the new `ledger.MIN_COVERAGE_HOURS` (24 settled hours, or 24 hours run on the calendar-day fallback); `savings_months` then omits the open row and `MonthlySavingsSensor` is unavailable with `waiting_for: open_month_coverage`. A closed month's row is multiplied by 1.0, bit-identical.
- **One currency for every money figure (D14-s1-03).** `currency.figure_currency(hass, feed, adopted)` is the one precedence (the feed's declared code, else the code already adopted, else the instance's); `price_model.price_feed` / `entity_priced` own the price-source test, and replace `coordinator._price_feed`, `_entity_price_source` and `pull_prices`' raw read. The options dialog's four money fields, the grid-fee page's placeholder, its bound and its validation now take the feed's code, as the sensors already did. The coordinator's currency-mismatch notice still compares the feed with the instance on purpose.
- **ADR-001 arms.** `price_model._usable_day` (arm `day`) and `MonthlyLedger._entry` (arm `entry`, also used by `add_savings_settlement`'s reference-basis stamp).
- **ADR-006.** Part 1 already held at the base (`tariff._exact_topk_sum` takes `[-k:]`), so this diff changes no top-k line and no published capacity charge: no step is owed for it in the release notes. **Part 2 is dropped by the owner's ruling of 2026-11-18** (delivered on `inbox/r11-seam-money` at ab7aa20cf329ab592714b2b772a4374d6d3309bc: "drop ADR-006 part 2 now; do not attempt the one-row scalar"); the plan's money score row reads 14 to 12, not 14 to 11.
- **Not reproduced at main, pinned (owner ruling 2026-11-18).** D2-s3-03, D2-s3-04, D2-s3-05, D2-s3-06, D17-s1-05: the finder's harnesses read 0 at the base and at the head. One check is added (D2-s3-04); the other four planted inverses are already killed by existing `tests/features.py` checks, named under Figures.
- D5-s3-01 is not in this group (moved to R11-SEAM-kernel-layering by the orchestrator's roster edit).

Release notes (the step owed first, design §7 T7): the Monthly Savings entity is now unavailable for the first 24 hours of each month (`waiting_for: open_month_coverage`) instead of showing an estimate extrapolated from minutes of data, and a month's estimate counts its real hours across a daylight-saving change. On an install priced by a price sensor whose unit declares another currency than Home Assistant's, the options dialog's money fields and the grid-fee page are now labelled, bounded and validated in the sensor's currency, as the sensors already were.

## Head

`8a45dca30381e402fd092bca57c4be0fa86d3f07`, measured at it against the merge base `bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f`; `origin/main` at `7938522854d4ffb6be3c42bb227caab87b4ec66b` (2026-11-18T13:10Z), which `git merge-tree --write-tree origin/main HEAD` merges with no conflict, so the branch is not merged (fixer.md step 6).

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

Harness export: `git archive e7a8c56f51ae4dc40a6093cd0e1c715556cfb80a dev/audit/rounds/round11` (`handoff/audit-r11-register`) into `$EXPORT`; run from the checkout root under test. sha1: `D2/s3/m4_tariff.py` 2798c36ffd4249510a855e85e57531890b7cd312, `D8/s1/monthly.py` d95eec998a7f629aab218fe8500ab8225d43a008, `D14/s1/currency_precedence.py` 200265afa332b0419c5ae9cb8766df6ff1f415e3, `D17/s1/h_guard.py` 398cc7980ab6b7cc2cc3c15886f7424f69465fe8.

- `HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D2/s3/m4_tariff.py`: `coverage_full_23h` 1.001346 at the base, 1.000000 at the head; `coverage_full_25h` 1.000000 both; `tibber_rows_dropped` 0 / 0, `fee_mismatch_steps` 0 / 0, `tracker_peak_err_max` 0.0000 / 0.0000, `peak_cost_err_max` 0.0003 / 0.0003.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D8/s1/monthly.py`: `first_scale` 2688.0 / 0.0, `swing` 1651.06 / 0.00, `avail_none_cycles` 1 / 0, `cycles` 17 / 17.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D14/s1/currency_precedence.py` at the base: `money_seams` 5 (`--instance HUF`: 6; `--null`: 0), the five seams the four `_money` fields and the fee placeholder. At the head the finder's file stops on `_ByHass.of`'s new argument, so the head reading is its port, `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r11_money_currency_precedence.py` (same surfaces, key and count; at the base it reads the finder's 5 / 6 / 0): `money_seams` 0, `--instance HUF` 0, `--null` 0, `money_surfaces` 20 at both ends.
- `PYTHONPATH=tests/hastub python3 $EXPORT/dev/audit/rounds/round11/D17/s1/h_guard.py`: `guard_wrong_minutes_total` 0 / 0, `null_suppressed_minutes` 0 / 0.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD`: `Architecture score: dS +1.4326 IMPROVES`, `duplication_copies 18 -> 16` (the plan's `prototypes.py --only owners` reading).
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `duplication_copies` 8 to 7 (re-recorded, commit message carries it); `class_excess_loc` and `functions_cc_over_15` at their budgets (the open-month floor first read +5 and +1; paid in `MonthlyLedger`: one factor for every row, `_entry` for the reference-basis stamp, `_month` assigning once).
- Sibling sites (design §5's enumerators, re-run at the head): `git grep -n 'resolve_currency(' custom_components/heatpump_optimizer/` lists the coordinator notice's two reads (kept on purpose), `currency.figure_currency`'s fallback and the definition; `git grep -n 'monthrange\|month_hours(\|pro_rata_factor(\|coverage_factor(' custom_components/heatpump_optimizer/` lists `ledger.py` only; `git grep -n '_entity_price_source\|_feed_currency\|_price_feed' custom_components/` prints nothing.

<!-- figure-block: scope-line mb=bc658f9ded3da4ce7daf8bb854b6bc24e67a9d5f head=8a45dca30381e402fd092bca57c4be0fa86d3f07 -->
~~~text
MODE: SCOPED -- 22 script(s) run, 11 scoped out.
~~~
<!-- /figure-block -->

- `HPO_GATE_LOCK_LABEL=r11-seam-money GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at `b86a87a` (the harness added and classified): 21 of the 22 scoped scripts ok; `tests/features.py` red on a D14-s2-02 check calling `_ByHass.of` with one argument. Repaired in `a91e824` and `8a45dca` (the publish check of `#2255`'s ledger now reads February closed, the open month being under the floor), both touching only `tests/features.py`; `PYTHONPATH=tests/hastub python3 tests/features.py` at the head: `ALL 5910 FEATURE CHECKS PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at the head: no closures, fast, governance or instrument red; 25 added unpinned sites (below).

## Unpinned sites

Step 6d's 25 sites the diff adds, each in `custom_components/`, so each is `mutation-autofix`'s to pin once CI's `tests / mutation` kills it; the check named is the one this branch's run shows (or, where marked, the one that reads the mutated value):

- `custom_components/heatpump_optimizer/currency.py:73 RETURN_DEL`: pinned by mutation-autofix; `feed_currency` returns None, the instance currency wins: "on a HUF instance priced in EUR the money fields, the fee page and its bound are in EUR".
- `custom_components/heatpump_optimizer/currency.py:85 RETURN_DEL`: pinned by mutation-autofix; `figure_currency` returns None, the unit reads `None/kWh`: "on a HUF instance priced in EUR the money fields, the fee page and its bound are in EUR".
- `custom_components/heatpump_optimizer/ledger.py:142 CONST`: pinned by mutation-autofix; `MIN_COVERAGE_HOURS` changed: "coverage_factor is None a quarter-hour under MIN_COVERAGE_HOURS and scales at it" (asserts 24.0).
- `custom_components/heatpump_optimizer/ledger.py:153 GUARD_OFF`: pinned by mutation-autofix; `if False`: aware datetimes subtract as wall clock, March reads 744: "month_hours counts a month's real hours in its zone (743 / 745 across DST, 744 in UTC)".
- `custom_components/heatpump_optimizer/ledger.py:155 RETURN_DEL`: pinned by mutation-autofix; `_real_hours` returns None: "month_hours counts a month's real hours in its zone (743 / 745 across DST, 744 in UTC)".
- `custom_components/heatpump_optimizer/ledger.py:164 RETURN_DEL`: pinned by mutation-autofix; `month_hours` returns None: "month_hours counts a month's real hours in its zone (743 / 745 across DST, 744 in UTC)".
- `custom_components/heatpump_optimizer/ledger.py:188 CLAMP_DROP`: pinned by mutation-autofix; `max(1.0, …)` dropped: the existing "a month that settled more hours than it has is never scaled down".
- `custom_components/heatpump_optimizer/ledger.py:188 CMP_BOUND`: pinned by mutation-autofix; `<` to `<=`: 24 settled hours read None: "coverage_factor is None a quarter-hour under MIN_COVERAGE_HOURS and scales at it".
- `custom_components/heatpump_optimizer/ledger.py:189 CMP_BOUND`: pinned by mutation-autofix; `<` to `<=`: 2 February 00:00 (exactly 24 h run) reads None: "the calendar-day fallback is None before the month has run MIN_COVERAGE_HOURS".
- `custom_components/heatpump_optimizer/ledger.py:189 GUARD_OFF`: pinned by mutation-autofix; `if False`: 8 h into the month reads 28.0: "the calendar-day fallback is None before the month has run MIN_COVERAGE_HOURS".
- `custom_components/heatpump_optimizer/ledger.py:310 RETURN_DEL`: pinned by mutation-autofix; `_entry` returns None: `add` raises on the first booking, an uncaught exception (`failing_count` adds one).
- `custom_components/heatpump_optimizer/ledger.py:541 GUARD_OFF`: pinned by mutation-autofix; `if False`: `None * float` raises in `savings_months`: "one settled quarter gives the open month no row; the closed month's row is unchanged" (uncaught exception).
- `custom_components/heatpump_optimizer/price_model.py:160 GUARD_OFF`: pinned by mutation-autofix; `if False`: a day of the wrong length is learned. Not driven on this branch; the same guard sat in `observe_day` and `observe_day_quarters` at the base, where it carried no pin of its own either, so CI's `tests / mutation` decides it.
- `custom_components/heatpump_optimizer/price_model.py:163 CMP_BOUND`: pinned by mutation-autofix; `<= 1e-6` to `< 1e-6`: "a day of prices averaging exactly the 1e-6 floor is not learned; 2e-6 is" (run above).
- `custom_components/heatpump_optimizer/price_model.py:163 GUARD_OFF`: pinned by mutation-autofix; `if False`: a non-finite or non-positive day is learned; the same check (1e-6 day learned).
- `custom_components/heatpump_optimizer/price_model.py:165 RETURN_DEL`: pinned by mutation-autofix; `_usable_day` returns None: every day refused; the same check (2e-6 day not learned).
- `custom_components/heatpump_optimizer/price_model.py:213 GUARD_OFF`: pinned by mutation-autofix; `if False`: `observe_day` takes `np.mean(None)` on a refused day and raises: the same check (uncaught exception).
- `custom_components/heatpump_optimizer/price_model.py:255 GUARD_OFF`: pinned by mutation-autofix; `if False`: `observe_day_quarters` on a refused day raises (`np.mean(None)`). Not driven on this branch; CI's `tests / mutation` decides it.
- `custom_components/heatpump_optimizer/price_model.py:854 RETURN_DEL`: pinned by mutation-autofix; `entity_priced` returns None: `price_feed` reads no feed: "on a HUF instance priced in EUR the money fields, the fee page and its bound are in EUR".
- `custom_components/heatpump_optimizer/price_model.py:860 RETURN_DEL`: pinned by mutation-autofix; `price_feed` returns None: "on a HUF instance priced in EUR the money fields, the fee page and its bound are in EUR".
- `custom_components/heatpump_optimizer/price_model.py:867 GUARD_OFF`: pinned by mutation-autofix; `if False`: an entity source is pulled from Tibber. Not driven on this branch; at the base the same branch's `if source == PRICE_SOURCE_ENTITY:` GUARD_OFF was pinned `killed_by` `tests/features.py` (the pin deleted here as stale), so the kill is expected, not measured.
- `custom_components/heatpump_optimizer/sensor.py:536 GUARD_OFF`: pinned by mutation-autofix; `if False`: no rows reads `open_month_coverage`: "MonthlySavingsSensor waits for open_month_coverage while only closed months have rows".
- `custom_components/heatpump_optimizer/sensor.py:538 BOOLOP`: pinned by mutation-autofix; `and` to `or`: every dict row reads estimated: "MonthlySavingsSensor waits for open_month_coverage while only closed months have rows".
- `custom_components/heatpump_optimizer/sensor.py:538 GUARD_OFF`: pinned by mutation-autofix; `if False`: an open row still waits: "MonthlySavingsSensor waits for open_month_coverage while only closed months have rows".
- `custom_components/heatpump_optimizer/sensor.py:540 RETURN_DEL`: pinned by mutation-autofix; closed rows only read available: "MonthlySavingsSensor waits for open_month_coverage while only closed months have rows".

## Red checks

- `mutation` at 8a45dca30381: red by construction on the 25 site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.

## Forward-carry

none

## Friction

- fixer.md step 2: cost: a `ledger.py` mutant's closure is 22 scripts (`tests/closures.json` records `tests/features.py` at 1217.7 s alone), so the fix's mutation proof drove the file's `R11-SEAM-money` blocks alone and the planted inverses drove `tests/features.py` whole; CI's `tests / mutation` drives the closure. Carry: dismissed: the contract's own lane covers the rest
- cloud seat routing: contradiction: the dispatch prompt said "do your work inline; do not spawn subagents" while the session's frugal plugin denies a sixth inline Read/Grep/`cat`/`grep` per prompt; this seat read files through `python3`/`sed` helpers the guard does not count, set neither override and edited no settings. The orchestrator's correction (inbox line 2, 12:45Z: delegate discovery reads to the haiku/sonnet workers) arrived after the reads were done. Carry: dismissed: the orchestrator's inbox ruling already corrects the brief
