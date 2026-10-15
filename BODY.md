R10-I1, the class "a guard whose deletion leaves the gate green" (#2219). Tests and the stress gate only; no production line changes.

Closes #2219.

The class RCA (#2219: a barriered class leaked) belongs to the root-cause seat beside this fix. It is not in this PR.

What changed:

- `tests/features.py`, D3 findings. **D3-s1-01**: a fetch that raises while a previous forecast exists must keep that forecast, marked stale. With no forecast and no entity state, the fetch fabricates nothing. **D3-s1-02**: a four-step plan whose optional schedules are two steps long. Inside them, every key is read. Past them, every one of the twelve `X and i < len(X)` guards in `get_current_action` falls back and nothing raises. **D3-s2-01**: the ledger and snapshot-ring loaders each log one `Quarantined 1 ...` WARNING on a malformed load and none on a clean load.
- `tests/features.py`, the sweep. The I1 sweep (`sweep-I1.md` at d23205d13) lists seventeen guard sites beyond the findings. One self-contained block hands each of them a series two steps short.
- `tests/closures.json`: the three new harnesses are added by hand to `tests/harness_headers.py`'s `inert_reads`, because `ci_predict` named them as INERT READS and `derive_closures --single` does not clear an inert read.
- `tests/stress.py`, **D9-s3-01**. `WORK_PROBE_DRIVER` now captures each baseline scenario's `solve_cpu_ms`. `solve_cpu_median` takes the median, over `work_drift_compare`'s covered scenarios, of this tree's solve CPU per unit of the baseline's, dividing out the work the counts vouch for. `solve_cpu_over_verdict` judges that median at `SWEEP_SOLVE_CPU_FACTOR = sqrt(DETECTION_TARGET)`, the file's own geometric-midpoint rule. The detection check refuses a factor at or above `DETECTION_TARGET`. Synthetic arm (b4) pins three things: the 2x fires, the null stays quiet, and neither counted growth nor a single scenario moves the median.

Alternatives for D9-s3-01, and why each lost:

1. `STRESS_SCENARIO_FACTOR` 1.5, the finder's perturbation. It fires, but this factor is judged against the recorded table, and `SCENARIO_BUDGET_FACTOR`'s note records cross-platform bimodality of 2.28x. On CI it would false-fail.
2. Per-scenario solve CPU against the baseline beside the run. Same-box movement of 1.10-1.44x (#346) against a 2x signal: the razor that the kernel channel needs a doubt band and re-solves to ride.
3. Cost-weighted sum. It is dominated by the few dearest scenarios, so it inherits their per-scenario noise.

The median of 54 same-machine ratios clears the noise without re-solves, and costs nothing extra: the baseline capture already solves every scenario. What it does not see is a slowdown confined to under half the covered scenarios. That stays with the per-scenario channels, and the constant's comment says so.

## Head

665f903c2. That is 4098a04cf merged with origin/main 78324e4a1, plus the inert-reads commit 665f903c2. The figures below were taken at 696762ddb, 8aa0dd467 and 4098a04cf, as each row names, on merge base 5603ee319. Main's delta to 78324e4a1 touches only `.claude/workflows/audit-find.js`, `dev/governance/config/corpus_excluded.json`, `tests/closures.json` and dev records. entities, doc_claims and harness_headers were re-run after the merge.

## Mutation proof

- **features.py, five quiet-window mutants.** Each ran in a detached worktree at 696762ddb with the one-line edit, then `PYTHONPATH=tests/hastub python3 tests/features.py`. Every arm went red:
  - M08 (coordinator `if state or not self._weather_forecast:`) failed "a raising fetch with a previous forecast keeps it, marked stale" [entries 48] and "a raising fetch with no forecast and no entity state fabricates nothing".
  - M01 (`valve_target_schedule` guard `or`) and M03 (`dhw_power_schedule` statement guard `or`) each failed "past a short optional schedule get_current_action falls back on every key and raises nothing" [IndexError].
  - M35 (ledger `if not (dropped):`) failed "the ledger loader warns once per malformed load ..." [clean load warned 'Quarantined 0 ...'].
  - M26 (snapshots, same edit) failed "the snapshot ring loader warns once ...".
  - NULL arm: rc=0.
- **All twelve `get_current_action` guards.** `dev/audit/harnesses/r10_i1_action_guards.py` gives `killed=12` of 12; `--null` gives 0.
- **Seventeen sweep sites.** `dev/audit/harnesses/r10_i1_sweep_guards.py` gives `sites=18 killed=17`; `--null` gives 0. The survivor is `coordinator.py:4060`, which the sweep already dispositions as guarded.
- **stress.py channel.** The (b4) synthetic block was run in memory against the unmutated verdict and three mutants: NULL 0 of 2 failed, `return False` 1 of 2, comparison flipped 2 of 2, factor at `DETECTION_TARGET` 1 of 2. The scratch probe is not landed, because a full-file mutant run of `stress.py` is the required CI mutation check's (fixer.md step 5).

## Null control

- Unmodified tree: the NULL features.py arm rc=0. Both harnesses' `--null` arms kill 0.
- Whole-sweep solve-CPU harness at `--factor 1.0`: `flagged=0`, `median_solve_cpu_ratio=0.977`, `judged=54 of 54`, `count_or_kernel_fired=0` (load1 39.28).

## Figures

- `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_i1_solve_cpu_2x.py --factor 2.0` at 8aa0dd467, under gate lease `r10-i1`: `flagged=1`, `median_solve_cpu_ratio=1.966`, `factor=1.4142`, `judged=54 of 54`, `count_or_kernel_fired=0`, load1 76.60. With `--factor 1.0`: `flagged=0`, median 0.977, load1 39.28. These are machine readings on an 8-core arm64 box carrying other seats' load.
- Finder's harness, `$EXPORT/dev/audit/rounds/round10/D9/s3/gate_blind_2x.py` (sha1 7da56aeaee889c75c1aaa7fafd3496406964e3f0), from the d23205d13 export. It judges only the verdicts it imports (count, kernel, recorded-table, global), none of which this PR changes, so it reads `flagged_solve_arm=0 of 5` at both ends by construction. The companion above applies the new verdict to the same injection (`stress.cpu_scaler` on `HeatPumpOptimizer.optimize`).
- Finder's harnesses at the head, from the same export:
  - `$EXPORT/dev/audit/rounds/round10/D3/s1/forecast_keep.py` (sha1 f211841d10f4a68df42a2ab6246b186fd1e81701): `prior_kept=1`; `--mutant` 0.
  - `$EXPORT/dev/audit/rounds/round10/D3/s1/action_guards.py` (sha1 9da161df29b3f8d1edcbba903555d8f1fb9ec3e6): `live_guards=12`; `--equal` 0.
  - `$EXPORT/dev/audit/rounds/round10/D3/s2/quarantine_warn.py` (sha1 c689f1a1f986b1c765bc36590805c6f5ace3733e): `loaders_correct=2 of_2`, `--mutate` 0. `tests_naming_warning` went from 0 at the base (`git show 5603ee319:tests/features.py | grep -c Quarantined` prints 0) to 1 at the head.
  - These three measure production behaviour, which this PR leaves alone, so they read the same at both ends. What moves is the gate's kill of each mutant (Mutation proof).
- Seam rule (fixer.md step 8): `python3 $EXPORT/dev/audit/rounds/round10/D14/sweep-I1/enumerate_i1.py` at the head gives `seams=34 LEN=30 DROP=2 KEEP=2`. Dispositions:
  - 15 finding sites (the 12 `get_current_action` guards, `coordinator.py:6522`, `ledger.py:306`, `snapshots.py:239`): closed in this diff (Mutation proof).
  - 17 beyond-finding LEN sites: closed in this diff (`r10_i1_sweep_guards.py` killed=17).
  - `coordinator.py:4060`: already guarded (the sweep's disposition).
  - `coordinator.py:9410`: not applicable (the sweep's KEEP false positive, a rollback latch).
- Scoped gate at 8aa0dd467, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=5603ee319 ./tests/run.sh`: MODE: SCOPED, running doc_claims, entities, features, harness_headers and stress. It printed `8 TEST SCRIPT(S) PASSED` and `ALL 110 STRESS CHECKS PASSED`. The real sweep's own null printed `whole-solve CPU: median 0.977x of the baseline beside this run over 54 of 54 covered scenarios`. features.py was then re-run alone at 4098a04cf: `ALL 4125 FEATURE CHECKS PASSED`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

## Red checks

none

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
