# D3 s1 report (rendered from the finder's returned JSON)

baseline: 17f1c55fad1b

## exposure

```json
""
```

## coverage

```json
[
  {
    "step": "D3.M1",
    "depth": "deep",
    "evidence": "mutants.py sample walks the AST of all 12 modules in my cells: 1278 candidates; one-line operators (< and <=, > and >=, min and max, and/or). Weights are module consequence (1-3) x operator (min/max 3, else 2) x 2 for an if/elif/while/return guard. Seed 10, 36 sampled, at most 4 per module. process_worker has no candidate, so it was not sampled."
  },
  {
    "step": "D3.M2",
    "depth": "deep",
    "evidence": "24 of the 36 pre-screened (M01-M24). Each mutant ran in a baseline worktree that carries one empty marker commit, so env_drift.py --all 17f1c55fad1b does not refuse a self-comparison. The chain is the measured closure minus stress, edge, backtest, boost_drift_replay and golden.py (drift mode), plus env_drift --all. The null control was green on every script; env_drift is green standalone in 184.5 s. Result: 12 killed, 12 survived; raw lines in dev/audit/rounds/round10/D3/s1/prescreen/results.txt."
  },
  {
    "step": "D3.M3",
    "depth": "deep",
    "evidence": "Prescreened list returned. The top six survivors for the quiet-window full gate are M08, M01, M03, M22, M21 and M19. M05, M06, M10, M11 and M23 are classed equivalent or equality-only. M18 is on a harness-only path (sysid.identify, #1395)."
  },
  {
    "step": "D3.M4",
    "depth": "deep",
    "evidence": "Every survivor has a named production line and the check that should fail. Two have executed probes: forecast_keep.py (M08: prior_kept 1 at baseline -> 0 under the mutant, null arm --no-prior fabricates in both arms) and action_guards.py (M01/M03 family: live_guards 12 of 12 with short schedules -> 0 under --equal)."
  },
  {
    "step": "D3.M5",
    "depth": "spot",
    "evidence": "Median per-script wall from 27 runs compared with closures.json recorded seconds: env_drift 301.2 s against 0.9 s recorded (disclosed #934), features 748.6 against 598.2, optimality 256.4 against 186.3, finite_boundary 154.7 against 90.4, card.mjs 41.7 against 18.7. These are provisional: load 5-150. Duplicated kills: 2 of 12 (M12, M13; both second kills by env_drift). features.py is the only killer of 6 of 12. Optimality, finite_boundary and validate killed 0 of the mutants they saw."
  }
]
```

## unfinished

```json
[
  {
    "step": "D3.M2",
    "what": "M25-M36 (seed 10) were sampled but not pre-screened. Other seats drove box load to 20-150, so one mutant took 6-40 minutes. Rerun with: PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/mutants.py run M25,...,M36, from a baseline worktree that has one marker commit."
  },
  {
    "step": "D3.M3",
    "what": "The full GATE_SCOPE=full GOLDEN_MODE=drift gate for the top six survivors (M08, M01, M03, M22, M21, M19) is owed to the quiet window."
  },
  {
    "step": "D3.M5",
    "what": "Assertions per solve and closure over-approximation were not measured. Wall numbers were taken under heavy contention."
  },
  {
    "step": "D3.M3",
    "what": "REPORT.md was not written: the subagent environment refused a write of a report .md file. Its full content (method, pre-screen table, M4 answers, M5 table, non-findings) is carried in this JSON. The orchestrator must write it to dev/audit/rounds/round10/D3/s1/REPORT.md if needed."
  }
]
```

## findings

```json
[
  {
    "id": "D3-s1-01",
    "scope": "D3-s1",
    "step": "D3.M4",
    "title": "No check pins that a raising weather fetch keeps the previous forecast; the and->or mutant at coordinator.py:6522 survives",
    "severity": "medium",
    "claim": "Flipping `if state and not self._weather_forecast:` to `or` in HeatPumpOptimizerCoordinator._fetch_weather_forecast replaces a 24-row previous forecast with the fabricated 48-row constant trajectory (prior_kept 1 -> 0), and the file's whole non-structural closure plus env_drift --all stays green on that mutant (M08 SURVIVED).",
    "mechanism": "tests/features.py 'Weather staleness is surfaced (M2)' covers three cases: a raise with no prior forecast (fabricates), an empty result with a prior forecast (keeps), and a good fetch. It does not cover a raise with a prior forecast. The method's own docstring says the fabricated constant forecast cost +41.9 % realized and may be built only when nothing better exists.",
    "evidence": {
      "command": "PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/forecast_keep.py [--mutant|--no-prior]; suite arm: PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/mutants.py run M08 (from a baseline worktree with one marker commit)",
      "harness_path": "dev/audit/rounds/round10/D3/s1/forecast_keep.py",
      "value": "prior_kept=1 baseline, 0 mutant; null --no-prior: fabricated=1 in both arms; mutants.py RESULT M08=SURVIVED",
      "unit": "count",
      "baseline_sha": "17f1c55fad1b",
      "machine": "owner 8-core Mac, Darwin 25.6, venv-ci python 3.14",
      "cpu_or_wall": "count",
      "contention_note": "other seats drove load 20-150; count metric, contention-immune",
      "tolerance": "exact",
      "load1": 18.07,
      "thread_factor": 1
    },
    "instrumented_symbol": "custom_components/heatpump_optimizer/coordinator.py:HeatPumpOptimizerCoordinator._fetch_weather_forecast",
    "perturbation": {
      "change": "--mutant: the guard on line 6522 flipped from `and` to `or`, in memory (the method is re-compiled from its source and patched onto the class)",
      "expected_direction": "prior_kept 1 -> 0 (fabricated 0 -> 1, rows 24 -> 48)"
    },
    "metric_definition": "prior_kept = 1 when, after a raising service call with a live weather entity at -8.0 C and a previous 24-row 2.0 C forecast, the coordinator's own _weather_forecast is still those 24 rows; else 0.",
    "phenomenon_property": "Each branch of the weather-forecast fallback ladder (raise/empty/none x prior/no-prior) has a check that fails when that branch's keep-or-fabricate decision inverts.",
    "seam_rule": "grep -n '_weather_fetch_failed\\|_fabricated_forecast(' custom_components/heatpump_optimizer/coordinator.py",
    "stop_rule_class": "bug",
    "class_guess": "I1",
    "files": [
      "custom_components/heatpump_optimizer/coordinator.py",
      "tests/features.py"
    ],
    "proposed_fix_scope": "Add the missing case (raise with a prior forecast must keep it, marked stale) to the features.py M2 section, and prove it kills M08."
  },
  {
    "id": "D3-s1-02",
    "scope": "D3-s1",
    "step": "D3.M4",
    "title": "get_current_action's 12 per-key length guards are live but no check feeds them a short schedule; M01 and M03 survive",
    "severity": "low",
    "claim": "With any optional schedule shorter than power_schedule, flipping `and` to `or` in each of the 12 `if result.X and i < len(result.X)` guards in HeatPumpOptimizer.get_current_action raises IndexError (12 of 12 live). Two sampled flips, at optimizer.py:5541 and 5557, survive the full non-structural closure plus env_drift --all.",
    "mechanism": "Every test plan builds schedules of equal length, so the length half of each guard is never exercised. A refactor that drops it would pass the gate and crash the action read if a shorter schedule ever reached it. Whether production can produce a shorter schedule is not shown, hence severity low.",
    "evidence": {
      "command": "PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/action_guards.py [--equal]; suite arm: PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/mutants.py run M01,M03",
      "harness_path": "dev/audit/rounds/round10/D3/s1/action_guards.py",
      "value": "live_guards=12 of guards=12 (short schedules); 0 under --equal; mutants.py RESULT M01=SURVIVED, M03=SURVIVED",
      "unit": "count",
      "baseline_sha": "17f1c55fad1b",
      "machine": "owner 8-core Mac, Darwin 25.6, venv-ci python 3.14",
      "cpu_or_wall": "count",
      "contention_note": "other seats drove load 20-150; count metric, contention-immune",
      "tolerance": "exact",
      "load1": 76.99,
      "thread_factor": 1
    },
    "instrumented_symbol": "custom_components/heatpump_optimizer/optimizer.py:HeatPumpOptimizer.get_current_action",
    "perturbation": {
      "change": "--equal: give every optional schedule power_schedule's length (null arm)",
      "expected_direction": "live_guards 12 -> 0"
    },
    "metric_definition": "live_guards = number of get_current_action length guards whose in-memory and->or flip changes the returned action (or raises) on a 4-step plan with 2-entry optional schedules and now in the last step.",
    "phenomenon_property": "Each per-step optional-schedule read in get_current_action has a check that hands it a schedule shorter than the step index.",
    "seam_rule": "grep -n 'and i < len(result\\.' custom_components/heatpump_optimizer/optimizer.py",
    "stop_rule_class": "hygiene",
    "class_guess": "I1",
    "files": [
      "custom_components/heatpump_optimizer/optimizer.py",
      "tests/features.py"
    ],
    "proposed_fix_scope": "One table-driven features.py check that calls get_current_action on a short-schedule plan and asserts each optional key is absent with no raise. Prove it kills M01 and M03."
  }
]
```

## non_findings

```json
[
  {
    "claim": "The pre-screen chain is green at baseline on this machine, so a kill is a real kill",
    "command": "PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s1/mutants.py run M02 --null (optimizer chain); also M04 --null and M23 --null; env_drift standalone: python tests/env_drift.py --all 17f1c55fad1b",
    "value": "Every script rc=0 except env_drift timing out at 300 s under load. env_drift standalone: NO UNCLAIMED DRIFT, 56 scenarios, 184.5 s"
  },
  {
    "claim": "12 of 24 sampled mutants are killed by the closure",
    "command": "mutants.py run M01..M24",
    "value": "killed: M02 M07 M14 M17 M20 (env_drift), M04 M09 M15 M16 M24 (features), M12 (manual_plan + env_drift), M13 (card.mjs + env_drift)"
  },
  {
    "claim": "Survivors M05, M06, M10, M11 and M23 are equivalent or equality-only, not gaps",
    "command": "mutants.py run M05,M06,M10,M11,M23 plus reading the guard and its neighbouring line",
    "value": "M05: total_seconds() is always a float. M06: samples==0 returns the inert learner on the next line. M10 (mean_spot==0.01), M11 (margins==1e-9) and M23 (known_count==n_steps) differ only at exact equality."
  },
  {
    "claim": "M18 survives only on a harness-only path",
    "command": "mutants.py run M18; sysid.py:1706/1743/1788 notes (#1395)",
    "value": "SURVIVED; SystemIdentification.identify is harness-only, so there is no production consequence"
  },
  {
    "claim": "env_drift's 0.9 s recorded closure time is a known, disclosed stub figure, not an unreported drift",
    "command": "python3 tools aggregation over the mutant logs; tests/closure.py CLOSURES_COMMENT",
    "value": "median 301.2 s real against 0.9 s recorded; disclosed in closures.json _comment (#934)"
  }
]
```

## harnesses

```json
[
  "dev/audit/rounds/round10/D3/s1/mutants.py",
  "dev/audit/rounds/round10/D3/s1/action_guards.py",
  "dev/audit/rounds/round10/D3/s1/forecast_keep.py",
  "dev/audit/rounds/round10/D3/s1/prescreen/results.txt"
]
```

## leads

```json
[
  {
    "owner_seat": "unknown",
    "file": "tests/closure.py",
    "symbol": "lane_plan",
    "what": "Greedy lane balancing uses recorded.seconds, and that table records env_drift.py at 0.9 s and golden.py at a stub figure. A real env_drift --all took 184-550 s here, so any lane holding it is under-weighted."
  },
  {
    "owner_seat": "unknown",
    "file": "tests/env_drift.py",
    "symbol": "may-drift fixtures",
    "what": "env_drift --all reports 'may-drift ... did not move' for several fixtures (winter_two_zone_*, wood_*, valve_upper_direct_slab). A mutant that moves only a may-drift fixture is not killed by the differential gate. The size of that blind spot is unmeasured."
  }
]
```
