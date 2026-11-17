# D3-s2 — round 11, test-suite gaps over the entity/store/payload cells

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`; worktree with one marker commit (HEAD^1 = baseline). Box B2, 4 cores, shared with D0-s2 and D9-s2 (load 6-14); the container restarted twice during the seat. Exposure: none.

## Method

- **M1** `enumerate.py`: the 7 ratcheted operators of `tests/mutation_table.py` over the 18 cell files: 1031 sites, 258 unpinned or recorded `gap`. Weighted RAISE_DEL > GUARD_OFF > CONST > CMP_BOUND > BOOLOP > CLAMP_DROP > RETURN_DEL, known gaps last.
- **M2** `prescreen.py` drove `mutation_table.main --scope full` over that pool to get 22 green traced baselines and the null control (`__init__.py:37 NULL_COMMENT survived every driver`). When the container restarted, `drive_resumable.py` took over. It applies the same verdict rule (`run_script`, `failing_count`, `reach_skip`, `driver_order`, `invalidated_rows`) and resumes at the (mutant, driver) pair. Drivers are the measured closure minus stress/edge/backtest/harness_headers, with `env_drift.py --all HEAD^1`. `tally.py` reads the verdicts.
- **M4** `m4_nonequiv.py` checks each survivor in memory: does the mutated module's output differ on a probe input? The null control (`--identity`) reads 0 of 10.
- **M5** `m5_gate_table.py` records per-script wall and CPU against `closures.json` seconds, plus `optimize()` calls and `Results.check` calls (from `hook/sitecustomize.py`). `m5_reach.py` checks closure over-approximation against the traced baselines.

## M2/M3 prescreened candidates (23 of 258 driven)

| mutant | verdict | drivers run (not reach-skipped) | first failing check |
|---|---|---|---|
| `__init__.py:55 GUARD_OFF unpinned ma1fa94` `if False:` | killed by tests/entities.py | 8 of 20 | a3:roster  [1 registered, 82 in the committed collect() roster; missin |
| `__init__.py:116 GUARD_OFF unpinned md6195f` `if False:` | killed by tests/manual_plan.py | 1 of 20 | ModuleNotFoundError: No module named 'heatpump_optimizer.None' |
| `__init__.py:188 GUARD_OFF unpinned md6195f` `if False:` | LIVES | 12 of 20 |  |
| `__init__.py:210 GUARD_OFF unpinned md6195f` `if False:` | killed by tests/entities.py | 2 of 20 | a downgrade is refused rather than mangled |
| `__init__.py:220 GUARD_OFF unpinned md6195f` `if False:` | killed by tests/entities.py | 2 of 20 | an old entry is stamped forward without touching its data  [every opti |
| `__init__.py:412 GUARD_OFF unpinned md6195f` `if False:` | killed by tests/manual_plan.py | 1 of 20 | unload keeps the published payload object identity |
| `accuracy.py:111 GUARD_OFF unpinned mddf8f5` `if False:` | LIVES | 14 of 20 |  |
| `accuracy.py:238 GUARD_OFF unpinned mddf8f5` `if False:` | LIVES | 11 of 20 |  |
| `accuracy.py:261 GUARD_OFF unpinned mddf8f5` `if False:` | LIVES | 12 of 20 |  |
| `accuracy.py:269 GUARD_OFF unpinned m2560b4` `if False:` | LIVES | 11 of 20 |  |
| `accuracy.py:275 GUARD_OFF unpinned m2560b4` `if False:` | killed by tests/features.py | 1 of 20 | a matured promise scores into its own lead bucket |
| `accuracy.py:352 GUARD_OFF unpinned mddf8f5` `if False:` | killed by tests/features.py | 2 of 20 | an empty tracker reports nothing rather than zero |
| `accuracy.py:364 GUARD_OFF unpinned mddf8f5` `if False:` | killed by tests/features.py | 2 of 20 | IndexError: list index out of range |
| `accuracy.py:379 GUARD_OFF unpinned mddf8f5` `if False:` | LIVES | 14 of 20 |  |
| `accuracy.py:465 GUARD_OFF unpinned mddf8f5` `if False:` | killed by tests/debug_collect.py | 1 of 20 | AttributeError: 'NoneType' object has no attribute 'get' |
| `accuracy.py:470 GUARD_OFF unpinned m7abdc1` `if False:` | killed by tests/features.py | 2 of 20 | AttributeError: 'str' object has no attribute 'get' |
| `accuracy.py:473 GUARD_OFF unpinned m7abdc1` `if False:` | killed by tests/debug_collect.py | 1 of 20 | the monitor self-test re-derives bias from the stored window beside th |
| `climate.py:173 GUARD_OFF unpinned mddf8f5` `if False:` | killed by tests/entities.py | 3 of 11 | hvac_action reports HEATING while the compressor runs at high power  [ |
| `climate.py:285 GUARD_OFF unpinned m2560b4` `if False:` | killed by tests/entities.py | 3 of 11 | HeatPumpOptimizerClimate publishes exactly its pinned attribute keys ( |
| `climate.py:315 GUARD_OFF unpinned mddf8f5` `if False:` | killed by tests/entities.py | 3 of 11 | setting hvac off reaches the coordinator as mode off  [[]] |
| `climate.py:319 GUARD_OFF unpinned mc0eeb5` `elif False:` | killed by tests/entities.py | 3 of 11 | setting hvac HEAT reaches the coordinator as mode comfort and publishe |
| `climate.py:324 GUARD_OFF unpinned mddf8f5` `if False:` | killed by tests/entities.py | 3 of 11 | a target change is recorded as override evidence, then persisted  [[]] |
| `sensor.py:404 RAISE_DEL unpinned m134edf` `pass` | LIVES | 11 of 15 |  |

## M4 — the verifier's question per survivor

- `__init__.py:188 GUARD_OFF unpinned md6195f` — **equivalent**: __init__.py:186 `if payload is None or stamped_at is None: return None` in _take_fresh_handover; every arm returns None anyway (as_utc(None) -> AttributeError -> return None); m4_nonequiv.py distinct_take_fresh_handover_none=0. No check should fail; triage equivalent.
- `accuracy.py:111 GUARD_OFF unpinned mddf8f5` — **equivalent**: accuracy.py:111 `if not raw: return None` in AccuracySample.from_dict; stored_instant('None'/'') returns None, so the same None comes back; distinct_sample_from_dict_falsy_t=0. Triage equivalent.
- `accuracy.py:238 GUARD_OFF unpinned mddf8f5` — **equivalent**: accuracy.py:238 non-finite predicted_temp guard in note_lead_prediction; shadowed by the scoring loop's own isfinite(predicted) filter (:269) and from_dict's (:522); distinct_note_lead_nan_predicted=0.
- `accuracy.py:261 GUARD_OFF unpinned mddf8f5` — **GAP**: accuracy.py:261 `if not np.isfinite(actual_temp): return` in score_lead_predictions; a check feeding a NaN actual after a finite one and asserting sigma finite (tests/features.py lead-bucket block, beside 'a matured promise scores into its own lead bucket') should fail; distinct_score_lead_nan_actual=1 (sigma 0.5 -> nan, persistent). Finding D3-s2-02.
- `accuracy.py:269 GUARD_OFF unpinned m2560b4` — **equivalent at every reachable input**: accuracy.py:269 `if not np.isfinite(predicted): continue`; distinct when a NaN is placed in lead_pending directly (distinct_score_nan_pending_direct=1), but both entry paths filter non-finite first (note_lead_prediction :238, from_dict :522), so no reachable input differs while those hold; it is the third barrier.
- `accuracy.py:379 GUARD_OFF unpinned mddf8f5` — **equivalent**: accuracy.py:379 `if pred.size == 0: return None` in cost_accuracy; with no pairs total_act=0.0 and the |total_act|<1e-6 arm returns None too.
- `sensor.py:404 RAISE_DEL unpinned m134edf` — **equivalent**: sensor.py:404 `raise NotImplementedError` in the abstract _WaitsForEvidenceMixin._waiting_for; all 7 concrete subclasses override it (executed check: 0 inherit the stub). Triage equivalent.

Recorded `gap` survivors in the cells (the ledger already holds them; not driven this round because they are queued last). Their non-equivalence is executed by `m4_nonequiv.py`:
- `inputs.py:590`: setpoint_step `step > 0.0`->`>= 0.0`: an entity advertising target_temp_step 0 -> _on_step divides by 0 (ZeroDivisionError in the set-point write); distinct_setpoint_step_zero=1. Should fail: a check writing a set-point to an entity whose step attribute is 0.
- `ledger.py:739`: roll_receipts retention `[:max(0,len-KEEP_MONTHS)]`->`[:0]`: receipts grow without bound (24 kept -> 27 with 27 months); distinct_roll_receipts_retention=1. Should fail: a check freezing KEEP_MONTHS+n months and asserting len == KEEP_MONTHS.
- `store.py:123`: _sanitize tuple arm off: a NaN inside a tuple leaf survives the store-load scrub; distinct_sanitize_tuple_nan=1.
- `sensor.py:2879`: _gap_energy_rate `rate <= 0.0`->`< 0.0`: a recent_kwh_price of exactly 0 is used instead of falling to current_price (1.7 -> 1.0 in the probe); distinct_gap_rate_zero_recent=1.
- `accuracy.py:555`: plan_promise `steps < 1` guard off: a one-point trajectory yields a promise instead of None; distinct_plan_promise_zero_steps=1.

Top candidates for the quiet-window full gate: accuracy.py:261, inputs.py:590, ledger.py:739, store.py:123, sensor.py:2879, accuracy.py:555.

## M5 — gate table (PROVISIONAL, shared box)

| script | wall s | CPU s | recorded s | wall/recorded | solves | checks | load1 |
|---|---|---|---|---|---|---|---|
| tests/plan_view.py | 1.5 | 1.2 | 1.8 | 0.86 | 1 | 0 | 6.88 |
| tests/arch_score_head.py | 80.4 | 52.0 | 31.8 | 2.53 | 0 | 18 | 8.21 |
| tests/backtest.py | 112.9 | 62.7 | 61.6 | 1.83 | 11 | 25 | 8.9 |
| tests/block_duty.py | 14.0 | 7.9 | 8.3 | 1.68 | 6 | 153 | 8.92 |
| tests/boost_drift_replay.py | 465.7 | 198.5 | 341.1 | 1.37 | 789 | 46 | 12.41 |
| tests/card.mjs | 294.7 | 128.7 | 82.3 | 3.58 | 0 | 0 | 12.13 |
| tests/card_drift.mjs | 19.2 | 8.1 | 6.0 | 3.2 | 0 | 0 | 12.39 |
| tests/config_flow_steps.py | 54.4 | 23.8 | 32.5 | 1.67 | 1 | 586 | 12.31 |
| tests/debug_collect.py | 2.8 | 1.2 | 1.5 | 1.87 | 0 | 163 | 12.31 |
| tests/deployment_shape.py | 6.2 | 2.7 | 3.3 | 1.89 | 0 | 0 | 12.26 |
| tests/doc_claims.py | 26.4 | 11.5 | 11.4 | 2.32 | 2 | 410 | 12.25 |
| tests/edge.py | 52.2 | 22.9 | 21.5 | 2.43 | 21 | 0 | 12.25 |
| tests/entities.py | 1197.7 | 493.9 | 867.9 | 1.38 | 33 | 2744 | 13.8 |
| tests/env_drift.py | 324.2 | 219.3 | 1.0 | 324.24 | 0 | 0 | 10.62 |
| tests/features.py | 1093.2 | 782.5 | 473.9 | 2.31 | 725 | 5917 | 9.23 |
| tests/finite_boundary.py | 110.3 | 98.8 | 90.4 | 1.22 | 0 | 114 | 9.34 |
| tests/frontend.py | 0.2 | 0.1 | 0.1 | 1.52 | 0 | 0 | 9.31 |
| tests/golden.py | None | None | 1.2 | None | None | None | GOLDEN_MODE=drift skips it (run.sh lane_golden) |
| tests/guard_pins.py | 5.4 | 4.5 | 8.2 | 0.66 | 0 | 91 | 9.45 |
| tests/harness_headers.py | 167.3 | 144.7 | 327.6 | 0.51 | 0 | 115 | 10.93 |
| tests/manual_plan.py | 8.6 | 5.6 | 6.5 | 1.32 | 31 | 132 | 10.78 |
| tests/open_meteo.py | 0.2 | 0.2 | 0.3 | 0.81 | 0 | 0 | 10.78 |
| tests/optimality.py | 149.7 | 110.0 | 142.5 | 1.05 | 23 | 84 | 9.93 |
| tests/solar_alignment.py | 1.1 | 0.8 | 1.2 | 0.93 | 0 | 0 | 9.93 |
| tests/stress.py | None | None | 463.0 | None | None | None | quiet window only (D3 trap) |
| tests/structure.py | 32.5 | 21.6 | 21.1 | 1.54 | 0 | 0 | 10.45 |
| tests/typing_ruler.py | 36.9 | 22.8 | 20.8 | 1.77 | 0 | 0 | 11.0 |
| tests/validate.py | 33.1 | 22.3 | 21.5 | 1.54 | 22 | 0 | 10.83 |
| tests/wood_advisor.py | 1.2 | 0.8 | 1.4 | 0.82 | 0 | 25 | 10.84 |

Closure over-approximation (`m5_reach.py`): 296 claimed pairs, 170 of them with a clean reach. In 29 of those the script executes no function body of the cell and does not read it as text. Edits confined to function bodies in payload.py select 525.7 s of the 3051.3 s recorded. See D3-s2-01. env_drift.py is recorded at 1.0 s but costs 324 s wall; this is documented (#934) and handled by `lazy_drivers`.

## Findings

- **D3-s2-01** (low, D3.M5): Import-level closures select 9 scripts (525.7 s recorded) for a payload.py function-body edit none of them executes. Harness `dev/audit/rounds/round11/D3/s2/m5_reach.py`, value 29; perturbation: --claim-only tests/boost_drift_replay.py:payload.py (drop that pair from the closure the count reads, the effect of a body-granular closure for that pair) gives 28 pairs; over_seconds[payload.py] 525.7 -> 184.6 s.
- **D3-s2-02** (medium, D3.M4): No check feeds NaN to score_lead_predictions; dropping its guard poisons lead sigma permanently. Harness `dev/audit/rounds/round11/D3/s2/m4_nonequiv.py`, value 1; perturbation: m4_nonequiv.py --identity (the null mutant old->old) gives 0.

## Non-findings

- closures.json records env_drift.py at 1.0 s though its gate run (--all HEAD^1) costs minutes; it is documented (#934) and mutation_table keeps env_drift eager so the stub seconds never order or budget a sweep: `/root/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/m5_gate_table.py ... (env_drift row) ; grep -n 'env_drift stays eager' tests/mutation_table.py` gives measured 324.2 s wall / 219.3 s CPU vs recorded 1.0 s (provisional, load 10.6); mutation_table.lazy_drivers excludes REF_DRIVEN
- The resumable drive's verdict rule agrees with the instrument's null control: a comment-only edit survives every driver: `see dev/audit/rounds/round11/D3/s2/run/stdout.txt line 29 (prescreen.py over mutation_table.main)` gives null control __init__.py:37 NULL_COMMENT survived every driver (22 drivers)
- All 22 driver baselines are green with clean reach records, so reach-skips are admissible: `grep baseline dev/audit/rounds/round11/D3/s2/run/progress.jsonl` gives 22/22 rc=0 failed=0 reach=true
- Six of seven survivors are equivalent at every reachable input (no test can kill them): `PYTHONPATH=tests/hastub /root/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/m4_nonequiv.py` gives distinct=0 for accuracy.py:111, :238, __init__.py:188; abstract stub sensor.py:404 overridden by 7/7 subclasses; accuracy.py:269 only distinct off every entry path; accuracy.py:379 returns None either way
- Scripts that solve more than they assert (M5): boost_drift_replay.py 789 optimize() calls for 46 checks (0.06 checks/solve), validate.py 22 solves and edge.py 21 solves with 0 harness checks (ISSUES/own counters); no redundancy proven (would need a solve-count ablation): `PYTHONPATH=tests/hastub /root/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/m5_gate_table.py dev/audit/rounds/round11/D3/s2/m5/table.json` gives see m5/table.json; provisional for timing, exact for counts

## Unfinished

- D3.M2: 235 of 258 mutants not driven (time cut: ~6/h at 3 jobs, load ~7). Resume with `PYTHONPATH=tests/hastub $HOME/venv-ci/bin/python3 dev/audit/rounds/round11/D3/s2/drive_resumable.py dev/audit/rounds/round11/D3/s2/drive dev/audit/rounds/round11/D3/s2/run --jobs 3` (pair-level resume from drive/pairs.jsonl; needs HEAD = marker commit over the baseline). Round-10 items C2 (M25-M36 via round10/D3/s1/mutants.py) and C6 are not identifiable here: that harness is absent from the walled export.
- D3.M3: Quiet-window GATE_SCOPE=full GOLDEN_MODE=drift gate for the top six survivors, stress.py included (C3); for this seat the top candidates are accuracy.py:261 then the recorded gaps inputs.py:590, ledger.py:739, store.py:123, sensor.py:2879, accuracy.py:555. C5 (writing round 10's REPORT.md) is the orchestrator's: round 10's directory is not in this export.
- D3.M5: Kill-overlap matrix (every closure script on every mutant, no early stop) not taken (C9): ~240 h serial on this cell set. Duplicate kills therefore unmeasured. All wall/CPU numbers provisional (load 6-14); the quiet window re-takes m5_gate_table.py.

## Harnesses

- `dev/audit/rounds/round11/D3/s2/enumerate.py`
- `dev/audit/rounds/round11/D3/s2/prescreen.py`
- `dev/audit/rounds/round11/D3/s2/drive_resumable.py`
- `dev/audit/rounds/round11/D3/s2/tally.py`
- `dev/audit/rounds/round11/D3/s2/m4_nonequiv.py`
- `dev/audit/rounds/round11/D3/s2/m5_gate_table.py`
- `dev/audit/rounds/round11/D3/s2/m5_reach.py`
- `dev/audit/rounds/round11/D3/s2/hook/sitecustomize.py`

The outputs are in `run/` (prescreen baselines and reach), `drive/pairs.jsonl`, `m4/`, and `m5/`. The files are uncommitted in the seat worktree; only the marker commit holds the earlier versions of the harnesses.
