# Box D3-g11 pre-gate probe notes (partial; each key's record is results/<key>.json once its gate lands)
Probes run in the clean baseline checkout (92d38ecb), never the gate's tree, while the gates run (load1 ~1-4 from the gate).

## 9efe002b48e1827d HeatPumpOptimizerCoordinator.async_run_optimization line 6360 RETURN_DEL (moves: candidate if the gate survives)
    RESULT reentrant_solves_baseline=0 mutant=2
    RESULT inflight_flag_after_baseline=True mutant=False
    RESULT null_moved=0 count  (no solve in flight: baseline (1, False, None), mutant (1, False, None))
    RESULT load1=0.00

## a7488872387d5ca7 HeatPumpOptimizerCoordinator.async_run_optimization line 6379 CMP_BOUND (equivalent-candidate if the gate survives)
    RESULT no_prices_len=0 baseline='no_prices' mutant='no_prices'
    RESULT one_hour_from_now_len=96 baseline=None mutant=None
    RESULT two_hours_from_now_len=96 baseline=None mutant=None
    RESULT past_only_len=0 baseline='no_prices' mutant='no_prices'
    RESULT head_2h_past_len=96 baseline=None mutant=None
    RESULT tail_23h_len=0 baseline='no_prices' mutant='no_prices'
    RESULT day_and_half_len=96 baseline=None mutant=None
    RESULT lengths_seen=[0, 96]
    RESULT moved_production=0 count
    RESULT sensitivity_1h_horizon_len=4 baseline=None mutant='no_prices'  (not a production horizon)
    RESULT null_moved=0 count  (len=5)
    RESULT load1=0.16

## 61e748f094f2daa8 HeatPumpOptimizerCoordinator.async_run_optimization line 6454 CMP_BOUND (moves: candidate if the gate survives)
    RESULT issues_left_after_recovery_3_failures_baseline=0 mutant=1  (raised 1 / 1)
    RESULT null_moved=0 count  (4 failures: baseline (1, 0), mutant (1, 0))
    RESULT load1=0.16

## a33188790c5affad HeatPumpOptimizerCoordinator.async_run_optimization line 6454 GUARD_OFF (moves: candidate if the gate survives)
    RESULT issues_left_after_recovery_3_failures_baseline=0 mutant=1  (raised 1 / 1)
    RESULT null_moved=0 count  (1 failures: baseline (0, 0), mutant (0, 0))
    RESULT load1=0.23

## 94285425a1bc856a HeatPumpOptimizerCoordinator.async_shutdown line 6615 GUARD_OFF (moves: candidate if the gate survives)
    RESULT pending_task_baseline=task_done:True warnings:0 mutant=task_done:False warnings:0
    RESULT task_done_baseline=True mutant=False
    RESULT null_moved=0 count  (already-done task: baseline (True, 0), mutant (True, 0))
    RESULT load1=0.23

## 69b933a6a720006b HeatPumpOptimizerCoordinator.async_shutdown line 6620 GUARD_OFF (moves: candidate if the gate survives)
    RESULT wedged_task_baseline=task_done:False warnings:1 mutant=task_done:False warnings:0
    RESULT warnings_baseline=1 mutant=0
    RESULT null_moved=0 count  (0.3 s task: baseline (True, 0), mutant (True, 0))
    RESULT load1=0.19

## ede3dd3467ffc6e5 HeatPumpOptimizerCoordinator.async_simulate line 11214 CMP_BOUND (equivalent-candidate if the gate survives)
    RESULT no_prices_len=0 baseline=no_prices mutant=no_prices
    RESULT one_hour_from_now_len=96 baseline=priced mutant=priced
    RESULT two_hours_from_now_len=96 baseline=priced mutant=priced
    RESULT past_only_len=0 baseline=no_prices mutant=no_prices
    RESULT head_2h_past_len=96 baseline=priced mutant=priced
    RESULT tail_23h_len=0 baseline=no_prices mutant=no_prices
    RESULT day_and_half_len=96 baseline=priced mutant=priced
    RESULT lengths_seen=[0, 96]
    RESULT moved_production=0 count
    RESULT sensitivity_1h_horizon_len=4 baseline=priced mutant=no_prices  (not a production horizon)
    RESULT null_moved=0 count  (len=5)
    RESULT load1=0.32

## 9dcd374ac007dfc9 HeatPumpOptimizerCoordinator.async_simulate line 11271 BOOLOP (moves: candidate if the gate survives)
    RESULT no_cap_breach_key_baseline=0 mutant=1 (mutant value 0.0)
    RESULT no_cap_empty_breach_key_baseline=0 mutant=1 (mutant value 0.0)
    RESULT null_moved=0 count  (capped: (1, 0.0))
    RESULT load1=0.29

## d4b32336085935df HeatPumpOptimizerCoordinator.month_channel_totals line 8457 GUARD_OFF (equivalent-candidate if the gate survives)
    RESULT fresh_ledger_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT other_month_only_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT other_line_only_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT restored_non_dict_entry_baseline=(0.0, 0.0) mutant=(0.0, 0.0)
    RESULT moved_production=0 count
    RESULT stub_empty_dict_baseline=None mutant=(0.0, 0.0)  (not a production ledger)
    RESULT stub_none_baseline=None mutant=AttributeError  (not a production ledger)
    RESULT null_moved=0 count
    RESULT load1=0.29

## 4fd094e9727818b3 _dhw_inlet_c line 2907 CMP_BOUND (moves: candidate if the gate survives)
    RESULT age_at_limit_baseline=12.0
    RESULT age_at_limit_mutant=None
    RESULT null_moved=0 count
    RESULT load1=0.29

## e2b030e0716d126c _dhw_inlet_c line 2910 CMP_BOUND (moves: candidate if the gate survives)
    RESULT inlet_35_baseline=35.0
    RESULT inlet_35_mutant=None
    RESULT null_moved=0 count
    RESULT load1=0.29

## dc6c13eca2ca1737 _ensure_worker line 1864 GUARD_OFF (moves: candidate if the gate survives)
    RESULT live_workers_after_3_calls_baseline=1 mutant=3
    RESULT null_moved=0 count
    RESULT load1=0.29

## 738102c9ed0f89af _fold_flow_lift line 984 GUARD_OFF (moves: candidate if the gate survives)
    RESULT outdoor_nan_baseline=ok samples=0 mutant=TypeError
    RESULT outdoor_inf_baseline=ok samples=0 mutant=TypeError
    RESULT null_moved=0 count  (finite outdoor: ok samples=1)
    RESULT load1=0.35

## 372a4f4fcc8de86f _learned_pair line 490 CMP_BOUND (moves: candidate if the gate survives)
    RESULT zero_value_baseline=0
    RESULT zero_value_mutant=1
    RESULT neg_zero_value_baseline=0
    RESULT neg_zero_value_mutant=1
    RESULT null_moved=0 count
    RESULT load1=0.35

## 6f5898d327366799 _liquid_fraction line 3101 CMP_BOUND (moves: candidate if the gate survives)
    RESULT precip_1e-9_snow_baseline=1.0 mutant=0.0
    RESULT null_moved=0 count
    RESULT load1=0.35

## b247841f5466162d _open_loop_plan_value line 2539 CMP_BOUND (equivalent-candidate if the gate survives)
    RESULT tie_96_steps_baseline=50.0 mutant=50.0
    RESULT tie_1_step_baseline=50.0 mutant=50.0
    RESULT tie_2_steps_baseline=50.0 mutant=50.0
    RESULT tie_plus_1us_baseline=50.0 mutant=50.0
    RESULT tie_minus_1us_baseline=50.0 mutant=50.0
    RESULT before_600s_baseline=50.0 mutant=50.0
    RESULT before_901s_baseline=None mutant=None
    RESULT mid_baseline=62.0 mutant=62.0
    RESULT past_end_baseline=None mutant=None
    RESULT moved_valid=0 count
    RESULT dup_head_baseline=51.0 mutant=50.0  (malformed plan, not a production state)
    RESULT load1=0.35
