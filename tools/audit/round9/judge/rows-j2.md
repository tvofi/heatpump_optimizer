| id | metric | expected | got | reproduced | direction | perturbed | perturbation | void | null_value | load1 | thread_factor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D1-s3-04 | max_published_deviation |  | 5.00 | by-hand | to_zero | 0.00 | moved | False | 0.00 | 0.89 | 1.000 |  |
| D1-s4-01 | duty_targeted_stuck |  | 53 | by-hand | to_zero | 0 | moved | False | 53 | 0.91 | 1.000 |  |
| D1-s5-01 | reported_divergent | 7 | 7 | yes | to_zero | 0 | moved | False | by-hand | 0.91 | 1.000 |  |
| D1-s5-03 | entity_huge_int_rows |  | 0 | by-hand | up | 24 | moved | False | by-hand | 0.91 | 1.000 |  |
| D10-s2-01 | untranslated_presets_en |  | 2 | by-hand | to_zero | 0 | moved | False | 0 | 1.00 | 1.000 |  |
| D11-s1-02 | nonstamp_direct_reported |  | 0 | by-hand | up | 2 | moved | False | by-hand | 1.00 | 1.000 |  |
| D11-s1-04 | owner_gate_accepts_agent_declared |  |  | by-hand | down |  | by-hand |  | by-hand | 1.00 |  | load1 from batch; no thread_factor |
| D11-s2-02 | variants_refused | 0 | 0 | yes | up |  | by-hand |  | by-hand | 1.22 | 1.000 |  |
| D13-s1-02 | reverify_blocked |  | 0 | by-hand | up | 1 | moved | False | by-hand | 1.22 | 1 |  |
| D14-s4-02 | replay_wrong_sites |  | 0 | by-hand | up | 10 | moved | False | by-hand | 1.53 | 0.996 |  |
| D4-s1-02 | popup_out_cells |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 1.74 |  | rc=1; load1 from batch; no thread_factor; perturb rc=1 |
| D4-s2-03 | escaped_error_texts_reached | 4 | 4 | yes | to_zero | 0 | moved | False | by-hand | 1.76 | 1.000 |  |
| D7-s1-02 | survivors |  |  | by-hand | down |  | by-hand |  | by-hand | 1.76 |  | load1 from batch; no thread_factor |
| D8-s2-02 | hvac_action_vs_plan |  | 14 | by-hand | to_zero | 0 | moved | False | by-hand | 1.94 | 1.000 |  |
| D8-s3-01 | families_split_unexplained_name_en |  | 2 | by-hand | down | 1 | moved | False | by-hand | 1.95 | 1.000 |  |
