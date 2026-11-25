# D3-g03 per-key notes (partial; probes run on the baseline side tree before gating)

## ec4b6ee2ab420129
- RESULT trip_saves_baseline=1 count log=1
- RESULT trip_saves_mutant=0 count log=0
- RESULT null_delta=0 count

## 3351754da55a2896
- RESULT state_nan_observed_baseline=(1.0, 0, 0, 0, True)
- RESULT state_nan_observed_mutant=(1.0, 0, 0, 0, True)
- RESULT state_pos_inf_residual_baseline=(1.0, 0, 0, 0, True)
- RESULT state_pos_inf_residual_mutant=(1.0, 0, 0, 0, True)
- RESULT state_neg_inf_residual_baseline=(1.0, 0, 0, 0, True)
- RESULT state_neg_inf_residual_mutant=(1.0, 0, 0, 0, True)
- RESULT states_moved=0 count
- RESULT debug_log_baseline=0 count
- RESULT debug_log_mutant=3 count
- RESULT positive_control_state_baseline=(1.01, 1, 1, 0, True)
- RESULT positive_control_moved=1 count

## 16f7665306eebdf3
- RESULT since_int_baseline=None
- RESULT since_int_mutant=12345
- RESULT since_list_baseline=None
- RESULT since_list_mutant=['2026-01-01']
- RESULT since_dict_baseline=None
- RESULT since_dict_mutant={'d': 1}
- RESULT since_empty_str_baseline=None
- RESULT since_empty_str_mutant=''
- RESULT forms_moved=4 count
- RESULT null_delta=0 count

## 2ec5fda238265712
- RESULT day_unhealthy_after_day2_baseline=None
- RESULT day3_healthy_baseline=True
- RESULT day_unhealthy_after_day2_mutant='indoor_temp stale'
- RESULT day3_healthy_mutant=False
- RESULT null_delta=0 count

## c0ecc8e0b6b66ded
- RESULT clear_issue_calls_baseline=['delete'] rollback_latch=False alarmed=False
- RESULT clear_issue_calls_mutant=['create'] rollback_latch=True alarmed=False
- RESULT null_delta=0 count

## ac6bedc70bb82ff7
- RESULT manual_plan_published_baseline=True
- RESULT manual_plan_published_mutant=False
- RESULT null_delta=0 count

## 3304e65ba361587f
- RESULT empty_views_baseline=True space_plan_keys=0
- RESULT empty_views_mutant=False space_plan_keys=5
- RESULT null_delta=0 count

## a28fd1af46c39331
- RESULT upper_published_baseline=0 count
- RESULT upper_published_mutant=4 count
- RESULT null_delta=0 count

## 4498461fcf451835
- RESULT valve_schedule_baseline=4 steps
- RESULT valve_schedule_mutant=None steps
- RESULT null_delta=0 count

## 79db73ec81b29f23
- RESULT caps_p0.1_baseline=None
- RESULT caps_p0.1_mutant=[0.06, 0.06]
- RESULT null_delta=0 count

## 816e18d55f46f0e4
- RESULT caps_p0.08_baseline=None
- RESULT caps_p0.08_mutant=[0.048, 0.048]
- RESULT caps_p0.1_baseline=None
- RESULT caps_p0.1_mutant=[0.06, 0.06]
- RESULT null_delta=0 count

## 9c82d861621b8087
- RESULT caps_tie_baseline=None
- RESULT caps_tie_mutant=[0.999999999, 0.999999999]
- RESULT max_cap_delta_kw=1e-09
- RESULT null_delta=0 count

## e880fd3537006726
- RESULT steady_writes_baseline=0 count
- RESULT steady_writes_mutant=3 count
- RESULT null_delta=0 count

## 134126ee4914191f
- RESULT score_tie_baseline=43.0
- RESULT score_tie_mutant=40.0
- RESULT null_delta=0 count

## b7623a645f34e628
- RESULT score_tie_baseline=40.0 free_streak=1.0
- RESULT score_tie_mutant=43.0 free_streak=None
- RESULT null_delta=0 count

## 420bcb8597761025
- RESULT written_baseline=50.1
- RESULT commanded_baseline=50.06 Hz
- RESULT tripped_baseline=False
- RESULT written_mutant=50.1
- RESULT commanded_mutant=50.1 Hz
- RESULT tripped_mutant=True
- RESULT null_delta=0 count

