# D3-s1 box D3-g18: full gate for 16 D3.M3 full-net survivors (round 11)

Baseline `92d38ecb640bd462f2e19c0814d0f0b7df1ee692`. Report JSON: `dev/audit/rounds/round11/D3/s1/wave/D3-g18/REPORT.json`.

## Machine and controls

4 vCPU Intel(R) Xeon(R) Processor @ 2.10GHz, 16 GB, no swap; MACHINE.txt holds both fires' readings. Every wall, CPU and load number is provisional.

Null control (`fullgate.py null`, comment-only marker): gate_rc 1, wall 3464.0 s, red scripts python3 tests/closure.py selftest (2), python3 tests/entities.py (1), python3 tests/harness_headers.py (3), all artefact checks (gates/null-note.txt). A mutant counts KILLED only on a script beyond these or more FAIL lines in one.

## Tally

- gated: 16 of 16; TIMEOUT: 0; not gated: 0
- verdicts: KILLED 1, RED-AS-NULL 15
- KILLED by: python3 tests/stress.py 1
- candidates (gate survivors whose probe moves): 5; equivalent-candidates: 10; killed: 1

| key | site | verdict | killed_by | class |
|---|---|---|---|---|
| 2580fdeb3923a03e | dhw_planner.py:1613 RETURN_DEL | RED-AS-NULL | - | equivalent-candidate |
| 64576dd552491452 | dhw_planner.py:1627 GUARD_OFF | RED-AS-NULL | - | candidate |
| 91617fb42e33ebdf | dhw_planner.py:1800 CMP_BOUND | RED-AS-NULL | - | candidate |
| fabfc9228615948e | dhw_planner.py:1803 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| ef125fd473e20ed2 | dhw_planner.py:1822 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| ff4f903a5a5c3f55 | dhw_planner.py:1828 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| 3c6e75178a60d75e | dhw_planner.py:1870 CMP_BOUND | KILLED | python3 tests/stress.py | killed |
| d7e250feefbd0343 | dhw_planner.py:1871 CLAMP_DROP | RED-AS-NULL | - | equivalent-candidate |
| e11dcf62611a5d1c | dhw_planner.py:1872 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| 936bcb2da6441e86 | dhw_planner.py:1893 GUARD_OFF | RED-AS-NULL | - | candidate |
| 2aa0f17a216035ee | flow_lift.py:51 CONST | RED-AS-NULL | - | candidate |
| 19ac62540d0d5ee8 | flow_lift.py:232 CMP_BOUND | RED-AS-NULL | - | equivalent-candidate |
| 3b87cd840077679e | grid_fee.py:445 CONST | RED-AS-NULL | - | equivalent-candidate |
| ee2d5a67d9d3a7f9 | grid_fee.py:329 GUARD_OFF | RED-AS-NULL | - | equivalent-candidate |
| db32007740226522 | grid_fee.py:187 GUARD_OFF | RED-AS-NULL | - | equivalent-candidate |
| 9297f123a6265555 | grid_fee.py:483 GUARD_OFF | RED-AS-NULL | - | candidate |

## Survivors: step-4 answers and probe numbers

### 2580fdeb3923a03e — dhw_planner.py:1613 RETURN_DEL (equivalent-candidate)

`return best -> pass` in `DhwPlanner._plan_dhw_min_cost`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2902.1 s, load1 0.72..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: dev/audit/rounds/round11/D3/s1/m4_u1a_part*.json

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_2580fdeb3923a03e.py`: baseline real-solver failures (infeasible, unbounded, iteration limit): x=None -> plan None (greedy fallback); golden_dhw_lp_failures=0; mutant the same three failures: plan None (differing_real_failures=0); a stubbed failure carrying a vector: the vector is published (differing_failure_with_vector=1). Inputs tried: a solvable 12-step program (branch not reached, reached_ok_solve=0); three genuinely failing scipy 1.18.1 programs (status 2, 3, 1); a stub failure with x kept (status 4 shape); three golden DHW scenarios (winter_single_dhw, winter_two_zone_dhw, summer_dhw_only) for reach. Line 1613 is not reached by any traced baseline, by the three golden DHW scenarios (0 solver failures) or by 147 captured production calls (40 golden DHW scenarios + 60 randomized variants, 0 failures); the installed scipy returns x=None on every failure status reproduced, so `pass` falls into `if solution is None: return best` (1616). Only a solver failure that still carries a vector separates the arms; none was found. Unreachable in practice: an unreachable line, not a test gap.

Should fail: none through production with the installed scipy: no closure script's traced baseline executes dhw_planner.py:1613; a check would need linprog to fail with a vector (e.g. tests/features.py patching dhw_planner.linprog to return success=False with x set and asserting _plan_dhw_min_cost returns None).

### 64576dd552491452 — dhw_planner.py:1627 GUARD_OFF (candidate)

`if np.allclose(refined, cop, rtol=0.02): -> if False:` in `DhwPlanner._plan_dhw_min_cost`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2771.4 s, load1 0.86..0.93 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: dev/audit/rounds/round11/D3/s1/m4_answers_u1b.json

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_64576dd552491452.py`: baseline plan returned after the first pass when it is already COP-consistent (17 of 600 seeded calls); mutant a second program solved at the refined COP: 16 of those 17 plans differ, max per-step delta 1.740 kW; null (first pass not converged) 0 differing; golden_first_pass_converged=0. Inputs tried: 600 seeded direct calls (tank 80-300 L, cooling 0.1-1.0 C/h, 4-23 steps, dt 0.25/1 h, flat / one-decimal / continuous prices, outdoor -15..20 C, requirement 40-58 C, start -8..+3 K around it, random draws, cap 1.5-4 kW); 3 golden DHW scenarios; 147 captured production calls (0 first-pass convergences there). The guard decides only when the first LP pass is already COP-consistent; that never happened in 147 captured production calls nor in the 3 golden scenarios, and happened in 17/600 seeded direct calls (flat or one-decimal prices: a degenerate LP whose tie-break the refined COP moves).

Should fail: tests/features.py's _plan_dhw_min_cost checks (features.py ~63150, ~63611, ~63732, ~63784) execute line 1627 on the traced baseline but none poses a first pass that is already COP-consistent (start at the requirement level on tied prices) and asserts the first-pass plan is returned (or that one program is solved).

Candidate: **No check makes the DHW cost LP's first pass COP-consistent; dropping its early exit moves the plan unseen** (class_guess I1, severity low); null: calls whose first pass did not converge: null_differing=0 (both arms solve the same two programs).

### 91617fb42e33ebdf — dhw_planner.py:1800 CMP_BOUND (candidate)

`pinned = np.where(temps[: b + 1] >= ceiling[: b + 1] - 0.1)[0] -> pinned = np.where(temps[: b + 1] > ceiling[: b + 1] - 0.1)[0]` in `DhwPlanner._repair_dhw_floor`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 3233.0 s, load1 0.79..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1c.json

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_91617fb42e33ebdf.py`: baseline one-decimal start 0.1 K under the ceiling (step 0 ties): plan as baseline; e.g. case 226 13.06 kWh; mutant sensor_reading_differing=3 of 500 (case 226: 13.06 -> 9.48 kWh, c=0.232 kWh/K, 4.8 kW cap); bisected exact ties in the first round: 262 ties, 0 differing; plain calls 0 differing. Inputs tried: 262 double-precision crossings of temps[i] - (ceiling[i] - 0.1) bisected on the start temperature (200 seeded near-ceiling calls); 1500 seeded calls; 500 seeded near-ceiling calls started from float(f'{ceil-0.1:.1f}'), which equals ceil - 0.1 exactly for every ceiling tried. A one-decimal tank reading exactly 0.1 K under the charge ceiling (64.9 under 65) is an exact tie at step 0; 3 of 500 such seeded calls move. Not seen in the 147 captured production calls.

Should fail: tests/features.py's floor-repair checks (the `_fr_fixed` 'the repair closes the breach' block at ~41112, ~63196, ~63616, ~63797, ~82600) execute line 1800 but none starts the tank on the pin boundary (ceiling - 0.1 exactly) and asserts that step counts as full.

Candidate: **No check starts the DHW floor repair exactly 0.1 K under the ceiling; the pinned-step >= boundary is unpinned** (class_guess I1, severity low); null: 1500 seeded calls with no tie forced: differing_plain_calls=0.

### fabfc9228615948e — dhw_planner.py:1803 CMP_BOUND (equivalent-candidate)

`usable = headroom > 1e-6 -> usable = headroom >= 1e-6` in `DhwPlanner._repair_dhw_floor`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 3231.9 s, load1 0.78..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1d.json

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_fabfc9228615948e.py`: baseline exact_ties_in_envelope=0 of 802000 (p_dhw_max, plan) pairs; differing_in_envelope=0 of 1500; mutant differing only outside the envelope: p_dhw_max=1e-6 -> 266 of 300 differ. Inputs tried: p_dhw_max over 2000 values in [0.1, 10] x the 401 doubles around p_dhw_max - 1e-6; 1500 seeded production-envelope calls; 300 seeded calls with p_dhw_max = 1e-6. headroom = p_dhw_max - plan equals 1e-6 exactly only if p_dhw_max < 0.0625 (Sterbenz: for p >= 0.0625 the difference is an exact multiple of 2^-56, and 1e-6 is not); _build_dhw_requirements sets p_dhw_max = p_dhw_run >= 0.1 (dhw_planner.py:1138-1140). Equivalent at the production seam.

Should fail: none through production: no producer delivers p_dhw_max < 0.1; a direct unit call with p_dhw_max = 1e-6 separates.

### ef125fd473e20ed2 — dhw_planner.py:1822 CMP_BOUND (equivalent-candidate)

`if decay > 1e-6: -> if decay >= 1e-6:` in `DhwPlanner._repair_dhw_floor`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 3286.9 s, load1 0.79..0.94 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1d.json

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_ef125fd473e20ed2.py`: baseline exact_decay_ties=0 of 40001 ratios; differing_derived_decay=0 of 1500; mutant differing only with a context forced to report decay = 1e-6: 1 of 300. Inputs tried: the 40001 doubles x around 1 - 1e-6 through dhw_planner._tank_decay; 1500 seeded calls with the derived decay; 300 seeded calls whose _DhwPlanContext subclass reports tank_decay = (1e-6, gain). decay = clip(1 - ua*dt/c, 0, 1): for x >= 0.5, 1 - x is exact and a multiple of 2^-53, and 1e-6 is not, so the derived decay never equals 1e-6; _DhwPlanContext.tank_decay -> _tank_decay is the only producer. Equivalent at the production seam.

Should fail: none: no tank volume, loss or step length yields decay == 1e-6.

### ff4f903a5a5c3f55 — dhw_planner.py:1828 CMP_BOUND (equivalent-candidate)

`usable &= room_c > 0.01 -> usable &= room_c >= 0.01` in `DhwPlanner._repair_dhw_floor`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 3346.3 s, load1 0.87..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: dev/audit/rounds/round11/D3/s1/m4_answers-D3-u1d.json

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_ff4f903a5a5c3f55.py`: baseline exact_ties=0 at 45 bisected crossings (2838 inputs tried); two_decimal_ceiling_ties=0; differing_plain_calls=0 of 1500; mutant identical plans on every input tried. Inputs tried: 45 double-precision crossings of room_c - 0.01 bisected on the start temperature over 1200 seeded near-ceiling calls (rising-ceiling variant included), 32 doubles either side; ceilings 40-80 C in 0.5 K steps against a two-decimal reading 0.01 K under them; 1500 seeded calls. A gap between doubles in [32, 64) is a multiple of 2^-47 and 0.01 lies 2.0e-15 from the nearest one, far beyond the rounding of the decay weighting, so room_c == 0.01 needs a suffix-minimum carried from a later step at an exact product; none found.

Should fail: none found: no input tried reaches room_c == 0.01.

### d7e250feefbd0343 — dhw_planner.py:1871 CLAMP_DROP (equivalent-candidate)

`runnable = min(min_run_power, p_dhw_max) -> runnable = (min_run_power)` in `DhwPlanner._repair_dhw_floor`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 3247.6 s, load1 0.38..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: d7e250feefbd0343 (u1d): when min_run_power > p_dhw_max the repair places a block above p_dhw_max; should fail: a floor-repair check with min_run_power > p_dhw_max asserting every repaired step <= p_dhw_max.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_d7e250feefbd0343.py`: baseline calls_in_envelope=1500, differing_in_envelope=0; golden_min_run_above_cap=0; mutant differing_in_envelope=0 of 1500; outside the envelope (min_run_power > p_dhw_max) 122 of 600 differ, max_over_cap_kw_mutant=0.000000 kW. Inputs tried: 1500 seeded direct calls inside the production envelope (p_dhw_max >= 0.1, min_run_power <= p_dhw_max); 600 seeded calls outside it (min_run_power > p_dhw_max); every repair call of the golden DHW scenarios. min_run_power <= p_dhw_max is guaranteed by _build_dhw_requirements (dhw_planner.py:1141, min_run_power = min(p_dhw_run, ...) with p_dhw_max = p_dhw_run at 1226), so the clamp is the identity on every production input; only out-of-envelope calls move, and even there line 1879 still clips every published step to p_dhw_max (0.000 kW over cap), refuting the carried M4 claim that the repair publishes above the cap. Equivalent at the production seam.

Should fail: none at the production seam: no configuration reaches min_run_power > p_dhw_max.

### e11dcf62611a5d1c — dhw_planner.py:1872 CMP_BOUND (equivalent-candidate)

`if runnable > plan[j] + room_kw + 1e-9: -> if runnable >= plan[j] + room_kw + 1e-9:` in `DhwPlanner._repair_dhw_floor`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2995.5 s, load1 0.78..0.96 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: e11dcf62611a5d1c (u1d): `>` -> `>=` with a 1e-9 epsilon: exact-boundary only; near-equivalent.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_e11dcf62611a5d1c.py`: baseline exact_ties=0 at 89 bisected crossings (17978 inputs tried); comparisons_not_positive_plain=0 of 2510 reached; mutant differing_at_ties=0; identical plans on every input tried. Inputs tried: 89 double-precision crossings of line 1870's boundary bisected over 400 seeded near-ceiling calls, 100 doubles either side (17978 inputs); 1500 seeded calls (2510 comparisons reached). Inside the line-1870 branch new_level < min_run_power - 1e-9 and, with min_run_power <= p_dhw_max, runnable - (plan[j] + room_kw) is never on the 1e-9 boundary: no exact tie exists in the inputs tried. Equivalent-candidate.

Should fail: none: no input found where runnable == plan[j] + room_kw + 1e-9.

### 936bcb2da6441e86 — dhw_planner.py:1893 GUARD_OFF (candidate)

`if np.array_equal(plan, before): -> if False:` in `DhwPlanner._repair_dhw_floor`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2957.6 s, load1 0.97..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: 936bcb2da6441e86 (u1c): should_have_failed tests/block_duty.py, doc_claims.py, entities.py, env_drift.py, features.py, manual_plan.py, optimality.py, plan_view.py, validate.py; full net SURVIVED.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_936bcb2da6441e86.py`: baseline differing_plans=0 (self); shortfall_ksteps_baseline=57165.329 K over 1500 seeded calls; golden_calls=5; mutant differing_plans=35 of 1500; shortfall_ksteps_mutant=58050.843 K (+885.5 K-steps); calls_mutant_more_shortfall=30; golden_differing=0 of 5. Inputs tried: 1500 seeded direct calls inside the production envelope (p_dhw_max >= 0.1, min_run_power <= p_dhw_max); the 5 repair calls three golden DHW scenarios make. executed by 9 closure scripts (state/reach.tsv). The guard marks a breach whose top-up the capacity clamp removed again as unreachable; without it the 48-round budget is spent retrying that breach and later breaches go unrepaired: 35 of 1500 plans differ, 30 with more residual floor shortfall. The golden scenarios never hit an unreachable breach (0 of 5 differ).

Should fail: tests/block_duty.py's floor-repair checks (block_duty.py:1003-1037, the place_startable / bounded-rounds pins) and tests/features.py's _repair_dhw_floor checks (features.py:41112-41131, 63300) execute line 1893 on the traced baseline (state/reach.tsv), but none poses a breach that no ceiling-legal top-up can close followed by a later closable breach and asserts the later one is repaired (or that the unreachable breach is not retried).

Candidate: **No check poses an unreachable DHW floor breach before a closable one; dropping the repair's skip leaves the later breach unrepaired unseen** (class_guess I1, severity medium); null: golden DHW scenarios' own repair calls: golden_differing=0 of 5 (every top-up survives the clamp).

### 2aa0f17a216035ee — flow_lift.py:51 CONST (candidate)

`FLOW_BIAS_MIN_SAMPLES = 5 -> FLOW_BIAS_MIN_SAMPLES = 10` in `<module>`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2888.7 s, load1 0.71..1.0 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: 2aa0f17a216035ee (u1a, m4_u1a_part10.json): gap. Should fail: a FlowCurveBias unit feeding 6 residuals asserting the switch from plain mean to EWMA; unpinned (the same seam as the flow_lift.py:188 survivor).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_2aa0f17a216035ee.py`: baseline bias_baseline=3.000000 K (sixth fold is the EWMA 0.9*2 + 0.1*12); mutant bias_mutant=3.666667 K (still the plain mean (5*2+12)/6): delta 0.666667 K; null (three folds) delta 0.000000 K; the arms never re-agree within 40 folds. Inputs tried: five residuals of +2 K then one of +12 K at curve 25 C; null: three folds; the same stream to 40 folds. flow_lift.py:51 is executed by 16 closure scripts (state/reach.tsv); FlowCurveBias.observe reads the constant at line 188 (executed by config_flow_steps.py, doc_claims.py, features.py). The warm-up length decides when the learned supply-temperature bias switches from a plain mean to the EWMA; doubling it moves the bias by 0.67 K on a six-sample stream and the difference persists.

Should fail: tests/features.py's FlowCurveBias checks (features.py:34733-34822, e.g. 'the first sample is the mean, not a tenth of itself') execute flow_lift.py:51/188 on the traced baseline but none feeds more samples than the warm-up and asserts the fold that switches from plain mean to EWMA (sample 6 -> 0.9*prev + 0.1*r); tests/doc_claims.py:1951-1961 reads FLOW_BIAS_MIN_SAMPLES only to compare it against its own document, so a coordinated doc+code change goes unseen.

Candidate: **No check pins the flow-curve bias warm-up length; FLOW_BIAS_MIN_SAMPLES 5 -> 10 moves the learned bias 0.67 K unseen** (class_guess I1, severity low); null: three folds, inside both warm-ups: null_delta=0.000000 K.

### 19ac62540d0d5ee8 — flow_lift.py:232 CMP_BOUND (equivalent-candidate)

`if not np.isfinite(bias) or samples < 0: -> if not np.isfinite(bias) or samples <= 0:` in `FlowCurveBias.from_dict`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2877.6 s, load1 0.93..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: 19ac62540d0d5ee8 (u1a, m4_u1a_part7.json): equivalent; a stored zero-sample state returns a fresh learner, which the following comment says is the same inert state.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_19ac62540d0d5ee8.py`: baseline differing_inputs=0 of 14; zero_sample_restores_inert_baseline=1; mutant differing_inputs=0 of 14; zero_sample_restores_inert_mutant=1; positive control (line 237's guard also dropped) differs on 3. Inputs tried: samples in {-1, 0, 1, 7} x bias in {0.0, 4.5, -20.0}, plus bias nan, samples '0' (string), samples 0.0 (float). The samples == 0 case the edit adds already returns cls() two lines later (line 237-238), so both arms restore the same inert learner; the positive control shows the probe can see a difference when one exists.

Should fail: none: the mutant is equivalent.

### 3b87cd840077679e — grid_fee.py:445 CONST (equivalent-candidate)

`CATALOG_VERSION = 1 -> CATALOG_VERSION = 2` in `<module>`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2836.9 s, load1 0.78..0.92 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: 3b87cd840077679e (u1a, m4_u1a_part14.json): gap. Should fail: a test pinning the catalogue version a stored config is migrated against; no test reads CATALOG_VERSION.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_3b87cd840077679e.py`: baseline differing_returns=0 of 5 ids; production_readers_of_constant=1 (grid_fee.py:497, a DEBUG line); mutant differing_returns=0 of 5; differing_debug_text=2 ('Applying DSO catalog v1' -> 'v2'); null_delta_returns=0. Inputs tried: 'none', 'ellevio_villa_effekt_2026', 'goteborg_energi_effekt_2026', 'not_a_dso', None; AST count of Name loads of CATALOG_VERSION over every production module. The only production reader is the DEBUG record at grid_fee.py:497; no config field, store key or migration reads it, so the carried M4 premise (a stored config migrated against the version) does not exist at this baseline. Equivalent at every config output; only the DEBUG text moves, so a later seat may re-class it.

Should fail: none: no behaviour beyond a DEBUG log string reads CATALOG_VERSION.

### ee2d5a67d9d3a7f9 — grid_fee.py:329 GUARD_OFF (equivalent-candidate)

`if self.mode == MODE_NONE or n == 0: -> if False:` in `GridFeeSchedule.fee_vector`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 2889.8 s, load1 0.72..1.0 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: ee2d5a67d9d3a7f9 (u1d): falls through for MODE_NONE; likely near-equivalent. Should fail: a fee_vector check with mode none and a stale rules list asserting all zeros.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_ee2d5a67d9d3a7f9.py`: baseline differing_cases=0 (self); mode_none_active=0; mutant differing_cases=4 of 36, all entity mode with n == 0 (IndexError on step_starts[0]); differing_mode_none_cases=0; production_deliverable_differing=0. Inputs tried: mode in {none, rules, entity} x n in {0, 1, 96} x entity value in {None, 0.4} x rules in {[], [Nov-Mar Mon-Fri 06-22 = 0.5, = 0.1]}. Mode none with stale rules returns zeros either way (current_fee returns 0.0 in mode none), refuting the carried M4 test idea; only n == 0 in entity mode moves, and the one production caller (coordinator.py:7272 via _fee_series) is gated on schedule.active and passes n_steps > 0. Equivalent at the production seam.

Should fail: none at the production seam: the caller never passes n == 0.

### db32007740226522 — grid_fee.py:187 GUARD_OFF (equivalent-candidate)

`if not token: -> if False:` in `_parse_rule`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 3264.5 s, load1 0.85..0.93 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: db32007740226522 (u1d): tokens come from body.split() and strip(), which never yields an empty string; equivalent (dead guard).

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_db32007740226522.py`: baseline differing_lines=0 of 15; empty_tokens_seen=0; mutant differing_lines=0 of 15; positive control (split(' ')) differs on 6. Inputs tried: ordinary rules, empty body, doubled spaces, tabs, NBSP, EM SPACE, \x1c-\x1f separators, trailing newline, a whitespace-only rule before '=', three malformed lines (error text compared). str.split() never yields a token strip() empties, so the guard is dead; the positive control shows the probe sees the guard when empty tokens exist.

Should fail: none: the mutant is equivalent.

### 9297f123a6265555 — grid_fee.py:483 GUARD_OFF (candidate)

`if not product_id or product_id == DSO_PRODUCT_NONE: -> if False:` in `apply_catalog`. Gate: verdict RED-AS-NULL, gate_rc 1, wall 3463.7 s, load1 0.86..1.0 (provisional; nproc 4, Intel Xeon @ 2.10GHz). Carried M4: 9297f123a6265555 (u1c): should_have_failed tests/config_flow_steps.py, entities.py, features.py; full net SURVIVED.

Probe `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_9297f123a6265555.py`: baseline warnings_baseline=0 over 3 submits (dso_product 'none', absent, ''); mutant warnings_mutant=3 ('Unknown DSO catalog product none|None|; not writing', one per submit); differing_stored_fields=0; null (a real product) delta 0. Inputs tried: config-flow grid-fee submits with dso_product 'none' (the default choice), absent, ''; null: 'goteborg_energi_effekt_2026'. executed by config_flow_steps.py, entities.py, features.py (state/reach.tsv). Without the guard every grid-fee step finished with the default 'none' product logs a WARNING 'Unknown DSO catalog product' into the Home Assistant log; the stored fields are unchanged.

Should fail: tests/entities.py:8236 'none writes nothing' and :8232 'an unknown catalog id writes nothing' execute line 483 on the traced baseline and assert the return only; neither (nor config_flow_steps.py's grid-fee step) asserts that the 'none' choice logs no WARNING, the one output that separates 'none' from an unknown id.

Candidate: **No check separates the DSO 'none' choice from an unknown catalog id; dropping the guard logs a WARNING on every default grid-fee submit unseen** (class_guess new, severity low); null: a real catalog product id: both arms write the row with no warning (null_delta_warnings=0).

### 3c6e75178a60d75e — dhw_planner.py:1870 CMP_BOUND (KILLED)

the suite fails on mutant 3c6e75178a60d75e (dhw_planner.py:1870 CMP_BOUND): KILLED by python3 tests/stress.py; gate_rc=1, wall 3328.7 s (provisional). python3 tests/stress.py: FAIL no scenario's simulate kernel got slower per call on an unchanged plan (round-5 D9-07)  [summer/1z/dhw/fuse-cap spent 81 ms of kernel CPU against the baseline's 45 ms = 1.81x, over the 1.80x factor on work the counts vouch at 1.00x, on an unchanged plan (objective 6437.359986); this is the per-call-cost half -- a kernel that got slower PER CALL moves no count at all,  | python3 tests/stress.py: 1 of 116 STRESS CHECKS FAILED | python3 tests/stress.py: >>> FAILED: python3 tests/stress.py

## Unfinished

none

## Harnesses

- `dev/audit/rounds/round11/D3/s1/fullgate.py`; procedure: gate_wave.sh (see REPORT.json `procedure`)
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_19ac62540d0d5ee8.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_2580fdeb3923a03e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_2aa0f17a216035ee.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_3b87cd840077679e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_3c6e75178a60d75e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_64576dd552491452.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_91617fb42e33ebdf.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_9297f123a6265555.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_936bcb2da6441e86.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_d7e250feefbd0343.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_db32007740226522.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_e11dcf62611a5d1c.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_ee2d5a67d9d3a7f9.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_ef125fd473e20ed2.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_fabfc9228615948e.py`
- `dev/audit/rounds/round11/D3/s1/wave/D3-g18/probes/probe_ff4f903a5a5c3f55.py`

Findings: [] (ids are assigned at consolidation); candidates are under `gate_survivors` in REPORT.json.
