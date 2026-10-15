Fix review: merge b7a0eb305f44a16e3bbbf5961275e8bcd2520781
bus-nonce: 588a66e55397993a8bbe404f15b2b66b

Round 1. Measured from a detached worktree; code head 2e7840f75, and b7a0eb305 adds only dev/programme/delivery/2290.md (three-dot name-only diff to the code head).

RESULT finder bogus_entry_actions.py (finder's, unmodified): base actions_silent_on_bogus_entry=1 silent=['apply_schedule'] raised=7; head 0 silent, raised=8; --perturb 0 at both ends
RESULT mutation_M1_base_services_py_restored: census FAILS with silent ['apply_schedule[]: returned', "apply_schedule['entry_id']: returned"]
RESULT planted_new_service_returning_before_resolving (ping, registered and in services.yaml): census FAILS silent ['ping[]: returned', "ping['entry_id']: returned"]
RESULT null_control: apply_schedule on a known loaded entry answers an empty call "nothing to apply" and applies dhw_windows; check passes at head
RESULT census_head: 5 ok via my own runner census_run.py (an instrument I built because features.py takes tens of minutes; it execs the census block with its fixtures); tests/entities.py ALL 2318 ENTITY CHECKS PASSED
RESULT class: census drives all 13 registered actions in both refusing states and asserts its preconditions; no other seam silent
RESULT step14: structure.py PASSED, no budget moved; archscore --diff dS +0.0000 NULL; tmp_paths 0 refused
RESULT claims/version: no golden, claim, closures, budget, VERSION, manifest or notes file in the diff
RESULT conflict: merge-tree origin/main b7a0eb305 exit 0
RESULT forward-carry: on origin/main via #2292 (e7002ec70), R10-PARAMS-OWNER carry names handle_set_thermal_params resolving _loaded_coordinators before any return, the census and its control
RESULT CI at b7a0eb305: 30 success, 15 skipped, 0 other (check-runs API); pr-contract green; no red check, so no root-cause answer owed
