| id | metric | expected | got | reproduced | direction | perturbed | perturbation | void | null_value | load1 | thread_factor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0-s2-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 200.81 |  | rc=127; load1 from batch; no thread_factor |
| D0-s3-01 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 200.81 |  | rc=127; load1 from batch; no thread_factor |
| D0-s3-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 200.81 |  | rc=127; load1 from batch; no thread_factor |
| D0-s3-03 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 200.81 |  | rc=127; load1 from batch; no thread_factor |
| D1-s1-01 | stale_fallback_issues_after_restart | 1, | 1 | no | to_zero |  | by-hand |  | by-hand | 204.59 | 1.019 |  |
| D1-s1-03 | rows |  | 29 | by-hand | to_zero |  | by-hand |  | by-hand | 185.08 | 1.014 |  |
| D1-s1-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D1-s2-01 | nan_boundary_passes | 1 | 0 | no | to_zero |  | by-hand |  | by-hand | 190.48 | 1.000 |  |
| D1-s2-02 | stale_cells_published | 6 | 6 | yes | to_zero |  | by-hand |  | by-hand | 192.36 | 1.001 |  |
| D1-s2-03 | stuck_published_fresh | 5 | 5 | yes | to_zero |  | by-hand |  | by-hand | 194.09 | 1.000 |  |
| D1-s2-04 | consequences | 2. | 2 | yes | to_zero |  | by-hand |  | by-hand | 194.09 | 0.999 |  |
| D1-s2-05 | v1_mutants |  | 200 | by-hand | to_zero |  | by-hand |  | by-hand | 233.04 | 1.000 |  |
| D1-s2-06 | restarts_raising | 8 | 8 | yes | to_zero |  | by-hand |  | by-hand | 236.66 | 1.000 |  |
| D1-s2-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D1-s2-52 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D1-s3-01 | pump_nonfinite_flag_true | 10 | 10 | yes | to_zero |  | by-hand |  | by-hand | 238.48 | 1.000 |  |
| D1-s3-02 | pump_nonfinite_flag_true | 10 |  | by-hand | to_zero |  | by-hand |  | by-hand | 238.48 | 1.000 |  |
| D1-s3-03 | pump_nonfinite_flag_true | 10 |  | by-hand | to_zero |  | by-hand |  | by-hand | 232.40 | 1.000 |  |
| D1-s3-04 | transport_returned_within_cap | 0 | 0 | yes | to_zero |  | by-hand |  | by-hand | 228.67 | 1.711 | re-take: thread_factor > 1.05 |
| D1-s3-05 | persist_silent_at_warning | 10 | 4 | no | down |  | by-hand |  | by-hand | 253.85 | 1.0 |  |
| D1-s3-06 | repeat_error_records | 3 |  | by-hand | to_zero |  | by-hand |  | by-hand | 260.56 |  | rc=1; load1 from batch; no thread_factor |
| D1-s3-07 | silent_broad_no_record | 7 | 3 | no | down |  | by-hand |  | by-hand | 254.80 | 1.0 |  |
| D10-s1-01 | cases |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 254.80 | 1.000 |  |
| D10-s1-02 | sysid_enabled_armed |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 254.90 | 1.000 |  |
| D10-s1-03 | continue_settings_in_data |  | 41 | by-hand | to_zero |  | by-hand |  | by-hand | 254.90 | 1.000 |  |
| D10-s1-05 | never_stepped_past_triples |  | 49 | by-hand | down |  | by-hand |  | by-hand | 241.19 | 1.000 |  |
| D10-s1-06 | late_files | $late |  | by-hand | up |  | by-hand |  | by-hand | 244.42 |  | rc=timeout; load1 from batch; no thread_factor |
| D10-s2-01 | shadowed_null | 0, | 0 | no | to_zero |  | by-hand |  | by-hand | 244.42 | 0.999 |  |
| D10-s2-03 | bad | 2 | 0 | no | up |  | by-hand |  | by-hand | 242.06 | 0.999 |  |
| D10-s2-04 | entities |  | 82 | by-hand | down |  | by-hand |  | by-hand | 241.01 | 0.999 |  |
| D10-s3-01 | cells_examined |  | 115 | by-hand | to_zero |  | by-hand |  | by-hand | 240.45 | 1.000 |  |
| D10-s3-02 | cells_examined |  | 115 | by-hand | to_zero |  | by-hand |  | by-hand | 240.45 | 1.000 |  |
| D11-s1-01 | missed | 2 |  | by-hand | to_zero |  | by-hand |  | by-hand | 240.45 |  | rc=127; load1 from batch; no thread_factor |
| D11-s1-02 | unmonitored | 1 | 2 | no | down |  | by-hand |  | by-hand | 239.61 | 1.000 |  |
| D11-s1-03 | control_red_on_drift | 0, |  | by-hand | up |  | by-hand |  | by-hand | 239.61 |  | rc=127; load1 from batch; no thread_factor |
| D11-s1-04 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 239.61 |  | rc=127; load1 from batch; no thread_factor |
| D11-s1-05 | meters | 8, |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.61 |  | rc=127; load1 from batch; no thread_factor |
| D11-s1-06 | real_repo_writes_on_selftest | 1 |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.61 |  | rc=127; load1 from batch; no thread_factor |
| D11-s2-01 | window_prs |  | 52 | by-hand | down |  | by-hand |  | by-hand | 239.61 | 1.007 |  |
| D11-s2-02 | window_prs |  | 52 | by-hand | up |  | by-hand |  | by-hand | 239.61 | 1.005 |  |
| D11-s2-03 | releases |  | 5 | by-hand | up |  | by-hand |  | by-hand | 239.73 | 1.000 |  |
| D11-s2-04 | corpus_files |  | 86 | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 | 1.000 |  |
| D11-s3-02 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D11-s3-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D11-s3-04 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D12-s1-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D12-s2-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D12-s3-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D12-s3-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D12-s3-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D13-s2-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D13-s2-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D14-s1-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D14-s1-02 | seams_baseline | 1 |  | by-hand | up |  | by-hand |  | by-hand | 239.51 |  | rc=127; load1 from batch; no thread_factor |
| D14-s1-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 239.31 |  | rc=127; load1 from batch; no thread_factor |
| D14-s2-01 | quiet_stale_flags | 6, | 6 | no | to_zero |  | by-hand |  | by-hand | 239.31 | 1.000 |  |
| D14-s2-02 | wind_mismatch_hours | 72 | 72 | yes | to_zero |  | by-hand |  | by-hand | 240.32 | 1.000 |  |
| D14-s2-03 | counted_warning | 1, | 1 | no | up |  | by-hand |  | by-hand | 242.11 | 1.000 |  |
| D15-s1-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 242.02 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-03 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 242.02 |  | rc=127; load1 from batch; no thread_factor |
| D15-s1-04 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 242.02 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-05 | fold_written |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 242.02 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 242.02 |  | rc=2; load1 from batch; no thread_factor |
| D15-s2-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 242.02 |  | rc=2; load1 from batch; no thread_factor |
| D15-s2-03 | cycles |  | 96 | by-hand | up |  | by-hand |  | by-hand | 245.18 | 1.000 |  |
| D15-s2-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 245.18 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 245.18 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-06 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 245.18 |  | rc=1; load1 from batch; no thread_factor |
| D15-s2-07 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 245.18 |  | rc=1; load1 from batch; no thread_factor |
| D15-s3-01 | solver_spread_unsolved_rows | 10 |  | by-hand | to_zero |  | by-hand |  | by-hand | 245.18 |  | rc=1; load1 from batch; no thread_factor |
| D15-s3-02 | rows_diverging_from_cycle_row | 48 | 48 | yes | to_zero |  | by-hand |  | by-hand | 246.72 | 1.0 |  |
| D16-s1-01 | cells | 532, |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s1-02 | cells | 532, |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s1-03 | cells | 532, |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s1-04 | cells | 532, |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s1-05 | cells | 532, |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s2-01 | stale_share_supply | 0, |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s2-02 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s2-03 | stale_share_supply | 0, |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s2-04 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s3-01 | unrestored_off | 5 |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s3-02 | unrestored_off | 5 |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s3-03 | unrestored_off | 5 |  | by-hand | to_zero |  | by-hand |  | by-hand | 246.72 |  | rc=127; load1 from batch; no thread_factor |
| D16-s3-04 | writes_again_off_restore_failed_while_off | 0 |  | by-hand | up |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s1-01 | option_fields_missing | 156 | 156 | yes | to_zero |  | by-hand |  | by-hand | 247.8662109375 | 1.0 |  |
| D17-s1-02 | computed_rows | 12, |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s1-03 | two_zone_rendered | 8, |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s1-05 | guard_wrong_minutes_total | 69 |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s2-02 | step0_outdoor_spread_K | 0.0 |  | by-hand | up |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s2-03 | quick_path_plan_kwh_spread | 0.0 |  | by-hand | up |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s2-04 | kept_schedule_cap_delta_kW | 0.00 |  | by-hand | down |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s2-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s3-01 | service_published_price | 0.5, |  | by-hand | up |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s3-02 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s3-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D17-s3-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D2-s1-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D2-s1-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D2-s1-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D2-s2-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 247.87 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-06 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-07 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-08 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-09 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-10 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D2-s3-11 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D3-s2-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 249.80 |  | rc=127; load1 from batch; no thread_factor |
| D4-s1-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 249.80 |  | rc=1; load1 from batch; no thread_factor |
| D4-s1-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 249.80 |  | rc=1; load1 from batch; no thread_factor |
| D4-s2-01 | unfilled_placeholders_total | 8 | 8 | yes | to_zero |  | by-hand |  | by-hand | 251.58 | 1.000 |  |
| D4-s2-02 | leaf_strings_compared |  | 4569 | by-hand | to_zero |  | by-hand |  | by-hand | 251.58 | 1.000 |  |
| D4-s3-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 251.58 |  | rc=1; load1 from batch; no thread_factor |
| D4-s3-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 251.58 |  | rc=1; load1 from batch; no thread_factor |
| D4-s3-03 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 251.58 |  | rc=1; load1 from batch; no thread_factor |
| D4-s3-04 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 251.58 |  | rc=1; load1 from batch; no thread_factor |
| D4-s3-05 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 251.58 |  | rc=1; load1 from batch; no thread_factor |
| D4-s3-06 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 251.58 |  | rc=127; load1 from batch; no thread_factor |
| D4-s3-07 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 251.58 |  | rc=127; load1 from batch; no thread_factor |
| D4-s2-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D5-s10-01 | named_source | .claude/rules/, |  | by-hand | up |  | by-hand |  | by-hand | 251.58 |  | rc=127; load1 from batch; no thread_factor |
| D5-s10-03 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 253.53 |  | rc=127; load1 from batch; no thread_factor |
| D5-s10-04 | units | 1794, |  | by-hand | down |  | by-hand |  | by-hand | 253.53 |  | rc=127; load1 from batch; no thread_factor |
| D5-s10-05 | units | 1794, |  | by-hand | down |  | by-hand |  | by-hand | 253.53 |  | rc=127; load1 from batch; no thread_factor |
| D5-s10-06 | units | 1794, |  | by-hand | down |  | by-hand |  | by-hand | 253.53 |  | rc=127; load1 from batch; no thread_factor |
| D5-s10-07 | units | 1794, |  | by-hand | down |  | by-hand |  | by-hand | 253.53 |  | rc=127; load1 from batch; no thread_factor |
| D5-s2-01 | menu_rows_readme |  | 25 | by-hand | down |  | by-hand |  | by-hand | 253.53 | 0.993 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/structure_fails.json; restored |
| D5-s2-02 | menu_rows_readme |  | 25 | by-hand | to_zero |  | by-hand |  | by-hand | 253.53 | 0.993 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/structure_fails.json; restored |
| D5-s2-03 | lower_floor_ratio |  | 1.4 | by-hand | up |  | by-hand |  | by-hand | 254.37 | 0.993 |  |
| D5-s2-04 | units |  | 75 | by-hand | down |  | by-hand |  | by-hand | 254.37 | 0.999 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/m4_ledger.tsv; restored |
| D5-s2-05 | units |  | 75 | by-hand | to_zero |  | by-hand |  | by-hand | 255.14 | 0.997 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/m4_ledger.tsv; restored |
| D5-s2-06 | units |  | 75 | by-hand | to_zero |  | by-hand |  | by-hand | 255.37 | 0.998 | tree edited by run: dev/audit/rounds/round11/D5/s2/work/m4_ledger.tsv; restored |
| D5-s2-07 | first_file |  | README.md | by-hand | up |  | by-hand |  | by-hand | 255.37 | 0.996 |  |
| D5-s2-08 | pairs |  | 57 | by-hand | down |  | by-hand |  | by-hand | 255.37 | 0.997 |  |
| D5-s2-09 | start_cost_swing |  | 0.000 | by-hand | up |  | by-hand |  | by-hand | 256.46 | 0.997 |  |
| D5-s2-10 | configurations |  | 7 | by-hand | to_zero |  | by-hand |  | by-hand | 256.46 | 0.995 |  |
| D5-s2-11 | menu_entries |  | 9 | by-hand | down |  | by-hand |  | by-hand | 256.46 | 0.997 |  |
| D5-s3-01 | claimed | 11, |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.46 |  | rc=127; load1 from batch; no thread_factor |
| D5-s3-02 | overshoot_c | 0.0, |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.46 |  | rc=127; load1 from batch; no thread_factor |
| D5-s3-03 | units | 2855, |  | by-hand | down |  | by-hand |  | by-hand | 256.46 |  | rc=127; load1 from batch; no thread_factor |
| D5-s4-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 256.46 |  | rc=127; load1 from batch; no thread_factor |
| D5-s4-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 256.46 |  | rc=127; load1 from batch; no thread_factor |
| D5-s5-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.46 |  | rc=127; load1 from batch; no thread_factor |
| D5-s5-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.46 |  | rc=127; load1 from batch; no thread_factor |
| D5-s5-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.90 |  | rc=127; load1 from batch; no thread_factor |
| D5-s5-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.90 |  | rc=127; load1 from batch; no thread_factor |
| D5-s5-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.90 |  | rc=127; load1 from batch; no thread_factor |
| D5-s5-06 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 256.90 |  | rc=127; load1 from batch; no thread_factor |
| D5-s5-07 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 256.90 |  | rc=127; load1 from batch; no thread_factor |
| D5-s6-01 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 258.03 | 1.00 |  |
| D5-s6-02 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 258.27 | 1.00 |  |
| D5-s6-03 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 258.97 | 1.00 |  |
| D5-s6-04 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 259.77 | 1.00 |  |
| D5-s6-05 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 259.95 | 1.00 |  |
| D5-s6-06 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 259.95 | 1.00 |  |
| D5-s6-07 | stamp_record_class_res_len |  | 6 | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 | 1.00 |  |
| D5-s6-08 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 259.87 |  | rc=1; load1 from batch; no thread_factor |
| D5-s7-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 259.87 |  | rc=127; load1 from batch; no thread_factor |
| D5-s7-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 |  | rc=127; load1 from batch; no thread_factor |
| D5-s7-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 |  | rc=127; load1 from batch; no thread_factor |
| D5-s8-01 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 259.87 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-02 | units | 3628, |  | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-03 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 259.87 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-04 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 259.87 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-05 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 259.87 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-06 | units | 3628, |  | by-hand | down |  | by-hand |  | by-hand | 259.87 |  | rc=1; load1 from batch; no thread_factor |
| D5-s8-07 | comment_units | 3099, |  | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 |  | rc=127; load1 from batch; no thread_factor |
| D5-s9-01 | stale_refs | 17 |  | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 |  | rc=127; load1 from batch; no thread_factor |
| D5-s9-02 | stale_refs | 17 |  | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 |  | rc=127; load1 from batch; no thread_factor |
| D5-s9-03 | stale_refs | 17 |  | by-hand | to_zero |  | by-hand |  | by-hand | 259.87 |  | rc=127; load1 from batch; no thread_factor |
| D5-s9-04 | units | 3748 |  | by-hand | down |  | by-hand |  | by-hand | 261.08 |  | rc=127; load1 from batch; no thread_factor |
| D6-s1-01 | false_rows_total | <n> |  | by-hand | to_zero |  | by-hand |  | by-hand | 261.08 |  | rc=1; load1 from batch; no thread_factor |
| D6-s1-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 261.08 |  | rc=1; load1 from batch; no thread_factor |
| D6-s2-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 261.08 |  | rc=127; load1 from batch; no thread_factor |
| D6-s2-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 261.08 |  | rc=127; load1 from batch; no thread_factor |
| D6-s2-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 261.08 |  | rc=127; load1 from batch; no thread_factor |
| D6-s3-01 | config_refusal_missing | 2 |  | by-hand | to_zero |  | by-hand |  | by-hand | 261.08 |  | rc=127; load1 from batch; no thread_factor |
| D6-s4-01 | unresolved_en |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 262.12 | 1.000 |  |
| D6-s4-02 | plan_writes_B0 |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 262.12 | 1.000 |  |
| D6-s5-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 262.12 |  | rc=2; load1 from batch; no thread_factor |
| D6-s5-02 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 262.12 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 262.12 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-04 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 262.12 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 262.12 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-06 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 262.12 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-07 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 262.12 |  | rc=1; load1 from batch; no thread_factor |
| D6-s5-08 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 262.12 |  | rc=1; load1 from batch; no thread_factor |
| D6-s6-01 | false_plus_stale | 18 |  | by-hand | down |  | by-hand |  | by-hand | 262.67 |  | rc=127; load1 from batch; no thread_factor |
| D6-s7-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 262.67 |  | rc=2; load1 from batch; no thread_factor |
| D6-s7-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 262.67 |  | rc=2; load1 from batch; no thread_factor |
| D7-s1-01 | perturbation |  | none | by-hand | up |  | by-hand |  | by-hand | 258.80 | 1.00 |  |
| D7-s1-02 | perturbation |  | none | by-hand | to_zero |  | by-hand |  | by-hand | 151.75 | 1.00 |  |
| D7-s1-03 | perturbation |  | none | by-hand | up |  | by-hand |  | by-hand | 95.56 | 1.00 |  |
| D7-s1-04 | perturbation |  | none | by-hand | up |  | by-hand |  | by-hand | 64.19 | 1.00 |  |
| D7-s1-05 | counters_ablated |  | none | by-hand | to_zero |  | by-hand |  | by-hand | 42.05 | 1.00 |  |
| D7-s1-06 | counters_ablated |  | none | by-hand | down |  | by-hand |  | by-hand | 38.95 | 1.00 |  |
| D7-s2-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 38.95 |  | rc=127; load1 from batch; no thread_factor |
| D7-s2-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 38.95 |  | rc=127; load1 from batch; no thread_factor |
| D7-s2-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 38.95 |  | rc=127; load1 from batch; no thread_factor |
| D7-s3-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 38.95 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 38.95 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 38.95 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 37.43 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-06 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 37.43 |  | rc=2; load1 from batch; no thread_factor |
| D8-s1-01 | no_dhw_pairs |  | 22 | by-hand | to_zero |  | by-hand |  | by-hand | 34.42 | 1.000 |  |
| D8-s1-02 | avail_none_cycles |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 34.52 | 1.000 |  |
| D8-s1-03 | avail_none_cycles |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 38.89 | 1.000 |  |
| D8-s2-02 | fam_runs_excess_entity_id_sensor |  | 2 | by-hand | to_zero |  | by-hand |  | by-hand | 39.30 | 1.000 |  |
| D8-s3-01 | triples |  | 984 | by-hand | to_zero |  | by-hand |  | by-hand | 39.30 | 1.000 |  |
| D9-s1-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 39.30 |  | rc=127; load1 from batch; no thread_factor |
| D9-s1-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 39.30 |  | rc=127; load1 from batch; no thread_factor |
| D9-s1-03 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 39.30 |  | rc=127; load1 from batch; no thread_factor |
| D9-s1-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 39.30 |  | rc=127; load1 from batch; no thread_factor |
| D9-s2-01 | retained_rows_slope |  | 1448.0 | by-hand | down |  | by-hand |  | by-hand | 39.28 | 1.000 |  |
| D9-s3-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 39.28 |  | rc=127; load1 from batch; no thread_factor |
| D9-s3-02 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 39.28 |  | rc=127; load1 from batch; no thread_factor |
