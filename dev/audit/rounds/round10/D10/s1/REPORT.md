# D10 s1 report (rendered from the finder's returned JSON)

baseline: 17f1c55fad1b

## exposure

```json
"None. The only docs read were README.md headings and service names, for the docs-* rule checks. No GitHub reads."
```

## coverage

```json
[
  {
    "step": "D10.M1",
    "depth": "deep",
    "evidence": "rules.py runs one executed check for each Bronze and Silver rule (28 rows). The checks are a dynamic census of 81 entities built through each platform's real async_setup_entry, all 13 registered actions called with no loaded entry, entity availability after last_update_success=False, AST/grep checks for the structural rules, and README lookups for the docs rules. Result: rules_todo=0; under --perturb, rules_todo=3."
  },
  {
    "step": "D10.M2",
    "depth": "deep",
    "evidence": "The tier table is the ROW lines of rules.py: 28 of 28 done (vacuous: docs-triggers, docs-conditions). The draft is dev/audit/rounds/round10/D10/s1/quality_scale.yaml. No row is todo, so no minimum HA release is needed above the hacs.json floor of 2025.2.0."
  },
  {
    "step": "D10.M3",
    "depth": "deep",
    "evidence": "Coverage: the per-script data from coverage_tree.sh fast (20 scripts) was combined and measured per module by coverage_modules.py. modules_below_95=0, lowest is accuracy.py at 96.80%, package 98.56%, config_flow 100.00%. With --drop config_flow_steps, config_flow falls to 84.83%. strict-typing: mypy_strict.py gives 0 errors over 76 files against real HA 2026.9.3, and 1 under --perturb. The stub arm gives 416 errors, all stub-shape artefacts."
  }
]
```

## unfinished

```json
[
  {
    "step": "D10.M3",
    "what": "The coverage figure is from the fast stage only. The e2e stage (validate, edge, backtest, optimality) was not added; since coverage data is a union, adding it can only raise the numbers. REPORT.md was not written: the harness refused writing a report file from this subagent. The report content is in this JSON."
  }
]
```

## findings

```json
[]
```

## non_findings

```json
[
  {
    "claim": "All 20 Bronze rules and the 8 measured Silver rules hold at baseline. The two coverage rows (config-flow-test-coverage, test-coverage) are measured by coverage_modules.py.",
    "command": "PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D10/s1/rules.py [--perturb]",
    "value": "rules_todo=0 at baseline; 3 under --perturb (unique_id nulled on one sensor, switch PARALLEL_UPDATES deleted, _loaded_coordinators returns [])"
  },
  {
    "claim": "entity-unique-id and has-entity-name: every constructed entity delivers a unique id and has_entity_name",
    "command": "rules.py",
    "value": "81 entities; without unique_id 0; duplicates 0; without has_entity_name 0"
  },
  {
    "claim": "action-exceptions: every registered action called with no loaded entry raises HomeAssistantError",
    "command": "rules.py",
    "value": "13/13 raise, 0 silent (9 silent under --perturb)"
  },
  {
    "claim": "entity-unavailable: no entity stays available after a failed coordinator update",
    "command": "rules.py",
    "value": "available_after_failed_update=0 of 81"
  },
  {
    "claim": "docs-configuration/installation-parameters: every config and options field carries a data_description",
    "command": "rules.py",
    "value": "374/374"
  },
  {
    "claim": "test-coverage (Silver): no integration module is below 95% statement coverage",
    "command": "W=$(mktemp -d); mkdir -p $W/site; venv-ci python -m pip install -q --target $W/site coverage; W5P_WORK=$W PYTHON=venv-ci/python bash tools/coverage/coverage_tree.sh fast; PYTHONPATH=$W/site:tests/hastub venv-ci/python dev/audit/rounds/round10/D10/s1/coverage_modules.py $W/out [--drop config_flow_steps]",
    "value": "modules_below_95=0, lowest accuracy.py 96.80%, package 98.56%, config_flow 100.00%; with --drop config_flow_steps, config_flow 84.83% and modules_below_95=1"
  },
  {
    "claim": "strict-typing: mypy --strict is clean against real Home Assistant. The 416 stub-arm errors (no-untyped-call 201, attr-defined 137, misc 36, ...) are stub-shape artefacts, a harness gap in tests/hastub and not an integration defect.",
    "command": "PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python dev/audit/rounds/round10/D10/s1/mypy_strict.py [--perturb]",
    "value": "mypy_real_errors=0 over 76 files (1 under --perturb); stub arm 416"
  }
]
```

## harnesses

```json
[
  "dev/audit/rounds/round10/D10/s1/rules.py",
  "dev/audit/rounds/round10/D10/s1/mypy_strict.py",
  "dev/audit/rounds/round10/D10/s1/coverage_modules.py"
]
```

## leads

```json
[
  {
    "owner_seat": "unknown",
    "file": "custom_components/heatpump_optimizer/__init__.py",
    "symbol": "async_setup / _async_register_services",
    "what": "The docstrings say 'the twelve services', and 'twelve handlers and the eleven hass.services.async_register calls'. services.py registers 13 (grep -c '.async_register(' = 13), so the code comments are stale. This belongs to D5 (code comments)."
  },
  {
    "owner_seat": "unknown",
    "file": "custom_components/heatpump_optimizer/services.py",
    "symbol": "handle_apply_schedule",
    "what": "A call with no applicable fields returns {'updated': {}, 'reason': 'nothing to apply'} before _loaded_entries runs. A bogus entry_id is therefore not refused when the call is empty, which is a possible action-exceptions edge."
  }
]
```
