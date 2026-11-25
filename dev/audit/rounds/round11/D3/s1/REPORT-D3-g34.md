# D3-s1 box D3-g34: full gates for 16 u1 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. All 16 keys mutate `SystemIdentification.identify` in `custom_components/heatpump_optimizer/sysid.py`.

## Machine and controls

nproc 4, Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB, no swap; load1 0.4-1.0 throughout (wall, CPU and load are provisional: true; the judge re-takes them). One gate at a time, GATE_JOBS=1, GATE_SCOPE=full GOLDEN_MODE=drift.

Null control (`fullgate.py null`, dev/audit/rounds/round11/D3/s1/wave/D3-g34/gates/null.json): gate_rc=1, red on ['python3 tests/closure.py selftest', 'python3 tests/entities.py', 'python3 tests/harness_headers.py'] only. All three are tree-state artefacts of the stripped detached worktree (closure.py selftest's skip-not-under-scoped pins, entities.py's scoped-path record, harness_headers.py's round-4 header the finder-wall strip removes). No machine red, so the null was usable as taken. Every key's gate was red on exactly these three, plus structure.py for the one KILLED key.

Probes run in `$HOME/probe-tree`, a clean baseline worktree, never in the gate's tree. The predecessor's first five records were rebuilt there after a contamination (see NOTES.md; the superseded records are kept in results-superseded/).

## Tally

- gated: 16 of 16; TIMEOUT: 0; not gated: 0
- KILLED: 1 (python3 tests/structure.py: 1)
- SURVIVED: 0; RED-AS-NULL: 15
- candidates (probe moves): 9; equivalent-candidates: 6

findings: [] — candidates go under `gate_survivors` for the orchestrator's consolidation to number.

| key | site | patch | verdict | class | probe differing |
|---|---|---|---|---|---|
| b8d5ec03e8eba5c7 | sysid.py:1942 GUARD_OFF | `if len(rows) < 5: -> if False:` | RED-AS-NULL | candidate | 2 count (of 2) |
| 756f3bebd6a42efc | sysid.py:1974 CLAMP_DROP | `prior_sd = 0.5 / max(self.config.thermal_mass_prior, 0.1) -> prior_sd = 0.5 / (self.config.thermal_mass_prior)` | RED-AS-NULL | candidate | 2 count (of 2) |
| 3918ca4fedbfc5bb | sysid.py:1979 CLAMP_DROP | `dof = max(len(rows) - n_cols, 1) -> dof = (len(rows) - n_cols)` | RED-AS-NULL | equivalent-candidate | 0 count (of 5) |
| 84372c0eb1502d14 | sysid.py:2010 CLAMP_DROP | `k_hat = max(float(pass1[0]), 0.0) -> k_hat = (float(pass1[0]))` | RED-AS-NULL | candidate | 1 count (of 1) |
| 20f72103eda78713 | sysid.py:2018 GUARD_OFF | `if h_prev <= 1e-6: -> if False:` | RED-AS-NULL | candidate | 3 count (of 3) |
| 50daaa57683189c5 | sysid.py:2018 CMP_BOUND | `if h_prev <= 1e-6: -> if h_prev < 1e-6:` | RED-AS-NULL | candidate | 3 count (of 3) |
| 4eeb366191982f92 | sysid.py:2032 CMP_BOUND | `if len(d2_all) >= 3: -> if len(d2_all) > 3:` | RED-AS-NULL | candidate | 2 count (of 2) |
| a9bc37e9ba781833 | sysid.py:2037 CLAMP_DROP | `x1_spread2 = float(np.var(a[:, 0])) * n_rows / max(n_rows - 1.0, 1.0) -> x1_spread2 = float(np.var(a[:, 0])) * n_rows / (n_rows - 1.0)` | RED-AS-NULL | equivalent-candidate | 0 count (of 5) |
| 44bb0ce0b258242c | sysid.py:2038 CMP_BOUND | `if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0: -> if sigma2 > 0.0 and sigma2 >= x1_spread2 / 9.0:` | RED-AS-NULL | candidate | 1 count (of 1) |
| b97b45a6162a2f00 | sysid.py:2038 CMP_BOUND | `if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0: -> if sigma2 >= 0.0 and sigma2 > x1_spread2 / 9.0:` | RED-AS-NULL | equivalent-candidate | 0 count (of 6) |
| 6b6a8493668dde1c | sysid.py:2068 CMP_BOUND | `if sigma2 > 0.0: -> if sigma2 >= 0.0:` | RED-AS-NULL | equivalent-candidate | 0 count (of 5) |
| 10665a84dc064489 | sysid.py:2114 GUARD_OFF | `if rank < 2: -> if False:` | RED-AS-NULL | candidate | 2 count (of 2) |
| d7421c10ed63c281 | sysid.py:2114 CMP_BOUND | `if rank < 2: -> if rank <= 2:` | RED-AS-NULL | candidate | 1 count (of 1) |
| 07227ec96c3e14de | sysid.py:2126 GUARD_OFF | `if one_over_c <= 1e-6 or ua_over_c <= 1e-6: -> if False:` | KILLED | killed | 1 count (of 1) |
| 3e78e62aa0f2e687 | sysid.py:2126 CMP_BOUND | `if one_over_c <= 1e-6 or ua_over_c <= 1e-6: -> if one_over_c < 1e-6 or ua_over_c <= 1e-6:` | RED-AS-NULL | equivalent-candidate | 0 count (of 1602) |
| 87c3101b5663f17b | sysid.py:2126 CMP_BOUND | `if one_over_c <= 1e-6 or ua_over_c <= 1e-6: -> if one_over_c <= 1e-6 or ua_over_c < 1e-6:` | RED-AS-NULL | equivalent-candidate | 0 count (of 1602) |

## KILLED

**07227ec96c3e14de** sysid.py:2126 `if one_over_c <= 1e-6 or ua_over_c <= 1e-6: -> if False:`: killed by tests/structure.py's ratchet reading the tree as IMPROVED (max_cc 44 -> 43: the GUARD_OFF removes an if and an or from identify()), not by a behavioural assertion; no other script failed beyond the null's three. Read as KILLED by the metric's definition (run.sh red with a script beyond the null). Behaviour probe, run for the record in the clean probe tree: PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_07227ec9.py -> cases_differing=1 (of 1) [negative_ua: baseline refused 'fit gave implausible signs', mutant refused 'fitted parameters outside plausible bounds'], null_differing=0 (of 2); the outcome stays a refusal, only the reason string changes. Carried as a lead, not a finding.

## Survivors: step-4 answers

### b8d5ec03e8eba5c7 — sysid.py:1942 GUARD_OFF (candidate)

Patch `if len(rows) < 5: -> if False:`. Gate RED-AS-NULL (gate_rc 1, wall 3526.8 s, load1 0.86..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_b8d5ec03.py`: baseline `[refused:not enough usable intervals]`, mutant `[refused:fitted gains outside plausible bounds]`; cases differing 2 count (of 2), null differing 0 count (of 2). Inputs tried: gap_4rows (differs=1); gap_0rows (differs=1); plant_20rows (differs=0); plant_noisy (differs=0).
Candidate: No check pins identify()'s rows<5 refusal when a >2 h gap leaves <5 intervals of >=6 samples. Mutant b8d5ec03e8eba5c7 at sysid.py:1942 (GUARD_OFF) survives the full gate (RED-AS-NULL), yet identify() moves on gap_4rows: baseline [refused:not enough usable intervals], mutant [refused:fitted gains outside plausible bounds] (2 count (of 2) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks a case with >= 6 usable samples whose dt filter (dt <= 1e-3 h or > 2 h) leaves fewer than 5 rows, asserting the 'not enough usable intervals' refusal

### 756f3bebd6a42efc — sysid.py:1974 CLAMP_DROP (candidate)

Patch `prior_sd = 0.5 / max(self.config.thermal_mass_prior, 0.1) -> prior_sd = 0.5 / (self.config.thermal_mass_prior)`. Gate RED-AS-NULL (gate_rc 1, wall 3321.7 s, load1 0.78..1.01, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_756f3beb.py`: baseline `[refused:fitted gains outside plausible bounds]`, mutant `[completed ua=0.18996319528283903 C=4.863743086867868 conf=0.8596648707648191]`; cases differing 2 count (of 2), null differing 0 count (of 2). Inputs tried: tm0.05_noisy (differs=1); tm0.0 (differs=1); tm10_noisy (differs=0); tm0.1_noisy (differs=0).
Candidate: No check pins identify()'s 0.1 floor on thermal_mass_prior in the gains-prior width. Mutant 756f3bebd6a42efc at sysid.py:1974 (CLAMP_DROP) survives the full gate (RED-AS-NULL), yet identify() moves on tm0.05_noisy: baseline [refused:fitted gains outside plausible bounds], mutant [completed ua=0.18996319528283903 C=4.863743086867868 conf=0.8596648707648191] (2 count (of 2) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case with SysIdConfig.thermal_mass_prior below 0.1 (0.05, or 0.0 where the mutant raises ZeroDivisionError)

### 84372c0eb1502d14 — sysid.py:2010 CLAMP_DROP (candidate)

Patch `k_hat = max(float(pass1[0]), 0.0) -> k_hat = (float(pass1[0]))`. Gate RED-AS-NULL (gate_rc 1, wall 3304.9 s, load1 0.79..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_84372c0e.py`: baseline `[completed ua=0.0711885946897037 C=5.2908388164657465 conf=0.7509833795353332]`, mutant `[completed ua=0.07119096309555645 C=5.290664908635567 conf=0.7509833763113594]`; cases differing 1 count (of 1), null differing 0 count (of 2). Inputs tried: seed53_noise0.1 (differs=1); plant_clean (differs=0); plant_noisy (differs=0).
Candidate: No check pins identify()'s k_hat >= 0 clamp in the curvature correction. Mutant 84372c0eb1502d14 at sysid.py:2010 (CLAMP_DROP) survives the full gate (RED-AS-NULL), yet identify() moves on seed53_noise0.1: baseline [completed ua=0.0711885946897037 C=5.2908388164657465 conf=0.7509833795353332], mutant [completed ua=0.07119096309555645 C=5.290664908635567 conf=0.7509833763113594] (1 count (of 1) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case whose first unregularised pass gives a negative UA/C slope (a noisy, drifting window) and asserts the curvature-corrected noise estimate uses k_hat = 0

### 20f72103eda78713 — sysid.py:2018 GUARD_OFF (candidate)

Patch `if h_prev <= 1e-6: -> if False:`. Gate RED-AS-NULL (gate_rc 1, wall 3288.7 s, load1 0.78..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_20f72103.py`: baseline `[completed ua=0.19574719588552128 C=5.126629633823094 conf=0.9928502727789756]`, mutant `[completed ua=0.19575055138538477 C=5.126622761903924 conf=0.9928505855787655]`; cases differing 3 count (of 3), null differing 0 count (of 2). Inputs tried: dup0_step (differs=1); dup0_relax (differs=1); tie3600us_step (differs=1); gap3601us_step (differs=0); dup0_across_phases (differs=0).
Candidate: No check pins identify()'s skip of zero-interval triples in the noise estimate. Mutant 20f72103eda78713 at sysid.py:2018 (GUARD_OFF) survives the full gate (RED-AS-NULL), yet identify() moves on dup0_step: baseline [completed ua=0.19574719588552128 C=5.126629633823094 conf=0.9928502727789756], mutant [completed ua=0.19575055138538477 C=5.126622761903924 conf=0.9928505855787655] (3 count (of 3) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case with two same-phase samples at one timestamp (h_prev = 0) asserting they do not enter the second-difference noise estimate

### 50daaa57683189c5 — sysid.py:2018 CMP_BOUND (candidate)

Patch `if h_prev <= 1e-6: -> if h_prev < 1e-6:`. Gate RED-AS-NULL (gate_rc 1, wall 3296.0 s, load1 0.86..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_50daaa57.py`: baseline `[completed ua=0.19574717836315605 C=5.126629119820056 conf=0.9928503284067113]`, mutant `[completed ua=0.1957505338951885 C=5.1266222478985455 conf=0.9928506412102832]`; cases differing 3 count (of 3), null differing 0 count (of 2). Inputs tried: tie3600us_step (differs=1); tie3600us_step2 (differs=1); tie3600us_relax (differs=1); dup0_step (differs=0); gap3601us_step (differs=0).
Candidate: No check pins the h_prev <= 1e-6 h boundary of identify()'s noise-estimate skip. Mutant 50daaa57683189c5 at sysid.py:2018 (CMP_BOUND) survives the full gate (RED-AS-NULL), yet identify() moves on tie3600us_step: baseline [completed ua=0.19574717836315605 C=5.126629119820056 conf=0.9928503284067113], mutant [completed ua=0.1957505338951885 C=5.1266222478985455 conf=0.9928506412102832] (3 count (of 3) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case with two same-phase samples exactly 3600 us (1e-6 h) apart

### 4eeb366191982f92 — sysid.py:2032 CMP_BOUND (candidate)

Patch `if len(d2_all) >= 3: -> if len(d2_all) > 3:`. Gate RED-AS-NULL (gate_rc 1, wall 3321.2 s, load1 0.78..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_4eeb3661.py`: baseline `[completed ua=0.1931445891215017 C=4.5987039940244845 conf=0.3039170461625474]`, mutant `[completed ua=0.1931817916300817 C=4.598419055037595 conf=0.30391700686422346]`; cases differing 2 count (of 2), null differing 0 count (of 2). Inputs tried: 3triples_noise0.02 (differs=1); 3triples_clean (differs=1); 4triples_noise0.02 (differs=0); plant (differs=0).
Candidate: No check pins identify()'s three-triple minimum for the sensor-noise estimate. Mutant 4eeb366191982f92 at sysid.py:2032 (CMP_BOUND) survives the full gate (RED-AS-NULL), yet identify() moves on 3triples_noise0.02: baseline [completed ua=0.1931445891215017 C=4.5987039940244845 conf=0.3039170461625474], mutant [completed ua=0.1931817916300817 C=4.598419055037595 conf=0.30391700686422346] (2 count (of 2) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case with exactly three in-phase second differences asserting sigma2 is estimated (the EIV correction applied)

### 44bb0ce0b258242c — sysid.py:2038 CMP_BOUND (candidate)

Patch `if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0: -> if sigma2 > 0.0 and sigma2 >= x1_spread2 / 9.0:`. Gate RED-AS-NULL (gate_rc 1, wall 4182.5 s, load1 0.96..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_44bb0ce0.py`: baseline `[refused:fit gave implausible signs]`, mutant `[refused:sensor noise dominates the excursion]`; cases differing 1 count (of 1), null differing 0 count (of 2). Inputs tried: sigma_tie (differs=1); sigma_tie_broken (differs=0); plant (differs=0).
Candidate: No check pins identify()'s noise refusal at the sigma2 == spread/9 tie. Mutant 44bb0ce0b258242c at sysid.py:2038 (CMP_BOUND) survives the full gate (RED-AS-NULL), yet identify() moves on sigma_tie: baseline [refused:fit gave implausible signs], mutant [refused:sensor noise dominates the excursion] (1 count (of 1) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case at sigma2 == x1_spread2/9 exactly (constructible in float64: dyadic temps, three triples) asserting the window is not refused as noise-dominated

### 10665a84dc064489 — sysid.py:2114 GUARD_OFF (candidate)

Patch `if rank < 2: -> if False:`. Gate RED-AS-NULL (gate_rc 1, wall 4027.5 s, load1 0.79..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_10665a84.py`: baseline `[refused:step gave insufficient excitation]`, mutant `[completed ua=0.49999999999999967 C=9.999999999999996 conf=0.75]`; cases differing 2 count (of 2), null differing 0 count (of 2). Inputs tried: power_prop_delta (differs=1); power_zero (differs=1); power_const_rank2 (differs=0); plant (differs=0).
Candidate: No check pins identify()'s collinear-regressor refusal; without it a rank-1 fit completes. Mutant 10665a84dc064489 at sysid.py:2114 (GUARD_OFF) survives the full gate (RED-AS-NULL), yet identify() moves on power_prop_delta: baseline [refused:step gave insufficient excitation], mutant [completed ua=0.49999999999999967 C=9.999999999999996 conf=0.75] (2 count (of 2) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case whose power column is exactly proportional to (Tout - T) asserting completed=False with 'step gave insufficient excitation' (the mutant completes with an arbitrary UA/C split)

### d7421c10ed63c281 — sysid.py:2114 CMP_BOUND (candidate)

Patch `if rank < 2: -> if rank <= 2:`. Gate RED-AS-NULL (gate_rc 1, wall 4241.6 s, load1 1.02..0.99, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_d7421c10.py`: baseline `[completed ua=2.0 C=4.000000000000002 conf=0.75]`, mutant `[refused:step gave insufficient excitation]`; cases differing 1 count (of 1), null differing 0 count (of 2). Inputs tried: power_const_rank2 (differs=1); power_prop_delta_rank1 (differs=0); plant (differs=0).
Candidate: No check reaches identify()'s two-column fallback with full rank 2. Mutant d7421c10ed63c281 at sysid.py:2114 (CMP_BOUND) survives the full gate (RED-AS-NULL), yet identify() moves on power_const_rank2: baseline [completed ua=2.0 C=4.000000000000002 conf=0.75], mutant [refused:step gave insufficient excitation] (1 count (of 1) separating inputs, null 0 count (of 2)).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks an identify() case whose 4-column solve is singular (power constant, collinear with the intercept) but whose 2-column fallback has rank 2, asserting completed=True (UA 2.0, C 4.0)

### 3918ca4fedbfc5bb — sysid.py:1979 CLAMP_DROP (equivalent-candidate)

Patch `dof = max(len(rows) - n_cols, 1) -> dof = (len(rows) - n_cols)`. Gate RED-AS-NULL (gate_rc 1, wall 3273.4 s, load1 0.85..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_3918ca4f.py`: baseline `[completed ua=0.19999999999957135 C=5.050166665555526 conf=0.23485492174384634]`, mutant `[completed ua=0.19999999999957135 C=5.050166665555526 conf=0.23485492174384634]`; cases differing 0 count (of 5), null differing 0 count (of 0). Inputs tried: rows5_exact (differs=0); rows5_noisy (differs=0); rows6 (differs=0); gap_4rows_guarded (differs=0); plant (differs=0).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks none reachable: an input with rows <= 4 is refused at :1942 before :1979

### a9bc37e9ba781833 — sysid.py:2037 CLAMP_DROP (equivalent-candidate)

Patch `x1_spread2 = float(np.var(a[:, 0])) * n_rows / max(n_rows - 1.0, 1.0) -> x1_spread2 = float(np.var(a[:, 0])) * n_rows / (n_rows - 1.0)`. Gate RED-AS-NULL (gate_rc 1, wall 4283.8 s, load1 0.51..0.95, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_a9bc37e9.py`: baseline `[completed ua=0.19999999999957135 C=5.050166665555526 conf=0.23485492174384634]`, mutant `[completed ua=0.19999999999957135 C=5.050166665555526 conf=0.23485492174384634]`; cases differing 0 count (of 5), null differing 0 count (of 0). Inputs tried: rows5_exact (differs=0); rows5_noisy (differs=0); rows6 (differs=0); gap_4rows_guarded (differs=0); plant (differs=0).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks none reachable

### b97b45a6162a2f00 — sysid.py:2038 CMP_BOUND (equivalent-candidate)

Patch `if sigma2 > 0.0 and sigma2 > x1_spread2 / 9.0: -> if sigma2 >= 0.0 and sigma2 > x1_spread2 / 9.0:`. Gate RED-AS-NULL (gate_rc 1, wall 4099.1 s, load1 0.94..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_b97b45a6.py`: baseline `[refused:sensor drift collapsed into heat-loss]`, mutant `[refused:sensor drift collapsed into heat-loss]`; cases differing 0 count (of 6), null differing 0 count (of 0). Inputs tried: no_triples_relabelled_plant (differs=0); no_triples_exact_series (differs=0); two_triples (differs=0); no_triples_flat_delta (differs=0); sigma_tie (differs=0); plant (differs=0).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks none: no input separates `sigma2 > 0.0` from `sigma2 >= 0.0` here

### 6b6a8493668dde1c — sysid.py:2068 CMP_BOUND (equivalent-candidate)

Patch `if sigma2 > 0.0: -> if sigma2 >= 0.0:`. Gate RED-AS-NULL (gate_rc 1, wall 3887.2 s, load1 0.95..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_6b6a8493.py`: baseline `[refused:sensor drift collapsed into heat-loss]`, mutant `[refused:sensor drift collapsed into heat-loss]`; cases differing 0 count (of 5), null differing 0 count (of 0). Inputs tried: no_triples_relabelled_plant (differs=0); no_triples_exact_series (differs=0); two_triples (differs=0); no_triples_flat_delta (differs=0); plant (differs=0).
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks none: subtracting an exact zero is inert

### 3e78e62aa0f2e687 — sysid.py:2126 CMP_BOUND (equivalent-candidate)

Patch `if one_over_c <= 1e-6 or ua_over_c <= 1e-6: -> if one_over_c < 1e-6 or ua_over_c <= 1e-6:`. Gate RED-AS-NULL (gate_rc 1, wall 4288.5 s, load1 0.79..1.01, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_3e78e62a.py`: baseline `[refused:fit gave implausible signs]`, mutant `[refused:fit gave implausible signs]`; cases differing 0 count (of 1602), null differing 0 count (of 1). Inputs tried: negative_ua (differs=0); plant (differs=0); 1601 tie-search inputs (ulp-300..+300, rand0..999), 0 differ.
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks none found: no input tried lands the fitted value on 1e-6

### 87c3101b5663f17b — sysid.py:2126 CMP_BOUND (equivalent-candidate)

Patch `if one_over_c <= 1e-6 or ua_over_c <= 1e-6: -> if one_over_c <= 1e-6 or ua_over_c < 1e-6:`. Gate RED-AS-NULL (gate_rc 1, wall 4323.6 s, load1 0.85..0.92, provisional).
Probe `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/wave/D3-g34/probes/probe_87c3101b.py`: baseline `[refused:fit gave implausible signs]`, mutant `[refused:fit gave implausible signs]`; cases differing 0 count (of 1602), null differing 0 count (of 1). Inputs tried: negative_ua (differs=0); plant (differs=0); 1601 tie-search inputs (ulp-300..+300, rand0..999), 0 differ.
Should have failed: tests/features.py, the identify() checks at :7848-7890 ('a fit with no samples fails cleanly', 'a fit outside the plausible (tau, UA) box is refused') and :29353-29440, the closure script whose traced baseline executes the line (tests/closures.json lists tests/features.py among sysid.py's readers); it lacks none found: no input tried lands the fitted value on 1e-6

## Leads

- 07227ec96c3e14de (custom_components/heatpump_optimizer/sysid.py:2126, if one_over_c <= 1e-6 or ua_over_c <= 1e-6: -> if False:) is KILLED only by tests/structure.py's max_cc ratchet reading the tree as IMPROVED (44 -> 43), not by a behavioural assertion; its probe separates 1 of 1 input (the refusal reason changes, the outcome stays a refusal). Any GUARD_OFF on identify() that lowers max_cc is killed this way regardless of behaviour.

## Unfinished

- none

## Coverage

D3.M3: universe 742 (the wave list), examined 16 on this box; the rest are assigned to boxes D3-g01..D3-g47 (not_reached in REPORT.json). D3.M1, D3.M2, D3.M4 and D3.M5 rows and their redispatched C-items are carried verbatim from REPORT-D3-u1b.json.
