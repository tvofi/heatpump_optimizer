# D15 verify, round 11

Verifier for D15. All 15 findings were measured in the git worktree `audit-r11-verify-D15` at `handoff/audit-r11-register` (28b864af6d). None of the finder seats is planted.
Bundle B is the owner's 2026-11-16 download (config_entry-...-13.json).
The box was heavily loaded: load1 between 118 and 295, thread_factor 1.000. All wall times are provisional. The s2 m5_zone and m5_judges arms timed out at 900 s; on the rerun, m5_zone's shipped and null arms timed out again at 2400 s.

| id | V1 reproduced (perturbation) | V2 independent | V3 reach / class | vote |
|---|---|---|---|---|
| D15-s1-01 | after_strip=-1 (refuse), before=1; --cite-in-tests -> 1 | the evidence path is under rounds/round10, which the strip removes | instrument only; I4 | verify, low |
| D15-s1-02 | synthetic_violations=72 scope=whole; --scope replay -> 0 | D15.md:24 says "over the bundle" while debug_ingest.py:98 gates the replay half: the brief and the tool disagree | instrument only; I4 | weaken, low: a run that follows the tool passes M2 |
| D15-s1-03 | stages_ok 12/12 with checks_run=11; --empty replay -> vacuous_passes 1 | debug_ingest.py:297 hard-codes `12 - len(fails)` | instrument; N-silent-zero | verify, low |
| D15-s1-04 | synthetic rows kept 0/192; --declare -> 192/192 | 192/192 samples have predicted_cost unpriced | production debugger ring in real HA; P2 | verify, medium |
| D15-s1-05 | lost=1 reloaded=0; --nameplate -> lost 0, reloaded 1 | coordinator.py setdefault(bucket, [thermal_kw, 0]) plus `+int(nameplate)`, against _learned_pair's `count>=1` | real HA, through the heat_kw floor path; P2 | verify, medium |
| D15-s2-01 | 2 learners voided, 42 samples lost | m8_replay: 2 resets; remap-ids -> 0 | replay tool only; I4; duplicate of s3-03 | verify, low |
| D15-s2-02 | future_samples_held=142/192 | window start to the newest store sample = 41.4 h | replay tool; I4 rather than new | verify, low |
| D15-s2-03 | observe_bias_calls=0; --perturb loads -> 96 | ring_days_counted 0 -> 3 | null-control instrument; N-silent-zero | verify, low |
| D15-s2-04 | shipped arm timed out (2400 s); fixed arm differing=0 | debug_replay.py never sets HASTUB_TZ (0 occurrences); tests/replay child_env does | tool only; I4 (not P7) | unresolved |
| D15-s2-05 | 8-cycle window (2 h): lane_red_judges=0, so no red judge was demonstrated | debug_replay.py:214-219 prints 5 judges and grades on 4; run_fixture counts 8 | tool; I4 | weaken, low: the defect is structural, and no red judge was hidden in the window measured |
| D15-s2-06 | no_default=0 in my 2 h window | SETPOINT_KEYS lists only valve_target_recommendation | tool judge; new | unresolved (the finder's window was not reached under load) |
| D15-s2-07 | not_frozen=0 in my 2 h window | not measured independently | tool judge; new | unresolved |
| D15-s3-01 | solver_week_min_ms=0; --perturb solver-filter -> 9806 | 10 of 662 rows with payload_solve_time_ms == 0 | self-test in real HA; N-silent-zero | verify, low |
| D15-s3-02 | TypeError, completes=False; production-row -> True | null feed_health on production rows: True | instrument; I4 (not P2) | verify, low |
| D15-s3-03 | learner_resets=2 over 18 solves; remap-ids -> 0 | same mechanism as s2-01 | replay tool; I4 | verify, low |

Seam rules were not run separately. Each harness covers only the seam it demonstrates; none enumerates every seam where the phenomenon could occur.
