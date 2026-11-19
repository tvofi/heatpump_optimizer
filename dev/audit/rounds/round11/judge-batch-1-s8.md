| id | metric | expected | got | reproduced | direction | perturbed | perturbation | void | null_value | load1 | thread_factor | flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D1-s2-01 | nan_boundary_passes | 1 | 0 | no | to_zero |  | by-hand |  | by-hand | 0.47 | 1.000 |  |
| D1-s3-04 | transport_returned_within_cap | 0 | 0 | yes | to_zero |  | by-hand |  | by-hand | 0.40 | 1.881 | re-take: thread_factor > 1.05 |
| D10-s2-04 | entities |  | 82 | by-hand | down |  | by-hand |  | by-hand | 0.40 | 1.000 |  |
| D11-s2-03 | releases |  | 5 | by-hand | up |  | by-hand |  | by-hand | 0.53 | 1.000 |  |
| D13-s2-02 | accepted_entries |  | 174 | by-hand | down |  | by-hand |  | by-hand | 0.53 | 1.00 |  |
| D15-s2-01 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.53 |  | rc=2; load1 from batch; no thread_factor |
| D16-s1-03 | cells | 532, | 532 | no | to_zero |  | by-hand |  | by-hand | 0.61 | 1.000 |  |
| D17-s1-01 | option_fields_missing | 156 | 156 | yes | to_zero |  | by-hand |  | by-hand | 0.60546875 | 1.0 |  |
| D17-s3-51 |  |  |  | by-hand |  |  | by-hand |  |  |  |  | harness not found |
| D2-s3-07 | fold_err_max |  | 8.882e-16 | by-hand | down |  | by-hand |  | by-hand | 0.72 | 1.0005 | tree edited by run: dev/audit/rounds/round11/D2/s3/__pycache__/_common.cpython-314.pyc; restored |
| D4-s3-01 | cells |  | 36 | by-hand | to_zero |  | by-hand |  | by-hand | 0.66 | 1.00 |  |
| D5-s10-06 | units | 1794, | 13 | no | down |  | by-hand |  | by-hand | 0.66 | 1.000 |  |
| D5-s2-10 | configurations |  | 7 | by-hand | to_zero |  | by-hand |  | by-hand | 0.66 | 1.000 |  |
| D5-s5-05 | false_units_total |  | 1 | by-hand | to_zero |  | by-hand |  | by-hand | 0.73 | 1.000 |  |
| D5-s7-01 | code_names |  | 87690 | by-hand | down |  | by-hand |  | by-hand | 0.81 | 0.997 | tree edited by run: dev/audit/rounds/round11/D5/s7/detail.tsv, dev/audit/rounds/round11/D5/s7/ledger.tsv; restored |
| D5-s9-02 | stale_refs | 17 | 18 | no | to_zero |  | by-hand |  | by-hand | 0.83 | 1.000 |  |
| D6-s5-01 |  |  |  | by-hand | down |  | by-hand |  | by-hand | 0.83 |  | rc=2; load1 from batch; no thread_factor |
| D7-s1-01 | perturbation |  | none | by-hand | up |  | by-hand |  | by-hand | 0.90 | 1.00 |  |
| D7-s3-04 |  |  |  | by-hand | to_zero |  | by-hand |  | by-hand | 0.90 |  | rc=2; load1 from batch; no thread_factor |
| D9-s1-04 | load1_start |  | 0.895996 | by-hand | to_zero |  | by-hand |  | by-hand | 0.99707 | 1.00001 | tree edited by run: dev/audit/rounds/round11/D9/s1/__pycache__/d9s1lib.cpython-314.pyc; restored |
