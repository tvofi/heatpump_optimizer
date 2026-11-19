# D14-s1, round 11: recurring bug classes (open and prototype-only axis)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`, box B7 (x86_64, 4 vCPU, Python 3.14.7). Steps D14.M2, M3, M4 over the 20 classes printed by:

    jq -r 'to_entries[]|select(.value.status? == "open" or .value.status? == "prototype-only")|.key' dev/audit/config/bugclasses.json

## Method

Each detector under this directory hooks a production seam, enumerates the class's seams across the package (not only known instances), re-finds a listed instance at a pre-fix tree (`git archive <sha> | tar -x`, run from that export's root), reads 0 (or the baseline count) on the baseline, and moves under a one-line in-memory perturbation. Every count is contention-immune; every wall number is provisional (load1 4.6-12 during the fan-out).

## Findings

### D14-s1-01 (N-step-grid, medium): N-step-grid: services.yaml thermal selectors keep the off-grid (min, step) pairs #1679 removed from the config flow

At 92d38ecb, 6 of 47 services.yaml number selectors (set_thermal_parameters: slab_thermal_mass, slab_heat_transfer, upper/lower_floor_thermal_mass, inter_zone_heat_transfer, window_area) have both their max and their documented example off their own min+k*step grid in HA's default slider mode (12 seams), the same (min, step) pairs the R9 D4-s2-05 fix took off the options flow; and config_flow._widen_to_fit moves a slider's grid base to a stored out-of-range value, putting the field's own default off grid on 28 of 28 slider fields with a constant default.

- Mechanism: The grid base of an HTML number input and ha-slider is min. #1679 set step "any" on box fields in config_flow._number only; the service surface declares the same min/step pairs in YAML (0.02 + k*0.1 never reaches 0.8 or 5.0), and _widen_to_fit rewrites min to the stored value without snapping it to the field's step, so every nominal value of a widened slider becomes unreachable.
- Evidence: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/step_grid.py` -> 40 seams (seams_services=12, seams_widen=28, seams_options=0)
- Perturbation: --perturb-svc: services.yaml number selectors read with step "any" (the #1679 fix carried to the service surface); --perturb-widen: _widen_to_fit snaps the widened min onto the field's own grid; --perturb-min: target-temperature slider min 15.2 -> seams_services 12 -> 0; seams_widen 28 -> 0; seams_options 0 -> 2 under --perturb-min (up)
- Property: Every number selector the integration exposes (options flow, widened options field, service field) admits its own max and its own default/example as reachable values: either step is "any" or (value - min) is an integer multiple of step.
- Seam rule: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/step_grid.py`
- Proposed barrier and fix: services.yaml set_thermal_parameters number selectors: mode box + step any (or min on the step grid); config_flow._widen_to_fit: when widening a slider, snap the new min down to old_min - ceil((old_min - v)/step)*step; barrier: this detector as a tests/config_flow_steps.py check over all three surfaces (sub-second)

### D14-s1-02 (N-finally-return, low): N-finally-return: one live return-inside-finally seam and no class barrier beyond the single nightly_ha pin

An AST walk of all 1069 .py files in the export finds 1 jump escaping a finally (dev/archive/handoff/r9-f2-solver-4/mutation_proof.py:224, which returns 2 from the restore finally and so discards a KeyboardInterrupt or runner exception in flight from sh()), re-finds the R9 D7-s3-51 seam at 957f4a1ed7^ (tests/nightly_ha.py:1274), and the only shipped guard is tests/entities.py's behavioural pin of that one function.

- Mechanism: A return/break/continue in a finally body replaces the in-flight exception (PEP 765); CPython 3.14 only emits a SyntaxWarning at compile, which a cached .pyc or a warnings filter hides, and no lint lane makes it an error.
- Evidence: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 -W ignore dev/audit/rounds/round11/D14/s1/finally_escape.py` -> 1 seams (RESULT seams_baseline)
- Perturbation: --reintroduce: a one-line `return None` inserted in memory at the first finally of custom_components/heatpump_optimizer/coordinator.py (line 1942) -> RESULT seams 1 -> 2; runtime_swallowed 0 -> 1
- Property: No return/break/continue escapes a finally anywhere in the repository; an exception in flight from the try always propagates.
- Seam rule: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 -W ignore dev/audit/rounds/round11/D14/s1/finally_escape.py`
- Proposed barrier and fix: dev/archive/handoff/r9-f2-solver-4/mutation_proof.py: set a flag in the finally and return after it; barrier: the AST walk (about 1 s over 1069 files, provisional) as a tests/ or tools/policy lint check, or `python -W error::SyntaxWarning -m compileall -f -q` in the lint lane

### D14-s1-03 (P8, medium): P8: the options dialog labels and bounds money in the instance currency while every published figure is in the feed's

On a SEK instance priced by a EUR/kWh entity feed, 5 of 20 money surfaces at 92d38ecb resolve to SEK while the feed and all 13 entity surfaces resolve to EUR: the four options-flow money fields built by config_flow._money (grid_fee_fixed, contract_fixed_price, wood_price_sek_m3, compressor_replacement_cost) and the grid-fee page's currency placeholder; on a HUF instance the grid-fee validation bound (config_flow._fee_placeholders -> grid_fee.fee_bound) is 500 against a feed-scaled 10, a sixth seam; a SEK/kWh feed (null) reads 0.

- Mechanism: #1657 moved the coordinator to feed-first precedence (coordinator._feed_currency or resolve_currency) but config_flow._money, _fee_placeholders and _grid_fee_errors still call currency.resolve_currency (instance-first). The value typed into those fields is added unconverted to feed-denominated prices (grid_fee.GridFeeSchedule.from_config), so the label names the wrong currency and the implausible-fee bound is scaled by the wrong currency; the price_currency repair names the disagreement but does not remove it.
- Evidence: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/currency_precedence.py` -> 5 money surfaces disagreeing with the feed currency (of 20)
- Perturbation: --perturb: config_flow.resolve_currency bound to the coordinator's precedence (coordinator._feed_currency(hass, cfg) or the instance currency), one line -> money_seams 5 -> 0
- Property: Every surface that shows, accepts or bounds a money amount resolves its currency by one precedence: the price feed's declared currency first, the instance currency only where the feed declares none.
- Seam rule: `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/currency_precedence.py --instance HUF`
- Proposed barrier and fix: one resolver for money surfaces that takes the entry config (feed first) used by config_flow._money, _fee_placeholders, _grid_fee_errors and the coordinator; barrier: this detector as a tests/config_flow_steps.py or tests/entities.py check (one coordinator build, about 3 s, provisional)

## Non-findings (class detectors that read zero at baseline)

- P10: no CPU kernel (ThermalModel.simulate_*, sysid fits, HeatPumpOptimizer.optimize, scipy minimize/linprog, numpy.linalg solve/lstsq/inv/pinv/cholesky) runs on the loop in any of the 5 replay arms, nor on an executor outside the fallback arm. `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/p10_kernels.py`: seams=0; base worker=1163 loop=0; fallback executor=1160 loop=0; sysid worker=2330; away 1346; learner 1168; --perturb (worker hop removed) seams=3, base loop=1163; 3490cb16 base loop=2304
- N-name-sort: no family splits under the en/sv/de name sorts over the 82 live entities, families from key tokens, overrides and shared English lead words. `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/name_sort.py`: split_families=0 over 16 families; --perturb 1; 3defa2d58^ 3 (en/sv away, sv compressor)
- N-reap-lock: every stop route reaps a real worker running a live silent job without waiting on _PROCESS_LOCK. `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/reap_lock.py`: pool/pool_at_exit/pool_stopped ratios 0.000/0.000/0.000, lock free after; --perturb 1.010/1.012/1.226 (3 seams); --idle 0.024/0.000/0.001; 1c4d70fdd^ 1.007/1.008 (provisional wall, load1 8.8-12)
- N-registry-leak: no torn coordinator stays reachable and no module-level container grows per cycle, reload and remove+add arms. `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/registry_sweep.py [--fresh-entry]`: torn_alive=0, registry_seams=0 over 107 containers; --perturb torn_alive=5, 11 registries; fresh-entry arm first read off_restore._RECORDS 0->5, a harness gap (tests/harness.py keeps removed entries in hass.config_entries), 0 once removal is modelled
- N-future-clamp: no instant the integration saved is rewritten by its own load at the same clock. `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/future_clamp.py`: clamp_seams=0 over 16 stores, 15 future leaves (accuracy lead_pending, snapshots); --perturb (ahead_h=0) 2
- N-leaf-imports-solver: no module outside the solver side and the coordinator's platforms loads the optimizer or scipy. `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D14/s1/leaf_imports.py`: leaf_seams=0 of 95 (84 clean, 3 solver side: coordinator, dhw_planner, optimizer; 8 via coordinator); --perturb 15; 234087a510^1: 7

## Coverage

### D14.M2: 20/20 examined

Every open/prototype-only class has a disposition: 9 measured here with a committed detector (P8, P10, N-name-sort, N-finally-return, N-step-grid, N-reap-lock, N-registry-leak, N-future-clamp, N-leaf-imports-solver), 11 under unfinished with the reason. C2: P8 now has a detector (currency_precedence.py, 5 seams at baseline, 18 at 3490cb16). C6: N-name-sort (name_sort.py), N-step-grid (step_grid.py), N-reap-lock (reap_lock.py) all picked and measured.

Redispatched: C2 examined, C6 examined

### D14.M3: 9/20 examined

Detectors under dev/audit/rounds/round11/D14/s1/: each re-finds at a pre-fix tree and moves under a one-line perturbation. finally_escape.py 1 seam (957f4a1ed7^: 1); step_grid.py 40 (26704a4e9f: box_pinned 43); currency_precedence.py 5 (3490cb16: 18; null 0); p10_kernels.py 0 over 5 arms (3490cb16: 2304 loop calls, topology._advisor_replay; c4e1e0c072^: 0; perturb 3 seams); name_sort.py 0 (3defa2d58^: 3); reap_lock.py 0 (1c4d70fdd^: ratio 1.007/1.008; perturb 3 routes); registry_sweep.py 0 over 107 containers (perturb torn_alive 5, 11 registries); future_clamp.py 0 over 16 stores (perturb 2); leaf_imports.py 0 over 95 modules (234087a510^1: 7; perturb 15). C1: c4e1e0c072^ base arm re-run (0 loop calls: the advisor seam was already moved on that branch), 3490cb16 re-finds 2304; the _replay_interval seam is driven by tests/replay.py's learner arm (worker 1168 vs base 1163, 0 loop). C3: P8 re-found at 3490cb16 (18 surfaces); config_flow fee-bound seams probed (_fee_placeholders, fee_bound: a seam on a HUF instance). C5 not reached: N-staleness is barriered, D14-s2's axis.

Not reached:

- N-postreview-merge-red: its census reads check-runs at recarry heads from the GitHub API; D14 may not read GitHub and no local arm was built
- N-approval-rebuy: needs per-PR reviewed vs merged patch-ids from GitHub reviews; not readable under the wall
- N-gate-yield: needs the blocked-verdict population from PR reviews on GitHub
- N-period-rollover: a detector over every period-boundary aggregate (tariff.PeakTracker month, ledger months, day counters) was not built for time
- N-confounded-learner: needs a covariate-error probe per residual-fed learner; not built for time
- N-order-coupling: needs an enumeration of destructively-read shared intervals and call-order permutation; not built for time
- N-restore-race: needs a writer injected inside every store load await; not built for time
- N-p2b-assembly-reader: no detector idea in the ledger; needs CI push-run history
- N-dispatch-overreach: the ledger detector reads the Actions API; a static arm (5 code dispatch callers found: stamp.py dispatch_record_beat, merge_train.py launch, beat_jobs.py pages.yml, ci_probe.py, sweep_selftest.py) evaluating each target workflow's job if: under workflow_dispatch was not built for time
- N-stamp-claim-conflict: a throwaway-repo arm (base with claim lines, stamp commit emptying them, branch adding a claim, merge through the claimnotes driver) was not built for time
- N-orphaned-handoff: the predicate reads handoff refs and PRs on origin; not readable under the wall

Redispatched: C1 examined, C3 examined, C5 not_reached

### D14.M4: 9/20 examined

Findings D14-s1-01 (N-step-grid), -02 (N-finally-return), -03 (P8); non-findings with a class detector for P10, N-name-sort, N-reap-lock, N-registry-leak, N-future-clamp, N-leaf-imports-solver. C4 not reached: the detector/barriered-axis sweep is D14-s2's cells.

Not reached:

- N-postreview-merge-red: no detector this round (see D14.M3)
- N-approval-rebuy: no detector this round (see D14.M3)
- N-gate-yield: no detector this round (see D14.M3)
- N-period-rollover: no detector this round (see D14.M3)
- N-confounded-learner: no detector this round (see D14.M3)
- N-order-coupling: no detector this round (see D14.M3)
- N-restore-race: no detector this round (see D14.M3)
- N-p2b-assembly-reader: no detector this round (see D14.M3)
- N-dispatch-overreach: no detector this round (see D14.M3)
- N-stamp-claim-conflict: no detector this round (see D14.M3)
- N-orphaned-handoff: no detector this round (see D14.M3)

Redispatched: C4 not_reached

## Barrier cost (provisional wall, load1 about 9)

- step_grid.py 0.9 s, currency_precedence.py 1.8 s, name_sort.py 1.4 s, finally_escape.py 19 s (1069 files plus one `git show`; an AST walk limited to tracked .py files under tools/ tests/ custom_components/ is the barrier shape), leaf_imports.py 44 s (one interpreter per module; the existing tests/features.py block pins 4 leaves).

## Unfinished

- D14.M3: N-postreview-merge-red: its census reads check-runs at recarry heads from the GitHub API; D14 may not read GitHub and no local arm was built
- D14.M3: N-approval-rebuy: needs per-PR reviewed vs merged patch-ids from GitHub reviews; not readable under the wall
- D14.M3: N-gate-yield: needs the blocked-verdict population from PR reviews on GitHub
- D14.M3: N-period-rollover: a detector over every period-boundary aggregate (tariff.PeakTracker month, ledger months, day counters) was not built for time
- D14.M3: N-confounded-learner: needs a covariate-error probe per residual-fed learner; not built for time
- D14.M3: N-order-coupling: needs an enumeration of destructively-read shared intervals and call-order permutation; not built for time
- D14.M3: N-restore-race: needs a writer injected inside every store load await; not built for time
- D14.M3: N-p2b-assembly-reader: no detector idea in the ledger; needs CI push-run history
- D14.M3: N-dispatch-overreach: the ledger detector reads the Actions API; a static arm (5 code dispatch callers found: stamp.py dispatch_record_beat, merge_train.py launch, beat_jobs.py pages.yml, ci_probe.py, sweep_selftest.py) evaluating each target workflow's job if: under workflow_dispatch was not built for time
- D14.M3: N-stamp-claim-conflict: a throwaway-repo arm (base with claim lines, stamp commit emptying them, branch adding a claim, merge through the claimnotes driver) was not built for time
- D14.M3: N-orphaned-handoff: the predicate reads handoff refs and PRs on origin; not readable under the wall
- D14.M3: C5 (N-staleness quiet-night fixture, MODE_LAST_GOOD consequence): barriered class, outside this seat's axis (D14-s2)
- D14.M4: C4 (detector/barriered classes swept for new seams): outside this seat's axis (D14-s2)
- D14.M3: coverage limits of the delivered detectors: registry_sweep.py and future_clamp.py drive one topology (minimal resp. coord_all_features, no boost press, away set or manual plan), so stores and registries only those actions populate are unexercised; reap_lock.py cannot simulate a child stuck in the kernel (D state)

## Leads

- unknown: custom_components/heatpump_optimizer/sensor.py entity_category of family members (learning, optimization, dhw, cost, indoor, prediction, wood): 7 of 16 entity families split across entity_category (none vs diagnostic), so Home Assistant's device page shows them on separate cards although the name sort keeps them together (name_sort.py RESULT category_split_families=7, informational); outside the name-sort class

## Harnesses

- `dev/audit/rounds/round11/D14/s1/finally_escape.py`
- `dev/audit/rounds/round11/D14/s1/step_grid.py`
- `dev/audit/rounds/round11/D14/s1/currency_precedence.py`
- `dev/audit/rounds/round11/D14/s1/p10_kernels.py`
- `dev/audit/rounds/round11/D14/s1/name_sort.py`
- `dev/audit/rounds/round11/D14/s1/reap_lock.py`
- `dev/audit/rounds/round11/D14/s1/registry_sweep.py`
- `dev/audit/rounds/round11/D14/s1/future_clamp.py`
- `dev/audit/rounds/round11/D14/s1/leaf_imports.py`

## Exposure

bugclasses.json (all open/prototype-only entries) and, from this worktree's .git, the instances' fix and pre-fix commits: 957f4a1ed7 and 772da27fd4 (D7-s3-51), 1938fc88de and parent 26704a4e9f (D4-s2-05), 234087a510 (#2371 leaf imports), 81ae048e8b (#2329 registry leak) with dev/audit/harnesses/r10_registry_leak.py (its scaffolding copied into registry_sweep.py and future_clamp.py), 3defa2d58 (#1760), 35b7548073 (D7-s3-53 message), 3490cb16 (P8/P10 pre-fix), c4e1e0c072 (P10), 1c4d70fdd (D1-s2-05), adcb782bd1 (#2230 message); dev/audit/rca/r10-process-worker-hang.md (first 60 lines), dev/audit/harnesses/silent_peer_waits.py header; the in-tree barriers tests/replay.py P10 arm, tests/entities.py #1760 block and D7-s3-51 pin, tests/features.py R10-LEAF-IMPORTS and D1-s2-05 blocks, tests/config_flow_steps.py D4-s2-05 block. No GitHub read.
