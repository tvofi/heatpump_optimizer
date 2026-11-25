# D3-s1, box D3-g35: full gate for 16 D3.M3 full-net survivors (audit round 11)

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Seat D3-s1, dimension D3, step D3.M3 with the D3.md step-4 answer per survivor. All 16 keys are mutants of `SystemIdentification.identify` in `custom_components/heatpump_optimizer/sysid.py` (lines 2141-2246).

## Machine and controls

```
nproc: 4
               total        used        free      shared  buff/cache   available
Mem:           16087         859       13985          12        1512       15227
Swap:              0           0           0
model name	: Intel(R) Xeon(R) Processor @ 2.10GHz
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda        252G   12G   58G  17% /
load1: 0.66
Wed Nov 25 00:53:07 UTC 2026
```

Null control (`fullgate.py null`, comment-only marker): gate_rc=1, red scripts ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'], failed-check counts {'python3 tests/closure.py selftest': 2, 'python3 tests/entities.py': 1, 'python3 tests/harness_headers.py': 4}, wall 3401.1 s, load1 0.47..0.92 (provisional). All red lines are instrument or artefact checks: closure.py selftest's two merge-reason pins (status skip-not-under-scoped), entities.py's one scoped-path record check, and harness_headers.py's round-4 D6 claims header (123 vs 122 in the stripped tree), its committed-output check, and its inlined-walk check naming this box's own untracked probes/sysid_probe_common.py. A key counts KILLED only when a script is red beyond these counts. Not re-taken: no production-behaviour script is red, and no script red for the machine.

Procedure: `gate_wave.sh run` runs `fullgate.py run --src complete --key <key>` for each key of keys.tsv in order, one gate at a time (GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1, 4 h cap), and checkpoints after each; the per-key record is `dev/audit/rounds/round11/D3/s1/wave/D3-g35/gates/<key>.json` with its log beside it. Every wall and load figure is provisional (nproc 4, Intel Xeon @ 2.10GHz, the box alone on its machine). One container restart happened mid-wave; the gate processes and the checkpointed records survived it.

Probes: each `probes/probe_<key>.py` loads the baseline's sysid.py with `git show` (never the gate's worktree file), applies the one-line mutant in memory, and drives `identify()` on synthetic exact first-order step tests (`probes/sysid_probe_common.py`: C dT/dt = Q + G - UA (T - T_out), 10-minute cadence, settle 1 h / step 2 h / relax 2 h) over a 29-case honest-search grid plus the key case. Boundary mutants (`<=` vs `<`) are reached by hunting a float input until an instrumentation arm (a `_TAP.append` before the mutated line, not the mutant) reads the boundary exactly. Metric `differing_cases`: inputs whose published result (completed, reason, UA, C, gains, drift, confidence) differs mutant vs baseline.

## Tally

- gated: 16 of 16; KILLED 1 (python3 tests/structure.py: 1); SURVIVED 0; RED-AS-NULL 15; TIMEOUT 0
- candidates (gate survivors whose probe moves): 12; equivalent-candidates: 3

| key | site | patch | verdict | killed_by | class | probe key case (baseline -> mutant) | differing_cases |
|---|---|---|---|---|---|---|---|
| 31bb6bebd6b45f0e | sysid.py:2141 CMP_BOUND | `if solution.shape[0] >= 3: -> if solution.shape[0] > 3:` | RED-AS-NULL | - | equivalent-candidate | None -> None | 0/29 |
| 501a5e7cda702183 | sysid.py:2146 GUARD_OFF | `if drift_c_per_h is not None: -> if False:` | RED-AS-NULL | - | candidate | 0.3000000499195061 -> None | 18/30 |
| 20cde1046cbd5681 | sysid.py:2154 CMP_BOUND | `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 <= gains_kw < 2.0):` | RED-AS-NULL | - | candidate | True -> False | 1/30 |
| 6cfdb101dc87a6ea | sysid.py:2154 CMP_BOUND | `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 < gains_kw <= 2.0):` | RED-AS-NULL | - | candidate | True -> False | 1/30 |
| d203230963349f60 | sysid.py:2162 CLAMP_DROP | `gains_kw = float(np.clip(gains_kw, 0.0, 2.0)) -> gains_kw = float((gains_kw))` | RED-AS-NULL | - | candidate | 0.0 -> -0.2999999803793181 | 2/30 |
| 078e78462859ff6b | sysid.py:2187 BOOLOP | `if drift_c_per_h is not None and a.shape[1] >= 4: -> if drift_c_per_h is not None or a.shape[1] >= 4:` | RED-AS-NULL | - | equivalent-candidate | None -> None | 0/29 |
| 5654f855fcc27724 | sysid.py:2187 CMP_BOUND | `if drift_c_per_h is not None and a.shape[1] >= 4: -> if drift_c_per_h is not None and a.shape[1] > 4:` | RED-AS-NULL | - | candidate | 0.9813074506931991 -> 0.9815294051605464 | 14/30 |
| c303df62a0b7b9bc | sysid.py:2187 GUARD_OFF | `if drift_c_per_h is not None and a.shape[1] >= 4: -> if False:` | KILLED | python3 tests/structure.py | killed | 0.9813074506931991 -> 0.9815294051605464 | 14/30 |
| ed00e6c2abf2aa66 | sysid.py:2208 CMP_BOUND | `if drift_c_per_h is not None and a.shape[1] >= 4 and excursion > 1e-9: -> if drift_c_per_h is not None and a.shape[1] >= 4 and excursion >= 1e-9:` | RED-AS-NULL | - | equivalent-candidate | None -> None | 0/29 |
| 4593852cf3862b3c | sysid.py:2223 CMP_BOUND | `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 < tau <= 200.0) or not (0.01 <= ua <= 5.0):` | RED-AS-NULL | - | candidate | True -> False | 1/30 |
| 64f3ef1feaaf7bc9 | sysid.py:2223 CMP_BOUND | `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau <= 200.0) or not (0.01 < ua <= 5.0):` | RED-AS-NULL | - | candidate | True -> False | 1/30 |
| 784e362919d88a92 | sysid.py:2223 CMP_BOUND | `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau <= 200.0) or not (0.01 <= ua < 5.0):` | RED-AS-NULL | - | candidate | True -> False | 1/30 |
| d661d68f54982097 | sysid.py:2223 CMP_BOUND | `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):` | RED-AS-NULL | - | candidate | True -> False | 1/30 |
| a5b06d898bf0ba03 | sysid.py:2237 CMP_BOUND | `and abs(drift_c_per_h) < self.config.sensor_drift_prior_c_per_h -> and abs(drift_c_per_h) <= self.config.sensor_drift_prior_c_per_h` | RED-AS-NULL | - | candidate | True -> False | 1/30 |
| c51115b0104a8bf5 | sysid.py:2244 CMP_BOUND | `if abs(den) > 1e-6: -> if abs(den) >= 1e-6:` | RED-AS-NULL | - | candidate | True -> False | 2/30 |
| 4da9d281d4714565 | sysid.py:2246 CMP_BOUND | `if ua_ss > 0.0 and abs(ua_ss - ua) / ua > 0.10: -> if ua_ss > 0.0 and abs(ua_ss - ua) / ua >= 0.10:` | RED-AS-NULL | - | candidate | True -> False | 1/30 |

## Survivors: the step-4 answer, with probe numbers

### 31bb6bebd6b45f0e — custom_components/heatpump_optimizer/sysid.py:2141 CMP_BOUND (RED-AS-NULL, equivalent-candidate)

Patch `if solution.shape[0] >= 3: -> if solution.shape[0] > 3:`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_u1a_part*.json. Gate: gate_rc=1, wall 3309.3 s, load1 0.72..0.93 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_31bb6bebd6b45f0e.py`: differing_cases 0 of 29.
Equivalent-candidate: none possible: solution.shape[0] is 4 (four-column solve) or 2 (fallback), never 3, so >= 3 and > 3 agree on every reachable input. Inputs tried: clean, drift+0.01, drift-0.01, drift+0.05, noise0.02_s0, noise0.02_s1, noise0.02_s2, noise0.02_s3, noise0.02_s4, noise0.005_s0, noise0.005_s1, noise0.005_s2, gains0, gains-0.3, gains1.9, gains3, cadence30, cadence60, unsettled1.3, q0.1, q1e-5, q0, tau~200, ua~5, ua~0.01, tau~0.1, settle_dT_1e-6, prior0.05, short.

### 501a5e7cda702183 — custom_components/heatpump_optimizer/sysid.py:2146 GUARD_OFF (RED-AS-NULL, candidate)

Patch `if drift_c_per_h is not None: -> if False:`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json. Gate: gate_rc=1, wall 3306.3 s, load1 0.79..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_501a5e7cda702183.py`: key case 0.3000000499195061 -> None, differing_cases 18 of 30.
Claim: With the guard at sysid.py:2146 forced False, a clean step test on a sensor drifting +0.01 C/h no longer completes (baseline completed, gains 0.300 kW; mutant refuses 'sensor drift collapsed into heat-loss'), and 18 of 30 probe cases change; GATE_SCOPE=full GOLDEN_MODE=drift stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks a drifting-sensor identify() check asserting completed and internal_gains_kw == the drift-free gains (0.30 kW at +0.01 C/h drift).
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction up.

### 20cde1046cbd5681 — custom_components/heatpump_optimizer/sysid.py:2154 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 <= gains_kw < 2.0):`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_u1a_part*.json. Gate: gate_rc=1, wall 3310.5 s, load1 0.78..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_20cde1046cbd5681.py`: key case True -> False, differing_cases 1 of 30; hunt hit=1 x=2.000000002534201 secondary=3.2.
Claim: A step test whose fitted gains_kw is exactly 2.0 completes at the baseline and is refused 'fitted gains outside plausible bounds' under `gains_kw < 2.0`; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check on a fit whose gains_kw is exactly 2.0 asserting it completes with internal_gains_kw == 2.0.
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### 6cfdb101dc87a6ea — custom_components/heatpump_optimizer/sysid.py:2154 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if not (-0.5 <= gains_kw <= 2.0): -> if not (-0.5 < gains_kw <= 2.0):`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json. Gate: gate_rc=1, wall 3392.1 s, load1 0.78..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_6cfdb101dc87a6ea.py`: key case True -> False, differing_cases 1 of 30; hunt hit=1 x=-0.5000000171684871 secondary=3.05.
Claim: A step test whose fitted gains_kw is exactly -0.5 completes (gains clipped to 0.0) at the baseline and is refused 'fitted gains outside plausible bounds' under `-0.5 < gains_kw`; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check on a fit whose gains_kw is exactly -0.5 asserting it completes with internal_gains_kw clipped to 0.0.
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### d203230963349f60 — custom_components/heatpump_optimizer/sysid.py:2162 CLAMP_DROP (RED-AS-NULL, candidate)

Patch `gains_kw = float(np.clip(gains_kw, 0.0, 2.0)) -> gains_kw = float((gains_kw))`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1d.json. Gate: gate_rc=1, wall 3473.5 s, load1 0.72..1.0 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_d203230963349f60.py`: key case 0.0 -> -0.2999999803793181, differing_cases 2 of 30.
Claim: Dropping np.clip(gains_kw, 0.0, 2.0) at sysid.py:2162 publishes internal_gains_kw -0.300 kW instead of 0.0 on a plant with true gains -0.3 kW; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check on a plant with gains -0.3 kW asserting internal_gains_kw == 0.0 (the clip).
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction sign_flip.

### 078e78462859ff6b — custom_components/heatpump_optimizer/sysid.py:2187 BOOLOP (RED-AS-NULL, equivalent-candidate)

Patch `if drift_c_per_h is not None and a.shape[1] >= 4: -> if drift_c_per_h is not None or a.shape[1] >= 4:`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_u1a_part*.json. Gate: gate_rc=1, wall 3610.7 s, load1 0.93..1.0 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_078e78462859ff6b.py`: differing_cases 0 of 29.
Equivalent-candidate: none possible: drift_c_per_h is None exactly on the two-column fallback, where a.shape[1] == 2, so `and` and `or` agree on every reachable input. Inputs tried: clean, drift+0.01, drift-0.01, drift+0.05, noise0.02_s0, noise0.02_s1, noise0.02_s2, noise0.02_s3, noise0.02_s4, noise0.005_s0, noise0.005_s1, noise0.005_s2, gains0, gains-0.3, gains1.9, gains3, cadence30, cadence60, unsettled1.3, q0.1, q1e-5, q0, tau~200, ua~5, ua~0.01, tau~0.1, settle_dT_1e-6, prior0.05, short.

### 5654f855fcc27724 — custom_components/heatpump_optimizer/sysid.py:2187 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if drift_c_per_h is not None and a.shape[1] >= 4: -> if drift_c_per_h is not None and a.shape[1] > 4:`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json. Gate: gate_rc=1, wall 3774.2 s, load1 0.85..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_5654f855fcc27724.py`: key case 0.9813074506931991 -> 0.9815294051605464, differing_cases 14 of 30.
Claim: With `a.shape[1] > 4` at sysid.py:2187 the excursion is no longer drift-corrected; on a +0.01 C/h drifting sensor the published confidence moves 0.981307 -> 0.981529 and 14 of 30 probe cases change; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks a drifting-sensor identify() check asserting the published confidence equals the drift-corrected excursion's (0.98131 at +0.01 C/h).
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction up.

### ed00e6c2abf2aa66 — custom_components/heatpump_optimizer/sysid.py:2208 CMP_BOUND (RED-AS-NULL, equivalent-candidate)

Patch `if drift_c_per_h is not None and a.shape[1] >= 4 and excursion > 1e-9: -> if drift_c_per_h is not None and a.shape[1] >= 4 and excursion >= 1e-9:`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1d.json. Gate: gate_rc=1, wall 3703.0 s, load1 0.8..1.0 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_ed00e6c2abf2aa66.py`: differing_cases 0 of 29; hunt hit=0 x=None secondary=None.
Equivalent-candidate: none found: every completing fit tried has excursion >= 2.04e-7 C (q swept 1e-3..0); below that the fit is refused before publication, so excursion == 1e-9 never reaches a published result. Inputs tried: clean, drift+0.01, drift-0.01, drift+0.05, noise0.02_s0, noise0.02_s1, noise0.02_s2, noise0.02_s3, noise0.02_s4, noise0.005_s0, noise0.005_s1, noise0.005_s2, gains0, gains-0.3, gains1.9, gains3, cadence30, cadence60, unsettled1.3, q0.1, q1e-5, q0, tau~200, ua~5, ua~0.01, tau~0.1, settle_dT_1e-6, prior0.05, short.

### 4593852cf3862b3c — custom_components/heatpump_optimizer/sysid.py:2223 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 < tau <= 200.0) or not (0.01 <= ua <= 5.0):`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json. Gate: gate_rc=1, wall 3604.8 s, load1 0.92..1.06 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_4593852cf3862b3c.py`: key case True -> False, differing_cases 1 of 30; hunt hit=1 x=3.281805987386395 secondary=3.3.
Claim: A fast-plant step test whose fitted tau is exactly 0.1 h completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `0.1 < tau`; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check on a fit whose tau is exactly 0.1 h asserting it completes.
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### 64f3ef1feaaf7bc9 — custom_components/heatpump_optimizer/sysid.py:2223 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau <= 200.0) or not (0.01 < ua <= 5.0):`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json. Gate: gate_rc=1, wall 3794.9 s, load1 0.9..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_64f3ef1feaaf7bc9.py`: key case True -> False, differing_cases 1 of 30; hunt hit=1 x=0.01000000000032415 secondary=3.35.
Claim: A step test whose fitted UA is exactly 0.01 kW/C completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `0.01 < ua`; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check on a fit whose UA is exactly 0.01 kW/C asserting it completes.
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### 784e362919d88a92 — custom_components/heatpump_optimizer/sysid.py:2223 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau <= 200.0) or not (0.01 <= ua < 5.0):`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json. Gate: gate_rc=1, wall 3744.5 s, load1 0.86..0.87 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_784e362919d88a92.py`: key case True -> False, differing_cases 1 of 30; hunt hit=1 x=5.000009159199536 secondary=3.05.
Claim: A step test whose fitted UA is exactly 5.0 kW/C completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `ua < 5.0`; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check on a fit whose UA is exactly 5.0 kW/C asserting it completes.
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### d661d68f54982097 — custom_components/heatpump_optimizer/sysid.py:2223 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if not (0.1 <= tau <= 200.0) or not (0.01 <= ua <= 5.0): -> if not (0.1 <= tau < 200.0) or not (0.01 <= ua <= 5.0):`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1d.json. Gate: gate_rc=1, wall 3928.5 s, load1 0.89..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_d661d68f54982097.py`: key case True -> False, differing_cases 1 of 30; hunt hit=0 x=None secondary=None.
Claim: A slow-plant step test whose fitted tau is exactly 200.0 h completes at the baseline and is refused 'fitted parameters outside plausible bounds' under `tau < 200.0`; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check on a fit whose tau is exactly 200.0 h asserting it completes.
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### a5b06d898bf0ba03 — custom_components/heatpump_optimizer/sysid.py:2237 CMP_BOUND (RED-AS-NULL, candidate)

Patch `and abs(drift_c_per_h) < self.config.sensor_drift_prior_c_per_h -> and abs(drift_c_per_h) <= self.config.sensor_drift_prior_c_per_h`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1c.json. Gate: gate_rc=1, wall 3824.2 s, load1 0.92..0.85 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_a5b06d898bf0ba03.py`: key case True -> False, differing_cases 1 of 30.
Claim: With sensor_drift_prior_c_per_h equal to the fitted |drift| (0.009999981 C/h) on an unsettled settle, the baseline skips the cross-check and completes; under `<=` the cross-check runs and refuses 'sensor drift collapsed into heat-loss'; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check with sensor_drift_prior_c_per_h equal to the fitted |drift| asserting the settle cross-check is skipped (completed).
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### c51115b0104a8bf5 — custom_components/heatpump_optimizer/sysid.py:2244 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if abs(den) > 1e-6: -> if abs(den) >= 1e-6:`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1d.json. Gate: gate_rc=1, wall 3619.0 s, load1 0.39..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_c51115b0104a8bf5.py`: key case True -> False, differing_cases 2 of 30.
Claim: When the last settling sample reads exactly 1e-6 C above outdoor, the baseline skips the steady-state UA and completes; under `>= 1e-6` ua_ss = (P+G)/1e-6 refuses 'sensor drift collapsed into heat-loss'; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check whose last settling sample reads exactly 1e-6 C above outdoor asserting the cross-check is skipped (completed).
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

### 4da9d281d4714565 — custom_components/heatpump_optimizer/sysid.py:2246 CMP_BOUND (RED-AS-NULL, candidate)

Patch `if ua_ss > 0.0 and abs(ua_ss - ua) / ua > 0.10: -> if ua_ss > 0.0 and abs(ua_ss - ua) / ua >= 0.10:`. Carried M4 answer: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json. Gate: gate_rc=1, wall 3685.9 s, load1 0.44..0.92 (provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_4da9d281d4714565.py`: key case True -> False, differing_cases 1 of 30; hunt hit=1 x=1.3920022034486481 secondary=(4.1, 0.308).
Claim: A step test whose steady-state settle UA disagrees with the fit by exactly 0.10 completes at the baseline and is refused 'sensor drift collapsed into heat-loss' under `>= 0.10`; the full gate stays green.
Should have failed: tests/features.py (its traced baseline executes the line: the slice box's closure trace; the one-state identify() checks near features.py:7850-7972 and 29353-29387 drive it) — it lacks an identify() check whose settle UA disagrees with the fit by exactly 10 % asserting it completes.
Severity claimed low (identify() is the harness-only one-state regression (#1395: the production sequence with a declared plant routes to identify_slab), so the mutant reaches no installed house; hygiene of the suite's pin, not user-visible); class_guess new; perturbation direction to_zero.

## Killed

- c303df62a0b7b9bc custom_components/heatpump_optimizer/sysid.py:2187 GUARD_OFF (`if drift_c_per_h is not None and a.shape[1] >= 4: -> if False:`): KILLED by ['python3 tests/structure.py']; Killed by the structural ratchet's improvement-not-recorded check (identify()'s cyclomatic complexity 44 -> 43 when the two-term guard becomes `if False:`), not by a behaviour check. The behaviour it removes (the excursion's drift correction) is the same one 5654f855fcc27724 (>= 4 -> > 4) removes without touching complexity, and that key SURVIVED the full gate with a moving probe (confidence 0.981307 -> 0.981529 on a +0.01 C/h drift); the probe for this key moves identically. Non-finding by the gate's rule; the behaviour gap is carried under 5654f855fcc27724.

## Non-findings, harnesses, unfinished, exposure

Non-findings: the null control, every KILLED key and every equivalent-candidate, each with its command and number (REPORT.json `non_findings`). Findings: none numbered here; the 12 candidates are under `gate_survivors` for the orchestrator's consolidation to number.

Harnesses: `dev/audit/rounds/round11/D3/s1/fullgate.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/sysid_probe_common.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_31bb6bebd6b45f0e.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_501a5e7cda702183.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_20cde1046cbd5681.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_6cfdb101dc87a6ea.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_d203230963349f60.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_078e78462859ff6b.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_5654f855fcc27724.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_c303df62a0b7b9bc.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_ed00e6c2abf2aa66.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_4593852cf3862b3c.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_64f3ef1feaaf7bc9.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_784e362919d88a92.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_d661d68f54982097.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_a5b06d898bf0ba03.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_c51115b0104a8bf5.py`, `dev/audit/rounds/round11/D3/s1/wave/D3-g35/probes/probe_4da9d281d4714565.py`; the box procedure is gate_wave.sh (dispatch ref tip b7a3ae2e).

Unfinished: finding ids: the 12 gate_survivors candidates carry no id (D3-s1-01..71 are taken); the orchestrator's consolidation assigns them before verification.

Exposure: Read COMMON.md, D3.md, dev/audit/README.md and finding.schema.json (through a haiku extractor), the u1 slice M4 answers for this box's 16 keys and the mutant records state/results/complete/<key>.json, REPORT-D3-u1b.json's coverage rows, REPORT-D3-rem.json's M3 row and two non-findings, m26_probe.py (the probe pattern), sysid.py 1890-2262 and 337-460, and the other 46 boxes' dispatch keys.tsv (key counts and sites only, for not_reached). No register, round11/J/, verifier report, docs/ page or GitHub record read; no gh run.

Note on severity: `identify()` is the harness-only one-state regression (#1395); the production sequence with a declared plant routes to `identify_slab`, so every candidate here is a gap in the suite's pin of a harness path, claimed low.

