<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
R10-SAV-COMFORT: the savings figures on the owner's baseline specification — round-4 re-cut.

Part of #2492. Part of #201. #2492 stays open. The group's roster row lists #2492 under `issues`, not `fixes`.

## Re-cut

Round 3 returned `blocked`; this body replaces that one rather than repairing it, on the rule in `dev/governance/roles/fixer.md` that a fourth round is a re-cut.

**This is a re-cut, not a repair.** Round 3 blocked on three things: the branch had rewritten the finder's own harness `dev/audit/harnesses/r10_sav_baseline.py`, its mutation harness died on ten of sixteen anchors, and its upgrade-month control died when `57eeda5a1` extracted `coverage_factor` without porting it. All three are answered here by restoring the instrument, not by re-specifying it: `r10_sav_baseline.py` is the base's own bytes (shasum `bc31f356191ededbfb0b15f768b258249867b134`), the mutant list is re-anchored on the tree it now runs against, and the control reads the module-level `coverage_factor` with the month's own meta.

**What the re-cut costs, stated up front.** Restoring the finder's transient arm required removing the comfort-matched reference (`_comfort_matched_targets`, `OptimizationResult.held_cost`). With it in, this branch failed the #2255 property the arm measures: the booked thermostat's step 0 moved 0.07 kW across four start states against a 0.05 bar, because a reference derived from the comfort the plan delivered is derived from where the plan started. With it out, the arm is SOUND (0.00 kW) and the null arm returns to the base's figure. Both arms cannot be green at once, and the measurement below says why. This is the finding-level statement the round-4 brief asked for: **the owner's flat-price null (|pct| < 3.0) cannot be met on the modelled basis by any honest change in `custom_components/`**, and the numbers follow in "The owner's null".

**One basis, calibrated to the meter (ledger.py).** Each settlement books `savings_plan`, the plan's own modelled kWh on the same intervals as `savings_baseline` and `savings_actual`. `MonthlyLedger.meter_calibration(month)` is metered kWh over modelled kWh, and the month row multiplies the modelled thermostat's cost by it, floored at `MIN_CALIBRATION_KWH`. A month whose savings lines began before the plan line existed stays on the modelled basis, as does one whose plan booked under that floor; both publish `meter_calibration: null`. `coverage_factor(meta, now)` is now module-level, reading the month's own meta; the row keeps the hours' scale over the calendar one. `month_cost` lost its last reader and is deleted. The row gains `meter_calibration` (`SavingsMonth`, payload.py).

**One basis, card equal to the ledger.** In `ledger.savings_months`, Baseline, Actual and Savings are all the covered intervals at spot plus fee, and Savings is computed from the two rounded cells. `tests/plan_view.py` builds the savings payload through the production `MonthlySavingsSensor` over a ledger settled by `observe_spot_and_settle_savings`, and `tests/card.mjs` renders the Savings tab from that payload and asserts every cell against the ledger's own row, plus that baseline less actual is the saving shown.

**The duty ledger re-freezes `planned` at each plan adoption (pump_arbiter.py `_observe`).** A cycle's re-solve can move a slot onto the current step, so the step is scored against the plan that actuated it rather than the one in force at its first tick.

**The savings reference is the thermostat at the comfort schedule (#2255).** The booked baseline runs all along and may not depend on where the optimiser left the house, so it holds the comfort schedule at `_thermostat_held_state`'s own start. The plan's start gap is settled against it instead of against a reference derived from the plan's delivered comfort.

**`_settle_horizon` and `_start_gap_cost`.** `_settle_horizon` gives both solve paths one settlement: the end's stored heat, less the start's. `_start_gap_cost` bounds a warm start's debit by what its heat could displace, the space heat the thermostat buys plus the end's own credit, so a summer house's passive warmth is debited nothing and a negative thermostat cost never turns the debit into a credit. The DHW path settles its tank at the end while the start is bounded by the house's end alone.

**The thermostat's per-step inputs, read once.** `_compute_baseline_power` reads its setpoints, the humidity series, the two-tank flag and the floored slab coefficient once per pass rather than once per step; the setpoints come from `_baseline_targets` and `_baseline_target` delegates to it, so the rule has one owner. `np.clip`'s lower bound is dropped: the demand is floored at 0 two lines above and `compute_cop` returns at least 1.0. `env_drift.py --all` reads the tree byte-identical to the merge base on all 56 scenarios, so nothing moved.

**The owner's null, measured.** The finder's null arm runs a two-day flat-price loop, re-planning hourly, and compares the month row's booked saving with its own baseline:

- at the merge base `3b4180dcc`: baseline 154.1, actual 137.41, saved 16.69 SEK = **10.83238932735682 %** — DEFECT against the 3.0 bar;
- at the round-3 head `3b55da2c`, with the comfort-matched reference: **6.179161545814557 %** — still DEFECT, and the transient arm broke (0.07 kW);
- at the re-cut head `4bf7c2eaa`, reference restored to the schedule: **10.83062946138871 %** — DEFECT, and within 0.002 percentage points of the base.

The terms are measured at the re-cut head `4bf7c2eaa`, not inferred (`dev/audit/harnesses/r10_sav_null_terms.py`, both arms): the booked thermostat uses 128.4 kWh against the plan's 114.5, and the plan's mean room is 18.79 °C against a mean comfort target of 20.44 °C. Its power-weighted COP is 8.383 against the thermostat's 7.149, an outdoor-timing gain of **+17.27 %**; it ends the window having drawn 23.7 kWh_th more from stored heat than the thermostat did. So the residual is two things: the plan reaching a mean room 1.65 K below the schedule, and a real COP-timing gain. Neutralising the first is exactly the comfort-matched reference, which breaks #2255's start-independence by measurement (0.07 kW). Removing the second would delete more than half of a real saving, and the owner's own words ("the volume difference may remain") permit it. A warm-up skip of the matching was measured at 0/4/8/16/32 h: the booked step's spread reads 0.07/0.07/0.06/0.05/0.04 kW, so the property only returns once the reference is essentially back at the start-dependent plan. Neither arm is claimed as green, and no threshold was moved to make one so.

**The roster carries, item by item.**
- Carry 1 (R10-SAV-BASELINE's three terms). Comfort and stored heat are separated by the reference and the settlement; the timing term survives. `r10_sav_volume.py` reads flat 0.00 and vary +74.88 (Null control).
- Carry 2 (volume against timing). The modelled thermostat is scaled by `meter_calibration`: the flat-price arm reads 0.00 and the varying profile keeps its timing term +74.88; a meter that reads the model keeps 48.0 at calibration 1.0. Mutant M17.
- Carry 3 (card equal to the ledger). `ledger.savings_months` puts every cell on one basis, and `tests/card.mjs` renders the Savings page from the sensor payload and asserts each cell against it.
- Carry 4 (the owner's specification). The baseline is the thermostat over the same price profile at the meter's power levels, and timing is 0 under one flat price (Carry 2's arms). The owner's `|pct| < 3.0` null on the finder's own instrument is **not met** — see "The owner's null"; the residual, its terms and the mutual exclusion with #2255 are the finding-level report.
- Carry 5 (the duty ledger). Seam 1 is done here (the re-freeze above). Seam 2 is routed under Forward-carry.

## Head

`3522cd92564309ba64ba08c9bcf5101ccd8f1b8b` merges the authored code head `6d526cfdc50ff472d3530f3c52dacee60bead7ee` into this PR's previous head, which carried its own row `dev/programme/delivery/2745.md`. The PR tree is that code head plus the row.

`6d526cfdc50ff472d3530f3c52dacee60bead7ee` is the measured head. It is the merged code head `805550f5323c4448fcba9bff97371b9501d89460` plus one commit: `805550f53` is the census fix `4522d46b019d3ac042b736bcafbf2c01669d5b3d` on top of `02a28aed` with a merge of main `524c1896b` (no hand resolution; `tests/closures.json` was the only conflict, resolved by the ledger merge driver), and `6d526cfdc` makes `coverage_factor` total for a partial month meta. The red: the D7-s2-58 finite-float census landed on main while this branch was open, and the merge-forward brought it in beside the module-level `coverage_factor` this branch extracted. The census's shape rule (a module-level function returning `float`, coercing with a builtin `float()` under an `isinstance` test) read `settled = float(entry["sum"]) if isinstance(entry, dict) else 0.0` as a tenth coercion beside the one owner, so `tests/finite_boundary.py` printed `stray=['ledger.py::coverage_factor']`. The read now goes through `const.finite_float`: `settled = finite_float(entry.get("sum"), 0.0) if isinstance(entry, dict) else 0.0`, and the same guard on the two fold counts, `int(finite_float(entry.get("count"), 0.0))` and `int(finite_float(spot.get("count"), 0.0))`. The owner's documented policy keeps a bool out of the number set, so a stored `True` sum now reads `0.0` and falls back to `pro_rata_factor(now)` where `float()` read it as `1.0` and claimed a settled hour.

**The two `int()` sites, which the census cannot see.** The census's seam rule matches a builtin `float()` call, so `int(entry["count"])` stayed green while it could still raise -- `KeyError` on a meta dict without the key, `TypeError` on `None`, `ValueError` on text -- inside the fold that computes every estimated figure. They now go through the same owner. A probe at `6d526cfdc` (`PYTHONPATH=custom_components:tests/hastub python3 probe_coverage.py`, `now = 2026-10-27`) reads:

```
nan-text      factor=  1.1481 is_pro_rata=True  loader_admits=False
inf-text      factor=  1.1481 is_pro_rata=True  loader_admits=False
bool-sum      factor=  1.1481 is_pro_rata=True  loader_admits=False
empty-meta    factor=  1.1481 is_pro_rata=True  loader_admits=True
no-sum-key    factor=  1.1481 is_pro_rata=True  loader_admits=False
no-count-key  factor=  1.1481 is_pro_rata=True  loader_admits=False
none-entry    factor=  1.1481 is_pro_rata=True  loader_admits=False
null-control  factor=  7.4400 is_pro_rata=False loader_admits=True
pro_rata=1.1481  settled-formula=7.4400
```

The null control is `{"sum": 100.0, "count": 3}` against `{"sum": 0.0, "count": 3}` at spot: it returns `month_hours/100 = 7.44`, not the fallback. Every malformed arm returns `pro_rata_factor(now)` with no raise. `loader_admits` is `_clean_month` on the same shape: it drops every malformed month whole, so these arms are not reachable from the store today -- the guards make the function's own contract (no coverage falls back) true for a direct caller too, and name the census gap rather than hiding it. `_clean_month` and `_leaf` are untouched. The import and these three lines are the whole code change; nothing else in the branch moved.

`02a28aed14dbbcd3047e76fbd881d11ba987540b` merges main `4f3c73020` into the previous head, an automatic merge by the orchestrator, no resolution. Neither merge touches `custom_components/heatpump_optimizer/ledger.py` or any of the five `r10_sav_*` harnesses; the merge did move 22 other `custom_components/` files (366 insertions, 418 deletions), so the re-cut arms below are quoted at the re-cut head `4bf7c2eaa` they were measured at.

`4bf7c2eaa95b3b4463ba273e3ca4c230c435e32b` is this re-cut on top of the round-3 head `3b55da2c65ca24780fa2b6da5137d64332279b36`, in three commits: the one-basis ledger and the duty re-freeze (`a50fe5146`); the savings reference, the settlement and the golden claims (`0ff823754`); the restored harness, the re-anchored proof and the control (`4bf7c2eaa`). Every re-cut figure quoted at `4bf7c2eaa` is taken against the merge base `3b4180dcc680e2e2e06f4d8ed0a0839a7374d78f`, the same base the round-3 verdict used, so both ends of every comparison are like for like. The relaunch's own figures are re-taken on the pushed lineage: the scoped gate at `805550f53`, and the census, the mutation table, the diff stat and the structure ratchet at the measured head `6d526cfdc`.

Round 3's head `3b55da2c` merged origin/main `3b4180dcc` into its predecessor; that merge is unchanged and is still this branch's base.

## Mutation proof

`python3 dev/audit/harnesses/r10_sav_baseline_mutants.py <copy>`, run on a `git archive HEAD` copy of the re-cut head `4bf7c2eaa`. M0 (unmutated): rc=0, failing=0. Every live mutant is killed by the `3L-G7 — monthly savings history` section of `tests/features.py`:

- M1 baseline starts from the plan's state — failing=6
- M2 held slab without its demand term — failing=5
- M4 coverage factor → calendar day — failing=4
- M5 savings priced at spot only — failing=2
- M7 metered energy without immersion — failing=1
- M8 settled hours never folded — failing=4
- M9 no start settlement (space path) — failing=4
- M10 start debit unbounded — failing=4
- M11 start settled at the caps only — failing=5
- M12 DHW path bounds the start by baseline_cost — failing=1
- M13 coverage factor unclamped — failing=1
- M14 negative thermostat cost unclamped — failing=1
- M15 start surplus unclamped — failing=1
- M16 held slab below target — failing=1
- M17 no plan line books, so the row never calibrates — failing=6

Two are retired, each with its reason printed beside the run: M3 (row actual from `savings_actual`) and M6 (capacity extrapolated), because the owner's one-basis acceptance made their degenerate form the required behaviour — the row's actual *is* the metered savings line, and capacity is in neither column. The checks pin that instead.

This file is therefore **not** the base's bytes, and it cannot be: ten of the committed list's sixteen anchors named lines that the accepted one-basis change removed, so the proof is anchored on the tree it runs against, and its own `assert orig.count(old) == 1` refuses any anchor that stops being unique. Restoring the committed list verbatim leaves the proof dying at M1's assertion, which is round 3's blocker 2. The measurement harness (`r10_sav_baseline.py`) is the finder's, byte for byte; this file is the proof beside it, not the instrument that found the finding.

The comment-only null control M0 is listed above and the mutation table's own null is `ledger.py:34 NULL_COMMENT`, which survived every driver in play.

## Instrument changes

Two files under `dev/audit/harnesses/` differ from the base. `r10_sav_baseline.py` is the finder's, restored byte for byte — `shasum -a 1` reads `bc31f356191ededbfb0b15f768b258249867b134`, the base's own value, and it is not touched again. `r10_sav_baseline_mutants.py` is re-anchored, and that is the whole change: ten of the committed list's sixteen anchors no longer occur in the tree, because the owner's one-basis acceptance removed the lines they named. Each one, and what happened to it:

| mutant | base anchor | at the re-cut head `4bf7c2eaa` |
|---|---|---|
| M1 | `state = _thermostat_held_state(` / `self.model, initial_state, weather,` / `_baseline_target(comfort_targets, 0, self.config.target_temp),` / `)` | re-anchored: `state = _thermostat_held_state(self.model, initial_state, weather, targets[0])` — `_baseline_targets` hoists the setpoints, so the three-line call the old anchor spelled is gone |
| M3 | `actual_sek = self.month_cost(key)` | **retired**: `MonthlyLedger.month_cost` is deleted by the one-basis acceptance; the row's actual is the metered savings line, so the mutant's degenerate form is the required behaviour |
| M4 | `return max(1.0, month_hours(now) / settled)` (method body, 12-space indent) | re-anchored: the same predicate at module level, 8-space indent — `coverage_factor` was extracted out of `MonthlyLedger`. Its degenerate form is still `pro_rata_factor(now)` |
| M6 | `actual_sek = (actual_sek - capacity) * factor + capacity` (16-space indent, inside the month row) | **retired**: the capacity column is in neither column of the row, so there is no line left to extrapolate |
| M9 | `) - self._start_gap_cost(` / `initial_state, weather, comfort_targets, prices, outdoor_temps,` / `space_caps, h.humidity, baseline_cost,  # the space-only reference` / `)` | re-anchored: the call moved into `_settle_horizon`, which returns `end - self._start_gap_cost(...)` over `h.initial_state`, `reference_targets` and `space_baseline_cost` |
| M10 | `return capped - min(surplus_above_caps, max(0.0, space_baseline_cost))` | re-anchored onto the bounded-debit return `return max(min(capped, uncapped), -displaced)`; still degenerates to `return min(capped, uncapped)` |
| M11 | the same line as M10 | re-anchored onto the same line; still degenerates to `return capped` |
| M13 | `return max(1.0, month_hours(now) / settled)` | re-anchored: the same predicate at module level, 8-space indent; degenerates to `return month_hours(now) / settled` |
| M14 | `max(0.0, space_baseline_cost))` (a fragment of the old return) | re-anchored: `displaced = max(0.0, space_baseline_cost) + max(0.0, -end_cost)`; degenerates to the unclamped first term |
| M15 | `surplus_above_caps = max(0.0, capped - uncapped)` | re-anchored onto the same bounded-debit return as M10; degenerates to `return max(uncapped, -displaced)` |

Six anchors — M2, M5, M7, M8, M12, M16 — occur at the re-cut head `4bf7c2eaa` exactly as committed and were not touched.

**The control that separates "re-anchored" from "weakened".** For each retired mutant the line it targeted is absent from the re-cut head `4bf7c2eaa`, counted rather than asserted: `month_cost` has 0 occurrences in `custom_components/heatpump_optimizer/ledger.py` (`grep -c` = 0), its M3 anchor 0; M6's anchor 0, and `capacity` has 0 occurrences inside `savings_months`. Both are dead code at the re-cut head `4bf7c2eaa`, not survivors that stopped being tested. The ten base anchors' occurrence counts at the re-cut head `4bf7c2eaa`, from the committed list read as data: M1 0, M3 0, M4 0, M6 0, M9 0, M10 0, M11 0, M13 0, M14 0, M15 0; M2 1, M5 1, M7 1, M8 1, M12 1, M16 1.

**The pre-fix control.** The mutant harness itself cannot run against the pre-fix tree — its anchors name lines the fix added, which is what an anchor is for. What can run is the section the mutants are judged by: the re-cut head `4bf7c2eaa`'s `tests/features.py` `3L-G7` section, executed against a tree that carries the re-cut head `4bf7c2eaa`'s tests and the merge base's `custom_components/`. It fails there, 5 of its checks: "open month scales the baseline, the actual and the saving by one factor"; "a closed month is unscaled; nothing saved reads baseline == actual on the energy basis"; "the closed month's actual is the covered metered energy at spot plus fee, not the bill" (actual_sek 15.0, the bill); "the open month scales by the month's hours over the hours it settled" (no coverage meta on that code); "the capacity line is in neither column: baseline less actual is the saving". The same section passes on the re-cut head `4bf7c2eaa` (M0, rc=0, failing=0). The checks bite on the pre-fix code and the proof's mutants are anchored to the code that makes them pass.

## Null control

`r10_sav_baseline.py`, the finder's bytes, run from a worktree of the merge base `3b4180dcc` and from the re-cut head `4bf7c2eaa`:

| arm | base `3b4180dcc` | head `4bf7c2eaa` |
|---|---|---|
| transient | SOUND, 2.06 kW at all four starts, spread 0.00 | SOUND, 2.06 kW at all four starts, spread 0.00 |
| cost (row Actual against the receipt's bill) | SOUND, 15.0 vs 15.0 | DEFECT, receipt 15.0 vs row 4.2 |
| coverage | SOUND, 28.00 | SOUND, 28.00 |
| null (flat price, two days, hourly re-plan) | DEFECT, 10.83238932735682 % | DEFECT, 10.83062946138871 % |

The cost arm's reversal is the one-basis acceptance: the row no longer carries the bill's capacity, wear and immersion lines that the receipt totals, and review has accepted that. It is reported as a DEFECT here because the finder's arm asserts the older identity.

The round-3 head `3b55da2c`, measured on the same bytes for the record: transient DEFECT (spread 0.07), cost DEFECT (15.0 vs 4.2), coverage SOUND (28.00), null DEFECT (6.179161545814557 %).

`r10_savings_upgrade_month.py` reads **upgrade 2.800, null 28.000, fresh 2.800** — the control's three expected factors, rc=0.

`r10_sav_volume.py`: flat SOUND, saving 0.0000 at `meter_calibration` 1.56; vary SOUND, timing +74.88; the meter-reads-the-model arm keeps 48.0 at calibration 1.0.

`r10_sav_null_terms.py` at the re-cut head `4bf7c2eaa`, both arms: booked 128.4 kWh against plan 114.5; steady at target 128.4, steady at the delivered room 121.7; plan mean room 18.79 °C against a mean comfort target 20.44 °C; stored heat drawn −23.7 kWh_th; power-weighted COP 8.383 against 7.149 (+17.27 %).

## Figures

- Finite-float census (D7-s2-58): `python3 tests/finite_boundary.py` at `02a28aed` printed `1 of 108 FINITE BOUNDARY CHECKS FAILED` with `stray=['ledger.py::coverage_factor'] stale=[] owner_found=True plant_found=True`; at the measured head `6d526cfdc` it prints `ALL 108 FINITE BOUNDARY CHECKS PASSED`, and the FAIL line's own tuple -- `stray=[...] stale=[] owner_found=... plant_found=...`, which the script prints only on a failure -- is gone; the passed check's line carries no tuple. (The first green run was at `805550f53`; the same script at `6d526cfdc`, after the two `int()` sites were guarded, is the one cited here.) A mutation of the fixed line back to `float(entry["sum"])` at `805550f53`, run on an uncommitted copy and restored and timed, prints `1 of 108 FINITE BOUNDARY CHECKS FAILED` with the same stray -- killed.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=524c1896b PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash tests/run.sh` at `805550f53` (the head the fix first landed at) printed `MODE: SCOPED -- 28 script(s) run, 5 scoped out` and finished in 5255 s with 3 scripts red -- `optimality.py`, `card.mjs`, `stress.py` -- each the environment red already recorded under Red checks (`one|summer_negative|shoulder` on arm64, the node heap OOM, and `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`), none this diff's. `finite_boundary.py` (185 s) passed inside the gate, as did `structure.py`, `features.py`, `entities.py`, `env_drift.py --all` and the rest. The head then moved by one commit, `6d526cfdc` -- three lines and a docstring clause inside `coverage_factor`, the function the census and `r10_savings_upgrade_month.py` both exercise. No gate was re-run at `6d526cfdc`: the evidence re-taken at that head is the census and the mutation control (first bullet), the upgrade-month harness, and the structure ratchet below, and CI's full suite runs at the pushed head.
- Harnesses (files unchanged by `6d526cfdc`; sha1 of each at the measured head): `r10_sav_baseline.py` `bc31f356191ededbfb0b15f768b258249867b134` (the base's bytes, unchanged); `r10_sav_baseline_mutants.py` `1ae1fe4a5338841b633b07f280f5ccfadadea8c4` (re-anchored on this tree — see Mutation proof); `r10_savings_upgrade_month.py` `597657aec717640c5015e9bbd08354d251fc4a3e` (ported to the module-level `coverage_factor`, same three factors); `r10_sav_volume.py` `be62082cc746a336a5580742b3047b2acc8f17df` (unchanged since round 3); `r10_sav_null_terms.py` `c981e7c840ede1a5fef95aa903e00e5809c92aa7` (the base's bytes, unchanged).
- Golden claims: `tests/golden/claimed_drift.txt` differs from the base by exactly two lines — `negative_prices` and `summer_dhw_only`, both "the warm start is debited only what it displaced". `env_drift.py --all` against origin/main prints `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE: 56 committed fixture(s)`. `--claims-only 3b4180dcc` is ok. `tests/golden/card_claimed_drift.txt` is byte-identical to the base.
- `git diff $(git merge-base origin/main HEAD)...HEAD --stat` is 49 files, 843 insertions, 320 deletions.
- Structure: `python3 tests/structure.py` at the measured head `6d526cfdc` prints `STRUCTURE RATCHET PASSED`, `class_excess_loc 18047 <= 18047`; every budget line reads at or below its cap. (`class_excess_loc` was 18079 at the re-cut's merge base and 18059 at the re-cut head, re-recorded in `4bf7c2eaa`; the merge-forward took main's lower 18047 budget.)
- `python3 tests/closure.py canonical` leaves `tests/closures.json` byte-identical.
- Architecture: `python3 tools/audit/archscore/score.py --diff <merge base> HEAD` prints `Architecture score: dS +0.0000 NULL`.
- `node tools/policy/policy_lint.mjs --budgets` exits 0.
- `python3 -I tools/audit/carry_audit.py check --body <this body>` -- the reading `pr-contract` runs -- prints `CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)`.
- Mutation table: `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --base origin/main` at the measured head `6d526cfdc` prints `3814 unpinned site(s) of 6396 candidate sites, 3818 at the ratchet base 524c1896b...; the ledger agrees with the deterministic inventory`, with no `ADDED UNPINNED` line. The mutant phase of that run was still in flight when this body was set (its baseline drivers report as they finish; `tests/features.py` rc=0), so no mutant verdict is cited from it — the mutation job at the pushed head is the verdict.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=3b4180dcc PYTHONPATH=tests/hastub PREPR_SKIP_CLOSURES=1 bash tests/run.sh` at the re-cut head `4bf7c2eaa` printed `MODE: FULL -- every test script runs, nothing is scoped out` (with no recorded closures the run cannot skip safely) and finished in 4695 s with 4 scripts red: `entities.py`, `optimality.py`, `card.mjs`, `stress.py`. Every one of the four reproduces at the merge base in this container — details and numbers in Red checks. Every other script passed, including `features.py` (ALL 4463 FEATURE CHECKS PASSED), `plan_view.py`, `card_drift.mjs`, `env_drift.py --all` (which is the golden check in `GOLDEN_MODE=drift`; `tests/golden.py` is skipped in that mode), `guard_pins.py`, `manual_plan.py`, `typing_ruler.py`, `validate.py`, `wood_advisor.py`, `finite_boundary.py` (ALL 106 FINITE BOUNDARY CHECKS PASSED) and `harness_headers.py` (ALL 112 HARNESS HEADER CHECKS PASSED).

## Red checks

- `tests / fast (3.14)` at `02a28aed` -- the finite-float census (D7-s2-58): `1 of 108 FINITE BOUNDARY CHECKS FAILED`, `stray=['ledger.py::coverage_factor']`. Fixed at the measured head `6d526cfdc` (Figures). The `gate` red was derivative: its only line was `FAIL tests / fast (3.14): failure (this run)`. **Root cause (`defect-root-cause.md`), state (d)**: the process was sound and its precondition changed underneath it -- the branch's last local run predated main `4f3c73020` landing the census, and the merge-forward produced a head no local run had measured. The cheaper detector is `python3 tests/finite_boundary.py` itself: one local run of 295 s on this box, in the fast lane already. The countermeasure is `fixer.md` step 6's re-execution of steps 2-8 after any merge, which this relaunch follows: the census and the structure ratchet are re-taken at `6d526cfdc`, and the scoped gate ran at `805550f53`, the head the fix first landed at.

The four reds below are the re-cut head `4bf7c2eaa`'s, each attributed against the merge base `3b4180dcc` in this container, three-dot; none is this diff's.

- `tests/entities.py`: `4 of 2463 ENTITY CHECKS FAILED`. The same script, on a worktree of the merge base, prints `4 of 2463 ENTITY CHECKS FAILED`, and the printed FAIL-line sets are identical between the two runs (`diff` of the two sets is empty; compared as sets, not totals). The failures include the `hb:` heartbeat controls, which time a spin against a wall clock, and this box was at load 220 during the run. Cheaper detector: none is owed — the check is the detector, and it fires on the base too.
- `tests/optimality.py`: `1 of 84 OPTIMALITY CHECKS FAILED` — `one|summer_negative|shoulder: a recorded claim still has a gap ... claimed but gap 0.0000%`. This is the case `tests/optimality.py`'s own comment already records: "CI's linux fast lane still measures ladder +10.55 %, though the arm64 seat reaches the basin ... so this claim reads stale on arm64 only. The gate's platform is the one that counts." This container is arm64. Not this diff's, and removing the claim would make CI red.
- `node tests/card.mjs`: `FATAL ERROR: Ineffective mark-compacts near heap limit ... JavaScript heap out of memory`, at the end of ~10,700 checks. On a worktree of the merge base, `node tests/card.mjs` aborts the same way (`Abort trap: 6`, same V8 trace). This container's node build runs out of default heap on the full card suite regardless of this diff. Cheaper detector: none is owed here; the crash is the runner's.
- `python3 tests/stress.py`: `1 of 113 STRESS CHECKS FAILED` — `shoulder: cheaper than holding the setpoint [4.67 vs 3.96]`. Measured directly at both ends with the same case builder: base `plan 4.67, thermostat 3.96`; head `plan 4.67, thermostat 3.96`; winter and winter_extreme also identical (23.28/88.96 and 41.40/170.34). The solver finding the same non-optimal basin on this loaded box is the runner's condition, not the diff's. The production-call channel is green in the same run: `20 of 20 family members judged against 3b4180dcc..., re-planned: [], new on this branch: []`.

The mutation-table baseline red and the `tests/entities.py` red are the same failure and are reported once.

**The CI check names this branch's own commits carried red.** `prepr.sh`'s ancestry arm derives these from the check runs on every commit this branch pushed (`3b4180dcc..origin/fix/r10-sav-comfort`), so each is named and answered here rather than left to the new head's runs:

- `tests / fast (3.14)` — red at `c70c3e464` (2026-10-24) on `tests/stress.py`'s production-call arm: `winter/1z/space/pin-off: 84263 production calls against the baseline's 78480 = 1.074x on work the counts vouch at 1.001x, over the 1.05x allowance (thermal_model.py +4072, optimizer.py +1654)`. That arm passes at the re-cut head `4bf7c2eaa`: the gate run above reports `1 of 113 STRESS CHECKS FAILED`, its one FAIL the solver-basin check `shoulder: cheaper than holding the setpoint`, and the production-call channel prints `20 of 20 family members judged against 3b4180dcc..., re-planned: [], new on this branch: []`. The arm is its own detector, its standing cost one stress run on the fast lane; there is no cheaper proxy for interpreter work that moves no evaluation or simulate count.
- `tests / mutation` — red at `36c985d33` (2026-10-25): `MUTATION TABLE REFUSED -- 3993 unpinned site(s) against 3990 at the ratchet base …, 6 of them added by this diff`, its `ADDED UNPINNED` lines on `optimizer.py` (the `_baseline_targets` returns and its guard, the `two_tank and state.wood_tank_temperature` guard and boolop, and `power = min(required_thermal / cop, p.max_electrical_power)`). At the re-cut head `4bf7c2eaa` the same command prints `3900 unpinned site(s) of 6416 candidate sites, 3904 at the ratchet base 3b4180dcc...; the ledger agrees with the deterministic inventory`, with no `ADDED UNPINNED` line — four below the base, so those six are not on the re-cut head `4bf7c2eaa`. The table is its own detector, and `--pin-killed` is the cheaper repair; both run in this job.
- `tests / replay` — red at `8174249e1` (2026-10-25) on `synthetic-dhw-only.json: cycle_cost [2 offender(s): cpu_ratio 2.216 over its budget 2.173 | loop_cpu_ratio 0.1441 over its budget 0.143]` — 1.98 % and 0.77 % over, on a shared runner. Not re-measured at the re-cut head `4bf7c2eaa`: the head is unpushed, so that job has not run on it, and it runs at the pushed head. Its detector is a CPU ratio against a recorded replay and a wall-clock proxy would be noisier, so no cheaper detector is owed.
- `governance / delivery-status` — red at `8d0572dc3` (2026-10-25) on the board-wide `overdue` list (`#2799`, `#2780`, `#2749`, … — rows a batch had not drained). The job's own output says it is "NOT a required context and a red here blocks no merge"; it is not this diff's and says nothing about this row.

## Forward-carry

- Carry 5, seam 2: actuate the supply switch at step boundaries from a one-minute tick, rather than at the cycle phase. Its owed controls are a synthetic install with the cycle phase at 0 and at 14 min that books identical duty verdicts, and one mutant per seam. It moves the actuator edge (`coordinator._apply_action`, `early_cutoff`, `pump_arbiter.switch_supply`) and needs a design note first. Main's roster, `dev/programme/rosters/wave-r10-groups.json`, holds the group for it, R10-SAV-ACTUATION (after R10-SAV-COMFORT, issues [2492]), whose `carry` already records both controls. Carry: R10-SAV-ACTUATION
- Review 6387209379's seam census (the Evidence bullet naming card line 8587): a census result, not a defect. Its own words are "No seam is open", and the one reader it names, card line 8587, reads the plan-horizon prediction, divergence (a). Carry: dismissed: census result with no seam open; card line 8587 is divergence (a), already out of scope by carry 3, per the census evidence review 6387209379 cites (item e4b56a35)

## Friction

- round-3-instrument-rewrite: cost: the round-3 branch rewrote the finder's own harness (`r10_sav_baseline.py`, 49 lines) and replaced the owner-required flat-price null arm with a comfort-term comparison; the round-4 re-cut restored the bytes and had to decide, from measurement, which of two arms the branch could keep. Carry: dismissed: the review caught it and the re-cut pays it; the process state is that a fixer may not re-specify the instrument that found the finding, which `fixer.md` already states — no new countermeasure is owed by this PR.
- entity-heartbeat-load: cost: `tests/entities.py`'s `hb:` controls time a spin against a wall clock and read red on a box at load 220; the same 4 of 2463 fail at the merge base. Carry: dismissed: environment-only, reproduced at the merge base with an identical FAIL set

