# D3-s1 wave box D3-g01: full gate for 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Seat D3-s1. Report path `dev/audit/rounds/round11/D3/s1/wave/D3-g01/REPORT.md`; machine-readable twin `REPORT.json`.

## Machine and controls

Counts are final; every wall, CPU and load number is provisional (the judge re-takes it).

```
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087        1097       13486          12        1801       14990
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  18% /
load1 0.84
Sun Nov 22 21:37:09 UTC 2026

== re-fire container (resumed from handoff-wip a4bb8699d3) ==
nproc 4
               total        used        free      shared  buff/cache   available
Mem:           16087         761       14049          12        1548       15325
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.30GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1 0.46
Wed Nov 25 00:46:05 UTC 2026
```

Null control: `fullgate.py null` (comment-only marker), gate_rc 1, red ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] with fail lines {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 3}, wall 3425.2 s. All three are artefacts of the stripped finder tree / branch environment (see gates/null-note.txt); no production-facing check is red, card.mjs did not OOM. fullgate.py counts KILLED only on a script beyond the null or more FAIL lines in one.

Stripped finder worktree of the baseline (prepare_baseline.sh --strip, 1832 files removed) plus the D3-s1 evidence from e3cb5c019b. Read: COMMON.md, D3.md, dev/audit/README.md, the D3-s1 slice reports and m4 answers, the dispatch refs' keys.tsv (to rebuild the wave list only). Not read: the register, round11/J/, any verifier report, docs/ or GitHub. Resumed box: a predecessor container (Intel Xeon @ 2.10GHz) took the null and gates fafb0d2c15e72efb, 0e6080e5385399cb, 021dc21415f3229e, 622996d751dca0c4, 1165914e57f5bd08 and ab918806fc8b4af6 and wrote every probe; this container (nproc 4, Intel Xeon @ 2.30GHz, 16 GB) restored that checkpoint and ran the other ten gates against the restored null. The re-gate of 676e8bfb416ff635 on this container reproduced the null's red set and per-script fail counts exactly (closure.py selftest 2, entities.py 1, harness_headers.py 3), so the null carries across the two containers. Every probe whose record this container wrote was re-executed here; its numbers are the ones recorded.

## Tally

- gated: 16 of 16 (RED-AS-NULL=16)
- KILLED: 0; SURVIVED: 0; RED-AS-NULL: 16 (every one with exactly the null's red set and fail counts); TIMEOUT: 0
- candidates (probe moves): 14; equivalent-candidates: 2; killed: 0
- findings: [] by the brief (ids are assigned at consolidation); candidates are under `gate_survivors`.

| key | site | patch | verdict | wall s | class | probe baseline -> mutant |
|---|---|---|---|---|---|---|
| fafb0d2c15e72efb | custom_components/heatpump_optimizer/coordinator.py:822 CONST | `SOLVE_FAILURE_ISSUE_COUNT = 3 -> SOLVE_FAILURE_ISSUE_COUNT = 6` | RED-AS-NULL | 3271.4 | candidate | issues_after_3=1, first_issue_at=3 -> issues_after_3=0, first_issue_at=6 |
| 676e8bfb416ff635 | custom_components/heatpump_optimizer/coordinator.py:829 CONST | `WORKER_FALLBACK_CAP = 3 -> WORKER_FALLBACK_CAP = 6` | RED-AS-NULL | 2814.7 | candidate | 3 -> 6 |
| 622996d751dca0c4 | custom_components/heatpump_optimizer/coordinator.py:1622 CONST | `BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.15 -> BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.3` | RED-AS-NULL | 3458.6 | candidate | 1 (rate +0.017208 degC/h) -> 0 (rate unchanged) |
| 0e6080e5385399cb | custom_components/heatpump_optimizer/coordinator.py:1624 CONST | `BUFFER_COOLING_MIN_DELTA = 4.0 -> BUFFER_COOLING_MIN_DELTA = 8.0` | RED-AS-NULL | 3387.8 | candidate | 1 (rate +0.006576 degC/h) -> 0 |
| 021dc21415f3229e | custom_components/heatpump_optimizer/coordinator.py:1651 CONST | `HOUSE_LOSS_MAX_STEP = 0.05 -> HOUSE_LOSS_MAX_STEP = 0.1` | RED-AS-NULL | 3295.1 | candidate | (re-anchored, 1.279005) -> (kept verbatim, 1.2) |
| 1165914e57f5bd08 | custom_components/heatpump_optimizer/coordinator.py:1796 CONST | `COP_LEARNING_MAX_STEP = 0.05 -> COP_LEARNING_MAX_STEP = 0.1` | RED-AS-NULL | 3334.3 | candidate | 1.05 -> 1.1 |
| ab918806fc8b4af6 | custom_components/heatpump_optimizer/coordinator.py:10331 GUARD_OFF | `if energy <= 0: -> if False:` | RED-AS-NULL | 3359.2 | candidate | 0 lines [] -> 3 lines ['dhw', 'space', 'spot'] at 0 kWh / 0 SEK (energy and cost totals unchanged) |
| db9b59ec36304943 | custom_components/heatpump_optimizer/coordinator.py:10331 CMP_BOUND | `if energy <= 0: -> if energy < 0:` | RED-AS-NULL | 2798.3 | candidate | 0 lines [] -> 3 lines ['dhw', 'space', 'spot'] at 0 kWh / 0 SEK (energy and cost totals unchanged) |
| cf7be12db1a662c4 | custom_components/heatpump_optimizer/coordinator.py:9613 GUARD_OFF | `if isinstance(prices, dict): -> if False:` | RED-AS-NULL | 2738.5 | candidate | 1.3 -> 1.0 (the snapshot's price-shape model is ignored) |
| 031dba68286ccfbf | custom_components/heatpump_optimizer/coordinator.py:9622 GUARD_OFF | `if isinstance(comfort, dict): -> if False:` | RED-AS-NULL | 2717.5 | candidate | 8.0 -> 5.0 (the snapshot's comfort learner is ignored) |
| 22205dc8a4a6e79b | custom_components/heatpump_optimizer/coordinator.py:9628 GUARD_OFF | `if isinstance(defrost, dict): -> if False:` | RED-AS-NULL | 2716.1 | candidate | 0.8 -> 1.0 (the snapshot's defrost derate is ignored) |
| 37e0face2a901e71 | custom_components/heatpump_optimizer/coordinator.py:7419 CMP_BOUND | `value = solar[i] if i < len(solar) else 0.0 -> value = solar[i] if i <= len(solar) else 0.0` | RED-AS-NULL | 2752.5 | candidate | [100.0, 101.0, 7.0, 0.0, 0.0, 0.0] -> IndexError |
| 68c8ce175dcfa839 | custom_components/heatpump_optimizer/coordinator.py:7422 GUARD_OFF | `if missing: -> if False:` | RED-AS-NULL | 2940.3 | candidate | 1 -> 0 (returned series identical) |
| 97628f4b14aec1b9 | custom_components/heatpump_optimizer/coordinator.py:4497 GUARD_OFF | `if not vvc_entity and not space_entity: -> if False:` | RED-AS-NULL | 3128.3 | equivalent-candidate | [] for every input -> [] for every input (moved 0 of 6) |
| 20f57d1eea0a5a1d | custom_components/heatpump_optimizer/coordinator.py:4508 BOOLOP | `if params.dhw_enabled and params.dhw_windows_active -> if params.dhw_enabled or params.dhw_windows_active` | RED-AS-NULL | 3014.8 | candidate | [('turn_on', 'switch.vvc')] -> [('turn_off', 'switch.vvc')] |
| e0bd801049aba41a | custom_components/heatpump_optimizer/coordinator.py:4524 CLAMP_DROP | `dt_hours = max(ctx._opt_config.dt_hours, 1e-6) -> dt_hours = (ctx._opt_config.dt_hours)` | RED-AS-NULL | 3226.8 | equivalent-candidate | [('turn_on', 'switch.space')] at the production 15-min step -> identical (moved 0 at every production step) |

## Survivors: the step-4 answer per key

### fafb0d2c15e72efb — custom_components/heatpump_optimizer/coordinator.py:822 CONST (candidate)

Patch `SOLVE_FAILURE_ISSUE_COUNT = 3 -> SOLVE_FAILURE_ISSUE_COUNT = 6` in `<module>`. Gate: RED-AS-NULL, gate_rc 1, wall 3271.4 s, load1 0.57..0.93 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key fafb0d2c15e72efb`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_fafb0d2c15e72efb.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_fafb0d2c15e72efb.py`), metric: repair issues 'solve_failures' raised after 3 consecutive failed solves (and the failure count at which the first is raised). Baseline **issues_after_3=1, first_issue_at=3**, mutant **issues_after_3=0, first_issue_at=6**. Inputs tried: 3 and 8 consecutive failures at counts 3 and 6; null: 2 failures (0 issues either way).

Candidate: No check drives three failed solves to the solve_failures repair issue; SOLVE_FAILURE_ISSUE_COUNT 3 -> 6 is unseen. Should have failed: tests/features.py and tests/entities.py execute coordinator.py:705 on the traced baseline but never line 706: no check drives three consecutive failed solves and asserts the solve_failures issue is created on the third. Class guess I1, severity claimed medium; perturbation direction down (issues after 3 failures).

### 676e8bfb416ff635 — custom_components/heatpump_optimizer/coordinator.py:829 CONST (candidate)

Patch `WORKER_FALLBACK_CAP = 3 -> WORKER_FALLBACK_CAP = 6` in `<module>`. Gate: RED-AS-NULL, gate_rc 1, wall 2814.7 s, load1 0.41..0.92 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 676e8bfb416ff635`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_676e8bfb416ff635.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_676e8bfb416ff635.py`), metric: in-process (GIL-holding) solves _await_optimize carries while the process worker is unusable before it raises UpdateFailed. Baseline **3**, mutant **6**. Inputs tried: 10 cycles with ProcessWorkerUnavailable; null: healthy worker, 0 fallbacks either way.

Candidate: No check counts the in-process fallbacks before the worker cap skips the solve; WORKER_FALLBACK_CAP 3 -> 6 is unseen. Should have failed: tests/features.py and tests/entities.py execute coordinator.py:2331-2332 on the traced baseline; neither counts the in-process fallbacks before the skip (no assertion that the fourth consecutive fallback raises process_worker_unusable). Class guess I1, severity claimed medium; perturbation direction up (in-process solves before the skip).

### 622996d751dca0c4 — custom_components/heatpump_optimizer/coordinator.py:1622 CONST (candidate)

Patch `BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.15 -> BUFFER_COOLING_MIN_SAMPLE_HOURS = 0.3` in `<module>`. Gate: RED-AS-NULL, gate_rc 1, wall 3458.6 s, load1 0.85..0.84 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 622996d751dca0c4`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_622996d751dca0c4.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_622996d751dca0c4.py`), metric: buffer-cooling samples folded from one quiet 0.2 h interval 40.0 -> 39.8 degC. Baseline **1 (rate +0.017208 degC/h)**, mutant **0 (rate unchanged)**. Inputs tried: dt_h 0.1 (both 0); 0.15 (1 vs 0); 0.2 (1 vs 0); 0.29 (1 vs 0); 0.3 (both 1); null 0.5 h (identical).

Candidate: No check folds a 0.15-0.3 h quiet buffer interval; BUFFER_COOLING_MIN_SAMPLE_HOURS 0.15 -> 0.3 is unseen. Should have failed: tests/features.py executes coordinator.py:5654 on the traced baseline but feeds no quiet interval between 0.15 h and 0.3 h asserting it is folded. Class guess I1, severity claimed low; perturbation direction down (samples folded).

### 0e6080e5385399cb — custom_components/heatpump_optimizer/coordinator.py:1624 CONST (candidate)

Patch `BUFFER_COOLING_MIN_DELTA = 4.0 -> BUFFER_COOLING_MIN_DELTA = 8.0` in `<module>`. Gate: RED-AS-NULL, gate_rc 1, wall 3387.8 s, load1 0.87..1.0 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 0e6080e5385399cb`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_0e6080e5385399cb.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_0e6080e5385399cb.py`), metric: buffer-cooling samples folded from one quiet 1 h interval 27.0 -> 26.8 degC (7.0 -> 6.8 K above ambient). Baseline **1 (rate +0.006576 degC/h)**, mutant **0**. Inputs tried: 24.0->23.9 (both 0); 27.0->26.8 (1 vs 0); 28.0->27.9 (1 vs 0); 28.1->28.0 (both 1); null 40.0->39.8 (identical).

Candidate: No check folds a buffer interval 4-8 K above ambient; BUFFER_COOLING_MIN_DELTA 4.0 -> 8.0 is unseen. Should have failed: tests/features.py executes coordinator.py:5663-5665 on the traced baseline but never folds an interval whose tank-to-ambient delta lies between 4 and 8 K. Class guess I1, severity claimed low; perturbation direction down (samples folded).

### 021dc21415f3229e — custom_components/heatpump_optimizer/coordinator.py:1651 CONST (candidate)

Patch `HOUSE_LOSS_MAX_STEP = 0.05 -> HOUSE_LOSS_MAX_STEP = 0.1` in `<module>`. Gate: RED-AS-NULL, gate_rc 1, wall 3295.1 s, load1 0.85..0.92 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 021dc21415f3229e`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_021dc21415f3229e.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_021dc21415f3229e.py`), metric: learned house heat-loss scale after restoring a store fitted against a nameplate UA 7 % off today's (scale 1.2, 200 samples). Baseline **(re-anchored, 1.279005)**, mutant **(kept verbatim, 1.2)**. Inputs tried: frac 0.049/0.051 (both kept); 0.07 (moved); 0.099 (moved); 0.101 (1.315551 vs 1.2); -0.07 (1.11396 vs 1.2); null 0.03 and 0.12 (identical).

Candidate: No check re-anchors a 5-10 % nameplate edit; HOUSE_LOSS_MAX_STEP 0.05 -> 0.1 is unseen. Should have failed: tests/features.py, tests/boost_drift_replay.py and tests/finite_boundary.py execute coordinator.py:5572 on the traced baseline; none restores a store whose nameplate moved between 5 % and 10 % and asserts the re-anchored scale. Class guess I1, severity claimed medium; perturbation direction down (learned scale).

### 1165914e57f5bd08 — custom_components/heatpump_optimizer/coordinator.py:1796 CONST (candidate)

Patch `COP_LEARNING_MAX_STEP = 0.05 -> COP_LEARNING_MAX_STEP = 0.1` in `<module>`. Gate: RED-AS-NULL, gate_rc 1, wall 3334.3 s, load1 0.86..0.92 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 1165914e57f5bd08`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_1165914e57f5bd08.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_1165914e57f5bd08.py`), metric: learned COP scale after one outlier interval (target scale 6.0) from scale 1.0. Baseline **1.05**, mutant **1.1**. Inputs tried: electrical 1.0 kW (1.05 vs 1.06); 0.5 (1.05 vs 1.1); 0.3 / 0.1 (1.05 vs 1.1); 60 kW (0.9715 both); null 2.0 and 5.0 kW (identical).

Candidate: No check pins the 5 % per-sample cap of the COP learner; COP_LEARNING_MAX_STEP 0.05 -> 0.1 is unseen. Should have failed: tests/features.py and tests/boost_drift_replay.py execute coordinator.py:5399 on the traced baseline; no check folds one outlier ratio and asserts the move is capped at 5 % of the scale. Class guess I1, severity claimed low; perturbation direction up (COP scale).

### ab918806fc8b4af6 — custom_components/heatpump_optimizer/coordinator.py:10331 GUARD_OFF (candidate)

Patch `if energy <= 0: -> if False:` in `HeatPumpOptimizerCoordinator._accumulate_energy`. Gate: RED-AS-NULL, gate_rc 1, wall 3359.2 s, load1 0.72..0.93 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key ab918806fc8b4af6`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_ab918806fc8b4af6.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_ab918806fc8b4af6.py`), metric: ledger lines booked for one settled 0.25 h interval with 0 kW drawn (energy == 0). Baseline **0 lines []**, mutant **3 lines ['dhw', 'space', 'spot'] at 0 kWh / 0 SEK (energy and cost totals unchanged)**. Inputs tried: 0 kW measured (0 vs 3); no meter, zero plan (0 vs 3); no price (0 vs 1 'spot'); null: 2 kW (identical).

Candidate: No check pins that a zero-energy interval books no ledger line; the energy <= 0 gate of _accumulate_energy is unseen. Should have failed: tests/features.py, tests/entities.py and tests/boost_drift_replay.py execute coordinator.py:10331-10332 on the traced baseline but none asserts the ledger is untouched by a zero-energy interval. Class guess I1, severity claimed low; perturbation direction up (ledger lines).

### db9b59ec36304943 — custom_components/heatpump_optimizer/coordinator.py:10331 CMP_BOUND (candidate)

Patch `if energy <= 0: -> if energy < 0:` in `HeatPumpOptimizerCoordinator._accumulate_energy`. Gate: RED-AS-NULL, gate_rc 1, wall 2798.3 s, load1 0.78..0.93 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key db9b59ec36304943`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_db9b59ec36304943.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_db9b59ec36304943.py`), metric: ledger lines booked for one settled 0.25 h interval with 0 kW drawn (energy == 0). Baseline **0 lines []**, mutant **3 lines ['dhw', 'space', 'spot'] at 0 kWh / 0 SEK (energy and cost totals unchanged)**. Inputs tried: 0 kW measured (0 vs 3); no meter, zero plan (0 vs 3); no price (0 vs 1 'spot'); null: 2 kW (identical).

Candidate: No check pins that a zero-energy interval books no ledger line; the energy <= 0 gate of _accumulate_energy is unseen. Should have failed: tests/features.py, tests/entities.py and tests/boost_drift_replay.py execute coordinator.py:10331-10332 on the traced baseline but none asserts the ledger is untouched by a zero-energy interval. Class guess I1, severity claimed low; perturbation direction up (ledger lines).

### cf7be12db1a662c4 — custom_components/heatpump_optimizer/coordinator.py:9613 GUARD_OFF (candidate)

Patch `if isinstance(prices, dict): -> if False:` in `HeatPumpOptimizerCoordinator._apply_learner_payloads`. Gate: RED-AS-NULL, gate_rc 1, wall 2738.5 s, load1 0.78..0.92 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key cf7be12db1a662c4`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_cf7be12db1a662c4.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_cf7be12db1a662c4.py`), metric: price_shape00 after _apply_learner_payloads restores a snapshot whose price-shape model differs from the fresh state. Baseline **1.3**, mutant **1.0 (the snapshot's price-shape model is ignored)**. Inputs tried: a snapshot from the producers' own as_dict() with one field changed; null: non-dict entries, empty snapshot, snapshot equal to the fresh state (identical).

Candidate: No check asserts the price-shape model a snapshot restore adopts; skipping that branch of _apply_learner_payloads is unseen. Should have failed: tests/features.py, tests/boost_drift_replay.py and tests/finite_boundary.py execute coordinator.py:9613-9614 on the traced baseline (the restore branch runs) but none asserts the restored price-shape model's state afterwards. Class guess I1, severity claimed medium; perturbation direction down (price_shape00).

### 031dba68286ccfbf — custom_components/heatpump_optimizer/coordinator.py:9622 GUARD_OFF (candidate)

Patch `if isinstance(comfort, dict): -> if False:` in `HeatPumpOptimizerCoordinator._apply_learner_payloads`. Gate: RED-AS-NULL, gate_rc 1, wall 2717.5 s, load1 0.86..1.0 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 031dba68286ccfbf`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_031dba68286ccfbf.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_031dba68286ccfbf.py`), metric: comfort_learned_weight after _apply_learner_payloads restores a snapshot whose comfort learner differs from the fresh state. Baseline **8.0**, mutant **5.0 (the snapshot's comfort learner is ignored)**. Inputs tried: a snapshot from the producers' own as_dict() with one field changed; null: non-dict entries, empty snapshot, snapshot equal to the fresh state (identical).

Candidate: No check asserts the comfort learner a snapshot restore adopts; skipping that branch of _apply_learner_payloads is unseen. Should have failed: tests/features.py, tests/boost_drift_replay.py and tests/finite_boundary.py execute coordinator.py:9622-9623 on the traced baseline (the restore branch runs) but none asserts the restored comfort learner's state afterwards. Class guess I1, severity claimed medium; perturbation direction down (comfort_learned_weight).

### 22205dc8a4a6e79b — custom_components/heatpump_optimizer/coordinator.py:9628 GUARD_OFF (candidate)

Patch `if isinstance(defrost, dict): -> if False:` in `HeatPumpOptimizerCoordinator._apply_learner_payloads`. Gate: RED-AS-NULL, gate_rc 1, wall 2716.1 s, load1 0.85..1.0 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 22205dc8a4a6e79b`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_22205dc8a4a6e79b.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_22205dc8a4a6e79b.py`), metric: defrost_factor00 after _apply_learner_payloads restores a snapshot whose defrost derate differs from the fresh state. Baseline **0.8**, mutant **1.0 (the snapshot's defrost derate is ignored)**. Inputs tried: a snapshot from the producers' own as_dict() with one field changed; null: non-dict entries, empty snapshot, snapshot equal to the fresh state (identical).

Candidate: No check asserts the defrost derate a snapshot restore adopts; skipping that branch of _apply_learner_payloads is unseen. Should have failed: tests/features.py, tests/boost_drift_replay.py and tests/finite_boundary.py execute coordinator.py:9628-9629 on the traced baseline (the restore branch runs) but none asserts the restored defrost derate's state afterwards. Class guess I1, severity claimed medium; perturbation direction up (defrost_factor00).

### 37e0face2a901e71 — custom_components/heatpump_optimizer/coordinator.py:7419 CMP_BOUND (candidate)

Patch `value = solar[i] if i < len(solar) else 0.0 -> value = solar[i] if i <= len(solar) else 0.0` in `HeatPumpOptimizerCoordinator._apply_open_meteo`. Gate: RED-AS-NULL, gate_rc 1, wall 2752.5 s, load1 0.84..0.86 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 37e0face2a901e71`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_37e0face2a901e71.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_37e0face2a901e71.py`), metric: irradiance series (or exception) for a 6-step horizon, a 3-entry weather solar list and Open-Meteo covering 2 steps. Baseline **[100.0, 101.0, 7.0, 0.0, 0.0, 0.0]**, mutant **IndexError**. Inputs tried: solar [] n 4 cover 0 (IndexError); solar 3 n 6 cover 3 (IndexError); cover 4 (identical); n 3 cover 0 (identical); null: solar as long as the horizon; full coverage (identical).

Candidate: No check feeds _apply_open_meteo a weather series shorter than the horizon with an Open-Meteo gap; i < len -> <= is unseen. Should have failed: tests/solar_alignment.py executes coordinator.py:7419 on the traced baseline but never with an Open-Meteo gap at a step index equal to the weather series' length (a weather forecast shorter than the horizon). Class guess I1, severity claimed medium; perturbation direction up (series or exception).

### 68c8ce175dcfa839 — custom_components/heatpump_optimizer/coordinator.py:7422 GUARD_OFF (candidate)

Patch `if missing: -> if False:` in `HeatPumpOptimizerCoordinator._apply_open_meteo`. Gate: RED-AS-NULL, gate_rc 1, wall 2940.3 s, load1 0.74..0.92 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 68c8ce175dcfa839`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_68c8ce175dcfa839.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_68c8ce175dcfa839.py`), metric: DEBUG records 'Open-Meteo irradiance covered %d/%d steps' emitted when Open-Meteo covers 2 of 6 steps. Baseline **1**, mutant **0 (returned series identical)**. Inputs tried: cover 2/6 and 5/6 and 0/4 (1 vs 0 each); null: full coverage (0 both).

Candidate: No check reads the Open-Meteo partial-coverage debug line; dropping its guard is unseen. Should have failed: tests/solar_alignment.py executes coordinator.py:7422-7423 on the traced baseline but asserts no log record; the only observable the guard gates is this DEBUG line. Class guess I1, severity claimed low; perturbation direction down (debug records).

### 97628f4b14aec1b9 — custom_components/heatpump_optimizer/coordinator.py:4497 GUARD_OFF (equivalent-candidate)

Patch `if not vvc_entity and not space_entity: -> if False:` in `HeatPumpOptimizerCoordinator._async_drive_pumps`. Gate: RED-AS-NULL, gate_rc 1, wall 3128.3 s, load1 0.72..1.0 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 97628f4b14aec1b9`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_97628f4b14aec1b9.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_97628f4b14aec1b9.py`), metric: pump service calls (and any exception) in one tick with no VVC pump and no drivable space pump. Baseline **[] for every input**, mutant **[] for every input (moved 0 of 6)**. Inputs tried: no pumps; no pumps in mode off; no pumps with a fresh plan; space pump held by a stale plan; no pumps with DHW windows; no pumps at midnight; positive control: a VVC pump issues 1 command.

Equivalent-candidate (non-finding unless a later seat finds the input): none: both branches after the early return are gated on the same two entities, so the guard only saves a dt_util.now() read.

### 20f57d1eea0a5a1d — custom_components/heatpump_optimizer/coordinator.py:4508 BOOLOP (candidate)

Patch `if params.dhw_enabled and params.dhw_windows_active -> if params.dhw_enabled or params.dhw_windows_active` in `HeatPumpOptimizerCoordinator._async_drive_pumps`. Gate: RED-AS-NULL, gate_rc 1, wall 3014.8 s, load1 1.01..0.92 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key 20f57d1eea0a5a1d`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_20f57d1eea0a5a1d.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_20f57d1eea0a5a1d.py`), metric: VVC pump command at 12:00 with a 06:00-08:30 DHW window and DHW disabled. Baseline **[('turn_on', 'switch.vvc')]**, mutant **[('turn_off', 'switch.vvc')]**. Inputs tried: DHW disabled, schedule on, 12:00 (on vs off); DHW enabled, schedule off, 12:00 (on vs off); DHW disabled at 07:00 inside the window (both on); null: both operands true / both false (identical).

Candidate: No check drives the VVC pump with DHW disabled but windows configured; and -> or switches the loop off unseen. Should have failed: tests/features.py and tests/config_flow_steps.py execute coordinator.py:4508 on the traced baseline but no check drives the VVC pump with exactly one of dhw_enabled / dhw_windows_active true and asserts it is left on. Class guess I1, severity claimed medium; perturbation direction down (VVC command).

### e0bd801049aba41a — custom_components/heatpump_optimizer/coordinator.py:4524 CLAMP_DROP (equivalent-candidate)

Patch `dt_hours = max(ctx._opt_config.dt_hours, 1e-6) -> dt_hours = (ctx._opt_config.dt_hours)` in `HeatPumpOptimizerCoordinator._async_drive_pumps`. Gate: RED-AS-NULL, gate_rc 1, wall 3226.8 s, load1 0.86..1.0 (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/fullgate.py run --src complete --key e0bd801049aba41a`).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_e0bd801049aba41a.py` (`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_e0bd801049aba41a.py`), metric: space-pump service calls with a fresh plan, across plan step lengths. Baseline **[('turn_on', 'switch.space')] at the production 15-min step**, mutant **identical (moved 0 at every production step)**. Inputs tried: production dt_hours 0.25 for configs {}, time_step_minutes 0 / 5, horizon 48 (time_step_minutes is never read from config); direct frozen-ctx writes: step 15, 5, 1, 1e-5, 6e-5, 1e-6 min (identical); step 0 min (baseline turn_on, mutant ZeroDivisionError: unreachable).

Equivalent-candidate (non-finding unless a later seat finds the input): none through production: OptimizationConfig.time_step_minutes is the 15.0 default (optimizer.py:2667) and no config key sets it.

## Coverage

- D3.M1 (carried from REPORT-D3-u1b.json): universe 1260, examined 1260, not reached 0; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`; redispatched [{'item': 'C8', 'state': 'examined'}]
- D3.M2 (carried from REPORT-D3-u1b.json): universe 1260, examined 343, not reached 29; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --unpinned`; redispatched [{'item': 'C2', 'state': 'examined'}, {'item': 'C6', 'state': 'examined'}]
- D3.M3: universe 742, examined 16, not reached 726; enumerator `awk -F'\t' '$6=="gate"' SURVIVORS.tsv`; redispatched [{'item': 'C3', 'state': 'not_reached'}, {'item': 'C5', 'state': 'examined'}]
- D3.M4 (carried from REPORT-D3-u1b.json): universe 268, examined 225, not reached 43; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/tabulate.py --tsv | grep -P '\tSURVIVED\t'`; redispatched []
- D3.M5 (carried from REPORT-D3-u1b.json): universe 27, examined 23, not reached 4; enumerator `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/enumerate.py --scripts`; redispatched [{'item': 'C1', 'state': 'examined'}, {'item': 'C4', 'state': 'not_reached'}, {'item': 'C7', 'state': 'not_reached'}, {'item': 'C9', 'state': 'not_reached'}]

D3.M3 not_reached: every other wave key by its box (D3-g02..D3-g47, 726 keys), listed in REPORT.json.

## Unfinished

- none: all 16 keys gated and recorded; no TIMEOUT, STOP or SKIP.

## Harnesses

- dev/audit/rounds/round11/D3/s1/fullgate.py
- gate_wave.sh (out-of-tree driver shipped on dispatch/finder-r11-D3-g01: per key in keys.tsv order, one gate at a time, fullgate.py run --src complete --key <key> under a 14400 s cap, tree reset to the baseline between gates; null via fullgate.py null)
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/_tools/ (the seat's probe builders, analysis.py, write_result.py, step2.sh)
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_fafb0d2c15e72efb.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_676e8bfb416ff635.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_622996d751dca0c4.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_0e6080e5385399cb.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_021dc21415f3229e.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_1165914e57f5bd08.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_ab918806fc8b4af6.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_db9b59ec36304943.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_cf7be12db1a662c4.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_031dba68286ccfbf.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_22205dc8a4a6e79b.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_37e0face2a901e71.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_68c8ce175dcfa839.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_97628f4b14aec1b9.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_20f57d1eea0a5a1d.py
- dev/audit/rounds/round11/D3/s1/wave/D3-g01/probes/probe_e0bd801049aba41a.py
