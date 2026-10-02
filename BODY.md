_Requested by **tvofi**_

Closes #1743 (R9-EG-B5). The nineteen DHW planner-core methods of `HeatPumpOptimizer` move into `DhwPlanner` in the new `custom_components/heatpump_optimizer/dhw_planner.py`. The module-level names only they use move with them: `DhwPlan`, `_DhwLegionellaPlan`, `_dhw_windows_at`, `_DHW_REFILL_WINDOW_HOURS` and `_DHW_MIN_RUN_CHUNK`. The shared helpers move without an import cycle: `_step_humidity` and `_mean_humidity` go to `thermal_model.py`, and `_pin_is_free` goes to `manual_plan.py`.

tvofi granted this group a `cap_exception` on 2026-10-02 (roster commit 6ddb9225 on handoff/audit-r9-fixplan): one PR for the whole extraction, on three conditions. The roster's `cap_exception` text sizes it at about 1,915 production lines. Every moved line is byte-identical to its source. Only call sites, imports and the build's return shape change. No behaviour changes. `tools/audit/round9/EG-B5/provenance.py` checks the first two, and a reviewer can re-run it. The third is checked by `tests/env_drift.py --all` and by a fingerprint of every golden scenario.

**What changed besides the move:**
- `optimize` builds one planner per solve, right after `_stash_price_horizon`, from explicit inputs: `DhwPlanner(self.model, self.config, self._pv_surplus, self._price_known)`. It passes the planner to `_optimize_with_dhw` and then to `_co_optimize`, which stay on the optimizer as orchestration. Nothing stores the planner.
- **One deviation from the design note.** The note says the planner takes "the PV export price". It takes `config` instead, typed by a one-field Protocol `_PlannerConfig(pv_export_price)`. Passing the float would have rewritten the moved line `self.config.pv_export_price` in `_dhw_planning_prices`, and the verbatim condition rules that out. The planner still reads exactly one config field.
- `_build_dhw_requirements` returns `(plan, requirement)`. It no longer writes `self._dhw_requirement` and `self._dhw_legionella_step`; those are the build's only three changed lines, all listed in the provenance table. The optimizer still holds `_dhw_requirement` and assigns it from each build's return value at the point the stash used to be written, so the last build of a solve still wins. `_dhw_legionella_step` is deleted, because no production code read it.
- The horizon parameter of `_dhw_coil_wood_forecast` is typed by a read-only Protocol named `_Horizon`, defined in `dhw_planner.py` with the 11 fields that method reads. Keeping the name keeps the annotation line verbatim. A `TYPE_CHECKING` import of `optimizer._Horizon` was not used: it would add an equivalent guard, which the mutation count ratchet refuses.
- The co-optimisation replan keeps `blocked=h.dhw_blocked` (#1747).

**Tests.**
- Direct calls in `tests/features.py` now go through a factory, `_dhw_planner(opt)`, which builds the planner the optimizer's solve would from its current inputs. That covers 44 retargeted calls.
- Class-level spies and patches retarget to `DhwPlanner`. `_LgOpt` keeps its optimizer alias, because `_lg_e2e` constructs optimizers, and a second alias `_LgPlanner` carries the floor-repair patches.
- The four `_dhw_legionella_step` reads now read the last build's `plan.legionella_step` through a spy. It is installed around the v5.1.10 legionella sections and removed after them.
- Every direct build unpacks `(plan, requirement)`. `DhwPlan` and `_DHW_MIN_RUN_CHUNK` are now imported from `dhw_planner`, and the two humidity helpers from `thermal_model`.
- `_P3_FILES` gains `dhw_planner.py`, and the seam-rule check's name now says so.
- `tests/guard_pins.py` calls `_dhw_legionella_ceilings` on a `DhwPlanner`.

**Ledger.** Ten mutation-ledger rows are re-keyed by path, scope and directory, with digests unchanged. The design counted nine; `DhwPlanner._dhw_window_floors CLAMP_DROP 84bf5434` is a row added since. The survivor-triage row `_repair_dhw_floor CLAMP_DROP 21bb873a` is carried as it was.

**Structure.** Per-class logical statements (`ast.stmt` nodes below the class), from `tools/audit/round9/EG-B5/class_stmts.py 948671af1 HEAD`:
- `HeatPumpOptimizer`: 1511 → 1001 (71 → 52 methods).
- `DhwPlanner`: 514 (20 methods).

Every `tests/structure.py` metric is unchanged; no budget is re-recorded. `classes_over_300` was retired by #1738, so the owner gate the roster recorded for it no longer applies. The architecture-score delta is owed until R9-EG-A1 (#1851) lands `score.py --diff`. The design's pre-study already reads this extraction as delta-S about 0, because that instrument prices only the coordinator.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`cb7cd281a9dd01ee7ff58efc5bbca90baa458020`. The merge base is origin/main `948671af1dcb63b1e3ceebb0154ba5c5b9c2911e`, measured 2026-10-02T16:15Z (`date -u`).

The branch was cut at `4e2582e79a4d788fee44c8eb82502cbf46f53af7`. It merged origin/main at `d3f3640c7`, and main's delta touched no file under `custom_components/` or `tests/`. `diff <(git diff 4e2582e79 d3f3640c7^1 -- custom_components tests) <(git diff 948671af1...d3f3640c7 -- custom_components tests) && echo CODE-AND-TEST-DELTA-IDENTICAL` printed `CODE-AND-TEST-DELTA-IDENTICAL`.

The `tests/features.py` runs below were measured at `0c458974916fe80c8873e11b71abb9afef178e53`, and `env_drift.py --all` at `07ff8248e6245d4591dd349b612b6eabc3990a39`. Both trees match this head under `custom_components/` and `tests/`: `git diff --quiet 0c4589749 cb7cd281a -- custom_components tests && echo CODE-AND-TESTS-IDENTICAL` printed `CODE-AND-TESTS-IDENTICAL`, and the same for `07ff8248e`.

## Mutation proof

Failing test first. `c9c0e397735fe7a8852b00b6094008549762b3f6` adds the three `#1743` checks to `tests/features.py` with no production change. They import the production symbols: `heatpump_optimizer.dhw_planner.DhwPlanner` when it exists, and `HeatPumpOptimizer`. A `git archive` export of that commit ran `PYTHONPATH=tests/hastub python3 tests/features.py` (seat venv, CI's `tests/requirements-ci.txt`, Python 3.14.7, macOS arm64). It reported 5 of 3652 failed:
- `the DHW planner core lives on DhwPlanner, not on HeatPumpOptimizer (#1743)`
- `and no DhwPlanner method but __init__ writes an attribute`
- `a solve builds one planner and every DHW build it makes runs on it, the co-optimisation replan's among them`
- plus the two failures the base also shows (see Null control).

Two mutants of the head export, each run through the whole `tests/features.py`:
- **M1:** `_co_optimize` builds its replan on a fresh `DhwPlanner(self.model, self.config, self._pv_surplus, self._price_known)` instead of the handed-down planner. This is behaviour-identical, so only the hand-down check sees it: 3 of 3652 failed, the new one being `a solve builds one planner and every DHW build it makes runs on it, ...` with `planners built: 2; builds: 2, on 2 planner(s)`.
- **M2:** `_build_dhw_requirements` stashes `self._last_requirement = requirement`. 3 of 3652 failed, the new one being `and no DhwPlanner method but __init__ writes an attribute` with `writes: [('_build_dhw_requirements', 1138)]`.

Mutation ledger: `PYTHONPATH=tests/hastub python3 tools/audit/round9/EG-B5/ledger_check.py 948671af1dcb63b1e3ceebb0154ba5c5b9c2911e` reports:
- form and layout `[]`, completeness `[]` over 4520 sites;
- 3909 unpinned sites here and 3909 at the base;
- `added unpinned: 0`, with ratchet refusal `None`.

Its null control is the same per-site match run without #1748's move pairing (`sides` empty), which counts 147 sites as added. So the move passes the per-site ratchet only through the #1748 carry, as the design required. The diff adds no new candidate site; `mutation_table.py --scope changed` was not run locally, because its drivers solve per mutant. Pinning and the sampled survivors are left to CI's required `mutation` check.

## Null control

- **Base features run.** An export of `4e2582e79` ran `tests/features.py` in the same venv: 2 of 3649 failed, both environmental and both also failing at the head.
  - `and the path that proceeds still stamps a resolvable recorded_at (#363)` fails because a `git archive` export has no `.git`.
  - `R9-F2.1 P3: the shipped storage plan ...` fails on this Mac's BLAS, as at main.
- **Head features run.** The head export: 2 of 3652 failed, the same two. 3649 + 3 new checks = 3652.
- **env_drift.** At `07ff8248e`: `DRIFT_CACHE_DIR=<scratch> PYTHONPATH=tests/hastub:custom_components python3 tests/env_drift.py --all 4e2582e79a4d788fee44c8eb82502cbf46f53af7` exited rc=0. It reported 37 scenarios `byte-identical` and 19 may-drift scenarios `did not move here`, then `NO UNCLAIMED DRIFT: 56 scenario(s) checked` and `NO STALE FIXTURE: 56 committed fixture(s)`.
- **Golden fingerprint.** `PYTHONPATH=tests/hastub:custom_components python3 tools/audit/round9/EG-B5/golden_hashes.py` hashes 100 solves: 50 scenarios, each at its own prices and at prices − 2.0. Base and head printed identical lines: `diff base.txt head.txt && echo IDENTICAL` printed `IDENTICAL`.
  - Perturbed control: the head with `_dhw_cop_profile` pricing the tank 5 K hotter. 79 of 100 solves differ, so the fingerprint sees a planner change.
  - A second control, `_DHW_MIN_RUN_CHUNK` 8 → 16, moved 0 of 100. That constant does not reach these scenarios; `tests/features.py` kills it.
- **Goldens.** `git diff --stat $(git merge-base origin/main HEAD)...HEAD -- tests/golden/` is empty, so nothing is claimed.

## Figures

- **Provenance.** `python3 tools/audit/round9/EG-B5/provenance.py 948671af1dcb63b1e3ceebb0154ba5c5b9c2911e HEAD` exited rc=0 and printed `PROVENANCE PASSED: 27 units, 0 problem(s)`.
  - The 27 units: 19 methods, 5 module-level names, the 3 helpers and the section banner.
  - Every unit prints `IDENTICAL`, except `_build_dhw_requirements`, which is `IDENTICAL after 3 listed substitution(s)`: the return annotation, the two stash lines, and `), requirement`.
  - `still defined on HeatPumpOptimizer at HEAD: []`.
  - `DhwPlanner methods the table does not name (besides __init__): []`.
  - The non-moved module-level names are exactly `['DhwPlanner', '_Horizon', '_LOGGER', '_PlannerConfig']`.
  - Its own null control: `control: 27 of 27 single-character perturbations detected`.
  - It prints the residual `optimizer.py` diff (BASE less every moved unit, against HEAD): `+29 -31` lines of imports, the construction, the six call sites and the `_dhw_legionella_step` removals.
- **Counts the description states.**
  - Retargeted direct calls: `git diff 948671af1...HEAD -- tests/features.py | grep '^+' | grep -o '_dhw_planner([^)]*)\._[a-z_]*(' | wc -l` printed 44.
  - Re-keyed ledger rows: `git diff --name-status -M 948671af1...HEAD -- tests/mutation_ledger | grep -c '^R'` printed 10.
  - `_Horizon` Protocol fields: `awk '/^class _Horizon\(Protocol\)/,/^class _PlannerConfig/' custom_components/heatpump_optimizer/dhw_planner.py | grep -c '    def '` printed 11.
  - Methods and statements per class: `python3 tools/audit/round9/EG-B5/class_stmts.py 948671af1 HEAD`.
- **The design's six entry sites.** The residual diff shows exactly six planner calls, all in `_optimize_with_dhw` and `_co_optimize`: two `_build_dhw_requirements`, two `_dhw_coil_wood_forecast`, one `_dhw_planner_draws` and one `_baseline_dhw_economics`.
- **Structure.** `PYTHONPATH=tests/hastub:custom_components python3 tests/structure.py` exited rc=0 at this head. `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/structure_budgets.json` is empty.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: FULL -- every test script runs, nothing is scoped out.`, with reason `no recorded closure mentions custom_components/heatpump_optimizer/dhw_planner.py`. This is the expected new-module case; the closures job will record it (see Red checks).
- **Scripts run locally.** Python 3.14.7 with CI's pinned numpy and scipy, on the head tree:
  - Passed: `guard_pins.py` (9), `manual_plan.py` (85), `finite_boundary.py` (68), `edge.py`, `validate.py`, `plan_view.py`, `solar_alignment.py`, `deployment_shape.py`, `config_flow_steps.py` (496), `doc_claims.py` (112), and `typing_ruler.py` (source-only, 11).
  - `dst_checks.py` failed 7 of 131, and the base export fails the same 7: the `grep FAIL` lists of the two runs diffed equal.
  - `tests/entities.py` fails 3 of 2060, all closure-recording checks (see Red checks).
  - Not run locally: `optimality.py`, `stress.py`, `backtest.py`, `replay.py`, `rolling.py`, the node lanes, and the pinned mypy census. CI runs the FULL suite.
- **Typing (indicative, not the census).** mypy 2.3.1 with scipy-stubs 1.18.1.1 and numpy 2.4.6 (not the pinned 2.5.3, and without homeassistant-stubs), `--strict --follow-imports=silent` over `optimizer.py`, `dhw_planner.py`, `thermal_model.py` and `manual_plan.py`, reported 0 errors at the base and 0 at the head. Null control: adding a property `not_on_the_horizon` to the `_Horizon` Protocol made mypy refuse both `_dhw_coil_wood_forecast(h)` call sites in `optimizer.py`, so `optimizer._Horizon` really is checked against the Protocol. The census proper (`HPO_TYPING_PYTHON`) is CI's `typing` job; the seat's typing venv was removed when the disk filled.
- **Humidity rule.** `python3 tools/audit/round9/EG-B5/p3_control.py` takes the seam rule's own functions out of `tests/features.py` by AST.
  - At the head it finds 0 open seams with `_P3_FILES` including `dhw_planner.py`.
  - With one planner call's `humidity=humidity` removed (`dhw_planner.py` line 368, in `_dhw_legionella_due`), it finds 2 open seams when `dhw_planner.py` is in the files and `[]` when it is not. Without the `_P3_FILES` edit, the rule stops covering the moved code.
- **The #1747 carry, enumerator** (`fixer.md` step 8). `tools/audit/round9/rca/1747/kwarg_seams.py` keys on `self.<method>(...)` calls. It prints `RESULT seams=10` on `optimizer.py` at the base and `RESULT seams=9` at the head, and the missing one is `_build_dhw_requirements omits space_demand`. The move made it blind to the two builds, which are now `planner.` calls. `python3 tools/audit/round9/EG-B5/kwarg_seams_receivers.py custom_components/heatpump_optimizer/optimizer.py custom_components/heatpump_optimizer/dhw_planner.py` reads the receivers `self` and `planner` across both files and prints `RESULT seams=10` at the head. These are the same 10 seams as the base, and EG-B8's dispositions hold for each:
  - `_build_dhw_requirements omits space_demand` at the first build: intended, since the replan exists to price the space profile, and `blocked` is passed at both builds.
  - `_build_result` ×4, `_compute_baseline_power` ×2, `_deferred_energy_cost` ×1 and `_settlement_caps` ×2: the space-only path against the DHW path, which is not a defect.
- **The #1747 carry, census reach.** At the base, `tools/audit/round9/rca/1747/rca_census_reach.py` printed:
  - `as-is builds_seen=[True, True] shipped_dhw_kwh=0.00 breach=20.810`;
  - `no-replan builds_seen=[True] ... companion_with_reach(>=2)=FAIL`;
  - `off-spy builds_seen=[True] shipped_dhw_kwh=9.22 breach=0.629 check_first=FAIL check_companion=pass companion_with_reach(>=2)=FAIL`.

  At the head that harness raises `AttributeError: type object 'HeatPumpOptimizer' has no attribute '_build_dhw_requirements'`. Its port to the planner route, `tools/audit/round9/EG-B5/census_reach_planner.py`, which spies on `DhwPlanner._build_dhw_requirements` and rebuilds the off-spy arm through the handed-down planner, printed the same three lines figure for figure. The features.py spy now patches `DhwPlanner._build_dhw_requirements`, the callable both builds use, and keeps its reach clause (`len >= 2`). The head run reports both #1747 checks `ok`.

## Red checks

Expected on the first CI run, each an autofix case by name (`.claude/rules/ci-autofix.md`):
- `closures`: UNDER-SCOPED for `custom_components/heatpump_optimizer/dhw_planner.py`, a new module no recorded closure mentions. `closures-autofix` re-records it as `ci: re-record closures`.
- Until that bot commit lands, `tests/entities.py` reports three reds:
  - `every tracked file is either measured or deliberately classified` (`these force the FULL suite when touched: custom_components/heatpump_optimizer/dhw_planner.py`);
  - `and still covers every python file of the integration` (the env_drift closure lacks the new module);
  - `the deployment-shape lane's closure is the whole tracked package ...`.

  All three read the closure table that the bot commit rewrites. Cheaper detector: none worth building, because the bot repairs it in the same run at no standing cost.

## Forward-carry

none. No stage that has not started is narrowed:
- R9-EG-B1's brief says the planner "takes its inputs at construction, so B1 changes at most that construction site", and that still holds. The construction is one statement in `optimize`, `DhwPlanner(self.model, self.config, self._pv_surplus, self._price_known)`.
- The #1747 instruments' blindness is answered in the tree: `tools/audit/round9/EG-B5/kwarg_seams_receivers.py` and `census_reach_planner.py`.
- R9-F1.11 (done) adopted no registry shape keyed on `self.` calls. P2's census entry `dhw_mode_blocked_at_every_build` in `tests/entities.py` names the features check, which now spies on the planner.

## Friction

- `fixer.step3`: cost: `rca_census_reach.py` and `kwarg_seams.py` are keyed on the pre-move receiver (`HeatPumpOptimizer._build_dhw_requirements`, `self.<method>`), so after the move one raises and the other silently loses its target seam (10 → 9). Both had to be ported to re-measure the carry.
- `seat-environment`: cost: the Mac's data volume reached 100% during the seat (`no space left on device` on scratch logs). The seat removed its pinned typing venv, so the mypy census is left to CI.
