This is roster group R10-FEEDS: the coordinator's price and weather ingest seam. It covers four bug classes from round 10, and it builds the class barrier both round-10 RCAs (`dev/audit/rca/R10-N-no-expiry.md` and `dev/audit/rca/R10-N-log-flood.md`) say is owed in this pull request.

Closes #2229.
Closes #2233.

Closes #2226. `dev/audit/rca/R10-N-log-flood.md`'s countermeasure is built here: its part 1 (the transition-latch helper, the 7 probed instance sites routed through it) and its part 2 (the static arm over the sweep's own reasoned list). The 8 sites the arm lists as OWED are on that reasoned list, which is what part 2 asks for; 5 of them are the sweep's "static evidence only, runtime probe owed" set, and 3 (`optimizer.py`) are new — the arm found them, and they are the "Distinct finding" below.
Part of #2236. The class issue covers seams outside this group. D1-s3-02 and its `_current_spot_price` sibling are fixed here.

**N-no-expiry (#2229).**
- New: one covering-slot helper, `coordinator._covering_index`. It is `_known_prices_for`'s end rule, extracted. An entry covers `[start, next start)`. The last entry covers one predecessor's span, or a given span when it is the only entry. Nothing covers before the first entry or after the end.
- These go through the helper:
  - `_known_prices_for`;
  - `_current_spot_price`, which is now `_known_prices_for([now])`;
  - `forecast_outdoor_now`, which keeps its documented "before the first entry, use the first" rule;
  - `_open_loop_plan_value`, which keeps its 900 s lead rule.
- When no price covers now, the distinct failure value is `None`. It used to be the last entry forever, or `0.0` with no prices at all. `None` travels through `_get_current_price`.
- The consumers of the two getters now handle `None`. Each change was approved by the orchestrator, and the hunks outside the ingest seam are listed below:
  - The published `current_price` is `None`, which the sensor already shows as unknown.
  - The settlement books the interval's kWh into the energy totals and no cost. A NaN spot is refused line by line by the ledger's own `add`/`observe_meta_mean`, so no zero price enters the month mean.
  - The accuracy sample records `predicted_cost`/`actual_cost` as `None`, which the tracker's pairing already skips.
  - The score day takes no unpriced kWh.
  - A setpoint override uses a neutral relative price (1.0).
  - sysid's `conditions_met` refuses to start.

**N-silent-zero (#2233).**
- `prices_from_tibber_payload` returns a failure reason when a subscription yields no usable row. An HTTP 200 with empty days therefore fails the fetch (latched ERROR, `UpdateFailed`) and keeps the held series. Before, it replaced the series with nothing and reported success.
- `_fetch_weather_forecast` applies the same rule. Rows that all fail plausibility are a failed fetch, and the held forecast is kept and marked stale.
- One design choice is kept and named here (fixer.md step 11). A home with no current subscription still returns `[]` as a successful fetch of nothing. `tests/features.py` pins this ("each Tibber failure names itself..."): the API answered, and the account has no contract. Any held prices still expire through the covering rule.

**P1 D1-s3-02 (#2236).**
- `_raw_start` now validates that the start is a timestamp (`datetime.fromisoformat`), and the Tibber parser uses it. That gives one start rule for both ingress paths.
- The positional fallbacks are deleted: `_known_prices_for`'s untimestamped branch and `_current_spot_price`'s list-head branch.
- Two existing checks changed meaning deliberately, and their texts say so:
  - "a half-formed price series ..." used to pin "`_raw_start` normalises and does not validate".
  - "untimestamped prices take the same hourly positional assumption" now reads `[]`.

**N-log-flood (#2226).**
- `coordinator._log_held(owner, key, active, message, *args)` is a transition latch. It logs WARNING when a condition starts or its text changes, DEBUG while the condition holds, and INFO when it clears.
- Its state is a module `WeakKeyDictionary` side table, on boost.py's precedent, so it adds no coordinator attribute. No helper of this kind existed: `grep -rnE "def [a-z_]*(latch|once|warn_)|_warned|log_once|warn_once"` over the package finds only one per-site flag (`_external_probe_stale_warned`).
- These sites route through it: `_weather_series`, `_fetch_solar_forecast`, `_solar_location`, and both of `_price_series`'s warnings.
- Two sites in the TARIFF area take a different route:
  - `_tariff_months` and `_tariff_hours`, whose bodies moved to the module functions `_peak_tariff_months` and `_peak_tariff_hours`. These are pure and `lru_cache`d per option text, so a malformed option warns once per distinct text. It also parses once, instead of on each of `_capacity_tariff`'s four reads per cycle. #2282 is merged, so these lines do not conflict.
  - `async_run_optimization`'s "Not enough price data" is now DEBUG. It fires only when `_price_series` returned None, and that call has already logged the reason, latched.

**The class barriers.** Both are AST arms appended to `tests/entities.py`. Each allow-list is keyed (module, function) to an EXACT count, and every entry carries its reason:
- N-no-expiry: every `bisect_right(...) - 1` outside `_covering_index` must be on the reasoned list. The list holds `_weather_series`, `early_cutoff._planned_room`, `pump_arbiter._planned_room`, `pump_arbiter.step_duty` and `pump_arbiter._share`, with the R10 sweep's dispositions.
- N-log-flood: every unlatched `_LOGGER.warning/.error` must be on the list, grouped under five reasons. The rule is the R10 sweep's static rule.

Both arms carry their own planted controls: a new unbounded lookup, a new unlatched warning, and a second site inside a listed function are each refused, and a latched warning is not a site.

One non-vacuity number is deliberately translated, and the choice is recorded here rather than left to read as a weakening. The RCA asks the log arm to show "the number of sites read is at least 85", which is the base's count. At this head the read is **74**: the enumerator prints `sites=80 latched=6 seams=74` against the base's `85/6/79`. The seam sets differ by 8 call sites out and 3 in: out are 5 routed through `_log_held` (in 4 functions), 2 (`_tariff_months`, `_tariff_hours`) moved to the two module parsers, and `async_run_optimization`'s demoted to DEBUG; in are `_log_held` itself and the two parsers. 79 - 8 + 3 = 74. An exact floor would refuse the next legitimate fix that latches one more site, so the arm asserts `>= 70` beside `len(sources) >= 70`, which is what its purpose — catching an empty or truncated read — needs; a truncated read also fails the exact-count comparison loudly.

**Hunks outside the ingest seam, each approved by the orchestrator:**
- in `coordinator.py`: `_accumulate_energy`, `_record_accuracy`'s cost lines, `_fold_score_sample`, `record_setpoint_override`, `async_run_optimization`'s one log line, and `_tariff_months`/`_tariff_hours`;
- `sysid.py` `conditions_met` (and `step`'s annotation);
- `payload.py`: `CurrentAction.price` and `GridView.current_price` become `float | None`.

**Ledger.** Seven `tests/mutation_ledger/killed_by` pins named lines this diff deleted or re-indented, and they are removed. The measurement is a counterfactual, because a deleted pin leaves no trace in the head's own ledger: the base's ledger read against the head's deterministic `inventory()` reports exactly those seven ("disposition names no site the inventory generates"), and the head's ledger against the same inventory reports 0. See `## Figures`.

**Fixtures that relied on a removed fallback.** Each now carries its hours:
- `tests/solar_alignment.py`, two coordinators;
- `tests/features.py`: the cheap-hour override, the #1523 sysid night and the g8 spot read.

## Head

`a0c4431df91e75b3c7ed4976586c0da86e292214` adds the four `survivor_triage` rows for this diff's surviving mutants and this pull request's own delivery row `dev/programme/delivery/2336.md`, on top of the mutation-autofix head `fba6de8de2712ed6bb771f15a5574d3eb92c5f51`, which pinned 30 of the 34 sites the `mutation` lane refused. No production or test code changes.

`8921b4825d260ff46a4d87779eeaf7784642f264` merges origin/main `8f174c4ce` into the authored code head `b0542727974af8992f1fcbd9355b7af536d45907` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`b0542727974af8992f1fcbd9355b7af536d45907`. This is `313fa04c5fe6f6a652122b828e2beacf6f5da324` with origin/main `e8718ec3b52e` merged. **Every figure below was re-taken at this head**: the finder harnesses at both ends, the class enumerators, the mutation proof, the gate scope, `tests/structure.py`, the architecture score and `tmp_paths`. The merge changed nothing the measurements read: three-dot `git diff --stat 7215e39df7a1..e8718ec3b -- custom_components` is one file, `www/heatpump-optimizer-card.js`; main added no change to the round-10 harnesses, to `tests/features.py`, `tests/entities.py` or `tests/solar_alignment.py`, and the mutation ledger it grew shares no pin with the seven this diff removes.

## Mutation proof

The tests were written first. Run at the merge-base production code (`git archive` of `7215e39df7a1`), the new block stops at its first new symbol: `AttributeError: module 'heatpump_optimizer.coordinator' has no attribute '_covering_index'`. The behaviour it pins is read at the baseline by the finder harnesses below.

Each mutant inverts or deletes one fix predicate in a fresh `git archive` of the head. The mutant then runs the PR's 16-check R10-FEEDS block, which is the block appended to `tests/features.py` with that file's import header. M0 is the unmutated head. Driver: `fixwave/R10-FEEDS/mutate.py`; output: `fixwave/R10-FEEDS/ev/mutation-ad523be5c210.out`.

| mutant | verdict | failing checks |
|---|---|---|
| M0 none (null control) | clean, rc 0 | none |
| M1 `_covering_index` end bound -> `return i` | killed | the covering arm, the stale price list, the forecast/plan-seed siblings |
| M2 `return prices or "..."` -> `return prices` | killed | the Tibber body arm, the HTTP-200-empty fetch |
| M3 `_raw_start` validation removed | killed | the Tibber body arm, one start rule for both paths |
| M4 `_log_held` `held.get(key) == text` -> `False` | killed | the latch transitions, the four-cycle flood |
| M5 weather `if forecast_data:` -> `if True:` | killed | the all-implausible forecast arm |
| M6 settlement `if known_price is not None:` -> `if True:` | killed | the unpriced interval books no cost |
| M7 override `spot is not None and` dropped | killed (TypeError) | the neutral relative price arm |
| M8 sysid `if price is None:` -> `if False:` | killed (TypeError) | the sysid refusal arm |
| M9 accuracy `if price is not None` -> `(price or 0.0) ... if True` | killed | the accuracy sample records no cost |
| M10 `lru_cache` dropped from `_peak_tariff_months` | killed | the four-cycle flood |
| M11 `forecast_outdoor_now` past the end -> last entry | killed | the forecast/plan-seed siblings |
| M12 score day `if spot_known and isfinite(sek)` -> `if True` | killed | the score day takes no unpriced kWh |

The two barrier arms carry their own perturbations: the planted lookup and warning, and a second site in a listed function.

## Null control

Each finder harness's own control reads the same at both ends:
- `stale_price.py` `control_covered_published=2`: a covered cycle still publishes exactly as at the base.
- `probe_n_no_expiry.py` `CONTROL covered forecast=-2.0 plan=49.5`.
- `log_flood/probe.py` `control.floods=0`.
- `weather_warn.py` `control_48_rows.warnings_4_cycles=0`.

Every arm of the new block pairs its defect input with a covered or healthy input that must read as before: a covered hour, a 96-row good body, a good 48-row forecast, a priced interval, a priced accuracy sample and a priced score sample.

## Figures

Finder harnesses, each run from the tree path, with its blob sha1 prefix (`git hash-object`). The base is a fresh `git archive origin/main` of `e8718ec3b52e`, re-taken at this head; the harness blobs are unchanged from `7215e39df7a1`, so the same sha1s cite them. Outputs are `fixwave/R10-FEEDS/ev/base-e8718ec3b/` and `fixwave/R10-FEEDS/ev/head-b0542727/`.

- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/stale_price.py` (5471a61a4342): `uncovered_current_price_published` 4 -> 0, `uncovered_price_booked` 4 -> 0, over `uncovered_cycles=4`; `control_covered_published` 2 -> 2.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s3/tibber_ingress.py` (f05a0870d46c): `empty_ok_wipes` 1 -> 0, `startless_rows` 96 -> 0, `misplaced_steps` 95 -> 0.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D1/s2/weather_warn.py` (52fca455b98b): `no_entity.warnings_4_cycles` 4 -> 1, `empty_forecast.warnings_4_cycles` 4 -> 1; control 0 -> 0.
- `PYTHONPATH=.:tests/hastub python3 dev/audit/rounds/round10/D14/probe_n_no_expiry.py` (404a33eede41): `probe_failures` 2 -> 0. Past the end: `forecast_outdoor_now` 0.0 -> None, `_open_loop_plan_value` 44.5 -> None.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-silent-zero/weather_probe.py` (3d751c49d77d): `empty_ok_wipes` 1 -> 0.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P1/probe_spot_head.py` (0c5f7cffb467): `spot_wrong` 1 -> 0.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/log_flood/probe.py` (74a7578dc969). Floods per arm go to 0 on every arm:
  - `no_weather_entity` 1, `weather_fetch_fails` 1, `open_meteo_no_coord` 1, `open_meteo_bad_coord` 2, `no_prices` 2, `bad_peak_months` 1, `bad_peak_hours` 1, all -> 0;
  - `control` 0 -> 0.

Class enumerators (fixer.md step 8). Each names a rule, and every seam it returns at the head is dispositioned:
- `python3 dev/audit/rounds/round10/D14/sweep_n_no_expiry.py` (6cd8af3def97): seams 9 -> 6, `unbounded` 6 -> 4. The four, by its syntactic rule:
  - `_covering_index`: the helper itself, bounded by `now < starts[i] + span`, which the rule's `end`/`timedelta` test does not read.
  - `_weather_series`: not applicable, horizon extrapolation.
  - `early_cutoff._planned_room`: guarded.
  - `pump_arbiter._planned_room`: guarded, per the sweep.

  All six are the `tests/entities.py` N-no-expiry allow-list, with exact counts.

- `python3 dev/audit/rounds/round10/D14/sweep_n_no_expiry.py --perturb` (6cd8af3def97): **this arm no longer runs at the head, and this diff is why.** Its perturbation is a one-line cut of `_known_prices_for`'s own text, `            if step_start >= end:` then `                break`, removed by `str.replace` under `assert cut != body, "perturbation anchor missing"`. That end rule is exactly what this pull request moved into `_covering_index`, so the anchor is gone at the head while it stands at the merge base: `grep -n "step_start >= end" custom_components/heatpump_optimizer/coordinator.py` prints `6726` at `8f174c4ce` (and the same line at `e8718ec3b`) and nothing at `a0c4431df`. Measured at both ends, the arm run from a `git archive` export of each ref: at the base it prints `SEAM coordinator.py:_known_prices_for(perturbed):22 _known_prices_for UNBOUNDED` with `RESULT seams=1` and `RESULT unbounded=1` -- the 0 -> 1 perturbation the arm exists to show -- and at `a0c4431df` it prints `AssertionError: perturbation anchor missing`, so it does not perturb at the head at all. Its sibling still applies: `--null` prints `RESULT seams=1` and `RESULT unbounded=0` at the head. The arm is NOT re-anchored here: `dev/audit/rounds/round10/D14/` sits outside this group's architect note, whose owning seam is the price and weather ingest methods, so re-pointing the cut at `_covering_index` is the orchestrator's file-scope decision rather than a fixer's. The claim the arm carried is not lost at the head -- `tests/entities.py`'s N-no-expiry arm pins the helper's own end bound at an exact count, and its planted-lookup perturbation is what drives it.

  A rule over the class, because one dead anchor may be an instance of more: every multi-line string literal a `dev/audit/rounds/round10/**/*.py` hands to `replace`, `find`, `index` or `split` -- 22 of them in the round's harnesses -- membership-tested against the head's `custom_components/**/*.py` and against the merge base's, leaves exactly ONE dead at the head and alive at the base, which is this one. The two other literals that are dead at the head are dead at the base too, so neither is this diff's doing: a self-contained fixture (`if xs:` in `dev/audit/rounds/round10/D14/sweep-I1/enumerate_i1.py`) and a markdown split (the two-character newline-heading opener in `dev/audit/rounds/round10/intake/intake.py`), neither of them production text. So this is the class, and it has one member.
- `python3 dev/audit/rounds/round10/D14/sweep-N-silent-zero/enumerate.py` (6f71fb362e25): `unguarded` 2 -> 1.
  - The `_fetch_weather_forecast` seam is GUARDED.
  - `_fetch_tibber_prices :: self._prices = payload` stays syntactically unguarded. Its guard is upstream: `pull_prices` returns `ok` with rows only, except for the pinned no-subscription `[]` named above. `tibber_ingress.py` reads `empty_ok_wipes=0`.
- `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P1/p1_ts_seams.py` (6ccd4146a877): `seams_flagged` 6 -> 3.
  - Gone: `prices_from_tibber_payload` ADMIT, and `_known_prices_for` and `_current_spot_price` POSITIONAL.
  - Remaining:
    - `_weather_series` and `forecast_outdoor_now` POSITIONAL are guarded per the sweep (the fetch asks for `"type": "hourly"`).
    - `away._holiday_span` ADMIT is not applicable per the sweep.
- `python3 dev/audit/rounds/round10/D14/log_flood/enumerate.py custom_components/heatpump_optimizer` (91876ad0b513): base `sites=85 latched=6 seams=79`, head `sites=80 latched=6 seams=74`. Every head seam is on the `tests/entities.py` N-log-flood list, with its exact count and reason.
- Consumers of the two getters, by the rule `grep -rnE "_get_current_price\(\)|_current_spot_price\(\)" custom_components/` plus `grep -rnE 'get\("(price|spot_price|current_price)"\)|\["(price|spot_price|current_price)"\]' custom_components/heatpump_optimizer/*.py`. Every returned seam, with its disposition:
  - `_current_action["price"]` (cycle), `coordinator.py` `"price": current_action.get("price")`, `sensor.py` `action.get("price")`: attributes, where None is published as is.
  - `_grid_view` `current_price`, `sensor.py` `CurrentPriceSensor`, `climate.py` attribute: the sensor already maps None to unknown.
  - `sensor.py` `data.get("current_price")` (the advisor's rate): already falls back on a non-number.
  - `_pending_prediction` `price` and `spot_price`, read by `_record_accuracy` and `_accumulate_energy`: changed, and tested at the unknown input.
  - `_fold_score_sample` (`spot_price is not None`): changed, and tested.
  - `record_setpoint_override`: changed, and tested.
  - `_run_system_identification` -> sysid `conditions_met`: changed, and tested.
  - `price_model.py` `item.get("price")`: a row parser, not a consumer.
- Each barrier's read set, probed with a key it does not name (fixer.md step 11). Both probes ran at this head:
  - N-log-flood reads `_LOGGER.warning`/`_LOGGER.error`. The probe asks whether any other logger exists: `grep -rnoE "^[A-Za-z_]+ = logging.getLogger\([^)]*\)" custom_components/heatpump_optimizer/*.py` returns 39 lines, all `_LOGGER = logging.getLogger(__name__)`, and `grep -rnE "\.(warning|error)\(" … | grep -vE "_LOGGER\.(warning|error)\("` returns 0. Null control for the probe: the same grep with `-vE` dropped returns 85 at the base and 80 at the head, so an empty second grep is not an empty input.
  - N-no-expiry reads `bisect_right(...) - 1`. The nearest equivalent the rule does not name is `np.searchsorted`: `grep -rn searchsorted custom_components/heatpump_optimizer/*.py` returns 2, both `optimizer.py:1130`/`:1131`, which index the next run/sunny boundary for the window counters and append a sentinel past the last (the opposite of holding a value current). No `bisect_left`, and every `bisect.bisect_right(...) - 1` in the package is one of the six the enumerator returns.
- `tests/mutation_ledger` completeness is measured as a counterfactual, because a deleted pin leaves no trace in the head's own ledger. `tests/mutation_table.py` is in the tree; the figure rests on two of its calls, driven from `sys.path.insert(0, "tests")`: `completeness_problems(load_budgets_at("<merge base>"), inventory())` reports exactly 7 problems, naming the seven pins this diff removes, and `completeness_problems(load_budgets(), inventory())` reports 0. `inventory()` is the deterministic whole-tree site list, so this is not a sample.

Gate and instruments:
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir …`: `MODE: SCOPED -- 28 script(s) run, 5 scoped out.` (`fixwave/R10-FEEDS/ev/scope-b0542727/scope.txt`). This one is a function of origin/main's tip, so it is stamped: measured at merge base `e8718ec3b52e`, main's tip then, on 2026-10-16 14:50 UTC. Main has since moved and its own `tests/closures.json` grew two lines, so after the orchestrator merges main into this head the figure must be re-derived against the new merge base — the rule is the mode line, not the count (`CLAUDE.md` rule 1). Run locally at this head, all green: `tests/features.py`, `tests/entities.py`, `tests/solar_alignment.py`, `tests/structure.py`, `tests/guard_pins.py`, `tests/manual_plan.py`, `tests/debug_collect.py`, `tests/deployment_shape.py`, `tests/wood_advisor.py`, `tests/block_duty.py`, `tests/plan_view.py`, `tests/config_flow_steps.py`, `tests/validate.py`, `tests/edge.py`, `tests/finite_boundary.py`, `tests/harness_headers.py`, `tests/doc_claims.py` and `tests/typing_ruler.py`, plus `tests/env_drift.py --claims-only <merge base>` — the gate's own form, `claims hygiene: e8718ec3b52e… ok`; the bare form takes `--capture` and clones a baseline instead, which is not what `run.sh` runs (`fixwave/R10-FEEDS/ev/scope-b0542727/`). The rest of the scope runs in CI: optimality, stress, backtest, golden, arch_score*, card*, boost_drift_replay and typing's mypy job — the container lane is CI-only (2026-10-04).
- `python3 tests/typing_ruler.py` with the pinned venv: `ALL 12 typing-ruler source checks PASSED`. An intermediate head grew `misc` by one at `_fetch_solar_forecast`'s None-narrowing, which was repaired before this head.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `max_class_loc` is re-recorded 8688 -> 8635 because the class got smaller. `coordinator_attrs` stays at 151 and `seam_cut_total` at 752.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `IMPROVES`, `coord_footprint 2575 -> 2547`.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.

## Architecture score

No gate rise. `coord_footprint` falls. Computation left the coordinator class:
- the tariff option parsers became pure module functions;
- `_current_spot_price` reuses `_known_prices_for` instead of a second lookup;
- two positional fallbacks are deleted.

No budget is raised. `seam_cut_total` was at zero headroom, and the first placement of the latch cost +5, so it was paid inside the change:
- the tariff sites stopped calling the coordinator-handed helper;
- the duplicated "Not enough price data" WARNING became DEBUG.

## Red checks

Two at this head, both answered here (fixer.md's last section,
`defect-root-cause.md`'s second trigger). Neither needs a code change.

**`mutation` -- failure.** The refusal, from the job at `8921b4825`:

    MUTATION TABLE REFUSED -- 4405 unpinned site(s) against 4398 at the
    ratchet base 0570b86e, 34 of them added by this diff.

Answered rather than disputed. The ratchet is the exact count of candidate
sites carrying no disposition, derived at both ends and committed nowhere
(`tests/mutation_budgets.json`'s own comment), so a diff that adds predicates
is *expected* to add unpinned sites until a driver has killed each one. The 34
are this seam's own new predicates, by the operator the inventory generates:
13 `GUARD_OFF` (the five latches, the `is None` guards, the subscription /
total / start refusals), 10 `RETURN_DEL` (the covering helper's two returns,
the two `None` returns the getters gained, the four parser returns), 7
`CMP_BOUND` (the covering rule's bounds, one line holding two), 3 `BOOLOP` and
1 `CLAMP_DROP`. Every one is named with its disposition under `## Unpinned
sites`, which is why that section carries 33 keys for 34 sites
(`coordinator.py:547 CMP_BOUND*2`). That section is the answer to "which
sites"; this is the answer to "what makes the red expected".

The cheaper detector, and its standing cost. `python3 tools/pr/ci_predict.py
--base origin/main` names the same 33 keys / 34 sites in **17.2 s wall, 10.3 s
user** at this head (`time`, measured), and `prepr.sh` runs it -- at this head
it printed `WARN unpinned sites 33 site(s) the diff adds with no pin`. Both are
a WARNING, not a refusal: nothing before CI refuses an added unpinned site, so
there is no cheaper *refusing* detector and the finding is that none exists.
What a seat pays for not reading the warning is one CI round, measured at this
head: `mutation` 26 s, `mutation-pin-plan` 14 s, then `mutation-pins (1-7)` in
parallel from 15:01:12Z and `mutation-autofix` behind them under a 10-minute
timeout. The repair is `python3 tests/mutation_table.py --pin-killed --base
origin/main`, which drives every candidate site the diff added and records each
kill under `killed_by`, shardable with `--shard K/N` (CI runs 7).

Disposition: `mutation-autofix` pins the killed mutants as `ci: pin killed
mutants` (`ci-autofix.md`), so nothing is hand-edited in this branch. State
read at 2026-10-16 15:13 UTC: `mutation-pin-plan` **success**, `mutation-pins
(1-7)` **in progress** since 15:01:12Z, `mutation-ledger` and
`mutation-ledger-push` **skipped**, `mutation-autofix` **not started** -- **the
bot commit is awaited, not landed**, and the branch tip is still `8921b4825`.
Per `ci-autofix.md` the summary line decides: a red `mutation-autofix` means no
commit comes and the pinning is mine to run; green means `changed`.

Outcome, 2026-10-16 16:5x UTC. The bot landed: `mutation-autofix` went green and
pushed `fba6de8de2712ed6bb771f15a5574d3eb92c5f51` (`ci: pin killed mutants`),
pinning 30 of the 34. The 4 it left — `_peak_tariff_hours` `GUARD_OFF fb12652e`,
`forecast_outdoor_now` `CMP_BOUND a439030d`, `_fold_score_sample` `BOOLOP
05bb5b4f` and `record_setpoint_override` `CMP_BOUND 1b2d9dbb` — are survivors no
driver separates, so by `ci-autofix.md` they owe a `survivor_triage` record and
not a pin; `a0c4431df` is that edit. Three are argued *equivalent* (the tariff
guard's two arms both return `()`, because `parse_windows("")` is `[]`; the
`now <`/`now <=` pair differ only at the instant `now == starts[0]`, where
`_covering_index` returns 0, the other branch's value; and the `and`/`or` pair
agree over the domain `pending["spot_price"]` can hold, a finite float or
`None`); one is recorded as a *gap* (`mean_price == 1e-6` exactly is reachable
and untested). Re-run at `a0c4431df`:
`python3 tests/mutation_table.py --pin-killed --base origin/main` prints
`PIN KILLED -- 0 new unpinned site(s)` -- 4368 unpinned of 6133 candidate
sites, 4398 at the ratchet base -- so the refusal's own arm is clear and
`mutation` is expected green at this head.

**`pr-contract` -- failure, 2026-10-16 17:17 UTC, answered.** "`## Head` does
not name a0c4431, which is the head this ran on." Correct and expected: the
ledger commit above moved the head after the previous body named `8921b4825`.
This edit names it (`## Head` above), which is the whole repair.

**`pr-contract` -- failure.** "check `mutation` is red and `## Red checks` does
not name it." Named and answered above; this edit is the answer, and it is the
only change -- the code head is untouched at `8921b4825`.

## Unpinned sites

`prepr.sh` step 6d lists 33 sites this diff adds, each named below by the exact `file:line KIND` key the step prints. Each one's disposition is below: the named arm of `tests/features.py` (or an existing check) drives it, and `mutation-autofix` pins whatever the gate's mutation pass kills. "Verified" marks a site whose predicate this body's mutation proof inverted and saw killed. Any survivor the gate reports is answered on the PR, not triaged here.

- `custom_components/heatpump_optimizer/coordinator.py:547 CMP_BOUND*2` (`if i < 0 or i + 1 < len(starts):`): the covering arm (before, first, inner, last). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:547 GUARD_OFF`: the covering arm. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:548 CMP_BOUND` (`return None if i < 0 else i`): the covering arm. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:549 CMP_BOUND` (the last entry's span): the covering arm's lone and quarter cases. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:550 CMP_BOUND` (`now < starts[i] + span`): the covering arm's exact `end` case. Verified (M1). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:550 RETURN_DEL`: the covering arm. Verified (M1). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:569 GUARD_OFF` (`if not active:`): the latch-transitions arm. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:570 GUARD_OFF` (`held.pop`): the latch arm's one INFO on clear. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:572 RETURN_DEL` (`return False`): the four-cycle flood arm, through `_price_series`. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:574 GUARD_OFF` (`held.get(key) == text`): the latch and flood arms. Verified (M4). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:579 RETURN_DEL` (`return True`): the flood arm (`_price_series` must return None). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:593 GUARD_OFF` (`if chunk.strip():`): the existing `_tariff_months` checks in `tests/features.py`. mutation-autofix, or a survivor answered on the PR.
- `custom_components/heatpump_optimizer/coordinator.py:605 GUARD_OFF` (`if not spec.strip():`): the existing `_tariff_hours`/`_tariff_months` empty-option checks. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:723 CMP_BOUND` (before the first forecast entry): the siblings arm's `fc_before`. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:724 GUARD_OFF` (`if index is None:`): the siblings arm's `fc_past`. Verified (M11). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:1866 RETURN_DEL` (`_open_loop_plan_value`): the siblings arm's `plan_*`. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:6793 GUARD_OFF` (`_known_prices_for` `if idx is None:`): the stale-price-list arm. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:7070 RETURN_DEL` (`_get_current_price`): the stale-price-list arm. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:7080 RETURN_DEL` (`_current_spot_price`): the stale-price-list and no-price arms. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:8325 RETURN_DEL` (`_tariff_months`): the existing `_tariff_months` checks. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:8329 RETURN_DEL` (`_tariff_hours`): `tests/config_flow_steps.py`'s `_tariff_hours()` mask check. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:9803 BOOLOP` (`actual_cost ... and price is not None`): the accuracy arm (`actual_cost is None`). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:10112 GUARD_OFF` (`if known_price is not None:`): the unpriced-interval arm. Verified (M6). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:10350 BOOLOP` (`spot_known and np.isfinite(sek)`): the score-day arm. mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:10350 GUARD_OFF`: the score-day arm. Verified (M12). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:10351 CLAMP_DROP` (`max(0.0, kwh)`): a pre-existing site re-indented under the new guard. Its old pin (killed by `tests/features.py`) is among the seven removed, so mutation-autofix re-pins it.
- `custom_components/heatpump_optimizer/coordinator.py:10842 BOOLOP` (`spot is not None and mean_price > 1e-6`): the neutral-relative-price arm. Verified (M7). mutation-autofix.
- `custom_components/heatpump_optimizer/coordinator.py:10842 CMP_BOUND` (`mean_price > 1e-6`): the existing near-zero-mean override check. mutation-autofix.
- `custom_components/heatpump_optimizer/price_model.py:652 GUARD_OFF` (`if not subscription:`): the existing "each Tibber failure names itself" check (no subscription reads `[]`). mutation-autofix.
- `custom_components/heatpump_optimizer/price_model.py:668 GUARD_OFF` (`if total is None or start is None:`): the Tibber body arm. Verified (M3). mutation-autofix.
- `custom_components/heatpump_optimizer/price_model.py:676 RETURN_DEL` (`return prices or "..."`): the Tibber body and HTTP-200-empty arms. Verified (M2). mutation-autofix.
- `custom_components/heatpump_optimizer/price_model.py:689 RETURN_DEL` (`_raw_start`'s `return text`): the existing `_raw_start` spellings check. mutation-autofix.
- `custom_components/heatpump_optimizer/sysid.py:1392 GUARD_OFF` (`if price is None:`): the sysid refusal arm. Verified (M8). mutation-autofix.

## Distinct finding (for the orchestrator to file; not fixed here)

The N-log-flood barrier lists 8 functions under "OWED". Each is unlatched, reached every cycle or every solve, and triggered by a condition that can persist, and each is outside this group's seam. Static evidence is the arm's own rule, i.e. `log_flood/enumerate.py` at this head. The runtime probe owed for each is a `log_flood/probe.py` arm that holds the condition for 4 cycles:
- `coordinator._apply_action`: the stale-plan hold; probe arm: a plan older than the stale bound.
- `coordinator._command_valve_target` (3 sites): wrong zone kind or wrong entity domain; probe arm: a mis-typed valve entity.
- `coordinator._note_solve_failure`: an ERROR on every failed solve; probe arm: a solver that always fails.
- `pump_arbiter._space_target`: an indoor set-point whose minimum is above the room target.
- `inputs._age_gate`: a future last-reported stamp, per read.
- `optimizer.optimize`, `optimizer._solve_space`, `optimizer._optimize_space_only`: the solver's per-failed-solve reports. The R10 sweep did not name these. They are the same persisting-failure shape as `_note_solve_failure`.

The 5 sites the sweep named are its "static evidence only" list. The 3 optimizer sites are my addition.

## Forward-carry

Owed to the roster, which the orchestrator writes:
- The new group for the distinct finding above: when a site is latched (through `coordinator._log_held`), delete its OWED entry in `tests/entities.py`'s `_R10_LOG_ALLOWED_BY_REASON`. Each count there is exact, so a fixed site turns the arm red until its entry goes.
- The later coordinator groups (R10-RATIO-SITES, R10-VENT-DETECTOR): any new `_LOGGER.warning/.error` or `bisect_right(...) - 1` in the package must go through `_log_held` / `_covering_index`, or be added to the matching list in `tests/entities.py` with its reason.
- `_get_current_price()` / `_current_spot_price()` now return `float | None`.

The D1 brief edit (step 3 reads the published and booked value) stays with R10-BRIEFS-FOLD, as the roster carry says.

## Friction

none



