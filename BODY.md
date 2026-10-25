The residue of #2257 that R10-ADVISOR (#2572) recorded and left. Part of #2257.

Each carried seam was sized under its own perturbation before any change, beside the null of `r10_sav_null_terms.py` (a flat price and a constant outdoor temperature). The instrument is a new harness, `dev/audit/harnesses/r10_advisor_residue.py`, because `r10_sav_null_terms.py` drives none of these readers: it replays the savings loop and prices a thermostat, and it never calls `async_simulate`, the fuse advisor, the sensor-gap rank or the setpoint sweep. Its null is reused as each arm's control. What each seam read, and what this branch does with it:

- **(a) The what-if's `monthly_cost_delta`.** It moves with the house's start: on 24 of 24 (instant, ask, series) rows, with the house coasted, at target or pre-heated (`whatif` arm). Both of its advisor readers hold the comfort schedule fixed (a cap). So each plan's spend plus its `deferred_energy_cost` answers to one thermostat, and that settled figure is comparable.
  - Across the 12 cap rows, the settled figure's start spread averages 10.1 against the plan's 50.4.
  - It reads a cap as a saving on 1 of 36 figures, against the plan's 18 of 36. A cap can cost; it cannot save.
  - **Fixed for the cap's readers:** the fuse advisor's `cost_delta_sek_month` and the cap tile now read `async_simulate`'s new `monthly_settled_cost_delta`.
  - **Not fixed for a comfort move:** the Plan page's what-if panel. There the settled figure gives the wrong sign (a degree cooler settles to +24.6 at the varying 00:00 rows, a degree warmer to -25.5), which is #2572's finding again. The held figure prices only the comfort part of a draft that can also move hot-water windows, quiet hours and wood. See Forward-carry.
- **(b) The inbox's sensor-gap and hot-water rows.** Both move with the instant they are read (`inbox` arm):
  - the gap row was priced at the spot price now, so over one week its figure spans a max/min of 18.50 and 453.6 within one day;
  - the hot-water row was priced at the feed's day window, so it spans a max/min of 3.08 across days.
  - **Fixed:** both now price at the ledger's recent kWh price (`MonthlyLedger.recent_kwh_price`). That is the time-mean spot price over this month and the last, plus the grid fee their kWh paid. The ledger already samples it every settled interval and persists it, so no new state is added. They now span 1.03 and 1.04. A fresh install, which has no settled interval yet, keeps today's pricing.
- **(c) The held estimator's per-solve asymmetry.** It moves with the start hour in the null too (`asym` arm): the gap reaches 21.0 % of the per-degree figure at the 06:00 start, from the 15-minute quantisation of a coast, and is 3.0 % at worst on varying prices. Nothing reads the two tiles together (the class grep in Figures), and the published mean averages over rotation starts. **Recorded, not fixed.**
- **MX4 (a pooled mean in `price_tiles.published`).** **Pinned** by a check of unequal daily counts: a day solved once at 0 and a day solved three times at 12 publish 6. A pooled mean would read 9.
- **The per-degree copy, decided.** The owner's screenshot copy, "A degree cooler is cheaper", is read against the button that moves the setting. The tile prices a degree of room temperature held; moving the setting moves the room by less (-0.514 K and +0.327 K per degree in `r10_advisor_degree.py null`). So the copy now says what is priced:
  - English: "Keeping the house a degree cooler is cheaper" and "Keeping it a degree warmer costs … more";
  - Swedish: "Att hålla huset en grad svalare är billigare" and "Att hålla det en grad varmare kostar … mer";
  - `docs/dashboard-card.md` states the distinction.

  Rescaling the figure by the delivered fraction lost. That fraction is the plan's comfort trade, measured only in a closed loop, which the what-if seam cannot run; the held degree is the figure that does not depend on it.
- **The 30-day mean mixes days priced at different schedules.** It moves (`mixing` arm): with the whole schedule moved -2..+2 K, the held degree spreads 28.5 % at the 07:00 start on varying prices, 16.7 % in the null at 07:00 and 0.0–9.3 % at the other instants. Most of it comes from schedules pushed against the 17–23 °C band. **Recorded, not fixed:** restarting a tile's days at each schedule change would bring back item 6's day-to-day swing after every setback or target change, which is the noise the owner asked the horizon to remove.

**Architecture.** The coordinator orchestrates and no longer computes these figures:
- `async_simulate`'s three monthly figures are `price_tiles.monthly_deltas`, beside `per_month`, which already owned the scaling and the choice of figure per tile;
- the sweep's price level (recent, else the feed's window, floored positive) is one module helper, `_sweep_price`;
- `_build_data_dict` hands the sweep the grid view's published price, so the dhw seam never reads the ledger.

Alternatives considered:
- **Reading the ledger inside the sweep.** This added two seam crossings and a 16th branch to `_dhw_setpoint_sweep`.
- **A new 30-day price book.** This needs new persisted state and a store migration, where the ledger's monthly mean already exists.

## Head

`367afeb856434fc863dd3617caac19e50f78bcfa`, cut from origin/main `da12aa37dee15b9e9567bd6c848493436f2592dd` (the merge base and the brief's head). Every figure below was taken at it, except where a line names `d8bcb95a8`: the mutants ran there, and the only change between it and the head is the harness file (`git diff d8bcb95a8 367afeb85 --stat`: `dev/audit/harnesses/r10_advisor_residue.py` alone, which no mutant or suite reads). At handoff (2026-10-25T18:46Z, `date -u`) origin/main is `dfcd8d9be`, and `git merge-tree --write-tree origin/main 367afeb85` rc 0.

## Mutation proof

Each mutant replaces one production line with an exact single-occurrence replacement, in a detached worktree of its own at `d8bcb95a8`, and runs the closure named. A check named is one that went red.

| mutant | production line replaced | closure | red |
|---|---|---|---|
| MX4 | `published`: `mean = sum(d["sum"] / d["count"] for d in days) / len(days)` -> `sum(d["sum"] for d in days) / sum(d["count"] for d in days)` (the review's pooled mean) | `python3 tests/features.py` | `#2257: a day solved once and a day solved three times weigh alike in the published mean` (detail: `monthly_cost_delta` 9.0, want 6.0) |
| MA1 | the fuse advisor's `cost_delta_sek_month` reads `monthly_cost_delta` | `python3 tests/features.py` | `the advisor publishes a verdict for the next-smaller fuse` (got -35.0) |
| MA2 | `monthly_figure`'s cap key -> `monthly_cost_delta` | `python3 tests/features.py` | `#2257: a degree tile reads the held figure, the cap tile the plan's settled one`; `#2257: the cap tile reads the settled figure, which the house's start moves less than the plan's` |
| MA3 | `monthly_deltas`' settled figure drops `sim.deferred_energy_cost - live.deferred_energy_cost` | `python3 tests/features.py` | `#2257: the cap tile reads the settled figure, which the house's start moves less than the plan's` (detail: settled = plan, -1.69 / -23.72 at 03:07 and -13.81 / -40.78 at 15:07 for the 19 °C / 23 °C house) |
| MB1 | `_gap_energy_rate` reads `current_price` first (the merge base's line) | `python3 tests/features.py` | `#2257: the sensor-gap row prices at the recent kWh price, the price now only without one` |
| MB2 | `_build_data_dict`'s `self._dhw_setpoint_sweep(data.get("recent_kwh_price"))` -> `self._dhw_setpoint_sweep()` | `python3 tests/features.py` | `#2257: the published setpoint sweep prices at the recent kWh price, whatever the day's window` |
| MB5 | `_sweep_price` drops `kwh_price or` | `python3 tests/features.py` | `#2257: the published setpoint sweep prices at the recent kWh price, whatever the day's window` |
| MB3 | `recent_kwh_price` keys this month alone | `python3 tests/features.py` | `#2257: the recent kWh price is this month's and last month's spot mean plus their fee per kWh` (spot only 4.0, want 2.0) |
| MB4 | `recent_kwh_price` returns `total / count` (no fee) | `python3 tests/features.py` | the same check (with fees 2.0, want 2.3) |
| MC1 | `advisor.degree_title` back to `"A degree cooler is cheaper"` | `node tests/card.mjs` (after `tests/plan_view.py`) | `price of a degree: the cooler tile is the saving, the warmer one is in the detail` |

Each mutant above failed exactly the checks named, and nothing else: `1 of 4407 FEATURE CHECKS FAILED` (`2 of 4407` for MA2), `1 CARD CHECK(S) FAILED` for MC1. The failing-test-first step for MX4 is that mutant. #2572's review recorded it surviving the suite at that PR's head (review 6328189370, carried in this group's roster entry); with this branch's check it fails.


## Null control

- **The unmutated tree passes:** `ALL 4407 FEATURE CHECKS PASSED` and `ALL CARD CHECKS PASSED` at `367afeb85` (Figures).
- **Every arm of the harness carries its own null,** and each reads as it must:
  - `whatif`: the held figure, which starts held at its own target, moves on 0 of 24 rows.
  - `inbox`: at the flat price and constant outdoor temperature both rows read flat (max/min 1.00) at the base and at the head.
  - `asym` and `mixing`: the null series is what separates the estimator's own term from the prices'.
- **The fresh-install control:** with no settled interval, the sweep prices at the feed's window (a check), and the gap row at the price now (a check).

## Figures

**Harness `dev/audit/harnesses/r10_advisor_residue.py`**, sha1 `ffb5f71b132ed9547aeb05f7dd7429d366bf412c`, this PR's instrument. Command: `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py <arm>`.

Every arm at `367afeb85`, rc 0 (no arm named runs all four). The rule each line states is the arm's own, in the harness header.
- `whatif`:
  - `RESULT whatif rows 24 plan_moves_by_start 24 held_moves_by_start 0` (a row moves when its three starts spread more than 1.0; the held figure counts any spread above 1e-9)
  - `RESULT whatif caps rows 12 spread_by_start mean plan 50.4 settled 10.1; figures reading a saving (< -1) plan 18/36 settled 1/36`
  - for a comfort move: `RESULT whatif varying 00:00 target_minus_1  plan by start  -131.6   -131.6  -133.3 … settled   +24.6   +24.7   +24.7`, and `target_plus_1 … settled   -25.5   -21.7   -25.0` (the settled figure's wrong sign across two schedules); `RESULT whatif null 00:00 target_plus_1 … plan … spread  132.0`
  - `VERDICT whatif the plan figure moves with the start; the held figure does not`
- `inbox`, the same harness file (sha1 above) run at both ends:
  - head: `RESULT inbox varying gap       mean  108.0 range  106.4.. 109.3 (max/min 1.03) widest_day    2.9`; `RESULT inbox varying hot_water mean   23.8 range   23.4..  24.3 (max/min 1.04) widest_day    0.6`
  - base, a detached worktree at `da12aa37d` with the head's harness copied in: `RESULT inbox varying gap       mean  108.8 range   27.9.. 516.4 (max/min 18.50) widest_day  453.6 day_means   65.4.. 200.3`; `RESULT inbox varying hot_water mean   23.9 range   14.4..  44.4 (max/min 3.08) widest_day    0.6 day_means   14.4..  44.1`
  - null, identical at both ends: `RESULT inbox null gap … (max/min 1.00) widest_day    0.0` and `RESULT inbox null hot_water … (max/min 1.00) widest_day    0.0`
- `asym`: `RESULT asym null gap -0.06..+11.10 of mean magnitude 52.83 (worst 21.0 %)`; `RESULT asym varying gap -0.10..+2.09 of mean magnitude 68.54 (worst 3.0 %)`
- `mixing`: `RESULT mixing worst spread 28.5 % of the per-degree figure`; per instant, `RESULT mixing null 07:00 … spread 16.7 %` and `RESULT mixing varying 07:00 … 58.93  70.16  79.95  79.96  79.85 spread 28.5 %`, the others 0.0–9.3 %

`whatif`, `asym` and `mixing` call the optimizer directly, not the readers this branch changes, so they read the same at both ends by design. Their companions are the real-seam features checks (MA2 and MA3 are red there) and the fuse-advisor check (MA1).


**The per-degree copy's delivered fraction.** `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_degree.py null` (sha1 `41ee4a43725dac312d95037575bc612f866af709`), at `367afeb85`, rc 0:

- `RESULT null offset -1 delivered -0.514 K truth_per_delivered_degree +59.4 held +54.4 (-8.4 %) first_solve_plan +145.6`
- `RESULT null offset +1 delivered +0.327 K truth_per_delivered_degree +59.4 held +54.4 (-8.4 %) first_solve_plan +85.1`

This run is from this worktree before any production line changed (production at the merge base). The arm reads only the optimizer and `price_tiles.per_month`, which this branch leaves as they were.

**Class seams (fixer step 8).**
- (a): `grep -rn "monthly_cost_delta\|monthly_settled_cost_delta\|monthly_held_cost_delta" custom_components/heatpump_optimizer --include=*.py --include=*.js` returns:
  - `price_tiles.monthly_figure` (degree reads held; cap reads settled, this diff);
  - `price_tiles.monthly_deltas` and `price_tiles.published` (the tile's publication key);
  - the fuse advisor (settled, this diff);
  - the card's `priceTiles` and `degreeRow` (the published tile), and `payload.PriceTile`'s field (its type);
  - `WhatIf.summary` (the plan's figure, the carried what-if seam).
- (b): `grep -rnE "30\.4|DAYS_PER_MONTH|\* 30\.0|24\.0 \* 30" custom_components/heatpump_optimizer --include=*.py --include=*.js` returns the monthly scalers, each with its disposition:
  - `price_tiles.MONTH_HOURS` (the tiles, averaged over 30 days, #2572);
  - the card's `DAYS_PER_MONTH` (the hot-water row, now priced at the recent kWh price);
  - `_gap_probe_terms`' `24.0 * 30.0` and `* 30.0` (the gap row, now at the recent kWh price);
  - the COP-health repair's `monthly_kwh / max(1, now.day) * 30.0` (month-to-date kWh at the feed's mean, in a repair issue raised once per trip). It does not refresh, so it cannot swing day to day: outside this class, left as is.
- (c): `grep -rn "target_minus_1\|target_plus_1" custom_components/ --include=*.py --include=*.js` returns `price_tiles.TILE_NAMES` and the card's `priceTiles`. The card's only relation between the two is `degreeRow`'s sign check; no reader compares their magnitudes.

**Suite and gate figures:**
- The scope: `python3 tests/closure.py select --diff da12aa37dee15b9e9567bd6c848493436f2592dd --workdir "$D"` -> `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=da12aa37dee15b9e9567bd6c848493436f2592dd ./tests/run.sh` at `367afeb85` -> `1 TEST SCRIPT(S) FAILED`, rc 1. The one is `tests/entities.py`, `2 of 2445 ENTITY CHECKS FAILED`: `gate-sweep.yml: on CI's completion, …` and `graders-head-copy's delivery_status step is red only when …`. Both fail identically at the merge base (`PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached `da12aa37d` worktree -> `2 of 2445 ENTITY CHECKS FAILED`, the same two names); see Friction. Every other script passed, among them:
  - `ALL 4407 FEATURE CHECKS PASSED` (4401 at the merge base: six checks added);
  - `ALL CARD CHECKS PASSED` and `card_drift: identical in all 40 states`;
  - `NO UNCLAIMED DRIFT: 56 scenario(s) checked against da12aa37dee1…` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`: the five coord fixtures, claimed `CLAIMED coord_*: 1 leaves moved` (`data.recent_kwh_price`, null);
  - `ALL 113 STRESS CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `STRUCTURE RATCHET PASSED`; `tests/typing_ruler.py` ok.
- `python3 tools/audit/archscore/score.py --diff da12aa37dee15b9e9567bd6c848493436f2592dd` -> `Architecture score: dS +0.0012 IMPROVES`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` -> `CI PREDICT: no closures, fast, wave-script or instrument red predicted against da12aa37dee1`; it lists the 10 unpinned sites below.

## Unpinned sites

Each is a `custom_components/` site, so `mutation-autofix`'s lane pins it after the PR opens (`ci-autofix.md`). The value checks this branch adds already read several of them.
- `custom_components/heatpump_optimizer/coordinator.py:2007 CLAMP_DROP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:2007 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/coordinator.py:2007 RETURN_DEL`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/ledger.py:287 BOOLOP`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/ledger.py:287 GUARD_OFF`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/ledger.py:290 GUARD_OFF`: pinned by `mutation-autofix` (the empty-ledger arm of the recent-price check reads it)
- `custom_components/heatpump_optimizer/ledger.py:294 CMP_BOUND`: pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/ledger.py:295 RETURN_DEL`: pinned by `mutation-autofix` (the recent-price check reads it)
- `custom_components/heatpump_optimizer/sensor.py:2813 CMP_BOUND`: pinned by `mutation-autofix` (the gap-rate check's zero-price arm reads it)
- `custom_components/heatpump_optimizer/sensor.py:2813 GUARD_OFF`: pinned by `mutation-autofix`

## Architecture score

`Architecture score: dS +0.0012`: IMPROVES, admissible.
- `coord_footprint` 2446 -> 2444: the what-if's monthly figures and the sweep's price level left the coordinator class.

`python3 tests/structure.py` records `class_excess_loc` 18102 -> 18101 and `max_class_loc` 8311 -> 8306 (commit `7e0156de8`, the reason in its message). `seam_cut_total` stays at 419. No budget rises.

## Red checks

- `mutation`: red at open, by prediction. The 10 `custom_components/` sites under Unpinned sites have no pin yet, and `mutation-autofix`'s bot commit pins them (`ci-autofix.md`: wait for it, do not duplicate). The cheaper detector already ran: `ci_predict.py` (prepr step 6d) listed every site before the push, at the cost of one static read per handoff.
- No other red is predicted at this head (`ci_predict.py` above). This branch has not run on CI yet.
- The local gate's one red, `tests/entities.py`'s `gate-sweep.yml` and `graders-head-copy` checks, reads the same at the merge base in this seat, so this diff did not turn it red; the environment observation is under Friction.

## Forward-carry

- **Seam (a) at the Plan page's what-if panel, for a comfort or schedule move.** `WhatIf.summary` still reads `monthly_cost_delta`, which moves with the house's start (`whatif` arm: the degree rows' plan spread is up to 132.0 in the null). `docs/dashboard-card.md` discloses this ("its figure includes the one-off coast or heat-up a change starts with"). No sound estimator exists within this seam:
  - the settled figure gives the wrong sign across two schedules (+24.6 / -25.5 at the varying 00:00 rows);
  - the held figure misses a draft's non-comfort edits.

  A fix needs an estimator design (an L-size designer stage), or the owner's acceptance of the disclosed copy. The brief expected this group to be the last on the issue; this body names it with Part of rather than a closing keyword, so that the residual keeps an owner. The orchestrator decides between a design group and dismissal. Carry: #2257
- **Seam (c), the held estimator's asymmetry.** Measured and left; no reader compares the two tiles. A later change that wants a convexity check starts from the `asym` arm. Carry: dismissed: no reader compares the two tiles, and the published 30-day mean averages it over rotation starts
- **The 30-day mean's mixing of schedules.** Measured and left: a reset at each schedule change trades the measured spread for item 6's swing. Carry: dismissed: a per-schedule reset re-introduces the day-to-day swing the owner asked the horizon to remove

## Friction

- brief-citations: unclear: the brief sizes seams (a)-(c) "with the null arm of r10_sav_null_terms.py", but that harness has no arm reading `async_simulate`, the fuse advisor, `rank_sensor_gaps` or the setpoint sweep. Its null (a flat price and a constant outdoor temperature) is reused as each arm's control in the new `dev/audit/harnesses/r10_advisor_residue.py`. Carry: dismissed: the residue harness landed here is the instrument the brief meant
- gate-scoping: cost: in this cloud seat `tests/entities.py` reads `2 of 2445 ENTITY CHECKS FAILED` (`gate-sweep.yml` U0c and `graders-head-copy`'s delivery_status case) identically at the merge base `da12aa37d`, so a local scoped gate is red for a reason no diff here reaches. Carry: R10-FLY-SUITE-ENV-FLAKES
