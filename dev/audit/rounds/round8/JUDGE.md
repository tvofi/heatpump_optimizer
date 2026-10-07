# Round 8 judge register

Baseline cdf82daabcfe3777d98b31489f36df5555ec9d82. One common judge across all 14 dimensions; tree /home/claude/audit-r8/seats/judge. Box: 4-vCPU cloud container; every timing number is provisional, decisions rest on counts and ratios unless stated.

| id | dim | finder sev | vote | verdict | final sev | class | prod | merged into |
|---|---|---|---|---|---|---|---|---|
| D5-s1-01 | D5 | low | verify(low) | verified | low | hygiene | False |  |
| D5-s2-01 | D5 | low | verify(low) | verified | low | hygiene | True |  |
| D6-s1-01 | D6 | low | verify(low) | verified | low | hygiene | False |  |
| D1-s1-01 | D1 | medium | verify(medium) | verified | medium | bug | True |  |
| D1-s1-02 | D1 | low | verify(low) | verified | low | bug | True |  |
| D1-s2-01 | D1 | critical | weaken(medium) | weakened | medium | bug | True |  |
| D1-s3-01 | D1 | high | weaken(medium) | weakened | medium | bug | True |  |
| D11-s1-01 | D11 | critical | weaken(high) | weakened | high | bug | False |  |
| D11-s1-02 | D11 | high | weaken(medium) | merged | medium | bug | False | D11-s2-01 |
| D11-s1-03 | D11 | low | verify(low) | verified | low | bug | False |  |
| D11-s2-01 | D11 | high | verify(high) | verified | high | bug | False |  |
| D11-s2-02 | D11 | high | verify(high) | verified | high | bug | False |  |
| D11-s2-03 | D11 | low | verify(low) | verified | low | hygiene | False |  |
| D2-s1-01 | D2 | medium | verify(medium) | verified | medium | bug | True |  |
| D2-s1-02 | D2 | low | verify(low) | verified | low | bug | True |  |
| D2-s2-01 | D2 | high | verify(high) | verified | high | bug | True |  |
| D2-s2-02 | D2 | high | verify(high) | verified | high | bug | True |  |
| D8-s1-01 | D8 | high | verify(high) | weakened | low | bug | True |  |
| D8-s2-01 | D8 | high | refute(none) | refuted | none | hygiene | False |  |
| D8-s2-02 | D8 | medium | weaken(low) | weakened | low | bug | True |  |
| D13-s1-01 | D13 | medium | weaken(low) | weakened | low | hygiene | False |  |
| D13-s1-02 | D13 | medium | verify(medium) | verified | medium | bug | False |  |
| D10-s1-01 | D10 | low | verify(low) | verified | low | hygiene | True |  |
| D10-s1-02 | D10 | low | verify(low) | verified | low | hygiene | True |  |
| D10-s2-01 | D10 | medium | weaken(low) | refuted | none | hygiene | False |  |
| D3-s1-02 | D3 | medium | weaken(low) | weakened | low | bug | False |  |
| D7-s1-01 | D7 | medium | verify(medium) | verified | medium | bug | True |  |
| D7-s1-02 | D7 | medium | verify(medium) | verified | medium | bug | True |  |
| D7-s1-03 | D7 | medium | verify(medium) | verified | medium | bug | True |  |
| D4-01 | D4 | medium | verify(medium) | verified | medium | bug | True |  |
| D4-s2-01 | D4 | low | verify(low) | verified | low | hygiene | True |  |
| D0-s1-01 | D0 | low | verify(low) | verified | low | hygiene | True |  |
| D12-s1-01 | D12 | high | weaken(medium) | weakened | medium | bug | True |  |
| D12-s1-02 | D12 | medium | verify(medium) | verified | medium | bug | True |  |
| D9-s1-01 | D9 | low | verify(low) | verified | low | hygiene | True |  |
| D9-s2-01 | D9 | medium | weaken(low) | weakened | low | hygiene | False |  |
| D7-s2-01 | D7 | low | verify(low) | verified | low | hygiene | True |  |
| D7-s2-02 | D7 | low | verify(low) | verified | low | hygiene | False |  |
| D7-s2-03 | D7 | low | verify(low) | verified | low | hygiene | False |  |
| D3-s1-01 | D3 | medium | verify(medium) | verified | medium | bug | False |  |
| D3-s2-01 | D3 | medium | weaken(low) | weakened | low | hygiene | False |  |
| D3-s2-02 | D3 | low | verify(low) | verified | low | hygiene | False |  |
| D9-s1-02 | D9 | low | refute(none (documented, capped fallback trade; judge to re-take timing)) | refuted | none | hygiene | False |  |

## D5-s1-01 -- verified, low, hygiene

**Judge number:** mismatched_labels=3 (harness); 4 by hand (building-description node diagram 4 vs prose 5, dropped by the <br/> label truncation)

**Ruling:** Re-ran s1_stepnum.py: 3 (load1 0.47, thread_factor 1.00); --fix -> 0. Verifier (verify, low) measured the same metric and the same 4th mismatch by hand; votes comparable. Non-timing text count, no null control applies.

**Issue title:** [R8-D5-s1-01] README Quick-start diagram numbers screens 3-6 while the prose numbers the same screens 4-7

README.md's Quick-start mermaid flowchart numbers Temperatures, building description, Hot water and Weather sensitivity 3, 4, 5, 6, while the numbered prose headings for the same screens read 4, 5, 6, 7 because the prose spends number 3 on the unnumbered finish-menu node; the harness counts 3 mismatched labels and a hand read finds the 4th (building description, diagram 4 vs prose 5), which the harness drops because its node regex truncates labels at the first <br/>.

Evidence: tools/audit/round8/D5/s1_stepnum.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D5/s1_stepnum.py` -> RESULT mismatched_labels=3 (judge re-run, load1 0.47, thread_factor 1.00); perturbation `--fix` (prose renumbered down by one in a temp copy) -> 0. No null control applies to a text count.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: README.md Quick-start only; renumber either the diagram nodes or the four prose headings so each screen carries one number; no code, test or golden change.

Finding id: D5-s1-01 (round 8, baseline cdf82daa).

## D5-s2-01 -- verified, low, hygiene

**Judge number:** shorthand_missing=2

**Ruling:** Re-ran s2_comment_idents.py: shorthand_missing=2 (raw_missing 19, 640 idents). Perturbation (two comment-only edits, restored in finally, git status clean) -> 0. Verifier measured a stricter block-local bar and found const.py:80's real name is not in the same block; claim wording 'beside the real full name' holds for 1 of 2, metric (same file) holds for 2 of 2. Comment-only, but the files are under custom_components/.

**Issue title:** [R8-D5-s2-01] Two production comments name MIN_POWER and min_power, bare forms with zero code occurrences

Two >3-line comment blocks in production abbreviate a real symbol to a bare form that occurs nowhere in code: const.py:80 writes `MIN_POWER` for CONF_HEAT_PUMP_MIN_POWER and optimizer.py:6518 writes `min_power` for min_electrical_power; the harness counts shorthand_missing=2 of 640 checked identifiers.

Evidence: tools/audit/round8/D5/s2_comment_idents.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D5/s2_comment_idents.py` -> RESULT shorthand_missing=2 (judge re-run, load1 0.47); perturbation replacing the two tokens with the full names -> 0, files restored byte-identical. The verifier's stricter same-block bar holds for optimizer.py only (const.py's block names CONF_HEAT_PUMP_MAX_POWER, not the MIN sibling). No null control applies to a text count.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: two comment-only edits in custom_components/heatpump_optimizer/const.py:80 and optimizer.py:6518; no behavioural change, no golden drift.

Finding id: D5-s2-01 (round 8, baseline cdf82daa).

## D6-s1-01 -- verified, low, hygiene

**Judge number:** undocumented_and_used_count=1 (threadpoolctl)

**Ruling:** Re-ran s1_requirements_claim.py: 1 of 3 manifest requirements undocumented. Judge perturbation (README Requirements names threadpoolctl) -> 0; finder's perturbation (remove from manifest) -> 0 per verifier. Verifier's AST/whole-README metric agrees (1). Runtime import is try/except guarded, so low.

**Issue title:** [R8-D6-s1-01] README Requirements names numpy and scipy but not threadpoolctl, the manifest's third requirement

README.md's Requirements section says the Python dependencies are `numpy` and `scipy`, installed from the manifest, while manifest.json's requirements pin a third package, threadpoolctl>=3.5.0, that optimizer.py imports at runtime; the harness counts 1 of 3 manifest requirements undocumented and used, and threadpoolctl appears nowhere in README.md.

Evidence: tools/audit/round8/D6/s1_requirements_claim.py, command `python3 tools/audit/round8/D6/s1_requirements_claim.py` -> RESULT undocumented_and_used_count=1 ['threadpoolctl'] (judge re-run, load1 0.72); perturbation adding threadpoolctl to the Requirements prose -> 0, README restored. The verifier's AST-import, whole-README metric gives the same 1. The import is guarded by try/except, so the omission costs no install failure.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: one clause in README.md's Requirements bullet naming threadpoolctl; no production code change.

Finding id: D6-s1-01 (round 8, baseline cdf82daa).

## D1-s1-01 -- verified, medium, bug

**Judge number:** race_reverted_live=2, race_reverted_published=2 of 2; control 0/0; --perturb 0/0

**Ruling:** Judge re-run s1_setback_race.py: race 2/2, control 0/0 (thread_factor 1.18 from the deliberate real worker thread; counts only), --perturb 0/0. Verifier's deterministic v1_setback_race.py re-run: race 2/2, control 0/0, late next-solve inputs reverted 2. Metrics comparable (both count reverted written fields live and published). Window widths (1.5 s here vs 5.8 s finder) are provisional and not relied on.

**Issue title:** [R8-D1-s1-01] set_thermal_parameters DHW minimums written during a solve are reverted by the away-setback unwind

A set_thermal_parameters call carrying dhw_min_temperature and dhw_idle_min_temperature that lands while async_run_optimization awaits its solve is applied and acknowledged, then the unconditional away.restore_setback in that method's finally writes the pre-solve values back, with away mode inactive; the harness counts 2 of 2 written fields reverted in the live params and 2 of 2 in coordinator.data, and the reverted values feed the next solve.

Evidence: tools/audit/round8/D1/s1_setback_race.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D1/s1_setback_race.py` -> RESULT race_reverted_live=2, race_reverted_published=2, control_reverted_live=0 (null control: the same call after the cycle returns); perturbation `--perturb` (away.py setback returns None, so no unwind) -> 0/0. Independent deterministic harness tools/audit/round8/D1/v1_setback_race.py (write injected at the solve await) -> race 2/2, control 0/0, late_next_solve_inputs_reverted=2. Counts only; the solve window width (1.5 s on the judge's quiet 4-vCPU box) is provisional.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/coordinator.py and away.py; restore only fields the setback or widening changed and only while they still hold the value the envelope wrote (compare-and-restore), or apply the setback to the solve snapshot instead of live ctx. The same unwind also rewrites target_temp, min_temp and comfort_temp_day/night (unmeasured). Seam rule: grep -n 'apply_setback\|restore_setback\|away_original' custom_components/heatpump_optimizer/{coordinator,away}.py

Finding id: D1-s1-01 (round 8, baseline cdf82daa).

## D1-s1-02 -- verified, low, bug

**Judge number:** service_offloop_attrs=3, button 0, cycle 0; --perturb 0; verifier torn read 1 (forced)

**Ruling:** Judge re-run s1_thread_reads.py: offloop_attrs=3 (all on the service path), button 0, --perturb 0. v1_diag_offloop.py: service 1 off-loop call on live params, 1 forced torn read; button 0/0. Finder counts attribute names, verifier counts consequences; both move to 0 under the same perturbation. Class set to bug (not hygiene): the code reads live mutable state off the loop, which the verifier showed can produce a torn diagnosis; consequence limited to a diagnostic report, so low.

**Issue title:** [R8-D1-s1-02] diagnose_interval service runs coordinator.diagnose_last_interval on the executor against live state

services.py passes the bound method coord.diagnose_last_interval to hass.async_add_executor_job, so an executor thread reads the live _ctx thermal params and _last_interval_record and writes _last_diagnosis, bypassing the deepcopy snapshot the Diagnose button path uses; the harness counts 3 private coordinator attributes touched off the loop on the service path and 0 on the button path and the solve cycle.

Evidence: tools/audit/round8/D1/s1_thread_reads.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D1/s1_thread_reads.py` -> RESULT service_offloop_attrs=3, button_offloop_attrs=0, cycle_offloop_attrs=0 (control arms); `--perturb` (handler routed through async_diagnose_interval) -> 0. Independent harness tools/audit/round8/D1/v1_diag_offloop.py (real ThreadPoolExecutor, loop write forced mid-call) -> service_offloop_live=1, service_torn=1, button 0/0; the torn read is forced, so it proves possibility, not frequency.

Final severity **low**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/services.py handle_diagnose_interval only; await coord.async_diagnose_interval() (the snapshot route) and read back its result.

Finding id: D1-s1-02 (round 8, baseline cdf82daa).

## D1-s2-01 -- weakened, medium, bug

**Judge number:** ledger_escape_rate=0.3240 (81/250); controls 0.0000; leaf-guard perturbation 0.0000 (250/250 quarantined clean); v1 cycles: 3/3 failed, 4 ERROR logs, 3/3 still actuated, first refresh ConfigEntryNotReady

**Ruling:** Judge re-ran s2_ledger_fuzz.py (0.3240, controls 0), v1_s2_perturb_runner.py (finder's from_dict leaf guard in-process: 0.0000), v1_ledger_cycles.py (corrupt 3/3 failed, null 0/3; --perturb 0). The 0.324 rate is a function of the mutator mix; the per-mutant fact is binary, so the decision rests on the cycle count. 'No log line' refuted (ERROR with traceback every cycle); actuation continues; 'forever' bounded by KEEP_MONTHS=24 for old months; trigger requires an external .storage edit or corruption; workaround: remove the bad month. Critical not earned -> medium. Shares the UpdateFailed channel with D1-s3-01 but a different loader and fix, not merged. Verifier vote weaken(medium) agrees.

**Issue title:** [R8-D1-s2-01] A non-numeric kwh/sek leaf in the persisted ledger passes MonthlyLedger.from_dict and fails every refresh cycle

MonthlyLedger.from_dict validates the ledger's structure but not its lines[*].kwh/sek leaves, so a persisted leaf such as sek='12,5' loads, then _build_data_dict raises on every refresh; with one corrupted leaf, 3 of 3 real async_refresh cycles end with last_update_success False (4 ERROR logs, entities stale) and the setup first refresh raises ConfigEntryNotReady, while actuation continues in 3 of 3 cycles because _apply_action runs first; across 250 seeded ledger mutants, 81 (0.324) escape the loader and raise in _build_data_dict.

Evidence: tools/audit/round8/D1/s2_ledger_fuzz.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D1/s2_ledger_fuzz.py` -> RESULT ledger_escape_rate=0.3240, accuracy_escape_rate=0.0000, price_model_escape_rate=0.0000 (sibling loaders that leaf-validate, a different mutator on different payloads); tools/audit/round8/D1/v1_ledger_cycles.py -> corrupt_failed_cycles=3, null_failed_cycles=0 (float leaf). Perturbation: the leaf guard in from_dict applied in-process (tools/audit/round8/D1/v1_s2_perturb_runner.py) -> escape 0.0000, 250/250 quarantined clean; v1_ledger_cycles.py --perturb -> 0 failed cycles. The 0.324 rate depends on the mutation mix; the per-leaf failure is deterministic. The integration never writes a non-float leaf, so the trigger is a hand edit or storage corruption.

Final severity **medium**, stop-rule class **bug** (judge-weakened from critical).

Proposed fix scope: custom_components/heatpump_optimizer/ledger.py MonthlyLedger.from_dict only; coerce each lines[*] kwh/sek inside try/except (TypeError, ValueError, OverflowError) and drop the month on failure, as accuracy.py, price_model.py and wear.py already do.

Finding id: D1-s2-01 (round 8, baseline cdf82daa).

## D1-s3-01 -- weakened, medium, bug

**Judge number:** async_refresh raises on 4 of 5 hostile shapes (control 0); cycle level 5 of 6 cycles fail with no actuation (control 0); finder's isinstance guard -> 1 (not 0); try/except fence -> 0

**Ruling:** Judge re-ran s3_openmeteo_hostile.py (4/5, control 0), v1_s3_perturb_runner.py (finder's stated guard: 1, the dict-with-string-time shape still raises TypeError in zip, so the finder's reported 4->0 is wrong but the direction holds), v1_openmeteo_cycle.py (5/6 failed, 0 actuated, control 0; --perturb=finder 1; --perturb=fence 0). Finder harness prints no load1/thread_factor (contract defect). Consequence (cycle loses solve and actuation) is high, but _get_json already rejects non-dict and error bodies so the trigger needs a schema-nonconformant 200 response; an immediate retry succeeds only because of the 20-minute gate. Medium. Verifier weaken(medium) agrees. Not merged with D1-s2-01 (different module and fix).

**Issue title:** [R8-D1-s3-01] A wrong-shaped Open-Meteo hourly/minutely_15 member raises out of OpenMeteoSolar.async_refresh and fails the whole cycle

OpenMeteoSolar.async_refresh documents that it never raises, but a valid-JSON body whose hourly member is a list, string, int or a dict with a non-list time raises AttributeError/TypeError out of _parse_block into _async_update_data's outer except, so the whole cycle fails as UpdateFailed; async_refresh raises on 4 of 5 hostile shapes, and at cycle level 5 of 6 malformed bodies end the cycle with last_update_success False and no actuation.

Evidence: tools/audit/round8/D1/s3_openmeteo_hostile.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D1/s3_openmeteo_hostile.py` -> RESULT cycles_crashed=4, control_crashed=0 (well-formed body); tools/audit/round8/D1/v1_openmeteo_cycle.py -> failed=5, failed_actuated=0, control_failed=0. Perturbation: the isinstance(dict) guard in _parse_block (tools/audit/round8/D1/v1_s3_perturb_runner.py) -> 1, since the dict-with-string-time shape still raises in zip; a try/except fence around async_refresh (`--perturb=fence`) -> 0. The trigger needs a schema-nonconformant 200 response, since _get_json already rejects non-dict and error bodies.

Final severity **medium**, stop-rule class **bug** (judge-weakened from high).

Proposed fix scope: custom_components/heatpump_optimizer/open_meteo.py; validate the block and the time/value sequences' types in _parse_block (returning _EMPTY) and make async_refresh keep its never-raises contract with a final except that falls back to cached irradiance.

Finding id: D1-s3-01 (round 8, baseline cdf82daa).

## D11-s1-01 -- weakened, high, bug

**Judge number:** required_skippable_edited=3 (perturb 0, null synchronize 0); history: superseded_merged_heads=3 of 15, superseded_heads=6 of 19, masked_red_heads=0; v1 ordering: 24 pairs, latest by id 18, by completed 6, race pairs 18

**Ruling:** Judge re-ran the tree arm (3, --perturb 0, null 0) and the --api arm against the live check-runs API with --clone /home/claude/heatpump_optimizer read-only (3 of 15 merged, 6 of 19 heads incl. one new open PR since the panel, masked 0), and v1_latest_order.py (24 pairs; by id 18, by started 6, by completed 6; 18 races; its null is now 1 pair, it was 0 at panel time: live data moved). The hop where the ruleset reads the latest run per name is still unprobed and no red has been masked, so critical is not earned; the precondition (3 required contexts re-created as skipped at an unchanged head by a body edit) is measured and moves under the perturbation. Verifier weaken(high) agrees.

**Issue title:** [R8-D11-s1-01] A PR body edit re-creates policy-docs, env-matrix and wave-script as skipped check runs at the unchanged head

governance.yml's `if:` guard on policy-docs, env-matrix and wave-script is false for pull_request/edited, so every PR body edit creates a new skipped check run for 3 of the 16 required contexts at the unchanged head SHA; in the live history since the guard landed, 3 of 15 merged PRs (#1484, #1485, #1488) and 6 of 19 examined heads carry a skipped run created after a real verdict for those contexts, and 0 heads have had a red masked so far.

Evidence: tools/audit/round8/D11/s1_skip_supersede.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/s1_skip_supersede.py --api --clone <full clone>` -> RESULT required_skippable_edited=3, null_synchronize_skipped=0 (control event), superseded_merged_heads=3, superseded_heads=6, heads_examined=19, masked_red_heads=0; perturbation `--perturb` (the three edited guards removed in a temp copy) -> 0. tools/audit/round8/D11/v1_latest_order.py -> 24 same-head pairs, the skipped run is latest by check-run id in 18, by completed_at in 6; 18 are races where the edited event fires seconds after opened. Whether the ruleset grades the latest run per name by creation order was not probed, so masking is plausible, not demonstrated.

Final severity **high**, stop-rule class **bug** (judge-weakened from critical).

Proposed fix scope: .github/workflows/governance.yml; move pr-contract into its own workflow on pull_request [opened, edited, synchronize, reopened] and drop `edited` from the workflow that runs the other three, so a body edit dispatches no run of them; treat tests.yml closure-scope under workflow_dispatch the same way. Probe latest-wins in a sandbox repository first.

Finding id: D11-s1-01 (round 8, baseline cdf82daa).

## D11-s1-02 -- merged, medium, bug

**Judge number:** uncovered_surface=14 of 51 (3 exec, 2 import, 9 data); --perturb 13; null (round-6 interpreter-only rule) 37/0

**Ruling:** Judge re-ran s1_owner_surface.py (14, --perturb 13, null 0). Same mechanism as D11-s2-01: the round-6 codeowners_gap derivation counts only interpreter-form invocations and never follows imports or data reads. D11-s2-01 carries the stronger measurement (a dynamic flip of pr-contract, 3 of 3, null 1). Of s1-02's 14, coverage_tree.sh carries no verdict (non-required job, || true) and closures.json plus both claim files are written by the autofix bots by design, so the extra data-file arm is folded into D11-s2-01's fix scope as the budget files and policy_known_bad.json (5 flipping files per v1_owner_flip.py).

## D11-s1-03 -- verified, low, bug

**Judge number:** blind_states=2 of 4 (perturb 0, null 0); v1: 3 of 6

**Ruling:** Judge re-ran s1_stop_hook_states.py (2/4, --perturb 0, null 0) and v1_stop_index.py (3 of 6; the extra untracked_new state is moot because policy_lint reads its corpus via git ls-files). CI policy-docs still refuses, so low.

**Issue title:** [R8-D11-s1-03] stop-selfcheck.sh ends a turn on a red policy corpus when the policy change is only staged

The Stop hook's CHANGED set unions BASE...HEAD and the unstaged worktree diff but never the index, so against a policy linter that exits 1 the real hook exits 0 in 2 of 4 policy-touching states (a staged modification and a staged new policy file).

Evidence: tools/audit/round8/D11/s1_stop_hook_states.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/s1_stop_hook_states.py` -> RESULT blind_states=2 of states=4, null_red_exits=0 (green linter stub: all states exit 0); perturbation `--perturb` (git diff --cached added to CHANGED in a temp copy) -> 0. tools/audit/round8/D11/v1_stop_index.py over 6 states -> 3 blind, 2 of them the finder's; the untracked-new state is moot since the linter reads git ls-files. CI's policy-docs and pr-contract still refuse the red corpus later.

Final severity **low**, stop-rule class **bug** (judge-verified).

Proposed fix scope: .claude/hooks/stop-selfcheck.sh; add `git diff --cached --name-only` to CHANGED and one staged case to the hook's end-to-end self-test.

Finding id: D11-s1-03 (round 8, baseline cdf82daa).

## D11-s2-01 -- verified, high, bug

**Judge number:** unowned_required_closure=8; pr_contract_flips=3 of 3 (unperturbed rc 1, unloaded-file null rc 1); --extra-owner x8 -> 0; v1: 5 unowned files flip a required context, owned-loaded null rc 1

**Ruling:** Judge re-ran s2_owner_closure.py (8, flips 3/3, null 1), --no-dynamic with all 8 --extra-owner (0), and v1_owner_flip.py (18 candidates, 5 flipping, null 1, owned file flip rc 1, tree clean). D11-s1-02 merged here (same derivation defect, weaker static measurement). The flip is not an artefact of any append: an owned loaded file and an unloaded file both stay at rc 1.

**Issue title:** [R8-D11-s2-01] Required checks run PR-editable code no CODEOWNERS pattern owns; a one-line edit turns pr-contract green

Required-context jobs execute 8 tracked files from the pull request's own checkout that no CODEOWNERS pattern owns (counts.mjs, render_md.mjs, vendor/markdown-it.min.js, tests/run.sh, tests/derive_closures.sh, tests/golden.py, tests/harness.py, tests/profiles.py), and a one-line append to any of the 3 that policy_lint.mjs loads turns pr-contract's refusal of an empty body from rc=1 to rc=0; across both finders' 18 candidates, 5 unowned files (the 3 loaders, policy_known_bad.json and tests/run.sh) flip a required context by a one-line edit, so those checks change on the hpo-approver App's review alone although CODEOWNERS says the enforcement surface is owner-owned. Cause: round 6's codeowners_gap.py counts a script only when invoked through an interpreter and never follows imports or data reads; pr-contract and briefs, unlike policy-docs, do not restore their check source from base.

Evidence: tools/audit/round8/D11/s2_owner_closure.py, command `PYTHONPATH=tests/hastub TMPDIR=<private> python3 tools/audit/round8/D11/s2_owner_closure.py` -> RESULT unowned_required_closure=8, pr_contract_flips=3 of 3, null_control_unloaded_file_rc=1 (append to a file policy_lint.mjs does not load); perturbation `--extra-owner` for the 8 paths -> 0. tools/audit/round8/D11/v1_owner_flip.py -> unowned_flipping=5, owned_loaded_flip_rc=1, null_unloaded_rc=1, tree clean after. Merged here: D11-s1-02 (tools/audit/round8/D11/s1_owner_surface.py, 14 of 51 surface files unowned including data files; --perturb -> 13; round-6 rule null 0), of which coverage_tree.sh carries no verdict and the closure/claim files are bot-written by design.

Final severity **high**, stop-rule class **bug** (judge-verified).

Proposed fix scope: .github/workflows/governance.yml and tests.yml (pr-contract and briefs restore .claude/workflows/{*.mjs,*.py,vendor} from the base SHA before grading, as policy-docs does); .github/CODEOWNERS lines for tests/run.sh, tests/derive_closures.sh, counts.mjs, render_md.mjs, vendor/, policy_known_bad.json and the budget files; extend codeowners_gap.py to bare ./ invocations, a transitive import walk and verdict data reads.

Finding id: D11-s2-01 (round 8, baseline cdf82daa).

## D11-s2-02 -- verified, high, bug

**Judge number:** off_main_published=2 of 2 (perturb 0 of 2); on_main_published=2 of 2 both arms; live tag_rulesets=0, controls=0

**Ruling:** Judge re-ran s2_release_gate.py (2/2 off-main, 2/2 on-main control) and --perturb (0/2 off-main, 2/2 on-main), and v1_release_controls.py (live unauthenticated rulesets read: 0 tag rulesets, 0 controls, 1 name refusal). The provisional tag-push hop is closed by the absence of a tag ruleset.

**Issue title:** [R8-D11-s2-02] release.yml publishes and attests a v* tag or dispatch ref at a commit that is not on main

release.yml's release job, executed step by step in a scratch clone, reaches gh release create and the attested tree digest for an unmerged branch commit in 2 of 2 event paths (tag push and workflow_dispatch), as it does for a commit on main; its only refusal is the vN.N.N tag-name shape, and the live repository has 0 tag-targeted rulesets, so any contents:write identity (hpo-author's token included) can publish unreviewed code as a HACS release under a valid-looking attestation.

Evidence: tools/audit/round8/D11/s2_release_gate.py, command `PYTHONPATH=tests/hastub TMPDIR=<private> python3 tools/audit/round8/D11/s2_release_gate.py` -> RESULT off_main_published=2 of 2, on_main_published=2 of 2 (control); perturbation `--perturb` (merge-base --is-ancestor against origin/main in the Resolve-the-tag step) -> off_main 0 of 2, on_main 2 of 2. tools/audit/round8/D11/v1_release_controls.py (live GET of rulesets, unauthenticated) -> tag_rulesets=0, controls=0, name_refusals=1. Dispatch-path permissions were not measured; the tag path suffices.

Final severity **high**, stop-rule class **bug** (judge-verified).

Proposed fix scope: .github/workflows/release.yml (an ancestry refusal as the first step, one line) plus a v* tag ruleset limited to the deploy key.

Finding id: D11-s2-02 (round 8, baseline cdf82daa).

## D11-s2-03 -- verified, low, hygiene

**Judge number:** pinned_deps_unpinned=12 (perturb 11); uses_unpinned=0

**Ruling:** Judge re-ran s2_scorecard.py (12, --perturb 11). Verifier's all-workflow shlex tokeniser agrees (12, all in tests.yml; 1 command with no version pins at all, the typing venv). Hardening gap, not a broken check.

**Issue title:** [R8-D11-s2-03] 12 CI install commands in tests.yml are version-pinned but not hash-pinned

Under Scorecard's Pinned-Dependencies definition, 12 install commands in tests.yml are unpinned: 9 `pip install -r requirements-ci.txt` with no hashes, the typing venv install (5 names with no version at all), `pip install coverage==7.13.1`, and the playwright npm install/npx; every uses: ref is SHA-pinned (0 unpinned).

Evidence: tools/audit/round8/D11/s2_scorecard.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D11/s2_scorecard.py` -> RESULT pinned_deps_unpinned=12, uses_unpinned=0 (control); perturbation `--perturb` (--require-hashes on one pip -r line) -> 11. tools/audit/round8/D11/v1_pins.py over every workflow -> 12 unhashed, 1 without version pins.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: tests/requirements-ci.txt as a hashed lock (pip-compile --generate-hashes), version pins for the typing venv, npm ci over a lockfile for the playwright lane in .github/workflows/tests.yml.

Finding id: D11-s2-03 (round 8, baseline cdf82daa).

## D2-s1-01 -- verified, medium, bug

**Judge number:** gap_max=4.9717 K (min cell 3.2716, LOO 4.8884, 6 cells); nulls 0.0000; --ambient-matches 0.0000; v1 published shortfall 4.4088 K (LOO 3.7823)

**Ruling:** Judge re-ran s1_dhw_humidity.py on a clean tree (a first run overlapped the judge's own on-disk D0 ftol perturbation and was discarded; the clean re-run gave identical numbers) and v1_dhw_humidity.py (published-vs-published shortfall 4.41 K, LOO 3.78, 8 of 8 cells below dhw_min, reverse arm over-buys 0.79 kWh, null 0). Finder measures plan-model vs published gap; verifier measures consequence between two published trajectories; different metrics, same direction, both LOO > 3.7 K.

**Issue title:** [R8-D2-s1-01] The DHW planner prices COP at the current humidity, not the forecast; published DHW runs up to 4.4 K below the correct plan

With a learned humid-bucket defrost derate and a humidity forecast of 85-95 % against a current reading of 55 %, the optimizer's DHW planning seams (extend_dhw_temps / simulate_dhw_only and the compute_cop_dhw / marginal_cop('dhw') calls) evaluate COP with humidity=None and so use the current reading, while the physics uses the forecast: the optimizer's own DHW schedule re-simulated through simulate_dhw_only deviates from the published dhw_temp_trajectory by up to 4.97 K (6 cells, min 3.27 K, most favourable cell dropped 4.89 K), and the published trajectory runs up to 4.41 K below the one planned with correct humidity (most favourable cell dropped 3.78 K), 0.1-0.8 kWh of DHW electricity under-bought.

Evidence: tools/audit/round8/D2/s1_dhw_humidity.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s1_dhw_humidity.py` -> RESULT gap_max=4.9717 K, gap_drop_most_favourable=4.8884 K, null_forecast_equals_ambient=0.0000, null_no_derate=0.0000; perturbation `--ambient-matches` -> gap_max 0.0000 in 6 of 6 cells. tools/audit/round8/D2/v1_dhw_humidity.py (published vs published) -> shortfall_max=4.4088 K, drop_most_favourable 3.7823 K, reverse arm (humid now, dry forecast) over-buys 0.7927 kWh, null 0.0000. A diurnal 60-95 % forecast gives 0.65-2.85 K. Re-solved every cycle, so the error is bounded to the forecast/current humidity split.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/thermal_model.py (an optional per-step humidity array in extend_dhw_temps / simulate_dhw_only) and optimizer.py (pass h.humidity at every DHW COP seam). Seam rule: grep -nE 'compute_cop(_dhw)?\(|marginal_cop\(' custom_components/heatpump_optimizer/optimizer.py custom_components/heatpump_optimizer/thermal_model.py | grep -v humidity; coordinator._capacity_caps follows the same pattern, unmeasured.

Finding id: D2-s1-01 (round 8, baseline cdf82daa).

## D2-s1-02 -- verified, low, bug

**Judge number:** ratio_max=1.4548; 102 of 105 cells >1.01; boost_below_ref 1.12; 55 C warm/cold 1.4286 vs 1.2500; --perturb 1.0000 / 0 cells; null at 35 C 0

**Ruling:** Judge re-ran s1_cop_laws.py and --perturb (class-attribute swap, restored). The finder's 105 cells collapse to 39 distinct values because the ratio is independent of cop_nominal, so the LOO is uninformative; verifier's 364-cell grid (358 > 1.05, min 1.039) holds the claim. Reachable only with cop_flow_carnot on plus DHW; plan and physics share compute_cop_dhw, so this is model accuracy, low.

**Issue title:** [R8-D2-s1-02] With cop_flow_carnot on, the DHW tank is priced up to 45 % more efficient than a buffer at the same water temperature

With cop_flow_carnot enabled, marginal_cop(o,'dhw',T) / marginal_cop(o,'buffer',T) exceeds 1.01 in 102 of 105 cells (tank 40-70 C, outdoor -15..12 C), with a maximum of 1.4548 at 70 C / 7 C, because compute_cop_dhw keeps its own lift penalty instead of flow_lift_factor; it also grants a 1.12x boost below the 35 C reference that the buffer law refuses, and at 55 C the DHW law's warm/cold advantage is 1.4286 against the Carnot law's 1.2500.

Evidence: tools/audit/round8/D2/s1_cop_laws.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s1_cop_laws.py` -> RESULT ratio_max=1.4548, cells_ratio_gt_1_01=102, boost_below_ref=1.1200, null_at_reference_flow=0.000000 (35 C control); perturbation `--perturb` (dhw_penalty = flow_lift_factor, class-attribute swap restored in finally) -> 1.0000, 0 cells, boost 1.0000. The 105 cells are 39 distinct values (the ratio is independent of cop_nominal); tools/audit/round8/D2/v1_cop_laws.py over 364 cells -> max 1.4548, min 1.039, 358 cells > 1.05. Plan and physics share compute_cop_dhw, so this is model accuracy, not a plan/physics split.

Final severity **low**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/thermal_model.py; behind cop_flow_carnot derive the DHW penalty from flow_lift_factor plus an optional coil-approach delta that can only lower COP, and decide whether a tank below 35 C earns a boost in both laws or neither. Seam rule: grep -nE 'def (compute_cop_dhw|flow_lift_factor|_batch_cop|marginal_cop)|dhw_penalty' custom_components/heatpump_optimizer/thermal_model.py

Finding id: D2-s1-02 (round 8, baseline cdf82daa).

## D2-s2-01 -- verified, high, bug

**Judge number:** headline_overbill_sek=96.3667/month (billed_peak_kw 9.80 vs 7.83; threshold 9.60 vs 6.50); grid 8/8 nonzero, 1.421-34.401, mean 19.114, LOO 16.930; plan ratio 3.0; --k1 all 0 / 1.0

**Ruling:** Judge re-ran s2_distinct_day_peaks.py and --k1 (exact). Headline is a constructed cold morning; the grid mean and its leave-one-out (16.93 SEK/month) carry the decision. Verifier's seeded-month harness (hidden SEK median 76.66, 20/20 months) is an upper bound on a different metric. The wrong published billed_peak_kw earns high.

**Issue title:** [R8-D2-s2-01] PeakTracker averages the top-k metering windows, not the top-k days the capacity tariff bills

tariff.PeakTracker keeps one flat sorted list of the k highest metering windows regardless of day, while both catalog rows bill the mean of the three highest peaks on three different days; a cold morning with three high hours publishes billed_peak_kw 9.80 kW against a true 7.83 kW (+96.37 SEK/month at 49 SEK/kW) and a threshold_kw of 9.60 kW against a true 6.50 kW, so a 9.0 kW hour on another day is priced free by the solver and the live guard while the bill charges 40.83 SEK for it; over an 8-cell grid of months the overbill is 1.42-34.40 SEK/month, mean 19.11, 16.93 with the most favourable cell dropped, nonzero in 8 of 8.

Evidence: tools/audit/round8/D2/s2_distinct_day_peaks.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s2_distinct_day_peaks.py` -> RESULT headline_overbill_sek=96.3667, tracker_threshold_kw=9.6000 vs true 6.5000, grid_overbill_mean_sek=19.114, grid_overbill_mean_drop_max_sek=16.930, grid_cells_nonzero=8, plan_overcharge_ratio=3.0000; null/perturbation `--k1` (peaks_averaged 1, where top window equals top day) -> 0.0000 everywhere, ratio 1.0000. tools/audit/round8/D2/v1_peak_days.py (20 seeded months) -> hidden SEK median 76.66/month, an upper bound because it prices whole-house load.

Final severity **high**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/tariff.py; keep one entry per local day behind a distinct-days flag set by the catalog rows, read billed_peak_kw and threshold_kw from the per-day list, and make peak_cost / peak_cost_smooth / peak_cost_batch take per-day maxima of the plan windows. Seam rule: grep -n 'def _close_window\|def billed_peak_kw\|def threshold_kw\|def peak_cost' custom_components/heatpump_optimizer/tariff.py. Capacity goldens may drift.

Finding id: D2-s2-01 (round 8, baseline cdf82daa).

## D2-s2-02 -- verified, high, bug

**Judge number:** import ratio 1.0000 / 83.0147 / 828.6029 (SEK/kWh, öre/kWh, SEK/MWh); export 1/100/1000; fee share 0.13228 -> 0.00152 / 0.00015; judge production-side unit conversion -> import 1.0000 in all three, export unchanged

**Ruling:** Judge re-ran s2_price_unit.py (exact). Because the finder's perturbation is an input attribute, the judge added a production-side perturbation (tools/audit/round8/D2/judge_price_unit_fix.py: prices_from_entity_state converts by unit_of_measurement, in-process): import ratios -> 1.0000 for all units, export stays 100/1000, proving _pv_export_price is a second independent seam. Verifier's plan-level arm (+5.4 kWh winter_mild, published cost 100x) shows the objective is not price-scale-invariant.

**Issue title:** [R8-D2-s2-02] Entity price sources are read unit-blind: öre/kWh and SEK/MWh prices reach the plan at 83x and 829x

price_model.prices_from_entity_state and Coordinator._pv_export_price never read the sensor's unit, so a Nord Pool sensor in öre/kWh (price_in_cents) or SEK/MWh reaches Coordinator._price_series at 83.01x / 828.60x the true SEK/kWh and the export price at 100x / 1000x, while the grid fee stays in SEK, shrinking the fee's share of the price spread from 0.13228 to 0.00152 / 0.00015; the verifier measured the plan moving +5.4 kWh (+17 %) on a winter_mild day and the published predicted cost at 100x.

Evidence: tools/audit/round8/D2/s2_price_unit.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D2/s2_price_unit.py` -> RESULT ratio_SEK_per_kWh=1.0000 (null), ratio_ore_per_kWh=83.0147, ratio_SEK_per_MWh=828.6029, export ratios 1 / 100 / 1000. Production-side perturbation tools/audit/round8/D2/judge_price_unit_fix.py (prices_from_entity_state converts by unit_of_measurement, in-process) -> import ratios 1.0000 for all three units, export unchanged at 100 / 1000, so the export read is a second seam. tools/audit/round8/D2/v1_price_unit.py -> plan +5.43 kWh winter_mild, +2.03 kWh shoulder, identical when capacity-bound, published cost 100.000x. The VAT multiplier cannot scale by 1/1000 or fix the export seam.

Final severity **high**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/price_model.py and coordinator.py; convert by unit_of_measurement / price_in_cents (0.01 per öre or cent, 0.001 per MWh) in one helper used by prices_from_entity_state, _pv_export_price and the grid-fee entity read, and refuse an unknown unit with a repair. Seam rule: grep -n 'def prices_from_entity_attributes\|def prices_from_entity_state\|def _pv_export_price\|def _grid_fee_entity_value' custom_components/heatpump_optimizer/price_model.py custom_components/heatpump_optimizer/coordinator.py

Finding id: D2-s2-02 (round 8, baseline cdf82daa).

## D8-s1-01 -- weakened, low, bug

**Judge number:** finite_call_count climate/switch/binary_sensor/datetime 0 each vs sensor 6; with the harness's ImportError fallback climate_leaks_nonfinite=1; with real orjson 3.12.0 on the path climate_leaks_nonfinite_nan=0 and _inf=0 (orjson writes NaN/Inf as null)

**Ruling:** orjson is not installed in the audit environment, so s1_finite_boundary.py fell back to a stub that counts any non-finite float as a serialisation failure. The judge installed orjson 3.12.0 into a private --target dir: orjson.dumps({'a':nan,'b':inf}) -> {"a":null,"b":null}, and the harness then reports climate_leaks 0/0. The claimed consequence (fails orjson serialisation) is refuted with a number; the structural asymmetry (4 platforms publish raw non-finite floats in-process, where a Jinja template sees inf, while sensor.py scrubs to None, the exact two-meanings defect sensor.py's _finite docstring names) holds. No producer path that puts a non-finite value under a key those platforms read was demonstrated. High -> low. Verifier verify(high) rested on the same fallback and is not comparable on the consequence.

**Issue title:** [R8-D8-s1-01] Only the sensor platform scrubs non-finite floats; climate, switch, binary_sensor and datetime publish raw NaN/Inf in-process

HeatPumpOptimizerSensorBase.__init_subclass__ wraps every sensor's native_value and extra_state_attributes in the _finite scrub, but HeatPumpOptimizerEntity, the base every platform shares, has none: with coordinator.data['current_price'] set to NaN or Inf, the climate entity's extra_state_attributes returns the raw non-finite float while CurrentPriceSensor returns None, and the scrub is called 0 times on climate, switch, binary_sensor and datetime against 6 on sensor. Real orjson (3.12.0) serialises NaN/Inf as null, so the wire and recorder see null; the defect is the in-process value a template reads (inf compares `> 100` as true), the divergence sensor.py's own _finite docstring was written to close.

Evidence: tools/audit/round8/D8/s1_finite_boundary.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D8/s1_finite_boundary.py` -> RESULT climate_finite_call_count=0, switch 0, binary_sensor 0, datetime 0, sensor_finite_call_count=6, null_control_ok=1 (finite 0.73 round-trips through both); the harness's climate_leaks_nonfinite=1 comes from its ImportError fallback, and with real orjson on PYTHONPATH it is 0 for NaN and Inf. No production path that writes a non-finite value under a key these platforms read was demonstrated.

Final severity **low**, stop-rule class **bug** (judge-weakened from high).

Proposed fix scope: custom_components/heatpump_optimizer/entity.py; move the _finite scrub (the __init_subclass__ hook) from sensor.py's base onto HeatPumpOptimizerEntity so every platform publishes through one boundary.

Finding id: D8-s1-01 (round 8, baseline cdf82daa).

## D8-s2-01 -- refuted, none, hygiene

**Judge number:** finder: 57 source-order position mismatches (static AST/text read of sensor.py); v1_ordering_refute.py on 59 real constructed entity_ids: family_splits_when_actually_sorted=0, sort_invariant_to_construction_order=1

**Ruling:** Judge re-ran both. The finder's number is read from the Python list literal in async_setup_entry against translation_key order, a code-reading metric the contract does not accept as evidence, and it has no runtime path to a user (HA and the card do not order by registration). Sorting the real entity_id strings clusters every family with 0 splits, independent of construction order. Refuted with a number, matching the verifier's refute.

## D8-s2-02 -- weakened, low, bug

**Judge number:** judge runtime re-measure: dhw_temperature_hidden_live=1 with a configured tank thermometer (control without probe 0); --perturb (static default removed, mixin default applies) 0

**Ruling:** The finder's harness is a static code read whose stated direction (up) does not match its own perturbation, so the judge replaced it with tools/audit/round8/D8/judge_probe_default.py driving the real sensor.async_setup_entry. With hot water and dhw_temp_entity configured and reading OK, DHWTemperatureSensor is available with a live value yet default-disabled (1); without the probe it is correctly off (0, the #1335 case); removing the static default lets the _DHWEntityMixin default apply (0). The card's overlayDhwDisplay guards probe != null, so the consequence is a missing live tank-temperature point on the card, not a failure. Medium -> low. Verifier weaken(low) agrees on severity.

**Issue title:** [R8-D8-s2-02] The tank temperature sensor stays disabled by default on installs that configure a tank thermometer, hiding the card's live probe point

DHWTemperatureSensor sets a static _attr_entity_registry_enabled_default = False (#1335, for installs with no tank thermometer), which also applies where dhw_temp_entity is configured and reads OK, so on a fresh install with a tank probe the entity is available with a live value but disabled, and the card's overlayDhwDisplay (probe: statNumber('_dhw_temperature')) drops the live tank point; the runtime count is 1 hidden live probe entity with a configured thermometer and 0 without one.

Evidence: tools/audit/round8/D8/judge_probe_default.py (judge re-measure through the real sensor.async_setup_entry, coord_dhw scenario), command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D8/judge_probe_default.py` -> RESULT dhw_temperature_hidden_live=1, control_dhw_temperature_hidden=0 (no probe configured); perturbation `--perturb` (static default removed in-process, so the _DHWEntityMixin default follows dhw_enabled) -> 0. The finder's tools/audit/round8/D8/s2_enabled_analysis.py reads the flag from source and is not an executed number. The card guards probe != null, so it degrades to the plan series.

Final severity **low**, stop-rule class **bug** (judge-weakened from medium).

Proposed fix scope: custom_components/heatpump_optimizer/sensor.py DHWTemperatureSensor; make the registry default follow whether dhw_temp_entity is configured (read from the config entry, as _DHWEntityMixin reads dhw_enabled) instead of a static False.

Finding id: D8-s2-02 (round 8, baseline cdf82daa).

## D13-s1-01 -- weakened, low, hygiene

**Judge number:** reverify->merge=15 of extra_rounds=20 (repair 3, duplicate 2); one_round_yield=0.8125 vs first_pass_yield=0.963; prod_head_moved_entries=19; LOO 12 PR cells, drop max 13; --pin-head 1375 -> 14 / 18

**Ruling:** Judge rebuilt the window from a private API cache (s1_window.py: 88 merges, 532 uncached calls, 0 failures) and re-ran s1_yield.mjs and --pin-head 1375 (15 -> 14, head-moved 19 -> 18) and --reshape 1493. Exact reproduction. The verifier's patch-id classification (14 of 15 re-verified a changed authored diff, which orchestrator.md s11 mandates; 1 byte-identical, #1433) and the null (first-round block rate 0.0375 predicts 0.56 blocks in 15 rounds, P(0)=0.57) mean the rounds are not shown wasteful. Production already prints the head-moved row (round 6 landed REWORK_CLASS). What survives is a reporting defect: statsHistogram lumps re-verification with repair and reports only first-verdict yield. Medium -> low; class hygiene (a metric's presentation, no wrong behaviour).

**Issue title:** [R8-D13-s1-01] statsHistogram reports first-verdict yield 0.963 while one-round yield is 0.8125; its head-moved row lumps 15 re-verifications with 3 repairs

Over the 88-merge window c310541..cdf82da, 80 merges carry a verdict and 20 verdicts follow a first one: 15 re-verified a head that moved after a merge verdict (all returned merge), 3 were repairs after a block and 2 duplicates; statsHistogram's first-pass yield of 0.963 counts as first-pass 12 merges reviewed two or three times, and the one-round yield is 0.8125, while its head-moved row (19) does not separate re-verification from repair.

Evidence: tools/audit/round8/D13/s1_window.py then tools/audit/round8/D13/s1_yield.mjs, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/s1_window.py && node tools/audit/round8/D13/s1_yield.mjs --window <window.json>` -> RESULT extra_rounds_by_cause reverify->merge 15, repair->merge 3, one_round_yield=0.8125, first_pass_yield=0.963, prod_head_moved_entries=19, reverify_loo 12 cells, drop max 13; perturbation `--pin-head 1375` -> 14 and 18. tools/audit/round8/D13/v1_rework.py -> 14 of 15 re-verified a changed authored diff (s11 requires them), 1 byte-identical (#1433); null: a first-round block rate of 0.0375 predicts 0.56 blocks in 15 rounds, so zero observed (P = 0.57) does not show the rounds wasted.

Final severity **low**, stop-rule class **hygiene** (judge-weakened from medium).

Proposed fix scope: .claude/workflows/policy_lint.mjs statsHistogram (--stats) only; print re-verification rounds separately from repair rounds and one-round yield beside first-verdict yield. Any change to the re-verification rule itself is the owner's call.

Finding id: D13-s1-01 (round 8, baseline cdf82daa).

## D13-s1-02 -- verified, medium, bug

**Judge number:** no_verdict=8 of 88; owner-approved 8/22 vs app-approved 0/66; --reshape 1493 -> 9 (app arm 1/66), verdict_prs 80 -> 79

**Ruling:** Judge re-ran on its own API cache: 8/22 vs 0/66 exact; perturbation moves up as stated. The verifier's code-owned-files split (8/31 vs 0/57) and inline-comment endpoint agree. The 0/66 arm is enforced by app_approve.sh ('REFUSE: no Fix review verdict at all'), so it is a mechanism, not an independent baseline; it confirms the only verdict check sits on the path code-owned PRs never take. Side claim (2 merged heads without a merge verdict at them) is 1 real (#1426) per the verifier's patch-id check.

**Issue title:** [R8-D13-s1-02] Owner-approved merges skip the fix-review verdict: 8 of 22 carry none, against 0 of 66 app-approved

8 of the 88 merges in window c310541..cdf82da carry no `Fix review: merge|blocked` first line on any endpoint, and all 8 went through the owner-approval path (8 of 22 owner-approved merges, against 0 of 66 hpo-approver merges), although orchestrator.md s11 requires a merge verdict at the merged head and no rule exempts the code-owned class; 3 of the 8 (#1445, #1423, #1439) are fix-class and touch tests/mutation_table.py, tests/closure.py and policy_lint.mjs.

Evidence: tools/audit/round8/D13/s1_window.py then tools/audit/round8/D13/s1_yield.mjs, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D13/s1_window.py && node tools/audit/round8/D13/s1_yield.mjs --window <window.json>` -> RESULT no_verdict=8, owner-approved 8 of 22 (#1445, #1442, #1423, #1439, #1436, #1430, #1358, #1362), app-approved 0 of 66 (control arm, enforced by tools/audit/app_approve.sh's refusal); perturbation `--reshape 1493` -> no_verdict 9, production statsHistogram verdict_prs 80 -> 79. tools/audit/round8/D13/v1_coverage.py -> 8 by code-owned files (8 of 31 vs 0 of 57), no verdict in inline review comments. Of the 2 merged heads with no merge verdict at them, 1 (#1426) changed content after its verdict; #1444's authored diff is byte-identical.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: policy, the owner decides: either make the code-owned merge path require a verdict (a check beside the owner review), or write a rule that exempts the owner-approved class and cite it beside the coverage row.

Finding id: D13-s1-02 (round 8, baseline cdf82daa).

## D10-s1-01 -- verified, low, hygiene

**Judge number:** qs_entry_param_bare=3 (AST); after one-site fix 2; regress 4; verifier's text scan 4 (adds config_flow.py:2911 PEP 604 union return the AST helper cannot see)

**Ruling:** Judge re-ran s1_entry_param_bare.py: 3, fix 2, regress 4. quality_scale.yaml:197 states qs_entry_param_bare=0. The true count is at least 3 and 4 by the verifier's broader scan; the two config_flow OptionsFlow sites may be HA-forced signatures, which the fix must decide.

**Issue title:** [R8-D10-s1-01] quality_scale.yaml states qs_entry_param_bare=0; 3 to 4 annotations use the bare ConfigEntry

The strict-typing row of quality_scale.yaml says every entry parameter is typed with HeatPumpOptimizerConfigEntry (qs_entry_param_bare=0), but 3 parameter/return annotations resolve to the bare ConfigEntry (diagnostics.py:119 and two OptionsFlow-dispatch signatures in config_flow.py), and a text scan finds a 4th at config_flow.py:2911 (`config_entries.ConfigEntry | None`, a PEP 604 union the AST helper does not walk).

Evidence: tools/audit/round8/D10/s1_entry_param_bare.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D10/s1_entry_param_bare.py` -> RESULT qs_entry_param_bare=3, qs_entry_param_bare_after_fix=2 (diagnostics.py site typed with the alias), qs_entry_param_bare_after_regress=4; tools/audit/round8/D10/v1_entry_param_bare_regex.py -> 4. No null control applies to a source count.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/diagnostics.py (use the alias), config_flow.py (alias where HA's signature allows, a recorded exemption where it does not), and the quality_scale.yaml comment's count.

Finding id: D10-s1-01 (round 8, baseline cdf82daa).

## D10-s1-02 -- verified, low, hygiene

**Judge number:** qs_exception_raise_missing_translation=4 of 25 (coordinator.py:1211, 4581, 4631, 5601); fix 3; regress 5

**Ruling:** Judge re-ran s1_exception_translations.py: 25 total, 4 missing, fix 3, regress 5. Verifier's independent regex scan: the same 4 lines. The UpdateFailed text is shown in logs and the integration card, untranslated.

**Issue title:** [R8-D10-s1-02] 4 of 25 exception raise sites omit translation_domain/translation_key although quality_scale.yaml claims all carry them

quality_scale.yaml's exception-translations row says every raise site carries translation_domain and translation_key, but 4 of the 25 HomeAssistantError-family raise sites, all `raise UpdateFailed(...)` in coordinator.py (lines 1211, 4581, 4631, 5601: the Tibber outage latch and the generic update-failure wrappers), carry neither.

Evidence: tools/audit/round8/D10/s1_exception_translations.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D10/s1_exception_translations.py` -> RESULT qs_exception_raise_total=25, qs_exception_raise_missing_translation=4; perturbation adding the keys at the outage-latch site -> 3, regress -> 5. tools/audit/round8/D10/v1_exception_translation_regex.py (text scan) -> the same 4 lines. No null control applies to a source count.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/coordinator.py (4 raise sites) plus matching strings.json, translations/en.json and sv.json exception entries; correct the quality_scale.yaml comment if any site is exempted.

Finding id: D10-s1-02 (round 8, baseline cdf82daa).

## D10-s2-01 -- refuted, none, hygiene

**Judge number:** finder: 515 mypy --strict errors with tests/hastub on the path; finder's perturbation 515 -> 515 (inert, harness void); verifier: 457 of 515 (88.7 %) stub cascade; repository's pinned stub-free typing ruler at the baseline: census errors budget 0, CI job 'typing' at cdf82daa success ('errors did not grow', 'ALL 8 typing-ruler checks PASSED')

**Ruling:** The finder's perturbation does not move (void). The repository's own ruler, tests/typing_ruler.py, refuses exactly this measurement (construction guard: error lines inside tests/hastub). The pinned, stub-free mypy --strict census with homeassistant-stubs 2026.2.3 is recorded at errors=0 in tests/typing_budgets.json, and the baseline's 'typing' check run (job 107333392110, read through the GitHub MCP tool) passed its ratchet against that 0. Refuted with the CI number; the 515 is an artefact of running mypy against an untyped test double.

## D3-s1-02 -- weakened, low, bug

**Judge number:** distinct_keys=4 over 4 capture-equivalent environments; null_equal=1; capture_reads=0; --perturb (HPO_ dropped from CACHE_ENV_PREFIXES) -> 1

**Ruling:** Judge re-ran s1_cachekey.py and --perturb (4 -> 1, null holds, 0 HPO_* reads). CI never sets HPO_GATE_LOCK_LABEL, so CI cache hits are unaffected; the cost is local/audit-box re-captures only, with no correctness impact. The finder's 23-minute miss (load1 ~23) and the verifier's 169 s (load1 ~2) are provisional and the judge did not re-time a cold capture. Medium -> low. Verifier weaken(low) agrees.

**Issue title:** [R8-D3-s1-02] env_drift's cache key hashes HPO_* variables no capture reads, so every locked or HPO_PLANDATA-setting run re-captures

tests/env_drift.py:cache_key includes every HPO_-prefixed environment variable, so environments that differ only in HPO_PLANDATA (required by the harness contract) or HPO_GATE_LOCK_LABEL / HPO_GATE_FLOCK_CHILD (set by tests/run.sh on the locked path) give 4 distinct keys for 4 capture-equivalent environments, while a full capture reads 0 HPO_* names; each locked gate run and each contract-following harness therefore pays a byte-identical cold re-capture (169 s at load1 ~2 on a 4-vCPU box, provisional).

Evidence: tools/audit/round8/D3/s1_cachekey.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s1_cachekey.py` -> RESULT distinct_keys=4, null_equal=1 (clean environment twice), capture_reads=0; perturbation `--perturb` (HPO_ dropped from CACHE_ENV_PREFIXES) -> distinct_keys=1. tools/audit/round8/D3/v1_cachekey.py (production CLI per arm) -> 4 of 4 HPO-only arms split, positive control OMP_NUM_THREADS=2 splits. CI sets no lock label, so CI hits are unaffected; the cost is local and audit-box time only.

Final severity **low**, stop-rule class **bug** (judge-weakened from medium).

Proposed fix scope: tests/env_drift.py; replace the blanket HPO_ prefix with the HPO_* names a capture reads (none today), or exclude the gate-lock and plan-data names, and pin it with a check that setting HPO_GATE_LOCK_LABEL leaves cache_key unchanged.

Finding id: D3-s1-02 (round 8, baseline cdf82daa).

## D7-s1-01 -- verified, medium, bug

**Judge number:** sysid_contaminated_ingest=4 of 4 (house heat-loss learner 0 of 4; clean arm 1); --perturb (freeze guard) -> 0; v1 dose sweep: 13 of 27 contaminated nights adopted, worst +21.44 % UA

**Ruling:** Judge re-ran s1_learner_freeze.py and --perturb (4 -> 0, clean stays 1). The measured-COP, flow-lift and buffer-cooling learners each ingest 1 of 4 contaminations, so 'the one learner that ignores the freeze' should read 'the only learner that ingests all four'. Verifier's dose sweep (v1_sysid_freeze.py) shows error grows with dose; with the worst cell dropped 12 adoptions remain, worst +8.75 %. Distinct from D7-s1-03 (missing freeze consult vs unnamed refusal), compounding with it.

**Issue title:** [R8-D7-s1-01] The active sysid experiment ignores the learning freeze and records external heat, defrost, open-window and stale-indoor nights

coordinator._run_system_identification aborts only on the pump freeze_reason / space_blocked and never consults _learning_frozen, so the experiment records samples through external heat, defrost, an open window and a pinned indoor reading (4 of 4 contaminations ingested) where the house heat-loss learner ingests 0 of 4 on the same coordinator state; across a dose sweep on three presets the #1410 gate adopts and persists 13 of 27 contaminated nights, worst heat-loss scale error +21.44 % (+8.75 % with that cell dropped).

Evidence: tools/audit/round8/D7/s1_learner_freeze.py, command `PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/s1_learner_freeze.py` -> RESULT sysid_contaminated_ingest=4, sysid_clean_ingest=1 (null), house_heat_loss_contaminated_ingest=0; perturbation `--perturb` (early return while _learning_frozen(indoor, outdoor) is set) -> 0, clean arm still 1. tools/audit/round8/D7/v1_sysid_freeze.py (real coordinator, tick by tick, contamination applied to the plant and as the production flag) -> 13 of 27 adopted, clean 2 of 3 at 0.000 %, perturbed 0. The scale is later corrected by the passive learner, and protection needs the external-heat or defrost signal configured.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/coordinator.py _run_system_identification; beside the freeze_reason abort, abort an armed or active experiment with a named reason while _learning_frozen(CONF_INDOOR_TEMP_ENTITY, CONF_OUTDOOR_TEMP_ENTITY) is set.

Finding id: D7-s1-01 (round 8, baseline cdf82daa).

## D7-s1-02 -- verified, medium, bug

**Judge number:** twozone_admitted=0 of 3; singlezone_admitted=2 of 3 (null); --perturb (plant single-zone, config two-zone) -> 2 of 3 (the finding's stated 1 is stale); v1 aborts at 0.828, 0.961, 1.288 K vs 0.8 K allowance

**Ruling:** Judge re-ran s1_sysid_twozone.py (0/3, null 2/3) and --perturb (2/3; direction holds, stated value 1 is stale). Verifier's real-coordinator path aborts all 3 two-zone presets past the 0.8 K allowance, and feeding the area-weighted room temperature still adopts 0/3, so the cause is the one-room model, not only the thermometer.

**Issue title:** [R8-D7-s1-02] The one-room sysid model cannot identify a two-zone house: 0 of 3 two-zone presets adopt and experiments overshoot the 0.8 K comfort allowance

sysid._sizing_model and sysid._simulate_slab_path hard-code two_zone_enabled=False while the coordinator feeds the upper-zone thermometer, so on the three stress presets derived two-zone the experiment adopts 0 of 3, and on the real coordinator path all three abort in the step phase at 0.83, 0.96 and 1.29 K sensor excursion, past the 0.8 K allowance; the same presets derived single-zone adopt 2 of 3 at <= 0.06 % scale error.

Evidence: tools/audit/round8/D7/s1_sysid_twozone.py, command `PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/s1_sysid_twozone.py` -> RESULT twozone_admitted=0, singlezone_admitted=2 (null control); perturbation `--perturb` (plant single-zone while the declared config stays two-zone) -> twozone_admitted=2. tools/audit/round8/D7/v1_sysid_twozone.py -> aborts at 0.828 / 0.961 / 1.288 K, --sensor avg still 0 of 3. A second inconsistency on the path: step() receives heat_loss_coefficient*scale while adoption divides by upper+lower.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/sysid.py and the coordinator's arm call; refuse arm() on a two_zone_enabled plant with a named reason, or size and fit on the two-zone ThermalModel with the upper zone as the observed state.

Finding id: D7-s1-02 (round 8, baseline cdf82daa).

## D7-s1-03 -- verified, medium, bug

**Judge number:** silent_refusals=10 of 19 finished (adopted 9 publish 'adopted' and log 1 line each); --perturb-fix -> 0; LOO without light_new 5 of 14; v1 8 of 23

**Ruling:** Judge re-ran s1_gate_silent.py (10/19) and --perturb-fix (0). Verifier's 30-night sweep reading the published learning-view attribute and the logger: 8 of 23 silent, 15/15 adoptions named and logged; with light_new dropped 4 of 16. _finish logs a UA at INFO that the gate then refuses without a word.

**Issue title:** [R8-D7-s1-03] The sysid adoption gate refuses without a reason: a refused fit stays published as completed, reason ok, with its UA

The first guard in coordinator._adopt_system_identification returns without writing a reason or a log line, so 10 of 19 finished experiments across three presets are refused while SystemIdentification.as_dict() (the learning view's system_identification attribute) still publishes completed=True, reason='ok' and the fitted heat_loss_kw_per_c, e.g. a heavy_old open-window night at 0.5328 kW/K (+72 %); with the most favourable preset (light_new) dropped, 5 of 14 remain silent.

Evidence: tools/audit/round8/D7/s1_gate_silent.py, command `PYTHONPATH=tests/hastub python3 -u tools/audit/round8/D7/s1_gate_silent.py` -> RESULT finished=19, adopted=9, silent_refusals=10; null: the 9 adopted cells publish reason 'adopted' with 1 log line each; perturbation `--perturb-fix` (the guard writes completed=False and a named reason) -> 0. tools/audit/round8/D7/v1_gate_silent.py (published attribute plus logger capture, 30 nights) -> 8 silent of 23 finished, 15/15 adoptions named and logged, perturbed 0.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/coordinator.py _adopt_system_identification; on the interval refusal write replace(result, completed=False, reason=<named>) and log at INFO, as the identifiability refusal two lines below does.

Finding id: D7-s1-03 (round 8, baseline cdf82daa).

## D4-01 -- verified, medium, bug

**Judge number:** inversions 375x812=3, 768x1024=1, 1280x800=2 (real Chromium, real Tab presses); perturbation .whatif .wi-row flex-wrap nowrap -> 2 / 1 / 2

**Ruling:** Judge regenerated the plan payload under its own HPO_PLANDATA (tests/plan_view.py) and re-ran s1_tab_order.mjs at the three required viewports: 3/1/2, exact. The flex-wrap perturbation (on disk, restored in finally, git status clean) moves only 375x812 (3 -> 2), as the finder stated; the other contributors (markup order of .wi-actions / .wi-revert) remain. Verifier's global pairwise metric 35/4/21 agrees in sign. All controls remain Tab-reachable, so medium.

**Issue title:** [R8-D4-01] Keyboard Tab order in the expanded what-if dialog jumps backward up the screen at all three required viewports

In the expanded dialog (what_if: true, plan-chart page) driven in real Chromium with real Tab presses, consecutive focus stops jump backward (the next stop sits more than 0.6 row-heights above the previous one and not to its right) 3 times at 375x812, once at 768x1024 and twice at 1280x800, because DOM order in the WhatIfPanel markup does not match the wrapped visual order; every control stays reachable.

Evidence: tools/audit/round8/D4/s1_tab_order.mjs, command `NODE_PATH=<playwright> PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers HPO_PLANDATA=<private tmp>/plan.json HPO_VP_W=375 HPO_VP_H=812 node tools/audit/round8/D4/s1_tab_order.mjs` (payload from tests/plan_view.py) -> RESULT inversions=3; 768x1024 -> 1; 1280x800 -> 2. Perturbation `.whatif .wi-row { flex-wrap: nowrap }` -> 2 / 1 / 2 (moves the phone viewport only; the remaining inversions come from markup order). The verifier's all-pairs reading-order metric gives 35 / 4 / 21. No null control applies to a count of focus stops.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js WhatIfPanel markup; reorder .wi-actions / .wi-row / .wi-revert so DOM order matches visual order when wrapped, and require inversions=0 at 375, 768 and 1280.

Finding id: D4-01 (round 8, baseline cdf82daa).

## D4-s2-01 -- verified, low, hygiene

**Judge number:** untranslated_residual=1 (8 identical en/sv strings, 7 allowlisted); --perturb -> 0

**Ruling:** Judge re-ran s2_translation_gap.py and --perturb (1 -> 0). Verifier's allowlist-free heuristic lands on the same key. The harness docstring says 10 ALLOWLIST entries while the dict holds 7 (instrument wording only).

**Issue title:** [R8-D4-s2-01] The ecl110_mqtt_qos options-flow label is untranslated in sv.json

translations/sv.json's label for ecl110_mqtt_qos on the heat-curve control page is byte-identical to en.json's ('MQTT quality of service') while its sibling ecl110_mqtt_retain is translated; of 8 identical en/sv strings outside exception bodies, 7 are legitimately identical (brand names, numeric ranges, loanwords) and this 1 is not.

Evidence: tools/audit/round8/D4/s2_translation_gap.py, command `python3 tools/audit/round8/D4/s2_translation_gap.py` -> RESULT identical_strings_total=8, allowlisted_legitimate=7, untranslated_residual=1; perturbation `--perturb` (translated placeholder in memory) -> 0. The verifier's allowlist-free heuristic finds the same single key. No null control applies to a catalog count.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: one string in custom_components/heatpump_optimizer/translations/sv.json (e.g. 'MQTT-kvalitetsnivå').

Finding id: D4-s2-01 (round 8, baseline cdf82daa).

## D0-s1-01 -- verified, low, hygiene

**Judge number:** runs_stopped_by_ftol=219/320, maxiter 0; ftol_cells_gap_gt_1e-3=15/40; gap mean 1.1249e-3, max 1.1074e-2, best-cell-dropped mean 8.698e-4; flat mean 7.29e-4 vs non-flat 1.18e-3; nfev median x1.824 (max x4.51); perturbation (ftol literals 1e-12 on disk): gap 0 in 4/4 cells run, ftol stops 1/8,1/8,1/8,4/8; closed loop (v1_mpc, 3 cells re-run, identical to verifier log): d_adj +1.06, -0.0002, -0.09 SEK/day, flat|winter_cold +0.43

**Ruling:** Judge re-ran the full 40-cell two-zone grid (4 m 38 s, load1 2.75, thread_factor 1.000): every RESULT identical to the finder and verifier. The on-disk perturbation is tautological for the gap (production becomes the arm) but moves runs_stopped_by_ftol and J as stated; its 5th cell was lost when the judge stopped a concurrent run, 4 of 4 completed cells went to 0. Verifier's non-tautological local-descent metric (7/40 cells > 1e-3) shows 5 of the finder's 15 cells are basin changes, not early stops. The closed loop re-run matched the verifier's log cell for cell: mixed sign, 2.3-2.7x nfev, and the gain survives the flat-price control, so no realised price-optimality gain. The number shows a solver-tolerance trade with no demonstrated wrong money: class set to hygiene (tuning), severity low. A first judge run of D2 overlapped this on-disk edit and was discarded (instrument note).

**Issue title:** [R8-D0-s1-01] L-BFGS-B ftol=1e-6 stops 219 of 320 refinements on the relative-reduction test, leaving >0.1 % of the objective in 15 of 40 cells

On the 8x5 profiles grid (two-zone, DHW off), 219 of 320 production L-BFGS-B runs stop on the ftol=1e-6 relative-reduction test and none on maxiter; re-running the same optimize with ftol=1e-12 at the same seam lowers the shipped objective_value by more than 0.1 % in 15 of 40 cells (mean 0.112 %, max 1.11 %, most favourable cell dropped 0.087 %) at a median 1.82x function evaluations (max 4.5x); the gap survives flat prices (mean 0.073 %), and in a 24 h closed loop the tighter tolerance is cheaper in some cells and dearer in others, so no realised saving is shown.

Evidence: tools/audit/round8/D0/s1_budget.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D0/s1_budget.py --tz 1 --dhw 0 --arms prod,ftol` -> RESULT runs_stopped_by_ftol=219, runs_stopped_by_maxiter=0, ftol_cells_gap_gt_1e-3=15, ftol_gap_mean=1.1249e-03, ftol_gap_mean_drop_best=8.6984e-04, ftol_flat_gap_mean=7.2917e-04 (null control), ftol_nfev_ratio_median=1.824. Perturbation tools/audit/round8/D0/s1_budget_perturb.sh (both ftol literals 1e-12, restored by trap) -> gap 0 and ftol stops 37 -> 7 of 32 runs in the 4 cells completed. tools/audit/round8/D0/v1_descent.py -> local descent headroom > 1e-3 in 7 of 40 cells (5 of the 15 are basin changes); tools/audit/round8/D0/v1_mpc.py (24 h closed loop) -> +1.06, -0.0002, -0.09 SEK/day and +0.43 at flat prices, nfev 2.3-2.7x.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/optimizer.py, the two options dicts passed to _scoped_minimize (ftol 1e-9..1e-12, or a relative-gap re-polish), priced against the stress budgets (nfev x1.6-x1.8 median). Seam rule: grep -n '"ftol"' custom_components/heatpump_optimizer/optimizer.py

Finding id: D0-s1-01 (round 8, baseline cdf82daa).

## D12-s1-01 -- weakened, medium, bug

**Judge number:** unroutable_writes=2 of 6 surfaces (input_boolean, climate); null switch 0; --fix-arm (homeassistant domain) -> 0; v1 not_following_runs=2 of 6, null 0

**Ruling:** Judge re-ran s1_actuation.py (2, --fix-arm 0, null 0) and v1_switch_follow.py (2 of 6, null 0). The config-flow picker offers switch only; the unroutable slot is reachable through assign_entity / the diagram's assign path. In real HA a switch.turn_off on an input_boolean logs a 'referenced entities missing' warning and does nothing, so the pump stays on its own curve: fails safe, costs savings. High -> medium. Verifier weaken(medium) agrees. Separate from D12-s1-02.

**Issue title:** [R8-D12-s1-01] An input_boolean or climate heat-pump switch accepted by assign_entity is never actuated: _apply_action always calls switch.turn_on/turn_off

topology.ASSIGNABLE_KEYS and the assign_entity service accept switch, input_boolean and climate for heat_pump_switch_entity, but coordinator._apply_action always calls switch.turn_on / switch.turn_off, which Home Assistant routes to no entity for the other two domains; across 6 actuation surfaces, 2 (input_boolean and climate) receive an unroutable call each cycle and do not follow the plan's heat_pump_on, while the plan publishes normally.

Evidence: tools/audit/round8/D12/s1_actuation.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D12/s1_actuation.py` -> RESULT unroutable_writes=2, surfaces_unactuated=2, null_control_switch_unroutable=0 (switch.* slot); perturbation `--fix-arm` (service domain 'homeassistant', in memory) -> 0. tools/audit/round8/D12/v1_switch_follow.py (HA routing emulated, both initial states) -> not_following_runs=2 of 6, null 0. The config-flow picker offers switch only, and real HA logs a warning rather than raising; the pump then runs on its own curve, so savings are lost, not comfort.

Final severity **medium**, stop-rule class **bug** (judge-weakened from high).

Proposed fix scope: custom_components/heatpump_optimizer/coordinator.py _apply_action (homeassistant.turn_on/turn_off, as the pump driver at coordinator.py:2706 already does, or branch on the entity domain), plus a tests/harness.py FakeServices routing check over the ASSIGNABLE_KEYS domains. Seam rule: grep -n 'async_call(' -A2 custom_components/heatpump_optimizer/*.py crossed with topology.ASSIGNABLE_KEYS.

Finding id: D12-s1-01 (round 8, baseline cdf82daa).

## D12-s1-02 -- verified, medium, bug

**Judge number:** phantom_dhw_cells=8 of 8 no-DHW cells at 4.000 kW; null DHW cells 0 of 8; --fix-arm -> 0 of 8; v1: 6 of 6 cells change (switch flipped off->on, dhw keys, commanded 0 -> 4 kW), measured null 0 of 6

**Ruling:** Judge re-ran s1_phantom_boost.py (8/8, fix 0/8) and v1_boost_effects.py (6/6, null 0/6). The finder's null is 0 by construction; the verifier's measured null (two no-boost cycles) is the real control and reads 0. Physical consequence: the boost turns the pump on in a peak hour the plan switched off, for 2 h, on an install with no tank.

**Issue title:** [R8-D12-s1-02] On an install with no hot water, the always-created Hot water boost switch injects 4 kW of DHW into the live action and turns the pump on

switch.py creates BoostDhwSwitch unconditionally, and on an install with no hot water turning it on makes the next cycle's action carry dhw_power = 0.8 x max_power (4.000 kW) in 8 of 8 no-DHW cells, publish dhw_heating_active = True, force heat_pump_on and add 4.0 kW to _commanded_power (which feeds the accuracy predictions, the peak guard and the frequency recommendation); in 6 of 6 cells the pump switch call flips from turn_off to turn_on in a peak hour the plan had switched off.

Evidence: tools/audit/round8/D12/s1_phantom_boost.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D12/s1_phantom_boost.py` -> RESULT phantom_dhw_cells=8 of 8, phantom_dhw_kw_min=max=4.000; perturbation `--fix-arm` (boost.apply drops CHANNEL_DHW when dhw_enabled is False, in memory) -> 0 of 8 while the DHW cells keep 4.00 kW. tools/audit/round8/D12/v1_boost_effects.py -> cells_changed=6 of 6, cells_switch_flipped=6, cells_commanded_changed=6, null_cells_changed=0 of 6 (two no-boost cycles). Learner bias through _interval_space_power was not measured.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/boost.py (drop or refuse the DHW channel when params.dhw_enabled is False) and switch.py (do not create BoostDhwSwitch, or keep it unavailable, without DHW). Seam rule: grep -n 'CHANNEL_DHW\|dhw_power\|dhw_heating_active' custom_components/heatpump_optimizer/boost.py custom_components/heatpump_optimizer/switch.py

Finding id: D12-s1-02 (round 8, baseline cdf82daa).

## D9-s1-01 -- verified, low, hygiene

**Judge number:** discarded_polish_share=0.0633 (1200 of 18967 njev; 149 of 206 polishes discarded; 24 ABNORMAL at nit 0, 501 njev); flat 0.0783; --maxls 5 -> 0.0406; per-scenario 0..0.4155, median 0.1311

**Ruling:** Judge re-ran s1_polish.py real, --flat and --maxls 5: every count identical to finder and verifier. The share persists at flat prices, as a waste claim should. 'Discarded' is known only after the polish ran, and the verifier measured the maxls=5 remedy worsening 9 of 51 shipped objectives (up to +1.06 %), so the number accounts for the owner-chosen unbounded polish (#1208) rather than a free saving; only the ABNORMAL-at-nit-0 polishes (2.6 % of kernel work) are separable waste. The finder's 'drop_most_favourable' 0.1258 is a mean of per-scenario shares, not a pooled share. Low, hygiene (a cost trade, no wrong output).

**Issue title:** [R8-D9-s1-01] The per-candidate L-BFGS-B polish spends 6.3 % of the sweep's gradient evaluations on results it discards, 2.6 % in polishes that end ABNORMAL at iteration 0

Over the 51 stress.sweep_combinations() solves, 149 of 206 _lbfgsb_restart polishes return their input unchanged, and those discarded polishes take 1,200 of 18,967 gradient evaluations (0.0633); 24 of them end ABNORMAL at nit 0 after 501 gradients without progress; per scenario the share runs 0 to 0.4155 (median 0.1311), and it is 0.0783 at flat prices.

Evidence: tools/audit/round8/D9/s1_polish.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D9/s1_polish.py` -> RESULT real.discarded_polish_share=0.0633, real.polishes_discarded=149, real.polishes_abnormal_nit0=24, real.njev_abnormal_nit0=501; `--flat` (null control) -> 0.0783; perturbation `--maxls 5` (polish line-search budget) -> 0.0406. Counts, contention-immune (thread_factor 1.000, load1 2.0-2.8). tools/audit/round8/D9/v1_polish_kernel.py -> 0.0631 of kernel work, ABNORMAL nit-0 polishes 0.0264; the maxls=5 remedy worsens 9 of 51 shipped objectives by up to +1.06 %, so only the nit-0 share is free.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: custom_components/heatpump_optimizer/optimizer.py _lbfgsb_restart only; an early exit (projected-gradient check at best.x) for polishes that cannot make progress, proved against D0's #1208 polish-gap grid and not a blanket maxls cut.

Finding id: D9-s1-01 (round 8, baseline cdf82daa).

## D9-s2-01 -- weakened, low, hygiene

**Judge number:** budgeted_scripts_seeing_coordinator=0 (also 0 for sensor, process_worker, price_model, narrative; control optimizer=1); --make-perturbed -> 1 (tautological: edits the table read)

**Ruling:** Judge re-ran s2_gate_blind.py (private temp copy): all counts exact. Perturbation (a) edits tests/closures.json, the table the metric reads, so it is tautological; the behavioural arm is the verifier's v1_suite_blind.sh (a doubled _build_data_dict changes 0 of 13 selected scripts in list-comprehension spelling) and s2_cycle --inject-build 2 (+22..33 % loop CPU same-session per the verifier; timing provisional, not re-taken). The title's '2x loop-thread regression' doubles a ~2 ms component; no regression or harm is shown. A coverage gap in the gate, not a check giving a wrong answer: low, hygiene.

**Issue title:** [R8-D9-s2-01] No CPU- or memory-budgeted gate script covers coordinator.py, sensor.py, process_worker.py, price_model.py or narrative.py

tests/stress.py is the only gate script that budgets CPU or memory, and its measured closure in tests/closures.json contains none of coordinator.py, sensor.py, process_worker.py, price_model.py or narrative.py, so the scoped gate skips stress.py for a change to any of them and no budgeted check measures the coordinator cycle; a one-line mutation that doubles the per-cycle _build_data_dict work changes the verdict of 0 of the 13 scripts the gate selects.

Evidence: tools/audit/round8/D9/s2_gate_blind.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D9/s2_gate_blind.py` -> RESULT budgeted_scripts_seeing_coordinator=0 (sensor, process_worker, price_model, narrative 0), budgeted_scripts_seeing_optimizer=1 (positive control); `--make-perturbed` (coordinator.py added to stress.py's closure) -> 1, which edits the table the metric reads. Behavioural arm: tools/audit/round8/D9/v1_suite_blind.sh -> 0 of 13 selected scripts change under the doubled-build mutation (list-comprehension spelling); tools/audit/round8/D9/s2_cycle.py --inject-build 2 -> loop CPU +22 to +33 % same session (provisional timing).

Final severity **low**, stop-rule class **hygiene** (judge-weakened from medium).

Proposed fix scope: tests/ only (a cycle arm in the stress gate or a new budgeted lane driving real _async_update_data cycles, budgeting loop-thread CPU as a ratio to reference_solve and the tracemalloc slope, with its measured closure recorded).

Finding id: D9-s2-01 (round 8, baseline cdf82daa).

## D7-s2-01 -- verified, low, hygiene

**Judge number:** unreachable_missed_by_gate=12 (gate_dead_total 0); --perturb 11; gate probe: planted describe() 0, unique name 1; sentinel prod_calls 0 for both functions and 0 logger reads vs controls 14 / 69 / 5324; sentinel --perturb 14 (finding says 12, stale)

**Ruling:** Judge re-ran s2_reach.py --perturb --gate-probe and s2_sentinel.py with and without --perturb (private TMPDIR). structure.py documents the screen as name-based ('not a linker'), so this reads a carried metric; 10 of 12 are unused _LOGGER lines, the two functions are test-pinned (10 and 1 test calls). Low, hygiene.

**Issue title:** [R8-D7-s2-01] structure.py's name-based dead-code screen reports 0 while 12 top-level production symbols are unreachable

tests/structure.py's dead_top_level_symbols decides liveness by bare name across the package, so it reports 0 while 12 top-level production symbols are unreachable from every Home Assistant root and never called or read at runtime: grid_fee.is_valid_spec, presets.describe and the unused _LOGGER in battery, binary_sensor, dhw_draws, power_guard, presets, pump_schedule, pv, sensor, switch and tariff (36 lines).

Evidence: tools/audit/round8/D7/s2_reach.py, command `PYTHONPATH=tests/hastub TMPDIR=<private> python3 tools/audit/round8/D7/s2_reach.py --perturb --gate-probe` -> RESULT unreachable_missed_by_gate=12, gate_dead_total=0, perturbed_unreachable_total=11 (a root import added); gate probe: a planted uncalled describe() leaves the gate at 0, a uniquely named one raises it to 1. tools/audit/round8/D7/s2_sentinel.py -> prod_calls 0 for both functions and logger_reads_total 0, against controls dhw_schedule.is_valid_spec 14, presets.derive 69, coordinator logger 5324; `--perturb` (config_flow rebinds to grid_fee.is_valid_spec) -> 14. The screen is documented as name-based, and the two functions are test-pinned.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: delete the 12 symbols in custom_components/heatpump_optimizer/ (re-point the features.py check on presets.describe) and make tests/structure.py:module_references resolve top-level names through import bindings, keeping the DYNAMIC_REFERENCES exemptions.

Finding id: D7-s2-01 (round 8, baseline cdf82daa).

## D7-s2-02 -- verified, low, hygiene

**Judge number:** renames_that_lower_cross_seam_edges=27 of 227 (raise 48); max drop 7 (_commanded_power), 5 without it; max cut drop 22; null 0; --perturb (SEAM_REGEXES empty) -> 0; baseline 140 at budget 140

**Ruling:** Judge re-ran s2_rename.py and --perturb. The partition is documented as name-first-match, so a rename reassigns the seam by the metric's own semantics; what stands is that a zero-headroom ratchet can be paid by renaming instead of decoupling. Low, hygiene.

**Issue title:** [R8-D7-s2-02] A pure method rename lowers the zero-headroom cross_seam_edges ratchet for 27 of 227 coordinator methods, by up to 7

tests/structure.py:seam_metrics buckets coordinator methods by name regex, so renaming a single method with no code change lowers the budgeted cross_seam_edges (140 at a budget of 140, zero headroom) for 27 of 227 methods, by 1 to 7 (5 with the top rename, _commanded_power, left out), and lowers sum(cut_*) by up to 22; 48 other renames raise it.

Evidence: tools/audit/round8/D7/s2_rename.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D7/s2_rename.py` -> RESULT base_cross_seam_edges=140, renames_that_lower_cross_seam_edges=27, max_single_rename_drop=7, max_drop_without_top_rename=5, max_single_rename_cut_drop=22, null_nonzero=0 (rename within the same bucket); perturbation `--perturb` (SEAM_REGEXES emptied) -> 0 everywhere. tools/audit/round8/D7/v1_seam_rename.py (any-bucket rename) -> 51 methods with a drop, max 7.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: tests/structure.py and its budget; bucket methods by an explicit committed method-to-seam map that structure.py checks, or refuse a bucket change for any method present at recorded_at.

Finding id: D7-s2-02 (round 8, baseline cdf82daa).

## D7-s2-03 -- verified, low, hygiene

**Judge number:** killed[M3]=0 (dhw_coil branch disabled); identity null M4 0; v1: published edge 1 -> 0 under the mutant, killed_by_features 0, one-check driver --perturb killed 1

**Ruling:** Judge re-ran s2_spot.py --only M3, --null --only M4, and v1_coil_edge.py with and without --perturb (private TMPDIR, tree clean). The closure-wide arm (13 drivers, 0 kills) was not re-run by the judge; the verifier re-ran it. The mutant is observable (describe_setup drops wood_tank->dhw_tank), so it is not equivalent. The finder's 'only dhw_coil check passes dhw_coil=False' is imprecise: features.py enables the coil but asserts only heat_pump->dhw_tank. A drawing edge, no control consequence: low.

**Issue title:** [R8-D7-s2-03] Disabling the dhw_coil branch of topology.layout_edges drops the wood_tank->dhw_tank edge and no test notices

Replacing `if dhw_coil:` with `if False:` in topology.layout_edges removes the wood_tank->dhw_tank edge that describe_setup publishes for a two_tank_4way layout with DHW and the wood coil (1 edge -> 0), and no driver in topology.py's measured closure, card.mjs or card_drift.mjs changes its verdict; features.py enables the coil at one site but asserts only the heat_pump->dhw_tank edge.

Evidence: tools/audit/round8/D7/s2_spot.py, command `PYTHONPATH=tests/hastub TMPDIR=<private> python3 tools/audit/round8/D7/s2_spot.py --only M3` -> RESULT killed[M3]=0; identity null `--null --only M4` -> 0; the verifier's closure arm (`--only M3 --closure`) -> 0 of 13 drivers. tools/audit/round8/D7/v1_coil_edge.py -> seam_edge_baseline=1, seam_edge_mutant=0, killed_by_features=0; `--perturb` (one added check asserting the edge) -> killed 1.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: tests/features.py; one check that layout_edges('two_tank_4way', two_zone=True, wood=True, dhw_coil=True) contains ('wood_tank', 'dhw_tank'), and the editor's match for it.

Finding id: D7-s2-03 (round 8, baseline cdf82daa).

## D3-s1-01 -- verified, medium, bug

**Judge number:** refused_mutants=17 of 17 at --ref cdf82daa (unmutated rc 0); --perturb (claim list emptied) -> 0 (unmutated rc 1); null at HEAD^1 -> 0 of 17; v1_claimgate 16 of 16, null 0, perturb 0; instrument_skips_envdrift_at_head_eq_base=1

**Ruling:** Judge re-ran s1_claimkill.py (temp root rewritten to the judge's) at the baseline ref, with --perturb, and at HEAD^1 (null), and v1_claimgate.py with and without --perturb: all exact, production restored (restored=1, git status clean). Reachability is narrower than claimed, per the verifier and confirmed by v1_claimgate's instrument_skips_envdrift_at_head_eq_base=1: at HEAD==BASE mutation_table drops env_drift from the driver net, so the D3-brief pre-screen and quiet-window claims hold only through the finder's wrapper; the reachable path is mutation_table --scope changed on a test-only PR whose merge base carries claims, where every would-be survivor is scored 'killed by tests/env_drift.py'. Medium with that scope.

**Issue title:** [R8-D3-s1-01] mutation_table scores env_drift's INHERITED CLAIMS refusal as a kill: 17 of 17 production mutants, a comment-only edit included

When the fork point carries a non-empty claim list the diff does not change, tests/env_drift.py's claim-hygiene check refuses every production mutant with INHERITED CLAIMS before any capture runs, while the unmutated tree passes (rc 0), and tests/mutation_table.py:run_script scores that rc change as 'killed by tests/env_drift.py': 17 of 17 seeded mutants are refused, including a comment-only edit and an equivalent threadpoolctl guard; because drivers run cheapest-first and stop at the first kill, every would-be survivor on that path becomes a false kill. The reachable path is mutation_table --scope changed on a test-only pull request whose merge base carries claims; at HEAD == BASE the instrument drops env_drift from the net.

Evidence: tools/audit/round8/D3/s1_claimkill.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s1_claimkill.py --ref cdf82daabcfe3777d98b31489f36df5555ec9d82` -> RESULT refused_mutants=17 of 17, unmutated_rc=0, restored=1; null at ref HEAD^1 (the nightly's gate_ref) -> 0 of 17; perturbation `--perturb` (claim list emptied, restored in finally) -> 0. tools/audit/round8/D3/v1_claimgate.py (in-process check_claims_hygiene over a test-only diff, 15 fresh mutants plus a comment-only edit) -> 16 of 16, null 0, --perturb 0, instrument_skips_envdrift_at_head_eq_base=1.

Final severity **medium**, stop-rule class **bug** (judge-verified).

Proposed fix scope: tests/mutation_table.py (drive_spec/run_script for tests/env_drift.py: apply the inherited-claims rewrite to the mutant tree, as claims-autofix does, or judge only env_drift's drift section), a check that a comment-only production edit is not killed by the env_drift driver, and the same note in tools/audit/briefs/D3.md step 2.

Finding id: D3-s1-01 (round 8, baseline cdf82daa).

## D3-s2-01 -- weakened, low, hygiene

**Judge number:** clamp-removed mutant (m05) survives 0 killers over legionella.py's measured closure (env_drift excluded); positive control killed 1; hours_since future reading 0.0 -> -2.0 h, past unchanged; overdue_instant_delta 0.0 h; published due_in_hours 24.0 -> 26.0 h

**Ruling:** Judge re-ran s2_finding01_hours_since.py, v1_legionella_due.py and the verifier's closure-wide v1_suite_mutants.py (private temp copy; restored, tree clean): m05 killers 0, posctl killed 1. The finder's consequence ('push the anti-legionella due time later') is false for the due instant (delta 0.0 h): the mutant changes only the published due_in_hours and the per-plan deadline (+2 h) during a clock-skew window. A test gap with a bounded published-value effect: low. Class hygiene (the suite misses a mutant; production behaves correctly).

**Issue title:** [R8-D3-s2-01] No test drives LegionellaGuard.hours_since with a future timestamp; removing its negative-elapsed clamp survives the whole closure

LegionellaGuard.hours_since clamps a negative elapsed time to 0.0, but no test sets last_cycle or the attempt stamp in the future: deleting the clamp moves a 2 h-future reading from 0.0 to -2.0 h and survives every script of legionella.py's measured closure (0 killers, env_drift excluded), while a positive-control mutant is killed; the disinfection due instant is unchanged (delta 0.0 h) and only the published due_in_hours (24.0 -> 26.0 h) and the optimizer's deadline (+2 h) move, and only during a clock-skew window.

Evidence: tools/audit/round8/D3/s2_finding01_hours_since.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s2_finding01_hours_since.py` -> RESULT baseline_future_reading_h=0.0, mutant_future_reading_h=-2.0, past readings unchanged (null), mutant_survives_entities=True; tools/audit/round8/D3/v1_suite_mutants.py -> m05_killers=0 over the closure, `--posctl` killed 1; tools/audit/round8/D3/v1_legionella_due.py -> overdue_instant_delta=0.0 h, due_in_hours_t0 24.0 vs 26.0, null identical.

Final severity **low**, stop-rule class **hygiene** (judge-weakened from medium).

Proposed fix scope: tests/features.py; one check driving last_cycle / the attempt stamp 2 h into the future and asserting hours_since == 0.0 and the published due_in_hours.

Finding id: D3-s2-01 (round 8, baseline cdf82daa).

## D3-s2-02 -- verified, low, hygiene

**Judge number:** boundary_flips=2 of 2 (minimum == ceiling accepted at baseline, rejected by the > -> >= mutant at each site); null (ceiling - 0.01) accepted everywhere; m11 and m12 killers 0 over services.py's closure; positive control killed 1

**Ruling:** Judge re-ran s2_finding02_deadband_boundary.py, v1_deadband.py (in memory) and v1_suite_mutants.py (m11, m12 survive every closure script; posctl killed). config_flow.py:895's separate boundary was not measured.

**Issue title:** [R8-D3-s2-02] The dhw minimum == ceiling deadband boundary is untested at both service call sites

handle_set_thermal_params and handle_apply_schedule each accept a DHW minimum exactly equal to the deadband ceiling (setpoint - 5 K), and a `>` -> `>=` mutation at either site flips that legal value to a ServiceValidationError while surviving every script of services.py's measured closure (0 killers each), because the suite tests only 51.0 against a 50.0 ceiling.

Evidence: tools/audit/round8/D3/s2_finding02_deadband_boundary.py, command `PYTHONPATH=tests/hastub python3 tools/audit/round8/D3/s2_finding02_deadband_boundary.py` -> baseline None at the boundary on both sites, mutant ServiceValidationError on both, null (ceiling - 0.01) accepted everywhere; tools/audit/round8/D3/v1_deadband.py (real setup and hass.services.async_call) -> boundary_flips=2 of 2, positive control 51.0 rejected everywhere; tools/audit/round8/D3/v1_suite_mutants.py -> m11_killers=0, m12_killers=0, --posctl killed 1.

Final severity **low**, stop-rule class **hygiene** (judge-verified).

Proposed fix scope: tests/features.py; one boundary-value check per call site (minimum == setpoint - 5 accepted), and the same for config_flow.py's separate check.

Finding id: D3-s2-02 (round 8, baseline cdf82daa).

## D9-s1-02 -- refuted, none, hygiene

**Judge number:** quiet box (load1 0.52-0.58, 0 concurrent python processes): s1_cycle inline starvation share 0.447 / 0.364 (finder 0.645 / 0.904 at load1 ~23), max gap 21.2 / 17.3 ms; --no-gil-yield 0.805 / 0.892, max gap 55 / 91 ms; process route 0.004 / 0.000; idle 0.000 / 0.003. v1_gil same session, median of 4: solve s5 0.451, pure-Python null s5 1.000, solve s20 0.000, null s20 0.000, solve max 14.7 ms vs null 12.6 ms; solve_noyield s5 0.699, s20 0.056, max 23.5 ms; thread_factor 1.033 with deliberate executor CPU subtracted

**Ruling:** Re-taken on the idle box, which the verifier could not do. The finder's 65-90 % does not reproduce (0.36-0.45). The same-session null decides it: a pure-Python job on the executor starves the 1 ms heartbeat past 5 ms for 100 % of its busy time, the real solve for 45 %, so the 5 ms cut sits on CPython's own switch interval and the solve holds the GIL less than any Python executor job; nothing exceeds 20 ms with the yield in place. The claimed cause ('_gil_yield does not bound the hold') is contradicted: removing the yield raises the share to 0.70-0.89 and the max gap to 23-91 ms, so the yield is what bounds it. The s1_cycle inline arms print thread_factor 1.09-1.19 because the harness does not subtract the deliberate executor thread's CPU (README contract); v1_gil does and reads 1.033. The inline route is the capped #511 fallback (WORKER_FALLBACK_CAP=3). Refuted with a number; matches the verifier's refute.

## Instrument notes

1) orjson is not installed in the audit environment (not among BASELINE.md's pins); tools/audit/round8/D8/s1_finite_boundary.py silently falls back to a stub that counts every non-finite float as a serialisation failure, while real orjson 3.12.0 writes NaN/Inf as null; the judge installed orjson into a private --target dir to re-measure (D8-s1-01 weakened on it). Harnesses that model HA serialisation must refuse to run without the real serializer. 2) Hard-coded seat temp roots: D3/s1_claimkill.py (/tmp/D3-s1), D3/v1_suite_mutants.py (/tmp/D3-v1), D9/s2_gate_blind.py (/tmp/D9-s2), D9/s2_cycle.py, D9/s1_cycle.py and D9/v1_gil.py headers, D3/s1_cachekey.py's HPO_PLANDATA arm; the judge ran sed-rewritten copies under /home/claude/audit-r8/tmp/judge/. The harness contract should require TMPDIR-derived roots. 3) Several harnesses (D0 s1_budget_perturb.sh, D3 s1_claimkill.py, D3 v1_suite_mutants.py, D3 s2_*.py, D4 perturbation) edit production files on disk; a concurrent run in the same tree imports the edited file. The judge's first D2-s1-01 run overlapped the D0 ftol edit and was discarded and re-run clean (identical numbers). The contract should prefer in-memory perturbation or require the gate lock for on-disk edits. 4) Finder perturbations that do not move or are tautological: D10-s2-01 (unused import, 515 -> 515: void), D11-s1-02 / D9-s2-01 (--make-perturbed edits the table the metric reads), D0-s1-01 (production becomes the arm), D2-s2-02 (input unit attribute; the judge added a production-side perturbation, tools/audit/round8/D2/judge_price_unit_fix.py), D8-s2-02 (a static code read whose stated direction contradicts its own edit; the judge replaced it with tools/audit/round8/D8/judge_probe_default.py). Stale observed values: D7-s1-02 (--perturb gives 2 not 1), D7-s2-01 sentinel (14 not 12), D1-s3-01 (finder's guard gives 1 not 0). 5) Contract gaps in harness output: D1/s3_openmeteo_hostile.py prints no load1/thread_factor/swapins; D1/s2_ledger_fuzz.py prints a hard-coded thread_factor; D9/s1_cycle.py does not subtract the deliberate executor thread's CPU (thread_factor 1.09-1.19 on the idle box). 6) D8-s2 static harnesses (s2_ordering_finding.py, s2_enabled_analysis.py) read source text rather than hooking a production symbol, which COMMON.md says is not evidence; D5-s1's node regex truncates labels at <br/>, undercounting 3 vs 4. 7) D10 finder ran mypy --strict with tests/hastub on PYTHONPATH, the exact configuration tests/typing_ruler.py's construction guard refuses; the baseline's pinned typing job (job 107333392110) passed against a census of 0. 8) The unauthenticated api.github.com path works for check-runs and rulesets but /rate_limit returns 403 in agent sessions; the live check-run history moved between panel and judge (a new open PR #1508), so v1_latest_order.py's null went 0 -> 1. 9) pip download writes into the cwd: the judge's orjson probe dropped a wheel into the tree root, removed immediately (git status clean). 10) seat-scoped finding ids (D4-01 vs D4-s2-01 style) are inconsistent across seats; the judge did not validate them against finding.schema.json. .md writes worked for the judge.
