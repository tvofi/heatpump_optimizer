# Round 9, D6-s1: finder report (D6)

The box B1 thread rendered this file from the JSON report D6-s1 returned, which is stored verbatim in `tools/audit/round9/reports-B1.json`. The seat's own Write tool refused to create a report `.md` file. The JSON is the record, and this file adds nothing to it.

Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`

## Exposure

I opened no audit-era document. I read RELEASE_NOTES.md: the v6.6.5 section, and only the headings elsewhere. For the README's relative links docs/audit-2026-08.md, docs/audit-2026-09.md and docs/backlog.md, which are stripped from the export, I tested existence only, with `git cat-file -e 1936d5ca:<path>` in /home/claude/heatpump_optimizer; I never read their content. REPORT.md was not written: the subagent harness refused the file write ("Subagents should return findings as text"), so this JSON is the report. The claims table, which is the harness output, is at tools/audit/round9/D6/s1/claims_table.txt.

## Coverage

- **D6.M1** (deep): I read README.md through (1004 lines) and extracted 82 claims, each with a number, default, entity, service or field, unit, behaviour, version or link. 67 are C01-C65 and U01-U04 (C63 and U01-U04 are unverifiable), and 13 are L01-L13 for the external links. C11-C14 each sweep every sensor and binary-sensor row (65 rows).
- **D6.M2** (deep): tools/audit/round9/D6/s1/claims.py executes one check per claim. Entities go through the real async_setup_entry of each platform on a real HeatPumpOptimizerCoordinator, with two entries: a hot-water install and a Finish-setup-now entry. Services go through a recorder around services.async_register_services, plus the schemas and a real call to handle_apply_manual_plan. Options pages are checked against config_flow._OPTION_FIELDS/_OPTION_PAGES and strings.json; defaults via const and module constants; store keys from the coordinator's Store objects. Links get an HTTP HEAD, and relative paths get Path.exists plus git cat-file. Result: 63 true, 4 false, 0 stale, 15 unverifiable (10 links the proxy refused, and 5 claims that are external facts or need a SLOW run).
- **D6.M3** (deep): The claims table (id, source, claim, check, result, verdict, and the true statement for each false claim) is the harness stdout. It is recorded in tools/audit/round9/D6/s1/claims_table.txt, with RESULT claims_checked=82, claims_true=63, claims_false=4, claims_stale=0, claims_unverifiable=15.

## Findings

### D6-s1-01: README's Heat Pump Action state list omits idle and system_identification, which the sensor publishes

- step D6.M2, severity low, class hygiene, class_guess I5, provisional None

**Claim.** README.md's Heat Pump Action row lists the states as off, hot_water, eco, normal, pre_heat, boost and comfort, but the sensor also publishes `idle` (the empty-plan and pre-horizon fallback, HeatPumpOptimizer._idle_action) and `system_identification` (while the step-response experiment drives the pump).

**Metric.** Count of states in HeatPumpActionSensor's ENUM options (less 'unknown'; 'idle' confirmed by calling _idle_action) that do not appear backticked in README's Heat Pump Action row.

**Instrumented symbol.** `sensor:HeatPumpActionSensor._attr_options, with optimizer:HeatPumpOptimizer._idle_action executed`

**Phenomenon property.** Every state a published ENUM sensor can report is named wherever README.md enumerates that sensor's states.

**Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net | grep -E '^\| C1[56] '`

**Proposed fix scope.** README.md Heat Pump Action row: add `idle` (no plan step applies yet) and `system_identification` (the commissioning experiment is driving the pump). Optionally derive a check from HEAT_PUMP_ACTION_STATES in tests/doc_claims.py.

**Files.** README.md, custom_components/heatpump_optimizer/const.py, custom_components/heatpump_optimizer/sensor.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net",
  "harness_path": "tools/audit/round9/D6/s1/claims.py",
  "value": 2,
  "unit": "count (RESULT action_states_undocumented)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "round-9 box B1, linux container, CPython 3.14.0rc2",
  "cpu_or_wall": "count",
  "contention_note": "shared fan-out box; a count, not affected by contention",
  "tolerance": "exact",
  "load1": 0.93,
  "thread_factor": 1
}
```

**Perturbation**

```json
{
  "change": "--perturb=action_states: drop idle and system_identification from HeatPumpActionSensor._attr_options and make _idle_action return mode 'off'",
  "expected_direction": "to_zero",
  "observed_value": 0
}
```

**reproduction_steps**

```json
[
  "cd <export root>",
  "PYTHONPATH=tests/hastub python tools/audit/round9/D6/s1/claims.py --no-net | grep -E 'C15|action_states'"
]
```

### D6-s1-02: README puts the two-zone split and the orientation factor on the wrong options pages

- step D6.M2, severity low, class hygiene, class_guess I5, provisional None

**Claim.** README.md says the two-zone split is on 'Thermal model (expert)' and the orientation factor on 'Building type and emitters', but config_flow._OPTION_FIELDS renders inter_zone_heat_transfer, radiator_power_fraction and solar_orientation_factor on the 'Two-zone model' page.

**Metric.** Count of README field-to-page statements (12 named fields in 'Changing settings' and Quick start step 5) whose page differs from the step _OPTION_FIELDS renders the field on.

**Instrumented symbol.** `config_flow:_OPTION_FIELDS (step column) and config_flow:_OPTION_PAGES, with labels from strings.json options.step.*.menu_options`

**Phenomenon property.** Every page README.md names for a setting is the options page that actually renders that setting.

**Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net | grep -E '^\| C5[23] '`

**Proposed fix scope.** README.md, the 'Both paths land on the same model…' paragraph (around line 392): say the per-floor masses and losses, inter-zone transfer, radiator fraction and orientation factor are on Advanced settings → Two-zone model. Leave the house/slab masses, loss coefficient and power limits on Thermal model (expert), and window area and SHGC on Building type and emitters.

**Files.** README.md, custom_components/heatpump_optimizer/config_flow.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net",
  "harness_path": "tools/audit/round9/D6/s1/claims.py",
  "value": 3,
  "unit": "count (RESULT option_page_misplaced)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "round-9 box B1, linux container, CPython 3.14.0rc2",
  "cpu_or_wall": "count",
  "contention_note": "shared fan-out box; a count, not affected by contention",
  "tolerance": "exact",
  "load1": 0.93,
  "thread_factor": 1
}
```

**Perturbation**

```json
{
  "change": "--perturb=orientation: move solar_orientation_factor's _F row to building_preset",
  "expected_direction": "down",
  "observed_value": 2
}
```

**reproduction_steps**

```json
[
  "PYTHONPATH=tests/hastub python tools/audit/round9/D6/s1/claims.py --no-net | grep -E 'C52|option_page'"
]
```

### D6-s1-03: README's disabled-by-default census omits six hot-water sensors that the no-hot-water install disables

- step D6.M2, severity low, class hygiene, class_guess I5, provisional None

**Claim.** README.md says nineteen entities are disabled by default and that its list is 'every entity the ordinary install cannot light', but a Finish-setup-now entry (token and weather only, no hot water) disables 26. Six hot-water sensors are among them, and neither the list, their rows nor the prose says they are disabled.

**Metric.** Entities whose delivered entity_registry_enabled_default is False on a token+weather-only entry and that README neither lists as disabled nor calls disabled in their row or a prose sentence.

**Instrumented symbol.** `entity:DHWEntityMixin.entity_registry_enabled_default, read through each platform's real async_setup_entry on a real coordinator:HeatPumpOptimizerCoordinator`

**Phenomenon property.** Every entity whose registry default is off on an install README.md describes (including the Finish setup now and no-tank paths it offers) is documented as disabled by default, with its condition.

**Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net | grep -E '^\| C(08|09|10|13|18) '`

**Proposed fix scope.** README.md Entities section: state the hot-water gate, i.e. that without hot water configured the hot-water entities are disabled and unavailable. Name them: DHW Heating Schedule, DHW Heating Cost (next 24 h), Plan DHW Heating (next 24 h), DHW Energy (lifetime), DHW Cost (lifetime), DHW Setpoint Advisor, plus DHW Boost, which is already stated. Or add the condition to each row's Notes.

**Files.** README.md, custom_components/heatpump_optimizer/entity.py, custom_components/heatpump_optimizer/sensor.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net",
  "harness_path": "tools/audit/round9/D6/s1/claims.py",
  "value": 6,
  "unit": "count (RESULT no_dhw_disabled_undocumented)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "round-9 box B1, linux container, CPython 3.14.0rc2",
  "cpu_or_wall": "count",
  "contention_note": "shared fan-out box; a count, not affected by contention",
  "tolerance": "exact",
  "load1": 0.93,
  "thread_factor": 1
}
```

**Perturbation**

```json
{
  "change": "--perturb=dhw_config: the Finish-now entry also carries dhw_tank_volume=200 (config change, hot water on)",
  "expected_direction": "to_zero",
  "observed_value": 0
}
```

**null_control**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net --perturb=dhw_config",
  "value": 0,
  "note": "On a hot-water install the census is exactly README's 19 (C08, C09 true), so the gap exists only on the no-hot-water path."
}
```

### D6-s1-04: README says apply_manual_plan pins 'up to 20 hours'; an explicit expires_at pins the whole horizon

- step D6.M2, severity low, class hygiene, class_guess I5, provisional None

**Claim.** README.md's services table says apply_manual_plan pins run slots 'for up to 20 hours', but 20 h is only the default expiry. handle_apply_manual_plan accepts any future expires_at, and space_slots=[] with expires_at=now+48h pins all 24 h of the horizon off.

**Metric.** Hours of pinned (non-NaN) 15-min steps over a 96-step horizon from the handler's now, less 20 h, for space_slots=[] and expires_at=now+48h.

**Instrumented symbol.** `services:handle_apply_manual_plan -> manual_plan:build_override -> manual_plan:ManualOverride.channel_pins`

**Phenomenon property.** The maximum pin duration README.md states for apply_manual_plan equals the longest pin the service will actually apply.

**Seam rule.** `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net | grep -E '^\| C2[56] '`

**Proposed fix scope.** Either correct README ('for 20 hours by default, or until expires_at'), or clamp expires_at in the handler to MANUAL_PLAN_WINDOW_HOURS, as const.py's invariant comment asks. The code side is routed as a lead to D1-s2.

**Files.** README.md, custom_components/heatpump_optimizer/services.py, custom_components/heatpump_optimizer/const.py

**Evidence**

```json
{
  "command": "PYTHONPATH=tests/hastub /home/claude/venv314/bin/python tools/audit/round9/D6/s1/claims.py --no-net",
  "harness_path": "tools/audit/round9/D6/s1/claims.py",
  "value": 4,
  "unit": "h pinned beyond 20 h (RESULT manual_pin_hours_beyond_20)",
  "baseline_sha": "1936d5ca72a06556eeed4e8e5bf3dea520e517e1",
  "machine": "round-9 box B1, linux container, CPython 3.14.0rc2",
  "cpu_or_wall": "count",
  "contention_note": "shared fan-out box; a step count x 0.25 h, not affected by contention",
  "tolerance": "exact",
  "load1": 0.93,
  "thread_factor": 1
}
```

**Perturbation**

```json
{
  "change": "--perturb=clamp_expiry: clamp expires_at to now+MANUAL_PLAN_WINDOW_HOURS inside the handler's build_override call",
  "expected_direction": "to_zero",
  "observed_value": 0
}
```

**null_control**

```json
{
  "command": "same harness, expires_at omitted (default path) = --perturb=clamp_expiry arm",
  "value": "20.0 h pinned, 0.0 beyond",
  "note": "The default expiry honours 20 h; only an explicit expires_at exceeds it."
}
```

## Non-findings

- All 75 entities; Sensors (59), Binary Sensors (6), Buttons (4); switches Optimizer Active/Away/DHW Boost/Boost Space Heating; one climate entity; datetime Expected Return: `PYTHONPATH=tests/hastub python tools/audit/round9/D6/s1/claims.py --no-net (C01-C07)` gave 75 = 59+6+4+4+1+1; names match
- Nineteen (18 sensors + wood binary) disabled by default, and the named list matches, on a hot-water install: `claims.py C08, C09` gave 19 (18 sensors); set difference empty
- Per-row Unit, Diagnostic, 'disabled by default' and 'not recorded' notes: `claims.py C11-C14` gave 65 rows, 0 mismatches
- Optimization Mode and set_mode states; climate HVAC modes and presets: `claims.py C16, C17, C24` gave auto/comfort/economy/boost/off; off/heat/auto; auto/comfort/economy/boost
- DHW Boost is unavailable and disabled without hot water; Optimize Now is unavailable while a run is in flight: `claims.py C18, C19` gave default=False available=False; available=False
- 12 services, table complete, Returns column matches supports_response, 28 set_thermal_parameters fields, dhw_slots: [] accepted: `claims.py C20-C25` gave 12; no diff; all match; 28; {'dhw_slots': []}
- Defaults: 21/21/19.5 °C, 07-22, DHW windows, legionella on at 60 °C/7 d, wind 3 %, rain 15 %, 30 min, comfort_weight 5, mould margin 0.5, 8 weekly snapshots, curve 0.5 K/week, 300 s frequency writes, 3 ticks, 2 h boosts, 2/2 peak hysteresis, observe as default, 40 °C mixed water, 3 peaks, sysid off: `claims.py C27-C48` gave all 22 equal
- ECL110 topics ship empty; no ECL110 field in initial setup: `claims.py C49, C50` gave 3 empty topics; no ecl110 key in config steps
- Options menu of 23 pages, 22 editable plus an overview; comfort_weight label; finish menu labels: `claims.py C51, C53, C54` gave 23/22; 'How strictly to hold the temperature'; 3 labels match
- Twelve named store files; card resource path: `claims.py C55, C56` gave 12 keys, diff []; /heatpump_optimizer_static/heatpump-optimizer-card.js
- HA 2025.2.0 floor and badge, manifest requirements, en/sv translations, Quick setup in v6.6.5, VERSION in RELEASE_NOTES, three blueprints: `claims.py C57-C62` gave 2025.2.0; numpy/scipy/threadpoolctl; [en, sv]; #1251 in v6.6.5; 6.7.1; 3 files
- 22 relative links and 6 in-page anchors resolve; the 3 raw.githubusercontent blueprint links are live: `HPO_BASELINE_GIT=/home/claude/heatpump_optimizer HPO_BASELINE_SHA=1936d5ca… PYTHONPATH=tests/hastub python tools/audit/round9/D6/s1/claims.py (C64, C65, L09-L11)` gave missing=[] (3 stripped audit pages resolved in git); anchors all resolve; HTTP 200 x3

## Harnesses

- `tools/audit/round9/D6/s1/claims.py`
- `tools/audit/round9/D6/s1/claims_table.txt`

## Unfinished

- **D6.M2**: Not executed: 10 external links, where the egress proxy refused CONNECT (developer.tibber.com, github.com/strutsfarm x2, hacs.xyz, 4 shields.io badges, home-assistant.io, python.org); a quiet re-run with network would settle them. Also not executed: U01 (closed-loop +35 % loss converging in 3 days, and a correct model left alone within ±12 %), which needs a SLOW tests/rolling.py run; U02 (the sysid two-state gate's ~0.02 °C noise and 5 h window); U03 (30-90 SEK/kW typical, an external fact); U04 and C63 (HA 2025.2.0 being the first release with requires-python >=3.13, and the Python 3.13 floor), both external. REPORT.md itself was not written because the harness refused the write; this JSON is the report.

## Leads

- owner D1-s2, `custom_components/heatpump_optimizer/services.py` `handle_apply_manual_plan`: expires_at is accepted unbounded, which breaks the invariant stated at const.py:MANUAL_PLAN_WINDOW_HOURS (the override must be shorter than the 24 h horizon, or re-applying switches the optimizer off while appearing to leave it on). With space_slots=[] and expires_at=now+48h, all 96 steps are pinned off (claims.py C26).
