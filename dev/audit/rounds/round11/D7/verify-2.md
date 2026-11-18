# D7 verify, unit D7#2 (seat D7-s3 findings)

All nine findings are in scope D7-s3, a planted seat, so every number below came from the private export copy
`../audit-r11-px-D7-2` (a plain directory, run with PYTHONPATH=tests/hastub). None came from the git worktree.
The box was contended throughout: load1 was 170-199, and the harnesses reported thread_factor 0.994-1.001.
Every number here is a static or behavioural count, so contention does not affect it.

My own harness is `v.py` in the session scratchpad. It calls the production functions directly and is not one of the finder's harnesses.

| id | V1 (finder harness) | perturbation / null | V2 (mine) | V3 reach | vote |
|---|---|---|---|---|---|
| D7-s3-01 | m8 temperature_roundtrip_disagreements=12 | --perturb gives 0 | normalize(from_c(v,u)) round trip fails on 9 of 28 (3 F units x 3 non-zero values; 0 is a fixed point); the C/K rows pass (null) | reachable: inputs.py:770 write_setpoint and the clamp at :643-647 | verify, high |
| D7-s3-02 | window_mean_disagreements=7 | --perturb gives 0 | constant 4 kW projects 0.0 at window start (mean None) and 4.0 at mid-window | reachable: coordinator.py:8794 peak guard | verify, high |
| D7-s3-03 | step_covering_now_disagreements=4 | --perturb gives 0 | code read: pump_arbiter._planned_room and early_cutoff._planned_room have no end rule (bisect-1 only); _covering_index and _step_index do | reachable: pump_arbiter.py:632/654/1421. The plan_stale gate at 1421 limits one caller only | verify, medium |
| D7-s3-04 | naive_instant 2 + finite_number 9 + water_heat 1 = 12 | --perturb gives 0. Leave-one-out without finite_number leaves 3 | per-family rows reproduce; the aggregate is dominated by finite_number | reachable, low consequence | verify, low |
| D7-s3-05 | m6_inner: unread_params 16, unread_locals 8, test_read_only attrs 8 / fields 8, unread_fields 1; m6_dead: unused_import 4, test_only 10 (the finder counts 6 of them as constants) | planted_delta=1; write_only_after_readers=0 | 6+4+16+7+8+8+1 = 50 | static count | verify, low |
| D7-s3-06 | m5_mutants.json: pinned 285, not_reached 100, timeout 2, swallowed 4, 89 absent (unentered) | `report` re-run against trace_site gives unentered=480: the per-script trace dir is not shipped, so the harness header is not reproducible as written | 93 = 89+4 from the mutant file; the 102 rows that were not driven make 93 a lower bound | test-suite gap | verify, medium |
| D7-s3-07 | twin_topk_disagreements=4 (twin_peak_cost 1) | --perturb gives 0 | _exact_topk_sum differs from the sum of the k largest on 200 of 200 random probes | reachable: tariff.py:958, :1038 | verify, high |
| D7-s3-08 | twin_trajectory_disagreements=18 | --perturb gives 0 | emitter_delivery(mix 18, zone 21, ua 0.5) = -1.5 kW | reachable: thermal_model.py:2526/2536 | verify, medium |
| D7-s3-09 | disagreements=4 of 6; the 3 NULL rows hold | --perturb gives 0 | DEFAULT_TWO_ZONE_MODE is TWO_ZONE_MODE_AUTO (const.py:770), so the presence arm is unreachable for auto or no key | reachable on every entry with no mode key | verify, high |

Classes: 01 P8 and 07/08 P2 confirmed. 03 is N-no-expiry: its seam_rule `grep bisect_right(` enumerates every seam.
04 is P2. 05 and 09 are new. 06 is I1.
