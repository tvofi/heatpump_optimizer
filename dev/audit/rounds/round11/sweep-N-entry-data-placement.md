# Class sweep: N-entry-data-placement (round 11, D14 steps 3-4)

Mechanism: a setting the options flow edits is persisted into `ConfigEntry.data` (or a
flow-control value is persisted there). Every reader merges `{**data, **options}`, so an
options value shadows a later data write, and options cannot remove a value held in data.
`dev/audit/config/bugclasses.json` has no entry for this class yet (`jq` returns null), so
it is new and not barriered.

## Enumerator and controls

`PYTHONPATH=tests/hastub:custom_components python3 dev/audit/rounds/round11/D14/sweep/entry_data_placement.py`
scans every module's AST for `async_create_entry(data=<non-empty>)` and `async_update_entry(data=...)`.

- Package: seams=5, listed below. Positive control: it re-finds `_create_setup_entry`, where
  both findings persist. `device_prefill`'s `after_save` reaches data only through that call.
- Null control: `--fixture` (one options-only write) gives seams=0.
- Perturbation: `--perturb` (one added `data=` line) gives seams=1.

## Dispositions

| seam | disposition | evidence |
|---|---|---|
| config_flow.py:2933 `HeatPumpOptimizerConfigFlow._create_setup_entry` | instance (D10-s1-03) | `cfg_data_options.py` settings_in_data=41 |
| config_flow.py `async_step_device_prefill` (feeds `_create_setup_entry`) | instance (D17-s2-05) | `after_save_stray.py` entries_with_after_save=2 |
| config_flow.py:2875 `_async_save_reconfigure` | **instance, not a finding site** | 18 of its 19 first-screen keys are `_OPTION_FIELDS` keys. It writes data only, and its form suggests values from `entry.data`. `--probe-reconfigure`: options hold sensor.a; reconfiguring to sensor.b leaves the merged view at sensor.a |
| config_flow.py:3299 `async_step_reauth_confirm` | **instance, not a finding site** | `tibber_token` is an options field (credentials group), and reauth writes data only. `--probe-reauth`: the merged token stays the old one, so a reauth can leave the rejected token in use |
| config_flow.py:3393 `HeatPumpOptimizerOptionsFlow._save` | not applicable | `OptionsFlow.async_create_entry(data=)` is how HA writes `entry.options` |
| coordinator.py:1498 `_async_rewrite_entry` | guarded | writes data and options together from `undo_point`/`undone_settings` snapshots (entry_config.py:371), so both containers are restored at once |

The other entry writers (coordinator.py:4260 and 6582; services.py:880, 945 and 1097; away.py:494)
write options only. `__init__.py:226` writes the version only, and `repairs.py:56` writes `data={}`.
None of them appear in the list.

## Proposed barrier

Move the enumerator into a `tests/` script with an allow-list of `data=` seams. A seam
passes only if its keys share none with `_OPTION_FIELDS` or it writes both containers.
Gate cost is under 1 s. All four instances are fixed at one seam: create, reconfigure and
reauth write options keys to options (or drop them from options), and strip flow-control
keys before anything is persisted.
