| id | metric | expected | got | reproduced | direction | perturbed | perturbation | void | null_value | load1 | thread_factor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D1-s1-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D1-s3-03 | pump_nonfinite_flag_true | 10 |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.28 | 1.000 |  |
| D10-s2-03 | bad | 2 | 0 | no | up |  | by-hand |  | by-hand | 0.28 | 1.000 |  |
| D11-s2-02 | window_prs |  | 52 | by-hand | up |  | by-hand |  | by-hand | 0.28 | 1.000 |  |
| D13-s2-01 | class_harness |  | 7 | by-hand | down |  | by-hand |  | by-hand | 0.28 | 1.00 |  |
| D15-s1-05 | fold_written |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.28 |  | rc=1; load1 from batch; no thread_factor |
| D16-s1-02 | cells | 532, | 532 | no | to_zero |  | by-hand |  | by-hand | 0.47 | 1.000 |  |
| D16-s3-04 | writes_again_off_restore_failed_while_off | 0 | 0 | yes | up |  | by-hand |  | by-hand | 0.47 | 1.000 | tree edited by run: dev/audit/rounds/round11/D16/s3/__pycache__/m6_restore.cpython-314.pyc; restored |
| D17-s3-03 | snapshots_in_ring |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.51 | 1.000 | tree edited by run: dev/audit/rounds/round11/D17/s3/__pycache__/rig.cpython-314.pyc; restored |
| D2-s3-06 | fold_err_max |  | 8.882e-16 | by-hand | to_zero |  | by-hand |  | by-hand | 0.65 | 1.0003 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D4-s2-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D5-s10-05 | units | 1794, | 3 | no | down |  | by-hand |  | by-hand | 0.65 | 1.000 |  |
| D5-s2-09 | start_cost_swing |  | 0.000 | by-hand | up |  | by-hand |  | by-hand | 0.65 | 1.000 |  |
| D5-s5-04 | false_units_total |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.73 | 1.000 |  |
| D5-s6-08 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.73 |  | rc=1; load1 from batch; no thread_factor |
| D5-s9-01 | stale_refs | 17 | 18 | no | to_zero |  | by-hand |  | by-hand | 0.75 | 1.000 |  |
| D6-s4-02 | plan_writes_B0 |  | 0 | by-hand | to_zero |  | by-hand |  | by-hand | 0.75 | 1.000 |  |
| D6-s7-02 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.75 |  | rc=2; load1 from batch; no thread_factor |
| D7-s3-03 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.75 |  | rc=2; load1 from batch; no thread_factor |
| D9-s1-03 | reference_solve_cpu_ms |  | 26.1489 | by-hand | down |  | by-hand |  | by-hand | 0.844727 | 1.00001 | tree edited by run: dev/audit/rounds/round11/D9/s1/__pycache__/d9s1lib.cpython-314.pyc; restored |
