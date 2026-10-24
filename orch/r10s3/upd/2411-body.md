R10-SAV-BASELINE. Closes #2255, the owner's savings items 1, 2 and 5 (tvofi, 2026-10-14): September at 81 % saved against a plain thermostat, an October estimate with a baseline below the actual, and a receipt total that disagreed with the month table's Actual.

**Item 1, the baseline.** The settlement books `baseline_power_schedule[i]` from the plan that covers each interval. That figure was the thermostat's first step, and the thermostat started from the plan's measured house, so it booked the recovery transient: the clip (6.00 kW) whenever the optimiser had left the house below target, and 0.00 kW at or above it. `_compute_baseline_power` now starts from `_thermostat_held_state`, with the zones at the step's comfort target and the slab at the temperature that delivers that demand. The booked step is then the steady holding power, whatever the plan did before.

Starting the reference held while the plan starts measured leaves the two with different stored heat at the start, as they already differ at the end. `_start_gap_cost` settles the start gap the way `_deferred_energy_cost` settles the end gap, and the caller nets it off. A pre-heated start is debited past the end's comfort caps, because the plan coasts on that heat. The debit is capped at the thermostat's space-heat cost over the horizon (on the hot-water path, the space reference's share of `baseline_cost`), because stored house heat can only displace space-heat purchases that exist.

**Item 2, the open month.** It was scaled by the calendar day (`days / day-of-month`). It now scales by the month's hours over the hours it settled (`settled_hours`, a ledger meta folded on every settlement with a positive length, priced or not). The capacity line is a whole-month figure (the running billed peak) and is not extrapolated.

**Item 5, one cost source.** The row's `actual_sek` is `MonthlyLedger.month_cost`, the same `billed_total` over the same lines the receipt adds. `savings_sek` is thermostat less plan over the covered intervals, both priced at spot plus the interval's grid fee. `baseline_sek` is the bill plus that saving. `_contract_comparison` reads the ledger's `metered_energy`.

**What R10-SCORES and R10-ADVISOR read after this.** For each `savings_months` row:
- `actual_sek` is the month's bill (the receipt total).
- `savings_sek` is thermostat minus plan over intervals a plan covered, at spot plus the grid fee.
- `baseline_sek` is `actual_sek + savings_sek`.
- The open row is scaled by the month's hours over its settled hours; capacity is not scaled.

`deferred_energy_cost` is the end gap less the start gap.

**This round.** The required `mutation` check refused two sites this diff adds. The previous body had triaged both as equivalent, but neither is:
- `ledger.py:186` CMP_BOUND (`dt >= 0`) is observable. A zero-length interval would persist a `settled_hours` sample (`{'sum': 0.0, 'count': 1}`) in the payload the ledger store saves (`as_dict`). It is now killed by a value check in the #2255 section of `tests/features.py`, "an interval of no length settles no hours: the stored coverage takes no sample". It is pinned to `tests/features.py`.
- `optimizer.py:324` BOOLOP is killed by `tests/typing_ruler.py`'s pinned mypy census, the same way main's identical assert in `_compute_baseline_power` is pinned (`HeatPumpOptimizer._compute_baseline_power.BOOLOP.7ac89f81`).

The CI pin shard recorded `ledger.py:186` as killed by `tests/entities.py`. That kill is vacuous, so it is not recorded; see `## Mutation proof`.

**The flat-price null does not read about 0, and this pull request does not redefine the baseline to make it.** On a flat price with the plant equal to the model, the month row reads 12.34 % saved at the head and 43.76 % at the merge base. Booked thermostat energy is 201.0 kWh at the base and 128.4 kWh at the head, against the plan's 112.6 kWh. The remaining 15.8 kWh gap has three terms, measured by `dev/audit/harnesses/r10_sav_null_terms.py`:
- (a) Comfort: 6.9 kWh. That is a steady thermostat at the target (128.4 kWh) less one at the room the plan delivered (121.5 kWh). The plan holds a mean 18.72 °C against a 20.44 °C target.
- (b) COP timing: the plan's power-weighted COP is 17.29 % above the thermostat's, over an outdoor range of -16 to -8 °C. That is a real saving at a flat price.
- (c) Unsettled stored heat: the plan ends holding 20.1 kWh_th more than it started (room/slab 21.00/22.00 → 19.27/29.48), about 11.3 kWh_e at the steady COP. The month row does not settle it.
- The control is the `const` arm, with outdoor held at the window's mean. Timing reads +0.00 %, comfort 5.2 kWh, and the start drawdown is 9.3 kWh_e. The plan's thermal balance closes in both arms (236.0 vs 235.9 and 202.3 vs 202.2 kWh_th).

**A known limit of the start bound.** `summer_dhw_only`'s predicted saving is -0.0206 SEK at the merge base and -0.2668 SEK at the head, on a reference of 0.6478 → 2.0939 SEK. The summer house starts above the end's comfort caps, and the thermostat's space-heat cost still exceeds the surplus. Carried with the null's terms below.

## Head

fe4e0a3b02049e1bb971f9c7808f58f531cce08f

The merge base is 07a09406a (origin/main at 2026-10-18T20:09Z). This head merges the PR branch's `ci: merge main` (339d4bce6) and, before that, origin/main at 106af95a3. Main's production changes in those merges (none up to 106af95a3; then #2379's `climate.py`, `entity.py` and `sensor.py`, and none from #2401) touch none of `optimizer.py`, `ledger.py`, `thermal_model.py` or `coordinator.py`. The new code commit is 90c104c5d (the value check and the two pins). Every figure below was taken in this pass at fe4e0a3b0, except where a line names another tree.

## Mutation proof

`dev/audit/harnesses/r10_sav_baseline_mutants.py .` on a scratch checkout of fe4e0a3b0. It applies each mutant, runs the #2255 checks (the `3L-G7` savings section of `tests/features.py`, 34 checks), and restores the file. Every mutant replaces a predicate of the fix. M0 (unmutated) has 0 failing, and all 16 mutants are killed:
- M1, the thermostat starts from the plan's state: 6 failing.
  - The booked step is not independent of the start state: single-zone `[0.0, 6.0, 6.0, 0.0]`, and two-zone with DHW.
  - The booked step is not the steady holding power: 0.0 vs 2.06 kW.
  - The held house is not a steady state of the plant model.
  - The predicted saving moves more with the start state than the plan's cost does: single-zone, and two-zone with DHW.
- M2, the held slab without its demand term: 5 failing.
  - Both independence checks: `[6.0, 6.0, 6.0, 6.0]`.
  - The steady holding power.
  - The steady state.
  - "a start colder than the held house is settled at the caps, with no surplus to debit".
- M3, the row's actual from `savings_actual`: 5.
- M4, the coverage factor back to the calendar day: 3.
- M5, the saving priced at spot alone: 1.
- M6, capacity extrapolated: 2.
- M7, metered energy without immersion: 1.
- M8, settled hours never folded: 3.
- M9, no start settlement on the space path: 1.
- M10, the start debit unbounded: 3.
- M11, the start settled at the caps only: 2.
- M12, the hot-water path bounds the start by `baseline_cost`: 1.
- M13, the coverage factor without its floor of 1: 1.
- M14, a negative thermostat cost unclamped: 1.
- M15, the start surplus unclamped: 1.
- M16, the held slab allowed below target: 1.

The two sites this round pins, each with its mutant and an equivalent rewrite of the same line as the null control. Both were run at fe4e0a3b0 on the scratch checkout and restored:
- `ledger.py:186`, `if dt > 0:`.
  - Mutant `if dt >= 0:`: the section reads `1 of 34 2255 FAILED`, namely "an interval of no length settles no hours: the stored coverage takes no sample" (`{'settled_hours': {'sum': 0.0, 'count': 1}, ...}`).
  - Null `if 0 < dt:`: `ALL 34 2255 PASSED`.
  - `mutation_table.py --pin-killed --scripts tests/features.py` recorded the pin: "took tests/features.py from rc=0 failed=0 to rc=1 failed=2".
- `optimizer.py:324`, the `and` assert.
  - Mutant `or`: `tests/typing_ruler.py` (under `HPO_TYPING_PYTHON`) reads `FAIL errors did not grow [recorded 0, measured 2 (+2)]` and `FAIL by_code[index] did not grow`.
  - Null, the same `and` with the operands swapped: `the pinned census passed`.
  - `--pin-killed --scripts tests/typing_ruler.py` recorded the pin.

The kill that is not recorded: under `if dt >= 0:`, `tests/entities.py` fails exactly one check, "--anchor re-drives one site ... (R9-F10.13)". Its message is `MUTATION TABLE REFUSED -- the ledger disagrees with the deterministic inventory`. That self-test runs `mutation_table.main` against the live tree, so any edit to a line that already carries a pin (here `observe_spot_and_settle_savings.GUARD_OFF.f0f29f9a`) trips it. The equivalent rewrite `if 0 < dt:` fails the same single check (`1 of 2347 ENTITY CHECKS FAILED`, the same check name). It is carried below.

## Null control

`dev/audit/harnesses/r10_sav_baseline.py` was run at fe4e0a3b0 and at the merge base 07a09406a (the head's harness file run against the base tree). It has four arms. The base reads `defect 4`; the head reads `defect 1: null`.
- transient: the booked first step across four start states. Base 0.00, 6.00, 6.00, 0.00 kW (spread 6.00). Head 2.06 kW for all four (spread 0.00).
- cost: the receipt total is 15.0 SEK. The row's actual is 3.0 at the base and 15.0 at the head.
- coverage: 24 settled hours of 672. The open-row scale is 2.80 at the base and 28.00 at the head.
- null (flat price, plant equal to the model, 2 days, re-planned hourly): 43.76 % saved at the base (thermostat 201.0 kWh, plan 113.0 kWh) and 12.34 % at the head (thermostat 128.4 kWh, plan 112.6 kWh). It reads `DEFECT` at both ends against its 3 % threshold. The residual is the three terms above.

For the new check, the null control is the equivalent rewrite above: it passes the check, so the check reads the zero-length sample and not the line's text.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline.py`: every arm figure in `## Null control`, at fe4e0a3b0 and at 07a09406a.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_terms.py`, and the same with `const`: the null's three terms and the control in the description.
- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_baseline_mutants.py .`: M0 to M16, with the failing counts as printed.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/entities.py,tests/typing_ruler.py`, under `env -u BASH_ENV`, at 1bbe062e2 (production identical to the head's for both files). It printed `pinned optimizer.py:324 BOOLOP -- killed by tests/typing_ruler.py` and `pinned ledger.py:186 CMP_BOUND -- killed by tests/entities.py`. The latter is the vacuous kill, and its file was deleted. A first run without `env -u BASH_ENV` read the entities.py baseline `rc=1 failed=1`, and its verdicts were discarded.
- `python3 tests/mutation_table.py --pin-killed --base origin/main --scripts tests/features.py`, with the check in the working tree. It printed `baseline tests/features.py: rc=0 failed=0`, `pinned ledger.py:186 CMP_BOUND -- killed by tests/features.py` and `UNPINNED optimizer.py:422 CLAMP_DROP -- lives` (see `## Unpinned sites`).
- `python3 tests/mutation_table.py --scope changed --base origin/main --max 0`: `4211 unpinned site(s) of 6083 candidate sites, 4217 at the ratchet base 07a09406a...; the ledger agrees with the deterministic inventory`, with no `ADDED UNPINNED` line. The `--max 10` drive is CI's.
- `GOLDEN_MODE=drift GOLDEN_REF=07a09406a1cc97076a6f28581f87f313b322a6b6 PYTHONPATH=tests/hastub python3 tests/golden.py`:
  - `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 07a09406a...` and `NO STALE FIXTURE: 56 committed fixture(s)`.
  - 50 `baseline_cost:` drift lines, one per claimed fixture, with the direction per fixture in `tests/golden/claimed_drift.txt`.
  - `summer_dhw_only`'s figures are from this run.
- `PYTHONPATH=tests/hastub python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` against 07a09406a. No budget file is touched in this round.
- `python3 tools/audit/archscore/score.py --diff 07a09406a1cc97076a6f28581f87f313b322a6b6`: `Architecture score: dS +0.0006 IMPROVES` (coord_footprint 2499 → 2498).
- `python3 tests/closure.py select --diff 07a09406a1cc97076a6f28581f87f313b322a6b6 --workdir <dir>`: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`
  - The scripts run green locally at fe4e0a3b0 under `env -u BASH_ENV PYTHONPATH=tests/hastub`: `features` (`ALL 4198`), `entities` (`ALL 2349`), `backtest`, `edge`, `validate`, `block_duty`, `manual_plan`, `plan_view`, `solar_alignment`, `wood_advisor`, `finite_boundary`, `guard_pins`, `boost_drift_replay`, `typing_ruler` (with the pinned census), `doc_claims`, `deployment_shape`, `config_flow_steps`, `debug_collect`, `arch_score_head`, `harness_headers`, `structure`, and `golden` and `env_drift` through the drift run.
  - Left to CI: `stress`, `optimality`, `card.mjs` and `card_drift.mjs`.
- `python3 tests/closure.py no-copies`: `no test file defines a symbol production also defines`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused, 0 stale allow entries`.
- `git diff --quiet 07a09406a HEAD -- VERSION tests/golden/card_claimed_drift.txt custom_components/heatpump_optimizer/manifest.json && echo identical` prints `identical`. `RELEASE_NOTES.md` has no diff.

Seams of the class, enumerated by `grep -rn "savings_months(\|month_cost(\|\"savings_actual\"\|_compute_baseline_power(\|metered_energy(\|freeze_month_report(" custom_components/heatpump_optimizer/*.py | grep -v "def "`. It returns 8 sites, each dispositioned:
- `coordinator.py` `"savings_months": self._ledger.savings_months(...)`: the published rows. Closed in this diff.
- `coordinator.py` `self._ledger.metered_energy(month)` in `_contract_comparison`: closed in this diff.
- `coordinator.py` `freeze_month_report(`: the receipt. It is unchanged and now the same total as the row.
- `ledger.py` `"savings_actual"` (the settlement's write) and `self.line(key, "savings_actual")` (in `savings_months`): now only the plan side of the saving, priced like the baseline side. Closed in this diff.
- `ledger.py` `actual_sek = self.month_cost(key)`: the row's actual. Closed in this diff.
- `optimizer.py`, two `self._compute_baseline_power(` calls (the space and hot-water paths): the one thermostat reference for the ledger's booked step and the plan's `baseline_cost`. Closed in this diff. `tests/backtest.py`'s replay calls the same function and is green.

## Unpinned sites

The table's added-site rule (`added_unpinned`: identity is file, operator and stripped text) lists none at this head. Two sites were refused at 74d66b355 and 339d4bce6, and the pin drive names a third:
- `ledger.py:186` CMP_BOUND: killed by the new value check, and pinned to `tests/features.py` in 90c104c5d.
- `optimizer.py:324` BOOLOP: killed by the pinned typing census, and pinned to `tests/typing_ruler.py` in 90c104c5d.
- `optimizer.py:422` CLAMP_DROP (`max(0.0, q_lower)` in `_thermostat_demand_two_zone`'s slab target): the base's unpinned stock. The same line was in `HeatPumpOptimizer._compute_baseline_power` at the base, and the refactor moved it within `optimizer.py`, so `added_unpinned` matches it to the base. The pin drive lists it because it drives every site in a new def, and no driver kills it. Not owed by this diff, and not triaged here.

The earlier rounds' sites (those `ci_predict` listed, pinned by `mutation-autofix` at 36723a969 and 74d66b355) are in `tests/mutation_ledger/killed_by/`. The ledger agrees with the inventory (`--max 0` above).

## Red checks

Every failed check run on this branch's pushed commits, each with its answer:
- `mutation` at 62f3704f7, b7a34f98a, 36723a969 and 74d66b355 (117738322488, 117738310043), and at 339d4bce6 (117766076509, 117766063855): `MUTATION TABLE REFUSED`. At 74d66b355 and 339d4bce6 the refused sites are `ledger.py:186 CMP_BOUND` and `optimizer.py:324 BOOLOP`.
  - This diff caused it. 90c104c5d answers it with a real kill for each site.
  - `mutation-autofix` at 74d66b355 read `AUTOFIX: skip-not-allowed`: the loop guard, since the head subject was `ci: pin killed mutants`. So no bot commit was coming.
  - The cheaper detector exists: `mutation_table.py --scope changed --max 0` takes seconds locally, and `prepr.sh` step 6d lists the same sites. Its standing cost is those seconds. The earlier rounds ran it and triaged the two sites in the body instead of recording a disposition.
- `fast (3.14)` at b7a34f98a (117692786859) and at 36723a969 (117704407882, 117704447188): `tests/optimality.py`, `one|summer_negative|shoulder: no unclaimed gap above the bar`. This diff caused it, when round 1 retired that cert claim on the arm64 figure. eeb607dd6 answers it by keeping the claim, and this head carries that.
- `pr-contract` (117692504964, 117692618046, 117704466268): `'Closes #2255' ... not in the intended list`. The orchestrator answers it on the roster (`fixes`).
- `nightly-ha (stable)` at 36723a969 (117704407933) and at 74d66b355 (117738343906): `FAILED: 2 of 64 checks: ['hb:positive_control', 'run:exit_status']`. Not this diff's.
  - The heartbeat's positive control spins the loop 600 ms in `tests/nightly_ha.py`'s own `_hb_spin`, and reads it as 600.3 ms. The loop's own dump names the spin (`dump names the spin: True`).
  - Only the py-spy leg failed: `py-spy did not run: TimeoutExpired: Command '['/opt/hpo/py-spy', 'dump', '--nonblocking', '--pid', '1']' timed out after 30 seconds`. `run:exit_status` is that failure's container exit.
  - The other 62 checks passed, among them the entity, payload, plan, reload and blocking-call arms.
  - This diff touches neither `tests/nightly_ha.py`, the workflow, nor `tests/requirements-nightly-ha.txt`.
  - At 339d4bce6, `nightly-ha (stable)` passed (117766102891) on the same production diff.
  - A root-cause seat is analysing the recurring py-spy timeout separately, so no detector is proposed here.
- `wave-script` at 339d4bce6 (117766080121): `AGREEMENT REFUSED`, `merge-subject-pr` divergent on `"Merge pull request #2401 (R10-ARCHSCORE-COVERAGE p5)"` and `"Merge pull request #2379 (R10-SENSOR-PAYLOAD)"`. Not this diff's.
  - Both subjects are main's merge commits, brought in by `ci: merge main`.
  - Main's own Governance runs at 07a09406a (39158144006) and 5756f2b15 (39156632953) are red.
  - This diff touches no governance reader. No fix to port exists yet.
- `delivery-status` at 339d4bce6 (117766080081): `DELIVERY STATUS OVERDUE`, with the overdue rows #2413, #2412 and #2407. It is not required, it grades main, and this diff adds no row it reads beyond its own `dev/programme/delivery/2411.md`. No answer is owed.

## Forward-carry

The carries are roster carries the orchestrator appends (`roster_edit append-carry`); the texts are in the seat's report.
- The mutation instrument's owner (the lane holding `tests/mutation_table.py` and `tests/entities.py`'s R9-F10.13 block): `tests/entities.py`'s `--anchor` self-test runs `mutation_table.main` against the live tree, and `clone_tree` overlays the working tree. So under `--pin-killed`, entities.py "kills" every mutant of a line that already carries a pin, by refusing the ledger/inventory disagreement.
  - Control: the equivalent rewrite `if 0 < dt:` of `ledger.py:186` fails the same single check.
  - Re-measure: at a later head, mutate any pinned line equivalently, and run `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`.
  - Until it is fixed, a `killed_by: tests/entities.py` pin on a line with a second pin is unproven. The ledger holds 123 `killed_by: tests/entities.py` pins in all, by `grep -rl '"killed_by": "tests/entities.py"' tests/mutation_ledger/killed_by | wc -l`. How many of them sit on a line with a second pin, or are vacuous, is not measured.
- The month row's flat-price null, its three terms, and the `summer_dhw_only` start-bound limit go to the group the orchestrator adds for the comfort-matched baseline. R10-ADVISOR's seam does not own `_compute_baseline_power` or `ledger.py`.
- R10-ADVISOR: its carried null ("savings about 0 on a flat-price profile"), restated so its acceptance separates comfort, COP timing and stored heat. The `const` arm of `r10_sav_null_terms.py` is the control.
- R10-SCORES and R10-ADVISOR: the row semantics in "What R10-SCORES and R10-ADVISOR read after this".
- The stamp (`tools/release/stamp.py` / web-stamp): restore the 19 suspended may-drift entries verbatim when the stamp empties the claim list. The obligation is written beside each entry in `tests/golden/claimed_drift.txt`.

## Friction

- golden-claims: cost: `baseline_cost` is a judged key that no may-drift entry can excuse, and a name cannot be both claimed and may-drift. Moving every plan fixture's reference therefore suspends 19 standing may-drift entries by hand, and their restore depends on whoever stamps reading a comment.
- ci-autofix: unenforced: the CI pin chain (`mutation-pins`) recorded `ledger.py:186` as "killed by tests/entities.py" (job 117738525584), on a kill an equivalent rewrite reproduces. Nothing in the pin rule asks for a null mutant per pin, so a vacuous kill becomes a pin with no human step.

🤖 Generated with [Claude Code](https://claude.com/claude-code) -- https://claude.ai/code/session_01WG9SNvz6cvkANRVzrLnJKF
