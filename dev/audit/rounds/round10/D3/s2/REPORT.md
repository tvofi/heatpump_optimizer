# D3 s2 report (rendered from the finder's returned JSON)

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
    "evidence": "mutants.py list: AST candidates over all 18 cell files (negated if-guards, boundary shifts, min<->max); seed 10, 36 mutants, <=4 per module, consequence WEIGHTS recorded in the harness; RESULT sampled=36"
  },
  {
    "step": "D3.M2",
    "depth": "deep",
    "evidence": "mutants.py run in an isolated worktree (plus a second worktree lane): each mutant's measured closure from tests/closures.json, run fast-first with stop at first kill: guard_pins, block_duty, debug_collect, wood_advisor, solar_alignment, manual_plan, config_flow_steps, plan_view, validate, then entities.py, then features.py for whatever survived. 32/36 killed (8 by the cheap scripts, 22 by entities, 2 by features). Baseline controls: features.py passes at baseline (4107 checks) and so does every cheap script. golden.py strict was dropped as a killer because it reports 55/56 scenarios CHANGED at baseline on this box. env_drift --all was not run on each mutant."
  },
  {
    "step": "D3.M3",
    "depth": "deep",
    "evidence": "prescreened list in results.json/results-lane2.json; 4 survivors: M26 snapshots.py:239, M35 ledger.py:306, M04 accuracy.py:369, M07 __init__.py:220; the quiet-window full drift gate is still owed on them"
  },
  {
    "step": "D3.M4",
    "depth": "deep",
    "evidence": "For each survivor, the line and the check that should have failed: M26/M35 need a features check asserting a 'Quarantined 1' WARNING on a malformed load and none on a clean load (next to the existing quarantine check at features.py:14943). M04 (pred==0.05 boundary) and M07 (a no-op async_update_entry at the current version) are near-equivalent. equiv_probe.py shows killed mutants M30 and M14 are not equivalent: they differ on 3/32 cells and 1/2 traces, and the identity null control gives 0/0."
  },
  {
    "step": "D3.M5",
    "depth": "spot",
    "evidence": "Provisional median walls from this run, load1 21-139: entities 341s with 22 kills out of 28 mutants seen; features 591s, 2/6; validate 65s, 0/6; config_flow_steps 52s, 2/30; wood_advisor, solar_alignment and plan_view each under 3s with 0 kills over 16-23 mutants. The recorded closure seconds a cell file forces range from 1237s to 5734s, and the larger closures include boost_drift_replay (3379s) and stress.py. Over-approximation and duplicate coverage were not measured."
  }
]
```

## unfinished

```json
[
  {
    "step": "D3.M2",
    "what": "env_drift.py --all <baseline> (it refuses ref==HEAD, so it needs a temp commit) and finite_boundary.py/optimality.py were not run on the 4 survivors M26, M35, M04, M07; the quiet-window GATE_SCOPE=full GOLDEN_MODE=drift run should cover them"
  },
  {
    "step": "D3.M5",
    "what": "No quiet-box gate table: per-script CPU vs closures.json seconds, assertions per solve, duplicate kills (the screen stopped at first kill), and whether the 5734s closures (boost_drift_replay, stress) over-approximate for cell files were all left unmeasured"
  }
]
```

## findings

```json
[
  {
    "id": "D3-s2-01",
    "scope": "D3-s2",
    "step": "D3.M3",
    "title": "Store-loader quarantine WARNING (ledger, snapshot ring) is pinned by no test; negating its guard survives the closure",
    "severity": "low",
    "claim": "Negating `if dropped:` in MonthlyLedger.from_dict (M35) or SnapshotRing.from_dict (M26) makes the loader silent when it really drops a record and logs 'Quarantined 0' on every clean load, yet every closure script run (cheap set, entities.py, features.py) still passes.",
    "evidence": {
      "command": "PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D3/s2/quarantine_warn.py [--mutate]; gate side: dev/audit/rounds/round10/D3/s2/mutants.py run M26 M35 --scripts guard_pins.py,block_duty.py,debug_collect.py,wood_advisor.py,solar_alignment.py,manual_plan.py,config_flow_steps.py,plan_view.py,validate.py,entities.py,features.py",
      "harness_path": "dev/audit/rounds/round10/D3/s2/quarantine_warn.py",
      "value": "loaders_correct=2 of 2 at baseline, 0 of 2 mutated; tests_naming_warning=0; gate scripts failing under M26/M35 = 0",
      "unit": "count",
      "baseline_sha": "17f1c55fad1b",
      "machine": "tvofi macOS arm64 8-core, shared box B2",
      "cpu_or_wall": "count",
      "contention_note": "fan-out, several other seats running env_drift/features; counts are contention-immune",
      "tolerance": "exact",
      "load1": 41.74,
      "thread_factor": 1
    },
    "instrumented_symbol": "custom_components.heatpump_optimizer.ledger:MonthlyLedger.from_dict, custom_components.heatpump_optimizer.snapshots:SnapshotRing.from_dict",
    "perturbation": {
      "change": "--mutate: replace `if dropped:` with `if not (dropped):` in both from_dict (in memory)",
      "expected_direction": "to_zero",
      "observed_value": "loaders_correct 2 -> 0"
    },
    "metric_definition": "Count of store loaders whose 'Quarantined N' WARNING fires exactly once on a load with one malformed record and not on a clean load",
    "phenomenon_property": "Every on-load quarantine of persisted records must emit its WARNING exactly when records are dropped, and that emission must be asserted by the gate",
    "seam_rule": "grep -n -A1 '_LOGGER.warning($' custom_components/heatpump_optimizer/*.py | grep Quarantined",
    "null_control": {
      "command": "quarantine_warn.py without --mutate",
      "value": "loaders_correct=2 of 2",
      "note": "the metric moves only under the guard negation"
    },
    "stop_rule_class": "hygiene",
    "class_guess": "new",
    "files": [
      "custom_components/heatpump_optimizer/ledger.py",
      "custom_components/heatpump_optimizer/snapshots.py",
      "tests/features.py"
    ],
    "proposed_fix_scope": "tests/features.py: next to the ledger quarantine check (~14943) and the snapshot ring checks, capture the module logger and assert one 'Quarantined 1' WARNING on a malformed load and none on a clean load, for both loaders",
    "provisional": true
  }
]
```

## non_findings

```json
[
  {
    "claim": "30 of 32 negated-guard/boundary mutants (excluding near-equivalent M04 and M07) in the D3-s2 cells are killed by their measured closure",
    "command": "PYTHONPATH=tests/hastub python dev/audit/rounds/round10/D3/s2/mutants.py run (results.json, results-lane2.json)",
    "value": "killed 32/36: 8 by the cheap scripts, 22 by entities.py, 2 by features.py"
  },
  {
    "claim": "M30 (const.topology_layout_valid two_tank_4way branch negated) and M14 (SnapshotRing.observe_bias `if not healthy` negated) are not equivalent mutants, and features.py kills both",
    "command": "dev/audit/rounds/round10/D3/s2/equiv_probe.py [--identity]",
    "value": "M30 differs 3/32 cells, M14 1/2 traces; identity control 0/0; features.py rc=1 on both and 4107/4107 passing at baseline"
  },
  {
    "claim": "M04 accuracy.py:369 `pred > 0.05`->`>=` survives but is near-equivalent (differs only at pred==0.05)",
    "command": "mutants.py run M04 --scripts entities.py,features.py",
    "value": "entities rc 0, features rc 0; not reported as a finding"
  },
  {
    "claim": "M07 __init__.py:220 `<`->`<=` survives but is behaviourally a no-op re-stamp of the same version",
    "command": "mutants.py run M07 --scripts entities.py,features.py",
    "value": "entities rc 0, features rc 0; not reported as a finding"
  },
  {
    "claim": "golden.py in strict mode cannot serve as a mutation killer on this box",
    "command": "GOLDEN_MODE=strict PYTHONPATH=tests/hastub python tests/golden.py",
    "value": "55 of 56 GOLDEN SCENARIOS CHANGED at baseline"
  }
]
```

## harnesses

```json
[
  "dev/audit/rounds/round10/D3/s2/mutants.py",
  "dev/audit/rounds/round10/D3/s2/equiv_probe.py",
  "dev/audit/rounds/round10/D3/s2/quarantine_warn.py"
]
```

## leads

```json
[
  {
    "owner_seat": "unknown",
    "file": "tests/run.sh",
    "symbol": "GOLDEN_MODE header comment",
    "what": "The run.sh header says strict is the default GOLDEN_MODE, but golden.py prints 'GOLDEN_MODE=drift (unset, defaulting to drift)' and runs env_drift --all origin/main when the variable is unset"
  },
  {
    "owner_seat": "unknown",
    "file": "tests/golden/",
    "symbol": "golden.py check_all (strict)",
    "what": "Strict mode reports 55/56 scenarios CHANGED at baseline on macOS arm64, with structural diffs such as 'components: length 4 -> 3', not only float drift. Either strict mode is dead locally or the fixtures are stale."
  }
]
```
