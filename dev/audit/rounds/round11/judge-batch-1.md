| id | metric | expected | got | reproduced | direction | perturbed | perturbation | void | null_value | load1 | thread_factor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0-s2-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.97 | 1.000 | tree edited by run: dev/audit/rounds/round11/D0/s2/__pycache__/cells.cpython-314.pyc, dev/audit/rounds/round11/D0/s2/__pycache__/race.cpython-314.pyc; restored |
| D0-s3-01 | stripped_earlier_rounds |  | 2 | by-hand | up |  | by-hand |  | by-hand | 0.05 | 1.000 |  |
| D0-s3-02 | universe |  | 120 | by-hand | down |  | by-hand |  | by-hand | 0.13 | 1.000 |  |
| D0-s3-03 | perturb |  | none | by-hand | up |  | by-hand |  | by-hand | 0.99 | 1.000 |  |
| D1-s1-01 | stale_fallback_issues_after_restart | 1, | 1 | no | to_zero |  | by-hand |  | by-hand | 0.14 | 1.181 | tree edited by run: dev/audit/rounds/round11/D1/s1/__pycache__/rl.cpython-314.pyc; restored; re-take: thread_factor > 1.05 |
| D1-s1-03 | rows |  | 29 | by-hand | to_zero |  | by-hand |  | by-hand | 0.09 | 1.019 | tree edited by run: dev/audit/rounds/round11/D1/s1/__pycache__/rl.cpython-314.pyc; restored |
| D1-s1-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D1-s2-01 | nan_boundary_passes | 1 | 0 | no | to_zero |  | by-hand |  | by-hand | 0.47 | 1.000 |  |
| D1-s2-02 | stale_cells_published | 6 | 6 | yes | to_zero |  | by-hand |  | by-hand | 0.05 | 1.011 |  |
| D1-s2-03 | stuck_published_fresh | 5 | 5 | yes | to_zero |  | by-hand |  | by-hand | 1.79 | 1.019 |  |
| D1-s2-04 | consequences | 2. | 2 | yes | to_zero |  | by-hand |  | by-hand | 0.63 | 0.999 |  |
| D1-s2-05 | v1_mutants |  | 200 | by-hand | to_zero |  | by-hand |  | by-hand | 0.99 | 1.000 |  |
| D1-s2-06 | restarts_raising | 8 | 8 | yes | to_zero |  | by-hand |  | by-hand | 0.12 | 1.000 |  |
| D1-s2-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D1-s2-52 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D1-s3-01 | pump_nonfinite_flag_true | 10 | 10 | yes | to_zero |  | by-hand |  | by-hand | 0.21 | 1.000 |  |
| D1-s3-02 | pump_nonfinite_flag_true | 10 |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.16 | 1.000 |  |
| D1-s3-03 | pump_nonfinite_flag_true | 10 |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.28 | 1.000 |  |
| D1-s3-04 | transport_returned_within_cap | 0 | 0 | yes | to_zero |  | by-hand |  | by-hand | 0.40 | 1.881 | re-take: thread_factor > 1.05 |
| D1-s3-05 | persist_silent_at_warning | 10 | 4 | no | down |  | by-hand |  | by-hand | 0.45 | 1.0 |  |
| D1-s3-06 | repeat_error_records | 3 |  | by-hand | to_zero |  | by-hand |  | by-hand | 2.13 |  | rc=1; load1 from batch; no thread_factor |
| D1-s3-07 | silent_broad_no_record | 7 | 3 | no | down |  | by-hand |  | by-hand | 0.77 | 1.0 |  |
| D10-s1-01 | cases |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 0.99 | 1.000 |  |
| D10-s1-02 | sysid_enabled_armed |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.12 | 1.000 |  |
| D10-s1-03 | continue_settings_in_data |  | 41 | by-hand | to_zero |  | by-hand |  | by-hand | 0.13 | 1.000 |  |
| D10-s1-05 | never_stepped_past_triples |  | 49 | by-hand | down |  | by-hand |  | by-hand | 0.99 | 1.000 |  |
| D10-s1-06 | late_files | $late | 0 | no | up |  | by-hand |  | by-hand | 1.13 | 1.0 |  |
| D10-s2-01 | shadowed_null | 0, | 0 | no | to_zero |  | by-hand |  | by-hand | 0.16 | 1.000 |  |
| D10-s2-03 | bad | 2 | 0 | no | up |  | by-hand |  | by-hand | 0.28 | 1.000 |  |
| D10-s2-04 | entities |  | 82 | by-hand | down |  | by-hand |  | by-hand | 0.40 | 1.000 |  |
| D10-s3-01 | cells_examined |  | 115 | by-hand | to_zero |  | by-hand |  | by-hand | 0.45 | 1.000 |  |
| D10-s3-02 | cells_examined |  | 115 | by-hand | to_zero |  | by-hand |  | by-hand | 2.13 | 1.000 |  |
| D11-s1-01 | missed | 2 | 2 | yes | to_zero |  | by-hand |  | by-hand | 0.79 | 1.000 |  |
| D11-s1-02 | unmonitored | 1 | 2 | no | down |  | by-hand |  | by-hand | 0.99 | 1.000 |  |
| D11-s1-03 | control_red_on_drift | 0, | 0 | no | up |  | by-hand |  | by-hand | 0.12 | 1.000 |  |
| D11-s1-04 | baseline_pass |  | 0 | by-hand | up |  | by-hand |  | by-hand | 0.13 | 1.000 |  |
| D11-s1-05 | meters | 8, | 8 | no | to_zero |  | by-hand |  | by-hand | 0.99 | 1.000 |  |
| D11-s1-06 | real_repo_writes_on_selftest | 1 | 1 | yes | to_zero |  | by-hand |  | by-hand | 1.48 | 1.000 |  |
| D11-s2-01 | window_prs |  | 52 | by-hand | down |  | by-hand |  | by-hand | 0.16 | 1.001 |  |
| D11-s2-02 | window_prs |  | 52 | by-hand | up |  | by-hand |  | by-hand | 0.28 | 1.000 |  |
| D11-s2-03 | releases |  | 5 | by-hand | up |  | by-hand |  | by-hand | 0.53 | 1.000 |  |
| D11-s2-04 | corpus_files |  | 86 | by-hand | to_zero |  | by-hand |  | by-hand | 0.45 | 1.000 |  |
| D11-s3-02 | null_total |  | 0 | by-hand | up |  | by-hand |  | by-hand | 2.56 | 1.000 |  |
| D11-s3-03 | null_rc |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 0.96 | 1.000 |  |
| D11-s3-04 | null_passed |  | 570 | by-hand | up |  | by-hand |  | by-hand | 2.82 | 1.397 | re-take: thread_factor > 1.05 |
| D12-s1-01 | arm |  | baseline | by-hand | to_zero |  | by-hand |  | by-hand | 0.42 | 1.000 | tree edited by run: dev/audit/rounds/round11/D12/s1/__pycache__/cells.cpython-314.pyc; restored |
| D12-s2-01 | single_zone_cells |  | 47 | by-hand | to_zero |  | by-hand |  | by-hand | 0.68 | 1.000 | tree edited by run: dev/audit/rounds/round11/D12/s2/__pycache__/cells.cpython-314.pyc; restored |
| D12-s3-01 | grid_cells |  | 10 | by-hand | to_zero |  | by-hand |  | by-hand | 0.95 | 1.000 | tree edited by run: dev/audit/rounds/round11/D12/s3/__pycache__/surfaces.cpython-314.pyc; restored |
| D12-s3-02 | arm |  | baseline | by-hand | to_zero |  | by-hand |  | by-hand | 1.32 | 1.000 | tree edited by run: dev/audit/rounds/round11/D12/s3/__pycache__/surfaces.cpython-314.pyc; restored |
| D12-s3-03 | arm |  | sees_dhw+no_mode+dhw_timer | by-hand | to_zero |  | by-hand |  | by-hand | 0.21 | 1.000 | tree edited by run: dev/audit/rounds/round11/D12/s3/__pycache__/surfaces.cpython-314.pyc; restored |
| D13-s2-01 | class_harness |  | 7 | by-hand | down |  | by-hand |  | by-hand | 0.28 | 1.00 |  |
| D13-s2-02 | accepted_entries |  | 174 | by-hand | down |  | by-hand |  | by-hand | 0.53 | 1.00 |  |
| D14-s1-01 | option_number_fields |  | 94 | by-hand | to_zero |  | by-hand |  | by-hand | 0.45 | 1.000 |  |
| D14-s1-02 | seams_baseline | 1 | 1 | yes | up |  | by-hand |  | by-hand | 2.22 | 1.000 |  |
| D14-s1-03 | instance |  | SEK | by-hand | to_zero |  | by-hand |  | by-hand | 0.96 | 1.000 |  |
| D14-s2-01 | quiet_stale_flags | 6, | 6 | no | to_zero |  | by-hand |  | by-hand | 2.82 | 1.000 |  |
| D14-s2-02 | wind_mismatch_hours | 72 | 72 | yes | to_zero |  | by-hand |  | by-hand | 0.42 | 1.000 |  |
| D14-s2-03 | counted_warning | 1, | 1 | no | up |  | by-hand |  | by-hand | 0.71 | 1.000 |  |
| D15-s1-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.95 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-03 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 1.32 |  | rc=127; load1 from batch; no thread_factor |
| D15-s1-04 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 0.21 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-05 | fold_written |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.28 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.53 |  | rc=2; load1 from batch; no thread_factor |
| D15-s2-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.45 |  | rc=2; load1 from batch; no thread_factor |
| D15-s2-03 | cycles |  | 96 | by-hand | up |  | by-hand |  | by-hand | 1.95 | 1.001 |  |
| D15-s2-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.96 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 2.82 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-06 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.42 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-07 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.71 |  | rc=1; load1 from batch; no thread_factor |
| D15-s3-01 | solver_spread_unsolved_rows | 10 |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.95 |  | rc=1; load1 from batch; no thread_factor |
| D15-s3-02 | rows_diverging_from_cycle_row | 48 | 48 | yes | to_zero |  | by-hand |  | by-hand | 1.27 | 1.001 |  |
| D16-s1-01 | cells | 532, | 532 | no | to_zero |  | by-hand |  | by-hand | 0.33 | 1.000 |  |
| D16-s1-02 | cells | 532, | 532 | no | to_zero |  | by-hand |  | by-hand | 0.47 | 1.000 |  |
| D16-s1-03 | cells | 532, | 532 | no | to_zero |  | by-hand |  | by-hand | 0.61 | 1.000 |  |
| D16-s1-04 | cells | 532, | 532 | no | to_zero |  | by-hand |  | by-hand | 0.53 | 1.000 |  |
| D16-s1-05 | cells | 532, | 532 | no | to_zero |  | by-hand |  | by-hand | 1.80 | 1.000 |  |
| D16-s2-01 | stale_share_supply | 0, | 0.0000 | no | to_zero |  | by-hand |  | by-hand | 0.96 | 1.000 | tree edited by run: dev/audit/rounds/round11/D16/s2/__pycache__/rig.cpython-314.pyc; restored |
| D16-s2-02 | on_in_window |  | 0 | by-hand | up |  | by-hand |  | by-hand | 2.67 | 1.000 | tree edited by run: dev/audit/rounds/round11/D16/s2/__pycache__/cells.cpython-314.pyc, dev/audit/rounds/round11/D16/s2/__pycache__/effect.cpython-314.pyc, dev/audit/rounds/round11/D16/s2/__pycache__/rig.cpython-314.pyc, dev/audit/rounds/round11/D16/s2/__pycache__/timing.cpython-314.pyc; restored |
| D16-s2-03 | stale_share_supply | 0, | 0.0000 | no | to_zero |  | by-hand |  | by-hand | 0.47 | 1.000 | tree edited by run: dev/audit/rounds/round11/D16/s2/__pycache__/rig.cpython-314.pyc; restored |
| D16-s2-04 | partial_abs_power_error_mean |  | 0.0788 | by-hand | down |  | by-hand |  | by-hand | 0.73 | 1.000 | tree edited by run: dev/audit/rounds/round11/D16/s2/__pycache__/rig.cpython-314.pyc, dev/audit/rounds/round11/D16/s2/__pycache__/timing.cpython-314.pyc; restored |
| D16-s3-01 | unrestored_off | 5 | 5 | yes | to_zero |  | by-hand |  | by-hand | 0.95 | 1.000 |  |
| D16-s3-02 | unrestored_off | 5 | 5 | yes | to_zero |  | by-hand |  | by-hand | 1.27 | 1.000 |  |
| D16-s3-03 | unrestored_off | 5 | 5 | yes | to_zero |  | by-hand |  | by-hand | 0.33 | 1.000 |  |
| D16-s3-04 | writes_again_off_restore_failed_while_off | 0 | 0 | yes | up |  | by-hand |  | by-hand | 0.47 | 1.000 | tree edited by run: dev/audit/rounds/round11/D16/s3/__pycache__/m6_restore.cpython-314.pyc; restored |
| D17-s1-01 | option_fields_missing | 156 | 156 | yes | to_zero |  | by-hand |  | by-hand | 0.60546875 | 1.0 |  |
| D17-s1-02 | computed_rows | 12, | 12 | no | to_zero |  | by-hand |  | by-hand | 0.5322265625 | 1.0 | tree edited by run: dev/audit/rounds/round11/D17/s1/__pycache__/rig.cpython-314.pyc; restored |
| D17-s1-03 | two_zone_rendered | 8, | 8 | no | to_zero |  | by-hand |  | by-hand | 1.37060546875 | 1.0 | tree edited by run: dev/audit/rounds/round11/D17/s1/__pycache__/rig.cpython-314.pyc; restored |
| D17-s1-05 | guard_wrong_minutes_total | 69 | 0 | no | to_zero |  | by-hand |  | by-hand | 0.95947265625 | 1.0 | tree edited by run: dev/audit/rounds/round11/D17/s1/__pycache__/rig.cpython-314.pyc; restored |
| D17-s2-02 | step0_outdoor_spread_K | 0.0 | 0.000 | by-hand | up |  | by-hand |  | by-hand | 2.54 | 1.00 | tree edited by run: dev/audit/rounds/round11/D17/s2/__pycache__/rig.cpython-314.pyc; restored |
| D17-s2-03 | quick_path_plan_kwh_spread | 0.0 | 0.0000 | by-hand | up |  | by-hand |  | by-hand | 0.97 | 1.00 | tree edited by run: dev/audit/rounds/round11/D17/s2/__pycache__/rig.cpython-314.pyc; restored |
| D17-s2-04 | kept_schedule_cap_delta_kW | 0.00 | 0.000 | by-hand | down |  | by-hand |  | by-hand | 0.73 | 1.00 | tree edited by run: dev/audit/rounds/round11/D17/s2/__pycache__/rig.cpython-314.pyc; restored |
| D17-s2-05 | entries_with_after_save |  | 2 | by-hand | to_zero |  | by-hand |  | by-hand | 0.95 | 1.00 | tree edited by run: dev/audit/rounds/round11/D17/s2/__pycache__/rig.cpython-314.pyc, dev/audit/rounds/round11/D17/s2/__pycache__/silent_prefill.cpython-314.pyc; restored |
| D17-s3-01 | service_published_price | 0.5, | 0.5 | no | up |  | by-hand |  | by-hand | 1.25 | 1.000 | tree edited by run: dev/audit/rounds/round11/D17/s3/__pycache__/rig.cpython-314.pyc; restored |
| D17-s3-02 | two_zone_inert_cells |  | 2 | by-hand | up |  | by-hand |  | by-hand | 0.63 | 1.000 | tree edited by run: dev/audit/rounds/round11/D17/s3/__pycache__/rig.cpython-314.pyc; restored |
| D17-s3-03 | snapshots_in_ring |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.51 | 1.000 | tree edited by run: dev/audit/rounds/round11/D17/s3/__pycache__/rig.cpython-314.pyc; restored |
| D17-s3-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D2-s1-01 | batch_parity_mismatch_total |  | 0 | by-hand | down |  | by-hand |  | by-hand | 0.53 | 1.0 | tree edited by run: dev/audit/rounds/round11/D2/s1/__pycache__/_common.cpython-314.pyc; restored |
| D2-s1-02 | batch_parity_mismatch_total |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 1.37 | 1.0 | tree edited by run: dev/audit/rounds/round11/D2/s1/__pycache__/_common.cpython-314.pyc; restored |
| D2-s1-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D2-s2-02 | duty_law_mismatch |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 2.53955078125 | 1.0 | tree edited by run: dev/audit/rounds/round11/D2/s2/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-01 | savings_inflation_max |  | 30.8631 | by-hand | to_zero |  | by-hand |  | by-hand | 0.97 | 1.0041 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-02 | fold_err_max |  | 8.882e-16 | by-hand | to_zero |  | by-hand |  | by-hand | 0.90 | 1.0003 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-03 | fold_err_max |  | 8.882e-16 | by-hand | to_zero |  | by-hand |  | by-hand | 0.97 | 1.0003 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-04 | fold_err_max |  | 8.882e-16 | by-hand | to_zero |  | by-hand |  | by-hand | 1.18 | 1.0003 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-05 | fold_err_max |  | 8.882e-16 | by-hand | to_zero |  | by-hand |  | by-hand | 0.74 | 1.0003 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-06 | fold_err_max |  | 8.882e-16 | by-hand | to_zero |  | by-hand |  | by-hand | 0.65 | 1.0003 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-07 | fold_err_max |  | 8.882e-16 | by-hand | down |  | by-hand |  | by-hand | 0.72 | 1.0005 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-08 | booked_kwh_long_max |  | 3.0160 | by-hand | to_zero |  | by-hand |  | by-hand | 0.53 | 1.0000 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-09 | narrowing_censored_kw |  | 4.100 | by-hand | to_zero |  | by-hand |  | by-hand | 1.37 | 1.0000 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-10 | drifting_admitted |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 1.02 | 1.0000 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D2-s3-11 | gain_recovery_mean |  | 0.5573 | by-hand | up |  | by-hand |  | by-hand | 2.42 | 1.0000 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D3-s2-01 | claimed_pairs |  | 296 | by-hand | down |  | by-hand |  | by-hand | 0.97 | 1.00 | tree edited by run: dev/audit/rounds/round11/D3/s2/__pycache__/enumerate.cpython-314.pyc; restored |
| D4-s1-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.90 |  | rc=1; load1 from batch; no thread_factor |
| D4-s1-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.97 |  | rc=1; load1 from batch; no thread_factor |
| D4-s2-01 | unfilled_placeholders_total | 8 | 8 | yes | to_zero |  | by-hand |  | by-hand | 1.18 | 1.000 |  |
| D4-s2-02 | leaf_strings_compared |  | 4569 | by-hand | to_zero |  | by-hand |  | by-hand | 0.74 | 1.000 |  |
| D4-s3-01 | cells |  | 36 | by-hand | to_zero |  | by-hand |  | by-hand | 0.66 | 1.00 |  |
| D4-s3-02 | cells |  | 108 | by-hand | to_zero |  | by-hand |  | by-hand | 0.45 | 1.00 |  |
| D4-s3-03 | cells |  | 108 | by-hand | down |  | by-hand |  | by-hand | 1.15 | 1.00 |  |
| D4-s3-04 | cells |  | 180 | by-hand | down |  | by-hand |  | by-hand | 1.21 | 1.00 |  |
| D4-s3-05 | cells |  | 180 | by-hand | down |  | by-hand |  | by-hand | 1.58 | 1.00 |  |
| D4-s3-06 | en_page_titles |  | 42 | by-hand | to_zero |  | by-hand |  | by-hand | 0.97 | 1.00 |  |
| D4-s3-07 | en_page_titles |  | 42 | by-hand | down |  | by-hand |  | by-hand | 0.90 | 1.00 |  |
| D4-s2-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D5-s10-01 | named_source | .claude/rules/, | .claude/rules/ | no | up |  | by-hand |  | by-hand | 0.97 | 1.000 |  |
| D5-s10-03 | report_lines |  | 7 | by-hand | down |  | by-hand |  | by-hand | 1.16 | 1.000 |  |
| D5-s10-04 | units | 1794, | 15 | no | down |  | by-hand |  | by-hand | 0.74 | 1.000 |  |
| D5-s10-05 | units | 1794, | 3 | no | down |  | by-hand |  | by-hand | 0.65 | 1.000 |  |
| D5-s10-06 | units | 1794, | 13 | no | down |  | by-hand |  | by-hand | 0.66 | 1.000 |  |
| D5-s10-07 | units | 1794, | 1800 | by-hand | down |  | by-hand |  | by-hand | 0.49 | 1.000 |  |
| D5-s2-01 | menu_rows_readme |  | 25 | by-hand | down |  | by-hand |  | by-hand | 1.15 | 1.000 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/structure_fails.json; restored |
| D5-s2-02 | menu_rows_readme |  | 25 | by-hand | to_zero |  | by-hand |  | by-hand | 1.21 | 1.000 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/structure_fails.json; restored |
| D5-s2-03 | lower_floor_ratio |  | 1.4 | by-hand | up |  | by-hand |  | by-hand | 1.58 | 1.000 |  |
| D5-s2-04 | units |  | 75 | by-hand | down |  | by-hand |  | by-hand | 0.97 | 1.000 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/m4_ledger.tsv; restored |
| D5-s2-05 | units |  | 75 | by-hand | to_zero |  | by-hand |  | by-hand | 0.90 | 1.000 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/m4_ledger.tsv; restored |
| D5-s2-06 | units |  | 75 | by-hand | to_zero |  | by-hand |  | by-hand | 0.97 | 1.000 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/m4_ledger.tsv; restored |
| D5-s2-07 | first_file |  | README.md | by-hand | up |  | by-hand |  | by-hand | 1.16 | 1.000 |  |
| D5-s2-08 | pairs |  | 57 | by-hand | down |  | by-hand |  | by-hand | 0.74 | 1.000 |  |
| D5-s2-09 | start_cost_swing |  | 0.000 | by-hand | up |  | by-hand |  | by-hand | 0.65 | 1.000 |  |
| D5-s2-10 | configurations |  | 7 | by-hand | to_zero |  | by-hand |  | by-hand | 0.66 | 1.000 |  |
| D5-s2-11 | menu_entries |  | 9 | by-hand | down |  | by-hand |  | by-hand | 0.49 | 1.000 |  |
| D5-s3-01 | claimed | 11, | 11 | no | to_zero |  | by-hand |  | by-hand | 1.15 | 0.489 |  |
| D5-s3-02 | overshoot_c | 0.0, | 0.0 | no | to_zero |  | by-hand |  | by-hand | 1.21 | 0.004 |  |
| D5-s3-03 | units | 2855, | 2862 | no | down |  | by-hand |  | by-hand | 1.53 | 1.000 |  |
| D5-s4-01 | units |  | 3374 | by-hand | down |  | by-hand |  | by-hand | 0.97 | 1.000 |  |
| D5-s4-02 | units |  | 143 | by-hand | down |  | by-hand |  | by-hand | 0.91 | 1.000 |  |
| D5-s5-01 | false_units_total |  | 3 | by-hand | to_zero |  | by-hand |  | by-hand | 0.98 | 1.000 |  |
| D5-s5-02 | false_units_total |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 1.14 | 1.000 |  |
| D5-s5-03 | false_units_total |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.79 | 1.000 |  |
| D5-s5-04 | false_units_total |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.73 | 1.000 |  |
| D5-s5-05 | false_units_total |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.73 | 1.000 |  |
| D5-s5-06 | false_units_total |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.60 | 1.000 |  |
| D5-s5-07 | false_units_total |  | 8 | by-hand | down |  | by-hand |  | by-hand | 1.11 | 1.000 | tree edited by run: dev/audit/rounds/round11/D5/s5/examined_by_file.tsv, dev/audit/rounds/round11/D5/s5/ledger.tsv, dev/audit/rounds/round11/D5/s5/long_sentences.tsv; restored |
| D5-s6-01 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 1.21 | 1.00 |  |
| D5-s6-02 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 1.53 | 1.00 |  |
| D5-s6-03 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 0.97 | 1.00 |  |
| D5-s6-04 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 0.91 | 1.00 |  |
| D5-s6-05 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 0.98 | 1.00 |  |
| D5-s6-06 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 1.13 | 1.00 |  |
| D5-s6-07 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 0.79 | 1.00 |  |
| D5-s6-08 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.73 |  | rc=1; load1 from batch; no thread_factor |
| D5-s7-01 | code_names |  | 87690 | by-hand | down |  | by-hand |  | by-hand | 0.81 | 0.997 | tree edited by run: dev/audit/rounds/round11/D5/s7/detail.tsv, dev/audit/rounds/round11/D5/s7/ledger.tsv; restored |
| D5-s7-02 | code_names |  | 87690 | by-hand | to_zero |  | by-hand |  | by-hand | 0.72 | 0.997 | tree edited by run: dev/audit/rounds/round11/D5/s7/detail.tsv, dev/audit/rounds/round11/D5/s7/ledger.tsv; restored |
| D5-s7-03 | code_names |  | 87690 | by-hand | to_zero |  | by-hand |  | by-hand | 1.08 | 0.997 | tree edited by run: dev/audit/rounds/round11/D5/s7/detail.tsv, dev/audit/rounds/round11/D5/s7/ledger.tsv; restored |
| D5-s8-01 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 1.21 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-02 | units | 3628, |  | by-hand | to_zero |  | by-hand |  | by-hand | 1.53 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-03 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 0.97 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-04 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 0.91 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-05 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 0.98 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-06 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 1.13 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-07 | comment_units | 3099, | 3106 | no | to_zero |  | by-hand |  | by-hand | 0.79 | 1.000 |  |
| D5-s9-01 | stale_refs | 17 | 18 | no | to_zero |  | by-hand |  | by-hand | 0.75 | 1.000 |  |
| D5-s9-02 | stale_refs | 17 | 18 | no | to_zero |  | by-hand |  | by-hand | 0.83 | 1.000 |  |
| D5-s9-03 | stale_refs | 17 | 18 | no | to_zero |  | by-hand |  | by-hand | 0.74 | 1.000 |  |
| D5-s9-04 | units | 3748 | 3748 | yes | down |  | by-hand |  | by-hand | 1.04 | 1.000 |  |
| D6-s1-01 | false_rows_total | <n> |  | by-hand | to_zero |  | by-hand |  | by-hand | 1.21 |  | rc=1; load1 from batch; no thread_factor |
| D6-s1-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 1.53 |  | rc=1; load1 from batch; no thread_factor |
| D6-s2-01 | rows_claim_stale |  | 2 | by-hand | to_zero |  | by-hand |  | by-hand | 0.98 | 1.000 | tree edited by run: dev/audit/rounds/round11/D6/s2/__pycache__/probes.cpython-314.pyc, dev/audit/rounds/round11/D6/s2/ledger.tsv; restored |
| D6-s2-02 | gov_paths |  | 2 | by-hand | to_zero |  | by-hand |  | by-hand | 0.91 | 1.000 |  |
| D6-s2-03 | gov_paths |  | 2 | by-hand | to_zero |  | by-hand |  | by-hand | 0.98 | 1.000 |  |
| D6-s3-01 | config_refusal_missing | 2 | 2 | yes | to_zero |  | by-hand |  | by-hand | 1.13 | 1.000 |  |
| D6-s4-01 | unresolved_en |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 0.79 | 1.000 |  |
| D6-s4-02 | plan_writes_B0 |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 0.75 | 1.000 |  |
| D6-s5-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.83 |  | rc=2; load1 from batch; no thread_factor |
| D6-s5-02 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 0.74 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 1.04 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-04 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 1.21 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 1.53 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-06 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.98 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-07 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.91 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-08 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 0.98 |  | rc=1; load1 from batch; no thread_factor |
| D6-s6-01 | false_plus_stale | 18 | 18 | yes | down |  | by-hand |  | by-hand | 1.13 | 1.000 | tree edited by run: dev/audit/rounds/round11/D6/s6/__pycache__/checks.cpython-314.pyc, dev/audit/rounds/round11/D6/s6/__pycache__/facts.cpython-314.pyc, dev/audit/rounds/round11/D6/s6/ledger.tsv; restored |
| D6-s7-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.79 |  | rc=2; load1 from batch; no thread_factor |
| D6-s7-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.75 |  | rc=2; load1 from batch; no thread_factor |
| D7-s1-01 | perturbation |  | none | by-hand | up |  | by-hand |  | by-hand | 0.90 | 1.00 |  |
| D7-s1-02 | perturbation |  | none | by-hand | to_zero |  | by-hand |  | by-hand | 0.99 | 1.00 |  |
| D7-s1-03 | perturbation |  | none | by-hand | up |  | by-hand |  | by-hand | 1.02 | 1.00 |  |
| D7-s1-04 | perturbation |  | none | by-hand | up |  | by-hand |  | by-hand | 1.13 | 1.00 |  |
| D7-s1-05 | counters_ablated |  | none | by-hand | to_zero |  | by-hand |  | by-hand | 1.18 | 1.00 |  |
| D7-s1-06 | counters_ablated |  | none | by-hand | down |  | by-hand |  | by-hand | 0.99 | 1.00 |  |
| D7-s2-01 | ingest_comfort_away |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.91 | 1.000 | tree edited by run: dev/audit/rounds/round11/D7/s2/__pycache__/enum_m3.cpython-314.pyc; restored |
| D7-s2-02 | ua_bias_2state_heavy_old_told_s0 |  | +0.0065 | by-hand | to_zero |  | by-hand |  | by-hand | 0.98 | 1.000 |  |
| D7-s2-03 | reuse_pairs |  | 5 | by-hand | to_zero |  | by-hand |  | by-hand | 1.05 | 1.000 |  |
| D7-s3-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.79 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.75 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.90 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.99 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-06 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 1.02 |  | rc=2; load1 from batch; no thread_factor |
| D8-s1-01 | no_dhw_pairs |  | 22 | by-hand | to_zero |  | by-hand |  | by-hand | 1.08 | 1.000 |  |
| D8-s1-02 | avail_none_cycles |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 1.15 | 1.000 |  |
| D8-s1-03 | avail_none_cycles |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.92 | 1.000 |  |
| D8-s2-02 | fam_runs_excess_entity_id_sensor |  | 2 | by-hand | to_zero |  | by-hand |  | by-hand | 0.91 | 1.000 |  |
| D8-s3-01 | triples |  | 984 | by-hand | to_zero |  | by-hand |  | by-hand | 0.98 | 1.000 |  |
| D9-s1-01 | cells |  | 5 | by-hand | to_zero |  | by-hand |  | by-hand | 1.0166 | 1 | tree edited by run: dev/audit/rounds/round11/D9/s1/__pycache__/d9s1lib.cpython-314.pyc; restored |
| D9-s1-02 | reference_solve_cpu_ms |  | 24.7506 | by-hand | down |  | by-hand |  | by-hand | 0.98877 | 1 | tree edited by run: dev/audit/rounds/round11/D9/s1/__pycache__/d9s1lib.cpython-314.pyc; restored |
| D9-s1-03 | reference_solve_cpu_ms |  | 26.1489 | by-hand | down |  | by-hand |  | by-hand | 0.844727 | 1.00001 | tree edited by run: dev/audit/rounds/round11/D9/s1/__pycache__/d9s1lib.cpython-314.pyc; restored |
| D9-s1-04 | load1_start |  | 0.895996 | by-hand | to_zero |  | by-hand |  | by-hand | 0.99707 | 1.00001 | tree edited by run: dev/audit/rounds/round11/D9/s1/__pycache__/d9s1lib.cpython-314.pyc; restored |
| D9-s2-01 | retained_rows_slope |  | 1448.0 | by-hand | down |  | by-hand |  | by-hand | 0.99 | 1.000 |  |
| D9-s3-01 | universe |  | 54 | by-hand | down |  | by-hand |  | by-hand | 2.02 | 1.047 |  |
| D9-s3-02 | clean_solves_per_cycle |  | 2.00 | by-hand | up |  | by-hand |  | by-hand | 1.00 | 1.000 |  |
