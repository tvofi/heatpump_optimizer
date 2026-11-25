# Class sweep: N-dead-input (round 11, PLAN phase D)

Property: a configured input that is accepted, stored and shown reaches the plan; changing it changes the plan.
Class status: `N-dead-input` has no entry in `dev/audit/config/bugclasses.json` at `handoff/audit-r11-register` (28b864af6d); it is new this round, so the ledger entry is owed at the judge/fold step.

## Enumerator (D14 step 3)

`python3 -I dev/audit/rounds/round11/D14/sweep-N-dead-input/dead_input_enum.py custom_components/heatpump_optimizer`, three lenses over the whole package, started from both findings' seam_rules:

- **A, unread key**: every `CONF_*` in `const.py` with no reader outside the flow layer (`config_flow`, `quick_setup`, prefill modules, `diagnostics`, `entry_config`), counting the symbol, its quoted value, the `"<NAME>"` mapping `thermal_model` uses, and `EntryConfig` attribute reads.
- **B, inert companion gate**: a `*_FRACTION`/`*_SCALE` option whose `DEFAULT_*` is the no-op 1.0 (the D17-s2-04 shape).
- **C, fallback-only measured input**: a coordinator method whose `_current_state.<x>` read sits only inside a `log_held(..., not self._<feed>)` early-return branch (the D17-s2-02 shape).

Controls (`controls.sh`, output in `controls.out`):
- positive: re-finds D17-s2-02 (lens C, `outdoor_temperature` in `_weather_series`) and D17-s2-04 (lens B, `CONF_SILENT_MODE_FRACTION`): True/True.
- null: a clean three-file fixture (every key read, fraction default 0.6, measured read outside the fallback): 0 seams.
- perturbation: the same fixture with one line (the measured read outside the fallback) removed: 1 seam.

## Dispositions (D14 step 4), 12 seams

| seam | lens | disposition |
|---|---|---|
| `coordinator._weather_series` / `outdoor_temperature` | C | **instance**, the D17-s2-02 site; probe `D17/s2/outdoor_sensor.py` |
| `CONF_SILENT_MODE_FRACTION` (gates `silent_mode_windows`) | B | **instance**, the D17-s2-04 site; probe `D17/s2/silent_prefill.py` |
| `CONF_COP_SCALE` | B | not applicable: learned state (`_COP_STORE_KEY`), 1.0 is the intended uncorrected value, not a gate on another stored option |
| `CONF_HOUSE_HEAT_LOSS_SCALE` | B | not applicable: identity multiplier, read by a consumer, 1.0 means no correction |
| `CONF_STALENESS_SCALE` | B | not applicable: identity multiplier on max ages, read by a consumer |
| `CONF_MAIN_FUSE_PHASES` | A | guarded: read by `EntryConfig`'s fuse-kW property (entry_config.py:269), an enumerator exclusion |
| `CONF_BUILDING_PRESET_ENABLED` | A | guarded: flow-time consumer, derives thermal values on save (config_flow.py:1005, 3904), as its field text says |
| `CONF_DHW_COMBI_TANK_TYPE` | A | guarded: flow-time preset selector writing the tank values (config_flow.py:630) |
| `CONF_DSO_PRODUCT` | A | guarded: flow-time `grid_fee.apply_catalog` writes the fee fields (config_flow.py:2099) |
| `CONF_AFTER_SAVE` | A | not applicable: options-flow navigation control, not a plan input |
| `CONF_MODBUS_PREFILL_PREFIX` | A | not applicable: prefill-step input consumed by the flow (config_flow.py:4086) |
| `CONF_PREFILL_OFFER` | A | not applicable: flow switch for the prefill offer (config_flow.py:2332) |

Instances beyond the two findings: **0**. Not barriered.

Proposed barrier (D14 step 5, for the plan): lens A+B as a `tests/` structure check (static, under 1 s of gate time); lens C as a lint over coordinator series builders. Limits: lens C only sees the `log_held` fallback idiom; lens B only names `FRACTION`/`SCALE` gates; dynamic reach (option changes plan) is proven only by the two finder harnesses.

Board lines: this sweep surfaced none; nothing owed a disposition.
