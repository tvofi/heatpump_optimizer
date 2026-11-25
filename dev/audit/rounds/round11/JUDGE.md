# Audit round 11 -- judge verdicts (cloud judge box J1)

Dedup: the local judge's result, laid in verbatim (DEDUP.json): 220 canonical, 19 merged; the merged rows are added by the workflow.

Verdicts over 220 canonical findings: verified 170, weakened 45, refuted 1, unreproduced 4

Survivor severities: critical 2, high 15, medium 50, low 148

## Measurement

- Scripted re-runs: tools/audit/judge_batch.py in eleven shards (judge-batch-1*.json/.md), label judge-r11-runner1, from the worktree at origin/handoff/audit-r11-register. Most rows are by-hand: harness headers carry no JUDGE-* lines, so the runner reads the first RESULT line as the metric.
- The evidence commands name $HOME/venv-ci/bin/python3; on this box that path was linked to /opt/hpo/venv-ci (the first shard-1 attempt ran rc=127 everywhere and was re-run whole).
- Hand re-runs, serially under the judge-r11 lease: every finding's evidence command, its null-control command where one is a command, and its perturbation where the change names a harness flag; planted-seat findings in a private copy of $HOME/audit-r11-px (macOS AppleDouble ._* extraction artefacts filtered out of the copy: with them every D10 harness raised UnicodeDecodeError), every other finding in the worktree. A second pass re-ran timeouts and commands with placeholders (<clone holding 92d38ecb> -> the box checkout, <plan_view.py payload> -> a generated payload, cd <export root> -> the copy) with full output.
- D15 findings that need the owner's bundle were not re-run: each carries 'bundle: local re-run owed' and is judged on its record and the verifier's executed number.
- Converted leads (D1-s1-51, D1-s2-51, D1-s2-52, D17-s3-51, D2-s1-51, D4-s2-51) carry no finder harness; they are judged on the verifier's executed number with its null and perturbation.
- Every number quotes its tree (planted copy or worktree). load1 stayed near 1 on this 1-box run; thread_factor re-takes are noted on the rows they touched.

## Classes

Survivor classes: I5 38, P2 23, N-move-stale-path 20, I4 13, N-comment-style 11, I3 8, P1 7, I1 7, N-silent-zero 6, P9 6, N-structure-blind 5, N-no-expiry 4, N-confounded-learner 4, N-unreleased-hold 4, I2 3, P4 2, N-swallowed-failure 2, N-log-flood 2, N-entry-data-placement 2, N-entity-metadata 2, N-vocabulary-drift 2, N-step-grid 2, P8 2, N-stale-step-actuation 2, N-partial-window-extrapolation 2, N-dead-input 2, P5 2, N-copy-style 2, N-unbudgeted-background 2, N-uncleared-issue 1, N-dropped-refresh 1, N-unordered-tiebreak 1, N-restore-race 1, N-finally-return 1, N-staleness 1, N-mode-coupled-write 1, P11 1, P3 1, N-order-coupling 1, N-table-value 1, N-wrong-law 1, N-objective-as-money 1, N-missing-unit-scale 1, N-partial-payload-parse 1, N-inverted-aggregate 1, P7 1, N-event-misattribution 1, N-untranslated-splice 1, N-orphan-doc 1, N-instrument-locator 1, N-duplicated-rule 1, N-leaf-imports-solver 1, N-shared-config 1, N-name-sort 1, N-solve-recompute 1, P10 1, N-unbounded-retention 1

Minted this round (nearest / differs in JUDGE.json): N-comment-style, N-copy-style, N-dead-input, N-dropped-refresh, N-duplicated-rule, N-entity-metadata, N-entry-data-placement, N-event-misattribution, N-instrument-locator, N-inverted-aggregate, N-missing-unit-scale, N-mode-coupled-write, N-objective-as-money, N-orphan-doc, N-partial-payload-parse, N-partial-window-extrapolation, N-stale-step-actuation, N-swallowed-failure, N-table-value, N-unbounded-retention, N-unbudgeted-background, N-uncleared-issue, N-unordered-tiebreak, N-unreleased-hold, N-untranslated-splice, N-wrong-law

## Verdicts

| id | verdict | severity | stop | class | value |
|---|---|---|---|---|---|
| D0-s2-01 | weakened | low | bug | P4 | worktree: race gap max 2.0292 (cells 2.0292/1.7251/1.6782/1.6310/1.4675); finder harness reproduces finder exactly; verifier V2 independent 0.73-1.77 and 0-zero-start gaps at 45 C |
| D0-s3-01 | verified | medium | bug | I2 | worktree: after_strip_lines=0 rc=2 (REFUSE) vs before 1 rc=0; perturb keep_bundles -> after_strip_lines=1 rc=0 |
| D0-s3-02 | verified | low | bug | P4 | worktree: summer_negative_gap_cells=16/60, max 3204.33, rel max 0.0739; perturb off_in_prod 16 -> 2; flat 0/60 |
| D0-s3-03 | refuted | low | hygiene | I5 | worktree, finder grid: 0/40 at default; weak_floor 13/40. Verifier V2 at comfort_weight 1.0: 24/44 cells breach without the credit (cold coast-down days absent from the finder grid) |
| D1-s1-01 | weakened | low | bug | N-uncleared-issue | planted copy: stale_fallback_issues_after_restart=0 in main and null; stop arm 0 -> 1 only under --perturb; runner (worktree) got 1 vs expected 1 at tf 1.181 |
| D1-s1-03 | verified | medium | bug | N-dropped-refresh | planted copy: stale_request_refresh_rows=7 of 8 (debounced); null origin=direct 0 of 8; --perturb-rerun 0 of 8 |
| D1-s1-51 | verified | low | bug | N-unordered-tiebreak | verifier: distinct_tie=2 over PYTHONHASHSEED 1..12 (null 1, perturb 1) |
| D1-s2-01 | weakened | low | bug | P1 | planted copy: leaves_reaching_live=3, disk_undecodable=3 of 515, stores 2; null 0 of 148 |
| D1-s2-02 | weakened | medium | bug | N-no-expiry | planted copy: stale_cells_published=6 of 6, future_published=1; fresh null 0 |
| D1-s2-03 | verified | high | bug | N-no-expiry | planted copy: stuck_published_fresh=5 of 5; advancing null 0 |
| D1-s2-04 | verified | medium | bug | N-restore-race | planted copy: consequences=2 (hold_not_released 1, baseline_lost_on_disk 1); serial null 0 |
| D1-s2-05 | weakened | low | bug | P1 | planted copy: per 200 mutants build 8-11 + permanent cycle 14-17 per version; null 0 |
| D1-s2-06 | weakened | low | bug | P1 | planted copy: restarts_raising=8 of 10, control 0 |
| D1-s2-51 | verified | medium | bug | P1 | verifier: above_max_accepted=15 of 15 (below_min 0, perturb 0) |
| D1-s2-52 | verified | low | bug | P2 | verifier: config_arms_disagree=2 (null 0, fresh 0, perturb 0) |
| D1-s3-01 | verified | medium | bug | P1 | planted copy: pump_nonfinite_flag_true=10, freeze_fault 5 cycles; null 0; perturb parse_bool_finite -> 0 |
| D1-s3-02 | verified | low | bug | P1 | planted copy: ecl110_bool_accepted=3; numeric null 0; perturb ecl110_refuse_bool -> 0 |
| D1-s3-03 | weakened | low | bug | P1 | planted copy: openmeteo_year1_solve_failures=3; healthy 0; perturb overflow_guard -> 0 |
| D1-s3-04 | verified | medium | bug | P2 | planted copy: transport_unbounded_waits=1, lock_held_after=1; perturb -> 0 |
| D1-s3-05 | weakened | low | bug | N-swallowed-failure | planted copy: persist_silent_at_warning=10 of 10 reached handlers; perturb 10 -> 9 |
| D1-s3-06 | verified | low | hygiene | N-log-flood | planted copy: repeat_error_records=3 of 5 injections; perturb -> 0 |
| D1-s3-07 | verified | low | bug | N-swallowed-failure | planted copy: silent_broad_no_record=7 of 12 reached; perturb 7 -> 6 |
| D10-s1-01 | verified | medium | bug | N-silent-zero | planted copy: acknowledged_unparseable=6 of 6, cleared_existing_return=3; perturb -> 0; control accepted 1 |
| D10-s1-02 | verified | low | bug | N-silent-zero | planted copy: silent_refusals=2 of 2; perturb -> 0; controls raised 2 |
| D10-s1-03 | verified | low | hygiene | N-entry-data-placement | planted copy: continue_settings_in_data=41; perturb split -> 0, merged_equal=1 |
| D10-s1-05 | weakened | low | hygiene | I1 | planted copy: unrecovered_triples=51 of 53, never_stepped_past=49; perturb 51 -> 47 |
| D10-s1-06 | weakened | low | hygiene | I5 | planted copy (2400 s re-take): modules_below_95=34 of 95, package 91.38 %, config_flow.py 99.21 % (8 missed); but 15 of 25 traced scripts exit non-zero on the export |
| D10-s2-01 | verified | medium | bug | P2 | planted copy: shadowed_options_saved=2, reconfigure_reported_success=1; perturb -> 0 |
| D10-s2-03 | verified | low | hygiene | I4 | planted copy: bad=2 of 37 sites; perturb raises bad to 4 (direction up as stated) |
| D10-s2-04 | verified | low | hygiene | N-entity-metadata | planted copy: unit_without_device_class=14 (3 delta sensors); --perturb-delta 14 -> 13 |
| D10-s3-01 | verified | low | hygiene | I5 | planted copy: untyped_requirements_under_done_row=1; null 0; perturb req -> 0 |
| D10-s3-02 | verified | low | hygiene | I5 | planted copy: coordinator_untyped_under_done_row=1; null 0; perturb coord -> 0 |
| D11-s1-01 | verified | low | bug | I3 | worktree: missed=2 of 67 corpus files; perturb -> 0; positive control rc=2, null rc=0 |
| D11-s1-02 | verified | medium | bug | I3 | worktree: unmonitored=2 of 3 rulesets; perturb -> 1; null 0 |
| D11-s1-03 | weakened | low | bug | I1 | worktree: control_red_on_drift=0, selftest_rewrote=1; perturb -> control red 1, rewrote 0 |
| D11-s1-04 | weakened | low | bug | I1 | worktree: baseline_pass=0, mutants_reached=0 of 16; perturb wraps -> baseline 1, 16/16 killed |
| D11-s1-05 | verified | medium | bug | I3 | worktree: pr_copy_unowned=1 of 8 meters; perturb -> 0; null 0 |
| D11-s1-06 | weakened | low | bug | I3 | worktree runner: real_repo_writes_on_selftest=1 (expected 1, reproduced, tf 1.000); my hand run timed out at 600 s; ls-remote shows no ref from this box's worktrees |
| D11-s2-01 | weakened | medium | bug | I3 | worktree: platform_gate_red=1 of 52 window merges, merged_not_green=2; perturb -> red 0, not_green 1 |
| D11-s2-02 | weakened | low | hygiene | I3 | worktree: owner_own_at_head=0 of 52; 31 approvals agent-declared under the owner account; null/perturb -> 31 |
| D11-s2-03 | weakened | low | hygiene | I3 | worktree: zip_attested=0 of 5 releases, tar 5/5; perturb -> 5 |
| D11-s2-04 | verified | low | hygiene | I5 | worktree: dup_units=16 over 86 corpus files, rulings_overlap 1; perturb -> 0 |
| D11-s3-02 | verified | medium | bug | I3 | worktree: rosters_linted=1 (.claude/workflows only), live rosters in dev/programme/rosters unlinted 2; gap arms TOTAL=0; perturb lints rosters/ and gap arms go red (TOTAL=4) |
| D11-s3-03 | weakened | low | bug | I1 | worktree: gap_noop_accepted=4 of 4; controls refused 3/3; perturb -> 0 |
| D11-s3-04 | weakened | low | bug | I1 | worktree (1500 s re-take): step5_wiring_gutted 570 passed, 0 failed; version_edit_gutted 9 failed; null 570/0; mutants_killed 1 of 2 |
| D12-s1-01 | weakened | low | bug | P2 | planted copy: zone_plants=2, zone_rows=192 on single-zone installs; control two-zone 96 rows |
| D12-s2-01 | verified | high | bug | P2 | planted copy: invented_zone_cells=47/47, heat_loss_response_kwh=0.000; --perturb -> 0/47 and 32.661 kWh response |
| D12-s3-01 | verified | high | bug | P2 | planted copy: on_off_clamped_cells=0/10 (166 sub-minimum steps); --perturb doc-modulation -> 10/10, 0 sub-minimum |
| D12-s3-02 | verified | medium | bug | P2 | planted copy: bad_fix_writes=8 of 12; --perturb entity-cap -> 0 |
| D12-s3-03 | verified | medium | bug | N-confounded-learner | planted copy: inflated_spans_folded=2, space_spans_folded 6; --perturb unobserved-no-space -> 0 and 0 |
| D13-s2-01 | verified | medium | hygiene | N-vocabulary-drift | worktree: untaught_share=0.478, 214 verdicts routed to other; --perturb teach-ci-red -> 0.337, 151 |
| D13-s2-02 | verified | medium | hygiene | N-vocabulary-drift | worktree: one_file 69 of 174 accepted entries (0.397), no_file 105; perturb readme -> 68 (0.391), down as stated |
| D14-s1-01 | verified | low | bug | N-step-grid | worktree: seams_total=40 (options widen 28 + services 12); --perturb-svc -> services 0, total 28 |
| D14-s1-02 | weakened | low | hygiene | N-finally-return | worktree: seams_baseline=1 (coordinator.py:1943), runtime_swallowed_reintroduced=1, control 0 |
| D14-s1-03 | verified | medium | bug | P8 | worktree: money_seams=5 with feed EUR on a SEK instance; null (feed SEK) 0; perturb -> 0 |
| D14-s2-01 | verified | medium | bug | N-staleness | worktree: quiet_stale_flags=6, input_problem_on=1; polled and null 0; perturb inf -> 0 |
| D14-s2-02 | verified | low | bug | N-no-expiry | worktree: wind_mismatch_hours=72 of 72; perturb covering -> 0 |
| D14-s2-03 | verified | low | bug | N-log-flood | worktree: barrier counts warning 1, exception/critical 0; live_blind_sites=1 of 71 |
| D15-s1-02 | weakened | low | hygiene | I4 | verifier: 72 privacy-gate violations over the whole synthetic bundle, 0 over the replay half |
| D15-s1-03 | verified | low | hygiene | N-silent-zero | verifier: verdict 12/12 with checks_run=11 |
| D15-s1-04 | verified | medium | bug | P2 | verifier: 0 of 192 rows kept by the debug ring loader |
| D15-s1-05 | verified | medium | bug | P2 | verifier: 1 count-0 bucket written and lost at reload; runner here fold_written=1 before rc=1 |
| D15-s2-01 | verified | low | hygiene | I4 | verifier: 2 learners voided, 42 samples lost |
| D15-s2-02 | verified | low | hygiene | I4 | verifier: 142 of 192 accuracy samples postdate the replay clock |
| D15-s2-03 | verified | low | hygiene | N-silent-zero | worktree: observe_bias_calls=0 over the --days 2 null bundle (96 cycles) |
| D15-s2-04 | unreproduced | low | bug | P7 | verifier: shipped arm timed out at 2400 s, fixed arm 0 differing; debug_replay.py has 0 occurrences of HASTUB_TZ |
| D15-s2-05 | weakened | low | hygiene | I4 | verifier: lane_red_judges=0 over 8 cycles; 5 judges printed, 4 graded, 8 counted |
| D15-s2-06 | unreproduced | low | hygiene | I4 | verifier: no_default=0 in a 2 h window (finder's window not reached under load) |
| D15-s2-07 | unreproduced | low | hygiene | I4 | verifier: not_frozen=0 in a 2 h window (finder's window not reached under load) |
| D15-s3-01 | verified | low | hygiene | N-silent-zero | verifier: self-test min 0 ms from 10 not-run rows; perturbation 0 -> 9806 ms |
| D15-s3-02 | verified | low | hygiene | I4 | worktree runner: rows_diverging_from_cycle_row=48 of 48 (expected 48, reproduced, tf 1.001); verifier: feed_health TypeError, perturbation completes |
| D16-s1-01 | weakened | low | bug | N-step-grid | worktree: clause_grid=50 rig x state rows; null 0; --perturb freq_grid -> 0 |
| D16-s1-02 | weakened | low | bug | N-mode-coupled-write | worktree: cold_tank_charge=2 rigs; --perturb dhw_gate -> 0 |
| D16-s1-03 | weakened | medium | bug | P2 | worktree: boost_indoor_between=2 rigs; perturb -> 0 |
| D16-s1-04 | verified | high | bug | N-unreleased-hold | worktree: baseline_switch_off=5 rigs; perturb -> 0 |
| D16-s1-05 | verified | low | bug | P11 | worktree: unavailable_recorded=5 rigs; null 0; perturb -> 0 |
| D16-s2-01 | weakened | medium | bug | N-stale-step-actuation | worktree: stale share mqtt 0.5732, curve 0.4644, freq 0.4480; leave-one-out drop-most-favourable stays > 0.4 (mqtt LOO 0.41-0.73) |
| D16-s2-02 | weakened | medium | bug | N-stale-step-actuation | worktree: on_in_window=0 of 30 min (long window 59/90); perturb -> 29/30 and 89/90 |
| D16-s2-03 | verified | low | bug | P2 | worktree: cell3530_record_wrong_mode_at_on=1; perturb -> 0; null arm 0 |
| D16-s2-04 | verified | medium | bug | P3 | worktree: min-cold-tank arm k_lift 8.0 -> 30 starts at 0.602 kW measured vs 1.0 booked; partial arm 1 start per run; null power error 0 |
| D16-s3-01 | verified | high | bug | N-unreleased-hold | worktree: on Off select.pump_mode stays at the optimizer's write (1); during disinfection Off leaves number.dhw_set at 60 (1); unrestored_off=5 entities |
| D16-s3-02 | verified | high | bug | N-unreleased-hold | worktree: 4 actuators unregistered on off, unload and remove each (supply switch, frequency, valve, circulation); perturb -> 0 |
| D16-s3-03 | weakened | medium | bug | N-order-coupling | worktree: unload during a held disinfection leaves number.dhw_set at 60 (unrestored 1, baseline 50); --perturb memo -> 0 |
| D16-s3-04 | verified | medium | bug | N-unreleased-hold | worktree: writes_again_off_restore_failed_while_off=0; perturb (retry) -> 1 |
| D17-s1-01 | verified | medium | bug | I4 | planted copy: option_fields_missing=156 of 286; perturb -> 0 |
| D17-s1-02 | verified | high | bug | P2 | planted copy: computed_kept_value_lost=8 of 12 computed rows; null 0; perturb -> 0 |
| D17-s1-03 | verified | medium | bug | P2 | planted copy: two-zone rendered_no_effect=2 incl house_thermal_mass; perturb -> 1 (thermal mass gone) |
| D17-s1-05 | verified | high | bug | N-partial-window-extrapolation | planted copy: guard_wrong_minutes_total=69 over 5 draws (range 3-25, drop-most-favourable 44); perturb -> 0 |
| D17-s2-02 | verified | medium | bug | N-dead-input | planted copy: step0_outdoor_spread_K=0.000 with a forecast; no-forecast null 35 K; perturb -> 35 K, 5.124 kWh |
| D17-s2-03 | verified | medium | bug | P2 | planted copy: quick_path_plan_kwh_spread=0.0000 (LOO 0.0000); the valve-arm reference spreads 11.81 kWh |
| D17-s2-04 | verified | medium | bug | N-dead-input | planted copy: kept_schedule_cap_delta_kW=0.000 (with fraction -2.0); perturb -> -2.0 |
| D17-s2-05 | verified | low | hygiene | N-entry-data-placement | planted copy: entries_with_after_save=2; perturb -> 0 |
| D17-s3-01 | verified | medium | bug | P2 | planted copy: service publishes 0.5 SEK/kWh and no plan, button 2.0 and republishes; perturb -> service 2.0 and republished |
| D17-s3-02 | verified | medium | bug | P2 | planted copy: heat_loss plan_delta=0.000 kW-steps on two-zone (also after restart); perturb -> 167.619 |
| D17-s3-03 | verified | low | bug | N-silent-zero | planted copy: snapshot_bias_is_none=1, restored=1 (scale 1.0); perturb -> restored 0, scale 1.3 |
| D17-s3-51 | verified | low | bug | P2 | verifier: 18 of 336 week half-hours wrong; perturb 18 -> 0; flat null 0; with a solve each day still 16 |
| D2-s1-01 | verified | critical | bug | P2 | planted copy: batch_parity_mismatch_total=14314 elements (dhw 1665, valve 6729, wood 2076, pv 1820 ...); space-only 0 |
| D2-s1-02 | verified | high | bug | P2 | planted copy: batch_parity_mismatch_total=3012 (2z valve arms), maxdiff 1.71 K |
| D2-s1-51 | verified | medium | bug | N-table-value | verifier: 36 of 36 cells derive 1.55x the post-2005 heat loss for 'low energy' |
| D2-s2-02 | verified | high | bug | N-wrong-law | planted copy: duty_law_mismatch=60 of 61 grid points; at duty 0.2 the code gives 1.0 vs documented 0.7 |
| D2-s3-01 | weakened | medium | bug | N-objective-as-money | planted copy: savings_inflation_lambda1_price_risk=12.4574, max 25.0586 currency; perturb -> 0 |
| D2-s3-02 | verified | critical | bug | N-missing-unit-scale | planted copy: unit_mismatches=8; --perturb minor -> 0 |
| D2-s3-03 | verified | high | bug | N-partial-payload-parse | planted copy: tibber_rows_dropped=96, known steps at 14h 40; --perturb tomorrow -> 0 dropped, 96 known |
| D2-s3-04 | verified | high | bug | I4 | planted copy: fee_mismatch_steps=192; --perturb weekday -> 0 |
| D2-s3-05 | verified | high | bug | N-inverted-aggregate | planted copy: tracker_peak_err_max=2.1268 kW; --perturb oneperday -> 0 |
| D2-s3-06 | verified | medium | bug | P2 | planted copy: peak_cost_err_max=41.4976 currency; --perturb topk -> 0.0004 |
| D2-s3-07 | verified | low | bug | P7 | planted copy: coverage_full_23h=1.001346; perturb -> 1.000000; 25 h month 1.000000 |
| D2-s3-08 | verified | medium | bug | N-event-misattribution | planted copy: booked_kwh_long_max=3.0160 kWh (short 0.0389); perturb -> 0 |
| D2-s3-09 | verified | medium | bug | N-confounded-learner | planted copy: narrowing_censored_kw=4.100; uncensored agree 0.000; perturb -> 0 |
| D2-s3-10 | verified | medium | bug | P5 | planted copy: miss rate 0.006 at 0.005 C noise, 0.214 (6 of 28) at 0.02 C, 1.000 (4 of 4) at 0.05 C; --perturb-bar5 -> 0 admitted |
| D2-s3-11 | weakened | low | bug | N-confounded-learner | planted copy: gain_recovery_mean=0.5573 (scale err max 0.060); perturb -> 0.7748, up as stated |
| D3-s2-01 | weakened | low | hygiene | I2 | worktree: a payload.py body edit over-selects 9 scripts (27 over-approximated pairs of 296 claimed) |
| D4-s1-01 | verified | medium | bug | P9 | planted copy: pipe_hit_under_floor=576 of 576 pipes (band 0-5.75 px); null port hits median 30.5 px; perturb stroke 60 -> 296 |
| D4-s1-03 | verified | low | bug | P9 | planted copy: strict_small=72 targets under 24/44 px over 72 score_open renders |
| D4-s2-01 | verified | low | hygiene | I4 | planted copy: unfilled_placeholders_total=8 over 9 fired cells; perturb -> 0 |
| D4-s2-02 | verified | low | hygiene | I4 | planted copy: placeholder_parity_mismatches=1 of 4533 leaf strings; perturb -> 0 |
| D4-s3-01 | weakened | low | hygiene | N-untranslated-splice | planted copy: english_error_lines=24 over 24 non-en error cells; --perturb err_localize -> 0 |
| D4-s3-02 | verified | low | hygiene | P9 | planted copy: tile_row_misaligned=12 of 216 headline rows, max 14 px at phone width; perturb -> 0 |
| D4-s3-03 | verified | low | hygiene | P9 | planted copy: below_floor_cells=78 (7 elements); --perturb tooltip_floor -> 54 (2 elements) |
| D4-s3-04 | verified | low | hygiene | P9 | planted copy: role_colour_split=5; --perturb one_error_colour -> 3 |
| D4-s3-05 | verified | low | hygiene | P9 | planted copy: offscale_font_sizes=14 (spacing 40); --perturb type_tokens -> 10 |
| D4-s3-06 | verified | low | hygiene | N-copy-style | planted copy: en_title_case_titles=6 of 41, sv 3; perturb -> 0 |
| D4-s3-07 | verified | low | hygiene | N-copy-style | planted copy: de_straight_spans=27 vs 95 typographic, en degree without sign 2; --perturb de_quotes -> 2 |
| D4-s2-51 | weakened | low | hygiene | I4 | verifier: 3 languages never render {tibber_info}; tibber_token's description already carries the hint |
| D5-s10-01 | verified | low | hygiene | N-move-stale-path | planted copy: edit_reaches_cursor=0, unguarded_generated=1; perturb -> edit reaches 1 |
| D5-s10-03 | verified | low | hygiene | I5 | planted copy: mismatches=3 (other_items 4 vs claimed 3); perturb -> 1 |
| D5-s10-04 | verified | low | hygiene | N-move-stale-path | planted copy: verdict_false=1 of 15 units (tools/audit/README.md) |
| D5-s10-05 | verified | low | hygiene | N-move-stale-path | planted copy: verdict_false=1 of 3 units (tools/audit/README.md) |
| D5-s10-06 | verified | low | hygiene | I5 | planted copy: verdict_false=1 of 13 units (carry-2065.json) |
| D5-s10-07 | weakened | low | hygiene | N-comment-style | planted copy: long_sentences=339 across the seat's cell files |
| D5-s2-01 | verified | low | hygiene | I5 | planted copy: dup_paragraph=15, menu_twin_drift=14 of 24, dup_fence=4 |
| D5-s2-02 | verified | low | hygiene | N-orphan-doc | planted copy: orphan_doc=1 (docs/CONTRIBUTING.md, inbound 0) |
| D5-s2-03 | verified | low | hygiene | I5 | planted copy: basis_gap_pct=18.9, basis_stated=0 of 5 units; null gap 0.0 |
| D5-s2-04 | verified | low | hygiene | I5 | planted copy: false_units=2 in the cell set (1 in make_model_figures.py); perturb -> 1 |
| D5-s2-05 | verified | low | hygiene | I5 | planted copy: false_units=2 and long_sentences=8 in the cell set; perturb -> 0 and 0 |
| D5-s2-06 | weakened | low | hygiene | N-comment-style | planted copy: long_sentences=8 in the cell set incl 2 in make_card_weekly_figure.mjs (51, 55 words); perturb -> 0 |
| D5-s2-07 | verified | low | hygiene | I2 | planted copy: plant_refused=0 planted_units=0 into README.md; perturb (plant a D5 cell) -> 1 and 1 |
| D5-s2-08 | verified | medium | hygiene | I5 | planted copy: mismatches=7 of 57 pairs; perturb -> 3 |
| D5-s2-09 | verified | low | hygiene | I5 | planted copy: swing_minus_flat=0.000 (doc describes a smooth start term); null 22.0, perturb 23.5 |
| D5-s2-10 | verified | low | hygiene | I5 | planted copy: contradicted=7 of 7 configs; null and perturb 0 |
| D5-s2-11 | verified | low | hygiene | I5 | planted copy: quick_setup_from_end=2, last entry advanced; perturb -> 1, quick_setup last |
| D5-s3-01 | verified | low | hygiene | I5 | planted copy: claimed_but_needs_ha=1 (grid_fee); perturb -> 0 |
| D5-s3-02 | verified | low | hygiene | I5 | planted copy: overshoot_c=0.0 vs the docstring's +1; null and perturb 1.0 |
| D5-s3-03 | weakened | low | hygiene | N-comment-style | planted copy: long_units=363; perturb -> 343 |
| D5-s4-01 | verified | low | hygiene | N-comment-style | planted copy: long_units=558 of 3367 units |
| D5-s4-02 | weakened | low | hygiene | I5 | planted copy: unresolved_units=2 (3 tokens) in sysid.py |
| D5-s5-01 | verified | low | hygiene | I5 | planted copy: false_units[tools/pr/prepr.sh]=3 of 390 units |
| D5-s5-02 | verified | low | hygiene | N-move-stale-path | planted copy: false_units[tools/pr/gh_comment.py]=1 |
| D5-s5-03 | verified | low | hygiene | N-move-stale-path | planted copy: false_units[tools/pr/preflight.sh]=1 |
| D5-s5-04 | verified | low | hygiene | I5 | planted copy: false_units[tools/audit/seat/open_pr.sh]=1 |
| D5-s5-05 | verified | low | hygiene | I5 | planted copy: false_units[tools/audit/seat/merge_train.py]=1 of 689 units |
| D5-s5-06 | weakened | low | hygiene | I5 | planted copy: false_units[tools/audit/seat/orchestrator_tick.py]=1 of 277 units |
| D5-s5-07 | verified | low | hygiene | N-comment-style | planted copy: long_sentences_strict=483 in 60 files (raw 743) |
| D5-s6-01 | verified | low | hygiene | I5 | planted copy: stamp record-class regexes 6 (comment says 3), stamp_py=3 false units; perturb -> 3 and 0 |
| D5-s6-02 | verified | low | hygiene | I5 | planted copy: replay table is tests/replay_cost_draws.tsv (docstring names replay_draws.tsv), 1 false unit; perturb -> 0 |
| D5-s6-03 | verified | low | hygiene | N-move-stale-path | planted copy: row_position usage path exits rc=2, 1 false unit; perturb -> rc 0, 0 |
| D5-s6-04 | verified | low | hygiene | I5 | planted copy: plan_audit end-to-end --target 22.7 exits rc=2, 1 false unit; perturb -> rc 0, 0 |
| D5-s6-05 | verified | low | hygiene | I5 | planted copy: header names updatepr.sh, script is update_pr.sh (1 false unit); perturb -> 0 |
| D5-s6-06 | weakened | low | hygiene | I5 | planted copy: roster_lib_py=3 false units; perturb -> 0 |
| D5-s6-07 | verified | low | hygiene | I5 | planted copy: plan_table_py=1 false unit (gen_table_rev3.py); perturb -> 0 |
| D5-s6-08 | verified | low | hygiene | N-comment-style | planted copy: C5-len=404 over 3781 units |
| D5-s7-01 | verified | low | hygiene | N-comment-style | planted copy: tests/features.py c5_fail=450, c2_fail=3, plus 1 C1 = 454; perturb c2 3 -> 2 |
| D5-s7-02 | verified | low | hygiene | N-comment-style | planted copy: tests/finite_boundary.py c5_fail=14 of 143 units; perturb -> 0 |
| D5-s7-03 | weakened | low | hygiene | N-comment-style | planted copy: tests/frontend.py c5_fail=3 of 24 units; perturb -> 0 |
| D5-s8-01 | verified | low | hygiene | N-move-stale-path | planted copy: tools/policy/policy_lint.mjs units_with_unresolved_ref=12 of 463 |
| D5-s8-02 | verified | low | hygiene | N-move-stale-path | planted copy: tools/policy/friction_issues.mjs unresolved_units=1 of 62 |
| D5-s8-03 | verified | low | hygiene | N-move-stale-path | planted copy: tests/closure.py unresolved_units=5 of 329 |
| D5-s8-04 | verified | low | hygiene | I5 | planted copy: tests/doc_claims.py unresolved_units=3 of 229 |
| D5-s8-05 | verified | low | hygiene | I5 | planted copy: tests/card.mjs unresolved_units=4 of 712 |
| D5-s8-06 | verified | low | hygiene | N-comment-style | planted copy: units_with_sentence_over_40_words=657 of 3628 |
| D5-s8-07 | verified | medium | bug | N-instrument-locator | planted copy: scan_c_like mislocates per file (tests/card.mjs 690, agreement.mjs 49, check-wave-script.mjs 59, ...) over 3099 comment units; verifier total 1175 of 1899 JS units |
| D5-s9-01 | verified | low | hygiene | N-move-stale-path | planted copy: stale_refs=17 in 3 files (14 moved), of which tests/entities.py holds the finder's 13 |
| D5-s9-02 | verified | low | hygiene | N-move-stale-path | planted copy: stale_refs=17 in 3 files, of which tests/run.sh holds the finder's 3 |
| D5-s9-03 | verified | low | hygiene | N-move-stale-path | planted copy: stale_refs=17 in 3 files, of which tests/structure.py holds 1 (tools/audit/README.md) |
| D5-s9-04 | verified | low | hygiene | N-comment-style | planted copy: C5-long=820 sentences; perturb removes the planted unit 1 -> 0 |
| D6-s1-01 | verified | low | hygiene | I5 | planted copy: claims.py false_claims=3 (legionella default 10 days vs doc 7, echo grace const 20 s vs doc 60 s with 6 contradictions, learner converges) |
| D6-s1-02 | verified | medium | hygiene | I5 | planted copy: false_claims include legionella_default (10 vs 7 days) and learner_converges_35pct, the two README rows |
| D6-s2-01 | verified | high | bug | I5 | planted copy: strings rows_claim_false=6, stale 2, across 3 files; perturb -> 0 and 0 |
| D6-s2-02 | verified | low | hygiene | N-move-stale-path | planted copy: gov_paths=2 dangling decision paths, one at dev/governance/roles/fixer.md:104 |
| D6-s2-03 | verified | low | hygiene | N-move-stale-path | planted copy: gov_paths=2 dangling decision paths, one at dev/governance/roles/orchestrator.md:73 |
| D6-s3-01 | verified | low | hygiene | I4 | planted copy: config_refusal_missing=2 placeholders (1 unrenderable unit), options page 0; perturb -> 0 |
| D6-s4-01 | verified | low | hygiene | I4 | planted copy: unresolved_sv=1 ({minuter}), en/de 0; perturb -> 0 |
| D6-s4-02 | verified | low | hygiene | I5 | planted copy: over_text at B=1, 2 and 12 is 1 each (B=0 0); perturb -> 0 |
| D6-s5-01 | verified | low | hygiene | N-move-stale-path | planted copy: c_mock false, mock_users=5 test scripts; fix_review_j5_refs=0 (stale pointer) |
| D6-s5-02 | verified | low | hygiene | N-move-stale-path | planted copy: round4_d6_rewritten_at_doc_path=0 (tools/audit/round4/D6/ absent) |
| D6-s5-03 | verified | low | hygiene | N-move-stale-path | planted copy: c_brief_exclude stale, round2_symbol_found=1 |
| D6-s5-04 | verified | low | hygiene | N-move-stale-path | planted copy: handovers_under_docs=0; the one handover is dev/programme/HANDOVER.md |
| D6-s5-05 | verified | low | hygiene | I5 | planted copy: leased_or_slotted_besides_stress=9 (1 lease, 8 slots) |
| D6-s5-06 | verified | low | hygiene | N-move-stale-path | planted copy: instrument_record_dirs_listed=19, absent from tools/audit/seat/ 19 |
| D6-s5-07 | verified | low | hygiene | I5 | planted copy: worktree_gc_apply_refused=1 |
| D6-s5-08 | verified | low | hygiene | N-move-stale-path | planted copy: event_hub_cited_name_files=0 (the control is r10_livestate_event_hub_writes.py) |
| D6-s6-01 | verified | low | hygiene | I5 | planted copy: de.json false=2, stale=16, false_plus_stale=18; perturb -> 17 |
| D6-s7-01 | verified | low | hygiene | I5 | planted copy: false_rows=4; CI skipped on 21 switches, 3 path classes mismatched (1788 delivery files), base-not-main refused 1 |
| D6-s7-02 | verified | low | hygiene | I5 | planted copy: wrong_rows=9 in the plan's standing sections |
| D7-s1-01 | verified | low | hygiene | N-structure-blind | planted copy: ratchet const_modules_over_50=3; read-count null 4; respell perturbation -> 2 |
| D7-s1-02 | verified | low | hygiene | N-structure-blind | planted copy: holes_clone1=95 files; duplication_copies 18 base vs 113 planted |
| D7-s1-03 | verified | low | hygiene | N-structure-blind | planted copy: unused_package_imports=14; adding one -> 15 with the ratchet unchanged |
| D7-s1-04 | verified | low | hygiene | N-structure-blind | planted copy: coordinator_py_unpriced_loc=2980; module-growth perturbation -> 4403 with ratchet_class_excess_loc flat at 17407 |
| D7-s1-05 | weakened | low | hygiene | N-duplicated-rule | planted copy: duplication_copies -> 9 with the ten prototypes, dS +9.2671 (verifier +8.2671); fold alone 17 |
| D7-s1-06 | verified | low | hygiene | N-leaf-imports-solver | planted copy: layer_violations=13 at the issues cut (11 single-carrier); verifier 13 -> 6 with the seven imports moved |
| D7-s2-01 | verified | medium | bug | N-confounded-learner | planted copy: away intervals ingested by comfort, DHW draws and internal gains (3 of 21 learners); perturb -> 0 |
| D7-s2-02 | weakened | low | bug | P5 | planted copy: biased_admitted=3 (first-order 0); --perturb -> 0 |
| D7-s2-03 | verified | low | bug | N-shared-config | planted copy: holder_torn_fields=2 (reuse divergence 0); --perturb-ctx -> 0 |
| D7-s3-01 | verified | high | bug | P8 | planted copy: temperature_roundtrip_disagreements=12 of 35 probes (55 F written 62.6, read back 17.0); perturb -> 0 |
| D7-s3-03 | verified | medium | bug | N-no-expiry | planted copy: step_covering_now_disagreements=4 of 8 (past steps held at 27.0); perturb -> 0 |
| D7-s3-04 | verified | low | bug | P2 | planted copy: water_heat 1 + naive_instant 2 + finite_number 9 = 12 disagreeing probes; perturb -> 0 |
| D7-s3-05 | verified | low | hygiene | N-structure-blind | planted copy: m6_inner unread params 16, locals 8, fields 1 (+ attributes); planted_delta=1 under --perturb |
| D7-s3-06 | unreproduced | medium | bug | I1 | verifier: 93 of 480 functions deletable with no behaviour script failing; pin demo 0 -> 1 failing under HPO_FN_MUTATE |
| D8-s1-01 | verified | medium | bug | P2 | planted copy: no_dhw_priced=12 of 22 no-DHW pairs; null 0 |
| D8-s1-02 | verified | medium | bug | N-partial-window-extrapolation | planted copy: first_scale=2688 (Feb), swing 1728.39 currency |
| D8-s1-03 | verified | low | bug | P2 | planted copy: avail_none_cycles=1 of 17 |
| D8-s2-02 | weakened | low | hygiene | N-name-sort | planted copy: fam_runs_excess_entity_id_sensor=2 (3 runs); perturb -> 0 |
| D8-s3-01 | verified | medium | bug | N-entity-metadata | planted copy: state_class_impossible=36 (3 accumulators x 6 cells x 2 cycles); perturb -> 0 |
| D9-s1-01 | verified | low | bug | N-solve-recompute | worktree: 2 _multi_start_minimize per diagnose press, 3 worker jobs incl optimize_in_process, 1.05 s process CPU |
| D9-s1-02 | weakened | low | bug | N-unbudgeted-background | worktree: fuse-advisor arm worst cycle 9.44 s host = 47.2 Pi-s at F=5 (B1 60), mean 6.67 s; default arm max 4.05 s; msm per cycle 4 vs 2 |
| D9-s1-03 | verified | medium | bug | N-unbudgeted-background | worktree: K=4 -> 12 worker jobs, scheduled solve latency 12.04x solo; in-flight guard -> 3 jobs, 4.43x |
| D9-s1-04 | verified | low | bug | P10 | worktree: 384 loop simulate_step calls per steady what-if; loop CPU median 19.9 ms host (null arm 11.6 ms) |
| D9-s2-01 | verified | low | bug | N-unbounded-retention | worktree: retained_rows_slope=1448 rows/day (log 476, action 152, seen 628); null 0 |
| D9-s3-01 | weakened | low | bug | I1 | worktree (2400 s re-take): probed_by_gate=6 of 54 scenarios, blind_confined=48, flagged_if_probed=54; traced growth 1.54-3.29x |
| D9-s3-02 | verified | low | hygiene | I1 | worktree: clean arm 2.00 solves/cycle, payload 87816 B, 533 yields/cycle; solves2x arm 4.00 solves/cycle; the stress gate runs no coordinator cycle |
