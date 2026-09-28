| id | metric | expected | got | reproduced | direction | perturbed | perturbation | void | null_value | load1 | thread_factor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0-s1-01 | drop_rel_max |  | 0.0001 | by-hand | to_zero |  | by-hand |  | 0.2422 | 5.08 | 1.424 | re-take: thread_factor > 1.05 |
| D0-s2-02 | gap_max |  | 13.8735 | by-hand | down |  | by-hand |  | 0.3247 | 1.00 | 1.000 | perturb rc=timeout |
| D1-s3-02 | live_registrations_after_unload |  | 2 | by-hand | to_zero | 0 | moved | False | 0 | 0.99 | 1.000 |  |
| D1-s3-05 | jump24_live_hours |  | 26.00 | by-hand | down | 0.00 | moved | False | 26.00 | 0.99 | 1.000 |  |
| D1-s4-02 | coord_minimal.guarded.solve_failures |  |  | by-hand | up |  | by-hand |  | by-hand | 0.99 | 1.003 |  |
| D1-s5-02 | price_model_silent_invalid | 11 | 11 | yes | to_zero | 0 | moved | False | 11 | 0.99 | 1.000 |  |
| D10-s1-02 | silent_presses |  | 2 | by-hand | to_zero | 0 | moved | False | by-hand | 1.00 | 1.000 |  |
| D11-s1-01 | owned_change_after_owner_approval |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 1.00 |  | load1 from batch; no thread_factor |
| D11-s1-03 | pr_jobs_with_write_running_pr_code |  | 3 | by-hand | to_zero | 0 | moved | False | by-hand | 1.00 | 1.000 |  |
| D11-s2-01 | joined_unrefused | 7 | 7 | yes | to_zero |  | by-hand |  | by-hand | 2.31 | 1.000 |  |
| D11-s2-04 | claims_holding | 0 | 0 | yes | up |  | by-hand |  | by-hand | 2.31 | 1.000 |  |
| D13-s1-03 | m3_body_answer_blocks |  | 8 | by-hand | down | 7 | moved | False | by-hand | 2.31 | 1 |  |
| D14-s4-01 | wrong_sites |  | 9 | by-hand | down | 8 | moved | False | 0 | 1.57 | 0.997 |  |
| D2-s1-01 | grid_envelope_violations |  | 69 | by-hand | to_zero | 0 | moved | False | by-hand | 0.98 | 1.0000 |  |
| D2-s2-03 | end_mismatch |  | 6 | by-hand | to_zero | 0 | moved | False | by-hand | 1.00 | 1.000 |  |
| D2-s4-01 | admitted_miss_rate |  | 0.636 | by-hand | to_zero | 0.439 | wrong-direction | True | 0.000 | 1.00 | 1.000 |  |
| D4-s1-05 | now_marker_collisions |  |  | by-hand | to_zero |  | by-hand |  |  | 1.00 |  | rc=1; load1 from batch; no thread_factor; perturb rc=1; null rc=1 |
| D6-s2-05 | simulate_plan_schema_only |  | 5 | by-hand | to_zero | 0 | moved | False | by-hand | 1.00 | 1.000 |  |
| D8-s2-01 | climate_unavailable_with_payload |  | 5 | by-hand | to_zero | 0 | moved | False | by-hand | 1.02 | 1.000 |  |
| D8-s2-03 | mode_split_after_action |  | 2 | by-hand | to_zero | 0 | moved | False | by-hand | 1.00 | 1.000 |  |
| D9-s1-01 | two_zone_dhw_winter.comfort_share_of_solve |  |  | by-hand | down |  | by-hand |  |  | 1.01 | 1.001 |  |
| D9-s1-03 | cad15.max_step_call_over_reference |  |  | by-hand | down |  | by-hand |  | by-hand | 1.0 | 1.0 |  |
| D9-s1-71 | saved_share_mean |  | 0.1035 | by-hand | down |  | by-hand |  | -0.0050 | 1.00 | 1.000 |  |
