# F1.8 (#1799) review preparation, code head 87bf02de, merge base 5dfa6684

Prepared against the merge base only (fix-review.md: before handoff, no head measurement). Head measurement follows the fixer's handoff.

## B1 (blocking): identity_update writes a unique id another entry already holds
- `config_flow.identity_update` returns the re-derived id whenever it moved; reauth, `_save`, `_save_or_menu` and `services.handle_assign_entity` write it with no check that another heatpump_optimizer entry holds it.
- `async_step_reconfigure` (the seam this PR says "already re-derived") guards the same write with `async_set_unique_id` + `_abort_if_unique_id_configured`.
- Real Home Assistant 2026.9.3 `ConfigEntries._async_update_entry` (wheel downloaded here, excerpt in ha_2026.9.3_async_update_entry_unique_id.txt): a changed unique_id already in use logs ERROR "Unique id of config entry ... changed to ... which is already in use, please report it to the integration" (comment: "Deprecated in 2024.11, should fail in 2025.11") and indexes both entries under one id.
- Population: exactly the duplicates D10-s1-01 created (two entries for one plant, one with a stale id). Any edit of the stale one now writes the other's id.
- Read from source, not executed: the stub's `async_update_entry` ignores `unique_id=`, so no test in this tree can see it.
- Fix asked: refuse (or leave unchanged) an id another entry of the domain holds, as reconfigure does, and a test that pins it.

## Budget raise: coordinator_multiassigned_attrs 116 -> 117
- structure.py at 87bf02de: coordinator_multiassigned_attrs 117 <= 117, coordinator_methods 224 <= 224 (zero headroom), coordinator_attrs 154 <= 154.
- Judgement: the raise is the architecturally right call. `currency` is now cycle state with an initial value (init: feed or instance; cycle: feed, sticky). Alternatives: dropping the __init__ write relies on first-refresh ordering (__init__.py first refresh precedes platform setup, but nothing pins that no pre-refresh reader exists); a holder or `_ctx` field moves the same two writes behind indirection and needs a coordinator property (coordinator_methods at zero headroom) or 13 edited sensor.py read sites. cut_grid goes 183 -> 182.

## sensor.py borrow (out of plan)
- 12 lines in HeatPumpOptimizerSensorBase only; merge-tree against origin/main conflicts only in tests/deployment_shape.py. Accept: the only place a sensor built before the feed's state can follow it; flagged in the body.

## Optional
- `declared_currency("ÖRE/kWh")` returns "ÖRE" and "ORE/kWh" returns "ORE" (any three upper-case letters pass as an ISO code). Lower-case "öre/kWh" returns None as intended.
