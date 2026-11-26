# D3 wave verifier record, round 11 (one verifier, three lenses)

Unit: the D3 u1 full-gate wave's gate survivors (`gate_survivors` of each `REPORT-D3-gNN.json`), one vote per mutant key. Ids are `D3-wave-<key>` until the consolidation step assigns D3-s1-72..99 by file and gap kind (d3wave PLAN, final ruling); a consolidated finding inherits the votes of the keys it lists. Equivalent candidates and KILLED keys are non-findings and get no vote.

Baseline tree: 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 with the harvested D3 evidence copied over it. Host: 8-core Apple silicon macOS, CPython 3.14 from venv-ci, numpy 2.5.5, scipy 1.18.1; load1 30-70 from other seats, so every number used is a count or a solver value, never a timing.

Not run here, by the brief: the judge, dedup and the class sweep (they wait for all 47 boxes).

## Stages

| stage | boxes | findings | votes |
|---|---|---|---|
| 1 | g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14, g15, g16, g17, g18, g19, g20, g21, g22, g23, g24, g25, g26, g27, g28, g29, g30, g31, g32, g33, g34, g35, g37, g38, g39, g41 | 381 | {'verify': 369, 'weaken': 9, 'unresolved': 3} |
| 2 | g36 | 14 | {'verify': 14} |
| 3 | g40 | 4 | {'verify': 4} |
| 4 | g43 | 2 | {'verify': 2} |
| 5 | g45 | 11 | {'unresolved': 11} |
| 6 | g44 | 7 | {'verify': 7} |
| 7 | g42 | 7 | {'verify': 7} |
| 8 | g46-h | 0 | {} |
| 9 | g46-h | 0 | {} |
| 10 | g46-h | 0 | {} |
| 11 | g46-h | 0 | {} |
| 12 | g46-h, g47-h | 0 | {} |
| 13 | g46-h, g47-h | 0 | {} |
| 14 | g46-h, g47-h | 0 | {} |

Total: 426 findings; {'verify': 403, 'weaken': 9, 'unresolved': 14}.

## Method

- **V1 reproduce.** Every probe re-run as its header says (`PYTHONPATH=tests/hastub python3 <probe>`, plus `--mutant` for the two-run probes of D3-g33) in the baseline tree; output in `out/v1/`, `out/v1m/`. Moved = baseline and mutant arm values the probe prints differ (`harness/v1_analyse.py`); else every value the finder stated is reproduced and the record's two values differ. Null control = the probe's null lines, which must not move. Leave-one-out does not apply: no aggregate claim.
- **V2 independent.** `harness/run_v2.py` writes the one-line mutant (fullgate's own mutant record, refusing a moved line) into the production file of a private clone and re-runs the scenario. Metric: whether the finder's in-memory perturbation is the real source mutant. Most probes refuse the on-disk mutant because they rebuild the mutated body from the source text, so their mutant arm is the literal edit (faithful by construction); probes that patch a module global in both arms are inconclusive by construction; the rest are compared arm by arm.
- **V3 reach and class.** `harness/v3.py`: traced reach from the wave's REACH.tsv; production references to the mutated symbol outside its definition; whether the function names a `tests/ha_contract.py` DIVERGENT stub symbol; the seam_rule's shape (executed only when it is a plain read-only grep/awk pipeline); the five record fields (claim, evidence, harness, metric, perturbation), all present on every record. Class: I1 for every test-gap key, as VD3L corrected `new` before.
- **Gate.** The full gate was not re-taken (about 1 h per key on a quiet 4-core box; this host is shared at load 30-70). Every vote cites the box's gate record. Attack carried on every vote: the stripped finder tree's null is red on `closure.py selftest`, `entities.py` and `harness_headers.py`, so a kill by those three only shows as a rising fail count; the judge's runners should re-take the gate on an unstripped tree.
- **Severity.** Highs whose consequence is a published attribute or report key, or a derate that re-learns, are graded medium (5); keys with no production reference would be cut to nit (none found by the scan; one cut by its own reach line).

## Constraint on the judge's gate re-take: the null is still red on the unstripped tree (unverified cause)

The three scripts red in every wave box's null, run once each on this seat's baseline tree (92d38ecb640bd462f2e19c0814d0f0b7df1ee692, unstripped, with the harvested D3 evidence copied over it), `PYTHONPATH=tests/hastub python3 <script>`, host load1 30-70:

| script | wall | result |
|---|---|---|
| `tests/closure.py selftest` | 16 s | rc 0, all 118 closure shrink pins passed |
| `tests/entities.py` | 2021 s | rc 1, 1 of 2722 entity checks failed |
| `tests/harness_headers.py` | 513 s | rc 1, 1 of 115 harness header checks failed |

Finding: removing the strip does not make the null green. `entities.py` and `harness_headers.py` still fail one check each, so a kill by either can still show only as a rising fail count. Cause unverified: the likeliest is the D3 evidence files copied into the tree (untracked to the suite's classification and header checks), but the failing check lines were not read. Constraint: before the judge's runners re-take any wave gate, they need a tree whose null is green, with its failing checks named and the cause confirmed. Re-running the two scripts per mutant here would cost about 42 min each (about 270 h for 381 keys), which is why this seat did not.

Carry: R11-D3-JUDGE

## Votes other than verify

| stage | key | box | site | vote | severity | value | why |
|---|---|---|---|---|---|---|---|
| 1 | ac6bedc70bb82ff7 | D3-g03 | coordinator.py:8265 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('manual_plan_published', ['True', 'False']) | severity: claimed high, graded medium by consequence: the consequence is a published attribute (manual_override reads None); no actuator or plan moves |
| 1 | 6aeb83e5435c9cac | D3-g04 | coordinator.py:10428 | weaken | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('', ["{'month': '2026-11', 'kwh': 10.0, 'hourly_spot_sek': 12.0, 'grid_fee_sek': 3.0, 'monthly_avg_spot_sek': 15.0,  | severity: claimed high, graded medium by consequence: the consequence is a missing report key (grid_fee_sek) in the contract comparison; no control path reads it |
| 1 | d06a2d8e53342785 | D3-g04 | coordinator.py:10433 | weaken | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('', ["{'month': '2026-11', 'kwh': 10.0, 'hourly_spot_sek': 12.0, 'grid_fee_sek': 3.0, 'monthly_avg_spot_sek': 15.0,  | severity: claimed high, graded medium by consequence: the consequence is the contract comparison's monthly-average entry vanishing from a report; no control path reads it |
| 1 | d943cc9f7670a834 | D3-g05 | coordinator.py:7069 | weaken | medium | V1 0 arm pair(s) moved, null moved 1; e.g. None | null control: MOVES or unparsed (1 null pair(s) moved 1; null lines ['null_forecast_held baseline=(1, 1, 1, [\'No forecast data returned for weather.home\']) mutant=(1, 1, 1, ["Error fetching weather forecast: \'weather.home\'"])']); severity: claimed medium, kept: not re-graded beyond reach in this |
| 1 | 61e748f094f2daa8 | D3-g11 | coordinator.py:6454 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('issues_left_after_recovery_3_failures', ['0', '1']) | severity: claimed medium, kept: not re-graded beyond reach in this stage; reach: the function names DIVERGENT stub symbols ['HomeAssistantError']: real-HA reach unproven |
| 1 | a33188790c5affad | D3-g11 | coordinator.py:6454 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('issues_left_after_recovery_3_failures', ['0', '1']) | severity: claimed medium, kept: not re-graded beyond reach in this stage; reach: the function names DIVERGENT stub symbols ['HomeAssistantError']: real-HA reach unproven |
| 1 | 4aac8e694ddc5dfe | D3-g12 | defrost.py:537 | weaken | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('duty0.0_restored_duty_count', ['12', '0']) | severity: claimed high, graded medium by consequence: zero-duty buckets re-learn after a restart: a transient derate (1.0 -> 0.8571) until re-measured, not a lasting fault |
| 1 | b1a8d3056bf42597 | D3-g17 | dhw_planner.py:1527 | weaken | nit | differing_pmax_nonpos=120/120 (max_delta 3 kW) but differing_pmax_pos=0/120; null 0/60 | null control: MOVES or unparsed (0 null pair(s) moved 0; null lines ['null_differing=0/60', 'inputs_tried=120 random at p_total_max 1/3 with demand -3..4; 120 random at p_total_max -0.5/0 with demand -3..4; 60 at p_total_max 0 with demand 0..4 (null)']); read by hand: the mutant moves the plan only  |
| 1 | a66e107749d0ae11 | D3-g21 | optimizer.py:5945 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('required_now', ['55.0', '20.0']) | severity: claimed high, graded medium by consequence: the consequence is the published dhw_required_temperature_now value; the plan itself is unchanged |
| 1 | 64f3ef1feaaf7bc9 | D3-g35 | sysid.py:2223 | unresolved | low | hunt_hit=0 of 14087 evaluations; key case not reached | read by hand: the finder's boundary input does not land on the boundary on this host (macOS arm64 CPython/numpy): the probe's hunt found no hitting input, so neither arm moves here; solver floats do not reproduce across BLAS builds, so this is a non-reproduction to re-take on a Linux x86 box, not a  |
| 1 | d661d68f54982097 | D3-g35 | sysid.py:2223 | unresolved | low | key_tapped_tau=200.00000000000887 (not 200); key_completed baseline False = mutant False | read by hand: the finder's boundary input does not land on the boundary on this host (macOS arm64 CPython/numpy): the probe's hunt found no hitting input, so neither arm moves here; solver floats do not reproduce across BLAS builds, so this is a non-reproduction to re-take on a Linux x86 box, not a  |
| 1 | 4da9d281d4714565 | D3-g35 | sysid.py:2246 | unresolved | low | hunt_hit=0 of 28215 evaluations; key case not reached | read by hand: the finder's boundary input does not land on the boundary on this host (macOS arm64 CPython/numpy): the probe's hunt found no hitting input, so neither arm moves here; solver floats do not reproduce across BLAS builds, so this is a non-reproduction to re-take on a Linux x86 box, not a  |
| 5 | b2faf84904db389e | D3-g45 | thermal_model.py:677 | unresolved | low |  |  |
| 5 | 1b476993921016f9 | D3-g45 | thermal_model.py:852 | unresolved | low |  |  |
| 5 | ea888783bb621669 | D3-g45 | thermal_model.py:855 | unresolved | low |  |  |
| 5 | b098598faf0d87dc | D3-g45 | thermal_model.py:835 | unresolved | low |  |  |
| 5 | dd40fdb4edae4d79 | D3-g45 | thermal_model.py:2270 | unresolved | medium |  | severity: claimed medium, kept: not re-graded beyond reach in this stage |
| 5 | 19404e3632806509 | D3-g45 | thermal_model.py:2554 | unresolved | medium |  | severity: claimed medium, kept: not re-graded beyond reach in this stage |
| 5 | beeb068352333132 | D3-g45 | thermal_model.py:2573 | unresolved | low |  |  |
| 5 | ea9c4705de428b28 | D3-g45 | thermal_model.py:2576 | unresolved | low |  |  |
| 5 | 98853a541b6b5d6a | D3-g45 | thermal_model.py:2581 | unresolved | medium |  | severity: claimed medium, kept: not re-graded beyond reach in this stage |
| 5 | fdf5872fd576c405 | D3-g45 | thermal_model.py:2581 | unresolved | medium |  | severity: claimed medium, kept: not re-graded beyond reach in this stage |
| 5 | 39041ccf21eedba6 | D3-g45 | thermal_model.py:2583 | unresolved | medium |  | severity: claimed medium, kept: not re-graded beyond reach in this stage |

## All votes

| stage | key | box | site | vote | severity | V1 | V2 |
|---|---|---|---|---|---|---|---|
| 1 | fafb0d2c15e72efb | D3-g01 | coordinator.py:822 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('issues_after_3', ['1', '0']) | inconclusive by construction |
| 1 | 676e8bfb416ff635 | D3-g01 | coordinator.py:829 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('inprocess_solves_before_skip', ['3', '6']) | inconclusive by construction |
| 1 | 622996d751dca0c4 | D3-g01 | coordinator.py:1622 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('samples', ['1', '0']) | 1 of 1 moving arms read the mutant value |
| 1 | 0e6080e5385399cb | D3-g01 | coordinator.py:1624 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('samples', ['1', '0']) | 1 of 1 moving arms read the mutant value |
| 1 | 021dc21415f3229e | D3-g01 | coordinator.py:1651 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('reanchor_7pct', ['(True, 1.279005)', '(False, 1.2)']) | inconclusive by construction |
| 1 | 1165914e57f5bd08 | D3-g01 | coordinator.py:1796 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('cop_scale_outlier', ['1.05', '1.1']) | inconclusive by construction |
| 1 | ab918806fc8b4af6 | D3-g01 | coordinator.py:10331 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('zero_energy_lines', ['0 count []', "3 count ['dhw', 'space', 'spo | faithful by construction |
| 1 | db9b59ec36304943 | D3-g01 | coordinator.py:10331 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('zero_energy_lines', ['0 count []', "3 count ['dhw', 'space', 'spo | faithful by construction |
| 1 | cf7be12db1a662c4 | D3-g01 | coordinator.py:9613 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('price_shape00', ['1.3', '1.0']) | faithful by construction |
| 1 | 031dba68286ccfbf | D3-g01 | coordinator.py:9622 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('comfort_learned_weight', ['8.0', '5.0']) | faithful by construction |
| 1 | 22205dc8a4a6e79b | D3-g01 | coordinator.py:9628 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('defrost_factor00', ['0.8', '1.0']) | faithful by construction |
| 1 | 37e0face2a901e71 | D3-g01 | coordinator.py:7419 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('short_solar', ['[100.0, 101.0, 7.0, 0.0, 0.0, 0.0]', 'IndexError' | faithful by construction |
| 1 | 68c8ce175dcfa839 | D3-g01 | coordinator.py:7422 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('partial_cover_log', ['1', '0']) | faithful by construction |
| 1 | 20f57d1eea0a5a1d | D3-g01 | coordinator.py:4508 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('dhw_disabled_vvc', ["[('turn_on', 'switch.vvc')]", "[('turn_off', | faithful by construction |
| 1 | cd1d099ef87f3ab9 | D3-g02 | coordinator.py:4525 | verify | high | V1 3 arm pair(s) moved, null moved 0; e.g. ('step5_heat_only_4_7', ['turn_on', 'turn_off']) | faithful by construction |
| 1 | 473508040d23cc21 | D3-g02 | coordinator.py:4528 | verify | high | V1 3 arm pair(s) moved, null moved 0; e.g. ('step5_heat_only_4_7', ['turn_on', 'turn_off']) | faithful by construction |
| 1 | ad8a02e5c07428ab | D3-g02 | coordinator.py:4538 | verify | high | V1 2 arm pair(s) moved, null moved 0; e.g. ('upper_cold_room_warm', ['turn_on', 'turn_off']) | faithful by construction |
| 1 | b3a8cff2e5c0a8cc | D3-g02 | coordinator.py:5654 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dt_exact_0p15h_samples', ['1 count rate=0.4327056338738068 saves= | faithful by construction |
| 1 | 59027d3bdf2e7a0c | D3-g02 | coordinator.py:5656 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dt_exact_3h_samples', ['1 count rate=0.39946104468116317 saves=1' | faithful by construction |
| 1 | 2700e28d79c64bd8 | D3-g02 | coordinator.py:5665 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('end4_exact_3h_samples', ['1 count rate=0.4075927387094018 saves=1 | faithful by construction |
| 1 | 9d324a1dc7a6aa82 | D3-g02 | coordinator.py:5674 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('observed_eq_high_1h_samples', ['1 count rate=0.4513030054632706 s | faithful by construction |
| 1 | bb1abbfc58114a17 | D3-g02 | coordinator.py:5674 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('observed_eq_low_2h_samples', ['1 count rate=0.3167038634829969 sa | faithful by construction |
| 1 | 74dbcc2eae2c24f5 | D3-g02 | coordinator.py:5679 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('observed_eq_rate_1p6564106040767907_set_samples', ['1 count rate= | faithful by construction |
| 1 | 355c3d7dd36a1b90 | D3-g02 | coordinator.py:5782 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('delta6_exact_cool_scale', ['1.01 samples=1 cusum_stat=0.0 tripped | faithful by construction |
| 1 | ec4b6ee2ab420129 | D3-g03 | coordinator.py:5810 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('trip_saves', ['1 count log=1', '0 count log=0']) | faithful by construction |
| 1 | 16f7665306eebdf3 | D3-g03 | coordinator.py:8419 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('since_int', ['None', '12345']) | faithful by construction |
| 1 | 2ec5fda238265712 | D3-g03 | coordinator.py:9685 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('day_unhealthy_after_day2', ['None', "'indoor_temp stale'"]) | faithful by construction |
| 1 | c0ecc8e0b6b66ded | D3-g03 | coordinator.py:9695 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('clear_issue_calls', ["['delete'] rollback_latch=False alarmed=Fal | faithful by construction |
| 1 | ac6bedc70bb82ff7 | D3-g03 | coordinator.py:8265 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('manual_plan_published', ['True', 'False']) | faithful by construction |
| 1 | 3304e65ba361587f | D3-g03 | coordinator.py:4831 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('empty_views', ['True space_plan_keys=0', 'False space_plan_keys=5 | faithful by construction |
| 1 | a28fd1af46c39331 | D3-g03 | coordinator.py:4851 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('upper_published', ['0', '4']) | faithful by construction |
| 1 | 4498461fcf451835 | D3-g03 | coordinator.py:4945 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('valve_schedule', ['4 steps', 'None steps']) | faithful by construction |
| 1 | 79db73ec81b29f23 | D3-g03 | coordinator.py:9352 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('caps_p0.1', ['None', '[0.06, 0.06]']) | faithful by construction |
| 1 | 816e18d55f46f0e4 | D3-g03 | coordinator.py:9352 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('caps_p0.08', ['None', '[0.048, 0.048]']) | faithful by construction |
| 1 | 9c82d861621b8087 | D3-g03 | coordinator.py:9365 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('caps_tie', ['None', '[0.999999999, 0.999999999]']) | faithful by construction |
| 1 | e880fd3537006726 | D3-g03 | coordinator.py:5986 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('steady_writes', ['0', '3']) | faithful by construction |
| 1 | 134126ee4914191f | D3-g03 | coordinator.py:10561 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('score_tie', ['43.0', '40.0']) | faithful by construction |
| 1 | b7623a645f34e628 | D3-g03 | coordinator.py:10564 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('score_tie', ['40.0 free_streak=1.0', '43.0 free_streak=None']) | faithful by construction |
| 1 | 420bcb8597761025 | D3-g03 | coordinator.py:10855 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('commanded', ['50.06', '50.1']) | faithful by construction |
| 1 | 466c95cb8978ea1d | D3-g04 | coordinator.py:7733 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('inputs[None]', ['(0, None, 0)', '(1, None, 0)']) | faithful by construction |
| 1 | a7dd3153718e531b | D3-g04 | coordinator.py:9153 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['None', 'array[4] max=2e-09']) | faithful by construction |
| 1 | 7457d714cd44306c | D3-g04 | coordinator.py:9166 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['None', 'array[4] max=1e-09']) | faithful by construction |
| 1 | 6aeb83e5435c9cac | D3-g04 | coordinator.py:10428 | weaken | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('', ["{'month': '2026-11', 'kwh': 10.0, 'hourly_spot_sek': 12.0, ' | faithful by construction |
| 1 | d06a2d8e53342785 | D3-g04 | coordinator.py:10433 | weaken | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('', ["{'month': '2026-11', 'kwh': 10.0, 'hourly_spot_sek': 12.0, ' | faithful by construction |
| 1 | faf822994582adfc | D3-g04 | coordinator.py:4463 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('recommended', ['48', '56']) | faithful by construction |
| 1 | feed2751f4116bd1 | D3-g04 | coordinator.py:4464 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('recommended', ['48', '50']) | faithful by construction |
| 1 | 29bad645ca2c2438 | D3-g04 | coordinator.py:4471 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('recommended', ['48', '50']) | faithful by construction |
| 1 | 640a1a68b6c1eb23 | D3-g04 | coordinator.py:9846 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('ha_contract', ['(None, {}) for None', 'raises AttributeError for  | faithful by construction |
| 1 | c087dc286eeff014 | D3-g05 | coordinator.py:5083 | verify | medium | V1 7 arm pair(s) moved, null moved 0; e.g. ('interval60_max_sample_hours', ['1.5', '1.0']) | faithful by construction |
| 1 | 218ac218da41d87d | D3-g05 | coordinator.py:5156 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('flue_30.0C', ['False', 'True']) | faithful by construction |
| 1 | bcf290164a0edeeb | D3-g05 | coordinator.py:5157 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('stale_probe_4_cycles', ['None baseline_warnings=1', 'None']) | faithful by construction |
| 1 | 375376c4733a1a51 | D3-g05 | coordinator.py:5174 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('stale_probe_4_cycles', ['None baseline_warnings=1', 'None']) | faithful by construction |
| 1 | 2699efc070f5d4e3 | D3-g05 | coordinator.py:5176 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('implausible_minus127C', ['None', 'True']) | faithful by construction |
| 1 | d05457b7adf4d691 | D3-g05 | coordinator.py:7056 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | d943cc9f7670a834 | D3-g05 | coordinator.py:7069 | weaken | medium | V1 0 arm pair(s) moved, null moved 1; e.g. None | faithful by construction |
| 1 | d915157ffe509e58 | D3-g06 | coordinator.py:10231 | verify | low | V1 5 arm pair(s) moved, null moved 0; e.g. ('len4', ['[]', 'raisesIndexError']) | faithful by construction |
| 1 | dff127b334682936 | D3-g06 | coordinator.py:9327 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('cop0', ['{}', '{-4:[0.0,1]}']) | faithful by construction |
| 1 | 59337f7f63497f21 | D3-g06 | coordinator.py:9437 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dt1e-6', ['None', '0.9']) | faithful by construction |
| 1 | 4542deee22df985f | D3-g06 | coordinator.py:9440 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('cap0', ['None', '0.3']) | faithful by construction |
| 1 | 8e729260c34e2e3b | D3-g06 | coordinator.py:9440 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('cap1e-6', ['None', '0.3']) | faithful by construction |
| 1 | e347b6890486dd0d | D3-g06 | coordinator.py:9447 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('res_nan', ['0.3', 'nan']) | faithful by construction |
| 1 | 72fbe692d30d275e | D3-g06 | coordinator.py:9452 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('g0_0', ['0.1', '0.0']) | faithful by construction |
| 1 | 2e4d4a89570a1b24 | D3-g06 | coordinator.py:9383 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('irr150', ['(1.0,1.0,0.0147,0.16)', '(0.0,1.0,0.0,0.0)']) | faithful by construction |
| 1 | 30fcf9ba50130ea2 | D3-g06 | coordinator.py:9386 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dt1e-6', ['(0.0,1.0,0.0,0.0)', '(1.0,1.0,0.0392,80000.0)']) | faithful by construction |
| 1 | 89a3d25e2425b8e0 | D3-g06 | coordinator.py:9386 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('cap0', ['(0.0,1.0,0.0,0.0)', '(1.0,1.0,0.0392,0.0)']) | faithful by construction |
| 1 | efa2c19c51831a68 | D3-g06 | coordinator.py:9386 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('cap1e-6', ['(0.0,1.0,0.0,0.0)', '(1.0,1.0,0.0392,0.0)']) | faithful by construction |
| 1 | 205d200980d58e9e | D3-g06 | coordinator.py:9390 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('x1e-6', ['(0.0,1.0,0.0,0.0)', '(1.0,1.0,2e-08,0.16)']) | faithful by construction |
| 1 | 96fe4cecaa16f997 | D3-g06 | coordinator.py:9390 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('x0', ['(0.0,1.0,0.0,0.0)', '(1.0,1.0,0.0,0.16)']) | faithful by construction |
| 1 | 1a24365a55bfb2c7 | D3-g06 | coordinator.py:9402 | verify | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('n1', ['(1.0,1.0,0.0392,0.16)', '(1.0,2.0,0.0392,0.16)']) | faithful by construction |
| 1 | d3cad40ffce9b765 | D3-g07 | coordinator.py:9402 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('scale_at_min', ['2.000000', '1.000000']) | faithful by construction |
| 1 | e163f6fbc359cd4c | D3-g07 | coordinator.py:9402 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('scale_tie', ['1.000000', '2.000000']) | faithful by construction |
| 1 | f0146f6f4901ec82 | D3-g07 | coordinator.py:7491 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('humidity_mean', ['95.0 %', '85.0 %']) | faithful by construction |
| 1 | 4410da4e8eb84cb8 | D3-g07 | coordinator.py:8838 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('hold', ['0', '1']) | faithful by construction |
| 1 | 7ec91efc2c6deffd | D3-g07 | coordinator.py:8838 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('hold', ['0', '1']) | faithful by construction |
| 1 | f11665aaedbf2550 | D3-g07 | coordinator.py:8838 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('hold', ['1', '0']) | faithful by construction |
| 1 | 9b72b944ac12fa25 | D3-g07 | coordinator.py:8842 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('hold', ['1', '0']) | faithful by construction |
| 1 | fd1cc23d380739ba | D3-g07 | coordinator.py:8847 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('hold', ['0', '1']) | faithful by construction |
| 1 | c20f346300d7efc1 | D3-g07 | coordinator.py:9292 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('margin', ['2.0', '0.0']) | faithful by construction |
| 1 | 60f673da42f9d671 | D3-g07 | coordinator.py:9294 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('margin', ['2.0', '0.0']) | faithful by construction |
| 1 | b6ac2d53028d45a3 | D3-g07 | coordinator.py:5049 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('space_kw', ['-1', '0']) | faithful by construction |
| 1 | 1ee0ec8960fb9a66 | D3-g07 | coordinator.py:5104 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('rise_dhw', ['71.659 degC/h', '409.483 degC/h']) | faithful by construction |
| 1 | 15456e64946920b5 | D3-g08 | coordinator.py:5108 | verify | low | V1 12 arm pair(s) moved, null moved 0; e.g. ('dhw_cap=0.0', ['0.0_baseline=None', '0.0_mutant=raises ZeroDivis | faithful by construction |
| 1 | ceee24404849933e | D3-g08 | coordinator.py:9010 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('fresh_error', ["((('candidate_fuse_a', 20),", "((), '2026-07-09T1 | faithful by construction |
| 1 | 341d807c3a3d361d | D3-g08 | coordinator.py:9030 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | d5ce59f9731dfc83 | D3-g08 | coordinator.py:8176 | verify | low | V1 5 arm pair(s) moved, null moved 0; e.g. ('zero_slot', ["price_ratio 0.5 reason 'Set to the'", "price_ratio  | faithful by construction |
| 1 | 7398de952c9d1510 | D3-g08 | coordinator.py:10603 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('step=15.0', ['15.0_baseline=kwh 3.0 lines 0', '15.0_mutant=kwh 3. | faithful by construction |
| 1 | 21a2563e1beb213f | D3-g08 | coordinator.py:9486 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('n_then_drop', ['stat 0.323333333 baseline_cop 2.98 count 21 issue | faithful by construction |
| 1 | 509893a173fa6a29 | D3-g08 | coordinator.py:9486 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | cd6eee1c9c175e5f | D3-g08 | coordinator.py:9500 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('n_then_drop', ['stat 0.323333333 baseline_cop 2.98 count 21 issue | faithful by construction |
| 1 | b283779946540c3d | D3-g08 | coordinator.py:8785 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 25fb4eaf35cfdda5 | D3-g08 | coordinator.py:8806 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('factor0_peak3_nofuse', ['(((5.0, inf),', '(((0.0, 3.0),']) | faithful by construction |
| 1 | 9cdf54d2309cfcc8 | D3-g09 | coordinator.py:9038 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('active_at_tie', ['0', '1']) | faithful by construction |
| 1 | d8101520588009d9 | D3-g09 | coordinator.py:8900 | verify | high | V1 1 arm pair(s) moved, null moved 0; e.g. ('available_offseason', ['0 limit_kw=None limit_source=None', "1 li | faithful by construction |
| 1 | 3d83c32f185cf411 | D3-g09 | coordinator.py:9819 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('summary_keys_peak0', ['0 surplus_sum_kw=0.0000', '5 surplus_sum_k | faithful by construction |
| 1 | 002980a15ae8b9a9 | D3-g09 | coordinator.py:9827 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('surplus0_meter', ['2.6000 kW  surplus_sum=11.3200 forecast_produc | faithful by construction |
| 1 | 1785780ac9dd1b18 | D3-g09 | coordinator.py:9836 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('measured_production_kw_meter', ['3.0 stored_summary_has_key=True' | faithful by construction |
| 1 | 326b26f53972df61 | D3-g09 | coordinator.py:9810 | verify | high | V1 2 arm pair(s) moved, null moved 0; e.g. ('ha_none', ['surplus_sum=8.7200', "raised AttributeError: 'NoneTyp | faithful by construction |
| 1 | 104db258fed59c2d | D3-g09 | coordinator.py:11000 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('calls_tie', ['0 evidence_delta=0.0', '1 evidence_delta=-0.007292' | faithful by construction |
| 1 | 8daaf4fcaf8cd897 | D3-g09 | coordinator.py:11002 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('calls_tie', ['1 evidence_delta=-0.007292', '0 evidence_delta=0.0' | faithful by construction |
| 1 | 3cfe39778305daba | D3-g09 | coordinator.py:11008 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('calls_tie', ['1 evidence_delta=-0.007292 heating_kwh=1.0', '0 evi | faithful by construction |
| 1 | 425a9196b86265d0 | D3-g09 | coordinator.py:11057 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('offloop_jobs_rooms_idle', ['0', '1']) | faithful by construction |
| 1 | 0c99189b7639f1bd | D3-g09 | coordinator.py:9980 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('calls_tie_i10', ['1', '0']) | faithful by construction |
| 1 | df697cc04154fbdd | D3-g09 | coordinator.py:9980 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('calls_tie_i10', ['1', '0']) | faithful by construction |
| 1 | 205660ee362d1a07 | D3-g10 | coordinator.py:7861 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('two_tank', ['2 keys wood=55.0', '0 keys wood=None']) | faithful by construction |
| 1 | 34c20aac32a34344 | D3-g10 | coordinator.py:9273 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('margin_neg_bias0', ['(bias,comfortable_days,resets)(0.0, 5, 0)',  | faithful by construction |
| 1 | c7054b2e59c82141 | D3-g10 | coordinator.py:9273 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('margin_zero_bias_neg', ['(bias,comfortable_days,resets)(0.0, 0, 1 | faithful by construction |
| 1 | ff56936f15fd4675 | D3-g10 | coordinator.py:9273 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('margin_pos_bias_neg', ['(bias,comfortable_days,resets)(-1.0, 5, 0 | faithful by construction |
| 1 | 349b2e117d076731 | D3-g10 | coordinator.py:6747 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('wood_logs', ['(warnings,infos,format_errors,temps)(1, 2, 0,', '(w | faithful by construction |
| 1 | cdd17526ebbf2a93 | D3-g10 | coordinator.py:6747 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('wood_logs', ['(warnings,infos,format_errors,temps)(1, 2, 0,', '(w | faithful by construction |
| 1 | 8ab42c4ab9755537 | D3-g10 | coordinator.py:6752 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('wood_logs', ['(warnings,infos,format_errors,temps)(1, 2, 0,', '(w | faithful by construction |
| 1 | e689dc488b493c6b | D3-g10 | coordinator.py:6752 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('wood_logs', ['(warnings,infos,format_errors,temps)(1, 2, 0,', '(w | faithful by construction |
| 1 | f2a191b48718e088 | D3-g10 | coordinator.py:5234 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('active', ['(debugs,flag)(1, False)', '(debugs,flag)(0, False)']) | faithful by construction |
| 1 | b871ff0486182e3e | D3-g10 | coordinator.py:7549 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('gap12h_rate0.2', ['(accum_cm,damped)(1.2, False)', '(accum_cm,dam | faithful by construction |
| 1 | 813cb7aecbd78f98 | D3-g10 | coordinator.py:7551 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie', ['(accum_cm,damped)(2.0, True)', '(accum_cm,damped)(2.0, Fa | faithful by construction |
| 1 | aa6b718c979bf831 | D3-g10 | coordinator.py:7118 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('weather', ['(warnings,infos,debugs,outage_cycles,stale)(1, 1, 1,  | faithful by construction |
| 1 | 18fe89552892dc4b | D3-g10 | coordinator.py:7130 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('weather', ['(warnings,infos,debugs,outage_cycles,stale)(1, 1, 1,  | faithful by construction |
| 1 | 65175bb211f70f26 | D3-g10 | coordinator.py:10678 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('none', ['(infos,report,refreshes)(1, None, 1)', '(infos,report,re | faithful by construction |
| 1 | 61e748f094f2daa8 | D3-g11 | coordinator.py:6454 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('issues_left_after_recovery_3_failures', ['0', '1']) | faithful by construction |
| 1 | a33188790c5affad | D3-g11 | coordinator.py:6454 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('issues_left_after_recovery_3_failures', ['0', '1']) | faithful by construction |
| 1 | 94285425a1bc856a | D3-g11 | coordinator.py:6615 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('task_done', ['True', 'False']) | faithful by construction |
| 1 | 69b933a6a720006b | D3-g11 | coordinator.py:6620 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('warnings', ['1', '0']) | faithful by construction |
| 1 | 9dcd374ac007dfc9 | D3-g11 | coordinator.py:11271 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('no_cap_breach_key', ['0', '1']) | faithful by construction |
| 1 | 4fd094e9727818b3 | D3-g11 | coordinator.py:2907 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('age_at_limit', ['12.0', 'None']) | faithful by construction |
| 1 | e2b030e0716d126c | D3-g11 | coordinator.py:2910 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('inlet_35', ['35.0', 'None']) | faithful by construction |
| 1 | 738102c9ed0f89af | D3-g11 | coordinator.py:984 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('outdoor_nan', ['ok samples=0', 'TypeError']) | faithful by construction |
| 1 | 372a4f4fcc8de86f | D3-g11 | coordinator.py:490 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('zero_value', ['0', '1']) | faithful by construction |
| 1 | 6f5898d327366799 | D3-g11 | coordinator.py:3101 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('precip_1e-9_snow', ['1.0', '0.0']) | faithful by construction |
| 1 | 7ffebcb567a4242e | D3-g12 | coordinator.py:2540 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('seed_at_900s', ['42.0', 'None']) | faithful by construction |
| 1 | 845155d368e8b524 | D3-g12 | coordinator.py:900 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('gap_90.0min', ['None', "'Update gap of 90 minutes'"]) | faithful by construction |
| 1 | 3e68dcd55f9567e5 | D3-g12 | coordinator.py:3013 | verify | medium | V1 6 arm pair(s) moved, null moved 0; e.g. ('temperature_lo_-70', ['-70.0', 'None']) | faithful by construction |
| 1 | 88ecd932bc81efec | D3-g12 | coordinator.py:3013 | verify | medium | V1 6 arm pair(s) moved, null moved 0; e.g. ('temperature_hi_70', ['70.0', 'None']) | faithful by construction |
| 1 | 4403a4c7bec83d8f | D3-g12 | coordinator.py:3417 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('unset_falsy_lookups', ['0', '1']) | faithful by construction |
| 1 | 89bec0a0291b4756 | D3-g12 | coordinator.py:467 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('accepted_2^31', ['1', '0']) | faithful by construction |
| 1 | b028ad9d6c702965 | D3-g12 | coordinator.py:2360 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('previous_plan_warm_plan_len', ['96', '0']) | faithful by construction |
| 1 | 3b9eddc7ba9a7488 | D3-g12 | defrost.py:124 | verify | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('ratio0.8_factor_after_1', ['0.990000', '0.980000']) | 3 of 3 moving arms read the mutant value |
| 1 | d1197dfed14a6927 | D3-g12 | defrost.py:313 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('tie_same_count_decide', ["('measured', 0.9375, 5)", "('inferred', | faithful by construction |
| 1 | 3e3fbb5fcbbe9bcc | D3-g12 | defrost.py:566 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('v1_store_upgrade_log_records', ['1', '0']) | faithful by construction |
| 1 | 1ba9abbe8e702464 | D3-g12 | defrost.py:537 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('duty1.0_restored_duty_count', ['12', '0']) | faithful by construction |
| 1 | 4aac8e694ddc5dfe | D3-g12 | defrost.py:537 | weaken | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('duty0.0_restored_duty_count', ['12', '0']) | faithful by construction |
| 1 | 5366f1e6254f603c | D3-g12 | defrost.py:392 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('ratio0.0_count', ['0', '1']) | faithful by construction |
| 1 | efb33eb6212be24e | D3-g12 | defrost.py:392 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('ratio3.0_count', ['1', '0']) | faithful by construction |
| 1 | 0e3569fef6b39497 | D3-g12 | defrost.py:434 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('no_inferred_handover_logs', ['0', '1']) | faithful by construction |
| 1 | 24d9995ccee4252e | D3-g13 | defrost.py:642 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('rows_with_duty', ['0', '1']) | faithful by construction |
| 1 | 8297234e122897ff | D3-g13 | defrost.py:802 | verify | low | V1 7 arm pair(s) moved, null moved 0; e.g. ('on_then_peek', ['(1.0, 1, True, 600.0)', '(0.0, 1, True, 600.0)'] | faithful by construction |
| 1 | 681130c48add1573 | D3-g13 | defrost.py:804 | verify | low | V1 7 arm pair(s) moved, null moved 0; e.g. ('on_then_peek', ['(1.0, 1, True, 600.0)', '(0.0, 1, True, 600.0)'] | faithful by construction |
| 1 | c61a89f42607c92b | D3-g13 | defrost.py:169 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('bucket_temp_at_top_edge', ['5', '0']) | faithful by construction |
| 1 | df4de55e12588fdf | D3-g13 | dhw_planner.py:2055 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('slot_at_1e-06_tank_room', ['1e-06', '0.6']) | faithful by construction |
| 1 | 3685cdbd27c1680f | D3-g14 | dhw_planner.py:2076 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_step0_kw', ['3.000000', '5.000000']) | faithful by construction |
| 1 | 1c0e818b4bb24fcd | D3-g14 | dhw_planner.py:2106 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_plan', ['[0,3,3,0,0,3,0.6,0]', '[0,3,3,-1,0,5,0.6,-1]']) | faithful by construction |
| 1 | 0b51e1d1975513aa | D3-g14 | dhw_planner.py:1645 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('short_pins_returns_plan', ['1', '0']) | faithful by construction |
| 1 | 0e3fc2bc64c2bf63 | D3-g14 | dhw_planner.py:1649 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_kw_at_pin_0p5', ['0.600000', '0.000000']) | faithful by construction |
| 1 | b25e80c59b31c20d | D3-g14 | dhw_planner.py:1184 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('_shortfall_c', ['0.2711', '6.3719']) | faithful by construction |
| 1 | 6999e2dab9790b53 | D3-g14 | dhw_planner.py:1187 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('pin0p5_kwh', ['4.5899', '4.6043']) | faithful by construction |
| 1 | cd7bc939ea82fecd | D3-g14 | dhw_planner.py:1188 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('_shortfall_c', ['0.2711', '6.3719']) | faithful by construction |
| 1 | de02e0a048abc451 | D3-g14 | dhw_planner.py:1190 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('suppressed_steps', ['0', '1']) | faithful by construction |
| 1 | 7f026b4dd7d44269 | D3-g14 | dhw_planner.py:1214 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('cr2_kwh', ['7.5261', '7.5303']) | faithful by construction |
| 1 | a1576c7241b67401 | D3-g14 | dhw_planner.py:1342 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('suppressed', ['1', '0']) | faithful by construction |
| 1 | 8fa714bbb756e11e | D3-g14 | dhw_planner.py:1343 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('suppressed', ['1', '0']) | faithful by construction |
| 1 | a1ebeff0870dfa76 | D3-g15 | dhw_planner.py:784 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('tie_runup_steps', ['6', '0']) | faithful by construction |
| 1 | f1549576a94b99be | D3-g15 | dhw_planner.py:784 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('runup_max', ['0.0000', '139.1276']) | faithful by construction |
| 1 | 7cd9b966a3bd0008 | D3-g15 | dhw_planner.py:793 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('tie_runup_steps', ['2', '5']) | faithful by construction |
| 1 | 31c1881164f2dcdf | D3-g15 | dhw_planner.py:626 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie_step', ['0', '1']) | faithful by construction |
| 1 | 7640e80a994db479 | D3-g15 | dhw_planner.py:628 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('edge_due', ['False step=None', 'True step=1']) | faithful by construction |
| 1 | 35d61c87783ebe66 | D3-g16 | dhw_planner.py:680 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('cycle_placed', ['0', '1']) | faithful by construction |
| 1 | 8fc6a207d6600867 | D3-g16 | dhw_planner.py:470 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('step0_price', ['2.000000000 per-kWh', '1.999999333 per-kWh']) | faithful by construction |
| 1 | 72882f2ac25c19b1 | D3-g16 | dhw_planner.py:474 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('step0_price', ['2.000000 per-kWh', '3.333333 per-kWh']) | faithful by construction |
| 1 | a21e5757eab163a7 | D3-g16 | dhw_planner.py:2140 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('raise_fits', ['1', '0']) | faithful by construction |
| 1 | 41000bf52dbaa1ad | D3-g16 | dhw_planner.py:547 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('window_hours', ['10.0 h', '13.0 h']) | faithful by construction |
| 1 | 88d911d796fdd71d | D3-g16 | dhw_planner.py:548 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('window_hours', ['16.0 h', '24.0 h']) | faithful by construction |
| 1 | 3ec31b99309ca722 | D3-g16 | dhw_planner.py:549 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('window_hours', ['24.0 h', 'nan h']) | faithful by construction |
| 1 | 84eb14f49ff66736 | D3-g16 | dhw_planner.py:2232 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('first_charge_step', ['10', '0']) | faithful by construction |
| 1 | 7da9151a6a79c43e | D3-g16 | dhw_planner.py:2234 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('dhw_kw_sum', ['1.9870', '0.0000']) | faithful by construction |
| 1 | 50ae25437a296deb | D3-g16 | dhw_planner.py:2280 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('step0_kw', ['0.0000', '0.1000']) | faithful by construction |
| 1 | 61862d35b6b2885d | D3-g17 | dhw_planner.py:2307 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('plan', ['[0,0,0,0,0,0,0,0,3,0,0,0]', '[0,0,0,0,0,0,0,0,3.5,0,0,0] | faithful by construction |
| 1 | 5b123e9e5b76ebc3 | D3-g17 | dhw_planner.py:2227 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('plan', ['[0,0,0,0,0,0,0,2.999999,0,0,0.202506121,0]', '[0,0,0,0,0 | faithful by construction |
| 1 | 4f1f941124291aeb | D3-g17 | dhw_planner.py:2228 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('plan', ['[0,0,0,0,0,0,0,0,1.13391471,2.03671589,0,0]', '[0,0,0,0. | faithful by construction |
| 1 | c1d6f40c74ee74ad | D3-g17 | dhw_planner.py:1510 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('decay0_warnings', ['0', '1']) | faithful by construction |
| 1 | b1a8d3056bf42597 | D3-g17 | dhw_planner.py:1527 | weaken | nit | differing_pmax_nonpos=120/120 (max_delta 3 kW) but differing_pmax_pos=0/120; null 0/60 | faithful by construction |
| 1 | ddf4602569b157b1 | D3-g17 | dhw_planner.py:1529 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('plan', ['[1e-06,0,0,1.31032673,0,0]', '[1.37938921,0,0,0,0,0]']) | faithful by construction |
| 1 | 247372989ae65baa | D3-g17 | dhw_planner.py:1535 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dt0', ['None', 'ZeroDivisionError']) | faithful by construction |
| 1 | b1074e70396100d8 | D3-g17 | dhw_planner.py:1538 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('plan', ['[1.75073672,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]', '[0,0,0,0,0 | faithful by construction |
| 1 | b7a6f145165338bf | D3-g17 | dhw_planner.py:1606 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('nan_price', ['None', 'UnboundLocalError']) | faithful by construction |
| 1 | 2074f3eefe8521aa | D3-g17 | dhw_planner.py:1608 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('status1', ['None', 'plan']) | faithful by construction |
| 1 | 64576dd552491452 | D3-g18 | dhw_planner.py:1627 | verify | low | V1 every finder-stated value reproduced (6 of 6); baseline plan returned after the first pass when it is alrea | faithful by construction |
| 1 | 91617fb42e33ebdf | D3-g18 | dhw_planner.py:1800 | verify | low | V1 every finder-stated value reproduced (8 of 8); baseline one-decimal start 0.1 K under the ceiling (step 0 t | faithful by construction |
| 1 | 936bcb2da6441e86 | D3-g18 | dhw_planner.py:1893 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('shortfall_ksteps', ['57165.329', '58050.843']) | faithful by construction |
| 1 | 2aa0f17a216035ee | D3-g18 | flow_lift.py:51 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('bias', ['3.000000', '3.666667']) | 1 of 1 moving arms read the mutant value |
| 1 | 9297f123a6265555 | D3-g18 | grid_fee.py:483 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('warnings', ['0', '3']) | faithful by construction |
| 1 | 911f3cf5172ffc44 | D3-g19 | grid_fee.py:496 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('stale_row', ['None', 'dict']) | faithful by construction |
| 1 | b5f0a73275608684 | D3-g19 | grid_fee.py:360 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('label', ['fixed', 'entity']) | faithful by construction |
| 1 | 68cc141bf2c3493a | D3-g19 | grid_fee.py:388 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('label', ['fixed', 'entity']) | faithful by construction |
| 1 | 2043855ef5cf151d | D3-g19 | grid_fee.py:219 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('parse_none', ['[]', 'GridFeeError']) | faithful by construction |
| 1 | eee37674711fa45f | D3-g19 | optimizer.py:2006 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('weights', ['[1.0, 0.7333, 0.4667, 0.2]', '[1.0, 0.8344, 0.2, 0.2] | faithful by construction |
| 1 | 23b144fb9583c5c7 | D3-g19 | optimizer.py:2156 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('fraction', ['0.6667', '0.9565']) | faithful by construction |
| 1 | 68ef00f470ecea8d | D3-g19 | optimizer.py:2385 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('release_calls', ['4', '7']) | faithful by construction |
| 1 | be95c184bf4746ff | D3-g19 | optimizer.py:4211 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('pre_heat_urgency', ['0.5', '0.0']) | faithful by construction |
| 1 | e53563e772b70dbc | D3-g19 | optimizer.py:4229 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('peaks', ['0', '1']) | faithful by construction |
| 1 | 24ef8e54dad20484 | D3-g19 | optimizer.py:4249 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('solar_reduction', ['1.0', '0.6']) | faithful by construction |
| 1 | 7f048d7823b17826 | D3-g19 | optimizer.py:4250 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('solar_reduction', ['0.8824', '0.6000']) | faithful by construction |
| 1 | 4c7e296370fc452d | D3-g19 | optimizer.py:4271 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('rain_anticipation', ['1.0', '1.0075']) | faithful by construction |
| 1 | 9644a454ac8f288b | D3-g19 | optimizer.py:4272 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('rain_anticipation', ['1.1500', '1.3000']) | faithful by construction |
| 1 | d800d2857a698d22 | D3-g20 | optimizer.py:3405 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie_weight0', ['1.0', '0.85']) | faithful by construction |
| 1 | 176e4dd6d5aec097 | D3-g20 | optimizer.py:3408 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie_weight0', ['1.0', '1.1']) | faithful by construction |
| 1 | c40e66fc9831672f | D3-g20 | optimizer.py:6069 | verify | medium | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 7add4cd79387ec24 | D3-g20 | optimizer.py:6091 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | bf2229e3f179f4b6 | D3-g20 | optimizer.py:6097 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 47430bf93e309e76 | D3-g20 | optimizer.py:4766 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 3652dbb5880d62c8 | D3-g20 | optimizer.py:3969 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | b1926550efd8eac4 | D3-g20 | optimizer.py:3969 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | fd57e13959b23a4c | D3-g21 | optimizer.py:3997 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie', ['original', 'replanned']) | faithful by construction |
| 1 | ad01ae06d7ea84ec | D3-g21 | optimizer.py:5054 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('nearflat', ['None', 'array:23,23,19,19,19,19,23,23']) | faithful by construction |
| 1 | cb58757b91fa48c4 | D3-g21 | optimizer.py:5054 | verify | low | V1 5 arm pair(s) moved, null moved 0; e.g. ('tie', ['None', 'array:23,23,19,19,19,23,23,23']) | faithful by construction |
| 1 | 00298af0aa9d1903 | D3-g21 | optimizer.py:5074 | verify | medium | V1 4 arm pair(s) moved, null moved 0; e.g. ('nohold', ['None', 'array:23,23,23,23,23,23,23,23']) | faithful by construction |
| 1 | a4f4c88e7480a514 | D3-g21 | optimizer.py:4033 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | be3a3a75280c7b7e | D3-g21 | optimizer.py:5016 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('short', ['array:1,0,nan,nan', 'raise:ValueError']) | faithful by construction |
| 1 | deb281264473bdd6 | D3-g21 | optimizer.py:5902 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dhw_active_steps_logged', ['0', '22']) | faithful by construction |
| 1 | a66e107749d0ae11 | D3-g21 | optimizer.py:5945 | weaken | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('required_now', ['55.0', '20.0']) | faithful by construction |
| 1 | 4e5a67b907d13871 | D3-g21 | optimizer.py:5956 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dhw_planned_heating_hours', ['0', '22']) | faithful by construction |
| 1 | ed5e3ec5b879ed90 | D3-g21 | optimizer.py:5962 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dhw_preheat_hours', ['0.0', '13.0']) | faithful by construction |
| 1 | 6309f3e4a0a6c45f | D3-g21 | optimizer.py:5283 | verify | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('pin_on_power_min0', ['0.1', '0.0']) | faithful by construction |
| 1 | ef9a378b671791ca | D3-g22 | optimizer.py:6504 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('tau_0.01h', ['[-19.6, -19.6, -19.6, -19.6, 20.0, 20.0, 20.0, 20.0 | faithful by construction |
| 1 | 7da20bf51cc217e6 | D3-g22 | optimizer.py:4917 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('tank60', ['0.0', '-1.394']) | faithful by construction |
| 1 | 8ef1027c9e221b64 | D3-g23 | optimizer.py:5229 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('direct_half_pin_release', ['([],[])', '([0],[])']) | faithful by construction |
| 1 | ce686724ef107650 | D3-g23 | optimizer.py:5229 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('direct_on_pin_at_floor_release', ['([],[])', '([0],[])']) | faithful by construction |
| 1 | 8fd14c249b86abf7 | D3-g23 | optimizer.py:5234 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('direct_off_step_at_floor_plus_0.1_release', ['([0],[])', '([],[]) | faithful by construction |
| 1 | 0120a5a672990611 | D3-g23 | optimizer.py:5235 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('direct_tie_release', ['([0],[])', '([],[])']) | faithful by construction |
| 1 | 0ecb763c4bcb0828 | D3-g23 | optimizer.py:5237 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('direct_tie_release', ['([],[])', '([0],[])']) | faithful by construction |
| 1 | bc3a42f14c903439 | D3-g23 | optimizer.py:5250 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('direct_tie_release', ['([],[])', '([],[0])']) | faithful by construction |
| 1 | 856aa341a89a6ab0 | D3-g23 | optimizer.py:5211 | verify | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('released_space', ['[0]', '[]']) | faithful by construction |
| 1 | 5ce83ed87c36b9a5 | D3-g23 | optimizer.py:5213 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('direct_half_pin_release', ['([0],[])', '([],[])']) | faithful by construction |
| 1 | fe3e41de6bdc640a | D3-g23 | optimizer.py:5213 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('released_space', ['[0,1]', '[]']) | faithful by construction |
| 1 | 70791cdb98f8ddd7 | D3-g23 | optimizer.py:6027 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('buffer_cap_initial60', ['60.000', '35.000']) | faithful by construction |
| 1 | 7516dd3d9e66d3ef | D3-g23 | optimizer.py:6029 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('buffer_cap_initial60', ['60.000', '35.000']) | faithful by construction |
| 1 | ce5b92d704397d85 | D3-g24 | optimizer.py:4717 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | aab0b73e229ad900 | D3-g24 | optimizer.py:4720 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 56de38e47369b2b7 | D3-g24 | optimizer.py:5123 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | df066a5f3f3d3e0f | D3-g24 | optimizer.py:5139 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | bbcded8a73c6a2f1 | D3-g24 | optimizer.py:5145 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | f3126cd40dc76143 | D3-g25 | optimizer.py:6565 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['mode=normal,power=2.0,setpoint=21.0', 'raised:IndexErr | faithful by construction |
| 1 | f58c6d034aa31e46 | D3-g25 | optimizer.py:6566 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['mode=normal,power=2.0,setpoint=21.0', 'mode=idle,power | faithful by construction |
| 1 | 6aec51dc6f670787 | D3-g25 | optimizer.py:6584 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['displace_value=0.0', 'raised:IndexError']) | faithful by construction |
| 1 | b2e075c0da35240d | D3-g25 | optimizer.py:6602 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ["'normal'", "'eco'"]) | faithful by construction |
| 1 | 57f696b2f988d5a9 | D3-g25 | optimizer.py:6604 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ["'pre_heat'", "'normal'"]) | faithful by construction |
| 1 | b143b01c4ea02159 | D3-g25 | optimizer.py:6604 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ["'normal'", "'pre_heat'"]) | faithful by construction |
| 1 | a581feadd69c6c42 | D3-g25 | optimizer.py:6606 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ["'pre_heat'", "'boost'"]) | faithful by construction |
| 1 | e96ae75a1f1f213e | D3-g25 | optimizer.py:6606 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ["'boost'", "'pre_heat'"]) | faithful by construction |
| 1 | d0de1c16101369f5 | D3-g25 | optimizer.py:6632 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['valve_target=absent', 'raised:IndexError']) | faithful by construction |
| 1 | f8b7db7badd35158 | D3-g25 | optimizer.py:6638 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['upper_setpoint=absent', 'raised:IndexError']) | faithful by construction |
| 1 | cd766b55c44ca3ee | D3-g25 | optimizer.py:6640 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['lower_setpoint=absent', 'raised:IndexError']) | faithful by construction |
| 1 | 724471c27310230f | D3-g25 | optimizer.py:6644 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['solar_gain_kw=absent', 'raised:IndexError']) | faithful by construction |
| 1 | 970ed4d74c36caa1 | D3-g25 | optimizer.py:6648 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['dhw_power=absent', 'raised:IndexError']) | faithful by construction |
| 1 | 1d11f24436471959 | D3-g25 | optimizer.py:6651 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['False', 'True']) | faithful by construction |
| 1 | e16ae8a6fd6cea40 | D3-g25 | optimizer.py:6653 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['dhw_temperature=absent', 'raised:IndexError']) | faithful by construction |
| 1 | 119b25afdd5d4988 | D3-g25 | optimizer.py:6655 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_value', ['55.0', "'absent'"]) | faithful by construction |
| 1 | 35d104f30f878131 | D3-g26 | optimizer.py:6661 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('predictive_keys', ["3 count  {'solar_reduction_factor': np.float6 | faithful by construction |
| 1 | f56e3474baa75dc5 | D3-g26 | optimizer.py:4528 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('released_space', ['4', '28']) | faithful by construction |
| 1 | 1721e50b7537a426 | D3-g26 | optimizer.py:4532 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('released_dhw', ['48', '56']) | faithful by construction |
| 1 | 2693e4fc04518cbf | D3-g26 | optimizer.py:4560 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('released', ['88', '96']) | faithful by construction |
| 1 | 977021e3b3964277 | D3-g26 | optimizer.py:2782 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('pair_holiday_wed', ['(20.0, 17.0, 8, 20)', '(20.0, 19.5, 8, 20)'] | faithful by construction |
| 1 | 10de422e4e1024a7 | D3-g26 | optimizer.py:2786 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('pair_holiday_wed', ['(20.0, 17.0, 8, 20)', '(20.0, 17.0, 8, 22)'] | faithful by construction |
| 1 | e4affa9b9b540588 | D3-g26 | optimizer.py:2788 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('pair_holiday_sat', ['(20.0, 17.0, 8, 20)', '(22.0, 20.0, 9, 23)'] | probe rc 1 with the mutant on disk (Type |
| 1 | 0fcdd4bdabc205ea | D3-g26 | optimizer.py:2794 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('pair_plain_sat', ['(22.0, 20.0, 9, 23)', '(22.0, 20.0, 7, 23)']) | faithful by construction |
| 1 | 8365c2592bae9886 | D3-g26 | optimizer.py:2796 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('pair_plain_sat', ['(22.0, 20.0, 9, 23)', '(22.0, 20.0, 9, 22)']) | faithful by construction |
| 1 | d128afa0c1ce3d28 | D3-g27 | optimizer.py:2418 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('bounds', ['(0.0,0.0)', '(0.8,0.0)']) | faithful by construction |
| 1 | 0a40fc8d3d37f2ba | D3-g27 | optimizer.py:2111 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('kept', ['right', 'left']) | faithful by construction |
| 1 | 6af4c3b8f521e3d3 | D3-g27 | optimizer.py:2111 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('kept', ['left', 'right']) | faithful by construction |
| 1 | f077d8a96cc1e3ed | D3-g27 | optimizer.py:1577 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('h', ['0.0001', '-0.0001']) | faithful by construction |
| 1 | 6a32950e7b3e62f2 | D3-g27 | optimizer.py:1580 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('h', ['9.999778782798785e-13', '0.0001']) | faithful by construction |
| 1 | c5abe60d7c7ca966 | D3-g27 | optimizer.py:1582 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | ef7b85a510c47950 | D3-g27 | optimizer.py:1870 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('kept', ['best', 'polished']) | faithful by construction |
| 1 | 3067ff76235329e4 | D3-g27 | optimizer.py:1871 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('kept', ['best', 'polished']) | faithful by construction |
| 1 | b94f040a7b0aed92 | D3-g27 | optimizer.py:2494 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('output', ["('ok',('idle_coasting',))", "('ok',('manual_plan',))"] | faithful by construction |
| 1 | 9aa50bd32847b4dd | D3-g28 | optimizer.py:1948 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['raise:ValueError: no usable starting point', 'raise:V | faithful by construction |
| 1 | 1e3d68358832d695 | D3-g28 | optimizer.py:1957 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('yields', ['5 calls', '3 calls']) | faithful by construction |
| 1 | b53efc6448b724e4 | D3-g28 | optimizer.py:1994 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('x', ['0.500000', '1.500000']) | faithful by construction |
| 1 | 92e6a72a53dd339f | D3-g28 | optimizer.py:1996 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('outcome', ['raise:FloatingPointError: solver blow-up', 'ok:None'] | faithful by construction |
| 1 | 64629e9b22df0c16 | D3-g28 | optimizer.py:2170 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('fraction', ['0.500000', '0.750000']) | faithful by construction |
| 1 | 0a673ba4467a184c | D3-g28 | optimizer.py:2172 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['ok:0.0', 'raise:ZeroDivisionError: division by zero'] | faithful by construction |
| 1 | 62abf71b9686f2b8 | D3-g28 | optimizer.py:2082 | verify | low | guess_max_abs_diff=0.2358 at a price mean exactly PRICE_MEAN_GUESS_EPS; null_ordinary_prices_diff=0 | faithful by construction |
| 1 | 9e9ab1d6567ff65b | D3-g28 | optimizer.py:2086 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('one_zero', ['[1.0]', '[nan]']) | faithful by construction |
| 1 | 01e740ed4f78ae95 | D3-g28 | optimizer.py:2126 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dt0', ['ok:[0.0, 0.0, 0.0, 0.0]', 'raise:ZeroDivisionError: divis | faithful by construction |
| 1 | 26180738b4dfa52e | D3-g28 | optimizer.py:2126 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('pmax_neg', ['ok:[0.0, 0.0, 0.0, 0.0]', 'ok:[-1.0, -1.0, -1.0, -1. | faithful by construction |
| 1 | 09e80cfe3036223e | D3-g28 | optimizer.py:2130 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 8206a42b98c8dd86 | D3-g28 | optimizer.py:2144 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('pct', ['0.000 %', '50.000 %']) | faithful by construction |
| 1 | e670e7e026a9f4ec | D3-g28 | optimizer.py:2146 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('over_pct', ['100.000 %', '200.000 %']) | faithful by construction |
| 1 | 8171db177f51df33 | D3-g29 | optimizer.py:2300 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie_reason', ["'comfort_floor'", "'cheap_price'"]) | faithful by construction |
| 1 | 2aff1f5c0b10dffa | D3-g29 | optimizer.py:2303 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie_reason', ["'cheap_price'", "'solar_surplus'"]) | faithful by construction |
| 1 | 000221f3921dd956 | D3-g29 | optimizer.py:2309 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('tie_reason', ["'cheap_price'", "'preheat_weather'"]) | faithful by construction |
| 1 | 0ea7620ce058c489 | D3-g29 | price_model.py:66 | verify | low | V1 6 arm pair(s) moved, null moved 0; e.g. ('days2_shape_h8', ['1.478675497', '1.36794702']) | 6 of 6 moving arms read the mutant value |
| 1 | 213a122afd9ff3e1 | D3-g29 | price_model.py:69 | verify | low | V1 8 arm pair(s) moved, null moved 0; e.g. ('days1_confidence', ['0.2', '0.1']) | 8 of 8 moving arms read the mutant value |
| 1 | b10967dd4ea185fd | D3-g30 | price_model.py:72 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('shape_min_winter_day', ['0.291439', '0.394538']) | faithful by construction |
| 1 | 7e5493bcbddd6c18 | D3-g30 | price_model.py:80 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('qf_h7q0_two_days_up_down', ['0.924', '0.948']) | faithful by construction |
| 1 | 66686e3bc3bac9b9 | D3-g30 | price_model.py:81 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('predict_0700_5_days', ['1.57377', '1.661202']) | faithful by construction |
| 1 | 5bf50f5d986f927d | D3-g30 | price_model.py:84 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('qf_h6q0_quarter_at_0p2_of_hour', ['0.246914', '0.465116']) | faithful by construction |
| 1 | cc96ce9e391ca6f2 | D3-g30 | price_model.py:85 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('qf_h3q0_negative_quarters_q0_30x', ['3.368421', '3.657143']) | faithful by construction |
| 1 | b5aef00760fd5ea8 | D3-g30 | price_model.py:90 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('weekday_sigma_17_two_days_day_reversed', ['1.0936', '0.9929']) | faithful by construction |
| 1 | b9b6cf1d15a84248 | D3-g30 | price_model.py:337 | verify | medium | V1 5 arm pair(s) moved, null moved 0; e.g. ('edm_empty_day_types_level_0p8', ['None', "'raises ValueError'"]) | faithful by construction |
| 1 | a5c9796d35117839 | D3-g30 | price_model.py:342 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('edm_5_days_exactly_confident', ['0.233151', 'None']) | faithful by construction |
| 1 | 13cadf1ab9a2de61 | D3-g30 | price_model.py:400 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('var_loaded_exactly_cap_225', ['225.0', '0.0']) | faithful by construction |
| 1 | b5a482468c783209 | D3-g30 | price_model.py:207 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('days_learned_mean_exactly_1e-6', ['0', '1']) | faithful by construction |
| 1 | 0b10a7c76e2514d2 | D3-g30 | price_model.py:219 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('weekday_sigma_17_one_winter_day', ['1.1858', '0.4593']) | faithful by construction |
| 1 | c4697335da324182 | D3-g30 | price_model.py:226 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('weekday_shape_17_one_winter_day', ['2.186', '1.142']) | faithful by construction |
| 1 | 4e79ba6ea642d086 | D3-g30 | price_model.py:258 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('qf_h3q3_hour_mean_exactly_1e-6', ['1.0', '3.368421']) | faithful by construction |
| 1 | 12cd6ddd79fb36fc | D3-g30 | price_model.py:269 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('qf_h7q0_1_day', ['0.9', '0.988']) | faithful by construction |
| 1 | 3a064c11321daba7 | D3-g31 | price_model.py:417 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('weekday_sigma_max', ['0.538', '0.0']) | faithful by construction |
| 1 | efa02472a5a773bc | D3-g31 | price_model.py:421 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('weekend_sigma_max', ['0.4726', '0.0']) | faithful by construction |
| 1 | a38612ad3ad9cd34 | D3-g31 | price_model.py:141 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | f06caefa38815e4f | D3-g31 | price_model.py:141 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 28de20de50a9540b | D3-g31 | price_model.py:155 | verify | medium | V1 4 arm pair(s) moved, null moved 0; e.g. ('weekday_days', ['5', '6']) | faithful by construction |
| 1 | e5eea05f4463602e | D3-g31 | price_model.py:844 | verify | medium | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 0d159d7ddd1702d9 | D3-g32 | price_model.py:544 | verify | medium | V1 1 arm pair(s) moved, null moved 0; e.g. ('guessed_tail', ['[3.0, 3.0, 3.0]', '[2.0, 2.0, 2.0]']) | faithful by construction |
| 1 | b539d4504385a139 | D3-g32 | price_model.py:825 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('reason_unknown_empty_dict', ["'Price entity is empty'", "'Price e | faithful by construction |
| 1 | 88732fcb7c604858 | D3-g32 | sysid.py:549 | verify | low | V1 5 arm pair(s) moved, null moved 0; e.g. ('tau_fast_0.333h', ['True', 'False']) | 5 of 5 moving arms read the mutant value |
| 1 | 0d5a6ef5041b90f9 | D3-g32 | sysid.py:1606 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('features_cell_step_kw', ['4.353515625', '4.3125']) | faithful by construction |
| 1 | 4a189db92053760e | D3-g32 | sysid.py:2409 | verify | medium | V1 16 arm pair(s) moved, null moved 0; e.g. ('moved_ua0.005_c4.0_g-0.8', ["(False, 'fitted gains outside plaus | faithful by construction |
| 1 | 80cb9a8152f72e57 | D3-g32 | sysid.py:2411 | verify | low | V1 4 arm pair(s) moved, null moved 0; e.g. ('gains_fit-0.5', ["(True, 'ok', 0.0)", "(True, 'ok', -0.5)"]) | faithful by construction |
| 1 | 822c0c6477ed703e | D3-g33 | sysid.py:1708 | verify | low | V1 consulted_tie: baseline run 0 vs --mutant run 1 (finder 0 -> 1); null consulted_null: 1 vs 1 | no parsed moving arm to compare |
| 1 | adc459d2db521041 | D3-g33 | sysid.py:1708 | verify | low | V1 consulted_tie: baseline run 1 vs --mutant run 0 (finder 1 -> 0); null consulted_null: 1 vs 1 | no parsed moving arm to compare |
| 1 | a23ed12204379870 | D3-g33 | sysid.py:1715 | verify | low | V1 refuses_tie: baseline run 0 vs --mutant run 1 (finder 0 -> 1); null refuses_below: 0 vs 0 | no parsed moving arm to compare |
| 1 | 6e67f128730b3ecd | D3-g33 | sysid.py:1541 | verify | low | V1 band_refused: baseline run 0 vs --mutant run 1 (finder 0 -> 1); null band_refused_inside: 0 vs 0 | no parsed moving arm to compare |
| 1 | cf96494341270371 | D3-g33 | sysid.py:1541 | verify | low | V1 band_refused: baseline run 0 vs --mutant run 1 (finder 0 -> 1); null band_refused_inside: 0 vs 0 | no parsed moving arm to compare |
| 1 | 20e001c48fb19330 | D3-g33 | sysid.py:1549 | verify | low | V1 open_hours: baseline run 6 vs --mutant run 7 (finder 6 -> 7); null open_hours_flat: 4 vs 4 | no parsed moving arm to compare |
| 1 | 95090bc58c6535b2 | D3-g33 | sysid.py:1913 | verify | low | V1 reached_fit_6: baseline run 1 vs --mutant run 0 (finder 1 -> 0); null reached_fit_7: 1 vs 1 | no parsed moving arm to compare |
| 1 | 505422349a01c3ff | D3-g33 | sysid.py:1922 | verify | low | V1 reached_fit_tie: baseline run 0 vs --mutant run 1 (finder 0 -> 1); null reached_fit_null: 1 vs 1 | no parsed moving arm to compare |
| 1 | 7dbbb95252ced538 | D3-g33 | sysid.py:1922 | verify | low | V1 reached_fit_tie: baseline run 1 vs --mutant run 0 (finder 1 -> 0); null reached_fit_null: 1 vs 1 | no parsed moving arm to compare |
| 1 | aa6d264aa0411bcd | D3-g33 | sysid.py:1942 | verify | low | V1 reached_fit_6: baseline run 1 vs --mutant run 0 (finder 1 -> 0); null reached_fit_7: 1 vs 1 | no parsed moving arm to compare |
| 1 | b8d5ec03e8eba5c7 | D3-g34 | sysid.py:1942 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[refused:not enough usable intervals]', '[refused:fit | faithful by construction |
| 1 | 756f3bebd6a42efc | D3-g34 | sysid.py:1974 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[refused:fitted gains outside plausible bounds]', '[c | faithful by construction |
| 1 | 84372c0eb1502d14 | D3-g34 | sysid.py:2010 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[completed ua=0.07118859468970369 C=5.290838816465746 | faithful by construction |
| 1 | 20f72103eda78713 | D3-g34 | sysid.py:2018 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[completed ua=0.19574719588552125 C=5.126629633823094 | faithful by construction |
| 1 | 50daaa57683189c5 | D3-g34 | sysid.py:2018 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[completed ua=0.19574717836315605 C=5.126629119820055 | faithful by construction |
| 1 | 4eeb366191982f92 | D3-g34 | sysid.py:2032 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[completed ua=0.1931445891215017 C=4.5987039940244845 | faithful by construction |
| 1 | 44bb0ce0b258242c | D3-g34 | sysid.py:2038 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[refused:fit gave implausible signs]', '[refused:sens | faithful by construction |
| 1 | 10665a84dc064489 | D3-g34 | sysid.py:2114 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[refused:step gave insufficient excitation]', '[compl | faithful by construction |
| 1 | d7421c10ed63c281 | D3-g34 | sysid.py:2114 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('outcome', ['[completed ua=1.9999999999999991 C=4.0 conf=0.75]', ' | faithful by construction |
| 1 | 501a5e7cda702183 | D3-g35 | sysid.py:2146 | verify | low | V1 18 arm pair(s) moved, null moved 0; e.g. ('key_internal_gains_kw.', ["0.300000049919569  # completed=1 reas | inconclusive by construction |
| 1 | 20cde1046cbd5681 | D3-g35 | sysid.py:2154 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('key_completed.', ["True  # completed=1 reason='ok' ua=0.199999998 | inconclusive by construction |
| 1 | 6cfdb101dc87a6ea | D3-g35 | sysid.py:2154 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('key_completed.', ["True  # completed=1 reason='ok' ua=0.199999998 | inconclusive by construction |
| 1 | d203230963349f60 | D3-g35 | sysid.py:2162 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('key_internal_gains_kw.', ["0.0  # completed=1 reason='ok' ua=0.19 | inconclusive by construction |
| 1 | 5654f855fcc27724 | D3-g35 | sysid.py:2187 | verify | low | V1 14 arm pair(s) moved, null moved 0; e.g. ('key_confidence.', ["0.9813074506932448  # completed=1 reason='ok | inconclusive by construction |
| 1 | 4593852cf3862b3c | D3-g35 | sysid.py:2223 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('key_completed.', ["True  # completed=1 reason='ok' ua=3.281804786 | inconclusive by construction |
| 1 | 64f3ef1feaaf7bc9 | D3-g35 | sysid.py:2223 | unresolved | low | hunt_hit=0 of 14087 evaluations; key case not reached | no parsed moving arm to compare |
| 1 | 784e362919d88a92 | D3-g35 | sysid.py:2223 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('key_completed.', ["True  # completed=1 reason='ok' ua=5.0 gains=1 | inconclusive by construction |
| 1 | d661d68f54982097 | D3-g35 | sysid.py:2223 | unresolved | low | key_tapped_tau=200.00000000000887 (not 200); key_completed baseline False = mutant False | no parsed moving arm to compare |
| 1 | a5b06d898bf0ba03 | D3-g35 | sysid.py:2237 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('key_completed.', ["True  # completed=1 reason='ok' ua=0.199999994 | inconclusive by construction |
| 1 | c51115b0104a8bf5 | D3-g35 | sysid.py:2244 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('key_completed.', ["True  # completed=1 reason='ok' ua=0.271958594 | inconclusive by construction |
| 1 | 4da9d281d4714565 | D3-g35 | sysid.py:2246 | unresolved | low | hunt_hit=0 of 28215 evaluations; key case not reached | no parsed moving arm to compare |
| 1 | b4f7503c6959449d | D3-g37 | sysid.py:1073 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('unit_halfwidth_seed1000', ['0.31963411254338214', '0.141996100744 | faithful by construction |
| 1 | f6016f6adb9683a8 | D3-g37 | sysid.py:1073 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('unit_halfwidth_seed1000', ['0.31963411254338214', '0.141996100744 | faithful by construction |
| 1 | c1ce480d20083d83 | D3-g38 | sysid.py:897 | verify | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('refused[tau500_ua0.5]', ['1', '0']) | faithful by construction |
| 1 | d8e588be2e0aba89 | D3-g38 | sysid.py:897 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('refused[tau0.1_exact]', ['0', '1']) | faithful by construction |
| 1 | e7edbe5bae5e180a | D3-g38 | sysid.py:897 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('refused[ua0.01_exact]', ['0', '1']) | faithful by construction |
| 1 | a1ba3ad7c4c53dd5 | D3-g38 | sysid.py:875 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('series[N=6]', ['1', '0']) | faithful by construction |
| 1 | 56294c2224449394 | D3-g38 | sysid.py:266 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('regulates[tie_flow-0.01]', ['1', '0']) | faithful by construction |
| 1 | 6c7eefdfaf64ea5a | D3-g38 | sysid.py:1279 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('admit[one_zone_1e-6]', ['0', '1']) | faithful by construction |
| 1 | a6c42cff101ffc65 | D3-g38 | sysid.py:643 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('admit[k_s=exact_1e-9,constructor]', ['0', '1']) | faithful by construction |
| 1 | 6f546669421ba07b | D3-g38 | sysid.py:676 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('admit[s3_st1_r2]', ['0', '1']) | faithful by construction |
| 1 | 7c25d8795fa2d46c | D3-g38 | sysid.py:677 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('admit[band_1e-9_exact]', ['0', '1']) | faithful by construction |
| 1 | 907d16324ff11dda | D3-g38 | sysid.py:677 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('admit[c_r=exact_1e-9]', ['0', '1']) | faithful by construction |
| 1 | 990cdd83373504ad | D3-g38 | sysid.py:677 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('admit[k_s=exact_1e-9]', ['0', '1']) | faithful by construction |
| 1 | d0f2d18b2b49232c | D3-g38 | sysid.py:677 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('admit[c_s=exact_1e-9]', ['0', '1']) | faithful by construction |
| 1 | 4467ecd198f47483 | D3-g38 | sysid.py:683 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('admit[band_3h_tie]', ['1', '0']) | faithful by construction |
| 1 | 559484953b5cdd5d | D3-g39 | sysid.py:610 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('boundary_k_s', ['0.0', '1200000000.0']) | faithful by construction |
| 1 | cb38833c854f6257 | D3-g39 | sysid.py:610 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('boundary_c_r', ['0.0', '1.999999999e-09']) | faithful by construction |
| 1 | fa6fdd76e6fa619d | D3-g39 | sysid.py:610 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('boundary_c_s', ['0.0', '1.999999999e-09']) | faithful by construction |
| 1 | 246043395831f540 | D3-g39 | tariff.py:128 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('peaks0', ['0.0', 'raises ZeroDivisionError']) | faithful by construction |
| 1 | de935c38786265e7 | D3-g39 | tariff.py:437 | verify | medium | V1 4 arm pair(s) moved, null moved 0; e.g. ('nan_state', ["('2026-01-10T07:00:00/60', 2.0, 1, 1.0)", "('', 0.0 | faithful by construction |
| 1 | 4ad3dc13bfdb70a8 | D3-g39 | tariff.py:465 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('f0_state', ["('2026-01-10T07:00:00/60', 2.0, 1, 0.0)", "('', 0.0, | faithful by construction |
| 1 | 7fcaf91cced5ce41 | D3-g39 | tariff.py:235 | verify | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('nan_peaks', ['((2.0,), 1)', "(('nan',), 1)"]) | faithful by construction |
| 1 | 37b3c9a03326d207 | D3-g39 | tariff.py:489 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('two_undated', ["[(3.0, ''),", "[(3.0, '')]"]) | faithful by construction |
| 1 | 6536ff6b094f971d | D3-g39 | tariff.py:744 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('k0', ['0.0', '2.9654859789671595']) | faithful by construction |
| 1 | 2d64a114647f1551 | D3-g39 | tariff.py:747 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 1 | 5371ee2b5e897750 | D3-g39 | tariff.py:747 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('all_negative', ['0.0', '-1.0']) | faithful by construction |
| 1 | 2d037a10caa62e28 | D3-g41 | tariff.py:1225 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('empty', ['0.0', 'raise:ValueError']) | faithful by construction |
| 1 | 43b54266f12bfb21 | D3-g41 | thermal_model.py:4453 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('cop_out30', ['np.float64(5.25)', 'np.float64(5.512500000000001)'] | faithful by construction |
| 1 | dfe094233a9164e0 | D3-g41 | thermal_model.py:4455 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('cop_m2_h90', ['np.float64(1.8987499999999997)', 'np.float64(2.712 | faithful by construction |
| 1 | e3a350a3272762f1 | D3-g41 | thermal_model.py:4458 | verify | medium | V1 4 arm pair(s) moved, null moved 0; e.g. ('amb_none_nan', ['np.float64(2.44125)', 'np.float64(1.627500000000 | faithful by construction |
| 1 | 94ce174acf85b6f2 | D3-g41 | thermal_model.py:4460 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('amb90_cop_m2', ['np.float64(1.6275000000000002)', 'np.float64(2.4 | faithful by construction |
| 1 | 898d741cf6142efb | D3-g41 | thermal_model.py:4463 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('cop_out0', ['np.float64(2.8874999999999997)', '[2.8875,2.8875,2.5 | faithful by construction |
| 1 | a6cebb125b72f083 | D3-g41 | thermal_model.py:3328 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('cop_out30', ['5.25', '5.512500000000001']) | faithful by construction |
| 1 | c5e678a5d1812e40 | D3-g41 | thermal_model.py:4019 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('dt0_buf', ['69.9999999', "'ZeroDivisionError'"]) | faithful by construction |
| 2 | 440c0a6d5ee72d19 | D3-g36 | sysid.py:2315 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('', ['ua=0.150000000 cap=15.000000000 tau=100.000000000 conf=0.125 | inconclusive by construction |
| 2 | 809e8d14f04e1127 | D3-g36 | sysid.py:2315 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('', ['refused:not enough samples', 'refused:not enough usable inte | inconclusive by construction |
| 2 | 0137ee1f014fb759 | D3-g36 | sysid.py:2325 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('', ['refused:slab mode too slow for the excitation window: tau_fa | inconclusive by construction |
| 2 | 24aa39e8c4c6d26a | D3-g36 | sysid.py:2325 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('', ['ua=0.150000000 cap=15.000000000 tau=100.000000000 conf=0.374 | inconclusive by construction |
| 2 | ae8f84354933d191 | D3-g36 | sysid.py:2375 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('', ['ua=0.150000000 cap=15.000000000 tau=100.000000000 conf=0.404 | inconclusive by construction |
| 2 | 9460d3802a8903d6 | D3-g36 | sysid.py:2376 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('', ['ua=0.123915027 cap=5.010000000 tau=40.430931814 conf=0.00000 | inconclusive by construction |
| 2 | de6bbadf1499bae9 | D3-g36 | sysid.py:2381 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('_nan', ['ua=0.150000000 cap=8.333333333 tau=55.555555556 conf=nan | inconclusive by construction |
| 2 | 0baef4e86433b225 | D3-g36 | sysid.py:1752 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('_idle_samples', ['0', '2']) | inconclusive by construction |
| 2 | b3c0e51c511b2618 | D3-g36 | sysid.py:1778 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('_kw', ['0.2', '0.1']) | inconclusive by construction |
| 2 | 9dd0547496b091b0 | D3-g36 | sysid.py:1782 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_kw', ['0', '-3']) | inconclusive by construction |
| 2 | 8840eb67a646cd97 | D3-g36 | sysid.py:1785 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('_phase', ['aborted', 'step']) | inconclusive by construction |
| 2 | 5104733df3085998 | D3-g36 | sysid.py:835 | verify | medium | V1 2 arm pair(s) moved, null moved 0; e.g. ('_log_ua', ['4.605170', '6.907755']) | inconclusive by construction |
| 2 | 373207a8e12c37c5 | D3-g36 | sysid.py:842 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('_x1', ['10.000000', '20.000000']) | inconclusive by construction |
| 2 | 291748b42a54c1f6 | D3-g36 | sysid.py:846 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('', ['ua=0.690204601 cap=16.767323953 tau=24.293265972 conf=0.9984 | inconclusive by construction |
| 3 | 5f094dbca9a593e9 | D3-g40 | tariff.py:750 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('runtime_warnings', ['0', '906']) | inconclusive by construction |
| 3 | 996dce5148e02763 | D3-g40 | tariff.py:806 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('runtime_warnings', ['0', '1356']) | inconclusive by construction |
| 3 | 3e9a439baa86a074 | D3-g40 | tariff.py:528 | verify | medium | V1 4 arm pair(s) moved, null moved 0; e.g. ('peaks_reloaded', ['3', '1']) | inconclusive by construction |
| 3 | 1894e6dcd2251a30 | D3-g40 | tariff.py:570 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('nan_windows', ['0', '10']) | inconclusive by construction |
| 4 | 7068e39e4608027f | D3-g43 | thermal_model.py:4699 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('batch_vs_scalar_parity', ['0', '0.00408045']) | faithful by construction |
| 4 | 6462c28df2f973e0 | D3-g43 | thermal_model.py:4702 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('batch_vs_scalar_parity', ['0', '0.0166438']) | faithful by construction |
| 5 | b2faf84904db389e | D3-g45 | thermal_model.py:677 | unresolved | low |  | faithful by construction |
| 5 | 1b476993921016f9 | D3-g45 | thermal_model.py:852 | unresolved | low |  | faithful by construction |
| 5 | ea888783bb621669 | D3-g45 | thermal_model.py:855 | unresolved | low |  | faithful by construction |
| 5 | b098598faf0d87dc | D3-g45 | thermal_model.py:835 | unresolved | low |  | faithful by construction |
| 5 | dd40fdb4edae4d79 | D3-g45 | thermal_model.py:2270 | unresolved | medium |  | faithful by construction |
| 5 | 19404e3632806509 | D3-g45 | thermal_model.py:2554 | unresolved | medium |  | faithful by construction |
| 5 | beeb068352333132 | D3-g45 | thermal_model.py:2573 | unresolved | low |  | faithful by construction |
| 5 | ea9c4705de428b28 | D3-g45 | thermal_model.py:2576 | unresolved | low |  | faithful by construction |
| 5 | 98853a541b6b5d6a | D3-g45 | thermal_model.py:2581 | unresolved | medium |  | faithful by construction |
| 5 | fdf5872fd576c405 | D3-g45 | thermal_model.py:2581 | unresolved | medium |  | faithful by construction |
| 5 | 39041ccf21eedba6 | D3-g45 | thermal_model.py:2583 | unresolved | medium |  | faithful by construction |
| 6 | 05b5a15efaaf70de | D3-g44 | thermal_model.py:677 | verify | medium | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 6 | 36117bb3a189672b | D3-g44 | thermal_model.py:3576 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 6 | 3d4899a05eb126c3 | D3-g44 | thermal_model.py:940 | verify | low | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 6 | 78b7f2ebcf85c8a1 | D3-g44 | thermal_model.py:4822 | verify | high | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 6 | 9362d5efbe6808c2 | D3-g44 | thermal_model.py:3569 | verify | medium | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 6 | cde383447b865539 | D3-g44 | thermal_model.py:303 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('vol_100.0', ['True', 'False']) | faithful by construction |
| 6 | f66c6e9cf9d1f84a | D3-g44 | thermal_model.py:3567 | verify | medium | V1 0 arm pair(s) moved, null moved 0; e.g. None | faithful by construction |
| 7 | 5b8e7044ee7974f8 | D3-g42 | thermal_model.py:5012 | verify | low | V1 2 arm pair(s) moved, null moved 0; e.g. ('wood_after_from_2.0', ["'2.0'", "'10.0'"]) | faithful by construction |
| 7 | f7e051cc469b465f | D3-g42 | thermal_model.py:3517 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('gain_m10', ["'0.0'", "'-0.049'"]) | faithful by construction |
| 7 | 402ffd06ddbd856a | D3-g42 | thermal_model.py:3649 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('h_20.0_10.0_20.0', ["'0.0'", "'168.0'"]) | faithful by construction |
| 7 | d90533f4d17cfa14 | D3-g42 | thermal_model.py:3649 | verify | low | V1 3 arm pair(s) moved, null moved 0; e.g. ('h_10.0_5.0_20.0', ["'0.0'", "'168.0'"]) | faithful by construction |
| 7 | 011b9e2e975b5e98 | D3-g42 | thermal_model.py:3654 | verify | medium | V1 4 arm pair(s) moved, null moved 0; e.g. ('config_coast_hours_cooling_rate_0.0', ["'168.0'", "'346.573590279 | faithful by construction |
| 7 | 9df41596c4fa89c6 | D3-g42 | thermal_model.py:3479 | verify | low | V1 1 arm pair(s) moved, null moved 0; e.g. ('u_0.1', ["'0.1'", "'0.10075'"]) | faithful by construction |
| 7 | 029c040224dc4e38 | D3-g42 | thermal_model.py:3483 | verify | medium | V1 3 arm pair(s) moved, null moved 0; e.g. ('u_10.0', ["'0.11499999999999999'", "'0.17499999999999996'"]) | faithful by construction |
