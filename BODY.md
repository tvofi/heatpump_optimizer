R10-SAV-BASELINE. Closes #2255, the owner's savings items 1, 2 and 5 (tvofi, 2026-10-14): September at 81 % saved against a plain thermostat, an October estimate with a baseline below the actual, and a receipt total that disagreed with the month table's Actual.

**Item 1, the baseline.** The settlement books `baseline_power_schedule[i]` from the plan covering each interval. That figure was the thermostat's first step, and the thermostat started from the plan's measured house. So it booked the recovery transient: 6.00 kW (the clip) whenever the optimiser had left the house below target, and 0.00 kW at or above it. A month of such first steps is the transient's month, not a thermostat's. `_compute_baseline_power` now starts from `_thermostat_held_state`: zones at the step's comfort target, slab at the temperature that delivers that demand. The booked step is then the steady holding power whatever the plan did before. Starting the reference held while the plan starts measured leaves the two with different stored heat at the start, as they already differ at the end. `_start_gap_cost` settles the start gap the same way `_deferred_energy_cost` settles the end gap, and the caller nets it off. A pre-heated start is debited past the end's comfort caps, because the plan coasts on that heat, but by no more than the thermostat's space-heat cost over the horizon (on the hot-water path, the space reference's share of `baseline_cost`): stored house heat displaces only space-heat purchases that exist. Without the start settlement, a plan starting below band read as losing money for buying its own heat back.

**Item 2, the open month.** It was scaled by the calendar day (`days / day-of-month`), so an install that settled 24 hours of February was scaled as if it had run ten days. It now scales by the month's hours over the hours it settled (`settled_hours`, a ledger meta folded on every settlement, priced or not). The capacity line is a whole-month figure (the running billed peak) and is not extrapolated.

**Item 5, one cost source.** The receipt's total summed the billed lines; the table's Actual was `savings_actual`, a second accumulation that dropped every interval no plan covered and every line but spot. The row's `actual_sek` is now `MonthlyLedger.month_cost`, the same `billed_total` over the same lines the receipt adds. `savings_sek` is thermostat less plan over the covered intervals, both priced at spot plus the interval's grid fee. `baseline_sek` is the bill plus that saving, so the lines no thermostat model prices (capacity, wear, uncovered intervals) are held equal on both sides. `_contract_comparison` reads the ledger's `metered_energy` instead of adding spot and immersion itself.

**What R10-SCORES and R10-ADVISOR read after this.** For each `savings_months` row:
- `actual_sek` is the month's bill (the receipt total, every billed line).
- `savings_sek` is thermostat minus plan over intervals a plan covered, at spot plus the grid fee.
- `baseline_sek` is `actual_sek + savings_sek`.
- The open row is scaled by the month's hours over its settled hours, with capacity unscaled.

`predicted_savings` and `deferred_energy_cost` are settled at both ends of the horizon (`deferred_energy_cost` is end gap less start gap). One view of savings: `ledger.savings_months` for months, the plan's `predicted_savings` for the horizon. No second computation of either.

**The flat-price null control does not read about 0, and this pull request does not redefine the baseline to make it.** On a flat price, with the plant equal to the model, the month row reads 10.83 % saved at the head and 43.66 % at the merge base. The transient that made up most of the base figure is gone: booked thermostat energy is 203.6 kWh at the base and 128.4 kWh at the head, against the plan's 114.5 kWh. The remaining 13.9 kWh gap has three terms. They were measured by the round-1 reviewer's probe, kept in the tree as `dev/audit/harnesses/r10_sav_null_terms.py` and re-run at the head:
- (a) Comfort: 6.6 kWh, about 5 of the 10.83 points. That is a steady thermostat at the comfort target (128.4 kWh, equal to the booked baseline) less a steady one at the room the plan delivered (121.7 kWh). The plan holds a mean 18.79 °C against a mean target of 20.44 °C.
- (b) COP timing: the plan's power-weighted COP is 17.27 % above the thermostat's. Over the window the outdoor temperature runs from -16 to -8 °C, and the plan buys its heat in the warmer hours. That is a real saving at a flat price, so a comfort-matched baseline must not cancel it.
- (c) Unsettled stored heat: the plan ends the 2-day window holding 23.7 kWh_th more than it started with (room/slab 21.00/22.00 → 19.36/30.01), about 13.3 kWh_e at the steady COP. The month row does not settle it (`predicted_savings` does), and here it offsets (b).
- The control is the `const` arm, with outdoor held at the window's mean. Timing reads +0.00 %, and the 15.6 kWh gap is comfort 5.1 plus a start drawdown of 10.1. The plan's thermal balance closes in both arms (240.0 = 240.0 and 200.9 = 200.9 kWh_th).
- So "comfort traded for money", as round 1 had it, names only term (a). The carry below asks for an acceptance that separates the three terms, not a null of about 0.

**A known limit of the start bound, measured.** `summer_dhw_only` reads -12.74 % predicted savings at the head (-3.17 % on main; -0.27 SEK on a 2.09 SEK reference). The summer house starts above the end's comfort caps, and the thermostat's space-heat cost over that horizon still exceeds the surplus, so the debit is not bounded away. Settled at the caps alone this fixture read 1.95 %, but that read the away-setback fixture at 60.71 %. Carried with the null's terms below, since both turn on what the reference is credited with.

## Head

f5ad054550cea2e572133f4a5693de5c13d5c293

Merge base 55dc8d9c2. Main merges into this branch: 6 (42e6dedb2, 3fb386d50, dc8aa807f, 413944b67 by the orchestrator, 003c3731c, then 55dc8d9c2; the last brought only CodeQL scoping and delivery rows). Only 413944b67 (#2365, R10-PUMP-MODEL) touched production code: `thermal_model.py`, `pump_arbiter.py`, `plan_step.py` and `coordinator.py` outside the #2255 seams. None of the five touched `optimizer.py` or `ledger.py`. Where each figure was measured:
- The harness arms (`r10_sav_baseline.py`, `r10_sav_null_terms.py` both arms) and the savings section (`ALL 33 ... PASSED`): at 7b4069789, after the last main merge. Every figure equals the round-1 figure.
- The mutation table and the site mutants: production code of e86c2085d, which is the head's for `optimizer.py` and `ledger.py`. The round-1 reviewer re-ran the table at b7a34f98a: all 16 killed.
- The golden drift with the claims: 09d3fe38f. CI's `env-matrix` was green at b7a34f98a.
- `tests/optimality.py`: the merge base and be2cac624 on the arm64 seat, and CI's `fast (3.14)` at b7a34f98a (check-run 117692786859).

## Mutation proof

`dev/audit/harnesses/r10_sav_baseline_mutants.py` applies each mutant to a scratch copy of e86c2085d, runs the #2255 checks (the `3L-G7` savings section of `tests/features.py`), and restores. Every mutant replaces a predicate of the fix. All 16 are killed.
- M0, unmutated: 0 failing.
- M1, the thermostat starts from the plan's state (`state = initial_state`): 5 failing. `the booked thermostat step is independent of the plan's start state` (single-zone `[0.0, 6.0, 6.0, 0.0]`; two-zone, DHW), `the booked thermostat step is the steady holding power at target`, and `the predicted saving moves less with the start state than the plan's cost` (single-zone; two-zone, DHW).
- M2, the held slab without its demand term: 4 failing. Both `independent of the plan's start state` checks (`[6.0, 6.0, 6.0, 6.0]`), `the steady holding power at target`, and `a start colder than the held house is settled at the caps, with no surplus to debit`.
- M3, the row's actual from `savings_actual`: 5 failing. `open month scales the bill and the saving by one factor`, `a closed month is unscaled; nothing saved reads baseline == actual == bill`, `the closed month's actual is the receipt's total, not a second sum`, `the open month scales by the month's hours over the hours it settled`, `the capacity line is a month figure already and is not extrapolated`.
- M4, the coverage factor back to the calendar day: 3 failing. `the open month scales by the month's hours over the hours it settled`, `the capacity line is a month figure already and is not extrapolated`, `a month that settled more hours than it has is never scaled down`.
- M5, the saving priced at spot alone: 1 failing. `the saving prices both sides at spot plus the grid fee, covered intervals only`.
- M6, capacity extrapolated: 2 failing. The first two of M4's three.
- M7, metered energy without immersion: 1 failing. `the ledger's metered energy is spot plus immersion, the one energy figure`.
- M8, settled hours never folded: 3 failing. The same three as M4.
- M9, no start settlement on the space path: 1 failing. `the predicted saving moves less with the start state than the plan's cost (single-zone)` (savings `[17.87, 9.61, -0.21, 28.43]`).
- M10, the start debit unbounded: 3 failing. `with a thermostat that buys nothing, the start is settled at the caps`, `between the two, the debit past the caps stops at the thermostat's cost`, `a negative thermostat cost (negative prices) never turns the debit into a credit`.
- M11, the start settled at the caps only: 2 failing. `with demand to displace, the pre-heated start is debited past the caps`, `between the two, the debit past the caps stops at the thermostat's cost`.
- M12, the hot-water path bounds the start by `baseline_cost`: 1 failing. `the hot-water path bounds the start debit by the space reference's cost, not the tank's`.
- M13, the coverage factor without its floor of 1: 1 failing. `a month that settled more hours than it has is never scaled down`.
- M14, a negative thermostat cost unclamped: 1 failing. `a negative thermostat cost (negative prices) never turns the debit into a credit`.
- M15, the start surplus unclamped: 1 failing. `a start colder than the held house is settled at the caps, with no surplus to debit`.
- M16, the held slab allowed below target: 1 failing. `with no demand at the held target the slab sits at the target, not below it`.

Three existing checks change, each because the fix changed what they measure:
- `with a pending baseline both savings lines move` in `tests/features.py` now expects spot plus the grid fee (5.0 and 2.5 SEK where spot alone gave 4.0 and 2.0).
- R9-F2.3 D2-s2-03's spy on `_deferred_energy_cost` kept the last call. The start settlement now calls that function after the end settlement, so the spy keeps the first call, the end's.
- `tests/optimality.py`'s `_CERT_CLAIMS` loses `one|winter_narrow|shoulder`, which the held baseline closed: ladder +0.70 % at the base, 0.0000 % at the head on the arm64 seat and on CI's `fast (3.14)` (check-run 117692786859). `one|summer_negative|shoulder` stays claimed. The arm64 seat reaches its basin (obj 0.2548, 0.0000 %; base +5.04 % re-polish, +9.96 % ladder), but CI's linux lane does not (obj 0.3058, ladder +10.55 %). The gate's platform counts, so the claim's stale check fails on arm64 only; round 1 retired it on the arm64 figure, and CI's fast lane went red. `one|shoulder|winter_cold` stays claimed. The baseline energy seeds the solver's anchor starts, so a steady reference seeds better basins where the platform's line search reaches them.

## Null control

`dev/audit/harnesses/r10_sav_baseline.py` at the merge base 42e6dedb2 and at c1a6598ce. Four arms; base: 4 defect, head: 1 defect (`null`).
- transient: booked first step across four start states. Base 0.00, 6.00, 6.00, 0.00 kW (spread 6.00); head 2.06 kW for all four (spread 0.00).
- cost: receipt total 15.0 SEK; row actual 3.0 at the base, 15.0 at the head.
- coverage: 24 settled hours of 672; open-row scale 2.80 at the base, 28.00 at the head.
- null (flat price, plant equal to the model, 2 days, re-plan hourly): base 43.66 % saved (thermostat 203.6 kWh, plan 114.7 kWh, house 18.75 °C mean against a 20.44 °C mean comfort target); head 10.83 % (thermostat 128.4 kWh, plan 114.5 kWh, house 18.79 °C against 20.44 °C). Reads `DEFECT` at both ends against its 3 % threshold. The residual is the three terms above.

The predicted-savings consequence of the held start, measured with the golden matrix (`GOLDEN_MODE=drift`). `savings_percentage` at main, then with the start settled at the caps alone, then uncapped, then with the bound this branch ships:
- away_setback: 34.18, 60.71, 29.09, 29.09
- start_above_band: 56.58, 61.03, 45.00, 45.00
- summer_dhw_only: -3.17, 1.95, -12.74, -12.74
- start_below_band: 23.73, 24.58, 24.58, 24.58

The capped and uncapped arms were measured on a scratch tree. The shipped values are those claimed in `tests/golden/claimed_drift.txt`.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline.py`: every arm figure in `## Null control`, at c1a6598ce and at the merge base.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_terms.py` and the same with `const`: the residual's three terms and the control in the null-control paragraph (6.6 and 5.1 kWh comfort, +17.27 % and +0.00 % timing, 23.7 kWh_th stored, 13.3 kWh_e, 240.0 and 200.9 kWh_th balances), at 7b4069789. The probe is the round-1 reviewer's, kept verbatim but for the `const` switch.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline_mutants.py .`: the mutation table, M0 to M16, failing counts and names as printed.
- `GOLDEN_MODE=drift PYTHONPATH=tests/hastub python3 tests/golden.py`: before the claims, 50 unclaimed drifts, and the five `coord_*` captures byte-identical to main. With the claims, at 09d3fe38f: `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE: 56 committed fixture(s)`. The 112 leaf values printed for the claimed fixtures are identical before (3832613b9) and after (09d3fe38f) the hot-water bound change. Not re-run after the second main merge (CI's `env_drift` re-checks it). The 50 claimed fixtures are each moved `baseline_cost`, with the direction per fixture in the claim line. Of these, 19 carry a suspended may-drift entry, each with its restore note. One fixture outside may-drift lands in another basin: `valve_storage_low_target`, plan cost 61.91 → 61.05 SEK, because `baseline_energy` seeds three solver starts.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: against the merge base 3fb386d50, class_excess_loc 18368 → 18302, max_class_loc 8547 → 8544, seam_cut_total 720 → 719. All improved and recorded; the reasons are in the messages of commits c1a6598ce and 6b191f504.
  - The payment is the thermostat reference's pure physics (`_floor_demand_at_target`, `_thermostat_held_state`, `_baseline_target`, `_thermostat_demand_single`, `_thermostat_demand_two_zone`). These read nothing of the optimiser but its model, so they left `HeatPumpOptimizer` for module scope, and the two demand functions now share one floor-demand helper.
  - No raise.
- `python3 tools/audit/archscore/score.py --diff 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8`: `Architecture score: dS +0.0006 IMPROVES` (coord_footprint 2506 → 2505).
- `python3 tests/closure.py select --diff 3fb386d5044e4ca10b5f30c1c6f380139d5ad3e8 --workdir <dir>`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
  - Run locally green at 6b191f504 (17): `backtest`, `edge`, `validate`, `block_duty`, `manual_plan`, `plan_view`, `solar_alignment`, `wood_advisor`, `finite_boundary`, `guard_pins`, `boost_drift_replay`, `typing_ruler`, `doc_claims`, `deployment_shape`, `config_flow_steps`, `debug_collect`, `arch_score_head`; plus `golden` and `env_drift` through the drift run.
  - Left to CI (tvofi 2026-10-07 and 2026-10-18): `features`, `entities`, `stress`, `optimality`, `structure`, `harness_headers`, `card.mjs`, `card_drift.mjs`. Locally, two `tests/features.py` blocks passed at d2220949d. The `3L-G7` savings section with the #2255 checks: `ALL 33 ... PASSED`. The R9-F2.3 block holding D2-s2-03: `ALL 22 ... PASSED`. The full script's last local run, at be2cac624, failed only the two D2-s2-03 checks the spy fix repairs.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries`.

Seams of the class: the savings figures have three producers, and each is dispositioned here.
- `ledger.savings_months`: closed in this diff.
- `freeze_month_report` (the receipt): unchanged, now the same total.
- `_contract_comparison`: closed in this diff, reads `metered_energy`.
- The thermostat reference has one producer, `_compute_baseline_power`, for both the ledger's booked step and the plan's `baseline_cost`, closed in this diff; `tests/backtest.py`'s replay reads the same function and stays reconciled (green).
- `_baseline_house_load`, named in the group's seams: audited. It is the non-pump house load used by the fuse caps and PV surplus, not a savings input, and it is unchanged.
- narrative.py has no month summary. The month figures it might have carried are the ledger's (`month_summary`, `month_cost`), so it is unchanged.

## Unpinned sites

`ci_predict` listed 22 sites the diff adds with no pin; at this head it lists 19, because mutation-autofix pinned ledger.py:315 CLAMP_DROP, optimizer.py:280 RETURN_DEL and optimizer.py:335 CLAMP_DROP at 36723a969. Each was mutated on a scratch copy of e86c2085d (`probe/sites.py`, the same section run as the table above). A crash counts as a kill, because features.py then exits non-zero; each crash's exception is quoted from that run. Killed sites are pinned by `mutation-autofix` when CI's mutation job records them.
- custom_components/heatpump_optimizer/ledger.py:68 RETURN_DEL: killed (TypeError: None in the coverage division). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/ledger.py:186 CMP_BOUND: survivor, triaged equivalent. `dt >= 0` also folds a zero-length interval. `_coverage_factor` reads only the meta's `sum`, so adding 0.0 to it changes nothing. A zero `dt` is the only value the mutant admits.
- custom_components/heatpump_optimizer/ledger.py:186 GUARD_OFF: killed, 3 failing (M8's three). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/ledger.py:242 BOOLOP: killed (TypeError: `math.isfinite` handed None). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/ledger.py:304 RETURN_DEL: killed (TypeError: None in a subtraction). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/ledger.py:314 CMP_BOUND: killed (ZeroDivisionError at zero settled hours). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/ledger.py:314 GUARD_OFF: killed, 3 failing. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/ledger.py:315 CLAMP_DROP: killed by M13. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/ledger.py:316 RETURN_DEL: killed (TypeError: the meta-less month's factor is None). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:278 BOOLOP: killed by the new edge check (IndexError past a one-step schedule). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:278 CMP_BOUND: killed by the same edge check (the same IndexError). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:278 GUARD_OFF: killed, 3 failing. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:280 RETURN_DEL: killed, 1 failing (the edge check). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:298 GUARD_OFF: killed, 1 failing. `the held house at the booked power is a steady state of the plant model` sees the two-zone terms drift a single-zone room 0.06 K. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:303 RETURN_DEL: killed, 1 failing (the same steady-state check: the deleted return falls through to the two-zone terms). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:309 RETURN_DEL: killed (TypeError: None compared with a float). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:322 GUARD_OFF: killed by the edge check (IndexError on the empty weather). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:324 BOOLOP: survivor, triaged equivalent up to the exception's type. With both series present both forms pass. With either one None, the original raises AssertionError and the mutant passes to the `float(...[0])` on line 327, which raises TypeError. No value differs, so no check can pin it.
- custom_components/heatpump_optimizer/optimizer.py:335 CLAMP_DROP: killed by M16. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:5325 CLAMP_DROP: killed by M15. Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:5326 CLAMP_DROP*2: killed by M10 (the outer `min`) and M14 (the inner `max`). Pinned by mutation-autofix.
- custom_components/heatpump_optimizer/optimizer.py:5326 RETURN_DEL: killed (TypeError: None in a subtraction). Pinned by mutation-autofix.

## Red checks

Every failed check run on the PR branch's pushed commits (the ancestry of `fix/r10-sav-baseline` from the merge base). Each has its answer.
- `pr-contract` (117692504964, 117692618046, 117704466268): `REFUSE 'Closes #2255' closes #2255; not in the intended list`. The orchestrator answers it by wiring 2255 into R10-SAV-BASELINE's `fixes` on the roster, so `Closes #2255` stays.
- `fast (3.14)` at b7a34f98a (117692786859) and at 36723a969 (117704407882, 117704447188): `tests/optimality.py`, `one|summer_negative|shoulder: no unclaimed gap above the bar` (ladder +10.55 %, `claimed=False`), 1 of 84. This diff caused it: round 1 retired that claim on the arm64 figure. Answered by eeb607dd6, which keeps the claim. This head carries it.
- `mutation` at 62f3704f7 (117691643842), b7a34f98a (117692723200) and 36723a969 (117704368238, 117704375789): `MUTATION TABLE REFUSED`, the sites this diff adds (23, then 20 once 36723a969 pinned three). This diff's, by design. Every site is answered under `## Unpinned sites`. mutation-autofix pinned `_coverage_factor` CLAMP_DROP, `_baseline_target` RETURN_DEL and `_thermostat_held_state` CLAMP_DROP at 36723a969, and this head merges that commit (aba674bca). The two survivors are triaged there.
- `nightly-ha (stable)` at 36723a969 (117704407933): `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`. This is the runner, not this diff. The heartbeat's positive control spins the event loop for 600 ms on purpose, reads it as 600.2 ms, and the loop's own dump names the spin (`dump names the spin: True`). Only the py-spy leg failed: `py-spy did not run: TimeoutExpired: Command '['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid', '1']' timed out after 30 seconds`. `run:exit_status` is that failure's container exit. The other 62 checks passed, among them the entity, payload, plan and reload arms. `nightly-ha (2025.2.0)` (117704407742) passed on the same commit. The diff touches no heartbeat, py-spy or container code. The answer is a re-run at the new head. A cheaper detector would be the py-spy leg's own timeout reported as a skip of that leg, not a FAIL of the positive control. I have not filed that, because one timeout is not yet a recurrence.

## Forward-carry

The carries go into the tree as roster carries appended by the orchestrator (`roster_edit append-carry`); the texts are in the seat's report.
- The month row's flat-price null, its three terms, and the `summer_dhw_only` start-bound limit. These go to the group the orchestrator adds for the comfort-matched baseline. R10-ADVISOR's seam (the what-if and its card) does not own `_compute_baseline_power` or `ledger.py`.
- R10-ADVISOR: its carried null ("savings about 0 on a flat-price profile"), restated so its acceptance separates comfort, COP timing and stored heat. The `const` arm of `r10_sav_null_terms.py` is the control.
- R10-SCORES and R10-ADVISOR: the row semantics in "What R10-SCORES and R10-ADVISOR read after this".
- The stamp (`tools/release/stamp.py` / web-stamp): restore the 19 suspended may-drift entries verbatim when the stamp empties the claim list. The obligation is written beside each entry in `tests/golden/claimed_drift.txt`, as R8-P3 did for `wood_coil`.

## Friction

- golden-claims: cost: baseline_cost is a judged key that no may-drift entry can excuse, and a name cannot be both claimed and may-drift. Moving every plan fixture's reference therefore suspends 19 standing may-drift entries by hand, and their restore depends on whoever stamps reading a comment.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
