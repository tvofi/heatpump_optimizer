| id | metric | expected | got | reproduced | direction | perturbed | perturbation | void | null_value | load1 | thread_factor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0-s1-01 | cells |  | 80 | by-hand | up | 80 | not-moved | True | by-hand | 6.90 | 1.000 |  |
| D0-s2-01 | polish_gap_winter_mean |  | 0.2025 | by-hand | down |  | by-hand |  | by-hand | 13.44 | 1.000 | perturb rc=2 |
| D1-s1-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 12.62 |  | rc=1; load1 from batch; no thread_factor |
| D1-s1-02 | torn_midsolve_total |  | 1 | by-hand | to_zero | 0 | moved | False | 1 | 30.36 | 1.069 | re-take: thread_factor > 1.05 |
| D1-s2-01 | snapshot_instants_rewritten |  | 5 | by-hand | to_zero | 0 | moved | False | by-hand | 29.04 | 1.166 | re-take: thread_factor > 1.05 |
| D1-s2-02 | uncovered_cycles |  | 4 | by-hand | to_zero | 4 | not-moved | True | by-hand | 28.82 | 1.123 | re-take: thread_factor > 1.05 |
| D1-s2-03 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 31.88 | 1.133 | re-take: thread_factor > 1.05 |
| D1-s3-01 | empty_ok_wipes |  | 1 | by-hand | to_zero | 0 | moved | False | by-hand | 31.88 | 1.000 |  |
| D1-s3-02 | empty_ok_wipes |  | 1 | by-hand | to_zero | 0 | moved | False | by-hand | 33.57 | 1.000 |  |
| D10-s1-51 | actions_silent_on_bogus_entry | 1 | 1 | yes | to_zero | 0 | moved | False | by-hand | 33.84 | 1.000 |  |
| D11-s1-01 | escaped_heading_writes | 1 | 1 | by-hand | to_zero | 0 | moved | False | by-hand | 33.84 | 1.000 |  |
| D11-s1-51 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 33.84 |  | rc=2; load1 from batch; no thread_factor |
| D12-s3-01 | misdelivered_cells | 2 | 2 | by-hand | to_zero | 0 | moved | False | by-hand | 34.57 | 1.000 |  |
| D12-s2-71 | model_rollout_48h_max_abs_diff_c |  | 0.000e+00 | by-hand | to_zero | 0.000e+00 | not-moved | True | by-hand | 34.57 | 1.000 |  |
| D13-s1-01 | window |  | 197 | by-hand | up | 197 | not-moved | True | by-hand | 18.03 |  | rc=1; load1 from batch; no thread_factor; perturb rc=1 |
| D13-s2-01 | blocked_verdicts |  | 124 | by-hand | down | 123 | moved | False | by-hand | 13.49 |  | load1 from batch; no thread_factor |
| D13-s2-02 | blocked_verdicts |  | 124 | by-hand | down | 124 | not-moved | True | by-hand | 13.49 |  | load1 from batch; no thread_factor |
| D13-s3-01 | dora_keys_loads |  | 0 | by-hand | up |  | by-hand |  | by-hand | 8.63 | 1.0 | tree edited by run: dev/audit/rounds/round10/D13/s3/cache/repos_tvofi_heatpump_optimizer_commits_00e31e8a364e2657d8db32e97d1853895c476170_check-runs~per_page-100.page.json, dev/audit/rounds/round10/D13/s3/cache/repos_tvofi_heatpump_optimizer_commits_016959485b24cf43b0b3c39aae18fa37cb8ba089_check-runs~per_page-100.page.json, dev/audit/rounds/round10/D13/s3/cache/repos_tvofi_heatpump_optimizer_commits_04a4705f062a977337aa7f703fed877b5b7315de_check-runs~per_page-100.page.json, dev/audit/rounds/round10/D13/s3/cache/repos_tvofi_heatpump_optimizer_commits_058b2ee19ff9bcea0c3e9ba15e9943f4a2a2464a_check-runs~per_page-100.page.json, dev/audit/rounds/round10/D13/s3/cache/repos_tvofi_heatpump_optimizer_commits_0632f89c89ad94f52bd7491fd4b7ea17a2d40968_check-runs~per_page-100.page.json (+289); restored |
| D13-s2-51 | split_keys | 34 |  | by-hand | to_zero |  | by-hand |  | by-hand | 8.98 |  | rc=2; load1 from batch; no thread_factor; perturb rc=2 |
| D14-s1-01 | static_seams |  | 35 | by-hand | to_zero | 35 | not-moved | True | by-hand | 8.90 | 1.002 |  |
| D14-s3-01 | base_money_seams |  | 14 | by-hand | to_zero |  | by-hand |  | by-hand | 9.06 | 0.070 |  |
| D14-s3-02 | polling_stale_cycles |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 37.13 | 0.998 |  |
| D15-s1-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 37.13 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-02 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 37.13 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-03 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 37.13 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 37.13 |  | rc=2; load1 from batch; no thread_factor |
| D15-s1-05 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 37.13 |  | rc=2; load1 from batch; no thread_factor |
| D2-s2-01 | dhw_mode_ratio_max |  | 1.4346 | by-hand | down | 1.0000 | moved | False | 1.0000 | 37.13 | 1.000 |  |
| D2-s3-01 | last_window_reached |  | 0 | by-hand | up | 24 | moved | False | by-hand | 42.38 | 1.000 |  |
| D2-s3-71 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 32.69 |  | tree edited by run: OUTDIR/plantP0scenarioautumn.json, OUTDIR/plantP0scenarioautumn.out, OUTDIR/plantP0scenarioautumndelivery0.4.json, OUTDIR/plantP0scenarioautumndelivery0.4.out, OUTDIR/plantP0scenarioautumndelivery0.6.json (+36); restored; load1 from batch; no thread_factor |
| D2-s3-72 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 12.31 |  | tree edited by run: OUTDIR/plantP0scenarioautumn.json, OUTDIR/plantP0scenarioautumn.out, OUTDIR/plantP0scenarioautumndelivery0.4.json, OUTDIR/plantP0scenarioautumndelivery0.4.out, OUTDIR/plantP0scenarioautumndelivery0.6.json (+36); restored; load1 from batch; no thread_factor |
| D2-s1-71 | model_rollout_48h_max_abs_diff_c |  | 0.000e+00 | by-hand | to_zero | 0.000e+00 | not-moved | True | by-hand | 12.31 | 1.000 |  |
| D2-s3-73 | model_rollout_48h_max_abs_diff_c |  | 0.000e+00 | by-hand | to_zero | 0.000e+00 | not-moved | True | by-hand | 12.31 | 1.000 |  |
| D3-s1-01 | prior_kept | 0. |  | by-hand | to_zero |  | by-hand |  | by-hand | 12.31 |  | rc=2; load1 from batch; no thread_factor; perturb rc=2 |
| D3-s1-02 | live_guards | 12 | 12 | yes | to_zero | 12 | not-moved | True | by-hand | 12.31 | 1.000 | rc=127; perturb rc=127 |
| D3-s2-01 | loaders_correct |  | 2 | by-hand | to_zero | 2 | not-moved | True | by-hand | 11.80 | 1.000 | rc=127; perturb rc=127 |
| D4-s1-01 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 11.80 |  | rc=1; load1 from batch; no thread_factor |
| D4-s3-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 11.80 |  | rc=1; load1 from batch; no thread_factor |
| D4-s3-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 11.80 |  | rc=1; load1 from batch; no thread_factor |
| D5-s1-01 | mismatches |  | 5 | by-hand | down | 1 | moved | False | by-hand | 11.80 | 1.000 |  |
| D5-s2-01 | banner_mismatch |  | 1 | by-hand | to_zero | 0 | moved | False | by-hand | 11.80 | 1.000 |  |
| D5-s3-01 | comment_symbols_untriaged_missing |  | 1 | by-hand | up | 10 | moved | False | by-hand | 11.50 | 1.000 |  |
| D5-s3-51 | registered_actions |  | 13 | by-hand | up | 14 | moved | False | by-hand | 10.56 | 1.000 |  |
| D7-s1-01 | lines_added_per_arm |  | 1201 | by-hand | up |  | by-hand |  | by-hand | 13.24 | 1.000 | perturb rc=1 |
| D7-s1-51 | delta_S |  | +6.5186 | by-hand | to_zero | +0.0000 | moved | False | by-hand | 11.40 | 1.000 |  |
| D7-s1-52 | delta_S |  | +2.3771 | by-hand | to_zero | +0.0000 | moved | False | by-hand | 7.61 | 1.000 |  |
| D7-s1-53 | delta_S |  | +1.5020 | by-hand | to_zero | +0.0000 | moved | False | by-hand | 6.52 | 1.000 |  |
| D7-s2-01 | freq_map_clean_folds |  | 8 | by-hand | to_zero | 8 | not-moved | True | by-hand | 5.78 | 1.000 |  |
| D7-s2-51 |  |  |  | by-hand | up |  | by-hand |  | by-hand | 5.78 |  | rc=2; load1 from batch; no thread_factor |
| D7-s2-52 | delta_S |  | +2.6888 | by-hand | to_zero |  | by-hand |  | by-hand | 5.64 |  | load1 from batch; no thread_factor |
| D7-s2-53 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 5.64 |  | rc=127; load1 from batch; no thread_factor |
| D7-s2-54 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 5.64 |  | rc=127; load1 from batch; no thread_factor |
| D7-s2-55 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 5.64 |  | rc=127; load1 from batch; no thread_factor |
| D7-s2-56 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 5.64 |  | rc=127; load1 from batch; no thread_factor |
| D7-s2-57 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 5.64 |  | rc=2; load1 from batch; no thread_factor |
| D7-s2-58 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 5.64 |  | rc=2; load1 from batch; no thread_factor |
| D7-s2-59 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 5.64 |  | rc=127; load1 from batch; no thread_factor |
| D7-s2-60 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 5.64 |  | rc=2; load1 from batch; no thread_factor |
| D7-s2-61 | implementations |  | 4 | by-hand | the negative-reading disagreement vanishes; 1e400 remains | 4 | not-moved | True | by-hand | 5.67 | 0.491 | direction 'the negative-reading disagreement vanishes; 1e400 remains' not machine-checkable |
| D7-s3-01 | bill_oracle_cells |  | 20 | by-hand | up |  | by-hand |  | by-hand | 8.74 | 1.000 |  |
| D7-s3-02 | card_top_level_functions |  | 147 | by-hand | to_zero |  | by-hand |  | by-hand | 9.24 | 1.000 |  |
| D7-s3-51 | census_keys |  | 166 | by-hand | to_zero | 166 | not-moved | True | by-hand | 9.70 | 1.000 |  |
| D7-s3-52 | baseline_headline |  | 0 | by-hand | up |  | by-hand |  | by-hand | 9.10 | 1.000 |  |
| D7-s3-53 | honest_family_splits |  | 0 | by-hand | up |  | by-hand |  | by-hand | 9.01 | 1.000 |  |
| D7-s3-54 | leaked_reads |  | 344367 | by-hand | to_zero |  | by-hand |  | by-hand | 8.93 | 1.001 |  |
| D8-s1-01 | heating_now_while_off |  | 1 | by-hand | to_zero | 0 | moved | False |  | 7.27 | 1.000 |  |
