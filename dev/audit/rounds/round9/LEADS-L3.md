# Round 9 leads, seat L3 (batch 1)

Baseline `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Export prepared by `git archive`, `docs/audit-*.md` and `docs/backlog.md` deleted, earlier rounds stripped with `r9-strip-rounds.sh` (498 files removed, 235 kept). Work only in the export, `PYTHONPATH=tests/hastub`, venv314. No heavy D3 script re-run (tvofi, 2026-09-26); no `gh`; no GitHub read (one API read was refused by the permission system, see lead 29).

Set: 32 leads from `leads_L3.json`. Converted 7, closed 25. Findings by severity: critical 0, high 0, medium 1, low 6.

## Method

Each lead's owner report (`intake/reports.json`) was read first; a lead the owner measured as a finding or non-finding is closed by that entry. Leads with owner `unknown` were resolved with `check_scopes.py --seat` over every seat: files under `tests/` and `tests/hastub/` sit in no seat's file cells, so a test-double or gate-lane lead goes to the seat whose production cell it stands in for (the coordinator's base class to D1-s2, card lanes to D4-s1, the GOV pin to D11-s1). Seven leads were already dispositioned by seat L1 before the split and are closed as `done by L1`. One finding per mechanism: a lead that names only the reason a judged finding escaped the gate is closed by that finding (its fix owes the failing test; its escape is the root-cause seat's).

Every harness carries the contract header, the thread pin, `RESULT` lines with `thread_factor`, `load1`, `swapins`, and a perturbation that moves its number. CPU numbers are provisional (fan-out box, other leads seats running).

## Findings

### D1-s2-71 (low, P11, D1.M1) hastub DataUpdateCoordinator drops update_interval: the coordinator's cadence is unreadable in 4 of 4 cells

- **Claim.** Built through the real HeatPumpOptimizerCoordinator.__init__ with optimization_interval 5, 15, 30 and 60 min, the hastub DataUpdateCoordinator exposes no update_interval in 4 of 4 cells (upstream stores it), and ha_contract.py's inventory does not declare the attribute absent.
- **Mechanism.** tests/hastub/homeassistant/helpers/update_coordinator.py:DataUpdateCoordinator.__init__ accepts update_interval as a keyword and never stores it; the stub's authority (tests/ha_contract.py, 'absent' tuple for DataUpdateCoordinator) lists _schedule_refresh, _handle_refresh_interval and others but not update_interval, so the divergence is undeclared and no test can pin the cadence (a harness had to spy on the base __init__).
- **Evidence.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/l3_update_interval.py` -> 4 (of 4 configured intervals with no readable coordinator.update_interval (RESULT unreadable_cells)); count, tolerance exact, load1 1.0, thread_factor 1.0. shared leads box, 3 other leads seats; a count, contention-immune.
- **Instrumented symbol.** tests/hastub/homeassistant/helpers/update_coordinator.py:DataUpdateCoordinator.__init__ (driven by heatpump_optimizer.coordinator:HeatPumpOptimizerCoordinator.__init__)
- **Perturbation.** --perturb store: the stub __init__ keeps self.update_interval = update_interval (in memory) -> expected to_zero; observed unreadable_cells 4 -> 0; matching_cells 0 -> 4.
- **Metric.** Configured optimization_interval cells whose coordinator.update_interval is absent after the real coordinator __init__ over the hastub base class.
- **Null control.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/l3_update_interval.py` -> null_control_kept_attrs_readable=4 of 4. attributes the stub does keep (name, config_entry) are readable in every cell
- **Property.** Every attribute upstream DataUpdateCoordinator sets from a constructor argument the integration passes is readable on the stub, or is declared absent in ha_contract.py's inventory.
- **Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D1/leads/l3_update_interval.py  (cells = configured intervals; extend to every keyword the integration passes to DataUpdateCoordinator.__init__)`
- **Fix scope.** Store update_interval in the stub's __init__ (as upstream does) and pin it in ha_contract.py against the real package; ~2 lines plus one contract row.

### D11-s1-71 (low, I4, D11.M3) Two parsers of a rule's paths: frontmatter disagree on 2 of 6 legal shapes (rules_sync vs policy_lint)

- **Claim.** On 2 of 6 probe frontmatters (a trailing YAML comment on a paths entry; a quoted list item under another key) rules_sync.mjs:parse and policy_lint.mjs:rulePaths return different path lists, so the generated .cursor/rules globs and the binding/budget checks read different scopes for one file; 0 of the 10 live rules diverge today.
- **Mechanism.** rules_sync.mjs:parse takes every `- "..."` line anywhere in the frontmatter and requires `"\s*$` at line end; policy_lint.mjs:rulePaths reads only the `paths:` block and accepts trailing text. Neither calls the other, and rules_sync --check compares the .mdc with its own parse, so the divergence passes both checks.
- **Evidence.** `node tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs` -> 2 (of 6 probe frontmatters with differing path lists (RESULT divergent_cells)); count, tolerance exact, load1 0.72, thread_factor 1.0. shared leads box, 3 other leads seats; a count, contention-immune.
- **Instrumented symbol.** .claude/workflows/rules_sync.mjs:parse and .claude/workflows/policy_lint.mjs:rulePaths (both extracted from the files at run time)
- **Perturbation.** --perturb eol: rules_sync parse's `"([^"]+)"\s*$/gm` -> `"([^"]+)"/gm` (one-line edit, in memory) -> expected down; observed divergent_cells 2 -> 1 (the trailing-comment cell agrees; the other-key cell remains).
- **Metric.** Probe rule frontmatters on which rules_sync parse().paths and policy_lint rulePaths() return different lists (JSON-compared).
- **Null control.** `node tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs` -> null_control_wellformed_divergent=0 of 3; live_rules_divergent=0 of 10. well-formed double-quoted block entries agree; capability, not incidence
- **Property.** One rule file's paths: scope is parsed by one function, so the generated Cursor globs, rule-binding, role budgets and the always-loaded cap read the same list for every frontmatter.
- **Seam rule.** `node tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs  (cells = frontmatter shapes; seams = every reader of a rule's paths: key: grep -n 'paths' .claude/workflows/*.mjs)`
- **Fix scope.** rules_sync.mjs reuses policy_lint's rulePaths (export it, or move it to a shared module) instead of its own regex; add the two probe shapes to rules_sync's --check fixtures.

### D11-s1-72 (low, I4, D11.M3) entities.py GOV pin reads governance.yml only: a new governance job in 3 of 3 other workflow files passes

- **Claim.** The entities.py pin on governance_cost.py's GOV set stays green when a new job is added to pr-contract.yml, budget-raise-gate.yml or budget-raise-gate-rerun.yml (3 of 3), although GOV's own derivation rule names the first two as governance, and rerun-stale-verdict is already a governance job GOV does not name.
- **Mechanism.** The pin checks GOV <= all job ids and _workflow_job_ids(governance.yml) <= GOV; the second arm reads only governance.yml, while governance_cost.py's comment derives GOV from governance.yml plus briefs, pr-contract.yml and budget-raise-gate.yml. Jobs in those files are never compared, so the set can go stale unseen (D13-s1 measured 64 s of rerun-stale-verdict missed).
- **Evidence.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/leads/l3_gov_pin.py` -> 3 (of 3 probe governance jobs outside governance.yml the pin passes (RESULT escaping_cells)); count, tolerance exact, load1 0.89, thread_factor 1.0. shared leads box, 3 other leads seats; a count, contention-immune.
- **Instrumented symbol.** tests/entities.py GOV pin ('the governance-cost GOV set names only jobs the workflow files define, and every governance.yml job'), executed from its own source slice; tools/audit/round4/D11/governance_cost.py:GOV
- **Perturbation.** --perturb all-files: the pin's `_workflow_job_ids(_DS_GOV)` widened, in memory, to the union over governance.yml, pr-contract.yml, budget-raise-gate.yml and budget-raise-gate-rerun.yml -> expected to_zero; observed escaping_cells 3 -> 0; the pin also fails at baseline on the live rerun-stale-verdict.
- **Metric.** Probe cells (one new job appended to a workflow file GOV's rule or D13's re-derivation counts as governance) in which entities.py's GOV pin still passes.
- **Null control.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/leads/l3_gov_pin.py` -> positive_control_pin_fails=1 of 1 (new job in governance.yml). the pin does fire on the file it reads
- **Property.** Every job of every workflow file GOV's derivation rule names is either in GOV or refused by the pin.
- **Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/leads/l3_gov_pin.py  (cells = workflow files named by GOV's derivation comment plus workflow_run followers of them)`
- **Fix scope.** Derive the pin's governance job set from the same file list GOV's comment names (and add budget-raise-gate-rerun.yml, or record why it is excluded); add rerun-stale-verdict to GOV.

### D7-s1-71 (low, new, D7.M1) Cold-water inlet default held three times: 3 of 5 sites ignore DEFAULT_DHW_INLET_TEMP when it moves

- **Claim.** With const.DEFAULT_DHW_INLET_TEMP moved from 10.0 to 12.5, 3 of 5 production sites that resolve a cold-water default still deliver 10.0: bare ThermalParameters() (thermal_model.py:469 literal), sysid._sizing_model's plant (via that literal) and dhw_coil_draw_reduction's inlet_temp default (const.DHW_COLD_WATER_TEMP).
- **Mechanism.** The default is spelled three ways: const.DEFAULT_DHW_INLET_TEMP (from_config and the options flow read it), a bare 10.0 on the ThermalParameters field, and const.DHW_COLD_WATER_TEMP, now only a default argument all three call sites override. They agree only because all three are 10.0 today.
- **Evidence.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_cold_water_default.py` -> 3 (of 5 sites whose delivered default does not follow the moved constant (RESULT sites_not_following)); count, tolerance exact, load1 1.19, thread_factor 1.0. shared leads box, 3 other leads seats; a count, contention-immune.
- **Instrumented symbol.** heatpump_optimizer.thermal_model:ThermalParameters.dhw_inlet_temp (also thermal_model:dhw_coil_draw_reduction, const:DEFAULT_DHW_INLET_TEMP)
- **Perturbation.** --perturb literal: thermal_model.py:469 `dhw_inlet_temp: float = 10.0` -> `= const.DEFAULT_DHW_INLET_TEMP` (one-line edit, in memory) -> expected down; observed sites_not_following 3 -> 1 (the coil default remains).
- **Metric.** Of 5 production sites resolving a cold-water inlet default, those whose delivered value does not move when const.DEFAULT_DHW_INLET_TEMP is moved 10.0 -> 12.5.
- **Null control.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_cold_water_default.py --no-move` -> sites_disagreeing=0 of 5. with the constant unmoved all sites agree at 10.0: no user-visible divergence today (hygiene)
- **Property.** A configurable default is defined once and every site that falls back to it reads that one definition.
- **Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_cold_water_default.py  (sites = grep -n 'DEFAULT_DHW_INLET_TEMP\|DHW_COLD_WATER_TEMP\|dhw_inlet_temp: float' custom_components/heatpump_optimizer/*.py)`
- **Fix scope.** The ThermalParameters field defaults to const.DEFAULT_DHW_INLET_TEMP; DHW_COLD_WATER_TEMP is removed or aliased to it and dhw_coil_draw_reduction's inlet_temp made required (all 3 callers pass it).

### D7-s3-72 (low, new, D7.M6) 4 of 5 ThermalModel per-step scratch members are written every step and read by no production consumer

- **Claim.** Across four real solves (winter_single_dhw, dhw_cold_tank, wood_two_tank, wood_coil) production writes _step_dhw_refused, _step_dhw_floor_injected, _step_dhw_draw_kw and _step_wood_refused 31k-167k times each and no production function reads them (0 consumer reads, 0 loads outside thermal_model.py); only tests/features.py does (18 references).
- **Mechanism.** The step functions book refused heat, floor injection and the debited draw on the model instance for a consumer that was never written: only _step_buffer_refused is read (simulate_trajectory). The _step_dhw_draw_kw comment says it lets 'energy accounting outside the model' balance the step; nothing outside reads it. D7-s3-01's reach census counts a store as reach, so it cannot see write-only members.
- **Evidence.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_write_only_scratch.py` -> 4 (of 5 _step_* members with production writes and 0 production consumer reads (RESULT write_only_members)); count, tolerance exact, load1 1.99, thread_factor 1.0. shared leads box, 3 other leads seats; a count, contention-immune.
- **Instrumented symbol.** heatpump_optimizer.thermal_model:ThermalModel._step_dhw_refused (and _step_dhw_floor_injected, _step_dhw_draw_kw, _step_wood_refused; runtime descriptors record caller frames)
- **Perturbation.** --perturb reader: a one-line production read of self._step_dhw_draw_kw in ThermalModel.simulate_trajectory, compiled under thermal_model.py -> expected down; observed write_only_members 4 -> 3.
- **Metric.** ThermalModel _step_* members with >=1 production write and 0 reads from production functions that never write that member, over four golden solves.
- **Null control.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_write_only_scratch.py` -> live_control_buffer_consumer_reads=97344. _step_buffer_refused, written by the same step functions, is read by simulate_trajectory: the instrument sees a live consumer
- **Property.** Every member production writes is read by some production consumer; state computed only for tests is dead production work.
- **Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_write_only_scratch.py  (members = ThermalModel class attributes named _step_*; extend to any attribute with production stores and no production loads)`
- **Fix scope.** Either give the ledgers their production consumer (the energy/refused-heat accounting their comments describe) or return them from the step for the tests that assert conservation instead of storing them on the instance; retarget the 18 features.py references.

### D9-s1-71 (low, new, D9.M1) Constant DHW parameter helpers recomputed ~15-45k times per solve; a per-solve cache saves 3-17 % of CPU

- **Claim.** ThermalParameters.dhw_tank_heat_loss_coefficient, dhw_inlet_reference and effective_dhw_draw_pattern are recomputed 4k-11k, 12k-33k and ~98 times per DHW solve for values constant within the solve; memoising them per instance leaves 5 of 5 plans bitwise identical and cuts the capture's thread CPU by 0.026-0.174 (mean 0.094) against a null arm of -0.030..+0.050 (mean -0.001).
- **Mechanism.** The DHW step reads the tank loss coefficient (an np.clip on a scalar each call), the inlet reference and, per horizon build, the windowed draw pattern (24 overlap_fraction calls) through properties/methods that recompute from unchanged parameters on every simulated step.
- **Evidence.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_dhw_helpers.py` -> 0.094 (mean share of golden.capture thread CPU saved by the per-solve cache over 5 DHW cells (RESULT saved_share_mean)); cpu, tolerance ±0.05 (null arm band), load1 1.79, thread_factor 1.0. PROVISIONAL: fan-out CPU on a shared box with other leads seats; interleaved plain/memo arms, ratio metric; re-take in the quiet window.
- **Instrumented symbol.** heatpump_optimizer.thermal_model:ThermalParameters.dhw_tank_heat_loss_coefficient (with .dhw_inlet_reference and .effective_dhw_draw_pattern), driven through HeatPumpOptimizer.optimize
- **Perturbation.** per-instance memoisation of the three helpers (in memory); the null arm installs the same wrapper layer without caching -> expected down; observed CPU ratio memo/plain 0.826-0.974 vs null 0.950-1.030.
- **Metric.** 1 - (thread CPU of golden.capture with the three helpers memoised per ThermalParameters instance / plain), interleaved x2 per cell; plus helper calls per solve.
- **Null control.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_dhw_helpers.py --null` -> saved_share_min=-0.0302 max=0.0497 mean=-0.0006. same wrapper layer, no cache: the band the memo arm must exceed
- **Leave-one-out.** 5 cells, range 0.0259..0.1742, mean with the most favourable cell dropped 0.0745.
- **Property.** A value that is constant within a solve is computed once per solve, not once per simulated step.
- **Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_dhw_helpers.py  (seams = ThermalParameters properties/methods called from simulate_dhw_step and the DHW planners; count calls per solve)`
- **Fix scope.** Hoist the three values once per solve (a cached_property invalidated on parameter change, or locals in simulate_dhw_step's caller); scalar math instead of np.clip in dhw_tank_heat_loss_coefficient.

### D9-s2-71 (medium, I1, D9.M2) stress.py samples 0 of 51 throttling-valve plants; a valve adds 1.3-2.7x solve CPU the gate never sees

- **Claim.** None of tests/stress.py's 51 sweep cases builds a plant with a throttling mixing valve (0 of 51, keyed on the params handed to optimize()), while on four golden valve plants the valve itself multiplies optimize() CPU by 1.30-2.70 against the same plant with mixing_valve_mode='none' (smart_write 2.70x: 2x the step-equivalents), so a regression confined to the valve path is unsampled by the only per-PR CPU gate.
- **Mechanism.** sweep_combinations() crosses season x zones x DHW and tariff/pv/cycling on house() defaults, which leave mixing_valve_mode at none; build_case takes no valve argument. The valve branches of the simulate kernels (_simulate_step_two_zone, simulate_trajectory_batch) and smart_write's larger search therefore contribute no row to the budget table, the same UNSAMPLED shape build_case's docstring records for #287's zero-range bounds.
- **Evidence.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_valve_solve.py` -> 0 (of 51 stress sweep cases with a throttling valve (RESULT stress_sweep_valve_cases); valve/no-valve CPU 1.30-2.70x); count, tolerance exact (count); CPU ratios provisional, load1 1.83, thread_factor 1.0. the coverage count is exact; CPU ratios are fan-out numbers on a shared box (thread_factor 1.000), re-take in the quiet window.
- **Instrumented symbol.** tests/stress.py:sweep_combinations/build_case (plant handed to heatpump_optimizer.optimizer:HeatPumpOptimizer.optimize), metered with tests/stress.py:SolverWork
- **Perturbation.** --perturb novalve: mixing_valve_mode='none' on the four valve cells (config change) -> expected down; observed valve cells' CPU/reference 131-285 -> 101-116; smart_write step-equivalents 9,426,048 -> 4,852,896.
- **Metric.** Stress sweep cases whose built ThermalParameters throttle; and per golden valve plant, optimize() thread CPU / reference_solve with the valve vs mixing_valve_mode='none'.
- **Null control.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_valve_solve.py --perturb novalve` -> control cells (winter_two_zone_no_dhw, shoulder_two_zone) step-equivalents unchanged exactly (4,219,488; 3,507,029); CPU/reference 84.7->92.6, 71.7->74.7. the no-valve controls do not move under the perturbation beyond CPU noise; only valve cells do
- **Property.** Every plant topology the integration supports that changes the solve's kernel or search is sampled by at least one stress.py budget row.
- **Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_valve_solve.py  (topology axes = const TOPOLOGY_* and mixing_valve modes; count sweep cases per axis value)`
- **Fix scope.** Add at least one manual and one smart_write two-zone valve case (and valve_upper_direct_slab / two_tank_4way where their kernels differ) to sweep_combinations via a build_case config, record their budget rows (a budget-table re-record, owner-approved).

## Converted leads

| # | raised by | file : symbol | finding |
|---|---|---|---|
| 9 | D5-s2 | `tests/hastub/homeassistant/helpers/update_coordinator.py` : DataUpdateCoordinator.__init__ | D1-s2-71 |
| 16 | D5-s2 | `custom_components/heatpump_optimizer/thermal_model.py` : ThermalParameters.dhw_inlet_temp | D7-s1-71 |
| 17 | D7-s2 | `custom_components/heatpump_optimizer/thermal_model.py` : ThermalModel._step_dhw_refused/_step_dhw_floor_injected/_step_dhw_draw_kw/_step_wood_refused | D7-s3-72 |
| 23 | D9-s2 | `custom_components/heatpump_optimizer/thermal_model.py` : ThermalModel.effective_dhw_draw_pattern / dhw_tank_heat_loss_coefficient / dhw_inlet_reference | D9-s1-71 |
| 24 | D12-s1 | `custom_components/heatpump_optimizer/optimizer.py` : HeatPumpOptimizer.optimize | D9-s2-71 |
| 27 | D11-s2 | `.claude/workflows/rules_sync.mjs` : parse | D11-s1-71 |
| 31 | D13-s1 | `tools/audit/round4/D11/governance_cost.py` : GOV | D11-s1-72 |

## Closed leads

| # | raised by | owner | file : symbol | why |
|---|---|---|---|---|
| 0 | D1-s1 | D1-s1 | `tests/hastub/homeassistant/helpers/storage.py` : Store.async_save/async_load | done by L1: D1-s1-51 |
| 1 | D1-s2 | D1-s1 | `tests/hastub/homeassistant/helpers/storage.py` : Store.async_load | done by L1: D1-s1-51 |
| 2 | D1-s2 | D1-s2 | `tests/harness.py` : ha_unload_entry | done by L1: non-finding (unload_coroutines.py dropped=1, raised_when_run=0) |
| 3 | D1-s3 | D1-s1 | `tests/hastub/homeassistant/util/dt.py` : now | done by L1: D1-s1-52 |
| 4 | D1-s4 | D1-s1 | `tests/hastub/homeassistant/helpers/storage.py` : Store.async_save/async_load | done by L1: D1-s1-51 |
| 5 | D3-s1 | D3-s1 | `tests/golden/coord_dhw.json` : data.dhw_advisor | closed by D3-s1's own M2 prescreen entry: dhw_advisor is produced in coordinator.py (D3-s1's cells, check_scopes --seat D3-s1), and mutant C0086 (_dhw_setpoint_sweep) was KILLED by features.py, so the gate is not blind to the advisor's cover/ranking logic; the golden's degeneracy is redundancy, not a gap. Not re-run (tvofi 2026-09-26: no heavy D3 scripts). |
| 6 | D3-s1 | D11-s1 | `tools/audit/round3..round8` : (tracked files) | by design, measured: r9-strip-rounds.sh (prepare_baseline strip_earlier_rounds) run on this seat's export printed RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 -- the same 498; it keeps every tools/audit/round* file named in tests/closures.json or by a literal path in tests/*.py/*.mjs/*.sh, so no file the gate reads is removed. Export-only; the tracked tree is untouched. |
| 7 | D4-s1 | D4-s1 | `tests/card_rig.mjs` : planStates | closed by D4-s1-05 (now-marker label over the measured-now reading on the live default view): that the card lanes' default-view states come from planStates() without withActuals is why the gate missed it -- the failing lane test that finding's fix owes (fixer.md step 1) and the escape's process cause under defect-root-cause.md, not a second mechanism. Owner D4-s1 (www/**; tests/*.mjs sit in no seat's cells, check_scopes). |
| 8 | D4-s1 | D4-s1 | `tests/card_browser.mjs` : contrastOf / REQUIRED | closed by D4-s1-01 (status-token text below WCAG AA): the contrast lane measuring four fixed sites on fixtures with no status outcome is why the gate missed it -- the failing lane test that fix owes and its root-cause seat's process cause, not a second mechanism. Owner D4-s1. |
| 10 | D6-s2 | D6-s2 | `tests/entities.py` : README count pins (~lines 566-886) | closed by D6-s2-01 (configuration.md 'All 74 entities' vs 75): the missing pin is the failing test that finding's fix owes under fixer.md step 1, not a second mechanism. D6-s2's cells hold docs/configuration.md (check_scopes --seat D6-s2). |
| 11 | D7-s3 | D7-s3 | `tests/nightly_ha.py` : line 1274 (return inside finally, A4 recovery block) | done by L1: D7-s3-51 |
| 12 | D11-s1 | D11-s1 | `tests/delivery_status.py` : collect | same phenomenon and seam as D11-s1-02 (single-parent direct pushes to main reported by no enumerator); its proposed_fix_scope already names delivery_status.collect. The docstring is that seam's prose; no separate mechanism. |
| 13 | D12-s1 | D12-s1 | `tools/audit/round9/D12/s1/` : REPORT.md | not a defect of the baseline: a report-rendering matter for the orchestrator (the seat's JSON is its report). Nothing to measure. |
| 14 | D12-s3 | D3-s3 | `tests/entities.py` : _walk_flow_untouched / check 'and turns hot water on anyway, with the 200 L tank the page pre-fills' | owner deferred to catch-up batch; re-route then (a test-suite gap on config_flow.py is a D3 cell; check_scopes --seat D3-s3 lists config_flow.py) |
| 15 | D14-s1 | D1-s1 | `tests/hastub/homeassistant/util/dt.py` : now | done by L1: D1-s1-52 |
| 18 | D9-s1 | D9-s2 | `custom_components/heatpump_optimizer/coordinator.py` : HeatPumpOptimizerCoordinator._run_system_identification | closed by D9-s1-03, one finding per mechanism: its claim already names the synchronous call of SystemIdentification.step in coordinator._async_update_data; the call-site fix is that finding's fix scope. |
| 19 | D9-s1 | D9-s2 | `custom_components/heatpump_optimizer/coordinator.py` : _maybe_run_fuse_advisor / _await_optimize | closed by D9-s2's non-finding 'A coordinator cycle runs exactly one full solve by default': solves_per_cycle_mean=1.0000 (main 48/48), 2.0000 with price tiles, fuse advisor 0 solves/day (weekly rate limit). |
| 20 | D9-s1 | D9-s2 | `custom_components/heatpump_optimizer/coordinator.py` : _solve_snapshot | closed by D9-s2's non-finding on the default cycle's loop-thread work: loop_update_cpu_ms=9.03 per cycle (0.617 reference solves including the entity read), which bounds everything _async_update_data runs on the loop, _solve_snapshot included. |
| 21 | D9-s1 | D9-s2 | `custom_components/heatpump_optimizer/coordinator.py` : _await_optimize (in-process fallback) | closed by D9-s1's non-finding (in-process fallback starvation share 0.91-0.94, documented degraded path capped by WORKER_FALLBACK_CAP with a repair issue); what remains is a design choice about N, not a falsifiable defect. |
| 22 | D9-s2 | D9-s1 | `custom_components/heatpump_optimizer/optimizer.py` : HeatPumpOptimizer._build_dhw_requirements / _apply_dhw_min_run / _plan_dhw_min_cost | closed by D9-s1-04 and D9-s1's DHW-planner non-finding: _build_dhw_requirements is the parent of every DHW planner (optimizer.py:4712; it calls _plan_dhw_min_cost, _plan_dhw_cheapest_first, _apply_dhw_min_run, _clamp_dhw_to_capacity, _repair_dhw_floor), D9-s1 decomposed that parent (0.526 of the single-zone DHW solve, 0.287 of it _apply_dhw_min_run = D9-s1-04; each other planner 0.001-0.124). The replay's 58 % is the same parent under cProfile. |
| 25 | D11-s2 | D11-s1 | `.github (ruleset on main)` : pull_request rule: require_last_push_approval / dismiss_stale_reviews_on_push | closed by D11-s1-01 (ruleset dismiss_stale_reviews_on_push=false, require_last_push_approval=false; #1621 and #1623 merged on a stale owner approval). |
| 26 | D11-s2 | D11-s1 | `.claude/workflows/policy_lint.mjs` : cmdHooks | closed by D11-s2-02 (cmdHooks never reads a hook's matcher, 4 of 4 wrong matchers pass): the missing policy-rot/hooks fixture is the failing test that fix owes, not a second mechanism. |
| 28 | D11-s2 | D11-s1 | `.claude/workflows/budget_raise_gate.py` : approval | closed by D11-s1-04 (budget_raise_gate.py:approval accepts orchestrator-given approvals as the owner's, 27/27) and D11-s2-03; the lead names a fix constraint, not a defect. |
| 29 | D13-s1 | D11-s1 | `.github/workflows/governance.yml` : instrument-self-tests | not measured by this seat: the lead needs GitHub Actions run history and logs for governance.yml's instrument-self-tests on main, and this seat's GitHub API read was refused by the permission system (no gh, per brief). D13-s1's count (18 of 201 main merges, one 11.69 h episode) stands unconverted; re-route to a seat with GitHub read (D11-s1's d11lib cache) in the catch-up batch. |
| 30 | D13-s1 | D11-s1 | `.claude/workflows/web-fix-wave.js` : verdict poster identity | same phenomenon as D11-s1-04 (seat actions are recorded under the owner account, so the record cannot show the owner's own act); D13-s1's count 166 of 239 'Fix review:' lines under tvofi is a further seam of it, carried here for that finding's fix. No GitHub read from this seat. |

## Non-findings

- Lead 'tools/audit/round3..round8 deleted' (D3-s1): the deletion is the round-9 strip of earlier rounds, by design; it keeps every round* file the gate reads (named in tests/closures.json or by a literal path in tests/*.py|*.mjs|*.sh). `sh r9-strip-rounds.sh <export> /home/claude/venv314/bin/python  (origin/handoff/audit-r9-plan:handoff/round9/r9-strip-rounds.sh)` -> RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235
- D12-s1's 50-145 s wall per two-zone valve solve is not reproduced as a solve cost: on this box one golden valve solve takes 9.7-21.1 s thread CPU (131-285 reference solves) against 5.3-6.3 s for two-zone no-valve plants; the valve's own share is recorded in D9-s2-71. `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D9/leads/l3_valve_solve.py` -> cpu_ratio_to_reference_valve_min=131.4 max=285.2; control 71.7-84.7; reference_solve_cpu_s=0.0739; load1 1.83 (provisional)
- Of the ThermalModel per-step scratch, _step_buffer_refused is live: simulate_trajectory reads it on every step (control arm of D7-s3-72). `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D7/leads/l3_write_only_scratch.py` -> live_control_buffer_consumer_reads=97344 over 4 solves
- The GOV pin in tests/entities.py does fire on a new job in governance.yml, the one file it reads (positive control of D11-s1-72). `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D11/leads/l3_gov_pin.py` -> positive_control_pin_fails=1 of 1
- No live .claude/rules/*.md file is parsed differently by rules_sync.mjs and policy_lint.mjs today (D11-s1-71 is a capability). `node tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs` -> live_rules_divergent=0 of 10

## Not finished

- Lead 29 (D13-s1: instrument-self-tests red on 18 of 201 main merges) is unconverted: it needs GitHub Actions history and logs, and this seat's API read was refused. Route to a seat with GitHub read.
- Every CPU ratio above (D9-s1-71, D9-s2-71's 1.30-2.70x) is a fan-out number; the quiet window should re-take `l3_dhw_helpers.py` (both arms) and `l3_valve_solve.py` (both arms). The counts are final.

## Harnesses

- `tools/audit/round9/D1/leads/l3_update_interval.py`
- `tools/audit/round9/D11/leads/l3_frontmatter_parsers.mjs`
- `tools/audit/round9/D11/leads/l3_gov_pin.py`
- `tools/audit/round9/D7/leads/l3_cold_water_default.py`
- `tools/audit/round9/D7/leads/l3_write_only_scratch.py`
- `tools/audit/round9/D9/leads/l3_dhw_helpers.py`
- `tools/audit/round9/D9/leads/l3_valve_solve.py`

## Exposure

Read the round-9 seat reports (`intake/reports.json`) and seat L1's `leads_result.json` as the brief requires; no earlier-round finding, no `docs/audit-*.md`, no GitHub.

