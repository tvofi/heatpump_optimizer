merge 2d2cc419576065c3c731815dc1130de5d6b6373a

Round 1 fix review of R9-F2.4 (PR #1782). Measured at 2d2cc419 (merge base 04fa97bc), live head re-read at posting: unchanged.
Env: Linux cloud, CPython 3.14.7, hash-pinned tests/requirements-ci.txt (numpy 2.4.6, scipy 1.17.1, scipy-openblas 0.3.31), OPENBLAS_CORETYPE=Haswell, 1 thread.
Evidence directory: audit-r9/fix/evidence/F2.4-review-2d2cc419 (project files).

RESULT lines (finder's harness, tools/audit/round9/D12/s2/onoff_switch.py, base 04fa97bc -> head 2d2cc419):
  onoff_failing_cells 3 -> 0; onoff_withheld_frac_mean 0.133 -> 0.000
  onoff_e2e_turn_off_with_planned_heat 30 -> 0; onoff_shoulder_Kh_below_plan_actuated 17.23 -> 0.00
  modulating (null arm) failing_cells 0 -> 0, e2e turn_off calls 58 -> 58
D8 harness minpower.py: 0 steps in every arm at both ends, and under --perturb at both ends (flat by design, as the body says).

Gate, scoped, at head: MODE: SCOPED -- 24 run, 3 scoped out. 23 of 24 green: features 3588, entities 1990, backtest 25,
optimality 84, structure, harness_headers 91, typing census; env_drift --all: NO UNCLAIMED DRIFT 56 / NO STALE FIXTURE 56 vs 04fa97bc.
Typing ruler --mypy (pinned pair): ALL 9 PASSED. codeowners_gap uncovered_files=0; policy_lint 0 errors; merge-tree clean;
5b176f0e's tree equals an automatic merge of 720a5de1 and 04fa97bc; VERSION, manifest and notes heading untouched.

Own mutants (full tests/features.py or tests/entities.py each): 8 run, 7 killed by the suite.
  R5 (count_compressor_starts default 0.1 -> 0.2) survives features.py, but moves published compressor_starts
  in 3 golden fixtures (valve_storage, valve_storage_low_target, valve_storage_smart_write), so env_drift kills it.
mutation_table.py --scope changed --base origin/main: ratchet 3580 unpinned vs 3583 at base, no new site;
  the driven table is INCONCLUSIVE because the stress baseline read 286x on the CPU arm (below).

Stress, the open item:
  Memory: not a regression. In this box's gate all six probes read at the import floor (attributable 0.0), as on CI.
  Standalone interleaved A/B of stress.py's own probes for winter/cycle, 8 draws each: base median 10.0 MiB, head 9.9;
  traced 3.45-3.46 at both ends; 0 draws over 14.1. The Mac container's 14.1 is the Docker-on-macOS offset F2.5's review
  measured (~40 % higher records). No stress_budgets.json re-record is warranted by this PR.
  CPU (shoulder/tariff+pv+cycle): F2.4 adds no cost. Interleaved A/B, 6 solves each: plan sha1 and objective identical;
  solve CPU median head 12.1 s vs base 12.6 s. The reference solve swings 41-85 ms, so the ratio swings with it;
  base's quiet stress run read 241x and head's 273x. The red is reference noise near a tight budget on Linux;
  a raise would be tvofi's call on its own merits and is not owed by this PR.

Non-blocking findings:
  1. The block's "one result cannot publish a compressor start on a step its own on schedule calls off" check does not
     separate count_compressor_starts' threshold from the owner (R5 survives features.py). A row with a step in (0.1, 0.2]
     after an off step would pin it.
  2. The on schedule reads space+dhw, step_duty reads each circuit, so a step where both circuits trickle (each <= 0.1,
     sum > 0.1) gives action on/hot_water and duty idle. Unreachable today: 0 of 4824 golden steps (split_probe).
  3. The claim note's "one-way by construction" is false at exactly 0.1 kW (old >=, new >). Measure-zero; no fixture moved True -> False.
  4. coordinator.py:1837's schedule-attribute fallback `p > 0.1` is a plan-side copy of the rule, space only, not dispositioned.
     Dead today (the only OptimizationResult constructor fills heat_pump_on_schedule). It is F1's file; worth adding to carry-1644.
  5. handoff/round9/fix/resume/F2.4.md is in the code head's ancestry, which standing.md forbids; #1781 merged the same shape.
Step 11: PR checks at this head show no red besides the mutation job the merge seat reported (null control, CPU arm) and re-ran.
Forward carry: carry-1644.json's third entry is present and brief_lint passes.
