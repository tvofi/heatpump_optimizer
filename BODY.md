R10-CLONE-2238: the clone-class (#2238, class P2: one fact decided twice) instances the F5_clone family still listed, each given one owner in the module that held both copies, with every other copy calling it. Implements the approved design note `design/r10-clone-2238` at aead688d (verdict `Design review: approve aead688d446317fbbb8b478a47bdfe19725db1c2`). Part of #201. #2238 is already closed, so this body closes nothing.

| # | the one fact | owner | callers routed through it |
|---|---|---|---|
| P1 | an interval's planned (space, dhw) kW, an absent channel read as 0 | `coordinator._planned_split` | `_accumulate_energy`, `_settle_interval_diag` |
| P2 | a fabric-loss residual too large to be a heat-loss error is refused and logged | `coordinator._loss_residual_rejected` | `_async_learn_house_heat_loss`, `_async_learn_lower_floor_loss` |
| P3 | the trajectory the indoor sensor reads (upper floor in two-zone mode when present, else the room) | `OptimizationResult.sensor_trajectory` | `_file_lead_predictions`, `_predicted_next_room_temp`, `_publish_breach_reports`, `_safety_release_steps` |
| P4 | window means at their billed-equivalent factor, a window past the factors billed at 1 | `tariff.billed_windows` (on `shape[-1]`) | `_peak_excess`, `peak_cost_batch`, optimizer `_grid_report` |
| P5 | how many metering windows a plan of `n_steps` spans | `HeatPumpOptimizer._n_peak_windows` | `_peak_window_factors`, `_peak_day_kwargs` |
| P6 | an evidence sensor's attributes: payload block, `waiting_for`, at most one insight report | `_WaitsForEvidenceMixin._evidence_attributes` | `PredictionAccuracySensor`, `ContractComparisonSensor`, and `FrequencyAdvisorSensor` (see below) |
| P7 | the tracker stores a ranked (kW, day) record as the parallel `peaks`/`peak_days` lists | `PeakTracker._keep_ranked` | `_close_window`, `from_dict` |
| P8 | the metering-window partition: steps per window, steps in the leading partial window | `tariff._window_partition` | `metering_windows`, `_window_means_batch` |
| P9 | each window's real local start, walked in UTC from the slot of `start_time` (#243, #777) | `tariff._window_starts` | `window_factors`, `plan_window_days` |

Re-measured at my own merge base (`git archive origin/main`, then `enumerate_p2.py --json`): the two pairs the brief lists that are no longer in F5 are gone and dropped (`_fold_internal_gains`/`_fold_solar_aperture`, `_buffer_charge_ceiling`/`hold_demand_kw`); the other nine are the nine above.

Departures from the note, raised here rather than made silently:
- **P6 has a third caller.** The P2 registry rule for this fact (below) returned `FrequencyAdvisorSensor.extra_state_attributes`, which builds the same payload block plus `waiting_for` with no report. That is the same fact, so it is closed here, not dispositioned: `report_key` is optional and that sensor calls the owner too. The other `insight` readers the note names (no `waiting_for`) are untouched.
- **P8's owner takes no `n`.** The note's signature is `_window_partition(n, window_minutes, dt_hours, offset_steps)`; neither output depends on `n` (the partition is the clocks' property, as `_window_means_batch`'s docstring says), so an unused parameter was left out.
- **Commit shape.** Nine pair commits (P1..P9, each with its owner, its callers, its sentinel check and its registry entry), then the probe repair, the budget re-record, three follow-up commits (a wrong `CapacityTariff` keyword and a missed owner binding in P4's check, strict typing of the P4/P6 owners, and an unbound name in P8's check) that the step ref's fast-forward-only rule kept as their own commits instead of folded in, and the merge of origin/main.

Invariants: every output is bit-for-bit what it was (no golden moved, below); P2 keeps both debug messages (they differ only in the learner's noun) and the house learner's finite check where it was; P4 slices before padding, so the 1-D and 2-D paths share the owner; `_peak_window_factors` keeps its signature for the two finder harnesses that drive it.

## Head

fe40be9853d509116f14b5e9e3fc96fb075b678f (the PR head). Since the head this body was last taken at, a46e4d02f (`record: the delivery row for #3273`, tvofi), it moved by one commit: `git log a46e4d02..fe40be98` prints exactly `fe40be985 ci: pin killed mutants` (github-actions[bot], the `mutation-autofix` job's push). It adds 17 files under `tests/mutation_ledger/killed_by/` and changes nothing else: `git diff --stat a46e4d02 fe40be98` reads `17 files changed, 102 insertions(+)`, and the three-dot diff over the code handoff ed225e75, `git diff ed225e759...fe40be98`, adds those 17 files and the delivery row `dev/programme/delivery/3273.md` and touches no `custom_components` file and no test script (`git diff --stat ed225e759 fe40be98 -- custom_components tests/*.py dev/audit` prints nothing). Code handoff: ed225e7597851daa179937915292a123f3076be2. Cut from 28482ece; origin/main moved three times during the work and was merged each time without conflict: 80016a71 (#3234, replay cost draws), 41aa9050 (#3256, policy role pack) and f2a01514 (delivery records only); merge base f2a015142714383722bf49d7ab20d8398ec9674c. origin/main has since moved to 08fd676e9087abba636ade4106a0f0313f838bda, which this branch has not merged: the head is frozen for this body re-take, so the figures below are measured against the merge base f2a01514 and the next merge is the orchestrator's. None of the earlier merges touched a production module or a test script this diff edits. Every figure below was re-taken at fe40be98 (the enumerator, archscore, structure, probes and closure selection; the scoped gate and the mutants ran at the earlier heads named where they appear, on production code and test scripts identical to this head: `git diff 41c2ffab fe40be98 -- custom_components` prints nothing).

## Mutation proof

Each mutant restores ONE caller's inline copy at the head (the shape the note names as the mutation target), runs that pair's script, and the pair's check goes red. Driver: scratch `mutants.py` (22 mutants, each `old -> new` text), applied to a detached worktree at the head.

All 22 killed, each by its pair's check (the detail is what the check printed):

| mutant (caller restored to its copy) | script | red check | what it read |
|---|---|---|---|
| P1 `_accumulate_energy` | features.py | `R10-CLONE-2238 P1: the ledger split and the diagnosis apportionment both read ...` | ledger space kWh 1.5 (the input, not the sentinel 1.0) |
| P1 `_settle_interval_diag` | features.py | same P1 check | diag electrical_power 1.5 |
| P2 house learner | dst_checks.py | `R10-CLONE-2238 P2: the house and lower-floor loss learners both gate ...` | gated `['lower-floor']` only |
| P2 lower-floor learner | dst_checks.py | same P2 check | gated `['house']` only |
| P3 `_file_lead_predictions` | features.py | `R10-CLONE-2238 P3: next-room temp, lead buckets, the breach report and the safety release ...` | leads `[]` |
| P3 `_predicted_next_room_temp` | features.py | same P3 check | next 21.0 |
| P3 `_publish_breach_reports` | features.py | same P3 check | breach not 11.0 |
| P3 `_safety_release_steps` | features.py | same P3 check | release not `[0, 1, 2]` |
| P4 `_peak_excess` | features.py | `R10-CLONE-2238 P4: peak_kw, peak_cost and peak_cost_batch all scale ...` | peak_cost 0.0 |
| P4 `peak_cost_batch` | features.py | same P4 check | batch differs from the sentinel's reference |
| P4 `_grid_report` | features.py | same P4 check | peak_kw 1.0 |
| P5 `_peak_window_factors` | features.py | `R10-CLONE-2238 P5: the window factors and the window days are both sized ...` | factors 24, days 7 |
| P5 `_peak_day_kwargs` | features.py | same P5 check | factors 7, days 24 |
| P6 `PredictionAccuracySensor` | entities.py | `R10-CLONE-2238 P6: the accuracy, contract-comparison and frequency-advisor sensors ...` | the accuracy block, not the sentinel |
| P6 `ContractComparisonSensor` | entities.py | same P6 check | the comparison block |
| P6 `FrequencyAdvisorSensor` | entities.py | same P6 check | the freq_control block |
| P7 `_close_window` | features.py | `R10-CLONE-2238 P7: from_dict and _close_window both store the ranked record ...` | calls `[1]`, closed `[9.0, 1.0]` |
| P7 `from_dict` | features.py | same P7 check | calls `[2]`, restored `[5.0]` |
| P8 `metering_windows` | features.py | `R10-CLONE-2238 P8: metering_windows and _window_means_batch both partition ...` | scalar `[1.5 5.5]` |
| P8 `_window_means_batch` | features.py | same P8 check | batch `[[1.5 5.5]]` |
| P9 `window_factors` | dst_checks.py | `R10-CLONE-2238 P9: window_factors and plan_window_days both walk ...` | factors all 0.0 |
| P9 `plan_window_days` | dst_checks.py | same P9 check | days the real autumn ordinals |

P1-P5 ran at 41c2ffab, P6-P9 at the merged head 4df95354; production is identical to fe40be98 (`git diff 41c2ffab fe40be98 -- custom_components` prints nothing) and the merge touched none of the four production modules or the three test scripts (`git diff --stat 28482ece 80016a71 -- custom_components tests/features.py tests/dst_checks.py tests/entities.py dev/audit/rounds` prints nothing). `stress.py` was left to CI's required mutation check, as `fixer.md` step 5 says.

The registry is its own mutation proof: run against the base's production code (every copy inline, no owner), each of the nine new entries reports every copy as a stray `SEAM` and its owner `OWNER-MISSING` (figures below).

## Unpinned sites

Each site the diff adds that `prepr.sh` step 6d lists, keyed as it prints them (all under `custom_components/`). At fe40be98 every one except the triaged `tariff.py:877 CMP_BOUND` is pinned: the `mutation-autofix` job (run 42329898240, attempt 2) recorded 17 `killed_by` pins in `fe40be985`, each `Recorded by mutation_table.py --pin-killed`, the 14 sites below and three CI measured beyond them (`_evidence_attributes` `GUARD_OFF f450751c`, `_window_partition` `CLAMP_DROP 80efca0b`, and the second of the `billed_windows` `GUARD_OFF` pair).

- `coordinator.py:1607 CMP_BOUND`: pinned (`killed_by/coordinator.py/_loss_residual_rejected.CMP_BOUND.07ea7eb6.json`, killed by tests/features.py); also the value check `R10-CLONE-2238 P2: _loss_residual_rejected keeps a residual at the bound (either sign) and refuses one just past it` (tests/dst_checks.py), whose mutant (`<=` -> `<`), run at 12992bed, turns it red: `FAIL ... [bound 1.0, past 1.0000000000000002]`.
- `coordinator.py:1607 GUARD_OFF`: pinned (`_loss_residual_rejected.GUARD_OFF.07ea7eb6.json`, tests/features.py), and by the same P2 bound check.
- `coordinator.py:1614 RETURN_DEL`: pinned (`_loss_residual_rejected.RETURN_DEL.80a0007e.json`, tests/features.py), and by the same P2 bound check.
- `coordinator.py:5660 GUARD_OFF`: pinned (`HeatPumpOptimizerCoordinator._async_learn_house_heat_loss.GUARD_OFF.ce809cca.json`, tests/features.py), and by the P2 sentinel check `the house and lower-floor loss learners both gate the residual through _loss_residual_rejected` (tests/dst_checks.py).
- `coordinator.py:5778 GUARD_OFF`: pinned (`..._async_learn_lower_floor_loss.GUARD_OFF.d05a0947.json`, tests/features.py), and by the same P2 sentinel check.
- `optimizer.py:1987 BOOLOP`: pinned (`OptimizationResult.sensor_trajectory.BOOLOP.cc727924.json`, tests/features.py); the value check `R10-CLONE-2238 P3: sensor_trajectory is the upper floor only in two-zone mode with an upper trajectory, else the room` also kills its mutant (`and` -> `or`, run at 12992bed): single-zone read the upper floor `[19.0, ...]`.
- `optimizer.py:1987 GUARD_OFF`: pinned (`sensor_trajectory.GUARD_OFF.cc727924.json`, tests/features.py), and by the same P3 rule check.
- `optimizer.py:1989 RETURN_DEL`: pinned (`sensor_trajectory.RETURN_DEL.1a942d8c.json`, killed by tests/manual_plan.py).
- `sensor.py:419 GUARD_OFF`: pinned (`_WaitsForEvidenceMixin._evidence_attributes.GUARD_OFF.5f1c8d82.json`, tests/entities.py).
- `tariff.py:546 RETURN_DEL`: pinned (`_window_partition.RETURN_DEL.b25dd300.json`, tests/features.py).
- `tariff.py:652 RETURN_DEL`: pinned (`_window_starts.RETURN_DEL.dd61f966.json`, tests/features.py).
- `tariff.py:873 GUARD_OFF`: pinned (`billed_windows.GUARD_OFF.0a51dd45.json`, tests/features.py).
- `tariff.py:877 CMP_BOUND`: triage `tests/mutation_ledger/survivor_triage/tariff.py/billed_windows.CMP_BOUND.0a51dd45.json`, equivalent: at equal sizes the moved branch appends `np.ones(0)`, the same values.
- `tariff.py:877 GUARD_OFF`: pinned (`billed_windows.GUARD_OFF.c32091bc.json`, tests/features.py).
- `tariff.py:880 RETURN_DEL`: pinned (`billed_windows.RETURN_DEL.dad1dd16.json`, tests/features.py).

## Null control

- `enumerate_p2.py --fixture` (the clean synthetic package) reads 0 in all seven families, at base and at head.
- Failing test first: each sentinel check run against the production code one commit before its owner landed fails, and passes at its own commit (figures below).
- The P2 registry entries pass at the head with zero hits outside their owner, and fail at base on every copy, so the rule is not vacuous.
- Probes: `probes_p2.py --perturb` re-inserts the retired `0.05` copy at probes 3-6 and reads 4 FAIL, against 6/6 PASS unperturbed.

## Figures

All at the head unless stated; base = `git archive origin/main` export at 28482ece; head figures re-taken at fe40be98.

- F5_clone: 24 classes at base, 15 at head. `python3 -I dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py --json`, read `F5_clone`, keyed by function names with line numbers stripped. Base `$EXPORT/dev/audit/rounds/round10/D14/sweep-P2/enumerate_p2.py` sha1 9a02577e652d525e1ed23a301d9bf49ba192f5e3. LEFT: exactly the nine pairs above; ENTERED: none (the other 15 differ only in line numbers). Null: `--fixture` reads `fixture.F5_clone=0` and `fixture.total=0`.
- Per commit, the same enumerator on each commit's export: P1 24->23, P2 23->22, P3 22->21, P4 21->20, P5 20->19, P6 19->18, P7 18->17, P8 17->16, P9 16->15, each LEFT exactly its own pair and ENTERED none. `_accumulate_energy`/`_maybe_run_fuse_advisor` left with P1 as the note predicted: the fuse advisor's two reads are a different fact, and its class matched only on the split's shape.
- Architecture score: `python3 tools/audit/archscore/score.py --diff origin/main` reads `dS +4.7870 IMPROVES`; `duplication_copies 28 -> 19`, `coord_footprint 2491 -> 2489`, `shape_copies 42 -> 40` (gate only). No metric rises.
- Structure: `python3 tests/structure.py` at base reads `class_excess_loc` 17585, `duplication_copies` 14, `max_class_loc` 7955 (each at zero headroom); at head 17561, 10, 7934. Re-recorded with `--record` in its own commit, rows named in its message; no raise.
- Probes: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py` reads `probes_failed=0`, `probes_total=6` (probe 6, `_observe_frequency`, now evaluates: `watch_active=False owner_runs=False`, PASS); `--perturb` reads `probes_failed=4` (probes 3-6 FAIL). At base the same script (sha1 2ad5991474c2cd23bfe30ccebbea2b273e37018f) stops with `LookupError: ('freq_control.py', 'evidence_exhausted', 'target_kw <=')`.
- P2 registry: the nine new entries in `tests/entities.py`'s P2 owners block (`_p2_registry`), driven alone over a package (scratch `p2scan.py`, which execs that block). Head: each `ok`, owner hit only. Base production code: planned_split SEAM 1219, 10153, 10154 + OWNER-MISSING; loss_residual_gate SEAM 5633, 5756; sensor_trajectory SEAM coordinator 10069, 10118, optimizer 4105, 4480; billed_window_pad SEAM optimizer 4934, tariff 876, 1169; plan_window_count SEAM optimizer 3377, 3396; evidence_attributes SEAM sensor 1915, 2413, 2806; ranked_peak_lists SEAM tariff 332-333, 413-414; window_partition SEAM tariff 557, 1077; window_starts_walk SEAM tariff 649, 672; each with OWNER-MISSING.
- Failing test first: each pair's check, run against the production code of the commit before its owner (the head's tests, production files checked out from that commit), fails, and passes from its own commit on. P1 (tests at cef2172b, production at base): `FAIL ... P1` (ledger space kWh 1.5, diag 1.5). P2 and P9 (production at base): `FAIL ... P2` (gated `[]`), `FAIL ... P9` (factors all 0.0, days the real ordinals). P3 (tests at d18bd0f3, production at b992309c): features.py stops with `AttributeError: type object 'OptimizationResult' has no attribute 'sensor_trajectory'` at the fake that binds the owner. P4 (production at d18bd0f3): `FAIL ... P4` (peak_kw 1.0, peak_cost 0.0) with P1 and P3 `ok`. P5 (production at db32dc6c): `FAIL ... P5` (factors 24, days 24) with P4 `ok`. P6 (production at bd832d50): `FAIL ... P6`. P7 (production at 54a1511a): `FAIL ... P7` (calls `[]`). P8 (production at 15b55663): `FAIL ... P8` (scalar `[1.5 5.5]`) with P7 `ok`.
- Golden: the scoped gate ran golden in drift mode (`GOLDEN_MODE=drift`, so `tests/golden.py` hands the fixtures to `python3 tests/env_drift.py --all origin/main`): `NO UNCLAIMED DRIFT: 56 scenario(s) checked against origin/main` and `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`; every named fixture reads `byte-identical to origin/main here` or, for a may-drift one, `did not move here`. Null: the same run reports 34729 leaves differing from the committed files in value alone, which is the dev-box BLAS difference `env_drift.py` reports and never fails on, so the comparison that matters is the one against origin/main's own capture. These cover P1-P3 and P7 (the `coord_*` fixtures) and P3's optimizer sites plus P5 (`capacity_tariff`, `capacity_tariff_15min`, `peak_masked`, `shoulder_two_zone`, `tariff_plus_two_zone`). No claim file is touched.
- Scoped gate: `GATE_SCOPE=auto GOLDEN_MODE=drift bash tests/run.sh` at fdb98e24: `MODE: SCOPED -- 27 script(s) run, 6 scoped out.`, `29 TEST SCRIPT(S) PASSED; 5 SCOPED OUT AND NOT RUN` (including `ALL 4883 FEATURE CHECKS PASSED`, `ALL 2650 ENTITY CHECKS PASSED`, `ALL 137 DST / QUARTER-GRID CHECKS PASSED`, `ALL 113 STRESS CHECKS PASSED`).
- Typing: `/opt/hpo/venv-ha/bin/python -m mypy --strict custom_components/heatpump_optimizer/` reads `Success: no issues found in 85 source files`; `python3 tests/typing_ruler.py` reads `ALL 12 typing-ruler source checks PASSED`.

## Red checks

Read from the check-runs of the PR's heads, with every page read (`list_workflow_jobs` per run, both pages of each: 42 jobs at a46e4d02, 40 at fe40be98; the PR-head check-runs read of fe40be98 returned 81 runs, no page left). The runs I could read are those at a46e4d02 (run 42329898240, attempt 2) and at fe40be98 (run 42339342568, attempt 5; a second run 42339338428 of the same head, whose 40 listed check-runs are all green or skipped). I did not find a separate run at the earlier handoff head ed225e75, so I name none for it.

At the head fe40be98: no check run concluded red. `gate` (job 128380226082, attempt 5) concluded success, as did `tests / mutation` (128362659151), `tests / closures`, `tests / fast (3.14)`, `tests / typing`, `pr-contract / pr-contract` (128380088617), `arch-score / arch-score`, `governance / instrument-self-tests`, `budget-raise-gate / budget-raise-gate`; the rest are success or skipped.

Reds a later push cleared, at a46e4d02 (two concluded red):
- `tests / mutation` (run 42329898240, job 128291088162), failing step `Drive the table over what this diff tested`: `MUTATION TABLE REFUSED -- 2941 unpinned site(s) against 2939 at the ratchet base f2a01514, 14 of them added by this diff`. Class: newly added unpinned sites, the kind `tools/pr/ci_predict.py` already predicts (it ran in `prepr.sh` step 6d before the handoff and named the eight stale pins repaired in the ledger commit). Answer: the `mutation-autofix` job (job 128303174886, success) pinned the 14 sites in `fe40be985`; `tests / mutation` at fe40be98 (job 128362659151 in run 42339342568) concluded success. Cheaper detector: none owed; `ci_predict.py` lists the sites and the autofix lane exists for them.
- `gate` (run 42329898240, job 128303555285, step `Judge this head`, kind edit): `FAIL run(s) [42329898240] at this head are still being judged; their gate decides`, the edit-run deferral (R10-HOTFIX-GATE-BUSY-DEFER) that waited on `tests / mutation` above. Answer: cleared at fe40be98, where `gate` (job 128380226082, attempt 5) concluded success. Cheaper detector: none owed; the deferral is the designed behaviour.

Not red: `governance / instrument-self-tests` completed success at both heads (no 30-minute cancellation).

Local scoped-gate reds before the handoff, each on a script I had turned red myself and fixed in its own commit:
- `tests/features.py`: P4's new check built `CapacityTariff(marginal_price_per_kw=...)` (a property, not a field) and patched only `tariff.billed_windows` while the optimizer binds the name by import; a third, P8's check calling a bare `metering_windows` features.py never binds, raised NameError. Cheaper detector: running the new check block alone before the 6-minute script, which I then did; standing cost nil, so no countermeasure to build.
- `tests/typing_ruler.py` (pinned census `--mypy`): +3 errors from the new P4/P6 owners (a `str` key into the `Payload` TypedDict, an ndarray product read as Any). Cheaper detector: `mypy --strict` over the package, about a minute, which exists and which I had not run before the gate; no new detector is owed.

## Forward-carry

- The brief's Carry 1 (item 5831fe5b, the frame-read bound in `_read_reply`) and Carry 2 (item 4233c20f, the diagnose-service translation in `services.py`) are on the unmerged `fix/r10-ext-3226` branch, not on main; this diff touches neither the process-worker transport nor `services.py`, so there is nothing of them for this group to own. Carry: dismissed: lands with r10-ext-3226 itself (item 5831fe5b). Carry: dismissed: lands with r10-ext-3226 itself (item 4233c20f).
- Design carry bugclasses-json: `dev/audit/config/bugclasses.json`'s P2 entry lists the nine pairs as `sw:` instances, with one `status` for the whole entry and no per-instance closed marker. The file is left untouched: marking nine instances closed would need a per-instance field the schema does not have, and the in-tree record of their closure is the P2 registry entries this PR lands. Carry: dismissed: no per-instance marker exists.

## Friction

none
