R10-SAV-COMFORT part 3: the month row settles the plan's stored heat and publishes the comfort shortfall beside the saving (carries 0 and 6, under the owner's ruling on carry 7).

Part of #2492. Part of #201. Critical path: R10-SAV-COMFORT. #2492 stays open: the summer start-bound limit and carry 5 are routed back to it.

## Re-cut

Fourth round (`fixer.md`, "Past three rounds"): this body replaces the earlier ones. Round history is deleted. Only figures re-taken in this pass remain; the production-call table of the earlier bodies is dropped, and `tests / fast (3.14)` is the authority for it at the final head.

**The ruling applied.** tvofi's mandated orchestrator ruling of 2026-11-04 on carry 7: the month row settles stored heat, the thermostat stays start-independent, and the comfort-matched null is reported beside the saving. Each plan step carries four settlement readings, `ledger.SETTLEMENT_KEYS` (`baseline_kw`, `stored_kw_th`, `comfort_kw`, `steady_cop`), from `optimizer._settlement_schedule` through `get_current_action` (`_settlement_at`) into the coordinator's pending snapshot, which `MonthlyLedger.observe_spot_and_settle_savings` books:

- `stored_kw_th`: the house store's change over the step (`_stored_thermal_energy` at the plan's boundary states), booked as kWh_th on `savings_stored`. `savings_months` converts the month's total once, at the month's mean steady COP, and prices it once, at the row's metered kWh price (`stored_heat_sek`).
- `comfort_kw`: the steady thermostat's heat demand at the step's comfort target less at the room the plan delivered (the slab-fed zone, at the step's midpoint), each floored at zero, at the step's steady COP. Published as `comfort_sek` beside `savings_sek`, not netted out of it.

**Three shapes tried** (figures from `dev/audit/harnesses/r10_sav_null_settled.py`): stored heat at the settlement caps and each step's COP lost because a cap that moves between re-plans breaks the telescope (varying arm -4.50 %); uncapped at each step's COP lost because it cancels the COP-timing saving (varying arm +0.01 %); uncapped at one COP and one price per row won (below).

**Payments (no budget raised).** The schedule is a module-level pure function; `ledger.settle_interval_savings` is folded into its one caller; the pending snapshot copies `SETTLEMENT_KEYS` in one spread; `_settlement_at` replaces `get_current_action`'s baseline branch. `tests/structure_budgets.json` is byte-identical to main's.

**This repair (blocked head `c383169a5`, `ci-red`).** `prelude` outlived its 8700 s cap because `tests / mutation-pins` shards ran the whole closure once per surviving site. The sites are killed by checks, not triaged:
- `tests/features.py` drives `_settlement_schedule` directly on controlled trajectories with a stored-heat function weighting every state field differently, for two-zone and single-zone houses and buffer lengths absent, valid, exactly `n_steps` and shorter. A mutant that crashes fails a named check (the call is wrapped).
- The COP floor `if cop < 1e-3: cop = 1e-3` and the comfort clamps `d if d > 0.0 else 0.0` become `max(...)`: the `<`/`>` to `<=`/`>=` mutants on those lines were equivalent (at equality the assignment is a no-op), so no check could kill them and a triage verdict would have papered over a killable shape.
- The ledger's `max(float(steady_cop), 1e-3)` is pinned by a zero-COP step.
- Carried defects of `verdict/3195` taken in lines already touched: the dead duplicate `before = after` is deleted; the `_settlement_schedule` docstring cites `_floor_demand_terms`, the function it calls; `payload.py`'s comment cites `OptimizationResult.settlement_schedule`, the field that exists.

## Head

`e0018143649336998518d267f49d66ea9a073b0a`: the handoff of `c383169a5` with the repair commit, merged with `origin/main` `499162c89d0f4f8369e16e6e41fb3a620bc1ecb0` (2026-11-05T01:48Z; merge, not a re-cut, no conflict). `tests/structure_budgets.json` and both claim files are byte-identical to `origin/main`: `git diff $(git merge-base origin/main HEAD)...HEAD --stat -- tests/structure_budgets.json tests/golden` prints nothing.

## Mutation proof

Mutant: in `MonthlyLedger.savings_months`, `baseline_sek = self.line(key, "savings_baseline")["sek"] * scale + stored_sek` becomes `... * scale`, at the head above.
- `python3 tests/features.py` prints `1 of 4810 FEATURE CHECKS FAILED`; the FAIL is `R10-SAV-COMFORT: the month row settles the plan's stored-heat change at the row's metered kWh price`.
- `python3 dev/audit/harnesses/r10_sav_null_settled.py const` prints `const: DEFECT`, rc=1.
- Restored: `ALL 4810 FEATURE CHECKS PASSED`.

Mutants of the 11 sites `ci_predict.py` lists for this diff, each applied by `sed` to `optimizer.py` or `ledger.py` and run against the new checks' statements (extracted unchanged from `tests/features.py`; the mutant column is the number of FAIL lines printed; the unmutated tree prints 0):

| site (line at the head) | mutant | FAIL lines |
|---|---|---|
| `optimizer.py:454` BOOLOP | `and len` to `or len` | 8 |
| `optimizer.py:454` CMP_BOUND | `>` to `>=` | 2 |
| `optimizer.py:485` GUARD_OFF | `if False:` / `if True:` | 4 / 6 |
| `optimizer.py:488` GUARD_OFF | `if False:` / `if True:` | 2 / 8 |
| `optimizer.py:493` CLAMP_DROP | `max(...)` dropped / floor set to -1e9 | 1 / 1 |
| `optimizer.py:497` GUARD_OFF | `if False:` / `if True:` | 4 / 6 |
| `optimizer.py:500` GUARD_OFF | `if False:` / `if True:` | 2 / 8 |
| `optimizer.py:512` CLAMP_DROP*2 | first / second `max` dropped, both floors to -1.0 | 1 / 1 / 1 |
| `optimizer.py:515` CMP_BOUND | `<` to `<=` | 10 |
| `optimizer.py:515` GUARD_OFF | `if False:` / `if True:` | 1 / 10 |
| `ledger.py:309` CLAMP_DROP | `float(steady_cop)` unfloored | the zero-COP step raises `ZeroDivisionError` where the check expects `-2000.0` |

## Null control

- The block above printed `failures 0` on the unmutated tree; the equivalent mutants (`cop <= 1e-3`, `d_t >= 0.0`, `d_d >= 0.0`) are the control that decided the `max` rewrite: `sed` of `cop < 1e-3` to `cop <= 1e-3` on the old line printed 0 FAIL lines, i.e. no check can tell them apart.
- `dev/audit/harnesses/r10_sav_null_settled.py` without the new readings: vary 12.34 %, const 11.86 %.
- `tests/features.py`: `R10-SAV-COMFORT null control: an interval without either reading settles nothing`.

## Figures

- `PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_sav_null_settled.py` (sha1 `eca29a18ee192f0d3727e447e1f981326fe5b9c0`) at the head, rc=0: vary saved 32.16 (19.23 %), `stored_heat_sek` 13.15, `comfort_sek` 8.28, comfort-matched 23.88 (+14.28 %), SOUND. const saved 6.62 (4.77 %), `stored_heat_sek` -11.15, `comfort_sek` 6.23, comfort-matched 0.39 (+0.28 %), SOUND. Rule: const `|pct| < 3.0`, vary `pct >= 3.0`.
- `python3 dev/audit/harnesses/r10_sav_baseline.py transient` (sha1 `bc31f356191ededbfb0b15f768b258249867b134`): spread 0.00 kW, SOUND.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>` prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` Every script `scope.run` names except `tests/stress.py` and the `.mjs` ones ran with `PYTHONPATH=tests/hastub`, rc=0 each: `arch_score_head`, `backtest`, `block_duty`, `boost_drift_replay`, `config_flow_steps`, `debug_collect`, `deployment_shape`, `doc_claims`, `edge`, `entities`, `env_drift`, `features`, `finite_boundary`, `golden`, `guard_pins`, `harness_headers`, `manual_plan`, `optimality`, `plan_view`, `solar_alignment`, `structure`, `typing_ruler`, `validate`, `wood_advisor`. `python3 tests/stress.py` printed `ALL 113 STRESS CHECKS PASSED`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Class seams: `git grep -n "_settlement_schedule" -- custom_components` returns the definition and its one caller; `git grep -n SETTLEMENT_KEYS -- custom_components` returns the coordinator's pending snapshot and the ledger.

## Unpinned sites

`python3 tools/pr/ci_predict.py` at the head lists 11 sites, all under `custom_components/`, the directory `mutation-autofix` mutates. Each is killed by the check named in `## Mutation proof`, so each is pinned by `mutation-autofix` when its lane drives it, and none is claimed pinned by this seat before the lane has run. No site is waiting on a triage verdict.

- `custom_components/heatpump_optimizer/ledger.py:309 CLAMP_DROP` (`max(float(steady_cop), 1e-3)`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:454 BOOLOP` (`buffer_temps is not None and len(buffer_temps) > h.n_steps`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:454 CMP_BOUND` (same line): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:485 GUARD_OFF` (`if two_zone:`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:488 GUARD_OFF` (`if bufs is not None:`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:493 CLAMP_DROP` (`max(compute_cop(...), 1e-3)`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:497 GUARD_OFF` (`if two_zone:`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:500 GUARD_OFF` (`if bufs is not None:`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:512 CLAMP_DROP*2` (`max(d_t, 0.0) - max(d_d, 0.0)`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:515 CMP_BOUND` (`if i < n_base:`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`
- `custom_components/heatpump_optimizer/optimizer.py:515 GUARD_OFF` (`if i < n_base:`): killing check in `tests/features.py` (see `## Mutation proof`); pinned by `mutation-autofix`

## Red checks

Concluded reds of the blocked head `c383169a5` (the check-run set of `tests`, `governance` and `prelude`, read in full by the reviewer in `probe/rev-3195-50e00e14` `ev/check_runs_final.tsv`, 54 rows). The final head above has had no CI yet: moving the head is what starts it, so none of these is claimed cured by a run.
- `prelude`: `still adding sources after 8700 s`; `tests / mutation-pins (1)` outlived it, and shards 2 and 3 ran 2 h 20 min and 1 h 37 min because 8 added sites survived and each ran the whole closure. Branch-caused. Cheaper detector: `python3 tools/pr/ci_predict.py`, about one pass (`prepr.sh` step 6d), which listed the sites before the push; it reads them as a warning, not a refusal, and a survivor is invisible to it until a mutant is run. Standing cost: that pass per `prepr.sh`; the countermeasure of running the sites' mutants is a seat's choice. Mutants of every listed site are run in `## Mutation proof`.
- `gate`: red only because `prelude` was (`FAIL prelude: failure`). Same answer.
- `pr-contract / pr-contract`: refused the body because `prelude` was red and `## Red checks` did not name it. Cured by this section; cheaper detector `tools/pr/prepr.sh --body-check`, which cannot see a check not yet red when the body is written.
- `tests / mutation`: the unpinned-site refusal; answered under `## Unpinned sites`.
- `tests / fast (3.14)` (ancestor head `212bef640`): `tests/stress.py`'s production-call check read the schedule's per-step work as growth. Branch-caused; repaired by reading each series once, reusing one `ThermalState` and building the weather-only demand terms once per step (`_floor_demand_terms`). Cheaper detector: `python3 tests/stress.py`, which printed `ALL 113 STRESS CHECKS PASSED` at the head above (`## Figures`); it is outside `prepr.sh` and costs a few minutes, owed on any diff adding per-step work in `optimizer.py`. Green at `c383169a5`.
- `tests / typing` (ancestor head `6f742a33e`): 9 `no-untyped-call` errors from an untyped lambda in `_settlement_schedule`; repaired by `def _l(x: Any) -> list[Any]` with no new `# type: ignore`; `python3 tests/typing_ruler.py --mypy` prints `ALL 9 typing-ruler checks PASSED`. Cheaper detector: that command (pinned venv, about one minute); `prepr.sh` does not run it. Green at `c383169a5`.
- `tests / mutation-autofix`: the lane that pins the sites under `## Unpinned sites`; it pins killed mutants only, so a survivor leaves it red. The answer is the kills in `## Mutation proof`; cheaper detector as for `prelude`.
- `tests / replay` (ancestor heads): `synthetic-dhw-only.json` `cpu_ratio` over budget on the baseline tree as well, so not branch-caused; owed a re-centre by the budget's owner. No cheaper detector exists for a CPU-time ratio on a shared runner. Green at `c383169a5`.
- `tests / nightly-status`: grades `main`, inherited (red on `origin/main`); this diff touches none of its scripts or workflows. Owed by the nightly's owner.

## Forward-carry

- The summer start-bound limit: `optimizer._start_gap_cost` caps the start-of-horizon settlement at the thermostat's space-heat cost, leaving `summer_dhw_only`'s predicted savings negative. Carry: #2492
- Carry 5: reconcile `power_ratio` and the planner's over-booking on one sample window (`dev/audit/harnesses/r10_demand_overbook.py`). Carry: #2492
- Verdict/3195's remaining test gaps outside the lines this repair touches (M13 `baseline_kw` end to end through `get_current_action`, M3 midpoint rule, M9/M10 calibrated-month scaling): not taken here. Carry: #2492

## Friction

none
